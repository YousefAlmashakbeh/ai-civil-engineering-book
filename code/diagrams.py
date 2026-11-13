import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle
def box(ax, x, y, w, h, t, fc="#e8f0fb", ec="tab:blue", fs=8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.02", fc=fc, ec=ec, lw=1.2))
    ax.text(x + w/2, y + h/2, t, ha="center", va="center", fontsize=fs)
def arr(ax, a, b, c="k", ls="-"):
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="->", color=c, lw=1.2, ls=ls))
# Fig 1.2 workflow
fig, ax = plt.subplots(figsize=(10, 3.2)); ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
steps = ["1. Engineering\nquestion", "2. Data\n(lab, field, open)", "3. Clean &\nphysics checks", "4. Features from\nengineering", "5. Baseline:\ncode/physics eq.", "6. ML model +\nhonest split", "7. Uncertainty &\nlimits", "8. Engineer\ndecides & signs"]
xs = [0.01 + i*0.124 for i in range(8)]
for x, s in zip(xs, steps):
    fc = "#fdeee6" if s.startswith(("5", "8")) else "#e8f0fb"; ec = "tab:orange" if s.startswith(("5", "8")) else "tab:blue"
    box(ax, x, 0.42, 0.11, 0.3, s, fc, ec, 7.5)
for x in xs[:-1]: arr(ax, (x+0.11, 0.57), (x+0.124, 0.57))
ax.annotate("", xy=(xs[1]+0.055, 0.40), xytext=(xs[6]+0.055, 0.40), arrowprops=dict(arrowstyle="->", color="tab:red", connectionstyle="arc3,rad=-0.35", ls="--"))
ax.text(0.5, -0.12, "fails a check (leakage, out-of-range, unsafe errors) -> go back to data", ha="center", fontsize=8, color="tab:red")
ax.text(0.5, 0.9, "AI project workflow in civil engineering (used throughout the book)", ha="center", fontsize=10)
plt.savefig("fig/fig1_2_workflow.png", dpi=150, bbox_inches="tight"); plt.close()
# Fig 8.6 accelerated corrosion setup
fig, ax = plt.subplots(figsize=(7.5, 3.6)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(-0.3, 6)
ax.add_patch(Rectangle((0.5, 0.0), 9, 2.8, fc="#dbeafe", ec="k")); ax.text(9.3, 2.0, "2% NaCl\nsolution", ha="right", fontsize=8)
ax.add_patch(Rectangle((2, 1.2), 6, 2.2, fc="#d4d4d4", ec="k", lw=1.5)); ax.text(5, 3.1, "RC specimen", ha="center", fontsize=8)
ax.plot([2.3, 7.7], [1.7, 1.7], color="#8b4513", lw=5); ax.text(5, 1.95, "steel bar = anode (+)", ha="center", fontsize=7.5)
ax.add_patch(Rectangle((1.5, 0.7), 7, 0.15, fc="0.3", ec="k")); ax.text(5, 0.5, "steel plate = cathode (-)", ha="center", va="top", fontsize=7.5)
ax.add_patch(Rectangle((4, 4.6), 2, 0.9, fc="#fef3c7", ec="k")); ax.text(5, 5.05, "DC power supply\n(constant current)", ha="center", va="center", fontsize=7.5)
ax.plot([4.2, 2.4, 2.4], [4.6, 4.6, 1.75], "r-", lw=1.2); ax.text(2.1, 4.1, "+", color="r", fontsize=12)
ax.plot([5.8, 9.2, 9.2, 8.5], [4.6, 4.6, 0.78, 0.78], "k-", lw=1.2); ax.text(9.35, 4.1, "-", fontsize=14)
ax.text(5, 3.75, "Faraday: mass loss  m = M I t / (z F)", ha="center", fontsize=8, style="italic")
plt.savefig("fig/fig8_6_setup.png", dpi=150, bbox_inches="tight"); plt.close()
