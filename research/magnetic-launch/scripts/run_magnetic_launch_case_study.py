#!/usr/bin/env python3
# NON-CONJUNCTIVE (audit 2026-11-27): components exercised as ISOLATED BLOCKS (Oasis, meshes, Goldilocks sweep, dampers, relational recombine run as separate stages; Oasis did not choose rail configs; mesh locks did not change flights).
# Kept for history; results are pre-integration. The conjunctive baseline (all Oroboro
# components on one loop) is research/metastasis-native (integrated=True) and
# research/cross-domain/scripts/run_conjunctive_check.py; an integrated launch rebuild is pending.
# Speculative modeling only. No engineering, flight or operational claims.
"""Magnetic-assist / inverse-Epcot / LAS-path / damper Goldilocks case study.

Runs Caitlyn Randels's conversation-thread concept through executable
Oroboro / Oasis code on the box, then a small relational + textbook-physics
simulation. Deterministic throughout. No Math.random reconciliation stub.
Writes JSON, text, and figures under ../outputs/.
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

OASIS_BRIDGE = Path("/workspace/oasis-build/SkyAriOasis/Bridge")
NACL_DIR = Path(__file__).resolve().parents[3] / "consciousness-mapping"  # this repo (was /workspace/github-staging/Oroboro/consciousness-mapping)

RUNTIME = ROOT / "runtime"
RUNTIME.mkdir(parents=True, exist_ok=True)
os.environ["OASIS_VAULT"] = str(RUNTIME / "vault.json")
os.environ["OASIS_COMPANION_DIR"] = str(RUNTIME / "companions")
for k in ("OASIS_LLM_ENDPOINT", "OASIS_LLM_API_KEY", "OASIS_FAMILY_NAMES",
          "OASIS_FAMILY_GROUP_TAGS", "OASIS_UNTAGGED_RESONANCE"):
    os.environ.pop(k, None)

sys.path.insert(0, str(OASIS_BRIDGE))
sys.path.insert(0, str(NACL_DIR))

import oasis_core as core  # noqa: E402
import ms_minutes  # noqa: E402
import nacl_polarity_mesh as nacl  # noqa: E402

# ---------------------------------------------------------------------------
# Input text: Caitlyn's conversation thread is the PRIMARY input.
# Engineering arc (items 4-12) is scored and simulated.
# Items 1-3 (patentability, copyright, outreach) are session context only.
# ---------------------------------------------------------------------------
CONTEXT_123 = (
    "Earlier in the same conversation: patentability of Oroboro, state reduction, "
    "Vision Pro work, and metastasis modeling was discussed in general terms "
    "(Alice/Mayo, ideas unlikely to be patentable, copyright covering expression "
    "not ideas, and public GitHub disclosures). Copyright of a thought process "
    "was distinguished from copyright of code and wording. Outreach had received "
    "no responses, and practical paths for attorneys, consultants, and university "
    "or SBDC help were mentioned. Those points are session context only."
)

PRIMARY_TEXT = """
A magnetic coaster-style track with intermittent segments driven by Intamin-style
linear synchronous and linear induction motors. Sequenced magnetic pulses accelerate
or decelerate a vehicle without continuous physical contact; segments can be isolated
while whole-system control is kept, the same analogy used in the Metastasis Heat-Trace
case study for discrete detach and attach events.

Use that track idea to launch lightweight drones or supplies toward space without
full rocket fuel. Combine the track with Las Vegas Harry Reid (LAS) airplane
approach-pass trajectories as path templates, in the same observational sense as
the earlier LAS trajectory reduction that used a NaCl-style polarity mesh, Levy
weights, mesh consensus, and delta reconciliation.

The layman's biggest problem is the roughly 17,000 mph orbital-speed figure: a
track that reaches that speed under modest acceleration would be many miles long,
and a shorter track would mean crushing acceleration.

The inverse of the Epcot Spaceship Earth geodesic sphere is a concave bowl
geodesic shell, used alongside the actual sphere. Intermittent magnetic segments
sit on the bowl panels and produce a natural pitch-up, mapping onto LAS-style
passes as structured path templates.

Rockets carry propellant and engines and face vibration; they accelerate gradually
while climbing out of the atmosphere. A magnetic track that reached very high speed
while still in thick air would face a different problem. Look for a Goldilocks zone:
there is no need for super speed at the bottom. Skyscraper earthquake technology —
base isolation, tuned mass dampers, and viscous dampers — supplies a controlled
energy-absorption and force-metering logic.

A Goldilocks sketch: magnetic assist to an intermediate speed, for example about
1,000 to 3,000 mph, delivered as intermittent pulses, then a small thruster or
upper stage. Damper logic meters forces. Inverse-Epcot bowl geometry plus LAS-style
passes supply the path structure.
""".strip()

CHUNKS = {
    "intermittent_magnetic_track": (
        "A magnetic coaster-style track with intermittent segments driven by "
        "Intamin-style linear synchronous and linear induction motors. Sequenced "
        "magnetic pulses accelerate a vehicle without continuous contact; segments "
        "can be isolated while whole-system control is kept."
    ),
    "inverse_epcot_bowl": (
        "The inverse of the Epcot Spaceship Earth geodesic sphere is a concave bowl "
        "geodesic shell, used alongside the actual sphere. Intermittent magnetic "
        "segments on the bowl panels produce a natural pitch-up."
    ),
    "las_approach_templates": (
        "Combine the track with Las Vegas Harry Reid LAS airplane approach-pass "
        "trajectories as schematic path templates, using the same NaCl-style polarity "
        "mesh, Levy weights, mesh consensus, and delta reconciliation as the earlier "
        "LAS reduction, observational equivalence only."
    ),
    "seismic_dampers": (
        "Skyscraper earthquake technology — base isolation, tuned mass dampers, and "
        "viscous dampers — supplies controlled energy absorption and force-metering "
        "logic for the launch track, not operational structural design."
    ),
    "goldilocks_band": (
        "Find a Goldilocks zone for launching lightweight drones or supplies toward "
        "space without full rocket fuel: magnetic assist to an intermediate speed of "
        "about 1,000 to 3,000 mph as intermittent pulses, then a small upper stage. "
        "There is no need for super speed at the bottom. Compare honestly with the "
        "roughly 17,000 mph orbital-speed figure."
    ),
}

LAB_POSITION = {"x": 2.0, "y": 1.0, "z": -2.0}


def pos_at(i: int) -> dict:
    return {"x": 2.0 + i * 2.0, "y": 1.0, "z": -2.0}

# Textbook constants (well-known) and labeled assumptions
G_STD = 9.80665
MU_EARTH = 3.986004418e14
R_EARTH = 6.371e6
RHO0 = 1.225
H_SCALE = 8500.0  # ASSUMPTION: isothermal scale height, m
KARMAN_M = 100_000.0
LEO_ALT_M = 200_000.0  # ASSUMPTION: reference circular LEO altitude
MPH = 0.44704  # 1 mph = 0.44704 m/s exactly

V_CIRC_200KM = math.sqrt(MU_EARTH / (R_EARTH + LEO_ALT_M))
V_ESC_SURFACE = math.sqrt(2.0 * MU_EARTH / R_EARTH)
V_17000_MPH = 17000.0 * MPH
V_1000_MPH = 1000.0 * MPH
V_2000_MPH = 2000.0 * MPH
V_3000_MPH = 3000.0 * MPH

ASSUMPTIONS = {
    "scale_height_m": H_SCALE,
    "reference_leo_altitude_m": LEO_ALT_M,
    "cd_blunt": 0.50,
    "cd_slender": 0.30,
    "area_blunt_m2": 0.20,
    "area_slender_m2": 0.008,
    "masses_kg": [5.0, 20.0, 50.0],
    "duty_cycle_on_fraction": 0.50,
    "pulse_on_s": 0.40,
    "coast_s": 0.40,
    "isolator_fn_hz": 0.5,
    "isolator_zeta": 0.20,
    "tmd_mass_ratio": 0.05,
    "tmd_zeta": 0.15,
    "viscous_zeta": 0.25,
    "structure_fn_hz": 2.0,
    "bowl_radius_m": 2500.0,
    "straight_angles_deg": [30, 45, 60, 80, 90],
    "goldilocks_mph": [1000.0, 2000.0, 3000.0],
    "comparison_mph": [60.0, 200.0, 500.0, 1000.0, 2000.0, 3000.0, 5000.0, 17000.0],
    "accel_g_table": [1.0, 2.0, 3.0, 5.0, 10.0],
    "coaster_like_note": "tens of m/s; illustrative 60 mph is an order-of-magnitude assumption, not an Intamin specification",
    "intamin_note": "LSM/LIM sequenced contactless pulses are a well-known coaster architecture; no numerical Intamin motor specification is used",
    "las_templates_note": "schematic path templates only; not FAA or LAS procedures",
}

LEVY_WEIGHTS = {
    "pulse": 7, "coast": 1, "isolation_engage": 3, "damper_reconcile": 4,
    "mesh_lock": 5, "release": 8, "goldilocks_in_band": 10,
    "failed_reach_leo_speed": 2, "dictator_ingest": 1,
}


def compact(result: dict) -> dict:
    a = result.get("anchor") or {}
    feats = a.get("features") or {}
    return {
        "status": result.get("status"),
        "score": result.get("score"),
        "baseScore": a.get("baseScore"),
        "threshold": result.get("threshold"),
        "nextThreshold": result.get("nextThreshold"),
        "principle": result.get("principle"),
        "principle_name": result.get("principle") if result.get("status") == core.STATUS_BLOCKED else a.get("principle"),
        "blocked_principle": result.get("principle") if result.get("status") == core.STATUS_BLOCKED else None,
        "reason": result.get("reason"),
        "anchorId": result.get("anchorId") or a.get("id"),
        "features": feats,
        "rationale": a.get("rationale"),
        "notes": a.get("notes"),
        "word_count": len(core.tokens(a.get("text") or "")),
        "score_breakdown": (
            {
                "0.30*novelty": round(0.30 * float(feats.get("novelty") or 0), 4),
                "0.25*tension": round(0.25 * float(feats.get("tension") or 0), 4),
                "0.25*coherence": round(0.25 * float(feats.get("coherence") or 0), 4),
                "0.20*resonance": round(0.20 * float(feats.get("resonance") or 0), 4),
            }
            if feats else None
        ),
        "metrics": result.get("metrics"),
    }


def make_event(text: str, event_id: str, position, typ: str = "CreateAnchor") -> dict:
    ev = {"type": typ, "id": event_id, "text": text, "device": "magnetic-launch-case-study"}
    if position is not None:
        ev["position"] = position
    return ev


def process_fresh(text: str, event_id: str, position) -> dict:
    world = core.OasisWorld(core.load_config(), vault_path=None)
    return compact(world.process(make_event(text, event_id, position)))


def run_oasis() -> dict:
    cfg = core.load_config()
    out: Dict[str, Any] = {
        "config": {
            "weights": cfg["weights"],
            "valuation_threshold": cfg["valuation_threshold"],
            "buffer_ratio": cfg["buffer_ratio"],
            "buffer_threshold_initial": cfg["valuation_threshold"] * cfg["buffer_ratio"],
            "default_tension": cfg["reasoning"]["default_tension"],
        },
        "chosen_inputs_not_derived_from_text": {
            "position": LAB_POSITION,
            "position_source": "operator-chosen lab coordinate; required by PrinciplesGate.AdaptOrDie; not derived from text",
            "tension_source": "config default_tension=0.5 (not derived from text)",
            "comfort": 1.0,
            "frustration": 0.0,
            "resonance_source": "untagged_resonance=0.0 (no family-name match in the engineering text)",
        },
        "input_source": (
            "Caitlyn Randels conversation thread supplied as the primary input. "
            "The engineering-concept arc was scored and simulated. Items on "
            "patentability, copyright, and outreach were retained only as session context."
        ),
    }
    out["isolated_fresh_world"] = {
        "engineering_arc": {
            "text": PRIMARY_TEXT,
            "result": process_fresh(PRIMARY_TEXT, "iso-engineering-arc", LAB_POSITION),
        }
    }
    out["gate_constraint_no_position"] = {
        "note": "Same engineering-arc text, position omitted. Expected AdaptOrDie block; this is a coordinate rule, not a judgment of the concept.",
        "result": process_fresh(PRIMARY_TEXT, "iso-no-position", None),
    }
    world = core.OasisWorld(core.load_config(), vault_path=None)
    seq = []
    for i, (key, text) in enumerate(CHUNKS.items()):
        r = world.process(make_event(text, f"seq-{key}", pos_at(i)))
        seq.append({"key": key, "result": compact(r)})
    r_full = world.process(make_event(PRIMARY_TEXT, "seq-full-arc", pos_at(20)))
    out["sequential_chunks_then_full"] = {
        "results": seq,
        "full_arc_after_chunks": compact(r_full),
        "final_metrics": world.metrics(),
        "committed_ids": list(world.anchors.keys()),
        "buffered_ids": [b["id"] for b in world.buffer],
        "recycled_ids": [g["id"] for g in world.garden],
        "export_oroboro_levy": world.export_oroboro()["levy"],
    }
    out["export_oroboro"] = world.export_oroboro()
    return out


def run_companion() -> dict:
    empty = ms_minutes.MsMinutes("magnetic-launch-empty")
    r0 = empty.message("status")
    r1 = empty.message(PRIMARY_TEXT)
    seeded = ms_minutes.MsMinutes("magnetic-launch-seeded")
    seeds = [
        "remember The Metastasis Heat-Trace case study maps Intamin-style sequenced linear motors to discrete detach and attach pulses.",
        "remember A NaCl polarity mesh note applied the same Genesis-mesh-Levy-consensus-delta loop to schematic LAS airspace trajectories, observational equivalence only.",
        "remember " + CHUNKS["goldilocks_band"],
    ]
    replies = [seeded.message(s) for s in seeds]
    ask = seeded.message(
        "What does the chronicle already hold about a Goldilocks magnetic-assist launch and LAS path templates?"
    )
    return {
        "empty_chronicle": {"status_before": r0, "engineering_arc": r1, "summary_after": empty.summary()},
        "seeded_chronicle": {"remember_replies": replies, "ask": ask, "summary_after": seeded.summary()},
    }

# Faithful Python port of oroboro-core.js, with DETERMINISTIC recombine.
# The JS RelationalSim uses Math.random; that stub is not used here.
# Dictator exists in oroboro-core.js as a stream-to-text feeder into Transcriber.

class OroboroNexus:
    def __init__(self):
        self.registry: Dict[str, dict] = {}
        self.archive: List[dict] = []
        self.subscribers: List = []
        self.metrics = {"deltas": 0, "reconciliations": 0, "isolations": 0}

    def register(self, id: str, data: dict):
        self.registry[id] = {**data, "weight": data.get("weight", 1)}
        self.archive.append({"type": "register", "id": id, "data": data})
        self.telemeter("register", {"id": id, "data": data})

    def telemeter(self, event: str, payload: dict):
        for fn in self.subscribers:
            fn(event, payload)

    def subscribe(self, fn):
        self.subscribers.append(fn)

    def getIndependentState(self, sector_id: str):
        sector = self.registry.get(sector_id)
        if not sector:
            return None
        return {"local": sector, "peers": self.getPeerSummaries(sector_id)}

    def getPeerSummaries(self, sector_id: str):
        return [{"id": i, "status": d.get("status"), "kind": d.get("kind")}
                for i, d in self.registry.items() if i != sector_id]


class OroboroTranscriber:
    def __init__(self):
        self.lexicon: Dict[str, str] = {}
        self.chronicles: List[dict] = []
        self.anonymousLog: List[dict] = []

    def ingest(self, transcript: str, source: str = "dictator"):
        entry = {"text": transcript, "source": source, "critical": self.isCritical(transcript)}
        self.chronicles.append(entry)
        if entry["critical"]:
            self.anonymousLog.append(entry)
        return entry

    def isCritical(self, text: str) -> bool:
        keywords = ["emergency", "mayday", "pan pan", "alert", "degraded", "flood", "isolate"]
        low = (text or "").lower()
        return any(k in low for k in keywords)

    def query(self, term: str):
        t = term.lower()
        return [c for c in self.chronicles if t in c["text"].lower()]


class OroboroDictator:
    """Real component in oroboro-core.js. processAudioText trims text and
    feeds the Transcriber. No audio or speech-recognition ran in this study;
    the written concept text was passed through the same ingest path."""

    def __init__(self, transcriber: OroboroTranscriber):
        self.transcriber = transcriber
        self.active = False

    def start(self):
        self.active = True

    def stop(self):
        self.active = False

    def processAudioText(self, raw: str):
        if not self.active:
            return None
        return self.transcriber.ingest(raw.strip(), "live-radio")


class OroboroLevy:
    def __init__(self, transcriber: OroboroTranscriber):
        self.transcriber = transcriber
        self.totalWeight = 0.0
        self.entries: List[dict] = []

    def assess(self, entry: dict, weight: Optional[float] = None):
        if weight is None:
            weight = 10 if entry.get("critical") else 1
        self.totalWeight += weight
        levied = {**entry, "weight": weight, "levied": True}
        self.entries.append(levied)
        self.transcriber.chronicles.append(levied)
        return weight


class OroboroGenesis:
    def __init__(self):
        self.rootTag = "I am the OG avatar"
        self.foundationalWeight = math.inf
        self.origin = "magnetic-launch-case-study"

    def mirror(self, history):
        return {"origin": self.rootTag, "history": history, "weight": self.foundationalWeight}


class OroboroRelationalSim:
    """Deterministic recombine: residual is a damped RMS spread of local deltas."""

    def __init__(self, nexus: OroboroNexus):
        self.nexus = nexus

    def processIndependent(self, sector_id: str, local_delta: float):
        state = self.nexus.getIndependentState(sector_id)
        return {"sectorId": sector_id, "processed": True, "localOutcome": state, "delta": float(local_delta)}

    def recombine(self, outcomes: List[dict], damping: float = 0.25):
        if not outcomes:
            return {"observable": {"n": 0, "mean_delta": 0.0, "residual": 0.0, "coherent": True},
                    "matchedWholeSystem": True}
        deltas = [float(o["delta"]) for o in outcomes]
        mean_d = sum(deltas) / len(deltas)
        spread = math.sqrt(sum((d - mean_d) ** 2 for d in deltas) / len(deltas))
        residual = spread * (1.0 - max(0.0, min(1.0, damping)))
        self.nexus.metrics["reconciliations"] += 1
        self.nexus.metrics["deltas"] += len(deltas)
        coherent = residual < 0.2
        return {
            "observable": {
                "n": len(outcomes), "mean_delta": mean_d, "spread": spread,
                "residual": residual, "damping": damping, "coherent": coherent,
            },
            "matchedWholeSystem": coherent,
        }


def transmissibility(r: float, zeta: float) -> float:
    """SDOF force transmissibility (textbook). r = omega/omega_n."""
    num = 1.0 + (2.0 * zeta * r) ** 2
    den = (1.0 - r ** 2) ** 2 + (2.0 * zeta * r) ** 2
    if den <= 0:
        return float("inf")
    return math.sqrt(num / den)


def ringdown_peak(amp0: float, zeta: float, n_cycles: int = 8) -> float:
    """Peak remaining amplitude after n cycles: exp(-2 pi zeta n)."""
    return amp0 * math.exp(-2.0 * math.pi * zeta * n_cycles)


def icosahedron_edges():
    """Frequency-1 icosahedron, golden-ratio construction (well-known).
    Charge is a role label for mesh locking, not an electrical claim."""
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    verts = []
    for i in (-1.0, 1.0):
        for j in (-1.0, 1.0):
            verts.append((0.0, i, j * phi))
            verts.append((i, j * phi, 0.0))
            verts.append((i * phi, 0.0, j))
    names = [f"V{k}" for k in range(12)]
    edges_idx = set()
    for a in range(12):
        ds = []
        for b in range(12):
            if a == b:
                continue
            dx = verts[a][0] - verts[b][0]
            dy = verts[a][1] - verts[b][1]
            dz = verts[a][2] - verts[b][2]
            ds.append((math.sqrt(dx * dx + dy * dy + dz * dz), b))
        ds.sort()
        min_d = ds[0][0]
        for d, b in ds:
            if abs(d - min_d) < 1e-9:
                edges_idx.add(tuple(sorted((a, b))))
    edges = []
    for a, b in sorted(edges_idx):
        dz = abs(verts[a][2] - verts[b][2])
        if dz >= 0.5:
            charge_a, charge_b = 1, -1  # vertical-span / pitch-up panels lock
        else:
            charge_a, charge_b = 1, 1  # hoop-like, stay open
        edges.append(nacl.Edge(names[a], names[b], charge_a, charge_b))
    return names, edges, verts


def _mesh_snapshot(invert: bool) -> dict:
    origin = nacl.IonicOrigin()
    nodes = ["Na0", "Cl0", "Na1", "Na2"]
    edges = [
        nacl.Edge("Na0", "Cl0", origin.Na, origin.Cl),
        nacl.Edge("Na0", "Na1", origin.Na, origin.Na),
        nacl.Edge("Cl0", "Na2", origin.Cl, origin.Na),
    ]
    mesh = nacl.Mesh(nodes, edges)
    mesh.process_polarities()
    mesh.apply_levy()
    if invert:
        mesh.flip_all()
        mesh.re_stabilize()
    cons = mesh.consensus()
    return {
        "run_return": nacl.Transcriber.write(nacl.Nexus.log(cons)),
        "n_edges": len(mesh.edges),
        "n_locked": len(cons),
        "edges": [
            {"a": e.node_a, "b": e.node_b, "locked": e.locked, "state": e.state,
             "weight": e.weight, "opposite": e.opposite_charge}
            for e in mesh.edges
        ],
    }


def run_meshes() -> dict:
    nacl_false = nacl.run(invert=False)
    nacl_true = nacl.run(invert=True)
    names, edges, verts = icosahedron_edges()
    geo = nacl.Mesh(names, edges)
    geo.process_polarities()
    geo.apply_levy()
    locked_before = len(geo.consensus())
    geo.flip_all()
    geo.re_stabilize()
    locked_after = len(geo.consensus())
    bowl_verts = sum(1 for v in verts if v[2] <= 0)

    las_nodes = ["ArrivalA", "ArrivalB", "Departure", "Runway", "Hold", "Weather"]
    las_edges = [
        nacl.Edge("ArrivalA", "Runway", +1, -1),
        nacl.Edge("ArrivalB", "Runway", +1, -1),
        nacl.Edge("Departure", "Runway", +1, -1),
        nacl.Edge("Hold", "Weather", +1, -1),
        nacl.Edge("ArrivalA", "ArrivalB", +1, +1),
        nacl.Edge("ArrivalA", "Departure", +1, +1),
        nacl.Edge("Hold", "ArrivalA", +1, +1),
    ]
    las = nacl.Mesh(las_nodes, las_edges)
    las.process_polarities()
    las.apply_levy()
    cons_las = las.consensus()
    locked_las = list(cons_las)
    open_before = [f"{e.node_a}-{e.node_b}" for e in las.edges if not e.locked]
    locked_before_las = [f"{e.node_a}-{e.node_b}" for e in las.edges if e.locked]
    las.flip_all()
    las.re_stabilize()
    cons_las_inv = las.consensus()
    return {
        "note": (
            "nacl_polarity_mesh.py was executed as written. The same Mesh operators "
            "were then applied to a frequency-1 icosahedral geodesic and to a schematic "
            "LAS sector mesh. The LAS mesh is observational equivalence only and is not "
            "a model of actual ATC procedures. There is no separate stored LAS-trajectory "
            "simulator on the box beyond this polarity-mesh tie-in and the earlier note."
        ),
        "nacl_as_written": {
            "invert_false_return": nacl_false,
            "invert_true_return": nacl_true,
            "invert_false": _mesh_snapshot(False),
            "invert_true": _mesh_snapshot(True),
        },
        "geodesic_icosahedron": {
            "n_vertices": len(verts),
            "n_bowl_hemisphere_vertices_z_le_0": bowl_verts,
            "n_edges": len(edges),
            "locked_before_invert": locked_before,
            "locked_after_invert": locked_after,
            "open_after_invert": len(edges) - locked_after,
            "levy_weight_on_edges": 0.999,
            "invert_preserves_lock_count": locked_before == locked_after,
        },
        "las_sector_mesh": {
            "nodes": las_nodes,
            "n_edges": len(las_edges),
            "locked_before_invert": len(locked_las),
            "locked_after_invert": len(cons_las_inv),
            "locked_edges_before": locked_before_las,
            "open_edges_before": open_before,
            "invert_preserves_lock_count": len(locked_las) == len(cons_las_inv),
        },
    }

def rho_of(h: float) -> float:
    return RHO0 * math.exp(-max(0.0, h) / H_SCALE)


def mph(v_mps: float) -> float:
    return v_mps / MPH


def m_to_mi(m: float) -> float:
    return m / 1609.344


def track_length_continuous(v: float, a: float) -> float:
    if a <= 0:
        return float("inf")
    return (v * v) / (2.0 * a)


def track_table() -> List[dict]:
    rows = []
    duty = ASSUMPTIONS["duty_cycle_on_fraction"]
    for mph_target in ASSUMPTIONS["comparison_mph"]:
        v = mph_target * MPH
        for gmult in ASSUMPTIONS["accel_g_table"]:
            a = gmult * G_STD
            L = track_length_continuous(v, a)
            L_int = L / duty
            rows.append({
                "speed_mph": mph_target,
                "speed_m_s": round(v, 3),
                "peak_accel_g": gmult,
                "peak_accel_m_s2": round(a, 5),
                "continuous_length_m": L,
                "continuous_length_km": L / 1000.0,
                "continuous_length_mi": m_to_mi(L),
                "intermittent_length_m": L_int,
                "intermittent_length_km": L_int / 1000.0,
                "intermittent_length_mi": m_to_mi(L_int),
                "duty_cycle": duty,
                "note": "vacuum, no gravity, constant peak a; kinematic v^2/2a only",
            })
    return rows


def integrate_track(v_target, geometry, exit_angle_deg, mass, cd, area, peak_a,
                    bowl_radius, dt=0.002):
    """Integrate along a rail until v_target or a cap. Sea-level start.
    Gravity and drag always on. Pulse-on applies peak_a along the rail; coast does not.
    concave_bowl: phi rises from 0 to exit_angle (natural pitch-up), then holds.
    convex_sphere: phi falls from exit_angle toward 0 (pitch-down), then holds.
    straight: phi stays at exit_angle.
    """
    theta_exit = math.radians(exit_angle_deg)
    R = bowl_radius
    if geometry == "straight":
        phi = theta_exit
    elif geometry == "concave_bowl":
        phi = 0.0
    elif geometry == "convex_sphere":
        phi = theta_exit
    else:
        raise ValueError(geometry)

    v = 0.0
    t = 0.0
    s = 0.0
    x = 0.0
    y = 0.0
    t_on = ASSUMPTIONS["pulse_on_s"]
    t_off = ASSUMPTIONS["coast_s"]
    period = t_on + t_off
    pulses = 0
    was_on = False
    max_q = 0.0
    reached = False
    n_steps = 0
    cap_s = 2.0e6
    cap_t = 800.0
    stalled = 0

    while t < cap_t and s < cap_s:
        h = max(0.0, y)
        rho = rho_of(h)
        q = 0.5 * rho * v * v
        max_q = max(max_q, q)
        drag_a = (0.5 * cd * rho * area * v * v) / mass if mass > 0 else 0.0
        g_along = G_STD * math.sin(phi)
        on = (t % period) < t_on
        if on and not was_on:
            pulses += 1
        if on and pulses == 0:
            pulses = 1
        was_on = on
        a_push = peak_a if on else 0.0
        a_along = a_push - g_along - drag_a
        v_new = v + a_along * dt
        if v_new < 0.0:
            v_new = 0.0
            stalled += 1
            if stalled > int(2.0 / dt) and t > 2.0:
                break
        else:
            stalled = 0
        v = v_new
        ds = v * dt
        s += ds
        x += ds * math.cos(phi)
        y += ds * math.sin(phi)
        if geometry == "concave_bowl":
            phi = min(s / R, theta_exit)
        elif geometry == "convex_sphere":
            phi = max(theta_exit - s / R, 0.0)
        t += dt
        n_steps += 1
        if v >= v_target:
            reached = True
            break

    return {
        "reached_target": reached,
        "v_end_m_s": v,
        "v_end_mph": mph(v),
        "v_target_m_s": v_target,
        "length_m": s,
        "length_km": s / 1000.0,
        "length_mi": m_to_mi(s),
        "time_s": t,
        "exit_angle_deg": math.degrees(phi),
        "exit_x_m": x,
        "exit_alt_m": y,
        "pulses": pulses,
        "peak_q_pa": max_q,
        "peak_push_m_s2": peak_a,
        "geometry_requested": geometry,
        "n_steps": n_steps,
    }


def fly(v0, angle_deg, h0, mass, cd, area, dt=0.01, t_max=1200.0) -> dict:
    """Point-mass flight, spherical Earth, inverse-square gravity, exponential
    atmosphere, no lift, no thrust. Origin at Earth center; start on the +y axis."""
    ang = math.radians(angle_deg)
    r0 = R_EARTH + max(0.0, h0)
    x = 0.0
    y = r0
    vx = v0 * math.cos(ang)
    vy = v0 * math.sin(ang)
    t = 0.0
    h_max = max(0.0, h0)
    v_at_apogee = v0
    t_apogee = 0.0
    peak_q = 0.5 * rho_of(h0) * v0 * v0
    peak_heating_proxy = (rho_of(h0) ** 0.5) * (v0 ** 3)
    impacted = False
    while t < t_max:
        r = math.hypot(x, y)
        if r < 1.0:
            break
        h = r - R_EARTH
        if h < 0.0:
            impacted = True
            break
        rho = rho_of(h)
        speed = math.hypot(vx, vy)
        q = 0.5 * rho * speed * speed
        peak_q = max(peak_q, q)
        peak_heating_proxy = max(peak_heating_proxy, (rho ** 0.5) * (speed ** 3))
        g = MU_EARTH / (r * r)
        ax = -g * x / r
        ay = -g * y / r
        if speed > 0 and mass > 0:
            drag = 0.5 * cd * rho * area * speed * speed
            ax -= (drag / mass) * (vx / speed)
            ay -= (drag / mass) * (vy / speed)
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt
        t += dt
        h_new = math.hypot(x, y) - R_EARTH
        if h_new > h_max:
            h_max = h_new
            v_at_apogee = math.hypot(vx, vy)
            t_apogee = t
        if t_apogee > 0 and t > t_apogee + 200.0:
            break
    return {
        "apogee_m": h_max,
        "apogee_km": h_max / 1000.0,
        "reached_karman": h_max >= KARMAN_M,
        "reached_200km": h_max >= LEO_ALT_M,
        "v_at_apogee_m_s": v_at_apogee,
        "v_at_apogee_mph": mph(v_at_apogee),
        "t_apogee_s": t_apogee,
        "peak_q_pa": peak_q,
        "peak_heating_proxy_si": peak_heating_proxy,
        "impacted_during_window": impacted,
        "v0_m_s": v0,
        "v0_fraction_of_7p8kms": v0 / 7800.0,
        "speed_gap_to_7p8kms_at_release_m_s": max(0.0, 7800.0 - v0),
        "speed_gap_to_vcirc200_at_release_m_s": max(0.0, V_CIRC_200KM - v0),
        "speed_gap_to_vcirc200_at_apogee_m_s": max(0.0, V_CIRC_200KM - v_at_apogee),
        "t_end_s": t,
    }

def damper_study(peak_a: float) -> dict:
    fn_iso = ASSUMPTIONS["isolator_fn_hz"]
    zeta_iso = ASSUMPTIONS["isolator_zeta"]
    zeta_visc = ASSUMPTIONS["viscous_zeta"]
    mu = ASSUMPTIONS["tmd_mass_ratio"]
    trans = []
    for f in [0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0]:
        r = f / fn_iso
        trans.append({"f_hz": f, "r": r, "T": transmissibility(r, zeta_iso)})
    zeta_eff = zeta_visc + 0.5 * math.sqrt(mu)
    T_10 = transmissibility(10.0 / fn_iso, zeta_iso)
    return {
        "assumptions": {
            "isolator_fn_hz": fn_iso, "isolator_zeta": zeta_iso,
            "viscous_zeta": zeta_visc, "tmd_mass_ratio": mu,
            "tmd_effective_zeta": zeta_eff, "ringdown_cycles": 8,
            "isolation_eval_freq_hz": 10.0,
        },
        "transmissibility_curve": trans,
        "peak_input_m_s2": peak_a,
        "undamped_residual_after_8_cycles_m_s2": peak_a,
        "viscous_residual_after_8_cycles_m_s2": ringdown_peak(peak_a, zeta_visc, 8),
        "viscous_plus_tmd_residual_after_8_cycles_m_s2": ringdown_peak(peak_a, zeta_eff, 8),
        "isolated_transmitted_peak_at_10hz_m_s2": peak_a * T_10,
        "isolation_transmissibility_at_10hz": T_10,
        "claim_limit": (
            "These figures meter peak residual and transmitted spike under the stated "
            "oscillator assumptions. They do not reduce the integrated impulse required "
            "to reach a given exit speed."
        ),
    }


def goldilocks_sweep() -> dict:
    vehicles = [
        {"name": "slender_5kg", "mass": 5.0, "cd": ASSUMPTIONS["cd_slender"], "area": ASSUMPTIONS["area_slender_m2"]},
        {"name": "slender_20kg", "mass": 20.0, "cd": ASSUMPTIONS["cd_slender"], "area": ASSUMPTIONS["area_slender_m2"]},
        {"name": "blunt_20kg", "mass": 20.0, "cd": ASSUMPTIONS["cd_blunt"], "area": ASSUMPTIONS["area_blunt_m2"]},
        {"name": "blunt_50kg", "mass": 50.0, "cd": ASSUMPTIONS["cd_blunt"], "area": ASSUMPTIONS["area_blunt_m2"]},
    ]
    flights = []
    for veh in vehicles:
        for sp in ASSUMPTIONS["comparison_mph"]:
            v = sp * MPH
            for ang in ASSUMPTIONS["straight_angles_deg"]:
                fl = fly(v, ang, 0.0, veh["mass"], veh["cd"], veh["area"])
                flights.append({
                    "vehicle": veh["name"], "mass_kg": veh["mass"], "cd": veh["cd"],
                    "area_m2": veh["area"], "speed_mph": sp,
                    "in_goldilocks_example_band": 1000.0 <= sp <= 3000.0,
                    "angle_deg": ang, **fl,
                })
    geo_rows = []
    peak_a = 3.0 * G_STD
    for sp in [1000.0, 2000.0, 3000.0, 17000.0]:
        v = sp * MPH
        for ang in [45.0, 80.0]:
            for geo in ("straight", "concave_bowl", "convex_sphere"):
                for veh in (vehicles[1], vehicles[2]):
                    tr = integrate_track(v, geo, ang, veh["mass"], veh["cd"], veh["area"],
                                         peak_a, ASSUMPTIONS["bowl_radius_m"])
                    h0 = max(0.0, tr["exit_alt_m"])
                    fl = fly(tr["v_end_m_s"], tr["exit_angle_deg"], h0, veh["mass"], veh["cd"], veh["area"])
                    geo_rows.append({
                        "vehicle": veh["name"], "speed_target_mph": sp,
                        "design_angle_deg": ang, "geometry": geo,
                        "track": tr,
                        "flight": {
                            "apogee_km": fl["apogee_km"],
                            "reached_karman": fl["reached_karman"],
                            "v_at_apogee_m_s": fl["v_at_apogee_m_s"],
                            "peak_q_pa": fl["peak_q_pa"],
                            "speed_gap_to_vcirc200_at_apogee_m_s": fl["speed_gap_to_vcirc200_at_apogee_m_s"],
                        },
                    })
    sea_level_drag = []
    for veh in vehicles:
        for sp in ASSUMPTIONS["comparison_mph"]:
            vv = sp * MPH
            a_d = (0.5 * veh["cd"] * RHO0 * veh["area"] * vv * vv) / veh["mass"]
            sea_level_drag.append({
                "vehicle": veh["name"], "speed_mph": sp, "speed_m_s": vv,
                "drag_accel_m_s2": a_d, "drag_accel_g": a_d / G_STD,
            })
    return {
        "constants_computed": {
            "v_circ_200km_m_s": V_CIRC_200KM,
            "v_circ_200km_km_s": V_CIRC_200KM / 1000.0,
            "v_circ_200km_mph": mph(V_CIRC_200KM),
            "v_esc_surface_m_s": V_ESC_SURFACE,
            "v_esc_surface_km_s": V_ESC_SURFACE / 1000.0,
            "v_17000_mph_m_s": V_17000_MPH,
            "v_17000_mph_vs_vcirc200_ratio": V_17000_MPH / V_CIRC_200KM,
            "note": (
                "The conversation used ~17,000 mph as the layman's orbital-speed figure. "
                "Circular speed at 200 km computed from mu and R_E is about 17,450 mph "
                "(7.78 km/s). 17,000 mph is 7.60 km/s, a rounded lower figure."
            ),
        },
        "kinematic_track_table": track_table(),
        "sea_level_drag": sea_level_drag,
        "flights_from_sea_level_release": flights,
        "geometry_integrated_track_and_flight": geo_rows,
    }


def summarize_sweep(sweep: dict) -> dict:
    flights = sweep["flights_from_sea_level_release"]

    def best(pred):
        cand = [f for f in flights if pred(f)]
        return max(cand, key=lambda f: f["apogee_km"]) if cand else None

    highlights = {
        "best_apogee_in_1000_3000_mph": best(lambda f: f["in_goldilocks_example_band"]),
        "best_apogee_at_17000_mph": best(lambda f: f["speed_mph"] == 17000.0),
        "best_apogee_slender_20_at_3000_mph": best(lambda f: f["vehicle"] == "slender_20kg" and f["speed_mph"] == 3000.0),
        "best_apogee_blunt_20_at_3000_mph": best(lambda f: f["vehicle"] == "blunt_20kg" and f["speed_mph"] == 3000.0),
        "best_apogee_slender_20_at_1000_mph": best(lambda f: f["vehicle"] == "slender_20kg" and f["speed_mph"] == 1000.0),
        "any_in_band_reached_karman": any(f["reached_karman"] and f["in_goldilocks_example_band"] for f in flights),
        "any_in_band_reached_200km": any(f["reached_200km"] and f["in_goldilocks_example_band"] for f in flights),
        "any_at_17000_reached_karman": any(f["reached_karman"] and f["speed_mph"] == 17000.0 for f in flights),
        "any_flight_reached_vcirc": any(f["v0_m_s"] >= V_CIRC_200KM for f in flights),
        "speed_fraction": {
            "1000_mph_over_vcirc200": V_1000_MPH / V_CIRC_200KM,
            "2000_mph_over_vcirc200": V_2000_MPH / V_CIRC_200KM,
            "3000_mph_over_vcirc200": V_3000_MPH / V_CIRC_200KM,
            "17000_mph_over_vcirc200": V_17000_MPH / V_CIRC_200KM,
            "residual_gap_at_3000_mph_m_s": V_CIRC_200KM - V_3000_MPH,
            "residual_gap_at_1000_mph_m_s": V_CIRC_200KM - V_1000_MPH,
            "residual_gap_at_17000_mph_m_s": V_CIRC_200KM - V_17000_MPH,
        },
        "kinematic_3g_selected": [
            r for r in sweep["kinematic_track_table"]
            if r["peak_accel_g"] == 3.0 and r["speed_mph"] in (1000.0, 3000.0, 17000.0)
        ],
        "sea_level_drag_selected": [
            d for d in sweep["sea_level_drag"]
            if d["vehicle"] in ("slender_20kg", "blunt_20kg") and d["speed_mph"] in (1000.0, 3000.0, 17000.0)
        ],
        "geometry_slender20_3000mph_80deg": [
            g for g in sweep["geometry_integrated_track_and_flight"]
            if g["vehicle"] == "slender_20kg" and g["speed_target_mph"] == 3000.0 and g["design_angle_deg"] == 80.0
        ],
        "geometry_slender20_17000mph_80deg": [
            g for g in sweep["geometry_integrated_track_and_flight"]
            if g["vehicle"] == "slender_20kg" and g["speed_target_mph"] == 17000.0 and g["design_angle_deg"] == 80.0
        ],
    }
    return highlights

def run_relational(highlights: dict, damper: dict) -> dict:
    genesis = OroboroGenesis()
    transcriber = OroboroTranscriber()
    dictator = OroboroDictator(transcriber)
    levy = OroboroLevy(transcriber)
    nexus = OroboroNexus()
    sim = OroboroRelationalSim(nexus)

    nexus.register("genesis", {"kind": "origin", "status": "seeded", "weight": math.inf, "tag": genesis.rootTag})
    levy.assess({"text": genesis.rootTag, "source": "genesis"}, weight=0)

    dictator.start()
    ingested = dictator.processAudioText(PRIMARY_TEXT)
    levy.assess({"text": "dictator_ingest_of_written_engineering_arc", "source": "dictator"},
                weight=LEVY_WEIGHTS["dictator_ingest"])
    dictator.stop()

    geo = highlights.get("geometry_slender20_3000mph_80deg") or []
    straight = next((g for g in geo if g["geometry"] == "straight"), None)
    n_pulses = int(straight["track"]["pulses"]) if straight else 20
    n_pulses = max(1, min(n_pulses, 200))

    outcomes_undamped = []
    outcomes_damped = []
    T = damper["isolation_transmissibility_at_10hz"]
    peak_a = 3.0 * G_STD
    g_term = (G_STD * math.sin(math.radians(80.0))) / peak_a
    for i in range(n_pulses):
        sid = f"pulse-{i}"
        nexus.register(sid, {"kind": "pulse", "status": "independent", "weight": LEVY_WEIGHTS["pulse"]})
        levy.assess({"text": f"magnetic pulse {i}", "source": "track"}, weight=LEVY_WEIGHTS["pulse"])
        local = 1.0 - g_term
        outcomes_undamped.append(sim.processIndependent(sid, local_delta=local))
        outcomes_damped.append(sim.processIndependent(sid, local_delta=local * T))
        nexus.metrics["isolations"] += 1
        levy.assess({"text": f"isolation engage {i}", "source": "isolator"}, weight=LEVY_WEIGHTS["isolation_engage"])
        cid = f"coast-{i}"
        nexus.register(cid, {"kind": "coast", "status": "independent", "weight": LEVY_WEIGHTS["coast"]})
        levy.assess({"text": f"coast gap {i}", "source": "track"}, weight=LEVY_WEIGHTS["coast"])
        outcomes_undamped.append(sim.processIndependent(cid, local_delta=-g_term))
        outcomes_damped.append(sim.processIndependent(cid, local_delta=-g_term))

    rec_undamped = sim.recombine(outcomes_undamped, damping=0.0)
    rec_viscous = sim.recombine(outcomes_damped, damping=ASSUMPTIONS["viscous_zeta"])
    levy.assess({"text": "damper reconcile", "source": "reconcile"}, weight=LEVY_WEIGHTS["damper_reconcile"])
    levy.assess({"text": "release from rail", "source": "track"}, weight=LEVY_WEIGHTS["release"])
    levy.assess({"text": "goldilocks 1000-3000 mph band evaluated", "source": "sweep"},
                weight=LEVY_WEIGHTS["goldilocks_in_band"])
    levy.assess({"text": "no case reached 200 km circular speed on the rail", "source": "sweep"},
                weight=LEVY_WEIGHTS["failed_reach_leo_speed"])

    return {
        "genesis": {"rootTag": genesis.rootTag, "foundationalWeight": "Infinity"},
        "dictator": {
            "exists": True,
            "definition": (
                "OroboroDictator in oroboro-core.js is a real-time stream-to-text path "
                "that feeds finalized text into OroboroTranscriber. This run passed the "
                "written engineering-arc text through processAudioText. No audio and no "
                "speech recognition were used."
            ),
            "ingested_chars": len(ingested["text"]) if ingested else 0,
            "ingested_critical": bool(ingested["critical"]) if ingested else None,
        },
        "levy": {"totalWeight": levy.totalWeight, "n_entries": len(levy.entries), "weight_table": LEVY_WEIGHTS},
        "nexus_metrics": nexus.metrics,
        "n_pulse_segments": n_pulses,
        "recombine_undamped": rec_undamped,
        "recombine_isolated_and_viscous": rec_viscous,
        "transcriber_n_chronicles": len(transcriber.chronicles),
        "transcriber_critical_count": len(transcriber.anonymousLog),
    }


def make_figures(sweep: dict) -> List[str]:
    paths = []
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    colors = {1.0: "#1f3a5f", 3.0: "#b85c38", 5.0: "#2a6f4e", 10.0: "#6b3fa0"}
    for gmult, col in colors.items():
        rows = [r for r in sweep["kinematic_track_table"] if r["peak_accel_g"] == gmult]
        ax.plot([r["speed_mph"] for r in rows], [r["continuous_length_mi"] for r in rows],
                marker="o", color=col, label=f"{gmult:.0f} g continuous")
    ax.axvspan(1000, 3000, color="#f3e5ab", alpha=0.45, label="1,000-3,000 mph example band")
    ax.axvline(17000, color="#444", ls="--", lw=1, label="17,000 mph (conversation figure)")
    ax.set_xlabel("Exit speed (mph)")
    ax.set_ylabel("Kinematic track length (miles)")
    ax.set_title("Track length vs speed (v^2/2a, no drag, no gravity)")
    ax.legend(fontsize=8)
    ax.set_xlim(0, 18000)
    fig.tight_layout()
    p = OUT / "fig01_track_length.png"
    fig.savefig(p, dpi=140)
    plt.close()
    paths.append(str(p))

    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    flights = [f for f in sweep["flights_from_sea_level_release"] if f["vehicle"] == "slender_20kg"]
    for ang, col in [(45, "#1f3a5f"), (80, "#b85c38"), (90, "#2a6f4e")]:
        rows = sorted([f for f in flights if f["angle_deg"] == ang], key=lambda r: r["speed_mph"])
        ax.plot([r["speed_mph"] for r in rows], [r["apogee_km"] for r in rows],
                marker="o", color=col, label=f"{ang:.0f} deg slender 20 kg")
    blunt = sorted([f for f in sweep["flights_from_sea_level_release"]
                    if f["vehicle"] == "blunt_20kg" and f["angle_deg"] == 80],
                   key=lambda r: r["speed_mph"])
    ax.plot([r["speed_mph"] for r in blunt], [r["apogee_km"] for r in blunt],
            marker="s", ls="--", color="#6b3fa0", label="80 deg blunt 20 kg")
    ax.axhline(100, color="#444", ls=":", lw=1, label="100 km (Karman line, convention)")
    ax.axvspan(1000, 3000, color="#f3e5ab", alpha=0.45, label="1,000-3,000 mph example band")
    ax.set_xlabel("Sea-level release speed (mph)")
    ax.set_ylabel("Apogee (km)")
    ax.set_title("Ballistic apogee with drag and inverse-square gravity")
    ax.legend(fontsize=8)
    ax.set_xlim(0, 18000)
    fig.tight_layout()
    p = OUT / "fig02_apogee.png"
    fig.savefig(p, dpi=140)
    plt.close()
    paths.append(str(p))

    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    for name, col in [("slender_20kg", "#1f3a5f"), ("blunt_20kg", "#b85c38")]:
        rows = sorted([d for d in sweep["sea_level_drag"] if d["vehicle"] == name],
                      key=lambda r: r["speed_mph"])
        ax.plot([r["speed_mph"] for r in rows], [r["drag_accel_g"] for r in rows],
                marker="o", color=col, label=name.replace("_", " "))
    ax.axvspan(1000, 3000, color="#f3e5ab", alpha=0.45, label="1,000-3,000 mph example band")
    ax.axvline(17000, color="#444", ls="--", lw=1, label="17,000 mph")
    ax.set_xlabel("Speed (mph)")
    ax.set_ylabel("Sea-level drag acceleration (g)")
    ax.set_title("Drag acceleration at sea level (h = 0)")
    ax.legend(fontsize=8)
    ax.set_xlim(0, 18000)
    fig.tight_layout()
    p = OUT / "fig03_sea_level_drag.png"
    fig.savefig(p, dpi=140)
    plt.close()
    paths.append(str(p))
    return paths


def json_default(o):
    if isinstance(o, float) and (math.isnan(o) or math.isinf(o)):
        return str(o)
    return str(o)

def main():
    oasis = run_oasis()
    companion = run_companion()
    meshes = run_meshes()
    sweep = goldilocks_sweep()
    highlights = summarize_sweep(sweep)
    damper = damper_study(3.0 * G_STD)
    relational = run_relational(highlights, damper)
    figures = make_figures(sweep)

    def pick_flight(vehicle, speed, angle):
        for f in sweep["flights_from_sea_level_release"]:
            if f["vehicle"] == vehicle and f["speed_mph"] == speed and f["angle_deg"] == angle:
                return {
                    "vehicle": vehicle, "speed_mph": speed, "angle_deg": angle,
                    "apogee_km": f["apogee_km"], "reached_karman": f["reached_karman"],
                    "v_at_apogee_m_s": f["v_at_apogee_m_s"], "peak_q_pa": f["peak_q_pa"],
                    "v0_fraction_of_7p8kms": f["v0_fraction_of_7p8kms"],
                    "speed_gap_to_vcirc200_at_release_m_s": f["speed_gap_to_vcirc200_at_release_m_s"],
                    "speed_gap_to_vcirc200_at_apogee_m_s": f["speed_gap_to_vcirc200_at_apogee_m_s"],
                }
        return None

    selected_flights = []
    for veh in ("slender_20kg", "blunt_20kg", "slender_5kg"):
        for sp in (60.0, 1000.0, 2000.0, 3000.0, 17000.0):
            for ang in (45.0, 80.0, 90.0):
                row = pick_flight(veh, sp, ang)
                if row:
                    selected_flights.append(row)

    payload = {
        "constants": {"well_known": {
            "g_m_s2": G_STD, "mu_earth_m3_s2": MU_EARTH, "r_earth_m": R_EARTH,
            "rho0_kg_m3": RHO0, "karman_m": KARMAN_M, "mph_to_m_s": MPH,
        }, "assumptions": ASSUMPTIONS, "levy_weights": LEVY_WEIGHTS},
        "oasis": oasis,
        "companion": companion,
        "meshes": meshes,
        "highlights": highlights,
        "damper": damper,
        "relational": relational,
        "selected_flights": selected_flights,
        "figures": figures,
        "constants_computed": sweep["constants_computed"],
        "kinematic_track_table": sweep["kinematic_track_table"],
        "sea_level_drag": sweep["sea_level_drag"],
        "context_123_not_scored_as_legal_advice": CONTEXT_123,
    }
    (OUT / "system_run.json").write_text(json.dumps(payload, indent=2, default=json_default), encoding="utf-8")
    (OUT / "flights_full.json").write_text(
        json.dumps(sweep["flights_from_sea_level_release"], indent=2, default=json_default), encoding="utf-8")
    (OUT / "geometry_runs.json").write_text(
        json.dumps(sweep["geometry_integrated_track_and_flight"], indent=2, default=json_default), encoding="utf-8")

    lines = []
    add = lines.append
    add("MAGNETIC-ASSIST / INVERSE-EPCOT / LAS / DAMPER CASE STUDY — RAW SYSTEM OUTPUT")
    add("Input source: Caitlyn Randels conversation thread (engineering arc scored and simulated).")
    add("")
    cc = sweep["constants_computed"]
    add("Computed constants:")
    add(f"  v_circ(200 km) = {cc['v_circ_200km_m_s']:.3f} m/s = {cc['v_circ_200km_km_s']:.4f} km/s = {cc['v_circ_200km_mph']:.1f} mph")
    add(f"  v_esc(surface) = {cc['v_esc_surface_m_s']:.3f} m/s = {cc['v_esc_surface_km_s']:.4f} km/s")
    add(f"  17,000 mph     = {cc['v_17000_mph_m_s']:.3f} m/s ({cc['v_17000_mph_vs_vcirc200_ratio']:.4f} of v_circ_200km)")
    add(f"  1,000 / 2,000 / 3,000 mph = {V_1000_MPH:.3f} / {V_2000_MPH:.3f} / {V_3000_MPH:.3f} m/s")
    add("")
    iso = oasis["isolated_fresh_world"]["engineering_arc"]["result"]
    add("Oasis isolated fresh world, engineering arc:")
    add(f"  status={iso['status']} score={iso['score']} features={iso['features']}")
    add(f"  breakdown={iso['score_breakdown']} principle={iso.get('principle_name')} reason={iso.get('reason')}")
    add(f"  rationale={iso.get('rationale')}")
    nop = oasis["gate_constraint_no_position"]["result"]
    add("Oasis same text, no position:")
    add(f"  status={nop['status']} blocked_principle={nop['blocked_principle']} reason={nop['reason']}")
    add("Oasis sequential chunks:")
    for item in oasis["sequential_chunks_then_full"]["results"]:
        r = item["result"]
        add(f"  {item['key']}: status={r['status']} score={r['score']} features={r['features']}")
    rf = oasis["sequential_chunks_then_full"]["full_arc_after_chunks"]
    add(f"  full_arc_after_chunks: status={rf['status']} score={rf['score']} features={rf['features']}")
    add(f"  committed={oasis['sequential_chunks_then_full']['committed_ids']}")
    add(f"  buffered={oasis['sequential_chunks_then_full']['buffered_ids']}")
    add("")
    add("Ms. Minutes empty chronicle:")
    add("  kind=" + str(companion["empty_chronicle"]["engineering_arc"].get("kind")))
    add("  reply=" + str(companion["empty_chronicle"]["engineering_arc"].get("reply")))
    add("Ms. Minutes seeded ask:")
    add("  kind=" + str(companion["seeded_chronicle"]["ask"].get("kind")))
    add("  reply=" + str(companion["seeded_chronicle"]["ask"].get("reply")))
    add("")
    add("NaCl as written: invert=False -> " + meshes["nacl_as_written"]["invert_false_return"])
    add("NaCl as written: invert=True  -> " + meshes["nacl_as_written"]["invert_true_return"])
    g = meshes["geodesic_icosahedron"]
    add(f"Geodesic icosahedron: {g['n_vertices']} vertices, {g['n_edges']} edges, "
        f"locked {g['locked_before_invert']} before invert / {g['locked_after_invert']} after; "
        f"bowl hemisphere vertices z<=0: {g['n_bowl_hemisphere_vertices_z_le_0']}; "
        f"invert preserves lock count: {g['invert_preserves_lock_count']}")
    lasm = meshes["las_sector_mesh"]
    add(f"LAS sector mesh: locked {lasm['locked_before_invert']} -> {lasm['locked_after_invert']} after invert; "
        f"locked edges {lasm['locked_edges_before']}; open {lasm['open_edges_before']}; "
        f"invert preserves lock count: {lasm['invert_preserves_lock_count']}")
    add("")
    add("Speed fractions of v_circ(200 km):")
    for k, v in highlights["speed_fraction"].items():
        add(f"  {k}: {v}")
    add(f"Any in-band flight reached Karman? {highlights['any_in_band_reached_karman']}")
    add(f"Any in-band flight reached 200 km? {highlights['any_in_band_reached_200km']}")
    add(f"Any 17,000 mph flight reached Karman? {highlights['any_at_17000_reached_karman']}")
    add("")
    add("Selected sea-level drag:")
    for d in highlights["sea_level_drag_selected"]:
        add(f"  {d}")
    add("Selected 3 g kinematic lengths:")
    for d in highlights["kinematic_3g_selected"]:
        add(f"  {d['speed_mph']} mph: continuous {d['continuous_length_km']:.3f} km ({d['continuous_length_mi']:.2f} mi); "
            f"intermittent {d['intermittent_length_km']:.3f} km ({d['intermittent_length_mi']:.2f} mi)")
    add("")
    add("Best apogees:")
    for key in ("best_apogee_in_1000_3000_mph", "best_apogee_slender_20_at_3000_mph",
                "best_apogee_blunt_20_at_3000_mph", "best_apogee_slender_20_at_1000_mph",
                "best_apogee_at_17000_mph"):
        f = highlights[key]
        if f:
            add(f"  {key}: {f['vehicle']} {f['speed_mph']} mph {f['angle_deg']} deg -> apogee {f['apogee_km']:.3f} km, "
                f"Karman={f['reached_karman']}, v_apogee={f['v_at_apogee_m_s']:.2f} m/s, peak_q={f['peak_q_pa']:.1f} Pa")
    add("")
    add("Geometry comparison (slender 20 kg, 3,000 mph target, 80 deg, 3 g peak, intermittent):")
    for grow in highlights["geometry_slender20_3000mph_80deg"]:
        tr, fl = grow["track"], grow["flight"]
        add(f"  {grow['geometry']}: reached={tr['reached_target']} v_end={tr['v_end_mph']:.1f} mph, "
            f"L={tr['length_km']:.3f} km ({tr['length_mi']:.2f} mi), t={tr['time_s']:.2f} s, "
            f"exit_angle={tr['exit_angle_deg']:.2f} deg, exit_alt={tr['exit_alt_m']:.1f} m, pulses={tr['pulses']}, "
            f"apogee={fl['apogee_km']:.3f} km, Karman={fl['reached_karman']}")
    add("Geometry comparison (slender 20 kg, 17,000 mph target, 80 deg, 3 g peak, intermittent):")
    for grow in highlights["geometry_slender20_17000mph_80deg"]:
        tr, fl = grow["track"], grow["flight"]
        add(f"  {grow['geometry']}: reached={tr['reached_target']} v_end={tr['v_end_mph']:.1f} mph, "
            f"L={tr['length_km']:.3f} km ({tr['length_mi']:.2f} mi), t={tr['time_s']:.2f} s, "
            f"exit_angle={tr['exit_angle_deg']:.2f} deg, exit_alt={tr['exit_alt_m']:.1f} m, pulses={tr['pulses']}, "
            f"apogee={fl['apogee_km']:.3f} km, Karman={fl['reached_karman']}")
    add("")
    add("Damper / isolation:")
    add(f"  T(10 Hz)={damper['isolation_transmissibility_at_10hz']:.6f}")
    add(f"  isolated transmitted peak={damper['isolated_transmitted_peak_at_10hz_m_s2']:.4f} m/s^2")
    add(f"  viscous residual after 8 cycles={damper['viscous_residual_after_8_cycles_m_s2']:.4f} m/s^2")
    add(f"  viscous+TMD residual after 8 cycles={damper['viscous_plus_tmd_residual_after_8_cycles_m_s2']:.4f} m/s^2")
    add(f"  undamped residual={damper['undamped_residual_after_8_cycles_m_s2']:.4f} m/s^2")
    add("")
    add("Relational recombine:")
    add(f"  undamped: {relational['recombine_undamped']}")
    add(f"  isolated+viscous: {relational['recombine_isolated_and_viscous']}")
    add(f"  levy total={relational['levy']['totalWeight']} entries={relational['levy']['n_entries']}")
    add(f"  nexus metrics={relational['nexus_metrics']}")
    add("")
    add("Selected flights (compact):")
    for row in selected_flights:
        add(f"  {row['vehicle']} {row['speed_mph']:.0f} mph {row['angle_deg']:.0f} deg: "
            f"apogee={row['apogee_km']:.3f} km Karman={row['reached_karman']} "
            f"v_apogee={row['v_at_apogee_m_s']:.2f} m/s peak_q={row['peak_q_pa']:.1f} Pa "
            f"gap_release={row['speed_gap_to_vcirc200_at_release_m_s']:.1f} m/s")
    add("")
    add("Figures: " + ", ".join(figures))
    text = "\n".join(lines) + "\n"
    (OUT / "system_run.txt").write_text(text, encoding="utf-8")
    print(text)
    print("Wrote", OUT / "system_run.json")


if __name__ == "__main__":
    main()
