#!/usr/bin/env python3
# CONJUNCTIVE (audit 2026-11-27): one loop Genesis -> Nexus -> Oasis admission -> PrinciplesGate
# -> NaCl consensus -> Dictator -> Transcriber -> Levy -> damped deterministic recombine.
# Speculative modeling only. No engineering, flight, siting or operational claims.
"""Redstone repeater + comparator, and a no-track pad ascent, on recycled exits.

Speculative modeling only. Not an engineering design, flight plan, or siting
recommendation. No operational claims.

The leftover Δv to a 200 km circular is treated as signal strength short of
locking orbit. Earth-rotation / site boost is the side pulse that can stretch
the ellipse if it is added in-track when the main pulse is not already close.

Repeater: a late two-burn (or partial) near apogee / the 200 km apsis, paid
for with the rocket equation from the vehicle's own mass. Not free Δv.

Comparator (subtraction mode): Earth rotation cannot be switched off. 'Suppress'
is modeled only with in-model levers — launch azimuth, and Oasis / PrinciplesGate
admission of a site for a due-east corridor. The gate admits a due-east
(in-track) boost only when the unboosted residual is already <= a swept
threshold T; otherwise the azimuth is set so rotation is nearly out of plane.

No-track: the magnetic / coaster rail is removed. The vehicle starts at rest
relative to the pad (inertial speed is only Earth rotation if due-east is
admitted) and must burn from its own propellant budget.

Components are run in one loop: Genesis → Nexus register → Oasis admission
→ PrinciplesGate → NaCl consensus → Dictator → Transcriber → Levy → damped
deterministic recombine. The Math.random stub in oroboro-core.js is not used.
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_goal_seek_recycle as G
import run_geography_addendum as GEO

sys.path.insert(0, os.environ.get("OASIS_BRIDGE", "/workspace/oasis-build/SkyAriOasis/Bridge"))  # Oasis bridge (sky-ari-ai build) on the project computer
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "consciousness-mapping"))  # this repo
import oasis_core as core  # noqa: E402
import nacl_polarity_mesh as nacl  # noqa: E402

OUT = G.OUT
MU, RE, G_STD = G.MU_EARTH, G.R_EARTH, G.G_STD
KARMAN = G.KARMAN_M
LEO = G.LEO_ALT_M
ISP_300, ISP_450 = G.ISP_STORABLE, G.ISP_LH2

# Recycled labeled mass fractions
FP_FILAMENT = G.FILAMENT_BUDGET_FRAC   # 0.05, previously a heat-regrowth budget
FP_PAYLOAD = 0.30                      # labeled payload fraction on the hollow-bone search
FP_OPTIMISTIC = G.FP_STAGE             # 0.85, optimistic staged-stack fraction

LEVY = {
    "genesis": 0, "admit_boost": 1, "suppress_boost": 2, "repeater_burn": 4,
    "orbit_lock": 14, "fail": 2, "no_track_ascent": 7, "damper_reconcile": 4,
}

# Operator-chosen non-zero lab coordinate, same role as Goldilocks AdaptOrDie.
# Real sites use (lat, lon, elev_km) but never (0,0,0).
LAB_POS = {"x": 2.0, "y": 1.0, "z": -2.0}


# ----- recycled orbital helpers -----

def fp_for_dv(dv, isp):
    if dv <= 0:
        return 0.0
    return 1.0 - math.exp(-dv / (isp * G_STD))


def dv_from_fp(fp, isp):
    return G.stage_dv(isp, fp) if 0.0 < fp < 1.0 else 0.0


def residual_of(h_apo, v_apo):
    if h_apo is None or v_apo is None or h_apo < 0:
        return None
    vac = G.vacuum_transfer_residual(h_apo, v_apo)
    return None if vac is None else vac


def kepler_vac(h, v, gamma_deg):
    kep = GEO.kepler_from_state(h, v, gamma_deg)
    vac = None
    if kep.get("h_apogee_m") is not None and kep.get("v_at_apogee_m_s") is not None:
        vac = residual_of(kep["h_apogee_m"], kep["v_at_apogee_m_s"])
    return kep, (None if vac is None else vac[0]), vac


def apply_horizontal_dv_at_apogee(h_apo, v_apo, dv):
    """Prograde (or retrograde if dv<0) impulsive burn at apogee, gamma=0."""
    v2 = max(0.0, v_apo + dv)
    return GEO.kepler_from_state(h_apo, v2, 0.0)


def apply_repeater(h_apo, v_apo, dv_budget):
    """Spend up to dv_budget on the parent two-burn to 200 km circular, apogee first.

    If the budget covers |dv1|+dv2, the two burns complete, residual is 0, and
    perigee is 200 km. Otherwise dv1 is applied as far as the budget allows,
    then any remainder toward dv2 (which would be done at the 200 km apsis).
    """
    vac = residual_of(h_apo, v_apo)
    if vac is None:
        return {"applied_dv1_m_s": 0.0, "applied_dv2_m_s": 0.0, "residual_after_m_s": None,
                "kepler_after": None, "locked": False, "reason": "no_apogee_state",
                "needed_m_s": None}
    needed, dv1, dv2 = vac
    budget = max(0.0, float(dv_budget))
    if budget >= needed - 1e-9:
        # Complete transfer: circular 200 km.
        kep = {
            "bound": True, "ecc": 0.0, "a_m": RE + LEO,
            "h_apogee_m": float(LEO), "h_perigee_m": float(LEO),
            "v_at_apogee_m_s": G.v_circ(LEO),
            "v_circ_apogee_m_s": G.v_circ(LEO),
            "dv_circularize_at_apogee_m_s": 0.0,
        }
        return {"applied_dv1_m_s": dv1, "applied_dv2_m_s": dv2 if dv1 >= 0 else -dv2 if False else (needed - abs(dv1)) * (1 if dv2 >= 0 else 1),
                "applied_abs_m_s": needed, "residual_after_m_s": 0.0,
                "kepler_after": kep, "locked": True,
                "reason": "two_burn_complete", "needed_m_s": needed, "dv1": dv1, "dv2": dv2}

    # Partial: apply as much of dv1 as possible (signed), then remainder of dv2.
    if budget >= abs(dv1):
        # Full dv1: perigee should now be 200 km (transfer ellipse). Residual is dv2 - leftover.
        leftover = budget - abs(dv1)
        applied_dv1 = dv1  # signed
        kep = apply_horizontal_dv_at_apogee(h_apo, v_apo, applied_dv1)
        residual = max(0.0, dv2 - leftover)
        # If leftover>0 it would be spent at the 200 km apsis; peri is already ~200 km.
        locked = residual <= 1.0 and (kep.get("h_perigee_m") or -1) >= KARMAN
        # After full dv1, peri should be LEO; leftover reduces circularization need.
        return {"applied_dv1_m_s": applied_dv1, "applied_dv2_m_s": leftover,
                "applied_abs_m_s": budget, "residual_after_m_s": residual,
                "kepler_after": kep, "locked": locked,
                "reason": "dv1_complete_partial_dv2", "needed_m_s": needed, "dv1": dv1, "dv2": dv2}

    applied_dv1 = math.copysign(budget, dv1) if dv1 != 0 else 0.0
    kep = apply_horizontal_dv_at_apogee(h_apo, v_apo, applied_dv1)
    vac2 = None
    res = None
    if kep.get("h_apogee_m") is not None and kep.get("v_at_apogee_m_s") is not None:
        vac2 = residual_of(kep["h_apogee_m"], kep["v_at_apogee_m_s"])
        res = vac2[0] if vac2 else None
    peri = kep.get("h_perigee_m")
    locked = bool(res is not None and res <= 1.0 and peri is not None and peri >= KARMAN)
    return {"applied_dv1_m_s": applied_dv1, "applied_dv2_m_s": 0.0,
            "applied_abs_m_s": budget, "residual_after_m_s": res,
            "kepler_after": kep, "locked": locked,
            "reason": "partial_dv1", "needed_m_s": needed, "dv1": dv1, "dv2": dv2}


def release_with_azimuth(v_rel, gamma_deg, h_m, lat_deg, az_deg):
    """Combine relative exit with Earth rotation at a launch azimuth (0=N, 90=E)."""
    boost = GEO.v_rot_at_altitude(lat_deg, h_m)
    gam = math.radians(gamma_deg)
    az = math.radians(az_deg)
    vh = v_rel * math.cos(gam)
    vr = v_rel * math.sin(gam)
    v_east = vh * math.sin(az) + boost
    v_north = vh * math.cos(az)
    v_h_i = math.hypot(v_east, v_north)
    v_i = math.hypot(v_h_i, vr)
    g_i = math.degrees(math.atan2(vr, v_h_i)) if v_h_i > 0 or vr != 0 else 0.0
    return v_i, g_i, boost, v_h_i, vr


def suppress_azimuth(v_rel, gamma_deg, h_m, lat_deg, step=2.0):
    """Azimuth that makes inertial horizontal speed closest to the unboosted v_h.

    That is the in-model 'suppress the side pulse' lever: rotation is nearly
    out of the trajectory plane, so it does not add in-track speed. Earth
    rotation itself is not switched off.
    """
    gam = math.radians(gamma_deg)
    vh = v_rel * math.cos(gam)
    best = None
    for az in np.arange(0.0, 360.0, step):
        v_i, g_i, boost, v_h_i, vr = release_with_azimuth(v_rel, gamma_deg, h_m, lat_deg, az)
        err = abs(v_h_i - vh)
        if best is None or err < best["err"]:
            best = {"az_deg": float(az), "err": err, "v_i": v_i, "g_i": g_i,
                    "boost": boost, "v_h_i": v_h_i, "vr": vr}
    return best


def best_azimuth(v_rel, gamma_deg, h_m, lat_deg, step=5.0):
    """Azimuth that minimizes the two-burn residual to 200 km circular (Kepler)."""
    best = None
    for az in np.arange(0.0, 360.0, step):
        v_i, g_i, boost, v_h_i, vr = release_with_azimuth(v_rel, gamma_deg, h_m, lat_deg, az)
        kep, res, vac = kepler_vac(h_m, v_i, g_i)
        if res is None:
            continue
        apo = kep.get("h_apogee_m")
        peri = kep.get("h_perigee_m")
        rec = {"az_deg": float(az), "residual_m_s": res, "v_i": v_i, "g_i": g_i,
               "boost": boost, "v_h_i": v_h_i, "kep": kep,
               "apogee_km": None if apo is None else apo / 1000.0,
               "perigee_km": None if peri is None else peri / 1000.0,
               "reached_karman": (apo or 0) >= KARMAN}
        if best is None or res < best["residual_m_s"] - 1e-9 or (
            abs(res - best["residual_m_s"]) < 1e-9 and rec["reached_karman"] and not best["reached_karman"]
        ):
            best = rec
    return best


def staged_relative_state(cfg):
    """Apply the already-flown horizontal stage to the rail exit, if present."""
    v, g, h = cfg["v_m_s"], cfg["gamma_deg"], cfg["h_m"]
    mass = cfg["mass"]
    if cfg.get("staged"):
        ang = math.radians(g)
        v, ang = G.apply_dv(v, ang, cfg["stage_dv_m_s"], cfg.get("stage_mode") or "horizontal")
        g = math.degrees(ang)
        fp = cfg.get("fp") if cfg.get("fp") is not None else FP_OPTIMISTIC
        mass = mass * (1.0 - fp)
    return v, g, h, mass


# ----- conjunctive Oroboro loop -----

class Nexus:
    def __init__(self):
        self.registry = {}
        self.archive = []
        self.metrics = {"deltas": 0, "reconciliations": 0, "isolations": 0}

    def register(self, key, data):
        self.registry[key] = data
        self.archive.append({"type": "register", "id": key})


class Transcriber:
    def __init__(self):
        self.chronicles = []
        self.anonymous = []

    def ingest(self, text, source="dictator", kind=None):
        entry = {"text": text, "source": source, "kind": kind,
                 "critical": kind in ("fail", "orbit_lock")}
        self.chronicles.append(entry)
        if entry["critical"]:
            self.anonymous.append(entry)
        return entry


class Dictator:
    def __init__(self, transcriber):
        self.transcriber = transcriber
        self.active = True

    def stream(self, kind, text):
        if not self.active:
            return None
        return self.transcriber.ingest(text, "dictator", kind)


class Levy:
    def __init__(self, transcriber):
        self.transcriber = transcriber
        self.total = 0.0
        self.entries = []
        self.ema = None

    def assess(self, kind, n=1):
        w = LEVY.get(kind, 1) * n
        self.total += w
        rec = {"kind": kind, "weight": w}
        self.entries.append(rec)
        return w


class RelationalSim:
    def __init__(self, nexus):
        self.nexus = nexus

    def recombine(self, residuals, damping=0.25):
        xs = np.array([r for r in residuals if r is not None], dtype=float)
        if len(xs) == 0:
            return {"residual": 0.0, "matchedWholeSystem": True, "n": 0}
        # Normalize by circular speed so the 0.2 match threshold stays the
        # same scale as the Goldilocks damper study (dimensionless).
        norm = xs / G.V_CIRC_200KM
        spread = float(np.sqrt(np.mean(norm ** 2)))
        residual = spread * (1.0 - max(0.0, min(1.0, damping)))
        self.nexus.metrics["reconciliations"] += 1
        self.nexus.metrics["deltas"] += len(xs)
        return {"n": int(len(xs)), "spread": spread, "residual": residual,
                "damping": damping, "matchedWholeSystem": residual < 0.2,
                "mean_residual_m_s": float(xs.mean()),
                "max_residual_m_s": float(xs.max())}


def site_position(site):
    """Non-zero AdaptOrDie coordinate for a real site; None for the 0° reference."""
    if site.get("id") == "equator_ref" or (site.get("lat") == 0.0 and site.get("lon") == 0.0
                                           and (site.get("elev_m") or 0) == 0.0
                                           and site.get("kind") == "reference"):
        return None
    # meters-as-units is not required; a non-zero triple is.
    return {"x": float(site["lat"]), "y": float(site["lon"]) if site.get("lon") not in (0, 0.0) or site["lat"] != 0
            else 0.001, "z": float(site.get("elev_m") or 1.0) / 1000.0 or 0.001}


def principles_allow_site(gate, site):
    pos_d = site_position(site)
    pos = core.vec(pos_d) if pos_d else None
    text = f"Admit site {site.get('name')} at lat {site.get('lat')}"
    gr = gate.check("CreateAnchor", pos, text, utility=0.65)
    return gr, pos_d


# ----- no-track powered ascent -----

def powered_ascent(h0, m0, fp, isp, area, cd,
                   tw0=3.0, kick_deg=5.0, tower_m=100.0,
                   dt=0.05, t_max=1500.0, reserve_fp=0.0):
    """Constant-thrust pitch program from the pad in the co-rotating / air-rest frame.

    The vehicle starts at rest relative to the pad and the atmosphere (zero airspeed).
    Earth rotation is not used as an initial airspeed — the air co-rotates with the
    pad. Rotation is added to the inertial state at burnout by the caller, the same
    way the geography layer adds a due-east boost to a recycled exit.

    After a 100 m vertical rise, pitch goes from (90 - kick)° to 5° over the 40 km
    flatten characteristic recycled from the goal-seek continuation. Thrust is never
    pointed below the local horizontal during the burn. reserve_fp is held for a
    later repeater.
    """
    fp_ascent = max(0.0, min(0.95, fp - reserve_fp))
    if fp_ascent <= 0 or m0 <= 0:
        return {"ok": False, "reason": "no_ascent_propellant", "h_max_m": h0, "residual_m_s": None}
    T = tw0 * m0 * G_STD
    ve = isp * G_STD
    mdot = T / ve
    m_prop = fp_ascent * m0
    m = m0
    r0 = RE + max(0.0, h0)
    x, y = 0.0, r0
    vx, vy = 0.0, 0.0
    t = 0.0
    h_max = max(0.0, h0)
    peak_q = peak_qsg = peak_Teq = 0.0
    t_burn_end = None
    g_loss = 0.0
    d_loss = 0.0
    burned = 0.0
    burnout = None
    apogee = None
    while t < t_max:
        r = math.hypot(x, y)
        if r < 1.0:
            break
        h = r - RE
        if h < -10.0 and t > 1.0:
            break
        rho = G.rho_isa(max(0.0, h))
        speed = math.hypot(vx, vy)
        q = 0.5 * rho * speed * speed
        qsg = G.sutton_graves_q(rho, speed)
        Teq = G.T_eq_radiation(qsg)
        peak_q = max(peak_q, q)
        peak_qsg = max(peak_qsg, qsg)
        peak_Teq = max(peak_Teq, Teq)
        g = MU / (r * r)
        gx, gy = -g * x / r, -g * y / r
        dx = dy = 0.0
        if speed > 1e-6 and m > 0:
            Fd = 0.5 * cd * rho * area * speed * speed
            dx, dy = -Fd / m * vx / speed, -Fd / m * vy / speed
            d_loss += (Fd / m) * dt
        tx = ty = 0.0
        thrusting = burned < m_prop - 1e-12
        urx, ury = x / r, y / r
        uhx, uhy = ury, -urx
        if thrusting:
            if h - h0 < tower_m:
                pitch = math.pi / 2.0
            else:
                frac = min(1.0, max(0.0, (h - h0 - tower_m) / 40_000.0))
                pitch = math.radians(90.0 - kick_deg) * (1.0 - frac) + math.radians(5.0) * frac
            tdirx = urx * math.sin(pitch) + uhx * math.cos(pitch)
            tdiry = ury * math.sin(pitch) + uhy * math.cos(pitch)
            # Never thrust below the local horizontal.
            if tdirx * urx + tdiry * ury < 0:
                tdirx, tdiry = uhx, uhy
            tx, ty = (T / m) * tdirx, (T / m) * tdiry
            if speed > 1e-6:
                g_along = -(gx * vx + gy * vy) / speed
                g_loss += max(0.0, g_along) * dt
            dm = min(mdot * dt, m_prop - burned)
            m -= dm
            burned += dm
            if burned >= m_prop - 1e-12 and t_burn_end is None:
                t_burn_end = t
                vr = vx * urx + vy * ury
                vt = vx * uhx + vy * uhy
                burnout = {
                    "t_s": t, "h_m": h, "v_m_s": speed,
                    "gamma_deg": math.degrees(math.atan2(vr, vt)) if (abs(vt) > 1e-9 or abs(vr) > 1e-9) else 0.0,
                    "mass_kg": m,
                }
        ax, ay = gx + dx + tx, gy + dy + ty
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt
        t += dt
        r2 = math.hypot(x, y)
        h2 = r2 - RE
        if h2 > h_max:
            h_max = h2
            ur2x, ur2y = x / r2, y / r2
            uh2x, uh2y = ur2y, -ur2x
            speed2 = math.hypot(vx, vy)
            vr2 = vx * ur2x + vy * ur2y
            vt2 = vx * uh2x + vy * uh2y
            apogee = {
                "t_s": t, "h_m": h2, "v_m_s": speed2,
                "gamma_deg": math.degrees(math.atan2(vr2, vt2)) if (abs(vt2) > 1e-9 or abs(vr2) > 1e-9) else 0.0,
            }
        if (not thrusting) and h2 < 0 and t > 1.0:
            break
    if burnout is None and burned > 0:
        r = math.hypot(x, y)
        h = r - RE
        urx, ury = x / r, y / r
        uhx, uhy = ury, -urx
        speed = math.hypot(vx, vy)
        vr = vx * urx + vy * ury
        vt = vx * uhx + vy * uhy
        burnout = {
            "t_s": t, "h_m": h, "v_m_s": speed,
            "gamma_deg": math.degrees(math.atan2(vr, vt)) if (abs(vt) > 1e-9 or abs(vr) > 1e-9) else 0.0,
            "mass_kg": m,
        }
    # Kepler / residual are computed by the caller after adding Earth rotation
    # to the burnout state (co-rotating air during the burn, inertial at cutoff).
    return {
        "ok": True,
        "h_max_m": h_max,
        "burnout": burnout,
        "apogee": apogee,
        "t_s": t, "t_burn_s": t_burn_end if t_burn_end is not None else t,
        "mass_end_kg": m, "burned_kg": burned, "fp_ascent": fp_ascent,
        "tw0": tw0, "isp_s": isp, "peak_q_pa": peak_q,
        "peak_sutton_graves_W_m2": peak_qsg, "peak_Teq_K": peak_Teq,
        "gravity_loss_m_s": g_loss, "drag_loss_m_s": d_loss,
        "reached_karman": h_max >= KARMAN, "reached_200km": h_max >= LEO,
        "reserve_fp": reserve_fp,
    }



def load_configs():
    geo = json.loads((OUT / "geography.json").read_text())
    # Hollow-bone dart mass for the 17,000 mph / 80 km no-stage exits (recycled).
    dart = G.vehicle_from_mass(20.0, hollow_k=0.8, payload_frac=FP_PAYLOAD)
    cfgs = {}
    for key in ("evac_dart_407", "tilt5_431", "tilt0_333", "staged_256"):
        raw = geo["configs"][key]
        c = dict(raw["cfg"])
        if key != "staged_256":
            c["mass"] = dart["mass"]
            c["cd"] = dart["cd"]
            c["area"] = dart["area"]
            c["mass_note"] = "12.56 kg hollow-bone dart (k=0.8, payload_frac=0.30 on a 20 kg request), recycled."
        else:
            c["mass_note"] = "125.6 kg hollow-scaled vehicle; f_p=0.85 already spent on the first stage."
        c["key"] = key
        c["baseline_kepler"] = raw["baseline_recomputed"]
        cfgs[key] = c
    return cfgs, geo["sites"], dart


def evaluate_release(cfg, site, az_deg):
    v, g, h, mass = staged_relative_state(cfg)
    v_i, g_i, boost, v_h_i, vr = release_with_azimuth(v, g, h, site["lat"], az_deg)
    kep, res, vac = kepler_vac(h, v_i, g_i)
    return {
        "v_rel_m_s": v, "gamma_rel_deg": g, "h_m": h, "mass_kg": mass,
        "az_deg": az_deg, "boost_m_s": boost,
        "v_inertial_m_s": v_i, "gamma_inertial_deg": g_i, "v_h_inertial_m_s": v_h_i,
        "kepler": kep, "residual_m_s": res, "vac": vac,
        "apogee_km": None if not kep.get("h_apogee_m") else kep["h_apogee_m"] / 1000.0,
        "perigee_km": None if not kep.get("h_perigee_m") else kep["h_perigee_m"] / 1000.0,
        "reached_karman": (kep.get("h_apogee_m") or 0) >= KARMAN,
    }


def run():
    cfgs, sites, dart = load_configs()
    gate = core.PrinciplesGate(core.load_config())
    nexus = Nexus()
    transcriber = Transcriber()
    dictator = Dictator(transcriber)
    levy = Levy(transcriber)
    sim = RelationalSim(nexus)
    nexus.register("genesis", {"tag": "I am the OG avatar", "weight": math.inf})
    levy.assess("genesis")
    dictator.stream("genesis", "Redstone repeater/comparator ledger. Recycled exits; new burns and azimuth gates only.")

    # Unboosted residuals (recycled, az-independent). Confirm against geography baseline.
    unboosted = {}
    for key, cfg in cfgs.items():
        v, g, h, mass = staged_relative_state(cfg)
        kep, res, vac = kepler_vac(h, v, g)
        unboosted[key] = {
            "residual_m_s": res, "kepler": kep,
            "apogee_km": None if not kep.get("h_apogee_m") else kep["h_apogee_m"] / 1000.0,
            "perigee_km": None if not kep.get("h_perigee_m") else kep["h_perigee_m"] / 1000.0,
            "mass_at_release_kg": mass,
            "v_rel_m_s": v, "gamma_deg": g, "h_m": h,
        }
        nexus.register(f"unboosted:{key}", unboosted[key])

    # Budget table: what Δv each recycled fraction buys, and what fraction each leftover needs.
    isp_list = [ISP_300, ISP_450]
    fp_list = [FP_FILAMENT, FP_PAYLOAD, FP_OPTIMISTIC]
    budget = {
        "fp_filament": FP_FILAMENT, "fp_payload": FP_PAYLOAD, "fp_optimistic": FP_OPTIMISTIC,
        "dv_by_fp_isp": {f"isp_{int(isp)}": {f"fp_{fp:.2f}": dv_from_fp(fp, isp) for fp in fp_list}
                         for isp in isp_list},
        "fp_needed": {},
    }
    for key, u in unboosted.items():
        budget["fp_needed"][key] = {
            "residual_m_s": u["residual_m_s"],
            "fp_at_300s": fp_for_dv(u["residual_m_s"] or 0, ISP_300),
            "fp_at_450s": fp_for_dv(u["residual_m_s"] or 0, ISP_450),
        }

    # Site-level: due-east, suppress-az, best-az, then repeater at 450 s under each budget.
    site_rows = []
    THRESHOLDS = [50, 100, 200, 250, 300, 333, 350, 400, 450, 500, 800, 1200, 2000]
    # Precompute azimuth policies per (config, site)
    policies = {}
    for key, cfg in cfgs.items():
        v, g, h, mass = staged_relative_state(cfg)
        for site in sites:
            east = evaluate_release(cfg, site, 90.0)
            sup = suppress_azimuth(v, g, h, site["lat"], step=2.0)
            sup_eval = evaluate_release(cfg, site, sup["az_deg"])
            best = best_azimuth(v, g, h, site["lat"], step=5.0)
            gr, pos = principles_allow_site(gate, site)
            policies[(key, site["id"])] = {
                "east": east, "suppress": {"az": sup, "eval": sup_eval},
                "best": best, "gate": {"allowed": gr.allowed, "principle": gr.principle,
                                       "explanation": gr.explanation},
            }

    # Comparator sweep + repeater
    comparator_rows = []
    repeater_rows = []
    for key, cfg in cfgs.items():
        u = unboosted[key]
        mass = u["mass_at_release_kg"]  # post-stage if staged
        for site in sites:
            pol = policies[(key, site["id"])]
            # repeater on due-east, suppress, best, and unboosted (no side pulse in-track)
            for policy_name, ev, az in (
                ("unboosted", None, None),
                ("due_east", pol["east"], 90.0),
                ("suppress_az", pol["suppress"]["eval"], pol["suppress"]["az"]["az_deg"]),
                ("best_az", None, pol["best"]["az_deg"] if pol["best"] else None),
            ):
                if policy_name == "unboosted":
                    kep = u["kepler"]; res = u["residual_m_s"]
                    apo, peri = u["apogee_km"], u["perigee_km"]
                    az_used = None
                elif policy_name == "best_az":
                    evb = evaluate_release(cfg, site, pol["best"]["az_deg"])
                    kep, res = evb["kepler"], evb["residual_m_s"]
                    apo, peri = evb["apogee_km"], evb["perigee_km"]
                    az_used = pol["best"]["az_deg"]
                    ev = evb
                else:
                    kep, res = ev["kepler"], ev["residual_m_s"]
                    apo, peri = ev["apogee_km"], ev["perigee_km"]
                    az_used = az
                h_apo = None if apo is None else apo * 1000.0
                v_apo = kep.get("v_at_apogee_m_s") if kep else None
                for isp_name, isp in (("450s", ISP_450), ("300s", ISP_300)):
                    for fp_name, fp in (("filament_0.05", FP_FILAMENT),
                                        ("payload_0.30", FP_PAYLOAD),
                                        ("optimistic_0.85", FP_OPTIMISTIC)):
                        # Staged already spent 0.85 of the *original* stack. Repeater fp is
                        # a fraction of the *remaining* mass (honesty: not a second 0.85 of m0).
                        dv_bud = dv_from_fp(fp, isp)
                        rep = apply_repeater(h_apo, v_apo, dv_bud) if h_apo is not None else {
                            "residual_after_m_s": None, "locked": False, "reason": "no_apogee",
                            "applied_abs_m_s": 0.0, "needed_m_s": res, "kepler_after": None,
                        }
                        ka = rep.get("kepler_after") or {}
                        repeater_rows.append({
                            "config": key, "site_id": site["id"], "site": site["name"],
                            "lat": site["lat"], "policy": policy_name, "az_deg": az_used,
                            "residual_before_m_s": res,
                            "apogee_before_km": apo, "perigee_before_km": peri,
                            "isp_s": isp, "fp": fp, "fp_name": fp_name, "isp_name": isp_name,
                            "dv_budget_m_s": dv_bud,
                            "fp_needed_for_before": fp_for_dv(res or 0, isp),
                            "fits_this_fp": (res or 1e9) <= dv_bud + 1e-6,
                            "residual_after_m_s": rep.get("residual_after_m_s"),
                            "applied_abs_m_s": rep.get("applied_abs_m_s"),
                            "needed_m_s": rep.get("needed_m_s"),
                            "locked": bool(rep.get("locked")),
                            "repeater_reason": rep.get("reason"),
                            "apogee_after_km": None if not ka.get("h_apogee_m") else ka["h_apogee_m"] / 1000.0,
                            "perigee_after_km": None if not ka.get("h_perigee_m") else ka["h_perigee_m"] / 1000.0,
                            "mass_at_release_kg": mass,
                            "principles_allowed": pol["gate"]["allowed"],
                            "principles": pol["gate"]["principle"],
                        })

            # Comparator: admit due-east iff unboosted residual <= T AND PrinciplesGate allows
            # a site coordinate. equator_ref has a zero coordinate and is blocked as a siting
            # admission (still computed as a physics reference).
            for T in THRESHOLDS:
                admit = (u["residual_m_s"] is not None and u["residual_m_s"] <= T
                         and pol["gate"]["allowed"])
                # If the site is blocked, treat as suppress (cannot admit a due-east corridor).
                if admit:
                    ev = pol["east"]; az_used = 90.0; mode = "admit_due_east"
                else:
                    ev = pol["suppress"]["eval"]
                    az_used = pol["suppress"]["az"]["az_deg"]
                    mode = "suppress_az" if pol["gate"]["allowed"] else "gate_blocked_or_above_T"
                comparator_rows.append({
                    "config": key, "site_id": site["id"], "site": site["name"], "lat": site["lat"],
                    "T_m_s": T, "unboosted_residual_m_s": u["residual_m_s"],
                    "admitted": admit, "mode": mode, "az_deg": az_used,
                    "residual_m_s": ev["residual_m_s"],
                    "apogee_km": ev["apogee_km"], "perigee_km": ev["perigee_km"],
                    "reached_karman": ev["reached_karman"],
                    "due_east_residual_m_s": pol["east"]["residual_m_s"],
                    "best_az_residual_m_s": pol["best"]["residual_m_s"] if pol["best"] else None,
                    "best_az_deg": pol["best"]["az_deg"] if pol["best"] else None,
                    "suppress_residual_m_s": pol["suppress"]["eval"]["residual_m_s"],
                    "principles_allowed": pol["gate"]["allowed"],
                })

    # Summaries: does the comparator beat always-due-east? always-best-az? per T
    comparator_summary = []
    for key in cfgs:
        for T in THRESHOLDS:
            sub = [r for r in comparator_rows if r["config"] == key and r["T_m_s"] == T
                   and r["site_id"] != "equator_ref"]
            if not sub:
                continue
            mean_comp = float(np.mean([r["residual_m_s"] for r in sub]))
            mean_east = float(np.mean([r["due_east_residual_m_s"] for r in sub]))
            mean_best = float(np.mean([r["best_az_residual_m_s"] for r in sub]))
            mean_sup = float(np.mean([r["suppress_residual_m_s"] for r in sub]))
            n_admit = int(sum(1 for r in sub if r["admitted"]))
            # count sites where comparator residual < due-east - 1 m/s
            n_better_than_east = int(sum(1 for r in sub if r["residual_m_s"] < r["due_east_residual_m_s"] - 1))
            n_worse_than_east = int(sum(1 for r in sub if r["residual_m_s"] > r["due_east_residual_m_s"] + 1))
            n_better_than_best = int(sum(1 for r in sub if r["residual_m_s"] < r["best_az_residual_m_s"] - 1))
            comparator_summary.append({
                "config": key, "T_m_s": T, "n_sites": len(sub), "n_admitted": n_admit,
                "mean_comparator_m_s": mean_comp, "mean_due_east_m_s": mean_east,
                "mean_best_az_m_s": mean_best, "mean_suppress_m_s": mean_sup,
                "n_better_than_due_east": n_better_than_east,
                "n_worse_than_due_east": n_worse_than_east,
                "n_better_than_best_az": n_better_than_best,
                "beats_due_east_mean": mean_comp < mean_east - 1,
                "beats_best_az_mean": mean_comp < mean_best - 1,
            })

    # ----- no-track -----
    no_track = []
    no_track_sites = [s for s in sites if s["id"] in
                      ("equator_ref", "kourou", "las_vegas", "baikonur", "cape_ksc", "mauna_kea")]
    vehicles = [
        {"name": "hollow_dart_12.6kg", "mass": dart["mass"], "cd": dart["cd"], "area": dart["area"]},
        {"name": "hollow_scaled_125.6kg", "mass": 125.59297999321456, "cd": 0.2,
         "area": 0.027809896729377014},
    ]
    for veh in vehicles:
        for site in no_track_sites:
            for isp_name, isp in (("450s", ISP_450),):
                for fp in (FP_FILAMENT, FP_PAYLOAD, FP_OPTIMISTIC):
                    for tw0 in (3.0, 10.0):
                        for az_policy, admit_east in (("due_east", True), ("suppress_polar", False)):
                            # Principles on site (equator_ref blocked as admission)
                            gr, _ = principles_allow_site(gate, site)
                            use_east = admit_east and gr.allowed
                            # If equator_ref and due_east requested, still compute physics
                            # but mark gate_blocked; physics-only due-east uses rotation anyway
                            # for the reference curve when we explicitly want the physics ref.
                            if site["id"] == "equator_ref" and admit_east:
                                use_east_physics = True
                                gate_ok = False
                            else:
                                use_east_physics = use_east
                                gate_ok = gr.allowed
                            v_rot = GEO.v_rot_at_altitude(site["lat"], site.get("elev_m") or 0.0)
                            az_used = 90.0 if use_east_physics else 0.0  # due-east vs near-polar (rotation out of plane)
                            fp_reserve_500 = fp_for_dv(500.0, isp)
                            for reserve_mode, reserve_fp in (
                                ("all_in_ascent", 0.0),
                                ("reserve_500mps", min(fp * 0.5, fp_reserve_500) if fp >= 0.10 else 0.0),
                            ):
                                if reserve_mode == "reserve_500mps" and reserve_fp <= 0:
                                    continue
                                ascent = powered_ascent(
                                    h0=float(site.get("elev_m") or 0.0),
                                    m0=veh["mass"], fp=fp, isp=isp,
                                    area=veh["area"], cd=veh["cd"],
                                    tw0=tw0, kick_deg=5.0, tower_m=100.0,
                                    reserve_fp=reserve_fp,
                                )
                                bo = ascent.get("burnout") or {}
                                h_bo = bo.get("h_m")
                                v_bo = bo.get("v_m_s")
                                g_bo = bo.get("gamma_deg")
                                # Add Earth rotation in the inertial frame at burnout, not as pad airspeed.
                                if h_bo is not None and v_bo is not None and g_bo is not None and h_bo > 0:
                                    v_i, g_i, boost, v_h_i, vr = release_with_azimuth(
                                        v_bo, g_bo, h_bo, site["lat"], az_used)
                                    kep, res, vac = kepler_vac(h_bo, v_i, g_i)
                                else:
                                    v_i = g_i = boost = None
                                    kep, res, vac = {}, None, None
                                dv_rep = dv_from_fp(reserve_fp, isp) if reserve_fp > 0 else 0.0
                                rep = {"residual_after_m_s": res, "locked": False, "reason": "no_reserve",
                                       "applied_abs_m_s": 0.0, "kepler_after": kep}
                                h_apo = kep.get("h_apogee_m") if kep else None
                                v_apo = kep.get("v_at_apogee_m_s") if kep else None
                                if dv_rep > 0 and h_apo is not None and h_apo >= 0 and v_apo:
                                    rep = apply_repeater(h_apo, v_apo, dv_rep)
                                ka = rep.get("kepler_after") or {}
                                locked = bool(rep.get("locked"))
                                row = {
                                    "vehicle": veh["name"], "site_id": site["id"], "site": site["name"],
                                    "lat": site["lat"], "elev_m": site.get("elev_m") or 0.0,
                                    "isp_s": isp, "fp": fp, "tw0": tw0, "az_policy": az_policy,
                                    "az_deg": az_used, "boost_at_burnout_m_s": boost, "gate_allowed": gate_ok,
                                    "reserve_mode": reserve_mode, "reserve_fp": reserve_fp,
                                    "h_max_km": (ascent.get("h_max_m") or 0) / 1000.0,
                                    "h_burnout_km": None if h_bo is None else h_bo / 1000.0,
                                    "v_burnout_m_s": v_bo, "gamma_burnout_deg": g_bo,
                                    "v_inertial_burnout_m_s": v_i, "gamma_inertial_deg": g_i,
                                    "reached_karman": ascent.get("reached_karman"),
                                    "reached_200km": ascent.get("reached_200km"),
                                    "residual_coast_m_s": res,
                                    "residual_after_repeater_m_s": rep.get("residual_after_m_s"),
                                    "locked": locked,
                                    "repeater_reason": rep.get("reason"),
                                    "apogee_coast_km": None if not kep.get("h_apogee_m") else kep["h_apogee_m"] / 1000.0,
                                    "perigee_coast_km": None if not kep.get("h_perigee_m") else kep["h_perigee_m"] / 1000.0,
                                    "apogee_after_km": None if not ka.get("h_apogee_m") else ka["h_apogee_m"] / 1000.0,
                                    "perigee_after_km": None if not ka.get("h_perigee_m") else ka["h_perigee_m"] / 1000.0,
                                    "peak_q_pa": ascent.get("peak_q_pa"),
                                    "peak_Teq_K": ascent.get("peak_Teq_K"),
                                    "peak_sutton_W_m2": ascent.get("peak_sutton_graves_W_m2"),
                                    "gravity_loss_m_s": ascent.get("gravity_loss_m_s"),
                                    "drag_loss_m_s": ascent.get("drag_loss_m_s"),
                                    "t_burn_s": ascent.get("t_burn_s"),
                                    "bound": bool((kep or {}).get("bound")),
                                    "ideal_ascent_dv_m_s": dv_from_fp(ascent.get("fp_ascent") or 0, isp),
                                    "ideal_repeater_dv_m_s": dv_rep,
                                }
                                no_track.append(row)
                                kind = "orbit_lock" if locked else ("no_track_ascent" if ascent.get("reached_karman") else "fail")
                                levy.assess(kind)
                                dictator.stream(kind, f"no-track {veh['name']} {site['id']} fp={fp} tw={tw0} {az_policy} hmax={row['h_max_km']:.1f} km res={row['residual_coast_m_s']} locked={locked}")

    # Levy / mesh / recombine on the headline leftovers
    # Polarity: leftover +1; due-east boost charge = -1 if it shrinks residual else +1
    signs = {"LeftoverDv": +1, "RepeaterBurn": -1, "DueEastBoost": +1, "BestAzimuth": -1,
             "ComparatorGate": -1, "NoTrackAscent": +1}
    # Set DueEastBoost sign per config from mean residual change
    sign_notes = {}
    for key in cfgs:
        sub = [policies[(key, s["id"])] for s in sites if s["id"] != "equator_ref"]
        east_mean = float(np.mean([p["east"]["residual_m_s"] for p in sub]))
        unb = unboosted[key]["residual_m_s"]
        sign_notes[key] = {"unboosted": unb, "mean_due_east": east_mean,
                           "due_east_shrinks": east_mean < unb - 1}
    # Global: due-east shrinks on no-stage, inflates staged
    edges = [
        ("RepeaterBurn", "LeftoverDv"),
        ("DueEastBoost", "LeftoverDv"),
        ("BestAzimuth", "LeftoverDv"),
        ("ComparatorGate", "LeftoverDv"),
        ("NoTrackAscent", "LeftoverDv"),
        ("RepeaterBurn", "DueEastBoost"),
        ("ComparatorGate", "DueEastBoost"),
        ("ComparatorGate", "BestAzimuth"),
    ]
    # Charge DueEastBoost +1 (same side as leftover) because it can stretch;
    # BestAzimuth -1 (can lock complementary). These are labeled interpretations.
    mesh = nacl.Mesh(list(signs), [nacl.Edge(a, b, signs[a], signs[b]) for a, b in edges])
    mesh.process_polarities()
    mesh.apply_levy()
    locked_e = [(e.node_a, e.node_b) for e in mesh.edges if e.locked]
    open_e = [(e.node_a, e.node_b) for e in mesh.edges if not e.locked]
    mesh.flip_all(); mesh.re_stabilize()
    inv = [(e.node_a, e.node_b) for e in mesh.edges if e.locked] == locked_e

    # Recombine a compact leftover list (due-east residuals, after-repeater payload 450s)
    rec_before, rec_after_fil, rec_after_pay = [], [], []
    for key in cfgs:
        rec_before.append(unboosted[key]["residual_m_s"])
        # mean due-east after payload and filament repeater, real sites
        for fp_name, bucket in (("filament_0.05", rec_after_fil), ("payload_0.30", rec_after_pay)):
            xs = [r["residual_after_m_s"] for r in repeater_rows
                  if r["config"] == key and r["policy"] == "due_east" and r["isp_name"] == "450s"
                  and r["fp_name"] == fp_name and r["site_id"] != "equator_ref"
                  and r["residual_after_m_s"] is not None]
            if xs:
                bucket.append(float(np.mean(xs)))

    recombine = {
        "unboosted": sim.recombine(rec_before, damping=0.25),
        "due_east_plus_filament_repeater": sim.recombine(rec_after_fil, damping=0.25),
        "due_east_plus_payload_repeater": sim.recombine(rec_after_pay, damping=0.25),
    }

    # Stream a few headline events
    for key, u in unboosted.items():
        dictator.stream("fail" if (u["residual_m_s"] or 1) > 1 else "orbit_lock",
                        f"{key} unboosted residual {u['residual_m_s']:.1f} m/s")
        levy.assess("fail" if (u["residual_m_s"] or 1) > 1 else "orbit_lock")

    payload = {
        "status": "Speculative modeling only. No engineering, siting, or operational claims.",
        "prepared": "2026-11-27 America/Denver",
        "unboosted": {k: {kk: vv for kk, vv in u.items() if kk != "kepler"} | {
            "kepler_ecc": (u["kepler"] or {}).get("ecc"),
            "kepler_peri_m": (u["kepler"] or {}).get("h_perigee_m"),
        } for k, u in unboosted.items()},
        "budget": budget,
        "sign_notes": sign_notes,
        "comparator_summary": comparator_summary,
        "comparator_rows": comparator_rows,
        "repeater_rows": repeater_rows,
        "no_track": no_track,
        "policies_compact": {
            f"{k}|{sid}": {
                "east_res": pol["east"]["residual_m_s"],
                "east_apo": pol["east"]["apogee_km"], "east_peri": pol["east"]["perigee_km"],
                "sup_az": pol["suppress"]["az"]["az_deg"],
                "sup_res": pol["suppress"]["eval"]["residual_m_s"],
                "best_az": pol["best"]["az_deg"] if pol["best"] else None,
                "best_res": pol["best"]["residual_m_s"] if pol["best"] else None,
                "best_apo": pol["best"]["apogee_km"] if pol["best"] else None,
                "best_peri": pol["best"]["perigee_km"] if pol["best"] else None,
                "gate_allowed": pol["gate"]["allowed"], "gate_principle": pol["gate"]["principle"],
            } for (k, sid), pol in policies.items()
        },
        "polarity": {
            "locked": [f"{a}—{b}" for a, b in locked_e],
            "open": [f"{a}—{b}" for a, b in open_e],
            "inversion_holds": inv,
            "charge_rule": "labeled interpretation: leftover and no-track ascent +1; repeater and best-azimuth −1 (complementary); due-east boost +1 (can stretch); comparator −1 (a gate).",
        },
        "recombine": recombine,
        "levy_total": levy.total,
        "transcriber_n": len(transcriber.chronicles),
        "nexus_n": len(nexus.registry),
        "assumptions": [
            "Repeater is a vacuum two-burn from apogee toward a 200 km circular, paid by the rocket equation. Not free Δv.",
            "I_sp = 300 s and 450 s, and f_p = 0.05 / 0.30 / 0.85, are recycled labeled assumptions, not certificates.",
            "f_p = 0.05 was the heat-regrowth filament budget; using it as propellant is a re-purpose, not a second mass.",
            "f_p = 0.85 was the optimistic first-stage fraction of the staged stack and is already spent there; a repeater on that config is a fraction of the remaining 15%.",
            "The no-stage dart did not fly with a reserved stage; adding a repeater is adding a new mass allocation.",
            "Earth rotation cannot be switched off. Suppress = near-polar azimuth (rotation out of plane) and/or Oasis-PrinciplesGate refusing a due-east site admission.",
            "equator_ref is a physics reference, not a site; AdaptOrDie blocks a zero coordinate as a siting admission.",
            "No-track starts at rest relative to the pad. In-plane inertial speed is only Earth rotation when due-east is admitted. Constant thrust at initial T/W of 3 or 10 (recycled g-order numbers, now T/W, not rail g). After a 100 m vertical tower, a labeled pitch program from (90-kick)° to 5° over the 40 km flatten characteristic of the goal-seek continuation. Thrust is not slaved to the initial horizontal Earth-rotation velocity.",
            "Orbit lock = two-burn residual to 200 km circular <= 1 m/s and perigee >= 100 km.",
            "Heating is a Sutton–Graves radiation-equilibrium proxy, not a CFD wall temperature.",
            "Deterministic delta recombine; Math.random stub not used.",
        ],
    }
    (OUT / "redstone_repeater_comparator.json").write_text(
        json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print("Wrote", OUT / "redstone_repeater_comparator.json")
    return payload


def make_figure(payload):
    """One figure: residual by site and policy, repeater, comparator, no-track."""
    fig, axes = plt.subplots(2, 2, figsize=(11.2, 9.2), constrained_layout=False)
    fig.suptitle("Repeater, comparator, and no-track pad ascent  (speculative modeling only)",
                 fontsize=11, color="#1f3a5f")

    nice = {"tilt0_333": "0° 80 km", "evac_dart_407": "5° evac dart",
            "tilt5_431": "5° tilt", "staged_256": "staged (true 1,148)"}

    # Panel A
    ax = axes[0, 0]
    lat = {r["site_id"]: r["lat"] for r in payload["comparator_rows"]}
    rows = [(k, v) for k, v in payload["policies_compact"].items()
            if k.startswith("tilt0_333|") and not k.endswith("equator_ref")]
    rows.sort(key=lambda kv: -abs(lat.get(kv[0].split("|", 1)[1], 0)))
    labels, east, best, sup, unb = [], [], [], [], []
    for k, v in rows:
        labels.append(k.split("|", 1)[1].replace("_", " "))
        east.append(v["east_res"]); best.append(v["best_res"]); sup.append(v["sup_res"])
        unb.append(payload["unboosted"]["tilt0_333"]["residual_m_s"])
    x = np.arange(len(labels))
    ax.plot(x, unb, "k--", lw=1, label="unboosted (333 m/s, no climb)")
    ax.plot(x, east, "o-", color="#1f3a5f", ms=3.5, label="due east")
    ax.plot(x, best, "s-", color="#2a7d4f", ms=3.5, label="best azimuth")
    ax.plot(x, sup, "^-", color="#b85c38", ms=3.5, label="suppress (near-polar az)")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=7)
    ax.set_ylabel("two-burn residual to 200 km (m/s)")
    ax.set_title("A.  0° / 17,000 mph / 80 km — azimuth levers")
    ax.legend(fontsize=7, loc="upper right")
    ax.set_ylim(0, 400)
    ax.grid(True, alpha=0.3)

    # Panel B — selected due-east repeater bars
    ax = axes[0, 1]
    recs = payload["repeater_rows"]
    def pick(config, site, fp_name):
        for r in recs:
            if (r["config"] == config and r["site_id"] == site and r["policy"] == "due_east"
                    and r["fp_name"] == fp_name and r["isp_name"] == "450s"):
                return r
        return None
    pairs = [("tilt0_333", "baikonur"), ("tilt0_333", "las_vegas"),
             ("evac_dart_407", "baikonur"), ("evac_dart_407", "las_vegas"),
             ("staged_256", "baikonur"), ("staged_256", "las_vegas")]
    h_before, h_fil, h_pay, tick = [], [], [], []
    for c, s in pairs:
        r_fil = pick(c, s, "filament_0.05")
        r_pay = pick(c, s, "payload_0.30")
        if not r_fil:
            continue
        h_before.append(r_fil["residual_before_m_s"])
        h_fil.append(r_fil["residual_after_m_s"])
        h_pay.append(r_pay["residual_after_m_s"])
        site = "Bai" if s == "baikonur" else "LAS"
        short = {"tilt0_333": "0° 80 km", "evac_dart_407": "5° dart",
                 "tilt5_431": "5° tilt", "staged_256": "staged"}
        tick.append(f"{short[c]}\n{site}")
    w = 0.27
    x = np.arange(len(tick))
    ax.bar(x - w, h_before, w, color="#7a7a7a", label="due-east, no repeater")
    ax.bar(x, h_fil, w, color="#b85c38", label="repeater f_p=0.05 (filament)")
    ax.bar(x + w, h_pay, w, color="#2a7d4f", label="repeater f_p=0.30 (payload) — 0 is a lock")
    ax.set_xticks(x)
    ax.set_xticklabels(tick, fontsize=7)
    ax.set_ylabel("residual (m/s)")
    ax.set_title("B.  Repeater at I_sp = 450 s, due-east releases")
    ax.legend(fontsize=6.5, loc="upper left")
    ax.grid(True, axis="y", alpha=0.3)

    # Panel C
    ax = axes[1, 0]
    colors = {"tilt0_333": "#1f3a5f", "evac_dart_407": "#2a7d4f",
              "tilt5_431": "#6b4c9a", "staged_256": "#b85c38"}
    for c, col in colors.items():
        sub = [r for r in payload["comparator_summary"] if r["config"] == c]
        sub.sort(key=lambda r: r["T_m_s"])
        ax.plot([r["T_m_s"] for r in sub], [r["mean_comparator_m_s"] for r in sub],
                "o-", color=col, ms=3, label=nice[c])
        ax.axhline(sub[0]["mean_due_east_m_s"], color=col, ls="--", lw=0.8, alpha=0.7)
        ax.axhline(sub[0]["mean_best_az_m_s"], color=col, ls=":", lw=1.0, alpha=0.8)
    ax.set_xlabel("comparator threshold T (m/s of unboosted residual)")
    ax.set_ylabel("mean residual over real sites (m/s)")
    ax.set_title("C.  Comparator vs due-east (dashed) and best az (dotted)")
    ax.legend(fontsize=6.5, loc="upper right")
    ax.set_xlim(0, 2050)
    ax.grid(True, alpha=0.3)

    # Panel D
    ax = axes[1, 1]
    nt = [r for r in payload["no_track"]
          if r["vehicle"] == "hollow_dart_12.6kg" and r["isp_s"] == 450
          and r["tw0"] == 3.0 and r["az_policy"] == "due_east"
          and r["reserve_mode"] == "all_in_ascent"
          and r["site_id"] in ("kourou", "las_vegas", "baikonur")]
    fps = [0.05, 0.30, 0.85]
    site_ids = ["baikonur", "las_vegas", "kourou"]
    site_lab = {"baikonur": "Baikonur", "las_vegas": "LAS", "kourou": "Kourou"}
    x = np.arange(len(fps))
    w = 0.22
    for i, sid in enumerate(site_ids):
        ys = []
        for fp in fps:
            rec = next((r for r in nt if r["site_id"] == sid and abs(r["fp"] - fp) < 1e-9), None)
            ys.append(0 if rec is None else rec["h_max_km"])
        ax.bar(x + (i - 1) * w, ys, w, label=site_lab[sid],
               color=["#1f3a5f", "#2a7d4f", "#b85c38"][i])
    ax.axhline(100, color="k", ls="--", lw=0.8, label="Karman 100 km")
    ax.axhline(200, color="k", ls=":", lw=0.8, label="200 km")
    ax.set_xticks(x)
    ax.set_xticklabels(["f_p=0.05\n(filament)", "f_p=0.30\n(payload)", "f_p=0.85\n(optimistic)"])
    ax.set_ylabel("max altitude (km)")
    ax.set_title("D.  No-track dart, I_sp=450 s, T/W=3, due-east, all-in")
    ax.legend(fontsize=6.5, loc="upper left")
    ax.grid(True, axis="y", alpha=0.3)

    fig.tight_layout(rect=[0, 0.01, 1, 0.94], w_pad=2.0, h_pad=1.6)
    path = OUT / "fig11_redstone_repeater_comparator.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    print("Wrote", path)
    return str(path)



if __name__ == "__main__":
    p = run()
    make_figure(p)
    # quick headlines
    print("\n=== UNBOOSTED ===")
    for k, u in p["unboosted"].items():
        print(f"  {k}: residual={u['residual_m_s']:.2f} apo={u['apogee_km']:.1f} peri={u['perigee_km']:.1f} mass={u['mass_at_release_kg']:.3f}")
    print("\n=== FP NEEDED ===")
    for k, v in p["budget"]["fp_needed"].items():
        print(f"  {k}: {v}")
    print("\n=== DV BY BUDGET ===")
    print(p["budget"]["dv_by_fp_isp"])
    print("\n=== COMPARATOR (does it beat best az?) ===")
    for r in p["comparator_summary"]:
        if r["T_m_s"] in (200, 350, 500, 1200):
            print(f"  {r['config']} T={r['T_m_s']}: comp={r['mean_comparator_m_s']:.1f} east={r['mean_due_east_m_s']:.1f} "
                  f"best={r['mean_best_az_m_s']:.1f} admit={r['n_admitted']} better_than_best={r['n_better_than_best_az']} "
                  f"beats_best={r['beats_best_az_mean']} beats_east={r['beats_due_east_mean']}")
    print("\n=== NO-TRACK HEADLINES (dart, 450s, T/W=3, due-east, all-in) ===")
    for r in p["no_track"]:
        if r["vehicle"] == "hollow_dart_12.6kg" and r["tw0"] == 3 and r["az_policy"] == "due_east" and r["reserve_mode"] == "all_in_ascent":
            print(f"  {r['site_id']} fp={r['fp']}: hmax={r['h_max_km']:.1f} km h_bo={r.get('h_burnout_km')} "
                  f"v_bo={r.get('v_burnout_m_s')} res={r['residual_coast_m_s']} after={r['residual_after_repeater_m_s']} "
                  f"karman={r['reached_karman']} lock={r['locked']} q={r['peak_q_pa']:.0f} Teq={r['peak_Teq_K']:.0f}K "
                  f"gloss={r['gravity_loss_m_s']:.0f} dloss={r['drag_loss_m_s']:.0f}")
    print("recombine", p["recombine"])
    print("polarity locked", p["polarity"]["locked"], "inv", p["polarity"]["inversion_holds"])
