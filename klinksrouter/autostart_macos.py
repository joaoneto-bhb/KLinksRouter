from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_LABEL = "store.bighub.KLinksRouter.Tray"

_PLIST_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{label}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{executable}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""


def _launch_agent_path() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / f"{_LABEL}.plist"


def install_autostart() -> None:
    """Instala um LaunchAgent pra reiniciar a bandeja no login (best-effort,
    idempotente). Só faz sentido dentro do .app empacotado (sys.frozen) --
    rodando de uma venv de dev não há o que autostartar."""
    if sys.platform != "darwin" or not getattr(sys, "frozen", False):
        return

    plist_path = _launch_agent_path()
    if plist_path.exists():
        return

    plist_path.parent.mkdir(parents=True, exist_ok=True)
    plist_path.write_text(
        _PLIST_TEMPLATE.format(label=_LABEL, executable=sys.executable),
        encoding="utf-8",
    )

    try:
        subprocess.Popen(
            ["launchctl", "bootstrap", f"gui/{os.getuid()}", str(plist_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        pass
