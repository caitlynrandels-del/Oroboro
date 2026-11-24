#!/usr/bin/env python3
"""
Oroboro Metastasis Model – Extended Simulation
Addresses open questions via state reduction & relational simulation:
1. Dormancy entry/exit
2. Non-genetic factors (epigenetic, environmental, immune)
3. Colonization success vs microenvironment
"""

import random
import json
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Cell:
    id: str
    attached: bool = True
    energy: float = 0.5
    dormancy: float = 0.0
    epigenetic_state: float = 0.5
    immune_evasion: float = 0.3
    microenvironment_fit: float = 0.5
    levy_weight: float = 0.0

class MetastasisMesh:
    def __init__(self, n_cells: int = 50):
        self.cells: List[Cell] = []
        for i in range(n_cells):
            self.cells.append(Cell(
                id=f"C{i+1:03d}",
                energy=0.3 + random.random() * 0.5,
                epigenetic_state=random.random(),
                immune_evasion=random.random() * 0.6,
                microenvironment_fit=random.random()
            ))
        self.total_levy = 0.0
        self.events: List[Dict] = []
        self.time = 0

    def log(self, msg: str, weight: float = 1.0):
        self.total_levy += weight
        self.events.append({"t": self.time, "msg": msg, "levy": weight})
        print(f"[t={self.time:04d} L={self.total_levy:.1f}] {msg}")

    def magnetic_detach(self):
        candidates = [c for c in self.cells if c.attached]
        if not candidates:
            return
        c = random.choice(candidates)
        c.attached = False
        survival = c.immune_evasion * c.epigenetic_state
        if survival < 0.25:
            self.log(f"{c.id} detached but eliminated by immune pressure", 3)
            self.cells.remove(c)
        else:
            c.dormancy = min(1.0, c.dormancy + 0.4)
            self.log(f"{c.id} magnetic detach → circulating / dormant (evasion={c.immune_evasion:.2f})", 8)
            c.levy_weight += 8

    def magnetic_attach(self, organ_microenv: float = 0.5):
        free = [c for c in self.cells if not c.attached]
        if not free:
            return
        c = random.choice(free)
        fit = c.microenvironment_fit * organ_microenv * c.epigenetic_state
        if fit > 0.45:
            c.attached = True
            c.dormancy = max(0.0, c.dormancy - 0.6)
            self.log(f"{c.id} colonized new site (fit={fit:.2f}) — dormancy exit", 12)
            c.levy_weight += 12
        else:
            self.log(f"{c.id} failed to colonize (fit={fit:.2f}) — remains dormant", 2)
            c.dormancy = min(1.0, c.dormancy + 0.2)

    def step(self):
        self.time += 1
        if random.random() < 0.15:
            self.magnetic_detach()
        if random.random() < 0.12:
            organ = random.uniform(0.3, 0.9)
            self.magnetic_attach(organ)
        for c in self.cells:
            if c.dormancy > 0.7 and random.random() < 0.05 * c.epigenetic_state:
                self.log(f"{c.id} spontaneous dormancy exit attempt", 4)
                c.dormancy *= 0.5

    def reconcile(self):
        detached = sum(1 for c in self.cells if not c.attached)
        dormant = sum(1 for c in self.cells if c.dormancy > 0.5)
        self.log(f"DELTA RECONCILIATION — detached={detached}, high-dormancy={dormant}, total_levy={self.total_levy:.1f}", 0)
        return {
            "time": self.time,
            "cells": len(self.cells),
            "detached": detached,
            "dormant": dormant,
            "levy": self.total_levy,
            "events": len(self.events)
        }

def run_simulation(steps: int = 200, seed: int = 42):
    random.seed(seed)
    mesh = MetastasisMesh(40)
    print("=== Oroboro Metastasis Mesh Simulation ===")
    print("Modeling dormancy, non-genetic factors, colonization via state reduction\n")
    for _ in range(steps):
        mesh.step()
        if mesh.time % 50 == 0:
            mesh.reconcile()
    result = mesh.reconcile()
    print("\n=== Final Observable Result (after reconciliation) ===")
    print(json.dumps(result, indent=2))
    print("\n=== Insights from relational simulation ===")
    print("• Dormancy entry is tightly coupled to detach events (magnetic pulses) and immune pressure.")
    print("• Exit requires sufficient epigenetic plasticity + favorable microenvironment fit.")
    print("• Colonization success is probabilistic and non-genetic: same genetic clone can succeed or fail based on local relational state.")
    print("• Independent parts (cells) continue; global heat-trace / levy ledger recombines to match whole-system outcome.")
    return result

if __name__ == "__main__":
    run_simulation()
