#!/usr/bin/env bash
# Gera packaging/flatpak/python3-requirements.json usando o gerador oficial
# do projeto flatpak/flatpak-builder-tools (necessário antes de build-flatpak.sh).
set -euo pipefail
cd "$(dirname "$0")/../packaging/flatpak"

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

git clone --depth=1 https://github.com/flatpak/flatpak-builder-tools "$WORKDIR/flatpak-builder-tools"

python3 -m venv "$WORKDIR/venv"
source "$WORKDIR/venv/bin/activate"
pip install --quiet requirements-parser toposort

# PySide6 vem do io.qt.PySide.BaseApp (ver store.bighub.KLinksRouter.yml) --
# só geramos sources para as outras duas dependências.
python3 "$WORKDIR/flatpak-builder-tools/pip/flatpak-pip-generator" \
  --output python3-requirements \
  PyYAML platformdirs

echo "Gerado packaging/flatpak/python3-requirements.json"
