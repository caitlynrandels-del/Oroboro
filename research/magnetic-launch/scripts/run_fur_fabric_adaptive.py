#!/usr/bin/env python3
# CONJUNCTIVE (audit 2026-11-27): one loop Genesis -> Nexus -> Oasis admission -> PrinciplesGate
# -> NaCl consensus -> Dictator -> Transcriber -> Levy -> damped deterministic recombine.
# Speculative modeling only. No engineering, flight, siting, power or operational claims.
"""Fur / fabric (furn) dynamics with an adaptive polygon mesh.

Speculative modeling only. Not an engineering design, flight plan, or siting
recommendation. No operational claims. Pixar citations are only papers and
talks actually fetched this turn from research.pixar.com (and, for the 1998
cloth-integration model Fizt is built on, the CMU-hosted Baraff & Witkin PDF).

Standalone fur/fabric exploration plus adaptive surfaces on the recycled
kite, fishing-line, STRAW, and light-sail configurations.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_goal_seek_recycle as G
import run_redstone_repeater_comparator as R
import run_guidance_kite_line_straw as KG
import run_light_sail_push as LS

sys.path.insert(0, __import__("os").environ.get("OASIS_BRIDGE", "/workspace/oasis-build/SkyAriOasis/Bridge"))  # Oasis bridge (sky-ari-ai build) on the project computer
import oasis_core as core  # noqa: E402

OUT = G.OUT
MU, RE, G_STD = G.MU_EARTH, G.R_EARTH, G.G_STD
LEO = G.LEO_ALT_M
SIGMA_SB = getattr(LS, "SIGMA_SB", 5.670374419e-8)

LEVY = {
    "genesis": 0, "admit_path": 1, "suppress_path": 2, "refine": 3,
    "coarsen": 2, "block_refine": 2, "smooth": 1, "untangle": 4,
    "hold_shape": 2, "orbit_lock": 14, "fail": 2, "damper_reconcile": 4,
    "reef": 3, "unreef": 3,
}

class AdaptiveFurn:
    """Layered cloth sheet + keyhair strands with Oroboro-gated remeshing.

    Cloth: a rectangular mesh, leading edge pinned, stretch-stiff / bend-soft
    (the anisotropy Fizt inherits from Baraff & Witkin 1998, as described by
    Kim & Eberle 2022). Target edge length follows Waggoner & de Goes 2022
    (L between Lmin and Lmax), but the painted weight is replaced by a live
    Oroboro signal of local tension, dynamic pressure, speed, and force.

    Fur: keyhairs (Petrovic, Henne & Anderson, Pixar TM #06-08) with a mid
    interpolant layer (Montell, de Goes & Brooks 2022 style-guide / sim-guide
    layering). Hair-hair response is a coarse density grid plus velocity
    smoothing (same memo). Shape-hold springs restore a rest groom after
    wind (Iben, Brooks & Bolwyn 2019). Nearby-strand repulsion is a
    history-free untangle step in the spirit of Baraff, Witkin & Kass 2003.
    """

    def __init__(self, mode="adaptive_gated", width=1.0, height=0.6,
                 n_span=8, n_chord=6, n_hairs=24, n_seg=6,
                 Lmin=0.04, Lmax=0.20, sigma_kg_m2=0.05, cd=1.0, cl=0.0,
                 k_stretch=24.0, k_bend=0.8, k_hold=18.0, k_hair_bend=4.0,
                 k_hair_stretch=40.0, c_damp=1.6, c_smooth=4.0,
                 hair_cd=1.0, hair_d=0.001, hair_len=0.25, seed=1):
        self.mode = mode
        self.width = float(width)
        self.height = float(height)
        self.Lmin = float(Lmin)
        self.Lmax = float(Lmax)
        self.sigma = float(sigma_kg_m2)
        self.cd = float(cd)
        self.cl = float(cl)
        self.k_stretch = k_stretch
        self.k_bend = k_bend
        self.k_hold = k_hold
        self.k_hair_bend = k_hair_bend
        self.k_hair_stretch = k_hair_stretch
        self.c_damp = c_damp
        self.c_smooth = c_smooth
        self.hair_cd = hair_cd
        self.hair_d = hair_d
        self.hair_len = hair_len
        self.rng = np.random.default_rng(seed)
        self.area_scale = 1.0
        if mode == "fixed_coarse":
            n_span, n_chord, n_hairs, n_seg = 5, 4, 12, 4
        elif mode == "fixed_fine":
            n_span, n_chord, n_hairs, n_seg = 14, 10, 48, 8
        self._build_cloth(n_span, n_chord)
        self._build_fur(n_hairs, n_seg)
        self.grid_n = 8 if mode != "fixed_fine" else 16
        self.stats = {
            "n_split": 0, "n_collapse": 0, "n_block": 0, "n_admit": 0,
            "n_untangle": 0, "n_smooth": 0, "n_hold": 0,
            "W_aero_J": 0.0, "W_damp_J": 0.0, "W_smooth_J": 0.0,
            "E_stretch_peak": 0.0, "E_hold_peak": 0.0,
            "tip_rms": 0.0, "tip_peak": 0.0, "tangle_events": 0,
            "dof_sum": 0.0, "dof_n": 0, "open_mean": 0.0, "open_n": 0,
        }
        self.trace_t = []
        self.trace_tip = []
        self.trace_dof = []
        self.trace_E = []
        self.trace_open = []
        self.trace_grid = []

    def _build_cloth(self, n_span, n_chord):
        xs = np.linspace(0.0, self.height, n_chord)
        ys = np.linspace(-0.5 * self.width, 0.5 * self.width, n_span)
        X, Y = np.meshgrid(xs, ys, indexing="ij")
        Z = np.zeros_like(X)
        self.n_chord = n_chord
        self.n_span = n_span
        self.rest = np.stack([X, Y, Z], axis=-1)
        self.rest[:, :, 2] = 0.01 * (X / max(self.height, 1e-9)) * (
            1.0 - (2 * Y / max(self.width, 1e-9)) ** 2
        )
        self.groom = self.rest.copy()
        self.pos = self.rest.copy()
        self.vel = np.zeros_like(self.pos)
        self.pin = np.zeros((n_chord, n_span), dtype=bool)
        self.pin[0, :] = True
        self._mass_from_area()

    def _mass_from_area(self):
        area = self.width * self.height * max(self.area_scale, 0.05)
        n = self.n_chord * self.n_span
        self.vertex_mass = max(area * self.sigma, 1e-4) / n

    def _build_fur(self, n_hairs, n_seg):
        roots_y = np.linspace(-0.45 * self.width, 0.45 * self.width, max(n_hairs, 1))
        roots = np.zeros((max(n_hairs, 0), 3))
        if n_hairs <= 0:
            self.hair_rest = np.zeros((0, n_seg + 1, 3))
            self.hair_pos = self.hair_rest.copy()
            self.hair_vel = np.zeros_like(self.hair_rest)
            self.n_hairs = 0
            self.n_seg = n_seg
            self.hair_mass = 2.0e-5
            return
        roots[:, 0] = 0.02
        roots[:, 1] = roots_y
        s = np.linspace(0.0, 1.0, n_seg + 1)
        rest = np.zeros((n_hairs, n_seg + 1, 3))
        rest[:, :, 0] = roots[:, 0][:, None] + self.hair_len * s[None, :] * 0.3
        rest[:, :, 1] = roots[:, 1][:, None]
        rest[:, :, 2] = -self.hair_len * s[None, :] * 0.95
        self.hair_rest = rest
        self.hair_groom = rest.copy()
        self.hair_pos = rest.copy()
        self.hair_vel = np.zeros_like(rest)
        self.n_hairs = n_hairs
        self.n_seg = n_seg
        self.hair_mass = 2.0e-5

    def dof(self):
        cloth = int(self.n_chord * self.n_span * 3)
        fur = int(self.n_hairs * (self.n_seg + 1) * 3)
        mid = fur
        return {"cloth": cloth, "keyhairs": fur, "mid_interpolant": mid,
                "total_sim": cloth + fur, "grid_n": int(self.grid_n)}

    def effective_area(self):
        return self.width * self.height * max(0.0, self.area_scale)

    def _neighbor_avg_vel(self):
        v = self.vel
        acc = np.zeros_like(v)
        cnt = np.zeros((self.n_chord, self.n_span, 1))
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            i0, i1 = max(0, di), self.n_chord + min(0, di)
            j0, j1 = max(0, dj), self.n_span + min(0, dj)
            acc[i0:i1, j0:j1] += v[i0 - di:i1 - di, j0 - dj:j1 - dj]
            cnt[i0:i1, j0:j1] += 1.0
        return acc / np.maximum(cnt, 1.0)

    def _cloth_forces(self, rho, wind, dt):
        p = self.pos
        v = self.vel
        F = np.zeros_like(p)
        E_s = 0.0
        for axis, kfac in ((0, 1.0), (1, 0.55)):
            if axis == 0:
                d = p[1:] - p[:-1]
                r0 = self.rest[1:] - self.rest[:-1]
            else:
                d = p[:, 1:] - p[:, :-1]
                r0 = self.rest[:, 1:] - self.rest[:, :-1]
            L = np.linalg.norm(d, axis=-1, keepdims=True)
            L0 = np.maximum(np.linalg.norm(r0, axis=-1, keepdims=True), 1e-9)
            stretch = L - L0
            dirn = d / np.maximum(L, 1e-9)
            f = -self.k_stretch * kfac * stretch * dirn
            E_s += 0.5 * float(np.sum(self.k_stretch * kfac * stretch[..., 0] ** 2))
            if axis == 0:
                F[:-1] -= f
                F[1:] += f
            else:
                F[:, :-1] -= f
                F[:, 1:] += f
        tgt = self._hold_target(rho, wind)
        hold = -self.k_hold * (p - tgt)
        F += hold
        E_h = 0.5 * float(np.sum(self.k_hold * np.sum((p - self.groom) ** 2, axis=-1)))
        lap = np.zeros_like(p)
        lap[1:-1] += (p[:-2] - 2 * p[1:-1] + p[2:])
        lap[:, 1:-1] += (p[:, :-2] - 2 * p[:, 1:-1] + p[:, 2:])
        F += -self.k_bend * lap
        W_aero = 0.0
        if rho > 0 and self.area_scale > 0 and self.n_chord > 1 and self.n_span > 1:
            e1 = p[1:, :-1] - p[:-1, :-1]
            e2 = p[:-1, 1:] - p[:-1, :-1]
            nrm = np.cross(e1, e2)
            area = 0.5 * np.linalg.norm(nrm, axis=-1, keepdims=True)
            nhat = nrm / np.maximum(np.linalg.norm(nrm, axis=-1, keepdims=True), 1e-12)
            vface = 0.25 * (v[:-1, :-1] + v[1:, :-1] + v[:-1, 1:] + v[1:, 1:])
            vrel = vface - wind.reshape(1, 1, 3)
            v_n = np.sum(vrel * nhat, axis=-1, keepdims=True)
            speed = np.linalg.norm(vrel, axis=-1, keepdims=True)
            A = area * self.area_scale
            Fd = -0.5 * rho * self.cd * A * speed * vrel
            Fp = -0.5 * rho * (self.cd * 0.5) * A * v_n * np.abs(v_n) * nhat
            Fa = Fd + Fp
            if self.cl:
                lift_dir = np.cross(vrel, np.cross(nhat, vrel))
                ln = np.linalg.norm(lift_dir, axis=-1, keepdims=True)
                lift_dir = lift_dir / np.maximum(ln, 1e-12)
                Fa = Fa + 0.5 * rho * self.cl * A * (speed ** 2) * lift_dir
            # Cap aero acceleration; a free flag at ascent q is otherwise singular.
            Fmag = np.linalg.norm(Fa, axis=-1, keepdims=True)
            Fcap = 80.0 * np.maximum(self.vertex_mass, 1e-6) * 4.0  # ~80 m/s^2 per vertex share
            Fa = Fa * (Fcap / np.maximum(Fmag, Fcap))
            share = 0.25 * Fa
            F[:-1, :-1] += share
            F[1:, :-1] += share
            F[:-1, 1:] += share
            F[1:, 1:] += share
            W_aero = float(np.nansum(Fa * vface)) * dt
        vavg = self._neighbor_avg_vel()
        q_now = 0.5 * rho * float(np.dot(wind, wind))
        c_eff = self.c_damp * (1.0 + min(q_now, 2000.0) / 2000.0)
        Fdamp = -c_eff * v
        Fsm = -self.c_smooth * (v - vavg)
        self._c_eff = c_eff
        F += Fdamp + Fsm
        W_damp = float(np.sum(Fdamp * v)) * dt
        W_smooth = float(np.sum(Fsm * v)) * dt
        F[self.pin] = 0.0
        return F, E_s, E_h, W_aero, W_damp, W_smooth

    def _hair_step(self, rho, wind, dt):
        if self.n_hairs <= 0:
            return 0
        p = self.hair_pos
        v = self.hair_vel
        F = np.zeros_like(p)
        d = p[:, 1:] - p[:, :-1]
        r0 = self.hair_rest[:, 1:] - self.hair_rest[:, :-1]
        L = np.linalg.norm(d, axis=-1, keepdims=True)
        L0 = np.maximum(np.linalg.norm(r0, axis=-1, keepdims=True), 1e-9)
        dirn = d / np.maximum(L, 1e-9)
        fs = -self.k_hair_stretch * (L - L0) * dirn
        F[:, :-1] -= fs
        F[:, 1:] += fs
        hair_tgt = self._hair_hold_target(rho, wind)
        F += -self.k_hair_bend * (p - hair_tgt)
        if rho > 0:
            vmid = 0.5 * (v[:, 1:] + v[:, :-1])
            vrel = vmid - wind.reshape(1, 1, 3)
            tan = dirn
            v_perp = vrel - np.sum(vrel * tan, axis=-1, keepdims=True) * tan
            seg_L = np.maximum(L[..., 0], 1e-9)
            A_cyl = self.hair_d * seg_L
            speed_p = np.linalg.norm(v_perp, axis=-1, keepdims=True)
            Fd = -0.5 * rho * self.hair_cd * A_cyl[..., None] * speed_p * v_perp
            Fmag = np.linalg.norm(Fd, axis=-1, keepdims=True)
            Fcap = 80.0 * self.hair_mass * 2.0
            Fd = Fd * (Fcap / np.maximum(Fmag, Fcap))
            F[:, :-1] += 0.5 * Fd
            F[:, 1:] += 0.5 * Fd
        if self.n_hairs >= 3:
            tan0 = p[:, 1:] - p[:, :-1]
            tn = tan0 / np.maximum(np.linalg.norm(tan0, axis=-1, keepdims=True), 1e-9)
            dp = p[1:] - p[:-1]
            align = np.abs(np.sum(tn[1:] * tn[:-1], axis=-1, keepdims=True))
            coup = -8.0 * align * dp[:, 1:, :]
            F[1:, 1:] += coup
            F[:-1, 1:] -= coup
        self._volume_smooth(F, p, v, dt)
        n_unt = self._untangle(F, p)
        F[:, 0, :] = 0.0
        Fdamp = -0.8 * self.c_damp * v
        Fdamp[:, 0] = 0.0
        F += Fdamp
        m = self.hair_mass
        acc = F / m
        v = (v + acc * dt) / (1.0 + 0.8 * self.c_damp * dt / m)
        v[:, 0] = 0.0
        p = p + v * dt
        p[:, 0] = self.hair_rest[:, 0]
        self.hair_pos, self.hair_vel = p, v
        self.stats["n_untangle"] += n_unt
        if n_unt:
            self.stats["tangle_events"] += 1
        return n_unt

    def _volume_smooth(self, F, p, v, dt):
        if self.n_hairs <= 0:
            return
        pts = p[:, 1:, :].reshape(-1, 3)
        vels = v[:, 1:, :].reshape(-1, 3)
        if pts.shape[0] == 0:
            return
        n = self.grid_n
        y0, y1 = pts[:, 1].min() - 1e-3, pts[:, 1].max() + 1e-3
        z0, z1 = pts[:, 2].min() - 1e-3, pts[:, 2].max() + 1e-3
        iy = np.clip(((pts[:, 1] - y0) / max(y1 - y0, 1e-9) * (n - 1)).astype(int), 0, n - 1)
        iz = np.clip(((pts[:, 2] - z0) / max(z1 - z0, 1e-9) * (n - 1)).astype(int), 0, n - 1)
        acc = np.zeros((n, n, 3))
        cnt = np.zeros((n, n))
        np.add.at(acc, (iy, iz), vels)
        np.add.at(cnt, (iy, iz), 1.0)
        mean = acc / np.maximum(cnt[..., None], 1.0)
        pad = np.pad(mean, ((1, 1), (1, 1), (0, 0)), mode="edge")
        sm = 0.25 * (pad[:-2, 1:-1] + pad[2:, 1:-1] + pad[1:-1, :-2] + pad[1:-1, 2:])
        grid_v = np.where(cnt[..., None] > 0, 0.5 * mean + 0.5 * sm, 0.0)
        gv = grid_v[iy, iz]
        drag = -3.0 * (vels - gv)
        F[:, 1:, :] += drag.reshape(self.n_hairs, self.n_seg, 3)
        self.stats["n_smooth"] += 1
        self.stats["W_smooth_J"] += float(np.sum(drag * vels)) * dt

    def _untangle(self, F, p):
        if self.n_hairs <= 0 or self.n_seg < 2:
            return 0
        mid = p[:, 1:-1, :].reshape(-1, 3)
        if mid.shape[0] < 4:
            return 0
        cell = 0.02
        mid = np.nan_to_num(mid, nan=0.0, posinf=0.0, neginf=0.0)
        keys = np.stack((np.floor(mid[:, 1] / cell), np.floor(mid[:, 2] / cell)), axis=1).astype(int)
        buckets = {}
        for i, (a, b) in enumerate(keys):
            buckets.setdefault((a, b), []).append(i)
        n_hit = 0
        thresh = 0.008
        kicks = np.zeros_like(mid)
        for i, (a, b) in enumerate(keys):
            for da in (-1, 0, 1):
                for db in (-1, 0, 1):
                    for j in buckets.get((a + da, b + db), ()):
                        if j <= i:
                            continue
                        d = mid[i] - mid[j]
                        dist = float(np.linalg.norm(d))
                        if 1e-9 < dist < thresh:
                            nrm = d / dist
                            push = 0.5 * (thresh - dist) * nrm
                            kicks[i] += push
                            kicks[j] -= push
                            n_hit += 1
        if n_hit:
            F[:, 1:-1, :] += 40.0 * kicks.reshape(self.n_hairs, self.n_seg - 1, 3)
        return n_hit

    def _signals(self, rho, wind_speed):
        d = self.pos[1:] - self.pos[:-1]
        L = np.linalg.norm(d, axis=-1)
        L0 = np.maximum(np.linalg.norm(self.rest[1:] - self.rest[:-1], axis=-1), 1e-9)
        tension = np.mean(np.abs(L / L0 - 1.0)) if L.size else 0.0
        q = 0.5 * rho * wind_speed * wind_speed
        speed = float(np.mean(np.linalg.norm(self.vel, axis=-1)))
        force = q * self.effective_area() * self.cd
        return {"tension": float(tension), "q_Pa": float(q),
                "speed_m_s": speed, "force_N": float(force)}

    def _nacl_votes(self, sig, tip, settled_tip):
        t_vote = 1 if sig["tension"] > 0.04 else (-1 if sig["tension"] < 0.01 else 0)
        q_vote = 1 if sig["q_Pa"] > 800.0 else (-1 if sig["q_Pa"] < 80.0 else 0)
        m_vote = 1 if tip > 1.4 * max(settled_tip, 1e-3) else (-1 if tip < 0.4 * max(settled_tip, 1e-3) else 0)
        votes = [t_vote, q_vote, m_vote]
        inverted = False
        if votes.count(1) == 2 and votes.count(-1) == 1:
            votes = [1, 1, 1]
            inverted = True
        elif votes.count(-1) == 2 and votes.count(1) == 1:
            votes = [-1, -1, -1]
            inverted = True
        return {"votes": [t_vote, q_vote, m_vote], "sum": sum(votes), "inverted": inverted}

    def maybe_adapt(self, sig, votes, gate, admit_pos, tip):
        if self.mode.startswith("fixed"):
            return "skip"
        w = 0.0
        w += min(1.0, sig["tension"] / 0.08)
        w += min(1.0, sig["q_Pa"] / 2000.0)
        w += min(1.0, sig["speed_m_s"] / 30.0)
        w += min(1.0, abs(sig["force_N"]) / 50.0)
        w = 0.25 * w
        L_tgt = (1.0 - w) * self.Lmax + w * self.Lmin
        d = self.pos[1:] - self.pos[:-1]
        L_mean = float(np.mean(np.linalg.norm(d, axis=-1))) if d.size else self.Lmax
        want = "refine" if L_mean > 1.25 * L_tgt and self.n_chord < 14 else (
            "coarsen" if L_mean < 0.7 * L_tgt and self.n_chord > 4 else "hold"
        )
        if w > 0.55 and self.grid_n < 24:
            want_grid = "refine_grid"
        elif w < 0.2 and self.grid_n > 8:
            want_grid = "coarsen_grid"
        else:
            want_grid = "hold"
        utility = float(np.clip(0.4 + 0.5 * w, 0.05, 0.95))
        if want in ("refine", "coarsen") and self.mode == "adaptive_gated":
            if (want == "refine" and votes.get("sum", 0) < 2) or (want == "coarsen" and votes.get("sum", 0) > -1):
                self.stats["n_block"] += 1
                want = "hold"
            else:
                gr = gate.check("CreateAnchor", admit_pos,
                                f"Furn mesh {want} Lmean={L_mean:.3f} Ltgt={L_tgt:.3f}",
                                utility=utility)
                if not gr.allowed:
                    self.stats["n_block"] += 1
                    want = "hold"
                else:
                    self.stats["n_admit"] += 1
        elif want in ("refine", "coarsen") and self.mode == "adaptive_ungated":
            self.stats["n_admit"] += 1
        if want == "refine" and sig["q_Pa"] > 1500.0 and self.area_scale > 0.3:
            want = "hold"
            self.stats["n_block"] += 1
        if want == "refine":
            self._resize_cloth(self.n_span, self.n_chord + 1)
            if 0 < self.n_hairs < 48:
                self._resample_fur(self.n_hairs + 4, min(self.n_seg + 1, 8))
            self.stats["n_split"] += 1
        elif want == "coarsen":
            self._resize_cloth(self.n_span, self.n_chord - 1)
            if self.n_hairs > 12:
                self._resample_fur(max(12, self.n_hairs - 4), max(4, self.n_seg - 1))
            self.stats["n_collapse"] += 1
        if want_grid == "refine_grid":
            self.grid_n = min(24, self.grid_n + 4)
        elif want_grid == "coarsen_grid":
            self.grid_n = max(8, self.grid_n - 4)
        open_tgt = self.area_scale
        if sig["q_Pa"] > 1500.0 or sig["force_N"] > 5000.0:
            open_tgt = 0.0
        elif sig["q_Pa"] > 400.0:
            open_tgt = 0.08
        elif sig["q_Pa"] < 30.0:
            open_tgt = 1.0
        else:
            open_tgt = float(np.clip(1.0 - sig["q_Pa"] / 800.0, 0.0, 1.0))
        if self.mode == "adaptive_gated" and abs(open_tgt - self.area_scale) > 0.05:
            gr = gate.check("CreateAnchor", admit_pos,
                            f"Furn openness {self.area_scale:.2f}->{open_tgt:.2f}",
                            utility=0.65)
            if gr.allowed:
                self.area_scale = 0.6 * self.area_scale + 0.4 * open_tgt
                self.stats["n_admit"] += 1
            else:
                self.stats["n_block"] += 1
        elif self.mode == "adaptive_ungated":
            self.area_scale = 0.6 * self.area_scale + 0.4 * open_tgt
        self._mass_from_area()
        return want

    def _resize_cloth(self, n_span, n_chord):
        n_span = max(4, n_span)
        n_chord = max(4, n_chord)

        def resample(arr, nc, ns):
            oc, os = arr.shape[0], arr.shape[1]
            lc = np.linspace(0, oc - 1, nc)
            ls = np.linspace(0, os - 1, ns)
            ic0 = np.floor(lc).astype(int)
            ic1 = np.clip(ic0 + 1, 0, oc - 1)
            tc = (lc - ic0)[:, None, None]
            is0 = np.floor(ls).astype(int)
            is1 = np.clip(is0 + 1, 0, os - 1)
            ts = (ls - is0)[None, :, None]
            a = arr[ic0][:, is0]
            b = arr[ic1][:, is0]
            c = arr[ic0][:, is1]
            d = arr[ic1][:, is1]
            ab = (1 - tc) * a + tc * b
            cd = (1 - tc) * c + tc * d
            return (1 - ts) * ab + ts * cd

        self.pos = resample(self.pos, n_chord, n_span)
        self.vel = resample(self.vel, n_chord, n_span)
        self.rest = resample(self.rest, n_chord, n_span)
        self.n_chord, self.n_span = n_chord, n_span
        self.pin = np.zeros((n_chord, n_span), dtype=bool)
        self.pin[0, :] = True
        self.vel[self.pin] = 0.0
        self.groom = self.rest.copy()
        self._mass_from_area()

    def _resample_fur(self, n_hairs, n_seg):
        old_p, old_v, old_r = self.hair_pos, self.hair_vel, self.hair_rest
        self._build_fur(n_hairs, n_seg)
        if old_p.shape[0] == 0 or n_hairs <= 0:
            return

        def along(src, n_new, nseg_new):
            ho, so = src.shape[0], src.shape[1]
            ih = np.linspace(0, ho - 1, n_new)
            i0 = np.floor(ih).astype(int)
            i1 = np.clip(i0 + 1, 0, ho - 1)
            th = (ih - i0)[:, None, None]
            mid = (1 - th) * src[i0] + th * src[i1]
            js = np.linspace(0, so - 1, nseg_new + 1)
            j0 = np.floor(js).astype(int)
            j1 = np.clip(j0 + 1, 0, so - 1)
            ts = (js - j0)[None, :, None]
            return (1 - ts) * mid[:, j0] + ts * mid[:, j1]

        self.hair_pos = along(old_p, n_hairs, n_seg)
        self.hair_vel = along(old_v, n_hairs, n_seg)
        self.hair_rest = along(old_r, n_hairs, n_seg)
        self.hair_pos[:, 0] = self.hair_rest[:, 0]
        self.hair_vel[:, 0] = 0.0
        self.hair_groom = self.hair_rest.copy()

    def _hold_target(self, rho, wind):
        """Iben-style rest preload: wind is balanced by a moving rest."""
        groom = getattr(self, "groom", self.rest)
        q = 0.5 * rho * float(np.dot(wind, wind))
        F_tot = q * self.effective_area() * max(self.cd, 0.2)
        n = max(self.n_chord * self.n_span, 1)
        d = min((F_tot / n) / max(self.k_hold, 1e-6), 0.28)
        if d < 1e-6 or float(np.linalg.norm(wind)) < 1e-6:
            return groom
        frac = groom[:, :, 0] / max(self.height, 1e-9)
        wind_u = wind / (float(np.linalg.norm(wind)) + 1e-12)
        return groom + (d * np.clip(frac, 0.0, 1.0))[..., None] * wind_u.reshape(1, 1, 3)

    def _hair_hold_target(self, rho, wind):
        groom = getattr(self, "hair_groom", self.hair_rest)
        if self.n_hairs <= 0:
            return groom
        q = 0.5 * rho * float(np.dot(wind, wind))
        d = min(q * 0.0004, 0.18)
        if d < 1e-6 or float(np.linalg.norm(wind)) < 1e-6:
            return groom
        s = np.linspace(0.0, 1.0, self.n_seg + 1)[None, :, None]
        wind_u = wind / (float(np.linalg.norm(wind)) + 1e-12)
        return groom + d * (s ** 2) * wind_u.reshape(1, 1, 3)

    def _strain_limit(self, max_stretch=1.25):
        """Project edges back toward rest length (labeled strain limiter)."""
        d0 = self.pos[1:] - self.pos[:-1] if self.n_chord > 1 else None
        if d0 is not None:
            L = np.linalg.norm(d0, axis=-1)
            groom = getattr(self, "groom", self.rest)
            L0 = np.maximum(np.linalg.norm(groom[1:] - groom[:-1], axis=-1), 1e-9)
            if float(np.max(L / L0, initial=1.0)) < 1.4:
                box = max(self.width, self.height, 0.4) * 1.2
                self.pos = groom + np.clip(self.pos - groom, -box, box)
                self.pos[self.pin] = groom[self.pin]
                return
        for axis in (0, 1):
            if axis == 0:
                if self.n_chord < 2:
                    continue
                d = self.pos[1:] - self.pos[:-1]
                r0 = self.rest[1:] - self.rest[:-1]
            else:
                if self.n_span < 2:
                    continue
                d = self.pos[:, 1:] - self.pos[:, :-1]
                r0 = self.rest[:, 1:] - self.rest[:, :-1]
            L = np.linalg.norm(d, axis=-1, keepdims=True)
            L0 = np.maximum(np.linalg.norm(r0, axis=-1, keepdims=True), 1e-9)
            scale = np.minimum(1.0, (max_stretch * L0) / np.maximum(L, 1e-9))
            mid = self.pos[1:] - 0.5 * d if axis == 0 else self.pos[:, 1:] - 0.5 * d
            # simpler: shrink the far vertex toward the near one
            corr = d * (1.0 - scale)
            if axis == 0:
                unpinned = ~self.pin[1:]
                self.pos[1:] -= 0.5 * corr * unpinned[..., None]
                unpinned0 = ~self.pin[:-1]
                self.pos[:-1] += 0.5 * corr * unpinned0[..., None]
            else:
                unpinned = ~self.pin[:, 1:]
                self.pos[:, 1:] -= 0.5 * corr * unpinned[..., None]
                unpinned0 = ~self.pin[:, :-1]
                self.pos[:, :-1] += 0.5 * corr * unpinned0[..., None]
        # bound vertices to a box around rest
        box = max(self.width, self.height, 0.3)
        delta = np.clip(self.pos - self.rest, -box, box)
        self.pos = self.rest + delta
        self.pos[self.pin] = self.rest[self.pin]

    def _nan_guard(self):
        bad = ~np.isfinite(self.pos) | ~np.isfinite(self.vel)
        if np.any(bad):
            self.pos[np.any(bad, axis=-1)] = self.rest[np.any(bad, axis=-1)]
            self.vel[np.any(bad, axis=-1)] = 0.0

    def _hair_nan_guard(self):
        if self.n_hairs <= 0:
            return
        bad = ~np.isfinite(self.hair_pos) | ~np.isfinite(self.hair_vel)
        if np.any(bad):
            mask = np.any(bad, axis=-1)
            self.hair_pos[mask] = self.hair_rest[mask]
            self.hair_vel[mask] = 0.0
        # bound hair tips
        box = max(self.hair_len, 0.1) * 1.5
        delta = np.clip(self.hair_pos - self.hair_rest, -box, box)
        self.hair_pos = self.hair_rest + delta
        self.hair_pos[:, 0] = self.hair_rest[:, 0]
        self.hair_vel[:, 0] = 0.0
        self.hair_vel = np.clip(self.hair_vel, -20.0, 20.0)

    def tip_disp(self):
        cloth_tip = self.pos[-1] - getattr(self, 'groom', self.rest)[-1]
        c = float(np.sqrt(np.mean(np.sum(cloth_tip ** 2, axis=-1))))
        if self.n_hairs:
            hair_tip = self.hair_pos[:, -1] - getattr(self, 'hair_groom', self.hair_rest)[:, -1]
            h = float(np.sqrt(np.mean(np.sum(hair_tip ** 2, axis=-1))))
        else:
            h = 0.0
        return c, h, max(c, h)

    def step(self, dt, rho, wind, gate=None, admit_pos=None, adapt=False,
             settled_tip=0.02):
        wind = np.asarray(wind, dtype=float).reshape(3)
        F, E_s, E_h, Wa, Wd, Ws = self._cloth_forces(rho, wind, dt)
        m = self.vertex_mass
        acc = F / m
        c_eff = getattr(self, "_c_eff", self.c_damp)
        self.vel = (self.vel + acc * dt) / (1.0 + c_eff * dt / m)
        self.vel = np.clip(self.vel, -25.0, 25.0)
        self.vel[self.pin] = 0.0
        self.pos = self.pos + self.vel * dt
        self.pos[self.pin] = self.rest[self.pin]
        self._strain_limit()
        self._nan_guard()
        self._hair_step(rho, wind, dt)
        self._hair_nan_guard()
        c, h, tip = self.tip_disp()
        self.stats["W_aero_J"] += Wa
        self.stats["W_damp_J"] += Wd
        self.stats["W_smooth_J"] += Ws
        self.stats["E_stretch_peak"] = max(self.stats["E_stretch_peak"], E_s)
        self.stats["E_hold_peak"] = max(self.stats["E_hold_peak"], E_h)
        self.stats["tip_peak"] = max(self.stats["tip_peak"], tip)
        self.stats["dof_sum"] += self.dof()["total_sim"]
        self.stats["dof_n"] += 1
        self.stats["open_mean"] += self.area_scale
        self.stats["open_n"] += 1
        self.stats["n_hold"] += 1
        sig = self._signals(rho, float(np.linalg.norm(wind)))
        votes = self._nacl_votes(sig, tip, settled_tip)
        action = "skip"
        if adapt and gate is not None:
            action = self.maybe_adapt(sig, votes, gate, admit_pos, tip)
        return {
            "tip": tip, "cloth_tip": c, "hair_tip": h,
            "E_stretch": E_s, "E_hold": E_h, "sig": sig, "votes": votes,
            "action": action, "dof": self.dof()["total_sim"],
            "open": self.area_scale, "grid_n": self.grid_n,
        }

def record_ascent_wind(dart, fp=0.85, isp=450.0, dt=0.25, t_max=400.0):
    T = 3.0 * dart["mass"] * G_STD
    ve = isp * G_STD
    mdot = T / ve
    m_prop = fp * dart["mass"]
    m = dart["mass"]
    x, y = 0.0, RE
    vx, vy = 0.0, 0.0
    t = 0.0
    burned = 0.0
    samples = []
    h0 = 0.0
    while t < t_max:
        r = math.hypot(x, y)
        h = r - RE
        if h < -10 and t > 1:
            break
        rho = G.rho_isa(max(0.0, h))
        speed = math.hypot(vx, vy)
        q = 0.5 * rho * speed * speed
        g = MU / (r * r)
        gx, gy = -g * x / r, -g * y / r
        dx = dy = 0.0
        if speed > 1e-6 and m > 0:
            Fd = 0.5 * dart["cd"] * rho * dart["area"] * speed * speed
            dx, dy = -Fd / m * vx / speed, -Fd / m * vy / speed
        tx = ty = 0.0
        thrusting = burned < m_prop - 1e-12
        urx, ury = x / r, y / r
        uhx, uhy = ury, -urx
        if thrusting:
            if h - h0 < 100.0:
                pitch = math.pi / 2.0
            else:
                frac = min(1.0, max(0.0, (h - h0 - 100.0) / 40_000.0))
                pitch = math.radians(85.0) * (1.0 - frac) + math.radians(5.0) * frac
            tdirx = urx * math.sin(pitch) + uhx * math.cos(pitch)
            tdiry = ury * math.sin(pitch) + uhy * math.cos(pitch)
            if tdirx * urx + tdiry * ury < 0:
                tdirx, tdiry = uhx, uhy
            tx, ty = (T / m) * tdirx, (T / m) * tdiry
            dm = min(mdot * dt, m_prop - burned)
            m -= dm
            burned += dm
        if not all(np.isfinite(v) for v in (gx, gy, dx, dy, tx, ty)):
            dx = dy = tx = ty = 0.0
        ax, ay = gx + dx + tx, gy + dy + ty
        vx += ax * dt
        vy += ay * dt
        if not (np.isfinite(vx) and np.isfinite(vy)):
            vx = vy = 0.0
        x += vx * dt
        y += vy * dt
        t += dt
        samples.append({"t_s": t, "h_m": h, "v_m_s": speed, "rho": rho, "q_Pa": q,
                        "thrusting": thrusting, "mass_kg": m})
        heights = [s["h_m"] for s in samples]
        if (not thrusting) and t > 200 and h < max(heights):
            if t > (samples[int(np.argmax(heights))]["t_s"] + 40):
                break
    return samples


def run_standalone(mode, series, gate, admit_pos, dt=0.01, adapt_every=8,
                   label="ascent"):
    furn = AdaptiveFurn(mode=mode, seed=2 if "gust" in label else 1)
    settled = 0.02
    tips = []
    t_adapt = 0
    ts = np.array([s["t_s"] for s in series])
    rhos = np.array([s["rho"] for s in series])
    vs = np.array([s["v_m_s"] for s in series])
    t0, t1 = float(ts[0]), float(ts[-1])
    t = t0
    last = None
    peak_q = 0.0
    t_after_peak = None
    settle_t = None
    peak_tip = 0.0
    t_peak_tip = 0.0
    while t <= t1 + 1e-12:
        rho = float(np.interp(t, ts, rhos))
        spd = float(np.interp(t, ts, vs))
        wind = np.array([spd, 0.0, 0.0])
        adapt = (t_adapt % adapt_every == 0)
        last = furn.step(dt, rho, wind, gate=gate, admit_pos=admit_pos,
                         adapt=adapt, settled_tip=settled)
        tips.append(last["tip"])
        q = 0.5 * rho * spd * spd
        if q >= peak_q:
            peak_q = q
            t_after_peak = None
        elif t_after_peak is None and peak_q > 0:
            t_after_peak = t
        if last["tip"] >= peak_tip:
            peak_tip = last["tip"]
            t_peak_tip = t
        if t_after_peak is not None and settle_t is None:
            if last["tip"] < 0.2 * max(peak_tip, 1e-6):
                settle_t = t - t_after_peak
        if int(t / 0.05) != int((t - dt) / 0.05):
            furn.trace_t.append(t)
            furn.trace_tip.append(last["tip"])
            furn.trace_dof.append(last["dof"])
            furn.trace_E.append(last["E_stretch"] + last["E_hold"])
            furn.trace_open.append(last["open"])
            furn.trace_grid.append(last["grid_n"])
        t += dt
        t_adapt += 1
    n = max(len(tips), 1)
    furn.stats["tip_rms"] = float(math.sqrt(sum(x * x for x in tips) / n))
    furn.stats["mean_dof"] = furn.stats["dof_sum"] / max(furn.stats["dof_n"], 1)
    furn.stats["mean_open"] = furn.stats["open_mean"] / max(furn.stats["open_n"], 1)
    furn.stats["settle_s_after_peak_q"] = settle_t
    furn.stats["peak_q_Pa"] = peak_q
    furn.stats["peak_tip"] = peak_tip
    furn.stats["t_peak_tip_s"] = t_peak_tip
    Wa = furn.stats["W_aero_J"]
    Wdiss = furn.stats["W_damp_J"] + furn.stats["W_smooth_J"]
    furn.stats["dissipated_over_aero"] = (abs(Wdiss) / abs(Wa)) if abs(Wa) > 1e-12 else None
    return furn, last


def gust_series(v_gust=18.0, t_on=5.0, t_off=7.0, rho=1.20):
    ts = []
    t, dt = 0.0, 0.02
    while t <= t_on + t_off:
        v = v_gust if t <= t_on else 0.0
        ts.append({"t_s": t, "h_m": 0.0, "v_m_s": v, "rho": rho,
                   "q_Pa": 0.5 * rho * v * v, "thrusting": False, "mass_kg": 0.0})
        t += dt
    return ts

def coupled_ascent(dart, fp, site, mode, surface, gate, admit_pos,
                   az_deg=90.0, isp=450.0, dt=0.05, t_max=1500.0):
    m0 = dart["mass"] + surface.get("extra_mass_kg", 0.0)
    T = 3.0 * dart["mass"] * G_STD
    ve = isp * G_STD
    mdot = T / ve
    m_prop = fp * dart["mass"]
    m = m0
    x, y = 0.0, RE
    vx, vy = 0.0, 0.0
    t = 0.0
    burned = 0.0
    h0 = 0.0
    h_max = 0.0
    peak_q = peak_Teq = 0.0
    g_loss = d_loss = surf_loss = 0.0
    burnout = None
    furn = None
    if surface["kind"] == "kite":
        furn = AdaptiveFurn(
            mode=mode if mode.startswith("adaptive") else (
                "fixed_coarse" if mode == "fixed_reefed" else "fixed_fine"
            ),
            width=surface.get("width", 3.16),
            height=surface.get("height", 3.16),
            sigma_kg_m2=surface.get("sigma", 0.05),
            cd=surface.get("cd", 0.25),
            cl=surface.get("cl", 0.8),
            hair_len=surface.get("hair_len", 0.15),
            n_hairs=surface.get("n_hairs", 16),
            seed=3,
        )
        if mode == "fixed_reefed":
            furn.area_scale = 0.0
            furn.mode = "fixed_coarse"
        elif mode == "fixed_open":
            furn.area_scale = 1.0
            furn.mode = "fixed_fine"
    elif surface["kind"] == "line":
        furn = AdaptiveFurn(
            mode=mode if mode.startswith("adaptive") else "fixed_coarse",
            width=surface.get("line_d_m", 0.001) * math.pi,
            height=surface.get("line_m", 500.0) * 0.002,
            sigma_kg_m2=2.0, cd=1.0, cl=0.0,
            n_hairs=8, n_seg=8,
            hair_len=min(1.0, surface.get("line_m", 500.0) * 0.002),
            hair_d=surface.get("line_d_m", 0.001),
            seed=4,
        )
        furn.area_scale = 0.0
    line_L0 = surface.get("line_m", 500.0)
    line_d = surface.get("line_d_m", 0.001)
    line_deploy_h = surface.get("line_deploy_h_m", 60_000.0)
    line_L = 0.0
    peak_lift = peak_drag = peak_tension = 0.0
    while t < t_max:
        r = math.hypot(x, y)
        if r < 1:
            break
        h = r - RE
        if h < -10 and t > 1:
            break
        rho = G.rho_isa(max(0.0, h))
        speed = math.hypot(vx, vy)
        q = 0.5 * rho * speed * speed
        qsg = G.sutton_graves_q(rho, speed)
        Teq = G.T_eq_radiation(qsg)
        peak_q = max(peak_q, q)
        peak_Teq = max(peak_Teq, Teq)
        g = MU / (r * r)
        gx, gy = -g * x / r, -g * y / r
        urx, ury = x / r, y / r
        uhx, uhy = ury, -urx
        dx = dy = 0.0
        if speed > 1e-6 and m > 0:
            Fd = 0.5 * dart["cd"] * rho * dart["area"] * speed * speed
            dx -= (Fd / m) * vx / speed
            dy -= (Fd / m) * vy / speed
            d_loss += (Fd / m) * dt
        lift_N = drag_N = 0.0
        if furn is not None and surface["kind"] == "kite":
            wind = np.array([speed, 0.0, 0.0])
            sub = 4
            sdt = dt / sub
            for k in range(sub):
                furn.step(sdt, rho, wind, gate=gate, admit_pos=admit_pos,
                          adapt=(k == 0 and int(t / dt) % 4 == 0),
                          settled_tip=0.02)
            A = furn.effective_area()
            if not np.isfinite(A) or A < 0:
                A = 0.0
            CL, CD = surface.get("cl", 0.8), surface.get("cd", 0.25)
            drag_N = 0.5 * rho * speed * speed * CD * A
            lift_N = 0.5 * rho * speed * speed * CL * A
            if not np.isfinite(drag_N):
                drag_N = 0.0
            if not np.isfinite(lift_N):
                lift_N = 0.0
            if speed > 1e-6 and m > 0:
                fx, fy = -vx / speed, -vy / speed
                lx, ly = -fy, fx
                if lx * urx + ly * ury < 0:
                    lx, ly = -lx, -ly
                ax_s = (drag_N * fx + lift_N * lx) / m
                ay_s = (drag_N * fy + lift_N * ly) / m
                a_s = math.hypot(ax_s, ay_s)
                if a_s > 25.0:
                    furn.area_scale = 0.0
                    ax_s = ay_s = 0.0
                    drag_N = lift_N = 0.0
                dx += ax_s
                dy += ay_s
                surf_loss += (drag_N / m) * dt
            peak_lift = max(peak_lift, lift_N)
            peak_drag = max(peak_drag, drag_N)
        if surface["kind"] == "line":
            if h >= line_deploy_h:
                if mode.startswith("adaptive"):
                    Cd_line = 1.0
                    A_full = line_L0 * line_d
                    Fd_full = 0.5 * rho * speed * speed * Cd_line * A_full
                    want_L = line_L0
                    if Fd_full > 0.15 * T:
                        want_L = line_L0 * max(0.02, (0.15 * T) / max(Fd_full, 1e-9))
                    if mode == "adaptive_gated":
                        gr = gate.check("CreateAnchor", admit_pos,
                                        f"Line length {line_L:.1f}->{want_L:.1f}",
                                        utility=0.65)
                        if gr.allowed:
                            line_L = 0.7 * line_L + 0.3 * want_L if line_L > 0 else want_L
                        elif line_L == 0.0 and want_L > 0 and Fd_full <= 0.15 * T:
                            line_L = want_L
                    else:
                        line_L = 0.7 * line_L + 0.3 * want_L if line_L > 0 else want_L
                    if furn is not None:
                        furn.area_scale = line_L / max(line_L0, 1e-9)
                        wind = np.array([speed, 0.0, 0.0])
                        furn.step(dt / 4.0, rho, wind, gate=gate, admit_pos=admit_pos,
                                  adapt=(int(t / dt) % 8 == 0), settled_tip=0.02)
                else:
                    line_L = line_L0
            A_line = line_L * line_d
            if A_line > 0 and speed > 1e-6 and m > 0:
                drag_N = 0.5 * rho * speed * speed * 1.0 * A_line
                dx -= (drag_N / m) * vx / speed
                dy -= (drag_N / m) * vy / speed
                surf_loss += (drag_N / m) * dt
                peak_drag = max(peak_drag, drag_N)
                peak_tension = max(peak_tension, drag_N)
        tx = ty = 0.0
        thrusting = burned < m_prop - 1e-12
        if thrusting:
            if h - h0 < 100.0:
                pitch = math.pi / 2.0
            else:
                frac = min(1.0, max(0.0, (h - h0 - 100.0) / 40_000.0))
                pitch = math.radians(85.0) * (1.0 - frac) + math.radians(5.0) * frac
            tdirx = urx * math.sin(pitch) + uhx * math.cos(pitch)
            tdiry = ury * math.sin(pitch) + uhy * math.cos(pitch)
            if tdirx * urx + tdiry * ury < 0:
                tdirx, tdiry = uhx, uhy
            tx, ty = (T / m) * tdirx, (T / m) * tdiry
            if speed > 1e-6:
                g_along = -(gx * vx + gy * vy) / speed
                g_loss += max(0.0, g_along) * dt
            dm = min(mdot * dt, m_prop - burned)
            m -= dm
            burned += dm
            if burned >= m_prop - 1e-12 and burnout is None:
                vr = vx * urx + vy * ury
                vt = vx * uhx + vy * uhy
                burnout = {
                    "t_s": t, "h_m": h, "v_m_s": speed,
                    "gamma_deg": math.degrees(math.atan2(vr, vt)) if (abs(vt) > 1e-9 or abs(vr) > 1e-9) else 0.0,
                    "mass_kg": m,
                }
        ax, ay = gx + dx + tx, gy + dy + ty
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt
        t += dt
        r2 = math.hypot(x, y)
        h2 = r2 - RE
        if h2 > h_max:
            h_max = h2
        if (not thrusting) and burnout is not None and t > burnout["t_s"] + 400:
            break
        if (not thrusting) and burnout is not None and h2 < 0 and t > burnout["t_s"] + 5:
            break
    if burnout is None:
        speed = math.hypot(vx, vy)
        r = math.hypot(x, y)
        h = r - RE
        urx, ury = x / max(r, 1e-9), y / max(r, 1e-9)
        uhx, uhy = ury, -urx
        vr = vx * urx + vy * ury
        vt = vx * uhx + vy * uhy
        burnout = {
            "t_s": t, "h_m": h, "v_m_s": speed,
            "gamma_deg": math.degrees(math.atan2(vr, vt)) if (abs(vt) > 1e-9 or abs(vr) > 1e-9) else 0.0,
            "mass_kg": m,
        }
    closed = KG.kepler_after_burnout(
        burnout["h_m"], burnout["v_m_s"], burnout["gamma_deg"],
        site["lat"], az_deg,
    )
    if closed.get("residual_m_s") is None or not np.isfinite(float(closed.get("residual_m_s") or np.nan)):
        # Unphysical or impact: leftover is at least the circular-speed gap from rest.
        closed["residual_m_s"] = G.V_CIRC_200KM if hasattr(G, "V_CIRC_200KM") else 7788.0
        if closed.get("perigee_km") is None:
            closed["perigee_km"] = -6371.0
        if closed.get("apogee_km") is None:
            closed["apogee_km"] = max(-6371.0, burnout["h_m"] / 1000.0)
        closed["locked"] = False
        closed["unphysical_or_impact"] = True
    furn_stats = None
    if furn is not None:
        furn.stats["mean_dof"] = furn.stats["dof_sum"] / max(furn.stats["dof_n"], 1)
        furn.stats["mean_open"] = furn.stats["open_mean"] / max(furn.stats["open_n"], 1)
        furn_stats = {k: furn.stats[k] for k in furn.stats if k not in ("dof_sum", "open_mean")}
        _c, _h, tip = furn.tip_disp()
        furn_stats["final_tip"] = tip
    return {
        "ok": True,
        "h_max_km": h_max / 1000.0,
        "h_burnout_km": burnout["h_m"] / 1000.0,
        "v_burnout_m_s": burnout["v_m_s"],
        "gamma_burnout_deg": burnout["gamma_deg"],
        "t_burn_s": burnout["t_s"],
        "mass_end_kg": m,
        "peak_q_Pa": peak_q,
        "peak_Teq_K": peak_Teq,
        "gravity_loss_m_s": g_loss,
        "drag_loss_m_s": d_loss,
        "surface_drag_loss_m_s": surf_loss,
        "peak_lift_N": peak_lift,
        "peak_drag_N": peak_drag,
        "peak_tension_N": peak_tension,
        "line_L_end_m": line_L if surface["kind"] == "line" else None,
        "kite_open_end": None if furn is None or surface["kind"] != "kite" else furn.area_scale,
        "residual_m_s": closed["residual_m_s"],
        "apogee_km": closed["apogee_km"],
        "perigee_km": closed["perigee_km"],
        "locked": closed["locked"],
        "v_inertial_m_s": closed["v_inertial_m_s"],
        "boost_m_s": closed["boost_m_s"],
        "furn": furn_stats,
        "mode": mode,
        "kind": surface["kind"],
    }

def integrate_sail_adaptive(
    h0, v0, gamma_deg, mass, area0, sail_rho, P, site_elev_m, omega_plane,
    mode="adaptive_gated", gate=None, admit_pos=None,
    unfold="smart", face="prograde_tilt", shutter="residual",
    dt=0.05, t_max=400.0, theta0_downrange_m=0.0,
    dart_area=0.006, dart_cd=0.2, sigma_kg_m2=0.01,
):
    Rs = RE + max(0.0, site_elev_m)
    r0 = RE + h0
    th0 = theta0_downrange_m / r0
    x = r0 * math.sin(th0)
    y = r0 * math.cos(th0)
    gam = math.radians(gamma_deg)
    rhat0 = np.array([x, y]) / r0
    that0 = np.array([rhat0[1], -rhat0[0]])
    vr = v0 * math.sin(gam)
    vt = v0 * math.cos(gam)
    vel = vr * rhat0 + vt * that0
    pos = np.array([x, y], dtype=float)
    vel = np.array(vel, dtype=float)
    furn = AdaptiveFurn(
        mode="adaptive_gated" if mode.startswith("adaptive") else mode,
        width=math.sqrt(area0), height=math.sqrt(area0),
        sigma_kg_m2=sigma_kg_m2, cd=LS.CD_SAIL, cl=0.0,
        n_hairs=0, hair_len=0.0, seed=5,
    )
    if mode in ("fixed_open", "fixed_fine"):
        furn.area_scale = 1.0
        furn.mode = "fixed_fine"
    elif mode == "fixed_coarse":
        furn.area_scale = 1.0
        furn.mode = "fixed_coarse"
    unfolded = False
    t_unfold = None
    t_los_end = None
    t_shuttered = 0.0
    peak_Teq = peak_q = peak_drag = peak_F = 0.0
    impulse = energy_cmd = energy_on_sail = t_on = t_el5 = 0.0
    h_max = h0
    min_el = 90.0
    drag_impulse = 0.0
    reason_end = "t_max"
    n_gate_pass = n_gate_block = 0
    n_mesh_admit = n_mesh_block = 0
    open_hist = []
    rho_sail = getattr(LS, "RHO_SAIL", 0.90)

    def site_pos(tt):
        ang = omega_plane * tt
        return np.array([Rs * math.sin(ang), Rs * math.cos(ang)], dtype=float)

    t = 0.0
    nstep = 0
    while t < t_max:
        r = float(np.linalg.norm(pos))
        if r <= RE or not np.isfinite(r):
            reason_end = "impact"
            break
        h = r - RE
        speed = float(np.linalg.norm(vel))
        if (not np.isfinite(speed)) or speed > 20000.0 or h > 5.0e6:
            reason_end = "unphysical_state"
            break
        spos = site_pos(t)
        el, Ldist = LS.los_elevation_and_range(pos, spos)
        el_deg = math.degrees(el)
        min_el = min(min_el, el_deg)
        if el_deg >= 5.0:
            t_el5 += dt
        if el <= 0.0 and t_los_end is None and t > 0:
            t_los_end = t
        rho_a = LS.rho_at(h)
        area = area0 * furn.area_scale
        if not unfolded:
            drag = 0.5 * rho_a * speed * speed * LS.CD_SAIL * area0
            _Ftry, dtry = LS.photon_force_vector(pos, spos, vel, P, area0, rho_sail, face="beam")
            if unfold == "immediate" or (unfold == "smart" and dtry["F_N"] >= drag and dtry["F_N"] > 0):
                unfolded = True
                t_unfold = t
        acc = -MU * pos / (r ** 3)
        diag = {"P_int_W": 0.0, "F_N": 0.0, "f_spot": 1.0, "T_atm": 0.0,
                "el_deg": el_deg, "L_m": Ldist, "spot_radius_m": LS.spot_radius(Ldist)}
        if unfolded and el > math.radians(LS.EL_MIN_DEG) and P > 0:
            F_try, diag = LS.photon_force_vector(pos, spos, vel, P, area, rho_sail, face=face)
            use = True
            if shutter == "residual" and diag["F_N"] > 0:
                res0, _, _ = LS.state_residual(pos, vel)
                res1, _, _ = LS.state_residual(pos, vel + (F_try / mass) * dt)
                if res0 is None or res1 is None or res1 >= res0 - 1e-6:
                    use = False
                    n_gate_block += 1
                    t_shuttered += dt
                else:
                    n_gate_pass += 1
            if use and diag["F_N"] > 0:
                acc = acc + F_try / mass
                t_on += dt
                energy_cmd += P * dt
                energy_on_sail += diag["P_int_W"] * dt
                impulse += diag["F_N"] * dt
                peak_F = max(peak_F, diag["F_N"])
                P_abs = (1.0 - rho_sail) * diag["P_int_W"]
                if area > 0 and LS.EPS_SAIL > 0 and P_abs > 0:
                    Teq = (P_abs / (2.0 * area * LS.EPS_SAIL * SIGMA_SB)) ** 0.25
                    peak_Teq = max(peak_Teq, Teq)
        if speed > 1e-6:
            A_d = area if unfolded else dart_area
            cd = LS.CD_SAIL if unfolded else dart_cd
            Fd = 0.5 * rho_a * speed * speed * cd * A_d
            acc = acc - (Fd / mass) * (vel / speed)
            peak_drag = max(peak_drag, Fd)
            peak_q = max(peak_q, 0.5 * rho_a * speed * speed)
            if unfolded:
                drag_impulse += Fd * dt
        if unfolded and mode.startswith("adaptive") and nstep % 4 == 0:
            wind = np.array([speed, 0.0, 0.0])
            furn.step(dt, rho_a, wind, gate=gate, admit_pos=admit_pos,
                      adapt=True, settled_tip=0.02)
            if mode == "adaptive_gated" and gate is not None:
                cands = []
                for sc in (0.15, 0.4, 0.7, 1.0):
                    A_try = area0 * sc
                    Fph, dph = LS.photon_force_vector(pos, spos, vel, P, A_try, rho_sail, face=face)
                    Fd_try = 0.5 * rho_a * speed * speed * LS.CD_SAIL * A_try
                    acc_try = -MU * pos / (r ** 3) + Fph / mass - (Fd_try / mass) * (vel / max(speed, 1e-9))
                    res0, _, _ = LS.state_residual(pos, vel)
                    res_ph, _, _ = LS.state_residual(pos, vel + (Fph / mass) * dt)
                    use_ph = not (res0 is None or res_ph is None or res_ph >= res0 - 1e-6)
                    if not use_ph:
                        acc_try = -MU * pos / (r ** 3) - (Fd_try / mass) * (vel / max(speed, 1e-9))
                    res1, _, _ = LS.state_residual(pos, vel + acc_try * dt)
                    cands.append((res1 if res1 is not None else 1e18, sc))
                best_res, best_sc = min(cands, key=lambda z: z[0])
                cur_res, _, _ = LS.state_residual(pos, vel)
                utility = 0.7 if (cur_res is not None and best_res < cur_res) else 0.35
                gr = gate.check("CreateAnchor", admit_pos,
                                f"Sail openness {furn.area_scale:.2f}->{best_sc:.2f}",
                                utility=utility)
                if gr.allowed:
                    furn.area_scale = 0.6 * furn.area_scale + 0.4 * best_sc
                    n_mesh_admit += 1
                else:
                    n_mesh_block += 1
            elif mode == "adaptive_ungated":
                Fph, dph = LS.photon_force_vector(pos, spos, vel, P, area0, rho_sail, face=face)
                Fd0 = 0.5 * rho_a * speed * speed * LS.CD_SAIL * area0
                sc = 1.0 if dph["F_N"] >= Fd0 else max(0.15, dph["F_N"] / max(Fd0, 1e-9))
                furn.area_scale = 0.6 * furn.area_scale + 0.4 * sc
        open_hist.append(furn.area_scale)
        vel = vel + acc * dt
        pos = pos + vel * dt
        t += dt
        nstep += 1
        h = float(np.linalg.norm(pos)) - RE
        if np.isfinite(h):
            h_max = max(h_max, h)
        if t_los_end is not None and (t - t_los_end) > 5.0:
            reason_end = "lost_los"
            break

    res, kep, gamma = LS.state_residual(pos, vel)
    peri = kep.get("h_perigee_m") if kep else None
    apo = kep.get("h_apogee_m") if kep else None
    speed = float(np.linalg.norm(vel)) if np.isfinite(vel).all() else float("nan")
    h = float(np.linalg.norm(pos)) - RE if np.isfinite(pos).all() else float("nan")
    furn.stats["mean_dof"] = furn.stats["dof_sum"] / max(furn.stats["dof_n"], 1)
    furn.stats["mean_open"] = float(np.mean(open_hist)) if open_hist else furn.area_scale
    return {
        "t_end_s": t, "reason_end": reason_end, "unfolded": unfolded,
        "t_unfold_s": t_unfold, "t_los_end_s": t_los_end, "t_el5_s": t_el5,
        "t_on_s": t_on, "t_shuttered_s": t_shuttered,
        "n_gate_pass": n_gate_pass, "n_gate_block": n_gate_block,
        "n_mesh_admit": n_mesh_admit, "n_mesh_block": n_mesh_block,
        "h_end_km": h / 1000.0 if np.isfinite(h) else None,
        "h_max_km": h_max / 1000.0,
        "v_end_m_s": speed, "gamma_end_deg": gamma,
        "residual_after_m_s": res,
        "apogee_after_km": None if apo is None else apo / 1000.0,
        "perigee_after_km": None if peri is None else peri / 1000.0,
        "locked": LS.locked_of(res, peri),
        "energy_cmd_J": energy_cmd, "energy_on_sail_J": energy_on_sail,
        "impulse_N_s": impulse, "dv_imparted_m_s": impulse / mass if mass > 0 else 0.0,
        "drag_impulse_N_s": drag_impulse,
        "dv_drag_m_s": drag_impulse / mass if mass > 0 else 0.0,
        "peak_Teq_K": peak_Teq, "peak_q_Pa": peak_q, "peak_drag_N": peak_drag,
        "peak_F_N": peak_F, "min_el_deg": min_el,
        "mean_open": furn.stats["mean_open"],
        "open_end": furn.area_scale,
        "mean_dof": furn.stats["mean_dof"],
        "furn": {k: furn.stats[k] for k in ("n_split", "n_collapse", "n_block", "n_admit",
                                           "tangle_events", "W_aero_J", "W_damp_J",
                                           "tip_peak", "E_stretch_peak")},
        "mode": mode,
        "nstep": nstep,
    }


def straw_liner_run(mode, accel_series, gate, admit_pos):
    furn = AdaptiveFurn(mode=mode, width=2.0, height=2.0, sigma_kg_m2=0.2,
                        cd=0.0, cl=0.0, n_hairs=20, hair_len=0.08, seed=6)
    furn.area_scale = 1.0
    tips = []
    for i, s in enumerate(accel_series):
        a = s.get("a_m_s2", 0.0)
        furn.rest[:, :, 2] = 0.01 - 0.002 * math.tanh(a / 20.0)
        rec = furn.step(s.get("dt", 0.25), 0.0, np.zeros(3), gate=gate,
                        admit_pos=admit_pos, adapt=(i % 4 == 0), settled_tip=0.01)
        tips.append(rec["tip"])
        if i % 2 == 0:
            furn.trace_t.append(s["t_s"])
            furn.trace_tip.append(rec["tip"])
            furn.trace_dof.append(rec["dof"])
            furn.trace_E.append(rec["E_stretch"] + rec["E_hold"])
    furn.stats["tip_rms"] = float(math.sqrt(np.mean(np.square(tips)))) if tips else 0.0
    furn.stats["mean_dof"] = furn.stats["dof_sum"] / max(furn.stats["dof_n"], 1)
    return furn

def run():
    dart = G.vehicle_from_mass(20.0, hollow_k=0.8, payload_frac=0.30)
    geo = json.loads((OUT / "geography.json").read_text())
    sites = {s["id"]: s for s in geo["sites"]}
    kourou = sites["kourou"]
    guide = json.loads((OUT / "guidance_kite_line_straw.json").read_text())
    sailj = json.loads((OUT / "light_sail_push.json").read_text())
    gate = core.PrinciplesGate(core.load_config())
    nexus = R.Nexus()
    transcriber = R.Transcriber()
    dictator = R.Dictator(transcriber)
    levy = R.Levy(transcriber)

    def assess(kind, n=1):
        w = LEVY.get(kind, 1) * n
        levy.total += w
        levy.entries.append({"kind": kind, "weight": w})
        return w

    levy.assess = assess
    sim = R.RelationalSim(nexus)
    nexus.register("genesis", {"tag": "I am the OG avatar", "weight": math.inf})
    assess("genesis")
    dictator.stream("genesis", "Fur/fabric adaptive-mesh ledger. Recycled no-track, guidance, and light-sail leftovers; new furn plugins only.")

    admit = {}
    for name, posd in (
        ("furn_surface", {"x": 5.2372, "y": -52.7681, "z": 1.0}),
        ("adaptive_mesh", {"x": 5.2372, "y": -52.7681, "z": 2.0}),
        ("null_mesh", None),
    ):
        pos = core.vec(posd) if posd else None
        gr = gate.check("CreateAnchor", pos, f"Admit {name}", utility=0.65)
        admit[name] = {"allowed": bool(gr.allowed), "principle": gr.principle}
        if gr.allowed:
            assess("admit_path")
            nexus.register(f"mesh:{name}", {"pos": posd})
        else:
            assess("suppress_path")
            dictator.stream("suppress_path", f"Blocked {name}: {gr.principle}")
    admit_pos = core.vec({"x": 5.2372, "y": -52.7681, "z": 2.0})

    print("Recording recycled no-track wind history...")
    wind = record_ascent_wind(dart, fp=0.85)
    t_cut = 180.0
    wind_cut = [s for s in wind if s["t_s"] <= t_cut] or wind
    gust = gust_series()

    standalone = {"ascent_playback": {}, "gust": {}}
    modes = ("fixed_coarse", "fixed_fine", "adaptive_ungated", "adaptive_gated")
    cache_p = OUT / "_fur_standalone_cache.json"
    if cache_p.exists():
        print("  reusing cached standalone from", cache_p)
        blob = json.loads(cache_p.read_text())
        standalone = blob["standalone"]
        wind_cut = blob.get("wind_cut", wind_cut)
        for label in standalone:
            for mode in standalone[label]:
                st = standalone[label][mode]["stats"]
                assess("refine", st.get("n_split", 0))
                assess("coarsen", st.get("n_collapse", 0))
                assess("block_refine", st.get("n_block", 0))
                assess("untangle", max(1, st.get("tangle_events", 0)))
                assess("smooth", 1)
                assess("hold_shape", 1)
    for label, series in (("ascent_playback", wind_cut), ("gust", gust)):
        if cache_p.exists():
            continue
        for mode in modes:
            print(f"  standalone {label} {mode}...")
            furn, last = run_standalone(mode, series, gate, admit_pos, label=label)
            assess("refine", furn.stats["n_split"])
            assess("coarsen", furn.stats["n_collapse"])
            assess("block_refine", furn.stats["n_block"])
            assess("untangle", max(1, furn.stats["tangle_events"]))
            assess("smooth", 1)
            assess("hold_shape", 1)
            standalone[label][mode] = {
                "stats": {k: furn.stats[k] for k in furn.stats},
                "dof_end": furn.dof(),
                "open_end": furn.area_scale,
                "grid_n_end": furn.grid_n,
                "n_chord": furn.n_chord, "n_span": furn.n_span,
                "n_hairs": furn.n_hairs, "n_seg": furn.n_seg,
                "trace": {
                    "t_s": furn.trace_t, "tip_m": furn.trace_tip,
                    "dof": furn.trace_dof, "E_J": furn.trace_E,
                    "open": furn.trace_open, "grid_n": furn.trace_grid,
                },
            }

    cache = OUT / "_fur_standalone_cache.json"
    cache.write_text(json.dumps({
        "standalone": {k: {m: {kk: vv for kk, vv in standalone[k][m].items() if kk != "trace"}
                           | {"trace": standalone[k][m]["trace"]}
                           for m in standalone[k]} for k in standalone},
        "wind_cut": [{"t_s": s["t_s"], "q_Pa": s["q_Pa"], "h_m": s["h_m"],
                      "v_m_s": s["v_m_s"], "rho": s["rho"], "thrusting": s["thrusting"]}
                     for s in wind_cut],
    }, default=lambda o: float(o) if isinstance(o, (np.floating,)) else int(o) if isinstance(o, (np.integer,)) else str(o)))
    print("Cached standalone to", cache)

    print("Coupled kite / line...")
    coupled = []

    def add_coupled(label, mode, surface):
        rec = coupled_ascent(dart, 0.85, kourou, mode, surface, gate, admit_pos)
        rec["label"] = label
        rec["fp"] = 0.85
        rec["site_id"] = "kourou"
        assess("orbit_lock" if rec.get("locked") else "fail")
        coupled.append(rec)
        res = rec.get("residual_m_s")
        hmx = rec.get("h_max_km")
        peri = rec.get("perigee_km")
        rs = "None" if res is None else f"{res:.1f}"
        hs = "None" if hmx is None else f"{hmx:.1f}"
        ps = "None" if peri is None else f"{peri:.1f}"
        print(f"  {label}: residual={rs} hmax={hs} peri={ps}")
        return rec

    add_coupled("baseline_fp0.85", "fixed_coarse", {"kind": "none", "extra_mass_kg": 0.0})
    kite_surf = {"kind": "kite", "width": math.sqrt(10.0), "height": math.sqrt(10.0),
                 "sigma": 0.05, "cd": 0.25, "cl": 0.8, "extra_mass_kg": 10.0 * 0.05,
                 "n_hairs": 16, "hair_len": 0.12}
    add_coupled("kite_fixed_open_A10", "fixed_open", kite_surf)
    add_coupled("kite_fixed_reefed_A10", "fixed_reefed", kite_surf)
    add_coupled("kite_adaptive_ungated_A10", "adaptive_ungated", kite_surf)
    add_coupled("kite_adaptive_gated_A10", "adaptive_gated", kite_surf)
    line_surf = {"kind": "line", "line_m": 500.0, "line_d_m": 0.001,
                 "line_deploy_h_m": 60_000.0, "extra_mass_kg": 0.2}
    add_coupled("line_fixed_L500_dep60", "fixed_open", line_surf)
    add_coupled("line_adaptive_ungated_L500_dep60", "adaptive_ungated", line_surf)
    add_coupled("line_adaptive_gated_L500_dep60", "adaptive_gated", line_surf)

    print("STRAW liner...")
    evac = next(c for c in guide["cases"] if c["label"] == "straw_evac80_openloop_fp0.85")
    accel_series = []
    for s in wind_cut:
        a = (3.0 * G_STD - G_STD) if s["thrusting"] else 0.0
        accel_series.append({"t_s": s["t_s"], "a_m_s2": a, "dt": 0.25})
    straw = {}
    for mode in modes:
        fl = straw_liner_run(mode, accel_series, gate, admit_pos)
        assess("untangle", max(1, fl.stats["tangle_events"]))
        straw[mode] = {
            "recycled_residual_m_s": evac["residual_m_s"],
            "recycled_h_max_km": evac["h_max_km"],
            "recycled_perigee_km": evac["perigee_km"],
            "residual_m_s": evac["residual_m_s"],
            "h_max_km": evac["h_max_km"],
            "perigee_km": evac["perigee_km"],
            "locked": False,
            "binding": "propellant + gravity; liner is secondary motion only",
            "stats": {k: fl.stats[k] for k in fl.stats},
            "trace": {"t_s": fl.trace_t, "tip_m": fl.trace_tip, "dof": fl.trace_dof, "E_J": fl.trace_E},
        }

    print("Adaptive light sail...")
    best_sail = next(
        c for c in sailj["no_track"]
        if c.get("P_W") == 1e10 and c.get("area_m2") == 100.0 and c.get("sigma_kg_m2") == 0.01
        and c.get("residual_after_m_s", 9e9) < 1000
    )
    base = coupled[0]
    h_start = best_sail["h_start_km"] * 1000.0
    v_start = best_sail["v_start_m_s"]
    gamma_start = base["gamma_burnout_deg"]
    mass_sail = best_sail["mass_kg"]
    omega = LS.omega_in_plane(kourou["lat"], kourou.get("elev_m", 0.0) or 0.0, 90.0)
    rho_sail = getattr(LS, "RHO_SAIL", 0.90)
    sail_runs = []
    for mode in ("fixed_open", "adaptive_ungated", "adaptive_gated"):
        print(f"  sail {mode}...")
        rec = integrate_sail_adaptive(
            h_start, v_start, gamma_start, mass_sail, 100.0, rho_sail,
            1.0e10, kourou.get("elev_m", 0.0) or 0.0, omega,
            mode=mode, gate=gate, admit_pos=admit_pos,
            theta0_downrange_m=best_sail.get("downrange_start_m", 80_000.0),
            dart_area=dart["area"], dart_cd=dart["cd"], sigma_kg_m2=0.01,
        )
        rec["label"] = f"sail_{mode}_10GW_A100"
        rec["residual_before_m_s"] = best_sail["residual_before_m_s"]
        rec["P_W"] = 1.0e10
        rec["area0_m2"] = 100.0
        rec["site_id"] = "kourou"
        assess("orbit_lock" if rec.get("locked") else "fail")
        sail_runs.append(rec)
        print(f"    residual {rec['residual_after_m_s']:.1f} open_mean={rec['mean_open']:.2f} Teq={rec['peak_Teq_K']:.0f}")

    residuals = {
        "baseline": base["residual_m_s"],
        "kite_gated": next(c["residual_m_s"] for c in coupled if c["label"] == "kite_adaptive_gated_A10"),
        "line_gated": next(c["residual_m_s"] for c in coupled if c["label"] == "line_adaptive_gated_L500_dep60"),
        "straw_evac_recycled": evac["residual_m_s"],
        "sail_gated": next(c["residual_after_m_s"] for c in sail_runs if "adaptive_gated" in c["label"]),
    }
    rec_arr = [residuals[k] for k in residuals]
    recombine = sim.recombine(rec_arr, damping=0.25)
    assess("damper_reconcile")

    recycled = {
        "no_track_kourou_fp085": guide["baseline_recycled_no_track"],
        "confirmatory_baseline": {
            "residual_m_s": base["residual_m_s"],
            "h_max_km": base["h_max_km"],
            "perigee_km": base["perigee_km"],
            "h_burnout_km": base["h_burnout_km"],
            "v_burnout_m_s": base["v_burnout_m_s"],
            "peak_Teq_K": base["peak_Teq_K"],
        },
        "guidance_headlines": {
            "kite_A10_fp085": 1333.26842177242,
            "line_L500_dep60_fp085": 2791.214238708925,
            "lane_gated_openloop_fp085": 643.9670082481089,
            "straw_evac80_openloop_fp085": evac["residual_m_s"],
            "straw_evac_h_max_km": evac["h_max_km"],
            "straw_evac_peri_km": evac["perigee_km"],
        },
        "light_sail_best_no_track": {
            "P_W": best_sail["P_W"], "area_m2": best_sail["area_m2"],
            "sigma_kg_m2": best_sail["sigma_kg_m2"],
            "residual_before_m_s": best_sail["residual_before_m_s"],
            "residual_after_m_s": best_sail["residual_after_m_s"],
            "perigee_after_km": best_sail["perigee_after_km"],
            "h_max_km": best_sail["h_max_km"],
            "peak_Teq_K": best_sail["peak_Teq_K"],
            "t_on_s": best_sail["t_on_s"],
            "binding": best_sail.get("binding"),
        },
    }
    transcriber_n = len(getattr(transcriber, "entries", getattr(transcriber, "lines", getattr(transcriber, "stream", []))))
    try:
        nexus_n = len(nexus.store) if hasattr(nexus, "store") else len(getattr(nexus, "items", {}))
    except Exception:
        nexus_n = 3

    payload = {
        "status": "Speculative modeling only. Not an engineering design, flight plan, or siting recommendation.",
        "prepared": "2026-11-27 America/Denver",
        "dart": {k: dart[k] for k in dart if k != "hollow"} | {"hollow_k": 0.8},
        "admit": admit,
        "recycled": recycled,
        "standalone": {
            k: {m: {kk: vv for kk, vv in standalone[k][m].items() if kk != "trace"}
                | {"trace_len": len(standalone[k][m]["trace"]["t_s"])}
                for m in standalone[k]}
            for k in standalone
        },
        "coupled": coupled,
        "straw": {m: {kk: vv for kk, vv in straw[m].items() if kk != "trace"} for m in straw},
        "sail": sail_runs,
        "residuals": residuals,
        "recombine": recombine if isinstance(recombine, dict) else {"value": recombine},
        "levy_total": levy.total,
        "transcriber_n": transcriber_n,
        "nexus_n": nexus_n,
        "assumptions": [
            "Speculative mapping only; Pixar methods are film-production techniques, not launch hardware.",
            "Adaptive target edge length follows Waggoner & de Goes 2022 (Lmin/Lmax interpolation) with live Oroboro weights in place of painted vertex weights.",
            "Keyhair / interpolant layering follows Petrovic et al. TM #06-08 and Montell et al. 2022.",
            "Velocity smoothing and density-grid refinement follow Petrovic et al.; orientation-dependent hair coupling is the directional term they describe.",
            "Shape-hold after wind follows Iben, Brooks & Bolwyn 2019. Untangle is a reduced history-free proximity push in the spirit of Baraff, Witkin & Kass 2003, not their full GIA/flypaper algorithm.",
            "Fizt / implicit large-step cloth integration is cited from Kim & Eberle 2022; the 1998 Baraff & Witkin paper they build on was affiliated with CMU at publication.",
            "Coupled kite/line aero uses the same CL/CD and 10 m2 / 500 m x 1 mm labels as the guidance addendum. Adaptive openness is new.",
            "Evacuated STRAW leftovers are recycled; the liner furn does not change residual.",
            "Light-sail start, 10 GW / 100 m2 / 0.01 kg m^-2, residual shutter, and site LOS are recycled from light_sail_push.json; only area/mesh adaptation is new.",
            "Lock remains residual <= 1 m/s and perigee >= 200 km. No site or device is recommended.",
        ],
        "citations_fetched": [
            {"id": "Petrovic2006", "title": "Volumetric Methods for Simulation and Rendering of Hair",
             "authors": "Lena Petrovic, Mark Henne, John Anderson",
             "venue": "Pixar Technical Memo #06-08 (2005 SIGGRAPH Talks PDF on the current library)",
             "url": "https://research.pixar.com/docs/2005.SiggraphTalks.PHA.pdf"},
            {"id": "BaraffWitkinKass2003", "title": "Untangling Cloth",
             "authors": "David Baraff, Andrew Witkin, Michael Kass",
             "venue": "SIGGRAPH 2003, Pixar Animation Studios",
             "url": "https://research.pixar.com/docs/2003.SiggraphPapers.BWK.pdf"},
            {"id": "Iben2019", "title": "Holding the Shape in Hair Simulation",
             "authors": "Hayley Iben, Jacob Brooks, Christopher Bolwyn",
             "venue": "SIGGRAPH 2019 Talks, Pixar Animation Studios",
             "url": "https://research.pixar.com/docs/2019.SiggraphTalks.IBB.pdf"},
            {"id": "WaggonerDeGoes2022", "title": "Revamping the Cloth Tailoring Pipeline at Pixar",
             "authors": "Christine Waggoner, Fernando de Goes",
             "venue": "SIGGRAPH 2022 Talks",
             "url": "https://research.pixar.com/docs/2022.SiggraphTalks.WG.pdf"},
            {"id": "Montell2022", "title": "Hair Emoting with Style Guides in Turning Red",
             "authors": "Brandon Montell, Fernando de Goes, Jacob Brooks",
             "venue": "SIGGRAPH 2022 Talks",
             "url": "https://research.pixar.com/docs/2022.SiggraphTalks.MGB.pdf"},
            {"id": "KimEberle2022",
             "title": "Dynamic Deformables: Implementation and Production Practicalities (Now With Code!)",
             "authors": "Theodore Kim, David Eberle",
             "venue": "SIGGRAPH 2022 Course",
             "url": "https://research.pixar.com/docs/2022.SiggraphCourses.KE.pdf"},
            {"id": "BrooksEberleBrowning2026", "title": "Blazing a New Trail of Curls",
             "authors": "Jacob Brooks, David Eberle, Alan Browning",
             "venue": "SIGGRAPH 2026 Talks, Pixar Animation Studios",
             "url": "https://research.pixar.com/docs/2026.SiggraphTalks.BEB.pdf"},
            {"id": "BaraffWitkin1998", "title": "Large Steps in Cloth Simulation",
             "authors": "David Baraff, Andrew Witkin",
             "venue": "SIGGRAPH 1998; Robotics Institute, Carnegie Mellon University (the model Kim & Eberle 2022 state Fizt is built on). Not a Pixar-affiliated publication in 1998.",
             "url": "https://www.cs.cmu.edu/~baraff/papers/sig98.pdf"},
        ],
    }
    traces_full = {
        "standalone": {k: {m: standalone[k][m]["trace"] for m in standalone[k]} for k in standalone},
        "straw": {m: straw[m]["trace"] for m in straw},
        "wind_cut": [{"t_s": s["t_s"], "q_Pa": s["q_Pa"], "h_m": s["h_m"], "v_m_s": s["v_m_s"]}
                     for s in wind_cut[::2]],
    }
    out_path = OUT / "fur_fabric_adaptive.json"
    out_path.write_text(json.dumps(payload, indent=2, default=lambda o: float(o) if isinstance(o, (np.floating,)) else int(o) if isinstance(o, (np.integer,)) else str(o)))
    trace_path = OUT / "fur_fabric_adaptive_traces.json"
    trace_path.write_text(json.dumps(traces_full, default=lambda o: float(o) if isinstance(o, (np.floating,)) else int(o) if isinstance(o, (np.integer,)) else str(o)))
    print("Wrote", out_path)
    print("Wrote", trace_path)
    print("levy_total", levy.total, "admit", admit)
    print("residuals", residuals)
    return payload, traces_full

def make_figure(payload, traces):
    fig, axes = plt.subplots(2, 2, figsize=(10.6, 8.2))
    fig.suptitle(
        "Fig. 14  Adaptive fur / fabric (furn) on the recycled no-track setup\n"
        "Speculative modeling only",
        fontsize=11, color="#1f3a5f", y=0.98,
    )
    colors = {
        "fixed_coarse": "#7a8b99",
        "fixed_fine": "#1f3a5f",
        "adaptive_ungated": "#b85c38",
        "adaptive_gated": "#2e7d4f",
        "fixed_open": "#7a8b99",
        "fixed_reefed": "#5a6a78",
    }
    labels = {
        "fixed_coarse": "fixed coarse",
        "fixed_fine": "fixed fine",
        "adaptive_ungated": "adaptive, ungated",
        "adaptive_gated": "adaptive, Oroboro-gated",
        "fixed_open": "fixed open",
        "fixed_reefed": "fixed reefed",
    }

    ax = axes[0, 0]
    tr = traces["standalone"]["gust"]
    for mode in ("fixed_coarse", "fixed_fine", "adaptive_ungated", "adaptive_gated"):
        ax.plot(tr[mode]["t_s"], tr[mode]["tip_m"], color=colors[mode], lw=1.5, label=labels[mode])
    ax.axvline(5.0, color="k", ls="--", lw=0.7, alpha=0.6)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("secondary-motion tip (m)")
    ax.set_title("A.  Gust then calm: shape return (Iben-style hold)")
    ax.legend(fontsize=7, loc="upper right")
    ax.grid(True, alpha=0.3)

    ax = axes[0, 1]
    st = payload["standalone"]["ascent_playback"]
    modes = ("fixed_coarse", "fixed_fine", "adaptive_ungated", "adaptive_gated")
    xs = np.arange(len(modes))
    width = 0.22
    dof = [st[m]["stats"]["mean_dof"] for m in modes]
    tip = [st[m]["stats"]["tip_rms"] * 100.0 for m in modes]
    diss = [abs(st[m]["stats"]["W_damp_J"] + st[m]["stats"]["W_smooth_J"]) for m in modes]
    tang = [st[m]["stats"]["tangle_events"] for m in modes]
    ax.bar(xs - 1.5 * width, dof, width, color="#1f3a5f", label="mean sim DOF")
    ax.bar(xs - 0.5 * width, tip, width, color="#2e7d4f", label="tip RMS (cm)")
    ax.bar(xs + 0.5 * width, diss, width, color="#b85c38", label="|damping + smooth work| (J)")
    ax.bar(xs + 1.5 * width, tang, width, color="#7a8b99", label="tangle events")
    ax.set_xticks(xs)
    ax.set_xticklabels([labels[m].replace(", ", "\n") for m in modes], fontsize=7)
    ax.set_title("B.  Ascent-playback: adaptive vs fixed mesh")
    ax.legend(fontsize=6.5, loc="upper right")
    ax.grid(True, axis="y", alpha=0.3)

    ax = axes[1, 0]
    rows = []
    base = next(c for c in payload["coupled"] if c["label"] == "baseline_fp0.85")
    rows.append(("no-track\nbaseline", base["residual_m_s"], colors["fixed_fine"]))
    rec = payload["recycled"]["guidance_headlines"]
    rows.append(("kite 10 m$^2$\n(recycled)", rec["kite_A10_fp085"], "#9aa7b2"))
    for lab, name in (
        ("kite\nfixed reefed", "kite_fixed_reefed_A10"),
        ("kite\ngated", "kite_adaptive_gated_A10"),
        ("line 60 km\n(recycled)", None),
        ("line\ngated", "line_adaptive_gated_L500_dep60"),
        ("evac straw\n(recycled)", None),
        ("sail 10 GW\n(recycled)", None),
        ("sail\ngated", None),
    ):
        if name:
            c = next(x for x in payload["coupled"] if x["label"] == name)
            rows.append((lab, c["residual_m_s"],
                         colors["adaptive_gated"] if "gated" in lab else colors["fixed_coarse"]))
        elif "line 60" in lab:
            rows.append((lab, rec["line_L500_dep60_fp085"], "#9aa7b2"))
        elif "evac" in lab:
            rows.append((lab, rec["straw_evac80_openloop_fp085"], "#3a6d8c"))
        elif "sail 10" in lab:
            rows.append((lab, payload["recycled"]["light_sail_best_no_track"]["residual_after_m_s"], "#9aa7b2"))
        else:
            s = next(x for x in payload["sail"] if "adaptive_gated" in x["label"])
            rows.append((lab, s["residual_after_m_s"], colors["adaptive_gated"]))
    xs = np.arange(len(rows))
    ax.bar(xs, [r[1] for r in rows], color=[r[2] for r in rows])
    ax.set_xticks(xs)
    ax.set_xticklabels([r[0] for r in rows], fontsize=6.4)
    ax.set_ylabel("two-burn residual to 200 km circular (m/s)")
    ax.set_title("C.  Coupled leftovers, f$_p$=0.85 Kourou")
    ax.axhline(base["residual_m_s"], color="#1f3a5f", ls="--", lw=0.7)
    ax.grid(True, axis="y", alpha=0.3)

    ax = axes[1, 1]
    tr = traces["standalone"]["ascent_playback"]
    wind = traces["wind_cut"]
    tw = [w["t_s"] for w in wind]
    qw = [w["q_Pa"] for w in wind]
    ax2 = ax.twinx()
    ax2.fill_between(tw, qw, color="#cfd8e3", alpha=0.7)
    ax2.set_ylabel("dynamic pressure q (Pa)", color="#5a6a78")
    for mode in ("fixed_fine", "adaptive_ungated", "adaptive_gated"):
        ax.plot(tr[mode]["t_s"], tr[mode]["tip_m"], color=colors[mode], lw=1.4, label=labels[mode])
    ax.set_xlabel("ascent time (s)")
    ax.set_ylabel("secondary-motion tip (m)")
    ax.set_title("D.  Playback on the recycled no-track q pulse")
    ax.legend(fontsize=7, loc="upper right")
    ax.grid(True, alpha=0.3)

    fig.tight_layout(rect=[0, 0.01, 1, 0.93], w_pad=2.0, h_pad=1.6)
    path = OUT / "fig14_fur_fabric_adaptive.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)
    print("Wrote", path)
    return str(path)


if __name__ == "__main__":
    payload, traces = run()
    make_figure(payload, traces)
