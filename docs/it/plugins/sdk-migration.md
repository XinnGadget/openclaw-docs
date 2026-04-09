---
read_when:
    - Vedi l'avviso OPENCLAW_PLUGIN_SDK_COMPAT_DEPRECATED
    - Vedi l'avviso OPENCLAW_EXTENSION_API_DEPRECATED
    - Stai aggiornando un plugin alla moderna architettura dei plugin
    - Mantieni un plugin OpenClaw esterno
sidebarTitle: Migrate to SDK
summary: Migra dal layer legacy di retrocompatibilità al moderno plugin SDK
title: Migrazione del Plugin SDK
x-i18n:
    generated_at: "2026-04-09T01:29:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: 60cbb6c8be30d17770887d490c14e3a4538563339a5206fb419e51e0558bbc07
    source_path: plugins/sdk-migration.md
    workflow: 15
---

# Migrazione del Plugin SDK

OpenClaw è passato da un ampio layer di retrocompatibilità a una moderna
architettura dei plugin con importazioni mirate e documentate. Se il tuo plugin è stato creato prima
della nuova architettura, questa guida ti aiuta a eseguire la migrazione.

## Cosa cambia

Il vecchio sistema di plugin forniva due superfici molto ampie che permettevano ai plugin di importare
qualsiasi cosa servisse da un unico punto di ingresso:

- **`openclaw/plugin-sdk/compat`** — una singola importazione che riesportava decine di
  helper. È stata introdotta per mantenere funzionanti i plugin più vecchi basati su hook mentre
  veniva costruita la nuova architettura dei plugin.
- **`openclaw/extension-api`** — un bridge che dava ai plugin accesso diretto a
  helper lato host come l'embedded agent runner.

Entrambe le superfici sono ora **deprecate**. Continuano a funzionare a runtime, ma i nuovi
plugin non devono usarle e i plugin esistenti dovrebbero migrare prima che la prossima
major release le rimuova.

<Warning>
  Il layer di retrocompatibilità verrà rimosso in una futura major release.
  I plugin che importano ancora da queste superfici smetteranno di funzionare quando ciò accadrà.
</Warning>

## Perché è cambiato

Il vecchio approccio causava problemi:

- **Avvio lento** — importare un helper caricava decine di moduli non correlati
- **Dipendenze circolari** — le ampie riesportazioni rendevano facile creare cicli di importazione
- **Superficie API poco chiara** — non c'era modo di distinguere quali export fossero stabili e quali interni

Il moderno plugin SDK risolve questo problema: ogni percorso di importazione (`openclaw/plugin-sdk/\<subpath\>`)
è un modulo piccolo e autonomo con uno scopo chiaro e un contratto documentato.

Sono state rimosse anche le seam legacy di convenienza dei provider per i canali inclusi. Importazioni
come `openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp`,
seam helper con branding del canale e
`openclaw/plugin-sdk/telegram-core` erano scorciatoie private del mono-repo, non
contratti di plugin stabili. Usa invece subpath SDK generici e più mirati. All'interno del
workspace dei plugin inclusi, mantieni gli helper di proprietà del provider nel file
`api.ts` o `runtime-api.ts` del plugin stesso.

Esempi attuali di provider inclusi:

- Anthropic mantiene gli helper di stream specifici di Claude nella propria seam `api.ts` /
  `contract-api.ts`
- OpenAI mantiene i builder dei provider, gli helper dei modelli predefiniti e i builder dei provider realtime
  nel proprio `api.ts`
- OpenRouter mantiene il builder del provider e gli helper di onboarding/configurazione nel proprio
  `api.ts`

## Come eseguire la migrazione

<Steps>
  <Step title="Migra gli handler approval-native ai capability fact">
    I plugin di canale con capacità di approvazione ora espongono il comportamento di approvazione nativo tramite
    `approvalCapability.nativeRuntime` più il registro condiviso del runtime-context.

    Modifiche principali:

    - Sostituisci `approvalCapability.handler.loadRuntime(...)` con
      `approvalCapability.nativeRuntime`
    - Sposta autenticazione/consegna specifiche dell'approvazione dal wiring legacy `plugin.auth` /
      `plugin.approvals` a `approvalCapability`
    - `ChannelPlugin.approvals` è stato rimosso dal contratto pubblico dei plugin di canale;
      sposta i campi delivery/native/render in `approvalCapability`
    - `plugin.auth` resta solo per i flussi di login/logout del canale; gli hook di autenticazione
      dell'approvazione lì non vengono più letti dal core
    - Registra gli oggetti runtime di proprietà del canale come client, token o app
      Bolt tramite `openclaw/plugin-sdk/channel-runtime-context`
    - Non inviare avvisi di reroute di proprietà del plugin dagli handler di approvazione nativi;
      il core ora gestisce gli avvisi instradati altrove a partire dai risultati di consegna reali
    - Quando passi `channelRuntime` a `createChannelManager(...)`, fornisci una
      superficie reale `createPluginRuntime().channel`. Gli stub parziali vengono rifiutati.

    Vedi `/plugins/sdk-channel-plugins` per il layout attuale della
    approval capability.

  </Step>

  <Step title="Controlla il comportamento di fallback del wrapper Windows">
    Se il tuo plugin usa `openclaw/plugin-sdk/windows-spawn`, i wrapper Windows
    `.cmd`/`.bat` non risolti ora falliscono in modalità fail closed a meno che tu non passi esplicitamente
    `allowShellFallback: true`.

    ```typescript
    // Prima
    const program = applyWindowsSpawnProgramPolicy({ candidate });

    // Dopo
    const program = applyWindowsSpawnProgramPolicy({
      candidate,
      // Impostalo solo per chiamanti di compatibilità fidati che accettano
      // intenzionalmente il fallback mediato dalla shell.
      allowShellFallback: true,
    });
    ```

    Se il tuo chiamante non dipende intenzionalmente dal fallback della shell, non impostare
    `allowShellFallback` e gestisci invece l'errore generato.

  </Step>

  <Step title="Trova le importazioni deprecate">
    Cerca nel tuo plugin le importazioni da una delle due superfici deprecate:

    ```bash
    grep -r "plugin-sdk/compat" my-plugin/
    grep -r "openclaw/extension-api" my-plugin/
    ```

  </Step>

  <Step title="Sostituiscile con importazioni mirate">
    Ogni export della vecchia superficie corrisponde a uno specifico percorso di importazione moderno:

    ```typescript
    // Prima (layer di retrocompatibilità deprecato)
    import {
      createChannelReplyPipeline,
      createPluginRuntimeStore,
      resolveControlCommandGate,
    } from "openclaw/plugin-sdk/compat";

    // Dopo (importazioni moderne e mirate)
    import { createChannelReplyPipeline } from "openclaw/plugin-sdk/channel-reply-pipeline";
    import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
    import { resolveControlCommandGate } from "openclaw/plugin-sdk/command-auth";
    ```

    Per gli helper lato host, usa il runtime del plugin iniettato invece di importare
    direttamente:

    ```typescript
    // Prima (bridge extension-api deprecato)
    import { runEmbeddedPiAgent } from "openclaw/extension-api";
    const result = await runEmbeddedPiAgent({ sessionId, prompt });

    // Dopo (runtime iniettato)
    const result = await api.runtime.agent.runEmbeddedPiAgent({ sessionId, prompt });
    ```

    Lo stesso pattern si applica ad altri helper legacy del bridge:

    | Vecchia importazione | Equivalente moderno |
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

## Riferimento dei percorsi di importazione

<Accordion title="Tabella dei percorsi di importazione comuni">
  | Percorso di importazione | Scopo | Export principali |
  | --- | --- | --- |
  | `plugin-sdk/plugin-entry` | Helper canonico per l'entry del plugin | `definePluginEntry` |
  | `plugin-sdk/core` | Riesportazione legacy ombrello per definizioni/builder delle entry di canale | `defineChannelPluginEntry`, `createChatChannelPlugin` |
  | `plugin-sdk/config-schema` | Export dello schema di configurazione root | `OpenClawSchema` |
  | `plugin-sdk/provider-entry` | Helper per entry a provider singolo | `defineSingleProviderPluginEntry` |
  | `plugin-sdk/channel-core` | Definizioni e builder mirati per le entry di canale | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
  | `plugin-sdk/setup` | Helper condivisi per la procedura guidata di setup | Prompt allowlist, builder dello stato di setup |
  | `plugin-sdk/setup-runtime` | Helper runtime in fase di setup | Adapter di patch setup import-safe, helper per lookup-note, `promptResolvedAllowFrom`, `splitSetupEntries`, proxy di setup delegati |
  | `plugin-sdk/setup-adapter-runtime` | Helper per adapter di setup | `createEnvPatchedAccountSetupAdapter` |
  | `plugin-sdk/setup-tools` | Helper per gli strumenti di setup | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
  | `plugin-sdk/account-core` | Helper multi-account | Helper per elenco/configurazione/account-action-gate |
  | `plugin-sdk/account-id` | Helper account-id | `DEFAULT_ACCOUNT_ID`, normalizzazione di account-id |
  | `plugin-sdk/account-resolution` | Helper per la ricerca dell'account | Helper per ricerca account + fallback predefinito |
  | `plugin-sdk/account-helpers` | Helper account mirati | Helper per elenco account/account-action |
  | `plugin-sdk/channel-setup` | Adapter per la procedura guidata di setup | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, più `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
  | `plugin-sdk/channel-pairing` | Primitive di pairing DM | `createChannelPairingController` |
  | `plugin-sdk/channel-reply-pipeline` | Wiring del prefisso di risposta + typing | `createChannelReplyPipeline` |
  | `plugin-sdk/channel-config-helpers` | Factory per adapter di configurazione | `createHybridChannelConfigAdapter` |
  | `plugin-sdk/channel-config-schema` | Builder dello schema di configurazione | Tipi dello schema di configurazione del canale |
  | `plugin-sdk/telegram-command-config` | Helper per la configurazione dei comandi Telegram | Normalizzazione del nome comando, trimming della descrizione, validazione di duplicati/conflitti |
  | `plugin-sdk/channel-policy` | Risoluzione delle policy gruppo/DM | `resolveChannelGroupRequireMention` |
  | `plugin-sdk/channel-lifecycle` | Tracciamento dello stato dell'account | `createAccountStatusSink` |
  | `plugin-sdk/inbound-envelope` | Helper inbound envelope | Helper condivisi per route + builder envelope |
  | `plugin-sdk/inbound-reply-dispatch` | Helper per le risposte inbound | Helper condivisi per registrazione e dispatch |
  | `plugin-sdk/messaging-targets` | Parsing dei target di messaggistica | Helper di parsing/matching dei target |
  | `plugin-sdk/outbound-media` | Helper per i media outbound | Caricamento condiviso dei media outbound |
  | `plugin-sdk/outbound-runtime` | Helper runtime outbound | Helper per identità outbound/delegati send |
  | `plugin-sdk/thread-bindings-runtime` | Helper thread-binding | Lifecycle del thread-binding e helper adapter |
  | `plugin-sdk/agent-media-payload` | Helper legacy per media payload | Builder del media payload dell'agente per layout di campi legacy |
  | `plugin-sdk/channel-runtime` | Shim di compatibilità deprecato | Solo utility legacy di channel runtime |
  | `plugin-sdk/channel-send-result` | Tipi del risultato di invio | Tipi del risultato della risposta |
  | `plugin-sdk/runtime-store` | Archiviazione persistente del plugin | `createPluginRuntimeStore` |
  | `plugin-sdk/runtime` | Helper runtime ampi | Helper per runtime/logging/backup/installazione plugin |
  | `plugin-sdk/runtime-env` | Helper runtime env mirati | Logger/runtime env, timeout, retry e helper per backoff |
  | `plugin-sdk/plugin-runtime` | Helper runtime condivisi del plugin | Helper per comandi/hook/http/interattivi del plugin |
  | `plugin-sdk/hook-runtime` | Helper per la pipeline degli hook | Helper condivisi per la pipeline degli hook webhook/interni |
  | `plugin-sdk/lazy-runtime` | Helper per lazy runtime | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeMethodBinder`, `createLazyRuntimeNamedExport`, `createLazyRuntimeSurface` |
  | `plugin-sdk/process-runtime` | Helper di processo | Helper condivisi per exec |
  | `plugin-sdk/cli-runtime` | Helper runtime CLI | Formattazione dei comandi, attese, helper per versione |
  | `plugin-sdk/gateway-runtime` | Helper gateway | Client gateway e helper per patch dello stato del canale |
  | `plugin-sdk/config-runtime` | Helper di configurazione | Helper per caricamento/scrittura della configurazione |
  | `plugin-sdk/telegram-command-config` | Helper per i comandi Telegram | Helper di validazione dei comandi Telegram stabili come fallback quando la superficie del contratto Telegram incluso non è disponibile |
  | `plugin-sdk/approval-runtime` | Helper per i prompt di approvazione | Payload di approvazione exec/plugin, helper di approval capability/profile, helper di routing/runtime dell'approvazione nativa |
  | `plugin-sdk/approval-auth-runtime` | Helper di autenticazione dell'approvazione | Risoluzione dell'approvatore, autenticazione di azione nella stessa chat |
  | `plugin-sdk/approval-client-runtime` | Helper client dell'approvazione | Helper profile/filter dell'approvazione exec nativa |
  | `plugin-sdk/approval-delivery-runtime` | Helper di consegna dell'approvazione | Adapter di delivery/capability dell'approvazione nativa |
  | `plugin-sdk/approval-gateway-runtime` | Helper gateway dell'approvazione | Helper condiviso di risoluzione del gateway di approvazione |
  | `plugin-sdk/approval-handler-adapter-runtime` | Helper adapter dell'approvazione | Helper leggeri di caricamento dell'adapter di approvazione nativa per entrypoint di canale hot |
  | `plugin-sdk/approval-handler-runtime` | Helper handler dell'approvazione | Helper runtime più ampi per gli handler di approvazione; preferisci le seam adapter/gateway più mirate quando sono sufficienti |
  | `plugin-sdk/approval-native-runtime` | Helper target dell'approvazione | Helper di binding target/account dell'approvazione nativa |
  | `plugin-sdk/approval-reply-runtime` | Helper di risposta dell'approvazione | Helper per il payload di risposta dell'approvazione exec/plugin |
  | `plugin-sdk/channel-runtime-context` | Helper channel runtime-context | Helper generici register/get/watch del channel runtime-context |
  | `plugin-sdk/security-runtime` | Helper di sicurezza | Helper condivisi per trust, gating DM, contenuto esterno e raccolta di segreti |
  | `plugin-sdk/ssrf-policy` | Helper della policy SSRF | Helper per allowlist host e policy di rete privata |
  | `plugin-sdk/ssrf-runtime` | Helper runtime SSRF | Helper pinned-dispatcher, guarded fetch e policy SSRF |
  | `plugin-sdk/collection-runtime` | Helper per cache limitata | `pruneMapToMaxSize` |
  | `plugin-sdk/diagnostic-runtime` | Helper di gating diagnostico | `isDiagnosticFlagEnabled`, `isDiagnosticsEnabled` |
  | `plugin-sdk/error-runtime` | Helper di formattazione degli errori | `formatUncaughtError`, `isApprovalNotFoundError`, helper del grafo degli errori |
  | `plugin-sdk/fetch-runtime` | Helper wrapped fetch/proxy | `resolveFetch`, helper proxy |
  | `plugin-sdk/host-runtime` | Helper di normalizzazione host | `normalizeHostname`, `normalizeScpRemoteHost` |
  | `plugin-sdk/retry-runtime` | Helper retry | `RetryConfig`, `retryAsync`, runner di policy |
  | `plugin-sdk/allow-from` | Formattazione allowlist | `formatAllowFromLowercase` |
  | `plugin-sdk/allowlist-resolution` | Mapping degli input della allowlist | `mapAllowlistResolutionInputs` |
  | `plugin-sdk/command-auth` | Gating dei comandi e helper della command surface | `resolveControlCommandGate`, helper di autorizzazione del mittente, helper del registro comandi |
  | `plugin-sdk/command-status` | Renderer di stato/help dei comandi | `buildCommandsMessage`, `buildCommandsMessagePaginated`, `buildHelpMessage` |
  | `plugin-sdk/secret-input` | Parsing dell'input segreto | Helper per input segreto |
  | `plugin-sdk/webhook-ingress` | Helper per richieste webhook | Utility per target webhook |
  | `plugin-sdk/webhook-request-guards` | Helper di guardia per il body webhook | Helper per lettura/limite del body della richiesta |
  | `plugin-sdk/reply-runtime` | Runtime di risposta condiviso | Dispatch inbound, heartbeat, reply planner, chunking |
  | `plugin-sdk/reply-dispatch-runtime` | Helper mirati per reply dispatch | Helper per finalize + provider dispatch |
  | `plugin-sdk/reply-history` | Helper reply-history | `buildHistoryContext`, `buildPendingHistoryContextFromMap`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` |
  | `plugin-sdk/reply-reference` | Pianificazione dei reply reference | `createReplyReferencePlanner` |
  | `plugin-sdk/reply-chunking` | Helper per reply chunk | Helper per chunking di testo/markdown |
  | `plugin-sdk/session-store-runtime` | Helper dello session store | Helper per percorso store + updated-at |
  | `plugin-sdk/state-paths` | Helper per i percorsi di stato | Helper per directory di stato e OAuth |
  | `plugin-sdk/routing` | Helper di routing/session-key | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId`, helper di normalizzazione della session key |
  | `plugin-sdk/status-helpers` | Helper di stato del canale | Builder del riepilogo dello stato canale/account, valori predefiniti dello stato runtime, helper per metadati dei problemi |
  | `plugin-sdk/target-resolver-runtime` | Helper target resolver | Helper condivisi del target resolver |
  | `plugin-sdk/string-normalization-runtime` | Helper di normalizzazione delle stringhe | Helper per normalizzazione di slug/stringhe |
  | `plugin-sdk/request-url` | Helper per l'URL della richiesta | Estrae URL stringa da input simili a una richiesta |
  | `plugin-sdk/run-command` | Helper per comandi temporizzati | Runner di comandi temporizzati con stdout/stderr normalizzati |
  | `plugin-sdk/param-readers` | Lettori di parametri | Lettori comuni di parametri per tool/CLI |
  | `plugin-sdk/tool-payload` | Estrazione del tool payload | Estrae payload normalizzati da oggetti risultato dei tool |
  | `plugin-sdk/tool-send` | Estrazione del tool send | Estrae campi target di invio canonici dagli argomenti del tool |
  | `plugin-sdk/temp-path` | Helper per percorsi temporanei | Helper condivisi per i percorsi temporanei di download |
  | `plugin-sdk/logging-core` | Helper di logging | Logger di sottosistema e helper di redazione |
  | `plugin-sdk/markdown-table-runtime` | Helper per tabelle markdown | Helper per la modalità tabella markdown |
  | `plugin-sdk/reply-payload` | Tipi di risposta dei messaggi | Tipi del payload di risposta |
  | `plugin-sdk/provider-setup` | Helper selezionati per il setup di provider locali/self-hosted | Helper per rilevamento/configurazione di provider self-hosted |
  | `plugin-sdk/self-hosted-provider-setup` | Helper mirati per il setup di provider self-hosted compatibili con OpenAI | Gli stessi helper per rilevamento/configurazione di provider self-hosted |
  | `plugin-sdk/provider-auth-runtime` | Helper runtime di autenticazione del provider | Helper per la risoluzione a runtime della chiave API |
  | `plugin-sdk/provider-auth-api-key` | Helper di setup della chiave API del provider | Helper per onboarding/scrittura del profilo della chiave API |
  | `plugin-sdk/provider-auth-result` | Helper per auth-result del provider | Builder standard per il risultato di autenticazione OAuth |
  | `plugin-sdk/provider-auth-login` | Helper di login interattivo del provider | Helper condivisi per il login interattivo |
  | `plugin-sdk/provider-env-vars` | Helper per env var del provider | Helper per la ricerca delle env var di autenticazione del provider |
  | `plugin-sdk/provider-model-shared` | Helper condivisi per modello/replay del provider | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, builder condivisi di replay-policy, helper per endpoint del provider e helper di normalizzazione dell'id modello |
  | `plugin-sdk/provider-catalog-shared` | Helper condivisi per il catalogo provider | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
  | `plugin-sdk/provider-onboard` | Patch di onboarding del provider | Helper di configurazione dell'onboarding |
  | `plugin-sdk/provider-http` | Helper HTTP del provider | Helper generici per HTTP/endpoint capability del provider |
  | `plugin-sdk/provider-web-fetch` | Helper web-fetch del provider | Helper per registrazione/cache del provider web-fetch |
  | `plugin-sdk/provider-web-search-config-contract` | Helper per la configurazione della web search del provider | Helper mirati per configurazione/credenziali della web search per provider che non richiedono wiring di abilitazione del plugin |
  | `plugin-sdk/provider-web-search-contract` | Helper di contratto della web search del provider | Helper mirati di contratto per configurazione/credenziali della web search come `createWebSearchProviderContractFields`, `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig` e setter/getter di credenziali con scope |
  | `plugin-sdk/provider-web-search` | Helper di web search del provider | Helper per registrazione/cache/runtime del provider di web search |
  | `plugin-sdk/provider-tools` | Helper di compatibilità tool/schema del provider | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, pulizia schema + diagnostica di Gemini e helper di compatibilità xAI come `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
  | `plugin-sdk/provider-usage` | Helper di utilizzo del provider | `fetchClaudeUsage`, `fetchGeminiUsage`, `fetchGithubCopilotUsage` e altri helper di utilizzo del provider |
  | `plugin-sdk/provider-stream` | Helper wrapper di stream del provider | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, tipi di stream wrapper e helper wrapper condivisi per Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
  | `plugin-sdk/keyed-async-queue` | Coda asincrona ordinata | `KeyedAsyncQueue` |
  | `plugin-sdk/media-runtime` | Helper media condivisi | Helper per fetch/transform/store dei media più builder di media payload |
  | `plugin-sdk/media-generation-runtime` | Helper condivisi per la generazione di media | Helper condivisi per failover, selezione dei candidati e messaggistica di modello mancante per generazione di immagini/video/musica |
  | `plugin-sdk/media-understanding` | Helper per media-understanding | Tipi di provider media-understanding più export di helper image/audio rivolti ai provider |
  | `plugin-sdk/text-runtime` | Helper di testo condivisi | Rimozione del testo visibile all'assistente, helper di render/chunking/tabella markdown, helper di redazione, helper per directive-tag, utility di testo sicuro e relativi helper di testo/logging |
  | `plugin-sdk/text-chunking` | Helper per il chunking del testo | Helper per il chunking del testo outbound |
  | `plugin-sdk/speech` | Helper speech | Tipi dei provider speech più helper rivolti ai provider per directive, registry e validazione |
  | `plugin-sdk/speech-core` | Core speech condiviso | Tipi dei provider speech, registry, directive, normalizzazione |
  | `plugin-sdk/realtime-transcription` | Helper per realtime transcription | Tipi dei provider e helper di registry |
  | `plugin-sdk/realtime-voice` | Helper per realtime voice | Tipi dei provider e helper di registry |
  | `plugin-sdk/image-generation-core` | Core condiviso per la generazione di immagini | Tipi per image-generation, failover, autenticazione e helper di registry |
  | `plugin-sdk/music-generation` | Helper per la generazione musicale | Tipi per provider/richiesta/risultato di generazione musicale |
  | `plugin-sdk/music-generation-core` | Core condiviso per la generazione musicale | Tipi di generazione musicale, helper di failover, ricerca del provider e parsing del model-ref |
  | `plugin-sdk/video-generation` | Helper per la generazione video | Tipi per provider/richiesta/risultato di generazione video |
  | `plugin-sdk/video-generation-core` | Core condiviso per la generazione video | Tipi di generazione video, helper di failover, ricerca del provider e parsing del model-ref |
  | `plugin-sdk/interactive-runtime` | Helper di risposta interattiva | Normalizzazione/riduzione del payload di risposta interattiva |
  | `plugin-sdk/channel-config-primitives` | Primitive di configurazione del canale | Primitive mirate dello schema di configurazione del canale |
  | `plugin-sdk/channel-config-writes` | Helper di scrittura della configurazione del canale | Helper di autorizzazione per la scrittura della configurazione del canale |
  | `plugin-sdk/channel-plugin-common` | Prelude condiviso del canale | Export della prelude condivisa del plugin di canale |
  | `plugin-sdk/channel-status` | Helper di stato del canale | Helper condivisi per snapshot/riepilogo dello stato del canale |
  | `plugin-sdk/allowlist-config-edit` | Helper di configurazione della allowlist | Helper di modifica/lettura della configurazione della allowlist |
  | `plugin-sdk/group-access` | Helper di accesso ai gruppi | Helper condivisi per le decisioni di accesso ai gruppi |
  | `plugin-sdk/direct-dm` | Helper Direct-DM | Helper condivisi di autenticazione/guard Direct-DM |
  | `plugin-sdk/extension-shared` | Helper condivisi dell'estensione | Primitive helper per passive-channel/status e proxy ambient |
  | `plugin-sdk/webhook-targets` | Helper per i target webhook | Registro dei target webhook e helper di installazione delle route |
  | `plugin-sdk/webhook-path` | Helper per il percorso webhook | Helper di normalizzazione del percorso webhook |
  | `plugin-sdk/web-media` | Helper media web condivisi | Helper per caricamento di media remoti/locali |
  | `plugin-sdk/zod` | Riesportazione Zod | `zod` riesportato per i consumer del plugin SDK |
  | `plugin-sdk/memory-core` | Helper memory-core inclusi | Superficie helper per memory manager/config/file/CLI |
  | `plugin-sdk/memory-core-engine-runtime` | Facade runtime del motore di memoria | Facade runtime per index/search della memoria |
  | `plugin-sdk/memory-core-host-engine-foundation` | Motore foundation dell'host della memoria | Export del motore foundation dell'host della memoria |
  | `plugin-sdk/memory-core-host-engine-embeddings` | Motore embedding dell'host della memoria | Export del motore embedding dell'host della memoria |
  | `plugin-sdk/memory-core-host-engine-qmd` | Motore QMD dell'host della memoria | Export del motore QMD dell'host della memoria |
  | `plugin-sdk/memory-core-host-engine-storage` | Motore storage dell'host della memoria | Export del motore storage dell'host della memoria |
  | `plugin-sdk/memory-core-host-multimodal` | Helper multimodali dell'host della memoria | Helper multimodali dell'host della memoria |
  | `plugin-sdk/memory-core-host-query` | Helper query dell'host della memoria | Helper query dell'host della memoria |
  | `plugin-sdk/memory-core-host-secret` | Helper secret dell'host della memoria | Helper secret dell'host della memoria |
  | `plugin-sdk/memory-core-host-events` | Helper del journal eventi dell'host della memoria | Helper del journal eventi dell'host della memoria |
  | `plugin-sdk/memory-core-host-status` | Helper di stato dell'host della memoria | Helper di stato dell'host della memoria |
  | `plugin-sdk/memory-core-host-runtime-cli` | Runtime CLI dell'host della memoria | Helper runtime CLI dell'host della memoria |
  | `plugin-sdk/memory-core-host-runtime-core` | Runtime core dell'host della memoria | Helper runtime core dell'host della memoria |
  | `plugin-sdk/memory-core-host-runtime-files` | Helper file/runtime dell'host della memoria | Helper file/runtime dell'host della memoria |
  | `plugin-sdk/memory-host-core` | Alias runtime core dell'host della memoria | Alias neutrale rispetto al vendor per gli helper runtime core dell'host della memoria |
  | `plugin-sdk/memory-host-events` | Alias del journal eventi dell'host della memoria | Alias neutrale rispetto al vendor per gli helper del journal eventi dell'host della memoria |
  | `plugin-sdk/memory-host-files` | Alias file/runtime dell'host della memoria | Alias neutrale rispetto al vendor per gli helper file/runtime dell'host della memoria |
  | `plugin-sdk/memory-host-markdown` | Helper markdown gestito | Helper markdown gestiti condivisi per plugin adiacenti alla memoria |
  | `plugin-sdk/memory-host-search` | Facade di ricerca della memoria attiva | Facade runtime lazy del search-manager della memoria attiva |
  | `plugin-sdk/memory-host-status` | Alias di stato dell'host della memoria | Alias neutrale rispetto al vendor per gli helper di stato dell'host della memoria |
  | `plugin-sdk/memory-lancedb` | Helper memory-lancedb inclusi | Superficie helper di memory-lancedb |
  | `plugin-sdk/testing` | Utility di test | Helper e mock per i test |
</Accordion>

Questa tabella è intenzionalmente un sottoinsieme comune per la migrazione, non l'intera
superficie dell'SDK. L'elenco completo di oltre 200 entrypoint si trova in
`scripts/lib/plugin-sdk-entrypoints.json`.

Quell'elenco include ancora alcune seam helper di plugin inclusi come
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` e `plugin-sdk/matrix*`. Restano esportate per
la manutenzione e la compatibilità dei plugin inclusi, ma sono intenzionalmente
omesse dalla tabella comune di migrazione e non sono il target consigliato per
nuovo codice dei plugin.

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

`plugin-sdk/github-copilot-token` espone attualmente la superficie mirata di helper per token
`DEFAULT_COPILOT_API_BASE_URL`,
`deriveCopilotApiBaseUrlFromToken` e `resolveCopilotApiToken`.

Usa l'importazione più mirata che corrisponde al lavoro da svolgere. Se non riesci a trovare un export,
controlla il sorgente in `src/plugin-sdk/` oppure chiedi su Discord.

## Timeline di rimozione

| Quando | Cosa succede |
| ---------------------- | ----------------------------------------------------------------------- |
| **Ora**                | Le superfici deprecate emettono avvisi a runtime                               |
| **Prossima major release** | Le superfici deprecate verranno rimosse; i plugin che le usano ancora non funzioneranno |

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

- [Per iniziare](/it/plugins/building-plugins) — crea il tuo primo plugin
- [Panoramica SDK](/it/plugins/sdk-overview) — riferimento completo alle importazioni per subpath
- [Plugin di canale](/it/plugins/sdk-channel-plugins) — creare plugin di canale
- [Plugin provider](/it/plugins/sdk-provider-plugins) — creare plugin provider
- [Interni dei plugin](/it/plugins/architecture) — approfondimento sull'architettura
- [Manifest del plugin](/it/plugins/manifest) — riferimento allo schema del manifest
