from dataclasses import dataclass
from typing import List
import math

# Genesis
@dataclass
class IonicOrigin:
    Na: int = +1
    Cl: int = -1
    weight: float = math.inf

# Mesh edge
@dataclass
class Edge:
    node_a: str
    node_b: str
    charge_a: int
    charge_b: int
    locked: bool = False
    state: str = "open"
    weight: float = 0.0

    @property
    def opposite_charge(self) -> bool:
        return (self.charge_a * self.charge_b) < 0

class Mesh:
    def __init__(self, nodes: List[str], edges: List[Edge]):
        self.nodes = nodes
        self.edges = edges

    def process_polarities(self):
        for e in self.edges:
            if e.opposite_charge:
                e.locked = True
                e.state = "membrane_lock"
            else:
                e.state = "open"

    def apply_levy(self, periodic_grounded: bool = True):
        w = 0.999 if periodic_grounded else 0.25  # altered critical detail
        for e in self.edges:
            e.weight = w

    def consensus(self) -> List[Edge]:
        return [e for e in self.edges if e.locked]

    def flip_all(self):
        for e in self.edges:
            e.charge_a *= -1
            e.charge_b *= -1

    def re_stabilize(self):
        self.process_polarities()

class Nexus:
    @staticmethod
    def log(edges: List[Edge]) -> str:
        return f"[Nexus] {len(edges)} locked edges"

class Transcriber:
    @staticmethod
    def write(msg: str) -> str:
        return f"[Transcriber] {msg}"

def run(invert: bool = False) -> str:
    origin = IonicOrigin()
    nodes = ["Na0", "Cl0", "Na1", "Na2"]
    edges = [
        Edge("Na0", "Cl0", origin.Na, origin.Cl),
        Edge("Na0", "Na1", origin.Na, origin.Na),
        Edge("Cl0", "Na2", origin.Cl, origin.Na),
    ]
    mesh = Mesh(nodes, edges)
    mesh.process_polarities()
    mesh.apply_levy()
    cons = mesh.consensus()
    if invert:
        mesh.flip_all()
        mesh.re_stabilize()
        cons = mesh.consensus()
    return Transcriber.write(Nexus.log(cons))

if __name__ == "__main__":
    print(run(invert=True))
