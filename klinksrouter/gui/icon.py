from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon

_ICON_FILE = "store.bighub.KLinksRouter.svg"


def _bundled_icon_path() -> Path | None:
    """Localiza o SVG do ícone quando empacotado via PyInstaller (macOS) ou
    rodando direto do checkout (dev). No Linux instalado, o ícone vem do
    tema do sistema (ver tray_icon()), não daqui."""
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidate = Path(meipass) / "icons" / _ICON_FILE
        return candidate if candidate.exists() else None

    dev_candidate = Path(__file__).resolve().parents[2] / "packaging" / "icons" / _ICON_FILE
    return dev_candidate if dev_candidate.exists() else None


def tray_icon() -> QIcon:
    if sys.platform == "darwin":
        path = _bundled_icon_path()
        if path is not None:
            return QIcon(str(path))
        return QIcon.fromTheme("network-workgroup")

    return QIcon.fromTheme("store.bighub.KLinksRouter", QIcon.fromTheme("network-workgroup"))
