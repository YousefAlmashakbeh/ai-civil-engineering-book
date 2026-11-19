# -*- coding: utf-8 -*-
from tk import *
# ---------------- Fig 1.2: workflow as a real flowchart ----------------
def workflow():
    f = Fig("fig1_3_workflow"); W, H, px, py = 3.05, 1.75, 3.65, 2.95
    xs = [3*px, 2*px, px, 0]
    S = [("السؤال الهندسي", "ما القرار الذي\nسيتغيّر؟", "navy"), ("البيانات", "مختبر، موقع،\nمصادر مفتوحة", "blue"),
         ("التنظيف والفحص", "وحدات، حدود\nفيزيائية، تكرار", "blue"), ("الخصائص", "من المعرفة\nالهندسية", "blue"),
         ("خط الأساس", "معادلة كود التصميم\nأو الفيزياء", "orange"), ("النموذج", "تقسيم صادق\nوتحقق متقاطع", "blue"),
         ("اللايقين والحدود", "فترات، معايرة،\nخارج النطاق", "blue")]
    for i in range(4): f.card("s%d" % (i+1), xs[i], 0, W, H, S[i][0], S[i][1], S[i][2], num=i+1)
    for i in range(3): f.card("s%d" % (i+5), xs[3-i], -py, W, H, S[i+4][0], S[i+4][1], S[i+4][2], num=i+5)
    f.add(r"\node[dec=red,minimum width=3.05cm,minimum height=1.75cm] (d) at (%.3f,%.3f) {%s};" % (xs[0], -py, RL("هل نجحت\nكل الفحوص؟", True)))
    f.card("s8", xs[0], -2*py + 0.25, W, 1.45, "قرار المهندس", "يراجع ويوقّع", "green", num=8)
    for a, b in [(1, 2), (2, 3), (3, 4)]: f.add(r"\draw[conn] (s%d.west) -- (s%d.east);" % (a, b))
    f.add(r"\draw[conn] (s4.south) -- (s5.north);")
    for a, b in [(5, 6), (6, 7)]: f.add(r"\draw[conn] (s%d.east) -- (s%d.west);" % (a, b))
    f.add(r"\draw[conn] (s7.east) -- (d.west);")
    f.add(r"\draw[connc=green] (d.south) -- node[lab,right,text=green,font=\bfseries\footnotesize] {%s} (s8.north);" % R("نعم"))
    f.add(r"\draw[fb] (d.north) -- ++(0,0.42) -| node[lab,pos=0.25,above,text=red,font=\bfseries\footnotesize] {%s} (s2.south);" % R("لا"))
    f.text((xs[1]+xs[3])/2 - 0.2, -py/2 - 0.05, "تسرّب بيانات، خروج عن النطاق، أخطاء غير آمنة:\nعُد إلى البيانات وأعد الدورة", "lab,text=red,align=center,fill=white,inner sep=3pt")
    f.build()
# ---------------- snake pipelines (13.6, 17.2) ----------------
def pipeline13():
    f = Fig("fig13_6_pipeline"); W, H, px, py = 3.5, 1.75, 4.25, 2.75; xs = [2*px, px, 0]
    S = [("القياس", "تسارع، انفعال،\nحرارة، UPV", "navy"), ("الخصائص", "ترددات، طاقة،\nسرعة موجة", "blue"), ("إزالة أثر البيئة", "نموذج حرارة\nورطوبة وحمل", "orange"),
         ("المقارنة", "بالحالة المرجعية\n(سنة أساس)", "blue"), ("قاعدة الإنذار", "عتبة معروفة ومعدّل\nإنذار كاذب محسوب", "blue"), ("قرار المهندس", "فحص، تقييد،\nصيانة", "green")]
    for i in range(3): f.card("s%d" % (i+1), xs[i], 0, W, H, *S[i], num=i+1)
    for i in range(3): f.card("s%d" % (i+4), xs[2-i], -py, W, H, *S[i+3], num=i+4)
    f.add(r"\draw[conn] (s1.west)--(s2.east); \draw[conn] (s2.west)--(s3.east); \draw[conn] (s3.south)--(s4.north); \draw[conn] (s4.east)--(s5.west); \draw[conn] (s5.east)--(s6.west);")
    f.add(r"\node[draw=red,dash pattern=on 3pt off 2pt,line width=0.8pt,rounded corners=3pt,fill=redT,text=red,font=\footnotesize,align=center,inner sep=5pt] (n) at (%.3f,%.3f) {%s};" % (-3.75, -py/2, RL("هنا تولد معظم\nالإنذارات الكاذبة،\nوهنا يضيع معظم\nالضرر الخفي")))
    f.add(r"\draw[red,line width=0.8pt,-{Stealth[length=5pt]}] (n.north) |- (s3.west);")
    f.build()
def pipeline17():
    f = Fig("fig17_2_pipeline"); W, H, px, py = 3.5, 1.75, 4.6, 2.85; xs = [2*px, px, 0]
    S = [("سؤال المهندس", "بلغته وبمصطلحات\nالموقع", "navy"), ("التطبيع", "همزات، تاء مربوطة،\nتشكيل", "blue"), ("الاسترجاع", "أفضل ثلاثة مقاطع\nمن المواصفات", "blue"),
         ("المسودة", "النموذج اللغوي\nمع أرقام البنود", "orange")]
    for i in range(3): f.card("s%d" % (i+1), xs[i], 0, W, H, *S[i], num=i+1)
    f.card("s4", xs[2], -py, W, H, *S[3], num=4)
    f.add(r"\node[dec=red,minimum width=3.5cm,minimum height=1.9cm] (d) at (%.3f,%.3f) {%s};" % (xs[1], -py, RL("حارس الأرقام:\nكل رقم في المصدر؟", True)))
    f.card("s6", xs[0], -py, W, H, "المراجعة", "المهندس يراجع\nويوقّع", "green", num=6)
    f.add(r"\node[circle,fill=red,text=white,font=\bfseries\footnotesize,inner sep=0pt,minimum size=0.42cm] at ($(d.north)+(0,0.02)$) {\lt 5};")
    f.add(r"\node[rounded corners=4pt,draw=red,line width=0.8pt,fill=redT,text=red,font=\footnotesize,align=center,minimum width=3.5cm,minimum height=1.05cm,sh] (rej) at (%.3f,%.3f) {%s};" % (xs[1], -py - 2.45, RL("يُرفض الجواب\nويُحال السؤال إلى المهندس")))
    f.add(r"\draw[conn] (s1.west)--(s2.east); \draw[conn] (s2.west)--(s3.east); \draw[conn] (s3.south)--(s4.north); \draw[conn] (s4.east)--(d.west);")
    f.add(r"\draw[connc=green] (d.east) -- node[lab,above=2pt,text=green,font=\bfseries\footnotesize] {%s} (s6.west);" % R("نعم"))
    f.add(r"\draw[fb] (d.south) -- node[lab,left=2pt,text=red,font=\bfseries\footnotesize] {%s} (rej.north);" % R("لا"))
    f.build()
# ---------------- Fig 16.2: model / shadow / twin ----------------
def twin():
    f = Fig("fig16_2_twinlevels"); PW, PH, gap = 5.3, 4.3, 0.4
    L = [("النموذج الرقمي", "لا تبادل آلي للبيانات", "grey", False, False), ("الظل الرقمي", "البيانات تصل إلى النموذج آلياً", "blue", True, False), ("التوأم الرقمي", "التبادل آلي في الاتجاهين", "green", True, True)]
    for i, (t, sub, c, up, dn) in enumerate(L):
        x = -(i)*(PW+gap)
        f.add(r"\node[rounded corners=6pt,fill=%sT,draw=%s,line width=0.9pt,minimum width=%.2fcm,minimum height=%.2fcm] (p%d) at (%.3f,0) {};" % (c, c, PW, PH, i, x))
        f.add(r"\node[pill=%s,font=\bfseries\small] at (%.3f,%.3f) {%s};" % (c, x, PH/2 - 0.5, R(t)))
        f.text(x, PH/2 - 1.1, sub, "text=slate,font=\\footnotesize")
        f.card("a%d" % i, x + 1.6, -0.25, 1.7, 1.35, "المنشأة", "حساسات", "navy", hb=0.55, shadow=True)
        f.card("b%d" % i, x - 1.6, -0.25, 1.7, 1.35, "النموذج", "صلابة، حالة", c if c != "grey" else "slate", hb=0.55, shadow=True)
        su = "connc=%s" % c if up else "draw=grey,line width=1pt,dash pattern=on 3pt off 2.5pt,-{Stealth[length=6pt]}"
        sd = "connc=%s" % c if dn else "draw=grey,line width=1pt,dash pattern=on 3pt off 2.5pt,-{Stealth[length=6pt]}"
        f.add(r"\draw[%s] ($(a%d.west)+(0,0.3)$) -- node[lab,above=1pt] {%s} ($(b%d.east)+(0,0.3)$);" % (su, i, R("بيانات"), i))
        f.add(r"\draw[%s] ($(b%d.east)+(0,-0.3)$) -- node[lab,below=1pt] {%s} ($(a%d.west)+(0,-0.3)$);" % (sd, i, R("قرار"), i))
        f.text(x, -PH/2 + 0.45, "البيانات: %s  •  القرار: %s" % ("آلي" if up else "يدوي", "آلي" if dn else "يدوي"), "text=navy,font=\\footnotesize\\bfseries")
    f.add(r"\draw[grey,line width=1pt,-{Stealth[length=6pt]}] (%.2f,%.2f) -- node[lab,below] {%s} (%.2f,%.2f);" % (PW/2, -PH/2 - 0.45, R("درجة التكامل بين المنشأة ونموذجها تزداد"), -2*(PW+gap) - PW/2, -PH/2 - 0.45))
    f.build()
# ---------------- roadmap ----------------
def roadmap():
    f = Fig("figT1_roadmap"); CW, CH_, g = 2.75, 1.25, 0.3
    P = [("الباب الأول: الأسس", "navy", [(1, "المدخل والسياق"), (2, "الأدوات الرياضية"), (3, "بايثون للمهندس"), (4, "البيانات الهندسية")]),
         ("الباب الثاني: الأدوات", "blue", [(5, "تعلّم الآلة الكلاسيكي"), (6, "الشبكات العصبية"), (7, "التحسين الذكي")]),
         ("الباب الثالث: التصميم والمواد والتشييد", "orange", [(8, "مواد البناء"), (9, "التحليل الإنشائي"), (10, "الجيوتقنية"), (11, "إدارة التشييد")]),
         ("الباب الرابع: البنية التحتية", "green", [(12, "الفحص البصري"), (13, "مراقبة المنشآت"), (14, "النقل والمرور"), (15, "المياه والبيئة")]),
         ("الباب الخامس: آفاق متقدمة", "gold", [(16, "الفيزياء والتوأم الرقمي"), (17, "النماذج اللغوية"), (18, "الموثوقية والبحث")])]
    TW = 4*CW + 3*g + 0.8
    def band(pid, cx, cy, w, h, title, col):
        f.add(r"\node[rounded corners=7pt,fill=%sT,draw=%s!55,line width=0.7pt,minimum width=%.2fcm,minimum height=%.2fcm] (%s) at (%.3f,%.3f) {};" % (col, col, w, h, pid, cx, cy))
        f.add(r"\node[pill=%s,anchor=north east] at ($(%s.north east)+(-0.3,0.28)$) {%s};" % (col, pid, R(title)))
    def chap(cx, cy, k, t, col, w=CW):
        f.add(r"\node[rounded corners=4pt,fill=white,draw=%s,line width=0.8pt,minimum width=%.2fcm,minimum height=%.2fcm,sh] (c%d) at (%.3f,%.3f) {};" % (col, w, CH_, k, cx, cy))
        f.add(r"\node[circle,fill=%s,text=white,font=\bfseries\small,inner sep=0pt,minimum size=0.6cm] at (%.3f,%.3f) {\lt %d};" % (col, cx + w/2 - 0.48, cy, k))
        f.add(r"\node[text=ink,font=\small\bfseries,align=center,text width=%.2fcm,inner sep=0pt] at (%.3f,%.3f) {%s};" % (w - 1.05, cx - 0.33, cy, R(t)))
    def row(chs, cy, col, x_right, w=CW):
        for i, (k, t) in enumerate(chs):
            cx = x_right - w/2 - i*(w+g); chap(cx, cy, k, t, col, w)
            if i: f.add(r"\draw[connc=%s,line width=0.9pt] (c%d.west) -- (c%d.east);" % (col, chs[i-1][0], k))
    y1 = 0; band("P1", 0, y1, TW, 2.0, P[0][0], "navy"); row(P[0][2], y1 - 0.1, "navy", TW/2 - 0.4)
    y2 = -2.85; band("P2", 0, y2, TW, 2.0, P[1][0], "blue"); row(P[1][2], y2 - 0.1, "blue", (3*3.5 + 2*g)/2, 3.5)
    hw = (TW - 0.5)/2; y3 = -7.2; w2 = (hw - 0.8 - g)/2
    for pid, cx, (title, col, chs) in [("P3", TW/2 - hw/2, P[2]), ("P4", -TW/2 + hw/2, P[3])]:
        band(pid, cx, y3, hw, 3.9, title, col)
        row(chs[:2], y3 + 0.72, col, cx + hw/2 - 0.4, w2); row(chs[2:], y3 - 1.05, col, cx + hw/2 - 0.4, w2)
        f.add(r"\draw[connc=%s,line width=0.9pt] (c%d.south) -- ++(0,-0.25) -| (c%d.north);" % (col, chs[1][0], chs[2][0]))
    y5 = -11.3; band("P5", 0, y5, TW, 2.0, P[4][0], "gold"); row(P[4][2], y5 - 0.1, "gold", (3*3.5 + 2*g)/2, 3.5)
    f.add(r"\draw[conn,line width=1.3pt] (P1.south) -- (P2.north);")
    f.add(r"\draw[conn,line width=1.3pt] (0.75,0 |- P2.south) -- (0.75,0 |- P3.north);")
    f.add(r"\draw[conn,line width=1.3pt] (-5.85,0 |- P2.south) -- (-5.85,0 |- P4.north);")
    f.add(r"\draw[conn,line width=1.3pt] (P3.south) -- ++(0,-0.4) -| ($(P5.north)+(1.2,0)$);")
    f.add(r"\draw[conn,line width=1.3pt] (P4.south) -- ++(0,-0.4) -| ($(P5.north)+(-1.2,0)$);")
    f.text(-2.55, y3 + 2.72, "بابان مستقلان: يُدرَّس أيّ فصل\nمنهما بعد الباب الثاني", "lab,font=\\footnotesize\\bfseries,text=slate,align=center")
    f.text(0, y5 - 1.6, "في كل فصل: خريطة الفصل • أمثلة محلولة • حدود النموذج • مصطلحات واختبار ذاتي\nتسع حالات عربية محلولة في الفصول 7 و9 إلى 16", "text=navy,font=\\footnotesize,align=center")
    f.build()
if __name__ == "__main__":
    for fn in [workflow, pipeline13, pipeline17, twin, roadmap, decision]: fn()
# ---------------- Fig 1.2: should I use AI at all? (decision flowchart of Section 1.8) ----------------
def decision():
    # gaps between the diamonds leave room for the short downward "no" arrows; drawn near print width (12.6 cm)
    f = Fig("fig1_2_decision"); py = 3.0; DW, DH = 4.4, 1.6; xo = -6.05; OW = 4.7
    Q = [("هل توجد معادلة موثوقة\nورخيصة تحلّ المسألة؟", "استخدم المعادلة", "هي النموذج، ولا حاجة إلى غيرها", "red"),
         ("هل يفرض كود التصميم\nطريقة حساب محددة؟", "التزم بطريقة الكود", "النموذج للتحقق والفرز فقط", "red"),
         ("هل البيانات أقل من أن\nتمثّل المشكلة؟", "اجمع بيانات أو ابنِ محاكاة", "قبل أي نموذج", "red"),
         ("هل كلفة الخطأ كارثية\nولا قياس لثقة التنبؤ؟", "أضف مدى الثقة", "ومراجعة مهندس لكل قرار", "orange"),
         ("هل ظروف الاستخدام\nتختلف عن ظروف البيانات؟", "نموذج هجين", "واختبار صريح خارج المدى", "orange")]
    f.add(r"\node[term=navy] (st) at (0,%.2f) {%s};" % (2.15, R("مسألة هندسية جديدة")))
    for i, (q, t, b, c) in enumerate(Q):
        y = -i*py
        f.add(r"\node[dec=%s,minimum width=%.2fcm,minimum height=%.2fcm,font=\footnotesize] (q%d) at (0,%.2f) {%s};" % ("navy", DW, DH, i, y, RL(q, True)))
        f.add(r"\node[circle,fill=navy,text=white,font=\bfseries\footnotesize,inner sep=0pt,minimum size=0.44cm] at ($(q%d.east)+(0.42,0)$) {\lt %d};" % (i, i+1))
        f.card("o%d" % i, xo, y, OW, 1.45, t, b, c, hb=0.6)
        f.add(r"\draw[connc=%s] (q%d.west) -- node[lab,above=1pt,text=%s,font=\bfseries\footnotesize] {%s} (o%d.east);" % (c, i, c, R("نعم"), i))
        prev = "st" if i == 0 else "q%d" % (i-1)
        if i == 0: f.add(r"\draw[conn] (st.south) -- (q0.north);")
        else: f.add(r"\draw[conn] (q%d.south) -- node[lab,right=1pt,font=\bfseries\footnotesize] {%s} (q%d.north);" % (i-1, R("لا"), i))
    f.add(r"\node[term=green,minimum width=4.6cm] (en) at (0,%.2f) {%s};" % (-4*py - 2.55, RL("ابدأ بأبسط نموذج يحلّ المسألة\nوقارنه بخط أساس فيزيائي")))
    f.add(r"\draw[connc=green] (q4.south) -- node[lab,right=1pt,text=green,font=\bfseries\footnotesize] {%s} (en.north);" % R("لا"))
    f.add(r"\draw[decorate,decoration={brace,amplitude=5pt},slate,line width=0.7pt] (%.2f,%.2f) -- (%.2f,%.2f);" % (xo - OW/2 - 0.25, -2*py - 0.75, xo - OW/2 - 0.25, 0.75))
    f.add(r"\node[rotate=90,font=\footnotesize,text=slate] at (%.2f,%.2f) {%s};" % (xo - OW/2 - 0.75, -py, R("الغالب أنك لا تحتاج إلى الذكاء الاصطناعي")))
    f.add(r"\draw[decorate,decoration={brace,amplitude=5pt},slate,line width=0.7pt] (%.2f,%.2f) -- (%.2f,%.2f);" % (xo - OW/2 - 0.25, -4*py - 0.75, xo - OW/2 - 0.25, -3*py + 0.75))
    f.add(r"\node[rotate=90,font=\footnotesize,text=slate] at (%.2f,%.2f) {%s};" % (xo - OW/2 - 0.75, -3.5*py, R("استخدمه بضمانات")))
    f.build()
