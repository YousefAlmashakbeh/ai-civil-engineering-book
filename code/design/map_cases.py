from bookstyle import *
from matplotlib.patches import Ellipse, Polygon
F = "../../figures/"
fig, ax = plt.subplots(figsize=(9.5, 11)); ax.set_xlim(34.3, 38.6); ax.set_ylim(29.15, 33.15); ax.set_aspect(1/np.cos(np.radians(31))) if False else None
ax.axis("off")
import numpy as np
ax.set_aspect(1/np.cos(np.radians(31)))
# schematic water bodies
ax.add_patch(Ellipse((35.50, 31.50), 0.16, 0.75, fc="#BEE3F8", ec="#90CDF4")); ax.text(35.36, 31.78, "البحر الميت", ha="right", va="center", fontsize=10, color="#2B6CB0")
ax.add_patch(Polygon([(34.92, 29.2), (35.00, 29.54), (35.06, 29.2)], fc="#BEE3F8", ec="#90CDF4")); ax.text(34.88, 29.35, "خليج العقبة", ha="right", fontsize=10, color="#2B6CB0")
city = {"إربد": (35.85, 32.55), "جرش": (35.90, 32.28), "الزرقاء": (36.09, 32.07), "عمّان": (35.93, 31.95), "الكرك": (35.70, 31.18),
        "معان": (35.73, 30.19), "القويرة": (35.31, 29.80), "العقبة": (35.01, 29.53), "غور الحديثة": (35.57, 31.30)}
carrier = [city[k] for k in ("العقبة", "القويرة", "معان", "الكرك", "عمّان")]
ax.plot(*zip(*carrier), color=BLUE, lw=3.2, alpha=0.85, solid_capstyle="round", zorder=2)
ax.plot(*zip(*[city[k] for k in ("إربد", "جرش", "عمّان")]), color=ORANGE, lw=3, ls=(0, (4, 2)), zorder=2)
ax.plot(*zip(*[city[k] for k in ("عمّان", "الزرقاء")]), color=GREEN, lw=3, ls=(0, (1, 1.5)), zorder=2)
for k, (x, y) in city.items():
    ax.scatter(x, y, s=55, color=NAVY, zorder=4, edgecolor="white", linewidth=1.2)
    ax.text(x-(0.12 if k=="غور الحديثة" else 0.05), y+(0.0 if k=="غور الحديثة" else 0), k, ha="right", va="center", fontsize=11.5, color=NAVY, fontweight="bold", zorder=5)
cases = [("14", "وفيات حوادث الطرق 2019–2024", None, RED), ("15", "فاقد المياه وكشف التسرب الليلي", None, BLUE),
         ("10", "انهيارات المارل على طريق إربد–عمّان", "جرش", ORANGE), ("11", "كلفة الباص سريع التردد وجدوله", "الزرقاء", GREEN),
         ("13", "مراقبة ترددات جسر عبدون", "عمّان", NAVY), ("12", "الحفر الخسفية وأثر دقة الصورة", "غور الحديثة", GOLD),
         ("16", "توأم هيدروليكي للناقل الوطني", "معان", BLUE), ("7", "جدولة الضخ مع محطة القويرة الشمسية", "القويرة", BLUE),
         ("9", "الخطر الزلزالي في العقبة والكود", "العقبة", RED)]
ys = np.linspace(32.62, 29.45, len(cases))
for (n, t, c, col), yy in zip(cases, ys):
    bx = 36.75
    ax.add_patch(FancyBboxPatch((bx, yy-0.13), 1.8, 0.26, boxstyle="round,pad=0,rounding_size=0.04", fc=TINT[col], ec=col, lw=1.4, zorder=3))
    ax.add_patch(FancyBboxPatch((bx+1.42, yy-0.13), 0.38, 0.26, boxstyle="round,pad=0,rounding_size=0.04", fc=col, ec=col, zorder=4))
    ax.text(bx+1.61, yy, "\u202a" + n + ".أ\u202c", ha="center", va="center", color="white", fontsize=11, fontweight="bold", zorder=5)
    ax.text(bx+1.37, yy, t, ha="right", va="center", fontsize=10, color=NAVY, zorder=5)
    if c:
        x, y = city[c]; ax.annotate("", xy=(x+0.03, y), xytext=(bx-0.02, yy), arrowprops=dict(arrowstyle="-", color=col, lw=1, alpha=0.6, connectionstyle="arc3,rad=0.0"), zorder=1)
    else:
        ax.text(bx-0.05, yy, "على مستوى المملكة", ha="right", va="center", fontsize=9.5, color=GREY)
ax.text(36.45, 33.1, "أطلس الحالات العربية المحلولة", ha="center", va="top", fontsize=19, color=NAVY, fontweight="bold")
lg = [(BLUE, "-", "الناقل الوطني للمياه (العقبة–عمّان)"), (ORANGE, (0, (4, 2)), "طريق إربد–جرش–عمّان"), (GREEN, (0, (1, 1.5)), "الباص سريع التردد عمّان–الزرقاء")]
for i, (c, ls, t) in enumerate(lg):
    y = 32.75 - i*0.17; ax.plot([34.45, 34.75], [y, y], color=c, lw=3, ls=ls); ax.text(34.8, y, t, ha="left", va="center", fontsize=9.5, color=NAVY)
ax.text(34.45, 29.22, "مخطط توضيحي: المواقع بإحداثياتها التقريبية، والحدود والمسطحات المائية غير مرسومة بمقياس", ha="left", fontsize=8.5, color=GREY)
save(fig, F + "figT2_atlas.png")
