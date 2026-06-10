from __future__ import annotations

import time
from typing import Protocol

from .config import Rule
from .rewriter import rewrite_text


class Clipboard(Protocol):
    def get_text(self) -> str | None: ...

    def set_text(self, text: str) -> None: ...


class ClipboardWatcher:
    def __init__(
        self,
        clipboard: Clipboard,
        rules: tuple[Rule, ...],
        poll_interval_seconds: float = 0.5,
        log_rewrites: bool = True,
    ) -> None:
        self._clipboard = clipboard
        self._rules = rules
        self._poll_interval_seconds = poll_interval_seconds
        self._log_rewrites = log_rewrites
        self._last_seen_text: str | None = None

    def rewrite_current_clipboard_once(self) -> bool:
        text = self._clipboard.get_text()
        if text is None:
            return False

        rewritten, changed = rewrite_text(text, self._rules)
        if changed:
            self._clipboard.set_text(rewritten)
            self._last_seen_text = rewritten
            if self._log_rewrites:
                print(f"Rewritten: {text} -> {rewritten}")
        else:
            self._last_seen_text = text
        return changed

    def run_forever(self) -> None:
        while True:
            text = self._clipboard.get_text()
            if text is not None and text != self._last_seen_text:
                rewritten, changed = rewrite_text(text, self._rules)
                if changed:
                    self._clipboard.set_text(rewritten)
                    self._last_seen_text = rewritten
                    if self._log_rewrites:
                        print(f"Rewritten: {text} -> {rewritten}")
                else:
                    self._last_seen_text = text
            time.sleep(self._poll_interval_seconds)

