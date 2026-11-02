from __future__ import annotations

import platform
import shlex
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

TASK_NAME = "GrepolisBot"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _python_command() -> str:
    return f'"{sys.executable}" -m src.main --logs'


def _windows_launcher(root: Path) -> Path:
    launcher = root / "data" / "grepolis_scheduler.cmd"
    launcher.parent.mkdir(parents=True, exist_ok=True)
    log_file = launcher.parent / "scheduler.log"
    marker_file = launcher.parent / "scheduler.log.date"
    launcher.write_text(
        "@echo off\n"
        "setlocal\n"
        f'cd /d "{root}"\n'
        f'set "LOG_FILE={log_file}"\n'
        f'set "DATE_FILE={marker_file}"\n'
        "for /f %%D in ('powershell -NoProfile -Command \"(Get-Date).ToString('yyyyMMdd')\"') do set \"TODAY=%%D\"\n"
        "set \"LAST_DATE=\"\n"
        "if exist \"%DATE_FILE%\" set /p LAST_DATE=<\"%DATE_FILE%\"\n"
        "if not \"%TODAY%\"==\"%LAST_DATE%\" (\n"
        "  type nul > \"%LOG_FILE%\"\n"
        "  >\"%DATE_FILE%\" echo %TODAY%\n"
        ")\n"
        f'"{sys.executable}" -m src.main --logs >> "%LOG_FILE%" 2>&1\n',
        encoding="utf-8",
    )
    return launcher


def schedule_at(run_at: int) -> str:
    root = _project_root()
    scheduled_timestamp = max(run_at, int(time.time()) + 60)
    scheduled_timestamp = ((scheduled_timestamp + 59) // 60) * 60
    when = datetime.fromtimestamp(scheduled_timestamp)
    if platform.system() == "Windows":
        launcher = _windows_launcher(root)
        subprocess.run(
            ["schtasks", "/Create", "/TN", TASK_NAME, "/SC", "ONCE", "/SD", when.strftime("%d/%m/%Y"), "/ST", when.strftime("%H:%M"), "/TR", f'cmd.exe /d /c ""{launcher}""', "/F"],
            check=True,
        )
        return f"Windows Task Scheduler set for {when.isoformat(timespec='minutes')}"
    command = f"cd {shlex.quote(str(root))} && {_python_command()}"
    process = subprocess.run(["at", "-t", when.strftime("%Y%m%d%H%M")], input=command + "\n", text=True, check=False)
    if process.returncode != 0:
        raise RuntimeError("Could not schedule Linux job; install the 'at' service")
    return f"Linux at job set for {when.isoformat(timespec='minutes')}"


def install() -> str:
    return schedule_at(int(datetime.now().timestamp()) + 1)


def uninstall() -> str:
    if platform.system() == "Windows":
        subprocess.run(["schtasks", "/Delete", "/TN", TASK_NAME, "/F"], check=True)
        return "Windows Task Scheduler removed"
    existing = subprocess.run(["crontab", "-l"], capture_output=True, text=True, check=False).stdout
    lines = [line for line in existing.splitlines() if TASK_NAME not in line]
    subprocess.run(["crontab", "-"], input="\n".join(lines) + "\n", text=True, check=True)
    return "Linux cron removed"
