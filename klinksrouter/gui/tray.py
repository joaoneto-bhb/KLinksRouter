from __future__ import annotations

import sys

from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from klinksrouter.editor import open_rules_file
from klinksrouter.gui.icon import tray_icon
from klinksrouter.gui.ipc import SingleInstanceGuard

SOCKET_NAME = "klinksrouter-tray"


class _Application(QApplication):
    """No macOS o SO entrega URLs abertas (quando este app é o navegador
    padrão) como QFileOpenEvent em vez de argv -- tanto no lançamento a frio
    quanto com a instância já rodando, então o roteamento tem que acontecer
    aqui, não numa CLI efêmera como no Linux."""

    def event(self, event) -> bool:
        if event.type() == QEvent.Type.FileOpen:
            from klinksrouter.routing import route_url

            route_url(event.url().toString())
            return True
        return super().event(event)


def _on_activated(reason: QSystemTrayIcon.ActivationReason) -> None:
    if reason == QSystemTrayIcon.ActivationReason.Trigger:
        open_rules_file()


def main() -> int:
    guard = SingleInstanceGuard(SOCKET_NAME)
    if guard.try_notify_running(command="ping"):
        return 0

    app_cls = _Application if sys.platform == "darwin" else QApplication
    app = app_cls(sys.argv)
    app.setOrganizationName("bighub")
    app.setApplicationName("KLinksRouter")
    app.setQuitOnLastWindowClosed(False)

    if sys.platform == "darwin":
        from klinksrouter.autostart_macos import install_autostart

        install_autostart()

    tray = QSystemTrayIcon(tray_icon(), app)
    tray.setToolTip("KLinksRouter")

    menu = QMenu()
    menu.addAction("Editar regras...", open_rules_file)
    menu.addSeparator()
    menu.addAction("Sair", app.quit)
    tray.setContextMenu(menu)
    tray.activated.connect(_on_activated)
    tray.show()

    guard.listen(on_message=lambda _msg: None)

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
