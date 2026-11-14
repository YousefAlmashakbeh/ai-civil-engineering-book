# Additional worked examples, chapters 7-12
import numpy as np, matplotlib, warnings; warnings.filterwarnings("ignore")
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.optimize import differential_evolution
B="#2b6cb0"; O="#dd6b20"; K="#2d3748"; R="#c53030"
def clean(ax): ax.spines[["top","right"]].set_visible(False)

# ---- Example 7.5: the ten-bar truss benchmark with differential evolution
L=9.144; P=444.8e3; E=68.9e9; rho=2768.0; smax=172.4e6; dmax=0.0508
nodes=np.array([[2*L,L],[2*L,0],[L,L],[L,0],[0,L],[0,0]])
bars=[(4,2),(2,0),(5,3),(3,1),(2,3),(0,1),(4,3),(5,2),(2,1),(3,0)]
Lb=np.array([np.linalg.norm(nodes[j]-nodes[i]) for i,j in bars])
def analyse(A):
    Kg=np.zeros((12,12))
    for (i,j),a,l in zip(bars,A,Lb):
        c,s=(nodes[j]-nodes[i])/l; k=E*a/l*np.array([[c*c,c*s,-c*c,-c*s],[c*s,s*s,-c*s,-s*s],[-c*c,-c*s,c*c,c*s],[-c*s,-s*s,c*s,s*s]]); d=[2*i,2*i+1,2*j,2*j+1]; Kg[np.ix_(d,d)]+=k
    F=np.zeros(12); F[3]=-P; F[7]=-P; free=np.arange(8); u=np.zeros(12); u[free]=np.linalg.solve(Kg[np.ix_(free,free)],F[free])
    sig=np.array([E/l*np.dot((nodes[j]-nodes[i])/l,u[[2*j,2*j+1]]-u[[2*i,2*i+1]]) for (i,j),l in zip(bars,Lb)]); return u,sig
def weight(A): return rho*np.dot(A,Lb)
def cost(A):
    u,s=analyse(A); g=max(0,np.abs(s).max()/smax-1)+max(0,np.abs(u).max()/dmax-1); return weight(A)*(1+10*g)**2
u0,s0=analyse(np.full(10,0.01)); print("Ex7.5 uniform 100 cm2: weight=%.0f kg, max |stress|=%.0f MPa, max deflection=%.1f mm"%(weight(np.full(10,0.01)),np.abs(s0).max()/1e6,np.abs(u0).max()*1e3))
hist=[]
r=differential_evolution(cost,[(0.645e-4,225e-4)]*10,seed=0,popsize=20,maxiter=600,tol=1e-8,polish=True,callback=lambda xk,convergence: hist.append(cost(xk)))
u,s=analyse(r.x); print("  DE optimum: weight=%.0f kg (published optimum about 2295 kg), max |stress|=%.0f MPa, max deflection=%.1f mm, evaluations=%d"%(weight(r.x),np.abs(s).max()/1e6,np.abs(u).max()*1e3,r.nfev))
print("  areas (cm2):",np.round(r.x*1e4,1))
fig,ax=plt.subplots(1,2,figsize=(8.6,3.2),gridspec_kw={"width_ratios":[1.5,1]})
for (i,j),a in zip(bars,r.x): ax[0].plot(*zip(nodes[i],nodes[j]),color=B,lw=0.6+a*1e4/22,solid_capstyle="round")
ax[0].plot(nodes[:,0],nodes[:,1],"o",color=K,ms=4); ax[0].plot([0,0],[-0.5,L+0.5],color="0.4",lw=4)
for n_ in (1,3): ax[0].annotate("",xy=(nodes[n_][0],-2.2),xytext=(nodes[n_][0],-0.2),arrowprops=dict(arrowstyle="->",color=R)); ax[0].text(nodes[n_][0]+0.3,-1.6,"445 kN",fontsize=7,color=R)
ax[0].set_aspect("equal"); ax[0].axis("off"); ax[0].set_title("Optimum: line width = bar area",fontsize=9)
ax[1].plot(hist,color=O); ax[1].set_yscale("log"); ax[1].set_xlabel("Generation"); ax[1].set_ylabel("Penalised weight (kg)"); clean(ax[1])
fig.tight_layout(); fig.savefig("fig/fig7_4_truss.png",dpi=200); plt.close()

# ---- Example 8.5: when can the slab formwork be struck? (equivalent age)
Ea,Rg=40000.0,8.314; fu,tau,beta=44.0,30.0,0.75                # strength gain at 20 C: f = fu*exp(-(tau/te)^beta), te in hours
def strength(te): return fu*np.exp(-(tau/np.maximum(te,1e-6))**beta)
f28=strength(28*24); target=0.70*f28; t=np.arange(0,24*21+1.0)
prof={"winter night-day 4-14 C":9+5*np.sin(2*np.pi*(t-9)/24),"spring 14-26 C":20+6*np.sin(2*np.pi*(t-9)/24),"summer 26-42 C":34+8*np.sin(2*np.pi*(t-9)/24)}
fig,ax=plt.subplots(figsize=(6,3.4)); print("Ex8.5 f28 (20 C)=%.1f MPa, striking target 70%%=%.1f MPa"%(f28,target))
for (nm,T),c in zip(prof.items(),[B,"#38a169",O]):
    te=np.cumsum(np.exp(-Ea/Rg*(1/(273+T)-1/293))); f=strength(te); ts=t[np.argmax(f>=target)]/24
    print(f"  {nm}: strike after {ts:.1f} days (equivalent age {te[np.argmax(f>=target)]/24:.1f} days at 20 C)"); ax.plot(t/24,f,color=c,label=nm)
ax.axhline(target,color=R,ls="--",lw=0.8); ax.text(20.8,target+0.8,"70% of f28",fontsize=7,ha="right",color=R); ax.set_xlabel("Age (days)"); ax.set_ylabel("In-place strength (MPa)"); ax.legend(frameon=False,fontsize=8); clean(ax)
fig.tight_layout(); fig.savefig("fig/fig8_7_striking.png",dpi=200); plt.close()

# ---- Example 9.4: column interaction diagram by strain compatibility, and a checker
b=h=400.0; fc=30.0; fy=420.0; Es=200000.0; cover=60.0; Ab=314.0            # 8 bars of 20 mm, three layers (3-2-3)
layers=[(cover,3*Ab),(h/2,2*Ab),(h-cover,3*Ab)]; Ast=8*Ab; b1=0.85-0.05*(fc-28)/7
def point(c):
    a=min(b1*c,h); Pn=0.85*fc*a*b; Mn=0.85*fc*a*b*(h/2-a/2); et=0
    for d,As in layers:
        es=0.003*(c-d)/c; fs=np.clip(es*Es,-fy,fy); fs_net=fs-(0.85*fc if a>d else 0); Pn+=As*fs_net; Mn+=As*fs_net*(h/2-d); et=-es if d==h-cover else et
    phi=np.clip(0.65+0.25*(et-0.0021)/0.003,0.65,0.90); return Pn/1e3,Mn/1e6,phi
cs=np.r_[np.linspace(40,h,120),np.linspace(h,6*h,60)]; pts=np.array([point(c) for c in cs]); Pn,Mn,phi=pts.T
P0=(0.85*fc*(b*h-Ast)+fy*Ast)/1e3; cap=0.80*0.65*P0; dP=np.minimum(phi*Pn,cap); dM=phi*Mn
ib=np.argmax(Mn); print("Ex9.4 P0=%.0f kN, max design axial 0.80*phi*P0=%.0f kN, balanced point: Pn=%.0f kN Mn=%.0f kN.m, pure bending Mn=%.0f kN.m"%(P0,cap,Pn[ib],Mn[ib],np.interp(0,Pn,Mn)))
def ok(Pu,Mu): return Mu<=np.interp(Pu,dP,dM) and Pu<=cap
loads={"A":(1500,120),"B":(2600,150),"C":(600,230),"D":(2000,240)}
for k_,(pu,mu) in loads.items(): print(f"  load case {k_}: Pu={pu} kN, Mu={mu} kN.m, capacity phi*Mn at this Pu={np.interp(pu,dP,dM):.0f} kN.m -> {'OK' if ok(pu,mu) else 'FAILS'}")
fig,ax=plt.subplots(figsize=(4.6,4.4)); ax.plot(Mn,Pn,"--",color="0.5",label="nominal (Pn, Mn)"); ax.plot(dM,dP,color=B,lw=1.8,label="design (phi Pn, phi Mn)")
for k_,(pu,mu) in loads.items(): ax.plot(mu,pu,"o" if ok(pu,mu) else "x",color="#38a169" if ok(pu,mu) else R,ms=7); ax.text(mu+6,pu+40,k_,fontsize=9)
ax.set_xlabel("Moment (kN.m)"); ax.set_ylabel("Axial load (kN)"); ax.set_ylim(0,None); ax.set_xlim(0,None); ax.legend(frameon=False,fontsize=8); clean(ax)
fig.tight_layout(); fig.savefig("fig/fig9_4_interaction.png",dpi=200); plt.close()

# ---- Example 10.4: bearing capacity of a strip footing, which uncertainty matters?
def qult(c,phi,gam,Bf=1.5,Df=1.2):
    p=np.radians(phi); Nq=np.exp(np.pi*np.tan(p))*np.tan(np.pi/4+p/2)**2; Nc=(Nq-1)/np.tan(p); Ng=2*(Nq+1)*np.tan(p)       # Vesic factors
    return c*Nc+gam*Df*Nq+0.5*gam*Bf*Ng
rng=np.random.default_rng(10); N=200000; mu=dict(c=10.0,phi=30.0,gam=18.0); cov=dict(c=0.40,phi=0.10,gam=0.05)
sl=np.sqrt(np.log(1+cov["c"]**2)); c_=np.exp(rng.normal(np.log(mu["c"])-sl**2/2,sl,N)); ph=rng.normal(mu["phi"],mu["phi"]*cov["phi"],N); ga=rng.normal(mu["gam"],mu["gam"]*cov["gam"],N)
q=qult(c_,ph,ga); q0=qult(**mu); qa=q0/3
print("Ex10.4 q_ult at mean values=%.0f kPa, allowable (FS=3)=%.0f kPa; Monte Carlo: mean=%.0f, 5th percentile=%.0f kPa; P(q_ult < applied %.0f kPa)=%.3f%%; P(q_ult < 2 x applied)=%.1f%%"%(q0,qa,q.mean(),np.percentile(q,5),qa,100*np.mean(q<qa),100*np.mean(q<2*qa)))
tor={}
for k_ in mu:
    lo=dict(mu); hi=dict(mu); lo[k_]=mu[k_]*(1-cov[k_]); hi[k_]=mu[k_]*(1+cov[k_]); tor[k_]=(qult(**lo),qult(**hi))
print("  one-sd swings (kPa):",{k_:(round(a),round(b_)) for k_,(a,b_) in tor.items()})
fig,ax=plt.subplots(1,2,figsize=(8.4,3)); ax[0].hist(q,bins=80,range=(0,2500),color=B); ax[0].axvline(qa,color=R,ls="--"); ax[0].text(qa+20,ax[0].get_ylim()[1]*0.9,"applied",fontsize=7,color=R); ax[0].set_xlabel("Ultimate bearing capacity (kPa)"); ax[0].set_yticks([]); clean(ax[0])
lab={"c":"cohesion c' (COV 40%)","phi":"friction angle (COV 10%)","gam":"unit weight (COV 5%)"}
for i,k_ in enumerate(sorted(tor,key=lambda z:abs(tor[z][1]-tor[z][0]))): ax[1].barh(i,tor[k_][1]-tor[k_][0],left=tor[k_][0],color=O); ax[1].text(tor[k_][1]+15,i,lab[k_],va="center",fontsize=7)
ax[1].axvline(q0,color=K,lw=0.8); ax[1].set_yticks([]); ax[1].set_xlabel("q_ult for -1 sd ... +1 sd (kPa)"); ax[1].set_xlim(None,tor["phi"][1]+520); clean(ax[1])
fig.tight_layout(); fig.savefig("fig/fig10_4_bearing.png",dpi=200); plt.close()

# ---- Example 11.4: schedule risk by Monte Carlo on a critical-path network
acts={"A excavation":(8,10,16,[]),"B foundations":(12,15,24,["A"]),"C columns+slabs":(40,48,70,["B"]),"D masonry":(18,22,34,["C"]),"E MEP rough-in":(20,26,45,["C"]),
      "F plaster":(14,18,28,["D","E"]),"G facade":(15,20,40,["C"]),"H finishes":(25,30,48,["F"]),"I external works":(10,14,25,["G"]),"J handover":(4,5,8,["H","I"])}
keys=[k_[0] for k_ in acts]; pred={k_[0]:v[3] for k_,v in acts.items()}
def cpm(d):
    ef={}
    for k_ in keys: ef[k_]=max([ef[p] for p in pred[k_]],default=0)+d[k_]
    crit=set(); cur="J"
    while True:
        crit.add(cur)
        if not pred[cur]: break
        cur=max(pred[cur],key=lambda p:ef[p])
    return ef["J"],crit
det,cdet=cpm({k_[0]:v[1] for k_,v in acts.items()}); print("Ex11.4 deterministic CPM with most-likely durations: %d days, critical path %s"%(det,"-".join(sorted(cdet,key=keys.index))))
rng=np.random.default_rng(11); n=20000; T=np.zeros(n); ci={k_:0 for k_ in keys}
D={k_[0]:rng.triangular(v[0],v[1],v[2],n) for k_,v in acts.items()}
for i in range(n):
    T[i],cr=cpm({k_:D[k_][i] for k_ in keys})
    for k_ in cr: ci[k_]+=1
print("  Monte Carlo: mean=%.0f days, P50=%.0f, P80=%.0f, P95=%.0f; P(finish within %d days)=%.1f%%"%(T.mean(),*np.percentile(T,[50,80,95]),det,100*np.mean(T<=det)))
print("  criticality index (%):",{k_:round(100*v/n) for k_,v in ci.items()})
fig,ax=plt.subplots(1,2,figsize=(8.6,3.1)); ax[0].hist(T,bins=60,color=B); ax[0].axvline(det,color=R,ls="--"); ax[0].text(det-2,ax[0].get_ylim()[1]*0.92,"CPM %d d"%det,fontsize=7,color=R,ha="right"); ax[0].axvline(np.percentile(T,80),color=K,ls=":"); ax[0].text(np.percentile(T,80)+2,ax[0].get_ylim()[1]*0.92,"P80",fontsize=7); ax[0].set_xlabel("Project duration (days)"); ax[0].set_yticks([]); clean(ax[0])
ax[1].bar(keys,[100*ci[k_]/n for k_ in keys],color=O); ax[1].set_ylabel("Criticality index (%)"); ax[1].set_xlabel("Activity"); clean(ax[1])
fig.tight_layout(); fig.savefig("fig/fig11_4_schedule.png",dpi=200); plt.close()

# ---- Example 12.2: a classical baseline for crack segmentation (no training)
from crackgen import make_images
from skimage.filters import threshold_otsu, gaussian
from skimage.morphology import black_tophat, disk, remove_small_objects
X,y,M=make_images(500,seed=2,joints=False); tp=fp=fn=0; fpc=[]; ex=None
for img,lab,m in zip(X,y,M):
    bt=black_tophat(gaussian(img,1.0),disk(4)); pm=remove_small_objects(bt>max(threshold_otsu(bt),0.04),12)
    if lab: tp+=(pm&m).sum(); fp+=(pm&~m).sum(); fn+=(~pm&m).sum(); ex=ex or (img,m,pm)
    else: fpc.append(pm.sum())
prec,rec=tp/(tp+fp),tp/(tp+fn); print("Ex12.2 black top-hat + Otsu: pixel precision=%.3f recall=%.3f F1=%.3f; false-positive pixels per crack-free image=%.1f (U-Net in Example 12.1: F1 0.915, 0.07 px)"%(prec,rec,2*prec*rec/(prec+rec),np.mean(fpc)))
fig,ax=plt.subplots(1,3,figsize=(6.6,2.4))
for a,im,t_ in zip(ax,ex,["Image","True mask","Top-hat + Otsu"]): a.imshow(im,cmap="gray"); a.set_title(t_,fontsize=8); a.axis("off")
fig.tight_layout(); fig.savefig("fig/fig12_4_classical.png",dpi=200); plt.close()
