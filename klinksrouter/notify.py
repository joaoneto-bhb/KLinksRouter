from __future__ import annotations

import subprocess


def notify_routed(url: str, browser_name: str) -> None:
    _notify("Link roteado", f"{url}\n→ {browser_name}")


def notify_error(message: str) -> None:
    _notify("KLinksRouter — erro", message, urgency="critical")


def _notify(summary: str, body: str, urgency: str = "normal") -> None:
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
