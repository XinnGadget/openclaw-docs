---
read_when:
    - Hai bisogno di eseguire il debug degli ID sessione, del JSONL della trascrizione o dei campi di sessions.json
    - Stai modificando il comportamento della compattazione automatica o aggiungendo operazioni preliminari di pulizia prima della compattazione
    - Vuoi implementare flush della memoria o turni di sistema silenziosi
summary: 'Approfondimento: store delle sessioni + trascrizioni, ciclo di vita e componenti interni della compattazione (automatica)'
title: Approfondimento sulla gestione delle sessioni
x-i18n:
    generated_at: "2026-04-08T02:18:36Z"
    model: gpt-5.4
    provider: openai
    source_hash: cb1a4048646486693db8943a9e9c6c5bcb205f0ed532b34842de3d0346077454
    source_path: reference/session-management-compaction.md
    workflow: 15
---

# Gestione delle sessioni e compattazione (approfondimento)

Questo documento spiega come OpenClaw gestisce le sessioni end-to-end:

- **Instradamento delle sessioni** (come i messaggi in ingresso vengono mappati a una `sessionKey`)
- **Store delle sessioni** (`sessions.json`) e cosa tiene traccia
- **Persistenza delle trascrizioni** (`*.jsonl`) e la loro struttura
- **Igiene delle trascrizioni** (correzioni specifiche del provider prima delle esecuzioni)
- **Limiti del contesto** (finestra di contesto rispetto ai token tracciati)
- **Compattazione** (compattazione manuale + automatica) e dove collegare il lavoro preliminare prima della compattazione
- **Pulizia silenziosa** (ad esempio scritture in memoria che non dovrebbero produrre output visibile all'utente)

Se vuoi prima una panoramica di livello superiore, inizia da:

- [/concepts/session](/it/concepts/session)
- [/concepts/compaction](/it/concepts/compaction)
- [/concepts/memory](/it/concepts/memory)
- [/concepts/memory-search](/it/concepts/memory-search)
- [/concepts/session-pruning](/it/concepts/session-pruning)
- [/reference/transcript-hygiene](/it/reference/transcript-hygiene)

---

## Fonte di verità: il Gateway

OpenClaw è progettato attorno a un singolo **processo Gateway** che possiede lo stato della sessione.

- Le UI (app macOS, web Control UI, TUI) dovrebbero interrogare il Gateway per gli elenchi delle sessioni e il conteggio dei token.
- In modalità remota, i file di sessione si trovano sull'host remoto; “controllare i file sul tuo Mac locale” non rifletterà ciò che il Gateway sta usando.

---

## Due livelli di persistenza

OpenClaw rende persistenti le sessioni su due livelli:

1. **Store delle sessioni (`sessions.json`)**
   - Mappa chiave/valore: `sessionKey -> SessionEntry`
   - Piccolo, mutabile, sicuro da modificare (o da cui eliminare voci)
   - Tiene traccia dei metadati della sessione (ID sessione corrente, ultima attività, interruttori, contatori di token, ecc.)

2. **Trascrizione (`<sessionId>.jsonl`)**
   - Trascrizione append-only con struttura ad albero (le voci hanno `id` + `parentId`)
   - Memorizza la conversazione effettiva + chiamate agli strumenti + riepiloghi di compattazione
   - Usata per ricostruire il contesto del modello per i turni futuri

---

## Posizioni su disco

Per agent, sull'host Gateway:

- Store: `~/.openclaw/agents/<agentId>/sessions/sessions.json`
- Trascrizioni: `~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl`
  - Sessioni dei topic Telegram: `.../<sessionId>-topic-<threadId>.jsonl`

OpenClaw le risolve tramite `src/config/sessions.ts`.

---

## Manutenzione dello store e controlli su disco

La persistenza delle sessioni ha controlli automatici di manutenzione (`session.maintenance`) per `sessions.json` e gli artefatti delle trascrizioni:

- `mode`: `warn` (predefinito) oppure `enforce`
- `pruneAfter`: soglia di età delle voci obsolete (predefinita `30d`)
- `maxEntries`: limite massimo di voci in `sessions.json` (predefinito `500`)
- `rotateBytes`: ruota `sessions.json` quando è troppo grande (predefinito `10mb`)
- `resetArchiveRetention`: retention per gli archivi delle trascrizioni `*.reset.<timestamp>` (predefinita: uguale a `pruneAfter`; `false` disabilita la pulizia)
- `maxDiskBytes`: budget facoltativo per la directory delle sessioni
- `highWaterBytes`: obiettivo facoltativo dopo la pulizia (predefinito `80%` di `maxDiskBytes`)

Ordine di applicazione per la pulizia del budget disco (`mode: "enforce"`):

1. Rimuove prima gli artefatti delle trascrizioni archiviati o orfani più vecchi.
2. Se ancora sopra l'obiettivo, sfratta le voci di sessione più vecchie e i relativi file di trascrizione.
3. Continua finché l'utilizzo non è pari o inferiore a `highWaterBytes`.

In `mode: "warn"`, OpenClaw segnala le possibili espulsioni ma non modifica store/file.

Esegui la manutenzione su richiesta:

```bash
openclaw sessions cleanup --dry-run
openclaw sessions cleanup --enforce
```

---

## Sessioni cron e log delle esecuzioni

Anche le esecuzioni cron isolate creano voci/trascrizioni di sessione e hanno controlli di retention dedicati:

- `cron.sessionRetention` (predefinito `24h`) elimina dallo store delle sessioni le vecchie sessioni isolate delle esecuzioni cron (`false` disabilita).
- `cron.runLog.maxBytes` + `cron.runLog.keepLines` eliminano i file `~/.openclaw/cron/runs/<jobId>.jsonl` (predefiniti: `2_000_000` byte e `2000` righe).

---

## Chiavi di sessione (`sessionKey`)

Una `sessionKey` identifica _in quale contenitore di conversazione_ ti trovi (instradamento + isolamento).

Pattern comuni:

- Chat principale/diretta (per agent): `agent:<agentId>:<mainKey>` (predefinito `main`)
- Gruppo: `agent:<agentId>:<channel>:group:<id>`
- Stanza/canale (Discord/Slack): `agent:<agentId>:<channel>:channel:<id>` oppure `...:room:<id>`
- Cron: `cron:<job.id>`
- Webhook: `hook:<uuid>` (salvo override)

Le regole canoniche sono documentate in [/concepts/session](/it/concepts/session).

---

## ID sessione (`sessionId`)

Ogni `sessionKey` punta a un `sessionId` corrente (il file di trascrizione che continua la conversazione).

Regole pratiche:

- **Reset** (`/new`, `/reset`) crea un nuovo `sessionId` per quella `sessionKey`.
- **Reset giornaliero** (predefinito alle 4:00 ora locale sull'host Gateway) crea un nuovo `sessionId` al messaggio successivo dopo il confine di reset.
- **Scadenza per inattività** (`session.reset.idleMinutes` o legacy `session.idleMinutes`) crea un nuovo `sessionId` quando arriva un messaggio dopo la finestra di inattività. Quando sono configurati sia giornaliero sia inattività, prevale quello che scade per primo.
- **Protezione fork del genitore del thread** (`session.parentForkMaxTokens`, predefinito `100000`) salta il fork della trascrizione genitore quando la sessione genitore è già troppo grande; il nuovo thread inizia da zero. Imposta `0` per disabilitare.

Dettaglio di implementazione: la decisione avviene in `initSessionState()` in `src/auto-reply/reply/session.ts`.

---

## Schema dello store delle sessioni (`sessions.json`)

Il tipo di valore dello store è `SessionEntry` in `src/config/sessions.ts`.

Campi principali (non esaustivi):

- `sessionId`: ID della trascrizione corrente (il nome file deriva da questo salvo che sia impostato `sessionFile`)
- `updatedAt`: timestamp dell'ultima attività
- `sessionFile`: override facoltativo del percorso esplicito della trascrizione
- `chatType`: `direct | group | room` (aiuta le UI e la policy di invio)
- `provider`, `subject`, `room`, `space`, `displayName`: metadati per etichettatura di gruppi/canali
- Interruttori:
  - `thinkingLevel`, `verboseLevel`, `reasoningLevel`, `elevatedLevel`
  - `sendPolicy` (override per sessione)
- Selezione del modello:
  - `providerOverride`, `modelOverride`, `authProfileOverride`
- Contatori di token (best-effort / dipendenti dal provider):
  - `inputTokens`, `outputTokens`, `totalTokens`, `contextTokens`
- `compactionCount`: quante volte la compattazione automatica è stata completata per questa chiave di sessione
- `memoryFlushAt`: timestamp dell'ultimo flush della memoria prima della compattazione
- `memoryFlushCompactionCount`: conteggio di compattazione al momento dell'ultimo flush

Lo store è sicuro da modificare, ma il Gateway è l'autorità: può riscrivere o reidratare le voci mentre le sessioni sono in esecuzione.

---

## Struttura della trascrizione (`*.jsonl`)

Le trascrizioni sono gestite dal `SessionManager` di `@mariozechner/pi-coding-agent`.

Il file è JSONL:

- Prima riga: intestazione della sessione (`type: "session"`, include `id`, `cwd`, `timestamp`, `parentSession` facoltativo)
- Poi: voci di sessione con `id` + `parentId` (albero)

Tipi di voce rilevanti:

- `message`: messaggi utente/assistente/toolResult
- `custom_message`: messaggi iniettati dall'estensione che _entrano_ nel contesto del modello (possono essere nascosti nella UI)
- `custom`: stato dell'estensione che _non_ entra nel contesto del modello
- `compaction`: riepilogo di compattazione persistito con `firstKeptEntryId` e `tokensBefore`
- `branch_summary`: riepilogo persistito durante la navigazione in un ramo dell'albero

OpenClaw intenzionalmente **non** “corregge” le trascrizioni; il Gateway usa `SessionManager` per leggerle/scriverle.

---

## Finestre di contesto rispetto ai token tracciati

Contano due concetti diversi:

1. **Finestra di contesto del modello**: limite rigido per modello (token visibili al modello)
2. **Contatori dello store delle sessioni**: statistiche progressive scritte in `sessions.json` (usate per /status e dashboard)

Se stai regolando i limiti:

- La finestra di contesto proviene dal catalogo dei modelli (e può essere sovrascritta tramite configurazione).
- `contextTokens` nello store è un valore di stima/reporting a runtime; non trattarlo come una garanzia rigorosa.

Per saperne di più, vedi [/token-use](/it/reference/token-use).

---

## Compattazione: cos'è

La compattazione riassume la conversazione più vecchia in una voce `compaction` persistita nella trascrizione e mantiene intatti i messaggi recenti.

Dopo la compattazione, i turni futuri vedono:

- Il riepilogo di compattazione
- I messaggi dopo `firstKeptEntryId`

La compattazione è **persistente** (a differenza del pruning della sessione). Vedi [/concepts/session-pruning](/it/concepts/session-pruning).

## Confini dei chunk di compattazione e accoppiamento con gli strumenti

Quando OpenClaw divide una lunga trascrizione in chunk di compattazione, mantiene
accoppiate le chiamate agli strumenti dell'assistente con le voci `toolResult` corrispondenti.

- Se la suddivisione in base alla quota di token cade tra una chiamata a uno strumento e il suo risultato, OpenClaw
  sposta il confine al messaggio di chiamata allo strumento dell'assistente invece di separare
  la coppia.
- Se un blocco finale di risultati degli strumenti altrimenti farebbe superare al chunk l'obiettivo,
  OpenClaw preserva quel blocco di strumenti in sospeso e mantiene intatta la coda non
  riassunta.
- I blocchi di chiamata agli strumenti interrotti/con errore non mantengono aperta una divisione in sospeso.

---

## Quando avviene la compattazione automatica (runtime Pi)

Nell'agent Pi integrato, la compattazione automatica si attiva in due casi:

1. **Recupero da overflow**: il modello restituisce un errore di overflow del contesto
   (`request_too_large`, `context length exceeded`, `input exceeds the maximum
number of tokens`, `input token count exceeds the maximum number of input
tokens`, `input is too long for the model`, `ollama error: context length
exceeded` e varianti simili modellate dal provider) → compatta → ritenta.
2. **Manutenzione della soglia**: dopo un turno riuscito, quando:

`contextTokens > contextWindow - reserveTokens`

Dove:

- `contextWindow` è la finestra di contesto del modello
- `reserveTokens` è il margine riservato per prompt + output del modello successivo

Queste sono semantiche del runtime Pi (OpenClaw consuma gli eventi, ma Pi decide quando compattare).

---

## Impostazioni della compattazione (`reserveTokens`, `keepRecentTokens`)

Le impostazioni di compattazione di Pi si trovano nelle impostazioni Pi:

```json5
{
  compaction: {
    enabled: true,
    reserveTokens: 16384,
    keepRecentTokens: 20000,
  },
}
```

OpenClaw applica anche una soglia minima di sicurezza per le esecuzioni integrate:

- Se `compaction.reserveTokens < reserveTokensFloor`, OpenClaw la aumenta.
- La soglia minima predefinita è `20000` token.
- Imposta `agents.defaults.compaction.reserveTokensFloor: 0` per disabilitare la soglia minima.
- Se è già più alta, OpenClaw la lascia invariata.

Perché: lasciare margine sufficiente per la “pulizia” multi-turno (come le scritture in memoria) prima che la compattazione diventi inevitabile.

Implementazione: `ensurePiCompactionReserveTokens()` in `src/agents/pi-settings.ts`
(chiamata da `src/agents/pi-embedded-runner.ts`).

---

## Provider di compattazione pluggable

I plugin possono registrare un provider di compattazione tramite `registerCompactionProvider()` sull'API del plugin. Quando `agents.defaults.compaction.provider` è impostato su un ID provider registrato, l'estensione safeguard delega il riepilogo a quel provider invece che alla pipeline integrata `summarizeInStages`.

- `provider`: ID di un plugin provider di compattazione registrato. Lascialo non impostato per il riepilogo LLM predefinito.
- Impostare un `provider` forza `mode: "safeguard"`.
- I provider ricevono le stesse istruzioni di compattazione e la stessa policy di preservazione degli identificatori del percorso integrato.
- Il safeguard preserva comunque il contesto dei turni recenti e del suffisso della suddivisione dei turni dopo l'output del provider.
- Se il provider fallisce o restituisce un risultato vuoto, OpenClaw torna automaticamente al riepilogo LLM integrato.
- I segnali di interruzione/timeout vengono rilanciati (non ignorati) per rispettare l'annullamento del chiamante.

Sorgente: `src/plugins/compaction-provider.ts`, `src/agents/pi-hooks/compaction-safeguard.ts`.

---

## Superfici visibili all'utente

Puoi osservare compattazione e stato della sessione tramite:

- `/status` (in qualsiasi sessione chat)
- `openclaw status` (CLI)
- `openclaw sessions` / `sessions --json`
- Modalità dettagliata: `🧹 Auto-compaction complete` + conteggio di compattazione

---

## Pulizia silenziosa (`NO_REPLY`)

OpenClaw supporta turni “silenziosi” per attività in background in cui l'utente non dovrebbe vedere output intermedio.

Convenzione:

- L'assistente inizia il proprio output con l'esatto token silenzioso `NO_REPLY` /
  `no_reply` per indicare “non consegnare una risposta all'utente”.
- OpenClaw lo rimuove/lo sopprime nel livello di consegna.
- La soppressione dell'esatto token silenzioso non distingue tra maiuscole e minuscole, quindi `NO_REPLY` e
  `no_reply` contano entrambi quando l'intero payload è solo il token silenzioso.
- Questo serve solo per veri turni in background/senza consegna; non è una scorciatoia per
  normali richieste utente con azioni da eseguire.

A partire da `2026.1.10`, OpenClaw sopprime anche lo **streaming draft/digitazione** quando un
chunk parziale inizia con `NO_REPLY`, così le operazioni silenziose non fanno trapelare output parziale a metà turno.

---

## "Memory flush" prima della compattazione (implementato)

Obiettivo: prima che avvenga la compattazione automatica, eseguire un turno agentico silenzioso che scriva
stato durevole su disco (ad esempio `memory/YYYY-MM-DD.md` nel workspace dell'agent) così la compattazione non possa
cancellare contesto critico.

OpenClaw usa l'approccio di **flush prima della soglia**:

1. Monitora l'utilizzo del contesto della sessione.
2. Quando supera una “soglia morbida” (al di sotto della soglia di compattazione di Pi), esegue una direttiva silenziosa
   “scrivi ora in memoria” verso l'agent.
3. Usa l'esatto token silenzioso `NO_REPLY` / `no_reply` così l'utente non vede
   nulla.

Configurazione (`agents.defaults.compaction.memoryFlush`):

- `enabled` (predefinito: `true`)
- `softThresholdTokens` (predefinito: `4000`)
- `prompt` (messaggio utente per il turno di flush)
- `systemPrompt` (prompt di sistema aggiuntivo aggiunto per il turno di flush)

Note:

- Il prompt/system prompt predefinito include un suggerimento `NO_REPLY` per sopprimere
  la consegna.
- Il flush viene eseguito una volta per ciclo di compattazione (tracciato in `sessions.json`).
- Il flush viene eseguito solo per sessioni Pi integrate (i backend CLI lo saltano).
- Il flush viene saltato quando il workspace della sessione è in sola lettura (`workspaceAccess: "ro"` o `"none"`).
- Vedi [Memory](/it/concepts/memory) per il layout dei file del workspace e i pattern di scrittura.

Pi espone anche un hook `session_before_compact` nell'API dell'estensione, ma oggi la logica di
flush di OpenClaw vive lato Gateway.

---

## Checklist di risoluzione dei problemi

- Chiave di sessione errata? Inizia da [/concepts/session](/it/concepts/session) e conferma la `sessionKey` in `/status`.
- Mancata corrispondenza tra store e trascrizione? Conferma l'host Gateway e il percorso dello store da `openclaw status`.
- Spam di compattazione? Controlla:
  - finestra di contesto del modello (troppo piccola)
  - impostazioni di compattazione (`reserveTokens` troppo alto rispetto alla finestra del modello può causare una compattazione anticipata)
  - crescita eccessiva dei risultati degli strumenti: abilita/regola il pruning della sessione
- I turni silenziosi trapelano? Conferma che la risposta inizi con `NO_REPLY` (token esatto case-insensitive) e che tu stia usando una build che include la correzione della soppressione dello streaming.
