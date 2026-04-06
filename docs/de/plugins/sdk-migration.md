---
read_when:
    - Sie sehen die Warnung OPENCLAW_PLUGIN_SDK_COMPAT_DEPRECATED
    - Sie sehen die Warnung OPENCLAW_EXTENSION_API_DEPRECATED
    - Sie aktualisieren ein Plugin auf die moderne Plugin-Architektur
    - Sie pflegen ein externes OpenClaw-Plugin
sidebarTitle: Migrate to SDK
summary: Migrieren Sie von der veralteten Abwärtskompatibilitätsschicht zum modernen Plugin SDK
title: Migration des Plugin SDK
x-i18n:
    generated_at: "2026-04-06T06:22:04Z"
    model: gpt-5.4
    provider: openai
    source_hash: 94f12d1376edd8184714cc4dbea4a88fa8ed652f65e9365ede6176f3bf441b33
    source_path: plugins/sdk-migration.md
    workflow: 15
---

# Migration des Plugin SDK

OpenClaw ist von einer umfassenden Abwärtskompatibilitätsschicht zu einer modernen Plugin-Architektur mit gezielten, dokumentierten Imports übergegangen. Wenn Ihr Plugin vor der neuen Architektur erstellt wurde, hilft Ihnen diese Anleitung bei der Migration.

## Was sich ändert

Das alte Plugin-System stellte zwei weit offene Oberflächen bereit, über die Plugins alles importieren konnten, was sie über einen einzigen Einstiegspunkt benötigten:

- **`openclaw/plugin-sdk/compat`** — ein einzelner Import, der Dutzende von Helfern re-exportierte. Er wurde eingeführt, damit ältere hook-basierte Plugins weiter funktionierten, während die neue Plugin-Architektur entwickelt wurde.
- **`openclaw/extension-api`** — eine Brücke, die Plugins direkten Zugriff auf hostseitige Helfer wie den eingebetteten Agent-Runner gab.

Beide Oberflächen sind jetzt **veraltet**. Sie funktionieren zur Laufzeit weiterhin, aber neue Plugins dürfen sie nicht verwenden, und bestehende Plugins sollten migrieren, bevor sie in der nächsten Hauptversion entfernt werden.

<Warning>
  Die Abwärtskompatibilitätsschicht wird in einer zukünftigen Hauptversion entfernt.
  Plugins, die weiterhin aus diesen Oberflächen importieren, werden dann nicht mehr funktionieren.
</Warning>

## Warum sich das geändert hat

Der alte Ansatz verursachte Probleme:

- **Langsamer Start** — der Import eines einzelnen Helfers lud Dutzende nicht zusammenhängender Module
- **Zirkuläre Abhängigkeiten** — umfangreiche Re-Exports machten es leicht, Importzyklen zu erzeugen
- **Unklare API-Oberfläche** — es gab keine Möglichkeit zu erkennen, welche Exporte stabil und welche intern waren

Das moderne Plugin SDK behebt das: Jeder Importpfad (`openclaw/plugin-sdk/\<subpath\>`) ist ein kleines, in sich geschlossenes Modul mit einem klaren Zweck und dokumentiertem Vertrag.

Veraltete Convenience-Seams für Provider bei gebündelten Kanälen sind ebenfalls entfernt worden. Imports wie `openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`, `openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp`, kanalmarkenspezifische Helper-Seams und `openclaw/plugin-sdk/telegram-core` waren private Mono-Repo-Abkürzungen, keine stabilen Plugin-Verträge. Verwenden Sie stattdessen schmale generische SDK-Subpaths. Innerhalb des gebündelten Plugin-Workspaces sollten Provider-eigene Helfer im eigenen `api.ts` oder `runtime-api.ts` dieses Plugins bleiben.

Aktuelle Beispiele für gebündelte Provider:

- Anthropic behält Claude-spezifische Stream-Helfer in seinem eigenen `api.ts` / `contract-api.ts`-Seam
- OpenAI behält Provider-Builder, Helfer für Standardmodelle und Realtime-Provider-Builder in seinem eigenen `api.ts`
- OpenRouter behält Provider-Builder sowie Onboarding-/Konfigurationshelfer in seinem eigenen `api.ts`

## So migrieren Sie

<Steps>
  <Step title="Fallback-Verhalten des Windows-Wrappers prüfen">
    Wenn Ihr Plugin `openclaw/plugin-sdk/windows-spawn` verwendet, schlagen nicht aufgelöste Windows-Wrapper vom Typ `.cmd`/`.bat` jetzt standardmäßig fehl, sofern Sie nicht ausdrücklich `allowShellFallback: true` übergeben.

    ```typescript
    // Vorher
    const program = applyWindowsSpawnProgramPolicy({ candidate });

    // Nachher
    const program = applyWindowsSpawnProgramPolicy({
      candidate,
      // Setzen Sie dies nur für vertrauenswürdige Kompatibilitätsaufrufer,
      // die bewusst shell-vermittelten Fallback akzeptieren.
      allowShellFallback: true,
    });
    ```

    Wenn Ihr Aufrufer nicht bewusst auf Shell-Fallback angewiesen ist, setzen Sie `allowShellFallback` nicht und behandeln Sie stattdessen den ausgelösten Fehler.

  </Step>

  <Step title="Veraltete Imports finden">
    Suchen Sie in Ihrem Plugin nach Imports aus einer der beiden veralteten Oberflächen:

    ```bash
    grep -r "plugin-sdk/compat" my-plugin/
    grep -r "openclaw/extension-api" my-plugin/
    ```

  </Step>

  <Step title="Durch gezielte Imports ersetzen">
    Jeder Export aus der alten Oberfläche entspricht einem bestimmten modernen Importpfad:

    ```typescript
    // Vorher (veraltete Abwärtskompatibilitätsschicht)
    import {
      createChannelReplyPipeline,
      createPluginRuntimeStore,
      resolveControlCommandGate,
    } from "openclaw/plugin-sdk/compat";

    // Nachher (moderne gezielte Imports)
    import { createChannelReplyPipeline } from "openclaw/plugin-sdk/channel-reply-pipeline";
    import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
    import { resolveControlCommandGate } from "openclaw/plugin-sdk/command-auth";
    ```

    Verwenden Sie für hostseitige Helfer die injizierte Plugin-Laufzeitumgebung, anstatt direkt zu importieren:

    ```typescript
    // Vorher (veraltete extension-api-Brücke)
    import { runEmbeddedPiAgent } from "openclaw/extension-api";
    const result = await runEmbeddedPiAgent({ sessionId, prompt });

    // Nachher (injizierte Laufzeitumgebung)
    const result = await api.runtime.agent.runEmbeddedPiAgent({ sessionId, prompt });
    ```

    Dasselbe Muster gilt für andere veraltete Bridge-Helfer:

    | Alter Import | Modernes Äquivalent |
    | --- | --- |
    | `resolveAgentDir` | `api.runtime.agent.resolveAgentDir` |
    | `resolveAgentWorkspaceDir` | `api.runtime.agent.resolveAgentWorkspaceDir` |
    | `resolveAgentIdentity` | `api.runtime.agent.resolveAgentIdentity` |
    | `resolveThinkingDefault` | `api.runtime.agent.resolveThinkingDefault` |
    | `resolveAgentTimeoutMs` | `api.runtime.agent.resolveAgentTimeoutMs` |
    | `ensureAgentWorkspace` | `api.runtime.agent.ensureAgentWorkspace` |
    | Session-Store-Helfer | `api.runtime.agent.session.*` |

  </Step>

  <Step title="Build und Tests ausführen">
    ```bash
    pnpm build
    pnpm test -- my-plugin/
    ```
  </Step>
</Steps>

## Referenz der Importpfade

<Accordion title="Tabelle häufiger Importpfade">
  | Importpfad | Zweck | Wichtige Exporte |
  | --- | --- | --- |
  | `plugin-sdk/plugin-entry` | Kanonischer Plugin-Entry-Helfer | `definePluginEntry` |
  | `plugin-sdk/core` | Veralteter umfassender Re-Export für Channel-Entry-Definitionen/-Builder | `defineChannelPluginEntry`, `createChatChannelPlugin` |
  | `plugin-sdk/config-schema` | Root-Config-Schema-Export | `OpenClawSchema` |
  | `plugin-sdk/provider-entry` | Single-Provider-Entry-Helfer | `defineSingleProviderPluginEntry` |
  | `plugin-sdk/channel-core` | Gezielte Channel-Entry-Definitionen und -Builder | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
  | `plugin-sdk/setup` | Gemeinsame Helfer für den Einrichtungsassistenten | Allowlist-Prompts, Builder für Einrichtungsstatus |
  | `plugin-sdk/setup-runtime` | Laufzeithelfer für die Einrichtung | Importsichere Patch-Adapter für die Einrichtung, Helfer für Lookup-Hinweise, `promptResolvedAllowFrom`, `splitSetupEntries`, delegierte Setup-Proxys |
  | `plugin-sdk/setup-adapter-runtime` | Helfer für Setup-Adapter | `createEnvPatchedAccountSetupAdapter` |
  | `plugin-sdk/setup-tools` | Helfer für Einrichtungswerkzeuge | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
  | `plugin-sdk/account-core` | Helfer für mehrere Accounts | Helfer für Account-Liste/Config/Action-Gate |
  | `plugin-sdk/account-id` | Helfer für Account-IDs | `DEFAULT_ACCOUNT_ID`, Normalisierung von Account-IDs |
  | `plugin-sdk/account-resolution` | Helfer für die Account-Auflösung | Account-Lookup- und Standard-Fallback-Helfer |
  | `plugin-sdk/account-helpers` | Schmale Account-Helfer | Helfer für Account-Listen/Account-Aktionen |
  | `plugin-sdk/channel-setup` | Adapter für den Einrichtungsassistenten | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, plus `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
  | `plugin-sdk/channel-pairing` | Grundbausteine für DM-Pairing | `createChannelPairingController` |
  | `plugin-sdk/channel-reply-pipeline` | Verkabelung für Antwortpräfix + Tippstatus | `createChannelReplyPipeline` |
  | `plugin-sdk/channel-config-helpers` | Fabriken für Config-Adapter | `createHybridChannelConfigAdapter` |
  | `plugin-sdk/channel-config-schema` | Builder für Config-Schemata | Typen für Channel-Config-Schemata |
  | `plugin-sdk/telegram-command-config` | Helfer für Telegram-Befehlskonfiguration | Normalisierung von Befehlsnamen, Kürzen von Beschreibungen, Validierung von Duplikaten/Konflikten |
  | `plugin-sdk/channel-policy` | Auflösung von Gruppen-/DM-Richtlinien | `resolveChannelGroupRequireMention` |
  | `plugin-sdk/channel-lifecycle` | Nachverfolgung des Account-Status | `createAccountStatusSink` |
  | `plugin-sdk/inbound-envelope` | Helfer für eingehende Envelopes | Gemeinsame Helfer für Route- und Envelope-Builder |
  | `plugin-sdk/inbound-reply-dispatch` | Helfer für eingehende Antworten | Gemeinsame Helfer zum Aufzeichnen und Dispatchen |
  | `plugin-sdk/messaging-targets` | Parsing von Messaging-Zielen | Helfer zum Parsen/Abgleichen von Zielen |
  | `plugin-sdk/outbound-media` | Helfer für ausgehende Medien | Gemeinsames Laden ausgehender Medien |
  | `plugin-sdk/outbound-runtime` | Laufzeithelfer für ausgehende Vorgänge | Helfer für ausgehende Identität/Sende-Delegation |
  | `plugin-sdk/thread-bindings-runtime` | Helfer für Thread-Bindings | Helfer für Thread-Binding-Lebenszyklus und Adapter |
  | `plugin-sdk/agent-media-payload` | Veraltete Helfer für Medien-Payloads | Agent-Medien-Payload-Builder für veraltete Feldlayouts |
  | `plugin-sdk/channel-runtime` | Veralteter Kompatibilitäts-Shim | Nur veraltete Laufzeit-Hilfsfunktionen für Channels |
  | `plugin-sdk/channel-send-result` | Send-Result-Typen | Typen für Antwortergebnisse |
  | `plugin-sdk/runtime-store` | Persistenter Plugin-Speicher | `createPluginRuntimeStore` |
  | `plugin-sdk/runtime` | Umfassende Laufzeithelfer | Laufzeit-/Logging-/Backup-/Plugin-Installationshelfer |
  | `plugin-sdk/runtime-env` | Schmale Helfer für die Laufzeitumgebung | Logger-/Laufzeitumgebungs-, Timeout-, Retry- und Backoff-Helfer |
  | `plugin-sdk/plugin-runtime` | Gemeinsame Helfer für die Plugin-Laufzeit | Plugin-Befehls-/Hook-/HTTP-/interaktive Helfer |
  | `plugin-sdk/hook-runtime` | Helfer für Hook-Pipelines | Gemeinsame Pipeline-Helfer für Webhook-/interne Hooks |
  | `plugin-sdk/lazy-runtime` | Helfer für Lazy Runtime | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeMethodBinder`, `createLazyRuntimeNamedExport`, `createLazyRuntimeSurface` |
  | `plugin-sdk/process-runtime` | Prozesshelfer | Gemeinsame Exec-Helfer |
  | `plugin-sdk/cli-runtime` | CLI-Laufzeithelfer | Helfer für Befehlsformatierung, Waits und Versionsfunktionen |
  | `plugin-sdk/gateway-runtime` | Gateway-Helfer | Gateway-Client und Patch-Helfer für Channel-Status |
  | `plugin-sdk/config-runtime` | Config-Helfer | Helfer zum Laden/Schreiben von Config |
  | `plugin-sdk/telegram-command-config` | Telegram-Befehlshelfer | Fallback-stabile Telegram-Befehlsvalidierungshelfer, wenn die gebündelte Telegram-Vertragsoberfläche nicht verfügbar ist |
  | `plugin-sdk/approval-runtime` | Helfer für Genehmigungs-Prompts | Payloads für Exec-/Plugin-Genehmigungen, Helfer für Genehmigungsfähigkeiten/-profile, natives Routing/Laufzeitverhalten für Genehmigungen |
  | `plugin-sdk/approval-auth-runtime` | Helfer für Genehmigungsautorisierung | Auflösung von Approvern, Aktionsautorisierung im selben Chat |
  | `plugin-sdk/approval-client-runtime` | Helfer für Genehmigungsclients | Helfer für native Exec-Genehmigungsprofile/-filter |
  | `plugin-sdk/approval-delivery-runtime` | Helfer für Genehmigungszustellung | Native Adapter für Genehmigungsfähigkeiten/-zustellung |
  | `plugin-sdk/approval-native-runtime` | Helfer für Genehmigungsziele | Native Helfer für Ziel-/Account-Binding von Genehmigungen |
  | `plugin-sdk/approval-reply-runtime` | Helfer für Genehmigungsantworten | Helfer für Antwort-Payloads bei Exec-/Plugin-Genehmigungen |
  | `plugin-sdk/security-runtime` | Sicherheitshelfer | Gemeinsame Helfer für Trust, DM-Gating, externe Inhalte und Geheimnissammlung |
  | `plugin-sdk/ssrf-policy` | Helfer für SSRF-Richtlinien | Helfer für Host-Allowlists und Richtlinien für private Netzwerke |
  | `plugin-sdk/ssrf-runtime` | SSRF-Laufzeithelfer | Helfer für Pinned Dispatcher, Guarded Fetch und SSRF-Richtlinien |
  | `plugin-sdk/collection-runtime` | Helfer für begrenzte Caches | `pruneMapToMaxSize` |
  | `plugin-sdk/diagnostic-runtime` | Helfer für Diagnose-Gating | `isDiagnosticFlagEnabled`, `isDiagnosticsEnabled` |
  | `plugin-sdk/error-runtime` | Helfer zur Fehlerformatierung | `formatUncaughtError`, `isApprovalNotFoundError`, Helfer für Fehlergraphen |
  | `plugin-sdk/fetch-runtime` | Helfer für Wrapped Fetch/Proxys | `resolveFetch`, Proxy-Helfer |
  | `plugin-sdk/host-runtime` | Helfer zur Host-Normalisierung | `normalizeHostname`, `normalizeScpRemoteHost` |
  | `plugin-sdk/retry-runtime` | Retry-Helfer | `RetryConfig`, `retryAsync`, Policy-Runner |
  | `plugin-sdk/allow-from` | Formatierung von Allowlists | `formatAllowFromLowercase` |
  | `plugin-sdk/allowlist-resolution` | Zuordnung von Allowlist-Eingaben | `mapAllowlistResolutionInputs` |
  | `plugin-sdk/command-auth` | Befehls-Gating und Helfer für Befehlsoberflächen | `resolveControlCommandGate`, Helfer für Senderautorisierung, Helfer für Befehlsregistrierung |
  | `plugin-sdk/secret-input` | Parsing geheimer Eingaben | Helfer für geheime Eingaben |
  | `plugin-sdk/webhook-ingress` | Helfer für Webhook-Anfragen | Hilfsfunktionen für Webhook-Ziele |
  | `plugin-sdk/webhook-request-guards` | Guard-Helfer für Webhook-Bodys | Helfer zum Lesen/Begrenzen von Request-Bodys |
  | `plugin-sdk/reply-runtime` | Gemeinsame Antwort-Laufzeit | Inbound-Dispatch, Heartbeat, Antwortplanung, Chunking |
  | `plugin-sdk/reply-dispatch-runtime` | Schmale Helfer für Antwort-Dispatch | Helfer zum Finalisieren + Provider-Dispatch |
  | `plugin-sdk/reply-history` | Helfer für Antwortverlauf | `buildHistoryContext`, `buildPendingHistoryContextFromMap`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` |
  | `plugin-sdk/reply-reference` | Planung von Antwortreferenzen | `createReplyReferencePlanner` |
  | `plugin-sdk/reply-chunking` | Helfer für Antwort-Chunks | Helfer für Text-/Markdown-Chunking |
  | `plugin-sdk/session-store-runtime` | Helfer für Session-Stores | Helfer für Store-Pfad + updated-at |
  | `plugin-sdk/state-paths` | Helfer für State-Pfade | Helfer für State- und OAuth-Verzeichnisse |
  | `plugin-sdk/routing` | Helfer für Routing/Session-Keys | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId`, Helfer zur Session-Key-Normalisierung |
  | `plugin-sdk/status-helpers` | Helfer für Channel-Status | Builder für Channel-/Account-Statuszusammenfassungen, Standardwerte für Laufzeitzustand, Issue-Metadaten-Helfer |
  | `plugin-sdk/target-resolver-runtime` | Helfer für Target Resolver | Gemeinsame Helfer für Target Resolver |
  | `plugin-sdk/string-normalization-runtime` | Helfer zur String-Normalisierung | Helfer zur Slug-/String-Normalisierung |
  | `plugin-sdk/request-url` | Helfer für Request-URLs | Extrahieren von String-URLs aus request-ähnlichen Eingaben |
  | `plugin-sdk/run-command` | Helfer für getimte Befehle | Runner für getimte Befehle mit normalisiertem stdout/stderr |
  | `plugin-sdk/param-readers` | Param-Reader | Gemeinsame Param-Reader für Tool/CLI |
  | `plugin-sdk/tool-send` | Extraktion für Tool-Send | Extrahieren kanonischer Send-Zielfelder aus Tool-Argumenten |
  | `plugin-sdk/temp-path` | Helfer für temporäre Pfade | Gemeinsame Helfer für temporäre Download-Pfade |
  | `plugin-sdk/logging-core` | Logging-Helfer | Subsystem-Logger und Redaktionshelfer |
  | `plugin-sdk/markdown-table-runtime` | Helfer für Markdown-Tabellen | Helfer für Markdown-Tabellenmodi |
  | `plugin-sdk/reply-payload` | Typen für Nachrichtenantworten | Antwort-Payload-Typen |
  | `plugin-sdk/provider-setup` | Kuratierte Helfer für die Einrichtung lokaler/self-hosted Provider | Helfer für Erkennung/Config self-hosted Provider |
  | `plugin-sdk/self-hosted-provider-setup` | Gezielte Helfer für die Einrichtung OpenAI-kompatibler self-hosted Provider | Dieselben Helfer für Erkennung/Config self-hosted Provider |
  | `plugin-sdk/provider-auth-runtime` | Laufzeithelfer für Provider-Authentifizierung | Helfer zur Auflösung von API-Schlüsseln zur Laufzeit |
  | `plugin-sdk/provider-auth-api-key` | Helfer für die Einrichtung von Provider-API-Schlüsseln | Helfer für API-Key-Onboarding/Profilschreibung |
  | `plugin-sdk/provider-auth-result` | Helfer für Provider-Authentifizierungsergebnisse | Standard-Builder für OAuth-Authentifizierungsergebnisse |
  | `plugin-sdk/provider-auth-login` | Helfer für interaktive Provider-Anmeldung | Gemeinsame Helfer für interaktive Anmeldung |
  | `plugin-sdk/provider-env-vars` | Helfer für Provider-Umgebungsvariablen | Helfer für das Lookup von Auth-Umgebungsvariablen bei Providern |
  | `plugin-sdk/provider-model-shared` | Gemeinsame Helfer für Provider-Modell-/Replay | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, gemeinsame Builder für Replay-Richtlinien, Helfer für Provider-Endpunkte und Helfer zur Modell-ID-Normalisierung |
  | `plugin-sdk/provider-catalog-shared` | Gemeinsame Helfer für Provider-Kataloge | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
  | `plugin-sdk/provider-onboard` | Patches für Provider-Onboarding | Helfer für Onboarding-Config |
  | `plugin-sdk/provider-http` | Helfer für Provider-HTTP | Generische Helfer für Provider-HTTP/Endpoint-Fähigkeiten |
  | `plugin-sdk/provider-web-fetch` | Helfer für Provider-Web-Fetch | Helfer für Registrierung/Cache von Web-Fetch-Providern |
  | `plugin-sdk/provider-web-search` | Helfer für Provider-Web-Suche | Helfer für Registrierung/Cache/Config von Web-Such-Providern |
  | `plugin-sdk/provider-tools` | Helfer für Kompatibilität von Provider-Tools/-Schemas | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, Gemini-Schema-Bereinigung + Diagnosefunktionen sowie xAI-Kompatibilitätshelfer wie `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
  | `plugin-sdk/provider-usage` | Helfer für Provider-Nutzung | `fetchClaudeUsage`, `fetchGeminiUsage`, `fetchGithubCopilotUsage` und weitere Helfer für Provider-Nutzung |
  | `plugin-sdk/provider-stream` | Helfer für Provider-Stream-Wrapper | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, Stream-Wrapper-Typen und gemeinsame Wrapper-Helfer für Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
  | `plugin-sdk/keyed-async-queue` | Geordnete Async-Queue | `KeyedAsyncQueue` |
  | `plugin-sdk/media-runtime` | Gemeinsame Medienhelfer | Helfer zum Abrufen/Transformieren/Speichern von Medien sowie Builder für Medien-Payloads |
  | `plugin-sdk/media-generation-runtime` | Gemeinsame Helfer für Mediengenerierung | Gemeinsame Helfer für Failover, Kandidatenauswahl und Meldungen bei fehlenden Modellen für Bild-/Video-/Musikgenerierung |
  | `plugin-sdk/media-understanding` | Helfer für Medienverständnis | Provider-Typen für Medienverständnis sowie providerseitige Exporte für Bild-/Audio-Helfer |
  | `plugin-sdk/text-runtime` | Gemeinsame Texthelfer | Entfernen assistentensichtbarer Texte, Helfer für Markdown-Rendering/Chunking/Tabellen, Redaktionshelfer, Helfer für Directive-Tags, Safe-Text-Utilities und verwandte Text-/Logging-Helfer |
  | `plugin-sdk/text-chunking` | Helfer für Text-Chunking | Helfer für ausgehendes Text-Chunking |
  | `plugin-sdk/speech` | Speech-Helfer | Provider-Typen für Speech sowie providerseitige Helfer für Direktiven, Registrierung und Validierung |
  | `plugin-sdk/speech-core` | Gemeinsamer Speech-Kern | Provider-Typen für Speech, Registrierung, Direktiven, Normalisierung |
  | `plugin-sdk/realtime-transcription` | Helfer für Realtime-Transkription | Provider-Typen und Registrierungshelfer |
  | `plugin-sdk/realtime-voice` | Helfer für Realtime-Voice | Provider-Typen und Registrierungshelfer |
  | `plugin-sdk/image-generation-core` | Gemeinsamer Kern für Bildgenerierung | Helfer für Typen, Failover, Authentifizierung und Registrierung der Bildgenerierung |
  | `plugin-sdk/music-generation` | Helfer für Musikgenerierung | Provider-/Request-/Result-Typen für Musikgenerierung |
  | `plugin-sdk/music-generation-core` | Gemeinsamer Kern für Musikgenerierung | Typen für Musikgenerierung, Failover-Helfer, Provider-Lookup und Parsing von Model-Refs |
  | `plugin-sdk/video-generation` | Helfer für Videogenerierung | Provider-/Request-/Result-Typen für Videogenerierung |
  | `plugin-sdk/video-generation-core` | Gemeinsamer Kern für Videogenerierung | Typen für Videogenerierung, Failover-Helfer, Provider-Lookup und Parsing von Model-Refs |
  | `plugin-sdk/interactive-runtime` | Helfer für interaktive Antworten | Normalisierung/Reduktion interaktiver Antwort-Payloads |
  | `plugin-sdk/channel-config-primitives` | Primitive für Channel-Config | Schmale Primitive für Channel-Config-Schemata |
  | `plugin-sdk/channel-config-writes` | Helfer zum Schreiben von Channel-Config | Helfer zur Autorisierung von Channel-Config-Schreibvorgängen |
  | `plugin-sdk/channel-plugin-common` | Gemeinsames Channel-Präludium | Exporte des gemeinsamen Channel-Plugin-Präludiums |
  | `plugin-sdk/channel-status` | Helfer für Channel-Status | Gemeinsame Helfer für Snapshots/Zusammenfassungen des Channel-Status |
  | `plugin-sdk/allowlist-config-edit` | Helfer für Allowlist-Config | Helfer zum Bearbeiten/Lesen von Allowlist-Config |
  | `plugin-sdk/group-access` | Helfer für Gruppenzugriff | Gemeinsame Helfer für Entscheidungen zum Gruppenzugriff |
  | `plugin-sdk/direct-dm` | Helfer für direkte DMs | Gemeinsame Helfer für Authentifizierung/Guards bei direkten DMs |
  | `plugin-sdk/extension-shared` | Gemeinsame Helfer für Erweiterungen | Primitive Helfer für passive Channels/Status |
  | `plugin-sdk/webhook-targets` | Helfer für Webhook-Ziele | Registry für Webhook-Ziele und Helfer für Route-Installation |
  | `plugin-sdk/webhook-path` | Helfer für Webhook-Pfade | Helfer zur Normalisierung von Webhook-Pfaden |
  | `plugin-sdk/web-media` | Gemeinsame Helfer für Web-Medien | Helfer zum Laden entfernter/lokaler Medien |
  | `plugin-sdk/zod` | Zod-Re-Export | Re-exportiertes `zod` für Plugin-SDK-Konsumenten |
  | `plugin-sdk/memory-core` | Gebündelte Helfer für memory-core | Helper-Oberfläche für Memory-Manager/Config/Datei/CLI |
  | `plugin-sdk/memory-core-engine-runtime` | Laufzeit-Fassade der Memory-Engine | Laufzeit-Fassade für Memory-Index/Suche |
  | `plugin-sdk/memory-core-host-engine-foundation` | Host-Foundation-Engine für Memory | Exporte der Host-Foundation-Engine für Memory |
  | `plugin-sdk/memory-core-host-engine-embeddings` | Host-Embedding-Engine für Memory | Exporte der Host-Embedding-Engine für Memory |
  | `plugin-sdk/memory-core-host-engine-qmd` | Host-QMD-Engine für Memory | Exporte der Host-QMD-Engine für Memory |
  | `plugin-sdk/memory-core-host-engine-storage` | Host-Storage-Engine für Memory | Exporte der Host-Storage-Engine für Memory |
  | `plugin-sdk/memory-core-host-multimodal` | Multimodale Host-Helfer für Memory | Multimodale Host-Helfer für Memory |
  | `plugin-sdk/memory-core-host-query` | Host-Query-Helfer für Memory | Host-Query-Helfer für Memory |
  | `plugin-sdk/memory-core-host-secret` | Host-Helfer für Geheimnisse in Memory | Host-Helfer für Geheimnisse in Memory |
  | `plugin-sdk/memory-core-host-events` | Host-Helfer für Event-Journale in Memory | Host-Helfer für Event-Journale in Memory |
  | `plugin-sdk/memory-core-host-status` | Host-Helfer für Status in Memory | Host-Helfer für Status in Memory |
  | `plugin-sdk/memory-core-host-runtime-cli` | Host-CLI-Laufzeit für Memory | Host-CLI-Laufzeithelfer für Memory |
  | `plugin-sdk/memory-core-host-runtime-core` | Host-Core-Laufzeit für Memory | Host-Core-Laufzeithelfer für Memory |
  | `plugin-sdk/memory-core-host-runtime-files` | Host-Datei-/Laufzeithelfer für Memory | Host-Datei-/Laufzeithelfer für Memory |
  | `plugin-sdk/memory-host-core` | Alias für Host-Core-Laufzeit von Memory | Anbieterneutraler Alias für Host-Core-Laufzeithelfer von Memory |
  | `plugin-sdk/memory-host-events` | Alias für Host-Event-Journal von Memory | Anbieterneutraler Alias für Host-Helfer des Event-Journals von Memory |
  | `plugin-sdk/memory-host-files` | Alias für Host-Datei-/Laufzeit von Memory | Anbieterneutraler Alias für Host-Datei-/Laufzeithelfer von Memory |
  | `plugin-sdk/memory-host-markdown` | Helfer für verwaltetes Markdown | Gemeinsame Helfer für verwaltetes Markdown bei Memory-nahen Plugins |
  | `plugin-sdk/memory-host-search` | Fassade für aktive Memory-Suche | Lazy Runtime-Fassade des Search-Managers für aktives Memory |
  | `plugin-sdk/memory-host-status` | Alias für Host-Status von Memory | Anbieterneutraler Alias für Host-Statushelfer von Memory |
  | `plugin-sdk/memory-lancedb` | Gebündelte Helfer für memory-lancedb | Helper-Oberfläche für memory-lancedb |
  | `plugin-sdk/testing` | Test-Utilities | Test-Helfer und Mocks |
</Accordion>

Diese Tabelle ist bewusst die übliche Migrations-Teilmenge und nicht die vollständige SDK-Oberfläche. Die vollständige Liste mit über 200 Entry-Points befindet sich in `scripts/lib/plugin-sdk-entrypoints.json`.

Diese Liste enthält weiterhin einige Helper-Seams für gebündelte Plugins wie `plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`, `plugin-sdk/zalo-setup` und `plugin-sdk/matrix*`. Diese bleiben für die Wartung gebündelter Plugins und zur Kompatibilität exportiert, werden jedoch bewusst aus der üblichen Migrationstabelle ausgelassen und sind nicht das empfohlene Ziel für neuen Plugin-Code.

Dieselbe Regel gilt für andere Familien gebündelter Helfer wie:

- Browser-Support-Helfer: `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support`
- Matrix: `plugin-sdk/matrix*`
- LINE: `plugin-sdk/line*`
- IRC: `plugin-sdk/irc*`
- gebündelte Helfer-/Plugin-Oberflächen wie `plugin-sdk/googlechat`,
  `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles*`,
  `plugin-sdk/mattermost*`, `plugin-sdk/msteams`,
  `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`,
  `plugin-sdk/twitch`,
  `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`,
  `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`,
  `plugin-sdk/thread-ownership` und `plugin-sdk/voice-call`

`plugin-sdk/github-copilot-token` stellt derzeit die schmale Token-Helferoberfläche `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken` und `resolveCopilotApiToken` bereit.

Verwenden Sie den schmalsten Import, der zur Aufgabe passt. Wenn Sie einen Export nicht finden können, prüfen Sie den Quellcode unter `src/plugin-sdk/` oder fragen Sie in Discord.

## Zeitplan für die Entfernung

| Wann | Was passiert |
| ---------------------- | ----------------------------------------------------------------------- |
| **Jetzt** | Veraltete Oberflächen geben Laufzeitwarnungen aus |
| **Nächste Hauptversion** | Veraltete Oberflächen werden entfernt; Plugins, die sie weiterhin verwenden, schlagen fehl |

Alle Kern-Plugins wurden bereits migriert. Externe Plugins sollten vor der nächsten Hauptversion migrieren.

## Warnungen vorübergehend unterdrücken

Setzen Sie diese Umgebungsvariablen, während Sie an der Migration arbeiten:

```bash
OPENCLAW_SUPPRESS_PLUGIN_SDK_COMPAT_WARNING=1 openclaw gateway run
OPENCLAW_SUPPRESS_EXTENSION_API_WARNING=1 openclaw gateway run
```

Dies ist ein vorübergehender Notausgang, keine dauerhafte Lösung.

## Verwandte Themen

- [Erste Schritte](/de/plugins/building-plugins) — Erstellen Sie Ihr erstes Plugin
- [SDK-Überblick](/de/plugins/sdk-overview) — vollständige Referenz für Subpath-Imports
- [Channel-Plugins](/de/plugins/sdk-channel-plugins) — Erstellen von Channel-Plugins
- [Provider-Plugins](/de/plugins/sdk-provider-plugins) — Erstellen von Provider-Plugins
- [Plugin-Interna](/de/plugins/architecture) — detaillierter Einblick in die Architektur
- [Plugin-Manifest](/de/plugins/manifest) — Referenz für das Manifest-Schema
