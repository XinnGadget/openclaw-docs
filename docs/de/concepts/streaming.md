---
read_when:
    - Erklärung, wie Streaming oder Chunking auf Kanälen funktioniert
    - Ändern des Block-Streamings oder des Kanal-Chunking-Verhaltens
    - Debuggen von doppelten/frühen Blockantworten oder Kanal-Vorschau-Streaming
summary: Verhalten von Streaming + Chunking (Blockantworten, Kanal-Vorschau-Streaming, Moduszuordnung)
title: Streaming und Chunking
x-i18n:
    generated_at: "2026-04-08T06:01:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: a8e847bb7da890818cd79dec7777f6ae488e6d6c0468e948e56b6b6c598e0000
    source_path: concepts/streaming.md
    workflow: 15
---

# Streaming + Chunking

OpenClaw hat zwei getrennte Streaming-Ebenen:

- **Block-Streaming (Kanäle):** sendet abgeschlossene **Blöcke**, während der Assistent schreibt. Das sind normale Kanalnachrichten (keine Token-Deltas).
- **Vorschau-Streaming (Telegram/Discord/Slack):** aktualisiert während der Generierung eine temporäre **Vorschau-Nachricht**.

Es gibt heute **kein echtes Token-Delta-Streaming** für Kanalnachrichten. Vorschau-Streaming ist nachrichtenbasiert (Senden + Bearbeitungen/Anhänge).

## Block-Streaming (Kanalnachrichten)

Block-Streaming sendet Assistent-Ausgaben in groben Chunks, sobald sie verfügbar werden.

```
Model output
  └─ text_delta/events
       ├─ (blockStreamingBreak=text_end)
       │    └─ chunker emits blocks as buffer grows
       └─ (blockStreamingBreak=message_end)
            └─ chunker flushes at message_end
                   └─ channel send (block replies)
```

Legende:

- `text_delta/events`: Stream-Ereignisse des Modells (bei nicht-streamenden Modellen möglicherweise spärlich).
- `chunker`: `EmbeddedBlockChunker`, der Mindest-/Höchstgrenzen + Trennpräferenz anwendet.
- `channel send`: tatsächliche ausgehende Nachrichten (Blockantworten).

**Steuerungen:**

- `agents.defaults.blockStreamingDefault`: `"on"`/`"off"` (standardmäßig aus).
- Kanalüberschreibungen: `*.blockStreaming` (und Varianten pro Konto), um `"on"`/`"off"` pro Kanal zu erzwingen.
- `agents.defaults.blockStreamingBreak`: `"text_end"` oder `"message_end"`.
- `agents.defaults.blockStreamingChunk`: `{ minChars, maxChars, breakPreference? }`.
- `agents.defaults.blockStreamingCoalesce`: `{ minChars?, maxChars?, idleMs? }` (zusammengeführte gestreamte Blöcke vor dem Senden).
- Feste Kanalobergrenze: `*.textChunkLimit` (z. B. `channels.whatsapp.textChunkLimit`).
- Kanal-Chunk-Modus: `*.chunkMode` (`length` standardmäßig, `newline` teilt an Leerzeilen (Absatzgrenzen), bevor nach Länge gechunked wird).
- Discord-Softlimit: `channels.discord.maxLinesPerMessage` (standardmäßig 17) teilt hohe Antworten, um UI-Abschneiden zu vermeiden.

**Grenzsemantik:**

- `text_end`: Blöcke streamen, sobald der Chunker sie ausgibt; bei jedem `text_end` flushen.
- `message_end`: warten, bis die Assistent-Nachricht fertig ist, dann gepufferte Ausgabe flushen.

`message_end` verwendet weiterhin den Chunker, wenn der gepufferte Text `maxChars` überschreitet, sodass am Ende mehrere Chunks ausgegeben werden können.

## Chunking-Algorithmus (untere/obere Grenzen)

Block-Chunking wird von `EmbeddedBlockChunker` implementiert:

- **Untere Grenze:** nichts ausgeben, bis der Puffer >= `minChars` ist (außer wenn erzwungen).
- **Obere Grenze:** Trennungen vor `maxChars` bevorzugen; wenn erzwungen, bei `maxChars` trennen.
- **Trennpräferenz:** `paragraph` → `newline` → `sentence` → `whitespace` → harter Umbruch.
- **Code-Fences:** niemals innerhalb von Fences trennen; wenn bei `maxChars` erzwungen, die Fence schließen + erneut öffnen, damit Markdown gültig bleibt.

`maxChars` wird auf das kanalbezogene `textChunkLimit` begrenzt, sodass per-Kanal-Limits nicht überschritten werden können.

## Coalescing (gestreamte Blöcke zusammenführen)

Wenn Block-Streaming aktiviert ist, kann OpenClaw **aufeinanderfolgende Block-Chunks zusammenführen**,
bevor sie gesendet werden. Das reduziert „Einzelzeilen-Spam“ und liefert trotzdem
eine schrittweise Ausgabe.

- Coalescing wartet vor dem Flushen auf **Leerlauf-Lücken** (`idleMs`).
- Puffer sind durch `maxChars` begrenzt und werden geflusht, wenn sie diesen Wert überschreiten.
- `minChars` verhindert, dass winzige Fragmente gesendet werden, bevor genug Text zusammenkommt
  (der abschließende Flush sendet immer den restlichen Text).
- Der Verknüpfer wird aus `blockStreamingChunk.breakPreference`
  abgeleitet (`paragraph` → `\n\n`, `newline` → `\n`, `sentence` → Leerzeichen).
- Kanalüberschreibungen sind über `*.blockStreamingCoalesce` verfügbar (einschließlich Konfigurationen pro Konto).
- Das standardmäßige Coalesce-`minChars` wird für Signal/Slack/Discord auf 1500 erhöht, sofern nicht überschrieben.

## Menschlich wirkendes Timing zwischen Blöcken

Wenn Block-Streaming aktiviert ist, können Sie eine **zufällige Pause** zwischen
Blockantworten hinzufügen (nach dem ersten Block). Dadurch wirken Antworten mit
mehreren Blasen natürlicher.

- Konfiguration: `agents.defaults.humanDelay` (Überschreibung pro Agent über `agents.list[].humanDelay`).
- Modi: `off` (Standard), `natural` (800–2500ms), `custom` (`minMs`/`maxMs`).
- Gilt nur für **Blockantworten**, nicht für endgültige Antworten oder Tool-Zusammenfassungen.

## "Chunks streamen oder alles"

Dies wird wie folgt zugeordnet:

- **Chunks streamen:** `blockStreamingDefault: "on"` + `blockStreamingBreak: "text_end"` (während der Ausgabe senden). Nicht-Telegram-Kanäle benötigen zusätzlich `*.blockStreaming: true`.
- **Alles am Ende streamen:** `blockStreamingBreak: "message_end"` (einmal flushen, möglicherweise mehrere Chunks, wenn sehr lang).
- **Kein Block-Streaming:** `blockStreamingDefault: "off"` (nur endgültige Antwort).

**Hinweis zu Kanälen:** Block-Streaming ist **deaktiviert, solange nicht**
`*.blockStreaming` explizit auf `true` gesetzt ist. Kanäle können eine Live-Vorschau
(`channels.<channel>.streaming`) streamen, ohne Blockantworten zu senden.

Zur Erinnerung zum Konfigurationsort: Die `blockStreaming*`-Standards befinden sich unter
`agents.defaults`, nicht in der Root-Konfiguration.

## Vorschau-Streaming-Modi

Kanonischer Schlüssel: `channels.<channel>.streaming`

Modi:

- `off`: Vorschau-Streaming deaktivieren.
- `partial`: einzelne Vorschau, die durch den neuesten Text ersetzt wird.
- `block`: Vorschau-Aktualisierungen in gechunkten/angehängten Schritten.
- `progress`: Fortschritts-/Statusvorschau während der Generierung, endgültige Antwort nach Abschluss.

### Kanalzuordnung

| Kanal    | `off` | `partial` | `block` | `progress`        |
| -------- | ----- | --------- | ------- | ----------------- |
| Telegram | ✅    | ✅        | ✅      | wird `partial` zugeordnet |
| Discord  | ✅    | ✅        | ✅      | wird `partial` zugeordnet |
| Slack    | ✅    | ✅        | ✅      | ✅                |

Nur Slack:

- `channels.slack.streaming.nativeTransport` schaltet Slack-native Streaming-API-Aufrufe um, wenn `channels.slack.streaming.mode="partial"` (Standard: `true`).
- Slack-natives Streaming und der Slack-Assistent-Thread-Status erfordern ein Antwort-Thread-Ziel; DMs auf oberster Ebene zeigen diese Thread-Vorschau nicht an.

Migration von Legacy-Schlüsseln:

- Telegram: `streamMode` + boolesches `streaming` werden automatisch zur `streaming`-Enum migriert.
- Discord: `streamMode` + boolesches `streaming` werden automatisch zur `streaming`-Enum migriert.
- Slack: `streamMode` wird automatisch zu `streaming.mode` migriert; boolesches `streaming` wird automatisch zu `streaming.mode` plus `streaming.nativeTransport` migriert; Legacy-`nativeStreaming` wird automatisch zu `streaming.nativeTransport` migriert.

### Laufzeitverhalten

Telegram:

- Verwendet `sendMessage` + `editMessageText` für Vorschau-Aktualisierungen in DMs sowie Gruppen/Themen.
- Vorschau-Streaming wird übersprungen, wenn Telegram-Block-Streaming explizit aktiviert ist (um doppeltes Streaming zu vermeiden).
- `/reasoning stream` kann Reasoning in die Vorschau schreiben.

Discord:

- Verwendet Vorschau-Nachrichten mit Senden + Bearbeiten.
- Der Modus `block` verwendet Draft-Chunking (`draftChunk`).
- Vorschau-Streaming wird übersprungen, wenn Discord-Block-Streaming explizit aktiviert ist.

Slack:

- `partial` kann Slack-natives Streaming (`chat.startStream`/`append`/`stop`) verwenden, wenn verfügbar.
- `block` verwendet Vorschauen im Anhänge-Stil für Entwürfe.
- `progress` verwendet Statusvorschautext und danach die endgültige Antwort.

## Verwandt

- [Nachrichten](/de/concepts/messages) — Nachrichtenlebenszyklus und Zustellung
- [Wiederholung](/de/concepts/retry) — Wiederholungsverhalten bei Zustellungsfehlern
- [Kanäle](/de/channels) — Streaming-Unterstützung pro Kanal
