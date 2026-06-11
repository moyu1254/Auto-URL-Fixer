from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from .runtime import (
    disable_startup,
    enable_startup,
    is_running_instance,
    start_watcher_instance,
    stop_running_instance,
)


def run_control_panel() -> int:
    root = tk.Tk()
    root.title("Auto URL Fixer")
    root.resizable(False, False)

    status_var = tk.StringVar()

    frame = tk.Frame(root, padx=18, pady=16)
    frame.grid(row=0, column=0)

    title = tk.Label(frame, text="Auto URL Fixer", font=("Segoe UI", 14, "bold"))
    title.grid(row=0, column=0, columnspan=2, sticky="w")

    status = tk.Label(frame, textvariable=status_var, font=("Segoe UI", 10))
    status.grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 14))

    def refresh_status() -> None:
        status_var.set("Status: Running" if is_running_instance() else "Status: Stopped")

    def refresh_status_after_process_change() -> None:
        refresh_status()
        root.after(500, refresh_status)
        root.after(1500, refresh_status)

    def start() -> None:
        if start_watcher_instance():
            refresh_status_after_process_change()
            messagebox.showinfo("Auto URL Fixer", "Started.")
        else:
            refresh_status_after_process_change()
            messagebox.showinfo("Auto URL Fixer", "Already running.")

    def stop() -> None:
        if stop_running_instance():
            refresh_status_after_process_change()
            messagebox.showinfo("Auto URL Fixer", "Stopped.")
        else:
            refresh_status_after_process_change()
            messagebox.showinfo("Auto URL Fixer", "No running instance was found.")

    def startup_on() -> None:
        enable_startup()
        messagebox.showinfo("Auto URL Fixer", "Startup enabled.")

    def startup_off() -> None:
        if disable_startup():
            messagebox.showinfo("Auto URL Fixer", "Startup disabled.")
        else:
            messagebox.showinfo("Auto URL Fixer", "No startup entry was found.")

    buttons = (
        ("Start", start),
        ("Stop", stop),
        ("Startup ON", startup_on),
        ("Startup OFF", startup_off),
    )

    for index, (label, command) in enumerate(buttons):
        button = tk.Button(frame, text=label, width=16, command=command)
        button.grid(row=2 + index // 2, column=index % 2, padx=4, pady=4)

    close_button = tk.Button(frame, text="Close", width=35, command=root.destroy)
    close_button.grid(row=4, column=0, columnspan=2, padx=4, pady=(10, 0))

    refresh_status()
    root.mainloop()
    return 0
