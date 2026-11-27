# Epilepsy adaptation and candidate psilocin on-off gate

**Speculative modeling / architecture testbed only. No clinical claims or medical advice.**

The Oroboro metastasis relational testbed (v4 metastatic-cascade model) was adapted to epilepsy and seizure dynamics in a separate public repository:

- **https://github.com/caitlynrandels-del/epilepsy-sim**

Independent neural circuits / foci are treated as reduced states; seizure events as Levy-weighted transitions; seizure freedom and residual risk as clearance / dormancy analogues; and the observable whole-brain result is required to match the recombined parts (delta reconciliation). Cell shading (provisional four-band scale: dark, quiet, active, seizing) is a first-class representation in the reduced states, events, and reconciled whole. A switchable sponge / absorbent intermediary is retained from the metastasis testbed.

## Candidate on-off gate (Balabandian et al. 2025)

Balabandian et al., *Pharmacol Res Perspect.* 2025;13(2):e70079 (open access, CC BY-NC-ND), reported that modest-dose psilocin (3 mg/kg i.p.) was anticonvulsant against PTZ clonic and MES tonic-clonic seizures in mice. The reported mechanism involves 5-HT1A (upregulated) and CB1 (downregulated expression; antagonist AM-251 blocks the effect), plus the kynurenine pathway (1-MT blocks), nitrergic/NO/cGMP, and opioidergic systems. 5-HT2A expression was not significantly changed.

This mouse receptor/pathway modulation is treated here as a **candidate on-off gate** in Oroboro terms, not as evidence for a human therapy:

- sponge `membrane_gate` / permeability (quiet-pool absorption vs reawakening);
- cell-shade band-switch threshold (quiet vs active/seizing);
- Levy-weighted transition threshold;
- residual dormancy vs clearance, analogous to the metastasis sponge on/off results.

An optional `psilocin_gate` (off by default) is proposed in the epilepsy repo (`GATE_NOTE.md`). It has not been used as a clinical claim, and no full production run of the gate was executed beyond an illustrative micro-check.

See also the epilepsy paper PDF in that repository and the metastasis papers in [metastatic-cascade-analysis](https://github.com/caitlynrandels-del/metastatic-cascade-analysis).
