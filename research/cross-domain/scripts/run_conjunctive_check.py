#!/usr/bin/env python3
"""Cheap recycled conjunctive-loop check for the cross-domain comparison.

The published native-mesh restart (data mtimes 2026-11-27 22:18–22:24 UTC,
America/Denver 15:18–15:24) ran Oroboro components inside the monthly step
but left Dictator/Transcriber/Levy as end-of-run or per-event ledgers, and
did not apply PrinciplesGate. A later wiring (oro_native.py / params.json
at 15:43 Denver) adds an integrated monthly loop: Dictator stream ->
Transcriber -> Levy assess -> Levy-spike term in the damper, PrinciplesGate
on the Oasis score (and AdaptOrDie re-seat), Nexus state feeding the next
month. This script recycles the same levers, cancers, and seed rule, and
compares isolated (pre-integration flags) vs conjunctive (integrated flags).
It does not re-derive cascade rates or re-fly the rails.

A second, non-integrating pass takes already-settled leftovers from both
domains, registers them in Nexus, polarity-locks lever-vs-leftover edges
with charges equal to the documented sign of association, recombines the
two domain residuals, and runs PrinciplesGate + OasisWorld on short fact
texts. Oasis text routing is reported with the Goldilocks caveat: the gate
scores and routes; it is not a judgment of scientific truth.

Speculative modeling only. No biological, clinical, or operational claims.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
NATIVE = ROOT.parent / "metastasis-native"  # was /workspace/oroboro-research/metastasis_native
LAUNCH = ROOT.parent / "magnetic-launch"  # was /workspace/oroboro-research/magnetic_launch_case_study
OUT = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(NATIVE))
sys.path.insert(0, os.environ.get("OASIS_BRIDGE", "/workspace/oasis-build/SkyAriOasis/Bridge"))  # Oasis bridge (sky-ari-ai build) on the project computer
sys.path.insert(0, str(ROOT.parent.parent / "consciousness-mapping"))  # this repo

from oro_native import load_params, run, NEUTRAL  # noqa: E402
import oasis_core as core  # noqa: E402
import nacl_polarity_mesh as nacl  # noqa: E402

CANCERS = None
P = None
LEV_KEYS = [
    "shed_mult", "circ_clear_mult", "dorm_clear_mult", "dorm_maintenance",
    "organ_perm_scale", "pref_perm_scale", "valuation_threshold",
    "colonization_barrier", "start_month",
]

ISOLATED = dict(integrated=False, principles_gate=False, levy_feedback=False)
CONJUNCTIVE = dict(integrated=True, principles_gate=True, levy_feedback=True)

LAB_POSITION = {"x": 2.0, "y": 1.0, "z": -2.0}  # same operator-chosen lab coord as Goldilocks


def _init():
    global P, CANCERS
    P = load_params()
    CANCERS = list(P["cancers"])


def _one(args):
    cancer, seed, lever, overrides = args
    return run(cancer, seed, P, lever=lever, native_overrides=overrides)


def run_condition(lever, nseed, overrides, n_workers=7):
    tasks = []
    for c in CANCERS:
        cs = P["cancers"][c]["seed"]
        for k in range(nseed):
            tasks.append((c, cs * 1000 + k, lever, overrides))
    if n_workers <= 1 or len(tasks) < 16:
        return [_one(t) for t in tasks]
    with ProcessPoolExecutor(max_workers=n_workers, initializer=_init) as ex:
        return list(ex.map(_one, tasks, chunksize=max(1, len(tasks) // (n_workers * 8))))


def summarize(rows, condition="", experiment=""):
    if not rows:
        return {}
    def col(k, default=0.0):
        return np.array([r.get(k, default) for r in rows], dtype=float)
    overt = col("overt")
    dorm = col("dorm_alive")
    out = dict(
        condition=condition, experiment=experiment, runs=len(rows),
        shed_mean=float(col("shed").mean()),
        p_overt_any=float((overt > 0).mean()),
        overt_mean=float(overt.mean()),
        dorm_alive_mean=float(dorm.mean()),
        levy_mean=float(col("levy").mean()),
        n_frustrated_mean=float(col("n_frustrated").mean()),
        n_frustrated_series_mean=float(col("n_frustrated_mean").mean()),
        n_repaired_mean=float(col("n_repaired").mean()),
        dorm_on_frustrated_mean=float(col("dorm_on_frustrated").mean()),
        damper_pressure_mean=float(col("damper_pressure").mean()),
        pressure_max_mean=float(col("pressure_max").mean()),
        pressure_mean_mean=float(col("pressure_mean").mean()),
        gate_commit_mean=float(col("gate_commit").mean()),
        gate_buffer_mean=float(col("gate_buffer").mean()),
        gate_recycle_mean=float(col("gate_recycle").mean()),
        adapted_mean=float(col("adapted").mean()),
        transcriber_entries_mean=float(col("transcriber_entries").mean()),
        pipeline_levy_ok=bool(all(r.get("pipeline_levy_ok", True) for r in rows)),
        census_ok=bool(all(r["census_ok"] for r in rows)),
        levy_ok=bool(all(r["levy_ok"] for r in rows)),
        consensus_ok=bool(all(r["consensus_ok"] for r in rows)),
        inversion_holds=bool(all(r["inversion_holds"] for r in rows)),
        genesis_closed=bool(all(r.get("genesis_closed", True) for r in rows)),
    )
    return out


def bootstrap_spearman(x, y, n_boot=2000, seed=42):
    rng = np.random.default_rng(seed)
    x = np.asarray(x, float); y = np.asarray(y, float)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    r, p = stats.spearmanr(x, y)
    boots = []
    n = len(x)
    for _ in range(n_boot):
        i = rng.integers(0, n, n)
        try:
            boots.append(stats.spearmanr(x[i], y[i]).correlation)
        except Exception:
            boots.append(np.nan)
    lo, hi = np.nanpercentile(np.array(boots, float), [2.5, 97.5])
    return dict(r=float(r), p=float(p), ci_lo=float(lo), ci_hi=float(hi), n=int(n))


def key_levers():
    return [
        ("baseline", dict(NEUTRAL)),
        ("valuation_threshold=0.80", dict(NEUTRAL, valuation_threshold=0.80)),
        ("valuation_threshold=0.85", dict(NEUTRAL, valuation_threshold=0.85)),
        ("organ_perm_scale=0.4", dict(NEUTRAL, organ_perm_scale=0.4)),
        ("organ_perm_scale=0.2", dict(NEUTRAL, organ_perm_scale=0.2)),
        ("dorm_clear_mult=10", dict(NEUTRAL, dorm_clear_mult=10.0)),
        ("dorm_maintenance=1.0", dict(NEUTRAL, dorm_maintenance=1.0)),
        ("colonization_barrier=0.5", dict(NEUTRAL, colonization_barrier=0.5)),
    ]


def tilt_levers():
    return [
        ("tilt=0.0", dict(NEUTRAL), dict(tilt=0.0, torque_phase=0.0)),
        ("tilt=0.3", dict(NEUTRAL), dict(tilt=0.3, torque_phase=0.0)),
        ("tilt=0.6", dict(NEUTRAL), dict(tilt=0.6, torque_phase=0.0)),
    ]


def lever_from_row(row):
    lev = dict(NEUTRAL)
    for k in LEV_KEYS:
        lev[k] = int(row[k]) if k == "start_month" else float(row[k])
    if pd.isna(lev["valuation_threshold"]):
        lev["valuation_threshold"] = None
    return lev


def run_cancer_check(nseed_key=40, nseed_corr=16, n_corr_settings=40, n_workers=7):
    _init()
    t0 = time.time()
    rows_out = []

    # Key settings, both wirings. 40 seeds x 5 cancers, same seed rule as run_priority.
    for cname, lev in key_levers():
        for exp, flags in (("isolated", ISOLATED), ("conjunctive", CONJUNCTIVE)):
            recs = run_condition(lev, nseed_key, flags, n_workers=n_workers)
            s = summarize(recs, cname, exp)
            rows_out.append(s)
            print(f"  key {cname:28s} {exp:12s} dorm={s['dorm_alive_mean']:.3f} "
                  f"pcol={s['p_overt_any']:.3f} Pmax={s['pressure_max_mean']:.4f} "
                  f"adapt={s['adapted_mean']:.2f}", flush=True)

    # Tilt probe, both wirings (tilt overlay on flags)
    for cname, lev, tilt in tilt_levers():
        for exp, flags in (("isolated", ISOLATED), ("conjunctive", CONJUNCTIVE)):
            ov = dict(flags, **tilt)
            recs = run_condition(lev, nseed_key, ov, n_workers=n_workers)
            s = summarize(recs, cname, exp)
            rows_out.append(s)
            print(f"  tilt {cname:28s} {exp:12s} dorm={s['dorm_alive_mean']:.3f} "
                  f"pcol={s['p_overt_any']:.3f}", flush=True)

    key_df = pd.DataFrame(rows_out)

    # Stratified 454 subsample for Spearman of frustrated-edge count vs dormant pool
    sweep = pd.read_csv(NATIVE / "data" / "sweep_454_native.csv")
    # keep unique lever rows in original order; take evenly spaced indices
    idx = np.linspace(0, len(sweep) - 1, n_corr_settings).round().astype(int)
    idx = np.unique(idx)
    corr_rows = []
    for exp, flags in (("isolated", ISOLATED), ("conjunctive", CONJUNCTIVE)):
        xs, ys = [], []
        for i in idx:
            row = sweep.iloc[int(i)]
            lev = lever_from_row(row)
            recs = run_condition(lev, nseed_corr, flags, n_workers=n_workers)
            s = summarize(recs, f"s{int(i)}", exp)
            s.update({k: (None if (k == "valuation_threshold" and pd.isna(row[k])) else (int(row[k]) if k == "start_month" else float(row[k])))
                      for k in LEV_KEYS})
            corr_rows.append(s)
            xs.append(s["n_frustrated_mean"])
            ys.append(s["dorm_alive_mean"])
            print(f"  corr {exp:12s} i={int(i):3d} dorm={s['dorm_alive_mean']:.3f} frust={s['n_frustrated_mean']:.2f}", flush=True)
        corr = bootstrap_spearman(xs, ys)
        corr["experiment"] = exp
        print(f"  SPEARMAN {exp} frustrated vs dormant: r={corr['r']:.3f} "
              f"CI {corr['ci_lo']:.3f}–{corr['ci_hi']:.3f} n={corr['n']}", flush=True)
        if exp == "isolated":
            isolated_corr = corr
        else:
            conjunctive_corr = corr

    corr_df = pd.DataFrame(corr_rows)
    elapsed = time.time() - t0
    return dict(key=key_df, corr=corr_df, isolated_corr=isolated_corr,
                conjunctive_corr=conjunctive_corr, elapsed_s=elapsed,
                nseed_key=nseed_key, nseed_corr=nseed_corr, n_corr_settings=int(len(idx)))


# ----- Launch + cross-domain conjunctive ledger (no new flights) -----

class OroboroNexus:
    def __init__(self):
        self.registry = {}
        self.archive = []
        self.metrics = {"deltas": 0, "reconciliations": 0, "isolations": 0}

    def register(self, id, data):
        self.registry[id] = {**data, "weight": data.get("weight", 1)}
        self.archive.append({"type": "register", "id": id, "data": data})


class OroboroTranscriber:
    def __init__(self):
        self.chronicles = []
        self.anonymousLog = []

    def ingest(self, transcript, source="dictator"):
        critical = any(k in (transcript or "").lower()
                       for k in ("emergency", "mayday", "alert", "degraded", "isolate", "invalid"))
        entry = {"text": transcript, "source": source, "critical": critical}
        self.chronicles.append(entry)
        if critical:
            self.anonymousLog.append(entry)
        return entry


class OroboroDictator:
    def __init__(self, transcriber):
        self.transcriber = transcriber
        self.active = False

    def start(self):
        self.active = True

    def stop(self):
        self.active = False

    def processAudioText(self, raw):
        if not self.active:
            return None
        return self.transcriber.ingest(raw.strip(), "live-radio")


class OroboroLevy:
    def __init__(self, transcriber):
        self.transcriber = transcriber
        self.totalWeight = 0
        self.entries = []

    def assess(self, entry, weight):
        self.totalWeight += weight
        rec = {**entry, "weight": weight, "levied": True}
        self.entries.append(rec)
        self.transcriber.chronicles.append({**rec, "source": "levy"})
        return weight


class OroboroGenesis:
    def __init__(self):
        self.rootTag = "I am the OG avatar"
        self.foundationalWeight = math.inf


class OroboroRelationalSim:
    def __init__(self, nexus):
        self.nexus = nexus

    def processIndependent(self, sector_id, local_delta):
        self.nexus.metrics["deltas"] += 1
        return {"sectorId": sector_id, "delta": float(local_delta),
                "local": self.nexus.registry.get(sector_id)}

    def recombine(self, outcomes, damping=0.0):
        # Deterministic residual: RMS spread, then viscous damping. No Math.random.
        deltas = np.array([o["delta"] for o in outcomes], dtype=float)
        spread = float(np.sqrt(np.mean(deltas ** 2))) if len(deltas) else 0.0
        residual = spread * (1.0 - max(0.0, min(1.0, damping)))
        coherent = residual < 0.2
        self.nexus.metrics["reconciliations"] += 1
        return {"n": len(outcomes), "spread": spread, "residual": residual,
                "damping": damping, "matchedWholeSystem": bool(coherent),
                "mean_delta": float(deltas.mean()) if len(deltas) else 0.0}


def run_cross_ledger():
    """Register recycled leftovers from both domains and run one conjunctive pass."""
    geo = json.loads((LAUNCH / "outputs" / "geography.json").read_text())
    sites = geo["sites"]

    # Documented residuals (geography addendum / goal-seek continuation)
    launch_leftovers = {
        "evac_dart_407_parent": 407.0,
        "tilt5_431_parent": 431.0,
        "tilt0_333_parent_no_climb": 333.0,
        "staged_reported_256_INVALID": 256.0,
        "staged_kepler_true": 1148.0,
        "equator_5deg_residual": 375.0,  # geography: 375 m/s at equator for 5° tilt
        "closed_loop_staged_residual": 744.0,  # vs open-loop 325
        "closed_loop_unstaged_apogee_km": 50.2,  # vs open-loop 115.1
    }
    # Ranked 0° residuals at listed sites (documented)
    site_res0 = []
    for s in sites:
        # tolerate either naming
        r0 = s.get("residual_0deg") or s.get("r0") or s.get("tilt0_residual") or s.get("residual_0")
        name = s.get("name") or s.get("site") or s.get("id")
        lat = s.get("lat") or s.get("latitude")
        if r0 is None:
            # inspect keys once
            continue
        site_res0.append({"name": name, "lat": lat, "residual_0": float(r0),
                          "ocean": s.get("ocean") or s.get("downrange_ocean") or s.get("ocean_east")})

    # If site residual field names differ, parse from the first site keys
    if not site_res0:
        sample = sites[0]
        # try common patterns in this file
        # we'll fill from known table if needed after inspecting
        pass

    genesis = OroboroGenesis()
    transcriber = OroboroTranscriber()
    dictator = OroboroDictator(transcriber)
    levy = OroboroLevy(transcriber)
    nexus = OroboroNexus()
    sim = OroboroRelationalSim(nexus)

    nexus.register("genesis", {"kind": "origin", "status": "seeded",
                               "weight": math.inf, "tag": genesis.rootTag})
    dictator.start()
    dictator.processAudioText(
        "Cross-domain ledger. Native-mesh cascade leftover: dormant pool about 10.36 cells "
        "at baseline; post-settling maintenance leaves about 10.5. Upstream Oasis threshold "
        "and organ permissiveness shrink both colonies and the pool. Frustrated-edge count "
        "anti-tracks the pool (Spearman -0.819) because adaptive repair unlocks odd loops. "
        "Launch leftover: no-stage evac dart 407 m/s, 5 degree tilt 431 m/s at 80 km. "
        "Y(c) was not met. Equatorial boost about 465 m/s does not close that gap "
        "(equator 5 degree residual 375 m/s). The 256 m/s staged figure is invalid; "
        "true Kepler residual is 1148 m/s. Closed-loop gamma law hurt insertion."
    )
    levy.assess({"text": "dictator_ingest of recycled cross-domain ledger", "source": "dictator"}, 1)
    dictator.stop()

    # Independent parts: normalize leftovers to a unit baseline so recombination is bookkeeping
    cancer_parts = [
        ("cancer_baseline_pool", 10.355 / 10.355),          # 1.0 leftover
        ("cancer_upstream_thr_0.85", 0.140 / 10.355),       # shrunk
        ("cancer_upstream_perm_0.2", 0.046 / 10.355),
        ("cancer_postsettle_maint", 10.562 / 10.355),       # leftover remains
        ("cancer_tilt_0.6_pool", 15.1925 / 10.355),         # worse
    ]
    launch_parts = [
        ("launch_evac_dart", 407.0 / 407.0),
        ("launch_tilt5", 431.0 / 407.0),
        ("launch_equator_5deg", 375.0 / 407.0),             # slight shrink, not closed
        ("launch_baikonur_0deg", 66.0 / 407.0),             # geography admission, 0° case
        ("launch_staged_true", 1148.0 / 407.0),             # invalid 256 corrected
        ("launch_closed_loop_staged", 744.0 / 407.0),       # worse than open-loop 325
    ]
    outcomes_raw = []
    outcomes_damped = []
    for sid, delta in cancer_parts + launch_parts:
        domain = "cancer" if sid.startswith("cancer") else "launch"
        nexus.register(sid, {"kind": "leftover_part", "status": "independent",
                             "domain": domain, "normalized_leftover": delta})
        outcomes_raw.append(sim.processIndependent(sid, local_delta=delta))
        # damper meters spikes only; it does not invent a closed leftover
        outcomes_damped.append(sim.processIndependent(sid, local_delta=max(0.0, delta - 1.0) + min(1.0, delta) * 0.0 + delta))
        # The line above is wrong-headed if I'm inventing damping. Use a simple
        # documented rule: damping shrinks the *spread* in recombine(), not the mean leftover.
        levy.assess({"text": sid, "source": domain}, weight=7 if domain == "cancer" else 2)

    # Fix damped outcomes: same deltas; damping is applied in recombine, as in Goldilocks.
    outcomes_damped = [sim.processIndependent(o["sectorId"], local_delta=o["delta"]) for o in outcomes_raw]
    rec_undamped = sim.recombine(outcomes_raw, damping=0.0)
    rec_damped = sim.recombine(outcomes_damped, damping=0.25)  # Goldilocks viscous_zeta style

    # Domain-wise recombine (parts of one domain vs the other)
    rec_cancer = sim.recombine([o for o in outcomes_raw if o["sectorId"].startswith("cancer")], 0.0)
    rec_launch = sim.recombine([o for o in outcomes_raw if o["sectorId"].startswith("launch")], 0.0)

    # Polarity mesh: lever nodes vs leftover nodes. Charge of a lever is -1 if the
    # documented association with leftover size is negative (a complementary / locking
    # admission edge), +1 if the documented association is positive or the leftover
    # is not reduced (cannot lock as a fix). This is a labeled interpretation of
    # already-settled signs, not a new measurement.
    # leftover nodes are +1 (the unreconciled residue).
    signs = {
        # node: charge
        "LeftoverPool": +1,
        "LeftoverDv": +1,
        "OasisAdmissionThreshold": -1,     # raised threshold shrinks pool (native table)
        "OrganPermissiveness": -1,         # lowering perm shrinks pool
        "PostSettlingBarrier": +1,         # colonies fall, pool remains ~10.5 (same side as leftover)
        "FrustratedEdgeCount": -1,         # Spearman -0.819, moves opposite the pool
        "AdaptiveRepair": +1,              # unlocks loops in busy (high-pool) settings
        "CirculationTilt": +1,             # tilt 0.3/0.6 raises pool and colonies
        "ReleaseTilt5": -1,                # 5° at 80 km satisfies Y(a); practical residual optimum in-set
        "EquatorialBoost": -1,             # residual falls only 9–56 m/s on 5° exits; opposite but weak
        "ClosedLoopGamma": +1,             # residuals / apogee got worse
        "Staged256Claim": +1,              # invalid low residual; same side as a false closure
        "SiteLatitudeAdmission": -1,       # 0° residual falls as latitude rises (Baikonur 66)
        "HeatRegrowth": +1,                # ablates budget on the 17k mph evac path; narrow window
    }
    edges_spec = [
        ("OasisAdmissionThreshold", "LeftoverPool"),
        ("OrganPermissiveness", "LeftoverPool"),
        ("PostSettlingBarrier", "LeftoverPool"),
        ("FrustratedEdgeCount", "LeftoverPool"),
        ("AdaptiveRepair", "LeftoverPool"),
        ("CirculationTilt", "LeftoverPool"),
        ("ReleaseTilt5", "LeftoverDv"),
        ("EquatorialBoost", "LeftoverDv"),
        ("ClosedLoopGamma", "LeftoverDv"),
        ("Staged256Claim", "LeftoverDv"),
        ("SiteLatitudeAdmission", "LeftoverDv"),
        ("HeatRegrowth", "LeftoverDv"),
        # cross-domain ties: same named mechanism in both leftovers
        ("CirculationTilt", "ReleaseTilt5"),   # same name, opposite usefulness — likely same-charge / open
        ("AdaptiveRepair", "HeatRegrowth"),
        ("OasisAdmissionThreshold", "SiteLatitudeAdmission"),
        ("LeftoverPool", "LeftoverDv"),
    ]
    nodes = list(signs)
    nacl_edges = [nacl.Edge(a, b, signs[a], signs[b]) for a, b in edges_spec]
    mesh = nacl.Mesh(nodes, nacl_edges)
    mesh.process_polarities()
    mesh.apply_levy()
    cons0 = mesh.consensus()
    locked0 = [(e.node_a, e.node_b) for e in mesh.edges if e.locked]
    open0 = [(e.node_a, e.node_b) for e in mesh.edges if not e.locked]
    mesh.flip_all()
    mesh.re_stabilize()
    cons1 = mesh.consensus()
    inversion_holds = [(e.node_a, e.node_b) for e in mesh.edges if e.locked] == locked0

    # Levy bookkeeping on the mesh (0.999 locked / 0.25 open, as in nacl apply_levy
    # with periodic_grounded True applied to ALL edges equally in the stock function.
    # The weave notes used 0.999 on locked, 0.25 on open as an interpretation of those
    # two weights. Report both the stock apply_levy total and the weave-style split.)
    stock_levy = sum(e.weight for e in mesh.edges)
    weave_levy = 0.999 * len(locked0) + 0.25 * len(open0)

    # PrinciplesGate + OasisWorld on short fact / false-closure texts
    os.environ.setdefault("OASIS_VAULT", str(OUT / "oasis_vault.json"))
    cfg = core.load_config()
    gate = core.PrinciplesGate(cfg)
    world = core.OasisWorld(cfg, vault_path=None)

    def ev(text, eid, position):
        return core.make_event(text, eid, position) if hasattr(core, "make_event") else {
            "type": "CreateAnchor",
            "id": eid,
            "text": text,
            "position": position,
        }

    # oasis_core event shape from Goldilocks
    sys.path.insert(0, str(LAUNCH / "scripts"))
    # reuse Goldilocks make_event if needed
    def make_event(text, event_id, position, typ="CreateAnchor"):
        return {
            "type": typ,
            "id": event_id,
            "text": text,
            "position": position,
        }

    def compact(result):
        a = result.get("anchor") or {}
        feats = a.get("features") or {}
        return {
            "status": result.get("status"),
            "score": result.get("score"),
            "threshold": result.get("threshold"),
            "principle": result.get("principle"),
            "reason": result.get("reason"),
            "features": feats,
        }

    texts = {
        "fact_upstream_admission": (
            "Recycled native-mesh table: valuation threshold 0.85 gives colony probability 0.000 "
            "and dormant pool 0.140; organ permissiveness times 0.2 gives 0.000 and 0.046. "
            "Upstream admission shrinks both leftovers."
        ),
        "fact_post_settling_pool": (
            "Recycled native-mesh table: dormant maintenance 1.0 leaves colony probability 0.000 "
            "and dormant pool 10.562. Post-settling barriers do not empty the pool."
        ),
        "fact_yc_not_met": (
            "Recycled launch continuation: best no-stage residuals are 407 m/s and 431 m/s. "
            "No configuration reached circular speed. Y(c) was not met."
        ),
        "fact_256_invalid": (
            "Geography addendum correction: the parent 256 m/s staged residual came from a 900 s "
            "coast that had not reached apogee. Kepler two-burn residual of that state is 1148 m/s."
        ),
        "false_closure_yc_met": (
            "Claim: the equatorial boost of 465 m/s closes the 407 m/s no-stage gap and Y(c) is met."
        ),
        "false_closure_pool_empty": (
            "Claim: frustrated odd-loop edges are the dormant pool, and loop ablation empties it."
        ),
    }

    oasis_routes = {}
    # Isolated fresh world per text (new OasisWorld each time) AND a sequential world
    isolated_routes = {}
    for key, text in texts.items():
        w = core.OasisWorld(core.load_config(), vault_path=None)
        isolated_routes[key] = compact(w.process(make_event(text, f"iso-{key}", LAB_POSITION)))

    # AdaptOrDie: same false-closure text, no coordinate
    nopos = compact(core.OasisWorld(core.load_config(), vault_path=None).process(
        make_event(texts["false_closure_yc_met"], "iso-yc-nocoord", None)))

    # Repeated failure at the same "spot" (AdaptOrDie adapt_failures)
    fail_world = core.OasisWorld(core.load_config(), vault_path=None)
    fail_seq = []
    for i in range(6):
        fail_seq.append(compact(fail_world.process(
            make_event(texts["false_closure_yc_met"], f"fail-yc-{i}", LAB_POSITION))))

    seq_world = core.OasisWorld(core.load_config(), vault_path=None)
    sequential = []
    for key, text in texts.items():
        sequential.append({"key": key, "result": compact(seq_world.process(
            make_event(text, f"seq-{key}", LAB_POSITION)))})

    # Direct PrinciplesGate checks (not the text scorer)
    pg = {
        "false_closure_no_coordinate": _gate_to_dict(gate.check(
            "CreateAnchor", None, texts["false_closure_yc_met"], utility=0.9)),
        "fact_yc_not_met_with_lab_coord": _gate_to_dict(gate.check(
            "CreateAnchor", (LAB_POSITION["x"], LAB_POSITION["y"], LAB_POSITION["z"]),
            texts["fact_yc_not_met"], utility=0.65)),
        "empty_payload": _gate_to_dict(gate.check(
            "CreateAnchor", (2.0, 1.0, -2.0), "  ", utility=0.5)),
    }

    return {
        "note": (
            "Charges on the polarity mesh are a labeled interpretation of documented "
            "association signs. Oasis text scores use the existing salience engine and "
            "are not a scientific verdict. Residuals and pool sizes are recycled, not recomputed."
        ),
        "nexus_n_registered": len(nexus.registry),
        "levy_total": levy.totalWeight,
        "transcriber_n": len(transcriber.chronicles),
        "transcriber_critical": len(transcriber.anonymousLog),
        "recombine_all_undamped": rec_undamped,
        "recombine_all_damped_zeta_0.25": rec_damped,
        "recombine_cancer_parts": rec_cancer,
        "recombine_launch_parts": rec_launch,
        "polarity": {
            "n_nodes": len(nodes),
            "n_edges": len(nacl_edges),
            "n_locked": len(locked0),
            "n_open": len(open0),
            "locked_edges": [f"{a}—{b}" for a, b in locked0],
            "open_edges": [f"{a}—{b}" for a, b in open0],
            "inversion_holds": inversion_holds,
            "stock_apply_levy_total": stock_levy,
            "weave_style_levy_0.999_locked_0.25_open": weave_levy,
            "charge_rule": "lever charge = -1 if documented association with leftover size is negative, else +1; leftover nodes +1",
        },
        "principles_gate_direct": pg,
        "oasis_isolated_fresh_world": isolated_routes,
        "oasis_false_closure_no_coordinate": nopos,
        "oasis_repeated_false_closure_same_coord": fail_seq,
        "oasis_sequential": sequential,
        "site_residual_fields_sample": list(sites[0].keys()) if sites else [],
        "recycled_launch_leftovers": launch_leftovers,
    }


def _gate_to_dict(g):
    return dict(allowed=g.allowed, principle=g.principle, explanation=g.explanation,
                utility=g.utility, notes=list(g.notes or []))


def main():
    print("=== conjunctive vs isolated cancer check ===", flush=True)
    cancer = run_cancer_check()
    key_df = cancer["key"]
    corr_df = cancer["corr"]
    key_df.to_csv(OUT / "conjunctive_vs_isolated_key.csv", index=False)
    corr_df.to_csv(OUT / "conjunctive_vs_isolated_corr.csv", index=False)

    print("=== cross-domain conjunctive ledger (recycled leftovers) ===", flush=True)
    ledger = run_cross_ledger()

    payload = {
        "status": "Speculative modeling only. No biological, clinical, or operational claims.",
        "prepared": "2026-11-27 America/Denver",
        "cancer_check": {
            "nseed_key": cancer["nseed_key"],
            "nseed_corr": cancer["nseed_corr"],
            "n_corr_settings": cancer["n_corr_settings"],
            "elapsed_s": cancer["elapsed_s"],
            "isolated_spearman_frustrated_vs_dormant": cancer["isolated_corr"],
            "conjunctive_spearman_frustrated_vs_dormant": cancer["conjunctive_corr"],
            "key_settings": key_df.to_dict(orient="records"),
        },
        "cross_ledger": ledger,
        "published_native_is_isolated_wiring": (
            "Published Native_Mesh_Restart_HeatTrace.md results (data 15:18–15:24 Denver) "
            "match the isolated flags: integrated=False, principles_gate=False, levy_feedback=False. "
            "params.json later set those flags True (15:43 Denver). This check compares both."
        ),
    }
    (OUT / "conjunctive_check.json").write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print("Wrote", OUT / "conjunctive_check.json")
    print("Elapsed cancer check", f"{cancer['elapsed_s']:.1f}s")
    # print key comparison compactly
    piv = key_df.pivot_table(index="condition", columns="experiment",
                             values=["dorm_alive_mean", "p_overt_any", "pressure_max_mean",
                                     "damper_pressure_mean", "adapted_mean", "n_frustrated_mean"])
    print(piv.to_string())


if __name__ == "__main__":
    main()
