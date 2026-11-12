#!/usr/bin/env python3
"""Summarise one local Kibo-RPC simulator run and diagnose known failure patterns.

Usage (from the repo root):
    python3 .claude/skills/sim-run/scripts/analyze_run.py            # latest run
    python3 .claude/skills/sim-run/scripts/analyze_run.py 20261112084639
    python3 .claude/skills/sim-run/scripts/analyze_run.py --all      # one line per past run

Exit code: 0 = run scored normally, 1 = run had a problem (see DIAGNOSIS), 2 = script error.

SELF-IMPROVING: when a run fails in a way this script does not recognise, it prints
"UNKNOWN". Claude then finds the cause and adds a new entry to SIGNATURES below,
so the next time it is recognised automatically. See .claude/skills/MAINTENANCE.md.
"""
import json
import os
import re
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
LOGS = os.path.join(REPO, 'krpc7th-simulator', 'share', 'logs')
TIME_LIMIT_SEC = 300.0


def read(path):
    try:
        with open(path, errors='replace') as f:
            return f.read()
    except OSError:
        return ''


def resolve_run_dir(arg):
    if arg:
        path = arg if os.path.isabs(arg) else os.path.join(LOGS, arg)
    else:
        latest = os.path.join(LOGS, 'latest', 'link_origin')
        # 'latest' is a copy without result.json; the timestamped folder has everything.
        path = os.path.realpath(latest) if os.path.exists(latest) else os.path.join(LOGS, 'latest')
    if not os.path.isdir(path):
        sys.exit('run folder not found: %s' % path)
    return path


def collect(run_dir):
    """Pull every fact we care about out of one run folder."""
    game = read(os.path.join(run_dir, 'judge_module_logs', 'game.log'))
    user = read(os.path.join(run_dir, 'user_programs_logs', 'user_program_output.log'))
    r = {'dir': os.path.basename(run_dir), 'game': game, 'user': user}

    cheat = read(os.path.join(run_dir, 'cheat_sheet.json'))
    try:
        cs = json.loads(cheat)
        r['seed'] = cs.get('RandomSeed')
        r['level'] = cs.get('Level')
        r['cp_ids'] = [c.get('checkpointid') for c in cs.get('Checkpoints', [])]
    except ValueError:
        r['seed'] = r['level'] = None
        r['cp_ids'] = []

    try:
        r['result'] = json.loads(read(os.path.join(run_dir, 'judge_module_logs', 'result.json')))
    except ValueError:
        r['result'] = None

    r['go'] = bool(re.search(r'\[INFO\] Go\s*$', game, re.M))
    r['watchdog_secs'] = None
    m = re.search(r'shutdown after (\d+) secs', game)
    if m:
        r['watchdog_secs'] = int(m.group(1))
    r['start_received'] = 'start id:' in user
    r['ready_line'] = (re.search(r'node (?:not )?settled[^\n]*', user) or [None])[0]
    r['mission_finished'] = re.search(r'mission_finished result: success=(\w+)', user)
    r['summary'] = (re.search(r'SUMMARY [^\n]*', user) or [None])[0]
    r['plans'] = re.findall(r'PLAN [^\n]*', user)
    r['moves'] = re.findall(r'MOVE_LOG [^\n]*', user)
    r['problems'] = re.findall(r'\[rosout\]\[(?:WARN|ERROR|FATAL)\][^\n]*', user)
    # Only tracebacks before shutdown count: rospy's own threads often print one while the
    # node is being stopped after 'finish processing', which is harmless (seen 2026-11-12).
    before_stop = user.split('finish processing')[0]
    r['traceback'] = 'Traceback (most recent call last)' in before_stop
    return r


# ---------------------------------------------------------------------------
# Known failure patterns. Add a new one whenever we diagnose a new kind of failure.
# Each: (id, test(run) -> bool, what it means, where to read more)
# ---------------------------------------------------------------------------
SIGNATURES = [
    ('NO_START_SIGNAL',
     lambda r: r['go'] and not r['start_received'],
     'Simulator said "Go" but our node never got the /ib2_user/start message, so the '
     'mission never began and the run scores nothing. The start is sent once, right after '
     '/ib2_user/ready turns true.',
     'docs/sim-troubleshooting.md (start signal), docs/decisions.md D-007; check RES_OPTIONS is still at the top of the node'),
    ('PYTHON_CRASH',
     lambda r: r['traceback'],
     'Our Python node crashed before the stop request (Traceback in user_program_output.log).',
     'read the traceback in user_programs_logs/user_program_output.log'),
    ('NEVER_REACHED_GO',
     lambda r: not r['go'],
     'The simulator never reached "Go": start-up broke before our code ran (Docker, '
     'Gazebo, or our node never set ready).',
     'docs/sim-troubleshooting.md; judge_module_logs/game.log'),
    ('NO_MISSION_FINISHED',
     lambda r: r['start_received'] and not r['mission_finished'],
     'Mission started but we never called mission_finished, which means a FAILED run on the web sim.',
     'user log: look at the last lines before "finish processing"'),
    ('ILLEGAL',
     lambda r: bool(r['result'] and r['result'].get('Illegal')),
     'Judge marked the run Illegal.',
     'docs/rules.md'),
    ('GOAL_FAILED',
     lambda r: bool(r['result'] and not r['result']['JudgeReport'].get('goal', {}).get('success')),
     'Goal was not reached / not accepted.',
     'result.json goal.reason'),
    ('OVER_TIME',
     lambda r: bool(r['result'] and (r['result']['JudgeReport']['mission'].get('duration_sec') or 0)
                    > TIME_LIMIT_SEC),
     'Mission took longer than 5 minutes.',
     'docs/rules.md (timing)'),
]


def diagnose(r):
    hits = [s for s in SIGNATURES if s[1](r)]
    if not hits and r['result'] is None:
        hits = [('UNKNOWN', None,
                 'No result.json and no known pattern matched. Investigate, then add a '
                 'signature to SIGNATURES in this script.', 'all logs in the run folder')]
    return hits


def git_commit():
    try:
        sha = subprocess.check_output(['git', '-C', REPO, 'rev-parse', '--short', 'HEAD'],
                                      universal_newlines=True).strip()
        dirty = subprocess.call(['git', '-C', REPO, 'diff', '--quiet', 'HEAD', '--',
                                 'krpc7th-simulator/users/catkin_ws/src/krpc_user']) != 0
        return sha + (' + uncommitted changes' if dirty else '')
    except (OSError, subprocess.CalledProcessError):
        return '?'


def cp_summary(r):
    if not r['result']:
        return None
    rep = r['result']['JudgeReport']
    passed, missed = [], []
    for c in rep.get('checkpoint_detail', []):
        if c['success']:
            passed.append('%d(Lv%d)' % (c['checkpoint_id'], c['level']))
        else:
            missed.append('%d: %s' % (c['checkpoint_id'], c.get('reason')))
    # Count includes the goal point, matching how docs/sim-log.md has always counted.
    total = len(rep.get('checkpoint_detail', []))
    return passed, missed, total, rep['mission'].get('duration_sec'), rep.get('goal', {}).get('success')


def one_line(r):
    s = cp_summary(r)
    diag = ','.join(h[0] for h in diagnose(r)) or 'OK'
    if s:
        return '%s  seed=%s  CPs %d/%d  goal=%s  %.1fs  %s' % (
            r['dir'], r['seed'], len(s[0]), s[2], 'Y' if s[4] else 'N', s[3] or 0, diag)
    return '%s  seed=%s  no result  %s' % (r['dir'], r['seed'], diag)


def report(r):
    out = ['# Run %s' % r['dir'], '',
           '- Level: %s, seed %s, %d points incl. goal: %s' % (r['level'], r['seed'],
                                                                len(r['cp_ids']), r['cp_ids']),
           '- Code checked out now (only meaningful for a run you just made): %s' % git_commit(),
           '- Start handshake: go=%s start_received=%s  ready: %s' % (
               r['go'], r['start_received'], r['ready_line'] or '(no settle line)')]
    s = cp_summary(r)
    if s:
        passed, missed, total, dur, goal = s
        out += ['- Checkpoints: %d/%d passed: %s' % (len(passed), total, ', '.join(passed)),
                '- Missed: %s' % ('; '.join(missed) or 'none'),
                '- Goal: %s   Mission time: %.1f s (%.0f s spare)' % (
                    'reached' if goal else 'NOT reached', dur or 0, TIME_LIMIT_SEC - (dur or 0))]
    else:
        out.append('- No result.json: the judge produced no score for this run.')
    if r['summary']:
        out.append('- Our summary line: `%s`' % r['summary'])
    if r['plans']:
        out.append('- First plan: `%s`' % r['plans'][0])
    if r['moves']:
        out.append('- Moves logged: %d (see MOVE_LOG lines for speed calibration)' % len(r['moves']))
    if r['problems']:
        out += ['', '## Warnings/errors from our node'] + ['- `%s`' % p for p in r['problems'][:15]]

    hits = diagnose(r)
    out += ['', '## DIAGNOSIS']
    if not hits:
        out.append('OK: the run scored normally.')
    for sid, _, meaning, where in hits:
        out.append('- **%s**: %s (read: %s)' % (sid, meaning, where))

    if s:
        passed, missed, total, dur, goal = s
        row = '| %s | ? | local | 1.1 bundle | %s (seed %s) | %s | n/a (local) | %d / %d (%s) | %s | %.1f s | n/a | n/a | <notes> |' % (
            '%s-%s-%s' % (r['dir'][0:4], r['dir'][4:6], r['dir'][6:8]), r['level'], r['seed'],
            git_commit(), len(passed), total, ', '.join(passed), 'Y' if goal else 'N', dur or 0)
    else:
        row = '| %s | ? | local | 1.1 bundle | %s (seed %s) | %s | n/a | none (no result) | N | - | n/a | n/a | %s |' % (
            '%s-%s-%s' % (r['dir'][0:4], r['dir'][4:6], r['dir'][6:8]), r['level'], r['seed'],
            git_commit(), ', '.join(h[0] for h in hits))
    out += ['', '## Suggested sim-log row', row]
    return '\n'.join(out), bool(hits)


def main():
    args = sys.argv[1:]
    if args and args[0] == '--all':
        for d in sorted(os.listdir(LOGS)):
            if d[:1].isdigit():
                print(one_line(collect(os.path.join(LOGS, d))))
        return 0
    text, problem = report(collect(resolve_run_dir(args[0] if args else None)))
    print(text)
    return 1 if problem else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:  # the script itself broke: Claude should fix it (see MAINTENANCE.md)
        print('analyze_run.py crashed: %r. Fix this script, then re-run.' % exc, file=sys.stderr)
        sys.exit(2)
