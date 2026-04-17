from __future__ import annotations

from dataclasses import dataclass

from robot_api.config import settings
from robot_api.sdk_loader import configure_fairino_sdk


class FairinoSDKUnavailableError(RuntimeError):
    """Raised when the FAIRINO SDK is not installed."""


class FairinoCommandError(RuntimeError):
    """Raised when the robot controller returns a non-zero error code."""

    def __init__(self, message: str, *, error_code: int | None = None, context: dict | None = None) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.context = context or {}


@dataclass
class MoveResult:
    error_code: int
    desc_pos: list[float]
    tool: int
    user: int
    vel: float


@dataclass
class JointMoveResult:
    error_code: int
    joint_pos: list[float]
    tool: int
    user: int
    vel: float


@dataclass
class RobotState:
    realtime_available: bool
    enabled: int
    robot_mode: int
    program_state: int
    robot_state: int
    emergency_stop: int
    safety_stop: list[int]
    collision_state: int
    motion_done: int
    tool: int
    user: int
    main_error_code: int
    sub_error_code: int
    tcp_pose: list[float]
    joint_pos: list[float]
    message: str | None = None


@dataclass
class ToolState:
    active_tool: int | None
    active_tcp_offset: list[float] | None
    current_tool_coord: list[float] | None
    tool_0_coord: list[float] | None
    tool_1_coord: list[float] | None
    message: str | None = None


@dataclass
class InverseKinResult:
    error_code: int
    joint_pos: list[float] | None


@dataclass
class InverseKinHasSolutionResult:
    error_code: int
    has_solution: bool


class FairinoClient:
    def __init__(self, robot_ip: str) -> None:
        self.robot_ip = robot_ip
        self._robot = None

    def connect(self) -> None:
        try:
            configure_fairino_sdk()
            from fairino import Robot
        except ModuleNotFoundError as exc:
            raise FairinoSDKUnavailableError(
                "The 'fairino' package could not be imported. "
                "Check that the bundled FAIRINO SDK is present and your Python version is supported."
            ) from exc
        except RuntimeError as exc:
            raise FairinoSDKUnavailableError(str(exc)) from exc

        Robot.RPC.ROBOT_RPC_PORT = settings.fairino_rpc_port
        Robot.RPC.ROBOT_REALTIME_PORT = settings.fairino_realtime_port
        self._robot = Robot.RPC(self.robot_ip)
        if self._robot is None:
            raise ConnectionError(f"Failed to connect to robot controller at {self.robot_ip}.")

    def close(self) -> None:
        if self._robot is None:
            return
        close_rpc = getattr(self._robot, "CloseRPC", None)
        if callable(close_rpc):
            close_rpc()
        self._robot = None

    @staticmethod
    def _unpack_sdk_state(result: object) -> tuple[int, object | None]:
        if isinstance(result, tuple):
            if len(result) == 2:
                return int(result[0]), result[1]
            if len(result) > 0:
                return int(result[0]), list(result[1:])
        return int(result), None

    def _realtime_available(self) -> bool:
        if self._robot is None:
            return False
        state_pkg = getattr(self._robot, "robot_state_pkg", None)
        return state_pkg is not None and not isinstance(state_pkg, type)

    def get_state(self) -> RobotState:
        if self._robot is None:
            raise RuntimeError("Robot is not connected.")

        if not self._realtime_available():
            return RobotState(
                realtime_available=False,
                enabled=-1,
                robot_mode=-1,
                program_state=-1,
                robot_state=-1,
                emergency_stop=-1,
                safety_stop=[-1, -1],
                collision_state=-1,
                motion_done=-1,
                tool=-1,
                user=-1,
                main_error_code=-1,
                sub_error_code=-1,
                tcp_pose=[],
                joint_pos=[],
                message=(
                    "Realtime state socket is unavailable, so controller state feedback "
                    "cannot be read through the SDK from this host."
                ),
            )

        error_code, tcp_pose = self._unpack_sdk_state(self._robot.GetActualTCPPose())
        error_code_joints, joint_pos = self._unpack_sdk_state(self._robot.GetActualJointPosDegree())
        error_code_errors, error_codes = self._unpack_sdk_state(self._robot.GetRobotErrorCode())
        error_code_safety, safety_stop = self._unpack_sdk_state(self._robot.GetSafetyStopState())
        error_code_estop, emergency_stop = self._unpack_sdk_state(self._robot.GetRobotEmergencyStopState())
        error_code_motion, motion_done = self._unpack_sdk_state(self._robot.GetRobotMotionDone())

        state_pkg = self._robot.robot_state_pkg
        return RobotState(
            realtime_available=True,
            enabled=int(state_pkg.rbtEnableState),
            robot_mode=int(state_pkg.robot_mode),
            program_state=int(state_pkg.program_state),
            robot_state=int(state_pkg.robot_state),
            emergency_stop=int(emergency_stop) if emergency_stop is not None else -1,
            safety_stop=[int(safety_stop[0]), int(safety_stop[1])] if safety_stop is not None else [-1, -1],
            collision_state=int(state_pkg.collisionState),
            motion_done=int(motion_done) if motion_done is not None else -1,
            tool=int(state_pkg.tool),
            user=int(state_pkg.user),
            main_error_code=int(error_codes[0]) if error_codes is not None else -1,
            sub_error_code=int(error_codes[1]) if error_codes is not None else -1,
            tcp_pose=[float(value) for value in tcp_pose] if tcp_pose is not None else [],
            joint_pos=[float(value) for value in joint_pos] if joint_pos is not None else [],
            message=(
                "Some realtime fields could not be read."
                if any(
                    code != 0
                    for code in (
                        error_code,
                        error_code_joints,
                        error_code_errors,
                        error_code_safety,
                        error_code_estop,
                        error_code_motion,
                    )
                )
                else None
            ),
        )

    def get_tool_state(self) -> ToolState:
        if self._robot is None:
            raise RuntimeError("Robot is not connected.")

        active_tool_error, active_tool = self._unpack_sdk_state(self._robot.GetActualTCPNum())
        tcp_offset_error, tcp_offset = self._unpack_sdk_state(self._robot.GetTCPOffset())
        current_tool_error, current_tool_coord = self._unpack_sdk_state(self._robot.GetCurToolCoord())
        tool_0_error, tool_0_coord = self._unpack_sdk_state(self._robot.GetToolCoordWithID(0))
        tool_1_error, tool_1_coord = self._unpack_sdk_state(self._robot.GetToolCoordWithID(1))

        errors = (
            active_tool_error,
            tcp_offset_error,
            current_tool_error,
            tool_0_error,
            tool_1_error,
        )
        message = None
        if any(code != 0 for code in errors):
            message = (
                "Some tool coordinate fields could not be read. "
                f"error_codes={list(errors)}"
            )

        return ToolState(
            active_tool=int(active_tool) if active_tool is not None else None,
            active_tcp_offset=[float(value) for value in tcp_offset] if tcp_offset is not None else None,
            current_tool_coord=[float(value) for value in current_tool_coord] if current_tool_coord is not None else None,
            tool_0_coord=[float(value) for value in tool_0_coord] if tool_0_coord is not None else None,
            tool_1_coord=[float(value) for value in tool_1_coord] if tool_1_coord is not None else None,
            message=message,
        )

    def get_inverse_kin_ref(
        self,
        type: int,
        desc_pos: list[float],
        joint_pos_ref: list[float],
    ) -> InverseKinResult:
        if self._robot is None:
            raise RuntimeError("Robot is not connected.")

        error_code, joint_pos = self._unpack_sdk_state(
            self._robot.GetInverseKinRef(type, desc_pos, joint_pos_ref)
        )
        return InverseKinResult(
            error_code=error_code,
            joint_pos=[float(value) for value in joint_pos] if joint_pos is not None else None,
        )

    def get_inverse_kin_has_solution(
        self,
        type: int,
        desc_pos: list[float],
        joint_pos_ref: list[float],
    ) -> InverseKinHasSolutionResult:
        if self._robot is None:
            raise RuntimeError("Robot is not connected.")

        error_code, has_solution = self._unpack_sdk_state(
            self._robot.GetInverseKinHasSolution(type, desc_pos, joint_pos_ref)
        )
        return InverseKinHasSolutionResult(
            error_code=error_code,
            has_solution=bool(has_solution) if has_solution is not None else False,
        )

    def move_cartesian(
        self,
        desc_pos: list[float],
        tool: int,
        user: int,
        vel: float,
    ) -> MoveResult:
        if self._robot is None:
            raise RuntimeError("Robot is not connected.")

        error_code = self._robot.MoveCart(
            desc_pos=desc_pos,
            tool=tool,
            user=user,
            vel=vel,
        )
        if error_code != 0:
            context = self.get_state()
            if not context.realtime_available:
                raise FairinoCommandError(
                    (
                        f"MoveCart failed with error code {error_code}. "
                        f"Realtime diagnostics are unavailable: {context.message}"
                    ),
                    error_code=error_code,
                    context={"realtime_available": False, "message": context.message},
                )
            summary = (
                f"MoveCart failed with error code {error_code}. "
                f"Controller error=[{context.main_error_code}, {context.sub_error_code}], "
                f"enabled={context.enabled}, mode={context.robot_mode}, "
                f"state={context.robot_state}, estop={context.emergency_stop}, "
                f"safety_stop={context.safety_stop}, collision={context.collision_state}."
            )
            raise FairinoCommandError(
                summary,
                error_code=error_code,
                context={
                    "enabled": context.enabled,
                    "robot_mode": context.robot_mode,
                    "program_state": context.program_state,
                    "robot_state": context.robot_state,
                    "emergency_stop": context.emergency_stop,
                    "safety_stop": context.safety_stop,
                    "collision_state": context.collision_state,
                    "motion_done": context.motion_done,
                    "tool": context.tool,
                    "user": context.user,
                    "main_error_code": context.main_error_code,
                    "sub_error_code": context.sub_error_code,
                    "tcp_pose": context.tcp_pose,
                    "joint_pos": context.joint_pos,
                },
            )

        return MoveResult(
            error_code=error_code,
            desc_pos=desc_pos,
            tool=tool,
            user=user,
            vel=vel,
        )

    def move_joint(
        self,
        joint_pos: list[float],
        tool: int,
        user: int,
        vel: float,
    ) -> JointMoveResult:
        if self._robot is None:
            raise RuntimeError("Robot is not connected.")

        error_code = self._robot.MoveJ(
            joint_pos=joint_pos,
            tool=tool,
            user=user,
            vel=vel,
        )
        if error_code != 0:
            context = self.get_state()
            if not context.realtime_available:
                raise FairinoCommandError(
                    (
                        f"MoveJ failed with error code {error_code}. "
                        f"Realtime diagnostics are unavailable: {context.message}"
                    ),
                    error_code=error_code,
                    context={"realtime_available": False, "message": context.message},
                )
            summary = (
                f"MoveJ failed with error code {error_code}. "
                f"Controller error=[{context.main_error_code}, {context.sub_error_code}], "
                f"enabled={context.enabled}, mode={context.robot_mode}, "
                f"state={context.robot_state}, estop={context.emergency_stop}, "
                f"safety_stop={context.safety_stop}, collision={context.collision_state}."
            )
            raise FairinoCommandError(
                summary,
                error_code=error_code,
                context={
                    "enabled": context.enabled,
                    "robot_mode": context.robot_mode,
                    "program_state": context.program_state,
                    "robot_state": context.robot_state,
                    "emergency_stop": context.emergency_stop,
                    "safety_stop": context.safety_stop,
                    "collision_state": context.collision_state,
                    "motion_done": context.motion_done,
                    "tool": context.tool,
                    "user": context.user,
                    "main_error_code": context.main_error_code,
                    "sub_error_code": context.sub_error_code,
                    "tcp_pose": context.tcp_pose,
                    "joint_pos": context.joint_pos,
                },
            )

        return JointMoveResult(
            error_code=error_code,
            joint_pos=joint_pos,
            tool=tool,
            user=user,
            vel=vel,
        )

    def __enter__(self) -> "FairinoClient":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
