---
read_when:
    - Devi sapere da quale sottopercorso dell'SDK importare
    - Vuoi un riferimento per tutti i metodi di registrazione su OpenClawPluginApi
    - Stai cercando una specifica esportazione dell'SDK
sidebarTitle: SDK Overview
summary: Mappa degli import, riferimento dell'API di registrazione e architettura SDK
title: Panoramica dell'SDK dei plugin
x-i18n:
    generated_at: "2026-04-11T02:46:36Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4bfeb5896f68e3e4ee8cf434d43a019e0d1fe5af57f5bf7a5172847c476def0c
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# Panoramica dell'SDK dei plugin

L'SDK dei plugin è il contratto tipizzato tra i plugin e il core. Questa pagina è il
riferimento per **cosa importare** e **cosa puoi registrare**.

<Tip>
  **Cerchi una guida pratica?**
  - Primo plugin? Inizia con [Per iniziare](/it/plugins/building-plugins)
  - Plugin canale? Vedi [Plugin canale](/it/plugins/sdk-channel-plugins)
  - Plugin provider? Vedi [Plugin provider](/it/plugins/sdk-provider-plugins)
</Tip>

## Convenzione di importazione

Importa sempre da un sottopercorso specifico:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

Ogni sottopercorso è un modulo piccolo e autosufficiente. Questo mantiene l'avvio rapido e
previene problemi di dipendenze circolari. Per helper specifici di entry/build dei canali,
preferisci `openclaw/plugin-sdk/channel-core`; mantieni `openclaw/plugin-sdk/core` per
la superficie ombrello più ampia e per gli helper condivisi come
`buildChannelConfigSchema`.

Non aggiungere né dipendere da seam di convenienza con nome di provider come
`openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp` o
seam helper con brand del canale. I plugin bundled dovrebbero comporre sottopercorsi
SDK generici all'interno dei propri barrel `api.ts` o `runtime-api.ts`, e il core
dovrebbe usare quei barrel locali al plugin oppure aggiungere un contratto SDK
generico ristretto quando l'esigenza è davvero cross-channel.

La mappa delle esportazioni generata contiene ancora un piccolo insieme di seam helper
per plugin bundled come `plugin-sdk/feishu`, `plugin-sdk/feishu-setup`,
`plugin-sdk/zalo`, `plugin-sdk/zalo-setup` e `plugin-sdk/matrix*`. Questi
sottopercorsi esistono solo per manutenzione e compatibilità dei plugin bundled; sono
intenzionalmente omessi dalla tabella comune qui sotto e non sono il percorso di
importazione consigliato per nuovi plugin di terze parti.

## Riferimento dei sottopercorsi

I sottopercorsi usati più comunemente, raggruppati per scopo. L'elenco completo generato di
oltre 200 sottopercorsi si trova in `scripts/lib/plugin-sdk-entrypoints.json`.

I sottopercorsi helper riservati ai plugin bundled compaiono ancora in quell'elenco generato.
Trattali come superfici di dettaglio implementativo/compatibilità a meno che una pagina di documentazione
non ne promuova esplicitamente una come pubblica.

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
    | `plugin-sdk/config-schema` | Esportazione dello schema Zod radice `openclaw.json` (`OpenClawSchema`) |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, più `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | Helper condivisi per il wizard di setup, prompt allowlist, builder di stato del setup |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | Helper per config/action-gate multi-account, helper di fallback dell'account predefinito |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`, helper di normalizzazione account-id |
    | `plugin-sdk/account-resolution` | Helper per ricerca account + fallback predefinito |
    | `plugin-sdk/account-helpers` | Helper ristretti per elenco account/azioni sugli account |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | Tipi di schema di configurazione del canale |
    | `plugin-sdk/telegram-command-config` | Helper di normalizzazione/validazione per comandi personalizzati Telegram con fallback al contratto bundled |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | Helper condivisi per instradamento inbound e costruzione dell'envelope |
    | `plugin-sdk/inbound-reply-dispatch` | Helper condivisi per registrazione e dispatch inbound |
    | `plugin-sdk/messaging-targets` | Helper per parsing/corrispondenza delle destinazioni |
    | `plugin-sdk/outbound-media` | Helper condivisi per caricamento dei media outbound |
    | `plugin-sdk/outbound-runtime` | Helper per identità outbound e delegati di invio |
    | `plugin-sdk/thread-bindings-runtime` | Helper per ciclo di vita e adattatori del binding dei thread |
    | `plugin-sdk/agent-media-payload` | Builder legacy del payload media dell'agente |
    | `plugin-sdk/conversation-runtime` | Helper per binding conversazione/thread, pairing e binding configurati |
    | `plugin-sdk/runtime-config-snapshot` | Helper per snapshot della configurazione runtime |
    | `plugin-sdk/runtime-group-policy` | Helper per risoluzione della policy di gruppo a runtime |
    | `plugin-sdk/channel-status` | Helper condivisi per snapshot/riepilogo dello stato del canale |
    | `plugin-sdk/channel-config-primitives` | Primitive ristrette dello schema di configurazione del canale |
    | `plugin-sdk/channel-config-writes` | Helper di autorizzazione per scritture della configurazione del canale |
    | `plugin-sdk/channel-plugin-common` | Esportazioni di preambolo condivise per i plugin canale |
    | `plugin-sdk/allowlist-config-edit` | Helper di lettura/modifica della configurazione allowlist |
    | `plugin-sdk/group-access` | Helper condivisi per decisioni di accesso ai gruppi |
    | `plugin-sdk/direct-dm` | Helper condivisi per auth/guard dei DM diretti |
    | `plugin-sdk/interactive-runtime` | Helper di normalizzazione/riduzione del payload di risposta interattiva |
    | `plugin-sdk/channel-inbound` | Debounce inbound, corrispondenza mention, helper per policy mention ed envelope |
    | `plugin-sdk/channel-send-result` | Tipi di risultato della risposta |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | Helper per parsing/corrispondenza delle destinazioni |
    | `plugin-sdk/channel-contract` | Tipi del contratto del canale |
    | `plugin-sdk/channel-feedback` | Wiring di feedback/reazioni |
    | `plugin-sdk/channel-secret-runtime` | Helper ristretti per il contratto dei secret come `collectSimpleChannelFieldAssignments`, `getChannelSurface`, `pushAssignment` e tipi di destinazione dei secret |
  </Accordion>

  <Accordion title="Sottopercorsi dei provider">
    | Sottopercorso | Esportazioni chiave |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | Helper curati per il setup di provider locali/self-hosted |
    | `plugin-sdk/self-hosted-provider-setup` | Helper focalizzati per il setup di provider self-hosted compatibili con OpenAI |
    | `plugin-sdk/cli-backend` | Valori predefiniti del backend CLI + costanti watchdog |
    | `plugin-sdk/provider-auth-runtime` | Helper runtime per la risoluzione delle API key per i plugin provider |
    | `plugin-sdk/provider-auth-api-key` | Helper per onboarding/scrittura del profilo API key come `upsertApiKeyProfile` |
    | `plugin-sdk/provider-auth-result` | Builder standard del risultato auth OAuth |
    | `plugin-sdk/provider-auth-login` | Helper condivisi di login interattivo per i plugin provider |
    | `plugin-sdk/provider-env-vars` | Helper di ricerca delle env var auth dei provider |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile`, `upsertApiKeyProfile`, `writeOAuthCredentials` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, builder condivisi di replay-policy, helper per endpoint provider e helper di normalizzazione model-id come `normalizeNativeXaiModelId` |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | Helper generici per capability HTTP/endpoint dei provider |
    | `plugin-sdk/provider-web-fetch-contract` | Helper ristretti per contratti di configurazione/selezione web-fetch come `enablePluginInConfig` e `WebFetchProviderPlugin` |
    | `plugin-sdk/provider-web-fetch` | Helper per registrazione/cache dei provider web-fetch |
    | `plugin-sdk/provider-web-search-config-contract` | Helper ristretti per configurazione/credenziali web-search per provider che non richiedono wiring di abilitazione del plugin |
    | `plugin-sdk/provider-web-search-contract` | Helper ristretti per contratti di configurazione/credenziali web-search come `createWebSearchProviderContractFields`, `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig` e setter/getter di credenziali con scope |
    | `plugin-sdk/provider-web-search` | Helper per registrazione/cache/runtime dei provider web-search |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, pulizia schema Gemini + diagnostica, e helper di compatibilità xAI come `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` e simili |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, tipi di wrapper stream e helper wrapper condivisi per Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
    | `plugin-sdk/provider-onboard` | Helper per patch di configurazione onboarding |
    | `plugin-sdk/global-singleton` | Helper per singleton/map/cache locali al processo |
  </Accordion>

  <Accordion title="Sottopercorsi di auth e sicurezza">
    | Sottopercorso | Esportazioni chiave |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`, helper del registro comandi, helper di autorizzazione del mittente |
    | `plugin-sdk/command-status` | Builder di comandi/messaggi di help come `buildCommandsMessagePaginated` e `buildHelpMessage` |
    | `plugin-sdk/approval-auth-runtime` | Risoluzione degli approvatori e helper di action-auth nella stessa chat |
    | `plugin-sdk/approval-client-runtime` | Helper per profilo/filtro di approvazione exec nativa |
    | `plugin-sdk/approval-delivery-runtime` | Adattatori di capability/consegna per approvazioni native |
    | `plugin-sdk/approval-gateway-runtime` | Helper condiviso per la risoluzione del gateway di approvazione |
    | `plugin-sdk/approval-handler-adapter-runtime` | Helper leggeri di caricamento dell'adattatore di approvazione nativa per entrypoint hot dei canali |
    | `plugin-sdk/approval-handler-runtime` | Helper runtime più ampi per il gestore delle approvazioni; preferisci i seam più ristretti di adapter/gateway quando sono sufficienti |
    | `plugin-sdk/approval-native-runtime` | Helper per destinazioni di approvazione native e binding degli account |
    | `plugin-sdk/approval-reply-runtime` | Helper per payload di risposta delle approvazioni exec/plugin |
    | `plugin-sdk/command-auth-native` | Helper di auth dei comandi nativi + helper nativi per la destinazione della sessione |
    | `plugin-sdk/command-detection` | Helper condivisi per il rilevamento dei comandi |
    | `plugin-sdk/command-surface` | Normalizzazione del corpo del comando e helper della superficie del comando |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/channel-secret-runtime` | Helper ristretti di raccolta per il contratto dei secret nelle superfici secret di canali/plugin |
    | `plugin-sdk/secret-ref-runtime` | Helper ristretti `coerceSecretRef` e di tipizzazione SecretRef per il parsing del contratto secret/della configurazione |
    | `plugin-sdk/security-runtime` | Helper condivisi per trust, gating DM, contenuti esterni e raccolta dei secret |
    | `plugin-sdk/ssrf-policy` | Helper per allowlist host e policy SSRF di rete privata |
    | `plugin-sdk/ssrf-runtime` | Dispatcher pinned, fetch protetto da SSRF e helper per policy SSRF |
    | `plugin-sdk/secret-input` | Helper per il parsing degli input segreti |
    | `plugin-sdk/webhook-ingress` | Helper per richieste/destinazioni webhook |
    | `plugin-sdk/webhook-request-guards` | Helper per dimensione body/timeout delle richieste |
  </Accordion>

  <Accordion title="Sottopercorsi di runtime e archiviazione">
    | Sottopercorso | Esportazioni chiave |
    | --- | --- |
    | `plugin-sdk/runtime` | Ampi helper per runtime/logging/backup/installazione plugin |
    | `plugin-sdk/runtime-env` | Helper ristretti per env runtime, logger, timeout, retry e backoff |
    | `plugin-sdk/channel-runtime-context` | Helper generici per registrazione e lookup del contesto runtime del canale |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | Helper condivisi per comandi/hook/http/interattivi dei plugin |
    | `plugin-sdk/hook-runtime` | Helper condivisi per la pipeline di webhook/hook interni |
    | `plugin-sdk/lazy-runtime` | Helper per import/binding lazy del runtime come `createLazyRuntimeModule`, `createLazyRuntimeMethod` e `createLazyRuntimeSurface` |
    | `plugin-sdk/process-runtime` | Helper per exec dei processi |
    | `plugin-sdk/cli-runtime` | Helper per formattazione CLI, attesa e versione |
    | `plugin-sdk/gateway-runtime` | Helper per client gateway e patch dello stato del canale |
    | `plugin-sdk/config-runtime` | Helper di caricamento/scrittura della configurazione |
    | `plugin-sdk/telegram-command-config` | Normalizzazione di nome/descrizione dei comandi Telegram e controlli di duplicati/conflitti, anche quando la superficie di contratto Telegram bundled non è disponibile |
    | `plugin-sdk/approval-runtime` | Helper per approvazioni exec/plugin, builder di capability di approvazione, helper di auth/profilo, helper di routing/runtime nativi |
    | `plugin-sdk/reply-runtime` | Helper runtime condivisi per inbound/reply, chunking, dispatch, heartbeat, pianificatore delle risposte |
    | `plugin-sdk/reply-dispatch-runtime` | Helper ristretti per dispatch/finalizzazione delle risposte |
    | `plugin-sdk/reply-history` | Helper condivisi per la cronologia delle risposte in finestre brevi come `buildHistoryContext`, `recordPendingHistoryEntry` e `clearHistoryEntriesIfEnabled` |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | Helper ristretti per chunking di testo/Markdown |
    | `plugin-sdk/session-store-runtime` | Helper per percorso dello store di sessione e `updated-at` |
    | `plugin-sdk/state-paths` | Helper per i percorsi delle directory state/OAuth |
    | `plugin-sdk/routing` | Helper per binding di route/session-key/account come `resolveAgentRoute`, `buildAgentSessionKey` e `resolveDefaultAgentBoundAccountId` |
    | `plugin-sdk/status-helpers` | Helper condivisi per riepilogo dello stato di canali/account, valori predefiniti dello stato runtime e helper per metadati dei problemi |
    | `plugin-sdk/target-resolver-runtime` | Helper condivisi per il risolutore delle destinazioni |
    | `plugin-sdk/string-normalization-runtime` | Helper per normalizzazione di slug/stringhe |
    | `plugin-sdk/request-url` | Estrazione di URL stringa da input simili a fetch/request |
    | `plugin-sdk/run-command` | Runner di comandi temporizzato con risultati stdout/stderr normalizzati |
    | `plugin-sdk/param-readers` | Lettori comuni di parametri per strumenti/CLI |
    | `plugin-sdk/tool-payload` | Estrazione di payload normalizzati da oggetti risultato degli strumenti |
    | `plugin-sdk/tool-send` | Estrazione dei campi canonici della destinazione di invio dagli argomenti degli strumenti |
    | `plugin-sdk/temp-path` | Helper condivisi per percorsi temporanei di download |
    | `plugin-sdk/logging-core` | Helper per logger di sottosistema e redazione |
    | `plugin-sdk/markdown-table-runtime` | Helper per la modalità tabella Markdown |
    | `plugin-sdk/json-store` | Piccoli helper di lettura/scrittura dello stato JSON |
    | `plugin-sdk/file-lock` | Helper per file-lock rientranti |
    | `plugin-sdk/persistent-dedupe` | Helper per cache di deduplicazione su disco |
    | `plugin-sdk/acp-runtime` | Helper per runtime/sessione ACP e reply-dispatch |
    | `plugin-sdk/agent-config-primitives` | Primitive ristrette dello schema di configurazione del runtime agente |
    | `plugin-sdk/boolean-param` | Lettore permissivo di parametri booleani |
    | `plugin-sdk/dangerous-name-runtime` | Helper di risoluzione per corrispondenza di nomi pericolosi |
    | `plugin-sdk/device-bootstrap` | Helper per bootstrap del dispositivo e token di pairing |
    | `plugin-sdk/extension-shared` | Primitive helper condivise per canali passivi, stato e proxy ambientali |
    | `plugin-sdk/models-provider-runtime` | Helper di risposta per il comando `/models` e i provider |
    | `plugin-sdk/skill-commands-runtime` | Helper per l'elenco dei comandi delle Skills |
    | `plugin-sdk/native-command-registry` | Helper per registro/build/serializzazione dei comandi nativi |
    | `plugin-sdk/agent-harness` | Superficie sperimentale per plugin trusted per agent harness di basso livello: tipi di harness, helper di steer/abort delle esecuzioni attive, bridge degli strumenti OpenClaw e utility per i risultati dei tentativi |
    | `plugin-sdk/provider-zai-endpoint` | Helper di rilevamento endpoint Z.A.I |
    | `plugin-sdk/infra-runtime` | Helper per eventi di sistema/heartbeat |
    | `plugin-sdk/collection-runtime` | Piccoli helper per cache limitate |
    | `plugin-sdk/diagnostic-runtime` | Helper per flag ed eventi diagnostici |
    | `plugin-sdk/error-runtime` | Grafo degli errori, formattazione, helper condivisi di classificazione degli errori, `isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | Helper per fetch wrapped, proxy e lookup pinned |
    | `plugin-sdk/host-runtime` | Helper per normalizzazione di hostname e host SCP |
    | `plugin-sdk/retry-runtime` | Helper per configurazione retry e runner di retry |
    | `plugin-sdk/agent-runtime` | Helper per directory/identità/workspace degli agenti |
    | `plugin-sdk/directory-runtime` | Query/dedup di directory basate sulla configurazione |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="Sottopercorsi per capability e test">
    | Sottopercorso | Esportazioni chiave |
    | --- | --- |
    | `plugin-sdk/media-runtime` | Helper condivisi per fetch/trasformazione/archiviazione dei media più builder di payload media |
    | `plugin-sdk/media-generation-runtime` | Helper condivisi per failover di generazione media, selezione dei candidati e messaggi per modelli mancanti |
    | `plugin-sdk/media-understanding` | Tipi di provider per comprensione dei media più esportazioni helper lato provider per immagini/audio |
    | `plugin-sdk/text-runtime` | Helper condivisi per testo/Markdown/logging come rimozione del testo visibile all'assistente, helper per rendering/chunking/tabelle Markdown, helper di redazione, helper per tag direttiva e utility per testo sicuro |
    | `plugin-sdk/text-chunking` | Helper per chunking del testo in uscita |
    | `plugin-sdk/speech` | Tipi di provider speech più helper lato provider per direttive, registro e validazione |
    | `plugin-sdk/speech-core` | Tipi condivisi di provider speech, registro, direttive e helper di normalizzazione |
    | `plugin-sdk/realtime-transcription` | Tipi di provider per trascrizione realtime e helper di registro |
    | `plugin-sdk/realtime-voice` | Tipi di provider per voce realtime e helper di registro |
    | `plugin-sdk/image-generation` | Tipi di provider per generazione immagini |
    | `plugin-sdk/image-generation-core` | Tipi condivisi per generazione immagini, failover, auth e helper di registro |
    | `plugin-sdk/music-generation` | Tipi di provider/richiesta/risultato per generazione musicale |
    | `plugin-sdk/music-generation-core` | Tipi condivisi per generazione musicale, helper di failover, lookup provider e parsing dei riferimenti ai modelli |
    | `plugin-sdk/video-generation` | Tipi di provider/richiesta/risultato per generazione video |
    | `plugin-sdk/video-generation-core` | Tipi condivisi per generazione video, helper di failover, lookup provider e parsing dei riferimenti ai modelli |
    | `plugin-sdk/webhook-targets` | Registro delle destinazioni webhook e helper di installazione delle route |
    | `plugin-sdk/webhook-path` | Helper per normalizzazione del percorso webhook |
    | `plugin-sdk/web-media` | Helper condivisi per caricamento di media remoti/locali |
    | `plugin-sdk/zod` | `zod` riesportato per i consumer del plugin SDK |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="Sottopercorsi della memoria">
    | Sottopercorso | Esportazioni chiave |
    | --- | --- |
    | `plugin-sdk/memory-core` | Superficie helper bundled memory-core per helper di manager/config/file/CLI |
    | `plugin-sdk/memory-core-engine-runtime` | Facciata runtime per indice/ricerca della memoria |
    | `plugin-sdk/memory-core-host-engine-foundation` | Esportazioni del motore foundation dell'host memoria |
    | `plugin-sdk/memory-core-host-engine-embeddings` | Esportazioni del motore embeddings dell'host memoria |
    | `plugin-sdk/memory-core-host-engine-qmd` | Esportazioni del motore QMD dell'host memoria |
    | `plugin-sdk/memory-core-host-engine-storage` | Esportazioni del motore storage dell'host memoria |
    | `plugin-sdk/memory-core-host-multimodal` | Helper multimodali dell'host memoria |
    | `plugin-sdk/memory-core-host-query` | Helper di query dell'host memoria |
    | `plugin-sdk/memory-core-host-secret` | Helper dei secret dell'host memoria |
    | `plugin-sdk/memory-core-host-events` | Helper del journal eventi dell'host memoria |
    | `plugin-sdk/memory-core-host-status` | Helper di stato dell'host memoria |
    | `plugin-sdk/memory-core-host-runtime-cli` | Helper runtime CLI dell'host memoria |
    | `plugin-sdk/memory-core-host-runtime-core` | Helper core runtime dell'host memoria |
    | `plugin-sdk/memory-core-host-runtime-files` | Helper per file/runtime dell'host memoria |
    | `plugin-sdk/memory-host-core` | Alias neutrale rispetto al vendor per gli helper core runtime dell'host memoria |
    | `plugin-sdk/memory-host-events` | Alias neutrale rispetto al vendor per gli helper del journal eventi dell'host memoria |
    | `plugin-sdk/memory-host-files` | Alias neutrale rispetto al vendor per gli helper file/runtime dell'host memoria |
    | `plugin-sdk/memory-host-markdown` | Helper condivisi per managed-markdown per plugin adiacenti alla memoria |
    | `plugin-sdk/memory-host-search` | Facciata runtime della memoria attiva per l'accesso al search-manager |
    | `plugin-sdk/memory-host-status` | Alias neutrale rispetto al vendor per gli helper di stato dell'host memoria |
    | `plugin-sdk/memory-lancedb` | Superficie helper bundled memory-lancedb |
  </Accordion>

  <Accordion title="Sottopercorsi helper riservati ai bundled">
    | Famiglia | Sottopercorsi attuali | Uso previsto |
    | --- | --- | --- |
    | Browser | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | Helper di supporto per il plugin browser bundled (`browser-support` resta il barrel di compatibilità) |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | Superficie helper/runtime Matrix bundled |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | Superficie helper/runtime LINE bundled |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | Superficie helper IRC bundled |
    | Helper specifici del canale | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | Seam di compatibilità/helper per canali bundled |
    | Helper specifici di auth/plugin | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | Seam helper per funzionalità/plugin bundled; `plugin-sdk/github-copilot-token` esporta attualmente `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken` e `resolveCopilotApiToken` |
  </Accordion>
</AccordionGroup>

## API di registrazione

La callback `register(api)` riceve un oggetto `OpenClawPluginApi` con questi
metodi:

### Registrazione delle capability

| Metodo                                           | Cosa registra                          |
| ------------------------------------------------ | -------------------------------------- |
| `api.registerProvider(...)`                      | Inferenza testuale (LLM)               |
| `api.registerAgentHarness(...)`                  | Esecutore sperimentale di basso livello dell'agente |
| `api.registerCliBackend(...)`                    | Backend CLI locale per inferenza       |
| `api.registerChannel(...)`                       | Canale di messaggistica                |
| `api.registerSpeechProvider(...)`                | Sintesi text-to-speech / STT           |
| `api.registerRealtimeTranscriptionProvider(...)` | Trascrizione realtime in streaming     |
| `api.registerRealtimeVoiceProvider(...)`         | Sessioni vocali realtime duplex        |
| `api.registerMediaUnderstandingProvider(...)`    | Analisi di immagini/audio/video        |
| `api.registerImageGenerationProvider(...)`       | Generazione immagini                   |
| `api.registerMusicGenerationProvider(...)`       | Generazione musicale                   |
| `api.registerVideoGenerationProvider(...)`       | Generazione video                      |
| `api.registerWebFetchProvider(...)`              | Provider di fetch / scraping web       |
| `api.registerWebSearchProvider(...)`             | Ricerca web                            |

### Strumenti e comandi

| Metodo                          | Cosa registra                                |
| ------------------------------- | -------------------------------------------- |
| `api.registerTool(tool, opts?)` | Strumento dell'agente (obbligatorio o `{ optional: true }`) |
| `api.registerCommand(def)`      | Comando personalizzato (bypassa l'LLM)       |

### Infrastruttura

| Metodo                                         | Cosa registra                          |
| ---------------------------------------------- | -------------------------------------- |
| `api.registerHook(events, handler, opts?)`     | Hook evento                            |
| `api.registerHttpRoute(params)`                | Endpoint HTTP del Gateway              |
| `api.registerGatewayMethod(name, handler)`     | Metodo RPC del Gateway                 |
| `api.registerCli(registrar, opts?)`            | Sottocomando CLI                       |
| `api.registerService(service)`                 | Servizio in background                 |
| `api.registerInteractiveHandler(registration)` | Gestore interattivo                    |
| `api.registerMemoryPromptSupplement(builder)`  | Sezione di prompt additiva adiacente alla memoria |
| `api.registerMemoryCorpusSupplement(adapter)`  | Corpus additivo per ricerca/lettura della memoria |

Gli spazi dei nomi di amministrazione core riservati (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`) restano sempre `operator.admin`, anche se un plugin prova ad assegnare uno
scope più ristretto a un metodo gateway. Preferisci prefissi specifici del plugin per
metodi posseduti dal plugin.

### Metadati di registrazione CLI

`api.registerCli(registrar, opts?)` accetta due tipi di metadati di livello superiore:

- `commands`: radici di comando esplicite possedute dal registrar
- `descriptors`: descrittori di comando a tempo di parsing usati per help della CLI root,
  instradamento e registrazione lazy della CLI del plugin

Se vuoi che un comando del plugin resti caricato lazy nel normale percorso CLI root,
fornisci `descriptors` che coprano ogni radice di comando di livello superiore esposta da quel
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
        description: "Manage Matrix accounts, verification, devices, and profile state",
        hasSubcommands: true,
      },
    ],
  },
);
```

Usa `commands` da solo solo quando non ti serve la registrazione lazy della CLI root.
Quel percorso di compatibilità eager continua a essere supportato, ma non installa
segnaposto supportati da descriptor per il caricamento lazy a tempo di parsing.

### Registrazione del backend CLI

`api.registerCliBackend(...)` consente a un plugin di possedere la configurazione predefinita per un backend
CLI AI locale come `codex-cli`.

- L'`id` del backend diventa il prefisso provider nei riferimenti ai modelli come `codex-cli/gpt-5`.
- La `config` del backend usa la stessa struttura di `agents.defaults.cliBackends.<id>`.
- La configurazione utente continua ad avere la precedenza. OpenClaw unisce `agents.defaults.cliBackends.<id>` sopra la
  configurazione predefinita del plugin prima di eseguire la CLI.
- Usa `normalizeConfig` quando un backend necessita di riscritture di compatibilità dopo l'unione
  (ad esempio normalizzare vecchie forme di flag).

### Slot esclusivi

| Metodo                                     | Cosa registra                                                                                                                                         |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `api.registerContextEngine(id, factory)`   | Motore di contesto (uno attivo alla volta). La callback `assemble()` riceve `availableTools` e `citationsMode` così il motore può adattare le aggiunte al prompt. |
| `api.registerMemoryCapability(capability)` | Capability di memoria unificata                                                                                                                       |
| `api.registerMemoryPromptSection(builder)` | Builder di sezione del prompt di memoria                                                                                                              |
| `api.registerMemoryFlushPlan(resolver)`    | Risolutore del piano di flush della memoria                                                                                                           |
| `api.registerMemoryRuntime(runtime)`       | Adattatore runtime della memoria                                                                                                                      |

### Adattatori di embedding della memoria

| Metodo                                         | Cosa registra                                   |
| ---------------------------------------------- | ----------------------------------------------- |
| `api.registerMemoryEmbeddingProvider(adapter)` | Adattatore di embedding della memoria per il plugin attivo |

- `registerMemoryCapability` è l'API preferita del plugin di memoria esclusivo.
- `registerMemoryCapability` può anche esporre `publicArtifacts.listArtifacts(...)`
  così i plugin companion possono usare gli artifact di memoria esportati tramite
  `openclaw/plugin-sdk/memory-host-core` invece di raggiungere il layout privato
  di uno specifico plugin di memoria.
- `registerMemoryPromptSection`, `registerMemoryFlushPlan` e
  `registerMemoryRuntime` sono API esclusive del plugin di memoria compatibili con i sistemi legacy.
- `registerMemoryEmbeddingProvider` consente al plugin di memoria attivo di registrare uno
  o più id di adattatore embedding (ad esempio `openai`, `gemini` o un id personalizzato definito dal plugin).
- La configurazione utente come `agents.defaults.memorySearch.provider` e
  `agents.defaults.memorySearch.fallback` viene risolta rispetto agli id di adattatore registrati.

### Eventi e ciclo di vita

| Metodo                                       | Cosa fa                     |
| -------------------------------------------- | --------------------------- |
| `api.on(hookName, handler, opts?)`           | Hook di ciclo di vita tipizzato |
| `api.onConversationBindingResolved(handler)` | Callback del binding della conversazione |

### Semantica delle decisioni degli hook

- `before_tool_call`: restituire `{ block: true }` è terminale. Non appena un handler lo imposta, gli handler a priorità più bassa vengono saltati.
- `before_tool_call`: restituire `{ block: false }` viene trattato come nessuna decisione (come omettere `block`), non come un override.
- `before_install`: restituire `{ block: true }` è terminale. Non appena un handler lo imposta, gli handler a priorità più bassa vengono saltati.
- `before_install`: restituire `{ block: false }` viene trattato come nessuna decisione (come omettere `block`), non come un override.
- `reply_dispatch`: restituire `{ handled: true, ... }` è terminale. Non appena un handler rivendica il dispatch, gli handler a priorità più bassa e il percorso di dispatch predefinito del modello vengono saltati.
- `message_sending`: restituire `{ cancel: true }` è terminale. Non appena un handler lo imposta, gli handler a priorità più bassa vengono saltati.
- `message_sending`: restituire `{ cancel: false }` viene trattato come nessuna decisione (come omettere `cancel`), non come un override.

### Campi dell'oggetto API

| Campo                    | Tipo                      | Descrizione                                                                                 |
| ------------------------ | ------------------------- | ------------------------------------------------------------------------------------------- |
| `api.id`                 | `string`                  | ID del plugin                                                                               |
| `api.name`               | `string`                  | Nome visualizzato                                                                           |
| `api.version`            | `string?`                 | Versione del plugin (facoltativa)                                                           |
| `api.description`        | `string?`                 | Descrizione del plugin (facoltativa)                                                        |
| `api.source`             | `string`                  | Percorso sorgente del plugin                                                                |
| `api.rootDir`            | `string?`                 | Directory root del plugin (facoltativa)                                                     |
| `api.config`             | `OpenClawConfig`          | Snapshot della configurazione corrente (snapshot runtime in memoria attivo quando disponibile) |
| `api.pluginConfig`       | `Record<string, unknown>` | Configurazione specifica del plugin da `plugins.entries.<id>.config`                        |
| `api.runtime`            | `PluginRuntime`           | [Helper di runtime](/it/plugins/sdk-runtime)                                                   |
| `api.logger`             | `PluginLogger`            | Logger con scope (`debug`, `info`, `warn`, `error`)                                         |
| `api.registrationMode`   | `PluginRegistrationMode`  | Modalità di caricamento corrente; `"setup-runtime"` è la finestra leggera di avvio/setup prima dell'entry completa |
| `api.resolvePath(input)` | `(string) => string`      | Risolve il percorso relativo alla root del plugin                                           |

## Convenzione dei moduli interni

All'interno del tuo plugin, usa file barrel locali per gli import interni:

```
my-plugin/
  api.ts            # Esportazioni pubbliche per consumer esterni
  runtime-api.ts    # Esportazioni runtime solo interne
  index.ts          # Punto di ingresso del plugin
  setup-entry.ts    # Entry leggera solo setup (facoltativa)
```

<Warning>
  Non importare mai il tuo plugin tramite `openclaw/plugin-sdk/<your-plugin>`
  dal codice di produzione. Instrada gli import interni tramite `./api.ts` o
  `./runtime-api.ts`. Il percorso SDK è solo il contratto esterno.
</Warning>

Le superfici pubbliche dei plugin bundled caricate tramite facade (`api.ts`, `runtime-api.ts`,
`index.ts`, `setup-entry.ts` e file entry pubblici simili) ora preferiscono lo
snapshot attivo della configurazione runtime quando OpenClaw è già in esecuzione. Se non esiste ancora
uno snapshot runtime, ricadono sulla configurazione risolta su disco.

I plugin provider possono anche esporre un barrel di contratto locale al plugin quando un
helper è intenzionalmente specifico del provider e non appartiene ancora a un sottopercorso SDK
generico. Esempio bundled attuale: il provider Anthropic mantiene i suoi helper di stream Claude
nel proprio seam pubblico `api.ts` / `contract-api.ts` invece di promuovere la logica
dell'header beta Anthropic e `service_tier` in un contratto generico
`plugin-sdk/*`.

Altri esempi bundled attuali:

- `@openclaw/openai-provider`: `api.ts` esporta builder del provider,
  helper per il modello predefinito e builder del provider realtime
- `@openclaw/openrouter-provider`: `api.ts` esporta il builder del provider più
  helper di onboarding/configurazione

<Warning>
  Anche il codice di produzione delle estensioni dovrebbe evitare import da `openclaw/plugin-sdk/<other-plugin>`.
  Se un helper è davvero condiviso, promuovilo a un sottopercorso SDK neutrale
  come `openclaw/plugin-sdk/speech`, `.../provider-model-shared` o un'altra
  superficie orientata alle capability invece di accoppiare due plugin tra loro.
</Warning>

## Correlati

- [Punti di ingresso](/it/plugins/sdk-entrypoints) — opzioni di `definePluginEntry` e `defineChannelPluginEntry`
- [Helper di runtime](/it/plugins/sdk-runtime) — riferimento completo dello spazio dei nomi `api.runtime`
- [Setup e configurazione](/it/plugins/sdk-setup) — packaging, manifest, schemi di configurazione
- [Test](/it/plugins/sdk-testing) — utility di test e regole lint
- [Migrazione SDK](/it/plugins/sdk-migration) — migrazione dalle superfici deprecate
- [Interni del plugin](/it/plugins/architecture) — architettura approfondita e modello delle capability
