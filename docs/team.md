# Team: Monash RoboClub (5 members)

**Goal: win the Malaysia preliminary and reach the ISS final.** That means a program that finishes reliably on all 10 random runs and code clean enough to pass JAXA's safety review.

| Member | GitHub | Role / owns | Computer | Uses Claude Code? |
|---|---|---|---|---|
| Timothy | `tlmotan` | **Team lead + infra/testing**: repo, packaging, simulators, web-sim uploads, submission, MYSA contact | Mac (Apple Silicon) | Yes |
| Hao Zhe | _?_ | _TBD_ | _?_ | _?_ |
| Nichole | _?_ | _TBD_ | _?_ | _?_ |
| Rachel | _?_ | _TBD_ | _?_ | _?_ |
| Yu Xin | _?_ | _TBD_ | _?_ | _?_ |

Team computers: a mix of Windows and Apple Silicon Macs. See [`setup.md`](setup.md).

## Workstreams (from the team timeline)
| Workstream | People | Owns |
|---|---|---|
| Lead + infra/testing | 1 (Timothy) | Repo, packaging, local + web simulator, `sim-log.md`, submission, MYSA |
| Movement + route | 2 | Moving between checkpoints, visit order, time budget, recovery when moves fail |
| Vision + alignment | 2 | ArUco marker detection, pose estimate, fine-tuning position and roll at each marker |

Who takes which workstream is still to be decided.

## How we split the work
Most of us are new to ROS and robotics, so Claude (the AI assistant Timothy runs) writes much of the code. Everyone else makes sure we **understand, test and improve** it.

Good things for anyone to pick up, no ROS experience needed:
- **Review PRs.** Every PR explains in plain language what changed and why. Read it, ask questions in the comments, approve when it makes sense to you.
- **Run the local simulator and log results** in [`sim-log.md`](sim-log.md). More runs = better averages = better decisions.
- **Own a small piece**, for example:
  - tune one constant at the top of `user_template.py` (speed estimate, hold time, safety margin) and compare runs
  - save camera frames from a run and try OpenCV ArUco detection on them offline
  - measure how long rotations take vs straight moves
  - read `share/logs/latest/judge_module_logs/` after a run and explain why a checkpoint failed
- **Learn ROS basics** (about 2–3 hours): the ROS wiki tutorials on [topics](https://wiki.ros.org/ROS/Tutorials/UnderstandingTopics), [services](https://wiki.ros.org/ROS/Tutorials/UnderstandingServicesParams) and [actionlib](https://wiki.ros.org/actionlib_tutorials/Tutorials), then read our [`api.md`](api.md) and [`architecture.md`](architecture.md).

## Availability
- One teammate's last exam is **17 Nov 2026**; expect lighter availability until then.
- Holiday plans: _to be confirmed by each person_. Shift weeks in the timeline around them.

## Working agreements
- Docs are written for humans first. Start at the repo `README.md`.
- **One branch per change, merged by pull request**, so `main` always finishes a run. Don't push straight to `main`.
- **Web-sim tickets are spent sparingly**: only to confirm a real improvement, plus a batch near submission. Everything else runs on the local simulator.
- Web runs: Timothy uploads. Put the commit + your name in the Memo field, log it in `sim-log.md`, and don't touch a slot someone else is using (see [`web-sim.md`](web-sim.md)).
- One 30-minute team sync per week: last week's best score, blockers, this week's owners.
- Never commit credentials. The simulator login is shared privately, never in the repo or group chats.
