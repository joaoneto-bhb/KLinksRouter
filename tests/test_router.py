from klinksrouter.router import Rule, apply_rule, find_rule


def make_rule(**kwargs):
    return Rule.from_dict(kwargs)


def test_domain_match_exact():
    rule = make_rule(match="discord.com", browser="firefox")
    assert find_rule("https://discord.com/channels/1", [rule]) is rule


def test_domain_match_subdomain():
    rule = make_rule(match="google.com", browser="chrome")
    assert find_rule("https://meet.google.com/abc", [rule]) is rule


def test_domain_no_match_unrelated():
    rule = make_rule(match="discord.com", browser="firefox")
    assert find_rule("https://example.com", [rule]) is None


def test_regex_match():
    rule = make_rule(match=r"github\.com/.*/pull/\d+", match_type="regex", browser="firefox")
    assert find_rule("https://github.com/org/repo/pull/42", [rule]) is rule


def test_first_matching_rule_wins():
    specific = make_rule(match="meet.google.com", browser="chrome")
    generic = make_rule(match="google.com", browser="firefox")
    assert find_rule("https://meet.google.com/abc", [specific, generic]) is specific


def test_apply_rule_sets_param():
    rule = make_rule(match="meet.google.com", browser="chrome", set_params={"authuser": "3"})
    result = apply_rule("https://meet.google.com/abc-defg?hl=en", rule)
    assert "authuser=3" in result
    assert "hl=en" in result


def test_apply_rule_overwrites_existing_param():
    rule = make_rule(match="meet.google.com", browser="chrome", set_params={"authuser": "3"})
    result = apply_rule("https://meet.google.com/abc?authuser=0", rule)
    assert "authuser=3" in result
    assert "authuser=0" not in result


def test_apply_rule_no_params_returns_same_url():
    rule = make_rule(match="discord.com", browser="firefox")
    url = "https://discord.com/channels/1"
    assert apply_rule(url, rule) == url
