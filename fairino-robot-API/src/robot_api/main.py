from fastapi import FastAPI, HTTPException

from robot_api.config import settings
from robot_api.fairino_client import FairinoCommandError, FairinoSDKUnavailableError
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
from robot_api.service import (
    get_inverse_kin_has_solution,
    get_inverse_kin_ref,
    get_robot_state,
    get_tool_state,
    move_cartesian,
    move_cartesian_partial,
)

app = FastAPI(
    title="FAIRINO Robot API",
    version="0.1.0",
    description="Minimal API for sending Cartesian moves to a FAIRINO robot arm.",
)


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "robot_ip": settings.fairino_robot_ip,
        "dry_run": settings.fairino_dry_run,
    }


@app.post("/move/cartesian", response_model=MoveResponse)
def move_cartesian_endpoint(request: CartesianMoveRequest) -> MoveResponse:
    try:
        return move_cartesian(request)
    except FairinoSDKUnavailableError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ConnectionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except FairinoCommandError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/move/cartesian/partial", response_model=MoveResponse)
def move_cartesian_partial_endpoint(request: PartialCartesianMoveRequest) -> MoveResponse:
    try:
        return move_cartesian_partial(request)
    except FairinoSDKUnavailableError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ConnectionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FairinoCommandError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/robot/state", response_model=RobotStateResponse)
def robot_state_endpoint() -> RobotStateResponse:
    try:
        return get_robot_state()
    except FairinoSDKUnavailableError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ConnectionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except FairinoCommandError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/robot/tool-state", response_model=ToolStateResponse)
def robot_tool_state_endpoint() -> ToolStateResponse:
    try:
        return get_tool_state()
    except FairinoSDKUnavailableError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ConnectionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except FairinoCommandError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/robot/ik/ref", response_model=InverseKinRefResponse)
def robot_inverse_kin_ref_endpoint(request: InverseKinRequest) -> InverseKinRefResponse:
    try:
        return get_inverse_kin_ref(request)
    except FairinoSDKUnavailableError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ConnectionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FairinoCommandError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/robot/ik/has-solution", response_model=InverseKinHasSolutionResponse)
def robot_inverse_kin_has_solution_endpoint(request: InverseKinRequest) -> InverseKinHasSolutionResponse:
    try:
        return get_inverse_kin_has_solution(request)
    except FairinoSDKUnavailableError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ConnectionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FairinoCommandError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
