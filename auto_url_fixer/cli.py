from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .clipboard import ClipboardError, create_clipboard
from .config import load_config
from .runtime import (
    AlreadyRunningError,
    disable_startup,
    enable_startup,
    get_application_dir,
    register_current_process,
    start_watcher_instance,
    stop_requested,
    stop_running_instance,
    unregister_current_process,
)
from .watcher import ClipboardWatcher


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="auto-url-fixer",
        description="Watch the clipboard and rewrite supported URLs to embed-friendly hosts.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to a JSON config file. Built-in defaults are used when omitted.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Rewrite the current clipboard content once and exit.",
    )
    parser.add_argument(
        "--stop",
        action="store_true",
        help="Stop the running Auto URL Fixer instance.",
    )
    parser.add_argument(
        "--enable-startup",
        action="store_true",
        help="Enable Auto URL Fixer at Windows logon.",
    )
    parser.add_argument(
        "--disable-startup",
        action="store_true",
        help="Disable Auto URL Fixer at Windows logon.",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Run the clipboard watcher in the current process.",
    )
    parser.add_argument(
        "--start",
        action="store_true",
        help="Start a background watcher process.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.stop:
        stopped = stop_running_instance()
        if not stopped:
            _safe_print("No running Auto URL Fixer instance was found.")
        return 0

    if args.enable_startup:
        startup_path = enable_startup()
        _safe_print(f"Startup enabled: {startup_path}")
        return 0

    if args.disable_startup:
        removed = disable_startup()
        if removed:
            _safe_print("Startup disabled.")
        else:
            _safe_print("No startup entry was found.")
        return 0

    if args.start:
        started = start_watcher_instance(args.config)
        if not started:
            _safe_print("Auto URL Fixer is already running.")
        return 0

    if not args.watch and not args.once:
        from .control_panel import run_control_panel

        return run_control_panel()

    config = load_config(_resolve_config_path(args.config))

    try:
        clipboard = create_clipboard()
    except ClipboardError as exc:
        _safe_print(f"Clipboard initialization failed: {exc}")
        return 1

    watcher = ClipboardWatcher(
        clipboard=clipboard,
        rules=config.enabled_rules,
        poll_interval_seconds=config.poll_interval_seconds,
        log_rewrites=config.log_rewrites,
        on_rewrite=_print_rewrite,
        stop_checker=stop_requested,
    )

    registered_pid: int | None = None

    try:
        if args.once:
            changed = watcher.rewrite_current_clipboard_once()
            if not changed:
                _safe_print("No supported URL found in the current clipboard.")
            return 0

        registered_pid = register_current_process()
        _safe_print("Auto URL Fixer is running. Press Ctrl+C to stop.")
        watcher.run_forever()
    except AlreadyRunningError as exc:
        _safe_print(str(exc))
        return 1
    except KeyboardInterrupt:
        _safe_print("\nStopped.")
    finally:
        unregister_current_process(registered_pid)
        clipboard.close()

    return 0


def _print_rewrite(original: str, rewritten: str) -> None:
    _safe_print(f"Rewritten: {original} -> {rewritten}")


def _safe_print(message: str) -> None:
    stream = sys.stdout
    if stream is None:
        return
    print(message, file=stream)


def _resolve_config_path(path: Path | None) -> Path | None:
    if path is not None:
        return path

    app_config = get_application_dir() / "config.json"
    if app_config.exists():
        return app_config

    return None
