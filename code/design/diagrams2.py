from bookstyle import *
F = "../../figures/"
# ---------- roadmap of the book (front matter) ----------
parts = [("الباب الأول: الأسس", NAVY, [(1, "المدخل والسياق"), (2, "الأدوات الرياضية"), (3, "بايثون للمهندس"), (4, "البيانات الهندسية")]),
         ("الباب الثاني: الأدوات", BLUE, [(5, "تعلّم الآلة الكلاسيكي"), (6, "الشبكات العصبية"), (7, "التحسين الذكي")]),
         ("الباب الثالث: التصميم والمواد والتشييد", ORANGE, [(8, "مواد البناء"), (9, "التحليل الإنشائي"), (10, "الجيوتقنية"), (11, "إدارة التشييد")]),
         ("الباب الرابع: البنية التحتية", GREEN, [(12, "الفحص البصري"), (13, "مراقبة المنشآت"), (14, "النقل والمرور"), (15, "المياه والبيئة")]),
         ("الباب الخامس: آفاق متقدمة", GOLD, [(16, "الفيزياء والتوأم الرقمي"), (17, "النماذج اللغوية"), (18, "الموثوقية والبحث")])]
fig, ax = canvas(12, 8.2)
ax.text(6, 7.95, "خريطة الكتاب: من الأسس إلى التطبيق", ha="center", fontsize=20, color=NAVY, fontweight="bold")
ax.text(6, 7.55, "كل باب يبني على ما قبله؛ والبابان الثالث والرابع مستقلان، فيمكن تدريس أيّ فصل منهما بعد الباب الثاني", ha="center", fontsize=11.5, color=GREY)
y = 6.3
for pi, (title, col, chs) in enumerate(parts):
    ax.add_patch(FancyBboxPatch((0.2, y-0.15), 11.6, 1.2, boxstyle="round,pad=0,rounding_size=0.15", fc=TINT[col], ec="none"))
    ax.text(11.65, y+0.45, title, ha="right", va="center", fontsize=13, color=col, fontweight="bold")
    n = len(chs); w = 1.85; gap = 0.22; x0 = 8.6
    for i, (k, t) in enumerate(chs):
        x = x0 - i*(w+gap) - w
        card(ax, x+ (0 if n == 4 else 0), y-0.05, w, 1.0, t, None, col, fs=11, num=k, shadow=True)
        if i: arrow(ax, (x+w+gap-0.02, y+0.45), (x+w+0.03, y+0.45), col, 1.4, head=10)
    if pi < 4: arrow(ax, (6.0, y-0.17), (6.0, y-0.33), GREY, 1.6, head=12)
    y -= 1.5
ax.text(6, -0.05, "تسع حالات عربية محلولة • خريطة فصل في أول كل فصل • مصطلحات واختبار ذاتي في آخره", ha="center", fontsize=11, color=NAVY)
save(fig, F + "figT1_roadmap.png")
# ---------- Fig 1.2: workflow ----------
steps = [("1", "السؤال الهندسي", "ما القرار الذي\nسيتغير؟", NAVY), ("2", "البيانات", "مختبر، موقع،\nمصادر مفتوحة", BLUE),
         ("3", "التنظيف والفحص", "وحدات، حدود\nفيزيائية، تكرار", BLUE), ("4", "الخصائص", "من المعرفة\nالهندسية", BLUE),
         ("5", "خط الأساس", "معادلة الكود\nأو الفيزياء", ORANGE), ("6", "النموذج", "تقسيم صادق\nوتحقق متقاطع", BLUE),
         ("7", "اللايقين والحدود", "فترات، معايرة،\nخارج النطاق", BLUE), ("8", "قرار المهندس", "يراجع ويوقّع", GREEN)]
fig, ax = canvas(12, 4.4)
w, h, gap = 2.55, 1.45, 0.4
xr = [12 - 0.25 - (j+1)*w - j*gap for j in range(4)]          # right-to-left slots
pos = [(xr[j], 2.6) for j in range(4)] + [(xr[3-j], 0.4) for j in range(4)]   # snake: bottom row runs back to the right
pos = [(xr[j], 2.6) for j in range(4)] + [(xr[::-1][j], 0.4) for j in range(4)]
for (n, t, b, c), (x, yy) in zip(steps, pos): card(ax, x, yy, w, h, t, b, c, fs=13, bfs=10.5, num=n)
for i in range(7):
    (x1, y1), (x2, y2) = pos[i], pos[i+1]
    if i == 3: arrow(ax, (x1+w/2, y1-0.03), (x2+w/2, y2+h+0.03), GREY, 2.0)
    elif i < 3: arrow(ax, (x1-0.02, y1+h/2), (x2+w+0.02, y2+h/2), GREY, 2.0)
    else: arrow(ax, (x1+w+0.02, y1+h/2), (x2-0.02, y2+h/2), GREY, 2.0)
# feedback: step 7 back to step 2
x7, y7 = pos[6]; x2_, y2_ = pos[1]
arrow(ax, (x7+w*0.5, y7+h+0.03), (x2_+w*0.5, y2_-0.03), RED, 1.8, rad=0.0, ls="--")
ax.text((x7+x2_)/2 + w*0.5 + 0.15, 2.2, "فشل أيّ فحص (تسرب بيانات، خروج عن النطاق، أخطاء غير آمنة)\nعُد إلى البيانات", ha="left", va="center", fontsize=10.5, color=RED)
save(fig, F + "fig1_3_workflow.png")
