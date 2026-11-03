"""Build a sparse edit from the GPU diagnosis (base-model traces only).
direction r = mean residual(pos class) - mean residual(neg class) at --res-layer, normalized
attribution: neuron j of MLP layer l writes c_j = (mean act_pos - mean act_neg)_j * (r . W_down[:, j]) extra along r
edit: in the top --n-layers layers (by sum of c_j), for the top --k neurons by c_j:  W[:, j] <- W[:, j] - r (r . W[:, j])
control (--control-out): same neurons, same coefficients (r . W[:, j]), but a random direction orthogonal to r."""
import argparse, torch
from safetensors import safe_open
from safetensors.torch import save_file

ap = argparse.ArgumentParser()
ap.add_argument("--diag"); ap.add_argument("--model"); ap.add_argument("--pos"); ap.add_argument("--neg")
ap.add_argument("--res-layer", type=int); ap.add_argument("--n-layers", type=int, default=2); ap.add_argument("--k", type=int, default=64)
ap.add_argument("--out"); ap.add_argument("--control-out", default=None); ap.add_argument("--seed", type=int, default=7)
ap.add_argument("--show", action="store_true", help="only print per-layer diagnostics")
ap.add_argument("--alpha", type=float, default=1.0, help="1 = remove the direction from the neurons, >1 = reverse it")
a = ap.parse_args()
D = torch.load(a.diag)
S = D["S"]
mu = {c: S[c]["res"] / max(1, S[c]["n"]) for c in S}
mact = {c: S[c]["act"] / max(1, S[c]["n"]) for c in S}
f = safe_open(f"{a.model}/model.safetensors-00001-of-00001.safetensors", "pt")
name = lambda l: f"model.language_model.layers.{l}.mlp.down_proj.weight"
W = {l: f.get_tensor(name(l)).float() for l in range(24)}
key = f"{a.pos}-{a.neg}"
auc = D["auc"].get(key)
diff = [(mu[a.pos][l] - mu[a.neg][l]).norm().item() for l in range(25)]
print(f"contrast {key}:  n_pos={S[a.pos]['n']}  n_neg={S[a.neg]['n']}")
print("layer: " + " ".join(f"{l:>5d}" for l in range(25)))
print("AUC  : " + " ".join(f"{x:5.3f}" for x in auc))
print("|d|  : " + " ".join(f"{x:5.2f}" for x in diff))
if a.show:
    raise SystemExit
r = (mu[a.pos][a.res_layer] - mu[a.neg][a.res_layer]).float(); r = r / r.norm()
dact = (mact[a.pos] - mact[a.neg]).float()
contrib = {l: dact[l] * (r @ W[l]) for l in range(a.res_layer)}
print(f"\nMLP layers writing r (direction at residual layer {a.res_layer}), mean extra write pos-neg:")
print("  " + "  ".join(f"L{l}:{contrib[l].sum():+.2f}" for l in range(a.res_layer)))
layers = sorted(contrib, key=lambda l: -contrib[l].sum().item())[:a.n_layers]
g = torch.Generator().manual_seed(a.seed); rr = torch.randn(1024, generator=g); rr = rr - (rr @ r) * r; rr = rr / rr.norm()
edit, ctrl, n = {}, {}, 0
for l in layers:
    J = contrib[l].topk(a.k).indices
    coef = r @ W[l][:, J]
    We = W[l].clone(); We[:, J] -= a.alpha * torch.outer(r, coef); edit[name(l)] = We.to(torch.bfloat16).contiguous()
    Wc = W[l].clone(); Wc[:, J] -= a.alpha * torch.outer(rr, coef); ctrl[name(l)] = Wc.to(torch.bfloat16).contiguous()
    n += 1024 * a.k
    print(f"layer {l}: {a.k} neurons carry {contrib[l][J].sum() / contrib[l].sum():.0%} of the layer's write along r")
save_file(edit, a.out)
if a.control_out:
    save_file(ctrl, a.control_out)
print(f"edit (alpha={a.alpha:g}): layers {sorted(layers)}, {n:,} weights ({n / 852e6:.4%}); saved {a.out}" + (f" and control {a.control_out}" if a.control_out else ""))
torch.save({"r": r, "layers": layers, "res_layer": a.res_layer, "pos": a.pos, "neg": a.neg}, a.out.replace(".safetensors", "_meta.pt"))
