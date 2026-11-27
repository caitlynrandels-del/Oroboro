#!/usr/bin/env python3
# NON-CONJUNCTIVE (audit 2026-11-27): Oasis-STYLE search utility + a compact onboard loop (votes/median consensus, Levy, Oasis commit) that is conjunctive among those four only; Genesis, Dictator, Transcriber, PrinciplesGate and the NaCl mesh are not in the flight integrator.
# Kept for history; results are pre-integration. The conjunctive baseline (all Oroboro
# components on one loop) is research/metastasis-native (integrated=True) and
# research/cross-domain/scripts/run_conjunctive_check.py; an integrated launch rebuild is pending.
# Speculative modeling only. No engineering, flight or operational claims.
"""Recycle ledger + goal-seeking search + onboard autonomy layer.

Settled prior results are cached and not re-run. Capped climbs that were still
accelerating are treated as undetermined and re-run uncapped. New configs are
scaled freely (materials, mass, g, altitude, evac tube, geometry, upper stage).
Onboard closed-loop vs no-control is compared only on the best frontier flights.

Speculative modeling only. No operational claims.
"""
from __future__ import annotations

import json
import math
import hashlib
import random
import statistics
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

# --- well-known constants ---
G_STD = 9.80665
MU_EARTH = 3.986004418e14
R_EARTH = 6.371e6
RHO0 = 1.225
H_SCALE = 8500.0          # ASSUMPTION: isothermal scale height, m
KARMAN_M = 100_000.0
LEO_ALT_M = 200_000.0     # ASSUMPTION: residual reference
MPH = 0.44704
V_CIRC_200KM = math.sqrt(MU_EARTH / (R_EARTH + LEO_ALT_M))  # 7788.488... m/s
PULSE_ON = 0.40
PULSE_OFF = 0.40
T_PULSE = PULSE_ON + PULSE_OFF
BOWL_R = 2500.0           # same assumed bowl radius as the parent run

# recycled damper (from parent run, not re-computed)
DAMPER_T_10HZ = 0.020202
DAMPER_T_PULSE = None  # filled at startup: T at 1/T_PULSE

# labeled material / stage assumptions (not vendor specs)
RHO_CFRP = 1600.0         # kg/m3, typical CFRP-order density (assumption)
RHO_ALLI = 2700.0         # kg/m3, Al-Li-order density (assumption)
CD_DART = 0.20            # slender dart Cd (assumption)
LD_DART = 15.0            # length/diameter (assumption)
ISP_STORABLE = 300.0      # s, modest chemical-stage order (assumption)
ISP_LH2 = 450.0           # s, hydrolox vacuum-order (assumption)
FP_STAGE = 0.85           # propellant mass fraction of the stack after rail (optimistic, labeled)
# assumed screening thresholds (not material certificates)
Q_SCREEN_PA = 200_000.0   # 200 kPa assumed "aggressive but reportable" q
G_ELECTRONICS = 1000.0    # assumed electronics-only gun-launch-like mean g screen
G_CONVENTIONAL = 100.0

# oasis-style gate on search candidates and onboard acts
COMMIT_TH = 0.65
BUFFER_TH = 0.325


def rho_of(h):
    return RHO0 * math.exp(-max(0.0, h) / H_SCALE)


def mph(v):
    return v / MPH


def m_to_mi(m):
    return m / 1609.344


def transmissibility(r, zeta):
    num = 1.0 + (2.0 * zeta * r) ** 2
    den = (1.0 - r ** 2) ** 2 + (2.0 * zeta * r) ** 2
    return math.sqrt(num / den) if den > 0 else float("inf")


def dart_area(mass, rho=RHO_CFRP, ld=LD_DART):
    """Volume = m/rho; cylinder with L = ld * d. Labeled assumption."""
    vol = mass / rho
    # vol = pi (d/2)^2 * (ld*d) = pi ld d^3 / 4
    d = (4.0 * vol / (math.pi * ld)) ** (1.0 / 3.0)
    return math.pi * (d / 2.0) ** 2, d


def cfg_key(d):
    # stable, rounded key
    items = []
    for k in sorted(d.keys()):
        v = d[k]
        if isinstance(v, float):
            items.append((k, round(v, 8)))
        else:
            items.append((k, v))
    return json.dumps(items, separators=(",", ":"), default=str)


def v_circ(h):
    return math.sqrt(MU_EARTH / (R_EARTH + max(0.0, h)))


def vacuum_transfer_residual(h_apo, v_apo):
    """Textbook two-burn transfer from a horizontal apogee state to 200 km circular.
    Optimistic if apogee is still in atmosphere (drag ignored)."""
    if h_apo < 0:
        return None
    r_a = R_EARTH + h_apo
    r_t = R_EARTH + LEO_ALT_M
    a = 0.5 * (r_a + r_t)
    v_tr_a = math.sqrt(MU_EARTH * (2.0 / r_a - 1.0 / a))
    v_tr_t = math.sqrt(MU_EARTH * (2.0 / r_t - 1.0 / a))
    v_c_t = math.sqrt(MU_EARTH / r_t)
    dv1 = v_tr_a - v_apo  # may be negative (need to slow)
    dv2 = abs(v_c_t - v_tr_t)
    return abs(dv1) + dv2, dv1, dv2


def stage_dv(isp, fp=FP_STAGE):
    if not (0.0 < fp < 1.0):
        return 0.0
    return isp * G_STD * math.log(1.0 / (1.0 - fp))


# ---------------------------------------------------------------------------
# Layered ISA-like atmosphere (textbook piecewise, well-known breakpoints)
# Troposphere 0-11 km, tropopause 11 km, stratosphere 11-47 km, mesosphere 47-86 km
# ---------------------------------------------------------------------------
R_AIR = 287.05287  # J/(kg K), dry air
P0 = 101325.0
T0 = 288.15


def isa_layer(h):
    """Return (name, T_K, tropopause_jet_flag) for geometric altitude h in m."""
    if h < 0:
        h = 0.0
    if h < 11000:
        return "troposphere"
    if h < 20000:
        return "tropopause/lower_stratosphere"
    if h < 47000:
        return "stratosphere"
    if h < 51000:
        return "stratopause"
    if h < 86000:
        return "mesosphere"
    return "thermosphere_edge"


def isa_T_P_rho(h):
    """Approximate ISA T, P, rho. Piecewise linear T (well-known ISA layers)."""
    h = max(0.0, float(h))
    # Build from the surface upward (hydrostatic with linear T)
    # 0-11 km: lapse 6.5 K/km
    if h <= 11000:
        T = T0 - 0.0065 * h
        P = P0 * (T / T0) ** (G_STD / (R_AIR * 0.0065))
        return T, P, P / (R_AIR * T)
    T11 = T0 - 0.0065 * 11000
    P11 = P0 * (T11 / T0) ** (G_STD / (R_AIR * 0.0065))
    # 11-20 km: isothermal 216.65
    if h <= 20000:
        T = T11
        P = P11 * math.exp(-G_STD * (h - 11000) / (R_AIR * T))
        return T, P, P / (R_AIR * T)
    P20 = P11 * math.exp(-G_STD * (9000) / (R_AIR * T11))
    T20 = T11
    # 20-32 km: +1 K/km
    if h <= 32000:
        T = T20 + 0.001 * (h - 20000)
        P = P20 * (T / T20) ** (-G_STD / (R_AIR * 0.001))
        return T, P, P / (R_AIR * T)
    T32 = T20 + 0.001 * 12000
    P32 = P20 * (T32 / T20) ** (-G_STD / (R_AIR * 0.001))
    # 32-47 km: +2.8 K/km
    if h <= 47000:
        T = T32 + 0.0028 * (h - 32000)
        P = P32 * (T / T32) ** (-G_STD / (R_AIR * 0.0028))
        return T, P, P / (R_AIR * T)
    T47 = T32 + 0.0028 * 15000
    P47 = P32 * (T47 / T32) ** (-G_STD / (R_AIR * 0.0028))
    # 47-51 km: isothermal
    if h <= 51000:
        T = T47
        P = P47 * math.exp(-G_STD * (h - 47000) / (R_AIR * T))
        return T, P, P / (R_AIR * T)
    P51 = P47 * math.exp(-G_STD * 4000 / (R_AIR * T47))
    T51 = T47
    # 51-71 km: -2.8 K/km
    if h <= 71000:
        T = T51 - 0.0028 * (h - 51000)
        P = P51 * (T / T51) ** (G_STD / (R_AIR * 0.0028))
        return T, P, P / (R_AIR * T)
    T71 = T51 - 0.0028 * 20000
    P71 = P51 * (T71 / T51) ** (G_STD / (R_AIR * 0.0028))
    # 71-86 km: -2.0 K/km
    if h <= 86000:
        T = T71 - 0.002 * (h - 71000)
        T = max(T, 180.0)
        P = P71 * (T / T71) ** (G_STD / (R_AIR * 0.002))
        return T, P, P / (R_AIR * T)
    T86 = max(T71 - 0.002 * 15000, 180.0)
    P86 = P71 * (T86 / T71) ** (G_STD / (R_AIR * 0.002))
    T = T86
    P = P86 * math.exp(-G_STD * (h - 86000) / (R_AIR * T))
    return T, P, P / (R_AIR * T)


def rho_isa(h):
    return isa_T_P_rho(h)[2]


# Wind / jet / updraft — LABELED ASSUMPTIONS, not a location-specific forecast
JET_H0, JET_H1 = 9000.0, 14000.0   # shear layer around the tropopause
JET_SPEED = 50.0                   # m/s, mid-latitude jet-order assumption
UPDRAFT = 5.0                      # m/s, modest orographic/thermal assumption, troposphere only
SOAR_ETA = 0.20                    # fraction of shear that a cycling glider can extract (assumption)
LIFT_USEFUL_H = 40000.0            # above this, lift is treated as negligible (rho too low)


def wind_horizontal(h):
    """Simple bump of JET_SPEED inside the tropopause shear layer, 0 elsewhere."""
    if JET_H0 <= h <= JET_H1:
        # cosine bump peaking at mid-layer
        mid = 0.5 * (JET_H0 + JET_H1)
        half = 0.5 * (JET_H1 - JET_H0)
        return JET_SPEED * 0.5 * (1.0 + math.cos(math.pi * (h - mid) / half))
    return 0.0


def wind_shear(h, dh=50.0):
    return (wind_horizontal(h + dh) - wind_horizontal(h - dh)) / (2.0 * dh)


def updraft_vertical(h):
    return UPDRAFT if 0.0 <= h <= 11000.0 else 0.0


# ---------------------------------------------------------------------------
# Hollow-bone textbook comparison (circular tube vs solid, equal mass or equal I)
# ---------------------------------------------------------------------------
def hollow_bone_ratios(k):
    """k = Di/Do. Equal-mass I_h/I_s = (1+k^2)/(1-k^2).
    Equal-stiffness mass ratio m_h/m_s = sqrt((1-k^2)/(1+k^2)).
    """
    if k <= 0 or k >= 1:
        return None
    i_ratio = (1.0 + k * k) / (1.0 - k * k)
    m_ratio = math.sqrt((1.0 - k * k) / (1.0 + k * k))
    return {"k": k, "I_hollow_over_I_solid_equal_mass": i_ratio, "mass_hollow_over_solid_equal_I": m_ratio,
            "mass_savings_equal_I": 1.0 - m_ratio}


# Feather / vane assumptions when origami wings are deployed
# Hierarchical rachis/barb/barbule -> area at low mass; porosity is a control
CL_FEATHER = 0.6          # assumption, modest cambered vane
CD_FEATHER_EXTRA = 0.08   # added Cd when deployed at porosity 0 (assumption)
S_OVER_A_DART = 8.0       # wing area / dart cross-section when deployed (assumption)
POROSITY_OPEN = 0.4       # onboard can raise porosity, cutting lift and extra drag


def feather_aero(base_area, porosity=0.0):
    """Effective wing area, Cl, extra Cd. Porosity reduces both lift and extra drag."""
    open_f = max(0.0, min(1.0, porosity))
    S = base_area * S_OVER_A_DART * (1.0 - 0.5 * open_f)
    Cl = CL_FEATHER * (1.0 - 0.7 * open_f)
    Cd_extra = CD_FEATHER_EXTRA * (1.0 - 0.5 * open_f)
    return S, Cl, Cd_extra


# Sutton-Graves-style heat flux (labeled Earth-order cold-wall proxy)
# q (W/m^2) = K * sqrt(rho / R_n) * v^3, with rho kg/m3, R_n m, v m/s.
# K_SG = 1.83e-4 is the conventional SI rearrangement of the well-known
# Sutton-Graves Earth constant (order-of-magnitude proxy, not a CFD result).
K_SG = 1.83e-4
R_NOSE = 0.02          # assumed dart nose radius, m
EPS_RAD = 0.8          # assumed emissivity
SIGMA_SB = 5.670374419e-8
C_SKIN = 1000.0        # assumed skin specific heat, J/kg/K (polymer-order)
M_SKIN_FRAC = 0.02     # assumed heated-skin mass as a fraction of vehicle mass

# Labeled textbook/typical melt and degradation temperatures (K). Ranges exist
# by grade; these are order-of-magnitude values used as assumptions.
# PLA Tm ~150-180 C, degradation often cited ~250-300 C.
# PETG is amorphous (softens well below print temp); print ~230-250 C, degrade ~280-300 C.
# EVA hot-glue typically applied ~120-170 C; degrade above ~200-250 C (grade-dependent).
# Paraffin wax Tm commonly ~50-70 C (a mid value of 60 C is used).
# PEEK Tm is well-known near 343 C; onset of thermal degradation often ~500-580 C.
MATERIALS = {
    "paraffin_wax": {"T_melt_K": 60 + 273.15, "T_degrade_K": 250 + 273.15, "H_abl_J_kg": 2.0e5},
    "EVA_hot_glue": {"T_melt_K": 140 + 273.15, "T_degrade_K": 230 + 273.15, "H_abl_J_kg": 2.5e5},
    "PLA": {"T_melt_K": 165 + 273.15, "T_degrade_K": 260 + 273.15, "H_abl_J_kg": 3.0e5},
    "PETG": {"T_melt_K": 230 + 273.15, "T_degrade_K": 290 + 273.15, "H_abl_J_kg": 3.0e5},
    "PEEK": {"T_melt_K": 343 + 273.15, "T_degrade_K": 530 + 273.15, "H_abl_J_kg": 5.0e5},
}
# H_abl_J_kg values are labeled assumptions (effective heat of ablation / phase change), not certificates.
FEED_RATE_KG_S = 0.0005   # assumed max filament feed when in the deposit band
FILAMENT_BUDGET_FRAC = 0.05  # assumed filament mass as a fraction of vehicle mass


def sutton_graves_q(rho, v, r_n=R_NOSE):
    if rho <= 0 or v <= 0 or r_n <= 0:
        return 0.0
    return K_SG * math.sqrt(rho / r_n) * (v ** 3)


def T_eq_radiation(q, eps=EPS_RAD):
    if q <= 0:
        return 0.0
    return (q / (eps * SIGMA_SB)) ** 0.25


# ---------------------------------------------------------------------------
# Track and flight integration
# ---------------------------------------------------------------------------
def phi_of_s(geometry, s, theta0, theta1=None):
    theta1 = theta0 if theta1 is None else theta1
    if geometry == "straight":
        return theta0
    if geometry == "concave_bowl":
        return min(s / BOWL_R, theta0)
    if geometry == "convex_sphere":
        return max(theta0 - s / BOWL_R, 0.0)
    if geometry == "flatten":
        # start at theta0, ease to theta1 over a 40 km characteristic length (assumption)
        Lc = 40000.0
        u = min(1.0, s / Lc)
        return theta0 + (theta1 - theta0) * u
    return theta0


def integrate_track(v_target, geometry, theta0_deg, mass, cd, area, peak_a,
                    h0=0.0, evac_until_h=None, evac_frac=0.0, theta1_deg=None,
                    dt=0.005, cap_t=20000.0, cap_s=2.0e7, atmosphere="isa"):
    theta0 = math.radians(theta0_deg)
    theta1 = None if theta1_deg is None else math.radians(theta1_deg)
    v, t, s = 0.0, 0.0, 0.0
    x, y = 0.0, float(h0)
    pulses, was_on = 0, False
    max_q, max_q_sg = 0.0, 0.0
    reached, stall_cycles = False, 0
    v_at_cycle = 0.0
    tube_coast = False
    rho_fn = rho_isa if atmosphere == "isa" else rho_of
    period = T_PULSE
    evac_s_limit = evac_frac * cap_s if evac_frac > 0 else None

    def in_evac():
        if evac_until_h is not None and y < evac_until_h:
            return True
        if evac_s_limit is not None and s < evac_s_limit:
            return True
        return False

    while t < cap_t and s < cap_s:
        phi = phi_of_s(geometry, s, theta0, theta1)
        rho = 0.0 if (in_evac() or tube_coast) else rho_fn(y)
        q = 0.5 * rho * v * v
        max_q = max(max_q, q)
        max_q_sg = max(max_q_sg, sutton_graves_q(rho, v))
        drag_a = (0.5 * cd * rho * area * v * v) / mass if mass > 0 else 0.0
        g_along = G_STD * math.sin(phi) * (R_EARTH / (R_EARTH + max(0.0, y))) ** 2
        if tube_coast:
            # unpowered ride to the tube exit; no drag inside the evac tube
            a_along = -g_along
            on = False
        else:
            on = (t % period) < PULSE_ON
            if on and not was_on:
                pulses += 1
            if on and pulses == 0:
                pulses = 1
            was_on = on
            a_along = (peak_a if on else 0.0) - g_along - drag_a
        v = max(0.0, v + a_along * dt)
        ds = v * dt
        s += ds
        x += ds * math.cos(phi)
        y += ds * math.sin(phi)
        t += dt
        # stall: over one full cycle, v barely rises while still short of target
        if (not tube_coast) and t > period and abs((t % period) - period) < dt:
            if v - v_at_cycle < 0.5 and v < 0.98 * v_target:
                stall_cycles += 1
                if stall_cycles >= 5:
                    break
            else:
                stall_cycles = 0
            v_at_cycle = v
        if (not tube_coast) and v >= v_target:
            reached = True
            # stay in the tube until the declared evac release altitude
            if evac_until_h is not None and y < evac_until_h:
                tube_coast = True
            else:
                break
        if tube_coast and evac_until_h is not None and y >= evac_until_h:
            break
        if tube_coast and v <= 10.0:
            break
    phi = phi_of_s(geometry, s, theta0, theta1)
    cap_hit = (not reached) and (t >= cap_t - 1e-6 or s >= cap_s - 1e-3)
    stalled = (not reached) and (not cap_hit)
    return {
        "reached_target": reached, "stalled": stalled, "cap_hit": cap_hit,
        "v_end_m_s": v, "v_end_mph": mph(v), "v_target_m_s": v_target,
        "length_m": s, "length_km": s / 1000.0, "length_mi": m_to_mi(s),
        "time_s": t, "exit_angle_deg": math.degrees(phi),
        "exit_alt_m": y, "exit_x_m": x, "pulses": pulses,
        "peak_q_pa": max_q, "peak_q_sg_W_m2": max_q_sg, "peak_push_m_s2": peak_a,
        "geometry": geometry, "h0_m": h0, "evac_until_h": evac_until_h,
        "evac_frac": evac_frac, "atmosphere": atmosphere,
    }


def apply_dv(v, ang, dv, mode="horizontal"):
    """Add a stage Δv at rail exit. mode: along_velocity or horizontal."""
    if dv <= 0:
        return v, ang
    vx, vy = v * math.cos(ang), v * math.sin(ang)
    if mode == "along_velocity":
        return v + dv, ang
    # add to local horizontal
    vx += dv
    v_new = math.hypot(vx, vy)
    return v_new, math.atan2(vy, vx)


def fly(v0, angle_deg, h0, mass, cd, area, dt=0.05, t_max=900.0,
        atmosphere="isa", lift=False, porosity=0.0, deployed=False,
        winds=False, density_scale=1.0, cd_scale=1.0,
        controller=None, deploy_mode="never", q_deploy=5000.0, t_deploy=10.0):
    """Point-mass flight. Optional feather lift, winds, and a callback controller.
    controller(state) -> dict with optional keys dgamma, porosity, deploy, levy_event
    """
    rho_fn = rho_isa if atmosphere == "isa" else rho_of
    ang = math.radians(angle_deg)
    r0 = R_EARTH + max(0.0, h0)
    x, y = 0.0, r0
    vx, vy = v0 * math.cos(ang), v0 * math.sin(ang)
    t = 0.0
    h_max, v_apo, t_apo = max(0.0, h0), v0, 0.0
    peak_q, peak_qsg, peak_Teq = 0.0, 0.0, 0.0
    deployed_flag = bool(deployed)
    t_deployed = None
    hist = []  # sparse heat/control log
    while t < t_max:
        r = math.hypot(x, y)
        h = r - R_EARTH
        if r < 1.0 or h < -10.0:
            break
        rho = density_scale * rho_fn(h)
        speed = math.hypot(vx, vy)
        q = 0.5 * rho * speed * speed
        qsg = sutton_graves_q(rho, speed)
        Teq = T_eq_radiation(qsg)
        peak_q, peak_qsg, peak_Teq = max(peak_q, q), max(peak_qsg, qsg), max(peak_Teq, Teq)
        # deployment
        if not deployed_flag:
            if deploy_mode == "fixed" and t >= t_deploy:
                deployed_flag, t_deployed = True, t
            elif deploy_mode == "q_threshold" and q <= q_deploy and t > 0.5:
                deployed_flag, t_deployed = True, t
        # aero
        Cd, S_ref, Cl, S_wing = cd * cd_scale, area, 0.0, 0.0
        if deployed_flag and lift and h < LIFT_USEFUL_H:
            S_wing, Cl, Cd_ex = feather_aero(area, porosity)
            Cd = cd * cd_scale + Cd_ex
        # gravity to Earth center
        g = MU_EARTH / (r * r)
        ax, ay = -g * x / r, -g * y / r
        if speed > 1e-6 and mass > 0:
            # drag opposite velocity
            Fd = 0.5 * Cd * rho * (S_wing if (S_wing > 0 and deployed_flag and lift) else S_ref) * speed * speed
            # when wings deployed, use wing area for both; otherwise dart area
            A_used = S_wing if (deployed_flag and lift and S_wing > 0) else S_ref
            Fd = 0.5 * Cd * rho * A_used * speed * speed
            ax -= (Fd / mass) * (vx / speed)
            ay -= (Fd / mass) * (vy / speed)
            if deployed_flag and lift and h < LIFT_USEFUL_H and Cl > 0:
                # lift perpendicular to velocity, "up" relative to local horizon
                # unit velocity
                tx, ty = vx / speed, vy / speed
                # out-of-plane 2D: rotate by +90 deg toward local radial (climb-seeking)
                # prefer the normal with a positive radial component
                nx, ny = -ty, tx
                if nx * x + ny * y < 0:
                    nx, ny = -nx, -ny
                L = 0.5 * rho * speed * speed * S_wing * Cl
                ax += (L / mass) * nx
                ay += (L / mass) * ny
            if winds and h < LIFT_USEFUL_H:
                # updraft adds vertical inertial accel in troposphere only (labeled)
                # model as an additive velocity-relative boost once per step, small
                w_up = updraft_vertical(h)
                if w_up > 0:
                    # local vertical is radial
                    ay += (w_up * 0.2) * (y / r) / max(dt, 1e-3) * 0.0  # don't use fake accel
                # dynamic soaring: specific energy increment η V (dW/dh) only with wings
                if deployed_flag and lift:
                    shear = wind_shear(h)
                    if abs(shear) > 0:
                        # Ė/m ≈ η * V * |ΔW| * |sin|  — cap by wind speed scale
                        dE = SOAR_ETA * speed * abs(wind_horizontal(h + 50) - wind_horizontal(h - 50)) * 0.5
                        dE = min(dE, 0.5 * JET_SPEED ** 2 / 10.0)  # modest cap per second, assumption
                        # apply as a tiny along-track Δv = dE / V
                        dv = (dE * dt) / max(speed, 1.0)
                        vx += dv * (vx / speed)
                        vy += dv * (vy / speed)
        # controller
        ctrl = None
        if controller is not None:
            state = {"t": t, "h": h, "v": speed, "q": q, "qsg": qsg, "Teq": Teq,
                     "ang": math.atan2(vy * y + vx * x, vx * (-y) + vy * x) if r > 0 else 0.0,
                     "gamma_approx": math.atan2(vx * x + vy * y, -vy * x + vx * y) if speed > 0 else 0.0,
                     "deployed": deployed_flag, "porosity": porosity,
                     "layer": isa_layer(h)}
            # flight-path angle from local horizontal
            # local horizontal unit: (-y, x)/r? Wait radial is (x,y)/r, horizontal is (-y, x)/r
            hr = math.hypot(x, y)
            urx, ury = x / hr, y / hr
            # velocity components
            v_r = vx * urx + vy * ury
            v_th = -vx * ury + vy * urx
            gamma = math.atan2(v_r, v_th) if speed > 0 else 0.0
            state["gamma"] = gamma
            ctrl = controller(state) or {}
            if "porosity" in ctrl:
                porosity = ctrl["porosity"]
            if ctrl.get("deploy") and not deployed_flag:
                deployed_flag, t_deployed = True, t
            dgamma = ctrl.get("dgamma", 0.0)
            if dgamma:
                # rotate velocity by dgamma (proportional steering), labeled limit applied in controller
                c, s_ = math.cos(dgamma), math.sin(dgamma)
                # rotate in the (v_th, v_r) plane
                vth2 = v_th * c - v_r * s_
                vr2 = v_th * s_ + v_r * c
                vx = vr2 * urx - vth2 * ury
                vy = vr2 * ury + vth2 * urx
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt
        t += dt
        h_new = math.hypot(x, y) - R_EARTH
        if h_new > h_max:
            h_max = h_new
            v_apo = math.hypot(vx, vy)
            t_apo = t
        if t_apo > 0 and t > t_apo + 180.0:
            break
        if t_apo > 0 and h_new < 0:
            break
    h_final = math.hypot(x, y) - R_EARTH
    v_end = math.hypot(vx, vy)
    res = vacuum_transfer_residual(h_max, v_apo)
    residual = res[0] if res else None
    return {
        "apogee_m": h_max, "apogee_km": h_max / 1000.0,
        "reached_karman": h_max >= KARMAN_M, "reached_200km": h_max >= LEO_ALT_M,
        "v_at_apogee_m_s": v_apo, "t_apogee_s": t_apo,
        "peak_q_pa": peak_q, "peak_q_sg_W_m2": peak_qsg, "peak_Teq_K": peak_Teq,
        "residual_200km_m_s": residual,
        "v0_m_s": v0, "h0_m": h0, "t_end_s": t,
        "deployed": deployed_flag, "t_deployed_s": t_deployed,
        "v_end_m_s": v_end, "h_end_m": h_final,
    }


def evaluate_exit(track, mass, cd, area, stages=True, lift=False, winds=False, deploy_mode="never"):
    """Coast (and optional stage) from a rail-exit state. Recycles fly()."""
    v, ang, h = track["v_end_m_s"], math.radians(track["exit_angle_deg"]), max(0.0, track["exit_alt_m"])
    out = {"track": {k: track[k] for k in track}, "flights": {}}
    # no stage, ballistic
    fl0 = fly(v, track["exit_angle_deg"], h, mass, cd, area, lift=False, winds=False, deploy_mode="never")
    out["flights"]["ballistic_no_stage"] = fl0
    if lift:
        fl_l = fly(v, track["exit_angle_deg"], h, mass, cd, area, lift=True, winds=winds,
                   deploy_mode=deploy_mode or "q_threshold")
        out["flights"]["lift_no_stage"] = fl_l
    # An upper stage is only applied when the rail actually reached its target.
    # Staging a stall at low altitude with 5-8 km/s would invent an unphysical escape.
    if stages and track.get("reached_target"):
        for name, isp in (("storable_300s", ISP_STORABLE), ("lh2_450s", ISP_LH2)):
            dv = stage_dv(isp)
            for mode in ("horizontal", "along_velocity"):
                v2, a2 = apply_dv(v, ang, dv, mode)
                fl = fly(v2, math.degrees(a2), h, mass * (1.0 - FP_STAGE), cd, area,
                         lift=False, deploy_mode="never")
                out["flights"][f"{name}_{mode}"] = {**fl, "stage_dv_m_s": dv, "isp_s": isp, "fp": FP_STAGE}
    return out


def score_candidate(ev):
    """Oasis-style utility for the search: higher is better toward Y."""
    # Use the best residual among flights, and whether 100 km was reached
    best_res, best_apo, reached = 1e12, 0.0, False
    for fl in ev["flights"].values():
        apo = fl.get("apogee_km") or 0.0
        best_apo = max(best_apo, apo)
        reached = reached or fl.get("reached_karman", False)
        r = fl.get("residual_200km_m_s")
        if r is not None:
            best_res = min(best_res, r)
    ev["best_residual_m_s"] = best_res
    ev["best_apogee_km"] = best_apo
    ev["reached_karman"] = reached
    # commit-like score in [0,1]
    # reach 100 km is the first Y; then residual toward 0
    s_alt = 1.0 if reached else min(1.0, best_apo / 100.0)
    s_res = max(0.0, 1.0 - best_res / V_CIRC_200KM)
    return 0.55 * s_alt + 0.45 * s_res


def gate_status(score, improves, near):
    if improves and score >= COMMIT_TH:
        return "COMMITTED"
    if improves:
        return "COMMITTED"  # improves frontier even if raw score < 0.65
    if near or score >= BUFFER_TH:
        return "BUFFERED"
    return "RECYCLED"


# ---------------------------------------------------------------------------
# Recycle ledger
# ---------------------------------------------------------------------------
def load_ledger():
    ledger = {"entries": {}, "hits": 0, "misses": 0, "loaded": 0, "undetermined_keys": []}
    # flights_full: sea-level ballistic releases
    flights = json.loads((OUT / "flights_full.json").read_text())
    for f in flights:
        cfg = {"kind": "flight_sealevel", "vehicle": f["vehicle"], "mass": f["mass_kg"],
               "cd": f["cd"], "area": f["area_m2"], "speed_mph": f["speed_mph"],
               "angle_deg": f["angle_deg"]}
        rec = {"source": "flights_full.json", "settled": True,
               "apogee_km": f["apogee_km"], "reached_karman": f["reached_karman"],
               "v_at_apogee_m_s": f["v_at_apogee_m_s"], "peak_q_pa": f["peak_q_pa"],
               "residual_200km_m_s": vacuum_transfer_residual(f["apogee_m"], f["v_at_apogee_m_s"])[0]
               if f.get("apogee_m") is not None else None}
        ledger["entries"][cfg_key(cfg)] = {"cfg": cfg, **rec}
        ledger["loaded"] += 1
    geo = json.loads((OUT / "geometry_runs.json").read_text())
    for row in geo:
        tr = row["track"]
        fl = row["flight"]
        cfg = {"kind": "geometry_track", "vehicle": row["vehicle"],
               "speed_mph": row["speed_target_mph"], "angle_deg": row["design_angle_deg"],
               "geometry": row["geometry"], "peak_g": 3.0, "duty": 0.5}
        cap_hit = (tr["time_s"] >= 799.0) or (tr.get("length_m", 0) >= 1.99e6)
        still_accelerating = cap_hit and (tr["v_end_m_s"] < 0.98 * tr["v_target_m_s"]) and tr["exit_alt_m"] > 50000
        # convex low-alt plateau is a determined stall, not undetermined
        stalled_convex = (row["geometry"] == "convex_sphere" and not tr["reached_target"]
                          and tr["exit_alt_m"] < 5000)
        settled = (tr["reached_target"] or stalled_convex) and not still_accelerating
        rec = {"source": "geometry_runs.json", "settled": settled, "undetermined": (not settled),
               "track": tr, "flight": fl, "cap_hit": cap_hit, "stalled_convex": stalled_convex}
        k = cfg_key(cfg)
        ledger["entries"][k] = {"cfg": cfg, **rec}
        ledger["loaded"] += 1
        if not settled:
            ledger["undetermined_keys"].append(k)
    # graph results: settled, never re-run
    for name in ("ondulatory_addendum.json", "dreamcatcher_weave.json", "system_run.json"):
        p = OUT / name
        if p.exists():
            cfg = {"kind": "graph_or_system", "file": name}
            ledger["entries"][cfg_key(cfg)] = {
                "cfg": cfg, "source": name, "settled": True,
                "note": "graph/system result recycled; not re-run"}
            ledger["loaded"] += 1
    return ledger


def record(ledger, cfg, rec, from_cache=False):
    k = cfg_key(cfg)
    if from_cache:
        ledger["hits"] += 1
    else:
        ledger["misses"] += 1
        ledger["entries"][k] = {"cfg": cfg, **rec}
    return k


def vehicle_from_mass(mass, material="cfrp", hollow_k=None, payload_frac=0.3):
    rho = RHO_CFRP if material == "cfrp" else RHO_ALLI
    struct_frac = 1.0 - payload_frac
    if hollow_k:
        hb = hollow_bone_ratios(hollow_k)
        # equal-stiffness mass savings applied only to the structural fraction (assumption)
        struct_frac = struct_frac * hb["mass_hollow_over_solid_equal_I"]
        mass_eff = mass * (payload_frac + struct_frac) / (payload_frac + (1.0 - payload_frac))
        # keep total mass as 'mass' (payload grows) OR shrink total mass. Use shrink:
        mass_use = mass * (payload_frac + struct_frac) / 1.0
        # wait: original mass M = payload + structure. New structure = struct0 * m_ratio.
        # new total = payload + structure*m_ratio = M * (pf + (1-pf)*m_ratio)
        mass_use = mass * (payload_frac + (1.0 - payload_frac) * hb["mass_hollow_over_solid_equal_I"])
    else:
        hb = None
        mass_use = mass
    area, diam = dart_area(mass_use, rho=rho)
    return {"mass": mass_use, "mass_requested": mass, "cd": CD_DART, "area": area, "diameter_m": diam,
            "material": material, "rho": rho, "hollow": hb, "payload_frac": payload_frac}


def uncap_undetermined(ledger):
    results = []
    geo = json.loads((OUT / "geometry_runs.json").read_text())
    # map vehicle names to mass/cd/area from first matching flight
    flights = json.loads((OUT / "flights_full.json").read_text())
    veh_map = {}
    for f in flights:
        veh_map.setdefault(f["vehicle"], {"mass": f["mass_kg"], "cd": f["cd"], "area": f["area_m2"]})
    for row in geo:
        tr = row["track"]
        cap_hit = (tr["time_s"] >= 799.0) or (tr.get("length_m", 0) >= 1.99e6)
        still = cap_hit and tr["v_end_m_s"] < 0.98 * tr["v_target_m_s"] and tr["exit_alt_m"] > 50000
        if not still:
            continue
        veh = veh_map[row["vehicle"]]
        cfg = {"kind": "uncap_geometry", "vehicle": row["vehicle"],
               "speed_mph": row["speed_target_mph"], "angle_deg": row["design_angle_deg"],
               "geometry": row["geometry"], "peak_g": 3.0}
        print(f"  UNCAP miss: {row['vehicle']} {row['speed_target_mph']} {row['geometry']} {row['design_angle_deg']}")
        tr2 = integrate_track(row["speed_target_mph"] * MPH, row["geometry"], row["design_angle_deg"],
                              veh["mass"], veh["cd"], veh["area"], 3.0 * G_STD,
                              cap_t=20000.0, cap_s=2.0e7, dt=0.01)
        ev = evaluate_exit(tr2, veh["mass"], veh["cd"], veh["area"], stages=True)
        ev["search_score"] = score_candidate(ev)
        record(ledger, cfg, {"settled": not tr2["cap_hit"], "source": "uncap_rerun",
                             "track": tr2, "eval": ev}, from_cache=False)
        results.append({"cfg": cfg, "eval": ev})
    return results


def run_search(ledger):
    """Coarse grid then a small refine around the best residual. Recycle hits."""
    candidates = []
    frontier = []  # list of committed eval summaries

    def consider(cfg, ev, track_meta=None):
        ev["search_score"] = score_candidate(ev)
        res, apo = ev["best_residual_m_s"], ev["best_apogee_km"]
        improves = False
        if ev["reached_karman"]:
            if not frontier:
                improves = True
            else:
                best_res = min(f["best_residual_m_s"] for f in frontier)
                # improve if lower residual, or similar residual with shorter track / lower g
                if res < best_res - 10:
                    improves = True
                elif res <= best_res + 50:
                    # weakly improves if cheaper g or length
                    improves = True if (track_meta or {}).get("shorter_or_softer") else False
        near = (apo >= 50) or (res < V_CIRC_200KM * 0.85)
        if improves and ev["reached_karman"]:
            # keep non-dominated on residual vs peak_g vs length
            frontier.append({"cfg": cfg, "best_residual_m_s": res, "best_apogee_km": apo,
                             "reached_karman": True, "score": ev["search_score"],
                             "track": ev["track"]})
        status = gate_status(ev["search_score"], improves and ev["reached_karman"], near)
        ev["gate"] = status
        candidates.append({"cfg": cfg, "eval": ev, "gate": status})
        return status

    # Recycle settled geometry tracks that already reached (3 g climbs etc.)
    for ent in ledger["entries"].values():
        if ent.get("source") == "geometry_runs.json" and ent.get("settled") and ent["cfg"].get("kind") == "geometry_track":
            if not ent.get("track", {}).get("reached_target"):
                continue
            tr = ent["track"]
            # vehicle lookup
            name = ent["cfg"]["vehicle"]
            # approximate from name
            if "20" in name:
                mass, cd, area = 20.0, (0.30 if "slender" in name else 0.50), (0.008 if "slender" in name else 0.20)
            else:
                continue
            ev = evaluate_exit(tr, mass, cd, area, stages=True)
            ev["track"] = tr
            consider(ent["cfg"], ev)
            record(ledger, {**ent["cfg"], "kind": "recycled_eval"}, {"settled": True, "eval": ev}, from_cache=True)

    grid_masses = [5.0, 20.0, 200.0]
    grid_h0 = [0.0, 4000.0, 30000.0]
    grid_g = [3.0, 10.0, 100.0, 1000.0]
    grid_speed = [3000.0, 8000.0, 17000.0]
    grid_geom = [
        ("straight", 45, None), ("straight", 80, None),
        ("flatten", 80, 15), ("concave_bowl", 80, None),
    ]
    evac_opts = [(None, 0.0), (80000.0, 1.0)]  # open air, or evac tube to 80 km

    # Coarse: not a full product; a structured subset
    coarse = []
    for mass in grid_masses:
        veh = vehicle_from_mass(mass, "cfrp", hollow_k=0.8)
        for h0 in grid_h0:
            for peak_g in grid_g:
                # skip 1000 g with conventional mass-heavy 200 kg as a soft filter but still allow 5 and 20
                if peak_g >= 1000 and mass >= 200:
                    continue
                for sp in grid_speed:
                    for geom, a0, a1 in grid_geom:
                        for evac_h, evac_f in evac_opts:
                            # skip evac+sea-level-only duplicates when h0 already high and evac to 80
                            coarse.append((veh, h0, peak_g, sp, geom, a0, a1, evac_h, evac_f))

    # subsample systematically: take every Nth plus all evac+flatten+high alt
    selected = []
    for i, item in enumerate(coarse):
        veh, h0, peak_g, sp, geom, a0, a1, evac_h, evac_f = item
        keep = (i % 7 == 0) or (geom == "flatten" and evac_h is not None) or (h0 >= 30000 and peak_g in (10, 100) and geom == "flatten")
        if keep:
            selected.append(item)
    print(f"  coarse selected {len(selected)} of {len(coarse)} grid cells")

    for veh, h0, peak_g, sp, geom, a0, a1, evac_h, evac_f in selected:
        cfg = {"kind": "search_track", "mass": veh["mass"], "material": "cfrp_hollow08",
               "h0": h0, "peak_g": peak_g, "speed_mph": sp, "geometry": geom,
               "angle0": a0, "angle1": a1, "evac_until_h": evac_h or 0.0, "evac_frac": evac_f}
        k = cfg_key(cfg)
        if k in ledger["entries"] and ledger["entries"][k].get("settled"):
            record(ledger, cfg, ledger["entries"][k], from_cache=True)
            ev = ledger["entries"][k].get("eval")
            if ev:
                consider(cfg, ev)
            continue
        tr = integrate_track(sp * MPH, geom, a0, veh["mass"], veh["cd"], veh["area"],
                             peak_g * G_STD, h0=h0, evac_until_h=evac_h, evac_frac=evac_f,
                             theta1_deg=a1, dt=0.01, cap_t=8000.0, cap_s=1.0e7)
        ev = evaluate_exit(tr, veh["mass"], veh["cd"], veh["area"], stages=True, lift=False, winds=False,
                           deploy_mode="never")
        ev["track"] = tr
        ev["vehicle"] = veh
        status = consider(cfg, ev)
        record(ledger, cfg, {"settled": not tr["cap_hit"], "eval": ev, "gate": status}, from_cache=False)

    # Refine: neighbors of the best residual among those that reached 100 km
    reached = [c for c in candidates if c["eval"].get("reached_karman")]
    reached.sort(key=lambda c: c["eval"]["best_residual_m_s"])
    refine_runs = []
    if reached:
        best = reached[0]["cfg"]
        print("  best coarse residual", reached[0]["eval"]["best_residual_m_s"], "cfg", best)
        if best.get("kind") == "search_track":
            for dg in (-5.0, 5.0, 0.0):
                for ds in (-2000.0, 2000.0, 0.0):
                    for gfac in (0.5, 1.0, 2.0):
                        if dg == 0 and ds == 0 and gfac == 1.0:
                            continue
                        cfg = dict(best)
                        cfg["angle0"] = max(10.0, min(85.0, (best.get("angle0") or 45) + dg))
                        if best.get("angle1") is not None:
                            cfg["angle1"] = max(5.0, (best["angle1"] + dg * 0.3))
                        cfg["speed_mph"] = max(1000.0, (best["speed_mph"] + ds))
                        cfg["peak_g"] = max(1.0, best["peak_g"] * gfac)
                        cfg["kind"] = "refine_track"
                        refine_runs.append(cfg)
    # cap refine
    refine_runs = refine_runs[:18]
    print(f"  refine runs {len(refine_runs)}")
    for cfg in refine_runs:
        k = cfg_key(cfg)
        if k in ledger["entries"] and ledger["entries"][k].get("settled"):
            record(ledger, cfg, ledger["entries"][k], from_cache=True)
            continue
        veh = vehicle_from_mass(cfg.get("mass") or 20.0, "cfrp", hollow_k=0.8)
        evac_h = cfg.get("evac_until_h") or None
        if evac_h == 0:
            evac_h = None
        tr = integrate_track(cfg["speed_mph"] * MPH, cfg["geometry"], cfg["angle0"],
                             veh["mass"], veh["cd"], veh["area"], cfg["peak_g"] * G_STD,
                             h0=cfg.get("h0") or 0.0, evac_until_h=evac_h,
                             evac_frac=cfg.get("evac_frac") or 0.0,
                             theta1_deg=cfg.get("angle1"), dt=0.01, cap_t=8000.0, cap_s=1.0e7)
        ev = evaluate_exit(tr, veh["mass"], veh["cd"], veh["area"], stages=True, lift=False, winds=False,
                           deploy_mode="never")
        ev["track"] = tr
        ev["vehicle"] = veh
        status = consider(cfg, ev)
        record(ledger, cfg, {"settled": not tr["cap_hit"], "eval": ev, "gate": status}, from_cache=False)

    return candidates, frontier


# ---------------------------------------------------------------------------
# Onboard autonomy
# ---------------------------------------------------------------------------
def make_controller(seed, angle_err_deg=0.0, Kp=0.4, dgamma_max_deg=2.0,
                    q_limit=50e3, levy_q=20e3):
    """Simple proportional flight-path correction with labeled limits.
    Sensors: three noisy altimeter / q / gamma votes; mesh consensus = median.
    Levy weight rises when |error| or q is large (priority on the next correction).
    Oasis-style: apply a correction only when salience on the error exceeds BUFFER,
    and only COMMIT the pulse when score >= COMMIT or Levy flags a large error.
    """
    rng = random.Random(seed)
    applied = {"n_sense": 0, "n_correct": 0, "n_buffer": 0, "n_commit": 0, "n_levy": 0}

    def controller(state):
        applied["n_sense"] += 1
        # three noisy votes of flight-path angle
        true_g = state["gamma"]
        votes = [true_g + rng.gauss(0, math.radians(0.8)) for _ in range(3)]
        votes.sort()
        gamma_hat = votes[1]  # median consensus
        # target: flatten toward ~5 deg after deploy / at high alt, else hold 0 if already shallow
        h = state["h"]
        if h > 80000:
            gamma_tgt = math.radians(2.0)
        elif h > 40000:
            gamma_tgt = math.radians(8.0)
        else:
            gamma_tgt = math.radians(15.0)
        err = gamma_hat - gamma_tgt  # positive means too steep, want negative dgamma
        q = state["q"]
        levy = 0.25 + 0.75 * min(1.0, abs(err) / math.radians(10.0)) * (0.5 + 0.5 * min(1.0, q / levy_q))
        # salience: novelty (error size) + tension (q) + coherence (vote agreement) + resonance (levy)
        novelty = min(1.0, abs(err) / math.radians(15.0))
        tension = min(1.0, q / q_limit)
        spread = max(votes) - min(votes)
        coherence = max(0.0, 1.0 - spread / math.radians(5.0))
        resonance = levy
        S = 0.30 * novelty + 0.25 * tension + 0.25 * coherence + 0.20 * resonance
        out = {"porosity": 0.0 if q > 20e3 else 0.2, "levy": levy, "S": S, "gamma_hat": gamma_hat}
        if S < BUFFER_TH:
            return out
        applied["n_buffer"] += 1
        if S >= COMMIT_TH or levy > 0.7:
            applied["n_commit"] += 1
            applied["n_correct"] += 1
            if levy > 0.7:
                applied["n_levy"] += 1
            # proportional, clipped
            dgamma = -Kp * err
            cap = math.radians(dgamma_max_deg)
            dgamma = max(-cap, min(cap, dgamma))
            # do not steer hard at very high q (structural / heating)
            if q > q_limit:
                dgamma *= 0.2
            out["dgamma"] = dgamma
        return out

    return controller, applied


def run_onboard_mc(exit_state, mass, cd, area, n=24):
    """Monte Carlo: no-control vs closed-loop under labeled perturbations."""
    v0 = exit_state["v_end_m_s"]
    a0 = exit_state["exit_angle_deg"]
    h0 = max(0.0, exit_state["exit_alt_m"])
    modes = {
        "open_loop_fixed_deploy": {"ctrl": False, "deploy": "fixed"},
        "open_loop_q_deploy": {"ctrl": False, "deploy": "q_threshold"},
        "closed_loop_q_deploy": {"ctrl": True, "deploy": "q_threshold"},
    }
    # perturbation scales (labeled assumptions)
    # release-angle error 1 deg 1-sigma; density 10%; Cd 15%; plus a 2 m/s lateral gust via density/angle
    rows = {m: [] for m in modes}
    for seed in range(n):
        rng = random.Random(1000 + seed)
        dang = rng.gauss(0.0, 1.0)          # deg
        dens = 1.0 + rng.gauss(0.0, 0.10)
        cds = 1.0 + rng.gauss(0.0, 0.15)
        dens = max(0.5, min(1.5, dens))
        cds = max(0.5, min(1.8, cds))
        for name, spec in modes.items():
            ctrl, stats = (None, None)
            if spec["ctrl"]:
                ctrl, stats = make_controller(seed + 17)
            fl = fly(v0, a0 + dang, h0, mass, cd, area,
                     lift=True, winds=True, density_scale=dens, cd_scale=cds,
                     controller=ctrl, deploy_mode=spec["deploy"],
                     q_deploy=5000.0, t_deploy=8.0)
            if stats:
                fl["control_stats"] = dict(stats)
            fl["pert"] = {"dang_deg": dang, "density_scale": dens, "cd_scale": cds}
            rows[name].append(fl)
    summary = {}
    for name, lst in rows.items():
        apos = [f["apogee_km"] for f in lst]
        ress = [f["residual_200km_m_s"] for f in lst if f["residual_200km_m_s"] is not None]
        success = sum(1 for f in lst if f["reached_karman"]) / len(lst)
        summary[name] = {
            "n": len(lst),
            "apogee_mean_km": statistics.mean(apos),
            "apogee_std_km": statistics.pstdev(apos) if len(apos) > 1 else 0.0,
            "apogee_min_km": min(apos), "apogee_max_km": max(apos),
            "residual_mean_m_s": statistics.mean(ress) if ress else None,
            "residual_std_m_s": statistics.pstdev(ress) if len(ress) > 1 else 0.0,
            "success_rate_karman": success,
            "deploy_times": [f["t_deployed_s"] for f in lst],
        }
    return {"modes": summary, "n": n, "perturbations": "angle 1-sigma=1 deg; density 10%; Cd 15% (labeled)"}


# ---------------------------------------------------------------------------
# Non-spinning interior
# ---------------------------------------------------------------------------
def isolator_sim(omega_shell, I_ratio=1.0, c_over_I=0.4, t_end=30.0, dt=0.002,
                 d_offset=0.05, v_path=None, r_path=BOWL_R):
    """Rotational isolation: I ω_int' = c (ω_s - ω_int).
    c/I is a labeled inverse time constant (s^-1); default 0.4 /s.
    Path centripetal a_path = v^2/r is unchanged. Spin-g at offset d is ω_int^2 d.
    """
    omega_int = 0.0  # start despun
    t = 0.0
    series = []
    while t <= t_end:
        # first-order lag
        omega_int += (c_over_I) * (omega_shell - omega_int) * dt
        a_spin = (omega_int ** 2) * d_offset
        a_path = ((v_path ** 2) / r_path) if (v_path and r_path) else 0.0
        if int(t / 0.1) != int((t - dt) / 0.1) or t == 0.0:
            series.append({"t": t, "omega_int": omega_int, "omega_shell": omega_shell,
                           "a_spin_m_s2": a_spin, "a_path_m_s2": a_path})
        t += dt
    # also the analytic tau
    tau = 1.0 / c_over_I if c_over_I else None
    # residual at 5 tau
    omega_ss = omega_shell  # first-order tracks if omega_shell constant — that would NOT isolate!
    # Correction: a true rotational isolator has the *base* trying to hold ω_int ~ 0 against leaked torque.
    # The equation above is a viscous coupler to the shell and would spin UP the interior.
    # Isolation requires a reaction: bearings + a despin motor or a counter-torque to reject leaked c*(ωs-ωint).
    # We therefore also integrate a held-despun model: a control torque u = -Kp ω_int - Kd? plus leak.
    return {"series_passive_coupler": series, "tau_s": tau,
            "note_passive": "A viscous coupler alone transmits spin; it is not an isolator."}


def isolator_held(omega_shell, c_over_I=0.05, Kp_over_I=8.0, t_end=30.0, dt=0.002,
                  d_offset=0.05, v_path=None, r_path=BOWL_R, wobble_amp=0.0, wobble_hz=2.0):
    """Despin hold: I ω' = c (ω_s - ω_int) - Kp ω_int  (P control to ω_int=0).
    c/I is the leak coefficient (labeled assumption, much smaller than a solid shaft).
    Kp/I is the despin-hold gain (labeled).
    Optional harmonic wobble torque (eddy/bearing runout), labeled amplitude in rad/s^2.
    """
    omega_int = 0.0
    t = 0.0
    series = []
    peak_spin_g, peak_omega = 0.0, 0.0
    while t <= t_end:
        leak = c_over_I * (omega_shell - omega_int)
        u = -Kp_over_I * omega_int
        wob = wobble_amp * math.sin(2 * math.pi * wobble_hz * t) if wobble_amp else 0.0
        omega_int += (leak + u + wob) * dt
        a_spin = (omega_int ** 2) * d_offset
        a_path = ((v_path ** 2) / r_path) if (v_path and r_path) else 0.0
        peak_spin_g = max(peak_spin_g, a_spin)
        peak_omega = max(peak_omega, abs(omega_int))
        if int(t / 0.05) != int((t - dt) / 0.05) or t == 0.0:
            series.append({"t": t, "omega_int_rad_s": omega_int, "omega_shell_rad_s": omega_shell,
                           "a_spin_m_s2": a_spin, "a_path_m_s2": a_path,
                           "spin_g": a_spin / G_STD, "path_g": a_path / G_STD})
        t += dt
    # residual at end (should be near leak/Kp * omega_shell)
    omega_ss = (c_over_I * omega_shell) / (c_over_I + Kp_over_I)
    return {
        "c_over_I_s": c_over_I, "Kp_over_I_s": Kp_over_I, "d_offset_m": d_offset,
        "omega_shell_rad_s": omega_shell, "omega_ss_rad_s": omega_ss,
        "omega_ss_rpm": omega_ss * 60 / (2 * math.pi),
        "peak_omega_int_rad_s": peak_omega,
        "peak_spin_g": peak_spin_g / G_STD,
        "a_path_m_s2": ((v_path ** 2) / r_path) if (v_path and r_path) else None,
        "path_g": (((v_path ** 2) / r_path) / G_STD) if (v_path and r_path) else None,
        "series": series,
        "release_tumble_omega_rad_s": omega_ss,
        "assumptions": "c/I and Kp/I are labeled; bearings/maglev leak is not measured.",
    }


# ---------------------------------------------------------------------------
# Heat-driven feather regrowth
# ---------------------------------------------------------------------------
def heat_regrowth_along_track(track_like, mass, samples=400):
    """Rebuild a heating time-history from a completed track by re-integrating
    with a coarser log. If the caller already has a history, use that.
    Here we re-run a short diagnostic with logging enabled.
    """
    # We don't have the original samples; reconstruct approximately by
    # interpolating a re-integration. The caller should pass enough fields
    # to re-run: we return a compact diagnostic instead from a scripted
    # re-integration performed by the caller. This function is a placeholder
    # used only if a prebuilt series is supplied.
    raise RuntimeError("use simulate_heat_path")


def simulate_heat_path(v_target, geometry, theta0_deg, mass, cd, area, peak_a,
                       h0=0.0, evac_until_h=None, evac_frac=0.0, theta1_deg=None,
                       coast=True, dt=0.01):
    """Track then a short coast, logging q_sg, T_eq, and deposit/ablate bands."""
    # integrate with logs
    theta0 = math.radians(theta0_deg)
    theta1 = None if theta1_deg is None else math.radians(theta1_deg)
    v, t, s = 0.0, 0.0, 0.0
    x, y = 0.0, float(h0)
    period = T_PULSE
    m_skin = max(1e-4, mass * M_SKIN_FRAC)
    T_skin = 288.15
    series = []
    evac_s_limit = evac_frac * 1e7 if evac_frac > 0 else None
    was_on = False
    pulses = 0
    cap_t, cap_s = 4000.0, 5.0e6
    reached = False

    def evac():
        if evac_until_h is not None and y < evac_until_h:
            return True
        if evac_s_limit is not None and s < evac_s_limit:
            return True
        return False

    budgets = {name: FILAMENT_BUDGET_FRAC * mass for name in MATERIALS}
    remaining = dict(budgets)
    grown = {name: 0.0 for name in MATERIALS}
    ablated = {name: 0.0 for name in MATERIALS}
    t_in_band = {name: 0.0 for name in MATERIALS}
    t_over = {name: 0.0 for name in MATERIALS}
    # missing-cell model: 12 hoop + 4 rings * 12 = 60 dream-catcher cells; start with a loss burst
    N_CELLS = 60
    missing = {name: 8 for name in MATERIALS}  # 8 cells already lost (assumption)
    levy_priority = {name: 0.25 for name in MATERIALS}
    log_every = max(1, int(0.05 / dt))
    step = 0
    on_track = True
    t_release = None
    ang = theta0
    while t < cap_t and s < cap_s:
        rho = 0.0 if (on_track and evac()) else rho_isa(y)
        qsg = sutton_graves_q(rho, v)
        Teq = T_eq_radiation(qsg) if qsg > 0 else max(180.0, 288.15 * 0.7)
        # lumped skin: m c T' = A (q - εσ T^4), A ~ 2 π R_n * L_char; use area as a proxy
        A_heat = max(area, 2 * math.pi * R_NOSE * 0.2)
        q_net = qsg - EPS_RAD * SIGMA_SB * (T_skin ** 4)
        T_skin = max(180.0, T_skin + (A_heat * q_net) * dt / (m_skin * C_SKIN))
        # if qsg is huge, T_skin is pulled toward Teq with a short lag already via this ODE
        T_use = T_skin

        for name, mat in MATERIALS.items():
            Tm, Td = mat["T_melt_K"], mat["T_degrade_K"]
            in_band = (T_use >= Tm) and (T_use < Td)
            over = T_use >= Td
            if in_band:
                t_in_band[name] += dt
                # mesh consensus: deposit only on missing cells, Levy-weighted by how many are missing
                levy_priority[name] = 0.25 + 0.75 * min(1.0, missing[name] / 12.0)
                if remaining[name] > 0 and missing[name] > 0:
                    dm = min(FEED_RATE_KG_S * dt * levy_priority[name], remaining[name])
                    remaining[name] -= dm
                    grown[name] += dm
                    # each cell ~ budget/N
                    cell_mass = budgets[name] / N_CELLS
                    if cell_mass > 0 and grown[name] // cell_mass > (grown[name] - dm) // cell_mass:
                        missing[name] = max(0, missing[name] - 1)
            if over:
                t_over[name] += dt
                # ablation: heat absorbed ~ q * A * dt / H_abl, limited by remaining grown+budget on surface
                dm_abl = (qsg * A_heat * dt) / max(mat["H_abl_J_kg"], 1.0)
                # only ablates what's already deposited plus a small surface inventory
                take = min(dm_abl, grown[name] + 0.1 * remaining[name])
                if take > 0:
                    if take <= grown[name]:
                        grown[name] -= take
                    else:
                        leftover = take - grown[name]
                        grown[name] = 0.0
                        remaining[name] = max(0.0, remaining[name] - leftover)
                    ablated[name] += take
                    # losing a cell
                    cell_mass = budgets[name] / N_CELLS
                    if cell_mass > 0:
                        missing[name] = min(N_CELLS, missing[name] + int(take / cell_mass))

        if step % log_every == 0:
            series.append({
                "t": t, "v": v, "h": y, "qsg": qsg, "Teq": Teq, "T_skin": T_use,
                "on_track": on_track,
            })

        if on_track:
            phi = phi_of_s(geometry, s, theta0, theta1)
            ang = phi
            drag_a = (0.5 * cd * rho * area * v * v) / mass if mass > 0 else 0.0
            g_along = G_STD * math.sin(phi) * (R_EARTH / (R_EARTH + max(0.0, y))) ** 2
            on = (t % period) < PULSE_ON
            a_along = ((peak_a if on else 0.0) - g_along - drag_a)
            v = max(0.0, v + a_along * dt)
            ds = v * dt
            s += ds
            y += ds * math.sin(phi)
            t += dt
            step += 1
            if v >= v_target:
                if evac_until_h is not None and y < evac_until_h:
                    # unpowered tube ride to the release altitude; no aero heating inside
                    g_along = G_STD * math.sin(phi) * (R_EARTH / (R_EARTH + max(0.0, y))) ** 2
                    v = max(0.0, v - g_along * dt)
                    ds = v * dt
                    s += ds
                    y += ds * math.sin(phi)
                    t += dt
                    step += 1
                    if y >= evac_until_h:
                        on_track = False
                        reached = True
                        t_release = t
                    continue
                on_track = False
                reached = True
                t_release = t
                # start coast at this angle
        else:
            # simple coast in the vertical plane, no lift, for a 120 s heating window
            if t - t_release > 120.0:
                break
            r = R_EARTH + max(0.0, y)
            g = MU_EARTH / (r * r)
            # flight path
            vx = v * math.cos(ang)
            vy = v * math.sin(ang)
            # gravity vertical (flat-earth for a short heating window — labeled approximation)
            vy -= g * dt
            # drag
            if mass > 0 and v > 0:
                Fd = 0.5 * cd * rho * area * v * v
                vx -= (Fd / mass) * (vx / max(v, 1e-9)) * dt
                vy -= (Fd / mass) * (vy / max(v, 1e-9)) * dt
            v = math.hypot(vx, vy)
            ang = math.atan2(vy, vx)
            y += vy * dt
            t += dt
            step += 1
            if y < 0 or t > (series[0]["t"] + 400 if series else 400):
                break
        if (not on_track) and t > 0 and y < h0 - 100 and v < 50:
            break
        # also stop if long after release
        if (not on_track) and reached and t > 0:
            # cap coast 90 s for the heat window
            # detect first coast time
            pass
    # trim coast
    # already limited

    mats = {}
    for name, mat in MATERIALS.items():
        mats[name] = {
            "T_melt_K": mat["T_melt_K"], "T_degrade_K": mat["T_degrade_K"],
            "T_melt_C": mat["T_melt_K"] - 273.15, "T_degrade_C": mat["T_degrade_K"] - 273.15,
            "t_in_band_s": t_in_band[name], "t_over_degrade_s": t_over[name],
            "grown_kg": grown[name], "ablated_kg": ablated[name],
            "net_kg": grown[name] - ablated[name],
            "remaining_filament_kg": remaining[name],
            "budget_kg": budgets[name],
            "missing_cells_end": missing[name],
            "levy_priority_end": levy_priority[name],
        }
    peak_qsg = max((p["qsg"] for p in series), default=0.0)
    peak_Teq = max((p["Teq"] for p in series), default=0.0)
    peak_Tskin = max((p["T_skin"] for p in series), default=0.0)
    return {
        "series": series, "materials": mats,
        "peak_qsg_W_m2": peak_qsg, "peak_Teq_K": peak_Teq, "peak_Tskin_K": peak_Tskin,
        "reached_target": reached, "v_end_m_s": v, "h_end_m": y, "t_end_s": t,
        "K_SG": K_SG, "R_NOSE_m": R_NOSE, "eps": EPS_RAD,
        "feed_rate_kg_s": FEED_RATE_KG_S, "filament_budget_frac": FILAMENT_BUDGET_FRAC,
        "N_cells": N_CELLS,
    }


def heat_screens_at_speeds(speeds_mph, altitudes_m, r_n=R_NOSE):
    """Equilibrium radiation temperature from Sutton-Graves at (h, v) points."""
    rows = []
    for h in altitudes_m:
        rho = rho_isa(h)
        for sp in speeds_mph:
            v = sp * MPH
            q = sutton_graves_q(rho, v, r_n)
            Teq = T_eq_radiation(q)
            bands = {}
            for name, mat in MATERIALS.items():
                if Teq < mat["T_melt_K"]:
                    state = "solid_below_melt"
                elif Teq < mat["T_degrade_K"]:
                    state = "deposit_band"
                else:
                    state = "above_degradation"
                bands[name] = state
            rows.append({"h_m": h, "h_km": h / 1000.0, "speed_mph": sp, "v_m_s": v,
                         "rho": rho, "q_sg_W_m2": q, "Teq_K": Teq, "Teq_C": Teq - 273.15,
                         "bands": bands})
    return rows


def run_priority(ledger, candidates, consider_fn=None):
    """Always-run, physically motivated configs (flatten + evac or elevated start)."""
    added = []
    pri = [
        # 3000 mph flatten, 3g, sea / mountain / 30 km, open and evac
        dict(mass=20.0, peak_g=3.0, speed_mph=3000.0, geometry="flatten", angle0=80, angle1=15, h0=0.0, evac_until_h=80000.0, evac_frac=1.0),
        dict(mass=20.0, peak_g=10.0, speed_mph=3000.0, geometry="flatten", angle0=80, angle1=15, h0=4000.0, evac_until_h=80000.0, evac_frac=1.0),
        dict(mass=20.0, peak_g=10.0, speed_mph=3000.0, geometry="flatten", angle0=80, angle1=15, h0=30000.0, evac_until_h=None, evac_frac=0.0),
        dict(mass=20.0, peak_g=100.0, speed_mph=8000.0, geometry="flatten", angle0=60, angle1=12, h0=30000.0, evac_until_h=None, evac_frac=0.0),
        dict(mass=20.0, peak_g=100.0, speed_mph=17000.0, geometry="flatten", angle0=50, angle1=8, h0=30000.0, evac_until_h=None, evac_frac=0.0),
        dict(mass=20.0, peak_g=100.0, speed_mph=17000.0, geometry="flatten", angle0=50, angle1=8, h0=0.0, evac_until_h=80000.0, evac_frac=1.0),
        dict(mass=20.0, peak_g=1000.0, speed_mph=17000.0, geometry="flatten", angle0=45, angle1=5, h0=0.0, evac_until_h=80000.0, evac_frac=1.0),
        dict(mass=5.0, peak_g=100.0, speed_mph=17000.0, geometry="flatten", angle0=50, angle1=8, h0=30000.0, evac_until_h=None, evac_frac=0.0),
        dict(mass=200.0, peak_g=100.0, speed_mph=17000.0, geometry="flatten", angle0=50, angle1=8, h0=0.0, evac_until_h=80000.0, evac_frac=1.0),
        dict(mass=20.0, peak_g=10.0, speed_mph=17000.0, geometry="straight", angle0=15, angle1=None, h0=30000.0, evac_until_h=None, evac_frac=0.0),
        dict(mass=20.0, peak_g=3.0, speed_mph=3000.0, geometry="straight", angle0=80, angle1=None, h0=0.0, evac_until_h=None, evac_frac=0.0),  # recycle-comparable
    ]
    for p in pri:
        veh = vehicle_from_mass(p["mass"], "cfrp", hollow_k=0.8)
        cfg = {"kind": "priority_track", **{k: p[k] for k in p}}
        cfg["mass"] = veh["mass"]
        evac_h = p["evac_until_h"]
        tr = integrate_track(p["speed_mph"] * MPH, p["geometry"], p["angle0"],
                             veh["mass"], veh["cd"], veh["area"], p["peak_g"] * G_STD,
                             h0=p["h0"], evac_until_h=evac_h, evac_frac=p["evac_frac"] or 0.0,
                             theta1_deg=p["angle1"], dt=0.01, cap_t=8000.0, cap_s=1.0e7)
        ev = evaluate_exit(tr, veh["mass"], veh["cd"], veh["area"], stages=True, lift=True, winds=True,
                           deploy_mode="q_threshold")
        ev["track"] = tr
        ev["vehicle"] = veh
        ev["search_score"] = score_candidate(ev)
        ev["gate"] = gate_status(ev["search_score"], ev["reached_karman"], ev["best_apogee_km"] >= 50)
        record(ledger, cfg, {"settled": not tr["cap_hit"], "eval": ev, "gate": ev["gate"]}, from_cache=False)
        candidates.append({"cfg": cfg, "eval": ev, "gate": ev["gate"]})
        added.append({"cfg": cfg, "eval": ev})
        print(f"  priority {p['speed_mph']}mph g={p['peak_g']} h0={p['h0']} evac={evac_h} reached={tr['reached_target']} "
              f"vend={tr['v_end_mph']:.0f} alt={tr['exit_alt_m']/1000:.1f}km ang={tr['exit_angle_deg']:.1f} "
              f"res={ev['best_residual_m_s']:.0f} apo={ev['best_apogee_km']:.1f} gate={ev['gate']}")
    return added


def hollow_table(ks=(0.5, 0.7, 0.8, 0.9)):
    return [hollow_bone_ratios(k) for k in ks]


def lift_vs_ballistic(exit_track, mass, cd, area):
    """Honest altitude help of feathers + soaring vs a ballistic coast from the same exit."""
    v, a, h = exit_track["v_end_m_s"], exit_track["exit_angle_deg"], max(0.0, exit_track["exit_alt_m"])
    base = fly(v, a, h, mass, cd, area, lift=False, winds=False, deploy_mode="never")
    lift_only = fly(v, a, h, mass, cd, area, lift=True, winds=False, deploy_mode="q_threshold")
    lift_wind = fly(v, a, h, mass, cd, area, lift=True, winds=True, deploy_mode="q_threshold")
    return {"ballistic": base, "lift_no_wind": lift_only, "lift_and_winds": lift_wind,
            "delta_apogee_km_lift": lift_only["apogee_km"] - base["apogee_km"],
            "delta_apogee_km_winds": lift_wind["apogee_km"] - base["apogee_km"],
            "delta_residual_lift": (None if (lift_only["residual_200km_m_s"] is None or base["residual_200km_m_s"] is None)
                                    else lift_only["residual_200km_m_s"] - base["residual_200km_m_s"])}


def make_figures(pareto_rows, heat_rows, heat_paths, iso_held, outdir):
    figpaths = []
    # Fig A: Pareto residual vs rail exit speed, sized by peak g
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    reached = [r for r in pareto_rows if r.get("reached_karman")]
    failed = [r for r in pareto_rows if not r.get("reached_karman")]
    if failed:
        ax.scatter([r["v_end_mph"] for r in failed], [r["best_residual_m_s"] / 1000.0 for r in failed],
                   c="#aaaaaa", s=22, alpha=0.7, label="did not reach 100 km (best residual if defined)")
    if reached:
        sc = ax.scatter([r["v_end_mph"] for r in reached], [r["best_residual_m_s"] / 1000.0 for r in reached],
                        c=[r["peak_g"] for r in reached], cmap="viridis", s=46, zorder=3, edgecolors="k", linewidths=0.3,
                        label="reached 100 km")
        cbar = fig.colorbar(sc, ax=ax, pad=0.02)
        cbar.set_label("peak rail g (assumed)")
    ax.axhline(0.0, color="#333", lw=0.6)
    ax.set_xlabel("Rail exit speed (mph)")
    ax.set_ylabel("Best residual Δv to 200 km circular (km/s)")
    ax.set_title("Goal-seeking Pareto: residual after rail + optional stage")
    ax.legend(loc="best", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    pA = outdir / "fig06_goal_seek_pareto.png"
    fig.savefig(pA, dpi=150, bbox_inches="tight")
    plt.close(fig)
    figpaths.append(pA)

    # Fig B: heat screens Teq vs speed at selected altitudes, melt/degrade bands
    fig, ax = plt.subplots(figsize=(8.2, 5.6))
    alts = sorted(set(r["h_km"] for r in heat_rows))
    colors = plt.cm.plasma([0.15, 0.35, 0.55, 0.75, 0.9])
    for i, hkm in enumerate(alts):
        pts = [r for r in heat_rows if r["h_km"] == hkm]
        pts.sort(key=lambda r: r["speed_mph"])
        ax.semilogy([r["speed_mph"] for r in pts], [max(r["Teq_K"], 1) for r in pts],
                    "o-", color=colors[i % len(colors)], label=f"{hkm:.0f} km")
    # material bands as horizontal spans (use mid of melt-degrade)
    y0, y1 = ax.get_ylim() if False else (200, 1e4)
    colors_m = {"paraffin_wax": "#c9a227", "EVA_hot_glue": "#d65a31", "PLA": "#3a7d44",
                "PETG": "#2a6f97", "PEEK": "#5c4d7a"}
    for name, mat in MATERIALS.items():
        ax.axhline(mat["T_melt_K"], color=colors_m[name], ls="--", lw=0.9, alpha=0.9)
        ax.axhline(mat["T_degrade_K"], color=colors_m[name], ls=":", lw=0.9, alpha=0.9)
        ax.text(180, mat["T_melt_K"] * 1.02, f"{name} melt", color=colors_m[name], fontsize=7, va="bottom")
    ax.set_xlabel("Speed (mph)")
    ax.set_ylabel("Sutton–Graves radiation-equilibrium T (K)")
    ax.set_title("Heating proxy vs labeled polymer melt / degradation temperatures")
    ax.legend(loc="upper left", fontsize=8, title="altitude")
    ax.grid(True, which="both", alpha=0.3)
    ax.set_xlim(0, 17500)
    fig.tight_layout()
    pB = outdir / "fig07_heat_regrowth_bands.png"
    fig.savefig(pB, dpi=150, bbox_inches="tight")
    plt.close(fig)
    figpaths.append(pB)

    # Fig C: isolator — path g unchanged, spin g held down
    if iso_held and iso_held.get("series"):
        fig, ax = plt.subplots(figsize=(8.2, 4.8))
        ser = iso_held["series"]
        t = [s["t"] for s in ser]
        ax.plot(t, [s["path_g"] for s in ser], color="#1f3a5f", lw=1.6, label="path centripetal g (v²/r), unchanged")
        ax.plot(t, [s["spin_g"] for s in ser], color="#d65a31", lw=1.6, label="residual spin g at 5 cm offset")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Acceleration (units of g)")
        ax.set_title("Non-spinning interior: isolation removes spin-g, not path-g")
        ax.legend(loc="best", fontsize=8)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        pC = outdir / "fig08_nonspin_interior.png"
        fig.savefig(pC, dpi=150, bbox_inches="tight")
        plt.close(fig)
        figpaths.append(pC)
    return figpaths


def compact_eval(ev):
    """Drop bulky nested series from JSON."""
    d = {
        "best_residual_m_s": ev.get("best_residual_m_s"),
        "best_apogee_km": ev.get("best_apogee_km"),
        "reached_karman": ev.get("reached_karman"),
        "search_score": ev.get("search_score"),
        "gate": ev.get("gate"),
        "track": ev.get("track"),
        "flights": {},
    }
    for name, fl in (ev.get("flights") or {}).items():
        d["flights"][name] = {k: fl[k] for k in fl if k not in ("hist", "series")}
    if ev.get("vehicle"):
        d["vehicle"] = ev["vehicle"]
    return d


def main():
    random.seed(7)
    print("V_CIRC_200KM", V_CIRC_200KM, "stage dv 300/450", stage_dv(ISP_STORABLE), stage_dv(ISP_LH2))
    print("loading ledger")
    ledger = load_ledger()
    print(f"  loaded {ledger['loaded']} settled/prior entries; undetermined {len(ledger['undetermined_keys'])}")

    print("uncapping still-accelerating climbs")
    uncap = uncap_undetermined(ledger)
    uncap_sum = []
    for u in uncap:
        ev = u["eval"]
        tr = ev["track"]
        uncap_sum.append({
            "cfg": u["cfg"],
            "reached_target": tr["reached_target"], "stalled": tr["stalled"], "cap_hit": tr["cap_hit"],
            "v_end_mph": tr["v_end_mph"], "time_s": tr["time_s"], "length_km": tr["length_km"],
            "exit_alt_km": tr["exit_alt_m"] / 1000.0, "exit_angle_deg": tr["exit_angle_deg"],
            "best_residual_m_s": ev["best_residual_m_s"], "best_apogee_km": ev["best_apogee_km"],
        })
        print("  UNCAP result", uncap_sum[-1])

    print("goal-seeking search")
    candidates, frontier = run_search(ledger)
    print("priority configs")
    pri = run_priority(ledger, candidates)

    # rebuild a simple frontier view
    rows = []
    for c in candidates:
        ev, cfg, tr = c["eval"], c["cfg"], c["eval"].get("track") or {}
        if not tr:
            continue
        rows.append({
            "cfg": cfg, "gate": c.get("gate"),
            "reached_karman": ev.get("reached_karman"),
            "best_residual_m_s": ev.get("best_residual_m_s"),
            "best_apogee_km": ev.get("best_apogee_km"),
            "v_end_mph": tr.get("v_end_mph"), "v_end_m_s": tr.get("v_end_m_s"),
            "exit_alt_m": tr.get("exit_alt_m"), "exit_angle_deg": tr.get("exit_angle_deg"),
            "length_km": tr.get("length_km"), "time_s": tr.get("time_s"),
            "peak_g": (tr.get("peak_push_m_s2") or 0) / G_STD,
            "reached_target": tr.get("reached_target"),
            "score": ev.get("search_score"),
            "best_flight": min(
                ((n, fl.get("residual_200km_m_s"), fl.get("apogee_km"))
                 for n, fl in ev.get("flights", {}).items()
                 if fl.get("residual_200km_m_s") is not None),
                default=None, key=lambda z: z[1]),
        })
    reached_rows = [r for r in rows if r["reached_karman"] and r["best_residual_m_s"] is not None]
    reached_rows.sort(key=lambda r: r["best_residual_m_s"])
    print("top residuals:")
    for r in reached_rows[:8]:
        print(" ", r["best_residual_m_s"], "apo", r["best_apogee_km"], "v", r["v_end_mph"],
              "ang", r["exit_angle_deg"], "g", r["peak_g"], r["best_flight"], r["cfg"].get("kind"))

    # Onboard MC on the best residual config that has a finite exit
    mc = None
    mc_staged = None
    lift_cmp = None
    lift_cases = []
    best_for_mc = reached_rows[0] if reached_rows else (rows[0] if rows else None)
    if best_for_mc:
        cfg = best_for_mc["cfg"]
        # find full eval
        ev_full = next(c["eval"] for c in candidates if c["cfg"] == cfg)
        tr = ev_full["track"]
        veh = ev_full.get("vehicle") or vehicle_from_mass(cfg.get("mass") or 20.0, "cfrp", hollow_k=0.8)
        print("onboard MC on best cfg", cfg)
        mc = run_onboard_mc(tr, veh["mass"], veh["cd"], veh["area"], n=24)
        for name, s in mc["modes"].items():
            print(f"  {name}: apo {s['apogee_mean_km']:.1f}±{s['apogee_std_km']:.1f} km  "
                  f"res {s['residual_mean_m_s']:.0f}±{s['residual_std_m_s']:.0f}  "
                  f"karman {s['success_rate_karman']:.2f}")
        lift_cmp = lift_vs_ballistic(tr, veh["mass"], veh["cd"], veh["area"])
        print("lift vs ballistic dH", lift_cmp["delta_apogee_km_lift"], "winds", lift_cmp["delta_apogee_km_winds"])
        # Also MC the optimistic staged state, if that flight exists
        mc_staged = None
        fl_st = ev_full.get("flights", {}).get("lh2_450s_horizontal")
        if fl_st and ev_full["track"].get("reached_target"):
            ang = math.radians(tr["exit_angle_deg"])
            v2, a2 = apply_dv(tr["v_end_m_s"], ang, stage_dv(ISP_LH2), "horizontal")
            staged_exit = {"v_end_m_s": v2, "exit_angle_deg": math.degrees(a2), "exit_alt_m": max(0.0, tr["exit_alt_m"])}
            print("staged MC at", v2, "m/s", math.degrees(a2), "deg", staged_exit["exit_alt_m"])
            mc_staged = run_onboard_mc(staged_exit, veh["mass"] * (1.0 - FP_STAGE), veh["cd"], veh["area"], n=24)
            for name, s in mc_staged["modes"].items():
                print(f"  STAGED {name}: apo {s['apogee_mean_km']:.1f}±{s['apogee_std_km']:.1f} km  "
                      f"res {s['residual_mean_m_s']:.0f}±{s['residual_std_m_s']:.0f}  "
                      f"karman {s['success_rate_karman']:.2f}")

    # also a mid-speed comparison from the recycled 3000 mph 80° straight if present
    mid_cmp = None
    for c in candidates:
        cfg, tr = c["cfg"], c["eval"].get("track") or {}
        if tr and abs((tr.get("v_end_mph") or 0) - 3000) < 50 and abs((tr.get("exit_angle_deg") or 0) - 80) < 8:
            veh = c["eval"].get("vehicle") or vehicle_from_mass(20.0, "cfrp")
            mid_cmp = {"cfg": cfg, **lift_vs_ballistic(tr, veh["mass"], veh["cd"], veh.get("area", veh.get("area", 0.008))) }
            # fix area
            mid_cmp = {"cfg": cfg, **lift_vs_ballistic(tr, 20.0, 0.30, 0.008)}
            print("mid-speed lift cmp", mid_cmp["delta_apogee_km_lift"], mid_cmp["ballistic"]["apogee_km"], mid_cmp["lift_and_winds"]["apogee_km"])
            break

    # Lift is useful only below ~40 km; run dedicated low-altitude coasts.
    lift_cases = []
    for lab, v_mph, ang, h, mass, cd, area in (
        ("15km_2000mph_25deg", 2000, 25.0, 15000.0, 20.0, 0.30, 0.008),
        ("5km_1000mph_30deg", 1000, 30.0, 5000.0, 20.0, 0.30, 0.008),
        ("20km_3000mph_15deg", 3000, 15.0, 20000.0, 20.0, 0.30, 0.008),
        ("10km_1500mph_20deg_featherarea", 1500, 20.0, 10000.0, 20.0, 0.30, 0.008),
    ):
        dummy = {"v_end_m_s": v_mph * MPH, "exit_angle_deg": ang, "exit_alt_m": h}
        cmp = lift_vs_ballistic(dummy, mass, cd, area)
        cmp["label"] = lab
        lift_cases.append(cmp)
        print("lift case", lab, "ball", cmp["ballistic"]["apogee_km"], "lift", cmp["lift_no_wind"]["apogee_km"],
              "winds", cmp["lift_and_winds"]["apogee_km"], "dH", cmp["delta_apogee_km_lift"])

    # Non-spinning interior: labeled example at a 3000 mph bowl path and a faster one
    v_path = 3000.0 * MPH
    # If the outer shell were spun at 1200 rpm (order-of-magnitude spinning-launch concept, not a vendor spec)
    omega_shell = 1200.0 * 2 * math.pi / 60.0
    iso_3000 = isolator_held(omega_shell, c_over_I=0.05, Kp_over_I=8.0, t_end=20.0,
                             d_offset=0.05, v_path=v_path, r_path=BOWL_R, wobble_amp=0.4, wobble_hz=2.0)
    v_fast = 17000.0 * MPH
    iso_fast = isolator_held(omega_shell, c_over_I=0.05, Kp_over_I=8.0, t_end=8.0,
                             d_offset=0.05, v_path=v_fast, r_path=BOWL_R)
    print("isolator 3000 mph path_g", iso_3000["path_g"], "peak_spin_g", iso_3000["peak_spin_g"], "omega_ss_rpm", iso_3000["omega_ss_rpm"])
    print("isolator 17000 path_g", iso_fast["path_g"], "peak_spin_g", iso_fast["peak_spin_g"])

    # Heat screens and path windows
    speeds = [200, 500, 1000, 2000, 3000, 8000, 17000]
    alts = [0.0, 4000.0, 11000.0, 30000.0, 50000.0, 80000.0]
    screens = heat_screens_at_speeds(speeds, alts)
    print("sample Teq SL 3000 mph", next(r for r in screens if r["speed_mph"]==3000 and r["h_m"]==0)["Teq_C"], "C")
    print("sample Teq 30km 1000 mph", next(r for r in screens if r["speed_mph"]==1000 and r["h_m"]==30000)["Teq_C"], "C")

    veh20 = vehicle_from_mass(20.0, "cfrp", hollow_k=0.8)
    heat_low = simulate_heat_path(3000*MPH, "straight", 80, veh20["mass"], veh20["cd"], veh20["area"], 3*G_STD, h0=0.0, dt=0.02)
    heat_high = simulate_heat_path(17000*MPH, "flatten", 50, veh20["mass"], veh20["cd"], veh20["area"], 100*G_STD,
                                   h0=0.0, evac_until_h=80000.0, evac_frac=1.0, theta1_deg=8, dt=0.02)
    heat_high_open = simulate_heat_path(3000*MPH, "flatten", 80, veh20["mass"], veh20["cd"], veh20["area"], 10*G_STD,
                                        h0=30000.0, theta1_deg=15, dt=0.02)
    print("heat low peak Teq/Tskin", heat_low["peak_Teq_K"], heat_low["peak_Tskin_K"])
    print("heat evac-high peak", heat_high["peak_Teq_K"], heat_high["peak_Tskin_K"])
    print("heat 30km 3000 peak", heat_high_open["peak_Teq_K"], heat_high_open["peak_Tskin_K"])
    for label, hp in (("low", heat_low), ("evac17000", heat_high), ("h30_3000", heat_high_open)):
        for name, m in hp["materials"].items():
            print(f"  {label} {name}: band {m['t_in_band_s']:.2f}s over {m['t_over_degrade_s']:.2f}s grown {m['grown_kg']:.4f} abl {m['ablated_kg']:.4f} miss {m['missing_cells_end']}")

    hb = hollow_table()
    print("hollow bones", hb)

    figs = make_figures(rows, screens, [heat_low, heat_high, heat_high_open], iso_3000, OUT)
    print("figures", figs)

    def heat_brief(hp):
        return {k: hp[k] for k in hp if k != "series"} | {
            "n_series": len(hp.get("series") or []),
            "Teq_peak_C": hp["peak_Teq_K"] - 273.15,
            "Tskin_peak_C": hp["peak_Tskin_K"] - 273.15,
        }

    out = {
        "constants": {
            "V_CIRC_200KM": V_CIRC_200KM, "stage_dv_300s": stage_dv(ISP_STORABLE),
            "stage_dv_450s": stage_dv(ISP_LH2), "FP_STAGE": FP_STAGE,
            "K_SG": K_SG, "R_NOSE_m": R_NOSE, "materials": {
                n: {"T_melt_C": m["T_melt_K"]-273.15, "T_degrade_C": m["T_degrade_K"]-273.15,
                    "H_abl_J_kg": m["H_abl_J_kg"]} for n, m in MATERIALS.items()
            },
        },
        "ledger": {"loaded": ledger["loaded"], "hits": ledger["hits"], "misses": ledger["misses"],
                   "undetermined_prior": len(ledger["undetermined_keys"]),
                   "undetermined_keys": ledger["undetermined_keys"]},
        "uncap": uncap_sum,
        "search": {
            "n_candidates": len(candidates),
            "n_reached_karman": len(reached_rows),
            "top": reached_rows[:12],
            "all_compact": [
                {k: r[k] for k in r if k != "cfg"} | {"cfg": r["cfg"]}
                for r in rows
            ],
        },
        "onboard_mc": mc,
        "onboard_mc_staged_lh2_horizontal": mc_staged if "mc_staged" in dir() else None,
        "lift_vs_ballistic_best": {
            k: lift_cmp[k] for k in lift_cmp
        } if lift_cmp else None,
        "lift_vs_ballistic_3000_80": mid_cmp,
        "lift_cases_low_altitude": lift_cases,
        "hollow_bones": hb,
        "isolator_3000mph_1200rpm_shell": {k: iso_3000[k] for k in iso_3000 if k != "series"},
        "isolator_17000mph_1200rpm_shell": {k: iso_fast[k] for k in iso_fast if k != "series"},
        "heat_screens": screens,
        "heat_paths": {
            "sea_level_3g_3000mph_80_straight": heat_brief(heat_low),
            "evac80km_100g_17000mph_flatten": heat_brief(heat_high),
            "h30km_10g_3000mph_flatten": heat_brief(heat_high_open),
        },
        "figures": [str(p) for p in figs],
        "assumptions": [
            "Speculative modeling only; not a design or operational claim.",
            "Sutton-Graves K=1.83e-4, Rn=0.02 m, eps=0.8 are labeled proxies, not CFD.",
            "Melt/degrade temperatures are textbook-order values, grade-dependent.",
            "H_abl, feed rate, filament budget fraction, skin mass fraction are assumptions.",
            "Jet 50 m/s and 5 m/s updraft are assumptions; lift neglected above 40 km.",
            "Isolator c/I=0.05 /s and Kp/I=8 /s are labeled; 1200 rpm shell is a concept-order spin, not a vendor spec.",
            "Upper-stage Isp 300/450 s and fp=0.85 are optimistic labeled values.",
            "Settled graph, pose, NaCl, damper, and determined 3 g 1000-3000 mph climbs were not re-integrated on the rail (exits were reused).",
        ],
    }
    (OUT / "goal_seek_recycle.json").write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print("wrote", OUT / "goal_seek_recycle.json")
    # also dump heat series separately (smaller)
    (OUT / "heat_path_series.json").write_text(json.dumps({
        "low": heat_low["series"][::2],
        "evac17000": heat_high["series"][::2],
        "h30_3000": heat_high_open["series"][::2],
    }, indent=2), encoding="utf-8")
    return out


if __name__ == "__main__":
    main()
