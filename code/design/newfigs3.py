# New explanatory figures added after the committee's fourth reading (all values computed here from the book's code or taken from its tables)
# Run from code/design: NOHOOK=1 python3 newfigs3.py
import sys, re, numpy as np, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, "..")
from bookstyle import *
from matplotlib.patches import Polygon, Rectangle, FancyBboxPatch, Circle, FancyArrowPatch, Arc
F = "../../figures/"
plt.rcParams.update({"font.size": 9.5})
def iso(s): return "⁦" + s + "⁩"
LAT = dict(fontfamily="DejaVu Sans")
ONLY = set(sys.argv[1:])
def want(k): return not ONLY or k in ONLY
def canvas(w, h):
    fig = plt.figure(figsize=(w, h)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis("off"); return fig, ax
def box(ax, x, y, w, h, col, lw=1.4, fc=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.08", fc=fc or TINT.get(col, "#fff"), ec=col, lw=lw))

# ================================================================ 1.2 three knowledge models (Section 1.5, numbers of Example 1.2)
if want("models3"):
    fig, ax = canvas(5.6, 3.25)
    rows = [  # (y, colour, ls, title, box text, example, value at w/c = 0.30 and 5 % air)
        (2.62, "#2D3748", "--", "النموذج الفيزيائي", "معادلة من الفيزياء\n" + iso("f(x)"), "قانون أبرامز", "53.8"),
        (1.62, ORANGE, "-", "النموذج المبني على البيانات", "نموذج يتعلّم من الأمثلة\n" + r"$\hat{f}_\theta(x)$", "الغابة العشوائية (المثالان 1.1 و1.2)", "41.5"),
        (0.62, BLUE, "-", "النموذج الهجين", None, "أبرامز × تصحيح تتعلّمه الغابة (المثال 1.2)", "46.4")]
    ax.text(0.15, 3.17, "الرقم تحت y: التنبؤ عند w/c = 0.30 وهواء 5%؛ الحقيقة " + iso("45.8 MPa"), ha="left", va="top", fontsize=8.6, color=GREY)
    for y, c, ls, title, body, ex, val in rows:
        ax.text(5.5, y + 0.12, title, ha="right", va="center", fontsize=9.6, color=c if c != "#2D3748" else NAVY, fontweight="bold")
        ax.text(5.5, y - 0.2, ex, ha="right", va="center", fontsize=8.6, color="#4A5568")
        # x on the right of the chain, y on the left (reading from the right)
        ax.add_patch(Circle((3.52, y), 0.17, fc="white", ec=c, lw=1.3)); ax.text(3.52, y, "x", ha="center", va="center", fontsize=10, **LAT)
        ax.add_patch(Circle((0.55, y), 0.17, fc="white", ec=c, lw=1.3)); ax.text(0.55, y, "y", ha="center", va="center", fontsize=10, **LAT)
        ax.text(0.55, y - 0.3, val, ha="center", va="top", fontsize=8.8, color=c, fontweight="bold", **LAT)
        if body:
            ax.add_patch(FancyBboxPatch((1.35, y - 0.3), 1.45, 0.6, boxstyle="round,pad=0,rounding_size=0.08", fc=TINT.get(c, "#EDF2F7"), ec=c, lw=1.4, ls=ls))
            ax.text(2.075, y, body, ha="center", va="center", fontsize=8.8, color=NAVY, linespacing=1.15)
            arrow(ax, (3.34, y), (2.82, y), col=c, lw=1.4, head=10); arrow(ax, (1.33, y), (0.73, y), col=c, lw=1.4, head=10)
    y = 0.62; c = BLUE
    ax.add_patch(FancyBboxPatch((2.05, y + 0.02), 1.0, 0.36, boxstyle="round,pad=0,rounding_size=0.06", fc="#EDF2F7", ec="#2D3748", lw=1.2, ls="--"))
    ax.text(2.55, y + 0.2, "الفيزياء " + iso("f"), ha="center", va="center", fontsize=8.8, color=NAVY)
    ax.add_patch(FancyBboxPatch((2.05, y - 0.4), 1.0, 0.36, boxstyle="round,pad=0,rounding_size=0.06", fc=TINT[ORANGE], ec=ORANGE, lw=1.2))
    ax.text(2.72, y - 0.22, "تصحيح", ha="center", va="center", fontsize=8.8, color=NAVY)
    ax.text(2.3, y - 0.22, r"$\hat{g}_\theta$", ha="center", va="center", fontsize=8.8, color=NAVY)
    ax.text(1.3, y - 0.24, "(أو ×)", ha="center", va="top", fontsize=8.6, color=BLUE)
    ax.add_patch(Circle((1.3, y), 0.19, fc=TINT[BLUE], ec=BLUE, lw=1.4)); ax.text(1.3, y, "+", ha="center", va="center", fontsize=13, color=BLUE, fontweight="bold", **LAT)
    arrow(ax, (3.34, y + 0.05), (3.07, y + 0.2), col=c, lw=1.2, head=9); arrow(ax, (3.34, y - 0.05), (3.07, y - 0.22), col=c, lw=1.2, head=9)
    arrow(ax, (2.03, y + 0.2), (1.47, y + 0.07), col=c, lw=1.2, head=9); arrow(ax, (2.03, y - 0.22), (1.47, y - 0.07), col=c, lw=1.2, head=9)
    arrow(ax, (1.11, y), (0.73, y), col=c, lw=1.4, head=10)
    for yy in (2.12, 1.12): ax.plot([0.2, 5.5], [yy, yy], color="#E2E8F0", lw=0.8)
    save(fig, F + "nfig3_models3.png")

# ================================================================ 2.1 shear building of Example 2.1: loads, displacements, modes
if want("building"):
    from scipy.linalg import eigh
    k = np.array([2.0e5, 1.5e5, 1.0e5]); K = np.array([[k[0]+k[1], -k[1], 0], [-k[1], k[1]+k[2], -k[2]], [0, -k[2], k[2]]])
    Fv = np.array([10., 20., 30.]); u = np.linalg.solve(K, Fv); M = np.diag([50., 50., 50.])
    w2, phi = eigh(K, M); f = np.sqrt(w2) / (2 * np.pi); phi = phi / np.abs(phi).max(0)
    phi = phi * np.sign(phi[2]) if False else phi
    print("building u (mm):", np.round(u * 1000, 3), " f (Hz):", np.round(f, 2)); print("modes:", np.round(phi.T, 2))
    fig, axs = plt.subplots(1, 5, figsize=(5.6, 2.75), gridspec_kw=dict(width_ratios=[1.0, 1.0, 1.0, 1.15, 1.25], wspace=0.06))
    fig.subplots_adjust(left=0.0, right=1.0, top=0.9, bottom=0.1)
    hs = [0, 1, 2, 3]; W0 = 0.5
    def frame(a, dx, col, lw=1.6, ghost=True):
        if ghost:
            for x0 in (-W0, W0): a.plot([x0, x0], [0, 3], color="#CBD5E0", lw=1.0, ls=":")
            for j in (1, 2, 3): a.plot([-W0, W0], [j, j], color="#CBD5E0", lw=1.0, ls=":")
        xs = np.r_[0, dx]
        for s in (-W0, W0): a.plot(xs + s, hs, color=col, lw=lw)
        for j in (1, 2, 3): a.plot([xs[j] - W0, xs[j] + W0], [j, j], color=col, lw=lw + 1.2, solid_capstyle="butt")
        a.plot([-0.9, 0.9], [0, 0], color="#4A5568", lw=1.2)
        for xx in np.linspace(-0.85, 0.85, 8): a.plot([xx, xx - 0.12], [0, -0.12], color="#4A5568", lw=0.7)
        a.set_xlim(-1.25, 1.45); a.set_ylim(-0.55, 3.75); a.axis("off")
    # panel 1 (rightmost): structure and loads
    a = axs[4]; frame(a, np.zeros(3), NAVY, ghost=False)
    for j in (1, 2, 3):
        arrow(a, (-1.45, j), (-W0 - 0.04, j), col=RED, lw=1.4, head=9); a.text(-1.5, j + 0.1, f"{Fv[j-1]:.0f} kN", ha="left", va="bottom", fontsize=8.6, color=RED, **LAT)
        a.text(0, j - 0.5, f"k{j}", ha="center", va="center", fontsize=8.6, color=NAVY, **LAT)
    a.text(0.0, 3.25, "كتلة الطابق " + iso("50 t"), ha="center", va="bottom", fontsize=8.6, color=NAVY)
    a.set_xlim(-1.75, 0.95)
    a.set_title("المبنى والأحمال", fontsize=9.6, pad=1)
    # panel 2: deformed shape (exaggerated)
    a = axs[3]; sc = 0.85 / u.max(); frame(a, u * sc, BLUE)
    for j in (1, 2, 3): a.text(u[j-1] * sc - W0 - 0.06, j + 0.08, f"{u[j-1]*1000:.2f}", ha="right", va="bottom", fontsize=8.6, color=BLUE, **LAT)
    a.text(0.1, -0.42, "mm (مضخّمة)", ha="center", va="top", fontsize=8.6, color=GREY)
    a.set_title("الإزاحات Ku = F", fontsize=9.6, pad=1)
    # panels 3-5: the three modes
    for m, a in zip(range(3), [axs[2], axs[1], axs[0]]):
        frame(a, phi[:, m] * 0.7, [GREEN, GOLD, ORANGE][m])
        a.set_title(f"النمط {m+1}: {f[m]:.2f} Hz", fontsize=9.6, pad=1)
    axs[0].set_xlim(-1.4, 1.3)
    fig.text(0.38, 0.0, iso("K φ = ω² M φ") + "   الأنماط من مسألة القيم الذاتية", ha="center", va="bottom", fontsize=9, color="#4A5568")
    fig.add_artist(plt.Line2D([0.583, 0.583], [0.08, 0.92], color="#CBD5E0", lw=0.9, transform=fig.transFigure))
    save(fig, F + "nfig3_building.png")

# ================================================================ 5.1 the depth-2 tree of Example 5.2 (same split, same data)
if want("tree2"):
    from ch5_data import make_concrete
    from sklearn.model_selection import GroupShuffleSplit
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.metrics import mean_absolute_error as mae
    df = make_concrete(); V = ["cement", "slag", "flyash", "water", "sp", "coarse", "fine"]
    X = df[V + ["age"]].copy(); X["log_age"] = np.log(X.pop("age")); y = df.fc.values; g = df.mix.values
    tr, te = next(GroupShuffleSplit(1, test_size=0.3, random_state=0).split(X.values, y, g))
    t = DecisionTreeRegressor(max_depth=2, random_state=0).fit(X.values[tr], y[tr]); T = t.tree_
    print("tree2: test MAE %.2f" % mae(y[te], t.predict(X.values[te])), "n", T.n_node_samples, "val", T.value.ravel().round(1),
          "thr", T.threshold.round(3), "feat", [list(X.columns)[i] if i >= 0 else "-" for i in T.feature], "age thr days", np.exp(T.threshold[[0, 1]]).round(1))
    # node ids: 0 root (log_age<=2.29), 1 left (log_age<=1.52), 2,3 leaves, 4 right (cement<=271), 5,6 leaves
    fig, ax = canvas(5.6, 2.75)
    def q(x, yq, txt, n):
        box(ax, x - 0.95, yq - 0.25, 1.9, 0.5, NAVY); ax.text(x, yq + 0.05, txt, ha="center", va="center", fontsize=9.2, color=NAVY, fontweight="bold")
        ax.text(x, yq - 0.15, f"n = {n}", ha="center", va="center", fontsize=8.6, color=GREY, **LAT)
    def leaf(x, yl, n, v, col):
        box(ax, x - 0.6, yl - 0.32, 1.2, 0.64, col)
        ax.text(x, yl + 0.12, f"{v:.1f} MPa", ha="center", va="center", fontsize=9.6, color=col, fontweight="bold", **LAT)
        ax.text(x, yl - 0.15, f"n = {n}", ha="center", va="center", fontsize=8.6, color="#4A5568", **LAT)
    a_thr = np.exp(T.threshold[0]); c_thr = T.threshold[4]
    q(2.8, 2.4, "العمر 7 أيام أو أقل؟", T.n_node_samples[0])
    q(4.2, 1.45, "العمر 3 أيام؟", T.n_node_samples[1]); q(1.4, 1.45, "الإسمنت " + iso(f"{c_thr:.0f} kg/m³") + " أو أقل؟", T.n_node_samples[4])
    xs = {2: 4.85, 3: 3.55, 5: 2.05, 6: 0.75}
    cols = {2: GREY, 3: GOLD, 5: BLUE, 6: GREEN}
    for nid in (2, 3, 5, 6): leaf(xs[nid], 0.45, T.n_node_samples[nid], T.value.ravel()[nid], cols[nid])
    def edge(p, c, lab):
        arrow(ax, p, c, col=GREY, lw=1.2, head=9); ax.text((p[0] + c[0]) / 2 + (0.1 if c[0] > p[0] else -0.1), (p[1] + c[1]) / 2 + 0.03, lab, ha="left" if c[0] > p[0] else "right", va="center", fontsize=8.8, color=GREEN if lab == "نعم" else RED, fontweight="bold")
    edge((3.2, 2.14), (4.0, 1.71), "نعم"); edge((2.4, 2.14), (1.6, 1.71), "لا")
    edge((4.45, 1.19), (4.8, 0.78), "نعم"); edge((3.95, 1.19), (3.6, 0.78), "لا")
    edge((1.65, 1.19), (2.0, 0.78), "نعم"); edge((1.15, 1.19), (0.8, 0.78), "لا")
    ax.text(5.55, 2.65, "شجرة بعمق 2 من المثال 5.2", ha="right", va="top", fontsize=9.2, color=NAVY, fontweight="bold")
    ax.text(5.55, 2.4, "خطأ الاختبار " + iso(f"MAE = {mae(y[te], t.predict(X.values[te])):.2f} MPa"), ha="right", va="top", fontsize=8.8, color="#4A5568")
    ax.text(0.05, 2.65, "الورقة تتنبأ بمتوسط\nمقاومة عيّناتها", ha="left", va="top", fontsize=8.8, color="#4A5568", linespacing=1.1)
    save(fig, F + "nfig3_tree2.png")

# ================================================================ 5.x the 150 bridges of Example 5.3 (same generator and K-Means call as ch5.py)
if want("bridges"):
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    rng = np.random.default_rng(4)
    age = np.r_[rng.uniform(5, 20, 60), rng.uniform(25, 45, 50), rng.uniform(40, 60, 40)]
    cr = np.r_[rng.normal(8, 0.6, 60), rng.normal(6, 0.7, 50), rng.normal(4, 0.7, 40)].clip(1, 9)
    cl = np.r_[rng.normal(0.1, 0.03, 60), rng.normal(0.3, 0.06, 50), rng.normal(0.6, 0.1, 40)].clip(0.01)
    km = KMeans(3, n_init=10, random_state=0).fit(StandardScaler().fit_transform(np.c_[age, cr, cl]))
    info = []
    for c in range(3):
        s = km.labels_ == c; info.append((c, s.sum(), age[s].mean(), cr[s].mean(), cl[s].mean()))
    info.sort(key=lambda r: r[2]); print("bridges:", [(c, n, round(a), round(r, 1), round(x, 2)) for c, n, a, r, x in info])
    colmap = {info[0][0]: GREEN, info[1][0]: GOLD, info[2][0]: RED}
    act = ["مراقبة روتينية", "صيانة وقائية", "تقييم تفصيلي\nوإصلاح عاجل"]
    fig = plt.figure(figsize=(5.6, 2.85))
    ax = fig.add_axes([0.08, 0.15, 0.5, 0.8])
    for c, n, a_, r_, x_ in info:
        s = km.labels_ == c; ax.scatter(age[s], cr[s], s=8 + 70 * cl[s], color=colmap[c], alpha=0.65, edgecolor="white", lw=0.4)
    ax.set_xlabel("Age (years)", fontsize=9); ax.set_ylabel("Condition rating (1-9)", fontsize=9); ax.tick_params(labelsize=8.6)
    ax.set_xlim(0, 64); ax.set_ylim(1.5, 9.8)
    ax.text(63, 9.6, "مساحة النقطة = الكلوريد", ha="right", va="top", fontsize=8.6, color=GREY)
    cax = fig.add_axes([0.62, 0.02, 0.37, 0.96]); cax.set_xlim(0, 2.1); cax.set_ylim(0, 2.85); cax.axis("off")
    for i, (c, n, a_, r_, x_) in enumerate(info):
        y0 = 2.0 - i * 0.93; col = colmap[c]
        box(cax, 0.05, y0, 2.0, 0.8, col)
        cax.add_patch(Rectangle((1.95, y0), 0.1, 0.8, fc=col, ec="none"))
        cax.text(1.88, y0 + 0.62, iso(f"{n}") + " جسراً", ha="right", va="center", fontsize=9.4, color=col, fontweight="bold")
        cax.text(1.88, y0 + 0.36, "عمر " + iso(f"{a_:.0f}") + " سنة · تقييم " + iso(f"{r_:.1f}") + " · كلوريد " + iso(f"{x_:.2f}%"), ha="right", va="center", fontsize=8.6, color="#2D3748")
        cax.text(1.88, y0 + 0.12, "← " + act[i].replace("\n", " "), ha="right", va="center", fontsize=8.8, color=NAVY, fontweight="bold")
    save(fig, F + "nfig3_bridges.png")

# ================================================================ 6.1 model ranking of Example 6.1 (MAE from Table 5.2 and the example's text)
if want("ranking"):
    R = [("MLP (16,)", 6.19, ORANGE), ("MLP (64, 64)", 5.61, ORANGE), ("Linear / Ridge", 4.96, "#A0AEC0"), ("Random forest", 4.20, "#A0AEC0"),
         ("SVR", 3.47, "#A0AEC0"), ("XGBoost", 3.39, "#A0AEC0"), ("MLP (64, 64) + target scaling", 3.31, BLUE), ("GPR", 2.72, "#A0AEC0")]
    fig, ax = plt.subplots(figsize=(5.6, 2.9))
    for i, (nm, v, c) in enumerate(R):
        ax.barh(i, v, color=c, height=0.62); ax.text(v + 0.07, i, f"{v:.2f}", va="center", fontsize=8.8, **LAT)
    ax.set_yticks(range(len(R))); ax.set_yticklabels([r[0] for r in R], fontsize=8.8); ax.invert_yaxis()
    ax.set_xlim(0, 7.6); ax.set_xlabel("MAE (MPa), grouped 5-fold CV — lower is better", fontsize=9); ax.tick_params(axis="x", labelsize=8.6)
    ax.add_patch(FancyArrowPatch((5.75, 1.3), (4.0, 5.9), arrowstyle="-|>", mutation_scale=12, color=BLUE, lw=1.5, connectionstyle="arc3,rad=-0.35"))
    ax.text(5.55, 4.6, "تغيير واحد في الإعداد:\nتقييس المخرَج", ha="left", va="center", fontsize=9, color=BLUE, fontweight="bold", linespacing=1.1)
    ax.text(7.55, 7.0, "رمادي: نماذج الفصل 5 (الجدول 5.2)", ha="right", va="center", fontsize=8.6, color=GREY)
    fig.tight_layout(); save(fig, F + "nfig3_ranking.png")

# ================================================================ 7.4 Bayesian optimisation from the inside (same loop as ch7.py, Example 7.3)
if want("bo"):
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel as Ck
    from scipy.stats import norm
    rng = np.random.default_rng(3); lab = lambda w: 110 / 6.5**w * rng.normal(1, 0.03); obj = lambda f: -abs(f - 40)
    X = [0.35, 0.60]; Y = [obj(lab(x)) for x in X]; grid = np.linspace(0.3, 0.7, 401); snaps = {}
    for it in range(5):
        gp = GaussianProcessRegressor(Ck(10) * RBF(0.1) + WhiteKernel(0.5), normalize_y=True, random_state=0).fit(np.array(X)[:, None], Y)
        mu, sd = gp.predict(grid[:, None], return_std=True); best = max(Y); z = (mu - best) / (sd + 1e-9)
        ei = (mu - best) * norm.cdf(z) + sd * norm.pdf(z); xn = grid[ei.argmax()]
        if len(X) in (3, 6): snaps[len(X)] = (list(X), list(Y), mu, sd, ei, xn)
        X.append(xn); Y.append(obj(lab(xn)))
    print("BO snapshots:", {k: (np.round(v[0], 3).tolist(), round(v[5], 3)) for k, v in snaps.items()})
    fig, axs = plt.subplots(2, 2, figsize=(5.6, 3.7), sharex=True, gridspec_kw=dict(height_ratios=[1.6, 1], hspace=0.12, wspace=0.12))
    for j, n in enumerate((3, 6)):          # right column = after three mixes (read first)
        Xs, Ys, mu, sd, ei, xn = snaps[n]; a, b = axs[0, 1 - j], axs[1, 1 - j]
        a.fill_between(grid, mu - 2 * sd, mu + 2 * sd, color=TINT[BLUE], lw=0); a.plot(grid, mu, color=BLUE, lw=1.4)
        a.plot(grid, -np.abs(110 / 6.5**grid - 40), color="#2D3748", lw=0.9, ls=":")
        a.scatter(Xs, Ys, color=ORANGE, zorder=4, s=18)
        for k, (x_, y_) in enumerate(zip(Xs, Ys)): a.annotate(str(k + 1), (x_, y_), textcoords="offset points", xytext=(3, -9), fontsize=8.6, **LAT)
        a.axvline(xn, color=RED, ls="--", lw=1); b.axvline(xn, color=RED, ls="--", lw=1)
        b.fill_between(grid, 0, ei, color=TINT[GREEN], lw=0); b.plot(grid, ei, color=GREEN, lw=1.4)
        a.set_ylim(-26, 6); b.set_ylim(0, 3.4); a.tick_params(labelsize=8.6); b.tick_params(labelsize=8.6)
        b.set_xlabel("w/b", fontsize=9)
        ttl = "بعد 3 خلطات: الاستكشاف" if n == 3 else "بعد 6 خلطات: الاستغلال"
        a.set_title(ttl, fontsize=9.6, pad=3)
        b.text(xn + (-0.008 if n == 3 else 0.008), 3.1, f"التالية {xn:.3f}", ha="right" if n == 3 else "left", va="center", fontsize=8.6, color=RED)
        if j == 0: a.set_yticklabels([]); b.set_yticklabels([])
    axs[0, 0].set_ylabel(iso("−|f − 40|") + " (MPa)", fontsize=9); axs[1, 0].set_ylabel("EI", fontsize=9, **LAT)
    fig.text(0.5, -0.05, "أزرق: متوسط " + iso("GPR ± 2σ") + " · منقّط: الهدف الحقيقي · برتقالي: الخلطات المقيسة · أحمر: الخلطة التالية", ha="center", va="top", fontsize=8.6, color="#4A5568")
    save(fig, F + "nfig3_bo.png")

# ================================================================ 7.5 the bridge maintenance MDP of Example 7.4
if want("mdp"):
    fig, ax = canvas(5.6, 2.95)
    xs = [5.0, 3.95, 2.9, 1.85, 0.8]; yc = 1.45; R0 = 0.3
    cols = ["#2F855A", "#68A04B", GOLD, "#DD6B20", RED]
    for i, x in enumerate(xs):
        ax.add_patch(Circle((x, yc), R0, fc=TINT.get(cols[i], "#FFFAF0") if cols[i] in TINT else "#F7FAF0", ec=cols[i], lw=3.0 if i >= 3 else 1.4, zorder=3))
        ax.text(x, yc + 0.04, str(i + 1), ha="center", va="center", fontsize=12, color=cols[i], fontweight="bold", zorder=4, **LAT)
        # self loop (stay)
        ax.add_patch(Arc((x, yc + R0 + 0.12), 0.32, 0.34, theta1=-40, theta2=220, color=GREY, lw=1.0))
        ax.text(x, yc + R0 + 0.33, "1.0" if i == 4 else "0.8", ha="center", va="bottom", fontsize=8.6, color="#4A5568", **LAT)
        if i < 4:
            arrow(ax, (x - R0 - 0.02, yc), (xs[i + 1] + R0 + 0.02, yc), col=GREY, lw=1.2, head=10)
            ax.text((x + xs[i + 1]) / 2, yc + 0.08, "0.2", ha="center", va="bottom", fontsize=8.6, color="#4A5568", **LAT)
    ax.text(5.0, yc - 0.6, "جيدة", ha="center", va="top", fontsize=8.8, color=cols[0]); ax.text(0.8, yc - 0.6, "فشل وظيفي", ha="center", va="top", fontsize=8.8, color=RED)
    ax.text(0.8, yc - 0.88, iso("500") + " لكل سنة", ha="center", va="top", fontsize=8.8, color=RED, fontweight="bold")
    # repair: back two states
    for i in (3, 4):
        ax.add_patch(FancyArrowPatch((xs[i] + 0.1, yc - R0), (xs[i - 2] - 0.1, yc - R0), arrowstyle="-|>", mutation_scale=11, color=BLUE, lw=1.4, connectionstyle="arc3,rad=0.42"))
    ax.text(2.9, 0.4, "إصلاح: " + iso("20") + " (درجتان إلى الخلف)", ha="center", va="center", fontsize=8.8, color=BLUE, fontweight="bold")
    # replace: dashed to state 1 (drawn above)
    ax.add_patch(FancyArrowPatch((xs[4] - 0.05, yc + R0 + 0.62), (xs[0] + 0.02, yc + R0 + 0.62), arrowstyle="-|>", mutation_scale=11, color=GREY, lw=1.1, ls="--", connectionstyle="arc3,rad=-0.1"))
    ax.text(2.9, 2.83, "استبدال: " + iso("100") + " (من أي حالة إلى 1)", ha="center", va="center", fontsize=8.8, color="#4A5568")
    ax.text(5.55, 0.02, "الإطار السميك: الحالات التي تختار فيها السياسة المثلى الإصلاح", ha="right", va="bottom", fontsize=8.6, color=NAVY)
    save(fig, F + "nfig3_mdp.png")

# ================================================================ 12.4 pixel size against the crack-width limit (Section 12.5, Table 12.2 and ex_b.py output)
if want("pixel"):
    fig = plt.figure(figsize=(5.6, 4.3))
    W = 1.0; x0 = 0.43; wc = 0.10
    for j, (px, lab) in enumerate([(0.25, "بكسل " + iso("0.25 mm") + ":\nالشق أصغر من البكسل"), (0.10, "بكسل " + iso("0.10 mm") + ":\nالشق بكسل واحد"), (0.025, "بكسل " + iso("0.025 mm") + ":\nالشق أربعة بكسلات")]):
        a = fig.add_axes([0.71 - j * 0.32, 0.575, 0.25, 0.345]); n = int(round(W / px))
        cov = np.zeros((n, n))
        for i in range(n):
            lo, hi = i * px, (i + 1) * px; cov[:, i] = max(0, min(hi, x0 + wc) - max(lo, x0)) / px
        a.imshow(1 - 0.85 * cov, cmap="gray", vmin=0, vmax=1, extent=[0, W, 0, W], origin="lower", interpolation="nearest")
        if n <= 40:
            for g_ in np.arange(0, W + 1e-9, px): a.axvline(g_, color="#A0AEC0", lw=0.35 if n > 12 else 0.6); a.axhline(g_, color="#A0AEC0", lw=0.35 if n > 12 else 0.6)
        a.add_patch(Rectangle((x0, 0), wc, W, fc="none", ec=RED, lw=1.0, ls="--"))
        a.set_xticks([]); a.set_yticks([]); a.set_xlabel(lab, fontsize=8.8, linespacing=1.1)
    fig.text(0.97, 0.965, "(أ) شق عرضه " + iso("0.10 mm") + " (حد منشآت حجز المياه) كما تراه الكاميرا في نافذة " + iso("1 × 1 mm"), ha="right", va="center", fontsize=9, color=NAVY, fontweight="bold")
    b = fig.add_axes([0.1, 0.075, 0.86, 0.265])
    r = [1.0, 0.5, 0.33, 0.25, 0.125]; wa = [17.3, 2.0, 1.0, 2.2, 2.8]; wn = [43, 7, 4, 7, 9]
    b.plot(r, wn, "s-", color=RED, lw=1.4, ms=4, label="near the limit"); b.plot(r, wa, "o-", color=BLUE, lw=1.4, ms=4, label="all cracks")
    for x_, v in zip(r, wn): b.text(x_ - (0.02 if x_ == 0.25 else 0), v + 3, f"{v}", ha="left" if x_ == 0.25 else "center", va="bottom", fontsize=8.6, color=RED, **LAT)   # the label at 0.25 sits right of the green rule
    b.text(1.0, 17.3 - 3, "17.3", ha="center", va="top", fontsize=8.6, color=BLUE, **LAT)
    b.axvline(0.25, color=GREEN, ls="--", lw=1); b.text(0.237, 52, "القاعدة العملية:\nبكسل ≈ ربع الحد", ha="left", va="top", fontsize=8.8, color=GREEN, fontweight="bold", linespacing=1.1)
    b.invert_xaxis(); b.set_xlim(1.05, 0.08); b.set_ylim(0, 55)
    b.set_xlabel("pixel size / width limit", fontsize=9); b.set_ylabel("wrong verdicts (%)", fontsize=9); b.tick_params(labelsize=8.6)
    b.legend(frameon=False, fontsize=8.6, loc="upper center", bbox_to_anchor=(0.5, 1.02))
    fig.text(0.97, 0.385, "(ب) نسبة الأحكام الخاطئة «هل يتجاوز الحد؟» على " + iso("600") + " شريط " + iso("(ex_b.py)"), ha="right", va="center", fontsize=9, color=NAVY, fontweight="bold")
    save(fig, F + "nfig3_pixel.png")

# ================================================================ 16.3 the Kalman loop of Example 16.3 (Q, R from the example; steady-state K computed)
if want("kalman"):
    Q, Rn, P = 0.002**2, 0.003**2, 0.02**2
    for _ in range(300): Pp = P + Q; Kg = Pp / (Pp + Rn); P = (1 - Kg) * Pp
    print("kalman: steady K = %.2f, posterior sd = %.4f" % (Kg, np.sqrt(P)))
    fig, ax = canvas(4.0, 3.15); cx, cy, rr = 2.0, 1.52, 1.05
    st = [(90, "تقدير الشهر السابق", iso("m , P"), NAVY), (0, "تنبؤ", iso("P + Q"), BLUE), (-90, "قياس جديد", iso("z") + " من التردد", ORANGE), (180, "الكسب", iso("K = P/(P + R)"), GREEN)]
    pos = {}
    for ang, t1, t2, c in st:
        x, y = cx + rr * 1.25 * np.cos(np.radians(ang)), cy + rr * np.sin(np.radians(ang)); pos[ang] = (x, y)
        box(ax, x - 0.62, y - 0.27, 1.24, 0.54, c); ax.text(x, y + 0.1, t1, ha="center", va="center", fontsize=9.2, color=c, fontweight="bold")
        ax.text(x, y - 0.13, t2, ha="center", va="center", fontsize=8.8, color="#2D3748")
    # loop arrows clockwise in reading order: top -> right -> bottom -> left -> top (update)
    def arc_(a, b, rad): ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=11, color=GREY, lw=1.3, connectionstyle=f"arc3,rad={rad}"))
    arc_((pos[90][0] + 0.64, pos[90][1]), (pos[0][0], pos[0][1] + 0.29), -0.35)
    arc_((pos[0][0], pos[0][1] - 0.29), (pos[-90][0] + 0.64, pos[-90][1]), -0.35)
    arc_((pos[-90][0] - 0.64, pos[-90][1]), (pos[180][0], pos[180][1] - 0.29), -0.35)
    arc_((pos[180][0], pos[180][1] + 0.29), (pos[90][0] - 0.64, pos[90][1]), -0.35)
    ax.text(0.55, 2.62, "تحديث:\n" + iso("m ← m + K(z − m)"), ha="center", va="center", fontsize=8.6, color=NAVY, linespacing=1.15)
    ax.text(cx, cy + 0.17, iso("Q = 0.002²   R = 0.003²"), ha="center", va="center", fontsize=8.6, color="#4A5568")
    ax.text(cx, cy - 0.12, "الكسب يستقر عند " + iso(f"K ≈ {Kg:.2f}"), ha="center", va="center", fontsize=8.8, color=GREEN, fontweight="bold")
    ax.text(cx, cy - 0.36, "والانحراف المعياري عند " + iso(f"{np.sqrt(P):.4f}"), ha="center", va="center", fontsize=8.6, color="#4A5568")
    save(fig, F + "nfig3_kalman.png")

# ================================================================ 17.2 word match against character n-grams (settings of Section 17.4)
if want("ngrams"):
    from sklearn.feature_extraction.text import CountVectorizer
    def norm_ar(s):
        s = re.sub(r"[ً-ْـ]", "", s); s = re.sub("[إأآا]", "ا", s); return s.replace("ى", "ي").replace("ة", "ه")
    an = CountVectorizer(analyzer="char_wb", ngram_range=(2, 4)).build_analyzer()
    w1, w2 = "الحفريات", "الحفرة"; g1, g2 = an(w1), an(w2); sh = set(g1) & set(g2)
    print("ngrams:", len(set(g1)), len(set(g2)), "shared", len(sh))
    fig, ax = canvas(5.6, 3.35)
    # top line: word matching
    ax.text(5.55, 3.18, "مطابقة الكلمات", ha="right", va="center", fontsize=9.6, color=NAVY, fontweight="bold")
    for x, w in ((3.6, w1), (1.9, w2)):
        box(ax, x - 0.5, 2.73, 1.0, 0.36, GREY); ax.text(x, 2.91, w, ha="center", va="center", fontsize=10, color="#2D3748")
    ax.text(2.75, 2.91, "≠", ha="center", va="center", fontsize=14, color=RED, **LAT)
    ax.text(0.95, 2.91, "المشترك: 0", ha="center", va="center", fontsize=9.4, color=RED, fontweight="bold")
    ax.plot([0.05, 5.55], [2.55, 2.55], color="#E2E8F0", lw=0.9)
    ax.text(5.55, 2.4, "مقاطع الحروف 2–4", ha="right", va="center", fontsize=9.6, color=NAVY, fontweight="bold")
    ax.text(5.55, 2.16, "(القوسان ⌊ ⌋ حدّا الكلمة)", ha="right", va="center", fontsize=8.6, color=GREY)
    def show(g):
        return g.replace(" ", "⌊") if g.startswith(" ") else (g.replace(" ", "⌋") if g.endswith(" ") else g)
    def chips(word, grams, xr, wdt):
        ax.text(xr - wdt / 2, 1.96, word + f"  ({len(set(grams))} مقطعاً)", ha="center", va="center", fontsize=9.6, color=NAVY, fontweight="bold")
        for r, n in enumerate((2, 3, 4)):
            gs = [g for g in grams if len(g) == n]; cw = wdt / 9; y = 1.55 - r * 0.47
            for i, gm in enumerate(gs):
                x = xr - (i + 0.5) * cw; s = gm in sh; c = BLUE if s else GREY
                ax.add_patch(FancyBboxPatch((x - cw / 2 + 0.02, y - 0.17), cw - 0.04, 0.34, boxstyle="round,pad=0,rounding_size=0.05", fc=TINT[BLUE] if s else "#F7FAFC", ec=c, lw=1.2 if s else 0.7))
                ax.text(x, y, show(gm), ha="center", va="center", fontsize=9 if n < 4 else 8.6, color=NAVY if s else "#718096", fontweight="bold" if s else "normal")
    chips(w1, g1, 5.55, 3.05); chips(w2, g2, 2.35, 2.3)
    ax.text(2.8, 0.2, f"المشترك: {len(sh)} مقطعاً (أزرق)", ha="center", va="center", fontsize=9.6, color=BLUE, fontweight="bold")
    save(fig, F + "nfig3_ngrams.png")
print("done")
