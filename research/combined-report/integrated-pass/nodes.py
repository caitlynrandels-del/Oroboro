# Node table for the integrated Oroboro pass. Every entry in "vals" is an exact
# substring of its source file (after stripping markdown ** * ` and collapsing
# whitespace); verify_nodes() enforces this. "text" is the page phrasing.
# kind -> native Levy kind:  colonize=settled result, detach=modification,
# fail=failed variant/falsified prediction, exit=superseded/corrected figure,
# extract=open item, clear=context/constant.
R = "/workspace/oroboro-research/"
P1, P2, P3, P4 = (R+"combined_report/part%d.md" % i for i in (1, 2, 3, 4))
RED = R+"magnetic_launch_case_study/Redstone_Repeater_Comparator_Addendum.md"
LS = R+"magnetic_launch_case_study/Light_Sail_Push_Addendum.md"
GKS = R+"magnetic_launch_case_study/Guidance_Kite_Line_Straw_Addendum.md"
FUR = R+"magnetic_launch_case_study/Fur_Fabric_Adaptive_Addendum.md"
PLB = R+"magnetic_launch_case_study/Plumbing_Dynamics_Addendum.md"
GEO = R+"magnetic_launch_case_study/Geography_Launch_Sites_Addendum.md"
GS = R+"magnetic_launch_case_study/Magnetic_Launch_GoalSeek_Continuation.md"
CD = R+"cross_domain/Oroboro_CrossDomain_Comparison.md"
LT = R+"metastasis_native/notes/Light_Transport_Extraction.md"
NM = R+"metastasis_native/notes/Native_Mesh_Restart_HeatTrace.md"
LOG = R+"metastasis_native/outputs/run_integrated.log"
PJ = R+"metastasis_native/params.json"
IP = R+"combined_report/integrated_pass/"
GH = IP+"github_state.json"
PC = IP+"evidence_plumbing_consensus.txt"
CORE = "/tmp/verify_oroboro-relay/oroboro-core.js"
SWIFT = "/tmp/verify_oroboro-relay/swift/Sources/OroboroRelay/OroboroRelayApp.swift"

N = []
def n(id, dom, kind, text, vals, src, lev=(), t=0):
    N.append(dict(id=id, domain=dom, kind=kind, text=text, vals=list(vals), src=src, levers=list(lev), t=t))

# ---------------- systems / wiring ----------------
n("S.pipeline", "sys", "detach", "Conjunctive loop per step: Genesis → state reduction → Oasis (commit ≥0.65 / buffer ≥0.325 / recycle) → PrinciplesGate/AdaptOrDie → NaCl polarity mesh → Dictator → Transcriber → Levy → Nexus → damped delta reconciliation → homeostasis → Genesis.",
  ["Genesis → state reduction → Oasis salience gate → PrinciplesGate → NaCl polarity-mesh consensus → Dictator → Transcriber → Levy → Nexus → damped delta reconciliation"], P1)
n("S.oasis", "sys", "clear", "Oasis S=0.30·nov+0.25·tens+0.25·coh+0.20·res.", ["S = 0.30·novelty + 0.25·tension + 0.25·coherence + 0.20·resonance", "Commit at ≥ 0.65, buffer at ≥ 0.325"], P1, ["admission"])
n("S.levyw", "sys", "clear", "Levy weights (bookkeeping): clear 1, detach 7, fail 2, exit 4, colonize 14; relay: critical 10/other 1.", ["clear 1, detach 7, fail 2, exit 4, colonize 14"], P1)
n("S.homeo", "sys", "clear", "Homeostasis rest load 40, rest bump 0.2; damper α 0.35, gain 0.08.", ["Rest load 40 and rest bump 0.2", "alpha 0.35, gain 0.08"], P1+"|"+GH)
n("S.systems17", "repo", "colonize", "SYSTEMS.md on Oroboro main indexes 17 systems with code links (pipeline, Genesis, Nexus, Oasis, PrinciplesGate, NaCl mesh, Dictator, Transcriber, Levy, damper, delta, isolate/recombine, dream-catcher, self-repairing niche, sponge, smart magnets, homeostasis).", ["indexes 17 systems"], GH)
n("S.audit_tree", "sys", "detach", "Audit: public NaCl mesh was a 4-node tree (no cycles); reconcile() only logged; oroboro-core.js L124 delta = Math.random()*0.1.", ["four-node *tree* with no cycles", "line 124 drew `delta: Math.random() * 0.1`"], P2)
n("S.delta_fix", "sys", "colonize", "Relay fix (cc77063): random delta replaced by deterministic delta vs Nexus + OroboroPipeline; node test passes.", ["Replaces the Math.random()*0.1 delta stub in oroboro-core.js", "pipeline tests passed"], GH)
n("S.cd_stub_claim", "sys", "exit", "Cross-domain note (pre-fix) said oroboro-core.js delta still a Math.random stub.", ["Delta reconciliation in `oroboro-core.js` is still a `Math.random` stub"], CD)
n("S.nonconj", "sys", "fail", "Not conjunctive: Goldilocks, strings, weave, goal-seek (isolated blocks); geography & tilt (no component calls); first native restart (Dictator/Transcriber/Levy ledger-only, no PrinciplesGate, damper silent).",
  ["used components as separate blocks", "called no Oroboro component", "PrinciplesGate was absent, and the damper never engaged"], P1)
n("S.conj", "sys", "colonize", "Conjunctive: every launch run from redstone on; cancer model integrated=True by default.", ["From the redstone run onward, every launch run used one loop", "conjunctive by default (`integrated=True`)"], P1)
n("S.sponge", "sys", "clear", "Sponge: documented (code in epilepsy-sim/cascade repos) but not used in these studies.", ["Documented in Caitlyn's notes but not used in any study here"], P1)
n("S.workspace", "sys", "clear", "Dream-catcher/odd-loop code lives in the research workspace (now Oroboro research/), not the original public repos.", ["The dream-catcher and odd-loop pieces exist in the project workspace, not in the original public repos"], P4)

# ---------------- cancer ----------------
n("C.sweep", "cancer", "colonize", "1.21 M-run sweep (484 cond./454 unique × 2,500) reproduced exactly; baseline p(colony) 21.7% (20.2–23.4), pool 10.38 (10.25–10.51), 94.7% preferred organ.",
  ["All 484 estimates were reproduced exactly", "21.7% of runs colonize (95% CI 20.2–23.4%)", "10.38 cells (10.25–10.51)", "94.7% of colonies"], P2, ["admission"])
n("C.switch", "cancer", "colonize", "Elimination switch: threshold x₅₀ 0.799, x₉₀ 0.854; permissiveness x₉₀ ×0.219; prostate-like stricter (0.872 vs 0.842).", ["50% at 0.799", "90% at 0.854", "×0.219", "0.872 vs 0.842"], P2, ["admission"])
n("C.onset", "cancer", "colonize", "Onset half-time: single upstream 15–17 mo, combined 57 mo, dormant clearance effective to 97 mo.", ["by months 15–17", "month 57", "month 97"], P2, ["admission"])
n("C.interact", "cancer", "clear", "Interactions mostly independent (74/98 within ±10%).", ["74 of 98 within ±10%"], P2)
n("C.native", "cancer", "detach", "Native polarity-mesh restart: 49 nodes, 89 edges, 32 frustrated (dream-catcher niche: 8-hoop + hub + spokes on inverse-Epcot bowl, return edges).", ["49 nodes and 89 edges, 32 of them frustrated", "an 8-node hoop, a hub and spokes"], P2)
n("C.native_base", "cancer", "exit", "Native baseline 18.0% / 10.355 (vs orig 21.72/10.380).", ["18.00%", "10.355", "21.72% colonies and a pool of 10.380"], P2)
n("C.tree", "cancer", "colonize", "Tree-niche ablation → 20.6%, pool 10.38: loops tax colonization, don't set pool.", ["raises colonies to 20.6% while the pool stays at 10.38", "Loops tax colonization; they do not set pool size."], P2, ["loops"])
n("C.frust819", "cancer", "exit", "Frustrated count vs pool Spearman −0.819 (−0.863, −0.765), opposite of prediction; shuffle +0.007.", ["−0.819 (−0.863, −0.765)", "+0.007"], P2, ["loops"])
n("C.upstream", "cancer", "colonize", "Only upstream levers shrink both: threshold 0.80 → 0.000/0.550; permissiveness ×0.4 → 0.000/2.222. Post-settling (maintenance, barrier) clears colonies, leaves ~10.5.",
  ["Valuation threshold 0.80 | 0.001 | 0.000 | 0.530 | 0.550", "Organ permissiveness ×0.4 | 0.002 | 0.000 | 2.275 | 2.222", "leave the ~10.5-cell pool"], P2, ["admission"])
n("C.tilt", "cancer", "colonize", "Circulation tilt 0/0.3/0.6 → colonies 0.165/0.348/0.438, pool 10.40/13.22/15.19.", ["0.165, 0.348 and 0.438", "10.40, 13.22 and 15.19"], P2, ["tilt"])
n("C.damper_silent", "cancer", "fail", "First restart: damper silent (occupancy never reached rest load 40).", ["the damper was silent"], P2)
n("C.wiring", "cancer", "detach", "Conjunctive wiring (27 Nov): Dictator.stream → Transcriber in-step; LevyLedger pulse → damper (levy_gain); Nexus builds next month; PrinciplesGate after Oasis; monthly Genesis closure; integrated=False reproduces pre-integration exactly.",
  ["`Dictator.stream()` now feeds the Transcriber inside each step.", "`integrated=False` reproduces the pre-integration run exactly."], P2)
n("C.gain1", "cancer", "colonize", "Recalibration (1,000 runs): pre 0.180/10.36; levy_gain 0.05 0.175/10.09; 0.5 0.134/8.01; 1.0 (params default) 0.091/6.36.",
  ["Pre-integration | 0.180 | 10.36", "levy_gain 0.05 (closest to calibration targets 0.217 / 10.38) | 0.175 | 10.09", "levy_gain 0.5 | 0.134 | 8.01", "levy_gain 1.0 (working baseline) | 0.091 | 6.36"], P2, ["levy"])
n("C.loo", "cancer", "colonize", "LOO @1.0: full 0.096/6.37; −Levy feedback or −damper → 0.178/10.41 (load-bearing); −PrinciplesGate unchanged; −adaptive niche 0.080/6.37; tree 0.112/6.36.",
  ["The full loop gives 0.096 and 6.37", "returns 0.178 and 10.41", "Removing PrinciplesGate changes nothing", "0.080 and 6.37", "0.112 and 6.36"], P2, ["levy"])
n("C.check200", "cancer", "colonize", "200-run conjunctive check: damper mean ~0.031, peak ~0.138; commits 16.9→10.6/run; pool 10.480→6.300, colonies 0.175→0.135; post-settling 6.41; tilt still worsens (0.135/0.200/0.295).",
  ["about 0.031 and peak about 0.138", "16.9 to 10.6", "10.480 to 6.300", "0.175 to 0.135", "(6.41)", "0.135, 0.200 and 0.295"], P2, ["admission", "tilt"])
n("C.frust829", "cancer", "colonize", "Frustrated-vs-pool sign survives wiring: −0.829 conjunctive (454 settings), pool rank ρ=0.988.", ["−0.829 conjunctive vs −0.819 before", "ρ = 0.988"], P2, ["loops"])
n("C.light_design", "cancer", "detach", "Light as directed transport: filter+extract nodes; lure / tag+magnet / flush / light+sound / combined × upstream, circulation, post-settling × 0.2/0.5/0.8; 200 runs each; Oasis/PrinciplesGate-gated; off by default, bit-identical when off.",
  ["Two nodes were added, `filter` and `extract`", "Light is off by default"], P2, ["admission", "exit_gate"])
n("C.light45", "cancer", "colonize", "45/45 light conditions shrink both (vs 17.5%/10.22); combined upstream 0.5 → 0.0%/0.67 (yield 15.1%); 0.8 → pool 0.045; upstream most efficient, post-settling leaves most.",
  ["45/45 conditions shrank both outcomes", "Combined, upstream, 0.5 | 0.0% | 0.67 | 15.1%", "Combined, upstream, 0.8 | 0.0% | 0.045 | 27.7%"], P2, ["admission", "exit_gate"])
n("C.light_oasis", "cancer", "colonize", "Oasis load-bearing on the exit: skip Oasis → yield 77.2% (ungated drain); threshold 0.80 starves exit (0.7%).", ["15.1% to 77.2%", "(yield 0.7%)"], P2, ["admission", "exit_gate"])
n("C.light_r", "cancer", "fail", "Frustrated-vs-pool link does not survive the light exit (Spearman 0.09); ring stays locked.", ["Spearman 0.09, CI −0.25 to 0.44"], P2, ["loops"])
n("C.plumb", "cancer", "colonize", "Plumbing (Oasis = valve): perfect seal upstream p(overt) 0.175→0.000, pool 10.215→1.270, yield 0.132 (valve blocks 253.8/285.5).",
  ["Perfect seal, upstream | 0.000 | 1.270 | 0.132", "blocked 253.8 of 285.5 attempts"], P2, ["admission", "exit_gate"])
n("C.plumb_leak", "cancer", "colonize", "Leak 0.3 → 6.33 leaked (5.88 back to circulation), pool 1.415; 16 stages 0.38 leaked; smart-magnet hold 2.97; post-settling 0.010/1.950; no-Oasis ablation yield 0.684.",
  ["Leak 0.3, upstream | 0.000 | 1.415 | 0.116 | 6.33", "Leak 0.3, 16 stages | 0.000 | 1.315 | 0.131 | 0.38", "Leak 0.3, smart-magnet hold | 0.000 | 1.335 | 0.125 | 2.97", "Perfect seal, post-settling | 0.010 | 1.950", "0.684"], P2, ["exit_gate"])
n("C.plumb_claim", "cancer", "exit", "Plumbing addendum text: consensus held on every condition.", ["Census, levy, consensus, and inversion checks held on every condition."], PLB)
n("C.plumb_cons", "cancer", "colonize", "consensus_ok = False on 4 plumbing rows (leak 0.6/seal 1 up; leak 0.3/seal 0.5 up; leak 0.3/seal 0 up; leak 0.3 post); census/Levy/inversion pass.",
  ["plumb_leak0.6_seal1_up consensus_ok=False", "plumb_leak0.3_seal0.5_up consensus_ok=False", "plumb_leak0.3_seal0_up consensus_ok=False", "plumb_leak0.3_post consensus_ok=False", "consensus_ok False count = 4"], PC)

# ---------------- launch ----------------
n("L.metric", "launch", "clear", "Target 7,788.5 m/s (200 km circ). Metric: vacuum two-burn residual; lock = residual ≤1 m/s & perigee ≥100 km (redstone) / ≥200 km (later).", ["7,788.5 m/s", "at most 1 m/s", "100 km (redstone note) or 200 km (all later notes)"], P1)
n("L.track", "launch", "clear", "17,000 mph at 3 g needs 981.6 km rail (1,963 km at 50% duty); Goldilocks 1,000–3,000 mph = 5.74–17.22% of v_circ.", ["981.6 km", "1,963 km with 50% duty", "5.74%, 11.48% and 17.22%"], P3)
n("L.sealevel", "launch", "fail", "Sea-level drag 13.5 g at 3,000 mph; best sea-level apogee 34.2 km.", ["13.5 g at 3,000 mph", "34.2 km"], P3, ["drag"])
n("L.climb", "launch", "colonize", "Climbing 80° rail: release ~182 km, apogee 278 km; convex geometry stalls (2.07 km).", ["releasing at about 182 km with apogees of 278 and 277 km", "2.07 km"], P3)
n("L.damp", "launch", "colonize", "Dampers meter peaks (0.0202 of 10 Hz pulse), don't change Δv.", ["0.0202 of a 10 Hz pulse", "Dampers meter peaks; they do not change the Δv budget."], P3)
n("L.strings", "launch", "fail", "Strings: pulse train chirped (ratio 2.118); no single uniform mode fits.", ["ratio of 2.118"], P3)
n("L.weave", "launch", "detach", "Dream-catcher weave: tree → 101 loops, 59 frustrated, Fiedler 0.122→0.177 (skeleton only; no video).", ["101", "59", "0.122 to 0.177", "No video frames or stills are reproduced anywhere"], P3, ["loops"])
n("L.dart407", "launch", "colonize", "Goal-seek best no-stage: 12.56 kg evac-tube hollow dart 407 m/s (held pusher, 80 km, 5°); 5° tilt 431; 0° 333 (no climb).", ["407 m/s, no stage.", "431 m/s, no stage.", "A 0° release leaves 333 m/s"], P3, ["release"])
n("L.256", "launch", "exit", "Staged residual 256 m/s (incomplete 900 s coast).", ["256 m/s, staged: invalid."], P3)
n("L.1148", "launch", "colonize", "True Kepler two-burn residual of the staged state: 1,148 m/s (apogee 5,436 km, perigee underground).", ["1,148 m/s", "apogee 5,436 km"], P3)
n("L.autopilot", "launch", "fail", "Onboard conjunctive Oroboro autopilot hurt: apogee 115.1→50.2 km; staged residual 325→744 m/s (n=24).", ["115.1 to 50.2 km", "from 325 to 744 m/s"], P3)
n("L.heat", "launch", "fail", "Heat-driven regrowth only in a narrow window (PLA 280 s); ablates ~3,700 °C at 17,000 mph.", ["280 s", "about 3,700 °C"], P3, ["heat"])
n("L.geo", "launch", "colonize", "Geography (boost 465.1·cos lat): 0° exit due-east Baikonur 66, Māhia 103, Mt Charleston 118, LAS 119, KSC 151, Kourou 206, Chimborazo 208 m/s; elevation irrelevant at 80 km mouth.",
  ["465.1·cos(lat)", "Baikonur 66, Māhia 103, Mount Charleston 118, Las Vegas 119", "Cape Canaveral 151", "Kourou 206", "Chimborazo 208 m/s", "Elevation does not change the residual at an 80 km mouth"], P3, ["admission", "release"])
n("L.equator", "launch", "fail", "Equator does not close the gap: 5° residual 375, dart 398 (boost overshoots).", ["375 m/s and the evac dart 398 m/s"], P3, ["release"])
n("L.planechg", "launch", "clear", "LAS → equatorial plane change ≈4.82 km/s.", ["4.82 km/s"], P3)
n("L.repeater", "launch", "colonize", "Redstone repeater = paid impulsive late two-burn (rocket eq., I_sp 450 s): f_p 0.05/0.30/0.85 → 226/1,574/8,372 m/s. f_p 0.05 locks the 0° exit at all 14 sites (Baikonur 0.015, LAS 0.027); f_p 0.30 locks every due-east setup incl. staged.",
  ["226, 1,574 and 8,372 m/s", "locks all 14 real sites on the 0°/80 km exit", "Baikonur needing only 0.015 and Las Vegas 0.027", "locks every due-east setup"], P3, ["late_burn"])
n("L.rep_limits", "launch", "fail", "Repeater f_p 0.05 does not circularize 5° darts (338→112); 407 m/s gap needs 1.11 kg > 0.63 kg filament budget.", ["338 → 112 m/s", "1.11 kg of the 12.56 kg dart", "0.63 kg filament budget"], P3, ["late_burn"])
n("L.comparator", "launch", "fail", "Comparator never beats best azimuth (0/14). Mean over 14 sites, due E / comparator / best az: 0° 153/336/42; 5° dart 372/409/328; staged 1,507/1,144/834.",
  ["0 of 14", "0° / 80 km | 153 m/s | 336 m/s (climb lost) | 42 m/s", "5° evac dart | 372 | 409 | 328", "Staged (true 1,148) | 1,507 | 1,144 | 834"], P3, ["release"])
n("L.bestaz", "launch", "colonize", "Best azimuth 40–65° off east: Baikonur 37, LAS 38 m/s; AdaptOrDie blocked only the zero-coordinate idealized equator.", ["40–65° off due east gives 37 m/s at Baikonur and 38 m/s at Las Vegas", "AdaptOrDie blocked only the zero-coordinate"], P3, ["release"])
n("L.notrack", "launch", "fail", "No-track pad ascent 0/240: f_p 0.85 leaves 661 (Kourou)/708 (LAS)/756 (Baikonur)/631 m/s, q 384–406 kPa, ~5,160–5,240 K; binding = thick-air drag/heating.",
  ["No track (240 runs, 0 locks)", "661 m/s (Kourou), 708 (Las Vegas), 756 (Baikonur) and 631 (Mauna Kea)", "5,160–5,240 K", "thick-air drag and heating"], P3, ["drag", "heat"])
n("L.sail", "launch", "fail", "Light sail 0/864 (≤100 GW): drag ~90 kN @80 km vs 63 N photon @10 GW; LOS ~134 s; sails 2,176–4,696 K; best staged 682→519 (12,990 GJ), no-track 661→514; second downrange laser not modeled.",
  ["0 of 864", "about 90 kN at 80 km", "63 N of photon force at 10 GW", "about 134 s", "2,176 K at 10 GW and 4,696 K at 100 GW", "682 m/s (coast) to 519 m/s, using 12,990 GJ", "661 to 514 m/s", "A second, downrange laser was not modeled."], P3, ["drag", "heat"])
n("L.kite", "launch", "fail", "Kite 10 m² reefed: 1,333 m/s (brake).", ["Kite, 10 m², reefed | 1,333"], P3, ["drag"])
n("L.line", "launch", "fail", "Fishing line 500 m from 60 km: 2,791 m/s; from pad 7,551.", ["Line, 500 m, from 60 km | 2,791", "Line, 500 m, from pad | 7,551"], P3, ["drag"])
n("L.lane", "launch", "fail", "Gated lane-keeping 644 m/s (871 commits, 0.01 s thrust-cosine waste).", ["Gated lane-keeping | 644", "871 commits"], P3, ["drag"])
n("L.magnet", "launch", "fail", "Smart magnet vs Earth field: F≈1.4×10⁻⁸ N (661 m/s unchanged); magnetorquer gives torque 0.030 N·m.", ["Force ≈ 1.4×10⁻⁸ N", "0.030 N·m"], P3)
n("L.straw", "launch", "fail", "Evacuated straw 595 m/s (0/46 guidance); vacuum to 7,788 m/s at T/W 3 needs 1,031 km channel (1.34× 767.6 km tube).", ["Evacuated straw | 595", "0 of 46", "1,031 km of channel, 1.34× the recycled 767.6 km"], P3, ["release"])
n("L.fur", "launch", "fail", "Adaptive fur/fabric (Waggoner–de Goes-form remesh, Oroboro-gated): kite 1,344; line adaptive 1,361 (vs fixed 2,378 in this integrator); straw liner 595; sail 554 (3,378 K); refining wrinkled cloth locks the wrinkle (~0.74 vs ~0.63 m).",
  ["Kite, adaptive gated | 1,344", "Line, fixed (this integrator) | 2,378", "Line, adaptive gated | 1,361", "Sail, adaptive gated | 554", "(3,378 K)", "~0.74 m vs ~0.63 m"], P3, ["drag"])
n("L.fur_line_note", "launch", "clear", "Line 2,791 (guidance) vs 2,378 (fur integrator): same failure mode, different projected-area bookkeeping.", ["same failure mode, a slightly different projected-area bookkeeping"], FUR)
n("L.plumb", "launch", "fail", "Plumbing straw 0/49: leak 0 595.0; leak 0.1 595.5 (heat 2,571 K first); leak 1 = no-track 661.3; 0.1 bar late 666, pad 791; 1 bar 2,934; longer vacuum unchanged (burnout at 109 km).",
  ["Evacuated to 80 km, leak 0 | 595.0 m/s", "Leak 0.1 | 595.5 | 502 km | 2,571 K", "Leak 1, or open air | 661.3", "0.1 bar, late valve | 666", "0.1 bar, from the pad | 791", "1 bar | 2,934", "0 of 49 locked", "burning at 109 km"], P3, ["release", "heat"])

# ---------------- cross-domain ----------------
n("X.door", "cross", "colonize", "Common rule: leftovers are set at admission/release; downstream correction rarely empties them.", ["What is left over is mostly decided at the door."], P4, ["admission", "release"])
n("X.lateburn", "cross", "colonize", "Only the small paid late burn closed the launch gap; nothing else locked (best leftovers ~514–661 m/s on the no-track baseline).", ["The small late burn is the only thing that closed the launch gap.", "between about 514 and 661 m/s"], P4, ["late_burn"])
n("X.gate", "cross", "colonize", "The gate is load-bearing both ways: Oasis keeps the cancer exit from an ungated drain (15% vs 77%); the comparator form of a gate is wrong when the side pulse makes the craft climb.", ["The gate is load-bearing, in both directions.", "(15% vs 77% yield)"], P4, ["exit_gate", "admission"])
n("X.tilt", "cross", "colonize", "Same name, opposite sign: 5° release tilt helps launch; circulation tilt doubles colonies.", ["The same name can have opposite effects."], P4, ["tilt"])
n("X.geo", "cross", "colonize", "Geography plays the role of organ permissiveness (an admission condition, not a free subtraction).", ["Geography plays the part of organ permissiveness."], P4, ["admission"])
n("X.loops", "cross", "colonize", "Loops are not the reservoir.", ["Loops are not the reservoir."], P4, ["loops"])
n("X.conj", "cross", "colonize", "Wiring together is not automatically better: lowers cancer leftovers without flipping findings; the onboard conjunctive launch loop hurt insertion.", ["Wiring things together is not automatically better; it has to be tested."], P4, ["levy"])
n("X.oasis_truth", "cross", "fail", "Oasis committed true and false closure claims alike at 0.65: it routes, it doesn't verify.", ["It committed true and false closure claims alike at exactly 0.65"], P4)

# ---------------- open items (status) ----------------
n("O.calib", "open", "extract", "Calibration: params.json levy_gain = 1.0 (9.1%/6.36); calibration-best 0.05 (17.5%/10.09) used by the light and plumbing runs but never set as default; remaining 17.5 vs 21.7 gap tracks the loop tax (tree 20.6%).",
  ['"levy_gain": 1.0', "USING levy_gain 1.0 (calibration-best 0.05 )"], PJ+"|"+LOG+"|"+P2+"|"+P1, ["levy"])
n("O.pgate", "open", "extract", "PrinciplesGate: wired after Oasis; LOO −PrinciplesGate identical at both gains (0.096/6.366 @1.0; 0.176/10.138 @0.05) — H never <0.3, frustration ≤0.36.",
  ["LOO baseline minus_principles_gate 0.096 6.366", "LOO baseline minus_principles_gate 0.176 10.138"], LOG+"|"+R+"metastasis_native/outputs/run_integrated_levy_gain_0.05.log|"+P2, ["admission"])
n("O.epi", "open", "extract", "epilepsy-sim @2be4eac: audit only — Nexus→salience/homeostasis loop real; Levy/Transcriber/Genesis ledger-only; no polarity mesh or PrinciplesGate; code unchanged; 50/50 preflight.",
  ["partially conjunctive, integrated rebuild pending", "there is no polarity mesh or PrinciplesGate", "50/50 PASS"], GH)
n("O.swift", "open", "extract", "Swift port: deterministic delta patched (OroboroRelayApp.swift L68) but never compiled; no swiftc on the box.", ["Replaces Double.random.", "swiftc not installed on the box"], SWIFT+"|"+GH)
n("O.plumb", "open", "extract", "Plumbing consensus: data written 17:42 MT, not rerun; 4 rows provisional.", ["consensus_ok False count = 4"], PC)

# ---------------- repo state ----------------
n("G.oroboro", "repo", "colonize", "Oroboro main @ 3a3e021 (SYSTEMS.md, 18:11 MT): research/ metastasis-native, magnetic-launch (all addenda), cross-domain, PIPELINE.md, combined-report, one-page brief v1.", ["3a3e021 SYSTEMS.md", "34339a5 combined-report: one-page engineering brief"], GH)
n("G.oroboro_v1", "repo", "exit", "Oroboro main @ d6f2763 (v1 brief).", ["d6f2763"], GH)
n("G.relay", "repo", "colonize", "oroboro-relay @ d3d0940 (cc77063 deterministic delta + OroboroPipeline).", ["d3d0940", "cc77063"], GH)
n("G.cascade", "repo", "colonize", "metastatic-cascade-analysis @ d9f09c8 (v1–v5 papers; old model superseded).", ["d9f09c8"], GH)
n("G.policy", "repo", "clear", "Text-only connector: PDF/PNG/DOCX as SVG page images; no force pushes; secret scans; no video or raw pose landmarks published.", ["no force pushes", "raw pose landmarks, and anything from the personal-use video"], P4)

# ---------------- falsified (consolidated) ----------------
n("F.list", "falsified", "fail", "Falsified: frustrated loops ↑ pool; loop ablation empties pool; damper matters pre-wiring; onboard autopilot helps; 256 m/s; equator closes gap; comparator beats best-az; no-track with fuel; light sail; kite/line lift; Earth-field magnets; adaptive mesh / longer vacuum / pressure push; frustrated link with light exit; Oasis as truth test.",
  ["Predictions that failed"], P4)


# Origin of each finding in the chat arc (for Oasis novelty = recency rank). Either the
# file the finding was first written to (its mtime) or a commit time from github_state.json.
GL = R+"magnetic_launch_case_study/Magnetic_Launch_Goldilocks_CaseStudy.md"
STR = R+"magnetic_launch_case_study/Ondulatory_Strings_Wireframe_Addendum.md"
DCW = R+"magnetic_launch_case_study/Dreamcatcher_Weave_FollowOn.md"
INV = R+"metastasis_native/notes/github_scan_inventory.md"
PDJ = R+"magnetic_launch_case_study/outputs/plumbing_dynamics.json"
MSIM = "/workspace/oroboro-metastasis-sim/ITERATION_LOG.md"
ORIGIN = {}
def o(f, *ks):
    for k in ks: ORIGIN[k] = f
o(MSIM, "C.sweep", "C.switch", "C.onset", "C.interact")
o(NM, "C.native", "C.native_base", "C.tree", "C.frust819", "C.upstream", "C.tilt", "C.damper_silent")
o(LOG, "C.wiring", "C.gain1", "C.loo", "O.calib", "O.pgate", "C.frust829")
o(CD, "C.check200", "S.cd_stub_claim", "S.nonconj", "S.conj")
o(LT, "C.light_design", "C.light45", "C.light_oasis", "C.light_r")
o(PLB, "C.plumb", "C.plumb_leak", "C.plumb_claim", "L.plumb")
o(PDJ, "C.plumb_cons", "O.plumb")
o(GL, "L.metric", "L.track", "L.sealevel", "L.climb", "L.damp")
o(STR, "L.strings"); o(DCW, "L.weave")
o(GS, "L.dart407", "L.256", "L.1148", "L.autopilot", "L.heat")
o(GEO, "L.geo", "L.equator", "L.planechg")
o(RED, "L.repeater", "L.rep_limits", "L.comparator", "L.bestaz", "L.notrack")
o(LS, "L.sail"); o(GKS, "L.kite", "L.line", "L.lane", "L.magnet", "L.straw"); o(FUR, "L.fur", "L.fur_line_note")
o(P4, "X.door", "X.lateburn", "X.gate", "X.tilt", "X.geo", "X.loops", "X.conj", "X.oasis_truth", "F.list", "S.sponge", "S.workspace", "G.policy")
o(P1, "S.pipeline", "S.oasis", "S.levyw", "S.homeo")
o(INV, "S.audit_tree")
o("2026-11-27T16:02:36-07:00", "S.delta_fix", "G.relay", "O.swift")
o("2026-11-27T16:02:39-07:00", "O.epi")
o("2026-11-27T17:49:05-07:00", "G.cascade")
o("2026-11-27T17:58:46-07:00", "G.oroboro_v1")
o("2026-11-27T18:11:26-07:00", "S.systems17", "G.oroboro")
assert set(ORIGIN) == {n["id"] for n in N}, set(n["id"] for n in N) ^ set(ORIGIN)
