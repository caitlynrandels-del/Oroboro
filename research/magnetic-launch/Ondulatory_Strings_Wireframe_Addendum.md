# Oroboro Structures for Consciousness Mapping
## Addendum to the Magnetic-Assist Launch Case Study
### Ondulatory Strings and the Avalanche Wireframe Scaffold

**Status:** Speculative modeling exercise only. An interpretive mapping plus a small deterministic computation. Not an engineering design, a materials claim, or a statement that the launch rail is a musical string or a waveguide. No operational claims.

Prepared 27 November 2026 as an addendum to *Magnetic-Assist Launch as Intermittent Relational Events*. It uses only Caitlyn Randels's added remarks, the existing placeholder Avalanche wireframe, and numbers already recorded in the parent launch run.

### The remarks, quoted

Caitlyn wrote:

> Shrink wrap porcelain ninja stars socks 3d printer filament straw/tube. Bubbles. This is an example of ondulatory strings that I know is incredibly pertinent, but I'm not really sure what to do with it right now.

And:

> We also have the wireframe model from the avalanche game analysis that helps.

The first stack is treated here as an ondulatory-string analogy: "ondulatory" is read, in this note, as wave-on-a-string / undulatory. Each item is mapped onto existing Oroboro components. That mapping is an interpretation, labeled as such, not a derivation from the objects themselves. The second remark is taken as a pointer to the existing Avalanche skeletal / wireframe work, which is used as a supporting mesh scaffold, with its documented limit stated plainly.

### Interpretive mapping

The assignments below are an interpretation of the quoted stack, not a measurement of shrink wrap, porcelain, socks, filament, or bubbles.

| Quoted item | Physical analogy (interpretation) | Oroboro / launch-run role (interpretation) |
|-------------|-----------------------------------|--------------------------------------------|
| Shrink wrap | A tight constraint envelope around a form | The bound that keeps reduced parts inside a working domain: the skeletal chunk-grid envelope, or the isolator envelope that meters peaks in the parent run |
| Porcelain | A brittle / rigid limit: a part that holds its shape until it doesn't | Length-conserving "rigid" edges in the wireframe; the place where a locked mesh is not allowed to stretch |
| Ninja stars | Radial, roughly symmetric hubs with several arms | Joints of degree ≥ 3 in the wireframe (here, neck and hip); discrete nodes from which pulses or branches can radiate |
| Socks | A compliant knit mesh: flexible, looped, load-spreading | A mesh layer that can hold crossings and isolated cells; in this placeholder graph the "knit" is only a tree, which is a real limit of the available model (no loops) |
| 3d printer filament | A continuous string, laid down as a thin path | The ondulatory filament itself: a chain of reduced states, or the launch rail as a single string along which discrete pulses are placed |
| Straw / tube | A waveguide: a hollow path that supports standing-wave modes, including closed-open harmonics | The rail or bowl as a tube of length L, compared with textbook string (open–open) and closed–open wavelengths |
| Bubbles | Minimal surfaces / pressure-balanced shells | The inverse-Epcot bowl already used in the parent run (a spherical shell of constant curvature, assumed radius 2,500 m). No new soap-film computation was added here |

Genesis is the origin of the filament (in the wireframe computation, the hip). Nexus registers the joints and bones. Discrete magnetic pulses from the parent run are the driving events along the string. Levy weighting is the existing 0.999 mesh weight when polarity is applied, and the skeletal run's Levy total of 8. Delta reconciliation is the recombine already performed on the placeholder skeleton, and the damper recombine from the parent run. State reduction remains the chunking of pulses, coast gaps, and joints into independent parts.

### The Avalanche wireframe, used honestly

The supporting structure is `/workspace/oroboro-skeletal/`: a cyan wireframe and chunking pipeline built for the Avalanche vs Devils analysis. It must be described as it actually is. `example_joints.json` and `run_report.json` state that the joint positions are invented placeholders. They were not extracted from the 28 October 2026 highlights. Pose estimation on the clip was later reported as incomplete. This addendum therefore uses the wireframe as a **scaffold and visualization layer**, not as a recording of real players.

The placeholder graph, taken from the stored bone list, has **16 joints and 15 bones**. It is a **tree** (connected, no cycles): two radial hubs (neck, degree 4; hip, degree 3), five leaves (head, both wrists, both ankles), and nine degree-2 chain joints. Two example skeletons share that topology. An already-completed skeletal run recombined two frames with residual **1.42×10⁻¹⁴** against whole-system bone length **99.927884** (abstract units, not metres), `matchedWholeSystem: true`. Frame t = 0 had 0 crossing bones and 10 isolated chunks; frame t = 1 had 2 crossing bones and 9 isolated chunks. Those figures are from the stored run, not new video.

As a scaffold for the launch model, the tree is a joint graph on which rail segments or string branches can be hung: hubs as ninja-star nodes, chains as filament, the chunk grid as a shrink-wrap envelope, conserved bone length as a porcelain-style rigid limit. Because the graph is a tree, it is a branching string, not yet a sock-like knit with loops. That is a property of the placeholder, not a finding about skating.

### What was added in this run

A short deterministic script (`scripts/run_ondulatory_addendum.py`) did three cheap things and invented no motor specifications:

1. Applied the existing `nacl_polarity_mesh.py` operators (process, Levy 0.999, consensus, invert, restabilize) to the 15-edge placeholder tree, under two declared interpretation rules for charge.
2. Computed the graph-Laplacian spectrum of that tree (no mass or tension assumed; this is a combinatorial mode count).
3. Compared textbook standing-wave wavelengths on the already-recorded slender-20 kg, 80° rails with the spatial period of the launch-run pulse cycle, T = 0.40 s on + 0.40 s coast = **0.80 s**. The spatial period at a local speed v is Λ = vT. No wave speed, tension, or linear density was assumed, so no frequencies in hertz are claimed.

### Observable claims (modeling only)

**1. Under an ondulatory-filament polarity, the placeholder wireframe locks completely; under a hub-and-leaf polarity, only the five tip bones lock.** Interpretation A (ninja-star hubs and leaves: degree ≥ 3 and degree 2 set to +1, leaves to −1) locked **5 of 15** edges: head–neck and the four distal bones into the wrists and ankles. The ten hub-to-chain and chain-to-chain bones stayed open. Interpretation B (alternate charge along the unique tree path from hip as Genesis origin) locked **15 of 15** edges, because every bone in a tree joins opposite depths. In both rules, invert-and-restabilize preserved the lock count, the same observable as the NaCl and LAS meshes in the parent note: opposite ends lock, open nodes stay open. These counts are for the declared charge rules only.

**2. The wireframe, as a graph, supports 15 non-trivial combinatorial modes and one rigid zero mode.** The Laplacian of the 16-joint tree has exactly one zero eigenvalue and 15 positive ones: 0; 0.085409; 0.198062 (twice); 0.491519; 0.832625; 1.320357; 1.554958 (twice); 1.741822; 2.825785; 3.055061; 3.246980 (twice); 4.362340; 5.285083. Three repeated values are consistent with the left/right symmetry of the placeholder. These are graph modes, not measured vibrations of a body or a rail.

**3. The intermittent pulse lattice on an accelerating rail is chirped, so a uniform standing wave cannot sit in register with the whole train, even when exit-speed spacing is close to one uniform harmonic.** Because the vehicle starts from rest, Λ = v(t)·T grows along the track. On the parent run's slender 20 kg, 3,000 mph, 80° straight climb (reached; L = 185.606 km; 367 pulses in 293.17 s), the mean spatial period is **506.48 m** and the exit-speed period is **1,072.93 m** (chirp ratio 2.118). The number of periods actually laid is 367; only **172.99** exit-speed periods fit in the same length. A uniform string mode (λ_n = 2L/n) whose wavelength equals that exit-speed period sits at n_real = **345.980**, nearest harmonic **346**, detuning **−0.020**. The concave bowl (346 pulses; L = 185.888 km) is not as close to a string integer (n_real = 346.508) but is very close to a closed–open tube harmonic (n_real = **347.008**, detuning **+0.008**). Those near-integers are geometric observations about *exit* spacing only. They do not cancel the chirp: the lattice is denser at the slow start and longer at the exit, so no single uniform mode matches the whole pulse train. The 1,000 and 2,000 mph straight climbs show the same chirp pattern (ratios 1.932 and 2.101). This is a modeling reading of the already-run rails, not a claim that the track "rings."

### Limits

The polarity rules and the item-by-item table are interpretations of a short quoted list. The wireframe joints are placeholders. The Laplacian modes have no assigned hertz. Standing-wave comparisons use only length, pulse period, and recorded speeds; they do not include tension, air in a tube, or damping. The assumed 2,500 m bowl is still only a short pitch-up at the start of a much longer climb. No bubble or knit-loop computation was added, because the available graph has no cycles and no soap-film code was run.

### Next possible steps

- If real pose data are ever ingested, replace the placeholder tree and repeat the lock-count and Laplacian steps on the measured graph, including any loops that would make the "socks" mesh actually a mesh.
- Build a chirped drive along the climbing rail (pulse phase vs uniform mode 346 or tube mode 347) and report overlap as a function of distance, still as modeling only.
- Give the shrink-wrap envelope an explicit capacity, in the sense of the existing sponge / isolator limits, and test when a pulse residual saturates it.

No claim is made that this identifies a material, a vibration, or a launch design. It records one interpretive use of the quoted ondulatory-string stack, and what a small run on the existing placeholder wireframe and the parent-run rails actually returned.

---

*Source: Caitlyn Randels remarks of 27 November 2026, the placeholder wireframe in oroboro-skeletal/, and the magnetic-launch case study outputs. Related: Magnetic_Launch_Goldilocks_CaseStudy.md, NaCl_Polarity_Mesh_Research_Note.md.*
