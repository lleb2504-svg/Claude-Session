import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ── Palette ───────────────────────────────────────────────────────────────────
NAVY   = RGBColor(0x1B, 0x2A, 0x4A)
RED    = RGBColor(0xC0, 0x39, 0x2B)
AMBER  = RGBColor(0xE6, 0x7E, 0x22)
GREEN  = RGBColor(0x27, 0xAE, 0x60)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
LGREY  = RGBColor(0xF4, 0xF6, 0xF7)
MGREY  = RGBColor(0x7F, 0x8C, 0x8D)
DKGREY = RGBColor(0x2C, 0x3E, 0x50)
def rgb(r,g,b): return RGBColor(r,g,b)

# ── Data ──────────────────────────────────────────────────────────────────────
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

# ── Helpers ───────────────────────────────────────────────────────────────────
def fig_to_picture(slide, fig, left, top, width, height):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=180, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    slide.shapes.add_picture(buf, left, top, width, height)
    plt.close(fig)

def add_text(slide, text, left, top, width, height,
             size=14, bold=False, color=DKGREY, align=PP_ALIGN.LEFT):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    p  = tf.paragraphs[0]
    p.alignment = align
    r  = p.add_run()
    r.text = text
    r.font.size  = Pt(size)
    r.font.bold  = bold
    r.font.color.rgb = color

def add_rect(slide, left, top, width, height, fill, line=None):
    sh = slide.shapes.add_shape(1, left, top, width, height)
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if line: sh.line.color.rgb = line
    else:    sh.line.fill.background()
    return sh

def slide_chrome(sl, num, title, accent=RED):
    add_rect(sl, Inches(0), Inches(0), Inches(13.33), Inches(7.5), LGREY)
    add_rect(sl, Inches(0), Inches(0), Inches(13.33), Inches(1.1),  NAVY)
    add_rect(sl, Inches(0), Inches(1.1), Inches(13.33), Inches(0.06), accent)
    add_text(sl, f"{num}  |  {title}",
             Inches(0.4), Inches(0.25), Inches(12), Inches(0.6),
             size=22, bold=True, color=WHITE)

def insight_panel(slide, bullets, left, top, w, h, accent=RED, header="KEY IMPLICATIONS"):
    add_rect(slide, left, top, w, h, rgb(0xFF,0xF5,0xF5))
    add_text(slide, header, left+Inches(0.15), top+Inches(0.15),
             w-Inches(0.3), Inches(0.4), size=9, bold=True, color=accent)
    for i, b in enumerate(bullets):
        add_text(slide, f"› {b}", left+Inches(0.15), top+Inches(0.65)+i*Inches(1.05),
                 w-Inches(0.3), Inches(0.95), size=9.5, color=DKGREY)

# ── Load existing deck ────────────────────────────────────────────────────────
prs = Presentation("meridian_board_deck.pptx")
blank = prs.slide_layouts[6]

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 6 — PROMOTION GAP: KEY DRIVER OF VOLUNTARY EXIT
# ════════════════════════════════════════════════════════════════════════════
sl6 = prs.slides.add_slide(blank)
slide_chrome(sl6, "06", "DEEP DIVE:  PROMOTION IS THE MISSING LEVER")

# Stat boxes
add_rect(sl6, Inches(0.35), Inches(1.35), Inches(2.9), Inches(1.7), WHITE)
add_text(sl6, "3.5×", Inches(0.5), Inches(1.42), Inches(2.6), Inches(0.85),
         size=52, bold=True, color=RED)
add_text(sl6, "higher promotion rate\nfor active vs. leavers\n(2–4 yr tenure band)",
         Inches(0.5), Inches(2.2), Inches(2.6), Inches(0.75), size=10, color=DKGREY)

add_rect(sl6, Inches(0.35), Inches(3.2), Inches(2.9), Inches(1.5), WHITE)
add_text(sl6, "7.3%", Inches(0.5), Inches(3.27), Inches(2.6), Inches(0.75),
         size=42, bold=True, color=RED)
add_text(sl6, "of voluntary leavers\never promoted\n(vs 20% of active staff)",
         Inches(0.5), Inches(3.95), Inches(2.6), Inches(0.7), size=10, color=DKGREY)

add_rect(sl6, Inches(0.35), Inches(4.85), Inches(2.9), Inches(1.4), WHITE)
add_text(sl6, "All tenures", Inches(0.5), Inches(4.92), Inches(2.6), Inches(0.5),
         size=16, bold=True, color=AMBER)
add_text(sl6, "Promotion gap holds\nat every tenure band\n— it's systemic, not\na new-hire problem",
         Inches(0.5), Inches(5.4), Inches(2.6), Inches(0.75), size=10, color=DKGREY)

# Chart: promotion rate by tenure band
bands = ["1-2yr","2-4yr","4-7yr","7yr+"]
lv_p  = [vol_snap[vol_snap["tenure_band"]==b]["last_promotion_month"].notna().mean()*100 for b in bands]
ac_p  = [snap[snap["is_active"]&(snap["tenure_band"]==b)]["last_promotion_month"].notna().mean()*100 for b in bands]

fig6, ax = plt.subplots(figsize=(5.8, 4.2), facecolor="white")
x = np.arange(len(bands)); w = 0.35
ax.bar(x-w/2, lv_p, width=w, color="#C0392B", alpha=0.85,
       edgecolor="white", label="Voluntary leavers")
ax.bar(x+w/2, ac_p, width=w, color="#27AE60", alpha=0.85,
       edgecolor="white", label="Active today")
for i,(lv,ac) in enumerate(zip(lv_p,ac_p)):
    ax.text(i-w/2, lv+0.4, f"{lv:.0f}%", ha="center", fontsize=11,
            fontweight="bold", color="#C0392B")
    ax.text(i+w/2, ac+0.4, f"{ac:.0f}%", ha="center", fontsize=11,
            fontweight="bold", color="#27AE60")
    # gap arrow annotation
    ax.annotate("", xy=(i+w/2, ac), xytext=(i-w/2, lv),
                arrowprops=dict(arrowstyle="<->", color="#7F8C8D", lw=1.2))
ax.set_xticks(x); ax.set_xticklabels(bands, fontsize=10)
ax.set_ylabel("% Ever Promoted During Panel", fontsize=10)
ax.set_ylim(0, 35)
ax.legend(fontsize=10, frameon=False)
ax.set_title("Promotion Rate: Voluntary Leavers vs. Active Employees",
             fontsize=11, fontweight="bold", color="#1B2A4A", loc="left", pad=8)
ax.spines[["top","right"]].set_visible(False)
ax.set_facecolor("white")
fig6.tight_layout(pad=0.6)
fig_to_picture(sl6, fig6, Inches(3.55), Inches(1.35), Inches(6.0), Inches(4.6))

insight_panel(sl6, [
    "Career stagnation — not pay — is the primary voluntary exit trigger",
    "Fixing promo velocity in Product & CS would directly cut 24–26% attrition",
    "Proposed action: bi-annual promo windows with manager accountability metrics",
], Inches(9.8), Inches(1.35), Inches(3.2), Inches(4.6))

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 7 — SEPTEMBER SPIKE + ENGAGEMENT TRAJECTORY
# ════════════════════════════════════════════════════════════════════════════
sl7 = prs.slides.add_slide(blank)
slide_chrome(sl7, "07", "DEEP DIVE:  WHEN AND HOW PEOPLE DISENGAGE")

# Sep spike chart
vol_snap["exit_month_num"] = pd.to_datetime(
    vol_snap["termination_month"].fillna(
        vol_snap["report_effective_date"].astype(str).str[:7]),
    errors="coerce").dt.month
monthly = vol_snap.groupby("exit_month_num").size()
month_labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

fig7a, ax1 = plt.subplots(figsize=(5.5, 3.8), facecolor="white")
bar_cols = ["#C0392B" if v==monthly.max() else
            "#E67E22" if v>=monthly.quantile(0.75) else "#AEB6BF"
            for v in monthly.values]
ax1.bar(month_labels, monthly.values, color=bar_cols, edgecolor="white", width=0.7)
ax1.axhline(monthly.mean(), color="#7F8C8D", linestyle="--", linewidth=1.5,
            label=f"Monthly avg ({monthly.mean():.0f})")
for i,(m,v) in enumerate(zip(month_labels, monthly.values)):
    if v >= monthly.quantile(0.75):
        ax1.text(i, v+0.5, str(v), ha="center", fontsize=9.5,
                 fontweight="bold", color="#2C3E50")
ax1.set_ylabel("Voluntary Exits", fontsize=10)
ax1.legend(fontsize=9, frameon=False)
ax1.set_title("Exits by Month of Year", fontsize=11,
              fontweight="bold", color="#1B2A4A", loc="left", pad=8)
ax1.spines[["top","right"]].set_visible(False); ax1.set_facecolor("white")
ax1.annotate("Post mid-year review\n(Eng = 38% of Sep exits)",
             xy=(8, 45), xytext=(9.2, 42), fontsize=8.5, color="#C0392B",
             arrowprops=dict(arrowstyle="->", color="#C0392B", lw=1.2))
fig7a.tight_layout(pad=0.6)
fig_to_picture(sl7, fig7a, Inches(0.35), Inches(1.35), Inches(5.8), Inches(4.2))

# Engagement trajectory chart
vol_ids   = set(vol_snap["worker_id"])
vol_panel = panel[panel["worker_id"].isin(vol_ids)].copy()
vol_panel = vol_panel.sort_values(["worker_id","report_effective_date"])

def months_before_exit(grp):
    last = grp["report_effective_date"].max()
    grp  = grp.copy()
    grp["mte"] = ((last - grp["report_effective_date"]) /
                  pd.Timedelta(days=30.44)).round().astype(int)
    return grp

vt      = vol_panel.groupby("worker_id", group_keys=False).apply(months_before_exit)
eng_traj = vt[vt["mte"]<=11].groupby("mte")["engagement_score"].mean().sort_index(ascending=False)
act_eng  = panel[panel["report_effective_date"]==panel_end]["engagement_score"].mean()

fig7b, ax2 = plt.subplots(figsize=(5.5, 3.8), facecolor="white")
ax2.plot(range(12), eng_traj.values, color="#C0392B", linewidth=2.5,
         marker="o", markersize=6, label="Pre-exit trajectory (leavers)")
ax2.axhline(act_eng, color="#27AE60", linestyle="--", linewidth=2,
            label=f"Active employee avg ({act_eng:.2f})")
ax2.fill_between(range(12), eng_traj.values, act_eng,
                 alpha=0.12, color="#C0392B")
ax2.set_xticks(range(12))
ax2.set_xticklabels([f"{v}m" for v in eng_traj.index], fontsize=9)
ax2.set_xlabel("Months before departure (0 = exit month)", fontsize=9)
ax2.set_ylabel("Avg Engagement Score", fontsize=10)
ax2.set_ylim(6.0, 7.6)
ax2.legend(fontsize=9, frameon=False)
ax2.set_title("Engagement Trajectory Before Exit", fontsize=11,
              fontweight="bold", color="#1B2A4A", loc="left", pad=8)
ax2.spines[["top","right"]].set_visible(False); ax2.set_facecolor("white")
ax2.annotate("Gap is flat for 12 months:\ndecision made long before notice",
             xy=(6, eng_traj.values[5]), xytext=(7.5, 6.55),
             fontsize=8.5, color="#C0392B",
             arrowprops=dict(arrowstyle="->", color="#C0392B", lw=1.2))
fig7b.tight_layout(pad=0.6)
fig_to_picture(sl7, fig7b, Inches(6.55), Inches(1.35), Inches(5.8), Inches(4.2))

# Stat callouts
add_rect(sl7, Inches(0.35), Inches(5.75), Inches(5.8), Inches(1.4),
         rgb(0xFF,0xF5,0xF5))
add_text(sl7, "› September has 45 exits — 40% above monthly average.  "
         "Engineering alone accounts for 38%.  Timing is consistent with mid-year "
         "review outcomes triggering resignation decisions.",
         Inches(0.5), Inches(5.82), Inches(5.5), Inches(1.25),
         size=9.5, color=DKGREY)

add_rect(sl7, Inches(6.55), Inches(5.75), Inches(5.8), Inches(1.4),
         rgb(0xFF,0xF5,0xF5))
add_text(sl7, "› Leavers sit 0.35 points below active employees for the "
         "entire year before they exit.  Exit interviews are too late — "
         "pulse scores at 12 months out are the real early-warning signal.",
         Inches(6.7), Inches(5.82), Inches(5.5), Inches(1.25),
         size=9.5, color=DKGREY)

# ════════════════════════════════════════════════════════════════════════════
# SLIDE 8 — MANAGER DECAY + APPENDIX SUMMARY TABLE
# ════════════════════════════════════════════════════════════════════════════
sl8 = prs.slides.add_slide(blank)
slide_chrome(sl8, "08", "DEEP DIVE:  MANAGER WATCH-LIST — 3-YEAR ENGAGEMENT TREND",
             accent=AMBER)

# Manager trend chart
overall_trend = panel.groupby("report_effective_date")["engagement_score"].mean()

fig8, ax = plt.subplots(figsize=(8.5, 4.4), facecolor="white")
ax.plot(overall_trend.index, overall_trend.values, color="#27AE60",
        linewidth=2, linestyle="--", alpha=0.8, label="Company average")

styles = [
    ("060f8cec1aecbd2c", "Mgr 060f  (Eng, 25-person team) — PRIORITY", "#C0392B", "-",  "o"),
    ("20c21d2b66105bd4", "Mgr 20c2  (Eng, 22-person team) — PRIORITY", "#E67E22", "-",  "s"),
    ("fbad34d858b1ec42", "Mgr fbad  (Ops Remote-US, 8-person) — WATCH", "#7F8C8D", "--", "^"),
    ("db3ccea897084810", "Mgr db3c  (Ops Remote-US, 8-person) — WATCH", "#AEB6BF", "--", "v"),
]
for mid, label, col, ls, mk in styles:
    mgr_p = panel[panel["manager_id"]==mid].groupby(
        "report_effective_date")["engagement_score"].mean()
    ax.plot(mgr_p.index, mgr_p.values, color=col, linewidth=2,
            linestyle=ls, label=label, marker=mk, markersize=3.5,
            markevery=4)

# Shade recovery window for 20c2
ax.axvspan(pd.Timestamp("2024-06-01"), pd.Timestamp("2025-05-01"),
           alpha=0.07, color="#E67E22", label="_nolegend_")
ax.text(pd.Timestamp("2024-10-01"), 6.05, "Brief recovery\n(20c2 only)",
        fontsize=8, color="#E67E22", ha="center")

ax.set_ylim(4.8, 7.8)
ax.set_ylabel("Team Avg Engagement Score", fontsize=10)
ax.legend(fontsize=8.5, frameon=False, loc="upper left", ncol=2)
ax.set_title("Team Engagement Over Time — Flagged vs. Company Average",
             fontsize=11, fontweight="bold", color="#1B2A4A", loc="left", pad=8)
ax.spines[["top","right"]].set_visible(False)
ax.set_facecolor("white")
ax.tick_params(axis="x", labelsize=9)
fig8.tight_layout(pad=0.6)
fig_to_picture(sl8, fig8, Inches(0.35), Inches(1.35), Inches(8.8), Inches(4.8))

# Summary table on the right
rows = [
    ("060f8cec", "Eng / SF",       "25", "56%", "5.3 ↓", "3 yrs declining", "PRIORITY"),
    ("20c21d2b", "Eng / SF",       "22", "55%", "5.4 ↓", "Recovery reversed","PRIORITY"),
    ("fbad34d8", "Ops / Remote",   " 8", "50%", "6.9",   "Low eng, decent mgr","WATCH"),
    ("db3ccea8", "Ops / Remote",   " 8", "38%", "6.8",   "Early exits (3mo)","WATCH"),
    ("bc48283a", "Ops / Remote",   " 8", "38%", "6.9",   "Early exits (3mo)","WATCH"),
]
headers = ["Manager", "Fn / Loc", "Team", "Attr%", "Eng", "Signal", "Status"]
col_w   = [Inches(1.0), Inches(1.1), Inches(0.6), Inches(0.65),
           Inches(0.65), Inches(1.55), Inches(0.85)]
left0   = Inches(9.4)
top0    = Inches(1.5)
row_h   = Inches(0.42)

# Header row
add_rect(sl8, left0, top0, sum(col_w), row_h, NAVY)
x = left0
for h, cw in zip(headers, col_w):
    add_text(sl8, h, x+Inches(0.04), top0+Inches(0.06), cw, row_h,
             size=8, bold=True, color=WHITE)
    x += cw

status_colors = {"PRIORITY": RED, "WATCH": AMBER}
for ri, row in enumerate(rows):
    rcolor = rgb(0xFF,0xF0,0xF0) if row[-1]=="PRIORITY" else rgb(0xFF,0xF9,0xF0)
    add_rect(sl8, left0, top0+(ri+1)*row_h, sum(col_w), row_h, rcolor)
    x = left0
    for ci, (val, cw) in enumerate(zip(row, col_w)):
        tc = status_colors.get(val, DKGREY) if ci == len(row)-1 else DKGREY
        bld = ci == len(row)-1
        add_text(sl8, val, x+Inches(0.04), top0+(ri+1)*row_h+Inches(0.06),
                 cw, row_h, size=8, bold=bld, color=tc)
        x += cw

add_text(sl8, "Action: structured skip-level conversations for both PRIORITY "
         "managers within 30 days. Use existing manager-effectiveness scores "
         "as the evidence base — the data is already there.",
         Inches(9.4), Inches(5.9), Inches(3.7), Inches(0.9),
         size=9, color=DKGREY)

# ── Save ──────────────────────────────────────────────────────────────────────
prs.save("meridian_board_deck.pptx")
print(f"Saved — deck now has {len(prs.slides)} slides")
