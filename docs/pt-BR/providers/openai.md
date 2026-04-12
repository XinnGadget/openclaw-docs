---
read_when:
    - Você quer usar modelos da OpenAI no OpenClaw
    - Você quer usar autenticação por assinatura do Codex em vez de chaves de API
    - Você precisa de um comportamento de execução do agente GPT-5 mais rigoroso
summary: Use o OpenAI por meio de chaves de API ou assinatura do Codex no OpenClaw
title: OpenAI
x-i18n:
    generated_at: "2026-04-12T00:18:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7aa06fba9ac901e663685a6b26443a2f6aeb6ec3589d939522dc87cbb43497b4
    source_path: providers/openai.md
    workflow: 15
---

# OpenAI

A OpenAI fornece APIs para desenvolvedores de modelos GPT. O Codex oferece suporte a **login com ChatGPT** para acesso por assinatura ou login com **chave de API** para acesso baseado em uso. O Codex cloud exige login com ChatGPT.
A OpenAI oferece suporte explícito ao uso de OAuth de assinatura em ferramentas/fluxos de trabalho externos como o OpenClaw.

## Estilo de interação padrão

O OpenClaw pode adicionar uma pequena sobreposição de prompt específica da OpenAI para execuções `openai/*` e
`openai-codex/*`. Por padrão, a sobreposição mantém o assistente caloroso,
colaborativo, conciso, direto e um pouco mais emocionalmente expressivo,
sem substituir o prompt de sistema base do OpenClaw. A sobreposição amigável também
permite o emoji ocasional quando isso se encaixa naturalmente, mantendo a
saída geral concisa.

Chave de configuração:

`plugins.entries.openai.config.personality`

Valores permitidos:

- `"friendly"`: padrão; ativa a sobreposição específica da OpenAI.
- `"on"`: alias para `"friendly"`.
- `"off"`: desativa a sobreposição e usa apenas o prompt base do OpenClaw.

Escopo:

- Aplica-se a modelos `openai/*`.
- Aplica-se a modelos `openai-codex/*`.
- Não afeta outros provedores.

Esse comportamento é ativado por padrão. Mantenha `"friendly"` explicitamente se quiser que
isso sobreviva a futuras mudanças locais de configuração:

```json5
{
  plugins: {
    entries: {
      openai: {
        config: {
          personality: "friendly",
        },
      },
    },
  },
}
```

### Desativar a sobreposição de prompt da OpenAI

Se você quiser o prompt base do OpenClaw sem modificações, defina a sobreposição como `"off"`:

```json5
{
  plugins: {
    entries: {
      openai: {
        config: {
          personality: "off",
        },
      },
    },
  },
}
```

Você também pode defini-la diretamente com a CLI de configuração:

```bash
openclaw config set plugins.entries.openai.config.personality off
```

O OpenClaw normaliza essa configuração sem diferenciar maiúsculas de minúsculas em tempo de execução, então valores como
`"Off"` ainda desativam a sobreposição amigável.

## Opção A: chave de API da OpenAI (OpenAI Platform)

**Ideal para:** acesso direto à API e cobrança baseada em uso.
Obtenha sua chave de API no painel da OpenAI.

Resumo da rota:

- `openai/gpt-5.4` = rota direta da API da OpenAI Platform
- Requer `OPENAI_API_KEY` (ou configuração equivalente do provedor OpenAI)
- No OpenClaw, login com ChatGPT/Codex é roteado por `openai-codex/*`, não por `openai/*`

### Configuração da CLI

```bash
openclaw onboard --auth-choice openai-api-key
# ou não interativo
openclaw onboard --openai-api-key "$OPENAI_API_KEY"
```

### Trecho de configuração

```json5
{
  env: { OPENAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

A documentação atual de modelos de API da OpenAI lista `gpt-5.4` e `gpt-5.4-pro` para uso direto
da API da OpenAI. O OpenClaw encaminha ambos pela rota `openai/*` Responses.
O OpenClaw suprime intencionalmente a linha obsoleta `openai/gpt-5.3-codex-spark`,
porque chamadas diretas à API da OpenAI a rejeitam em tráfego real.

O OpenClaw **não** expõe `openai/gpt-5.3-codex-spark` no caminho direto da API da OpenAI.
O `pi-ai` ainda fornece uma linha embutida para esse modelo, mas solicitações reais da API da OpenAI
atualmente o rejeitam. O Spark é tratado como exclusivo do Codex no OpenClaw.

## Geração de imagem

O plugin `openai` incluído também registra geração de imagem por meio da ferramenta compartilhada
`image_generate`.

- Modelo de imagem padrão: `openai/gpt-image-1`
- Gerar: até 4 imagens por solicitação
- Modo de edição: ativado, até 5 imagens de referência
- Suporta `size`
- Limitação atual específica da OpenAI: o OpenClaw não encaminha substituições de `aspectRatio` nem
  `resolution` para a API de Imagens da OpenAI atualmente

Para usar a OpenAI como provedor de imagem padrão:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "openai/gpt-image-1",
      },
    },
  },
}
```

Consulte [Geração de imagem](/pt-BR/tools/image-generation) para ver os parâmetros
da ferramenta compartilhada, seleção de provedor e comportamento de failover.

## Geração de vídeo

O plugin `openai` incluído também registra geração de vídeo por meio da ferramenta compartilhada
`video_generate`.

- Modelo de vídeo padrão: `openai/sora-2`
- Modos: texto para vídeo, imagem para vídeo e fluxos de referência/edição com vídeo único
- Limites atuais: 1 imagem ou 1 vídeo de referência como entrada
- Limitação atual específica da OpenAI: atualmente, o OpenClaw encaminha apenas substituições de `size`
  para geração de vídeo nativa da OpenAI. Substituições opcionais não compatíveis
  como `aspectRatio`, `resolution`, `audio` e `watermark` são ignoradas
  e retornadas como um aviso da ferramenta.

Para usar a OpenAI como provedor de vídeo padrão:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "openai/sora-2",
      },
    },
  },
}
```

Consulte [Geração de vídeo](/pt-BR/tools/video-generation) para ver os parâmetros
da ferramenta compartilhada, seleção de provedor e comportamento de failover.

## Opção B: assinatura do OpenAI Code (Codex)

**Ideal para:** usar acesso por assinatura do ChatGPT/Codex em vez de uma chave de API.
O Codex cloud exige login com ChatGPT, enquanto a CLI do Codex oferece suporte a login com ChatGPT ou chave de API.

Resumo da rota:

- `openai-codex/gpt-5.4` = rota OAuth do ChatGPT/Codex
- Usa login do ChatGPT/Codex, não uma chave direta da API da OpenAI Platform
- Limites do lado do provedor para `openai-codex/*` podem ser diferentes da experiência no web/app do ChatGPT

### Configuração da CLI (OAuth do Codex)

```bash
# Execute o OAuth do Codex no assistente
openclaw onboard --auth-choice openai-codex

# Ou execute o OAuth diretamente
openclaw models auth login --provider openai-codex
```

### Trecho de configuração (assinatura do Codex)

```json5
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
}
```

A documentação atual do Codex da OpenAI lista `gpt-5.4` como o modelo Codex atual. O OpenClaw
mapeia isso para `openai-codex/gpt-5.4` para uso com OAuth do ChatGPT/Codex.

Essa rota é intencionalmente separada de `openai/gpt-5.4`. Se você quiser o
caminho direto da API da OpenAI Platform, use `openai/*` com uma chave de API. Se quiser
login com ChatGPT/Codex, use `openai-codex/*`.

Se o onboarding reutilizar um login existente da CLI do Codex, essas credenciais continuarão
gerenciadas pela CLI do Codex. Ao expirarem, o OpenClaw relê primeiro a fonte externa do Codex
e, quando o provedor consegue atualizá-las, grava a credencial atualizada
de volta no armazenamento do Codex em vez de assumir sua posse em uma cópia separada
apenas do OpenClaw.

Se sua conta Codex tiver direito ao Codex Spark, o OpenClaw também oferece suporte a:

- `openai-codex/gpt-5.3-codex-spark`

O OpenClaw trata o Codex Spark como exclusivo do Codex. Ele não expõe um caminho direto
`openai/gpt-5.3-codex-spark` com chave de API.

O OpenClaw também preserva `openai-codex/gpt-5.3-codex-spark` quando o `pi-ai`
o descobre. Trate-o como dependente de direito de acesso e experimental: o Codex Spark é
separado de GPT-5.4 `/fast`, e a disponibilidade depende da conta Codex /
ChatGPT conectada.

### Limite da janela de contexto do Codex

O OpenClaw trata os metadados do modelo Codex e o limite de contexto em tempo de execução como
valores separados.

Para `openai-codex/gpt-5.4`:

- `contextWindow` nativo: `1050000`
- limite padrão de `contextTokens` em tempo de execução: `272000`

Isso mantém os metadados do modelo fiéis, ao mesmo tempo que preserva a janela menor
padrão em tempo de execução, que na prática apresenta melhores características de latência e qualidade.

Se você quiser um limite efetivo diferente, defina `models.providers.<provider>.models[].contextTokens`:

```json5
{
  models: {
    providers: {
      "openai-codex": {
        models: [
          {
            id: "gpt-5.4",
            contextTokens: 160000,
          },
        ],
      },
    },
  },
}
```

Use `contextWindow` apenas quando estiver declarando ou substituindo metadados nativos
do modelo. Use `contextTokens` quando quiser limitar o orçamento de contexto em tempo de execução.

### Padrão de transporte

O OpenClaw usa `pi-ai` para streaming do modelo. Tanto para `openai/*` quanto para
`openai-codex/*`, o transporte padrão é `"auto"` (WebSocket primeiro, depois fallback
para SSE).

No modo `"auto"`, o OpenClaw também tenta novamente uma falha inicial de WebSocket que possa ser repetida
antes de fazer fallback para SSE. O modo `"websocket"` forçado ainda expõe erros de transporte diretamente
em vez de escondê-los atrás do fallback.

Após uma falha de conexão ou uma falha de WebSocket no início do turno no modo `"auto"`, o OpenClaw marca
o caminho de WebSocket dessa sessão como degradado por cerca de 60 segundos e envia
os turnos subsequentes por SSE durante o período de resfriamento, em vez de alternar
entre transportes sem parar.

Para endpoints nativos da família OpenAI (`openai/*`, `openai-codex/*` e Azure
OpenAI Responses), o OpenClaw também anexa estado estável de identidade de sessão e turno
às solicitações, para que novas tentativas, reconexões e fallback para SSE permaneçam alinhados à mesma
identidade de conversa. Em rotas nativas da família OpenAI, isso inclui cabeçalhos estáveis de identidade
de solicitação para sessão/turno, além de metadados de transporte correspondentes.

O OpenClaw também normaliza contadores de uso da OpenAI entre variantes de transporte antes
que eles cheguem às superfícies de sessão/status. O tráfego nativo OpenAI/Codex Responses pode
relatar uso como `input_tokens` / `output_tokens` ou
`prompt_tokens` / `completion_tokens`; o OpenClaw trata esses pares como os mesmos contadores
de entrada e saída para `/status`, `/usage` e logs de sessão. Quando o tráfego WebSocket nativo omite `total_tokens`
(ou relata `0`), o OpenClaw usa como fallback o total normalizado de entrada + saída para que as exibições de sessão/status permaneçam preenchidas.

Você pode definir `agents.defaults.models.<provider/model>.params.transport`:

- `"sse"`: força SSE
- `"websocket"`: força WebSocket
- `"auto"`: tenta WebSocket e depois faz fallback para SSE

Para `openai/*` (API Responses), o OpenClaw também ativa o aquecimento de WebSocket por padrão
(`openaiWsWarmup: true`) quando o transporte WebSocket é usado.

Documentação relacionada da OpenAI:

- [Realtime API with WebSocket](https://platform.openai.com/docs/guides/realtime-websocket)
- [Streaming API responses (SSE)](https://platform.openai.com/docs/guides/streaming-responses)

```json5
{
  agents: {
    defaults: {
      model: { primary: "openai-codex/gpt-5.4" },
      models: {
        "openai-codex/gpt-5.4": {
          params: {
            transport: "auto",
          },
        },
      },
    },
  },
}
```

### Aquecimento de WebSocket da OpenAI

A documentação da OpenAI descreve o aquecimento como opcional. O OpenClaw o ativa por padrão para
`openai/*` para reduzir a latência do primeiro turno ao usar transporte WebSocket.

### Desativar o aquecimento

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            openaiWsWarmup: false,
          },
        },
      },
    },
  },
}
```

### Ativar o aquecimento explicitamente

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            openaiWsWarmup: true,
          },
        },
      },
    },
  },
}
```

### Processamento prioritário da OpenAI e do Codex

A API da OpenAI expõe processamento prioritário por meio de `service_tier=priority`. No
OpenClaw, defina `agents.defaults.models["<provider>/<model>"].params.serviceTier`
para encaminhar esse campo em endpoints nativos OpenAI/Codex Responses.

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            serviceTier: "priority",
          },
        },
        "openai-codex/gpt-5.4": {
          params: {
            serviceTier: "priority",
          },
        },
      },
    },
  },
}
```

Os valores compatíveis são `auto`, `default`, `flex` e `priority`.

O OpenClaw encaminha `params.serviceTier` para solicitações Responses diretas de `openai/*`
e solicitações Codex Responses de `openai-codex/*` quando esses modelos apontam
para endpoints nativos OpenAI/Codex.

Comportamento importante:

- `openai/*` direto deve apontar para `api.openai.com`
- `openai-codex/*` deve apontar para `chatgpt.com/backend-api`
- se você rotear qualquer um dos provedores por outra URL base ou proxy, o OpenClaw deixa `service_tier` inalterado

### Modo rápido da OpenAI

O OpenClaw expõe uma alternância compartilhada de modo rápido para sessões `openai/*` e
`openai-codex/*`:

- Chat/UI: `/fast status|on|off`
- Configuração: `agents.defaults.models["<provider>/<model>"].params.fastMode`

Quando o modo rápido está ativado, o OpenClaw o mapeia para processamento prioritário da OpenAI:

- chamadas Responses diretas de `openai/*` para `api.openai.com` enviam `service_tier = "priority"`
- chamadas Responses de `openai-codex/*` para `chatgpt.com/backend-api` também enviam `service_tier = "priority"`
- valores existentes de `service_tier` no payload são preservados
- o modo rápido não reescreve `reasoning` nem `text.verbosity`

Para GPT 5.4 especificamente, a configuração mais comum é:

- enviar `/fast on` em uma sessão usando `openai/gpt-5.4` ou `openai-codex/gpt-5.4`
- ou definir `agents.defaults.models["openai/gpt-5.4"].params.fastMode = true`
- se você também usa OAuth do Codex, defina `agents.defaults.models["openai-codex/gpt-5.4"].params.fastMode = true` também

Exemplo:

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            fastMode: true,
          },
        },
        "openai-codex/gpt-5.4": {
          params: {
            fastMode: true,
          },
        },
      },
    },
  },
}
```

As substituições da sessão têm prioridade sobre a configuração. Limpar a substituição da sessão na UI de Sessões
faz a sessão voltar ao padrão configurado.

### Rotas OpenAI nativas versus OpenAI-compatíveis

O OpenClaw trata endpoints diretos da OpenAI, Codex e Azure OpenAI de forma diferente
de proxies genéricos OpenAI-compatíveis com `/v1`:

- rotas nativas `openai/*`, `openai-codex/*` e Azure OpenAI mantêm
  `reasoning: { effort: "none" }` intacto quando você desativa explicitamente o raciocínio
- rotas nativas da família OpenAI usam esquemas de ferramenta em modo estrito por padrão
- cabeçalhos ocultos de atribuição do OpenClaw (`originator`, `version` e
  `User-Agent`) só são anexados em hosts nativos OpenAI verificados
  (`api.openai.com`) e hosts nativos Codex (`chatgpt.com/backend-api`)
- rotas nativas OpenAI/Codex mantêm formatação de solicitação exclusiva da OpenAI, como
  `service_tier`, `store` do Responses, payloads de compatibilidade de raciocínio da OpenAI e
  dicas de cache de prompt
- rotas OpenAI-compatíveis no estilo proxy mantêm o comportamento de compatibilidade mais flexível e não
  forçam esquemas de ferramenta estritos, formatação de solicitação exclusiva de rotas nativas nem
  cabeçalhos ocultos de atribuição OpenAI/Codex

O Azure OpenAI permanece no grupo de rotas nativas para comportamento de transporte e compatibilidade,
mas não recebe os cabeçalhos ocultos de atribuição OpenAI/Codex.

Isso preserva o comportamento atual do OpenAI Responses nativo sem forçar shims
OpenAI-compatíveis mais antigos em backends `/v1` de terceiros.

### Modo GPT agêntico estrito

Para execuções da família GPT-5 de `openai/*` e `openai-codex/*`, o OpenClaw pode usar um
contrato de execução Pi incorporado mais rigoroso:

```json5
{
  agents: {
    defaults: {
      embeddedPi: {
        executionContract: "strict-agentic",
      },
    },
  },
}
```

Com `strict-agentic`, o OpenClaw deixa de tratar um turno do assistente apenas com plano como
progresso bem-sucedido quando uma ação concreta com ferramenta está disponível. Ele tenta novamente o
turno com uma orientação para agir agora, ativa automaticamente a ferramenta estruturada `update_plan` para
trabalho substancial e exibe um estado explícito de bloqueio se o modelo continuar
planejando sem agir.

O modo é limitado a execuções da família GPT-5 da OpenAI e OpenAI Codex. Outros provedores
e famílias de modelos mais antigas mantêm o comportamento padrão do Pi incorporado, a menos que você as inclua
explicitamente em outras configurações de runtime.

### Compactação no lado do servidor do OpenAI Responses

Para modelos diretos OpenAI Responses (`openai/*` usando `api: "openai-responses"` com
`baseUrl` em `api.openai.com`), o OpenClaw agora ativa automaticamente dicas de payload
de compactação no lado do servidor da OpenAI:

- Força `store: true` (a menos que a compatibilidade do modelo defina `supportsStore: false`)
- Injeta `context_management: [{ type: "compaction", compact_threshold: ... }]`

Por padrão, `compact_threshold` é `70%` de `contextWindow` do modelo (ou `80000`
quando indisponível).

### Ativar explicitamente a compactação no lado do servidor

Use isso quando quiser forçar a injeção de `context_management` em modelos Responses compatíveis
(por exemplo Azure OpenAI Responses):

```json5
{
  agents: {
    defaults: {
      models: {
        "azure-openai-responses/gpt-5.4": {
          params: {
            responsesServerCompaction: true,
          },
        },
      },
    },
  },
}
```

### Ativar com um limite personalizado

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            responsesServerCompaction: true,
            responsesCompactThreshold: 120000,
          },
        },
      },
    },
  },
}
```

### Desativar a compactação no lado do servidor

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            responsesServerCompaction: false,
          },
        },
      },
    },
  },
}
```

`responsesServerCompaction` controla apenas a injeção de `context_management`.
Modelos diretos OpenAI Responses ainda forçam `store: true`, a menos que a compatibilidade defina
`supportsStore: false`.

## Observações

- As referências de modelo sempre usam `provider/model` (consulte [/concepts/models](/pt-BR/concepts/models)).
- Os detalhes de autenticação + regras de reutilização estão em [/concepts/oauth](/pt-BR/concepts/oauth).
