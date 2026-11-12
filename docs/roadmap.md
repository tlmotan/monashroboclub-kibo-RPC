# Roadmap: from today to submission (and the ISS final)

Written 12 Nov 2026. This is the whole-project plan. It replaces the week-by-week table in the
"Team Timeline & To-dos" PDF, but keeps that timeline's milestones and dates.
For what is happening *this week*, see [`status.md`](status.md).

## Where we are
The baseline program works on the local simulator: it visits checkpoints, ends at the goal and
reports finished inside 5 minutes. Three things we learned changed the plan:

1. **The baseline came early.** The timeline gave it until week 4. It was done on day 1.
2. **We may not need the camera.** Flying to the pose the API gives us already scores Lv3 (the top
   level), landing about 1 cm from the target. The timeline assumed we would need camera alignment
   to get there. We don't know yet if this holds on the web simulator, which adds a disturbance.
3. **Every move has a big fixed cost.** A move takes about 20 s plus 8 s per metre
   (see [`field.md`](field.md)). So the order we visit checkpoints in, and that fixed 20 s,
   matter more than anything else right now.

## Milestones (unchanged from the timeline)
| Milestone | Date | Meaning |
|---|---|---|
| M1 | 6 Dec 2026 | Program finishes on every difficulty level |
| M2 | 20 Dec 2026 | Checkpoints score well on the web simulator |
| M3 | 11 Jan 2027 | Feature freeze: after this, bug fixes and tuning only |
| M4 | 17 Jan 2027 | Submitted, with 3 days of buffer |
| Deadline | 20 Jan 2027, 10:59 PM Malaysia time | SUBMIT and CANCEL lock |

## Phase 1: Prove it on the real simulator (now to 23 Nov)
**Goal:** get a real score, and answer the unknowns that decide everything after.

- **Route ordering.** Pick the visit order that fits the most checkpoints and still ends at the goal. There are at most 12 checkpoints, so the program can try the options and pick the best. This is the biggest improvement available.
- **First web runs.** Baseline on Easy, then the route-ordered version on Normal. About 2–3 tickets. Timothy uploads; Claude prepares the file, level and memo.
- **Questions those runs answer:**
  - Does the web simulator's disturbance spoil our 1 cm accuracy?
  - What do a score and a time bonus actually look like?
  - What does "Sim Tickets: 240 / 120" mean?
- **Everyone:** get one local run working using [`setup.md`](setup.md).
- **Timothy:** email MYSA the open questions listed in [`web-sim.md`](web-sim.md).

**Done when:** a FINISHED web run is logged in [`sim-log.md`](sim-log.md) with a score.

## Phase 2: Reliable on every level (24 Nov to 6 Dec) → M1
**Goal:** it finishes every time, from Easy to Very Hard (6 to 12 checkpoints).

- **Batch runner.** A script that runs the local simulator several times in a row and prints a results table, so anyone can produce an average without reading log files.
- **Self-check before reporting.** Before telling the judge "checkpoint passed", the program works out its own position, aim and roll error and logs the level it expects. We then know why a checkpoint scored what it did.
- **Level sweep.** Local runs on each level; fix whatever breaks with more checkpoints and longer routes.
- **Wall check.** Confirm that flying in a straight line between two checkpoints never clips the module walls. No run so far has hit an awkward pair.

**Done when:** 10 local runs in a row finish on each level, and one web run per level is FINISHED.

## Decision gate (around 6 Dec): do we need the camera?
We decide from the Phase 1 and 2 results and write the decision in [`decisions.md`](decisions.md).

| If the web simulator shows… | Then… |
|---|---|
| Navigation alone still scores Lv3 | The camera stays out of the flight path. The vision pair builds an offline marker check only, and the team's effort moves to speed. |
| The disturbance or drift costs us levels | Phase 3 builds marker-based correction, as the original timeline planned. |

We also settle Python vs C++ here (decision D-003), using timing evidence from the web runs.

## Phase 3: Accuracy under disturbance (7 to 20 Dec) → M2
What gets built depends on the gate. Either way:

- **Correct after a move.** If the self-check says the level would drop, make one short extra move before reporting. One retry at most.
- **If the camera is needed:** detect the ArUco marker, work out our pose from it, correct position, aim and roll, and fall back to navigation alone when no marker is visible.

**Done when:** on the web simulator, every checkpoint we report scores Lv3 on Normal and Hard.

## Phase 4: Speed (21 Dec to 3 Jan)
**Goal:** the best average score. The time bonus multiplies the score by up to 2×, so finishing earlier can be worth more than one extra checkpoint.

- **Cut the fixed 20 s per move.** Measure how much is turning and how much is travelling, try a shorter hold, and try reporting as soon as the self-check passes.
- **Tune the skip rule.** The scoring formula is not published, so we find the best trade-off by experiment on the web simulator. Tickets are budgeted for this.
- **Holiday week is light:** batch runs, and fix the most common failure.

**Done when:** we have our best 10-run local average so far, confirmed by a few web runs.

## Phase 5: Recovery and safety (4 to 11 Jan) → M3 feature freeze
- **Recovery.** Handle a stuck move, missing navigation data and drift. Every retry has a cap.
- **Clean-up.** JAXA reads finalists' source code for safety. Clear structure, no dead code, every wait has a timeout.

**Done when:** deliberately broken runs (a forced move failure, missing checkpoint data, a stop signal in the middle of a move) all end cleanly.

## Phase 6: Submit (12 to 20 Jan) → M4
- Bug fixes and tuning only.
- When the "Preliminary" simulator opens: run the frozen version there, check it says FINISHED, and Timothy presses SUBMIT by **17 Jan**.
- Resubmit only for a measured improvement.
- Last questions to JAXA must be sent before 20 Jan, 11:00 AM Malaysia time.

## After submission
- **21 Jan to 17 Feb 2027:** Malaysia preliminary round. Our program is run 10 times; the average is our score.
- **If we qualify:** code changes for the ISS from early March to mid April (JAXA releases an ISS simulator in mid March), then one real run on the ISS in early May. No restarts.

## Who does what
| Who | Does |
|---|---|
| Claude (AI assistant, run by Timothy) | Most of the code, the batch runner, log analysis, plain-language PR descriptions |
| Timothy | Web uploads, tickets, MYSA contact, merging PRs |
| Movement + route pair | Review route ordering, run level sweeps, own the tuning numbers at the top of `user_template.py` |
| Vision + alignment pair | Save camera frames and test marker detection offline **now**, so the gate decision is informed and Phase 3 can start quickly if needed |

Who is in each pair is tracked in [`team.md`](team.md).

## Biggest risks
| Risk | What we do about it |
|---|---|
| The web simulator behaves differently from the local one | Web runs come first (Phase 1), before we build more on local results |
| The scoring formula and the judged difficulty level are unknown | Ask MYSA now; tune by experiment in Phase 4 |
| We run out of tickets | Local simulator for everyday work; a small planned ticket budget per phase |
| The camera turns out to be necessary late | The vision pair starts offline groundwork in Phase 1; the gate is 6 Dec, not January |
| One run in the preliminary ends FAILED (it's an average of 10) | Reliability phases come before speed; broken-run tests in Phase 5 |

## Keeping this up to date
Change this file when a phase finishes, a date moves or the gate decision is made. Week-to-week
detail belongs in [`status.md`](status.md), not here.
