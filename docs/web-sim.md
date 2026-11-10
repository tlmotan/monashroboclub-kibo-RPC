# Web Simulator & Submission: What We Know vs. Assume

Last updated: 10 Nov 2026. Page: https://jaxa.krpc.jp/simulation (one shared team login, shown as "Monash RoboClub (Malaysia)").

## Confirmed (from the 7th Kibo-RPC Rulebook v1.1 and Programming Manual)

- Deadline to submit: **20 Jan 2027, 23:59 JST** (10:59 PM Malaysia time). [Rulebook p.5]
- Deadline for questions to JAXA: **20 Jan 2027, 12:00 JST** (11:00 AM Malaysia time). [Rulebook p.5]
- Before the preliminary round, JAXA updates the RESULTS screen and opens a **"Preliminary" simulator**. Our program must be run there before it can be submitted. [Rulebook p.16]
- To submit: pick a run from the "Preliminary" results list on **RESULTS**, then press **SUBMIT**.
- Only runs with status **FINISHED** can be submitted. If we only have FAILED runs, we cannot enter.
- Resubmitting: press **CANCEL** on the submitted run, then SUBMIT another. Allowed any number of times before the deadline.
- After the deadline, SUBMIT and CANCEL lock. The run submitted at that moment is the one judged.
- In the preliminary round, the submitted program is run 10 times with random conditions; the score is the average. [Rulebook p.12]
- Upload format: the `.tar.gz` made by `krpc7th-simulator/users/packing.sh`.
- Finished runs offer VIEW RESULT, DOWNLOAD LOG FILES (result JSON + our `rospy.log*` output) and SIMULATOR VIEWER (replay). [Manual p.27–36]

## Observed on the page (screenshot, 10 Nov 2026)

- Course dropdown: **Regular**. Round tabs: **Preliminary** (Final is greyed out).
- Run slots (Slot #1 and #2 visible in the screenshot; teammate reports **3**), each with: program upload, Simulator Version (**1.1**), Simulator Level, Memo, START SIMULATION / TERMINATE SIMULATION / VIEW RESULT.
- Simulator Level options: **Easy / Normal / Hard / Very Hard** (default Normal).
- A box reading **"Sim Tickets: 240 / 120"**.
- Top nav includes a **BULLETIN BOARD**, so check it for announcements.
- No SUBMIT button yet.

## Assumptions (not confirmed, verify before relying on them)

| # | Assumption | How to check |
|---|---|---|
| 1 | The current Preliminary page is for practice; the special "Preliminary" simulator for submission isn't open yet | Watch for a SUBMIT button on RESULTS; check the Bulletin Board and MYSA emails |
| 2 | Each simulation run uses up 1 Sim Ticket | Start one run and see which number changes |
| 3 | Runs are limited by tickets, but we don't know if that's per day or for the whole competition | Note the count on two different days; ask MYSA if unclear |
| 4 | "240 / 120" might mean tickets left plus an amount that refills; meaning unknown | Same as #2 and #3 |
| 5 | The 3 slots can run 3 simulations at the same time | Start runs in two slots at once |
| 6 | Slots are shared by the whole team (one login), not assigned per person | Implied by the single account; agree on who uses which slot |
| 7 | Choosing a different Simulator Level (e.g. harder) changes the number/range of checkpoints | Run the same code on each level and compare results |
| 8 | The level used for the official preliminary 10-run evaluation is unknown | Ask MYSA / watch the Bulletin Board |

## Team rules until these are confirmed

- Test everyday changes on the **local simulator**; use web runs (tickets) only to confirm real improvements.
- Write the git commit and your name in the **Memo** field of every web run (e.g. `a1b2c3d Rachel: goal-first route`).
- Log every web run in [`sim-log.md`](sim-log.md).
- Don't terminate or overwrite a slot someone else is using.

## Open questions for MYSA (krpc@mysa.gov.my)

- What does "Sim Tickets: 240 / 120" mean, and do tickets refill?
- When does the "Preliminary" submission simulator open?
- Which Simulator Level is used for the official preliminary evaluation?
- Does Malaysia add any judging criteria on top of JAXA's score?
