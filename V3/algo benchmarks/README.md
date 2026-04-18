# ⚡ EV Charger Finder — Algorithm Stress Test Benchmarks

> Stress test results for the scheduling and collision-mitigation algorithm powering the EV Charger Finder application.

---

## 📋 Table of Contents

- [Overview](#overview)
- [What Is Being Measured](#what-is-being-measured)
- [Benchmark Results](#benchmark-results)
  - [50 Concurrent Users](#1--50-concurrent-users)
  - [100 Concurrent Users](#2--100-concurrent-users)
  - [250 Concurrent Users](#3--250-concurrent-users)
  - [500 Concurrent Users](#4--500-concurrent-users)
  - [1000 Concurrent Users](#5--1000-concurrent-users)
- [Key Findings](#key-findings)
- [Conclusion](#conclusion)

---

## Overview

This document presents the results of **five benchmark stress tests** conducted on the core algorithm used in the EV Charger Finder simulation. Each test simulates a progressively larger number of concurrent users — from **50 to 1,000** — to evaluate how the algorithm handles load, wait time prediction accuracy, and system collision mitigation at scale.

---

## What Is Being Measured

Each benchmark graph tracks two metrics simultaneously:

| Metric | Axis | Color |
|---|---|---|
| **Predicted Wait Time (Min)** | Left Y-axis | 🔴 Red Line |
| **Mitigated System Collisions** | Right Y-axis | 🔵 Blue Shaded Area |

The X-axis in all graphs represents **Total Simulated Users** added progressively during the test run.

---

## Benchmark Results

### 1 · 50 Concurrent Users

![Algorithm Stress Test: 50 Concurrent Users](https://raw.githubusercontent.com/MayankNarain/ev-charging-station-finder/main/V3/algo%20benchmarks/50.png)

At the smallest load tested, the algorithm reveals an interesting early-sensitivity behavior. Wait time **climbs gradually and steadily** from 0 users up to approximately **39 simulated users**, at which point it abruptly **spikes to ~360 minutes** — the highest predicted wait time recorded across all tests.

This spike represents a **saturation threshold** being hit at a relatively low absolute user count, suggesting the system is most sensitive at this scale where the spike occupies a large proportion of the x-axis range. Immediately after the spike, the algorithm self-corrects and clamps the wait time down to a stable **50-minute ceiling**, holding it there for the remainder of the test.

Mitigated collisions grow linearly and top out at approximately **35** — the lowest absolute collision count across all five scenarios, expected given the small user pool.

---

### 2 · 100 Concurrent Users

![Algorithm Stress Test: 100 Concurrent Users](https://raw.githubusercontent.com/MayankNarain/ev-charging-station-finder/main/V3/algo%20benchmarks/100.png)


With double the load, the saturation spike occurs at approximately the **same absolute user count (~38–40 users)**, not at a proportionally scaled point. This is a **critical finding** — the threshold appears fixed in nature, independent of total concurrent user capacity.

The spike again reaches ~360 minutes before the algorithm resets cleanly to the **50-minute stable floor**. Prior to the spike, wait time remains near zero for longer compared to the 50-user test, and the pre-spike growth curve is steeper and more compressed.

Mitigated collisions scale linearly to approximately **70** at full load — double that of the 50-user test, confirming the collision system is tracking load proportionally.

---

### 3 · 250 Concurrent Users

![Algorithm Stress Test: 250 Concurrent Users](https://raw.githubusercontent.com/MayankNarain/ev-charging-station-finder/main/V3/algo%20benchmarks/250.png)


The 250-user test reinforces the established pattern. The critical spike still occurs around **~38–42 absolute users** — now appearing at roughly the **15–17% mark** of total scale. This confirms the threshold is **algorithmically fixed** and does not scale with total user count.

Post-spike stabilization at **50 minutes** remains consistent. The blue collision shaded area grows more steeply in absolute terms, reaching approximately **180 mitigated collisions** at peak load — indicating the collision-mitigation component continues functioning effectively as the user base grows threefold.

---

### 4 · 500 Concurrent Users

![Algorithm Stress Test: 500 Concurrent Users](https://raw.githubusercontent.com/MayankNarain/ev-charging-station-finder/main/V3/algo%20benchmarks/500.png)


At 500 users, the spike appears very early on the x-axis (around the **~30–35 user mark** visually), and the remainder of the chart is dominated by the flat, stable 50-minute wait line. This demonstrates that the algorithm spends the **vast majority of its operational time in a stable, predictable state** at scale.

Mitigated collisions climb to roughly **360**, maintaining the same linear growth rate observed in smaller tests. This linearity is a strong positive signal — the collision resolution system is not experiencing exponential degradation as concurrency doubles.

---

### 5 · 1000 Concurrent Users

![Algorithm Stress Test: 1000 Concurrent Users](https://raw.githubusercontent.com/MayankNarain/ev-charging-station-finder/main/V3/algo%20benchmarks/1000.png)


The most demanding test confirms the algorithm's scalability under extreme load. The wait time spike — still peaking at ~360 minutes — now appears at **the very beginning of the x-axis**, representing a negligible fraction of total simulation time. Beyond it, predicted wait time holds rock-solid at **50 minutes** across 950+ additional simulated users, demonstrating strong and consistent stability.

Mitigated collisions reach approximately **760–780** at 1,000 users, still following the same linear trajectory observed across all prior tests. No signs of exponential collision growth or system degradation are visible, validating the robustness of the mitigation layer at production-scale loads.

---

## Key Findings

| Finding | Detail |
|---|---|
| 🔺 **Fixed Spike Threshold** | Saturation spike consistently occurs at ~38–42 absolute users regardless of total simulation scale |
| 📈 **Peak Wait Time** | Always spikes to ~360 min before self-correcting — ceiling appears hard-coded or algorithmically bounded |
| ✅ **Stable Wait Floor** | Reliably clamps to 50 min post-spike across all five test scales |
| 📊 **Linear Collision Scaling** | Mitigated collisions grow linearly with user count — no degradation observed up to 1,000 users |
| ⚡ **Scale Stability** | Algorithm is highly stable and predictable at large scales (500–1,000 users) |
| ⚠️ **Early-Load Sensitivity** | The fixed threshold means smaller deployments (50–100 users) experience the spike proportionally earlier and more prominently |

---

## Conclusion

The EV Charger Finder algorithm demonstrates **strong scalability and stability** across all tested load levels. The collision mitigation system performs predictably and linearly, showing no signs of breakdown even at 1,000 concurrent users.

The primary area warranting further investigation is the **fixed saturation threshold** at approximately 38–42 users. Understanding the root cause of this early spike — and whether it can be smoothed or shifted — could meaningfully improve the algorithm's behavior during initial load ramp-up before large-scale stabilization kicks in.

---

> 📁 Benchmark graphs are located in the `/benchmarks` directory of this repository.  
> 🛠️ Tests were conducted using the internal simulation engine of the EV Charger Finder application.
