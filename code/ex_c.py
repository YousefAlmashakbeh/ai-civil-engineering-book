# Additional worked examples, chapters 13-18
import re, numpy as np, matplotlib, warnings; warnings.filterwarnings("ignore")
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import stats
B="#2b6cb0"; O="#dd6b20"; K="#2d3748"; R="#c53030"; G="#38a169"
def clean(ax): ax.spines[["top","right"]].set_visible(False)

# ---- Example 13.4: impact-echo, slab thickness from a frequency peak
fs=500e3; t=np.arange(0,0.008,1/fs); V=4000.0; beta=0.96; rng=np.random.default_rng(13)
def echo(depth,amp=1.0,decay=900):                      # multiple reflections between the surface and a reflector at 'depth'
    f=beta*V/(2*depth); return amp*np.exp(-decay*t)*np.sin(2*np.pi*f*t)
def spectrum(x): X=np.abs(np.fft.rfft(x*np.hanning(len(x)),8*len(x))); fr=np.fft.rfftfreq(8*len(x),1/fs); return fr,X/X.max()
surface=0.8*np.exp(-6000*t)*np.sin(2*np.pi*2500*t)      # low-frequency surface (R-wave) part of the record
cases={"sound slab, 250 mm":echo(0.25)+surface,"delamination at 90 mm":0.15*echo(0.25)+echo(0.09)+surface}
fig,ax=plt.subplots(1,2,figsize=(5.0,2.9)); print("Ex13.4 expected: 250 mm -> %.2f kHz, 90 mm -> %.2f kHz"%(beta*V/0.5/1e3,beta*V/0.18/1e3))
for (nm,x),c in zip(cases.items(),[B,O]):
    x=x+rng.normal(0,0.05,len(t)); fr,X=spectrum(x); band=(fr>4000)&(fr<40000); fp=fr[band][np.argmax(X[band])]; Tm=beta*V/(2*fp)
    print(f"  {nm}: peak {fp/1e3:.2f} kHz -> depth {Tm*1e3:.0f} mm; with assumed V off by +5%: {Tm*1.05*1e3:.0f} mm")
    ls_="--" if c==O else "-"; ax[0].plot(t*1e3,x+(1.6 if c==O else 0),color=c,lw=0.5,ls=ls_); ax[1].plot(fr/1e3,X,color=c,lw=1,ls=ls_,label=nm); ax[1].text(fp/1e3+0.8,0.93 if c==O else 0.75,nm.replace(", ","\n").replace(" at ","\nat ").replace("sound slab","sound\nslab"),color=c,fontsize=9,va="top")
ax[0].set_xlim(0,4); ax[0].set_xlabel("Time (ms)"); ax[0].set_yticks([]); clean(ax[0]); ax[1].set_xlim(0,40); ax[1].set_xlabel("Frequency (kHz)"); ax[1].set_ylabel("Normalised amplitude"); clean(ax[1])
print("  frequency resolution of an 8 ms record = %.0f Hz -> thickness resolution near 250 mm = %.1f mm"%(1/0.008,0.25*(1/0.008)/(beta*V/0.5)*1e3))
fig.set_layout_engine("tight", w_pad=1.5); fig.savefig("fig/fig13_5_impactecho.png",dpi=200)   # drawn at print width (12.6 cm): fonts >= 9 pt in print; plt.close()

# ---- Example 14.4: fundamental diagram of a traffic stream, two fitted models
rng=np.random.default_rng(14); k=rng.uniform(5,110,220); vf,km=92.0,38.0
v=vf*np.exp(-k/km)*np.exp(rng.normal(0,0.07,220))                       # field-like data: Underwood form + scatter
A=np.c_[np.ones_like(k),k]; a,b=np.linalg.lstsq(A,v,rcond=None)[0]; kj=-a/b; cap_g=a*kj/4                                   # Greenshields: v = vf (1 - k/kj)
c0,c1=np.linalg.lstsq(A,np.log(v),rcond=None)[0]; vf_u,km_u=np.exp(c0),-1/c1; cap_u=vf_u*km_u/np.e                          # Underwood: v = vf exp(-k/km)
rm=lambda p:np.sqrt(np.mean((v-p)**2))
print("Ex14.4 Greenshields: vf=%.0f km/h, kj=%.0f veh/km, capacity=%.0f veh/h/lane at k=%.0f, RMSE=%.1f km/h"%(a,kj,cap_g,kj/2,rm(a+b*k)))
print("  Underwood: vf=%.0f km/h, km=%.0f veh/km, capacity=%.0f veh/h/lane at k=%.0f, RMSE=%.1f km/h; highest observed flow=%.0f"%(vf_u,km_u,cap_u,km_u,rm(vf_u*np.exp(-k/km_u)),(k*v).max()))
g=np.linspace(0,125,200); fig,ax=plt.subplots(1,2,figsize=(8.4,3.1))
ax[0].scatter(k,v,s=6,color="0.6"); ax[0].plot(g,np.maximum(a+b*g,0),color=O,label="Greenshields (linear)"); ax[0].plot(g,vf_u*np.exp(-g/km_u),color=B,label="Underwood (exponential)"); ax[0].set_xlabel("Density (veh/km/lane)"); ax[0].set_ylabel("Speed (km/h)"); ax[0].legend(frameon=False,fontsize=7.5,loc="upper right"); clean(ax[0])
ax[1].scatter(k,k*v,s=6,color="0.6"); ax[1].plot(g,g*np.maximum(a+b*g,0),color=O); ax[1].plot(g,g*vf_u*np.exp(-g/km_u),color=B); ax[1].set_xlabel("Density (veh/km/lane)"); ax[1].set_ylabel("Flow (veh/h/lane)"); clean(ax[1])
fig.tight_layout(); fig.subplots_adjust(wspace=0.35); fig.savefig("fig/fig14_5_fundamental.png",dpi=200); plt.close()

# ---- Example 15.4: design rainfall from a short record (Gumbel + bootstrap)
rng=np.random.default_rng(15); true=stats.genextreme(c=-0.10,loc=28,scale=11); x=true.rvs(35,random_state=rng)          # 35 annual maxima of daily rain (mm)
def gumbel_q(s,Tr): loc,sc=stats.gumbel_r.fit(s); return loc-sc*np.log(-np.log(1-1/np.asarray(Tr)))
Tr=[10,50,100]; q=gumbel_q(x,Tr); bs=np.array([gumbel_q(rng.choice(x,len(x)),Tr) for _ in range(2000)]); lo,hi=np.percentile(bs,[5,95],axis=0)
print("Ex15.4 record: n=35, mean=%.1f mm, max=%.1f mm"%(x.mean(),x.max()))
for T_,qq,l_,h_ in zip(Tr,q,lo,hi): print(f"  T={T_} yr: Gumbel estimate {qq:.0f} mm (90% bootstrap interval {l_:.0f}-{h_:.0f}); value of the generating distribution {true.ppf(1-1/T_):.0f} mm")
xs=np.sort(x); pp=(np.arange(1,36)-0.44)/(35+0.12); rp=1/(1-pp); TT=np.logspace(0.05,2.3,100)
fig,ax=plt.subplots(figsize=(5.6,3.4)); ax.plot(rp,xs,"o",color=K,ms=3,label="annual maxima (Gringorten)"); ax.plot(TT,gumbel_q(x,TT),color=B,label="Gumbel fit")
b2=np.array([gumbel_q(rng.choice(x,35),TT) for _ in range(500)]); ax.fill_between(TT,*np.percentile(b2,[5,95],axis=0),color=B,alpha=0.15,label="90% bootstrap band"); ax.plot(TT,true.ppf(1-1/TT),"--",color=R,lw=1,label="generating distribution")
ax.set_xscale("log"); ax.set_xlabel("Return period (years)"); ax.set_ylabel("Daily rainfall (mm)"); ax.legend(frameon=False,fontsize=7); clean(ax)
fig.tight_layout(); fig.savefig("fig/fig15_4_gumbel.png",dpi=200); plt.close()

# ---- Example 16.5: Bayesian updating of a girder's stiffness from load tests
Lg=20.0; Pt=300e3; EI_true=2.1e9; sig=0.6e-3; rng=np.random.default_rng(16)          # span m, test truck N at midspan, N.m2, deflection noise m
defl=lambda EI:Pt*Lg**3/(48*EI); grid=np.linspace(1.2e9,3.6e9,2000); prior=stats.lognorm(s=0.15,scale=2.6e9).pdf(grid); prior/=np.trapezoid(prior,grid)
z=defl(EI_true)+rng.normal(0,sig,8); fig,ax=plt.subplots(figsize=(5.6,3.3)); ax.plot(grid/1e9,prior*1e9,"--",color="0.5",label="prior (design drawings)")
print("Ex16.5 design EI=2.60, true EI=2.10 GN.m2; expected deflection %.1f mm vs measured mean %.1f mm"%(defl(2.6e9)*1e3,z.mean()*1e3))
for n_,c in [(1,O),(8,B)]:
    like=np.exp(-0.5*(((z[:n_,None]-defl(grid)[None,:])/sig)**2).sum(0)); post=prior*like; post/=np.trapezoid(post,grid); cdf=np.cumsum(post)*(grid[1]-grid[0])
    m_=np.trapezoid(grid*post,grid); l_,h_=grid[np.searchsorted(cdf,0.025)],grid[np.searchsorted(cdf,0.975)]
    print(f"  after {n_} test(s): posterior mean {m_/1e9:.2f}, 95% interval {l_/1e9:.2f}-{h_/1e9:.2f} GN.m2"); ax.plot(grid/1e9,post*1e9,color=c,label=f"posterior after {n_} test{'s' if n_>1 else ''}")
ax.axvline(EI_true/1e9,color=R,ls=":"); ax.set_xlabel("EI (GN.m2)"); ax.set_ylabel("Probability density"); ax.legend(frameon=False,fontsize=8); clean(ax)
fig.tight_layout(); fig.savefig("fig/fig16_5_bayes.png",dpi=200); plt.close()

# ---- Example 17.3: how good is the numeric guard? a systematic test
from ch17_corpus import DOCS
UN=r"(مم|سم|متر|متراً|درجة|يوم|يوماً|أيام|ساعة)"
def nums(s): return re.findall(r"(\d+(?:\.\d+)?)\s*"+UN,s)
def guard_basic(ans,src): return all(n in {x[0] for x in nums(src)} for n,_ in nums(ans))            # as in Example 17.2: number must appear in the source
def to_mm(n,u): return float(n)*{"مم":1,"سم":10,"متر":1000,"متراً":1000}.get(u,np.nan)
def guard_units(ans,src):
    S=nums(src)
    for n,u in nums(ans):
        if any(n==a and u[:2]==b[:2] for a,b in S): continue
        if any(abs(to_mm(n,u)-to_mm(a,b))<1e-6 for a,b in S if not np.isnan(to_mm(n,u)) and not np.isnan(to_mm(a,b))): continue
        return False
    return True
tests=[]                                                                                               # (answer, source, is the answer right?)
with_num=[d for d in DOCS if nums(d)]
for d in with_num:
    n,u=nums(d)[0]; tests.append((d,d,True))                                                           # 1 faithful copy
    tests.append((d.replace(n,str(round(float(n)*1.5,1)).rstrip("0").rstrip(".")),d,False))            # 2 invented number
    if u=="مم": tests.append((d.replace(n+" مم",str(float(n)/10).rstrip("0").rstrip(".")+" سم"),d,True))   # 3 right value, other unit
    if len(nums(d))>=2:                                                                               # 4 two numbers of the source swapped
        (n1,u1),(n2,u2)=nums(d)[:2]
        if n1!=n2: tests.append((d.replace(n1,"#").replace(n2,n1).replace("#",n2),d,False))
print("Ex17.3 passages with a number: %d of %d; test answers: %d (%d right, %d wrong)"%(len(with_num),len(DOCS),len(tests),sum(t[2] for t in tests),sum(not t[2] for t in tests)))
for nm,gd in [("basic guard",guard_basic),("guard with unit conversion",guard_units)]:
    passed=np.array([gd(a,s) for a,s,_ in tests]); right=np.array([t[2] for t in tests])
    print(f"  {nm}: wrong answers caught {np.sum(~passed&~right)} of {np.sum(~right)}; right answers rejected {np.sum(~passed&right)} of {np.sum(right)}")

# ---- Example 18.3: conformal prediction intervals and what they do not cover
from ch5_data import make_concrete
from sklearn.ensemble import GradientBoostingRegressor
df=make_concrete(); X=df.drop(columns=["fc","mix"]).copy(); X["log_age"]=np.log(X.pop("age")); y=df.fc.values; gm=df.mix.values; rng=np.random.default_rng(18)
mixes=rng.permutation(df.mix.unique()); tr=np.isin(gm,mixes[:60]); ca=np.isin(gm,mixes[60:90]); te=np.isin(gm,mixes[90:])
gb=GradientBoostingRegressor(random_state=0).fit(X[tr],y[tr]); res_tr=np.abs(y[tr]-gb.predict(X[tr])); res_ca=np.abs(y[ca]-gb.predict(X[ca]))
qn=np.quantile(res_tr,0.9); nc=len(res_ca); qc=np.sort(res_ca)[int(np.ceil(0.9*(nc+1)))-1]; err=np.abs(y[te]-gb.predict(X[te]))
print("Ex18.3 half-width from training residuals=%.1f MPa -> coverage %.0f%%; conformal half-width (calibration mixes)=%.1f MPa -> coverage %.0f%% (target 90%%)"%(qn,100*np.mean(err<=qn),qc,100*np.mean(err<=qc)))
cov=[]
for s in range(200):
    r_=np.random.default_rng(s); mx=r_.permutation(df.mix.unique()); a_=np.isin(gm,mx[:60]); c_=np.isin(gm,mx[60:90]); t_=np.isin(gm,mx[90:])
    g_=GradientBoostingRegressor(n_estimators=60,random_state=0).fit(X[a_],y[a_]); rc=np.sort(np.abs(y[c_]-g_.predict(X[c_]))); cov.append(np.mean(np.abs(y[t_]-g_.predict(X[t_]))<=rc[int(np.ceil(0.9*(len(rc)+1)))-1]))
print("  over 200 random splits: mean coverage %.1f%%, range of the middle 90%% of splits %.0f-%.0f%%"%(100*np.mean(cov),*(100*np.percentile(cov,[5,95]))))
early=te&(df.age.values<=3); late=te&(df.age.values>=56); print("  coverage by age: <=3 days %.0f%%, >=56 days %.0f%% (same interval for all)"%(100*np.mean(err[early[te]]<=qc),100*np.mean(err[late[te]]<=qc)))
y2=y[te]*0.75                                                                                       # same mixes, but site-cured cores 25% weaker than lab cubes
print("  shifted population (in-place strength 25%% below lab cubes): coverage %.0f%%"%(100*np.mean(np.abs(y2-gb.predict(X[te]))<=qc)))
fig,ax=plt.subplots(figsize=(5.4,3.2)); ax.hist(100*np.array(cov),bins=25,color=B); ax.axvline(90,color=R,ls="--"); ax.set_xlabel("Coverage of the 90% conformal interval on new mixes (%)"); ax.set_ylabel("number of splits (of 200)"); clean(ax)
fig.tight_layout(); fig.savefig("fig/fig18_3_conformal.png",dpi=200); plt.close()
