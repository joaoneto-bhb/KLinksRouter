from __future__ import annotations

import sys

from klinksrouter.config import load_config
from klinksrouter.launcher import launch
from klinksrouter.notify import notify_routed
from klinksrouter.router import Rule, apply_rule, find_rule


def main() -> int:
    if len(sys.argv) < 2:
        print("uso: klinksrouter <url>", file=sys.stderr)
        return 1

    url = sys.argv[1]
    config = load_config()
    rules = [Rule.from_dict(r) for r in config.get("rules", [])]
    browsers = config.get("browsers", {})

    rule = find_rule(url, rules)
    browser_name = rule.browser if rule and rule.browser else config.get("default_browser")
    browser = browsers.get(browser_name)

    if not browser:
        print(f"navegador '{browser_name}' não configurado em rules.yaml", file=sys.stderr)
        return 1

    final_url = apply_rule(url, rule) if rule else url
    launch(browser["command"], final_url)

    if rule is not None:
        notify_routed(url, browser_name)

    return 0


if __name__ == "__main__":
    sys.exit(main())
