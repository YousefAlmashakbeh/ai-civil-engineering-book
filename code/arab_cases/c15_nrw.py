# Jordan non-revenue water: national trajectory + minimum-night-flow leak detection in a district metered area (DMA)
import numpy as np
base, now = 41.0 + 10.7, 41.0            # % in 2022 and 2025 (Ministry of Water and Irrigation)
print(f"NRW 2022 = {base:.1f}%, 2025 = {now:.1f}%, achieved {10.7/3:.2f} points/yr (target 2.0)")
print(f"needed for 25% by 2040: {(now-25)/15:.2f} points/yr")
r = np.log((base-15)/(now-15))/3          # diminishing returns: losses above a 15% floor decay exponentially (assumption)
for y in (2030, 2035, 2040): print(f"  {y}: {15+(now-15)*np.exp(-r*(y-2025)):.1f}% if the same relative effort continues")
# synthetic DMA: 2,000 connections, hourly inflow for 8 weeks, a burst appears on day 37 at 14:00
rng = np.random.default_rng(11); n, days = 2000, 56; h = np.arange(24*days)
dem = n*(1.7 + 12*np.sin(2*np.pi*(h % 24 - 7)/24).clip(0) + 7*np.exp(-((h % 24 - 20)/2.0)**2))/1000   # m3/h
background = 6.0                          # m3/h background leakage
burst = np.where(h >= 24*36 + 14, 4.5, 0)  # m3/h
q = dem + background + burst + rng.normal(0, 0.8, h.size)
mnf = q.reshape(days, 24)[:, 2:5].mean(1)                   # 02:00-04:00 average
legit = n*1.7/1000                                          # legitimate night use, 1.7 L/conn/h (assumption)
print(f"MNF first week = {mnf[:7].mean():.1f} m3/h, legitimate night use = {legit:.1f} m3/h, night leakage = {mnf[:7].mean()-legit:.1f} m3/h")
ref, sd = mnf[:21].mean(), mnf[:21].std(ddof=1); S = 0; k, H = 0.5*sd, 5*sd
for d in range(21, days):
    S = max(0, S + mnf[d] - ref - k)
    if S > H: print(f"CUSUM alarm on day {d+1} (first night with the burst: day 38); estimated new loss = {mnf[d]-ref:.1f} m3/h = {24*(mnf[d]-ref):.0f} m3/day"); break
