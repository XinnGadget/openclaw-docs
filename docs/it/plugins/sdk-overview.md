---
read_when:
    - Devi sapere da quale sottopercorso SDK importare
    - Vuoi un riferimento per tutti i metodi di registrazione su OpenClawPluginApi
    - Stai cercando un'esportazione SDK specifica
sidebarTitle: SDK Overview
summary: Mappa degli import, riferimento dell'API di registrazione e architettura dell'SDK
title: Panoramica del Plugin SDK
x-i18n:
    generated_at: "2026-04-08T02:17:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: c5a41bd82d165dfbb7fbd6e4528cf322e9133a51efe55fa8518a7a0a626d9d30
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# Panoramica del Plugin SDK

Il plugin SDK è il contratto tipizzato tra i plugin e il core. Questa pagina è il
riferimento per **cosa importare** e **cosa puoi registrare**.

<Tip>
  **Cerchi una guida pratica?**
  - Primo plugin? Inizia con [Getting Started](/it/plugins/building-plugins)
  - Plugin di canale? Vedi [Channel Plugins](/it/plugins/sdk-channel-plugins)
  - Plugin provider? Vedi [Provider Plugins](/it/plugins/sdk-provider-plugins)
</Tip>

## Convenzione di importazione

Importa sempre da un sottopercorso specifico:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

Ogni sottopercorso è un modulo piccolo e autosufficiente. Questo mantiene l'avvio rapido e
previene i problemi di dipendenze circolari. Per helper di entry/build specifici del canale,
preferisci `openclaw/plugin-sdk/channel-core`; mantieni `openclaw/plugin-sdk/core` per
la superficie ombrello più ampia e per gli helper condivisi come
`buildChannelConfigSchema`.

Non aggiungere né dipendere da scorciatoie convenience con nome del provider come
`openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp` o
superfici helper brandizzate per canale. I plugin inclusi dovrebbero comporre sottopercorsi
SDK generici all'interno dei propri barrel `api.ts` o `runtime-api.ts`, e il core
dovrebbe usare o quei barrel locali al plugin oppure aggiungere un contratto SDK
generico e ristretto quando l'esigenza è davvero cross-channel.

La mappa di esportazione generata contiene ancora un piccolo insieme di superfici helper
per plugin inclusi come `plugin-sdk/feishu`, `plugin-sdk/feishu-setup`,
`plugin-sdk/zalo`, `plugin-sdk/zalo-setup` e `plugin-sdk/matrix*`. Questi
sottopercorsi esistono solo per manutenzione e compatibilità dei plugin inclusi; sono
intenzionalmente omessi dalla tabella comune qui sotto e non sono il percorso di
importazione consigliato per nuovi plugin di terze parti.

## Riferimento dei sottopercorsi

I sottopercorsi usati più comunemente, raggruppati per finalità. L'elenco completo generato di
oltre 200 sottopercorsi si trova in `scripts/lib/plugin-sdk-entrypoints.json`.

I sottopercorsi helper riservati per plugin inclusi compaiono ancora in quell'elenco generato.
Trattali come dettagli implementativi/superfici di compatibilità, a meno che una pagina della documentazione
non ne promuova esplicitamente uno come pubblico.

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
    | `plugin-sdk/config-schema` | Esportazione dello schema Zod root `openclaw.json` (`OpenClawSchema`) |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, più `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | Helper condivisi per il wizard di setup, prompt allowlist, builder dello stato di setup |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | Helper per config multi-account/action-gate, helper di fallback dell'account predefinito |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`, helper di normalizzazione dell'ID account |
    | `plugin-sdk/account-resolution` | Helper per lookup account + fallback predefinito |
    | `plugin-sdk/account-helpers` | Helper ristretti per lista account/azioni account |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | Tipi di schema della configurazione del canale |
    | `plugin-sdk/telegram-command-config` | Helper di normalizzazione/convalida dei comandi personalizzati Telegram con fallback al contratto incluso |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | Helper condivisi per routing inbound + builder envelope |
    | `plugin-sdk/inbound-reply-dispatch` | Helper condivisi per registrazione e dispatch inbound |
    | `plugin-sdk/messaging-targets` | Helper per parsing/matching dei target |
    | `plugin-sdk/outbound-media` | Helper condivisi per il caricamento dei media outbound |
    | `plugin-sdk/outbound-runtime` | Helper per identità outbound/delegati di invio |
    | `plugin-sdk/thread-bindings-runtime` | Helper per ciclo di vita thread-binding e adapter |
    | `plugin-sdk/agent-media-payload` | Builder legacy del payload media dell'agente |
    | `plugin-sdk/conversation-runtime` | Helper per binding conversazione/thread, pairing e binding configurati |
    | `plugin-sdk/runtime-config-snapshot` | Helper per snapshot della configurazione runtime |
    | `plugin-sdk/runtime-group-policy` | Helper runtime per la risoluzione delle group-policy |
    | `plugin-sdk/channel-status` | Helper condivisi per snapshot/riepilogo dello stato del canale |
    | `plugin-sdk/channel-config-primitives` | Primitive ristrette dello schema di configurazione del canale |
    | `plugin-sdk/channel-config-writes` | Helper di autorizzazione per la scrittura della configurazione del canale |
    | `plugin-sdk/channel-plugin-common` | Esportazioni prelude condivise del plugin di canale |
    | `plugin-sdk/allowlist-config-edit` | Helper per lettura/modifica della configurazione allowlist |
    | `plugin-sdk/group-access` | Helper condivisi per le decisioni di accesso ai gruppi |
    | `plugin-sdk/direct-dm` | Helper condivisi per auth/guard dei DM diretti |
    | `plugin-sdk/interactive-runtime` | Helper di normalizzazione/riduzione del payload delle risposte interattive |
    | `plugin-sdk/channel-inbound` | Helper per debounce inbound, matching delle menzioni, policy delle menzioni e helper envelope |
    | `plugin-sdk/channel-send-result` | Tipi del risultato di risposta |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | Helper per parsing/matching dei target |
    | `plugin-sdk/channel-contract` | Tipi del contratto del canale |
    | `plugin-sdk/channel-feedback` | Wiring di feedback/reazioni |
    | `plugin-sdk/channel-secret-runtime` | Helper ristretti del contratto secret come `collectSimpleChannelFieldAssignments`, `getChannelSurface`, `pushAssignment` e tipi target secret |
  </Accordion>

  <Accordion title="Sottopercorsi del provider">
    | Sottopercorso | Esportazioni chiave |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | Helper curati di setup per provider locali/self-hosted |
    | `plugin-sdk/self-hosted-provider-setup` | Helper focalizzati di setup per provider self-hosted compatibili con OpenAI |
    | `plugin-sdk/cli-backend` | Costanti watchdog + valori predefiniti del backend CLI |
    | `plugin-sdk/provider-auth-runtime` | Helper runtime per la risoluzione della chiave API per i plugin provider |
    | `plugin-sdk/provider-auth-api-key` | Helper di onboarding/scrittura del profilo API key come `upsertApiKeyProfile` |
    | `plugin-sdk/provider-auth-result` | Builder standard del risultato auth OAuth |
    | `plugin-sdk/provider-auth-login` | Helper condivisi di login interattivo per i plugin provider |
    | `plugin-sdk/provider-env-vars` | Helper per il lookup delle env var auth del provider |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile`, `upsertApiKeyProfile`, `writeOAuthCredentials` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, builder condivisi della replay-policy, helper degli endpoint provider e helper di normalizzazione degli ID modello come `normalizeNativeXaiModelId` |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | Helper generici per capacità HTTP/endpoint del provider |
    | `plugin-sdk/provider-web-fetch-contract` | Helper ristretti del contratto config/selezione web-fetch come `enablePluginInConfig` e `WebFetchProviderPlugin` |
    | `plugin-sdk/provider-web-fetch` | Helper di registrazione/cache del provider web-fetch |
    | `plugin-sdk/provider-web-search-contract` | Helper ristretti del contratto config/credenziali web-search come `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig` e setter/getter di credenziali con scope |
    | `plugin-sdk/provider-web-search` | Helper di registrazione/cache/runtime del provider web-search |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, cleanup + diagnostica dello schema Gemini e helper compat xAI come `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` e simili |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, tipi di wrapper stream e helper wrapper condivisi Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
    | `plugin-sdk/provider-onboard` | Helper per patch della configurazione di onboarding |
    | `plugin-sdk/global-singleton` | Helper per singleton/map/cache locali al processo |
  </Accordion>

  <Accordion title="Sottopercorsi auth e sicurezza">
    | Sottopercorso | Esportazioni chiave |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`, helper del registro comandi, helper di autorizzazione del mittente |
    | `plugin-sdk/approval-auth-runtime` | Helper per risoluzione dell'approvatore e action-auth nella stessa chat |
    | `plugin-sdk/approval-client-runtime` | Helper nativi per profilo/filtro di approvazione exec |
    | `plugin-sdk/approval-delivery-runtime` | Adapter di consegna/capacità di approvazione nativi |
    | `plugin-sdk/approval-gateway-runtime` | Helper condiviso per la risoluzione del gateway di approvazione |
    | `plugin-sdk/approval-handler-adapter-runtime` | Helper leggeri per il caricamento degli adapter di approvazione nativi per entrypoint di canale hot |
    | `plugin-sdk/approval-handler-runtime` | Helper runtime più ampi per il gestore di approvazione; preferisci le superfici adapter/gateway più ristrette quando bastano |
    | `plugin-sdk/approval-native-runtime` | Helper nativi per target di approvazione + account-binding |
    | `plugin-sdk/approval-reply-runtime` | Helper per il payload di risposta di approvazione exec/plugin |
    | `plugin-sdk/command-auth-native` | Helper auth dei comandi nativi + target di sessione nativi |
    | `plugin-sdk/command-detection` | Helper condivisi per il rilevamento dei comandi |
    | `plugin-sdk/command-surface` | Helper per la normalizzazione del body del comando e command-surface |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/channel-secret-runtime` | Helper ristretti di raccolta del contratto secret per superfici secret di canale/plugin |
    | `plugin-sdk/secret-ref-runtime` | Helper ristretti `coerceSecretRef` e di tipizzazione SecretRef per parsing di secret-contract/config |
    | `plugin-sdk/security-runtime` | Helper condivisi per trust, gating DM, contenuti esterni e raccolta secret |
    | `plugin-sdk/ssrf-policy` | Helper di allowlist host e policy SSRF per rete privata |
    | `plugin-sdk/ssrf-runtime` | Helper per pinned-dispatcher, fetch protetto da SSRF e policy SSRF |
    | `plugin-sdk/secret-input` | Helper per il parsing dell'input secret |
    | `plugin-sdk/webhook-ingress` | Helper per request/target webhook |
    | `plugin-sdk/webhook-request-guards` | Helper per dimensione body request/timeout |
  </Accordion>

  <Accordion title="Sottopercorsi runtime e storage">
    | Sottopercorso | Esportazioni chiave |
    | --- | --- |
    | `plugin-sdk/runtime` | Ampi helper runtime/logging/backup/installazione plugin |
    | `plugin-sdk/runtime-env` | Helper ristretti per env runtime, logger, timeout, retry e backoff |
    | `plugin-sdk/channel-runtime-context` | Helper generici per registrazione e lookup del contesto runtime del canale |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | Helper condivisi per plugin command/hook/http/interactive |
    | `plugin-sdk/hook-runtime` | Helper condivisi per la pipeline webhook/hook interni |
    | `plugin-sdk/lazy-runtime` | Helper per import/binding runtime lazy come `createLazyRuntimeModule`, `createLazyRuntimeMethod` e `createLazyRuntimeSurface` |
    | `plugin-sdk/process-runtime` | Helper per l'esecuzione dei processi |
    | `plugin-sdk/cli-runtime` | Helper per formattazione CLI, attesa e versione |
    | `plugin-sdk/gateway-runtime` | Helper per client gateway e patch dello stato del canale |
    | `plugin-sdk/config-runtime` | Helper per caricamento/scrittura della configurazione |
    | `plugin-sdk/telegram-command-config` | Normalizzazione di nome/descrizione dei comandi Telegram e controlli di duplicazione/conflitto, anche quando la superficie del contratto Telegram incluso non è disponibile |
    | `plugin-sdk/approval-runtime` | Helper per approvazione exec/plugin, builder di capacità di approvazione, helper auth/profili, helper di routing/runtime nativi |
    | `plugin-sdk/reply-runtime` | Helper condivisi runtime inbound/reply, chunking, dispatch, heartbeat, pianificatore delle risposte |
    | `plugin-sdk/reply-dispatch-runtime` | Helper ristretti per dispatch/finalizzazione delle risposte |
    | `plugin-sdk/reply-history` | Helper condivisi della cronologia delle risposte su finestra breve come `buildHistoryContext`, `recordPendingHistoryEntry` e `clearHistoryEntriesIfEnabled` |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | Helper ristretti per chunking di testo/markdown |
    | `plugin-sdk/session-store-runtime` | Helper per percorso dell'archivio sessioni + updated-at |
    | `plugin-sdk/state-paths` | Helper per i percorsi di stato/OAuth dir |
    | `plugin-sdk/routing` | Helper per route/session-key/account binding come `resolveAgentRoute`, `buildAgentSessionKey` e `resolveDefaultAgentBoundAccountId` |
    | `plugin-sdk/status-helpers` | Helper condivisi per riepilogo dello stato di canale/account, valori predefiniti dello stato runtime e helper per metadati dei problemi |
    | `plugin-sdk/target-resolver-runtime` | Helper condivisi per il resolver dei target |
    | `plugin-sdk/string-normalization-runtime` | Helper per normalizzazione di slug/stringhe |
    | `plugin-sdk/request-url` | Estrai URL stringa da input simili a fetch/request |
    | `plugin-sdk/run-command` | Runner di comandi con timeout e risultati stdout/stderr normalizzati |
    | `plugin-sdk/param-readers` | Lettori comuni di parametri tool/CLI |
    | `plugin-sdk/tool-send` | Estrai campi target di invio canonici dagli argomenti del tool |
    | `plugin-sdk/temp-path` | Helper condivisi per i percorsi temporanei di download |
    | `plugin-sdk/logging-core` | Logger di sottosistema e helper di redazione |
    | `plugin-sdk/markdown-table-runtime` | Helper per la modalità tabella Markdown |
    | `plugin-sdk/json-store` | Piccoli helper di lettura/scrittura dello stato JSON |
    | `plugin-sdk/file-lock` | Helper di file-lock rientranti |
    | `plugin-sdk/persistent-dedupe` | Helper di cache dedupe persistente su disco |
    | `plugin-sdk/acp-runtime` | Helper runtime/session ACP e reply-dispatch |
    | `plugin-sdk/agent-config-primitives` | Primitive ristrette dello schema di configurazione runtime dell'agente |
    | `plugin-sdk/boolean-param` | Lettore permissivo di parametri booleani |
    | `plugin-sdk/dangerous-name-runtime` | Helper per la risoluzione del matching di nomi pericolosi |
    | `plugin-sdk/device-bootstrap` | Helper per bootstrap del dispositivo e token di pairing |
    | `plugin-sdk/extension-shared` | Primitive helper condivise per canale passivo, stato e proxy ambientale |
    | `plugin-sdk/models-provider-runtime` | Helper di risposta del comando `/models`/provider |
    | `plugin-sdk/skill-commands-runtime` | Helper per l'elenco dei comandi Skills |
    | `plugin-sdk/native-command-registry` | Helper per registro/build/serializzazione dei comandi nativi |
    | `plugin-sdk/provider-zai-endpoint` | Helper per rilevamento endpoint Z.A.I |
    | `plugin-sdk/infra-runtime` | Helper per eventi di sistema/heartbeat |
    | `plugin-sdk/collection-runtime` | Piccoli helper di cache limitata |
    | `plugin-sdk/diagnostic-runtime` | Helper per flag diagnostici ed eventi |
    | `plugin-sdk/error-runtime` | Grafo degli errori, formattazione, helper condivisi di classificazione degli errori, `isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | Helper per fetch avvolto, proxy e lookup pinned |
    | `plugin-sdk/host-runtime` | Helper per normalizzazione di hostname e host SCP |
    | `plugin-sdk/retry-runtime` | Helper per configurazione retry ed esecuzione retry |
    | `plugin-sdk/agent-runtime` | Helper per directory/identità/workspace dell'agente |
    | `plugin-sdk/directory-runtime` | Query/dedup di directory basate sulla configurazione |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="Sottopercorsi per capacità e test">
    | Sottopercorso | Esportazioni chiave |
    | --- | --- |
    | `plugin-sdk/media-runtime` | Helper condivisi per fetch/transform/store dei media più builder del payload media |
    | `plugin-sdk/media-generation-runtime` | Helper condivisi per failover della generazione media, selezione dei candidati e messaggistica per modello mancante |
    | `plugin-sdk/media-understanding` | Tipi del provider media understanding più esportazioni helper lato provider per immagini/audio |
    | `plugin-sdk/text-runtime` | Helper condivisi per testo/markdown/logging come rimozione del testo visibile all'assistente, helper di render/chunking/tabella markdown, helper di redazione, helper dei tag direttiva e utility per testo sicuro |
    | `plugin-sdk/text-chunking` | Helper per chunking del testo outbound |
    | `plugin-sdk/speech` | Tipi del provider speech più helper lato provider per direttive, registro e convalida |
    | `plugin-sdk/speech-core` | Tipi condivisi del provider speech, helper per registro, direttive e normalizzazione |
    | `plugin-sdk/realtime-transcription` | Tipi del provider realtime transcription e helper del registro |
    | `plugin-sdk/realtime-voice` | Tipi del provider realtime voice e helper del registro |
    | `plugin-sdk/image-generation` | Tipi del provider image generation |
    | `plugin-sdk/image-generation-core` | Tipi condivisi image-generation, helper di failover, auth e registro |
    | `plugin-sdk/music-generation` | Tipi di provider/request/result per la generazione musicale |
    | `plugin-sdk/music-generation-core` | Tipi condivisi music-generation, helper di failover, lookup provider e parsing model-ref |
    | `plugin-sdk/video-generation` | Tipi di provider/request/result per la generazione video |
    | `plugin-sdk/video-generation-core` | Tipi condivisi video-generation, helper di failover, lookup provider e parsing model-ref |
    | `plugin-sdk/webhook-targets` | Registro dei target webhook e helper per installazione route |
    | `plugin-sdk/webhook-path` | Helper per la normalizzazione del percorso webhook |
    | `plugin-sdk/web-media` | Helper condivisi per il caricamento di media remoti/locali |
    | `plugin-sdk/zod` | `zod` riesportato per i consumer del plugin SDK |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="Sottopercorsi memory">
    | Sottopercorso | Esportazioni chiave |
    | --- | --- |
    | `plugin-sdk/memory-core` | Superficie helper memory-core inclusa per helper di manager/config/file/CLI |
    | `plugin-sdk/memory-core-engine-runtime` | Facade runtime dell'indice/ricerca memory |
    | `plugin-sdk/memory-core-host-engine-foundation` | Esportazioni del motore foundation per l'host memory |
    | `plugin-sdk/memory-core-host-engine-embeddings` | Esportazioni del motore embeddings per l'host memory |
    | `plugin-sdk/memory-core-host-engine-qmd` | Esportazioni del motore QMD per l'host memory |
    | `plugin-sdk/memory-core-host-engine-storage` | Esportazioni del motore storage per l'host memory |
    | `plugin-sdk/memory-core-host-multimodal` | Helper multimodali per l'host memory |
    | `plugin-sdk/memory-core-host-query` | Helper di query per l'host memory |
    | `plugin-sdk/memory-core-host-secret` | Helper secret per l'host memory |
    | `plugin-sdk/memory-core-host-events` | Helper del journal eventi per l'host memory |
    | `plugin-sdk/memory-core-host-status` | Helper di stato per l'host memory |
    | `plugin-sdk/memory-core-host-runtime-cli` | Helper runtime CLI per l'host memory |
    | `plugin-sdk/memory-core-host-runtime-core` | Helper runtime core per l'host memory |
    | `plugin-sdk/memory-core-host-runtime-files` | Helper file/runtime per l'host memory |
    | `plugin-sdk/memory-host-core` | Alias neutrale rispetto al vendor per gli helper runtime core dell'host memory |
    | `plugin-sdk/memory-host-events` | Alias neutrale rispetto al vendor per gli helper del journal eventi dell'host memory |
    | `plugin-sdk/memory-host-files` | Alias neutrale rispetto al vendor per gli helper file/runtime dell'host memory |
    | `plugin-sdk/memory-host-markdown` | Helper condivisi di managed-markdown per plugin adiacenti alla memory |
    | `plugin-sdk/memory-host-search` | Facade runtime active memory per accesso al search-manager |
    | `plugin-sdk/memory-host-status` | Alias neutrale rispetto al vendor per gli helper di stato dell'host memory |
    | `plugin-sdk/memory-lancedb` | Superficie helper memory-lancedb inclusa |
  </Accordion>

  <Accordion title="Sottopercorsi helper inclusi riservati">
    | Famiglia | Sottopercorsi correnti | Uso previsto |
    | --- | --- | --- |
    | Browser | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | Helper di supporto per il plugin browser incluso (`browser-support` resta il barrel di compatibilità) |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | Superficie helper/runtime Matrix inclusa |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | Superficie helper/runtime LINE inclusa |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | Superficie helper IRC inclusa |
    | Helper specifici del canale | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | Superfici di compatibilità/helper per canali inclusi |
    | Helper auth/plugin-specifici | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | Superfici helper per feature/plugin inclusi; `plugin-sdk/github-copilot-token` al momento esporta `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken` e `resolveCopilotApiToken` |
  </Accordion>
</AccordionGroup>

## API di registrazione

La callback `register(api)` riceve un oggetto `OpenClawPluginApi` con questi
metodi:

### Registrazione delle capacità

| Metodo                                           | Cosa registra                   |
| ------------------------------------------------ | ------------------------------- |
| `api.registerProvider(...)`                      | Inferenza testuale (LLM)        |
| `api.registerCliBackend(...)`                    | Backend CLI di inferenza locale |
| `api.registerChannel(...)`                       | Canale di messaggistica         |
| `api.registerSpeechProvider(...)`                | Sintesi text-to-speech / STT    |
| `api.registerRealtimeTranscriptionProvider(...)` | Trascrizione realtime streaming |
| `api.registerRealtimeVoiceProvider(...)`         | Sessioni vocali realtime duplex |
| `api.registerMediaUnderstandingProvider(...)`    | Analisi di immagini/audio/video |
| `api.registerImageGenerationProvider(...)`       | Generazione di immagini         |
| `api.registerMusicGenerationProvider(...)`       | Generazione musicale            |
| `api.registerVideoGenerationProvider(...)`       | Generazione video               |
| `api.registerWebFetchProvider(...)`              | Provider di web fetch / scrape  |
| `api.registerWebSearchProvider(...)`             | Ricerca web                     |

### Strumenti e comandi

| Metodo                          | Cosa registra                                |
| ------------------------------- | -------------------------------------------- |
| `api.registerTool(tool, opts?)` | Tool agente (obbligatorio o `{ optional: true }`) |
| `api.registerCommand(def)`      | Comando personalizzato (bypassa l'LLM)       |

### Infrastruttura

| Metodo                                         | Cosa registra                          |
| ---------------------------------------------- | -------------------------------------- |
| `api.registerHook(events, handler, opts?)`     | Hook evento                            |
| `api.registerHttpRoute(params)`                | Endpoint HTTP del gateway              |
| `api.registerGatewayMethod(name, handler)`     | Metodo RPC del gateway                 |
| `api.registerCli(registrar, opts?)`            | Sottocomando CLI                       |
| `api.registerService(service)`                 | Servizio in background                 |
| `api.registerInteractiveHandler(registration)` | Gestore interattivo                    |
| `api.registerMemoryPromptSupplement(builder)`  | Sezione di prompt additiva adiacente alla memory |
| `api.registerMemoryCorpusSupplement(adapter)`  | Corpus additivo di ricerca/lettura memory |

I namespace amministrativi core riservati (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`) restano sempre `operator.admin`, anche se un plugin prova ad assegnare uno
scope del metodo gateway più ristretto. Preferisci prefissi specifici del plugin per i
metodi posseduti dal plugin.

### Metadati di registrazione CLI

`api.registerCli(registrar, opts?)` accetta due tipi di metadati di primo livello:

- `commands`: radici di comando esplicite possedute dal registrar
- `descriptors`: descrittori di comando in fase di parsing usati per l'help della CLI root,
  il routing e la registrazione lazy della CLI del plugin

Se vuoi che un comando del plugin resti caricato lazy nel normale percorso della CLI root,
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

Usa `commands` da solo solo quando non hai bisogno della registrazione lazy della CLI root.
Quel percorso di compatibilità eager resta supportato, ma non installa
placeholder supportati da descriptor per il caricamento lazy in fase di parsing.

### Registrazione del backend CLI

`api.registerCliBackend(...)` consente a un plugin di possedere la configurazione predefinita per un backend
CLI AI locale come `codex-cli`.

- L'`id` del backend diventa il prefisso provider nei model ref come `codex-cli/gpt-5`.
- La `config` del backend usa la stessa forma di `agents.defaults.cliBackends.<id>`.
- La configurazione utente continua ad avere la precedenza. OpenClaw unisce `agents.defaults.cliBackends.<id>` sopra il
  valore predefinito del plugin prima di eseguire la CLI.
- Usa `normalizeConfig` quando un backend ha bisogno di riscritture di compatibilità dopo il merge
  (ad esempio la normalizzazione di vecchie forme dei flag).

### Slot esclusivi

| Metodo                                     | Cosa registra                         |
| ------------------------------------------ | ------------------------------------- |
| `api.registerContextEngine(id, factory)`   | Motore di contesto (uno attivo alla volta) |
| `api.registerMemoryCapability(capability)` | Capacità memory unificata             |
| `api.registerMemoryPromptSection(builder)` | Builder di sezione del prompt memory  |
| `api.registerMemoryFlushPlan(resolver)`    | Resolver del piano di flush memory    |
| `api.registerMemoryRuntime(runtime)`       | Adapter runtime memory                |

### Adapter embedding memory

| Metodo                                         | Cosa registra                                        |
| ---------------------------------------------- | ---------------------------------------------------- |
| `api.registerMemoryEmbeddingProvider(adapter)` | Adapter embedding memory per il plugin attivo        |

- `registerMemoryCapability` è l'API preferita per plugin memory esclusivi.
- `registerMemoryCapability` può anche esporre `publicArtifacts.listArtifacts(...)`
  così i plugin companion possono usare gli artifact memory esportati tramite
  `openclaw/plugin-sdk/memory-host-core` invece di entrare nel layout privato di uno specifico
  plugin memory.
- `registerMemoryPromptSection`, `registerMemoryFlushPlan` e
  `registerMemoryRuntime` sono API legacy-compatibili per plugin memory esclusivi.
- `registerMemoryEmbeddingProvider` consente al plugin memory attivo di registrare uno
  o più ID di adapter embedding (ad esempio `openai`, `gemini` o un ID
  personalizzato definito dal plugin).
- La configurazione utente come `agents.defaults.memorySearch.provider` e
  `agents.defaults.memorySearch.fallback` viene risolta rispetto a quegli ID di adapter
  registrati.

### Eventi e ciclo di vita

| Metodo                                       | Cosa fa                    |
| -------------------------------------------- | -------------------------- |
| `api.on(hookName, handler, opts?)`           | Hook di ciclo di vita tipizzato |
| `api.onConversationBindingResolved(handler)` | Callback di risoluzione del binding conversazione |

### Semantica delle decisioni degli hook

- `before_tool_call`: restituire `{ block: true }` è terminale. Una volta che un handler lo imposta, gli handler con priorità inferiore vengono saltati.
- `before_tool_call`: restituire `{ block: false }` è trattato come nessuna decisione (come omettere `block`), non come override.
- `before_install`: restituire `{ block: true }` è terminale. Una volta che un handler lo imposta, gli handler con priorità inferiore vengono saltati.
- `before_install`: restituire `{ block: false }` è trattato come nessuna decisione (come omettere `block`), non come override.
- `reply_dispatch`: restituire `{ handled: true, ... }` è terminale. Una volta che un handler rivendica il dispatch, gli handler con priorità inferiore e il percorso predefinito di dispatch del modello vengono saltati.
- `message_sending`: restituire `{ cancel: true }` è terminale. Una volta che un handler lo imposta, gli handler con priorità inferiore vengono saltati.
- `message_sending`: restituire `{ cancel: false }` è trattato come nessuna decisione (come omettere `cancel`), non come override.

### Campi dell'oggetto API

| Campo                    | Tipo                      | Descrizione                                                                                 |
| ------------------------ | ------------------------- | ------------------------------------------------------------------------------------------- |
| `api.id`                 | `string`                  | ID del plugin                                                                               |
| `api.name`               | `string`                  | Nome visualizzato                                                                           |
| `api.version`            | `string?`                 | Versione del plugin (facoltativa)                                                           |
| `api.description`        | `string?`                 | Descrizione del plugin (facoltativa)                                                        |
| `api.source`             | `string`                  | Percorso sorgente del plugin                                                                |
| `api.rootDir`            | `string?`                 | Directory root del plugin (facoltativa)                                                     |
| `api.config`             | `OpenClawConfig`          | Snapshot della configurazione corrente (snapshot runtime in-memory attivo quando disponibile) |
| `api.pluginConfig`       | `Record<string, unknown>` | Configurazione specifica del plugin da `plugins.entries.<id>.config`                        |
| `api.runtime`            | `PluginRuntime`           | [Helper runtime](/it/plugins/sdk-runtime)                                                      |
| `api.logger`             | `PluginLogger`            | Logger con scope (`debug`, `info`, `warn`, `error`)                                         |
| `api.registrationMode`   | `PluginRegistrationMode`  | Modalità di caricamento corrente; `"setup-runtime"` è la finestra leggera di avvio/setup prima dell'entry completa |
| `api.resolvePath(input)` | `(string) => string`      | Risolve il percorso relativo alla root del plugin                                           |

## Convenzione dei moduli interni

All'interno del tuo plugin, usa file barrel locali per le importazioni interne:

```
my-plugin/
  api.ts            # Esportazioni pubbliche per consumer esterni
  runtime-api.ts    # Esportazioni runtime solo interne
  index.ts          # Entry point del plugin
  setup-entry.ts    # Entry leggera solo per setup (facoltativa)
```

<Warning>
  Non importare mai il tuo plugin tramite `openclaw/plugin-sdk/<your-plugin>`
  dal codice di produzione. Instrada le importazioni interne tramite `./api.ts` o
  `./runtime-api.ts`. Il percorso SDK è solo il contratto esterno.
</Warning>

Le superfici pubbliche dei plugin inclusi caricate tramite facade (`api.ts`, `runtime-api.ts`,
`index.ts`, `setup-entry.ts` e file di entry pubblici simili) ora preferiscono lo
snapshot della configurazione runtime attiva quando OpenClaw è già in esecuzione. Se non esiste ancora
uno snapshot runtime, fanno fallback al file di configurazione risolto su disco.

I plugin provider possono anche esporre un barrel di contratto locale al plugin e ristretto quando un
helper è intenzionalmente specifico del provider e non appartiene ancora a un sottopercorso SDK generico.
Esempio incluso attuale: il provider Anthropic mantiene i suoi helper di stream Claude
nella propria superficie pubblica `api.ts` / `contract-api.ts` invece di
promuovere la logica degli header beta Anthropic e `service_tier` in un contratto
generico `plugin-sdk/*`.

Altri esempi inclusi attuali:

- `@openclaw/openai-provider`: `api.ts` esporta builder del provider,
  helper del modello predefinito e builder del provider realtime
- `@openclaw/openrouter-provider`: `api.ts` esporta il builder del provider più
  helper di onboarding/config

<Warning>
  Il codice di produzione delle estensioni dovrebbe anche evitare importazioni da `openclaw/plugin-sdk/<other-plugin>`.
  Se un helper è davvero condiviso, promuovilo a un sottopercorso SDK neutrale
  come `openclaw/plugin-sdk/speech`, `.../provider-model-shared` o un'altra
  superficie orientata alle capacità invece di accoppiare due plugin tra loro.
</Warning>

## Correlati

- [Entry Points](/it/plugins/sdk-entrypoints) — opzioni di `definePluginEntry` e `defineChannelPluginEntry`
- [Runtime Helpers](/it/plugins/sdk-runtime) — riferimento completo del namespace `api.runtime`
- [Setup and Config](/it/plugins/sdk-setup) — packaging, manifest, schemi di configurazione
- [Testing](/it/plugins/sdk-testing) — utility di test e regole lint
- [SDK Migration](/it/plugins/sdk-migration) — migrazione da superfici deprecate
- [Plugin Internals](/it/plugins/architecture) — architettura approfondita e modello di capacità
