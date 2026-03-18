from robot_api.config import settings
from robot_api.fairino_client import FairinoClient
from robot_api.models import CartesianMoveRequest, MoveResponse, RobotStateResponse


def move_cartesian(request: CartesianMoveRequest) -> MoveResponse:
    desc_pos = request.to_desc_pos()
    tool = settings.fairino_tool if request.tool is None else request.tool
    user = settings.fairino_user if request.user is None else request.user
    vel = settings.fairino_default_vel if request.vel is None else request.vel

    if settings.fairino_dry_run:
        return MoveResponse(
            success=True,
            dry_run=True,
            robot_ip=settings.fairino_robot_ip,
            command="MoveCart",
            desc_pos=desc_pos,
            tool=tool,
            user=user,
            vel=vel,
            message="Dry-run mode enabled. No motion command was sent.",
        )

    with FairinoClient(settings.fairino_robot_ip) as client:
        result = client.move_cartesian(
            desc_pos=desc_pos,
            tool=tool,
            user=user,
            vel=vel,
        )

    return MoveResponse(
        success=True,
        dry_run=False,
        robot_ip=settings.fairino_robot_ip,
        command="MoveCart",
        desc_pos=result.desc_pos,
        tool=result.tool,
        user=result.user,
        vel=result.vel,
        error_code=result.error_code,
        message="Motion command accepted by robot controller.",
    )


def get_robot_state() -> RobotStateResponse:
    with FairinoClient(settings.fairino_robot_ip) as client:
        state = client.get_state()

    return RobotStateResponse(
        robot_ip=settings.fairino_robot_ip,
        realtime_available=state.realtime_available,
        enabled=None if state.enabled < 0 else state.enabled,
        robot_mode=None if state.robot_mode < 0 else state.robot_mode,
        program_state=None if state.program_state < 0 else state.program_state,
        robot_state=None if state.robot_state < 0 else state.robot_state,
        emergency_stop=None if state.emergency_stop < 0 else state.emergency_stop,
        safety_stop=None if state.safety_stop == [-1, -1] else state.safety_stop,
        collision_state=None if state.collision_state < 0 else state.collision_state,
        motion_done=None if state.motion_done < 0 else state.motion_done,
        tool=None if state.tool < 0 else state.tool,
        user=None if state.user < 0 else state.user,
        main_error_code=None if state.main_error_code < 0 else state.main_error_code,
        sub_error_code=None if state.sub_error_code < 0 else state.sub_error_code,
        tcp_pose=state.tcp_pose or None,
        joint_pos=state.joint_pos or None,
        message=state.message,
    )
