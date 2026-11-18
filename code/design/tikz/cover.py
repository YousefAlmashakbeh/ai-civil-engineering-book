# -*- coding: utf-8 -*-
"""Front cover (A4) and part-opening pages for the print edition."""
from tk import *
import tk, random
tk.PRE = tk.PRE.replace("border=7pt", "border=0pt")
def cover():
    f = Fig("cover"); W, H = 21.0, 29.7; random.seed(7)
    f.add(r"\fill[navy] (0,0) rectangle (%.1f,%.1f);" % (W, H))
    f.add(r"\shade[top color=navy,bottom color=black!70!navy] (0,0) rectangle (%.1f,11);" % W)
    # faint engineering grid
    for i in range(1, 21): f.add(r"\draw[white,opacity=0.035,line width=0.4pt] (%d,11) -- (%d,%.1f);" % (i, i, H))
    for j in range(11, 30): f.add(r"\draw[white,opacity=0.035,line width=0.4pt] (0,%d) -- (%.1f,%d);" % (j, W, j))
    # cable-stayed bridge whose cables continue into a neural network
    deck_y, px, top = 15.2, 10.5, 24.6
    deck = [2.0 + i*1.7 for i in range(11)]
    f.add(r"\draw[white,opacity=0.9,line width=3pt,line cap=round] (0.8,%.2f) -- (%.2f,%.2f);" % (deck_y, W - 0.8, deck_y))
    f.add(r"\draw[white,opacity=0.9,line width=5pt,line cap=round] (%.2f,%.2f) -- (%.2f,%.2f);" % (px, deck_y - 2.2, px, top))
    for k, x in enumerate(deck):
        if abs(x - px) < 0.5: continue
        yy = top - 0.55*(abs(x - px)/1.7 - 1)
        f.add(r"\draw[blue!45!white,opacity=0.85,line width=1pt] (%.2f,%.2f) -- (%.2f,%.2f);" % (px, yy, x, deck_y))
    # hidden layer nodes above the deck, output node at the pylon top
    hid = [(3.2 + i*2.9, 27.0) for i in range(6)]
    for hx, hy in hid:
        f.add(r"\draw[gold,opacity=0.55,line width=0.7pt] (%.2f,%.2f) -- (%.2f,%.2f);" % (hx, hy, px, top))
        for x in deck[1::2]:
            f.add(r"\draw[white,opacity=0.07,line width=0.5pt] (%.2f,%.2f) -- (%.2f,%.2f);" % (hx, hy, x, deck_y))
    for hx, hy in hid: f.add(r"\fill[gold] (%.2f,%.2f) circle (0.2); \fill[navy] (%.2f,%.2f) circle (0.09);" % (hx, hy, hx, hy))
    for x in deck: f.add(r"\fill[orange!80!white] (%.2f,%.2f) circle (0.2); \fill[white] (%.2f,%.2f) circle (0.08);" % (x, deck_y, x, deck_y))
    f.add(r"\fill[white] (%.2f,%.2f) circle (0.3); \fill[orange] (%.2f,%.2f) circle (0.15);" % (px, top, px, top))
    for x in (4.5, 16.5): f.add(r"\fill[white,opacity=0.9] (%.2f,%.2f) rectangle (%.2f,%.2f);" % (x - 0.22, deck_y - 2.2, x + 0.22, deck_y - 0.05))
    f.add(r"\draw[blue!40!white,opacity=0.5,line width=1.2pt] plot[smooth,tension=0.7] coordinates {(0,12.75) (3,12.95) (6,12.7) (9,12.95) (12,12.7) (15,12.95) (18,12.7) (21,12.9)};")
    # title block
    f.add(r"\fill[gold] (%.2f,9.55) rectangle (%.2f,9.67);" % (W - 6.3, W - 1.8))
    f.add(r"\node[anchor=east,text=white,font=\fontsize{38}{48}\selectfont\bfseries,align=right,inner sep=0pt] at (%.2f,7.9) {%s};" % (W - 1.8, R("الذكاء الاصطناعي")))
    f.add(r"\node[anchor=east,text=white,font=\fontsize{38}{48}\selectfont\bfseries,align=right,inner sep=0pt] at (%.2f,6.05) {%s};" % (W - 1.8, R("في الهندسة المدنية")))
    f.add(r"\node[anchor=east,text=blue!35!white,font=\fontsize{20}{26}\selectfont,inner sep=0pt] at (%.2f,4.55) {%s};" % (W - 1.8, R("من المبادئ إلى التطبيق")))
    f.add(r"\node[anchor=east,text=white,opacity=0.8,font=\fontsize{11.5}{15}\selectfont,inner sep=0pt] at (%.2f,3.45) {%s};" % (W - 1.8, R("18 فصلاً  •  أمثلة محلولة بالشيفرة  •  حالات عربية محلولة  •  بيانات مفتوحة")))
    f.add(r"\node[anchor=east,text=white,font=\fontsize{17}{22}\selectfont\bfseries,inner sep=0pt] at (%.2f,1.95) {%s};" % (W - 1.8, R("م. د. يوسف المشاقبة")))
    f.add(r"\node[anchor=east,text=white,opacity=0.75,font=\fontsize{12}{15}\selectfont,inner sep=0pt] at (%.2f,1.25) {%s};" % (W - 1.8, R("الجامعة الهاشمية")))
    f.add(r"\node[anchor=west,text=white,opacity=0.75,font=\fontsize{12}{15}\selectfont,inner sep=0pt] at (1.8,1.25) {%s};" % R("الطبعة الأولى — 2026"))
    f.add(r"\path[use as bounding box] (0,0) rectangle (%.1f,%.1f);" % (W, H))
    f.build(dpi=200)
if __name__ == "__main__": cover()
