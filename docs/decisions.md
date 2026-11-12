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

### D-006 (2026-11-12) — Route planner: exact search, most checkpoints first, re-plan after every stop
**Status:** accepted (supersedes the "API order" part of D-004)
**Context:** Flying in API order wasted travel: the estimated full tour was about 340 s on our three Normal layouts, over the 300 s limit, so 1–2 checkpoints were skipped each run. With at most 12 checkpoints there are few enough combinations to check them all.
**Decision:** `plan_route` in `user_template.py` checks every combination (Held-Karp dynamic programming) and returns the route that visits the most checkpoints within the time left and ends at the goal, fastest route as tie-break. It re-plans after every checkpoint using the real position and clock.
**Why:** Exact beats a nearest-neighbour guess at no real cost (planning takes a fraction of a second). "Most checkpoints, then fastest" matches the scoring as far as we know it: the goal bonus needs every checkpoint, and the time bonus rewards finishing early. Re-planning keeps us safe when a leg runs slow and uses the spare time when legs run fast. It treats every checkpoint as equally valuable and ignores turning time; revisit both once we have web-sim scores.

### D-007 (2026-11-12) — Set `RES_OPTIONS=single-request` at the top of the node
**Status:** accepted
**Context:** Three local runs did nothing at all because our node missed the simulator's one-shot start signal. The cause is a 5-second hostname-lookup stall that every new process hits once inside the simulator's Docker network (measured; see `sim-troubleshooting.md`). In the preliminary round the score is the average of 10 runs, so each silent run would cost about 10% of our score. We don't know whether the web simulator has the same stall.
**Decision:** The first lines of `user_template.py` set the environment variable `RES_OPTIONS=single-request` before `rospy` is imported. This is a standard Linux resolver option that sends the IPv4 and IPv6 lookups one after the other instead of together.
**Why:** It removed the stall completely in testing (0 of 25 processes, against 25 of 25 without it), it is two lines, and it changes nothing about how the program flies. A first attempt, waiting for connections before setting `ready`, did not help and was removed: the stall happens later, when connecting to the start signal itself. The fix lives in our own file because we must not edit the simulator's Docker or launch scripts.

### D-008 (2026-11-12) — Wait until on target before reporting; retry a rejected move
**Status:** accepted
**Context:** Two problems showed up while testing the route planner. (1) One run scored Lv1 and Lv2 on two checkpoints although the position was 1 cm off: the move had reported success while IB2 was still turning. (2) In one run the controller rejected a move with "navigation invalid", and the program then dropped every remaining checkpoint within a second.
**Decision:** (1) After each move, wait until navigation shows we are within 3° and 3 cm of the target, for at most 8 s, then do the 1.5 s hold and report. (2) Retry a rejected move up to 3 times, 3 s apart, before giving up on that checkpoint. Moves that time out are still not retried.
**Why:** (1) is confirmed: the next run caught a move that ended 14° off, waited 3.6 s and scored Lv3. (2) is a safety net we have not seen succeed yet: in the one real case the simulator's navigation data never came back, so nothing could have saved that run. It costs at most 6 s per checkpoint and stops a brief glitch from ending the mission.
