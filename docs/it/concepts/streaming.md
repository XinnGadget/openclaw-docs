---
read_when:
    - Spiegare come funzionano lo streaming o il chunking sui canali
    - Modificare il comportamento dello streaming a blocchi o del chunking del canale
    - Eseguire il debug di risposte a blocchi duplicate/premature o dello streaming di anteprima del canale
summary: Comportamento di streaming + chunking (risposte a blocchi, streaming di anteprima del canale, mappatura delle modalità)
title: Streaming e Chunking
x-i18n:
    generated_at: "2026-04-08T06:00:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: a8e847bb7da890818cd79dec7777f6ae488e6d6c0468e948e56b6b6c598e0000
    source_path: concepts/streaming.md
    workflow: 15
---

# Streaming + chunking

OpenClaw ha due livelli di streaming separati:

- **Streaming a blocchi (canali):** emette **blocchi** completati mentre l'assistente scrive. Questi sono normali messaggi del canale (non delta di token).
- **Streaming di anteprima (Telegram/Discord/Slack):** aggiorna un **messaggio di anteprima** temporaneo durante la generazione.

Al momento **non esiste un vero streaming token-delta** verso i messaggi del canale. Lo streaming di anteprima è basato sui messaggi (invio + modifiche/append).

## Streaming a blocchi (messaggi del canale)

Lo streaming a blocchi invia l'output dell'assistente in chunk grossolani man mano che diventano disponibili.

```
Model output
  └─ text_delta/events
       ├─ (blockStreamingBreak=text_end)
       │    └─ chunker emits blocks as buffer grows
       └─ (blockStreamingBreak=message_end)
            └─ chunker flushes at message_end
                   └─ channel send (block replies)
```

Legenda:

- `text_delta/events`: eventi del flusso del modello (possono essere radi per i modelli non in streaming).
- `chunker`: `EmbeddedBlockChunker` che applica limiti min/max + preferenza di interruzione.
- `channel send`: messaggi effettivamente inviati in uscita (risposte a blocchi).

**Controlli:**

- `agents.defaults.blockStreamingDefault`: `"on"`/`"off"` (predefinito off).
- Override del canale: `*.blockStreaming` (e varianti per account) per forzare `"on"`/`"off"` per canale.
- `agents.defaults.blockStreamingBreak`: `"text_end"` o `"message_end"`.
- `agents.defaults.blockStreamingChunk`: `{ minChars, maxChars, breakPreference? }`.
- `agents.defaults.blockStreamingCoalesce`: `{ minChars?, maxChars?, idleMs? }` (unisce i blocchi in streaming prima dell'invio).
- Limite rigido del canale: `*.textChunkLimit` (ad esempio `channels.whatsapp.textChunkLimit`).
- Modalità di chunking del canale: `*.chunkMode` (`length` predefinito, `newline` divide sulle righe vuote (confini dei paragrafi) prima del chunking per lunghezza).
- Limite morbido di Discord: `channels.discord.maxLinesPerMessage` (predefinito 17) divide le risposte alte per evitare il clipping dell'interfaccia.

**Semantica dei confini:**

- `text_end`: trasmette i blocchi non appena il chunker li emette; svuota a ogni `text_end`.
- `message_end`: attende che il messaggio dell'assistente finisca, poi svuota l'output nel buffer.

`message_end` usa comunque il chunker se il testo nel buffer supera `maxChars`, quindi può emettere più chunk alla fine.

## Algoritmo di chunking (limiti basso/alto)

Il chunking a blocchi è implementato da `EmbeddedBlockChunker`:

- **Limite basso:** non emette finché il buffer non è >= `minChars` (a meno che non sia forzato).
- **Limite alto:** preferisce divisioni prima di `maxChars`; se forzato, divide a `maxChars`.
- **Preferenza di interruzione:** `paragraph` → `newline` → `sentence` → `whitespace` → interruzione forzata.
- **Blocchi di codice:** non divide mai all'interno dei blocchi; quando è forzato a `maxChars`, chiude e riapre il blocco per mantenere valido il Markdown.

`maxChars` è limitato a `textChunkLimit` del canale, quindi non puoi superare i limiti per canale.

## Coalescenza (unione dei blocchi in streaming)

Quando lo streaming a blocchi è abilitato, OpenClaw può **unire chunk di blocchi consecutivi**
prima di inviarli. Questo riduce lo “spam di righe singole” pur fornendo
un output progressivo.

- La coalescenza attende **intervalli di inattività** (`idleMs`) prima di svuotare.
- I buffer sono limitati da `maxChars` e verranno svuotati se li superano.
- `minChars` impedisce l'invio di frammenti minuscoli finché non si accumula abbastanza testo
  (lo svuotamento finale invia sempre il testo rimanente).
- Il separatore deriva da `blockStreamingChunk.breakPreference`
  (`paragraph` → `\n\n`, `newline` → `\n`, `sentence` → spazio).
- Sono disponibili override del canale tramite `*.blockStreamingCoalesce` (incluse le configurazioni per account).
- Il valore predefinito di coalescenza `minChars` viene aumentato a 1500 per Signal/Slack/Discord, salvo override.

## Cadenza umana tra i blocchi

Quando lo streaming a blocchi è abilitato, puoi aggiungere una **pausa casuale** tra
le risposte a blocchi (dopo il primo blocco). Questo rende le risposte con più bolle
più naturali.

- Configurazione: `agents.defaults.humanDelay` (override per agente tramite `agents.list[].humanDelay`).
- Modalità: `off` (predefinita), `natural` (800–2500ms), `custom` (`minMs`/`maxMs`).
- Si applica solo alle **risposte a blocchi**, non alle risposte finali o ai riepiloghi degli strumenti.

## "Trasmettere i chunk o tutto"

Questo corrisponde a:

- **Trasmettere i chunk:** `blockStreamingDefault: "on"` + `blockStreamingBreak: "text_end"` (emette man mano). I canali diversi da Telegram richiedono anche `*.blockStreaming: true`.
- **Trasmettere tutto alla fine:** `blockStreamingBreak: "message_end"` (svuota una volta, possibilmente in più chunk se molto lungo).
- **Nessuno streaming a blocchi:** `blockStreamingDefault: "off"` (solo risposta finale).

**Nota sul canale:** lo streaming a blocchi è **disattivato a meno che**
`*.blockStreaming` non sia impostato esplicitamente su `true`. I canali possono trasmettere un'anteprima live
(`channels.<channel>.streaming`) senza risposte a blocchi.

Promemoria sulla posizione della configurazione: i valori predefiniti `blockStreaming*` si trovano sotto
`agents.defaults`, non nella configurazione root.

## Modalità di streaming di anteprima

Chiave canonica: `channels.<channel>.streaming`

Modalità:

- `off`: disabilita lo streaming di anteprima.
- `partial`: una singola anteprima che viene sostituita con il testo più recente.
- `block`: l'anteprima viene aggiornata in passaggi a chunk/in append.
- `progress`: anteprima di avanzamento/stato durante la generazione, risposta finale al completamento.

### Mappatura dei canali

| Canale   | `off` | `partial` | `block` | `progress`         |
| -------- | ----- | --------- | ------- | ------------------ |
| Telegram | ✅    | ✅        | ✅      | mappa a `partial`  |
| Discord  | ✅    | ✅        | ✅      | mappa a `partial`  |
| Slack    | ✅    | ✅        | ✅      | ✅                 |

Solo Slack:

- `channels.slack.streaming.nativeTransport` abilita/disabilita le chiamate API di streaming native di Slack quando `channels.slack.streaming.mode="partial"` (predefinito: `true`).
- Lo streaming nativo di Slack e lo stato del thread assistant di Slack richiedono una destinazione in thread di risposta; i DM di primo livello non mostrano quell'anteprima in stile thread.

Migrazione delle chiavi legacy:

- Telegram: `streamMode` + booleano `streaming` vengono migrati automaticamente all'enum `streaming`.
- Discord: `streamMode` + booleano `streaming` vengono migrati automaticamente all'enum `streaming`.
- Slack: `streamMode` viene migrato automaticamente a `streaming.mode`; il booleano `streaming` viene migrato automaticamente a `streaming.mode` più `streaming.nativeTransport`; il legacy `nativeStreaming` viene migrato automaticamente a `streaming.nativeTransport`.

### Comportamento in runtime

Telegram:

- Usa aggiornamenti di anteprima `sendMessage` + `editMessageText` in DM e gruppi/topic.
- Lo streaming di anteprima viene saltato quando lo streaming a blocchi di Telegram è esplicitamente abilitato (per evitare il doppio streaming).
- `/reasoning stream` può scrivere il ragionamento nell'anteprima.

Discord:

- Usa messaggi di anteprima con invio + modifica.
- La modalità `block` usa il chunking delle bozze (`draftChunk`).
- Lo streaming di anteprima viene saltato quando lo streaming a blocchi di Discord è esplicitamente abilitato.

Slack:

- `partial` può usare lo streaming nativo di Slack (`chat.startStream`/`append`/`stop`) quando disponibile.
- `block` usa anteprime bozza in stile append.
- `progress` usa il testo di anteprima dello stato, poi la risposta finale.

## Correlati

- [Messaggi](/it/concepts/messages) — ciclo di vita e consegna dei messaggi
- [Retry](/it/concepts/retry) — comportamento di retry in caso di errore di consegna
- [Canali](/it/channels) — supporto dello streaming per canale
