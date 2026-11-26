# OROBORO: A Relational Simulation Framework for State Reduction and Observable Equivalence in Complex Systems

**Structures for Consciousness Mapping, Resilient Systems, and Cross-Domain Prototypes**

Research Submission

**Caitlyn Connor Randels**  
Independent Researcher  
caitlynrandels@gmail.com  
GitHub: [caitlynrandels-del](https://github.com/caitlynrandels-del)

November 2026  
Prepared for scientific and technical review

---

## Table of Contents

1. Abstract and Overview of the Combined System
2. Core Theoretical Framework: State Reduction and Relational Simulation
3. Oroboro Core Runtime and Component Architecture
4. Consciousness Mapping Structures
5. Oroboro Relay: Application to Air Traffic Control Resilience
6. Oroboro OS: Deterministic Operating System Sketch
7. ORB: MemoryOS and Persistent Cognitive Context
8. Sky-Ari-AI and AegisMesh: Cognitive Logistics Mesh
9. Metastatic Cascade Analysis: Stochastic Modeling Application
10. Spatial Computing and VisionOS Prototypes
11. Simulation Engines and Domain-Specific Prototypes
12. Supporting Infrastructure and Tooling
13. Synthesis, Open Problems, and Future Directions
14. References and Repository Index

---

## 1. Abstract and Overview of the Combined System

This document presents a comprehensive research submission detailing the Oroboro (also referred to as Ouroboros) framework, an independent research project developing methods for state reduction and relational simulation of complex systems. The central thesis is that a complex system may be decomposed into independent subsystems, processed in isolation, and recombined via mechanisms of delta reconciliation, mesh consensus, and weighted persistent ledgers such that the final observable state is equivalent to that obtained by monolithic whole-system processing.

When the contents of the complete public repository collection (29 repositories under the identifier caitlynrandels-del) are considered as a unified body of work, they constitute the living implementation surface of this framework. The collection encompasses theoretical formulations, reusable architectural primitives (Nexus, Transcriber, Dictator, Levy, and Genesis), domain-specific prototypes spanning air traffic control resilience, stochastic biological modeling, cognitive logistics meshes, spatial immersive computing, and AI memory architectures, together with supporting tooling. The work is motivated in part by the creation of durable, interactive artifacts that embody the researcher's cognitive structures for familial continuity.

The framework has been implemented across multiple technological substrates including zero-dependency client-side runtimes, native visionOS applications, Python-based cognitive loops, and large-scale stochastic simulation ensembles. All prototypes share a common relational ontology: concepts, entities, and states are represented as nodes; relationships and state transitions as weighted synapses or deltas; and historical continuity is maintained through levied, persistent ledgers.

## 2. Core Theoretical Framework: State Reduction and Relational Simulation

### 2.1 Formal Statement

Let S denote a complex system with full state space Σ. A state reduction partitions S into independent components {C₁, C₂, ..., Cₙ} with reduced state spaces σᵢ ⊂ Σ. Independent processing yields local outcomes oᵢ. Relational recombination via a reconciliation operator R produces a global observable O_R such that O_R ≡ O_full, where O_full is the observable obtained by processing the unreduced system. Equivalence is defined with respect to specified observable predicates rather than full state identity.

### 2.2 Key Mechanisms

- **Delta Reconciliation**: Incremental state differences (deltas) are captured, transmitted, and applied such that partial results can be merged without requiring full state retransmission.
- **Mesh Consensus**: Distributed nodes maintain local consistency and reach agreement on shared observables through structured communication.
- **Levy Weighting**: Records and events accumulate measurable weight (toll) that prioritizes critical information and provides an audit trail.
- **Persistent Ledger**: Historical continuity is maintained through append-only chronicles that support query and reconstruction.

These mechanisms enable systems that remain operational under partial failure, support modular analysis of high-dimensional phenomena, and preserve semantic relationships across linguistic, spatial, temporal, and domain-specific representations.

## 3. Oroboro Core Runtime and Component Architecture

The foundational Oroboro repository implements a zero-dependency, client-side runtime that treats language as a semantic coordinate system rather than a localization string. Declaration of the non-standard document type <!DOCTYPE Oroboro> and attributes lang="all" universe="infinite" constitutes a protocol for world instantiation rather than document rendering. The runtime maintains a real-time cognitive node-synapse matrix in which arbitrary concepts (linguistic tokens, memories, sensory data) are injected as living nodes possessing position, velocity, and label attributes.

### Primary Components

| Component | Description |
|-----------|-------------|
| **OroboroNexus** | Unified nexus simultaneously performing runtime registration (in-memory Map), persistent archival, and live telemetry broadcast to subscribers, with associated metrics. |
| **OroboroTranscriber** | Universal history and definition nexus comprising a lexicon (dictionary/thesaurus), structured chronicles, and anonymous logging for ingestion and query of records, definitions, and synonyms. |
| **OroboroDictator** | Real-time stream-to-text transcription layer utilizing speech recognition APIs; finalized transcripts are automatically levied and ingested into the Transcriber. |
| **OroboroLevy** | Universal toll, weight, and history ledger that assesses weight on records, accumulates total weight, and passes levied entries into the Transcriber for prioritization and audit. |
| **OroboroGenesis** | Origin identity ledger with root tag and foundational levy of infinite weight, serving as the origin point from which all subsequent histories mirror. |

The runtime is fully client-side (~170 kb, single file in the primary implementation), employing Canvas 2D physics at 60 fps with proximity, semantic-family, and core synapses. Persistence is achieved via localStorage. The system demonstrates that relational structure (Node A → Synapse → Node B) remains mathematically invariant across languages, domains, and representational modalities.

## 4. Consciousness Mapping Structures

The framework has been extended into Oroboro Structures for Consciousness Mapping. A technical paper remains in draft form and incorporates thorough testing with edge cases, documentation of withdrawn claims, and identification of open problems. The consciousness-mapping directory within the primary repository contains the November 2026 independent research summary, a speculative metastatic heat-trace case study, refined cascade analysis, and a research note on NaCl polarity mesh applied to observational equivalence of aircraft trajectories.

Key themes include independent-parts processing, delta reconciliation guaranteeing observable equivalence, application of the relational ontology to putative structures of consciousness, and explicit treatment of limitations. The work seeks expert feedback and has prepared materials suitable for academic and industry review.

## 5. Oroboro Relay: Application to Air Traffic Control Resilience

Oroboro Relay constitutes a concrete application of the framework to the failure mode that produced a nationwide ground stop on 13 November 2026: overload of legacy routers during a copper-to-fiber upgrade cascading into inconsistent radar and voice data across the national air traffic control network. Rather than requiring global system perfection, each Air Route Traffic Control Center (and neighboring sectors) is treated as an independent component maintaining reduced local state. Deltas are reconciled upon restoration of links, preserving observable traffic-picture equivalence.

Demonstrated capabilities include independent sector processing, mesh isolation of degraded nodes, one-click delta reconciliation, live Dictator transcription of voice communications, Levy weighting of critical messages, and Nexus telemetry. The repository contains a self-contained interactive HTML prototype, updated core classes with aviation-specific methods, and a native SwiftUI conversion targeting visionOS, iOS, and macOS.

## 6. Oroboro OS: Deterministic Operating System Sketch

Oroboro OS is described as a deterministic operating system constructed from the Genesis, Nexus, Transcriber, Dictator, and Levy primitives together with the full GitHub archive. It is characterized as a single-file bootable system that boots from what is already inside, installs programs, opens memory, and performs blender-style recombination.

## 7. ORB: MemoryOS and Persistent Cognitive Context

ORB (Oroboro MemoryOS) implements a layer that enables AI systems to retain ongoing team or session context rather than reinitializing from scratch. The prototype comprises a core mind loop, memory and entity tracking, language interpretation, simple game and input layers (including MIDI), and browser-based experiments. A Python API bridge supports integration with static web interfaces.

## 8. Sky-Ari-AI and AegisMesh: Cognitive Logistics Mesh

Sky (Ari AI) provides a cognitive architecture blueprint emphasizing identity, reasoning design, decision logic, salience models, homeostasis, and moral constraints prior to implementation. AegisMesh (Sky Logistics) realizes a browser-based prototype of a self-healing logistics mesh that replaces reactive supply chains with a biological-nervous-system metaphor. Dynamic nodes and synapses ingest multi-source data, simulate disruptions, and autonomously reroute; live metrics track homeostasis, salience, and decision traces.

## 9. Metastatic Cascade Analysis: Stochastic Modeling Application

An agent-based discrete-time stochastic cascade model (shedding, circulation, arrest, establishment, dormancy, reawakening, colonization; 120 monthly steps) was calibrated to published cohort data for five tumor types. Eight parameters were perturbed singly and combinatorially across 484 conditions × 2,500 runs (1,210,000 total runs). The analysis demonstrates that cumulative-incidence targets can be reproduced while stage-specific rates remain under-identified; establishment-checkpoint thresholds and upstream parameters dominate residual-free probability in the calibrated sparse-shedding regime. Pairwise interactions approximate independence; benefit of perturbation declines with later onset. The work explicitly documents study-design limitations and is presented as a modeling exercise only.

## 10. Spatial Computing and VisionOS Prototypes

Multiple prototypes target Apple Vision Pro / visionOS as the primary platform for standalone spatial and immersive experiences. Notable examples include VisionRxGuesstimate, a complete prototype for rough refractive prescription estimation using only the device display (Landolt C acuity, digital blur matching, astigmatism fan), and early SwiftUI sketches within the Relay repository. Additional spatial work includes 3D wildfire visualization and malleable elements employing Metal compute shaders and adaptive level-of-detail.

## 11. Simulation Engines and Domain-Specific Prototypes

The repository collection contains numerous domain-adapted simulation engines and interactive prototypes that instantiate the relational ontology, including stateful particle engines, SIR/SEIR disease models, real-time 3D wildfire visualization, Paradox Engine particle systems, track generators, Broadway projection tools, and the Colorado Water Rights Research Assistant.

## 12. Supporting Infrastructure and Tooling

Oroboro Launcher is a command-line utility that automates detection and execution of HTML, Python, and Swift/VisionOS sources. Additional repositories provide profile optimization, experimental widgets, and archival experiments.

## 13. Synthesis, Open Problems, and Future Directions

Taken as a whole, the Oroboro collection constitutes a coherent research program investigating whether relational reduction and recombination can preserve observational equivalence across scales and domains. Implemented prototypes provide existence proofs for client-side cognitive matrices, resilient sectorized control, large-scale stochastic biological modeling, cognitive logistics meshes, and immersive spatial interfaces. Open problems include formal proofs of equivalence under specified observable predicates, scalability of mesh consensus, clinical or operational validation of domain applications, and tighter integration of the primitives into a unified runtime. The work remains independent research; claims are limited to modeling and prototype demonstration. Materials are available for expert review and potential collaboration.

## 14. References and Repository Index

Primary repositories: [Oroboro](https://github.com/caitlynrandels-del/Oroboro) (framework and consciousness mapping), [oroboro-relay](https://github.com/caitlynrandels-del/oroboro-relay) (ATC application), [metastatic-cascade-analysis](https://github.com/caitlynrandels-del/metastatic-cascade-analysis), [oroboro-os](https://github.com/caitlynrandels-del/oroboro-os), [ORB](https://github.com/caitlynrandels-del/ORB), [sky-ari-ai](https://github.com/caitlynrandels-del/sky-ari-ai), [AegisMesh](https://github.com/caitlynrandels-del/AegisMesh), [VisionRxGuesstimate](https://github.com/caitlynrandels-del/VisionRxGuesstimate), [oroboro-launcher](https://github.com/caitlynrandels-del/oroboro-launcher), and additional simulation and tooling repositories under github.com/caitlynrandels-del.

Contact: caitlynrandels@gmail.com

---

*End of Research Submission — November 2026*
