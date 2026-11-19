# Figures added after the fourth reading, drawn at their printed size (all values from the book's examples)
import sys, numpy as np
sys.path.insert(0, "..")
from bookstyle import *
from matplotlib.patches import Polygon, FancyBboxPatch
F = "../../figures/"
def iso(s): return "⁦" + s + "⁩"

# ---------------------------------------------------------------- 17.2 the engineering assistant pipeline (Arabic)
fig, ax = canvas(5.8, 4.25)
W_, H_ = 1.55, 1.18
xs = [5.8 - 0.25 - W_, 5.8 - 0.25 - 2 * W_ - 0.42, 0.08]          # right, middle, left
y1, y2 = 2.95, 1.38
card(ax, xs[0], y1, W_, H_, "سؤال المهندس", "بلغته وبمصطلحات\nالموقع", NAVY, fs=11, bfs=9.4, num=1)
card(ax, xs[1], y1, W_, H_, "التطبيع", "الهمزات والتاء\nالمربوطة والتشكيل", BLUE, fs=11, bfs=9.4, num=2)
card(ax, xs[2], y1, W_, H_, "الاسترجاع", "أفضل ثلاثة مقاطع\nبأرقام البنود", BLUE, fs=11, bfs=9.4, num=3)
card(ax, xs[2], y2, W_, H_, "المسودة", "النموذج اللغوي\nيكتب الجواب", ORANGE, fs=11, bfs=9.4, num=4)
card(ax, xs[0], y2, W_, H_, "المراجعة", "المهندس يراجع\nويوقّع", GREEN, fs=11, bfs=9.4, num=6)
cx, cy = xs[1] + W_ / 2, y2 + H_ / 2
ax.add_patch(Polygon([(cx, cy + 0.62), (cx + 0.86, cy), (cx, cy - 0.62), (cx - 0.86, cy)], fc=TINT[RED], ec=RED, lw=1.6))
ax.text(cx, cy + 0.12, "حارس الأرقام", ha="center", va="center", fontsize=10.5, color=RED, fontweight="bold")
ax.text(cx, cy - 0.17, "كل رقم في المصدر؟", ha="center", va="center", fontsize=9.4, color="#2D3748")
ax.add_patch(plt.Circle((cx + 0.62, cy + 0.5), 0.17, fc=RED, ec="white", lw=1.4, zorder=5)); ax.text(cx + 0.62, cy + 0.5, "5", ha="center", va="center", color="white", fontsize=10, fontweight="bold", zorder=6)
ax.add_patch(FancyBboxPatch((cx - 1.0, 0.05), 2.0, 0.66, boxstyle="round,pad=0,rounding_size=0.1", fc=TINT[RED], ec=RED, lw=1.2))
ax.text(cx, 0.38, "يُرفض الجواب\nويُحال السؤال إلى المهندس", ha="center", va="center", fontsize=9.4, color=RED, linespacing=1.1)
arrow(ax, (xs[0] - 0.02, y1 + H_ / 2), (xs[1] + W_ + 0.02, y1 + H_ / 2), col=GREY, lw=1.6, head=12)
arrow(ax, (xs[1] - 0.02, y1 + H_ / 2), (xs[2] + W_ + 0.02, y1 + H_ / 2), col=GREY, lw=1.6, head=12)
arrow(ax, (xs[2] + W_ / 2, y1 - 0.02), (xs[2] + W_ / 2, y2 + H_ + 0.04), col=GREY, lw=1.6, head=12)
arrow(ax, (xs[2] + W_ + 0.02, cy), (cx - 0.88, cy), col=GREY, lw=1.6, head=12)
arrow(ax, (cx + 0.88, cy), (xs[0] - 0.02, cy), col=GREEN, lw=1.8, head=12); ax.text((cx + 0.86 + xs[0]) / 2, cy + 0.08, "نعم", ha="center", va="bottom", fontsize=10, color=GREEN, fontweight="bold")
arrow(ax, (cx, cy - 0.64), (cx, 0.73), col=RED, lw=1.8, head=12); ax.text(cx + 0.1, (cy - 0.62 + 0.73) / 2, "لا", ha="left", va="center", fontsize=10, color=RED, fontweight="bold")
save(fig, F + "nfig_pipeline17.png")

# ---------------------------------------------------------------- 11.2b earned value at the end of month 6 (Example 11.2b)
PV, EV, AC, BAC = 500_000, 420_000, 480_000, 1_000_000
CPI, SPI = EV / AC, EV / PV
EAC1 = BAC / CPI; EAC2 = AC + (BAC - EV) / (CPI * SPI)
fig, axs = plt.subplots(1, 2, figsize=(5.6, 2.7), gridspec_kw=dict(width_ratios=[1.15, 1], wspace=0.35))
a = axs[1]                                      # right panel first (reading order): month 6
vals = [("المخطط PV", PV, "#A0AEC0"), ("المكتسب EV", EV, BLUE), ("الفعلي AC", AC, ORANGE)]
for i, (lab, v, c) in enumerate(vals):
    a.bar(i, v / 1e3, color=c, width=0.62); a.text(i, v / 2e3, f"{v/1e3:.0f}", ha="center", va="center", fontsize=8.8, fontfamily="DejaVu Sans", color="white", fontweight="bold")
a.set_xticks(range(3)); a.set_xticklabels([v[0] for v in vals], fontsize=8.8); a.set_ylim(0, 640); a.set_ylabel("ألف دينار", fontsize=9); a.tick_params(axis="y", labelsize=8.4)
a.annotate("", xy=(2, EV / 1e3), xytext=(2, AC / 1e3), arrowprops=dict(arrowstyle="<->", color="#1A202C", lw=1.3, mutation_scale=8, shrinkA=0, shrinkB=0))   # dark on the orange bar, as SV on the grey one
a.text(2, 530, iso("CV = −60"), fontsize=8.6, color=RED, fontfamily="DejaVu Sans", ha="center")
a.annotate("", xy=(0, EV / 1e3), xytext=(0, PV / 1e3), arrowprops=dict(arrowstyle="<->", color=NAVY, lw=1.3, mutation_scale=8, shrinkA=0, shrinkB=0))
a.hlines(EV / 1e3, -0.31, 2.31, color=BLUE, lw=0.8, ls=":")
a.text(0.22, 545, iso("SV = −80"), fontsize=8.6, color=NAVY, fontfamily="DejaVu Sans", ha="center")
a.set_title("نهاية الشهر السادس", fontsize=10)
b = axs[0]
vals2 = [("الميزانية BAC", BAC, "#A0AEC0"), ("الأداء نفسه", EAC1, BLUE), ("الصيغة المتشائمة", EAC2, RED)]
for i, (lab, v, c) in enumerate(vals2):
    b.bar(i, v / 1e6, color=c, width=0.62); b.text(i, v / 1e6 + 0.02, f"{v/1e6:.2f}", ha="center", va="bottom", fontsize=8.8, fontfamily="DejaVu Sans")
b.axhline(1.0, color=GREY, ls="--", lw=0.9); b.set_ylim(0, 1.5); b.set_xticks(range(3)); b.set_xticklabels([v[0] for v in vals2], fontsize=8.8)
b.set_ylabel("مليون دينار", fontsize=9); b.tick_params(axis="y", labelsize=8.4); b.set_title("الكلفة المتوقعة عند الإنجاز EAC", fontsize=10)
save(fig, F + "nfig_ev.png")
print("EV check: CPI %.3f SPI %.2f EAC1 %.0f EAC2 %.0f" % (CPI, SPI, EAC1, EAC2))

# ---------------------------------------------------------------- 14.x Webster's optimal cycle against the critical flow ratio
L = 8.0
Y = np.linspace(0.3, 0.95, 300); C0 = (1.5 * L + 5) / (1 - Y)
fig, ax = plt.subplots(figsize=(4.2, 2.9))
ax.plot(Y, C0, color=NAVY, lw=1.8)
ax.axvspan(0.9, 0.95, color=TINT[RED]); ax.text(0.925, 150, "المعادلة\nتفقد\nمعناها", ha="center", va="top", fontsize=8.6, color=RED, linespacing=1.05)
for y_, lab in ((0.556, "المثال 14.2"), (0.778, "التمرين")):
    c = (1.5 * L + 5) / (1 - y_); ax.plot(y_, c, "o", color=ORANGE, ms=6, zorder=5)
    ax.text(y_ - 0.015, c + 12, f"{lab}: {c:.0f} ثانية", ha="right", va="bottom", fontsize=8.8, color=ORANGE)
ax.set_xlim(0.3, 0.95); ax.set_ylim(0, 320)
ax.set_xlabel("نسبة الطلب الحرج Y", fontsize=9.5); ax.set_ylabel(iso("C₀ (s)") + " زمن الدورة", fontsize=9.5); ax.tick_params(labelsize=8.6)
fig.tight_layout(); save(fig, F + "nfig_webster.png")
print("webster:", [(y_, round((1.5 * L + 5) / (1 - y_), 1)) for y_ in (0.556, 0.778)])
