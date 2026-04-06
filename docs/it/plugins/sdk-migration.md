---
read_when:
    - Vedi l'avviso OPENCLAW_PLUGIN_SDK_COMPAT_DEPRECATED
    - Vedi l'avviso OPENCLAW_EXTENSION_API_DEPRECATED
    - Stai aggiornando un plugin alla moderna architettura dei plugin
    - Mantieni un plugin esterno di OpenClaw
sidebarTitle: Migrate to SDK
summary: Migra dal livello legacy di retrocompatibilità al moderno Plugin SDK
title: Migrazione del Plugin SDK
x-i18n:
    generated_at: "2026-04-06T08:16:01Z"
    model: gpt-5.4
    provider: openai
    source_hash: 94f12d1376edd8184714cc4dbea4a88fa8ed652f65e9365ede6176f3bf441b33
    source_path: plugins/sdk-migration.md
    workflow: 15
---

# Migrazione del Plugin SDK

OpenClaw è passato da un ampio livello di retrocompatibilità a una moderna
architettura dei plugin con importazioni mirate e documentate. Se il tuo plugin
è stato creato prima della nuova architettura, questa guida ti aiuterà nella
migrazione.

## Cosa sta cambiando

Il vecchio sistema dei plugin forniva due superfici molto ampie che permettevano
ai plugin di importare tutto ciò di cui avevano bisogno da un unico punto di accesso:

- **`openclaw/plugin-sdk/compat`** — una singola importazione che riesportava
  decine di helper. È stata introdotta per mantenere funzionanti i vecchi
  plugin basati su hook mentre veniva sviluppata la nuova architettura dei plugin.
- **`openclaw/extension-api`** — un bridge che forniva ai plugin accesso diretto
  agli helper lato host, come l'embedded agent runner.

Entrambe le superfici sono ora **deprecate**. Continuano a funzionare a runtime,
ma i nuovi plugin non devono usarle e i plugin esistenti dovrebbero migrare prima
che la prossima major release le rimuova.

<Warning>
  Il livello di retrocompatibilità verrà rimosso in una futura major release.
  I plugin che importano ancora da queste superfici smetteranno di funzionare quando ciò accadrà.
</Warning>

## Perché è cambiato

Il vecchio approccio causava problemi:

- **Avvio lento** — importare un helper caricava decine di moduli non correlati
- **Dipendenze circolari** — le riesportazioni ampie rendevano facile creare cicli di importazione
- **Superficie API poco chiara** — non c'era modo di capire quali export fossero stabili e quali interni

Il moderno Plugin SDK risolve questo problema: ogni percorso di importazione (`openclaw/plugin-sdk/\<subpath\>`)
è un modulo piccolo e autosufficiente con uno scopo chiaro e un contratto documentato.

Anche le vecchie convenience seam dei provider per i canali bundled non esistono più. Importazioni
come `openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp`,
le helper seam con branding del canale e
`openclaw/plugin-sdk/telegram-core` erano scorciatoie private del mono-repo, non
contratti stabili per i plugin. Usa invece i sotto-percorsi SDK generici e mirati. All'interno del
workspace dei plugin bundled, mantieni gli helper di proprietà del provider nel file
`api.ts` o `runtime-api.ts` del plugin stesso.

Esempi attuali di provider bundled:

- Anthropic mantiene gli helper di stream specifici per Claude nel proprio `api.ts` /
  `contract-api.ts`
- OpenAI mantiene builder dei provider, helper per i modelli predefiniti e builder del provider realtime
  nel proprio `api.ts`
- OpenRouter mantiene il builder del provider e gli helper di onboarding/config nel proprio
  `api.ts`

## Come migrare

<Steps>
  <Step title="Verifica il comportamento di fallback del wrapper Windows">
    Se il tuo plugin usa `openclaw/plugin-sdk/windows-spawn`, i wrapper Windows
    `.cmd`/`.bat` non risolti ora falliscono in modo chiuso, a meno che tu non passi esplicitamente
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

    Se il tuo chiamante non dipende intenzionalmente dal fallback della shell, non impostare
    `allowShellFallback` e gestisci invece l'errore sollevato.

  </Step>

  <Step title="Trova le importazioni deprecate">
    Cerca nel tuo plugin le importazioni da una delle due superfici deprecate:

    ```bash
    grep -r "plugin-sdk/compat" my-plugin/
    grep -r "openclaw/extension-api" my-plugin/
    ```

  </Step>

  <Step title="Sostituisci con importazioni mirate">
    Ogni export dalla vecchia superficie corrisponde a uno specifico percorso di importazione moderno:

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

    Lo stesso schema si applica ad altri helper legacy del bridge:

    | Vecchia importazione | Equivalente moderno |
    | --- | --- |
    | `resolveAgentDir` | `api.runtime.agent.resolveAgentDir` |
    | `resolveAgentWorkspaceDir` | `api.runtime.agent.resolveAgentWorkspaceDir` |
    | `resolveAgentIdentity` | `api.runtime.agent.resolveAgentIdentity` |
    | `resolveThinkingDefault` | `api.runtime.agent.resolveThinkingDefault` |
    | `resolveAgentTimeoutMs` | `api.runtime.agent.resolveAgentTimeoutMs` |
    | `ensureAgentWorkspace` | `api.runtime.agent.ensureAgentWorkspace` |
    | helper del session store | `api.runtime.agent.session.*` |

  </Step>

  <Step title="Compila ed esegui i test">
    ```bash
    pnpm build
    pnpm test -- my-plugin/
    ```
  </Step>
</Steps>

## Riferimento dei percorsi di importazione

<Accordion title="Tabella dei percorsi di importazione comuni">
  | Percorso di importazione | Scopo | Export chiave |
  | --- | --- | --- |
  | `plugin-sdk/plugin-entry` | Helper canonico per l'entry del plugin | `definePluginEntry` |
  | `plugin-sdk/core` | Riesportazione legacy ombrello per definizioni/builder dell'entry del canale | `defineChannelPluginEntry`, `createChatChannelPlugin` |
  | `plugin-sdk/config-schema` | Export dello schema di configurazione root | `OpenClawSchema` |
  | `plugin-sdk/provider-entry` | Helper di entry per provider singolo | `defineSingleProviderPluginEntry` |
  | `plugin-sdk/channel-core` | Definizioni e builder mirati per l'entry del canale | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
  | `plugin-sdk/setup` | Helper condivisi della procedura guidata di setup | Prompt allowlist, builder dello stato di setup |
  | `plugin-sdk/setup-runtime` | Helper runtime per il setup | Adattatori patch di setup sicuri per l'importazione, helper per note di lookup, `promptResolvedAllowFrom`, `splitSetupEntries`, proxy di setup delegati |
  | `plugin-sdk/setup-adapter-runtime` | Helper per gli adattatori di setup | `createEnvPatchedAccountSetupAdapter` |
  | `plugin-sdk/setup-tools` | Helper di tooling per il setup | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
  | `plugin-sdk/account-core` | Helper multi-account | Helper per elenco/configurazione/azione-gate degli account |
  | `plugin-sdk/account-id` | Helper per account-id | `DEFAULT_ACCOUNT_ID`, normalizzazione di account-id |
  | `plugin-sdk/account-resolution` | Helper per la ricerca degli account | Helper per ricerca account + fallback predefinito |
  | `plugin-sdk/account-helpers` | Helper mirati per gli account | Helper per elenco account/azioni account |
  | `plugin-sdk/channel-setup` | Adattatori della procedura guidata di setup | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, più `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
  | `plugin-sdk/channel-pairing` | Primitive di abbinamento DM | `createChannelPairingController` |
  | `plugin-sdk/channel-reply-pipeline` | Wiring di prefisso risposta + digitazione | `createChannelReplyPipeline` |
  | `plugin-sdk/channel-config-helpers` | Factory degli adattatori di configurazione | `createHybridChannelConfigAdapter` |
  | `plugin-sdk/channel-config-schema` | Builder dello schema di configurazione | Tipi di schema di configurazione del canale |
  | `plugin-sdk/telegram-command-config` | Helper di configurazione dei comandi Telegram | Normalizzazione dei nomi dei comandi, trimming delle descrizioni, validazione di duplicati/conflitti |
  | `plugin-sdk/channel-policy` | Risoluzione delle policy gruppo/DM | `resolveChannelGroupRequireMention` |
  | `plugin-sdk/channel-lifecycle` | Tracciamento dello stato degli account | `createAccountStatusSink` |
  | `plugin-sdk/inbound-envelope` | Helper per inbound envelope | Helper condivisi di route + builder di envelope |
  | `plugin-sdk/inbound-reply-dispatch` | Helper per le risposte in ingresso | Helper condivisi di registrazione e dispatch |
  | `plugin-sdk/messaging-targets` | Parsing dei target di messaggistica | Helper per parsing/corrispondenza dei target |
  | `plugin-sdk/outbound-media` | Helper per media in uscita | Caricamento condiviso dei media in uscita |
  | `plugin-sdk/outbound-runtime` | Helper runtime in uscita | Helper per identità in uscita/delegati di invio |
  | `plugin-sdk/thread-bindings-runtime` | Helper per thread-binding | Ciclo di vita dei thread-binding e helper degli adattatori |
  | `plugin-sdk/agent-media-payload` | Helper legacy per media payload | Builder del media payload dell'agente per layout legacy dei campi |
  | `plugin-sdk/channel-runtime` | Shim di compatibilità deprecato | Solo utility legacy del runtime del canale |
  | `plugin-sdk/channel-send-result` | Tipi di risultato dell'invio | Tipi di risultato della risposta |
  | `plugin-sdk/runtime-store` | Storage persistente del plugin | `createPluginRuntimeStore` |
  | `plugin-sdk/runtime` | Helper runtime ampi | Helper per runtime/logging/backup/installazione plugin |
  | `plugin-sdk/runtime-env` | Helper mirati per runtime env | Helper per logger/runtime env, timeout, retry e backoff |
  | `plugin-sdk/plugin-runtime` | Helper runtime condivisi del plugin | Helper per comandi/hook/http/interattività del plugin |
  | `plugin-sdk/hook-runtime` | Helper della pipeline di hook | Helper condivisi della pipeline di webhook/internal hook |
  | `plugin-sdk/lazy-runtime` | Helper runtime lazy | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeMethodBinder`, `createLazyRuntimeNamedExport`, `createLazyRuntimeSurface` |
  | `plugin-sdk/process-runtime` | Helper di processo | Helper condivisi di exec |
  | `plugin-sdk/cli-runtime` | Helper runtime della CLI | Formattazione dei comandi, attese, helper per la versione |
  | `plugin-sdk/gateway-runtime` | Helper del gateway | Client del gateway e helper patch dello stato dei canali |
  | `plugin-sdk/config-runtime` | Helper di configurazione | Helper di caricamento/scrittura della configurazione |
  | `plugin-sdk/telegram-command-config` | Helper per comandi Telegram | Helper di validazione dei comandi Telegram con fallback stabile quando la superficie contrattuale del Telegram bundled non è disponibile |
  | `plugin-sdk/approval-runtime` | Helper per prompt di approvazione | Payload di approvazione exec/plugin, helper per capability/profilo di approvazione, helper nativi di routing/runtime dell'approvazione |
  | `plugin-sdk/approval-auth-runtime` | Helper auth per approvazione | Risoluzione degli approvatori, auth di azione nella stessa chat |
  | `plugin-sdk/approval-client-runtime` | Helper client per approvazione | Helper per profilo/filtro di approvazione nativa di exec |
  | `plugin-sdk/approval-delivery-runtime` | Helper di delivery per approvazione | Adattatori nativi di capability/delivery dell'approvazione |
  | `plugin-sdk/approval-native-runtime` | Helper target per approvazione | Helper nativi per target/account binding dell'approvazione |
  | `plugin-sdk/approval-reply-runtime` | Helper per risposte di approvazione | Helper per payload di risposta di approvazione exec/plugin |
  | `plugin-sdk/security-runtime` | Helper di sicurezza | Helper condivisi per trust, gating DM, contenuti esterni e raccolta dei segreti |
  | `plugin-sdk/ssrf-policy` | Helper per policy SSRF | Helper per allowlist host e policy di rete privata |
  | `plugin-sdk/ssrf-runtime` | Helper runtime SSRF | Pinned-dispatcher, fetch protetto, helper per policy SSRF |
  | `plugin-sdk/collection-runtime` | Helper per cache bounded | `pruneMapToMaxSize` |
  | `plugin-sdk/diagnostic-runtime` | Helper per gating diagnostico | `isDiagnosticFlagEnabled`, `isDiagnosticsEnabled` |
  | `plugin-sdk/error-runtime` | Helper di formattazione degli errori | `formatUncaughtError`, `isApprovalNotFoundError`, helper per grafi di errore |
  | `plugin-sdk/fetch-runtime` | Helper per fetch/proxy wrapped | `resolveFetch`, helper proxy |
  | `plugin-sdk/host-runtime` | Helper di normalizzazione host | `normalizeHostname`, `normalizeScpRemoteHost` |
  | `plugin-sdk/retry-runtime` | Helper di retry | `RetryConfig`, `retryAsync`, esecutori di policy |
  | `plugin-sdk/allow-from` | Formattazione allowlist | `formatAllowFromLowercase` |
  | `plugin-sdk/allowlist-resolution` | Mappatura input dell'allowlist | `mapAllowlistResolutionInputs` |
  | `plugin-sdk/command-auth` | Gating dei comandi e helper per la superficie dei comandi | `resolveControlCommandGate`, helper di autorizzazione del mittente, helper del registro comandi |
  | `plugin-sdk/secret-input` | Parsing dell'input segreto | Helper per input segreti |
  | `plugin-sdk/webhook-ingress` | Helper per richieste webhook | Utility per target webhook |
  | `plugin-sdk/webhook-request-guards` | Helper guard per il body dei webhook | Helper per lettura/limite del body della richiesta |
  | `plugin-sdk/reply-runtime` | Runtime condiviso delle risposte | Dispatch in ingresso, heartbeat, pianificatore delle risposte, chunking |
  | `plugin-sdk/reply-dispatch-runtime` | Helper mirati per dispatch delle risposte | Helper per finalize + dispatch del provider |
  | `plugin-sdk/reply-history` | Helper per reply-history | `buildHistoryContext`, `buildPendingHistoryContextFromMap`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` |
  | `plugin-sdk/reply-reference` | Pianificazione dei riferimenti di risposta | `createReplyReferencePlanner` |
  | `plugin-sdk/reply-chunking` | Helper per chunk delle risposte | Helper per chunking di testo/markdown |
  | `plugin-sdk/session-store-runtime` | Helper per session store | Helper per percorso dello store + updated-at |
  | `plugin-sdk/state-paths` | Helper per i percorsi di stato | Helper per directory di stato e OAuth |
  | `plugin-sdk/routing` | Helper per routing/session-key | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId`, helper di normalizzazione session-key |
  | `plugin-sdk/status-helpers` | Helper per stato del canale | Builder di riepilogo dello stato canale/account, valori predefiniti dello stato runtime, helper per metadati dei problemi |
  | `plugin-sdk/target-resolver-runtime` | Helper per target resolver | Helper condivisi per target resolver |
  | `plugin-sdk/string-normalization-runtime` | Helper per normalizzazione delle stringhe | Helper per normalizzazione di slug/stringhe |
  | `plugin-sdk/request-url` | Helper per URL della richiesta | Estrae URL stringa da input simili a richieste |
  | `plugin-sdk/run-command` | Helper per comandi temporizzati | Runner di comandi temporizzati con stdout/stderr normalizzati |
  | `plugin-sdk/param-readers` | Lettori di parametri | Lettori comuni di parametri di tool/CLI |
  | `plugin-sdk/tool-send` | Estrazione dell'invio del tool | Estrae i campi target di invio canonici dagli argomenti del tool |
  | `plugin-sdk/temp-path` | Helper per percorsi temporanei | Helper condivisi per percorsi temporanei di download |
  | `plugin-sdk/logging-core` | Helper di logging | Logger di sottosistema e helper di redazione |
  | `plugin-sdk/markdown-table-runtime` | Helper per markdown table | Helper per modalità markdown table |
  | `plugin-sdk/reply-payload` | Tipi di risposta del messaggio | Tipi di payload della risposta |
  | `plugin-sdk/provider-setup` | Helper curati per setup di provider locali/self-hosted | Helper per scoperta/configurazione di provider self-hosted |
  | `plugin-sdk/self-hosted-provider-setup` | Helper mirati per setup di provider self-hosted compatibili con OpenAI | Gli stessi helper per scoperta/configurazione di provider self-hosted |
  | `plugin-sdk/provider-auth-runtime` | Helper auth runtime del provider | Helper runtime per risoluzione delle API key |
  | `plugin-sdk/provider-auth-api-key` | Helper per setup delle API key del provider | Helper per onboarding/scrittura del profilo delle API key |
  | `plugin-sdk/provider-auth-result` | Helper per auth-result del provider | Builder standard di auth-result OAuth |
  | `plugin-sdk/provider-auth-login` | Helper per login interattivo del provider | Helper condivisi per login interattivo |
  | `plugin-sdk/provider-env-vars` | Helper per env var del provider | Helper per lookup delle env var auth del provider |
  | `plugin-sdk/provider-model-shared` | Helper condivisi per modelli/replay del provider | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, builder condivisi per replay-policy, helper per endpoint del provider e normalizzazione degli id modello |
  | `plugin-sdk/provider-catalog-shared` | Helper condivisi per cataloghi provider | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
  | `plugin-sdk/provider-onboard` | Patch di onboarding del provider | Helper di configurazione dell'onboarding |
  | `plugin-sdk/provider-http` | Helper HTTP del provider | Helper generici per HTTP/capability degli endpoint del provider |
  | `plugin-sdk/provider-web-fetch` | Helper per web-fetch del provider | Helper per registrazione/cache del provider web-fetch |
  | `plugin-sdk/provider-web-search` | Helper per web-search del provider | Helper per registrazione/cache/configurazione del provider web-search |
  | `plugin-sdk/provider-tools` | Helper di compatibilità tool/schema del provider | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, pulizia dello schema Gemini + diagnostica e helper di compatibilità xAI come `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
  | `plugin-sdk/provider-usage` | Helper di utilizzo del provider | `fetchClaudeUsage`, `fetchGeminiUsage`, `fetchGithubCopilotUsage` e altri helper di utilizzo del provider |
  | `plugin-sdk/provider-stream` | Helper wrapper degli stream del provider | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, tipi di stream wrapper e helper wrapper condivisi per Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
  | `plugin-sdk/keyed-async-queue` | Coda async ordinata | `KeyedAsyncQueue` |
  | `plugin-sdk/media-runtime` | Helper media condivisi | Helper per fetch/trasformazione/storage dei media più builder di media payload |
  | `plugin-sdk/media-generation-runtime` | Helper condivisi per media-generation | Helper condivisi per failover, selezione dei candidati e messaggi di modello mancante per generazione di immagini/video/musica |
  | `plugin-sdk/media-understanding` | Helper per media-understanding | Tipi di provider media-understanding più export di helper immagine/audio lato provider |
  | `plugin-sdk/text-runtime` | Helper di testo condivisi | Rimozione del testo visibile all'assistente, helper di rendering/chunking/tabelle markdown, helper di redazione, helper directive-tag, utility di testo sicuro e relativi helper di testo/logging |
  | `plugin-sdk/text-chunking` | Helper per chunking del testo | Helper per chunking del testo in uscita |
  | `plugin-sdk/speech` | Helper speech | Tipi di provider speech più export di helper lato provider per direttive, registry e validazione |
  | `plugin-sdk/speech-core` | Core speech condiviso | Tipi di provider speech, registry, direttive, normalizzazione |
  | `plugin-sdk/realtime-transcription` | Helper per trascrizione realtime | Tipi di provider e helper del registry |
  | `plugin-sdk/realtime-voice` | Helper per voce realtime | Tipi di provider e helper del registry |
  | `plugin-sdk/image-generation-core` | Core condiviso per image-generation | Tipi, failover, auth e helper del registry per image-generation |
  | `plugin-sdk/music-generation` | Helper per music-generation | Tipi di provider/richiesta/risultato per music-generation |
  | `plugin-sdk/music-generation-core` | Core condiviso per music-generation | Tipi di music-generation, helper di failover, lookup dei provider e parsing di model-ref |
  | `plugin-sdk/video-generation` | Helper per video-generation | Tipi di provider/richiesta/risultato per video-generation |
  | `plugin-sdk/video-generation-core` | Core condiviso per video-generation | Tipi di video-generation, helper di failover, lookup dei provider e parsing di model-ref |
  | `plugin-sdk/interactive-runtime` | Helper per risposte interattive | Normalizzazione/riduzione del payload delle risposte interattive |
  | `plugin-sdk/channel-config-primitives` | Primitive di configurazione del canale | Primitive mirate dello schema di configurazione del canale |
  | `plugin-sdk/channel-config-writes` | Helper di scrittura della configurazione del canale | Helper di autorizzazione per la scrittura della configurazione del canale |
  | `plugin-sdk/channel-plugin-common` | Prelude condiviso del canale | Export condivisi del preludio del plugin del canale |
  | `plugin-sdk/channel-status` | Helper per stato del canale | Helper condivisi per snapshot/riepilogo dello stato del canale |
  | `plugin-sdk/allowlist-config-edit` | Helper di configurazione dell'allowlist | Helper per modifica/lettura della configurazione dell'allowlist |
  | `plugin-sdk/group-access` | Helper per accesso ai gruppi | Helper condivisi per decisioni di accesso ai gruppi |
  | `plugin-sdk/direct-dm` | Helper per direct-DM | Helper condivisi per auth/guard di direct-DM |
  | `plugin-sdk/extension-shared` | Helper condivisi delle estensioni | Primitive helper per canali passivi/stato |
  | `plugin-sdk/webhook-targets` | Helper per target webhook | Registry dei target webhook e helper per installazione delle route |
  | `plugin-sdk/webhook-path` | Helper per percorsi webhook | Helper di normalizzazione dei percorsi webhook |
  | `plugin-sdk/web-media` | Helper web media condivisi | Helper per caricamento di media remoti/locali |
  | `plugin-sdk/zod` | Riesportazione di zod | Riesporta `zod` per i consumer del Plugin SDK |
  | `plugin-sdk/memory-core` | Helper bundled memory-core | Superficie helper per gestore memoria/configurazione/file/CLI |
  | `plugin-sdk/memory-core-engine-runtime` | Facade runtime del motore di memoria | Facade runtime per indice/ricerca della memoria |
  | `plugin-sdk/memory-core-host-engine-foundation` | Motore foundation host di memoria | Export del motore foundation host di memoria |
  | `plugin-sdk/memory-core-host-engine-embeddings` | Motore embedding host di memoria | Export del motore embedding host di memoria |
  | `plugin-sdk/memory-core-host-engine-qmd` | Motore QMD host di memoria | Export del motore QMD host di memoria |
  | `plugin-sdk/memory-core-host-engine-storage` | Motore storage host di memoria | Export del motore storage host di memoria |
  | `plugin-sdk/memory-core-host-multimodal` | Helper multimodali host di memoria | Helper multimodali host di memoria |
  | `plugin-sdk/memory-core-host-query` | Helper query host di memoria | Helper query host di memoria |
  | `plugin-sdk/memory-core-host-secret` | Helper secret host di memoria | Helper secret host di memoria |
  | `plugin-sdk/memory-core-host-events` | Helper per journal degli eventi host di memoria | Helper per journal degli eventi host di memoria |
  | `plugin-sdk/memory-core-host-status` | Helper stato host di memoria | Helper stato host di memoria |
  | `plugin-sdk/memory-core-host-runtime-cli` | Runtime CLI host di memoria | Helper runtime CLI host di memoria |
  | `plugin-sdk/memory-core-host-runtime-core` | Runtime core host di memoria | Helper runtime core host di memoria |
  | `plugin-sdk/memory-core-host-runtime-files` | Helper file/runtime host di memoria | Helper file/runtime host di memoria |
  | `plugin-sdk/memory-host-core` | Alias runtime core host di memoria | Alias vendor-neutral per helper runtime core host di memoria |
  | `plugin-sdk/memory-host-events` | Alias journal eventi host di memoria | Alias vendor-neutral per helper journal eventi host di memoria |
  | `plugin-sdk/memory-host-files` | Alias file/runtime host di memoria | Alias vendor-neutral per helper file/runtime host di memoria |
  | `plugin-sdk/memory-host-markdown` | Helper managed markdown | Helper condivisi managed-markdown per plugin adiacenti alla memoria |
  | `plugin-sdk/memory-host-search` | Facade di ricerca della memoria attiva | Facade runtime lazy del gestore di ricerca della memoria attiva |
  | `plugin-sdk/memory-host-status` | Alias stato host di memoria | Alias vendor-neutral per helper stato host di memoria |
  | `plugin-sdk/memory-lancedb` | Helper bundled memory-lancedb | Superficie helper memory-lancedb |
  | `plugin-sdk/testing` | Utility di test | Helper e mock di test |
</Accordion>

Questa tabella è intenzionalmente il sottoinsieme comune per la migrazione, non l'intera
superficie dell'SDK. L'elenco completo di oltre 200 entrypoint si trova in
`scripts/lib/plugin-sdk-entrypoints.json`.

Questo elenco include ancora alcune helper seam dei plugin bundled, come
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` e `plugin-sdk/matrix*`. Rimangono esportate per
la manutenzione e la compatibilità dei plugin bundled, ma sono intenzionalmente
omesse dalla tabella di migrazione comune e non sono il target consigliato per
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

`plugin-sdk/github-copilot-token` espone attualmente la superficie mirata degli helper token
`DEFAULT_COPILOT_API_BASE_URL`,
`deriveCopilotApiBaseUrlFromToken` e `resolveCopilotApiToken`.

Usa l'importazione più mirata che corrisponde al compito. Se non riesci a trovare un export,
controlla il codice sorgente in `src/plugin-sdk/` o chiedi su Discord.

## Tempistiche di rimozione

| Quando | Cosa succede |
| ---------------------- | ----------------------------------------------------------------------- |
| **Ora**                | Le superfici deprecate emettono avvisi a runtime                               |
| **Prossima major release** | Le superfici deprecate verranno rimosse; i plugin che le usano ancora smetteranno di funzionare |

Tutti i plugin core sono già stati migrati. I plugin esterni dovrebbero migrare
prima della prossima major release.

## Sopprimere temporaneamente gli avvisi

Imposta queste variabili di ambiente mentre lavori alla migrazione:

```bash
OPENCLAW_SUPPRESS_PLUGIN_SDK_COMPAT_WARNING=1 openclaw gateway run
OPENCLAW_SUPPRESS_EXTENSION_API_WARNING=1 openclaw gateway run
```

Questa è una via di fuga temporanea, non una soluzione permanente.

## Correlati

- [Per iniziare](/it/plugins/building-plugins) — crea il tuo primo plugin
- [Panoramica dell'SDK](/it/plugins/sdk-overview) — riferimento completo delle importazioni per sottopercorso
- [Plugin di canale](/it/plugins/sdk-channel-plugins) — creare plugin di canale
- [Plugin provider](/it/plugins/sdk-provider-plugins) — creare plugin provider
- [Elementi interni dei plugin](/it/plugins/architecture) — approfondimento sull'architettura
- [Manifest del plugin](/it/plugins/manifest) — riferimento dello schema del manifest
