import numpy as np, torch, torch.nn as nn, time, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from crackgen import make_images
torch.manual_seed(0); torch.set_num_threads(2)
Xtr,ytr,_=make_images(4000,1); Xte,yte,_=make_images(1000,2)
norm=lambda X:(X-X.mean(axis=(1,2),keepdims=True))/(X.std(axis=(1,2),keepdims=True)+1e-6)
print("train cracks:",ytr.mean().round(3))
fig,ax=plt.subplots(3,6,figsize=(8,4.3)); rng=np.random.default_rng(9)
idx=np.r_[np.where(ytr==1)[0][:6],np.where(ytr==0)[0][:12]]
for a,i in zip(ax.ravel(),idx): a.imshow(Xtr[i],cmap="gray",vmin=0,vmax=1); a.set_axis_off(); a.set_title("crack" if ytr[i] else "no crack",fontsize=7)
fig.tight_layout(); fig.savefig("fig/fig6_1_samples.png",dpi=200)
class CNN(nn.Module):
    def __init__(s):
        super().__init__()
        s.f=nn.Sequential(nn.Conv2d(1,16,3,padding=1),nn.BatchNorm2d(16),nn.ReLU(),nn.MaxPool2d(2),
                          nn.Conv2d(16,32,3,padding=1),nn.BatchNorm2d(32),nn.ReLU(),nn.MaxPool2d(2),
                          nn.Conv2d(32,64,3,padding=1),nn.BatchNorm2d(64),nn.ReLU(),nn.AdaptiveMaxPool2d(1))
        s.h=nn.Linear(64,2)
    def forward(s,x): return s.h(s.f(x).flatten(1))
m=CNN(); print("parameters:",sum(p.numel() for p in m.parameters()))
opt=torch.optim.Adam(m.parameters(),2e-3); lf=nn.CrossEntropyLoss()
Xt=torch.tensor(norm(Xtr))[:,None]; Yt=torch.tensor(ytr); Xv=torch.tensor(norm(Xte))[:,None]; Yv=torch.tensor(yte)
hist=[]; t0=time.time()
for ep in range(12):
    m.train(); perm=torch.randperm(len(Xt)); L=0
    for b in range(0,len(Xt),64):
        i=perm[b:b+64]; opt.zero_grad(); l=lf(m(Xt[i]),Yt[i]); l.backward(); opt.step(); L+=l.item()*len(i)
    m.eval()
    with torch.no_grad(): pv=m(Xv).argmax(1); vl=lf(m(Xv),Yv).item()
    acc=(pv==Yv).float().mean().item(); hist.append([L/len(Xt),vl,acc])
    print(f"epoch {ep+1:2d} train_loss={L/len(Xt):.3f} test_loss={vl:.3f} test_acc={acc:.3f}")
print("time s:",round(time.time()-t0))
p=pv.numpy(); tp=((p==1)&(yte==1)).sum(); fn=((p==0)&(yte==1)).sum(); fp=((p==1)&(yte==0)).sum(); tn=((p==0)&(yte==0)).sum()
print("confusion TP FN FP TN:",tp,fn,fp,tn, " recall",round(tp/(tp+fn),3)," precision",round(tp/(tp+fp),3))
H=np.array(hist); fig,ax=plt.subplots(1,2,figsize=(8,3))
ax[0].plot(range(1,13),H[:,0],label="train",color="#2b6cb0"); ax[0].plot(range(1,13),H[:,1],label="test",color="#dd6b20"); ax[0].set_xlabel("Epoch"); ax[0].set_ylabel("Loss"); ax[0].legend(frameon=False)
ax[1].plot(range(1,13),H[:,2],color="#2b6cb0"); ax[1].set_xlabel("Epoch"); ax[1].set_ylabel("Test accuracy")
for a in ax: a.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig("fig/fig6_2_curves.png",dpi=200)
torch.save(m.state_dict(),"cnn_crack.pt")
# domain shift: test on images without the hard-negative joints vs with only joints
Xj,yj,_=make_images(1000,3,joints=True)
with torch.no_grad(): pj=m(torch.tensor(norm(Xj))[:,None]).argmax(1).numpy()
