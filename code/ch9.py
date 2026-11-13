import numpy as np, matplotlib, time, warnings; warnings.filterwarnings("ignore")
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.model_selection import KFold, cross_val_predict
from xgboost import XGBRegressor
rng=np.random.default_rng(9)
# (1) plane frame FE
def frame_k(E,A,I,x1,y1,x2,y2):
    L=np.hypot(x2-x1,y2-y1); c=(x2-x1)/L; s=(y2-y1)/L
    k=np.array([[E*A/L,0,0,-E*A/L,0,0],[0,12*E*I/L**3,6*E*I/L**2,0,-12*E*I/L**3,6*E*I/L**2],
                [0,6*E*I/L**2,4*E*I/L,0,-6*E*I/L**2,2*E*I/L],[-E*A/L,0,0,E*A/L,0,0],
                [0,-12*E*I/L**3,-6*E*I/L**2,0,12*E*I/L**3,-6*E*I/L**2],[0,6*E*I/L**2,2*E*I/L,0,-6*E*I/L**2,4*E*I/L]])
    T=np.zeros((6,6)); R=np.array([[c,s,0],[-s,c,0],[0,0,1]]); T[:3,:3]=R; T[3:,3:]=R
    return T.T@k@T
def portal_drift(L,h,Ic,Ib,H,E=25e6,nseg=8):
    # nodes along col1 (0,0)->(0,h), beam (0,h)->(L,h), col2 (L,h)->(L,0)
    pts=[(0,y) for y in np.linspace(0,h,nseg+1)]+[(x,h) for x in np.linspace(0,L,nseg+1)[1:]]+[(L,y) for y in np.linspace(h,0,nseg+1)[1:]]
    n=len(pts); K=np.zeros((3*n,3*n)); A=0.16
    for e in range(n-1):
        I=Ib if nseg<=e<2*nseg else Ic
        ke=frame_k(E,A,I,*pts[e],*pts[e+1]); idx=np.r_[3*e:3*e+3,3*e+3:3*e+6]; K[np.ix_(idx,idx)]+=ke
    F=np.zeros(3*n); F[3*nseg]=H
    free=np.setdiff1d(np.arange(3*n),np.r_[0,1,2,3*(n-1),3*(n-1)+1,3*(n-1)+2])
    u=np.zeros(3*n); u[free]=np.linalg.solve(K[np.ix_(free,free)],F[free]); return u[3*nseg]
# check vs hand formula: fixed-base portal with rigid beam: delta = H h^3/(24 E Ic)
d=portal_drift(6,3.5,0.002,1e3,50); print("FE rigid-beam drift (mm):",round(d*1000,3)," hand:",round(50*3.5**3/(24*25e6*0.002)*1000,3))
N=2000; P=np.c_[rng.uniform(4,10,N),rng.uniform(3,5,N),10**rng.uniform(-3.3,-2.3,N),10**rng.uniform(-3.3,-2.0,N),rng.uniform(10,100,N)]
t0=time.time(); D=np.array([portal_drift(*p) for p in P])*1000; tfe=(time.time()-t0)/N
Xr=P; Xl=np.log(P); y=np.log(D)
for name,X in [("raw inputs",Xr),("log inputs",Xl)]:
    p=cross_val_predict(XGBRegressor(n_estimators=600,max_depth=4,learning_rate=0.05,random_state=0),X,y,cv=KFold(5,shuffle=True,random_state=0))
    err=np.abs(np.exp(p)-D)/D; print(f"surrogate ({name}): median error={np.median(err)*100:.1f}%  95th pct={np.percentile(err,95)*100:.1f}%")
from sklearn.linear_model import LinearRegression
lr=cross_val_predict(LinearRegression(),Xl,y,cv=KFold(5,shuffle=True,random_state=0)); err=np.abs(np.exp(lr)-D)/D
print(f"log-linear (power law): median error={np.median(err)*100:.1f}%  95th={np.percentile(err,95)*100:.1f}%")
coef=LinearRegression().fit(Xl,y).coef_; print("power-law exponents L,h,Ic,Ib,H:",np.round(coef,2))
print(f"FE time per run {tfe*1000:.2f} ms")
fig,ax=plt.subplots(figsize=(4.6,4.3)); ax.loglog(D,np.exp(p),".",ms=3,color="#2b6cb0"); lim=[D.min()*0.8,D.max()*1.2]
ax.plot(lim,lim,color="#2d3748",lw=1); ax.set_xlabel("FE drift (mm)"); ax.set_ylabel("Surrogate drift (mm)"); ax.set_title("XGBoost surrogate, log inputs",fontsize=9); ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig("fig/fig9_1_surrogate.png",dpi=200)
# (2) shear without stirrups
n=400; fc=rng.uniform(20,60,n); rho=rng.uniform(0.005,0.035,n); d=rng.uniform(150,1200,n); ad=rng.uniform(2.5,6,n); bw=rng.uniform(150,400,n)
lam=np.minimum(1,np.sqrt(2/(1+d/250)))
vtrue=2.17*(fc*rho/ad)**(1/3)*lam*np.exp(rng.normal(0,0.12,n))   # labelled synthetic mechanics model (Zsutty form + size effect)
Vtest=vtrue*bw*d/1000
Vaci=0.66*lam*rho**(1/3)*np.sqrt(fc)*bw*d/1000
X=np.c_[fc,rho,d,ad,bw]; px=cross_val_predict(XGBRegressor(n_estimators=500,max_depth=3,learning_rate=0.05,random_state=0),np.log(X),np.log(Vtest),cv=KFold(5,shuffle=True,random_state=0))
rA=Vtest/Vaci; rX=Vtest/np.exp(px)
for nm,r in [("ACI 318-19",rA),("XGBoost",rX)]: print(f"{nm}: mean Vtest/Vpred={r.mean():.2f} COV={r.std()/r.mean()*100:.0f}% unsafe(<1)={np.mean(r<1)*100:.0f}%")
hiad=ad>4.5; print("ACI mean ratio a/d<3:",round(rA[ad<3].mean(),2)," a/d>4.5:",round(rA[hiad].mean(),2))
fig,ax=plt.subplots(figsize=(6,3.3)); ax.scatter(ad,rA,s=8,color="#dd6b20",label="ACI 318-19"); ax.scatter(ad,rX,s=8,color="#2b6cb0",label="XGBoost")
ax.axhline(1,color="#2d3748",lw=1); ax.set_xlabel("Shear span ratio a/d"); ax.set_ylabel("V_test / V_pred"); ax.legend(frameon=False,fontsize=8); ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig("fig/fig9_2_shear.png",dpi=200)
# (3) fragility
def ground_motion(pga,r,dt=0.01,T=20):
    t=np.arange(0,T,dt); w=r.normal(0,1,t.size)
    wg,zg=2*np.pi*2.5,0.6   # Kanai-Tajimi filter (firm soil)
    x=np.zeros(2); out=np.zeros(t.size)
    for i in range(t.size):
        a=-2*zg*wg*x[1]-wg**2*x[0]+w[i]/np.sqrt(dt); x=x+dt*np.array([x[1],a]); out[i]=-2*zg*wg*x[1]-wg**2*x[0]
    env=np.minimum(1,t/2)*np.exp(-0.25*np.maximum(0,t-8)); g=out*env; return t,g/np.abs(g).max()*pga*9.81
def sdof(ag,dt=0.01,T=0.5,z=0.05,Cy=0.15,h=3.5,alpha=0.05):
    wn=2*np.pi/T; k=wn**2; fy=Cy*9.81; uy=fy/k; u=v=0; fs=0; umax=0
    for a in ag:
        acc=-a-2*z*wn*v-fs; v+=acc*dt; du=v*dt; u+=du
        fs_trial=fs+k*du; fmax=fy+alpha*k*(u-np.sign(u)*uy)
        fs=fs_trial if abs(fs_trial)<=abs(fy)+alpha*k*max(0,abs(u)-uy) else np.sign(fs_trial)*(fy+alpha*k*max(0,abs(u)-uy))
        umax=max(umax,abs(u))
    return umax/h
pgas=np.exp(rng.uniform(np.log(0.05),np.log(0.8),200)); drift=np.array([sdof(ground_motion(p,rng)[1]) for p in pgas])
ex=(drift>0.01).astype(int); print("records exceeding 1% drift:",ex.sum(),"/",len(ex))
from scipy.optimize import minimize
from scipy.stats import norm
nll=lambda th: -np.sum(ex*np.log(norm.cdf((np.log(pgas)-th[0])/abs(th[1]))+1e-12)+(1-ex)*np.log(1-norm.cdf((np.log(pgas)-th[0])/abs(th[1]))+1e-12))
th=minimize(nll,[np.log(0.3),0.5],method="Nelder-Mead").x; med=np.exp(th[0]); beta=abs(th[1])
print(f"fragility: median PGA={med:.2f} g, beta={beta:.2f}; P(exceed|PGA=0.3g)={norm.cdf((np.log(0.3)-th[0])/beta)*100:.0f}%")
fig,ax=plt.subplots(1,2,figsize=(8,3.2))
ax[0].loglog(pgas,drift*100,".",color="#2b6cb0",ms=4); ax[0].axhline(1,color="#c53030",ls="--",lw=1); ax[0].set_xlabel("PGA (g)"); ax[0].set_ylabel("Peak drift ratio (%)")
g=np.linspace(0.03,0.9,200); ax[1].plot(g,norm.cdf((np.log(g)-th[0])/beta),color="#c53030",lw=2); ax[1].plot(pgas,ex,"|",color="#a0aec0")
ax[1].set_xlabel("PGA (g)"); ax[1].set_ylabel("P(drift > 1%)")
for a in ax: a.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig("fig/fig9_3_fragility.png",dpi=200)
