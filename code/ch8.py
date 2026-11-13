import numpy as np, matplotlib, warnings; warnings.filterwarnings("ignore")
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.special import erf
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.metrics import mean_absolute_error
rng=np.random.default_rng(8)
# (1) early-age prediction
n=300; wb=rng.uniform(0.35,0.6,n); scm=rng.uniform(0,0.5,n)*(rng.random(n)<0.6)
f28=110/6.5**wb*rng.normal(1,0.04,n)
def g(t,s): a,b=4+10*s,0.85-0.1*s; return (t/(a+b*t))/(28/(a+b*28))
f3=f28*g(3,scm)*rng.normal(1,0.05,n); f7=f28*g(7,scm)*rng.normal(1,0.05,n)
aci=f7/(7/(4+0.85*7)/(28/(4+0.85*28)))
X=np.c_[f3,f7,wb,scm]; gb=GradientBoostingRegressor(random_state=0)
p=cross_val_predict(gb,X,f28,cv=KFold(5,shuffle=True,random_state=0))
hi=scm>0.3
print(f"ACI-209 from 7d: MAE={mean_absolute_error(f28,aci):.2f}  high-SCM MAE={mean_absolute_error(f28[hi],aci[hi]):.2f} bias={np.mean(aci[hi]-f28[hi]):.2f}")
print(f"GBM (f3,f7,w/b,SCM): MAE={mean_absolute_error(f28,p):.2f}  high-SCM MAE={mean_absolute_error(f28[hi],p[hi]):.2f} bias={np.mean(p[hi]-f28[hi]):.2f}")
print("high-SCM mixes:",hi.sum())
fig,ax=plt.subplots(1,2,figsize=(8,3.5),sharey=True)
for a,pp,t in [(ax[0],aci,"ACI 209 extrapolation from 7 d"),(ax[1],p,"Gradient boosting (3 d, 7 d, mix)")]:
    a.scatter(f28[~hi],pp[~hi],s=8,color="#2b6cb0",label="SCM <= 30%"); a.scatter(f28[hi],pp[hi],s=8,color="#dd6b20",label="SCM > 30%")
    a.plot([20,75],[20,75],color="#2d3748",lw=1); a.set_title(t,fontsize=9); a.set_xlabel("Measured f'c 28 d (MPa)"); a.spines[["top","right"]].set_visible(False)
ax[0].set_ylabel("Predicted (MPa)"); ax[0].legend(frameon=False,fontsize=8); fig.tight_layout(); fig.savefig("fig/fig8_1_early.png",dpi=200)
# (2) maturity
E,R,Tr=40000,8.314,293.15
def true_strength(t,T): te=t*np.exp(-E/R*(1/(T+273.15)-1/Tr)); fu=50*(1-0.006*(T-20)); return fu*te/(3+te)
def nurse_saul(t,T): M=(T+10)*t; te20=M/30; return 50*te20/(3+te20)
for T in (10,20,35):
    print(f"T={T}C 7d true={true_strength(7,T):.1f} NS={nurse_saul(7,T):.1f} | 28d true={true_strength(28,T):.1f} NS={nurse_saul(28,T):.1f}")
# ML with temperature
ages=rng.choice([1,3,7,14,28],600); Ts=rng.uniform(8,38,600); fs=true_strength(ages,Ts)*rng.normal(1,0.04,600)
gbT=GradientBoostingRegressor(random_state=0).fit(np.c_[np.log(ages),Ts],fs)
for T in (10,35):
    print(f"ML T={T} 28d={gbT.predict([[np.log(28),T]])[0]:.1f}")
tt=np.linspace(0.5,28,200); fig,ax=plt.subplots(figsize=(6.5,3.5)); cols={10:"#2b6cb0",20:"#2d3748",35:"#c53030"}
for T in (10,20,35):
    ax.plot(tt,true_strength(tt,T),color=cols[T],lw=2,label=f"{T} °C true"); ax.plot(tt,nurse_saul(tt,T),color=cols[T],lw=1,ls="--")
ax.set_xlabel("Age (days)"); ax.set_ylabel("f'c (MPa)"); ax.legend(frameon=False,fontsize=8,title="dashed = Nurse-Saul",title_fontsize=8)
ax.spines[["top","right"]].set_visible(False); fig.tight_layout(); fig.savefig("fig/fig8_2_maturity.png",dpi=200)
# (3) chloride service life (Life-365-type relations)
def life(wbv,sg,cover_mm,Cs=0.6,Cc=0.05):
    D28=10**(-12.06+2.40*wbv)*31536000   # m2/yr
    m=0.2+0.4*(sg/70); m=min(m,0.6)
    t=np.arange(1,201)/1.0; x=cover_mm/1000
    tr=28/365; Dint=D28*tr**m*(t**(1-m))/(1-m)   # integral of D dt
    Cst=np.minimum(0.04*t,Cs)
    C=Cst*(1-erf(x/(2*np.sqrt(Dint))))
    k=np.argmax(C>=Cc); return t[k] if C.max()>=Cc else 200
for wbv,sg in [(0.50,0),(0.40,0),(0.40,50)]:
    print(f"w/b={wbv} slag={sg}% cover 50mm -> initiation {life(wbv,sg,50):.0f} yr")
# surrogate
import time
N=3000; S=np.c_[rng.uniform(0.35,0.6,N),rng.uniform(0,70,N),rng.uniform(30,75,N)]
t0=time.time(); L=np.array([life(*s) for s in S]); tsim=(time.time()-t0)/N
sur=GradientBoostingRegressor(n_estimators=400,random_state=0)
ps=cross_val_predict(sur,S,np.log(L),cv=KFold(5,shuffle=True,random_state=0))
print(f"surrogate log-life MAE={mean_absolute_error(np.log(L),ps):.3f} (≈{(np.exp(mean_absolute_error(np.log(L),ps))-1)*100:.0f}% typical error); sim time per case {tsim*1e3:.2f} ms")
sur.fit(S,np.log(L)); t0=time.time(); sur.predict(S); print(f"surrogate time per case {(time.time()-t0)/N*1e3:.4f} ms")
xx=np.linspace(0,100,200)/1000; fig,ax=plt.subplots(figsize=(6.5,3.4))
for (wbv,sg,c) in [(0.5,0,"#c53030"),(0.4,0,"#dd6b20"),(0.4,50,"#2b6cb0")]:
    D28=10**(-12.06+2.40*wbv)*31536000; m=min(0.2+0.4*sg/70,0.6); Dint=D28*(28/365)**m*25**(1-m)/(1-m)
    ax.plot(xx*1000,min(0.04*25,0.6)*(1-erf(xx/(2*np.sqrt(Dint)))),color=c,lw=2,label=f"w/b={wbv}, slag={sg}%")
ax.axhline(0.05,ls="--",color="#2d3748",lw=1); ax.axvline(50,ls=":",color="#2d3748",lw=1); ax.text(52,0.5,"cover 50 mm",fontsize=8); ax.text(80,0.06,"threshold",fontsize=8)
ax.set_xlabel("Depth (mm)"); ax.set_ylabel("Chloride (% by mass of concrete)"); ax.set_title("Profiles after 25 years",fontsize=9); ax.legend(frameon=False,fontsize=8)
ax.spines[["top","right"]].set_visible(False); fig.tight_layout(); fig.savefig("fig/fig8_3_chloride.png",dpi=200)
# (4) corrosion-bond (synthetic trend)
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel as C
c=rng.uniform(0,10,30)
trend=lambda c: np.where(c<1.5,1+0.12*c,1.18*np.exp(-0.15*(c-1.5)))
r=trend(c)*rng.normal(1,0.07,30)
gp=GaussianProcessRegressor(C(1)*RBF(2)+WhiteKernel(0.01),normalize_y=True,random_state=0).fit(c[:,None],r)
cg=np.linspace(0,12,200); mu,sd=gp.predict(cg[:,None],return_std=True)
for q in (1.5,5,12): m_,s_=gp.predict([[q]],return_std=True); print(f"corrosion {q}%: bond ratio {m_[0]:.2f} ± {1.96*s_[0]:.2f}")
fig,ax=plt.subplots(figsize=(6.5,3.3)); ax.fill_between(cg,mu-1.96*sd,mu+1.96*sd,color="#bee3f8"); ax.plot(cg,mu,color="#2b6cb0",lw=2,label="GPR mean ± 95%")
ax.scatter(c,r,s=14,color="#dd6b20",zorder=3,label="Pull-out tests (synthetic)"); ax.axhline(1,color="#a0aec0",lw=1)
ax.set_xlabel("Corrosion level (% mass loss)"); ax.set_ylabel("Bond strength ratio tau/tau0"); ax.legend(frameon=False,fontsize=8); ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig("fig/fig8_4_bond.png",dpi=200)
