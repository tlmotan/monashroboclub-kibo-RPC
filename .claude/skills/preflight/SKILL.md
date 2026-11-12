---
name: preflight
description: Check the Kibo-RPC user code against the CLAUDE.md hard rules (Python 3.6 syntax, mandatory start/stop/ready lines, timeouts on every wait, stop handler cancels actions, D-007 resolver fix, no edits outside krpc_user/). Use before any sim run, before packing for the web sim, before opening a PR that touches the node, or when asked "is this safe to submit".
---

# /preflight: catch disqualifying mistakes before they cost a run

## Steps

1. Run:
   ```bash
   python3 .claude/skills/preflight/scripts/preflight.py
   ```
   It reads whichever script `launch/krpc_user.launch` runs. Exit 0 = OK, 1 = at least one FAIL, 2 = the checker itself broke.
2. **Any FAIL → fix the code, re-run, repeat until OK.** FAILs are things that make the run FAILED or get us disqualified (CLAUDE.md "Hard rules").
3. **WARNs → look at each one and decide.** For example a `while True` loop that does have a deadline inside is fine. If a WARN is a false alarm that will keep coming back, teach the script, e.g. add a real ROS package to `KNOWN_IMPORTS`. Don't ignore it silently.
4. If the launch file runs the C++ node, the script only checks package/path rules. Review the C++ by hand against CLAUDE.md "Hard rules", and note it in the report.
5. Report: OK, or the list of FAILs and how you fixed them.
6. **Self-improve:** follow `.claude/skills/MAINTENANCE.md`. Each time a rule-breaking mistake reaches a sim run or a review without preflight catching it, add a check to `CHECKS` in `preflight.py`. If a person caught it, also add a **Mistakes log** entry.

## What it checks (keep this list in sync with `CHECKS`)
| Level | Check |
|---|---|
| FAIL | Package still named `krpc_user`; launch file present |
| FAIL | Nothing changed in `krpc7th-simulator/` outside `users/catkin_ws/src/krpc_user/` (compared with `origin/main`) |
| FAIL | File parses; no syntax newer than Python 3.6 (walrus, `match`, `/` params, f-string `=`, `dataclasses`, `from __future__ import annotations`) |
| FAIL | `/ib2_user/start` subscriber, `/ib2_user/stop` service, `set_param('/ib2_user/ready', True)` present |
| FAIL | `RES_OPTIONS` set before `import rospy` (D-007, prevents missed start signal) |
| FAIL | Every `wait_for_service/server/result/message` has a timeout |
| FAIL | Stop handler calls `cancel_goal()` and returns a response |
| WARN | `while True` loops (need a deadline + retry cap) |
| WARN | Imports not known to exist on the target image |
| WARN | `print()` instead of `rospy.log*` (web sim only returns rospy logs) |

## Never
- Never delete or loosen a FAIL check without Timothy's OK, even to make a run go through.
- Never "fix" a FAIL by editing protected simulator files. The only exception is restoring them with `git checkout -- <file>`.

## Mistakes log
Corrections from Timothy or teammates. Format and rules: `.claude/skills/MAINTENANCE.md` section 1.

_No entries yet._

## Lessons learned
- 2026-11-12: Local `main` was stale (behind `origin/main`), which made every simulator file look "changed". The script compares with `origin/main` first for this reason.
- The simulator itself rewrites `krpc7th-simulator/rviz/urdf.rviz` during runs. Restore it, don't commit it.

## Changelog
- 2026-11-12: Created with 10 checks, including the D-007 resolver check. Tested on the current node (all pass) and on a deliberately broken sample (every FAIL fired).
