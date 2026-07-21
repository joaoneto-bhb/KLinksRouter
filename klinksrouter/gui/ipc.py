from __future__ import annotations

from typing import Callable

from PySide6.QtNetwork import QLocalServer, QLocalSocket


class SingleInstanceGuard:
    """Garante uma única instância da bandeja usando um socket local nomeado."""

    def __init__(self, name: str):
        self._name = name
        self._server: QLocalServer | None = None
        self._on_message: Callable[[str], None] | None = None

    def try_notify_running(self, command: str, timeout_ms: int = 200) -> bool:
        socket = QLocalSocket()
        socket.connectToServer(self._name)
        if socket.waitForConnected(timeout_ms):
            socket.write(command.encode("utf-8"))
            socket.waitForBytesWritten(timeout_ms)
            socket.disconnectFromServer()
            return True
        return False

    def listen(self, on_message: Callable[[str], None]) -> None:
        self._on_message = on_message
        QLocalServer.removeServer(self._name)
        self._server = QLocalServer()
        self._server.newConnection.connect(self._handle_new_connection)
        self._server.listen(self._name)

    def _handle_new_connection(self) -> None:
        socket = self._server.nextPendingConnection()
        if socket is None:
            return
        socket.readyRead.connect(lambda: self._read(socket))

    def _read(self, socket) -> None:
        data = bytes(socket.readAll()).decode("utf-8", errors="ignore")
        if self._on_message and data:
            self._on_message(data)
        socket.disconnectFromServer()
