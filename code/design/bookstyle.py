# Shared visual identity for the book's diagrams (colours, fonts, boxes, arrows)
import glob, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
for f in glob.glob(os.path.expanduser("~/.fonts/Amiri*.ttf")): fm.fontManager.addfont(f)
plt.rcParams.update({"font.family": ["AmiriBook", "Amiri", "DejaVu Sans"], "axes.spines.top": False,
                     "axes.spines.right": False, "axes.titleweight": "bold", "figure.dpi": 110})
NAVY, BLUE, ORANGE, GREEN, RED, GOLD, GREY = "#1A365D", "#2B6CB0", "#C05621", "#2F855A", "#C53030", "#B7791F", "#718096"
TINT = {NAVY: "#E6EEF7", BLUE: "#EBF4FF", ORANGE: "#FFF5EB", GREEN: "#F0FFF4", RED: "#FFF5F5", GOLD: "#FFFBEB", GREY: "#F7FAFC"}
def canvas(w, h):
    fig, ax = plt.subplots(figsize=(w, h)); ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis("off"); return fig, ax
def card(ax, x, y, w, h, title, body=None, col=BLUE, fs=13, bfs=10.5, num=None, shadow=True):
    if shadow: ax.add_patch(FancyBboxPatch((x+0.05, y-0.05), w, h, boxstyle="round,pad=0,rounding_size=0.12", fc="#00000014", ec="none"))
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.12", fc=TINT.get(col, "#fff"), ec=col, lw=1.6))
    ax.add_patch(FancyBboxPatch((x, y+h-0.09), w, 0.09, boxstyle="square,pad=0", fc=col, ec="none"))
    ty = y + h - 0.35 if body else y + h/2
    ax.text(x + w/2, ty, title, ha="center", va="center", fontsize=fs, color=NAVY, fontweight="bold")
    if body: ax.text(x + w/2, y + (h-0.5)/2, body, ha="center", va="center", fontsize=bfs, color="#2D3748", linespacing=1.15)
    if num is not None:
        ax.add_patch(Circle((x + w - 0.05, y + h - 0.05), 0.2, fc=col, ec="white", lw=1.5, zorder=5))
        ax.text(x + w - 0.05, y + h - 0.05, str(num), ha="center", va="center", color="white", fontsize=11, fontweight="bold", zorder=6)
def arrow(ax, a, b, col=GREY, lw=2.0, rad=0.0, ls="-", head=14):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=head, color=col, lw=lw, ls=ls, connectionstyle=f"arc3,rad={rad}"))
def save(fig, path): fig.savefig(path, dpi=220, bbox_inches="tight", pad_inches=0.08, facecolor="white"); plt.close(fig)
