# Conditional slope reliability: water table as a seasonal state, not a random soil property
import numpy as np
rng=np.random.default_rng(0); N=200000; z,g,gw=2.0,19.0,9.81
def FS(beta,c,phi,m): b=np.radians(beta); return c/(g*z*np.sin(b)*np.cos(b))+(1-m*gw/g)*np.tan(np.radians(phi))/np.tan(b)
s_ln=np.sqrt(np.log(1+0.4**2)); c=np.exp(rng.normal(np.log(8)-s_ln**2/2,s_ln,N)); phi=rng.normal(34,3,N)
for bt in (22,24,26,28,30,32,36):
    print(f"slope {bt} deg: Pf mixed m~U(0,0.8)={np.mean(FS(bt,c,phi,rng.uniform(0,0.8,N))<1)*100:.2f}%  dry (m=0)={np.mean(FS(bt,c,phi,0)<1)*100:.2f}%  wet season (m=0.8)={np.mean(FS(bt,c,phi,0.8)<1)*100:.1f}%  FS(mean, m=0.8)={FS(bt,8,34,0.8):.2f}")
