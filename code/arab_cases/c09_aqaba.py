# Aqaba seismic hazard: PSHA values (JJEES 15(1)) vs. the Jordanian code value
import numpy as np
T   = np.array([475, 975, 2475])          # return period (years)
pga = np.array([0.30, 0.45, 0.52])        # g, published PSHA for Aqaba
lam = 1 / T
k, c = np.polyfit(np.log(pga), np.log(lam), 1)      # ln(lambda) = c + k ln(PGA)
print(f"hazard curve: lambda = {np.exp(c):.2e} * PGA^{k:.2f}")
for p in pga: print(f"  PGA {p:.2f} g -> fitted T = {1/np.exp(c + k*np.log(p)):6.0f} yr")
lc = np.exp(c + k*np.log(0.20))
print(f"code PGA 0.20 g: return period {1/lc:.0f} yr, P(exceed in 50 yr) = {1-np.exp(-50*lc):.0%}")
print(f"design base shear ratio (PSHA 475 yr / code) = {0.30/0.20:.2f}")
# leave-one-out check of the 3-point fit
for i in range(3):
    j = [0, 1, 2]; j.remove(i)
    kk, cc = np.polyfit(np.log(pga[j]), np.log(lam[j]), 1)
    print(f"  without T={T[i]}: predicted PGA at {T[i]} yr = {np.exp((np.log(1/T[i]) - cc)/kk):.2f} g (published {pga[i]:.2f})")
# local slope from the two lowest points only (closest to 0.20 g)
kk, cc = np.polyfit(np.log(pga[:2]), np.log(lam[:2]), 1); l2 = np.exp(cc + kk*np.log(0.20))
print(f"local fit (475 & 975 yr): code PGA 0.20 g -> T = {1/l2:.0f} yr, P(50 yr) = {1-np.exp(-50*l2):.0%}")
