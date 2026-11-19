# Chapter blueprints (one per chapter), drawn at their printed size (12.6 cm wide), right-to-left
import re, textwrap
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
from matplotlib import font_manager as fm
from blueprint_data import CH
fm.fontManager.addfont("/root/.fonts/AmiriBook-Regular.ttf"); fm.fontManager.addfont("/root/.fonts/AmiriBook-Bold.ttf")
plt.rcParams["font.family"] = "AmiriBook"
PART = [(range(1, 5), "#1A365D", "#E6EEF7", "الأسس"), (range(5, 8), "#2B6CB0", "#EBF4FF", "الأدوات"),
        (range(8, 12), "#C05621", "#FFF5EB", "التصميم والمواد والتشييد"), (range(12, 16), "#2F855A", "#F0FFF4", "البنية التحتية"),
        (range(16, 19), "#B7791F", "#FFFBEA", "آفاق متقدمة")]
def part(k): return next(p for p in PART if k in p[0])
def chapters(s):
    if "التطبيقية" in s: return set(range(8, 19))
    out = set()
    for a, b in re.findall(r"(\d+)\s*[–-]\s*(\d+)", s): out |= set(range(int(a), int(b) + 1))
    out |= {int(x) for x in re.findall(r"\d+", s)}
    return out
W = 4.96; LH = 0.148            # inch width; line height for 8.5 pt
def wrap(items, chars): return [textwrap.wrap(t, chars) or [""] for t in items]
for k, d in CH.items():
    rng, dark, light, pname = part(k)
    cols = [("المفاهيم والأدوات", d["concepts"], 1.86, 33), ("الأمثلة المحلولة", d["examples"], 1.86, 33), ("ما تخرج به", d["skills"], 1.04, 17)]
    wrapped = [wrap(it, ch) for _, it, _, ch in cols]
    nlines = max(sum(len(w) for w in col) for col in wrapped)
    mid = 0.30 + nlines * LH + 0.12
    H = 0.48 + 0.08 + mid + 0.10 + 0.56
    fig = plt.figure(figsize=(W, H)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
    # problem band with the chapter number
    yb = H - 0.50
    ax.add_patch(FancyBboxPatch((0.03, yb), W - 0.06, 0.46, boxstyle="round,pad=0,rounding_size=0.06", fc=light, ec=dark, lw=1.2))
    ax.add_patch(Circle((W - 0.30, yb + 0.23), 0.19, fc=dark, ec="none"))
    ax.text(W - 0.30, yb + 0.225, str(k), ha="center", va="center", color="white", fontsize=13, fontweight="bold")
    ax.text(W - 0.56, yb + 0.33, "المشكلة المحفّزة", ha="right", va="center", fontsize=8.5, color=dark, fontweight="bold")
    ax.text(W - 0.56, yb + 0.13, d["problem"], ha="right", va="center", fontsize=10, color="#1A202C", fontweight="bold")
    ax.text(0.12, yb + 0.33, "الباب: " + pname, ha="left", va="center", fontsize=8, color=dark)
    # three columns
    ytop = yb - 0.08; x = W - 0.03
    for (head, items, w, _), wl in zip(cols, wrapped):
        x0 = x - w
        ax.add_patch(FancyBboxPatch((x0, ytop - mid), w, mid, boxstyle="round,pad=0,rounding_size=0.05", fc="white", ec=dark, lw=0.9))
        ax.add_patch(FancyBboxPatch((x0, ytop - 0.24), w, 0.24, boxstyle="round,pad=0,rounding_size=0.05", fc=dark, ec=dark, lw=0.9))
        ax.text(x0 + w / 2, ytop - 0.12, head, ha="center", va="center", color="white", fontsize=9.5, fontweight="bold")
        y = ytop - 0.31
        for it, lines in zip(items, wl):
            tc = "#C05621" if re.match(r"حالة \d+\.أ", it) else "#1A202C"      # Arab cases in the colour of their headings
            for j, ln in enumerate(lines):
                ax.text(x - 0.07, y, ("• " if j == 0 else "   ") + ln, ha="right", va="top", fontsize=8.5, color=tc); y -= LH
        x = x0 - 0.06
    # chapter strip: where this chapter sits in the book
    needs, leads = chapters(d["needs"]), chapters(d["leads"])
    ys = 0.30; xs = {}; xx = W - 0.22
    for rr, dk, lt, _ in PART:
        for c in rr: xs[c] = xx; xx -= 0.243
        xx -= 0.06
    for c, xc in xs.items():
        _, dk, lt, _ = part(c)
        if c == k:   ax.add_patch(Circle((xc, ys), 0.122, fc=dk, ec=dk, lw=1.2)); col, fw = "white", "bold"
        elif c in needs: ax.add_patch(Circle((xc, ys), 0.10, fc=lt, ec=dk, lw=2.0)); col, fw = dk, "bold"
        elif c in leads: ax.add_patch(Circle((xc, ys), 0.10, fc="white", ec=dk, lw=1.2, ls=(0, (2, 1.5)))); col, fw = dk, "normal"
        else:        ax.add_patch(Circle((xc, ys), 0.085, fc="#EDF2F7", ec="none")); col, fw = "#A0AEC0", "normal"
        ax.text(xc, ys - 0.005, str(c), ha="center", va="center", fontsize=8, color=col, fontweight=fw)
    lx = W - 0.12
    for kind, lab in (("cur", "هذا الفصل"), ("need", "يعتمد عليه هذا الفصل"), ("lead", "يقود إليه")):
        if kind == "cur": ax.add_patch(Circle((lx, 0.085), 0.05, fc=dark, ec=dark))
        elif kind == "need": ax.add_patch(Circle((lx, 0.085), 0.05, fc=light, ec=dark, lw=1.6))
        else: ax.add_patch(Circle((lx, 0.085), 0.05, fc="white", ec=dark, lw=1.0, ls=(0, (2, 1.5))))
        t = ax.text(lx - 0.09, 0.08, lab, ha="right", va="center", fontsize=8, color="#4A5568")
        fig.canvas.draw(); bb = t.get_window_extent().transformed(ax.transData.inverted()); lx = bb.x0 - 0.22
    fig.savefig(f"fig/fig{k}_0_blueprint.png", dpi=300); plt.close(fig)
print("ok")
