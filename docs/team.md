# Team — Monash RoboClub (5 members)

| Member | GitHub | Role / owns | Uses Claude Code? | Read manual? |
|---|---|---|---|---|
| Repo owner | `tlmotan` | _TBD_ | Yes | Yes |
| Hao Zhe | _?_ | _TBD_ | _?_ | _?_ |
| Nichole | _?_ | _TBD_ | _?_ | _?_ |
| Rachel | _?_ | _TBD_ | _?_ | _?_ |
| Yu Xin | _?_ | _TBD_ | _?_ | _?_ |

## Possible ownership split (suggestion — edit freely)
Maps to modules in `architecture.md`, so people can work in parallel without merge conflicts.
- **Planner** — checkpoint ordering, time budget / when to skip
- **Motion** — `/ctl/command` wrapper, settling, retries
- **Vision** — ArUco detection, centering + roll checks
- **Integration & testing** — main flow, packing, running web-sim batches, score history
- **Docs & submission** — keeps `status.md` / `decisions.md` current, handles the MYSA side

## Working agreements
- Most teammates don't use Claude Code: the docs are written for humans first. Start at the repo `README.md`.
- Branch per feature, PR into `main`; don't push straight to `main`.
- Log every web-sim run in `sim-log.md`, put commit + your name in the Memo field, and don't touch a slot someone else is using (see `web-sim.md`).
- Never commit credentials (the simulator account is shared through email only).
