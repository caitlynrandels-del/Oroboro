# magnetic-launch: magnetic-assist launch case study and addenda

**Speculative modeling exercise only. Not an engineering design, flight plan, siting recommendation or operational claim.** All residuals and speeds are model outputs from point-mass physics plus Oroboro bookkeeping.

## Documents (Markdown is canonical; PDFs stay on the project computer)
1. `Magnetic_Launch_Goldilocks_CaseStudy.md`: magnetic LSM/LIM intermittent track, inverse-Epcot bowl, LAS passes, seismic dampers, Goldilocks zone
2. `Ondulatory_Strings_Wireframe_Addendum.md`: ondulatory strings on the Avalanche wireframe scaffold
3. `Dreamcatcher_Weave_FollowOn.md`: dream-catcher weave on one detected pose (no video stills; raw landmarks not published)
4. `Magnetic_Launch_GoalSeek_Continuation.md`: goal-seek recycling, rocket materials at drone scale, origami, onboard autonomy, atmospheric tiers, feathers, hollow bones, helix, spinning dual Epcot, non-spinning interior, heat-driven feather regrowth, tilt/torque
5. `Geography_Launch_Sites_Addendum.md`: launch-site geography
6. `Redstone_Repeater_Comparator_Addendum.md`: a repeater and a comparator on the residual gap, plus a no-track pad ascent with Earth rotation as a gated side pulse (**conjunctive**)
7. `Light_Sail_Push_Addendum.md`: a ground-laser light-sail push after the rail, on the recycled exits (**conjunctive**)

HTML versions of each document are alongside (figures load from `figures/`). PDF page views (SVG page images): [Goldilocks](pdf-pages/Magnetic_Launch_Goldilocks_CaseStudy/view.html), [Ondulatory](pdf-pages/Ondulatory_Strings_Wireframe_Addendum/view.html), [Dreamcatcher](pdf-pages/Dreamcatcher_Weave_FollowOn/view.html) (its only raster is the skeleton-only fig05; no video stills), [GoalSeek](pdf-pages/Magnetic_Launch_GoalSeek_Continuation/view.html), [Geography](pdf-pages/Geography_Launch_Sites_Addendum/view.html), [Redstone](pdf-pages/Redstone_Repeater_Comparator_Addendum/view.html), [Light sail](pdf-pages/Light_Sail_Push_Addendum/view.html).

## Correction carried in this update
The earlier **256 m/s** staged residual is **invalid**. It came from a 900 s coast that had not yet reached apogee. Under the Kepler vacuum apogee of the same staged state, the two-burn residual is **~1,148 m/s**, with the perigee still underground. The staged state already overshoots, and adding Earth rotation makes the ellipse larger (1,430–1,558 m/s). Do not compare 256 m/s with any boost.

## Headline results (model outputs)
- Best no-stage evacuated hollow-bone dart: residual 407–431 m/s to a 200 km circular orbit (431 m/s is the best case that also satisfies the climb condition Y(a), at a 5° tilt and an 80 km open mouth). Orbit was not reached.
- Equatorial spin (465.1·cos(lat) m/s) is real but does not close the gap for the fast exits. Speed in the wrong direction stretches the orbit.
- Geography: Baikonur ranks best at ~66 m/s for the 0° 80 km exit, and Las Vegas and Mt Charleston come in at 118–119 m/s. Coastal sites are favored for ocean downrange safety, not Δv. Kourou is best when the target orbit is equatorial. A plane change to equatorial costs 4.82 km/s from LAS and 0.71 km/s from Kourou.
- Hollow bones help mass. Feathers are limited. The spinning dual Epcot isolates the interior, but the outward pull remains. Heat-driven regrowth has a narrow window. The simple closed-loop onboard controller hurt the flights.

## Redstone repeater / comparator results (model outputs)
- **Repeater** (a paid two-burn at apogee and at the 200 km apsis, using the rocket equation on the vehicle's own mass, I_sp 450 s):
  - The filament budget f_p = 0.05 (226 m/s) locks all 14 real sites on the 0° / 80 km exit, but not the 5° darts or the staged stack.
  - The payload fraction f_p = 0.30 (1,574 m/s) locks every due-east site on all four setups. That is a mass-bookkeeping result, and it turns the dart into a staged vehicle.
  - Closing the 407 m/s evac-dart leftover needs f_p ≈ 0.088 (1.11 kg of 12.56 kg).
- **Comparator** (subtracting Earth rotation by gating due-east admission through Oasis/PrinciplesGate):
  - It never beat always-best-azimuth (0 of 14 sites). It beats always-due-east only on the staged config (1,144 vs 1,507 m/s mean).
  - Best azimuth, e.g. 40–65° on the 0° exit, gives 37 m/s at Baikonur and 38 m/s at LAS, versus 66 and 119 m/s due east.
  - AdaptOrDie blocks only the zero-coordinate equator reference.
- **No-track** (rail removed, pad start): no configuration locked. Thick-air drag and heating bind first. Even f_p 0.85 at 450 s leaves 631–756 m/s, with a heating proxy of ~5,200 K. Reserving a 500 m/s repeater made the ascent worse.
- Lock means a residual ≤ 1 m/s and a perigee ≥ 100 km. Nothing locked without a paid repeater on a recycled high-altitude exit. No site is recommended.

## Light-sail push results (model outputs)
- Sweep: 1 MW to 100 GW from one ground site under the tube mouth; sail 10–1,000 m²; 1–100 g/m²; four focus sites (Kourou, Mauna Kea, Chimborazo, Sriharikota); recycled exits; residual gate and smart unfold.
- **0 of 864** gated, best-azimuth, smart-unfold runs locked a 200 km circular orbit. Site-to-site differences were small. Diffraction was not the limit (spot < 1 m with the labeled 3 m / 1.06 μm aperture).
- Binding constraints:
  - **Drag:** a 100 m² sail at 80 km sees ~90 kN vs ~63 N of photon force at 10 GW. Unfold has to wait until ~130 km.
  - **Single-site line of sight:** about 134 s above 5° elevation. Useful light is on the climbing leg only; apogee is out of view.
  - **Heating:** almost every sail that opened ran above the PEEK degrade band (e.g. 2,176 K at 10 GW / 100 m²). This is an equilibrium proxy.
- Best cuts were staged 100 GW cases (Kourou 682 m/s coast → 519 m/s, ~13,000 GJ), with perigee still underground. Opening at the 80 km mouth gives back the tube's work (~7,960 m/s left). An ungated push stretches the orbit (~1,400 m/s); the gate stops that, but it does not close the gap. No site, power or sail is recommended.

## In progress (not pushed yet)
The kite / fishing-line / straw guidance run and the Pixar-referenced fur / fabric ("furn") dynamics run are in progress. Their files (`Guidance_*`, `fig13*`) will be pushed when finished.

## Conjunctive-use audit
| Script | Verdict |
|---|---|
| `run_magnetic_launch_case_study.py` | Components exercised as isolated blocks (Oasis, meshes, sweep, dampers, recombine as separate stages) |
| `run_ondulatory_addendum.py` | NaCl polarity and Laplacian only |
| `run_dreamcatcher_weave.py` | NaCl polarity and accounting recombine only |
| `run_goal_seek_recycle.py` | Oasis-style search plus a compact onboard loop. Genesis, Dictator, Transcriber, PrinciplesGate and the NaCl mesh are not in the integrator |
| `run_tilt_torque.py` | No Oroboro component calls |
| `run_geography_addendum.py` | No Oroboro component calls |
| `run_redstone_repeater_comparator.py` | **CONJUNCTIVE**: Genesis → Nexus register → Oasis admission → PrinciplesGate → NaCl consensus → Dictator → Transcriber → Levy (total weight 968) → damped deterministic recombine, in one loop |
| `run_light_sail_push.py` | **CONJUNCTIVE**: same one loop as redstone (Genesis → Nexus → Oasis → PrinciplesGate → NaCl → Dictator → Transcriber → Levy → damped recombine) |

The first six scripts are non-conjunctive and kept for history. Each script carries its verdict in its header. The conjunctive baseline is [`../metastasis-native`](../metastasis-native) and [`../cross-domain/scripts/run_conjunctive_check.py`](../cross-domain/scripts/run_conjunctive_check.py). A launch rebuild on the [one-loop pipeline](../PIPELINE.md) is pending.

## Figures (SVG)
`figures/fig01_track_length.svg`, `fig02_apogee.svg`, `fig03_sea_level_drag.svg`, `fig05_dreamcatcher_weave.svg`, `fig06_goal_seek_pareto.svg`, `fig07_heat_regrowth_bands.svg`, `fig08_nonspin_interior.svg`, `fig09_tilt_torque.svg`, `fig10_geography.svg`, `fig11_redstone_repeater_comparator.svg`, `fig12_light_sail_push.svg` (PNG pixels wrapped in SVG)

## Outputs and reproducibility
`outputs/` holds the JSON/TXT results. Now published: `heat_path_series.json`, `redstone_repeater_comparator.json` and `light_sail_push.json`. Not published: `dreamcatcher_weave.json` and pose landmarks (derived from a personal-use clip), and `work/` frames. Scripts expect the Oasis bridge from the sky-ari-ai build (`/workspace/oasis-build/...`) on the project computer. The NaCl mesh path points to `../../consciousness-mapping` in this repo.
