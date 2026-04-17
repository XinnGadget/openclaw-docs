---
read_when:
    - Devi sapere da quale sottopercorso dell'SDK importare
    - Vuoi un riferimento per tutti i metodi di registrazione su OpenClawPluginApi
    - Stai cercando un'esportazione specifica dell'SDK
sidebarTitle: SDK Overview
summary: Mappa di importazione, riferimento dell'API di registrazione e architettura dell'SDK
title: Panoramica del Plugin SDK
x-i18n:
    generated_at: "2026-04-17T08:17:26Z"
    model: gpt-5.4
    provider: openai
    source_hash: b177fdb6830f415d998a24812bc2c7db8124d3ba77b0174c9a67ac7d747f7e5a
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# Panoramica del Plugin SDK

Il Plugin SDK è il contratto tipizzato tra i plugin e il core. Questa pagina è il
riferimento per **cosa importare** e **cosa puoi registrare**.

<Tip>
  **Cerchi una guida pratica?**
  - Primo plugin? Inizia da [Getting Started](/it/plugins/building-plugins)
  - Plugin di canale? Vedi [Channel Plugins](/it/plugins/sdk-channel-plugins)
  - Plugin provider? Vedi [Provider Plugins](/it/plugins/sdk-provider-plugins)
</Tip>

## Convenzione di importazione

Importa sempre da un sottopercorso specifico:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

Ogni sottopercorso è un modulo piccolo e autosufficiente. Questo mantiene
l'avvio veloce e previene problemi di dipendenze circolari. Per gli helper di
entry/build specifici dei canali, preferisci `openclaw/plugin-sdk/channel-core`;
mantieni `openclaw/plugin-sdk/core` per la superficie ombrello più ampia e per
gli helper condivisi come `buildChannelConfigSchema`.

Non aggiungere né dipendere da seam di convenienza con nome del provider come
`openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp` o
seam di helper con branding del canale. I plugin inclusi dovrebbero comporre
sottopercorsi generici dell'SDK all'interno dei propri barrel `api.ts` o
`runtime-api.ts`, e il core dovrebbe usare quei barrel locali al plugin oppure
aggiungere un contratto SDK generico e ristretto quando l'esigenza è davvero
trasversale ai canali.

La mappa di esportazione generata contiene ancora un piccolo insieme di seam di
helper per plugin inclusi come `plugin-sdk/feishu`, `plugin-sdk/feishu-setup`,
`plugin-sdk/zalo`, `plugin-sdk/zalo-setup` e `plugin-sdk/matrix*`. Quei
sottopercorsi esistono solo per manutenzione e compatibilità dei plugin inclusi;
sono intenzionalmente omessi dalla tabella comune qui sotto e non sono il
percorso di importazione consigliato per nuovi plugin di terze parti.

## Riferimento dei sottopercorsi

I sottopercorsi usati più comunemente, raggruppati per scopo. L'elenco completo
generato di oltre 200 sottopercorsi si trova in `scripts/lib/plugin-sdk-entrypoints.json`.

I sottopercorsi helper riservati ai plugin inclusi compaiono ancora in questo
elenco generato. Trattali come dettagli di implementazione/superfici di
compatibilità, a meno che una pagina della documentazione non ne promuova
esplicitamente uno come pubblico.

### Entry del plugin

| Sottopercorso              | Esportazioni chiave                                                                                                                    |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/plugin-entry`   | `definePluginEntry`                                                                                                                    |
| `plugin-sdk/core`           | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema`  | `OpenClawSchema`                                                                                                                       |
| `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry`                                                                                                      |

<AccordionGroup>
  <Accordion title="Sottopercorsi dei canali">
    | Sottopercorso | Esportazioni chiave |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | Esportazione dello schema Zod radice di `openclaw.json` (`OpenClawSchema`) |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, più `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | Helper condivisi per il wizard di configurazione, prompt allowlist, builder dello stato di configurazione |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | Helper per configurazione multi-account/action-gate, helper di fallback per account predefinito |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`, helper di normalizzazione dell'ID account |
    | `plugin-sdk/account-resolution` | Helper per lookup dell'account + fallback predefinito |
    | `plugin-sdk/account-helpers` | Helper mirati per elenco account/azioni account |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | Tipi dello schema di configurazione del canale |
    | `plugin-sdk/telegram-command-config` | Helper di normalizzazione/validazione dei comandi personalizzati Telegram con fallback al contratto incluso |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | Helper condivisi per instradamento in ingresso + builder di envelope |
    | `plugin-sdk/inbound-reply-dispatch` | Helper condivisi per registrazione e dispatch in ingresso |
    | `plugin-sdk/messaging-targets` | Helper per parsing/matching dei target |
    | `plugin-sdk/outbound-media` | Helper condivisi per il caricamento di media in uscita |
    | `plugin-sdk/outbound-runtime` | Helper per identità in uscita/delegati di invio |
    | `plugin-sdk/thread-bindings-runtime` | Helper per ciclo di vita e adapter dei binding di thread |
    | `plugin-sdk/agent-media-payload` | Builder legacy del payload media dell'agente |
    | `plugin-sdk/conversation-runtime` | Helper per binding di conversazione/thread, pairing e binding configurati |
    | `plugin-sdk/runtime-config-snapshot` | Helper per snapshot della configurazione runtime |
    | `plugin-sdk/runtime-group-policy` | Helper runtime per la risoluzione delle policy di gruppo |
    | `plugin-sdk/channel-status` | Helper condivisi per snapshot/riepilogo dello stato del canale |
    | `plugin-sdk/channel-config-primitives` | Primitive mirate dello schema di configurazione del canale |
    | `plugin-sdk/channel-config-writes` | Helper di autorizzazione per scritture della configurazione del canale |
    | `plugin-sdk/channel-plugin-common` | Esportazioni di preludio condivise per plugin di canale |
    | `plugin-sdk/allowlist-config-edit` | Helper di lettura/modifica della configurazione allowlist |
    | `plugin-sdk/group-access` | Helper condivisi per decisioni di accesso ai gruppi |
    | `plugin-sdk/direct-dm` | Helper condivisi per autenticazione/guard dei messaggi diretti |
    | `plugin-sdk/interactive-runtime` | Helper di normalizzazione/riduzione dei payload di risposta interattiva |
    | `plugin-sdk/channel-inbound` | Debounce in ingresso, matching delle menzioni, helper per policy delle menzioni e helper di envelope |
    | `plugin-sdk/channel-send-result` | Tipi del risultato di risposta |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | Helper per parsing/matching dei target |
    | `plugin-sdk/channel-contract` | Tipi del contratto del canale |
    | `plugin-sdk/channel-feedback` | Wiring di feedback/reazioni |
    | `plugin-sdk/channel-secret-runtime` | Helper mirati per il contratto dei secret come `collectSimpleChannelFieldAssignments`, `getChannelSurface`, `pushAssignment` e tipi target dei secret |
  </Accordion>

  <Accordion title="Sottopercorsi dei provider">
    | Sottopercorso | Esportazioni chiave |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | Helper curati di configurazione per provider locali/self-hosted |
    | `plugin-sdk/self-hosted-provider-setup` | Helper mirati di configurazione per provider self-hosted compatibili con OpenAI |
    | `plugin-sdk/cli-backend` | Predefiniti del backend CLI + costanti watchdog |
    | `plugin-sdk/provider-auth-runtime` | Helper runtime per la risoluzione delle API key per plugin provider |
    | `plugin-sdk/provider-auth-api-key` | Helper per onboarding/scrittura del profilo API key come `upsertApiKeyProfile` |
    | `plugin-sdk/provider-auth-result` | Builder standard del risultato di autenticazione OAuth |
    | `plugin-sdk/provider-auth-login` | Helper condivisi di login interattivo per plugin provider |
    | `plugin-sdk/provider-env-vars` | Helper di lookup delle variabili d'ambiente di autenticazione del provider |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile`, `upsertApiKeyProfile`, `writeOAuthCredentials` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, builder condivisi delle replay-policy, helper per endpoint provider e helper di normalizzazione degli ID modello come `normalizeNativeXaiModelId` |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | Helper generici per capacità HTTP/endpoint del provider |
    | `plugin-sdk/provider-web-fetch-contract` | Helper mirati per contratto di configurazione/selezione web-fetch come `enablePluginInConfig` e `WebFetchProviderPlugin` |
    | `plugin-sdk/provider-web-fetch` | Helper di registrazione/cache per provider web-fetch |
    | `plugin-sdk/provider-web-search-config-contract` | Helper mirati per configurazione/credenziali web-search per provider che non richiedono wiring di abilitazione del plugin |
    | `plugin-sdk/provider-web-search-contract` | Helper mirati per contratto di configurazione/credenziali web-search come `createWebSearchProviderContractFields`, `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig` e setter/getter di credenziali con scope |
    | `plugin-sdk/provider-web-search` | Helper di registrazione/cache/runtime per provider web-search |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, pulizia dello schema Gemini + diagnostica e helper di compatibilità xAI come `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` e simili |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, tipi di wrapper di stream e helper condivisi di wrapper per Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
    | `plugin-sdk/provider-onboard` | Helper di patch della configurazione di onboarding |
    | `plugin-sdk/global-singleton` | Helper per singleton/map/cache locali al processo |
  </Accordion>

  <Accordion title="Sottopercorsi di autenticazione e sicurezza">
    | Sottopercorso | Esportazioni chiave |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`, helper del registro dei comandi, helper di autorizzazione del mittente |
    | `plugin-sdk/command-status` | Builder di messaggi di comando/aiuto come `buildCommandsMessagePaginated` e `buildHelpMessage` |
    | `plugin-sdk/approval-auth-runtime` | Risoluzione degli approvatori e helper di autenticazione delle azioni nella stessa chat |
    | `plugin-sdk/approval-client-runtime` | Helper di profilo/filtro di approvazione per esecuzione nativa |
    | `plugin-sdk/approval-delivery-runtime` | Adapter di capacità/consegna dell'approvazione nativa |
    | `plugin-sdk/approval-gateway-runtime` | Helper condiviso per la risoluzione del Gateway di approvazione |
    | `plugin-sdk/approval-handler-adapter-runtime` | Helper leggeri di caricamento degli adapter di approvazione nativa per entrypoint hot dei canali |
    | `plugin-sdk/approval-handler-runtime` | Helper runtime più ampi per il gestore delle approvazioni; preferisci i seam adapter/gateway più ristretti quando sono sufficienti |
    | `plugin-sdk/approval-native-runtime` | Helper per target di approvazione nativa + binding dell'account |
    | `plugin-sdk/approval-reply-runtime` | Helper per payload di risposta di approvazione exec/plugin |
    | `plugin-sdk/command-auth-native` | Helper di autenticazione dei comandi nativi + target di sessione nativi |
    | `plugin-sdk/command-detection` | Helper condivisi per il rilevamento dei comandi |
    | `plugin-sdk/command-surface` | Normalizzazione del corpo del comando e helper della superficie del comando |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/channel-secret-runtime` | Helper ristretti di raccolta del contratto dei secret per superfici secret di canale/plugin |
    | `plugin-sdk/secret-ref-runtime` | Helper ristretti `coerceSecretRef` e di tipizzazione SecretRef per parsing del contratto dei secret/della configurazione |
    | `plugin-sdk/security-runtime` | Helper condivisi per trust, gating dei DM, contenuti esterni e raccolta dei secret |
    | `plugin-sdk/ssrf-policy` | Helper per policy SSRF di allowlist host e rete privata |
    | `plugin-sdk/ssrf-runtime` | Helper per dispatcher bloccato, fetch protetto da SSRF e policy SSRF |
    | `plugin-sdk/secret-input` | Helper di parsing dell'input dei secret |
    | `plugin-sdk/webhook-ingress` | Helper per richieste/target Webhook |
    | `plugin-sdk/webhook-request-guards` | Helper per dimensione del body della richiesta/timeout |
  </Accordion>

  <Accordion title="Sottopercorsi di runtime e storage">
    | Sottopercorso | Esportazioni chiave |
    | --- | --- |
    | `plugin-sdk/runtime` | Helper ampi per runtime/logging/backup/installazione dei plugin |
    | `plugin-sdk/runtime-env` | Helper ristretti per env runtime, logger, timeout, retry e backoff |
    | `plugin-sdk/channel-runtime-context` | Helper generici per registrazione e lookup del contesto runtime del canale |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | Helper condivisi per comandi/hook/http/interazioni del plugin |
    | `plugin-sdk/hook-runtime` | Helper condivisi per pipeline di hook Webhook/interni |
    | `plugin-sdk/lazy-runtime` | Helper per importazione/binding lazy del runtime come `createLazyRuntimeModule`, `createLazyRuntimeMethod` e `createLazyRuntimeSurface` |
    | `plugin-sdk/process-runtime` | Helper per esecuzione di processi |
    | `plugin-sdk/cli-runtime` | Helper per formattazione CLI, attesa e versione |
    | `plugin-sdk/gateway-runtime` | Helper per client Gateway e patch dello stato del canale |
    | `plugin-sdk/config-runtime` | Helper per caricamento/scrittura della configurazione |
    | `plugin-sdk/telegram-command-config` | Normalizzazione di nome/descrizione dei comandi Telegram e controlli di duplicati/conflitti, anche quando la superficie contrattuale Telegram inclusa non è disponibile |
    | `plugin-sdk/approval-runtime` | Helper di approvazione exec/plugin, builder di capacità di approvazione, helper auth/profilo, helper di instradamento/runtime nativi |
    | `plugin-sdk/reply-runtime` | Helper runtime condivisi per ingresso/risposta, chunking, dispatch, Heartbeat, pianificatore di risposta |
    | `plugin-sdk/reply-dispatch-runtime` | Helper ristretti per dispatch/finalizzazione della risposta |
    | `plugin-sdk/reply-history` | Helper condivisi per la cronologia delle risposte su finestra breve come `buildHistoryContext`, `recordPendingHistoryEntry` e `clearHistoryEntriesIfEnabled` |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | Helper ristretti per chunking di testo/markdown |
    | `plugin-sdk/session-store-runtime` | Helper per percorso del session store + updated-at |
    | `plugin-sdk/state-paths` | Helper per percorsi di directory state/OAuth |
    | `plugin-sdk/routing` | Helper per instradamento/chiave di sessione/binding dell'account come `resolveAgentRoute`, `buildAgentSessionKey` e `resolveDefaultAgentBoundAccountId` |
    | `plugin-sdk/status-helpers` | Helper condivisi per riepilogo dello stato di canale/account, valori predefiniti dello stato runtime e helper per metadati dei problemi |
    | `plugin-sdk/target-resolver-runtime` | Helper condivisi per il resolver dei target |
    | `plugin-sdk/string-normalization-runtime` | Helper di normalizzazione di slug/stringhe |
    | `plugin-sdk/request-url` | Estrae URL stringa da input simili a fetch/request |
    | `plugin-sdk/run-command` | Runner di comandi con timeout e risultati stdout/stderr normalizzati |
    | `plugin-sdk/param-readers` | Lettori comuni di parametri per tool/CLI |
    | `plugin-sdk/tool-payload` | Estrae payload normalizzati da oggetti risultato del tool |
    | `plugin-sdk/tool-send` | Estrae campi target di invio canonici dagli argomenti del tool |
    | `plugin-sdk/temp-path` | Helper condivisi per percorsi temporanei di download |
    | `plugin-sdk/logging-core` | Helper per logger di sottosistema e redazione |
    | `plugin-sdk/markdown-table-runtime` | Helper per modalità tabella Markdown |
    | `plugin-sdk/json-store` | Piccoli helper di lettura/scrittura dello stato JSON |
    | `plugin-sdk/file-lock` | Helper di file lock rientrante |
    | `plugin-sdk/persistent-dedupe` | Helper per cache di deduplicazione persistente su disco |
    | `plugin-sdk/acp-runtime` | Helper runtime/sessione/disptach della risposta ACP |
    | `plugin-sdk/agent-config-primitives` | Primitive ristrette dello schema di configurazione runtime dell'agente |
    | `plugin-sdk/boolean-param` | Lettore permissivo di parametri booleani |
    | `plugin-sdk/dangerous-name-runtime` | Helper per la risoluzione del matching di nomi pericolosi |
    | `plugin-sdk/device-bootstrap` | Helper per bootstrap del dispositivo e token di pairing |
    | `plugin-sdk/extension-shared` | Primitive helper condivise per canali passivi, stato e proxy ambientale |
    | `plugin-sdk/models-provider-runtime` | Helper per risposta del comando `/models`/provider |
    | `plugin-sdk/skill-commands-runtime` | Helper per l'elenco dei comandi Skills |
    | `plugin-sdk/native-command-registry` | Helper per registro/build/serializzazione dei comandi nativi |
    | `plugin-sdk/agent-harness` | Superficie sperimentale trusted-plugin per harness di agente di basso livello: tipi harness, helper per steer/abort di esecuzioni attive, helper del bridge tool OpenClaw e utility per i risultati dei tentativi |
    | `plugin-sdk/provider-zai-endpoint` | Helper per il rilevamento degli endpoint Z.A.I |
    | `plugin-sdk/infra-runtime` | Helper per eventi di sistema/Heartbeat |
    | `plugin-sdk/collection-runtime` | Piccoli helper per cache limitate |
    | `plugin-sdk/diagnostic-runtime` | Helper per flag ed eventi diagnostici |
    | `plugin-sdk/error-runtime` | Grafo degli errori, formattazione, helper condivisi di classificazione degli errori, `isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | Helper per fetch avvolto, proxy e lookup bloccato |
    | `plugin-sdk/host-runtime` | Helper per normalizzazione di hostname e host SCP |
    | `plugin-sdk/retry-runtime` | Helper per configurazione retry e runner di retry |
    | `plugin-sdk/agent-runtime` | Helper per directory/identità/workspace dell'agente |
    | `plugin-sdk/directory-runtime` | Query/deduplicazione di directory supportata dalla configurazione |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="Sottopercorsi di capacità e test">
    | Sottopercorso | Esportazioni chiave |
    | --- | --- |
    | `plugin-sdk/media-runtime` | Helper condivisi per fetch/trasformazione/storage dei media più builder di payload media |
    | `plugin-sdk/media-generation-runtime` | Helper condivisi per failover della generazione media, selezione dei candidati e messaggistica per modelli mancanti |
    | `plugin-sdk/media-understanding` | Tipi provider per media understanding più esportazioni di helper per immagini/audio rivolte ai provider |
    | `plugin-sdk/text-runtime` | Helper condivisi per testo/markdown/logging come rimozione del testo visibile all'assistente, helper di rendering/chunking/tabelle Markdown, helper di redazione, helper per tag di direttiva e utility per testo sicuro |
    | `plugin-sdk/text-chunking` | Helper per chunking del testo in uscita |
    | `plugin-sdk/speech` | Tipi provider speech più helper per direttive, registro e validazione rivolti ai provider |
    | `plugin-sdk/speech-core` | Helper condivisi per tipi provider speech, registro, direttive e normalizzazione |
    | `plugin-sdk/realtime-transcription` | Tipi provider per trascrizione in tempo reale e helper del registro |
    | `plugin-sdk/realtime-voice` | Tipi provider per voce in tempo reale e helper del registro |
    | `plugin-sdk/image-generation` | Tipi provider per generazione di immagini |
    | `plugin-sdk/image-generation-core` | Helper condivisi per tipi di generazione di immagini, failover, auth e registro |
    | `plugin-sdk/music-generation` | Tipi provider/richiesta/risultato per generazione musicale |
    | `plugin-sdk/music-generation-core` | Helper condivisi per tipi di generazione musicale, failover, lookup dei provider e parsing di model-ref |
    | `plugin-sdk/video-generation` | Tipi provider/richiesta/risultato per generazione video |
    | `plugin-sdk/video-generation-core` | Helper condivisi per tipi di generazione video, failover, lookup dei provider e parsing di model-ref |
    | `plugin-sdk/webhook-targets` | Registro dei target Webhook e helper di installazione delle route |
    | `plugin-sdk/webhook-path` | Helper di normalizzazione del percorso Webhook |
    | `plugin-sdk/web-media` | Helper condivisi per caricamento di media remoti/locali |
    | `plugin-sdk/zod` | `zod` riesportato per i consumer del Plugin SDK |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="Sottopercorsi della memoria">
    | Sottopercorso | Esportazioni chiave |
    | --- | --- |
    | `plugin-sdk/memory-core` | Superficie helper inclusa memory-core per helper di manager/config/file/CLI |
    | `plugin-sdk/memory-core-engine-runtime` | Facciata runtime per indice/ricerca della memoria |
    | `plugin-sdk/memory-core-host-engine-foundation` | Esportazioni del motore foundation dell'host della memoria |
    | `plugin-sdk/memory-core-host-engine-embeddings` | Contratti di embedding dell'host della memoria, accesso al registro, provider locale e helper generici batch/remoti |
    | `plugin-sdk/memory-core-host-engine-qmd` | Esportazioni del motore QMD dell'host della memoria |
    | `plugin-sdk/memory-core-host-engine-storage` | Esportazioni del motore di storage dell'host della memoria |
    | `plugin-sdk/memory-core-host-multimodal` | Helper multimodali dell'host della memoria |
    | `plugin-sdk/memory-core-host-query` | Helper di query dell'host della memoria |
    | `plugin-sdk/memory-core-host-secret` | Helper secret dell'host della memoria |
    | `plugin-sdk/memory-core-host-events` | Helper per event journal dell'host della memoria |
    | `plugin-sdk/memory-core-host-status` | Helper di stato dell'host della memoria |
    | `plugin-sdk/memory-core-host-runtime-cli` | Helper runtime CLI dell'host della memoria |
    | `plugin-sdk/memory-core-host-runtime-core` | Helper runtime core dell'host della memoria |
    | `plugin-sdk/memory-core-host-runtime-files` | Helper file/runtime dell'host della memoria |
    | `plugin-sdk/memory-host-core` | Alias neutrale rispetto al vendor per helper runtime core dell'host della memoria |
    | `plugin-sdk/memory-host-events` | Alias neutrale rispetto al vendor per helper dell'event journal dell'host della memoria |
    | `plugin-sdk/memory-host-files` | Alias neutrale rispetto al vendor per helper file/runtime dell'host della memoria |
    | `plugin-sdk/memory-host-markdown` | Helper condivisi per markdown gestito per plugin adiacenti alla memoria |
    | `plugin-sdk/memory-host-search` | Facciata runtime di Active Memory per l'accesso al search manager |
    | `plugin-sdk/memory-host-status` | Alias neutrale rispetto al vendor per helper di stato dell'host della memoria |
    | `plugin-sdk/memory-lancedb` | Superficie helper inclusa memory-lancedb |
  </Accordion>

  <Accordion title="Sottopercorsi helper inclusi riservati">
    | Famiglia | Sottopercorsi attuali | Uso previsto |
    | --- | --- | --- |
    | Browser | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | Helper di supporto per il Plugin browser incluso (`browser-support` rimane il barrel di compatibilità) |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | Superficie helper/runtime Matrix inclusa |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | Superficie helper/runtime LINE inclusa |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | Superficie helper IRC inclusa |
    | Helper specifici del canale | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | Seam di compatibilità/helper per canali inclusi |
    | Helper specifici di auth/plugin | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | Seam helper per funzionalità/plugin inclusi; `plugin-sdk/github-copilot-token` attualmente esporta `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken` e `resolveCopilotApiToken` |
  </Accordion>
</AccordionGroup>

## API di registrazione

La callback `register(api)` riceve un oggetto `OpenClawPluginApi` con questi
metodi:

### Registrazione delle capacità

| Metodo                                           | Cosa registra                         |
| ------------------------------------------------ | ------------------------------------- |
| `api.registerProvider(...)`                      | Inferenza di testo (LLM)              |
| `api.registerAgentHarness(...)`                  | Esecutore sperimentale di agenti a basso livello |
| `api.registerCliBackend(...)`                    | Backend di inferenza CLI locale       |
| `api.registerChannel(...)`                       | Canale di messaggistica               |
| `api.registerSpeechProvider(...)`                | Sintesi text-to-speech / STT          |
| `api.registerRealtimeTranscriptionProvider(...)` | Trascrizione realtime in streaming    |
| `api.registerRealtimeVoiceProvider(...)`         | Sessioni vocali realtime duplex       |
| `api.registerMediaUnderstandingProvider(...)`    | Analisi di immagini/audio/video       |
| `api.registerImageGenerationProvider(...)`       | Generazione di immagini               |
| `api.registerMusicGenerationProvider(...)`       | Generazione musicale                  |
| `api.registerVideoGenerationProvider(...)`       | Generazione video                     |
| `api.registerWebFetchProvider(...)`              | Provider di recupero / scraping Web   |
| `api.registerWebSearchProvider(...)`             | Ricerca Web                           |

### Tool e comandi

| Metodo                          | Cosa registra                                |
| ------------------------------- | -------------------------------------------- |
| `api.registerTool(tool, opts?)` | Tool dell'agente (obbligatorio o `{ optional: true }`) |
| `api.registerCommand(def)`      | Comando personalizzato (bypassa l'LLM)       |

### Infrastruttura

| Metodo                                         | Cosa registra                           |
| ---------------------------------------------- | --------------------------------------- |
| `api.registerHook(events, handler, opts?)`     | Hook di evento                          |
| `api.registerHttpRoute(params)`                | Endpoint HTTP del Gateway               |
| `api.registerGatewayMethod(name, handler)`     | Metodo RPC del Gateway                  |
| `api.registerCli(registrar, opts?)`            | Sottocomando CLI                        |
| `api.registerService(service)`                 | Servizio in background                  |
| `api.registerInteractiveHandler(registration)` | Gestore interattivo                     |
| `api.registerMemoryPromptSupplement(builder)`  | Sezione aggiuntiva del prompt adiacente alla memoria |
| `api.registerMemoryCorpusSupplement(adapter)`  | Corpus aggiuntivo di ricerca/lettura della memoria |

Gli spazi dei nomi amministrativi riservati del core (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`) restano sempre `operator.admin`, anche se un plugin prova ad assegnare
un ambito più ristretto al metodo Gateway. Preferisci prefissi specifici del plugin per
i metodi di proprietà del plugin.

### Metadati di registrazione CLI

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
Quel percorso di compatibilità eager resta supportato, ma non installa
placeholder supportati da descriptor per il caricamento lazy in fase di parsing.

### Registrazione del backend CLI

`api.registerCliBackend(...)` permette a un plugin di possedere la configurazione predefinita per un
backend CLI AI locale come `codex-cli`.

- L'`id` del backend diventa il prefisso del provider nei model ref come `codex-cli/gpt-5`.
- La `config` del backend usa la stessa forma di `agents.defaults.cliBackends.<id>`.
- La configurazione dell'utente ha comunque la precedenza. OpenClaw unisce `agents.defaults.cliBackends.<id>` sopra il
  valore predefinito del plugin prima di eseguire la CLI.
- Usa `normalizeConfig` quando un backend ha bisogno di riscritture di compatibilità dopo il merge
  (per esempio per normalizzare vecchie forme di flag).

### Slot esclusivi

| Metodo                                     | Cosa registra                                                                                                                                         |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `api.registerContextEngine(id, factory)`   | Motore di contesto (uno attivo alla volta). La callback `assemble()` riceve `availableTools` e `citationsMode` così il motore può adattare le aggiunte al prompt. |
| `api.registerMemoryCapability(capability)` | Capacità di memoria unificata                                                                                                                         |
| `api.registerMemoryPromptSection(builder)` | Builder della sezione prompt della memoria                                                                                                            |
| `api.registerMemoryFlushPlan(resolver)`    | Resolver del piano di flush della memoria                                                                                                             |
| `api.registerMemoryRuntime(runtime)`       | Adapter runtime della memoria                                                                                                                         |

### Adapter di embedding della memoria

| Metodo                                         | Cosa registra                              |
| ---------------------------------------------- | ------------------------------------------ |
| `api.registerMemoryEmbeddingProvider(adapter)` | Adapter di embedding della memoria per il plugin attivo |

- `registerMemoryCapability` è l'API preferita per plugin di memoria esclusivi.
- `registerMemoryCapability` può anche esporre `publicArtifacts.listArtifacts(...)`
  così i plugin companion possono usare artefatti di memoria esportati tramite
  `openclaw/plugin-sdk/memory-host-core` invece di entrare nel layout privato
  di uno specifico plugin di memoria.
- `registerMemoryPromptSection`, `registerMemoryFlushPlan` e
  `registerMemoryRuntime` sono API legacy compatibili per plugin di memoria esclusivi.
- `registerMemoryEmbeddingProvider` permette al plugin di memoria attivo di registrare uno
  o più ID di adapter di embedding (per esempio `openai`, `gemini` o un ID personalizzato
  definito dal plugin).
- La configurazione dell'utente, come `agents.defaults.memorySearch.provider` e
  `agents.defaults.memorySearch.fallback`, viene risolta rispetto a quegli ID
  di adapter registrati.

### Eventi e ciclo di vita

| Metodo                                       | Cosa fa                     |
| -------------------------------------------- | --------------------------- |
| `api.on(hookName, handler, opts?)`           | Hook di ciclo di vita tipizzato |
| `api.onConversationBindingResolved(handler)` | Callback di binding della conversazione |

### Semantica decisionale degli hook

- `before_tool_call`: restituire `{ block: true }` è terminale. Una volta che un handler lo imposta, gli handler a priorità inferiore vengono saltati.
- `before_tool_call`: restituire `{ block: false }` è trattato come nessuna decisione (come omettere `block`), non come override.
- `before_install`: restituire `{ block: true }` è terminale. Una volta che un handler lo imposta, gli handler a priorità inferiore vengono saltati.
- `before_install`: restituire `{ block: false }` è trattato come nessuna decisione (come omettere `block`), non come override.
- `reply_dispatch`: restituire `{ handled: true, ... }` è terminale. Una volta che un handler rivendica il dispatch, gli handler a priorità inferiore e il percorso predefinito di dispatch del modello vengono saltati.
- `message_sending`: restituire `{ cancel: true }` è terminale. Una volta che un handler lo imposta, gli handler a priorità inferiore vengono saltati.
- `message_sending`: restituire `{ cancel: false }` è trattato come nessuna decisione (come omettere `cancel`), non come override.

### Campi dell'oggetto API

| Campo                    | Tipo                      | Descrizione                                                                                 |
| ------------------------ | ------------------------- | ------------------------------------------------------------------------------------------- |
| `api.id`                 | `string`                  | ID del plugin                                                                               |
| `api.name`               | `string`                  | Nome visualizzato                                                                           |
| `api.version`            | `string?`                 | Versione del plugin (facoltativa)                                                           |
| `api.description`        | `string?`                 | Descrizione del plugin (facoltativa)                                                        |
| `api.source`             | `string`                  | Percorso sorgente del plugin                                                                |
| `api.rootDir`            | `string?`                 | Directory radice del plugin (facoltativa)                                                   |
| `api.config`             | `OpenClawConfig`          | Snapshot corrente della configurazione (snapshot runtime in memoria attivo quando disponibile) |
| `api.pluginConfig`       | `Record<string, unknown>` | Configurazione specifica del plugin da `plugins.entries.<id>.config`                        |
| `api.runtime`            | `PluginRuntime`           | [Helper runtime](/it/plugins/sdk-runtime)                                                      |
| `api.logger`             | `PluginLogger`            | Logger con scope (`debug`, `info`, `warn`, `error`)                                         |
| `api.registrationMode`   | `PluginRegistrationMode`  | Modalità di caricamento corrente; `"setup-runtime"` è la finestra leggera di avvio/configurazione prima dell'entry completa |
| `api.resolvePath(input)` | `(string) => string`      | Risolve il percorso relativo alla radice del plugin                                         |

## Convenzione dei moduli interni

All'interno del tuo plugin, usa file barrel locali per le importazioni interne:

```
my-plugin/
  api.ts            # Esportazioni pubbliche per consumer esterni
  runtime-api.ts    # Esportazioni runtime solo interne
  index.ts          # Punto di ingresso del plugin
  setup-entry.ts    # Entry leggera solo per la configurazione (facoltativa)
```

<Warning>
  Non importare mai il tuo stesso plugin tramite `openclaw/plugin-sdk/<your-plugin>`
  dal codice di produzione. Instrada le importazioni interne tramite `./api.ts` o
  `./runtime-api.ts`. Il percorso SDK è solo il contratto esterno.
</Warning>

Le superfici pubbliche dei plugin inclusi caricate tramite facade (`api.ts`, `runtime-api.ts`,
`index.ts`, `setup-entry.ts` e file di entry pubblici simili) ora preferiscono lo
snapshot della configurazione runtime attiva quando OpenClaw è già in esecuzione. Se non esiste ancora
uno snapshot runtime, ricadono sulla configurazione risolta dal file su disco.

I plugin provider possono anche esporre un barrel di contratto locale al plugin e ristretto quando un
helper è intenzionalmente specifico del provider e non appartiene ancora a un sottopercorso
SDK generico. Esempio attuale incluso: il provider Anthropic mantiene i propri helper di stream Claude
nel proprio seam pubblico `api.ts` / `contract-api.ts` invece di promuovere la logica
dell'header beta Anthropic e `service_tier` in un contratto generico
`plugin-sdk/*`.

Altri esempi attuali inclusi:

- `@openclaw/openai-provider`: `api.ts` esporta builder di provider,
  helper per modelli predefiniti e builder di provider realtime
- `@openclaw/openrouter-provider`: `api.ts` esporta il builder del provider più
  helper di onboarding/configurazione

<Warning>
  Il codice di produzione delle estensioni dovrebbe anche evitare importazioni
  `openclaw/plugin-sdk/<other-plugin>`. Se un helper è davvero condiviso, promuovilo a un sottopercorso
  SDK neutrale come `openclaw/plugin-sdk/speech`, `.../provider-model-shared` o a un'altra
  superficie orientata alle capacità invece di accoppiare due plugin tra loro.
</Warning>

## Correlati

- [Punti di ingresso](/it/plugins/sdk-entrypoints) — opzioni di `definePluginEntry` e `defineChannelPluginEntry`
- [Helper runtime](/it/plugins/sdk-runtime) — riferimento completo del namespace `api.runtime`
- [Configurazione e config](/it/plugins/sdk-setup) — packaging, manifest, schemi di configurazione
- [Testing](/it/plugins/sdk-testing) — utility di test e regole lint
- [Migrazione dell'SDK](/it/plugins/sdk-migration) — migrazione dalle superfici deprecate
- [Elementi interni del Plugin](/it/plugins/architecture) — architettura approfondita e modello di capacità
