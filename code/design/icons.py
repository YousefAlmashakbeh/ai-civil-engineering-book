# Line icons for the recurring chapter sections (navy, square)
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Rectangle, FancyBboxPatch
N = "#1A365D"; O = "../../figures/icons/"
def new():
    f, a = plt.subplots(figsize=(1, 1)); a.set_xlim(0, 1); a.set_ylim(0, 1); a.axis("off"); a.set_aspect("equal"); return f, a
def done(f, n): f.savefig(O + n + ".png", dpi=200, transparent=True); plt.close(f)
f, a = new()                                             # objectives: target
for r in (0.42, 0.28, 0.14): a.add_patch(Circle((0.5, 0.5), r, fill=False, ec=N, lw=3))
a.add_patch(Circle((0.5, 0.5), 0.04, fc=N)); done(f, "goals")
f, a = new()                                             # motivating problem: question mark
a.add_patch(Circle((0.5, 0.5), 0.42, fill=False, ec=N, lw=3)); a.text(0.5, 0.48, "?", ha="center", va="center", fontsize=40, color=N, fontweight="bold", family="DejaVu Sans"); done(f, "problem")
f, a = new()                                             # limits: warning triangle
a.add_patch(Polygon([(0.5, 0.92), (0.08, 0.12), (0.92, 0.12)], fill=False, ec=N, lw=3, joinstyle="round"))
a.text(0.5, 0.4, "!", ha="center", va="center", fontsize=34, color=N, fontweight="bold", family="DejaVu Sans"); done(f, "limits")
f, a = new()                                             # summary: checklist
for k, y in enumerate((0.75, 0.5, 0.25)):
    a.plot([0.12, 0.2, 0.32], [y, y - 0.07, y + 0.08], color=N, lw=3, solid_capstyle="round"); a.plot([0.45, 0.9], [y, y], color=N, lw=3, solid_capstyle="round")
done(f, "summary")
f, a = new()                                             # exercises: pencil
a.add_patch(Polygon([(0.2, 0.2), (0.3, 0.42), (0.75, 0.87), (0.87, 0.75), (0.42, 0.3)], fill=False, ec=N, lw=3, joinstyle="round"))
a.plot([0.2, 0.3], [0.2, 0.42], color=N, lw=3); a.plot([0.68, 0.8], [0.8, 0.68], color=N, lw=3); done(f, "exercises")
f, a = new()                                             # reading: open book
a.add_patch(Polygon([(0.5, 0.25), (0.08, 0.32), (0.08, 0.8), (0.5, 0.72)], fill=False, ec=N, lw=3, joinstyle="round"))
a.add_patch(Polygon([(0.5, 0.25), (0.92, 0.32), (0.92, 0.8), (0.5, 0.72)], fill=False, ec=N, lw=3, joinstyle="round")); done(f, "reading")
print("icons ok")
