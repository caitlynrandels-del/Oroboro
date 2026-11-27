#!/usr/bin/env python3
"""Light as a directed transport signal to an extraction node.

Uses only the native Oroboro conjunctive loop (Genesis, Nexus, Oasis,
PrinciplesGate, NaCl polarity mesh, dream-catcher niches, Dictator ->
Transcriber -> Levy -> damper, deterministic delta reconciliation).
Speculative modeling only. No biological or clinical claims.
"""
from __future__ import annotations
import json, time, sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import run_priority as rp
from oro_native import load_params, run, reconcile_whole_vs_parts, NEUTRAL
from oro_mesh import build_system_mesh

HERE = Path(__file__).resolve().parent
OUT = HERE / "data" / "light_transport"
CHARTS = HERE / "charts"
NOTES = HERE / "notes"
OUT.mkdir(parents=True, exist_ok=True)
CHARTS.mkdir(exist_ok=True)
NOTES.mkdir(exist_ok=True)

NSEED = 40
TARGET = dict(p_overt_any=0.217, dorm_alive_mean=10.38)
MODES = ["lure", "tag_magnet", "flush", "photoacoustic", "combined"]
TIMINGS = ["upstream", "circulation", "post_settling"]
STRENGTHS = [0.2, 0.5, 0.8]
GAINS = [0.05, 1.0]


def extra(rows, s):
    if not rows:
        return s
    for k in ("pressure_mean", "pressure_max", "transcriber_entries",
              "transcriber_critical", "adapted"):
        s[k] = float(np.mean([r[k] for r in rows]))
    s["pipeline_levy_ok"] = bool(all(r["pipeline_levy_ok"] for r in rows))
    s["genesis_closed"] = bool(all(r["genesis_closed"] for r in rows))
    s["extraction_mesh"] = bool(all(r.get("extraction_mesh", False) for r in rows))
    return s


def ov_base(gain, **kw):
    o = dict(levy_gain=float(gain), integrated=True, extraction_coloring="preserve")
    o.update(kw)
    return o


def light_ov(gain, mode, strength, timing, **kw):
    return ov_base(gain, light=True, light_mode=mode, light_strength=float(strength),
                   light_timing=timing, **kw)


def main():
    rp._init()
    P = load_params()
    t0 = time.time()
    ledger = dict(note="Speculative modeling only. No biological or clinical claims.",
                  nseed=NSEED, cancers=list(P["cancers"]),
                  levy_gains=GAINS, modes=MODES, timings=TIMINGS, strengths=STRENGTHS,
                  post_settling_start_month=61)

    # --- mesh structure: none / preserve / joint
    organs = list(P["cancers"]["Prostate"]["organ_permissiveness"])
    struct = {}
    for name, kw in [("none", dict()),
                     ("preserve", dict(extraction=True, extraction_coloring="preserve")),
                     ("joint", dict(extraction=True, extraction_coloring="joint"))]:
        mesh, meta = build_system_mesh(organs, **kw)
        inv = mesh.inversion_holds()
        by = {}
        for e in mesh.edges:
            d = by.setdefault(e.kind, dict(n=0, locked=0, frustrated=0))
            d["n"] += 1
            d["locked" if e.locked else "frustrated"] += 1
        struct[name] = dict(n_nodes=meta["n_nodes"], n_edges=meta["n_edges"],
                            n_frustrated0=meta["n_frustrated0"], n_locked0=meta["n_locked0"],
                            inversion_holds=inv, by_kind=by)
        print("MESH", name, struct[name]["n_edges"], "frust0", struct[name]["n_frustrated0"],
              "inv", inv)
    ledger["mesh"] = struct

    # --- whole vs parts
    wp = {}
    for label, ov in [
        ("no_light_g0.05", ov_base(0.05)),
        ("combined_up_s0.5_g0.05", light_ov(0.05, "combined", 0.5, "upstream")),
        ("flush_up_s0.5_g0.05", light_ov(0.05, "flush", 0.5, "upstream")),
        ("combined_joint", light_ov(0.05, "combined", 0.5, "upstream", extraction_coloring="joint")),
    ]:
        a = run("Prostate", 17000, P, sig=True, native_overrides=ov)
        b = run("Prostate", 17000, P, mode="decomposed", sig=True, native_overrides=ov)
        wp[label] = reconcile_whole_vs_parts(a, b)["consistent"]
    ledger["whole_vs_parts_consistent"] = wp
    print("WHOLE vs PARTS", wp)

    summaries = []

    def run_sum(name, lever, ov, experiment):
        rows = rp.run_condition(lever, nseed=NSEED, overrides=ov)
        s = extra(rows, rp.summarize(rows, name, experiment))
        s["levy_gain"] = float((ov or {}).get("levy_gain", P["native"].get("levy_gain", 1.0)))
        s["light"] = bool((ov or {}).get("light", False))
        s["light_mode"] = (ov or {}).get("light_mode", "off")
        s["light_strength"] = float((ov or {}).get("light_strength", 0.0) or 0.0)
        s["light_timing"] = (ov or {}).get("light_timing", "")
        s["extraction_coloring"] = (ov or {}).get("extraction_coloring", "preserve")
        summaries.append(s)
        print(f"{time.time()-t0:6.0f}s {experiment:16s} {name:48s} "
              f"p={s['p_overt_any']:.3f} dorm={s['dorm_alive_mean']:.2f} "
              f"ext={s['extracted_mean']:.2f} y={s['extract_yield_mean']:.3f} "
              f"frust={s['n_frustrated_mean']:.1f} "
              f"checks={s['census_ok'] and s['levy_ok'] and s['consensus_ok'] and s['pipeline_levy_ok']}")
        return s

    # baselines + mesh-only (no transport)
    for gain in GAINS:
        run_sum(f"baseline_g{gain}", dict(NEUTRAL), ov_base(gain), "baseline")
        run_sum(f"mesh_preserve_g{gain}", dict(NEUTRAL),
                ov_base(gain, extraction=True, extraction_coloring="preserve"), "mesh_only")
        run_sum(f"mesh_joint_g{gain}", dict(NEUTRAL),
                ov_base(gain, extraction=True, extraction_coloring="joint"), "mesh_only")

    # main sweep
    for gain in GAINS:
        for mode in MODES:
            for strength in STRENGTHS:
                for timing in TIMINGS:
                    run_sum(f"{mode}/{timing}/s{strength}/g{gain}",
                            dict(NEUTRAL), light_ov(gain, mode, strength, timing), "sweep")

    # key lever interactions (calibrated gain), recycle settled upstream findings
    gain = 0.05
    levers = [
        ("baseline", dict(NEUTRAL)),
        ("valuation_threshold=0.80", dict(NEUTRAL, valuation_threshold=0.80)),
        ("organ_perm_scale=0.4", dict(NEUTRAL, organ_perm_scale=0.4)),
        ("dorm_clear_mult=20", dict(NEUTRAL, dorm_clear_mult=20.0)),
    ]
    light_on = [
        ("no_light", ov_base(gain)),
        ("combined_up_s0.5", light_ov(gain, "combined", 0.5, "upstream")),
        ("combined_up_s0.8", light_ov(gain, "combined", 0.8, "upstream")),
        ("lure_up_s0.5", light_ov(gain, "lure", 0.5, "upstream")),
        ("flush_post_s0.5", light_ov(gain, "flush", 0.5, "post_settling")),
    ]
    for lname, lev in levers:
        for aname, ov in light_on:
            run_sum(f"{lname} | {aname}", lev, ov, "levers")

    # leave-one-out / conjunctive ablations on combined upstream s=0.5, g=0.05
    loo_core = light_ov(0.05, "combined", 0.5, "upstream")
    loo = [
        ("conjunctive_full", {}),
        ("minus_principles_gate", dict(principles_gate=False)),
        ("minus_levy_feedback", dict(levy_feedback=False)),
        ("minus_damped_reconcile", dict(damped_reconcile=False)),
        ("minus_adaptive_niche", dict(adaptive_niche=False)),
        ("minus_looped_niche", dict(include_loops=False)),
        ("minus_oasis_on_extract", dict(light_oasis=False)),
        ("extraction_coloring=joint", dict(extraction_coloring="joint")),
        ("pre_integration", dict(integrated=False)),
    ]
    for aname, ov in loo:
        o = dict(loo_core); o.update(ov)
        run_sum(f"combined_up_s0.5 | {aname}", dict(NEUTRAL), o, "loo")

    sdf = pd.DataFrame(summaries)
    sdf.to_csv(OUT / "light_transport_summaries.csv", index=False)

    # correlations across the light sweep (calibrated gain), plus niche-only frustrated
    sw = sdf[(sdf["experiment"] == "sweep") & (sdf["levy_gain"] == 0.05)]
    corrs = {}
    if len(sw) >= 5:
        corrs["frustrated_end_vs_dorm"] = rp.bootstrap_corr(sw["n_frustrated_mean"], sw["dorm_alive_mean"], "spearman")
        corrs["frustrated_niche_vs_dorm"] = rp.bootstrap_corr(sw["n_frustrated_niche_mean"], sw["dorm_alive_mean"], "spearman")
        corrs["extract_yield_vs_dorm"] = rp.bootstrap_corr(sw["extract_yield_mean"], sw["dorm_alive_mean"], "spearman")
        corrs["extract_yield_vs_povert"] = rp.bootstrap_corr(sw["extract_yield_mean"], sw["p_overt_any"], "spearman")
        corrs["extracted_vs_dorm"] = rp.bootstrap_corr(sw["extracted_mean"], sw["dorm_alive_mean"], "spearman")
    ledger["correlations_sweep_g0.05"] = corrs

    checks = dict(
        census=bool(sdf["census_ok"].all()),
        levy=bool(sdf["levy_ok"].all()),
        consensus=bool(sdf["consensus_ok"].all()),
        pipeline_levy=bool(sdf["pipeline_levy_ok"].all()),
        genesis_closed=bool(sdf["genesis_closed"].all()),
        inversion=bool(sdf["inversion_holds"].all()),
        whole_vs_parts=all(wp.values()),
    )
    ledger["all_checks"] = checks
    ledger["runtime_s"] = time.time() - t0
    json.dump(ledger, open(OUT / "light_transport_ledger.json", "w"), indent=2, default=str)
    print("CORR", json.dumps(corrs, indent=1))
    print("CHECKS", checks)
    print(f"DONE {ledger['runtime_s']:.0f}s  rows={len(sdf)}")

    make_figure(sdf)
    return sdf, ledger


def make_figure(sdf):
    plt.rcParams.update({
        "font.family": "Liberation Sans",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "figure.dpi": 140,
    })
    sw = sdf[(sdf["experiment"] == "sweep")].copy()
    base = sdf[sdf["experiment"] == "baseline"].copy()
    mesh = sdf[sdf["experiment"] == "mesh_only"].copy()
    loo = sdf[sdf["experiment"] == "loo"].copy()
    levers = sdf[sdf["experiment"] == "levers"].copy()

    mode_colors = {
        "lure": "#1f4e79",
        "tag_magnet": "#2a9d8f",
        "flush": "#b5651d",
        "photoacoustic": "#6a4c93",
        "combined": "#9b2226",
    }
    timing_ls = {"upstream": "-", "circulation": "--", "post_settling": ":"}
    timing_marker = {"upstream": "o", "circulation": "s", "post_settling": "D"}

    fig = plt.figure(figsize=(11.0, 12.2))
    fig.suptitle("Light-transport extraction on the native Oroboro mesh\n(speculative modeling only; 40 seeds × 5 cancers)",
                 fontsize=12, color="#1f3a5f", y=0.995)

    # --- 1. colony rate vs strength, levy 0.05
    ax = fig.add_subplot(3, 2, 1)
    sub = sw[sw["levy_gain"] == 0.05]
    b05 = base[base["levy_gain"] == 0.05].iloc[0]
    ax.axhline(b05["p_overt_any"], color="#444", lw=1.0, alpha=0.8, label="no-light baseline")
    ax.axhline(0.217, color="#888", lw=0.8, ls="--", alpha=0.7, label="original target 21.7%")
    for mode in MODES:
        for timing in TIMINGS:
            d = sub[(sub["light_mode"] == mode) & (sub["light_timing"] == timing)].sort_values("light_strength")
            ax.plot(d["light_strength"], d["p_overt_any"],
                    color=mode_colors[mode], ls=timing_ls[timing],
                    marker=timing_marker[timing], ms=4, lw=1.3,
                    label=f"{mode} / {timing}" if timing == "upstream" else None)
    ax.set_xlabel("light strength")
    ax.set_ylabel("colony rate (any overt)")
    ax.set_title("A. Colony rate vs strength  (levy_gain = 0.05)")
    ax.set_ylim(0, 0.28)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=6.5, loc="upper right", framealpha=0.92)

    # --- 2. dormant pool vs strength
    ax = fig.add_subplot(3, 2, 2)
    ax.axhline(b05["dorm_alive_mean"], color="#444", lw=1.0, alpha=0.8, label="no-light baseline")
    ax.axhline(10.38, color="#888", lw=0.8, ls="--", alpha=0.7, label="original target 10.38")
    for mode in MODES:
        for timing in TIMINGS:
            d = sub[(sub["light_mode"] == mode) & (sub["light_timing"] == timing)].sort_values("light_strength")
            ax.plot(d["light_strength"], d["dorm_alive_mean"],
                    color=mode_colors[mode], ls=timing_ls[timing],
                    marker=timing_marker[timing], ms=4, lw=1.3)
    ax.set_xlabel("light strength")
    ax.set_ylabel("mean dormant pool")
    ax.set_title("B. Dormant pool vs strength  (levy_gain = 0.05)")
    ax.grid(True, alpha=0.3)
    # timing legend
    ax.plot([], [], "k-", label="upstream")
    ax.plot([], [], "k--", label="circulation")
    ax.plot([], [], "k:", label="post-settling")
    ax.legend(fontsize=6.5, loc="upper right", framealpha=0.92)

    # --- 3. extract yield vs strength
    ax = fig.add_subplot(3, 2, 3)
    for mode in MODES:
        for timing in TIMINGS:
            d = sub[(sub["light_mode"] == mode) & (sub["light_timing"] == timing)].sort_values("light_strength")
            ax.plot(d["light_strength"], d["extract_yield_mean"],
                    color=mode_colors[mode], ls=timing_ls[timing],
                    marker=timing_marker[timing], ms=4, lw=1.3,
                    label=mode if timing == "upstream" else None)
    ax.set_xlabel("light strength")
    ax.set_ylabel("extraction yield (extracted / shed)")
    ax.set_title("C. Extraction yield vs strength  (levy_gain = 0.05)")
    ax.set_ylim(0, None)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=6.5, loc="upper left", framealpha=0.92, ncol=2)

    # --- 4. yield vs dorm/colony, points
    ax = fig.add_subplot(3, 2, 4)
    for mode in MODES:
        d = sub[sub["light_mode"] == mode]
        ax.scatter(d["extract_yield_mean"], d["dorm_alive_mean"],
                   c=mode_colors[mode], marker="o", s=28, label=f"{mode} dorm", alpha=0.85)
        ax.scatter(d["extract_yield_mean"], d["p_overt_any"] * 20,  # scale noted in legend
                   c=mode_colors[mode], marker="x", s=28, alpha=0.85)
    ax.axhline(b05["dorm_alive_mean"], color="#444", lw=0.8, alpha=0.6)
    ax.set_xlabel("extraction yield")
    ax.set_ylabel("dormant pool  (and colony rate × 20, × marks)")
    ax.set_title("D. Does yield shrink the leftover pool?")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=6.5, loc="upper right", framealpha=0.92, ncol=2)

    # --- 5. source of extracted cells at s=0.5, g=0.05
    ax = fig.add_subplot(3, 2, 5)
    sub05 = sub[np.isclose(sub["light_strength"], 0.5)].copy()
    mode_short = {"lure": "lure", "tag_magnet": "tag", "flush": "flush",
                  "photoacoustic": "photo", "combined": "comb"}
    time_short = {"upstream": "up", "circulation": "circ", "post_settling": "post"}
    labels, circs, dorms, overts = [], [], [], []
    for mode in MODES:
        for timing in TIMINGS:
            d = sub05[(sub05["light_mode"] == mode) & (sub05["light_timing"] == timing)]
            if d.empty:
                continue
            r = d.iloc[0]
            labels.append(f"{mode_short[mode]}\n{time_short[timing]}")
            circs.append(r["extracted_circ_mean"])
            dorms.append(r["extracted_dorm_mean"])
            overts.append(r["extracted_overt_mean"])
    x = np.arange(len(labels))
    ax.bar(x, circs, 0.78, label="from circulation", color="#4c78a8")
    ax.bar(x, dorms, 0.78, bottom=circs, label="from dormant", color="#f2c14e")
    bot = np.array(circs) + np.array(dorms)
    ax.bar(x, overts, 0.78, bottom=bot, label="from overt colony", color="#e45756")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=6.5)
    ax.set_ylabel("mean cells extracted")
    ax.set_title("E. Preferred exit path at strength 0.5  (levy_gain = 0.05)")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend(fontsize=6.5, loc="upper left", framealpha=0.92)

    # --- 6. 0.05 vs 1.0 and loo / mesh destab
    ax = fig.add_subplot(3, 2, 6)
    # compare combined upstream s=0.5 at two gains vs baselines
    rows_plot = []
    names = []
    for gain, gname in [(0.05, "g 0.05"), (1.0, "g 1.0")]:
        b = base[base["levy_gain"] == gain].iloc[0]
        rows_plot.append((b["p_overt_any"], b["dorm_alive_mean"], b["extract_yield_mean"]))
        names.append(f"no light\n{gname}")
        d = sw[(sw["levy_gain"] == gain) & (sw["light_mode"] == "combined")
               & (sw["light_timing"] == "upstream") & np.isclose(sw["light_strength"], 0.5)]
        if not d.empty:
            r = d.iloc[0]
            rows_plot.append((r["p_overt_any"], r["dorm_alive_mean"], r["extract_yield_mean"]))
            names.append(f"combined up 0.5\n{gname}")
    if not loo.empty:
        for key, lab in [
            ("conjunctive_full", "full loop"),
            ("minus_oasis_on_extract", "minus Oasis\non extract"),
            ("pre_integration", "not integrated"),
            ("extraction_coloring=joint", "joint BFS\nstar"),
        ]:
            d = loo[loo["condition"].str.endswith(key)]
            if d.empty:
                d = loo[loo["condition"].str.contains(key, regex=False)]
            if not d.empty:
                r = d.iloc[0]
                rows_plot.append((r["p_overt_any"], r["dorm_alive_mean"], r["extract_yield_mean"]))
                names.append(lab)
    x = np.arange(len(names))
    w = 0.26
    p_overt = [r[0] for r in rows_plot]
    yields = [r[2] for r in rows_plot]
    dorms20 = [r[1] / 20.0 for r in rows_plot]
    ax.bar(x - w, p_overt, w, label="colony rate", color="#1f3a5f")
    ax.bar(x, dorms20, w, label="dormant / 20", color="#e9c46a")
    ax.bar(x + w, yields, w, label="extract yield", color="#9b2226")
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=6.2)
    ax.set_ylabel("rate  (dormant pool ÷ 20)")
    ax.set_title("F. Calibrated vs full Levy gain, and conjunctive checks")
    ax.set_ylim(0, 0.9)
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend(fontsize=6.5, loc="upper right", framealpha=0.92)

    fig.tight_layout(rect=[0, 0.01, 1, 0.97])
    png = CHARTS / "fig_light_transport.png"
    svg = CHARTS / "fig_light_transport.svg"
    fig.savefig(png, dpi=160)
    fig.savefig(svg)
    # also copy into notes next to the write-up
    fig.savefig(NOTES / "fig_light_transport.png", dpi=160)
    plt.close(fig)
    print("wrote", png, "and", NOTES / "fig_light_transport.png")


if __name__ == "__main__":
    main()
