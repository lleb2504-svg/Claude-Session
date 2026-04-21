import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch

df = pd.read_csv("meridian_snapshot.csv")
panel_end = pd.to_datetime("2026-03-01")
df["report_effective_date"] = pd.to_datetime(df["report_effective_date"])
df["is_active"] = df["report_effective_date"] == panel_end
active = df[df["is_active"]].copy()
departed = df[~df["is_active"]].copy()

RISK   = "#c0392b"
WARN   = "#e67e22"
GREEN  = "#27ae60"
BLUE   = "#2980b9"
DARK   = "#2c3e50"
LIGHT  = "#f7f8fa"
MID    = "#7f8c8d"

fig = plt.figure(figsize=(18, 12))
fig.patch.set_facecolor(LIGHT)
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.52, wspace=0.38)

# ── RISK 1: Early-tenure voluntary attrition ──────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
df["tenure_band"] = pd.cut(df["tenure_months"],
    bins=[0, 12, 24, 48, 84, 999],
    labels=["<1 yr", "1–2 yr", "2–4 yr", "4–7 yr", "7+ yr"])
vol = df[df["reason_for_departure"] == "Voluntary"]
vol_rate = (vol.groupby("tenure_band", observed=True).size() /
            df.groupby("tenure_band", observed=True).size() * 100).round(1)
bar_colors = [RISK if v > 18 else WARN if v > 14 else GREEN for v in vol_rate]
bars = ax1.bar(vol_rate.index, vol_rate.values, color=bar_colors,
               edgecolor="white", width=0.6)
for b, v in zip(bars, vol_rate.values):
    ax1.text(b.get_x() + b.get_width()/2, v + 0.3, f"{v}%",
             ha="center", fontsize=10, fontweight="bold", color=DARK)
ax1.set_ylim(0, 28)
ax1.set_ylabel("Voluntary Attrition Rate", fontsize=9)
ax1.set_title("RISK 1\nNew-Hire Attrition: 21% in Year 1", fontsize=11,
              fontweight="bold", color=RISK, loc="left")
ax1.set_facecolor(LIGHT); ax1.spines[["top","right"]].set_visible(False)
ax1.tick_params(axis="x", labelsize=9)

# ── RISK 2: Attrition by function (top 5 worst) ───────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
func_total = df.groupby("function_name").size()
func_dep   = departed.groupby("function_name").size()
func_attr  = (func_dep / func_total * 100).sort_values(ascending=True)
top5 = func_attr.tail(5)
bar_colors2 = [RISK if v > 24 else WARN if v > 21 else MID for v in top5]
ax2.barh(top5.index, top5.values, color=bar_colors2, edgecolor="white", height=0.55)
for i, v in enumerate(top5.values):
    ax2.text(v + 0.3, i, f"{v:.1f}%", va="center", fontsize=10,
             fontweight="bold", color=DARK)
ax2.set_xlim(0, 32)
ax2.set_xlabel("Total Attrition Rate", fontsize=9)
ax2.set_title("RISK 2\nProduct, CS & Sales Losing 1-in-4", fontsize=11,
              fontweight="bold", color=RISK, loc="left")
ax2.set_facecolor(LIGHT); ax2.spines[["top","right"]].set_visible(False)
ax2.tick_params(axis="y", labelsize=9)

# ── RISK 3: Gender voluntary attrition + pay gap ─────────────────────────
ax3 = fig.add_subplot(gs[0, 2])
us = df[df["location"].isin(["SF", "NYC", "Austin", "Remote-US"])]
us_active = active[active["location"].isin(["SF", "NYC", "Austin", "Remote-US"])]
vol_us = us[us["reason_for_departure"] == "Voluntary"]
genders = ["Man", "Woman"]
vol_rates_g = [(vol_us[vol_us["gender"]==g].shape[0] /
                us[us["gender"]==g].shape[0] * 100) for g in genders]
pay_med = [us_active[us_active["gender"]==g]["base_salary"].median()/1000 for g in genders]

x = np.arange(len(genders))
w = 0.35
ax3b = ax3.twinx()
b1 = ax3.bar(x - w/2, vol_rates_g, width=w, color=[BLUE, RISK],
             alpha=0.85, edgecolor="white", label="Vol. attrition rate")
b2 = ax3b.bar(x + w/2, pay_med, width=w, color=[BLUE, RISK],
              alpha=0.35, edgecolor="white", label="Median salary $k")
ax3.set_xticks(x); ax3.set_xticklabels(genders, fontsize=10)
ax3.set_ylabel("Voluntary Attrition %", fontsize=9, color=DARK)
ax3b.set_ylabel("Median Base Salary ($k)", fontsize=9, color=MID)
for i, (vr, pm) in enumerate(zip(vol_rates_g, pay_med)):
    ax3.text(i - w/2, vr + 0.3, f"{vr:.1f}%", ha="center",
             fontsize=10, fontweight="bold", color=DARK)
    ax3b.text(i + w/2, pm + 1, f"${pm:.0f}k", ha="center",
              fontsize=9, color=MID)
ax3.set_title("RISK 3\nWomen Leave More, Earn Less (US)", fontsize=11,
              fontweight="bold", color=RISK, loc="left")
ax3.set_facecolor(LIGHT); ax3.spines[["top","right"]].set_visible(False)
ax3b.spines[["top","right"]].set_visible(False)
ax3.set_ylim(0, 24); ax3b.set_ylim(0, 220)

# ── BRIGHT SPOT 1: Acquired cohort vs overall ────────────────────────────
ax4 = fig.add_subplot(gs[1, 0])
sources = ["acquired", "referral", "campus", "agency", "direct"]
ret = (df.groupby("hire_source").apply(lambda x: x["is_active"].sum()/len(x)*100)
       .reindex(sources).round(1))
bar_colors4 = [GREEN if v >= 79 else WARN if v >= 76 else RISK for v in ret]
bars4 = ax4.bar(sources, ret.values, color=bar_colors4, edgecolor="white", width=0.6)
for b, v in zip(bars4, ret.values):
    ax4.text(b.get_x() + b.get_width()/2, v + 0.4, f"{v:.1f}%",
             ha="center", fontsize=10, fontweight="bold", color=DARK)
ax4.set_ylim(65, 88)
ax4.set_ylabel("Still Active (%)", fontsize=9)
ax4.set_title("BRIGHT SPOT 1\nM&A Cohort Is Sticky (79.5% Retained)", fontsize=11,
              fontweight="bold", color=GREEN, loc="left")
ax4.set_facecolor(LIGHT); ax4.spines[["top","right"]].set_visible(False)
ax4.tick_params(axis="x", labelsize=9)

# ── BRIGHT SPOT 2: Low performers leaving ────────────────────────────────
ax5 = fig.add_subplot(gs[1, 1])
ratings = [1, 2, 3, 4, 5]
lv_pct  = [vol[vol["last_performance_rating"]==r].shape[0] / len(vol) * 100 for r in ratings]
ac_pct  = [active[active["last_performance_rating"]==r].shape[0] / len(active) * 100 for r in ratings]
x5 = np.arange(len(ratings))
w5 = 0.35
ax5.bar(x5 - w5/2, lv_pct, width=w5, color=RISK, alpha=0.75,
        edgecolor="white", label="Vol. leavers")
ax5.bar(x5 + w5/2, ac_pct, width=w5, color=GREEN, alpha=0.75,
        edgecolor="white", label="Active today")
ax5.set_xticks(x5)
ax5.set_xticklabels(["1\n(Low)", "2", "3", "4", "5\n(High)"], fontsize=9)
ax5.set_ylabel("% of Group", fontsize=9)
ax5.legend(fontsize=9, frameon=False)
ax5.set_title("BRIGHT SPOT 2\nLow Performers Leaving, High Performers Staying",
              fontsize=11, fontweight="bold", color=GREEN, loc="left")
ax5.set_facecolor(LIGHT); ax5.spines[["top","right"]].set_visible(False)
ax5.annotate("3.4× over-\nrepresented\nin leavers", xy=(0 - w5/2, lv_pct[0]),
             xytext=(-0.15, lv_pct[0]+3.5), fontsize=8, color=RISK,
             arrowprops=dict(arrowstyle="->", color=RISK, lw=1))
ax5.annotate("Under-\nrepresented\nin leavers", xy=(3 + w5/2, ac_pct[3]),
             xytext=(3.2, ac_pct[3]+4), fontsize=8, color=GREEN,
             arrowprops=dict(arrowstyle="->", color=GREEN, lw=1))

# ── BRIGHT SPOT 3: Long-tenured stickiness + location risk callout ────────
ax6 = fig.add_subplot(gs[1, 2])
loc_attr = (departed.groupby("location").size() /
            df.groupby("location").size() * 100).sort_values(ascending=True)
bar_colors6 = [RISK if v > 25 else WARN if v > 22 else GREEN for v in loc_attr]
ax6.barh(loc_attr.index, loc_attr.values, color=bar_colors6,
         edgecolor="white", height=0.6)
for i, v in enumerate(loc_attr.values):
    ax6.text(v + 0.3, i, f"{v:.1f}%", va="center", fontsize=10,
             fontweight="bold", color=DARK)
ax6.set_xlim(0, 34)
ax6.set_xlabel("Total Attrition Rate", fontsize=9)
ax6.set_title("NYC & Dublin: Hidden Location Risk\n(26% attrition vs 20% Sydney/Austin)",
              fontsize=11, fontweight="bold", color=WARN, loc="left")
ax6.set_facecolor(LIGHT); ax6.spines[["top","right"]].set_visible(False)
ax6.tick_params(axis="y", labelsize=9)

fig.suptitle(
    "Meridian Technologies — People Risk & Bright Spots  |  CPO Board View  |  Apr 2026\n"
    "n = 2,500 employees  ·  36-month panel  ·  1,928 active  ·  572 departed",
    fontsize=13, fontweight="bold", color=DARK, y=0.99)

plt.savefig("meridian_board.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
print("Saved meridian_board.png")
