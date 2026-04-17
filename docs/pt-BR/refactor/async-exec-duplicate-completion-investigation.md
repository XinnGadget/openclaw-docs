---
x-i18n:
    generated_at: "2026-04-16T05:37:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: 95e56c5411204363676f002059c942201503e2359515d1a4b409882cc2e04920
    source_path: refactor/async-exec-duplicate-completion-investigation.md
    workflow: 15
---

# Investigação de Conclusão Duplicada de Async Exec

## Escopo

- Sessão: `agent:main:telegram:group:-1003774691294:topic:1`
- Sintoma: a mesma conclusão de async exec para a sessão/run `keen-nexus` foi registrada duas vezes no LCM como turnos do usuário.
- Objetivo: identificar se isso é mais provavelmente injeção duplicada na sessão ou simples retry de entrega de saída.

## Conclusão

Muito provavelmente isso é **injeção duplicada na sessão**, não um retry puro de entrega de saída.

A lacuna mais forte no lado do Gateway está no **caminho de conclusão de exec do Node**:

1. Um término de exec no lado do Node emite `exec.finished` com o `runId` completo.
2. O Gateway `server-node-events` converte isso em um evento de sistema e solicita um heartbeat.
3. A execução do heartbeat injeta o bloco de eventos de sistema drenado no prompt do agente.
4. O runner embutido persiste esse prompt como um novo turno do usuário na transcrição da sessão.

Se o mesmo `exec.finished` chegar ao Gateway duas vezes para o mesmo `runId` por qualquer motivo (replay, duplicata em reconexão, reenvio upstream, produtor duplicado), o OpenClaw atualmente **não tem verificação de idempotência com chave em `runId`/`contextKey`** nesse caminho. A segunda cópia se tornará uma segunda mensagem de usuário com o mesmo conteúdo.

## Caminho Exato no Código

### 1. Produtor: evento de conclusão de exec no Node

- `src/node-host/invoke.ts:340-360`
  - `sendExecFinishedEvent(...)` emite `node.event` com o evento `exec.finished`.
  - O payload inclui `sessionKey` e o `runId` completo.

### 2. Ingestão de eventos no Gateway

- `src/gateway/server-node-events.ts:574-640`
  - Processa `exec.finished`.
  - Constrói o texto:
    - `Exec finished (node=..., id=<runId>, code ...)`
  - Enfileira isso via:
    - `enqueueSystemEvent(text, { sessionKey, contextKey: runId ? \`exec:${runId}\` : "exec", trusted: false })`
  - Solicita imediatamente um wake:
    - `requestHeartbeatNow(scopedHeartbeatWakeOptions(sessionKey, { reason: "exec-event" }))`

### 3. Fragilidade na deduplicação de eventos de sistema

- `src/infra/system-events.ts:90-115`
  - `enqueueSystemEvent(...)` só suprime **texto duplicado consecutivo**:
    - `if (entry.lastText === cleaned) return false`
  - Ele armazena `contextKey`, mas **não** usa `contextKey` para idempotência.
  - Após o drain, a supressão de duplicatas é reiniciada.

Isso significa que um `exec.finished` replayado com o mesmo `runId` pode ser aceito novamente mais tarde, embora o código já tivesse um candidato estável para idempotência (`exec:<runId>`).

### 4. O tratamento de wake não é o principal duplicador

- `src/infra/heartbeat-wake.ts:79-117`
  - Os wakes são consolidados por `(agentId, sessionKey)`.
  - Solicitações de wake duplicadas para o mesmo alvo colapsam em uma única entrada de wake pendente.

Isso faz de **tratamento duplicado de wake isoladamente** uma explicação mais fraca do que ingestão duplicada de evento.

### 5. O heartbeat consome o evento e o transforma em entrada de prompt

- `src/infra/heartbeat-runner.ts:535-574`
  - O preflight faz peek nos eventos de sistema pendentes e classifica execuções de exec-event.
- `src/auto-reply/reply/session-system-events.ts:86-90`
  - `drainFormattedSystemEvents(...)` drena a fila da sessão.
- `src/auto-reply/reply/get-reply-run.ts:400-427`
  - O bloco drenado de eventos de sistema é prefixado no corpo do prompt do agente.

### 6. Ponto de injeção na transcrição

- `src/agents/pi-embedded-runner/run/attempt.ts:2000-2017`
  - `activeSession.prompt(effectivePrompt)` envia o prompt completo para a sessão PI embutida.
  - Esse é o ponto em que o prompt derivado da conclusão se torna um turno persistido do usuário.

Portanto, uma vez que o mesmo evento de sistema seja reconstruído no prompt duas vezes, mensagens duplicadas de usuário no LCM são esperadas.

## Por que retry puro de entrega de saída é menos provável

Existe um caminho real de falha de saída no runner de heartbeat:

- `src/infra/heartbeat-runner.ts:1194-1242`
  - A resposta é gerada primeiro.
  - A entrega de saída acontece depois via `deliverOutboundPayloads(...)`.
  - Falha ali retorna `{ status: "failed" }`.

No entanto, para a mesma entrada da fila de evento de sistema, isso sozinho **não é suficiente** para explicar os turnos duplicados do usuário:

- `src/auto-reply/reply/session-system-events.ts:86-90`
  - A fila de eventos de sistema já é drenada antes da entrega de saída.

Assim, um retry de envio do canal por si só não recriaria exatamente o mesmo evento enfileirado. Isso poderia explicar entrega externa ausente/com falha, mas não, por si só, uma segunda mensagem idêntica de usuário na sessão.

## Possibilidade secundária, de menor confiança

Existe um loop de retry de execução completa no runner do agente:

- `src/auto-reply/reply/agent-runner-execution.ts:741-1473`
  - Certas falhas transitórias podem repetir a execução inteira e reenviar o mesmo `commandBody`.

Isso pode duplicar um prompt persistido do usuário **dentro da mesma execução de resposta** se o prompt já tiver sido anexado antes da condição de retry disparar.

Eu classifico isso abaixo de ingestão duplicada de `exec.finished` porque:

- o intervalo observado foi de cerca de 51 segundos, o que parece mais um segundo wake/turno do que um retry em processo;
- o relatório já menciona falhas repetidas de envio de mensagem, o que aponta mais para um turno posterior separado do que para um retry imediato de modelo/runtime.

## Hipótese de Causa Raiz

Hipótese de maior confiança:

- A conclusão `keen-nexus` veio pelo **caminho de evento de exec do Node**.
- O mesmo `exec.finished` foi entregue ao `server-node-events` duas vezes.
- O Gateway aceitou ambos porque `enqueueSystemEvent(...)` não deduplica por `contextKey` / `runId`.
- Cada evento aceito disparou um heartbeat e foi injetado como um turno do usuário na transcrição do PI.

## Pequena Correção Cirúrgica Proposta

Se uma correção for desejada, a menor mudança de alto valor é:

- fazer a idempotência de exec/evento de sistema respeitar `contextKey` por uma janela curta, pelo menos para repetições exatas de `(sessionKey, contextKey, text)`;
- ou adicionar uma deduplicação dedicada em `server-node-events` para `exec.finished`, com chave em `(sessionKey, runId, tipo de evento)`.

Isso bloquearia diretamente duplicatas replayadas de `exec.finished` antes que se tornem turnos da sessão.
