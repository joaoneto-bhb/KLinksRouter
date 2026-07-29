from __future__ import annotations

import sys

from klinksrouter.routing import route_url


def main() -> int:
    if len(sys.argv) < 2:
        print("uso: klinksrouter <url>", file=sys.stderr)
        return 1

    return 0 if route_url(sys.argv[1]) else 1


if __name__ == "__main__":
    sys.exit(main())
