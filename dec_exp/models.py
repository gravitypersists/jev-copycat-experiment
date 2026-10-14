"""Judges: the decision model (Jev) and a no-model local-checklist baseline.

Jev answers two separate requests per item:

  main call (bundled; bundling was checked and doesn't shift `sustainable`):
    sustainable (noul)   P(everything named can persist)            -> discrimination
    fails       (choice) which entity most clearly can't persist    -> localization
    familiar    (noul)   P(this is a well-known system)             -> manipulation check / disentanglement
  gate call (separate, unprimed, stimulus framed as a proposed design):
    coherent    (noul)   P(the design hangs together)               -> the vague question a pipeline gate would ask

Jev is not deterministic (harness retest: 23% of scores identical, max diff 0.08), so
each call is repeated `samples` times and answers are averaged; raw samples are kept.

Normalized answer shape:
  {"sustainable": float, "familiar": float, "coherent": float, "fails": {option: prob}}
"""

from __future__ import annotations

import asyncio
import json
import os
import random

import httpx

OR = "https://openrouter.ai/api"
PROMPT_VERSION = "q3"

DESIGN_FRAME = "Here is a proposed design for a self-sustaining system.\n\n"


def questions(item: dict) -> dict:
    # Option order is shuffled per base+rendering (not per variant), so minimal pairs see
    # identical option lists and "none" has no fixed position.
    opts = ["none"] + list(item["entities"])
    random.Random(f"{item['base_id']}|{item['names']}|{item['register']}|{item['rule']}").shuffle(opts)
    fails = {o: "Everything named can persist indefinitely." if o == "none"
             else f"{o} cannot persist indefinitely." for o in opts}
    return {
        "sustainable": {
            "type": "noul",
            "instructions": "Using only what is described, can everything named persist indefinitely?",
            "criteria": {
                "true": "The system as described sustains itself indefinitely.",
                "false": "Over time, something named would be depleted or die out.",
            },
        },
        "fails": {
            "type": "choice",
            "instructions": "Using only what is described, which named entity most clearly cannot persist indefinitely, if any?",
            "criteria": fails,
        },
        "familiar": {
            "type": "noul",
            "instructions": "Is this a well-known, commonly described real-world system?",
            "criteria": {
                "true": "A widely known real system that appears in textbooks or common knowledge.",
                "false": "An unfamiliar, invented, or unusual system.",
            },
        },
    }


GATE = {
    "coherent": {
        "type": "noul",
        "instructions": "Does this design hang together?",
        "criteria": {
            "true": "The parts fit together into a whole that works.",
            "false": "Something about how the parts fit together doesn't work.",
        },
    }
}


def _headers() -> dict:
    return {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}", "Content-Type": "application/json"}


async def _post(client: httpx.AsyncClient, path: str, body: dict, tries: int = 6) -> dict:
    for attempt in range(tries):
        try:
            r = await client.post(OR + path, json=body, headers=_headers(), timeout=180)
            if r.status_code in (429, 500, 502, 503, 524, 529):
                raise httpx.HTTPStatusError(r.text[:300], request=r.request, response=r)
            if r.status_code >= 400:
                raise RuntimeError(f"{r.status_code}: {r.text[:400]}")
            data = r.json()
            if "error" in data:
                raise RuntimeError(data["error"])
            return data
        except (httpx.HTTPError, RuntimeError, json.JSONDecodeError) as e:
            if attempt == tries - 1 or (isinstance(e, RuntimeError) and str(e)[:3] in ("400", "401", "402", "403", "404")):
                raise
            await asyncio.sleep(2 ** attempt)
    raise AssertionError


class Jev:
    kind = "decision"

    def __init__(self, model: str = "typesafe/jev-1.13", samples: int = 3):
        self.model, self.samples = model, samples

    async def _once(self, client: httpx.AsyncClient, item: dict) -> tuple[dict, float, str]:
        main, gate = await asyncio.gather(
            _post(client, "/alpha/decisions", {"model": self.model, "state": item["text"], "questions": questions(item)}),
            _post(client, "/alpha/decisions", {"model": self.model, "state": DESIGN_FRAME + item["text"], "questions": GATE}),
        )
        a, g = main["answers"], gate["answers"]
        ans = {
            "sustainable": a["sustainable"]["noul"],
            "familiar": a["familiar"]["noul"],
            "coherent": g["coherent"]["noul"],
            "fails": a["fails"].get("probabilities") or {a["fails"]["choice"]: 1.0},
        }
        cost = (main.get("usage", {}).get("cost") or 0.0) + (gate.get("usage", {}).get("cost") or 0.0)
        return ans, cost, main.get("model")

    async def judge(self, client: httpx.AsyncClient, item: dict) -> dict:
        runs = await asyncio.gather(*(self._once(client, item) for _ in range(self.samples)))
        samples = [r[0] for r in runs]
        mean = {k: sum(s[k] for s in samples) / len(samples) for k in ("sustainable", "familiar", "coherent")}
        opts = set().union(*(s["fails"] for s in samples))
        mean["fails"] = {o: sum(s["fails"].get(o, 0.0) for s in samples) / len(samples) for o in opts}
        return {"answers": mean, "samples": samples, "served_by": runs[0][2], "cost": sum(r[1] for r in runs)}


class Checklist:
    """No-model baseline: the purely local strategy. Reads the true graph and flags a system
    as broken iff some entity has no inflow or no outflow. Perfect on source/sink by
    construction, blind on global breaks (where every entity keeps its degree)."""

    kind = "baseline"

    async def judge(self, client, item: dict) -> dict:
        ins = {e: 0 for e in item["entities"]}
        outs = dict(ins)
        for u, v in item["graph"]["edges"]:
            outs[u] += 1
            ins[v] += 1
        flagged = [e for e in item["entities"] if ins[e] == 0 or outs[e] == 0]
        fails = {"none": 0.0 if flagged else 1.0} | {e: (1 / len(flagged) if e in flagged else 0.0) for e in item["entities"]}
        s = fails["none"]
        return {"answers": {"sustainable": s, "familiar": 0.5, "coherent": s, "fails": fails}, "served_by": "checklist", "cost": 0.0}


JUDGES = {
    "jev": lambda: Jev("typesafe/jev-1.13"),
    "checklist": lambda: Checklist(),
}
