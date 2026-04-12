---
read_when:
    - Explicando o uso de tokens, custos ou janelas de contexto
    - Depurando o crescimento do contexto ou o comportamento de compactação
summary: Como o OpenClaw monta o contexto do prompt e informa o uso de tokens + custos
title: Uso de tokens e custos
x-i18n:
    generated_at: "2026-04-12T05:33:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: f8c856549cd28b8364a640e6fa9ec26aa736895c7a993e96cbe85838e7df2dfb
    source_path: reference/token-use.md
    workflow: 15
---

# Uso de tokens e custos

O OpenClaw rastreia **tokens**, não caracteres. Os tokens são específicos de cada modelo, mas a maioria dos
modelos no estilo OpenAI tem uma média de ~4 caracteres por token em texto em inglês.

## Como o prompt do sistema é montado

O OpenClaw monta seu próprio prompt do sistema em cada execução. Ele inclui:

- Lista de ferramentas + descrições curtas
- Lista de Skills (somente metadados; as instruções são carregadas sob demanda com `read`)
- Instruções de autoatualização
- Arquivos de workspace + bootstrap (`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md` quando novo, além de `MEMORY.md` quando presente ou `memory.md` como fallback em minúsculas). Arquivos grandes são truncados por `agents.defaults.bootstrapMaxChars` (padrão: 20000), e a injeção total de bootstrap é limitada por `agents.defaults.bootstrapTotalMaxChars` (padrão: 150000). Arquivos diários `memory/*.md` não fazem parte do prompt bootstrap normal; eles permanecem sob demanda por meio de ferramentas de memória em turnos comuns, mas `/new` e `/reset` sem nenhum argumento podem prefixar um bloco único de contexto de inicialização com memória diária recente para esse primeiro turno. Esse prelúdio de inicialização é controlado por `agents.defaults.startupContext`.
- Hora (UTC + fuso horário do usuário)
- Tags de resposta + comportamento de heartbeat
- Metadados de runtime (host/OS/model/thinking)

Veja o detalhamento completo em [Prompt do sistema](/pt-BR/concepts/system-prompt).

## O que conta na janela de contexto

Tudo o que o modelo recebe conta para o limite de contexto:

- Prompt do sistema (todas as seções listadas acima)
- Histórico da conversa (mensagens do usuário + assistente)
- Chamadas de ferramentas e resultados de ferramentas
- Anexos/transcrições (imagens, áudio, arquivos)
- Resumos de compactação e artefatos de poda
- Wrappers do provedor ou cabeçalhos de segurança (não visíveis, mas ainda contabilizados)

Para imagens, o OpenClaw reduz a escala das cargas de imagens de transcrição/ferramentas antes das chamadas ao provedor.
Use `agents.defaults.imageMaxDimensionPx` (padrão: `1200`) para ajustar isso:

- Valores menores geralmente reduzem o uso de vision tokens e o tamanho da carga.
- Valores maiores preservam mais detalhes visuais para OCR/capturas de tela com muita interface.

Para uma análise prática (por arquivo injetado, ferramentas, Skills e tamanho do prompt do sistema), use `/context list` ou `/context detail`. Veja [Contexto](/pt-BR/concepts/context).

## Como ver o uso atual de tokens

Use estes comandos no chat:

- `/status` → **cartão de status rico em emojis** com o modelo da sessão, uso de contexto,
  tokens de entrada/saída da última resposta e **custo estimado** (somente chave de API).
- `/usage off|tokens|full` → adiciona um **rodapé de uso por resposta** a cada resposta.
  - Persiste por sessão (armazenado como `responseUsage`).
  - Autenticação OAuth **oculta o custo** (somente tokens).
- `/usage cost` → mostra um resumo local de custos a partir dos logs de sessão do OpenClaw.

Outras superfícies:

- **TUI/Web TUI:** `/status` + `/usage` são compatíveis.
- **CLI:** `openclaw status --usage` e `openclaw channels list` mostram
  janelas de cota normalizadas do provedor (`X% restantes`, não custos por resposta).
  Provedores atuais com janela de uso: Anthropic, GitHub Copilot, Gemini CLI,
  OpenAI Codex, MiniMax, Xiaomi e z.ai.

As superfícies de uso normalizam aliases comuns de campos nativos do provedor antes da exibição.
Para tráfego OpenAI-family Responses, isso inclui tanto `input_tokens` /
`output_tokens` quanto `prompt_tokens` / `completion_tokens`, para que nomes de campos
específicos do transporte não alterem `/status`, `/usage` ou resumos de sessão.
O uso de JSON do Gemini CLI também é normalizado: o texto da resposta vem de `response`, e
`stats.cached` é mapeado para `cacheRead`, com `stats.input_tokens - stats.cached`
usado quando a CLI omite um campo explícito `stats.input`.
Para tráfego nativo OpenAI-family Responses, aliases de uso em WebSocket/SSE são
normalizados da mesma forma, e os totais usam como fallback entrada + saída normalizadas quando
`total_tokens` está ausente ou é `0`.
Quando o snapshot da sessão atual é esparso, `/status` e `session_status` também podem
recuperar contadores de tokens/cache e o rótulo do modelo de runtime ativo do log de uso
da transcrição mais recente. Valores ativos não zero existentes ainda têm precedência sobre
valores de fallback da transcrição, e totais maiores da transcrição orientados a prompt
podem prevalecer quando os totais armazenados estão ausentes ou são menores.
A autenticação de uso para janelas de cota do provedor vem de hooks específicos do provedor quando
disponíveis; caso contrário, o OpenClaw usa como fallback a correspondência de credenciais OAuth/chave de API
de perfis de autenticação, env ou config.

## Estimativa de custo (quando exibida)

Os custos são estimados a partir da configuração de preços do seu modelo:

```
models.providers.<provider>.models[].cost
```

Esses valores são **USD por 1M de tokens** para `input`, `output`, `cacheRead` e
`cacheWrite`. Se o preço estiver ausente, o OpenClaw mostrará apenas os tokens. Tokens OAuth
nunca mostram custo em dólar.

## Impacto de TTL de cache e poda

O cache de prompt do provedor só se aplica dentro da janela de TTL do cache. O OpenClaw pode
executar opcionalmente a **poda por cache-ttl**: ele poda a sessão assim que o TTL do cache
expira e, em seguida, redefine a janela de cache para que solicitações subsequentes possam reutilizar o
contexto recém-cacheado em vez de colocar todo o histórico em cache novamente. Isso mantém os custos
de escrita em cache mais baixos quando uma sessão fica ociosa além do TTL.

Configure isso em [Configuração do Gateway](/pt-BR/gateway/configuration) e veja os
detalhes do comportamento em [Poda de sessão](/pt-BR/concepts/session-pruning).

Heartbeat pode manter o cache **aquecido** durante intervalos de inatividade. Se o TTL do cache
do seu modelo for `1h`, definir o intervalo de heartbeat logo abaixo disso (por exemplo, `55m`) pode evitar
recolocar todo o prompt em cache, reduzindo os custos de escrita em cache.

Em configurações multiagente, você pode manter uma configuração de modelo compartilhada e ajustar o comportamento
de cache por agente com `agents.list[].params.cacheRetention`.

Para um guia completo de cada ajuste, veja [Prompt Caching](/pt-BR/reference/prompt-caching).

Para preços da API Anthropic, leituras de cache são significativamente mais baratas do que
tokens de entrada, enquanto gravações em cache são cobradas com um multiplicador maior. Veja os preços
de prompt caching da Anthropic para as taxas e multiplicadores de TTL mais recentes:
[https://docs.anthropic.com/docs/build-with-claude/prompt-caching](https://docs.anthropic.com/docs/build-with-claude/prompt-caching)

### Exemplo: manter cache de 1h aquecido com heartbeat

```yaml
agents:
  defaults:
    model:
      primary: "anthropic/claude-opus-4-6"
    models:
      "anthropic/claude-opus-4-6":
        params:
          cacheRetention: "long"
    heartbeat:
      every: "55m"
```

### Exemplo: tráfego misto com estratégia de cache por agente

```yaml
agents:
  defaults:
    model:
      primary: "anthropic/claude-opus-4-6"
    models:
      "anthropic/claude-opus-4-6":
        params:
          cacheRetention: "long" # linha de base padrão para a maioria dos agentes
  list:
    - id: "research"
      default: true
      heartbeat:
        every: "55m" # mantém o cache longo aquecido para sessões profundas
    - id: "alerts"
      params:
        cacheRetention: "none" # evita gravações em cache para notificações intermitentes
```

`agents.list[].params` é mesclado sobre `params` do modelo selecionado, então você pode
substituir apenas `cacheRetention` e herdar os outros padrões do modelo sem alterações.

### Exemplo: habilitar o cabeçalho beta de contexto 1M da Anthropic

A janela de contexto de 1M da Anthropic atualmente é controlada por beta. O OpenClaw pode injetar o
valor `anthropic-beta` necessário quando você habilita `context1m` em modelos Opus
ou Sonnet compatíveis.

```yaml
agents:
  defaults:
    models:
      "anthropic/claude-opus-4-6":
        params:
          context1m: true
```

Isso é mapeado para o cabeçalho beta `context-1m-2025-08-07` da Anthropic.

Isso só se aplica quando `context1m: true` está definido nessa entrada de modelo.

Requisito: a credencial deve ser elegível para uso de contexto longo. Caso contrário,
a Anthropic responde com um erro de limite de taxa do lado do provedor para essa solicitação.

Se você autenticar a Anthropic com tokens OAuth/assinatura (`sk-ant-oat-*`),
o OpenClaw ignora o cabeçalho beta `context-1m-*` porque a Anthropic atualmente
rejeita essa combinação com HTTP 401.

## Dicas para reduzir a pressão de tokens

- Use `/compact` para resumir sessões longas.
- Corte saídas grandes de ferramentas nos seus fluxos de trabalho.
- Reduza `agents.defaults.imageMaxDimensionPx` para sessões com muitas capturas de tela.
- Mantenha descrições de Skills curtas (a lista de Skills é injetada no prompt).
- Prefira modelos menores para trabalho exploratório e verboso.

Veja [Skills](/pt-BR/tools/skills) para a fórmula exata de overhead da lista de Skills.
