import numpy as np, torch, torch.nn as nn
from crackgen import make_images
import importlib.util
torch.manual_seed(0); torch.set_num_threads(2)
norm=lambda X:(X-X.mean(axis=(1,2),keepdims=True))/(X.std(axis=(1,2),keepdims=True)+1e-6)
class CNN(nn.Module):
    def __init__(s):
        super().__init__()
        s.f=nn.Sequential(nn.Conv2d(1,16,3,padding=1),nn.BatchNorm2d(16),nn.ReLU(),nn.MaxPool2d(2),
                          nn.Conv2d(16,32,3,padding=1),nn.BatchNorm2d(32),nn.ReLU(),nn.MaxPool2d(2),
                          nn.Conv2d(32,64,3,padding=1),nn.BatchNorm2d(64),nn.ReLU(),nn.AdaptiveMaxPool2d(1))
        s.h=nn.Linear(64,2)
    def forward(s,x): return s.h(s.f(x).flatten(1))
def train(X,y,ep=6):
    m=CNN(); opt=torch.optim.Adam(m.parameters(),2e-3); lf=nn.CrossEntropyLoss()
    Xt=torch.tensor(norm(X))[:,None]; Yt=torch.tensor(y)
    for e in range(ep):
        m.train(); perm=torch.randperm(len(Xt))
        for b in range(0,len(Xt),64):
            i=perm[b:b+64]; opt.zero_grad(); lf(m(Xt[i]),Yt[i]).backward(); opt.step()
    return m.eval()
# test set with joints, tracking which negatives contain joints
rng_seed=5
from crackgen import concrete_bg, crack, joint
rng=np.random.default_rng(rng_seed); N=1000; X=np.zeros((N,64,64),np.float32); y=np.zeros(N,int); J=np.zeros(N,bool)
for i in range(N):
    img=concrete_bg(rng)
    if rng.random()<0.5: img,_=crack(img,rng); y[i]=1
    elif rng.random()<0.4: img,_=joint(img,rng); J[i]=True
    X[i]=np.clip(img,0,1)
for name,jflag in [("trained WITHOUT joints",False),("trained WITH joints",True)]:
    Xtr,ytr,_=make_images(4000,1,joints=jflag); m=train(Xtr,ytr)
    with torch.no_grad(): p=m(torch.tensor(norm(X))[:,None]).argmax(1).numpy()
    acc=(p==y).mean(); fp_joint=p[J].mean(); fp_plain=p[(y==0)&~J].mean(); rec=p[y==1].mean()
    print(f"{name}: acc={acc:.3f} recall={rec:.3f} false-alarm on joints={fp_joint:.3f} on plain={fp_plain:.3f} (joint imgs={J.sum()})")
