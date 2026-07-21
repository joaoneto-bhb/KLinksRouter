from __future__ import annotations

from pathlib import Path

import yaml
from platformdirs import user_config_dir

APP_NAME = "klinksrouter"

DEFAULT_RULES_YAML = """\
# Configuração do KLinksRouter.
#
# Edite este arquivo à vontade -- a CLI (klinksrouter <url>) lê a versão mais
# recente do disco a cada link clicado, não precisa reiniciar nada.

# Navegador padrão, usado quando nenhuma regra abaixo casar com a URL.
default_browser: firefox

# Navegadores disponíveis: nome -> comando. A URL final é anexada como
# último argumento do comando na hora de abrir o link.
browsers:
  firefox:
    command: [firefox]
  chrome:
    command: [google-chrome-stable]
  # brave:
  #   command: [brave-browser]

# Regras avaliadas em ordem -- a primeira que casar com a URL vence (sem
# "melhor match"). Coloque regras mais específicas antes de genéricas
# (ex: meet.google.com antes de google.com).
rules:
  - match: meet.google.com
    match_type: domain       # "domain" (padrão) ou "regex"
    browser: chrome
    # set_params sobrescreve (não soma) query params existentes na URL --
    # é assim que isso força &authuser=3 mesmo se já vier outro valor.
    set_params:
      authuser: "3"

  - match: discord.com
    match_type: domain
    browser: firefox

  # match_type: domain casa o host exato OU qualquer subdomínio -- não
  # precisa escrever "*.google.com", "google.com" já casa "docs.google.com".

  # Exemplo com regex, rodando re.search contra a URL inteira:
  # - match: 'github\\.com/.*/pull/\\d+'
  #   match_type: regex
  #   browser: firefox
"""


def config_dir() -> Path:
    return Path(user_config_dir(APP_NAME))


def config_path() -> Path:
    return config_dir() / "rules.yaml"


def load_config() -> dict:
    path = config_path()
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(DEFAULT_RULES_YAML, encoding="utf-8")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    data.setdefault("browsers", {})
    data.setdefault("rules", [])
    data.setdefault("default_browser", next(iter(data["browsers"]), None))
    return data
