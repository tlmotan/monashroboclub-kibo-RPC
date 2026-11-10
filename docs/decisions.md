# Decision log

Append-only. Format: `D-NNN (YYYY-MM-DD) — title` · **Status** · Context · Decision · Why.
Status: `proposed` / `accepted` / `superseded by D-NNN`.

---

### D-001 (2026-11-10) — Which `users/` is the working copy
**Status:** proposed — team to confirm
**Context:** Two copies exist. Repo-root `users/` came from `krpc7th-sample-source-beta.tar.gz` (Sept 2026, Japanese comments, no OpenCV in CMake). `krpc7th-simulator/users/` is from the Oct 2026 simulator release, adds `find_package(OpenCV)`, and is what `docker-compose.yaml` mounts (`./users:/users`).
**Decision:** Develop in `krpc7th-simulator/users/catkin_ws/src/krpc_user/`. Treat root `users/` as obsolete (delete once confirmed).
**Why:** It's the one the local sim actually builds and runs, and it's newer.

### D-002 (2026-11-10) — Python version
**Status:** accepted
**Context:** Guidebook p.7 says Python 2.7.17; Programming Manual p.12 says Python 3.6.9; template shebang is `/usr/bin/python3` and launch runs the API node with `python3`.
**Decision:** Target Python 3.6.
**Why:** Manual is the more recent technical doc and matches the shipped template.

### D-003 — Python or C++ for our node
**Status:** proposed — undecided
**Context:** Both templates provided. Python: faster iteration, easier OpenCV. C++14: faster on Jetson TX2, less likely to hit timing issues.
**Decision:** _TBD_
