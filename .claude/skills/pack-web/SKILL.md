---
name: pack-web
description: Prepare a Kibo-RPC web-simulator submission — preflight, make the .tar.gz with packing.sh, and hand Timothy the file, the Simulator Level and the Memo text, plus a pending sim-log row. Use when asked to "pack", "prepare an upload", "get it ready for the web sim", or before spending a web-sim ticket. Never uploads or logs in.
---

# /pack-web: get a build ready for Timothy to upload

Argument (optional): a short label for this build (e.g. `route-planner`), and the level if already decided.

## Steps

1. **Is a ticket worth it?** Web runs are for confirming real improvements (`docs/web-sim.md`, team rules). If this build hasn't beaten the last one locally (`/sim-run`, `analyze_run.py --all`), say so and ask before going on.
2. **Preflight:** `python3 .claude/skills/preflight/scripts/preflight.py` must say OK.
3. **The code must be committed and pushed**, because the Memo names a commit and teammates must be able to see exactly what ran. Check that `git status --short krpc7th-simulator/users/catkin_ws/src/krpc_user` is empty. If not, commit on the current branch (never `main`) and push first.
4. **Pack** (name = short commit + label, letters/digits/dashes only):
   ```bash
   SHA=$(git rev-parse --short HEAD); NAME="${SHA}-<label>"
   cd krpc7th-simulator/users && bash ./packing.sh "$NAME" > /dev/null
   mkdir -p ../share/uploads && mv "$NAME.tar.gz" ../share/uploads/
   ```
   `share/` is git-ignored, so the tarball never gets committed by accident.
5. **Check the tarball**:
   ```bash
   tar -tzf krpc7th-simulator/share/uploads/$NAME.tar.gz | grep -E 'krpc_user/(scripts|launch)/|package.xml$' | head
   ```
   It must contain `catkin_ws/src/krpc_user/scripts/<the launched script>` and the launch file. Also check the size: a few hundred KB at most. If it's MB, something like logs or build output got in, so find it and fix it.
6. **Hand over to Timothy** in one block he can copy from:
   - File: full path to the `.tar.gz`
   - Simulator Version: `1.1` (or whatever `docs/web-sim.md` says is current)
   - Simulator Level: the one asked for, else suggest one with a reason (Easy for a first pipeline check, Normal to compare with local runs)
   - Memo: `<sha> <who>: <label>` (format from `docs/web-sim.md`)
   - Ask him to note the ticket count before and after, and paste back the result JSON or the VIEW RESULT numbers.
7. **Add a pending row** to the top of `docs/sim-log.md`: `web`, the level, the commit and the label, with score columns `pending`. When the results come back, fill them in. Use `analyze_run.py` if he drops the result JSON into a run-style folder; otherwise fill them in by hand.
8. **Self-improve:** follow `.claude/skills/MAINTENANCE.md`. Web-sim facts we learn (ticket rules, level meaning, version changes) go in `docs/web-sim.md`, not here.

## Never
- Never log in to jaxa.krpc.jp, upload, start or terminate a simulation. Timothy does that.
- Never pack uncommitted code, and never commit the `.tar.gz`.
- Never edit `packing.sh`.

## Mistakes log
Corrections from Timothy or teammates. Format and rules: `.claude/skills/MAINTENANCE.md` section 1.

_No entries yet._

## Lessons learned
- `packing.sh` is just `tar -zcvf $1.tar.gz catkin_ws/src` and must be run from `krpc7th-simulator/users/`. It packs every package in `src/`, including the API server and msgs. That's expected.

## Changelog
- 2026-11-12: Created. Not yet used for a real upload, so the first use is a test of this skill too.
