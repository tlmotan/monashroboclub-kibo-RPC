---
name: meeting-update
description: Keep the Kibo-RPC kickoff meeting agenda (what Timothy says at the next team meeting) in step with the project — refresh the demo results, decisions, homework, links and the "New since last version" box, then republish the shared page. Run automatically by /wrap-session after every change, or when asked to "update the kickoff/meeting agenda" or "what should I say at the meeting".
---

# /meeting-update: keep the kickoff agenda current

**The page:** https://claude.ai/artifact/SaBuz3CcB2hrEvPwfPHY41 ("Kibo-RPC Team Kickoff")
**Its source:** `docs/meetings/kickoff-agenda.html`. Always edit this file and publish it to the URL above, so the link stays the same and changes show up in PRs.

## When it runs
- At the end of every `/wrap-session`, i.e. after every change. Also whenever Timothy asks.
- **Only until the kickoff has happened.** Once Timothy says it's done, stop updating this page. Ask him whether to start a weekly-sync agenda the same way, then update this skill to match (MAINTENANCE.md).

## Steps

1. **Collect what changed since the page's "Last updated" date:** `docs/status.md` (session log, next up), `docs/sim-log.md` (best result), `docs/decisions.md` (new or changed decisions), `docs/roadmap.md` (dates), and open PRs (`GH_TOKEN=$(gh auth token --user tlmotan) gh pr list`).
2. **Decide if the meeting content changes.** Ask: would Timothy say something different at the meeting because of this? If not, for example a typo fix or an internal refactor, stop here and say "agenda unchanged".
3. **Edit the matching sections** of `docs/meetings/kickoff-agenda.html`:
   | If this changed… | …update |
   |---|---|
   | Best local/web score, a new failure or fix | **Demo** bullets (real numbers from `sim-log.md`) |
   | A decision proposed, made or reversed (`decisions.md`) | **Decisions to make**: remove ones already settled, add new open ones |
   | Next-up tasks done or added (`status.md`) | **Homework**: don't assign work that's already done |
   | New/merged PRs, new docs | **Homework** review task and **Read before the call** links |
   | Workflow rules (branch protection, skills, tickets) | **How we work together** card |
   | Milestones (`roadmap.md`) | **Key dates** |
4. **Rewrite the "New since the last version" box**: 2–5 bullets, in plain words for beginners, saying what changed since the last version that the team should hear. Replace the old bullets rather than piling up a history; git keeps the history. Set **Last updated** to today.
5. **Keep it a ~55-minute meeting.** If a section grows, cut the least important item rather than adding time.
6. **Publish** with the Artifact tool: `file_path` = the source file, `url` = the page above. If the publish says a newer version exists, merge onto that version and publish again; never force it. If the source file doesn't exist in this checkout yet (its PR isn't merged), use `Artifact read` on the URL and save it there first.
7. **Commit** the source change with the rest of the session's work. `/wrap-session` does this.
8. **Tell Timothy** in one line what changed on the agenda, with the link.
9. **Self-improve:** follow `.claude/skills/MAINTENANCE.md`.

## Never
- Never put the simulator login, tickets details beyond counts, or anyone's personal info on the page.
- Never change sharing settings. Timothy shares the link himself.
- Never assign homework to a named teammate unless `docs/team.md` (or Timothy) says they own that work.

## Mistakes log
Corrections from Timothy or teammates. Format and rules: `.claude/skills/MAINTENANCE.md` section 1.

_No entries yet._

## Lessons learned
- The page was first published from a scratchpad file; its source now lives in `docs/meetings/` so every update is versioned.

## Changelog
- 2026-11-12: Created. First update: route planner, start-signal fix (D-007), `main` protection, roadmap PR #3, skills PR #4.
