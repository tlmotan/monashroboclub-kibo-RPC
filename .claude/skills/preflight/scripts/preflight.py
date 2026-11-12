#!/usr/bin/env python3
"""Check our Kibo-RPC user code against the CLAUDE.md hard rules before a sim run or PR.

Usage (from anywhere in the repo):  python3 .claude/skills/preflight/scripts/preflight.py
Exit code: 0 = all FAIL checks passed (WARNs may remain), 1 = at least one FAIL, 2 = script error.

SELF-IMPROVING: each check is one function registered in CHECKS. When a new kind of mistake
slips through (or a rule is added), add a check. Never delete or loosen a FAIL check without
Timothy's OK. See .claude/skills/MAINTENANCE.md.
"""
import ast
import os
import re
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
PKG = os.path.join(REPO, 'krpc7th-simulator', 'users', 'catkin_ws', 'src', 'krpc_user')
PKG_REL = 'krpc7th-simulator/users/catkin_ws/src/krpc_user/'
SIM_REL = 'krpc7th-simulator/'
# Paths under the simulator bundle we are allowed to change (everything else there is off-limits).
ALLOWED_SIM_PATHS = (PKG_REL, 'krpc7th-simulator/share/')
# Imports available on the target image (ROS Melodic, Python 3.6, OpenCV 3.3.1). Others -> WARN.
KNOWN_IMPORTS = {
    'json', 'math', 'time', 'sys', 'os', 're', 'threading', 'itertools', 'functools', 'collections',
    'copy', 'heapq', 'random', 'traceback', 'enum', 'typing',
    'rospy', 'actionlib', 'actionlib_msgs', 'tf', 'tf2_ros', 'tf.transformations', 'numpy', 'cv2',
    'cv_bridge', 'platform_msgs', 'geometry_msgs', 'std_msgs', 'sensor_msgs', 'krpc_ib2_msgs', 'ib2_msgs',
}
WAIT_CALLS = {'wait_for_service', 'wait_for_server', 'wait_for_result', 'wait_for_message'}

results = []  # (level, name, detail)


def report(level, name, detail=''):
    results.append((level, name, detail))


def read(path):
    with open(path, errors='replace') as f:
        return f.read()


def git(*args):
    return subprocess.check_output(['git', '-C', REPO] + list(args), universal_newlines=True)


def user_script_path():
    launch = read(os.path.join(PKG, 'launch', 'krpc_user.launch'))
    m = re.search(r'name="team_user_script"\s+default="([^"]+)"', launch)
    name = m.group(1) if m else 'user_template.py'
    return name, os.path.join(PKG, 'scripts', name)


# ---------------------------------------------------------------------------- checks

def check_package_identity(src, tree):
    pkg_xml = read(os.path.join(PKG, 'package.xml'))
    cmake = read(os.path.join(PKG, 'CMakeLists.txt'))
    ok = '<name>krpc_user</name>' in pkg_xml and re.search(r'project\(\s*krpc_user\s*\)', cmake)
    ok = ok and os.path.exists(os.path.join(PKG, 'launch', 'krpc_user.launch'))
    report('PASS' if ok else 'FAIL', 'package name / launch file unchanged',
           '' if ok else 'package.xml, CMakeLists.txt project() and launch/krpc_user.launch must stay krpc_user')


def check_protected_paths(src, tree):
    try:
        # Local 'main' can be stale (it was, 2026-11-12), so prefer the remote's main.
        ref = 'origin/main'
        if subprocess.call(['git', '-C', REPO, 'rev-parse', '--verify', '-q', ref],
                           stdout=subprocess.DEVNULL) != 0:
            ref = 'main'
        base = git('merge-base', 'HEAD', ref).strip()
        changed = set(git('diff', '--name-only', base).split())
        changed |= set(git('ls-files', '--others', '--exclude-standard').split())
    except (OSError, subprocess.CalledProcessError) as exc:
        report('WARN', 'protected paths', 'could not run git: %s' % exc)
        return
    bad = sorted(p for p in changed if p.startswith(SIM_REL) and not p.startswith(ALLOWED_SIM_PATHS))
    if bad:
        hint = ''
        if bad == ['krpc7th-simulator/rviz/urdf.rviz']:
            hint = ' (the sim rewrites this itself: git checkout -- krpc7th-simulator/rviz/urdf.rviz)'
        report('FAIL', 'only krpc_user/ changed inside the simulator bundle', ', '.join(bad) + hint)
    else:
        report('PASS', 'only krpc_user/ changed inside the simulator bundle')


def check_compiles(src, tree):
    report('PASS' if tree is not None else 'FAIL', 'Python file parses')


def check_py36_syntax(src, tree):
    problems = []
    for node in ast.walk(tree):
        kind = type(node).__name__
        if kind == 'NamedExpr':
            problems.append('line %d: walrus := (3.8+)' % node.lineno)
        elif kind == 'Match':
            problems.append('line %d: match statement (3.10+)' % node.lineno)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)) and \
                getattr(node.args, 'posonlyargs', None):
            problems.append('line %d: positional-only "/" parameters (3.8+)' % node.lineno)
        elif isinstance(node, ast.ImportFrom) and node.module == '__future__' and \
                any(a.name == 'annotations' for a in node.names):
            problems.append('line %d: from __future__ import annotations (3.7+)' % node.lineno)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or '']
            if any(n.split('.')[0] in ('dataclasses', 'contextvars', 'importlib.resources') for n in names):
                problems.append('line %d: module not in Python 3.6 (%s)' % (node.lineno, names))
    for i, line in enumerate(src.splitlines(), 1):
        if re.search(r'\bf["\'].*\{[^{}]*=\s*[!:}]', line):
            problems.append('line %d: f-string "=" debug specifier (3.8+)' % i)
    report('FAIL' if problems else 'PASS', 'no syntax newer than Python 3.6', '; '.join(problems))


def check_required_lines(src, tree):
    need = {
        "/ib2_user/start subscriber": r"rospy\.Subscriber\(\s*['\"]/ib2_user/start['\"]",
        "/ib2_user/stop service": r"rospy\.Service\(\s*['\"]/ib2_user/stop['\"]",
        "ready param set True": r"rospy\.set_param\(\s*['\"]/ib2_user/ready['\"]\s*,\s*True\s*\)",
    }
    missing = [k for k, rx in need.items() if not re.search(rx, src)]
    report('FAIL' if missing else 'PASS', 'mandatory start/stop/ready lines present', ', '.join(missing))


def check_resolver_fix(src, tree):
    # D-007: without this the node can miss the one-shot start signal (a silent, zero-score run).
    m = re.search(r"os\.environ(?:\.setdefault\(|\[)\s*['\"]RES_OPTIONS['\"]", src)
    r = re.search(r'^\s*import rospy|^\s*from rospy', src, re.M)
    ok = m and r and m.start() < r.start()
    report('PASS' if ok else 'FAIL', 'RES_OPTIONS set before rospy is imported (D-007)',
           '' if ok else 'keep the RES_OPTIONS=single-request lines above "import rospy"; see docs/sim-troubleshooting.md')


def check_waits_have_timeouts(src, tree):
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in WAIT_CALLS:
            kw = {k.arg for k in node.keywords}
            n_pos = len(node.args)
            # wait_for_service(name, timeout) / wait_for_message(topic, type, timeout) / others(timeout)
            need_pos = {'wait_for_service': 2, 'wait_for_message': 3}.get(node.func.attr, 1)
            if n_pos < need_pos and 'timeout' not in kw:
                bad.append('line %d: %s() without timeout' % (node.lineno, node.func.attr))
    report('FAIL' if bad else 'PASS', 'every wait_for_* has a timeout', '; '.join(bad))


def check_loops(src, tree):
    risky = []
    for node in ast.walk(tree):
        if isinstance(node, ast.While) and isinstance(node.test, ast.Constant) and node.test.value is True:
            risky.append('line %d' % node.lineno)
    report('WARN' if risky else 'PASS', 'no unbounded "while True" loops',
           ('check these have a deadline and a retry cap: ' + ', '.join(risky)) if risky else '')


def check_stop_handler(src, tree):
    handler = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and 'stop_processing' in node.name:
            handler = node
    if handler is None:
        report('FAIL', 'stop handler cancels actions', 'no function named *stop_processing* found')
        return
    body = ast.get_source_segment(src, handler) or ''
    ok = re.search(r'cancel_(all_)?goals?\(', body) and 'Response' in body
    report('PASS' if ok else 'FAIL', 'stop handler cancels actions then responds',
           '' if ok else 'handler must call cancel_goal()/cancel_all_goals() on running actions and return a response')


def check_imports(src, tree):
    unknown = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            names = [node.module]
        else:
            continue
        for n in names:
            if n not in KNOWN_IMPORTS and n.split('.')[0] not in KNOWN_IMPORTS:
                unknown.add(n)
    report('WARN' if unknown else 'PASS', 'imports are ones the target image has',
           ('not in the known list (fine if it ships with ROS Melodic/py3.6; then add it to '
            'KNOWN_IMPORTS): ' + ', '.join(sorted(unknown))) if unknown else '')


def check_logging(src, tree):
    prints = [str(n.lineno) for n in ast.walk(tree)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'print']
    report('WARN' if prints else 'PASS', 'uses rospy.log* not print()',
           ('print() at lines ' + ', '.join(prints) + ' (web sim only returns rospy logs)') if prints else '')


CHECKS = [check_package_identity, check_protected_paths, check_compiles, check_py36_syntax,
          check_required_lines, check_resolver_fix, check_waits_have_timeouts, check_loops, check_stop_handler,
          check_imports, check_logging]


def main():
    name, path = user_script_path()
    if not name.endswith('.py'):
        report('WARN', 'launch runs %s (C++)' % name, 'these checks only cover Python; review the C++ node by hand')
        src, tree = '', None
    else:
        src = read(path)
        try:
            tree = ast.parse(src, filename=path)
        except SyntaxError as exc:
            tree = None
            report('FAIL', 'Python file parses', str(exc))
    for check in CHECKS:
        if tree is None and check not in (check_package_identity, check_protected_paths):
            continue
        check(src, tree)

    print('Preflight for %s' % os.path.relpath(path, REPO))
    for level, check_name, detail in results:
        print('  [%s] %s%s' % (level, check_name, (' -> ' + detail) if detail else ''))
    fails = sum(1 for r in results if r[0] == 'FAIL')
    warns = sum(1 for r in results if r[0] == 'WARN')
    print('RESULT: %s (%d fail, %d warn)' % ('FAIL' if fails else 'OK', fails, warns))
    return 1 if fails else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:
        print('preflight.py crashed: %r. Fix this script, then re-run.' % exc, file=sys.stderr)
        sys.exit(2)
