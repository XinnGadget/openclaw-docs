---
read_when:
    - Vedi l'avviso OPENCLAW_PLUGIN_SDK_COMPAT_DEPRECATED
    - Vedi l'avviso OPENCLAW_EXTENSION_API_DEPRECATED
    - Stai aggiornando un plugin alla moderna architettura dei plugin
    - Mantieni un plugin OpenClaw esterno
sidebarTitle: Migrate to SDK
summary: Migra dal livello legacy di retrocompatibilità al moderno Plugin SDK
title: Migrazione del Plugin SDK
x-i18n:
    generated_at: "2026-04-08T02:17:25Z"
    model: gpt-5.4
    provider: openai
    source_hash: 155a8b14bc345319c8516ebdb8a0ccdea2c5f7fa07dad343442996daee21ecad
    source_path: plugins/sdk-migration.md
    workflow: 15
---

# Migrazione del Plugin SDK

OpenClaw è passato da un ampio livello di retrocompatibilità a una moderna
architettura dei plugin con import focalizzati e documentati. Se il tuo plugin è stato creato prima
della nuova architettura, questa guida ti aiuta nella migrazione.

## Che cosa sta cambiando

Il vecchio sistema di plugin forniva due superfici molto ampie che permettevano ai plugin di importare
qualsiasi cosa servisse da un singolo punto di ingresso:

- **`openclaw/plugin-sdk/compat`** — un singolo import che riesportava decine di
  helper. È stato introdotto per mantenere funzionanti i plugin più vecchi basati su hook mentre veniva costruita la
  nuova architettura dei plugin.
- **`openclaw/extension-api`** — un ponte che dava ai plugin accesso diretto a
  helper lato host come il runner incorporato dell'agente.

Entrambe le superfici sono ora **deprecate**. Funzionano ancora a runtime, ma i nuovi
plugin non devono usarle e i plugin esistenti dovrebbero migrare prima che la prossima
major release le rimuova.

<Warning>
  Il livello di retrocompatibilità verrà rimosso in una futura major release.
  I plugin che importano ancora da queste superfici smetteranno di funzionare quando ciò accadrà.
</Warning>

## Perché è cambiato

Il vecchio approccio causava problemi:

- **Avvio lento** — importare un helper caricava decine di moduli non correlati
- **Dipendenze circolari** — riesportazioni ampie rendevano facile creare cicli di import
- **Superficie API poco chiara** — non c'era modo di capire quali export fossero stabili e quali interni

Il moderno Plugin SDK risolve questo problema: ogni percorso di import (`openclaw/plugin-sdk/\<subpath\>`)
è un modulo piccolo e autonomo con uno scopo chiaro e un contratto documentato.

Anche le convenience seam legacy dei provider per i canali bundled non esistono più. Import
come `openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp`,
seam helper brandizzate per canale e
`openclaw/plugin-sdk/telegram-core` erano scorciatoie private del mono-repo, non
contratti stabili per plugin. Usa invece subpath generici e ristretti del SDK. All'interno del
workspace plugin bundled, mantieni gli helper gestiti dal provider nel file
`api.ts` o `runtime-api.ts` del plugin stesso.

Esempi bundled attuali di provider:

- Anthropic mantiene gli helper di stream specifici per Claude nella propria seam `api.ts` /
  `contract-api.ts`
- OpenAI mantiene builder del provider, helper del modello predefinito e builder del provider
  realtime nel proprio `api.ts`
- OpenRouter mantiene builder del provider e helper di onboarding/configurazione nel proprio
  `api.ts`

## Come migrare

<Steps>
  <Step title="Migra gli handler approval-native ai capability fact">
    I plugin di canale con capacità di approvazione ora espongono il comportamento di approvazione nativo tramite
    `approvalCapability.nativeRuntime` più il registro condiviso del runtime context.

    Cambiamenti principali:

    - Sostituisci `approvalCapability.handler.loadRuntime(...)` con
      `approvalCapability.nativeRuntime`
    - Sposta autenticazione/consegna specifiche per l'approvazione dal wiring legacy `plugin.auth` /
      `plugin.approvals` a `approvalCapability`
    - `ChannelPlugin.approvals` è stato rimosso dal contratto pubblico dei plugin di canale;
      sposta i campi delivery/native/render su `approvalCapability`
    - `plugin.auth` resta per i soli flussi di login/logout del canale; gli hook auth
      per l'approvazione lì non vengono più letti dal core
    - Registra gli oggetti runtime gestiti dal canale come client, token o app
      Bolt tramite `openclaw/plugin-sdk/channel-runtime-context`
    - Non inviare avvisi di reroute gestiti dal plugin dagli handler di approvazione nativa;
      il core ora gestisce gli avvisi di instradamento altrove dai risultati reali di delivery
    - Quando passi `channelRuntime` a `createChannelManager(...)`, fornisci una
      superficie reale `createPluginRuntime().channel`. Gli stub parziali vengono rifiutati.

    Vedi `/plugins/sdk-channel-plugins` per il layout attuale
    delle capability di approvazione.

  </Step>

  <Step title="Controlla il comportamento di fallback del wrapper Windows">
    Se il tuo plugin usa `openclaw/plugin-sdk/windows-spawn`, i wrapper Windows
    `.cmd`/`.bat` non risolti ora falliscono in modalità chiusa a meno che tu non passi esplicitamente
    `allowShellFallback: true`.

    ```typescript
    // Before
    const program = applyWindowsSpawnProgramPolicy({ candidate });

    // After
    const program = applyWindowsSpawnProgramPolicy({
      candidate,
      // Only set this for trusted compatibility callers that intentionally
      // accept shell-mediated fallback.
      allowShellFallback: true,
    });
    ```

    Se il tuo chiamante non si basa intenzionalmente sul fallback della shell, non impostare
    `allowShellFallback` e gestisci invece l'errore sollevato.

  </Step>

  <Step title="Trova gli import deprecati">
    Cerca nel tuo plugin gli import da una delle due superfici deprecate:

    ```bash
    grep -r "plugin-sdk/compat" my-plugin/
    grep -r "openclaw/extension-api" my-plugin/
    ```

  </Step>

  <Step title="Sostituisci con import focalizzati">
    Ogni export della vecchia superficie corrisponde a uno specifico percorso di import moderno:

    ```typescript
    // Before (deprecated backwards-compatibility layer)
    import {
      createChannelReplyPipeline,
      createPluginRuntimeStore,
      resolveControlCommandGate,
    } from "openclaw/plugin-sdk/compat";

    // After (modern focused imports)
    import { createChannelReplyPipeline } from "openclaw/plugin-sdk/channel-reply-pipeline";
    import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
    import { resolveControlCommandGate } from "openclaw/plugin-sdk/command-auth";
    ```

    Per gli helper lato host, usa il runtime del plugin iniettato invece di importare
    direttamente:

    ```typescript
    // Before (deprecated extension-api bridge)
    import { runEmbeddedPiAgent } from "openclaw/extension-api";
    const result = await runEmbeddedPiAgent({ sessionId, prompt });

    // After (injected runtime)
    const result = await api.runtime.agent.runEmbeddedPiAgent({ sessionId, prompt });
    ```

    Lo stesso schema si applica agli altri helper del bridge legacy:

    | Vecchio import | Equivalente moderno |
    | --- | --- |
    | `resolveAgentDir` | `api.runtime.agent.resolveAgentDir` |
    | `resolveAgentWorkspaceDir` | `api.runtime.agent.resolveAgentWorkspaceDir` |
    | `resolveAgentIdentity` | `api.runtime.agent.resolveAgentIdentity` |
    | `resolveThinkingDefault` | `api.runtime.agent.resolveThinkingDefault` |
    | `resolveAgentTimeoutMs` | `api.runtime.agent.resolveAgentTimeoutMs` |
    | `ensureAgentWorkspace` | `api.runtime.agent.ensureAgentWorkspace` |
    | helper dello session store | `api.runtime.agent.session.*` |

  </Step>

  <Step title="Compila e testa">
    ```bash
    pnpm build
    pnpm test -- my-plugin/
    ```
  </Step>
</Steps>

## Riferimento dei percorsi di import

<Accordion title="Tabella comune dei percorsi di import">
  | Percorso di import | Scopo | Export principali |
  | --- | --- | --- |
  | `plugin-sdk/plugin-entry` | Helper canonico per l'entry del plugin | `definePluginEntry` |
  | `plugin-sdk/core` | Riesportazione legacy ombrello per definizioni/builder di entry dei canali | `defineChannelPluginEntry`, `createChatChannelPlugin` |
  | `plugin-sdk/config-schema` | Export dello schema di configurazione root | `OpenClawSchema` |
  | `plugin-sdk/provider-entry` | Helper di entry per provider singolo | `defineSingleProviderPluginEntry` |
  | `plugin-sdk/channel-core` | Definizioni e builder focalizzati per entry di canale | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
  | `plugin-sdk/setup` | Helper condivisi del setup wizard | Prompt allowlist, builder dello stato di setup |
  | `plugin-sdk/setup-runtime` | Helper runtime in fase di setup | Adapter di patch del setup sicuri da importare, helper per note di lookup, `promptResolvedAllowFrom`, `splitSetupEntries`, proxy di setup delegati |
  | `plugin-sdk/setup-adapter-runtime` | Helper per adapter di setup | `createEnvPatchedAccountSetupAdapter` |
  | `plugin-sdk/setup-tools` | Helper di tooling per il setup | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
  | `plugin-sdk/account-core` | Helper multi-account | Helper per elenco/configurazione/account-action-gate |
  | `plugin-sdk/account-id` | Helper per account-id | `DEFAULT_ACCOUNT_ID`, normalizzazione account-id |
  | `plugin-sdk/account-resolution` | Helper per ricerca account | Helper per lookup dell'account + fallback al predefinito |
  | `plugin-sdk/account-helpers` | Helper account ristretti | Helper per elenco account/account-action |
  | `plugin-sdk/channel-setup` | Adapter del setup wizard | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, più `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
  | `plugin-sdk/channel-pairing` | Primitive per il pairing DM | `createChannelPairingController` |
  | `plugin-sdk/channel-reply-pipeline` | Wiring del prefisso di reply + typing | `createChannelReplyPipeline` |
  | `plugin-sdk/channel-config-helpers` | Factory per adapter di configurazione | `createHybridChannelConfigAdapter` |
  | `plugin-sdk/channel-config-schema` | Builder di schema di configurazione | Tipi di schema di configurazione del canale |
  | `plugin-sdk/telegram-command-config` | Helper per configurazione dei comandi Telegram | Normalizzazione dei nomi comando, trimming delle descrizioni, validazione di duplicati/conflitti |
  | `plugin-sdk/channel-policy` | Risoluzione delle policy gruppo/DM | `resolveChannelGroupRequireMention` |
  | `plugin-sdk/channel-lifecycle` | Tracciamento dello stato account | `createAccountStatusSink` |
  | `plugin-sdk/inbound-envelope` | Helper per inbound envelope | Helper condivisi per route + builder di envelope |
  | `plugin-sdk/inbound-reply-dispatch` | Helper per reply inbound | Helper condivisi per registrazione e dispatch |
  | `plugin-sdk/messaging-targets` | Parsing dei target di messaggistica | Helper per parsing/matching dei target |
  | `plugin-sdk/outbound-media` | Helper per media outbound | Caricamento condiviso dei media outbound |
  | `plugin-sdk/outbound-runtime` | Helper runtime outbound | Helper per identità outbound/delega di invio |
  | `plugin-sdk/thread-bindings-runtime` | Helper per thread-binding | Ciclo di vita dei thread-binding e helper per adapter |
  | `plugin-sdk/agent-media-payload` | Helper legacy per payload media | Builder di payload media dell'agente per layout legacy dei campi |
  | `plugin-sdk/channel-runtime` | Shim di compatibilità deprecato | Solo utility legacy di runtime del canale |
  | `plugin-sdk/channel-send-result` | Tipi di risultato dell'invio | Tipi di risultato della reply |
  | `plugin-sdk/runtime-store` | Storage persistente del plugin | `createPluginRuntimeStore` |
  | `plugin-sdk/runtime` | Helper runtime ampi | Helper per runtime/logging/backup/installazione plugin |
  | `plugin-sdk/runtime-env` | Helper runtime env ristretti | Logger/runtime env, helper per timeout, retry e backoff |
  | `plugin-sdk/plugin-runtime` | Helper runtime condivisi del plugin | Helper per comandi/hook/http/interattivi del plugin |
  | `plugin-sdk/hook-runtime` | Helper per pipeline di hook | Helper condivisi per pipeline di webhook/hook interni |
  | `plugin-sdk/lazy-runtime` | Helper per runtime lazy | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeMethodBinder`, `createLazyRuntimeNamedExport`, `createLazyRuntimeSurface` |
  | `plugin-sdk/process-runtime` | Helper di processo | Helper condivisi di exec |
  | `plugin-sdk/cli-runtime` | Helper runtime CLI | Formattazione dei comandi, attese, helper per versione |
  | `plugin-sdk/gateway-runtime` | Helper del gateway | Helper per client gateway e patch dello stato del canale |
  | `plugin-sdk/config-runtime` | Helper di configurazione | Helper per caricamento/scrittura della configurazione |
  | `plugin-sdk/telegram-command-config` | Helper per comandi Telegram | Helper di validazione dei comandi Telegram stabili in fallback quando la superficie contrattuale bundled di Telegram non è disponibile |
  | `plugin-sdk/approval-runtime` | Helper per prompt di approvazione | Payload di approvazione exec/plugin, helper per capability/profilo di approvazione, helper nativi di routing/runtime per approvazione |
  | `plugin-sdk/approval-auth-runtime` | Helper auth per approvazione | Risoluzione dell'approver, auth per azioni nella stessa chat |
  | `plugin-sdk/approval-client-runtime` | Helper client per approvazione | Helper nativi di profilo/filtro per approvazione exec |
  | `plugin-sdk/approval-delivery-runtime` | Helper delivery per approvazione | Adapter nativi di capability/delivery per approvazione |
  | `plugin-sdk/approval-gateway-runtime` | Helper gateway per approvazione | Helper condiviso di risoluzione del gateway di approvazione |
  | `plugin-sdk/approval-handler-adapter-runtime` | Helper adapter per approvazione | Helper leggeri per il caricamento di adapter di approvazione nativa per entrypoint di canale hot |
  | `plugin-sdk/approval-handler-runtime` | Helper handler per approvazione | Helper runtime più ampi per handler di approvazione; preferisci le seam adapter/gateway più ristrette quando bastano |
  | `plugin-sdk/approval-native-runtime` | Helper per target di approvazione | Helper nativi per binding target/account di approvazione |
  | `plugin-sdk/approval-reply-runtime` | Helper reply per approvazione | Helper per payload di reply di approvazione exec/plugin |
  | `plugin-sdk/channel-runtime-context` | Helper per runtime-context del canale | Helper generici per register/get/watch del runtime-context del canale |
  | `plugin-sdk/security-runtime` | Helper di sicurezza | Helper condivisi per trust, gating DM, contenuti esterni e raccolta segreti |
  | `plugin-sdk/ssrf-policy` | Helper di policy SSRF | Helper per host allowlist e policy di rete privata |
  | `plugin-sdk/ssrf-runtime` | Helper runtime SSRF | Helper per pinned-dispatcher, fetch protetto e policy SSRF |
  | `plugin-sdk/collection-runtime` | Helper per cache limitata | `pruneMapToMaxSize` |
  | `plugin-sdk/diagnostic-runtime` | Helper per gating diagnostico | `isDiagnosticFlagEnabled`, `isDiagnosticsEnabled` |
  | `plugin-sdk/error-runtime` | Helper per formattazione degli errori | `formatUncaughtError`, `isApprovalNotFoundError`, helper per grafo degli errori |
  | `plugin-sdk/fetch-runtime` | Helper per fetch/proxy wrapperizzati | `resolveFetch`, helper per proxy |
  | `plugin-sdk/host-runtime` | Helper di normalizzazione host | `normalizeHostname`, `normalizeScpRemoteHost` |
  | `plugin-sdk/retry-runtime` | Helper per retry | `RetryConfig`, `retryAsync`, runner di policy |
  | `plugin-sdk/allow-from` | Formattazione allowlist | `formatAllowFromLowercase` |
  | `plugin-sdk/allowlist-resolution` | Mapping dell'input allowlist | `mapAllowlistResolutionInputs` |
  | `plugin-sdk/command-auth` | Gating dei comandi e helper per la command surface | `resolveControlCommandGate`, helper di autorizzazione del mittente, helper del registro comandi |
  | `plugin-sdk/secret-input` | Parsing dell'input segreto | Helper per input segreto |
  | `plugin-sdk/webhook-ingress` | Helper per richieste webhook | Utility per target webhook |
  | `plugin-sdk/webhook-request-guards` | Helper di guardia del body webhook | Helper per lettura/limite del body della richiesta |
  | `plugin-sdk/reply-runtime` | Runtime condiviso per le reply | Dispatch inbound, heartbeat, pianificatore delle reply, chunking |
  | `plugin-sdk/reply-dispatch-runtime` | Helper ristretti per dispatch delle reply | Helper per finalize + dispatch del provider |
  | `plugin-sdk/reply-history` | Helper per la cronologia delle reply | `buildHistoryContext`, `buildPendingHistoryContextFromMap`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` |
  | `plugin-sdk/reply-reference` | Pianificazione dei riferimenti di reply | `createReplyReferencePlanner` |
  | `plugin-sdk/reply-chunking` | Helper per chunk di reply | Helper per chunking di testo/markdown |
  | `plugin-sdk/session-store-runtime` | Helper per session store | Percorso dello store + helper updated-at |
  | `plugin-sdk/state-paths` | Helper per path di stato | Helper per directory di stato e OAuth |
  | `plugin-sdk/routing` | Helper di instradamento/session-key | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId`, helper di normalizzazione delle session-key |
  | `plugin-sdk/status-helpers` | Helper per stato del canale | Builder di riepilogo dello stato di canale/account, valori predefiniti dello stato runtime, helper per metadati dei problemi |
  | `plugin-sdk/target-resolver-runtime` | Helper per il resolver del target | Helper condivisi per il resolver del target |
  | `plugin-sdk/string-normalization-runtime` | Helper per normalizzazione delle stringhe | Helper per normalizzazione di slug/stringhe |
  | `plugin-sdk/request-url` | Helper per URL di richiesta | Estrazione di URL stringa da input simili a richieste |
  | `plugin-sdk/run-command` | Helper per comandi temporizzati | Runner di comandi temporizzati con stdout/stderr normalizzati |
  | `plugin-sdk/param-readers` | Lettori di parametri | Lettori comuni di parametri tool/CLI |
  | `plugin-sdk/tool-send` | Estrazione dell'invio del tool | Estrae campi target canonici di invio dagli argomenti del tool |
  | `plugin-sdk/temp-path` | Helper per path temporanei | Helper condivisi per path temporanei di download |
  | `plugin-sdk/logging-core` | Helper di logging | Logger di sottosistema e helper di redazione |
  | `plugin-sdk/markdown-table-runtime` | Helper per tabelle Markdown | Helper per modalità tabella Markdown |
  | `plugin-sdk/reply-payload` | Tipi di reply dei messaggi | Tipi di payload della reply |
  | `plugin-sdk/provider-setup` | Helper selezionati per setup di provider locali/self-hosted | Helper di discovery/configurazione per provider self-hosted |
  | `plugin-sdk/self-hosted-provider-setup` | Helper focalizzati per setup di provider self-hosted compatibili con OpenAI | Gli stessi helper di discovery/configurazione per provider self-hosted |
  | `plugin-sdk/provider-auth-runtime` | Helper di auth runtime del provider | Helper per risoluzione runtime delle API key |
  | `plugin-sdk/provider-auth-api-key` | Helper di setup API key del provider | Helper per onboarding/scrittura del profilo con API key |
  | `plugin-sdk/provider-auth-result` | Helper per auth-result del provider | Builder standard del risultato auth OAuth |
  | `plugin-sdk/provider-auth-login` | Helper per login interattivo del provider | Helper condivisi per login interattivo |
  | `plugin-sdk/provider-env-vars` | Helper per env var del provider | Helper di lookup delle env var auth del provider |
  | `plugin-sdk/provider-model-shared` | Helper condivisi per modello/replay del provider | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, builder condivisi di replay-policy, helper per endpoint del provider e helper di normalizzazione degli id modello |
  | `plugin-sdk/provider-catalog-shared` | Helper condivisi per catalogo provider | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
  | `plugin-sdk/provider-onboard` | Patch di onboarding del provider | Helper di configurazione per l'onboarding |
  | `plugin-sdk/provider-http` | Helper HTTP del provider | Helper generici per capacità HTTP/endpoint del provider |
  | `plugin-sdk/provider-web-fetch` | Helper web-fetch del provider | Helper per registrazione/cache del provider web-fetch |
  | `plugin-sdk/provider-web-search-contract` | Helper del contratto web-search del provider | Helper ristretti per il contratto di configurazione/credenziali della web search come `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig` e setter/getter di credenziali con scope |
  | `plugin-sdk/provider-web-search` | Helper web-search del provider | Helper per registrazione/cache/runtime del provider web-search |
  | `plugin-sdk/provider-tools` | Helper di compatibilità tool/schema del provider | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, pulizia degli schemi Gemini + diagnostica e helper di compatibilità xAI come `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
  | `plugin-sdk/provider-usage` | Helper per usage del provider | `fetchClaudeUsage`, `fetchGeminiUsage`, `fetchGithubCopilotUsage` e altri helper per usage del provider |
  | `plugin-sdk/provider-stream` | Helper per wrapper di stream del provider | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, tipi di wrapper di stream e helper condivisi per wrapper Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
  | `plugin-sdk/keyed-async-queue` | Coda async ordinata | `KeyedAsyncQueue` |
  | `plugin-sdk/media-runtime` | Helper media condivisi | Helper per fetch/transform/store dei media più builder di payload media |
  | `plugin-sdk/media-generation-runtime` | Helper condivisi per generazione media | Helper condivisi per failover, selezione dei candidati e messaggistica di modello mancante per generazione di immagini/video/musica |
  | `plugin-sdk/media-understanding` | Helper per media-understanding | Tipi di provider per media understanding più export di helper immagine/audio orientati ai provider |
  | `plugin-sdk/text-runtime` | Helper di testo condivisi | Rimozione del testo visibile all'assistente, helper di render/chunking/tabella Markdown, helper di redazione, helper per directive-tag, utility di testo sicuro e relativi helper di testo/logging |
  | `plugin-sdk/text-chunking` | Helper per chunking del testo | Helper per chunking del testo in uscita |
  | `plugin-sdk/speech` | Helper per speech | Tipi di provider speech più export di helper per direttive, registro e validazione orientati ai provider |
  | `plugin-sdk/speech-core` | Core speech condiviso | Tipi di provider speech, registro, direttive, normalizzazione |
  | `plugin-sdk/realtime-transcription` | Helper per trascrizione realtime | Tipi di provider e helper di registro |
  | `plugin-sdk/realtime-voice` | Helper per voce realtime | Tipi di provider e helper di registro |
  | `plugin-sdk/image-generation-core` | Core condiviso per generazione immagini | Tipi, failover, auth e helper di registro per generazione immagini |
  | `plugin-sdk/music-generation` | Helper per generazione musicale | Tipi di provider/richiesta/risultato per generazione musicale |
  | `plugin-sdk/music-generation-core` | Core condiviso per generazione musicale | Tipi di generazione musicale, helper di failover, lookup del provider e parsing del model-ref |
  | `plugin-sdk/video-generation` | Helper per generazione video | Tipi di provider/richiesta/risultato per generazione video |
  | `plugin-sdk/video-generation-core` | Core condiviso per generazione video | Tipi di generazione video, helper di failover, lookup del provider e parsing del model-ref |
  | `plugin-sdk/interactive-runtime` | Helper per reply interattive | Normalizzazione/riduzione del payload delle reply interattive |
  | `plugin-sdk/channel-config-primitives` | Primitive di configurazione del canale | Primitive ristrette di schema per la configurazione del canale |
  | `plugin-sdk/channel-config-writes` | Helper per scrittura della configurazione del canale | Helper di autorizzazione per la scrittura della configurazione del canale |
  | `plugin-sdk/channel-plugin-common` | Prelude condiviso del canale | Export condivisi del prelude del plugin di canale |
  | `plugin-sdk/channel-status` | Helper di stato del canale | Helper condivisi per snapshot/riepilogo dello stato del canale |
  | `plugin-sdk/allowlist-config-edit` | Helper di configurazione allowlist | Helper per modifica/lettura della configurazione allowlist |
  | `plugin-sdk/group-access` | Helper per accesso ai gruppi | Helper condivisi per le decisioni di accesso ai gruppi |
  | `plugin-sdk/direct-dm` | Helper per direct-DM | Helper condivisi per auth/guard dei direct-DM |
  | `plugin-sdk/extension-shared` | Helper condivisi dell'estensione | Primitive helper per canali/status passivi e proxy ambient |
  | `plugin-sdk/webhook-targets` | Helper per target webhook | Registro dei target webhook e helper per installazione delle route |
  | `plugin-sdk/webhook-path` | Helper per path webhook | Helper per normalizzazione dei path webhook |
  | `plugin-sdk/web-media` | Helper media web condivisi | Helper per caricamento di media remoti/locali |
  | `plugin-sdk/zod` | Riesportazione Zod | Riesportazione di `zod` per i consumer del Plugin SDK |
  | `plugin-sdk/memory-core` | Helper bundled memory-core | Superficie helper per memory manager/config/file/CLI |
  | `plugin-sdk/memory-core-engine-runtime` | Facciata runtime del motore di memoria | Facciata runtime per indice/ricerca della memoria |
  | `plugin-sdk/memory-core-host-engine-foundation` | Motore foundation host della memoria | Export del motore foundation host della memoria |
  | `plugin-sdk/memory-core-host-engine-embeddings` | Motore embeddings host della memoria | Export del motore embeddings host della memoria |
  | `plugin-sdk/memory-core-host-engine-qmd` | Motore QMD host della memoria | Export del motore QMD host della memoria |
  | `plugin-sdk/memory-core-host-engine-storage` | Motore storage host della memoria | Export del motore storage host della memoria |
  | `plugin-sdk/memory-core-host-multimodal` | Helper multimodali host della memoria | Helper multimodali host della memoria |
  | `plugin-sdk/memory-core-host-query` | Helper query host della memoria | Helper query host della memoria |
  | `plugin-sdk/memory-core-host-secret` | Helper secret host della memoria | Helper secret host della memoria |
  | `plugin-sdk/memory-core-host-events` | Helper del journal eventi host della memoria | Helper del journal eventi host della memoria |
  | `plugin-sdk/memory-core-host-status` | Helper di stato host della memoria | Helper di stato host della memoria |
  | `plugin-sdk/memory-core-host-runtime-cli` | Runtime CLI host della memoria | Helper runtime CLI host della memoria |
  | `plugin-sdk/memory-core-host-runtime-core` | Runtime core host della memoria | Helper runtime core host della memoria |
  | `plugin-sdk/memory-core-host-runtime-files` | Helper file/runtime host della memoria | Helper file/runtime host della memoria |
  | `plugin-sdk/memory-host-core` | Alias runtime core host della memoria | Alias vendor-neutral per helper runtime core host della memoria |
  | `plugin-sdk/memory-host-events` | Alias journal eventi host della memoria | Alias vendor-neutral per helper del journal eventi host della memoria |
  | `plugin-sdk/memory-host-files` | Alias file/runtime host della memoria | Alias vendor-neutral per helper file/runtime host della memoria |
  | `plugin-sdk/memory-host-markdown` | Helper per markdown gestito | Helper condivisi di managed-markdown per plugin adiacenti alla memoria |
  | `plugin-sdk/memory-host-search` | Facciata di ricerca della memoria attiva | Facciata runtime lazy del search-manager della memoria attiva |
  | `plugin-sdk/memory-host-status` | Alias stato host della memoria | Alias vendor-neutral per helper di stato host della memoria |
  | `plugin-sdk/memory-lancedb` | Helper bundled memory-lancedb | Superficie helper di memory-lancedb |
  | `plugin-sdk/testing` | Utility di test | Helper e mock per test |
</Accordion>

Questa tabella è intenzionalmente il sottoinsieme comune per la migrazione, non l'intera
superficie del SDK. L'elenco completo di oltre 200 entrypoint si trova in
`scripts/lib/plugin-sdk-entrypoints.json`.

Quell'elenco include ancora alcune seam helper per plugin bundled come
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` e `plugin-sdk/matrix*`. Restano esportate per
la manutenzione e la compatibilità dei plugin bundled, ma sono intenzionalmente
omesse dalla tabella comune di migrazione e non sono il target consigliato per
nuovo codice plugin.

La stessa regola si applica ad altre famiglie di helper bundled come:

- helper di supporto browser: `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support`
- Matrix: `plugin-sdk/matrix*`
- LINE: `plugin-sdk/line*`
- IRC: `plugin-sdk/irc*`
- superfici bundled helper/plugin come `plugin-sdk/googlechat`,
  `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles*`,
  `plugin-sdk/mattermost*`, `plugin-sdk/msteams`,
  `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`,
  `plugin-sdk/twitch`,
  `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`,
  `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`,
  `plugin-sdk/thread-ownership` e `plugin-sdk/voice-call`

`plugin-sdk/github-copilot-token` attualmente espone la ristretta
superficie helper per token `DEFAULT_COPILOT_API_BASE_URL`,
`deriveCopilotApiBaseUrlFromToken` e `resolveCopilotApiToken`.

Usa l'import più ristretto che corrisponde al lavoro da svolgere. Se non riesci a trovare un export,
controlla il sorgente in `src/plugin-sdk/` o chiedi su Discord.

## Timeline di rimozione

| Quando | Che cosa succede |
| ---------------------- | ----------------------------------------------------------------------- |
| **Ora** | Le superfici deprecate emettono avvisi a runtime |
| **Prossima major release** | Le superfici deprecate verranno rimosse; i plugin che le usano ancora smetteranno di funzionare |

Tutti i plugin core sono già stati migrati. I plugin esterni dovrebbero migrare
prima della prossima major release.

## Sopprimere temporaneamente gli avvisi

Imposta queste variabili d'ambiente mentre lavori alla migrazione:

```bash
OPENCLAW_SUPPRESS_PLUGIN_SDK_COMPAT_WARNING=1 openclaw gateway run
OPENCLAW_SUPPRESS_EXTENSION_API_WARNING=1 openclaw gateway run
```

Questa è una via di fuga temporanea, non una soluzione permanente.

## Correlati

- [Getting Started](/it/plugins/building-plugins) — crea il tuo primo plugin
- [SDK Overview](/it/plugins/sdk-overview) — riferimento completo agli import per subpath
- [Channel Plugins](/it/plugins/sdk-channel-plugins) — creare plugin di canale
- [Provider Plugins](/it/plugins/sdk-provider-plugins) — creare plugin provider
- [Plugin Internals](/it/plugins/architecture) — approfondimento sull'architettura
- [Plugin Manifest](/it/plugins/manifest) — riferimento dello schema del manifest
