from __future__ import annotations

import time
from collections.abc import Callable
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
        on_rewrite: Callable[[str, str], None] | None = None,
        stop_checker: Callable[[], bool] | None = None,
    ) -> None:
        self._clipboard = clipboard
        self._rules = rules
        self._poll_interval_seconds = poll_interval_seconds
        self._log_rewrites = log_rewrites
        self._on_rewrite = on_rewrite
        self._stop_checker = stop_checker
        self._last_seen_text: str | None = None

    def rewrite_current_clipboard_once(self) -> bool:
        text = self._clipboard.get_text()
        if text is None:
            return False

        rewritten, changed = rewrite_text(text, self._rules)
        if changed:
            self._clipboard.set_text(rewritten)
            self._last_seen_text = rewritten
            self._emit_rewrite(text, rewritten)
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
                    self._emit_rewrite(text, rewritten)
                else:
                    self._last_seen_text = text
            if self.should_stop():
                return
            time.sleep(self._poll_interval_seconds)

    def _emit_rewrite(self, original: str, rewritten: str) -> None:
        if self._log_rewrites and self._on_rewrite is not None:
            self._on_rewrite(original, rewritten)

    def should_stop(self) -> bool:
        return self._stop_checker is not None and self._stop_checker()
