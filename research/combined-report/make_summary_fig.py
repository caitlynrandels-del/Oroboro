# Summary chart built ONLY from numbers stated in the source addenda (no new simulation).
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
rows = [  # (label, residual m/s, group, source)
 ("Repeater f_p 0.05, 0° exit (all 14 sites)", 0, "lock"),
 ("Repeater f_p 0.30, every setup", 0, "lock"),
 ("0° / 80 km exit, best azimuth (Baikonur)", 37, "track"),
 ("0° / 80 km exit, due east (Baikonur)", 66, "track"),
 ("Evac-tube dart, 5° (no stage)", 407, "track"),
 ("5° tilt, 80 km (no stage)", 431, "track"),
 ("Staged config (corrected; was 256)", 1148, "track"),
 ("No track, f_p 0.85 (Kourou)", 661, "notrack"),
 ("No track + light sail 10 GW", 514, "notrack"),
 ("No track + evacuated straw", 595, "notrack"),
 ("No track + lane-keeping (gated)", 644, "notrack"),
 ("No track + smart magnets (Earth field)", 661, "notrack"),
 ("No track + kite 10 m²", 1333, "notrack"),
 ("No track + adaptive fishing line", 1361, "notrack"),
 ("No track + fishing line (from 60 km)", 2791, "notrack"),
 ("Evac straw + 0.1 bar pneumatic push (late)", 666, "notrack"),
]
col={"lock":"#2e7d4f","track":"#2f5d8a","notrack":"#b5553c"}
fig,ax=plt.subplots(figsize=(8.2,5.6),dpi=200)
y=range(len(rows))[::-1]
for yi,(l,v,g) in zip(y,rows):
    ax.barh(yi, max(v,8), color=col[g], height=0.66)
    ax.text(max(v,8)+30, yi, "LOCKED (0)" if v==0 else f"{v:,}", va="center", fontsize=8.5, color="#222", fontweight="bold" if v==0 else None)
ax.set_yticks(list(y)); ax.set_yticklabels([r[0] for r in rows], fontsize=8.5)
ax.set_xlabel("Remaining speed gap to a 200 km circular orbit (m/s, model output; lower is better)", fontsize=9)
ax.set_xlim(0,3200); ax.grid(axis="x",alpha=.3)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=col["lock"],label="Small paid late burn (redstone repeater)"),
  Patch(color=col["track"],label="Track / evacuated-tube exits, no late burn"),
  Patch(color=col["notrack"],label="Track removed, other add-ons")],fontsize=8,loc="center right")
ax.set_title("Only the small late burn closed the gap (speculative model outputs)",fontsize=10.5)
for s in ["top","right"]: ax.spines[s].set_visible(False)
plt.tight_layout(); plt.savefig("figures/figS1_launch_gap_summary.png")
