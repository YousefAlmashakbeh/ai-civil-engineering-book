# Cut slopes in clayey marl along the Irbid-Jerash-Amman highway: Monte Carlo infinite-slope analysis
# residual strength ranges from Al-Homoud & Tubeileh: c'r = 5-18 kPa, phi'r = 13-18 deg; other values are teaching assumptions
import numpy as np
rng = np.random.default_rng(7); N = 200_000
c   = rng.uniform(5, 18, N)                 # kPa
phi = np.radians(rng.uniform(13, 18, N))
m   = rng.uniform(0.2, 1.0, N)              # water table ratio in a wet winter
z, g, gw = 4.0, 19.0, 9.81                  # slip depth (m), unit weights (kN/m3)
def FS(beta):
    b = np.radians(beta)
    return (c + (g - m*gw)*z*np.cos(b)**2*np.tan(phi)) / (g*z*np.sin(b)*np.cos(b))
for beta in (12, 15, 18, 22, 26):
    f = FS(beta); print(f"slope {beta:2d} deg: mean FS = {f.mean():.2f}, P(FS<1) = {np.mean(f<1):6.1%}, P(FS<1.3) = {np.mean(f<1.3):6.1%}")
f = FS(18); X = np.column_stack([(c-c.mean())/c.std(), (phi-phi.mean())/phi.std(), (m-m.mean())/m.std()])
w = np.linalg.lstsq(np.column_stack([X, np.ones(N)]), f, rcond=None)[0][:3]
share = w**2 / np.sum(w**2)
print("share of FS variance (18 deg): " + ", ".join(f"{k} {v:.0%}" for k, v in zip(["c'", "phi'", "water m"], share)))
dry = (c + g*z*np.cos(np.radians(18))**2*np.tan(phi))/(g*z*np.sin(np.radians(18))*np.cos(np.radians(18)))
print(f"same slope with drainage (m = 0): P(FS<1) = {np.mean(dry<1):.1%}")
