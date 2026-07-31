# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

repo_root = Path(SPECPATH).resolve().parent.parent
version = os.environ.get("KLINKSROUTER_VERSION", "0.0.0")

a = Analysis(
    [str(repo_root / "klinksrouter" / "gui" / "tray.py")],
    pathex=[str(repo_root)],
    datas=[
        (str(repo_root / "packaging" / "icons" / "store.bighub.KLinksRouter.svg"), "icons"),
    ],
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="KLinksRouter",
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    name="KLinksRouter",
)

app = BUNDLE(
    coll,
    name="KLinksRouter.app",
    icon=str(repo_root / "packaging" / "macos" / "KLinksRouter.icns"),
    bundle_identifier="store.bighub.KLinksRouter",
    info_plist={
        "CFBundleName": "KLinksRouter",
        "CFBundleDisplayName": "KLinksRouter",
        "CFBundleShortVersionString": version,
        "CFBundleVersion": version,
        "LSUIElement": True,
        "NSHumanReadableCopyright": "bighub",
        "CFBundleURLTypes": [
            {
                "CFBundleURLName": "store.bighub.KLinksRouter.http",
                "CFBundleTypeRole": "Viewer",
                "CFBundleURLSchemes": ["http", "https"],
            }
        ],
        # Declarar http/https em CFBundleURLTypes não basta pra aparecer na lista
        # "Navegador da Web padrão" do macOS (Big Sur+). O sistema exige, além
        # disso, que o app se declare navegador via NSUserActivityTypes e que
        # saiba "abrir" documentos HTML. Espelha o Info.plist da Finicky (mesmo
        # caso de uso, aparece na lista no macOS 12+).
        "NSUserActivityTypes": ["NSUserActivityTypeBrowsingWeb"],
        "CFBundleDocumentTypes": [
            {
                "CFBundleTypeName": "HTML Document",
                "CFBundleTypeRole": "Viewer",
                "LSItemContentTypes": ["public.html"],
            },
            {
                "CFBundleTypeName": "XHTML document",
                "CFBundleTypeRole": "Viewer",
                "LSItemContentTypes": ["public.xhtml"],
            },
        ],
    },
)
