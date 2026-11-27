#!/usr/bin/env python3
# NON-CONJUNCTIVE (audit 2026-11-27): NaCl polarity + accounting-only recombine; not the full loop. Reads pose landmarks that are NOT published (personal-use clip).
# Kept for history; results are pre-integration. The conjunctive baseline (all Oroboro
# components on one loop) is research/metastasis-native (integrated=True) and
# research/cross-domain/scripts/run_conjunctive_check.py; an integrated launch rebuild is pending.
# Speculative modeling only. No engineering, flight or operational claims.
"""Tree-only vs dream-catcher-woven mesh on a MediaPipe-detected highlight pose.

Real joints come from one personal-use frame of the Avalanche vs Devils
highlight (clip t=515.999 s). The broadcast still is not written into the
published figure. No player pose is invented.
"""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict, deque
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
WORK = ROOT / "work"
DET = WORK / "pose_detections.json"

NACL_DIR = Path(__file__).resolve().parents[3] / "consciousness-mapping"  # this repo (was /workspace/github-staging/Oroboro/consciousness-mapping)
sys.path.insert(0, str(NACL_DIR))
import nacl_polarity_mesh as nacl  # noqa: E402

# Dream-catcher assumptions (labeled, not measured)
N_HOOP = 12
N_ROUNDS = 4          # inward web rounds after the hoop; innermost is the hole
HOLE_FRAC = 0.20      # innermost radius / hoop radius
HOOP_SCALE = 1.15     # hoop radius vs max torso-joint distance from mid-hip
TIE_JOINTS = ("neck", "l_shoulder", "r_shoulder", "l_hip", "r_hip")

# Body joints used from BlazePose / MediaPipe Pose (published names)
BODY = [
    "nose", "l_shoulder", "r_shoulder", "l_elbow", "r_elbow",
    "l_wrist", "r_wrist", "l_hip", "r_hip", "l_knee", "r_knee",
    "l_ankle", "r_ankle",
]
KEEP_VIS = 0.30  # include in the graph; report which are below 0.5


def load_primary_pose():
    data = json.loads(DET.read_text())
    # Choose the detection with the most body joints at visibility >= 0.5,
    # then highest mean body visibility. Record the rest as a survey.
    survey = []
    best = None
    best_key = None
    for fr in data["frames"]:
        for i, p in enumerate(fr.get("poses") or []):
            row = {
                "file": fr["file"], "t_s": fr["t_s"], "pose_index": i,
                "n_body_vis_ge_0.5": p["n_body_vis_ge_0.5"],
                "n_body_vis_ge_0.3": p["n_body_vis_ge_0.3"],
                "mean_visibility_body": p["mean_visibility_body"],
                "width": fr["width"], "height": fr["height"],
            }
            survey.append(row)
            key = (p["n_body_vis_ge_0.5"], p["mean_visibility_body"])
            if best_key is None or key > best_key:
                best_key = key
                best = {**row, "landmarks": p["landmarks"], "bbox_norm": p["bbox_norm"]}
    return data["method"], survey, best


def skeleton_from_pose(pose):
    w, h = pose["width"], pose["height"]
    lms = {lm["name"]: lm for lm in pose["landmarks"]}
    used = {}
    vis = {}
    for name in BODY:
        lm = lms[name]
        vis[name] = lm["visibility"]
        if lm["visibility"] >= KEEP_VIS:
            # image pixels, y downward; for analysis we keep this and flip only in the figure
            used[name] = np.array([lm["x"] * w, lm["y"] * h], dtype=float)
    # Derived midpoints — labeled as such, not detected landmarks
    derived = {}
    if "l_hip" in used and "r_hip" in used:
        derived["mid_hip"] = 0.5 * (used["l_hip"] + used["r_hip"])
        used["mid_hip"] = derived["mid_hip"]
    if "l_shoulder" in used and "r_shoulder" in used:
        derived["neck"] = 0.5 * (used["l_shoulder"] + used["r_shoulder"])
        used["neck"] = derived["neck"]

    # Kinematic tree (acyclic). Skip an edge if either end is missing.
    candidates = [
        ("mid_hip", "l_hip"), ("mid_hip", "r_hip"),
        ("l_hip", "l_knee"), ("l_knee", "l_ankle"),
        ("r_hip", "r_knee"), ("r_knee", "r_ankle"),
        ("mid_hip", "neck"),
        ("neck", "l_shoulder"), ("neck", "r_shoulder"),
        ("l_shoulder", "l_elbow"), ("l_elbow", "l_wrist"),
        ("r_shoulder", "r_elbow"), ("r_elbow", "r_wrist"),
        ("neck", "nose"),
    ]
    edges = [(a, b) for a, b in candidates if a in used and b in used]
    return used, edges, derived, vis


def dreamcatcher_and_ties(coords):
    center = coords["mid_hip"]
    torso = [coords[n] for n in ("neck", "l_shoulder", "r_shoulder", "l_hip", "r_hip") if n in coords]
    r_torso = max(float(np.linalg.norm(p - center)) for p in torso)
    R = HOOP_SCALE * r_torso
    rounds = []
    hoop = []
    for i in range(N_HOOP):
        th = 2 * math.pi * i / N_HOOP - math.pi / 2
        hoop.append(center + R * np.array([math.cos(th), math.sin(th)]))
    rounds.append(hoop)
    names = [[f"hoop-{i}" for i in range(N_HOOP)]]
    for k in range(1, N_ROUNDS + 1):
        target_r = R * (1.0 - (k / N_ROUNDS) * (1.0 - HOLE_FRAC))
        prev = rounds[-1]
        nxt, nm = [], []
        for i in range(N_HOOP):
            mid = 0.5 * (prev[i] + prev[(i + 1) % N_HOOP])
            vec = mid - center
            nrm = float(np.linalg.norm(vec))
            pt = center + vec / nrm * target_r if nrm > 0 else center + np.array([target_r, 0.0])
            nxt.append(pt)
            nm.append(f"web-{k}-{i}")
        rounds.append(nxt)
        names.append(nm)

    weave_coords = dict(coords)
    for rpts, rnames in zip(rounds, names):
        for p, n in zip(rpts, rnames):
            weave_coords[n] = p

    weave_edges = []
    # hoop cycle and each inner cycle (the innermost cycle is the center hole)
    for rnames in names:
        for i in range(N_HOOP):
            weave_edges.append((rnames[i], rnames[(i + 1) % N_HOOP]))
    # each new vertex attaches to the two ends of the previous segment (midpoint weave)
    for k in range(1, N_ROUNDS + 1):
        prev_n, cur_n = names[k - 1], names[k]
        for i in range(N_HOOP):
            weave_edges.append((cur_n[i], prev_n[i]))
            weave_edges.append((cur_n[i], prev_n[(i + 1) % N_HOOP]))

    # Neck and shoulders tie to the nearest hoop vertex (torso envelope).
    # Hips sit near Genesis, so they tie to the nearest vertex of the innermost
    # hole ring rather than stretching across the web to the outer hoop.
    ties = []
    hoop_names = names[0]
    hole_names = names[-1]
    hoop_ties = ("neck", "l_shoulder", "r_shoulder")
    hole_ties = ("l_hip", "r_hip")
    for jn, pool in [(j, hoop_names) for j in hoop_ties] + [(j, hole_names) for j in hole_ties]:
        if jn not in coords:
            continue
        dists = [float(np.linalg.norm(coords[jn] - weave_coords[hn])) for hn in pool]
        hn = pool[int(np.argmin(dists))]
        ties.append((jn, hn))
        weave_edges.append((jn, hn))

    return {
        "coords": weave_coords,
        "weave_edges": weave_edges,
        "ties": ties,
        "R": R,
        "r_torso": r_torso,
        "center": center,
        "hole_radius": R * HOLE_FRAC,
        "n_hoop": N_HOOP,
        "n_rounds": N_ROUNDS,
        "hole_frac": HOLE_FRAC,
        "hoop_scale": HOOP_SCALE,
        "round_names": names,
    }


def graph_stats(nodes, edges):
    V = len(nodes)
    E = len(edges)
    # connected components via union-find / BFS
    adj = defaultdict(list)
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    seen = set()
    comps = 0
    for n in nodes:
        if n in seen:
            continue
        comps += 1
        q = deque([n])
        seen.add(n)
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    q.append(v)
    cycle_rank = E - V + comps
    return {"V": V, "E": E, "components": comps, "cycle_rank": cycle_rank}


def degrees(edges):
    d = defaultdict(int)
    for a, b in edges:
        d[a] += 1
        d[b] += 1
    return d


def bfs_parent_and_level(edges, origin):
    adj = defaultdict(list)
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    parent = {origin: None}
    level = {origin: 0}
    q = deque([origin])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in parent:
                parent[v] = u
                level[v] = level[u] + 1
                q.append(v)
    return parent, level, adj


def is_bipartite(edges, nodes, origin):
    _, _, adj = bfs_parent_and_level(edges, origin)
    color = {origin: 0}
    q = deque([origin])
    conflicts = []
    seen = {origin}
    # also start BFS from any uncolored node (should be connected)
    rest = [n for n in nodes if n != origin]
    starts = [origin] + rest
    for s in starts:
        if s not in color:
            color[s] = 0
            q.append(s)
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v not in color:
                    color[v] = 1 - color[u]
                    q.append(v)
                elif color[v] == color[u]:
                    e = tuple(sorted((u, v)))
                    if e not in conflicts:
                        conflicts.append(e)
    return len(conflicts) == 0, conflicts, color


def charge_hub_leaf(name, deg):
    d = deg.get(name, 0)
    if d >= 3:
        return 1
    if d == 1:
        return -1
    return 1


def charge_alternate(name, level, origin="mid_hip"):
    return 1 if (level.get(name, 0) % 2 == 0) else -1


def run_mesh(nodes, edges, charge_fn, invert=False):
    nacl_edges = [nacl.Edge(a, b, charge_fn(a), charge_fn(b)) for a, b in edges]
    mesh = nacl.Mesh(list(nodes), nacl_edges)
    mesh.process_polarities()
    mesh.apply_levy()
    if invert:
        mesh.flip_all()
        mesh.re_stabilize()
    cons = mesh.consensus()
    locked = [f"{e.node_a}-{e.node_b}" for e in mesh.edges if e.locked]
    open_e = [f"{e.node_a}-{e.node_b}" for e in mesh.edges if not e.locked]
    return {
        "n_nodes": len(nodes),
        "n_edges": len(edges),
        "n_locked": len(cons),
        "n_open": len(edges) - len(cons),
        "locked": locked,
        "open": open_e,
        "levy_all_0.999": 0.999 * len(edges),
        "levy_locked_0.999_open_0.25": 0.999 * len(cons) + 0.25 * (len(edges) - len(cons)),
    }


def laplacian_spectrum(nodes, edges):
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    A = np.zeros((n, n), dtype=float)
    for a, b in edges:
        i, j = idx[a], idx[b]
        A[i, j] = 1.0
        A[j, i] = 1.0
    deg = A.sum(axis=1)
    L = np.diag(deg) - A
    w = np.real(np.linalg.eigh(L)[0])
    w = np.sort(w)
    # multiplicity clusters
    clusters = []
    for val in w:
        if not clusters or abs(val - clusters[-1][0]) > 1e-8:
            clusters.append([float(val), 1])
        else:
            clusters[-1][1] += 1
    n_zero = int(np.sum(np.abs(w) < 1e-8))
    fiedler = float(w[1]) if n > 1 else 0.0
    return {
        "n_zero_eigenvalues": n_zero,
        "algebraic_connectivity_fiedler": fiedler,
        "eigenvalues": [float(x) for x in w],
        "multiplicity_clusters": [{"value": v, "multiplicity": m} for v, m in clusters],
        "lambda_max": float(w[-1]),
    }


def edge_length_total(coords, edges):
    return float(sum(np.linalg.norm(coords[a] - coords[b]) for a, b in edges))


def reconcile_by_parts(coords, parts):
    """parts: dict name -> edge list. Residual of summed part lengths vs union."""
    lengths = {k: edge_length_total(coords, ev) for k, ev in parts.items()}
    combined = sum(lengths.values())
    union = []
    seen = set()
    for ev in parts.values():
        for e in ev:
            key = tuple(sorted(e))
            if key not in seen:
                seen.add(key)
                union.append(e)
    whole = edge_length_total(coords, union)
    return {
        "part_lengths": lengths,
        "sum_of_parts": combined,
        "whole": whole,
        "residual": abs(combined - whole),
        "matchedWholeSystem": abs(combined - whole) < 1e-8,
    }


def pulse_diffusion(nodes, edges, origin, steps=(1, 2, 4, 8, 16, 32)):
    """Lazy random walk, mass conserved. Pulse starts at origin."""
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    A = np.zeros((n, n), dtype=float)
    for a, b in edges:
        A[idx[a], idx[b]] = 1.0
        A[idx[b], idx[a]] = 1.0
    deg = A.sum(axis=1)
    # P = 0.5 I + 0.5 D^{-1} A
    DinvA = np.zeros_like(A)
    for i in range(n):
        if deg[i] > 0:
            DinvA[i, :] = A[i, :] / deg[i]
    P = 0.5 * np.eye(n) + 0.5 * DinvA
    # graph distance from origin
    adj = defaultdict(list)
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    dist = {origin: 0}
    q = deque([origin])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)

    u = np.zeros(n)
    u[idx[origin]] = 1.0
    out = []
    k_set = set(steps)
    max_k = max(steps)
    for k in range(1, max_k + 1):
        u = P @ u
        if k in k_set:
            # participation: (sum u)^2 / sum u^2
            s2 = float(np.sum(u * u))
            pr = (1.0 / s2) if s2 > 0 else 0.0
            thresh = 1e-3
            active = [nodes[i] for i in range(n) if u[i] > thresh]
            radii = [dist.get(nm, 0) for nm in active]
            out.append({
                "k": k,
                "mass_at_origin": float(u[idx[origin]]),
                "participation_ratio": pr,
                "n_nodes_mass_gt_1e-3": len(active),
                "spread_radius_graph_steps": max(radii) if radii else 0,
                "max_mass": float(u.max()),
            })
    return out


def draw_figure(tree_coords, tree_edges, weave, vis, out_path):
    coords = weave["coords"]
    fig, ax = plt.subplots(figsize=(7.2, 6.2))
    ax.set_aspect("equal")
    # Inverse-Epcot shell hint: a slightly larger dashed circle, the bowl the hoop sits on
    c = weave["center"]
    shell_r = weave["R"] * 1.08
    shell = plt.Circle((c[0], -c[1]), shell_r, fill=False, ls="--", lw=1.0,
                       color="#8aa0b8", label="inverse-Epcot shell (interpretation)")
    ax.add_patch(shell)
    # hole
    hole = plt.Circle((c[0], -c[1]), weave["hole_radius"], fill=False, lw=1.2,
                      color="#b85c38", label="center hole at mid-hip (Genesis)")
    ax.add_patch(hole)

    def seg(a, b, **kw):
        pa, pb = coords[a], coords[b]
        ax.plot([pa[0], pb[0]], [-pa[1], -pb[1]], **kw)

    # web (not hoop cycle): attachments + inner cycles
    hoop_set = set(weave["round_names"][0])
    for a, b in weave["weave_edges"]:
        if a in hoop_set and b in hoop_set:
            continue
        if a in tree_coords and b in hoop_set or b in tree_coords and a in hoop_set:
            continue  # ties drawn later
        seg(a, b, color="#d4a017", lw=0.7, alpha=0.85, zorder=2)
    # hoop
    first = True
    for a, b in weave["weave_edges"]:
        if a in hoop_set and b in hoop_set:
            seg(a, b, color="#1f3a5f", lw=2.0, zorder=3,
                label="dream-catcher hoop" if first else None)
            first = False
    # ties
    first = True
    for a, b in weave["ties"]:
        seg(a, b, color="#2a6f4e", lw=1.1, ls=":", zorder=4,
            label="joint-to-hoop ties" if first else None)
        first = False
    # skeleton tree
    first = True
    for a, b in tree_edges:
        weak = (vis.get(a, 1) < 0.5) or (vis.get(b, 1) < 0.5)
        seg(a, b, color="#00c8d4", lw=2.2 if not weak else 1.3,
            ls="-" if not weak else "--", zorder=5,
            label="detected kinematic tree" if first else None)
        first = False
    # joints
    for n, p in tree_coords.items():
        ax.scatter([p[0]], [-p[1]], s=22 if n not in ("mid_hip", "neck") else 36,
                   color="#00c8d4", zorder=6, edgecolors="#103040", linewidths=0.4)
    ax.scatter([c[0]], [-c[1]], s=50, facecolors="none", edgecolors="#b85c38",
               linewidths=1.6, zorder=7)
    ax.annotate("Genesis\n(mid-hip)", (c[0], -c[1]), textcoords="offset points",
                xytext=(8, -16), fontsize=7, color="#b85c38")
    ax.set_title("Detected pose with a dream-catcher weave\n(clip 8:36, personal-use highlight; still not shown)")
    ax.legend(fontsize=7, loc="upper right", frameon=True)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    return str(out_path)


def main():
    method, survey, pose = load_primary_pose()
    tree_coords, tree_edges, derived, vis = skeleton_from_pose(pose)
    tree_nodes = list(tree_coords.keys())
    weave = dreamcatcher_and_ties(tree_coords)
    woven_edges = list(tree_edges) + list(weave["weave_edges"])
    # de-duplicate
    def dedupe(ev):
        out, seen = [], set()
        for a, b in ev:
            k = tuple(sorted((a, b)))
            if k not in seen:
                seen.add(k)
                out.append((a, b))
        return out
    tree_edges = dedupe(tree_edges)
    woven_edges = dedupe(woven_edges)
    woven_nodes = list(weave["coords"].keys())

    # partitions for reconcile
    hoop_edges, web_edges, tie_edges = [], [], []
    hoop_set = set(weave["round_names"][0])
    tie_set = {tuple(sorted(e)) for e in weave["ties"]}
    for a, b in weave["weave_edges"]:
        k = tuple(sorted((a, b)))
        if k in tie_set:
            tie_edges.append((a, b))
        elif a in hoop_set and b in hoop_set:
            hoop_edges.append((a, b))
        else:
            web_edges.append((a, b))

    rec = reconcile_by_parts(weave["coords"], {
        "tree": tree_edges,
        "hoop": hoop_edges,
        "web": web_edges,
        "ties": tie_edges,
    })

    origin = "mid_hip"
    out = {"pose_source": {}, "tree": {}, "woven": {}, "assumptions": {}}

    # polarity for both graphs
    for label, nodes, edges in (("tree", tree_nodes, tree_edges), ("woven", woven_nodes, woven_edges)):
        deg = degrees(edges)
        parent, level, adj = bfs_parent_and_level(edges, origin)
        bip, conflicts, _ = is_bipartite(edges, nodes, origin)
        mesh_a = {
            "rule": "Interpretation A (hub-leaf): deg>=3 +1, deg==1 -1, deg==2 +1",
            "invert_false": run_mesh(nodes, edges, lambda n: charge_hub_leaf(n, deg), invert=False),
            "invert_true": run_mesh(nodes, edges, lambda n: charge_hub_leaf(n, deg), invert=True),
        }
        mesh_b = {
            "rule": "Interpretation B (ondulatory filament): alternate charge by BFS level from mid_hip",
            "invert_false": run_mesh(nodes, edges, lambda n: charge_alternate(n, level), invert=False),
            "invert_true": run_mesh(nodes, edges, lambda n: charge_alternate(n, level), invert=True),
        }
        block = {
            "stats": graph_stats(nodes, edges),
            "bipartite": bip,
            "n_same_color_conflicts_in_bfs_2color": len(conflicts),
            "laplacian": laplacian_spectrum(nodes, edges),
            "polarity_A": mesh_a,
            "polarity_B": mesh_b,
            "pulse_diffusion_from_mid_hip": pulse_diffusion(nodes, edges, origin),
        }
        # invert stability
        for m in (mesh_a, mesh_b):
            m["invert_preserves_lock_count"] = (
                m["invert_false"]["n_locked"] == m["invert_true"]["n_locked"]
            )
        if label == "tree":
            out["tree"] = block
        else:
            out["woven"] = block

    fig_path = OUT / "fig05_dreamcatcher_weave.png"
    draw_figure(tree_coords, tree_edges, weave, vis, fig_path)

    out["pose_source"] = {
        "real_pose_used": True,
        "method": method,
        "video": "Avalanche vs Devils official highlights, 28 Oct 2026, personal use only; not redistributed, not in the published figure",
        "clip_t_s": pose["t_s"],
        "frame_file_work_only": pose["file"],
        "pose_index": pose["pose_index"],
        "n_body_vis_ge_0.5": pose["n_body_vis_ge_0.5"],
        "n_body_vis_ge_0.3": pose["n_body_vis_ge_0.3"],
        "mean_visibility_body": pose["mean_visibility_body"],
        "body_visibility": vis,
        "derived_points": {k: "midpoint of detected joints (not a detected landmark)" for k in derived},
        "joints_kept": list(tree_coords.keys()),
        "survey_of_six_frames": survey,
        "note": (
            "Wide ice shots at 5.0 s and 90.0 s returned 0 poses in this run. "
            "The primary graph uses the single most complete detection "
            "(most body joints at visibility >= 0.5)."
        ),
    }
    out["assumptions"] = {
        "dreamcatcher": {
            "n_hoop": N_HOOP, "n_inward_rounds": N_ROUNDS, "hole_frac": HOLE_FRAC,
            "hoop_scale": HOOP_SCALE, "tie_joints": list(TIE_JOINTS),
            "construction": (
                "Round 0 is a regular 12-gon hoop around the torso, centered at mid-hip. "
                "Each later round's vertices start at midpoints of the previous round's "
                "segments and are scaled in toward the center, leaving a hole of radius "
                "0.20 R. New vertices attach to both ends of the parent segment. "
                "Named torso joints are tied to the nearest hoop vertex."
            ),
        },
        "visibility_keep_threshold": KEEP_VIS,
        "inverse_epcot": "The hoop is interpreted as sitting on a pressure-balanced circular shell (the bowl rim) in the image plane; not a 3-D bowl computation.",
    }
    out["weave_geometry"] = {
        "R_px": weave["R"],
        "r_torso_px": weave["r_torso"],
        "hole_radius_px": weave["hole_radius"],
        "n_tie_edges": len(weave["ties"]),
        "ties": [f"{a}-{b}" for a, b in weave["ties"]],
        "n_hoop_edges": len(hoop_edges),
        "n_web_edges": len(web_edges),
    }
    out["reconcile_edge_lengths_px"] = rec
    out["figure"] = str(fig_path)

    (OUT / "dreamcatcher_weave.json").write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")

    def brief(label, b):
        s, L = b["stats"], b["laplacian"]
        a0, b0 = b["polarity_A"]["invert_false"], b["polarity_B"]["invert_false"]
        lines = [
            f"{label}: V={s['V']} E={s['E']} components={s['components']} cycle_rank={s['cycle_rank']}",
            f"  bipartite={b['bipartite']} 2color_conflicts={b['n_same_color_conflicts_in_bfs_2color']}",
            f"  Fiedler={L['algebraic_connectivity_fiedler']:.6f} lambda_max={L['lambda_max']:.6f} n_zero={L['n_zero_eigenvalues']}",
            f"  polarity A locked {a0['n_locked']}/{a0['n_edges']} open {a0['n_open']}; invert_stable={b['polarity_A']['invert_preserves_lock_count']}; levy_lockedmix={a0['levy_locked_0.999_open_0.25']:.3f}",
            f"  polarity B locked {b0['n_locked']}/{b0['n_edges']} open {b0['n_open']}; invert_stable={b['polarity_B']['invert_preserves_lock_count']}; levy_lockedmix={b0['levy_locked_0.999_open_0.25']:.3f}",
        ]
        for step in b["pulse_diffusion_from_mid_hip"]:
            lines.append(
                f"  pulse k={step['k']}: mass_origin={step['mass_at_origin']:.4f} "
                f"participation={step['participation_ratio']:.2f} "
                f"n_active={step['n_nodes_mass_gt_1e-3']} radius={step['spread_radius_graph_steps']}"
            )
        return "\n".join(lines)

    text = []
    add = text.append
    add("DREAM-CATCHER WEAVE — RAW OUTPUT")
    add(f"Real pose used: yes. Method: {method}")
    add(f"Primary: t={pose['t_s']}s file={pose['file']} body >=0.5: {pose['n_body_vis_ge_0.5']}/13 mean_vis={pose['mean_visibility_body']:.3f}")
    add("Visibility by joint: " + ", ".join(f"{k}={v:.3f}" for k, v in vis.items()))
    add("Derived points: " + ", ".join(derived.keys()))
    add("Frame survey:")
    for row in survey:
        add(f"  t={row['t_s']} poses>=0.5 body {row['n_body_vis_ge_0.5']} mean={row['mean_visibility_body']:.3f}")
    add("")
    add(brief("TREE", out["tree"]))
    add("")
    add(brief("WOVEN", out["woven"]))
    add("")
    add(f"Reconcile residual (edge lengths, px): {rec['residual']:.3e} matched={rec['matchedWholeSystem']}")
    add(f"  parts={ {k: round(v, 3) for k, v in rec['part_lengths'].items()} } whole={rec['whole']:.3f}")
    add(f"Ties: {out['weave_geometry']['ties']}")
    add(f"Hoop R={weave['R']:.2f}px hole={weave['hole_radius']:.2f}px")
    add(f"Figure: {fig_path}")
    report = "\n".join(text) + "\n"
    (OUT / "dreamcatcher_weave.txt").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
