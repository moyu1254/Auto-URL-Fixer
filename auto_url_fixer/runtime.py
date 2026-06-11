from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path


APP_DIR_NAME = "AutoURLFixer"
PID_FILE_NAME = "auto_url_fixer.pid"
STOP_FILE_NAME = "stop.flag"
STARTUP_ENTRY_NAME = "Auto URL Fixer.vbs"


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


def clear_pid_file() -> None:
    pid_file = get_pid_file()
    if pid_file.exists():
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


def is_running_instance() -> bool:
    return bool(_collect_target_pids())


def start_watcher_instance(config_path: Path | None = None) -> bool:
    if is_running_instance():
        return False

    command = _build_watcher_command(config_path)
    create_no_window = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    detached_process = getattr(subprocess, "DETACHED_PROCESS", 0)
    subprocess.Popen(
        command,
        cwd=get_application_dir(),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=create_no_window | detached_process,
    )
    return True


def stop_running_instance(timeout_seconds: float = 2.0) -> bool:
    request_stop()

    target_pids = _collect_target_pids()
    if not target_pids:
        clear_stop_request()
        return False

    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if not any(is_process_running(pid) for pid in target_pids):
            clear_stop_request()
            unregister_current_process()
            return True
        time.sleep(0.1)

    for pid in target_pids:
        if is_process_running(pid):
            _terminate_process(pid)

    clear_stop_request()
    clear_pid_file()
    return not any(is_process_running(pid) for pid in target_pids)


def enable_startup() -> Path:
    startup_path = get_startup_entry_path()
    startup_path.parent.mkdir(parents=True, exist_ok=True)
    startup_path.write_text(build_startup_vbs(), encoding="utf-8")
    return startup_path


def disable_startup() -> bool:
    startup_path = get_startup_entry_path()
    if startup_path.exists():
        startup_path.unlink()
        return True
    return False


def get_startup_entry_path() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        base_dir = Path(appdata)
    else:
        base_dir = Path.home() / "AppData" / "Roaming"
    return base_dir / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup" / STARTUP_ENTRY_NAME


def build_startup_vbs() -> str:
    command = get_hidden_launch_command(("--watch",))
    working_dir = get_application_dir()
    escaped_dir = str(working_dir).replace('"', '""')
    escaped_command = command.replace('"', '""')
    return (
        'Set shell = CreateObject("WScript.Shell")\n'
        f'shell.CurrentDirectory = "{escaped_dir}"\n'
        f'shell.Run "{escaped_command}", 0, False\n'
    )


def get_application_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def get_hidden_launch_command(extra_args: tuple[str, ...] = ()) -> str:
    if getattr(sys, "frozen", False):
        command = f'"{Path(sys.executable).resolve()}"'
        if extra_args:
            command = " ".join((command, *extra_args))
        return command

    base_command = (
        'cmd /c "where pyw >nul 2>nul && pyw -3 -m auto_url_fixer'
        ' || where pythonw >nul 2>nul && pythonw -m auto_url_fixer'
        ' || where py >nul 2>nul && py -3 -m auto_url_fixer'
        ' || python -m auto_url_fixer'
    )
    if extra_args:
        base_command += " " + " ".join(extra_args)
    return base_command + '"'


def _collect_target_pids() -> set[int]:
    target_pids: set[int] = set()
    current_pid = os.getpid()

    pid = read_pid()
    if pid is not None and pid != current_pid and is_process_running(pid):
        target_pids.add(pid)

    for candidate_pid in _list_watcher_process_ids_by_command_line():
        if candidate_pid != current_pid and is_process_running(candidate_pid):
            target_pids.add(candidate_pid)

    return target_pids


def _build_watcher_command(config_path: Path | None = None) -> list[str]:
    if getattr(sys, "frozen", False):
        command = [str(Path(sys.executable).resolve()), "--watch"]
    else:
        command = [sys.executable, "-m", "auto_url_fixer", "--watch"]

    if config_path is not None:
        command.extend(("--config", str(config_path)))

    return command


def _list_watcher_process_ids_by_command_line() -> set[int]:
    create_no_window = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    script = (
        "Get-CimInstance Win32_Process | "
        "Where-Object { $_.CommandLine -and $_.CommandLine -match '--watch' -and "
        "($_.CommandLine -match 'Auto URL Fixer|auto_url_fixer') } | "
        "ForEach-Object { $_.ProcessId }"
    )
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True,
            text=True,
            check=False,
            creationflags=create_no_window,
        )
    except OSError:
        return set()

    if result.returncode != 0:
        return set()

    pids: set[int] = set()
    for line in result.stdout.splitlines():
        try:
            pids.add(int(line.strip()))
        except ValueError:
            continue
    return pids


def _terminate_process(pid: int) -> None:
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        pass
