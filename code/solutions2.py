# Appendix D: numeric answers for selected exercises (chapters 1-12)
import numpy as np
from scipy.linalg import eigh
def f1(k):
    K=np.array([[k[0]+k[1],-k[1],0],[-k[1],k[1]+k[2],-k[2]],[0,-k[2],k[2]]]); w2,_=eigh(K,np.diag([50.,50.,50.])); return np.sqrt(w2[0])/(2*np.pi)
a=f1([2e5,1.5e5,1e5]); b=f1([1.6e5,1.5e5,1e5]); print(f"Ch2 Ex1: f1={a:.2f} -> {b:.2f} Hz ({100*(b/a-1):.1f}%)")
b_=np.array([250,250,300,300,300,350]); d=np.array([450,450,540,540,640,640]); As=np.array([942,1232,1232,1608,1608,2412])
print("Ch3 Ex1: rho (%) =",np.round(100*As/(b_*d),2))
print("Ch4 Ex2: missed per 100 cracks:",round(100*(1-8/27)),"and",round(100*(1-24/27)))
print("Ch6 Ex1: weights =",3*3*16*32,"+ biases 32 =",3*3*16*32+32)
print("Ch8 Ex2: Nurse-Saul (T0=-10C): 3 d at 35C =",(35+10)*72,"C.h ; 7 d at 10C =",(10+10)*168,"C.h")
print("Ch12 Ex1: pixel =",1500/6000,"mm/px ; smallest limit judged with the quarter rule =",4*1500/6000,"mm")
rng=np.random.default_rng(0); N=200000; z,g,gw=2.0,19.0,9.81
def FS(beta,c,phi,m): bb=np.radians(beta); return c/(g*z*np.sin(bb)*np.cos(bb))+(1-m*gw/g)*np.tan(np.radians(phi))/np.tan(bb)
s=np.sqrt(np.log(1+0.4**2)); c=np.exp(rng.normal(np.log(8)-s**2/2,s,N)); phi=rng.normal(34,3,N)
print("Ch10 Ex4: Pf with m~U(0,0.3):"," ".join(f"{bt}deg={np.mean(FS(bt,c,phi,rng.uniform(0,0.3,N))<1)*100:.2f}%" for bt in (28,32,36,40)), "| worst case m=0.3:", " ".join(f"{bt}deg={np.mean(FS(bt,c,phi,0.3)<1)*100:.2f}%" for bt in (28,32,36,40)))
r4=np.random.default_rng(1); N4=4000000; c4=np.exp(r4.normal(np.log(8)-s**2/2,s,N4)); p4=r4.normal(34,3,N4); m4=r4.uniform(0,0.3,N4); print("Ch10 Ex4 (all six slopes, 4e6 samples): m~U(0,0.3):"," ".join(f"{bt}deg={np.mean(FS(bt,c4,p4,m4)<1)*100:.3f}%" for bt in (26,28,30,32,36,40)),"| m=0.3:"," ".join(f"{bt}deg={np.mean(FS(bt,c4,p4,0.3)<1)*100:.3f}%" for bt in (26,28,30,32,36,40)))
# Ch7 Ex1 short column: Pu=2000 kN
print("Ch9/18: beta for Pf=1%:", round(float(__import__('scipy.stats',fromlist=['norm']).norm.ppf(0.99)),2))
