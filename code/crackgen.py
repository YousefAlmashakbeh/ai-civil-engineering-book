import numpy as np
from scipy.ndimage import gaussian_filter
def concrete_bg(rng, n=64):
    img = 0.55 + 0.08*gaussian_filter(rng.normal(0,1,(n,n)), 1.2) + 0.03*rng.normal(0,1,(n,n))
    for _ in range(rng.integers(3,12)):                      # pores
        y,x = rng.integers(0,n,2); r=rng.uniform(0.6,1.6)
        yy,xx=np.ogrid[:n,:n]; img[(yy-y)**2+(xx-x)**2<=r*r] -= rng.uniform(0.1,0.25)
    gy,gx = np.mgrid[:n,:n]/n; img += rng.uniform(-0.12,0.12)*gx + rng.uniform(-0.12,0.12)*gy  # lighting
    if rng.random()<0.3:                                      # shadow band
        a=rng.uniform(0,np.pi); d=(gx-0.5)*np.cos(a)+(gy-0.5)*np.sin(a); img[d>rng.uniform(-0.3,0.3)] -= rng.uniform(0.08,0.18)
    return img
def draw_path(img, pts, width, depth):
    n=img.shape[0]; yy,xx=np.mgrid[:n,:n]; m=np.zeros_like(img)
    for (y0,x0),(y1,x1) in zip(pts[:-1],pts[1:]):
        for t in np.linspace(0,1,8):
            y=y0+(y1-y0)*t; x=x0+(x1-x0)*t
            m=np.maximum(m, np.exp(-((yy-y)**2+(xx-x)**2)/(2*(width/2)**2)))
    return img - depth*m, m>0.5
def crack(img, rng):
    n=img.shape[0]; y,x=rng.uniform(16,48,2); a=rng.uniform(0,2*np.pi); pts=[(y,x)]
    for _ in range(rng.integers(8,16)):
        a+=rng.normal(0,0.6); y+=3.5*np.sin(a); x+=3.5*np.cos(a)
        if not (4<y<60 and 4<x<60): a+=np.pi; y=np.clip(y,4,60); x=np.clip(x,4,60)
        pts.append((y,x))
    return draw_path(img, pts, rng.uniform(0.8,2.6), rng.uniform(0.15,0.45))
def joint(img, rng):                                           # straight formwork joint = hard negative
    n=img.shape[0]; a=rng.uniform(0,np.pi); c=rng.uniform(16,48)
    p0=(c-40*np.sin(a), c-40*np.cos(a)); p1=(c+40*np.sin(a), c+40*np.cos(a))
    return draw_path(img,[p0,p1],rng.uniform(1.0,2.2),rng.uniform(0.15,0.4))
def make_images(N, seed=0, joints=True):
    rng=np.random.default_rng(seed); X=np.zeros((N,64,64),np.float32); y=np.zeros(N,np.int64); M=np.zeros((N,64,64),bool)
    for i in range(N):
        img=concrete_bg(rng)
        if rng.random()<0.5: img,M[i]=crack(img,rng); y[i]=1
        elif joints and rng.random()<0.4: img,_=joint(img,rng)
        X[i]=np.clip(img,0,1)
    return X,y,M
