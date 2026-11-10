# Field: coordinates, frames, hardware geometry

## Frames
- **`iss_body`** — world frame used for `MOVE_TO_ABSOLUTE_TARGET`. Origin = docking station. [Rulebook p.8, Manual p.62]
- **`body`** — IB2 vehicle frame: +X forward (camera direction), +Y left, +Z up. Used for `MOVE_TO_RELATIVE_TARGET` and `/ctl/wrench`. [Manual p.45, p.63]
- **OpenCV camera frame** — +X image right, +Y image down, +Z out of lens. ArUco `rvec/tvec` = marker → camera. Must convert to `body`/`iss_body` yourself. [Manual p.45]
- Quaternions in this doc and the API JSON are **[x, y, z, w]**.

## Camera mounting [Manual p.45–46]
Main camera on IB2's front, optical axis = body +X. Offset from body origin: **x = 0.14 m, y = 0, z = 0**.
Intrinsics: read `/camera_main/camera_info` (`K` 3×3, `D` distortion). Rescale fx, fy, cx, cy if you resize.

## AR markers [Rulebook p.8, Manual p.44]
Dictionary **ArUco 4x4** (exact variant e.g. `DICT_4X4_50` — **unverified, test**), IDs **1–12**, side **0.02 m**.

| ID | Target | x | y | z | qx | qy | qz | qw |
|---|---|---|---|---|---|---|---|---|
| 1 | SAIBO | 1.451 | -1.001 | 0.681 | -0.707 | 0 | 0 | 0.707 |
| 2 | RYUTAI | 2.973 | -1.001 | 0.718 | -0.707 | 0 | 0 | 0.707 |
| 3 | MSPR_1 | 3.313 | -1.001 | 0.523 | -0.707 | 0 | 0 | 0.707 |
| 4 | MSPR_2 | 4.181 | -1.001 | 0.523 | -0.707 | 0 | 0 | 0.707 |
| 5 | RMS_Console | 5.754 | -1.001 | 0.838 | -0.707 | 0 | 0 | 0.707 |
| 6 | EPS1 | 1.895 | -0.282 | -0.208 | 0 | 0 | 0.707 | -0.707 |
| 7 | MELFI1 | 1.451 | -1.001 | 0.372 | -0.707 | 0 | 0 | 0.707 |
| 8 | EPS2_2 | 4.779 | 0.112 | 1.884 | -0.707 | 0.707 | 0 | 0 |
| 9 | EPS2_1 | 2.066 | 1.046 | -0.014 | 0 | 0.707 | -0.707 | 0 |
| 10 | ECLSS_TCS2 | 5.851 | 0.010 | 1.884 | -0.707 | 0.707 | 0 | 0 |
| 11 | Airlock | 7.195 | 0.363 | 1.230 | 0.5 | 0.5 | -0.5 | -0.5 |
| 12 | Bay0_Closeout_Panel | 0.000 | -0.059 | -0.102 | -0.5 | 0.5 | -0.5 | 0.5 |

Note: markers 1–5 and 7 are all on the y = -1.001 wall; 8 and 10 on the z = 1.884 ceiling.

## Start
DockingStation: position (0.200, 0, 0), attitude (0, 0, 0, 1). [Rulebook p.8]

## GoalPoint
Given in `get_checkpoints` response as `goalpoint_id` (sample: 12 → Bay0 panel, next to the dock). **Confirm per run; it's a checkpoint ID.**

## Observed in local runs
**Run 2026-11-10, normal level, seed 1418795058** (8 checkpoints):
| CP id | position (x, y, z) | marker_pose quaternion (from API) |
|---|---|---|
| 1 | 1.453, -0.526, 0.523 | -0.5, 0.5, 0.5, 0.5 |
| 3 | 3.345, -0.510, 0.610 | -0.5, 0.5, 0.5, 0.5 |
| 4 | 4.094, -0.512, 0.581 | -0.5, 0.5, 0.5, 0.5 |
| 6 | 1.868, -0.245, 0.290 | 0, 0, 0.707, 0.707 |
| 8 | 4.827, 0.161, 1.388 | 0, 1, 0, 0 |
| 10 | 5.927, -0.031, 1.391 | 0, 1, 0, 0 |
| 11 | 6.728, 0.194, 1.288 | -0.5, 0.5, 0.5, -0.5 |
| 12 (goal) | 0.483, -0.092, 0.025 | -0.5, 0.5, -0.5, 0.5 |

Findings:
- **Checkpoint IDs = AR marker IDs**, a subset of 1–12 per run. The goal was also a checkpoint (id 12, next to the dock).
- **Marker quaternions from the API differ from the Rulebook table** (e.g. marker 1: rulebook `[-0.707,0,0,0.707]`, API `[-0.5,0.5,0.5,0.5]`). Positions match. **Trust the API response**; the two likely use different marker-axis conventions.
- Moving to the given `position` + `attitude.quaternion` with `MOVE_TO_ABSOLUTE_TARGET` alone scored **Lv3** on CP1, with no vision used.
- **Speed (one data point):** dock → CP1, ~1.45 m, took ~30 s including accel/settle. That's ≈0.05 m/s effective. A naive route through all 8 CPs and back to the goal is ~14 m, so **time is tight**. Route order and the 5-min budget really matter.

## Things we still need to measure (fill in as found)
- Flyable volume / keep-out zones of Kibo: _unknown; `share/logs/latest/iss.urdf` may help_
- IB2 body radius: _unknown_
- Move time vs distance over several moves (is it ~linear? max speed?): _measure_
- Settling time after a move before the 1 s hold is stable: _measure_
