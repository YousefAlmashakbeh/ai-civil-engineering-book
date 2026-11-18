# Aqaba-Amman National Water Carrier: hydraulic estimate + a Kalman-filter "twin" that tracks pipe roughness
# published: 300 MCM/yr (250 to Amman), ~438 km pipeline, 2.0-2.5 m diameter, Amman ~1000 m above sea level
import numpy as np
Q = 250e6/365/86400; L, D, Hs, eta = 438e3, 2.5, 1000.0, 0.85
A = np.pi*D**2/4; v = Q/A
def hf(f): return f*L/D*v**2/(2*9.81)
f0 = 0.011
P = 1000*9.81*Q*(Hs + hf(f0))/eta/1e6
print(f"Q = {Q:.2f} m3/s, v = {v:.2f} m/s, friction head = {hf(f0):.0f} m, total head = {Hs+hf(f0):.0f} m")
print(f"pumping power = {P:.0f} MW, energy = {9.81*(Hs+hf(f0))/eta/3600:.2f} kWh/m3")
# twin: daily head-loss measurements on one 40 km section; true f drifts (scaling/biofouling) - synthetic
rng = np.random.default_rng(5); days = 730; Ls = 40e3
f_true = f0 + 0.002*np.arange(days)/days + 0.0006*(np.arange(days) > 500)     # gradual drift + a step on day 501
y = f_true*Ls/D*v**2/19.62 + rng.normal(0, 0.6, days)                          # measured head loss (m)
Hm = Ls/D*v**2/19.62; x, Pk, qn, R = f0, 1e-6, 1e-9, 0.6**2
est = []
for k in range(days):
    Pk += qn; K = Pk*Hm/(Hm*Pk*Hm + R); x += K*(y[k] - Hm*x); Pk *= (1 - K*Hm); est.append(x)
est = np.array(est)
for d in (100, 400, 500, 530, 729):
    print(f"day {d+1:3d}: true f = {f_true[d]:.5f}, twin f = {est[d]:.5f} +/- {1.96*np.sqrt(Pk):.5f}")
dP = 1000*9.81*Q*(hf(est[-1]) - hf(f0))/eta/1e6
print(f"extra pumping power after two years = {dP:.1f} MW (~{dP*8760/1e3:.0f} GWh/yr)")
