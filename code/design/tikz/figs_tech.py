# -*- coding: utf-8 -*-
from tk import *
from blueprint_data import CH
ST = "draw=grey,line width=1pt,dash pattern=on 3pt off 2.5pt"
# ---------------- chapter blueprints ----------------
def blueprint(k, d):
    f = Fig("fig%d_0_blueprint" % k); W, g = 3.95, 0.6; HB = 0.68
    cols = [("المشكلة المحفّزة", [d["problem"]], "navy"), ("المفاهيم والأدوات", d["concepts"], "blue"), ("الأمثلة المحلولة", d["examples"], "orange"), ("ما تخرج به", d["skills"], "green")]
    xs = [-(i)*(W+g) for i in range(4)]
    fit = []
    for i, ((head, items, c), x) in enumerate(zip(cols, xs)):
        f.add(r"\coordinate (tl%d) at (%.3f,0); \coordinate (tr%d) at (%.3f,0);" % (i, x - W/2, i, x + W/2))
        if i == 0: continue
        for j, t in enumerate(items):
            pos = "at (%.3f,%.3f)" % (x + W/2 - 0.55, -HB - 0.3) if j == 0 else "at ($(b%d_%d.south east)+(0,-0.13)$)" % (i, j-1)
            f.add(r"\node[anchor=north east,text width=%.2fcm,align=right,inner sep=0pt,font=\footnotesize,text=ink] (b%d_%d) %s {%s};" % (W - 0.85, i, j, pos, R(t)))
            f.add(r"\fill[%s] ($(b%d_%d.north east)+(0.13,-0.21)$) rectangle ++(0.1,0.1);" % (c, i, j))
            fit.append("(b%d_%d)" % (i, j))
    f.add(r"\node[fit=%s,inner sep=0pt] (allb) {}; \path (allb.south) ++(0,-0.3) coordinate (bot);" % ("(0,-2.4)" + "".join(fit)))
    f.add(r"\node[text=ink,font=\small\bfseries,align=center,text width=%.2fcm,inner sep=0pt] at ($(tl0)!0.5!(tr0 |- bot)+(0,-%.2f)$) {%s};" % (W - 0.6, HB/2, R(d["problem"])))
    f.add(r"\begin{scope}[on background layer]")
    for i, (head, items, c) in enumerate(cols):
        f.add(r"\path[fill=white,sh,rounded corners=4pt] (tl%d) rectangle (tr%d |- bot);" % (i, i))
        f.add(r"\begin{scope}\clip[rounded corners=4pt] (tl%d) rectangle (tr%d |- bot); \fill[%s] (tl%d) rectangle ($(tr%d)+(0,-%.2f)$);\end{scope}" % (i, i, c, i, i, HB))
        f.add(r"\draw[%s,line width=0.8pt,rounded corners=4pt] (tl%d) rectangle (tr%d |- bot);" % (c, i, i))
    f.add(r"\end{scope}")
    for i, (head, items, c) in enumerate(cols):
        f.add(r"\node[text=white,font=\bfseries\small,inner sep=0pt] at (%.3f,%.3f) {%s};" % (xs[i] - 0.25, -HB/2, R(head)))
        f.add(r"\node[circle,fill=white,text=%s,font=\bfseries\footnotesize,inner sep=0pt,minimum size=0.42cm] at (%.3f,%.3f) {\lt %d};" % (c, xs[i] + W/2 - 0.38, -HB/2, i+1))
        if i < 3: f.add(r"\draw[conn] ($(tl%d)!0.5!(tl%d |- bot)$) -- ++(-%.2f,0);" % (i, i, g))
    f.add(r"\node[anchor=north east,font=\footnotesize,text=slate,inner sep=0pt] at ($(tr0 |- bot)+(0,-0.22)$) {%s};" % R("يعتمد على: " + d["needs"]))
    f.add(r"\node[anchor=north west,font=\footnotesize,text=slate,inner sep=0pt] at ($(tl3 |- bot)+(0,-0.22)$) {%s};" % R("يقود إلى: " + d["leads"]))
    return f.build()
# ---------------- Fig 5.5: k-fold vs grouped k-fold ----------------
def kfold():
    f = Fig("fig5_5_kfold"); c = 0.33; perm = [1, 4, 1, 0, 3, 4, 0, 2, 2, 2, 0, 3, 1, 1, 4, 4, 3, 2, 0, 3]
    panels = [(0, "تقسيم بالصفوف: المكعبات تُوزَّع منفردة", perm, "red", "مكعبات الخلطة الواحدة في التدريب والاختبار معاً: تسرّب"),
              (8.6, "تقسيم حسب الخلطة: GroupKFold", [i // 4 for i in range(20)], "green", "كل خلطة تُختبر مرة واحدة بنموذج لم يرَ أيّ مكعب منها")]
    for x0, title, fold, nc, note in panels:
        f.text(x0 + 10*c, 0.75, title, "font=\\small\\bfseries,text=navy")
        for r in range(5):
            for j in range(20):
                col = "orange" if fold[j] == r else "blueT"
                f.add(r"\fill[%s] (%.3f,%.3f) rectangle ++(%.3f,%.3f);" % (col, x0 + j*c + 0.02, -r*0.5, c - 0.04, 0.38))
            f.add(r"\node[anchor=west,font=\scriptsize,text=slate,inner sep=1pt] at (%.3f,%.3f) {%s};" % (x0 + 20*c + 0.05, -r*0.5 + 0.19, R("الطيّة %d" % (r+1))))
        for gk in range(5):
            f.add(r"\draw[navy,line width=1.2pt] (%.3f,-2.28) -- (%.3f,-2.28);" % (x0 + gk*4*c + 0.04, x0 + (gk*4+4)*c - 0.04))
            f.add(r"\node[font=\scriptsize,text=navy,inner sep=1pt] at (%.3f,-2.52) {%s};" % (x0 + (gk*4+2)*c, R("خلطة %d" % (gk+1))))
        f.text(x0 + 10*c, -3.05, note, "font=\\footnotesize,text=%s" % nc)
    f.add(r"\fill[orange] (5.0,-3.85) rectangle ++(0.3,0.3); \node[anchor=west,font=\footnotesize,text=ink] at (5.35,-3.7) {%s};" % R("مكعب اختبار"))
    f.add(r"\fill[blueT] (8.6,-3.85) rectangle ++(0.3,0.3); \node[anchor=west,font=\footnotesize,text=ink] at (8.95,-3.7) {%s};" % R("مكعب تدريب"))
    f.build()
# ---------------- Fig 4.4: confusion matrix ----------------
def confusion():
    f = Fig("fig4_4_confusion"); s = 2.5
    cells = [(0, 0, "TP", "شق مكتشف", "green"), (-s, 0, "FN", "شق فائت", "red"), (0, -s*0.72, "FP", "إنذار كاذب", "orange"), (-s, -s*0.72, "TN", "سليم صحيح", "grey")]
    for x, y, a, t, c in cells:
        f.add(r"\node[rounded corners=3pt,fill=%sT,draw=%s,line width=0.8pt,minimum width=%.2fcm,minimum height=%.2fcm,align=center] at (%.2f,%.2f) {{\lt\bfseries\large\textcolor{%s}{%s}}\\[2pt]%s};" % (c, c, s - 0.12, s*0.72 - 0.12, x, y, c, a, R(t)))
    f.text(0, 1.3, "النموذج يقول:\nشق", "font=\\footnotesize\\bfseries,text=navy,align=center"); f.text(-s, 1.3, "النموذج يقول:\nلا شق", "font=\\footnotesize\\bfseries,text=navy,align=center")
    f.text(1.95, 0, "الحقيقة:\nمشقوق", "font=\\footnotesize\\bfseries,text=navy,align=center"); f.text(1.95, -s*0.72, "الحقيقة:\nسليم", "font=\\footnotesize\\bfseries,text=navy,align=center")
    D = [("الاستدعاء", r"\dfrac{TP}{TP+FN}", "من الشقوق الحقيقية، كم اكتشفنا؟", "green"), ("الضبط", r"\dfrac{TP}{TP+FP}", "من الإنذارات، كم كان صحيحاً؟", "blue"), ("الدقة", r"\dfrac{TP+TN}{N}", "مضلِّلة حين تكون الشقوق نادرة", "red")]
    for i, (n, eq, note, c) in enumerate(D):
        y = 0.75 - i*1.55; x = -s - 4.9
        f.add(r"\node[rounded corners=3pt,fill=white,draw=%s,line width=0.8pt,sh,minimum width=5.3cm,minimum height=1.3cm] at (%.2f,%.2f) {};" % (c, x, y))
        f.add(r"\node[anchor=east,font=\small\bfseries,text=%s] at (%.2f,%.2f) {%s};" % (c, x + 2.5, y + 0.25, R(n)))
        f.add(r"\node[anchor=west,font=\footnotesize] at (%.2f,%.2f) {\lt$= %s$};" % (x - 2.5, y + 0.2, eq.replace("TP", r"\mathrm{TP}").replace("FN", r"\mathrm{FN}").replace("FP", r"\mathrm{FP}").replace("TN", r"\mathrm{TN}")))
        f.add(r"\node[anchor=east,font=\scriptsize,text=slate] at (%.2f,%.2f) {%s};" % (x + 2.5, y - 0.33, R(note)))
    f.build()
# ---------------- Fig 6.5: CNN ----------------
def cnn():
    f = Fig("fig6_5_cnn")
    B = [("الصورة", "1×64×64", 3.0, 0.25, "grey"), ("التفاف 3×3", "16×64×64", 3.0, 0.5, "blue"), ("تجميع أقصى", "16×32×32", 2.0, 0.5, "gold"), ("التفاف 3×3", "32×32×32", 2.0, 0.8, "blue"),
         ("تجميع أقصى", "32×16×16", 1.3, 0.8, "gold"), ("التفاف 3×3", "64×16×16", 1.3, 1.2, "blue"), ("تجميع أقصى شامل", "64", 0.45, 1.2, "gold"), ("طبقة خطية", "فئتان", 0.45, 0.45, "green")]
    x = 0; prev = None
    for i, (t, sz, h, w, c) in enumerate(B):
        x -= w/2
        f.add(r"\node[fill=%sT,draw=%s,line width=0.8pt,rounded corners=1.5pt,minimum width=%.2fcm,minimum height=%.2fcm,sh] (n%d) at (%.3f,0) {};" % (c, c, w, h, i, x))
        f.add(r"\node[font=\scriptsize\bfseries,text=%s,align=center,inner sep=1pt] at (%.3f,%.3f) {%s};" % ("ink", x, 1.95 if i % 2 == 0 else 2.45, R(t)))
        f.add(r"\draw[draw=line,line width=0.5pt] (%.3f,%.3f) -- (n%d.north);" % (x, 1.78 if i % 2 == 0 else 2.28, i))
        f.add(r"\node[font=\scriptsize,text=slate,inner sep=1pt] at (%.3f,%.3f) {%s};" % (x, -h/2 - 0.3, R(sz)))
        if prev is not None: f.add(r"\draw[conn,line width=0.8pt] (n%d.west) -- (n%d.east);" % (prev, i))
        prev = i; x -= w/2 + (1.25 if i == 0 else 0.8)
    f.text(x/2 + 0.4, -2.45, "الحجم المكاني ينتصف عند كل تجميع وعدد القنوات يتضاعف • مجموع الأوزان 23,650", "font=\\footnotesize,text=navy")
    f.add(r"\node[font=\scriptsize,text=slate] at (%.3f,-1.3) {%s};" % (0.35, ""))
    f.build()
# ---------------- Fig 12.5: U-Net ----------------
def unet():
    f = Fig("fig12_2_unet")
    E = [("e1", 0, 0, "16 قناة", "64×64", "blue"), ("e2", -2.6, -1.7, "32 قناة", "32×32", "blue"), ("e3", -5.6, -3.4, "64 قناة", "16×16", "navy"), ("d2", -8.6, -1.7, "32 قناة", "32×32", "green"), ("d1", -11.2, 0, "16 قناة", "64×64", "green")]
    f.add(r"\node[fill=greyT,draw=grey,line width=0.8pt,rounded corners=3pt,minimum width=1.5cm,minimum height=1.15cm,align=center,font=\footnotesize,sh] (in) at (2.6,0) {%s};" % RL("الصورة\n64×64"))
    for id, x, y, a, b, c in E:
        f.add(r"\node[fill=%sT,draw=%s,line width=0.8pt,rounded corners=3pt,minimum width=2.0cm,minimum height=1.15cm,align=center,font=\footnotesize,sh] (%s) at (%.2f,%.2f) {%s\\%s};" % (c, c, id, x, y, R(a, True), R(b)))
    f.add(r"\node[fill=goldT,draw=gold,line width=0.8pt,rounded corners=3pt,minimum width=1.5cm,minimum height=1.15cm,align=center,font=\footnotesize,sh] (out) at (-13.8,0) {%s};" % RL("قناع\nالشق"))
    f.add(r"\draw[conn] (in.west)--(e1.east); \draw[conn] (e1.south) |- node[lab,pos=0.25,right] {%s} (e2.east); \draw[conn] (e2.south) |- node[lab,pos=0.25,right] {%s} (e3.east);" % (R("تجميع"), R("تجميع")))
    f.add(r"\draw[connc=green] (e3.west) -| node[lab,pos=0.75,left] {%s} (d2.south); \draw[connc=green] (d2.west) -| node[lab,pos=0.75,left] {%s} (d1.south); \draw[connc=green] (d1.west)--(out.east);" % (R("تكبير"), R("تكبير")))
    f.add(r"\draw[fb] (e1.west) -- node[lab,above,text=red] {%s} (d1.east); \draw[fb] (e2.west) -- node[lab,above,text=red] {%s} (d2.east);" % (R("وصلة تخطٍّ: تنقل التفاصيل الدقيقة (الشقوق الرفيعة)"), R("وصلة تخطٍّ")))
    f.text(-1.6, -4.5, "المسار الهابط: ما الذي في الصورة؟", "font=\\footnotesize\\bfseries,text=blue"); f.text(-9.6, -4.5, "المسار الصاعد: أين هو بالضبط؟", "font=\\footnotesize\\bfseries,text=green")
    f.build()
# ---------------- Fig 10.5: infinite slope ----------------
def slope():
    f = Fig("fig10_3_slopesketch"); be = 28; t = math.tan(math.radians(be)); L = 10; z = 2.2; mz = 1.3
    f.add(r"\fill[greyT] (0,-0.7) -- (%.2f,%.3f) -- (%.2f,%.3f) -- (0,0) -- cycle;" % (L, L*t - 0.7, L, L*t))
    f.add(r"\fill[goldT] (0,0) -- (%.2f,%.3f) -- (%.2f,%.3f) -- (0,%.2f) -- cycle;" % (L, L*t, L, L*t + z, z))
    f.add(r"\fill[blueT] (0,0) -- (%.2f,%.3f) -- (%.2f,%.3f) -- (0,%.2f) -- cycle;" % (L, L*t, L, L*t + mz, mz))
    f.add(r"\draw[ink,line width=1.2pt] (0,0) -- (%.2f,%.3f); \draw[ink,line width=0.9pt] (0,%.2f) -- (%.2f,%.3f); \draw[blue,line width=0.9pt,dash pattern=on 4pt off 2pt] (0,%.2f) -- (%.2f,%.3f);" % (L, L*t, z, L, L*t + z, mz, L, L*t + mz))
    x1, x2 = 3.9, 5.6
    f.add(r"\draw[red,line width=1.1pt] (%.2f,%.3f) -- (%.2f,%.3f) -- (%.2f,%.3f) -- (%.2f,%.3f) -- cycle;" % (x1, x1*t, x2, x2*t, x2, x2*t + z, x1, x1*t + z))
    cx = (x1 + x2)/2; cy = cx*t + z/2 + 0.2
    f.add(r"\draw[red,line width=1.2pt,-{Stealth[length=6pt]}] (%.2f,%.2f) -- ++(0,-1.35) node[right,font=\small] {\lt$W$};" % (cx, cy))
    f.add(r"\draw[ink,line width=0.7pt,{Stealth[length=4pt]}-{Stealth[length=4pt]}] (%.2f,%.3f) -- node[right,font=\small] {\lt$z$} (%.2f,%.3f);" % (x2 + 1.0, (x2+1.0)*t, x2 + 1.0, (x2+1.0)*t + z))
    f.add(r"\draw[blue,line width=0.7pt,{Stealth[length=4pt]}-{Stealth[length=4pt]}] (%.2f,%.3f) -- node[right,font=\small,text=blue] {\lt$m\,z$} (%.2f,%.3f);" % (x2 + 2.1, (x2+2.1)*t, x2 + 2.1, (x2+2.1)*t + mz))
    f.add(r"\draw[slate,line width=0.6pt] (0,0) -- (2.6,0); \draw[slate,line width=0.6pt] (1.9,0) arc (0:%d:1.9); \node[font=\small] at (2.25,0.5) {\lt$\beta$};" % be)
    f.add(r"\node[font=\footnotesize,text=ink,rotate=%d] at (%.2f,%.2f) {%s};" % (be, 2.2, 2.2*t + z + 0.28, R("سطح الأرض")))
    f.add(r"\node[font=\footnotesize,text=blue,rotate=%d] at (%.2f,%.2f) {%s};" % (be, 8.6, 8.6*t + mz + 0.25, R("منسوب الماء")))
    f.add(r"\node[font=\footnotesize,text=ink,rotate=%d] at (%.2f,%.2f) {%s};" % (be, 7.6, 7.6*t - 0.32, R("سطح الانزلاق (صخر)")))
    f.add(r"\node[font=\footnotesize,text=red,align=center] at (%.2f,%.2f) {%s};" % (cx - 2.1, cx*t + z + 1.0, RL("شريحة\nالتحليل")))
    f.add(r"\draw[red,line width=0.6pt,-{Stealth[length=4pt]}] (%.2f,%.2f) -- (%.2f,%.2f);" % (cx - 1.6, cx*t + z + 0.75, x1 + 0.1, x1*t + z + 0.15))
    f.build()
# ---------------- Fig 14.5: intersection and Webster plan ----------------
def signal():
    f = Fig("fig14_2_signalplan")
    f.add(r"\fill[fill=line] (-2.6,-0.55) rectangle (2.6,0.55); \fill[fill=line] (-0.55,-2.6) rectangle (0.55,2.6);")
    f.add(r"\draw[white,line width=1pt,dash pattern=on 5pt off 4pt] (-2.6,0)--(-0.55,0) (0.55,0)--(2.6,0) (0,-2.6)--(0,-0.55) (0,0.55)--(0,2.6);")
    f.add(r"\draw[blue,line width=2pt,-{Stealth[length=7pt]}] (-2.5,-0.27) -- (-0.7,-0.27); \draw[orange,line width=2pt,-{Stealth[length=7pt]}] (0.27,-2.5) -- (0.27,-0.7);")
    f.text(-1.75, -1.25, "المدخل 1\n600 مركبة/ساعة", "font=\\scriptsize\\bfseries,text=blue,align=center"); f.text(1.75, -1.7, "المدخل 2\n400 مركبة/ساعة", "font=\\scriptsize\\bfseries,text=orange,align=center")
    x0, sc = 4.0, 0.24
    rows = [(0.75, "الطور 1", [(0, 18, "green"), (18, 4, "gold"), (22, 16, "red")]), (-0.75, "الطور 2", [(0, 22, "red"), (22, 12, "green"), (34, 4, "gold")])]
    for y, lab, segs in rows:
        for s0, dlen, c in segs:
            f.add(r"\fill[%s,rounded corners=1.5pt] (%.3f,%.2f) rectangle (%.3f,%.2f);" % (c, x0 + s0*sc + 0.03, y - 0.38, x0 + (s0+dlen)*sc - 0.03, y + 0.38))
            if dlen >= 12: f.add(r"\node[text=white,font=\scriptsize\bfseries] at (%.3f,%.2f) {\lt %d s};" % (x0 + (s0 + dlen/2)*sc, y, dlen))
        f.add(r"\node[anchor=west,font=\footnotesize\bfseries,text=navy] at (%.2f,%.2f) {%s};" % (x0 + 38*sc + 0.2, y, R(lab)))
    f.add(r"\draw[slate,line width=0.7pt,-{Stealth[length=5pt]}] (%.2f,-1.6) -- (%.2f,-1.6);" % (x0, x0 + 38*sc + 0.35))
    for tt in [0, 10, 18, 22, 34, 38]:
        f.add(r"\draw[slate,line width=0.6pt] (%.3f,-1.6) -- ++(0,-0.1) node[below,font=\scriptsize,text=slate,inner sep=2pt] {\lt %d};" % (x0 + tt*sc, tt))
    f.text(x0 + 19*sc, -2.45, "الزمن ضمن الدورة (ثانية): دورة وبستر 38 ثانية، وأربع ثوانٍ ضائعة عند كل تبديل", "font=\\scriptsize,text=slate")
    for i, (c, t) in enumerate([("green", "أخضر"), ("gold", "أصفر وإخلاء"), ("red", "أحمر")]):
        f.add(r"\fill[%s,rounded corners=1pt] (%.2f,1.75) rectangle ++(0.35,0.25); \node[anchor=west,font=\scriptsize] at (%.2f,1.87) {%s};" % (c, x0 + 0.2 + i*3.0, x0 + 0.6 + i*3.0, R(t)))
    f.build()
# ---------------- Fig 8.6: accelerated corrosion set-up ----------------
def setup():
    f = Fig("fig8_6_setup")
    f.add(r"\fill[blueT] (-5,0) rectangle (5,2.9); \draw[blue,line width=1pt] (-5,3.3) -- (-5,0) -- (5,0) -- (5,3.3); \draw[blue,line width=0.6pt,dash pattern=on 3pt off 2pt] (-5,2.9)--(5,2.9);")
    f.add(r"\fill[fill=line] (-3.3,1.2) rectangle (3.3,3.6); \draw[slate,line width=1pt] (-3.3,1.2) rectangle (3.3,3.6);")
    f.add(r"\draw[orange,line width=4.5pt,line cap=butt] (-3.0,1.85) -- (3.0,1.85);")
    f.add(r"\fill[slate] (-4.0,0.55) rectangle (4.0,0.75);")
    f.add(r"\node[fill=goldT,draw=gold,line width=0.9pt,rounded corners=3pt,minimum width=3.2cm,minimum height=1.1cm,align=center,font=\footnotesize,sh] (ps) at (0,5.3) {%s};" % RL("مصدر تيار مستمر\n(تيار ثابت)"))
    f.add(r"\draw[red,line width=1.1pt,rounded corners=4pt] (ps.west) -- (-2.6,5.3) -- (-2.6,1.95); \node[circle,fill=red,text=white,font=\bfseries\footnotesize,inner sep=1.5pt] at (-2.6,4.4) {\lt +};")
    f.add(r"\draw[ink,line width=1.1pt,rounded corners=4pt] (ps.east) -- (4.4,5.3) -- (4.4,0.65) -- (4.0,0.65); \node[circle,fill=ink,text=white,font=\bfseries\footnotesize,inner sep=1.5pt] at (4.4,4.4) {\lt$-$};")
    f.text(0, 3.15, "عينة خرسانة مسلحة", "font=\\footnotesize\\bfseries,text=ink"); f.text(0, 2.3, "قضيب التسليح = المصعد (+)", "font=\\footnotesize,text=orange")
    f.text(0, 0.28, "صفيحة فولاذية = المهبط (−)", "font=\\footnotesize,text=slate"); f.text(-4.15, 2.45, "محلول\nNaCl 2%", "font=\\scriptsize,text=blue,align=center")
    f.add(r"\node[font=\footnotesize,text=navy] at (0,-0.75) {%s \quad {\lt$m = \dfrac{M\,I\,t}{z\,F}$}};" % R("قانون فاراداي لفقدان الكتلة:"))
    f.build()
if __name__ == "__main__":
    import sys
    which = sys.argv[1:] or ["bp", "kfold", "confusion", "cnn", "unet", "slope", "signal", "setup"]
    if "bp" in which:
        for k, d in CH.items(): blueprint(k, d)
    for n, fn in [("kfold", kfold), ("confusion", confusion), ("cnn", cnn), ("unet", unet), ("slope", slope), ("signal", signal), ("setup", setup)]:
        if n in which: fn()
