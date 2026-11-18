# Dead Sea sinkholes (Ghor Al-Haditha): growth of the inventory + detecting sinkholes in a synthetic elevation model
# published: 1,565 sinkholes (2018) -> 2,247 (2024); diameters 0.8-72.9 m, lognormal with mu = 1.97 (ln m)
import numpy as np
from scipy import ndimage
n18, n24 = 1565, 2247
print(f"growth: {(n24-n18)/6:.0f} new sinkholes per year, +{n24/n18-1:.0%} in six years -> linear 2030 estimate {n24+(n24-n18):.0f}")
rng = np.random.default_rng(2); N = 600                            # 600 x 600 m tile at 1 m
yy, xx = np.mgrid[0:N, 0:N].astype(float)
dem = -400 + 0.01*xx + 0.6*np.sin(xx/90)*np.cos(yy/70) + rng.normal(0, 0.05, (N, N))
diam = np.clip(rng.lognormal(1.97, 0.7, 60), 0.8, 40)              # sigma 0.7 is an assumption
C = rng.uniform(25, N-25, (60, 2))
for d, (cx, cy) in zip(diam, C):
    dem -= 0.3*d*np.exp(-((xx-cx)**2 + (yy-cy)**2)/(2*(d/4)**2))
def run(px, thr=0.25, min_px=3):
    k = int(px); z = dem[::k, ::k]
    resid = z - ndimage.gaussian_filter(z, 25/px)                  # remove the regional surface
    lab, n = ndimage.label(resid < -thr)
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n+1)); keep = np.isin(lab, 1 + np.where(sizes >= min_px)[0])
    lab, n = ndimage.label(keep); cm = np.array(ndimage.center_of_mass(keep, lab, range(1, n+1))).reshape(-1, 2)*px
    hit = np.array([np.any(np.hypot(cm[:, 1]-cx, cm[:, 0]-cy) < max(d/2, px)) for d, (cx, cy) in zip(diam, C)]) if n else np.zeros(60, bool)
    tp = sum(np.any(np.hypot(C[:, 0]-x, C[:, 1]-y) < np.maximum(diam/2, px)) for y, x in cm)
    return n, hit, tp
for px in (1, 2, 5):
    n, hit, tp = run(px)
    print(f"pixel {px} m: {n:3d} detections, precision {tp/max(n,1):.2f}, recall {hit.mean():.2f}, "
          f"recall for < 5 m: {hit[diam<5].mean():.2f}, for >= 5 m: {hit[diam>=5].mean():.2f}")
print(f"sinkholes < 5 m across in this tile: {np.sum(diam<5)} of 60")
