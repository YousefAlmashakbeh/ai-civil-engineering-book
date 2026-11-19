# Aqaba seismic hazard: PSHA values (JJEES 15(1)) vs. the Jordanian code value, compared on one site basis
import numpy as np
T   = np.array([475, 975, 2475])          # return period (years)
pga = np.array([0.30, 0.40, 0.50])        # g, stiff soil SD, Vs = 270 m/s (Table 4 of the study)
rock = np.array([0.40, 0.45, 0.52])       # g, rock, Vs = 760 m/s (Table 4 of the study)
Z, Ca = 0.20, 0.28                        # code zone factor (rock reference); UBC-97 Ca for soil SD at Z = 0.20
lam = 1 / T
k, c = np.polyfit(np.log(pga), np.log(lam), 1)      # ln(lambda) = c + k ln(PGA)
print(f"hazard curve (stiff soil): lambda = {np.exp(c):.2e} * PGA^{k:.2f}")
for p in pga: print(f"  PGA {p:.2f} g -> fitted T = {1/np.exp(c + k*np.log(p)):6.0f} yr")
print(f"rock basis : PSHA 475 yr {rock[0]:.2f} g vs zone factor Z {Z:.2f} g -> ratio {rock[0]/Z:.2f}")
lc = np.exp(c + k*np.log(Ca))
print(f"soil SD    : code Ca {Ca:.2f} g -> return period {1/lc:.0f} yr, P(exceed in 50 yr) = {1-np.exp(-50*lc):.0%}, ratio {pga[0]/Ca:.2f}")
lz = np.exp(c + k*np.log(Z))
print(f"mixed basis (rock Z on the soil curve, wrong): {Z:.2f} g -> {1/lz:.0f} yr, P(50 yr) = {1-np.exp(-50*lz):.0%}")
# leave-one-out check of the 3-point fit
for i in range(3):
    j = [0, 1, 2]; j.remove(i)
    kk, cc = np.polyfit(np.log(pga[j]), np.log(lam[j]), 1)
    print(f"  without T={T[i]}: predicted PGA at {T[i]} yr = {np.exp((np.log(1/T[i]) - cc)/kk):.2f} g (published {pga[i]:.2f})")
# local slope from the two lowest points only (closest to the code values)
kk, cc = np.polyfit(np.log(pga[:2]), np.log(lam[:2]), 1)
for a in (Ca, Z):
    l2 = np.exp(cc + kk*np.log(a)); print(f"local fit (475 & 975 yr): {a:.2f} g -> T = {1/l2:.0f} yr, P(50 yr) = {1-np.exp(-50*l2):.0%}")
