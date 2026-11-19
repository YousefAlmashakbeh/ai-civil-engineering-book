import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.ensemble import HistGradientBoostingRegressor, HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split, GroupShuffleSplit
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import brier_score_loss
from ch5_data import make_concrete

# ---------------- Part 1: how much does one number depend on the seed? ----------------
df = make_concrete()
X = df[["cement", "slag", "flyash", "water", "sp", "coarse", "fine", "age"]].values; y = df["fc"].values; g = df["mix"].values
rand, grp = [], []
for s in range(30):
    tr, te = train_test_split(np.arange(len(y)), test_size=0.2, random_state=s)
    m = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, random_state=s).fit(X[tr], y[tr])
    rand.append(np.mean(np.abs(m.predict(X[te]) - y[te])))
    tr, te = next(GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=s).split(X, y, g))
    m = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, random_state=s).fit(X[tr], y[tr])
    grp.append(np.mean(np.abs(m.predict(X[te]) - y[te])))
rand, grp = np.array(rand), np.array(grp)
print("Part1 GBM on concrete twin, 30 seeds (MAE, MPa):")
for name, a in [("random split", rand), ("split by mix", grp)]:
    print("  %-13s min=%.2f median=%.2f max=%.2f mean=%.2f sd=%.2f" % (name, a.min(), np.median(a), a.max(), a.mean(), a.std(ddof=1)))
print("  'best seed' random split vs honest median by mix: %.2f vs %.2f MPa (optimism %.0f%%)" %
      (rand.min(), np.median(grp), 100 * (1 - rand.min() / np.median(grp))))

fig, ax = plt.subplots(figsize=(6.5, 3.5))
bins = np.linspace(min(rand.min(), grp.min()) - 0.1, max(rand.max(), grp.max()) + 0.1, 22)
ax.hist(rand, bins=bins, alpha=0.6, color="#C05621", label="Random split (leaky)")
ax.hist(grp, bins=bins, histtype="step", lw=2, color="#2B6CB0", label="Split by mix (honest)")   # outline: no third colour where the two overlap
ax.axvline(rand.min(), color="#C05621", ls="--", lw=1); ax.text(rand.min(), ax.get_ylim()[1] * 0.9, " best seed", color="#C05621", fontsize=8)
ax.set_xlabel("Test MAE (MPa)"); ax.set_ylabel("Number of seeds (of 30)"); ax.legend(fontsize=8)
plt.tight_layout(); plt.savefig("fig/fig18_1_seeds.png", dpi=150); plt.close()

# ---------------- Part 2: calibration of failure probabilities ----------------
r = np.random.default_rng(18)
def slopes(n):
    beta = r.uniform(15, 38, n); c = r.uniform(5, 18, n); phi = r.uniform(30, 40, n); m = r.uniform(0, 1, n)
    z, gam, gw = 3.0, 19.0, 9.81
    b = np.radians(beta); p = np.radians(phi)
    fs = (c + (gam - m * gw) * z * np.cos(b) ** 2 * np.tan(p)) / (gam * z * np.sin(b) * np.cos(b))
    fs_obs = fs * r.lognormal(0, 0.12, n)          # unmodelled variability
    return np.column_stack([beta, c, phi, m]), (fs_obs < 1).astype(int)
Xa, ya = slopes(6000); Xc, yc = slopes(3000); Xt, yt = slopes(6000)
print("Part2 slope failure rate: train=%.3f test=%.3f" % (ya.mean(), yt.mean()))
# common practice: rebalance classes by oversampling failures in training
pos = np.where(ya == 1)[0]; neg = np.where(ya == 0)[0]
idx = np.r_[neg, r.choice(pos, len(neg), replace=True)]
clf_bal = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, random_state=0).fit(Xa[idx], ya[idx])
clf_raw = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, random_state=0).fit(Xa, ya)
iso = IsotonicRegression(out_of_bounds="clip").fit(clf_bal.predict_proba(Xc)[:, 1], yc)
def ece(p, y, nb=10):
    e = 0; edges = np.linspace(0, 1, nb + 1)
    for a, b in zip(edges[:-1], edges[1:]):
        k = (p >= a) & (p < b) if b < 1 else (p >= a)
        if k.any(): e += k.mean() * abs(p[k].mean() - y[k].mean())
    return e
P = {"Rebalanced training": clf_bal.predict_proba(Xt)[:, 1], "Natural class ratio": clf_raw.predict_proba(Xt)[:, 1]}
P["Rebalanced + isotonic"] = iso.predict(P["Rebalanced training"])
for k, p in P.items():
    print("  %-22s Brier=%.4f  ECE=%.3f  mean predicted Pf=%.3f (observed %.3f)  slopes flagged p>0.5: %d (true failures among them %d)" %
          (k, brier_score_loss(yt, p), ece(p, yt), p.mean(), yt.mean(), (p > 0.5).sum(), yt[p > 0.5].sum()))
fig, ax = plt.subplots(figsize=(5, 4.2))
edges = np.linspace(0, 1, 11)
for (k, p), col, mk in zip(P.items(), ["#C53030", "#2F855A", "#2B6CB0"], ["o", "s", "^"]):
    xs, ys = [], []
    for a, b in zip(edges[:-1], edges[1:]):
        sel = (p >= a) & (p < b) if b < 1 else (p >= a)
        if sel.sum() >= 20: xs.append(p[sel].mean()); ys.append(yt[sel].mean())
    ax.plot(xs, ys, marker=mk, color=col, label=k)
ax.plot([0, 1], [0, 1], "k--", lw=0.8, label="Perfect calibration")
ax.set_xlabel("Predicted failure probability"); ax.set_ylabel("Observed failure frequency"); ax.legend(fontsize=7)
plt.tight_layout(); plt.savefig("fig/fig18_2_calibration.png", dpi=150); plt.close()
