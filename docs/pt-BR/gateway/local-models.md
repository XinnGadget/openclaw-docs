---
read_when:
    - Você quer servir modelos da sua própria máquina com GPU
    - Você está configurando o LM Studio ou um proxy compatível com OpenAI
    - Você precisa das orientações mais seguras para modelos locais
summary: Execute o OpenClaw em LLMs locais (LM Studio, vLLM, LiteLLM, endpoints OpenAI personalizados)
title: Modelos locais
x-i18n:
    generated_at: "2026-04-15T05:33:49Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8778cc1c623a356ff3cf306c494c046887f9417a70ec71e659e4a8aae912a780
    source_path: gateway/local-models.md
    workflow: 15
---

# Modelos locais

Localmente é viável, mas o OpenClaw espera um contexto grande + defesas fortes contra injeção de prompt. Placas pequenas truncam o contexto e comprometem a segurança. Mire alto: **≥2 Mac Studios no máximo ou equipamento GPU equivalente (~US$ 30 mil+)**. Uma única GPU de **24 GB** funciona apenas para prompts mais leves, com latência maior. Use a **maior variante / variante de tamanho completo do modelo que você conseguir executar**; checkpoints agressivamente quantizados ou “small” aumentam o risco de injeção de prompt (veja [Segurança](/pt-BR/gateway/security)).

Se você quiser a configuração local com menos atrito, comece com [LM Studio](/pt-BR/providers/lmstudio) ou [Ollama](/pt-BR/providers/ollama) e `openclaw onboard`. Esta página é o guia opinativo para stacks locais mais robustas e servidores locais personalizados compatíveis com OpenAI.

## Recomendado: LM Studio + modelo local grande (API Responses)

Melhor stack local atual. Carregue um modelo grande no LM Studio (por exemplo, uma build completa de Qwen, DeepSeek ou Llama), ative o servidor local (padrão `http://127.0.0.1:1234`) e use a API Responses para manter o raciocínio separado do texto final.

```json5
{
  agents: {
    defaults: {
      model: { primary: “lmstudio/my-local-model” },
      models: {
        “anthropic/claude-opus-4-6”: { alias: “Opus” },
        “lmstudio/my-local-model”: { alias: “Local” },
      },
    },
  },
  models: {
    mode: “merge”,
    providers: {
      lmstudio: {
        baseUrl: “http://127.0.0.1:1234/v1”,
        apiKey: “lmstudio”,
        api: “openai-responses”,
        models: [
          {
            id: “my-local-model”,
            name: “Local Model”,
            reasoning: false,
            input: [“text”],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 196608,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

**Checklist de configuração**

- Instale o LM Studio: [https://lmstudio.ai](https://lmstudio.ai)
- No LM Studio, baixe a **maior build de modelo disponível** (evite variantes “small”/muito quantizadas), inicie o servidor e confirme que `http://127.0.0.1:1234/v1/models` o lista.
- Substitua `my-local-model` pelo ID real do modelo exibido no LM Studio.
- Mantenha o modelo carregado; o carregamento a frio adiciona latência na inicialização.
- Ajuste `contextWindow`/`maxTokens` se a sua build do LM Studio for diferente.
- Para WhatsApp, use a API Responses para que apenas o texto final seja enviado.

Mantenha também os modelos hospedados configurados mesmo ao executar localmente; use `models.mode: "merge"` para que fallbacks continuem disponíveis.

### Configuração híbrida: primário hospedado, fallback local

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-6",
        fallbacks: ["lmstudio/my-local-model", "anthropic/claude-opus-4-6"],
      },
      models: {
        "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
        "lmstudio/my-local-model": { alias: "Local" },
        "anthropic/claude-opus-4-6": { alias: "Opus" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      lmstudio: {
        baseUrl: "http://127.0.0.1:1234/v1",
        apiKey: "lmstudio",
        api: "openai-responses",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 196608,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

### Local primeiro com rede de segurança hospedada

Troque a ordem de primário e fallback; mantenha o mesmo bloco `providers` e `models.mode: "merge"` para poder recorrer a Sonnet ou Opus quando a máquina local estiver indisponível.

### Hospedagem regional / roteamento de dados

- Variantes hospedadas de MiniMax/Kimi/GLM também existem no OpenRouter com endpoints fixados por região (por exemplo, hospedados nos EUA). Escolha ali a variante regional para manter o tráfego dentro da jurisdição desejada, enquanto ainda usa `models.mode: "merge"` para fallbacks de Anthropic/OpenAI.
- Somente local continua sendo o caminho mais forte para privacidade; o roteamento regional hospedado é o meio-termo quando você precisa de recursos do provedor, mas quer controle sobre o fluxo de dados.

## Outros proxies locais compatíveis com OpenAI

vLLM, LiteLLM, OAI-proxy ou gateways personalizados funcionam se expuserem um endpoint `/v1` no estilo OpenAI. Substitua o bloco do provedor acima pelo seu endpoint e ID de modelo:

```json5
{
  models: {
    mode: "merge",
    providers: {
      local: {
        baseUrl: "http://127.0.0.1:8000/v1",
        apiKey: "sk-local",
        api: "openai-responses",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 120000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

Mantenha `models.mode: "merge"` para que os modelos hospedados continuem disponíveis como fallbacks.

Observação de comportamento para backends locais/proxy com `/v1`:

- O OpenClaw trata esses backends como rotas no estilo proxy compatíveis com OpenAI, não como endpoints OpenAI nativos
- a formatação de requisição exclusiva do OpenAI nativo não se aplica aqui: sem `service_tier`, sem `store` de Responses, sem formatação de payload de compatibilidade de raciocínio do OpenAI e sem dicas de cache de prompt
- cabeçalhos ocultos de atribuição do OpenClaw (`originator`, `version`, `User-Agent`) não são injetados nessas URLs de proxy personalizadas

Observações de compatibilidade para backends compatíveis com OpenAI mais restritivos:

- Alguns servidores aceitam apenas `messages[].content` como string em Chat Completions, e não arrays estruturados de partes de conteúdo. Defina `models.providers.<provider>.models[].compat.requiresStringContent: true` para esses endpoints.
- Alguns backends locais menores ou mais restritivos são instáveis com o formato completo de prompt do runtime do agente do OpenClaw, especialmente quando esquemas de ferramentas são incluídos. Se o backend funciona para chamadas diretas pequenas a `/v1/chat/completions`, mas falha em turnos normais do agente do OpenClaw, primeiro tente `agents.defaults.localModelMode: "lean"` para remover ferramentas padrão pesadas como `browser`, `cron` e `message`; se isso ainda falhar, tente `models.providers.<provider>.models[].compat.supportsTools: false`.
- Se o backend ainda falhar apenas em execuções maiores do OpenClaw, o problema restante normalmente é capacidade do modelo/servidor upstream ou um bug do backend, não da camada de transporte do OpenClaw.

## Solução de problemas

- O Gateway consegue alcançar o proxy? `curl http://127.0.0.1:1234/v1/models`.
- Modelo do LM Studio descarregado? Carregue novamente; inicialização a frio é uma causa comum de “travamento”.
- O OpenClaw avisa quando a janela de contexto detectada fica abaixo de **32k** e bloqueia abaixo de **16k**. Se você encontrar essa verificação prévia, aumente o limite de contexto do servidor/modelo ou escolha um modelo maior.
- Erros de contexto? Reduza `contextWindow` ou aumente o limite do seu servidor.
- O servidor compatível com OpenAI retorna `messages[].content ... expected a string`?
  Adicione `compat.requiresStringContent: true` nessa entrada de modelo.
- Chamadas diretas pequenas para `/v1/chat/completions` funcionam, mas `openclaw infer model run`
  falha com Gemma ou outro modelo local? Desative primeiro os esquemas de ferramentas com
  `compat.supportsTools: false`, depois teste novamente. Se o servidor ainda travar apenas
  com prompts maiores do OpenClaw, trate isso como uma limitação do servidor/modelo upstream.
- Segurança: modelos locais ignoram filtros do lado do provedor; mantenha os agentes limitados e a Compaction ativada para limitar o raio de impacto da injeção de prompt.
