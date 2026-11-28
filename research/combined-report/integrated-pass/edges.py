# Typed edges between nodes. support / mirror / same_lever are "agree" edges;
# contradict / supersede are "oppose" edges. supersede is (old, new) and carries the
# reason the later/corrected value wins. same_lever edges are generated from node lever tags.
from nodes import N
E = []
def e(a, b, t, note=""): E.append(dict(a=a, b=b, type=t, note=note))

# supersede (old -> new)
e("L.256", "L.1148", "supersede", "incomplete 900 s coast; true Kepler two-burn residual (P3 B4)")
e("C.native_base", "C.gain1", "supersede", "conjunctive wiring is the working baseline (P2 A3)")
e("C.frust819", "C.frust829", "supersede", "conjunctive 454-setting rerun (P2 A3)")
e("S.cd_stub_claim", "S.delta_fix", "supersede", "relay cc77063 replaced the stub after the cross-domain note")
e("S.audit_tree", "S.delta_fix", "supersede", "audited stub fixed in relay cc77063")
e("C.plumb_claim", "C.plumb_cons", "supersede", "plumbing_dynamics.json shows consensus_ok False on 4 rows; corrected in P2 A5")
e("C.damper_silent", "C.check200", "supersede", "damper engages once Levy is wired in (P2 A3)")
e("G.oroboro_v1", "G.oroboro", "supersede", "later commits on main (GitHub API)")
# contradict (not a supersession)
e("L.line", "L.fur", "contradict", "fixed line 2,791 (guidance) vs 2,378 (fur integrator)")
e("O.calib", "C.sweep", "contradict", "conjunctive default 9.1%/6.36 vs calibration 21.7%/10.38")
e("C.frust829", "C.light_r", "contradict", "frustrated-vs-pool link absent under light exit")
e("L.autopilot", "S.conj", "contradict", "a conjunctive onboard loop hurt insertion")
# support
for a, b in [("C.sweep","C.switch"),("C.sweep","C.onset"),("C.interact","C.sweep"),("G.cascade","C.sweep"),
             ("C.upstream","X.door"),("C.check200","X.door"),("C.light45","X.door"),("C.plumb","X.door"),("L.dart407","X.door"),("L.geo","X.door"),
             ("L.repeater","X.lateburn"),("L.notrack","X.lateburn"),("L.sail","X.lateburn"),("L.kite","X.lateburn"),("L.line","X.lateburn"),
             ("L.lane","X.lateburn"),("L.magnet","X.lateburn"),("L.straw","X.lateburn"),("L.fur","X.lateburn"),("L.plumb","X.lateburn"),("L.comparator","X.lateburn"),
             ("C.light_oasis","X.gate"),("C.plumb_leak","X.gate"),("L.comparator","X.gate"),("S.oasis","C.light_oasis"),
             ("C.tilt","X.tilt"),("L.dart407","X.tilt"),("C.check200","X.tilt"),("L.geo","X.geo"),("L.equator","X.geo"),("C.upstream","X.geo"),
             ("C.tree","X.loops"),("C.frust829","X.loops"),("C.light_r","X.loops"),("C.native","C.tree"),("L.weave","C.native"),
             ("C.wiring","C.gain1"),("C.gain1","C.loo"),("C.check200","X.conj"),("L.autopilot","X.conj"),("C.loo","X.conj"),
             ("S.pipeline","S.conj"),("S.conj","C.wiring"),("S.nonconj","S.conj"),("S.levyw","C.wiring"),("S.homeo","C.damper_silent"),
             ("S.delta_fix","G.relay"),("S.systems17","G.oroboro"),("S.sponge","S.systems17"),("S.workspace","L.weave"),("G.policy","G.oroboro"),
             ("L.metric","L.repeater"),("L.metric","L.dart407"),("L.track","L.climb"),("L.sealevel","L.climb"),("L.damp","L.climb"),
             ("L.bestaz","L.comparator"),("L.rep_limits","L.repeater"),("L.planechg","L.geo"),("L.1148","L.comparator"),("L.1148","L.repeater"),
             ("L.plumb","L.notrack"),("L.straw","L.plumb"),("L.sail","L.notrack"),("L.fur_line_note","L.fur"),("L.fur_line_note","L.line"),
             ("L.strings","L.weave"),("L.heat","L.dart407"),("C.light_design","C.light45"),("C.plumb","C.plumb_leak"),
             ("C.plumb_cons","O.plumb"),("O.pgate","C.loo"),("O.calib","C.gain1"),("O.swift","S.delta_fix"),("O.epi","G.policy"),
             ("X.oasis_truth","S.oasis")]:
    e(a, b, "support")
for nd in N:
    if nd["kind"] == "fail" and nd["id"] != "F.list": e(nd["id"], "F.list", "support")
# cross-domain mirrors
for a, b, note in [("C.upstream","L.geo","geography ~ organ permissiveness"),("C.tilt","L.dart407","tilt, opposite sign"),
                   ("C.light45","L.repeater","small paid well-placed action"),("C.plumb","L.plumb","plumbing both domains"),
                   ("C.light_oasis","L.comparator","gate form matters"),("C.tree","L.weave","odd loops"),
                   ("C.check200","L.autopilot","conjunctive wiring effect"),("L.heat","C.native","heat-window repair"),
                   ("L.magnet","C.plumb_leak","smart magnet")]:
    e(a, b, "mirror", note)
# same-lever (generated)
ids = [nd for nd in N if nd["levers"]]
for i in range(len(ids)):
    for j in range(i+1, len(ids)):
        sh = set(ids[i]["levers"]) & set(ids[j]["levers"])
        if sh: e(ids[i]["id"], ids[j]["id"], "same_lever", ",".join(sorted(sh)))
