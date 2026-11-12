# Architecture — what our program does

> Status: **baseline (2026-11-10).** One file, no vision, no route optimisation yet. Update this file whenever structure changes.

## Current (baseline: visit every checkpoint, then goal)
`krpc7th-simulator/users/catkin_ws/src/krpc_user/scripts/user_template.py`
```
__init__               set up clients, mandatory /ib2_user/* plumbing, nav subscriber, set ready=True
__callback_start       (on /ib2_user/start) guard → __run_user_flow
__run_user_flow        mission_start → start mission clock → __fly_mission → mission_finished
__fly_mission          get checkpoints → for each (API order, goal last): time check → __visit
  ├─ __fetch_checkpoints   get_checkpoints, up to 3 attempts, parse JSON; gives up cleanly if unusable
  ├─ __visit               __move_to_checkpoint → hold 1.5 s → __notify_checkpoint_passed (max 2 tries)
  └─ __move_to_checkpoint  absolute move with a hard timeout; cancels and confirms stop on timeout
__stop_processing      set stop flag, cancel move + checkpoint actions → respond
```

How it behaves:
- **Order:** the order the API returns, with the GoalPoint checkpoint moved to the end.
- **Time check:** before each checkpoint it estimates "time to get there + time from there to the goal" using `EST_SPEED_MPS`. If that doesn't fit in the time left (minus `SAFETY_MARGIN_SEC`), the checkpoint is skipped. The goal always gets flown last.
- **Failures:** a failed or timed-out move is not retried and not reported; the program moves on. Nothing waits forever.
- **Tunables** are constants at the top of the file (speed estimate, margins, hold time, timeouts).
- **Logs to look for:** `MOVE_LOG` (one per move: distance, duration, final error, result) and `SUMMARY` (passed / skipped lists).

## Planned shape (draft — revise as we build)
```
main node
 ├─ MissionClient     wraps mission_start / get_checkpoints / checkpoint_passed / mission_finished
 ├─ Motion            move_abs / move_rel / stop, with timeouts + status polling
 ├─ State             latest Navigation pose (+timestamp), CameraInfo, latest image
 ├─ Vision            ArUco detect + pose, centering angle, roll error
 ├─ Planner           order checkpoints (TSP-ish over ≤12 nodes, start=dock, end=goal)
 ├─ Approach          per checkpoint: coarse move → visual fine-align → hold 1 s → report
 └─ Timekeeper        mission clock; decides when to skip / head to goal
```

### Main loop (intended)
1. Ready → wait start → `mission_start`, record t0.
2. `get_checkpoints` (retry ≤N) → parse → plan order.
3. For each checkpoint while time budget allows:
   coarse move to `position` + `attitude.quaternion` → settle → (optional) visual correction → check all 3 bands locally → `checkpoint_passed`.
4. Reserve time to reach goal and call `mission_finished` before 5:00 regardless.

## Data flow
`get_checkpoints JSON` → Planner → target poses → Motion → `/ctl/command`
`/sensor_fusion/navigation` + `/camera_main/*` → State/Vision → Approach decides "stable & aligned" → MissionClient.

## Open questions
- Python vs C++ (see decisions.md)
- Is visual correction needed, or is nav pose accurate enough for Lv3?
- Can we self-evaluate centering/roll from nav pose alone (geometry) instead of vision?
