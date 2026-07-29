# KLinksRouter

Roteador leve de links, com foco primário em KDE Plasma 6 e suporte também a
macOS: intercepta a abertura de URLs e decide, por regras configuráveis, em
qual navegador cada uma deve abrir — podendo reescrever parâmetros da URL no
processo (ex: `meet.google.com` → Chrome com `&authuser=3`; `discord.com` →
Firefox). Ao rotear uma URL que casou com alguma regra, mostra uma
notificação do sistema avisando pra onde foi.

## Componentes

No KDE são dois processos independentes:

- `klinksrouter` — CLI sem estado, invocada pelo KDE como handler de
  `x-scheme-handler/http(s)` a cada link aberto (`klinksrouter <url>`).
- `klinksrouter-tray` — ícone na bandeja do sistema (autostart na sessão).
  Clicar nele (ou em "Editar regras..." no menu) abre o `rules.yaml` no seu
  editor padrão — não tem formulário de GUI, é editar o arquivo mesmo.

No macOS não existe handler de URL via CLI/argv — o sistema entrega links
abertos como Apple Event pro app já registrado como navegador padrão. Por
isso lá o `KLinksRouter.app` (gerado por `scripts/build-macos.sh`, ver
"Instalação no macOS" abaixo) acumula os dois papéis: fica na barra de menu
*e* recebe e roteia as URLs diretamente.

As regras ficam em `~/.config/klinksrouter/rules.yaml`, criado já comentado
na primeira execução (explica cada campo direto no arquivo). Formato
completo: [`docs/rules-format.md`](docs/rules-format.md).

## Desenvolvimento

```bash
scripts/dev-run.sh   # cria .venv, instala em modo editável e abre a bandeja
pytest                # dentro do .venv
```

## Instalação nativa (sem Flatpak)

```bash
scripts/install-local.sh
```

Instala via `pipx`, registra os `.desktop` (app + handler de URL) e o
autostart da bandeja em `~/.config/autostart`.

## Instalação via Flatpak

```bash
scripts/generate-flatpak-pip-sources.sh   # gera python3-requirements.json (PyYAML + platformdirs)
scripts/build-flatpak.sh                  # build + install --user
```

O manifest usa o [`io.qt.PySide.BaseApp`](https://github.com/flathub/io.qt.PySide.BaseApp)
oficial por cima do runtime `org.kde.Platform` para o PySide6 — vendorizar o
wheel do PyPI direto (via `flatpak-pip-generator`) não é suportado para
PySide6/PyQt propositalmente, por causar incompatibilidade de ABI com o Qt do
runtime; o BaseApp resolve isso.

Dentro do sandbox, lançar Chrome/Firefox do host depende de
`flatpak-spawn --host`, liberado via `--talk-name=org.freedesktop.Flatpak`
no manifest. O autostart da bandeja é pedido em runtime via portal
(`org.freedesktop.portal.Background`), que pede confirmação do usuário no
primeiro uso.

## Instalação no macOS

```bash
scripts/build-macos.sh 1.2.3   # gera dist/KLinksRouter.app e KLinksRouter.dmg
```

Abra o `.dmg` e arraste o `KLinksRouter.app` pra `/Applications`. Como o
`.dmg` não é assinado com Developer ID (sem conta paga da Apple), o Gatekeeper
bloqueia a primeira abertura — clique com o botão direito no app → "Abrir"
pra confirmar uma vez.

Depois de aberto, defina o KLinksRouter como navegador padrão do sistema em
Ajustes do Sistema → Área de Trabalho e Dock → Navegador padrão. O autostart
no login é instalado automaticamente (LaunchAgent) na primeira execução.

## Releases

Toda tag `v*.*.*` dispara `.github/workflows/release.yml`, que builda o
Flatpak e o `.dmg` do macOS e anexa os dois bundles a uma GitHub Release.
Isso não publica no Flathub (é um passo manual separado, via PR em
flathub/flathub) nem em nenhum "app store" de macOS.
