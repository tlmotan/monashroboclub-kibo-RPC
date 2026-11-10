# Simulator & environment troubleshooting

Add an entry every time something breaks and you fix it: **Symptom → Cause → Fix**.

## Known from the manual
- **Mac / Apple Silicon:** build with `bash ./build.sh --arm64` (also matches web sim + IB2 architecture). [Manual p.38]
- **x86 builds** behave differently from the ARM64 web sim / Jetson TX2 — always do the final check on the web sim. [Manual p.37]
- **http://localhost won't load:** something else is on port 80 → change the port mapping in `docker-compose.yaml` (local only, don't commit). [Manual p.39]
- **Unstable / crashes:** usually RAM. Needs 8 GB min, 16 GB recommended; give Docker enough memory. [Manual p.10–11]
- **Stale image:** `bash ./build.sh --no-cache`.
- **Web sim run says FAILED:** can't submit that run. Check the downloaded user log; a FINISHED run on the *Preliminary* sim is required to submit. [Rulebook p.16]
- **Only logs available from web sim:** result JSON + our own `rospy.log*` output. Everything else (sensors, topics) → local rosbag only. [Manual p.34]

## Result JSON quick read [Manual p.34–36]
`Illegal` (violation?), `JudgeReport.mission` (start/finish/duration), `.checkpoint_detail[]` (id, success, level, reason), `.goal`, `.events`.

## Team-found issues
- **2026-11-10: Mac (Apple Silicon) works.** `bash ./build.sh --arm64` succeeded (images ~8.8 GB, build took a few minutes on Docker with 8 GB RAM / 10 CPUs), then `bash ./simulation.sh` ran a full mission and exited cleanly.
- **macOS has no `timeout` command.** To cap a run in a script, use `perl -e 'alarm 900; exec @ARGV' bash ./simulation.sh`, then `docker compose down`.
- **Each run writes ~300 MB** (`simulation.bag`) into `share/logs/<timestamp>/`. It's gitignored, but delete old runs to save disk.
- **The local `result.json` has no numeric score**, only per-checkpoint pass/level, goal and timing. Final score / time bonus only show on the web sim.
- Useful local-only files: `share/logs/latest/cheat_sheet.json` (the run's full checkpoint layout + seed + level), `judge_module_logs/judge.log`, `user_programs_logs/`.
