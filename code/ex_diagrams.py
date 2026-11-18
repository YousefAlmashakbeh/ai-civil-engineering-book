# Explanatory diagrams added to the chapters
import numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon, Circle
B="#2b6cb0"; O="#dd6b20"; K="#2d3748"; R="#c53030"; G="#38a169"
def box(ax,x,y,w,h,t,fc="#e8f0fb",ec=B,fs=8): ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.01,rounding_size=0.02",fc=fc,ec=ec,lw=1.1)); ax.text(x+w/2,y+h/2,t,ha="center",va="center",fontsize=fs)
def arr(ax,a,b,c="k",ls="-"): ax.annotate("",xy=b,xytext=a,arrowprops=dict(arrowstyle="->",color=c,lw=1.1,ls=ls))
def save(fig,name): fig.savefig("fig/"+name,dpi=200,bbox_inches="tight"); plt.close(fig)

# 5.5 k-fold and grouped k-fold
fig,ax=plt.subplots(1,2,figsize=(9,2.8))
for a,title,grouped in zip(ax,["5-fold: rows shuffled individually","Grouped 5-fold: a mix stays in one fold"],[False,True]):
    a.axis("off"); a.set_xlim(0,20); a.set_ylim(-0.5,6.6); a.set_title(title,fontsize=9); rng=np.random.default_rng(0)
    fold=np.repeat(np.arange(5),4) if grouped else rng.permutation(np.repeat(np.arange(5),4))
    for r in range(5):
        for c in range(20): a.add_patch(Rectangle((c,5-r),0.92,0.8,fc=O if fold[c]==r else "#cbd5e0",ec="w"))
        a.text(-0.3,5.4-r,"fold %d"%(r+1),ha="right",va="center",fontsize=7)
    for g_ in range(5): a.plot([4*g_,4*g_+3.92],[0.55,0.55],color=K,lw=2); a.text(4*g_+2,0.05,"mix %d"%(g_+1),ha="center",fontsize=7)
ax[0].text(10,-0.6,"orange = test rows of the fold; cubes of one mix appear on both sides (leakage)",ha="center",fontsize=7,color=R)
ax[1].text(10,-0.6,"each mix is tested exactly once, by a model that never saw it",ha="center",fontsize=7,color=G)
save(fig,"fig5_5_kfold.png")

# 4.4 confusion matrix with definitions
fig,ax=plt.subplots(figsize=(6.4,3)); ax.axis("off"); ax.set_xlim(0,10); ax.set_ylim(0,5)
cells=[(2,2.5,"TP\ncrack found","#c6f6d5"),(4.5,2.5,"FN\ncrack missed","#fed7d7"),(2,0.5,"FP\nfalse alarm","#feebc8"),(4.5,0.5,"TN\ncorrectly clear","#e2e8f0")]
for x,y,t,c in cells: ax.add_patch(Rectangle((x,y),2.4,1.9,fc=c,ec="w",lw=2)); ax.text(x+1.2,y+0.95,t,ha="center",va="center",fontsize=9)
ax.text(3.2,4.6,"model says: crack",ha="center",fontsize=8); ax.text(5.7,4.6,"model says: no crack",ha="center",fontsize=8)
ax.text(1.8,3.45,"truly\ncracked",ha="right",va="center",fontsize=8); ax.text(1.8,1.45,"truly\nsound",ha="right",va="center",fontsize=8)
ax.text(7.2,3.6,"Recall = TP / (TP + FN)\nof the real cracks, how many found",fontsize=8,va="center"); ax.text(7.2,2.3,"Precision = TP / (TP + FP)\nof the alarms, how many real",fontsize=8,va="center")
ax.text(7.2,1.0,"Accuracy = (TP + TN) / all\nmisleading when cracks are rare",fontsize=8,va="center",color=R)
save(fig,"fig4_4_confusion.png")

# 6.5 CNN architecture with the sizes of Example 6.5
fig,ax=plt.subplots(figsize=(9,2.6)); ax.axis("off"); ax.set_xlim(0,18); ax.set_ylim(0,5)
blocks=[(0.3,3.2,"image\n1 x 64 x 64","#e2e8f0"),(3.0,3.2,"conv 3x3 + ReLU\n16 x 64 x 64","#bee3f8"),(5.9,2.2,"max-pool\n16 x 32 x 32","#fefcbf"),(7.9,2.2,"conv 3x3 + ReLU\n32 x 32 x 32","#bee3f8"),(10.8,1.5,"max-pool\n32 x 16 x 16","#fefcbf"),(12.6,1.5,"conv 3x3 + ReLU\n64 x 16 x 16","#bee3f8"),(15.3,0.9,"global max\n64","#fefcbf"),(16.7,0.9,"linear\n2 classes","#c6f6d5")]
x0=None
for x,h,t,c in blocks:
    ax.add_patch(Rectangle((x,2.5-h/2),1.15 if "x" in t else 1.0,h,fc=c,ec=K)); ax.text(x+0.55,2.5+h/2+0.35,t,ha="center",fontsize=6.8)
    if x0 is not None: arr(ax,(x0+1.2,2.5),(x-0.05,2.5))
    x0=x
ax.text(9,0.1,"spatial size halves at each pooling, channels double: 160 + 4,640 + 18,496 + 130 weights (plus 224 batch-norm) = 23,650",ha="center",fontsize=7.5)
save(fig,"fig6_5_cnn.png")

# 12.5 U-Net
fig,ax=plt.subplots(figsize=(8,3.2)); ax.axis("off"); ax.set_xlim(0,16); ax.set_ylim(0,6)
enc=[(1,4.2,"16 ch\n64 x 64"),(3.6,2.6,"32 ch\n32 x 32"),(6.6,1.0,"64 ch\n16 x 16")]; dec=[(9.6,2.6,"32 ch\n32 x 32"),(12.2,4.2,"16 ch\n64 x 64")]
for x,y,t in enc: box(ax,x,y,2,1.1,t,"#bee3f8",B)
for x,y,t in dec: box(ax,x,y,2,1.1,t,"#c6f6d5",G)
box(ax,14.6,4.2,1.2,1.1,"mask","#fefcbf",O)
arr(ax,(2,4.2),(4.4,3.7)); arr(ax,(4.6,2.6),(7.4,2.1)); arr(ax,(8.6,1.6),(10.4,2.6)); arr(ax,(11,3.7),(13,4.2)); arr(ax,(14.2,4.75),(14.6,4.75))
arr(ax,(3,4.75),(12.2,4.75),c=R,ls="--"); arr(ax,(5.6,3.15),(9.6,3.15),c=R,ls="--")
ax.text(7.6,5.05,"skip connection: fine detail (thin cracks) copied across",ha="center",fontsize=7.5,color=R)
ax.text(3.3,1.2,"encoder: pool,\nwhat is it?",ha="center",fontsize=7.5); ax.text(12.4,1.6,"decoder: up-sample,\nwhere is it?",ha="center",fontsize=7.5)
save(fig,"fig12_1_unet.png")

# 16.5 from model to twin
fig,ax=plt.subplots(figsize=(8.6,2.9)); ax.axis("off"); ax.set_xlim(0,12); ax.set_ylim(0,4.4)
for i,(t,sub) in enumerate([("Digital model","no automatic data flow"),("Digital shadow","structure -> model only"),("Digital twin","both directions")]):
    x=0.3+4*i; ax.text(x+1.7,4.1,t,ha="center",fontsize=9.5,weight="bold"); ax.text(x+1.7,3.7,sub,ha="center",fontsize=7.5,color="0.3")
    box(ax,x,2.2,1.4,1.0,"structure\n+ sensors","#e2e8f0",K); box(ax,x+2.0,2.2,1.4,1.0,"model","#bee3f8",B)
    if i==0: ax.plot([x+1.45,x+1.95],[2.7,2.7],color="0.6",ls=":",lw=1.2); ax.text(x+1.7,1.75,"manual update",ha="center",fontsize=7)
    if i>=1: arr(ax,(x+1.42,2.9),(x+1.98,2.9),c=G); ax.text(x+1.7,3.25,"data",ha="center",fontsize=7,color=G)
    if i==2: arr(ax,(x+1.98,2.5),(x+1.42,2.5),c=R); ax.text(x+1.7,1.95,"decision / control",ha="center",fontsize=7,color=R)
ax.text(6,0.8,"Example 16.3 updates one stiffness parameter from frequency and raises an inspection alert: a digital shadow.",ha="center",fontsize=8)
save(fig,"fig16_2_twinlevels.png")

# 13.6 monitoring pipeline
fig,ax=plt.subplots(figsize=(9,2.2)); ax.axis("off"); ax.set_xlim(0,1); ax.set_ylim(0,1)
st=["Measure\n(acceleration,\nstrain, UPV)","Features\n(frequency,\nvelocity, energy)","Remove environment\n(temperature,\nmoisture, load)","Compare with\nreference state\n(control chart)","Alarm rule\nwith a known\nfalse-alarm rate","Engineer inspects\nand decides"]
for i,s in enumerate(st): box(ax,0.005+i*0.166,0.25,0.15,0.55,s,"#fdeee6" if i==5 else "#e8f0fb",O if i==5 else B,7.3)
for i in range(5): arr(ax,(0.155+i*0.166,0.525),(0.171+i*0.166,0.525))
ax.text(0.5,0.05,"most false alarms are born in step 3; most missed damage in step 2",ha="center",fontsize=8,color=R)
save(fig,"fig13_6_pipeline.png")

# 10.5 infinite slope sketch
fig,ax=plt.subplots(figsize=(5.6,3.2)); ax.axis("off"); be=np.radians(28); L_=9
gx=np.array([0,L_]); top=np.tan(be)*gx+2.2; rock=np.tan(be)*gx; wt=np.tan(be)*gx+1.3
ax.fill_between(gx,rock,top,color="#e9d8a6"); ax.fill_between(gx,rock-0.6,rock,color="#a0aec0"); ax.plot(gx,top,color=K); ax.plot(gx,rock,color=K,lw=1.5); ax.plot(gx,wt,color=B,ls="--")
ax.text(8.2,wt[1]-0.75,"water table",color=B,fontsize=8,rotation=28); ax.text(5.6,2.05,"bedrock (slip surface)",fontsize=8,rotation=28)
x1,x2=3.6,5.2; sl=Polygon([[x1,np.tan(be)*x1],[x2,np.tan(be)*x2],[x2,np.tan(be)*x2+2.2],[x1,np.tan(be)*x1+2.2]],fc="none",ec=R,lw=1.3); ax.add_patch(sl)
cx=(x1+x2)/2; cy=np.tan(be)*cx+1.1; ax.annotate("",xy=(cx,cy-1.3),xytext=(cx,cy),arrowprops=dict(arrowstyle="->",color=R,lw=1.5)); ax.text(cx+0.12,cy-0.9,"W",color=R,fontsize=9)
ax.annotate("",xy=(x2+0.9,np.tan(be)*x2+2.2),xytext=(x2+0.9,np.tan(be)*x2),arrowprops=dict(arrowstyle="<->",color=K)); ax.text(x2+1.0,np.tan(be)*x2+1.1,"z",fontsize=9)
ax.annotate("",xy=(x2+1.6,np.tan(be)*x2+1.3),xytext=(x2+1.6,np.tan(be)*x2),arrowprops=dict(arrowstyle="<->",color=B)); ax.text(x2+1.7,np.tan(be)*x2+0.55,"m z",fontsize=9,color=B)
ax.plot([0,2.6],[0,0],color="0.5",lw=0.7); ax.text(1.75,0.22,r"$\beta$",fontsize=11); ax.set_aspect("equal"); ax.set_xlim(-0.2,L_+0.2); ax.set_ylim(-0.8,7.4)
save(fig,"fig10_3_slopesketch.png")

# 14.5 two-phase intersection and its signal plan
fig,ax=plt.subplots(1,2,figsize=(8.4,2.8),gridspec_kw={"width_ratios":[1,1.6]}); a=ax[0]; a.axis("off"); a.set_xlim(-5,5); a.set_ylim(-5,5); a.set_aspect("equal")
a.add_patch(Rectangle((-5,-1),10,2,fc="#cbd5e0")); a.add_patch(Rectangle((-1,-5),2,10,fc="#cbd5e0"))
a.annotate("",xy=(-1.2,-0.45),xytext=(-4.8,-0.45),arrowprops=dict(arrowstyle="->",color=B,lw=2)); a.text(-3,-1.9,"approach 1\n600 veh/h",ha="center",fontsize=8,color=B)
a.annotate("",xy=(0.45,-1.2),xytext=(0.45,-4.8),arrowprops=dict(arrowstyle="->",color=O,lw=2)); a.text(2.7,-3.4,"approach 2\n400 veh/h",ha="center",fontsize=8,color=O)
b_=ax[1]; b_.set_xlim(0,38); b_.set_ylim(0,3); b_.set_yticks([0.75,2.05]); b_.set_yticklabels(["phase 2","phase 1"],fontsize=8); b_.set_xlabel("Time in cycle (s): Webster C = 38 s, greens 18 and 12 s, 4 s lost per change",fontsize=8)
for y,segs in [(1.7,[(0,18,G),(18,4,"#ecc94b"),(22,16,R)]),(0.4,[(0,22,R),(22,12,G),(34,4,"#ecc94b")])]:
    for s0,d,c in segs: b_.add_patch(Rectangle((s0,y),d,0.7,fc=c,ec="w"))
b_.spines[["top","right"]].set_visible(False); fig.tight_layout(); save(fig,"fig14_2_signalplan.png")
print("diagrams done")
