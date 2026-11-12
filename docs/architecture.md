# Architecture — what our program does

> Status: **baseline + route planner (2026-11-12).** One file, no vision. Update this file whenever structure changes.

## Current (plan a route, visit the checkpoints, end at the goal)
`krpc7th-simulator/users/catkin_ws/src/krpc_user/scripts/user_template.py`
```
__init__               set up clients, mandatory /ib2_user/* plumbing, nav subscriber, set ready=True
__callback_start       (on /ib2_user/start) guard → __run_user_flow
__run_user_flow        mission_start → start mission clock → __fly_mission → mission_finished
__fly_mission          get checkpoints → loop: plan_route → __visit first stop → repeat; goal last
  ├─ plan_route            (plain function, no ROS) best visit order for the time left
  ├─ __fetch_checkpoints   get_checkpoints, up to 3 attempts, parse JSON; gives up cleanly if unusable
  ├─ __visit               __move_to_checkpoint (max 3 tries if rejected) → __wait_until_on_target (max 8 s) → hold 1.5 s → __notify_checkpoint_passed (max 2 tries)
  └─ __move_to_checkpoint  absolute move with a hard timeout; cancels and confirms stop on timeout
__stop_processing      set stop flag, cancel move + checkpoint actions → respond
```

How it behaves:
- **Order (route planner, `plan_route`):** the program picks the route itself. It finds the route that visits the **most checkpoints** in the time left and still ends at the goal; if several routes visit the same number, it takes the fastest. It checks every possible combination (there are at most 12 checkpoints, so this takes well under a second).
- **Time estimate:** each leg is costed as `MOVE_OVERHEAD_SEC` + distance / `EST_SPEED_MPS` + `HOLD_SEC`, from the measurements in `field.md`. `SAFETY_MARGIN_SEC` is kept in hand.
- **Re-planning:** after every checkpoint it plans again from where it actually is, with the time actually left. If earlier legs went faster than estimated, a checkpoint that was left out can come back in. Checkpoints that don't fit are skipped; the goal is always flown last.
- **On-target check:** after a move, the program waits (8 s at most) until the navigation data says it is within 3° and 3 cm of the target, then holds 1.5 s, then reports. Look for `SETTLE` in the log.
- **Failures:** a move that runs out of time is not retried. A move the controller rejects (for example "navigation invalid") is retried up to 3 times, 3 s apart. A checkpoint whose move failed is not reported; the program moves on. Nothing waits forever.
- **Start-up:** the first lines of the file set `RES_OPTIONS=single-request` so the node cannot miss the start signal (D-007). Don't remove them.
- **Tunables** are constants at the top of the file (speed estimate, margins, hold time, timeouts).
- **Logs to look for:** `PLAN` (the chosen route and its time estimate), `MOVE_LOG` (one per move: distance, duration, final error, result), `SETTLE` (angle when the move ended and how long we waited) and `SUMMARY` (passed / failed / skipped lists).

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
