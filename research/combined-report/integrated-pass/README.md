# Integrated Oroboro pass (t93u) — one-page brief v2

Speculative modeling only. This is a document-selection pass, not new science.

- `nodes.py` — 84 findings; every value is an exact substring of its source file (`verify_nodes.py`, output in `verify_nodes.out`). `ORIGIN` gives each finding's place in the chat arc.
- `edges.py` — 307 typed edges (support, mirror, same_lever, supersede, contradict).
- `integrated_pass.py` — one loop per iteration over all nodes at once, using unchanged code from `metastasis_native/oro_native.py`, `oro_mesh.py` and oroboro-relay `oroboro-core.js` (@d3d0940) via `relay_driver.js`. Deterministic (rerun gives an identical JSON).
- `integrated_pass_result.json` — per-node gate/weight/features/cluster, clusters and shares, delta reconciliation, mesh, components run vs not applicable, glue mappings, iteration history.
- `render_v2.py` — builds `../Oroboro_OnePage_Engineer_Brief_v2.html/.pdf` from the JSON.
- `github_state.json`, `evidence_plumbing_consensus.txt` — evidence copied from GitHub (read-only) and repo data.

**Repo note:** this folder is a text copy of the pass. Absolute paths in the scripts and JSON (such as `/workspace/oroboro-research/metastasis_native/`) point to the project computer. The repo equivalents are [`research/metastasis-native/`](../../metastasis-native/), [`research/magnetic-launch/`](../../magnetic-launch/), [`research/cross-domain/`](../../cross-domain/) and this report folder. Output: [v2 brief HTML](../Oroboro_OnePage_Engineer_Brief_v2.html) · [v2 page view](../pdf-pages/Oroboro_OnePage_Engineer_Brief_v2/view.html). The PDF binary stays on the project computer, because the connector is text-only.
