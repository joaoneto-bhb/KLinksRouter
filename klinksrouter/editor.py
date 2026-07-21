from __future__ import annotations

import subprocess
import sys

from klinksrouter.config import load_config, config_path


def open_rules_file() -> None:
    load_config()  # garante que o arquivo exista antes de tentar abri-lo
    subprocess.Popen(["xdg-open", str(config_path())])


def main() -> int:
    open_rules_file()
    return 0


if __name__ == "__main__":
    sys.exit(main())
