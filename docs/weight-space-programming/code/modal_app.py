"""Replication of the blog's Qwen3.5-0.8B MATH-500 experiment, with the blog's protocol
(vLLM 0.33.0, thinking on, temperature 0.6, top_p 0.95, top_k 20, presence_penalty 1.5, max 32,768 new tokens, seed 0,
last-\\boxed{} graded with math-verify 0.9.0), on 100 MATH-500 problems, 4 arms run in parallel on H100s:
  base     Qwen/Qwen3.5-0.8B
  blog     the blog's released edit (layers 15 and 19 down_proj)
  control  same 64 columns x 2 layers and same change norm as the blog edit, random direction
  mine     my edit from the CPU diagnosis (layers 18 and 19 down_proj)
"""
import json, os
import modal

app = modal.App("wsp-replication")
image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "vllm==0.33.0", "transformers==5.20.2", "math-verify==0.9.0", "huggingface_hub", "safetensors").env(
    {"VLLM_USE_FLASHINFER_SAMPLER": "0"})   # FlashInfer's sampler JIT-compiles with nvcc, absent from this image
results_vol = modal.Volume.from_name("wsp-results", create_if_missing=True)
SUFFIX = "\nPlease reason step by step, and put your final answer within \\boxed{}."

def _download(repo):
    """snapshot_download with retries (Hugging Face sometimes drops connections)"""
    import time
    from huggingface_hub import snapshot_download
    for attempt in range(6):
        try:
            return snapshot_download(repo)
        except Exception as e:
            print(f"download attempt {attempt + 1} failed: {e}", flush=True)
            time.sleep(5 * 2 ** attempt)
    return snapshot_download(repo)



def last_boxed(text):
    i = text.rfind("\\boxed")
    if i < 0:
        return None
    j = text.find("{", i)
    if j < 0:
        return None
    depth = 0
    for k in range(j, len(text)):
        if text[k] == "{":
            depth += 1
        elif text[k] == "}":
            depth -= 1
            if depth == 0:
                return text[j + 1:k]
    return None


@app.function(image=image, gpu="H100", timeout=3 * 3600, volumes={"/results": results_vol})
def run_arm(arm: str, edit_bytes, problems: list, max_tokens: int = 32768, return_ids: bool = False, temperature: float = 0.6, slim: bool = False) -> dict:
    import glob, shutil, time
    from huggingface_hub import snapshot_download
    t0 = time.time()
    path = _download("Qwen/Qwen3.5-0.8B")
    if edit_bytes is not None:
        from safetensors.torch import load, load_file, save_file
        new = "/tmp/model"
        shutil.copytree(path, new, dirs_exist_ok=True)          # follows the HF cache symlinks -> real files
        f = glob.glob(f"{new}/*.safetensors")[0]
        sd, ed = load_file(f), load(edit_bytes)
        for k, v in ed.items():
            assert k in sd and sd[k].shape == v.shape and sd[k].dtype == v.dtype, k
            sd[k] = v
        os.remove(f)
        save_file(sd, f, metadata={"format": "pt"})
        path = new
    import vllm
    from vllm import LLM, SamplingParams
    llm = LLM(model=path, dtype="bfloat16", max_model_len=34816, seed=0)
    tok = llm.get_tokenizer()
    prompts = [tok.apply_chat_template([{"role": "user", "content": p["problem"] + SUFFIX}], tokenize=False,
                                       add_generation_prompt=True, enable_thinking=True) for p in problems]
    sp = SamplingParams(n=1, temperature=temperature, top_p=0.95, top_k=20, presence_penalty=1.5, max_tokens=max_tokens, seed=0)
    t1 = time.time()
    outs = llm.generate(prompts, sp)
    t2 = time.time()
    from math_verify import parse, verify

    def ok(ans, gold_str):
        if ans is None:
            return False
        try:
            return bool(verify(parse("\\boxed{" + gold_str + "}"), parse("\\boxed{" + ans + "}")))
        except Exception:
            return False

    recs = []
    for p, o in zip(problems, outs):
        c = o.outputs[0]
        text = c.text
        closed = "</think>" in text
        recs.append({"id": p["id"], "level": p["level"], "n_tok": len(c.token_ids), "finish": c.finish_reason,
                     "closed_think": closed,
                     "correct_lastbox": ok(last_boxed(text), p["answer"]),
                     "correct_strict": ok(last_boxed(text.split("</think>")[-1]) if closed else None, p["answer"]),
                     "text": text, **({"token_ids": list(c.token_ids)} if return_ids else {})})
    n = len(recs)
    summary = {"arm": arm, "n": n, "vllm": vllm.__version__,
               "acc_lastbox": sum(r["correct_lastbox"] for r in recs) / n,
               "acc_strict": sum(r["correct_strict"] for r in recs) / n,
               "hit_limit": sum(r["finish"] == "length" for r in recs) / n,
               "closed_think": sum(r["closed_think"] for r in recs) / n,
               "mean_tokens": sum(r["n_tok"] for r in recs) / n,
               "gen_tokens": sum(r["n_tok"] for r in recs),
               "setup_s": round(t1 - t0), "generate_s": round(t2 - t1)}
    with open(f"/results/{arm}.jsonl", "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    with open(f"/results/{arm}_summary.json", "w") as fh:
        json.dump(summary, fh)
    results_vol.commit()
    if slim:                                          # full records stay on the volume; return a small payload
        recs = [{k: v for k, v in r.items() if k not in ("text", "token_ids")} for r in recs]
    return {"summary": summary, "records": recs}


@app.local_entrypoint()
def main(arms: str = "base,blog,control,mine", max_tokens: int = 32768, n: int = 100):
    here = os.path.dirname(os.path.abspath(__file__))
    problems = json.load(open(f"{here}/math100.json"))[:n]
    files = {"base": None, "blog": "edit_blog.safetensors", "control": "edit_control.safetensors", "mine": "edit_mine.safetensors"}
    jobs = [(a, open(f"{here}/{files[a]}", "rb").read() if files[a] else None, problems, max_tokens) for a in arms.split(",")]
    for res in run_arm.starmap(jobs, order_outputs=False):
        s = res["summary"]
        with open(f"{here}/results_{s['arm']}.jsonl", "w") as fh:
            for r in res["records"]:
                fh.write(json.dumps(r) + "\n")
        print("RESULT " + json.dumps(s), flush=True)


@app.local_entrypoint()
def eval_edits(edits: str, max_tokens: int = 32768, n: int = 100, problems_file: str = "math100.json", temperature: float = 0.6):
    here = os.path.dirname(os.path.abspath(__file__))
    problems = json.load(open(f"{here}/{problems_file}"))[:n]
    jobs = []
    for item in edits.split(","):
        name, fname = item.split("=")
        jobs.append((name, None if fname == "none" else open(f"{here}/{fname}", "rb").read(), problems, max_tokens, False, temperature, True))
    for res in run_arm.starmap(jobs, order_outputs=False):
        s_ = res["summary"]
        with open(f"{here}/results_{s_['arm']}.jsonl", "w") as fh:
            for r in res["records"]:
                fh.write(json.dumps(r) + "\n")
        print("RESULT " + json.dumps(s_), flush=True)


# ---------------------------------------------------------------- independent diagnosis on base-model traces only
def _repeat_flags(ids, n=32):
    seen, flags = set(), [False] * len(ids)
    for i in range(n - 1, len(ids)):
        g = tuple(ids[i - n + 1:i + 1])
        flags[i] = g in seen
        seen.add(g)
    return flags


def _loop_onset(flags, win=512):
    """first token index from which the trace is (almost) only verbatim repetition until the end"""
    import numpy as np
    N = len(flags)
    if N < 2 * win:
        return None
    cs = np.concatenate([[0], np.cumsum(np.array(flags, dtype=np.float32))])
    for i in range(0, N - win, 16):
        if (cs[i + win] - cs[i]) / win >= 0.9 and (cs[N] - cs[i]) / (N - i) >= 0.85:
            return i
    return None


@app.function(image=image, gpu="H100", timeout=2 * 3600, volumes={"/results": results_vol})
def diagnose(traces: list = None, max_after: int = 2048, n_keep: int = 24, volume_file: str = None,
             problems_by_id: dict = None, doubt: bool = False, edit_bytes: bytes = None) -> dict:
    """Teacher-forced passes over the base model's own traces. Classes of positions (state predicting token i):
       pre   = normal reasoning 3072..512 tokens before the verbatim-loop onset (novel 32-grams)
       onset = the 256 tokens just before the onset
       loop  = inside the verbatim loop (first 2048 tokens after onset, repeated 32-grams)
       healthy = thinking tokens of traces that finished normally"""
    import torch
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer, AutoModelForImageTextToText
    if traces is None:                                   # read the traces where run_arm wrote them (no big upload)
        traces = [json.loads(l) for l in open(f"/results/{volume_file}")]
        for t in traces:
            t["problem"] = problems_by_id[t["id"]]
    path = _download("Qwen/Qwen3.5-0.8B")
    tok = AutoTokenizer.from_pretrained(path)
    model = AutoModelForImageTextToText.from_pretrained(path, dtype=torch.bfloat16).to("cuda").eval()
    if edit_bytes is not None:                       # diagnose an already-edited model
        from safetensors.torch import load as st_load
        for k, v in st_load(edit_bytes).items():
            model.get_parameter(k).data.copy_(v.to("cuda", torch.bfloat16))
    lm = model.model.language_model
    nL = len(lm.layers)
    for t in traces:                                 # traces saved without token ids: re-tokenize the generated text
        if "token_ids" not in t:
            t["token_ids"] = tok(t["text"], add_special_tokens=False)["input_ids"]
    end_think = tok.convert_tokens_to_ids("</think>")
    C = ["pre", "onset", "loop", "healthy"] + (["doubt", "progress"] if doubt else [])
    DOUBT_W = {"Wait", "No", "But", "Or", "Hmm", "Actually", "However", "Maybe", "Hold"}
    PROG_W = {"So", "Therefore", "Thus", "Then", "Now", "Next", "Total", "Finally", "Hence"}

    def marker_positions(ids, lo, hi):
        toks = tok.convert_ids_to_tokens(ids[max(0, lo - 2):hi])
        off = max(0, lo - 2)
        dpos, ppos = [], []
        for j in range(2, len(toks)):
            i = off + j
            if i < lo:
                continue
            prev, prev2 = toks[j - 1], toks[j - 2]
            line_start = ("\u010a" in prev) or (prev.strip("\u0120") in ("*", "**") and "\u010a" in prev2)
            if not line_start:
                continue
            w = toks[j].replace("\u0120", "").strip("*")
            if w in DOUBT_W:
                dpos.append(i)
            elif w in PROG_W:
                ppos.append(i)
        return dpos, ppos
    S = {c: {"res": torch.zeros(nL + 1, 1024, dtype=torch.float64, device="cuda"),
             "act": torch.zeros(nL, 3584, dtype=torch.float64, device="cuda"), "n": 0} for c in C}
    samples = {c: [] for c in C}
    cur = {}

    def mk_hook(l):
        def h(mod, inp):
            x = inp[0][0]
            for c, P in cur.items():
                S[c]["act"][l] += x[P].double().sum(0)
        return h

    hooks = [lm.layers[l].mlp.down_proj.register_forward_pre_hook(mk_hook(l)) for l in range(nL)]
    info = []
    for ti, t in enumerate(traces):
        ids = t["token_ids"]
        flags = _repeat_flags(ids)
        onset = _loop_onset(flags)
        pos = {}
        if onset is not None and onset >= 2048:
            pos["pre"] = [i for i in range(max(128, onset - 3072), onset - 512) if not flags[i]]
            pos["onset"] = list(range(onset - 256, onset))
            pos["loop"] = [i for i in range(onset, min(len(ids), onset + max_after)) if flags[i]]
            T_end = min(len(ids), onset + max_after)
            if doubt:
                pos["doubt"], pos["progress"] = marker_positions(ids, 128, onset - 512)
        elif t["finish"] != "length" and end_think in ids:
            e = ids.index(end_think)
            pos["healthy"] = [i for i in range(128, e) if not flags[i]]
            T_end = e
            if doubt:
                pos["doubt"], pos["progress"] = marker_positions(ids, 128, e)
        else:
            info.append({"i": ti, "id": t["id"], "onset": onset, "used": False})
            continue
        prompt = tok.apply_chat_template([{"role": "user", "content": t["problem"] + SUFFIX}], tokenize=False,
                                         add_generation_prompt=True, enable_thinking=True)
        p_ids = tok(prompt)["input_ids"]
        L = len(p_ids)
        cur.clear()
        cur.update({c: torch.tensor([L + i - 1 for i in P], device="cuda") for c, P in pos.items() if len(P) >= 16})
        seq = torch.tensor([p_ids + ids[:T_end]], device="cuda")
        with torch.no_grad():
            hs = lm(input_ids=seq, output_hidden_states=True).hidden_states
            for c, P in cur.items():
                res = torch.stack([h[0, P] for h in hs]).float()
                S[c]["res"] += res.double().sum(1)
                S[c]["n"] += len(P)
                k = torch.randperm(len(P), device="cuda")[:n_keep]
                samples[c].append((ti, res[:, k].half().cpu()))
        info.append({"i": ti, "id": t["id"], "onset": onset, "used": True, "T": int(seq.shape[1]),
                     "classes": {c: len(P) for c, P in pos.items()}})
        del hs
    for h in hooks:
        h.remove()

    def auc(a, b):
        x = torch.cat([a, b]); y = torch.cat([torch.ones(len(a)), torch.zeros(len(b))])
        rk = x.argsort().argsort().float() + 1
        return ((rk[y == 1].sum() - len(a) * (len(a) + 1) / 2) / (len(a) * len(b))).item()

    def stack(c, parity):
        parts = [s for i, s in samples[c] if i % 2 == parity]
        return torch.cat(parts, 1).float() if parts else None

    table = {}
    for a_c, b_c in [("loop", "pre"), ("onset", "pre"), ("loop", "healthy"), ("onset", "healthy"), ("pre", "healthy"), ("doubt", "progress")]:
        if a_c not in samples or b_c not in samples:
            continue
        A0, B0, A1, B1 = stack(a_c, 0), stack(b_c, 0), stack(a_c, 1), stack(b_c, 1)
        if any(x is None for x in (A0, B0, A1, B1)):
            continue
        rows = []
        for l in range(nL + 1):
            d = A0[l].mean(0) - B0[l].mean(0)
            d = d / d.norm()
            rows.append(auc(A1[l] @ d, B1[l] @ d))
        table[f"{a_c}-{b_c}"] = rows
    return {"S": {c: {"res": S[c]["res"].cpu(), "act": S[c]["act"].cpu(), "n": S[c]["n"]} for c in C},
            "auc": table, "info": info}


@app.local_entrypoint()
def diag_main(max_tokens: int = 32768):
    import torch
    here = os.path.dirname(os.path.abspath(__file__))
    probs = json.load(open(f"{here}/diag100.json"))
    res = run_arm.remote("base_diag", None, probs, max_tokens, True)
    print("GEN " + json.dumps(res["summary"]), flush=True)
    by_id = {p["id"]: p for p in probs}
    recs = res["records"]
    for r in recs:
        r["problem"] = by_id[r["id"]]["problem"]
    with open(f"{here}/results_base_diag.jsonl", "w") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    out = diagnose.remote(recs)
    torch.save(out, f"{here}/diag_gpu.pt")
    used = [i for i in out["info"] if i["used"]]
    print(f"DIAG traces used: {len(used)} / {len(out['info'])}; positions per class: "
          + ", ".join(f"{c}={v['n']}" for c, v in out["S"].items()), flush=True)
    for k, rows in out["auc"].items():
        print(f"AUC {k}: " + " ".join(f"{l}:{a:.3f}" for l, a in enumerate(rows)), flush=True)


@app.local_entrypoint()
def diag_only():
    """re-run only the diagnosis on traces already saved by diag_main"""
    import torch
    here = os.path.dirname(os.path.abspath(__file__))
    probs = json.load(open(f"{here}/diag100.json"))
    out = diagnose.remote(volume_file="base_diag.jsonl", problems_by_id={p["id"]: p["problem"] for p in probs})
    torch.save(out, f"{here}/diag_gpu.pt")
    used = [i for i in out["info"] if i["used"]]
    print(f"DIAG traces used: {len(used)} / {len(out['info'])}; positions per class: "
          + ", ".join(f"{c}={v['n']}" for c, v in out["S"].items()), flush=True)
    for k, rows in out["auc"].items():
        print(f"AUC {k}: " + " ".join(f"{l}:{a:.3f}" for l, a in enumerate(rows)), flush=True)


@app.local_entrypoint()
def diag_doubt():
    import torch
    here = os.path.dirname(os.path.abspath(__file__))
    probs = json.load(open(f"{here}/diag100.json"))
    out = diagnose.remote(volume_file="base_diag.jsonl", problems_by_id={p["id"]: p["problem"] for p in probs}, doubt=True)
    torch.save(out, f"{here}/diag_gpu_doubt.pt")
    print("DIAG positions per class: " + ", ".join(f"{c}={v['n']}" for c, v in out["S"].items()), flush=True)
    for k, rows in out["auc"].items():
        print(f"AUC {k}: " + " ".join(f"{l}:{a:.3f}" for l, a in enumerate(rows)), flush=True)


@app.local_entrypoint()
def diag_edited(edit_file: str, volume_file: str, out: str):
    """diagnose the model with `edit_file` applied, on its own traces stored in the volume (`volume_file`)"""
    import torch
    here = os.path.dirname(os.path.abspath(__file__))
    probs = json.load(open(f"{here}/diag100.json"))
    out_d = diagnose.remote(volume_file=volume_file, problems_by_id={p["id"]: p["problem"] for p in probs},
                            edit_bytes=open(f"{here}/{edit_file}", "rb").read())
    torch.save(out_d, f"{here}/{out}")
    used = [i for i in out_d["info"] if i["used"]]
    print(f"DIAG2 traces used: {len(used)} / {len(out_d['info'])}; positions per class: "
          + ", ".join(f"{c}={v['n']}" for c, v in out_d["S"].items()), flush=True)
    for k, rows in out_d["auc"].items():
        print(f"AUC2 {k}: " + " ".join(f"{l}:{a:.3f}" for l, a in enumerate(rows)), flush=True)
