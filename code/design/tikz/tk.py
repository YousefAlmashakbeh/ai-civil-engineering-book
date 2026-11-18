# -*- coding: utf-8 -*-
"""TikZ/XeLaTeX figure toolkit for the book: Arabic RTL text, one visual identity."""
import re, os, subprocess, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.environ.get("BOOK_FONTS", os.path.join(HERE, "fonts"))
OUT = os.environ.get("BOOK_FIG_OUT", os.path.join(HERE, "..", "png"))
WORK = os.environ.get("BOOK_FIG_WORK", os.path.join(HERE, "build"))
COL = dict(navy="1A365D", blue="2B6CB0", orange="C05621", green="2F855A", red="C53030", gold="B7791F", grey="718096",
           slate="4A5568", ink="1A202C", line="CBD5E0", paper="F7FAFC",
           navyT="E6EEF7", blueT="EBF4FF", orangeT="FFF5EB", greenT="F0FFF4", redT="FFF5F5", goldT="FFFBEB", greyT="EDF2F7")
PRE = r"""\documentclass[tikz,border=7pt]{standalone}
\usepackage{fontspec}
\usepackage{amsmath}
\usetikzlibrary{shapes.geometric,shapes.misc,arrows.meta,positioning,shadows.blur,calc,fit,backgrounds,decorations.pathreplacing,patterns}
\setmainfont[Path=%(fonts)s/,Extension=.ttf,UprightFont=*-Regular,BoldFont=*-SemiBold,Script=Arabic]{IBMPlexSansArabic}
\newfontfamily\lt[Path=%(fonts)s/,Extension=.ttf,UprightFont=*-Regular,BoldFont=*-SemiBold]{IBMPlexSansArabic}
\TeXXeTstate=1
\newcommand{\R}[1]{{\beginR #1\endR}}
\newcommand{\LL}[1]{{\beginL\lt #1\endL}}
%(colors)s
\tikzset{
  every picture/.style={line cap=round,line join=round},
  sh/.style={blur shadow={shadow blur steps=8,shadow xshift=0.6pt,shadow yshift=-1.2pt,shadow opacity=22,shadow blur radius=2.2pt}},
  conn/.style={draw=slate,line width=1.05pt,-{Stealth[length=6.5pt,width=5.5pt]},rounded corners=5pt},
  connc/.style={conn,draw=#1},
  fb/.style={draw=red,line width=1pt,dash pattern=on 4pt off 2.5pt,-{Stealth[length=6.5pt,width=5.5pt]},rounded corners=5pt},
  lab/.style={font=\footnotesize,text=slate,inner sep=2pt},
  pill/.style={rounded rectangle,fill=#1,text=white,font=\bfseries\footnotesize,inner xsep=7pt,inner ysep=3pt},
  dec/.style={diamond,aspect=1.9,draw=#1,line width=0.9pt,fill=white,sh,align=center,inner sep=1.5pt,font=\small},
  term/.style={rounded rectangle,draw=#1,line width=0.9pt,fill=#1,text=white,sh,align=center,font=\bfseries\small,inner xsep=10pt,inner ysep=6pt},
}
\begin{document}
\begin{tikzpicture}[font=\small]
"""
POST = "\n\\end{tikzpicture}\n\\end{document}\n"
_LAT = re.compile(r"[A-Za-z0-9\\$][A-Za-z0-9 \-\+/\.,:=×%@'_\^\{\}\\$²³⁴]*[A-Za-z0-9%\}$²³⁴]|[A-Za-z0-9]")
def esc(s):
    return s.replace("&", r"\&").replace("%", r"\%").replace("#", r"\#")
def Rin(s):
    """Inner RTL text: Latin/number runs are set left-to-right (the font engine mirrors brackets itself)."""
    out, pos = [], 0
    for m in _LAT.finditer(s):
        out.append(s[pos:m.start()]); out.append(r"\LL{" + m.group(0) + "}"); pos = m.end()
    out.append(s[pos:])
    return esc("".join(out))
def R(s, bold=False):
    t = Rin(s)
    if bold: t = r"\textbf{" + t + "}"
    return r"\R{" + t + "}"
def RL(s, bold=False):
    return r"\\".join(R(l, bold) for l in s.split("\n"))
class Fig:
    def __init__(self, name): self.name, self.b = name, []
    def add(self, s): self.b.append(s)
    def card(self, id, x, y, w, h, title, body=None, col="blue", num=None, hb=0.62, tfs=r"\small", bfs=r"\footnotesize", shadow=True, fill="white"):
        """Card centred at (x,y): coloured header bar with white title (and number badge), white body."""
        a = self.add; x0, x1, y0, y1 = x - w/2, x + w/2, y - h/2, y + h/2
        a(r"\node[rectangle,rounded corners=4pt,fill=%s,minimum width=%.3fcm,minimum height=%.3fcm,inner sep=0pt%s] (%s) at (%.3f,%.3f) {};" % (fill, w, h, ",sh" if shadow else "", id, x, y))
        a(r"\begin{scope}\clip[rounded corners=4pt] (%.3f,%.3f) rectangle (%.3f,%.3f);\fill[%s] (%.3f,%.3f) rectangle (%.3f,%.3f);\end{scope}" % (x0, y0, x1, y1, col, x0, y1 - hb, x1, y1))
        a(r"\draw[%s,line width=0.8pt,rounded corners=4pt] (%.3f,%.3f) rectangle (%.3f,%.3f);" % (col, x0, y0, x1, y1))
        tx = x - (0.26 if num is not None else 0)
        a(r"\node[text=white,font=\bfseries%s,inner sep=0pt] at (%.3f,%.3f) {%s};" % (tfs, tx, y1 - hb/2, R(title)))
        if num is not None:
            a(r"\node[circle,fill=white,text=%s,font=\bfseries\footnotesize,inner sep=0pt,minimum size=0.42cm] at (%.3f,%.3f) {\lt %s};" % (col, x1 - 0.36, y1 - hb/2, num))
        if body:
            a(r"\node[text=ink,font=%s,align=center,text width=%.3fcm,inner sep=0pt] at (%.3f,%.3f) {%s};" % (bfs, w - 0.3, x, (y0 + y1 - hb)/2, RL(body)))
    def text(self, x, y, s, opts=""):
        self.add(r"\node[%s] at (%.3f,%.3f) {%s};" % (opts, x, y, RL(s)))
    def build(self, dpi=300):
        os.makedirs(WORK, exist_ok=True); os.makedirs(OUT, exist_ok=True)
        cols = "\n".join(r"\definecolor{%s}{HTML}{%s}" % kv for kv in COL.items())
        pre = PRE % dict(fonts=FONTS.replace("\\", "/"), colors=cols)
        k = float(os.environ.get("BOOK_FONT_SCALE", "1"))
        if k != 1:   # print-size fonts: every size command scaled by k
            defs = "".join(r"\renewcommand\%s{\fontsize{%.2f}{%.2f}\selectfont}" % (n, b * k, b * k * 1.2)
                           for n, b in (("scriptsize", 7), ("footnotesize", 8), ("small", 9), ("normalsize", 10), ("large", 12), ("Large", 14.4)))
            pre = pre.replace("\\begin{document}", "\\begin{document}" + defs)
        tex = pre + "\n".join(self.b) + POST
        p = os.path.join(WORK, self.name + ".tex"); open(p, "w", encoding="utf8").write(tex)
        r = subprocess.run(["xelatex", "-interaction=batchmode", "-halt-on-error", self.name + ".tex"], cwd=WORK, capture_output=True, text=True)
        if r.returncode:
            log = open(os.path.join(WORK, self.name + ".log"), encoding="utf8", errors="ignore").read()
            i = log.find("\n!"); print("FAILED", self.name, log[i:i+500]); return False
        subprocess.run(["pdftoppm", "-r", str(dpi), "-singlefile", "-png", self.name + ".pdf", os.path.join(OUT, self.name)], cwd=WORK, check=True)
        pdfdir = os.path.join(OUT, "..", "pdf"); os.makedirs(pdfdir, exist_ok=True)
        subprocess.run(["cp", os.path.join(WORK, self.name + ".pdf"), pdfdir])
        print("ok", self.name); return True
