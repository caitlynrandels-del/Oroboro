#!/usr/bin/env python3
# NON-CONJUNCTIVE (audit 2026-11-27): NaCl polarity + Laplacian only; no Oasis, Nexus loop, Dictator, Transcriber, Levy feedback or homeostasis.
# Kept for history; results are pre-integration. The conjunctive baseline (all Oroboro
# components on one loop) is research/metastasis-native (integrated=True) and
# research/cross-domain/scripts/run_conjunctive_check.py; an integrated launch rebuild is pending.
# Speculative modeling only. No engineering, flight or operational claims.
"""Small deterministic computations for the ondulatory-string / wireframe addendum.

Uses the existing placeholder Avalanche skeletal graph and the already-recorded
magnetic-launch pulse/rail numbers. No invented motor specs. No new physics constants
beyond textbook standing-wave geometry and the graph Laplacian.
"""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict, deque
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

NACL_DIR = Path(__file__).resolve().parents[3] / "consciousness-mapping"  # this repo (was /workspace/github-staging/Oroboro/consciousness-mapping)
sys.path.insert(0, str(NACL_DIR))
import nacl_polarity_mesh as nacl  # noqa: E402

JOINTS_PATH = Path("/workspace/oroboro-skeletal/example_joints.json")
RUN_REPORT_PATH = Path("/workspace/oroboro-skeletal/run_report.json")
LAUNCH_PATH = Path("/workspace/oroboro-research/magnetic_launch_case_study/outputs/system_run.json")
GEOM_PATH = Path("/workspace/oroboro-research/magnetic_launch_case_study/outputs/geometry_runs.json")

MPH = 0.44704
T_PULSE = 0.40 + 0.40  # from the launch run assumptions (s)


def degrees_from(bones):
    deg = defaultdict(int)
    nodes = set()
    for a, b in bones:
        deg[a] += 1
        deg[b] += 1
        nodes.add(a)
        nodes.add(b)
    return dict(deg), sorted(nodes)


def charge_hub_leaf(name, deg):
    """Interpretation A: ninja-star hubs vs leaf tips vs chain.
    degree >= 3 -> +1 (radial hub); degree == 1 -> -1 (leaf);
    degree == 2 -> +1 (chain / filament joint).
    """
    d = deg[name]
    if d >= 3:
        return 1
    if d == 1:
        return -1
    return 1


def charge_alternate(name, parent_map, origin="hip"):
    """Interpretation B: ondulatory filament. Alternate charge along the
    unique tree path from a Genesis origin (hip). Origin +1, each step flips.
    """
    # walk to origin
    n = 0
    cur = name
    seen = set()
    while cur != origin:
        if cur in seen or cur not in parent_map:
            break
        seen.add(cur)
        cur = parent_map[cur]
        n += 1
    return 1 if (n % 2 == 0) else -1


def tree_parents(bones, origin="hip"):
    adj = defaultdict(list)
    for a, b in bones:
        adj[a].append(b)
        adj[b].append(a)
    parent = {origin: None}
    q = deque([origin])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in parent:
                parent[v] = u
                q.append(v)
    return parent, adj


def run_mesh(bones, charge_fn, invert=False):
    edges = []
    for a, b in bones:
        edges.append(nacl.Edge(a, b, charge_fn(a), charge_fn(b)))
    nodes = sorted({n for e in bones for n in e})
    mesh = nacl.Mesh(nodes, edges)
    mesh.process_polarities()
    mesh.apply_levy()
    if invert:
        mesh.flip_all()
        mesh.re_stabilize()
    cons = mesh.consensus()
    return {
        "n_nodes": len(nodes),
        "n_edges": len(edges),
        "n_locked": len(cons),
        "n_open": len(edges) - len(cons),
        "locked": [f"{e.node_a}-{e.node_b}" for e in mesh.edges if e.locked],
        "open": [f"{e.node_a}-{e.node_b}" for e in mesh.edges if not e.locked],
        "levy_weight": 0.999,
    }


def laplacian_spectrum(nodes, bones):
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    A = np.zeros((n, n), dtype=float)
    for a, b in bones:
        i, j = idx[a], idx[b]
        A[i, j] = 1.0
        A[j, i] = 1.0
    deg = A.sum(axis=1)
    L = np.diag(deg) - A
    w, v = np.linalg.eigh(L)
    w = np.real(w)
    # Sort already by eigh
    n_zero = int(np.sum(np.abs(w) < 1e-10))
    return {
        "n_nodes": n,
        "n_edges": len(bones),
        "is_tree": len(bones) == n - 1 and n_zero == 1,
        "n_zero_eigenvalues": n_zero,
        "eigenvalues": [float(x) for x in w],
        "n_positive_modes": n - n_zero,
    }


def nearest_harmonic(L, Lambda, kind="string"):
    """Closest textbook harmonic whose wavelength is Lambda on length L.
    string / open-open tube: Lambda_n = 2L/n, n = 1,2,3,...
    closed-open tube: Lambda_n = 4L/(2n-1), n = 1,2,3,...
    """
    if Lambda <= 0 or L <= 0:
        return None
    if kind == "string":
        n_real = 2.0 * L / Lambda
        n_hat = max(1, int(round(n_real)))
        Lambda_n = 2.0 * L / n_hat
    else:
        # 4L/(2n-1) = Lambda => 2n-1 = 4L/Lambda => n = (4L/Lambda + 1)/2
        n_real = (4.0 * L / Lambda + 1.0) / 2.0
        n_hat = max(1, int(round(n_real)))
        Lambda_n = 4.0 * L / (2 * n_hat - 1)
    return {
        "kind": kind,
        "n_real": n_real,
        "nearest_n": n_hat,
        "detuning_from_integer": n_real - n_hat,
        "Lambda_mode_m": Lambda_n,
        "Lambda_target_m": Lambda,
        "relative_wavelength_mismatch": (Lambda - Lambda_n) / Lambda_n if Lambda_n else None,
    }


def rail_row(speed_mph, geometry, tr):
    L = float(tr["length_m"])
    t = float(tr["time_s"])
    pulses = int(tr["pulses"])
    v_end = float(tr["v_end_m_s"])
    Lambda_exit = v_end * T_PULSE
    Lambda_mean = (L / t) * T_PULSE if t > 0 else None
    n_laid = pulses  # one spatial period per pulse cycle, by construction along the path
    n_exit_periods = L / Lambda_exit if Lambda_exit else None
    return {
        "speed_target_mph": speed_mph,
        "geometry": geometry,
        "reached_target": tr["reached_target"],
        "length_m": L,
        "length_km": L / 1000.0,
        "time_s": t,
        "pulses": pulses,
        "v_end_m_s": v_end,
        "pulse_period_s": T_PULSE,
        "Lambda_exit_m": Lambda_exit,
        "Lambda_mean_m": Lambda_mean,
        "n_spatial_periods_laid": n_laid,
        "t_over_T": t / T_PULSE if T_PULSE else None,
        "n_exit_speed_periods_that_fit": n_exit_periods,
        "chirp_ratio_Lambda_exit_over_mean": (Lambda_exit / Lambda_mean) if Lambda_mean else None,
        "string_mode_at_exit_spacing": nearest_harmonic(L, Lambda_exit, "string"),
        "closed_open_tube_mode_at_exit_spacing": nearest_harmonic(L, Lambda_exit, "closed-open"),
        "string_mode_at_mean_spacing": nearest_harmonic(L, Lambda_mean, "string") if Lambda_mean else None,
    }


def main():
    joints = json.loads(JOINTS_PATH.read_text())
    report = json.loads(RUN_REPORT_PATH.read_text())
    launch = json.loads(LAUNCH_PATH.read_text())
    geom = json.loads(GEOM_PATH.read_text())

    bones = [tuple(b) for b in joints["bones"]]
    deg, nodes = degrees_from(bones)
    parent, adj = tree_parents(bones, origin="hip")
    hubs = sorted(n for n, d in deg.items() if d >= 3)
    leaves = sorted(n for n, d in deg.items() if d == 1)
    chain = sorted(n for n, d in deg.items() if d == 2)

    mesh_a = {
        "rule": "hub-leaf (interpretation A): deg>=3 +1, deg==1 -1, deg==2 +1",
        "invert_false": run_mesh(bones, lambda n: charge_hub_leaf(n, deg), invert=False),
        "invert_true": run_mesh(bones, lambda n: charge_hub_leaf(n, deg), invert=True),
    }
    mesh_b = {
        "rule": "ondulatory filament (interpretation B): alternate charge along the tree from hip (Genesis origin +1)",
        "origin": "hip",
        "invert_false": run_mesh(bones, lambda n: charge_alternate(n, parent, "hip"), invert=False),
        "invert_true": run_mesh(bones, lambda n: charge_alternate(n, parent, "hip"), invert=True),
    }
    # Both placeholder skeletons share the same topology; lock counts do not change.
    spec = laplacian_spectrum(nodes, bones)

    rails = []
    for row in geom:
        if row["vehicle"] != "slender_20kg" or row["design_angle_deg"] != 80:
            continue
        if row["speed_target_mph"] not in (1000.0, 2000.0, 3000.0):
            continue
        rails.append(rail_row(row["speed_target_mph"], row["geometry"], row["track"]))

    # Highlight the accelerating (reached) rails vs the convex cases that did not.
    chirp_claim = {
        "note": (
            "On a rail that starts from rest, the spatial period of a fixed pulse "
            "cycle, Lambda = v(t) * T, grows as speed grows. The number of periods "
            "actually laid equals the pulse count (approximately t/T). A uniform "
            "standing-wave mode uses one wavelength. Exit-speed spacing is longer "
            "than mean spacing, so fewer uniform exit-speed periods fit in L than "
            "pulses that were laid. That mismatch is the chirp."
        )
    }

    out = {
        "input_quotes": {
            "ondulatory_stack": (
                "Shrink wrap porcelain ninja stars socks 3d printer filament "
                "straw/tube. Bubbles. This is an example of ondulatory strings "
                "that I know is incredibly pertinent, but I'm not really sure "
                "what to do with it right now."
            ),
            "wireframe": "We also have the wireframe model from the avalanche game analysis that helps.",
        },
        "wireframe_source": {
            "path": str(JOINTS_PATH),
            "honest_status": joints["_warning"],
            "n_bones": len(bones),
            "n_joints": len(nodes),
            "n_skeletons_in_example": len(joints["frames"][0]["skeletons"]),
            "n_frames": len(joints["frames"]),
            "degrees": deg,
            "hubs_deg_ge_3": hubs,
            "leaves_deg_1": leaves,
            "chain_deg_2": chain,
            "connected_tree": spec["is_tree"],
        },
        "existing_skeletal_run": {
            "path": str(RUN_REPORT_PATH),
            "levy_total": report["levy_total"],
            "frames": [
                {
                    "t": f["t"],
                    "matchedWholeSystem": f["matchedWholeSystem"],
                    "residual_vs_whole": f["residual_vs_whole"],
                    "total_bone_length": f["total_bone_length"],
                    "crossing_count": f["crossing_count"],
                    "n_isolated_chunks": len(f["isolated_chunks"]),
                }
                for f in report["frames"]
            ],
        },
        "laplacian": spec,
        "polarity_mesh": {"interpretation_A_hub_leaf": mesh_a, "interpretation_B_filament": mesh_b},
        "pulse_period_s_from_launch_run": T_PULSE,
        "rails_slender20_80deg": rails,
        "chirp": chirp_claim,
    }

    (OUT / "ondulatory_addendum.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    lines = []
    add = lines.append
    add("ONDULATORY-STRING / WIREFRAME ADDENDUM — RAW OUTPUT")
    add("Wireframe: placeholder joints in example_joints.json (NOT extracted from game video).")
    add(f"  {len(nodes)} joints, {len(bones)} bones, tree={spec['is_tree']}, hubs={hubs}, leaves={leaves}")
    add(f"  Laplacian: n_zero={spec['n_zero_eigenvalues']}, n_positive_modes={spec['n_positive_modes']}")
    add("  eigenvalues: " + ", ".join(f"{x:.6f}" for x in spec["eigenvalues"]))
    add("")
    add("Existing skeletal run (run_report.json):")
    for f in out["existing_skeletal_run"]["frames"]:
        add(f"  t={f['t']}: matched={f['matchedWholeSystem']} residual={f['residual_vs_whole']:.3e} "
            f"bone_length={f['total_bone_length']:.6f} crossing={f['crossing_count']} isolated_chunks={f['n_isolated_chunks']}")
    add("")
    for label, block in (("A hub-leaf", mesh_a), ("B filament", mesh_b)):
        a, b = block["invert_false"], block["invert_true"]
        add(f"Polarity {label}: {block['rule']}")
        add(f"  invert=False locked {a['n_locked']}/{a['n_edges']} {a['locked']}; open {a['open']}")
        add(f"  invert=True  locked {b['n_locked']}/{b['n_edges']} (count preserved={a['n_locked']==b['n_locked']})")
    add("")
    add(f"Pulse period T={T_PULSE:.2f} s (0.40 on + 0.40 coast from the launch run).")
    for r in rails:
        sm = r["string_mode_at_exit_spacing"]
        tm = r["closed_open_tube_mode_at_exit_spacing"]
        ms = r["string_mode_at_mean_spacing"]
        add(f"  {r['speed_target_mph']:.0f} mph {r['geometry']}: reached={r['reached_target']} "
            f"L={r['length_km']:.3f} km t={r['time_s']:.2f}s pulses={r['pulses']} "
            f"Lambda_exit={r['Lambda_exit_m']:.3f} m Lambda_mean={r['Lambda_mean_m']:.3f} m "
            f"n_laid={r['n_spatial_periods_laid']} n_exit_fit={r['n_exit_speed_periods_that_fit']:.3f} "
            f"chirp={r['chirp_ratio_Lambda_exit_over_mean']:.4f} "
            f"string n_real={sm['n_real']:.3f} nearest={sm['nearest_n']} detune={sm['detuning_from_integer']:.4f} "
            f"tube n_real={tm['n_real']:.3f} nearest={tm['nearest_n']} detune={tm['detuning_from_integer']:.4f} "
            f"string-mean n_real={ms['n_real']:.3f} nearest={ms['nearest_n']} detune={ms['detuning_from_integer']:.4f}")
    text = "\n".join(lines) + "\n"
    (OUT / "ondulatory_addendum.txt").write_text(text, encoding="utf-8")
    print(text)
    print("Wrote", OUT / "ondulatory_addendum.json")


if __name__ == "__main__":
    main()
