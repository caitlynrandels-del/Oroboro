#!/usr/bin/env python3
"""Follow-up: slider re-zips only if a tooth's re-test can differ (material < 1 adds per-test noise)."""
import sys, json
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1].parent) + "/metastasis-native")
import numpy as np, run_priority as RP
from oro_native import NEUTRAL
RP._init(); out = []
for g in (1.0, 0.05):
    for mat in (1.0, 0.7, 0.4):
        for sl in (0.0, 0.5):
            o = dict(levy_gain=g, zipper=True, zip_tolerance=0.3, zip_material=mat, zip_slider=sl)
            rows = RP.run_condition(dict(NEUTRAL), nseed=40, overrides=o)
            s = dict(gain=g, material=mat, slider=sl, tol=0.3, p_overt_any=float(np.mean([r["overt"] > 0 for r in rows])),
                     dorm_alive_mean=float(np.mean([r["dorm_alive"] for r in rows])), zip_skips=float(np.mean([r["zip_skips"] for r in rows])),
                     zip_rezips=float(np.mean([r["zip_rezips"] for r in rows])), n_frustrated=float(np.mean([r["n_frustrated"] for r in rows])))
            out.append(s); print(s, flush=True)
json.dump(out, open(str(__import__("pathlib").Path(__file__).resolve().parents[1]) + "/data/slider_followup.json", "w"), indent=1)
