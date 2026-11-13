import numpy as np, torch, time, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
torch.set_num_threads(2)
torch.manual_seed(16); np.random.seed(16)

w_exact = lambda x: (x**4 - 2 * x**3 + x) / 24.0          # nondimensional SS beam, uniform load, EI=1
def mlp(width=32, depth=3):
    layers = [torch.nn.Linear(1, width), torch.nn.Tanh()]
    for _ in range(depth - 1): layers += [torch.nn.Linear(width, width), torch.nn.Tanh()]
    layers += [torch.nn.Linear(width, 1)]
    return torch.nn.Sequential(*layers)
def d(y, x): return torch.autograd.grad(y, x, torch.ones_like(y), create_graph=True)[0]
SCALE = 0.01   # output scaling so the network works with O(1) numbers

# ---------------- Part 1: forward PINN ----------------
net = mlp(); opt = torch.optim.Adam(net.parameters(), lr=2e-3)
xc = torch.linspace(0, 1, 101).reshape(-1, 1).requires_grad_(True)
xb = torch.tensor([[0.0], [1.0]], requires_grad=True)
t0 = time.time(); hist = []
for it in range(4000):
    opt.zero_grad()
    w = SCALE * net(xc); w4 = d(d(d(d(w, xc), xc), xc), xc)
    wb = SCALE * net(xb); wb2 = d(d(wb, xb), xb)
    loss = ((w4 - 1.0) ** 2).mean() + 1e4 * (wb ** 2).mean() + 1e2 * (wb2 ** 2).mean()
    loss.backward(); opt.step(); hist.append(loss.item())
tt = time.time() - t0
xs = np.linspace(0, 1, 201)
wp = SCALE * net(torch.tensor(xs, dtype=torch.float32).reshape(-1, 1)).detach().numpy().ravel()
we = w_exact(xs)
print("Part1 forward PINN: training time=%.1f s, final loss=%.2e" % (tt, hist[-1]))
print("  max deflection exact=%.5f (5/384=%.5f) PINN=%.5f ; max abs error / max w = %.2f%%" %
      (we.max(), 5 / 384, wp.max(), 100 * np.abs(wp - we).max() / we.max()))

# ---------------- Part 2: inverse PINN (identify EI) vs data-only MLP ----------------
EI_true = 0.8
xsens = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
rng = np.random.default_rng(162)
wsens = w_exact(xsens) / EI_true * (1 + 0.0) + rng.normal(0, 0.01 * (5 / 384 / EI_true), len(xsens))
Xs = torch.tensor(xsens, dtype=torch.float32).reshape(-1, 1); Ws = torch.tensor(wsens, dtype=torch.float32).reshape(-1, 1)
net2 = mlp(); logEI = torch.nn.Parameter(torch.tensor(0.0))
opt2 = torch.optim.Adam(list(net2.parameters()) + [logEI], lr=2e-3)
for it in range(5000):
    opt2.zero_grad()
    w = SCALE * net2(xc); w4 = d(d(d(d(w, xc), xc), xc), xc)
    wb = SCALE * net2(xb); wb2 = d(d(wb, xb), xb)
    EI = torch.exp(logEI)
    loss = ((EI * w4 - 1.0) ** 2).mean() + 1e4 * (wb ** 2).mean() + 1e2 * (wb2 ** 2).mean() \
           + 1e5 * ((SCALE * net2(Xs) - Ws) ** 2).mean()
    loss.backward(); opt2.step()
EI_hat = float(torch.exp(logEI))
wi = SCALE * net2(torch.tensor(xs, dtype=torch.float32).reshape(-1, 1)).detach().numpy().ravel()
# data-only network on the same 5 sensors
net3 = mlp(); opt3 = torch.optim.Adam(net3.parameters(), lr=2e-3)
for it in range(3000):
    opt3.zero_grad(); loss = ((SCALE * net3(Xs) - Ws) ** 2).mean(); loss.backward(); opt3.step()
wd = SCALE * net3(torch.tensor(xs, dtype=torch.float32).reshape(-1, 1)).detach().numpy().ravel()
wt = w_exact(xs) / EI_true
right = xs > 0.5
print("Part2 inverse: 5 sensors at x=0.1..0.5 with 1%% noise; EI true=%.2f, PINN estimate=%.3f (err %.1f%%)" %
      (EI_true, EI_hat, 100 * abs(EI_hat - EI_true) / EI_true))
print("  max error on unsensed half x>0.5 (%% of max w): PINN=%.1f%%  data-only MLP=%.1f%%" %
      (100 * np.abs(wi - wt)[right].max() / wt.max(), 100 * np.abs(wd - wt)[right].max() / wt.max()))
print("  support reaction check w(1): PINN=%.5f data-only=%.5f (should be 0)" % (wi[-1], wd[-1]))

fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
ax[0].plot(xs, we, "k", lw=2, label="Exact")
ax[0].plot(xs, wp, "--", color="tab:orange", lw=1.5, label="PINN (no data)")
ax[0].set_xlabel("x / L"); ax[0].set_ylabel("w EI / (q L^4)"); ax[0].invert_yaxis(); ax[0].legend(fontsize=8)
ax[0].set_title("Forward problem")
ax[1].plot(xs, wt, "k", lw=2, label="True (EI = 0.8)")
ax[1].plot(xs, wi, "--", color="tab:blue", lw=1.5, label="Inverse PINN (EI = %.3f)" % EI_hat)
ax[1].plot(xs, wd, ":", color="tab:red", lw=1.8, label="Data-only MLP")
ax[1].scatter(xsens, wsens, color="k", zorder=5, label="5 sensors")
ax[1].set_xlabel("x / L"); ax[1].set_ylabel("w (nondimensional)"); ax[1].invert_yaxis(); ax[1].legend(fontsize=7)
ax[1].set_title("Inverse problem")
plt.tight_layout(); plt.savefig("fig/fig16_1_pinn.png", dpi=150); plt.close()

# ---------------- Part 3: digital twin - Kalman updating of stiffness from frequency ----------------
r3 = np.random.default_rng(163)
months = np.arange(0, 72)
theta = 1 - 0.0025 * months / 12            # slow ageing 0.25%/yr
theta = np.where(months >= 40, theta - 0.04, theta)   # damage event: -4% stiffness at month 40
f0 = 4.0; sig_f = 0.006
f_meas = f0 * np.sqrt(theta) + r3.normal(0, sig_f, len(months))
z = (f_meas / f0) ** 2                       # measured stiffness ratio
R = (2 * sig_f / f0) ** 2                    # var of z (delta method)
Qp = (0.002) ** 2                            # process noise per month
m, P = 1.0, 0.02 ** 2
M, S = [], []
for k in range(len(months)):
    P = P + Qp                               # predict (random walk)
    K = P / (P + R); m = m + K * (z[k] - m); P = (1 - K) * P   # update
    M.append(m); S.append(np.sqrt(P))
M = np.array(M); S = np.array(S)
from scipy.stats import norm
p_below = norm.cdf((0.97 - M) / S)
first = months[np.argmax(p_below > 0.95)] if np.any(p_below > 0.95) else None
print("Part3 digital twin: frequency noise %.3f Hz; measurement sd of stiffness ratio=%.4f" % (sig_f, np.sqrt(R)))
for k in [12, 36, 39, 41, 44, 48, 71]:
    print("  month %2d: true theta=%.4f  posterior mean=%.4f  sd=%.4f  P(theta<0.97)=%.2f" % (k, theta[k], M[k], S[k], p_below[k]))
print("  first month with P(theta<0.97)>0.95: %s (damage at month 40)" % first)
# predicted midspan deflection under a rating load relative to design (prop. to 1/theta)
print("  deflection increase implied at month 71: %.1f%% (true %.1f%%)" % (100 * (1 / M[71] - 1), 100 * (1 / theta[71] - 1)))
fig, ax = plt.subplots(figsize=(7, 3.6))
ax.scatter(months, z, s=10, color="0.6", label="Single-month estimate (f/f0)^2")
ax.plot(months, theta, "k", lw=2, label="True stiffness ratio")
ax.plot(months, M, color="tab:blue", lw=1.5, label="Twin posterior mean")
ax.fill_between(months, M - 2 * S, M + 2 * S, color="tab:blue", alpha=0.2, label="95% band")
ax.axhline(0.97, color="tab:red", ls="--", lw=1, label="Inspection trigger 0.97")
ax.set_xlabel("Month"); ax.set_ylabel("Stiffness ratio theta"); ax.legend(fontsize=7, loc="lower left")
plt.tight_layout(); plt.savefig("fig/fig16_2_twin.png", dpi=150); plt.close()
