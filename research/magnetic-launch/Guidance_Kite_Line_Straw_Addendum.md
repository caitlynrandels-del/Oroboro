# Oroboro Structures for Consciousness Mapping
## Addendum: Kite, Fishing-Line, Lane-Keeping, Smart-Magnet, and STRAW Guidance

**Status:** Speculative modeling exercise only. Not an engineering design, a flight plan, a siting recommendation, or a claim that any of these devices can put a dart into orbit. No operational claims. No vendor, facility, or citation numbers are used. The no-track baseline, light-sail leftovers, redstone best-azimuth / repeater bookkeeping, geography rotation, and hollow-bone dart are recycled; only the guidance plugins are new. The queued Pixar fur/fabric follow-up is not started here.

Prepared 27 November 2026 (America/Denver). Components were run in one loop: Genesis → Nexus register → Oasis admission → PrinciplesGate → NaCl consensus over sensor votes → Dictator stream → Transcriber → Levy assess → damped deterministic recombine. The `Math.random` stub in `oroboro-core.js` was not used.

### The question

The recycled no-track pad ascent (hollow-bone 12.56 kg dart, I_sp = 450 s, T/W = 3, due-east burnout boost at Kourou) never locked in 240 runs. Drag and heating in thick air were binding. This note asks whether five guidance ideas, used in conjunction with that setup — and with the light-sail / repeater / geography findings where they apply — can close the leftover, raise perigee, or at least waste less of the propellant budget.

Lock still means a two-burn residual to 200 km circular of ≤ 1 m/s and a perigee ≥ 200 km. The 7,788 m/s figure is that circular speed; only the leftover is asked of any new device.

The confirmatory open-loop run matches the recycled Kourou f_p = 0.85 point: residual **661 m/s**, max altitude **354 km**, burnout at 95 km and 7,021 m/s, perigee −1,430 km, peak radiation-equilibrium temperature **5,158 K**, drag-loss integral 7,863 m/s.

### 1. Plain kite

A labeled lifting surface (CL = 0.8, CD = 0.25, 50 g/m², areas 2 / 10 / 50 m²) is flown free or on a 2 or 8 km tether with a 50 kN labeled line cap. The sheet is reefed when dynamic pressure exceeds 1,500 Pa or load exceeds 5 kN — otherwise the lift at modest speed already throws the 12 kg dart into an unphysical state.

The kite always reefs in thick air, long before a 2 km tether goes taut, so tethered and free are the same run. A 10 m² kite leaves residual **1,333 m/s** (worse by 672), max altitude 208 km, burnout speed 6,184 m/s. A 50 m² kite is worse still (3,295 m/s, 109 km). Peak lift on the 10 m² sheet already reaches 19 kN before reef. At 40 m/s in sea-level air, drag on that sheet is already several kilonewtons — several times the dart’s 370 N thrust. A surface big enough to loft is a brake long before it can carry the vehicle into thin air. A ground tether, even if it never reefed, cannot follow the vehicle to orbit; that would be an orbital-length line. Binding constraint: kite drag and reefing in thick air.

### 2. Fishing-line

A long thin tensioned line (1–2 mm diameter, 100–1,000 m, cylinder Cd = 1, labeled 0.5 Hz / 2° dither and a small restoring spring) is meant to damp heading waste and sideways drift.

Deployed from the pad, it is a sea anchor. A 500 m × 1 mm line takes max altitude down to **4.3 km**, leftover **7,551 m/s**, line-drag integral 12,000 m/s. Deployed only after 60 km, it is still a brake (leftover **2,791 m/s**, line-drag 6,118 m/s, max altitude 88 km). The oscillation never gets a chance to save angle: the line’s own drag is the wasted energy. Binding constraint: line drag at speed, even in residual air at 60+ km.

### 3. Car-style lane-keeping

Nexus registers a path. Three noisy path-sensor votes are reduced by a median (NaCl invert-and-restabilize on outliers). Corrections are Levy-weighted, q-limited, and admitted only when Oasis salience reaches the 0.65 commit threshold (buffer 0.325), the same numbers as the parent onboard note. PrinciplesGate admits the non-zero open-loop, steep, and shallow paths; a null path is blocked by AdaptOrDie.

The recycled harmful law — slaving flight-path angle to a coarse altitude schedule — is **worse from the pad than it was from an 80 km exit**: the vehicle hits the ground, max altitude **1.1 km**, leftover 6,890 m/s, 767 commits, 10.9 rad of integrated |Δpitch|, and 27 s of thrust-cosine waste.

The gated controller, following the registered open-loop program, does **not** repeat that failure. Across five seeds the leftover is stable at **644 m/s** (17 m/s better than the 661 m/s baseline), burnout 7,030 m/s, max altitude 341 km, perigee still −1,396 km, Teq still 5,143 K. It used 871 commits and 16.5 rad of effort, but cosine waste versus the open-loop program was only 0.01 s: the gate kept the nose on the registered lane rather than wrestling it. That is a real, small improvement, not a lock. Heating and an underground perigee are unchanged. A user-drawn steep path (80 km in 40 km downrange) or a shallower one raises apogee and leftover (1,665 and 1,177 m/s) and runs hundreds of kilometres off the drawn lane: without a physical channel, the T/W = 3 dart cannot stay in a 500 m corridor. Binding constraint: still thick-air drag and heating; the gate avoids the old γ-law crash but cannot buy the missing kilometres per second.

### 4. Smart-magnet vs Earth’s field only

Off-track, the only reaction surface is Earth’s magnetic field, about 25–65 µT at the surface (a labeled dipole, 30 µT at the equator, used here). A magnetorquer produces **torque** τ = m B, not a useful **force** in a nearly uniform field. The dipole gradient is dB/dr = −3B/r ≈ 1.4×10⁻¹¹ T/m. For a labeled moment of 1,000 A·m² on this dart:

- translational force ≈ **1.4×10⁻⁸ N**, acceleration 1.1×10⁻⁹ m/s², Δv in 1,000 s ≈ 10⁻⁶ m/s;
- torque ≈ **0.030 N·m**, enough to slew the dart’s attitude about 10° in 4.5 s.

The force-only run is identical to the open-loop baseline (leftover 661 m/s). Torque can point a body-fixed engine slowly, but it does not add a path force, and a torque-steered copy of the steep lane-keeping run matches the thrust-vector run exactly. Binding constraint: with only Earth’s field to push against, there is no useful translational lane-keeping while the vehicle is building momentum.

### 5. STRAW

The drawn path is now a continuous guided channel whose wall is the magnet reaction surface. That is a built structure, not a free field. Its length is the path length.

The recycled evac tube that delivered the 17,000 mph / 5° / 80 km rail exit was **767.6 km** long. A vertical straw to 80 km is 80 km (0.10× that tube); to 200 km, 200 km (0.26×). The steep user path to 80 km is about 92 km of arc. Reaching 7,788 m/s at T/W = 3 in vacuum, ignoring gravity, already needs **1,031 km** of channel (1.34× the evac tube). Magnetic walls do not remove air.

An *open-air* straw along the steep path still has aero; leftover 1,407 m/s, worse than baseline because of the steep climb. An *evacuated* straw along the same open-loop pitch program as the no-track baseline is the first variant that actually returns some of the drag budget: leftover **595 m/s** (−66 m/s vs 661), burnout 7,275 m/s at 109 km, max altitude 524 km, drag-loss ≈ 0, Teq **1,579 K** if the channel ends at 80 km and **160 K** if it continues to 200 km (the whole burn then stays in vacuum). Perigee is still −1,022 km. Extending the vacuum from 80 to 200 km does not close the leftover, because burnout is already at 109 km: more tube after cutoff only avoids heating on the coast. The binding constraint, once drag is gone, is the **propellant budget plus gravity loss**. f_p = 0.85 at 450 s is 8,372 m/s of ideal Δv, not enough to arrive already circular at 200 km after gravity, which is why a vacuum accel path to circular speed is already longer than the recycled evac tube. The straw is, honestly, a very tall (or very long) track. If it is evacuated and follows a shallow program, it is the evac-tube idea again, and it still does not lock this dart.

At f_p = 0.30, even an evacuated straw peaks at 73 km and leaves ~6,955 m/s — below Karman, as in the recycled no-track 47 km / 1,730 K point.

### Light-sail, repeater, and geography

The best leftovers in this note (gated 644 m/s, evacuated-straw 595 m/s) are the same order as the recycled no-track burnout the light-sail addendum already pushed (661 m/s at Kourou, cut to 514 m/s at 10 GW / 100 m², perigee still underground, Teq 2,780 K). A repeater paid from remaining mass still cannot raise an underground perigee if the burn happens at 80–110 km. Best-azimuth / due-east at Kourou remains the burnout boost; it does not change the guidance ranking. No new lock appears by stacking those recycled layers on these burnouts.

### What binds, variant by variant

| Variant | Residual (f_p=0.85, Kourou) | h_max | Perigee | Momentum vs baseline | Waste / effort | Binding constraint |
|---------|----------------------------:|------:|--------:|---------------------:|----------------|--------------------|
| Open-loop baseline | 661 m/s | 354 km | −1,430 km | — | — | Drag / heating |
| Kite, 10 m², reefed | 1,333 m/s | 208 km | −2,918 km | −838 m/s | Sheet drag before reef | Thick-air kite drag |
| Line 500 m from pad | 7,551 m/s | 4.3 km | underground | −7,010 m/s | Line-drag 12 km/s | Line drag (sea anchor) |
| Line 500 m from 60 km | 2,791 m/s | 88 km | underground | −2,330 m/s | Line-drag 6.1 km/s | Line drag in residual air |
| Harmful γ-law | 6,890 m/s | 1.1 km | impact | −6,340 m/s | 767 commits, 27 s cosine waste | The old closed-loop law, from the pad |
| Gated open-loop lane | **644 m/s** | 341 km | −1,396 km | +9 m/s | 871 commits, 0.01 s cosine waste | Still drag / heating; gate does not hurt |
| Magnet vs Earth field | 661 m/s | 354 km | −1,430 km | ~0 | F ≈ 10⁻⁸ N | No reaction surface but Earth’s field |
| Open-air STRAW, steep | 1,407 m/s | 101 km | underground | −967 m/s | Path too steep | Aero remains; path losses |
| Evac STRAW, open-loop, 80 or 200 km | **595 m/s** | 524 km | −1,022 km | +254 m/s | Drag ≈ 0; Teq 1,579 K / 160 K | Propellant + gravity; it is a tall track |

Zero of 46 guided runs locked, as with the 0/240 no-track baseline. No site or device is recommended.

### Conjunctive loop

Dictator streamed admit / correct / reef / fail events into Transcriber. Levy assessed them (total weight 101). Nexus registered the non-zero paths; PrinciplesGate blocked the null path. A labeled NaCl pass treated a physical reaction surface (straw wall, evac tube) as opposite-charge to leftover Δv, and treated kite/line drag, an un-gated γ slave, and Earth-field-only magnets as same-charge (they widen or do nothing). Invert-and-restabilize is the same rule as in the parent notes. Recombine over the f_p = 0.85 leftovers does not match (mean residual 2,464 m/s, pulled up by the failed kite/line/harmful runs).

### Limits

All of this is a labeled model. Kite coefficients, line diameters, dipole moments, Reef and tension caps, and the 25–65 µT field range are assumptions, not hardware certificates. The magnet model is a uniform dipole-plus-gradient, not a local anomaly map. The STRAW wall is a perfect-containment idealization inside its radius; cost is reported as path length, not money. Lane-keeping noise is a labeled 1-σ vote, not a flown lidar. The two-burn residual is a vacuum metric applied after burnout. A second downrange laser, a rail, or a Pixar fur/fabric layer was not added in this run. No configuration locked a 200 km circular orbit.

---

*Source: recycled no-track baseline from Redstone_Repeater_Comparator_Addendum.md (outputs/redstone_repeater_comparator.json); light-sail leftovers from Light_Sail_Push_Addendum.md (outputs/light_sail_push.json); evac-tube length from outputs/goal_seek_recycle.json. New evaluation: scripts/run_guidance_kite_line_straw.py, outputs/guidance_kite_line_straw.json. Figure: figures/fig13_guidance_kite_line_straw.svg.*
