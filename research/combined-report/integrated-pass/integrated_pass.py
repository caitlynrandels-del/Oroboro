#!/usr/bin/env python3
"""Integrated Oroboro pass over ALL findings at once (t93u).

Speculative modeling only. Runs Caitlyn Randels' own Oroboro components over the
node/edge table (nodes.py, edges.py) as ONE loop per iteration, every node scored
simultaneously (no item-by-item walk), iterating to convergence:

 Genesis seed -> Nexus register -> Oasis score (her weights, make_env thresholds)
 -> PrinciplesGate.apply_score / veto -> NaCl PolarityMesh consensus (signed edges)
 -> native Dictator.stream -> Transcriber -> LevyLedger.assess (+ relay Dictator/
 Transcriber/Levy via OroboroPipeline) -> Levy salience -> deterministic delta
 reconciliation (supersede/contradict) -> isolate/recombine (OroboroPipeline) ->
 damper (native formula) -> homeostasis (rest load 40) -> next iteration.

Component code is imported unchanged from metastasis_native/oro_native.py,
metastasis_native/oro_mesh.py and oroboro-relay/oroboro-core.js (@d3d0940).
Mappings from document features onto component inputs are labeled glue, listed in
the output JSON under "mapping".
"""
import sys, os, re, json, glob, subprocess, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
R = "/workspace/oroboro-research/"
sys.path.insert(0, HERE); sys.path.insert(0, R + "metastasis_native")
from nodes import N, ORIGIN
from datetime import datetime
from edges import E
from oro_native import (PrinciplesGate, LevyLedger, Dictator, Transcriber, Genesis, Nexus,
                        make_env, load_params, KINDS)
from oro_mesh import PolarityMesh, Edge, IonicOrigin
CORE = "/tmp/verify_oroboro-relay/oroboro-core.js"

P = load_params(R + "metastasis_native/params.json")
NAT = P["native"]; ALPHA, GAIN, LEVY_GAIN = NAT["damper_alpha"], NAT["damper_gain"], NAT["levy_gain"]
W_LEVY = P["levy_weights"]
ids = [n["id"] for n in N]; idx = {k: i for i, k in enumerate(ids)}; M = len(ids)
kind = [n["kind"] for n in N]

def norm(s):
    s = s.replace('**', '').replace('`', '').replace('*', '').replace('\u202f', ' ').replace('\u00a0', ' ')
    return re.sub(r'\s+', ' ', s)

# ---------- static evidence features (copied from files, no estimates) ----------
corpus = sorted(set(glob.glob(R + "combined_report/part*.md") + glob.glob(R + "magnetic_launch_case_study/*.md")
                    + glob.glob(R + "metastasis_native/notes/*.md") + glob.glob(R + "cross_domain/*.md")))
ctext = {p: norm(open(p, encoding="utf-8").read()) for p in corpus}
corr = np.zeros(M); mt = np.zeros(M)
for i, nd in enumerate(N):
    corr[i] = max(sum(1 for t in ctext.values() if norm(v) in t) for v in nd["vals"])
    og = ORIGIN[nd["id"]]
    mt[i] = datetime.fromisoformat(og).timestamp() if og[:4].isdigit() else os.path.getmtime(og)
rank = mt.argsort().argsort(); nov = rank / max(1, M - 1)          # recency rank: newest source = 1

AGREE = {"support": 1.0, "mirror": 1.0, "same_lever": 0.4}
OPP = {"contradict", "supersede"}
A = np.zeros((M, M)); deg = np.zeros(M); opp_deg = np.zeros(M)
for e in E:
    a, b = idx[e["a"]], idx[e["b"]]; deg[a] += 1; deg[b] += 1
    if e["type"] in AGREE: A[a, b] = A[b, a] = max(A[a, b], AGREE[e["type"]])
    else: opp_deg[a] += 1; opp_deg[b] += 1

# ---------- NaCl polarity mesh over signed edges ----------
def build_mesh(repaired_pairs):
    nodes = ["GENESIS"] + ids; medges = []; owner = []
    for k, e in enumerate(E):
        if e["type"] in AGREE:          # agree = even path (two lock steps) -> same charge at endpoints
            m = f"m{k}"; nodes.append(m)
            medges += [Edge(e["a"], m, kind="agree"), Edge(m, e["b"], kind="agree")]; owner += [k, k]
        else:                            # oppose = one lock step -> opposite charge
            ed = Edge(e["a"], e["b"], kind=e["type"]); ed.repaired = (e["a"], e["b"]) in repaired_pairs
            medges.append(ed); owner.append(k)
    # Genesis seeds every connected component (anchor = highest-degree node of each component)
    par = {x: x for x in ids}
    def f(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for e in E: par[f(e["a"])] = f(e["b"])
    comps = {}
    for x in ids: comps.setdefault(f(x), []).append(x)
    for c in comps.values():
        hub = max(c, key=lambda x: (deg[idx[x]], x))
        nodes.append(f"g_{hub}"); medges += [Edge("GENESIS", f"g_{hub}", kind="genesis"), Edge(f"g_{hub}", hub, kind="genesis")]; owner += [-1, -1]
    mesh = PolarityMesh(nodes, medges, IonicOrigin())
    mesh.assign_charges_from("GENESIS", +1); mesh.process_polarities()
    return mesh, owner, len(comps)

def mesh_node_stats(mesh, owner):
    locked_by_edge = {}
    for ed, k in zip(mesh.edges, owner):
        if k < 0: continue
        locked_by_edge[k] = locked_by_edge.get(k, True) and ed.locked
    lock = np.zeros(M); tot = np.zeros(M); frustrated = []
    for k, ok in locked_by_edge.items():
        e = E[k]
        for x in (e["a"], e["b"]): tot[idx[x]] += 1; lock[idx[x]] += ok
        if not ok: frustrated.append(k)
    return np.where(tot > 0, lock / np.maximum(tot, 1), 1.0), frustrated, locked_by_edge

# ---------- relay pipeline (oroboro-core.js OroboroPipeline) ----------
relay = subprocess.Popen(["node", os.path.join(HERE, "relay_driver.js"), CORE, str(M)],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
def relay_tick(msg):
    relay.stdin.write(json.dumps(msg) + "\n"); relay.stdin.flush()
    return json.loads(relay.stdout.readline())

# ---------- the loop ----------
genesis = Genesis(); nexus = Nexus(); pg = PrinciplesGate()
transcriber = Transcriber(); dictator = Dictator(transcriber); ledger = LevyLedger(W_LEVY)
for i, nd in enumerate(N):        # Genesis seeds every node; Nexus records it
    nexus.register(nd["id"], dict(kind=nd["kind"], src=nd["src"], mirror=genesis.mirror("findings", i)))
supersede = [(idx[e["a"]], idx[e["b"]], e["note"]) for e in E if e["type"] == "supersede"]
contradict = [(idx[e["a"]], idx[e["b"]], e["note"]) for e in E if e["type"] == "contradict"]
# delta reconciliation resolution of contradictions: a node that supports BOTH endpoints resolves the pair
resolved = {}
for a, b, note in contradict:
    res = [ids[k] for k in range(M) if A[k, a] >= 1.0 and A[k, b] >= 1.0 and kind[k] == "clear"]
    if res: resolved[(ids[a], ids[b])] = res
repaired_pairs = set(resolved) | {(ids[a], ids[b]) for a, b, _ in supersede}   # Edge.repaired (self-repair flag)
mesh0, owner, n_comp = build_mesh(set())
lock0, frust0, _ = mesh_node_stats(mesh0, owner)
mesh, owner, _ = build_mesh(repaired_pairs)
lock_frac, frustrated, locked_by_edge = mesh_node_stats(mesh, owner)
inversion = mesh.inversion_holds()
frust_level = len(frustrated) / max(1, len(E))
ten = np.minimum(1.0, opp_deg / (1 + deg) + (1 - lock_frac))
coh = 0.5 * np.minimum(1.0, corr / 3.0) + 0.5 * lock_frac

gate = np.full(M, -1); w = np.array([W_LEVY[k] for k in kind], float); w /= w.sum()
labels = list(ids); pressure = 0.0; n_prev = 0; iso = None
nexus.register("state", dict(n_active=0, levy_pulse=0.0, frust_level=frust_level, pressure=0.0, principles=True, genesis_closed=True))
hist = []; vetoes_total = 0; it = 0
for it in range(1, 501):
    env = make_env((n_prev, n_prev * 0.5e6), P, {"valuation_threshold": None}, pressure=pressure,
                   damper_on=True, nexus_state=nexus.registry["state"])
    res_f = w / w.max()
    score = env["w"] @ np.vstack([nov, ten, coh, res_f])
    score = pg.apply_score(score, env)
    thr = env["thr"]
    g = np.where(score >= thr, 2, np.where(score >= 0.5 * thr, 1, 0))          # OasisGate.decide rule
    g2 = pg.veto(g, env); vetoes = int(((g == 2) & (g2 == 1)).sum()); vetoes_total += vetoes; g = g2
    # Delta reconciliation: superseded figures exit (later / corrected value wins)
    for a, b, _ in supersede: g[a] = 0
    # Dictator -> Transcriber -> Levy (native): one entry per kind among admitted nodes
    counts = {k: 0 for k in KINDS}
    for i in np.where(g > 0)[0]: counts[kind[i]] += 1
    entries = dictator.stream(it, counts); pulse = ledger.assess(entries)
    ema = ledger.ema if ledger.ema is not None else pulse
    levy_spike = max(0.0, (pulse - ema) / ema) if ema > 0 else 0.0
    ledger.ema = (1 - ALPHA) * ema + ALPHA * pulse
    # Levy salience: kind weight x gate, propagated over locked agree edges
    gf = np.array([{2: 1.0, 1: 0.5, 0: 0.1}[int(x)] for x in g])
    base = np.array([W_LEVY[k] for k in kind], float) * gf; base /= base.max()
    Aiso = A.copy()
    if iso is not None:                  # isolated cluster: cut from outside, others continue
        memb = np.array([labels[i] == iso for i in range(M)])
        Aiso[np.ix_(memb, ~memb)] = 0; Aiso[np.ix_(~memb, memb)] = 0
    rs = Aiso.sum(1, keepdims=True); An = np.where(rs > 0, Aiso / np.maximum(rs, 1e-12), 0)
    w_new = 0.5 * base + 0.5 * (An @ (w / w.max()))
    for a, b, _ in supersede: w_new[b] += w_new[a]; w_new[a] = 0.0
    w_new = w_new / w_new.sum()
    # Clusters: Levy-weighted label propagation on agree edges among admitted nodes (glue)
    adm = g > 0; new_labels = list(ids)
    order = sorted(range(M), key=lambda i: (-w_new[i], ids[i]))
    for _ in range(60):
        changed = False
        for i in order:
            if not adm[i]: continue
            sc = {new_labels[i]: w_new[i]}
            for j in np.where(A[i] > 0)[0]:
                if adm[j]: sc[new_labels[j]] = sc.get(new_labels[j], 0) + A[i, j] * w_new[j]
            best = max(sc.items(), key=lambda kv: (kv[1], kv[0]))[0]
            if best != new_labels[i]: new_labels[i] = best; changed = True
        if not changed: break
    sizes = {}
    for i in range(M):
        if adm[i]: sizes[new_labels[i]] = sizes.get(new_labels[i], 0) + 1
    for i in range(M):                    # merge clusters < 3 into best-connected neighbour cluster
        if adm[i] and sizes[new_labels[i]] < 3:
            sc = {}
            for j in np.where(A[i] > 0)[0]:
                if adm[j] and sizes[new_labels[j]] >= 3: sc[new_labels[j]] = sc.get(new_labels[j], 0) + A[i, j] * w_new[j]
            if not sc:                    # no admitted neighbour cluster: join the largest same-domain cluster
                for j in range(M):
                    if adm[j] and sizes[new_labels[j]] >= 3 and N[j]["domain"] == N[i]["domain"]:
                        sc[new_labels[j]] = sizes[new_labels[j]]
            if sc: new_labels[i] = max(sc.items(), key=lambda kv: (kv[1], kv[0]))[0]
    for i in range(M):
        if not adm[i]: new_labels[i] = "_recycled"
    # Relay pipeline tick: sectors = clusters; parts compute local Levy mass from intra-cluster edges only
    cl = sorted(set(l for l in new_labels if l != "_recycled"))
    whole = {c: int(round(1e5 * sum(w_new[i] for i in range(M) if new_labels[i] == c))) for c in cl}
    local = {}
    for c in cl:
        memb = np.array([new_labels[i] == c for i in range(M)])
        Ai = A * np.outer(memb, memb); r = Ai.sum(1, keepdims=True); Ain = np.where(r > 0, Ai / np.maximum(r, 1e-12), 0)
        wl = 0.5 * base + 0.5 * (Ain @ (w / w.max()))
        wl = wl / (0.5 * base + 0.5 * (An @ (w / w.max()))).sum()
        local[c] = {"flights": int(round(1e5 * wl[memb].sum())), "status": "ok"}
    out = relay_tick({"register": {c: {"flights": whole[c], "status": "ok"} for c in cl},
                      "radio": [N[i]["text"] for i in range(M) if adm[i]], "local": local})
    iso = out["isolated"]
    # Damper (native formula) + homeostasis load
    n_now = int((g == 2).sum())
    spike = max(0.0, (n_now - P["homeostasis"]["rest_load"]) / P["homeostasis"]["rest_load"])
    p_new = (1 - ALPHA) * pressure + ALPHA * GAIN * (spike + LEVY_GAIN * levy_spike)
    closed = all(k in nexus.registry for k in ids)
    nexus.register("state", dict(n_active=n_now, levy_pulse=pulse, frust_level=frust_level, pressure=p_new,
                                 principles=True, genesis_closed=closed))
    nexus.telemeter(it, dict(n_active=n_now, sum_epi_int=int(1e6 * float(w_new.sum()))))
    dw = float(np.abs(w_new - w).max()); dp = abs(p_new - pressure)
    same = (gate == g).all() and labels == new_labels
    hist.append(dict(it=it, thr=float(thr), H=float(env["H"]), committed=n_now, buffered=int((g == 1).sum()),
                     recycled=int((g == 0).sum()), vetoes=vetoes, pulse=pulse, pressure=p_new, relay_pressure=out["pressure"],
                     relay_limit=out["limit"], relay_coherent=out["coherent"], isolated=iso, n_clusters=len(cl), dw=dw, dp=dp))
    gate, w, labels, pressure, n_prev = g, w_new, new_labels, p_new, n_now
    if it > 3 and same and dw < 1e-9 and dp < 1e-9: break
relay.stdin.close(); relay.wait()

# ---------- outputs ----------
crit_native = [N[i]["id"] for i in range(M) if transcriber.CRITICAL and kind[i] in transcriber.CRITICAL]
clusters = {}
for i in range(M):
    clusters.setdefault(labels[i], []).append(i)
cl_out = []
tot_adm = sum(w[i] for i in range(M) if gate[i] > 0)
for c, mem in clusters.items():
    if c == "_recycled": continue
    share = float(sum(w[i] for i in mem) / tot_adm)
    cl_out.append(dict(hub=ids[max(mem, key=lambda i: w[i])], label=c, share=share, members=[ids[i] for i in sorted(mem, key=lambda i: -w[i])],
                       domains=sorted(set(N[i]["domain"] for i in mem))))
cl_out.sort(key=lambda d: -d["share"])
# Adaptive surface (ported rule from AdaptiveFurn.maybe_adapt / _nacl_votes): per-cluster detail
Lmin, Lmax = 0.04, 0.20; smax = max(d["share"] for d in cl_out); ncl = len(cl_out)
flag_nodes = {ids[a] for a, b, _ in contradict} | {ids[b] for a, b, _ in contradict}
for d in cl_out:
    s = d["share"] / smax; d["L_tgt"] = (1 - s) * Lmax + s * Lmin
    t_vote = 1 if any(m in flag_nodes for m in d["members"]) else 0
    q_vote = 1 if d["share"] > 1.0 / ncl else (-1 if d["share"] < 0.5 / ncl else 0)
    m_vote = 1 if d["L_tgt"] < 0.5 * (Lmin + Lmax) else -1
    votes = [t_vote, q_vote, m_vote]
    if votes.count(1) == 2 and votes.count(-1) == 1: votes = [1, 1, 1]
    elif votes.count(-1) == 2 and votes.count(1) == 1: votes = [-1, -1, -1]
    d["votes"] = [t_vote, q_vote, m_vote]; d["detail"] = "refine" if sum(votes) >= 2 else ("coarsen" if sum(votes) <= -1 else "hold")
result = dict(
    status="speculative modeling only; document-selection pass, not new science",
    n_nodes=M, n_edges=len(E), edge_types={t: sum(1 for e in E if e["type"] == t) for t in sorted(set(e["type"] for e in E))},
    iterations=it, converged=bool(hist[-1]["dw"] < 1e-9 and hist[-1]["dp"] < 1e-9), final_dw=hist[-1]["dw"], final_dp=hist[-1]["dp"],
    mesh=dict(components_seeded_by_genesis=n_comp, frustrated_before_repair=[(E[k]["a"], E[k]["b"], E[k]["type"]) for k in frust0],
              frustrated_after_repair=[(E[k]["a"], E[k]["b"], E[k]["type"]) for k in frustrated], inversion_holds=bool(inversion),
              mesh_nodes=len(mesh.nodes), mesh_edges=len(mesh.edges)),
    delta_reconciliation=dict(superseded=[dict(old=ids[a], new=ids[b], why=nt) for a, b, nt in supersede],
                              contradictions=[dict(a=ids[a], b=ids[b], note=nt, resolved_by=resolved.get((ids[a], ids[b]), [])) for a, b, nt in contradict]),
    principles_gate=dict(vetoes_total=vetoes_total, final_H=hist[-1]["H"], frust_level=frust_level,
                         note="apply_score clamps >0.99 to 0.9 and boosts when frust_level>0.6; veto turns commit->buffer when H<0.3"),
    relay=dict(isolations=sum(1 for h in hist if h["isolated"]), last=hist[-1]),
    native_transcriber_critical_kinds=list(transcriber.CRITICAL), levy_total=ledger.total_weight,
    clusters=cl_out,
    nodes=[dict(id=ids[i], domain=N[i]["domain"], kind=kind[i], gate={2: "commit", 1: "buffer", 0: "recycle"}[int(gate[i])],
                levy_w=float(w[i]), nov=float(nov[i]), ten=float(ten[i]), coh=float(coh[i]), corroboration=int(corr[i]),
                lock_frac=float(lock_frac[i]), cluster=labels[i], text=N[i]["text"], src=N[i]["src"], vals=N[i]["vals"]) for i in range(M)],
    history=hist,
    components=dict(
        ran={"Genesis": "seeds every node (mirror) and anchors every mesh component",
             "Nexus": "registers every node + per-iteration state; telemeter each iteration",
             "Oasis": "S = w·[nov,ten,coh,res] with params.json weights; commit/buffer/recycle at make_env threshold (0.65 base, +0.2 rest bump, + damper pressure)",
             "PrinciplesGate": "oro_native.PrinciplesGate.apply_score + veto, unchanged",
             "NaCl polarity mesh": "oro_mesh.PolarityMesh: BFS charges from Genesis, process_polarities, frustrated edges, inversion_holds",
             "Dictator/Transcriber": "native Dictator.stream + Transcriber (critical = colonize/exit); relay Dictator/Transcriber keyword flags",
             "Levy": "native LevyLedger.assess pulse; relay OroboroLevy; Levy kind weights drive salience",
             "Damper": "native formula p=(1-a)p+a*g*(spike+levy_gain*levy_spike), a=0.35, g=0.08; relay pipeline damped pressure",
             "Delta reconciliation": "deterministic: superseded figures exit and pass weight to the later/corrected node; contradictions flagged; relay computeDelta per cluster",
             "Isolate/recombine": "relay OroboroPipeline isolates most-drifted cluster when incoherent; isolated cluster cut from outside propagation next iteration",
             "Homeostasis": "make_env rest_load 40 / rest_bump 0.2 on committed count",
             "Self-repair flag": "Edge.repaired set on contradictions resolved by delta reconciliation (heat model of _adapt_niche not applicable)",
             "Adaptive surface (ported rule)": "AdaptiveFurn.maybe_adapt L_tgt interpolation + _nacl_votes 3-vote majority sets per-cluster detail"},
        not_applicable={"Dream-catcher weave": "build_system_mesh / run_dreamcatcher_weave build a fixed niche/skeleton geometry; no clustering operation exists to apply to a findings graph. Its purpose (odd-loop frustration) is used via PolarityMesh.",
                        "Smart magnets": "defined only as a physical force (guidance) and a leak-halving hold (plumbing); nothing applies to a findings graph",
                        "Sponge": "not used in any study; not applied here",
                        "Self-repairing niche heat model": "_adapt_niche needs fail/exit/colonize heat on niche edges; no analogue",
                        "Clustering": "Levy-weighted label propagation is glue code, not an Oroboro component"}),
    mapping=dict(nov="recency rank of the finding in the chat arc (origin file mtime or commit time, nodes.ORIGIN)", ten="oppose-edge share + mesh frustration", coh="0.5*min(1,corroborating corpus files/3) + 0.5*mesh lock fraction",
                 res="Levy salience / max (from previous iteration)", levy_kind="colonize=settled result, detach=modification, fail=failed/falsified, exit=superseded, extract=open item, clear=context",
                 n_active="committed node count (homeostasis load)"),
)
json.dump(result, open(os.path.join(HERE, "integrated_pass_result.json"), "w"), indent=1, ensure_ascii=False)
print("iterations", it, "converged", result["converged"], "dw", hist[-1]["dw"])
print("gates", {k: sum(1 for n in result["nodes"] if n["gate"] == k) for k in ("commit", "buffer", "recycle")})
print("vetoes", vetoes_total, "H", hist[-1]["H"], "thr", hist[-1]["thr"], "pressure", hist[-1]["pressure"])
print("mesh frustrated before", len(frust0), "after", len(frustrated), "inversion", inversion)
for d in cl_out: print(round(d["share"], 3), d["detail"], d["hub"], d["members"])
print("recycled", [n["id"] for n in result["nodes"] if n["gate"] == "recycle"])
