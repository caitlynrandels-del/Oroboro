"""Bit-identity check: toggles off must reproduce the pre-t96u model exactly."""
import sys, json
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent) + "/metastasis-native")
from oro_native import run, load_params
P = load_params()
CONDS = {
 "base_g1": dict(levy_gain=1.0),
 "base_g005": dict(levy_gain=0.05),
 "light_comb_up05": dict(levy_gain=0.05, light=True, light_mode="combined", light_strength=0.5, light_timing="upstream", integrated=True, extraction_coloring="preserve"),
 "plumb_leak06": dict(levy_gain=0.05, plumbing=True, plumbing_strength=0.5, plumbing_leak=0.6, plumbing_seal=1.0, plumbing_stages=1, plumbing_timing="upstream", plumbing_magnet=False, plumbing_oasis=True),
 "plumb_leak03_post": dict(levy_gain=0.05, plumbing=True, plumbing_strength=0.5, plumbing_leak=0.3, plumbing_seal=1.0, plumbing_stages=1, plumbing_timing="post_settling", plumbing_magnet=False, plumbing_oasis=True),
 "pre_integration": dict(integrated=False),
}
KEYS = ["overt", "dorm_alive", "levy", "n_frustrated", "consensus_ok", "pressure_mean", "extracted"]
out = {}
for name, ov in CONDS.items():
    for c in P["cancers"]:
        for k in range(3):
            sd = P["cancers"][c]["seed"] * 1000 + k
            r = run(c, sd, P, native_overrides=ov, sig=True)
            out[f"{name}|{c}|{k}"] = [r["_sig"]] + [r[x] for x in KEYS]
mode = sys.argv[1]
path = str(__import__("pathlib").Path(__file__).resolve().parent) + "/sig_reference.json"
if mode == "save":
    json.dump(out, open(path, "w"), indent=0); print("saved", len(out))
else:
    ref = json.load(open(path)); bad = [k for k in ref if ref[k] != out[k]]
    print("compared", len(ref), "mismatches", len(bad), bad[:5])
