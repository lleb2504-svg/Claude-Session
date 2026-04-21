import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

snap  = pd.read_csv("meridian_snapshot.csv")
panel = pd.read_csv("meridian_panel.csv.gz")
panel["report_effective_date"] = pd.to_datetime(panel["report_effective_date"])
panel_end = pd.to_datetime("2026-03-01")
snap["report_effective_date"] = pd.to_datetime(snap["report_effective_date"])
snap["is_active"]     = snap["report_effective_date"] == panel_end
snap["is_vol_leaver"] = snap["reason_for_departure"] == "Voluntary"
snap["tenure_band"]   = pd.cut(snap["tenure_months"],
    bins=[0,12,24,48,84,999], labels=["<1yr","1-2yr","2-4yr","4-7yr","7yr+"])

vol_snap = snap[snap["is_vol_leaver"]].copy()
vol_snap["tenure_band"] = pd.cut(vol_snap["tenure_months"],
    bins=[0,12,24,48,84,999], labels=["<1yr","1-2yr","2-4yr","4-7yr","7yr+"])

NAVY  = "#1B2A4A"; RED   = "#C0392B"; AMBER = "#E67E22"
GREEN = "#27AE60"; BLUE  = "#2980B9"; LGREY = "#F4F6F7"
MGREY = "#7F8C8D"; DKGREY= "#2C3E50"

fig = plt.figure(figsize=(20, 14))
fig.patch.set_facecolor(LGREY)
gs  = gridspec.GridSpec(3, 3, figure=fig, hspace=0.52, wspace=0.38)

# ── 1. PROMOTION RATE: leavers vs active by tenure band ────────────────────
ax1 = fig.add_subplot(gs[0, 0])
bands   = ["1-2yr","2-4yr","4-7yr","7yr+"]
lv_promo = []
ac_promo = []
for b in bands:
    lv_promo.append(vol_snap[vol_snap["tenure_band"]==b]["last_promotion_month"].notna().mean()*100)
    ac_promo.append(snap[snap["is_active"] & (snap["tenure_band"]==b)]["last_promotion_month"].notna().mean()*100)

x = np.arange(len(bands)); w = 0.35
ax1.bar(x-w/2, lv_promo, width=w, color=RED,  alpha=0.85, edgecolor="white", label="Vol. leavers")
ax1.bar(x+w/2, ac_promo, width=w, color=GREEN, alpha=0.85, edgecolor="white", label="Active today")
for i,(lv,ac) in enumerate(zip(lv_promo,ac_promo)):
    ax1.text(i-w/2, lv+0.5, f"{lv:.0f}%", ha="center", fontsize=9, fontweight="bold", color=RED)
    ax1.text(i+w/2, ac+0.5, f"{ac:.0f}%", ha="center", fontsize=9, fontweight="bold", color=GREEN)
ax1.set_xticks(x); ax1.set_xticklabels(bands, fontsize=9)
ax1.set_ylabel("% Ever Promoted", fontsize=9)
ax1.set_ylim(0, 35)
ax1.legend(fontsize=9, frameon=False)
ax1.set_title("KEY FINDING\nLeavers Rarely Get Promoted",
              fontsize=11, fontweight="bold", color=RED, loc="left")
ax1.set_facecolor(LGREY); ax1.spines[["top","right"]].set_visible(False)
ax1.annotate("3.5× gap\nat 2-4yr", xy=(1+w/2, ac_promo[1]), xytext=(1.6, 28),
             fontsize=8.5, color=DKGREY,
             arrowprops=dict(arrowstyle="->", color=DKGREY, lw=1))

# ── 2. ENGAGEMENT TRAJECTORY before voluntary exit ─────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
vol_ids   = set(vol_snap["worker_id"])
vol_panel = panel[panel["worker_id"].isin(vol_ids)].copy()
vol_panel = vol_panel.sort_values(["worker_id","report_effective_date"])

def months_before_exit(grp):
    last = grp["report_effective_date"].max()
    grp  = grp.copy()
    grp["mte"] = ((last - grp["report_effective_date"]) / pd.Timedelta(days=30.44)).round().astype(int)
    return grp

vt = vol_panel.groupby("worker_id", group_keys=False).apply(months_before_exit)
eng_traj = vt[vt["mte"]<=11].groupby("mte")["engagement_score"].mean().sort_index(ascending=False)

act_eng = panel[panel["report_effective_date"]==panel_end]["engagement_score"].mean()
ax2.plot(range(12), eng_traj.values, color=RED, linewidth=2.5, marker="o",
         markersize=5, label="Pre-exit (leavers)")
ax2.axhline(act_eng, color=GREEN, linestyle="--", linewidth=1.8,
            label=f"Active avg ({act_eng:.2f})")
ax2.set_xticks(range(12))
ax2.set_xticklabels([f"{v}m" for v in eng_traj.index], fontsize=8)
ax2.set_xlabel("Months before departure", fontsize=9)
ax2.set_ylabel("Avg Engagement Score", fontsize=9)
ax2.set_ylim(6.0, 7.5)
ax2.legend(fontsize=9, frameon=False)
ax2.set_title("Engagement Gap Is Persistent,\nNot a Last-Minute Dip",
              fontsize=11, fontweight="bold", color=DKGREY, loc="left")
ax2.set_facecolor(LGREY); ax2.spines[["top","right"]].set_visible(False)
gap = act_eng - eng_traj.mean()
ax2.annotate(f"Persistent\n–{gap:.2f} gap\nvs actives",
             xy=(5, eng_traj.values[5]), xytext=(7, 6.55),
             fontsize=8.5, color=RED,
             arrowprops=dict(arrowstyle="->", color=RED, lw=1))

# ── 3. SEASONAL: exits by month ────────────────────────────────────────────
ax3 = fig.add_subplot(gs[0, 2])
vol_snap["exit_month_num"] = pd.to_datetime(
    vol_snap["termination_month"].fillna(
        vol_snap["report_effective_date"].astype(str).str[:7]),
    errors="coerce").dt.month
monthly = vol_snap.groupby("exit_month_num").size()
month_labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
bar_colors3 = [RED if v == monthly.max() else AMBER if v >= monthly.quantile(0.75) else BLUE
               for v in monthly.values]
bars3 = ax3.bar(month_labels, monthly.values, color=bar_colors3, edgecolor="white", width=0.7)
ax3.axhline(monthly.mean(), color=MGREY, linestyle="--", linewidth=1.2,
            label=f"Monthly avg ({monthly.mean():.0f})")
ax3.set_ylabel("Voluntary Exits", fontsize=9)
ax3.legend(fontsize=9, frameon=False)
ax3.set_title("September Spike: 40% Above\nMonthly Average",
              fontsize=11, fontweight="bold", color=RED, loc="left")
ax3.set_facecolor(LGREY); ax3.spines[["top","right"]].set_visible(False)
ax3.tick_params(axis="x", labelsize=8.5)
ax3.annotate("Post mid-year\nreview window\n(Eng-heavy: 38%)",
             xy=(8, 45), xytext=(9.5, 43),
             fontsize=8, color=RED,
             arrowprops=dict(arrowstyle="->", color=RED, lw=1))

# ── 4. FLAGGED MANAGER: engagement decay ──────────────────────────────────
ax4 = fig.add_subplot(gs[1, :2])
overall_trend = panel.groupby("report_effective_date")["engagement_score"].mean()
for mid, label, col, ls in [
    ("060f8cec1aecbd2c", "Mgr 060f (Engineering, 25-person team)", RED, "-"),
    ("20c21d2b66105bd4", "Mgr 20c2 (Engineering, 22-person team)", AMBER, "-"),
]:
    mgr_p = panel[panel["manager_id"]==mid].groupby("report_effective_date")["engagement_score"].mean()
    ax4.plot(mgr_p.index, mgr_p.values, color=col, linewidth=2.2,
             linestyle=ls, label=label, marker="o", markersize=3)

ax4.plot(overall_trend.index, overall_trend.values, color=GREEN, linewidth=1.8,
         linestyle="--", alpha=0.8, label="Company average")
ax4.set_ylabel("Team Avg Engagement Score", fontsize=9)
ax4.set_ylim(4.5, 7.8)
ax4.legend(fontsize=9, frameon=False)
ax4.set_title("Flagged Managers: 060f Has Been in Decay for 3 Years  ·  20c2 Is Sliding Again After a Brief Recovery",
              fontsize=11, fontweight="bold", color=RED, loc="left")
ax4.set_facecolor(LGREY); ax4.spines[["top","right"]].set_visible(False)
ax4.tick_params(axis="x", labelsize=8.5)
ax4.axvspan(pd.Timestamp("2023-04-01"), pd.Timestamp("2023-04-01"),
            alpha=0, color="white")  # spacer
# Shade the "recovery" window for 20c2
ax4.axvspan(pd.Timestamp("2024-06-01"), pd.Timestamp("2025-05-01"),
            alpha=0.08, color=AMBER)
ax4.annotate("Brief recovery\n(team change?)", xy=(pd.Timestamp("2024-11-01"), 5.8),
             xytext=(pd.Timestamp("2024-01-01"), 5.1),
             fontsize=8, color=AMBER,
             arrowprops=dict(arrowstyle="->", color=AMBER, lw=1))

# ── 5. COMP GAP: vol leavers vs active peers ───────────────────────────────
ax5 = fig.add_subplot(gs[1, 2])
def comp_gap(grp):
    a = grp[grp["is_active"]]["base_salary"].median()
    l = grp[grp["is_vol_leaver"]]["base_salary"].median()
    return ((l - a) / a * 100) if not (pd.isna(a) or pd.isna(l)) else np.nan

cgap = snap.groupby("function_name").apply(comp_gap).dropna().sort_values()
bar_colors5 = [RED if v < -10 else AMBER if v < 0 else GREEN for v in cgap]
ax5.barh(cgap.index, cgap.values, color=bar_colors5, edgecolor="white", height=0.65)
ax5.axvline(0, color=DKGREY, linewidth=1)
for i,v in enumerate(cgap.values):
    xpos = v - 1.5 if v < 0 else v + 0.5
    ha   = "right"  if v < 0 else "left"
    ax5.text(xpos, i, f"{v:+.0f}%", va="center", fontsize=8.5,
             fontweight="bold", color=DKGREY)
ax5.set_xlabel("Leaver Salary vs Active Median (%)", fontsize=9)
ax5.set_title("Design & People Leavers:\nJunior Roles Exiting, Not Senior",
              fontsize=11, fontweight="bold", color=RED, loc="left")
ax5.set_facecolor(LGREY); ax5.spines[["top","right"]].set_visible(False)
ax5.tick_params(axis="y", labelsize=9)

# ── 6. VOLUNTARY EXITS QUARTERLY TREND ────────────────────────────────────
ax6 = fig.add_subplot(gs[2, :])
vol_snap2 = snap[snap["is_vol_leaver"]].copy()
vol_snap2["exit_month"] = pd.to_datetime(
    vol_snap2["termination_month"].fillna(
        vol_snap2["report_effective_date"].astype(str).str[:7]), errors="coerce")
vol_snap2["exit_q"] = vol_snap2["exit_month"].dt.to_period("Q")
q_vol = vol_snap2.groupby("exit_q").size()

# Also split by function group
vol_snap2["fn_group"] = vol_snap2["function_name"].map({
    "Engineering":"Product & Eng", "Product":"Product & Eng","Design":"Product & Eng","Data":"Product & Eng",
    "Sales":"Go-to-Market","Customer Success":"Go-to-Market","Marketing":"Go-to-Market",
    "People":"Corporate","Finance":"Corporate","Legal":"Corporate","Operations":"Corporate",
})
q_fn = vol_snap2.groupby(["exit_q","fn_group"]).size().unstack(fill_value=0)

colors_fn = {"Product & Eng": NAVY, "Go-to-Market": RED, "Corporate": AMBER}
bottom = np.zeros(len(q_fn))
for fn in q_fn.columns:
    ax6.bar(range(len(q_fn)), q_fn[fn].values, bottom=bottom,
            color=colors_fn.get(fn, MGREY), edgecolor="white",
            width=0.7, label=fn, alpha=0.9)
    bottom += q_fn[fn].values

ax6.set_xticks(range(len(q_fn)))
ax6.set_xticklabels([str(q) for q in q_fn.index], rotation=45, ha="right", fontsize=9)
ax6.set_ylabel("Voluntary Exits", fontsize=9)
ax6.legend(fontsize=9, frameon=False, loc="upper left")
ax6.set_title("Voluntary Exit Volume: Stable Overall — No Acceleration  ·  Go-to-Market Consistently the Largest Source",
              fontsize=11, fontweight="bold", color=DKGREY, loc="left")
ax6.set_facecolor(LGREY); ax6.spines[["top","right"]].set_visible(False)
# Trend line
z = np.polyfit(range(len(q_vol)), q_vol.values, 1)
p = np.poly1d(z)
ax6.plot(range(len(q_vol)), p(range(len(q_vol))), color=MGREY,
         linestyle="--", linewidth=1.5, label="Trend")

fig.suptitle(
    "Meridian Technologies — Voluntary Turnover Deep Dive  |  Apr 2026\n"
    "Panel: 64,186 employee-months  ·  384 voluntary departures",
    fontsize=13, fontweight="bold", color=DKGREY, y=0.99)

plt.savefig("voluntary_deep_dive.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
print("Saved voluntary_deep_dive.png")
