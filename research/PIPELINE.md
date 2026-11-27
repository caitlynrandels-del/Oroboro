# The Oroboro conjunctive pipeline (one loop, every component feeding the next)

**Speculative in-silico modeling only. No clinical, medical, biological or engineering claims.**

All Oroboro components run as ONE cycle per step. None is called on its own or bolted on afterwards.

```mermaid
flowchart LR
  G[Genesis origin<br/>IonicOrigin / epi origin 0.5] --> SR[State reduction<br/>independent Parts]
  SR --> OA[Oasis salience gate<br/>commit 0.65 / buffer / recycle]
  OA --> PG[PrinciplesGate<br/>InternalDiagnosticFirst · AdaptOrDie<br/>AcceptHumanPain · RerouteFrustration]
  PG --> NA[NaCl polarity mesh seat<br/>dream-catcher niche, odd loops]
  NA --> MC[Mesh consensus<br/>locked vs frustrated edges]
  MC --> DI[Dictator stream<br/>this step's events]
  DI --> TR[Transcriber<br/>chronicle + critical flag]
  TR --> LV[Levy assess<br/>clear 1 · detach 7 · fail 2 · exit 4 · colonize 14]
  LV --> NX[Nexus register + recombine parts<br/>occupancy, Levy pulse, frustration, pressure]
  NX --> DR[Delta reconciliation<br/>damped: occupancy spike + Levy pulse spike]
  DR --> HO[Homeostasis<br/>rest load, comfort H]
  HO --> OA2[Next step's Oasis threshold]
  NX --> NR[Dream-catcher niche self-repair<br/>heat window] --> MC2[Consensus refresh]
  NX --> GC[Genesis closure check<br/>every event traces to a detach]
  OA2 -.next step.-> OA
  MC2 -.next step.-> NA
  GC -.next step.-> G
```

Text form: Genesis → Parts (state reduction) → Oasis salience → PrinciplesGate → NaCl polarity seat / mesh consensus → Dictator stream → Transcriber → Levy (assesses the Transcriber entries) → Nexus register + recombine → damped delta reconciliation (occupancy spike + Levy pulse spike) → homeostasis + next Oasis threshold → niche self-repair → consensus refresh → Genesis closure → next step.

Accounting checks that must hold every run: whole-system run == decomposed run (bit-identical signature), census, Levy (running == pipeline Levy from Transcriber entries), mesh consensus (ledger == heat-trace == census), Genesis closure.

Implementations:
- Python, metastasis cascade: [`metastasis-native/oro_native.py`](metastasis-native/oro_native.py) (`integrated=True`, default).
- JavaScript, relay: [`oroboro-relay/oroboro-core.js`](https://github.com/caitlynrandels-del/oroboro-relay/blob/main/oroboro-core.js) `OroboroPipeline` (Dictator → Transcriber → Levy → damped pressure → deterministic delta vs Nexus → consensus isolation → Genesis mirror).
