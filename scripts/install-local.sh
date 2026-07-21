#!/usr/bin/env bash
# Instala o KLinksRouter nativamente (sem Flatpak) para o usuário atual,
# registra como handler de http/https e ativa o autostart da bandeja.
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v pipx >/dev/null 2>&1; then
  echo "pipx não encontrado. Instale com: sudo dnf install pipx" >&2
  exit 1
fi

pipx install --force .

APPS_DIR="$HOME/.local/share/applications"
AUTOSTART_DIR="$HOME/.config/autostart"
ICONS_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"
mkdir -p "$APPS_DIR" "$AUTOSTART_DIR" "$ICONS_DIR"

cp packaging/store.bighub.KLinksRouter.desktop "$APPS_DIR/"
cp packaging/store.bighub.KLinksRouter.UrlHandler.desktop "$APPS_DIR/"
cp packaging/store.bighub.KLinksRouter.Tray.desktop "$AUTOSTART_DIR/"
cp packaging/icons/store.bighub.KLinksRouter.svg "$ICONS_DIR/"

update-desktop-database "$APPS_DIR" >/dev/null 2>&1 || true
kbuildsycoca6 >/dev/null 2>&1 || true

xdg-mime default store.bighub.KLinksRouter.UrlHandler.desktop x-scheme-handler/http
xdg-mime default store.bighub.KLinksRouter.UrlHandler.desktop x-scheme-handler/https

echo "Instalado via pipx."
echo "A bandeja inicia automaticamente no próximo login. Para iniciar agora: klinksrouter-tray &"
echo "Para forçar como navegador padrão do sistema:"
echo "  xdg-settings set default-web-browser store.bighub.KLinksRouter.UrlHandler.desktop"
