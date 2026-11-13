import numpy as np, pandas as pd
def make_concrete(n_mix=200, seed=2026):
    rng=np.random.default_rng(seed); rows=[]
    for i in range(n_mix):
        cem=rng.uniform(150,500); slag=rng.uniform(0,250)*(rng.random()<0.5); fa=rng.uniform(0,180)*(rng.random()<0.5)
        wat=rng.uniform(140,220); sp=rng.uniform(0,15)*(rng.random()<0.6)
        ca=rng.uniform(850,1100); fag=rng.uniform(650,900)
        b=cem+0.8*slag+0.4*fa; wb=wat/b; s=(slag+fa)/(cem+slag+fa)
        f28=110/6.5**wb + 0.4*sp; batch=rng.normal(0,2.0)
        for t in rng.choice([3,7,14,28,56,90],3,replace=False):
            a_,b_=4+10*s,0.85-0.1*s
            g=(t/(a_+b_*t))/(28/(a_+b_*28))
            f=max(2.0,(f28*g+batch)*rng.normal(1,0.05))
            rows.append([cem,slag,fa,wat,sp,ca,fag,t,f,i])
    return pd.DataFrame(rows,columns=["cement","slag","flyash","water","sp","coarse","fine","age","fc","mix"]).round(1)
