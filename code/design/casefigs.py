import runpy, io, contextlib, numpy as np
from bookstyle import *
plt.rcParams.update({"font.family": ["DejaVu Sans"], "font.size": 9.5, "axes.titlesize": 10.5, "xtick.color": "#4A5568", "ytick.color": "#4A5568",
                     "axes.edgecolor": "#4A5568", "axes.labelcolor": "#1A202C", "xtick.labelsize": 9, "ytick.labelsize": 9})
AR = dict(family="Amiri"); LEG = dict(prop={"family": "Amiri", "size": 9.5}, frameon=False)
def T(ax, x, y, s, **k): k.setdefault("fontsize", 10); return ax.text(x, y, s, fontfamily="Amiri", **k)
def XL(ax, s): ax.set_xlabel(s, fontfamily="Amiri", fontsize=10.5)
def YL(ax, s): ax.set_ylabel(s, fontfamily="Amiri", fontsize=10.5)
A = "../arab_cases/"; F = "../../figures/"
def run(f):
    with contextlib.redirect_stdout(io.StringIO()): return runpy.run_path(A + f)
# 7 ---------------------------------------------------------------
g = run("c07_solar_pump.py"); t = g["t"]; kMW = g["kMW"]; Qavg = g["Qavg"]
fig, ax = plt.subplots(figsize=(5.8, 3.3))
ax.axvspan(16.5, 22.5, color=TINT[RED], zorder=0); T(ax, 19.5, 203, "ذروة التعرفة المسائية", ha="center", color=RED)
ax.fill_between(t, g["pv"], step="mid", color="#F6E05E", alpha=0.6, label="طاقة شمسية متاحة للضخ")
ax.step(t, np.full(24, kMW*Qavg), where="mid", color=GREY, lw=2, ls="--", label="ضخ ثابت")
ax.step(t, kMW*g["q"], where="mid", color=BLUE, lw=2.4, label="الجدول الأمثل")
XL(ax, "ساعة اليوم"); YL(ax, "قدرة الضخ (MW)"); ax.set_xlim(-0.5, 23.5); ax.set_ylim(0, 215); ax.set_xticks(range(0, 24, 3))
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3, **LEG)
save(fig, F + "fig7_5_carrier_schedule.png")
# 9 ---------------------------------------------------------------
g = run("c09_aqaba.py"); pga, lam = g["pga"], g["lam"]
x = np.linspace(0.12, 0.7, 100)
fig, ax = plt.subplots(figsize=(5.0, 3.7))
ax.loglog(x, np.exp(g["c"] + g["k"]*np.log(x)), color=BLUE, lw=2, label="ملاءمة النقاط الثلاث")
kk, cc = np.polyfit(np.log(pga[:2]), np.log(lam[:2]), 1)
ax.loglog(x, np.exp(cc + kk*np.log(x)), color=ORANGE, lw=2, ls="--", label="ملاءمة محلية (475 و975 سنة)")
ax.loglog(pga, lam, "o", color=NAVY, ms=7, label="قيم الدراسة (تربة صلبة)")
ax.axvline(0.20, color=RED, lw=1.6); T(ax, 0.205, 1.25e-2, "الكود الأردني\nPGA = 0.20 g", color=RED, fontsize=9.5)
ax.axhline(1/475, color=GREY, lw=0.8, ls=":"); T(ax, 0.48, 1/475*1.15, "⁦10%⁩ في 50 سنة", color=GREY, fontsize=9, ha="center")
ax.fill_betweenx([1/172, 1/122], 0.12, 0.2, color=TINT[RED], zorder=0)
ax.annotate("مستوى الكود:\nفترة عودة 122–172 سنة", xy=(0.2, 1/145), xytext=(0.212, 2.6e-4), fontsize=9.5, color=RED, family="Amiri",
            arrowprops=dict(arrowstyle="->", color=RED, lw=0.9))
from matplotlib.ticker import FixedLocator, FixedFormatter, NullFormatter
ax.xaxis.set_major_locator(FixedLocator([0.15, 0.2, 0.3, 0.4, 0.5, 0.6])); ax.xaxis.set_major_formatter(FixedFormatter(["0.15", "0.20", "0.30", "0.40", "0.50", "0.60"])); ax.xaxis.set_minor_formatter(NullFormatter())
XL(ax, "أقصى تسارع أرضي PGA (g)"); YL(ax, "معدل التجاوز السنوي"); ax.legend(loc="upper right", bbox_to_anchor=(1.03, 1.03), handlelength=1.6, **LEG)
save(fig, F + "fig9_5_aqaba_hazard.png")
# 10 --------------------------------------------------------------
g = run("c10_marl.py"); FS = g["FS"]; c = g["c"]; phi = g["phi"]; gg, z = g["g"], g["z"]
betas = np.arange(10, 29); wet = [np.mean(FS(b) < 1) for b in betas]
dry = [np.mean((c + gg*z*np.cos(np.radians(b))**2*np.tan(phi))/(gg*z*np.sin(np.radians(b))*np.cos(np.radians(b))) < 1) for b in betas]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.8, 3.2), gridspec_kw={"width_ratios": [1.35, 1]})
a1.plot(betas, np.array(wet)*100, "-o", color=ORANGE, ms=4, label="شتاء رطب (منسوب ماء مرتفع)")
a1.plot(betas, np.array(dry)*100, "--s", color=GREEN, ms=4, label="مع الصرف الكامل")
a1.axvspan(15, 18, color=TINT[RED]); T(a1, 16.5, 58, "زيادة 3 درجات\n= ثلاثة أضعاف\nالخطر", ha="center", color=RED, fontsize=9)
XL(a1, "ميل طبقة الانزلاق (درجة)"); YL(a1, "احتمال الانهيار (%)"); a1.legend(loc="upper center", bbox_to_anchor=(0.75, -0.24), ncol=2, **LEG)
f18 = FS(18); a2.hist(f18, bins=60, color=BLUE, alpha=0.8); a2.axvline(1, color=RED, lw=1.8)
T(a2, 0.62, a2.get_ylim()[1]*0.8, "⁦" + f"{np.mean(f18<1):.0%}" + "⁩\nانهيار", color=RED, ha="center"); XL(a2, "معامل الأمان عند 18°"); a2.set_yticks([])
save(fig, F + "fig10_6_marl.png")
# 11 --------------------------------------------------------------
g = run("c11_brt.py"); D = np.sort(g["D"]); plan = g["plan"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.8, 3.2), gridspec_kw={"width_ratios": [1.6, 1]})
a1.plot(D, np.linspace(0, 1, D.size), color=BLUE, lw=2.4)
for p, col, lab, ha_, yy in ((plan, GREY, "الخطة", "right", 1.03), (np.percentile(D, 50), GREEN, "P50", "center", 1.2), (np.percentile(D, 80), ORANGE, "P80", "left", 1.03)):
    a1.axvline(p, color=col, ls="--", lw=1.4); T(a1, p + {"right": 0.6, "center": 0, "left": -0.6}[ha_], yy, f"{lab}\n{p:.0f} شهراً", color=col, fontsize=9, ha=ha_, va="bottom")
XL(a1, "مدة امتداد طوله 12 كم (شهر)"); YL(a1, "احتمال الإنجاز"); a1.set_xlim(40, 95); a1.set_ylim(0, 1.0)
a2.bar([0, 1], [127.4/27.5, 153/20], color=[BLUE, GREEN], width=0.55); a2.set_xticks([0, 1])
a2.set_xticklabels(["المرحلة الأولى\n27.5 كم", "عمّان–الزرقاء\n20 كم"], fontfamily="Amiri", fontsize=9.5)
for i, v in enumerate([127.4/27.5, 153/20]): a2.text(i, v+0.15, f"{v:.2f}", ha="center", fontsize=9.5)
YL(a2, "مليون دينار لكل كم"); a2.yaxis.labelpad = 6; a2.set_ylim(0, 9)
fig.subplots_adjust(wspace=0.38)
save(fig, F + "fig11_5_brt.png")
# 12 --------------------------------------------------------------
g = run("c12_sinkholes.py"); dem = g["dem"]; diam, C = g["diam"], g["C"]
from scipy import ndimage
fig, axs = plt.subplots(1, 3, figsize=(5.8, 2.9), gridspec_kw={"width_ratios": [1.3, 1.3, 1]})
for ax_, px in zip(axs[:2], (1, 5)):
    z = dem[::px, ::px]; r = z - ndimage.gaussian_filter(z, 25/px)
    ax_.imshow(r[:300//px, :300//px], cmap="Greys_r", extent=(0, 300, 300, 0), vmin=-1.5, vmax=0.3)
    for d, (cx, cy) in zip(diam, C):
        if cx < 300 and cy < 300:
            small = d < 5; ax_.add_patch(plt.Circle((cx, cy), max(d/2, 6 if small else 1.5), fill=False, ec=ORANGE if small else "#63B3ED", lw=1.3 if small else 1.0))
    ax_.set_title(f"بكسل {px} م", fontfamily="Amiri", fontsize=10.5); ax_.set_xticks([]); ax_.set_yticks([])
    ax_.plot([215, 265], [280, 280], color="white", lw=2.5); ax_.text(240, 268, "50 m", color="white", ha="center", fontsize=8)
rec = {px: g["run"](px)[1] for px in (1, 2, 5)}
xx = np.arange(3); a3 = axs[2]
a3.bar(xx-0.18, [rec[p][diam<5].mean() for p in (1, 2, 5)], 0.36, color=ORANGE, label="أصغر من 5 م")
a3.bar(xx+0.18, [rec[p][diam>=5].mean() for p in (1, 2, 5)], 0.36, color=BLUE, hatch="//", edgecolor="white", label="5 م فأكثر")
a3.set_xticks(xx, ["1 m", "2 m", "5 m"]); YL(a3, "الاستدعاء"); a3.set_ylim(0, 1.05); a3.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, **LEG); XL(a3, "حجم البكسل")
fig.subplots_adjust(wspace=0.45, bottom=0.2)
b0 = axs[0].get_position(); b1 = axs[1].get_position()
fig.text((b0.x0 + b1.x1) / 2, 0.06, "الدوائر حفر خسفية معروفة: البرتقالية أصغر من 5 م، والزرقاء 5 م فأكثر", ha="center", fontsize=9, fontfamily="Amiri", color="#2D3748")
save(fig, F + "fig12_6_sinkholes.png")
# 13 ---------------------------------------------------------------
g = run("c13_abdoun.py"); days, f, T_, res, s, al = g["days"], g["f"], g["T"], g["res"], g["s"], g["al"]
fig, (a1, a2) = plt.subplots(2, 1, figsize=(5.8, 4.4), sharex=True)
a1.axhspan(0.62*0.98, 0.62*1.02, color="#EDF2F7", zorder=0); T(a1, 0.0, 1.03, "نطاق ثابت ⁦±2%⁩ حول التردد المرجعي", fontsize=9, color=GREY, transform=a1.transAxes)
a1.scatter(days, f, c=T_, cmap="coolwarm", s=5); a1.axvline(600, color=NAVY, ls="--"); a1.set_ylabel("f1 (Hz)")
T(a1, 605, 0.62*1.03, "انخفاض ⁦1%⁩\nمن اليوم 601", fontsize=9, color=NAVY, va="top"); T(a1, 590, 0.6015, "اللون: حرارة اليوم، الأزرق بارد والأحمر حار", fontsize=9, color=GREY, ha="right")
e = np.zeros_like(res); acc = 0
for i, r in enumerate(res): acc = 0.2*r + 0.8*acc; e[i] = acc
a2.axvspan(0, 365, color=TINT[GREEN], zorder=0); T(a2, 10, -5.5, "سنة التدريب", fontsize=9, color=GREEN)
a2.plot(days, e*1000, color=BLUE, lw=1); a2.axhline(-3*s*np.sqrt(0.2/1.8)*1000, color=RED, ls="--"); a2.axvline(600, color=NAVY, ls="--")
T(a2, 380, -3*s*np.sqrt(0.2/1.8)*1000*1.15, "حدّ الإنذار", fontsize=9, color=RED, va="top")
YL(a2, "\u2067EWMA للبواقي (mHz)\u2069"); XL(a2, "اليوم")
save(fig, F + "fig13_7_abdoun.png")
# 14 --------------------------------------------------------------
g = run("c14_accidents.py"); yr, dth, b = g["yr"], g["dth"], g["b"]
fig, ax = plt.subplots(figsize=(5.8, 3.3))
cols = [RED if y == 2020 else BLUE for y in yr]; ax.bar(yr, dth, color=cols, width=0.6)
for y, d in zip(yr, dth): ax.text(y, d+8, str(d), ha="center", fontsize=9)
xx = np.linspace(2019, 2025, 50); ax.plot(xx, np.exp(b[0]+b[1]*(xx-2019)), color=NAVY, lw=2, label="اتجاه بواسون (دون 2020)")
ax.errorbar(2025, g["mu25"], yerr=[[g["mu25"]-g["lo"]], [g["hi"]-g["mu25"]]], fmt="D", color=ORANGE, capsize=5, label="توقع 2025 بفترة ⁦90%⁩")
ax.plot([2025.18], [510], marker="*", ms=11, color=GREEN, ls="none", label="الفعلي لعام 2025 (510)"); 
T(ax, 2020, 230, "سنة\nالإغلاق", ha="center", color="white", fontsize=9.5)
ax.set_ylim(0, 820); YL(ax, "وفيات الطرق"); ax.set_xticks(list(yr)+[2025]); ax.legend(loc="upper right", ncol=2, **LEG)
save(fig, F + "fig14_6_jordan_roads.png")
# 15 --------------------------------------------------------------
g = run("c15_nrw.py"); mnf, ref, sd = g["mnf"], g["ref"], g["sd"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(5.8, 3.2))
yrs = np.arange(2025, 2041); a1.plot([2022, 2025], [51.7, 41], "o-", color=NAVY, label="المنشور")
a1.plot(yrs, 15+(41-15)*np.exp(-g["r"]*(yrs-2025)), "--", color=BLUE, label="مسار العائد المتناقص")
a1.plot([2025, 2040], [41, 25], ":", color=GREY, label="خط مستقيم إلى الهدف")
a1.axhline(25, color=GREEN, lw=1.5); T(a1, 2022.3, 23.5, "الهدف الوطني ⁦25%⁩ (2040)", color=GREEN, fontsize=9, ha="left", va="top")
YL(a1, "المياه غير المحاسب عليها (%)"); a1.set_xticks([2022, 2030, 2040]); a1.legend(loc="upper right", **LEG); a1.set_ylim(10, 55)
dd = np.arange(1, mnf.size+1); a2.plot(dd, mnf, "o-", ms=3, color=BLUE); a2.axhline(ref, color=GREY, ls="--"); a2.axvline(38, color=RED, ls="--")
T(a2, 37, mnf.max()*0.98, "إنذار CUSUM\nاليوم 38", color=RED, fontsize=9, ha="right", va="top"); a2.axhline(g["legit"], color=GREEN, lw=1)
T(a2, 2, g["legit"]+0.3, "الاستهلاك الليلي المشروع", color=GREEN, fontsize=9); XL(a2, "اليوم"); YL(a2, "أقل تدفق ليلي (m³/h)")
save(fig, F + "fig15_5_nrw.png")
# 16 --------------------------------------------------------------
g = run("c16_carrier.py"); est, ft = g["est"], g["f_true"]; band = 1.96*np.sqrt(g["Pk"])
fig, ax = plt.subplots(figsize=(5.8, 3.2)); d = np.arange(est.size)
ax.plot(d, ft, color=NAVY, lw=2, label="معامل الاحتكاك الحقيقي (اصطناعي)"); ax.plot(d, est, color=ORANGE, lw=1.5, ls="--", label="تقدير التوأم (مرشح كالمان)")
ax.fill_between(d, est-band, est+band, color=ORANGE, alpha=0.25); ax.axvline(500, color=GREY, ls=":")
T(ax, 505, 0.0113, "قفزة مفاجئة\nفي الترسّبات", color=GREY, fontsize=9)
ax2 = ax.twinx(); ax2.set_ylim(*[1000*9.81*g["Q"]*(g["hf"](v)-g["hf"](0.011))/0.85/1e6 for v in ax.get_ylim()]); YL(ax2, "قدرة ضخ إضافية (MW)")
ax2.spines["right"].set_visible(True); ax2.tick_params(colors="#4A5568")
XL(ax, "اليوم"); YL(ax, "معامل احتكاك دارسي f"); ax.legend(loc="upper left", **LEG)
save(fig, F + "fig16_6_carrier_twin.png")
print("done")
