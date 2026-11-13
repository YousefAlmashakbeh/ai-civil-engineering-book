"""Author's own measurements (Al-Mashaqbeh, HU): UPV on corroding RC beams and bond pull-out on corroded prisms."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr, pearsonr

# ---------------- A. UPV transit times: 4 beams x 60 grid points x 3 ages, path 100 mm ----------------
u = pd.read_csv("author_data/upv_transit_times.csv")
L = 100.0  # mm, direct transmission across beam width
med = u.groupby(["day", "block"]).transit_us.transform("median")
mad = u.groupby(["day", "block"]).transit_us.transform(lambda s: np.median(np.abs(s - s.median())))
u["robust_z"] = 0.6745 * (u.transit_us - med) / mad.replace(0, np.nan)
u["outlier"] = u.robust_z.abs() > 3.5
u["V_kms"] = L / u.transit_us          # mm/us = km/s
print("A. UPV: %d readings; flagged outliers (|robust z|>3.5): %d (%.1f%%); max raw transit time %.1f us"
      % (len(u), u.outlier.sum(), 100 * u.outlier.mean(), u.transit_us.max()))
print("   example of a flagged entry:", u.loc[u.transit_us.idxmax(), ["day", "block", "row", "point", "transit_us"]].to_dict())
c = u[~u.outlier]
tab = c.groupby(["block", "day"]).V_kms.mean().unstack()
tab_raw = u.groupby(["block", "day"]).V_kms.mean().unstack()
print("   mean UPV (km/s) after removing outliers, rows = beam block, cols = days of accelerated corrosion:")
print(tab.round(2).to_string())
print("   change day0 -> day8 per block (%):", (100 * (tab[8] / tab[0] - 1)).round(1).to_dict())
print("   block 1 mean with vs without outliers at day 3: %.3f vs %.3f km/s" % (tab_raw.loc[1, 3], tab.loc[1, 3]))
cv = c.groupby(["block", "day"]).V_kms.agg(lambda s: 100 * s.std() / s.mean()).unstack()
print("   within-beam CoV of UPV (%):"); print(cv.round(1).to_string())

fig, ax = plt.subplots(1, 3, figsize=(11, 2.6))
vmin, vmax = c.V_kms.quantile(0.02), c.V_kms.quantile(0.98)
for a, d in zip(ax, [0, 3, 8]):
    g = u[(u.block == 1) & (u.day == d)].pivot(index="row", columns="point", values="V_kms")
    im = a.imshow(g.values, aspect="auto", cmap="viridis", vmin=vmin, vmax=vmax)
    a.set_title("Block 1, day %d" % d, fontsize=9); a.set_yticks(range(3)); a.set_yticklabels(g.index)
    a.set_xlabel("Grid point along beam (50 mm cells)")
fig.colorbar(im, ax=ax, label="UPV (km/s)", shrink=0.9)
plt.savefig("fig/figA_upv_grid.png", dpi=150, bbox_inches="tight"); plt.close()

# ---------------- B. Bond pull-out on corroded prisms ----------------
s = pd.read_csv("author_data/all_prisms_summary.csv", comment="#")
cw = pd.read_csv("author_data/crackwidth_all_prisms.csv")
print("B. Bond: %d prisms, %d with valid pull-out results" % (len(s), s.Pmax_kN.notna().sum()))
for wc, g in s.groupby("wc"):
    ctrl = g[g.corroded == 0].Pmax_kN.iloc[0]
    for _, r in g[g.corroded == 1].iterrows():
        print("   w/c %.2f %-7s crack %.1f mm  Pmax %s kN  ratio to control %s" %
              (wc, r.prism, r.max_crack_mm, "%.1f" % r.Pmax_kN if r.Pmax_kN == r.Pmax_kN else "  - ",
               "%.2f" % (r.Pmax_kN / ctrl) if r.Pmax_kN == r.Pmax_kN else "failed during installation"))
v = s[(s.corroded == 1) & s.Pmax_kN.notna()]
rho, p = spearmanr(v.max_crack_mm, v.Pmax_kN)
print("   corroded prisms with results: n=%d; Spearman(crack width, Pmax)=%.2f (p=%.2f)" % (len(v), rho, p))
cor = s[s.corroded == 1]
rd, pd_ = spearmanr(cor.EGCI_pct, cor.max_crack_mm)
print("   inhibitor dose vs max corrosion crack width, all 8 corroded prisms: Spearman=%.2f (p=%.3f)" % (rd, pd_))
k = cw[cw.n == 3].copy(); k["ml"] = pd.to_numeric(k["mass_loss_%"], errors="coerce")
kk = k.dropna(subset=["ml"])
r, pr = pearsonr(kk["max_crack_width_mm (thesis Fig 4.11-4.12)"], kk.ml)
print("   crack width vs inferred mass loss (FE inversion, n=3 rust ratio): r=%.3f over %d prisms (by construction of the inversion)" % (r, len(kk)))

fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
for f, lab in [("curve_p0-3-c_smoothed.csv", "PN0-3 (control)"), ("curve_p20-3-c_smoothed.csv", "PC20-3"),
               ("curve_p30-3-c_smoothed.csv", "PC30-3"), ("curve_p40-3-c_smoothed.csv", "PC40-3")]:
    d = pd.read_csv("author_data/" + f)
    ax[0].plot(d.slip_mm, d.load_kN, marker=".", label=lab)
ax[0].set_xlabel("Slip (mm)"); ax[0].set_ylabel("Pull-out load (kN)"); ax[0].set_title("w/c 0.38, smoothed curves", fontsize=9)
ax[0].legend(fontsize=7)
ok = s[s.Pmax_kN.notna()]
cols = ["tab:gray" if c0 == 0 else "tab:red" for c0 in ok.corroded]
ax[1].scatter(ok.max_crack_mm, ok.Pmax_kN, c=cols, s=40)
for _, r0 in ok.iterrows(): ax[1].annotate(r0.prism, (r0.max_crack_mm, r0.Pmax_kN), fontsize=7, xytext=(3, 3), textcoords="offset points")
ax[1].set_xlabel("Max corrosion crack width before test (mm)"); ax[1].set_ylabel("Peak pull-out load (kN)")
ax[1].set_title("8 prisms with valid tests (grey = control)", fontsize=9)
plt.tight_layout(); plt.savefig("fig/figB_bond.png", dpi=150); plt.close()
