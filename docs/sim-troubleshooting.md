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
- **2026-11-12: a run sits idle for 10 minutes and there is no `result.json`.**
  - *What happened:* our program never received the start signal, so it never flew. Seen in 3 of 4 local runs on one day (none two days earlier, on a different network).
  - *Cause:* inside the simulator's Docker network, every newly started program has one hostname lookup that stalls for exactly 5 seconds. The simulator sends the start signal only once (`rostopic pub --once /ib2_user/start` in `rootfs/run.sh`) and keeps it available for about 3 seconds. If the stalled lookup is the one for the start signal, we miss it. The stock template has the same weakness. We measured it in a test container: 25 of 25 new processes had a 5 s lookup; with the setting below, 0 of 25.
  - *How to spot it:* the user log has no `start id: 0` line, and `krpc_user-2.log` has no `topic[/ib2_user/start] adding connection`. Other connections in that log show a gap of exactly 5 seconds.
  - *Fix:* `user_template.py` sets `RES_OPTIONS=single-request` before it imports `rospy` (decision D-007). **Keep those lines at the top of the file.** If you write a C++ node, it needs the same setting (for example an `<env>` tag in the launch file).
- **2026-11-12: don't let the laptop sleep during a run.** A run takes about 6 minutes of real time. If the Mac sleeps, the simulator pauses and navigation "times out" when it wakes, so moves get rejected (`result=3`) and the run is worthless. On a Mac, start runs with `caffeinate -i bash ./simulation.sh`. *How to spot it:* large jumps in the wall-clock timestamps in `judge_module_logs/system.log`.
- **2026-11-12: "Navigation message timed out" with no sleep (seen once, cause unknown).** 14 s into the first move, the simulator's navigation data stopped and never came back; every move was rejected with `result=3` (INVALID_NAV) and the run scored 0. This is inside the simulator, not our code. If you see it again, keep that run's folder in `share/logs/` and note it in `sim-log.md` so we can tell how often it happens.
- **A full run with our program now takes 4–4.5 minutes of mission time**, so allow about 7 minutes per local run including start-up.
