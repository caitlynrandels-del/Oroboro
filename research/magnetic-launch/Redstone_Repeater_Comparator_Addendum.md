# Oroboro Structures for Consciousness Mapping
## Addendum: A Repeater and a Comparator on the Residual Gap
### Plus a no-track pad ascent, with Earth rotation as a gated side pulse

**Status:** Speculative modeling exercise only. Not an engineering design, a flight plan, a siting recommendation, or a claim that a dart can reach orbit. No operational claims. Residuals and exits are recycled from the goal-seek continuation and the geography addendum; only the repeater burns, the azimuth / admission gate, and the no-track pad integrations are new. HARP, SpinLaunch, and StarTram are not given invented numbers.

Prepared 27 November 2026 (America/Denver). Components were run in one loop: Genesis → Nexus register → Oasis admission → PrinciplesGate → NaCl consensus → Dictator stream → Transcriber → Levy assess → damped deterministic recombine. The `Math.random` stub in `oroboro-core.js` was not used.

### The redstone mapping

The leftover two-burn Δv to a 200 km circular orbit is treated as signal strength short of locking the final piston. Earth rotation at a launch site is the side pulse: added in-track (due east) it can close a small gap, or it can raise apogee and leave perigee underground — stretching the circuit. A **repeater** is a late two-burn at apogee and at the 200 km apsis, paid for with the rocket equation from the vehicle’s own mass, not with free Δv. A **comparator in subtraction mode** cannot switch Earth rotation off. “Suppress” is modeled only with levers that already exist: launch azimuth (near-polar, so rotation sits almost out of the trajectory plane), and Oasis / PrinciplesGate admission of a site for a due-east corridor. The gate admits due east only when the unboosted residual is already at or below a swept threshold T.

Orbit *lock* in this note means a two-burn residual to 200 km circular of ≤ 1 m/s and a perigee ≥ 100 km.

### Recycled setups

Hollow-bone dart mass is the recycled 12.56 kg vehicle (k = 0.8, payload fraction 0.30 on a 20 kg request). The staged stack is the recycled 125.6 kg hollow-scaled vehicle, with f_p = 0.85 already spent on the first I_sp = 450 s horizontal stage; a repeater there is a fraction of the remaining 18.84 kg, not a second 0.85 of the original mass. Unboosted Kepler residuals, recycled:

| Setup | Residual | Apogee | Perigee | Mass at release |
|-------|--------:|-------:|--------:|----------------:|
| Evac dart, 5°, 80 km (17,093 mph, pusher held) | 406.9 m/s | 373 km | −886 km | 12.56 kg |
| 5° tilt, 17,000 mph, 80 km | 431.2 m/s | 343 km | −974 km | 12.56 kg |
| 0°, 17,000 mph, 80 km | 333.0 m/s | 80 km (no climb) | −711 km | 12.56 kg |
| Staged config (true Kepler, not the invalid 256 m/s figure) | 1,148 m/s | 5,436 km | −234 km | 18.84 kg |

I_sp = 300 s and 450 s, and the mass fractions 0.05 / 0.30 / 0.85, are the same labeled assumptions as the parent notes. The 0.05 fraction was the heat-regrowth filament budget; using it as propellant is a re-purpose, not a second mass. The 0.85 fraction was the optimistic first-stage budget and is not part of the no-stage dart’s flown allocation. Adding a repeater to that dart is a new mass assignment.

At I_sp = 450 s, those fractions buy **226 / 1,574 / 8,372 m/s**. Closing the unboosted leftovers needs f_p = **0.088 / 0.093 / 0.073 / 0.229** respectively. The filament budget does not cover the 5° leftovers or the staged leftover; the payload fraction does, at 450 s. At 300 s the payload fraction (1,049 m/s) still covers the no-stage leftovers and does not cover a due-east staged residual of 1,430 m/s.

### Repeater

The repeater spends its Δv budget on the parent two-burn, apogee first. If the budget covers the leftover, residual goes to 0 and perigee is 200 km.

On due-east geography releases, at I_sp = 450 s:

- **f_p = 0.05 (filament, 226 m/s).** Locks all fourteen real sites on the 0° / 80 km exit (due-east leftovers 66–206 m/s all fit; Baikonur needs only f_p = 0.015, LAS 0.027). On the 5° evac dart and 5° tilt it is not enough to circularize (Baikonur 338 → 112 m/s and 329 → 103 m/s): the first burn can raise perigee to 200 km, but a 100-odd m/s circularization remains. On the staged leftover it barely moves the needle (Baikonur 1,430 → 1,203 m/s).
- **f_p = 0.30 (payload fraction, 1,574 m/s).** Locks every due-east site on all four setups, including the staged stack’s post-stage mass. For the staged due-east case the needed fraction of the remaining 18.84 kg is 0.28 at Baikonur — just inside 0.30. Best-azimuth on that config needs only 0.18 of the remaining mass. This lock is a mass-bookkeeping result, not a structural certificate, and it turns the no-stage dart into a staged vehicle.
- **f_p = 0.85** also locks, and is the optimistic first-stage fraction already spent on the staged config; treating it as still available on the dart would double-count that assumption.

Mass on the 12.56 kg dart: 407 m/s at 450 s is 1.11 kg (f_p = 0.088), more than the 0.63 kg filament budget and less than a 3.77 kg payload-fraction allocation. Failure modes: a filament-only repeater leaves the 5° ellipses bound with a 200 km perigee but not circular; a repeater does not fix heating, rail g, or an underground perigee until the burn is actually applied; the invalid 256 m/s staged figure is still not a budget.

### Comparator

Thresholds from 50 to 2,000 m/s were swept. Due east is admitted only when the unboosted residual ≤ T *and* PrinciplesGate allows a non-zero site coordinate. The idealized equator reference, at (0, 0, 0), is blocked by AdaptOrDie (“confront reality, not null”) as a siting admission; it remains a physics curve only. Real listed sites pass.

The gate is a binary on/off for the in-track boost. A continuous azimuth already in the model is a stronger lever. Mean residuals over the fourteen real sites:

| Setup | Always due east | Comparator when it suppresses (T below the unboosted leftover) | Always best azimuth |
|-------|----------------:|---------------------------------------------------------------:|--------------------:|
| 0° / 80 km | 153 m/s | 336 m/s (hurts; climb is lost) | **42 m/s** |
| 5° evac dart | 372 m/s | 409 m/s (slightly worse) | **328 m/s** |
| 5° tilt | 353 m/s | 433 m/s (worse) | **326 m/s** |
| Staged (true 1,148) | 1,507 m/s | **1,144 m/s** (helps vs due east) | **834 m/s** |

The comparator *never* beat always-best-azimuth on any site or threshold (0 of 14). It beats always-due-east only on the staged config, where a due-east boost stretches the already-high ellipse (1,148 → 1,430–1,558 m/s). There, suppressing (near-polar, azimuth ≈ 182°) holds the residual near the unboosted 1,148 m/s, and a westward best azimuth (270°) does better still, 798–893 m/s, by taking rotation against the in-track overshoot.

On the 0° exit, best azimuth is the real story: a heading of about 40–65° (not due east) trims the in-track boost so the residual falls to 37 m/s at Baikonur and 38 m/s at LAS, against 66 and 119 m/s due east. Perigee is still 80 km until a repeater raises it. Suppressing to near-polar on that exit throws the climb away and returns a ~336 m/s leftover. So the comparator, used as a hard subtraction gate, is the wrong tool whenever the side pulse is what makes the vehicle climb. The honest in-model control is the azimuth itself, plus Oasis admission of a real site, not a threshold that zeros the boost.

### No-track: the rail removed

The magnetic / coaster track and the evac tube are taken out. The vehicle starts at rest relative to the pad and the co-rotating air (zero airspeed; no free rail speed). A constant-thrust burn at initial T/W = 3 or 10 (the parent rail-g figures, reused here as thrust-to-weight, labeled) follows a pitch program from near-vertical to 5° over the recycled 40 km flatten length. Earth rotation is added to the inertial state at burnout, the same way the geography layer adds a due-east boost, and only when the comparator / azimuth policy admits it. A reserved f_p for a 500 m/s repeater was also tried.

No no-track configuration locked. The binding constraint is **thick-air drag and heating**, not a missing last 100 m/s of propellant.

On the 12.56 kg dart, I_sp = 450 s, T/W = 3, due-east, all propellant in the ascent: f_p = 0.05 reaches 1.6 km (filament budget is not an orbital ascent). f_p = 0.30 reaches a 47 km apogee, still below Karman, with a Sutton–Graves radiation-equilibrium proxy already ~1,730 K (above every polymer band in the parent heat-regrowth table, including PEEK’s 530 °C degrade). f_p = 0.85 does cross Karman and 200 km (max altitude 354 km at Kourou, 366 km at LAS, 424 km from Mauna Kea’s elevation), with a burnout near 95–106 km at ~7.0–7.1 km/s. After the due-east inertial boost the two-burn residual is still **661 m/s at Kourou, 708 m/s at LAS, 756 m/s at Baikonur, 631 m/s at Mauna Kea**. Perigee stays underground. Peak q is ~384–406 kPa; the heating proxy is **5,160–5,240 K**. Reserving 500 m/s for a repeater made the ascent worse (Kourou residual 2,836 → 2,336 m/s after the reserved burn), because the climb then ended lower and slower. The 125.6 kg hollow-scaled vehicle at the same optimistic fraction gets a slightly lower leftover (609 m/s at Kourou) and even higher heating (~5,800 K). T/W = 10 burns in thicker air and leaves a larger residual.

The evac-tube mouth at 80 km was doing the work that a pad burn on this dart cannot: it kept the high-speed portion out of dense air. Remove the track, and even an optimistic 0.85 / 450 s budget does not lock, and the heating proxy is far beyond the parent material bands. That is a model result, not a vehicle design.

### Conjunctive loop

Dictator streamed admit / suppress / repeater / lock / fail events into Transcriber; Levy assessed them (total weight 968). Nexus registered unboosted leftovers and site policies. Oasis and PrinciplesGate ran the site-admission comparator; AdaptOrDie blocked only the zero-coordinate reference. A labeled NaCl pass locked repeater, best-azimuth, and comparator edges against leftover Δv, and left due-east boost same-charge as the leftover (it can stretch). Invert-and-restabilize held. A payload-fraction repeater at 450 s recombined the four setups’ due-east leftovers to a residual of 0 (matched). A filament-only repeater did not.

### Limits

All of this is a labeled model. The two-burn residual is a vacuum metric, as in the parent geography note. The repeater is impulsive and ignores finite-burn gravity and pointing. f_p and I_sp are assumptions, not certificates that a hollow dart can carry or survive those burns. Best azimuth is a 5° grid on the Kepler residual, not a flown guidance law, and it does not by itself raise an 80 km perigee out of the atmosphere. The no-track integrator is a 2-D point mass in a co-rotating atmosphere with a fixed pitch program; it is not a 3-D launch vehicle, and the Sutton–Graves T_eq is a high-speed proxy, not a CFD wall temperature. Closed-loop γ steering from the goal-seek note was not reused as a primary controller (that law had been harmful). No configuration without a paid repeater on a recycled high-altitude exit locked a 200 km circular orbit. No site is recommended.

---

*Source: recycled exits from Magnetic_Launch_GoalSeek_Continuation.md and Geography_Launch_Sites_Addendum.md (outputs/geography.json). New evaluation: scripts/run_redstone_repeater_comparator.py, outputs/redstone_repeater_comparator.json. Figure: outputs/fig11_redstone_repeater_comparator.png.*
