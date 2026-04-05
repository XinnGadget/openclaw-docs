---
read_when:
    - Executando ou configurando o onboarding da CLI
    - Configurando uma nova máquina
sidebarTitle: 'Onboarding: CLI'
summary: 'Onboarding da CLI: configuração guiada para gateway, workspace, canais e Skills'
title: Onboarding (CLI)
x-i18n:
    generated_at: "2026-04-05T10:48:27Z"
    model: gpt-5.4
    provider: openai
    source_hash: 81e33fb4f8be30e7c2c6e0024bf9bdcf48583ca58eaf5fff5afd37a1cd628523
    source_path: start/wizard.md
    workflow: 15
---

# Onboarding (CLI)

O onboarding da CLI é a forma **recomendada** de configurar o OpenClaw no macOS,
Linux ou Windows (via WSL2; fortemente recomendado).
Ele configura um Gateway local ou uma conexão com Gateway remoto, além de canais, Skills
e padrões de workspace em um único fluxo guiado.

```bash
openclaw onboard
```

<Info>
Primeiro chat mais rápido: abra a UI de controle (não é necessário configurar canais). Execute
`openclaw dashboard` e converse no navegador. Documentação: [Painel](/web/dashboard).
</Info>

Para reconfigurar depois:

```bash
openclaw configure
openclaw agents add <name>
```

<Note>
`--json` não implica modo não interativo. Para scripts, use `--non-interactive`.
</Note>

<Tip>
O onboarding da CLI inclui uma etapa de pesquisa na web em que você pode escolher um provedor
como Brave, DuckDuckGo, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search,
Ollama Web Search, Perplexity, SearXNG ou Tavily. Alguns provedores exigem uma
chave de API, enquanto outros não exigem chave. Você também pode configurar isso depois com
`openclaw configure --section web`. Documentação: [Ferramentas web](/tools/web).
</Tip>

## QuickStart vs Avançado

O onboarding começa com **QuickStart** (padrões) vs **Avançado** (controle total).

<Tabs>
  <Tab title="QuickStart (padrões)">
    - Gateway local (loopback)
    - Workspace padrão (ou workspace existente)
    - Porta do Gateway **18789**
    - Autenticação do Gateway **Token** (gerado automaticamente, mesmo em loopback)
    - Política de ferramentas padrão para novas configurações locais: `tools.profile: "coding"` (um perfil explícito existente é preservado)
    - Padrão de isolamento de DM: o onboarding local grava `session.dmScope: "per-channel-peer"` quando não definido. Detalhes: [Referência de configuração da CLI](/start/wizard-cli-reference#outputs-and-internals)
    - Exposição via Tailscale **Desativada**
    - Telegram + DMs do WhatsApp usam **lista de permissão** por padrão (será solicitado o seu número de telefone)
  </Tab>
  <Tab title="Avançado (controle total)">
    - Expõe todas as etapas (modo, workspace, gateway, canais, daemon, Skills).
  </Tab>
</Tabs>

## O que o onboarding configura

**Modo local (padrão)** orienta você por estas etapas:

1. **Modelo/Autenticação** — escolha qualquer fluxo compatível de provedor/autenticação (chave de API, OAuth ou autenticação manual específica do provedor), incluindo Provedor personalizado
   (compatível com OpenAI, compatível com Anthropic ou detecção automática desconhecida). Escolha um modelo padrão.
   Observação de segurança: se este agente vai executar ferramentas ou processar conteúdo de webhook/hooks, prefira o modelo de última geração mais forte disponível e mantenha a política de ferramentas rígida. Camadas mais fracas/antigas são mais fáceis de sofrer prompt injection.
   Para execuções não interativas, `--secret-input-mode ref` armazena referências baseadas em env em perfis de autenticação em vez de valores de chave de API em texto simples.
   No modo `ref` não interativo, a variável de ambiente do provedor deve estar definida; passar flags de chave inline sem essa variável de ambiente falha imediatamente.
   Em execuções interativas, escolher o modo de referência secreta permite apontar para uma variável de ambiente ou para uma referência configurada de provedor (`file` ou `exec`), com uma validação rápida prévia antes de salvar.
   Para Anthropic, o onboarding/configure interativo oferece **Anthropic Claude CLI** como fallback local e **chave de API da Anthropic** como caminho de produção recomendado. O setup-token da Anthropic também está disponível novamente como um caminho legado/manual específico do OpenClaw, com a expectativa de cobrança **Extra Usage** específica do OpenClaw da Anthropic.
2. **Workspace** — Local para arquivos do agente (padrão `~/.openclaw/workspace`). Inicializa arquivos de bootstrap.
3. **Gateway** — Porta, endereço de bind, modo de autenticação, exposição via Tailscale.
   No modo interativo com token, escolha o armazenamento padrão em texto simples do token ou opte por SecretRef.
   Caminho SecretRef de token não interativo: `--gateway-token-ref-env <ENV_VAR>`.
4. **Canais** — canais de chat integrados e incluídos, como BlueBubbles, Discord, Feishu, Google Chat, Mattermost, Microsoft Teams, QQ Bot, Signal, Slack, Telegram, WhatsApp e mais.
5. **Daemon** — Instala um LaunchAgent (macOS), unidade de usuário systemd (Linux/WSL2) ou Scheduled Task nativa do Windows com fallback por usuário na pasta Inicialização.
   Se a autenticação por token exigir um token e `gateway.auth.token` for gerenciado por SecretRef, a instalação do daemon o valida, mas não persiste o token resolvido nos metadados de ambiente do serviço supervisor.
   Se a autenticação por token exigir um token e o SecretRef de token configurado não for resolvido, a instalação do daemon é bloqueada com orientações práticas.
   Se tanto `gateway.auth.token` quanto `gateway.auth.password` estiverem configurados e `gateway.auth.mode` não estiver definido, a instalação do daemon será bloqueada até que o modo seja definido explicitamente.
6. **Verificação de integridade** — Inicia o Gateway e verifica se ele está em execução.
7. **Skills** — Instala Skills recomendadas e dependências opcionais.

<Note>
Executar o onboarding novamente **não** apaga nada, a menos que você escolha explicitamente **Reset** (ou passe `--reset`).
O `--reset` da CLI usa por padrão configuração, credenciais e sessões; use `--reset-scope full` para incluir o workspace.
Se a configuração for inválida ou contiver chaves legadas, o onboarding pedirá que você execute `openclaw doctor` primeiro.
</Note>

O **modo remoto** configura apenas o cliente local para se conectar a um Gateway em outro lugar.
Ele **não** instala nem altera nada no host remoto.

## Adicionar outro agente

Use `openclaw agents add <name>` para criar um agente separado com seu próprio workspace,
sessões e perfis de autenticação. Executar sem `--workspace` inicia o onboarding.

O que ele define:

- `agents.list[].name`
- `agents.list[].workspace`
- `agents.list[].agentDir`

Observações:

- Os workspaces padrão seguem `~/.openclaw/workspace-<agentId>`.
- Adicione `bindings` para rotear mensagens de entrada (o onboarding pode fazer isso).
- Flags não interativas: `--model`, `--agent-dir`, `--bind`, `--non-interactive`.

## Referência completa

Para detalhamentos passo a passo e saídas de configuração, consulte
[Referência de configuração da CLI](/start/wizard-cli-reference).
Para exemplos não interativos, consulte [Automação da CLI](/start/wizard-cli-automation).
Para a referência técnica mais profunda, incluindo detalhes de RPC, consulte
[Referência do onboarding](/reference/wizard).

## Documentação relacionada

- Referência de comando da CLI: [`openclaw onboard`](/cli/onboard)
- Visão geral do onboarding: [Visão geral do onboarding](/start/onboarding-overview)
- Onboarding do app macOS: [Onboarding](/start/onboarding)
- Ritual da primeira execução do agente: [Bootstrap do agente](/start/bootstrapping)
