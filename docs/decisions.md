# Decision log

Append-only. Format: `D-NNN (YYYY-MM-DD) — title` · **Status** · Context · Decision · Why.
Status: `proposed` / `accepted` / `superseded by D-NNN`.

---

### D-001 (2026-11-10) — Which `users/` is the working copy
**Status:** accepted (2026-11-11, Timothy). Root `users/` deleted; the original is still in `krpc7th-sample-source-beta.tar.gz`.
**Context:** Two copies exist. Repo-root `users/` came from `krpc7th-sample-source-beta.tar.gz` (Sept 2026, Japanese comments, no OpenCV in CMake). `krpc7th-simulator/users/` is from the Oct 2026 simulator release, adds `find_package(OpenCV)`, and is what `docker-compose.yaml` mounts (`./users:/users`).
**Decision:** Develop in `krpc7th-simulator/users/catkin_ws/src/krpc_user/`. Treat root `users/` as obsolete (delete once confirmed).
**Why:** It's the one the local sim actually builds and runs, and it's newer.

### D-002 (2026-11-10) — Python version
**Status:** accepted
**Context:** Guidebook p.7 says Python 2.7.17; Programming Manual p.12 says Python 3.6.9; template shebang is `/usr/bin/python3` and launch runs the API node with `python3`.
**Decision:** Target Python 3.6.
**Why:** Manual is the more recent technical doc and matches the shipped template.

### D-003 — Python or C++ for our node
**Status:** proposed: leaning Python, pending team discussion (Timothy, 2026-11-11)
**Context:** Both templates provided. Python: faster iteration, easier OpenCV, and easier for a mostly-beginner team to read and change. C++14: faster on Jetson TX2, less likely to hit timing issues.
**Decision:** _TBD_ — the baseline (D-004) is written in Python because it's quicker to iterate; that doesn't settle this.

### D-004 (2026-11-10) — Baseline visits checkpoints in API order, no optimisation yet
**Status:** accepted
**Context:** We had one speed data point (~0.05 m/s) and no idea how move time scales with distance. Tuning a route planner against a guess would be wasted work.
**Decision:** First program flies the checkpoints in the order the API returns them, goal last, and logs every move (`MOVE_LOG`). Route ordering comes after we have real timings.
**Why:** Gets a reliable end-to-end run and the measurements the planner needs, with the least code.

### D-005 (2026-11-10) — Skip a checkpoint rather than risk missing the goal
**Status:** accepted
**Context:** A full tour doesn't always fit in 5 minutes. Running out of time away from the goal means no mission-finished report in time and no time bonus.
**Decision:** Before each checkpoint, estimate the time to reach it plus the time from it back to the goal. If that doesn't fit (with a 15 s margin), skip it. Failed moves are not retried.
**Why:** Preliminary score is the average of 10 runs, so a dependable finish beats an occasional extra checkpoint. Revisit the margin and speed estimate once measured.
