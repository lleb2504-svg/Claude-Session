import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

df = pd.read_csv("toy_hr_data.csv")

bins = [0, 2, 5, 8, 20]
labels = ["0–2 yrs", "2–5 yrs", "5–8 yrs", "8+ yrs"]
df["tenure_band"] = pd.cut(df["tenure_years"], bins=bins, labels=labels)

fig = plt.figure(figsize=(16, 10))
fig.patch.set_facecolor("#f7f8fa")
gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

RISK_RED   = "#c0392b"
BRIGHT_GRN = "#27ae60"
WARN_ORG   = "#e67e22"
NEUTRAL    = "#2c3e50"
BAR_BASE   = "#aab7c4"

# ── FINDING 1: Satisfaction by tenure band ──────────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
tenure_sat = df.groupby("tenure_band", observed=True)["satisfaction_score"].mean()
colors = [BRIGHT_GRN if v >= 7 else WARN_ORG if v >= 5 else RISK_RED for v in tenure_sat]
bars = ax1.bar(tenure_sat.index, tenure_sat.values, color=colors, edgecolor="white", width=0.55)
for bar, val in zip(bars, tenure_sat.values):
    ax1.text(bar.get_x() + bar.get_width()/2, val + 0.05, f"{val:.1f}",
             ha="center", va="bottom", fontsize=11, fontweight="bold", color=NEUTRAL)
ax1.set_ylim(0, 10)
ax1.set_ylabel("Avg Satisfaction Score", fontsize=10)
ax1.set_xlabel("Tenure Band", fontsize=10)
ax1.set_title("RISK #1\nSatisfaction Collapses with Tenure",
              fontsize=12, fontweight="bold", color=RISK_RED, loc="left")
ax1.axhline(df["satisfaction_score"].mean(), color=NEUTRAL, linestyle="--",
            linewidth=1, alpha=0.5, label=f"Company avg ({df['satisfaction_score'].mean():.1f})")
ax1.legend(fontsize=9)
ax1.set_facecolor("#f7f8fa")
ax1.spines[["top","right"]].set_visible(False)

# ── FINDING 2: High performers are disengaged ───────────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
perf_sat = df.groupby("performance_rating")["satisfaction_score"].mean()
bar_colors = [BRIGHT_GRN if r <= 3 else WARN_ORG if r == 4 else RISK_RED for r in perf_sat.index]
bars2 = ax2.bar([str(r) for r in perf_sat.index], perf_sat.values,
                color=bar_colors, edgecolor="white", width=0.55)
for bar, val in zip(bars2, perf_sat.values):
    ax2.text(bar.get_x() + bar.get_width()/2, val + 0.05, f"{val:.1f}",
             ha="center", va="bottom", fontsize=11, fontweight="bold", color=NEUTRAL)
ax2.set_ylim(0, 10)
ax2.set_xlabel("Performance Rating (1–5)", fontsize=10)
ax2.set_ylabel("Avg Satisfaction Score", fontsize=10)
ax2.set_title("RISK #2\nTop Performers Are the Least Satisfied",
              fontsize=12, fontweight="bold", color=RISK_RED, loc="left")
ax2.axhline(df["satisfaction_score"].mean(), color=NEUTRAL, linestyle="--",
            linewidth=1, alpha=0.5, label=f"Company avg ({df['satisfaction_score'].mean():.1f})")
ax2.legend(fontsize=9)
ax2.set_facecolor("#f7f8fa")
ax2.spines[["top","right"]].set_visible(False)

# ── FINDING 3: Salary spread by department ──────────────────────────────────
ax3 = fig.add_subplot(gs[1, :])
dept_order = ["Engineering", "Finance", "Marketing", "Sales", "HR"]
dept_colors = {
    "Engineering": WARN_ORG,
    "Finance":     NEUTRAL,
    "Marketing":   NEUTRAL,
    "Sales":       NEUTRAL,
    "HR":          RISK_RED,
}
y_positions = range(len(dept_order))
for i, dept in enumerate(dept_order):
    sub = df[df["department"] == dept]["salary"]
    ax3.scatter(sub.values, [i] * len(sub), alpha=0.55, s=60,
                color=dept_colors[dept], zorder=3)
    ax3.plot([sub.min(), sub.max()], [i, i], color=dept_colors[dept],
             linewidth=2, alpha=0.4, zorder=2)
    ax3.scatter([sub.mean()], [i], marker="D", s=80,
                color=dept_colors[dept], zorder=4, label="_nolegend_")
    ax3.text(sub.mean(), i + 0.22, f"avg ${sub.mean()/1000:.0f}k",
             ha="center", va="bottom", fontsize=9, color=dept_colors[dept], fontweight="bold")

ax3.set_yticks(list(y_positions))
ax3.set_yticklabels(dept_order, fontsize=11)
ax3.set_xlabel("Annual Salary ($)", fontsize=10)
ax3.set_title("BRIGHT SPOT #1 (& Hidden Risk)\nEngineering Pays to Win — HR Pays to Lose",
              fontsize=12, fontweight="bold", color=BRIGHT_GRN, loc="left")
ax3.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
ax3.set_facecolor("#f7f8fa")
ax3.spines[["top","right"]].set_visible(False)
ax3.annotate("Engineering avg: $134k\n(wide spread — risk of internal\ninequity at senior levels)",
             xy=(133500, 0), xytext=(170000, 0.7),
             fontsize=8.5, color=WARN_ORG,
             arrowprops=dict(arrowstyle="->", color=WARN_ORG, lw=1.2))
ax3.annotate("HR avg: $71k\n(lowest paid team;\nlikely to churn)",
             xy=(70900, 4), xytext=(120000, 3.55),
             fontsize=8.5, color=RISK_RED,
             arrowprops=dict(arrowstyle="->", color=RISK_RED, lw=1.2))

fig.suptitle("Meridian Technologies — People Risk & Bright Spots\nCPO Board Briefing · 90-Day View",
             fontsize=15, fontweight="bold", color=NEUTRAL, y=0.98)

plt.savefig("board_findings.png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
print("Saved board_findings.png")
