import numpy as np, matplotlib, warnings; warnings.filterwarnings("ignore")
matplotlib.use("Agg"); import matplotlib.pyplot as plt
fc,fy,Mu=28.0,420.0,250.0  # MPa, MPa, kN.m
beta1=0.85; rmin=max(0.25*np.sqrt(fc)/fy,1.4/fy); rmax=0.85*beta1*fc/fy*0.003/0.008
def cost(b,h,As):  # JD per metre
    return 80*b*h/1e6 + 7850*As/1e6*1.1 + 12*(b+2*h)/1000
def phiMn(b,h,As):
    d=h-60; a=As*fy/(0.85*fc*b); return 0.9*As*fy*(d-a/2)/1e6
def penalised(x):
    b,h,As=x; d=h-60; rho=As/(b*d); p=0
    p+=max(0,Mu-phiMn(b,h,As))*1.0; p+=max(0,rmin-rho)*1e4; p+=max(0,rho-rmax)*1e4
    return cost(b,h,As)+p
# brute force reference
best=(1e9,None)
for b in range(200,401,50):
    for h in range(300,801,50):
        d=h-60
        for As in np.arange(200,6000,5):
            rho=As/(b*d)
            if rho<rmin or rho>rmax: continue
            if phiMn(b,h,As)>=Mu: 
                c=cost(b,h,As); best=min(best,(c,(b,h,As))); break
print("grid optimum: cost=%.2f JD/m b=%d h=%d As=%.0f"%(best[0],*best[1]))
# GA
rng=np.random.default_rng(0); lo=np.array([200,300,200]); hi=np.array([400,800,6000])
def snap(P): P[:,0]=np.round(P[:,0]/50)*50; P[:,1]=np.round(P[:,1]/50)*50; return np.clip(P,lo,hi)
P=snap(lo+rng.random((40,3))*(hi-lo)); hist=[]
for gen in range(80):
    F=np.array([penalised(x) for x in P]); hist.append(F.min())
    new=[P[F.argmin()].copy()]
    while len(new)<40:
        i,j=rng.integers(0,40,2); a=P[i] if F[i]<F[j] else P[j]
        i,j=rng.integers(0,40,2); bb=P[i] if F[i]<F[j] else P[j]
        w=rng.random(3); c=w*a+(1-w)*bb
        mut=rng.random(3)<0.2; c[mut]+=rng.normal(0,0.1,3)[mut]*(hi-lo)[mut]
        new.append(c)
    P=snap(np.array(new))
F=np.array([penalised(x) for x in P]); xb=P[F.argmin()]
print("GA optimum: cost=%.2f b=%d h=%d As=%.0f phiMn=%.1f evaluations=%d"%(cost(*xb),xb[0],xb[1],xb[2],phiMn(*xb),80*40))
from scipy.optimize import differential_evolution
r=differential_evolution(lambda x: penalised(snap(x.reshape(1,3).copy())[0]),list(zip(lo,hi)),seed=0,tol=1e-8,maxiter=200)
xd=snap(r.x.reshape(1,3).copy())[0]; print("DE optimum: cost=%.2f b=%d h=%d As=%.0f nfev=%d"%(cost(*xd),xd[0],xd[1],xd[2],r.nfev))
fig,ax=plt.subplots(figsize=(6,3)); ax.plot(hist,color="#2b6cb0",lw=2); ax.axhline(best[0],ls="--",color="#2d3748",lw=1); ax.text(55,best[0]+0.6,"grid optimum",fontsize=8)
ax.set_xlabel("Generation"); ax.set_ylabel("Best cost (JD/m)"); ax.set_ylim(best[0]-2,best[0]+15); ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig("fig/fig7_1_ga.png",dpi=200)
# Pareto
rng=np.random.default_rng(1); N=20000
binder=rng.uniform(280,500,N); fa=rng.uniform(0,0.6,N); wb=rng.uniform(0.33,0.6,N)
cem=binder*(1-fa); fly=binder*fa; wbe=wb*binder/(cem+0.8*fly)
f28=110/6.5**wbe; ok=f28>=35
C=0.09*cem+0.12*fly; E=0.9*cem+0.07*fly
c,e=C[ok],E[ok]; o=np.argsort(c); front=[]; emin=1e9
for k in o:
    if e[k]<emin: front.append(k); emin=e[k]
front=np.array(front)
print("feasible mixes:",ok.sum()," Pareto points:",len(front))
iC=front[0]; iE=front[-1]
idx=np.where(ok)[0]
mid=front[len(front)//2]
for name,k in [("min cost",iC),("balanced",mid),("min CO2",iE)]:
    g=idx[k]; print(f"{name}: binder={binder[g]:.0f} slag={fa[g]*100:.0f}% w/b={wb[g]:.2f} cost={C[g]:.1f} JD/m3 CO2={E[g]:.0f} kg/m3 f28={f28[g]:.1f}")
fig,ax=plt.subplots(figsize=(6,3.6)); ax.scatter(c,e,s=2,color="#cbd5e0",label="Feasible mixes (f'c >= 35 MPa)")
ax.plot(c[front],e[front],color="#c53030",lw=2,label="Pareto front"); ax.set_xlabel("Material cost (JD/m3)"); ax.set_ylabel("Embodied CO2 (kg/m3)")
ax.legend(frameon=False,fontsize=8); ax.spines[["top","right"]].set_visible(False); fig.tight_layout(); fig.savefig("fig/fig7_2_pareto.png",dpi=200)
# Bayesian optimisation: find w/b giving 40 MPa
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel as Ck
from scipy.stats import norm
rng=np.random.default_rng(3); lab=lambda w: 110/6.5**w*rng.normal(1,0.03)
obj=lambda f: -abs(f-40)
X=[0.35,0.60]; Y=[obj(lab(x)) for x in X]; grid=np.linspace(0.3,0.7,401)
for it in range(5):
    gp=GaussianProcessRegressor(Ck(10)*RBF(0.1)+WhiteKernel(0.5),normalize_y=True,random_state=0).fit(np.array(X)[:,None],Y)
    mu,sd=gp.predict(grid[:,None],return_std=True); best_y=max(Y); z=(mu-best_y)/(sd+1e-9)
    ei=(mu-best_y)*norm.cdf(z)+sd*norm.pdf(z); xn=grid[ei.argmax()]
    X.append(xn); Y.append(obj(lab(xn)))
    print(f"test {len(X)}: w/b={xn:.3f}  |f-40|={-Y[-1]:.2f} MPa")
true=np.log(110/40)/np.log(6.5); print("true w/b for 40 MPa:",round(true,3))
fig,ax=plt.subplots(figsize=(6,3.2)); ax.plot(grid,110/6.5**grid,color="#2d3748",lw=1.5,label="True strength law")
ax.axhline(40,ls="--",color="#a0aec0"); ax.scatter(X,[110/6.5**x for x in X],color="#dd6b20",zorder=3)
for k,x in enumerate(X): ax.annotate(str(k+1),(x,110/6.5**x),textcoords="offset points",xytext=(4,4),fontsize=8)
ax.set_xlabel("w/b"); ax.set_ylabel("f'c 28 d (MPa)"); ax.legend(frameon=False,fontsize=8); ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig("fig/fig7_3_bo.png",dpi=200)
# Q-learning maintenance
S=5; A=3; cost_a=[0,20,100]; fail=500; p=0.2; gam=0.95
def step(s,a,r):
    if a==2: s2=0
    elif a==1: s2=max(0,s-2)
    else: s2=s
    if s2<S-1 and r.random()<p: s2+=1
    c=cost_a[a]+(fail if s2==S-1 else 0)
    return s2,c
r=np.random.default_rng(0); Q=np.zeros((S,A)); s=0
for t in range(300000):
    a=r.integers(A) if r.random()<0.2 else Q[s].argmin()
    s2,c=step(s,a,r); Q[s,a]+=0.02*(c+gam*Q[s2].min()-Q[s,a]); s=s2
V=np.zeros(S)
for _ in range(2000):
    Qv=np.zeros((S,A))
    for s_ in range(S):
        for a in range(A):
            base=0 if a==2 else (max(0,s_-2) if a==1 else s_)
            for s2,pr in ([(base,1-p),(base+1,p)] if base<S-1 else [(base,1.0)]):
                Qv[s_,a]+=pr*(cost_a[a]+(fail if s2==S-1 else 0)+gam*V[s2])
    V=Qv.min(1)
names=["do nothing","repair","replace"]
print("state | Q-learning policy | value-iteration policy")
for s_ in range(S): print(s_+1, names[Q[s_].argmin()], names[Qv[s_].argmin()])
