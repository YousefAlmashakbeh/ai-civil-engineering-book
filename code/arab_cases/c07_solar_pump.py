# Daily pumping schedule for the Aqaba-Amman carrier with the Al-Quweira solar plant (linear programme)
# published: 281 MW PV, 250 MCM/yr to Amman; tariffs, storage and the PV share for pumping are teaching assumptions
import numpy as np
from scipy.optimize import linprog
t = np.arange(24); Qavg = 250e6/365/86400; V = Qavg*86400
kMW = 115/Qavg                                        # MW per m3/s (from the hydraulic estimate)
pv = 140*np.clip(np.sin(np.pi*(t - 6)/12), 0, None)   # MW of PV left for pumping (half of 281 MW, clear day)
price = np.where((t >= 17) & (t <= 22), 120, 80)      # JD per MWh from the grid
Qmax, S = 1.6*Qavg, 300_000                           # m3/s, Amman storage band (m3)
# variables: q_0..23 (m3/s), g_0..23 (MW from grid)
c = np.r_[np.zeros(24), price]
def solve(S):
    A_ub, b_ub = [], []
    for i in range(24):                                   # kMW*q - g <= pv
        r = np.zeros(48); r[i] = kMW; r[24+i] = -1; A_ub.append(r); b_ub.append(pv[i])
    cum = np.tril(np.ones((24, 24)))*3600                 # storage: |cumulative pumped - cumulative delivered| <= S/2
    for i in range(24):
        r = np.r_[cum[i], np.zeros(24)]; A_ub += [r, -r]; b_ub += [S/2 + Qavg*3600*(i+1), S/2 - Qavg*3600*(i+1)]
    A_eq = [np.r_[np.full(24, 3600.0), np.zeros(24)]]; b_eq = [V]
    res = linprog(c, A_ub, b_ub, A_eq, b_eq, bounds=[(0, Qmax)]*24 + [(0, None)]*24)
    return res
res = solve(S)
q, g = res.x[:24], res.x[24:]
flat_grid = np.clip(kMW*Qavg - pv, 0, None)
print(f"daily volume {V/1e3:,.0f} thousand m3, pumping energy {kMW*V/3600:,.0f} MWh")
print(f"constant pumping : grid {flat_grid.sum():6,.0f} MWh, cost {np.dot(flat_grid, price):8,.0f} JD, PV used {kMW*V/3600-flat_grid.sum():5,.0f} MWh")
print(f"optimised        : grid {g.sum():6,.0f} MWh, cost {res.fun:8,.0f} JD, PV used {kMW*V/3600-g.sum():5,.0f} MWh")
print("hour : " + " ".join(f"{h:4d}" for h in t[::3]))
print("q/Qavg:" + " ".join(f"{x:4.2f}" for x in (q/Qavg)[::3]))
for S2 in (150_000, 300_000, 600_000, 1_200_000):
    r = solve(S2); print(f"storage band {S2/1e3:5,.0f} thousand m3: cost {r.fun:8,.0f} JD ({1-r.fun/np.dot(flat_grid, price):.0%} saving)")
