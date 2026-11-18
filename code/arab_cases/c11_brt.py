# Amman BRT: published cost figures and a schedule-risk Monte Carlo for a hypothetical 12 km extension
import numpy as np
p1_km, p1_cost = 27.5, 127.4      # first phase, million JD (GAM figures via Jordan Times)
az_km, az_cost = 20.0, 153.0      # Amman-Zarqa BRT, million JD
print(f"Amman BRT phase 1 : {p1_cost/p1_km:.2f} M JD/km")
print(f"Amman-Zarqa BRT   : {az_cost/az_km:.2f} M JD/km")
print(f"works started 2010, first line in service 2021 -> {2021-2010} years from start to service")
# hypothetical 12 km extension: activity durations (months) as triangular (min, mode, max)
acts = {"design & tender": (6, 9, 15), "utilities relocation": (6, 10, 20), "civil works": (14, 18, 30),
        "stations & systems": (6, 8, 12), "trial operation": (2, 3, 5)}
rng = np.random.default_rng(3); N = 100_000
D = sum(rng.triangular(*v, N) for v in acts.values())
halt = rng.random(N) < 0.20                       # funding interruption risk (assumption)
D = D + halt * rng.uniform(6, 24, N)
plan = sum(v[1] for v in acts.values())
print(f"deterministic plan (modes): {plan} months")
print(f"P50 = {np.percentile(D,50):.0f}, P80 = {np.percentile(D,80):.0f}, P95 = {np.percentile(D,95):.0f} months")
print(f"P(finish within plan) = {np.mean(D <= plan):.1%}")
cost = 12 * rng.uniform(p1_cost/p1_km, az_cost/az_km, N) * (1 + 0.004*np.maximum(D - plan, 0))
print(f"cost: P50 = {np.percentile(cost,50):.0f} M JD, P80 = {np.percentile(cost,80):.0f} M JD")
