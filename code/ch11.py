import numpy as np, matplotlib, warnings; warnings.filterwarnings("ignore")
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_predict
from sklearn.metrics import mean_absolute_error, roc_auc_score, roc_curve, confusion_matrix, accuracy_score
rng=np.random.default_rng(11)
# (1) cost per m2
n=900; year=rng.integers(2015,2026,n)
idx={y:100*(1.02**(min(y,2020)-2015))*(1.13 if y>=2021 else 1)*(1.12 if y>=2022 else 1)*(1.03**max(0,y-2022)) for y in range(2015,2026)}
pi=np.array([idx[y] for y in year]); q=rng.integers(1,4,n); loc=rng.choice([1.0,0.92,0.95,1.08],n)  # Amman,Zarqa,Irbid,Aqaba
area=rng.uniform(300,6000,n); floors=rng.integers(1,9,n)
cost=(180+70*(q-1))*loc*(pi/100)*(1+0.015*floors)*(area/1000)**-0.05*np.exp(rng.normal(0,0.07,n))
city=np.searchsorted([0.92,0.95,1.0,1.08],loc); D=np.eye(4)[city][:,1:]   # city as a category (one-hot), not its true cost factor
X=np.c_[year,q,D,np.log(area),floors]; Xp=np.c_[np.log(pi),q,D,np.log(area),floors]
tr,te=train_test_split(np.arange(n),test_size=0.25,random_state=0); old=year<=2021; new=~old
def ev(model,XX,a,b,logy=False):
    y=np.log(cost) if logy else cost; model.fit(XX[a],y[a]); p=model.predict(XX[b]); p=np.exp(p) if logy else p
    return mean_absolute_error(cost[b],p)/cost[b].mean()*100, p
r1,_=ev(GradientBoostingRegressor(random_state=0),X,tr,te); r2,pg=ev(GradientBoostingRegressor(random_state=0),X,old,new)
r3,pl=ev(LinearRegression(),Xp,old,new,logy=True)
print(f"GBM random split error (MAE/mean)={r1:.1f}% ; GBM time split (train<=2021,test>=2022)={r2:.1f}% ; log-linear with price index time split={r3:.1f}%")
for yv in (2023,2025):
    s=year[new]==yv; print(yv,"mean actual",round(cost[new][s].mean()),"GBM",round(pg[s].mean()),"loglinear",round(pl[s].mean()))
fig,ax=plt.subplots(figsize=(6.5,3.4)); yrs=np.arange(2015,2026)
ax.plot(yrs,[cost[year==y].mean() for y in yrs],"o-",color="#2d3748",label="Actual mean")
ax.plot(yrs[yrs>=2022],[pg[year[new]==y].mean() for y in yrs[yrs>=2022]],"s--",color="#dd6b20",label="GBM (year as input)")
ax.plot(yrs[yrs>=2022],[pl[year[new]==y].mean() for y in yrs[yrs>=2022]],"^--",color="#2b6cb0",label="Log-linear with price index")
ax.axvspan(2021.5,2025.5,color="#edf2f7"); ax.text(2022,ax.get_ylim()[0]+5,"test period",fontsize=8)
ax.set_xlabel("Year"); ax.set_ylabel("Cost (JD/m2, illustrative)"); ax.legend(frameon=False,fontsize=8); ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig("fig/fig11_1_cost.png",dpi=200)
# (2) delay risk
m=1500; size=rng.uniform(np.log(0.2),np.log(50),m); design=rng.uniform(40,100,m); gov=rng.integers(0,2,m); lump=rng.integers(0,2,m); summer=rng.integers(0,2,m); var=rng.poisson(3,m)
z=-1.0+0.35*size-0.05*(design-70)+0.5*gov-0.3*lump+0.2*summer+0.25*var+0.02*(100-design)*gov
yd=(rng.random(m)<1/(1+np.exp(-z))).astype(int); D=np.c_[size,design,gov,lump,summer,var]
cv=StratifiedKFold(5,shuffle=True,random_state=0)
pL=cross_val_predict(LogisticRegression(max_iter=1000),D,yd,cv=cv,method="predict_proba")[:,1]
pG=cross_val_predict(GradientBoostingClassifier(random_state=0),D,yd,cv=cv,method="predict_proba")[:,1]
print(f"delayed share={yd.mean():.2f}; AUC logistic={roc_auc_score(yd,pL):.3f} GBM={roc_auc_score(yd,pG):.3f}")
pT=cross_val_predict(LogisticRegression(max_iter=1000),D[:,:5],yd,cv=cv,method="predict_proba")[:,1]
print(f"tender-stage model (without number of variation orders, unknown before execution): AUC logistic={roc_auc_score(yd,pT):.3f}")
# decision threshold, confusion matrix and reliability for the tender-stage model
for thr in (0.5,0.7):
    pr=(pT>=thr); tp=(pr&(yd==1)).sum(); fp=(pr&(yd==0)).sum(); fn=(~pr&(yd==1)).sum(); tn=(~pr&(yd==0)).sum()
    print(f"tender-stage, threshold {thr}: TP={tp} FP={fp} FN={fn} TN={tn}  recall={tp/(tp+fn):.2f} precision={tp/(tp+fp):.2f}")
bins=np.clip((pT*5).astype(int),0,4); print("reliability (predicted -> observed):"," ".join(f"{pT[bins==b].mean():.2f}->{yd[bins==b].mean():.2f}(n={np.sum(bins==b)})" for b in range(5) if np.sum(bins==b)>0))
print(f"Brier score={np.mean((pT-yd)**2):.3f} (always predicting the base rate: {yd.mean()*(1-yd.mean()):.3f})")
# earned value example
BAC,PV,EV,AC=1_000_000,500_000,420_000,480_000; CPI=EV/AC; SPI=EV/PV
print(f"EVM: CPI={CPI:.3f} SPI={SPI:.3f} EAC=BAC/CPI={BAC/CPI:,.0f}  EAC(CPI*SPI)={AC+(BAC-EV)/(CPI*SPI):,.0f}")
lg=LogisticRegression(max_iter=1000).fit((D-D.mean(0))/D.std(0),yd); names=["log size","design %","government","lump sum","summer start","variations"]
sc=[f"{k} {v:.2f}" for k,v in zip(names,lg.coef_[0])]; print("standardised coefs: "+", ".join(sc[:3])+",\n"+" "*20+", ".join(sc[3:]))
fig,ax=plt.subplots(figsize=(4.6,4.2))
for p,c,l,ls_ in [(pL,"#2b6cb0","Logistic","-"),(pG,"#dd6b20","GBM","--")]:
    f,t,_=roc_curve(yd,p); ax.plot(f,t,color=c,lw=2,ls=ls_,label=f"{l} AUC={roc_auc_score(yd,p):.3f}")
ax.plot([0,1],[0,1],color="#a0aec0",lw=1); ax.set_xlabel("False positive rate"); ax.set_ylabel("True positive rate"); ax.legend(frameon=False,fontsize=8); ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig("fig/fig11_2_roc.png",dpi=200)
# (3) clauses
from clauses import CLAUSES
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
txt=[s for k in CLAUSES for s in CLAUSES[k]]; lab=[k for k in CLAUSES for s in CLAUSES[k]]
clf=make_pipeline(TfidfVectorizer(analyzer="char_wb",ngram_range=(2,5)),LogisticRegression(max_iter=2000,C=10))
pc=cross_val_predict(clf,txt,lab,cv=StratifiedKFold(4,shuffle=True,random_state=0))
print(f"clauses={len(txt)} CV accuracy={accuracy_score(lab,pc):.3f}")
ks=list(CLAUSES); cm=confusion_matrix(lab,pc,labels=ks); print(cm)
wrong=[(t,l,str(p)) for t,l,p in zip(txt,lab,pc) if l!=p]
for w in wrong[:6]: print("WRONG:",w)
clf.fit(txt,lab)
new=["تُصرف مستحقات المقاول خلال ستين يوماً من تقديم الفاتورة",
     "يُغرّم المقاول مبلغ مئتي دينار عن كل يوم تأخير في التسليم",
     "يجوز لصاحب العمل إضافة طابق إضافي بأمر خطي مع تعديل السعر",
     "يُعدّ الزلزال أو الحريق العام حدثاً خارجاً عن إرادة الطرفين",
     "يضمن المقاول سلامة الهيكل الإنشائي عشر سنوات من الاستلام"]
print("new clauses ->",list(map(str,clf.predict(new))))
fig,ax=plt.subplots(figsize=(5,4.2)); ax.imshow(cm,cmap="Blues")
lbl=["Payment","Delay","Variation","Force maj.","Warranty"]
ax.set_xticks(range(5),lbl,rotation=30,fontsize=8); ax.set_yticks(range(5),lbl,fontsize=8)
for i in range(5):
    for j in range(5): ax.text(j,i,cm[i,j],ha="center",va="center",color="white" if cm[i,j]>8 else "#2d3748")
ax.set_xlabel("Predicted"); ax.set_ylabel("True"); fig.tight_layout(); fig.savefig("fig/fig11_3_clauses.png",dpi=200)
