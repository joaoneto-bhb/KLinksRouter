from __future__ import annotations

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from klinksrouter.editor import open_rules_file
from klinksrouter.gui.ipc import SingleInstanceGuard

SOCKET_NAME = "klinksrouter-tray"


def _on_activated(reason: QSystemTrayIcon.ActivationReason) -> None:
    if reason == QSystemTrayIcon.ActivationReason.Trigger:
        open_rules_file()


def main() -> int:
    guard = SingleInstanceGuard(SOCKET_NAME)
    if guard.try_notify_running(command="ping"):
        return 0

    app = QApplication(sys.argv)
    app.setOrganizationName("bighub")
    app.setApplicationName("KLinksRouter")
    app.setQuitOnLastWindowClosed(False)

    icon = QIcon.fromTheme("store.bighub.KLinksRouter", QIcon.fromTheme("network-workgroup"))
    tray = QSystemTrayIcon(icon, app)
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
