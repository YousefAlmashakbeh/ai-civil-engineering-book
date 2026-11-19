import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from scipy.stats import norm
# Ch1 figure (same data/model as example 1.1)
rng = np.random.default_rng(42); n=300
wc = rng.uniform(0.35,0.70,n); age = rng.choice([7,14,28,56],n)
A,B=96.5,7.0
fc = A/B**wc*age/(4+0.85*age)*rng.normal(1.0,0.07,n)
X=np.column_stack([wc,age]); Xtr,Xte,ytr,yte=train_test_split(X,fc,test_size=0.2,random_state=0)
m=RandomForestRegressor(n_estimators=300,random_state=0).fit(Xtr,ytr)
from sklearn.metrics import mean_absolute_error
print("MAE =", round(mean_absolute_error(yte, m.predict(Xte)), 2), "MPa")          # printed output of Example 1.1
for w in (0.45, 0.30): print(f"w/c={w}: ML={m.predict([[w, 28]])[0]:.1f}  Abrams={A/B**w*28/(4+0.85*28):.1f}")
g=np.linspace(0.25,0.80,200); phys=A/B**g*28/(4+0.85*28)
ml=m.predict(np.column_stack([g,np.full_like(g,28)]))
fig,ax=plt.subplots(figsize=(6.5,3.6))
ax.axvspan(0.35,0.70,facecolor="#edf2f7",edgecolor="#A0AEC0",lw=0.8,label="Training range")
sel=age==28; ax.scatter(wc[sel],fc[sel],s=10,color="#a0aec0",label="Data (28 d)")
ax.plot(g,phys,color="#2d3748",lw=2,label="Abrams law (physics)")
ax.plot(g,ml,color="#dd6b20",lw=2,label="Random forest")
ax.set_xlabel("w/c"); ax.set_ylabel("f'c at 28 d (MPa)"); ax.legend(frameon=False,fontsize=8)
ax.spines[["top","right"]].set_visible(False); fig.tight_layout(); fig.savefig("fig/fig1_1_extrap.png",dpi=200)
# Ch2 cube histogram
rng=np.random.default_rng(7); cubes=rng.normal(38.0,4.0,40).round(1)
mu,s=cubes.mean(),cubes.std(ddof=1); fk=mu-1.645*s
fig,ax=plt.subplots(figsize=(6.5,3.4))
ax.hist(cubes,bins=10,density=True,color="#bee3f8",edgecolor="white")
xx=np.linspace(24,50,300); ax.plot(xx,norm.pdf(xx,mu,s),color="#2b6cb0",lw=2)
ax.axvline(fk,color="#c53030",ls="--"); ax.text(fk+0.3,ax.get_ylim()[1]*0.9,f"fk = {fk:.1f}",ha="left",color="#c53030")
ax.axvline(30,color="#2d3748",ls=":"); ax.text(29.7,ax.get_ylim()[1]*0.75,"spec 30",ha="right",color="#2d3748")
ax.set_xlabel("Cube strength (MPa)"); ax.set_ylabel("Density"); ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig("fig/fig2_1_cubes.png",dpi=200)
# Ch2 GD loss
rng=np.random.default_rng(42); wc=rng.uniform(0.35,0.70,60); y=np.log(96.5/7.0**wc*rng.normal(1,0.05,60))
a,b,lr=3.0,0.0,0.5; L=[]
for it in range(4001):
    e=(a-b*wc)-y; L.append((e**2).mean()); a,b=a-lr*2*e.mean(), b+lr*2*(e*wc).mean()
fig,ax=plt.subplots(figsize=(6.5,3.2)); ax.semilogy(L,color="#2b6cb0",lw=2)
ax.set_xlabel("Iteration"); ax.set_ylabel("Mean squared error (log)"); ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig("fig/fig2_2_gd.png",dpi=200)
print("ok")
