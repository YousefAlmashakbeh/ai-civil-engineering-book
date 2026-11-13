import numpy as np, matplotlib, warnings; warnings.filterwarnings("ignore")
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from scipy.stats import norm
rng=np.random.default_rng(10)
# (1) USCS
n=800; LL=rng.uniform(15,90,n); PI=np.clip(0.73*(LL-20)+rng.normal(0,12,n),0,None); PI=np.minimum(PI,LL*0.9)
A=0.73*(LL-20)
def uscs(ll,pi,a):
    if ll<50:
        if pi>7 and pi>=a: return "CL"
        if 4<=pi<=7 and pi>=a: return "CL-ML"
        return "ML"
    return "CH" if pi>=a else "MH"
y=np.array([uscs(l,p,a) for l,p,a in zip(LL,PI,A)])
print({k:int((y==k).sum()) for k in np.unique(y)})
X=np.c_[LL,PI]; Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.3,random_state=0,stratify=y)
for d in (3,6,12):
    t=DecisionTreeClassifier(max_depth=d,random_state=0).fit(Xtr,ytr); print(f"tree depth {d}: test acc={t.score(Xte,yte):.3f} leaves={t.get_n_leaves()}")
Xe=np.c_[LL,PI,PI-0.73*(LL-20)]; Xetr,Xete,_,_=train_test_split(Xe,y,test_size=0.3,random_state=0,stratify=y)
te=DecisionTreeClassifier(max_depth=3,random_state=0).fit(Xetr,ytr); print(f"tree depth 3 + A-line feature: test acc={te.score(Xete,yte):.3f} leaves={te.get_n_leaves()}")
t6=DecisionTreeClassifier(max_depth=6,random_state=0).fit(Xtr,ytr)
gx,gy=np.meshgrid(np.linspace(15,90,400),np.linspace(0,70,300)); Z=t6.predict(np.c_[gx.ravel(),gy.ravel()]).reshape(gx.shape)
cls=["CH","CL","CL-ML","MH","ML"]; Zi=np.vectorize(cls.index)(Z)
fig,ax=plt.subplots(figsize=(6.5,4)); ax.contourf(gx,gy,Zi,levels=np.arange(-0.5,5),colors=["#fbd38d","#90cdf4","#c6f6d5","#fed7e2","#e2e8f0"],alpha=0.8)
ll=np.linspace(20,90,10); ax.plot(ll,0.73*(ll-20),color="#2d3748",lw=1.5); ax.axvline(50,color="#2d3748",lw=1.5)
for c in cls: ax.text(*{"CH":(70,45),"CL":(35,22),"CL-ML":(19,5.5),"MH":(70,12),"ML":(38,3)}[c],c,fontsize=9,weight="bold")
ax.set_xlabel("Liquid limit LL (%)"); ax.set_ylabel("Plasticity index PI (%)"); ax.set_title("Tree (depth 6) regions vs true A-line and LL=50",fontsize=9)
fig.tight_layout(); fig.savefig("fig/fig10_1_uscs.png",dpi=200)
# (2) kriging bedrock
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, WhiteKernel, ConstantKernel as C
def bedrock(x,y): return 6+3*np.sin(x/45)+2*np.cos(y/35)+1.5*np.exp(-((x-140)**2+(y-60)**2)/800)
bx=rng.uniform(0,200,25); by=rng.uniform(0,200,25); bz=bedrock(bx,by)+rng.normal(0,0.2,25)
gp=GaussianProcessRegressor(C(4)*Matern([50,50],nu=1.5)+WhiteKernel(0.05),normalize_y=True,random_state=0).fit(np.c_[bx,by],bz)
gx,gy=np.meshgrid(np.linspace(0,200,101),np.linspace(0,200,101)); G=np.c_[gx.ravel(),gy.ravel()]
mu,sd=gp.predict(G,return_std=True); err=np.abs(mu-bedrock(G[:,0],G[:,1]))
print(f"kriging: mean abs error={err.mean():.2f} m, max={err.max():.2f} m; max std={sd.max():.2f} m at",np.round(G[sd.argmax()],0))
inside=(sd<np.percentile(sd,50)); print(f"error where std below median={err[inside].mean():.2f} m ; above={err[~inside].mean():.2f} m")
cov=np.mean(np.abs(mu-bedrock(G[:,0],G[:,1]))<=1.96*sd); print(f"95% band coverage of true surface: {cov*100:.0f}%")
fig,ax=plt.subplots(1,2,figsize=(8.5,3.6))
c0=ax[0].contourf(gx,gy,mu.reshape(gx.shape),20,cmap="viridis"); fig.colorbar(c0,ax=ax[0],label="Depth to rock (m)")
c1=ax[1].contourf(gx,gy,sd.reshape(gx.shape),20,cmap="magma_r"); fig.colorbar(c1,ax=ax[1],label="Std (m)")
for a in ax: a.plot(bx,by,"wo",ms=4,mec="k"); a.set_xlabel("x (m)"); a.set_aspect("equal")
ax[0].set_ylabel("y (m)"); ax[1].plot(*G[sd.argmax()],"r*",ms=14,mec="k"); ax[0].set_title("Kriged depth",fontsize=9); ax[1].set_title("Uncertainty; star = next borehole",fontsize=9)
fig.tight_layout(); fig.savefig("fig/fig10_2_kriging.png",dpi=200)
# (3) infinite slope Monte Carlo
z,g,gw=2.0,19.0,9.81
def FS(beta,c,phi,m): b=np.radians(beta); return c/(g*z*np.sin(b)*np.cos(b))+(1-m*gw/g)*np.tan(np.radians(phi))/np.tan(b)
N=200000; betas=np.arange(26,49,2); pf=[]
s_ln=np.sqrt(np.log(1+0.4**2)); c=np.exp(rng.normal(np.log(8)-s_ln**2/2,s_ln,N)); phi=rng.normal(34,3,N); m=rng.uniform(0,0.8,N)
for bt in betas:
    f=FS(bt,c,phi,m); pf.append(np.mean(f<1))
    if bt in (32,36,40): print(f"slope {bt}°: FS(mean values)={FS(bt,8,34,0.4):.2f}  Pf={np.mean(f<1)*100:.2f}%  beta_R={-norm.ppf(max(np.mean(f<1),1e-6)):.2f}")
# surrogate classifier
from sklearn.ensemble import HistGradientBoostingClassifier
Ns=20000; B=rng.uniform(20,40,Ns); cc=np.exp(rng.normal(np.log(8)-s_ln**2/2,s_ln,Ns)); pp=rng.normal(34,3,Ns); mm=rng.uniform(0,0.8,Ns)
lab=(FS(B,cc,pp,mm)<1).astype(int); clf=HistGradientBoostingClassifier(random_state=0).fit(np.c_[B,cc,pp,mm],lab)
for bt in (32,36,40):
    pr=clf.predict(np.c_[np.full(N,bt),c,phi,m]).mean(); print(f"surrogate Pf at {bt}°: {pr*100:.2f}%")
fig,ax=plt.subplots(figsize=(6,3.3)); ax.semilogy(betas,np.maximum(pf,1e-5)*100,"o-",color="#c53030"); ax.axhline(1,ls="--",color="#a0aec0"); ax.text(26.5,1.2,"1% target",fontsize=8)
ax.set_xlabel("Slope angle (deg)"); ax.set_ylabel("Probability of failure (%)"); ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig("fig/fig10_3_slope.png",dpi=200)
