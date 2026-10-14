"""Run judges over items. Resumable: responses append to runs/<run>/<judge>.jsonl and
items already answered (same prompt version) are skipped.

    uv run python -m dec_exp.run --items items/v1.jsonl --run pilot --judges checklist,jev --limit 40
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import time
from pathlib import Path

import httpx

from .models import JUDGES, PROMPT_VERSION


def load_env(path: str = ".env") -> None:
    if Path(path).exists():
        for line in Path(path).read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def select(items: list[dict], args) -> list[dict]:
    """Subset by factor filters, then by base (whole bases only, so minimal pairs stay intact)."""
    for key in ("set", "names", "register", "rule", "variant"):
        allowed = getattr(args, key)
        if allowed:
            items = [it for it in items if it[key] in allowed.split(",")]
    if args.bases:
        bases = sorted({it["base_id"] for it in items})
        keep = set(random.Random(args.seed).sample(bases, min(args.bases, len(bases))))
        items = [it for it in items if it["base_id"] in keep]
    return items[: args.limit] if args.limit else items


async def run_judge(name: str, items: list[dict], out: Path, concurrency: int) -> None:
    judge = JUDGES[name]()
    done = set()
    if out.exists():
        for line in out.read_text().splitlines():
            r = json.loads(line)
            if r.get("prompt_version") == PROMPT_VERSION and "error" not in r:
                done.add(r["item_id"])
    todo = [it for it in items if it["id"] not in done]
    print(f"[{name}] {len(todo)} to do ({len(done)} cached)")
    sem = asyncio.Semaphore(concurrency)
    cost, n_err, t0 = 0.0, 0, time.time()

    async with httpx.AsyncClient(limits=httpx.Limits(max_connections=concurrency * 3)) as client:
        with out.open("a") as f:
            async def one(it):
                nonlocal cost, n_err
                async with sem:
                    t = time.time()
                    try:
                        r = await judge.judge(client, it)
                        rec = {"item_id": it["id"], "judge": name, "prompt_version": PROMPT_VERSION,
                               "latency": round(time.time() - t, 3), **r}
                        cost += r.get("cost") or 0.0
                    except Exception as e:  # recorded, retried on the next invocation
                        n_err += 1
                        rec = {"item_id": it["id"], "judge": name, "prompt_version": PROMPT_VERSION, "error": repr(e)[:500]}
                    f.write(json.dumps(rec) + "\n")
                    f.flush()

            await asyncio.gather(*(one(it) for it in todo))
    print(f"[{name}] done in {time.time() - t0:.0f}s, cost ${cost:.4f}, errors {n_err}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default="items/v1.jsonl")
    ap.add_argument("--run", required=True)
    ap.add_argument("--judges", default="checklist,jev")
    ap.add_argument("--concurrency", type=int, default=16)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--bases", type=int, help="random subset of whole bases")
    ap.add_argument("--seed", type=int, default=0)
    for key in ("set", "names", "register", "rule", "variant"):
        ap.add_argument(f"--{key}", help="comma-separated filter")
    a = ap.parse_args()
    load_env()

    items = select([json.loads(l) for l in open(a.items)], a)
    run_dir = Path("runs") / a.run
    run_dir.mkdir(parents=True, exist_ok=True)
    # Record every item this run has touched (union across invocations).
    seen_path = run_dir / "items.jsonl"
    seen = {json.loads(l)["id"]: json.loads(l) for l in seen_path.read_text().splitlines()} if seen_path.exists() else {}
    seen |= {it["id"]: it for it in items}
    seen_path.write_text("".join(json.dumps(it) + "\n" for it in seen.values()))
    for name in a.judges.split(","):
        asyncio.run(run_judge(name, items, run_dir / f"{name}.jsonl", a.concurrency))


if __name__ == "__main__":
    main()
