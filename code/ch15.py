import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.ensemble import HistGradientBoostingRegressor, IsolationForest
from sklearn.linear_model import LinearRegression
from scipy.optimize import minimize_scalar

# ---------------- Part 1: daily urban water demand ----------------
rng = np.random.default_rng(15)
d = pd.date_range("2022-01-01", "2025-12-31", freq="D")
doy = d.dayofyear.values; yr = d.year.values
T = 19 + 9 * np.sin(2 * np.pi * (doy - 110) / 365) + rng.normal(0, 2.0, len(d))
# heatwave in test year beyond anything seen in training
hw = (d >= "2025-08-05") & (d <= "2025-08-18")
T[hw] += 7
ram = np.zeros(len(d), bool)
for a, b in [("2022-04-02", "2022-05-01"), ("2023-03-23", "2023-04-20"), ("2024-03-11", "2024-04-09"), ("2025-03-01", "2025-03-29")]:
    ram |= (d >= a) & (d <= b)
fri = d.dayofweek.values == 4
demand = (100 * (1.02 ** (yr - 2022)) + 1.6 * (T - 20) + 0.12 * np.maximum(T - 28, 0) ** 2
          + 5 * ram - 6 * fri + rng.normal(0, 2.5, len(d)))       # thousand m3/day
X = pd.DataFrame({"T": T, "dow": d.dayofweek.values, "ram": ram.astype(int), "trend": (d - d[0]).days.values,
                  "T2": np.maximum(T - 28, 0) ** 2, "fri": fri.astype(int)})
tr = yr < 2025; te = ~tr
gb = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, random_state=0).fit(X[tr][["T", "dow", "ram", "trend"]], demand[tr])
lin = LinearRegression().fit(X[tr][["T", "T2", "fri", "ram", "trend"]], demand[tr])
pg = gb.predict(X[te][["T", "dow", "ram", "trend"]]); pl = lin.predict(X[te][["T", "T2", "fri", "ram", "trend"]])
yt = demand[te]; hwt = hw[te]
mae = lambda a, b: np.mean(np.abs(a - b))
print("Part1 demand: max T train=%.1f C, max T heatwave=%.1f C" % (T[tr].max(), T[hw].max()))
print("  test 2025 MAE (thousand m3/d): GBM=%.2f  physics-informed linear=%.2f" % (mae(yt, pg), mae(yt, pl)))
print("  heatwave MAE: GBM=%.2f  linear=%.2f ; heatwave mean demand=%.1f, GBM mean=%.1f, linear mean=%.1f" %
      (mae(yt[hwt], pg[hwt]), mae(yt[hwt], pl[hwt]), yt[hwt].mean(), pg[hwt].mean(), pl[hwt].mean()))
qs = {}
for a in (0.1, 0.9):
    m = HistGradientBoostingRegressor(loss="quantile", quantile=a, max_iter=300, learning_rate=0.05, random_state=0)
    m.fit(X[tr][["T", "dow", "ram", "trend"]], demand[tr]); qs[a] = m.predict(X[te][["T", "dow", "ram", "trend"]])
inside = (yt >= qs[0.1]) & (yt <= qs[0.9])
print("  GBM 10-90%% interval coverage: all 2025=%.0f%%  heatwave=%.0f%% (nominal 80%%)" % (100 * inside.mean(), 100 * inside[hwt].mean()))
fig, ax = plt.subplots(figsize=(5.0, 3.3))   # drawn at print width (12.6 cm): fonts >= 8.6 pt in print
w = (d[te] >= "2025-06-15") & (d[te] <= "2025-09-15")
dd = d[te][w]
ax.fill_between(dd, qs[0.1][w], qs[0.9][w], color="#2B6CB0", alpha=0.2, label="GBM 10-90% interval")
ax.plot(dd, yt[w], "k", lw=1.2, label="Observed")
ax.plot(dd, pg[w], color="#2B6CB0", lw=1, label="GBM")
ax.plot(dd, pl[w], color="#C53030", lw=1, ls="--", label="Linear with T and (T-28)+^2")
ax.axvspan(pd.Timestamp("2025-08-05"), pd.Timestamp("2025-08-18"), color="orange", alpha=0.15, label="Heatwave (unseen T)")
import matplotlib.dates as mdates
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=(1, 15))); ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
ax.set_ylabel("Demand (1000 m3/day)"); ax.legend(fontsize=8.6, ncol=2, loc="upper center", bbox_to_anchor=(0.45, -0.1)); ax.tick_params(axis="x", labelsize=8.6)
plt.tight_layout(); plt.savefig("fig/fig15_1_demand.png", dpi=260); plt.close()

# ---------------- Part 2: leak detection from minimum night flow ----------------
r2 = np.random.default_rng(152)
def dma(leak, size, start=60, ndays=120):
    base = r2.uniform(15, 30); trend = r2.normal(0, 0.003)
    mnf = base + trend * np.arange(ndays) + r2.normal(0, 0.9, ndays) + 1.5 * (r2.random(ndays) < 0.03)  # occasional night use
    if leak: mnf[start:] += size
    return mnf
def cusum(x, base_n=30, k=0.5, h=5.0):
    m, s = x[:base_n].mean(), x[:base_n].std(ddof=1)
    z = (x - m) / s; c = 0; al = []
    for i in range(base_n, len(x)):
        c = max(0, c + z[i] - k)
        if c > h: al.append(i); c = 0          # investigate, then reset
    return al
def shewhart(x, base_n=30):
    m, s = x[:base_n].mean(), x[:base_n].std(ddof=1)
    return [i for i in range(base_n, len(x)) if x[i] > m + 3 * s]
def iforest(x, base_n=30):
    feats = lambda v: np.column_stack([v, np.r_[v[0], v[:-1]], np.r_[v[:2], v[:-2]]])
    F = feats(x)
    mdl = IsolationForest(contamination=0.01, random_state=0).fit(F[2:base_n])
    lab = mdl.predict(F)
    return [i for i in range(base_n, len(x)) if lab[i] == -1 and lab[i - 1] == -1]
sizes = [1.0, 2.0, 3.0, 5.0]; N = 150
rows = []
for name, f in [("Shewhart 3-sigma", shewhart), ("CUSUM k=0.5,h=5", cusum), ("Isolation forest (2 days)", iforest)]:
    fa = np.mean([len(f(dma(False, 0))) for _ in range(N)]) / 3.0     # false alarms per DMA per month (90 monitored days)
    res = []
    for sz in sizes:
        det = []; delay = []
        for _ in range(N):
            al = [i for i in f(dma(True, sz)) if i >= 60]
            ok = len(al) > 0 and al[0] - 60 <= 30
            det.append(ok); delay.append(al[0] - 60 if ok else np.nan)
        res.append((np.mean(det), np.nanmedian(delay) if np.any(det) else np.nan))
    rows.append((name, fa, res))
print("Part2 leak detection (MNF noise sd 0.9 m3/h, 150 DMAs per case, detection within 30 days):")
for name, fa, res in rows:
    print("  %-26s false alarms/DMA/month=%.2f | " % (name, fa) +
          " ".join("leak %.0f: det %3.0f%% delay %s d" % (s, 100 * r[0], "%.0f" % r[1] if r[1] == r[1] else "-") for s, r in zip(sizes, res)))
fig = plt.figure(figsize=(7.2, 4.4)); gsp = fig.add_gridspec(2, 2, width_ratios=[1.25, 1])
a0 = fig.add_subplot(gsp[0, 0]); a2 = fig.add_subplot(gsp[1, 0], sharex=a0); a1 = fig.add_subplot(gsp[:, 1]); ax = [a0, a1]
r2 = np.random.default_rng(7)
x = dma(True, 2.0)
m, s = x[:30].mean(), x[:30].std(ddof=1); z = (x - m) / s; c = np.zeros(len(x))
for i in range(30, len(x)): c[i] = max(0, c[i - 1] + z[i] - 0.5)
a0.plot(x, "k", lw=1, label="min night flow")
a0.axhline(m + 3 * s, color="#C05621", ls="--", label="Shewhart limit")
for _a in (a0, a2): _a.axvline(60, color="#C53030", ls=":", lw=1.2)
a0.set_ylim(a0.get_ylim()[0] - 3.2, a0.get_ylim()[1])   # room under the data for the legend
a0.text(58, a0.get_ylim()[1], "leak starts\n(+2 m$^3$/h)", fontsize=8.6, va="top", ha="right", color="#C53030")   # left of the line, clear of the data
a0.set_ylabel("MNF (m$^3$/h)"); a0.legend(fontsize=8.6, loc="lower right"); plt.setp(a0.get_xticklabels(), visible=False)
a2.plot(c, color="#2B6CB0", lw=1.1, label="CUSUM"); a2.axhline(5, color="#2B6CB0", ls="--", lw=0.9)
a2.text(2, 14, "threshold h = 5", fontsize=8.6, va="bottom", color="#2B6CB0"); a2.set_ylabel("CUSUM"); a2.set_xlabel("day")   # label above the dashed line, clear of the curve
for (name, fa, res), mk, ls in zip(rows, ["o", "s", "^"], ["-", "--", "-."]):
    a1.plot(sizes, [100 * r[0] for r in res], marker=mk, ls=ls, label=name)
a1.set_xlabel("leak size (m$^3$/h)"); a1.set_ylabel("detected within 30 d (%)"); a1.set_xlim(0.7, 5.5); a1.set_ylim(42, 102); a1.set_xticks([1, 2, 3, 4, 5]); a1.legend(fontsize=8.6, loc="lower right", handlelength=1.4, handletextpad=0.4, borderaxespad=0.1)
fig.set_layout_engine("tight", w_pad=2.0); plt.savefig("fig/fig15_2_leaks.png", dpi=260); plt.close()

# ---------------- Part 3: wadi rainfall-runoff, extrapolation to an extreme storm ----------------
r3 = np.random.default_rng(153)
ndays = 30 * 150   # 30 wet seasons x 150 days
P = np.where(r3.random(ndays) < 0.18, r3.gamma(0.8, 9.0, ndays), 0.0)
P = np.minimum(P, 75)
P[-60] = 120.0     # extreme storm in test period (beyond training range)
P5 = np.array([P[max(0, i - 5):i].sum() for i in range(ndays)])
CN_true = np.where(P5 < 13, 72, np.where(P5 < 28, 82, 91))  # AMC I/II/III style
def scs(Pv, CN):
    S = 25400 / CN - 254; Ia = 0.2 * S
    return np.where(Pv > Ia, (Pv - Ia) ** 2 / (Pv + 0.8 * S), 0.0)
Q = scs(P, CN_true) * r3.lognormal(0, 0.15, ndays)
season = np.arange(ndays) // 150
tr = season < 25; te = ~tr
F = np.column_stack([P, P5])
gbq = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, random_state=0).fit(F[tr], Q[tr])
def loss(cn2):  # calibrate a single AMC-II CN with standard AMC adjustment (Chow et al. formulas)
    cn1 = 4.2 * cn2 / (10 - 0.058 * cn2); cn3 = 23 * cn2 / (10 + 0.13 * cn2)
    cn = np.where(P5[tr] < 13, cn1, np.where(P5[tr] < 28, cn2, cn3))
    return np.mean((scs(P[tr], cn) - Q[tr]) ** 2)
cn2 = minimize_scalar(loss, bounds=(50, 98), method="bounded").x
cn1 = 4.2 * cn2 / (10 - 0.058 * cn2); cn3 = 23 * cn2 / (10 + 0.13 * cn2)
cnt = np.where(P5 < 13, cn1, np.where(P5 < 28, cn2, cn3))
qc = scs(P, cnt); qg = gbq.predict(F)
wet = te & (P > 0)
i = ndays - 60
print("Part3 runoff: training max daily rain=%.0f mm; calibrated CN(AMC II)=%.1f (CN I=%.1f, III=%.1f)" % (P[tr].max(), cn2, cn1, cn3))
print("  test wet days MAE (mm): GBM=%.2f  calibrated SCS-CN=%.2f" % (mae(Q[wet & (P < 100)], qg[wet & (P < 100)]), mae(Q[wet & (P < 100)], qc[wet & (P < 100)])))
print("  extreme storm P=%.0f mm, P5=%.0f mm: true Q=%.1f mm  GBM=%.1f mm  SCS-CN=%.1f mm" % (P[i], P5[i], Q[i], qg[i], qc[i]))
fig, ax = plt.subplots(figsize=(6, 3.8))
ax.scatter(P[tr & (P > 0)], Q[tr & (P > 0)], s=5, color="0.7", label="Training days")
pp = np.linspace(0, 130, 200)
for p5, col, mk in [(5, "#2F855A", "o"), (35, "#B7791F", "s")]:
    cn = cn1 if p5 < 13 else (cn2 if p5 < 28 else cn3)
    ax.plot(pp, scs(pp, cn), color=col, lw=1.2, marker=mk, markevery=25, ms=4, label="SCS-CN, P5=%d mm" % p5)
    ax.plot(pp, gbq.predict(np.column_stack([pp, np.full_like(pp, p5)])), color=col, ls="--", lw=1.2, marker=mk, markevery=25, ms=4, mfc="white", label="GBM, P5=%d mm" % p5)
ax.scatter([P[i]], [Q[i]], marker="*", s=150, color="#C53030", zorder=5, label="Extreme storm (true)")
ax.axvline(P[tr].max(), color="k", ls=":", lw=0.8)
ax.set_xlabel("Daily rainfall P (mm)"); ax.set_ylabel("Runoff Q (mm)"); ax.legend(fontsize=7)
plt.tight_layout(); plt.savefig("fig/fig15_3_runoff.png", dpi=150); plt.close()
