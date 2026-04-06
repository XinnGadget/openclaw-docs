---
read_when:
    - Devi sapere da quale sottopercorso dell'SDK importare
    - Vuoi un riferimento per tutti i metodi di registrazione su OpenClawPluginApi
    - Stai cercando una specifica esportazione dell'SDK
sidebarTitle: SDK Overview
summary: Mappa di importazione, riferimento dell'API di registrazione e architettura dell'SDK
title: Panoramica dell'SDK plugin
x-i18n:
    generated_at: "2026-04-06T08:16:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: acd2887ef52c66b2f234858d812bb04197ecd0bfb3e4f7bf3622f8fdc765acad
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# Panoramica dell'SDK plugin

L'SDK plugin è il contratto tipizzato tra i plugin e il core. Questa pagina è il
riferimento per **cosa importare** e **cosa è possibile registrare**.

<Tip>
  **Cerchi una guida pratica?**
  - Primo plugin? Inizia con [Introduzione](/it/plugins/building-plugins)
  - Plugin di canale? Vedi [Plugin di canale](/it/plugins/sdk-channel-plugins)
  - Plugin provider? Vedi [Plugin provider](/it/plugins/sdk-provider-plugins)
</Tip>

## Convenzione di importazione

Importa sempre da un sottopercorso specifico:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

Ogni sottopercorso è un modulo piccolo e autosufficiente. Questo mantiene
l'avvio rapido e previene i problemi di dipendenze circolari. Per gli helper di
entry/build specifici del canale, preferisci `openclaw/plugin-sdk/channel-core`;
mantieni `openclaw/plugin-sdk/core` per la superficie ombrello più ampia e per
gli helper condivisi come `buildChannelConfigSchema`.

Non aggiungere né dipendere da seam di convenienza con nome del provider come
`openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp` o
seam di helper a marchio di canale. I plugin inclusi dovrebbero comporre
sottopercorsi SDK generici all'interno dei propri barrel `api.ts` o `runtime-api.ts`, e il core
dovrebbe usare quei barrel locali al plugin oppure aggiungere un contratto SDK
generico e ristretto quando l'esigenza è davvero trasversale ai canali.

La mappa di esportazione generata contiene ancora un piccolo insieme di
seam helper per plugin inclusi come `plugin-sdk/feishu`, `plugin-sdk/feishu-setup`,
`plugin-sdk/zalo`, `plugin-sdk/zalo-setup` e `plugin-sdk/matrix*`. Questi
sottopercorsi esistono solo per la manutenzione e la compatibilità dei plugin inclusi;
sono intenzionalmente omessi dalla tabella comune qui sotto e non sono il
percorso di importazione consigliato per nuovi plugin di terze parti.

## Riferimento dei sottopercorsi

I sottopercorsi più comunemente usati, raggruppati per scopo. L'elenco completo
generato di oltre 200 sottopercorsi si trova in `scripts/lib/plugin-sdk-entrypoints.json`.

I sottopercorsi helper riservati per plugin inclusi compaiono ancora in
quell'elenco generato. Trattali come superfici di dettaglio implementativo/compatibilità
a meno che una pagina della documentazione non ne promuova esplicitamente uno come pubblico.

### Entry del plugin

| Sottopercorso              | Esportazioni chiave                                                                                                                    |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/plugin-entry`   | `definePluginEntry`                                                                                                                    |
| `plugin-sdk/core`           | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema`  | `OpenClawSchema`                                                                                                                       |
| `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry`                                                                                                      |

<AccordionGroup>
  <Accordion title="Sottopercorsi del canale">
    | Sottopercorso | Esportazioni chiave |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | Esportazione dello schema Zod radice `openclaw.json` (`OpenClawSchema`) |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, oltre a `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | Helper condivisi per il wizard di configurazione, prompt per allowlist, builder dello stato della configurazione |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | Helper di config/action-gate multi-account e helper di fallback per account predefinito |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`, helper di normalizzazione dell'ID account |
    | `plugin-sdk/account-resolution` | Helper di ricerca account + fallback predefinito |
    | `plugin-sdk/account-helpers` | Helper ristretti per elenco account/azioni account |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | Tipi di schema della configurazione del canale |
    | `plugin-sdk/telegram-command-config` | Helper di normalizzazione/validazione dei comandi personalizzati di Telegram con fallback al contratto incluso |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | Helper condivisi di instradamento in ingresso + builder di envelope |
    | `plugin-sdk/inbound-reply-dispatch` | Helper condivisi di registrazione e dispatch in ingresso |
    | `plugin-sdk/messaging-targets` | Helper di parsing/corrispondenza dei target |
    | `plugin-sdk/outbound-media` | Helper condivisi di caricamento dei media in uscita |
    | `plugin-sdk/outbound-runtime` | Helper di delega per identità/invio in uscita |
    | `plugin-sdk/thread-bindings-runtime` | Helper di lifecycle e adapter per thread-binding |
    | `plugin-sdk/agent-media-payload` | Builder legacy del payload media dell'agente |
    | `plugin-sdk/conversation-runtime` | Helper per binding conversazione/thread, pairing e binding configurato |
    | `plugin-sdk/runtime-config-snapshot` | Helper per snapshot della config runtime |
    | `plugin-sdk/runtime-group-policy` | Helper runtime per la risoluzione delle policy di gruppo |
    | `plugin-sdk/channel-status` | Helper condivisi per snapshot/riepilogo dello stato del canale |
    | `plugin-sdk/channel-config-primitives` | Primitive ristrette per lo schema di configurazione del canale |
    | `plugin-sdk/channel-config-writes` | Helper di autorizzazione per la scrittura della configurazione del canale |
    | `plugin-sdk/channel-plugin-common` | Esportazioni prelude condivise del plugin di canale |
    | `plugin-sdk/allowlist-config-edit` | Helper di modifica/lettura della configurazione dell'allowlist |
    | `plugin-sdk/group-access` | Helper condivisi per le decisioni di accesso ai gruppi |
    | `plugin-sdk/direct-dm` | Helper condivisi di autenticazione/protezione direct-DM |
    | `plugin-sdk/interactive-runtime` | Helper di normalizzazione/riduzione del payload di risposta interattiva |
    | `plugin-sdk/channel-inbound` | Debounce, corrispondenza delle menzioni, helper di envelope |
    | `plugin-sdk/channel-send-result` | Tipi del risultato di risposta |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | Helper di parsing/corrispondenza dei target |
    | `plugin-sdk/channel-contract` | Tipi del contratto del canale |
    | `plugin-sdk/channel-feedback` | Wiring di feedback/reazioni |
  </Accordion>

  <Accordion title="Sottopercorsi provider">
    | Sottopercorso | Esportazioni chiave |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | Helper selezionati di configurazione del provider locale/self-hosted |
    | `plugin-sdk/self-hosted-provider-setup` | Helper focalizzati di configurazione del provider self-hosted compatibile con OpenAI |
    | `plugin-sdk/provider-auth-runtime` | Helper runtime di risoluzione della chiave API per plugin provider |
    | `plugin-sdk/provider-auth-api-key` | Helper di onboarding/scrittura profilo per chiavi API |
    | `plugin-sdk/provider-auth-result` | Builder standard del risultato di autenticazione OAuth |
    | `plugin-sdk/provider-auth-login` | Helper condivisi di login interattivo per plugin provider |
    | `plugin-sdk/provider-env-vars` | Helper di ricerca delle variabili d'ambiente di autenticazione del provider |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, builder condivisi di replay-policy, helper per endpoint provider e helper di normalizzazione dell'ID modello come `normalizeNativeXaiModelId` |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | Helper generici di capacità HTTP/endpoint del provider |
    | `plugin-sdk/provider-web-fetch` | Helper di registrazione/cache del provider web-fetch |
    | `plugin-sdk/provider-web-search` | Helper di registrazione/cache/config del provider web-search |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, cleanup + diagnostica dello schema Gemini e helper di compatibilità xAI come `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` e simili |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, tipi di stream wrapper e helper wrapper condivisi per Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
    | `plugin-sdk/provider-onboard` | Helper di patch della configurazione di onboarding |
    | `plugin-sdk/global-singleton` | Helper di singleton/map/cache locali al processo |
  </Accordion>

  <Accordion title="Sottopercorsi di autenticazione e sicurezza">
    | Sottopercorso | Esportazioni chiave |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`, helper del registro comandi, helper di autorizzazione del mittente |
    | `plugin-sdk/approval-auth-runtime` | Risoluzione dell'approvatore e helper di action-auth nella stessa chat |
    | `plugin-sdk/approval-client-runtime` | Helper nativi per profilo/filtro di approvazione exec |
    | `plugin-sdk/approval-delivery-runtime` | Adapter nativi per capacità/consegna dell'approvazione |
    | `plugin-sdk/approval-native-runtime` | Helper nativi per target di approvazione + binding account |
    | `plugin-sdk/approval-reply-runtime` | Helper per il payload di risposta di approvazione exec/plugin |
    | `plugin-sdk/command-auth-native` | Autenticazione nativa dei comandi + helper nativi per target di sessione |
    | `plugin-sdk/command-detection` | Helper condivisi per il rilevamento dei comandi |
    | `plugin-sdk/command-surface` | Normalizzazione del corpo del comando e helper della superficie dei comandi |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/security-runtime` | Helper condivisi per trust, gating DM, contenuto esterno e raccolta di secret |
    | `plugin-sdk/ssrf-policy` | Helper di policy SSRF per allowlist host e reti private |
    | `plugin-sdk/ssrf-runtime` | Helper per pinned-dispatcher, fetch protetto da SSRF e policy SSRF |
    | `plugin-sdk/secret-input` | Helper di parsing degli input secret |
    | `plugin-sdk/webhook-ingress` | Helper per richieste/target webhook |
    | `plugin-sdk/webhook-request-guards` | Helper per dimensione body/timeout della richiesta |
  </Accordion>

  <Accordion title="Sottopercorsi runtime e storage">
    | Sottopercorso | Esportazioni chiave |
    | --- | --- |
    | `plugin-sdk/runtime` | Ampi helper di runtime/logging/backup/installazione plugin |
    | `plugin-sdk/runtime-env` | Helper ristretti per env runtime, logger, timeout, retry e backoff |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | Helper condivisi per comandi/hook/http/interattività del plugin |
    | `plugin-sdk/hook-runtime` | Helper condivisi per la pipeline di webhook/hook interni |
    | `plugin-sdk/lazy-runtime` | Helper di importazione/binding runtime lazy come `createLazyRuntimeModule`, `createLazyRuntimeMethod` e `createLazyRuntimeSurface` |
    | `plugin-sdk/process-runtime` | Helper di esecuzione dei processi |
    | `plugin-sdk/cli-runtime` | Helper CLI di formattazione, attesa e versione |
    | `plugin-sdk/gateway-runtime` | Helper del client gateway e di patch dello stato del canale |
    | `plugin-sdk/config-runtime` | Helper di caricamento/scrittura della configurazione |
    | `plugin-sdk/telegram-command-config` | Normalizzazione di nome/descrizione del comando Telegram e controlli di duplicati/conflitti, anche quando la superficie contrattuale Telegram inclusa non è disponibile |
    | `plugin-sdk/approval-runtime` | Helper di approvazione exec/plugin, builder di capacità di approvazione, helper di autenticazione/profilo, helper nativi di instradamento/runtime |
    | `plugin-sdk/reply-runtime` | Helper condivisi di runtime inbound/reply, chunking, dispatch, heartbeat, pianificatore di risposte |
    | `plugin-sdk/reply-dispatch-runtime` | Helper ristretti per dispatch/finalizzazione della risposta |
    | `plugin-sdk/reply-history` | Helper condivisi per la cronologia delle risposte a breve finestra come `buildHistoryContext`, `recordPendingHistoryEntry` e `clearHistoryEntriesIfEnabled` |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | Helper ristretti per chunking di testo/markdown |
    | `plugin-sdk/session-store-runtime` | Helper per percorso dello store di sessione + updated-at |
    | `plugin-sdk/state-paths` | Helper di percorso per directory di stato/OAuth |
    | `plugin-sdk/routing` | Helper per route/session-key/binding account come `resolveAgentRoute`, `buildAgentSessionKey` e `resolveDefaultAgentBoundAccountId` |
    | `plugin-sdk/status-helpers` | Helper condivisi per il riepilogo dello stato di canale/account, valori predefiniti dello stato runtime e helper dei metadati dei problemi |
    | `plugin-sdk/target-resolver-runtime` | Helper condivisi per la risoluzione dei target |
    | `plugin-sdk/string-normalization-runtime` | Helper di normalizzazione slug/stringhe |
    | `plugin-sdk/request-url` | Estrae URL stringa da input simili a fetch/richiesta |
    | `plugin-sdk/run-command` | Runner di comandi con timing e risultati stdout/stderr normalizzati |
    | `plugin-sdk/param-readers` | Lettori comuni di parametri per tool/CLI |
    | `plugin-sdk/tool-send` | Estrae i campi del target di invio canonico dagli argomenti del tool |
    | `plugin-sdk/temp-path` | Helper condivisi per percorsi temporanei di download |
    | `plugin-sdk/logging-core` | Helper di logger del sottosistema e redazione |
    | `plugin-sdk/markdown-table-runtime` | Helper per la modalità tabella Markdown |
    | `plugin-sdk/json-store` | Piccoli helper di lettura/scrittura dello stato JSON |
    | `plugin-sdk/file-lock` | Helper di file-lock rientrante |
    | `plugin-sdk/persistent-dedupe` | Helper di cache dedupe persistente su disco |
    | `plugin-sdk/acp-runtime` | Helper di runtime/sessione ACP e reply-dispatch |
    | `plugin-sdk/agent-config-primitives` | Primitive ristrette per lo schema di configurazione runtime dell'agente |
    | `plugin-sdk/boolean-param` | Lettore permissivo di parametri booleani |
    | `plugin-sdk/dangerous-name-runtime` | Helper di risoluzione per la corrispondenza di nomi pericolosi |
    | `plugin-sdk/device-bootstrap` | Helper per bootstrap del dispositivo e token di pairing |
    | `plugin-sdk/extension-shared` | Primitive condivise per canali passivi e helper di stato |
    | `plugin-sdk/models-provider-runtime` | Helper di risposta per comando `/models`/provider |
    | `plugin-sdk/skill-commands-runtime` | Helper per l'elenco dei comandi di Skills |
    | `plugin-sdk/native-command-registry` | Helper nativi di registro/build/serializzazione dei comandi |
    | `plugin-sdk/provider-zai-endpoint` | Helper di rilevamento endpoint Z.AI |
    | `plugin-sdk/infra-runtime` | Helper di eventi di sistema/heartbeat |
    | `plugin-sdk/collection-runtime` | Piccoli helper di cache limitata |
    | `plugin-sdk/diagnostic-runtime` | Helper di flag ed eventi diagnostici |
    | `plugin-sdk/error-runtime` | Grafo degli errori, formattazione, helper condivisi di classificazione degli errori, `isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | Helper per fetch incapsulato, proxy e ricerca pinned |
    | `plugin-sdk/host-runtime` | Helper di normalizzazione hostname e host SCP |
    | `plugin-sdk/retry-runtime` | Helper di configurazione retry ed esecuzione retry |
    | `plugin-sdk/agent-runtime` | Helper per directory/identità/workspace dell'agente |
    | `plugin-sdk/directory-runtime` | Query/dedup di directory basata su config |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="Sottopercorsi di capacità e test">
    | Sottopercorso | Esportazioni chiave |
    | --- | --- |
    | `plugin-sdk/media-runtime` | Helper condivisi per fetch/transform/store dei media più builder di payload media |
    | `plugin-sdk/media-generation-runtime` | Helper condivisi per failover della generazione media, selezione candidati e messaggistica per modelli mancanti |
    | `plugin-sdk/media-understanding` | Tipi provider per media understanding più esportazioni helper orientate al provider per immagini/audio |
    | `plugin-sdk/text-runtime` | Helper condivisi per testo/markdown/logging come rimozione del testo visibile all'assistente, helper di render/chunking/tabella Markdown, helper di redazione, helper di directive-tag e utility di testo sicuro |
    | `plugin-sdk/text-chunking` | Helper per chunking del testo in uscita |
    | `plugin-sdk/speech` | Tipi provider speech più helper orientati al provider per directive, registro e validazione |
    | `plugin-sdk/speech-core` | Tipi provider speech condivisi, helper di registro, directive e normalizzazione |
    | `plugin-sdk/realtime-transcription` | Tipi provider di trascrizione realtime e helper di registro |
    | `plugin-sdk/realtime-voice` | Tipi provider di voce realtime e helper di registro |
    | `plugin-sdk/image-generation` | Tipi provider di generazione immagini |
    | `plugin-sdk/image-generation-core` | Tipi condivisi di generazione immagini, helper di failover, autenticazione e registro |
    | `plugin-sdk/music-generation` | Tipi provider/richiesta/risultato per generazione musicale |
    | `plugin-sdk/music-generation-core` | Tipi condivisi di generazione musicale, helper di failover, ricerca provider e parsing model-ref |
    | `plugin-sdk/video-generation` | Tipi provider/richiesta/risultato per generazione video |
    | `plugin-sdk/video-generation-core` | Tipi condivisi di generazione video, helper di failover, ricerca provider e parsing model-ref |
    | `plugin-sdk/webhook-targets` | Registro dei target webhook e helper di installazione route |
    | `plugin-sdk/webhook-path` | Helper di normalizzazione del percorso webhook |
    | `plugin-sdk/web-media` | Helper condivisi di caricamento media remoti/locali |
    | `plugin-sdk/zod` | `zod` riesportato per i consumatori dell'SDK plugin |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="Sottopercorsi memory">
    | Sottopercorso | Esportazioni chiave |
    | --- | --- |
    | `plugin-sdk/memory-core` | Superficie helper `memory-core` inclusa per helper di manager/config/file/CLI |
    | `plugin-sdk/memory-core-engine-runtime` | Facade runtime di indice/ricerca memory |
    | `plugin-sdk/memory-core-host-engine-foundation` | Esportazioni del motore foundation host memory |
    | `plugin-sdk/memory-core-host-engine-embeddings` | Esportazioni del motore embedding host memory |
    | `plugin-sdk/memory-core-host-engine-qmd` | Esportazioni del motore QMD host memory |
    | `plugin-sdk/memory-core-host-engine-storage` | Esportazioni del motore storage host memory |
    | `plugin-sdk/memory-core-host-multimodal` | Helper multimodali host memory |
    | `plugin-sdk/memory-core-host-query` | Helper query host memory |
    | `plugin-sdk/memory-core-host-secret` | Helper secret host memory |
    | `plugin-sdk/memory-core-host-events` | Helper journal degli eventi host memory |
    | `plugin-sdk/memory-core-host-status` | Helper di stato host memory |
    | `plugin-sdk/memory-core-host-runtime-cli` | Helper runtime CLI host memory |
    | `plugin-sdk/memory-core-host-runtime-core` | Helper runtime core host memory |
    | `plugin-sdk/memory-core-host-runtime-files` | Helper file/runtime host memory |
    | `plugin-sdk/memory-host-core` | Alias neutrale rispetto al vendor per helper runtime core host memory |
    | `plugin-sdk/memory-host-events` | Alias neutrale rispetto al vendor per helper journal degli eventi host memory |
    | `plugin-sdk/memory-host-files` | Alias neutrale rispetto al vendor per helper file/runtime host memory |
    | `plugin-sdk/memory-host-markdown` | Helper condivisi di markdown gestito per plugin adiacenti a memory |
    | `plugin-sdk/memory-host-search` | Facade runtime della memory attiva per l'accesso al search-manager |
    | `plugin-sdk/memory-host-status` | Alias neutrale rispetto al vendor per helper di stato host memory |
    | `plugin-sdk/memory-lancedb` | Superficie helper `memory-lancedb` inclusa |
  </Accordion>

  <Accordion title="Sottopercorsi helper inclusi riservati">
    | Famiglia | Sottopercorsi attuali | Uso previsto |
    | --- | --- | --- |
    | Browser | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | Helper di supporto per il plugin browser incluso (`browser-support` rimane il barrel di compatibilità) |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | Superficie helper/runtime Matrix inclusa |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | Superficie helper/runtime LINE inclusa |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | Superficie helper IRC inclusa |
    | Helper specifici del canale | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | Seam di compatibilità/helper per canali inclusi |
    | Helper specifici di auth/plugin | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | Seam helper per funzionalità/plugin inclusi; `plugin-sdk/github-copilot-token` esporta attualmente `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken` e `resolveCopilotApiToken` |
  </Accordion>
</AccordionGroup>

## API di registrazione

La callback `register(api)` riceve un oggetto `OpenClawPluginApi` con questi
metodi:

### Registrazione delle capacità

| Metodo                                           | Cosa registra                    |
| ------------------------------------------------ | -------------------------------- |
| `api.registerProvider(...)`                      | Inferenza del testo (LLM)        |
| `api.registerChannel(...)`                       | Canale di messaggistica          |
| `api.registerSpeechProvider(...)`                | Sintesi text-to-speech / STT     |
| `api.registerRealtimeTranscriptionProvider(...)` | Trascrizione realtime in streaming |
| `api.registerRealtimeVoiceProvider(...)`         | Sessioni vocali realtime duplex  |
| `api.registerMediaUnderstandingProvider(...)`    | Analisi di immagini/audio/video  |
| `api.registerImageGenerationProvider(...)`       | Generazione di immagini          |
| `api.registerMusicGenerationProvider(...)`       | Generazione musicale             |
| `api.registerVideoGenerationProvider(...)`       | Generazione video                |
| `api.registerWebFetchProvider(...)`              | Provider di web fetch / scrape   |
| `api.registerWebSearchProvider(...)`             | Ricerca web                      |

### Tool e comandi

| Metodo                          | Cosa registra                                |
| ------------------------------- | -------------------------------------------- |
| `api.registerTool(tool, opts?)` | Tool dell'agente (obbligatorio o `{ optional: true }`) |
| `api.registerCommand(def)`      | Comando personalizzato (bypassa l'LLM)       |

### Infrastruttura

| Metodo                                         | Cosa registra                          |
| ---------------------------------------------- | -------------------------------------- |
| `api.registerHook(events, handler, opts?)`     | Hook di evento                         |
| `api.registerHttpRoute(params)`                | Endpoint HTTP del gateway              |
| `api.registerGatewayMethod(name, handler)`     | Metodo RPC del gateway                 |
| `api.registerCli(registrar, opts?)`            | Sottocomando CLI                       |
| `api.registerService(service)`                 | Servizio in background                 |
| `api.registerInteractiveHandler(registration)` | Handler interattivo                    |
| `api.registerMemoryPromptSupplement(builder)`  | Sezione di prompt additiva adiacente a memory |
| `api.registerMemoryCorpusSupplement(adapter)`  | Corpus additivo di ricerca/lettura memory |

I namespace amministrativi del core riservati (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`) restano sempre `operator.admin`, anche se un plugin prova ad assegnare
uno scope più ristretto a un metodo gateway. Preferisci prefissi specifici del plugin per
i metodi di proprietà del plugin.

### Metadati di registrazione della CLI

`api.registerCli(registrar, opts?)` accetta due tipi di metadati di primo livello:

- `commands`: radici di comando esplicite possedute dal registrar
- `descriptors`: descrittori di comando in fase di parsing usati per l'help della CLI radice,
  l'instradamento e la registrazione lazy della CLI del plugin

Se vuoi che un comando del plugin resti caricato lazy nel normale percorso della CLI radice,
fornisci `descriptors` che coprano ogni radice di comando di primo livello esposta da quel
registrar.

```typescript
api.registerCli(
  async ({ program }) => {
    const { registerMatrixCli } = await import("./src/cli.js");
    registerMatrixCli({ program });
  },
  {
    descriptors: [
      {
        name: "matrix",
        description: "Gestisci account Matrix, verifica, dispositivi e stato del profilo",
        hasSubcommands: true,
      },
    ],
  },
);
```

Usa `commands` da solo solo quando non hai bisogno della registrazione lazy della CLI radice.
Questo percorso di compatibilità eager rimane supportato, ma non installa
placeholder basati su descriptor per il caricamento lazy in fase di parsing.

### Slot esclusivi

| Metodo                                     | Cosa registra                        |
| ------------------------------------------ | ------------------------------------ |
| `api.registerContextEngine(id, factory)`   | Motore di contesto (uno attivo alla volta) |
| `api.registerMemoryPromptSection(builder)` | Builder della sezione del prompt memory |
| `api.registerMemoryFlushPlan(resolver)`    | Resolver del piano di flush memory   |
| `api.registerMemoryRuntime(runtime)`       | Adapter runtime memory               |

### Adapter di embedding memory

| Metodo                                         | Cosa registra                                 |
| ---------------------------------------------- | --------------------------------------------- |
| `api.registerMemoryEmbeddingProvider(adapter)` | Adapter di embedding memory per il plugin attivo |

- `registerMemoryPromptSection`, `registerMemoryFlushPlan` e
  `registerMemoryRuntime` sono esclusivi dei plugin memory.
- `registerMemoryEmbeddingProvider` consente al plugin memory attivo di registrare
  uno o più ID di adapter di embedding (per esempio `openai`, `gemini` o un ID
  personalizzato definito dal plugin).
- La configurazione utente come `agents.defaults.memorySearch.provider` e
  `agents.defaults.memorySearch.fallback` viene risolta rispetto a quegli ID
  di adapter registrati.

### Eventi e lifecycle

| Metodo                                       | Cosa fa                    |
| -------------------------------------------- | -------------------------- |
| `api.on(hookName, handler, opts?)`           | Hook lifecycle tipizzato   |
| `api.onConversationBindingResolved(handler)` | Callback di binding della conversazione |

### Semantica delle decisioni degli hook

- `before_tool_call`: restituire `{ block: true }` è terminale. Una volta che un handler lo imposta, gli handler a priorità inferiore vengono saltati.
- `before_tool_call`: restituire `{ block: false }` viene trattato come nessuna decisione (come omettere `block`), non come override.
- `before_install`: restituire `{ block: true }` è terminale. Una volta che un handler lo imposta, gli handler a priorità inferiore vengono saltati.
- `before_install`: restituire `{ block: false }` viene trattato come nessuna decisione (come omettere `block`), non come override.
- `reply_dispatch`: restituire `{ handled: true, ... }` è terminale. Una volta che un handler rivendica il dispatch, gli handler a priorità inferiore e il percorso predefinito di dispatch del modello vengono saltati.
- `message_sending`: restituire `{ cancel: true }` è terminale. Una volta che un handler lo imposta, gli handler a priorità inferiore vengono saltati.
- `message_sending`: restituire `{ cancel: false }` viene trattato come nessuna decisione (come omettere `cancel`), non come override.

### Campi dell'oggetto API

| Campo                    | Tipo                      | Descrizione                                                                                 |
| ------------------------ | ------------------------- | ------------------------------------------------------------------------------------------- |
| `api.id`                 | `string`                  | ID del plugin                                                                               |
| `api.name`               | `string`                  | Nome visualizzato                                                                           |
| `api.version`            | `string?`                 | Versione del plugin (facoltativa)                                                           |
| `api.description`        | `string?`                 | Descrizione del plugin (facoltativa)                                                        |
| `api.source`             | `string`                  | Percorso sorgente del plugin                                                                |
| `api.rootDir`            | `string?`                 | Directory radice del plugin (facoltativa)                                                   |
| `api.config`             | `OpenClawConfig`          | Snapshot della configurazione corrente (snapshot runtime in memoria attivo quando disponibile) |
| `api.pluginConfig`       | `Record<string, unknown>` | Configurazione specifica del plugin da `plugins.entries.<id>.config`                        |
| `api.runtime`            | `PluginRuntime`           | [Helper runtime](/it/plugins/sdk-runtime)                                                      |
| `api.logger`             | `PluginLogger`            | Logger con scope (`debug`, `info`, `warn`, `error`)                                         |
| `api.registrationMode`   | `PluginRegistrationMode`  | Modalità di caricamento corrente; `"setup-runtime"` è la finestra leggera di avvio/configurazione prima della full-entry |
| `api.resolvePath(input)` | `(string) => string`      | Risolve un percorso relativo alla radice del plugin                                         |

## Convenzione dei moduli interni

All'interno del tuo plugin, usa file barrel locali per le importazioni interne:

```
my-plugin/
  api.ts            # Esportazioni pubbliche per i consumatori esterni
  runtime-api.ts    # Esportazioni runtime solo interne
  index.ts          # Punto di ingresso del plugin
  setup-entry.ts    # Entry leggera solo per la configurazione (facoltativa)
```

<Warning>
  Non importare mai il tuo stesso plugin tramite `openclaw/plugin-sdk/<your-plugin>`
  dal codice di produzione. Instrada le importazioni interne attraverso `./api.ts` o
  `./runtime-api.ts`. Il percorso SDK è solo il contratto esterno.
</Warning>

Le superfici pubbliche dei plugin inclusi caricate tramite facade (`api.ts`, `runtime-api.ts`,
`index.ts`, `setup-entry.ts` e file di entry pubblici simili) ora preferiscono lo
snapshot della configurazione runtime attivo quando OpenClaw è già in esecuzione. Se non esiste ancora
uno snapshot runtime, fanno fallback al file di configurazione risolto su disco.

Anche i plugin provider possono esporre un barrel contrattuale locale al plugin e ristretto quando un
helper è intenzionalmente specifico del provider e non appartiene ancora a un
sottopercorso SDK generico. Esempio incluso attuale: il provider Anthropic mantiene i suoi helper
di stream Claude nel proprio seam pubblico `api.ts` / `contract-api.ts` invece di
promuovere la logica dell'header beta Anthropic e `service_tier` in un contratto
generico `plugin-sdk/*`.

Altri esempi inclusi attuali:

- `@openclaw/openai-provider`: `api.ts` esporta builder di provider,
  helper di modelli predefiniti e builder di provider realtime
- `@openclaw/openrouter-provider`: `api.ts` esporta il builder del provider più
  helper di onboarding/configurazione

<Warning>
  Anche il codice di produzione delle estensioni dovrebbe evitare le importazioni
  `openclaw/plugin-sdk/<other-plugin>`. Se un helper è davvero condiviso, promuovilo a un sottopercorso SDK neutrale
  come `openclaw/plugin-sdk/speech`, `.../provider-model-shared` o un'altra
  superficie orientata alle capacità invece di accoppiare due plugin tra loro.
</Warning>

## Correlati

- [Punti di ingresso](/it/plugins/sdk-entrypoints) — opzioni di `definePluginEntry` e `defineChannelPluginEntry`
- [Helper runtime](/it/plugins/sdk-runtime) — riferimento completo dello spazio dei nomi `api.runtime`
- [Configurazione e config](/it/plugins/sdk-setup) — packaging, manifest, schemi di configurazione
- [Test](/it/plugins/sdk-testing) — utility di test e regole lint
- [Migrazione dell'SDK](/it/plugins/sdk-migration) — migrazione dalle superfici deprecate
- [Interni dei plugin](/it/plugins/architecture) — architettura approfondita e modello di capacità
