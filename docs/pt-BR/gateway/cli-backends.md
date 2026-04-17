---
read_when:
    - Você quer um fallback confiável quando os provedores de API falham
    - Você está executando o Codex CLI ou outras CLIs de IA locais e quer reutilizá-las
    - Você quer entender a ponte MCP de loopback para acesso a ferramentas do backend de CLI
summary: 'Backends de CLI: fallback de CLI de IA local com ponte de ferramenta MCP opcional'
title: Backends de CLI
x-i18n:
    generated_at: "2026-04-16T19:31:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: 381273532a8622bc4628000a6fb999712b12af08faade2b5f2b7ac4cc7d23efe
    source_path: gateway/cli-backends.md
    workflow: 15
---

# Backends de CLI (runtime de fallback)

O OpenClaw pode executar **CLIs de IA locais** como um **fallback somente de texto** quando provedores de API estão fora do ar,
limitados por taxa ou temporariamente se comportando mal. Isso é intencionalmente conservador:

- **As ferramentas do OpenClaw não são injetadas diretamente**, mas backends com `bundleMcp: true`
  podem receber ferramentas do gateway por meio de uma ponte MCP de loopback.
- **Streaming JSONL** para CLIs que oferecem suporte.
- **Sessões são suportadas** (para que turnos de acompanhamento permaneçam coerentes).
- **Imagens podem ser repassadas** se a CLI aceitar caminhos de imagem.

Isso foi projetado como uma **rede de segurança** em vez de um caminho principal. Use quando você
quiser respostas de texto que “sempre funcionam” sem depender de APIs externas.

Se você quiser um runtime de harness completo com controles de sessão ACP, tarefas em segundo plano,
vinculação de thread/conversa e sessões externas persistentes de programação, use
[Agentes ACP](/pt-BR/tools/acp-agents). Backends de CLI não são ACP.

## Início rápido amigável para iniciantes

Você pode usar o Codex CLI **sem nenhuma configuração** (o Plugin OpenAI incluído
registra um backend padrão):

```bash
openclaw agent --message "hi" --model codex-cli/gpt-5.4
```

Se o seu gateway estiver em execução sob launchd/systemd e o PATH for mínimo, adicione apenas o
caminho do comando:

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "codex-cli": {
          command: "/opt/homebrew/bin/codex",
        },
      },
    },
  },
}
```

É isso. Nenhuma chave, nenhuma configuração extra de autenticação necessária além da própria CLI.

Se você usar um backend de CLI incluído como **provedor principal de mensagens** em um
host de gateway, o OpenClaw agora carrega automaticamente o Plugin incluído proprietário quando sua configuração
faz referência explicitamente a esse backend em uma referência de modelo ou em
`agents.defaults.cliBackends`.

## Usando como fallback

Adicione um backend de CLI à sua lista de fallback para que ele só seja executado quando os modelos principais falharem:

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["codex-cli/gpt-5.4"],
      },
      models: {
        "anthropic/claude-opus-4-6": { alias: "Opus" },
        "codex-cli/gpt-5.4": {},
      },
    },
  },
}
```

Observações:

- Se você usar `agents.defaults.models` (lista de permissões), também deverá incluir ali os modelos do seu backend de CLI.
- Se o provedor principal falhar (autenticação, limites de taxa, timeouts), o OpenClaw
  tentará o backend de CLI em seguida.

## Visão geral da configuração

Todos os backends de CLI ficam em:

```
agents.defaults.cliBackends
```

Cada entrada é indexada por um **id de provedor** (por exemplo, `codex-cli`, `my-cli`).
O id do provedor se torna o lado esquerdo da sua referência de modelo:

```
<provider>/<model>
```

### Exemplo de configuração

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "codex-cli": {
          command: "/opt/homebrew/bin/codex",
        },
        "my-cli": {
          command: "my-cli",
          args: ["--json"],
          output: "json",
          input: "arg",
          modelArg: "--model",
          modelAliases: {
            "claude-opus-4-6": "opus",
            "claude-sonnet-4-6": "sonnet",
          },
          sessionArg: "--session",
          sessionMode: "existing",
          sessionIdFields: ["session_id", "conversation_id"],
          systemPromptArg: "--system",
          // CLIs no estilo Codex podem apontar para um arquivo de prompt em vez disso:
          // systemPromptFileConfigArg: "-c",
          // systemPromptFileConfigKey: "model_instructions_file",
          systemPromptWhen: "first",
          imageArg: "--image",
          imageMode: "repeat",
          serialize: true,
        },
      },
    },
  },
}
```

## Como funciona

1. **Seleciona um backend** com base no prefixo do provedor (`codex-cli/...`).
2. **Monta um prompt de sistema** usando o mesmo prompt + contexto de workspace do OpenClaw.
3. **Executa a CLI** com um id de sessão (se suportado) para que o histórico permaneça consistente.
4. **Analisa a saída** (JSON ou texto simples) e retorna o texto final.
5. **Persiste ids de sessão** por backend, para que acompanhamentos reutilizem a mesma sessão de CLI.

<Note>
O backend `claude-cli` incluído da Anthropic voltou a ser suportado. A equipe da Anthropic
nos informou que o uso do Claude CLI no estilo OpenClaw voltou a ser permitido, então o OpenClaw trata o uso de
`claude -p` como autorizado para esta integração, a menos que a Anthropic publique
uma nova política.
</Note>

O backend `codex-cli` incluído da OpenAI passa o prompt de sistema do OpenClaw por meio
da substituição de configuração `model_instructions_file` do Codex (`-c
model_instructions_file="..."`). O Codex não expõe uma flag no estilo Claude
`--append-system-prompt`, então o OpenClaw grava o prompt montado em um
arquivo temporário para cada nova sessão do Codex CLI.

O backend `claude-cli` incluído da Anthropic recebe o snapshot de Skills do OpenClaw
de duas formas: o catálogo compacto de Skills do OpenClaw no prompt de sistema anexado e
um Plugin temporário do Claude Code passado com `--plugin-dir`. O Plugin contém
apenas as Skills elegíveis para aquele agente/sessão, para que o resolvedor nativo de Skills do Claude Code veja o mesmo conjunto filtrado que o OpenClaw anunciaria no prompt de outra forma. Substituições de env/chave de API de Skill ainda são aplicadas pelo OpenClaw ao ambiente do processo filho para a execução.

## Sessões

- Se a CLI oferecer suporte a sessões, defina `sessionArg` (por exemplo, `--session-id`) ou
  `sessionArgs` (placeholder `{sessionId}`) quando o ID precisar ser inserido
  em várias flags.
- Se a CLI usar um **subcomando de retomada** com flags diferentes, defina
  `resumeArgs` (substitui `args` ao retomar) e opcionalmente `resumeOutput`
  (para retomadas não JSON).
- `sessionMode`:
  - `always`: sempre envia um id de sessão (novo UUID se nenhum estiver armazenado).
  - `existing`: só envia um id de sessão se um já tiver sido armazenado antes.
  - `none`: nunca envia um id de sessão.

Observações sobre serialização:

- `serialize: true` mantém as execuções da mesma faixa em ordem.
- A maioria das CLIs serializa em uma faixa de provedor.
- O OpenClaw descarta a reutilização de sessão de CLI armazenada quando o estado de autenticação do backend muda, incluindo novo login, rotação de token ou alteração de credencial de perfil de autenticação.

## Imagens (pass-through)

Se a sua CLI aceitar caminhos de imagem, defina `imageArg`:

```json5
imageArg: "--image",
imageMode: "repeat"
```

O OpenClaw gravará imagens base64 em arquivos temporários. Se `imageArg` estiver definido, esses
caminhos serão passados como argumentos da CLI. Se `imageArg` estiver ausente, o OpenClaw anexa os
caminhos dos arquivos ao prompt (injeção de caminho), o que é suficiente para CLIs que carregam
automaticamente arquivos locais a partir de caminhos simples.

## Entradas / saídas

- `output: "json"` (padrão) tenta analisar JSON e extrair texto + id de sessão.
- Para saída JSON do Gemini CLI, o OpenClaw lê o texto da resposta em `response` e
  o uso em `stats` quando `usage` está ausente ou vazio.
- `output: "jsonl"` analisa streams JSONL (por exemplo, Codex CLI `--json`) e extrai a mensagem final do agente, além de identificadores de sessão quando presentes.
- `output: "text"` trata stdout como a resposta final.

Modos de entrada:

- `input: "arg"` (padrão) passa o prompt como o último argumento da CLI.
- `input: "stdin"` envia o prompt via stdin.
- Se o prompt for muito longo e `maxPromptArgChars` estiver definido, stdin será usado.

## Padrões (propriedade do Plugin)

O Plugin OpenAI incluído também registra um padrão para `codex-cli`:

- `command: "codex"`
- `args: ["exec","--json","--color","never","--sandbox","workspace-write","--skip-git-repo-check"]`
- `resumeArgs: ["exec","resume","{sessionId}","-c","sandbox_mode=\"workspace-write\"","--skip-git-repo-check"]`
- `output: "jsonl"`
- `resumeOutput: "text"`
- `modelArg: "--model"`
- `imageArg: "--image"`
- `sessionMode: "existing"`

O Plugin Google incluído também registra um padrão para `google-gemini-cli`:

- `command: "gemini"`
- `args: ["--output-format", "json", "--prompt", "{prompt}"]`
- `resumeArgs: ["--resume", "{sessionId}", "--output-format", "json", "--prompt", "{prompt}"]`
- `imageArg: "@"`
- `imagePathScope: "workspace"`
- `modelArg: "--model"`
- `sessionMode: "existing"`
- `sessionIdFields: ["session_id", "sessionId"]`

Pré-requisito: o Gemini CLI local deve estar instalado e disponível como
`gemini` no `PATH` (`brew install gemini-cli` ou
`npm install -g @google/gemini-cli`).

Observações sobre JSON do Gemini CLI:

- O texto da resposta é lido do campo JSON `response`.
- O uso recorre a `stats` quando `usage` está ausente ou vazio.
- `stats.cached` é normalizado em `cacheRead` do OpenClaw.
- Se `stats.input` estiver ausente, o OpenClaw deriva os tokens de entrada de
  `stats.input_tokens - stats.cached`.

Substitua apenas se necessário (comum: caminho absoluto de `command`).

## Padrões de propriedade do Plugin

Os padrões de backend de CLI agora fazem parte da superfície do Plugin:

- Plugins os registram com `api.registerCliBackend(...)`.
- O `id` do backend se torna o prefixo do provedor em referências de modelo.
- A configuração do usuário em `agents.defaults.cliBackends.<id>` ainda substitui o padrão do Plugin.
- A limpeza de configuração específica do backend continua sendo propriedade do Plugin por meio do hook opcional
  `normalizeConfig`.

Plugins que precisarem de pequenos shims de compatibilidade de prompt/mensagem podem declarar
transformações de texto bidirecionais sem substituir um provedor ou backend de CLI:

```typescript
api.registerTextTransforms({
  input: [
    { from: /red basket/g, to: "blue basket" },
    { from: /paper ticket/g, to: "digital ticket" },
    { from: /left shelf/g, to: "right shelf" },
  ],
  output: [
    { from: /blue basket/g, to: "red basket" },
    { from: /digital ticket/g, to: "paper ticket" },
    { from: /right shelf/g, to: "left shelf" },
  ],
});
```

`input` reescreve o prompt de sistema e o prompt do usuário passados para a CLI. `output`
reescreve deltas transmitidos do assistente e o texto final analisado antes que o OpenClaw processe
seus próprios marcadores de controle e a entrega ao canal.

Para CLIs que emitem JSONL compatível com stream-json do Claude Code, defina
`jsonlDialect: "claude-stream-json"` na configuração desse backend.

## Overlays MCP incluídos

Backends de CLI **não** recebem chamadas de ferramenta do OpenClaw diretamente, mas um backend pode
optar por um overlay de configuração MCP gerado com `bundleMcp: true`.

Comportamento incluído atualmente:

- `claude-cli`: arquivo de configuração MCP estrito gerado
- `codex-cli`: substituições de configuração inline para `mcp_servers`
- `google-gemini-cli`: arquivo de configurações de sistema Gemini gerado

Quando o bundle MCP está habilitado, o OpenClaw:

- inicia um servidor HTTP MCP de loopback que expõe ferramentas do gateway ao processo da CLI
- autentica a ponte com um token por sessão (`OPENCLAW_MCP_TOKEN`)
- limita o acesso às ferramentas ao contexto atual de sessão, conta e canal
- carrega servidores bundle-MCP habilitados para o workspace atual
- os mescla com qualquer forma existente de configuração/ajustes MCP do backend
- reescreve a configuração de inicialização usando o modo de integração de propriedade do backend da extensão proprietária

Se nenhum servidor MCP estiver habilitado, o OpenClaw ainda injeta uma configuração estrita quando um
backend opta por bundle MCP para que execuções em segundo plano permaneçam isoladas.

## Limitações

- **Sem chamadas diretas de ferramenta do OpenClaw.** O OpenClaw não injeta chamadas de ferramenta no
  protocolo do backend de CLI. Backends só veem ferramentas do gateway quando optam por
  `bundleMcp: true`.
- **O streaming é específico do backend.** Alguns backends transmitem JSONL; outros acumulam
  até a saída.
- **Saídas estruturadas** dependem do formato JSON da CLI.
- **Sessões do Codex CLI** retomam via saída de texto (sem JSONL), o que é menos
  estruturado do que a execução inicial com `--json`. As sessões do OpenClaw ainda funcionam
  normalmente.

## Solução de problemas

- **CLI não encontrada**: defina `command` com um caminho completo.
- **Nome de modelo incorreto**: use `modelAliases` para mapear `provider/model` → modelo da CLI.
- **Sem continuidade de sessão**: verifique se `sessionArg` está definido e se `sessionMode` não é
  `none` (o Codex CLI atualmente não pode retomar com saída JSON).
- **Imagens ignoradas**: defina `imageArg` (e verifique se a CLI oferece suporte a caminhos de arquivo).
