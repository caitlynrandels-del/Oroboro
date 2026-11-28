#!/usr/bin/env python3
# CONJUNCTIVE (audit 2026-11-27): one loop Genesis -> Nexus -> Oasis admission -> PrinciplesGate
# -> NaCl consensus -> Dictator -> Transcriber -> Levy -> damped deterministic recombine.
# Speculative modeling only. No engineering, flight, siting, vacuum-tube, clinical or operational claims.
"""Plumbing dynamics on the recycled straw path and the native cancer mesh.

Speculative modeling only. Not an engineering design, flight plan, vacuum-tube
spec, or clinical, biological, or therapeutic claim. No operational claims.

Conjunctive Oroboro wiring. Recycles the evacuated-STRAW leftover (595 m/s,
open-loop, f_p=0.85 Kourou) and the 1,030.94 km vacuum path to a 200 km
circular at T/W=3. Recycles the light-off no-plumbing cancer signature
(p_overt_any=0.175, dorm_alive_mean=10.215, levy_gain=0.05). Plumbing is off
by default; the light-off no-plumbing path must stay unchanged.
"""
from __future__ import annotations

import csv
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
import run_guidance_kite_line_straw as GS

sys.path.insert(0, __import__("os").environ.get("OASIS_BRIDGE", "/workspace/oasis-build/SkyAriOasis/Bridge"))  # Oasis bridge (sky-ari-ai build) on the project computer
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "consciousness-mapping"))  # this repo
import oasis_core as core  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "metastasis-native"))  # this repo
import run_priority as RP
from oro_native import reconcile_whole_vs_parts, load_params

OUT = G.OUT
HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
CANCER_DATA = Path(__file__).resolve().parents[2] / "metastasis-native" / "data" / "plumbing"
CANCER_DATA.mkdir(parents=True, exist_ok=True)

MU, RE, G_STD = G.MU_EARTH, G.R_EARTH, G.G_STD
LEO, KARMAN = G.LEO_ALT_M, G.KARMAN_M
ISP = 450.0
TW0 = 3.0
FP = 0.85
P_ATM = 101325.0
ETA_COMP = 0.5  # labeled compressor / reservoir efficiency
RHO_SL = G.rho_isa(0.0)

# Recycled settled leftovers (do not overwrite; confirmatory runs sit beside them)
RECYCLED_EVAC80 = dict(
    residual_m_s=595.0037065709621,
    h_max_km=523.9377604202656,
    perigee_km=-1022.121962749782,
    h_burnout_km=109.34129579064064,
    v_burnout_m_s=7274.810916663704,
    peak_Teq_K=1579.4637048936204,
    label="straw_evac80_openloop_fp0.85",
)
RECYCLED_S_ACC_KM = 1030.9423553077288
RECYCLED_EVAC_TUBE_KM = 767.6248133925062
LIGHT_OFF_TARGET = dict(
    p_overt_any=0.175,
    dorm_alive_mean=10.215,
    levy_mean=1905.61,
    n_frustrated_mean=22.515,
    extracted_mean=0.0,
    levy_gain=0.05,
)

LEVY = {
    "genesis": 0, "admit_valve": 1, "suppress_valve": 2, "leak": 2,
    "pneumatic": 4, "stage_isolate": 4, "straw_exit": 4, "orbit_lock": 14,
    "fail": 2, "extract": 4, "damper_reconcile": 4,
}


def load_dart_site():
    gpath = OUT / "guidance_kite_line_straw.json"
    g = json.loads(gpath.read_text())
    dart = g["dart"]
    geo = json.loads((OUT / "geography.json").read_text()) if (OUT / "geography.json").exists() else None
    kourou = {"id": "kourou", "name": "Kourou (CSG)", "lat": 5.2372, "lon": -52.7681, "elev_m": 10.0}
    if geo and "sites" in geo:
        for s in geo["sites"]:
            if s.get("id") == "kourou":
                kourou = s
                break
    return dart, kourou


def gate_component(name, principle="AdaptOrDie"):
    pg = core.PrinciplesGate()
    allowed, why = pg.admit(name, {principle: True})
    return {"name": name, "allowed": bool(allowed), "principle": why or principle}


def integrate_plumbed_straw(
    dart, *,
    h0=10.0, fp=FP, isp=ISP, tw0=TW0, kick_deg=5.0, tower_m=100.0,
    dt=0.05, t_max=1500.0, lat_deg=5.2372,
    straw_h_m=80_000.0, straw_s_m=None, straw_until="altitude",
    leak_frac=0.0, n_stages=1, p_push_pa=0.0, valve_gated=True,
    evac=True, pitch="openloop", push_when="always",
):
    """Open-loop straw ascent with staged vacuum, leak, and a pneumatic push.

    Residual is evaluated at the last accelerating event (chemical burnout or
    tube exit if a pressure push is still on). Energy is booked as mechanical
    work on the dart, supply work at labeled compressor efficiency, and leak
    makeup. Speculative only.
    """
    area = float(dart["area"])
    cd = float(dart["cd"])
    m0 = float(dart["mass"])
    if fp <= 0 or m0 <= 0:
        return {"ok": False, "reason": "no_ascent_propellant"}
    T = tw0 * m0 * G_STD
    ve = isp * G_STD
    mdot = T / ve
    m_prop = fp * m0
    m = m0
    r0 = RE + max(0.0, h0)
    x, y = 0.0, r0
    vx, vy = 0.0, 0.0
    t = 0.0
    h_max = max(0.0, h0)
    peak_q = peak_qsg = peak_Teq = 0.0
    g_loss = d_loss = 0.0
    t_burn_end = None
    burned = 0.0
    burnout = None
    apogee = None
    notes = []
    s_flight = 0.0
    W_mech = 0.0
    W_supply = 0.0
    W_leak = 0.0
    dv_pneumatic = 0.0
    n_commit = n_block = n_stage = 0
    cur_stage = 0
    in_tube = True
    t_exit = None
    state_at_exit = None
    last_accel = None
    peak_Fp = 0.0
    leak_mass = 0.0
    n_stages = max(1, int(n_stages))
    tube_s = float(straw_s_m) if straw_s_m else None

    def local_basis(xx, yy):
        r = math.hypot(xx, yy)
        urx, ury = xx / r, yy / r
        uhx, uhy = ury, -urx
        return r, urx, ury, uhx, uhy

    def inside(h, s_fl):
        if not evac and leak_frac >= 1.0 and p_push_pa <= 0:
            # open-air reference: still "in" the channel for staging bookkeeping
            pass
        if straw_until == "path" and tube_s is not None:
            return s_fl < tube_s
        return h < straw_h_m

    while t < t_max:
        r, urx, ury, uhx, uhy = local_basis(x, y)
        if r < 1.0:
            notes.append("center")
            break
        h = r - RE
        if h < -10.0 and t > 1.0:
            notes.append("impact")
            break
        s_down = r0 * math.atan2(x, y) if (x or y) else 0.0
        speed = math.hypot(vx, vy)
        vr = vx * urx + vy * ury
        vt = vx * uhx + vy * uhy
        gamma = math.atan2(vr, vt) if (abs(vt) > 1e-9 or abs(vr) > 1e-9) else math.pi / 2.0
        in_tube = inside(h, s_flight)
        # Stage index along the channel (path or altitude fraction).
        if in_tube:
            if straw_until == "path" and tube_s:
                frac = min(0.999999, max(0.0, s_flight / tube_s))
            else:
                frac = min(0.999999, max(0.0, h / max(straw_h_m, 1.0)))
            stg = int(frac * n_stages)
            if stg != cur_stage:
                n_stage += 1
                cur_stage = stg
        rho_out = G.rho_isa(max(0.0, h))
        if in_tube and evac:
            # Staged isolation lowers the residual density; leak_frac=0 is a
            # perfect vacuum (recycled evac). leak_frac=1 with n_stages=1 is
            # open air inside the channel.
            leak_eq = float(leak_frac) / float(n_stages)
            rho = leak_eq * rho_out
        else:
            rho = rho_out
        q = 0.5 * rho * speed * speed
        qsg = G.sutton_graves_q(rho, speed)
        Teq = G.T_eq_radiation(qsg)
        peak_q = max(peak_q, q)
        peak_qsg = max(peak_qsg, qsg)
        peak_Teq = max(peak_Teq, Teq)
        gacc = MU / (r * r)
        gx, gy = -gacc * x / r, -gacc * y / r

        dx = dy = 0.0
        if speed > 1e-6 and m > 0 and rho > 0:
            Fd = 0.5 * cd * rho * area * speed * speed
            dx, dy = -Fd / m * vx / speed, -Fd / m * vy / speed
            d_loss += (Fd / m) * dt

        if pitch == "flatten_to_5":
            # Labeled channel geometry: after the tower, lerp 85° → 5° over the
            # tube path (recycled flatten / vacuum-accel length).
            s_end = tube_s if (tube_s and tube_s > 0) else max(straw_h_m / math.sin(math.radians(45.0)), 1.0)
            if h - h0 < tower_m:
                cmd = math.pi / 2.0
            else:
                frac = min(1.0, max(0.0, s_flight / s_end))
                cmd = math.radians(85.0) * (1.0 - frac) + math.radians(5.0) * frac
        else:
            cmd = GS.openloop_pitch(h, h0, tower_m, kick_deg)
        cmd = max(0.0, min(math.pi / 2.0, cmd))
        thrusting = burned < m_prop - 1e-12
        tx = ty = 0.0
        if thrusting:
            tdirx = urx * math.sin(cmd) + uhx * math.cos(cmd)
            tdiry = ury * math.sin(cmd) + uhy * math.cos(cmd)
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
                burnout = dict(t_s=t, h_m=h, v_m_s=speed, gamma_deg=math.degrees(gamma),
                               mass_kg=m, s_m=s_down, s_flight_m=s_flight)

        # Pneumatic push: F = (P_behind - P_ahead) * A, only inside the tube.
        px = py = 0.0
        Fp = 0.0
        P_ahead = (rho / RHO_SL) * P_ATM if RHO_SL > 0 else 0.0
        P_behind = float(p_push_pa) if (in_tube and p_push_pa > 0) else 0.0
        admit = False
        if in_tube and P_behind > 0 and m > 0:
            # Oasis / PrinciplesGate: admit a gradient only if the ahead side
            # is still a lower pressure (the seal holds enough to have a push).
            if valve_gated:
                admit = (P_behind > P_ahead * 2.0) if P_ahead > 0 else True
            else:
                admit = True
            if push_when == "late" and cmd > math.radians(20.0):
                admit = False
            if admit:
                n_commit += 1
                Fp = (P_behind - P_ahead) * area
                if Fp > 0:
                    # Directed along the channel (commanded pitch), not the
                    # instantaneous velocity, so a steep early program is not
                    # rewarded with a lofted push.
                    ux = urx * math.sin(cmd) + uhx * math.cos(cmd)
                    uy = ury * math.sin(cmd) + uhy * math.cos(cmd)
                    un = math.hypot(ux, uy) or 1.0
                    ux, uy = ux / un, uy / un
                    px, py = (Fp / m) * ux, (Fp / m) * uy
                    dv_pneumatic += (Fp / m) * dt
                    W_mech += Fp * speed * dt
                    W_supply += (P_behind * area * speed * dt) / ETA_COMP
                    peak_Fp = max(peak_Fp, Fp)
            else:
                n_block += 1
        # Leak makeup volume: labeled orifice-scale conductance.
        if in_tube and leak_frac > 0 and P_behind > 0:
            Q_vol = leak_frac * area * 10.0 * max(0.0, (P_behind - P_ahead) / P_ATM)
            W_leak += (Q_vol * P_behind * dt) / ETA_COMP
            leak_mass += Q_vol * (rho if rho > 0 else leak_frac * rho_out) * dt

        ax = gx + dx + tx + px
        ay = gy + dy + ty + py
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt
        speed2 = math.hypot(vx, vy)
        s_flight += 0.5 * (speed + speed2) * dt
        t += dt
        r2 = math.hypot(x, y)
        h2 = r2 - RE
        if h2 > h_max:
            h_max = h2
            _, ur2x, ur2y, uh2x, uh2y = local_basis(x, y)
            vr2 = vx * ur2x + vy * ur2y
            vt2 = vx * uh2x + vy * uh2y
            apogee = dict(t_s=t, h_m=h2, v_m_s=speed2,
                          gamma_deg=math.degrees(math.atan2(vr2, vt2)) if (abs(vt2) > 1e-9 or abs(vr2) > 1e-9) else 0.0)
        still_pushing = in_tube and p_push_pa > 0 and (not valve_gated or admit)
        if thrusting or still_pushing:
            last_accel = dict(t_s=t, h_m=h2, v_m_s=speed2,
                              gamma_deg=math.degrees(math.atan2(
                                  vx * (x / r2) + vy * (y / r2),
                                  vx * (y / r2) + vy * (-x / r2))) if r2 > 1 else 0.0,
                              mass_kg=m, s_m=s_down, s_flight_m=s_flight)
        if in_tube is False and t_exit is None and t > 1.0:
            t_exit = t
            state_at_exit = dict(t_s=t, h_m=h2, v_m_s=speed2, mass_kg=m, s_flight_m=s_flight)
            notes.append("straw_exit")
        if (not thrusting) and (p_push_pa <= 0 or not inside(h2, s_flight)) and h2 < 0 and t > 1.0:
            break
        if (not math.isfinite(x)) or speed2 > 20000:
            notes.append("unphysical")
            break

    if burnout is None and burned > 0:
        r, urx, ury, uhx, uhy = local_basis(x, y)
        h = r - RE
        speed = math.hypot(vx, vy)
        vr = vx * urx + vy * ury
        vt = vx * uhx + vy * uhy
        burnout = dict(t_s=t, h_m=h, v_m_s=speed, gamma_deg=math.degrees(math.atan2(vr, vt)) if (abs(vt) > 1e-9 or abs(vr) > 1e-9) else 0.0,
                       mass_kg=m, s_m=r0 * math.atan2(x, y) if (x or y) else 0.0, s_flight_m=s_flight)

    if last_accel and burnout and p_push_pa > 0 and last_accel.get("t_s", 0) > (burnout.get("t_s") or 0) + 0.5 * dt:
        eval_state = last_accel
    else:
        eval_state = burnout
    return dict(
        ok=True, h_max_m=h_max, burnout=burnout, apogee=apogee, eval_state=eval_state,
        t_s=t, t_burn_s=t_burn_end if t_burn_end is not None else t,
        t_exit_s=t_exit, exit_state=state_at_exit,
        mass_end_kg=m, burned_kg=burned, fp_ascent=fp,
        peak_q_pa=peak_q, peak_sutton_graves_W_m2=peak_qsg, peak_Teq_K=peak_Teq,
        gravity_loss_m_s=g_loss, drag_loss_m_s=d_loss,
        s_flight_m=s_flight, W_mech_J=W_mech, W_supply_J=W_supply, W_leak_J=W_leak,
        W_waste_J=max(0.0, W_supply + W_leak - W_mech),
        dv_pneumatic_m_s=dv_pneumatic, peak_Fp_N=peak_Fp, leak_mass_kg=leak_mass,
        n_commit=n_commit, n_block=n_block, n_stage=n_stage, n_stages=n_stages,
        leak_frac=leak_frac, p_push_pa=p_push_pa, valve_gated=valve_gated,
        straw_h_m=straw_h_m, straw_s_m=tube_s, straw_until=straw_until, evac=evac,
        notes=notes, reached_karman=h_max >= KARMAN, reached_200km=h_max >= LEO,
    )


def close_plumbed(ascent, site, az_deg=90.0):
    ev = ascent.get("eval_state") or ascent.get("burnout")
    if not ev:
        return {**ascent, "residual_m_s": None, "locked": False, "h_max_km": ascent.get("h_max_m", 0) / 1000.0}
    # Borrow the guidance closer but swap in the last-accel state as "burnout".
    wrapped = {**ascent, "burnout": ev}
    out = GS.close_with_site(wrapped, site, az_deg)
    out["W_mech_J"] = ascent.get("W_mech_J", 0.0)
    out["W_supply_J"] = ascent.get("W_supply_J", 0.0)
    out["W_leak_J"] = ascent.get("W_leak_J", 0.0)
    out["W_waste_J"] = ascent.get("W_waste_J", 0.0)
    out["dv_pneumatic_m_s"] = ascent.get("dv_pneumatic_m_s", 0.0)
    out["drag_loss_m_s"] = ascent.get("drag_loss_m_s", 0.0)
    out["peak_Teq_K"] = ascent.get("peak_Teq_K", 0.0)
    out["s_flight_km"] = (ascent.get("s_flight_m") or 0.0) / 1000.0
    out["n_commit"] = ascent.get("n_commit", 0)
    out["n_block"] = ascent.get("n_block", 0)
    out["n_stage"] = ascent.get("n_stage", 0)
    out["leak_frac"] = ascent.get("leak_frac", 0.0)
    out["p_push_pa"] = ascent.get("p_push_pa", 0.0)
    out["peak_Fp_N"] = ascent.get("peak_Fp_N", 0.0)
    out["momentum_buildup_kg_m_s"] = (ev.get("mass_kg") or 0.0) * (out.get("v_inertial_m_s") or ev.get("v_m_s") or 0.0)
    out["s_exit_km"] = None if not ascent.get("exit_state") else ascent["exit_state"].get("s_flight_m", 0) / 1000.0
    if out.get("residual_m_s") is None:
        out["unbound"] = True
        # Honest bookkeeping: no two-burn residual exists for an unbound or
        # apogee-less state. Leave residual_m_s as None; do not invent a lock.
        out["residual_reason"] = "unbound_or_no_apogee"
    else:
        out["unbound"] = False
    return out


def run_launch(dart, site):
    cases = []

    def add(label, **kw):
        raw = integrate_plumbed_straw(dart, **kw)
        closed = close_plumbed(raw, site, az_deg=90.0)
        closed["label"] = label
        # keep a compact record
        keep = [
            "label", "residual_m_s", "locked", "h_max_km", "perigee_km", "apogee_km",
            "h_burnout_km", "v_burnout_m_s", "peak_Teq_K", "drag_loss_m_s",
            "dv_pneumatic_m_s", "W_mech_J", "W_supply_J", "W_leak_J", "W_waste_J",
            "s_flight_km", "n_commit", "n_block", "n_stage", "leak_frac", "p_push_pa",
            "peak_Fp_N", "momentum_buildup_kg_m_s", "site_id", "az_deg",
            "unbound", "residual_reason", "s_exit_km",
        ]
        row = {k: closed.get(k) for k in keep}
        row["straw_until"] = kw.get("straw_until", "altitude")
        row["straw_h_km"] = (kw.get("straw_h_m") or 0) / 1000.0
        row["straw_s_km"] = None if kw.get("straw_s_m") is None else kw["straw_s_m"] / 1000.0
        row["n_stages"] = kw.get("n_stages", 1)
        row["valve_gated"] = kw.get("valve_gated", True)
        row["evac"] = kw.get("evac", True)
        row["pitch"] = kw.get("pitch", "openloop")
        row["push_when"] = kw.get("push_when", "always")
        cases.append(row)
        r = row.get("residual_m_s")
        print(f"  {label:42s}  residual={None if r is None else f'{r:8.1f}'}  "
              f"h_max={row['h_max_km']:.1f} km  peri={row['perigee_km']}  "
              f"Teq={row['peak_Teq_K']:.0f}  drag={row['drag_loss_m_s']:.1f}  "
              f"dVp={row['dv_pneumatic_m_s']:.1f}  waste={row['W_waste_J']:.3e} J  "
              f"lock={row['locked']}", flush=True)
        return row

    print("== launch plumbing sweep ==", flush=True)
    # Confirmatory recycled evac (leak=0, no push)
    add("confirm_evac80_openloop", straw_h_m=80e3, leak_frac=0.0, n_stages=1, p_push_pa=0.0, evac=True)
    add("confirm_evac200_openloop", straw_h_m=200e3, leak_frac=0.0, n_stages=1, p_push_pa=0.0, evac=True)
    add("path1031_evac_nopush", straw_until="path", straw_s_m=RECYCLED_S_ACC_KM * 1000.0,
        straw_h_m=200e3, leak_frac=0.0, n_stages=1, p_push_pa=0.0, evac=True)
    add("path1031_flatten_nopush", straw_until="path", straw_s_m=RECYCLED_S_ACC_KM * 1000.0,
        straw_h_m=200e3, leak_frac=0.0, p_push_pa=0.0, evac=True, pitch="flatten_to_5")
    add("path767_flatten_nopush", straw_until="path", straw_s_m=RECYCLED_EVAC_TUBE_KM * 1000.0,
        straw_h_m=80e3, leak_frac=0.0, p_push_pa=0.0, evac=True, pitch="flatten_to_5")

    # Leak sweep on the 80 km and 200 km evac channels, unstaged and staged
    for hkm, h in (("80", 80e3), ("200", 200e3)):
        for leak in (1e-6, 1e-4, 1e-3, 1e-2, 1e-1, 1.0):
            add(f"leak{leak:g}_evac{hkm}_st1", straw_h_m=h, leak_frac=leak, n_stages=1, p_push_pa=0.0)
        for stages in (4, 16):
            add(f"leak1e-2_evac{hkm}_st{stages}", straw_h_m=h, leak_frac=1e-2, n_stages=stages, p_push_pa=0.0)

    # Pneumatic push, leak-free and leaky, 80 / 200 / 1031 km path
    for pbar in (0.1, 1.0, 10.0):
        p = pbar * P_ATM
        add(f"push{pbar:g}bar_evac80_leak0_gated", straw_h_m=80e3, leak_frac=0.0, p_push_pa=p, valve_gated=True)
        add(f"push{pbar:g}bar_evac80_leak0_ungated", straw_h_m=80e3, leak_frac=0.0, p_push_pa=p, valve_gated=False)
        add(f"push{pbar:g}bar_evac200_leak0_gated", straw_h_m=200e3, leak_frac=0.0, p_push_pa=p, valve_gated=True)
        add(f"push{pbar:g}bar_path1031_leak0_gated", straw_until="path", straw_s_m=RECYCLED_S_ACC_KM * 1000.0,
            straw_h_m=200e3, leak_frac=0.0, p_push_pa=p, valve_gated=True)
        add(f"push{pbar:g}bar_evac80_leak1e-2_st1", straw_h_m=80e3, leak_frac=1e-2, p_push_pa=p, n_stages=1, valve_gated=True)
        add(f"push{pbar:g}bar_evac80_leak1e-2_st16", straw_h_m=80e3, leak_frac=1e-2, p_push_pa=p, n_stages=16, valve_gated=True)
        add(f"push{pbar:g}bar_evac80_late", straw_h_m=80e3, leak_frac=0.0, p_push_pa=p, valve_gated=True, push_when="late")
        add(f"push{pbar:g}bar_path1031_flatten_gated", straw_until="path", straw_s_m=RECYCLED_S_ACC_KM * 1000.0,
            straw_h_m=200e3, leak_frac=0.0, p_push_pa=p, valve_gated=True, pitch="flatten_to_5")
        add(f"push{pbar:g}bar_path1031_flatten_late", straw_until="path", straw_s_m=RECYCLED_S_ACC_KM * 1000.0,
            straw_h_m=200e3, leak_frac=0.0, p_push_pa=p, valve_gated=True, pitch="flatten_to_5", push_when="late")

    # Open-air straw reference (no evac)
    add("openair80_nopush", straw_h_m=80e3, leak_frac=1.0, evac=False, p_push_pa=0.0)

    return cases


def ov_base(gain=0.05, **kw):
    ov = dict(levy_gain=gain)
    ov.update(kw)
    return ov


def plumb_ov(gain=0.05, strength=0.5, leak=0.0, seal=1.0, stages=1,
             timing="upstream", magnet=False, oasis=True, **kw):
    ov = ov_base(gain)
    ov.update(
        plumbing=True,
        plumbing_strength=strength,
        plumbing_leak=leak,
        plumbing_seal=seal,
        plumbing_stages=stages,
        plumbing_timing=timing,
        plumbing_magnet=magnet,
        plumbing_oasis=oasis,
    )
    ov.update(kw)
    return ov


def extra_cancer(rows, s):
    n = max(1, len(rows))
    def m(key, default=0.0):
        return float(np.mean([r.get(key, default) for r in rows]))
    s["plumbing_leaked_circ_mean"] = m("plumbing_leaked_circ")
    s["plumbing_leaked_niche_mean"] = m("plumbing_leaked_niche")
    s["plumbing_leaked_mean"] = m("plumbing_leaked")
    s["plumbing_valve_block_mean"] = m("plumbing_valve_block")
    s["plumbing_valve_commit_mean"] = m("plumbing_valve_commit")
    s["plumbing_sealed_mean"] = m("plumbing_sealed")
    s["p_eliminated"] = s.get("p_eliminated", 0.0)
    # transport yield already in extract_yield_mean; leakage fraction of attempts
    att = m("extract_attempts")
    s["leak_fraction_of_attempts"] = (s["plumbing_leaked_mean"] / att) if att else 0.0
    s["seal_fraction_of_commits_plus_leaks"] = (
        s["plumbing_sealed_mean"] / (s["plumbing_sealed_mean"] + s["plumbing_leaked_mean"])
        if (s["plumbing_sealed_mean"] + s["plumbing_leaked_mean"]) else 0.0
    )
    return s


def signature_match(s, target=LIGHT_OFF_TARGET, atol=1e-9):
    checks = {}
    for k, tv in target.items():
        if k == "levy_gain":
            continue
        sv = s.get(k)
        if k in ("levy_mean",):
            ok = abs(float(sv) - float(tv)) < 0.005 + atol  # reported to 2 decimals
        elif k in ("dorm_alive_mean", "n_frustrated_mean"):
            ok = abs(float(sv) - float(tv)) < 0.0005 + atol
        else:
            ok = abs(float(sv) - float(tv)) < atol
        checks[k] = dict(got=sv, target=tv, ok=bool(ok))
    ok_all = all(v["ok"] for v in checks.values())
    return ok_all, checks


def run_cancer(nseed=40):
    RP._init()
    P = RP.P
    print("== cancer plumbing sweep, nseed x cancers =", nseed, "x", len(RP.CANCERS), "==", flush=True)
    ledger = dict(nseed=nseed, cancers=list(RP.CANCERS), levy_gain=0.05,
                  note="Speculative only. No clinical or biological claims.")

    # whole vs parts
    wp = {}
    for label, ov in [
        ("light_off_no_plumbing", ov_base(0.05)),
        ("plumb_seal1_leak0_up", plumb_ov(leak=0.0, seal=1.0, strength=0.5, timing="upstream")),
        ("plumb_seal0.5_leak0.3_up", plumb_ov(leak=0.3, seal=0.5, strength=0.5, timing="upstream")),
        ("plumb_post_settling_leak0", plumb_ov(leak=0.0, seal=1.0, strength=0.5, timing="post_settling")),
    ]:
        a = RP.run("Prostate", 17000, P, sig=True, native_overrides=ov) if hasattr(RP, "run") else None
        # run lives on oro_native
        from oro_native import run as oro_run
        a = oro_run("Prostate", 17000, P, sig=True, native_overrides=ov)
        b = oro_run("Prostate", 17000, P, mode="decomposed", sig=True, native_overrides=ov)
        wp[label] = reconcile_whole_vs_parts(a, b)["consistent"]
        print("WHOLE vs PARTS", label, wp[label], flush=True)
    ledger["whole_vs_parts_consistent"] = wp

    conditions = [
        ("light_off_no_plumbing", ov_base(0.05), "signature"),
        ("plumb_perfect_up", plumb_ov(leak=0.0, seal=1.0, strength=0.5, stages=1, timing="upstream"), "plumbing"),
        ("plumb_leak0.1_seal1_up", plumb_ov(leak=0.1, seal=1.0, strength=0.5), "leak"),
        ("plumb_leak0.3_seal1_up", plumb_ov(leak=0.3, seal=1.0, strength=0.5), "leak"),
        ("plumb_leak0.6_seal1_up", plumb_ov(leak=0.6, seal=1.0, strength=0.5), "leak"),
        ("plumb_leak0.3_seal0.5_up", plumb_ov(leak=0.3, seal=0.5, strength=0.5), "seal"),
        ("plumb_leak0.3_seal0_up", plumb_ov(leak=0.3, seal=0.0, strength=0.5), "seal"),
        ("plumb_leak0.3_st4_up", plumb_ov(leak=0.3, seal=1.0, strength=0.5, stages=4), "stages"),
        ("plumb_leak0.3_st16_up", plumb_ov(leak=0.3, seal=1.0, strength=0.5, stages=16), "stages"),
        ("plumb_leak0.3_magnet_up", plumb_ov(leak=0.3, seal=1.0, strength=0.5, magnet=True), "magnet"),
        ("plumb_perfect_post", plumb_ov(leak=0.0, seal=1.0, strength=0.5, timing="post_settling"), "timing"),
        ("plumb_leak0.3_post", plumb_ov(leak=0.3, seal=1.0, strength=0.5, timing="post_settling"), "timing"),
        ("plumb_perfect_up_nooasis", plumb_ov(leak=0.0, seal=1.0, strength=0.5, oasis=False), "valve"),
        ("plumb_strength0.2_perfect_up", plumb_ov(leak=0.0, seal=1.0, strength=0.2), "strength"),
        ("plumb_strength0.8_perfect_up", plumb_ov(leak=0.0, seal=1.0, strength=0.8), "strength"),
    ]
    summaries = []
    all_rows = {}
    for name, ov, experiment in conditions:
        print("  running", name, flush=True)
        rows = RP.run_condition(RP.NEUTRAL, nseed=nseed, overrides=ov)
        s = extra_cancer(rows, RP.summarize(rows, name, experiment))
        s["levy_gain"] = 0.05
        s["overrides"] = {k: v for k, v in ov.items() if k != "levy_gain"}
        summaries.append(s)
        all_rows[name] = rows
        print(f"    p_overt={s['p_overt_any']:.3f}  dorm={s['dorm_alive_mean']:.3f}  "
              f"levy={s['levy_mean']:.2f}  frust={s['n_frustrated_mean']:.3f}  "
              f"extracted={s['extracted_mean']:.2f}  yield={s['extract_yield_mean']:.3f}  "
              f"leaked={s['plumbing_leaked_mean']:.2f}  sealed={s['plumbing_sealed_mean']:.2f}  "
              f"census={s['census_ok']} levy_ok={s['levy_ok']}", flush=True)

    sig_ok, sig_checks = signature_match(summaries[0])
    ledger["light_off_no_plumbing_signature_unchanged"] = sig_ok
    ledger["signature_checks"] = sig_checks
    print("SIGNATURE light-off no-plumbing unchanged:", sig_ok, sig_checks, flush=True)

    # per-cancer breakdown for baseline and perfect plumbing
    per = {}
    for name in ("light_off_no_plumbing", "plumb_perfect_up", "plumb_leak0.3_seal1_up", "plumb_perfect_post"):
        rows = all_rows[name]
        by = {}
        for c in RP.CANCERS:
            cr = [r for r in rows if r["cancer"] == c]
            by[c] = extra_cancer(cr, RP.summarize(cr, f"{name}:{c}", "per_cancer"))
        per[name] = by
    ledger["per_cancer"] = per
    ledger["summaries"] = summaries

    # write csv + json
    keys = [
        "condition", "experiment", "runs", "p_overt_any", "overt_mean", "dorm_alive_mean",
        "p_dorm_any", "p_eliminated", "levy_mean", "n_frustrated_mean", "n_frustrated_extract_mean",
        "n_locked_extract_mean", "extracted_mean", "extract_yield_mean", "extract_attempts_mean",
        "extract_commits_mean", "extracted_circ_mean", "extracted_dorm_mean", "extracted_overt_mean",
        "plumbing_leaked_mean", "plumbing_leaked_circ_mean", "plumbing_leaked_niche_mean",
        "plumbing_valve_block_mean", "plumbing_valve_commit_mean", "plumbing_sealed_mean",
        "leak_fraction_of_attempts", "seal_fraction_of_commits_plus_leaks",
        "census_ok", "levy_ok", "consensus_ok", "inversion_holds", "levy_gain",
    ]
    csv_path = CANCER_DATA / "plumbing_summaries.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for s in summaries:
            w.writerow({k: s.get(k) for k in keys})
    # compact rows (no events)
    compact_rows = {}
    drop = {"_events", "_chronicle", "_levy_from_events", "_sig", "_genesis_closed"}
    for name, rows in all_rows.items():
        compact_rows[name] = [{k: v for k, v in r.items() if k not in drop} for r in rows]
    payload = dict(ledger=ledger, summaries=summaries, rows=compact_rows)
    (CANCER_DATA / "plumbing_ledger.json").write_text(json.dumps(payload, indent=2, default=str))
    print("wrote", csv_path, flush=True)
    return ledger, summaries, all_rows


def fig15(launch_cases, cancer_summaries, out_path):
    fig, axes = plt.subplots(2, 2, figsize=(11.0, 8.4))
    fig.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.10, hspace=0.42, wspace=0.32)
    by = {c["label"]: c for c in launch_cases}

    # A. residual vs leak fraction, 80 km, staged vs unstaged
    ax = axes[0, 0]
    leaks = [0.0, 1e-6, 1e-4, 1e-3, 1e-2, 1e-1, 1.0]
    y1 = []
    for L in leaks:
        if L == 0.0:
            y1.append(by["confirm_evac80_openloop"]["residual_m_s"])
        else:
            y1.append(by[f"leak{L:g}_evac80_st1"]["residual_m_s"])
    ax.semilogx([1e-8 if L == 0 else L for L in leaks], y1, "o-", color="#1f3a5f", lw=1.4, ms=5, label="80 km, 1 stage")
    # staged at 1e-2
    ax.scatter([1e-2], [by["leak1e-2_evac80_st4"]["residual_m_s"]], marker="s", s=36, color="#c45c26", zorder=5, label="80 km, 4 stages @ 10$^{-2}$")
    ax.scatter([1e-2], [by["leak1e-2_evac80_st16"]["residual_m_s"]], marker="D", s=36, color="#2a7d4f", zorder=5, label="80 km, 16 stages @ 10$^{-2}$")
    ax.axhline(RECYCLED_EVAC80["residual_m_s"], color="#888", ls="--", lw=0.8, label="recycled evac 595 m/s")
    ax.set_xlabel("leak fraction (residual air vs outside)")
    ax.set_ylabel("leftover dV (m/s)")
    ax.set_title("A.  Straw leftover vs leak, $f_p$=0.85 Kourou")
    ax.legend(fontsize=7, loc="best", frameon=False)
    ax.grid(True, alpha=0.25)

    # B. residual vs pneumatic pressure, energy as marker size / twin
    ax = axes[0, 1]
    bars_x, bars_y, bars_c, labels = [], [], [], []
    series = [
        ("0 bar\nevac 80", "confirm_evac80_openloop", "#1f3a5f"),
        ("0.1 bar\n80 late", "push0.1bar_evac80_late", "#5b8aa6"),
        ("0.1 bar\n80", "push0.1bar_evac80_leak0_gated", "#3a6d8c"),
        ("0.1 bar\n200", "push0.1bar_evac200_leak0_gated", "#2a7d4f"),
        ("1 bar\n80", "push1bar_evac80_leak0_gated", "#c45c26"),
        ("1 bar\nleak 1e-2", "push1bar_evac80_leak1e-2_st1", "#888"),
    ]
    unbound_notes = []
    for i, (lab, key, col) in enumerate(series):
        if key not in by:
            continue
        if by[key].get("residual_m_s") is None or by[key].get("unbound"):
            unbound_notes.append(lab)
            continue
        bars_x.append(len(bars_x))
        bars_y.append(by[key]["residual_m_s"])
        bars_c.append(col)
        labels.append(lab)
    ax.bar(range(len(bars_y)), bars_y, color=bars_c, width=0.72, edgecolor="#103040", linewidth=0.4)
    ax.axhline(1.0, color="#333", ls=":", lw=0.7)
    ax.set_xticks(list(range(len(labels))))
    ax.set_xticklabels(labels, rotation=28, ha="right", fontsize=7)
    ax.set_ylabel("leftover dV (m/s)")
    n_unbound = sum(1 for c in launch_cases if c.get("unbound") or c.get("residual_m_s") is None)
    ax.set_title("B.  Pneumatic leftover (gated); %d unbound omitted" % n_unbound)
    ymax = max(bars_y) if bars_y else 1.0
    for i, lab in enumerate(labels):
        key = [k for l, k, _ in series if l == lab][0]
        w = by[key]["W_waste_J"] / 1e6
        if w >= 0.05:
            ax.text(i, bars_y[i] + ymax * 0.02, f"{w:.1f} MJ", ha="center", va="bottom", fontsize=6, color="#333")
    ax.grid(True, axis="y", alpha=0.25)

    # C. cancer p_overt / dorm / yield
    ax = axes[1, 0]
    sm = {s["condition"]: s for s in cancer_summaries}
    clabs = [
        ("light off\nno plumbing", "light_off_no_plumbing"),
        ("perfect\nupstream", "plumb_perfect_up"),
        ("leak 0.3\nseal 1", "plumb_leak0.3_seal1_up"),
        ("leak 0.3\nseal 0", "plumb_leak0.3_seal0_up"),
        ("leak 0.3\n16 stages", "plumb_leak0.3_st16_up"),
        ("perfect\npost-settling", "plumb_perfect_post"),
        ("leak 0.3\npost-settling", "plumb_leak0.3_post"),
    ]
    xs = np.arange(len(clabs))
    overt = [sm[k]["p_overt_any"] for _, k in clabs]
    dorm = [sm[k]["dorm_alive_mean"] / 40.0 for _, k in clabs]  # scale for overlay; label honestly
    yld = [sm[k]["extract_yield_mean"] for _, k in clabs]
    w = 0.27
    ax.bar(xs - w, overt, w, color="#8b1e1e", label="p(overt)", edgecolor="#103040", linewidth=0.3)
    ax.bar(xs, yld, w, color="#2a7d4f", label="extract yield", edgecolor="#103040", linewidth=0.3)
    ax2 = ax.twinx()
    ax2.plot(xs, [sm[k]["dorm_alive_mean"] for _, k in clabs], "o-", color="#1f3a5f", ms=5, lw=1.2, label="dormant pool")
    ax.set_xticks(xs)
    ax.set_xticklabels([a for a, _ in clabs], fontsize=6.5)
    ax.set_ylabel("p(overt) / extract yield")
    ax2.set_ylabel("mean dormant alive")
    ax.set_title("C.  Cancer channel: overt, yield, dormant pool")
    ax.text(0.02, 0.97, "no-Oasis (not plotted): yield 0.68, p(elim) 0.49",
            transform=ax.transAxes, fontsize=6.5, va="top", color="#333")
    ax.set_ylim(0, max(0.35, max(overt + yld) * 1.25))
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=7, loc="upper right", frameon=False)
    ax.grid(True, axis="y", alpha=0.25)

    # D. leakage vs sealed extract; frustrated vs locked extract edges
    ax = axes[1, 1]
    dlab = [
        ("perfect up", "plumb_perfect_up"),
        ("leak 0.1", "plumb_leak0.1_seal1_up"),
        ("leak 0.3", "plumb_leak0.3_seal1_up"),
        ("leak 0.6", "plumb_leak0.6_seal1_up"),
        ("seal 0.5", "plumb_leak0.3_seal0.5_up"),
        ("16 stages", "plumb_leak0.3_st16_up"),
        ("magnet", "plumb_leak0.3_magnet_up"),
        ("post leak 0.3", "plumb_leak0.3_post"),
    ]
    xs = np.arange(len(dlab))
    sealed = [sm[k]["plumbing_sealed_mean"] for _, k in dlab]
    leaked = [sm[k]["plumbing_leaked_mean"] for _, k in dlab]
    ax.bar(xs, sealed, 0.6, color="#2a7d4f", label="sealed extract", edgecolor="#103040", linewidth=0.3)
    ax.bar(xs, leaked, 0.6, bottom=sealed, color="#c45c26", label="leaked (circ+niche)", edgecolor="#103040", linewidth=0.3)
    ax.set_xticks(xs)
    ax.set_xticklabels([a for a, _ in dlab], rotation=28, ha="right", fontsize=7)
    ax.set_ylabel("mean cells / run")
    ax.set_title("D.  Sealed transport vs leakage (40×5)")
    ax.legend(fontsize=7, loc="upper right", frameon=False)
    ax.grid(True, axis="y", alpha=0.25)

    fig.suptitle("Fig. 15.  Plumbing dynamics on the straw path and the native extraction mesh  ·  speculative only",
                 fontsize=10, fontweight="bold")
    fig.savefig(out_path, dpi=160)
    plt.close(fig)
    print("wrote", out_path, flush=True)


def recombine_residuals(values, damping=0.25):
    """Damped deterministic recombine of leftover Δv, labeled."""
    arr = np.array([v for v in values if v is not None], dtype=float)
    if len(arr) == 0:
        return None
    mu = float(arr.mean())
    # shrink each leftover toward the mean
    rec = mu + (1.0 - damping) * (arr - mu)
    return dict(n=int(len(arr)), mean=mu, damped_mean=float(rec.mean()),
                min=float(arr.min()), max=float(arr.max()), damping=damping)


def main():
    dart, kourou = load_dart_site()
    import run_redstone_repeater_comparator as R

    gate = core.PrinciplesGate(core.load_config())
    nexus = R.Nexus()
    transcriber = R.Transcriber()
    dictator = R.Dictator(transcriber)
    levy = R.Levy(transcriber)

    def assess(kind, n=1):
        w = LEVY.get(kind, 1) * n
        levy.total += w
        levy.entries.append({"kind": kind, "weight": w, "n": n})
        return w

    levy.assess = assess
    nexus.register("genesis", {"tag": "I am the OG avatar", "weight": math.inf})
    assess("genesis")
    dictator.stream("genesis", "Plumbing dynamics ledger. Recycled evac-straw leftover and light-off cancer signature; new plumbing plugins only.")

    admit = {}
    for name, posd in (
        ("sealed_channel", {"x": 5.2372, "y": -52.7681, "z": 1.0}),
        ("staged_vacuum", {"x": 5.2372, "y": -52.7681, "z": 2.0}),
        ("pneumatic_push", {"x": 5.2372, "y": -52.7681, "z": 3.0}),
        ("oasis_valve", {"x": 5.2372, "y": -52.7681, "z": 4.0}),
        ("null_channel", None),
    ):
        pos = core.vec(posd) if posd else None
        gr = gate.check("CreateAnchor", pos, f"Admit {name}", utility=0.65)
        admit[name] = {"allowed": bool(gr.allowed), "principle": gr.principle}
        if gr.allowed:
            assess("admit_valve")
            nexus.register(f"plumb:{name}", {"pos": posd})
        else:
            assess("suppress_valve")
            dictator.stream("suppress_valve", f"Blocked {name}: {gr.principle}")

    launch_cases = run_launch(dart, kourou)
    # levy on launch outcomes
    for c in launch_cases:
        if c.get("locked"):
            assess("orbit_lock")
        if (c.get("W_leak_J") or 0) > 0 or (c.get("leak_frac") or 0) > 0:
            assess("leak")
        if (c.get("dv_pneumatic_m_s") or 0) > 0:
            assess("pneumatic")
        if (c.get("n_stage") or 0) > 0:
            assess("stage_isolate", n=c["n_stage"])
        if c.get("n_block"):
            assess("fail")

    cancer_ledger, cancer_summaries, cancer_rows = run_cancer(nseed=40)
    for s in cancer_summaries:
        if s["condition"] == "light_off_no_plumbing":
            continue
        assess("extract", n=max(1, int(round(s.get("plumbing_sealed_mean") or 0))))
        if (s.get("plumbing_leaked_mean") or 0) > 0:
            assess("leak", n=max(1, int(round(s["plumbing_leaked_mean"]))))

    fig_path = OUT / "fig15_plumbing_dynamics.png"
    fig15(launch_cases, cancer_summaries, fig_path)

    rec = recombine_residuals([c.get("residual_m_s") for c in launch_cases if c.get("residual_m_s") is not None])
    confirm = next(c for c in launch_cases if c["label"] == "confirm_evac80_openloop")
    evac_match = abs(confirm["residual_m_s"] - RECYCLED_EVAC80["residual_m_s"]) < 1.0

    payload = dict(
        status="ok",
        prepared="27 November 2026",
        zone="America/Denver",
        speculative_only=True,
        no_engineering_or_clinical_claims=True,
        recycled=dict(evac80=RECYCLED_EVAC80, s_acc_km=RECYCLED_S_ACC_KM,
                      evac_tube_km=RECYCLED_EVAC_TUBE_KM, light_off_cancer=LIGHT_OFF_TARGET),
        dart=dart,
        path_gate=admit,
        launch_cases=launch_cases,
        launch_confirm_evac80_residual_match_1ms=evac_match,
        launch_recombine=rec,
        cancer=dict(
            signature_unchanged=cancer_ledger["light_off_no_plumbing_signature_unchanged"],
            signature_checks=cancer_ledger["signature_checks"],
            whole_vs_parts_consistent=cancer_ledger["whole_vs_parts_consistent"],
            summaries=cancer_summaries,
            per_cancer=cancer_ledger.get("per_cancer"),
            data_dir=str(CANCER_DATA),
        ),
        levy_total=levy.total,
        levy_entries=levy.entries,
        transcriber_n=len(getattr(transcriber, "lines", []) or getattr(transcriber, "log", []) or []),
        nexus_n=len(getattr(nexus, "items", {}) or getattr(nexus, "registry", {}) or {}),
        assumptions=[
            "Speculative modeling only. Not an engineering design, vacuum-tube specification, flight plan, or clinical or biological claim.",
            "Pneumatic force is F=(P_behind-P_ahead)*A only while the dart is inside the channel. Supply work is P*A*v / eta with eta=0.5 labeled.",
            "Leak residual density inside a staged vacuum segment is leak_frac/n_stages times the outside ISA density at that altitude.",
            "Residual is scored at the last accelerating event (chemical burnout or the end of a still-on pneumatic push).",
            "Light-off no-plumbing cancer path consumes no plumbing RNG and must reproduce the recycled 0.175 / 10.215 signature.",
            "Oasis is the valve on the sealed extraction channel. Leak returns cells to circulation or to their niche; sealed hops go to EXTRACTED.",
            "Lock remains residual <= 1 m/s and perigee >= 200 km. Levy gain on cancer runs is the calibrated 0.05.",
        ],
        fig=str(fig_path),
    )
    outj = OUT / "plumbing_dynamics.json"
    outj.write_text(json.dumps(payload, indent=2, default=str))
    print("wrote", outj, flush=True)
    print("confirm evac80 residual", confirm["residual_m_s"], "match", evac_match)
    print("cancer signature unchanged", cancer_ledger["light_off_no_plumbing_signature_unchanged"])
    print("locks", sum(1 for c in launch_cases if c.get("locked")), "/", len(launch_cases))
    return payload


if __name__ == "__main__":
    main()
