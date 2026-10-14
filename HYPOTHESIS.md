# Hypothesis: do decision models sense structural completeness?

*Revision 3. Revision 2 incorporated an external review of revision 1 (see "What changed" at the end); revision 3 adds related work.*

## Why we're asking

Generative models used for novel idea generation tend toward mode homogenization: run the same system again and it returns to the same ideas. LLM assistance raises the quality of individual outputs but shrinks the diversity of what a group produces (Doshi & Hauser, 2024). Part of the cause appears to be *typicality bias*: preference data favors familiar text, so models and the evaluators trained on that data drift toward the mode (Zhang et al., 2025).

One alternative comes from Hofstadter's *parallel terraced scan* (the Copycat architecture): run many cheap, shallow probes in parallel and give deeper exploration only to those that look promising. Cheap evaluation is what makes broad exploration affordable. Applied to idea generation: produce a flood of far-flung candidates from new starting points, then let a fast, intuitive filter drop the ones that "don't hang together".

A decision model like Jev (TypeSafe; marketed as a "System One" model) is a candidate for that filter. It is fast (~$0.00003 per judgment), and it returns probabilities instead of prose. The design depends on one property: **the filter has to recognize whether a structure is coherent and complete, separately from whether it is familiar, and separately from simple local cues.** If its sense of "makes sense" is really "seen it before" or "nothing looks out of place", it brings back exactly the typicality bias the scan is meant to escape.

## The hypothesis

> **H.** A decision model's judgments are sensitive to whether a described system *closes* into a self-sustaining whole, including when the break can only be found by integrating across the whole description (no single sentence or entity shows it), and when familiarity is removed.

The human analogue is the "structural click" of intuitive coherence: people can tell that something hangs together before they can say why (see Related work). The claim tested here is behavioral: *can the model detect a closure break that has no local signature?* A pass doesn't show that the model has intuitions in any deep sense. It shows the property a filter needs.

H has two tiers, and the design keeps them apart:

- **Local sensitivity:** the model notices when some entity has no inflow or no outflow. A checklist can do this ("does every name appear on both sides of some relation?"). It's a positive control, not evidence for H.
- **Global sensitivity:** the model notices when every entity looks fine locally but the flows don't close. Only this tier supports H.

### Nulls we're trying to reject

The model's score tracks only:
- **familiarity:** real-world systems it has seen;
- **local cues:** an entity with nothing feeding it, or nothing consuming it;
- **nothing structural at all:** wording, length or noise.

## Related work

Nobody seems to have run this exact experiment: testing whether a single-pass probability evaluator detects closure in self-sustaining loops, as a filter for novel ideas. Several lines of work cover its pieces, and some of them predict what Jev will do.

**Intuitive coherence in humans: the "structural click".** Bowers, Regehr, Balthazard & Parker (1990), *Intuition in the context of discovery*, showed people pairs of word triads. In one triad the words shared a hidden remote associate (e.g., SALT, DEEP, FOAM → SEA); the other was random. People picked the coherent triad above chance, even when they couldn't name the link. Topolinski & Strack (2009), *The analysis of intuition: Processing fluency and affect in judgements of semantic coherence*, traced that judgment to **processing fluency**: coherent triads are processed more easily, and the ease registers as a brief positive feeling. Fluency has other sources too, such as repetition, priming and familiarity, and they can feed the same feeling. **This is the human version of our central confound:** a fast coherence judgment that can't fully separate "this hangs together" from "this is familiar". Our design asks whether a decision model's fast judgment has the same entanglement.

**Separating structure from familiarity with nonce words.**
- PrOntoQA (Saparov & He, 2023) builds parallel ontologies with real and nonce terms ("Every wumpus is an impus"). Models handled individual deduction steps well but struggled with proof planning when several steps were possible.
- Dasgupta et al. (2022; PNAS Nexus 2024) found human-like *content effects*: models judge logical validity more accurately when the conclusion agrees with real-world beliefs, and less accurately with unfamiliar or belief-violating content.
- SynthWorlds (Gu et al., ICLR 2026) builds parallel real and synthetic-entity corpora with identical structure, and reads the performance gap as reliance on memorized knowledge.

Our familiar/nonce factor and canonical set apply the same logic to closure judgments.

**Graph reasoning in natural language.** NLGraph (Wang et al., NeurIPS 2023) tested LLMs on connectivity, cycle and flow problems written in natural language. It found preliminary graph-reasoning ability that is brittle to spurious correlations in the problem setup. That is why our core contrast holds every surface statistic fixed: degree sequence, per-entity mention counts and word counts are identical between control and global items.

**Latent (single-pass) multi-hop limits.** Jev answers without a reasoning trace, so this is a test of latent integration.
- Yang et al. (ACL 2024), *Do Large Language Models Latently Perform Multi-Hop Reasoning?*, found substantial evidence for the first hop of a two-hop query, only moderate evidence for the second, and a scaling trend for the first hop but not the second.
- Biran et al. (EMNLP 2024), *Hopping Too Late*, located the failure mechanistically: the bridge entity is resolved partway through the network, sometimes too late for the second hop to be composed.

These studies cover two hops. Our global breaks need closure traced across a whole loop of 7–15 entities.

### What the literature predicts for Jev

| Finding | Prediction for this experiment |
|---|---|
| Latent composition is reliable for one hop and shaky for two (Yang; Biran) | local breaks (source/sink, 1-hop checks) detected more readily than global ones; the global effect shrinks with system size |
| Content effects (Dasgupta) and the fluency account of coherence (Topolinski & Strack) | real names shift `sustainable`/`coherent` regardless of truth: `fam_beta` > 0 on the canonical set |
| Spurious-correlation brittleness (NLGraph) | any global effect has to survive identical surface statistics; if Jev "detects" global breaks only in cells with some residual cue, that's the explanation |
| Nonce vs real performance gaps (PrOntoQA; SynthWorlds) | the nonce cells are where any structural effect is smallest |

A positive P1 would therefore be the surprising result, and the prior favors "local sensitivity only".

### What this experiment adds

| Dimension | Prior work | Here |
|---|---|---|
| Structure | acyclic deduction chains (PrOntoQA), explicit graph problems (NLGraph), two-hop factual queries (Yang; Biran) | closed, self-sustaining loops where every part depends on the whole |
| Judge | chain-of-thought generation, or internal probing of 2-hop recall | a single-pass decision model's calibrated probabilities, at a cost that makes it usable as a mass filter |
| Controls | real vs nonce words | minimal pairs with identical degree sequences and mention counts (control vs global), local-break positive controls, a checklist baseline, and a canonical real-world set |

## Operationalizing "complete"

Each stimulus is a closed ecosystem, one sentence per flow ("Glims hunt vorrows"; "Fungi return nitrogen to the soil"), under a closure statement: *"Sunlight and rain are plentiful, but no living things or nutrients enter or leave it; every one of them is named below."*

**Semantics: conservation.** Matter is never created or destroyed; it only moves along the described flows. Over time, matter drains out of any part of the system it can't flow back to.

- An entity persists ⇔ it lies in a closed (terminal) strongly connected component.
- The system is complete ⇔ every entity persists, i.e. everything that flows out of anything eventually comes back around.
- This is ecologically standard (nutrient cycling), and it is **not decidable locally**: an entity can have both a supplier and a consumer and still be drained.

Ground truth is computed from the graph. Nothing is hand-labeled.

### Minimal pairs

Every sentence in every variant is a flow; there are no filler sentences. Variants differ from intact only in the one or two sentences they change, with the same names, wording and sentence order.

| Variant | Construction | Truth | Local cue? | Role |
|---|---|---|---|---|
| intact | the base graph | complete | — | reference |
| control | swap the endpoints of two same-type flows; still closes | complete | none | matched reference for global |
| **global** | swap the endpoints of two same-type flows; loop opens | **broken** | **none: every entity keeps exactly the same in/out links and mention count** | **the test of H** |
| source | re-target one flow so an entity loses its only inflow | broken | yes | local positive control |
| sink | re-source one flow so an entity loses its only outflow | broken | yes | local positive control |

**control vs global is the core contrast.** Both are one swap away from intact, and they have identical degree sequences and word statistics. Only the topology differs, so nothing local can tell them apart.

Example (nonce names, eco wording), where the global variant changes only which nutrient two decomposers return:

> intact: "…Drorrs return **dorrick** to the soil… Fleskiths release **drullow** as they feed…"
> global: "…Drorrs return **drullow** to the soil… Fleskiths release **dorrick** as they feed…"

After the swap, five entities, including the nutrient dorrick, are in a loop that drains into the rest of the system and never gets matter back.

### Two item sets

| Set | Bases | Purpose |
|---|---|---|
| random | 60 procedurally generated systems: 12 at each of 7, 9, 11, 13 and 15 entities, density fixed at 4/3 flows per entity (rounded: 9–20 flows) | main test; size dose-response |
| canonical | 8 recognizable food webs (meadow, pond, forest, tundra, marsh, savanna, prairie, desert) with real species, 2 draws each, built with the same templates and code path | gives the familiarity manipulation teeth |

Each canonical web has **two nutrient cycles** (nitrogen and phosphorus). That isn't decoration. With a single nutrient, every cycle passes through it, so the loop can only break locally. A non-local break needs two cycles that can come apart, which is also true of real ecosystems. The canonical topologies follow one fixed two-loop recipe; their *names* are canonical, but their *topology* isn't drawn from textbooks.

### Rendering factors (fully crossed, identical within a minimal pair)

| Factor | Levels | Purpose |
|---|---|---|
| names | familiar / nonce | removes lexical familiarity; the "Jabberwocky" condition |
| register | eco ("graze", "a sealed valley") / abstract ("X can flow into Y", "a closed system") | does an ecological frame recruit a nutrient-cycle schema? (a Bransford & Johnson analogue) |
| rule | stated (conservation spelled out) / implicit | implicit: the schema has to supply the rule |

**The decisive cell is random × nonce × implicit**, where only structure remains.

Total: 3,040 items.

## What we ask Jev

Each item gets two independent Decisions API calls. Each call is **repeated 3×** and averaged, because Jev is not deterministic: in the harness retest, 23% of scores were bit-identical and the largest difference was 0.08. The correlation between two single samples was r = 0.975.

| Call | Question | Type | Measures |
|---|---|---|---|
| main | `sustainable`: "Using only what is described, can everything named persist indefinitely?" | noul | explicit discrimination |
| main | `fails`: "Which named entity most clearly cannot persist, if any?" (none + all entities, order shuffled per base) | choice | localization |
| main | `familiar`: "Is this a well-known real-world system?" | noul | manipulation check |
| gate | `coherent`: "Does this design hang together?", with the stimulus prefixed "Here is a proposed design for a self-sustaining system." | noul | the vague question a generation filter would actually ask |

The gate call is separate so the survival questions can't prime it. The "design" frame makes a structural failure count as incoherence: a doomed ecosystem can still be a coherent *description*, but a self-sustaining *design* that doesn't sustain itself doesn't hang together. Bundling the main questions was checked and doesn't bias `sustainable` (mean shift −0.003, n = 88).

**Baseline: `checklist`.** No model. It reads the true graph and flags "broken" if any entity has no inflow or no outflow. That is the best purely local strategy: perfect on source/sink, exactly at chance on global.

## Predictions and pass criteria

These are fixed before the run. Confidence intervals are bootstrapped over bases, the unit minimal pairs share. `d` is the mean paired difference in score (complete minus broken; > 0 means the model is sensitive to the break), and `w` is the fraction of pairs ranked correctly (0.5 = blind).

| # | Prediction | Metric | Pass |
|---|---|---|---|
| P0 | **Positive control:** Jev responds to local breaks | `d` source vs intact, sink vs intact | both > 0, CI excludes 0 |
| **P1** | **Core: Jev detects non-local breaks** (where the checklist is at chance by construction) | `d` and `w`, control vs global, random × nonce × implicit | `d` CI excludes 0 and `w` ≥ 0.65 |
| P2 | Not recall | control vs global `d`, canonical: nonce vs real names | nonce ≥ ½ × real-name effect |
| P3 | Knows *where* the break is | `fails` mass on the drained set ÷ chance, global items | lift > 1, CI excludes 1 |
| P4 | Coherence isn't familiarity | `fam_beta`: does `familiar` predict `sustainable` once truth is controlled? (canonical set, where familiarity actually varies) | CI includes 0, or \|β\| < 0.1 |
| P5 | **The vague gate question carries the signal** | P0 and P1 metrics on `coherent` | same criteria |
| P6 | (exploratory) schema activation | control vs global `d`, eco vs abstract, implicit rule | eco > abstract |

**Dose-response (descriptive):** control vs global `d` against size (7–15 entities, density fixed, so size isn't confounded with redundancy). The integration horizon is where the effect vanishes, and it caps how big a "thought" Jev can gate.

### Reading the outcomes

| Outcome | Interpretation | Consequence for an idea-generation filter |
|---|---|---|
| P0 fails | Jev doesn't respond to closure on this task at all | revisit domain and wording before concluding anything |
| P0 passes, P1 fails | local sensitivity only: Jev runs something like a checklist | it can screen for dangling parts, not for whether ideas close up |
| P1 passes, P2 fails | global sensitivity, but only on familiar systems | the gate rewards familiar structure; risky for novelty |
| P1, P2 pass; P5 fails | the capacity is there but only when asked explicitly | the gate must ask about closure explicitly, not "does it make sense" |
| P1, P2, P5 pass | Jev has usable, familiarity-independent structural sensitivity | viable gate; use the integration horizon to size thoughts |

**How the gate would use scores.** Jev's scores are compressed (harness: 0.19–0.64, even intact ≈ 0.42), so no fixed threshold will transfer across prompts. The gate should rank within a batch (e.g. keep the top 10% of 50 candidates), which is exactly the property P1/P5 measure.

## Known risks (please challenge these)

1. **"Sink" localization is counterintuitive.** Under conservation, an entity with no outflow *accumulates* (it persists) while everything upstream drains. If Jev names the sink as the failing entity, it's scored wrong, though a human might agree with Jev. Localization (P3) is therefore scored on **global** items only; sink still counts for P0.
2. **The effect may be tiny.** In the 4-base harness, local contrasts were small but nonzero (`d` ≈ 0.015–0.06) and the global contrast was ≈ 0. Small `d` can still be reliable, which is why the criteria lean on CIs and win rates rather than raw size.
3. **Canonical topology is a recipe, not a textbook web.** It raises familiarity through names and recognizable trophic roles, not through matching a specific memorized diagram.
4. **One domain.** Passing on nutrient cycles doesn't show a general completeness sense. Generated ideas depend more on precondition satisfaction (a procedure using an ingredient never produced). A small procedure-domain pilot would test that; it's not in run 1 unless we add it.
5. **Model drift.** `typesafe/jev-1.13` is pinned; every response records the dated snapshot it was served by, and the full `fails` distribution is logged.

## Run 1 plan

- **Items:** 3,040 (60 random + 8 canonical × 2 draws bases, × 5 variants × 8 renderings).
- **Judges:** Jev (3 samples × 2 calls per item) and the checklist baseline.
- **Cost:** ≈ $0.45 (extrapolated from the harness: 160 items for $0.024).
- **Commands:**
  ```
  uv run python -m dec_exp.generate                 # items/v1.jsonl
  uv run python -m dec_exp.run --run run1           # resumable
  uv run python -m dec_exp.analyze --run run1       # runs/run1/report.md
  ```

## What changed after review (revision 1 → 2)

| Review point | Verdict | Change |
|---|---|---|
| "Lure" was broken under the literal question: the outside name is itself a named, unsupplied entity | **Correct.** Rev-1 harness results for lure vs dangling are uninterpretable and are withdrawn | lure and dangling removed; closed-world semantics have no outsiders |
| Under "at least one supplier" semantics, complete ⇔ every entity has a supplier: a local checklist, not integration | **Correct.** Rev 1 overclaimed non-local integration | switched to conservation semantics; added degree-preserving *global* breaks; local breaks demoted to positive controls; added the checklist baseline |
| Orphan's filler sentence was a pragmatic anomaly | **Correct** | no fillers; every break is a rewire or swap of relational sentences |
| A sealed valley without sunlight violates thermodynamics | Already addressed: rev 1 said "Apart from sunlight and rain" | now stated more plainly: "Sunlight and rain are plentiful" |
| Hand-written familiar set adds a style confound | Agreed | canonical set uses the same templates and code |
| `coherent` would be primed; a doomed system can be coherently described | Agreed | separate call; "proposed design" framing |
| Fixed thresholds are brittle | Agreed | the gate ranks within a batch |
| Check determinism; pair wins are fragile to noise | **Checked: Jev is not deterministic** | 3 samples per call; report paired `d` with CIs alongside win rates |
| Bundled questions may leak | **Checked: no measurable shift** | kept bundled for the main call |
| Size confounded with density | Agreed | density fixed at 4/3; size varies 7–15 entities (global breaks are impossible below 7) |
| Spearman(`sustainable`, `familiar`) passes trivially by range restriction | **Correct** | replaced by `fam_beta` on the canonical set, controlling for truth |
| Add a procedure-domain pilot | Reasonable | deferred (risk 4); decision needed |
