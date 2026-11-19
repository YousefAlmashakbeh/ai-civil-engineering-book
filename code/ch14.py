import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.ensemble import HistGradientBoostingRegressor
import statsmodels.api as sm

# ---------------- Part 1: hourly traffic, Amman-like corridor ----------------
rng = np.random.default_rng(14)
idx = pd.date_range("2024-01-01", "2026-06-30 23:00", freq="h")
df = pd.DataFrame(index=idx)
h = idx.hour.values; dow = idx.dayofweek.values  # Mon=0 ... Fri=4, Sat=5
weekend = np.isin(dow, [4, 5])
# approximate Ramadan and Eid al-Fitr windows (illustrative)
ram = [("2024-03-11", "2024-04-09"), ("2025-03-01", "2025-03-29"), ("2026-02-18", "2026-03-19")]
eid = [("2024-04-10", "2024-04-13"), ("2025-03-30", "2025-04-02"), ("2026-03-20", "2026-03-23")]
def flag(pairs):
    f = np.zeros(len(idx), bool)
    for a, b in pairs:
        f |= (idx >= a) & (idx < pd.Timestamp(b) + pd.Timedelta(days=1))
    return f
R = flag(ram); E = flag(eid)
def g(x, mu, s): return np.exp(-0.5 * ((x - mu) / s) ** 2)
normal = 250 + 1300 * g(h, 7.5, 1.2) + 1100 * g(h, 15.5, 1.8) + 500 * g(h, 11, 3)
wkend = 200 + 700 * g(h, 13, 3) + 600 * g(h, 20, 2.5)
ramad = 200 + 1000 * g(h, 9.5, 1.2) + 1500 * g(h, 16.5, 1.0) + 900 * g(h, 21.5, 1.8)  # pre-iftar peak, late night
base = np.where(weekend, wkend, normal)
base = np.where(R & ~weekend, ramad, base)
base = np.where(R & weekend, 0.8 * ramad, base)
base = np.where(E, wkend * 0.7, base)
growth = 1 + 0.03 * (idx.year.values - 2024)
y = rng.poisson(base * growth * rng.lognormal(0, 0.08, len(idx)))
df["y"] = y
df["hour"] = h; df["dow"] = dow; df["ram"] = R.astype(int); df["eid"] = E.astype(int)
df["year"] = idx.year.values; df["month"] = idx.month.values
df["lag168"] = df["y"].shift(168)
train = df[(df.index < "2026-01-01") & df.lag168.notna()]
test = df[df.index >= "2026-01-01"]
feats = ["hour", "dow", "ram", "eid", "year", "month"]
gbm = HistGradientBoostingRegressor(max_iter=400, learning_rate=0.05, random_state=0)
gbm.fit(train[feats], train["y"])
pg = gbm.predict(test[feats]); pn = test["lag168"].values
def mape(a, b): return 100 * np.mean(np.abs(a - b) / np.maximum(a, 50))
mask_r = test.ram.values == 1; mask_e = test.eid.values == 1
mask_after = (test.index >= "2026-03-20") & (test.index < "2026-03-27")  # first week after Ramadan
print("Part1 traffic: train hours=%d test hours=%d" % (len(train), len(test)))
for name, m in [("all", np.ones(len(test), bool)), ("ramadan", mask_r), ("normal (no ram/eid)", ~mask_r & ~mask_e),
                ("first week after Ramadan", mask_after)]:
    print("  %-26s MAPE seasonal-naive=%.1f%%  GBM-calendar=%.1f%%" % (name, mape(test.y.values[m], pn[m]), mape(test.y.values[m], pg[m])))
# GBM without ramadan flag
gb2 = HistGradientBoostingRegressor(max_iter=400, learning_rate=0.05, random_state=0)
f2 = ["hour", "dow", "eid", "year", "month"]
gb2.fit(train[f2], train["y"]); p2 = gb2.predict(test[f2])
print("  GBM without Ramadan flag: ramadan MAPE=%.1f%%" % mape(test.y.values[mask_r], p2[mask_r]))

import matplotlib.dates as mdates
fig, ax = plt.subplots(2, 2, figsize=(6.8, 4.8), sharex="col", gridspec_kw=dict(height_ratios=[1.5, 1]))
w1 = (test.index >= "2026-01-11") & (test.index < "2026-01-18")
w2 = (test.index >= "2026-03-01") & (test.index < "2026-03-08")
for k, (w, t) in enumerate([(w1, "normal week (Jan 2026)"), (w2, "Ramadan week (Mar 2026)")]):
    a, b = ax[0, k], ax[1, k]; x = test.index[w]; yo = test.y.values[w]
    a.plot(x, yo, "k", lw=1.1, label="observed")
    a.plot(x, pn[w], color="#C05621", lw=.9, ls="--", label="seasonal naive (t-168 h)")
    a.plot(x, pg[w], color="#2B6CB0", lw=.9, ls="-", label="GBM + calendar")
    a.set_title(t); a.set_ylabel("vehicles / hour" if k == 0 else "")
    b.plot(x, pn[w] - yo, color="#C05621", lw=.8, ls="--", label="naive error")
    b.plot(x, pg[w] - yo, color="#2B6CB0", lw=.9, label="GBM error"); b.axhline(0, c="k", lw=.6)
    b.set_ylabel("forecast - observed" if k == 0 else ""); b.xaxis.set_major_locator(mdates.DayLocator()); b.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: mdates.num2date(v).strftime("%a")[:2])); b.tick_params(axis="x", labelsize=7, rotation=0)
    for lab in b.get_xticklabels(): lab.set_ha("left")
    lim = max(abs(pn[w] - yo).max(), abs(pg[w] - yo).max()) * 1.05; b.set_ylim(-lim, lim)
_h, _l = ax[0, 0].get_legend_handles_labels(); ax[1, 0].legend(fontsize=7, loc="lower left", ncol=2)
plt.tight_layout(rect=(0, 0, 1, 0.94)); fig.legend(_h, _l, loc="upper center", ncol=3, fontsize=7.5, frameon=False); plt.savefig("fig/fig14_1_traffic.png", dpi=260); plt.close()

# ---------------- Part 2: signal control, Webster vs Q-learning ----------------
S = 0.5      # saturation flow veh/s per approach (1800 veh/h)
LOST = 4     # all-red/lost seconds per phase change
MING = 6
def webster(q1, q2):
    y1, y2 = q1 / 1800, q2 / 1800; Y = y1 + y2; L = 2 * LOST
    C = (1.5 * L + 5) / (1 - Y); ge = C - L
    return C, ge * y1 / Y, ge * y2 / Y
def demand(t, profile):
    if profile == "steady": return 600, 400
    # shifting peak: approach 1 heavy first half, approach 2 heavy second half
    return (750, 300) if t < 1800 else (300, 750)
def simulate(policy, profile, seed, Q=None, eps=0.0, alpha=0.1, gamma=0.98, learn=False):
    r = np.random.default_rng(seed)
    q = np.zeros(2); t = 0; tot = 0.0; arrived = 0
    def step(green):          # advance 1 s; green = index of served approach or None (lost time)
        nonlocal t, tot, arrived
        l1, l2 = demand(t, profile)
        a = r.poisson([l1 / 3600, l2 / 3600]); q[:] += a; arrived += a.sum()
        if green is not None: q[green] = max(0, q[green] - S)
        tot += q.sum(); t += 1
        return q.sum()
    if policy in ("webster", "tod"):
        C, g1, g2 = webster(600, 400); plan = [int(round(g1)), int(round(g2))]; ph = 0
        while t < 3600:
            if policy == "tod":   # time-of-day plan re-timed with the true demand of each period
                C, g1, g2 = webster(*demand(t, profile)); plan = [int(round(g1)), int(round(g2))]
            for _ in range(plan[ph]): step(ph)
            for _ in range(LOST): step(None)
            ph = 1 - ph
        return tot / arrived
    b = lambda x: min(int(x // 2), 9)
    phase = 0; tin = 0
    for _ in range(MING): step(phase); tin += 1
    while t < 3600:
        s = (b(q[phase]), b(q[1 - phase]), min(tin // 5, 5))
        act = int(r.integers(2)) if r.random() < eps else int(np.argmax(Q[s]))
        cost = 0.0
        if act == 0:
            cost += step(phase); tin += 1
        else:
            for _ in range(LOST): cost += step(None)
            phase = 1 - phase; tin = 0
            for _ in range(MING): cost += step(phase); tin += 1
        if learn:
            s2 = (b(q[phase]), b(q[1 - phase]), min(tin // 5, 5))
            Q[s][act] += alpha * (-cost / 20 + gamma * Q[s2].max() - Q[s][act])
    return tot / arrived   # mean delay, s/veh

C, g1, g2 = webster(600, 400)
print("Part2 Webster: cycle=%.1f s green1=%.1f s green2=%.1f s" % (C, g1, g2))
Q = np.zeros((10, 10, 6, 2))
curve = []
for ep in range(400):
    eps = max(0.05, 1 - ep / 250)
    prof = "steady" if ep % 2 == 0 else "shift"
    simulate("rl", prof, 1000 + ep, Q=Q, eps=eps, learn=True)
    if ep % 20 == 19:
        curve.append((ep + 1, np.mean([simulate("rl", "steady", 50000 + k, Q=Q) for k in range(5)]),
                      np.mean([simulate("rl", "shift", 60000 + k, Q=Q) for k in range(5)])))
res = {}
for prof in ["steady", "shift"]:
    w = [simulate("webster", prof, 90000 + k) for k in range(30)]
    rl = [simulate("rl", prof, 90000 + k, Q=Q) for k in range(30)]
    td = [simulate("tod", prof, 90000 + k) for k in range(30)]
    res[prof] = (np.mean(w), np.mean(rl))
    print("  demand=%-6s mean delay Webster fixed=%.1f  Webster time-of-day=%.1f  Q-learning=%.1f s/veh" % (prof, np.mean(w), np.mean(td), np.mean(rl)))
fig, ax = plt.subplots(figsize=(6, 3.6))
cv = np.array(curve)
ax.plot(cv[:, 0], cv[:, 1], "o-", color="#2B6CB0", label="Q-learning, steady demand")
ax.plot(cv[:, 0], cv[:, 2], "s-", color="#C53030", label="Q-learning, shifting peak")
ax.axhline(res["steady"][0], color="#2B6CB0", ls="--", lw=1.3, label="Webster fixed, steady")
ax.axhline(res["shift"][0], color="#C53030", ls=":", lw=2, label="Webster fixed, shifting")
ax.set_yscale("log"); ax.set_xlabel("Training episodes (1 h each)"); ax.set_ylabel("Mean delay (s/veh, log scale)"); ax.legend(fontsize=7)
plt.tight_layout(); plt.savefig("fig/fig14_3_signal.png", dpi=150); plt.close()

# ---------------- Part 3: crash frequency, NB vs Poisson, Empirical Bayes hotspots ----------------
r3 = np.random.default_rng(314)
n = 1500
L = r3.uniform(0.5, 3.0, n); aadt = np.exp(r3.uniform(np.log(3000), np.log(40000), n))
curv = r3.binomial(1, 0.25, n); acc = r3.poisson(4, n)
X = np.column_stack([np.log(aadt), curv, acc])
mu = np.exp(-7.8 + 0.75 * np.log(aadt) + np.log(L) + 0.35 * curv + 0.06 * acc)  # crashes/yr
alpha_true = 0.5
lam = mu * r3.gamma(1 / alpha_true, alpha_true, n)   # segment's true long-term rate
yrs = 3
y1 = r3.poisson(lam * yrs); y2 = r3.poisson(lam * yrs)  # two 3-year periods
Xd = sm.add_constant(X); off = np.log(L * yrs)
pois = sm.GLM(y1, Xd, family=sm.families.Poisson(), offset=off).fit()
nbm = sm.NegativeBinomial(y1, Xd, offset=off).fit(disp=0)
alpha_hat = nbm.params[-1]
print("Part3 crashes: mean=%.2f var=%.2f per segment (3 yr)" % (y1.mean(), y1.var()))
print("  Poisson dispersion (Pearson chi2/df)=%.2f" % (pois.pearson_chi2 / pois.df_resid))
print("  coef ln(AADT): Poisson %.3f (se %.3f) | NB %.3f (se %.3f) | true 0.75" %
      (pois.params[1], pois.bse[1], nbm.params[1], nbm.bse[1]))
print("  coef curve: Poisson %.3f (se %.3f) | NB %.3f (se %.3f) | true 0.35" %
      (pois.params[2], pois.bse[2], nbm.params[2], nbm.bse[2]))
print("  NB alpha_hat=%.2f (true %.2f)" % (alpha_hat, alpha_true))
mu_hat = np.exp(Xd @ nbm.params[:-1] + off)           # predicted 3-yr count
w = 1 / (1 + alpha_hat * mu_hat)
eb = w * mu_hat + (1 - w) * y1
k = int(0.05 * n)
top_raw = np.argsort(-y1)[:k]; top_eb = np.argsort(-eb)[:k]

print("  top 5%% by raw count: period1 mean=%.1f -> period2 mean=%.1f (drop %.0f%%)" %
      (y1[top_raw].mean(), y2[top_raw].mean(), 100 * (1 - y2[top_raw].mean() / y1[top_raw].mean())))
print("  top 5%% by EB: EB estimate mean=%.1f -> period2 mean=%.1f" % (eb[top_eb].mean(), y2[top_eb].mean()))
excess_true = lam * yrs - mu * yrs  # true excess over similar sites
tt = set(np.argsort(-excess_true)[:k])
print("  overlap with true top-5%% excess sites: raw=%d/%d EB-excess=%d/%d" %
      (len(tt & set(top_raw)), k, len(tt & set(np.argsort(-(eb - mu_hat))[:k])), k))
fig, ax = plt.subplots(figsize=(6, 3.8))
ax.scatter(y1, y2, s=6, color="0.75", label="All segments")
ax.scatter(y1[top_raw], y2[top_raw], s=14, color="#C53030", label="Top 5% by raw count")
ax.plot([0, y1.max()], [0, y1.max()], "k--", lw=0.8)
ax.axhline(y2[top_raw].mean(), color="#C53030", ls=":", lw=1)
ax.axvline(y1[top_raw].mean(), color="#C53030", ls=":", lw=1)
ax.set_xlabel("Crashes, period 1 (3 yr)"); ax.set_ylabel("Crashes, period 2 (3 yr)"); ax.legend(fontsize=8)
plt.tight_layout(); plt.savefig("fig/fig14_4_hotspots.png", dpi=150); plt.close()

# ---------------- Checks requested in review ----------------
# (a) simulator vs Webster's delay formula, steady demand 600/400 veh/h
C, g1, g2 = webster(600, 400)
def webster_delay(qh, gr, C):
    q = qh / 3600; lam = gr / C; x = q / (lam * S)
    return C * (1 - lam) ** 2 / (2 * (1 - lam * x)) + x ** 2 / (2 * q * (1 - x)) - 0.65 * (C / q ** 2) ** (1 / 3) * x ** (2 + 5 * lam)
d1, d2 = webster_delay(600, round(g1), 2 * LOST + round(g1) + round(g2)), webster_delay(400, round(g2), 2 * LOST + round(g1) + round(g2))
dw = (600 * d1 + 400 * d2) / 1000
ds = np.array([simulate("webster", "steady", s) for s in range(200)])
print("Check: Webster plan C=%.0f s g=%d/%d s; Webster formula delay=%.1f / %.1f -> %.1f s/veh; simulator=%.1f +- %.1f s/veh (200 seeds)" % (2 * LOST + round(g1) + round(g2), round(g1), round(g2), d1, d2, dw, ds.mean(), ds.std()))
# (b) the 'year' feature: trees cannot extend a trend to an unseen year
f3 = ["hour", "dow", "ram", "eid", "month"]
gb3 = HistGradientBoostingRegressor(max_iter=400, learning_rate=0.05, random_state=0).fit(train[f3], train["y"])
p3 = gb3.predict(test[f3])
# growth handled outside the trees: fit on volume divided by a yearly level, then scale by the extrapolated level
lvl = train.groupby("year").y.mean(); rate = lvl[2025] / lvl[2024]
gb4 = HistGradientBoostingRegressor(max_iter=400, learning_rate=0.05, random_state=0).fit(train[f3], train["y"] / train["year"].map(lvl))
p4 = gb4.predict(test[f3]) * lvl[2025] * rate
nm = ~mask_r & ~mask_e
for nme, p in [("GBM with year (as in text)", pg), ("GBM without year", p3), ("GBM on detrended volume x extrapolated growth", p4)]:
    print("  %-46s normal-days MAPE=%.1f%%  mean bias=%+.1f%%" % (nme, mape(test.y.values[nm], p[nm]), 100 * (p[nm].sum() / test.y.values[nm].sum() - 1)))
print("  yearly level ratio 2025/2024 = %.3f" % rate)
