Oroboro Structures for Consciousness Mapping: Relational Simulation of Cancer Metastasis
State Reduction, Levy-Weighted Events, and Data-Informed Modeling of Dormancy and Colonization

Caitlyn Connor Randels
Independent Researcher
caitlynrandels@gmail.com
November 2026

Abstract
Metastasis remains the dominant cause of cancer mortality. Disseminated tumor cells (DTCs) frequently enter prolonged dormancy, survive in distant organs through non-genetic mechanisms, and only rarely progress to overt colonization. This paper documents the application of the Oroboro relational simulation framework—state reduction of complex systems into independent parts with delta reconciliation—to model these processes. Building on an existing heat-trace case study in the Oroboro repository, we developed and executed two Python simulations in a sandbox environment: an initial model addressing open questions on dormancy entry/exit, non-genetic factors, and colonization success, followed by a data-informed version incorporating publicly available clinical and experimental constraints (DTC prevalence of approximately 27–40% in early breast cancer bone marrow, extreme metastatic inefficiency from peritoneovenous shunt studies, organ-specific permissiveness, and multi-year dormancy half-lives). Results show high clearance of circulating cells, rare successful colonization consistent with literature, and maintenance of global observational coherence via reconciliation. The work is speculative modeling only and makes no clinical claims.

1. Introduction
The largest unsolved problem in cancer research is metastasis: why and how cancer cells leave a primary tumor, survive elsewhere (often remaining dormant for years), and then awaken to form lethal secondary tumors. Metastasis accounts for the large majority of cancer deaths. Primary tumors are increasingly manageable; disseminated cells that seed distant sites are not.

Key open questions include: (1) how disseminated cancer cells enter and exit dormancy; (2) what non-genetic (epigenetic, environmental, immune) factors allow survival and later growth in new organs; and (3) why some cells successfully colonize while others do not, and how the distant microenvironment enables or blocks that process.

The Oroboro framework decomposes complex systems into independent parts, processes them separately, and recombines outcomes via delta reconciliation so that the final observable result matches whole-system processing. Core components include OroboroNexus (registration, archiving, telemetry), OroboroLevy (weight/toll accumulation), state reduction, and magnetic-style force event analogies. A prior case study in the repository (consciousness-mapping/Metastasis_HeatTrace_CaseStudy.md) mapped metastasis onto these mechanisms as relational heat-trace migration.

2. Methods
2.1 Framework Application
Independent cellular units are treated as reduced-state parts. Detach and attach events are modeled as discrete high-Levy-weight “magnetic pulses” that alter relational coupling. Dormancy is a local state variable that can persist independently. Non-genetic factors (epigenetic plasticity, immune evasion, microenvironment fit) modulate survival and colonization probability. Delta reconciliation restores observational coherence of the heat-trace and levy ledger.

2.2 Initial Extended Simulation
A Python implementation (metastasis_extended_sim.py) was created and executed. Forty cells with random energy, epigenetic state, immune evasion, and microenvironment fit were simulated for 200 steps. Detach pulses could lead to immune elimination or dormancy entry. Colonization success depended on fit thresholds. Spontaneous dormancy exit attempts were plasticity-dependent. Reconciliation occurred periodically.

2.3 Data-Informed Simulation
Public literature was surveyed and parameters embedded: DTC prevalence in early breast cancer bone marrow (~27–40%), low progression fraction among DTC-positive patients, extreme metastatic inefficiency (peritoneovenous shunt studies of Tarin et al. 1984 showing that continuous infusion of large numbers of viable cells produced few or no clinically significant metastases), organ permissiveness (bone > liver > lung > brain), and dormancy persistence on the order of years to decades. An 800-cell, 120-month simulation was run with high clearance rates and rare colonization thresholds.

3. Results
3.1 Initial Simulation Outcomes
After 200 steps: 17 cells remaining, 8 detached, 3 in high dormancy, total Levy weight 187 across 59 events. Dormancy entry was tightly coupled to detach events and immune pressure. Colonization was probabilistic and non-genetic.

3.2 Data-Informed Outcomes
Over 120 months: high clearance of circulating cells. One overt metastasis formed (bone colonization at month 36). Final reconciled state: 790 cells remaining, 1 high-dormancy detached cell, 1 overt metastasis, Levy weight 67. Outcomes align with literature descriptions of metastatic inefficiency and rare progression from DTCs.

4. Discussion
The simulations demonstrate that the Oroboro architecture can represent independent cellular states, discrete relational events with measurable Levy weight, and recombination that preserves whole-system observational consistency. Non-genetic parameters produce heterogeneous outcomes from genetically similar clones, consistent with the open questions. The data-informed version embeds quantitative constraints from the literature so that clearance rates, dormancy persistence, and rare colonization remain within observed ranges.

Limitations: this is speculative modeling only. No claim is made that the framework predicts, prevents, or treats metastasis. Parameters are simplified abstractions of complex biology. Secondary (metastasis-to-metastasis) seeding, detailed immune compartments, and imaging-derived inputs were noted as possible extensions but not fully implemented in the runs reported here.

5. Conclusion
Application of state reduction and relational simulation to metastasis yields a coherent modeling approach for dormancy entry/exit, non-genetic survival factors, and microenvironment-filtered colonization. Public data constraints keep outcomes consistent with known metastatic inefficiency and long latency. The work extends existing Oroboro materials (case study and interactive heat-trace prototype) with executable simulations. Further development could include organ-specific modules, secondary seeding, or integration with real imaging streams via the Dictator/Transcriber components.

Selected References
- Tarin D, Price JE, Kettlewell MG, et al. Mechanisms of human tumor metastasis studied in patients with peritoneovenous shunts. Cancer Res. 1984;44(8):3584–3592.
- Pooled analyses of DTC detection in early breast cancer bone marrow (multiple large cohorts, ~27–40% prevalence; independent prognostic value).
- Blasco MT, et al. Ecology and evolution of dormant metastasis. Trends Cancer. 2022.
- Oroboro repository materials: consciousness-mapping/Metastasis_HeatTrace_CaseStudy.md and oroboro-relay/metastasis-sim/index.html (November 2026).

Status: Speculative modeling exercise. Not a medical treatment, protocol, diagnostic tool, or claim of clinical efficacy. Prepared as part of Oroboro Structures for Consciousness Mapping materials.
