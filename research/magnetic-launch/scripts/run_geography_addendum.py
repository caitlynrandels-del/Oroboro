#!/usr/bin/env python3
# NON-CONJUNCTIVE (audit 2026-11-27): NO Oroboro component calls (physics re-evaluation of recycled exits).
# Kept for history; results are pre-integration. The conjunctive baseline (all Oroboro
# components on one loop) is research/metastasis-native (integrated=True) and
# research/cross-domain/scripts/run_conjunctive_check.py; an integrated launch rebuild is pending.
# Speculative modeling only. No engineering, flight or operational claims.
"""Geography layer on settled frontier configs only.

Earth-rotation boost, inclination limits, and site ranking.
Does not re-run the rail search, graphs, or pose work.
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
MU, RE, G_STD, MPH = G.MU_EARTH, G.R_EARTH, G.G_STD, G.MPH
# Stated boost law: v = 465.1 * cos(lat) m/s. This is ω * R_eq
# with WGS84 R_eq = 6,378,137 m and ω = 7.292115e-5 rad/s.
V_ROT0 = 465.1
R_EQ = 6_378_137.0


def v_rot_surface(lat_deg: float) -> float:
    return V_ROT0 * math.cos(math.radians(lat_deg))


def v_rot_at_altitude(lat_deg: float, h_m: float) -> float:
    """Surface law scaled by (R_eq + h)/R_eq. About +5.8 m/s at the equator at 80 km."""
    return v_rot_surface(lat_deg) * (R_EQ + max(0.0, h_m)) / R_EQ


def kepler_from_state(h_m, v, gamma_deg):
    """Osculating elements from (altitude, speed, flight-path angle) in inverse-square gravity."""
    r = RE + h_m
    gam = math.radians(gamma_deg)
    vr = v * math.sin(gam)
    vt = v * math.cos(gam)
    energy = 0.5 * v * v - MU / r
    h_ang = r * vt
    if energy >= 0:
        # hyperbolic / escape
        e = math.sqrt(1.0 + 2.0 * energy * (h_ang ** 2) / (MU ** 2)) if h_ang else 1.0
        return {
            "bound": False, "energy_J_kg": energy, "ecc": e,
            "a_m": float("inf") if energy == 0 else -MU / (2.0 * energy),
            "h_apogee_m": None, "h_perigee_m": None,
            "v_at_apogee_m_s": None,
        }
    a = -MU / (2.0 * energy)
    e = math.sqrt(max(0.0, 1.0 + 2.0 * energy * (h_ang ** 2) / (MU ** 2)))
    ra = a * (1.0 + e)
    rp = a * (1.0 - e)
    v_apo = math.sqrt(max(0.0, MU * (2.0 / ra - 1.0 / a)))
    return {
        "bound": True, "energy_J_kg": energy, "ecc": e, "a_m": a,
        "h_apogee_m": ra - RE, "h_perigee_m": rp - RE,
        "v_at_apogee_m_s": v_apo,
        "v_circ_apogee_m_s": math.sqrt(MU / ra),
        "dv_circularize_at_apogee_m_s": math.sqrt(MU / ra) - v_apo,
    }


def add_eastward_boost(v, gamma_deg, lat_deg, h_m, use_altitude_factor=True):
    boost = v_rot_at_altitude(lat_deg, h_m) if use_altitude_factor else v_rot_surface(lat_deg)
    gam = math.radians(gamma_deg)
    vh = v * math.cos(gam) + boost
    vr = v * math.sin(gam)
    v2 = math.hypot(vh, vr)
    g2 = math.degrees(math.atan2(vr, vh))
    return v2, g2, boost, vh, vr


# Settled frontier exit states (recycled; not re-integrated on the rail)
CONFIGS = {
    "evac_dart_407": {
        "label": "407 m/s no-stage evac dart",
        "short": "407 m/s evac dart",
        "v_m_s": 17093.0 * MPH,          # hold-speed tube exit, 17,093 mph
        "gamma_deg": 5.0,
        "h_m": 80_000.0,
        "staged": False,
        "baseline_residual_m_s": 407.0,
        "baseline_apogee_km": 372.6,
        "mass": None, "cd": None, "area": None,  # filled at runtime
        "note": "12.6 kg hollow dart, 1,000 g rail, flatten 45°→5°, evac tube held to 80 km.",
    },
    "tilt5_431": {
        "label": "431 m/s, 5° tilt at 80 km",
        "short": "431 m/s 5° tilt",
        "v_m_s": 17_000.0 * MPH,
        "gamma_deg": 5.0,
        "h_m": 80_000.0,
        "staged": False,
        "baseline_residual_m_s": 431.0,
        "baseline_apogee_km": 342.7,
        "mass": 20.0, "cd": 0.30, "area": 0.008,
        "note": "Tilt-sweep release: 17,000 mph at 5° from 80 km, 20 kg slender dart, no stage.",
    },
    "tilt0_333": {
        "label": "333 m/s, 0° release at 80 km",
        "short": "333 m/s 0° release",
        "v_m_s": 17_000.0 * MPH,
        "gamma_deg": 0.0,
        "h_m": 80_000.0,
        "staged": False,
        "baseline_residual_m_s": 333.0,
        "baseline_apogee_km": 80.0,
        "mass": 20.0, "cd": 0.30, "area": 0.008,
        "note": "Tilt-sweep 0° (horizontal) release at 17,000 mph and 80 km. Without Earth rotation this does not climb; 80 km is apogee.",
    },
    "staged_256": {
        "label": "256 m/s staged config",
        "short": "256 m/s staged",
        "v_m_s": 3005.8427718085004 * MPH,  # rail exit before stage
        "gamma_deg": 68.77435658875122,
        "h_m": 33846.81345496688,
        "staged": True,
        "stage_dv_m_s": G.stage_dv(G.ISP_LH2),
        "stage_mode": "horizontal",
        "fp": G.FP_STAGE,
        "baseline_residual_m_s": 256.47058607208237,
        "baseline_apogee_km": 1132.7898299885635,
        "mass": 125.59297999321456,
        "cd": None, "area": None,
        "note": "125.6 kg hollow-scaled, 50 g, 3,000 mph, start 30 km, flatten unfinished (exit 68.8°), then I_sp=450 s, f_p=0.85 horizontal stage.",
    },
}

# Public coordinates. Elevations are published site or summit values.
# downrange_east: what a due-east launch overflies first.
SITES = [
    {"id": "equator_ref", "name": "Equator (reference)", "lat": 0.0, "lon": 0.0, "elev_m": 0.0,
     "kind": "reference", "downrange_east": "n/a (reference point, not a site)",
     "ocean_east": None, "jet_latitude": False,
     "source": "Idealized 0° latitude at sea level, for the boost law only."},
    {"id": "kourou", "name": "Kourou (CSG)", "lat": 5.2372, "lon": -52.7681, "elev_m": 10.0,
     "kind": "spaceport", "downrange_east": "Atlantic Ocean",
     "ocean_east": True, "jet_latitude": False,
     "source": "Guiana Space Centre / ELA-3 area; 5°14′14″N 52°46′05″W, coastal."},
    {"id": "chimborazo", "name": "Chimborazo, Ecuador", "lat": -1.4692, "lon": -78.8175, "elev_m": 6263.0,
     "kind": "equatorial_mountain", "downrange_east": "Andes then Amazon (land) for several hundred km",
     "ocean_east": False, "jet_latitude": False,
     "source": "Summit 1.469°S, 78.817°W, 6,263 m. Near-equator high mountain, not a spaceport."},
    {"id": "kilimanjaro", "name": "Kilimanjaro, Tanzania", "lat": -3.0758, "lon": 37.3533, "elev_m": 5895.0,
     "kind": "equatorial_mountain", "downrange_east": "Kenya land, then Indian Ocean after a few hundred km",
     "ocean_east": False, "jet_latitude": False,
     "source": "Kibo / Uhuru Peak 3.076°S, 37.353°E, 5,895 m. Not a spaceport."},
    {"id": "sriharikota", "name": "Sriharikota (SDSC)", "lat": 13.7199, "lon": 80.2304, "elev_m": 3.0,
     "kind": "spaceport", "downrange_east": "Bay of Bengal",
     "ocean_east": True, "jet_latitude": False,
     "source": "Satish Dhawan Space Centre, First Launch Pad area, 13.720°N, 80.230°E, coastal."},
    {"id": "wenchang", "name": "Wenchang, Hainan", "lat": 19.6145, "lon": 110.9511, "elev_m": 10.0,
     "kind": "spaceport", "downrange_east": "South China Sea / Pacific",
     "ocean_east": True, "jet_latitude": False,
     "source": "Wenchang LC-101, 19.6145°N, 110.9511°E, coastal."},
    {"id": "mauna_kea", "name": "Mauna Kea, Hawaiʻi", "lat": 19.8207, "lon": -155.4681, "elev_m": 4207.0,
     "kind": "known_elevation_mountain", "downrange_east": "Pacific Ocean",
     "ocean_east": True, "jet_latitude": False,
     "source": "Summit 19.821°N, 155.468°W, 4,207 m. Known-elevation site, not a spaceport."},
    {"id": "cape_ksc", "name": "Cape Canaveral / KSC", "lat": 28.6082, "lon": -80.6041, "elev_m": 3.0,
     "kind": "spaceport", "downrange_east": "Atlantic Ocean",
     "ocean_east": True, "jet_latitude": False,
     "source": "Kennedy Space Center LC-39A, 28.6082°N, 80.6041°W, ~3 m."},
    {"id": "tanegashima", "name": "Tanegashima (Yoshinobu)", "lat": 30.4008, "lon": 130.9775, "elev_m": 20.0,
     "kind": "spaceport", "downrange_east": "Pacific Ocean",
     "ocean_east": True, "jet_latitude": True,
     "source": "Yoshinobu launch complex, 30.401°N, 130.977°E, coastal. Southern edge of the mid-latitude jet belt."},
    {"id": "spaceport_america", "name": "Spaceport America, NM", "lat": 32.9903, "lon": -106.9697, "elev_m": 1409.0,
     "kind": "spaceport", "downrange_east": "continental U.S. land",
     "ocean_east": False, "jet_latitude": True,
     "source": "FAA 9NM9 / published 32.990°N, 106.970°W, elevation 1,409 m (4,622 ft)."},
    {"id": "vandenberg", "name": "Vandenberg SFB", "lat": 34.5813, "lon": -120.6268, "elev_m": 25.0,
     "kind": "spaceport", "downrange_east": "continental U.S. land (site is used south over the Pacific, not due east)",
     "ocean_east": False, "jet_latitude": True,
     "source": "SLC-6, 34.581°N, 120.627°W, coastal. Due-east boost is computed but is not how the site is used."},
    {"id": "las_vegas", "name": "Las Vegas (LAS area)", "lat": 36.0840, "lon": -115.1537, "elev_m": 664.0,
     "kind": "caitlyn_region", "downrange_east": "continental U.S. land",
     "ocean_east": False, "jet_latitude": True,
     "source": "Harry Reid International (LAS), 36.084°N, 115.154°W, 664 m. A regional reference, not a spaceport."},
    {"id": "mt_charleston", "name": "Mount Charleston, NV", "lat": 36.2716, "lon": -115.6958, "elev_m": 3632.0,
     "kind": "caitlyn_region_mountain", "downrange_east": "continental U.S. land",
     "ocean_east": False, "jet_latitude": True,
     "source": "Charleston Peak, 36.272°N, 115.696°W, 3,632 m. High-desert mountain near Las Vegas, not a spaceport."},
    {"id": "mahia", "name": "Māhia, New Zealand (LC-1)", "lat": -39.26085, "lon": 177.86586, "elev_m": 104.0,
     "kind": "spaceport", "downrange_east": "Pacific Ocean",
     "ocean_east": True, "jet_latitude": True,
     "source": "Rocket Lab LC-1, 39.26085°S, 177.86586°E, 104 m. Southern mid-latitudes; due-east over water."},
    {"id": "baikonur", "name": "Baikonur, Kazakhstan", "lat": 45.9203, "lon": 63.3422, "elev_m": 90.0,
     "kind": "spaceport", "downrange_east": "Kazakhstan / Central Asian land",
     "ocean_east": False, "jet_latitude": True,
     "source": "Gagarin's Start (Site 1/5), 45.920°N, 63.342°E, ~90 m."},
]


def evaluate_config_at_site(cfg, site, use_altitude_factor=True):
    """Apply a due-east Earth-rotation boost to a recycled exit state and recompute residual."""
    v0, g0, h = cfg["v_m_s"], cfg["gamma_deg"], cfg["h_m"]
    mass, cd, area = cfg["mass"], cfg["cd"], cfg["area"]
    # If there is a stage, apply it first (horizontal), then the boost, both in the local horizontal.
    if cfg.get("staged"):
        ang = math.radians(g0)
        v0, ang = G.apply_dv(v0, ang, cfg["stage_dv_m_s"], cfg.get("stage_mode") or "horizontal")
        g0 = math.degrees(ang)
        mass = mass * (1.0 - cfg.get("fp") or G.FP_STAGE)
    v1, g1, boost, vh, vr = add_eastward_boost(v0, g0, site["lat"], h, use_altitude_factor)
    kep = kepler_from_state(h, v1, g1)
    # Re-coast with the existing flight integrator for a residual consistent with the parent notes.
    # fly() is recorded only as a check; it can hit a 900 s cap before apogee.
    fl = G.fly(v1, g1, h, mass, cd, area, lift=False, winds=False, deploy_mode="never")
    residual_fly = fl.get("residual_200km_m_s")
    vac = None
    if kep.get("h_apogee_m") is not None and kep.get("v_at_apogee_m_s") is not None:
        vac = G.vacuum_transfer_residual(kep["h_apogee_m"], kep["v_at_apogee_m_s"])
    residual_k = vac[0] if vac else None
    return {
        "site_id": site["id"], "site": site["name"], "lat": site["lat"],
        "boost_m_s": boost, "boost_surface_m_s": v_rot_surface(site["lat"]),
        "i_min_deg": abs(site["lat"]),
        "v_rel_m_s": cfg["v_m_s"],
        "v_inertial_m_s": v1, "gamma_inertial_deg": g1,
        "v_horizontal_inertial_m_s": vh,
        "v_circ_release_m_s": G.v_circ(h),
        "horizontal_minus_circular_m_s": vh - G.v_circ(h),
        "kepler": kep,
        "apogee_km_fly": fl.get("apogee_km"),
        "fly_t_apogee_s": fl.get("t_apogee_s"),
        "fly_t_end_s": fl.get("t_end_s"),
        "residual_fly_m_s": residual_fly,
        "residual_200km_m_s": residual_k,  # Kepler two-burn; this is the ranking metric
        "residual_kepler_m_s": residual_k,
        "kepler_apogee_km": None if kep.get("h_apogee_m") is None else kep["h_apogee_m"] / 1000.0,
        "kepler_perigee_km": None if kep.get("h_perigee_m") is None else kep["h_perigee_m"] / 1000.0,
        "dv_circularize_at_apogee_m_s": kep.get("dv_circularize_at_apogee_m_s"),
        "reached_karman_kepler": (kep.get("h_apogee_m") or 0) >= 100_000.0,
        "baseline_residual_m_s": cfg["baseline_residual_m_s"],
        "delta_residual_m_s": (None if residual_k is None else residual_k - cfg["baseline_residual_m_s"]),
    }


def mountain_tube_savings(elev_m, mouth_m=80_000.0, gamma_deg=5.0):
    """StarTram-type slope: a real mountain shortens, but does not replace, a tube to 80 km."""
    remain = max(0.0, mouth_m - elev_m)
    s_full = mouth_m / math.sin(math.radians(gamma_deg))
    s_remain = remain / math.sin(math.radians(gamma_deg))
    return {
        "elev_m": elev_m, "remaining_climb_m": remain,
        "path_full_5deg_km": s_full / 1000.0,
        "path_remaining_5deg_km": s_remain / 1000.0,
        "path_saved_5deg_km": (s_full - s_remain) / 1000.0,
    }


def main():
    veh20h = G.vehicle_from_mass(20.0, "cfrp", hollow_k=0.8)
    veh200h = G.vehicle_from_mass(200.0, "cfrp", hollow_k=0.8)
    CONFIGS["evac_dart_407"]["mass"] = veh20h["mass"]
    CONFIGS["evac_dart_407"]["cd"] = veh20h["cd"]
    CONFIGS["evac_dart_407"]["area"] = veh20h["area"]
    # tilt config already has 20 kg / 0.30 / 0.008
    CONFIGS["staged_256"]["cd"] = veh200h["cd"]
    CONFIGS["staged_256"]["area"] = veh200h["area"]

    # Recompute the no-boost baseline with the same pipeline, so the delta is clean.
    equator0 = {"id": "no_boost", "name": "no boost (parent inertial frame)", "lat": 90.0,  # cos 90 = 0, but we'll skip
                "lon": 0, "elev_m": 0}
    results = {}
    for cid, cfg in CONFIGS.items():
        rows = []
        # explicit zero-boost baseline via lat=90 in the boost law would be wrong if we still fly the state;
        # just evaluate the recycled state with boost=0.
        v0, g0, h = cfg["v_m_s"], cfg["gamma_deg"], cfg["h_m"]
        mass, cd, area = cfg["mass"], cfg["cd"], cfg["area"]
        if cfg.get("staged"):
            ang = math.radians(g0)
            v0, ang = G.apply_dv(v0, ang, cfg["stage_dv_m_s"], "horizontal")
            g0 = math.degrees(ang)
            mass = mass * (1.0 - cfg["fp"])
        fl0 = G.fly(v0, g0, h, mass, cd, area, lift=False, winds=False, deploy_mode="never")
        kep0 = kepler_from_state(cfg["h_m"] if not cfg.get("staged") else cfg["h_m"], v0, g0)
        # after stage, h is still the rail-exit altitude
        vac0 = G.vacuum_transfer_residual(kep0["h_apogee_m"], kep0["v_at_apogee_m_s"]) if kep0.get("h_apogee_m") is not None else None
        baseline = {
            "apogee_km_fly": fl0["apogee_km"],
            "residual_fly_m_s": fl0["residual_200km_m_s"],
            "v_at_apogee_m_s": fl0["v_at_apogee_m_s"],
            "kepler": kep0,
            "residual_kepler_m_s": vac0[0] if vac0 else None,
            "kepler_apogee_km": None if kep0.get("h_apogee_m") is None else kep0["h_apogee_m"] / 1000.0,
            "kepler_perigee_km": None if kep0.get("h_perigee_m") is None else kep0["h_perigee_m"] / 1000.0,
            "v_state_m_s": v0, "gamma_state_deg": g0,
            "note": "Zero Earth-rotation boost; same 2-D inertial frame as the parent continuation. Kepler residual is the ranking baseline.",
        }
        print(f"BASE {cid}: fly_apo={fl0['apogee_km']:.1f} fly_res={fl0['residual_200km_m_s']:.1f}  "
              f"kep_apo={baseline['kepler_apogee_km']} kep_hp={baseline['kepler_perigee_km']} kep_res={baseline['residual_kepler_m_s']}  "
              f"(parent quoted {cfg['baseline_residual_m_s']:.1f})")
        for site in SITES:
            ev = evaluate_config_at_site(cfg, site, use_altitude_factor=True)
            rows.append(ev)
            print(f"  {site['name']:28s} lat={site['lat']:+7.3f}  boost={ev['boost_m_s']:6.1f}  "
                  f"kep_res={ev['residual_kepler_m_s']:8.1f}  dres={ev['delta_residual_m_s']:8.1f}  "
                  f"ha={ev['kepler_apogee_km']:7.1f}  hp={ev['kepler_perigee_km']:8.1f}  "
                  f"vh-vc={ev['horizontal_minus_circular_m_s']:+7.1f}  "
                  f"circ_apo={None if ev['dv_circularize_at_apogee_m_s'] is None else round(ev['dv_circularize_at_apogee_m_s'],1)}")
        # rank real sites (not the equator reference) plus include the reference in a side list
        real = [r for r in rows if r["site_id"] != "equator_ref"]
        real.sort(key=lambda r: (r["residual_200km_m_s"] is None, r["residual_200km_m_s"] if r["residual_200km_m_s"] is not None else 1e99))
        results[cid] = {"cfg": {k: cfg[k] for k in cfg}, "baseline_recomputed": baseline,
                        "rows": rows, "ranked": real}

    # Mountain-slope tube arithmetic for the high sites
    mtn = {}
    for s in SITES:
        if s["elev_m"] >= 1000:
            mtn[s["id"]] = {"name": s["name"], "lat": s["lat"], **mountain_tube_savings(s["elev_m"])}

    # Fine latitude curve for the figure (due-east, altitude factor on)
    lats = list(range(-50, 51, 2))
    curves = {}
    for cid, cfg in CONFIGS.items():
        curves[cid] = []
        for lat in lats:
            site = {"id": f"lat{lat}", "name": f"{lat}°", "lat": float(lat), "lon": 0, "elev_m": 0}
            ev = evaluate_config_at_site(cfg, site, use_altitude_factor=True)
            curves[cid].append({"lat": lat, "boost_m_s": ev["boost_m_s"],
                                "residual_200km_m_s": ev["residual_kepler_m_s"],
                                "kepler_apogee_km": ev["kepler_apogee_km"],
                                "dv_circ_apo": ev["dv_circularize_at_apogee_m_s"],
                                "h_perigee_km": ev["kepler_perigee_km"]})

    # Figure: residual vs latitude, sites overplotted
    fig, ax = plt.subplots(figsize=(6.3, 5.0))
    plot_ids = ["tilt0_333", "tilt5_431", "evac_dart_407"]
    colors = {"evac_dart_407": "#d65a31", "tilt5_431": "#1f3a5f", "tilt0_333": "#3a7d44", "staged_256": "#888888"}
    for cid in plot_ids:
        xs = [p["lat"] for p in curves[cid]]
        ys = [p["residual_200km_m_s"] / 1000.0 for p in curves[cid]]
        ax.plot(xs, ys, "-", color=colors[cid], lw=1.6, label=CONFIGS[cid]["short"])
    ax.axhline(0.0, color="#333", lw=0.7)
    label_ids = {"kourou", "cape_ksc", "las_vegas", "baikonur", "mahia",
                 "chimborazo", "wenchang", "vandenberg"}
    for r in results["tilt0_333"]["rows"]:
        ax.scatter([r["lat"]], [r["residual_kepler_m_s"] / 1000.0],
                   color=colors["tilt0_333"], s=28, zorder=4, edgecolors="k", linewidths=0.3)
        if r["site_id"] in label_ids:
            ha = "left" if r["lat"] >= 0 else "right"
            dx = 0.9 if r["lat"] >= 0 else -0.9
            ax.annotate(r["site"].split(",")[0], (r["lat"] + dx, r["residual_kepler_m_s"] / 1000.0 + 0.01),
                        fontsize=6.5, ha=ha, va="bottom")
    ax.set_xlabel("Geodetic latitude (deg, +N / −S)")
    ax.set_ylabel("Kepler two-burn residual to 200 km circular (km/s)")
    ax.set_title("Due-east residual vs latitude (vacuum, recycled exits)")
    ax.set_xlim(-52, 52)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=7)
    fig.tight_layout()
    figpath = OUT / "fig10_geography.png"
    fig.savefig(figpath, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("wrote", figpath)

    out = {
        "boost_law": "v = 465.1 * cos(lat) m/s at the surface; at altitude, multiplied by (R_eq+h)/R_eq with R_eq=6,378,137 m.",
        "V_ROT0": V_ROT0, "R_EQ_m": R_EQ,
        "target": "200 km circular at inclination i = |latitude| (no plane change). A due-east launch cannot reach a lower inclination without a plane-change burn.",
        "plane_change_note": "Δv_plane ≈ 2 v sin(Δi/2). From 36.1°N to i=0 at 7,788 m/s is about 4.8 km/s and is not part of the ranked residual.",
        "configs": results,
        "curves": curves,
        "mountain_tubes": mtn,
        "sites": SITES,
        "figure": str(figpath),
        "assumptions": [
            "Speculative modeling only; not a siting recommendation or an operational claim.",
            "Settled rail exits are recycled; only the Earth-rotation boost and the residual re-evaluation are new.",
            "Boost is applied due east, fully in the local horizontal. Off-azimuth launches get less.",
            "The parent continuation's 2-D integrator had no Earth rotation; this layer adds it at release (and after the stage, when present).",
            "Residual is the same two-burn-from-apogee metric as the parent notes.",
            "Site coordinates are published public values, rounded as listed in each source field.",
            "StarTram is named only as a well-known mountain-slope / evac-tube concept; no vendor specs are used.",
        ],
    }
    # compact json: drop bulky fly internals already absent
    (OUT / "geography.json").write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    print("wrote", OUT / "geography.json")


if __name__ == "__main__":
    main()
