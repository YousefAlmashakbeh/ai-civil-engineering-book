import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
rng=np.random.default_rng(5)
def make(n,clo,chi):
    c=rng.uniform(clo,chi,n); wc=rng.uniform(0.38,0.65,n); w=c*wc
    f=96.5/7**wc*rng.normal(1,0.06,n); return c,w,f
c,w,f=make(120,280,450); ct,wt,ft=make(40,500,600)   # new high-cement mixes
raw=LinearRegression().fit(np.c_[c,w],f)
eng=LinearRegression().fit((w/c).reshape(-1,1),np.log(f))
p_raw=raw.predict(np.c_[ct,wt]); p_eng=np.exp(eng.predict((wt/ct).reshape(-1,1)))
print(f"New mixes (cement 500-600): MAE raw={mean_absolute_error(ft,p_raw):.2f} MPa  MAE w/c={mean_absolute_error(ft,p_eng):.2f} MPa")
print("raw coefs (cement, water):", np.round(raw.coef_,3))
