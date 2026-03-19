from pydantic import BaseModel, Field, field_validator


class CartesianMoveRequest(BaseModel):
    x: float = Field(..., description="Target X in mm")
    y: float = Field(..., description="Target Y in mm")
    z: float = Field(..., description="Target Z in mm")
    rx: float = Field(..., description="Target RX in degrees")
    ry: float = Field(..., description="Target RY in degrees")
    rz: float = Field(..., description="Target RZ in degrees")
    tool: int | None = Field(None, ge=0, le=14, description="Tool frame index")
    user: int | None = Field(None, ge=0, le=14, description="Workpiece/user frame index")
    vel: float | None = Field(None, gt=0, le=100, description="Speed percentage")

    @field_validator("tool", "user")
    @classmethod
    def validate_frame_index(cls, value: int | None) -> int | None:
        return value

    def to_desc_pos(self) -> list[float]:
        return [self.x, self.y, self.z, self.rx, self.ry, self.rz]


class MoveResponse(BaseModel):
    success: bool
    dry_run: bool
    robot_ip: str
    command: str
    desc_pos: list[float]
    tool: int
    user: int
    vel: float
    error_code: int | None = None
    message: str


class RobotStateResponse(BaseModel):
    robot_ip: str
    realtime_available: bool
    enabled: int | None = None
    robot_mode: int | None = None
    program_state: int | None = None
    robot_state: int | None = None
    emergency_stop: int | None = None
    safety_stop: list[int] | None = None
    collision_state: int | None = None
    motion_done: int | None = None
    tool: int | None = None
    user: int | None = None
    main_error_code: int | None = None
    sub_error_code: int | None = None
    tcp_pose: list[float] | None = None
    joint_pos: list[float] | None = None
    message: str | None = None


class ToolStateResponse(BaseModel):
    robot_ip: str
    active_tool: int | None = None
    active_tcp_offset: list[float] | None = None
    current_tool_coord: list[float] | None = None
    tool_0_coord: list[float] | None = None
    tool_1_coord: list[float] | None = None
    message: str | None = None
