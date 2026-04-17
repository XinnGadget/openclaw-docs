---
read_when:
    - Esecuzione dei test in locale o in CI
    - Aggiunta di regressioni per bug di modelli/provider
    - Debug del comportamento di Gateway + agent
summary: 'Kit di test: suite unit/e2e/live, runner Docker e cosa copre ciascun test'
title: Test
x-i18n:
    generated_at: "2026-04-17T08:17:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: 55483bc68d3b24daca3189fba3af1e896f39b8e83068d102fed06eac05b36102
    source_path: help/testing.md
    workflow: 15
---

# Test

OpenClaw ha tre suite Vitest (unit/integration, e2e, live) e un piccolo insieme di runner Docker.

Questa documentazione è una guida al “come testiamo”:

- Cosa copre ciascuna suite (e cosa deliberatamente _non_ copre)
- Quali comandi eseguire per i flussi di lavoro comuni (locale, pre-push, debug)
- Come i test live individuano le credenziali e selezionano modelli/provider
- Come aggiungere regressioni per problemi reali di modelli/provider

## Avvio rapido

Nella maggior parte dei casi:

- Gate completo (atteso prima del push): `pnpm build && pnpm check && pnpm test`
- Esecuzione locale più veloce dell’intera suite su una macchina capiente: `pnpm test:max`
- Loop watch diretto di Vitest: `pnpm test:watch`
- Il targeting diretto dei file ora instrada anche i percorsi di extension/channel: `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`
- Quando stai iterando su un singolo errore, preferisci prima le esecuzioni mirate.
- Sito QA con supporto Docker: `pnpm qa:lab:up`
- Corsia QA con supporto VM Linux: `pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline`

Quando tocchi i test o vuoi maggiore sicurezza:

- Gate di copertura: `pnpm test:coverage`
- Suite E2E: `pnpm test:e2e`

Quando esegui il debug di provider/modelli reali (richiede credenziali reali):

- Suite live (sonde di modelli + tool/immagini del gateway): `pnpm test:live`
- Seleziona un singolo file live in modalità silenziosa: `pnpm test:live -- src/agents/models.profiles.live.test.ts`

Suggerimento: quando ti serve solo un caso fallito, preferisci restringere i test live tramite le variabili env di allowlist descritte sotto.

## Runner specifici per QA

Questi comandi si affiancano alle suite di test principali quando ti serve il realismo di QA-lab:

- `pnpm openclaw qa suite`
  - Esegue direttamente sull’host gli scenari QA supportati dal repository.
  - Esegue più scenari selezionati in parallelo per impostazione predefinita con worker gateway isolati, fino a 64 worker o al numero di scenari selezionati. Usa `--concurrency <count>` per regolare il numero di worker, oppure `--concurrency 1` per la vecchia corsia seriale.
  - Supporta le modalità provider `live-frontier`, `mock-openai` e `aimock`.
    `aimock` avvia un server provider locale basato su AIMock per copertura sperimentale di fixture e mock di protocollo senza sostituire la corsia `mock-openai` basata sugli scenari.
- `pnpm openclaw qa suite --runner multipass`
  - Esegue la stessa suite QA all’interno di una VM Linux Multipass usa e getta.
  - Mantiene lo stesso comportamento di selezione degli scenari di `qa suite` sull’host.
  - Riutilizza gli stessi flag di selezione provider/modello di `qa suite`.
  - Le esecuzioni live inoltrano gli input di autenticazione QA supportati che sono pratici per il guest:
    chiavi provider basate su env, il percorso della configurazione del provider live QA e `CODEX_HOME` quando presente.
  - Le directory di output devono rimanere sotto la root del repository affinché il guest possa scrivere indietro tramite il workspace montato.
  - Scrive il normale report + riepilogo QA e i log di Multipass sotto `.artifacts/qa-e2e/...`.
- `pnpm qa:lab:up`
  - Avvia il sito QA con supporto Docker per attività QA in stile operatore.
- `pnpm openclaw qa aimock`
  - Avvia solo il server provider locale AIMock per test smoke diretti del protocollo.
- `pnpm openclaw qa matrix`
  - Esegue la corsia QA live Matrix contro un homeserver Tuwunel usa e getta supportato da Docker.
  - Questo host QA oggi è solo per repository/sviluppo. Le installazioni OpenClaw pacchettizzate non distribuiscono `qa-lab`, quindi non espongono `openclaw qa`.
  - I checkout del repository caricano direttamente il runner integrato; non è necessario alcun passaggio separato di installazione del plugin.
  - Effettua il provisioning di tre utenti Matrix temporanei (`driver`, `sut`, `observer`) più una stanza privata, quindi avvia un processo figlio del gateway QA con il vero plugin Matrix come trasporto SUT.
  - Usa per impostazione predefinita l’immagine stabile Tuwunel fissata `ghcr.io/matrix-construct/tuwunel:v1.5.1`. Sostituiscila con `OPENCLAW_QA_MATRIX_TUWUNEL_IMAGE` quando devi testare un’immagine diversa.
  - Matrix non espone flag condivisi per la sorgente delle credenziali perché la corsia effettua localmente il provisioning di utenti usa e getta.
  - Scrive un report QA Matrix, un riepilogo, un artifact observed-events e un log combinato stdout/stderr sotto `.artifacts/qa-e2e/...`.
- `pnpm openclaw qa telegram`
  - Esegue la corsia QA live Telegram contro un gruppo privato reale usando i token bot del driver e del SUT provenienti dall’env.
  - Richiede `OPENCLAW_QA_TELEGRAM_GROUP_ID`, `OPENCLAW_QA_TELEGRAM_DRIVER_BOT_TOKEN` e `OPENCLAW_QA_TELEGRAM_SUT_BOT_TOKEN`. L’id del gruppo deve essere l’id numerico della chat Telegram.
  - Supporta `--credential-source convex` per credenziali condivise in pool. Usa per impostazione predefinita la modalità env, oppure imposta `OPENCLAW_QA_CREDENTIAL_SOURCE=convex` per adottare lease condivisi.
  - Richiede due bot distinti nello stesso gruppo privato, con il bot SUT che espone un nome utente Telegram.
  - Per un’osservazione stabile bot-to-bot, abilita la modalità Bot-to-Bot Communication in `@BotFather` per entrambi i bot e assicurati che il bot driver possa osservare il traffico dei bot nel gruppo.
  - Scrive un report QA Telegram, un riepilogo e un artifact observed-messages sotto `.artifacts/qa-e2e/...`.

Le corsie live transport condividono un unico contratto standard così che i nuovi transport non divergano:

`qa-channel` rimane la suite QA sintetica ampia e non fa parte della matrice di copertura live transport.

| Corsia   | Canary | Vincolo di mention | Blocco allowlist | Risposta di primo livello | Ripresa dopo riavvio | Follow-up nel thread | Isolamento del thread | Osservazione delle reazioni | Comando help |
| -------- | ------ | ------------------ | ---------------- | ------------------------- | -------------------- | -------------------- | --------------------- | --------------------------- | ------------ |
| Matrix   | x      | x                  | x                | x                         | x                    | x                    | x                     | x                           |              |
| Telegram | x      |                    |                  |                           |                      |                      |                       |                             | x            |

### Credenziali Telegram condivise tramite Convex (v1)

Quando `--credential-source convex` (o `OPENCLAW_QA_CREDENTIAL_SOURCE=convex`) è abilitato per
`openclaw qa telegram`, QA lab acquisisce un lease esclusivo da un pool supportato da Convex, invia heartbeat
a quel lease mentre la corsia è in esecuzione e rilascia il lease allo spegnimento.

Scaffold di riferimento del progetto Convex:

- `qa/convex-credential-broker/`

Variabili env obbligatorie:

- `OPENCLAW_QA_CONVEX_SITE_URL` (ad esempio `https://your-deployment.convex.site`)
- Un secret per il ruolo selezionato:
  - `OPENCLAW_QA_CONVEX_SECRET_MAINTAINER` per `maintainer`
  - `OPENCLAW_QA_CONVEX_SECRET_CI` per `ci`
- Selezione del ruolo credenziale:
  - CLI: `--credential-role maintainer|ci`
  - Valore env predefinito: `OPENCLAW_QA_CREDENTIAL_ROLE` (predefinito `maintainer`)

Variabili env facoltative:

- `OPENCLAW_QA_CREDENTIAL_LEASE_TTL_MS` (predefinito `1200000`)
- `OPENCLAW_QA_CREDENTIAL_HEARTBEAT_INTERVAL_MS` (predefinito `30000`)
- `OPENCLAW_QA_CREDENTIAL_ACQUIRE_TIMEOUT_MS` (predefinito `90000`)
- `OPENCLAW_QA_CREDENTIAL_HTTP_TIMEOUT_MS` (predefinito `15000`)
- `OPENCLAW_QA_CONVEX_ENDPOINT_PREFIX` (predefinito `/qa-credentials/v1`)
- `OPENCLAW_QA_CREDENTIAL_OWNER_ID` (id di trace facoltativo)
- `OPENCLAW_QA_ALLOW_INSECURE_HTTP=1` consente URL Convex `http://` di loopback solo per sviluppo locale.

`OPENCLAW_QA_CONVEX_SITE_URL` dovrebbe usare `https://` nel funzionamento normale.

I comandi CLI di amministrazione per i maintainer (aggiungi/rimuovi/elenca pool) richiedono
specificamente `OPENCLAW_QA_CONVEX_SECRET_MAINTAINER`.

Helper CLI per i maintainer:

```bash
pnpm openclaw qa credentials add --kind telegram --payload-file qa/telegram-credential.json
pnpm openclaw qa credentials list --kind telegram
pnpm openclaw qa credentials remove --credential-id <credential-id>
```

Usa `--json` per output leggibile dalle macchine negli script e nelle utility CI.

Contratto endpoint predefinito (`OPENCLAW_QA_CONVEX_SITE_URL` + `/qa-credentials/v1`):

- `POST /acquire`
  - Richiesta: `{ kind, ownerId, actorRole, leaseTtlMs, heartbeatIntervalMs }`
  - Successo: `{ status: "ok", credentialId, leaseToken, payload, leaseTtlMs?, heartbeatIntervalMs? }`
  - Esaurito/riprovabile: `{ status: "error", code: "POOL_EXHAUSTED" | "NO_CREDENTIAL_AVAILABLE", ... }`
- `POST /heartbeat`
  - Richiesta: `{ kind, ownerId, actorRole, credentialId, leaseToken, leaseTtlMs }`
  - Successo: `{ status: "ok" }` (o `2xx` vuoto)
- `POST /release`
  - Richiesta: `{ kind, ownerId, actorRole, credentialId, leaseToken }`
  - Successo: `{ status: "ok" }` (o `2xx` vuoto)
- `POST /admin/add` (solo secret maintainer)
  - Richiesta: `{ kind, actorId, payload, note?, status? }`
  - Successo: `{ status: "ok", credential }`
- `POST /admin/remove` (solo secret maintainer)
  - Richiesta: `{ credentialId, actorId }`
  - Successo: `{ status: "ok", changed, credential }`
  - Protezione lease attivo: `{ status: "error", code: "LEASE_ACTIVE", ... }`
- `POST /admin/list` (solo secret maintainer)
  - Richiesta: `{ kind?, status?, includePayload?, limit? }`
  - Successo: `{ status: "ok", credentials, count }`

Forma del payload per il tipo Telegram:

- `{ groupId: string, driverToken: string, sutToken: string }`
- `groupId` deve essere una stringa con l’id numerico della chat Telegram.
- `admin/add` valida questa forma per `kind: "telegram"` e rifiuta payload non validi.

### Aggiungere un channel a QA

Aggiungere un channel al sistema QA in markdown richiede esattamente due cose:

1. Un adapter transport per il channel.
2. Un pacchetto di scenari che eserciti il contratto del channel.

Non aggiungere una nuova root di comando QA di primo livello quando l’host condiviso `qa-lab` può
gestire il flusso.

`qa-lab` gestisce le meccaniche host condivise:

- la root di comando `openclaw qa`
- l’avvio e l’arresto della suite
- la concorrenza dei worker
- la scrittura degli artifact
- la generazione dei report
- l’esecuzione degli scenari
- alias di compatibilità per i vecchi scenari `qa-channel`

I plugin runner gestiscono il contratto transport:

- come `openclaw qa <runner>` viene montato sotto la root condivisa `qa`
- come il gateway viene configurato per quel transport
- come viene verificata la readiness
- come vengono iniettati gli eventi in ingresso
- come vengono osservati i messaggi in uscita
- come vengono esposti transcript e stato transport normalizzato
- come vengono eseguite le azioni supportate dal transport
- come viene gestito il reset o la pulizia specifici del transport

La soglia minima di adozione per un nuovo channel è:

1. Mantenere `qa-lab` come proprietario della root condivisa `qa`.
2. Implementare il runner transport sulla seam host condivisa di `qa-lab`.
3. Mantenere le meccaniche specifiche del transport all’interno del plugin runner o dell’harness del plugin channel.
4. Montare il runner come `openclaw qa <runner>` invece di registrare una root di comando concorrente.
   I plugin runner dovrebbero dichiarare `qaRunners` in `openclaw.plugin.json` ed esportare un array `qaRunnerCliRegistrations` corrispondente da `runtime-api.ts`.
   Mantieni `runtime-api.ts` leggero; la CLI lazy e l’esecuzione del runner dovrebbero restare dietro entrypoint separati.
5. Creare o adattare scenari markdown sotto `qa/scenarios/`.
6. Usare gli helper di scenario generici per i nuovi scenari.
7. Mantenere funzionanti gli alias di compatibilità esistenti, a meno che il repository non stia effettuando una migrazione intenzionale.

La regola decisionale è rigorosa:

- Se un comportamento può essere espresso una sola volta in `qa-lab`, mettilo in `qa-lab`.
- Se un comportamento dipende da un solo channel transport, mantienilo in quel plugin runner o harness del plugin.
- Se uno scenario ha bisogno di una nuova capacità che può essere usata da più di un channel, aggiungi un helper generico invece di un branch specifico del channel in `suite.ts`.
- Se un comportamento è significativo solo per un transport, mantieni lo scenario specifico del transport e rendilo esplicito nel contratto dello scenario.

I nomi preferiti degli helper generici per i nuovi scenari sono:

- `waitForTransportReady`
- `waitForChannelReady`
- `injectInboundMessage`
- `injectOutboundMessage`
- `waitForTransportOutboundMessage`
- `waitForChannelOutboundMessage`
- `waitForNoTransportOutbound`
- `getTransportSnapshot`
- `readTransportMessage`
- `readTransportTranscript`
- `formatTransportTranscript`
- `resetTransport`

Gli alias di compatibilità rimangono disponibili per gli scenari esistenti, inclusi:

- `waitForQaChannelReady`
- `waitForOutboundMessage`
- `waitForNoOutbound`
- `formatConversationTranscript`
- `resetBus`

Il nuovo lavoro sui channel dovrebbe usare i nomi helper generici.
Gli alias di compatibilità esistono per evitare una migrazione in un solo giorno, non come modello per
la creazione di nuovi scenari.

## Suite di test (cosa viene eseguito e dove)

Pensa alle suite come a un “realismo crescente” (e flakiness/costo crescenti):

### Unit / integrazione (predefinita)

- Comando: `pnpm test`
- Configurazione: dieci esecuzioni shard sequenziali (`vitest.full-*.config.ts`) sui progetti Vitest scoped esistenti
- File: inventari core/unit in `src/**/*.test.ts`, `packages/**/*.test.ts`, `test/**/*.test.ts` e i test node `ui` in allowlist coperti da `vitest.unit.config.ts`
- Ambito:
  - Test unitari puri
  - Test di integrazione in-process (autenticazione Gateway, routing, tooling, parsing, config)
  - Regressioni deterministiche per bug noti
- Aspettative:
  - Viene eseguita in CI
  - Non richiede chiavi reali
  - Dovrebbe essere veloce e stabile
- Nota sui progetti:
  - `pnpm test` senza target ora esegue undici configurazioni shard più piccole (`core-unit-src`, `core-unit-security`, `core-unit-ui`, `core-unit-support`, `core-support-boundary`, `core-contracts`, `core-bundled`, `core-runtime`, `agentic`, `auto-reply`, `extensions`) invece di un unico enorme processo root-project nativo. Questo riduce il picco RSS su macchine cariche ed evita che il lavoro di auto-reply/extension sottragga risorse alle suite non correlate.
  - `pnpm test --watch` continua a usare il grafo di progetti nativo root `vitest.config.ts`, perché un loop watch multi-shard non è pratico.
  - `pnpm test`, `pnpm test:watch` e `pnpm test:perf:imports` instradano prima i target espliciti di file/directory attraverso corsie scoped, quindi `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts` evita di pagare il costo completo di avvio del root project.
  - `pnpm test:changed` espande i percorsi git modificati nelle stesse corsie scoped quando il diff tocca solo file sorgente/test instradabili; le modifiche a config/setup tornano comunque a una riesecuzione ampia del root project.
  - I test unitari leggeri lato import da agent, command, plugin, helper auto-reply, `plugin-sdk` e aree utility pure simili passano attraverso la corsia `unit-fast`, che salta `test/setup-openclaw-runtime.ts`; i file stateful/runtime-heavy restano sulle corsie esistenti.
  - Alcuni file sorgente helper selezionati di `plugin-sdk` e `commands` mappano anche le esecuzioni changed-mode verso test sibling espliciti in quelle corsie leggere, così le modifiche agli helper evitano di rieseguire l’intera suite pesante per quella directory.
  - `auto-reply` ora ha tre bucket dedicati: helper core di primo livello, test di integrazione `reply.*` di primo livello e il sottoalbero `src/auto-reply/reply/**`. Questo mantiene il lavoro dell’harness reply più pesante fuori dai test economici di status/chunk/token.
- Nota sul runner embedded:
  - Quando modifichi gli input di individuazione dei message-tool o il contesto runtime di Compaction,
    mantieni entrambi i livelli di copertura.
  - Aggiungi regressioni helper mirate per boundary puri di routing/normalizzazione.
  - Mantieni anche in salute le suite di integrazione del runner embedded:
    `src/agents/pi-embedded-runner/compact.hooks.test.ts`,
    `src/agents/pi-embedded-runner/run.overflow-compaction.test.ts` e
    `src/agents/pi-embedded-runner/run.overflow-compaction.loop.test.ts`.
  - Queste suite verificano che gli id scoped e il comportamento di Compaction continuino a passare
    attraverso i veri percorsi `run.ts` / `compact.ts`; i test solo helper non sono un
    sostituto sufficiente per questi percorsi di integrazione.
- Nota sul pool:
  - La configurazione base di Vitest ora usa `threads` per impostazione predefinita.
  - La configurazione Vitest condivisa fissa anche `isolate: false` e usa il runner non isolato nei progetti root, nelle configurazioni e2e e live.
  - La corsia root UI mantiene il proprio setup `jsdom` e l’optimizer, ma ora gira anch’essa sul runner condiviso non isolato.
  - Ogni shard di `pnpm test` eredita gli stessi valori predefiniti `threads` + `isolate: false` dalla configurazione Vitest condivisa.
  - Il launcher condiviso `scripts/run-vitest.mjs` ora aggiunge anche `--no-maglev` per impostazione predefinita ai processi child Node di Vitest, per ridurre il churn di compilazione V8 durante grandi esecuzioni locali. Imposta `OPENCLAW_VITEST_ENABLE_MAGLEV=1` se devi confrontare il comportamento con V8 standard.
- Nota sull’iterazione locale veloce:
  - `pnpm test:changed` passa attraverso corsie scoped quando i percorsi modificati mappano in modo pulito a una suite più piccola.
  - `pnpm test:max` e `pnpm test:changed:max` mantengono lo stesso comportamento di instradamento, solo con un limite worker più alto.
  - L’auto-scaling locale dei worker ora è intenzionalmente più conservativo e riduce anche quando il load average dell’host è già alto, così più esecuzioni Vitest concorrenti fanno meno danni per impostazione predefinita.
  - La configurazione base di Vitest contrassegna i file di progetto/config come `forceRerunTriggers` così le riesecuzioni in modalità changed restano corrette quando cambia il wiring dei test.
  - La configurazione mantiene `OPENCLAW_VITEST_FS_MODULE_CACHE` abilitato sugli host supportati; imposta `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/abs/path` se vuoi una posizione cache esplicita per il profiling diretto.
- Nota sul debug delle prestazioni:
  - `pnpm test:perf:imports` abilita il report sulla durata degli import di Vitest più l’output di breakdown degli import.
  - `pnpm test:perf:imports:changed` limita la stessa vista di profiling ai file modificati da `origin/main`.
- `pnpm test:perf:changed:bench -- --ref <git-ref>` confronta il percorso instradato di `test:changed` con il percorso root-project nativo per quel diff committato e stampa wall time più max RSS su macOS.
- `pnpm test:perf:changed:bench -- --worktree` esegue benchmark dell’albero dirty corrente instradando l’elenco dei file modificati attraverso `scripts/test-projects.mjs` e la configurazione root Vitest.
  - `pnpm test:perf:profile:main` scrive un profilo CPU del thread principale per l’overhead di avvio e trasformazione di Vitest/Vite.
  - `pnpm test:perf:profile:runner` scrive profili CPU+heap del runner per la suite unitaria con il parallelismo dei file disabilitato.

### E2E (smoke Gateway)

- Comando: `pnpm test:e2e`
- Configurazione: `vitest.e2e.config.ts`
- File: `src/**/*.e2e.test.ts`, `test/**/*.e2e.test.ts`
- Valori predefiniti runtime:
  - Usa Vitest `threads` con `isolate: false`, in linea con il resto del repository.
  - Usa worker adattivi (CI: fino a 2, locale: 1 per impostazione predefinita).
  - Viene eseguita in modalità silenziosa per impostazione predefinita per ridurre l’overhead I/O della console.
- Override utili:
  - `OPENCLAW_E2E_WORKERS=<n>` per forzare il numero di worker (massimo 16).
  - `OPENCLAW_E2E_VERBOSE=1` per riattivare output console dettagliato.
- Ambito:
  - Comportamento end-to-end multiistanza del Gateway
  - Superfici WebSocket/HTTP, pairing dei Node e networking più pesante
- Aspettative:
  - Viene eseguita in CI (quando abilitata nella pipeline)
  - Non richiede chiavi reali
  - Ha più parti in movimento rispetto ai test unitari (può essere più lenta)

### E2E: smoke backend OpenShell

- Comando: `pnpm test:e2e:openshell`
- File: `test/openshell-sandbox.e2e.test.ts`
- Ambito:
  - Avvia sull’host un Gateway OpenShell isolato tramite Docker
  - Crea un sandbox a partire da un Dockerfile locale temporaneo
  - Esercita il backend OpenShell di OpenClaw su `sandbox ssh-config` reale + exec SSH
  - Verifica il comportamento del filesystem canonico remoto tramite il bridge fs del sandbox
- Aspettative:
  - Solo opt-in; non fa parte dell’esecuzione predefinita `pnpm test:e2e`
  - Richiede una CLI locale `openshell` e un daemon Docker funzionante
  - Usa `HOME` / `XDG_CONFIG_HOME` isolati, quindi distrugge il Gateway di test e il sandbox
- Override utili:
  - `OPENCLAW_E2E_OPENSHELL=1` per abilitare il test quando si esegue manualmente la suite e2e più ampia
  - `OPENCLAW_E2E_OPENSHELL_COMMAND=/path/to/openshell` per puntare a un binario CLI non predefinito o a uno script wrapper

### Live (provider reali + modelli reali)

- Comando: `pnpm test:live`
- Configurazione: `vitest.live.config.ts`
- File: `src/**/*.live.test.ts`
- Predefinito: **abilitata** da `pnpm test:live` (imposta `OPENCLAW_LIVE_TEST=1`)
- Ambito:
  - “Questo provider/modello funziona davvero _oggi_ con credenziali reali?”
  - Intercettare cambi di formato del provider, particolarità delle tool call, problemi di autenticazione e comportamento dei rate limit
- Aspettative:
  - Per progettazione non è stabile in CI (reti reali, policy reali dei provider, quote, outage)
  - Costa denaro / usa rate limit
  - È preferibile eseguire sottoinsiemi ristretti invece di “tutto”
- Le esecuzioni live leggono `~/.profile` per recuperare eventuali chiavi API mancanti.
- Per impostazione predefinita, le esecuzioni live isolano comunque `HOME` e copiano il materiale di config/auth in una home di test temporanea, così le fixture unitarie non possono modificare il tuo vero `~/.openclaw`.
- Imposta `OPENCLAW_LIVE_USE_REAL_HOME=1` solo quando hai intenzionalmente bisogno che i test live usino la tua vera home directory.
- `pnpm test:live` ora usa per impostazione predefinita una modalità più silenziosa: mantiene l’output di avanzamento `[live] ...`, ma sopprime l’avviso extra su `~/.profile` e silenzia i log di bootstrap del Gateway e il chatter Bonjour. Imposta `OPENCLAW_LIVE_TEST_QUIET=0` se vuoi ripristinare i log completi di avvio.
- Rotazione delle chiavi API (specifica per provider): imposta `*_API_KEYS` con formato virgola/punto e virgola oppure `*_API_KEY_1`, `*_API_KEY_2` (ad esempio `OPENAI_API_KEYS`, `ANTHROPIC_API_KEYS`, `GEMINI_API_KEYS`) oppure l’override per-live `OPENCLAW_LIVE_*_KEY`; i test ritentano in caso di risposte con rate limit.
- Output di avanzamento/heartbeat:
  - Le suite live ora emettono righe di avanzamento su stderr così le chiamate lunghe al provider risultano visibilmente attive anche quando il capture della console di Vitest è silenzioso.
  - `vitest.live.config.ts` disabilita l’intercettazione della console di Vitest così le righe di avanzamento provider/Gateway vengono trasmesse subito durante le esecuzioni live.
  - Regola gli heartbeat direct-model con `OPENCLAW_LIVE_HEARTBEAT_MS`.
  - Regola gli heartbeat Gateway/probe con `OPENCLAW_LIVE_GATEWAY_HEARTBEAT_MS`.

## Quale suite dovrei eseguire?

Usa questa tabella decisionale:

- Stai modificando logica/test: esegui `pnpm test` (e `pnpm test:coverage` se hai cambiato molto)
- Stai toccando networking del Gateway / protocollo WS / pairing: aggiungi `pnpm test:e2e`
- Stai facendo debug di “il mio bot è giù” / errori specifici del provider / tool calling: esegui un `pnpm test:live` ristretto

## Live: sweep delle capability del Node Android

- Test: `src/gateway/android-node.capabilities.live.test.ts`
- Script: `pnpm android:test:integration`
- Obiettivo: invocare **ogni comando attualmente pubblicizzato** da un Node Android connesso e verificare il comportamento del contratto del comando.
- Ambito:
  - Setup manuale/precondizionato (la suite non installa/esegue/effettua il pairing dell’app).
  - Validazione `node.invoke` del Gateway comando per comando per il Node Android selezionato.
- Pre-setup richiesto:
  - App Android già connessa + associata al Gateway.
  - App mantenuta in foreground.
  - Permessi/consenso di acquisizione concessi per le capability che ti aspetti passino.
- Override target facoltativi:
  - `OPENCLAW_ANDROID_NODE_ID` o `OPENCLAW_ANDROID_NODE_NAME`.
  - `OPENCLAW_ANDROID_GATEWAY_URL` / `OPENCLAW_ANDROID_GATEWAY_TOKEN` / `OPENCLAW_ANDROID_GATEWAY_PASSWORD`.
- Dettagli completi sul setup Android: [App Android](/it/platforms/android)

## Live: smoke dei modelli (chiavi profilo)

I test live sono divisi in due livelli così possiamo isolare i guasti:

- “Direct model” ci dice se il provider/modello riesce almeno a rispondere con la chiave data.
- “Gateway smoke” ci dice se la pipeline completa Gateway+agent funziona per quel modello (sessioni, cronologia, tool, policy del sandbox, ecc.).

### Livello 1: completamento direct model (senza Gateway)

- Test: `src/agents/models.profiles.live.test.ts`
- Obiettivo:
  - Enumerare i modelli individuati
  - Usare `getApiKeyForModel` per selezionare i modelli per cui hai credenziali
  - Eseguire un piccolo completamento per modello (e regressioni mirate dove necessario)
- Come abilitarlo:
  - `pnpm test:live` (oppure `OPENCLAW_LIVE_TEST=1` se invochi direttamente Vitest)
- Imposta `OPENCLAW_LIVE_MODELS=modern` (oppure `all`, alias di modern) per eseguire davvero questa suite; altrimenti viene saltata per mantenere `pnpm test:live` focalizzato sul Gateway smoke
- Come selezionare i modelli:
  - `OPENCLAW_LIVE_MODELS=modern` per eseguire l’allowlist moderna (Opus/Sonnet 4.6+, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.7, Grok 4)
  - `OPENCLAW_LIVE_MODELS=all` è un alias per l’allowlist moderna
  - oppure `OPENCLAW_LIVE_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,..."` (allowlist separata da virgole)
  - Le sweep modern/all usano per impostazione predefinita un limite curato ad alto segnale; imposta `OPENCLAW_LIVE_MAX_MODELS=0` per una sweep moderna esaustiva oppure un numero positivo per un limite più piccolo.
- Come selezionare i provider:
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity,google-gemini-cli"` (allowlist separata da virgole)
- Da dove provengono le chiavi:
  - Per impostazione predefinita: store dei profili e fallback env
  - Imposta `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` per imporre **solo** lo store dei profili
- Perché esiste:
  - Separa “l’API del provider è rotta / la chiave non è valida” da “la pipeline agent del Gateway è rotta”
  - Contiene regressioni piccole e isolate (esempio: reasoning replay di OpenAI Responses/Codex Responses + flussi di tool call)

### Livello 2: smoke Gateway + agent dev (quello che fa davvero "@openclaw")

- Test: `src/gateway/gateway-models.profiles.live.test.ts`
- Obiettivo:
  - Avviare un Gateway in-process
  - Creare/modificare una sessione `agent:dev:*` (override del modello per esecuzione)
  - Iterare sui modelli-con-chiavi e verificare:
    - risposta “significativa” (senza tool)
    - il funzionamento di una vera invocazione di tool (sonda `read`)
    - sonde di tool extra facoltative (sonda `exec+read`)
    - che i percorsi di regressione OpenAI (solo tool-call → follow-up) continuino a funzionare
- Dettagli delle sonde (così puoi spiegare rapidamente i guasti):
  - sonda `read`: il test scrive un file nonce nel workspace e chiede all’agent di `read` e restituire il nonce.
  - sonda `exec+read`: il test chiede all’agent di scrivere un nonce in un file temporaneo tramite `exec`, quindi di leggerlo di nuovo con `read`.
  - sonda immagine: il test allega un PNG generato (gatto + codice randomizzato) e si aspetta che il modello restituisca `cat <CODE>`.
  - Riferimento di implementazione: `src/gateway/gateway-models.profiles.live.test.ts` e `src/gateway/live-image-probe.ts`.
- Come abilitarlo:
  - `pnpm test:live` (oppure `OPENCLAW_LIVE_TEST=1` se invochi direttamente Vitest)
- Come selezionare i modelli:
  - Predefinito: allowlist moderna (Opus/Sonnet 4.6+, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.7, Grok 4)
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all` è un alias per l’allowlist moderna
  - Oppure imposta `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"` (o una lista separata da virgole) per restringere
  - Le sweep gateway modern/all usano per impostazione predefinita un limite curato ad alto segnale; imposta `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=0` per una sweep moderna esaustiva oppure un numero positivo per un limite più piccolo.
- Come selezionare i provider (evita “tutto OpenRouter”):
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,google-gemini-cli,openai,anthropic,zai,minimax"` (allowlist separata da virgole)
- Le sonde tool + immagine sono sempre attive in questo test live:
  - sonda `read` + sonda `exec+read` (stress dei tool)
  - la sonda immagine viene eseguita quando il modello pubblicizza il supporto per input immagine
  - Flusso (alto livello):
    - Il test genera un piccolo PNG con “CAT” + codice casuale (`src/gateway/live-image-probe.ts`)
    - Lo invia tramite `agent` `attachments: [{ mimeType: "image/png", content: "<base64>" }]`
    - Il Gateway analizza gli allegati in `images[]` (`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`)
    - L’agent embedded inoltra al modello un messaggio utente multimodale
    - Verifica: la risposta contiene `cat` + il codice (tolleranza OCR: sono ammessi piccoli errori)

Suggerimento: per vedere cosa puoi testare sulla tua macchina (e gli id esatti `provider/model`), esegui:

```bash
openclaw models list
openclaw models list --json
```

## Live: smoke backend CLI (Claude, Codex, Gemini o altre CLI locali)

- Test: `src/gateway/gateway-cli-backend.live.test.ts`
- Obiettivo: validare la pipeline Gateway + agent usando un backend CLI locale, senza toccare la tua configurazione predefinita.
- I valori predefiniti smoke specifici del backend si trovano nella definizione `cli-backend.ts` del plugin proprietario.
- Abilitazione:
  - `pnpm test:live` (oppure `OPENCLAW_LIVE_TEST=1` se invochi direttamente Vitest)
  - `OPENCLAW_LIVE_CLI_BACKEND=1`
- Valori predefiniti:
  - Provider/modello predefinito: `claude-cli/claude-sonnet-4-6`
  - Il comportamento di comando/argomenti/immagine proviene dai metadati del plugin backend CLI proprietario.
- Override (facoltativi):
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4"`
  - `OPENCLAW_LIVE_CLI_BACKEND_COMMAND="/full/path/to/codex"`
  - `OPENCLAW_LIVE_CLI_BACKEND_ARGS='["exec","--json","--color","never","--sandbox","read-only","--skip-git-repo-check"]'`
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_PROBE=1` per inviare un vero allegato immagine (i percorsi vengono iniettati nel prompt).
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_ARG="--image"` per passare i percorsi dei file immagine come argomenti CLI invece dell’iniezione nel prompt.
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_MODE="repeat"` (oppure `"list"`) per controllare come vengono passati gli argomenti immagine quando `IMAGE_ARG` è impostato.
  - `OPENCLAW_LIVE_CLI_BACKEND_RESUME_PROBE=1` per inviare un secondo turno e validare il flusso di ripresa.
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL_SWITCH_PROBE=0` per disabilitare la sonda predefinita di continuità nella stessa sessione Claude Sonnet -> Opus (imposta `1` per forzarla quando il modello selezionato supporta una destinazione di switch).

Esempio:

```bash
OPENCLAW_LIVE_CLI_BACKEND=1 \
  OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4" \
  pnpm test:live src/gateway/gateway-cli-backend.live.test.ts
```

Ricetta Docker:

```bash
pnpm test:docker:live-cli-backend
```

Ricette Docker per singolo provider:

```bash
pnpm test:docker:live-cli-backend:claude
pnpm test:docker:live-cli-backend:claude-subscription
pnpm test:docker:live-cli-backend:codex
pnpm test:docker:live-cli-backend:gemini
```

Note:

- Il runner Docker si trova in `scripts/test-live-cli-backend-docker.sh`.
- Esegue lo smoke live CLI-backend dentro l’immagine Docker del repository come utente non root `node`.
- Risolve i metadati smoke CLI dall’extension proprietaria, quindi installa il pacchetto CLI Linux corrispondente (`@anthropic-ai/claude-code`, `@openai/codex` o `@google/gemini-cli`) in un prefisso scrivibile in cache in `OPENCLAW_DOCKER_CLI_TOOLS_DIR` (predefinito: `~/.cache/openclaw/docker-cli-tools`).
- `pnpm test:docker:live-cli-backend:claude-subscription` richiede OAuth portabile dell’abbonamento Claude Code tramite `~/.claude/.credentials.json` con `claudeAiOauth.subscriptionType` oppure `CLAUDE_CODE_OAUTH_TOKEN` da `claude setup-token`. Prima dimostra `claude -p` diretto in Docker, poi esegue due turni Gateway CLI-backend senza preservare le variabili env della chiave API Anthropic. Questa corsia subscription disabilita per impostazione predefinita le sonde Claude MCP/tool e immagine perché Claude attualmente instrada l’uso di app di terze parti tramite fatturazione extra-usage invece dei normali limiti del piano di abbonamento.
- Lo smoke live CLI-backend ora esercita lo stesso flusso end-to-end per Claude, Codex e Gemini: turno testuale, turno di classificazione immagine, quindi chiamata al tool MCP `cron` verificata tramite la CLI del Gateway.
- Lo smoke predefinito di Claude modifica inoltre la sessione da Sonnet a Opus e verifica che la sessione ripresa ricordi ancora una nota precedente.

## Live: smoke di bind ACP (`/acp spawn ... --bind here`)

- Test: `src/gateway/gateway-acp-bind.live.test.ts`
- Obiettivo: validare il vero flusso conversation-bind di ACP con un agent ACP live:
  - inviare `/acp spawn <agent> --bind here`
  - associare sul posto una conversazione sintetica di message-channel
  - inviare un normale follow-up sulla stessa conversazione
  - verificare che il follow-up arrivi nel transcript della sessione ACP associata
- Abilitazione:
  - `pnpm test:live src/gateway/gateway-acp-bind.live.test.ts`
  - `OPENCLAW_LIVE_ACP_BIND=1`
- Valori predefiniti:
  - Agent ACP in Docker: `claude,codex,gemini`
  - Agent ACP per `pnpm test:live ...` diretto: `claude`
  - Channel sintetico: contesto conversazione in stile DM Slack
  - Backend ACP: `acpx`
- Override:
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=claude`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=codex`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude,codex,gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND='npx -y @agentclientprotocol/claude-agent-acp@<version>'`
- Note:
  - Questa corsia usa la superficie `chat.send` del Gateway con campi synthetic originating-route riservati agli admin così i test possono allegare il contesto del message-channel senza fingere una consegna esterna.
  - Quando `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND` non è impostato, il test usa il registro agent integrato del plugin embedded `acpx` per l’agent harness ACP selezionato.

Esempio:

```bash
OPENCLAW_LIVE_ACP_BIND=1 \
  OPENCLAW_LIVE_ACP_BIND_AGENT=claude \
  pnpm test:live src/gateway/gateway-acp-bind.live.test.ts
```

Ricetta Docker:

```bash
pnpm test:docker:live-acp-bind
```

Ricette Docker per singolo agent:

```bash
pnpm test:docker:live-acp-bind:claude
pnpm test:docker:live-acp-bind:codex
pnpm test:docker:live-acp-bind:gemini
```

Note Docker:

- Il runner Docker si trova in `scripts/test-live-acp-bind-docker.sh`.
- Per impostazione predefinita, esegue in sequenza lo smoke ACP bind contro tutti gli agent CLI live supportati: `claude`, `codex`, poi `gemini`.
- Usa `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude`, `OPENCLAW_LIVE_ACP_BIND_AGENTS=codex` o `OPENCLAW_LIVE_ACP_BIND_AGENTS=gemini` per restringere la matrice.
- Legge `~/.profile`, prepara nel container il materiale auth CLI corrispondente, installa `acpx` in un prefisso npm scrivibile, quindi installa la CLI live richiesta (`@anthropic-ai/claude-code`, `@openai/codex` o `@google/gemini-cli`) se manca.
- Dentro Docker, il runner imposta `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=$HOME/.npm-global/bin/acpx` così acpx mantiene disponibili alla CLI harness figlia le variabili env del provider provenienti dal profilo caricato.

## Live: smoke harness app-server Codex

- Obiettivo: validare l’harness Codex posseduto dal plugin tramite il normale
  metodo `agent` del Gateway:
  - caricare il plugin integrato `codex`
  - selezionare `OPENCLAW_AGENT_RUNTIME=codex`
  - inviare un primo turno gateway agent a `codex/gpt-5.4`
  - inviare un secondo turno alla stessa sessione OpenClaw e verificare che il thread
    app-server possa riprendere
  - eseguire `/codex status` e `/codex models` tramite lo stesso percorso
    di comando del Gateway
- Test: `src/gateway/gateway-codex-harness.live.test.ts`
- Abilitazione: `OPENCLAW_LIVE_CODEX_HARNESS=1`
- Modello predefinito: `codex/gpt-5.4`
- Sonda immagine facoltativa: `OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=1`
- Sonda MCP/tool facoltativa: `OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=1`
- Lo smoke imposta `OPENCLAW_AGENT_HARNESS_FALLBACK=none` così un harness Codex
  guasto non può passare ricadendo silenziosamente su Pi.
- Auth: `OPENAI_API_KEY` dalla shell/profilo, più facoltativamente
  `~/.codex/auth.json` e `~/.codex/config.toml` copiati

Ricetta locale:

```bash
source ~/.profile
OPENCLAW_LIVE_CODEX_HARNESS=1 \
  OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=1 \
  OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=1 \
  OPENCLAW_LIVE_CODEX_HARNESS_MODEL=codex/gpt-5.4 \
  pnpm test:live -- src/gateway/gateway-codex-harness.live.test.ts
```

Ricetta Docker:

```bash
source ~/.profile
pnpm test:docker:live-codex-harness
```

Note Docker:

- Il runner Docker si trova in `scripts/test-live-codex-harness-docker.sh`.
- Legge il `~/.profile` montato, passa `OPENAI_API_KEY`, copia i file auth della CLI Codex
  quando presenti, installa `@openai/codex` in un prefisso npm montato e scrivibile,
  prepara l’albero sorgente, quindi esegue solo il test live Codex-harness.
- Docker abilita per impostazione predefinita le sonde immagine e MCP/tool. Imposta
  `OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=0` o
  `OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=0` quando hai bisogno di un’esecuzione di debug più ristretta.
- Docker esporta anche `OPENCLAW_AGENT_HARNESS_FALLBACK=none`, in linea con la configurazione del
  test live così il fallback `openai-codex/*` o Pi non può nascondere una regressione
  dell’harness Codex.

### Ricette live consigliate

Allowlist ristrette ed esplicite sono più veloci e meno soggette a flakiness:

- Modello singolo, direct (senza Gateway):
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.4" pnpm test:live src/agents/models.profiles.live.test.ts`

- Modello singolo, Gateway smoke:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Tool calling su più provider:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Focus Google (chiave API Gemini + Antigravity):
  - Gemini (chiave API): `OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  - Antigravity (OAuth): `OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

Note:

- `google/...` usa l’API Gemini (chiave API).
- `google-antigravity/...` usa il bridge OAuth Antigravity (endpoint agent in stile Cloud Code Assist).
- `google-gemini-cli/...` usa la CLI Gemini locale sulla tua macchina (autenticazione separata + particolarità dei tool).
- API Gemini vs CLI Gemini:
  - API: OpenClaw chiama via HTTP l’API Gemini ospitata da Google (autenticazione tramite chiave API / profilo); è ciò che la maggior parte degli utenti intende con “Gemini”.
  - CLI: OpenClaw esegue una shell verso un binario locale `gemini`; ha una propria autenticazione e può comportarsi diversamente (supporto streaming/tool/version skew).

## Live: matrice dei modelli (cosa copriamo)

Non esiste un “elenco modelli CI” fisso (live è opt-in), ma questi sono i modelli **consigliati** da coprire regolarmente su una macchina di sviluppo con chiavi.

### Set smoke moderno (tool calling + image)

Questa è l’esecuzione dei “modelli comuni” che ci aspettiamo continui a funzionare:

- OpenAI (non-Codex): `openai/gpt-5.4` (facoltativo: `openai/gpt-5.4-mini`)
- OpenAI Codex: `openai-codex/gpt-5.4`
- Anthropic: `anthropic/claude-opus-4-6` (oppure `anthropic/claude-sonnet-4-6`)
- Google (API Gemini): `google/gemini-3.1-pro-preview` e `google/gemini-3-flash-preview` (evita i vecchi modelli Gemini 2.x)
- Google (Antigravity): `google-antigravity/claude-opus-4-6-thinking` e `google-antigravity/gemini-3-flash`
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

Esegui Gateway smoke con tool + immagine:
`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,openai-codex/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3.1-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

### Baseline: tool calling (Read + Exec facoltativo)

Scegline almeno uno per famiglia di provider:

- OpenAI: `openai/gpt-5.4` (oppure `openai/gpt-5.4-mini`)
- Anthropic: `anthropic/claude-opus-4-6` (oppure `anthropic/claude-sonnet-4-6`)
- Google: `google/gemini-3-flash-preview` (oppure `google/gemini-3.1-pro-preview`)
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

Copertura aggiuntiva facoltativa (utile ma non indispensabile):

- xAI: `xai/grok-4` (oppure l’ultima disponibile)
- Mistral: `mistral/`… (scegli un modello con capacità “tools” che hai abilitato)
- Cerebras: `cerebras/`… (se hai accesso)
- LM Studio: `lmstudio/`… (locale; il tool calling dipende dalla modalità API)

### Vision: invio immagini (allegato → messaggio multimodale)

Includi almeno un modello con capacità immagine in `OPENCLAW_LIVE_GATEWAY_MODELS` (varianti Claude/Gemini/OpenAI con supporto vision, ecc.) per esercitare la sonda immagine.

### Aggregatori / Gateway alternativi

Se hai chiavi abilitate, supportiamo anche i test tramite:

- OpenRouter: `openrouter/...` (centinaia di modelli; usa `openclaw models scan` per trovare candidati con capacità tool+image)
- OpenCode: `opencode/...` per Zen e `opencode-go/...` per Go (autenticazione tramite `OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY`)

Altri provider che puoi includere nella matrice live (se hai credenziali/configurazione):

- Integrati: `openai`, `openai-codex`, `anthropic`, `google`, `google-vertex`, `google-antigravity`, `google-gemini-cli`, `zai`, `openrouter`, `opencode`, `opencode-go`, `xai`, `groq`, `cerebras`, `mistral`, `github-copilot`
- Tramite `models.providers` (endpoint personalizzati): `minimax` (cloud/API), più qualsiasi proxy compatibile OpenAI/Anthropic (LM Studio, vLLM, LiteLLM, ecc.)

Suggerimento: non cercare di codificare rigidamente “tutti i modelli” nella documentazione. L’elenco autorevole è quello che `discoverModels(...)` restituisce sulla tua macchina + qualunque chiave sia disponibile.

## Credenziali (non committare mai)

I test live individuano le credenziali nello stesso modo in cui lo fa la CLI. Implicazioni pratiche:

- Se la CLI funziona, i test live dovrebbero trovare le stesse chiavi.
- Se un test live dice “nessuna credenziale”, esegui il debug come faresti per `openclaw models list` / selezione del modello.

- Profili auth per-agent: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` (questo è il significato di “chiavi profilo” nei test live)
- Configurazione: `~/.openclaw/openclaw.json` (oppure `OPENCLAW_CONFIG_PATH`)
- Directory di stato legacy: `~/.openclaw/credentials/` (copiata nella home live staged quando presente, ma non è lo store principale delle chiavi profilo)
- Le esecuzioni live locali copiano per impostazione predefinita la configurazione attiva, i file `auth-profiles.json` per-agent, la directory legacy `credentials/` e le directory auth CLI esterne supportate in una home di test temporanea; le home live staged saltano `workspace/` e `sandboxes/`, e gli override di percorso `agents.*.workspace` / `agentDir` vengono rimossi così le sonde restano fuori dal tuo vero workspace host.

Se vuoi fare affidamento sulle chiavi env (ad esempio esportate nel tuo `~/.profile`), esegui i test locali dopo `source ~/.profile`, oppure usa i runner Docker qui sotto (possono montare `~/.profile` nel container).

## Live Deepgram (trascrizione audio)

- Test: `src/media-understanding/providers/deepgram/audio.live.test.ts`
- Abilitazione: `DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`

## Live BytePlus coding plan

- Test: `src/agents/byteplus.live.test.ts`
- Abilitazione: `BYTEPLUS_API_KEY=... BYTEPLUS_LIVE_TEST=1 pnpm test:live src/agents/byteplus.live.test.ts`
- Override facoltativo del modello: `BYTEPLUS_CODING_MODEL=ark-code-latest`

## Live media workflow ComfyUI

- Test: `extensions/comfy/comfy.live.test.ts`
- Abilitazione: `OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts`
- Ambito:
  - Esercita i percorsi integrati comfy per immagine, video e `music_generate`
  - Salta ogni capability a meno che `models.providers.comfy.<capability>` non sia configurato
  - Utile dopo modifiche all’invio del workflow comfy, polling, download o registrazione del plugin

## Live generazione immagini

- Test: `src/image-generation/runtime.live.test.ts`
- Comando: `pnpm test:live src/image-generation/runtime.live.test.ts`
- Harness: `pnpm test:live:media image`
- Ambito:
  - Enumera ogni plugin provider di generazione immagini registrato
  - Carica le variabili env mancanti del provider dalla tua shell di login (`~/.profile`) prima delle sonde
  - Usa per impostazione predefinita le chiavi API live/env prima dei profili auth memorizzati, così chiavi di test obsolete in `auth-profiles.json` non mascherano le vere credenziali della shell
  - Salta i provider senza auth/profilo/modello utilizzabili
  - Esegue le varianti standard di generazione immagini tramite la capability runtime condivisa:
    - `google:flash-generate`
    - `google:pro-generate`
    - `google:pro-edit`
    - `openai:default-generate`
- Provider integrati attualmente coperti:
  - `openai`
  - `google`
- Restrizione facoltativa:
  - `OPENCLAW_LIVE_IMAGE_GENERATION_PROVIDERS="openai,google"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_MODELS="openai/gpt-image-1,google/gemini-3.1-flash-image-preview"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_CASES="google:flash-generate,google:pro-edit"`
- Comportamento auth facoltativo:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` per forzare l’auth dallo store profili e ignorare gli override solo-env

## Live generazione musica

- Test: `extensions/music-generation-providers.live.test.ts`
- Abilitazione: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts`
- Harness: `pnpm test:live:media music`
- Ambito:
  - Esercita il percorso condiviso integrato del provider di generazione musica
  - Attualmente copre Google e MiniMax
  - Carica le variabili env del provider dalla tua shell di login (`~/.profile`) prima delle sonde
  - Usa per impostazione predefinita le chiavi API live/env prima dei profili auth memorizzati, così chiavi di test obsolete in `auth-profiles.json` non mascherano le vere credenziali della shell
  - Salta i provider senza auth/profilo/modello utilizzabili
  - Esegue entrambe le modalità runtime dichiarate quando disponibili:
    - `generate` con input di solo prompt
    - `edit` quando il provider dichiara `capabilities.edit.enabled`
  - Copertura attuale della corsia condivisa:
    - `google`: `generate`, `edit`
    - `minimax`: `generate`
    - `comfy`: file live Comfy separato, non questa sweep condivisa
- Restrizione facoltativa:
  - `OPENCLAW_LIVE_MUSIC_GENERATION_PROVIDERS="google,minimax"`
  - `OPENCLAW_LIVE_MUSIC_GENERATION_MODELS="google/lyria-3-clip-preview,minimax/music-2.5+"`
- Comportamento auth facoltativo:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` per forzare l’auth dallo store profili e ignorare gli override solo-env

## Live generazione video

- Test: `extensions/video-generation-providers.live.test.ts`
- Abilitazione: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts`
- Harness: `pnpm test:live:media video`
- Ambito:
  - Esercita il percorso condiviso integrato del provider di generazione video
  - Per impostazione predefinita usa il percorso smoke sicuro per il rilascio: provider non-FAL, una richiesta text-to-video per provider, prompt lobster di un secondo e un limite operativo per provider da `OPENCLAW_LIVE_VIDEO_GENERATION_TIMEOUT_MS` (`180000` per impostazione predefinita)
  - Salta FAL per impostazione predefinita perché la latenza della coda lato provider può dominare i tempi di rilascio; passa `--video-providers fal` oppure `OPENCLAW_LIVE_VIDEO_GENERATION_PROVIDERS="fal"` per eseguirlo esplicitamente
  - Carica le variabili env del provider dalla tua shell di login (`~/.profile`) prima delle sonde
  - Usa per impostazione predefinita le chiavi API live/env prima dei profili auth memorizzati, così chiavi di test obsolete in `auth-profiles.json` non mascherano le vere credenziali della shell
  - Salta i provider senza auth/profilo/modello utilizzabili
  - Esegue solo `generate` per impostazione predefinita
  - Imposta `OPENCLAW_LIVE_VIDEO_GENERATION_FULL_MODES=1` per eseguire anche le modalità transform dichiarate quando disponibili:
    - `imageToVideo` quando il provider dichiara `capabilities.imageToVideo.enabled` e il provider/modello selezionato accetta input immagine locale buffer-backed nella sweep condivisa
    - `videoToVideo` quando il provider dichiara `capabilities.videoToVideo.enabled` e il provider/modello selezionato accetta input video locale buffer-backed nella sweep condivisa
  - Provider `imageToVideo` attualmente dichiarati ma saltati nella sweep condivisa:
    - `vydra` perché il `veo3` integrato è solo testuale e il `kling` integrato richiede un URL immagine remoto
  - Copertura specifica provider per Vydra:
    - `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_VYDRA_VIDEO=1 pnpm test:live -- extensions/vydra/vydra.live.test.ts`
    - quel file esegue `veo3` text-to-video più una corsia `kling` che usa per impostazione predefinita una fixture con URL immagine remoto
  - Copertura live attuale `videoToVideo`:
    - solo `runway` quando il modello selezionato è `runway/gen4_aleph`
  - Provider `videoToVideo` attualmente dichiarati ma saltati nella sweep condivisa:
    - `alibaba`, `qwen`, `xai` perché quei percorsi richiedono attualmente URL di riferimento remoti `http(s)` / MP4
    - `google` perché l’attuale corsia condivisa Gemini/Veo usa input locale buffer-backed e quel percorso non è accettato nella sweep condivisa
    - `openai` perché l’attuale corsia condivisa non garantisce l’accesso specifico dell’organizzazione al video inpaint/remix
- Restrizione facoltativa:
  - `OPENCLAW_LIVE_VIDEO_GENERATION_PROVIDERS="google,openai,runway"`
  - `OPENCLAW_LIVE_VIDEO_GENERATION_MODELS="google/veo-3.1-fast-generate-preview,openai/sora-2,runway/gen4_aleph"`
  - `OPENCLAW_LIVE_VIDEO_GENERATION_SKIP_PROVIDERS=""` per includere ogni provider nella sweep predefinita, incluso FAL
  - `OPENCLAW_LIVE_VIDEO_GENERATION_TIMEOUT_MS=60000` per ridurre il limite operativo di ciascun provider in una smoke run aggressiva
- Comportamento auth facoltativo:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` per forzare l’auth dallo store profili e ignorare gli override solo-env

## Harness live media

- Comando: `pnpm test:live:media`
- Scopo:
  - Esegue le suite live condivise di immagini, musica e video tramite un unico entrypoint nativo del repository
  - Carica automaticamente le variabili env mancanti del provider da `~/.profile`
  - Restringe automaticamente ogni suite, per impostazione predefinita, ai provider che al momento hanno auth utilizzabile
  - Riutilizza `scripts/test-live.mjs`, così il comportamento heartbeat e quiet-mode resta coerente
- Esempi:
  - `pnpm test:live:media`
  - `pnpm test:live:media image video --providers openai,google,minimax`
  - `pnpm test:live:media video --video-providers openai,runway --all-providers`
  - `pnpm test:live:media music --quiet`

## Runner Docker (verifiche facoltative “funziona su Linux”)

Questi runner Docker sono divisi in due gruppi:

- Runner live-model: `test:docker:live-models` e `test:docker:live-gateway` eseguono solo il rispettivo file live con chiavi profilo dentro l’immagine Docker del repository (`src/agents/models.profiles.live.test.ts` e `src/gateway/gateway-models.profiles.live.test.ts`), montando la directory di configurazione locale e il workspace (e leggendo `~/.profile` se montato). Gli entrypoint locali corrispondenti sono `test:live:models-profiles` e `test:live:gateway-profiles`.
- I runner Docker live usano per impostazione predefinita un limite smoke più piccolo così una sweep Docker completa resta pratica:
  `test:docker:live-models` usa per impostazione predefinita `OPENCLAW_LIVE_MAX_MODELS=12`, e
  `test:docker:live-gateway` usa per impostazione predefinita `OPENCLAW_LIVE_GATEWAY_SMOKE=1`,
  `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=8`,
  `OPENCLAW_LIVE_GATEWAY_STEP_TIMEOUT_MS=45000` e
  `OPENCLAW_LIVE_GATEWAY_MODEL_TIMEOUT_MS=90000`. Sostituisci queste variabili env quando
  vuoi esplicitamente la scansione esaustiva più ampia.
- `test:docker:all` costruisce una volta l’immagine Docker live tramite `test:docker:live-build`, poi la riutilizza per le due corsie Docker live.
- Runner smoke del container: `test:docker:openwebui`, `test:docker:onboard`, `test:docker:gateway-network`, `test:docker:mcp-channels` e `test:docker:plugins` avviano uno o più container reali e verificano percorsi di integrazione di livello più alto.

I runner Docker live-model montano inoltre in bind solo le home auth CLI necessarie (oppure tutte quelle supportate quando l’esecuzione non è ristretta), poi le copiano nella home del container prima dell’esecuzione così l’OAuth delle CLI esterne può aggiornare i token senza modificare lo store auth dell’host:

- Modelli direct: `pnpm test:docker:live-models` (script: `scripts/test-live-models-docker.sh`)
- Smoke ACP bind: `pnpm test:docker:live-acp-bind` (script: `scripts/test-live-acp-bind-docker.sh`)
- Smoke backend CLI: `pnpm test:docker:live-cli-backend` (script: `scripts/test-live-cli-backend-docker.sh`)
- Smoke harness app-server Codex: `pnpm test:docker:live-codex-harness` (script: `scripts/test-live-codex-harness-docker.sh`)
- Gateway + agent dev: `pnpm test:docker:live-gateway` (script: `scripts/test-live-gateway-models-docker.sh`)
- Smoke live Open WebUI: `pnpm test:docker:openwebui` (script: `scripts/e2e/openwebui-docker.sh`)
- Procedura guidata di onboarding (TTY, scaffolding completo): `pnpm test:docker:onboard` (script: `scripts/e2e/onboard-docker.sh`)
- Networking del Gateway (due container, autenticazione WS + health): `pnpm test:docker:gateway-network` (script: `scripts/e2e/gateway-network-docker.sh`)
- Bridge channel MCP (Gateway seeded + bridge stdio + smoke raw del frame di notifica Claude): `pnpm test:docker:mcp-channels` (script: `scripts/e2e/mcp-channels-docker.sh`)
- Plugin (smoke di installazione + alias `/plugin` + semantica di riavvio del bundle Claude): `pnpm test:docker:plugins` (script: `scripts/e2e/plugins-docker.sh`)

I runner Docker live-model montano inoltre il checkout corrente in sola lettura e
lo preparano in una workdir temporanea dentro il container. Questo mantiene snella l’immagine
runtime pur eseguendo Vitest contro l’esatta sorgente/configurazione locale.
Il passaggio di staging salta grandi cache solo locali e output di build dell’app come
`.pnpm-store`, `.worktrees`, `__openclaw_vitest__` e directory `.build` locali dell’app o
output Gradle, così le esecuzioni live Docker non passano minuti a copiare
artifact specifici della macchina.
Impostano anche `OPENCLAW_SKIP_CHANNELS=1` così le sonde live del Gateway non avviano
veri worker di channel Telegram/Discord/ecc. dentro il container.
`test:docker:live-models` esegue comunque `pnpm test:live`, quindi fai passare anche
`OPENCLAW_LIVE_GATEWAY_*` quando devi restringere o escludere la copertura live
Gateway da quella corsia Docker.
`test:docker:openwebui` è uno smoke di compatibilità di livello più alto: avvia un
container Gateway OpenClaw con gli endpoint HTTP compatibili OpenAI abilitati,
avvia un container Open WebUI fissato contro quel Gateway, esegue il sign-in tramite
Open WebUI, verifica che `/api/models` esponga `openclaw/default`, quindi invia una
vera richiesta chat tramite il proxy `/api/chat/completions` di Open WebUI.
La prima esecuzione può essere sensibilmente più lenta perché Docker potrebbe dover scaricare
l’immagine Open WebUI e Open WebUI potrebbe dover completare il proprio cold start.
Questa corsia si aspetta una chiave di modello live utilizzabile, e `OPENCLAW_PROFILE_FILE`
(`~/.profile` per impostazione predefinita) è il modo principale per fornirla nelle esecuzioni Docker.
Le esecuzioni riuscite stampano un piccolo payload JSON come `{ "ok": true, "model":
"openclaw/default", ... }`.
`test:docker:mcp-channels` è intenzionalmente deterministico e non richiede un
vero account Telegram, Discord o iMessage. Avvia un container Gateway seeded,
avvia un secondo container che esegue `openclaw mcp serve`, quindi
verifica discovery delle conversazioni instradate, letture del transcript, metadati degli allegati,
comportamento della coda eventi live, instradamento dell’invio in uscita e notifiche di channel +
permessi in stile Claude sul vero bridge stdio MCP. Il controllo delle notifiche
ispeziona direttamente i frame raw stdio MCP così lo smoke valida ciò che il
bridge emette davvero, non solo ciò che un particolare SDK client espone.

Smoke manuale ACP del thread in linguaggio semplice (non CI):

- `bun scripts/dev/discord-acp-plain-language-smoke.ts --channel <discord-channel-id> ...`
- Mantieni questo script per flussi di regressione/debug. Potrebbe servire di nuovo per la validazione del routing dei thread ACP, quindi non eliminarlo.

Variabili env utili:

- `OPENCLAW_CONFIG_DIR=...` (predefinita: `~/.openclaw`) montata su `/home/node/.openclaw`
- `OPENCLAW_WORKSPACE_DIR=...` (predefinita: `~/.openclaw/workspace`) montata su `/home/node/.openclaw/workspace`
- `OPENCLAW_PROFILE_FILE=...` (predefinita: `~/.profile`) montata su `/home/node/.profile` e letta prima di eseguire i test
- `OPENCLAW_DOCKER_PROFILE_ENV_ONLY=1` per verificare solo le variabili env lette da `OPENCLAW_PROFILE_FILE`, usando directory config/workspace temporanee e nessun mount auth CLI esterno
- `OPENCLAW_DOCKER_CLI_TOOLS_DIR=...` (predefinita: `~/.cache/openclaw/docker-cli-tools`) montata su `/home/node/.npm-global` per installazioni CLI in cache dentro Docker
- Directory/file auth CLI esterni sotto `$HOME` vengono montati in sola lettura sotto `/host-auth...`, poi copiati in `/home/node/...` prima dell’avvio dei test
  - Directory predefinite: `.minimax`
  - File predefiniti: `~/.codex/auth.json`, `~/.codex/config.toml`, `.claude.json`, `~/.claude/.credentials.json`, `~/.claude/settings.json`, `~/.claude/settings.local.json`
  - Le esecuzioni con provider ristretto montano solo le directory/file necessari dedotti da `OPENCLAW_LIVE_PROVIDERS` / `OPENCLAW_LIVE_GATEWAY_PROVIDERS`
  - Override manuale con `OPENCLAW_DOCKER_AUTH_DIRS=all`, `OPENCLAW_DOCKER_AUTH_DIRS=none` o una lista separata da virgole come `OPENCLAW_DOCKER_AUTH_DIRS=.claude,.codex`
- `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...` per restringere l’esecuzione
- `OPENCLAW_LIVE_GATEWAY_PROVIDERS=...` / `OPENCLAW_LIVE_PROVIDERS=...` per filtrare i provider nel container
- `OPENCLAW_SKIP_DOCKER_BUILD=1` per riutilizzare un’immagine `openclaw:local-live` esistente per riesecuzioni che non richiedono una ricostruzione
- `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` per assicurare che le credenziali provengano dallo store profili (non dall’env)
- `OPENCLAW_OPENWEBUI_MODEL=...` per scegliere il modello esposto dal Gateway per lo smoke Open WebUI
- `OPENCLAW_OPENWEBUI_PROMPT=...` per sostituire il prompt di controllo nonce usato dallo smoke Open WebUI
- `OPENWEBUI_IMAGE=...` per sostituire il tag immagine Open WebUI fissato

## Verifica rapida della documentazione

Esegui i controlli documentazione dopo modifiche ai documenti: `pnpm check:docs`.
Esegui la validazione completa degli anchor Mintlify quando ti servono anche i controlli sugli heading nella pagina: `pnpm docs:check-links:anchors`.

## Regressione offline (sicura per CI)

Queste sono regressioni di “pipeline reale” senza provider reali:

- Tool calling del Gateway (mock OpenAI, vero loop Gateway + agent): `src/gateway/gateway.test.ts` (caso: "runs a mock OpenAI tool call end-to-end via gateway agent loop")
- Wizard del Gateway (WS `wizard.start`/`wizard.next`, scrive config + auth applicata): `src/gateway/gateway.test.ts` (caso: "runs wizard over ws and writes auth token config")

## Valutazioni di affidabilità dell’agent (Skills)

Abbiamo già alcuni test sicuri per CI che si comportano come “valutazioni di affidabilità dell’agent”:

- Tool-calling simulato tramite il vero loop Gateway + agent (`src/gateway/gateway.test.ts`).
- Flussi wizard end-to-end che validano il wiring della sessione e gli effetti sulla configurazione (`src/gateway/gateway.test.ts`).

Cosa manca ancora per Skills (vedi [Skills](/it/tools/skills)):

- **Decisioning:** quando le Skills sono elencate nel prompt, l’agent sceglie la skill giusta (o evita quelle irrilevanti)?
- **Compliance:** l’agent legge `SKILL.md` prima dell’uso e segue i passaggi/argomenti richiesti?
- **Workflow contracts:** scenari multi-turno che verificano ordine dei tool, mantenimento della cronologia di sessione e boundary del sandbox.

Le valutazioni future dovrebbero restare prima di tutto deterministiche:

- Un runner di scenari che usi provider mock per verificare tool call + ordine, lettura dei file skill e wiring della sessione.
- Una piccola suite di scenari focalizzati sulle skill (usare vs evitare, gating, prompt injection).
- Valutazioni live facoltative (opt-in, protette da env) solo dopo che la suite sicura per CI è in posto.

## Test di contratto (forma di plugin e channel)

I test di contratto verificano che ogni plugin e channel registrato sia conforme al
proprio contratto di interfaccia. Iterano su tutti i plugin individuati ed eseguono una suite di
asserzioni su forma e comportamento. La corsia unitaria predefinita `pnpm test`
salta intenzionalmente questi file condivisi di seam e smoke; esegui i comandi di contratto in modo esplicito
quando tocchi superfici condivise di channel o provider.

### Comandi

- Tutti i contratti: `pnpm test:contracts`
- Solo contratti channel: `pnpm test:contracts:channels`
- Solo contratti provider: `pnpm test:contracts:plugins`

### Contratti channel

Si trovano in `src/channels/plugins/contracts/*.contract.test.ts`:

- **plugin** - Forma base del plugin (id, nome, capability)
- **setup** - Contratto della procedura guidata di setup
- **session-binding** - Comportamento di associazione della sessione
- **outbound-payload** - Struttura del payload del messaggio
- **inbound** - Gestione dei messaggi in ingresso
- **actions** - Handler delle azioni del channel
- **threading** - Gestione degli id del thread
- **directory** - API di directory/roster
- **group-policy** - Applicazione della policy di gruppo

### Contratti di stato del provider

Si trovano in `src/plugins/contracts/*.contract.test.ts`.

- **status** - Sonde di stato del channel
- **registry** - Forma del registry del plugin

### Contratti provider

Si trovano in `src/plugins/contracts/*.contract.test.ts`:

- **auth** - Contratto del flusso auth
- **auth-choice** - Scelta/selezione auth
- **catalog** - API del catalogo modelli
- **discovery** - Discovery del plugin
- **loader** - Caricamento del plugin
- **runtime** - Runtime del provider
- **shape** - Forma/interfaccia del plugin
- **wizard** - Procedura guidata di setup

### Quando eseguirli

- Dopo aver modificato export o subpath di plugin-sdk
- Dopo aver aggiunto o modificato un plugin channel o provider
- Dopo aver rifattorizzato registrazione o discovery dei plugin

I test di contratto vengono eseguiti in CI e non richiedono chiavi API reali.

## Aggiunta di regressioni (linee guida)

Quando correggi un problema di provider/modello scoperto in live:

- Aggiungi una regressione sicura per CI se possibile (provider mock/stub, oppure cattura l’esatta trasformazione della forma della richiesta)
- Se è intrinsecamente solo-live (rate limit, policy auth), mantieni il test live ristretto e opt-in tramite variabili env
- Preferisci colpire il livello più piccolo che intercetta il bug:
  - bug di conversione/replay della richiesta del provider → test direct models
  - bug della pipeline sessione/cronologia/tool del Gateway → Gateway live smoke o test mock Gateway sicuro per CI
- Guardrail sull’attraversamento di SecretRef:
  - `src/secrets/exec-secret-ref-id-parity.test.ts` deriva un target campionato per classe SecretRef dai metadati del registry (`listSecretTargetRegistryEntries()`), poi verifica che gli id exec dei segmenti di attraversamento vengano rifiutati.
  - Se aggiungi una nuova famiglia di target SecretRef `includeInPlan` in `src/secrets/target-registry-data.ts`, aggiorna `classifyTargetClass` in quel test. Il test fallisce intenzionalmente sugli id target non classificati così le nuove classi non possono essere saltate in silenzio.
