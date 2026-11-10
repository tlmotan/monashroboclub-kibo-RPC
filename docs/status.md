# Status

_Update at the end of every work session. Newest at top of the log._

## Now
- Phase: **setup** — docs drafted, no custom code yet.
- Submission deadline: **2027-01-20 23:59 JST** (~10 weeks from 2026-11-10).
- Best web-sim score: _none yet_

## Next up
0. Check MYSA portal / ask `krpc@mysa.gov.my` for any Malaysia-specific judging criteria or dates.
1. Confirm D-001 (working `users/` copy) and remove the stale one.
2. Build local sim (`bash ./build.sh --arm64`) and run the stock template once; record results here.
3. Run the stock template on the web sim (Easy) to confirm the upload pipeline works; note ticket count before/after (checks `web-sim.md` assumption #2).
4. Decide D-003 (Python vs C++).
5. Implement: visit **all** checkpoints in given order → goal → finish (baseline score).
6. Measure move times / settling → fill gaps in `field.md`.

## Known issues
- _none yet_

## Score history
Full run log lives in [`sim-log.md`](sim-log.md). Best so far: _none yet_.

## Session log
- **2026-11-10** — Distilled rulebook/manual/guidebook into `docs/`, wrote `CLAUDE.md`, added `.gitignore`.
