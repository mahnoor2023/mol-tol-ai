from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build_wheel import build_sdk_wheel


def test_offline_wheel_contains_only_the_sdk(tmp_path: Path) -> None:
    wheel_path = build_sdk_wheel(tmp_path)
    assert wheel_path.name == "mol_tol_sdk-0.4.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel_path) as wheel:
        names = wheel.namelist()
    assert "mol_tol_sdk/__init__.py" in names
    assert not any("mol_tol_core" in name or "mol_tol_agents" in name for name in names)


def test_existing_conflicting_wheel_is_not_overwritten(tmp_path: Path) -> None:
    wheel_path = build_sdk_wheel(tmp_path)
    wheel_path.write_bytes(b"owner data")
    try:
        build_sdk_wheel(tmp_path)
    except FileExistsError:
        pass
    else:
        raise AssertionError("conflicting wheel should not be overwritten")
    assert wheel_path.read_bytes() == b"owner data"
