import re, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from ch17_corpus import DOCS, QA

def norm_ar(s):
    s = re.sub(r"[ً-ْـ]", "", s)            # diacritics, tatweel
    s = re.sub("[إأآا]", "ا", s); s = s.replace("ى", "ي").replace("ة", "ه")
    return s
def tok(s): return re.findall(r"\w+", s)

class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.D = [tok(d) for d in docs]; self.k1, self.b = k1, b
        self.avg = np.mean([len(d) for d in self.D]); N = len(self.D)
        df = {}
        for d in self.D:
            for w in set(d): df[w] = df.get(w, 0) + 1
        self.idf = {w: np.log(1 + (N - n + 0.5) / (n + 0.5)) for w, n in df.items()}
    def scores(self, q):
        s = np.zeros(len(self.D))
        for i, d in enumerate(self.D):
            L = len(d)
            for w in tok(q):
                f = d.count(w)
                if f: s[i] += self.idf[w] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * L / self.avg))
        return s

def tfidf_ret(analyzer, ngram, pre=None):
    v = TfidfVectorizer(analyzer=analyzer, ngram_range=ngram, preprocessor=pre, sublinear_tf=True)
    X = v.fit_transform(DOCS)
    return lambda q: (X @ v.transform([q]).T).toarray().ravel()

bm = BM25(DOCS)
bmn = BM25([norm_ar(d) for d in DOCS])
retrievers = {
    "Word TF-IDF": tfidf_ret("word", (1, 1)),
    "BM25 (words)": bm.scores,
    "BM25 + Arabic normalisation": lambda q: bmn.scores(norm_ar(q)),
    "Char 2-4 TF-IDF": tfidf_ret("char_wb", (2, 4)),
    "Char 2-4 + normalisation": tfidf_ret("char_wb", (2, 4), pre=norm_ar),
}
res = {}
print("Chapter 17 RAG retrieval: %d original snippets, %d questions" % (len(DOCS), len(QA)))
for name, f in retrievers.items():
    h1 = h3 = 0; miss = []
    for q, gold in QA:
        s = f(q); order = np.argsort(-s)
        h1 += order[0] == gold; h3 += gold in order[:3]
        if gold not in order[:3]: miss.append(q)
    res[name] = (h1 / len(QA), h3 / len(QA), miss)
    print("  %-28s hit@1=%.2f  hit@3=%.2f  misses(top3)=%d" % (name, h1 / len(QA), h3 / len(QA), len(miss)))
best = "Char 2-4 + normalisation"
print("  questions missed by best retriever:")
for q in res[best][2]: print("   -", q)

# numeric guard: check every number+unit in an answer against the retrieved snippet
def numbers(s):
    return set(re.findall(r"(\d+(?:\.\d+)?)\s*(مم|متر|درجة|يوم|أيام|ساعة|متراً)", s))
cases = [
    ("كم الغطاء الخرساني للأساسات الملامسة للتربة؟", "الحد الأدنى للغطاء في الأساسات الملامسة للتربة هو 75 مم."),
    ("كم الغطاء الخرساني للأساسات الملامسة للتربة؟", "الحد الأدنى للغطاء في الأساسات الملامسة للتربة هو 50 مم."),
    ("متى تفك الدعامات السفلية للبلاطات؟", "تفك الدعامات بعد 7 أيام إذا كان الجو حاراً."),
]
f = retrievers[best]
print("Numeric guard (answers are illustrative inputs written for the example):")
for q, ans in cases:
    src = DOCS[int(np.argmax(f(q)))]
    a, s = numbers(ans), numbers(src)
    bad = [n for n in a if n[0] not in {x[0] for x in s}]
    print("  Q: %s | answer numbers=%s | source numbers=%s -> %s" %
          (q, sorted(x[0] for x in a), sorted(x[0] for x in s), "FLAG: unsupported " + ",".join(n[0] for n in bad) if bad else "OK"))

fig, ax = plt.subplots(figsize=(7.5, 3.6))
names = list(res); x = np.arange(len(names))
ax.bar(x - 0.18, [100 * res[n][0] for n in names], 0.36, label="hit@1", color="#2B6CB0")
ax.bar(x + 0.18, [100 * res[n][1] for n in names], 0.36, label="hit@3", color="#C05621")
ax.set_xticks(x); ax.set_xticklabels(names, rotation=15, fontsize=8); ax.set_ylabel("Questions answered (%)")
ax.set_ylim(0, 100); ax.legend(fontsize=8)
for i, n in enumerate(names):
    ax.text(i + 0.18, 100 * res[n][1] + 1.5, "%.0f" % (100 * res[n][1]), ha="center", fontsize=7)
plt.tight_layout(); plt.savefig("fig/fig17_1_retrieval.png", dpi=150); plt.close()

# Figure 17.2: RAG pipeline schematic
fig, ax = plt.subplots(figsize=(9, 2.6)); ax.axis("off")
boxes = [("Engineer's\nquestion", 0.06), ("Normalise +\nretrieve top-3", 0.25), ("Snippets with\nclause IDs", 0.44),
         ("LLM drafts answer\nciting snippets", 0.63), ("Numeric & citation\nguard", 0.80), ("Engineer\nreviews & signs", 0.95)]
for t, xc in boxes:
    ax.add_patch(plt.Rectangle((xc - 0.075, 0.3), 0.15, 0.4, fill=True, fc="#e8f0fb", ec="#2B6CB0"))
    ax.text(xc, 0.5, t, ha="center", va="center", fontsize=8)
for (_, a), (_, b) in zip(boxes[:-1], boxes[1:]):
    ax.annotate("", xy=(b - 0.077, 0.5), xytext=(a + 0.077, 0.5), arrowprops=dict(arrowstyle="->"))
ax.annotate("", xy=(0.63, 0.28), xytext=(0.80, 0.28), arrowprops=dict(arrowstyle="->", color="#C53030", connectionstyle="arc3,rad=0.5"))
ax.text(0.715, 0.05, "flag -> regenerate or escalate", ha="center", fontsize=7, color="#C53030")
ax.set_xlim(0, 1.03); ax.set_ylim(0, 1)
plt.tight_layout(); plt.savefig("fig/fig17_2_pipeline.png", dpi=150); plt.close()

# site-jargon glossary (query expansion): colloquial/borrowed term -> formal term in the documents
GLOSS = {"سلامب": "هبوط", "كفر": "الغطاء الخرساني", "باطون": "الخرسانة", "طوبار": "قوالب", "شميت": "مطرقة الارتداد",
         "هامر": "مطرقة", "فايبريتر": "الهزاز", "مي": "ماء", "بالمي": "بالماء", "شوالات": "أكياس الإسمنت", "القوائم": "الدعامات",
         "التغطية": "الغطاء الخرساني", "نرش": "معالجة", "قوام": "هبوط", "الصبة": "الخرسانة", "البئر": "مياه الخلط",
         "الشمس": "الطقس الحار", "شاحنة": "الخلط", "نكب": "السقوط الحر"}
def expand(q): return q + " " + " ".join(v for k, v in GLOSS.items() if k in q)
f = retrievers[best]
h1 = h3 = 0
for q, gold in QA:
    o = np.argsort(-f(expand(q))); h1 += o[0] == gold; h3 += gold in o[:3]
print("  %-28s hit@1=%.2f  hit@3=%.2f  (glossary of %d terms, written after seeing the questions -> optimistic)" %
      ("Char+norm+site glossary", h1 / len(QA), h3 / len(QA), len(GLOSS)))
