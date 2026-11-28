<div class="titlepage" markdown="1">

<p class="kicker">Oroboro Structures for Consciousness Mapping</p>

# Leftovers, Gates and the Last Push { .title }

<p class="subtitle">A combined report on every Oroboro modeling study from this project: the cancer-spread (metastasis) model, light-guided extraction, plumbing, and the magnetic-launch case study through all its variants. Written to be read by specialists and by people with no background, at the same time.</p>

<p class="meta"><strong>Caitlyn Randels</strong><br>Prepared with AI modeling assistance<br>27 November 2026</p>

<div class="status" markdown="1">
**Speculative in-silico modeling only.** Every number in this report is the output of a computer model running on assumed parameters. Nothing here is a medical, clinical, biological or therapeutic claim, and nothing is an engineering design, flight plan, siting recommendation or operational proposal. The cancer model is a model of *simulated occupancy on a graph*. It is not a model of any patient. The launch model is a reduced point-mass model. It is not a vehicle.
</div>

</div>

<div class="toc" markdown="1">

## Contents { .notoc }

1. [Two front summaries](#two-front-summaries)
2. [How to read this report](#how-to-read-this-report)
3. [The Oroboro systems, wired as one loop](#the-oroboro-systems-wired-as-one-loop)
4. [Part A: the cancer-spread model](#part-a-the-cancer-spread-model)
    - A1 The 1.21-million-run sweep · A2 Native-mesh restart · A3 Wiring everything together · A4 Light as transport · A5 Plumbing: a sealed exit
5. [Part B: the magnetic-launch model](#part-b-the-magnetic-launch-model)
    - B1 Goldilocks case study · B2 Ondulatory strings · B3 Dream-catcher weave · B4 Goal-seek continuation (and the 256 → 1,148 m/s correction) · B5 Geography · B6 Redstone repeater, comparator and no-track · B7 Light sail · B8 Kite, line, lane-keeping, magnets, straw · B9 Adaptive fur and fabric · B10 Plumbing on the straw
6. [What the two domains say together](#what-the-two-domains-say-together)
7. [Predictions that failed](#predictions-that-failed)
8. [What this report does not claim](#what-this-report-does-not-claim)
9. [GitHub state](#github-state)
10. [Glossary](#glossary)
11. [Sources, files and references](#sources-files-and-references)

</div>

## Two front summaries

<div class="summary everyone" markdown="1">

### For everyone (no background needed)

We built two "what-if" computer models using Caitlyn's own software parts, called the **Oroboro systems**. One model imagines how cancer cells might spread, hide and grow in the body. The other imagines throwing a small craft toward space along a magnetic track, a bit like a roller-coaster launch. Neither is real medicine or real engineering. They are thought experiments with numbers attached.

**The one big idea both models share:** what is left over at the end is mostly decided *at the door*, when things are first let in or let go, not by fixing them later.

- **Cancer model.** The only things that shrank *both* the grown tumours (colonies) and the hidden "sleeping" cells (the dormant pool) were changes at the door: making the gate pickier about which cells may settle, making organs less welcoming, or opening a *guarded* exit that guides cells out. A light-guided exit, with the gate still deciding who may use it, shrank both in all 45 settings tried. Fixes applied after cells had settled cleared colonies but left sleeping cells behind.
- **Launch model.** The best track runs left the craft a few hundred metres per second short of orbit. Many add-ons were tried: a smart gate on Earth's spin, a laser-pushed light sail, a kite, a fishing line, car-style lane-keeping, magnets pushing on Earth's magnetic field, a tall vacuum "straw", self-adjusting fur-and-fabric surfaces and plumbing-style pressure pushes. **None of them closed the gap.** The one thing that did was a **small final rocket burn at the very end**, paid for with the craft's own fuel (the "redstone repeater"). Spending just 5% of the craft's mass on it closed the gap from all 14 real launch sites on the flattest exit.

We also checked something Caitlyn asked for: do all the Oroboro parts really work *together* as one loop, rather than as separate add-ons? Several early runs did not. Once everything was wired together, the main findings held. Several of our own predictions turned out wrong, and those are listed honestly in their own section.

</div>

<div class="summary specialist" markdown="1">

### For specialists

Two speculative in-silico studies share one component pipeline: Genesis → state reduction → Oasis salience gate → PrinciplesGate → NaCl polarity-mesh consensus → Dictator → Transcriber → Levy → Nexus → damped delta reconciliation → homeostasis and next-step Oasis threshold.

**Metastasis cascade (agent-based, monthly, 120 months, 5 organotropism configurations).** A reanalysis of 1.21 M stored runs reproduced all 484 condition estimates exactly. Baseline: 21.7% (95% CI 20.2–23.4%) of runs colonize, and the dormant pool is 10.38 (10.25–10.51). Elimination switch points: establishment threshold x₅₀ 0.799 and x₉₀ 0.854. A from-scratch native polarity-mesh restart (49 nodes, 89 edges, 32 frustrated) reproduced the pool (10.36) and slightly under-reproduced colonies (18.0%). Across 454 settings, the dynamic frustrated-edge count *anti*-correlates with the pool (Spearman −0.819, CI −0.863 to −0.765). Only upstream levers (Oasis threshold, organ permissiveness) shrink both outcomes. Full conjunctive wiring engages the damper and lowers both: `levy_gain` 1.0 gives 9.1% and 6.36, and 0.05 gives 17.5% and 10.09. An Oasis-gated directed-transport exit ("light") reduced both colony rate and pool in 45/45 conditions. Combined upstream at strength 0.5 gave 0.0% and 0.67. Oasis admission is load-bearing: ablating it raises yield from 15% to 77%. A sealed, valved plumbing exit (perfect seal, upstream) gave p(overt) 0.175 → 0.000 and pool 10.215 → 1.270, and leaks return cargo.

**Magnetic-assist launch (2-D point mass, exponential/ISA atmosphere, vacuum two-burn residual to 200 km circular, 7,788.5 m/s).** The best no-stage evacuated-tube exits leave 407 m/s (held pusher) and 431 m/s (5° tilt, 80 km). The earlier 256 m/s staged figure is invalid: it came from an incomplete coast, and the true Kepler two-burn residual is 1,148 m/s. Lock is defined as residual ≤ 1 m/s with perigee above the stated floor. The only configurations that locked were a paid impulsive late two-burn ("repeater", rocket equation, I_sp 450 s). f_p 0.05 locks all 14 real sites on the 0°/80 km exit, and f_p 0.30 locks every due-east setup. Everything else failed to lock: a subtraction-mode comparator (0/14 vs best azimuth), the no-track pad ascent (0/240, drag/heating bound, ~5,200 K proxy), a laser light sail (0/864), kite, fishing line, lane-keeping and smart-magnet guidance, an evacuated straw (0/46 combined), adaptive fur/fabric meshes, and plumbing (0/49).

</div>

## How to read this report

<div class="inshort" markdown="1">
**In short.** Each section opens with a shaded **In short** box like this one: plain words, an everyday comparison, and the main result. The text after the box is the **technical detail**: methods, assumptions and exact numbers from the original write-ups. You can read just the boxes, just the detail, or both. Unfamiliar words are in the [Glossary](#glossary).
</div>

A few conventions apply throughout:

- **"Model output", not "result about the world".** Every number comes from a simulation with labeled assumptions, so it describes the model and nothing outside it.
- **Recycled vs new.** Later studies reuse settled numbers from earlier ones ("recycled") instead of recomputing them. This report says which is which.
- **Lock.** In the launch model, *lock* means reaching a 200 km circular orbit in the model. The leftover two-burn speed must be at most 1 m/s, and the lowest point of the orbit (perigee) must be at least 100 km (redstone note) or 200 km (all later notes).
- **Conjunctive.** Caitlyn asked that all her components run *together* in one loop, each feeding the next, rather than as separate tools bolted on. Each study states whether it was conjunctive.
- **Units.** m/s is metres per second (1 m/s ≈ 2.24 mph). 7,788.5 m/s (about 17,422 mph) is the speed needed for a circular orbit 200 km up in this model.

## The Oroboro systems, wired as one loop

<div class="inshort" markdown="1">
**In short.** Oroboro is a set of software parts from Caitlyn's public GitHub. Think of a restaurant kitchen line. One station takes the order (Genesis), one writes it on the board (Nexus), and a host decides who gets seated (the **Oasis gate**). A manager checks the house rules (PrinciplesGate). The pieces are fitted together like a jigsaw (the **NaCl polarity mesh**), and a scribe narrates what happens (Dictator and Transcriber). An accountant weighs how important each event was (Levy), and a shock absorber (the **damper**) calms sudden rushes before the next round of seating. "Conjunctive" means the whole line runs every round, with each station handing off to the next.
</div>

<div class="flow">
<span>Genesis<small>origin</small></span>→<span>State reduction<small>independent parts</small></span>→<span>Oasis<small>commit ≥ 0.65 / buffer / recycle</small></span>→<span>PrinciplesGate<small>AdaptOrDie etc.</small></span>→<span>NaCl mesh<small>lock vs frustrated</small></span>→<span>Dictator<small>event stream</small></span>→<span>Transcriber<small>chronicle, critical flags</small></span>→<span>Levy<small>event weights</small></span>→<span>Nexus<small>register + recombine</small></span>→<span>Damped delta reconciliation<small>spike metering</small></span>→<span>Homeostasis<small>next Oasis threshold</small></span>↺
</div>
<p class="caption">Figure 1. The conjunctive pipeline (after research/PIPELINE.md in the Oroboro repository). Each step runs inside every model step. In the cancer model, niche self-repair, a consensus refresh and a Genesis closure check also run every month.</p>

| Component | What it does (plain) | Technical role |
|---|---|---|
| Genesis | The starting point every event traces back to | Origin identity. In the cancer model, shedding is a Levy +7 "detach" pulse from Genesis into a circulation ring. Monthly closure check |
| Nexus | The register or whiteboard | Registers state each step. In the conjunctive cancer model, the next month's environment is built from it |
| State reduction | Split a big problem into small independent parts | Parts see only local state plus last step's Nexus summary, then recombine. Whole-system and decomposed runs must be bit-identical |
| Oasis salience gate | The host deciding who is admitted | S = 0.30·novelty + 0.25·tension + 0.25·coherence + 0.20·resonance. Commit at ≥ 0.65, buffer at ≥ 0.325, recycle below |
| PrinciplesGate / AdaptOrDie | House rules | Port of `OroboroCorePrinciplesGate_REAL.cs`. AdaptOrDie blocks a zero or missing coordinate ("confront reality, not null") |
| NaCl polarity mesh | Jigsaw pieces that only click if opposite | Opposite charges *lock*. Edges in odd loops cannot all lock and stay *frustrated*. Invert-and-restabilize preserves the lock set |
| Dictator → Transcriber | Narrator and scribe | Streams each step's events into a chronicle and flags critical entries |
| Levy | How heavy each event is | Cancer weights: clear 1, detach 7, fail 2, exit 4, colonize 14. These are bookkeeping, not energies |
| Delta reconciliation / damper | Shock absorber | Recombines parts deterministically. The damper turns occupancy and Levy-pulse spikes into a higher next-step Oasis threshold. (The public `oroboro-core.js` used `Math.random()*0.1` here. That stub is now replaced on GitHub.) |
| Homeostasis | Resting load | Rest load 40 and rest bump 0.2 on the Oasis threshold |
| Sponge | An absorbent buffer compartment | Documented in Caitlyn's notes but **not used** in any study here |

**Which runs were conjunctive.** An audit found that the early launch scripts (Goldilocks, strings, dream-catcher, goal-seek) used components as separate blocks, and that the geography and tilt/torque scripts called no Oroboro component. The first native cancer restart had the mesh, Oasis, repair and an occupancy damper inside the step, but Dictator, Transcriber and Levy only kept records, PrinciplesGate was absent, and the damper never engaged. From the redstone run onward, every launch run used one loop: Genesis → Nexus → Oasis → PrinciplesGate → NaCl → Dictator → Transcriber → Levy → damped recombine. The cancer model was rewired as conjunctive by default (`integrated=True`). Section A3 shows what changed.

