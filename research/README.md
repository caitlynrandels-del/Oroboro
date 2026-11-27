# research/: latest Oroboro modeling (27 November 2026)

**Speculative in-silico modeling only. No clinical, medical, biological, engineering, flight or operational claims.** Every number below is a model output, not a measurement.

| Folder | What it is | Conjunctive status |
|---|---|---|
| [`metastasis-native/`](metastasis-native/) | Native Oroboro metastasis cascade, rebuilt on the NaCl polarity mesh with dream-catcher niches, now running all components as one loop | **Conjunctive** (`integrated=True` default). Pre-integration run kept as history |
| [`magnetic-launch/`](magnetic-launch/) | Magnetic-assist launch case study, ondulatory-string addendum, dream-catcher weave, goal-seek continuation, tilt/torque and geography addendum | Mostly **non-conjunctive (pre-integration)**, marked in each header. The redstone repeater/comparator addendum (27 Nov) **is conjunctive**. Light-sail, kite and light-extraction runs are in progress |
| [`cross-domain/`](cross-domain/) | Comparison of the two domains using only Oroboro components, and the conjunctive-use check | Uses the conjunctive wiring as its baseline |

How the components fit together: [PIPELINE.md](PIPELINE.md).

## Native-systems audit (27 Nov 2026)

| Sim | Verdict | Notes |
|---|---|---|
| `metastasis-native/oro_native.py` | **Native + conjunctive now** | Dictator/Transcriber/Levy were ledgers only. The damper never engaged at baseline, and PrinciplesGate was absent. All are now wired into the monthly loop (see that README) |
| `consciousness-mapping/corrected_multi_cancer_sim.py`, `metastasis_data_informed_sim.py`, `metastasis_extended_sim.py` | **Superseded** (header banner added) | Python `random`, Levy only as a running ledger, no polarity mesh, consensus or reconciliation |
| `consciousness-mapping/nacl_polarity_mesh.py` | Component (unchanged) | 4-node tree, no odd loops. The looped mesh lives in `metastasis-native/oro_mesh.py` |
| `magnetic-launch/scripts/*` (except redstone) | **Non-conjunctive**, kept for history | Geography and tilt/torque call no Oroboro component. The others use components as isolated blocks |
| [oroboro-relay `oroboro-core.js`](https://github.com/caitlynrandels-del/oroboro-relay) | **Fixed** | `Math.random()*0.1` delta replaced with a deterministic delta against the Nexus record. `OroboroPipeline` added, with tests |
| oroboro-relay `metastasis-sim/index.html` | **Superseded** (banner) | Visual sketch only |
| [metastatic-cascade-analysis `metastatic_cascade_model.py`](https://github.com/caitlynrandels-del/metastatic-cascade-analysis) | **Superseded** (banner) | Sponge compartment only, no Oroboro loop |
| [epilepsy-sim](https://github.com/caitlynrandels-del/epilepsy-sim) | **Partially conjunctive, untouched code** | The Nexus → salience/homeostasis gate loop is real. Levy, Transcriber and Genesis are ledgers, and there is no polarity mesh. The integrated rebuild is pending. Preflight passed 50/50 on 27 Nov |

Not published here: PDF/PNG/DOCX binaries (the connected GitHub interface stores text only). Figures are SVG. PDFs stay on the project computer, and their Markdown sources are here. Raw pose landmarks and anything from the personal-use highlight video are excluded.
