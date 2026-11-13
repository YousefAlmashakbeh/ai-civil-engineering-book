import numpy as np, torch, torch.nn as nn, matplotlib, warnings; warnings.filterwarnings("ignore")
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import hilbert
rng=np.random.default_rng(13); torch.manual_seed(0); torch.set_num_threads(2)
# (1) environmental effects
days=np.arange(730); T=18+10*np.sin(2*np.pi*(days-110)/365)+rng.normal(0,3,730)
f=4.0*(1-0.0025*(T-15)+0.00004*(T-15)**2)+rng.normal(0,0.004,730); f[500:]*=0.985
base=days<365; mu,sd=f[base].mean(),f[base].std()
raw_alarm=np.abs(f-mu)>3*sd
print(f"raw: seasonal range={f[base].max()-f[base].min():.3f} Hz, damage shift={4.0*0.015:.3f} Hz; alarms before day500={raw_alarm[365:500].sum()}, after={raw_alarm[500:].sum()}/230")
c=np.polyfit(T[base],f[base],2); res=f-np.polyval(c,T); rs=res[base].std()
lam=0.2; e=np.zeros(730); 
for i in range(730): e[i]=lam*res[i]+(1-lam)*(e[i-1] if i else 0)
L=3*rs*np.sqrt(lam/(2-lam)); alarm=np.abs(e)>L
first=days[500:][alarm[500:]][0]
print(f"residual std={rs:.4f} Hz; EWMA limit={L:.4f}; false alarms days365-499={alarm[365:500].sum()}; first alarm after damage: day {first} (delay {first-500} d); alarms after damage {alarm[500:].sum()}/230")
fig,ax=plt.subplots(2,1,figsize=(7.5,4.6),sharex=True)
ax[0].plot(days,f,".",ms=2,color="#2b6cb0"); ax[0].axvline(500,color="#c53030",ls="--"); ax[0].set_ylabel("f1 (Hz)"); ax[0].text(505,f.max()-0.01,"damage",color="#c53030",fontsize=8)
ax[1].plot(days,e,color="#2d3748",lw=1); ax[1].axhline(L,color="#c53030",ls=":"); ax[1].axhline(-L,color="#c53030",ls=":"); ax[1].axvline(500,color="#c53030",ls="--"); ax[1].axvspan(0,365,color="#edf2f7")
ax[1].set_ylabel("EWMA of residual (Hz)"); ax[1].set_xlabel("Day"); ax[1].text(10,L*1.3,"baseline year",fontsize=8)
for a in ax: a.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig("fig/fig13_1_shm.png",dpi=200)
# (2) ultrasonic pulse-echo
fs=1e6; n=1000; t=np.arange(n)/fs; V0=4000; H=0.40
def burst(t0,amp,fc=100e3,cyc=3):
    tt=t-t0; w=(tt>=0)&(tt<=cyc/fc); s=np.zeros(n); s[w]=amp*np.sin(2*np.pi*fc*tt[w])*np.hanning(w.sum()); return s
def ascan(r,defect):
    V=V0*r.normal(1,0.03); sig=burst(0,1.0)*0.3
    sig+=burst(2*H/V,0.35)
    d=np.nan; a=0
    if defect:
        d=r.uniform(0.08,0.30); a=r.uniform(0.03,0.3); sig+=burst(2*d/V,a)
    for _ in range(60): sig+=burst(r.uniform(20e-6,0.9e-3),r.normal(0,0.025))   # grain noise
    sig*=np.exp(-3000*t); sig+=r.normal(0,0.01,n); return sig,d,a
N=2000; S=np.zeros((N,n),np.float32); Y=np.zeros(N,int); Dd=np.full(N,np.nan); A=np.zeros(N)
for i in range(N):
    y=rng.random()<0.5; S[i],Dd[i],A[i]=ascan(rng,y); Y[i]=y
tr=np.arange(1500); te=np.arange(1500,2000)
# depth via TOF on envelope
def depth_tof(s,V=V0):
    env=np.abs(hilbert(s)); i0=int(40e-6*fs); i1=int(2*H/V*fs*0.95)
    k=i0+np.argmax(env[i0:i1]); return (k/fs-1.5/100e3)*V/2, env[k]   # subtract half burst duration
dep=np.array([depth_tof(s) for s in S[te]]); yt=Y[te]
from sklearn.linear_model import LogisticRegression
feat=lambda SS:np.array([np.log(depth_tof(s)[1]) for s in SS])[:,None]
lr=LogisticRegression().fit(feat(S[tr]),Y[tr]); pl=lr.predict(feat(S[te]))
print(f"feature (peak envelope) detector: acc={(pl==yt).mean():.3f} recall={pl[yt==1].mean():.3f} false alarm={pl[yt==0].mean():.3f}")
class Net(nn.Module):
    def __init__(s): super().__init__(); s.f=nn.Sequential(nn.Conv1d(1,16,15,padding=7),nn.ReLU(),nn.MaxPool1d(4),nn.Conv1d(16,32,9,padding=4),nn.ReLU(),nn.MaxPool1d(4),nn.Conv1d(32,32,9,padding=4),nn.ReLU(),nn.AdaptiveMaxPool1d(1)); s.h=nn.Linear(32,2)
    def forward(s,x): return s.h(s.f(x).flatten(1))
mdl=Net(); opt=torch.optim.Adam(mdl.parameters(),2e-3); lf=nn.CrossEntropyLoss()
sc=S.std(); Xt=torch.tensor(S[tr]/sc)[:,None]; Yt=torch.tensor(Y[tr])
for ep in range(15):
    perm=torch.randperm(len(Xt))
    for b in range(0,len(Xt),64):
        i=perm[b:b+64]; opt.zero_grad(); lf(mdl(Xt[i]),Yt[i]).backward(); opt.step()
with torch.no_grad(): pc=mdl(torch.tensor(S[te]/sc)[:,None]).argmax(1).numpy()
print(f"1D-CNN detector: acc={(pc==yt).mean():.3f} recall={pc[yt==1].mean():.3f} false alarm={pc[yt==0].mean():.3f}")
at=A[te]
for lo,hi in [(0.03,0.08),(0.08,0.15),(0.15,0.3)]:
    s=(yt==1)&(at>=lo)&(at<hi); print(f"echo amp {lo}-{hi}: recall feature={pl[s].mean():.2f} CNN={pc[s].mean():.2f} n={s.sum()}")
det=(yt==1)&(pc==1); err=np.abs(dep[det,0]-Dd[te][det])*1000
print(f"TOF depth on CNN-detected defects: median abs error={np.median(err):.1f} mm, 90th pct={np.percentile(err,90):.1f} mm")
print(f"effect of 5% velocity error on 200 mm depth: {0.2*0.05*1000:.0f} mm")
# UPV dynamic modulus
rho,nu,V=2400,0.2,4000; Ed=rho*V**2*(1+nu)*(1-2*nu)/(1-nu); print(f"dynamic E from UPV 4000 m/s: {Ed/1e9:.1f} GPa")
fig,ax=plt.subplots(1,2,figsize=(8.5,3.2))
i1=te[np.where((yt==1)&(at>0.2))[0][0]]; i0=te[np.where(yt==0)[0][0]]
ax[0].plot(t*1e6,S[i0]+0.4,color="#2d3748",lw=0.8); ax[0].plot(t*1e6,S[i1],color="#2b6cb0",lw=0.8)
ax[0].axvline(2*Dd[i1]/V0*1e6,color="#c53030",ls=":"); ax[0].set_xlim(0,260); ax[0].set_xlabel("Time (µs)"); ax[0].set_yticks([]); ax[0].set_title("A-scans: sound (top) / with defect (bottom)",fontsize=9)
ax[1].scatter(Dd[te][det]*1000,dep[det,0]*1000,s=8,color="#2b6cb0"); ax[1].plot([80,300],[80,300],color="#2d3748",lw=1)
ax[1].set_xlabel("True defect depth (mm)"); ax[1].set_ylabel("TOF depth (mm)")
for a in ax: a.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig("fig/fig13_2_ultrasonic.png",dpi=200)
