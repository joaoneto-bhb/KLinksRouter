# Formato de `rules.yaml`

## Onde fica

| Instalação | Caminho |
|---|---|
| Nativa (pipx, este repo) | `~/.config/klinksrouter/rules.yaml` |
| Flatpak | mesmo caminho *dentro do sandbox* — `$XDG_CONFIG_HOME` é redirecionado pelo Flatpak para `~/.var/app/store.bighub.KLinksRouter/config/klinksrouter/rules.yaml`, sem nenhum código extra |

`~/.config` (não `~/.local/share`) porque é configuração editável pelo
usuário, não dado de aplicação — segue o padrão XDG. Criado automaticamente
com um exemplo na primeira execução (`klinksrouter/config.py`).

## Protocolo

```yaml
default_browser: <nome>          # usado quando nenhuma regra casa

browsers:
  <nome>:
    command: [<binário>, <args...>]   # a URL final é anexada como último argumento

rules:                            # avaliadas em ordem; a primeira que casar vence
  - match: <domínio ou regex>
    match_type: domain            # "domain" (default) ou "regex"
    browser: <nome>                # precisa existir em `browsers`
    set_params:                    # opcional — sobrescreve (não soma) params existentes
      <chave>: <valor>
```

- `match_type: domain` casa o hostname exato **ou qualquer subdomínio**
  (`match: google.com` casa `meet.google.com`, `docs.google.com`, etc. —
  não precisa de `*.` na frente).
- `match_type: regex` roda `re.search(match, url)` contra a URL inteira.
- Coloque regras mais específicas antes das genéricas: a primeira que casar
  ganha, sem "melhor match".
- `set_params` ausente ou vazio não mexe na URL.

## Exemplo completo

```yaml
default_browser: firefox

browsers:
  firefox:
    command: [firefox]
  chrome:
    command: [google-chrome-stable]

rules:
  - match: meet.google.com
    match_type: domain
    browser: chrome
    set_params:
      authuser: "3"

  - match: discord.com
    match_type: domain
    browser: firefox

  - match: 'github\.com/.*/pull/\d+'
    match_type: regex
    browser: firefox
```

Editar é sempre à mão (é só YAML) — clicar no ícone da bandeja ou em
"Editar regras..." no menu apenas abre este arquivo no seu editor padrão
(`xdg-open`). Não precisa recarregar nada: a CLI (`klinksrouter <url>`) lê o
arquivo do zero a cada link clicado.
