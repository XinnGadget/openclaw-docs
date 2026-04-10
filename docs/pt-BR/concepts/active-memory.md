---
read_when:
    - Você quer entender para que serve a memória ativa
    - Você quer ativar a memória ativa para um agente conversacional
    - Você quer ajustar o comportamento da memória ativa sem ativá-la em todos os lugares
summary: Um subagente de memória de bloqueio, pertencente ao plugin, que injeta memória relevante em sessões de chat interativas
title: Memória ativa
x-i18n:
    generated_at: "2026-04-10T05:34:14Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6a51437df4ae4d9d57764601dfcfcdadb269e2895bf49dc82b9f496c1b3cb341
    source_path: concepts/active-memory.md
    workflow: 15
---

# Memória ativa

A memória ativa é um subagente opcional de memória de bloqueio, pertencente ao plugin, que é executado
antes da resposta principal em sessões conversacionais qualificadas.

Ela existe porque a maioria dos sistemas de memória é capaz, mas reativa. Eles dependem
do agente principal para decidir quando pesquisar na memória, ou do usuário para dizer coisas
como "lembre-se disso" ou "pesquise na memória". Nessa altura, o momento em que a memória teria
feito a resposta parecer natural já passou.

A memória ativa dá ao sistema uma chance limitada de trazer memória relevante
antes de a resposta principal ser gerada.

## Cole isto no seu agente

Cole isto no seu agente se você quiser habilitar a Memória ativa com uma
configuração autocontida e segura por padrão:

```json5
{
  plugins: {
    entries: {
      "active-memory": {
        enabled: true,
        config: {
          enabled: true,
          agents: ["main"],
          allowedChatTypes: ["direct"],
          modelFallbackPolicy: "default-remote",
          queryMode: "recent",
          promptStyle: "balanced",
          timeoutMs: 15000,
          maxSummaryChars: 220,
          persistTranscripts: false,
          logging: true,
        },
      },
    },
  },
}
```

Isso ativa o plugin para o agente `main`, o mantém limitado por padrão a
sessões no estilo de mensagens diretas, permite que ele herde primeiro o modelo da
sessão atual e ainda permite o fallback remoto integrado caso nenhum modelo explícito
ou herdado esteja disponível.

Depois disso, reinicie o gateway:

```bash
node scripts/run-node.mjs gateway --profile dev
```

Para inspecioná-lo ao vivo em uma conversa:

```text
/verbose on
```

## Ativar a memória ativa

A configuração mais segura é:

1. habilitar o plugin
2. direcioná-lo para um agente conversacional
3. manter o logging ativado apenas durante o ajuste fino

Comece com isto em `openclaw.json`:

```json5
{
  plugins: {
    entries: {
      "active-memory": {
        enabled: true,
        config: {
          agents: ["main"],
          allowedChatTypes: ["direct"],
          modelFallbackPolicy: "default-remote",
          queryMode: "recent",
          promptStyle: "balanced",
          timeoutMs: 15000,
          maxSummaryChars: 220,
          persistTranscripts: false,
          logging: true,
        },
      },
    },
  },
}
```

Depois reinicie o gateway:

```bash
node scripts/run-node.mjs gateway --profile dev
```

O que isso significa:

- `plugins.entries.active-memory.enabled: true` ativa o plugin
- `config.agents: ["main"]` habilita a memória ativa apenas para o agente `main`
- `config.allowedChatTypes: ["direct"]` mantém a memória ativa habilitada por padrão apenas para sessões no estilo de mensagens diretas
- se `config.model` não estiver definido, a memória ativa herda primeiro o modelo da sessão atual
- `config.modelFallbackPolicy: "default-remote"` mantém o fallback remoto integrado como padrão quando nenhum modelo explícito ou herdado está disponível
- `config.promptStyle: "balanced"` usa o estilo de prompt padrão de uso geral para o modo `recent`
- a memória ativa ainda é executada apenas em sessões de chat persistentes interativas qualificadas

## Como vê-la

A memória ativa injeta contexto oculto de sistema para o modelo. Ela não expõe
tags brutas `<active_memory_plugin>...</active_memory_plugin>` ao cliente.

## Alternância por sessão

Use o comando do plugin quando quiser pausar ou retomar a memória ativa na
sessão de chat atual sem editar a configuração:

```text
/active-memory status
/active-memory off
/active-memory on
```

Isso é aplicado no escopo da sessão. Não altera
`plugins.entries.active-memory.enabled`, o direcionamento por agente nem outras
configurações globais.

Se você quiser que o comando grave a configuração e pause ou retome a memória ativa para
todas as sessões, use a forma global explícita:

```text
/active-memory status --global
/active-memory off --global
/active-memory on --global
```

A forma global grava `plugins.entries.active-memory.config.enabled`. Ela deixa
`plugins.entries.active-memory.enabled` ativado para que o comando continue disponível
para reativar a memória ativa depois.

Se você quiser ver o que a memória ativa está fazendo em uma sessão ao vivo, ative o
modo detalhado para essa sessão:

```text
/verbose on
```

Com o modo detalhado ativado, o OpenClaw pode mostrar:

- uma linha de status da memória ativa como `Active Memory: ok 842ms recent 34 chars`
- um resumo de depuração legível como `Active Memory Debug: Lemon pepper wings with blue cheese.`

Essas linhas são derivadas da mesma passagem de memória ativa que alimenta o contexto
oculto do sistema, mas são formatadas para humanos em vez de expor marcação bruta
de prompt.

Por padrão, a transcrição do subagente de memória de bloqueio é temporária e excluída
após a conclusão da execução.

Fluxo de exemplo:

```text
/verbose on
what wings should i order?
```

Formato de resposta visível esperado:

```text
...normal assistant reply...

🧩 Active Memory: ok 842ms recent 34 chars
🔎 Active Memory Debug: Lemon pepper wings with blue cheese.
```

## Quando ela é executada

A memória ativa usa dois critérios:

1. **Opt-in de configuração**
   O plugin deve estar habilitado, e o id do agente atual deve aparecer em
   `plugins.entries.active-memory.config.agents`.
2. **Qualificação estrita em tempo de execução**
   Mesmo quando habilitada e direcionada, a memória ativa só é executada em
   sessões de chat persistentes interativas qualificadas.

A regra real é:

```text
plugin enabled
+
agent id targeted
+
allowed chat type
+
eligible interactive persistent chat session
=
active memory runs
```

Se qualquer um deles falhar, a memória ativa não será executada.

## Tipos de sessão

`config.allowedChatTypes` controla quais tipos de conversas podem executar a Memória
ativa de qualquer forma.

O padrão é:

```json5
allowedChatTypes: ["direct"]
```

Isso significa que a Memória ativa é executada por padrão em sessões no estilo de
mensagens diretas, mas não em sessões de grupo ou canal, a menos que você as habilite
explicitamente.

Exemplos:

```json5
allowedChatTypes: ["direct"]
```

```json5
allowedChatTypes: ["direct", "group"]
```

```json5
allowedChatTypes: ["direct", "group", "channel"]
```

## Onde ela é executada

A memória ativa é um recurso de enriquecimento conversacional, não um recurso de
inferência para toda a plataforma.

| Superfície                                                          | Executa memória ativa?                                  |
| ------------------------------------------------------------------- | ------------------------------------------------------- |
| Sessões persistentes da UI de controle / chat web                   | Sim, se o plugin estiver habilitado e o agente for direcionado |
| Outras sessões de canal interativas no mesmo caminho de chat persistente | Sim, se o plugin estiver habilitado e o agente for direcionado |
| Execuções avulsas sem interface                                     | Não                                                     |
| Execuções de heartbeat/background                                   | Não                                                     |
| Caminhos internos genéricos de `agent-command`                      | Não                                                     |
| Execução interna de subagente/helper                                | Não                                                     |

## Por que usá-la

Use a memória ativa quando:

- a sessão for persistente e voltada ao usuário
- o agente tiver memória de longo prazo significativa para pesquisar
- continuidade e personalização importarem mais do que o determinismo bruto do prompt

Ela funciona especialmente bem para:

- preferências estáveis
- hábitos recorrentes
- contexto de longo prazo do usuário que deve surgir naturalmente

Ela é pouco adequada para:

- automação
- workers internos
- tarefas de API de execução única
- lugares em que a personalização oculta seria surpreendente

## Como ela funciona

O formato em tempo de execução é:

```mermaid
flowchart LR
  U["User Message"] --> Q["Build Memory Query"]
  Q --> R["Active Memory Blocking Memory Sub-Agent"]
  R -->|NONE or empty| M["Main Reply"]
  R -->|relevant summary| I["Append Hidden active_memory_plugin System Context"]
  I --> M["Main Reply"]
```

O subagente de memória de bloqueio pode usar apenas:

- `memory_search`
- `memory_get`

Se a conexão estiver fraca, ele deve retornar `NONE`.

## Modos de consulta

`config.queryMode` controla quanto da conversa o subagente de memória de bloqueio vê.

## Estilos de prompt

`config.promptStyle` controla quão disposto ou rigoroso o subagente de memória de bloqueio é
ao decidir se deve retornar memória.

Estilos disponíveis:

- `balanced`: padrão de uso geral para o modo `recent`
- `strict`: menos disposto; melhor quando você quer muito pouca interferência do contexto próximo
- `contextual`: mais favorável à continuidade; melhor quando o histórico da conversa deve importar mais
- `recall-heavy`: mais disposto a trazer memória em correspondências mais sutis, mas ainda plausíveis
- `precision-heavy`: prefere agressivamente `NONE`, a menos que a correspondência seja óbvia
- `preference-only`: otimizado para favoritos, hábitos, rotinas, gostos e fatos pessoais recorrentes

Mapeamento padrão quando `config.promptStyle` não está definido:

```text
message -> strict
recent -> balanced
full -> contextual
```

Se você definir `config.promptStyle` explicitamente, essa substituição prevalece.

Exemplo:

```json5
promptStyle: "preference-only"
```

## Política de fallback de modelo

Se `config.model` não estiver definido, a Memória ativa tenta resolver um modelo nesta ordem:

```text
explicit plugin model
-> current session model
-> agent primary model
-> optional built-in remote fallback
```

`config.modelFallbackPolicy` controla a última etapa.

Padrão:

```json5
modelFallbackPolicy: "default-remote"
```

Outra opção:

```json5
modelFallbackPolicy: "resolved-only"
```

Use `resolved-only` se quiser que a Memória ativa ignore a recuperação em vez de usar
o padrão remoto integrado como fallback quando nenhum modelo explícito ou herdado
estiver disponível.

## Escapes avançados

Essas opções intencionalmente não fazem parte da configuração recomendada.

`config.thinking` pode substituir o nível de raciocínio do subagente de memória de bloqueio:

```json5
thinking: "medium"
```

Padrão:

```json5
thinking: "off"
```

Não habilite isso por padrão. A Memória ativa é executada no caminho da resposta, então tempo
extra de raciocínio aumenta diretamente a latência percebida pelo usuário.

`config.promptAppend` adiciona instruções extras do operador após o prompt padrão da
Memória ativa e antes do contexto da conversa:

```json5
promptAppend: "Prefer stable long-term preferences over one-off events."
```

`config.promptOverride` substitui o prompt padrão da Memória ativa. O OpenClaw
ainda anexa o contexto da conversa em seguida:

```json5
promptOverride: "You are a memory search agent. Return NONE or one compact user fact."
```

A personalização do prompt não é recomendada, a menos que você esteja testando
deliberadamente um contrato de recuperação diferente. O prompt padrão é ajustado para
retornar `NONE` ou um contexto compacto de fatos do usuário para o modelo principal.

### `message`

Apenas a mensagem mais recente do usuário é enviada.

```text
Latest user message only
```

Use isso quando:

- você quiser o comportamento mais rápido
- você quiser o viés mais forte em direção à recuperação de preferências estáveis
- turnos de acompanhamento não precisarem de contexto conversacional

Tempo limite recomendado:

- comece em torno de `3000` a `5000` ms

### `recent`

A mensagem mais recente do usuário, mais uma pequena cauda recente da conversa, são enviadas.

```text
Recent conversation tail:
user: ...
assistant: ...
user: ...

Latest user message:
...
```

Use isso quando:

- você quiser um melhor equilíbrio entre velocidade e contextualização conversacional
- perguntas de acompanhamento frequentemente dependerem dos últimos turnos

Tempo limite recomendado:

- comece em torno de `15000` ms

### `full`

A conversa completa é enviada ao subagente de memória de bloqueio.

```text
Full conversation context:
user: ...
assistant: ...
user: ...
...
```

Use isso quando:

- a melhor qualidade de recuperação for mais importante do que a latência
- a conversa contiver preparação importante muito antes na thread

Tempo limite recomendado:

- aumente-o substancialmente em comparação com `message` ou `recent`
- comece em torno de `15000` ms ou mais, dependendo do tamanho da thread

Em geral, o tempo limite deve aumentar com o tamanho do contexto:

```text
message < recent < full
```

## Persistência de transcrições

As execuções do subagente de memória de bloqueio da memória ativa criam uma transcrição real
`session.jsonl` durante a chamada do subagente de memória de bloqueio.

Por padrão, essa transcrição é temporária:

- ela é gravada em um diretório temporário
- ela é usada apenas para a execução do subagente de memória de bloqueio
- ela é excluída imediatamente após o término da execução

Se você quiser manter essas transcrições do subagente de memória de bloqueio em disco para depuração ou
inspeção, ative a persistência explicitamente:

```json5
{
  plugins: {
    entries: {
      "active-memory": {
        enabled: true,
        config: {
          agents: ["main"],
          persistTranscripts: true,
          transcriptDir: "active-memory",
        },
      },
    },
  },
}
```

Quando habilitada, a memória ativa armazena transcrições em um diretório separado dentro da
pasta de sessões do agente de destino, e não no caminho principal da transcrição da conversa
do usuário.

O layout padrão é conceitualmente:

```text
agents/<agent>/sessions/active-memory/<blocking-memory-sub-agent-session-id>.jsonl
```

Você pode alterar o subdiretório relativo com `config.transcriptDir`.

Use isso com cuidado:

- as transcrições do subagente de memória de bloqueio podem se acumular rapidamente em sessões movimentadas
- o modo de consulta `full` pode duplicar muito contexto de conversa
- essas transcrições contêm contexto oculto de prompt e memórias recuperadas

## Configuração

Toda a configuração da memória ativa fica em:

```text
plugins.entries.active-memory
```

Os campos mais importantes são:

| Chave                       | Tipo                                                                                                 | Significado                                                                                             |
| --------------------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `enabled`                   | `boolean`                                                                                            | Habilita o próprio plugin                                                                               |
| `config.agents`             | `string[]`                                                                                           | IDs de agente que podem usar memória ativa                                                              |
| `config.model`              | `string`                                                                                             | Referência opcional de modelo do subagente de memória de bloqueio; quando não definido, a memória ativa usa o modelo atual da sessão |
| `config.queryMode`          | `"message" \| "recent" \| "full"`                                                                    | Controla quanto da conversa o subagente de memória de bloqueio vê                                       |
| `config.promptStyle`        | `"balanced" \| "strict" \| "contextual" \| "recall-heavy" \| "precision-heavy" \| "preference-only"` | Controla quão disposto ou rigoroso o subagente de memória de bloqueio é ao decidir se deve retornar memória |
| `config.thinking`           | `"off" \| "minimal" \| "low" \| "medium" \| "high" \| "xhigh" \| "adaptive"`                         | Substituição avançada do nível de raciocínio para o subagente de memória de bloqueio; padrão `off` para velocidade |
| `config.promptOverride`     | `string`                                                                                             | Substituição avançada completa do prompt; não recomendada para uso normal                               |
| `config.promptAppend`       | `string`                                                                                             | Instruções extras avançadas anexadas ao prompt padrão ou substituído                                    |
| `config.timeoutMs`          | `number`                                                                                             | Tempo limite rígido para o subagente de memória de bloqueio                                             |
| `config.maxSummaryChars`    | `number`                                                                                             | Máximo de caracteres totais permitidos no resumo da memória ativa                                       |
| `config.logging`            | `boolean`                                                                                            | Emite logs da memória ativa durante o ajuste fino                                                       |
| `config.persistTranscripts` | `boolean`                                                                                            | Mantém em disco as transcrições do subagente de memória de bloqueio em vez de excluir arquivos temporários |
| `config.transcriptDir`      | `string`                                                                                             | Diretório relativo das transcrições do subagente de memória de bloqueio dentro da pasta de sessões do agente |

Campos úteis para ajuste fino:

| Chave                         | Tipo     | Significado                                                   |
| ----------------------------- | -------- | ------------------------------------------------------------- |
| `config.maxSummaryChars`      | `number` | Máximo de caracteres totais permitidos no resumo da memória ativa |
| `config.recentUserTurns`      | `number` | Turnos anteriores do usuário a incluir quando `queryMode` é `recent` |
| `config.recentAssistantTurns` | `number` | Turnos anteriores do assistente a incluir quando `queryMode` é `recent` |
| `config.recentUserChars`      | `number` | Máximo de caracteres por turno recente do usuário             |
| `config.recentAssistantChars` | `number` | Máximo de caracteres por turno recente do assistente          |
| `config.cacheTtlMs`           | `number` | Reutilização de cache para consultas idênticas repetidas      |

## Configuração recomendada

Comece com `recent`.

```json5
{
  plugins: {
    entries: {
      "active-memory": {
        enabled: true,
        config: {
          agents: ["main"],
          queryMode: "recent",
          promptStyle: "balanced",
          timeoutMs: 15000,
          maxSummaryChars: 220,
          logging: true,
        },
      },
    },
  },
}
```

Se você quiser inspecionar o comportamento ao vivo durante o ajuste fino, use `/verbose on` na
sessão em vez de procurar um comando de depuração separado da memória ativa.

Depois passe para:

- `message` se quiser menor latência
- `full` se decidir que o contexto extra vale o subagente de memória de bloqueio mais lento

## Depuração

Se a memória ativa não estiver aparecendo onde você espera:

1. Confirme que o plugin está habilitado em `plugins.entries.active-memory.enabled`.
2. Confirme que o id do agente atual está listado em `config.agents`.
3. Confirme que você está testando por meio de uma sessão de chat persistente interativa.
4. Ative `config.logging: true` e observe os logs do gateway.
5. Verifique se a própria pesquisa de memória funciona com `openclaw memory status --deep`.

Se os resultados de memória estiverem ruidosos, ajuste:

- `maxSummaryChars`

Se a memória ativa estiver lenta demais:

- reduza `queryMode`
- reduza `timeoutMs`
- reduza as contagens de turnos recentes
- reduza os limites de caracteres por turno

## Páginas relacionadas

- [Pesquisa de memória](/pt-BR/concepts/memory-search)
- [Referência de configuração de memória](/pt-BR/reference/memory-config)
- [Configuração do Plugin SDK](/pt-BR/plugins/sdk-setup)
