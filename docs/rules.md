# Rules & Scoring (distilled)

Sources: *7th Kibo-RPC Rulebook v1.1 (2026-10-15)*, *Guidebook v1.1*, *Guidance Session 2 (2026-10-21)*.
Page refs are PDF page numbers. Regular Course only; the Beginner Course has its own rulebook (not covered here).

## Our registration
- Team **Monash RoboClub**, competing in **Malaysia** — National Level, **Advanced Category (Regular Course)**. Confirmed by MYSA 2026-10-13.
- POC / secretariat: **Malaysian Space Agency (MYSA)** — `krpc@mysa.gov.my`, portal https://www.mysa.gov.my/kibo-rpcmalaysia. Email them for login/access problems.
- Simulator logins come from `no-reply@mail.jaxa.krpc.jp` (credentials are never stored in this repo).
- Links: simulator https://jaxa.krpc.jp/user-auth · downloads https://jaxa.krpc.jp/download · tutorial videos https://jaxa.krpc.jp/#section_tutorial_video
- Each country can add its own evaluation criteria on top of JAXA's [Rulebook p.4]. **Malaysia-specific criteria and preliminary dates: unverified — check the MYSA portal or ask the secretariat.**

## Key dates (JST)
| What | When |
|---|---|
| Question deadline | 2027-01-20 12:00 |
| **Program submission deadline** | **2027-01-20 23:59** |
| Preliminary round | 2027-01-21 → 2027-02-17 |
| Finalist code modification | early Mar → mid-Apr 2027 (ISS sim released mid-Mar) |
| ISS Final Round Run | early May 2027 |
| Final Round Event | June 2027 |
[Rulebook p.5, Guidebook p.6–8]

## Mission flow [Rulebook p.6, p.11]
1. IB2 auto-undocks from Dock Station → **timer starts** (Mission Start).
2. Call `/mission/get_checkpoints` to get CheckPoint positions/attitudes (randomised per run).
3. Visit CheckPoints in any order (route is ours to plan).
4. At each: hold position + aim + roll for **1 s** with marker in view, then call `/event/checkpoint_passed`.
5. Go to GoalPoint, call `/event/mission_finished` (= mission completion report).

Mission Finish = time limit hit **or** completion report started. Anything after doesn't score. [Rulebook p.24]

## Preconditions [Rulebook p.7]
- **6–12 CheckPoints**, count depends on difficulty level (Easy / Normal / Hard / Very Hard on web sim [Manual p.32]).
- Each CheckPoint is a **sphere** placed randomly at an angle+distance from its AR marker.
- **Microgravity module** disturbance (simulator only) — unknown gravity pattern. Expect drift.
- **Time limit: 5 min** from undock, report must be inside it.
- Known in advance: start point, AR marker poses/IDs (see `field.md`), number & range of CheckPoints, GoalPoint position.
- Not known: actual CheckPoint poses for a given run; disturbance pattern.

## Scoring [Rulebook p.13–15, p.24–25; Manual p.58–59]
`Score = Pt_all × Mag_clear`, where `Pt_all = Σ Pt_check + Pt_goal`.

**Pt_check** — per CheckPoint, three conditions each graded Lv1–Lv3; awarded level = **min** of the three. Any condition outside Lv1 → zero.
| Condition | Measured as | Example bands (from sample JSON) |
|---|---|---|
| ① Position | distance IB2 ↔ checkpoint `position` | Lv3 ≤0.1 m, Lv2 ≤0.2 m, Lv1 ≤0.3 m |
| ② Camera centering | angle between camera line-of-sight and direction to marker | Lv3 ≤10°, Lv2 ≤20°, Lv1 ≤30° |
| ③ Roll about line of sight | roll error vs `attitude.quaternion` | Lv3 ≤10°, Lv2 ≤20°, Lv1 ≤30° |
Bands come per-checkpoint in the API response — **always read them, don't hardcode.**
State must be held for **1 s**. Exact point values per level: **not published.**

**Pt_goal** — awarded for passing all CheckPoints within time and reaching GoalPoint.

**Mag_clear** — multiplier from remaining time at report; more time left = higher; **max ~2×**. Formula not published.
→ No report within 5 min = no time bonus.

Manual's tip [p.33]: first make *CheckPoints Passed* and *Goal Reached* reliable, then chase Time Bonus.

## Preliminary evaluation [Rulebook p.12, p.16–17]
- Submitted program is auto-run **10 times** with different random + disturbance conditions; **average** is the ranking score. → Robustness > peak score.
- Only a run in **FINISHED** status on the *Preliminary* simulator can be SUBMITted. FAILED-only = can't enter.
- Can CANCEL and resubmit until the deadline; buttons lock after.

## Final round (if we qualify) [Rulebook p.18–22]
- Real IB2 on ISS, **one run**, no stopping. Re-run only if the fault isn't our code.
- JAXA reviews source for safety; "many corrections required every year" — keep code clean and defensive from the start.
- Auto-terminated if stuck, lost self-position, or idle too long.
- Run order by preliminary rank tiers; low tiers may not get to run.

## Strategy notes from the organisers [Guidance p.22]
- Accurate relative pose to the marker is the core skill.
- Route design matters: trade accuracy vs speed deliberately.
- Plan recovery for loops, missing markers, bad localisation; bound every retry.
- "Teams that run many simulations win."
