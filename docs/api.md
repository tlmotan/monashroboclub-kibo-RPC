# Game API cheat sheet (ROS 1 Melodic)

Source: *Programming Manual v1.0 (2026-10-05)* ch.6. Python shown; C++ equivalents in [Manual p.53–56] and `user_template_node.cpp`.

## Mission events
| Name | Kind | Type | Notes |
|---|---|---|---|
| `/mission/get_checkpoints` | Service | `krpc_ib2_msgs/CheckPoints` | empty req → `success`, `message` (JSON string) |
| `/event/mission_start` | Service | `krpc_ib2_msgs/MissionStart` | call first |
| `/event/checkpoint_passed` | Action | `krpc_ib2_msgs/CheckpointPassedAction` | goal `checkpoint_id:int32` → result `success, message`. **Server judges current state** — only send once stable and all 3 conditions hold |
| `/event/mission_finished` | Service | `krpc_ib2_msgs/MissionFinished` | = completion report. Ends scoring |

`get_checkpoints` JSON [Manual p.58]:
```json
{ "checkpoint_count": 8,
  "checkpoints": [{
    "checkpoint_id": 1,
    "position": [x, y, z],
    "marker_pose": {"position": [...], "quaternion": [x,y,z,w]},
    "score_bands": [{"radius":0.1,"level":3}, {"radius":0.2,"level":2}, {"radius":0.3,"level":1}],
    "attitude": {
      "quaternion": [x,y,z,w],
      "centering_bands": [{"angle":10.0,"level":3}, ...],
      "roll_bands":      [{"angle":10.0,"level":3}, ...] } }],
  "goalpoint_id": 12 }
```
Attitude conditions only apply if the band arrays are present.

## Movement & state
| Name | Kind | Type | Notes |
|---|---|---|---|
| `/ctl/command` | Action | `ib2_msgs/CtlCommandAction` | goal: `target: PoseStamped`, `type: CtlStatusType` |
| `/sensor_fusion/navigation` | Topic | `ib2_msgs/Navigation` | `pose` (PoseStamped), `twist`, `a`, `status` |
| `/ctl/status` | Topic | `ib2_msgs/CtlStatus` | pose/twist/a + current `type` |
| `/ctl/wrench` | Topic | `geometry_msgs/WrenchStamped` | direct force [N] / torque [Nm] in `body`. Advanced; don't mix with `/ctl/command` without testing |

Command types to use: `MOVE_TO_ABSOLUTE_TARGET` (=40, `frame_id='iss_body'`), `MOVE_TO_RELATIVE_TARGET` (=30, `frame_id='body'`), `STOP_MOVING` (=20, target zeros → then `KEEP_POSE`).
Result `type`: `TERMINATE_SUCCESS=0, ABORTED=1, TIME_OUT=2, INVALID_NAV=3, INVALID_CMD=4`.
Move done ⇔ `/ctl/status.type` goes from MOVE_* → `KEEP_POSE`(10) or `STOP_MOVING`(20).
Cancel: `client.cancel_goal(); client.wait_for_result(rospy.Duration(10))` before sending next target.

```python
from ib2_msgs.msg import CtlCommandAction, CtlCommandGoal, CtlCommandResult, CtlStatusType
goal = CtlCommandGoal(target=pose_stamped,
                      type=CtlStatusType(type=CtlStatusType.MOVE_TO_ABSOLUTE_TARGET))
```

## Camera
| Name | Kind | Type |
|---|---|---|
| `/camera_main/image_raw` | Topic | `sensor_msgs/Image` → `cv_bridge` to OpenCV |
| `/camera_main/camera_info` | Topic | `sensor_msgs/CameraInfo` (`K`, `D`) — None until first msg |

ArUco recipe [Manual p.44–45]: gray → `cv2.aruco.detectMarkers` (4x4 dict) → pick ID → `estimatePoseSingleMarkers(corners, 0.02, K, D)` → check stability over frames. OpenCV **3.3.1** API (old-style `aruco.DetectorParameters_create()`).
Left/right cameras are off unless `slam_wrapper=false` in launch.

## Mandatory plumbing — DO NOT REMOVE [Manual p.56, p.68–70]
- Subscribe `/ib2_user/start` (`platform_msgs/UserLogic`) — mission trigger; guard against double start.
- Serve `/ib2_user/stop` (`platform_msgs/StopProcessingUserNode`) — cancel all actions **then** return `SUCCESS`(0) / `ERROR`(255).
- `rospy.set_param('/ib2_user/ready', True)` — start isn't published until this is set.

## Error-handling policy [Manual p.75]
| Situation | Do |
|---|---|
| Service/action server unavailable | wait with timeout; give up cleanly |
| Move failed | don't send checkpoint_passed; log cause |
| Action timed out | `cancel_goal()`, confirm stopped |
| checkpoint_passed failed | log; don't resend forever (cap retries) |
| No fresh camera data | log; skip camera-dependent step |
| Stop received | cancel everything, then respond |

## Template gotcha
`__resolve_first_checkpoint_target` falls back to a default origin target on failure — scores nothing. Replace with real retry/abort logic.
