from bookstyle import *
from matplotlib.patches import Ellipse, Polygon
F = "../../figures/"
fig, ax = plt.subplots(figsize=(6.7, 7.2)); ax.set_xlim(34.3, 38.65); ax.set_ylim(28.98, 33.2); ax.set_aspect(1/np.cos(np.radians(31))) if False else None
ax.axis("off")
import numpy as np
ax.set_aspect(1/np.cos(np.radians(31)))
# simplified outline of Jordan (schematic, about 25 vertices)
JO = [(35.62,32.68),(35.78,32.75),(36.07,32.53),(36.38,32.52),(36.84,32.31),(38.79,33.38),(39.30,32.24),(38.99,32.00),(37.00,31.50),
      (37.99,30.50),(37.67,30.34),(37.50,30.00),(36.74,29.86),(36.50,29.50),(36.07,29.19),(34.96,29.36),(35.06,29.85),(35.15,30.20),
      (35.33,30.70),(35.42,31.05),(35.50,31.25),(35.56,31.55),(35.55,31.80),(35.53,32.10),(35.56,32.40)]
ax.add_patch(Polygon(JO, closed=True, fc="#F7FAFC", ec="#A0AEC0", lw=1.2, zorder=0))
ax.annotate("", xy=(34.55, 33.12), xytext=(34.55, 32.82), arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.6, mutation_scale=14)); ax.text(34.55, 32.74, "ش", ha="center", va="top", fontsize=11, color=NAVY, fontweight="bold")
# schematic water bodies
ax.add_patch(Ellipse((35.49, 31.45), 0.15, 0.70, fc="#BEE3F8", ec="#90CDF4")); ax.text(35.38, 31.62, "البحر\nالميت", ha="right", va="center", fontsize=9.5, color="#2B6CB0")
ax.add_patch(Polygon([(34.92, 29.2), (35.00, 29.54), (35.06, 29.2)], fc="#BEE3F8", ec="#90CDF4")); ax.text(34.88, 29.30, "خليج\nالعقبة", ha="right", va="center", fontsize=9.5, color="#2B6CB0")
city = {"إربد": (35.85, 32.55), "جرش": (35.90, 32.28), "الزرقاء": (36.09, 32.07), "عمّان": (35.93, 31.95), "القطرانة": (36.04, 31.25),
        "معان": (35.73, 30.19), "القويرة": (35.31, 29.80), "العقبة": (35.01, 29.53), "غور الحديثة": (35.57, 31.30)}
carrier = [city[k] for k in ("العقبة", "القويرة", "معان", "القطرانة", "عمّان")]
ax.plot(*zip(*carrier), color=BLUE, lw=3.2, alpha=0.85, solid_capstyle="round", zorder=2)
ax.plot(*zip(*[city[k] for k in ("إربد", "جرش", "عمّان")]), color=ORANGE, lw=3, ls=(0, (4, 2)), zorder=2)
ax.plot(*zip(*[city[k] for k in ("عمّان", "الزرقاء")]), color=GREEN, lw=3.6, ls=(0, (1.5, 1)), zorder=4, solid_capstyle="round")
for k, (x, y) in city.items():
    ax.scatter(x, y, s=55, color=NAVY, zorder=4, edgecolor="white", linewidth=1.2)
    dx, dy, ha, va = {"الزرقاء": (0.0, 0.07, "center", "bottom"), "غور الحديثة": (-0.10, 0.0, "right", "center"), "القطرانة": (0.05, -0.06, "left", "top")}.get(k, (-0.05, 0.0, "right", "center"))
    ax.text(x+dx, y+dy, k, ha=ha, va=va, fontsize=10, color=NAVY, fontweight="bold", zorder=5, bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.7))
cases = [("14", "وفيات الطرق 2019–2024 (المملكة)", None, RED), ("15", "فاقد المياه وكشف التسرب (المملكة)", None, BLUE),
         ("10", "انهيارات المارل على طريق إربد–عمّان", "جرش", ORANGE), ("11", "كلفة الباص سريع التردد وجدوله", "الزرقاء", GREEN),
         ("13", "مراقبة ترددات جسر عبدون", "عمّان", NAVY), ("12", "الحفر الخسفية وأثر دقة الصورة", "غور الحديثة", GOLD),
         ("16", "توأم هيدروليكي للناقل الوطني", "معان", BLUE), ("7", "جدولة الضخ مع محطة القويرة الشمسية", "القويرة", BLUE),
         ("9", "الخطر الزلزالي في العقبة والكود", "العقبة", RED)]
ys = np.linspace(32.80, 30.30, len(cases))
for (n, t, c, col), yy in zip(cases, ys):
    bx = 36.55
    ax.add_patch(FancyBboxPatch((bx, yy-0.13), 2.05, 0.26, boxstyle="round,pad=0,rounding_size=0.04", fc=TINT[col], ec=col, lw=1.4, zorder=3))
    ax.add_patch(FancyBboxPatch((bx+1.67, yy-0.13), 0.38, 0.26, boxstyle="round,pad=0,rounding_size=0.04", fc=col, ec=col, zorder=4))
    ax.text(bx+1.86, yy, "\u202a" + n + ".أ\u202c", ha="center", va="center", color="white", fontsize=10, fontweight="bold", zorder=5)
    ax.text(bx+1.62, yy, t, ha="right", va="center", fontsize=9.3, color=NAVY, zorder=5)
    if c:
        x, y = city[c]; ax.annotate("", xy=(x+0.03, y), xytext=(bx-0.02, yy), arrowprops=dict(arrowstyle="-", color=col, lw=1, alpha=0.6, connectionstyle=f"arc3,rad={0.3 if n == '12' else (0.4 if n == '10' else 0.0)}"), zorder=1)
ax.text(36.6, 33.18, "أطلس الحالات العربية المحلولة", ha="center", va="top", fontsize=15, color=NAVY, fontweight="bold")
lg = [(BLUE, "-", "الناقل الوطني للمياه (العقبة–عمّان)"), (ORANGE, (0, (4, 2)), "طريق إربد–جرش–عمّان"), (GREEN, (0, (1.5, 1)), "الباص سريع التردد عمّان–الزرقاء")]
for i, (c, ls, t) in enumerate(lg):
    y = 29.90 - i*0.19; ax.plot([36.85, 37.15], [y, y], color=c, lw=3, ls=ls); ax.text(37.2, y, t, ha="left", va="center", fontsize=9, color=NAVY)
ax.text(38.62, 29.06, "مخطط توضيحي: المواقع بإحداثياتها التقريبية، والحدود والمسطحات المائية مبسّطة وغير مرسومة بمقياس", ha="right", fontsize=8, color=GREY)
save(fig, F + "figT2_atlas.png")
