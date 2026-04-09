---
read_when:
    - Sie benötigen eine genaue Schritt-für-Schritt-Erklärung der Agentenschleife oder der Lebenszyklusereignisse
summary: Lebenszyklus der Agentenschleife, Streams und Warte-Semantik
title: Agentenschleife
x-i18n:
    generated_at: "2026-04-09T01:28:00Z"
    model: gpt-5.4
    provider: openai
    source_hash: 32d3a73df8dabf449211a6183a70dcfd2a9b6f584dc76d0c4c9147582b2ca6a1
    source_path: concepts/agent-loop.md
    workflow: 15
---

# Agentenschleife (OpenClaw)

Eine agentische Schleife ist der vollständige „echte“ Lauf eines Agenten: Eingabe → Kontextzusammenstellung → Modellinferenz →
Werkzeugausführung → gestreamte Antworten → Persistenz. Es ist der maßgebliche Pfad, der eine Nachricht
in Aktionen und eine endgültige Antwort umwandelt und dabei den Sitzungszustand konsistent hält.

In OpenClaw ist eine Schleife ein einzelner, serialisierter Lauf pro Sitzung, der Lebenszyklus- und Stream-Ereignisse ausgibt,
während das Modell nachdenkt, Werkzeuge aufruft und Ausgaben streamt. Dieses Dokument erklärt, wie diese authentische Schleife Ende-zu-Ende
verdrahtet ist.

## Einstiegspunkte

- Gateway RPC: `agent` und `agent.wait`.
- CLI: Befehl `agent`.

## Funktionsweise (Überblick)

1. RPC `agent` validiert Parameter, löst die Sitzung auf (`sessionKey`/`sessionId`), persistiert Sitzungsmetadaten und gibt sofort `{ runId, acceptedAt }` zurück.
2. `agentCommand` führt den Agenten aus:
   - löst Modell- sowie Thinking-/Verbose-Standards auf
   - lädt den Skills-Snapshot
   - ruft `runEmbeddedPiAgent` auf (Laufzeit von pi-agent-core)
   - gibt **Lebenszyklus-Ende/Fehler** aus, wenn die eingebettete Schleife keines davon ausgibt
3. `runEmbeddedPiAgent`:
   - serialisiert Läufe über sitzungsbezogene und globale Queues
   - löst Modell- und Auth-Profil auf und erstellt die Pi-Sitzung
   - abonniert Pi-Ereignisse und streamt Assistant-/Werkzeug-Deltas
   - erzwingt ein Timeout -> bricht den Lauf bei Überschreitung ab
   - gibt Nutzlasten und Nutzungsmetadaten zurück
4. `subscribeEmbeddedPiSession` überbrückt pi-agent-core-Ereignisse zum OpenClaw-`agent`-Stream:
   - Werkzeugereignisse => `stream: "tool"`
   - Assistant-Deltas => `stream: "assistant"`
   - Lebenszyklusereignisse => `stream: "lifecycle"` (`phase: "start" | "end" | "error"`)
5. `agent.wait` verwendet `waitForAgentRun`:
   - wartet auf **Lebenszyklus-Ende/Fehler** für `runId`
   - gibt `{ status: ok|error|timeout, startedAt, endedAt, error? }` zurück

## Queueing + Nebenläufigkeit

- Läufe werden pro Sitzungsschlüssel (Sitzungs-Lane) und optional über eine globale Lane serialisiert.
- Dies verhindert Wettlaufsituationen bei Werkzeugen/Sitzungen und hält den Sitzungsverlauf konsistent.
- Messaging-Kanäle können Queue-Modi auswählen (collect/steer/followup), die in dieses Lane-System einspeisen.
  Siehe [Befehlswarteschlange](/de/concepts/queue).

## Sitzungs- und Workspace-Vorbereitung

- Der Workspace wird aufgelöst und erstellt; sandboxed Läufe können auf ein Sandbox-Workspace-Stammverzeichnis umgeleitet werden.
- Skills werden geladen (oder aus einem Snapshot wiederverwendet) und in Umgebungsvariablen und Prompt injiziert.
- Bootstrap-/Kontextdateien werden aufgelöst und in den Bericht des System-Prompts injiziert.
- Eine Schreibsperre für die Sitzung wird erworben; `SessionManager` wird geöffnet und vor dem Streaming vorbereitet.

## Prompt-Zusammenstellung + System-Prompt

- Der System-Prompt wird aus dem Basisprompt von OpenClaw, dem Skills-Prompt, dem Bootstrap-Kontext und laufspezifischen Überschreibungen aufgebaut.
- Modellspezifische Limits und für Kompaktierung reservierte Tokens werden erzwungen.
- Unter [System-Prompt](/de/concepts/system-prompt) sehen Sie, was das Modell sieht.

## Hook-Punkte (wo Sie eingreifen können)

OpenClaw hat zwei Hook-Systeme:

- **Interne Hooks** (Gateway-Hooks): ereignisgesteuerte Skripte für Befehle und Lebenszyklusereignisse.
- **Plugin-Hooks**: Erweiterungspunkte innerhalb des Agenten-/Werkzeug-Lebenszyklus und der Gateway-Pipeline.

### Interne Hooks (Gateway-Hooks)

- **`agent:bootstrap`**: wird ausgeführt, während Bootstrap-Dateien erstellt werden, bevor der System-Prompt finalisiert wird.
  Verwenden Sie dies, um Bootstrap-Kontextdateien hinzuzufügen oder zu entfernen.
- **Befehls-Hooks**: `/new`, `/reset`, `/stop` und andere Befehlsereignisse (siehe Hook-Dokumentation).

Unter [Hooks](/de/automation/hooks) finden Sie Einrichtung und Beispiele.

### Plugin-Hooks (Agenten- und Gateway-Lebenszyklus)

Diese werden innerhalb der Agentenschleife oder der Gateway-Pipeline ausgeführt:

- **`before_model_resolve`**: wird vor der Sitzung ausgeführt (ohne `messages`), um Provider/Modell vor der Modellauflösung deterministisch zu überschreiben.
- **`before_prompt_build`**: wird nach dem Laden der Sitzung ausgeführt (mit `messages`), um `prependContext`, `systemPrompt`, `prependSystemContext` oder `appendSystemContext` vor dem Senden des Prompts einzuschleusen. Verwenden Sie `prependContext` für dynamischen Text pro Turn und die Systemkontext-Felder für stabile Hinweise, die im Bereich des System-Prompts liegen sollen.
- **`before_agent_start`**: Legacy-Kompatibilitätshook, der in beiden Phasen ausgeführt werden kann; bevorzugen Sie die expliziten Hooks oben.
- **`before_agent_reply`**: wird nach Inline-Aktionen und vor dem LLM-Aufruf ausgeführt und ermöglicht es einem Plugin, den Turn zu übernehmen und eine synthetische Antwort zurückzugeben oder den Turn vollständig stummzuschalten.
- **`agent_end`**: inspiziert die endgültige Nachrichtenliste und Metadaten des Laufs nach Abschluss.
- **`before_compaction` / `after_compaction`**: beobachten oder annotieren Kompaktierungszyklen.
- **`before_tool_call` / `after_tool_call`**: fangen Werkzeugparameter/-ergebnisse ab.
- **`before_install`**: inspiziert integrierte Scan-Ergebnisse und kann Skill- oder Plugin-Installationen optional blockieren.
- **`tool_result_persist`**: transformiert Werkzeugergebnisse synchron, bevor sie in das Sitzungsprotokoll geschrieben werden.
- **`message_received` / `message_sending` / `message_sent`**: Hooks für eingehende und ausgehende Nachrichten.
- **`session_start` / `session_end`**: Grenzen des Sitzungslebenszyklus.
- **`gateway_start` / `gateway_stop`**: Gateway-Lebenszyklusereignisse.

Entscheidungsregeln für ausgehende/Werkzeug-Schutzmechanismen bei Hooks:

- `before_tool_call`: `{ block: true }` ist final und stoppt Handler mit niedrigerer Priorität.
- `before_tool_call`: `{ block: false }` ist eine No-Op und hebt eine vorherige Blockierung nicht auf.
- `before_install`: `{ block: true }` ist final und stoppt Handler mit niedrigerer Priorität.
- `before_install`: `{ block: false }` ist eine No-Op und hebt eine vorherige Blockierung nicht auf.
- `message_sending`: `{ cancel: true }` ist final und stoppt Handler mit niedrigerer Priorität.
- `message_sending`: `{ cancel: false }` ist eine No-Op und hebt einen vorherigen Abbruch nicht auf.

Unter [Plugin-Hooks](/de/plugins/architecture#provider-runtime-hooks) finden Sie die Hook-API sowie Details zur Registrierung.

## Streaming + partielle Antworten

- Assistant-Deltas werden von pi-agent-core gestreamt und als `assistant`-Ereignisse ausgegeben.
- Block-Streaming kann partielle Antworten entweder bei `text_end` oder `message_end` ausgeben.
- Reasoning-Streaming kann als separater Stream oder als Blockantworten ausgegeben werden.
- Unter [Streaming](/de/concepts/streaming) finden Sie Informationen zum Chunking und zum Verhalten von Blockantworten.

## Werkzeugausführung + Messaging-Werkzeuge

- Ereignisse für Start/Aktualisierung/Ende von Werkzeugen werden im `tool`-Stream ausgegeben.
- Werkzeugergebnisse werden vor dem Protokollieren/Ausgeben in Bezug auf Größe und Bildnutzlasten bereinigt.
- Sendevorgänge von Messaging-Werkzeugen werden verfolgt, um doppelte Bestätigungen durch den Assistant zu unterdrücken.

## Antwortformung + Unterdrückung

- Endgültige Nutzlasten werden zusammengestellt aus:
  - Assistant-Text (und optional Reasoning)
  - Inline-Werkzeugzusammenfassungen (wenn verbose + erlaubt)
  - Assistant-Fehlertext bei Modellfehlern
- Das exakte stumme Token `NO_REPLY` / `no_reply` wird aus ausgehenden
  Nutzlasten herausgefiltert.
- Duplikate von Messaging-Werkzeugen werden aus der endgültigen Nutzlastliste entfernt.
- Wenn keine darstellbaren Nutzlasten verbleiben und ein Werkzeug einen Fehler erzeugt hat, wird
  eine Fallback-Antwort für Werkzeugfehler ausgegeben
  (es sei denn, ein Messaging-Werkzeug hat bereits eine für Benutzer sichtbare Antwort gesendet).

## Kompaktierung + Wiederholungen

- Die automatische Kompaktierung gibt `compaction`-Stream-Ereignisse aus und kann eine Wiederholung auslösen.
- Bei einer Wiederholung werden In-Memory-Puffer und Werkzeugzusammenfassungen zurückgesetzt, um doppelte Ausgaben zu vermeiden.
- Unter [Kompaktierung](/de/concepts/compaction) finden Sie die Kompaktierungs-Pipeline.

## Ereignis-Streams (heute)

- `lifecycle`: ausgegeben von `subscribeEmbeddedPiSession` (und als Fallback von `agentCommand`)
- `assistant`: gestreamte Deltas von pi-agent-core
- `tool`: gestreamte Werkzeugereignisse von pi-agent-core

## Handhabung von Chat-Kanälen

- Assistant-Deltas werden in Chat-`delta`-Nachrichten gepuffert.
- Ein Chat-`final` wird bei **Lebenszyklus-Ende/Fehler** ausgegeben.

## Timeouts

- Standard für `agent.wait`: 30 s (nur das Warten). Der Parameter `timeoutMs` überschreibt dies.
- Agentenlaufzeit: Standard für `agents.defaults.timeoutSeconds` ist 172800 s (48 Stunden); erzwungen im Abort-Timer von `runEmbeddedPiAgent`.
- LLM-Leerlauf-Timeout: `agents.defaults.llm.idleTimeoutSeconds` bricht eine Modellanfrage ab, wenn vor Ablauf des Leerlauffensters keine Antwort-Chunks eintreffen. Legen Sie es explizit für langsame lokale Modelle oder Reasoning-/Werkzeugaufruf-Provider fest; setzen Sie es auf 0, um es zu deaktivieren. Wenn es nicht gesetzt ist, verwendet OpenClaw `agents.defaults.timeoutSeconds`, falls konfiguriert, andernfalls 60 s. Durch Cron ausgelöste Läufe ohne explizites LLM- oder Agenten-Timeout deaktivieren den Leerlauf-Wächter und verlassen sich auf das äußere Cron-Timeout.

## Wo Dinge vorzeitig enden können

- Agenten-Timeout (Abbruch)
- AbortSignal (Abbruch)
- Gateway-Trennung oder RPC-Timeout
- `agent.wait`-Timeout (nur Warten, stoppt den Agenten nicht)

## Verwandt

- [Werkzeuge](/de/tools) — verfügbare Agentenwerkzeuge
- [Hooks](/de/automation/hooks) — ereignisgesteuerte Skripte, die durch Agenten-Lebenszyklusereignisse ausgelöst werden
- [Kompaktierung](/de/concepts/compaction) — wie lange Unterhaltungen zusammengefasst werden
- [Exec-Genehmigungen](/de/tools/exec-approvals) — Genehmigungsschranken für Shell-Befehle
- [Thinking](/de/tools/thinking) — Konfiguration der Thinking-/Reasoning-Stufe
