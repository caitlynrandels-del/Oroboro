#!/usr/bin/env python3
"""
Native Oroboro polarity mesh for the metastasis restart.

Built from nacl_polarity_mesh.py (IonicOrigin / Edge / Mesh / Nexus / Levy /
flip+re-stabilize) plus dream-catcher niches, a circulation loop, and
return edges. Speculative modeling only; no biological or clinical claims.

A dream-catcher around each target organ is a wheel: an even hoop (lockable
even cycle) plus a hub and spokes. Each hoop-spoke-hoop face is a 3-cycle,
so a consistent 2-coloring is impossible and some spokes stay frustrated.
That is the same odd-loop result as the launch-chat dream-catcher weave.

Inverse-Epcot bowl: hoop sits on a concave shell. bowl_depth is the chance
a landing cell falls into the web (spokes/hub) rather than the hoop.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math

# ----- Genesis ionic origin (nacl_polarity_mesh.IonicOrigin) -----
@dataclass
class IonicOrigin:
    Na: int = +1
    Cl: int = -1
    weight: float = math.inf
    root_tag: str = "I am the OG avatar"


@dataclass
class Edge:
    node_a: str
    node_b: str
    charge_a: int = +1
    charge_b: int = -1
    locked: bool = False
    state: str = "open"
    weight: float = 0.0
    organ: Optional[int] = None
    kind: str = "generic"       # circ, shed, hoop, spoke, organ_hub, return, approach, lure, magnet, flush
    repaired: bool = False      # adaptive-niche: treated as lockable even if odd-loop

    @property
    def opposite_charge(self) -> bool:
        return (self.charge_a * self.charge_b) < 0


class PolarityMesh:
    """Relational mesh whose consensus (locks vs frustrated odd-loop edges) is native state."""

    def __init__(self, nodes: List[str], edges: List[Edge], origin: Optional[IonicOrigin] = None):
        self.origin = origin or IonicOrigin()
        self.nodes = list(nodes)
        self.edges = list(edges)
        self.charge: Dict[str, int] = {}
        self.adj: Dict[str, List[int]] = {n: [] for n in self.nodes}
        for i, e in enumerate(self.edges):
            self.adj.setdefault(e.node_a, []).append(i)
            self.adj.setdefault(e.node_b, []).append(i)

    def assign_charges_from(self, root: str, root_charge: int = +1) -> None:
        """BFS 2-coloring from Genesis. Conflicts on already-colored same-charge neighbors
        are left as-is; process_polarities will mark those edges frustrated."""
        self.charge = {root: root_charge}
        q = [root]
        seen = {root}
        while q:
            u = q.pop(0)
            cu = self.charge[u]
            for ei in self.adj.get(u, []):
                e = self.edges[ei]
                v = e.node_b if e.node_a == u else e.node_a
                if v not in self.charge:
                    self.charge[v] = -cu
                    if v not in seen:
                        seen.add(v); q.append(v)
        for n in self.nodes:
            if n not in self.charge:
                self.charge[n] = root_charge

    def process_polarities(self) -> None:
        for e in self.edges:
            e.charge_a = self.charge.get(e.node_a, +1)
            e.charge_b = self.charge.get(e.node_b, -1)
            if e.repaired or e.opposite_charge:
                e.locked = True
                e.state = "membrane_lock"
            else:
                e.locked = False
                e.state = "frustrated" if not e.opposite_charge else "open"

    def apply_levy(self, periodic_grounded: bool = True) -> None:
        w = 0.999 if periodic_grounded else 0.25
        for e in self.edges:
            e.weight = w

    def consensus(self) -> List[Edge]:
        return [e for e in self.edges if e.locked]

    def frustrated_edges(self) -> List[Edge]:
        return [e for e in self.edges if (not e.locked) and (not e.repaired)]

    def flip_all(self) -> None:
        for n in list(self.charge):
            self.charge[n] *= -1

    def re_stabilize(self) -> None:
        self.process_polarities()

    def inversion_holds(self) -> bool:
        """nacl_polarity_mesh test: flip all charges, re-stabilize, locked set unchanged."""
        before = {(e.node_a, e.node_b, e.locked) for e in self.edges}
        self.flip_all()
        self.re_stabilize()
        after = {(e.node_a, e.node_b, e.locked) for e in self.edges}
        self.flip_all()
        self.re_stabilize()
        return before == after

    def counts(self, organ: Optional[int] = None) -> Dict[str, int]:
        es = [e for e in self.edges if (organ is None or e.organ == organ)]
        return dict(
            n_edges=len(es),
            n_locked=sum(1 for e in es if e.locked),
            n_frustrated=sum(1 for e in es if not e.locked),
            n_repaired=sum(1 for e in es if e.repaired),
        )


def _odd_cycles_count(n_nodes: int, edge_index: List[Tuple[int, int]], cap: int = 2000) -> int:
    """Count simple cycles of odd length up to a cap (for the inventory / note)."""
    from collections import defaultdict
    g = defaultdict(list)
    for a, b in edge_index:
        g[a].append(b); g[b].append(a)
    found = 0
    def dfs(start, u, path, seen):
        nonlocal found
        if found >= cap:
            return
        for v in g[u]:
            if v == start and len(path) >= 3:
                if len(path) % 2 == 1:
                    found += 1
                continue
            if v in seen or v < start:
                continue
            seen.add(v)
            path.append(v)
            dfs(start, v, path, seen)
            path.pop()
            seen.remove(v)
    nodes = range(n_nodes)
    # This is exponential; only used on the small niche itself, not the sweep.
    return found


def build_system_mesh(organs: List[str], hoop_n: int = 8, circulation_nodes: int = 8,
                      include_loops: bool = True, extraction: bool = False,
                      extraction_coloring: str = "preserve") -> Tuple[PolarityMesh, Dict]:
    """
    Full native mesh:
      Genesis origin -- circulation ring -- approach edges into each organ's
      dream-catcher (hoop + hub + spokes) -- return edges back to circulation.
    If include_loops is False, the niche is a tree (organ-hub-hoop spokes only,
    no hoop ring, no return edges): a control ablation with no odd faces.
    If extraction is True, a filter node and an extract (collection) node are
    added, with lure edges from each circulation node to the filter, flush
    edges from each organ hub and hoop entry to the filter, and a magnet edge
    from the filter to extract.

    extraction_coloring:
      "preserve" (default) — 2-color the Genesis / circulation / niche mesh first,
        then attach the extract branch and color only the new nodes from an
        already-colored neighbor. Existing ring and niche charges do not change.
      "joint" — put the extract star in the same BFS as the ring. A hub attached
        to every circulation node is a shortcut and can recode the ring.
    """
    origin = IonicOrigin()
    nodes = ["genesis"]
    edges: List[Edge] = []
    meta = dict(organs=list(organs), hoop_n=hoop_n, include_loops=include_loops,
                extraction=bool(extraction),
                extraction_coloring=str(extraction_coloring or "preserve"),
                circ_nodes=[], organ_nodes=[], hub_nodes=[], hoop_nodes=[],
                spoke_idx=[[] for _ in organs], hoop_idx=[[] for _ in organs],
                return_idx=[[] for _ in organs], approach_idx=[[] for _ in organs],
                niche_edge_idx=[[] for _ in organs],
                lure_idx=[], magnet_idx=[], flush_idx=[],
                filter_node=None, extract_node=None)

    # Circulation ring (vascular loop). Kept even in the niche-ablation, because it
    # models recirculation of the vessel compartment, not the organ web.
    circ = [f"circ{i}" for i in range(circulation_nodes)]
    nodes += circ
    meta["circ_nodes"] = circ
    for i in range(circulation_nodes):
        edges.append(Edge("genesis" if i == 0 else circ[i], circ[(i + 1) % circulation_nodes]
                          if i == 0 else circ[(i + 1) % circulation_nodes],
                          kind="circ"))
    # Fix genesis-circ0 and the ring cleanly
    edges = [e for e in edges if e.kind != "circ"]
    edges.append(Edge("genesis", circ[0], kind="shed", organ=None))
    if include_loops or True:
        for i in range(circulation_nodes):
            edges.append(Edge(circ[i], circ[(i + 1) % circulation_nodes], kind="circ"))

    for o, name in enumerate(organs):
        organ_n = f"organ:{name}"
        hub = f"hub:{name}"
        hoops = [f"hoop:{name}:{i}" for i in range(hoop_n)]
        nodes += [organ_n, hub] + hoops
        meta["organ_nodes"].append(organ_n)
        meta["hub_nodes"].append(hub)
        meta["hoop_nodes"].append(hoops)

        # organ -- hub
        e = Edge(organ_n, hub, kind="organ_hub", organ=o)
        edges.append(e); meta["niche_edge_idx"][o].append(len(edges) - 1)

        for i, h in enumerate(hoops):
            # spokes (hub -- hoop). In a wheel these sit in triangles when the hoop exists.
            e = Edge(hub, h, kind="spoke", organ=o)
            edges.append(e)
            meta["spoke_idx"][o].append(len(edges) - 1)
            meta["niche_edge_idx"][o].append(len(edges) - 1)

        if include_loops:
            for i in range(hoop_n):
                e = Edge(hoops[i], hoops[(i + 1) % hoop_n], kind="hoop", organ=o)
                edges.append(e)
                meta["hoop_idx"][o].append(len(edges) - 1)
                meta["niche_edge_idx"][o].append(len(edges) - 1)
            # Return edges close the recirculation / reawakening loops
            e = Edge(hub, circ[o % circulation_nodes], kind="return", organ=o)
            edges.append(e); meta["return_idx"][o].append(len(edges) - 1)
            e = Edge(hoops[0], circ[(o + 1) % circulation_nodes], kind="return", organ=o)
            edges.append(e); meta["return_idx"][o].append(len(edges) - 1)

        # Approach from a circulation node into the hoop (entry)
        e = Edge(circ[o % circulation_nodes], hoops[0] if hoops else organ_n, kind="approach", organ=o)
        edges.append(e)
        meta["approach_idx"][o].append(len(edges) - 1)

    # Extraction / collection branch (optional). Filter sits on the way to extract.
    # Edges use the same NaCl lock rule as the rest of the mesh.
    extract_edges: List[Edge] = []
    if extraction:
        meta["filter_node"] = "filter"
        meta["extract_node"] = "extract"
        extract_edges.append(Edge("filter", "extract", kind="magnet"))
        for cnode in circ:
            extract_edges.append(Edge(cnode, "filter", kind="lure"))
        for o, name in enumerate(organs):
            extract_edges.append(Edge(meta["hub_nodes"][o], "filter", kind="flush", organ=o))
            hoops_o = meta["hoop_nodes"][o]
            if hoops_o:
                extract_edges.append(Edge(hoops_o[0], "filter", kind="flush", organ=o))

    coloring = str(extraction_coloring or "preserve")
    if extraction and coloring == "joint":
        nodes += ["filter", "extract"]
        for e in extract_edges:
            edges.append(e)
            if e.kind == "magnet":
                meta["magnet_idx"].append(len(edges) - 1)
            elif e.kind == "lure":
                meta["lure_idx"].append(len(edges) - 1)
            elif e.kind == "flush":
                meta["flush_idx"].append(len(edges) - 1)
        mesh = PolarityMesh(nodes, edges, origin)
        mesh.assign_charges_from("genesis", origin.Na)
        mesh.process_polarities()
        mesh.apply_levy()
    else:
        mesh = PolarityMesh(nodes, edges, origin)
        mesh.assign_charges_from("genesis", origin.Na)
        if extraction:
            for n in ("filter", "extract"):
                mesh.nodes.append(n)
                mesh.adj[n] = []
            for e in extract_edges:
                mesh.edges.append(e)
                ei = len(mesh.edges) - 1
                mesh.adj.setdefault(e.node_a, []).append(ei)
                mesh.adj.setdefault(e.node_b, []).append(ei)
                if e.kind == "magnet":
                    meta["magnet_idx"].append(ei)
                elif e.kind == "lure":
                    meta["lure_idx"].append(ei)
                elif e.kind == "flush":
                    meta["flush_idx"].append(ei)
            # Color only the new nodes from an already-colored neighbor (no re-BFS).
            pending = ["filter", "extract"]
            guard = 0
            while pending and guard < 8:
                guard += 1
                nxt = []
                for n in pending:
                    colored = False
                    for ei in mesh.adj.get(n, []):
                        e = mesh.edges[ei]
                        other = e.node_b if e.node_a == n else e.node_a
                        if other in mesh.charge:
                            mesh.charge[n] = -mesh.charge[other]
                            colored = True
                            break
                    if not colored:
                        nxt.append(n)
                pending = nxt
            for n in pending:
                mesh.charge[n] = origin.Na
        mesh.process_polarities()
        mesh.apply_levy()
    meta["n_nodes"] = len(mesh.nodes)
    meta["n_edges"] = len(mesh.edges)
    meta["n_frustrated0"] = sum(1 for e in mesh.edges if not e.locked)
    meta["n_locked0"] = sum(1 for e in mesh.edges if e.locked)
    meta["inversion_holds"] = None  # computed once outside the hot path
    return mesh, meta

def mesh_inversion_holds(organs, **kwargs) -> bool:
    mesh, _ = build_system_mesh(organs, **kwargs)
    return mesh.inversion_holds()


def landing_pools(meta: Dict, mesh: PolarityMesh, organ: int, bowl_depth: float):
    """Split niche edges of an organ into web (spokes) vs hoop; bowl_depth weights the web."""
    spoke = [i for i in meta["spoke_idx"][organ]]
    hoop = [i for i in meta["hoop_idx"][organ]]
    # If loops are ablated there is no hoop ring; landing is on spokes only, all lockable.
    return spoke, hoop, float(bowl_depth if hoop else 0.0)
