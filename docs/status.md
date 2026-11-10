# Status

_Update at the end of every work session. Newest at top of the log._

## Now
- Phase: **baseline working locally** — visits checkpoints in API order, ends at the goal, finishes inside 5 min. Not yet run on the web sim.
- Submission deadline: **2027-01-20 23:59 JST** (~10 weeks from 2026-11-10).
- Best web-sim score: _none yet_

## Next up
0. Check MYSA portal / ask `krpc@mysa.gov.my` for any Malaysia-specific judging criteria or dates.
1. Confirm D-001 (working `users/` copy) and remove the stale one.
2. ~~Build local sim and run the stock template once~~ ✅ 2026-11-10: works on Mac; CP1 passed at Lv3, goal not reached (see `sim-log.md`).
3. Run the **baseline** on the web sim (Easy) to confirm the upload pipeline works and get a first real score; note ticket count before/after (checks `web-sim.md` assumption #2).
4. Decide D-003 (Python vs C++).
5. ~~Implement: visit all checkpoints in given order → goal → finish~~ ✅ 2026-11-10 (D-004, D-005).
6. ~~Measure move times / settling~~ ✅ 2026-11-10: ≈ 20 s + 8 s per metre per move (see `field.md`).
7. **Route ordering** — pick the visit order that fits the most checkpoints and ends at the goal (≤12 points, so brute force / nearest-neighbour is fine), using the measured move-time rule. This is the biggest score gain available now.
8. Measure rotation time separately and try a shorter hold, to trim the ~20 s fixed cost per move.

## Known issues
- Baseline skips 1–2 of 8 checkpoints on Normal because API order wastes travel and the goal sits next to the dock. Run 2 finished with 102 s unused. Fix = item 7.

## Score history
Full run log lives in [`sim-log.md`](sim-log.md). Best so far: _none yet_.

## Session log
- **2026-11-10** — Wrote the baseline in `user_template.py` (commit 25835fe) and ran it twice locally on Normal: 7/8 and 6/8 checkpoints, all Lv3, goal reached both times, finished at 230 s and 198 s. Measured 13 moves: ≈ 20 s fixed + 8 s per metre, landing within 1.4 cm. Next: route ordering, then first web-sim upload.
- **2026-11-10** — Built local sim on Mac (arm64), ran stock template: 1/8 CPs (Lv3), 30 s, no goal. Key finding: just flying to the given pose earns Lv3; travel is slow (~0.05 m/s), so route/time budget is the main challenge. Details in `field.md`.
- **2026-11-10** — Distilled rulebook/manual/guidebook into `docs/`, wrote `CLAUDE.md`, added `.gitignore`.
