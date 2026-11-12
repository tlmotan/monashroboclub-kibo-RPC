---
name: wrap-session
description: End-of-session routine for the Kibo-RPC repo — update docs/status.md, log non-obvious decisions in docs/decisions.md, fix any doc facts that turned out wrong, preflight if the node changed, then commit on a branch, push and open a beginner-friendly PR. Use when asked to wrap up, finish the session, "commit and PR this", or at the end of any work session that changed files.
---

# /wrap-session: leave the repo so a beginner teammate can pick it up

## Steps

1. **See what changed:** `git status --short` and `git diff --stat`. Group the changes into what they are about.
   If changes from **different** pieces of work are mixed, ask which go together. One branch + PR per change.
2. **If the node changed:** run `/preflight` (must be OK). Mention the most recent relevant `/sim-run` result. If the change was never run in the sim, say so plainly in the PR.
3. **Update `docs/status.md`** (CLAUDE.md requires it every session):
   - **Now:** phase and best score, only if they changed.
   - **Next up:** strike through done items (`~~…~~ ✅ date`) and add new ones.
   - **Known issues:** add or remove.
   - **Session log:** one new entry at the top, `**YYYY-MM-DD** — what changed, last sim result, next step`, in plain words.
4. **Decisions:** for each non-obvious choice made this session, append `D-NNN (date) — title` to `docs/decisions.md` in its format (Status · Context · Decision · Why). Use the next free number. If a decision replaced an earlier one, mark the old one `superseded by D-NNN`.
5. **Wrong facts:** if a doc turned out wrong this session, fix that doc in this same change (CLAUDE.md rule).
6. **Branch:** never commit to `main`. If on `main`, `git fetch` then `git checkout -b <short-topic> origin/main`.
7. **Commit and push:** a plain-English message that says why, not just what, ending with the attribution line from the system reminder. Then `git push -u origin <branch>`.
8. **Open the PR** against `main`. Use the `tlmotan` account: `GH_TOKEN=$(gh auth token --user tlmotan) gh pr create ...` (the default `gh` account is not a collaborator). The body is for beginners:
   ```
   ## What this does        (2–4 sentences, no jargon, or explain the jargon)
   ## Why                   (the problem or score gain)
   ## How we checked it     (preflight result, sim runs with numbers, or "not run yet")
   ## What to look at when reviewing   (files, in reading order)
   ## Next                  (what's left)
   ```
   End with the attribution line from the system reminder. If this PR stacks on another, name it.
9. **Update the meeting agenda:** run `/meeting-update` (`.claude/skills/meeting-update/SKILL.md`) so the kickoff page matches this change. Commit its source edit in this same PR. This step happens until Timothy says the kickoff is done.
10. **Tell Timothy** the PR link, what's not verified, what changed on the agenda, and anything that needs his decision.
11. **Self-improve:** follow `.claude/skills/MAINTENANCE.md`. Review comments asking for a change count as corrections: log them in the **Mistakes log** of the skill they belong to (or `.claude/skills/MISTAKES.md`).

## Never
- Never push to or merge `main`; Timothy or a teammate merges.
- Never commit `krpc7th-simulator/share/` output, `.tar.gz` uploads, or simulator files the sim rewrote (`rviz/urdf.rviz`).
- Never record D-003 (Python vs C++) as decided until Timothy says the team agreed.

## Mistakes log
Corrections from Timothy or teammates. Format and rules: `.claude/skills/MAINTENANCE.md` section 1.

_No entries yet._

## Lessons learned
- Local `main` can lag `origin/main`; always branch from `origin/main` after `git fetch`.

## Changelog
- 2026-11-12: Created from the routine used in the 10–12 Nov sessions.
- 2026-11-12: Added step 9 (update the kickoff agenda after every change), asked for by Timothy.
