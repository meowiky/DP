from __future__ import annotations

import sys
from pathlib import Path

from robot_api.config import settings


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def configure_fairino_sdk() -> Path:
    sdk_root = _project_root() / "fairino-python-sdk-2.2.3_robot3.9.3"
    package_dir = sdk_root / "fairino"

    if not package_dir.exists():
        raise RuntimeError(
            f"FAIRINO SDK package directory not found: {package_dir}. "
            "Check that the bundled FAIRINO SDK folder exists in the project."
        )

    sdk_root_str = str(sdk_root)
    if sdk_root_str not in sys.path:
        sys.path.insert(0, sdk_root_str)

    return sdk_root
