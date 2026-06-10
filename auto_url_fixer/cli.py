from __future__ import annotations

import argparse
from pathlib import Path

from .clipboard import ClipboardError, create_clipboard
from .config import load_config
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
        print(f"Clipboard initialization failed: {exc}")
        return 1

    watcher = ClipboardWatcher(
        clipboard=clipboard,
        rules=config.enabled_rules,
        poll_interval_seconds=config.poll_interval_seconds,
        log_rewrites=config.log_rewrites,
    )

    try:
        if args.once:
            changed = watcher.rewrite_current_clipboard_once()
            if not changed:
                print("No supported URL found in the current clipboard.")
            return 0

        print("Auto URL Fixer is running. Press Ctrl+C to stop.")
        watcher.run_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        clipboard.close()

    return 0
