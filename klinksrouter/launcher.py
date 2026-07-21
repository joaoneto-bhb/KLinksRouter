from __future__ import annotations

import subprocess
from pathlib import Path


def in_flatpak_sandbox() -> bool:
    return Path("/.flatpak-info").exists()


def launch(command: list[str], url: str) -> None:
    full_command = [*command, url]
    if in_flatpak_sandbox():
        # sem isso o binário do host (chrome/firefox) não é alcançável de dentro do sandbox
        full_command = ["flatpak-spawn", "--host", *full_command]
    subprocess.Popen(full_command, start_new_session=True)
