---
read_when:
    - Implementazione o aggiornamento dei client WS del Gateway
    - Debug di incongruenze del protocollo o errori di connessione
    - Rigenerazione dello schema/dei modelli del protocollo
summary: 'Protocollo WebSocket del Gateway: handshake, frame, controllo delle versioni'
title: Protocollo Gateway
x-i18n:
    generated_at: "2026-04-17T08:17:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4f0eebcfdd8c926c90b4753a6d96c59e3134ddb91740f65478f11eb75be85e41
    source_path: gateway/protocol.md
    workflow: 15
---

# Protocollo Gateway (WebSocket)

Il protocollo WS del Gateway è il **singolo piano di controllo + trasporto dei node** per
OpenClaw. Tutti i client (CLI, interfaccia web, app macOS, node iOS/Android, node
headless) si connettono tramite WebSocket e dichiarano il proprio **ruolo** + **ambito**
al momento dell'handshake.

## Trasporto

- WebSocket, frame di testo con payload JSON.
- Il primo frame **deve** essere una richiesta `connect`.

## Handshake (connect)

Gateway → Client (challenge di pre-connessione):

```json
{
  "type": "event",
  "event": "connect.challenge",
  "payload": { "nonce": "…", "ts": 1737264000000 }
}
```

Client → Gateway:

```json
{
  "type": "req",
  "id": "…",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "cli",
      "version": "1.2.3",
      "platform": "macos",
      "mode": "operator"
    },
    "role": "operator",
    "scopes": ["operator.read", "operator.write"],
    "caps": [],
    "commands": [],
    "permissions": {},
    "auth": { "token": "…" },
    "locale": "en-US",
    "userAgent": "openclaw-cli/1.2.3",
    "device": {
      "id": "device_fingerprint",
      "publicKey": "…",
      "signature": "…",
      "signedAt": 1737264000000,
      "nonce": "…"
    }
  }
}
```

Gateway → Client:

```json
{
  "type": "res",
  "id": "…",
  "ok": true,
  "payload": {
    "type": "hello-ok",
    "protocol": 3,
    "server": { "version": "…", "connId": "…" },
    "features": { "methods": ["…"], "events": ["…"] },
    "snapshot": { "…": "…" },
    "policy": {
      "maxPayload": 26214400,
      "maxBufferedBytes": 52428800,
      "tickIntervalMs": 15000
    }
  }
}
```

`server`, `features`, `snapshot` e `policy` sono tutti obbligatori nello schema
(`src/gateway/protocol/schema/frames.ts`). `canvasHostUrl` è facoltativo. `auth`
riporta il ruolo/gli scope negoziati quando disponibili e include `deviceToken`
quando il gateway ne emette uno.

Quando non viene emesso alcun token del dispositivo, `hello-ok.auth` può comunque riportare i
permessi negoziati:

```json
{
  "auth": {
    "role": "operator",
    "scopes": ["operator.read", "operator.write"]
  }
}
```

Quando viene emesso un token del dispositivo, `hello-ok` include anche:

```json
{
  "auth": {
    "deviceToken": "…",
    "role": "operator",
    "scopes": ["operator.read", "operator.write"]
  }
}
```

Durante il passaggio di consegne del bootstrap attendibile, `hello-ok.auth` può includere anche
voci di ruolo aggiuntive con ambito limitato in `deviceTokens`:

```json
{
  "auth": {
    "deviceToken": "…",
    "role": "node",
    "scopes": [],
    "deviceTokens": [
      {
        "deviceToken": "…",
        "role": "operator",
        "scopes": ["operator.approvals", "operator.read", "operator.talk.secrets", "operator.write"]
      }
    ]
  }
}
```

Per il flusso di bootstrap integrato node/operator, il token principale del node rimane
`scopes: []` e qualsiasi token operator passato rimane limitato alla allowlist
dell'operator di bootstrap (`operator.approvals`, `operator.read`,
`operator.talk.secrets`, `operator.write`). I controlli degli scope di bootstrap restano
con prefisso del ruolo: le voci operator soddisfano solo le richieste operator e i ruoli non operator
continuano a richiedere scope sotto il prefisso del proprio ruolo.

### Esempio di node

```json
{
  "type": "req",
  "id": "…",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "ios-node",
      "version": "1.2.3",
      "platform": "ios",
      "mode": "node"
    },
    "role": "node",
    "scopes": [],
    "caps": ["camera", "canvas", "screen", "location", "voice"],
    "commands": ["camera.snap", "canvas.navigate", "screen.record", "location.get"],
    "permissions": { "camera.capture": true, "screen.record": false },
    "auth": { "token": "…" },
    "locale": "en-US",
    "userAgent": "openclaw-ios/1.2.3",
    "device": {
      "id": "device_fingerprint",
      "publicKey": "…",
      "signature": "…",
      "signedAt": 1737264000000,
      "nonce": "…"
    }
  }
}
```

## Framing

- **Request**: `{type:"req", id, method, params}`
- **Response**: `{type:"res", id, ok, payload|error}`
- **Event**: `{type:"event", event, payload, seq?, stateVersion?}`

I metodi con effetti collaterali richiedono **chiavi di idempotenza** (vedere lo schema).

## Ruoli + scope

### Ruoli

- `operator` = client del piano di controllo (CLI/UI/automazione).
- `node` = host delle capacità (`camera`/`screen`/`canvas`/`system.run`).

### Scope (operator)

Scope comuni:

- `operator.read`
- `operator.write`
- `operator.admin`
- `operator.approvals`
- `operator.pairing`
- `operator.talk.secrets`

`talk.config` con `includeSecrets: true` richiede `operator.talk.secrets`
(o `operator.admin`).

I metodi RPC del Gateway registrati dai Plugin possono richiedere un proprio scope operator, ma
i prefissi admin core riservati (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`) vengono sempre risolti come `operator.admin`.

Lo scope del metodo è solo il primo controllo. Alcuni comandi slash raggiunti tramite
`chat.send` applicano controlli a livello di comando più restrittivi in aggiunta. Per esempio, le scritture
persistenti `/config set` e `/config unset` richiedono `operator.admin`.

Anche `node.pair.approve` ha un controllo degli scope aggiuntivo al momento dell'approvazione oltre allo
scope di base del metodo:

- richieste senza comando: `operator.pairing`
- richieste con comandi node non exec: `operator.pairing` + `operator.write`
- richieste che includono `system.run`, `system.run.prepare` o `system.which`:
  `operator.pairing` + `operator.admin`

### Caps/commands/permissions (node)

I node dichiarano le proprie capacità al momento della connessione:

- `caps`: categorie di capacità di alto livello.
- `commands`: allowlist dei comandi per invoke.
- `permissions`: toggle granulari (ad esempio `screen.record`, `camera.capture`).

Il Gateway le tratta come **dichiarazioni** e applica allowlist lato server.

## Presenza

- `system-presence` restituisce voci indicate in base all'identità del dispositivo.
- Le voci di presenza includono `deviceId`, `roles` e `scopes` così le UI possono mostrare una singola riga per dispositivo
  anche quando questo si connette sia come **operator** sia come **node**.

## Famiglie comuni di metodi RPC

Questa pagina non è un dump completo generato, ma la superficie WS pubblica è più ampia
dei soli esempi di handshake/auth sopra. Queste sono le principali famiglie di metodi che il
Gateway espone oggi.

`hello-ok.features.methods` è un elenco di individuazione conservativo costruito da
`src/gateway/server-methods-list.ts` più le esportazioni dei metodi di plugin/channel caricati.
Trattalo come individuazione delle funzionalità, non come un dump generato di ogni helper richiamabile
implementato in `src/gateway/server-methods/*.ts`.

### Sistema e identità

- `health` restituisce lo snapshot dello stato del gateway memorizzato nella cache o appena verificato.
- `status` restituisce il riepilogo del gateway in stile `/status`; i campi sensibili sono
  inclusi solo per i client operator con scope admin.
- `gateway.identity.get` restituisce l'identità del dispositivo gateway usata dai flussi relay e
  pairing.
- `system-presence` restituisce lo snapshot di presenza corrente per i dispositivi
  operator/node connessi.
- `system-event` aggiunge un evento di sistema e può aggiornare/trasmettere il contesto
  di presenza.
- `last-heartbeat` restituisce l'ultimo evento Heartbeat persistito.
- `set-heartbeats` attiva o disattiva l'elaborazione Heartbeat sul gateway.

### Modelli e utilizzo

- `models.list` restituisce il catalogo dei modelli consentiti a runtime.
- `usage.status` restituisce finestre di utilizzo dei provider/riepiloghi della quota residua.
- `usage.cost` restituisce riepiloghi aggregati dei costi di utilizzo per un intervallo di date.
- `doctor.memory.status` restituisce lo stato di prontezza di memoria vettoriale / embedding per il
  workspace dell'agente predefinito attivo.
- `sessions.usage` restituisce riepiloghi di utilizzo per sessione.
- `sessions.usage.timeseries` restituisce serie temporali di utilizzo per una sessione.
- `sessions.usage.logs` restituisce le voci del log di utilizzo per una sessione.

### Canali e helper di accesso

- `channels.status` restituisce riepiloghi di stato dei canali/plugin integrati + inclusi.
- `channels.logout` disconnette un canale/account specifico nei casi in cui il canale
  supporti il logout.
- `web.login.start` avvia un flusso di accesso QR/web per il provider del canale web compatibile con QR
  attualmente in uso.
- `web.login.wait` attende il completamento di quel flusso di accesso QR/web e avvia il
  canale in caso di successo.
- `push.test` invia una notifica push APNs di test a un node iOS registrato.
- `voicewake.get` restituisce i trigger della parola di attivazione memorizzati.
- `voicewake.set` aggiorna i trigger della parola di attivazione e trasmette la modifica.

### Messaggistica e log

- `send` è l'RPC di consegna diretta in uscita per invii mirati a canale/account/thread
  al di fuori del runner di chat.
- `logs.tail` restituisce la coda del log file del gateway configurato con controlli di cursore/limite e
  byte massimi.

### Talk e TTS

- `talk.config` restituisce il payload effettivo della configurazione Talk; `includeSecrets`
  richiede `operator.talk.secrets` (o `operator.admin`).
- `talk.mode` imposta/trasmette lo stato attuale della modalità Talk per i client
  WebChat/Control UI.
- `talk.speak` sintetizza il parlato tramite il provider speech Talk attivo.
- `tts.status` restituisce lo stato di abilitazione TTS, il provider attivo, i provider di fallback
  e lo stato di configurazione del provider.
- `tts.providers` restituisce l'inventario visibile dei provider TTS.
- `tts.enable` e `tts.disable` attivano e disattivano lo stato delle preferenze TTS.
- `tts.setProvider` aggiorna il provider TTS preferito.
- `tts.convert` esegue una conversione text-to-speech una tantum.

### Secrets, config, update e wizard

- `secrets.reload` risolve nuovamente i SecretRef attivi e sostituisce lo stato dei segreti a runtime
  solo in caso di successo completo.
- `secrets.resolve` risolve le assegnazioni dei segreti destinati ai comandi per un insieme specifico di comando/destinazione.
- `config.get` restituisce lo snapshot e l'hash della configurazione corrente.
- `config.set` scrive un payload di configurazione validato.
- `config.patch` unisce un aggiornamento parziale della configurazione.
- `config.apply` valida e sostituisce il payload di configurazione completo.
- `config.schema` restituisce il payload dello schema di configurazione live usato da Control UI e
  dagli strumenti CLI: schema, `uiHints`, versione e metadati di generazione, inclusi
  metadati di schema di plugin + canale quando il runtime può caricarli. Lo schema
  include metadati dei campi `title` / `description` derivati dalle stesse etichette
  e dallo stesso testo di aiuto usati dalla UI, incluse le diramazioni di composizione annidate di oggetto, wildcard, elemento di array
  e `anyOf` / `oneOf` / `allOf` quando esiste documentazione dei campi corrispondente.
- `config.schema.lookup` restituisce un payload di ricerca con ambito al percorso per un percorso di configurazione:
  percorso normalizzato, un nodo di schema superficiale, hint corrispondente + `hintPath`, e
  riepiloghi dei figli immediati per drill-down UI/CLI.
  - I nodi di schema di ricerca mantengono la documentazione visibile all'utente e i comuni campi di validazione:
    `title`, `description`, `type`, `enum`, `const`, `format`, `pattern`,
    limiti numerici/stringa/array/oggetto e flag booleani come
    `additionalProperties`, `deprecated`, `readOnly`, `writeOnly`.
  - I riepiloghi dei figli espongono `key`, `path` normalizzato, `type`, `required`,
    `hasChildren`, oltre a `hint` / `hintPath` corrispondenti.
- `update.run` esegue il flusso di aggiornamento del gateway e pianifica un riavvio solo quando
  l'aggiornamento stesso è riuscito.
- `wizard.start`, `wizard.next`, `wizard.status` e `wizard.cancel` espongono la
  procedura guidata di onboarding tramite WS RPC.

### Principali famiglie esistenti

#### Helper per agente e workspace

- `agents.list` restituisce le voci degli agenti configurati.
- `agents.create`, `agents.update` e `agents.delete` gestiscono i record degli agenti e il wiring del
  workspace.
- `agents.files.list`, `agents.files.get` e `agents.files.set` gestiscono i file del
  workspace di bootstrap esposti per un agente.
- `agent.identity.get` restituisce l'identità effettiva dell'assistente per un agente o una
  sessione.
- `agent.wait` attende il completamento di un'esecuzione e restituisce lo snapshot terminale quando
  disponibile.

#### Controllo della sessione

- `sessions.list` restituisce l'indice corrente delle sessioni.
- `sessions.subscribe` e `sessions.unsubscribe` attivano o disattivano le sottoscrizioni agli eventi
  di modifica della sessione per il client WS corrente.
- `sessions.messages.subscribe` e `sessions.messages.unsubscribe` attivano o disattivano
  le sottoscrizioni agli eventi di trascrizione/messaggio per una sessione.
- `sessions.preview` restituisce anteprime limitate della trascrizione per chiavi di sessione
  specifiche.
- `sessions.resolve` risolve o canonizza una destinazione di sessione.
- `sessions.create` crea una nuova voce di sessione.
- `sessions.send` invia un messaggio in una sessione esistente.
- `sessions.steer` è la variante di interruzione e reindirizzamento per una sessione attiva.
- `sessions.abort` interrompe il lavoro attivo per una sessione.
- `sessions.patch` aggiorna i metadati/le sostituzioni della sessione.
- `sessions.reset`, `sessions.delete` e `sessions.compact` eseguono operazioni di
  manutenzione della sessione.
- `sessions.get` restituisce l'intera riga di sessione memorizzata.
- L'esecuzione della chat usa ancora `chat.history`, `chat.send`, `chat.abort` e
  `chat.inject`.
- `chat.history` è normalizzato per la visualizzazione per i client UI: i tag di direttiva inline vengono
  rimossi dal testo visibile, i payload XML di chiamata di strumenti in testo semplice (inclusi
  `<tool_call>...</tool_call>`, `<function_call>...</function_call>`,
  `<tool_calls>...</tool_calls>`, `<function_calls>...</function_calls>` e
  i blocchi di chiamata di strumenti troncati) e i token di controllo del modello ASCII/a larghezza piena fuoriusciti
  vengono rimossi, le righe assistant composte solo da token silenziosi come l'esatto `NO_REPLY` /
  `no_reply` vengono omesse e le righe troppo grandi possono essere sostituite con segnaposto.

#### Associazione dei dispositivi e token del dispositivo

- `device.pair.list` restituisce i dispositivi associati in attesa e approvati.
- `device.pair.approve`, `device.pair.reject` e `device.pair.remove` gestiscono
  i record di associazione dei dispositivi.
- `device.token.rotate` ruota un token di dispositivo associato entro i limiti del ruolo
  e dello scope approvati.
- `device.token.revoke` revoca un token di dispositivo associato.

#### Associazione dei node, invoke e lavoro in sospeso

- `node.pair.request`, `node.pair.list`, `node.pair.approve`,
  `node.pair.reject` e `node.pair.verify` coprono l'associazione dei node e la verifica
  del bootstrap.
- `node.list` e `node.describe` restituiscono lo stato dei node conosciuti/connessi.
- `node.rename` aggiorna l'etichetta di un node associato.
- `node.invoke` inoltra un comando a un node connesso.
- `node.invoke.result` restituisce il risultato di una richiesta invoke.
- `node.event` trasporta nel gateway gli eventi originati dal node.
- `node.canvas.capability.refresh` aggiorna i token delle capacità canvas con scope limitato.
- `node.pending.pull` e `node.pending.ack` sono le API di coda per i node connessi.
- `node.pending.enqueue` e `node.pending.drain` gestiscono il lavoro in sospeso durevole
  per i node offline/disconnessi.

#### Famiglie di approvazione

- `exec.approval.request`, `exec.approval.get`, `exec.approval.list` e
  `exec.approval.resolve` coprono le richieste di approvazione exec una tantum più
  la ricerca/riproduzione delle approvazioni in sospeso.
- `exec.approval.waitDecision` attende una decisione di approvazione exec in sospeso e restituisce
  la decisione finale (o `null` in caso di timeout).
- `exec.approvals.get` e `exec.approvals.set` gestiscono gli snapshot dei criteri di approvazione exec
  del gateway.
- `exec.approvals.node.get` e `exec.approvals.node.set` gestiscono i criteri locali di approvazione exec
  del node tramite comandi relay del node.
- `plugin.approval.request`, `plugin.approval.list`,
  `plugin.approval.waitDecision` e `plugin.approval.resolve` coprono
  i flussi di approvazione definiti dai Plugin.

#### Altre famiglie principali

- automazione:
  - `wake` pianifica un'iniezione di testo wake immediata o al prossimo Heartbeat
  - `cron.list`, `cron.status`, `cron.add`, `cron.update`, `cron.remove`,
    `cron.run`, `cron.runs`
- Skills/strumenti: `commands.list`, `skills.*`, `tools.catalog`, `tools.effective`

### Famiglie di eventi comuni

- `chat`: aggiornamenti della chat UI come `chat.inject` e altri eventi di chat
  solo di trascrizione.
- `session.message` e `session.tool`: aggiornamenti della trascrizione/del flusso di eventi per una
  sessione sottoscritta.
- `sessions.changed`: l'indice della sessione o i metadati sono cambiati.
- `presence`: aggiornamenti dello snapshot di presenza del sistema.
- `tick`: evento periodico di keepalive / verifica di attività.
- `health`: aggiornamento dello snapshot dello stato del gateway.
- `heartbeat`: aggiornamento del flusso di eventi Heartbeat.
- `cron`: evento di modifica dell'esecuzione/del job Cron.
- `shutdown`: notifica di arresto del gateway.
- `node.pair.requested` / `node.pair.resolved`: ciclo di vita dell'associazione dei node.
- `node.invoke.request`: trasmissione della richiesta invoke del node.
- `device.pair.requested` / `device.pair.resolved`: ciclo di vita del dispositivo associato.
- `voicewake.changed`: la configurazione del trigger della parola di attivazione è cambiata.
- `exec.approval.requested` / `exec.approval.resolved`: ciclo di vita
  dell'approvazione exec.
- `plugin.approval.requested` / `plugin.approval.resolved`: ciclo di vita
  dell'approvazione del Plugin.

### Metodi helper del node

- I node possono chiamare `skills.bins` per recuperare l'elenco corrente degli eseguibili delle Skills
  per i controlli di autorizzazione automatica.

### Metodi helper dell'operator

- Gli operator possono chiamare `commands.list` (`operator.read`) per recuperare l'inventario dei comandi a runtime per un
  agente.
  - `agentId` è facoltativo; omettilo per leggere il workspace dell'agente predefinito.
  - `scope` controlla quale superficie usa il `name` primario:
    - `text` restituisce il token del comando di testo primario senza la `/` iniziale
    - `native` e il percorso predefinito `both` restituiscono nomi nativi dipendenti dal provider
      quando disponibili
  - `textAliases` contiene alias slash esatti come `/model` e `/m`.
  - `nativeName` contiene il nome del comando nativo dipendente dal provider quando esiste.
  - `provider` è facoltativo e influisce solo sulla denominazione nativa più sulla disponibilità dei comandi
    nativi del Plugin.
  - `includeArgs=false` omette i metadati degli argomenti serializzati dalla risposta.
- Gli operator possono chiamare `tools.catalog` (`operator.read`) per recuperare il catalogo degli strumenti a runtime per un
  agente. La risposta include strumenti raggruppati e metadati di provenienza:
  - `source`: `core` o `plugin`
  - `pluginId`: proprietario del Plugin quando `source="plugin"`
  - `optional`: indica se uno strumento del Plugin è facoltativo
- Gli operator possono chiamare `tools.effective` (`operator.read`) per recuperare l'inventario effettivo degli strumenti a runtime
  per una sessione.
  - `sessionKey` è obbligatorio.
  - Il gateway ricava il contesto runtime attendibile dalla sessione lato server invece di accettare
    auth o contesto di consegna forniti dal chiamante.
  - La risposta ha ambito di sessione e riflette ciò che la conversazione attiva può usare in quel momento,
    inclusi gli strumenti core, dei Plugin e dei canali.
- Gli operator possono chiamare `skills.status` (`operator.read`) per recuperare l'inventario visibile delle
  Skills per un agente.
  - `agentId` è facoltativo; omettilo per leggere il workspace dell'agente predefinito.
  - La risposta include idoneità, requisiti mancanti, controlli di configurazione e
    opzioni di installazione sanificate senza esporre valori segreti grezzi.
- Gli operator possono chiamare `skills.search` e `skills.detail` (`operator.read`) per
  i metadati di individuazione di ClawHub.
- Gli operator possono chiamare `skills.install` (`operator.admin`) in due modalità:
  - Modalità ClawHub: `{ source: "clawhub", slug, version?, force? }` installa una
    cartella skill nella directory `skills/` del workspace dell'agente predefinito.
  - Modalità installer Gateway: `{ name, installId, dangerouslyForceUnsafeInstall?, timeoutMs? }`
    esegue un'azione `metadata.openclaw.install` dichiarata sull'host gateway.
- Gli operator possono chiamare `skills.update` (`operator.admin`) in due modalità:
  - La modalità ClawHub aggiorna uno slug tracciato o tutte le installazioni ClawHub tracciate nel
    workspace dell'agente predefinito.
  - La modalità config applica patch ai valori `skills.entries.<skillKey>` come `enabled`,
    `apiKey` ed `env`.

## Approvazioni exec

- Quando una richiesta exec necessita di approvazione, il gateway trasmette `exec.approval.requested`.
- I client operator risolvono chiamando `exec.approval.resolve` (richiede lo scope `operator.approvals`).
- Per `host=node`, `exec.approval.request` deve includere `systemRunPlan` (`argv`/`cwd`/`rawCommand`/metadati di sessione canonici). Le richieste senza `systemRunPlan` vengono rifiutate.
- Dopo l'approvazione, le chiamate inoltrate `node.invoke system.run` riutilizzano quel
  `systemRunPlan` canonico come contesto autorevole per comando/cwd/sessione.
- Se un chiamante modifica `command`, `rawCommand`, `cwd`, `agentId` o
  `sessionKey` tra prepare e l'inoltro finale approvato di `system.run`, il
  gateway rifiuta l'esecuzione invece di fidarsi del payload modificato.

## Fallback di consegna dell'agente

- Le richieste `agent` possono includere `deliver=true` per richiedere la consegna in uscita.
- `bestEffortDeliver=false` mantiene il comportamento rigoroso: le destinazioni di consegna irrisolte o solo interne restituiscono `INVALID_REQUEST`.
- `bestEffortDeliver=true` consente il fallback all'esecuzione solo di sessione quando non è possibile risolvere alcun percorso esterno recapitabile (per esempio sessioni interne/webchat o configurazioni multicanale ambigue).

## Controllo delle versioni

- `PROTOCOL_VERSION` si trova in `src/gateway/protocol/schema/protocol-schemas.ts`.
- I client inviano `minProtocol` + `maxProtocol`; il server rifiuta le incongruenze.
- Schemi + modelli sono generati da definizioni TypeBox:
  - `pnpm protocol:gen`
  - `pnpm protocol:gen:swift`
  - `pnpm protocol:check`

### Costanti del client

Il client di riferimento in `src/gateway/client.ts` usa questi valori predefiniti. I valori sono
stabili in tutto il protocollo v3 e costituiscono la baseline attesa per i client di terze parti.

| Constant                                  | Default                                               | Source                                                     |
| ----------------------------------------- | ----------------------------------------------------- | ---------------------------------------------------------- |
| `PROTOCOL_VERSION`                        | `3`                                                   | `src/gateway/protocol/schema/protocol-schemas.ts`          |
| Timeout della richiesta (per RPC)         | `30_000` ms                                           | `src/gateway/client.ts` (`requestTimeoutMs`)               |
| Timeout preauth / connect-challenge       | `10_000` ms                                           | `src/gateway/handshake-timeouts.ts` (clamp `250`–`10_000`) |
| Backoff iniziale di riconnessione         | `1_000` ms                                            | `src/gateway/client.ts` (`backoffMs`)                      |
| Backoff massimo di riconnessione          | `30_000` ms                                           | `src/gateway/client.ts` (`scheduleReconnect`)              |
| Clamp di retry rapido dopo chiusura del token del dispositivo | `250` ms                                 | `src/gateway/client.ts`                                    |
| Grace force-stop prima di `terminate()`   | `250` ms                                              | `FORCE_STOP_TERMINATE_GRACE_MS`                            |
| Timeout predefinito di `stopAndWait()`    | `1_000` ms                                            | `STOP_AND_WAIT_TIMEOUT_MS`                                 |
| Intervallo tick predefinito (prima di `hello-ok`) | `30_000` ms                                    | `src/gateway/client.ts`                                    |
| Chiusura per timeout del tick             | codice `4000` quando il silenzio supera `tickIntervalMs * 2` | `src/gateway/client.ts`                            |
| `MAX_PAYLOAD_BYTES`                       | `25 * 1024 * 1024` (25 MB)                            | `src/gateway/server-constants.ts`                          |

Il server pubblicizza i valori effettivi `policy.tickIntervalMs`, `policy.maxPayload`
e `policy.maxBufferedBytes` in `hello-ok`; i client dovrebbero rispettare tali valori
piuttosto che i valori predefiniti pre-handshake.

## Auth

- L'autenticazione del gateway con segreto condiviso usa `connect.params.auth.token` oppure
  `connect.params.auth.password`, a seconda della modalità auth configurata.
- Le modalità che portano identità, come Tailscale Serve
  (`gateway.auth.allowTailscale: true`) o `gateway.auth.mode: "trusted-proxy"`
  non-loopback, soddisfano il controllo auth di connect a partire dalle
  intestazioni della richiesta invece che da `connect.params.auth.*`.
- L'ingresso privato con `gateway.auth.mode: "none"` salta completamente l'auth connect con segreto condiviso;
  non esporre quella modalità su ingressi pubblici/non attendibili.
- Dopo l'associazione, il Gateway emette un **token del dispositivo** con scope limitato al ruolo + agli scope
  della connessione. Viene restituito in `hello-ok.auth.deviceToken` e dovrebbe essere
  persistito dal client per connessioni future.
- I client dovrebbero persistere il `hello-ok.auth.deviceToken` primario dopo ogni
  connessione riuscita.
- Anche la riconnessione con quel token del dispositivo **memorizzato** dovrebbe riutilizzare l'insieme di scope approvati memorizzato per quel token. Questo preserva l'accesso
  già concesso per lettura/verifica/stato ed evita che le riconnessioni si riducano silenziosamente a un
  scope implicito solo admin più ristretto.
- Assemblaggio auth connect lato client (`selectConnectAuth` in
  `src/gateway/client.ts`):
  - `auth.password` è ortogonale e viene sempre inoltrato quando impostato.
  - `auth.token` viene popolato in ordine di priorità: prima un token condiviso esplicito,
    poi un `deviceToken` esplicito, quindi un token per dispositivo memorizzato (indicato da
    `deviceId` + `role`).
  - `auth.bootstrapToken` viene inviato solo quando nessuna delle opzioni sopra ha risolto un
    `auth.token`. Un token condiviso o qualsiasi token del dispositivo risolto lo sopprime.
  - L'auto-promozione di un token del dispositivo memorizzato nel retry one-shot
    `AUTH_TOKEN_MISMATCH` è limitata ai soli **endpoint attendibili** —
    loopback oppure `wss://` con `tlsFingerprint` fissata. `wss://` pubblico
    senza pinning non è idoneo.
- Le voci aggiuntive `hello-ok.auth.deviceTokens` sono token di handoff bootstrap.
  Persistile solo quando la connessione ha usato auth bootstrap su un trasporto attendibile
  come `wss://` o pairing loopback/local.
- Se un client fornisce un **deviceToken** esplicito o `scopes` espliciti, quell'insieme di scope richiesto dal chiamante
  resta autorevole; gli scope in cache vengono riutilizzati solo quando il client sta riutilizzando il token per dispositivo memorizzato.
- I token del dispositivo possono essere ruotati/revocati tramite `device.token.rotate` e
  `device.token.revoke` (richiede lo scope `operator.pairing`).
- L'emissione/rotazione del token rimane limitata all'insieme di ruoli approvati registrato nella
  voce di associazione di quel dispositivo; ruotare un token non può estendere il dispositivo in un
  ruolo che l'approvazione del pairing non ha mai concesso.
- Per le sessioni con token del dispositivo associato, la gestione del dispositivo ha scope limitato al chiamante a meno che il
  chiamante non abbia anche `operator.admin`: i chiamanti non admin possono rimuovere/revocare/ruotare
  solo la **propria** voce di dispositivo.
- `device.token.rotate` controlla anche l'insieme di scope operator richiesto rispetto agli
  scope della sessione corrente del chiamante. I chiamanti non admin non possono ruotare un token verso
  un insieme di scope operator più ampio di quello che già possiedono.
- Gli errori di autenticazione includono `error.details.code` più suggerimenti per il recupero:
  - `error.details.canRetryWithDeviceToken` (boolean)
  - `error.details.recommendedNextStep` (`retry_with_device_token`, `update_auth_configuration`, `update_auth_credentials`, `wait_then_retry`, `review_auth_configuration`)
- Comportamento del client per `AUTH_TOKEN_MISMATCH`:
  - I client attendibili possono tentare un retry limitato con un token per dispositivo in cache.
  - Se quel retry fallisce, i client dovrebbero interrompere i loop di riconnessione automatica e mostrare indicazioni per l'intervento dell'operatore.

## Identità del dispositivo + pairing

- I node dovrebbero includere un'identità del dispositivo stabile (`device.id`) derivata da un
  fingerprint della coppia di chiavi.
- I gateway emettono token per dispositivo + ruolo.
- Le approvazioni di pairing sono richieste per nuovi ID dispositivo a meno che non sia abilitata
  l'auto-approvazione locale.
- L'auto-approvazione del pairing è centrata sulle connessioni loopback locali dirette.
- OpenClaw ha anche un percorso ristretto di self-connect backend/container-local per
  flussi helper attendibili con segreto condiviso.
- Le connessioni tailnet o LAN sullo stesso host sono comunque trattate come remote per il pairing e
  richiedono approvazione.
- Tutti i client WS devono includere l'identità `device` durante `connect` (operator + node).
  Control UI può ometterla solo in queste modalità:
  - `gateway.controlUi.allowInsecureAuth=true` per compatibilità con HTTP non sicuro solo localhost.
  - autenticazione operator Control UI riuscita con `gateway.auth.mode: "trusted-proxy"`.
  - `gateway.controlUi.dangerouslyDisableDeviceAuth=true` (modalità break-glass, grave riduzione della sicurezza).
- Tutte le connessioni devono firmare il nonce `connect.challenge` fornito dal server.

### Diagnostica di migrazione auth del dispositivo

Per i client legacy che usano ancora il comportamento di firma pre-challenge, `connect` ora restituisce
codici di dettaglio `DEVICE_AUTH_*` in `error.details.code` con un valore stabile di `error.details.reason`.

Errori di migrazione comuni:

| Message                     | details.code                     | details.reason           | Meaning                                            |
| --------------------------- | -------------------------------- | ------------------------ | -------------------------------------------------- |
| `device nonce required`     | `DEVICE_AUTH_NONCE_REQUIRED`     | `device-nonce-missing`   | Il client ha omesso `device.nonce` (o l'ha inviato vuoto). |
| `device nonce mismatch`     | `DEVICE_AUTH_NONCE_MISMATCH`     | `device-nonce-mismatch`  | Il client ha firmato con un nonce obsoleto/errato. |
| `device signature invalid`  | `DEVICE_AUTH_SIGNATURE_INVALID`  | `device-signature`       | Il payload della firma non corrisponde al payload v2. |
| `device signature expired`  | `DEVICE_AUTH_SIGNATURE_EXPIRED`  | `device-signature-stale` | Il timestamp firmato è fuori dallo skew consentito. |
| `device identity mismatch`  | `DEVICE_AUTH_DEVICE_ID_MISMATCH` | `device-id-mismatch`     | `device.id` non corrisponde al fingerprint della chiave pubblica. |
| `device public key invalid` | `DEVICE_AUTH_PUBLIC_KEY_INVALID` | `device-public-key`      | Il formato/canonicalizzazione della chiave pubblica non è riuscito. |

Obiettivo della migrazione:

- Attendere sempre `connect.challenge`.
- Firmare il payload v2 che include il nonce del server.
- Inviare lo stesso nonce in `connect.params.device.nonce`.
- Il payload di firma preferito è `v3`, che vincola `platform` e `deviceFamily`
  oltre ai campi device/client/role/scopes/token/nonce.
- Le firme legacy `v2` restano accettate per compatibilità, ma il pinning dei metadati
  del dispositivo associato continua a controllare la policy dei comandi alla riconnessione.

## TLS + pinning

- TLS è supportato per le connessioni WS.
- I client possono facoltativamente fissare il fingerprint del certificato del gateway (vedere la configurazione `gateway.tls`
  più `gateway.remote.tlsFingerprint` o il flag CLI `--tls-fingerprint`).

## Ambito

Questo protocollo espone l'**API completa del gateway** (status, canali, modelli, chat,
agent, sessioni, node, approvazioni, ecc.). La superficie esatta è definita dagli
schemi TypeBox in `src/gateway/protocol/schema.ts`.
