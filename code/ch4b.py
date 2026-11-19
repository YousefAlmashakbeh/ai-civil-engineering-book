import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
rng=np.random.default_rng(5)
def make(n,clo,chi):
    c=rng.uniform(clo,chi,n); wc=rng.uniform(0.38,0.65,n); w=c*wc
    f=96.5/7**wc*rng.normal(1,0.06,n); return c,w,f
c,w,f=make(120,280,450); ct,wt,ft=make(40,500,600)   # new high-cement mixes
# in range: hold out 25% of the 120 training mixes
tr,te=train_test_split(np.arange(len(f)),test_size=0.25,random_state=0)
r_in=LinearRegression().fit(np.c_[c,w][tr],f[tr])
e_in=LinearRegression().fit((w/c)[tr].reshape(-1,1),np.log(f[tr]))
r2_raw=r2_score(f[te],r_in.predict(np.c_[c,w][te]))
r2_eng=r2_score(f[te],np.exp(e_in.predict((w/c)[te].reshape(-1,1))))
print("In range (cement 280-450 kg/m3):")
print(f"R2 raw (cement, water) = {r2_raw:.3f} ; R2 engineered log-f vs w/c = {r2_eng:.3f}")
# new mixes: fit on all 120 mixes
raw=LinearRegression().fit(np.c_[c,w],f)
eng=LinearRegression().fit((w/c).reshape(-1,1),np.log(f))
p_raw=raw.predict(np.c_[ct,wt]); p_eng=np.exp(eng.predict((wt/ct).reshape(-1,1)))
print("\nNew mixes (cement 500-600 kg/m3):")
print(f"MAE raw = {mean_absolute_error(ft,p_raw):.2f} MPa   MAE w/c = {mean_absolute_error(ft,p_eng):.2f} MPa")
print(f"recovered A, B = {np.exp(eng.intercept_):.1f}, {np.exp(-eng.coef_[0]):.2f}")
