from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


@dataclass
class Rule:
    match: str
    match_type: str = "domain"
    browser: str | None = None
    set_params: dict | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "Rule":
        return cls(
            match=data["match"],
            match_type=data.get("match_type", "domain"),
            browser=data.get("browser"),
            set_params=data.get("set_params") or {},
        )


def _domain_matches(hostname: str, pattern: str) -> bool:
    hostname = hostname.lower()
    pattern = pattern.lower()
    return hostname == pattern or hostname.endswith("." + pattern)


def find_rule(url: str, rules: list[Rule]) -> Rule | None:
    parts = urlsplit(url)
    for rule in rules:
        if rule.match_type == "domain":
            if parts.hostname and _domain_matches(parts.hostname, rule.match):
                return rule
        elif rule.match_type == "regex":
            if re.search(rule.match, url):
                return rule
    return None


def apply_rule(url: str, rule: Rule) -> str:
    if not rule.set_params:
        return url
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query.update({k: str(v) for k, v in rule.set_params.items()})
    new_query = urlencode(query)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))
