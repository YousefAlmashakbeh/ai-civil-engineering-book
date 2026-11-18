# Chapter 7, Example 7.3 repeated on 200 seeds:
# Bayesian optimisation vs. simple bisection vs. fitting Abrams' law, seven mixes each.
# "True error" = |f(w/b recommended) - 40 MPa| on the noise-free strength law.
import warnings
import numpy as np
from scipy.stats import norm
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel as Ck

warnings.filterwarnings("ignore")
law = lambda w: 110 / 6.5**w                 # strength law used in Example 7.3
grid = np.linspace(0.3, 0.7, 401)
err = {"bayes": [], "bisection": [], "abrams": []}

for seed in range(200):
    # 1) Bayesian optimisation exactly as in ch7.py (two starting mixes + five chosen)
    rng = np.random.default_rng(seed)
    lab = lambda w: law(w) * rng.normal(1, 0.03)
    obj = lambda f: -abs(f - 40)
    X = [0.35, 0.60]; Y = [obj(lab(x)) for x in X]
    for it in range(5):
        gp = GaussianProcessRegressor(Ck(10) * RBF(0.1) + WhiteKernel(0.5), normalize_y=True,
                                      random_state=0).fit(np.array(X)[:, None], Y)
        mu, sd = gp.predict(grid[:, None], return_std=True)
        best = max(Y); z = (mu - best) / (sd + 1e-9)
        ei = (mu - best) * norm.cdf(z) + sd * norm.pdf(z)
        X.append(grid[ei.argmax()]); Y.append(obj(lab(X[-1])))
    err["bayes"].append(abs(law(X[int(np.argmax(Y))]) - 40))      # best measured mix

    # 2) bisection on the same bracket, same number of mixes (2 + 5)
    rng = np.random.default_rng(seed)
    a, b = 0.35, 0.60; lab(a); lab(b)
    for it in range(5):
        m = (a + b) / 2
        if lab(m) > 40: a = m
        else: b = m
    err["bisection"].append(abs(law((a + b) / 2) - 40))

    # 3) Abrams' law fitted to seven mixes spread over the bracket
    rng = np.random.default_rng(seed)
    xs = np.linspace(0.35, 0.60, 7)
    slope, icpt = np.polyfit(xs, np.log([lab(x) for x in xs]), 1)
    err["abrams"].append(abs(law((np.log(40) - icpt) / slope) - 40))

for k, v in err.items():
    print(f"{k:10s} mean true error = {np.mean(v):.2f} MPa  (median {np.median(v):.2f})")
