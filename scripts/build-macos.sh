#!/usr/bin/env bash
# Gera KLinksRouter.app + KLinksRouter.dmg. Só roda em macOS (usa sips/iconutil
# indiretamente via Qt offscreen, hdiutil).
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "Este script só roda no macOS." >&2
  exit 1
fi

VERSION="${1:-0.0.0}"

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -e . --quiet
pip install --quiet pyinstaller

WORKDIR="$(mktemp -d)"
ICONSET_DIR="$WORKDIR/KLinksRouter.iconset"
mkdir -p "$ICONSET_DIR"

QT_QPA_PLATFORM=offscreen python3 - "packaging/icons/store.bighub.KLinksRouter.svg" "$ICONSET_DIR" <<'PYEOF'
import sys
from pathlib import Path

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication

svg_path, out_dir = sys.argv[1], Path(sys.argv[2])
app = QApplication([])
renderer = QSvgRenderer(svg_path)
for size in (16, 32, 128, 256, 512):
    for scale, suffix in ((1, ""), (2, "@2x")):
        px = size * scale
        pixmap = QPixmap(QSize(px, px))
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        pixmap.save(str(out_dir / f"icon_{size}x{size}{suffix}.png"))
PYEOF

iconutil -c icns "$ICONSET_DIR" -o packaging/macos/KLinksRouter.icns

rm -rf build dist
KLINKSROUTER_VERSION="$VERSION" pyinstaller --noconfirm packaging/macos/klinksrouter-tray.spec

rm -f KLinksRouter.dmg
hdiutil create -volname KLinksRouter -srcfolder dist/KLinksRouter.app -ov -format UDZO KLinksRouter.dmg

echo "Gerado: KLinksRouter.dmg"
