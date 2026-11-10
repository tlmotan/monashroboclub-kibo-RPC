# Simulation run log

One row per **web** run (they cost tickets). Notable local runs are welcome too; mark them `local`.
Newest at the top. Put the same commit + name in the web sim's **Memo** field.

| Date | Who | Sim (web/local) | Version | Level | Commit | Final score | CPs passed | Goal | Mission time | Time bonus | Tickets after | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-11-10 | tlmotan (via Claude) | local (Mac arm64) | 1.1 bundle | normal (seed 1804124538) | 25835fe (baseline) | n/a (local) | 6 / 8, all **Lv3** (1, 3, 4, 6, 7, 12) | ✓ | 198.0 s | n/a | n/a | CPs 8 and 11 skipped by the time check (8 missed by 3 s). Finished with 102 s spare, so the check is too cautious for API order; route ordering should recover these. |
| 2026-11-10 | tlmotan (via Claude) | local (Mac arm64) | 1.1 bundle | normal (seed 3065868304) | 25835fe but with the old 0.05 m/s time estimate | n/a (local) | 7 / 8, all **Lv3** (1, 2, 3, 4, 8, 9, 12) | ✓ | 230.1 s | n/a | n/a | First baseline run. CP10 skipped for time. Every move ended within 1.4 cm of target. |
| 2026-11-10 | tlmotan (via Claude) | local (Mac arm64) | 1.1 bundle | normal (seed 1418795058) | 0276f26 (stock template) | n/a (local result.json has no score) | 1 / 8 (CP1 at **Lv3**) | ✗ ("checkpoint outside threshold") | 30.3 s | n/a | n/a | Baseline. Template flies to first CP only, then reports finish. Dock→CP1 (~1.45 m) took ~30 s. |
