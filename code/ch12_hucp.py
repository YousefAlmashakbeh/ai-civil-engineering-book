"""HU-CP (walls subset): record-level vs random patch split.
Data: Almashakbeh, Alelaimat, Al-Majali (2026) HU-CP v1.0, Zenodo, doi:10.5281/zenodo.23836570, CC BY 4.0.
Download HU_CP_W.zip and HU_CP_tables_README_audit.zip, unzip into HUCP_DIR (default ./hucp).
"""
import os, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from PIL import Image
from skimage.feature import hog
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split, GroupKFold, StratifiedKFold
from sklearn.metrics import roc_auc_score, f1_score, recall_score, precision_score
from joblib import Parallel, delayed

D = os.environ.get("HUCP_DIR", "hucp"); F = "fig"; os.makedirs(F, exist_ok=True)
if not os.path.exists(os.path.join(D, "tables")):
    raise SystemExit(f"HU-CP data not found in '{D}'. Download HU_CP_W.zip and HU_CP_tables_README_audit.zip from "
                     "https://doi.org/10.5281/zenodo.23836570, unzip them there, or set HUCP_DIR.")
lab = pd.read_csv(f"{D}/tables/patch_labels_clean.csv", low_memory=False)
SURF = os.environ.get("HUCP_SURFACE", "W")   # "W" walls (book figure) or "P" pavements
w = lab[lab.surface_code == SURF].reset_index(drop=True)
w["y"] = (w.label == "cracked").astype(int)

def feat(path):
    im = Image.open(f"{D}/{SURF}/{path}").convert("L").resize((64, 64), Image.BILINEAR)
    a = np.asarray(im, dtype=np.float32) / 255.0
    h = hog(a, orientations=9, pixels_per_cell=(8, 8), cells_per_block=(2, 2), feature_vector=True)
    g = np.abs(np.diff(a, axis=0)).mean(), np.abs(np.diff(a, axis=1)).mean()
    return np.concatenate([h, [a.mean(), a.std(), a.min(), np.percentile(a, 5), *g]])

cache = f"{D}/{SURF}_feats.npy"
if os.path.exists(cache): X = np.load(cache)
else:
    X = np.array(Parallel(n_jobs=-1)(delayed(feat)(p) for p in w.file)); np.save(cache, X)
y = w.y.values

def fit_eval(tr, te, seed=0):
    m = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08, random_state=seed)
    m.fit(X[tr], y[tr]); p = m.predict_proba(X[te])[:, 1]; yh = (p >= 0.5).astype(int)
    return dict(AUC=roc_auc_score(y[te], p), F1=f1_score(y[te], yh), recall=recall_score(y[te], yh),
                precision=precision_score(y[te], yh)), p

out = {"n_patches": len(w), "n_records": w.record.nunique(), "cracked": int(y.sum())}
# A) official record-level split (train+val -> train, test -> test)
tr = np.where(w.split != "test")[0]; te = np.where(w.split == "test")[0]
res_rec, p_rec = fit_eval(tr, te)
# B) random patch split with the same test size, repeated
rs = []
for s in range(3):
    a, b = train_test_split(np.arange(len(w)), test_size=len(te), stratify=y, random_state=s)
    rs.append(fit_eval(a, b, s)[0])
res_rand = {k: float(np.mean([r[k] for r in rs])) for k in rs[0]}
out["record_split"] = {k: round(v, 3) for k, v in res_rec.items()}
out["random_split"] = {k: round(v, 3) for k, v in res_rand.items()}
out["test_records"] = int(w.record[te].nunique()); out["test_patches"] = len(te)
# D) five-fold cross-validation over all records (GroupKFold by record) vs five random patch folds
f_rec = [fit_eval(a, b)[0]["F1"] for a, b in GroupKFold(5).split(X, y, w.record)]
f_rnd = [fit_eval(a, b)[0]["F1"] for a, b in StratifiedKFold(5, shuffle=True, random_state=0).split(X, y)]
out["cv5_by_record_F1"] = {"folds": [round(float(f), 3) for f in f_rec], "mean": round(float(np.mean(f_rec)), 3)}
out["cv5_random_F1"] = {"folds": [round(float(f), 3) for f in f_rnd], "mean": round(float(np.mean(f_rnd)), 3)}
# C) recall on cracked test patches by stated crack width and lighting
t = w.iloc[te].copy(); t["p"] = p_rec; c = t[t.y == 1].copy()
wm = c.width_mm.astype(str).str.strip()
c["wclass"] = np.where(wm.isin(["<1", "0.5"]), "< 1 mm", np.where(wm.isin(["1", "1.0", "1-2", "1.5"]), "1-1.5 mm", "≥ 1.8 mm"))
by_w = c.groupby("wclass").apply(lambda d: pd.Series({"n": len(d), "recall": (d.p >= .5).mean()}))
by_l = t.groupby("lighting").apply(lambda d: pd.Series({"n": len(d), "F1": f1_score(d.y, d.p >= .5) if d.y.sum() else np.nan}))
out["recall_by_width"] = by_w.round(3).to_dict("index"); out["by_lighting"] = by_l.round(3).to_dict("index")

pr = t.groupby("record").apply(lambda d: pd.Series({"n": len(d), "c": int(d.y.sum()), "F1": f1_score(d.y, d.p >= .5) if d.y.sum() else np.nan})).sort_values("F1")
out["per_record_F1"] = pr.round(3).to_dict("index")
# figure (needs the image folder)
if os.path.isdir(f"{D}/{SURF}"):
    fig = plt.figure(figsize=(5.6, 5.6)); gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.05], width_ratios=[1, 1.25], hspace=0.22, wspace=1.05)
    ax0 = fig.add_subplot(gs[0, :]); rng = np.random.default_rng(3)
    pick = [*rng.choice(np.where(y == 1)[0], 4, replace=False), *rng.choice(np.where(y == 0)[0], 4, replace=False)]
    tiles = [np.asarray(Image.open(f"{D}/{SURF}/{w.file[i]}").convert("L").resize((96, 96))) for i in pick]
    grid = np.vstack([np.hstack(tiles[:4]), np.hstack(tiles[4:])]); ax0.imshow(grid, cmap="gray"); ax0.axis("off")
    ax0.set_title(f"(a) HU-CP {'walls' if SURF=='W' else 'pavements'}: cracked (top), uncracked (bottom)", fontsize=9.5)
    # (b) as a dot plot: a bar starting at 0.85 would exaggerate a 0.01 difference; the 5-fold record-level CV mean of F1 is added
    ax1 = fig.add_subplot(gs[1, 0]); ks = ["AUC", "F1", "recall"]; yy = np.arange(3)[::-1]
    cvm = float(np.mean(f_rec))
    for yk, k in zip(yy, ks):
        for dy, v, mk, col in [(0.25, res_rand[k], "o", "#C05621"), (0.0, res_rec[k], "s", "#2B6CB0")] + ([(-0.27, cvm, "D", "#1A202C")] if k == "F1" else []):
            ax1.plot(v, yk + dy, mk, color=col, ms=5.5, mfc=col if mk != "D" else "white", mew=1.2)
            ax1.text(v + 0.011, yk + dy, f"{v:.3f}", ha="left", va="center", fontsize=8.6, color=col)
    lo = min(min(res_rand[k] for k in ks), min(res_rec[k] for k in ks), cvm); x0 = min(0.85, np.floor(lo * 20) / 20)
    ax1.set_xlim(x0, 1.05); ax1.set_xticks(np.arange(x0, 1.001, 0.05), minor=True); ax1.set_xticks([0.9, 1.0]); ax1.set_xticklabels(["0.90", "1.00"], fontsize=8.6)
    ax1.set_yticks(yy); ax1.set_yticklabels(ks, fontsize=8.6); ax1.set_ylim(-0.55, 2.5); ax1.grid(axis="x", which="both", color="#E2E8F0", lw=0.6); ax1.set_axisbelow(True)
    from matplotlib.lines import Line2D
    hh = [Line2D([], [], ls="none", marker="o", color="#C05621", ms=5.5), Line2D([], [], ls="none", marker="s", color="#2B6CB0", ms=5.5),
          Line2D([], [], ls="none", marker="D", color="#1A202C", mfc="white", ms=5.5, mew=1.2)]
    ax1.legend(hh, ["random patch split", "record-level split", "record-level 5-fold CV\n(mean F1)"], loc="upper center", bbox_to_anchor=(0.45, -0.12), ncol=1, fontsize=8.6, frameon=False)
    ax1.set_title("(b) same model, two splits", fontsize=9.5)
    ax2 = fig.add_subplot(gs[1, 1])
    ax2.barh(range(len(pr)), pr.F1, color="#2F855A"); ax2.set_yticks(range(len(pr)))
    ax2.set_yticklabels([f"{r} (n={int(n)})" for r, n in zip(pr.index, pr.n)], fontsize=8.6); ax2.set_xlim(0, 1); ax2.tick_params(axis="x", labelsize=8.6)
    ax2.axvline(res_rec["F1"], ls="--", c="k", lw=.8); ax2.set_xlabel("F1 on each test record", fontsize=9)
    ax2.set_title(f"(c) {len(pr)} test records", fontsize=9.5)
    fig.savefig(f"{F}/fig12_4_hucp.png" if SURF == "W" else f"{F}/fig12_4_hucp_{SURF}.png", dpi=260, bbox_inches="tight"); plt.close()

import json; print(json.dumps(out, indent=1, default=float, ensure_ascii=False))
