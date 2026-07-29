from __future__ import annotations

import sys

from klinksrouter.config import config_path, load_config
from klinksrouter.launcher import launch
from klinksrouter.notify import notify_error, notify_routed
from klinksrouter.router import Rule, apply_rule, find_rule


def route_url(url: str) -> bool:
    """Casa a URL contra as regras, lança o navegador e notifica. Retorna
    False se o navegador resolvido não existir em rules.yaml."""
    config = load_config()
    rules = [Rule.from_dict(r) for r in config.get("rules", [])]
    browsers = config.get("browsers", {})

    rule = find_rule(url, rules)
    browser_name = rule.browser if rule and rule.browser else config.get("default_browser")
    browser = browsers.get(browser_name)

    if not browser:
        message = (
            f"Navegador '{browser_name}' não existe em {config_path()}.\n"
            f"Chaves válidas em browsers: {', '.join(browsers) or '(nenhuma)'}"
        )
        print(message, file=sys.stderr)
        notify_error(message)
        return False

    final_url = apply_rule(url, rule) if rule else url
    launch(browser["command"], final_url)

    if rule is not None:
        notify_routed(url, browser_name)

    return True
