#!/usr/bin/env python3
"""t96u launch checks: does zipper tolerance / attachment (and an RBC-style deformable seal)
change the repeater, straw or plumbing results? Speculative 2-D point-mass bookkeeping only.

Conjunctive loop per case: Genesis seed -> Nexus register -> PrinciplesGate (oasis_core AdaptOrDie,
as in the redstone runs) admits each burn -> Dictator/Transcriber chronicle -> Levy assess ->
damped recombine of the residual. Recycled: repeater rows (redstone JSON), straw leak sweep
(plumbing JSON). New: pointing-tolerance slider closure (vector geometry on recycled needs) and
straw runs at RBC-halved leak through the existing integrate_plumbed_straw."""
import sys, json, math
from pathlib import Path
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1].parent) + "/magnetic-launch/scripts")
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1].parent) + "/metastasis-native")
import run_plumbing_dynamics as PD
from oro_native import Nexus, Genesis, Transcriber, Dictator, LevyLedger
OUTD = Path(str(__import__("pathlib").Path(__file__).resolve().parents[1])) / "data"; OUTD.mkdir(parents=True, exist_ok=True)
MC = Path(str(__import__("pathlib").Path(__file__).resolve().parents[1].parent)) / "magnetic-launch" / "outputs"
red = json.loads((MC / "redstone_repeater_comparator.json").read_text())
plb = json.loads((MC / "plumbing_dynamics.json").read_text())
G0 = 9.80665; ISP = 450.0
nexus, genesis = Nexus(), Genesis(); tr = Transcriber(); dic = Dictator(tr)
LW = dict(clear=1, detach=7, fail=2, colonize=14, exit=4, extract=4)
ledger = LevyLedger(LW)
nexus.register("genesis", genesis.mirror("launch_zdb", 0))

# A) Repeater + zipper pointing tolerance, slider = sequential correction burns
rows = [x for x in red["repeater_rows"] if x["config"] == "tilt0_333" and x["policy"] == "due_east" and x["fp"] == 0.05 and x["isp_s"] == 450.0]
THETAS = [0.0, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0]
rep = []
for x in rows:
    need, budget = float(x["needed_m_s"]), float(x["dv_budget_m_s"]); ok = bool(x["principles_allowed"])  # recycled oasis_core PrinciplesGate.check result
    for th in THETAS:
        e = 2 * math.sin(math.radians(th) / 2)          # vector error fraction of each burn
        for kmax in (1, 2, 3, 5):
            res, spent, k = need, 0.0, 0
            while k < kmax and res > 1.0 and ok:
                if spent + res > budget: break           # cannot afford the next closing burn
                spent += res; res = res * e; k += 1
                ent = dic.stream(k, {"exit": 1}); ledger.assess(ent)   # each closing tooth = Levy exit pulse
            rep.append(dict(site=x["site_id"], needed_m_s=need, budget_m_s=budget, theta_deg=th, slider_burns_max=kmax,
                            burns_used=k, residual_m_s=res, dv_spent_m_s=spent, locked=bool(res <= 1.0 and ok),
                            principles_allowed=ok))
    nexus.register(x["site_id"], dict(needed=need))
def lock_count(th, k):
    return sum(1 for r in rep if r["theta_deg"] == th and r["slider_burns_max"] == k and r["locked"])
rep_summary = {f"theta{th}_k{k}": lock_count(th, k) for th in THETAS for k in (1, 2, 3, 5)}
th_max_single = {x["site_id"]: math.degrees(2 * math.asin(min(1.0, 1.0 / (2 * float(x["needed_m_s"]))))) for x in rows}

# B) Straw / plumbing: attachment quality a -> joint leak 1-a (recycled sweep) ; RBC seal halves leak (new runs)
rec = {c["label"]: c for c in plb["launch_cases"]}
straw_recycled = [dict(attach=1 - L, leak=L, residual_m_s=rec[f"leak{lab}_evac80_st1"]["residual_m_s"], peak_Teq_K=rec[f"leak{lab}_evac80_st1"]["peak_Teq_K"], source="recycled plumbing_dynamics.json")
                  for L, lab in ((1e-6, "1e-06"), (1e-4, "0.0001"), (1e-3, "0.001"), (1e-2, "0.01"), (0.1, "0.1"), (1.0, "1"))]
dart, site = PD.load_dart_site()
straw_new = []
for L in (0.05, 0.3, 0.5):        # RBC seal 0.5 applied to leak 0.1, 0.6, 1.0
    raw = PD.integrate_plumbed_straw(dart, straw_h_m=80e3, leak_frac=L, n_stages=1, p_push_pa=0.0, evac=True)
    c = PD.close_plumbed(raw, site, az_deg=90.0)
    straw_new.append(dict(leak=L, rbc_equivalent_of_leak=L / 0.5, residual_m_s=c.get("residual_m_s"), peak_Teq_K=c.get("peak_Teq_K"),
                          h_burnout_km=c.get("h_burnout_km"), locked=c.get("locked"), source="new integrate_plumbed_straw"))
    ent = dic.stream(1, {"fail": 1}); ledger.assess(ent)
    print("straw leak", L, c.get("residual_m_s"), c.get("peak_Teq_K"), flush=True)

# C) Coupling: straw exit residual + repeater -> f_p needed (rocket equation, I_sp 450 s)
def fp_need(dv): return 1 - math.exp(-dv / (ISP * G0))
coupling = []
for s in straw_recycled + straw_new:
    r = s["residual_m_s"]
    coupling.append(dict(leak=s["leak"], residual_m_s=r, fp_needed_450s=fp_need(r), fits_fp005=r <= red["budget"]["dv_by_fp_isp"]["isp_450"]["fp_0.05"]))
out = dict(status="speculative bookkeeping; no engineering claim", repeater_rows=rep, repeater_lock_counts=rep_summary,
           n_sites=len(rows), theta_max_single_burn_deg=th_max_single, straw_recycled=straw_recycled, straw_new=straw_new,
           coupling=coupling, levy_total=ledger.total_weight, transcriber_n=len(tr.chronicles), nexus_n=len(nexus.registry),
           gate_source="recycled principles_allowed per site (redstone_repeater_comparator.json)", dna_mrna_wbc_note="DNA proofreading = the same PrinciplesGate admit on each burn; mRNA/WBC have no launch "
           "dynamics in these scripts (Levy decay and patrol do not change delta-v) and were not applied.")
json.dump(out, open(OUTD / "launch_zdb.json", "w"), indent=1)
print(json.dumps(rep_summary)); print({k: round(v, 3) for k, v in th_max_single.items()})
for c in coupling: print(c)
