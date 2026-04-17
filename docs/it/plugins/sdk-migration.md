---
read_when:
    - Vedi l'avviso `OPENCLAW_PLUGIN_SDK_COMPAT_DEPRECATED`
    - Vedi l'avviso `OPENCLAW_EXTENSION_API_DEPRECATED`
    - Stai aggiornando un Plugin alla moderna architettura dei plugin
    - Gestisci un Plugin OpenClaw esterno
sidebarTitle: Migrate to SDK
summary: Migra dal livello legacy di retrocompatibilità al moderno Plugin SDK
title: Migrazione al Plugin SDK
x-i18n:
    generated_at: "2026-04-17T08:17:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: f0283f949eec358a12a0709db846cde2a1509f28e5c60db6e563cb8a540b979d
    source_path: plugins/sdk-migration.md
    workflow: 15
---

# Migrazione al Plugin SDK

OpenClaw è passato da un ampio livello di retrocompatibilità a una moderna
architettura dei plugin con import mirati e documentati. Se il tuo plugin è
stato creato prima della nuova architettura, questa guida ti aiuta a eseguire
la migrazione.

## Cosa sta cambiando

Il vecchio sistema dei plugin forniva due superfici molto ampie che
consentivano ai plugin di importare tutto ciò di cui avevano bisogno da un
unico punto di ingresso:

- **`openclaw/plugin-sdk/compat`** — un singolo import che riesportava decine di
  helper. È stato introdotto per mantenere funzionanti i plugin più vecchi
  basati su hook mentre veniva sviluppata la nuova architettura dei plugin.
- **`openclaw/extension-api`** — un bridge che dava ai plugin accesso diretto a
  helper lato host come l'embedded agent runner.

Entrambe le superfici sono ora **deprecate**. Continuano a funzionare a
runtime, ma i nuovi plugin non devono usarle e i plugin esistenti dovrebbero
migrare prima che la prossima major release le rimuova.

<Warning>
  Il livello di retrocompatibilità verrà rimosso in una futura major release.
  I plugin che continuano a importare da queste superfici smetteranno di
  funzionare quando ciò accadrà.
</Warning>

## Perché è cambiato

Il vecchio approccio causava problemi:

- **Avvio lento** — importare un helper caricava decine di moduli non correlati
- **Dipendenze circolari** — riesportazioni ampie rendevano facile creare cicli di importazione
- **Superficie API poco chiara** — non c'era modo di capire quali export fossero stabili e quali interni

Il moderno Plugin SDK risolve questo problema: ogni percorso di import
(`openclaw/plugin-sdk/\<subpath\>`) è un modulo piccolo e autosufficiente con
uno scopo chiaro e un contratto documentato.

Sono stati rimossi anche i legacy convenience seam dei provider per i canali
inclusi. Import come `openclaw/plugin-sdk/slack`,
`openclaw/plugin-sdk/discord`, `openclaw/plugin-sdk/signal`,
`openclaw/plugin-sdk/whatsapp`, i channel-branded helper seam e
`openclaw/plugin-sdk/telegram-core` erano scorciatoie private del mono-repo,
non contratti plugin stabili. Usa invece subpath SDK generici e mirati.
All'interno del workspace dei plugin inclusi, mantieni gli helper di proprietà
del provider nel file `api.ts` o `runtime-api.ts` del plugin stesso.

Esempi attuali di provider inclusi:

- Anthropic mantiene gli helper di stream specifici per Claude nel proprio seam
  `api.ts` / `contract-api.ts`
- OpenAI mantiene i provider builder, gli helper per i modelli predefiniti e i
  realtime provider builder nel proprio `api.ts`
- OpenRouter mantiene il provider builder e gli helper di onboarding/config nel
  proprio `api.ts`

## Come eseguire la migrazione

<Steps>
  <Step title="Migra gli handler approval-native ai capability fact">
    I plugin di canale con capacità di approvazione ora espongono il
    comportamento di approvazione nativo tramite
    `approvalCapability.nativeRuntime` più il registro condiviso del contesto di runtime.

    Modifiche principali:

    - Sostituisci `approvalCapability.handler.loadRuntime(...)` con
      `approvalCapability.nativeRuntime`
    - Sposta l'autenticazione/consegna specifica per l'approvazione dal legacy
      wiring `plugin.auth` / `plugin.approvals` a `approvalCapability`
    - `ChannelPlugin.approvals` è stato rimosso dal contratto pubblico del
      channel plugin; sposta i campi delivery/native/render in `approvalCapability`
    - `plugin.auth` resta solo per i flussi di login/logout del canale; gli hook
      di autenticazione per l'approvazione non vengono più letti dal core
    - Registra gli oggetti di runtime di proprietà del canale come client,
      token o app Bolt tramite
      `openclaw/plugin-sdk/channel-runtime-context`
    - Non inviare avvisi di reroute di proprietà del plugin dagli handler di
      approvazione nativi; il core ora gestisce gli avvisi di instradamento
      altrove dai risultati effettivi di consegna
    - Quando passi `channelRuntime` a `createChannelManager(...)`, fornisci una
      vera superficie `createPluginRuntime().channel`. Gli stub parziali
      vengono rifiutati.

    Vedi `/plugins/sdk-channel-plugins` per l'attuale layout della capability
    di approvazione.

  </Step>

  <Step title="Controlla il comportamento di fallback del wrapper Windows">
    Se il tuo plugin usa `openclaw/plugin-sdk/windows-spawn`, i wrapper Windows
    `.cmd`/`.bat` non risolti ora falliscono in modo chiuso a meno che tu non
    passi esplicitamente `allowShellFallback: true`.

    ```typescript
    // Prima
    const program = applyWindowsSpawnProgramPolicy({ candidate });

    // Dopo
    const program = applyWindowsSpawnProgramPolicy({
      candidate,
      // Imposta questo solo per chiamanti di compatibilità attendibili che
      // accettano intenzionalmente il fallback mediato dalla shell.
      allowShellFallback: true,
    });
    ```

    Se il tuo chiamante non dipende intenzionalmente dal fallback della shell,
    non impostare `allowShellFallback` e gestisci invece l'errore generato.

  </Step>

  <Step title="Trova gli import deprecati">
    Cerca nel tuo plugin gli import da una delle due superfici deprecate:

    ```bash
    grep -r "plugin-sdk/compat" my-plugin/
    grep -r "openclaw/extension-api" my-plugin/
    ```

  </Step>

  <Step title="Sostituisci con import mirati">
    Ogni export della vecchia superficie corrisponde a uno specifico percorso
    di import moderno:

    ```typescript
    // Prima (livello di retrocompatibilità deprecato)
    import {
      createChannelReplyPipeline,
      createPluginRuntimeStore,
      resolveControlCommandGate,
    } from "openclaw/plugin-sdk/compat";

    // Dopo (import moderni e mirati)
    import { createChannelReplyPipeline } from "openclaw/plugin-sdk/channel-reply-pipeline";
    import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
    import { resolveControlCommandGate } from "openclaw/plugin-sdk/command-auth";
    ```

    Per gli helper lato host, usa il runtime del plugin iniettato invece di
    importare direttamente:

    ```typescript
    // Prima (bridge extension-api deprecato)
    import { runEmbeddedPiAgent } from "openclaw/extension-api";
    const result = await runEmbeddedPiAgent({ sessionId, prompt });

    // Dopo (runtime iniettato)
    const result = await api.runtime.agent.runEmbeddedPiAgent({ sessionId, prompt });
    ```

    Lo stesso schema si applica ad altri helper legacy del bridge:

    | Vecchio import | Equivalente moderno |
    | --- | --- |
    | `resolveAgentDir` | `api.runtime.agent.resolveAgentDir` |
    | `resolveAgentWorkspaceDir` | `api.runtime.agent.resolveAgentWorkspaceDir` |
    | `resolveAgentIdentity` | `api.runtime.agent.resolveAgentIdentity` |
    | `resolveThinkingDefault` | `api.runtime.agent.resolveThinkingDefault` |
    | `resolveAgentTimeoutMs` | `api.runtime.agent.resolveAgentTimeoutMs` |
    | `ensureAgentWorkspace` | `api.runtime.agent.ensureAgentWorkspace` |
    | helper del session store | `api.runtime.agent.session.*` |

  </Step>

  <Step title="Build e test">
    ```bash
    pnpm build
    pnpm test -- my-plugin/
    ```
  </Step>
</Steps>

## Riferimento ai percorsi di import

  <Accordion title="Tabella comune dei percorsi di import">
  | Percorso di import | Scopo | Export principali |
  | --- | --- | --- |
  | `plugin-sdk/plugin-entry` | Helper canonico per il punto di ingresso del plugin | `definePluginEntry` |
  | `plugin-sdk/core` | Riesportazione legacy ombrello per definizioni/builder di entry dei canali | `defineChannelPluginEntry`, `createChatChannelPlugin` |
  | `plugin-sdk/config-schema` | Export dello schema di configurazione radice | `OpenClawSchema` |
  | `plugin-sdk/provider-entry` | Helper per entry a provider singolo | `defineSingleProviderPluginEntry` |
  | `plugin-sdk/channel-core` | Definizioni e builder mirati per l'entry del canale | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
  | `plugin-sdk/setup` | Helper condivisi per la procedura guidata di configurazione | Prompt di allowlist, builder dello stato di configurazione |
  | `plugin-sdk/setup-runtime` | Helper di runtime per il setup | Adapter di patch setup import-safe, helper per note di lookup, `promptResolvedAllowFrom`, `splitSetupEntries`, proxy di setup delegati |
  | `plugin-sdk/setup-adapter-runtime` | Helper per adapter di setup | `createEnvPatchedAccountSetupAdapter` |
  | `plugin-sdk/setup-tools` | Helper di tooling per il setup | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
  | `plugin-sdk/account-core` | Helper multi-account | Helper per elenco account/config/action-gate |
  | `plugin-sdk/account-id` | Helper per account-id | `DEFAULT_ACCOUNT_ID`, normalizzazione di account-id |
  | `plugin-sdk/account-resolution` | Helper per la risoluzione degli account | Helper per lookup account + fallback predefinito |
  | `plugin-sdk/account-helpers` | Helper mirati per account | Helper per elenco account/account-action |
  | `plugin-sdk/channel-setup` | Adapter della procedura guidata di configurazione | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, più `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
  | `plugin-sdk/channel-pairing` | Primitive per l'associazione DM | `createChannelPairingController` |
  | `plugin-sdk/channel-reply-pipeline` | Wiring per prefisso risposta + digitazione | `createChannelReplyPipeline` |
  | `plugin-sdk/channel-config-helpers` | Factory per adapter di configurazione | `createHybridChannelConfigAdapter` |
  | `plugin-sdk/channel-config-schema` | Builder per schema di configurazione | Tipi di schema di configurazione del canale |
  | `plugin-sdk/telegram-command-config` | Helper di configurazione dei comandi Telegram | Normalizzazione del nome comando, trimming della descrizione, validazione di duplicati/conflitti |
  | `plugin-sdk/channel-policy` | Risoluzione delle policy gruppo/DM | `resolveChannelGroupRequireMention` |
  | `plugin-sdk/channel-lifecycle` | Tracciamento dello stato account | `createAccountStatusSink` |
  | `plugin-sdk/inbound-envelope` | Helper per inbound envelope | Helper condivisi per route + builder di envelope |
  | `plugin-sdk/inbound-reply-dispatch` | Helper per risposte in ingresso | Helper condivisi per registrazione e dispatch |
  | `plugin-sdk/messaging-targets` | Parsing dei target di messaggistica | Helper per parsing/matching dei target |
  | `plugin-sdk/outbound-media` | Helper per media in uscita | Caricamento condiviso dei media in uscita |
  | `plugin-sdk/outbound-runtime` | Helper di runtime per l'uscita | Helper per identità in uscita/delegati di invio |
  | `plugin-sdk/thread-bindings-runtime` | Helper per thread-binding | Helper per ciclo di vita dei thread-binding e adapter |
  | `plugin-sdk/agent-media-payload` | Helper legacy per media payload | Builder di media payload dell'agente per layout legacy dei campi |
  | `plugin-sdk/channel-runtime` | Shim di compatibilità deprecato | Solo utility legacy per channel runtime |
  | `plugin-sdk/channel-send-result` | Tipi del risultato di invio | Tipi del risultato di risposta |
  | `plugin-sdk/runtime-store` | Archiviazione persistente del plugin | `createPluginRuntimeStore` |
  | `plugin-sdk/runtime` | Helper di runtime ad ampio spettro | Helper per runtime/logging/backup/installazione plugin |
  | `plugin-sdk/runtime-env` | Helper mirati per l'ambiente di runtime | Helper per logger/runtime env, timeout, retry e backoff |
  | `plugin-sdk/plugin-runtime` | Helper condivisi per plugin runtime | Helper per comandi/hook/http/interattività del plugin |
  | `plugin-sdk/hook-runtime` | Helper per la pipeline degli hook | Helper condivisi per la pipeline di webhook/hook interni |
  | `plugin-sdk/lazy-runtime` | Helper per lazy runtime | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeMethodBinder`, `createLazyRuntimeNamedExport`, `createLazyRuntimeSurface` |
  | `plugin-sdk/process-runtime` | Helper per i processi | Helper condivisi per `exec` |
  | `plugin-sdk/cli-runtime` | Helper di runtime per CLI | Formattazione comandi, attese, helper per versione |
  | `plugin-sdk/gateway-runtime` | Helper per Gateway | Client Gateway e helper di patch dello stato del canale |
  | `plugin-sdk/config-runtime` | Helper di configurazione | Helper per caricamento/scrittura della configurazione |
  | `plugin-sdk/telegram-command-config` | Helper per comandi Telegram | Helper di validazione dei comandi Telegram con fallback stabile quando la superficie del contratto Telegram inclusa non è disponibile |
  | `plugin-sdk/approval-runtime` | Helper per prompt di approvazione | Payload di approvazione exec/plugin, helper per capability/profili di approvazione, helper di routing/runtime per approvazioni native |
  | `plugin-sdk/approval-auth-runtime` | Helper di autenticazione per approvazione | Risoluzione degli approvatori, autenticazione delle azioni nella stessa chat |
  | `plugin-sdk/approval-client-runtime` | Helper client per approvazione | Helper per profili/filtri di approvazione exec native |
  | `plugin-sdk/approval-delivery-runtime` | Helper di consegna per approvazione | Adapter per capability/consegna di approvazioni native |
  | `plugin-sdk/approval-gateway-runtime` | Helper Gateway per approvazione | Helper condiviso per la risoluzione del gateway di approvazione |
  | `plugin-sdk/approval-handler-adapter-runtime` | Helper adapter per approvazione | Helper leggeri per il caricamento di adapter di approvazione nativi per hot channel entrypoint |
  | `plugin-sdk/approval-handler-runtime` | Helper handler per approvazione | Helper di runtime più ampi per handler di approvazione; preferisci i seam adapter/gateway più mirati quando bastano |
  | `plugin-sdk/approval-native-runtime` | Helper per target di approvazione | Helper di binding target/account per approvazioni native |
  | `plugin-sdk/approval-reply-runtime` | Helper per risposta di approvazione | Helper per payload di risposta di approvazione exec/plugin |
  | `plugin-sdk/channel-runtime-context` | Helper per channel runtime-context | Helper generici per register/get/watch del channel runtime-context |
  | `plugin-sdk/security-runtime` | Helper di sicurezza | Helper condivisi per trust, gating DM, contenuti esterni e raccolta di segreti |
  | `plugin-sdk/ssrf-policy` | Helper per policy SSRF | Helper per allowlist host e policy di rete privata |
  | `plugin-sdk/ssrf-runtime` | Helper di runtime SSRF | Dispatcher pinning, fetch protetta, helper per policy SSRF |
  | `plugin-sdk/collection-runtime` | Helper per cache limitata | `pruneMapToMaxSize` |
  | `plugin-sdk/diagnostic-runtime` | Helper per gating diagnostico | `isDiagnosticFlagEnabled`, `isDiagnosticsEnabled` |
  | `plugin-sdk/error-runtime` | Helper per formattazione errori | `formatUncaughtError`, `isApprovalNotFoundError`, helper per grafi di errori |
  | `plugin-sdk/fetch-runtime` | Helper per fetch/proxy con wrapper | `resolveFetch`, helper per proxy |
  | `plugin-sdk/host-runtime` | Helper per normalizzazione host | `normalizeHostname`, `normalizeScpRemoteHost` |
  | `plugin-sdk/retry-runtime` | Helper per retry | `RetryConfig`, `retryAsync`, runner di policy |
  | `plugin-sdk/allow-from` | Formattazione della allowlist | `formatAllowFromLowercase` |
  | `plugin-sdk/allowlist-resolution` | Mappatura degli input di allowlist | `mapAllowlistResolutionInputs` |
  | `plugin-sdk/command-auth` | Helper per command gating e superfici dei comandi | `resolveControlCommandGate`, helper per autorizzazione del mittente, helper per registro dei comandi |
  | `plugin-sdk/command-status` | Renderer di stato/help dei comandi | `buildCommandsMessage`, `buildCommandsMessagePaginated`, `buildHelpMessage` |
  | `plugin-sdk/secret-input` | Parsing dell'input segreto | Helper per input segreto |
  | `plugin-sdk/webhook-ingress` | Helper per richieste Webhook | Utility per target Webhook |
  | `plugin-sdk/webhook-request-guards` | Helper di guardia per body Webhook | Helper per lettura/limite del corpo della richiesta |
  | `plugin-sdk/reply-runtime` | Runtime condiviso per le risposte | Dispatch in ingresso, Heartbeat, pianificatore delle risposte, chunking |
  | `plugin-sdk/reply-dispatch-runtime` | Helper mirati per il dispatch delle risposte | Helper per finalizzazione + dispatch del provider |
  | `plugin-sdk/reply-history` | Helper per reply-history | `buildHistoryContext`, `buildPendingHistoryContextFromMap`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` |
  | `plugin-sdk/reply-reference` | Pianificazione dei riferimenti di risposta | `createReplyReferencePlanner` |
  | `plugin-sdk/reply-chunking` | Helper per chunk di risposta | Helper per chunking di testo/markdown |
  | `plugin-sdk/session-store-runtime` | Helper per session store | Helper per percorso dello store + updated-at |
  | `plugin-sdk/state-paths` | Helper per percorsi di stato | Helper per directory di stato e OAuth |
  | `plugin-sdk/routing` | Helper per routing/session-key | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId`, helper di normalizzazione per session-key |
  | `plugin-sdk/status-helpers` | Helper per stato del canale | Builder di riepilogo dello stato canale/account, valori predefiniti dello stato runtime, helper per metadati dei problemi |
  | `plugin-sdk/target-resolver-runtime` | Helper per target resolver | Helper condivisi per target resolver |
  | `plugin-sdk/string-normalization-runtime` | Helper per normalizzazione stringhe | Helper per normalizzazione di slug/stringhe |
  | `plugin-sdk/request-url` | Helper per URL della richiesta | Estrai URL stringa da input simili a request |
  | `plugin-sdk/run-command` | Helper per comandi temporizzati | Runner di comandi temporizzati con stdout/stderr normalizzati |
  | `plugin-sdk/param-readers` | Lettori di parametri | Lettori comuni di parametri per tool/CLI |
  | `plugin-sdk/tool-payload` | Estrazione del payload dei tool | Estrai payload normalizzati dagli oggetti risultato dei tool |
  | `plugin-sdk/tool-send` | Estrazione di invio dei tool | Estrai i campi canonici del target di invio dagli argomenti del tool |
  | `plugin-sdk/temp-path` | Helper per percorsi temporanei | Helper condivisi per percorsi temporanei di download |
  | `plugin-sdk/logging-core` | Helper di logging | Logger di sottosistema e helper di redazione |
  | `plugin-sdk/markdown-table-runtime` | Helper per tabelle Markdown | Helper per modalità delle tabelle Markdown |
  | `plugin-sdk/reply-payload` | Tipi di risposta dei messaggi | Tipi di reply payload |
  | `plugin-sdk/provider-setup` | Helper curati per il setup di provider locali/self-hosted | Helper per discovery/config di provider self-hosted |
  | `plugin-sdk/self-hosted-provider-setup` | Helper mirati per il setup di provider self-hosted compatibili OpenAI | Gli stessi helper per discovery/config di provider self-hosted |
  | `plugin-sdk/provider-auth-runtime` | Helper di autenticazione runtime del provider | Helper per la risoluzione runtime delle API key |
  | `plugin-sdk/provider-auth-api-key` | Helper per setup API key del provider | Helper per onboarding API key/scrittura del profilo |
  | `plugin-sdk/provider-auth-result` | Helper per risultato di autenticazione del provider | Builder standard del risultato di autenticazione OAuth |
  | `plugin-sdk/provider-auth-login` | Helper per login interattivo del provider | Helper condivisi per login interattivo |
  | `plugin-sdk/provider-env-vars` | Helper per env var del provider | Helper per lookup delle env var di autenticazione del provider |
  | `plugin-sdk/provider-model-shared` | Helper condivisi per modelli/replay del provider | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, builder condivisi per replay-policy, helper per endpoint del provider e helper per normalizzazione degli id dei modelli |
  | `plugin-sdk/provider-catalog-shared` | Helper condivisi per il catalogo provider | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
  | `plugin-sdk/provider-onboard` | Patch di onboarding del provider | Helper di configurazione per l'onboarding |
  | `plugin-sdk/provider-http` | Helper HTTP del provider | Helper generici per HTTP/capacità endpoint del provider |
  | `plugin-sdk/provider-web-fetch` | Helper web-fetch del provider | Helper per registrazione/cache del provider web-fetch |
  | `plugin-sdk/provider-web-search-config-contract` | Helper di configurazione web-search del provider | Helper mirati per configurazione/credenziali web-search per provider che non richiedono wiring di abilitazione del plugin |
  | `plugin-sdk/provider-web-search-contract` | Helper del contratto web-search del provider | Helper mirati per il contratto di configurazione/credenziali web-search come `createWebSearchProviderContractFields`, `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig` e setter/getter di credenziali con ambito |
  | `plugin-sdk/provider-web-search` | Helper web-search del provider | Helper per registrazione/cache/runtime del provider web-search |
  | `plugin-sdk/provider-tools` | Helper di compatibilità tool/schema del provider | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, cleanup + diagnostica dello schema Gemini e helper di compatibilità xAI come `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
  | `plugin-sdk/provider-usage` | Helper di utilizzo del provider | `fetchClaudeUsage`, `fetchGeminiUsage`, `fetchGithubCopilotUsage` e altri helper di utilizzo del provider |
  | `plugin-sdk/provider-stream` | Helper wrapper di stream del provider | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, tipi dei wrapper di stream e helper wrapper condivisi per Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
  | `plugin-sdk/keyed-async-queue` | Coda asincrona ordinata | `KeyedAsyncQueue` |
  | `plugin-sdk/media-runtime` | Helper media condivisi | Helper per fetch/transform/store dei media più builder di media payload |
  | `plugin-sdk/media-generation-runtime` | Helper condivisi per la generazione media | Helper condivisi per failover, selezione dei candidati e messaggi di modello mancante per la generazione di immagini/video/musica |
  | `plugin-sdk/media-understanding` | Helper per media-understanding | Tipi del provider di media understanding più export di helper per immagini/audio rivolti ai provider |
  | `plugin-sdk/text-runtime` | Helper testuali condivisi | Rimozione del testo visibile all'assistente, helper per render/chunking/tabelle Markdown, helper di redazione, helper per tag di direttiva, utility di testo sicuro e relativi helper di testo/logging |
  | `plugin-sdk/text-chunking` | Helper per chunking del testo | Helper per chunking del testo in uscita |
  | `plugin-sdk/speech` | Helper Speech | Tipi dei provider Speech più helper rivolti ai provider per direttive, registry e validazione |
  | `plugin-sdk/speech-core` | Core Speech condiviso | Tipi dei provider Speech, registry, direttive, normalizzazione |
  | `plugin-sdk/realtime-transcription` | Helper per trascrizione realtime | Tipi dei provider e helper per registry |
  | `plugin-sdk/realtime-voice` | Helper per voce realtime | Tipi dei provider e helper per registry |
  | `plugin-sdk/image-generation-core` | Core condiviso per la generazione di immagini | Tipi per la generazione di immagini, helper per failover, autenticazione e registry |
  | `plugin-sdk/music-generation` | Helper per la generazione musicale | Tipi di provider/richiesta/risultato per la generazione musicale |
  | `plugin-sdk/music-generation-core` | Core condiviso per la generazione musicale | Tipi per la generazione musicale, helper per failover, lookup dei provider e parsing di model-ref |
  | `plugin-sdk/video-generation` | Helper per la generazione video | Tipi di provider/richiesta/risultato per la generazione video |
  | `plugin-sdk/video-generation-core` | Core condiviso per la generazione video | Tipi per la generazione video, helper per failover, lookup dei provider e parsing di model-ref |
  | `plugin-sdk/interactive-runtime` | Helper per risposte interattive | Normalizzazione/riduzione del payload delle risposte interattive |
  | `plugin-sdk/channel-config-primitives` | Primitive di configurazione del canale | Primitive mirate per lo schema di configurazione del canale |
  | `plugin-sdk/channel-config-writes` | Helper per scrittura della configurazione del canale | Helper di autorizzazione per la scrittura della configurazione del canale |
  | `plugin-sdk/channel-plugin-common` | Prelude condiviso del canale | Export condivisi del prelude del channel plugin |
  | `plugin-sdk/channel-status` | Helper di stato del canale | Helper condivisi per snapshot/riepilogo dello stato del canale |
  | `plugin-sdk/allowlist-config-edit` | Helper di configurazione della allowlist | Helper per modifica/lettura della configurazione della allowlist |
  | `plugin-sdk/group-access` | Helper di accesso ai gruppi | Helper condivisi per le decisioni di accesso ai gruppi |
  | `plugin-sdk/direct-dm` | Helper Direct-DM | Helper condivisi di autenticazione/guard per Direct-DM |
  | `plugin-sdk/extension-shared` | Helper condivisi per extension | Primitive helper per canale passivo/stato e proxy ambient |
  | `plugin-sdk/webhook-targets` | Helper per target Webhook | Registry dei target Webhook e helper per installazione delle route |
  | `plugin-sdk/webhook-path` | Helper per percorsi Webhook | Helper per la normalizzazione dei percorsi Webhook |
  | `plugin-sdk/web-media` | Helper web media condivisi | Helper per caricamento di media remoti/locali |
  | `plugin-sdk/zod` | Riesportazione di zod | `zod` riesportato per i consumer del Plugin SDK |
  | `plugin-sdk/memory-core` | Helper inclusi di memory-core | Superficie helper per gestore memoria/configurazione/file/CLI |
  | `plugin-sdk/memory-core-engine-runtime` | Facade runtime del motore di memoria | Facade runtime per indice/ricerca della memoria |
  | `plugin-sdk/memory-core-host-engine-foundation` | Motore foundation dell'host di memoria | Export del motore foundation dell'host di memoria |
  | `plugin-sdk/memory-core-host-engine-embeddings` | Motore embedding dell'host di memoria | Contratti embedding della memoria, accesso al registry, provider locale e helper generici batch/remoti; i provider remoti concreti si trovano nei plugin proprietari corrispondenti |
  | `plugin-sdk/memory-core-host-engine-qmd` | Motore QMD dell'host di memoria | Export del motore QMD dell'host di memoria |
  | `plugin-sdk/memory-core-host-engine-storage` | Motore storage dell'host di memoria | Export del motore storage dell'host di memoria |
  | `plugin-sdk/memory-core-host-multimodal` | Helper multimodali dell'host di memoria | Helper multimodali dell'host di memoria |
  | `plugin-sdk/memory-core-host-query` | Helper query dell'host di memoria | Helper query dell'host di memoria |
  | `plugin-sdk/memory-core-host-secret` | Helper secret dell'host di memoria | Helper secret dell'host di memoria |
  | `plugin-sdk/memory-core-host-events` | Helper del journal eventi dell'host di memoria | Helper del journal eventi dell'host di memoria |
  | `plugin-sdk/memory-core-host-status` | Helper di stato dell'host di memoria | Helper di stato dell'host di memoria |
  | `plugin-sdk/memory-core-host-runtime-cli` | Runtime CLI dell'host di memoria | Helper runtime CLI dell'host di memoria |
  | `plugin-sdk/memory-core-host-runtime-core` | Runtime core dell'host di memoria | Helper runtime core dell'host di memoria |
  | `plugin-sdk/memory-core-host-runtime-files` | Helper file/runtime dell'host di memoria | Helper file/runtime dell'host di memoria |
  | `plugin-sdk/memory-host-core` | Alias runtime core dell'host di memoria | Alias neutrale rispetto al vendor per gli helper runtime core dell'host di memoria |
  | `plugin-sdk/memory-host-events` | Alias journal eventi dell'host di memoria | Alias neutrale rispetto al vendor per gli helper del journal eventi dell'host di memoria |
  | `plugin-sdk/memory-host-files` | Alias file/runtime dell'host di memoria | Alias neutrale rispetto al vendor per gli helper file/runtime dell'host di memoria |
  | `plugin-sdk/memory-host-markdown` | Helper markdown gestiti | Helper condivisi per managed-markdown per plugin adiacenti alla memoria |
  | `plugin-sdk/memory-host-search` | Facade di ricerca Active Memory | Facade runtime lazy del gestore di ricerca Active Memory |
  | `plugin-sdk/memory-host-status` | Alias stato dell'host di memoria | Alias neutrale rispetto al vendor per gli helper di stato dell'host di memoria |
  | `plugin-sdk/memory-lancedb` | Helper inclusi di memory-lancedb | Superficie helper di memory-lancedb |
  | `plugin-sdk/testing` | Utility di test | Helper di test e mock |
</Accordion>

Questa tabella è intenzionalmente il sottoinsieme comune per la migrazione, non
l'intera superficie del SDK. L'elenco completo di oltre 200 entrypoint si trova
in `scripts/lib/plugin-sdk-entrypoints.json`.

Quell'elenco include ancora alcuni helper seam per plugin inclusi come
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` e `plugin-sdk/matrix*`. Questi continuano a essere
esportati per la manutenzione e la compatibilità dei plugin inclusi, ma sono
intenzionalmente omessi dalla tabella comune di migrazione e non sono il target
consigliato per nuovo codice plugin.

La stessa regola si applica ad altre famiglie di helper inclusi come:

- helper di supporto browser: `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support`
- Matrix: `plugin-sdk/matrix*`
- LINE: `plugin-sdk/line*`
- IRC: `plugin-sdk/irc*`
- superfici di helper/plugin inclusi come `plugin-sdk/googlechat`,
  `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles*`,
  `plugin-sdk/mattermost*`, `plugin-sdk/msteams`,
  `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`,
  `plugin-sdk/twitch`,
  `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`,
  `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`,
  `plugin-sdk/thread-ownership` e `plugin-sdk/voice-call`

`plugin-sdk/github-copilot-token` espone attualmente la superficie mirata di
helper per token `DEFAULT_COPILOT_API_BASE_URL`,
`deriveCopilotApiBaseUrlFromToken` e `resolveCopilotApiToken`.

Usa l'import più mirato che corrisponde al compito. Se non riesci a trovare un
export, controlla il sorgente in `src/plugin-sdk/` oppure chiedi su Discord.

## Tempistica di rimozione

| Quando | Cosa succede |
| ---------------------- | ----------------------------------------------------------------------- |
| **Ora** | Le superfici deprecate emettono avvisi a runtime |
| **Prossima major release** | Le superfici deprecate verranno rimosse; i plugin che le usano ancora non funzioneranno |

Tutti i plugin core sono già stati migrati. I plugin esterni dovrebbero
migrare prima della prossima major release.

## Sopprimere temporaneamente gli avvisi

Imposta queste variabili d'ambiente mentre lavori alla migrazione:

```bash
OPENCLAW_SUPPRESS_PLUGIN_SDK_COMPAT_WARNING=1 openclaw gateway run
OPENCLAW_SUPPRESS_EXTENSION_API_WARNING=1 openclaw gateway run
```

Si tratta di una soluzione temporanea, non di una soluzione permanente.

## Correlati

- [Guida introduttiva](/it/plugins/building-plugins) — crea il tuo primo plugin
- [Panoramica del SDK](/it/plugins/sdk-overview) — riferimento completo per gli import dei subpath
- [Plugin di canale](/it/plugins/sdk-channel-plugins) — creare plugin di canale
- [Plugin provider](/it/plugins/sdk-provider-plugins) — creare plugin provider
- [Interni dei plugin](/it/plugins/architecture) — approfondimento sull'architettura
- [Manifest del plugin](/it/plugins/manifest) — riferimento dello schema del manifest
