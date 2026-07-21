from __future__ import annotations

import subprocess


def notify_routed(url: str, browser_name: str) -> None:
    try:
        subprocess.Popen(
            [
                "notify-send",
                "--app-name=KLinksRouter",
                "--icon=store.bighub.KLinksRouter",
                "Link roteado",
                f"{url}\n→ {browser_name}",
            ]
        )
    except FileNotFoundError:
        pass
