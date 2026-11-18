# Frequency monitoring on a cable-stayed bridge with the dimensions of Wadi Abdoun Bridge (two 132-134 m main spans)
# all monitoring data below are synthetic; f0 and the temperature coefficient are assumptions
import numpy as np
rng = np.random.default_rng(4); days = np.arange(730)
T = 18 + 11*np.sin(2*np.pi*(days - 110)/365) + rng.normal(0, 3, days.size)       # daily mean temperature (C), Amman-like
f0, a = 0.620, -0.0012                                                            # Hz, relative change per C
dmg = np.where(days >= 600, -0.010, 0.0)                                          # 1 % stiffness-related drop from day 601
f = f0*(1 + a*(T - 18) + dmg) + rng.normal(0, 0.0015, days.size)
print(f"seasonal swing of f: {f[:365].max()-f[:365].min():.4f} Hz = {100*(f[:365].max()-f[:365].min())/f0:.1f}% of f0")
# rule 1: fixed band +/- 2% around f0
alarm1 = np.abs(f/f0 - 1) > 0.02
print(f"fixed band: {alarm1[:600].sum()} false alarms before day 601, first alarm after damage: day {601 + np.argmax(alarm1[600:]) if alarm1[600:].any() else 'none'}")
# rule 2: learn f = b0 + b1*T on year 1, control chart on residuals
X = np.column_stack([np.ones(365), T[:365]]); b = np.linalg.lstsq(X, f[:365], rcond=None)[0]
res = f - (b[0] + b[1]*T); s = res[:365].std(ddof=2)
print(f"model: f = {b[0]:.4f} {b[1]:+.6f} T  (residual sd {s*1000:.2f} mHz)")
ewma, lam, al = 0.0, 0.2, []
for r in res:
    ewma = lam*r + (1-lam)*ewma; al.append(ewma < -3*s*np.sqrt(lam/(2-lam)))
al = np.array(al)
print(f"residual EWMA: {al[365:600].sum()} false alarms in days 366-600, first alarm after damage: day {601 + np.argmax(al[600:])}")
print(f"estimated drop = {-res[600:].mean()/f0:.2%} (true 1.00%)")
