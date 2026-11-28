#!/usr/bin/env python3
"""t96u cancer checks: zipper / DNA-mRNA / RBC-WBC toggles on the conjunctive native mesh.
Speculative modeling only; structural analogies, no biological claims. 200 runs/condition
(40 seeds x 5 cancers) unless noted; frustrated-vs-pool on a 60-setting subsample."""
import sys, json, time
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1].parent) + "/metastasis-native")
import numpy as np, pandas as pd
from scipy import stats
import run_priority as RP
from oro_native import NEUTRAL
RP._init()
OUT = str(__import__("pathlib").Path(__file__).resolve().parents[1]) + "/data/"
NSEED = 40
ZIP = dict(zipper=True, zip_tolerance=0.5, zip_slider=0.1)
EL = {"zipper": ZIP, "dna": dict(dna=True), "mrna": dict(mrna=True), "rbc": dict(rbc=True), "wbc": dict(wbc=True)}
def comb(drop=None, **kw):
    o = {}
    for k, v in EL.items():
        if k != drop: o.update(v)
    o.update(kw); return o
EXTRA = ["pg_score_mod", "pg_veto", "pg_proof", "zip_skips", "zip_unanchored", "zip_rezips", "dna_reannealed",
         "dna_unzipped_overt", "wbc_patrolled", "wbc_cleared", "rbc_passes", "pressure_mean", "gate_commit", "extracted"]
rows_out = []
def cond(name, exp, gain, ov=None, lever=None, nseed=NSEED):
    o = dict(levy_gain=gain); o.update(ov or {})
    lev = dict(NEUTRAL); lev.update(lever or {})
    rows = RP.run_condition(lev, nseed=nseed, overrides=o)
    s = RP.summarize(rows, name, exp); s["levy_gain"] = gain
    for k in EXTRA: s[k + "_mean"] = float(np.mean([r.get(k, 0) for r in rows]))
    s["pipeline_levy_ok"] = bool(all(r["pipeline_levy_ok"] for r in rows)); s["genesis_closed"] = bool(all(r["genesis_closed"] for r in rows))
    s["consensus_fail_runs"] = int(sum(1 for r in rows if not r["consensus_ok"]))
    s["overrides"] = json.dumps({k: v for k, v in o.items()}); s["lever"] = json.dumps(lever or {})
    rows_out.append(s)
    print(f"{exp:10s} {name:34s} g={gain:<5} col={s['p_overt_any']:.3f} pool={s['dorm_alive_mean']:.3f} "
          f"frust={s['n_frustrated_mean']:.2f} cons={s['consensus_ok']} pg={s['pg_score_mod_mean']:.2f}/{s['pg_veto_mean']:.2f}/{s['pg_proof_mean']:.2f}", flush=True)
    return s
t0 = time.time()
UP = {"thr080": dict(valuation_threshold=0.80), "perm04": dict(organ_perm_scale=0.4)}
POST = {"maint1": dict(dorm_maintenance=1.0), "barrier05": dict(colonization_barrier=0.5)}
for g in (1.0, 0.05):
    cond("baseline", "base", g)
    for k, v in EL.items(): cond(k, "single", g, v)
    cond("wbc_lenient", "single", g, dict(wbc=True, wbc_recognize="non_commit"))
    cond("combined", "combined", g, comb())
    for k in EL: cond(f"combined_minus_{k}", "loo", g, comb(drop=k))
    cond("combined_wbc_lenient", "combined", g, comb(wbc_recognize="non_commit"))
    for tau in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0):
        cond(f"zipper_tau{tau}", "zip_sweep", g, dict(zipper=True, zip_tolerance=tau, zip_slider=0.1))
        cond(f"combined_tau{tau}", "zip_sweep_comb", g, comb(zip_tolerance=tau, dna_proof_thr=tau))
    for nm, ov in {"material0.7": dict(zip_material=0.7), "attach0.9": dict(zip_attach=0.9), "spring0.5": dict(zip_spring=0.5),
                   "spring2": dict(zip_spring=2.0), "tape0.5": dict(zip_tape=0.5), "tape2": dict(zip_tape=2.0),
                   "size1.5": dict(zip_size=1.5), "slider0": dict(zip_slider=0.0), "slider0.5": dict(zip_slider=0.5)}.items():
        o = dict(ZIP); o.update(ov); cond(f"zipper_{nm}", "zip_parts", g, o)
    for nm, lev in {**UP, **POST}.items():
        cond(f"baseline_{nm}", "levers", g, None, lev)
        cond(f"combined_{nm}", "levers", g, comb(), lev)
    cond("mrna_decay0.1", "mrna_sweep", g, dict(mrna=True, mrna_decay=0.1))
    cond("mrna_decay0.95", "mrna_sweep", g, dict(mrna=True, mrna_decay=0.95))
# plumbing rows (recycled settings, gain 0.05) + light combined upstream 0.5
def plumb(leak, seal, timing="upstream", stages=1, magnet=False):
    return dict(plumbing=True, plumbing_strength=0.5, plumbing_leak=leak, plumbing_seal=seal, plumbing_stages=stages,
                plumbing_timing=timing, plumbing_magnet=magnet, plumbing_oasis=True)
PROWS = {"plumb_perfect_up": plumb(0.0, 1.0), "plumb_leak0.6_seal1_up": plumb(0.6, 1.0), "plumb_leak0.3_seal0.5_up": plumb(0.3, 0.5),
         "plumb_leak0.3_seal0_up": plumb(0.3, 0.0), "plumb_leak0.3_post": plumb(0.3, 1.0, "post_settling")}
for nm, ov in PROWS.items():
    cond(nm, "plumbing", 0.05, ov)
    o = dict(ov); o.update(dna=True, dna_reanneal=0.0, dna_proofread=False); cond(nm + "+dna_ledger_only", "plumbing", 0.05, o)
    o = dict(ov); o.update(rbc=True); cond(nm + "+rbc", "plumbing", 0.05, o)
    o = dict(ov); o.update(comb()); cond(nm + "+combined", "plumbing", 0.05, o)
LIGHT = dict(light=True, light_mode="combined", light_strength=0.5, light_timing="upstream", extraction_coloring="preserve")
cond("light_comb_up0.5", "light", 0.05, LIGHT)
o = dict(LIGHT); o.update(rbc=True); cond("light_comb_up0.5+rbc", "light", 0.05, o)
o = dict(LIGHT); o.update(comb()); cond("light_comb_up0.5+combined", "light", 0.05, o)
pd.DataFrame(rows_out).to_csv(OUT + "cancer_summaries.csv", index=False)
# frustrated-vs-pool, 60-setting subsample of the recycled 454
S = pd.read_csv(str(__import__("pathlib").Path(__file__).resolve().parents[1].parent) + "/metastasis-native/data/pre_integration/original_454_settings.csv")
sub = S.iloc[np.linspace(0, len(S) - 1, 60).astype(int)]
corr = {}
for g in (1.0, 0.05):
    for lab, ov in (("baseline", {}), ("combined", comb())):
        fr, po = [], []
        for _, row in sub.iterrows():
            lev = RP.lever_from_row(row); o = dict(levy_gain=g); o.update(ov)
            rr = RP.run_condition(lev, nseed=8, overrides=o)
            fr.append(np.mean([r["n_frustrated"] for r in rr])); po.append(np.mean([r["dorm_alive"] for r in rr]))
        rho, p = stats.spearmanr(fr, po)
        corr[f"{lab}_g{g}"] = dict(spearman=float(rho), p=float(p), n_settings=60, runs_per_setting=40)
        print("frust-vs-pool", lab, g, rho, flush=True)
json.dump(corr, open(OUT + "frustrated_vs_pool.json", "w"), indent=1)
print("DONE", round(time.time() - t0), "s")
