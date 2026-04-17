---
read_when:
    - Você está alterando o runtime de agente incorporado ou o registro de harnesses
    - Você está registrando um harness de agente a partir de um plugin empacotado ou confiável
    - Você precisa entender como o plugin Codex se relaciona com os provedores de modelo
sidebarTitle: Agent Harness
summary: Superfície experimental do SDK para plugins que substituem o executor de agente incorporado de baixo nível
title: Plugins de Harness de Agente
x-i18n:
    generated_at: "2026-04-12T00:18:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: 62b88fd24ce8b600179db27e16e8d764a2cd7a14e5c5df76374c33121aa5e365
    source_path: plugins/sdk-agent-harness.md
    workflow: 15
---

# Plugins de Harness de Agente

Um **harness de agente** é o executor de baixo nível para um turno preparado de agente do OpenClaw. Não é um provedor de modelo, não é um canal e não é um registro de ferramentas.

Use essa superfície apenas para plugins nativos empacotados ou confiáveis. O contrato ainda é experimental porque os tipos de parâmetro espelham intencionalmente o executor incorporado atual.

## Quando usar um harness

Registre um harness de agente quando uma família de modelos tiver seu próprio runtime nativo de sessão e o transporte normal de provedor do OpenClaw for a abstração errada.

Exemplos:

- um servidor nativo de agente de programação que gerencia threads e compactação
- uma CLI ou daemon local que precisa transmitir eventos nativos de plano/raciocínio/ferramenta
- um runtime de modelo que precisa do próprio id de retomada, além da transcrição de sessão do OpenClaw

**Não** registre um harness apenas para adicionar uma nova API de LLM. Para APIs de modelo normais via HTTP ou WebSocket, crie um [plugin de provedor](/pt-BR/plugins/sdk-provider-plugins).

## O que o core ainda controla

Antes de um harness ser selecionado, o OpenClaw já resolveu:

- provedor e modelo
- estado de autenticação do runtime
- nível de raciocínio e orçamento de contexto
- a transcrição/arquivo de sessão do OpenClaw
- workspace, sandbox e política de ferramentas
- callbacks de resposta do canal e callbacks de streaming
- política de fallback de modelo e troca dinâmica de modelo

Essa separação é intencional. Um harness executa uma tentativa preparada; ele não escolhe provedores, não substitui a entrega do canal e não troca modelos silenciosamente.

## Registrar um harness

**Import:** `openclaw/plugin-sdk/agent-harness`

```typescript
import type { AgentHarness } from "openclaw/plugin-sdk/agent-harness";
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

const myHarness: AgentHarness = {
  id: "my-harness",
  label: "My native agent harness",

  supports(ctx) {
    return ctx.provider === "my-provider"
      ? { supported: true, priority: 100 }
      : { supported: false };
  },

  async runAttempt(params) {
    // Start or resume your native thread.
    // Use params.prompt, params.tools, params.images, params.onPartialReply,
    // params.onAgentEvent, and the other prepared attempt fields.
    return await runMyNativeTurn(params);
  },
};

export default definePluginEntry({
  id: "my-native-agent",
  name: "My Native Agent",
  description: "Runs selected models through a native agent daemon.",
  register(api) {
    api.registerAgentHarness(myHarness);
  },
});
```

## Política de seleção

O OpenClaw escolhe um harness depois da resolução de provedor/modelo:

1. `OPENCLAW_AGENT_RUNTIME=<id>` força um harness registrado com esse id.
2. `OPENCLAW_AGENT_RUNTIME=pi` força o harness PI integrado.
3. `OPENCLAW_AGENT_RUNTIME=auto` pergunta aos harnesses registrados se eles oferecem suporte ao provedor/modelo resolvido.
4. Se nenhum harness registrado corresponder, o OpenClaw usa PI, a menos que o fallback de PI esteja desativado.

Falhas forçadas de harness de plugin aparecem como falhas de execução. No modo `auto`, o OpenClaw pode recorrer a PI quando o harness de plugin selecionado falha antes de um turno produzir efeitos colaterais. Defina `OPENCLAW_AGENT_HARNESS_FALLBACK=none` ou `embeddedHarness.fallback: "none"` para tornar esse fallback uma falha definitiva.

O plugin Codex empacotado registra `codex` como seu id de harness. O core trata isso como um id comum de harness de plugin; aliases específicos do Codex pertencem ao plugin ou à configuração do operador, não ao seletor de runtime compartilhado.

## Pareamento de provedor e harness

A maioria dos harnesses também deve registrar um provedor. O provedor torna referências de modelo, status de autenticação, metadados do modelo e seleção de `/model` visíveis para o restante do OpenClaw. O harness então reivindica esse provedor em `supports(...)`.

O plugin Codex empacotado segue esse padrão:

- id do provedor: `codex`
- referências de modelo do usuário: `codex/gpt-5.4`, `codex/gpt-5.2` ou outro modelo retornado pelo servidor de app do Codex
- id do harness: `codex`
- autenticação: disponibilidade sintética do provedor, porque o harness Codex controla o login/sessão nativo do Codex
- requisição ao servidor de app: o OpenClaw envia o id simples do modelo ao Codex e deixa o harness falar com o protocolo nativo do servidor de app

O plugin Codex é aditivo. Referências simples `openai/gpt-*` continuam sendo referências do provedor OpenAI e seguem usando o caminho normal de provedor do OpenClaw. Selecione `codex/gpt-*` quando quiser autenticação gerenciada pelo Codex, descoberta de modelos do Codex, threads nativas e execução do servidor de app do Codex. `/model` pode alternar entre os modelos do Codex retornados pelo servidor de app do Codex sem exigir credenciais do provedor OpenAI.

Para configuração do operador, exemplos de prefixo de modelo e configurações exclusivas do Codex, consulte [Harness Codex](/pt-BR/plugins/codex-harness).

O OpenClaw exige Codex app-server `0.118.0` ou mais recente. O plugin Codex verifica o handshake de inicialização do app-server e bloqueia servidores mais antigos ou sem versão, para que o OpenClaw execute apenas sobre a superfície de protocolo com a qual foi testado.

### Modo de harness Codex nativo

O harness `codex` empacotado é o modo Codex nativo para turnos de agente incorporado do OpenClaw. Primeiro ative o plugin `codex` empacotado e inclua `codex` em `plugins.allow` se sua configuração usar uma allowlist restritiva. Ele é diferente de `openai-codex/*`:

- `openai-codex/*` usa OAuth do ChatGPT/Codex pelo caminho normal de provedor do OpenClaw.
- `codex/*` usa o provedor Codex empacotado e roteia o turno pelo app-server do Codex.

Quando esse modo é executado, o Codex controla o id nativo da thread, o comportamento de retomada, a compactação e a execução do app-server. O OpenClaw ainda controla o canal de chat, o espelhamento visível da transcrição, a política de ferramentas, aprovações, entrega de mídia e seleção de sessão. Use `embeddedHarness.runtime: "codex"` com `embeddedHarness.fallback: "none"` quando precisar comprovar que o caminho do app-server do Codex está sendo usado e que o fallback para PI não está ocultando um harness nativo com problema.

## Desativar o fallback para PI

Por padrão, o OpenClaw executa agentes incorporados com `agents.defaults.embeddedHarness` definido como `{ runtime: "auto", fallback: "pi" }`. No modo `auto`, harnesses de plugin registrados podem reivindicar um par provedor/modelo. Se nenhum corresponder, ou se um harness de plugin selecionado automaticamente falhar antes de produzir saída, o OpenClaw recorre a PI.

Defina `fallback: "none"` quando precisar comprovar que um harness de plugin é o único runtime em uso. Isso desativa o fallback automático para PI; não bloqueia um `runtime: "pi"` explícito nem `OPENCLAW_AGENT_RUNTIME=pi`.

Para execuções incorporadas somente com Codex:

```json
{
  "agents": {
    "defaults": {
      "model": "codex/gpt-5.4",
      "embeddedHarness": {
        "runtime": "codex",
        "fallback": "none"
      }
    }
  }
}
```

Se você quiser que qualquer harness de plugin registrado reivindique modelos correspondentes, mas nunca quiser que o OpenClaw recorra silenciosamente a PI, mantenha `runtime: "auto"` e desative o fallback:

```json
{
  "agents": {
    "defaults": {
      "embeddedHarness": {
        "runtime": "auto",
        "fallback": "none"
      }
    }
  }
}
```

Substituições por agente usam o mesmo formato:

```json
{
  "agents": {
    "defaults": {
      "embeddedHarness": {
        "runtime": "auto",
        "fallback": "pi"
      }
    },
    "list": [
      {
        "id": "codex-only",
        "model": "codex/gpt-5.4",
        "embeddedHarness": {
          "runtime": "codex",
          "fallback": "none"
        }
      }
    ]
  }
}
```

`OPENCLAW_AGENT_RUNTIME` ainda substitui o runtime configurado. Use `OPENCLAW_AGENT_HARNESS_FALLBACK=none` para desativar o fallback para PI a partir do ambiente.

```bash
OPENCLAW_AGENT_RUNTIME=codex \
OPENCLAW_AGENT_HARNESS_FALLBACK=none \
openclaw gateway run
```

Com o fallback desativado, uma sessão falha cedo quando o harness solicitado não está registrado, não oferece suporte ao provedor/modelo resolvido ou falha antes de produzir efeitos colaterais no turno. Isso é intencional para implantações exclusivas do Codex e para testes live que precisam comprovar que o caminho do app-server do Codex está realmente em uso.

Essa configuração controla apenas o harness de agente incorporado. Ela não desativa o roteamento específico de modelo para imagem, vídeo, música, TTS, PDF ou outros provedores.

## Sessões nativas e espelhamento de transcrição

Um harness pode manter um id de sessão nativa, id de thread ou token de retomada no lado do daemon. Mantenha esse vínculo explicitamente associado à sessão do OpenClaw e continue espelhando a saída visível de assistente/ferramenta na transcrição do OpenClaw.

A transcrição do OpenClaw continua sendo a camada de compatibilidade para:

- histórico de sessão visível no canal
- busca e indexação da transcrição
- voltar para o harness PI integrado em um turno posterior
- comportamento genérico de `/new`, `/reset` e exclusão de sessão

Se o seu harness armazenar um vínculo sidecar, implemente `reset(...)` para que o OpenClaw possa limpá-lo quando a sessão proprietária do OpenClaw for redefinida.

## Resultados de ferramentas e mídia

O core constrói a lista de ferramentas do OpenClaw e a passa para a tentativa preparada. Quando um harness executa uma chamada dinâmica de ferramenta, retorne o resultado da ferramenta pela estrutura de resultado do harness em vez de enviar mídia do canal por conta própria.

Isso mantém saídas de texto, imagem, vídeo, música, TTS, aprovação e ferramentas de mensagens no mesmo caminho de entrega das execuções com suporte de PI.

## Limitações atuais

- O caminho público de importação é genérico, mas alguns aliases de tipo de tentativa/resultado ainda carregam nomes `Pi` por compatibilidade.
- A instalação de harnesses de terceiros é experimental. Prefira plugins de provedor até precisar de um runtime de sessão nativo.
- A troca de harnesses é suportada entre turnos. Não troque de harness no meio de um turno depois que ferramentas nativas, aprovações, texto do assistente ou envios de mensagem já tiverem começado.

## Relacionado

- [Visão geral do SDK](/pt-BR/plugins/sdk-overview)
- [Helpers de Runtime](/pt-BR/plugins/sdk-runtime)
- [Plugins de Provedor](/pt-BR/plugins/sdk-provider-plugins)
- [Harness Codex](/pt-BR/plugins/codex-harness)
- [Provedores de Modelo](/pt-BR/concepts/model-providers)
