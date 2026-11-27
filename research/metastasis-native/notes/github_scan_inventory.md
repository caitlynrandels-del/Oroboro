# GitHub rescan inventory — caitlynrandels-del (public)

Scan date: 2026-11-27 (America/Los_Angeles). Fresh shallow clones in `/tmp/gscan2`.
30 public repositories. A prior workspace inventory (27 repos, Nov 24 snapshots) was stale:
new or updated since that clone include `metastatic-cascade-analysis`, `epilepsy-sim`, `caitlynrandels-del`, and fresh pushes to `Oroboro` and `oroboro-relay`.

The file `sky-ari-ai/Oroboro AI Companion` was not opened or copied. It is known to contain an exposed Gemini API key; that key was not used.

## Repositories

| Repo | HEAD (short) | Notes |
|------|--------------|-------|
| `AegisMesh` | `6e0647e` | Revise README with project details and instructions |
| `BROADWAY-PROJECTION-MASTER` | `e307ed1` | Create LICENSE |
| `DnD_Widget_ChatGPT` | `6e2f112` | Delete README.md |
| `Full-Interactive-React-App-Firefly-Edition-` | `54e2db1` | Create UpdateReactAPP |
| `Meta-Thesis` | `987f699` | Update Proof |
| `O.W.L.S` | `d7cd436` | Update .html |
| `ORB` | `3b67d45` | track_vscode_tasks_for_shared_orb_workflows |
| `OpenSourceDATASim` | `ea3595d` | Update README.md |
| `Oroboro` | `ea49814` | Add epilepsy adaptation and psilocin on-off gate cross-links. Speculative modeli |
| `Oroboro-Widgets-KISS-Style-...` | `ba7950f` | Create Index.html |
| `Oroboro_Auto` | `5a69991` | Update README.md |
| `Orroboro-Wildfire-Sim-3D-Spatial-` | `7a2dd07` | Update README.md |
| `Paradox-Engine-via-Oroboro` | `174eb5e` | Create Paradox Engine CellCELL |
| `Simulation-Platform-ORO-` | `5b66a73` | Update README.md |
| `SimulationEngine---Template---Stateful-Particle-Engine` | `e4b3452` | Create Gene Expression Particle Engine |
| `State-Engine-Interface` | `8ab4266` | Create Open Native App |
| `The-Live-Rig-Power-Play` | `11cb7c0` | Add files via upload |
| `Track-Generator` | `7fdb50f` | Update README.md |
| `VisionRxGuesstimate` | `174483f` | Add complete VisionRxGuesstimate visionOS prototype |
| `Wattson-Widget` | `d4309fc` | Rename Index.html to index.html |
| `caitlynrandels-del` | `246f418` | Optimize profile README for SEO: Caitlyn Randels / Caitlyn Connor Randels Orobor |
| `colorado-water-rights-assistant` | `1062685` | Add index.html for the research assistant site |
| `dnd_ar_widget` | `a82e407` | Update Hedwig.html |
| `epilepsy-sim` | `fe692ca` | Add final paper page and update README links for the page-image view and SVG cha |
| `metastatic-cascade-analysis` | `079b920` | Clarify that PDF/Word paper binaries are not in the tree yet. Speculative modeli |
| `oroboro-launcher` | `786adae` | Add Oroboro launcher script and README |
| `oroboro-os` | `7595314` | Add toggleable Epcot ball (Spaceship Earth) behind the net as polygon demonstrat |
| `oroboro-relay` | `61d89c9` | Update metastatic cascade reference to refined title |
| `sky-ari-ai` | `eb5d37a` | Add clickable Oasis-inside-Oroboro-OS page |
| `wii` | `132e824` | Update index.html |

## Component implementations

Where the named Oroboro pieces actually appear as code or a working note, not just a mention in a README.

| Component | Canonical implementation | Also present in |
|-----------|--------------------------|-----------------|
| Genesis / IonicOrigin | `Oroboro/consciousness-mapping/nacl_polarity_mesh.py`; `oroboro-relay/oroboro-core.js` (`OroboroGenesis`); `oroboro-os/oroboro` | |
| Nexus registry | `oroboro-relay/oroboro-core.js` (`OroboroNexus`); `oroboro-os/oroboro`; epilepsy-sim `epi_core.py`; workspace `oro_cascade.py` | |
| Transcriber | `oroboro-relay/oroboro-core.js`; `oroboro-os/oroboro` | |
| Dictator | `oroboro-relay/oroboro-core.js` (`OroboroDictator`). Not in `oroboro-os/oroboro` header. | |
| Levy ledger | `oroboro-relay/oroboro-core.js`; `nacl_polarity_mesh.py` (`apply_levy`); metastasis sims use event weights | |
| NaCl polarity mesh | `Oroboro/consciousness-mapping/nacl_polarity_mesh.py` (identical copy in `oroboro-relay/`). 4 nodes, 3 edges — a tree. Locks opposite-charge edges. No odd-cycle / frustration test. | |
| Mesh consensus | Polarity: `Mesh.consensus()` returns locked edges. Cascade sims: a *different* meaning — event ledger, heat-trace and census must agree (`oro_cascade.py`, `epi_core.py`). | |
| Delta reconciliation | Intended: recombine independent parts so the observable matches the whole. In `oroboro-core.js` the delta is `Math.random() * 0.1` (stub). In metastasis HTML, reconcile is a log line. In `oro_cascade.py` / `epi_core.py`, whole-vs-parts is an accounting check, not in-step feedback. | |
| Homeostasis | `sky-ari-ai` MetaToolsAndHomeostasis*.cs; `oro_cascade.py` rest_load / threshold bump; epilepsy-sim | |
| Sponge limits | `Oroboro/consciousness-mapping/Sponge_Absorption_Mechanic.md`; `epilepsy-sim/code/sponge.py`; `metastatic-cascade-analysis/metastatic_cascade_model.py` | |
| Oasis commit/buffer/recycle | Sky / Oasis salience gate in `oro_cascade.py` (`_gate`, threshold 0.65, recycle below half). OASIS engine in `sky-ari-ai` (not the metastasis sims). | |
| Relational simulation / state reduction | Framework summary; `OroboroRelationalSim` in `oroboro-core.js`; part decomposition in `oro_cascade.py` and `epi_core.py`. | |
| Odd-loop frustration / dream-catcher weave | NOT implemented in any public repo. The only GitHub hit on 'frustration' is an Oasis user-friction reroute in `OroboroCorePrinciplesGate_REAL.cs` (psychological gate, not a mesh). The odd-loop result lives in the launch-chat workspace studies, not GitHub. | |

## Metastasis-related materials on GitHub

- `Oroboro/consciousness-mapping/`: Heat-Trace case study, framework summary, `nacl_polarity_mesh.py`, `metastasis_extended_sim.py`, `metastasis_data_informed_sim.py`, `corrected_multi_cancer_sim.py`.
- `oroboro-relay/metastasis-sim/index.html`: interactive heat-trace sketch.
- `metastatic-cascade-analysis/`: 1.21-million-run study writeups + `metastatic_cascade_model.py` (sponge compartment; no polarity mesh).
- Workspace (not a GitHub repo): `/workspace/oroboro-prevention-sim/oro_cascade.py` — the calibrated 454-setting cascade used as the original baseline.

