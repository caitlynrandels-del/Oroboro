# research/: latest Oroboro modeling (27 November 2026)

**Speculative in-silico modeling only. No clinical, medical, biological, engineering, flight or operational claims.** Every number below is a model output, not a measurement.

| Folder | What it is | Conjunctive status |
|---|---|---|
| [`metastasis-native/`](metastasis-native/) | Native Oroboro metastasis cascade, rebuilt on the NaCl polarity mesh with dream-catcher niches, now running all components as one loop | **Conjunctive** (`integrated=True` default). Pre-integration run kept as history |
| [`magnetic-launch/`](magnetic-launch/) | Magnetic-assist launch case study, ondulatory-string addendum, dream-catcher weave, goal-seek continuation, tilt/torque and geography addendum | Mostly **non-conjunctive (pre-integration)**, marked in each header. The redstone, light-sail, kite/line/straw guidance, and fur/fabric adaptive addenda (27 Nov) **are conjunctive**. Light sail: 0/864 locks. Guidance: 0/46 locks, best leftover an evacuated STRAW at 595 m/s. Fur/fabric: adaptive polygons change how loss is booked, still no locks (Pixar citations from the current library). Light-transport extraction (in `metastasis-native/`): all 45 conditions shrink colonies and the pool. Plumbing / sealed-channel: 0/49 launch locks; evac leftover stays 595 m/s until the channel is substantially leaked; Oasis is load-bearing on the cancer hook (off by default; light-off signature unchanged) |
| [`cross-domain/`](cross-domain/) | Comparison of the two domains using only Oroboro components, and the conjunctive-use check | Uses the conjunctive wiring as its baseline |
| [`combined-report/`](combined-report/) | Combined shareable report covering the full modeling arc (plain language and technical, side by side). [Markdown](combined-report/Oroboro_Studies_Combined_Report.md), [HTML](combined-report/Oroboro_Studies_Combined_Report.html), [PDF page view](combined-report/pdf-pages/view.html) | Narrative of the existing conjunctive and pre-integration results; speculative modeling only |

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

Not published here: PDF/PNG/DOCX binaries (the connected GitHub interface stores text only). Figures are SVG. PDF binaries stay on the project computer. Their Markdown sources are here, and every finished PDF also has an SVG page-image view (`pdf-pages/*/view.html`). Raw pose landmarks and anything from the personal-use highlight video are excluded.
