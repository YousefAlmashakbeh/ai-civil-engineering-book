import runpy, io, contextlib, numpy as np
from bookstyle import *
plt.rcParams.update({"font.family": ["DejaVu Sans"], "font.size": 10, "axes.titlesize": 11})
A = "../arab_cases/"; F = "../../figures/"
def run(f):
    with contextlib.redirect_stdout(io.StringIO()): return runpy.run_path(A + f)
# 7 ---------------------------------------------------------------
g = run("c07_solar_pump.py"); t = g["t"]; kMW = g["kMW"]; Qavg = g["Qavg"]
fig, ax = plt.subplots(figsize=(8.6, 3.6))
ax.axvspan(16.5, 22.5, color=TINT[RED], zorder=0); ax.text(19.5, 205, "evening peak tariff", ha="center", color=RED, fontsize=9)
ax.fill_between(t, g["pv"], step="mid", color="#F6E05E", alpha=0.6, label="PV available for pumping")
ax.step(t, np.full(24, kMW*Qavg), where="mid", color=GREY, lw=2, ls="--", label="constant pumping")
ax.step(t, kMW*g["q"], where="mid", color=BLUE, lw=2.4, label="optimised schedule")
ax.set_xlabel("Hour of day"); ax.set_ylabel("Pumping power (MW)"); ax.set_xlim(-0.5, 23.5); ax.set_ylim(0, 215); ax.set_xticks(range(0, 24, 3))
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=3, frameon=False, fontsize=9); ax.set_title("Aqaba-Amman carrier: grid cost -19 % by shifting pumping out of the peak")
save(fig, F + "fig7_5_carrier_schedule.png")
# 9 ---------------------------------------------------------------
g = run("c09_aqaba.py"); pga, lam = g["pga"], g["lam"]
x = np.linspace(0.12, 0.7, 100)
fig, ax = plt.subplots(figsize=(6.6, 4.2))
ax.loglog(x, np.exp(g["c"] + g["k"]*np.log(x)), color=BLUE, lw=2, label="fit to all three points")
kk, cc = np.polyfit(np.log(pga[:2]), np.log(lam[:2]), 1)
ax.loglog(x, np.exp(cc + kk*np.log(x)), color=ORANGE, lw=2, ls="--", label="local fit (475, 975 yr)")
ax.loglog(pga, lam, "o", color=NAVY, ms=8, label="published PSHA, Aqaba")
ax.axvline(0.20, color=RED, lw=1.6); ax.text(0.205, 2.2e-2, "Jordanian code\nPGA = 0.20 g", color=RED, fontsize=9)
ax.axhline(1/475, color=GREY, lw=0.8, ls=":"); ax.text(0.125, 1/475*1.12, "10 % in 50 yr", color=GREY, fontsize=8.5)
ax.fill_betweenx([1/231, 1/145], 0.12, 0.2, color=TINT[RED], zorder=0); ax.text(0.125, 1/185, "code level:\nT = 145-231 yr", fontsize=8.5, color=RED, va="center")
from matplotlib.ticker import FixedLocator, FixedFormatter, NullFormatter
ax.xaxis.set_major_locator(FixedLocator([0.15, 0.2, 0.3, 0.45, 0.6])); ax.xaxis.set_major_formatter(FixedFormatter(["0.15", "0.20", "0.30", "0.45", "0.60"])); ax.xaxis.set_minor_formatter(NullFormatter())
ax.set_xlabel("Peak ground acceleration (g)"); ax.set_ylabel("Annual exceedance rate"); ax.legend(frameon=False, fontsize=8.5, loc="upper right")
ax.set_title("Aqaba: the code value sits at a 145-231 year return period")
save(fig, F + "fig9_5_aqaba_hazard.png")
# 10 --------------------------------------------------------------
g = run("c10_marl.py"); FS = g["FS"]; c = g["c"]; phi = g["phi"]; gg, z = g["g"], g["z"]
betas = np.arange(10, 29); wet = [np.mean(FS(b) < 1) for b in betas]
dry = [np.mean((c + gg*z*np.cos(np.radians(b))**2*np.tan(phi))/(gg*z*np.sin(np.radians(b))*np.cos(np.radians(b))) < 1) for b in betas]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.2, 3.6), gridspec_kw={"width_ratios": [1.3, 1]})
a1.plot(betas, np.array(wet)*100, "-o", color=ORANGE, ms=4, label="wet winter (m = 0.2-1.0)")
a1.plot(betas, np.array(dry)*100, "-o", color=GREEN, ms=4, label="drained (m = 0)")
a1.axvspan(15, 18, color=TINT[RED]); a1.text(16.5, 85, "+3 deg\n= x3 risk", ha="center", color=RED, fontsize=9)
a1.set_xlabel("Cut slope angle (deg)"); a1.set_ylabel("P(FS < 1) (%)"); a1.legend(frameon=False, fontsize=8.5, loc="upper left", bbox_to_anchor=(0.0, 0.78))
f18 = FS(18); a2.hist(f18, bins=70, color=BLUE, alpha=0.8); a2.axvline(1, color=RED, lw=1.8)
a2.text(0.6, a2.get_ylim()[1]*0.85, f"{np.mean(f18<1):.0%}\nfail", color=RED, ha="center"); a2.set_xlabel("Factor of safety at 18 deg"); a2.set_yticks([])
fig.suptitle("Clayey marl cuts, Irbid-Jerash-Amman highway (measured residual strength ranges)", fontsize=11)
save(fig, F + "fig10_6_marl.png")
# 11 --------------------------------------------------------------
g = run("c11_brt.py"); D = np.sort(g["D"]); plan = g["plan"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.2, 3.6), gridspec_kw={"width_ratios": [1.6, 1]})
a1.plot(D, np.linspace(0, 1, D.size), color=BLUE, lw=2.4)
for p, col, lab in ((plan, GREY, "plan"), (np.percentile(D, 50), GREEN, "P50"), (np.percentile(D, 80), ORANGE, "P80")):
    a1.axvline(p, color=col, ls="--", lw=1.4); a1.text(p+0.5, 0.05 if lab.startswith("plan") else 0.3 if lab == "P50" else 0.55, f"{lab}\n{p:.0f} months", color=col, fontsize=9)
a1.set_xlabel("Duration of a 12 km extension (months)"); a1.set_ylabel("Probability of finishing"); a1.set_xlim(40, 95)
a2.bar(["Phase 1\n27.5 km", "Amman-Zarqa\n20 km"], [127.4/27.5, 153/20], color=[BLUE, GREEN], width=0.55)
for i, v in enumerate([127.4/27.5, 153/20]): a2.text(i, v+0.15, f"{v:.2f}", ha="center", fontsize=10)
a2.set_ylabel("Million JD per km"); a2.set_ylim(0, 9)
fig.suptitle("Amman BRT: published costs and the schedule-risk curve of a hypothetical extension", fontsize=11)
save(fig, F + "fig11_5_brt.png")
# 12 --------------------------------------------------------------
g = run("c12_sinkholes.py"); dem = g["dem"]; diam, C = g["diam"], g["C"]
from scipy import ndimage
resid = dem - ndimage.gaussian_filter(dem, 25)
fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.7), gridspec_kw={"width_ratios": [1, 1, 1.2]})
for ax_, px in zip(axs[:2], (1, 5)):
    z = dem[::px, ::px]; r = z - ndimage.gaussian_filter(z, 25/px)
    ax_.imshow(r[:300//px, :300//px], cmap="cividis", extent=(0, 300, 300, 0), vmin=-1.5, vmax=0.3)
    for d, (cx, cy) in zip(diam, C):
        if cx < 300 and cy < 300: ax_.add_patch(plt.Circle((cx, cy), max(d/2, 1.5), fill=False, ec=ORANGE if d < 5 else "white", lw=1.2))
    ax_.set_title(f"{px} m pixels", fontsize=10); ax_.set_xticks([]); ax_.set_yticks([])
rec = {px: g["run"](px)[1] for px in (1, 2, 5)}
xx = np.arange(3); a3 = axs[2]
a3.bar(xx-0.18, [rec[p][diam<5].mean() for p in (1, 2, 5)], 0.36, color=ORANGE, label="< 5 m across")
a3.bar(xx+0.18, [rec[p][diam>=5].mean() for p in (1, 2, 5)], 0.36, color=BLUE, label=">= 5 m across")
a3.set_xticks(xx, ["1 m", "2 m", "5 m"]); a3.set_ylabel("Recall"); a3.set_ylim(0, 1.05); a3.legend(frameon=False, fontsize=8.5); a3.set_xlabel("Pixel size")
fig.suptitle("Dead Sea sinkholes: small holes (orange circles) vanish as pixels grow", fontsize=11)
save(fig, F + "fig12_6_sinkholes.png")
# 13 ---------------------------------------------------------------
g = run("c13_abdoun.py"); days, f, T, res, s, al = g["days"], g["f"], g["T"], g["res"], g["s"], g["al"]
fig, (a1, a2) = plt.subplots(2, 1, figsize=(8.6, 5.0), sharex=True)
a1.axhspan(0.62*0.98, 0.62*1.02, color="#EDF2F7", zorder=0); a1.text(5, 0.62*1.022, "fixed +/-2 % band", fontsize=8.5, color=GREY)
a1.scatter(days, f, c=T, cmap="coolwarm", s=6); a1.axvline(600, color=NAVY, ls="--"); a1.set_ylabel("f1 (Hz)")
a1.text(605, 0.62*1.03, "1 % drop\nfrom day 601", fontsize=8.5, color=NAVY, va="top"); a1.text(240, 0.6015, "colour = daily temperature (blue cold, red hot)", fontsize=8.5, color=GREY)
e = np.zeros_like(res); acc = 0
for i, r in enumerate(res): acc = 0.2*r + 0.8*acc; e[i] = acc
a2.axvspan(0, 365, color=TINT[GREEN], zorder=0); a2.text(10, -5.5, "training year", fontsize=8.5, color=GREEN)
a2.plot(days, e*1000, color=BLUE, lw=1); a2.axhline(-3*s*np.sqrt(0.2/1.8)*1000, color=RED, ls="--"); a2.axvline(600, color=NAVY, ls="--")
a2.set_ylabel("EWMA residual (mHz)"); a2.set_xlabel("Day")
a1.set_title("Abdoun-type bridge: temperature hides a 1 % drop that the residual chart reveals (synthetic data)", fontsize=10.5)
save(fig, F + "fig13_7_abdoun.png")
# 14 --------------------------------------------------------------
g = run("c14_accidents.py"); yr, dth, b = g["yr"], g["dth"], g["b"]
fig, ax = plt.subplots(figsize=(7.6, 3.8))
cols = [RED if y == 2020 else BLUE for y in yr]; ax.bar(yr, dth, color=cols, width=0.6)
for y, d in zip(yr, dth): ax.text(y, d+8, str(d), ha="center", fontsize=9)
xx = np.linspace(2019, 2025, 50); ax.plot(xx, np.exp(b[0]+b[1]*(xx-2019)), color=NAVY, lw=2, label="Poisson trend (-3.3 %/yr)")
ax.errorbar(2025, g["mu25"], yerr=[[g["mu25"]-g["lo"]], [g["hi"]-g["mu25"]]], fmt="D", color=ORANGE, capsize=5, label="2025 forecast, 90 % interval")
ax.text(2020, 230, "COVID\nyear\nz = -6.2", ha="center", color="white", fontsize=8.5)
ax.set_ylim(0, 820); ax.set_ylabel("Road deaths"); ax.set_xticks(list(yr)+[2025]); ax.legend(frameon=False, fontsize=9, loc="upper right", ncol=2)
ax.set_title("Jordan road deaths 2019-2024 (Public Security Directorate figures)")
save(fig, F + "fig14_6_jordan_roads.png")
# 15 --------------------------------------------------------------
g = run("c15_nrw.py"); mnf, ref, sd = g["mnf"], g["ref"], g["sd"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 3.6))
yrs = np.arange(2025, 2041); a1.plot([2022, 2025], [51.7, 41], "o-", color=NAVY, label="reported")
a1.plot(yrs, 15+(41-15)*np.exp(-g["r"]*(yrs-2025)), "--", color=BLUE, label="diminishing-returns path")
a1.plot([2025, 2040], [41, 25], ":", color=GREY, label="straight line to target")
a1.axhline(25, color=GREEN, lw=1.5); a1.text(2030, 25.8, "national target 25 % (2040)", color=GREEN, fontsize=8.5)
a1.set_ylabel("Non-revenue water (%)"); a1.set_xticks([2022, 2025, 2030, 2035, 2040]); a1.legend(frameon=False, fontsize=8.5); a1.set_ylim(10, 55)
dd = np.arange(1, mnf.size+1); a2.plot(dd, mnf, "o-", ms=3, color=BLUE); a2.axhline(ref, color=GREY, ls="--"); a2.axvline(38, color=RED, ls="--")
a2.text(38.5, mnf.max()*0.97, "CUSUM alarm\nday 38", color=RED, fontsize=9); a2.axhline(g["legit"], color=GREEN, lw=1)
a2.text(2, g["legit"]+0.3, "legitimate night use", color=GREEN, fontsize=8.5); a2.set_xlabel("Day"); a2.set_ylabel("Minimum night flow (m3/h)")
fig.suptitle("Jordan non-revenue water: national path (left) and leak detection in a synthetic DMA (right)", fontsize=11)
save(fig, F + "fig15_5_nrw.png")
# 16 --------------------------------------------------------------
g = run("c16_carrier.py"); est, ft = g["est"], g["f_true"]; band = 1.96*np.sqrt(g["Pk"])
fig, ax = plt.subplots(figsize=(8.0, 3.6)); d = np.arange(est.size)
ax.plot(d, ft, color=NAVY, lw=2, label="true friction factor (synthetic)"); ax.plot(d, est, color=ORANGE, lw=1.5, label="twin estimate (Kalman filter)")
ax.fill_between(d, est-band, est+band, color=ORANGE, alpha=0.25); ax.axvline(500, color=GREY, ls=":")
ax.text(505, 0.0113, "sudden\nscaling step", color=GREY, fontsize=8.5)
ax2 = ax.twinx(); ax2.set_ylim(*[1000*9.81*g["Q"]*(g["hf"](v)-g["hf"](0.011))/0.85/1e6 for v in ax.get_ylim()]); ax2.set_ylabel("extra pumping power (MW)")
ax2.spines["right"].set_visible(True)
ax.set_xlabel("Day"); ax.set_ylabel("Darcy friction factor f"); ax.legend(frameon=False, fontsize=9, loc="upper left")
ax.set_title("National Water Carrier: a twin that turns pressure readings into megawatts")
save(fig, F + "fig16_6_carrier_twin.png")
print("done")
