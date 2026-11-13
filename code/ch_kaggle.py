"""Worked examples on open Kaggle datasets (licences checked Nov 2026).
Data are not redistributed; download them from Kaggle into kaggle_dl/<name>/.
  seattle_energy  : city-of-seattle/sea-building-energy-benchmarking (CC0)
  melbourne_ww    : samansiadati/melbourne-water-19952019 (CC BY 4.0)
  slope_stability : ziya07/slope-stability-analysis-dataset (CC0)
  sustainable_concrete : ziya07/sustainable-concrete-dataset (CC0)
  frp_bond        : vijayaadithyanvg/frp-bond-strength (CC0)
"""
import os, glob, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.linear_model import RidgeCV
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.inspection import permutation_importance

D = os.environ.get("KAGGLE_DIR", "kaggle_dl"); F = "fig"; os.makedirs(F, exist_ok=True)
out = {}

# ---------- K1: data audit ----------
s = pd.read_csv(f"{D}/slope_stability/slope_stability_dataset.csv")
np.random.seed(42); gen = 15 + 10*np.random.rand(len(s))
out["slope_seed42_match"] = float(np.mean(np.isclose(gen, s.iloc[:, 0])))
c = pd.read_csv(f"{D}/sustainable_concrete/sustainable_concrete_dataset.csv")
y = pd.read_csv(f"{D}/frp_bond/concrete_data.csv"); y.columns = [k.strip() for k in y.columns]
out["sust_fc_range"] = (float(c.compressive_strength.min()), float(c.compressive_strength.max()))
out["frp_is_yeh"] = list(y.columns)[:3] + [len(y)]
out["sust_corr_fc_cement"] = float(c[["cement", "compressive_strength"]].corr().iloc[0, 1])
out["yeh_corr_fc_cement"] = float(y[["cement", "concrete_compressive_strength"]].corr().iloc[0, 1])

fig, ax = plt.subplots(1, 3, figsize=(12, 3.4))
ax[0].hist(s["Cohesion (kPa)"], 40, color="#7a8ca8"); ax[0].set_title("(a) Slope set: cohesion is flat U(5,50)", fontsize=9)
ax[0].set_xlabel("c (kPa)")
ax[1].scatter(gen[:300], s.iloc[:300, 0], s=4); ax[1].set_title(f"(b) np.random.seed(42) reproduces {out['slope_seed42_match']:.0%}", fontsize=9)
ax[1].set_xlabel("generated value"); ax[1].set_ylabel("unit weight in file")
ax[2].hist(y.concrete_compressive_strength, 40, alpha=.7, label="Yeh (real, UCI)")
ax[2].hist(c.compressive_strength, 40, alpha=.7, label="'sustainable' set")
ax[2].axvline(120, ls="--", c="k", lw=.8); ax[2].set_xlabel("f'c (MPa)"); ax[2].legend(fontsize=7)
ax[2].set_title("(c) Strengths up to 615 MPa are impossible", fontsize=9)
fig.tight_layout(); fig.savefig(f"{F}/figK1_audit.png", dpi=200); plt.close()

# ---------- K2: Seattle building energy (Ch16) ----------
e = pd.read_csv(f"{D}/seattle_energy/2016-building-energy-benchmarking.csv")
e = e[(e.ComplianceStatus == "Compliant") & e.Outlier.isna() & ~e.BuildingType.str.contains("Multifamily")]
e = e[(e["SiteEUI(kBtu/sf)"] > 0) & (e["PropertyGFABuilding(s)"] > 0)].copy()
e["logEUI"] = np.log(e["SiteEUI(kBtu/sf)"])
e["logGFA"] = np.log(e["PropertyGFABuilding(s)"])
e["parking_frac"] = e["PropertyGFAParking"] / e["PropertyGFATotal"]
e["gas_share"] = e["NaturalGas(kBtu)"].fillna(0) / e["SiteEnergyUse(kBtu)"].replace(0, np.nan)
e["steam"] = (e["SteamUse(kBtu)"].fillna(0) > 0).astype(int)
cat = e["LargestPropertyUseType"].fillna("NA")
top = cat.value_counts().index[:12]; e["use"] = np.where(cat.isin(top), cat, "Other")
num = ["YearBuilt", "NumberofFloors", "logGFA", "parking_frac", "Latitude", "Longitude"]
X0 = pd.get_dummies(e[num + ["use"]], columns=["use"], dtype=float).fillna(0); yv = e.logEUI.values
kf = KFold(5, shuffle=True, random_state=0)
p_lin = cross_val_predict(RidgeCV(alphas=np.logspace(-2, 3, 20)), X0, yv, cv=kf)
gbm = HistGradientBoostingRegressor(max_iter=400, learning_rate=0.05, max_leaf_nodes=15, random_state=0)
p_gbm = cross_val_predict(gbm, X0, yv, cv=kf)
X1 = X0.assign(gas_share=e.gas_share.fillna(0).values, steam=e.steam.values)
p_gbm2 = cross_val_predict(gbm, X1, yv, cv=kf)
def m(p): return dict(R2=round(r2_score(yv, p), 3), MAE_pct=round(float(np.mean(np.abs(np.exp(p - yv) - 1))*100), 1))
out["seattle_n"] = len(e); out["seattle_ridge"] = m(p_lin); out["seattle_gbm"] = m(p_gbm); out["seattle_gbm_fuel"] = m(p_gbm2)
gbm.fit(X1, yv); pi = permutation_importance(gbm, X1, yv, n_repeats=5, random_state=0)
imp = pd.Series(pi.importances_mean, X1.columns).sort_values()[-8:]
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].scatter(np.exp(yv), np.exp(p_gbm2), s=5, alpha=.5); lim = [5, 800]
ax[0].plot(lim, lim, "k--", lw=.8); ax[0].set_xscale("log"); ax[0].set_yscale("log"); ax[0].set_xlim(lim); ax[0].set_ylim(lim)
ax[0].set_xlabel("measured site EUI (kBtu/sf)"); ax[0].set_ylabel("predicted (5-fold CV)")
ax[0].set_title(f"(a) Seattle 2016, n={len(e)}: R²={out['seattle_gbm_fuel']['R2']}", fontsize=9)
ax[1].barh(imp.index.str.replace("use_", ""), imp.values, color="#4c72b0"); ax[1].set_xlabel("permutation importance (ΔR²)")
ax[1].set_title("(b) What drives energy intensity", fontsize=9)
fig.tight_layout(); fig.savefig(f"{F}/figK2_seattle.png", dpi=200); plt.close()

# ---------- K3: Melbourne wastewater inflow anomalies (Ch15) ----------
w = pd.read_csv(glob.glob(f"{D}/melbourne_ww/*.csv")[0])
w["t"] = pd.to_datetime(w.recorddate.str[:10]); w = w.set_index("t").sort_index()
q = w["ETP_DailyInfluent_ML"].astype(float).asfreq("D")
out["mel_nonpositive"] = int((q <= 0).sum()); q = q.where(q > 0)
base = q.rolling(91, center=True, min_periods=30).median()
r = q - base; mad = (r - r.rolling(91, center=True, min_periods=30).median()).abs().rolling(91, center=True, min_periods=30).median()
z = 0.6745*r/mad; flag = z > 3.5
out["mel_days"] = int(q.notna().sum()); out["mel_flagged"] = int(flag.sum())
out["mel_flag_pct"] = round(100*flag.sum()/q.notna().sum(), 1)
yr = q.groupby(q.index.year).median(); out["mel_median_1996_2018"] = (float(yr.loc[1996]), float(yr.loc[2018]))
fig, ax = plt.subplots(2, 1, figsize=(11, 5), sharex=True)
ax[0].plot(q.index, q, lw=.4, c="#888"); ax[0].plot(base.index, base, c="k", lw=1, label="91-day rolling median")
ax[0].scatter(q.index[flag], q[flag], s=6, c="r", label="robust z > 3.5 (wet-weather peaks)")
ax[0].set_ylabel("ETP inflow (ML/day)"); ax[0].legend(fontsize=7)
ax[1].plot(z.index, z, lw=.4); ax[1].axhline(3.5, c="r", ls="--", lw=.8); ax[1].set_ylabel("robust z")
ax[0].set_title("Melbourne Eastern Treatment Plant daily inflow 1995-2019", fontsize=9)
fig.tight_layout(); fig.savefig(f"{F}/figK3_melbourne.png", dpi=200); plt.close()

import json; print(json.dumps(out, indent=1, default=str))
