"""Generate the item set: bases x variants x rendering factors -> JSONL.

    uv run python -m dec_exp.generate --out items/v2.jsonl

Two sets:
  random     - procedurally sampled bases; size varies, density (edges/entity) held ~constant
  canonical  - textbook food webs (canon.py); "familiar" names are their real names
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
from collections import Counter

from .canon import CANON, canonical
from .render import render, word_count
from .systems import VARIANTS, sample_base, variants

FACTORS = {"names": ["familiar", "nonce"], "register": ["eco", "abstract"], "rule": ["stated", "implicit"]}
DENSITY = 4 / 3  # edges per entity, held constant across sizes so size isn't confounded with redundancy


def items_for(set_name: str, base_id: str, draw: int, vs: dict, canon_names: dict | None) -> list[dict]:
    out = []
    for vname in VARIANTS:
        v = vs[vname]
        sys = v["system"]
        for names, register, rule in itertools.product(*FACTORS.values()):
            r = render(sys, base_id, names, register, rule, canon_names)
            nm = r["names"]
            pos = {slot: i for i, slot in enumerate(r["order"])}
            out.append({
                "id": f"{base_id}-d{draw}-{vname}-{names[:3]}-{register[:3]}-{rule[:3]}",
                "set": set_name,
                "base_id": base_id,
                "draw": draw,
                "variant": vname,
                "names": names,
                "register": register,
                "rule": rule,
                "n_entities": len(sys.roles),
                "n_edges": len(sys.edges),
                "complete": v["complete"],
                "local_cue": v["local_cue"],
                "drained": sorted(nm[e] for e in v["drained"]),
                "changed_sentences": sorted(pos[s] for s in v["slots"]),
                "entities": sorted(nm.values()),
                "n_words": word_count(r["text"]),
                "text": r["text"],
                "graph": {"roles": {nm[e]: role for e, role in sys.roles.items()},
                          "edges": [[nm[u], nm[w]] for u, w in sys.edges]},
            })
    return out


def generate(sizes: list[int], bases_per_size: int, canon_draws: int, seed: int) -> list[dict]:
    items = []
    for n in sizes:
        b, attempt = 0, 0
        while b < bases_per_size:
            rng = random.Random(f"{seed}|{n}|{attempt}")
            attempt += 1
            if attempt > 5000:
                raise RuntimeError(f"size {n}: too few bases admit every variant")
            base = sample_base(n, round(n * DENSITY), rng)
            vs = variants(base, rng)
            if vs is None:  # base can't produce every variant; resample
                continue
            items += items_for("random", f"n{n:02d}b{b:02d}", 0, vs, None)
            b += 1
    for cname in CANON:
        base, real = canonical(cname)
        for d in range(canon_draws):
            vs = variants(base, random.Random(f"{seed}|{cname}|{d}"))
            assert vs is not None, cname
            items += items_for("canonical", f"c-{cname}", d, vs, real)
    return items


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="items/v2.jsonl")
    ap.add_argument("--sizes", default="7,9,11,13,15")
    ap.add_argument("--bases", type=int, default=12)
    ap.add_argument("--canon-draws", type=int, default=2)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    items = generate([int(s) for s in a.sizes.split(",")], a.bases, a.canon_draws, a.seed)
    with open(a.out, "w") as f:
        for it in items:
            f.write(json.dumps(it) + "\n")
    print(f"wrote {len(items)} items to {a.out}")
    print(Counter((it["set"], it["variant"], it["complete"], it["local_cue"]) for it in items))


if __name__ == "__main__":
    main()
