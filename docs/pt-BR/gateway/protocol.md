---
read_when:
    - Implementando ou atualizando clientes WS do Gateway
    - Depurando incompatibilidades de protocolo ou falhas de conexão
    - Regenerando esquema/modelos de protocolo
summary: 'Protocolo WebSocket do Gateway: handshake, frames, controle de versão'
title: Protocolo do Gateway
x-i18n:
    generated_at: "2026-04-16T05:37:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: 683e61ebe993a2d739bc34860060b0e3eda36b5c57267a2bcc03d177ec612fb3
    source_path: gateway/protocol.md
    workflow: 15
---

# Protocolo do Gateway (WebSocket)

O protocolo WS do Gateway é o **plano de controle único + transporte de nós** do
OpenClaw. Todos os clientes (CLI, interface web, app para macOS, nós iOS/Android,
nós headless) se conectam por WebSocket e declaram seu **papel** + **escopo** no
momento do handshake.

## Transporte

- WebSocket, frames de texto com payloads JSON.
- O primeiro frame **deve** ser uma requisição `connect`.

## Handshake (connect)

Gateway → Cliente (desafio pré-conexão):

```json
{
  "type": "event",
  "event": "connect.challenge",
  "payload": { "nonce": "…", "ts": 1737264000000 }
}
```

Cliente → Gateway:

```json
{
  "type": "req",
  "id": "…",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "cli",
      "version": "1.2.3",
      "platform": "macos",
      "mode": "operator"
    },
    "role": "operator",
    "scopes": ["operator.read", "operator.write"],
    "caps": [],
    "commands": [],
    "permissions": {},
    "auth": { "token": "…" },
    "locale": "en-US",
    "userAgent": "openclaw-cli/1.2.3",
    "device": {
      "id": "device_fingerprint",
      "publicKey": "…",
      "signature": "…",
      "signedAt": 1737264000000,
      "nonce": "…"
    }
  }
}
```

Gateway → Cliente:

```json
{
  "type": "res",
  "id": "…",
  "ok": true,
  "payload": {
    "type": "hello-ok",
    "protocol": 3,
    "server": { "version": "…", "connId": "…" },
    "features": { "methods": ["…"], "events": ["…"] },
    "snapshot": { "…": "…" },
    "policy": {
      "maxPayload": 26214400,
      "maxBufferedBytes": 52428800,
      "tickIntervalMs": 15000
    }
  }
}
```

`server`, `features`, `snapshot` e `policy` são todos obrigatórios pelo esquema
(`src/gateway/protocol/schema/frames.ts`). `auth` e `canvasHostUrl` são opcionais.

Quando um token de dispositivo é emitido, `hello-ok` também inclui:

```json
{
  "auth": {
    "deviceToken": "…",
    "role": "operator",
    "scopes": ["operator.read", "operator.write"]
  }
}
```

Durante a transferência confiável de bootstrap, `hello-ok.auth` também pode incluir
entradas de papel adicionais delimitadas em `deviceTokens`:

```json
{
  "auth": {
    "deviceToken": "…",
    "role": "node",
    "scopes": [],
    "deviceTokens": [
      {
        "deviceToken": "…",
        "role": "operator",
        "scopes": ["operator.approvals", "operator.read", "operator.talk.secrets", "operator.write"]
      }
    ]
  }
}
```

Para o fluxo de bootstrap integrado de node/operator, o token principal do nó permanece com
`scopes: []` e qualquer token de operador transferido permanece delimitado à allowlist
do operador de bootstrap (`operator.approvals`, `operator.read`,
`operator.talk.secrets`, `operator.write`). As verificações de escopo do bootstrap continuam
prefixadas por papel: entradas de operador só satisfazem requisições de operador, e papéis
não operadores ainda precisam de escopos sob o prefixo do seu próprio papel.

### Exemplo de nó

```json
{
  "type": "req",
  "id": "…",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "ios-node",
      "version": "1.2.3",
      "platform": "ios",
      "mode": "node"
    },
    "role": "node",
    "scopes": [],
    "caps": ["camera", "canvas", "screen", "location", "voice"],
    "commands": ["camera.snap", "canvas.navigate", "screen.record", "location.get"],
    "permissions": { "camera.capture": true, "screen.record": false },
    "auth": { "token": "…" },
    "locale": "en-US",
    "userAgent": "openclaw-ios/1.2.3",
    "device": {
      "id": "device_fingerprint",
      "publicKey": "…",
      "signature": "…",
      "signedAt": 1737264000000,
      "nonce": "…"
    }
  }
}
```

## Enquadramento

- **Requisição**: `{type:"req", id, method, params}`
- **Resposta**: `{type:"res", id, ok, payload|error}`
- **Evento**: `{type:"event", event, payload, seq?, stateVersion?}`

Métodos com efeitos colaterais exigem **chaves de idempotência** (veja o esquema).

## Papéis + escopos

### Papéis

- `operator` = cliente do plano de controle (CLI/interface/automação).
- `node` = host de capacidades (camera/screen/canvas/system.run).

### Escopos (operator)

Escopos comuns:

- `operator.read`
- `operator.write`
- `operator.admin`
- `operator.approvals`
- `operator.pairing`
- `operator.talk.secrets`

`talk.config` com `includeSecrets: true` exige `operator.talk.secrets`
(ou `operator.admin`).

Métodos RPC do Gateway registrados por Plugin podem solicitar seu próprio escopo de operator, mas
prefixos administrativos reservados do núcleo (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`) sempre são resolvidos para `operator.admin`.

O escopo do método é apenas o primeiro controle. Alguns comandos slash acessados por
`chat.send` aplicam verificações em nível de comando mais restritas além disso. Por exemplo, escritas
persistentes de `/config set` e `/config unset` exigem `operator.admin`.

`node.pair.approve` também tem uma verificação de escopo adicional no momento da aprovação além do
escopo base do método:

- requisições sem comando: `operator.pairing`
- requisições com comandos de nó sem exec: `operator.pairing` + `operator.write`
- requisições que incluem `system.run`, `system.run.prepare` ou `system.which`:
  `operator.pairing` + `operator.admin`

### Caps/commands/permissions (node)

Nós declaram reivindicações de capacidade no momento da conexão:

- `caps`: categorias de capacidade de alto nível.
- `commands`: allowlist de comandos para invoke.
- `permissions`: toggles granulares (por exemplo, `screen.record`, `camera.capture`).

O Gateway trata isso como **reivindicações** e aplica allowlists no lado do servidor.

## Presença

- `system-presence` retorna entradas indexadas pela identidade do dispositivo.
- As entradas de presença incluem `deviceId`, `roles` e `scopes` para que as interfaces possam mostrar uma única linha por dispositivo
  mesmo quando ele se conecta como **operator** e **node** ao mesmo tempo.

## Famílias comuns de métodos RPC

Esta página não é um dump completo gerado, mas a superfície WS pública é mais ampla
do que os exemplos de handshake/auth acima. Estas são as principais famílias de métodos que
o Gateway expõe atualmente.

`hello-ok.features.methods` é uma lista conservadora de descoberta construída a partir de
`src/gateway/server-methods-list.ts` mais as exportações de métodos de plugins/canais carregados.
Trate isso como descoberta de recursos, não como um dump gerado de todos os helpers chamáveis
implementados em `src/gateway/server-methods/*.ts`.

### Sistema e identidade

- `health` retorna o snapshot de saúde do gateway em cache ou recém-sondado.
- `status` retorna o resumo do gateway no estilo `/status`; campos sensíveis são
  incluídos apenas para clientes operator com escopo de admin.
- `gateway.identity.get` retorna a identidade do dispositivo do gateway usada pelos fluxos de relay e
  pareamento.
- `system-presence` retorna o snapshot de presença atual para dispositivos
  operator/node conectados.
- `system-event` acrescenta um evento de sistema e pode atualizar/transmitir contexto
  de presença.
- `last-heartbeat` retorna o evento Heartbeat persistido mais recente.
- `set-heartbeats` ativa ou desativa o processamento de Heartbeat no gateway.

### Modelos e uso

- `models.list` retorna o catálogo de modelos permitido em tempo de execução.
- `usage.status` retorna janelas de uso do provedor/resumos de cota restante.
- `usage.cost` retorna resumos agregados de uso de custo para um intervalo de datas.
- `doctor.memory.status` retorna a prontidão de memória vetorial / embeddings para o
  workspace padrão ativo do agente.
- `sessions.usage` retorna resumos de uso por sessão.
- `sessions.usage.timeseries` retorna séries temporais de uso para uma sessão.
- `sessions.usage.logs` retorna entradas de log de uso para uma sessão.

### Canais e helpers de login

- `channels.status` retorna resumos de status de canais/plugins integrados + empacotados.
- `channels.logout` desconecta uma conta/canal específico quando o canal
  oferece suporte a logout.
- `web.login.start` inicia um fluxo de login por QR/web para o provedor de canal web
  atual com suporte a QR.
- `web.login.wait` aguarda a conclusão desse fluxo de login por QR/web e inicia o
  canal em caso de sucesso.
- `push.test` envia um push APNs de teste para um nó iOS registrado.
- `voicewake.get` retorna os gatilhos de palavra de ativação armazenados.
- `voicewake.set` atualiza os gatilhos de palavra de ativação e transmite a alteração.

### Mensageria e logs

- `send` é o RPC direto de entrega de saída para envios direcionados por canal/conta/thread
  fora do executor de chat.
- `logs.tail` retorna a cauda configurada dos logs de arquivo do gateway com cursor/limite e
  controles de bytes máximos.

### Talk e TTS

- `talk.config` retorna o payload efetivo de configuração do Talk; `includeSecrets`
  exige `operator.talk.secrets` (ou `operator.admin`).
- `talk.mode` define/transmite o estado atual do modo Talk para clientes
  WebChat/Control UI.
- `talk.speak` sintetiza fala por meio do provedor de fala Talk ativo.
- `tts.status` retorna o estado de ativação do TTS, provedor ativo, provedores de fallback,
  e o estado de configuração do provedor.
- `tts.providers` retorna o inventário visível de provedores de TTS.
- `tts.enable` e `tts.disable` alternam o estado das preferências de TTS.
- `tts.setProvider` atualiza o provedor de TTS preferido.
- `tts.convert` executa conversão pontual de texto para fala.

### Secrets, config, update e wizard

- `secrets.reload` resolve novamente os SecretRefs ativos e troca o estado de segredos em tempo de execução
  apenas em caso de sucesso completo.
- `secrets.resolve` resolve atribuições de segredos direcionadas a comandos para um conjunto específico
  de comando/alvo.
- `config.get` retorna o snapshot e hash da configuração atual.
- `config.set` grava um payload de configuração validado.
- `config.patch` mescla uma atualização parcial de configuração.
- `config.apply` valida + substitui o payload completo de configuração.
- `config.schema` retorna o payload do esquema de configuração em tempo de execução usado pela Control UI e
  pelas ferramentas de CLI: esquema, `uiHints`, versão e metadados de geração, incluindo
  metadados de esquema de plugins + canais quando o runtime pode carregá-los. O esquema
  inclui metadados de campo `title` / `description` derivados dos mesmos rótulos
  e textos de ajuda usados pela interface, incluindo ramificações aninhadas de objeto, curinga, item de array
  e composição `anyOf` / `oneOf` / `allOf` quando existe documentação de campo correspondente.
- `config.schema.lookup` retorna um payload de consulta com escopo de caminho para um caminho de configuração:
  caminho normalizado, um nó raso do esquema, `hint` correspondente + `hintPath`, e
  resumos imediatos dos filhos para detalhamento na interface/CLI.
  - Nós de esquema de consulta mantêm a documentação voltada ao usuário e campos comuns de validação:
    `title`, `description`, `type`, `enum`, `const`, `format`, `pattern`,
    limites numéricos/de string/de array/de objeto e flags booleanas como
    `additionalProperties`, `deprecated`, `readOnly`, `writeOnly`.
  - Resumos de filhos expõem `key`, `path` normalizado, `type`, `required`,
    `hasChildren`, além do `hint` / `hintPath` correspondente.
- `update.run` executa o fluxo de atualização do gateway e agenda uma reinicialização apenas quando
  a própria atualização foi bem-sucedida.
- `wizard.start`, `wizard.next`, `wizard.status` e `wizard.cancel` expõem o
  assistente de onboarding por WS RPC.

### Famílias principais existentes

#### Helpers de agente e workspace

- `agents.list` retorna entradas de agentes configuradas.
- `agents.create`, `agents.update` e `agents.delete` gerenciam registros de agentes e
  a ligação com o workspace.
- `agents.files.list`, `agents.files.get` e `agents.files.set` gerenciam os
  arquivos do workspace de bootstrap expostos para um agente.
- `agent.identity.get` retorna a identidade efetiva do assistente para um agente ou
  sessão.
- `agent.wait` aguarda a conclusão de uma execução e retorna o snapshot terminal quando
  disponível.

#### Controle de sessão

- `sessions.list` retorna o índice atual de sessões.
- `sessions.subscribe` e `sessions.unsubscribe` ativam ou desativam assinaturas de eventos
  de mudança de sessão para o cliente WS atual.
- `sessions.messages.subscribe` e `sessions.messages.unsubscribe` ativam ou desativam
  assinaturas de eventos de transcrição/mensagens para uma sessão.
- `sessions.preview` retorna prévias delimitadas da transcrição para chaves específicas
  de sessão.
- `sessions.resolve` resolve ou canonicaliza um destino de sessão.
- `sessions.create` cria uma nova entrada de sessão.
- `sessions.send` envia uma mensagem para uma sessão existente.
- `sessions.steer` é a variante de interrupção e redirecionamento para uma sessão ativa.
- `sessions.abort` aborta o trabalho ativo de uma sessão.
- `sessions.patch` atualiza metadados/substituições de sessão.
- `sessions.reset`, `sessions.delete` e `sessions.compact` executam manutenção
  da sessão.
- `sessions.get` retorna a linha completa armazenada da sessão.
- a execução de chat ainda usa `chat.history`, `chat.send`, `chat.abort` e
  `chat.inject`.
- `chat.history` é normalizado para exibição para clientes de interface: tags de diretiva inline são
  removidas do texto visível, payloads XML de chamada de ferramenta em texto simples (incluindo
  `<tool_call>...</tool_call>`, `<function_call>...</function_call>`,
  `<tool_calls>...</tool_calls>`, `<function_calls>...</function_calls>` e
  blocos truncados de chamada de ferramenta) e tokens de controle do modelo ASCII/full-width vazados
  são removidos, linhas de assistente compostas apenas por tokens silenciosos, como `NO_REPLY` /
  `no_reply` exatos, são omitidas, e linhas grandes demais podem ser substituídas por placeholders.

#### Pareamento de dispositivos e tokens de dispositivo

- `device.pair.list` retorna dispositivos pareados pendentes e aprovados.
- `device.pair.approve`, `device.pair.reject` e `device.pair.remove` gerenciam
  registros de pareamento de dispositivos.
- `device.token.rotate` rotaciona um token de dispositivo pareado dentro dos limites
  aprovados de papel e escopo.
- `device.token.revoke` revoga um token de dispositivo pareado.

#### Pareamento de nós, invoke e trabalho pendente

- `node.pair.request`, `node.pair.list`, `node.pair.approve`,
  `node.pair.reject` e `node.pair.verify` cobrem pareamento de nós e verificação
  de bootstrap.
- `node.list` e `node.describe` retornam o estado conhecido/conectado dos nós.
- `node.rename` atualiza um rótulo de nó pareado.
- `node.invoke` encaminha um comando para um nó conectado.
- `node.invoke.result` retorna o resultado de uma requisição invoke.
- `node.event` transporta eventos originados no nó de volta para o gateway.
- `node.canvas.capability.refresh` atualiza tokens de capacidade de canvas com escopo.
- `node.pending.pull` e `node.pending.ack` são as APIs de fila de nós conectados.
- `node.pending.enqueue` e `node.pending.drain` gerenciam trabalho pendente durável
  para nós offline/desconectados.

#### Famílias de aprovação

- `exec.approval.request`, `exec.approval.get`, `exec.approval.list` e
  `exec.approval.resolve` cobrem requisições pontuais de aprovação de exec, além de
  consulta/reexecução de aprovações pendentes.
- `exec.approval.waitDecision` aguarda uma aprovação pendente de exec e retorna
  a decisão final (ou `null` em caso de timeout).
- `exec.approvals.get` e `exec.approvals.set` gerenciam snapshots da política de aprovação
  de exec do gateway.
- `exec.approvals.node.get` e `exec.approvals.node.set` gerenciam a política local de exec
  do nó via comandos de relay do nó.
- `plugin.approval.request`, `plugin.approval.list`,
  `plugin.approval.waitDecision` e `plugin.approval.resolve` cobrem
  fluxos de aprovação definidos por Plugin.

#### Outras famílias principais

- automação:
  - `wake` agenda uma injeção de texto imediata ou no próximo Heartbeat
  - `cron.list`, `cron.status`, `cron.add`, `cron.update`, `cron.remove`,
    `cron.run`, `cron.runs`
- skills/ferramentas: `commands.list`, `skills.*`, `tools.catalog`, `tools.effective`

### Famílias comuns de eventos

- `chat`: atualizações de chat da interface, como `chat.inject` e outros eventos
  de chat apenas de transcrição.
- `session.message` e `session.tool`: atualizações de transcrição/fluxo de eventos para uma
  sessão assinada.
- `sessions.changed`: o índice ou os metadados da sessão mudaram.
- `presence`: atualizações do snapshot de presença do sistema.
- `tick`: evento periódico de keepalive / vivacidade.
- `health`: atualização do snapshot de saúde do gateway.
- `heartbeat`: atualização do fluxo de eventos Heartbeat.
- `cron`: evento de mudança de execução/trabalho do cron.
- `shutdown`: notificação de desligamento do gateway.
- `node.pair.requested` / `node.pair.resolved`: ciclo de vida do pareamento de nós.
- `node.invoke.request`: transmissão da requisição invoke de nó.
- `device.pair.requested` / `device.pair.resolved`: ciclo de vida do dispositivo pareado.
- `voicewake.changed`: a configuração do gatilho de palavra de ativação mudou.
- `exec.approval.requested` / `exec.approval.resolved`: ciclo de vida da aprovação
  de exec.
- `plugin.approval.requested` / `plugin.approval.resolved`: ciclo de vida da aprovação
  de Plugin.

### Métodos helper de nó

- Nós podem chamar `skills.bins` para buscar a lista atual de executáveis de skill
  para verificações de auto-allow.

### Métodos helper de operator

- Operators podem chamar `commands.list` (`operator.read`) para buscar o inventário de comandos em runtime para um
  agente.
  - `agentId` é opcional; omita-o para ler o workspace padrão do agente.
  - `scope` controla qual superfície o `name` primário segmenta:
    - `text` retorna o token primário do comando de texto sem a `/` inicial
    - `native` e o caminho padrão `both` retornam nomes nativos sensíveis ao provedor
      quando disponíveis
  - `textAliases` carrega aliases slash exatos, como `/model` e `/m`.
  - `nativeName` carrega o nome nativo sensível ao provedor quando ele existe.
  - `provider` é opcional e afeta apenas a nomenclatura nativa mais a disponibilidade
    de comandos nativos de Plugin.
  - `includeArgs=false` omite metadados serializados de argumentos da resposta.
- Operators podem chamar `tools.catalog` (`operator.read`) para buscar o catálogo de ferramentas em runtime para um
  agente. A resposta inclui ferramentas agrupadas e metadados de procedência:
  - `source`: `core` ou `plugin`
  - `pluginId`: proprietário do Plugin quando `source="plugin"`
  - `optional`: se uma ferramenta de Plugin é opcional
- Operators podem chamar `tools.effective` (`operator.read`) para buscar o inventário efetivo de ferramentas em runtime
  para uma sessão.
  - `sessionKey` é obrigatório.
  - O gateway deriva o contexto confiável de runtime do lado do servidor a partir da sessão, em vez de aceitar
    autenticação ou contexto de entrega fornecidos pelo chamador.
  - A resposta tem escopo de sessão e reflete o que a conversa ativa pode usar agora,
    incluindo ferramentas de core, Plugin e canal.
- Operators podem chamar `skills.status` (`operator.read`) para buscar o inventário visível
  de skills para um agente.
  - `agentId` é opcional; omita-o para ler o workspace padrão do agente.
  - A resposta inclui elegibilidade, requisitos ausentes, verificações de configuração e
    opções de instalação sanitizadas sem expor valores brutos de segredos.
- Operators podem chamar `skills.search` e `skills.detail` (`operator.read`) para metadados
  de descoberta do ClawHub.
- Operators podem chamar `skills.install` (`operator.admin`) em dois modos:
  - Modo ClawHub: `{ source: "clawhub", slug, version?, force? }` instala uma
    pasta de skill no diretório `skills/` do workspace padrão do agente.
  - Modo instalador do gateway: `{ name, installId, dangerouslyForceUnsafeInstall?, timeoutMs? }`
    executa uma ação declarada `metadata.openclaw.install` no host do gateway.
- Operators podem chamar `skills.update` (`operator.admin`) em dois modos:
  - O modo ClawHub atualiza um slug rastreado ou todas as instalações do ClawHub rastreadas no
    workspace padrão do agente.
  - O modo Config aplica patch em valores de `skills.entries.<skillKey>`, como `enabled`,
    `apiKey` e `env`.

## Aprovações de exec

- Quando uma requisição de exec precisa de aprovação, o gateway transmite `exec.approval.requested`.
- Clientes operator resolvem chamando `exec.approval.resolve` (exige escopo `operator.approvals`).
- Para `host=node`, `exec.approval.request` deve incluir `systemRunPlan` (`argv`/`cwd`/`rawCommand`/metadados de sessão canônicos). Requisições sem `systemRunPlan` são rejeitadas.
- Após a aprovação, chamadas encaminhadas de `node.invoke system.run` reutilizam esse
  `systemRunPlan` canônico como o contexto autoritativo de comando/cwd/sessão.
- Se um chamador modificar `command`, `rawCommand`, `cwd`, `agentId` ou
  `sessionKey` entre o prepare e o encaminhamento final aprovado de `system.run`, o
  gateway rejeita a execução em vez de confiar no payload modificado.

## Fallback de entrega do agente

- Requisições de `agent` podem incluir `deliver=true` para solicitar entrega de saída.
- `bestEffortDeliver=false` mantém o comportamento estrito: destinos de entrega não resolvidos ou apenas internos retornam `INVALID_REQUEST`.
- `bestEffortDeliver=true` permite fallback para execução apenas em sessão quando nenhuma rota externa entregável pode ser resolvida (por exemplo, sessões internas/webchat ou configurações ambíguas com múltiplos canais).

## Controle de versão

- `PROTOCOL_VERSION` fica em `src/gateway/protocol/schema/protocol-schemas.ts`.
- Clientes enviam `minProtocol` + `maxProtocol`; o servidor rejeita incompatibilidades.
- Esquemas + modelos são gerados a partir de definições TypeBox:
  - `pnpm protocol:gen`
  - `pnpm protocol:gen:swift`
  - `pnpm protocol:check`

### Constantes do cliente

O cliente de referência em `src/gateway/client.ts` usa estes padrões. Os valores são
estáveis no protocolo v3 e são a linha de base esperada para clientes de terceiros.

| Constante                                  | Padrão                                               | Origem                                                     |
| ------------------------------------------ | ---------------------------------------------------- | ---------------------------------------------------------- |
| `PROTOCOL_VERSION`                         | `3`                                                  | `src/gateway/protocol/schema/protocol-schemas.ts`          |
| Timeout de requisição (por RPC)            | `30_000` ms                                          | `src/gateway/client.ts` (`requestTimeoutMs`)               |
| Timeout de pré-autenticação / connect-challenge | `10_000` ms                                     | `src/gateway/handshake-timeouts.ts` (clamp `250`–`10_000`) |
| Backoff inicial de reconexão               | `1_000` ms                                           | `src/gateway/client.ts` (`backoffMs`)                      |
| Backoff máximo de reconexão                | `30_000` ms                                          | `src/gateway/client.ts` (`scheduleReconnect`)              |
| Clamp de nova tentativa rápida após fechamento por token de dispositivo | `250` ms                     | `src/gateway/client.ts`                                    |
| Tolerância de parada forçada antes de `terminate()` | `250` ms                                    | `FORCE_STOP_TERMINATE_GRACE_MS`                            |
| Timeout padrão de `stopAndWait()`          | `1_000` ms                                           | `STOP_AND_WAIT_TIMEOUT_MS`                                 |
| Intervalo padrão de tick (antes de `hello-ok`) | `30_000` ms                                      | `src/gateway/client.ts`                                    |
| Fechamento por timeout de tick             | código `4000` quando o silêncio excede `tickIntervalMs * 2` | `src/gateway/client.ts`                             |
| `MAX_PAYLOAD_BYTES`                        | `25 * 1024 * 1024` (25 MB)                           | `src/gateway/server-constants.ts`                          |

O servidor anuncia os valores efetivos de `policy.tickIntervalMs`, `policy.maxPayload`
e `policy.maxBufferedBytes` em `hello-ok`; os clientes devem respeitar esses valores
em vez dos padrões de pré-handshake.

## Autenticação

- A autenticação do gateway por segredo compartilhado usa `connect.params.auth.token` ou
  `connect.params.auth.password`, dependendo do modo de autenticação configurado.
- Modos que carregam identidade, como Tailscale Serve
  (`gateway.auth.allowTailscale: true`) ou `gateway.auth.mode: "trusted-proxy"` fora de loopback,
  satisfazem a verificação de autenticação de conexão a partir dos cabeçalhos da
  requisição em vez de `connect.params.auth.*`.
- `gateway.auth.mode: "none"` para ingresso privado ignora completamente a autenticação de conexão por segredo compartilhado; não exponha esse modo em ingressos públicos/não confiáveis.
- Após o pareamento, o Gateway emite um **token de dispositivo** com escopo para o papel + escopos da conexão. Ele é retornado em `hello-ok.auth.deviceToken` e deve ser persistido pelo cliente para conexões futuras.
- Os clientes devem persistir o `hello-ok.auth.deviceToken` primário após qualquer
  conexão bem-sucedida.
- Ao reconectar com esse token de dispositivo **armazenado**, também deve ser reutilizado o conjunto de escopos aprovados armazenado para esse token. Isso preserva o acesso de leitura/sondagem/status
  que já foi concedido e evita reduzir silenciosamente as reconexões a um
  escopo implícito mais restrito apenas de admin.
- Montagem da autenticação de conexão no lado do cliente (`selectConnectAuth` em
  `src/gateway/client.ts`):
  - `auth.password` é ortogonal e sempre é encaminhado quando definido.
  - `auth.token` é preenchido em ordem de prioridade: primeiro token compartilhado explícito,
    depois um `deviceToken` explícito, depois um token armazenado por dispositivo (indexado por
    `deviceId` + `role`).
  - `auth.bootstrapToken` é enviado apenas quando nenhuma das opções acima resolve um
    `auth.token`. Um token compartilhado ou qualquer token de dispositivo resolvido o suprime.
  - A promoção automática de um token de dispositivo armazenado na nova tentativa pontual
    `AUTH_TOKEN_MISMATCH` é limitada apenas a **endpoints confiáveis** —
    loopback, ou `wss://` com `tlsFingerprint` fixado. `wss://` público
    sem pinning não se qualifica.
- Entradas adicionais em `hello-ok.auth.deviceTokens` são tokens de transferência de bootstrap.
  Persista-as apenas quando a conexão tiver usado autenticação de bootstrap em um transporte confiável,
  como `wss://` ou loopback/pareamento local.
- Se um cliente fornecer um `deviceToken` **explícito** ou `scopes` explícitos, esse
  conjunto de escopos solicitado pelo chamador permanece autoritativo; escopos em cache só
  são reutilizados quando o cliente estiver reutilizando o token armazenado por dispositivo.
- Tokens de dispositivo podem ser rotacionados/revogados via `device.token.rotate` e
  `device.token.revoke` (exige escopo `operator.pairing`).
- A emissão/rotação de tokens permanece limitada ao conjunto de papéis aprovados registrado
  na entrada de pareamento daquele dispositivo; rotacionar um token não pode expandir o dispositivo para um
  papel que a aprovação de pareamento nunca concedeu.
- Para sessões com token de dispositivo pareado, o gerenciamento de dispositivos tem escopo próprio, a menos que o
  chamador também tenha `operator.admin`: chamadores que não são admin só podem remover/revogar/rotacionar
  sua **própria** entrada de dispositivo.
- `device.token.rotate` também verifica o conjunto de escopos de operator solicitado em relação aos
  escopos da sessão atual do chamador. Chamadores que não são admin não podem rotacionar um token para
  um conjunto de escopos de operator mais amplo do que o que já possuem.
- Falhas de autenticação incluem `error.details.code` mais dicas de recuperação:
  - `error.details.canRetryWithDeviceToken` (boolean)
  - `error.details.recommendedNextStep` (`retry_with_device_token`, `update_auth_configuration`, `update_auth_credentials`, `wait_then_retry`, `review_auth_configuration`)
- Comportamento do cliente para `AUTH_TOKEN_MISMATCH`:
  - Clientes confiáveis podem tentar uma nova tentativa limitada com um token por dispositivo em cache.
  - Se essa nova tentativa falhar, os clientes devem interromper loops automáticos de reconexão e exibir orientações de ação para o operator.

## Identidade do dispositivo + pareamento

- Nós devem incluir uma identidade estável de dispositivo (`device.id`) derivada da
  impressão digital de um par de chaves.
- Gateways emitem tokens por dispositivo + papel.
- Aprovações de pareamento são necessárias para novos IDs de dispositivo, a menos que a aprovação automática local
  esteja habilitada.
- A aprovação automática de pareamento é centrada em conexões diretas locais por loopback.
- O OpenClaw também tem um caminho restrito de autoconexão local de backend/container para
  fluxos helper confiáveis com segredo compartilhado.
- Conexões no mesmo host por tailnet ou LAN ainda são tratadas como remotas para pareamento e
  exigem aprovação.
- Todos os clientes WS devem incluir identidade `device` durante `connect` (operator + node).
  A Control UI só pode omiti-la nestes modos:
  - `gateway.controlUi.allowInsecureAuth=true` para compatibilidade com HTTP inseguro apenas em localhost.
  - autenticação bem-sucedida de operator da Control UI com `gateway.auth.mode: "trusted-proxy"`.
  - `gateway.controlUi.dangerouslyDisableDeviceAuth=true` (break-glass, grave redução de segurança).
- Todas as conexões devem assinar o nonce `connect.challenge` fornecido pelo servidor.

### Diagnósticos de migração de autenticação de dispositivo

Para clientes legados que ainda usam o comportamento de assinatura pré-desafio, `connect` agora retorna
códigos de detalhe `DEVICE_AUTH_*` em `error.details.code` com um `error.details.reason` estável.

Falhas comuns de migração:

| Mensagem                    | details.code                     | details.reason           | Significado                                        |
| --------------------------- | -------------------------------- | ------------------------ | -------------------------------------------------- |
| `device nonce required`     | `DEVICE_AUTH_NONCE_REQUIRED`     | `device-nonce-missing`   | O cliente omitiu `device.nonce` (ou o enviou em branco). |
| `device nonce mismatch`     | `DEVICE_AUTH_NONCE_MISMATCH`     | `device-nonce-mismatch`  | O cliente assinou com um nonce antigo/incorreto.   |
| `device signature invalid`  | `DEVICE_AUTH_SIGNATURE_INVALID`  | `device-signature`       | O payload da assinatura não corresponde ao payload v2. |
| `device signature expired`  | `DEVICE_AUTH_SIGNATURE_EXPIRED`  | `device-signature-stale` | O timestamp assinado está fora da defasagem permitida. |
| `device identity mismatch`  | `DEVICE_AUTH_DEVICE_ID_MISMATCH` | `device-id-mismatch`     | `device.id` não corresponde à impressão digital da chave pública. |
| `device public key invalid` | `DEVICE_AUTH_PUBLIC_KEY_INVALID` | `device-public-key`      | O formato/canonicalização da chave pública falhou. |

Destino da migração:

- Sempre aguarde `connect.challenge`.
- Assine o payload v2 que inclui o nonce do servidor.
- Envie o mesmo nonce em `connect.params.device.nonce`.
- O payload de assinatura preferido é `v3`, que vincula `platform` e `deviceFamily`
  além dos campos device/client/role/scopes/token/nonce.
- Assinaturas legadas `v2` continuam sendo aceitas por compatibilidade, mas o pinning de metadados
  do dispositivo pareado ainda controla a política de comandos na reconexão.

## TLS + pinning

- TLS é compatível com conexões WS.
- Os clientes podem opcionalmente fixar a impressão digital do certificado do gateway (consulte a configuração `gateway.tls`
  além de `gateway.remote.tlsFingerprint` ou a CLI `--tls-fingerprint`).

## Escopo

Este protocolo expõe a **API completa do gateway** (status, canais, modelos, chat,
agente, sessões, nós, aprovações etc.). A superfície exata é definida pelos
esquemas TypeBox em `src/gateway/protocol/schema.ts`.
