"""Shear-wave dispersion: Kelvin-Voigt vs fractional (spring-pot) model, classical inversion vs learned (amortised) inversion."""
import numpy as np, time, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
from sklearn.ensemble import HistGradientBoostingRegressor

rho = 1000.0
f = np.linspace(100, 1000, 19); w = 2 * np.pi * f
def G_fd(mu, eta, a):            # KVFD / spring-pot in parallel with spring: G* = mu + eta (i w)^a
    return mu + eta * (1j * w) ** a
def c_phase(G):                  # phase velocity of a plane shear wave in a viscoelastic medium
    return np.sqrt(2 * np.abs(G) ** 2 / (rho * (G.real + np.abs(G))))
rng = np.random.default_rng(1313)
true = dict(mu=4000.0, eta=25.0, a=0.35)
c_true = c_phase(G_fd(**true))
c_obs = c_true * (1 + rng.normal(0, 0.02, len(f)))

# 1) classical inverse problem: fit KV (a = 1) and KVFD (a free) by least squares
def fit(model, c):
    if model == "KV":
        r = lambda p: c_phase(G_fd(p[0], p[1], 1.0)) - c
        s = least_squares(r, [3000, 1.0], bounds=([100, 1e-4], [1e5, 1e3]))
        return s.x, s.fun
    r = lambda p: c_phase(G_fd(p[0], p[1], p[2])) - c
    s = least_squares(r, [3000, 10, 0.5], bounds=([100, 1e-3, 0.01], [1e5, 1e4, 1.0]))
    return s.x, s.fun
n = len(f)
for m in ["KV", "KVFD"]:
    p, res = fit(m, c_obs); k = len(p); rss = np.sum(res ** 2)
    aic = n * np.log(rss / n) + 2 * k
    print("%-4s params=%s  RMS misfit=%.3f m/s  AIC=%.1f" % (m, np.round(p, 3), np.sqrt(rss / n), aic))
# extrapolation to 2 kHz
f2 = np.array([1500.0, 2000.0]); w2 = 2 * np.pi * f2
pk, _ = fit("KV", c_obs); pf, _ = fit("KVFD", c_obs)
def c_at(mu, eta, a, ww): G = mu + eta * (1j * ww) ** a; return np.sqrt(2 * np.abs(G) ** 2 / (rho * (G.real + np.abs(G))))
ct = c_at(true["mu"], true["eta"], true["a"], w2)
print("extrapolation to 1.5/2 kHz: true %s  KV %s  KVFD %s m/s" % (np.round(ct, 2), np.round(c_at(pk[0], pk[1], 1.0, w2), 2), np.round(c_at(*pf, w2), 2)))

# 2) learned (amortised) inversion: train GBM on simulated curves -> parameters
N = 4000
mu_s = rng.uniform(1000, 10000, N); eta_s = 10 ** rng.uniform(0, 2, N); a_s = rng.uniform(0.1, 0.9, N)
X = np.array([c_phase(G_fd(m_, e_, a_)) * (1 + rng.normal(0, 0.02, n)) for m_, e_, a_ in zip(mu_s, eta_s, a_s)])
feat = lambda X: np.column_stack([X, np.log(X[:, -1] / X[:, 0])])
Y = np.column_stack([np.log(mu_s), np.log(eta_s), a_s])
tr, te = slice(0, 3600), slice(3600, N)
models = [HistGradientBoostingRegressor(max_iter=400, learning_rate=0.05, random_state=j).fit(feat(X[tr]), Y[tr, j]) for j in range(3)]
t0 = time.time(); P = np.column_stack([m_.predict(feat(X[te])) for m_ in models]); t_ml = time.time() - t0
t0 = time.time(); LS = np.array([fit("KVFD", x)[0] for x in X[te]]); t_ls = time.time() - t0
mu_t, a_t = mu_s[te], a_s[te]
def stats(name, mu_hat, a_hat, t):
    e_mu = 100 * np.median(np.abs(mu_hat - mu_t) / mu_t); e_a = np.median(np.abs(a_hat - a_t))
    print("%-22s median |err| mu=%.1f%%  alpha=%.3f   time for %d curves=%.2f s" % (name, e_mu, e_a, len(mu_t), t))
    return e_mu, e_a
stats("Least squares (KVFD)", LS[:, 0], LS[:, 2], t_ls)
stats("Learned inversion (GBM)", np.exp(P[:, 0]), P[:, 2], t_ml)
# shear modulus of a concrete-like solid: same physics, different scale
for name, rho_c, vs in [("young concrete (6 h)", 2350, 600), ("concrete (28 d)", 2400, 2500), ("stiff clay", 1900, 250)]:
    print("  G = rho Vs^2 for %-22s Vs=%5d m/s -> G=%.2f GPa" % (name, vs, rho_c * vs ** 2 / 1e9))

fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.4))
ff = np.linspace(100, 2000, 200); ww = 2 * np.pi * ff
ax[0].scatter(f, c_obs, color="k", s=15, label="Measured (synthetic, 2% noise)")
ax[0].plot(ff, c_at(true["mu"], true["eta"], true["a"], ww), "k", lw=1, label="True (spring-pot, a=0.35)")
ax[0].plot(ff, c_at(pk[0], pk[1], 1.0, ww), "--", color="#C53030", label="Kelvin-Voigt fit")
ax[0].plot(ff, c_at(*pf, ww), ":", color="#2B6CB0", lw=2, label="KVFD fit")
ax[0].axvspan(1000, 2000, color="0.9"); _y0, _y1 = ax[0].get_ylim(); ax[0].text(1500, _y0 + 0.08 * (_y1 - _y0), "extrapolation", ha="center", fontsize=8, color="#4A5568")
ax[0].set_xlabel("Frequency (Hz)"); ax[0].set_ylabel("phase velocity (m/s)"); ax[0].legend(fontsize=7.5, loc="upper left")
ax[1].scatter(a_t, LS[:, 2], s=10, marker="x", linewidths=.7, alpha=.55, color="#C05621", label="least squares")
ax[1].scatter(a_t, P[:, 2], s=8, marker="o", alpha=.5, color="#2B6CB0", label="learned (GBM)")
ax[1].plot([0.1, 0.9], [0.1, 0.9], "k--", lw=0.8)
ax[1].set_xlabel(r"true fractional order $\alpha$"); ax[1].set_ylabel(r"estimated $\alpha$"); ax[1].legend(fontsize=7.5, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
ax[1].annotate("stuck at bound", xy=(0.75, 0.0), xytext=(0.55, 0.25), fontsize=7.5, arrowprops=dict(arrowstyle="->", lw=.7))
ax[1].annotate("stuck at bound", xy=(0.3, 1.0), xytext=(0.12, 0.72), fontsize=7.5, arrowprops=dict(arrowstyle="->", lw=.7))
plt.tight_layout(); plt.savefig("fig/fig13_4_elasto.png", dpi=260); plt.close()
