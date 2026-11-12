# Monash RoboClub — 7th Kibo-RPC

Our entry for JAXA's **7th Kibo Robot Programming Challenge** (Malaysia national level via MYSA, Advanced Category, Regular Course).
We program the **Int-Ball2** robot to fly around the ISS Kibo module, line up its camera on AR markers at 6–12 checkpoints, and finish at the goal point, all within 5 minutes.

**Program submission deadline: 20 Jan 2027, 23:59 JST.**

## New here? Read in this order (~20 min instead of ~150 pages of PDFs)
1. [docs/rules.md](docs/rules.md) — the game, the scoring, the deadlines
2. [docs/status.md](docs/status.md) — where we are and what's next
3. [docs/team.md](docs/team.md) — who owns what, and beginner-friendly ways to help
4. [docs/architecture.md](docs/architecture.md) — how our program is structured
5. When you start coding: [docs/api.md](docs/api.md) (ROS interfaces) and [docs/field.md](docs/field.md) (coordinates)

Before using the web simulator: [docs/web-sim.md](docs/web-sim.md) (tickets, slots, submission) and log runs in [docs/sim-log.md](docs/sim-log.md).

Also: [docs/decisions.md](docs/decisions.md) (why we chose things) · [docs/sim-troubleshooting.md](docs/sim-troubleshooting.md) (when the simulator breaks).

The official PDFs (Rulebook, Programming Manual, Guidebook) are in the repo root and at https://jaxa.krpc.jp/download. Our docs cite their page numbers, so go there when you need the full detail.

## Where the code is
`krpc7th-simulator/users/catkin_ws/src/krpc_user/`. **This is the only folder we edit.**
- `scripts/user_template.py` is the Python program (default)
- `src/user_template_node.cpp` is the C++ alternative

## Quick start
Step-by-step for Windows and Mac: **[docs/setup.md](docs/setup.md)**. Short version:
```bash
cd krpc7th-simulator
bash ./build.sh            # add --arm64 on Apple Silicon Macs
bash ./simulation.sh       # then open http://localhost
```
To run on the web simulator, package the code and upload the result at https://jaxa.krpc.jp/user-auth → SIMULATION:
```bash
cd krpc7th-simulator/users
bash ./packing.sh my_run
```

## Rules of the repo
- Never edit `krpc_api_server/`, `krpc_ib2_msgs/`, `bootstrap/`, or the simulator infrastructure.
- Work on a branch and open a PR into `main`.
- Log your web-sim runs in `docs/sim-log.md` (web runs cost Sim Tickets, so test locally first).
- Never commit passwords.

`CLAUDE.md` holds instructions for the Claude Code AI assistant. You can ignore it if you don't use it.
