---
read_when:
    - Implementazione o aggiornamento di client WS del gateway
    - Debug di mismatch del protocollo o errori di connessione
    - Rigenerazione di schema/modelli del protocollo
summary: 'Protocollo WebSocket del gateway: handshake, frame, versioning'
title: Protocollo del gateway
x-i18n:
    generated_at: "2026-04-08T02:15:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8635e3ac1dd311dbd3a770b088868aa1495a8d53b3ebc1eae0dfda3b2bf4694a
    source_path: gateway/protocol.md
    workflow: 15
---

# Protocollo del gateway (WebSocket)

Il protocollo WS del gateway è il **singolo control plane + trasporto dei nodi** per
OpenClaw. Tutti i client (CLI, interfaccia web, app macOS, nodi iOS/Android, nodi
headless) si connettono tramite WebSocket e dichiarano il proprio **ruolo** + **ambito** al
momento dell'handshake.

## Trasporto

- WebSocket, frame di testo con payload JSON.
- Il primo frame **deve** essere una richiesta `connect`.

## Handshake (connect)

Gateway → Client (challenge pre-connessione):

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
  "payload": { "type": "hello-ok", "protocol": 3, "policy": { "tickIntervalMs": 15000 } }
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

Durante il passaggio di bootstrap attendibile, `hello-ok.auth` può includere anche voci di ruolo aggiuntive limitate in `deviceTokens`:

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

Per il flusso di bootstrap integrato node/operator, il token primario del nodo resta
`scopes: []` e qualsiasi token operator passato resta limitato all'allowlist dell'operatore di bootstrap
(`operator.approvals`, `operator.read`,
`operator.talk.secrets`, `operator.write`). I controlli dell'ambito di bootstrap restano
con prefisso del ruolo: le voci operator soddisfano solo richieste operator, e i ruoli non-operator
continuano a richiedere ambiti sotto il proprio prefisso di ruolo.

### Esempio node

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

I metodi con effetti collaterali richiedono **chiavi di idempotenza** (vedi schema).

## Ruoli + ambiti

### Ruoli

- `operator` = client del control plane (CLI/UI/automazione).
- `node` = host di capacità (camera/screen/canvas/system.run).

### Ambiti (operator)

Ambiti comuni:

- `operator.read`
- `operator.write`
- `operator.admin`
- `operator.approvals`
- `operator.pairing`
- `operator.talk.secrets`

`talk.config` con `includeSecrets: true` richiede `operator.talk.secrets`
(o `operator.admin`).

I metodi RPC del gateway registrati dai plugin possono richiedere il proprio ambito operator, ma
i prefissi admin core riservati (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`) vengono sempre risolti in `operator.admin`.

L'ambito del metodo è solo il primo gate. Alcuni slash command raggiunti tramite
`chat.send` applicano controlli a livello di comando più restrittivi in aggiunta. Per esempio, le scritture persistenti
`/config set` e `/config unset` richiedono `operator.admin`.

`node.pair.approve` ha anche un controllo aggiuntivo dell'ambito al momento dell'approvazione oltre al
metodo base:

- richieste senza comando: `operator.pairing`
- richieste con comandi del nodo non-exec: `operator.pairing` + `operator.write`
- richieste che includono `system.run`, `system.run.prepare` o `system.which`:
  `operator.pairing` + `operator.admin`

### Caps/commands/permissions (node)

I nodi dichiarano le proprie capability claim al momento della connessione:

- `caps`: categorie di capacità di alto livello.
- `commands`: allowlist dei comandi per invoke.
- `permissions`: toggle granulari (ad esempio `screen.record`, `camera.capture`).

Il gateway tratta questi elementi come **claim** e applica allowlist lato server.

## Presence

- `system-presence` restituisce voci indicizzate per identità del dispositivo.
- Le voci di presence includono `deviceId`, `roles` e `scopes` così le UI possono mostrare una singola riga per dispositivo
  anche quando si connette sia come **operator** sia come **node**.

## Famiglie comuni di metodi RPC

Questa pagina non è un dump completo generato, ma la superficie WS pubblica è più ampia
degli esempi di handshake/auth sopra. Queste sono le principali famiglie di metodi che il
gateway espone oggi.

`hello-ok.features.methods` è un elenco conservativo di discovery costruito da
`src/gateway/server-methods-list.ts` più le esportazioni dei metodi plugin/channel caricati.
Trattalo come discovery delle funzionalità, non come un dump generato di ogni helper invocabile
implementato in `src/gateway/server-methods/*.ts`.

### Sistema e identità

- `health` restituisce lo snapshot di health del gateway memorizzato in cache o appena sondato.
- `status` restituisce il riepilogo del gateway in stile `/status`; i campi sensibili sono
  inclusi solo per client operator con ambito admin.
- `gateway.identity.get` restituisce l'identità del dispositivo gateway usata dai flussi di relay e
  pairing.
- `system-presence` restituisce lo snapshot corrente della presence per i dispositivi
  operator/node connessi.
- `system-event` aggiunge un evento di sistema e può aggiornare/trasmettere il contesto
  di presence.
- `last-heartbeat` restituisce l'ultimo evento heartbeat persistito.
- `set-heartbeats` attiva/disattiva l'elaborazione heartbeat sul gateway.

### Modelli e utilizzo

- `models.list` restituisce il catalogo dei modelli consentiti a runtime.
- `usage.status` restituisce finestre di utilizzo del provider/riepiloghi della quota residua.
- `usage.cost` restituisce riepiloghi aggregati del costo di utilizzo per un intervallo di date.
- `doctor.memory.status` restituisce lo stato di preparazione di vector-memory / embedding per il
  workspace dell'agente predefinito attivo.
- `sessions.usage` restituisce riepiloghi di utilizzo per sessione.
- `sessions.usage.timeseries` restituisce serie temporali di utilizzo per una sessione.
- `sessions.usage.logs` restituisce voci del log di utilizzo per una sessione.

### Canali e helper di login

- `channels.status` restituisce riepiloghi di stato dei canali/plugin integrati + inclusi.
- `channels.logout` disconnette uno specifico canale/account nei casi in cui il canale
  supporti il logout.
- `web.login.start` avvia un flusso di login QR/web per il provider del canale web corrente con supporto QR.
- `web.login.wait` attende il completamento di quel flusso di login QR/web e avvia il
  canale in caso di successo.
- `push.test` invia una push APNs di test a un nodo iOS registrato.
- `voicewake.get` restituisce i trigger della parola di attivazione memorizzati.
- `voicewake.set` aggiorna i trigger della parola di attivazione e trasmette la modifica.

### Messaggistica e log

- `send` è l'RPC diretto di consegna in uscita per invii indirizzati a canale/account/thread
  al di fuori del runner chat.
- `logs.tail` restituisce il tail configurato del log file del gateway con controlli di cursore/limite e
  byte massimi.

### Talk e TTS

- `talk.config` restituisce il payload di configurazione Talk effettivo; `includeSecrets`
  richiede `operator.talk.secrets` (o `operator.admin`).
- `talk.mode` imposta/trasmette lo stato corrente della modalità Talk per i client WebChat/Control UI.
- `talk.speak` sintetizza il parlato tramite il provider speech Talk attivo.
- `tts.status` restituisce stato TTS abilitato, provider attivo, provider di fallback
  e stato della configurazione del provider.
- `tts.providers` restituisce l'inventario visibile dei provider TTS.
- `tts.enable` e `tts.disable` attivano/disattivano lo stato delle preferenze TTS.
- `tts.setProvider` aggiorna il provider TTS preferito.
- `tts.convert` esegue una conversione text-to-speech one-shot.

### Secrets, config, update e wizard

- `secrets.reload` risolve nuovamente i SecretRef attivi e sostituisce lo stato runtime dei secret
  solo in caso di successo completo.
- `secrets.resolve` risolve le assegnazioni di secret destinate ai comandi per uno specifico
  insieme comando/target.
- `config.get` restituisce lo snapshot e l'hash della configurazione corrente.
- `config.set` scrive un payload di configurazione validato.
- `config.patch` unisce un aggiornamento parziale della configurazione.
- `config.apply` valida + sostituisce l'intero payload di configurazione.
- `config.schema` restituisce il payload dello schema di configurazione live usato da Control UI e
  strumenti CLI: schema, `uiHints`, versione e metadati di generazione, inclusi
  i metadati di schema di plugin + canale quando il runtime può caricarli. Lo schema
  include i metadati dei campi `title` / `description` derivati dalle stesse etichette
  e dal testo di aiuto usati dalla UI, incluse diramazioni di composizione annidate di oggetto, wildcard,
  elemento di array e `anyOf` / `oneOf` / `allOf` quando esiste documentazione
  di campo corrispondente.
- `config.schema.lookup` restituisce un payload di lookup con ambito di percorso per un percorso di configurazione:
  percorso normalizzato, nodo di schema superficiale, hint corrispondente + `hintPath`, e
  riepiloghi dei figli immediati per drill-down UI/CLI.
  - I nodi di schema di lookup mantengono la documentazione rivolta all'utente e i comuni campi di validazione:
    `title`, `description`, `type`, `enum`, `const`, `format`, `pattern`,
    limiti numerici/stringa/array/oggetto, e flag booleani come
    `additionalProperties`, `deprecated`, `readOnly`, `writeOnly`.
  - I riepiloghi dei figli espongono `key`, `path` normalizzato, `type`, `required`,
    `hasChildren`, più `hint` / `hintPath` corrispondenti.
- `update.run` esegue il flusso di aggiornamento del gateway e pianifica un riavvio solo quando
  l'aggiornamento stesso è riuscito.
- `wizard.start`, `wizard.next`, `wizard.status` e `wizard.cancel` espongono il
  wizard di onboarding tramite WS RPC.

### Principali famiglie esistenti

#### Helper di agente e workspace

- `agents.list` restituisce le voci di agente configurate.
- `agents.create`, `agents.update` e `agents.delete` gestiscono i record degli agenti e
  il wiring del workspace.
- `agents.files.list`, `agents.files.get` e `agents.files.set` gestiscono i
  file bootstrap del workspace esposti per un agente.
- `agent.identity.get` restituisce l'identità effettiva dell'assistente per un agente o
  sessione.
- `agent.wait` attende che un'esecuzione finisca e restituisce lo snapshot terminale quando
  disponibile.

#### Controllo della sessione

- `sessions.list` restituisce l'indice corrente delle sessioni.
- `sessions.subscribe` e `sessions.unsubscribe` attivano/disattivano le sottoscrizioni agli eventi di modifica della sessione
  per il client WS corrente.
- `sessions.messages.subscribe` e `sessions.messages.unsubscribe` attivano/disattivano
  le sottoscrizioni agli eventi di transcript/messaggi per una sessione.
- `sessions.preview` restituisce anteprime limitate del transcript per specifiche chiavi di sessione.
- `sessions.resolve` risolve o canonizza un target di sessione.
- `sessions.create` crea una nuova voce di sessione.
- `sessions.send` invia un messaggio in una sessione esistente.
- `sessions.steer` è la variante di interrompi-e-sterza per una sessione attiva.
- `sessions.abort` interrompe il lavoro attivo per una sessione.
- `sessions.patch` aggiorna metadati/override della sessione.
- `sessions.reset`, `sessions.delete` e `sessions.compact` eseguono manutenzione della sessione.
- `sessions.get` restituisce l'intera riga di sessione memorizzata.
- l'esecuzione della chat usa ancora `chat.history`, `chat.send`, `chat.abort` e
  `chat.inject`.
- `chat.history` è normalizzato per la visualizzazione per i client UI: i tag di direttiva inline vengono
  rimossi dal testo visibile, i payload XML di chiamata strumento in testo semplice (inclusi
  `<tool_call>...</tool_call>`, `<function_call>...</function_call>`,
  `<tool_calls>...</tool_calls>`, `<function_calls>...</function_calls>`, e
  blocchi di chiamata strumento troncati) e i token di controllo del modello ASCII/full-width trapelati
  vengono rimossi, le righe dell'assistente composte solo da token silenziosi come esatto `NO_REPLY` /
  `no_reply` vengono omesse, e le righe troppo grandi possono essere sostituite con placeholder.

#### Pairing del dispositivo e token del dispositivo

- `device.pair.list` restituisce i dispositivi associati in attesa e approvati.
- `device.pair.approve`, `device.pair.reject` e `device.pair.remove` gestiscono
  i record di pairing del dispositivo.
- `device.token.rotate` ruota un token di dispositivo associato entro i limiti di ruolo
  e ambito approvati.
- `device.token.revoke` revoca un token di dispositivo associato.

#### Pairing dei nodi, invoke e lavoro in sospeso

- `node.pair.request`, `node.pair.list`, `node.pair.approve`,
  `node.pair.reject` e `node.pair.verify` coprono il pairing dei nodi e la verifica
  del bootstrap.
- `node.list` e `node.describe` restituiscono lo stato dei nodi noti/connessi.
- `node.rename` aggiorna un'etichetta di nodo associato.
- `node.invoke` inoltra un comando a un nodo connesso.
- `node.invoke.result` restituisce il risultato di una richiesta invoke.
- `node.event` trasporta eventi originati dal nodo di nuovo nel gateway.
- `node.canvas.capability.refresh` aggiorna i token di capacità canvas con ambito.
- `node.pending.pull` e `node.pending.ack` sono le API della coda dei nodi connessi.
- `node.pending.enqueue` e `node.pending.drain` gestiscono il lavoro persistente in sospeso
  per nodi offline/disconnessi.

#### Famiglie di approvazione

- `exec.approval.request`, `exec.approval.get`, `exec.approval.list` e
  `exec.approval.resolve` coprono le richieste di approvazione exec one-shot più
  lookup/replay delle approvazioni in sospeso.
- `exec.approval.waitDecision` attende una singola approvazione exec in sospeso e restituisce
  la decisione finale (o `null` in caso di timeout).
- `exec.approvals.get` e `exec.approvals.set` gestiscono gli snapshot della policy di approvazione exec del gateway.
- `exec.approvals.node.get` e `exec.approvals.node.set` gestiscono la policy di approvazione exec locale del nodo
  tramite comandi di relay del nodo.
- `plugin.approval.request`, `plugin.approval.list`,
  `plugin.approval.waitDecision` e `plugin.approval.resolve` coprono
  i flussi di approvazione definiti dai plugin.

#### Altre principali famiglie

- automazione:
  - `wake` pianifica un'iniezione di testo wake immediata o al successivo heartbeat
  - `cron.list`, `cron.status`, `cron.add`, `cron.update`, `cron.remove`,
    `cron.run`, `cron.runs`
- skills/tools: `skills.*`, `tools.catalog`, `tools.effective`

### Famiglie comuni di eventi

- `chat`: aggiornamenti della chat UI come `chat.inject` e altri eventi chat
  solo transcript.
- `session.message` e `session.tool`: aggiornamenti del transcript/event-stream per una
  sessione sottoscritta.
- `sessions.changed`: l'indice della sessione o i metadati sono cambiati.
- `presence`: aggiornamenti dello snapshot della presence di sistema.
- `tick`: evento periodico di keepalive / liveness.
- `health`: aggiornamento dello snapshot di health del gateway.
- `heartbeat`: aggiornamento del flusso di eventi heartbeat.
- `cron`: evento di modifica di esecuzione/job cron.
- `shutdown`: notifica di arresto del gateway.
- `node.pair.requested` / `node.pair.resolved`: ciclo di vita del pairing dei nodi.
- `node.invoke.request`: broadcast di richiesta invoke del nodo.
- `device.pair.requested` / `device.pair.resolved`: ciclo di vita del dispositivo associato.
- `voicewake.changed`: la configurazione dei trigger della parola di attivazione è cambiata.
- `exec.approval.requested` / `exec.approval.resolved`: ciclo di vita
  dell'approvazione exec.
- `plugin.approval.requested` / `plugin.approval.resolved`: ciclo di vita dell'approvazione del plugin.

### Metodi helper node

- I nodi possono chiamare `skills.bins` per recuperare l'elenco corrente degli eseguibili delle skill
  per i controlli di auto-allow.

### Metodi helper operator

- Gli operator possono chiamare `tools.catalog` (`operator.read`) per recuperare il catalogo runtime degli strumenti per un
  agente. La risposta include strumenti raggruppati e metadati di provenienza:
  - `source`: `core` o `plugin`
  - `pluginId`: proprietario del plugin quando `source="plugin"`
  - `optional`: se uno strumento plugin è facoltativo
- Gli operator possono chiamare `tools.effective` (`operator.read`) per recuperare l'inventario degli strumenti effettivo a runtime
  per una sessione.
  - `sessionKey` è obbligatorio.
  - Il gateway deriva il contesto runtime attendibile dalla sessione lato server invece di accettare
    auth o contesto di consegna forniti dal chiamante.
  - La risposta ha ambito di sessione e riflette ciò che la conversazione attiva può usare in questo momento,
    inclusi strumenti core, plugin e canale.
- Gli operator possono chiamare `skills.status` (`operator.read`) per recuperare l'inventario visibile
  delle skill per un agente.
  - `agentId` è facoltativo; omettilo per leggere il workspace dell'agente predefinito.
  - La risposta include idoneità, requisiti mancanti, controlli di configurazione e
    opzioni di installazione sanificate senza esporre valori segreti grezzi.
- Gli operator possono chiamare `skills.search` e `skills.detail` (`operator.read`) per i metadati di discovery di
  ClawHub.
- Gli operator possono chiamare `skills.install` (`operator.admin`) in due modalità:
  - Modalità ClawHub: `{ source: "clawhub", slug, version?, force? }` installa una
    cartella skill nella directory `skills/` del workspace dell'agente predefinito.
  - Modalità installer gateway: `{ name, installId, dangerouslyForceUnsafeInstall?, timeoutMs? }`
    esegue un'azione dichiarata `metadata.openclaw.install` sull'host gateway.
- Gli operator possono chiamare `skills.update` (`operator.admin`) in due modalità:
  - La modalità ClawHub aggiorna uno slug tracciato o tutte le installazioni ClawHub tracciate nel
    workspace dell'agente predefinito.
  - La modalità Config modifica i valori `skills.entries.<skillKey>` come `enabled`,
    `apiKey` ed `env`.

## Approvazioni exec

- Quando una richiesta exec richiede approvazione, il gateway trasmette `exec.approval.requested`.
- I client operator risolvono chiamando `exec.approval.resolve` (richiede ambito `operator.approvals`).
- Per `host=node`, `exec.approval.request` deve includere `systemRunPlan` (`argv`/`cwd`/`rawCommand`/metadati di sessione canonici). Le richieste senza `systemRunPlan` vengono rifiutate.
- Dopo l'approvazione, le chiamate `node.invoke system.run` inoltrate riutilizzano quel
  `systemRunPlan` canonico come contesto autorevole di comando/cwd/sessione.
- Se un chiamante modifica `command`, `rawCommand`, `cwd`, `agentId` o
  `sessionKey` tra prepare e l'inoltro finale approvato di `system.run`, il
  gateway rifiuta l'esecuzione invece di fidarsi del payload modificato.

## Fallback di consegna dell'agente

- Le richieste `agent` possono includere `deliver=true` per richiedere la consegna in uscita.
- `bestEffortDeliver=false` mantiene il comportamento rigoroso: i target di consegna irrisolti o solo interni restituiscono `INVALID_REQUEST`.
- `bestEffortDeliver=true` consente il fallback all'esecuzione solo-sessione quando non è possibile risolvere alcun percorso di consegna esterno (ad esempio sessioni internal/webchat o configurazioni multi-canale ambigue).

## Versioning

- `PROTOCOL_VERSION` si trova in `src/gateway/protocol/schema.ts`.
- I client inviano `minProtocol` + `maxProtocol`; il server rifiuta i mismatch.
- Schemi + modelli sono generati da definizioni TypeBox:
  - `pnpm protocol:gen`
  - `pnpm protocol:gen:swift`
  - `pnpm protocol:check`

## Auth

- L'autenticazione gateway con secret condiviso usa `connect.params.auth.token` o
  `connect.params.auth.password`, a seconda della modalità auth configurata.
- Le modalità con identità portante come Tailscale Serve
  (`gateway.auth.allowTailscale: true`) o `gateway.auth.mode: "trusted-proxy"` non-loopback
  soddisfano il controllo auth di connect dagli header della richiesta invece che da `connect.params.auth.*`.
- L'ingresso privato `gateway.auth.mode: "none"` salta completamente l'auth connect con secret condiviso; non esporre quella modalità su ingressi pubblici/non attendibili.
- Dopo il pairing, il gateway emette un **token del dispositivo** con ambito del ruolo + degli ambiti della connessione. Viene restituito in `hello-ok.auth.deviceToken` e dovrebbe essere
  persistito dal client per le connessioni future.
- I client dovrebbero persistere il `hello-ok.auth.deviceToken` primario dopo ogni
  connessione riuscita.
- La riconnessione con quel token del dispositivo **memorizzato** dovrebbe anche riutilizzare l'insieme di ambiti approvati memorizzato
  per quel token. Questo preserva l'accesso in lettura/probe/stato
  già concesso ed evita di ridurre silenziosamente le riconnessioni a un
  ambito implicito più ristretto solo admin.
- La normale precedenza auth di connect è prima token/password condivisi espliciti, poi
  `deviceToken` esplicito, poi token per dispositivo memorizzato, poi token di bootstrap.
- Le voci aggiuntive `hello-ok.auth.deviceTokens` sono token di passaggio bootstrap.
  Persistile solo quando la connessione ha usato auth bootstrap su un trasporto attendibile
  come `wss://` o pairing loopback/locale.
- Se un client fornisce un **`deviceToken` esplicito** o `scopes` espliciti, quell'insieme di ambiti richiesto dal chiamante resta autorevole; gli ambiti in cache vengono riutilizzati solo
  quando il client sta riutilizzando il token per dispositivo memorizzato.
- I token del dispositivo possono essere ruotati/revocati tramite `device.token.rotate` e
  `device.token.revoke` (richiede ambito `operator.pairing`).
- L'emissione/rotazione dei token resta limitata all'insieme di ruoli approvati registrato nella
  voce di pairing di quel dispositivo; ruotare un token non può espandere il dispositivo in un
  ruolo che l'approvazione del pairing non ha mai concesso.
- Per le sessioni token di dispositivo associato, la gestione del dispositivo ha ambito proprio salvo che il
  chiamante abbia anche `operator.admin`: i chiamanti non-admin possono rimuovere/revocare/ruotare
  solo la **propria** voce dispositivo.
- `device.token.rotate` controlla anche l'insieme di ambiti operator richiesto rispetto agli
  ambiti della sessione corrente del chiamante. I chiamanti non-admin non possono ruotare un token in un insieme di ambiti operator più ampio di quello che già possiedono.
- I fallimenti auth includono `error.details.code` più suggerimenti di recupero:
  - `error.details.canRetryWithDeviceToken` (boolean)
  - `error.details.recommendedNextStep` (`retry_with_device_token`, `update_auth_configuration`, `update_auth_credentials`, `wait_then_retry`, `review_auth_configuration`)
- Comportamento del client per `AUTH_TOKEN_MISMATCH`:
  - I client attendibili possono tentare un unico retry limitato con un token per dispositivo in cache.
  - Se quel retry fallisce, i client devono interrompere i loop di riconnessione automatica e mostrare indicazioni per l'azione dell'operatore.

## Identità del dispositivo + pairing

- I nodi devono includere un'identità del dispositivo stabile (`device.id`) derivata da un
  fingerprint della coppia di chiavi.
- I gateway emettono token per dispositivo + ruolo.
- Le approvazioni di pairing sono richieste per nuovi ID dispositivo a meno che non sia abilitata
  l'auto-approvazione locale.
- L'auto-approvazione del pairing è centrata sulle connessioni dirette local loopback.
- OpenClaw ha anche un percorso ristretto di self-connect backend/container-local per
  flussi helper attendibili con secret condiviso.
- Le connessioni tailnet o LAN sullo stesso host sono comunque trattate come remote per il pairing e
  richiedono approvazione.
- Tutti i client WS devono includere l'identità `device` durante `connect` (operator + node).
  Control UI può ometterla solo in queste modalità:
  - `gateway.controlUi.allowInsecureAuth=true` per compatibilità localhost-only con HTTP insicuro.
  - auth operator Control UI riuscita con `gateway.auth.mode: "trusted-proxy"`.
  - `gateway.controlUi.dangerouslyDisableDeviceAuth=true` (break-glass, grave downgrade della sicurezza).
- Tutte le connessioni devono firmare il nonce `connect.challenge` fornito dal server.

### Diagnostica di migrazione auth del dispositivo

Per i client legacy che usano ancora il comportamento di firma pre-challenge, `connect` ora restituisce
codici di dettaglio `DEVICE_AUTH_*` sotto `error.details.code` con un `error.details.reason` stabile.

Fallimenti di migrazione comuni:

| Messaggio                    | details.code                     | details.reason           | Significato                                         |
| ---------------------------- | -------------------------------- | ------------------------ | --------------------------------------------------- |
| `device nonce required`      | `DEVICE_AUTH_NONCE_REQUIRED`     | `device-nonce-missing`   | Il client ha omesso `device.nonce` (o lo ha inviato vuoto). |
| `device nonce mismatch`      | `DEVICE_AUTH_NONCE_MISMATCH`     | `device-nonce-mismatch`  | Il client ha firmato con un nonce vecchio/errato.   |
| `device signature invalid`   | `DEVICE_AUTH_SIGNATURE_INVALID`  | `device-signature`       | Il payload della firma non corrisponde al payload v2. |
| `device signature expired`   | `DEVICE_AUTH_SIGNATURE_EXPIRED`  | `device-signature-stale` | Il timestamp firmato è fuori dallo skew consentito. |
| `device identity mismatch`   | `DEVICE_AUTH_DEVICE_ID_MISMATCH` | `device-id-mismatch`     | `device.id` non corrisponde al fingerprint della chiave pubblica. |
| `device public key invalid`  | `DEVICE_AUTH_PUBLIC_KEY_INVALID` | `device-public-key`      | Il formato/canonicalizzazione della chiave pubblica non è riuscito. |

Obiettivo della migrazione:

- Attendere sempre `connect.challenge`.
- Firmare il payload v2 che include il nonce del server.
- Inviare lo stesso nonce in `connect.params.device.nonce`.
- Il payload di firma preferito è `v3`, che vincola `platform` e `deviceFamily`
  oltre ai campi device/client/role/scopes/token/nonce.
- Le firme legacy `v2` restano accettate per compatibilità, ma il pinning dei metadati del dispositivo associato continua a controllare la policy dei comandi alla riconnessione.

## TLS + pinning

- TLS è supportato per le connessioni WS.
- I client possono opzionalmente fissare il fingerprint del certificato del gateway (vedi config `gateway.tls`
  più `gateway.remote.tlsFingerprint` o CLI `--tls-fingerprint`).

## Ambito

Questo protocollo espone la **API completa del gateway** (status, channels, models, chat,
agent, sessions, nodes, approvals, ecc.). La superficie esatta è definita dagli
schemi TypeBox in `src/gateway/protocol/schema.ts`.
