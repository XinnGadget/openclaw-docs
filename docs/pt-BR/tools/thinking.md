---
read_when:
    - Ajuste da análise, do modo rápido ou da análise detalhada na interpretação de diretivas ou nos padrões definidos
summary: Sintaxe de diretivas para /think, /fast, /verbose, /trace e visibilidade do raciocínio
title: Níveis de reflexão
x-i18n:
    generated_at: "2026-04-17T05:36:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1cb44a7bf75546e5a8c3204e12f3297221449b881161d173dea4983da3921649
    source_path: tools/thinking.md
    workflow: 15
---

# Níveis de reflexão (diretivas /think)

## O que faz

- Diretiva inline em qualquer corpo de mensagem recebido: `/t <level>`, `/think:<level>` ou `/thinking <level>`.
- Níveis (aliases): `off | minimal | low | medium | high | xhigh | adaptive`
  - minimal → “pensar”
  - low → “pensar bastante”
  - medium → “pensar ainda mais”
  - high → “ultrathink” (orçamento máximo)
  - xhigh → “ultrathink+” (esforço GPT-5.2 + modelos Codex e Anthropic Claude Opus 4.7)
  - adaptive → reflexão adaptativa gerenciada pelo provedor (compatível com Anthropic Claude 4.6 e Opus 4.7)
  - `x-high`, `x_high`, `extra-high`, `extra high` e `extra_high` são mapeados para `xhigh`.
  - `highest`, `max` são mapeados para `high`.
- Observações por provedor:
  - Modelos Anthropic Claude 4.6 usam `adaptive` por padrão quando nenhum nível de reflexão explícito é definido.
  - Anthropic Claude Opus 4.7 não usa reflexão adaptativa por padrão. O padrão de esforço da API continua sendo definido pelo provedor, a menos que você defina explicitamente um nível de reflexão.
  - Anthropic Claude Opus 4.7 mapeia `/think xhigh` para reflexão adaptativa mais `output_config.effort: "xhigh"`, porque `/think` é uma diretiva de reflexão e `xhigh` é a configuração de esforço do Opus 4.7.
  - MiniMax (`minimax/*`) no caminho de streaming compatível com Anthropic usa `thinking: { type: "disabled" }` por padrão, a menos que você defina explicitamente a reflexão em parâmetros do modelo ou da requisição. Isso evita vazamento de deltas `reasoning_content` do formato de stream Anthropic não nativo do MiniMax.
  - Z.AI (`zai/*`) oferece suporte apenas a reflexão binária (`on`/`off`). Qualquer nível diferente de `off` é tratado como `on` (mapeado para `low`).
  - Moonshot (`moonshot/*`) mapeia `/think off` para `thinking: { type: "disabled" }` e qualquer nível diferente de `off` para `thinking: { type: "enabled" }`. Quando a reflexão está habilitada, o Moonshot aceita apenas `tool_choice` `auto|none`; o OpenClaw normaliza valores incompatíveis para `auto`.

## Ordem de resolução

1. Diretiva inline na mensagem (aplica-se apenas àquela mensagem).
2. Substituição da sessão (definida ao enviar uma mensagem contendo apenas a diretiva).
3. Padrão por agente (`agents.list[].thinkingDefault` na configuração).
4. Padrão global (`agents.defaults.thinkingDefault` na configuração).
5. Fallback: `adaptive` para modelos Anthropic Claude 4.6, `off` para Anthropic Claude Opus 4.7, a menos que explicitamente configurado, `low` para outros modelos com capacidade de raciocínio e `off` caso contrário.

## Definindo um padrão de sessão

- Envie uma mensagem que seja **apenas** a diretiva (espaços em branco são permitidos), por exemplo `/think:medium` ou `/t high`.
- Isso permanece na sessão atual (por remetente, por padrão); é limpo por `/think:off` ou pela redefinição por inatividade da sessão.
- Uma resposta de confirmação é enviada (`Thinking level set to high.` / `Thinking disabled.`). Se o nível for inválido (por exemplo `/thinking big`), o comando é rejeitado com uma dica e o estado da sessão permanece inalterado.
- Envie `/think` (ou `/think:`) sem argumento para ver o nível de reflexão atual.

## Aplicação por agente

- **Pi incorporado**: o nível resolvido é passado para o runtime do agente Pi em processo.

## Modo rápido (/fast)

- Níveis: `on|off`.
- Uma mensagem contendo apenas a diretiva alterna uma substituição do modo rápido na sessão e responde com `Fast mode enabled.` / `Fast mode disabled.`.
- Envie `/fast` (ou `/fast status`) sem modo para ver o estado efetivo atual do modo rápido.
- O OpenClaw resolve o modo rápido nesta ordem:
  1. `/fast on|off` inline/somente diretiva
  2. Substituição da sessão
  3. Padrão por agente (`agents.list[].fastModeDefault`)
  4. Configuração por modelo: `agents.defaults.models["<provider>/<model>"].params.fastMode`
  5. Fallback: `off`
- Para `openai/*`, o modo rápido é mapeado para processamento prioritário da OpenAI, enviando `service_tier=priority` em requisições Responses compatíveis.
- Para `openai-codex/*`, o modo rápido envia a mesma flag `service_tier=priority` em Codex Responses. O OpenClaw mantém um único alternador `/fast` compartilhado entre ambos os caminhos de autenticação.
- Para requisições diretas públicas `anthropic/*`, incluindo tráfego autenticado via OAuth enviado para `api.anthropic.com`, o modo rápido é mapeado para níveis de serviço da Anthropic: `/fast on` define `service_tier=auto`, `/fast off` define `service_tier=standard_only`.
- Para `minimax/*` no caminho compatível com Anthropic, `/fast on` (ou `params.fastMode: true`) reescreve `MiniMax-M2.7` para `MiniMax-M2.7-highspeed`.
- Parâmetros explícitos de modelo Anthropic `serviceTier` / `service_tier` substituem o padrão do modo rápido quando ambos são definidos. O OpenClaw ainda ignora a injeção de nível de serviço da Anthropic para URLs base de proxy que não sejam Anthropic.

## Diretivas detalhadas (/verbose ou /v)

- Níveis: `on` (mínimo) | `full` | `off` (padrão).
- Uma mensagem contendo apenas a diretiva alterna o modo detalhado da sessão e responde com `Verbose logging enabled.` / `Verbose logging disabled.`; níveis inválidos retornam uma dica sem alterar o estado.
- `/verbose off` armazena uma substituição explícita da sessão; limpe-a pela interface de Sessões escolhendo `inherit`.
- A diretiva inline afeta apenas aquela mensagem; os padrões de sessão/globais se aplicam caso contrário.
- Envie `/verbose` (ou `/verbose:`) sem argumento para ver o nível detalhado atual.
- Quando o modo detalhado está ativado, agentes que emitem resultados estruturados de ferramentas (Pi, outros agentes JSON) enviam cada chamada de ferramenta de volta como sua própria mensagem somente de metadados, com o prefixo `<emoji> <tool-name>: <arg>` quando disponível (caminho/comando). Esses resumos de ferramenta são enviados assim que cada ferramenta começa (em bolhas separadas), não como deltas de streaming.
- Resumos de falha de ferramenta permanecem visíveis no modo normal, mas sufixos brutos com detalhes de erro ficam ocultos, a menos que o modo detalhado esteja em `on` ou `full`.
- Quando o modo detalhado está em `full`, as saídas das ferramentas também são encaminhadas após a conclusão (em bolha separada, truncadas para um tamanho seguro). Se você alternar `/verbose on|full|off` enquanto uma execução estiver em andamento, as bolhas de ferramenta subsequentes respeitarão a nova configuração.

## Diretivas de rastreamento de Plugin (/trace)

- Níveis: `on` | `off` (padrão).
- Uma mensagem contendo apenas a diretiva alterna a saída de rastreamento de Plugin da sessão e responde com `Plugin trace enabled.` / `Plugin trace disabled.`.
- A diretiva inline afeta apenas aquela mensagem; os padrões de sessão/globais se aplicam caso contrário.
- Envie `/trace` (ou `/trace:`) sem argumento para ver o nível de rastreamento atual.
- `/trace` é mais restrito que `/verbose`: ele expõe apenas linhas de rastreamento/depuração pertencentes ao Plugin, como resumos de depuração do Active Memory.
- Linhas de rastreamento podem aparecer em `/status` e como uma mensagem de diagnóstico de acompanhamento após a resposta normal do assistente.

## Visibilidade do raciocínio (/reasoning)

- Níveis: `on|off|stream`.
- Uma mensagem contendo apenas a diretiva alterna se blocos de reflexão são exibidos nas respostas.
- Quando habilitado, o raciocínio é enviado como uma **mensagem separada** com o prefixo `Reasoning:`.
- `stream` (somente Telegram): transmite o raciocínio na bolha de rascunho do Telegram enquanto a resposta é gerada e, em seguida, envia a resposta final sem o raciocínio.
- Alias: `/reason`.
- Envie `/reasoning` (ou `/reasoning:`) sem argumento para ver o nível atual de raciocínio.
- Ordem de resolução: diretiva inline, depois substituição da sessão, depois padrão por agente (`agents.list[].reasoningDefault`) e, por fim, fallback (`off`).

## Relacionado

- A documentação do modo elevado está em [Modo elevado](/pt-BR/tools/elevated).

## Heartbeats

- O corpo da sondagem de Heartbeat é o prompt de heartbeat configurado (padrão: `Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`). Diretivas inline em uma mensagem de heartbeat se aplicam normalmente (mas evite alterar padrões de sessão a partir de heartbeats).
- A entrega de Heartbeat usa apenas a carga final por padrão. Para também enviar a mensagem separada `Reasoning:` (quando disponível), defina `agents.defaults.heartbeat.includeReasoning: true` ou `agents.list[].heartbeat.includeReasoning: true` por agente.

## Interface web de chat

- O seletor de reflexão do chat na web espelha o nível armazenado da sessão a partir do armazenamento/configuração de sessão de entrada quando a página é carregada.
- Escolher outro nível grava imediatamente a substituição da sessão via `sessions.patch`; não espera o próximo envio e não é uma substituição `thinkingOnce` de uso único.
- A primeira opção é sempre `Default (<resolved level>)`, em que o padrão resolvido vem do modelo ativo da sessão: `adaptive` para Claude 4.6 na Anthropic, `off` para Anthropic Claude Opus 4.7, a menos que configurado, `low` para outros modelos com capacidade de raciocínio e `off` caso contrário.
- O seletor permanece ciente do provedor:
  - a maioria dos provedores mostra `off | minimal | low | medium | high | adaptive`
  - Anthropic Claude Opus 4.7 mostra `off | minimal | low | medium | high | xhigh | adaptive`
  - Z.AI mostra `off | on` binário
- `/think:<level>` continua funcionando e atualiza o mesmo nível armazenado da sessão, para que as diretivas do chat e o seletor permaneçam sincronizados.
