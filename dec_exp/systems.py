"""Closed systems of flows: dependency graphs with computable completeness.

A system is a directed graph of entities; edge (u, v) means "u flows into v"
(v feeds on / is supplied by u). Semantics are *conservation*: matter is never
created or destroyed, it only moves along edges. In the long run matter drains
out of any part of the graph that it cannot flow back to, and pools in the
closed (terminal) strongly connected components. So:

    an entity persists  <=>  it lies in a terminal SCC
    a system is complete <=> every entity persists (for a connected graph: it is strongly connected)

This is deliberately *not* checkable locally: an entity can have both a
supplier and a consumer and still be drained.

Every base graph is generated complete. Variants keep the same number of
sentences, all of them relational, and change only edges:

  intact   - the base graph                                          -> complete
  control  - degree-preserving swap of two edges, still closed       -> complete
  global   - degree-preserving swap of two edges that opens the loop  -> broken
             (every entity keeps its exact in/out degree: no local cue)
  source   - one edge re-targeted so an entity loses its only inflow -> broken (local: in-degree 0)
  sink     - one edge re-sourced so an entity loses its only outflow -> broken (local: out-degree 0)

Swaps and rewires respect ecological roles, so every sentence stays sensible.
Edge lists are index-aligned with the base, so a variant differs from intact
only in the slots it changed.
"""

from __future__ import annotations

import itertools
import random
from dataclasses import dataclass

NUTRIENT, PRODUCER, GRAZER, PREDATOR, DECOMPOSER = "nutrient", "producer", "grazer", "predator", "decomposer"
ROLES = [NUTRIENT, PRODUCER, GRAZER, PREDATOR, DECOMPOSER]

# (supplier role, consumer role) pairs that make ecological sense.
ALLOWED = {
    (NUTRIENT, PRODUCER),
    (PRODUCER, GRAZER),
    (GRAZER, PREDATOR),
    (PRODUCER, DECOMPOSER),
    (GRAZER, DECOMPOSER),
    (PREDATOR, DECOMPOSER),
    (DECOMPOSER, NUTRIENT),
}

VARIANTS = ["intact", "control", "global", "source", "sink"]
COMPLETE = {"intact": True, "control": True, "global": False, "source": False, "sink": False}


@dataclass(frozen=True)
class System:
    roles: dict[str, str]  # entity id -> role
    edges: tuple[tuple[str, str], ...]  # (supplier, consumer), index-aligned across variants

    def reach(self) -> dict[str, set[str]]:
        adj = {n: [v for u, v in self.edges if u == n] for n in self.roles}
        out = {}
        for s in self.roles:
            seen, stack = {s}, [s]
            while stack:
                for w in adj[stack.pop()]:
                    if w not in seen:
                        seen.add(w)
                        stack.append(w)
            out[s] = seen
        return out

    def drained(self) -> set[str]:
        """Entities outside every terminal SCC: matter flows out and never comes back."""
        r = self.reach()
        return {a for a in self.roles if any(a not in r[b] for b in r[a])}

    def complete(self) -> bool:
        return not self.drained()

    def degrees(self) -> dict[str, tuple[int, int]]:
        return {n: (sum(v == n for _, v in self.edges), sum(u == n for u, _ in self.edges)) for n in self.roles}


def sample_base(n_ent: int, n_edges: int, rng: random.Random, max_tries: int = 50000) -> System:
    """Rejection-sample a strongly connected, role-consistent system of exact size."""
    for _ in range(max_tries):
        counts = {NUTRIENT: 1, PRODUCER: 1, DECOMPOSER: 1, GRAZER: 0, PREDATOR: 0}
        for _ in range(n_ent - 3):
            counts[rng.choice(ROLES)] += 1
        # Predators need grazers; cap per-role counts so familiar name pools never run dry.
        if (counts[PREDATOR] and not counts[GRAZER]) or max(counts.values()) > 5:
            continue
        roles = {f"{r}{i}": r for r in ROLES for i in range(counts[r])}
        by_role = {r: [e for e, rr in roles.items() if rr == r] for r in ROLES}
        edges: set[tuple[str, str]] = set()
        for v, rv in roles.items():
            ups = [u for (ru, rv2) in ALLOWED if rv2 == rv for u in by_role[ru]]
            for u in rng.sample(ups, min(len(ups), rng.choice([1, 1, 2]))):
                edges.add((u, v))
        for u, ru in roles.items():
            if not any(e[0] == u for e in edges):
                downs = [v for (ru2, rv) in ALLOWED if ru2 == ru for v in by_role[rv]]
                edges.add((u, rng.choice(downs)))
        sys = System(roles, tuple(rng.sample(sorted(edges), len(edges))))
        if len(edges) == n_edges and sys.complete():
            return sys
    raise RuntimeError(f"could not sample a base with {n_ent} entities / {n_edges} edges")


def _replace(sys: System, changes: dict[int, tuple[str, str]]) -> System:
    return System(sys.roles, tuple(changes.get(i, e) for i, e in enumerate(sys.edges)))


def swaps(base: System) -> tuple[list[dict], list[dict]]:
    """All role-preserving double-edge swaps, split into (still complete, broken)."""
    ok, broken = [], []
    E = set(base.edges)
    for i, j in itertools.combinations(range(len(base.edges)), 2):
        (u1, v1), (u2, v2) = base.edges[i], base.edges[j]
        if u1 == u2 or v1 == v2 or base.roles[u1] != base.roles[u2] or base.roles[v1] != base.roles[v2]:
            continue
        if (u1, v2) in E or (u2, v1) in E:
            continue
        s = _replace(base, {i: (u1, v2), j: (u2, v1)})
        (ok if s.complete() else broken).append({"system": s, "slots": [i, j]})
    return ok, broken


def rewires(base: System, kind: str) -> list[dict]:
    """Single-edge rewires that leave one entity with no inflow (source) or no outflow (sink)."""
    deg, E, out = base.degrees(), set(base.edges), []
    for i, (u, v) in enumerate(base.edges):
        if kind == "source" and deg[v][0] == 1:
            for w, rw in base.roles.items():
                if w != v and (base.roles[u], rw) in ALLOWED and (u, w) not in E:
                    out.append({"system": _replace(base, {i: (u, w)}), "slots": [i], "target": v})
        if kind == "sink" and deg[u][1] == 1:
            for x, rx in base.roles.items():
                if x != u and (rx, base.roles[v]) in ALLOWED and (x, v) not in E:
                    out.append({"system": _replace(base, {i: (x, v)}), "slots": [i], "target": u})
    return out


def variants(base: System, rng: random.Random) -> dict[str, dict] | None:
    """One draw of each variant, or None if this base can't produce all of them."""
    assert base.complete()
    ok, broken = swaps(base)
    src, snk = rewires(base, "source"), rewires(base, "sink")
    if not (ok and broken and src and snk):
        return None
    out = {
        "intact": {"system": base, "slots": []},
        "control": rng.choice(ok),
        "global": rng.choice(broken),
        "source": rng.choice(src),
        "sink": rng.choice(snk),
    }
    for name, v in out.items():
        s: System = v["system"]
        v["complete"] = s.complete()
        v["drained"] = sorted(s.drained())
        assert v["complete"] == COMPLETE[name], name
        deg = s.degrees()
        v["local_cue"] = any(i == 0 or o == 0 for i, o in deg.values())
        if name in ("control", "global"):
            assert deg == base.degrees()  # no local cue by construction
    return out
