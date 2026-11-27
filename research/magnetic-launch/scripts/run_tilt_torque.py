#!/usr/bin/env python3
# NON-CONJUNCTIVE (audit 2026-11-27): NO Oroboro component calls (physics only).
# Kept for history; results are pre-integration. The conjunctive baseline (all Oroboro
# components on one loop) is research/metastasis-native (integrated=True) and
# research/cross-domain/scripts/run_conjunctive_check.py; an integrated launch rebuild is pending.
# Speculative modeling only. No engineering, flight or operational claims.
"""Tilt and torque add-on. Recycles helpers from run_goal_seek_recycle.
Does not re-run the settled search, graphs, or pose work.
Speculative modeling only.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_goal_seek_recycle as G

OUT = G.OUT
G_STD, MU, RE, MPH = G.G_STD, G.MU_EARTH, G.R_EARTH, G.MPH
BOWL_R = G.BOWL_R
V_CIRC = G.V_CIRC_200KM


def tilt_geometry(beta_deg, R=BOWL_R):
    """Dual-Epcot / rim plane tilted by beta from horizontal.
    Release at the azimuth where the tangent climb angle equals beta
    and the release height equals the rim-center height.
    Vertical footprint of the machine is 2 R sin(beta).
    Path centripetal acceleration v^2/R lies in the tilted plane and is
    unchanged by the tilt (same as the non-spinning-interior result).
    """
    b = math.radians(beta_deg)
    return {
        "beta_deg": beta_deg,
        "R_m": R,
        "climb_angle_at_release_deg": beta_deg,
        "vertical_footprint_m": 2.0 * R * abs(math.sin(b)),
        "release_height_offset_from_center_m": 0.0,
        "rim_circumference_m": 2.0 * math.pi * R,
    }


def helix_length(delta_h, gamma_deg):
    """Path length of a constant-inclination helix (or straight climb) to gain delta_h."""
    g = math.radians(gamma_deg)
    if abs(math.sin(g)) < 1e-12:
        return float("inf")
    return abs(delta_h) / math.sin(g)


def spinup_budget(m_shell, R, v, t_spin_s):
    """Labeled thin-rim shell I = m R^2, spun to v = omega R in time t_spin.
    Average power depends on kinetic energy and time, not on R.
    Average torque scales with R.
    """
    if t_spin_s <= 0 or R <= 0:
        return None
    omega = v / R
    I = m_shell * R * R
    E = 0.5 * I * omega * omega  # = 0.5 m v^2
    tau = I * (omega / t_spin_s)
    P_avg = E / t_spin_s
    return {
        "m_shell_kg": m_shell, "R_m": R, "v_m_s": v, "v_mph": v / MPH,
        "omega_rad_s": omega, "omega_rpm": omega * 60.0 / (2.0 * math.pi),
        "I_kg_m2": I, "E_spin_J": E, "t_spin_s": t_spin_s,
        "tau_avg_N_m": tau, "P_avg_W": P_avg,
        "path_g": (v * v / R) / G_STD,
        "note": "Thin-rim I=m R^2 is a labeled assumption, not a measured shell.",
    }


def residual_interior_torque(omega_shell, I_int, c_over_I=0.05, Kp_over_I=8.0):
    """Steady residual from the held-despun model already used.
    tau_leak = c (omega_s - omega_ss) = Kp * omega_ss.
    """
    omega_ss = (c_over_I * omega_shell) / (c_over_I + Kp_over_I)
    c = c_over_I * I_int
    Kp = Kp_over_I * I_int
    tau_hold = Kp * omega_ss
    return {
        "I_int_kg_m2": I_int, "c_over_I_s": c_over_I, "Kp_over_I_s": Kp_over_I,
        "omega_shell_rad_s": omega_shell, "omega_ss_rad_s": omega_ss,
        "omega_ss_rpm": omega_ss * 60.0 / (2.0 * math.pi),
        "tau_hold_N_m": tau_hold, "P_hold_W": tau_hold * omega_ss,
        "spin_g_at_5cm": (omega_ss ** 2) * 0.05 / G_STD,
    }


def vane_torque(h_m, v, area_dart=0.008, porosity=0.0, lever_m=0.30):
    """Available aerodynamic torque from deployed feather vanes: q S Cl * lever.
    Lever arm 0.30 m is a labeled drone-scale assumption.
    """
    rho = G.rho_isa(h_m)
    q = 0.5 * rho * v * v
    S, Cl, Cd_ex = G.feather_aero(area_dart, porosity)
    L = q * S * Cl
    D_ex = q * S * Cd_ex
    return {
        "h_m": h_m, "v_m_s": v, "q_pa": q, "S_m2": S, "Cl": Cl,
        "lift_N": L, "extra_drag_N": D_ex,
        "tau_vane_N_m": L * lever_m, "lever_m": lever_m,
    }


def fly_release(v, beta_deg, h0, mass, cd, area, stages=True):
    fl = {}
    fl["ballistic_no_stage"] = G.fly(v, beta_deg, h0, mass, cd, area, lift=False, deploy_mode="never")
    if stages:
        ang = math.radians(beta_deg)
        for name, isp in (("storable_300s", G.ISP_STORABLE), ("lh2_450s", G.ISP_LH2)):
            dv = G.stage_dv(isp)
            v2, a2 = G.apply_dv(v, ang, dv, "horizontal")
            fl[f"{name}_horizontal"] = {
                **G.fly(v2, math.degrees(a2), h0, mass * (1.0 - G.FP_STAGE), cd, area,
                        lift=False, deploy_mode="never"),
                "stage_dv_m_s": dv, "isp_s": isp,
            }
    best = min((n, f.get("residual_200km_m_s"), f.get("apogee_km"))
               for n, f in fl.items() if f.get("residual_200km_m_s") is not None)
    best = min(((n, f.get("residual_200km_m_s"), f.get("apogee_km"))
                for n, f in fl.items() if f.get("residual_200km_m_s") is not None),
               key=lambda z: z[1])
    return {"flights": {n: {k: f[k] for k in f if k not in ("hist", "series")} for n, f in fl.items()},
            "best_flight": best[0], "best_residual_m_s": best[1], "best_apogee_km": best[2],
            "reached_karman_any": any(f.get("reached_karman") for f in fl.values())}


def always_deploy_lift(v_mph, ang, h, mass=20.0, cd=0.30, area=0.008):
    v = v_mph * MPH
    base = G.fly(v, ang, h, mass, cd, area, lift=False, winds=False, deploy_mode="never")
    # already-deployed: start with deployed=True so q-gate cannot block the vanes
    lifted = G.fly(v, ang, h, mass, cd, area, lift=True, winds=False, deploy_mode="never", deployed=True)
    windy = G.fly(v, ang, h, mass, cd, area, lift=True, winds=True, deploy_mode="never", deployed=True)
    return {
        "v_mph": v_mph, "angle_deg": ang, "h0_m": h,
        "ballistic_apogee_km": base["apogee_km"],
        "lift_apogee_km": lifted["apogee_km"],
        "lift_winds_apogee_km": windy["apogee_km"],
        "delta_apogee_km": lifted["apogee_km"] - base["apogee_km"],
        "delta_apogee_winds_km": windy["apogee_km"] - base["apogee_km"],
        "ballistic_residual_m_s": base["residual_200km_m_s"],
        "lift_residual_m_s": lifted["residual_200km_m_s"],
        "ballistic_peak_q_pa": base["peak_q_pa"],
        "lift_peak_q_pa": lifted["peak_q_pa"],
        "note": "Vanes forced open from t=0; 5 kPa q-gate is bypassed. Structural/heating feasibility is not claimed.",
    }


def powered_tube_to_exit(v_target, geometry, theta0, theta1, mass, cd, area, peak_a,
                         h0=0.0, evac_h=80000.0, dt=0.01):
    """Keep damper-metered pulses on until the evac-tube mouth, not just until v_target."""
    th0 = math.radians(theta0)
    th1 = None if theta1 is None else math.radians(theta1)
    v = t = s = 0.0
    y = float(h0)
    period = G.T_PULSE
    cap_t, cap_s = 8000.0, 1.0e7
    while t < cap_t and s < cap_s:
        phi = G.phi_of_s(geometry, s, th0, th1)
        # still inside tube: no drag
        g_along = G_STD * math.sin(phi) * (RE / (RE + max(0.0, y))) ** 2
        on = (t % period) < G.PULSE_ON
        a_along = (peak_a if on else 0.0) - g_along
        v = max(0.0, v + a_along * dt)
        ds = v * dt
        s += ds
        y += ds * math.sin(phi)
        t += dt
        if y >= evac_h and v >= v_target:
            break
        # if we already have speed but haven't reached the mouth, keep pulsing
        # (that is the whole point); only stop when both conditions hold
    reached = v >= v_target * 0.98 and y >= evac_h * 0.98
    return {
        "reached_target": reached, "v_end_m_s": v, "v_end_mph": v / MPH,
        "length_km": s / 1000.0, "time_s": t, "exit_alt_m": y,
        "exit_angle_deg": math.degrees(G.phi_of_s(geometry, s, th0, th1)),
        "peak_push_m_s2": peak_a,
    }


def main():
    mass, cd, area = 20.0, 0.30, 0.008
    betas = [0, 5, 8, 10, 15, 20, 30, 45]
    speeds = [3000.0, 8000.0, 17000.0]
    alts = [0.0, 4000.0, 30000.0, 80000.0]
    sweep = []
    for sp in speeds:
        v = sp * MPH
        for h0 in alts:
            for beta in betas:
                geo = tilt_geometry(beta)
                ev = fly_release(v, beta, h0, mass, cd, area, stages=True)
                row = {"speed_mph": sp, "h0_m": h0, "beta_deg": beta,
                       "vertical_footprint_m": geo["vertical_footprint_m"],
                       "path_g": (v * v / BOWL_R) / G_STD,
                       **{k: ev[k] for k in ev if k != "flights"},
                       "flights": ev["flights"]}
                sweep.append(row)
            print(f"  tilt sweep {sp} mph h0={h0/1000:.0f} km done")

    # best beta at each (speed, alt) by residual (must reach 100 km to count as a Y(a) candidate)
    optima = []
    for sp in speeds:
        for h0 in alts:
            cand = [r for r in sweep if r["speed_mph"] == sp and r["h0_m"] == h0 and r["reached_karman_any"]]
            if not cand:
                cand = [r for r in sweep if r["speed_mph"] == sp and r["h0_m"] == h0]
            best = min(cand, key=lambda r: r["best_residual_m_s"])
            optima.append({k: best[k] for k in best if k != "flights"})
            print("  OPT", sp, "mph", h0/1000, "km beta", best["beta_deg"],
                  "res", round(best["best_residual_m_s"], 1), "via", best["best_flight"],
                  "apo", round(best["best_apogee_km"], 1))

    # Helix vs tilted rim vs 80 deg bowl, to reach 80 km altitude while going to a speed
    helix_rows = []
    for gamma in (5, 8, 15, 30, 45, 80):
        helix_rows.append({
            "gamma_deg": gamma,
            "s_to_80km_m": helix_length(80000.0, gamma),
            "s_to_80km_km": helix_length(80000.0, gamma) / 1000.0,
            "g_along_over_g": math.sin(math.radians(gamma)),
            "tilted_rim_footprint_for_same_angle_m": 2.0 * BOWL_R * math.sin(math.radians(gamma)),
        })

    # Spin-up and residual torque budgets
    payloads_shell = [(20.0, 200.0), (20.0, 1000.0), (200.0, 2000.0)]
    radii = [BOWL_R, 50.0, 250.0]
    times = [60.0, 300.0, 900.0]
    budgets = []
    for m_pay, m_shell in payloads_shell:
        for R in radii:
            for sp in (3000.0, 17000.0):
                v = sp * MPH
                for tsu in times:
                    budgets.append({
                        "m_payload_kg": m_pay,
                        **spinup_budget(m_shell, R, v, tsu),
                    })

    # Interior residual torque at consistent bowl omega AND at the earlier 1200 rpm example
    I_int_20 = 20.0 * (0.10 ** 2)  # 0.20 kg m^2, k=10 cm, labeled
    I_int_200 = 200.0 * (0.25 ** 2)
    residual_tau = {
        "assumptions": "I_int = m k^2 with k=0.10 m (20 kg) or 0.25 m (200 kg), labeled.",
        "bowl_3000mph_R2500": residual_interior_torque(3000*MPH/BOWL_R, I_int_20),
        "bowl_17000mph_R2500": residual_interior_torque(17000*MPH/BOWL_R, I_int_20),
        "compact_1200rpm_I20": residual_interior_torque(1200*2*math.pi/60, I_int_20),
        "compact_1200rpm_I200": residual_interior_torque(1200*2*math.pi/60, I_int_200),
        "compact_50m_3000mph": residual_interior_torque(3000*MPH/50.0, I_int_20),
    }

    # Vane / control torque at a few states
    vane_rows = []
    for h, sp, note in (
        (10000.0, 400, "tropospheric glide"),
        (10000.0, 1000, "mid troposphere, 1000 mph"),
        (15000.0, 2000, "lower stratosphere"),
        (30000.0, 3000, "upper-tier, 3000 mph"),
        (80000.0, 17000, "evac mouth, 17000 mph"),
        (33847.0, 3000, "best-search unstaged exit"),
    ):
        vt = vane_torque(h, sp * MPH)
        vt["note"] = note
        vt["speed_mph"] = sp
        # I_veh * alpha for 2 deg in 1 s (the labeled onboard cap, as a 1-s average)
        I_veh = 20.0 * (0.15 ** 2)
        alpha = math.radians(2.0) / 1.0
        vt["tau_needed_2deg_per_s_N_m"] = I_veh * alpha
        vt["I_veh_kg_m2"] = I_veh
        vt["vane_can_meet_2deg_s"] = abs(vt["tau_vane_N_m"]) >= vt["tau_needed_2deg_per_s_N_m"]
        vane_rows.append(vt)

    # Always-deployed lift (q-gate bypassed) — honest upper bound on altitude help
    lift_forced = []
    for lab, sp, ang, h in (
        ("15km_2000mph_25deg", 2000, 25.0, 15000.0),
        ("5km_1000mph_30deg", 1000, 30.0, 5000.0),
        ("20km_3000mph_15deg", 3000, 15.0, 20000.0),
        ("10km_400mph_10deg_glide", 400, 10.0, 10000.0),
        ("8km_600mph_8deg", 600, 8.0, 8000.0),
    ):
        row = always_deploy_lift(sp, ang, h)
        row["label"] = lab
        lift_forced.append(row)
        print("  lift forced", lab, "dH", round(row["delta_apogee_km"], 3),
              "ball", round(row["ballistic_apogee_km"], 3), "lift", round(row["lift_apogee_km"], 3))

    # Powered-to-tube-mouth vs the earlier unpowered-tube-coast
    veh = G.vehicle_from_mass(20.0, "cfrp", hollow_k=0.8)
    powered = []
    for p in (
        dict(sp=3000.0, g=3.0, a0=80, a1=15, geom="flatten"),
        dict(sp=17000.0, g=100.0, a0=50, a1=8, geom="flatten"),
        dict(sp=17000.0, g=1000.0, a0=45, a1=5, geom="flatten"),
    ):
        tr = powered_tube_to_exit(p["sp"]*MPH, p["geom"], p["a0"], p["a1"],
                                  veh["mass"], veh["cd"], veh["area"], p["g"]*G_STD)
        ev = G.evaluate_exit(tr, veh["mass"], veh["cd"], veh["area"], stages=True, lift=False)
        ev["search_score"] = G.score_candidate(ev)
        powered.append({"cfg": p, "track": tr,
                        "best_residual_m_s": ev["best_residual_m_s"],
                        "best_apogee_km": ev["best_apogee_km"],
                        "flights": {n: {k: f[k] for k in ("apogee_km","residual_200km_m_s","reached_karman","v_at_apogee_m_s") if k in f}
                                    for n, f in ev["flights"].items()}})
        print("  powered tube", p, "vend", round(tr["v_end_mph"], 1), "alt", round(tr["exit_alt_m"]/1000, 2),
              "ang", round(tr["exit_angle_deg"], 2), "res", round(ev["best_residual_m_s"], 1),
              "L", round(tr["length_km"], 1), "t", round(tr["time_s"], 1))

    # Figure: residual vs tilt at 80 km and at 30 km
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 4.6), sharey=True)
    for ax, h0, title in ((axes[0], 80000.0, "Release at 80 km (evac mouth)"),
                          (axes[1], 30000.0, "Release at 30 km")):
        for sp, col, mk in ((3000.0, "#1f3a5f", "o"), (8000.0, "#3a7d44", "s"), (17000.0, "#d65a31", "^")):
            rows = [r for r in sweep if r["speed_mph"] == sp and r["h0_m"] == h0]
            rows.sort(key=lambda r: r["beta_deg"])
            ax.plot([r["beta_deg"] for r in rows], [r["best_residual_m_s"]/1000.0 for r in rows],
                    mk+"-", color=col, label=f"{sp:.0f} mph")
        ax.set_xlabel("Spin-plane / release tilt (deg)")
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
    axes[0].set_ylabel("Best residual Δv to 200 km circular (km/s)")
    fig.suptitle("Tilted dual-Epcot release: residual vs spin-plane tilt", fontsize=12)
    fig.tight_layout()
    figpath = OUT / "fig09_tilt_torque.png"
    fig.savefig(figpath, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("wrote", figpath)

    out = {
        "geometry_note": "Climb angle at the mid-height release azimuth equals the spin-plane tilt. Path g = v^2/R is unchanged by tilt. Vertical footprint = 2 R sin(beta), R=2500 m assumed.",
        "sweep_optima": optima,
        "helix": helix_rows,
        "spinup_budgets": budgets,
        "residual_interior_torque": residual_tau,
        "vane_control_torque": vane_rows,
        "lift_forced_deploy": lift_forced,
        "powered_tube_to_mouth": powered,
        "figure": str(figpath),
        "assumptions": [
            "Speculative modeling only.",
            "Thin-rim I = m R^2; spin-up at constant average torque over a labeled time.",
            "c/I=0.05 /s and Kp/I=8 /s recycled from the isolator model (labeled).",
            "Vane lever 0.30 m and vehicle radius of gyration 0.15 m are labeled drone-scale values.",
            "Upper-stage Isp and mass fraction are the same optimistic labels as the parent search.",
            "R=50 m and 250 m compact spinners are comparison assumptions, not vendor specs. HARP / SpinLaunch / StarTram named as well-known concepts only.",
        ],
        # compact sweep without full flights for the note
        "sweep_summary": [
            {k: r[k] for k in r if k != "flights"} for r in sweep
        ],
    }
    (OUT / "tilt_torque.json").write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print("wrote", OUT / "tilt_torque.json")


if __name__ == "__main__":
    main()
