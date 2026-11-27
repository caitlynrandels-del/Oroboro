#!/usr/bin/env python3
"""Calibrate, sweep the recycled 454 settings, ablations, tilt, and priority correlations.

Speculative modeling only. No biological or clinical claims.
"""
from __future__ import annotations
import json, os, time, math, csv
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

from oro_native import load_params, run, reconcile_whole_vs_parts, NEUTRAL
from oro_mesh import build_system_mesh

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
CHARTS = HERE / "charts"
DATA.mkdir(exist_ok=True)
CHARTS.mkdir(exist_ok=True)

CANCERS = None
P = None
LEV_KEYS = ["shed_mult","circ_clear_mult","dorm_clear_mult","dorm_maintenance",
            "organ_perm_scale","pref_perm_scale","valuation_threshold","colonization_barrier","start_month"]


def _init():
    global P, CANCERS
    P = load_params()
    CANCERS = list(P["cancers"])


def _one(args):
    cancer, seed, lever, overrides = args
    # lever may contain start_month etc.
    return run(cancer, seed, P, lever=lever, native_overrides=overrides)


def run_condition(lever, nseed, overrides=None, n_workers=7):
    tasks = []
    for c in CANCERS:
        cs = P["cancers"][c]["seed"]
        for k in range(nseed):
            tasks.append((c, cs * 1000 + k, lever, overrides))
    rows = []
    if n_workers <= 1 or len(tasks) < 16:
        for t in tasks:
            rows.append(_one(t))
    else:
        with ProcessPoolExecutor(max_workers=n_workers, initializer=_init) as ex:
            rows = list(ex.map(_one, tasks, chunksize=max(1, len(tasks)//(n_workers*8))))
    return rows


def summarize(rows, condition="", experiment=""):
    if not rows:
        return {}
    overt = np.array([r["overt"] for r in rows], dtype=float)
    dorm = np.array([r["dorm_alive"] for r in rows], dtype=float)
    shed = np.array([r["shed"] for r in rows], dtype=float)
    frust = np.array([r["n_frustrated"] for r in rows], dtype=float)
    frust_m = np.array([r["n_frustrated_mean"] for r in rows], dtype=float)
    frust0 = np.array([r["n_frustrated0"] for r in rows], dtype=float)
    dorm_f = np.array([r["dorm_on_frustrated"] for r in rows], dtype=float)
    levy = np.array([r["levy"] for r in rows], dtype=float)
    elim = ((overt == 0) & (dorm == 0) & (np.array([r["circ_alive"] for r in rows]) == 0))
    out = dict(
        condition=condition, experiment=experiment, runs=len(rows),
        shed_mean=float(shed.mean()),
        p_overt_any=float((overt > 0).mean()),
        overt_mean=float(overt.mean()),
        dorm_alive_mean=float(dorm.mean()),
        p_dorm_any=float((dorm > 0).mean()),
        p_eliminated=float(elim.mean()),
        levy_mean=float(levy.mean()),
        n_frustrated_mean=float(frust.mean()),
        n_frustrated_series_mean=float(frust_m.mean()),
        n_frustrated0_mean=float(frust0.mean()),
        dorm_on_frustrated_mean=float(dorm_f.mean()),
        n_repaired_mean=float(np.mean([r["n_repaired"] for r in rows])),
        extracted_mean=float(np.mean([r.get("extracted", 0) for r in rows])),
        extract_yield_mean=float(np.mean([r.get("extract_yield", 0.0) for r in rows])),
        extracted_circ_mean=float(np.mean([r.get("extracted_circ", 0) for r in rows])),
        extracted_dorm_mean=float(np.mean([r.get("extracted_dorm", 0) for r in rows])),
        extracted_overt_mean=float(np.mean([r.get("extracted_overt", 0) for r in rows])),
        extract_attempts_mean=float(np.mean([r.get("extract_attempts", 0) for r in rows])),
        extract_commits_mean=float(np.mean([r.get("extract_commits", 0) for r in rows])),
        n_tagged_ever_mean=float(np.mean([r.get("n_tagged_ever", 0) for r in rows])),
        n_leaky_ever_mean=float(np.mean([r.get("n_leaky_ever", 0) for r in rows])),
        n_located_ever_mean=float(np.mean([r.get("n_located_ever", 0) for r in rows])),
        n_frustrated_circ_mean=float(np.mean([r.get("n_frustrated_circ", 0) for r in rows])),
        n_frustrated_niche_mean=float(np.mean([r.get("n_frustrated_niche", 0) for r in rows])),
        n_frustrated_extract_mean=float(np.mean([r.get("n_frustrated_extract", 0) for r in rows])),
        n_locked_extract_mean=float(np.mean([r.get("n_locked_extract", 0) for r in rows])),
        census_ok=bool(all(r["census_ok"] for r in rows)),
        levy_ok=bool(all(r["levy_ok"] for r in rows)),
        consensus_ok=bool(all(r["consensus_ok"] for r in rows)),
        inversion_holds=bool(all(r["inversion_holds"] for r in rows)),
    )
    return out


def bootstrap_corr(x, y, kind="spearman", n_boot=2000, seed=42):
    rng = np.random.default_rng(seed)
    x = np.asarray(x, float); y = np.asarray(y, float)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if kind == "spearman":
        r, p = stats.spearmanr(x, y)
        def fn(a, b):
            return stats.spearmanr(a, b).correlation
    else:
        r, p = stats.pearsonr(x, y)
        def fn(a, b):
            return stats.pearsonr(a, b)[0]
    boots = []
    n = len(x)
    for _ in range(n_boot):
        i = rng.integers(0, n, n)
        try:
            boots.append(fn(x[i], y[i]))
        except Exception:
            boots.append(np.nan)
    boots = np.array(boots, float)
    lo, hi = np.nanpercentile(boots, [2.5, 97.5])
    return dict(r=float(r), p=float(p), ci_lo=float(lo), ci_hi=float(hi), n=int(n))


def partial_pearson(x, y, z):
    """Pearson of residuals of x and y after linear regression on z (cells released)."""
    x = np.asarray(x, float); y = np.asarray(y, float); z = np.asarray(z, float)
    def resid(a, b):
        b2 = np.column_stack([np.ones(len(b)), b])
        coef, _, _, _ = np.linalg.lstsq(b2, a, rcond=None)
        return a - b2 @ coef
    rx, ry = resid(x, z), resid(y, z)
    r, p = stats.pearsonr(rx, ry)
    return dict(r=float(r), p=float(p), n=int(len(x)))


def lever_from_row(row):
    lev = dict(NEUTRAL)
    for k in LEV_KEYS:
        lev[k] = int(row[k]) if k == "start_month" else float(row[k])
    return lev


def main():
    global P, CANCERS
    _init()
    t_all = time.time()
    ledger = {}

    # --- mesh structural facts (once) ---
    organs_ex = list(P["cancers"]["Prostate"]["organ_permissiveness"])
    mesh_l, meta_l = build_system_mesh(organs_ex, include_loops=True)
    mesh_t, meta_t = build_system_mesh(organs_ex, include_loops=False)
    inv_l = mesh_l.inversion_holds()
    inv_t = mesh_t.inversion_holds()
    struct = dict(
        looped=dict(n_nodes=meta_l["n_nodes"], n_edges=meta_l["n_edges"],
                    n_frustrated0=meta_l["n_frustrated0"], n_locked0=meta_l["n_locked0"],
                    inversion_holds=inv_l, counts=mesh_l.counts()),
        tree=dict(n_nodes=meta_t["n_nodes"], n_edges=meta_t["n_edges"],
                  n_frustrated0=meta_t["n_frustrated0"], n_locked0=meta_t["n_locked0"],
                  inversion_holds=inv_t, counts=mesh_t.counts()),
    )
    json.dump(struct, open(DATA / "mesh_structure.json", "w"), indent=2)
    print("MESH looped", struct["looped"], "\nTREE", struct["tree"])

    # --- whole vs parts check ---
    a = run("Prostate", 17000, P, sig=True)
    b = run("Prostate", 17000, P, mode="decomposed", sig=True)
    rec = reconcile_whole_vs_parts(a, b)
    print("WHOLE vs PARTS", rec["consistent"])
    ledger["whole_vs_parts"] = rec

    # --- calibrated baseline (200 seeds / cancer = 1000 runs) ---
    print("=== baseline 200 seeds ===")
    base_rows = run_condition(dict(NEUTRAL), nseed=200)
    base_sum = summarize(base_rows, "baseline", "native_baseline")
    print("BASELINE", base_sum)
    ledger["baseline"] = base_sum
    pd.DataFrame(base_rows).drop(columns=[c for c in pd.DataFrame(base_rows).columns if c.startswith("_")], errors="ignore")\
        .to_csv(DATA / "baseline_runs.csv", index=False)

    # --- tilt / torque side probe (baseline lever, not in the 454) ---
    tilt_tbl = []
    for tilt in (0.0, 0.3, 0.6):
        rows = run_condition(dict(NEUTRAL), nseed=80, overrides=dict(tilt=tilt, torque_phase=0.0))
        s = summarize(rows, f"tilt={tilt}", "tilt")
        # preferred-organ share
        pref = np.array([r["overt_preferred"] for r in rows], float)
        overt = np.array([r["overt"] for r in rows], float)
        s["overt_pref_share"] = float(pref.sum() / overt.sum()) if overt.sum() else float("nan")
        tilt_tbl.append(s)
        print("TILT", s["condition"], s)
    pd.DataFrame(tilt_tbl).to_csv(DATA / "tilt_probe.csv", index=False)
    ledger["tilt"] = tilt_tbl

    # --- key settings + ablations at 100 seeds ---
    key_levers = [
        ("baseline", dict(NEUTRAL)),
        ("valuation_threshold=0.80", dict(NEUTRAL, valuation_threshold=0.80)),
        ("valuation_threshold=0.85", dict(NEUTRAL, valuation_threshold=0.85)),
        ("organ_perm_scale=0.4", dict(NEUTRAL, organ_perm_scale=0.4)),
        ("organ_perm_scale=0.2", dict(NEUTRAL, organ_perm_scale=0.2)),
        ("dorm_clear_mult=10", dict(NEUTRAL, dorm_clear_mult=10.0)),
        ("dorm_clear_mult=20", dict(NEUTRAL, dorm_clear_mult=20.0)),
        ("dorm_clear_mult=50", dict(NEUTRAL, dorm_clear_mult=50.0)),
        ("dorm_maintenance=1.0", dict(NEUTRAL, dorm_maintenance=1.0)),
        ("colonization_barrier=0.3", dict(NEUTRAL, colonization_barrier=0.3)),
        ("colonization_barrier=0.5", dict(NEUTRAL, colonization_barrier=0.5)),
    ]
    ablations = [
        ("native_full", None),
        ("ablate_looped_niche", dict(include_loops=False)),
        ("ablate_damped_reconcile", dict(damped_reconcile=False)),
        ("ablate_adaptive_niche", dict(adaptive_niche=False)),
    ]
    key_rows = []
    for cname, lev in key_levers:
        for aname, ov in ablations:
            print(f"=== key {cname} / {aname} ===")
            rows = run_condition(lev, nseed=100, overrides=ov)
            s = summarize(rows, cname, aname)
            s["ablation"] = aname
            key_rows.append(s)
            print("  ", s["p_overt_any"], s["dorm_alive_mean"], s["n_frustrated_mean"])
    pd.DataFrame(key_rows).to_csv(DATA / "key_settings_ablations.csv", index=False)
    ledger["key_settings"] = key_rows

    # --- 454 unique settings, 40 seeds / cancer = 200 runs each ---
    settings = pd.read_csv(DATA / "original_454_settings.csv")
    print("=== sweep 454 settings, 40 seeds x 5 cancers ===")
    sweep = []
    t0 = time.time()
    for i, row in settings.iterrows():
        lev = lever_from_row(row)
        rows = run_condition(lev, nseed=40)
        s = summarize(rows, row["condition"], "native_454")
        for k in LEV_KEYS:
            s[k] = lev[k]
        s["original_p_overt_any"] = float(row["p_overt_any"])
        s["original_dorm_alive_mean"] = float(row["dorm_alive_mean"])
        s["original_overt_mean"] = float(row["overt_mean"])
        s["original_shed_mean"] = float(row["shed_mean"])
        sweep.append(s)
        if (i + 1) % 25 == 0 or i == 0:
            print(f"  {i+1}/{len(settings)}  elapsed {time.time()-t0:.0f}s  last p_overt={s['p_overt_any']:.3f} dorm={s['dorm_alive_mean']:.2f} frust={s['n_frustrated_mean']:.1f}")
    sdf = pd.DataFrame(sweep)
    sdf.to_csv(DATA / "sweep_454_native.csv", index=False)
    print("sweep done", len(sdf), "in", time.time()-t0)

    # --- priority correlations ---
    def corrs(df, xcol, ycol):
        return dict(
            spearman=bootstrap_corr(df[xcol], df[ycol], "spearman"),
            pearson=bootstrap_corr(df[xcol], df[ycol], "pearson"),
        )
    y = "dorm_alive_mean"
    results = {
        "n_settings": int(len(sdf)),
        "frustrated_end_vs_dorm": corrs(sdf, "n_frustrated_mean", y),
        "frustrated_series_vs_dorm": corrs(sdf, "n_frustrated_series_mean", y),
        "frustrated0_vs_dorm": corrs(sdf, "n_frustrated0_mean", y),
        "dorm_on_frustrated_vs_dorm": corrs(sdf, "dorm_on_frustrated_mean", y),
        "partial_frustrated_end_vs_dorm_given_shed": partial_pearson(sdf["n_frustrated_mean"], sdf[y], sdf["shed_mean"]),
        "partial_dorm_on_frustrated_vs_dorm_given_shed": partial_pearson(sdf["dorm_on_frustrated_mean"], sdf[y], sdf["shed_mean"]),
    }
    # Circularity checks
    rng = np.random.default_rng(123)
    shuf = sdf["n_frustrated_mean"].to_numpy().copy(); rng.shuffle(shuf)
    results["shuffled_frustrated_end_vs_dorm"] = bootstrap_corr(shuf, sdf[y], "spearman")
    # residual circularity: dorm_on_frustrated / max(dorm, eps) vs frustrated edges
    frac = sdf["dorm_on_frustrated_mean"] / np.maximum(sdf[y], 1e-6)
    results["frustrated_end_vs_frust_occupancy_fraction"] = bootstrap_corr(sdf["n_frustrated_mean"], frac, "spearman")
    results["shed_vs_dorm"] = corrs(sdf, "shed_mean", y)
    # also vs original dormant pool (recycled outcome, not a native loop count)
    results["native_frust_vs_original_dorm"] = corrs(sdf, "n_frustrated_mean", "original_dorm_alive_mean")
    results["native_dorm_vs_original_dorm"] = corrs(sdf, "dorm_alive_mean", "original_dorm_alive_mean")
    results["native_povert_vs_original_povert"] = corrs(sdf, "p_overt_any", "original_p_overt_any")
    json.dump(results, open(DATA / "priority_correlations.json", "w"), indent=2)
    print(json.dumps(results, indent=2))

    # simple scatter data already in csv; make a tiny matplotlib figure
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.0))
    axes[0].scatter(sdf["n_frustrated_mean"], sdf["dorm_alive_mean"], s=12, alpha=0.55, c="#1f4e79", edgecolors="none")
    axes[0].set_xlabel("Mean frustrated-edge count (end of run)")
    axes[0].set_ylabel("Dormant pool (mean cells)")
    axes[0].set_title("Native frustrated edges vs dormant pool")
    axes[1].scatter(sdf["dorm_on_frustrated_mean"], sdf["dorm_alive_mean"], s=12, alpha=0.55, c="#9c2a2a", edgecolors="none")
    axes[1].set_xlabel("Cells on frustrated edges (mean)")
    axes[1].set_ylabel("Dormant pool (mean cells)")
    axes[1].set_title("Frustrated occupancy vs dormant pool")
    for ax in axes:
        ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(CHARTS / "frustrated_vs_dormant.png", dpi=140)
    fig.savefig(CHARTS / "frustrated_vs_dormant.svg")
    plt.close()

    ledger["correlations"] = results
    ledger["seconds"] = time.time() - t_all
    json.dump(ledger, open(DATA / "ledger.json", "w"), indent=2, default=float)
    print("DONE in", ledger["seconds"], "s")


if __name__ == "__main__":
    main()
