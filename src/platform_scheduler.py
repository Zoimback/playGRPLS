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


def schedule_at(run_at: int) -> str:
    root = _project_root()
    scheduled_timestamp = max(run_at, int(time.time()) + 60)
    scheduled_timestamp = ((scheduled_timestamp + 59) // 60) * 60
    when = datetime.fromtimestamp(scheduled_timestamp)
    if platform.system() == "Windows":
        command = f'cmd /c "cd /d "{root}" && {_python_command()}"'
        subprocess.run(
            ["schtasks", "/Create", "/TN", TASK_NAME, "/SC", "ONCE", "/SD", when.strftime("%d/%m/%Y"), "/ST", when.strftime("%H:%M"), "/TR", command, "/F"],
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
