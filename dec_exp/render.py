"""Render systems as prose under the experimental factors.

Factors (crossed, applied identically to every variant of a base so the
variants form minimal pairs):
  names    - familiar (real organisms/nutrients) | nonce (invented words)
  register - eco (ecological verbs + valley frame) | abstract (neutral "flows into")
  rule     - stated (conservation rule spelled out) | implicit (left to the schema)

Every sentence is one flow; there are no filler sentences. A variant differs
from intact only in the slots (edge indices) it changed.
"""

from __future__ import annotations

import random
import re
from functools import lru_cache

from .systems import DECOMPOSER, GRAZER, NUTRIENT, PREDATOR, PRODUCER, System

FAMILIAR = {
    # Nutrient pools are compartments of one nutrient, not different elements: with different
    # elements, cross-loop flows would turn nitrogen into phosphorus, and a model that knows
    # chemistry could prefer the broken (uncrossed) variant for the right reason.
    NUTRIENT: ["upland nitrogen", "lowland nitrogen", "streambed nitrogen", "hillside nitrogen", "marsh nitrogen",
               "forest-floor nitrogen"],
    PRODUCER: ["clover", "ferns", "sedge", "moss", "wildflowers", "algae", "grass"],
    GRAZER: ["rabbits", "voles", "deer", "snails", "grasshoppers", "mice"],
    PREDATOR: ["foxes", "hawks", "owls", "weasels", "snakes", "stoats"],
    DECOMPOSER: ["fungi", "earthworms", "bacteria", "woodlice", "millipedes", "slime molds"],
}

ECO = {
    (NUTRIENT, PRODUCER): ["{V} cannot grow without {u}.", "Without {u}, {v} cannot grow."],
    (PRODUCER, GRAZER): ["{V} feed on {u}.", "{V} graze on {u}."],
    (GRAZER, PREDATOR): ["{V} hunt {u}.", "{V} prey on {u}."],
    (PRODUCER, DECOMPOSER): ["{V} break down dead {u}.", "{V} live on the remains of {u}."],
    (GRAZER, DECOMPOSER): ["{V} break down dead {u}.", "{V} live on the remains of {u}."],
    (PREDATOR, DECOMPOSER): ["{V} break down dead {u}.", "{V} live on the remains of {u}."],
    (DECOMPOSER, NUTRIENT): ["{U} return {v} to the soil.", "{U} release {v} as they feed."],
}
ABSTRACT = ["{U} can flow into {v}.", "{V} can draw on {u}.", "{U} can pass to {v}."]

PREAMBLE = {
    "eco": "A sealed valley. Sunlight and rain are plentiful, but no living things or nutrients enter or leave it; every one of them is named below.",
    "abstract": "A closed system. Nothing enters or leaves it, and every entity in it is named below.",
}
RULE = {
    "eco": "Nothing is created or destroyed: living things and nutrients are replenished only by what passes to them along the relationships below, and whatever passes out of something is gone from it unless it eventually comes back around.",
    "abstract": "Quantity is conserved and only moves along the flows below: an entity is replenished only by what flows into it, and whatever flows out of it is gone unless it eventually flows back.",
}


@lru_cache(maxsize=1)
def _english() -> set[str]:
    try:
        with open("/usr/share/dict/words") as f:
            return {w.strip().lower() for w in f}
    except OSError:
        return set()


def nonce_word(rng: random.Random, taken: set[str]) -> str:
    onsets = ["b", "d", "g", "gl", "k", "m", "n", "p", "pl", "r", "s", "sp", "t", "tr", "v", "z", "dr", "br", "fl"]
    vowels = ["a", "e", "i", "o", "u", "ae", "oo"]
    codas = ["ll", "rr", "m", "n", "sk", "nd", "x", "th", "l", "rn"]
    while True:
        w = rng.choice(onsets) + rng.choice(vowels) + rng.choice(codas)
        if rng.random() < 0.5:
            w += rng.choice(["ow", "el", "ick", "a", "ent", "ith"])
        if 4 <= len(w) <= 9 and w not in _english() and w not in taken and w + "s" not in _english():
            return w


def assign_names(sys: System, names: str, rng: random.Random, canon: dict[str, str] | None) -> dict[str, str]:
    if names == "familiar" and canon:
        return dict(canon)
    out: dict[str, str] = {}
    if names == "familiar":
        pools = {r: rng.sample(v, len(v)) for r, v in FAMILIAR.items()}
        for e, r in sys.roles.items():
            out[e] = pools[r].pop()
    else:
        taken: set[str] = set()
        for e, r in sys.roles.items():
            w = nonce_word(rng, taken)
            taken.add(w)
            out[e] = w if r == NUTRIENT else w + "s"
    return out


def _cap(s: str) -> str:
    return s[:1].upper() + s[1:]


def render(sys: System, base_key: str, names: str, register: str, rule: str, canon: dict[str, str] | None = None) -> dict:
    """Randomness (names, templates, order) is keyed only by base and factors, so every
    variant of a base shares names, wording and sentence order."""
    key = f"{base_key}|{names}|{register}|{rule}"
    name = assign_names(sys, names, random.Random(key), canon)

    def sentence(slot: int, u: str, v: str) -> str:
        pair = (sys.roles[u], sys.roles[v])
        r = random.Random(f"{key}|{slot}|{pair}")
        tmpl = r.choice(ECO[pair] if register == "eco" else ABSTRACT)
        kw = {"u": name[u], "v": name[v]}
        return tmpl.format(**kw, **{k.upper(): _cap(x) for k, x in kw.items()})

    order = list(range(len(sys.edges)))
    random.Random(key + "|order").shuffle(order)
    sentences = [sentence(i, *sys.edges[i]) for i in order]
    head = PREAMBLE[register] + (" " + RULE[register] if rule == "stated" else "")
    return {"text": head + "\n\n" + " ".join(sentences), "names": name, "order": order}


def word_count(text: str) -> int:
    return len(re.findall(r"\w+", text))
