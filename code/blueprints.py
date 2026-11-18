# Chapter blueprint diagrams (one per chapter), right-to-left flow
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib import font_manager as fm
from blueprint_data import CH
import glob, os
for f in glob.glob(os.path.expanduser("~/.fonts/Amiri*.ttf")): fm.fontManager.addfont(f)  # Amiri: https://github.com/aliftype/amiri
plt.rcParams["font.family"] = ["AmiriBook", "Amiri", "DejaVu Sans"]
A = lambda s: s   # matplotlib 3.11 shapes and orders Arabic itself
COL = [("#1A365D", "#E6EEF7"), ("#2B6CB0", "#EBF4FF"), ("#C05621", "#FFF5EB"), ("#2F855A", "#F0FFF4")]
def box(ax, x, y, w, h, head, items, c):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.03", fc=c[1], ec=c[0], lw=1.4))
    ax.add_patch(FancyBboxPatch((x, y + h - 0.13), w, 0.13, boxstyle="round,pad=0.012,rounding_size=0.03", fc=c[0], ec=c[0], lw=1.4))
    ax.text(x + w / 2, y + h - 0.065, A(head), ha="center", va="center", color="white", fontsize=11, fontweight="bold")
    n = len(items); step = (h - 0.18) / max(n, 1)
    for i, t in enumerate(items):
        ax.text(x + w - 0.02, y + h - 0.2 - i * step, A("• " + t), ha="right", va="top", fontsize=8.6, color="#1A202C", wrap=True)
for k, d in CH.items():
    fig = plt.figure(figsize=(9.6, 3.4)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 4.2); ax.set_ylim(0, 1.18); ax.axis("off")
    cols = [("المشكلة المحفّزة", [d["problem"]]), ("المفاهيم والأدوات", d["concepts"]), ("الأمثلة المحلولة", d["examples"]), ("ما تخرج به", d["skills"])]
    w, gap = 0.92, 0.12; xs = [4.2 - 0.06 - (i + 1) * w - i * gap for i in range(4)]
    for i, ((head, items), x) in enumerate(zip(cols, xs)):
        box(ax, x, 0.16, w, 0.94, head, items, COL[i])
        if i < 3:
            ax.add_patch(FancyArrowPatch((x - 0.005, 0.63), (x - gap + 0.005, 0.63), arrowstyle="-|>", mutation_scale=16, lw=1.6, color="#4A5568"))
    ax.text(4.14, 0.06, A("يعتمد على: " + d["needs"]), ha="right", va="center", fontsize=9, color="#4A5568")
    ax.text(0.06, 0.06, A("يقود إلى: " + d["leads"]), ha="left", va="center", fontsize=9, color="#4A5568")
    fig.savefig(f"fig/fig{k}_0_blueprint.png", dpi=220); plt.close(fig)
print("ok")
