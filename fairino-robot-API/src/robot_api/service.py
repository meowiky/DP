from robot_api.config import settings
from robot_api.fairino_client import FairinoClient
from robot_api.models import (
    CartesianMoveRequest,
    InverseKinHasSolutionResponse,
    InverseKinRefResponse,
    InverseKinRequest,
    MoveResponse,
    PartialCartesianMoveRequest,
    RobotStateResponse,
    ToolStateResponse,
)


def _resolve_joint_pos_ref(client: FairinoClient, joint_pos_ref: list[float] | None) -> list[float]:
    if joint_pos_ref is not None:
        return joint_pos_ref

    state = client.get_state()
    if not state.realtime_available or not state.joint_pos:
        raise RuntimeError(
            "Realtime joint state is unavailable, so joint_pos_ref must be provided explicitly."
        )
    return state.joint_pos


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


def move_cartesian_partial(request: PartialCartesianMoveRequest) -> MoveResponse:
    with FairinoClient(settings.fairino_robot_ip) as client:
        state = client.get_state()
        if not state.realtime_available or not state.tcp_pose:
            raise RuntimeError(
                "Realtime TCP pose is unavailable, so omitted Cartesian fields cannot be filled."
            )

        desc_pos = [
            state.tcp_pose[0] if request.x is None else request.x,
            state.tcp_pose[1] if request.y is None else request.y,
            state.tcp_pose[2] if request.z is None else request.z,
            state.tcp_pose[3] if request.rx is None else request.rx,
            state.tcp_pose[4] if request.ry is None else request.ry,
            state.tcp_pose[5] if request.rz is None else request.rz,
        ]
        tool = state.tool if request.tool is None and state.tool >= 0 else request.tool
        user = state.user if request.user is None and state.user >= 0 else request.user
        vel = settings.fairino_default_vel if request.vel is None else request.vel

        if tool is None:
            tool = settings.fairino_tool
        if user is None:
            user = settings.fairino_user

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


def get_tool_state() -> ToolStateResponse:
    with FairinoClient(settings.fairino_robot_ip) as client:
        tool_state = client.get_tool_state()

    return ToolStateResponse(
        robot_ip=settings.fairino_robot_ip,
        active_tool=tool_state.active_tool,
        active_tcp_offset=tool_state.active_tcp_offset,
        current_tool_coord=tool_state.current_tool_coord,
        tool_0_coord=tool_state.tool_0_coord,
        tool_1_coord=tool_state.tool_1_coord,
        message=tool_state.message,
    )


def get_inverse_kin_ref(request: InverseKinRequest) -> InverseKinRefResponse:
    desc_pos = request.to_desc_pos()

    with FairinoClient(settings.fairino_robot_ip) as client:
        joint_pos_ref = _resolve_joint_pos_ref(client, request.joint_pos_ref)
        result = client.get_inverse_kin_ref(
            type=request.type,
            desc_pos=desc_pos,
            joint_pos_ref=joint_pos_ref,
        )

    message = None
    if result.error_code != 0:
        message = "GetInverseKinRef returned a non-zero error code."

    return InverseKinRefResponse(
        robot_ip=settings.fairino_robot_ip,
        type=request.type,
        desc_pos=desc_pos,
        joint_pos_ref=joint_pos_ref,
        error_code=result.error_code,
        joint_pos=result.joint_pos,
        message=message,
    )


def get_inverse_kin_has_solution(request: InverseKinRequest) -> InverseKinHasSolutionResponse:
    desc_pos = request.to_desc_pos()

    with FairinoClient(settings.fairino_robot_ip) as client:
        joint_pos_ref = _resolve_joint_pos_ref(client, request.joint_pos_ref)
        result = client.get_inverse_kin_has_solution(
            type=request.type,
            desc_pos=desc_pos,
            joint_pos_ref=joint_pos_ref,
        )

    message = None
    if result.error_code != 0:
        message = "GetInverseKinHasSolution returned a non-zero error code."

    return InverseKinHasSolutionResponse(
        robot_ip=settings.fairino_robot_ip,
        type=request.type,
        desc_pos=desc_pos,
        joint_pos_ref=joint_pos_ref,
        has_solution=result.has_solution,
        error_code=result.error_code,
        message=message,
    )
