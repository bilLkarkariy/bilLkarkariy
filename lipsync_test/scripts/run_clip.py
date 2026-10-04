"""Driver MuseTalk 1.5 (CPU) : sortie sans son, même nombre d'images que la vidéo source."""
import argparse, os, pickle, subprocess, time, json
import cv2, numpy as np, torch
from transformers import WhisperModel

p = argparse.ArgumentParser()
p.add_argument("--video"); p.add_argument("--audio"); p.add_argument("--out")
p.add_argument("--extra_margin", type=int, default=10)
p.add_argument("--parsing_mode", default="jaw")
p.add_argument("--left_cheek_width", type=int, default=90)
p.add_argument("--right_cheek_width", type=int, default=90)
p.add_argument("--smooth", type=int, default=0, help="fenêtre de lissage temporel des bbox (0 = aucun)")
p.add_argument("--upper_boundary_ratio", type=float, default=0.5)
p.add_argument("--expand", type=float, default=1.5)
p.add_argument("--batch_size", type=int, default=8)
p.add_argument("--threads", type=int, default=4)
p.add_argument("--max_frames", type=int, default=0)
args = p.parse_args()
torch.set_num_threads(args.threads)

t0 = time.time()
from musetalk.utils.utils import load_all_model, datagen
from musetalk.utils.audio_processor import AudioProcessor
from musetalk.utils.face_parsing import FaceParsing
from musetalk.utils.blending import get_image

device = torch.device("cpu")
vae, unet, pe = load_all_model(unet_model_path="./models/musetalkV15/unet.pth", vae_type="sd-vae",
                               unet_config="./models/musetalkV15/musetalk.json", device=device)
timesteps = torch.tensor([0], device=device)
ap = AudioProcessor(feature_extractor_path="./models/whisper")
whisper = WhisperModel.from_pretrained("./models/whisper").to(device).eval()
fp = FaceParsing(left_cheek_width=args.left_cheek_width, right_cheek_width=args.right_cheek_width)
t_load = time.time() - t0

# Images source
cap = cv2.VideoCapture(args.video)
frames = []
while True:
    ok, f = cap.read()
    if not ok: break
    frames.append(f)
fps = cap.get(cv2.CAP_PROP_FPS)
if args.max_frames: frames = frames[:args.max_frames]
N = len(frames); H, W = frames[0].shape[:2]

# Repères du visage (cache par clip)
t1 = time.time()
cache = os.path.join(os.path.dirname(args.out), "..", "coords", os.path.basename(args.video) + f".{N}.pkl")
os.makedirs(os.path.dirname(cache), exist_ok=True)
if os.path.exists(cache):
    coords = pickle.load(open(cache, "rb"))
else:
    import tempfile
    from musetalk.utils.preprocessing import get_landmark_and_bbox
    d = tempfile.mkdtemp(dir=os.path.dirname(cache))
    paths = []
    for i, f in enumerate(frames):
        pth = f"{d}/{i:08d}.png"; cv2.imwrite(pth, f); paths.append(pth)
    coords, _ = get_landmark_and_bbox(paths, 0)
    for pth in paths: os.remove(pth)
    os.rmdir(d)
    pickle.dump(coords, open(cache, "wb"))
t_lmk = time.time() - t1

coords = np.array(coords, dtype=np.float64)
if args.smooth > 1:
    k = args.smooth; pad = k // 2
    padded = np.pad(coords, ((pad, pad), (0, 0)), mode="edge")
    coords = np.array([padded[i:i + k].mean(0) for i in range(N)])
coords = [tuple(int(round(v)) for v in c) for c in coords]

# Audio -> fenêtres whisper, une par image
t2 = time.time()
feats, alen = ap.get_audio_feature(args.audio)
chunks = ap.get_whisper_chunk(feats, device, torch.float32, whisper, alen, fps=fps,
                              audio_padding_length_left=2, audio_padding_length_right=2)
n_audio = len(chunks)
if n_audio < N:  # complète par la dernière fenêtre (silence)
    chunks = torch.cat([chunks, chunks[-1:].repeat(N - n_audio, 1, 1)], 0)
chunks = chunks[:N]

# Latents d'entrée
lat = []
for (x1, y1, x2, y2), f in zip(coords, frames):
    y2 = min(y2 + args.extra_margin, H)
    crop = cv2.resize(f[y1:y2, x1:x2], (256, 256), interpolation=cv2.INTER_LANCZOS4)
    lat.append(vae.get_latents_for_unet(crop))

res = []
with torch.no_grad():
    for wb, lb in datagen(whisper_chunks=chunks, vae_encode_latents=lat, batch_size=args.batch_size,
                          delay_frame=0, device=device):
        pred = unet.model(lb, timesteps, encoder_hidden_states=pe(wb)).sample
        res.extend(vae.decode_latents(pred))
t_inf = time.time() - t2

# Recomposition + encodage sans son
t3 = time.time()
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                        "-r", "30", "-i", "-", "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "14",
                        "-pix_fmt", "yuv420p", "-r", "30", args.out], stdin=subprocess.PIPE)
for i in range(N):
    x1, y1, x2, y2 = coords[i]
    y2 = min(y2 + args.extra_margin, H)
    face = cv2.resize(res[i].astype(np.uint8), (x2 - x1, y2 - y1))
    out = get_image(frames[i].copy(), face, [x1, y1, x2, y2], upper_boundary_ratio=args.upper_boundary_ratio,
                    expand=args.expand, mode=args.parsing_mode, fp=fp)
    enc.stdin.write(np.ascontiguousarray(out).tobytes())
enc.stdin.close(); enc.wait()
t_blend = time.time() - t3

stats = dict(frames=N, audio_windows=n_audio, fps=fps, load_s=round(t_load, 1), landmarks_s=round(t_lmk, 1),
             inference_s=round(t_inf, 1), blend_encode_s=round(t_blend, 1),
             total_s=round(time.time() - t0, 1), face_box_px=[int(np.mean([c[2] - c[0] for c in coords])),
                                                             int(np.mean([c[3] - c[1] for c in coords]))],
             args=vars(args))
print(json.dumps(stats))
json.dump(stats, open(os.path.splitext(args.out)[0] + ".json", "w"), indent=1)
