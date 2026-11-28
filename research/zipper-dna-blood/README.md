# research/zipper-dna-blood/: zipper, DNA/mRNA and RBC/WBC toggles (t96u, 27 Nov 2026)

**Speculative in-silico modeling only. These are structural analogies mapped onto existing Oroboro components. No clinical, medical, biological, engineering, flight or operational claims. No external biology models.**

Every mechanic is a toggle that is **off by default**, inside existing code paths in [`../metastasis-native/oro_native.py`](../metastasis-native/oro_native.py). With every toggle off, the output is bit-identical to the previous version: `python3 sigcheck.py check` gives 90/90 runs with 0 mismatches.

| Toggle (`native_overrides`) | Mapped onto |
|---|---|
| `zipper` (`zip_tolerance`, `zip_material`, `zip_attach`, `zip_slider`, `zip_size`, `zip_spring`, `zip_tape`) | teeth = NaCl polarity edges; slider = Oasis re-test of skipped teeth; tape/spring = damper α and levy_gain; attachment = seating anchor |
| `dna` (`dna_reanneal`, `dna_proofread`, `dna_proof_thr`, `dna_unzip_ledger`) | pairing = polarity pairs; unzip/reanneal = delta-reconciliation reseat, plus a ledger of OVERT cells that leak to circulation; proofreading = a **new** PrinciplesGate rule |
| `mrna` (`mrna_decay`) | transient Levy EMA vs the persistent Nexus record |
| `rbc` (`rbc_deform`, `rbc_seal`) | deformable carrier in the plumbing/transport channels |
| `wbc` (`wbc_patrol`, `wbc_start_month`, `wbc_recognize`) | dormant patrol through the Oasis gate, clearing cells via recycle (strict) or non-commit (lenient) |

- Addendum: [Markdown](Zipper_DNA_Blood_Addendum.md), [HTML](Zipper_DNA_Blood_Addendum.html), [PDF page view](pdf-pages/Zipper_DNA_Blood_Addendum/view.html)
- Figure: [SVG](figures/zipper_dna_blood_figure.svg)
- Results: [`zipper_dna_blood.json`](zipper_dna_blood.json), plus `data/` (cancer_summaries.csv, launch_zdb.json, frustrated_vs_pool.json, slider_followup.json, run_cancer.log)
- Scripts: `scripts/run_cancer_zdb.py`, `scripts/run_launch_zdb.py`, `scripts/run_slider_followup.py`, `scripts/make_outputs.py`

**Headline results:**
- The 4 failing consensus rows are closed by the DNA unzip ledger. This is a bookkeeping fix only; no cell moves differently.
- PrinciplesGate's original rules still never fire. Holds come only from the newly added proofread rule.
- Calibration toward 21.7% / 10.38 is not closed.
- Frustrated loops vs dormant pool: ρ ≈ −0.8.
- Launch: the straw residual floor stays at ≈595 m/s. A zipper slider (re-burns) keeps repeater locks up to 2° of pointing tolerance.
