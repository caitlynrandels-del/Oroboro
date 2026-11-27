#!/usr/bin/env python3
# CONJUNCTIVE (audit 2026-11-27): one loop Genesis -> Nexus -> Oasis admission -> PrinciplesGate
# -> NaCl consensus -> Dictator -> Transcriber -> Levy -> damped deterministic recombine.
# Speculative modeling only. No engineering, flight, siting, power or operational claims.
"""Ground-based laser + reflective sail as a late-stage directed push.

Speculative modeling only. Not an engineering design, flight plan, or siting
recommendation. No operational claims. No vendor or facility specs.

After the magnetic / evac-tube exit, the vehicle is stripped to a hollow-bone
chassis plus an ultra-thin reflective sail that unfolds in the post-track
window. A ground laser at the geography site pushes the sail by reflective
photon momentum. The ~7.8 km/s circular-speed goal is already mostly supplied
by the rail (or, in the no-track contrast, by a chemical ascent); only the
recycled two-burn residual to a 200 km circular orbit has to be closed.

Lock: residual <= 1 m/s and perigee >= 200 km.

Components run in one loop: Genesis → Nexus → Oasis admission →
PrinciplesGate → NaCl consensus → Dictator → Transcriber → Levy → damped
deterministic recombine. The Math.random stub in oroboro-core.js is not used.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_goal_seek_recycle as G
import run_geography_addendum as GEO
import run_redstone_repeater_comparator as R

sys.path.insert(0, __import__("os").environ.get("OASIS_BRIDGE", "/workspace/oasis-build/SkyAriOasis/Bridge"))  # Oasis bridge (sky-ari-ai build) on the project computer
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "consciousness-mapping"))  # this repo
import oasis_core as core  # noqa: E402
import nacl_polarity_mesh as nacl  # noqa: E402

OUT = G.OUT
MU, RE, G_STD = G.MU_EARTH, G.R_EARTH, G.G_STD
LEO = G.LEO_ALT_M
KARMAN = G.KARMAN_M
C_LIGHT = 299792458.0
SIGMA_SB = 5.670374419e-8
FP_PAYLOAD = 0.30

# ----- labeled model assumptions (not certificates or vendor specs) -----
LAMBDA_M = 1.06e-6          # near-IR wavelength, labeled
APERTURE_M = 3.0            # transmitter diameter, labeled
TAU_ZENITH = 0.20           # zenith optical depth, labeled (~82% zenith transmission)
EL_MIN_DEG = 0.0            # geometric horizon; 5° is also recorded
RHO_SAIL = 0.90             # reflectivity, labeled (absorption 1-ρ, no transmission)
EPS_SAIL = 0.80             # emissivity, same order as the parent Sutton–Graves ε
CD_SAIL = 2.0               # flat-plate / free-molecular Cd, labeled
H_ISA_TOP = 86000.0
# Order-of-magnitude thermosphere density anchors (labeled, not a standard-
# atmosphere certificate). Parent ISA is used to 86 km; above that the parent
# file's isothermal extension is unphysically thin, so these anchors are
# log-interpolated instead. They are orders only: 5e-7, 2e-8, 2e-9, 2.5e-10.
RHO_ANCHORS_M = [
    (100000.0, 5.0e-7),
    (120000.0, 2.0e-8),
    (150000.0, 2.0e-9),
    (200000.0, 2.5e-10),
    (300000.0, 2.0e-11),
    (500000.0, 1.0e-12),
]

POWERS_W = [1e6, 1e7, 1e8, 1e9, 1e10, 1e11]   # 1 MW … 100 GW
AREAS_M2 = [10.0, 100.0, 1000.0]
SIGMAS_KG_M2 = [0.001, 0.010, 0.100]          # 1, 10, 100 g/m²
FOCUS_SITES = ("kourou", "mauna_kea", "chimborazo", "sriharikota")

LEVY = {
    "genesis": 0, "admit_site": 1, "suppress_site": 2, "sail_push": 4,
    "orbit_lock": 14, "fail": 2, "unfold": 1, "no_track_contrast": 7,
    "damper_reconcile": 4,
}


def rho_at(h):
    """ISA to 86 km; labeled log-interpolated thermosphere anchors above."""
    if h <= 0:
        return G.isa_T_P_rho(0)[2]
    if h <= H_ISA_TOP:
        return G.isa_T_P_rho(h)[2]
    pts = [(H_ISA_TOP, G.isa_T_P_rho(H_ISA_TOP)[2])] + list(RHO_ANCHORS_M)
    if h >= pts[-1][0]:
        # extend last interval's log-slope, floored
        h1, r1 = pts[-2]
        h2, r2 = pts[-1]
        s = math.log(r2 / r1) / (h2 - h1)
        return max(r2 * math.exp(s * (h - h2)), 1e-16)
    for i in range(1, len(pts)):
        h1, r1 = pts[i-1]
        h2, r2 = pts[i]
        if h <= h2:
            frac = (h - h1) / (h2 - h1)
            return math.exp(math.log(r1) + frac * math.log(r2 / r1))
    return pts[-1][1]


def chassis_masses(dart_mass):
    """Strip after the rail. Payload was 0.30 of the 20 kg request (6.0 kg)."""
    payload_req = 20.0 * FP_PAYLOAD          # 6.0 kg, recycled payload fraction
    chassis_dart = dart_mass - payload_req   # 6.559 kg hollow structure
    staged_remaining = 125.59297999321456 * (1.0 - 0.85)
    chassis_staged = staged_remaining * (chassis_dart / dart_mass)
    return {
        "payload_requested_kg": payload_req,
        "chassis_dart_kg": chassis_dart,
        "staged_remaining_kg": staged_remaining,
        "chassis_staged_stripped_kg": chassis_staged,
        "note": ("No-stage: jettison the 6.0 kg requested payload, leave the "
                 "6.56 kg hollow-bone chassis, then add sail mass σA. "
                 "Staged: start from the recycled remaining 18.84 kg after "
                 "f_p=0.85, then apply the same chassis/total ratio "
                 f"({chassis_dart/dart_mass:.4f}) to get a stripped chassis."),
    }


def residual_of(h_apo, v_apo):
    if h_apo is None or v_apo is None or h_apo < 0:
        return None
    return G.vacuum_transfer_residual(h_apo, v_apo)


def kepler_vac(h, v, gamma_deg):
    kep = GEO.kepler_from_state(h, v, gamma_deg)
    vac = None
    res = None
    if kep.get("h_apogee_m") is not None and kep.get("v_at_apogee_m_s") is not None:
        vac = residual_of(kep["h_apogee_m"], kep["v_at_apogee_m_s"])
        res = None if vac is None else vac[0]
    return kep, res, vac


def locked_of(res, peri_m):
    return bool(res is not None and res <= 1.0 and peri_m is not None and peri_m >= LEO)


def los_elevation_and_range(pos_v, pos_s):
    """Elevation (rad) from the site's local horizontal, and slant range (m)."""
    los = pos_v - pos_s
    L = np.linalg.norm(los)
    if L <= 1e-6:
        return math.pi / 2.0, L
    zen = pos_s / np.linalg.norm(pos_s)
    los_hat = los / L
    s = float(np.clip(np.dot(los_hat, zen), -1.0, 1.0))
    # el = π/2 - angle(los, zenith)
    el = math.asin(s) if abs(s) <= 1.0 else math.copysign(math.pi / 2.0, s)
    return el, L


def atm_transmission(el):
    if el <= 0.0:
        return 0.0
    return math.exp(-TAU_ZENITH / max(math.sin(el), 1e-4))


def spot_radius(L):
    """Airy first-minimum radius, 1.22 λ L / D. Labeled simple diffraction."""
    return 1.22 * LAMBDA_M * max(L, 1.0) / APERTURE_M


def intercept_fraction(L, area):
    w = spot_radius(L)
    a_spot = math.pi * w * w
    if a_spot <= 0:
        return 1.0, w, a_spot
    return min(1.0, area / a_spot), w, a_spot


def photon_force_vector(pos_v, pos_s, vel, P, area, rho, face="prograde_tilt"):
    """Force on the sail (N, 2-vector) and diagnostics.

    F = ((1+ρ) P_int / c) * cos(i) along the sail normal, with
    P_int = P * T_atm * f_spot * max(cos i, 0) already using the incidence
    cosine once in P_int and once as the force-direction factor?  We use the
    textbook tilted-sail form once: F_normal = (1+ρ) (P_beam T f_spot) cos(i) / c
    along the normal, i = angle(beam, normal), and we pick the normal to
    maximize the prograde component (or face the beam).
    """
    el, L = los_elevation_and_range(pos_v, pos_s)
    if el <= math.radians(EL_MIN_DEG) or P <= 0 or area <= 0:
        return np.zeros(2), {"el_deg": math.degrees(el), "L_m": L, "T_atm": 0.0,
                             "f_spot": 0.0, "P_int_W": 0.0, "F_N": 0.0, "i_deg": None}
    T = atm_transmission(el)
    f_spot, w, a_spot = intercept_fraction(L, area)
    P_beam = P * T * f_spot
    beam = pos_v - pos_s
    bhat = beam / np.linalg.norm(beam)
    # Prograde = local horizontal, in-track (sign of tangential speed).
    rhat = pos_v / np.linalg.norm(pos_v)
    # 2-D polar theta-hat
    that = np.array([rhat[1], -rhat[0]])  # if r=(x,y), this is one perp; fix sign
    # Use velocity projected into the horizontal as the prograde direction.
    v_h = vel - np.dot(vel, rhat) * rhat
    if np.linalg.norm(v_h) < 1e-6:
        e_p = that
    else:
        e_p = v_h / np.linalg.norm(v_h)

    if face == "beam":
        n = bhat
    else:
        # n along bhat + e_p maximizes (n·b)(n·e_p) when they are <90° apart.
        s = bhat + e_p
        sn = np.linalg.norm(s)
        n = s / sn if sn > 1e-9 else bhat
        if np.dot(n, bhat) <= 0:
            n = bhat
    cosi = float(np.dot(n, bhat))
    if cosi <= 0:
        return np.zeros(2), {"el_deg": math.degrees(el), "L_m": L, "T_atm": T,
                             "f_spot": f_spot, "P_int_W": 0.0, "F_N": 0.0,
                             "i_deg": math.degrees(math.acos(max(-1, min(1, cosi)))),
                             "spot_radius_m": w}
    P_int = P_beam * cosi
    Fmag = (1.0 + rho) * P_int / C_LIGHT
    F = Fmag * n
    return F, {"el_deg": math.degrees(el), "L_m": L, "T_atm": T, "f_spot": f_spot,
               "P_int_W": P_int, "F_N": Fmag,
               "i_deg": math.degrees(math.acos(max(-1, min(1, cosi)))),
               "spot_radius_m": w}


def state_residual(pos, vel):
    r = float(np.linalg.norm(pos))
    h = r - RE
    speed = float(np.linalg.norm(vel))
    if h <= 0 or speed <= 0 or not np.isfinite(h) or not np.isfinite(speed):
        return None, None, None
    rhat = pos / r
    vr = float(np.dot(vel, rhat))
    vt = float(np.linalg.norm(vel - vr * rhat))
    gamma = math.degrees(math.atan2(vr, vt if vt > 0 else 0.0))
    kep, res, vac = kepler_vac(h, speed, gamma)
    return res, kep, gamma


def integrate_sail_push(
    h0, v0, gamma_deg, mass, area, rho, P, site_elev_m, omega_plane,
    unfold="smart", face="prograde_tilt", shutter="residual",
    dt=0.05, t_max=400.0,
    theta0_downrange_m=0.0, dart_area=0.006, dart_cd=0.2,
):
    """2-D inertial-plane integration after release, laser at the geography site.

    shutter='residual' is the comparator analogue: the beam is on only when a
    trial pulse would lower the two-burn residual to 200 km circular. Otherwise
    the pulse is treated as stretching the ellipse and is cut.
    """
    Rs = RE + max(0.0, site_elev_m)
    r0 = RE + h0
    th0 = theta0_downrange_m / r0
    x = r0 * math.sin(th0)
    y = r0 * math.cos(th0)
    gam = math.radians(gamma_deg)
    rhat0 = np.array([x, y]) / r0
    that0 = np.array([rhat0[1], -rhat0[0]])
    vr = v0 * math.sin(gam)
    vt = v0 * math.cos(gam)
    vel = vr * rhat0 + vt * that0
    pos = np.array([x, y], dtype=float)
    vel = np.array(vel, dtype=float)

    unfolded = False
    t_unfold = None
    t_los_end = None
    t_shuttered = 0.0
    peak_Teq = 0.0
    peak_q = 0.0
    peak_drag = 0.0
    peak_F = 0.0
    impulse = 0.0
    energy_cmd = 0.0
    energy_on_sail = 0.0
    t_on = 0.0
    t_el5 = 0.0
    h_max = h0
    min_el = 90.0
    min_fspot = 1.0
    max_spot = 0.0
    drag_impulse = 0.0
    reason_end = "t_max"
    n_gate_pass = 0
    n_gate_block = 0

    def site_pos(t):
        ang = omega_plane * t
        return np.array([Rs * math.sin(ang), Rs * math.cos(ang)], dtype=float)

    def maybe_unfold(h, speed, pos, vel, t, spos):
        if unfold == "immediate":
            return True
        if unfold == "never":
            return False
        rho_a = rho_at(h)
        drag = 0.5 * rho_a * speed * speed * CD_SAIL * area
        F, diag = photon_force_vector(pos, spos, vel, P, area, rho, face="beam")
        return bool(diag["F_N"] >= drag and diag["F_N"] > 0)

    t = 0.0
    nstep = 0
    while t < t_max:
        r = float(np.linalg.norm(pos))
        if r <= RE or not np.isfinite(r):
            reason_end = "impact"
            break
        h = r - RE
        speed = float(np.linalg.norm(vel))
        if (not np.isfinite(speed)) or speed > 20000.0 or h > 5.0e6:
            reason_end = "unphysical_state"
            break
        spos = site_pos(t)
        el, L = los_elevation_and_range(pos, spos)
        el_deg = math.degrees(el)
        if el_deg < min_el:
            min_el = el_deg
        if el_deg >= 5.0:
            t_el5 += dt
        if el <= 0.0 and t_los_end is None and t > 0:
            t_los_end = t
        if not unfolded:
            if maybe_unfold(h, speed, pos, vel, t, spos):
                unfolded = True
                t_unfold = t

        acc = -MU * pos / (r ** 3)
        F_ph = np.zeros(2)
        diag = {"P_int_W": 0.0, "F_N": 0.0, "f_spot": 1.0, "T_atm": 0.0,
                "el_deg": el_deg, "L_m": L, "spot_radius_m": spot_radius(L)}
        laser_on = False
        if unfolded and el > math.radians(EL_MIN_DEG) and P > 0:
            # candidate force
            F_try, diag = photon_force_vector(pos, spos, vel, P, area, rho, face=face)
            use = True
            if shutter == "residual" and diag["F_N"] > 0:
                res0, _, _ = state_residual(pos, vel)
                res1, _, _ = state_residual(pos, vel + (F_try / mass) * dt)
                if res0 is None or res1 is None or res1 >= res0 - 1e-6:
                    use = False
                    n_gate_block += 1
                    t_shuttered += dt
                else:
                    n_gate_pass += 1
            if use and diag["F_N"] > 0:
                F_ph = F_try
                acc = acc + F_ph / mass
                laser_on = True
                t_on += dt
                energy_cmd += P * dt
                energy_on_sail += diag["P_int_W"] * dt
                impulse += diag["F_N"] * dt
                peak_F = max(peak_F, diag["F_N"])
                P_abs = (1.0 - rho) * diag["P_int_W"]
                if area > 0 and EPS_SAIL > 0 and P_abs > 0:
                    Teq = (P_abs / (2.0 * area * EPS_SAIL * SIGMA_SB)) ** 0.25
                    peak_Teq = max(peak_Teq, Teq)

        rho_a = rho_at(h)
        if speed > 1e-6:
            A_d = area if unfolded else dart_area
            cd = CD_SAIL if unfolded else dart_cd
            Fd = 0.5 * rho_a * speed * speed * cd * A_d
            acc = acc - (Fd / mass) * (vel / speed)
            peak_drag = max(peak_drag, Fd)
            peak_q = max(peak_q, 0.5 * rho_a * speed * speed)
            if unfolded:
                drag_impulse += Fd * dt
        if diag.get("f_spot") is not None and el > 0:
            min_fspot = min(min_fspot, diag["f_spot"])
        if diag.get("spot_radius_m"):
            max_spot = max(max_spot, diag["spot_radius_m"])

        vel = vel + acc * dt
        pos = pos + vel * dt
        t += dt
        nstep += 1
        h = float(np.linalg.norm(pos)) - RE
        if np.isfinite(h):
            h_max = max(h_max, h)
        if t_los_end is not None and (t - t_los_end) > 5.0:
            reason_end = "lost_los"
            break

    res, kep, gamma = state_residual(pos, vel)
    peri = kep.get("h_perigee_m") if kep else None
    apo = kep.get("h_apogee_m") if kep else None
    speed = float(np.linalg.norm(vel)) if np.isfinite(vel).all() else float("nan")
    h = float(np.linalg.norm(pos)) - RE if np.isfinite(pos).all() else float("nan")
    return {
        "t_end_s": t, "reason_end": reason_end, "unfolded": unfolded,
        "t_unfold_s": t_unfold, "t_los_end_s": t_los_end, "t_el5_s": t_el5,
        "t_on_s": t_on, "t_shuttered_s": t_shuttered,
        "n_gate_pass": n_gate_pass, "n_gate_block": n_gate_block,
        "h_end_km": h / 1000.0 if np.isfinite(h) else None,
        "h_max_km": h_max / 1000.0,
        "v_end_m_s": speed, "gamma_end_deg": gamma,
        "residual_after_m_s": res,
        "apogee_after_km": None if apo is None else apo / 1000.0,
        "perigee_after_km": None if peri is None else peri / 1000.0,
        "locked": locked_of(res, peri),
        "energy_cmd_J": energy_cmd, "energy_on_sail_J": energy_on_sail,
        "impulse_N_s": impulse, "dv_imparted_m_s": impulse / mass if mass > 0 else 0.0,
        "drag_impulse_N_s": drag_impulse,
        "dv_drag_m_s": drag_impulse / mass if mass > 0 else 0.0,
        "peak_Teq_K": peak_Teq, "peak_q_Pa": peak_q, "peak_drag_N": peak_drag,
        "peak_F_N": peak_F, "min_el_deg": min_el, "min_fspot": min_fspot,
        "max_spot_radius_m": max_spot,
        "nstep": nstep,
        "kepler_after": {k: kep.get(k) for k in ("bound", "ecc", "h_apogee_m", "h_perigee_m", "v_at_apogee_m_s")} if kep else None,
    }


def omega_in_plane(lat_deg, elev_m, az_deg):
    boost = GEO.v_rot_at_altitude(lat_deg, elev_m)
    Rs = RE + max(0.0, elev_m)
    return boost * math.sin(math.radians(az_deg)) / Rs


def binding_of(row, res_before):
    """Name the tightest labeled constraint on this run."""
    reasons = []
    if row.get("locked"):
        return "locked"
    if not row.get("unfolded"):
        reasons.append("never_unfolded_drag_window")
    if (row.get("dv_drag_m_s") or 0) > 0.5 * max(row.get("dv_imparted_m_s") or 0, 1.0):
        reasons.append("sail_drag")
    if (row.get("t_on_s") or 0) < 20:
        reasons.append("short_los_window")
    if (row.get("peak_Teq_K") or 0) > 803:
        reasons.append("sail_heating_above_PEEK_803K_band")
    peri = row.get("perigee_after_km")
    if peri is not None and peri < 200 and (row.get("apogee_after_km") or 0) > 80:
        # peri cannot exceed the lowest burn altitude in a simple apogee-at-80 picture
        if peri < 100:
            reasons.append("perigee_still_low_or_underground")
    res = row.get("residual_after_m_s")
    if res is not None and res_before is not None and res > 0.8 * res_before:
        reasons.append("power_or_window_insufficient")
    if (row.get("min_fspot") or 1) < 0.5:
        reasons.append("diffraction_spot_larger_than_sail")
    return reasons[0] if reasons else "residual_remains"


def run():
    cfgs, sites, dart = R.load_configs()
    masses = chassis_masses(dart["mass"])
    gate = core.PrinciplesGate(core.load_config())
    nexus = R.Nexus()
    transcriber = R.Transcriber()
    dictator = R.Dictator(transcriber)
    levy = R.Levy(transcriber)
    # reuse Levy weight table? Redstone Levy uses R.LEVY. Patch local weights.
    levy_local = type(levy)(transcriber)
    # we'll use our LEVY via a tiny wrapper
    class LevyL(R.Levy):
        pass
    # inject
    orig_assess = levy.assess
    def assess(kind, n=1):
        w = LEVY.get(kind, 1) * n
        levy.total += w
        levy.entries.append({"kind": kind, "weight": w})
        return w
    levy.assess = assess

    sim = R.RelationalSim(nexus)
    nexus.register("genesis", {"tag": "I am the OG avatar", "weight": math.inf})
    levy.assess("genesis")
    dictator.stream("genesis", "Light-sail push ledger. Recycled exits; new sail/laser window only.")

    site_by_id = {s["id"]: s for s in sites}
    focus = [site_by_id[i] for i in FOCUS_SITES if i in site_by_id]

    # Unboosted leftovers (recycled)
    unboosted = {}
    for key, cfg in cfgs.items():
        v, g, h, mass = R.staged_relative_state(cfg)
        kep, res, vac = kepler_vac(h, v, g)
        unboosted[key] = {
            "residual_m_s": res,
            "apogee_km": None if not kep.get("h_apogee_m") else kep["h_apogee_m"] / 1000.0,
            "perigee_km": None if not kep.get("h_perigee_m") else kep["h_perigee_m"] / 1000.0,
            "mass_at_release_before_strip_kg": mass,
            "v_rel_m_s": v, "gamma_deg": g, "h_m": h,
        }
        nexus.register(f"unboosted:{key}", unboosted[key])

    # Precompute best-azimuth and due-east release states at focus sites
    releases = []
    for key, cfg in cfgs.items():
        v, g, h, mass_rel = R.staged_relative_state(cfg)
        chassis = masses["chassis_dart_kg"] if key != "staged_256" else masses["chassis_staged_stripped_kg"]
        for site in focus:
            gr, pos_d = R.principles_allow_site(gate, site)
            allowed = bool(gr.allowed)
            if allowed:
                levy.assess("admit_site")
                dictator.stream("admit_site", f"Admit {site['id']} for {key}")
            else:
                levy.assess("suppress_site")
            best = R.best_azimuth(v, g, h, site["lat"], step=5.0)
            east = R.evaluate_release(cfg, site, 90.0)
            releases.append({
                "config": key, "site_id": site["id"], "site": site["name"],
                "lat": site["lat"], "elev_m": site["elev_m"],
                "ocean_east": site.get("ocean_east"), "kind": site.get("kind"),
                "gate_allowed": allowed, "gate_principle": gr.principle,
                "v_rel_m_s": v, "gamma_rel_deg": g, "h_m": h,
                "chassis_kg": chassis, "dart_area": cfg.get("area") or dart["area"],
                "dart_cd": cfg.get("cd") or dart["cd"],
                "best_az_deg": best["az_deg"] if best else None,
                "best_res_m_s": best["residual_m_s"] if best else None,
                "best_v_i": best["v_i"] if best else None,
                "best_g_i": best["g_i"] if best else None,
                "best_apo_km": best["apogee_km"] if best else None,
                "best_peri_km": best["perigee_km"] if best else None,
                "east_res_m_s": east["residual_m_s"],
                "east_v_i": east["v_inertial_m_s"],
                "east_g_i": east["gamma_inertial_deg"],
                "east_apo_km": east["apogee_km"],
                "east_peri_km": east["perigee_km"],
            })

    # Main sweep: best azimuth (settled comparator finding), smart unfold
    rows = []
    headline_series = []  # sparse time samples for one or two plots
    n_run = 0
    for rel in releases:
        if not rel["gate_allowed"]:
            continue
        if rel["best_v_i"] is None:
            continue
        omega = omega_in_plane(rel["lat"], rel["elev_m"], rel["best_az_deg"])
        for P in POWERS_W:
            for area in AREAS_M2:
                for sig in SIGMAS_KG_M2:
                    m = rel["chassis_kg"] + sig * area
                    rec = integrate_sail_push(
                        rel["h_m"], rel["best_v_i"], rel["best_g_i"], m,
                        area, RHO_SAIL, P, rel["elev_m"], omega,
                        unfold="smart", face="prograde_tilt",
                        dart_area=rel["dart_area"], dart_cd=rel["dart_cd"],
                    )
                    n_run += 1
                    row = {
                        "config": rel["config"], "site_id": rel["site_id"],
                        "site": rel["site"], "lat": rel["lat"], "elev_m": rel["elev_m"],
                        "ocean_east": rel["ocean_east"],
                        "az_policy": "best", "az_deg": rel["best_az_deg"],
                        "P_W": P, "P_label": _plabel(P),
                        "area_m2": area, "sigma_kg_m2": sig,
                        "sail_mass_kg": sig * area, "mass_kg": m,
                        "chassis_kg": rel["chassis_kg"],
                        "residual_before_m_s": rel["best_res_m_s"],
                        "apogee_before_km": rel["best_apo_km"],
                        "perigee_before_km": rel["best_peri_km"],
                        "unfold": "smart",
                        **{k: rec[k] for k in rec if k != "kepler_after"},
                    }
                    row["binding"] = binding_of(rec, rel["best_res_m_s"])
                    if rec["locked"]:
                        levy.assess("orbit_lock")
                        dictator.stream("orbit_lock", f"Lock {rel['config']} {rel['site_id']} P={P}")
                    else:
                        levy.assess("fail")
                    if rec["unfolded"]:
                        levy.assess("unfold")
                    levy.assess("sail_push")
                    rows.append(row)

    # Immediate-unfold contrast on a reduced grid (Kourou, mid sail 100 m² / 10 g/m²)
    immediate = []
    for rel in releases:
        if rel["site_id"] != "kourou" or not rel["gate_allowed"]:
            continue
        omega = omega_in_plane(rel["lat"], rel["elev_m"], rel["best_az_deg"])
        area, sig = 100.0, 0.010
        for P in POWERS_W:
            m = rel["chassis_kg"] + sig * area
            rec = integrate_sail_push(
                rel["h_m"], rel["best_v_i"], rel["best_g_i"], m,
                area, RHO_SAIL, P, rel["elev_m"], omega,
                unfold="immediate", face="prograde_tilt",
                dart_area=rel["dart_area"], dart_cd=rel["dart_cd"],
            )
            immediate.append({
                "config": rel["config"], "site_id": rel["site_id"],
                "P_W": P, "area_m2": area, "sigma_kg_m2": sig, "mass_kg": m,
                "residual_before_m_s": rel["best_res_m_s"],
                "apogee_before_km": rel["best_apo_km"],
                "perigee_before_km": rel["best_peri_km"],
                "unfold": "immediate",
                **{k: rec[k] for k in rec if k != "kepler_after"},
                "binding": binding_of(rec, rel["best_res_m_s"]),
            })

    # Due-east vs best-az at Kourou, 10 GW, 100 m², 10 g/m², smart unfold
    az_compare = []
    for rel in releases:
        if rel["site_id"] != "kourou" or not rel["gate_allowed"]:
            continue
        for policy, v_i, g_i, res_b, az, apo, peri in (
            ("best", rel["best_v_i"], rel["best_g_i"], rel["best_res_m_s"],
             rel["best_az_deg"], rel["best_apo_km"], rel["best_peri_km"]),
            ("due_east", rel["east_v_i"], rel["east_g_i"], rel["east_res_m_s"],
             90.0, rel["east_apo_km"], rel["east_peri_km"]),
        ):
            omega = omega_in_plane(rel["lat"], rel["elev_m"], az)
            area, sig, P = 100.0, 0.010, 1e10
            m = rel["chassis_kg"] + sig * area
            rec = integrate_sail_push(
                rel["h_m"], v_i, g_i, m, area, RHO_SAIL, P, rel["elev_m"], omega,
                unfold="smart", face="prograde_tilt",
                dart_area=rel["dart_area"], dart_cd=rel["dart_cd"],
            )
            az_compare.append({
                "config": rel["config"], "policy": policy, "az_deg": az,
                "residual_before_m_s": res_b, "residual_after_m_s": rec["residual_after_m_s"],
                "perigee_after_km": rec["perigee_after_km"],
                "apogee_after_km": rec["apogee_after_km"],
                "locked": rec["locked"], "t_on_s": rec["t_on_s"],
                "dv_imparted_m_s": rec["dv_imparted_m_s"],
            })

    # No-track contrasts
    no_track = []
    nt_src = json.loads((OUT / "redstone_repeater_comparator.json").read_text())["no_track"]
    nt_pick = None
    for r in nt_src:
        if (r["vehicle"] == "hollow_dart_12.6kg" and abs(r["fp"] - 0.85) < 1e-9
                and r["tw0"] == 3.0 and r["az_policy"] == "due_east"
                and r["reserve_mode"] == "all_in_ascent" and r["site_id"] == "kourou"
                and r.get("isp_s") == 450):
            nt_pick = r
            break
    # (a) unfold from the pad at rest — drag-bound contrast
    kourou = site_by_id["kourou"]
    omega_k = omega_in_plane(kourou["lat"], kourou["elev_m"], 90.0)
    for P in (1e9, 1e10, 1e11):
        area, sig = 100.0, 0.010
        m = masses["chassis_dart_kg"] + sig * area
        rec = integrate_sail_push(
            10.0, 1.0, 90.0, m, area, RHO_SAIL, P, kourou["elev_m"], omega_k,
            unfold="immediate", face="beam", t_max=200.0,
            dart_area=dart["area"], dart_cd=dart["cd"],
        )
        no_track.append({
            "kind": "pad_unfold", "site_id": "kourou", "P_W": P,
            "area_m2": area, "sigma_kg_m2": sig, "mass_kg": m,
            "residual_before_m_s": None,
            "note": "Start nearly at rest at the pad, sail already open. No rail speed.",
            **{k: rec[k] for k in rec if k != "kepler_after"},
            "binding": binding_of(rec, 7788.0),
        })
        levy.assess("no_track_contrast")
    # (b) after recycled f_p=0.85 no-track burnout at Kourou
    if nt_pick:
        # remaining mass after f_p=0.85 on the 12.56 kg dart; then add sail
        m_remain = dart["mass"] * (1.0 - 0.85)
        # labeled downrange at burnout: 80 km (order of the 40 km flatten plus climb)
        x_down = 80_000.0
        for area, sig in ((10.0, 0.010), (100.0, 0.010), (100.0, 0.001)):
            for P in (1e9, 1e10, 1e11):
                m = m_remain + sig * area
                rec = integrate_sail_push(
                    nt_pick["h_burnout_km"] * 1000.0,
                    nt_pick["v_inertial_burnout_m_s"],
                    nt_pick["gamma_inertial_deg"],
                    m, area, RHO_SAIL, P, kourou["elev_m"], omega_k,
                    unfold="smart", face="prograde_tilt",
                    theta0_downrange_m=x_down,
                    dart_area=dart["area"], dart_cd=dart["cd"],
                )
                no_track.append({
                    "kind": "post_burnout_fp085", "site_id": "kourou", "P_W": P,
                    "area_m2": area, "sigma_kg_m2": sig, "mass_kg": m,
                    "chassis_kg": m_remain,
                    "residual_before_m_s": nt_pick["residual_coast_m_s"],
                    "apogee_before_km": nt_pick["apogee_coast_km"],
                    "perigee_before_km": nt_pick["perigee_coast_km"],
                    "h_start_km": nt_pick["h_burnout_km"],
                    "v_start_m_s": nt_pick["v_inertial_burnout_m_s"],
                    "downrange_start_m": x_down,
                    **{k: rec[k] for k in rec if k != "kepler_after"},
                    "binding": binding_of(rec, nt_pick["residual_coast_m_s"]),
                })
                levy.assess("no_track_contrast")
                if rec["locked"]:
                    levy.assess("orbit_lock")

    # Time series for the figure: one 5° evac and one 0° case at 10 GW, 100 m², 10 g/m², Kourou
    series = {}
    for key in ("evac_dart_407", "tilt0_333"):
        rel = next(r for r in releases if r["config"] == key and r["site_id"] == "kourou")
        omega = omega_in_plane(rel["lat"], rel["elev_m"], rel["best_az_deg"])
        area, sig, P = 100.0, 0.010, 1e10
        m = rel["chassis_kg"] + sig * area
        # instrumented: hook by re-running a sampler
        series[key] = _sample_series(
            rel["h_m"], rel["best_v_i"], rel["best_g_i"], m, area, P,
            rel["elev_m"], omega, rel["dart_area"], rel["dart_cd"],
        )
        series[key]["residual_before_m_s"] = rel["best_res_m_s"]

    # Polarity / recombine
    # Labeled edges: leftover Δv, sail push, drag, heating, best azimuth
    try:
        mesh = nacl.PolarityMesh() if hasattr(nacl, "PolarityMesh") else None
    except Exception:
        mesh = None
    polarity = {"note": "labeled signs only", "edges_locked": None}
    try:
        # reuse a lightweight labeled pass if the module exposes the prior helper
        polarity = {
            "mode": "labeled_signs",
            "edges": [
                {"a": "sail_push", "b": "leftover_dv", "relation": "opposite_can_lock"},
                {"a": "sail_drag", "b": "leftover_dv", "relation": "same_charge_widens"},
                {"a": "best_azimuth", "b": "leftover_dv", "relation": "opposite_can_trim"},
                {"a": "due_east_boost", "b": "leftover_dv", "relation": "same_charge_can_stretch"},
                {"a": "heating", "b": "sail_push", "relation": "same_charge_limits_power"},
            ],
        }
    except Exception as e:
        polarity["error"] = str(e)

    # Recombine residuals after the 10 GW / 100 m² / 10 g/m² Kourou best-az smart runs
    reco_res = []
    for row in rows:
        if (row["site_id"] == "kourou" and row["P_W"] == 1e10
                and row["area_m2"] == 100.0 and abs(row["sigma_kg_m2"] - 0.01) < 1e-12):
            reco_res.append(row.get("residual_after_m_s"))
    recombine = sim.recombine(reco_res, damping=0.25)
    levy.assess("damper_reconcile")
    nexus.register("light_sail_rows_n", {"n": len(rows)})

    # Summary tables for the addendum
    locks = [r for r in rows if r["locked"]]
    summary = {
        "n_sweep": len(rows), "n_locks": len(locks),
        "locks": [
            {k: r[k] for k in ("config", "site_id", "P_W", "area_m2", "sigma_kg_m2",
                               "residual_before_m_s", "residual_after_m_s",
                               "perigee_after_km", "apogee_after_km", "t_on_s",
                               "energy_cmd_J", "dv_imparted_m_s", "peak_Teq_K", "binding")}
            for r in locks
        ],
    }

    assumptions = [
        "Speculative modeling only; not an engineering design, a flight plan, or a siting recommendation.",
        "The ~7.8 km/s figure is 200 km circular speed (7,788 m/s in this file). The rail already supplied most of it; only the recycled two-burn residual is asked of the sail.",
        "Lock means residual <= 1 m/s and perigee >= 200 km (stricter peri than the redstone Karman-100 km note).",
        "Laser powers 1 MW, 10 MW, 100 MW, 1 GW, 10 GW, 100 GW are labeled model values, not facilities.",
        "Sail areal densities 1, 10, 100 g/m² and areas 10, 100, 1,000 m² are labeled model values, not materials or flight hardware.",
        "Reflectivity 0.90, emissivity 0.80, sail Cd 2.0, wavelength 1.06 μm, aperture 3 m, zenith optical depth 0.20 are labeled.",
        "Force is F_n = (1+ρ) P_int / c with P_int = P T_atm f_spot cos(i); sail normal is aimed to raise the prograde component (bisector of beam and prograde).",
        "Diffraction: Airy first-minimum radius 1.22 λ L / D, uniform-spot intercept min(1, A_sail/A_spot).",
        "Atmosphere: parent ISA to 86 km; above that, labeled order-of-magnitude thermosphere anchors (100 km 5e-7, 120 km 2e-8, 150 km 2e-9, 200 km 2.5e-10 kg/m³) with log interpolation. Not a standard-atmosphere certificate.",
        "One ground site: the geography site under the evac-tube mouth (vehicle starts nearly overhead at 80 km). A laser at a sea-level tube entrance hundreds of km up-track would already be near the horizon at exit and is not the baseline.",
        "Best azimuth is used (redstone finding: a subtraction-mode comparator never beat best azimuth).",
        "Chassis: 6.56 kg hollow-bone structure after jettisoning the 6.0 kg requested payload from the 12.56 kg dart. Staged chassis applies the same ratio to the remaining 18.84 kg.",
        "No invented vendor, facility, or citation numbers.",
    ]

    payload = {
        "status": "Speculative modeling only. Not an engineering design, flight plan, or siting recommendation.",
        "prepared": "2026-11-27 America/Denver",
        "constants": {
            "c_m_s": C_LIGHT, "V_circ_200km_m_s": G.V_CIRC_200KM,
            "lambda_m": LAMBDA_M, "aperture_m": APERTURE_M,
            "tau_zenith": TAU_ZENITH, "rho_sail": RHO_SAIL, "eps_sail": EPS_SAIL,
            "Cd_sail": CD_SAIL, "rho_anchors_m": RHO_ANCHORS_M, "peek_degrade_K": 803.0,
        },
        "masses": masses,
        "unboosted": unboosted,
        "releases": releases,
        "sweep": rows,
        "immediate_unfold_kourou": immediate,
        "azimuth_compare_kourou_10GW": az_compare,
        "no_track": no_track,
        "series": series,
        "summary": summary,
        "polarity": polarity,
        "recombine": recombine,
        "levy_total": levy.total,
        "transcriber_n": len(transcriber.chronicles),
        "nexus_n": len(nexus.registry),
        "assumptions": assumptions,
        "rho_check": {f"h_{int(h/1000)}km": rho_at(h)
                      for h in (80000, 86000, 100000, 120000, 150000, 200000)},
    }
    path = OUT / "light_sail_push.json"
    path.write_text(json.dumps(payload, default=_json_default))
    print("Wrote", path, "sweep", len(rows), "locks", len(locks), "levy", levy.total)
    return payload


def _plabel(P):
    if P >= 1e9:
        return f"{P/1e9:.0f} GW" if P >= 1e10 or abs(P/1e9 - int(P/1e9)) < 1e-9 else f"{P/1e9:g} GW"
    if P >= 1e6:
        return f"{P/1e6:.0f} MW"
    return f"{P:g} W"


def _json_default(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


def _sample_series(h0, v0, g0, mass, area, P, elev, omega, dart_area, dart_cd, dt=0.2, t_max=250.0):
    """Elevation, thrust, drag, altitude vs time for the figure."""
    Rs = RE + max(0.0, elev)
    r0 = RE + h0
    pos = np.array([0.0, r0])
    gam = math.radians(g0)
    rhat = np.array([0.0, 1.0])
    that = np.array([1.0, 0.0])
    vel = (v0 * math.sin(gam)) * rhat + (v0 * math.cos(gam)) * that
    unfolded = False
    t = 0.0
    out = []
    while t < t_max:
        r = float(np.linalg.norm(pos))
        if r <= RE:
            break
        h = r - RE
        speed = float(np.linalg.norm(vel))
        ang = omega * t
        spos = np.array([Rs * math.sin(ang), Rs * math.cos(ang)])
        el, L = los_elevation_and_range(pos, spos)
        rho_a = rho_at(h)
        F, diag = photon_force_vector(pos, spos, vel, P, area, RHO_SAIL, face="beam")
        drag = 0.5 * rho_a * speed * speed * CD_SAIL * area
        if (not unfolded) and diag["F_N"] >= drag and diag["F_N"] > 0:
            unfolded = True
        acc = -MU * pos / (r ** 3)
        F2, d2 = (np.zeros(2), diag)
        if unfolded and el > 0:
            F2, d2 = photon_force_vector(pos, spos, vel, P, area, RHO_SAIL, face="prograde_tilt")
            acc = acc + F2 / mass
        if speed > 1e-6:
            A_d = area if unfolded else dart_area
            cd = CD_SAIL if unfolded else dart_cd
            Fd = 0.5 * rho_a * speed * speed * cd * A_d
            acc = acc - (Fd / mass) * (vel / speed)
        else:
            Fd = 0.0
        vel = vel + acc * dt
        pos = pos + vel * dt
        t += dt
        out.append({
            "t": t, "h_km": h / 1000.0, "el_deg": math.degrees(el),
            "F_N": d2["F_N"], "drag_N": Fd if unfolded else 0.5 * rho_a * speed * speed * CD_SAIL * area,
            "v": float(np.linalg.norm(vel)), "unfolded": unfolded,
        })
        if el <= 0 and t > 5:
            break
    return {"points": out, "unfolded": unfolded}


def make_figure(payload):
    fig, axes = plt.subplots(2, 2, figsize=(11.2, 9.2))
    fig.suptitle("Light-sail push after the evac-tube exit  (speculative modeling only)",
                 fontsize=11, color="#1f3a5f")
    nice = {"tilt0_333": "0° 80 km", "evac_dart_407": "5° evac dart",
            "tilt5_431": "5° tilt", "staged_256": "staged (true 1,148)"}
    colors = {"tilt0_333": "#1f3a5f", "evac_dart_407": "#2a7d4f",
              "tilt5_431": "#6b4c9a", "staged_256": "#b85c38"}

    # A: residual vs power, Kourou, 100 m², 10 g/m², smart, best az
    ax = axes[0, 0]
    for key, col in colors.items():
        sub = [r for r in payload["sweep"]
               if r["config"] == key and r["site_id"] == "kourou"
               and r["area_m2"] == 100.0 and abs(r["sigma_kg_m2"] - 0.01) < 1e-12]
        sub.sort(key=lambda r: r["P_W"])
        if not sub:
            continue
        ax.semilogx([r["P_W"]/1e6 for r in sub],
                    [r["residual_after_m_s"] for r in sub],
                    "o-", color=col, ms=4, label=nice[key])
        ax.axhline(sub[0]["residual_before_m_s"], color=col, ls="--", lw=0.7, alpha=0.6)
    ax.set_xlabel("laser power (MW, log)")
    ax.set_ylabel("two-burn residual after push (m/s)")
    ax.set_title("A.  Residual after push, Kourou, 100 m², 10 g/m²")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0.8, 1.5e5)

    # B: elevation window + drag vs thrust, 5° evac at 10 GW
    ax = axes[0, 1]
    ser = payload["series"].get("evac_dart_407", {})
    pts = ser.get("points") or []
    if pts:
        t = [p["t"] for p in pts]
        ax.plot(t, [p["el_deg"] for p in pts], color="#1f3a5f", label="elevation (°)")
        ax.set_ylabel("elevation from site (°)", color="#1f3a5f")
        ax2 = ax.twinx()
        ax2.semilogy(t, [max(p["F_N"], 1e-2) for p in pts], color="#2a7d4f", label="photon force (N)")
        ax2.semilogy(t, [max(p["drag_N"], 1e-2) for p in pts], color="#b85c38", ls="--", label="sail drag if open (N)")
        ax2.set_ylabel("force (N, log)")
        ax2.set_ylim(0.05, 2e5)
        # combined legend
        h1, l1 = ax.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        ax.legend(h1 + h2, l1 + l2, fontsize=6.5, loc="upper right")
        unf = next((p["t"] for p in pts if p["unfolded"]), None)
        if unf:
            ax.axvline(unf, color="#888", ls=":", lw=0.8)
    ax.set_xlabel("time after exit (s)")
    ax.set_title("B.  Elevation and forces, 5° evac dart, 10 GW, 100 m²")
    ax.grid(True, alpha=0.3)

    # C: perigee after push vs power, same cut
    ax = axes[1, 0]
    ax.axhline(200, color="k", ls=":", lw=0.8, label="200 km lock floor")
    ax.axhline(100, color="k", ls="--", lw=0.7, label="Karman 100 km")
    for key, col in colors.items():
        sub = [r for r in payload["sweep"]
               if r["config"] == key and r["site_id"] == "kourou"
               and r["area_m2"] == 100.0 and abs(r["sigma_kg_m2"] - 0.01) < 1e-12]
        sub.sort(key=lambda r: r["P_W"])
        if not sub:
            continue
        ax.semilogx([r["P_W"]/1e6 for r in sub],
                    [r["perigee_after_km"] for r in sub],
                    "s-", color=col, ms=4, label=nice[key])
    ax.set_xlabel("laser power (MW, log)")
    ax.set_ylabel("perigee after push (km)")
    ax.set_title("C.  Perigee after the window (same cut as A)")
    ax.legend(fontsize=6.5, loc="lower right")
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0.8, 1.5e5)

    # D: peak Teq vs power for three areas, evac dart Kourou 10 g/m²
    ax = axes[1, 1]
    area_col = {10.0: "#1f3a5f", 100.0: "#2a7d4f", 1000.0: "#b85c38"}
    for area, col in area_col.items():
        sub = [r for r in payload["sweep"]
               if r["config"] == "evac_dart_407" and r["site_id"] == "kourou"
               and r["area_m2"] == area and abs(r["sigma_kg_m2"] - 0.01) < 1e-12]
        sub.sort(key=lambda r: r["P_W"])
        if not sub:
            continue
        ax.semilogx([r["P_W"]/1e6 for r in sub],
                    [r["peak_Teq_K"] for r in sub],
                    "o-", color=col, ms=4, label=f"{int(area)} m²")
    ax.axhline(803, color="#8a1f1f", ls="--", lw=0.9, label="PEEK degrade ~803 K (parent band)")
    ax.set_xlabel("laser power (MW, log)")
    ax.set_ylabel("peak radiation-equilibrium T (K)")
    ax.set_title("D.  Sail heating, 5° evac dart, Kourou, 10 g/m²")
    ax.legend(fontsize=6.5, loc="upper left")
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0.8, 1.5e5)

    fig.tight_layout(rect=[0, 0.01, 1, 0.94], w_pad=2.0, h_pad=1.6)
    path = OUT / "fig12_light_sail_push.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    print("Wrote", path)
    return str(path)


if __name__ == "__main__":
    payload = run()
    make_figure(payload)
