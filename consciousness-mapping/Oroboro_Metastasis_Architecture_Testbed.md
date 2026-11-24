Oroboro Relational Simulation as an Architecture Testbed: Metastasis Case Studies
State Reduction, Levy-Weighted Events, and Delta Reconciliation Applied to Dissemination and Colonization

Caitlyn Connor Randels · Independent Researcher · November 2026

Abstract
This paper presents the Oroboro framework’s state-reduction and relational-simulation machinery as an architecture testbed. Metastasis is used as a multi-step process to exercise independent reduced-state parts, discrete Levy-weighted events, and delta reconciliation. Corrected multi-cancer runs (prostate, ER+ breast, lung, melanoma, colorectal) with distinct seeds and organ-weighted permissiveness produce high clearance, residual dormancy, and rare preferred-organ colonization. The work is speculative modeling with no clinical claims.

1. Purpose and Framing
The simulations reverse the usual order of cancer modeling. Metastasis supplies a complex multi-step process against which Oroboro’s mechanisms—state reduction into independent parts, Levy event weighting, and reconciliation that restores observational consistency—can be exercised. Cancer is the subject being simulated, not the goal being investigated.

2. What Sets the Approach Apart
The difference is not the biological outcomes (high clearance, dormancy, organ tropism are established). It is the purpose and construction: an architecture testbed for Oroboro rather than a domain-specific oncology study. Framing pairs the process with Oroboro components and an Intamin-style magnetic-pulse analogy. Detail is heuristic rather than calibrated prediction. The paper states it is speculative modeling only.

3. Corrected Simulation Results
Each cancer type used its own random seed and literature-informed organ permissiveness. Standardized Levy weights: clearance +1, detach +7, failed colonization +2, successful colonization +14.

| Cancer       | Preferred | Overt | Preferred mets | Dormant | Levy |
|--------------|-----------|-------|----------------|---------|------|
| Prostate     | bone      | 1     | 1              | 0       | 36   |
| ER+ Breast   | bone      | 1     | 1              | 2       | 71   |
| Lung         | lung      | 0     | 0              | 2       | 30   |
| Melanoma     | lung      | 0     | 0              | 2       | 39   |
| Colorectal   | liver     | 1     | 1              | 2       | 70   |

All runs show predominant clearance. Colonization, when it occurred, was in the preferred organ (prostate and ER+ breast → bone; colorectal → liver). Residual high-dormancy cells remained in four of the five runs. These are the qualitative patterns expected from the literature; they confirm that independent cellular states, Levy-weighted events, and reconciliation can host them.

4. How the Exercise Ties into the Broader Research
The Oroboro program develops methods for decomposing complex systems so independent parts can be processed and recombined to match whole-system observables. Metastasis provides long-lived independent units, discrete high-weight transitions, and the need for global observational consistency. The corrected runs supply a worked example that the same machinery can handle a multi-step biological cascade without rewriting the core components.

5. Conclusion
The corrected multi-cancer runs function as an architecture testbed. They demonstrate state reduction, standardized Levy weighting, and reconciliation while reproducing the known qualitative patterns of metastatic inefficiency and organ filtering. The contribution is the demonstration that Oroboro’s relational machinery can host them. The work remains speculative modeling with no clinical claims.

Speculative modeling exercise only. Not a medical treatment, protocol, diagnostic tool, or claim of clinical efficacy.
