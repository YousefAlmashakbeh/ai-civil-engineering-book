# Additional worked examples, chapters 1-6
import numpy as np, pandas as pd, matplotlib, warnings; warnings.filterwarnings("ignore")
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.impute import KNNImputer
from sklearn.model_selection import GroupKFold, cross_val_predict, GroupShuffleSplit
from sklearn.tree import DecisionTreeRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error as mae
from ch5_data import make_concrete
B="#2b6cb0"; O="#dd6b20"; K="#2d3748"
def clean(ax): ax.spines[["top","right"]].set_visible(False)

# ---- Example 1.2: physics + data = hybrid, tested outside the training range
rng=np.random.default_rng(1); n=300
wc=rng.uniform(0.35,0.70,n); f28=96.5/7**wc      # Abrams' law, 28 days (as in Example 1.1)
air=rng.uniform(1.0,6.0,n)                       # entrained air (%), unknown to Abrams' law
y=f28*(1-0.05*(air-2))*np.exp(rng.normal(0,0.05,n))
X=np.c_[wc,air]
rf=RandomForestRegressor(300,random_state=0).fit(X,y)
phys=lambda w:96.5/7**w
hyb=RandomForestRegressor(300,random_state=0).fit(X,y/phys(wc))        # learn the ratio to physics
wt=np.array([0.30,0.50]); at=np.array([2.0,5.0])
for w in wt:
    for a in at:
        true=phys(w)*(1-0.05*(a-2)); print(f"Ex1.2 w/c={w:.2f} air={a:.0f}%: true={true:.1f}  Abrams={phys(w):.1f}  RF={rf.predict([[w,a]])[0]:.1f}  hybrid={phys(w)*hyb.predict([[w,a]])[0]:.1f}")
g=np.linspace(0.25,0.75,100); fig,ax=plt.subplots(figsize=(6,3.6))
ax.scatter(wc,y,s=6,color="0.75",label="tests (air 1-6%)")
ax.plot(g,phys(g)*(1-0.05*3),color=K,lw=1.5,label="truth at 5% air")
ax.plot(g,phys(g),"--",color="0.4",label="Abrams only")
ax.plot(g,rf.predict(np.c_[g,np.full(100,5.0)]),color=O,ls="-.",lw=1.4,label="random forest")
ax.plot(g,phys(g)*hyb.predict(np.c_[g,np.full(100,5.0)]),color=B,ls=(0,(1,1)),lw=2.2,label="hybrid (Abrams x RF ratio)")
ax.axvspan(0.25,0.35,color="#fff5f5"); ax.axvspan(0.70,0.75,color="#fff5f5"); ax.set_xlabel("w/c"); ax.set_ylabel("28-day strength (MPa)"); ax.legend(fontsize=7,frameon=False); clean(ax)
fig.tight_layout(); fig.savefig("fig/fig1_4_hybrid.png",dpi=200); plt.close()

# ---- Example 2.4: principal components of eight strain gauges on a bridge
rng=np.random.default_rng(24); days=np.arange(730); T=15+12*np.sin(2*np.pi*(days-110)/365)+rng.normal(0,2.5,730); L=rng.gamma(4,0.25,730)   # temperature, daily traffic load index
aT=rng.uniform(4,9,8); aL=rng.uniform(10,40,8); S=np.outer(T-15,aT)+np.outer(L,aL)+rng.normal(0,4,(730,8))      # microstrain, 8 gauges
S[600:,2]-=18                                                                                                    # from day 600 gauge 3 loses 18 microstrain (local damage)
sc2=StandardScaler().fit(S[:365]); p=PCA().fit(sc2.transform(S[:365]))
print("Ex2.4 explained variance:",np.round(p.explained_variance_ratio_,3),"first two=%.3f"%p.explained_variance_ratio_[:2].sum())
Zs=sc2.transform(S); rec=p.inverse_transform(np.c_[p.transform(Zs)[:,:2],np.zeros((730,6))]); q=((Zs-rec)**2).sum(1)      # residual outside the 2-component plane
thr=np.percentile(q[:365],99); print("  residual threshold (99%% of year 1)=%.2f; alarms days 365-599: %.1f%%; days 600-729: %.1f%%"%(thr,100*np.mean(q[365:600]>thr),100*np.mean(q[600:]>thr)))
print("  raw gauge 3, mean before/after day 600: %.1f / %.1f microstrain (sd of the raw signal %.1f)"%(S[365:600,2].mean(),S[600:,2].mean(),S[365:600,2].std()))
fig,ax=plt.subplots(1,2,figsize=(7.0,3.0),gridspec_kw=dict(width_ratios=[1,2]))
ev=p.explained_variance_ratio_; bb=ax[0].bar(range(1,9),ev,color=B); ax[0].set_yscale("log"); ax[0].set_ylim(ev.min()/2,2)
ax[0].bar_label(bb,labels=["%.1f%%"%(100*v) if i<2 else "" for i,v in enumerate(ev)],fontsize=7.5,padding=1); ax[0].set_xticks(range(1,9)); ax[0].set_xlabel("component"); ax[0].set_ylabel("explained variance (log)"); clean(ax[0])
ax[1].plot(days,q,color=B,lw=0.6); ax[1].axhline(thr,color="#c53030",ls="--",lw=0.9); ax[1].axvline(600,color="0.4",ls=":"); ax[1].axvspan(0,365,color="#edf2f7"); ax[1].set_yscale("log"); ax[1].set_xlabel("day"); ax[1].set_ylabel("residual outside 2 PCs")
ax[1].text(10,q.max()*0.6,"reference year",fontsize=7.5); ax[1].text(10,thr*1.25,"alarm threshold (99%)",fontsize=7.5,color="#c53030")
ax[1].annotate("gauge 3 drifts",xy=(600,thr*1.6),xytext=(430,q.max()*0.25),fontsize=7.5,arrowprops=dict(arrowstyle="->",lw=.7)); clean(ax[1])
fig.tight_layout(); fig.savefig("fig/fig2_3_pca.png",dpi=260); plt.close()
df=make_concrete(); V=["cement","slag","flyash","water","sp","coarse","fine"]

# ---- Example 3.3: borehole log -> SPT profile and design table
rng=np.random.default_rng(3); rows=[]
for bh,(x0,drift) in {"BH-1":(0,0),"BH-2":(25,3),"BH-3":(50,-2)}.items():
    for z in np.arange(1.5,21.1,1.5):
        base=6+1.6*z+drift if z<9 else 28+0.9*(z-9)+drift
        rows.append((bh,z,max(2,int(rng.normal(base,3))), "clay" if z<9 else "dense sand"))
log=pd.DataFrame(rows,columns=["borehole","depth_m","N","layer"])
log["N60"]=(log.N*0.60/0.60).round(1)                      # hammer efficiency 60%: no correction
sv=np.maximum(18*log.depth_m-9.81*np.maximum(log.depth_m-4,0),1); log["N1_60"]=(log.N60*np.minimum(np.sqrt(100/sv),1.7)).round(1)
tab=log.groupby("layer").agg(n=("N","size"),N_mean=("N","mean"),N_min=("N","min"),N1_60_mean=("N1_60","mean")).round(1); print("Ex3.3\n",tab.to_string())
print("  characteristic N1_60 (mean - 0.5 sd): clay=%.1f sand=%.1f"%tuple(log.groupby("layer").N1_60.agg(lambda s:s.mean()-0.5*s.std())[["clay","dense sand"]]))
fig,ax=plt.subplots(figsize=(3.6,4.6))
for (bh,gp),c,mk,ls_ in zip(log.groupby("borehole"),[B,O,"#38a169"],["o","s","^"],["-","--",":"]): ax.plot(gp.N,gp.depth_m,marker=mk,ls=ls_,ms=3.5,lw=1.1,color=c,label=bh)
ax.axhline(9,color="0.5",ls=":"); ax.text(60,8.6,"clay / sand",fontsize=7,ha="right"); ax.axhline(4,color=B,ls="--",lw=0.7); ax.text(60,3.7,"water table",fontsize=7,ha="right",color=B)
ax.invert_yaxis(); ax.set_xlabel("SPT N (blows / 300 mm)"); ax.set_ylabel("Depth (m)"); ax.legend(fontsize=7,frameon=False); clean(ax)
fig.tight_layout(); fig.savefig("fig/fig3_3_spt.png",dpi=200); plt.close()

# ---- Example 4.5: a physics check finds bad records that statistics miss
rng=np.random.default_rng(44); m4=df.drop_duplicates("mix")[V].reset_index(drop=True).copy()
sg={"cement":3.15,"slag":2.90,"flyash":2.30,"water":1.00,"sp":1.10,"coarse":2.65,"fine":2.62}                    # specific gravities
m4["coarse"]=(1000-20-sum(m4[v]/sg[v] for v in V if v!="coarse"))*sg["coarse"]                                    # close each mix to 1 m3 with 2% air
m4[V]*=rng.normal(1,0.004,m4[V].shape)                                                                             # weighing tolerance
bad=np.zeros(len(m4),bool); kinds=[]
for i in rng.choice(len(m4),12,replace=False):
    k=rng.choice(["fine<->coarse swapped","water +30 (typing)","cement -60 (typing)","sp x10 (unit)"]); bad[i]=True; kinds.append((i,k))
    if k.startswith("fine"): m4.loc[i,["fine","coarse"]]=m4.loc[i,["coarse","fine"]].values
    elif k.startswith("water"): m4.loc[i,"water"]+=30
    elif k.startswith("cement"): m4.loc[i,"cement"]-=60
    else: m4.loc[i,"sp"]*=10
vol=sum(m4[v]/sg[v] for v in V)+20                                                                                 # litres per m3, should be 1000
q1,q3=m4[V].quantile(0.25),m4[V].quantile(0.75); iqr_flag=((m4[V]<q1-1.5*(q3-q1))|(m4[V]>q3+1.5*(q3-q1))).any(axis=1).values
vol_flag=(np.abs(vol-1000)>10).values
def pr(f): tp=(f&bad).sum(); return tp,f.sum(),tp/max(f.sum(),1),tp/bad.sum()
for nm,f in [("IQR rule on each column",iqr_flag),("volume balance |V-1000|>10 L",vol_flag),("either",iqr_flag|vol_flag)]:
    tp,nf,pc,rc=pr(f); print(f"Ex4.5 {nm}: flagged {nf}, true errors found {tp} of {bad.sum()} (precision {pc:.2f}, recall {rc:.2f})")
for kind in sorted(set(k for _,k in kinds)):
    ii=[i for i,k in kinds if k==kind]; print(f"  {kind}: n={len(ii)}, volume error {np.round((vol-1000)[ii].values,0)} L, found by volume {int(vol_flag[ii].sum())}, by IQR {int(iqr_flag[ii].sum())}")
fig,ax=plt.subplots(figsize=(5.6,3.2)); ax.scatter(np.arange(len(m4))[~bad],vol[~bad],s=8,color="0.6",label="correct records"); ax.scatter(np.arange(len(m4))[bad],vol[bad],s=26,color="#c53030",marker="x",label="planted errors")
ax.axhline(1010,color=B,ls="--",lw=0.8); ax.axhline(990,color=B,ls="--",lw=0.8); ax.set_xlabel("Mix record"); ax.set_ylabel("Absolute volume (L per m3)"); ax.legend(frameon=False,fontsize=8); clean(ax)
fig.tight_layout(); fig.savefig("fig/fig4_3_volume.png",dpi=200); plt.close()
Xfull=df[V+["age"]].copy(); Xfull["log_age"]=np.log(Xfull.pop("age")); yc=df.fc.values; gmix=df.mix.values

# ---- Example 5.2: learning curve and model complexity (bias-variance)
X5=Xfull.values; tr,te=next(GroupShuffleSplit(1,test_size=0.3,random_state=0).split(X5,yc,gmix))
depths=[1,2,3,4,6,8,10,14,20]; etr=[];ete=[]
for dpt in depths:
    t=DecisionTreeRegressor(max_depth=dpt,random_state=0).fit(X5[tr],yc[tr]); etr.append(mae(yc[tr],t.predict(X5[tr]))); ete.append(mae(yc[te],t.predict(X5[te])))
print("Ex5.2 tree depth -> test MAE: {"+", ".join(f"{d}: {e:.2f}" for d,e in zip(depths,ete))+"}"); print(f"  train MAE at depth 20 = {etr[-1]:.2f}")
sizes=[20,40,80,160,320,len(tr)]; ltr=[];lte=[]; r5=np.random.default_rng(5); order=r5.permutation(tr)
for s in sizes:
    i=order[:s]; f=RandomForestRegressor(200,random_state=0).fit(X5[i],yc[i]); ltr.append(mae(yc[i],f.predict(X5[i]))); lte.append(mae(yc[te],f.predict(X5[te])))
print("  learning curve (rows -> test MAE): {"+", ".join(f"{s}: {e:.2f}" for s,e in zip(sizes,lte))+"}")
fig,ax=plt.subplots(1,2,figsize=(8,3.2))
ax[0].plot(depths,etr,"o-",color=B,label="training"); ax[0].plot(depths,ete,"s-",color=O,label="test"); ax[0].set_xlabel("Tree depth (model complexity)"); ax[0].set_ylabel("MAE (MPa)"); ax[0].legend(frameon=False,fontsize=8); clean(ax[0])
ax[1].plot(sizes,ltr,"o-",color=B,label="training"); ax[1].plot(sizes,lte,"s-",color=O,label="test"); ax[1].set_xscale("log"); ax[1].set_xticks(sizes[:-1]); ax[1].set_xticklabels(sizes[:-1],fontsize=7); ax[1].minorticks_off(); ax[1].annotate(str(sizes[-1]),(sizes[-1],lte[-1]),xytext=(0,7),textcoords="offset points",ha="center",fontsize=7,color=O); ax[1].set_xlabel("Training rows (random forest)"); ax[1].legend(frameon=False,fontsize=8); clean(ax[1])
fig.tight_layout(); fig.savefig("fig/fig5_4_biasvar.png",dpi=200); plt.close()

# ---- Example 6.5: sizes and parameter count of the crack CNN, layer by layer
import torch, torch.nn as nn
net=nn.Sequential(nn.Conv2d(1,16,3,padding=1),nn.BatchNorm2d(16),nn.ReLU(),nn.MaxPool2d(2),nn.Conv2d(16,32,3,padding=1),nn.BatchNorm2d(32),nn.ReLU(),nn.MaxPool2d(2),
                  nn.Conv2d(32,64,3,padding=1),nn.BatchNorm2d(64),nn.ReLU(),nn.AdaptiveMaxPool2d(1),nn.Flatten(),nn.Linear(64,2))
x=torch.zeros(1,1,64,64); tot=0
for layer in net:
    x=layer(x); n=sum(p.numel() for p in layer.parameters()); tot+=n
    if n or isinstance(layer,(nn.MaxPool2d,nn.AdaptiveMaxPool2d)): print(f"Ex6.5 {layer.__class__.__name__:18s} output {tuple(x.shape[1:])}  parameters {n}")
print("  total parameters:",tot,"| receptive field after conv3: 3 -> 8 -> 18 pixels (each pooling doubles the step)")
