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


class PartialCartesianMoveRequest(BaseModel):
    x: float | None = Field(None, description="Target X in mm")
    y: float | None = Field(None, description="Target Y in mm")
    z: float | None = Field(None, description="Target Z in mm")
    rx: float | None = Field(None, description="Target RX in degrees")
    ry: float | None = Field(None, description="Target RY in degrees")
    rz: float | None = Field(None, description="Target RZ in degrees")
    tool: int | None = Field(None, ge=0, le=14, description="Tool frame index")
    user: int | None = Field(None, ge=0, le=14, description="Workpiece/user frame index")
    vel: float | None = Field(None, gt=0, le=100, description="Speed percentage")

    @field_validator("tool", "user")
    @classmethod
    def validate_frame_index(cls, value: int | None) -> int | None:
        return value


class JointMoveRequest(BaseModel):
    j1: float = Field(..., description="Target joint 1 in degrees")
    j2: float = Field(..., description="Target joint 2 in degrees")
    j3: float = Field(..., description="Target joint 3 in degrees")
    j4: float = Field(..., description="Target joint 4 in degrees")
    j5: float = Field(..., description="Target joint 5 in degrees")
    j6: float = Field(..., description="Target joint 6 in degrees")
    tool: int | None = Field(None, ge=0, le=14, description="Tool frame index")
    user: int | None = Field(None, ge=0, le=14, description="Workpiece/user frame index")
    vel: float | None = Field(None, gt=0, le=100, description="Speed percentage")

    def to_joint_pos(self) -> list[float]:
        return [self.j1, self.j2, self.j3, self.j4, self.j5, self.j6]


class InverseKinRequest(BaseModel):
    x: float = Field(..., description="Target X in mm")
    y: float = Field(..., description="Target Y in mm")
    z: float = Field(..., description="Target Z in mm")
    rx: float = Field(..., description="Target RX in degrees")
    ry: float = Field(..., description="Target RY in degrees")
    rz: float = Field(..., description="Target RZ in degrees")
    type: int = Field(0, ge=0, le=2, description="0=absolute/base, 1=relative/base, 2=relative/tool")
    joint_pos_ref: list[float] | None = Field(
        None,
        min_length=6,
        max_length=6,
        description="Reference joint position [j1, j2, j3, j4, j5, j6] in degrees. If omitted, the current robot joint state is used.",
    )

    def to_desc_pos(self) -> list[float]:
        return [self.x, self.y, self.z, self.rx, self.ry, self.rz]


class CartesianViaJointMoveRequest(InverseKinRequest):
    tool: int | None = Field(None, ge=0, le=14, description="Tool frame index")
    user: int | None = Field(None, ge=0, le=14, description="Workpiece/user frame index")
    vel: float | None = Field(None, gt=0, le=100, description="Speed percentage")


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


class JointMoveResponse(BaseModel):
    success: bool
    dry_run: bool
    robot_ip: str
    command: str
    joint_pos: list[float]
    tool: int
    user: int
    vel: float
    error_code: int | None = None
    message: str


class CartesianViaJointMoveResponse(BaseModel):
    success: bool
    dry_run: bool
    robot_ip: str
    command: str
    desc_pos: list[float]
    joint_pos_ref: list[float]
    joint_pos: list[float]
    tool: int
    user: int
    vel: float
    ik_error_code: int
    move_error_code: int | None = None
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


class InverseKinHasSolutionResponse(BaseModel):
    robot_ip: str
    type: int
    desc_pos: list[float]
    joint_pos_ref: list[float]
    has_solution: bool
    error_code: int
    message: str | None = None


class InverseKinRefResponse(BaseModel):
    robot_ip: str
    type: int
    desc_pos: list[float]
    joint_pos_ref: list[float]
    error_code: int
    joint_pos: list[float] | None = None
    message: str | None = None
