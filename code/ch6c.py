import numpy as np, torch
exec(open("ch6b.py").read().split("# test set with joints")[0])
from crackgen import concrete_bg, draw_path
def faint_set(N,seed,depth,width):
    rng=np.random.default_rng(seed); X=np.zeros((N,64,64),np.float32); y=np.zeros(N,int)
    for i in range(N):
        img=concrete_bg(rng)
        if rng.random()<0.5:
            yy,xx=rng.uniform(16,48,2); a=rng.uniform(0,6.28); pts=[(yy,xx)]
            for _ in range(rng.integers(8,16)):
                a+=rng.normal(0,0.6); yy=np.clip(yy+3.5*np.sin(a),4,60); xx=np.clip(xx+3.5*np.cos(a),4,60); pts.append((yy,xx))
            img,_=draw_path(img,pts,rng.uniform(*width),rng.uniform(*depth)); y[i]=1
        X[i]=np.clip(img,0,1)
    return X,y
Xtr,ytr,_=make_images(4000,1); m=train(Xtr,ytr)
for name,d,w in [("same as training",(0.15,0.45),(0.8,2.6)),("hairline field cracks",(0.05,0.12),(0.6,1.0))]:
    X,y=faint_set(1000,11,d,w)
    with torch.no_grad(): p=m(torch.tensor(norm(X))[:,None]).argmax(1).numpy()
    print(f"{name:22s} acc={(p==y).mean():.3f} recall={p[y==1].mean():.3f}")
# fine-tune with 200 hairline examples
Xf,yf=faint_set(200,21,(0.05,0.12),(0.6,1.0))
Xmix=np.concatenate([Xtr[:1000],Xf]); ymix=np.concatenate([ytr[:1000],yf])
opt=torch.optim.Adam(m.parameters(),5e-4); lf=torch.nn.CrossEntropyLoss(); Xt=torch.tensor(norm(Xmix))[:,None]; Yt=torch.tensor(ymix)
for e in range(4):
    m.train(); perm=torch.randperm(len(Xt))
    for b in range(0,len(Xt),64):
        i=perm[b:b+64]; opt.zero_grad(); lf(m(Xt[i]),Yt[i]).backward(); opt.step()
m.eval(); X,y=faint_set(1000,11,(0.05,0.12),(0.6,1.0))
with torch.no_grad(): p=m(torch.tensor(norm(X))[:,None]).argmax(1).numpy()
print(f"after fine-tuning (200 hairline imgs) acc={(p==y).mean():.3f} recall={p[y==1].mean():.3f}")
