---
name: sim-run
description: Run the Kibo-RPC local simulator (or analyse runs already made), summarise the score, diagnose known failure patterns, and log the result in docs/sim-log.md. Use when asked to run a sim, test a change in the simulator, check/compare the last run, or "why did the run fail".
---

# /sim-run: run the local sim, read the result, log it

Argument (optional): how many runs (default 1), or `analyse <run-folder>` / `analyse all` to skip running.

## Steps

1. **Preflight first.** Run `/preflight` (or `python3 .claude/skills/preflight/scripts/preflight.py`). If it fails, stop and fix. Don't spend 10 minutes on a sim that is broken before it starts.
2. **Run the sim in the background** (a run takes ~5–11 min; the watchdog ends it at 600 s after "Go"):
   ```bash
   cd krpc7th-simulator && caffeinate -i perl -e 'alarm 900; exec @ARGV' bash ./simulation.sh > /dev/null 2>&1; echo "EXIT=$?"
   ```
   Use `run_in_background` and wait for the notification. Don't poll. Run sims one at a time: they share Docker and `share/logs/latest`.
   If Docker isn't running or the image is missing, see `docs/sim-troubleshooting.md`. If `build.sh` is needed, use `--arm64`.
3. **Analyse:**
   ```bash
   python3 .claude/skills/sim-run/scripts/analyze_run.py          # newest run
   python3 .claude/skills/sim-run/scripts/analyze_run.py --all    # one line per run, for comparing
   ```
   Exit 0 = scored normally, 1 = a known (or UNKNOWN) problem, 2 = the script itself broke.
4. **If the diagnosis is UNKNOWN or the script crashed**, investigate the run folder (`game.log`, `user_program_output.log`, `result.json`). Then **add a new entry to `SIGNATURES`** in `analyze_run.py` (or fix the parser) so it's recognised next time. Re-run the script to confirm.
5. **Log it.** Add the suggested row to the top of the table in `docs/sim-log.md`. Fill in Who (`tlmotan (via Claude)` unless someone else ran it), the Commit (include "+ uncommitted" if the script says so) and a one-sentence Notes. Log notable runs: a new best, a failure, or a run that tests a change. You don't have to log every repeat.
6. **Report to the user** in plain words: score, checkpoints passed and at what level, goal Y/N, time spare, and the diagnosis. Compare with the previous runs (`--all`) when testing a change. Remember the preliminary round averages 10 runs, so one failed run in N costs about 1/N of the score.
7. **Self-improve:** follow `.claude/skills/MAINTENANCE.md`. If anyone corrected you during this run, add it to the **Mistakes log** below and fix the step.

## Never
- Never touch files outside `krpc7th-simulator/users/catkin_ws/src/krpc_user/` to "fix" a run (CLAUDE.md hard rules). If the sim edits `rviz/urdf.rviz` itself, restore it with `git checkout -- krpc7th-simulator/rviz/urdf.rviz`.
- Never upload to the web sim. That's `/pack-web` and Timothy.

## Mistakes log
Corrections from Timothy or teammates. Format and rules: `.claude/skills/MAINTENANCE.md` section 1.

_No entries yet._

## Lessons learned
- 2026-11-12: `share/logs/latest/` has no `result.json`. The real result is in the timestamped folder that `latest/link_origin` points to. The script handles this.
- 2026-11-12: A run with no `result.json` and "Go" but no `start id` in our log = missed start signal (NO_START_SIGNAL). Seen in 3 of 7 local runs, caused by a 5 s DNS stall; fixed by D-007 (`RES_OPTIONS`). If it shows up again, the fix has stopped working, so investigate.
- 2026-11-12: A run where the Mac slept was invalid (NAV_LOST). Step 2 now wraps the sim in `caffeinate -i`.
- 2026-11-13: A Traceback printed *after* "finish processing" is rospy closing its connections during shutdown, not a crash. PYTHON_CRASH now only looks before that line.
- Checkpoint counts include the goal point (e.g. "7 / 8"), matching the existing sim-log rows.

## Changelog
- 2026-11-13: Added NAV_LOST signature and `caffeinate -i` in step 2 (from the 12 Nov runs in sim-log); clear error when the logs folder is missing.
- 2026-11-13: Fixed PYTHON_CRASH false positive on run 20261112093454 (shutdown-time rospy traceback).
- 2026-11-12: Created. Signatures: NO_START_SIGNAL, PYTHON_CRASH, NEVER_REACHED_GO, NO_MISSION_FINISHED, ILLEGAL, GOAL_FAILED, OVER_TIME.
