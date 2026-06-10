from __future__ import annotations

import ctypes
import sys
import tkinter as tk
from tkinter import TclError
from typing import Protocol


class ClipboardError(RuntimeError):
    """Raised when the system clipboard cannot be read or written."""


class Clipboard(Protocol):
    def get_text(self) -> str | None: ...

    def set_text(self, text: str) -> None: ...

    def close(self) -> None: ...


def create_clipboard() -> Clipboard:
    if sys.platform == "win32":
        return WindowsClipboard()
    return TkClipboard()


class WindowsClipboard:
    CF_UNICODETEXT = 13
    GMEM_MOVEABLE = 0x0002

    def __init__(self) -> None:
        self._user32 = ctypes.WinDLL("user32", use_last_error=True)
        self._kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._configure_api()

    def get_text(self) -> str | None:
        if not self._user32.OpenClipboard(None):
            return None

        try:
            handle = self._user32.GetClipboardData(self.CF_UNICODETEXT)
            if not handle:
                return None

            pointer = self._kernel32.GlobalLock(handle)
            if not pointer:
                return None

            try:
                return ctypes.wstring_at(pointer)
            finally:
                self._kernel32.GlobalUnlock(handle)
        finally:
            self._user32.CloseClipboard()

    def set_text(self, text: str) -> None:
        data = (text + "\0").encode("utf-16-le")
        handle = self._kernel32.GlobalAlloc(self.GMEM_MOVEABLE, len(data))
        if not handle:
            raise ClipboardError("GlobalAlloc failed.")

        pointer = self._kernel32.GlobalLock(handle)
        if not pointer:
            self._kernel32.GlobalFree(handle)
            raise ClipboardError("GlobalLock failed.")

        try:
            ctypes.memmove(pointer, data, len(data))
        finally:
            self._kernel32.GlobalUnlock(handle)

        if not self._user32.OpenClipboard(None):
            self._kernel32.GlobalFree(handle)
            raise ClipboardError("OpenClipboard failed.")

        try:
            if not self._user32.EmptyClipboard():
                raise ClipboardError("EmptyClipboard failed.")
            if not self._user32.SetClipboardData(self.CF_UNICODETEXT, handle):
                raise ClipboardError("SetClipboardData failed.")
            handle = None
        finally:
            self._user32.CloseClipboard()
            if handle:
                self._kernel32.GlobalFree(handle)

    def close(self) -> None:
        return None

    def _configure_api(self) -> None:
        self._user32.OpenClipboard.argtypes = [ctypes.c_void_p]
        self._user32.OpenClipboard.restype = ctypes.c_bool
        self._user32.CloseClipboard.argtypes = []
        self._user32.CloseClipboard.restype = ctypes.c_bool
        self._user32.EmptyClipboard.argtypes = []
        self._user32.EmptyClipboard.restype = ctypes.c_bool
        self._user32.GetClipboardData.argtypes = [ctypes.c_uint]
        self._user32.GetClipboardData.restype = ctypes.c_void_p
        self._user32.SetClipboardData.argtypes = [ctypes.c_uint, ctypes.c_void_p]
        self._user32.SetClipboardData.restype = ctypes.c_void_p

        self._kernel32.GlobalAlloc.argtypes = [ctypes.c_uint, ctypes.c_size_t]
        self._kernel32.GlobalAlloc.restype = ctypes.c_void_p
        self._kernel32.GlobalFree.argtypes = [ctypes.c_void_p]
        self._kernel32.GlobalFree.restype = ctypes.c_void_p
        self._kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
        self._kernel32.GlobalLock.restype = ctypes.c_void_p
        self._kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
        self._kernel32.GlobalUnlock.restype = ctypes.c_bool


class TkClipboard:
    """Small tkinter-backed clipboard adapter.

    tkinter is part of the Python standard library and works well for a
    dependency-free Windows clipboard watcher.
    """

    def __init__(self) -> None:
        try:
            self._root = tk.Tk()
            self._root.withdraw()
        except TclError as exc:
            raise ClipboardError(str(exc)) from exc

    def get_text(self) -> str | None:
        try:
            return self._root.clipboard_get()
        except TclError:
            return None

    def set_text(self, text: str) -> None:
        try:
            self._root.clipboard_clear()
            self._root.clipboard_append(text)
            self._root.update()
        except TclError as exc:
            raise ClipboardError(str(exc)) from exc

    def close(self) -> None:
        try:
            self._root.destroy()
        except TclError:
            pass
