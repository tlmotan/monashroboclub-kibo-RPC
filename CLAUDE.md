# Monash Robo Club — 7th Kibo-RPC

Team Monash RoboClub's entry for JAXA's 7th Kibo Robot Programming Challenge — **Malaysia national
level (POC: MYSA), Advanced Category, Regular Course**. We write a ROS 1 node that flies
**Int-Ball2 (IB2)** around the Kibo module: undock → visit 6–12 CheckPoints (AR-marker-relative)
→ reach the GoalPoint → report mission finished, all within **5 minutes**.

## Read these before you start (don't re-read the PDFs unless a doc says "unverified")
| When you are… | Read |
|---|---|
| Deciding strategy / anything about scoring, timing, rules | `docs/rules.md` |
| Writing movement, poses, frames, marker coordinates | `docs/field.md` |
| Calling any ROS topic/service/action | `docs/api.md` |
| Changing program structure | `docs/architecture.md` |
| Starting a session / picking up work | `docs/status.md` |
| Checking which phase we're in, milestones, what comes later | `docs/roadmap.md` |
| About to make or revisit a design choice | `docs/decisions.md` |
| Simulator/Docker misbehaving | `docs/sim-troubleshooting.md` |
| Assigning work / who owns a module | `docs/team.md` |
| Helping a teammate install the simulator | `docs/setup.md` |
| Using the web simulator, tickets, submitting | `docs/web-sim.md` |
| Recording or comparing run results | `docs/sim-log.md` |

Team of 5, mostly ROS/robotics beginners, aiming to **win Malaysia and reach the ISS final**. Timothy (`tlmotan`) is lead; Claude writes much of the code, teammates review, run sims and own small pieces. Most don't use Claude Code, so `README.md`, `docs/` and every PR description are written for beginners: plain and readable.

Workflow: one branch + PR per change (never commit to `main`). Claude never logs in to the web sim: prepare the `.tar.gz`, state level + memo, and Timothy uploads. Spend web-sim tickets sparingly.

Source PDFs live in the repo root (committed; extract text with `pymupdf` if a doc fact needs re-checking). Extracted page numbers are cited in the docs as `[Rulebook p.N]`, `[Manual p.N]`.

## Repo map
- `krpc7th-simulator/` — official simulator bundle (Oct 2026). **Only edit inside `users/catkin_ws/src/krpc_user/`.**
  - `users/catkin_ws/src/krpc_user/scripts/user_template.py` — Python entry point (default)
  - `users/catkin_ws/src/krpc_user/src/user_template_node.cpp` — C++14 alternative
  - `users/catkin_ws/src/krpc_user/launch/krpc_user.launch` — picks which one runs (`team_user_script`)
  - `share/logs/latest/` — results of last local run (`cheat_sheet.json`, judge logs, rosbag)
- `docs/` — distilled project knowledge (this file's index above).

## Commands (run from `krpc7th-simulator/`)
```bash
bash ./build.sh --arm64      # first time / after image update (we're on Apple Silicon → --arm64)
bash ./simulation.sh         # run one local sim; view at http://localhost ; Ctrl+C to stop
bash ./replay.sh [speed] [start_time]   # replay last rosbag
cd users && bash ./packing.sh <name>    # → users/<name>.tar.gz for the Web simulator
```
Web simulator: https://jaxa.krpc.jp/user-auth (SIMULATION tab → upload → START SIMULATION). The web sim is ARM64 and is the source of truth.

## Environment constraints (target = IB2 / Jetson TX2, ARM64)
- ROS 1 Melodic, Python 3.6.9 (template shebang `#!/usr/bin/python3`), GCC 7.5 / C++14, OpenCV 3.3.1 (`cv2.aruco`).
- No f-string-only features beyond 3.6; no `dataclasses`, no walrus, no `from __future__ import annotations`.
- Don't add pip dependencies — nothing beyond what the image provides.

## Hard rules (breaking these = FAILED run or disqualification)
- Never touch `krpc_api_server/`, `krpc_ib2_msgs/`, `bootstrap/`, `packing.sh`, `docker/`, `rootfs/`, `rviz/`.
- Never rename the package, `CMakeLists.txt`/`package.xml` package names, or the launch file.
- Never remove: `/ib2_user/start` subscriber, `/ib2_user/stop` service, `rospy.set_param('/ib2_user/ready', True)`.
- Every wait (`wait_for_service`, `wait_for_server`, `wait_for_result`, loops) needs a finite timeout. Every retry needs a cap.
- `/ib2_user/stop` handler must cancel all running actions, then respond.

## Working conventions
- Update `docs/status.md` at the end of every work session (what changed, last sim score, next steps).
- Log a one-paragraph entry in `docs/decisions.md` for any non-obvious choice.
- If a doc fact turns out wrong, fix the doc in the same change.
- Use `rospy.loginfo/logwarn/logerr` — it's the only log we get back from the web sim.
