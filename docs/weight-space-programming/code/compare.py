"""python compare.py REF ARM [ARM ...] : accuracy / hit-limit table + exact McNemar vs REF (and optional pairs X:Y)."""
import json, sys, os
from math import comb

here = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
pairs = [a for a in args if ":" in a]
names = [a for a in args if ":" not in a]
ref = names[0]
R = {a: {r["id"]: r for r in map(json.loads, open(f"{here}/results_{a}.jsonl"))} for a in set(names + [p for q in pairs for p in q.split(":")])}


def mcnemar(a, b, key="correct_lastbox"):
    ids = sorted(set(R[a]) & set(R[b]))
    b_only = sum(R[b][i][key] and not R[a][i][key] for i in ids)
    a_only = sum(R[a][i][key] and not R[b][i][key] for i in ids)
    k, m = min(a_only, b_only), a_only + b_only
    p = min(1.0, 2 * sum(comb(m, j) for j in range(k + 1)) / 2 ** m) if m else 1.0
    return b_only, a_only, p


def gpu_s(a):
    p = f"{here}/results_{a}.jsonl"
    return None


print(f"{'arm':12}{'acc':>7}{'strict':>8}{'hit limit':>11}{'closed':>8}{'mean tok':>10}   vs {ref} (+only/-only, p)")
for a in names:
    rs = list(R[a].values()); n = len(rs)
    acc = sum(r["correct_lastbox"] for r in rs) / n
    line = (f"{a:12}{acc:>7.0%}{sum(r['correct_strict'] for r in rs) / n:>8.0%}{sum(r['finish'] == 'length' for r in rs) / n:>11.0%}"
            f"{sum(r['closed_think'] for r in rs) / n:>8.0%}{sum(r['n_tok'] for r in rs) / n:>10,.0f}")
    if a != ref:
        w, l, p = mcnemar(ref, a)
        line += f"   +{w} / -{l}  p={p:.2g}"
    print(line)
for q in pairs:
    x, y = q.split(":")
    w, l, p = mcnemar(y, x)
    print(f"pair {x} vs {y}: +{w} / -{l}  p={p:.2g}")
