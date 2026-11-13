import numpy as np
from scipy.stats import norm
print("Ch13 Ex1: wavelength in concrete V=4000 m/s")
for f in (50e3, 100e3): print("  f=%3.0f kHz -> lambda=%.0f mm" % (f/1e3, 4000/f*1000))
print("Ch13 Ex2: dynamic E for V=3500 m/s, rho=2400, nu=0.2")
rho, nu = 2400, 0.2
for V in (4000, 3500):
    print("  V=%d -> Ed=%.1f GPa" % (V, rho*V**2*(1+nu)*(1-2*nu)/(1-nu)/1e9))
print("Ch14 Ex1: Webster, q=900 & 500 veh/h, s=1800, lost 4 s/phase")
y1, y2 = 900/1800, 500/1800; Y = y1+y2; L = 8
C = (1.5*L+5)/(1-Y); print("  Y=%.3f C0=%.1f s g1=%.1f s g2=%.1f s" % (Y, C, (C-L)*y1/Y, (C-L)*y2/Y))
for Yt in (0.85, 0.9, 0.95): print("  Y=%.2f -> C0=%.0f s" % (Yt, (1.5*L+5)/(1-Yt)))
print("Ch15 Ex1: SCS-CN, P=60 mm, CN=80 and AMC III")
def scs(P, CN):
    S = 25400/CN-254; Ia = 0.2*S; return (P-Ia)**2/(P+0.8*S) if P > Ia else 0.0
cn3 = 23*80/(10+0.13*80)
print("  CN=80: Q=%.1f mm ; CN_III=%.1f: Q=%.1f mm" % (scs(60, 80), cn3, scs(60, cn3)))
print("Ch15 Ex2: leak 2 m3/h for one year")
v = 2*24*365; print("  volume=%d m3 = weekly use of %.0f households for a year (4 m3/week -> %.0f m3/yr)" % (v, v/(4*52), 4*52))
print("Ch18 Ex1: predicted 0.8 for 100 bridges, 50 failed -> observed 0.50, overconfident by %.0f points" % ((0.8-0.5)*100))
print("Ch10/Ch18: reliability index for Pf=7.5%%: beta=%.2f ; Pf for beta=3.0: %.2e" % (-norm.ppf(0.075), norm.cdf(-3)))
print("Ch16 Ex1: cantilever max deflection (EI w''''=q, L=1): exact qL^4/(8EI) = %.4f" % (1/8))
