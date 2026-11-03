"""Apply Claude's edit (data/edit_compact.json) to Qwen/Qwen3.5-0.8B and save the edited model.

    pip install torch safetensors huggingface_hub
    python apply_edit.py ./qwen35-0.8b-edited

The edit has 4 parts (layers 15, 16, 18, 19). For each part, in that layer's MLP output matrix W (1024 x 3584):
    W[:, j] <- W[:, j] - alpha * r * (r . W[:, j])     for the 64 listed columns j
where r is a unit direction of 1024 numbers. The result matches the evaluated weights up to one bf16 rounding
step on a few dozen entries per layer.
"""
import glob, json, os, shutil, sys

import torch
from huggingface_hub import snapshot_download
from safetensors.torch import load_file, save_file

out = sys.argv[1] if len(sys.argv) > 1 else "qwen35-0.8b-edited"
spec = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "edit_compact.json")))
shutil.copytree(snapshot_download(spec["model"]), out, dirs_exist_ok=True)   # follows the cache symlinks
path = glob.glob(os.path.join(out, "*.safetensors"))[0]
weights = load_file(path)
for part in spec["parts"]:
    key = f"model.language_model.layers.{part['layer']}.mlp.down_proj.weight"
    W = weights[key].float()
    r = torch.tensor(part["direction"])
    cols = torch.tensor(part["columns"])
    W[:, cols] -= part["alpha"] * torch.outer(r, r @ W[:, cols])
    weights[key] = W.to(torch.bfloat16).contiguous()
    print(f"layer {part['layer']:2d} ({part['name']}): {len(cols)} columns, alpha = {part['alpha']:g}")
os.remove(path)
save_file(weights, path, metadata={"format": "pt"})
print("edited model saved to", out)
