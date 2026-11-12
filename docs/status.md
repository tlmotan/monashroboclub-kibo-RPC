# Status

_Update at the end of every work session. Newest at top of the log._

## Now
- Phase: **Phase 1 of the [roadmap](roadmap.md): prove it on the real simulator** (to 23 Nov). Works locally with route planning — passes 7–8 of 8 checkpoints on Normal, ends at the goal, finishes inside 5 min. Not yet run on the web sim.
- Submission deadline: **2027-01-20 23:59 JST** (~10 weeks from 2026-11-10).
- Best web-sim score: _none yet_

## Next up
0. Check MYSA portal / ask `krpc@mysa.gov.my` for any Malaysia-specific judging criteria or dates.
1. ~~Confirm D-001 and remove the stale `users/`~~ ✅ 2026-11-11.
1b. Each teammate: follow [`setup.md`](setup.md), get one local run, log it in `sim-log.md`. Fill in GitHub usernames + workstreams in `team.md`.
1c. Team discussion to settle D-003 (Python vs C++); currently leaning Python.
2. ~~Build local sim and run the stock template once~~ ✅ 2026-11-10: works on Mac; CP1 passed at Lv3, goal not reached (see `sim-log.md`).
3. Run the **baseline** on the web sim (Easy) to confirm the upload pipeline works and get a first real score; note ticket count before/after (checks `web-sim.md` assumption #2).
4. Decide D-003 (Python vs C++).
5. ~~Implement: visit all checkpoints in given order → goal → finish~~ ✅ 2026-11-10 (D-004, D-005).
6. ~~Measure move times / settling~~ ✅ 2026-11-10: ≈ 20 s + 8 s per metre per move (see `field.md`).
7. ~~Route ordering~~ ✅ 2026-11-12 (D-006): 7/8 or 8/8 checkpoints on Normal, goal reached every valid run.
7b. **Tighten the time estimate.** Runs that left one checkpoint out still finished with 60–100 s spare. Good first task for the movement + route pair: tune `MOVE_OVERHEAD_SEC` / `EST_SPEED_MPS` / `SAFETY_MARGIN_SEC` and compare runs.
7c. Watch for "Navigation message timed out" runs (seen once, cause unknown; see `sim-troubleshooting.md`).
8. Measure rotation time separately and try a shorter hold, to trim the ~20 s fixed cost per move.

## Known issues
- The far-end checkpoint (CP11) is often left out on Normal even though there turns out to be time for it: the time estimate is cautious. Fix = item 7b.
- One local run lost all navigation data 14 s in and scored 0 (simulator-side, cause unknown). Item 7c.
- Local runs are unreliable if the Mac sleeps mid-run; use `caffeinate` (see `sim-troubleshooting.md`).

## Score history
Full run log lives in [`sim-log.md`](sim-log.md). Best so far: _none yet_.

## Session log
- **2026-11-13** — Opened the route-planner PR (the code and docs were committed on 12 Nov; the last run on the final code, `b9ee651`, passed 7/8 at Lv3 with 63 s spare). Separately: `main` is now protected (every PR needs one teammate's approval; Timothy can bypass), and Claude skills (`/preflight`, `/sim-run`, `/pack-web`, `/wrap-session`, `/meeting-update`) are in PR #4. No new sim runs. Next: first web-sim upload (item 3), then tighten the time estimate (7b).
- **2026-11-12** — Route planner added (D-006): on Normal it now passes 7/8 or 8/8 checkpoints with the goal reached, finishing at 237–266 s (5 valid runs; first 8/8 all-Lv3 run). Found and fixed two real problems along the way: the node could miss the simulator's start signal because of a Docker name-lookup stall (D-007), and it sometimes reported a checkpoint before it had finished turning (D-008). One unexplained simulator-side navigation failure logged. Still not run on the web sim.
- **2026-11-12** — Added [`roadmap.md`](roadmap.md): the end-to-end plan in six phases, replacing the week table in the timeline PDF (milestones and dates unchanged). No code changes.
- **2026-11-11** — Recorded team context in `team.md` (Timothy = lead, beginner team aiming for the ISS final, ways to help); accepted D-001 and deleted root `users/`; D-003 leaning Python pending team chat; added `setup.md` for Windows (WSL2) and Mac.
- **2026-11-10** — Wrote the baseline in `user_template.py` (commit 25835fe) and ran it twice locally on Normal: 7/8 and 6/8 checkpoints, all Lv3, goal reached both times, finished at 230 s and 198 s. Measured 13 moves: ≈ 20 s fixed + 8 s per metre, landing within 1.4 cm. Next: route ordering, then first web-sim upload.
- **2026-11-10** — Built local sim on Mac (arm64), ran stock template: 1/8 CPs (Lv3), 30 s, no goal. Key finding: just flying to the given pose earns Lv3; travel is slow (~0.05 m/s), so route/time budget is the main challenge. Details in `field.md`.
- **2026-11-10** — Distilled rulebook/manual/guidebook into `docs/`, wrote `CLAUDE.md`, added `.gitignore`.
