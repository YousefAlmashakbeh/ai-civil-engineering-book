# New explanatory figures added after the committee's first reading (all values computed here or taken from the book's tables)
import sys, numpy as np
sys.path.insert(0, "..")
from bookstyle import *
from matplotlib.patches import Polygon, Rectangle, FancyBboxPatch
F = "../../figures/"
plt.rcParams.update({"font.size": 10})
PART = {"1": NAVY, "2": BLUE, "3": ORANGE, "4": GREEN, "5": GOLD}
def iso(s): return "⁦" + s + "⁩"

# ---------------------------------------------------------------- 1. timeline (Table 1.3)
fig, ax = plt.subplots(figsize=(6.8, 3.3)); ax.set_xlim(1949, 2028); ax.set_ylim(-3.1, 3.3); ax.axis("off")
ax.hlines(0, 1950, 2026, color=GREY, lw=2)
for y in range(1950, 2030, 10):
    ax.plot([y, y], [-0.12, 0.12], color=GREY, lw=1.2); ax.text(y, -0.32, str(y), ha="center", va="top", fontsize=8.5, color="#4A5568", fontfamily="DejaVu Sans", zorder=6, bbox=dict(boxstyle="square,pad=0.05", fc="white", ec="none"))
ax.add_patch(Rectangle((1980, -0.09), 9.6, 0.18, fc=BLUE, alpha=0.35, ec="none"))
civ = [(1960, 1.2, "Clough:\n«العناصر المحدودة»"), (1981, 2.45, "الأنظمة الخبيرة\n(HI-RISE)"), (1989, 1.15, "Adeli: شبكات\nعصبية للتصميم"),
       (1998, 2.45, "Yeh: مقاومة\nالخرسانة"), (2017, 1.25, "Cha: كشف\nالشقوق بشبكة\nالتفافية")]
gen = [(1956, -1.25, "دارتموث:\nولادة المصطلح"), (2012, -1.3, "AlexNet:\nالتعلّم العميق"), (2019, -2.45, "PINN:\nالفيزياء في التعلّم"), (2022, -1.25, "النماذج\nاللغوية")]
for x, y, t in civ:
    ax.plot([x, x], [0, y - 0.15 * np.sign(y)], color=BLUE, lw=1.2); ax.plot(x, 0, "o", color=BLUE, ms=6, zorder=4)
    ax.text(x, y, t, ha="center", va="bottom", fontsize=9.3, color=NAVY, linespacing=1.0)
for x, y, t in gen:
    ax.plot([x, x], [0, y + 0.15], color=ORANGE, lw=1.2, ls="--"); ax.plot(x, 0, "D", color=ORANGE, ms=5.5, zorder=4)
    ax.text(x, y, t, ha="center", va="top", fontsize=9.3, color="#7B341E", linespacing=1.0)
ax.text(1951, 3.05, "● محطات في الهندسة المدنية", color=BLUE, fontsize=9.5, ha="left")
ax.text(1951, -2.75, "◆ محطات في الذكاء الاصطناعي عامة", color=ORANGE, fontsize=9.5, ha="left")
ax.annotate("", xy=(1979.5, 0.55), xytext=(1962, 0.55), arrowprops=dict(arrowstyle="<->", color=GREY, lw=0.8))
ax.text(1970.7, 0.62, "عقدان هادئان", ha="center", va="bottom", fontsize=8.5, color=GREY)
save(fig, F + "nfig_timeline.png")

# ---------------------------------------------------------------- 2. life cycle (Table 1.5)
stages = [("التخطيط", "الطلب على النقل والمياه\nواختيار المواقع", ["14", "15"], NAVY),
          ("التصميم", "النماذج البديلة والتصميم\nالأمثل وتصميم الخلطات", ["7", "8", "9", "10"], BLUE),
          ("التشييد", "تقدير الكلفة والمدة\nومراقبة السلامة والتقدّم", ["11"], ORANGE),
          ("التشغيل والصيانة", "الفحص الآلي ومراقبة\nالسلامة وتخطيط الصيانة", ["12", "13", "14"], GREEN),
          ("نهاية العمر", "العمر المتبقي وقرار\nالتدعيم أو الإحلال", ["13", "16"], GOLD)]
fig, ax = canvas(6.8, 3.0)
W = 6.8 / 5
def icon(ax, k, cx, cy, col):
    if k == 0:   # road plan
        ax.plot([cx - .35, cx - .05, cx + .1, cx + .35], [cy - .2, cy - .05, cy + .12, cy + .2], color=col, lw=2.2); ax.plot([cx - .3, cx + .3], [cy + .22, cy - .22], color=col, lw=1, ls=":")
    elif k == 1:  # beam with loads
        ax.add_patch(Rectangle((cx - .35, cy - .08), .7, .12, fc=col, ec=col)); ax.plot([cx - .3, cx + .3], [cy - .16, cy - .16], "^", color=col, ms=5)
        for x in (cx - .2, cx, cx + .2): arrow(ax, (x, cy + .28), (x, cy + .06), col=col, lw=1.2, head=7)
    elif k == 2:  # crane
        ax.plot([cx - .1, cx - .1], [cy - .25, cy + .25], color=col, lw=2); ax.plot([cx - .35, cx + .35], [cy + .25, cy + .25], color=col, lw=2)
        ax.plot([cx + .25, cx + .25], [cy + .25, cy + .02], color=col, lw=1); ax.add_patch(Rectangle((cx + .19, cy - .06), .12, .08, fc=col))
    elif k == 3:  # bridge with sensor
        ax.plot([cx - .38, cx + .38], [cy + .05, cy + .05], color=col, lw=2.4)
        for x in (cx - .13, cx + .13): ax.plot([x, x], [cy + .05, cy - .25], color=col, lw=2)
        ax.plot(cx, cy + .14, "o", color=RED, ms=5); ax.plot([cx, cx], [cy + .14, cy + .3], color=RED, lw=.8)
    else:        # strengthened column
        ax.add_patch(Rectangle((cx - .08, cy - .27), .16, .52, fc="none", ec=col, lw=2))
        for y in np.linspace(cy - .2, cy + .18, 4): ax.plot([cx - .14, cx + .14], [y, y], color=col, lw=1.3)
for i, (name, txt, chs, col) in enumerate(stages):
    x1 = 6.8 - i * W; x0 = x1 - W + 0.02; h = 0.55; y0 = 1.75
    pts = [(x1, y0 + h / 2), (x1 - 0.18, y0 + h), (x0, y0 + h), (x0 + (0.18 if i < 4 else 0), y0 + h / 2), (x0, y0), (x1 - 0.18, y0)] if i else \
          [(x1, y0), (x1, y0 + h), (x0, y0 + h), (x0 + 0.18, y0 + h / 2), (x0, y0)]
    ax.add_patch(Polygon(pts, closed=True, fc=col, ec="white", lw=1.5))
    cx = (x0 + x1) / 2 - 0.05
    ax.text(cx, y0 + h / 2, name.replace("التشغيل والصيانة", "التشغيل\nوالصيانة"), ha="center", va="center", color="white", fontsize=10 if "\n" not in name.replace("التشغيل والصيانة", "\n") else 9.2, fontweight="bold", linespacing=0.9)
    icon(ax, i, cx, 2.62, col)
    ax.text(cx, 1.55, txt, ha="center", va="top", fontsize=8.8, color="#2D3748", linespacing=1.05)
    n = len(chs); xs = cx + (np.arange(n) - (n - 1) / 2) * 0.3
    for x, c in zip(xs[::-1], chs):
        ax.add_patch(Circle((x, 0.42), 0.12, fc=TINT.get(col, "#fff"), ec=col, lw=1.3)); ax.text(x, 0.42, c, ha="center", va="center", fontsize=8.5, color=NAVY, fontfamily="DejaVu Sans")
ax.text(6.75, 0.08, "الأرقام في الدوائر أرقام الفصول", ha="right", fontsize=8.5, color=GREY)
save(fig, F + "nfig_lifecycle.png")

# ---------------------------------------------------------------- 3. patch leakage (sections 4.7, 6.5, 12)
from crackgen import concrete_bg, crack
rng = np.random.default_rng(5)
walls = []
for s in range(2):
    big = np.zeros((128, 128))
    for a in range(2):
        for b in range(2):
            bg = concrete_bg(rng); img, _ = crack(bg, rng) if (a + b + s) % 2 == 0 else (bg, None); big[a*64:(a+1)*64, b*64:(b+1)*64] = img
    walls.append(big)
fig, axs = plt.subplots(1, 4, figsize=(6.8, 2.75), gridspec_kw=dict(wspace=0.08))
rs = np.random.default_rng(2)
lab_rand = [rs.random((4, 4)) < 0.25 for _ in range(2)]
lab_img = [np.zeros((4, 4), bool), np.ones((4, 4), bool)]
panels = [(axs[3], walls[0], lab_rand[0]), (axs[2], walls[1], lab_rand[1]), (axs[1], walls[0], lab_img[0]), (axs[0], walls[1], lab_img[1])]
for ax_, im, lab in panels:
    ax_.imshow(im, cmap="gray", vmin=0.1, vmax=0.8); ax_.set_xticks([]); ax_.set_yticks([])
    for sp in ax_.spines.values(): sp.set_visible(False)
    for r in range(4):
        for c in range(4):
            test = lab[r, c]
            ax_.add_patch(Rectangle((c*32 + 1.5, r*32 + 1.5), 29, 29, fill=test, fc=(0.75, 0.34, 0.13, 0.35) if test else "none",
                                    ec=ORANGE if test else BLUE, lw=1.3, ls="--" if test else "-"))
axs[2].set_title("صورة ب", fontsize=10); axs[3].set_title("صورة أ", fontsize=10); axs[0].set_title("صورة ب", fontsize=10); axs[1].set_title("صورة أ", fontsize=10)
fig.text(0.735, 0.97, "تقسيم عشوائي للرقع", ha="center", fontsize=11.5, color=RED, fontweight="bold")
fig.text(0.29, 0.97, "تقسيم حسب الصورة الأصلية", ha="center", fontsize=11.5, color=GREEN, fontweight="bold")
fig.text(0.735, 0.03, "رقعة اختبار تجاورها رقعة تدريب من الشق نفسه:\nالنموذج يتذكّر الجدار، والخطأ المعلَن متفائل", ha="center", va="bottom", fontsize=9.3, color="#2D3748")
fig.text(0.29, 0.03, "صورة كاملة للتدريب وأخرى كاملة للاختبار:\nالخطأ المعلَن يقارب خطأ جدار جديد", ha="center", va="bottom", fontsize=9.3, color="#2D3748")
fig.add_artist(plt.Line2D([0.515, 0.515], [0.12, 0.93], color=GREY, lw=1, ls=":"))
from matplotlib.lines import Line2D
fig.legend(handles=[Rectangle((0, 0), 1, 1, fc="none", ec=BLUE, lw=1.4), Rectangle((0, 0), 1, 1, fc=(0.75, 0.34, 0.13, 0.35), ec=ORANGE, ls="--", lw=1.4)],
           labels=["رقعة تدريب", "رقعة اختبار"], loc="lower center", bbox_to_anchor=(0.5, -0.1), ncol=2, frameon=False, fontsize=9.5)
fig.subplots_adjust(top=0.82, bottom=0.25)
save(fig, F + "nfig_patchleak.png")

# ---------------------------------------------------------------- 4. one convolution filter, computed
from scipy.signal import correlate2d
rng = np.random.default_rng(11)
bg = concrete_bg(rng); img, m = crack(bg, rng)
ys, xs = np.where(m); cy, cx = int(np.median(ys)), int(np.median(xs))
r0 = int(np.clip(cy - 4, 0, 56)); c0 = int(np.clip(cx - 4, 0, 56))
P = np.round(img[r0:r0+8, c0:c0+8] * 100).astype(int)
K = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
O = correlate2d(P, K, mode="valid")
fig, axs = plt.subplots(1, 3, figsize=(6.8, 2.9), gridspec_kw=dict(width_ratios=[8, 3, 6], wspace=0.45))
axs[0].imshow(P, cmap="gray", vmin=P.min() - 10, vmax=P.max() + 10)
for i in range(8):
    for j in range(8): axs[0].text(j, i, str(P[i, j]), ha="center", va="center", fontsize=6.8, color="white" if P[i, j] < P.mean() else "black", fontfamily="DejaVu Sans")
axs[0].add_patch(Rectangle((-0.5, -0.5), 3, 3, fill=False, ec=RED, lw=2))
axs[1].imshow(K, cmap="RdBu_r", vmin=-2, vmax=2)
for i in range(3):
    for j in range(3): axs[1].text(j, i, str(K[i, j]), ha="center", va="center", fontsize=10, fontfamily="DejaVu Sans")
lim = np.abs(O).max(); axs[2].imshow(O, cmap="RdBu_r", vmin=-lim, vmax=lim)
for i in range(6):
    for j in range(6): axs[2].text(j, i, str(O[i, j]), ha="center", va="center", fontsize=7, fontfamily="DejaVu Sans")
axs[2].add_patch(Rectangle((-0.5, -0.5), 1, 1, fill=False, ec=RED, lw=2))
for a in axs: a.set_xticks([]); a.set_yticks([])
axs[0].set_title("رقعة 8×8 من صورة شق", fontsize=10); axs[1].set_title("المرشّح 3×3", fontsize=10); axs[2].set_title("خريطة الخصائص 6×6", fontsize=10)
fig.canvas.draw(); b0, b1, b2 = [a.get_position() for a in axs]
fig.text((b0.x1 + b1.x0) / 2, 0.55, "×", fontsize=18, ha="center", va="center", color=NAVY, fontfamily="DejaVu Sans"); fig.text((b1.x1 + b2.x0) / 2, 0.55, "=", fontsize=18, ha="center", va="center", color=NAVY, fontfamily="DejaVu Sans")
w = P[0:3, 0:3]; s = int((w * K).sum())
calc = f"({w[0,2]}+{w[1,2]}+{w[2,2]}) − ({w[0,0]}+{w[1,0]}+{w[2,0]}) = {s}"
fig.text(0.5, 0.02, iso(calc), ha="center", fontsize=9, color=RED, fontfamily="DejaVu Sans")
fig.text(0.5, 0.095, "الخلية الحمراء في الخريطة = مجموع حاصل ضرب المربع الأحمر في المرشّح:", ha="center", fontsize=9.5, color="#2D3748")
fig.subplots_adjust(bottom=0.22, top=0.86)
save(fig, F + "nfig_conv.png")
print("conv check: patch origin", r0, c0, "first output", O[0, 0], "=", s)

# ---------------------------------------------------------------- 5. concrete life on a log time axis (chapter 8)
fig, ax = plt.subplots(figsize=(6.8, 3.0))
D, Y = 1, 365.25
rows = [("8.5", "متى يُفكّ الشدّ؟", 1, 21, GOLD), ("8.2", "هل تصدق طريقة النضج في الحر؟", 1, 28, ORANGE),
        ("8.1", "28 يوماً من نتائج 3 و7 أيام", 3, 28, BLUE), ("8.3", "متى يبدأ التآكل؟", 1 * Y, 50 * Y, GREEN), ("8.4", "كم يبقى من التماسك؟", 10 * Y, 100 * Y, RED)]
for i, (ex, q, a, b, col) in enumerate(rows):
    y = len(rows) - 1 - i
    ax.barh(y, np.log10(b) - np.log10(a), left=np.log10(a), height=0.62, color=TINT[col], edgecolor=col, lw=1.4)
    ax.text(np.log10(a) + 0.06, y, f"مثال {ex}", ha="left", va="center", fontsize=9.5, color=col, fontweight="bold")
    xt = np.log10(b) + 0.08
    ax.text(xt, y, q, ha="left", va="center", fontsize=9.3, color="#2D3748")
ticks = [(1, "يوم"), (7, "أسبوع"), (28, "28 يوماً"), (Y, "سنة"), (10 * Y, "10 سنوات"), (100 * Y, "100 سنة")]
ax.set_xticks([np.log10(t) for t, _ in ticks]); ax.set_xticklabels([l for _, l in ticks], fontfamily="Amiri", fontsize=10)
for t, _ in ticks: ax.axvline(np.log10(t), color="#E2E8F0", lw=0.8, zorder=0)
ax.set_yticks([]); ax.spines[["left", "top", "right"]].set_visible(False); ax.set_xlim(-0.05, 5.4); ax.set_ylim(-0.6, len(rows) - 0.4)
ax.text(0.0, len(rows) - 0.25, "عمر الخرسانة على محور زمني لوغاريتمي", fontsize=10.5, color=NAVY, fontweight="bold", ha="left")
save(fig, F + "nfig_concretelife.png")

# ---------------------------------------------------------------- 6. activity network of Example 11.4 (same data and seed as the example)
acts = {"A": (8, 10, 16, []), "B": (12, 15, 24, ["A"]), "C": (40, 48, 70, ["B"]), "D": (18, 22, 34, ["C"]), "E": (20, 26, 45, ["C"]),
        "F": (14, 18, 28, ["D", "E"]), "G": (15, 20, 40, ["C"]), "H": (25, 30, 48, ["F"]), "I": (10, 14, 25, ["G"]), "J": (4, 5, 8, ["H", "I"])}
names = {"A": "حفريات", "B": "أساسات", "C": "الهيكل", "D": "طوب", "E": "تمديدات", "F": "قصارة", "G": "واجهات", "H": "تشطيبات", "I": "خارجية", "J": "تسليم"}
keys = list(acts); pred = {k: v[3] for k, v in acts.items()}
def cpm(d):
    ef = {}; es = {}
    for k in keys: es[k] = max([ef[p] for p in pred[k]], default=0); ef[k] = es[k] + d[k]
    crit = set(); cur = "J"
    while True:
        crit.add(cur)
        if not pred[cur]: break
        cur = max(pred[cur], key=lambda p: ef[p])
    return ef["J"], crit, es
rng = np.random.default_rng(11); n = 20000; ci = {k: 0 for k in keys}
Dd = {k: rng.triangular(v[0], v[1], v[2], n) for k, v in acts.items()}
for i in range(n):
    _, cr, _ = cpm({k: Dd[k][i] for k in keys})
    for k in cr: ci[k] += 1
det, cdet, es = cpm({k: v[1] for k, v in acts.items()})
print("network: CPM", det, "critical", sorted(cdet), "criticality", {k: round(100 * v / n) for k, v in ci.items()})
pos = {"A": (6.35, 2.0), "B": (5.4, 2.0), "C": (4.45, 2.0), "D": (3.45, 2.75), "E": (3.45, 2.0), "G": (3.45, 1.2), "F": (2.45, 2.4), "I": (2.45, 1.2), "H": (1.45, 2.4), "J": (0.55, 1.8)}
fig = plt.figure(figsize=(6.8, 4.6)); ax = fig.add_axes([0.0, 0.42, 0.92, 0.58]); ax.set_xlim(0.1, 6.9); ax.set_ylim(0.85, 3.2); ax.axis("off")
cmap = plt.get_cmap("OrRd"); bw, bh = 0.8, 0.5
for k in keys:
    x, y = pos[k]
    for p in pred[k]:
        px, py = pos[p]; c = p in cdet and k in cdet
        ax.annotate("", xy=(x + bw / 2, y), xytext=(px - bw / 2, py), arrowprops=dict(arrowstyle="-|>", color=NAVY if c else GREY, lw=2 if c else 1, mutation_scale=10))
for k in keys:
    x, y = pos[k]; c = 100 * ci[k] / n
    ax.add_patch(FancyBboxPatch((x - bw / 2, y - bh / 2), bw, bh, boxstyle="round,pad=0,rounding_size=0.06", fc=cmap(0.05 + 0.5 * c / 100),
                                ec=NAVY if k in cdet else GREY, lw=2.4 if k in cdet else 1))
    ax.text(x, y + 0.1, f"{k}  {names[k]}", ha="center", va="center", fontsize=8.6, color="black")
    ax.text(x, y - 0.12, iso(f"{acts[k][1]} d · {c:.0f}%"), ha="center", va="center", fontsize=7.2, color="#1A202C", fontfamily="DejaVu Sans")
from matplotlib.colors import LinearSegmentedColormap
cmap2 = LinearSegmentedColormap.from_list("c2", [cmap(0.05), cmap(0.55)]); sm = plt.cm.ScalarMappable(cmap=cmap2, norm=plt.Normalize(0, 100)); cax = fig.add_axes([0.93, 0.5, 0.015, 0.42])
cb = fig.colorbar(sm, cax=cax); cb.set_label("مؤشر الحرجية (%)", fontsize=9.5); cb.ax.tick_params(labelsize=8)
ax.text(6.85, 3.12, "الإطار السميك: المسار الحرج بالمدد الأرجح", ha="right", fontsize=9.3, color=NAVY)
ag = fig.add_axes([0.1, 0.08, 0.82, 0.3])
for i, k in enumerate(keys):
    y = len(keys) - 1 - i; lo, ml, hi = acts[k][:3]
    ag.barh(y, ml, left=es[k], height=0.6, color=NAVY if k in cdet else "#A0AEC0")
    ag.plot([es[k] + lo, es[k] + hi], [y, y], color=ORANGE, lw=1.1); ag.plot([es[k] + lo, es[k] + hi], [y, y], "|", color=ORANGE, ms=6)
ag.set_yticks(range(len(keys))); ag.set_yticklabels(keys[::-1], fontfamily="DejaVu Sans", fontsize=8)
ag.set_xlabel("اليوم (المدة الأرجح، والخط البرتقالي من المتفائلة إلى المتشائمة)", fontsize=9.5); ag.tick_params(axis="x", labelsize=8)
save(fig, F + "nfig_network.png")

# ---------------------------------------------------------------- 7. an instrumented bridge (chapter 13 examples)
fig = plt.figure(figsize=(6.8, 3.9)); ax = fig.add_axes([0, 0.32, 1, 0.45]); ax.set_xlim(0, 10); ax.set_ylim(-1.45, 0.75); ax.axis("off")
ax.add_patch(Rectangle((0.3, 0.0), 9.4, 0.32, fc="#CBD5E0", ec="#4A5568"))
for x in (3.4, 6.6):
    ax.add_patch(Polygon([(x - 0.25, -1.3), (x + 0.25, -1.3), (x + 0.15, 0.0), (x - 0.15, 0.0)], fc="#E2E8F0", ec="#4A5568"))
for x in (0.3, 9.7): ax.add_patch(Polygon([(x - 0.3, -0.5), (x + 0.3, -0.5), (x, 0.0)], fc="#A0AEC0", ec="#4A5568"))
ax.plot([0, 10], [-1.3, -1.3], color="#A0AEC0", lw=1)
sens = [(1.85, 0.32, "s", BLUE, "13.1"), (5.0, 0.32, "s", BLUE, "13.1"), (8.15, 0.32, "s", BLUE, "13.1"), (4.6, 0.32, "o", RED, "13.1"),
        (2.6, 0.16, "v", GREEN, "13.2"), (7.4, 0.16, "v", GREEN, "13.4"), (6.0, 0.16, "D", GOLD, "13.3"), (3.4, -0.7, "P", NAVY, "13.3")]
for x, y, mk, col, ex in sens: ax.plot(x, y + (0.1 if y > 0.2 else 0), marker=mk, color=col, ms=9, mec="white", mew=0.8, zorder=5)
leg = [("s", BLUE, "مقياس تسارع: الترددات الطبيعية (المثال 13.1)"), ("o", RED, "حساس حرارة يفسّر تغيّر التردد (المثال 13.1)"),
       ("v", GREEN, "نبضة فوق صوتية وصدى صدمي: سماكة البلاطة وعيوبها (13.2، 13.4)"), ("D", GOLD, "موجات قص: صلابة المادة (المثال 13.3)"),
       ("P", NAVY, "نصف الخلية على الركيزة: نشاط التآكل (الحالة الدراسية)")]
lx = fig.add_axes([0, 0, 1, 0.3]); lx.axis("off"); lx.set_xlim(0, 10); lx.set_ylim(0, 5.5)
for i, (mk, col, t) in enumerate(leg):
    lx.plot(9.7, 4.9 - i * 1.15, marker=mk, color=col, ms=8); lx.text(9.5, 4.9 - i * 1.15, t, ha="right", va="center", fontsize=9.3, color="#2D3748")
def inset(rect, kind, col):
    a = fig.add_axes(rect); a.set_xticks([]); a.set_yticks([])
    for s_ in a.spines.values(): s_.set_color(col)
    t = np.linspace(0, 1, 400)
    if kind == "acc": a.plot(t, np.exp(-3 * t) * np.sin(2 * np.pi * 9 * t), color=col, lw=0.9)
    elif kind == "echo": y = 0.05 * np.random.default_rng(0).normal(size=400); y[60:70] += np.hanning(10); y[260:272] += 0.6 * np.hanning(12); a.plot(t, y, color=col, lw=0.9)
    elif kind == "disp": f_ = np.linspace(100, 1000, 50); a.plot(f_, 2 + 0.6 * (f_ / 1000) ** 0.35, color=col, lw=1.4)
    else: f_ = np.linspace(0, 1, 300); a.plot(f_, np.exp(-((f_ - 0.45) / 0.03) ** 2) + 0.05, color=col, lw=1.0)
    return a
ins = [([0.06, 0.84, 0.17, 0.1], "acc", BLUE, "تسارع في الزمن", (1.85, 0.42)), ([0.29, 0.84, 0.17, 0.1], "echo", GREEN, "نبضة وصدى", (2.6, 0.26)),
       ([0.53, 0.84, 0.17, 0.1], "disp", GOLD, "منحنى تشتت", (6.0, 0.26)), ([0.77, 0.84, 0.17, 0.1], "spec", GREEN, "طيف الصدى الصدمي", (7.4, 0.26))]
from matplotlib.patches import ConnectionPatch
for rect, kind, col, t, (sx, sy_) in ins:
    a = inset(rect, kind, col); fig.text(rect[0] + rect[2] / 2, rect[1] + rect[3] + 0.012, t, ha="center", va="bottom", fontsize=9, color="#2D3748")
    fig.add_artist(ConnectionPatch(xyA=(0.5, 0.0), coordsA=a.transAxes, xyB=(sx, sy_ + 0.1), coordsB=ax.transData, color=col, lw=0.8, ls=":"))
save(fig, F + "nfig_bridge.png")

# ---------------------------------------------------------------- 8. the numeric guard on the three answers of Example 17.2
fig, ax = canvas(6.8, 3.9)
src = [("الغطاء الخرساني للحديد في الأساسات\nالملامسة للتربة لا يقل عن", "75 مم", "."),
       ("لا تفك الدعامات السفلية للبلاطات قبل", "14 يوماً", " إلا إذا أثبتت الفحوص…")]
ans = [("الحد الأدنى للغطاء في الأساسات\nالملامسة للتربة هو", "75 مم", 0, True), ("الحد الأدنى للغطاء في الأساسات\nالملامسة للتربة هو", "50 مم", 0, False),
       ("تفك الدعامات بعد", "7 أيام", 1, False)]
ax.text(5.3, 3.75, "المقطع المسترجَع", ha="center", fontsize=11, color=NAVY, fontweight="bold")
ax.text(1.75, 3.75, "جواب النموذج", ha="center", fontsize=11, color=NAVY, fontweight="bold")
sy = [2.85, 1.0]
for (a, num, b), y in zip(src, sy):
    ax.add_patch(FancyBboxPatch((3.85, y - 0.5), 2.9, 1.0, boxstyle="round,pad=0,rounding_size=0.08", fc="#F7FAFC", ec=GREY))
    ax.text(6.65, y + 0.17, a, ha="right", va="center", fontsize=8.8, color="#2D3748", linespacing=1.0)
    ax.text(6.65, y - 0.3, num, ha="right", va="center", fontsize=10, color=GREEN, fontweight="bold", bbox=dict(boxstyle="round,pad=0.15", fc=TINT[GREEN], ec=GREEN, lw=0.8))
ay = [3.1, 2.15, 1.0]
for (a, num, si, ok), y in zip(ans, ay):
    col = GREEN if ok else RED
    ax.add_patch(FancyBboxPatch((0.05, y - 0.44), 3.3, 0.9, boxstyle="round,pad=0,rounding_size=0.08", fc="white", ec=col, lw=1.2))
    ax.text(3.25, y + 0.17, a, ha="right", va="center", fontsize=8.8, color="#2D3748", linespacing=1.0)
    ax.text(3.25, y - 0.27, num, ha="right", va="center", fontsize=9.5, color=col, fontweight="bold", bbox=dict(boxstyle="round,pad=0.15", fc=TINT[col], ec=col, lw=0.8))
    ax.text(0.45, y, "مقبول" if ok else "مرفوض", ha="center", va="center", fontsize=10, color=col, fontweight="bold", rotation=12,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=col, lw=1.5))
    if ok: arrow(ax, (3.36, y - 0.24), (3.85, sy[si] - 0.3), col=GREEN, lw=1.3, head=10)
    else: ax.text(3.6, y - 0.24, "؟", ha="center", va="center", fontsize=14, color=RED, fontweight="bold")
ax.text(3.4, 0.12, "الحارس يبحث عن كل رقم بوحدته من الجواب داخل المقطع: الرقم غير المسنود يوقف الجواب قبل أن يصل إلى المهندس", ha="center", fontsize=8.6, color=GREY)
save(fig, F + "nfig_guard.png")
print("ok")
