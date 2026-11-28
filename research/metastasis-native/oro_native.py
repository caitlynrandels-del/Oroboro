#!/usr/bin/env python3
"""
Native Oroboro metastasis sim.

The core state is the polarity mesh (Genesis origin, circulation loop,
dream-catcher niche around each organ, return edges). Cell occupancy,
mesh consensus (locks vs frustrated odd-loop edges), a real damped
delta-reconciliation feedback, a documented Levy +4 reawakening pulse,
an Oasis commit/buffer/recycle gate, and an adaptive self-repairing
niche all run inside the monthly step. Not bolted on after the fact.

Cascade timing rates are taken from the original oro_cascade calibration
so a baseline close to colony ~21.7% / dormant ~10.4 can be asked for.

Conjunctive pipeline (integrated=True, default since 2026-11-27): every
component sits on ONE monthly loop and feeds the next:

  Genesis -> Parts (state reduction) -> Oasis salience -> PrinciplesGate
  -> NaCl polarity mesh seat / mesh consensus -> Dictator stream
  -> Transcriber -> Levy (assesses Transcriber entries) -> Nexus registry
  -> delta reconciliation (occupancy spike + Levy pulse spike, damped)
  -> homeostasis + Oasis threshold for next month -> dream-catcher niche
  self-repair (heat) -> mesh consensus refresh -> Genesis closure -> loop.

integrated=False reproduces the pre-integration native run (Levy and
Transcriber were ledgers only; the damper never engaged at baseline).

Speculative modeling only. No biological or clinical claims.
"""
from __future__ import annotations
import json, os, math, hashlib
from typing import Optional
import numpy as np
from oro_mesh import IonicOrigin, PolarityMesh, build_system_mesh, landing_pools, mesh_inversion_holds
_INV_CACHE = {}

HERE = os.path.dirname(os.path.abspath(__file__))
M64 = (1 << 64) - 1
KINDS = ["clear", "detach", "fail", "colonize", "exit", "extract"]
CIRC, DORM, OVERT, CLEARED, LOST, PENDING, EXTRACTED = 0, 1, 2, 3, 4, -1, 5


def load_params(path=None):
    with open(path or os.path.join(HERE, "params.json")) as f:
        return json.load(f)


def _u64(x): return np.uint64(x & M64)


def U(seed, ids, month, stream):
    """Counter-based uniform [0,1) per id; depends only on (seed, id, month, stream)."""
    base = _u64(seed * 0xD1B54A32D192ED03 + month * 0x8CB92BA72F3D8DD7 + stream * 0xFF51AFD7ED558CCD)
    with np.errstate(over="ignore"):
        x = ids.astype(np.uint64) * _u64(0x9E3779B97F4A7C15) + base
        x ^= x >> np.uint64(30); x *= _u64(0xBF58476D1CE4E5B9)
        x ^= x >> np.uint64(27); x *= _u64(0x94D049BB133111EB)
        x ^= x >> np.uint64(31)
    return (x >> np.uint64(11)).astype(np.float64) * (1.0 / (1 << 53))


def poisson_inv(u, lam):
    k, p = 0, math.exp(-lam); c = p
    while u > c and k < 60:
        k += 1; p *= lam / k; c += p
    return k


NEUTRAL = dict(shed_mult=1.0, circ_clear_mult=1.0, dorm_clear_mult=1.0, dorm_maintenance=0.0,
               organ_perm_scale=1.0, pref_perm_scale=1.0, valuation_threshold=None,
               colonization_barrier=0.0, start_month=1)


def lever_at(base, lev, m):
    if m >= lev["start_month"]:
        return lev
    return base


# ----- Oroboro components (from oroboro-core.js / oro_cascade, no Math.random stub) -----
class Genesis:
    root_tag = "I am the OG avatar"
    weight = float("inf")
    epi_origin = 0.5
    def mirror(self, cancer, seed):
        return dict(origin=self.root_tag, cancer=cancer, seed=seed, weight=self.weight)


class Nexus:
    def __init__(self):
        self.registry = {}
        self.archive = []
        self.metrics = dict(deltas=0, reconciliations=0, isolations=0)
    def register(self, key, data): self.registry[key] = data
    def telemeter(self, m, summary): self.archive.append((m, summary["n_active"], summary["sum_epi_int"]))


class Transcriber:
    CRITICAL = ("colonize", "exit")   # oroboro-core.js isCritical(): alert-class events
    def __init__(self):
        self.lexicon = {}
        self.chronicles = []
        self.anonymous_log = []
    def ingest(self, text, source="dictator", kind=None, n=1, month=None):
        entry = dict(text=text, source=source, kind=kind, n=int(n), month=month,
                     critical=(kind in self.CRITICAL))
        self.chronicles.append(entry)
        if entry["critical"]:
            self.anonymous_log.append(entry)
        return entry
    def write(self, msg):
        return self.ingest(msg, "transcriber")


class Dictator:
    def __init__(self, transcriber: Transcriber):
        self.transcriber = transcriber
    def stream(self, month, counts):
        """In-step stream: one finalized entry per event kind this month -> Transcriber."""
        out = []
        for k in KINDS:
            n = int(counts.get(k, 0))
            if n:
                out.append(self.transcriber.ingest(f"[Dictator t={month:03d}] {k.upper()} x{n}", "dictator", k, n, month))
        return out
    def chronicle(self, month, kind, cell_id, organ_name=None):
        loc = f" @{organ_name}" if organ_name else ""
        return self.transcriber.ingest(f"[Dictator t={month:03d}] cell {cell_id} {kind.upper()}{loc}", "dictator")


class LevyLedger:
    """System Levy: assesses Transcriber entries (oroboro-core.js OroboroLevy.assess)."""
    def __init__(self, W):
        self.W = {k: W[k] for k in KINDS}
        self.total_weight = 0.0
        self.ema = None
    def assess(self, entries):
        pulse = 0.0
        for e in entries:
            w = self.W[e["kind"]] * e["n"]
            e["weight"] = w; e["levied"] = True
            pulse += w
        self.total_weight += pulse
        return pulse


class PrinciplesGate:
    """Port of sky-ari-ai OroboroCorePrinciplesGate_REAL.cs, applied after the Oasis score.
    InternalDiagnosticFirst: comfort (homeostasis H) < 0.3 -> no world mutation (commit -> buffer).
    AcceptHumanPain: utility > 0.99 is clamped to 0.9 (perfection = hazard).
    RerouteFrustration: frustration level (unlocked mesh-edge fraction) > 0.6 -> utility + 0.3*f.
    AdaptOrDie: a cell that keeps failing at the same niche must adapt (re-seat), see Part.step.
    """
    def apply_score(self, score, S_env):
        score = np.where(score > 0.99, 0.9, score)
        f = S_env.get("frust_level", 0.0)
        if f > 0.6:
            score = np.minimum(1.0, score + f * 0.3)
        return score
    def veto(self, g, S_env):
        if S_env.get("H", 1.0) < 0.3:
            g = np.where(g == 2, 1, g)
        return g
    def proofread(self, g, mismatch, thr):
        """t96u DNA toggle only (off by default): mismatch-repair proofreading. A commit whose
        zipper/pairing mismatch exceeds thr is held back to buffer (structural analogy only)."""
        return np.where((g == 2) & (mismatch > thr), 1, g)


class Levy:
    def __init__(self, W):
        self.W = {k: W[k] for k in KINDS}
        self.counts = {k: 0 for k in KINDS}
    def add(self, kind, n=1): self.counts[kind] += int(n)
    def total(self): return float(sum(self.W[k] * self.counts[k] for k in KINDS))


class OasisGate:
    """Sky / Oasis salience engine: commit / buffer / recycle. Threshold default 0.65."""
    COMMIT, BUFFER, RECYCLE = 2, 1, 0
    def score(self, epi, fit, org_perm, S_env):
        w = S_env["w"]
        nov = np.minimum(1.0, 2 * np.abs(epi - S_env["mean_epi"]))
        ten = 1 - np.abs(fit - S_env["H"])
        coh = 0.5 * fit + 0.5 * org_perm
        res = 1 - 2 * np.abs(epi - Genesis.epi_origin)
        return w[0] * nov + w[1] * ten + w[2] * coh + w[3] * res
    def decide(self, epi, fit, org_perm, S_env, thr):
        score = self.score(epi, fit, org_perm, S_env)
        return np.where(score >= thr, self.COMMIT, np.where(score >= 0.5 * thr, self.BUFFER, self.RECYCLE))


# ----- Part (independent reduced state) -----
class Part:
    def __init__(self, pid, ids, shed_month, seed, P):
        self.pid = pid; self.ids = ids; self.shed_month = shed_month; n = len(ids)
        ci = P["cell_init"]
        self.epi = U(seed, ids, 0, 1)
        self.ev = ci["immune_evasion_lo"] + U(seed, ids, 0, 2) * ci["immune_evasion_span"]
        self.fit = U(seed, ids, 0, 3)
        self.state = np.full(n, PENDING, dtype=np.int8)
        self.organ = np.full(n, -1, dtype=np.int16)
        self.d = np.zeros(n)                # origami fold depth (0 unfolded, high = folded/dormant)
        self.edge = np.full(n, -1, dtype=np.int32)   # occupied mesh edge
        self.frust = np.zeros(n, dtype=np.bool_)     # sitting on a frustrated odd-loop edge
        self.levy = Levy(P["levy_weights"])
        self.events = []
        self.heat = {}
        self.organ_colonized = {}
        self.ledger_gate = dict(recycle=0, buffer=0, commit=0)
        self.cleared_by = dict(circ=0, dorm=0, recycle=0)
        self.lost_seed = 0; self.col_fail = 0
        self.oasis = OasisGate()
        self.principles = PrinciplesGate()
        self.fails = np.zeros(n, dtype=np.int8)
        self.adapted = 0
        # Light-transport flags (no-op unless native["light"] is on)
        self.tagged = np.zeros(n, dtype=np.bool_)
        self.leaky = np.zeros(n, dtype=np.bool_)
        self.located = np.zeros(n, dtype=np.bool_)
        self.organ_extracted_overt = {}
        self.extracted_from = dict(circ=0, dorm=0, overt=0)
        self.n_tagged_ever = 0; self.n_leaky_ever = 0; self.n_located_ever = 0
        self.extract_attempts = 0; self.extract_commits = 0
        # Plumbing counters (no-op unless native['plumbing'] is on)
        self.plumbing_leaked_circ = 0
        self.plumbing_leaked_niche = 0
        self.plumbing_valve_block = 0
        self.plumbing_valve_commit = 0
        self.plumbing_sealed = 0
        # t96u counters (stay zero unless a toggle is on)
        self.skip = np.zeros(n, dtype=np.bool_)
        self.zip_skips = 0; self.zip_unanchored = 0; self.zip_rezips = 0
        self.dna_reannealed = 0; self.organ_unzipped_overt = {}
        self.pg_score_mod = 0; self.pg_veto = 0; self.pg_proof = 0
        self.wbc_patrolled = 0; self.wbc_cleared = 0; self.rbc_passes = 0

    def summary(self):
        a = (self.state == CIRC) | (self.state == DORM)
        return int(a.sum()), int(np.rint(self.epi[a] * 1e6).astype(np.int64).sum())

    def _gate(self, idx, org_perm, S_env, seed, m, stream, thr):
        if not S_env.get("integrated", False):
            return self.oasis.decide(self.epi[idx], self.fit[idx], org_perm, S_env, thr)
        score = self.oasis.score(self.epi[idx], self.fit[idx], org_perm, S_env)
        if S_env.get("principles", True):
            s0 = score
            score = self.principles.apply_score(score, S_env)
            self.pg_score_mod += int(np.sum(score != s0))
        g = np.where(score >= thr, OasisGate.COMMIT, np.where(score >= 0.5 * thr, OasisGate.BUFFER, OasisGate.RECYCLE))
        if S_env.get("principles", True):
            g0 = g
            g = self.principles.veto(g, S_env)
            self.pg_veto += int(np.sum(g != g0))
        return g

    def step(self, m, S_env, cfg, P, lev, seed, mesh, meta, native, record=False):
        st = self.state; ids = self.ids
        # --- detach pulse for newly shed cells (Genesis / magnetic detach): Levy +7
        new = (st == PENDING) & (self.shed_month == m)
        if new.any():
            st[new] = CIRC; self.levy.add("detach", int(new.sum()))
            if record: self.events += [(m, "detach", int(i), -1) for i in ids[new]]
        self._light_step(m, S_env, cfg, P, lev, seed, mesh, meta, native, record)
        self._plumbing_step(m, S_env, cfg, P, lev, seed, mesh, meta, native, record)
        organs = cfg["organs"]; perm = cfg["perm_eff"](lev)
        # tilt / torque: rotational bias on the circulation loop's organ encounter weights
        tilt = float(native.get("tilt", 0.0)); phase = float(native.get("torque_phase", 0.0))
        if tilt != 0.0:
            ang = 2 * math.pi * np.arange(len(perm)) / max(len(perm), 1) - phase
            perm = np.clip(perm * (1.0 + tilt * np.cos(ang)), 1e-6, 1.0)
        thr = S_env["thr"]

        # --- circulating cells
        ci = np.nonzero(st == CIRC)[0]
        if len(ci):
            evn = (self.ev[ci] - P["cell_init"]["immune_evasion_lo"]) / P["cell_init"]["immune_evasion_span"]
            pc = np.minimum(0.99, P["circ_clear_p"] * lev["circ_clear_mult"] * (1 - 0.5 * evn))
            clr = U(seed, ids[ci], m, 10) < pc
            if clr.any():
                st[ci[clr]] = CLEARED; self.levy.add("clear", int(clr.sum())); self.cleared_by["circ"] += int(clr.sum())
                if record: self.events += [(m, "clear", int(i), -1) for i in ids[ci[clr]]]
            rem = ci[~clr]
            if len(rem):
                arr = U(seed, ids[rem], m, 11) < P["arrest_p"]
                ai = rem[arr]
                if len(ai):
                    lc = _light_cfg(native)
                    up_lure = (lc["on"] and lc["do_lure"] and lc["timing"] == "upstream"
                               and m >= lc["start"] and lc["strength"] > 0)
                    if up_lure:
                        perm_use = np.concatenate([perm, [lc["strength"]]])
                    else:
                        perm_use = perm
                    cum = np.cumsum(perm_use / perm_use.sum())
                    org = np.minimum(np.searchsorted(cum, U(seed, ids[ai], m, 12), side="right"), len(perm_use) - 1)
                    if up_lure:
                        is_ex = org == len(perm)
                        ex_i = ai[is_ex]
                        if len(ex_i):
                            # Oasis recycle on an extract proposal is a refused move, not a clearance.
                            self._try_extract(ex_i, meta.get("lure_idx") or [], S_env, P, seed, m, 40,
                                              mesh, meta, native, record, attempt_all=True)
                        ai = ai[~is_ex]; org = org[~is_ex]
                    if len(ai):
                        g = self._gate(ai, perm[org], S_env, seed, m, 12, thr)
                        self.ledger_gate["recycle"] += int((g == 0).sum()); self.ledger_gate["buffer"] += int((g == 1).sum())
                        self.ledger_gate["commit"] += int((g == 2).sum())
                        rec = ai[g == 0]
                        if len(rec):
                            st[rec] = CLEARED; self.levy.add("clear", len(rec)); self.cleared_by["recycle"] += len(rec)
                            if record: self.events += [(m, "recycle", int(i), -1) for i in ids[rec]]
                        cm = g == 2; ci2 = ai[cm]; o2 = org[cm]
                        if len(ci2):
                            fo = self.fit[ci2] * perm[o2] * (P["fit_mix"][0] + P["fit_mix"][1] * self.epi[ci2])
                            ok = fo >= P["seed_threshold"]
                            bad = ci2[~ok]
                            if len(bad):
                                st[bad] = LOST; self.levy.add("fail", len(bad)); self.lost_seed += len(bad)
                                if record: self.events += [(m, "fail", int(i), int(o)) for i, o in zip(ids[bad], o2[~ok])]
                            good = ci2[ok]; og = o2[ok]
                            bc = _bio_cfg(native)
                            if bc["zipper"] and bc["zip_attach"] < 1.0 and len(good):
                                # attachment quality: an unanchored cell stays in circulation
                                anch = U(seed, ids[good], m, 50) < bc["zip_attach"]
                                self.zip_unanchored += int((~anch).sum()); good = good[anch]; og = og[anch]
                            if len(good):
                                st[good] = DORM; self.organ[good] = og; self.d[good] = P["dormancy"]["initial_depth"]
                                self._seat_on_niche(good, og, mesh, meta, native, seed, m)
                                if bc["zipper"]:
                                    sk = _mismatch(self, good, perm[og], bc, seed, m, 51) > bc["zip_tol"]
                                    self.skip[good] = sk; self.frust[good] = self.frust[good] | sk
                                    self.zip_skips += int(sk.sum())
                                for o in og:
                                    self.heat[int(o)] = self.heat.get(int(o), 0.0) + 0.1

        # --- dormant cells (origami-folded). Reawakening = documented Levy +4 pulse.
        di = np.nonzero(st == DORM)[0]
        if len(di):
            evn = (self.ev[di] - P["cell_init"]["immune_evasion_lo"]) / P["cell_init"]["immune_evasion_span"]
            pdc = np.minimum(0.99, P["dorm_clear_p"] * lev["dorm_clear_mult"] * (1 - 0.5 * evn))
            clr = U(seed, ids[di], m, 13) < pdc
            if clr.any():
                st[di[clr]] = CLEARED; self.levy.add("clear", int(clr.sum())); self.cleared_by["dorm"] += int(clr.sum())
                self.edge[di[clr]] = -1; self.frust[di[clr]] = False
                if record: self.events += [(m, "clear", int(i), int(o)) for i, o in zip(ids[di[clr]], self.organ[di[clr]])]
            di = di[~clr]
        bc = _bio_cfg(native)
        if len(di) and bc["wbc"] and m >= bc["wbc_start"] and bc["wbc_patrol"] > 0:
            pat = di[U(seed, ids[di], m, 54) < bc["wbc_patrol"]]
            if len(pat):
                self.wbc_patrolled += len(pat)
                gw = self._gate(pat, perm[self.organ[pat].astype(int)], S_env, seed, m, 54, thr)
                rc = pat[gw == OasisGate.RECYCLE] if native.get("wbc_recognize", "recycle") == "recycle" else pat[gw != OasisGate.COMMIT]
                if len(rc):
                    st[rc] = CLEARED; self.levy.add("clear", len(rc)); self.cleared_by["recycle"] += len(rc)
                    self.edge[rc] = -1; self.frust[rc] = False; self.skip[rc] = False; self.wbc_cleared += len(rc)
                    if record: self.events += [(m, "recycle", int(ids[i]), int(self.organ[i])) for i in rc]
                di = di[st[di] == DORM]
        if len(di) and bc["zipper"] and bc["zip_slider"] > 0:
            sk = di[self.skip[di]]
            if len(sk):
                tr = sk[U(seed, ids[sk], m, 52) < bc["zip_slider"]]
                if len(tr):
                    still = _mismatch(self, tr, perm[self.organ[tr].astype(int)], bc, seed, m, 55) > bc["zip_tol"]
                    closed = tr[~still]; self.zip_rezips += len(closed)
                    self.skip[closed] = False
                    for c_ in closed:
                        ei = int(self.edge[c_]); self.frust[c_] = (ei < 0) or (not mesh.edges[ei].locked)
        if len(di) and bc["dna"] and bc["dna_reanneal"] > 0:
            fr = di[self.frust[di] & ~self.skip[di]]
            if len(fr):
                ra = fr[U(seed, ids[fr], m, 56) < bc["dna_reanneal"]]
                if len(ra):
                    self._reseat_lockable(ra, self.organ[ra].astype(int), mesh, meta, native)
                    self.dna_reannealed += int((~self.frust[ra]).sum())
        if len(di):
            mt = lev["dorm_maintenance"]
            self.d[di] = np.minimum(1.0, self.d[di] + P["dormancy"]["restore_rate"] * mt * (1 - self.d[di]))
            o = self.organ[di].astype(int)
            h = P["exit_p"] * self.epi[di] * (1 - mt) * (1.25 - self.d[di]) * (0.4 + perm[o])
            wake = U(seed, ids[di], m, 14) < np.minimum(1.0, h)
            wi = di[wake]
            if len(wi):
                ow = self.organ[wi].astype(int)
                g = self._gate(wi, perm[ow], S_env, seed, m, 14, thr)
                if bc["dna"] and bc["dna_proof"] and S_env.get("integrated", False) and S_env.get("principles", True):
                    g0 = g
                    g = self.principles.proofread(g, _mismatch(self, wi, perm[ow], bc, seed, m, 53), bc["dna_proof_thr"])
                    self.pg_proof += int(np.sum(g != g0))
                self.ledger_gate["recycle"] += int((g == 0).sum()); self.ledger_gate["buffer"] += int((g == 1).sum())
                self.ledger_gate["commit"] += int((g == 2).sum())
                rec = wi[g == 0]
                if len(rec):
                    st[rec] = CLEARED; self.levy.add("clear", len(rec)); self.cleared_by["recycle"] += len(rec)
                    self.edge[rec] = -1; self.frust[rec] = False
                    if record: self.events += [(m, "recycle", int(ids[i]), int(self.organ[i])) for i in rec]
                cm = wi[g == 2]
                if len(cm):
                    # Documented Levy-weighted reawakening / origami-unfold pulse (+4)
                    self.levy.add("exit", len(cm)); self.d[cm] *= P["dormancy"]["exit_factor"]
                    if record: self.events += [(m, "exit", int(ids[i]), int(self.organ[i])) for i in cm]
                    # Frustrated occupants may hop onto a lockable hoop edge (return / unfold)
                    hop_p = float(native.get("hop_from_frustrated", 0.0))
                    if hop_p > 0 and self.frust[cm].any():
                        hop = self.frust[cm] & (U(seed, ids[cm], m, 16) < hop_p)
                        if hop.any():
                            self._reseat_lockable(cm[hop], self.organ[cm[hop]].astype(int), mesh, meta, native)
                    oc = self.organ[cm].astype(int)
                    fo = self.fit[cm] * perm[oc] * (P["fit_mix"][0] + P["fit_mix"][1] * self.epi[cm])
                    thr_c = np.where(oc == cfg["pref_idx"], P["col_threshold_pref"], P["col_threshold_other"]) + lev["colonization_barrier"]
                    # Native mesh rule: a frustrated odd-loop edge cannot lock, so it cannot colonize.
                    open_path = ~self.frust[cm]
                    succ = (fo > thr_c) & (U(seed, ids[cm], m, 15) < P["col_accept"]) & open_path
                    s_i = cm[succ]
                    if len(s_i):
                        st[s_i] = OVERT; self.levy.add("colonize", len(s_i))
                        self.frust[s_i] = False
                        for o_ in self.organ[s_i]:
                            self.organ_colonized[int(o_)] = self.organ_colonized.get(int(o_), 0) + 1
                            self.heat[("col", int(o_))] = self.heat.get(("col", int(o_)), 0) + 1
                        if record: self.events += [(m, "colonize", int(ids[i]), int(self.organ[i])) for i in s_i]
                    f_i = cm[~succ]
                    if len(f_i):
                        self.levy.add("fail", len(f_i)); self.col_fail += len(f_i)
                        self.d[f_i] = np.minimum(1.0, self.d[f_i] + P["dormancy"]["fail_gain"])
                        if S_env.get("integrated", False) and S_env.get("principles", True):
                            # AdaptOrDie: repeated failure at the same niche forces adaptation (re-seat)
                            self.fails[f_i] = np.minimum(100, self.fails[f_i] + 1)
                            ad = f_i[(self.fails[f_i] >= 2) & self.frust[f_i]]
                            if len(ad):
                                self._reseat_lockable(ad, self.organ[ad].astype(int), mesh, meta, native)
                                self.fails[ad] = 0; self.adapted += len(ad)
                        if record: self.events += [(m, "fail", int(ids[i]), int(self.organ[i])) for i in f_i]

    def _seat_on_niche(self, idx, organs, mesh, meta, native, seed, m):
        """Seat newly arrested cells on a niche edge. Bowl-depth sends them into the web."""
        bowl = float(native.get("bowl_depth", 0.5))
        u_bowl = U(seed, self.ids[idx], m, 20)
        u_pick = U(seed, self.ids[idx], m, 21)
        for k, cell in enumerate(idx):
            o = int(organs[k])
            spoke, hoop, b = landing_pools(meta, mesh, o, bowl)
            use_web = (u_bowl[k] < b) if spoke else False
            pool = spoke if (use_web and spoke) else (hoop if hoop else spoke)
            if not pool:
                self.edge[cell] = -1; self.frust[cell] = False
                continue
            ei = pool[int(u_pick[k] * len(pool)) % len(pool)]
            self.edge[cell] = ei
            e = mesh.edges[ei]
            self.frust[cell] = (not e.locked)

    def _reseat_lockable(self, idx, organs, mesh, meta, native):
        for k, cell in enumerate(idx):
            o = int(organs[k])
            lockable = [i for i in (meta["hoop_idx"][o] + meta["spoke_idx"][o] + meta["niche_edge_idx"][o])
                        if mesh.edges[i].locked]
            if not lockable:
                continue
            ei = lockable[int(self.ids[cell]) % len(lockable)]
            self.edge[cell] = ei
            self.frust[cell] = (not mesh.edges[ei].locked)

    def _light_step(self, m, S_env, cfg, P, lev, seed, mesh, meta, native, record=False):
        """Directed light-transport to the extraction node, on the conjunctive loop.

        Marks (tag / leaky / locate) and Oasis-gated moves happen before monthly
        clearance so a directed exit can compete with other fates. Recycle on an
        extract proposal is a refused move, not a clearance. Speculative only.
        """
        lc = _light_cfg(native)
        if not lc["on"] or not meta.get("extraction") or m < lc["start"] or lc["strength"] <= 0:
            return
        st = self.state; ids = self.ids; n = len(ids)
        if n == 0:
            return
        if lc["timing"] == "circulation":
            elig = (st == CIRC)
        elif lc["timing"] == "post_settling":
            elig = (st == DORM) | (st == OVERT)
        else:
            elig = (st == CIRC) | (st == DORM) | (st == OVERT)
        strength = lc["strength"]

        if lc["do_tag"]:
            cand = elig & (~self.tagged)
            if cand.any():
                idx = np.nonzero(cand)[0]
                hit = U(seed, ids[idx], m, 32) < strength
                if hit.any():
                    self.tagged[idx[hit]] = True
                    self.n_tagged_ever += int(hit.sum())
        if lc["do_pa"]:
            cand = elig & (~self.located)
            if cand.any():
                idx = np.nonzero(cand)[0]
                hit = U(seed, ids[idx], m, 36) < strength
                if hit.any():
                    self.located[idx[hit]] = True
                    self.n_located_ever += int(hit.sum())
        if lc["do_flush"]:
            cand = elig & (~self.leaky)
            if cand.any():
                idx = np.nonzero(cand)[0]
                hit = U(seed, ids[idx], m, 34) < strength
                hi = idx[hit]
                if len(hi):
                    self.leaky[hi] = True
                    self.n_leaky_ever += len(hi)
                    seated = (st[hi] == DORM) | (st[hi] == OVERT)
                    if seated.any():
                        # Documented Levy +4 unfold pulse; not a second Genesis detach.
                        self.d[hi[seated]] *= P["dormancy"]["exit_factor"]
                        self.levy.add("exit", int(seated.sum()))
                        if record:
                            self.events += [(m, "exit", int(ids[i]), int(self.organ[i])) for i in hi[seated]]

        # Moves. Combined mode can apply several; a cell is extracted at most once.
        if lc["do_lure"]:
            if lc["timing"] == "circulation":
                idx = np.nonzero((st == CIRC) & elig)[0]
                self._try_extract(idx, meta.get("lure_idx") or [], S_env, P, seed, m, 30,
                                  mesh, meta, native, record, p=strength)
            elif lc["timing"] != "upstream":
                # post-settling: directed bias out of the niche along flush edges
                idx = np.nonzero(((st == DORM) | (st == OVERT)) & elig)[0]
                self._try_extract(idx, meta.get("flush_idx") or [], S_env, P, seed, m, 31,
                                  mesh, meta, native, record, p=strength)
            else:
                # upstream: niche pull here; CIRC lure competes at the arrest gate
                idx = np.nonzero(((st == DORM) | (st == OVERT)) & elig)[0]
                self._try_extract(idx, meta.get("flush_idx") or [], S_env, P, seed, m, 31,
                                  mesh, meta, native, record, p=strength)
        if lc["do_tag"]:
            idx = np.nonzero(elig & self.tagged & (st != EXTRACTED))[0]
            pool = (meta.get("magnet_idx") or []) + (meta.get("lure_idx") or []) + (meta.get("flush_idx") or [])
            self._try_extract(idx, pool, S_env, P, seed, m, 33, mesh, meta, native, record, p=strength)
        if lc["do_flush"]:
            # Streams are fixed by compartment so whole vs parts stays deterministic.
            idx = np.nonzero(elig & self.leaky & (st != EXTRACTED))[0]
            circ_i = idx[st[idx] == CIRC]
            seat_i = idx[(st[idx] == DORM) | (st[idx] == OVERT)]
            self._try_extract(circ_i, meta.get("lure_idx") or [], S_env, P, seed, m, 35,
                              mesh, meta, native, record, p=strength)
            self._try_extract(seat_i, meta.get("flush_idx") or [], S_env, P, seed, m, 38,
                              mesh, meta, native, record, p=strength)
        if lc["do_pa"]:
            idx = np.nonzero(elig & self.located & (st != EXTRACTED))[0]
            pool = (meta.get("lure_idx") or []) + (meta.get("flush_idx") or [])
            self._try_extract(idx, pool, S_env, P, seed, m, 37, mesh, meta, native, record, p=strength)

    def _plumbing_step(self, m, S_env, cfg, P, lev, seed, mesh, meta, native, record):
        """Sealed-channel transport. Strict no-op (no RNG) unless plumbing is on."""
        pc = _plumbing_cfg(native)
        if (not pc["on"]) or (not meta.get("extraction")) or m < pc["start"] or pc["strength"] <= 0:
            return
        st = self.state
        elig = (st == CIRC) | (st == DORM) | (st == OVERT)
        if pc["timing"] == "post_settling":
            elig = (st == DORM) | (st == OVERT)
        idx = np.nonzero(elig & (st != EXTRACTED) & (st != CLEARED) & (st != LOST))[0]
        if len(idx) == 0:
            return
        pool = (meta.get("lure_idx") or []) + (meta.get("magnet_idx") or []) + (meta.get("flush_idx") or [])
        self._try_plumb(idx, pool, S_env, P, seed, m, 40, mesh, meta, native, record, pc)

    def _try_plumb(self, idx, edge_pool, S_env, P, seed, m, stream, mesh, meta, native, record, pc):
        """Oasis-valve + pressure-gradient hop onto an extract edge, then a seal check."""
        if len(idx) == 0 or not edge_pool:
            return
        st = self.state; ids = self.ids
        live = idx[st[idx] != EXTRACTED]
        if len(live) == 0:
            return
        att = U(seed, ids[live], m, stream) < float(pc["strength"])
        live = live[att]
        if len(live) == 0:
            return
        self.extract_attempts += len(live)
        extract_perm = float(np.clip(pc["strength"], 1e-6, 1.0))
        if pc["oasis"]:
            g = self._gate(live, np.full(len(live), extract_perm), S_env, seed, m, stream, S_env["thr"])
            self.ledger_gate["recycle"] += int((g == 0).sum())
            self.ledger_gate["buffer"] += int((g == 1).sum())
            self.ledger_gate["commit"] += int((g == 2).sum())
            self.plumbing_valve_block += int((g != 2).sum())
            self.plumbing_valve_commit += int((g == 2).sum())
            cm = live[g == 2]
        else:
            self.ledger_gate["commit"] += len(live)
            self.plumbing_valve_commit += len(live)
            cm = live
        if len(cm) == 0:
            return
        locked = [i for i in edge_pool if mesh.edges[i].locked]
        frust = [i for i in edge_pool if not mesh.edges[i].locked]
        hop = float(native.get("hop_from_frustrated", 0.2))
        bc = _bio_cfg(native)
        if bc["rbc"]:
            hop = hop + bc["rbc_deform"] * (1.0 - hop)  # t96u: carrier deforms through narrow passages
            if (not locked) and frust: self.rbc_passes += len(cm)
        if locked:
            ok = np.ones(len(cm), dtype=bool)
            pool = locked
        elif frust:
            ok = U(seed, ids[cm], m, stream + 1) < hop
            pool = frust
        else:
            return
        use = cm[ok]
        if len(use) == 0:
            return
        # Seal check: leak returns the cell to circulation or to its niche.
        leak_u = U(seed, ids[use], m, stream + 3)
        dest_u = U(seed, ids[use], m, stream + 4)
        leak_p = float(pc["leak"])
        stay = []
        for k, cell in enumerate(use):
            cell = int(cell)
            prev = int(st[cell])
            org = int(self.organ[cell])
            if leak_u[k] < leak_p:
                # Leaked transport: not extracted. Prefer circulation on upstream
                # attempts, niches after settling; 50/50 otherwise for seated cells.
                to_circ = (prev == CIRC) or (dest_u[k] < (0.7 if pc["timing"] != "post_settling" else 0.3))
                if to_circ:
                    if prev == OVERT and org >= 0 and _bio_cfg(native)["dna"] and _bio_cfg(native)["dna_ledger"]:
                        # t96u helicase-unzip ledger: an overt occupant leaving to circulation is booked
                        self.organ_unzipped_overt[org] = self.organ_unzipped_overt.get(org, 0) + 1
                    st[cell] = CIRC
                    self.organ[cell] = -1
                    self.edge[cell] = -1
                    self.frust[cell] = False
                    self.plumbing_leaked_circ += 1
                else:
                    # remain seated in the niche if already there; otherwise a
                    # circulating leak into a random already-permitted organ is
                    # not invented — sit back in CIRC.
                    if prev in (DORM, OVERT):
                        st[cell] = prev
                        self.plumbing_leaked_niche += 1
                    else:
                        st[cell] = CIRC
                        self.organ[cell] = -1
                        self.edge[cell] = -1
                        self.frust[cell] = False
                        self.plumbing_leaked_circ += 1
                self.levy.add("fail", 1)
                if record:
                    self.events.append((m, "fail", int(ids[cell]), org))
            else:
                stay.append(cell)
        if not stay:
            return
        stay = np.array(stay, dtype=int)
        upick = U(seed, ids[stay], m, stream + 2)
        for k, cell in enumerate(stay):
            ei = pool[int(upick[k] * len(pool)) % len(pool)]
            self.edge[int(cell)] = int(ei)
            self.frust[int(cell)] = (not mesh.edges[ei].locked)
        for cell in stay:
            prev = int(st[int(cell)])
            org = int(self.organ[int(cell)])
            if prev == CIRC:
                self.extracted_from["circ"] += 1
            elif prev == DORM:
                self.extracted_from["dorm"] += 1
            elif prev == OVERT:
                self.extracted_from["overt"] += 1
                if org >= 0:
                    self.organ_extracted_overt[org] = self.organ_extracted_overt.get(org, 0) + 1
        self.extract_commits += len(stay)
        self.plumbing_sealed += len(stay)
        st[stay] = EXTRACTED
        self.levy.add("extract", len(stay))
        if record:
            self.events += [(m, "extract", int(ids[i]), int(self.organ[i])) for i in stay]

    def _try_extract(self, idx, edge_pool, S_env, P, seed, m, stream, mesh, meta, native, record,
                     p=1.0, attempt_all=False):
        """Oasis-gated move onto a directed extract edge. Prefers lockable polarity paths."""
        if len(idx) == 0 or not edge_pool:
            return
        st = self.state; ids = self.ids
        live = idx[st[idx] != EXTRACTED]
        if len(live) == 0:
            return
        if not attempt_all:
            att = U(seed, ids[live], m, stream) < float(p)
            live = live[att]
        if len(live) == 0:
            return
        self.extract_attempts += len(live)
        extract_perm = float(np.clip(_light_cfg(native)["strength"] or p, 1e-6, 1.0))
        if native.get("light_oasis", True):
            g = self._gate(live, np.full(len(live), extract_perm), S_env, seed, m, stream, S_env["thr"])
            self.ledger_gate["recycle"] += int((g == 0).sum())
            self.ledger_gate["buffer"] += int((g == 1).sum())
            self.ledger_gate["commit"] += int((g == 2).sum())
            # Recycle/buffer = refused move, stay in place (not a clearance).
            cm = live[g == 2]
        else:
            # Ablation: skip Oasis/PrinciplesGate on the extract proposal only.
            self.ledger_gate["commit"] += len(live)
            cm = live
        if len(cm) == 0:
            return
        locked = [i for i in edge_pool if mesh.edges[i].locked]
        frust = [i for i in edge_pool if not mesh.edges[i].locked]
        hop = float(native.get("hop_from_frustrated", 0.2))
        bc = _bio_cfg(native)
        if bc["rbc"]:
            hop = hop + bc["rbc_deform"] * (1.0 - hop)  # t96u: carrier deforms through narrow passages
            if (not locked) and frust: self.rbc_passes += len(cm)
        if locked:
            ok = np.ones(len(cm), dtype=bool)
            pool = locked
        elif frust:
            ok = U(seed, ids[cm], m, stream + 1) < hop
            pool = frust
        else:
            return
        use = cm[ok]
        if len(use) == 0:
            return
        upick = U(seed, ids[use], m, stream + 2)
        for k, cell in enumerate(use):
            ei = pool[int(upick[k] * len(pool)) % len(pool)]
            self.edge[int(cell)] = int(ei)
            self.frust[int(cell)] = (not mesh.edges[ei].locked)
        # Bookkeeping per prior state
        for cell in use:
            prev = int(st[int(cell)])
            org = int(self.organ[int(cell)])
            if prev == CIRC:
                self.extracted_from["circ"] += 1
            elif prev == DORM:
                self.extracted_from["dorm"] += 1
            elif prev == OVERT:
                self.extracted_from["overt"] += 1
                if org >= 0:
                    self.organ_extracted_overt[org] = self.organ_extracted_overt.get(org, 0) + 1
        self.extract_commits += len(use)
        st[use] = EXTRACTED
        self.levy.add("extract", len(use))
        if record:
            self.events += [(m, "extract", int(ids[i]), int(self.organ[i])) for i in use]


def _light_cfg(native):
    """Resolve light-transport flags. Off unless native['light'] is true."""
    mode = str(native.get("light_mode") or "off")
    timing = str(native.get("light_timing") or "upstream")
    on = bool(native.get("light", False)) and mode not in ("off", "", "none")
    start = native.get("light_start_month")
    if start is None:
        start = 61 if timing == "post_settling" else 1
    return dict(on=on, mode=mode, timing=timing, start=int(start),
                strength=float(native.get("light_strength", 0.0) or 0.0),
                do_lure=mode in ("lure", "combined"),
                do_tag=mode in ("tag_magnet", "combined"),
                do_flush=mode in ("flush", "combined"),
                do_pa=mode in ("photoacoustic", "combined"))



def _plumbing_cfg(native):
    """Resolve plumbing flags. Off unless native['plumbing'] is true. No side effects."""
    on = bool(native.get("plumbing", False))
    timing = str(native.get("plumbing_timing") or "upstream")
    start = native.get("plumbing_start_month")
    if start is None:
        start = 61 if timing == "post_settling" else 1
    leak0 = float(native.get("plumbing_leak", 0.0) or 0.0)
    strength = float(native.get("plumbing_strength", 0.0) or 0.0)
    n_stages = max(1, int(native.get("plumbing_stages", 1) or 1))
    seal = float(np.clip(native.get("plumbing_seal", 1.0) or 0.0, 0.0, 1.0))
    magnet = bool(native.get("plumbing_magnet", False))
    oasis = bool(native.get("plumbing_oasis", True))
    # Higher pressure and a poorer seal raise leak; staged isolation lowers it.
    leak_eff = leak0 * (1.0 - 0.5 * seal) * (1.0 + 0.5 * strength) / float(n_stages)
    if magnet:
        leak_eff *= 0.5  # labeled directional hold in the channel, not a therapy claim
    bc = _bio_cfg(native)
    if bc["rbc"]:
        leak_eff *= (1.0 - bc["rbc_seal"])  # t96u: deformable carrier fills the channel bore
    leak_eff = float(np.clip(leak_eff, 0.0, 0.95))
    return dict(on=on, timing=timing, start=int(start), leak=leak_eff, leak0=leak0,
                strength=strength, n_stages=n_stages, seal=seal, magnet=magnet,
                oasis=oasis)


def _bio_cfg(native):
    """t96u structural analogies, each OFF by default and a strict no-op (no RNG) when off.
    zipper: teeth = niche polarity edges; tolerance = max cell/niche size mismatch before a tooth
            skips (cell sits frustrated); material = mismatch noise; attach = anchoring at seating;
            slider = monthly re-closing of skipped teeth; spring x levy_gain; tape: damper alpha / tape.
    dna:    complementary pairing = polarity locks; reanneal = frustrated occupants re-pair on a
            locked edge (delta reconciliation); proofread = PrinciplesGate mismatch check before a
            colonization commit; unzip ledger = book overt cells leaked back to circulation.
    mrna:   transient message: Levy pulse memory decays at mrna_decay (Nexus record persists).
    rbc:    deformable carrier in transport channels (light/plumbing extract edges): raises passage
            through frustrated channel edges and lowers seal leak.
    wbc:    patrol + Oasis recognition: patrolled dormant cells that Oasis would recycle are cleared.
    Speculative structural mapping only; no biological model or claim."""
    z = bool(native.get("zipper", False)); d = bool(native.get("dna", False))
    return dict(
        zipper=z, zip_tol=float(native.get("zip_tolerance", 0.5)), zip_material=float(native.get("zip_material", 1.0)),
        zip_attach=float(native.get("zip_attach", 1.0)), zip_slider=float(native.get("zip_slider", 0.0)),
        zip_size=float(native.get("zip_size", 1.0)), zip_spring=float(native.get("zip_spring", 1.0)),
        zip_tape=float(native.get("zip_tape", 1.0)),
        dna=d, dna_reanneal=float(native.get("dna_reanneal", 0.1)), dna_proof=bool(native.get("dna_proofread", True)),
        dna_proof_thr=float(native.get("dna_proof_thr", native.get("zip_tolerance", 0.5))),
        dna_ledger=bool(native.get("dna_unzip_ledger", True)),
        mrna=bool(native.get("mrna", False)), mrna_decay=float(native.get("mrna_decay", 0.7)),
        rbc=bool(native.get("rbc", False)), rbc_deform=float(native.get("rbc_deform", 0.5)), rbc_seal=float(native.get("rbc_seal", 0.5)),
        wbc=bool(native.get("wbc", False)), wbc_patrol=float(native.get("wbc_patrol", 0.05)),
        wbc_start=int(native.get("wbc_start_month", 1)))


def _mismatch(part, idx, perm_o, bc, seed, m, stream):
    """Zipper size mismatch between a cell (fit) and its niche tooth (organ permissiveness)."""
    mm = bc["zip_size"] * np.abs(part.fit[idx] - perm_o)
    if bc["zip_material"] < 1.0:
        mm = mm + (1.0 - bc["zip_material"]) * U(seed, part.ids[idx], m, stream)
    return mm


def make_cfg(name, P):
    c = P["cancers"][name]; organs = list(c["organ_permissiveness"]); base = np.array([c["organ_permissiveness"][o] for o in organs])
    pref_idx = int(np.argmax(base))
    def perm_eff(lev):
        p = base * lev["organ_perm_scale"]; p = p.copy(); p[pref_idx] *= lev["pref_perm_scale"]; return np.clip(p, 1e-6, 1.0)
    return dict(name=name, organs=organs, perm_eff=perm_eff, pref_idx=pref_idx, preferred=organs[pref_idx], seed=c["seed"])


def make_env(S, P, lev, pressure=0.0, damper_on=True, nexus_state=None):
    n, s = S
    mean_epi = (s / n / 1e6) if n else Genesis.epi_origin
    rest = n > P["homeostasis"]["rest_load"]
    H = max(0.2, min(1.0, 1 - n / (2.0 * P["homeostasis"]["rest_load"])))
    vt = lev["valuation_threshold"] if lev["valuation_threshold"] is not None else P["salience"]["valuation_threshold"]
    thr = vt + (P["homeostasis"]["rest_bump"] if rest else 0.0)
    if damper_on:
        # Real damped feedback: niche pressure (from last month's occupancy delta) raises the
        # admission threshold, the same way launch dampers meter force spikes. Not cosmetic.
        thr = thr + float(pressure)
    w = np.array(P["salience"]["weights_tension"] if (1 - H) > P["salience"]["tension_hi"] else P["salience"]["weights"]); w = w / w.sum()
    env = dict(mean_epi=mean_epi, H=H, rest=rest, thr=thr, w=w, integrated=False)
    if nexus_state is not None:
        env.update(integrated=True, principles=nexus_state.get("principles", True),
                   frust_level=nexus_state.get("frust_level", 0.0))
    return env


def shed_schedule(cfg, seed, P, lev, base_lev):
    out = []
    for m in range(1, P["months"] + 1):
        L = lever_at(base_lev, lev, m)
        u = float(U(seed, np.array([0xFFFFFF]), m, 99)[0])
        out.append(poisson_inv(u, P["shed_rate"] * L["shed_mult"]))
    return out


def _native_flags(P, overrides=None):
    n = dict(P.get("native") or {})
    if overrides:
        n.update(overrides)
    return n


def _adapt_niche(mesh, meta, parts, native, n_organs, month, seed):
    """Heat-driven self-repair of frustrated niche edges, and rebuild after clearance.

    Heat is the month's fail+colonize+exit activity per organ. In a melt window the
    niche can mark a frustrated edge repaired (lockable path). After dormant
    clearance, rebuild_rate can restore a repaired edge to frustrated (web regrowth).
    """
    if not native.get("adaptive_niche", True):
        return
    heat_org = np.zeros(n_organs)
    n_cleared_dorm = 0
    for p in parts:
        n_cleared_dorm += p.cleared_by["dorm"]
        for k, v in p.heat.items():
            if isinstance(k, tuple):
                heat_org[int(k[1])] += v
            else:
                heat_org[int(k)] += v
    # normalize roughly into [0, 1+]
    h = heat_org / (1.0 + heat_org)
    melt_lo = float(native.get("melt_lo", 0.15)); melt_hi = float(native.get("melt_hi", 0.85))
    repair_rate = float(native.get("repair_rate", 0.0))
    rebuild_rate = float(native.get("rebuild_rate", 0.0))
    for o in range(n_organs):
        if melt_lo <= h[o] <= melt_hi and repair_rate > 0:
            u = float(U(seed, np.array([1000 + o], dtype=np.uint64), month, 70)[0])
            if u < repair_rate:
                cands = [i for i in meta["niche_edge_idx"][o] if (not mesh.edges[i].locked) and (not mesh.edges[i].repaired)]
                if cands:
                    mesh.edges[cands[int(u * 1e6) % len(cands)]].repaired = True
        # rebuild after some dorm clearance (feather-regrowth mapping)
        if rebuild_rate > 0 and n_cleared_dorm > 0:
            u2 = float(U(seed, np.array([2000 + o], dtype=np.uint64), month, 71)[0])
            if u2 < rebuild_rate:
                cands = [i for i in meta["niche_edge_idx"][o] if mesh.edges[i].repaired]
                if cands:
                    e = mesh.edges[cands[int(u2 * 1e6) % len(cands)]]
                    e.repaired = False
    mesh.process_polarities()
    # Refresh occupancy flags to match the updated mesh
    for p in parts:
        occ = p.edge >= 0
        if occ.any():
            for i in np.nonzero(occ)[0]:
                ei = int(p.edge[i])
                if 0 <= ei < len(mesh.edges):
                    p.frust[i] = ((not mesh.edges[ei].locked) or bool(p.skip[i])) and (p.state[i] == DORM)


def run(name, seed, P, lever=None, mode="whole", K=4, record=False, isolate=None, sig=False,
        native_overrides=None):
    """mode: 'whole' or 'decomposed' (K independent parts, recombined each month)."""
    lev = dict(NEUTRAL); lev.update(lever or {}); base_lev = dict(NEUTRAL)
    cfg = make_cfg(name, P); sd = seed if seed is not None else cfg["seed"]
    native = _native_flags(P, native_overrides)
    extraction = bool(native.get("light", False) or native.get("extraction", False) or native.get("plumbing", False))
    extraction_coloring = str(native.get("extraction_coloring") or "preserve")
    mesh, meta = build_system_mesh(cfg["organs"], hoop_n=int(native.get("hoop_n", 8)),
                                   circulation_nodes=int(native.get("circulation_nodes", 8)),
                                   include_loops=bool(native.get("include_loops", True)),
                                   extraction=extraction,
                                   extraction_coloring=extraction_coloring)
    nshed = shed_schedule(cfg, sd, P, lev, base_lev)
    ids, sm = [], []
    for m, n in enumerate(nshed, start=1):
        for j in range(n): ids.append(m * 4096 + j); sm.append(m)
    ids = np.array(ids, dtype=np.uint64); sm = np.array(sm, dtype=np.int32)
    nparts = 1 if mode == "whole" else K
    pidx = (sm + (ids % 4096).astype(np.int32)) % nparts if len(ids) else np.zeros(0, dtype=int)
    parts = [Part(k, ids[pidx == k], sm[pidx == k], sd, P) for k in range(nparts)]
    nexus = Nexus(); genesis = Genesis(); transcriber = Transcriber(); dictator = Dictator(transcriber)
    nexus.register("genesis", genesis.mirror(name, sd))
    key = (tuple(cfg["organs"]), bool(native.get("include_loops", True)), extraction, extraction_coloring)
    if key not in _INV_CACHE:
        _INV_CACHE[key] = mesh_inversion_holds(cfg["organs"], hoop_n=int(native.get("hoop_n", 8)),
                                               circulation_nodes=int(native.get("circulation_nodes", 8)),
                                               include_loops=bool(native.get("include_loops", True)),
                                               extraction=extraction,
                                               extraction_coloring=extraction_coloring)
    meta["inversion_holds"] = _INV_CACHE[key]
    nexus.register("mesh", dict(n_nodes=meta["n_nodes"], n_edges=meta["n_edges"],
                                n_frustrated0=meta["n_frustrated0"], inversion=meta["inversion_holds"]))
    S = (0, 0); pressure = 0.0
    damper_on = bool(native.get("damped_reconcile", True))
    alpha = float(native.get("damper_alpha", 0.35))
    gain = float(native.get("damper_gain", 0.08))
    integrated = bool(native.get("integrated", True))
    principles_on = bool(native.get("principles_gate", True))
    levy_feedback = bool(native.get("levy_feedback", True))
    levy_gain = float(native.get("levy_gain", 1.0))
    _bc = _bio_cfg(native)
    if _bc["zipper"]:
        levy_gain *= _bc["zip_spring"]                # spring tension -> Levy pulse gain
        alpha = alpha / max(_bc["zip_tape"], 1e-9)    # tape stability -> smoother damper
    levy_alpha = _bc["mrna_decay"] if _bc["mrna"] else alpha
    levy_ledger = LevyLedger(P["levy_weights"])
    prev_counts = {k: 0 for k in KINDS}
    n_edges = max(1, len(mesh.edges))
    nexus.register("state", dict(n_active=0, levy_pulse=0.0, frust_level=sum(1 for e in mesh.edges if not e.locked) / n_edges,
                                 pressure=0.0, principles=principles_on, genesis_closed=True))
    frust_series = []; levy_pulses = []; pressure_series = []
    for m in range(1, P["months"] + 1):
        L = lever_at(base_lev, lev, m)
        env = make_env(S, P, L, pressure=pressure, damper_on=damper_on,
                       nexus_state=(nexus.registry["state"] if integrated else None))
        for p in parts: p.step(m, env, cfg, P, L, sd, mesh, meta, native, record)
        # Nexus recombination of the parts (state reduction -> whole)
        tot_n = tot_s = 0
        for p in parts:
            n, s = p.summary()
            if isolate and p.pid == isolate[0] and isolate[1] <= m <= isolate[2]:
                nexus.metrics["isolations"] += 1; continue
            tot_n += n; tot_s += s
        target = P["homeostasis"]["rest_load"]
        delta = (tot_n - target) / max(target, 1)
        spike = max(0.0, delta)
        levy_spike = 0.0; pulse = 0.0
        if integrated:
            # Dictator streams this month's events -> Transcriber -> Levy assesses the entries
            cur = {k: sum(p.levy.counts[k] for p in parts) for k in KINDS}
            month_counts = {k: cur[k] - prev_counts[k] for k in KINDS}; prev_counts = cur
            entries = dictator.stream(m, month_counts)
            pulse = levy_ledger.assess(entries)
            ema = levy_ledger.ema if levy_ledger.ema is not None else pulse
            if levy_feedback and ema > 0:
                levy_spike = max(0.0, (pulse - ema) / ema)
            levy_ledger.ema = (1.0 - levy_alpha) * ema + levy_alpha * pulse
        # Delta reconciliation: damped occupancy spike + (integrated) Levy pulse spike
        pressure = (1.0 - alpha) * pressure + alpha * gain * (spike + levy_gain * levy_spike)
        nexus.metrics["deltas"] += 1
        S = (tot_n, tot_s); nexus.telemeter(m, dict(n_active=S[0], sum_epi_int=S[1]))
        _adapt_niche(mesh, meta, parts, native, len(cfg["organs"]), m, sd)
        n_unlocked = sum(1 for e in mesh.edges if not e.locked)
        frust_series.append(n_unlocked); levy_pulses.append(pulse); pressure_series.append(pressure)
        if integrated:
            # Mesh consensus + Genesis closure registered on the Nexus; next month's env reads it
            n_states = sum(int((p.state != PENDING).sum()) for p in parts)
            n_detach = sum(p.levy.counts["detach"] for p in parts)
            closure = genesis.mirror(name, sd); closure["closed"] = (n_states == n_detach)
            nexus.register("state", dict(n_active=tot_n, levy_pulse=pulse, frust_level=n_unlocked / n_edges,
                                         pressure=pressure, principles=principles_on, genesis_closed=closure["closed"]))
    if record:
        for p in parts:
            for ev in p.events:
                month, kind, cid, org = ev
                on = cfg["organs"][org] if org is not None and org >= 0 else None
                if kind in ("colonize", "exit", "recycle"):
                    dictator.chronicle(month, kind, cid, on)
    res = recombine(parts, cfg, P, nexus, genesis, sd, len(ids), record, name, sig, mesh, meta, frust_series, pressure)
    res.update(integrated=integrated, principles_gate=principles_on, levy_feedback=levy_feedback,
               pipeline_levy=float(levy_ledger.total_weight),
               pipeline_levy_ok=(not integrated) or abs(levy_ledger.total_weight - res["levy"]) < 1e-6,
               transcriber_entries=len(transcriber.chronicles), transcriber_critical=len(transcriber.anonymous_log),
               genesis_closed=bool(nexus.registry["state"].get("genesis_closed", True)),
               pressure_max=float(max(pressure_series) if pressure_series else 0.0),
               pressure_mean=float(np.mean(pressure_series) if pressure_series else 0.0),
               adapted=sum(p.adapted for p in parts),
               pg_score_mod=sum(p.pg_score_mod for p in parts), pg_veto=sum(p.pg_veto for p in parts),
               pg_proof=sum(p.pg_proof for p in parts), zip_skips=sum(p.zip_skips for p in parts),
               zip_unanchored=sum(p.zip_unanchored for p in parts), zip_rezips=sum(p.zip_rezips for p in parts),
               dna_reannealed=sum(p.dna_reannealed for p in parts),
               dna_unzipped_overt=sum(sum(p.organ_unzipped_overt.values()) for p in parts),
               wbc_patrolled=sum(p.wbc_patrolled for p in parts), wbc_cleared=sum(p.wbc_cleared for p in parts),
               rbc_passes=sum(p.rbc_passes for p in parts))
    return res


def recombine(parts, cfg, P, nexus, genesis, seed, n_shed, record, name, sig, mesh, meta, frust_series, pressure):
    W = P["levy_weights"]
    counts = {k: sum(p.levy.counts[k] for p in parts) for k in KINDS}
    levy_running = sum(p.levy.total() for p in parts)
    levy_counts = sum(W[k] * counts[k] for k in KINDS)
    state = np.concatenate([p.state for p in parts]) if parts else np.zeros(0, dtype=np.int8)
    d = np.concatenate([p.d for p in parts]) if parts else np.zeros(0)
    organ = np.concatenate([p.organ for p in parts]) if parts else np.zeros(0, dtype=np.int16)
    frust_cell = np.concatenate([p.frust for p in parts]) if parts else np.zeros(0, dtype=np.bool_)
    n_circ = int((state == CIRC).sum()); n_dorm = int((state == DORM).sum()); n_overt = int((state == OVERT).sum())
    n_clr = int((state == CLEARED).sum()); n_lost = int((state == LOST).sum())
    n_extracted = int((state == EXTRACTED).sum())
    dorm_high = int(((state == DORM) & (d > P["dormancy"]["high_cutoff"])).sum())
    dorm_frust = int(((state == DORM) & frust_cell).sum())
    col_org = {}; heat_col = {}; ext_overt_org = {}
    extracted_from = dict(circ=0, dorm=0, overt=0)
    n_tagged_ever = n_leaky_ever = n_located_ever = extract_attempts = extract_commits = 0
    for p in parts:
        for o, c in p.organ_colonized.items(): col_org[o] = col_org.get(o, 0) + c
        for k, v in p.heat.items():
            if isinstance(k, tuple): heat_col[k[1]] = heat_col.get(k[1], 0) + v
        for o, c in getattr(p, "organ_extracted_overt", {}).items():
            ext_overt_org[o] = ext_overt_org.get(o, 0) + c
        for o, c in getattr(p, "organ_unzipped_overt", {}).items():
            ext_overt_org[o] = ext_overt_org.get(o, 0) + c
        for k in extracted_from:
            extracted_from[k] += getattr(p, "extracted_from", {}).get(k, 0)
        n_tagged_ever += int(getattr(p, "n_tagged_ever", 0))
        n_leaky_ever += int(getattr(p, "n_leaky_ever", 0))
        n_located_ever += int(getattr(p, "n_located_ever", 0))
        extract_attempts += int(getattr(p, "extract_attempts", 0))
        extract_commits += int(getattr(p, "extract_commits", 0))
    plumbing_leaked_circ = sum(int(getattr(p, "plumbing_leaked_circ", 0)) for p in parts)
    plumbing_leaked_niche = sum(int(getattr(p, "plumbing_leaked_niche", 0)) for p in parts)
    plumbing_valve_block = sum(int(getattr(p, "plumbing_valve_block", 0)) for p in parts)
    plumbing_valve_commit = sum(int(getattr(p, "plumbing_valve_commit", 0)) for p in parts)
    plumbing_sealed = sum(int(getattr(p, "plumbing_sealed", 0)) for p in parts)
    census_org = {int(o): int(((state == OVERT) & (organ == o)).sum()) for o in set(organ[state == OVERT].tolist()) if len(state)}
    # Current overt occupancy = cumulative colonize minus overt-to-extract; heat stays cumulative.
    agree = {o: (census_org.get(o, 0) == col_org.get(o, 0) - ext_overt_org.get(o, 0)
                 and int(heat_col.get(o, 0)) == col_org.get(o, 0))
             for o in set(col_org) | set(census_org) | set(ext_overt_org)}
    consensus_ok = all(agree.values()) if agree else True
    census_ok = (n_shed == n_circ + n_dorm + n_overt + n_clr + n_lost + n_extracted) and counts["detach"] == n_shed
    levy_ok = abs(levy_running - levy_counts) < 1e-9
    nexus.metrics["reconciliations"] += 1
    pref = cfg["pref_idx"]
    overt_pref = col_org.get(pref, 0)
    fc = mesh.counts()
    n_frust_circ = sum(1 for e in mesh.edges if (not e.locked) and e.kind in ("circ", "shed"))
    n_frust_niche = sum(1 for e in mesh.edges if (not e.locked) and e.kind in ("spoke", "hoop", "return", "approach", "organ_hub"))
    n_frust_extract = sum(1 for e in mesh.edges if (not e.locked) and e.kind in ("lure", "magnet", "flush"))
    n_lock_extract = sum(1 for e in mesh.edges if e.locked and e.kind in ("lure", "magnet", "flush"))
    n_extract_edges = sum(1 for e in mesh.edges if e.kind in ("lure", "magnet", "flush"))
    res = dict(cancer=name, seed=seed, preferred=cfg["preferred"], shed=n_shed, cleared=n_clr, lost_failed_seeding=n_lost,
               circ_alive=n_circ, dorm_alive=n_dorm, dorm_high=dorm_high, overt=n_overt, overt_preferred=overt_pref,
               overt_other=n_overt - overt_pref, extracted=n_extracted,
               extracted_circ=extracted_from["circ"], extracted_dorm=extracted_from["dorm"], extracted_overt=extracted_from["overt"],
               extract_yield=(n_extracted / n_shed) if n_shed else 0.0,
               extract_attempts=extract_attempts, extract_commits=extract_commits,
               n_tagged_ever=n_tagged_ever, n_leaky_ever=n_leaky_ever, n_located_ever=n_located_ever,
               levy=levy_running,
               ev_clear=counts["clear"], ev_detach=counts["detach"], ev_fail=counts["fail"], ev_colonize=counts["colonize"], ev_exit=counts["exit"], ev_extract=counts.get("extract", 0),
               clr_circ=sum(p.cleared_by["circ"] for p in parts), clr_dorm=sum(p.cleared_by["dorm"] for p in parts),
               clr_recycle=sum(p.cleared_by["recycle"] for p in parts),
               gate_recycle=sum(p.ledger_gate["recycle"] for p in parts), gate_buffer=sum(p.ledger_gate["buffer"] for p in parts),
               gate_commit=sum(p.ledger_gate["commit"] for p in parts),
               census_ok=census_ok, levy_ok=levy_ok, consensus_ok=consensus_ok, parts=len(parts),
               # native mesh observables
               n_mesh_edges=fc["n_edges"], n_locked=fc["n_locked"],
               n_frustrated=fc["n_frustrated"], n_frustrated0=meta["n_frustrated0"],
               n_repaired=fc["n_repaired"], n_frustrated_mean=float(np.mean(frust_series) if frust_series else fc["n_frustrated"]),
               dorm_on_frustrated=dorm_frust,
               inversion_holds=bool(meta["inversion_holds"]),
               damper_pressure=float(pressure),
               include_loops=bool(meta["include_loops"]),
               extraction_mesh=bool(meta.get("extraction", False)),
               n_frustrated_circ=int(n_frust_circ), n_frustrated_niche=int(n_frust_niche),
               n_frustrated_extract=int(n_frust_extract), n_locked_extract=int(n_lock_extract),
               n_extract_edges=int(n_extract_edges),
               plumbing_leaked_circ=plumbing_leaked_circ,
               plumbing_leaked_niche=plumbing_leaked_niche,
               plumbing_leaked=plumbing_leaked_circ + plumbing_leaked_niche,
               plumbing_valve_block=plumbing_valve_block,
               plumbing_valve_commit=plumbing_valve_commit,
               plumbing_sealed=plumbing_sealed)
    if sig:
        import hashlib
        allids = np.concatenate([p.ids for p in parts]); o = np.argsort(allids, kind="stable")
        res["_sig"] = hashlib.sha1(allids[o].tobytes() + state[o].tobytes() + organ[o].tobytes() + np.rint(d[o] * 1e9).astype(np.int64).tobytes()).hexdigest()
    if record:
        evs = sorted([e for p in parts for e in p.events], key=lambda e: (e[0], e[2], e[1]))
        res["_events"] = evs
        kmap = {"recycle": "clear"}
        res["_levy_from_events"] = sum(W[kmap.get(k, k)] for _, k, _, _ in evs)
        names = {i: o for i, o in enumerate(cfg["organs"])}
        res["_chronicle"] = [f"[Dictator t={m:03d}] cell {i} {k.upper()}" + (f" @{names[o]}" if o >= 0 else "")
                             for m, k, i, o in evs if k in ("colonize", "exit", "recycle")]
        shed_ids = set(i for _, k, i, _ in evs if k == "detach")
        res["_genesis_closed"] = all(i in shed_ids for _, _, i, _ in evs)
    return res


RECON_KEYS = ["shed", "cleared", "lost_failed_seeding", "circ_alive", "dorm_alive", "dorm_high", "overt", "overt_preferred",
              "extracted", "levy", "ev_clear", "ev_detach", "ev_fail", "ev_colonize", "ev_exit", "ev_extract"]


def reconcile_whole_vs_parts(a, b):
    """Accounting-layer check: decomposed vs whole-system. Distinct from the in-step damped feedback."""
    delta = {k: b[k] - a[k] for k in RECON_KEYS}
    delta["sig_equal"] = (a.get("_sig") == b.get("_sig"))
    delta["consistent"] = all(delta[k] == 0 for k in RECON_KEYS) and delta["sig_equal"]
    return delta
