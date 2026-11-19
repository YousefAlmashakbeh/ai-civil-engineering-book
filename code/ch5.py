import numpy as np, pandas as pd, matplotlib, warnings; warnings.filterwarnings("ignore")
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from ch5_data import make_concrete
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel as C
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor
df=make_concrete(); print(df.shape, "mixes:", df.mix.nunique(), "fc range:", df.fc.min(), df.fc.max())
X=df.drop(columns=["fc","mix"]).copy(); X["log_age"]=np.log(X.age); X=X.drop(columns="age"); y=df.fc.values; g=df.mix.values
models={"Linear":make_pipeline(StandardScaler(),LinearRegression()),
 "Ridge":make_pipeline(StandardScaler(),Ridge(alpha=1.0)),
 "SVR":make_pipeline(StandardScaler(),SVR(C=50,epsilon=1.0)),
 "GPR":make_pipeline(StandardScaler(),GaussianProcessRegressor(C(100)*RBF(np.ones(8))+WhiteKernel(4),normalize_y=True,random_state=0)),
 "RandomForest":RandomForestRegressor(n_estimators=400,random_state=0),
 "XGBoost":XGBRegressor(n_estimators=600,learning_rate=0.05,max_depth=4,subsample=0.8,colsample_bytree=0.8,random_state=0)}
cv=GroupKFold(5); res=[]; preds={}
for n,m in models.items():
    p=cross_val_predict(m,X,y,cv=cv,groups=g); preds[n]=p
    a20=np.mean((y/p>=0.8)&(y/p<=1.2))   # measured/predicted within 0.8-1.2
    fold=[mean_absolute_error(y[te],p[te]) for _,te in cv.split(X,y,g)]
    res.append([n,mean_absolute_error(y,p),np.std(fold,ddof=1),np.sqrt(mean_squared_error(y,p)),r2_score(y,p),a20])
R=pd.DataFrame(res,columns=["model","MAE","MAE_fold_sd","RMSE","R2","a20"]).sort_values("MAE")
print(R.round(3).to_string(index=False))
best=R.iloc[0].model; p=preds[best]
fig,ax=plt.subplots(figsize=(4.6,4.4))
ax.scatter(y,p,s=8,alpha=0.6,color="#2b6cb0"); lim=[0,max(y.max(),p.max())+5]
ax.plot(lim,lim,color="#2d3748",lw=1); ax.plot(lim,[l*1.2 for l in lim],ls="--",color="#a0aec0",lw=1); ax.plot(lim,[l*0.8 for l in lim],ls="--",color="#a0aec0",lw=1)
ax.set_xlim(lim); ax.set_ylim(lim); ax.set_xlabel("Measured f'c (MPa)"); ax.set_ylabel("Predicted f'c (MPa)")
ax.set_title(f"{best}, GroupKFold by mix",fontsize=10); ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig("fig/fig5_1_parity.png",dpi=200)
# SHAP
import shap
xm=models["XGBoost"].fit(X,y); sv=shap.TreeExplainer(xm).shap_values(X)
imp=pd.Series(np.abs(sv).mean(0),index=X.columns).sort_values()
print("mean|SHAP|:", imp[::-1].round(2).to_dict())
fig,ax=plt.subplots(figsize=(5.5,3.4)); ax.barh(imp.index,imp.values,color="#2b6cb0")
ax.set_xlabel("Mean |SHAP value| (MPa)"); ax.spines[["top","right"]].set_visible(False); fig.tight_layout(); fig.savefig("fig/fig5_2_shap.png",dpi=200)
# dependence: water SHAP
i=list(X.columns).index("water"); print("SHAP water corr:", round(np.corrcoef(X.water,sv[:,i])[0,1],2))
# GPR 1D uncertainty
rng=np.random.default_rng(1); wb=rng.uniform(0.35,0.55,25); f=110/6.5**wb*rng.normal(1,0.05,25)
gp=GaussianProcessRegressor(C(100)*RBF(0.1)+WhiteKernel(1),normalize_y=True,random_state=0).fit(wb.reshape(-1,1),f)
xs=np.linspace(0.25,0.75,200); mu,sd=gp.predict(xs.reshape(-1,1),return_std=True)
for q in (0.45,0.70): 
    m_,s_=gp.predict([[q]],return_std=True); print(f"GPR w/b={q}: {m_[0]:.1f} ± {1.96*s_[0]:.1f} MPa (true {110/6.5**q:.1f})")
fig,ax=plt.subplots(figsize=(6.5,3.4))
ax.fill_between(xs,mu-1.96*sd,mu+1.96*sd,color="#bee3f8",label="95% band"); ax.plot(xs,mu,color="#2b6cb0",lw=2,label="GPR mean")
ax.plot(xs,110/6.5**xs,color="#2d3748",ls="--",lw=1,label="True law"); ax.scatter(wb,f,s=14,color="#dd6b20",zorder=3,label="Tests")
ax.set_xlabel("w/b"); ax.set_ylabel("f'c 28 d (MPa)"); ax.legend(frameon=False,fontsize=8); ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig("fig/fig5_3_gpr.png",dpi=200)
# k-means bridges
from sklearn.cluster import KMeans
rng=np.random.default_rng(4); n=150
age=np.r_[rng.uniform(5,20,60),rng.uniform(25,45,50),rng.uniform(40,60,40)]
cr=np.r_[rng.normal(8,0.6,60),rng.normal(6,0.7,50),rng.normal(4,0.7,40)].clip(1,9)
cl=np.r_[rng.normal(0.1,0.03,60),rng.normal(0.3,0.06,50),rng.normal(0.6,0.1,40)].clip(0.01)
B=np.c_[age,cr,cl]; km=KMeans(3,n_init=10,random_state=0).fit(StandardScaler().fit_transform(B))
for k in range(3):
    s=km.labels_==k; print(f"cluster {k}: n={s.sum()} age={age[s].mean():.0f} rating={cr[s].mean():.1f} chloride={cl[s].mean():.2f}%")
