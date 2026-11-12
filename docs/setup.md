# Setup: get the local simulator running

Takes about 30–60 min the first time, mostly downloads. You need about **20 GB free disk** and **8 GB+ RAM** (16 GB is better).
Based on Programming Manual ch.2 and 4.4. If you get stuck, check [`sim-troubleshooting.md`](sim-troubleshooting.md), then ask in the group.

> You only need this to run the simulator on your own computer. To read code, review PRs or just follow along, a browser and GitHub are enough.

Pick your computer: **[Windows](#windows-10--11)** · **[Mac (Apple Silicon: M1/M2/M3/M4)](#mac-apple-silicon)**

---

## Windows 10 / 11
Everything runs inside **Ubuntu on WSL2**. JAXA's scripts don't run in plain Windows.

**1. Install WSL2 + Ubuntu.** Open PowerShell **as Administrator**:
```powershell
wsl --install -d Ubuntu-24.04
```
Restart when asked. Ubuntu then opens and asks you to pick a username and password (a new one, just for Ubuntu).
Check it's WSL **2**: `wsl --list --verbose` should show `VERSION 2`.

**2. Install Docker inside Ubuntu.** Open the **Ubuntu** app (not PowerShell) and paste this:
```bash
sudo apt-get update && sudo apt-get install -y ca-certificates curl gnupg git
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update && sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
```
Close the Ubuntu window, reopen it, and check that `docker run hello-world` prints "Hello from Docker!".
(Docker Desktop with the WSL2 backend also works if you already have it. Don't install both.)

**3. Give WSL enough memory (optional but recommended).** WSL gets half your RAM by default. If your laptop has 16 GB, create `C:\Users\<you>\.wslconfig` containing:
```ini
[wsl2]
memory=10GB
```
Then run `wsl --shutdown` in PowerShell and reopen Ubuntu.

**4. Get the code, inside Ubuntu.** Clone into your Ubuntu home folder, **not** under `/mnt/c/...`. That avoids slow builds and Windows line-ending problems.
```bash
cd ~
git clone https://github.com/tlmotan/monashroboclub-kibo-RPC.git
cd monashroboclub-kibo-RPC/krpc7th-simulator
```

**5. Build and run.** Most Windows laptops are Intel/AMD, so **no `--arm64`**:
```bash
bash ./build.sh          # first time only, ~10–30 min
bash ./simulation.sh     # one full run, ~5 min
```
While it runs, open **http://localhost** in your Windows browser to watch. Then go to [After your first run](#after-your-first-run).

**Editing code:** install [VS Code](https://code.visualstudio.com/) on Windows plus the **WSL** extension. Then, in Ubuntu, run `code .` inside the repo folder.

---

## Mac (Apple Silicon)
**1. Install Docker Desktop** from https://www.docker.com/products/docker-desktop/ (pick "Apple Silicon"). Open it once and let it start.
In Docker Desktop → Settings → Resources, set **Memory to 8 GB or more**.

**2. Get the code** (Terminal app):
```bash
cd ~/Documents
git clone https://github.com/tlmotan/monashroboclub-kibo-RPC.git
cd monashroboclub-kibo-RPC/krpc7th-simulator
```
(If `git` isn't found, macOS will offer to install the command-line tools. Say yes.)

**3. Build and run.** On Apple Silicon you **must** add `--arm64`:
```bash
bash ./build.sh --arm64  # first time only, ~10–30 min
bash ./simulation.sh     # one full run, ~5 min
```
Open **http://localhost** to watch.

---

## After your first run
- Results are in `krpc7th-simulator/share/logs/latest/`:
  - `judge_module_logs/result.json`: which checkpoints passed, at what level, and whether the goal was reached
  - `cheat_sheet.json`: that run's random checkpoint layout
  - `user_programs_logs/`: our program's log messages
- Replay the last run: `bash ./replay.sh`
- Add a row to [`sim-log.md`](sim-log.md) with the date, your name, `local`, the level and the result.
- Each run saves about 300 MB. Delete old folders in `share/logs/` now and then. Git ignores them.

## Common problems
| Problem | Fix |
|---|---|
| `permission denied ... docker.sock` (Windows) | You skipped reopening Ubuntu after `usermod`. Close and reopen it. |
| http://localhost doesn't load | Something else uses port 80. See [`sim-troubleshooting.md`](sim-troubleshooting.md). |
| Build or sim crashes / freezes | Usually not enough RAM. Close other apps; raise Docker/WSL memory (steps above). |
| `exec format error` | Wrong architecture build. Mac: use `--arm64`. Windows (Intel/AMD): don't. |
| Very slow on Windows | The repo is under `/mnt/c`. Re-clone into `~` inside Ubuntu. |
