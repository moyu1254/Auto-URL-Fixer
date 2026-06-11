from __future__ import annotations

import os
from pathlib import Path


APP_DIR_NAME = "AutoURLFixer"
PID_FILE_NAME = "auto_url_fixer.pid"
STOP_FILE_NAME = "stop.flag"


class AlreadyRunningError(RuntimeError):
    """Raised when another watcher process is already running."""


def get_runtime_dir() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        base_dir = Path(local_app_data)
    else:
        base_dir = Path.home() / "AppData" / "Local"
    return base_dir / APP_DIR_NAME


def get_pid_file() -> Path:
    return get_runtime_dir() / PID_FILE_NAME


def get_stop_file() -> Path:
    return get_runtime_dir() / STOP_FILE_NAME


def register_current_process() -> int:
    pid = os.getpid()
    runtime_dir = get_runtime_dir()
    runtime_dir.mkdir(parents=True, exist_ok=True)
    clear_stop_request()

    existing_pid = read_pid()
    if existing_pid is not None and existing_pid != pid and is_process_running(existing_pid):
        raise AlreadyRunningError(f"Auto URL Fixer is already running (PID: {existing_pid}).")

    get_pid_file().write_text(str(pid), encoding="utf-8")
    return pid


def unregister_current_process(pid: int | None = None) -> None:
    expected_pid = os.getpid() if pid is None else pid
    pid_file = get_pid_file()
    current_pid = read_pid()
    if current_pid == expected_pid and pid_file.exists():
        pid_file.unlink()


def read_pid() -> int | None:
    pid_file = get_pid_file()
    if not pid_file.exists():
        return None

    try:
        return int(pid_file.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def request_stop() -> None:
    runtime_dir = get_runtime_dir()
    runtime_dir.mkdir(parents=True, exist_ok=True)
    get_stop_file().write_text("stop", encoding="utf-8")


def clear_stop_request() -> None:
    stop_file = get_stop_file()
    if stop_file.exists():
        stop_file.unlink()


def stop_requested() -> bool:
    return get_stop_file().exists()


def is_process_running(pid: int) -> bool:
    if pid <= 0:
        return False

    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True
