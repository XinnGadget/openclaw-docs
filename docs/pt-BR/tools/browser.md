---
read_when:
    - Adicionando automação do navegador controlada pelo agente
    - Depurando por que o openclaw está interferindo no seu próprio Chrome
    - Implementando configurações e ciclo de vida do navegador no app para macOS
summary: Serviço integrado de controle do navegador + comandos de ação
title: Navegador (gerenciado pelo OpenClaw)
x-i18n:
    generated_at: "2026-04-10T05:34:15Z"
    model: gpt-5.4
    provider: openai
    source_hash: cd3424f62178bbf25923b8bc8e4d9f70e330f35428d01fe153574e5fa45d7604
    source_path: tools/browser.md
    workflow: 15
---

# Navegador (gerenciado pelo openclaw)

O OpenClaw pode executar um **perfil dedicado de Chrome/Brave/Edge/Chromium** que o agente controla.
Ele é isolado do seu navegador pessoal e é gerenciado por meio de um pequeno
serviço local de controle dentro do Gateway (apenas loopback).

Visão para iniciantes:

- Pense nele como um **navegador separado, apenas para o agente**.
- O perfil `openclaw` **não** toca no perfil do seu navegador pessoal.
- O agente pode **abrir abas, ler páginas, clicar e digitar** em um ambiente seguro.
- O perfil integrado `user` se conecta à sua sessão real do Chrome autenticada por meio do Chrome MCP.

## O que você recebe

- Um perfil de navegador separado chamado **openclaw** (destaque laranja por padrão).
- Controle determinístico de abas (listar/abrir/focar/fechar).
- Ações do agente (clicar/digitar/arrastar/selecionar), snapshots, capturas de tela e PDFs.
- Suporte opcional a vários perfis (`openclaw`, `work`, `remote`, ...).

Este navegador **não** é o que você usa no dia a dia. Ele é uma superfície segura e isolada para
automação e verificação pelo agente.

## Início rápido

```bash
openclaw browser --browser-profile openclaw status
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw open https://example.com
openclaw browser --browser-profile openclaw snapshot
```

Se você receber “Navegador desativado”, ative-o na configuração (veja abaixo) e reinicie o
Gateway.

Se `openclaw browser` estiver totalmente ausente, ou se o agente disser que a ferramenta de navegador
não está disponível, vá para [Comando ou ferramenta de navegador ausente](/pt-BR/tools/browser#missing-browser-command-or-tool).

## Controle por plugin

A ferramenta `browser` padrão agora é um plugin integrado que é distribuído ativado por
padrão. Isso significa que você pode desativá-la ou substituí-la sem remover o restante do
sistema de plugins do OpenClaw:

```json5
{
  plugins: {
    entries: {
      browser: {
        enabled: false,
      },
    },
  },
}
```

Desative o plugin integrado antes de instalar outro plugin que forneça o
mesmo nome de ferramenta `browser`. A experiência padrão do navegador precisa de ambos:

- `plugins.entries.browser.enabled` não desativado
- `browser.enabled=true`

Se você desativar apenas o plugin, a CLI de navegador integrada (`openclaw browser`),
o método do gateway (`browser.request`), a ferramenta do agente e o serviço padrão de controle do navegador
desaparecem juntos. Sua configuração `browser.*` permanece intacta para que um
plugin substituto a reutilize.

O plugin integrado do navegador também agora é responsável pela implementação de runtime do navegador.
O núcleo mantém apenas auxiliares compartilhados do Plugin SDK, além de reexports de compatibilidade para
caminhos de importação internos mais antigos. Na prática, remover ou substituir o pacote do plugin do navegador
remove o conjunto de recursos do navegador, em vez de deixar um segundo runtime de propriedade do
núcleo para trás.

Alterações na configuração do navegador ainda exigem reiniciar o Gateway para que o plugin integrado
possa registrar novamente seu serviço de navegador com as novas configurações.

## Comando ou ferramenta de navegador ausente

Se `openclaw browser` de repente se tornar um comando desconhecido após uma atualização, ou
se o agente informar que a ferramenta de navegador está ausente, a causa mais comum é uma
lista restritiva em `plugins.allow` que não inclui `browser`.

Exemplo de configuração com problema:

```json5
{
  plugins: {
    allow: ["telegram"],
  },
}
```

Corrija adicionando `browser` à lista de permissões de plugins:

```json5
{
  plugins: {
    allow: ["telegram", "browser"],
  },
}
```

Notas importantes:

- `browser.enabled=true` não é suficiente por si só quando `plugins.allow` está definido.
- `plugins.entries.browser.enabled=true` também não é suficiente por si só quando `plugins.allow` está definido.
- `tools.alsoAllow: ["browser"]` **não** carrega o plugin integrado do navegador. Ele apenas ajusta a política da ferramenta depois que o plugin já foi carregado.
- Se você não precisa de uma lista restritiva de permissões de plugins, remover `plugins.allow` também restaura o comportamento padrão do navegador integrado.

Sintomas típicos:

- `openclaw browser` é um comando desconhecido.
- `browser.request` está ausente.
- O agente informa que a ferramenta de navegador está indisponível ou ausente.

## Perfis: `openclaw` vs `user`

- `openclaw`: navegador gerenciado e isolado (nenhuma extensão necessária).
- `user`: perfil integrado de conexão via Chrome MCP para sua **sessão real do Chrome autenticada**.

Para chamadas da ferramenta de navegador do agente:

- Padrão: use o navegador isolado `openclaw`.
- Prefira `profile="user"` quando sessões autenticadas já existentes importarem e o usuário
  estiver no computador para clicar/aprovar qualquer prompt de conexão.
- `profile` é a substituição explícita quando você quer um modo de navegador específico.

Defina `browser.defaultProfile: "openclaw"` se quiser o modo gerenciado por padrão.

## Configuração

As configurações do navegador ficam em `~/.openclaw/openclaw.json`.

```json5
{
  browser: {
    enabled: true, // padrão: true
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: true, // modo trusted-network padrão
      // allowPrivateNetwork: true, // alias legado
      // hostnameAllowlist: ["*.example.com", "example.com"],
      // allowedHostnames: ["localhost"],
    },
    // cdpUrl: "http://127.0.0.1:18792", // substituição legada de perfil único
    remoteCdpTimeoutMs: 1500, // tempo limite de HTTP do CDP remoto (ms)
    remoteCdpHandshakeTimeoutMs: 3000, // tempo limite do handshake WebSocket do CDP remoto (ms)
    defaultProfile: "openclaw",
    color: "#FF4500",
    headless: false,
    noSandbox: false,
    attachOnly: false,
    executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    profiles: {
      openclaw: { cdpPort: 18800, color: "#FF4500" },
      work: { cdpPort: 18801, color: "#0066CC" },
      user: {
        driver: "existing-session",
        attachOnly: true,
        color: "#00AA00",
      },
      brave: {
        driver: "existing-session",
        attachOnly: true,
        userDataDir: "~/Library/Application Support/BraveSoftware/Brave-Browser",
        color: "#FB542B",
      },
      remote: { cdpUrl: "http://10.0.0.42:9222", color: "#00AA00" },
    },
  },
}
```

Notas:

- O serviço de controle do navegador se vincula ao loopback em uma porta derivada de `gateway.port`
  (padrão: `18791`, que é gateway + 2).
- Se você substituir a porta do Gateway (`gateway.port` ou `OPENCLAW_GATEWAY_PORT`),
  as portas derivadas do navegador mudam para permanecer na mesma “família”.
- `cdpUrl` usa por padrão a porta CDP local gerenciada quando não está definido.
- `remoteCdpTimeoutMs` se aplica a verificações de alcance do CDP remoto (não loopback).
- `remoteCdpHandshakeTimeoutMs` se aplica a verificações de alcance do handshake WebSocket do CDP remoto.
- A navegação/abertura de aba do navegador é protegida contra SSRF antes da navegação e verificada novamente, no melhor esforço, na URL final `http(s)` após a navegação.
- No modo SSRF estrito, a descoberta/sondagem de endpoints CDP remotos (`cdpUrl`, incluindo buscas em `/json/version`) também é verificada.
- `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork` usa `true` por padrão (modelo de rede confiável). Defina como `false` para navegação estrita apenas pública.
- `browser.ssrfPolicy.allowPrivateNetwork` continua com suporte como alias legado por compatibilidade.
- `attachOnly: true` significa “nunca iniciar um navegador local; apenas conectar se ele já estiver em execução”.
- `color` + `color` por perfil tingem a interface do navegador para que você possa ver qual perfil está ativo.
- O perfil padrão é `openclaw` (navegador independente gerenciado pelo OpenClaw). Use `defaultProfile: "user"` para optar pelo navegador autenticado do usuário.
- Ordem de autodetecção: navegador padrão do sistema se for baseado em Chromium; caso contrário Chrome → Brave → Edge → Chromium → Chrome Canary.
- Perfis `openclaw` locais atribuem automaticamente `cdpPort`/`cdpUrl` — defina esses valores apenas para CDP remoto.
- `driver: "existing-session"` usa Chrome DevTools MCP em vez de CDP bruto. Não
  defina `cdpUrl` para esse driver.
- Defina `browser.profiles.<name>.userDataDir` quando um perfil existing-session
  deve se conectar a um perfil de usuário Chromium não padrão, como Brave ou Edge.

## Usar Brave (ou outro navegador baseado em Chromium)

Se o seu navegador **padrão do sistema** for baseado em Chromium (Chrome/Brave/Edge/etc),
o OpenClaw o usa automaticamente. Defina `browser.executablePath` para substituir a
autodetecção:

Exemplo na CLI:

```bash
openclaw config set browser.executablePath "/usr/bin/google-chrome"
```

```json5
// macOS
{
  browser: {
    executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
  }
}

// Windows
{
  browser: {
    executablePath: "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
  }
}

// Linux
{
  browser: {
    executablePath: "/usr/bin/brave-browser"
  }
}
```

## Controle local vs remoto

- **Controle local (padrão):** o Gateway inicia o serviço de controle em loopback e pode iniciar um navegador local.
- **Controle remoto (host de nó):** execute um host de nó na máquina que tem o navegador; o Gateway encaminha as ações do navegador para ele.
- **CDP remoto:** defina `browser.profiles.<name>.cdpUrl` (ou `browser.cdpUrl`) para
  se conectar a um navegador remoto baseado em Chromium. Nesse caso, o OpenClaw não iniciará um navegador local.

O comportamento de parada difere por modo de perfil:

- perfis locais gerenciados: `openclaw browser stop` interrompe o processo do navegador que
  o OpenClaw iniciou
- perfis somente de conexão e CDP remoto: `openclaw browser stop` fecha a sessão de controle ativa
  e libera as substituições de emulação do Playwright/CDP (viewport,
  esquema de cores, localidade, fuso horário, modo offline e estado semelhante), mesmo
  que nenhum processo de navegador tenha sido iniciado pelo OpenClaw

URLs de CDP remoto podem incluir autenticação:

- Tokens de query (por exemplo, `https://provider.example?token=<token>`)
- Autenticação HTTP Basic (por exemplo, `https://user:pass@provider.example`)

O OpenClaw preserva a autenticação ao chamar endpoints `/json/*` e ao se conectar
ao WebSocket do CDP. Prefira variáveis de ambiente ou gerenciadores de segredos para
tokens em vez de confirmá-los em arquivos de configuração.

## Proxy de navegador do nó (padrão sem configuração)

Se você executar um **host de nó** na máquina que tem o navegador, o OpenClaw pode
rotear automaticamente chamadas da ferramenta de navegador para esse nó sem nenhuma configuração extra de navegador.
Este é o caminho padrão para gateways remotos.

Notas:

- O host de nó expõe seu servidor local de controle de navegador por meio de um **comando proxy**.
- Os perfis vêm da própria configuração `browser.profiles` do nó (igual à local).
- `nodeHost.browserProxy.allowProfiles` é opcional. Deixe vazio para o comportamento legado/padrão: todos os perfis configurados permanecem acessíveis por meio do proxy, incluindo rotas de criação/exclusão de perfil.
- Se você definir `nodeHost.browserProxy.allowProfiles`, o OpenClaw trata isso como um limite de menor privilégio: apenas perfis na lista de permissões podem ser direcionados, e rotas persistentes de criação/exclusão de perfil são bloqueadas na superfície do proxy.
- Desative se não quiser isso:
  - No nó: `nodeHost.browserProxy.enabled=false`
  - No gateway: `gateway.nodes.browser.mode="off"`

## Browserless (CDP remoto hospedado)

[Browserless](https://browserless.io) é um serviço hospedado de Chromium que expõe
URLs de conexão CDP por HTTPS e WebSocket. O OpenClaw pode usar qualquer uma das formas, mas
para um perfil de navegador remoto a opção mais simples é a URL WebSocket direta
da documentação de conexão do Browserless.

Exemplo:

```json5
{
  browser: {
    enabled: true,
    defaultProfile: "browserless",
    remoteCdpTimeoutMs: 2000,
    remoteCdpHandshakeTimeoutMs: 4000,
    profiles: {
      browserless: {
        cdpUrl: "wss://production-sfo.browserless.io?token=<BROWSERLESS_API_KEY>",
        color: "#00AA00",
      },
    },
  },
}
```

Notas:

- Substitua `<BROWSERLESS_API_KEY>` pelo seu token real do Browserless.
- Escolha o endpoint de região que corresponda à sua conta do Browserless (veja a documentação deles).
- Se o Browserless fornecer uma URL base HTTPS, você pode convertê-la para
  `wss://` para uma conexão CDP direta ou manter a URL HTTPS e deixar o OpenClaw
  descobrir `/json/version`.

## Provedores CDP WebSocket diretos

Alguns serviços hospedados de navegador expõem um endpoint **WebSocket direto** em vez da
descoberta CDP padrão baseada em HTTP (`/json/version`). O OpenClaw oferece suporte a ambos:

- **Endpoints HTTP(S)** — o OpenClaw chama `/json/version` para descobrir a
  URL do depurador WebSocket e então se conecta.
- **Endpoints WebSocket** (`ws://` / `wss://`) — o OpenClaw se conecta diretamente,
  ignorando `/json/version`. Use isso para serviços como
  [Browserless](https://browserless.io),
  [Browserbase](https://www.browserbase.com), ou qualquer provedor que forneça uma
  URL WebSocket.

### Browserbase

[Browserbase](https://www.browserbase.com) é uma plataforma em nuvem para executar
navegadores headless com resolução de CAPTCHA integrada, modo furtivo e
proxies residenciais.

```json5
{
  browser: {
    enabled: true,
    defaultProfile: "browserbase",
    remoteCdpTimeoutMs: 3000,
    remoteCdpHandshakeTimeoutMs: 5000,
    profiles: {
      browserbase: {
        cdpUrl: "wss://connect.browserbase.com?apiKey=<BROWSERBASE_API_KEY>",
        color: "#F97316",
      },
    },
  },
}
```

Notas:

- [Cadastre-se](https://www.browserbase.com/sign-up) e copie sua **API Key**
  do [painel Overview](https://www.browserbase.com/overview).
- Substitua `<BROWSERBASE_API_KEY>` pela sua API key real do Browserbase.
- O Browserbase cria automaticamente uma sessão de navegador na conexão WebSocket, portanto
  nenhuma etapa manual de criação de sessão é necessária.
- O plano gratuito permite uma sessão simultânea e uma hora de navegador por mês.
  Veja os [preços](https://www.browserbase.com/pricing) para os limites dos planos pagos.
- Veja a [documentação do Browserbase](https://docs.browserbase.com) para a
  referência completa da API, guias de SDK e exemplos de integração.

## Segurança

Ideias principais:

- O controle do navegador é apenas por loopback; o acesso flui pela autenticação do Gateway ou pelo emparelhamento de nó.
- A API HTTP independente do navegador em loopback usa **apenas autenticação por segredo compartilhado**:
  bearer auth com token do gateway, `x-openclaw-password`, ou autenticação HTTP Basic com a
  senha configurada do gateway.
- Cabeçalhos de identidade do Tailscale Serve e `gateway.auth.mode: "trusted-proxy"` **não**
  autenticam esta API independente do navegador em loopback.
- Se o controle do navegador estiver ativado e nenhuma autenticação por segredo compartilhado estiver configurada, o OpenClaw
  gera automaticamente `gateway.auth.token` na inicialização e o persiste na configuração.
- O OpenClaw **não** gera automaticamente esse token quando `gateway.auth.mode` já é
  `password`, `none` ou `trusted-proxy`.
- Mantenha o Gateway e quaisquer hosts de nó em uma rede privada (Tailscale); evite exposição pública.
- Trate URLs/tokens remotos de CDP como segredos; prefira variáveis de ambiente ou um gerenciador de segredos.

Dicas para CDP remoto:

- Prefira endpoints criptografados (HTTPS ou WSS) e tokens de curta duração quando possível.
- Evite incorporar tokens de longa duração diretamente em arquivos de configuração.

## Perfis (vários navegadores)

O OpenClaw oferece suporte a vários perfis nomeados (configurações de roteamento). Os perfis podem ser:

- **gerenciados pelo openclaw**: uma instância dedicada de navegador baseado em Chromium com seu próprio diretório de dados de usuário + porta CDP
- **remoto**: uma URL CDP explícita (navegador baseado em Chromium em execução em outro lugar)
- **sessão existente**: seu perfil atual do Chrome via conexão automática do Chrome DevTools MCP

Padrões:

- O perfil `openclaw` é criado automaticamente se estiver ausente.
- O perfil `user` é integrado para conexão de sessão existente do Chrome MCP.
- Perfis de sessão existente são opt-in além de `user`; crie-os com `--driver existing-session`.
- As portas CDP locais são alocadas de **18800–18899** por padrão.
- Excluir um perfil move seu diretório de dados local para a Lixeira.

Todos os endpoints de controle aceitam `?profile=<name>`; a CLI usa `--browser-profile`.

## Sessão existente via Chrome DevTools MCP

O OpenClaw também pode se conectar a um perfil de navegador baseado em Chromium já em execução por meio do
servidor oficial Chrome DevTools MCP. Isso reutiliza as abas e o estado de login
já abertos nesse perfil de navegador.

Referências oficiais de contexto e configuração:

- [Chrome for Developers: Use Chrome DevTools MCP with your browser session](https://developer.chrome.com/blog/chrome-devtools-mcp-debug-your-browser-session)
- [Chrome DevTools MCP README](https://github.com/ChromeDevTools/chrome-devtools-mcp)

Perfil integrado:

- `user`

Opcional: crie seu próprio perfil personalizado de sessão existente se quiser um
nome, cor ou diretório de dados do navegador diferente.

Comportamento padrão:

- O perfil integrado `user` usa conexão automática do Chrome MCP, que mira o
  perfil local padrão do Google Chrome.

Use `userDataDir` para Brave, Edge, Chromium ou um perfil Chrome não padrão:

```json5
{
  browser: {
    profiles: {
      brave: {
        driver: "existing-session",
        attachOnly: true,
        userDataDir: "~/Library/Application Support/BraveSoftware/Brave-Browser",
        color: "#FB542B",
      },
    },
  },
}
```

Então, no navegador correspondente:

1. Abra a página de inspeção desse navegador para depuração remota.
2. Ative a depuração remota.
3. Mantenha o navegador em execução e aprove o prompt de conexão quando o OpenClaw se conectar.

Páginas comuns de inspeção:

- Chrome: `chrome://inspect/#remote-debugging`
- Brave: `brave://inspect/#remote-debugging`
- Edge: `edge://inspect/#remote-debugging`

Teste rápido de conexão ao vivo:

```bash
openclaw browser --browser-profile user start
openclaw browser --browser-profile user status
openclaw browser --browser-profile user tabs
openclaw browser --browser-profile user snapshot --format ai
```

Como é o sucesso:

- `status` mostra `driver: existing-session`
- `status` mostra `transport: chrome-mcp`
- `status` mostra `running: true`
- `tabs` lista as abas do navegador que já estavam abertas
- `snapshot` retorna refs da aba ativa selecionada

O que verificar se a conexão não funcionar:

- o navegador baseado em Chromium de destino está na versão `144+`
- a depuração remota está ativada na página de inspeção desse navegador
- o navegador exibiu o prompt de consentimento de conexão e você o aceitou
- `openclaw doctor` migra a configuração antiga de navegador baseada em extensão e verifica se
  o Chrome está instalado localmente para perfis padrão de conexão automática, mas não pode
  ativar a depuração remota no lado do navegador para você

Uso pelo agente:

- Use `profile="user"` quando precisar do estado do navegador autenticado do usuário.
- Se você usa um perfil personalizado de sessão existente, passe esse nome de perfil explícito.
- Só escolha esse modo quando o usuário estiver no computador para aprovar o
  prompt de conexão.
- o Gateway ou host de nó pode iniciar `npx chrome-devtools-mcp@latest --autoConnect`

Notas:

- Esse caminho tem mais risco do que o perfil isolado `openclaw` porque pode
  agir dentro da sua sessão autenticada do navegador.
- O OpenClaw não inicia o navegador para esse driver; ele se conecta apenas a uma
  sessão existente.
- O OpenClaw usa aqui o fluxo oficial `--autoConnect` do Chrome DevTools MCP. Se
  `userDataDir` estiver definido, o OpenClaw o repassa para mirar esse diretório explícito
  de dados de usuário Chromium.
- Capturas de tela de sessão existente oferecem suporte a capturas de página e capturas de elemento com `--ref`
  a partir de snapshots, mas não a seletores CSS `--element`.
- Capturas de tela de página de sessão existente funcionam sem Playwright por meio do Chrome MCP.
  Capturas de elemento baseadas em ref (`--ref`) também funcionam ali, mas `--full-page`
  não pode ser combinado com `--ref` ou `--element`.
- Ações de sessão existente ainda são mais limitadas do que no caminho do navegador
  gerenciado:
  - `click`, `type`, `hover`, `scrollIntoView`, `drag` e `select` exigem
    refs de snapshot em vez de seletores CSS
  - `click` é apenas com botão esquerdo (sem substituições de botão ou modificadores)
  - `type` não oferece suporte a `slowly=true`; use `fill` ou `press`
  - `press` não oferece suporte a `delayMs`
  - `hover`, `scrollIntoView`, `drag`, `select`, `fill` e `evaluate` não
    oferecem suporte a substituições de tempo limite por chamada
  - `select` atualmente oferece suporte apenas a um único valor
- `wait --url` para sessão existente oferece suporte a padrões exatos, de substring e glob
  como outros drivers de navegador. `wait --load networkidle` ainda não é compatível.
- Hooks de upload em sessão existente exigem `ref` ou `inputRef`, oferecem suporte a um arquivo
  por vez e não oferecem suporte ao direcionamento por `element` CSS.
- Hooks de diálogo em sessão existente não oferecem suporte a substituições de tempo limite.
- Alguns recursos ainda exigem o caminho de navegador gerenciado, incluindo ações em lote,
  exportação em PDF, interceptação de download e `responsebody`.
- Sessão existente é local ao host. Se o Chrome estiver em outra máquina ou em um
  namespace de rede diferente, use CDP remoto ou um host de nó.

## Garantias de isolamento

- **Diretório de dados de usuário dedicado**: nunca toca no perfil do seu navegador pessoal.
- **Portas dedicadas**: evita `9222` para prevenir colisões com fluxos de trabalho de desenvolvimento.
- **Controle determinístico de abas**: mira abas por `targetId`, não pela “última aba”.

## Seleção do navegador

Ao iniciar localmente, o OpenClaw escolhe o primeiro disponível:

1. Chrome
2. Brave
3. Edge
4. Chromium
5. Chrome Canary

Você pode substituir isso com `browser.executablePath`.

Plataformas:

- macOS: verifica `/Applications` e `~/Applications`.
- Linux: procura `google-chrome`, `brave`, `microsoft-edge`, `chromium`, etc.
- Windows: verifica locais comuns de instalação.

## API de controle (opcional)

Apenas para integrações locais, o Gateway expõe uma pequena API HTTP em loopback:

- Status/iniciar/parar: `GET /`, `POST /start`, `POST /stop`
- Abas: `GET /tabs`, `POST /tabs/open`, `POST /tabs/focus`, `DELETE /tabs/:targetId`
- Snapshot/captura de tela: `GET /snapshot`, `POST /screenshot`
- Ações: `POST /navigate`, `POST /act`
- Hooks: `POST /hooks/file-chooser`, `POST /hooks/dialog`
- Downloads: `POST /download`, `POST /wait/download`
- Depuração: `GET /console`, `POST /pdf`
- Depuração: `GET /errors`, `GET /requests`, `POST /trace/start`, `POST /trace/stop`, `POST /highlight`
- Rede: `POST /response/body`
- Estado: `GET /cookies`, `POST /cookies/set`, `POST /cookies/clear`
- Estado: `GET /storage/:kind`, `POST /storage/:kind/set`, `POST /storage/:kind/clear`
- Configurações: `POST /set/offline`, `POST /set/headers`, `POST /set/credentials`, `POST /set/geolocation`, `POST /set/media`, `POST /set/timezone`, `POST /set/locale`, `POST /set/device`

Todos os endpoints aceitam `?profile=<name>`.

Se a autenticação do gateway por segredo compartilhado estiver configurada, as rotas HTTP do navegador também exigirão autenticação:

- `Authorization: Bearer <gateway token>`
- `x-openclaw-password: <gateway password>` ou autenticação HTTP Basic com essa senha

Notas:

- Esta API independente do navegador em loopback **não** consome cabeçalhos de identidade de trusted-proxy ou
  Tailscale Serve.
- Se `gateway.auth.mode` for `none` ou `trusted-proxy`, essas rotas de navegador em loopback
  não herdam esses modos com identidade; mantenha-as apenas em loopback.

### Contrato de erro de `/act`

`POST /act` usa uma resposta de erro estruturada para validação no nível da rota e
falhas de política:

```json
{ "error": "<message>", "code": "ACT_*" }
```

Valores atuais de `code`:

- `ACT_KIND_REQUIRED` (HTTP 400): `kind` está ausente ou não é reconhecido.
- `ACT_INVALID_REQUEST` (HTTP 400): a carga da ação falhou na normalização ou validação.
- `ACT_SELECTOR_UNSUPPORTED` (HTTP 400): `selector` foi usado com um tipo de ação não compatível.
- `ACT_EVALUATE_DISABLED` (HTTP 403): `evaluate` (ou `wait --fn`) está desativado por configuração.
- `ACT_TARGET_ID_MISMATCH` (HTTP 403): `targetId` de nível superior ou em lote entra em conflito com o alvo da solicitação.
- `ACT_EXISTING_SESSION_UNSUPPORTED` (HTTP 501): a ação não é compatível com perfis de sessão existente.

Outras falhas de runtime ainda podem retornar `{ "error": "<message>" }` sem um
campo `code`.

### Requisito do Playwright

Alguns recursos (navigate/act/AI snapshot/role snapshot, capturas de tela de elementos,
PDF) exigem Playwright. Se o Playwright não estiver instalado, esses endpoints retornam
um erro 501 claro.

O que ainda funciona sem Playwright:

- Snapshots ARIA
- Capturas de tela de página para o navegador gerenciado `openclaw` quando um WebSocket
  CDP por aba está disponível
- Capturas de tela de página para perfis `existing-session` / Chrome MCP
- Capturas de tela baseadas em ref (`--ref`) para `existing-session` a partir da saída de snapshot

O que ainda exige Playwright:

- `navigate`
- `act`
- Snapshots AI / snapshots de função
- Capturas de tela de elemento por seletor CSS (`--element`)
- Exportação completa de PDF do navegador

Capturas de tela de elemento também rejeitam `--full-page`; a rota retorna `fullPage is
not supported for element screenshots`.

Se você vir `Playwright is not available in this gateway build`, instale o pacote completo
do Playwright (não `playwright-core`) e reinicie o gateway, ou reinstale o
OpenClaw com suporte a navegador.

#### Instalação do Playwright no Docker

Se o seu Gateway roda em Docker, evite `npx playwright` (conflitos de override do npm).
Use a CLI incluída em vez disso:

```bash
docker compose run --rm openclaw-cli \
  node /app/node_modules/playwright-core/cli.js install chromium
```

Para persistir downloads do navegador, defina `PLAYWRIGHT_BROWSERS_PATH` (por exemplo,
`/home/node/.cache/ms-playwright`) e garanta que `/home/node` seja persistido por meio de
`OPENCLAW_HOME_VOLUME` ou de um bind mount. Veja [Docker](/pt-BR/install/docker).

## Como funciona (internamente)

Fluxo de alto nível:

- Um pequeno **servidor de controle** aceita requisições HTTP.
- Ele se conecta a navegadores baseados em Chromium (Chrome/Brave/Edge/Chromium) por meio de **CDP**.
- Para ações avançadas (clicar/digitar/snapshot/PDF), ele usa **Playwright** sobre
  o CDP.
- Quando o Playwright está ausente, apenas operações que não usam Playwright ficam disponíveis.

Esse design mantém o agente em uma interface estável e determinística, ao mesmo tempo em que permite
trocar navegadores e perfis locais/remotos.

## Referência rápida da CLI

Todos os comandos aceitam `--browser-profile <name>` para direcionar um perfil específico.
Todos os comandos também aceitam `--json` para saída legível por máquina (payloads estáveis).

Básico:

- `openclaw browser status`
- `openclaw browser start`
- `openclaw browser stop`
- `openclaw browser tabs`
- `openclaw browser tab`
- `openclaw browser tab new`
- `openclaw browser tab select 2`
- `openclaw browser tab close 2`
- `openclaw browser open https://example.com`
- `openclaw browser focus abcd1234`
- `openclaw browser close abcd1234`

Inspeção:

- `openclaw browser screenshot`
- `openclaw browser screenshot --full-page`
- `openclaw browser screenshot --ref 12`
- `openclaw browser screenshot --ref e12`
- `openclaw browser snapshot`
- `openclaw browser snapshot --format aria --limit 200`
- `openclaw browser snapshot --interactive --compact --depth 6`
- `openclaw browser snapshot --efficient`
- `openclaw browser snapshot --labels`
- `openclaw browser snapshot --selector "#main" --interactive`
- `openclaw browser snapshot --frame "iframe#main" --interactive`
- `openclaw browser console --level error`

Observação sobre o ciclo de vida:

- Para perfis somente de conexão e CDP remoto, `openclaw browser stop` continua sendo o
  comando de limpeza correto após os testes. Ele fecha a sessão de controle ativa e
  limpa substituições temporárias de emulação em vez de encerrar o navegador
  subjacente.
- `openclaw browser errors --clear`
- `openclaw browser requests --filter api --clear`
- `openclaw browser pdf`
- `openclaw browser responsebody "**/api" --max-chars 5000`

Ações:

- `openclaw browser navigate https://example.com`
- `openclaw browser resize 1280 720`
- `openclaw browser click 12 --double`
- `openclaw browser click e12 --double`
- `openclaw browser type 23 "hello" --submit`
- `openclaw browser press Enter`
- `openclaw browser hover 44`
- `openclaw browser scrollintoview e12`
- `openclaw browser drag 10 11`
- `openclaw browser select 9 OptionA OptionB`
- `openclaw browser download e12 report.pdf`
- `openclaw browser waitfordownload report.pdf`
- `openclaw browser upload /tmp/openclaw/uploads/file.pdf`
- `openclaw browser fill --fields '[{"ref":"1","type":"text","value":"Ada"}]'`
- `openclaw browser dialog --accept`
- `openclaw browser wait --text "Done"`
- `openclaw browser wait "#main" --url "**/dash" --load networkidle --fn "window.ready===true"`
- `openclaw browser evaluate --fn '(el) => el.textContent' --ref 7`
- `openclaw browser highlight e12`
- `openclaw browser trace start`
- `openclaw browser trace stop`

Estado:

- `openclaw browser cookies`
- `openclaw browser cookies set session abc123 --url "https://example.com"`
- `openclaw browser cookies clear`
- `openclaw browser storage local get`
- `openclaw browser storage local set theme dark`
- `openclaw browser storage session clear`
- `openclaw browser set offline on`
- `openclaw browser set headers --headers-json '{"X-Debug":"1"}'`
- `openclaw browser set credentials user pass`
- `openclaw browser set credentials --clear`
- `openclaw browser set geo 37.7749 -122.4194 --origin "https://example.com"`
- `openclaw browser set geo --clear`
- `openclaw browser set media dark`
- `openclaw browser set timezone America/New_York`
- `openclaw browser set locale en-US`
- `openclaw browser set device "iPhone 14"`

Notas:

- `upload` e `dialog` são chamadas de **preparação**; execute-as antes do clique/tecla
  que aciona o seletor de arquivos/caixa de diálogo.
- Os caminhos de saída de download e trace são restritos às raízes temporárias do OpenClaw:
  - traces: `/tmp/openclaw` (fallback: `${os.tmpdir()}/openclaw`)
  - downloads: `/tmp/openclaw/downloads` (fallback: `${os.tmpdir()}/openclaw/downloads`)
- Os caminhos de upload são restritos a uma raiz temporária de uploads do OpenClaw:
  - uploads: `/tmp/openclaw/uploads` (fallback: `${os.tmpdir()}/openclaw/uploads`)
- `upload` também pode definir diretamente entradas de arquivo por meio de `--input-ref` ou `--element`.
- `snapshot`:
  - `--format ai` (padrão quando o Playwright está instalado): retorna um snapshot AI com refs numéricos (`aria-ref="<n>"`).
  - `--format aria`: retorna a árvore de acessibilidade (sem refs; apenas inspeção).
  - `--efficient` (ou `--mode efficient`): preset compacto de snapshot por função (interativo + compacto + profundidade + `maxChars` menor).
  - Padrão de configuração (apenas ferramenta/CLI): defina `browser.snapshotDefaults.mode: "efficient"` para usar snapshots eficientes quando quem chama não passar um modo (veja [Configuração do Gateway](/pt-BR/gateway/configuration-reference#browser)).
  - Opções de snapshot por função (`--interactive`, `--compact`, `--depth`, `--selector`) forçam um snapshot baseado em função com refs como `ref=e12`.
  - `--frame "<iframe selector>"` limita snapshots por função a um iframe (combina com refs por função como `e12`).
  - `--interactive` gera uma lista simples e fácil de escolher de elementos interativos (melhor para conduzir ações).
  - `--labels` adiciona uma captura de tela apenas da viewport com rótulos de ref sobrepostos (imprime `MEDIA:<path>`).
- `click`/`type`/etc exigem um `ref` de `snapshot` (seja numérico `12` ou ref por função `e12`).
  Seletores CSS intencionalmente não têm suporte para ações.

## Snapshots e refs

O OpenClaw oferece suporte a dois estilos de “snapshot”:

- **Snapshot AI (refs numéricos)**: `openclaw browser snapshot` (padrão; `--format ai`)
  - Saída: um snapshot em texto que inclui refs numéricos.
  - Ações: `openclaw browser click 12`, `openclaw browser type 23 "hello"`.
  - Internamente, o ref é resolvido via `aria-ref` do Playwright.

- **Snapshot por função (refs por função como `e12`)**: `openclaw browser snapshot --interactive` (ou `--compact`, `--depth`, `--selector`, `--frame`)
  - Saída: uma lista/árvore baseada em função com `[ref=e12]` (e opcionalmente `[nth=1]`).
  - Ações: `openclaw browser click e12`, `openclaw browser highlight e12`.
  - Internamente, o ref é resolvido via `getByRole(...)` (mais `nth()` para duplicatas).
  - Adicione `--labels` para incluir uma captura de tela da viewport com rótulos `e12` sobrepostos.

Comportamento dos refs:

- Refs **não são estáveis entre navegações**; se algo falhar, execute `snapshot` novamente e use um ref novo.
- Se o snapshot por função foi obtido com `--frame`, os refs por função ficam limitados a esse iframe até o próximo snapshot por função.

## Recursos avançados de espera

Você pode esperar por mais do que apenas tempo/texto:

- Esperar por URL (globs compatíveis com Playwright):
  - `openclaw browser wait --url "**/dash"`
- Esperar por estado de carregamento:
  - `openclaw browser wait --load networkidle`
- Esperar por um predicado JS:
  - `openclaw browser wait --fn "window.ready===true"`
- Esperar por um seletor ficar visível:
  - `openclaw browser wait "#main"`

Esses recursos podem ser combinados:

```bash
openclaw browser wait "#main" \
  --url "**/dash" \
  --load networkidle \
  --fn "window.ready===true" \
  --timeout-ms 15000
```

## Fluxos de depuração

Quando uma ação falhar (por exemplo, “not visible”, “strict mode violation”, “covered”):

1. `openclaw browser snapshot --interactive`
2. Use `click <ref>` / `type <ref>` (prefira refs por função no modo interativo)
3. Se ainda falhar: `openclaw browser highlight <ref>` para ver o que o Playwright está mirando
4. Se a página se comportar de forma estranha:
   - `openclaw browser errors --clear`
   - `openclaw browser requests --filter api --clear`
5. Para depuração profunda: grave um trace:
   - `openclaw browser trace start`
   - reproduza o problema
   - `openclaw browser trace stop` (imprime `TRACE:<path>`)

## Saída JSON

`--json` é para scripts e ferramentas estruturadas.

Exemplos:

```bash
openclaw browser status --json
openclaw browser snapshot --interactive --json
openclaw browser requests --filter api --json
openclaw browser cookies --json
```

Snapshots por função em JSON incluem `refs` além de um pequeno bloco `stats` (linhas/chars/refs/interactive) para que ferramentas possam analisar tamanho e densidade do payload.

## Ajustes de estado e ambiente

Eles são úteis para fluxos de trabalho do tipo “faça o site se comportar como X”:

- Cookies: `cookies`, `cookies set`, `cookies clear`
- Storage: `storage local|session get|set|clear`
- Offline: `set offline on|off`
- Headers: `set headers --headers-json '{"X-Debug":"1"}'` (o legado `set headers --json '{"X-Debug":"1"}'` continua com suporte)
- Autenticação HTTP basic: `set credentials user pass` (ou `--clear`)
- Geolocalização: `set geo <lat> <lon> --origin "https://example.com"` (ou `--clear`)
- Mídia: `set media dark|light|no-preference|none`
- Fuso horário / localidade: `set timezone ...`, `set locale ...`
- Dispositivo / viewport:
  - `set device "iPhone 14"` (presets de dispositivo do Playwright)
  - `set viewport 1280 720`

## Segurança e privacidade

- O perfil de navegador openclaw pode conter sessões autenticadas; trate-o como algo sensível.
- `browser act kind=evaluate` / `openclaw browser evaluate` e `wait --fn`
  executam JavaScript arbitrário no contexto da página. Injeção de prompt pode conduzir
  isso. Desative com `browser.evaluateEnabled=false` se você não precisar disso.
- Para logins e observações sobre anti-bot (X/Twitter etc.), veja [Login no navegador + postagem no X/Twitter](/pt-BR/tools/browser-login).
- Mantenha o Gateway/host de nó privado (apenas loopback ou tailnet).
- Endpoints CDP remotos são poderosos; faça túnel e proteja-os.

Exemplo de modo estrito (bloquear destinos privados/internos por padrão):

```json5
{
  browser: {
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: false,
      hostnameAllowlist: ["*.example.com", "example.com"],
      allowedHostnames: ["localhost"], // permissão exata opcional
    },
  },
}
```

## Solução de problemas

Para problemas específicos de Linux (especialmente Chromium via snap), veja
[Solução de problemas do navegador](/pt-BR/tools/browser-linux-troubleshooting).

Para configurações com Gateway no WSL2 + Chrome no Windows em hosts separados, veja
[Solução de problemas de WSL2 + Windows + CDP remoto do Chrome](/pt-BR/tools/browser-wsl2-windows-remote-cdp-troubleshooting).

## Ferramentas do agente + como o controle funciona

O agente recebe **uma ferramenta** para automação do navegador:

- `browser` — status/start/stop/tabs/open/focus/close/snapshot/screenshot/navigate/act

Como isso se mapeia:

- `browser snapshot` retorna uma árvore de UI estável (AI ou ARIA).
- `browser act` usa os IDs `ref` do snapshot para clicar/digitar/arrastar/selecionar.
- `browser screenshot` captura pixels (página inteira ou elemento).
- `browser` aceita:
  - `profile` para escolher um perfil nomeado do navegador (openclaw, chrome ou CDP remoto).
  - `target` (`sandbox` | `host` | `node`) para selecionar onde o navegador está.
  - Em sessões em sandbox, `target: "host"` exige `agents.defaults.sandbox.browser.allowHostControl=true`.
  - Se `target` for omitido: sessões em sandbox usam `sandbox` por padrão, sessões sem sandbox usam `host` por padrão.
  - Se um nó com capacidade de navegador estiver conectado, a ferramenta poderá ser roteada automaticamente para ele, a menos que você fixe `target="host"` ou `target="node"`.

Isso mantém o agente determinístico e evita seletores frágeis.

## Relacionado

- [Visão geral das ferramentas](/pt-BR/tools) — todas as ferramentas disponíveis para o agente
- [Sandboxing](/pt-BR/gateway/sandboxing) — controle do navegador em ambientes em sandbox
- [Segurança](/pt-BR/gateway/security) — riscos e fortalecimento do controle do navegador
