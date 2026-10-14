# Run 1 results

*Pre-registered in HYPOTHESIS.md (revision 3). Run 2026-10-14 · `typesafe/jev-1.13` (snapshot `jev-1.13-20260917`) · 3,040 items × 3 samples × 2 calls · $0.50 · 0 errors. Raw data in `runs/run1/` (`report.md`, `scored.csv`).*

## Verdict

**H is not supported.** Jev shows a small, reliable sensitivity to *local* breaks: an entity with no inflow or no outflow. It shows **no detectable sensitivity to global breaks**, which change whether the system closes without changing any entity's links. It can't say where the break is. Real names *lower* its scores rather than raising them.

This matches the prior from the literature on latent multi-hop reasoning: one-hop checks show up, closure across a whole loop doesn't.

## Scorecard

`d` is the mean paired score difference (complete minus broken; > 0 means sensitive). `w` is the fraction of minimal pairs ranked correctly (0.5 = blind). Brackets are 95% bootstrap CIs over bases.

| # | Prediction | Result | Verdict |
|---|---|---|---|
| P0 | Responds to local breaks | source: `d` = 0.022 [0.02, 0.03]; sink: `d` = 0.007 [0.00, 0.01] (random set, `sustainable`) | **pass** (small: source ≈ 0.27 item-SD) |
| **P1** | **Detects global breaks** (decisive cell: random × nonce × implicit) | `d` = 0.001 [−0.005, 0.007], `w` = 0.58 [0.50, 0.65] | **fail** |
| P2 | Not recall | not testable: no global effect in either names condition | n/a |
| P3 | Localizes global breaks | `fails` mass on drained entities = 0.74× chance [0.71, 0.76] | **fail** |
| P4 | Coherence ≠ familiarity | `fam_beta` = −0.28 [−0.49, −0.15] (canonical) | **fail, in an unexpected direction** (below) |
| P5 | Vague gate question carries the signal | `coherent`: P0 passes, more strongly (source `d` = 0.036 [0.03, 0.04]); P1 fails (`d` = 0.002 [−0.005, 0.010]) | **partial**: same profile as `sustainable` |
| P6 | Eco frame helps (exploratory) | no global effect to modulate | n/a |

Overall AUROC (complete vs broken): 0.54 for `sustainable` and 0.55 for `coherent`. The local-checklist baseline gets 0.83 by construction.

## What the data show

**1. Scores barely move.** `sustainable` averages 0.40 (SD 0.08, range 0.16–0.70). Intact systems average 0.40, not above 0.5. Jev leans toward "not sustainable" for everything and nudges scores down slightly for local breaks:

| Variant | `sustainable` | `coherent` |
|---|---|---|
| intact | 0.403 | 0.433 |
| control (closed swap) | 0.404 | 0.433 |
| **global (open swap)** | **0.405** | **0.432** |
| sink | 0.396 | 0.422 |
| source | 0.381 | 0.397 |

(random set; the canonical set has the same ordering)

**2. Local sensitivity fades with size.** Source-break `d` falls from 0.033 at 7 entities to 0.011 at 15. A one-hop check spread across more sentences gets harder to see. Global `d` is about 0 at every size.

**3. Real names lower scores; they don't raise them.** On the same graphs, real names lower `sustainable` (canonical 0.35 vs 0.42 nonce; random 0.37 vs 0.42). This is the reverse of the belief-bias prediction (Dasgupta et al.). A plausible reading: real species invite real-world knowledge ("a sealed valley with just foxes and rabbits wouldn't last"), while invented ones are taken on the text's terms. Either way, the score depends on the names, not just the structure, so P4 fails, though not in the predicted direction. The manipulation check was also weak: even the canonical webs only got P(familiar) = 0.12 (vs 0.03 for nonce).

**4. One false lead, checked.** On the canonical set, `coherent` showed a borderline global effect (`d` = 0.007 [0.00, 0.014], `w` = 0.58 [0.52, 0.65]), similar with real and nonce names. All canonical webs share one topology, so that set contains only two distinct global swaps. The same swap type in random systems (nutrient → producer, 23 bases) shows nothing (`d` = 0.001, `w` = 0.50). It's treated as noise.

**5. Noise was handled.** Single samples correlate at r = 0.955 between repeats, and averaging three per item makes measurement noise negligible next to the effects reported. The global null isn't a power problem: CIs on `d` are about ±0.006 around zero, a quarter of the local effect.

## Interpretation for idea-generation filtering

In the parallel-terraced-scan framing, Jev can act as a weak **local well-formedness** screen. It slightly penalizes candidates with dangling parts, and more so when asked the vague "does this hang together?" question. That signal is small (≈ 0.3 SD), shrinks as candidates get longer, and depends on the names used. Jev showed **no sign of the "structural click"**, the sense of whether a whole closes up, that the filter was meant to supply. Ranking candidates by its score would mostly reward surface completeness.

## Post-hoc checks from a second review

A second reviewer critiqued revision 3 before seeing results. Four of their points could be tested against run 1. These checks weren't pre-registered and are reported as exploratory.

| Concern | Check | Result |
|---|---|---|
| **Nitrogen → phosphorus "alchemy."** In intact/control, cross-loop flows turn one element into another; the broken global swap un-crosses them, so chemistry knowledge could favor *global* on real names | control vs global with familiar vs nonce names | familiar names lean the predicted way (canonical `d` = −0.003 [−0.009, 0.004], `w` = 0.45), but within noise and indistinguishable from nonce. **Can't rule it out. Fixed for future runs:** nutrient pools are now compartments of one nutrient (upland/lowland nitrogen); `items/v2.jsonl` |
| **The implicit rule may not imply draining.** Without the conservation rule, a self-sufficient loop that leaks into another can look fine | P1 contrast with the rule stated (random × nonce) | `sustainable` `d` = −0.001 [−0.008, 0.006]; `coherent` `d` = 0.002 [−0.004, 0.009]. **Stating the rule doesn't help;** the null holds either way |
| **Pooling sizes could hide a small-system effect** | P1 contrast at 7 and at 7–9 entities | no effect detected (e.g. 7–9, nonce × implicit, `coherent`: `d` = 0.008 [−0.004, 0.021], `w` = 0.62 [0.49, 0.75]), **but CIs are wide** with 12 bases per size. Run 1 can't exclude a global effect in small systems; this is a real power limit |
| **Within-pair `w` hides between-candidate noise** | effect in item-SD units, plus simulated batch filtering on unmatched candidates (batches of 50, 20% complete, keep top 5) | local breaks: 0.28 SD (`sustainable`), 0.42 SD (`coherent`), giving **1.24× and 1.37× enrichment** (20% → 25–27% complete among the kept). Global breaks: ~0 SD and 0.97–0.98× enrichment, no better than random |

The batch simulation is now part of `analyze.py`. It's the most direct measure of usefulness as a filter: even where Jev has a real signal, it only modestly enriches a batch.

Two smaller notes: density is 4/3 flows per entity *rounded* (9, 12, 15, 17 and 20 flows at 7–15 entities), and the generator verifies every base and variant against computed ground truth regardless.

## Limits on this conclusion

- **One domain, one wording.** Nutrient-cycle closure is one kind of completeness. Procedural precondition checks ("step 4 uses something never made") are closer to how generated ideas fail, and are untested.
- **The decision model's question format.** A Decisions API question is short instructions plus criteria. Other question framings might elicit more, though the gate question already did a little better than the explicit one.
- **Task solvability by single-pass models generally is unknown.** We didn't run any non-decision model, by design, so we can't say whether the null is specific to Jev or a ceiling for single-pass evaluation at this size. The latent multi-hop literature suggests the latter.

## Possible next steps

1. **Procedure domain** (precondition chains), using the same minimal-pair logic and the same pipeline; it costs cents.
2. **Find the smallest global break Jev can see, with power.** Run 1 had 12 bases per size, too few to settle small systems. A focused run at the smallest sizes (dropping role constraints in the abstract register allows loops of 4–6 entities) with ~50 bases per size would cost about $0.50 and either find an integration horizon or rule one out.
3. **Re-run with `items/v2.jsonl`** (nitrogen compartments) to close the alchemy question.
4. **Investigate the reversed familiarity effect.** It's robust and the most surprising finding here.
