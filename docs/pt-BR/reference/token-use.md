---
read_when:
    - Explicando o uso de tokens, custos ou janelas de contexto
    - Depurando o crescimento do contexto ou o comportamento de Compaction
summary: Como o OpenClaw constrói o contexto do prompt e informa o uso de tokens + custos
title: Uso de Tokens e Custos
x-i18n:
    generated_at: "2026-04-15T19:42:06Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9a706d3df8b2ea1136b3535d216c6b358e43aee2a31a4759824385e1345e6fe5
    source_path: reference/token-use.md
    workflow: 15
---

# Uso de tokens e custos

O OpenClaw rastreia **tokens**, não caracteres. Os tokens são específicos de cada modelo, mas a maioria dos modelos no estilo OpenAI tem média de ~4 caracteres por token para texto em inglês.

## Como o prompt do sistema é construído

O OpenClaw monta seu próprio prompt do sistema em cada execução. Ele inclui:

- Lista de ferramentas + descrições curtas
- Lista de Skills (somente metadados; as instruções são carregadas sob demanda com `read`).
  O bloco compacto de Skills é limitado por `skills.limits.maxSkillsPromptChars`,
  com substituição opcional por agente em
  `agents.list[].skillsLimits.maxSkillsPromptChars`.
- Instruções de autoatualização
- Arquivos do workspace + bootstrap (`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md` quando novo, além de `MEMORY.md` quando presente ou `memory.md` como alternativa em minúsculas). Arquivos grandes são truncados por `agents.defaults.bootstrapMaxChars` (padrão: 12000), e a injeção total de bootstrap é limitada por `agents.defaults.bootstrapTotalMaxChars` (padrão: 60000). Arquivos diários `memory/*.md` não fazem parte do prompt de bootstrap normal; eles permanecem sob demanda via ferramentas de memória em turnos comuns, mas `/new` e `/reset` sem argumentos podem prefixar um bloco único de contexto de inicialização com memória diária recente para esse primeiro turno. Esse prelúdio de inicialização é controlado por `agents.defaults.startupContext`.
- Hora (UTC + fuso horário do usuário)
- Tags de resposta + comportamento de Heartbeat
- Metadados de runtime (host/OS/model/thinking)

Veja a análise completa em [Prompt do sistema](/pt-BR/concepts/system-prompt).

## O que conta na janela de contexto

Tudo o que o modelo recebe conta para o limite de contexto:

- Prompt do sistema (todas as seções listadas acima)
- Histórico da conversa (mensagens do usuário + do assistente)
- Chamadas de ferramenta e resultados de ferramenta
- Anexos/transcrições (imagens, áudio, arquivos)
- Resumos de Compaction e artefatos de poda
- Wrappers do provedor ou cabeçalhos de segurança (não visíveis, mas ainda contabilizados)

Algumas superfícies pesadas de runtime têm seus próprios limites explícitos:

- `agents.defaults.contextLimits.memoryGetMaxChars`
- `agents.defaults.contextLimits.memoryGetDefaultLines`
- `agents.defaults.contextLimits.toolResultMaxChars`
- `agents.defaults.contextLimits.postCompactionMaxChars`

As substituições por agente ficam em `agents.list[].contextLimits`. Esses ajustes são
para trechos limitados de runtime e blocos injetados de propriedade do runtime. Eles são
separados dos limites de bootstrap, dos limites de contexto de inicialização e dos
limites do prompt de Skills.

Para imagens, o OpenClaw reduz a escala de cargas de imagem de transcrição/ferramenta antes das chamadas ao provedor.
Use `agents.defaults.imageMaxDimensionPx` (padrão: `1200`) para ajustar isso:

- Valores menores normalmente reduzem o uso de vision tokens e o tamanho da carga.
- Valores maiores preservam mais detalhes visuais para capturas de tela com muito OCR/UI.

Para uma análise prática (por arquivo injetado, ferramentas, Skills e tamanho do prompt do sistema), use `/context list` ou `/context detail`. Veja [Contexto](/pt-BR/concepts/context).

## Como ver o uso atual de tokens

Use estes comandos no chat:

- `/status` → **cartão de status rico em emoji** com o modelo da sessão, uso de contexto,
  tokens de entrada/saída da última resposta e **custo estimado** (somente chave de API).
- `/usage off|tokens|full` → acrescenta um **rodapé de uso por resposta** a cada resposta.
  - Persiste por sessão (armazenado como `responseUsage`).
  - Autenticação OAuth **oculta o custo** (somente tokens).
- `/usage cost` → mostra um resumo local de custos a partir dos logs de sessão do OpenClaw.

Outras superfícies:

- **TUI/Web TUI:** `/status` + `/usage` são compatíveis.
- **CLI:** `openclaw status --usage` e `openclaw channels list` mostram
  janelas de cota normalizadas do provedor (`X% restante`, não custos por resposta).
  Provedores atuais com janela de uso: Anthropic, GitHub Copilot, Gemini CLI,
  OpenAI Codex, MiniMax, Xiaomi e z.ai.

As superfícies de uso normalizam aliases comuns de campos nativos de provedores antes da exibição.
Para tráfego Responses da família OpenAI, isso inclui tanto `input_tokens` /
`output_tokens` quanto `prompt_tokens` / `completion_tokens`, de forma que nomes de campos específicos do transporte
não alterem `/status`, `/usage` ou os resumos da sessão.
O uso JSON do Gemini CLI também é normalizado: o texto da resposta vem de `response`, e
`stats.cached` é mapeado para `cacheRead`, com `stats.input_tokens - stats.cached`
usado quando a CLI omite um campo `stats.input` explícito.
Para tráfego Responses nativo da família OpenAI, aliases de uso de WebSocket/SSE são
normalizados da mesma forma, e os totais recorrem a entrada + saída normalizadas quando
`total_tokens` está ausente ou é `0`.
Quando o snapshot da sessão atual é esparso, `/status` e `session_status` também podem
recuperar contadores de tokens/cache e o rótulo do modelo de runtime ativo do log de uso da transcrição mais recente. Valores ativos diferentes de zero ainda têm precedência sobre valores de fallback da transcrição, e totais de transcrição maiores orientados a prompt
podem prevalecer quando os totais armazenados estão ausentes ou são menores.
A autenticação de uso para janelas de cota do provedor vem de hooks específicos do provedor quando
disponíveis; caso contrário, o OpenClaw recorre à correspondência de credenciais OAuth/chave de API
de perfis de autenticação, env ou config.

## Estimativa de custo (quando exibida)

Os custos são estimados com base na sua configuração de preços do modelo:

```
models.providers.<provider>.models[].cost
```

Esses valores são **USD por 1M de tokens** para `input`, `output`, `cacheRead` e
`cacheWrite`. Se o preço estiver ausente, o OpenClaw mostrará apenas tokens. Tokens OAuth
nunca mostram custo em dólares.

## Impacto do TTL de cache e da poda

O cache de prompt do provedor só se aplica dentro da janela de TTL do cache. O OpenClaw pode
executar opcionalmente **cache-ttl pruning**: ele faz a poda da sessão quando o TTL do cache
expira e então redefine a janela de cache para que solicitações subsequentes possam reutilizar
o contexto recém-cacheado em vez de recachear o histórico completo. Isso mantém os custos de
gravação em cache mais baixos quando uma sessão fica ociosa além do TTL.

Configure isso em [Configuração do Gateway](/pt-BR/gateway/configuration) e veja os
detalhes do comportamento em [Poda de sessão](/pt-BR/concepts/session-pruning).

O Heartbeat pode manter o cache **aquecido** durante períodos de inatividade. Se o TTL de cache
do seu modelo for `1h`, definir o intervalo de Heartbeat um pouco abaixo disso (por exemplo, `55m`) pode evitar
o recacheamento do prompt completo, reduzindo os custos de gravação em cache.

Em configurações com vários agentes, você pode manter uma configuração de modelo compartilhada e ajustar o comportamento do cache
por agente com `agents.list[].params.cacheRetention`.

Para um guia completo parâmetro por parâmetro, veja [Prompt Caching](/pt-BR/reference/prompt-caching).

Para preços da API Anthropic, leituras de cache são significativamente mais baratas que
tokens de entrada, enquanto gravações em cache são cobradas com um multiplicador maior. Veja os preços de prompt caching da Anthropic para as tarifas e multiplicadores de TTL mais recentes:
[https://docs.anthropic.com/docs/build-with-claude/prompt-caching](https://docs.anthropic.com/docs/build-with-claude/prompt-caching)

### Exemplo: manter o cache de 1h aquecido com Heartbeat

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
          cacheRetention: "long" # baseline padrão para a maioria dos agentes
  list:
    - id: "research"
      default: true
      heartbeat:
        every: "55m" # mantém o cache longo aquecido para sessões profundas
    - id: "alerts"
      params:
        cacheRetention: "none" # evita gravações em cache para notificações intermitentes
```

`agents.list[].params` é mesclado sobre os `params` do modelo selecionado, então você pode
substituir apenas `cacheRetention` e herdar os outros padrões do modelo sem alterações.

### Exemplo: ativar o cabeçalho beta de contexto 1M da Anthropic

A janela de contexto de 1M da Anthropic atualmente é controlada por beta. O OpenClaw pode injetar o
valor `anthropic-beta` necessário quando você ativa `context1m` em modelos Opus
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

Isso só se aplica quando `context1m: true` está definido nessa entrada do modelo.

Requisito: a credencial deve ser elegível para uso de contexto longo. Caso contrário,
a Anthropic responde com um erro de limite de taxa do lado do provedor para essa solicitação.

Se você autenticar a Anthropic com tokens OAuth/assinatura (`sk-ant-oat-*`),
o OpenClaw ignora o cabeçalho beta `context-1m-*` porque a Anthropic atualmente
rejeita essa combinação com HTTP 401.

## Dicas para reduzir a pressão de tokens

- Use `/compact` para resumir sessões longas.
- Reduza grandes saídas de ferramentas nos seus fluxos de trabalho.
- Diminua `agents.defaults.imageMaxDimensionPx` para sessões com muitas capturas de tela.
- Mantenha descrições de Skills curtas (a lista de Skills é injetada no prompt).
- Prefira modelos menores para trabalho exploratório e verboso.

Veja [Skills](/pt-BR/tools/skills) para a fórmula exata de sobrecarga da lista de Skills.
