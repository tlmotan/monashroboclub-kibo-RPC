# Architecture — what our program does

> Status: **template only.** Nothing custom written yet. Update this file whenever structure changes.

## Current (stock JAXA template)
`krpc7th-simulator/users/catkin_ws/src/krpc_user/scripts/user_template.py`
```
__init__            set up clients, mandatory /ib2_user/* plumbing, set ready=True
__callback_start    (on /ib2_user/start) guard → __run_user_flow
__run_user_flow     mission_start → [USER EDIT AREA] → mission_finished
  └─ USER EDIT AREA currently: first checkpoint only → move → checkpoint_passed
__stop_processing   cancel active move → respond
```

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
