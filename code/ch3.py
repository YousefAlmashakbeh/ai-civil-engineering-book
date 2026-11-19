import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
# Example 3.1 beam capacity table
beams = pd.DataFrame({
 "beam": ["B1","B2","B3","B4","B5","B6"],
 "b_mm": [250,250,300,300,300,350],
 "d_mm": [450,450,540,540,640,640],
 "As_mm2":[942,1232,1232,1608,1608,2412],
 "fc_MPa":[28,28,28,32,32,32],
 "Mu_kNm":[120,190,210,320,330,520]})
fy = 420
beams["a_mm"] = beams.As_mm2*fy/(0.85*beams.fc_MPa*beams.b_mm)
beams["phiMn_kNm"] = 0.9*beams.As_mm2*fy*(beams.d_mm-beams.a_mm/2)/1e6
beams["ratio"] = beams.Mu_kNm/beams.phiMn_kNm
beams["OK"] = np.where(beams.ratio<=1.0, "OK", "FAIL")
print(beams[["beam","a_mm","phiMn_kNm","Mu_kNm","ratio","OK"]].round(2).to_string(index=False))
fig, ax = plt.subplots(figsize=(7,3.6))
x = np.arange(len(beams))
ax.bar(x-0.2, beams.phiMn_kNm, 0.4, label="Capacity  phi*Mn", color="#2b6cb0")
ax.bar(x+0.2, beams.Mu_kNm, 0.4, label="Demand  Mu", color="#dd6b20")
ax.set_xticks(x, beams.beam); ax.set_ylabel("Moment (kN.m)"); ax.legend(frameon=False)
ax.spines[["top","right"]].set_visible(False)
for i,r in beams.iterrows():
    if r.OK=="FAIL": ax.annotate("FAIL", (i+0.2, r.Mu_kNm+8), ha="center", color="#c53030", fontweight="bold")
fig.tight_layout(); fig.savefig("fig/fig3_1_beams.png", dpi=200)

# Example 3.2 accelerometer FFT
fs, T = 100, 60
t = np.arange(0, T, 1/fs)
rng = np.random.default_rng(3)
acc = 0.02*np.sin(2*np.pi*4.03*t) + 0.006*np.sin(2*np.pi*10.07*t) + rng.normal(0, 0.02, t.size)
spec = np.abs(np.fft.rfft(acc))/t.size
freq = np.fft.rfftfreq(t.size, 1/fs)
top = freq[np.argsort(spec)[-2:]][::-1]
print("peaks (Hz):", np.round(top, 2))
fig, ax = plt.subplots(1,2, figsize=(8,3.2))
ax[0].plot(t[:500], acc[:500], lw=0.8, color="#2d3748"); ax[0].set_xlabel("Time (s)"); ax[0].set_ylabel("Acceleration (g)")
ax[1].plot(freq, spec, lw=0.9, color="#2b6cb0"); ax[1].set_xlim(0,20); ax[1].set_xlabel("Frequency (Hz)"); ax[1].set_ylabel("Amplitude")
for f0 in top: ax[1].annotate(f"{f0:.2f} Hz",(f0, spec[np.argmin(abs(freq-f0))]), textcoords="offset points", xytext=(6,0), fontsize=8)
for a in ax: a.spines[["top","right"]].set_visible(False)
fig.set_layout_engine("tight", w_pad=2.5); fig.savefig("fig/fig3_2_fft.png", dpi=200)   # w_pad: the right y-label stays clear of the left panel
print("SNR time-domain: signal amp 0.02 vs noise sd 0.02")
