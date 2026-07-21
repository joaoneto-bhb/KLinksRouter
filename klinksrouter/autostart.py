from __future__ import annotations

from klinksrouter.launcher import in_flatpak_sandbox

_REASON = "Manter o KLinksRouter ativo para rotear links ao iniciar a sessão"


def request_autostart(command: list[str] | None = None) -> None:
    """Pede autostart via portal xdg-desktop-portal (Background).

    Só é necessário dentro do sandbox Flatpak: fora dele o autostart é
    resolvido em instalação, copiando o .desktop para ~/.config/autostart
    (ver scripts/install-local.sh).
    """
    if not in_flatpak_sandbox():
        return

    try:
        from PySide6.QtDBus import QDBusInterface
    except ImportError:
        return

    interface = QDBusInterface(
        "org.freedesktop.portal.Desktop",
        "/org/freedesktop/portal/desktop",
        "org.freedesktop.portal.Background",
    )
    if not interface.isValid():
        return

    options = {
        "reason": _REASON,
        "autostart": True,
        "commandline": command or ["klinksrouter-tray"],
        "dbus-activatable": False,
    }
    interface.call("RequestBackground", "", options)
