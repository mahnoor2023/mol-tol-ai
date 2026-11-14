"""Build the pure-Python Mol-Tol SDK wheel using only Python's standard library.

This is an offline-friendly alternative to the setuptools PEP 517 build backend.
It packages only the SDK module and refuses to overwrite a different wheel.
"""
from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import os
import tempfile
import tomllib
import zipfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]


def _record_hash(data: bytes) -> str:
    digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=")
    return "sha256=" + digest.decode("ascii")


def build_sdk_wheel(output_dir: Path | None = None) -> Path:
    metadata = tomllib.loads((PROJECT / "pyproject.toml").read_text(encoding="utf-8"))
    project = metadata["project"]
    name = project["name"]
    version = project["version"]
    requires_python = project.get("requires-python", ">=3.12")
    normalized_name = name.replace("-", "_")
    dist_info = f"{normalized_name}-{version}.dist-info"
    wheel_name = f"{normalized_name}-{version}-py3-none-any.whl"

    files: dict[str, bytes] = {}
    for source in sorted((PROJECT / "mol_tol_sdk").rglob("*.py")):
        if "__pycache__" not in source.parts:
            files[source.relative_to(PROJECT).as_posix()] = source.read_bytes()
    if not files:
        raise FileNotFoundError("SDK source package is empty")

    files[f"{dist_info}/METADATA"] = (
        "Metadata-Version: 2.1\n"
        f"Name: {name}\nVersion: {version}\nRequires-Python: {requires_python}\n"
        "Summary: Standard-library HTTP SDK for the Mol-Tol negotiation API\n\n"
    ).encode()
    files[f"{dist_info}/WHEEL"] = (
        "Wheel-Version: 1.0\nGenerator: mol-tol-sdk-offline-builder\n"
        "Root-Is-Purelib: true\nTag: py3-none-any\n"
    ).encode()

    record_name = f"{dist_info}/RECORD"
    record = io.StringIO(newline="")
    writer = csv.writer(record, lineterminator="\n")
    for filename, data in sorted(files.items()):
        writer.writerow((filename, _record_hash(data), len(data)))
    writer.writerow((record_name, "", ""))
    files[record_name] = record.getvalue().encode()

    destination = Path(output_dir) if output_dir else PROJECT / "dist"
    destination.mkdir(parents=True, exist_ok=True)
    wheel_path = destination / wheel_name
    fd, temporary = tempfile.mkstemp(prefix=".mol-tol-sdk-", suffix=".tmp", dir=destination)
    os.close(fd)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as wheel:
            for filename, data in sorted(files.items()):
                info = zipfile.ZipInfo(filename, date_time=(2020, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                wheel.writestr(info, data)
        if wheel_path.exists():
            if Path(temporary).read_bytes() != wheel_path.read_bytes():
                raise FileExistsError(f"Refusing to overwrite conflicting wheel: {wheel_path}")
            return wheel_path
        os.rename(temporary, wheel_path)
        return wheel_path
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, help="wheel output directory (defaults to SDK dist/)")
    args = parser.parse_args()
    print(build_sdk_wheel(args.output))
