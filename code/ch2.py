import numpy as np
# Example 2.1
k = np.array([2.0e5, 1.5e5, 1.0e5])   # kN/m
K = np.array([[k[0]+k[1], -k[1], 0],
              [-k[1], k[1]+k[2], -k[2]],
              [0, -k[2], k[2]]])
F = np.array([10., 20., 30.])          # kN
u = np.linalg.solve(K, F)
print("u (mm) =", np.round(u*1000, 3))
M = np.diag([50., 50., 50.])           # t
w2, phi = np.linalg.eig(np.linalg.inv(M) @ K)
f = np.sort(np.sqrt(w2.real))/(2*np.pi)
print("f (Hz) =", np.round(f, 2))

# Example 2.2
rng = np.random.default_rng(7)
cubes = rng.normal(38.0, 4.0, 40).round(1)
m, s = cubes.mean(), cubes.std(ddof=1)
fk = m - 1.645*s
print(f"mean={m:.1f} s={s:.2f} fk={fk:.1f} below30={np.sum(cubes<30)}")
from scipy.stats import norm
print("P(f<30) =", round(norm.cdf(30, m, s)*100, 1), "%")
boot = [rng.choice(cubes, 40).mean() for _ in range(5000)]
print("95% CI mean:", np.round(np.percentile(boot,[2.5,97.5]),1))

# Example 2.3
rng = np.random.default_rng(42)
wc = rng.uniform(0.35, 0.70, 60)
f28 = 96.5/7.0**wc * rng.normal(1, 0.05, 60)
y = np.log(f28)
a, b, lr = 3.0, 0.0, 0.5           # ln A, ln B
for it in range(4001):
    pred = a - b*wc
    e = pred - y
    ga, gb = 2*e.mean(), -2*(e*wc).mean()
    a, b = a - lr*ga, b - lr*gb
    if it in (0, 100, 1000, 4000):
        print(it, round((e**2).mean(),5), round(np.exp(a),1), round(np.exp(b),2))
