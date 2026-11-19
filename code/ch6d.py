import numpy as np, pandas as pd, torch, torch.nn as nn, matplotlib, warnings; warnings.filterwarnings("ignore")
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from ch5_data import make_concrete
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.metrics import mean_absolute_error, r2_score
df=make_concrete(); X=df.drop(columns=["fc","mix"]).copy(); X["log_age"]=np.log(X.pop("age")); y=df.fc.values; g=df.mix.values
for h in [(16,),(64,64)]:
    mlp=make_pipeline(StandardScaler(),MLPRegressor(hidden_layer_sizes=h,alpha=1e-3,max_iter=4000,early_stopping=True,random_state=0))
    p=cross_val_predict(mlp,X,y,cv=GroupKFold(5),groups=g)
    print(f"MLP {h}: MAE={mean_absolute_error(y,p):.2f} R2={r2_score(y,p):.3f}")
    # same network, but with the target standardised as well (TransformedTargetRegressor)
    from sklearn.compose import TransformedTargetRegressor
    p2=cross_val_predict(TransformedTargetRegressor(regressor=mlp,transformer=StandardScaler()),X,y,cv=GroupKFold(5),groups=g)
    print(f"MLP {h} + scaled target: MAE={mean_absolute_error(y,p2):.2f} R2={r2_score(y,p2):.3f}")
# traffic
torch.manual_seed(0); rng=np.random.default_rng(8)
hours=24*7*10; t=np.arange(hours); hod=t%24; dow=(t//24)%7   # dow 0=Sunday ... 5=Friday 6=Saturday
base=np.where(np.isin(dow,[5,6]),0.55,1.0)
prof=0.25+0.9*np.exp(-((hod-8)/1.5)**2)+0.8*np.exp(-((hod-16)/2.0)**2)+0.3*np.exp(-((hod-21)/2)**2)
vol=1800*base*prof*(1+0.06*rng.normal(size=hours)); vol[np.isin(dow,[5])&(hod>=11)&(hod<=13)]*=0.5  # Friday prayer dip
vol=vol.astype(np.float32)
L=24; Xs=np.stack([vol[i:i+L] for i in range(hours-L)]); ys=vol[L:]
s=vol[:24*7*8].max(); split=24*7*8-L   # scale from the training weeks only
Xtr,ytr,Xte,yte=Xs[:split]/s,ys[:split]/s,Xs[split:]/s,ys[split:]/s
class LSTM(nn.Module):
    def __init__(s_): super().__init__(); s_.l=nn.LSTM(1,32,batch_first=True); s_.o=nn.Linear(32,1)
    def forward(s_,x): h,_=s_.l(x[...,None]); return s_.o(h[:,-1]).squeeze(-1)
m=LSTM(); opt=torch.optim.Adam(m.parameters(),5e-3); Xt=torch.tensor(Xtr); Yt=torch.tensor(ytr)
for e in range(60):
    perm=torch.randperm(len(Xt))
    for b in range(0,len(Xt),128):
        i=perm[b:b+128]; opt.zero_grad(); l=((m(Xt[i])-Yt[i])**2).mean(); l.backward(); opt.step()
with torch.no_grad(): p=m(torch.tensor(Xte)).numpy()*s
yt=yte*s; naive=vol[split+L-168:hours-168]   # same hour last week
print(f"LSTM MAE={np.abs(p-yt).mean():.0f} veh/h ; seasonal-naive (last week) MAE={np.abs(naive-yt).mean():.0f} veh/h ; mean volume={yt.mean():.0f}")
fig,ax=plt.subplots(figsize=(8,3)); k=24*7
ax.plot(yt[:k],color="#2d3748",lw=1.2,label="Observed"); ax.plot(p[:k],color="#dd6b20",lw=1.2,label="LSTM 1-h ahead")
ax.set_xlabel("Hour of test week (starts Sunday)"); ax.set_ylabel("Volume (veh/h)"); ax.legend(frameon=False,fontsize=8); ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig("fig/fig6_4_lstm.png",dpi=200)
fig,ax=plt.subplots(figsize=(5.5,3))
vals=[0.996,0.055,0.366]; lab=["Test like training","Hairline field cracks","After fine-tuning\n(+200 hairline imgs)"]
ax.bar(lab,vals,color=["#2b6cb0","#c53030","#dd6b20"])
for i,v in enumerate(vals): ax.text(i,v+0.02,f"{v:.1%}",ha="center")
ax.set_ylabel("Recall (cracks found)"); ax.set_ylim(0,1.1); ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig("fig/fig6_3_shift.png",dpi=200)
