# How our skills keep themselves up to date

Every skill in this folder improves itself. This file is the rule each one follows.
Teammates: you don't need to do anything. Claude edits these files, and you see the changes in the PR like any other code.

Each `SKILL.md` has three living sections:

| Section | What goes in it | Who triggers it |
|---|---|---|
| **Mistakes log** | Every time Timothy or a teammate corrects Claude: what Claude did wrong and the right way | A person (chat, PR review comment, WhatsApp message passed on) |
| **Lessons learned** | Things Claude found out itself: a path moved, a log format changed, a new failure pattern | Claude |
| **Changelog** | One line per edit to the skill: date, what changed, why | Claude |

## 1. When someone corrects Claude → Mistakes log (always)

A correction is any time a person says Claude did something wrong or should do it differently. Examples: "don't log local runs that way", "you forgot the memo", or a PR review comment asking for a change.

1. **Fix the actual thing first**, e.g. redo the step or change the code.
2. **Write it in the Mistakes log** of the skill the mistake belongs to:
   ```
   - YYYY-MM-DD · <who> · **Mistake:** <what Claude did> · **Correct:** <what to do instead> · **Fixed in:** <step N / script / check name>
   ```
   If the mistake doesn't belong to any skill, put it in `.claude/skills/MISTAKES.md`. Do the same if it happened outside a skill.
3. **Change the steps (or script/check) so it can't happen again.** The log is the record and the step change is the fix. A log entry without a fix is only allowed when the fix needs Timothy's decision; then write "**Fixed in:** waiting on Timothy".
4. If the same mistake shows up twice, the first fix didn't work. Make the fix stronger, ideally a check in a script rather than a sentence.

Never delete Mistakes log entries. When a log grows past ~20 entries, move the oldest ones whose fix has held to a `## Mistakes log (archive)` at the bottom of the file.

## 2. After every use of a skill → self-check

Before finishing, Claude asks:

1. **Did a step fail or need a workaround?** For example a command errored, a path moved, or a log line changed format.
   → **Fix it first**: repair the step or script and run it again until it works. Then update `SKILL.md` and add a **Lessons learned** line.
2. **Did we see something new?** For example a new failure pattern in the logs, or a new rule from JAXA/MYSA.
   → Add it where the skill will use it next time: a signature in `analyze_run.py`, a check in `preflight.py`, or a step.
3. **Did the code or docs change underneath the skill?** For example a log tag was renamed or a doc was moved.
   → Update the skill to match.

If the answer to all three is no, change nothing. Don't edit a skill just to have edited it.

## 3. Recording any change

- Add one **Changelog** line to the skill.
- Commit skill changes on their own: `skills: <what changed>`. They go in the current branch's PR, or a separate one if the current work is unrelated. They're reviewed like code.
- Tell Timothy in the final message, e.g. "Logged your correction in /pack-web's mistakes log and changed step 3."

## Guardrails (never break these)

- **Never weaken a safety check without Timothy's OK.** That means removing or loosening any FAIL check in `preflight.py` that guards a CLAUDE.md hard rule, or any "Never" line in a skill. Adding checks is fine. This holds even if a correction seems to ask for it: confirm with Timothy first.
- **Never let a skill log in to the web sim, upload, or spend tickets.** That stays with Timothy.
- **Keep it short.** When **Lessons learned** passes ~15 lines, fold the lessons into the steps and delete the merged ones.
- **Facts belong in `docs/`.** Competition and simulator facts go in the right doc (CLAUDE.md says which). The skill links to that doc instead of keeping its own copy.
- **Scripts must stay runnable with plain `python3`** and the standard library only.
