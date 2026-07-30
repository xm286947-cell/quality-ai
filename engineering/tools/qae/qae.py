#!/usr/bin/env python3
"""QAE V1.0 - lightweight increment installer for QUALITY_AGENT."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

QAE_VERSION = "1.0.0"
PROJECT_NAME = "quality-ai"
STATE_DIR = Path("engineering/tools/qae/.state")
BACKUP_DIR = Path("engineering/tools/qae/.backups")
STATE_FILE = STATE_DIR / "last_install.json"


class QAEError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repository_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        readme = candidate / "README.md"
        if readme.is_file():
            try:
                if "# QUALITY_AGENT" in readme.read_text(encoding="utf-8", errors="ignore"):
                    return candidate
            except OSError:
                pass
    raise QAEError("当前目录不在 QUALITY_AGENT（quality-ai）仓库中。")


def safe_relative_path(raw: str) -> Path:
    if not isinstance(raw, str) or not raw.strip():
        raise QAEError("Manifest 中存在空文件路径。")
    normalized = raw.replace("\\", "/")
    pure = PurePosixPath(normalized)
    if pure.is_absolute() or ".." in pure.parts or "." in pure.parts:
        raise QAEError(f"非法目标路径：{raw}")
    if pure.parts and pure.parts[0].endswith(":"):
        raise QAEError(f"非法目标路径：{raw}")
    return Path(*pure.parts)


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise QAEError(f"文件不存在：{path}") from exc
    except json.JSONDecodeError as exc:
        raise QAEError(f"JSON 格式错误：{path}（{exc}）") from exc
    if not isinstance(data, dict):
        raise QAEError(f"JSON 根节点必须是对象：{path}")
    return data


def manifest_paths(manifest: dict[str, Any]) -> list[Path]:
    required = ["package_name", "target_project", "target_scope", "version", "milestone", "files"]
    missing = [key for key in required if key not in manifest]
    if missing:
        raise QAEError("Manifest 缺少字段：" + ", ".join(missing))
    if manifest["target_project"] != PROJECT_NAME:
        raise QAEError(f"target_project 必须是 {PROJECT_NAME}。")
    files = manifest["files"]
    if not isinstance(files, list) or not files:
        raise QAEError("Manifest files 必须是非空数组。")
    result: list[Path] = []
    seen: set[str] = set()
    for entry in files:
        raw = entry if isinstance(entry, str) else entry.get("path") if isinstance(entry, dict) else None
        path = safe_relative_path(raw)
        key = path.as_posix()
        if key in seen:
            raise QAEError(f"Manifest 包含重复文件：{key}")
        seen.add(key)
        result.append(path)
    return result


def safe_extract(zip_path: Path, destination: Path) -> None:
    try:
        archive = zipfile.ZipFile(zip_path)
    except (FileNotFoundError, zipfile.BadZipFile) as exc:
        raise QAEError(f"无法读取增量包：{zip_path}") from exc
    with archive:
        for member in archive.infolist():
            path = safe_relative_path(member.filename.rstrip("/")) if member.filename.rstrip("/") else None
            if path is None:
                continue
            target = (destination / path).resolve()
            if destination.resolve() not in [target, *target.parents]:
                raise QAEError(f"ZIP 包含越界路径：{member.filename}")
        archive.extractall(destination)


def write_state(root: Path, state: dict[str, Any]) -> None:
    target = root / STATE_FILE
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def read_state(root: Path) -> dict[str, Any]:
    return load_json(root / STATE_FILE)


def perform_rollback(root: Path, state: dict[str, Any], update_state: bool = True) -> None:
    backup_root = root / state["backup_dir"]
    errors: list[str] = []
    for raw in reversed(state.get("installed_files", [])):
        rel = safe_relative_path(raw)
        target = root / rel
        backup = backup_root / "files" / rel
        existed = raw in state.get("overwritten_files", [])
        try:
            if existed:
                if not backup.is_file():
                    raise QAEError(f"备份缺失：{backup}")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup, target)
            elif target.exists():
                target.unlink()
        except (OSError, QAEError) as exc:
            errors.append(f"{raw}: {exc}")
    # Clean empty directories created by installation, but never cross repository root.
    for raw in reversed(state.get("installed_files", [])):
        parent = (root / safe_relative_path(raw)).parent
        while parent != root and root in parent.parents:
            try:
                parent.rmdir()
            except OSError:
                break
            parent = parent.parent
    if errors:
        raise QAEError("回滚未完整完成：\n" + "\n".join(errors))
    if update_state:
        state["status"] = "rolled_back"
        state["rolled_back_at"] = datetime.now().isoformat(timespec="seconds")
        write_state(root, state)


def verify_state(root: Path, state: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    expected = state.get("installed_hashes", {})
    for raw in state.get("installed_files", []):
        path = root / safe_relative_path(raw)
        if not path.is_file():
            failures.append(f"MISSING {raw}")
            continue
        expected_hash = expected.get(raw)
        if expected_hash and sha256(path) != expected_hash:
            failures.append(f"CHANGED {raw}")
    return failures


def command_install(package: str) -> int:
    root = repository_root()
    package_path = Path(package).expanduser().resolve()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    with tempfile.TemporaryDirectory(prefix="qae_") as temp_name:
        temp = Path(temp_name)
        safe_extract(package_path, temp)
        manifest_file = temp / "manifest.json"
        files_root = temp / "files"
        manifest = load_json(manifest_file)
        paths = manifest_paths(manifest)
        if not files_root.is_dir():
            raise QAEError("增量包缺少 files/ 目录。")
        for rel in paths:
            if not (files_root / rel).is_file():
                raise QAEError(f"增量包缺少 Manifest 声明文件：{rel.as_posix()}")

        backup_rel = BACKUP_DIR / timestamp
        backup_root = root / backup_rel
        (backup_root / "files").mkdir(parents=True, exist_ok=False)
        shutil.copy2(manifest_file, backup_root / "manifest.json")

        overwritten: list[str] = []
        installed: list[str] = []
        state: dict[str, Any] = {
            "qae_version": QAE_VERSION,
            "package_name": manifest["package_name"],
            "target_scope": manifest["target_scope"],
            "version": manifest["version"],
            "milestone": manifest["milestone"],
            "installed_at": datetime.now().isoformat(timespec="seconds"),
            "status": "installing",
            "backup_dir": backup_rel.as_posix(),
            "overwritten_files": overwritten,
            "installed_files": installed,
            "installed_hashes": {},
        }
        write_state(root, state)
        try:
            for rel in paths:
                source = files_root / rel
                target = root / rel
                raw = rel.as_posix()
                if target.exists():
                    if not target.is_file():
                        raise QAEError(f"目标路径不是文件：{raw}")
                    backup = backup_root / "files" / rel
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(target, backup)
                    overwritten.append(raw)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                installed.append(raw)
                state["installed_hashes"][raw] = sha256(target)
                write_state(root, state)
            failures = verify_state(root, state)
            if failures:
                raise QAEError("安装后校验失败：\n" + "\n".join(failures))
            state["status"] = "installed"
            state["verified_at"] = datetime.now().isoformat(timespec="seconds")
            write_state(root, state)
        except Exception:
            try:
                perform_rollback(root, state, update_state=False)
                state["status"] = "failed_rolled_back"
                write_state(root, state)
            except Exception as rollback_exc:
                state["status"] = "failed_rollback_incomplete"
                state["rollback_error"] = str(rollback_exc)
                write_state(root, state)
            raise

    print("QAE Install   PASS")
    print(f"Package       {manifest['package_name']}")
    print(f"Files         {len(paths)}")
    print(f"Backup        {backup_rel.as_posix()}")
    return 0


def command_verify() -> int:
    root = repository_root()
    state = read_state(root)
    if state.get("status") != "installed":
        raise QAEError(f"最近一次安装状态不可校验：{state.get('status', 'unknown')}")
    failures = verify_state(root, state)
    print("Repository    PASS")
    print("State         PASS")
    if failures:
        print("Files         FAIL")
        for failure in failures:
            print(f"  {failure}")
        return 1
    print("Files         PASS")
    print("Verify        PASS")
    return 0


def command_rollback() -> int:
    root = repository_root()
    state = read_state(root)
    if state.get("status") != "installed":
        raise QAEError(f"最近一次安装状态不可回滚：{state.get('status', 'unknown')}")
    perform_rollback(root, state)
    print("QAE Rollback  PASS")
    print(f"Package       {state.get('package_name', 'unknown')}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="qae", description="QAE V1.0 increment installer")
    parser.add_argument("--version", action="version", version=f"QAE {QAE_VERSION}")
    sub = parser.add_subparsers(dest="command", required=True)
    install = sub.add_parser("install", help="安装标准增量包")
    install.add_argument("package", help="增量包 ZIP 路径")
    sub.add_parser("verify", help="校验最近一次安装")
    sub.add_parser("rollback", help="回滚最近一次安装")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "install":
            return command_install(args.package)
        if args.command == "verify":
            return command_verify()
        if args.command == "rollback":
            return command_rollback()
        raise QAEError(f"未知命令：{args.command}")
    except QAEError as exc:
        print(f"QAE ERROR: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"QAE ERROR: 文件系统操作失败：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
