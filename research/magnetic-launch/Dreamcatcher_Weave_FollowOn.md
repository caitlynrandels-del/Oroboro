# Oroboro Structures for Consciousness Mapping
## Follow-on: A Dream-Catcher Weave on a Detected Pose
### Loops, Frustration, and Pulse Spread Versus the Tree-Only Wireframe

**Status:** Speculative modeling exercise only. Not an engineering design, a claim about a player's body, or a statement that a dream-catcher is a launch structure. No operational claims. The official highlight was used for personal analysis only; it is not redistributed, not committed, and not shown in the figure.

Prepared 27 November 2026 as a follow-on to the ondulatory-string addendum. It does the next step named there: replace the placeholder tree with the best available pose, and give the mesh actual loops by laying a dream-catcher weave over it.

### Pose data: what was used

The addendum had used invented placeholder joints from `example_joints.json`, and had noted that a prior MediaPipe probe of the 28 October 2026 Avalanche vs Devils highlights stored only summary counts, not coordinates. This run installed MediaPipe Tasks PoseLandmarker (lite, IMAGE mode, up to eight poses, confidence 0.4) on the box, used the already-stored lite model, and estimated poses on six frames extracted from the personal-use highlight. The broadcast stills are kept only in a work folder and are not part of the published figure.

Results of the six-frame survey:

- Clip 0:05 and 1:30 (wide ice) — 0 poses in this run. The earlier probe had reported a detection on those times; a zero here is a detection result, not a claim that no players are on the ice. MediaPipe Pose is built for a nearby person, not a wide shot of many small figures.
- Clip 4:10 — two poses, 11 of 13 body joints at visibility ≥ 0.5 each.
- Clip 6:40 (a close view of number 91) — one pose, 10 of 13 body joints at visibility ≥ 0.5.
- Clip 8:36 — one pose, **12 of 13** body joints at visibility ≥ 0.5, mean body visibility **0.825**. This is the most complete detection and is the graph used below.
- Clip 9:30 — one pose, 9 of 13 body joints at visibility ≥ 0.5.

**Real pose data were used.** No player pose was invented, and a COCO-17 rest-pose template was not needed. The kinematic tree is built from the clip-8:36 landmarks (published BlazePose / MediaPipe names), plus two midpoints labeled as derived, not detected: mid-hip (Genesis) as the average of the detected hips, and neck as the average of the detected shoulders. The right knee is included at visibility **0.431**, above the keep threshold of 0.30 but below 0.50; that one bone is treated as a weaker observation and is drawn dashed in the figure. All other body joints in this pose are at visibility ≥ 0.50.

The tree has **15 vertices and 14 edges**. It is acyclic (cycle rank 0), of the same kind as the earlier placeholder tree, but its coordinates come from a detected frame rather than from example data.

### The dream-catcher weave

The weave is a hoop plus an inward web, constructed as follows (all of these numbers are declared assumptions, not measurements of a physical object):

- The hoop is a regular 12-gon in the image plane, centered at mid-hip (Genesis). Its radius is 1.15 times the maximum distance of the neck, shoulders, and hips from that center (127.37 px in this frame), so the hoop sits around the torso envelope.
- Four inward rounds follow. Each new vertex starts at the midpoint of a previous-round segment and is scaled in toward the center. The innermost round is left as a hole of radius 0.20 R (25.47 px), not collapsed to a point.
- Each new vertex attaches to both ends of the parent segment, which makes triangular cells — the "knit."
- Neck and both shoulders are tied to the nearest hoop vertex; both hips, which sit near Genesis, are tied to the nearest vertex of the inner hole ring.

The inverse-Epcot bowl is mapped, as an interpretation, as a pressure-balanced circular shell in the same plane, a little outside the hoop; the hoop is the rim, the web hangs inward, and the hole is at Genesis. That is a 2-D reading of the parent-run bowl, not a new 3-D shell computation.

The woven graph is the kinematic tree plus hoop, web, and ties: **75 vertices, 175 edges**, one connected component.

### Observable claims (modeling only)

Each claim is tied to this run. Tree means the 15-joint detected kinematic tree alone. Woven means that tree plus the dream-catcher.

**1. The weave turns a tree into a mesh with 101 independent loops; the tree has none.** Cycle rank, E − V + C, is **0** for the tree and **101** for the woven graph (175 − 75 + 1). The placeholder wireframe in the addendum was also a tree (16 vertices, 15 edges, no cycles). The sock-like knit appears only once the hoop and the midpoint web are added.

**2. Odd cells in the weave frustrate a two-color polarity: the tree can lock completely, the weave cannot.** Both graphs were passed through the existing `nacl_polarity_mesh.py` operators under the same two charge rules as the addendum, then inverted and restabilized. The tree is bipartite (0 two-color conflicts). Interpretation B (alternate charge by BFS level from mid-hip) locked **14 of 14** tree edges; interpretation A (hub-and-leaf) locked **5 of 14**. The woven graph is not bipartite: a BFS two-coloring finds **59** conflicts, which are the triangular cells of the midpoint weave. Under interpretation B, **116 of 175** edges lock and **59** stay open — exactly the conflict count. Under interpretation A only **5 of 175** lock, because most weave vertices have degree greater than 1 and are given the same charge. Invert-and-restabilize preserved the lock count in every case. The unbreakable NaCl observable still holds in the weaker form: opposite ends lock, and the frustrated odd-cycle edges stay open. That frustration is a real property of this weave, not a failure of the invert step.

Levy bookkeeping (0.999 on locked edges, 0.25 on open edges, the two weights already present in the NaCl mesh code) totals **13.986** on the tree under rule B and **130.634** on the weave under rule B. Those figures scale with edge count and lock fraction; they are not physical energies.

**3. Loops raise algebraic connectivity and let a pulse leave the origin and fill the graph more thoroughly.** The Laplacian of each graph has one zero eigenvalue (one component). The Fiedler value (algebraic connectivity) rises from **0.122019** on the tree to **0.176666** on the weave. A unit pulse at mid-hip, stepped by a conservative lazy random walk, behaves as follows:

| Steps k | Tree: mass at origin | Tree: participation | Tree: nodes reached (mass > 10⁻³) | Weave: mass at origin | Weave: participation | Weave: nodes reached |
|--------:|---------------------:|--------------------:|----------------------------------:|----------------------:|---------------------:|---------------------:|
| 1 | 0.5000 | 2.56 | 4 | 0.5000 | 3.17 | 4 |
| 2 | 0.3542 | 3.57 | 9 | 0.3222 | 5.66 | 12 |
| 4 | 0.2374 | 4.79 | 15 (all) | 0.1808 | 10.33 | 30 |
| 8 | 0.1611 | 5.26 | 15 | 0.0923 | 16.49 | 51 |
| 16 | 0.1275 | 5.39 | 15 | 0.0483 | 29.86 | 70 |
| 32 | 0.1159 | 5.65 | 15 | 0.0250 | 76.09 | 75 (all) |

On the tree the pulse has already reached every joint by step 4, then can only slosh among those 15 nodes; mass at Genesis is still 0.116 at step 32. On the weave the same step lets mass run out along the web, participation is much larger, and mass at Genesis has fallen to 0.025 by step 32, with all 75 nodes active. The loops do not just add vertices; they change how an ondulatory pulse leaves the origin.

**4. State reduction and delta reconciliation still recombine to the whole, with loops present.** The woven edge set was split into four independent parts — tree, hoop, web, and ties — and their lengths were summed. The residual against the whole-graph length (6,221.909 px) was **7.28×10⁻¹²**, `matchedWholeSystem: true`. That is a bookkeeping identity, of the same kind as the 1.42×10⁻¹⁴ residual on the placeholder skeleton. It confirms the parts were recombined without loss; it does not validate a physical model of yarn or ice.

Nexus is the joint and vertex register; Genesis remains mid-hip; Levy and mesh consensus are the lock counts above; discrete pulses are the random-walk steps. The figure shows the detected tree, the hoop, the web, the ties, the center hole, and a dashed circular shell for the inverse-Epcot reading. A still from the highlight is not included.

### Limits

Only one pose, from one frame, was woven. Other detections exist and were not built out. The right knee is a weaker landmark. The dream-catcher counts (12-gon, four rounds, hole fraction 0.20, hoop scale 1.15) are assumptions. The shell around the hoop is an interpretive circle, not a 3-D bowl. Laplacian modes have no hertz. Diffusion is a discrete lazy walk, not a wave equation and not the magnetic-rail pulse train. MediaPipe can miss players on wide ice; a missed detection is not a count of people.

### Next possible steps

- Weave the other usable detections (clip 4:10 and 6:40) and report whether the 59-edge frustration and the Fiedler rise recur.
- If a later pose stream is dense enough, let the hoop radius follow the torso from frame to frame and watch lock counts move.
- Drive the woven mesh with the chirped pulse lattice from the magnetic-launch run and report overlap with the frustrated odd cells, still as modeling only.

No claim is made that this is a player's measured anatomy, a textile, or a launch design. It records what changed when a detected tree was given a dream-catcher of closed loops.

---

*Source: MediaPipe pose estimates from the personal-use 28 October 2026 highlight (clip 8:36), the dream-catcher construction above, and the prior magnetic-launch and ondulatory-string notes. Related: Ondulatory_Strings_Wireframe_Addendum.md, Magnetic_Launch_Goldilocks_CaseStudy.md. Figure: outputs/fig05_dreamcatcher_weave.png.*
