"""Score judges against computed ground truth.

    uv run python -m dec_exp.analyze --run pilot

Minimal-pair contrasts (each within base x draw x rendering; higher score = "closes"):
  global_vs_control  the core test: same degree sequence, same mentions, only topology differs
  global_vs_intact
  source_vs_intact   local break (an entity loses its only inflow)
  sink_vs_intact     local break (an entity loses its only outflow)
For each: `d_<pair>` mean paired difference (complete minus broken; > 0 = sensitive) and
`w_<pair>` win rate (ties = 0.5). Both are computed for `sustainable` (asked explicitly) and
`coherent` (the vague gate question, asked separately).

Other metrics:
  auroc       complete vs broken over all items
  loc_lift    on global items: P(fails ∈ drained set) / chance
  fam_gap     mean P(familiar), familiar minus nonce names (manipulation check)
  fam_beta    OLS coefficient of P(familiar) on score, controlling for truth (canonical set)
  retest_r    correlation between two independent samples of `sustainable` (noise ceiling)
95% CIs are bootstrap over bases (the unit minimal pairs share).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

RENDER = ["names", "register", "rule"]
PAIR_KEY = ["judge", "set", "base_id", "draw", *RENDER]
CONTRASTS = {"gc": ("control", "global"), "gi": ("intact", "global"), "si": ("intact", "source"), "ki": ("intact", "sink")}


def auroc(scores: np.ndarray, labels: np.ndarray) -> float:
    pos, neg = scores[labels], scores[~labels]
    if len(pos) == 0 or len(neg) == 0:
        return np.nan
    ranks = pd.Series(np.concatenate([pos, neg])).rank().to_numpy()
    return (ranks[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def load(run: Path) -> pd.DataFrame:
    items = {json.loads(l)["id"]: json.loads(l) for l in (run / "items.jsonl").read_text().splitlines()}
    rows = []
    for f in sorted(run.glob("*.jsonl")):
        if f.name == "items.jsonl":
            continue
        latest = {}
        for line in f.read_text().splitlines():
            r = json.loads(line)
            if "error" not in r and r["item_id"] in items:
                latest[r["item_id"]] = r  # last answer wins
        for iid, r in latest.items():
            it, a = items[iid], r["answers"]
            drained, fails = set(it["drained"]), a["fails"]
            samples = r.get("samples") or []
            rows.append({
                **{k: it[k] for k in ["id", "set", "base_id", "draw", "variant", *RENDER, "n_entities", "complete", "local_cue"]},
                "judge": r["judge"],
                "sustainable": a["sustainable"],
                "coherent": a.get("coherent", np.nan),
                "familiar": a["familiar"],
                "loc_mass": sum(p for o, p in fails.items() if o in drained) if drained else np.nan,
                "loc_chance": len(drained) / (it["n_entities"] + 1) if drained else np.nan,
                "s1": samples[0]["sustainable"] if len(samples) > 1 else np.nan,
                "s2": samples[1]["sustainable"] if len(samples) > 1 else np.nan,
                "cost": r.get("cost") or 0.0,
            })
    return pd.DataFrame(rows)


def paired(df: pd.DataFrame, a: str, b: str, score: str) -> pd.DataFrame:
    x = df[df.variant == a].set_index(PAIR_KEY)[score].rename("a")
    y = df[df.variant == b].set_index(PAIR_KEY)[score].rename("b")
    j = pd.concat([x, y], axis=1).dropna()
    j["d"] = j.a - j.b
    j["w"] = np.sign(j.d) * 0.5 + 0.5
    return j


def metrics(df: pd.DataFrame, score: str = "sustainable") -> dict:
    out = {"n": len(df)}
    uniq = df.drop_duplicates(["judge", "set", "base_id", "variant", *RENDER, "draw"])
    out["auroc"] = auroc(uniq[score].to_numpy(), uniq.complete.to_numpy(bool))
    for k, (a, b) in CONTRASTS.items():
        p = paired(df, a, b, score)
        out[f"d_{k}"] = p.d.mean() if len(p) else np.nan
        out[f"w_{k}"] = p.w.mean() if len(p) else np.nan
    br = df[df.variant == "global"]  # sink localization is counterintuitive under conservation; score global only
    out["loc_lift"] = br.loc_mass.mean() / br.loc_chance.mean() if len(br) else np.nan
    out["fam_gap"] = df[df.names == "familiar"].familiar.mean() - df[df.names == "nonce"].familiar.mean()
    if df.familiar.std() > 0 and df.complete.nunique() == 2:
        X = np.column_stack([np.ones(len(df)), df.complete.astype(float), df.familiar])
        out["fam_beta"] = np.linalg.lstsq(X, df[score].to_numpy(), rcond=None)[0][2]
    else:
        out["fam_beta"] = np.nan
    ok = df[["s1", "s2"]].dropna()
    out["retest_r"] = ok.s1.corr(ok.s2) if len(ok) > 2 else np.nan
    return out


def bootstrap(df: pd.DataFrame, keys: list[str], score: str, n: int, seed: int = 0) -> dict[str, tuple[float, float]]:
    rng = np.random.default_rng(seed)
    groups = {b: g for b, g in df.groupby("base_id")}
    bases = list(groups)
    draws = []
    for _ in range(n):
        pick = rng.choice(len(bases), len(bases))
        sample = pd.concat([groups[bases[i]].assign(base_id=f"{bases[i]}#{k}") for k, i in enumerate(pick)])
        draws.append(metrics(sample, score))
    return {k: tuple(np.nanpercentile([d[k] for d in draws], [2.5, 97.5])) for k in keys}


def batch_enrichment(df: pd.DataFrame, good: str, bad: str, score: str, batch: int = 50, keep: int = 5,
                     base_rate: float = 0.2, n: int = 4000, seed: int = 0) -> dict:
    """Draw batches of distinct candidates (good = complete, bad = broken, each from any base and
    rendering), keep the top-k by score, and report how often the kept ones are complete."""
    rng = np.random.default_rng(seed)
    pos, neg = df[df.variant == good][score].to_numpy(), df[df.variant == bad][score].to_numpy()
    n_pos = round(batch * base_rate)
    hits = 0
    for _ in range(n):
        s = np.concatenate([rng.choice(pos, n_pos, replace=False), rng.choice(neg, batch - n_pos, replace=False)])
        s = s + rng.uniform(0, 1e-9, len(s))  # break ties randomly
        hits += (np.argsort(-s)[:keep] < n_pos).sum()
    precision = hits / (n * keep)
    return {"base_rate": base_rate, "precision_top": precision, "enrichment": precision / base_rate}


def fmt(v) -> str:
    if isinstance(v, str):
        return v
    return "—" if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v:.3f}" if isinstance(v, float) else str(v)


def table(rows: list[dict], cols: list[str]) -> str:
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(fmt(r.get(c)) for c in cols) + " |" for r in rows]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--boot", type=int, default=500)
    a = ap.parse_args()
    run = Path("runs") / a.run
    df = load(run)
    out = []
    pair_cols = ["d_gc", "w_gc", "d_gi", "d_si", "d_ki"]

    for score in ("sustainable", "coherent"):
        rows = []
        for (judge, set_), g in df.groupby(["judge", "set"]):
            m = metrics(g, score)
            ci = bootstrap(g, ["d_gc", "w_gc", "d_si", "d_ki"], score, a.boot) if judge != "checklist" else {}
            rows.append({"judge": judge, "set": set_, **m, "cost": g.cost.sum(),
                         **{k: f"{m[k]:.3f} [{lo:.2f}, {hi:.2f}]" for k, (lo, hi) in ci.items()}})
        out += [f"## `{score}`: overall (95% CI over bases)",
                table(rows, ["judge", "set", "n", "auroc", *pair_cols, "loc_lift", "retest_r", "cost"])]

    # The key comparison: does the global contrast survive with nonce names and an implicit rule?
    cell_rows = [{"judge": j, "set": s, "names": n, "register": r, "rule": ru, **metrics(g)}
                 for (j, s, n, r, ru), g in df[df.judge != "checklist"].groupby(["judge", "set", *RENDER])]
    out += ["## `sustainable` by rendering cell", table(cell_rows, ["judge", "set", "names", "register", "rule", "n", *pair_cols, "fam_gap"])]

    fam_rows = [{"judge": j, "set": s, **metrics(g)} for (j, s), g in df[df.judge != "checklist"].groupby(["judge", "set"])]
    out += ["## Familiarity", table(fam_rows, ["judge", "set", "fam_gap", "fam_beta"])]

    dose = df[(df.set == "random") & (df.judge != "checklist")]
    dose_rows = [{"judge": j, "n_entities": e, **metrics(g)} for (j, e), g in dose.groupby(["judge", "n_entities"])]
    out += ["## Dose-response (random set, `sustainable`)", table(dose_rows, ["judge", "n_entities", "n", *pair_cols])]

    # Filter usefulness on *unmatched* candidates: minimal pairs hide between-item nuisance variance,
    # a real batch doesn't. Effect size in item-SD units, and simulated top-k enrichment.
    batch_rows = []
    for (judge, score), (good, bad) in [((j, s), c) for j in df.judge.unique() for s in ("sustainable", "coherent")
                                        for c in (("intact", "source"), ("control", "global"))]:
        g = df[(df.judge == judge) & (df.set == "random")]
        sd_item = g[g.variant == good][score].std()  # spread across distinct candidates (base x rendering)
        d = paired(g, good, bad, score).d.mean()
        batch_rows.append({"judge": judge, "score": score, "contrast": f"{good} vs {bad}", "d": d,
                           "d_per_sd": d / sd_item if sd_item > 0 else np.nan,
                           **batch_enrichment(g, good, bad, score)})
    out += ["## Batch filtering on unmatched candidates (random set; batches of 50, keep top 5, 20% complete)",
            table(batch_rows, ["judge", "score", "contrast", "d", "d_per_sd", "base_rate", "precision_top", "enrichment"])]

    report = "\n\n".join(out)
    (run / "report.md").write_text(report + "\n")
    df.to_csv(run / "scored.csv", index=False)
    print(report)


if __name__ == "__main__":
    main()
