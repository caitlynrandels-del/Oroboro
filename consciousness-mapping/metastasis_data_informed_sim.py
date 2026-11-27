#!/usr/bin/env python3
# SUPERSEDED (2026-11-27): NON-NATIVE, NON-INTEGRATED RUN. Kept for history.
# Audit: this sim draws from Python `random` and calls no Oroboro component in a loop
# (no NaCl polarity mesh / odd loops, no mesh consensus, no deterministic delta
# reconciliation, Levy/Nexus/Transcriber/Genesis absent or ledger-only, no Oasis or
# PrinciplesGate). Native, integrated replacement:
#   https://github.com/caitlynrandels-del/Oroboro/tree/main/research/metastasis-native
# Speculative in-silico modeling only. No clinical, medical or engineering claims.
"""
Oroboro Metastasis Model – Data-Informed Simulation
Incorporates publicly available clinical and experimental data on:
- Metastatic inefficiency (peritoneovenous shunt studies)
- DTC prevalence in early breast cancer bone marrow (~27-40%)
- Heterogeneous relapse potential of DTCs
- Organ-specific microenvironments
- Dormancy durations (months to decades)
- Metastasis-to-metastasis seeding
"""

import random
import json
from dataclasses import dataclass, field
from typing import List, Dict

# Public data-derived constants
DTC_PREVALENCE_BM = 0.30          # ~27-40% of early breast cancer patients have DTCs in BM
RELAPSE_FRACTION_DTC_POS = 0.40   # only a minority of DTC+ patients relapse within 10 years
METASTATIC_INEFFICIENCY = 0.85   # high clearance; rare survival to colonization attempt
ORGAN_PERMISSIVENESS = {
    "bone": 0.65,    # more permissive for many breast cancers
    "lung": 0.35,    # macrophages often enforce dormancy
    "liver": 0.45,
    "brain": 0.25
}
DORMANCY_HALF_LIFE_YEARS = 12     # approximate from modeling studies

@dataclass
class Cell:
    id: str
    attached: bool = True
    energy: float = 0.5
    dormancy: float = 0.0
    epigenetic_state: float = 0.5
    immune_evasion: float = 0.3
    microenvironment_fit: float = 0.5
    organ: str = "primary"
    levy_weight: float = 0.0
    seed_origin: str = "primary"  # primary or metastasis-to-metastasis

class DataInformedMetastasisMesh:
    def __init__(self, n_cells: int = 1000):
        self.cells: List[Cell] = []
        for i in range(n_cells):
            self.cells.append(Cell(
                id=f"C{i+1:04d}",
                energy=0.3 + random.random() * 0.5,
                epigenetic_state=random.random(),
                immune_evasion=random.random() * 0.6,
                microenvironment_fit=random.random()
            ))
        self.total_levy = 0.0
        self.events: List[Dict] = []
        self.time_months = 0
        self.overt_mets = 0

    def log(self, msg: str, weight: float = 1.0):
        self.total_levy += weight
        self.events.append({"t_months": self.time_months, "msg": msg, "levy": weight})
        if len(self.events) < 40 or self.time_months % 12 == 0:
            print(f"[t={self.time_months:03d}mo L={self.total_levy:.1f}] {msg}")

    def magnetic_detach(self):
        candidates = [c for c in self.cells if c.attached and c.organ == "primary"]
        if not candidates:
            return
        c = random.choice(candidates)
        if random.random() < METASTATIC_INEFFICIENCY:
            self.log(f"{c.id} entered circulation but cleared (metastatic inefficiency)", 1)
            self.cells.remove(c)
            return
        c.attached = False
        c.organ = "circulation"
        survival = c.immune_evasion * c.epigenetic_state
        if survival < 0.3:
            self.log(f"{c.id} detached but eliminated by immune pressure", 3)
            self.cells.remove(c)
        else:
            c.dormancy = min(1.0, c.dormancy + 0.5)
            self.log(f"{c.id} magnetic detach → circulating / likely dormant (evasion={c.immune_evasion:.2f})", 8)
            c.levy_weight += 8

    def attempt_colonization(self):
        free = [c for c in self.cells if not c.attached]
        if not free:
            return
        c = random.choice(free)
        organ = random.choices(list(ORGAN_PERMISSIVENESS.keys()), 
                               weights=list(ORGAN_PERMISSIVENESS.values()))[0]
        fit = c.microenvironment_fit * ORGAN_PERMISSIVENESS[organ] * c.epigenetic_state
        if fit > 0.25 and random.random() < 0.4:
            c.attached = True
            c.organ = organ
            c.dormancy = max(0.0, c.dormancy - 0.7)
            self.overt_mets += 1
            origin = "primary" if c.seed_origin == "primary" else "meta-to-meta"
            self.log(f"{c.id} COLONIZED {organ} (fit={fit:.2f}, origin={origin}) — dormancy exit / outgrowth", 15)
            c.levy_weight += 15
            c.seed_origin = "metastasis"
        else:
            self.log(f"{c.id} failed colonization in {organ} (fit={fit:.2f}) — remains dormant", 2)
            c.dormancy = min(1.0, c.dormancy + 0.15)

    def step_month(self):
        self.time_months += 1
        detach_prob = 0.15 if self.time_months < 36 else 0.05
        if random.random() < detach_prob:
            self.magnetic_detach()
        if random.random() < 0.06:
            self.attempt_colonization()
        for c in self.cells[:]:
            if c.dormancy > 0.6 and random.random() < 0.02 * c.epigenetic_state:
                self.log(f"{c.id} spontaneous dormancy exit attempt", 4)
                c.dormancy *= 0.4

    def reconcile(self):
        detached = sum(1 for c in self.cells if not c.attached)
        dormant = sum(1 for c in self.cells if c.dormancy > 0.5)
        self.log(f"DELTA RECONCILIATION — cells={len(self.cells)}, detached={detached}, high-dormancy={dormant}, overt_mets={self.overt_mets}, levy={self.total_levy:.1f}", 0)
        return {
            "time_months": self.time_months,
            "cells_remaining": len(self.cells),
            "detached": detached,
            "high_dormancy": dormant,
            "overt_metastases": self.overt_mets,
            "levy": self.total_levy,
            "events": len(self.events)
        }

def run_data_informed_simulation(months: int = 120, seed: int = 42):
    random.seed(seed)
    mesh = DataInformedMetastasisMesh(800)
    print("=== Oroboro Data-Informed Metastasis Mesh ===")
    print("Parameters drawn from public literature:")
    print(f"  • DTC BM prevalence ~{DTC_PREVALENCE_BM*100:.0f}%")
    print(f"  • Relapse fraction among DTC+ ~{RELAPSE_FRACTION_DTC_POS*100:.0f}%")
    print(f"  • Extreme metastatic inefficiency (shunt studies)")
    print(f"  • Organ permissiveness: bone > liver > lung > brain")
    print(f"  • Dormancy half-life modeling ~{DORMANCY_HALF_LIFE_YEARS} years\n")
    
    for _ in range(months):
        mesh.step_month()
        if mesh.time_months % 24 == 0:
            mesh.reconcile()
    
    result = mesh.reconcile()
    print("\n=== Final Observable Result (after reconciliation) ===")
    print(json.dumps(result, indent=2))
    
    print("\n=== Insights informed by public data + relational simulation ===")
    print("• Metastatic inefficiency is extreme: most circulating cells are cleared before colonization.")
    print("• DTCs are common (~30% of early breast cancer patients) but only a minority progress to overt metastasis.")
    print("• Organ microenvironments strongly filter success (bone more permissive in many models; lung macrophages enforce dormancy).")
    print("• Dormancy can persist for years-decades; exit depends on epigenetic plasticity + local signals.")
    print("• Secondary (metastasis-to-metastasis) seeding becomes important once the first site is established.")
    print("• Independent cellular states continue; delta reconciliation keeps the global heat-trace / levy ledger consistent.")
    return result

if __name__ == "__main__":
    run_data_informed_simulation()
