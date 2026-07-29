# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## O que é

KLinksRouter é um roteador de links: intercepta a abertura de qualquer URL
http/https no sistema e decide, por regras configuráveis, qual navegador deve
abri-la — podendo reescrever query params no processo (ex:
`meet.google.com` → Chrome com `&authuser=3` forçado; `discord.com` →
Firefox). Foco primário é KDE Plasma 6; há também suporte a macOS (ver seção
"macOS" em Arquitetura) — sem pretensão de cobrir outros DEs Linux (GNOME
etc.) além desses dois alvos.

Não tem GUI de formulário para editar regras — "editar" é abrir
`rules.yaml` num editor de texto (ver seção Arquitetura). É proposital: menos
superfície de UI para manter, e o arquivo já é autoexplicativo (comentado).

## Comandos

```bash
scripts/dev-run.sh          # cria/reusa .venv, instala em modo editável, abre a bandeja
source .venv/bin/activate && pytest -q    # roda os testes (só klinksrouter/router.py hoje)
scripts/install-local.sh    # instala nativamente (pipx) para o usuário atual, Linux
scripts/generate-flatpak-pip-sources.sh   # regenera packaging/flatpak/python3-requirements.json (PyYAML+platformdirs)
scripts/build-flatpak.sh    # flatpak-builder --user --install
scripts/build-macos.sh <versão>   # gera dist/KLinksRouter.app + KLinksRouter.dmg (só roda em macOS)
```

Para testar a lógica de roteamento manualmente sem lançar navegador de verdade,
edite `klinksrouter/launcher.py:launch` temporariamente ou inspecione o
resultado de `router.apply_rule` num REPL — não há flag `--dry-run` no CLI.

## Arquitetura

Sem estado compartilhado em memória — tudo passa por
`~/.config/klinksrouter/rules.yaml` (via `platformdirs`, `klinksrouter/config.py`).
A lógica de "casar regra, reescrever params, lançar navegador, notificar" vive
em `klinksrouter/routing.py:route_url(url)`, compartilhada entre o processo
que trata a URL no KDE (CLI efêmera) e no macOS (o próprio app da bandeja,
via Apple Event) — ver as duas seções abaixo.

### KDE (Linux)

Dois processos independentes:

1. **`klinksrouter <url>`** (`klinksrouter/__main__.py`) — CLI efêmera,
   registrada no KDE como handler de `x-scheme-handler/http(s)` (ver
   `packaging/store.bighub.KLinksRouter.UrlHandler.desktop`). Todo link
   clicado no sistema chama essa CLI, que delega pra
   `klinksrouter/routing.py:route_url`. Sai imediatamente depois. Não depende
   da bandeja estar rodando.

2. **`klinksrouter-tray`** (`klinksrouter/gui/tray.py`) — processo de longa
   duração, autostart na sessão (`packaging/store.bighub.KLinksRouter.Tray.desktop`
   em `~/.config/autostart` ou `/app/etc/xdg/autostart` no Flatpak). Sobe só um
   `QSystemTrayIcon` + `QMenu` (QtWidgets puro — sem QML/Kirigami). O único item
   de menu relevante, "Editar regras...", e o clique no próprio ícone, chamam
   `klinksrouter/editor.py:open_rules_file` (`xdg-open` no `rules.yaml`) — não
   existe form de edição, é abrir o arquivo mesmo. Instância única garantida via
   socket local (`gui/ipc.py`, `SingleInstanceGuard`): uma segunda invocação
   apenas confirma que já tem uma rodando e sai, sem abrir ícone duplicado.

`klinksrouter/launcher.py` detecta sandbox Flatpak (`/.flatpak-info`) e prefixa
o comando com `flatpak-spawn --host` quando necessário — é o único jeito de
alcançar Chrome/Firefox do host de dentro do sandbox, liberado via
`--talk-name=org.freedesktop.Flatpak` no manifest.

`klinksrouter/autostart.py` só age dentro do sandbox Flatpak: pede autostart
via portal (`org.freedesktop.portal.Background`, `RequestBackground` com
`autostart=True`), que pede confirmação do usuário no primeiro uso. Fora do
Flatpak, o autostart é resolvido em instalação (script copia o `.desktop` para
`~/.config/autostart`), não em runtime.

### macOS

Não existe um equivalente direto ao handler de URL via CLI/argv: o macOS
entrega a URL de um link clicado como **Apple Event** (`GetURL`) pro app já
registrado como navegador padrão — mesmo se o app ainda não estava rodando.
Por isso, ao contrário do KDE, aqui é **um único processo** que acumula os
dois papéis: `klinksrouter/gui/tray.py` roda uma `QApplication` (`_Application`)
que sobrescreve `event()` pra capturar `QEvent.Type.FileOpenEvent` — Qt já
traduz o Apple Event pra esse tipo — e chama `routing.route_url()` direto,
sem precisar de uma CLI separada. `klinksrouter/__main__.py` continua existindo
mas não tem papel nenhum no fluxo de macOS.

`klinksrouter/autostart_macos.py` escreve um LaunchAgent em
`~/Library/LaunchAgents/store.bighub.KLinksRouter.Tray.plist` (`RunAtLoad`) na
primeira execução e dá `launchctl bootstrap` nele — só age se `sys.frozen`
(dentro do `.app` empacotado; rodando de uma venv de dev não há o que
autostartar). `klinksrouter/notify.py` e `klinksrouter/editor.py` fazem branch
por `sys.platform == "darwin"` pra usar `osascript`/`open` no lugar de
`notify-send`/`xdg-open`. O ícone da bandeja vem de
`klinksrouter/gui/icon.py`, que carrega o SVG bundlado via `QtSvg` em vez de
`QIcon.fromTheme` (sem tema de ícones no macOS).

Empacotamento (`scripts/build-macos.sh` + `packaging/macos/klinksrouter-tray.spec`,
PyInstaller): gera `dist/KLinksRouter.app` com `Info.plist` declarando
`CFBundleURLTypes` (schemes `http`/`https`) e `LSUIElement=1` (sem ícone no
Dock, só barra de menu), depois empacota em `KLinksRouter.dmg` via `hdiutil`.
O `.icns` do ícone é gerado on-the-fly a partir do SVG usando `QSvgRenderer`
offscreen (evita depender de `rsvg-convert`/Inkscape no runner). **Sem
assinatura Developer ID/notarização** (sem conta paga da Apple) — o `.dmg`
final dispara o aviso do Gatekeeper, contornável com clique-direito → Abrir
na primeira execução. Se algum dia houver conta Apple, o próximo passo é
assinar + notarizar no job de CI antes de gerar o `.dmg`.

### Empacotamento Python: PySide6-Essentials, não PySide6

A dependência é `PySide6-Essentials`, não o metapacote `PySide6` — como a
bandeja só usa `QtWidgets`/`QtGui` (sem QML/Kirigami), isso evita puxar o
`PySide6-Addons` (WebEngine, Qt3D, Charts...) inteiro à toa. Instalação limpa
via `pip`/`pipx` traz só o Essentials; se aparecer o Addons instalado, é
resíduo de uma venv/pipx-venv reaproveitada de uma versão anterior — apague o
venv e reinstale para conferir.

Não há mais nenhuma dependência de Kirigami/QML nem exigência de PySide6 do
sistema — isso foi removido junto com a GUI de formulário (ver histórico do
projeto se precisar de contexto).

### Flatpak: `io.qt.PySide.BaseApp`, não pip puro

`flatpak-pip-generator` **recusa** gerar sources pra `PySide6`/`PySide6-Essentials`
e recomenda o BaseApp oficial (`https://github.com/flathub/io.qt.PySide.BaseApp`)
— vendorizar o wheel do PyPI por cima de um runtime KDE é a fonte clássica de
incompatibilidade de ABI. O manifest (`packaging/flatpak/store.bighub.KLinksRouter.yml`)
usa `base: io.qt.PySide.BaseApp` / `base-version: "6.7"` por cima de
`org.kde.Platform` (branch 6.7 está marcada "Discouraged" no BaseApp, mas é a
mais recente com imagem de CI publicada em `bilelmoussaoui/flatpak-github-actions`
— sem isso o job de build falha no pull do container; revisitar quando a tag
`kde-6.8` sair), com
`BASEAPP_REMOVE_WEBENGINE=1` e `BASEAPP_DISABLE_NUMPY=1` pra reduzir o bundle,
e `cleanup-commands: [/app/cleanup-BaseApp.sh]` (exigido pelo BaseApp). O
módulo `python3-requirements.json` gerado por
`scripts/generate-flatpak-pip-sources.sh` cobre só `PyYAML` e `platformdirs`
(as duas dependências que não vêm do BaseApp) e é comitado no repo (não é
gitignored — funciona como lockfile).

### Modelo de regras (`rules.yaml`)

Spec completa em [`docs/rules-format.md`](docs/rules-format.md) — resumo abaixo.
O arquivo default (`klinksrouter/config.py:default_rules_yaml()`) já vem com
comentários `#` explicando cada campo — é a documentação primária pro usuário
final, que só vai abrir esse arquivo, não o README. O bloco `browsers:` do
template varia por `sys.platform`: no macOS vem com `command: [open, -a,
Firefox, --args]` em vez do binário Linux (`firefox`), já que lá o padrão é
abrir apps via `open -a`.

```yaml
default_browser: firefox
browsers:
  firefox: {command: [firefox]}
  chrome: {command: [google-chrome-stable]}
rules:
  - match: meet.google.com
    match_type: domain   # domain | regex
    browser: chrome
    set_params: {authuser: "3"}
  - match: discord.com
    match_type: domain
    browser: firefox
```

Regras são avaliadas em ordem — a primeira que casar vence
(`router.find_rule`), então coloque regras mais específicas (ex:
`meet.google.com`) antes de genéricas (ex: `google.com`) se ambas puderem
casar a mesma URL. `match_type: domain` casa o hostname exato ou qualquer
subdomínio; `match_type: regex` roda `re.search` na URL inteira.
`set_params` sobrescreve params existentes com mesmo nome (não faz merge
aditivo) — é assim que a regra do Meet força `authuser=3` mesmo se a URL já
tiver outro valor.

### IDs e naming

App-id Flatpak / prefixo de arquivo: `store.bighub.KLinksRouter` (reverse-DNS
do domínio do autor). Os três `.desktop` em `packaging/` têm papéis distintos
e não são intercambiáveis: `.desktop` (entrada visível no menu, roda
`klinksrouter-edit-rules`), `.UrlHandler.desktop` (`NoDisplay=true`,
registrado como MIME handler), `.Tray.desktop` (`NoDisplay=true`, vai em
autostart).

## CI/release

`.github/workflows/release.yml` builda em paralelo o Flatpak (job `flatpak`,
com `flatpak/flatpak-github-actions/flatpak-builder`, container
`bilelmoussaoui/flatpak-github-actions:kde-6.7`) e o `.dmg` do macOS (job
`macos`, `runs-on: macos-14`, via `scripts/build-macos.sh`). O job `flatpak`
roda em todo push/PR pra `main` (validação de build); o job `macos` só roda
em tag (`v*.*.*` — runner macOS é mais caro, não vale gastar em todo PR). O
job `release`, condicionado a tag, baixa os dois artefatos e os anexa numa
GitHub Release via `softprops/action-gh-release` — não publica em Flathub
nem em nenhum "app store" de macOS automaticamente, isso é passo manual
separado.
