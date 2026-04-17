---
x-i18n:
    generated_at: "2026-04-16T06:22:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: 95e56c5411204363676f002059c942201503e2359515d1a4b409882cc2e04920
    source_path: refactor/async-exec-duplicate-completion-investigation.md
    workflow: 15
---

# Untersuchung zu doppeltem Abschluss bei Async Exec

## Umfang

- Sitzung: `agent:main:telegram:group:-1003774691294:topic:1`
- Symptom: Derselbe Async-Exec-Abschluss für Sitzung/Run `keen-nexus` wurde in LCM zweimal als Nutzer-Turn erfasst.
- Ziel: Ermitteln, ob dies höchstwahrscheinlich eine doppelte Sitzungsinjektion oder ein einfacher Retry bei der ausgehenden Zustellung ist.

## Schlussfolgerung

Am wahrscheinlichsten ist dies eine **doppelte Sitzungsinjektion**, nicht ein reiner Retry bei der ausgehenden Zustellung.

Die stärkste Lücke auf Gateway-Seite liegt im **Pfad für Node-Exec-Abschlüsse**:

1. Ein Exec-Abschluss auf Node-Seite sendet `exec.finished` mit der vollständigen `runId`.
2. Gateway `server-node-events` wandelt das in ein System-Event um und fordert einen Heartbeat an.
3. Der Heartbeat-Run injiziert den geleerten System-Event-Block in den Agent-Prompt.
4. Der eingebettete Runner persistiert diesen Prompt als neuen Nutzer-Turn im Sitzungs-Transkript.

Wenn dasselbe `exec.finished` aus irgendeinem Grund (Replay, erneute Verbindung mit Duplikat, erneutes Senden Upstream, duplizierter Producer) zweimal mit derselben `runId` beim Gateway ankommt, hat OpenClaw auf diesem Pfad derzeit **keine Idempotenzprüfung, die nach `runId`/`contextKey` schlüsselt**. Die zweite Kopie wird zu einer zweiten Nutzernachricht mit identischem Inhalt.

## Exakter Code-Pfad

### 1. Producer: Event für Node-Exec-Abschluss

- `src/node-host/invoke.ts:340-360`
  - `sendExecFinishedEvent(...)` sendet `node.event` mit dem Event `exec.finished`.
  - Die Payload enthält `sessionKey` und die vollständige `runId`.

### 2. Gateway-Event-Ingestion

- `src/gateway/server-node-events.ts:574-640`
  - Verarbeitet `exec.finished`.
  - Baut Text auf:
    - `Exec finished (node=..., id=<runId>, code ...)`
  - Stellt ihn in die Queue über:
    - `enqueueSystemEvent(text, { sessionKey, contextKey: runId ? \`exec:${runId}\` : "exec", trusted: false })`
  - Fordert sofort ein Wake an:
    - `requestHeartbeatNow(scopedHeartbeatWakeOptions(sessionKey, { reason: "exec-event" }))`

### 3. Schwäche bei der Deduplizierung von System-Events

- `src/infra/system-events.ts:90-115`
  - `enqueueSystemEvent(...)` unterdrückt nur **aufeinanderfolgende doppelte Texte**:
    - `if (entry.lastText === cleaned) return false`
  - Es speichert `contextKey`, verwendet `contextKey` jedoch **nicht** für Idempotenz.
  - Nach dem Drain wird die Duplikatunterdrückung zurückgesetzt.

Das bedeutet: Ein erneut gesendetes `exec.finished` mit derselben `runId` kann später erneut akzeptiert werden, obwohl der Code bereits einen stabilen Kandidaten für Idempotenz hatte (`exec:<runId>`).

### 4. Wake-Handling ist nicht der primäre Verursacher von Duplikaten

- `src/infra/heartbeat-wake.ts:79-117`
  - Wakes werden nach `(agentId, sessionKey)` zusammengefasst.
  - Doppelte Wake-Anfragen für dasselbe Ziel werden zu einem ausstehenden Wake-Eintrag zusammengeführt.

Dadurch ist **doppeltes Wake-Handling allein** eine schwächere Erklärung als doppelte Event-Ingestion.

### 5. Heartbeat verarbeitet das Event und macht daraus Prompt-Eingabe

- `src/infra/heartbeat-runner.ts:535-574`
  - Preflight prüft ausstehende System-Events vorab und klassifiziert Runs mit Exec-Events.
- `src/auto-reply/reply/session-system-events.ts:86-90`
  - `drainFormattedSystemEvents(...)` leert die Queue für die Sitzung.
- `src/auto-reply/reply/get-reply-run.ts:400-427`
  - Der geleerte System-Event-Block wird dem Agent-Prompt-Body vorangestellt.

### 6. Injektionspunkt ins Transkript

- `src/agents/pi-embedded-runner/run/attempt.ts:2000-2017`
  - `activeSession.prompt(effectivePrompt)` übergibt den vollständigen Prompt an die eingebettete PI-Sitzung.
  - Das ist der Punkt, an dem der vom Abschluss abgeleitete Prompt als persistierter Nutzer-Turn gespeichert wird.

Sobald also dasselbe System-Event zweimal in den Prompt eingebaut wird, sind doppelte LCM-Nutzernachrichten zu erwarten.

## Warum ein einfacher Retry bei der ausgehenden Zustellung weniger wahrscheinlich ist

Es gibt einen realen Fehlerpfad für ausgehende Zustellung im Heartbeat-Runner:

- `src/infra/heartbeat-runner.ts:1194-1242`
  - Die Antwort wird zuerst generiert.
  - Die ausgehende Zustellung erfolgt später über `deliverOutboundPayloads(...)`.
  - Ein Fehler dort liefert `{ status: "failed" }` zurück.

Für denselben System-Event-Queue-Eintrag reicht das allein jedoch **nicht aus**, um die doppelten Nutzer-Turns zu erklären:

- `src/auto-reply/reply/session-system-events.ts:86-90`
  - Die System-Event-Queue ist bereits geleert, bevor die ausgehende Zustellung erfolgt.

Ein Retry beim Kanalversand allein würde das exakt gleiche Queue-Event also nicht erneut erzeugen. Das könnte fehlende/fehlgeschlagene externe Zustellung erklären, aber für sich genommen nicht eine zweite identische Nutzer-Nachricht in der Sitzung.

## Sekundäre Möglichkeit mit geringerer Sicherheit

Es gibt eine Retry-Schleife für vollständige Runs im Agent-Runner:

- `src/auto-reply/reply/agent-runner-execution.ts:741-1473`
  - Bestimmte transiente Fehler können den gesamten Run erneut versuchen und denselben `commandBody` erneut absenden.

Das kann einen persistierten Nutzer-Prompt **innerhalb derselben Antwortausführung** duplizieren, wenn der Prompt bereits angehängt wurde, bevor die Retry-Bedingung ausgelöst hat.

Ich stufe das niedriger ein als doppelte `exec.finished`-Ingestion, weil:

- der beobachtete Abstand bei etwa 51 Sekunden lag, was eher wie ein zweiter Wake/Turn aussieht als wie ein In-Process-Retry;
- im Bericht bereits wiederholte Fehler beim Nachrichtensenden erwähnt werden, was eher auf einen separaten späteren Turn hindeutet als auf einen unmittelbaren Modell-/Runtime-Retry.

## Hypothese zur Grundursache

Hypothese mit der höchsten Sicherheit:

- Der Abschluss von `keen-nexus` kam über den **Node-Exec-Event-Pfad**.
- Dasselbe `exec.finished` wurde zweimal an `server-node-events` zugestellt.
- Das Gateway akzeptierte beide, weil `enqueueSystemEvent(...)` nicht nach `contextKey` / `runId` dedupliziert.
- Jedes akzeptierte Event löste einen Heartbeat aus und wurde als Nutzer-Turn in das PI-Transkript injiziert.

## Vorgeschlagener kleiner, gezielter Fix

Falls ein Fix gewünscht ist, ist die kleinste Änderung mit hohem Nutzen:

- dafür zu sorgen, dass die Idempotenz von Exec-/System-Events `contextKey` für einen kurzen Zeitraum berücksichtigt, zumindest für exakte Wiederholungen von `(sessionKey, contextKey, text)`;
- oder eine dedizierte Deduplizierung in `server-node-events` für `exec.finished` hinzuzufügen, geschlüsselt nach `(sessionKey, runId, event kind)`.

Das würde erneut gesendete `exec.finished`-Duplikate direkt blockieren, bevor sie zu Sitzungsturns werden.
