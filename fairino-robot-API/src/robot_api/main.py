from fastapi import FastAPI, HTTPException

from robot_api.config import settings
from robot_api.fairino_client import FairinoCommandError, FairinoSDKUnavailableError
from robot_api.models import CartesianMoveRequest, MoveResponse, RobotStateResponse
from robot_api.service import get_robot_state, move_cartesian

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
