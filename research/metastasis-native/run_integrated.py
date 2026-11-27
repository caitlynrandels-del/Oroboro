#!/usr/bin/env python3
"""Re-run the native metastasis sim with ALL Oroboro components in one conjunctive loop.

Compares against the pre-integration native run, leave-one-out ablates each component
to show it is load-bearing, re-runs key settings, and re-sweeps the recycled 454 settings.
Speculative modeling only. No biological or clinical claims.
"""
from __future__ import annotations
import json, time
import numpy as np, pandas as pd
import run_priority as rp
from oro_native import load_params, run, reconcile_whole_vs_parts, NEUTRAL

import sys
# Usage: python run_integrated.py            -> conjunctive baseline at params.json levy_gain (1.0), data/integrated/
#        python run_integrated.py --calibrate -> pick the grid gain closest to the original calibration targets
CALIBRATE = "--calibrate" in sys.argv
OUT = rp.DATA / ("integrated_calibrated" if CALIBRATE else "integrated"); OUT.mkdir(exist_ok=True)
TARGET = dict(p_overt_any=0.217, dorm_alive_mean=10.38)   # original oro_cascade calibration targets


def extra(rows, s):
    for k in ("pressure_mean", "pressure_max", "transcriber_entries", "transcriber_critical", "adapted"):
        s[k] = float(np.mean([r[k] for r in rows]))
    s["pipeline_levy_ok"] = bool(all(r["pipeline_levy_ok"] for r in rows))
    s["genesis_closed"] = bool(all(r["genesis_closed"] for r in rows))
    return s


def main():
    rp._init(); P = load_params(); t0 = time.time(); ledger = {}
    wp = {}
    for ov in (dict(integrated=False), dict(integrated=True)):
        a = run("Prostate", 17000, P, sig=True, native_overrides=ov)
        b = run("Prostate", 17000, P, mode="decomposed", sig=True, native_overrides=ov)
        wp[str(ov)] = reconcile_whole_vs_parts(a, b)["consistent"]
    ledger["whole_vs_parts_consistent"] = wp; print("WHOLE vs PARTS", wp)

    # baseline: pre-integration vs integrated at two Levy gains (200 seeds x 5 cancers)
    base = []
    grid = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.5, 1.0]   # calibration grid for the one new coupling
    for name, ov in [("pre_integration", dict(integrated=False))] + \
                    [(f"integrated_levy_gain_{g}", dict(levy_gain=g)) for g in grid]:
        rows = rp.run_condition(dict(NEUTRAL), nseed=200, overrides=ov)
        s = extra(rows, rp.summarize(rows, name, "baseline"))
        s["calib_err"] = abs(s["p_overt_any"] - TARGET["p_overt_any"]) / TARGET["p_overt_any"] + \
                         abs(s["dorm_alive_mean"] - TARGET["dorm_alive_mean"]) / TARGET["dorm_alive_mean"]
        base.append(s); print("BASE", name, round(s["p_overt_any"], 4), round(s["dorm_alive_mean"], 3), round(s["calib_err"], 4), f"{time.time()-t0:.0f}s")
    pd.DataFrame(base).to_csv(OUT / "baseline_compare.csv", index=False)
    integ = [b for b in base if b["condition"].startswith("integrated")]
    best = min(integ, key=lambda s: s["calib_err"])
    gain = float(best["condition"].rsplit("_", 1)[1]) if CALIBRATE else float(P["native"].get("levy_gain", 1.0))
    ledger["levy_gain_used"] = gain; ledger["calibration_best_gain"] = float(best["condition"].rsplit("_", 1)[1])
    ledger["baseline"] = base; print("USING levy_gain", gain, "(calibration-best", ledger["calibration_best_gain"], ")")

    # leave-one-out: each component removed from the integrated loop (100 seeds x 5)
    loo = [("integrated_full", {}), ("minus_principles_gate", dict(principles_gate=False)),
           ("minus_levy_feedback", dict(levy_feedback=False)), ("minus_damped_reconcile", dict(damped_reconcile=False)),
           ("minus_adaptive_niche", dict(adaptive_niche=False)), ("minus_looped_niche", dict(include_loops=False)),
           ("pre_integration", dict(integrated=False))]
    levers = [("baseline", dict(NEUTRAL)), ("valuation_threshold=0.80", dict(NEUTRAL, valuation_threshold=0.80)),
              ("organ_perm_scale=0.4", dict(NEUTRAL, organ_perm_scale=0.4)), ("dorm_clear_mult=20", dict(NEUTRAL, dorm_clear_mult=20.0)),
              ("colonization_barrier=0.3", dict(NEUTRAL, colonization_barrier=0.3))]
    krows = []
    for lname, lev in levers:
        for aname, ov in loo:
            o = dict(levy_gain=gain); o.update(ov)
            rows = rp.run_condition(lev, nseed=100, overrides=o)
            s = extra(rows, rp.summarize(rows, lname, aname)); s["ablation"] = aname; krows.append(s)
            print("LOO", lname, aname, round(s["p_overt_any"], 3), round(s["dorm_alive_mean"], 3), round(s["pressure_mean"], 4), round(s["adapted"], 2))
    pd.DataFrame(krows).to_csv(OUT / "key_settings_leave_one_out.csv", index=False)

    # tilt under the integrated loop
    trows = []
    for tilt in (0.0, 0.3, 0.6):
        rows = rp.run_condition(dict(NEUTRAL), nseed=80, overrides=dict(levy_gain=gain, tilt=tilt, torque_phase=0.0))
        s = extra(rows, rp.summarize(rows, f"tilt={tilt}", "tilt_integrated")); trows.append(s)
        print("TILT", tilt, round(s["p_overt_any"], 3), round(s["dorm_alive_mean"], 3))
    pd.DataFrame(trows).to_csv(OUT / "tilt_probe_integrated.csv", index=False)

    # 454 recycled settings (40 seeds x 5)
    settings = pd.read_csv(rp.DATA / "pre_integration" / "original_454_settings.csv")
    sweep = []
    for i, row in settings.iterrows():
        lev = rp.lever_from_row(row)
        rows = rp.run_condition(lev, nseed=40, overrides=dict(levy_gain=gain))
        s = extra(rows, rp.summarize(rows, row["condition"], "integrated_454"))
        for k in rp.LEV_KEYS: s[k] = lev[k]
        s["original_p_overt_any"] = float(row["p_overt_any"]); s["original_dorm_alive_mean"] = float(row["dorm_alive_mean"])
        sweep.append(s)
        if (i + 1) % 50 == 0: print(f"  sweep {i+1}/{len(settings)} {time.time()-t0:.0f}s")
    sdf = pd.DataFrame(sweep); sdf.to_csv(OUT / "sweep_454_integrated.csv", index=False)
    pre = pd.read_csv(rp.DATA / "pre_integration" / "sweep_454_native.csv")
    y = "dorm_alive_mean"
    ledger["correlations"] = {
        "integrated_frustrated_end_vs_dorm": rp.bootstrap_corr(sdf["n_frustrated_mean"], sdf[y], "spearman"),
        "integrated_dorm_on_frustrated_vs_dorm": rp.bootstrap_corr(sdf["dorm_on_frustrated_mean"], sdf[y], "spearman"),
        "integrated_vs_pre_dorm": rp.bootstrap_corr(sdf[y], pre[y], "spearman"),
        "integrated_vs_pre_povert": rp.bootstrap_corr(sdf["p_overt_any"], pre["p_overt_any"], "spearman"),
        "integrated_vs_original_dorm": rp.bootstrap_corr(sdf[y], sdf["original_dorm_alive_mean"], "spearman"),
    }
    both = sdf[(sdf["p_overt_any"] < 0.05) & (sdf[y] < 2.0)]
    ledger["settings_clearing_both"] = both[["condition", "p_overt_any", y] + rp.LEV_KEYS].to_dict("records")
    ledger["all_checks"] = dict(census=bool(sdf["census_ok"].all()), levy=bool(sdf["levy_ok"].all()),
                                consensus=bool(sdf["consensus_ok"].all()), pipeline_levy=bool(sdf["pipeline_levy_ok"].all()),
                                genesis_closed=bool(sdf["genesis_closed"].all()))
    json.dump(ledger, open(OUT / "integrated_ledger.json", "w"), indent=2, default=str)
    print("CORR", json.dumps(ledger["correlations"], indent=1)); print("CHECKS", ledger["all_checks"])
    print("CLEAR BOTH", len(both)); print(f"DONE {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
