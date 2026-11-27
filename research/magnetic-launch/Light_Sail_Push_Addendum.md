# Oroboro Structures for Consciousness Mapping
## Addendum: A Light-Sail Push after the Magnetic Track

**Status:** Speculative modeling exercise only. Not an engineering design, a flight plan, a siting recommendation, or a claim that a laser array or a sail can put a dart into orbit. No operational claims. No vendor, facility, or citation numbers are used. Residuals and exits are recycled from the goal-seek, geography, and redstone notes; only the post-exit chassis-and-sail window is new.

Prepared 27 November 2026 (America/Denver). Components were run in one loop: Genesis → Nexus register → Oasis admission → PrinciplesGate → NaCl consensus → Dictator stream → Transcriber → Levy assess → damped deterministic recombine. The `Math.random` stub in `oroboro-core.js` was not used.

### What is being asked of the sail

The 7,788 m/s figure is 200 km circular speed in this file. The evac-tube / rail exit already supplies most of that. The sail is asked only for the recycled two-burn leftover to a 200 km circular orbit, treated as a late-stage directed push in the same role as the redstone repeater. Earth rotation and site geography stay in, under the best-azimuth policy from the redstone note (a subtraction-mode comparator never beat best azimuth). A residual *gate* on the beam is the comparator analogue for the light line: the laser is on only when a trial pulse would lower the two-burn leftover; otherwise the pulse is treated as stretching the ellipse and is cut.

Orbit *lock* in this note means a two-burn residual of ≤ 1 m/s and a perigee ≥ 200 km (stricter than the redstone Karman-100 km floor).

### Recycled setups and the stripped chassis

Unboosted leftovers, recycled, before site rotation or the sail:

| Setup | Residual | Apogee | Perigee | Mass before strip |
|-------|--------:|-------:|--------:|------------------:|
| Evac dart, 5°, 80 km | 406.9 m/s | 373 km | −886 km | 12.56 kg |
| 5° tilt, 17,000 mph, 80 km | 431.2 m/s | 343 km | −974 km | 12.56 kg |
| 0°, 17,000 mph, 80 km | 333.0 m/s | 80 km | −711 km | 12.56 kg |
| Staged (true Kepler; post-stage state at 33.8 km) | 1,148 m/s | 5,436 km | −234 km | 18.84 kg remaining |

The dart is stripped after the rail: the 6.0 kg requested payload (0.30 of the 20 kg request) is jettisoned, leaving a **6.56 kg hollow-bone chassis**. A sail of mass σA is then added. For the staged stack, the same chassis/total ratio (0.522) is applied to the remaining 18.84 kg, giving a **9.84 kg chassis**, then the sail. That is a bookkeeping strip, not a structural certificate.

Best azimuth at the focus sites (Kourou, Mauna Kea, Chimborazo, Sriharikota — near-equator, high-altitude, and/or over-ocean entries from geography.json) already cuts those leftovers, as in the redstone note: about **328 m/s** on both 5° no-stage exits, **41–50 m/s** on the 0° exit (with perigee sitting at 80 km), and **797–815 m/s** on the staged stack (west azimuth 270°, because due east stretches that ellipse). PrinciplesGate admits all four real sites; the zero-coordinate equator reference is not used as a siting admission.

The staged leftover above is a *vacuum* Kepler number from 33.8 km. An integrated coast with the dart body through the remaining air, sail still folded, already drops that Kourou leftover to about **682 m/s** and pulls perigee down. The vacuum figure overstates what survives the climb from 33.8 km; sail comparisons for the staged case are therefore also read against that coast.

### Labeled model assumptions

These are model values, not facilities or materials.

- Laser power: **1 MW, 10 MW, 100 MW, 1 GW, 10 GW, 100 GW**, from one ground site at the geography coordinate (the evac-tube *mouth*, vehicle nearly overhead at 80 km). A laser at a sea-level tube entrance hundreds of km up-track would already be near the horizon at exit and is not the baseline.
- Sail area **10, 100, 1,000 m²**; areal density **1, 10, 100 g/m²**.
- Reflectivity 0.90 (absorbed fraction 0.10, no transmission); emissivity 0.80; sail Cd 2.0; wavelength 1.06 μm; transmitter diameter 3 m; zenith optical depth 0.20.
- Force: \(F_n = (1+\rho)\,P_\text{int}/c\), with \(P_\text{int} = P\,T_\text{atm}\,f_\text{spot}\cos i\). The sail normal is aimed along the bisector of the beam and the prograde direction so the prograde component is raised. Perfect reflection at normal incidence is the familiar \(2P/c\).
- Diffraction: Airy first-minimum radius \(1.22\,\lambda L/D\), uniform-spot intercept \(\min(1, A_\text{sail}/A_\text{spot})\).
- Atmosphere: parent ISA to 86 km; above that, labeled order-of-magnitude thermosphere anchors (100 km 5×10⁻⁷, 120 km 2×10⁻⁸, 150 km 2×10⁻⁹, 200 km 2.5×10⁻¹⁰ kg/m³) with log interpolation. Not a standard-atmosphere certificate.
- Unfold when photon thrust first exceeds sail drag. Immediate unfold at the 80 km mouth is a separate contrast.

### Results: the leftover does not lock

**Zero of 864** gated, best-azimuth, smart-unfold runs locked. Site-to-site differences among the four focus sites were small next to the other constraints. With the labeled 3 m aperture and 1.06 μm wavelength, the diffraction spot stayed under 1 m over the whole window, so the sail intercepted the beam; diffraction is not the binding constraint here.

**Line-of-sight.** From a site under the mouth, elevation starts near 90° and falls to the horizon in about **230 s**; time above 5° is about **134 s** on the 5° evac dart at Kourou. Apogee on those boosted 5° arcs is 640–670 km, still ahead when the site loses the vehicle (altitude then ~230 km). The launch-site window is a *climbing-leg* burn, not an apogee repeater.

**0° / 80 km.** Best azimuth already leaves only 41–50 m/s, but 80 km is *perigee*. The sail never unfolds: at 80 km a 100 m² sail sees on the order of 90 kN of drag, against ~63 N of photon force at 10 GW or ~634 N at 100 GW. The vehicle stays near 80 km through the window (apogee, 180–250 km, is half an orbit away and out of view). Residual drifts 48 → 38 m/s at Kourou from dart-body drag alone; perigee stays ~80 km. A burn at perigee cannot raise perigee to 200 km. No lock.

**5° evac dart and 5° tilt.** Below 1 GW, thrust never beats drag in the window and the sail stays folded; leftover stays ~328 m/s, perigee still hundreds of km underground. At 10 GW, 100 m², 10 g/m², Kourou, the sail opens at ~104 s (near 130 km): 103 s on, 22 s shuttered, 10 GW × 103 s = **1,034 GJ** commanded, ~56 m/s imparted, ~61 m/s of sail drag, residual **328 → 330 m/s**, perigee still about −441 km, peak radiation-equilibrium temperature **2,176 K**. At 100 GW the residual *gate* prevents the open-loop stretch (ungated, the leftover jumped to ~1,400 m/s with apogee at 8,300 km); gated, it is **328 → 342 m/s**, perigee −379 km, 100 GW × 62 s = **6,235 GJ**, Teq **4,696 K**. Drag still eats most of the imparted Δv. The same pattern holds, within a few m/s, at Mauna Kea, Chimborazo, and Sriharikota, and for the 5° tilt.

**Staged.** Against the integrated coast (~682 m/s at Kourou, not the vacuum 798), 10 GW barely moves the leftover (679 m/s). 100 GW, 100 m², 10 g/m², Kourou: **798 vacuum / 682 coast → 519 m/s**, 100 GW × 130 s = **12,990 GJ**, but perigee stays underground (−634 km) and Teq is 4,060 K. The largest leftover cuts in the whole sweep are this kind of staged 100 GW case, about 280–306 m/s off the vacuum number, still far from a 200 km perigee.

**Immediate unfold at the 80 km mouth** (100 m², Kourou) is worse: sail drag of order 10 km/s stops the dart, residual ~7,960 m/s, perigee at the Earth’s center scale, even at 10 GW. The evac tube’s job was to keep this speed out of thick air; opening a sail at the mouth gives that work back.

### No-track contrast

With the rail removed, a sail opened at the pad does not climb (max altitude ~0.01 km at Kourou; leftover ~8,031 m/s). Starting instead from the recycled no-track burnout (f_p = 0.85, T/W = 3, I_sp = 450 s, Kourou: 95 km, inertial 7,486 m/s, vacuum leftover 661 m/s, remaining mass 1.88 kg plus sail, 80 km downrange labeled), a 10 GW / 100 m² / 10 g/m² gated push cuts the leftover to **514 m/s**, perigee still −538 km, Teq 2,780 K. No lock. The binding constraints are the same ones, now with even less mass and a start still in residual air.

### Binding constraints

The leftover is only a few hundred m/s, but the launch-site light window cannot spend it as an apogee repeater. In this model the tight constraints are, in order:

1. **Residual-atmosphere drag on an unfolded sail at 80+ km.** A 100 m² sail at 7.7 km/s sees ~90 kN at 80 km and still ~119 N at 120 km, against 63 N of photon force at 10 GW. Smart unfold has to wait until ~130 km, and even then drag is comparable to thrust.
2. **Geometry of the one-site window.** Useful illumination is on the climbing leg. For the 0° exit, 80 km is already perigee and apogee is out of view, so perigee cannot be raised to 200 km. For the 5° exits, apogee is also still ahead when the horizon cuts the beam.
3. **Stretching, if the gate is left off.** An ungated 100 GW push on the 5° evac dart drove the leftover to ~1,400 m/s by raising apogee to 8,300 km — the same “side pulse stretches the circuit” failure the redstone comparator was written to block. The residual gate stops that stretch; it does not close the gap.
4. **Sail heating.** Almost every run in which the sail actually opened had a radiation-equilibrium temperature above the parent PEEK degrade band (803 K): 2,176 K at 10 GW / 100 m², 4,700 K at 100 GW / 100 m², and higher on 10 m². This is a labeled equilibrium proxy, not a wall-temperature certificate.
5. **Power × time** at the high end is already 10³–10⁴ GJ and is still not enough, under the constraints above, to lock. Diffraction, with the labeled 3 m / 1.06 μm aperture, is not the limiter.

### Conjunctive loop

Dictator streamed admit / unfold / shutter / fail events into Transcriber; Levy assessed them (total weight 5,495). Nexus registered unboosted leftovers and site policies. Oasis and PrinciplesGate admitted the four real focus sites. A labeled NaCl pass treated the sail push as opposite-charge to the leftover (it can close), sail drag and due-east stretch as same-charge (they widen), and heating as a same-charge cap on power. Invert-and-restabilize is the same rule as in the parent notes; no run locked, so the recombine of the 10 GW / 100 m² Kourou leftovers stays at a mean residual of 344 m/s (matched only on the dimensionless 0.2 threshold, not as an orbit lock).

### Limits

All of this is a labeled model. The two-burn residual is a vacuum metric, as in the parent notes; drag and heating are applied only during the integrated window. The thermosphere anchors are orders of magnitude, not a tabulated standard atmosphere. The force law ignores beam jitter, adaptive optics, and weather. The residual gate is a one-step Kepler trial, not a flown guidance law. Best azimuth is the recycled 5° grid. Chassis and sail masses are bookkeeping, not a built vehicle. A second, downrange laser site at apogee was not modeled; it would be a different assumption. No configuration locked a 200 km circular orbit. No site, power, or sail is recommended.

---

*Source: recycled exits from Magnetic_Launch_GoalSeek_Continuation.md, Geography_Launch_Sites_Addendum.md, and Redstone_Repeater_Comparator_Addendum.md. New evaluation: scripts/run_light_sail_push.py, outputs/light_sail_push.json. Figure: figures/fig12_light_sail_push.svg.*
