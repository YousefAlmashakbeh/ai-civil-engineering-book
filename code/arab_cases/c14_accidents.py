# Jordan road deaths 2019-2024 (Public Security Directorate annual reports, as reported by Jordan Times)
import numpy as np
from scipy import stats, optimize
yr  = np.array([2019, 2020, 2021, 2022, 2023, 2024])
dth = np.array([643, 461, 589, 562, 560, 543])
acc = np.array([161511, np.nan, 160000, 169409, 170058, 190175])   # 2021 is "around 160,000"
print("year  deaths  accidents  deaths/1000 acc")
for y, d, a in zip(yr, dth, acc):
    print(f"{y}  {d:6d}  {'   n/a  ' if np.isnan(a) else f'{a:9,.0f}'}  {'  n/a' if np.isnan(a) else f'{1000*d/a:5.2f}'}")
print(f"2023 rates: {560/11.5e6*1e5:.2f} deaths per 100k people, {560/1930958*1e4:.2f} per 10k vehicles")
print(f"pedestrian check: 219 / 0.361 = {219/0.361:.0f} deaths  (headline figure 560)")
# Poisson log-linear trend, 2020 (lockdown year) left out of the fit
m = yr != 2020; x = yr - 2019
def nll(b): mu = np.exp(b[0] + b[1]*x[m]); return np.sum(mu - dth[m]*np.log(mu))
b = optimize.minimize(nll, [np.log(600), 0.0]).x
H = np.zeros((2, 2)); mu = np.exp(b[0] + b[1]*x[m])
for xi, mi in zip(x[m], mu): v = np.array([1, xi]); H += mi*np.outer(v, v)
se = np.sqrt(np.diag(np.linalg.inv(H)))
print(f"trend: {100*(np.exp(b[1])-1):+.1f}% per year  (95% CI {100*(np.exp(b[1]-1.96*se[1])-1):+.1f}% to {100*(np.exp(b[1]+1.96*se[1])-1):+.1f}%)")
e20 = np.exp(b[0] + b[1]*1); z = (461 - e20)/np.sqrt(e20)
print(f"2020 expected {e20:.0f}, observed 461, z = {z:.1f}")
mu25 = np.exp(b[0] + b[1]*6); lo, hi = stats.poisson.ppf([0.05, 0.95], mu25)
print(f"2025 forecast: {mu25:.0f} deaths, 90% Poisson interval {lo:.0f}-{hi:.0f}")
