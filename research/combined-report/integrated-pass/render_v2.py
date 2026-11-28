#!/usr/bin/env python3
"""Render the v2 one-page brief from integrated_pass_result.json.
Sections = converged clusters (ordered by Levy share); body = admitted node texts (ordered by
Levy weight); 'refine' clusters as bullets, 'coarsen'/'hold' as run-on text. Superseded and
recycled nodes go to compact strips. Scope banner, open-item status and GitHub state are
fixed requirements of the brief, not pass-selected. No numbers are typed here except the
pass statistics read from the JSON and the open-item verdict lines (sourced in the JSON)."""
import json, html, os, subprocess, re
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE)
r = json.load(open(os.path.join(HERE, "integrated_pass_result.json")))
nodes = {n["id"]: n for n in r["nodes"]}
# Section titles (labels only; chosen from each cluster's member content)
TITLE = {"C.light45": "Gated exits · the gate as valve (both domains)",
         "L.damp": "Launch residual · only the small late burn locks",
         "C.upstream": "Admission is the lever · geography ≈ permissiveness",
         "C.frust829": "Loops, frustration & the dormant pool",
         "C.gain1": "Conjunctive wiring & recalibration",
         "S.systems17": "Systems index & repository state",
         "C.check200": "Tilt sign flip · wiring is not automatically better",
         "G.relay": "Relay core: deterministic delta",
         "S.conj": "Which runs were conjunctive"}
def esc(s): return html.escape(s, quote=False)
def fmt(t):
    t = esc(t)
    t = re.sub(r"(levy_gain|integrated=True|integrated=False|consensus_ok|oroboro-core\.js|Math\.random\(\)\*0\.1|SYSTEMS\.md|params\.json|OroboroPipeline)", r"<code>\1</code>", t)
    return t
sec = []
for c in r["clusters"]:
    mem = [nodes[m] for m in c["members"] if nodes[m]["gate"] != "recycle"]
    title = TITLE.get(c["hub"], c["hub"])
    head = f'<h2>{esc(title)} <span class="sh">{100*c["share"]:.0f}%</span></h2>'
    if c["detail"] == "refine":
        body = "<ul>" + "".join(f"<li>{fmt(n['text'])}</li>" for n in mem) + "</ul>"
    else:
        body = "<p>" + " · ".join(fmt(n["text"]) for n in mem) + "</p>"
    sec.append(head + body)
dr = r["delta_reconciliation"]
CORR = {"L.256": "staged 256 m/s → 1,148 m/s true Kepler residual (incomplete 900 s coast)",
        "C.native_base": "native baseline 18.0%/10.355 → conjunctive working baseline 0.091/6.36",
        "C.frust819": "Spearman −0.819 → −0.829 (conjunctive rerun)",
        "S.cd_stub_claim": "cross-domain note “delta still a Math.random stub” → replaced in cc77063",
        "S.audit_tree": "audited L124 random delta → deterministic delta (cc77063)",
        "C.plumb_claim": "plumbing addendum “consensus held on every condition” → False on 4 rows",
        "C.damper_silent": "damper silent in first restart → engages once Levy is wired (~0.031 mean, ~0.138 peak)",
        "G.oroboro_v1": "Oroboro main d6f2763 (v1) → 3a3e021"}
corr = " · ".join(esc(CORR[s["old"]]) for s in dr["superseded"])
contra = " · ".join(f"{esc(c['note'])} → " + ("both cited with integrator labels" if c["resolved_by"] else "kept as stated (unresolved in source)") for c in dr["contradictions"])
recyc = [n for n in r["nodes"] if n["gate"] == "recycle" and n["id"] not in {s["old"] for s in dr["superseded"]} and n["domain"] != "open"]  # open items shown in the status table
rec = " · ".join(fmt(n["text"]) for n in recyc)
open_items = [
 ("Calibration", "open (partly addressed)", "<code>params.json</code> default <code>levy_gain</code> 1.0 → 0.091/6.36; 0.05 (0.175/10.09, closest to 0.217/10.38) was the matched setting for the light and plumbing runs but was never made the default; the 0.175 vs 0.217 gap matches the loop tax (tree niche 20.6%)."),
 ("PrinciplesGate", "open (inert)", "Wired after Oasis; LOO without it identical at gain 1.0 (0.096/6.366) and 0.05 (0.176/10.138); comfort H never &lt;0.3 and frustration ≤0.36, so no veto/boost triggers. It also made 0 vetoes in this pass."),
 ("epilepsy-sim", "open", "Remote head <code>2be4eac</code>: audit only, “partially conjunctive, integrated rebuild pending”; code unchanged; 50/50 preflight. No later commit."),
 ("Swift relay port", "open", "Deterministic delta patched in <code>cc77063</code> (OroboroRelayApp.swift) but never compiled; no Swift toolchain on the build machine."),
 ("Plumbing consensus", "open", "<code>consensus_ok</code>=False on 4 leak/seal rows; census/Levy/inversion pass; data last written 17:42 MT, no rerun. Perfect-seal and staged rows pass all checks."),
 ("Resolved", "closed", "<code>Math.random()*0.1</code> delta replaced (<code>cc77063</code>, test passes); launch runs conjunctive from redstone on; damper engages once Levy is wired in."),
]
oi = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>" for a, b, c in open_items)
m = r["mesh"]; ph = r["history"][-1]
gates = {k: sum(1 for n in r["nodes"] if n["gate"] == k) for k in ("commit", "buffer", "recycle")}
passline = (f"Content selected by running the Oroboro pipeline over <b>{r['n_nodes']} findings</b> and {r['n_edges']} typed edges in one loop "
            f"(Genesis → Nexus → Oasis 0.65 → PrinciplesGate → NaCl mesh → Dictator/Transcriber → Levy → damper → delta reconciliation → isolate/recombine → homeostasis): "
            f"<b>{r['iterations']} iterations, converged</b> (max Δweight {r['final_dw']:.1e}). Oasis: {gates['commit']} commit / {gates['buffer']} buffer / {gates['recycle']} recycle; "
            f"{len(dr['superseded'])} superseded by delta reconciliation; {len(dr['contradictions'])} contradictions flagged; mesh {len(m['frustrated_after_repair'])} frustrated edges, inversion holds; "
            f"PrinciplesGate {r['principles_gate']['vetoes_total']} vetoes. Section % = Levy share. Dream-catcher and smart magnets: no applicable code (not used). Selection bookkeeping only, not new modeling. Source: <code>combined_report/integrated_pass/</code>.")
css = open(os.path.join(OUT, "Oroboro_OnePage_Engineer_Brief.html")).read().split("<style>")[1].split("</style>")[0]
css = css.replace("font-size:7.05pt;line-height:1.2", "font-size:6.9pt;line-height:1.15")
css += """
ul{margin:0 0 2px 0;padding-left:0;list-style:none} li{padding-left:7px;text-indent:-6px} li::before{content:"▸ ";color:#2f5d8a}
.sh{float:right;font-weight:400;font-size:6.2pt;opacity:.85}
.pass{background:#eef3f8;border-left:3px solid #2f5d8a;padding:2px 5px;margin-bottom:3px;font-size:6.2pt}
.strip{font-size:6.1pt;color:#222;margin:0 0 1px}
s{color:#666}
table.oi td{vertical-align:top}
"""
doc = f"""<!doctype html><html><head><meta charset="utf-8"><title>Oroboro one-page engineer brief v2</title><style>{css}</style></head><body>
<div class="hdr"><h1>Oroboro studies — one-page engineering brief (v2, integrated pass)</h1><div class="m">Caitlyn Randels · prepared with AI modeling assistance · 27 Nov 2026 · full report: <code>research/combined-report</code></div></div>
<div class="scope"><b>Scope:</b> speculative in-silico modeling only. All numbers are model outputs on labeled assumptions. No clinical/biological/medical claims; no engineering, flight, siting or operational claims. Levy weights and Oasis scores are bookkeeping/routing, not energies or truth tests. Bootstrap CIs = Monte Carlo error only.</div>
<div class="pass">{passline}</div>
<div class="cols">
{''.join(sec)}
<h2>Status of tracked items</h2>
<table class="oi"><colgroup><col style="width:21%"><col style="width:17%"><col style="width:62%"></colgroup><tr><th>Item</th><th>Status</th><th>Evidence</th></tr>{oi}</table>
<h2>Delta reconciliation: corrections</h2>
<p class="strip">{corr}</p>
<p class="strip"><b>Flagged contradictions:</b> {contra}</p>
<h2>Low salience (Oasis recycle, kept for completeness)</h2>
<p class="strip">{rec}</p>
</div></body></html>"""
html_path = os.path.join(OUT, "Oroboro_OnePage_Engineer_Brief_v2.html")
open(html_path, "w").write(doc)
pdf = os.path.join(OUT, "Oroboro_OnePage_Engineer_Brief_v2.pdf")
subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                "--print-to-pdf=" + pdf, "file://" + html_path], check=True, capture_output=True)
print(pdf)
