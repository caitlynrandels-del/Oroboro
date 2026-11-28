#!/usr/bin/env python3
import json, hashlib, datetime
import numpy as np, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
B = str(__import__("pathlib").Path(__file__).resolve().parents[1]) + "/"
d = pd.read_csv(B + "data/cancer_summaries.csv"); L = json.load(open(B + "data/launch_zdb.json"))
fvp = json.load(open(B + "data/frustrated_vs_pool.json")); sl = json.load(open(B + "data/slider_followup.json"))
def row(c, g): r = d[(d.condition == c) & (d.levy_gain == g)].iloc[0]; return r
fig, ax = plt.subplots(2, 2, figsize=(12, 8.2))
names = ["baseline", "zipper", "dna", "mrna", "rbc", "wbc", "wbc_lenient", "combined", "combined_minus_zipper", "combined_minus_dna",
         "combined_minus_mrna", "combined_minus_rbc", "combined_minus_wbc", "combined_wbc_lenient"]
short = ["base", "zip", "dna", "mrna", "rbc", "wbc", "wbc-len", "COMB", "-zip", "-dna", "-mrna", "-rbc", "-wbc", "COMB+wbc-len"]
x = np.arange(len(names)); a = ax[0, 0]; a2 = a.twinx()
for i, (g, c) in enumerate(((1.0, "#1f77b4"), (0.05, "#d62728"))):
    a.bar(x + (i - .5) * .38, [row(n, g).p_overt_any for n in names], .38, color=c, alpha=.75, label=f"colony rate, gain {g}")
    a2.plot(x, [row(n, g).dorm_alive_mean for n in names], "o-" if g == 1 else "s--", color=c, ms=4, label=f"dormant pool, gain {g}")
a.axhline(.217, color="k", lw=.8, ls=":"); a.text(-.5, .222, "21.7% / 10.38 targets (dotted)", fontsize=6.5)
a2.axhline(10.38, color="gray", lw=.8, ls=":")
a.set_xticks(x); a.set_xticklabels(short, rotation=55, fontsize=7); a.set_ylabel("P(any overt colony)"); a2.set_ylabel("mean dormant pool")
a.set_title("A. Single toggles, combined, leave-one-out (200 runs each)", fontsize=9); a.set_ylim(0, .32); a2.set_ylim(0, 16); a.legend(loc="upper left", fontsize=6.5, ncol=2); a2.legend(loc="upper right", fontsize=6.5, ncol=1, bbox_to_anchor=(1, .9))
a = ax[0, 1]; a2 = a.twinx(); taus = [.1, .2, .3, .4, .5, .6, .8, 1.0]
for g, c in ((1.0, "#1f77b4"), (0.05, "#d62728")):
    a.plot(taus, [row(f"zipper_tau{t}", g).p_overt_any for t in taus], "o-", color=c, label=f"zipper only, g{g}")
    a.plot(taus, [row(f"combined_tau{t}", g).p_overt_any for t in taus], "s--", color=c, label=f"combined, g{g}")
    a2.plot(taus, [row(f"combined_tau{t}", g).pg_proof_mean for t in taus], ":", color=c, alpha=.6)
a.set_xlabel("zipper tolerance τ (teeth skip if mismatch > τ)"); a.set_ylabel("P(any overt colony)"); a2.set_ylabel("new proofread holds / run (dotted)")
a.set_title("B. Zipper tolerance sweep; original PrinciplesGate rules fired 0×", fontsize=9); a.legend(fontsize=6.5)
a = ax[1, 0]; th = [0.0, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0]
for k, m in ((1, "o-"), (2, "s-"), (3, "^-"), (5, "d--")):
    a.plot(th, [L["repeater_lock_counts"][f"theta{t}_k{k}"] for t in th], m, label=f"slider: ≤{k} correction burn(s)")
a.set_xscale("symlog", linthresh=0.1); a.set_xlabel("repeater pointing tolerance θ (deg)"); a.set_ylabel(f"sites locked (of {L['n_sites']}; equator gate-blocked; f_p 0.05)")
a.set_title("C. Launch repeater: teeth = pointing tolerance, slider = re-burns", fontsize=9); a.legend(fontsize=7)
a = ax[1, 1]; sr = sorted(L["straw_recycled"], key=lambda s: s["leak"]); sn = L["straw_new"]
a.plot([s["leak"] for s in sr], [s["residual_m_s"] for s in sr], "o-", label="recycled leak sweep (attach = 1 − leak)")
a.plot([s["leak"] for s in sn], [s["residual_m_s"] for s in sn], "s", color="C3", label="new runs at RBC-halved leak")
a.axhline(226.36, color="k", ls=":", lw=.8); a.text(2e-6, 232, "f_p 0.05 repeater budget 226 m/s", fontsize=7)
a.set_xscale("log"); a.set_ylim(0, 720); a.set_xlabel("straw joint leak fraction"); a.set_ylabel("residual Δv to LEO (m/s)")
a.set_title("D. Straw attachment/seal: residual floor ≈595 m/s", fontsize=9); a.legend(fontsize=7, loc="lower right")
fig.suptitle("Zipper / DNA-mRNA / RBC-WBC toggles on Oroboro (speculative, structural analogy only)", fontsize=11)
fig.tight_layout(); fig.savefig(B + "figures/zipper_dna_blood_figure.svg")
def pick(c, g):
    r = row(c, g); return {k: (float(r[k]) if not isinstance(r[k], (bool, np.bool_)) else bool(r[k])) for k in
        ["p_overt_any", "dorm_alive_mean", "n_frustrated_mean", "consensus_fail_runs", "pg_score_mod_mean", "pg_veto_mean", "pg_proof_mean",
         "zip_skips_mean", "dna_reannealed_mean", "wbc_patrolled_mean", "wbc_cleared_mean", "dna_unzipped_overt_mean"]}
J = dict(task="t96u", status="speculative structural analogy; no clinical/biological/engineering claim; no invented data",
    generated=datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    code=dict(modified=str(__import__("pathlib").Path(__file__).resolve().parents[1].parent) + "/metastasis-native/oro_native.py",
              sha1=hashlib.sha1(open(str(__import__("pathlib").Path(__file__).resolve().parents[1].parent) + "/metastasis-native/oro_native.py", "rb").read()).hexdigest(),
              backup="git history (version before this commit)", toggles_off_bit_identical="90/90 runs (sigcheck.py)"),
    mapping=dict(zipper=dict(teeth="NaCl polarity edges", slider="Oasis re-test of skipped teeth in dormant block", tolerance="teeth skip if |fit-perm|*size+(1-material)*U > tau",
                 tape="damper alpha/tape", spring="levy_gain*spring", attachment="seating anchor (cells stay in circulation if unanchored)"),
                 dna=dict(pairing="polarity pairs", unzip_reanneal="delta-reconciliation reseat of frustrated occupants + ledger of overt cells unzipped to circulation",
                          proofreading="NEW rule inside PrinciplesGate: hold commit if mismatch > threshold"),
                 mrna="Levy EMA uses mrna_decay (transient) vs Nexus record (persistent)", rbc="plumbing leak*(1-seal), hop+deform*(1-hop)",
                 wbc="dormant patrol through Oasis gate; recycle (strict) or non-commit (lenient) -> cleared"),
    cancer={f"g{g}": {c: pick(c, g) for c in names} for g in (1.0, 0.05)},
    tau_sweep={f"g{g}": {f"tau{t}": dict(zipper=pick(f"zipper_tau{t}", g)["p_overt_any"], combined=pick(f"combined_tau{t}", g)["p_overt_any"],
               proof=pick(f"combined_tau{t}", g)["pg_proof_mean"]) for t in taus} for g in (1.0, 0.05)},
    levers={f"g{g}": {c: pick(c, g) for c in ["baseline_thr080", "combined_thr080", "baseline_perm04", "combined_perm04", "baseline_maint1",
            "combined_maint1", "baseline_barrier05", "combined_barrier05"]} for g in (1.0, 0.05)},
    plumbing_consensus={c: pick(c, 0.05) for c in d[d.condition.str.startswith("plumb")].condition},
    frustrated_vs_pool=fvp, slider_followup=sl,
    launch=dict(repeater_lock_counts=L["repeater_lock_counts"], n_sites=L["n_sites"], theta_max_single_burn_deg=L["theta_max_single_burn_deg"],
                straw_recycled=L["straw_recycled"], straw_new=L["straw_new"], coupling=L["coupling"], note=L["dna_mrna_wbc_note"]),
    open_items=dict(calibration="not closed: best g0.05 colony 0.195 (dna) vs 0.175 baseline, pool ~10.2; within binomial SE ~0.027",
                    principles_gate="original 4 rules: 0 score mods, 0 vetoes in every condition; only the newly added proofread rule fires",
                    consensus_4_rows="closed as bookkeeping: DNA unzip ledger books OVERT->circulation leaks; 1/200 failing run per row -> 0"),
    files=dict(cancer_csv=B + "data/cancer_summaries.csv", launch_json=B + "data/launch_zdb.json", figure=B + "zipper_dna_blood_figure.png"))
json.dump(J, open(B + "zipper_dna_blood.json", "w"), indent=1, default=float)
print("ok")
