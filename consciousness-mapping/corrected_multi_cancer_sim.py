#!/usr/bin/env python3
# SUPERSEDED (2026-11-27): NON-NATIVE, NON-INTEGRATED RUN. Kept for history.
# Audit: this sim draws from Python `random` and calls no Oroboro component in a loop
# (no NaCl polarity mesh / odd loops, no mesh consensus, no deterministic delta
# reconciliation, Levy/Nexus/Transcriber/Genesis absent or ledger-only, no Oasis or
# PrinciplesGate). Native, integrated replacement:
#   https://github.com/caitlynrandels-del/Oroboro/tree/main/research/metastasis-native
# Speculative in-silico modeling only. No clinical, medical or engineering claims.
"""
Oroboro Metastasis Architecture Testbed – Corrected Multi-Cancer Runs
Each cancer gets its own seed and organ permissiveness.
Standardized Levy weights: detach +7, colonize +14, clear +1, fail +2
"""
import random, json
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Cell:
    id: str
    attached: bool = True
    dormancy: float = 0.0
    epigenetic_state: float = 0.5
    immune_evasion: float = 0.4
    microenvironment_fit: float = 0.5
    organ: str = "primary"
    levy_weight: float = 0.0

def run_cancer(name: str, organ_perm: Dict[str, float], seed: int, months: int = 120, n: int = 400):
    random.seed(seed)
    cells: List[Cell] = []
    for i in range(n):
        cells.append(Cell(
            id=f"{name[:3].upper()}{i+1:03d}",
            epigenetic_state=random.random(),
            immune_evasion=0.3 + random.random() * 0.4,
            microenvironment_fit=random.random()
        ))
    levy = 0.0
    time = 0
    overt = 0
    bone_or_preferred = 0
    events = []
    preferred = max(organ_perm, key=organ_perm.get)

    def log(msg: str, w: float = 1.0):
        nonlocal levy
        levy += w
        events.append({"t": time, "msg": msg, "w": w})
        if len(events) < 20 or time % 24 == 0:
            print(f"[{name:12} t={time:03d} L={levy:5.0f}] {msg}")

    print(f"\n=== {name} (seed={seed}, preferred={preferred}) ===")
    for _ in range(months):
        time += 1
        if random.random() < 0.11:
            cands = [c for c in cells if c.attached and c.organ == "primary"]
            if cands:
                c = random.choice(cands)
                if random.random() < 0.72:
                    log(f"{c.id} cleared in circulation", 1)
                    cells.remove(c)
                else:
                    c.attached = False
                    c.dormancy = min(1.0, c.dormancy + 0.5)
                    log(f"{c.id} detached → dormant candidate", 7)
        if random.random() < 0.055:
            free = [c for c in cells if not c.attached]
            if free:
                c = random.choice(free)
                organ = random.choices(list(organ_perm.keys()), weights=list(organ_perm.values()))[0]
                fit = c.microenvironment_fit * organ_perm[organ] * (0.55 + 0.45 * c.epigenetic_state)
                thr = 0.30 if organ == preferred else 0.42
                if fit > thr and random.random() < 0.65:
                    c.attached = True
                    c.organ = organ
                    c.dormancy = max(0.0, c.dormancy - 0.6)
                    overt += 1
                    if organ == preferred:
                        bone_or_preferred += 1
                    log(f"{c.id} COLONIZED {organ} (fit={fit:.2f})", 14)
                else:
                    log(f"{c.id} failed {organ} (fit={fit:.2f})", 2)
                    c.dormancy = min(1.0, c.dormancy + 0.1)
        for c in cells[:]:
            if c.dormancy > 0.6 and random.random() < 0.012 * c.epigenetic_state:
                log(f"{c.id} spontaneous exit attempt", 4)
                c.dormancy *= 0.5

    dormant = sum(1 for c in cells if c.dormancy > 0.5)
    result = {
        "cancer": name,
        "seed": seed,
        "preferred_organ": preferred,
        "cells_remaining": len(cells),
        "overt_mets": overt,
        "preferred_mets": bone_or_preferred,
        "high_dormancy": dormant,
        "levy": levy,
        "events": len(events)
    }
    print(f"Final: cells={len(cells)} overt={overt} preferred={bone_or_preferred} dormant={dormant} levy={levy:.0f}")
    return result

configs = [
    ("Prostate",     {"bone": 0.85, "lung": 0.25, "liver": 0.18, "lymph": 0.30}, 17),
    ("ER+ Breast",   {"bone": 0.70, "lung": 0.40, "liver": 0.35, "brain": 0.20}, 42),
    ("Lung",         {"lung": 0.60, "bone": 0.45, "liver": 0.40, "brain": 0.50}, 99),
    ("Melanoma",     {"lung": 0.55, "skin": 0.50, "liver": 0.40, "brain": 0.45}, 123),
    ("Colorectal",   {"liver": 0.75, "lung": 0.40, "bone": 0.25, "peritoneum": 0.35}, 77),
]

results = {}
for name, perm, seed in configs:
    results[name] = run_cancer(name, perm, seed)

print("\n=== Corrected Summary ===")
print(json.dumps(results, indent=2))
