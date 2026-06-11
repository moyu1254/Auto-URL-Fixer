from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .clipboard import ClipboardError, create_clipboard
from .config import load_config
from .runtime import AlreadyRunningError, stop_requested, register_current_process, unregister_current_process
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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_config(args.config)

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
