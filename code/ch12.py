import numpy as np, torch, torch.nn as nn, time, matplotlib, warnings; warnings.filterwarnings("ignore")
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from crackgen import concrete_bg, draw_path
from scipy.ndimage import distance_transform_edt
from skimage.morphology import skeletonize
torch.manual_seed(0); torch.set_num_threads(2); PX=0.2  # mm per pixel
def make(N,seed):
    r=np.random.default_rng(seed); X=np.zeros((N,64,64),np.float32); M=np.zeros((N,64,64),np.float32); W=np.zeros(N)
    for i in range(N):
        img=concrete_bg(r)
        if r.random()<0.85:
            y,x=r.uniform(16,48,2); a=r.uniform(0,6.28); pts=[(y,x)]
            for _ in range(r.integers(8,16)):
                a+=r.normal(0,0.6); y=np.clip(y+3.5*np.sin(a),4,60); x=np.clip(x+3.5*np.cos(a),4,60); pts.append((y,x))
            w=r.uniform(0.8,3.5); img,m=draw_path(img,pts,w,r.uniform(0.12,0.45)); M[i]=m; W[i]=w
        X[i]=np.clip(img,0,1)
    return X,M,W
Xtr,Mtr,_=make(3000,1); Xte,Mte,Wte=make(500,2)
norm=lambda X:(X-X.mean(axis=(1,2),keepdims=True))/(X.std(axis=(1,2),keepdims=True)+1e-6)
def block(i,o): return nn.Sequential(nn.Conv2d(i,o,3,padding=1),nn.BatchNorm2d(o),nn.ReLU(),nn.Conv2d(o,o,3,padding=1),nn.BatchNorm2d(o),nn.ReLU())
class UNet(nn.Module):
    def __init__(s):
        super().__init__(); s.e1=block(1,16); s.e2=block(16,32); s.b=block(32,64)
        s.u2=nn.ConvTranspose2d(64,32,2,2); s.d2=block(64,32); s.u1=nn.ConvTranspose2d(32,16,2,2); s.d1=block(32,16); s.o=nn.Conv2d(16,1,1); s.p=nn.MaxPool2d(2)
    def forward(s,x):
        e1=s.e1(x); e2=s.e2(s.p(e1)); b=s.b(s.p(e2))
        d2=s.d2(torch.cat([s.u2(b),e2],1)); d1=s.d1(torch.cat([s.u1(d2),e1],1)); return s.o(d1)
m=UNet(); print("U-Net parameters:",sum(p.numel() for p in m.parameters()))
opt=torch.optim.Adam(m.parameters(),2e-3); bce=nn.BCEWithLogitsLoss(pos_weight=torch.tensor(10.0))
Xt=torch.tensor(norm(Xtr))[:,None]; Mt=torch.tensor(Mtr)[:,None]
def dice(lo,t): p=torch.sigmoid(lo); return 1-(2*(p*t).sum()+1)/(p.sum()+t.sum()+1)
t0=time.time()
for ep in range(10):
    m.train(); perm=torch.randperm(len(Xt))
    for b in range(0,len(Xt),32):
        i=perm[b:b+32]; opt.zero_grad(); lo=m(Xt[i]); l=bce(lo,Mt[i])+dice(lo,Mt[i]); l.backward(); opt.step()
print("train time s:",round(time.time()-t0))
m.eval()
with torch.no_grad(): P=(torch.sigmoid(m(torch.tensor(norm(Xte))[:,None]))[:,0].numpy()>0.5)
T=Mte>0.5; has=T.sum((1,2))>0
inter=(P&T).sum((1,2)); uni=(P|T).sum((1,2)); iou=inter[has]/uni[has]
prec=(P&T).sum()/P.sum(); rec=(P&T).sum()/T.sum(); f1=2*prec*rec/(prec+rec)
print(f"pixel precision={prec:.3f} recall={rec:.3f} F1={f1:.3f}; mean IoU (crack images)={iou.mean():.3f}")
fp_img=P[~has].sum((1,2)); print("false-positive pixels per crack-free image (mean):",round(fp_img.mean(),2))
from skimage.measure import perimeter_crofton
def width_mm(mask, how="area"):
    # a ribbon of length L and width w has area A = w L and perimeter P = 2L + 2w, so w = (P - sqrt(P^2 - 16 A)) / 4
    # the perimeter is measured by the Crofton formula, which is nearly unbiased for digital outlines at any angle
    if mask.sum()<5: return np.nan
    if how=="area":
        A=mask.sum(); P=perimeter_crofton(mask,4); return (P-np.sqrt(max(P*P-16*A,0)))/4*PX
    sk=skeletonize(mask); d=distance_transform_edt(mask); return np.median(2*d[sk]-1)*PX
# estimator check on straight strips of known width (independent of the network)
rs=np.random.default_rng(0); yy,xx=np.mgrid[:96,:96]
for w0 in [1,2,4,8]:
    ea=[]; eo=[]
    for _ in range(200):
        a=rs.uniform(0,np.pi); c=rs.uniform(40,56,2); mk=np.abs((yy-c[0])*np.cos(a)-(xx-c[1])*np.sin(a))<=w0/2
        mk[:8]=mk[-8:]=0; mk[:,:8]=mk[:,-8:]=0; ea.append(width_mm(mk)/PX-w0); eo.append(width_mm(mk,"2d-1")/PX-w0)
    print(f"strip width {w0} px: bias area-perimeter={np.mean(ea):+.2f} px (sd {np.std(ea):.2f}); bias 2d-1={np.mean(eo):+.2f} px (sd {np.std(eo):.2f})")
wt=np.array([width_mm(t) for t in T[has]]); wp=np.array([width_mm(p) for p in P[has]]); ok=~np.isnan(wt)&~np.isnan(wp)
err=np.abs(wp[ok]-wt[ok]); print(f"width (pred mask vs true mask): MAE={err.mean():.3f} mm, within +-0.1 mm={np.mean(err<=0.1)*100:.0f}%")
# non-circular check: the generator's mask is a Gaussian ridge cut at 0.5, so its analytic width is 2*sqrt(2 ln 2)*(w/2)
wa=Wte[has]*np.sqrt(2*np.log(2))*PX
for nm,wx in [("true mask",wt),("predicted mask",wp)]:
    e=wx[ok]-wa[ok]; print(f"{nm} vs analytic width: bias={e.mean():+.3f} mm, sd={e.std():.3f} mm, MAE={np.abs(e).mean():.3f} mm, within +-0.1 mm={np.mean(np.abs(e)<=0.1)*100:.0f}%")
wo=np.array([width_mm(p,'2d-1') for p in P[has]]); e=wo[ok]-wa[ok]; print(f"old 2d-1 rule on predicted mask vs analytic: bias={e.mean():+.3f} mm, MAE={np.abs(e).mean():.3f} mm")
gw=Wte[has]
bins=[(0.8,1.5),(1.5,2.5),(2.5,3.5)]
for lo_,hi_ in bins:
    s=(gw>=lo_)&(gw<hi_); print(f"generator width {lo_}-{hi_} px: mean IoU={iou[s].mean():.3f}, mean true width={np.nanmean(wt[s]):.2f} mm")
limits=[("dry air or protective membrane",0.41),("humidity, moist air, soil",0.30),("deicing chemicals",0.18),("seawater, wetting/drying",0.15),("water-retaining structures",0.10)]
for nm,lim in limits: print(f"{nm}: exceed {lim} mm -> true {np.mean(wt[ok]>lim)*100:.0f}%  predicted {np.mean(wp[ok]>lim)*100:.0f}%")
# deployment
x=torch.tensor(norm(Xte[:1]))[:,None]; t0=time.time()
with torch.no_grad():
    for _ in range(200): m(x)
print(f"CPU inference per 64x64 tile: {(time.time()-t0)/200*1000:.2f} ms; model size float32: {sum(p.numel() for p in m.parameters())*4/1024:.0f} KB")
# figures
idx=np.where(has)[0][[0,3,7,12]]
fig,ax=plt.subplots(3,4,figsize=(7,5.4))
for j,i in enumerate(idx):
    ax[0,j].imshow(Xte[i],cmap="gray",vmin=0,vmax=1); ax[1,j].imshow(T[i],cmap="gray"); ax[2,j].imshow(P[i],cmap="gray")
for a in ax.ravel(): a.set_axis_off()
for r,t in enumerate(["Image","True mask","U-Net"]): ax[r,0].text(-8,32,t,rotation=90,va="center",fontsize=9)
fig.tight_layout(); fig.savefig("fig/fig12_1_unet.png",dpi=200)
fig,ax=plt.subplots(figsize=(4.6,4.2)); ax.scatter(wt[ok],wp[ok],s=8,color="#2b6cb0"); ax.plot([0,0.9],[0,0.9],color="#2d3748",lw=1)
for lim in (0.15,0.30,0.41): ax.axvline(lim,color="#c53030",ls=":",lw=0.8)
ax.set_xlabel("Width from true mask (mm)"); ax.set_ylabel("Width from U-Net mask (mm)"); ax.spines[["top","right"]].set_visible(False)
fig.tight_layout(); fig.savefig("fig/fig12_3_width.png",dpi=200)
