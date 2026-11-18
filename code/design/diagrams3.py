from bookstyle import *
F = "../../figures/"
def chain(steps, fname, w=1.85, h=1.55, note=None, note_col=RED, hl=None, H=3.0):
    n = len(steps); W = n*w + (n-1)*0.35 + 0.4
    fig, ax = canvas(W, H)
    xs = [W - 0.2 - (i+1)*w - i*0.35 for i in range(n)]
    for i, ((t, b, c), x) in enumerate(zip(steps, xs)):
        card(ax, x, H-h-0.35, w, h, t, b, c, fs=12.5, bfs=10, num=i+1)
        if i: arrow(ax, (xs[i-1]-0.02, H-0.35-h/2), (x+w+0.02, H-0.35-h/2), GREY, 2)
    if note:
        i, txt = note; x = xs[i]
        ax.add_patch(FancyBboxPatch((x-0.1, 0.05), w+0.2, H-h-0.65, boxstyle="round,pad=0,rounding_size=0.1", fc=TINT[note_col], ec=note_col, lw=1.2, ls="--"))
        ax.text(x+w/2, 0.05+(H-h-0.65)/2, txt, ha="center", va="center", fontsize=10, color=note_col)
        arrow(ax, (x+w/2, H-h-0.55), (x+w/2, H-h-0.38), note_col, 1.4, head=10)
    save(fig, F + fname)
chain([("القياس", "تسارع، انفعال،\nحرارة، UPV", NAVY), ("الخصائص", "ترددات، طاقة،\nسرعة موجة", BLUE),
       ("إزالة أثر البيئة", "نموذج حرارة\nورطوبة وحمل", ORANGE), ("المقارنة", "بالحالة المرجعية\n(سنة أساس)", BLUE),
       ("قاعدة الإنذار", "عتبة معروفة\nمعدل إنذار كاذب", BLUE), ("قرار المهندس", "فحص، تقييد،\nصيانة", GREEN)],
      "fig13_6_pipeline.png", note=(2, "هنا تولد معظم الإنذارات الكاذبة\nوهنا يضيع معظم الضرر الخفي"), H=3.2)
chain([("سؤال المهندس", "بلغته وبمصطلحات\nالموقع", NAVY), ("التطبيع", "همزات، تاء مربوطة،\nتشكيل", BLUE),
       ("الاسترجاع", "أفضل ثلاثة مقاطع\nمن الكود والعقد", BLUE), ("المسودة", "النموذج اللغوي\nمع أرقام البنود", ORANGE),
       ("الحارس", "تحقق من الأرقام\nوالاستشهادات", RED), ("المراجعة", "المهندس يراجع\nويوقّع", GREEN)],
      "fig17_2_pipeline.png", note=(4, "رقم لا يوجد في المقطع المسترجع\n← يُرفض الجواب ويعود للمهندس"), H=3.2)
# ---------- Fig 16.5: three levels ----------
fig, ax = canvas(12, 3.9); ax.set_xlim(-0.1, 12)
lv = [("النموذج الرقمي", "لا تدفق آلي للبيانات", GREY, "يدوي", "يدوي"), ("الظل الرقمي", "البيانات تتدفق إلى النموذج آلياً", BLUE, "آلي", "يدوي"),
      ("التوأم الرقمي", "التدفق آلي في الاتجاهين", GREEN, "آلي", "آلي")]
for i, (t, sub, c, up, down) in enumerate(lv):
    x0 = 12 - 0.15 - (i+1)*3.75 - i*0.25 + 0.0
    ax.add_patch(FancyBboxPatch((x0, 0.15), 3.75, 3.35, boxstyle="round,pad=0,rounding_size=0.15", fc=TINT[c], ec=c, lw=1.6))
    ax.text(x0+1.875, 3.15, t, ha="center", fontsize=15, color=c, fontweight="bold"); ax.text(x0+1.875, 2.75, sub, ha="center", fontsize=10.5, color="#2D3748")
    card(ax, x0+2.15, 1.0, 1.4, 1.0, "المنشأة", "حساسات", NAVY, fs=11.5, bfs=9.5, shadow=False)
    card(ax, x0+0.2, 1.0, 1.4, 1.0, "النموذج", "صلابة، حالة", c, fs=11.5, bfs=9.5, shadow=False)
    cu = c if up == "آلي" else GREY; cd = c if down == "آلي" else GREY
    arrow(ax, (x0+2.12, 1.72), (x0+1.63, 1.72), cu, 2.2, ls="-" if up == "آلي" else "--")
    arrow(ax, (x0+1.63, 1.28), (x0+2.12, 1.28), cd, 2.2, ls="-" if down == "آلي" else "--")
    ax.text(x0+1.875, 0.55, f"بيانات ← نموذج: {up}    قرار ← منشأة: {down}", ha="center", fontsize=10, color=NAVY)
save(fig, F + "fig16_2_twinlevels.png")
