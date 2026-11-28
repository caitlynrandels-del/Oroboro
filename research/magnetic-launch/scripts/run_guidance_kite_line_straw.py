#!/usr/bin/env python3
# CONJUNCTIVE (audit 2026-11-27): one loop Genesis -> Nexus -> Oasis admission -> PrinciplesGate
# -> NaCl consensus -> Dictator -> Transcriber -> Levy -> damped deterministic recombine.
# Speculative modeling only. No engineering, flight, siting, power or operational claims.
"""Guidance variants on the no-track pad ascent (and light-sail where relevant).

Speculative modeling only. Not an engineering design, flight plan, or siting
recommendation. No operational claims. No vendor or facility specs.

Variants, all on the recycled hollow-bone dart, conjunctive Oroboro loop,
best-azimuth / geography rotation at burnout, residual to 200 km circular:

1. Plain kite (free and tethered).
2. Fishing-line (long thin tensioned line that damps heading waste).
3. Car-style lane-keeping with Nexus path register, damped delta
   reconciliation, Levy-weighted corrections, Oasis/PrinciplesGate
   admission, and NaCl consensus over noisy path-sensor votes.
4. Smart-magnet lane-keeping against Earth's field only (~25-65 µT).
5. STRAW: a continuous guided channel whose wall is a magnet reaction
   surface (effectively a very tall track).

Lock: residual <= 1 m/s and perigee >= 200 km.
Baseline: recycled no-track (0/240 locks; drag/heating binding).

The queued Pixar fur/fabric follow-up is not started here.
"""
from __future__ import annotations

import json
import math
import random
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

OUT = G.OUT
MU, RE, G_STD = G.MU_EARTH, G.R_EARTH, G.G_STD
LEO, KARMAN = G.LEO_ALT_M, G.KARMAN_M
MU0 = 4.0e-7 * math.pi
# Dipole equatorial surface field, labeled order for the 25-65 µT range.
B0_EQ_T = 30e-6

LEVY = {
    "genesis": 0, "admit_path": 1, "suppress_path": 2, "correct": 4,
    "orbit_lock": 14, "fail": 2, "cut_tether": 7, "straw_exit": 4,
    "damper_reconcile": 4,
}


def earth_B_T(lat_deg, h_m):
    """Dipole order: |B| = B0 (R/(R+h))^3 * sqrt(1+3 sin^2 lat). Labeled."""
    lat = math.radians(lat_deg)
    r = RE + max(0.0, h_m)
    return B0_EQ_T * (RE / r) ** 3 * math.sqrt(1.0 + 3.0 * math.sin(lat) ** 2)


def earth_dBdr_T_per_m(lat_deg, h_m):
    B = earth_B_T(lat_deg, h_m)
    r = RE + max(0.0, h_m)
    return -3.0 * B / r


def kepler_after_burnout(h, v_rel, gamma_deg, lat_deg, az_deg):
    v_i, g_i, boost, v_h_i, vr = R.release_with_azimuth(v_rel, gamma_deg, h, lat_deg, az_deg)
    kep, res, vac = R.kepler_vac(h, v_i, g_i)
    peri = kep.get("h_perigee_m") if kep else None
    apo = kep.get("h_apogee_m") if kep else None
    return {
        "v_inertial_m_s": v_i, "gamma_inertial_deg": g_i, "boost_m_s": boost,
        "residual_m_s": res,
        "apogee_km": None if apo is None else apo / 1000.0,
        "perigee_km": None if peri is None else peri / 1000.0,
        "locked": bool(res is not None and res <= 1.0 and peri is not None and peri >= LEO),
        "kepler": kep,
    }


def dart_inertia(mass, diameter, ld=15.0):
    L = diameter * ld
    # slender rod about a transverse axis through the center, labeled.
    I = mass * L * L / 12.0
    return I, L


# ----- reference paths (Nexus-registered, user-drawn or open-loop) -----

def path_loft_steep(s_m, h0=0.0, h_end=80_000.0, s_end=40_000.0):
    """Steeper user-drawn loft: reach h_end in s_end downrange (quarter-cosine)."""
    frac = min(1.0, max(0.0, s_m / max(s_end, 1.0)))
    h = h0 + (h_end - h0) * math.sin(0.5 * math.pi * frac)
    # slope dh/ds
    dfrac = 1.0 / max(s_end, 1.0)
    dhds = (h_end - h0) * 0.5 * math.pi * math.cos(0.5 * math.pi * frac) * dfrac
    pitch = math.atan2(dhds, 1.0)  # from local horizontal, in the plane
    return h, pitch


def path_loft_shallow(s_m, h0=0.0, h_end=80_000.0, s_end=120_000.0):
    frac = min(1.0, max(0.0, s_m / max(s_end, 1.0)))
    h = h0 + (h_end - h0) * math.sin(0.5 * math.pi * frac)
    dfrac = 1.0 / max(s_end, 1.0)
    dhds = (h_end - h0) * 0.5 * math.pi * math.cos(0.5 * math.pi * frac) * dfrac
    pitch = math.atan2(dhds, 1.0)
    return h, pitch


def openloop_pitch(h, h0, tower_m=100.0, kick_deg=5.0):
    if h - h0 < tower_m:
        return math.pi / 2.0
    frac = min(1.0, max(0.0, (h - h0 - tower_m) / 40_000.0))
    return math.radians(90.0 - kick_deg) * (1.0 - frac) + math.radians(5.0) * frac


# ----- unified ascent -----

def integrate_guided(
    h0, m0, fp, isp, area, cd, tw0=3.0, kick_deg=5.0, tower_m=100.0,
    dt=0.05, t_max=1500.0, mode="baseline", lat_deg=5.2372,
    params=None, seed=0,
):
    """Co-rotating / air-rest pad ascent with a guidance plugin.

    Thrust, gravity, and body drag as in the recycled no-track integrator.
    Extra forces and a pitch override come from the mode.
    """
    P = params or {}
    rng = random.Random(seed)
    fp_ascent = max(0.0, min(0.95, fp))
    if fp_ascent <= 0 or m0 <= 0:
        return {"ok": False, "reason": "no_ascent_propellant"}
    # dry / wet
    extra_mass = P.get("extra_mass_kg", 0.0)
    m0_tot = m0 + extra_mass
    T = tw0 * m0 * G_STD  # thrust from the dart's T/W, labeled (not from kite mass)
    ve = isp * G_STD
    mdot = T / ve
    m_prop = fp_ascent * m0
    m = m0_tot
    r0 = RE + max(0.0, h0)
    x, y = 0.0, r0
    vx, vy = 0.0, 0.0
    # out-of-plane (cross-track) for line / lane metrics; starts at 0 plus a
    # labeled initial heading error if requested.
    z = 0.0
    vz = 0.0
    t = 0.0
    h_max = max(0.0, h0)
    peak_q = peak_qsg = peak_Teq = 0.0
    g_loss = d_loss = lift_impulse = 0.0
    line_drag_loss = 0.0
    t_burn_end = None
    burned = 0.0
    burnout = None
    apogee = None
    peaked_tension = 0.0
    t_cut = None
    tether_cut = False
    n_sense = n_commit = n_buffer = n_block = n_levy = 0
    effort = 0.0
    cosine_waste = 0.0  # integral (1 - tdir·program) * dt while thrusting
    xt_abs_max = 0.0
    xt_int = 0.0
    peak_lift = peak_kite_drag = 0.0
    contain_ok = True
    lane_half_m = P.get("lane_half_m", 500.0)
    straw_half_m = P.get("straw_half_m", 5.0)
    I_spin, L_dart = dart_inertia(m0, P.get("diameter_m", 0.0873))
    att = 0.0  # body pitch error vs commanded, for magnetorquer slew, rad
    att_rate = 0.0
    magnet_dv = 0.0
    peak_tau = 0.0
    peak_Fmag = 0.0
    in_straw = mode.startswith("straw")
    straw_h_end = P.get("straw_h_m", 80_000.0)
    straw_evac = bool(P.get("straw_evac", False))
    path_name = P.get("path", "openloop")
    kite_open = True
    notes = []

    def local_basis(xx, yy):
        r = math.hypot(xx, yy)
        urx, ury = xx / r, yy / r
        uhx, uhy = ury, -urx
        return r, urx, ury, uhx, uhy

    while t < t_max:
        r, urx, ury, uhx, uhy = local_basis(x, y)
        if r < 1.0:
            notes.append("center")
            break
        h = r - RE
        if h < -10.0 and t > 1.0:
            notes.append("impact")
            break
        # downrange arc along the surface
        s = r0 * math.atan2(x, y) if (x or y) else 0.0
        speed = math.hypot(vx, vy)
        vr = vx * urx + vy * ury
        vt = vx * uhx + vy * uhy
        gamma = math.atan2(vr, vt) if (abs(vt) > 1e-9 or abs(vr) > 1e-9) else math.pi / 2.0

        # atmosphere: inside an evacuated straw, rho = 0
        inside_evac = bool(in_straw and straw_evac and h < straw_h_end and not tether_cut
                           and (P.get("straw_until", "altitude") == "altitude"))
        if inside_evac:
            rho = 0.0
        else:
            rho = G.rho_isa(max(0.0, h))
        q = 0.5 * rho * speed * speed
        qsg = G.sutton_graves_q(rho, speed)
        Teq = G.T_eq_radiation(qsg)
        peak_q = max(peak_q, q)
        peak_qsg = max(peak_qsg, qsg)
        peak_Teq = max(peak_Teq, Teq)
        gacc = MU / (r * r)
        gx, gy = -gacc * x / r, -gacc * y / r

        # body drag
        dx = dy = dz = 0.0
        if speed > 1e-6 and m > 0 and rho > 0:
            Fd = 0.5 * cd * rho * area * speed * speed
            dx, dy = -Fd / m * vx / speed, -Fd / m * vy / speed
            d_loss += (Fd / m) * dt

        # --- kite ---
        lx = ly = 0.0
        if mode in ("kite_free", "kite_tether") and kite_open:
            S = P.get("kite_area_m2", 10.0)
            CL = P.get("CL", 0.8)
            CD = P.get("CD", 0.25)
            if speed > 5.0 and rho > 0 and m > 0:
                # lift direction: 90° from velocity toward local zenith
                vhx, vhy = vx / speed, vy / speed
                zdotv = urx * vhx + ury * vhy
                px, py = urx - zdotv * vhx, ury - zdotv * vhy
                pn = math.hypot(px, py)
                if pn > 1e-9:
                    px, py = px / pn, py / pn
                    L = 0.5 * rho * speed * speed * S * CL
                    D = 0.5 * rho * speed * speed * S * CD
                    peak_lift = max(peak_lift, L)
                    peak_kite_drag = max(peak_kite_drag, D)
                    load = L + D
                    q_reef = P.get("kite_q_reef_Pa", 1500.0)
                    load_cap = P.get("kite_load_cap_N", 5.0e3)
                    if q > q_reef or load > load_cap:
                        kite_open = False
                        notes.append("kite_reefed")
                    else:
                        lx += (L * px - D * vhx) / m
                        ly += (L * py - D * vhy) / m
                        d_loss += (D / m) * dt
                        lift_impulse += L * dt
            if mode == "kite_tether" and not tether_cut:
                L_t = P.get("tether_m", 5000.0)
                # anchor at the pad (0, r0)
                ax_, ay_ = 0.0, r0
                rx, ry = x - ax_, y - ay_
                dist = math.hypot(rx, ry)
                if dist > L_t and dist > 1.0:
                    # stiff constraint spring (labeled), then cut if tension exceeds cap
                    k_s = P.get("tether_k_N_m", 2.0e3)
                    stretch = dist - L_t
                    tens = k_s * stretch
                    peaked_tension = max(peaked_tension, tens)
                    cap = P.get("tether_cap_N", 5.0e4)
                    if tens > cap:
                        tether_cut = True
                        t_cut = t
                        kite_open = P.get("keep_kite_after_cut", True)
                    else:
                        fx, fy = -tens * rx / dist, -tens * ry / dist
                        lx += fx / m
                        ly += fy / m
                # if the line is fully paid out almost vertically and we still climb, cut at 80° from pad
                if dist > 0.98 * L_t:
                    el = math.asin(max(-1.0, min(1.0, (y - ay_) / dist)))
                    if el > math.radians(75.0) and h > 0.7 * L_t:
                        tether_cut = True
                        t_cut = t

        # --- fishing line (trailing / tensioned damper + cylinder drag) ---
        if mode == "fishing" and h >= P.get("line_deploy_h_m", 0.0):
            L_line = P.get("line_m", 200.0)
            d_line = P.get("line_d_m", 0.001)
            if speed > 1e-6 and rho > 0 and m > 0:
                # cylinder cross-flow drag on the exposed length (labeled Cd~1)
                A_line = L_line * d_line
                Fd_l = 0.5 * 1.0 * rho * A_line * speed * speed
                dx -= (Fd_l / m) * vx / speed
                dy -= (Fd_l / m) * vy / speed
                line_drag_loss += (Fd_l / m) * dt
                d_loss += (Fd_l / m) * dt
            # oscillating restoring on out-of-plane error (and a small in-plane heading dither
            # that damps deviation from the open-loop pitch program)
            k_line = P.get("line_k_N_m", 2.0)
            c_line = P.get("line_c_N_s_m", 8.0)
            # a slow oscillation of the effective rest angle, labeled 0.5 Hz, amplitude 2°
            osc = math.radians(P.get("osc_amp_deg", 2.0)) * math.sin(2.0 * math.pi * P.get("osc_hz", 0.5) * t)
            # cross-track spring
            Fz = -k_line * z - c_line * vz
            dz += Fz / m if m > 0 else 0.0
            # in-plane: a small restoring toward open-loop pitch, dithered
            # applied later as a pitch bias
            P["_fish_bias"] = osc

        # --- magnet force (Earth field only) ---
        moment = P.get("moment_A_m2", 0.0)
        if moment and mode in ("magnet_force", "magnet_torque", "lane_magnet"):
            B = earth_B_T(lat_deg, h)
            dBdr = earth_dBdr_T_per_m(lat_deg, h)
            Fmag = abs(moment * dBdr)  # gradient force, cannot exceed this order
            peak_Fmag = max(peak_Fmag, Fmag)
            # direction is radial (dipole gradient); this is NOT a lane force
            if mode == "magnet_force" and m > 0:
                lx += (Fmag / m) * urx * (1.0 if dBdr < 0 else -1.0)
                ly += (Fmag / m) * ury * (1.0 if dBdr < 0 else -1.0)
                magnet_dv += (Fmag / m) * dt
            tau = abs(moment * B)
            peak_tau = max(peak_tau, tau)
            if mode in ("magnet_torque", "lane_magnet") and I_spin > 0:
                # torque can slew attitude toward a commanded pitch; no net force
                # α = τ/I, limited
                pass  # applied after command is known

        # --- commanded pitch ---
        thrusting = burned < m_prop - 1e-12
        cmd = openloop_pitch(h, h0, tower_m, kick_deg)
        xt = 0.0  # signed cross-track of the registered path (altitude error at this s)
        if path_name == "steep":
            h_ref, p_ref = path_loft_steep(max(0.0, s), h0, P.get("path_h_m", 80_000.0),
                                           P.get("path_s_m", 40_000.0))
            xt = h - h_ref
            if mode.startswith("lane") or mode in ("magnet_torque", "lane_magnet"):
                cmd = p_ref
        elif path_name == "shallow":
            h_ref, p_ref = path_loft_shallow(max(0.0, s), h0, P.get("path_h_m", 80_000.0),
                                             P.get("path_s_m", 120_000.0))
            xt = h - h_ref
            if mode.startswith("lane") or mode in ("magnet_torque", "lane_magnet"):
                cmd = p_ref
        else:
            h_ref = None
            # open-loop path has no spatial register other than the pitch program
            xt = z  # out-of-plane only

        # fishing-line heading damper toward cmd
        if mode == "fishing":
            cmd = cmd + P.get("_fish_bias", 0.0)
            # additional small gain on gamma error (damped)
            err_g = gamma - cmd
            cmd = cmd - 0.15 * err_g

        # harmful-style closed-loop: slave gamma to a coarse h-schedule (recycled idea)
        if mode == "lane_harmful" and thrusting:
            n_sense += 1
            if h > 80000:
                g_tgt = math.radians(2.0)
            elif h > 40000:
                g_tgt = math.radians(8.0)
            else:
                g_tgt = math.radians(15.0)
            # plus a 1-deg-order noise
            g_hat = gamma + rng.gauss(0, math.radians(0.8))
            err = g_hat - g_tgt
            dgamma = max(-math.radians(2.0), min(math.radians(2.0), -0.4 * err))
            if q > 50e3:
                dgamma *= 0.2
            cmd = max(0.0, min(math.pi / 2.0, (gamma + dgamma)))
            n_commit += 1
            effort += abs(dgamma)

        # gated Oroboro lane-keeping
        if mode in ("lane_gated", "lane_magnet") and thrusting:
            n_sense += 1
            # NaCl-style votes: 3 noisy measurements of cross-track (or of gamma
            # vs path pitch). Median consensus. Labeled 1-sigma 5 m / 0.8 deg.
            if h_ref is not None:
                votes = [xt + rng.gauss(0, 5.0) for _ in range(3)]
            else:
                votes = [math.degrees(gamma - cmd) + rng.gauss(0, 0.8) for _ in range(3)]
                # interpret as an angle error, convert to a pseudo cross-track
            votes.sort()
            hat = votes[1]
            spread = votes[2] - votes[0]
            # invert-and-restabilize: if one vote is an extreme outlier vs the
            # other two, drop it (already using median).
            if h_ref is not None:
                err = hat  # meters
                err_n = min(1.0, abs(err) / max(lane_half_m, 1.0))
            else:
                err = math.radians(hat)
                err_n = min(1.0, abs(err) / math.radians(15.0))
            novelty = err_n
            tension = min(1.0, q / 50e3)
            coherence = max(0.0, 1.0 - (spread / (15.0 if h_ref is not None else 5.0)))
            levy = 0.25 + 0.75 * err_n * (0.5 + 0.5 * tension)
            S = 0.30 * novelty + 0.25 * tension + 0.25 * coherence + 0.20 * levy
            # PrinciplesGate-like: do not write a world-changing steer if
            # salience is in the buffer only, or if q is in a danger band
            if S < 0.325:
                n_block += 1
            else:
                n_buffer += 1
                if S >= 0.65 or levy > 0.7:
                    n_commit += 1
                    if levy > 0.7:
                        n_levy += 1
                    # damped delta: correct a fraction of the pitch error, clipped
                    if h_ref is not None:
                        # convert altitude error to a pitch correction: if too low, pitch up
                        dgamma = 0.25 * math.atan2(err, 2000.0) * (-1.0)  # too high (xt>0) => pitch down
                    else:
                        dgamma = -0.25 * err
                    cap = math.radians(P.get("dgamma_max_deg", 1.5))
                    dgamma = max(-cap, min(cap, dgamma))
                    if q > 50e3:
                        dgamma *= 0.2
                    cmd = max(0.0, min(math.pi / 2.0, cmd + dgamma))
                    effort += abs(dgamma)
                else:
                    n_block += 1

        # straw containment: if open or evac, walls react (no aero change except evac rho)
        if in_straw and h < straw_h_end:
            # force the flight-path toward the registered path; walls do the reaction
            if path_name in ("steep", "shallow"):
                cmd = p_ref if 'p_ref' in dir() else cmd
            # cross-track vs path; if |xt| would exceed the straw radius, a wall force
            # (evac or open) returns the vehicle — labeled as perfect containment
            # within straw_half_m when "in" the channel.
            if h_ref is not None and abs(xt) > straw_half_m:
                # reflect the radial-path error by a restoring acceleration
                # (the wall), capped
                a_wall = max(-200.0, min(200.0, -20.0 * (xt - math.copysign(straw_half_m, xt))))
                # apply along local zenith (altitude error)
                lx += a_wall * urx
                ly += a_wall * ury
                contain_ok = contain_ok and (abs(xt) < 5.0 * straw_half_m)
            if h >= straw_h_end - 1.0:
                in_straw = False
                notes.append("straw_exit")

        # magnetorquer slew of attitude toward cmd (torque-only lane)
        if mode in ("magnet_torque", "lane_magnet") and moment:
            B = earth_B_T(lat_deg, h)
            tau = abs(moment * B)
            peak_tau = max(peak_tau, tau)
            # desired att = 0 when body matches cmd; err = att (body) vs 0 after we
            # set the command as the target. Track att as body_pitch - cmd.
            # Simpler: slew body toward cmd at limited angular accel tau/I.
            body = cmd + att
            # spring the error with available alpha
            alpha_max = tau / max(I_spin, 1e-9)
            # need att -> 0, att_rate
            # bang-bang toward reducing att
            if att > 0:
                alpha = -alpha_max
            elif att < 0:
                alpha = alpha_max
            else:
                alpha = 0.0
            att_rate += alpha * dt
            # clamp rate at a modest value
            att_rate = max(-0.2, min(0.2, att_rate))
            att += att_rate * dt
            body = cmd + att
            cmd_used = body
        else:
            cmd_used = cmd

        # never thrust below local horizontal
        cmd_used = max(0.0, min(math.pi / 2.0, cmd_used))

        tx = ty = 0.0
        if thrusting:
            tdirx = urx * math.sin(cmd_used) + uhx * math.cos(cmd_used)
            tdiry = ury * math.sin(cmd_used) + uhy * math.cos(cmd_used)
            if tdirx * urx + tdiry * ury < 0:
                tdirx, tdiry = uhx, uhy
            tx, ty = (T / m) * tdirx, (T / m) * tdiry
            # program direction (open-loop) for effort/waste
            p0 = openloop_pitch(h, h0, tower_m, kick_deg)
            pdx = urx * math.sin(p0) + uhx * math.cos(p0)
            pdy = ury * math.sin(p0) + uhy * math.cos(p0)
            dot = max(-1.0, min(1.0, tdirx * pdx + tdiry * pdy))
            cosine_waste += max(0.0, 1.0 - dot) * dt
            if speed > 1e-6:
                g_along = -(gx * vx + gy * vy) / speed
                g_loss += max(0.0, g_along) * dt
            dm = min(mdot * dt, m_prop - burned)
            m -= dm
            burned += dm
            if burned >= m_prop - 1e-12 and t_burn_end is None:
                t_burn_end = t
                burnout = {
                    "t_s": t, "h_m": h, "v_m_s": speed,
                    "gamma_deg": math.degrees(gamma),
                    "mass_kg": m, "s_m": s,
                }

        ax = gx + dx + tx + lx
        ay = gy + dy + ty + ly
        vx += ax * dt
        vy += ay * dt
        vz += dz * dt
        x += vx * dt
        y += vy * dt
        z += vz * dt
        t += dt
        xt_abs_max = max(xt_abs_max, abs(xt if path_name != "openloop" else z))
        xt_int += abs(xt if path_name != "openloop" else z) * dt
        r2 = math.hypot(x, y)
        h2 = r2 - RE
        if h2 > h_max:
            h_max = h2
            _, ur2x, ur2y, uh2x, uh2y = local_basis(x, y)
            speed2 = math.hypot(vx, vy)
            vr2 = vx * ur2x + vy * ur2y
            vt2 = vx * uh2x + vy * uh2y
            apogee = {
                "t_s": t, "h_m": h2, "v_m_s": speed2,
                "gamma_deg": math.degrees(math.atan2(vr2, vt2)) if (abs(vt2) > 1e-9 or abs(vr2) > 1e-9) else 0.0,
            }
        if (not thrusting) and h2 < 0 and t > 1.0:
            break
        if (not np.isfinite(x)) or speed > 20000:
            notes.append("unphysical")
            break

    if burnout is None and burned > 0:
        r, urx, ury, uhx, uhy = local_basis(x, y)
        h = r - RE
        speed = math.hypot(vx, vy)
        vr = vx * urx + vy * ury
        vt = vx * uhx + vy * uhy
        burnout = {
            "t_s": t, "h_m": h, "v_m_s": speed,
            "gamma_deg": math.degrees(math.atan2(vr, vt)) if (abs(vt) > 1e-9 or abs(vr) > 1e-9) else 0.0,
            "mass_kg": m, "s_m": r0 * math.atan2(x, y) if (x or y) else 0.0,
        }

    return {
        "ok": True, "mode": mode, "path": path_name,
        "h_max_m": h_max, "burnout": burnout, "apogee": apogee,
        "t_s": t, "t_burn_s": t_burn_end if t_burn_end is not None else t,
        "mass_end_kg": m, "burned_kg": burned, "fp_ascent": fp_ascent,
        "peak_q_pa": peak_q, "peak_sutton_graves_W_m2": peak_qsg, "peak_Teq_K": peak_Teq,
        "gravity_loss_m_s": g_loss, "drag_loss_m_s": d_loss,
        "line_drag_loss_m_s": line_drag_loss, "lift_impulse_N_s": lift_impulse,
        "peak_lift_N": peak_lift, "peak_kite_drag_N": peak_kite_drag,
        "peak_tension_N": peaked_tension, "t_cut_s": t_cut, "tether_cut": tether_cut,
        "n_sense": n_sense, "n_commit": n_commit, "n_buffer": n_buffer,
        "n_block": n_block, "n_levy": n_levy,
        "effort_rad_s": effort, "cosine_waste_s": cosine_waste,
        "xt_abs_max_m": xt_abs_max, "xt_int_m_s": xt_int,
        "contain_ok": contain_ok, "lane_half_m": lane_half_m,
        "peak_tau_N_m": peak_tau, "peak_Fmag_N": peak_Fmag, "magnet_dv_m_s": magnet_dv,
        "reached_karman": h_max >= KARMAN, "reached_200km": h_max >= LEO,
        "notes": notes, "extra_mass_kg": extra_mass,
    }


def close_with_site(ascent, site, az_deg=90.0):
    bo = ascent.get("burnout")
    if not bo:
        return {**ascent, "residual_m_s": None, "locked": False, "h_max_km": ascent.get("h_max_m", 0) / 1000.0}
    orb = kepler_after_burnout(bo["h_m"], bo["v_m_s"], bo["gamma_deg"], site["lat"], az_deg)
    return {
        **{k: v for k, v in ascent.items() if k != "burnout" and k != "apogee"},
        "h_max_km": ascent["h_max_m"] / 1000.0,
        "h_burnout_km": bo["h_m"] / 1000.0,
        "v_burnout_m_s": bo["v_m_s"],
        "gamma_burnout_deg": bo["gamma_deg"],
        "mass_burnout_kg": bo["mass_kg"],
        **orb,
        "momentum_kg_m_s": bo["mass_kg"] * orb["v_inertial_m_s"],
        "site_id": site["id"], "az_deg": az_deg,
    }


def straw_geometry():
    """Honest extent of a ground-to-sky channel vs the recycled evac tube."""
    evac_flatten_km = 767.6248133925062  # recycled 17,000 mph, 45→5°, evac to 80 km, 1000 g
    # acceleration distance to circular speed at T/W=3, no drag, labeled
    v_c = G.V_CIRC_200KM
    a = 3.0 * G_STD
    s_acc_200 = (v_c ** 2) / (2.0 * a)
    rows = []
    for name, h, shape, length in (
        ("vertical_80km", 80e3, "vertical", 80e3),
        ("vertical_200km", 200e3, "vertical", 200e3),
        ("flatten_45_to_5_80km_recycled_evac", 80e3, "flatten_45_to_5", evac_flatten_km * 1000.0),
        ("steep_user_path_80km_in_40km", 80e3, "quarter_sine_40km", math.hypot(40e3, 80e3)),  # lower bound chord
        ("acc_distance_to_200km_circ_TW3_vacuum", 200e3, "in_channel_accel", s_acc_200),
    ):
        rows.append({
            "name": name, "exit_alt_km": h / 1000.0, "shape": shape,
            "length_km": length / 1000.0,
            "vs_evac_flatten_80km": (length / 1000.0) / evac_flatten_km,
            "evacuated_removes_drag_heat": True,
            "open_air_leaves_drag_heat": True,
        })
    # path length of the quarter-sine steep path (integrate)
    s_end, h_end = 40e3, 80e3
    acc = 0.0
    prev = None
    for i in range(401):
        s = s_end * i / 400
        frac = s / s_end
        hh = h_end * math.sin(0.5 * math.pi * frac)
        if prev:
            acc += math.hypot(s - prev[0], hh - prev[1])
        prev = (s, hh)
    rows.append({
        "name": "steep_user_path_80km_arc_length",
        "exit_alt_km": 80.0, "shape": "quarter_sine_40km_arc",
        "length_km": acc / 1000.0,
        "vs_evac_flatten_80km": (acc / 1000.0) / evac_flatten_km,
        "evacuated_removes_drag_heat": True,
        "open_air_leaves_drag_heat": True,
    })
    return {
        "evac_flatten_45_to_5_80km_km": evac_flatten_km,
        "note": ("The recycled evac tube that delivered the 17,000 mph / 5° / 80 km "
                 "exit was 767.6 km long. A STRAW is a built channel of comparable "
                 "kind: its length is the path length, not a free field. Magnetic "
                 "walls do not remove air; only an evacuated channel removes "
                 "drag/heating inside. A vacuum acceleration to 7,788 m/s at T/W=3 "
                 "already needs about 1,030 km of path, before gravity losses."),
        "rows": rows,
        "s_acc_200km_TW3_vacuum_km": s_acc_200 / 1000.0,
    }


def magnet_table(lat_deg, diameter_m, mass):
    I, L = dart_inertia(mass, diameter_m)
    rows = []
    for moment in (1.0, 10.0, 100.0, 1000.0):
        for h in (0.0, 80e3, 200e3):
            B = earth_B_T(lat_deg, h)
            dBdr = earth_dBdr_T_per_m(lat_deg, h)
            tau = moment * B
            F = abs(moment * dBdr)
            alpha = tau / I
            # time to slew 10 deg from rest, bang-bang half (order)
            theta = math.radians(10.0)
            t_slew = math.sqrt(2.0 * theta / alpha) if alpha > 0 else None
            rows.append({
                "moment_A_m2": moment, "h_km": h / 1000.0, "B_uT": B * 1e6,
                "dBdr_T_m": dBdr, "tau_N_m": tau, "F_N": F,
                "a_trans_m_s2": F / mass, "alpha_rad_s2": alpha,
                "t_slew_10deg_s": t_slew,
                "dv_in_1000s_m_s": (F / mass) * 1000.0,
            })
    return {"I_kg_m2": I, "L_m": L, "mass_kg": mass, "lat_deg": lat_deg, "rows": rows}


def run():
    dart = G.vehicle_from_mass(20.0, hollow_k=0.8, payload_frac=0.30)
    geo = json.loads((OUT / "geography.json").read_text())
    sites = {s["id"]: s for s in geo["sites"]}
    kourou = sites["kourou"]
    gate = core.PrinciplesGate(core.load_config())
    nexus = R.Nexus()
    transcriber = R.Transcriber()
    dictator = R.Dictator(transcriber)
    levy = R.Levy(transcriber)
    def assess(kind, n=1):
        w = LEVY.get(kind, 1) * n
        levy.total += w
        levy.entries.append({"kind": kind, "weight": w})
        return w
    levy.assess = assess
    sim = R.RelationalSim(nexus)
    nexus.register("genesis", {"tag": "I am the OG avatar", "weight": math.inf})
    assess("genesis")
    dictator.stream("genesis", "Guidance kite/line/straw ledger. Recycled no-track baseline; new guidance only.")

    # Admit user-drawn paths (non-zero coordinates). A null path is blocked.
    paths_to_admit = [
        ("openloop", {"x": 5.2372, "y": -52.7681, "z": 0.01}),
        ("steep", {"x": 5.2372, "y": -52.7681, "z": 80.0}),
        ("shallow", {"x": 5.2372, "y": -52.7681, "z": 80.0}),
        ("null", None),
    ]
    path_gate = {}
    for name, posd in paths_to_admit:
        pos = core.vec(posd) if posd else None
        gr = gate.check("CreateAnchor", pos, f"Admit guidance path {name}", utility=0.65)
        path_gate[name] = {"allowed": bool(gr.allowed), "principle": gr.principle}
        if gr.allowed:
            assess("admit_path")
            nexus.register(f"path:{name}", {"pos": posd})
        else:
            assess("suppress_path")
            dictator.stream("suppress_path", f"Blocked path {name}: {gr.principle}")

    isp, tw0 = 450.0, 3.0
    fps = (0.30, 0.85)
    # best-az on a no-track burnout is approximately due-east at Kourou (low lat).
    # Recycle due-east as the geography boost at burnout, consistent with the
    # no-track baseline. (Redstone best-az was for high-altitude rail exits.)
    az = 90.0

    cases = []

    def add(label, mode, fp, params, seed=1):
        extra = 0.0
        if mode in ("kite_free", "kite_tether"):
            extra = params.get("kite_area_m2", 10.0) * params.get("kite_sigma_kg_m2", 0.05)
        params = dict(params or {})
        params["extra_mass_kg"] = extra
        params["diameter_m"] = dart["diameter_m"]
        rec = integrate_guided(
            0.0, dart["mass"], fp, isp, dart["area"], dart["cd"],
            tw0=tw0, mode=mode, lat_deg=kourou["lat"], params=params, seed=seed,
        )
        closed = close_with_site(rec, kourou, az)
        closed["label"] = label
        closed["fp"] = fp
        closed["params"] = {k: v for k, v in params.items() if k != "_fish_bias"}
        if closed.get("locked"):
            assess("orbit_lock")
        else:
            assess("fail")
        cases.append(closed)
        return closed

    # Baseline (confirms recycled no-track)
    for fp in fps:
        add(f"baseline_fp{fp}", "baseline", fp, {"path": "openloop"})

    # Kite free and tethered
    for fp in fps:
        for area, sig in ((2.0, 0.05), (10.0, 0.05), (50.0, 0.05)):
            add(f"kite_free_A{area:g}_fp{fp}", "kite_free", fp,
                {"path": "openloop", "kite_area_m2": area, "kite_sigma_kg_m2": sig,
                 "CL": 0.8, "CD": 0.25})
        for L in (2000.0, 8000.0):
            add(f"kite_tether_L{L/1000:g}km_A10_fp{fp}", "kite_tether", fp,
                {"path": "openloop", "kite_area_m2": 10.0, "kite_sigma_kg_m2": 0.05,
                 "CL": 0.8, "CD": 0.25, "tether_m": L, "tether_cap_N": 5.0e4,
                 "keep_kite_after_cut": True})

    # Fishing line
    for fp in fps:
        for L, d, hdep in ((100.0, 0.001, 0.0), (500.0, 0.001, 0.0),
                           (500.0, 0.001, 60_000.0), (1000.0, 0.002, 60_000.0)):
            tag = f"fishing_L{L:g}_d{d}_dep{int(hdep/1000)}km_fp{fp}"
            add(tag, "fishing", fp,
                {"path": "openloop", "line_m": L, "line_d_m": d,
                 "line_deploy_h_m": hdep,
                 "line_k_N_m": 2.0, "line_c_N_s_m": 8.0, "osc_hz": 0.5, "osc_amp_deg": 2.0})

    # Lane-keeping: harmful vs gated, openloop / steep / shallow paths
    for fp in fps:
        add(f"lane_harmful_fp{fp}", "lane_harmful", fp, {"path": "openloop"})
        add(f"lane_gated_openloop_fp{fp}", "lane_gated", fp, {"path": "openloop"})
        if path_gate["steep"]["allowed"]:
            add(f"lane_gated_steep_fp{fp}", "lane_gated", fp,
                {"path": "steep", "path_h_m": 80_000.0, "path_s_m": 40_000.0, "lane_half_m": 500.0})
        if path_gate["shallow"]["allowed"]:
            add(f"lane_gated_shallow_fp{fp}", "lane_gated", fp,
                {"path": "shallow", "path_h_m": 80_000.0, "path_s_m": 120_000.0, "lane_half_m": 500.0})

    # Magnets: force-only, torque-slew on open-loop and on gated steep path
    for fp in fps:
        add(f"magnet_force_m1000_fp{fp}", "magnet_force", fp,
            {"path": "openloop", "moment_A_m2": 1000.0})
        add(f"magnet_torque_m1000_fp{fp}", "magnet_torque", fp,
            {"path": "openloop", "moment_A_m2": 1000.0})
        add(f"lane_magnet_steep_m1000_fp{fp}", "lane_magnet", fp,
            {"path": "steep", "path_h_m": 80_000.0, "path_s_m": 40_000.0,
             "moment_A_m2": 1000.0, "lane_half_m": 500.0})

    # STRAW: open-air vs evacuated, 80 km and 200 km, vertical-ish (steep path)
    for fp in fps:
        for evac, h_s, tag, path in (
            (False, 80e3, "open80_steep", "steep"),
            (True, 80e3, "evac80_steep", "steep"),
            (True, 80e3, "evac80_openloop", "openloop"),
            (False, 200e3, "open200_steep", "steep"),
            (True, 200e3, "evac200_steep", "steep"),
            (True, 200e3, "evac200_openloop", "openloop"),
        ):
            add(f"straw_{tag}_fp{fp}", "straw_open" if not evac else "straw_evac", fp,
                {"path": path, "path_h_m": h_s,
                 "path_s_m": 40_000.0 if h_s <= 80e3 else 60_000.0,
                 "straw_h_m": h_s, "straw_evac": evac, "straw_half_m": 5.0, "lane_half_m": 5.0})

    # Magnet physics table and straw geometry (analytic, honest)
    mag = magnet_table(kourou["lat"], dart["diameter_m"], dart["mass"])
    straw = straw_geometry()

    # Recycle light-sail post-burnout numbers for the baseline and note
    # whether a better burnout would change that leftover. Pull the recycled
    # Kourou f_p=0.85 residual (661 m/s) and the best light-sail cut (514 m/s).
    ls = json.loads((OUT / "light_sail_push.json").read_text())
    nt_src = json.loads((OUT / "redstone_repeater_comparator.json").read_text())["no_track"]
    base_nt = None
    for r in nt_src:
        if (r["vehicle"] == "hollow_dart_12.6kg" and abs(r["fp"] - 0.85) < 1e-9
                and r["tw0"] == 3.0 and r["az_policy"] == "due_east"
                and r["reserve_mode"] == "all_in_ascent" and r["site_id"] == "kourou"
                and r.get("isp_s") == 450):
            base_nt = r
            break
    ls_best = None
    for r in ls.get("no_track") or []:
        if r.get("kind") == "post_burnout_fp085" and r.get("residual_after_m_s") is not None:
            if ls_best is None or r["residual_after_m_s"] < ls_best["residual_after_m_s"]:
                ls_best = {k: r[k] for k in r if k not in ("kepler_after",)}

    # Recombine residuals at f_p=0.85 for the headline variants
    reco = [c["residual_m_s"] for c in cases if c.get("fp") == 0.85 and c.get("residual_m_s") is not None]
    recombine = sim.recombine(reco, damping=0.25)
    assess("damper_reconcile")

    n_lock = sum(1 for c in cases if c.get("locked"))
    # compact cases (drop heavy kepler)
    compact = []
    for c in cases:
        d = {k: v for k, v in c.items() if k not in ("kepler", "params")}
        d["param_brief"] = {k: c["params"][k] for k in c["params"]
                            if k in ("kite_area_m2", "tether_m", "line_m", "line_d_m", "line_deploy_h_m",
                                     "path", "path_h_m", "moment_A_m2", "straw_h_m",
                                     "straw_evac", "extra_mass_kg", "CL", "CD")}
        compact.append(d)

    # efficiency vs baseline at same fp
    baselines = {c["fp"]: c for c in compact if c["label"].startswith("baseline_")}
    for c in compact:
        b = baselines.get(c["fp"])
        if not b or not c.get("v_inertial_m_s") or not b.get("v_inertial_m_s"):
            c["dv_vs_baseline_m_s"] = None
            c["dres_vs_baseline_m_s"] = None
            c["dhmax_km"] = None
            continue
        c["dv_vs_baseline_m_s"] = c["v_inertial_m_s"] - b["v_inertial_m_s"]
        if c["residual_m_s"] is not None and b["residual_m_s"] is not None:
            c["dres_vs_baseline_m_s"] = c["residual_m_s"] - b["residual_m_s"]
        else:
            c["dres_vs_baseline_m_s"] = None
        c["dhmax_km"] = c["h_max_km"] - b["h_max_km"]
        # energy-ish: useful massless specific energy vs baseline
        c["drag_loss_vs_baseline_m_s"] = c["drag_loss_m_s"] - b["drag_loss_m_s"]
        c["grav_loss_vs_baseline_m_s"] = c["gravity_loss_m_s"] - b["gravity_loss_m_s"]

    assumptions = [
        "Speculative modeling only; not an engineering design, flight plan, or siting recommendation.",
        "No-track baseline recycled: 0/240 locks; drag/heating binding. Confirmatory open-loop runs use the same dart, I_sp=450 s, T/W=3, Kourou due-east burnout boost.",
        "Lock means residual <= 1 m/s and perigee >= 200 km.",
        "Kite CL=0.8, CD=0.25, areal density 0.05 kg/m², areas 2/10/50 m² are labeled model values, not materials. Tether cap 50 kN is a labeled line-strength assumption.",
        "Fishing-line diameter 1–2 mm, lengths 100–1000 m, cylinder Cd=1, k=2 N/m, 0.5 Hz / 2° dither are labeled.",
        "Lane-keeping uses the same Oasis buffer 0.325 / commit 0.65 and median-of-three noisy votes as the parent onboard note. The 'harmful' variant slaved flight-path angle to a coarse altitude schedule (the prior closed-loop idea). The gated variant registers a spatial path in Nexus and applies damped, Levy-weighted, q-limited corrections only when the gate commits.",
        "Earth field is a labeled dipole: B0=30 µT at the equator, |B|=B0 (R/r)^3 sqrt(1+3 sin^2 lat), covering the ~25–65 µT surface range. Gradient force F=m|dB/dr| with dB/dr=-3B/r. Dipole moments 1–1000 A·m² are labeled. Magnetorquers produce torque m×B; they do not produce a useful translational force in a nearly uniform field.",
        "STRAW length is a built path length. The recycled evac tube to the 17,000 mph / 5° / 80 km exit was 767.6 km. Magnetic walls are a reaction surface, not a vacuum. Only an evacuated channel removes drag and heating inside.",
        "A second, downrange laser or a Pixar fur/fabric layer was not run here.",
        "No invented vendor, facility, or citation numbers.",
    ]

    payload = {
        "status": "Speculative modeling only. Not an engineering design, flight plan, or siting recommendation.",
        "prepared": "2026-11-27 America/Denver",
        "n_cases": len(compact), "n_locks": n_lock,
        "baseline_recycled_no_track": {
            "locks": "0/240",
            "binding": "thick-air drag and heating",
            "kourou_fp085_residual_m_s": None if not base_nt else base_nt["residual_coast_m_s"],
            "kourou_fp085_h_max_km": None if not base_nt else base_nt["h_max_km"],
            "kourou_fp085_peri_km": None if not base_nt else base_nt["perigee_coast_km"],
            "kourou_fp085_Teq_K": None if not base_nt else base_nt["peak_Teq_K"],
        },
        "light_sail_recycled": ls_best,
        "path_gate": path_gate,
        "magnet_table": mag,
        "straw_geometry": straw,
        "cases": compact,
        "recombine": recombine,
        "levy_total": levy.total,
        "transcriber_n": len(transcriber.chronicles),
        "nexus_n": len(nexus.registry),
        "assumptions": assumptions,
        "dart": {"mass": dart["mass"], "area": dart["area"], "cd": dart["cd"],
                 "diameter_m": dart["diameter_m"]},
    }
    path = OUT / "guidance_kite_line_straw.json"
    path.write_text(json.dumps(payload, default=lambda o: float(o) if isinstance(o, (np.floating,)) else int(o) if isinstance(o, (np.integer,)) else str(o)))
    print("Wrote", path, "cases", len(compact), "locks", n_lock, "levy", levy.total)
    return payload


def make_figure(payload):
    fig, axes = plt.subplots(2, 2, figsize=(11.2, 9.4))
    fig.suptitle("Guidance on the no-track ascent  (speculative modeling only)",
                 fontsize=11, color="#1f3a5f")
    cases = payload["cases"]
    sub = [c for c in cases if abs(c.get("fp", 0) - 0.85) < 1e-12]

    headlines = [
        ("baseline", "baseline_fp0.85", "#1f3a5f"),
        ("kite 10 m²", "kite_free_A10_fp0.85", "#2a7d4f"),
        ("line 500 m\nfrom pad", "fishing_L500_d0.001_dep0km_fp0.85", "#6b4c9a"),
        ("line 500 m\nat 60 km", "fishing_L500_d0.001_dep60km_fp0.85", "#6b4c9a"),
        ("lane\nharmful", "lane_harmful_fp0.85", "#b85c38"),
        ("lane gated\nopen-loop", "lane_gated_openloop_fp0.85", "#b85c38"),
        ("lane gated\nsteep", "lane_gated_steep_fp0.85", "#b85c38"),
        ("magnet\nforce", "magnet_force_m1000_fp0.85", "#7a5c2e"),
        ("straw open\n80 km steep", "straw_open80_steep_fp0.85", "#3a6d8c"),
        ("straw evac\n80 km, program", "straw_evac80_openloop_fp0.85", "#3a6d8c"),
        ("straw evac\n200 km, program", "straw_evac200_openloop_fp0.85", "#3a6d8c"),
    ]
    labs, res, hmax, teq, cols = [], [], [], [], []
    for lab, key, col in headlines:
        c = next((x for x in sub if x["label"] == key), None)
        if not c or c.get("residual_m_s") is None:
            continue
        labs.append(lab); res.append(c["residual_m_s"]); cols.append(col)
        hmax.append(c.get("h_max_km") or 0); teq.append(c.get("peak_Teq_K") or 0)

    ax = axes[0, 0]
    ax.bar(range(len(labs)), res, color=cols)
    ax.set_xticks(range(len(labs)))
    ax.set_xticklabels(labs, fontsize=6.5, rotation=35, ha="right")
    ax.set_ylabel("two-burn residual after burnout (m/s)")
    ax.set_title("A.  Residual, f_p=0.85, T/W=3, Kourou, I_sp=450 s")
    ax.grid(True, axis="y", alpha=0.3)

    ax = axes[0, 1]
    x = np.arange(len(labs))
    ax.bar(x - 0.2, hmax, 0.4, color="#1f3a5f", label="h_max (km)")
    ax2 = ax.twinx()
    ax2.bar(x + 0.2, teq, 0.4, color="#b85c38", label="peak T_eq (K)")
    ax.axhline(100, color="k", ls="--", lw=0.7)
    ax.axhline(200, color="k", ls=":", lw=0.7)
    ax2.axhline(803, color="#8a1f1f", ls="--", lw=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(labs, fontsize=6.5, rotation=35, ha="right")
    ax.set_ylabel("max altitude (km)")
    ax2.set_ylabel("peak radiation-equilibrium T (K)")
    ax.set_title("B.  Max altitude and heating (same cut)")
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, fontsize=6.5, loc="upper left")
    ax.grid(True, axis="y", alpha=0.3)

    ax = axes[1, 0]
    # a few labeled points only
    show = {
        "baseline_fp0.85": "baseline",
        "lane_harmful_fp0.85": "harmful γ-law",
        "lane_gated_openloop_fp0.85": "gated, open-loop path",
        "lane_gated_steep_fp0.85": "gated, steep path",
        "fishing_L500_d0.001_dep0km_fp0.85": "line from pad",
        "fishing_L500_d0.001_dep60km_fp0.85": "line at 60 km",
        "magnet_torque_m1000_fp0.85": "magnet torque",
    }
    for c in sub:
        if c["label"] not in show or c.get("dres_vs_baseline_m_s") is None:
            continue
        ax.scatter(c.get("effort_rad_s") or 0.0, c["dres_vs_baseline_m_s"], s=32, zorder=3, color="#1f3a5f")
        ax.annotate(show[c["label"]], (c.get("effort_rad_s") or 0.0, c["dres_vs_baseline_m_s"]),
                    fontsize=7, xytext=(4, 4), textcoords="offset points")
    ax.axhline(0.0, color="k", lw=0.7)
    ax.set_xlabel("control effort (integrated |Δpitch|, rad)")
    ax.set_ylabel("residual minus baseline (m/s); negative is better")
    ax.set_title("C.  Control effort vs leftover change, f_p=0.85")
    ax.grid(True, alpha=0.3)

    ax = axes[1, 1]
    geo = payload["straw_geometry"]
    want = [
        ("vertical_80km", "vertical\n80 km"),
        ("vertical_200km", "vertical\n200 km"),
        ("steep_user_path_80km_arc_length", "steep path\nto 80 km"),
        ("flatten_45_to_5_80km_recycled_evac", "evac tube\n45°→5°, 80 km"),
        ("acc_distance_to_200km_circ_TW3_vacuum", "vacuum path to\ncircular, T/W=3"),
    ]
    xs, ys = [], []
    for i, (name, lab) in enumerate(want):
        r = next((row for row in geo["rows"] if row["name"] == name), None)
        if not r:
            continue
        xs.append(i); ys.append(r["length_km"])
    colors = ["#3a6d8c", "#3a6d8c", "#3a6d8c", "#1f3a5f", "#b85c38"]
    ax.bar(xs, ys, color=colors[:len(xs)])
    ax.set_xticks(xs)
    ax.set_xticklabels([lab for _, lab in want], fontsize=7)
    ax.set_ylabel("channel / path length (km)")
    ax.set_title("D.  STRAW extent vs the recycled evac tube")
    ax.axhline(geo["evac_flatten_45_to_5_80km_km"], color="#1f3a5f", ls="--", lw=0.8)
    ax.grid(True, axis="y", alpha=0.3)

    fig.tight_layout(rect=[0, 0.01, 1, 0.94], w_pad=2.0, h_pad=1.8)
    path = OUT / "fig13_guidance_kite_line_straw.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    print("Wrote", path)
    return str(path)




if __name__ == "__main__":
    payload = run()
    make_figure(payload)
