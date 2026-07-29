from __future__ import annotations

import subprocess
import sys


def notify_routed(url: str, browser_name: str) -> None:
    _notify("Link roteado", f"{url}\n→ {browser_name}")


def notify_error(message: str) -> None:
    _notify("KLinksRouter — erro", message, urgency="critical")


def _notify(summary: str, body: str, urgency: str = "normal") -> None:
    if sys.platform == "darwin":
        _notify_macos(summary, body)
        return

    try:
        subprocess.Popen(
            [
                "notify-send",
                "--app-name=KLinksRouter",
                "--icon=store.bighub.KLinksRouter",
                f"--urgency={urgency}",
                summary,
                body,
            ]
        )
    except FileNotFoundError:
        pass


def _notify_macos(summary: str, body: str) -> None:
    # osascript não tem --urgency; "critical" vs "normal" não faz diferença
    # visual no Centro de Notificações do macOS.
    script = f"display notification {_applescript_literal(body)} with title {_applescript_literal(summary)}"
    try:
        subprocess.Popen(["osascript", "-e", script])
    except FileNotFoundError:
        pass


def _applescript_literal(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'
