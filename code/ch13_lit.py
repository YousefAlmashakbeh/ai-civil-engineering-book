# Chapter 13 literature case: reading a half-cell potential map with the ASTM C876 limits (CSE electrode)
# > -200 mV: >90 % probability of no active corrosion; -200..-350 mV: uncertain; < -350 mV: >90 % probability of active corrosion
# The deck map is GENERATED (teaching data): 20 x 8 grid at 0.6 m, two chloride-rich zones near drains, cover varies.
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
rng = np.random.default_rng(13)
nx, ny, s = 20, 8, 0.6
X, Y = np.meshgrid(np.arange(nx) * s, np.arange(ny) * s)
active = 0.9 * np.exp(-((X - 2.4)**2 + (Y - 3.6)**2) / 1.2) + 0.7 * np.exp(-((X - 9.0)**2 + (Y - 1.2)**2) / 0.8)
E = -150 - 330 * active + rng.normal(0, 25, X.shape)                      # mV vs CSE
E[5, 15] = -180 + 900                                                    # a sign/entry error: +720 mV is not physical
med = np.median(E); mad = np.median(np.abs(E - med)); z = 0.6745 * (E - med) / mad
bad = np.abs(z) > 3.5; print("robust z flags:", int(bad.sum()), "points; values (mV):", np.round(E[bad]).astype(int).tolist())
phys = (E > 200) | (E < -1000)                                            # outside the range steel in concrete can reach (CSE; dry concrete up to about +200 mV)
print("physical-range flags:", int(phys.sum()), "point; value:", np.round(E[phys]).astype(int).tolist())
print("robust-z flags that lie in the generated active zones:", int((bad & (active > 0.35)).sum()), "of", int(bad.sum()))
Ec = np.where(phys, np.nan, E)
cls = np.select([Ec > -200, Ec >= -350, Ec < -350], [0, 1, 2], -1)
n = np.isfinite(Ec).sum()
for k, nm in enumerate(["> -200 mV  (corrosion unlikely)", "-200..-350 (uncertain)", "< -350 mV  (corrosion likely)"]):
    print(f"{nm:34s}: {int((cls == k).sum()):3d} points ({(cls == k).sum() / n:.0%})")
true = active > 0.35
print("C876 '< -350' vs generated active zone: precision %.2f, recall %.2f" % ((true & (cls == 2)).sum() / (cls == 2).sum(), (true & (cls == 2)).sum() / true.sum()))
fig, ax = plt.subplots(1, 2, figsize=(9.6, 2.9), gridspec_kw={"width_ratios": [1.25, 1]})
im = ax[0].pcolormesh(X, Y, Ec, cmap="RdYlBu", vmin=-550, vmax=-50, shading="nearest"); fig.colorbar(im, ax=ax[0], label="E (mV vs CSE)")
ax[0].contour(X, Y, np.nan_to_num(Ec, nan=-150), levels=[-350, -200], colors="k", linewidths=[1.2, .8], linestyles=["-", "--"])
ax[0].plot(*np.argwhere(phys)[0][::-1] * s, "kx", ms=9); ax[0].set_title("Half-cell map (generated deck)", fontsize=9); ax[0].set_xlabel("x (m)"); ax[0].set_ylabel("y (m)")
ax[1].hist(Ec[np.isfinite(Ec)], bins=24, color="#4A5568"); [ax[1].axvline(v, color="k", ls=ls) for v, ls in ((-200, "--"), (-350, "-"))]
ax[1].set_xlabel("E (mV vs CSE)"); ax[1].set_ylabel("points"); ax[1].set_title("ASTM C876 limits", fontsize=9)
fig.tight_layout(); fig.savefig("fig/fig13_3_halfcell.png", dpi=200)
