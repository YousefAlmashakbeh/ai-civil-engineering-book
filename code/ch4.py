import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, KFold, GroupKFold, cross_val_score
from sklearn.metrics import r2_score, accuracy_score, recall_score, f1_score, precision_score
from sklearn.dummy import DummyClassifier
rng = np.random.default_rng(11)
# 4.1 cleaning
n=120
df = pd.DataFrame({"cement":rng.uniform(280,450,n).round(0)})
df["water"] = (df.cement*rng.uniform(0.38,0.65,n)).round(0)
df["fc28"] = (96.5/7**(df.water/df.cement)*rng.normal(1,0.06,n)).round(1)
df.loc[rng.choice(n,5,replace=False),"water"] = np.nan
bad = [17, 64]; df.loc[bad,"water"] = df.loc[bad,"water"]*10   # unit error
print("missing:", df.water.isna().sum())
wc = df.water/df.cement
q1,q3 = wc.quantile([.25,.75]); iqr=q3-q1
out_iqr = df.index[(wc<q1-1.5*iqr)|(wc>q3+1.5*iqr)].tolist()
out_phys = df.index[(wc<0.25)|(wc>0.9)].tolist()
print("IQR outliers:", out_iqr, " physical-limit outliers:", out_phys)
raw = df.copy()
df.loc[out_phys,"water"] = df.loc[out_phys,"water"]/10
df["water"] = df.water.fillna((df.cement*np.nanmedian(df.water/df.cement)).round(0))
print("after cleaning: missing", df.water.isna().sum(), " w/c range", round((df.water/df.cement).min(),2), round((df.water/df.cement).max(),2))
fig,ax=plt.subplots(1,2,figsize=(8,3.2),sharey=True)
ax[0].scatter(raw.water/raw.cement, raw.fc28, s=10, color="#2b6cb0"); ax[0].scatter((raw.water/raw.cement)[bad], raw.fc28[bad], s=40, color="#c53030")
ax[0].set_title("Raw data", fontsize=10); ax[0].set_xlabel("w/c"); ax[0].set_ylabel("f'c 28 d (MPa)")
ax[1].scatter(df.water/df.cement, df.fc28, s=10, color="#2b6cb0"); ax[1].scatter((df.water/df.cement)[bad], df.fc28[bad], s=40, color="#38a169")
ax[1].set_title("After cleaning", fontsize=10); ax[1].set_xlabel("w/c")
for a in ax: a.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig("fig/fig4_1_clean.png",dpi=200)
# 4.2 feature engineering
X_raw = df[["cement","water"]].values; y=df.fc28.values
X_eng = (df.water/df.cement).values.reshape(-1,1)
Xr_tr,Xr_te,Xe_tr,Xe_te,y_tr,y_te = train_test_split(X_raw,X_eng,y,test_size=0.25,random_state=0)
r2_raw = r2_score(y_te, LinearRegression().fit(Xr_tr,y_tr).predict(Xr_te))
lin = LinearRegression().fit(Xe_tr,np.log(y_tr))
r2_eng = r2_score(y_te, np.exp(lin.predict(Xe_te)))
print(f"R2 raw (cement, water) = {r2_raw:.3f} ; R2 engineered log-f vs w/c = {r2_eng:.3f}")
print("recovered A,B:", round(np.exp(lin.intercept_),1), round(np.exp(-lin.coef_[0]),2))
# 4.3 imbalance
m=2000
y_c = (rng.random(m)<0.05).astype(int)
X_c = np.column_stack([rng.normal(0,1,m)+1.5*y_c, rng.normal(0,1,m)+1.0*y_c])
Xtr,Xte,ytr,yte = train_test_split(X_c,y_c,test_size=0.3,random_state=0,stratify=y_c)
for name,clf in [("always no-crack",DummyClassifier(strategy="most_frequent")),
                 ("logistic",LogisticRegression()),
                 ("logistic balanced",LogisticRegression(class_weight="balanced"))]:
    p = clf.fit(Xtr,ytr).predict(Xte)
    print(f"{name:18s} acc={accuracy_score(yte,p):.3f} recall={recall_score(yte,p):.3f} precision={precision_score(yte,p,zero_division=0):.3f} F1={f1_score(yte,p):.3f}")
# 4.4 leakage
mixes=40; reps=3
wcm = rng.uniform(0.35,0.7,mixes); cem = rng.uniform(300,450,mixes); batch = rng.normal(0,3.0,mixes)
rows=[]
for i in range(mixes):
    for r in range(reps):
        rows.append([wcm[i],cem[i],96.5/7**wcm[i]+batch[i]+rng.normal(0,1.0),i])
L=np.array(rows); X4=L[:,:2]; y4=L[:,2]; g=L[:,3]
rf=RandomForestRegressor(n_estimators=300,random_state=0)
mae_rand = -cross_val_score(rf,X4,y4,cv=KFold(5,shuffle=True,random_state=0),scoring="neg_mean_absolute_error").mean()
mae_grp  = -cross_val_score(rf,X4,y4,cv=GroupKFold(5),groups=g,scoring="neg_mean_absolute_error").mean()
print(f"MAE random KFold = {mae_rand:.2f} MPa ; GroupKFold by mix = {mae_grp:.2f} MPa")
fig,ax=plt.subplots(figsize=(5.5,3))
ax.barh(["Random split\n(cubes of same mix\nin train & test)","Split by mix\n(GroupKFold)"],[mae_rand,mae_grp],color=["#a0aec0","#2b6cb0"])
for i,v in enumerate([mae_rand,mae_grp]): ax.text(v+0.05,i,f"{v:.2f} MPa",va="center")
ax.set_xlabel("Cross-validated MAE (MPa)"); ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig("fig/fig4_2_leakage.png",dpi=200)
