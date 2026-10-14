"""Canonical, textbook-shaped food webs with their real names.

These give the familiarity manipulation teeth: a random graph with real names
isn't a *known* system, but these are. They go through exactly the same
perturbation and rendering code as random bases, and are also rendered with
nonce names (same topology, familiarity removed).
"""

from __future__ import annotations

from .systems import DECOMPOSER, GRAZER, NUTRIENT, PREDATOR, PRODUCER, System

N, P, G, X, D = NUTRIENT, PRODUCER, GRAZER, PREDATOR, DECOMPOSER


def _web(n1, n2, p1, p2, g1, g2, x1, x2, d1, d2):
    """Two nutrient loops, A (n1 ... d1 -> n1) and B (n2 ... d2 -> n2), joined because each
    plant draws on the *other* loop's nutrient, plus one-way predation from A into B.

    The two pools are compartments of the same nutrient (upland and lowland nitrogen), so
    cross-loop flows conserve elements literally.

    With a single nutrient pool every cycle passes through it, so the loop can only break
    locally. Here, swapping which nutrient each plant needs (a degree-preserving swap)
    separates the loops; A still feeds B through x2, nothing returns, and A drains.
    """
    roles = {n1: N, n2: N, p1: P, p2: P, g1: G, g2: G, x1: X, x2: X, d1: D, d2: D}
    edges = [(n2, p1), (n1, p2),                                  # cross-fed nutrients
             (p1, g1), (g1, x1), (x1, d1), (p1, d1), (d1, n1),    # loop A
             (p2, g2), (g2, x2), (x2, d2), (p2, d2), (d2, n2),    # loop B
             (g1, x2)]                                            # one-way link A -> B
    return roles, edges


CANON: dict[str, tuple[dict[str, str], list[tuple[str, str]]]] = {
    "meadow": _web("upland nitrogen", "lowland nitrogen", "clover", "grass", "rabbits", "grasshoppers", "foxes", "shrews", "earthworms", "bacteria"),
    "pond": _web("upland nitrogen", "lowland nitrogen", "algae", "pondweed", "tadpoles", "snails", "perch", "herons", "bacteria", "fungi"),
    "forest": _web("upland nitrogen", "lowland nitrogen", "oaks", "ferns", "caterpillars", "deer", "songbirds", "wolves", "fungi", "beetles"),
    "tundra": _web("upland nitrogen", "lowland nitrogen", "lichen", "sedge", "lemmings", "caribou", "snowy owls", "wolves", "fungi", "bacteria"),
    "marsh": _web("upland nitrogen", "lowland nitrogen", "reeds", "cattails", "geese", "muskrats", "harriers", "minks", "bacteria", "fungi"),
    "savanna": _web("upland nitrogen", "lowland nitrogen", "acacias", "grass", "giraffes", "zebras", "cheetahs", "lions", "termites", "bacteria"),
    "prairie": _web("upland nitrogen", "lowland nitrogen", "bluestem", "sunflowers", "bison", "prairie dogs", "wolves", "hawks", "fungi", "dung beetles"),
    "desert": _web("upland nitrogen", "lowland nitrogen", "cacti", "creosote bushes", "kangaroo rats", "jackrabbits", "rattlesnakes", "coyotes", "termites", "bacteria"),
}


def canonical(name: str) -> tuple[System, dict[str, str]]:
    """(system with role-style ids, id -> real name)."""
    names, edges = CANON[name]
    ids = {n: f"{r}_{i}" for i, (n, r) in enumerate(names.items())}
    sys = System({ids[n]: r for n, r in names.items()}, tuple((ids[u], ids[v]) for u, v in edges))
    assert sys.complete(), name
    return sys, {i: n for n, i in ids.items()}
