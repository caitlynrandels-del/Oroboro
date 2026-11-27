# cross-domain: native cascade vs magnetic launch, using only Oroboro components

**Speculative modeling only. No medical, clinical, biological, engineering or operational claims.**

- `Oroboro_CrossDomain_Comparison.md` / `.html`: the comparison and contrast, component mapping, conjunctive-use audit and next steps
- `scripts/run_conjunctive_check.py`: isolated (pre-integration flags) vs conjunctive (Dictator → Transcriber → Levy → damper, with Oasis admission and PrinciplesGate) rerun of the cascade, plus a cross-ledger pass. This wiring is the **conjunctive baseline**.
- `outputs/`: `conjunctive_check.json`, `conjunctive_vs_isolated_key.csv`, `conjunctive_vs_isolated_corr.csv`

Note: the comparison states that `oroboro-core.js` still used `Math.random()*0.1` for its delta. That was true when it was written. The same day it was replaced in [oroboro-relay](https://github.com/caitlynrandels-del/oroboro-relay) with a deterministic delta and `OroboroPipeline`.

PDF page view (SVG page images): [Oroboro_CrossDomain_Comparison](pdf-pages/Oroboro_CrossDomain_Comparison/view.html).
