#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""Monash RoboClub - 7th Kibo-RPC baseline.

Visits every CheckPoint the API gives us (in API order, GoalPoint last), reports each one,
then reports mission finished. A checkpoint is skipped when visiting it would leave too little
time to still reach the goal. Every move is logged (distance, duration, final error) so we can
measure IB2's real speed. See docs/architecture.md.
"""
import json
import math
import os

# Must run before rospy is imported. Inside the simulator's Docker network, the first hostname
# lookups a new process makes can stall for exactly 5 seconds (the IPv4 and IPv6 queries are sent
# together and one answer gets lost). The simulator sends the start signal only once and keeps it
# available for about 3 seconds, so a stalled node misses it and the whole run does nothing.
# 'single-request' makes the system resolver send the two queries one after the other, which
# removes the stall. It changes nothing else. See docs/sim-troubleshooting.md and decision D-007.
os.environ.setdefault('RES_OPTIONS', 'single-request')

import rospy
import actionlib
from platform_msgs.msg import UserLogic
from platform_msgs.srv import StopProcessingUserNode, StopProcessingUserNodeResponse
from geometry_msgs.msg import PoseStamped
from krpc_ib2_msgs.srv import MissionStart, MissionFinished, CheckPoints
from krpc_ib2_msgs.msg import CheckpointPassedAction, CheckpointPassedGoal
from ib2_msgs.msg import CtlCommandAction, CtlCommandGoal, CtlCommandResult, CtlStatusType
from ib2_msgs.msg import Navigation

# ---- Tunables (change these after measuring; see docs/field.md) ----
TIME_LIMIT_SEC = 300.0        # mission time limit from mission start [Rulebook p.7]
EST_SPEED_MPS = 0.10          # cruise speed; measured ~10 s per metre (docs/field.md)
MOVE_OVERHEAD_SEC = 18.0      # fixed cost per move (accel, turn, settle); measured ~15 s
SAFETY_MARGIN_SEC = 15.0      # time kept in hand when deciding whether a checkpoint fits
FINISH_RESERVE_SEC = 5.0      # stop flying this long before the limit and report finish
SETTLE_ANGLE_DEG = 3.0        # after a move, wait until attitude is within this of the target...
SETTLE_POSITION_M = 0.03      # ...and position within this...
SETTLE_TIMEOUT_SEC = 8.0      # ...but never wait longer than this
HOLD_SEC = 1.5                # wait after a move before reporting (rules need a 1 s hold)
MOVE_TIMEOUT_FACTOR = 2.0     # move timeout = estimated time x this
MIN_MOVE_TIMEOUT_SEC = 20.0   # ...but never shorter than this
SERVICE_TIMEOUT_SEC = 10.0    # wait_for_service / wait_for_server
ACTION_RESULT_TIMEOUT_SEC = 10.0  # checkpoint_passed result, and cancel confirmation
GET_CHECKPOINTS_ATTEMPTS = 3
CHECKPOINT_REPORT_ATTEMPTS = 2
MOVE_ATTEMPTS = 3             # tries per checkpoint when the move is rejected (e.g. INVALID_NAV)
MOVE_RETRY_PAUSE_SEC = 3.0    # pause before trying a rejected move again
MAX_PLAN_CHECKPOINTS = 12     # route planner considers at most this many (rules: 6-12)
DOCK_POSITION = (0.2, 0.0, 0.0)   # used only until the first navigation message arrives


def _distance(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def _angle_between_deg(q1, q2):
    """Smallest rotation angle between two quaternions [x, y, z, w], in degrees."""
    norm = math.sqrt(sum(c * c for c in q1)) * math.sqrt(sum(c * c for c in q2))
    if norm <= 0.0:
        return 180.0
    dot = abs(q1[0] * q2[0] + q1[1] * q2[1] + q1[2] * q2[2] + q1[3] * q2[3]) / norm
    return math.degrees(2.0 * math.acos(min(1.0, dot)))


def _estimate_move_sec(a, b):
    return MOVE_OVERHEAD_SEC + _distance(a, b) / EST_SPEED_MPS + HOLD_SEC


def plan_route(start, targets, goal_position, budget_sec):
    """Choose which checkpoints to visit, and in what order.

    start          (x, y, z) where IB2 is now
    targets        list of dicts with a 'position'; the goal checkpoint must NOT be in it
    goal_position  [x, y, z] of the goal, flown to last (None = route may end anywhere)
    budget_sec     time we may spend, including the final leg to the goal

    Returns (route, estimated_sec). The route visits as many checkpoints as fit in the budget;
    among routes with the same count it is the fastest one. estimated_sec includes the goal leg.

    Method: exact search over every subset of checkpoints (Held-Karp dynamic programming).
    best[mask][i] = least time to visit exactly the checkpoints in 'mask', ending at i.
    With at most 11 checkpoints that is 2048 x 11 states, which is quick even on IB2.
    """
    n = min(len(targets), MAX_PLAN_CHECKPOINTS)
    points = [targets[i]['position'] for i in range(n)]
    infinity = float('inf')

    from_start = [_estimate_move_sec(start, p) for p in points]
    between = [[_estimate_move_sec(a, b) for b in points] for a in points]
    if goal_position is None:
        to_goal = [0.0] * n
        direct_sec = 0.0
    else:
        to_goal = [_estimate_move_sec(p, goal_position) for p in points]
        direct_sec = _estimate_move_sec(start, goal_position)

    full = 1 << n
    best = [[infinity] * n for _ in range(full)]
    previous = [[-1] * n for _ in range(full)]
    for i in range(n):
        best[1 << i][i] = from_start[i]

    best_count = 0
    best_total = direct_sec
    best_end = (0, -1)
    for mask in range(1, full):
        row = best[mask]
        count = bin(mask).count('1')
        for last in range(n):
            time_here = row[last]
            if time_here >= budget_sec:   # unreachable, or already over budget
                continue
            total = time_here + to_goal[last]
            if total <= budget_sec and (count > best_count or (count == best_count and total < best_total)):
                best_count = count
                best_total = total
                best_end = (mask, last)
            leg = between[last]
            for nxt in range(n):
                bit = 1 << nxt
                if mask & bit:
                    continue
                candidate = time_here + leg[nxt]
                if candidate < best[mask | bit][nxt]:
                    best[mask | bit][nxt] = candidate
                    previous[mask | bit][nxt] = last

    route = []
    mask, last = best_end
    while last >= 0:
        route.append(targets[last])
        before = previous[mask][last]
        mask &= ~(1 << last)
        last = before
    route.reverse()
    return route, best_total


class UserTemplate:

    def __init__(self):
        rospy.init_node('krpc_user')

        # Action client
        self.__command = actionlib.SimpleActionClient('/ctl/command', CtlCommandAction)
        self.__checkpoint_client = actionlib.SimpleActionClient('/event/checkpoint_passed', CheckpointPassedAction)

        # Service client
        self.__mission_start = rospy.ServiceProxy('/event/mission_start', MissionStart)
        self.__mission_finished = rospy.ServiceProxy('/event/mission_finished', MissionFinished)
        self.__checkpoints = rospy.ServiceProxy('/mission/get_checkpoints', CheckPoints)

        self.__started = False
        self.__action_active = False
        self.__checkpoint_action_active = False
        self.__stop_requested = False
        self.__t0 = None
        self.__nav_position = None
        self.__nav_status = None
        self.__nav_quaternion = None
        self.__last_move_timed_out = False

        # Subscriber
        self.__subscriber_start = rospy.Subscriber('/ib2_user/start', UserLogic, self.__callback_start)  # DO NOT REMOVE THIS LINE
        self.__subscriber_nav = rospy.Subscriber('/sensor_fusion/navigation', Navigation, self.__callback_nav)

        # Service server
        self.__stop_processing_server = rospy.Service('/ib2_user/stop', StopProcessingUserNode, self.__stop_processing) # DO NOT REMOVE THIS LINE

        rospy.set_param('/ib2_user/ready', True) # DO NOT REMOVE THIS LINE

    # ------------------------------------------------------------------
    # Small helpers
    # ------------------------------------------------------------------
    def __should_abort(self):
        return rospy.is_shutdown() or self.__stop_requested

    def __elapsed(self):
        if self.__t0 is None:
            return 0.0
        return rospy.get_time() - self.__t0

    def __time_left(self):
        return TIME_LIMIT_SEC - self.__elapsed()

    def __current_position(self):
        position = self.__nav_position
        if position is None:
            return DOCK_POSITION
        return position

    def __callback_nav(self, data):
        try:
            p = data.pose.pose.position
            self.__nav_position = (p.x, p.y, p.z)
            q = data.pose.pose.orientation
            self.__nav_quaternion = (q.x, q.y, q.z, q.w)
            self.__nav_status = (data.status.status, data.status.marker)
        except Exception as exc:
            rospy.logwarn_throttle(10.0, 'navigation message not usable: %s' % exc)

    def __attitude_error_deg(self, quaternion):
        current = self.__nav_quaternion
        if current is None:
            return 0.0   # no data: don't block on it
        return _angle_between_deg(current, quaternion)

    def __wait_until_on_target(self, checkpoint_target):
        """After a move reports success, wait (bounded) until IB2 really is at the target pose.

        The move can report success while IB2 is still finishing its turn. Reporting the
        checkpoint then costs levels on centering/roll (seen locally: Lv1 and Lv2 with the
        position only 1 cm off). Returns after SETTLE_TIMEOUT_SEC at the latest.
        """
        checkpoint_id = checkpoint_target['checkpoint_id']
        start = rospy.get_time()
        first_angle = self.__attitude_error_deg(checkpoint_target['quaternion'])
        while not self.__should_abort():
            angle = self.__attitude_error_deg(checkpoint_target['quaternion'])
            offset = _distance(self.__current_position(), checkpoint_target['position'])
            waited = rospy.get_time() - start
            on_target = angle <= SETTLE_ANGLE_DEG and offset <= SETTLE_POSITION_M
            if on_target or waited >= SETTLE_TIMEOUT_SEC:
                log = rospy.loginfo if on_target else rospy.logwarn
                log('SETTLE cp=%d on_target=%s waited=%.1fs angle_at_move_end=%.1fdeg angle_now=%.1fdeg pos_err=%.3fm',
                    checkpoint_id, on_target, waited, first_angle, angle, offset)
                return on_target
            rospy.sleep(0.1)
        return False

    def __wait_for_service(self, name):
        try:
            rospy.wait_for_service(name, timeout=SERVICE_TIMEOUT_SEC)
            return True
        except (rospy.ROSException, rospy.ROSInterruptException) as exc:
            rospy.logerr('service %s not available: %s', name, exc)
            return False

    # ------------------------------------------------------------------
    # Mission events
    # ------------------------------------------------------------------
    def __notify_mission_start(self):
        if not self.__wait_for_service('/event/mission_start'):
            return False
        res = self.__mission_start()
        rospy.loginfo('mission_start result: success=%s message=%s', res.success, res.message)
        return res.success

    def __notify_mission_finished(self):
        if not self.__wait_for_service('/event/mission_finished'):
            return False
        res = self.__mission_finished()
        rospy.loginfo('mission_finished result: success=%s message=%s (clock=%.1fs)',
                      res.success, res.message, self.__elapsed())
        return res.success

    def __notify_checkpoint_passed(self, checkpoint_id):
        if not self.__checkpoint_client.wait_for_server(rospy.Duration(SERVICE_TIMEOUT_SEC)):
            rospy.logerr('checkpoint_passed action server not available')
            return False

        goal = CheckpointPassedGoal()
        goal.checkpoint_id = checkpoint_id
        for attempt in range(1, CHECKPOINT_REPORT_ATTEMPTS + 1):
            if self.__should_abort():
                return False
            rospy.loginfo('notify checkpoint_id=%d passed (attempt %d/%d)',
                          checkpoint_id, attempt, CHECKPOINT_REPORT_ATTEMPTS)
            self.__checkpoint_action_active = True
            try:
                self.__checkpoint_client.send_goal(goal)
                deadline = rospy.get_time() + ACTION_RESULT_TIMEOUT_SEC
                finished = False
                while not self.__should_abort() and rospy.get_time() < deadline:
                    if self.__checkpoint_client.wait_for_result(rospy.Duration(0.2)):
                        finished = True
                        break
                if not finished:
                    self.__checkpoint_client.cancel_goal()
                    rospy.logwarn('checkpoint_passed id=%d: no result (timeout or stop), cancelled', checkpoint_id)
                    continue
                result = self.__checkpoint_client.get_result()
            finally:
                self.__checkpoint_action_active = False

            if result is None:
                rospy.logwarn('checkpoint_passed id=%d: empty result', checkpoint_id)
                continue
            rospy.loginfo('checkpoint_passed id=%d result: success=%s message=%s',
                          checkpoint_id, result.success, result.message)
            if result.success:
                return True
            rospy.sleep(0.5)
        return False

    # ------------------------------------------------------------------
    # Checkpoint list
    # ------------------------------------------------------------------
    def __get_checkpoint_id(self, checkpoint):
        for key in ('checkpoint_id', 'checkpointid', 'id'):
            if key in checkpoint:
                return int(checkpoint[key])
        return None

    def __parse_checkpoints(self, message):
        """Returns (list of targets in API order, goal id or None). Raises on a bad payload."""
        payload = json.loads(message)
        # Key spelling differs between the manual and the simulator files, so normalise it.
        normalised = dict((str(k).lower().replace('_', ''), v) for k, v in payload.items())

        targets = []
        for cp in normalised.get('checkpoints', []):
            if not isinstance(cp, dict):
                continue
            checkpoint_id = self.__get_checkpoint_id(cp)
            position = cp.get('position')
            if checkpoint_id is None or not (isinstance(position, list) and len(position) >= 3):
                rospy.logwarn('ignoring malformed checkpoint entry: %s', cp)
                continue

            quaternion = [0.0, 0.0, 0.0, 1.0]
            attitude = cp.get('attitude')
            if isinstance(attitude, dict):
                attitude_quaternion = attitude.get('quaternion')
                if isinstance(attitude_quaternion, list) and len(attitude_quaternion) >= 4:
                    quaternion = attitude_quaternion
            else:
                rospy.logwarn('checkpoint_id=%d has no attitude, using identity', checkpoint_id)

            targets.append({
                'checkpoint_id': checkpoint_id,
                'position': [float(position[0]), float(position[1]), float(position[2])],
                'quaternion': [float(quaternion[0]), float(quaternion[1]), float(quaternion[2]), float(quaternion[3])],
            })

        goal_id = normalised.get('goalpointid')
        if goal_id is not None:
            goal_id = int(goal_id)
        return targets, goal_id

    def __fetch_checkpoints(self):
        """Returns (targets, goal_id), or (None, None) if the API could not give us a usable list."""
        for attempt in range(1, GET_CHECKPOINTS_ATTEMPTS + 1):
            if self.__should_abort():
                break
            try:
                if not self.__wait_for_service('/mission/get_checkpoints'):
                    continue
                res = self.__checkpoints()
                if not res.success:
                    rospy.logwarn('get_checkpoints attempt %d/%d failed: %s',
                                  attempt, GET_CHECKPOINTS_ATTEMPTS, res.message)
                    rospy.sleep(0.5)
                    continue
                targets, goal_id = self.__parse_checkpoints(res.message)
                if targets:
                    rospy.loginfo('get_checkpoints: %d checkpoints, ids=%s, goalpoint_id=%s',
                                  len(targets), [t['checkpoint_id'] for t in targets], goal_id)
                    return targets, goal_id
                rospy.logwarn('get_checkpoints attempt %d/%d: no usable checkpoints',
                              attempt, GET_CHECKPOINTS_ATTEMPTS)
            except Exception as exc:
                rospy.logwarn('get_checkpoints attempt %d/%d error: %s',
                              attempt, GET_CHECKPOINTS_ATTEMPTS, exc)
            rospy.sleep(0.5)
        rospy.logerr('could not get checkpoints after %d attempts', GET_CHECKPOINTS_ATTEMPTS)
        return None, None

    # ------------------------------------------------------------------
    # Movement
    # ------------------------------------------------------------------
    def __move_to_checkpoint(self, checkpoint_target, timeout_sec):
        """Absolute move with a hard timeout. Returns True only on TERMINATE_SUCCESS."""
        checkpoint_id = checkpoint_target['checkpoint_id']
        position = checkpoint_target['position']
        quaternion = checkpoint_target['quaternion']
        start_position = self.__current_position()
        distance = _distance(start_position, position)
        rospy.loginfo(
            'moving to checkpoint_id=%d: x=%.3f y=%.3f z=%.3f qx=%.4f qy=%.4f qz=%.4f qw=%.4f (dist=%.2fm timeout=%.0fs)',
            checkpoint_id,
            position[0], position[1], position[2],
            quaternion[0], quaternion[1], quaternion[2], quaternion[3],
            distance, timeout_sec
        )

        target = PoseStamped()
        target.header.frame_id = 'iss_body'
        target.pose.position.x = position[0]
        target.pose.position.y = position[1]
        target.pose.position.z = position[2]
        target.pose.orientation.x = quaternion[0]
        target.pose.orientation.y = quaternion[1]
        target.pose.orientation.z = quaternion[2]
        target.pose.orientation.w = quaternion[3]

        command_type = CtlStatusType(type=CtlStatusType.MOVE_TO_ABSOLUTE_TARGET)
        goal = CtlCommandGoal(target=target, type=command_type)

        if not self.__command.wait_for_server(rospy.Duration(SERVICE_TIMEOUT_SEC)):
            rospy.logerr('/ctl/command action server not available')
            return False

        move_start = rospy.get_time()
        deadline = move_start + timeout_sec
        result_text = 'NO_RESULT'
        success = False
        self.__last_move_timed_out = False
        self.__action_active = True
        try:
            self.__command.send_goal(goal)
            finished = False
            while not self.__should_abort() and rospy.get_time() < deadline:
                if self.__command.wait_for_result(rospy.Duration(0.2)):
                    finished = True
                    break
            if finished:
                result = self.__command.get_result()
                if result is not None:
                    result_text = str(result.type)
                    success = (result.type == CtlCommandResult.TERMINATE_SUCCESS)
            else:
                self.__command.cancel_goal()
                stopped = self.__command.wait_for_result(rospy.Duration(ACTION_RESULT_TIMEOUT_SEC))
                result_text = 'CANCELLED_STOP' if self.__should_abort() else 'CANCELLED_TIMEOUT'
                self.__last_move_timed_out = True
                rospy.logwarn('move to checkpoint_id=%d cancelled (%s), stop confirmed=%s',
                              checkpoint_id, result_text, stopped)
        finally:
            self.__action_active = False

        # MOVE_LOG lines are our speed measurements: grep for them in the user log.
        rospy.loginfo('MOVE_LOG cp=%d dist=%.3f dur=%.2f err=%.3f result=%s ok=%s nav=%s clock=%.1f',
                      checkpoint_id, distance, rospy.get_time() - move_start,
                      _distance(self.__current_position(), position), result_text, success,
                      self.__nav_status, self.__elapsed())
        return success

    def __visit(self, checkpoint_target, move_timeout_sec):
        """Move, hold, report. Returns True if the judge accepted the checkpoint."""
        checkpoint_id = checkpoint_target['checkpoint_id']
        deadline = rospy.get_time() + move_timeout_sec
        moved = False
        for attempt in range(1, MOVE_ATTEMPTS + 1):
            time_for_move = deadline - rospy.get_time()
            if self.__should_abort() or time_for_move <= 0.0:
                break
            if self.__move_to_checkpoint(checkpoint_target, time_for_move):
                moved = True
                break
            # A move that ran out of time is not retried. A move the controller rejected
            # (INVALID_NAV, ABORTED...) is worth another go after a short pause, because
            # otherwise one bad moment makes us give up on every checkpoint in turn.
            if self.__last_move_timed_out or attempt == MOVE_ATTEMPTS:
                break
            rospy.logwarn('checkpoint_id=%d: move rejected (attempt %d/%d), retrying in %.0fs',
                          checkpoint_id, attempt, MOVE_ATTEMPTS, MOVE_RETRY_PAUSE_SEC)
            rospy.sleep(MOVE_RETRY_PAUSE_SEC)
        if not moved:
            rospy.logwarn('checkpoint_id=%d: move failed, not reporting it', checkpoint_id)
            return False
        if self.__should_abort():
            return False
        self.__wait_until_on_target(checkpoint_target)
        if self.__should_abort():
            return False
        rospy.sleep(HOLD_SEC)
        rospy.loginfo('checkpoint_id=%d: after hold pos_err=%.3fm angle=%.1fdeg', checkpoint_id,
                      _distance(self.__current_position(), checkpoint_target['position']),
                      self.__attitude_error_deg(checkpoint_target['quaternion']))
        passed = self.__notify_checkpoint_passed(checkpoint_id)
        if not passed:
            rospy.logwarn('checkpoint_id=%d: not accepted by judge', checkpoint_id)
        return passed

    # ------------------------------------------------------------------
    # Mission flow
    # ------------------------------------------------------------------
    def __fly_mission(self):
        targets, goal_id = self.__fetch_checkpoints()
        if targets is None:
            return

        goal_target = None
        remaining = []
        for target in targets:
            if goal_id is not None and target['checkpoint_id'] == goal_id:
                goal_target = target
            else:
                remaining.append(target)
        if goal_target is None:
            rospy.logwarn('goalpoint_id=%s is not in the checkpoint list; no goal leg planned', goal_id)
        goal_position = goal_target['position'] if goal_target is not None else None

        passed = []
        failed = []
        # Each pass: re-plan from where we are with the time we really have left, fly the first
        # leg of that plan, drop that checkpoint from the list. The list shrinks every pass, so
        # the loop is bounded. Re-planning means time saved (or lost) on earlier legs is used.
        while remaining and not self.__should_abort():
            here = self.__current_position()
            budget_sec = self.__time_left() - SAFETY_MARGIN_SEC
            plan_start = rospy.get_time()
            route, estimated_sec = plan_route(here, remaining, goal_position, budget_sec)
            rospy.loginfo('PLAN route=%s est=%.0fs budget=%.0fs left_out=%d (planned in %.2fs)',
                          [t['checkpoint_id'] for t in route], estimated_sec, budget_sec,
                          len(remaining) - len(route), rospy.get_time() - plan_start)
            if not route:
                break
            target = route[0]
            remaining.remove(target)
            checkpoint_id = target['checkpoint_id']
            leg_sec = _estimate_move_sec(here, target['position'])
            goal_leg_sec = 0.0
            if goal_position is not None:
                goal_leg_sec = _estimate_move_sec(target['position'], goal_position)
            move_timeout_sec = min(max(leg_sec * MOVE_TIMEOUT_FACTOR, MIN_MOVE_TIMEOUT_SEC),
                                   budget_sec - goal_leg_sec)
            if self.__visit(target, move_timeout_sec):
                passed.append(checkpoint_id)
            else:
                failed.append(checkpoint_id)
        skipped = [t['checkpoint_id'] for t in remaining]
        if skipped:
            rospy.logwarn('checkpoints skipped, not enough time: %s (%.0fs left)', skipped, self.__time_left())

        if goal_target is not None and not self.__should_abort():
            move_timeout_sec = self.__time_left() - FINISH_RESERVE_SEC
            if move_timeout_sec > 0.0:
                if self.__visit(goal_target, move_timeout_sec):
                    passed.append(goal_target['checkpoint_id'])
            else:
                rospy.logwarn('no time left to fly to the goal')

        rospy.loginfo('SUMMARY passed=%s failed=%s skipped=%s of %d checkpoints, clock=%.1fs',
                      passed, failed, skipped, len(targets), self.__elapsed())

    def __run_user_flow(self, msg):
        try:
            if not self.__notify_mission_start():
                return
            self.__t0 = rospy.get_time()

            # USER EDIT AREA: define route planning and game-specific flow here.
            # ***********************************************
            try:
                self.__fly_mission()
            except Exception as exc:
                rospy.logerr('mission flow failed: %s', exc)
            # ***********************************************

            if not self.__should_abort():
                self.__notify_mission_finished()
        except Exception as exc:
            rospy.logerr('user flow failed: %s', exc)

    def __callback_start(self, msg):
        if self.__started:
            rospy.logwarn('start callback is already processed')
            return
        self.__started = True

        rospy.loginfo('start %s', msg)
        self.__run_user_flow(msg)

    def __stop_processing(self, request):
        try:
            self.__stop_requested = True  # every loop in the mission flow checks this
            if self.__action_active:
                self.__command.cancel_goal()
            if self.__checkpoint_action_active:
                self.__checkpoint_client.cancel_goal()
            rospy.loginfo('finish processing')
            return StopProcessingUserNodeResponse(result=StopProcessingUserNodeResponse.SUCCESS)
        except Exception as exc:
            rospy.logerr('stop processing failed: %s', exc)
            return StopProcessingUserNodeResponse(result=StopProcessingUserNodeResponse.ERROR)

    def run(self):
        rospy.spin()


if __name__ == '__main__':
    UserTemplate().run()
