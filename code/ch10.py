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
fig,ax=plt.subplots(1,2,figsize=(5.6,2.7))
c0=ax[0].contourf(gx,gy,mu.reshape(gx.shape),20,cmap="viridis"); cb0=fig.colorbar(c0,ax=ax[0],shrink=0.9); cb0.ax.tick_params(labelsize=8)
c1=ax[1].contourf(gx,gy,sd.reshape(gx.shape),20,cmap="magma_r"); cb1=fig.colorbar(c1,ax=ax[1],shrink=0.9); cb1.ax.tick_params(labelsize=8)
for a in ax: a.plot(bx,by,"wo",ms=4,mec="k"); a.set_xlabel("x (m)"); a.set_aspect("equal")
ax[0].set_ylabel("y (m)"); ax[1].plot(*G[sd.argmax()],"r*",ms=13,mec="k",clip_on=False,zorder=6); ax[0].set_title("Kriged depth to rock (m)",fontsize=8.6); ax[1].set_title("Std (m); star: next hole",fontsize=8.6)
for a in ax: a.set_xlim(-6,206); a.set_ylim(-6,206); a.tick_params(labelsize=8)
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
# Figure 10.4: seasonal mean (as Table 10.1), wet season (m=0.8) and dry season (m=0), same samples as ch10_wet.py
rng2=np.random.default_rng(0); c2=np.exp(rng2.normal(np.log(8)-s_ln**2/2,s_ln,N)); phi2=rng2.normal(34,3,N)
bb=np.arange(22,41,1.0); wet=np.array([np.mean(FS(b_,c2,phi2,0.8)<1) for b_ in bb]); dry=np.array([np.mean(FS(b_,c2,phi2,0.0)<1) for b_ in bb])
mb=np.r_[22,24,betas[betas<=40]]; mp=np.r_[[np.mean(FS(b_,c,phi,m)<1) for b_ in (22,24)],np.array(pf)[betas<=40]]
fig,ax=plt.subplots(figsize=(5.6,3.2)); ok=mp>0; ax.semilogy(mb[ok],mp[ok]*100,"o-",color="#c53030",lw=1.6,ms=4,label="Seasonal mean (Table 10.1)")
ax.semilogy(bb[wet>0],wet[wet>0]*100,"-",color="#1A365D",lw=1.8,label="Wet season (m = 0.8)")
ax.semilogy(bb[dry>0],dry[dry>0]*100,"--",color="#718096",lw=1.4,label="Dry season (m = 0)")
ax.axhline(1,ls="--",color="#a0aec0",lw=0.9); ax.text(39.8,1.12,"1% target",fontsize=8.6,ha="right",va="bottom",color="#4A5568")
xw=np.interp(np.log10(1),np.log10(wet[wet>0]*100),bb[wet>0]); xm=np.interp(np.log10(1),np.log10(mp[ok]*100),mb[ok])
for xx,t,col in ((xw,f"≈{xw:.1f}°\nwet season","#1A365D"),(xm,f"≈{xm:.1f}° seasonal mean","#c53030")):
    ax.annotate(t,xy=(xx,1),xytext=(23.4 if col=="#1A365D" else xx,3.0 if col=="#1A365D" else 0.035),ha="center",fontsize=8.6,color=col,arrowprops=dict(arrowstyle="-|>",color=col,lw=1))
ax.set_xlim(22,40); ax.set_ylim(0.01,100); ax.set_yticks([0.01,0.1,1,10,100]); ax.set_yticklabels(["0.01%","0.1%","1%","10%","100%"])
ax.set_xlabel("Slope angle (deg)"); ax.set_ylabel("Probability of failure"); ax.spines[["top","right"]].set_visible(False); ax.legend(fontsize=8.6,frameon=False,loc="upper left")
print("fig10.4 crossings: wet %.1f deg, seasonal mean %.1f deg; wet Pf at 40 deg %.1f%%"%(xw,xm,wet[-1]*100))
fig.tight_layout(); fig.savefig("fig/fig10_4_slope.png",dpi=200)
