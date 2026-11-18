# -*- coding: utf-8 -*-
"""Modern front covers (A4 proportion): dark 'network arch' and light 'dot matrix' variants."""
from tk import *
import tk, math
tk.PRE = tk.PRE.replace("border=7pt", "border=0pt")
tk.COL.update(ink0="081A30", deep="0E2A4A", sea="14507A", amber="F6AD55", mist="F4F7FA", steel="A0AEC0")
W, H = 21.0, 29.7
def arch_nodes(x0=2.6, x1=18.4, yb=13.6, rise=6.6, n=9):
    bot = [(x0 + i*(x1-x0)/(n-1), yb) for i in range(n)]
    top = []
    for i in range(n-1):
        xm = (bot[i][0] + bot[i+1][0])/2; t = (xm - x0)/(x1 - x0)
        top.append((xm, yb + 1.3 + rise*math.sin(math.pi*t)))
    return bot, top
def titles(f, col_title, col_sub, col_txt, y0=8.6):
    xr = W - 2.0
    f.add(r"\node[anchor=east,text=%s,font=\fontsize{46}{56}\selectfont\bfseries,inner sep=0pt] at (%.2f,%.2f) {%s};" % (col_title, xr, y0, R("الذكاء الاصطناعي")))
    f.add(r"\node[anchor=east,text=%s,font=\fontsize{46}{56}\selectfont\bfseries,inner sep=0pt] at (%.2f,%.2f) {%s};" % (col_title, xr, y0 - 2.15, R("في الهندسة المدنية")))
    f.add(r"\fill[%s] (%.2f,%.2f) rectangle (%.2f,%.2f);" % (col_sub, xr - 3.2, y0 - 3.72, xr, y0 - 3.62))
    f.add(r"\node[anchor=east,text=%s,font=\fontsize{21}{26}\selectfont,inner sep=0pt] at (%.2f,%.2f) {%s};" % (col_sub, xr, y0 - 4.55, R("من المبادئ إلى التطبيق")))
    f.add(r"\node[anchor=east,text=%s,font=\fontsize{17}{22}\selectfont\bfseries,inner sep=0pt] at (%.2f,2.25) {%s};" % (col_txt, xr, R("م. د. يوسف المشاقبة")))
    f.add(r"\node[anchor=east,text=%s,opacity=0.8,font=\fontsize{12}{15}\selectfont,inner sep=0pt] at (%.2f,1.5) {%s};" % (col_txt, xr, R("الجامعة الهاشمية")))
    f.add(r"\node[anchor=west,text=%s,opacity=0.8,font=\fontsize{12}{15}\selectfont,inner sep=0pt] at (2.0,1.5) {%s};" % (col_txt, R("الطبعة الأولى — 2026")))
def cover_dark():
    f = Fig("cover"); bot, top = arch_nodes()
    f.add(r"\shade[top color=ink0,bottom color=deep,middle color=deep] (0,0) rectangle (%.1f,%.1f);" % (W, H))
    f.add(r"\shade[inner color=sea,outer color=deep,opacity=0.9] (10.5,18.5) circle (9.5);")
    f.add(r"\begin{scope}\clip (0,0) rectangle (%.1f,%.1f);" % (W, H))
    for r_ in (4.2, 6.4, 8.6, 10.8, 13.0): f.add(r"\draw[white,opacity=0.05,line width=0.6pt] (10.5,13.6) circle (%.1f);" % r_)
    f.add(r"\end{scope}")
    f.add(r"\fill[amber] (%.2f,0) rectangle (%.1f,%.1f);" % (W - 0.42, W, H))
    # input layer above the arch
    inp = [(3.4 + i*2.84, 25.4) for i in range(6)]
    for ix, iy in inp:
        for tx, ty in top[1:-1]:
            f.add(r"\draw[white,opacity=0.10,line width=0.5pt] (%.2f,%.2f) -- (%.2f,%.2f);" % (ix, iy, tx, ty))
    lw = "line width=1.5pt,line cap=round"
    for i in range(len(top)):
        f.add(r"\draw[white,opacity=0.55,%s] (%.2f,%.2f) -- (%.2f,%.2f) -- (%.2f,%.2f);" % (lw, bot[i][0], bot[i][1], top[i][0], top[i][1], bot[i+1][0], bot[i+1][1]))
    f.add(r"\draw[amber,line width=2.6pt,line cap=round,line join=round] " + " -- ".join("(%.2f,%.2f)" % p for p in [bot[0]] + top + [bot[-1]]) + ";")
    f.add(r"\draw[white,line width=3.2pt,line cap=round] (1.2,%.2f) -- (%.2f,%.2f);" % (bot[0][1], W - 1.6, bot[0][1]))
    for x, y in bot: f.add(r"\fill[white,opacity=0.18] (%.2f,%.2f) circle (0.42); \fill[white] (%.2f,%.2f) circle (0.21); \fill[deep] (%.2f,%.2f) circle (0.09);" % (x, y, x, y, x, y))
    for x, y in top: f.add(r"\fill[amber,opacity=0.22] (%.2f,%.2f) circle (0.46); \fill[amber] (%.2f,%.2f) circle (0.23); \fill[deep] (%.2f,%.2f) circle (0.09);" % (x, y, x, y, x, y))
    for x, y in inp: f.add(r"\fill[white,opacity=0.15] (%.2f,%.2f) circle (0.36); \draw[white,line width=1.2pt] (%.2f,%.2f) circle (0.17);" % (x, y, x, y))
    f.add(r"\node[anchor=north east,text=white,opacity=0.75,font=\fontsize{11}{14}\selectfont,inner sep=0pt] at (%.2f,%.2f) {%s};" % (W - 2.0, H - 1.5, R("هندسة مدنية  •  تعلّم الآلة  •  بيانات مفتوحة  •  حالات عربية")))
    titles(f, "white", "amber", "white")
    f.add(r"\path[use as bounding box] (0,0) rectangle (%.1f,%.1f);" % (W, H)); f.build(dpi=200)
def cover_light():
    f = Fig("cover_alt"); bot, top = arch_nodes(yb=15.2, rise=6.0)
    f.add(r"\fill[mist] (0,0) rectangle (%.1f,%.1f);" % (W, H))
    f.add(r"\fill[navy] (0,0) rectangle (%.1f,3.6);" % W)
    f.add(r"\fill[orange] (%.2f,3.6) rectangle (%.1f,%.1f);" % (W - 0.42, W, H))
    pts = bot + top
    for i in range(27):
        for j in range(19):
            x, y = 1.6 + i*0.68, 13.2 + j*0.68
            d = min(math.hypot(x - a, y - b) for a, b in pts)
            if d < 0.45: continue
            f.add(r"\fill[steel,opacity=%.2f] (%.2f,%.2f) circle (0.045);" % (0.75 if d > 1.2 else 0.3, x, y))
    for i in range(len(top)):
        f.add(r"\draw[blue,line width=1.4pt,line cap=round,line join=round] (%.2f,%.2f) -- (%.2f,%.2f) -- (%.2f,%.2f);" % (bot[i][0], bot[i][1], top[i][0], top[i][1], bot[i+1][0], bot[i+1][1]))
    f.add(r"\draw[orange,line width=2.6pt,line cap=round,line join=round] " + " -- ".join("(%.2f,%.2f)" % p for p in [bot[0]] + top + [bot[-1]]) + ";")
    f.add(r"\draw[navy,line width=3.2pt,line cap=round] (1.4,%.2f) -- (%.2f,%.2f);" % (bot[0][1], W - 1.8, bot[0][1]))
    for x, y in bot: f.add(r"\fill[navy] (%.2f,%.2f) circle (0.22); \fill[mist] (%.2f,%.2f) circle (0.09);" % (x, y, x, y))
    for x, y in top: f.add(r"\fill[orange] (%.2f,%.2f) circle (0.24); \fill[mist] (%.2f,%.2f) circle (0.09);" % (x, y, x, y))
    f.add(r"\node[anchor=north east,text=slate,font=\fontsize{11}{14}\selectfont,inner sep=0pt] at (%.2f,%.2f) {%s};" % (W - 2.0, H - 1.5, R("هندسة مدنية  •  تعلّم الآلة  •  بيانات مفتوحة  •  حالات عربية")))
    titles(f, "navy", "orange", "white", y0=10.6)
    f.add(r"\path[use as bounding box] (0,0) rectangle (%.1f,%.1f);" % (W, H)); f.build(dpi=200)
if __name__ == "__main__": cover_dark(); cover_light()
