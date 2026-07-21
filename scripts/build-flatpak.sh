#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../packaging/flatpak"

if [ ! -f python3-requirements.json ]; then
  echo "Rode antes: scripts/generate-flatpak-pip-sources.sh" >&2
  exit 1
fi

flatpak-builder --user --install --force-clean build-dir store.bighub.KLinksRouter.yml
