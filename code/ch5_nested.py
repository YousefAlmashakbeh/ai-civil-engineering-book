# Fair comparison: every model tuned inside nested, group-wise cross-validation
import numpy as np, warnings; warnings.filterwarnings("ignore")
from ch5_data import make_concrete
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.model_selection import GroupKFold, GridSearchCV
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor
df=make_concrete(); X=df.drop(columns=["fc","mix"]).copy(); X["log_age"]=np.log(X.age); X=X.drop(columns="age").values; y=df.fc.values; g=df.mix.values
cands={"Ridge":(make_pipeline(StandardScaler(),Ridge()),{"ridge__alpha":[0.01,0.1,1,10,100]}),
 "SVR":(make_pipeline(StandardScaler(),SVR()),{"svr__C":[10,50,200,1000],"svr__epsilon":[0.3,1.0],"svr__gamma":["scale",0.03,0.1]}),
 "RandomForest":(RandomForestRegressor(n_estimators=300,random_state=0,n_jobs=-1),{"max_features":[0.33,0.6,1.0],"min_samples_leaf":[1,3]}),
 "XGBoost":(XGBRegressor(n_estimators=600,subsample=0.8,colsample_bytree=0.8,random_state=0,n_jobs=2),{"max_depth":[2,3,4,6],"learning_rate":[0.03,0.1]})}
for nm,(m,grid) in cands.items():
    p=np.zeros(len(y)); best=[]
    for tr,te in GroupKFold(5).split(X,y,g):
        gs=GridSearchCV(m,grid,cv=GroupKFold(4),scoring="neg_mean_absolute_error").fit(X[tr],y[tr],groups=g[tr]); p[te]=gs.predict(X[te]); best.append(str(gs.best_params_))
    print(f"{nm}: nested-CV MAE={mean_absolute_error(y,p):.2f} MPa; most frequent choice: {max(set(best),key=best.count)}")
