# Chapter 8 literature case: bond of corroded bars
# Empirical model for pull-out specimens (Bhargava et al., 2008, rounded): R = 1 for X <= 1.5 %, R = 1.2 exp(-0.12 X) otherwise
# Stage boundaries reported by Almusallam et al. (1996): bond rises to ~4 % mass loss, drops sharply to ~6 %, then little change up to 80 %
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = lambda X: np.where(X <= 1.5, 1.0, 1.2 * np.exp(-0.12 * X))
for x in (1, 2, 4, 6, 10, 20): print(f"X = {x:>2} %  R = {float(R(np.array(x))):.2f}")
X = np.linspace(0, 25, 500)
fig, ax = plt.subplots(figsize=(6.4, 3.8))
ax.axvspan(0, 4, color="#C6F6D5", alpha=.6, label="Almusallam 1996: bond rises (pre-cracking)")
ax.axvspan(4, 6, color="#FED7D7", alpha=.8, label="sharp drop (cover splitting)")
ax.axvspan(6, 25, color="#E2E8F0", alpha=.6, label="little further change (to 80 %)")
ax.plot(X, R(X), "k-", lw=2, label="Bhargava et al. 2008 (pull-out, fitted to many studies)")
for x in (2, 4, 10): ax.plot(x, R(np.array(x)), "ko"); ax.annotate(f"{float(R(np.array(x))):.2f}", (x, R(np.array(x))), xytext=(4, 6), textcoords="offset points")
ax.set_xlabel("Corrosion level X (% mass loss)"); ax.set_ylabel("Relative bond strength R"); ax.set_ylim(0, 1.25); ax.set_xlim(0, 25)
ax.legend(fontsize=7.5, loc="upper right"); fig.tight_layout(); fig.savefig("fig/fig8_5_bond_lit.png", dpi=200)
