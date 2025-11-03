#!/usr/bin/env python3
"""
CodeSentinel Setup Wizard (Modular, Minimal)

A compact, secure-first, multi-step GUI wizard that ports the tested legacy
features in a clean architecture:

- Welcome (auto-starting flow)
- Install Location with smart Git repo detection
- Alerts (console/file/email/slack) with compact layout
- GitHub Integration options (init/clone/connect) — configuration only
- IDE Detection (8 popular IDEs) with guidance
- Optional Features (scheduler, git hooks, CI templates)
- Summary + Save (writes codesentinel.json)

This wizard intentionally avoids side effects beyond config writes and simple
git init; integration steps that require credentials or network calls are
captured as configuration for follow-up commands handled by the CLI.
"""

from __future__ import annotations

import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Dict, Any, List, Tuple, Callable

from .utils.config import ConfigManager


class ScrollableFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.inner = ttk.Frame(canvas)
        self.inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.inner, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")


class WizardApp:
    WIDTH, HEIGHT = 800, 700

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CodeSentinel Setup Wizard")
        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.root.resizable(True, True)
        self._center()

        self.data: Dict[str, Any] = {
            "install_location": str(Path.cwd()),
            "alerts": {
                "console": {"enabled": True},
                "file": {"enabled": True, "log_file": "codesentinel.log"},
                "email": {"enabled": False, "smtp_server": "", "smtp_port": 587, "username": "", "password": "", "from_email": "", "to_emails": []},
                "slack": {"enabled": False, "webhook_url": "", "channel": "#maintenance-alerts"},
            },
            "github": {"mode": "connect", "repo_url": "", "create": False},
            "ide": {},
            "optional": {"scheduler": False, "git_hooks": True, "ci": False},
        }

        self.steps: List[Tuple[str, Callable[[], ttk.Frame]]] = []
        self._active_frame: ttk.Frame | None = None
        self._build_ui()
        self._build_steps()
        self._show_step(0)

    # ---- window layout ----
    def _center(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.WIDTH // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.HEIGHT // 2)
        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")

    def _build_ui(self):
        self.header = ttk.Frame(self.root)
        self.header.pack(fill="x", padx=16, pady=12)
        ttk.Label(self.header, text="CodeSentinel Setup Wizard", font=("Segoe UI", 18, "bold")).pack()
        ttk.Label(self.header, text="Security-First Automated Maintenance and Monitoring", foreground="gray").pack(pady=(4, 0))

        self.body = ttk.Frame(self.root)
        self.body.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        self.footer = ttk.Frame(self.root)
        self.footer.pack(fill="x", padx=16, pady=16)
        self.back_btn = ttk.Button(self.footer, text="Back", command=self._back)
        self.next_btn = ttk.Button(self.footer, text="Next", command=self._next)
        self.cancel_btn = ttk.Button(self.footer, text="Cancel", command=self.root.destroy)
        self.back_btn.pack(side="left")
        self.cancel_btn.pack(side="right")
        self.next_btn.pack(side="right", padx=(0, 8))

    def _clear_body(self):
        for w in self.body.winfo_children():
            w.destroy()

    def _show_step(self, idx: int):
        self.current = idx
        self._clear_body()
        title, builder = self.steps[idx]
        ttk.Label(self.body, text=title, font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 8))
        self._active_frame = builder()
        self._active_frame.pack(fill="both", expand=True)
        self.back_btn.state(["!disabled"] if idx > 0 else ["disabled"])
        self.next_btn.config(text="Finish" if idx == len(self.steps) - 1 else "Next")

    def _next(self):
        # collect data from current step if it has a collect() method
        frame = self._active_frame
        if frame is not None and hasattr(frame, "collect"):
            if frame.collect() is False:  # type: ignore[attr-defined]
                return
        if self.current == len(self.steps) - 1:
            self._save_and_finish()
            return
        self._show_step(self.current + 1)

    def _back(self):
        if self.current > 0:
            self._show_step(self.current - 1)

    # ---- step builders ----
    def _build_steps(self):
        self.steps = [
            ("Welcome", self._step_welcome),
            ("Installation Location", self._step_location),
            ("Alert Preferences", self._step_alerts),
            ("GitHub Integration", self._step_github),
            ("IDE Integration", self._step_ide),
            ("Optional Features", self._step_optional),
            ("Summary", self._step_summary),
        ]

    def _step_welcome(self):
        f = ScrollableFrame(self.body)
        inner = f.inner
        ttk.Label(inner, text=(
            "Welcome! This wizard will configure CodeSentinel.\n\n"
            "Steps:\n"
            "1) Choose install location (smart repo detection)\n"
            "2) Configure alerts (console/file/email/slack)\n"
            "3) Select GitHub integration mode\n"
            "4) Detect IDEs\n"
            "5) Pick optional automation features\n"
            "6) Review and save configuration"
        ), justify="left").pack(anchor="w")
        return f

    def _step_location(self):
        f = ScrollableFrame(self.body)
        inner = f.inner
        self.loc_var = tk.StringVar(value=self.data["install_location"]) 
        row = ttk.Frame(inner)
        row.pack(fill="x", pady=4)
        ttk.Label(row, text="Install location (project root):").pack(side="left")
        ttk.Entry(row, textvariable=self.loc_var).pack(side="left", fill="x", expand=True, padx=8)
        ttk.Button(row, text="Browse...", command=self._browse_location).pack(side="left")

        # smart repo detection panel
        ttk.Label(inner, text="Detected Git repositories:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(12, 4))
        self.repo_list = tk.Listbox(inner, height=8)
        self.repo_list.pack(fill="both", expand=True)
        for p in self._detect_git_repos():
            self.repo_list.insert(tk.END, str(p))
        ttk.Button(inner, text="Use Selected Repository", command=self._use_selected_repo).pack(anchor="e", pady=(6, 0))

        def collect():
            self.data["install_location"] = self.loc_var.get().strip() or str(Path.cwd())
        f.collect = collect  # type: ignore
        return f

    def _step_alerts(self):
        f = ScrollableFrame(self.body)
        inner = f.inner
        alerts = self.data["alerts"]

        # Channels
        channels = ttk.LabelFrame(inner, text="Channels", padding=8)
        channels.pack(fill="x", pady=6)
        self.console_var = tk.BooleanVar(value=alerts["console"]["enabled"]) 
        self.file_var = tk.BooleanVar(value=alerts["file"]["enabled"]) 
        self.email_var = tk.BooleanVar(value=alerts["email"]["enabled"]) 
        self.slack_var = tk.BooleanVar(value=alerts["slack"]["enabled"]) 
        ttk.Checkbutton(channels, text="Console", variable=self.console_var).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(channels, text="File", variable=self.file_var).grid(row=0, column=1, sticky="w")
        ttk.Checkbutton(channels, text="Email", variable=self.email_var).grid(row=0, column=2, sticky="w")
        ttk.Checkbutton(channels, text="Slack", variable=self.slack_var).grid(row=0, column=3, sticky="w")

        # File log
        filebox = ttk.Frame(inner)
        filebox.pack(fill="x", pady=(6, 0))
        self.log_file_var = tk.StringVar(value=alerts["file"]["log_file"]) 
        ttk.Label(filebox, text="Log file:").pack(side="left")
        ttk.Entry(filebox, textvariable=self.log_file_var).pack(side="left", fill="x", expand=True, padx=8)

        # Email compact layout
        email = ttk.LabelFrame(inner, text="Email Settings", padding=8)
        email.pack(fill="x", pady=6)
        self.smtp_server_var = tk.StringVar(value=alerts["email"].get("smtp_server", ""))
        self.smtp_port_var = tk.StringVar(value=str(alerts["email"].get("smtp_port", 587)))
        self.email_user_var = tk.StringVar(value=alerts["email"].get("username", ""))
        self.email_pass_var = tk.StringVar(value=alerts["email"].get("password", ""))
        self.from_email_var = tk.StringVar(value=alerts["email"].get("from_email", ""))
        self.to_emails_var = tk.StringVar(value=",".join(alerts["email"].get("to_emails", [])))
        grid = ttk.Frame(email); grid.pack(fill="x")
        for i,(lbl,var,w) in enumerate([
            ("SMTP Server", self.smtp_server_var, 25),
            ("Port", self.smtp_port_var, 6),
            ("Username", self.email_user_var, 22),
            ("Password", self.email_pass_var, 22),
            ("From", self.from_email_var, 24),
            ("To (comma-separated)", self.to_emails_var, 36),
        ]):
            ttk.Label(grid, text=lbl).grid(row=i, column=0, sticky="w", padx=(0,8), pady=2)
            ttk.Entry(grid, textvariable=var, width=w, show='*' if lbl=="Password" else '').grid(row=i, column=1, sticky="we", pady=2)

        # Slack
        slack = ttk.LabelFrame(inner, text="Slack", padding=8)
        slack.pack(fill="x", pady=6)
        self.slack_url_var = tk.StringVar(value=alerts["slack"].get("webhook_url", ""))
        self.slack_channel_var = tk.StringVar(value=alerts["slack"].get("channel", "#maintenance-alerts"))
        ttk.Label(slack, text="Webhook URL").grid(row=0, column=0, sticky="w", padx=(0,8))
        ttk.Entry(slack, textvariable=self.slack_url_var, width=48).grid(row=0, column=1, sticky="we", pady=2)
        ttk.Label(slack, text="Channel").grid(row=1, column=0, sticky="w", padx=(0,8))
        ttk.Entry(slack, textvariable=self.slack_channel_var, width=24).grid(row=1, column=1, sticky="we", pady=2)

        def collect():
            alerts["console"]["enabled"] = bool(self.console_var.get())
            alerts["file"]["enabled"] = bool(self.file_var.get())
            alerts["file"]["log_file"] = self.log_file_var.get().strip() or "codesentinel.log"
            alerts["email"]["enabled"] = bool(self.email_var.get())
            alerts["email"].update({
                "smtp_server": self.smtp_server_var.get().strip(),
                "smtp_port": int(self.smtp_port_var.get() or 587),
                "username": self.email_user_var.get().strip(),
                "password": self.email_pass_var.get(),
                "from_email": self.from_email_var.get().strip(),
                "to_emails": [e.strip() for e in self.to_emails_var.get().split(',') if e.strip()],
            })
            alerts["slack"]["enabled"] = bool(self.slack_var.get())
            alerts["slack"].update({
                "webhook_url": self.slack_url_var.get().strip(),
                "channel": self.slack_channel_var.get().strip() or "#maintenance-alerts",
            })
        f.collect = collect  # type: ignore
        return f

    def _step_github(self):
        f = ScrollableFrame(self.body)
        inner = f.inner
        ttk.Label(inner, text="Choose how to connect this project to GitHub.").pack(anchor="w")
        self.gh_mode = tk.StringVar(value=self.data["github"]["mode"])  # initialize, clone, connect
        for m, txt in [("initialize","Initialize new repository"), ("clone","Clone existing repository"), ("connect","Connect local to remote")]:
            ttk.Radiobutton(inner, text=txt, variable=self.gh_mode, value=m).pack(anchor="w")
        self.gh_url = tk.StringVar(value=self.data["github"].get("repo_url",""))
        url_row = ttk.Frame(inner); url_row.pack(fill="x", pady=(6,0))
        ttk.Label(url_row, text="Repository URL").pack(side="left")
        ttk.Entry(url_row, textvariable=self.gh_url).pack(side="left", fill="x", expand=True, padx=8)

        def collect():
            self.data["github"]["mode"] = self.gh_mode.get()
            self.data["github"]["repo_url"] = self.gh_url.get().strip()
        f.collect = collect  # type: ignore
        return f

    def _step_ide(self):
        f = ScrollableFrame(self.body)
        inner = f.inner
        ttk.Label(inner, text="Detected IDEs:").pack(anchor="w")
        ide_map = {
            "VS Code": ["code"],
            "Visual Studio": ["devenv"],
            "PyCharm": ["pycharm64", "charm"],
            "IntelliJ IDEA": ["idea64"],
            "Sublime Text": ["sublime_text", "subl"],
            "Atom": ["atom"],
            "Notepad++": ["notepad++"],
            "Eclipse": ["eclipse"],
        }
        statuses = {}
        for name, cmds in ide_map.items():
            found = any(shutil.which(c) for c in cmds)
            statuses[name] = found
            color = "#2e7d32" if found else "#9e9e9e"
            ttk.Label(inner, text=(f"✓ {name} detected" if found else f"{name} not detected"), foreground=color).pack(anchor="w")
        self.data["ide"] = statuses
        return f

    def _step_optional(self):
        f = ScrollableFrame(self.body)
        inner = f.inner
        self.opt_scheduler = tk.BooleanVar(value=self.data["optional"]["scheduler"]) 
        self.opt_hooks = tk.BooleanVar(value=self.data["optional"]["git_hooks"]) 
        self.opt_ci = tk.BooleanVar(value=self.data["optional"]["ci"]) 
        ttk.Checkbutton(inner, text="Enable scheduled maintenance", variable=self.opt_scheduler).pack(anchor="w")
        ttk.Checkbutton(inner, text="Install Git hooks (pre-commit/push)", variable=self.opt_hooks).pack(anchor="w")
        ttk.Checkbutton(inner, text="Add CI templates (GitHub Actions)", variable=self.opt_ci).pack(anchor="w")

        def collect():
            self.data["optional"].update({
                "scheduler": bool(self.opt_scheduler.get()),
                "git_hooks": bool(self.opt_hooks.get()),
                "ci": bool(self.opt_ci.get()),
            })
        f.collect = collect  # type: ignore
        return f

    def _step_summary(self):
        f = ScrollableFrame(self.body)
        inner = f.inner
        ttk.Label(inner, text="Review your configuration, then click Finish to save.", font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 8))
        self.summary_text = tk.Text(inner, height=18)
        self.summary_text.pack(fill="both", expand=True)

        def collect():
            import json
            self.summary_text.delete("1.0", tk.END)
            self.summary_text.insert("1.0", json.dumps(self.data, indent=2))
        f.collect = collect  # type: ignore  # refresh summary on Next
        return f

    # ---- helpers ----
    def _browse_location(self):
        selected = filedialog.askdirectory(initialdir=self.loc_var.get() or str(Path.home()))
        if selected:
            self.loc_var.set(selected)

    def _detect_git_repos(self) -> List[Path]:
        # Search a few common roots and parents, limited depth and count
        roots = {
            Path.home() / "Documents",
            Path.home() / "Projects",
            Path.home() / "Code",
            Path.cwd().parent,
            Path.cwd(),
        }
        found: List[Path] = []
        queue: List[Tuple[Path, int]] = [(p, 0) for p in roots if p.exists()]
        max_depth, max_count = 3, 10
        seen = set()
        while queue and len(found) < max_count:
            base, depth = queue.pop(0)
            if base in seen:
                continue
            seen.add(base)
            try:
                for child in base.iterdir():
                    if child.is_dir():
                        if (child / ".git").exists():
                            found.append(child)
                            if len(found) >= max_count:
                                break
                        if depth < max_depth:
                            queue.append((child, depth + 1))
            except (PermissionError, OSError):
                continue
        return found

    def _use_selected_repo(self):
        try:
            sel = self.repo_list.curselection()
            if sel:
                self.loc_var.set(self.repo_list.get(sel[0]))
        except Exception:
            pass

    def _save_and_finish(self):
        # Save configuration to selected location
        target = Path(self.data["install_location"]) / "codesentinel.json"
        cm = ConfigManager(config_path=target)
        cm.save_config(self.data)
        # Optionally init git if chosen mode requires and repo missing
        if self.data.get("github", {}).get("mode") == "initialize":
            path = Path(self.data["install_location"]) 
            if not (path / ".git").exists():
                try:
                    import subprocess
                    subprocess.run(["git", "init"], cwd=str(path), capture_output=True)
                except Exception:
                    pass
        messagebox.showinfo("Setup Complete", f"Configuration saved to: {target}")
        self.root.destroy()


def main():
    app = WizardApp()
    app.root.mainloop()


if __name__ == "__main__":
    main()
