"""Worked hybrid example (Ch 16): SCS-CN runoff + GBM on the residuals, inside and outside the training range. Synthetic teaching case."""
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingRegressor
rng = np.random.default_rng(16)
def scs(P, CN):
    S = 25400/CN - 254; Ia = 0.2*S
    return np.where(P > Ia, (P - Ia)**2/(P - Ia + S), 0.0)
n = 1500; P = rng.uniform(5, 120, n); CN = rng.uniform(65, 90, n); amc = rng.uniform(0, 1, n)   # antecedent moisture index
CN_eff = np.clip(CN + 8*(amc - 0.5), 40, 98)                       # wet soil behaves like a higher CN (not in the textbook formula)
Q = scs(P, CN_eff) + rng.normal(0, 1.0, n); Q = np.clip(Q, 0, None)
tr = P <= 60; te_in = rng.random(n) < 0.25; tr_in = tr & ~te_in; inside = tr & te_in; outside = P > 60
X = np.c_[P, CN, amc]; phys = scs(P, CN)
gbm = GradientBoostingRegressor(random_state=0).fit(X[tr_in], Q[tr_in])
res = GradientBoostingRegressor(random_state=0).fit(X[tr_in], (Q - phys)[tr_in])
pred = {"physics (SCS-CN)": phys, "GBM only": gbm.predict(X), "hybrid (SCS-CN + GBM residual)": phys + res.predict(X)}
print(f"Hybrid example: train storms P<=60 mm (n={tr_in.sum()}), test inside (n={inside.sum()}), test outside P>60 mm (n={outside.sum()})")
for k, p in pred.items():
    print(f"  {k:32s} MAE inside={np.abs(p-Q)[inside].mean():.2f} mm   outside={np.abs(p-Q)[outside].mean():.2f} mm   bias outside={np.mean(p-Q)[()] if False else (p-Q)[outside].mean():+.2f} mm")
fig, ax = plt.subplots(figsize=(7, 3.6)); o = np.argsort(P); m = np.abs(CN - 78) < 3
sty = {"physics (SCS-CN)": dict(marker="s", s=8), "GBM only": dict(marker="x", s=12, linewidths=0.8), "hybrid (SCS-CN + GBM residual)": dict(marker="o", s=6, facecolors="none", linewidths=0.7)}   # markers keep the models apart in greyscale
for k, c in zip(pred, ["#718096", "#c53030", "#2b6cb0"]):
    kw = dict(sty[k]); kw.update(dict(edgecolors=c) if "facecolors" in kw else dict(color=c))
    ax.scatter(P[m], pred[k][m], label=k, alpha=.6, **kw)
ax.scatter(P[m], Q[m], s=4, marker=".", color="k", label="observed", alpha=.5); ax.axvline(60, ls="--", c="k", lw=.8); ax.text(62, 2, "outside training range", fontsize=8)
ax.set_xlabel("Storm depth P (mm)"); ax.set_ylabel("Runoff Q (mm), CN 75-81"); ax.legend(frameon=False, fontsize=7); ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig("fig/fig16_4_hybrid.png", dpi=200)
