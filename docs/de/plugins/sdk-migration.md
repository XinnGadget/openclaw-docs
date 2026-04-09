---
read_when:
    - Sie sehen die Warnung `OPENCLAW_PLUGIN_SDK_COMPAT_DEPRECATED`
    - Sie sehen die Warnung `OPENCLAW_EXTENSION_API_DEPRECATED`
    - Sie aktualisieren ein Plugin auf die moderne Plugin-Architektur
    - Sie pflegen ein externes OpenClaw-Plugin
sidebarTitle: Migrate to SDK
summary: Von der alten Abwärtskompatibilitätsschicht auf das moderne Plugin SDK migrieren
title: Plugin-SDK-Migration
x-i18n:
    generated_at: "2026-04-09T01:31:04Z"
    model: gpt-5.4
    provider: openai
    source_hash: 60cbb6c8be30d17770887d490c14e3a4538563339a5206fb419e51e0558bbc07
    source_path: plugins/sdk-migration.md
    workflow: 15
---

# Plugin-SDK-Migration

OpenClaw ist von einer breiten Abwärtskompatibilitätsschicht zu einer modernen Plugin-
Architektur mit fokussierten, dokumentierten Imports übergegangen. Wenn Ihr Plugin vor
der neuen Architektur erstellt wurde, hilft Ihnen diese Anleitung bei der Migration.

## Was sich ändert

Das alte Plugin-System stellte zwei weit offene Oberflächen bereit, über die Plugins
alles importieren konnten, was sie von einem einzigen Einstiegspunkt aus benötigten:

- **`openclaw/plugin-sdk/compat`** — ein einzelner Import, der Dutzende von
  Hilfsfunktionen re-exportierte. Er wurde eingeführt, damit ältere hookbasierte Plugins weiter funktionierten, während die
  neue Plugin-Architektur aufgebaut wurde.
- **`openclaw/extension-api`** — eine Brücke, die Plugins direkten Zugriff auf
  hostseitige Hilfsfunktionen wie den eingebetteten Agent-Runner gab.

Beide Oberflächen sind jetzt **veraltet**. Sie funktionieren zur Laufzeit weiterhin, aber neue
Plugins dürfen sie nicht verwenden, und bestehende Plugins sollten migrieren, bevor die nächste
Hauptversion sie entfernt.

<Warning>
  Die Abwärtskompatibilitätsschicht wird in einer zukünftigen Hauptversion entfernt.
  Plugins, die weiterhin aus diesen Oberflächen importieren, werden dann nicht mehr funktionieren.
</Warning>

## Warum sich das geändert hat

Der alte Ansatz verursachte Probleme:

- **Langsamer Start** — das Importieren einer Hilfsfunktion lud Dutzende nicht zusammenhängender Module
- **Zirkuläre Abhängigkeiten** — breite Re-Exports machten es leicht, Importzyklen zu erzeugen
- **Unklare API-Oberfläche** — es gab keine Möglichkeit zu erkennen, welche Exporte stabil und welche intern waren

Das moderne Plugin SDK behebt das: Jeder Importpfad (`openclaw/plugin-sdk/\<subpath\>`)
ist ein kleines, in sich geschlossenes Modul mit einem klaren Zweck und dokumentiertem Vertrag.

Alte Convenience-Seams für Provider in gebündelten Kanälen entfallen ebenfalls. Imports
wie `openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp`,
kanalmarkenspezifische Helper-Seams und
`openclaw/plugin-sdk/telegram-core` waren private Mono-Repo-Abkürzungen, keine
stabilen Plugin-Verträge. Verwenden Sie stattdessen schmale generische SDK-Unterpfade. Innerhalb des
gebündelten Plugin-Workspaces sollten provider-eigene Hilfsfunktionen im eigenen
`api.ts` oder `runtime-api.ts` dieses Plugins bleiben.

Aktuelle Beispiele für gebündelte Provider:

- Anthropic hält Claude-spezifische Stream-Hilfsfunktionen in seiner eigenen `api.ts` /
  `contract-api.ts`-Naht
- OpenAI hält Provider-Builder, Standardmodell-Hilfsfunktionen und Realtime-Provider-
  Builder in seiner eigenen `api.ts`
- OpenRouter hält Provider-Builder und Onboarding-/Konfigurationshilfsfunktionen in seiner eigenen
  `api.ts`

## Migration

<Steps>
  <Step title="Native Approval-Handler auf Capability-Fakten migrieren">
    Approval-fähige Kanal-Plugins stellen natives Approval-Verhalten jetzt über
    `approvalCapability.nativeRuntime` plus die gemeinsame Runtime-Context-Registry bereit.

    Wichtige Änderungen:

    - Ersetzen Sie `approvalCapability.handler.loadRuntime(...)` durch
      `approvalCapability.nativeRuntime`
    - Verschieben Sie Approval-spezifische Auth-/Delivery-Logik von der alten Verkabelung `plugin.auth` /
      `plugin.approvals` auf `approvalCapability`
    - `ChannelPlugin.approvals` wurde aus dem öffentlichen Vertrag für Kanal-Plugins
      entfernt; verschieben Sie Delivery-/Native-/Render-Felder auf `approvalCapability`
    - `plugin.auth` bleibt nur für Login-/Logout-Abläufe von Kanälen; Approval-
      Auth-Hooks dort werden vom Core nicht mehr gelesen
    - Registrieren Sie kanal-eigene Runtime-Objekte wie Clients, Tokens oder Bolt-
      Apps über `openclaw/plugin-sdk/channel-runtime-context`
    - Senden Sie aus nativen Approval-Handlern keine plugin-eigenen Umleitungs-Hinweise;
      Core verwaltet Hinweise „anderswo zugestellt“ jetzt anhand der tatsächlichen Delivery-Ergebnisse
    - Wenn Sie `channelRuntime` an `createChannelManager(...)` übergeben, stellen Sie eine
      echte `createPluginRuntime().channel`-Oberfläche bereit. Teilweise Stubs werden abgelehnt.

    Siehe `/plugins/sdk-channel-plugins` für das aktuelle Layout der Approval-Capabilities.

  </Step>

  <Step title="Fallback-Verhalten des Windows-Wrappers prüfen">
    Wenn Ihr Plugin `openclaw/plugin-sdk/windows-spawn` verwendet,
    schlagen nicht aufgelöste Windows-Wrapper vom Typ `.cmd`/`.bat` jetzt standardmäßig fehl, es sei denn, Sie übergeben explizit
    `allowShellFallback: true`.

    ```typescript
    // Vorher
    const program = applyWindowsSpawnProgramPolicy({ candidate });

    // Nachher
    const program = applyWindowsSpawnProgramPolicy({
      candidate,
      // Nur für vertrauenswürdige Kompatibilitätsaufrufer setzen, die
      // bewusst einen Shell-vermittelten Fallback akzeptieren.
      allowShellFallback: true,
    });
    ```

    Wenn Ihr Aufrufer nicht bewusst auf einen Shell-Fallback angewiesen ist, setzen Sie
    `allowShellFallback` nicht und behandeln Sie stattdessen den ausgelösten Fehler.

  </Step>

  <Step title="Veraltete Imports finden">
    Durchsuchen Sie Ihr Plugin nach Imports aus einer der beiden veralteten Oberflächen:

    ```bash
    grep -r "plugin-sdk/compat" my-plugin/
    grep -r "openclaw/extension-api" my-plugin/
    ```

  </Step>

  <Step title="Durch fokussierte Imports ersetzen">
    Jeder Export aus der alten Oberfläche entspricht einem bestimmten modernen Importpfad:

    ```typescript
    // Vorher (veraltete Abwärtskompatibilitätsschicht)
    import {
      createChannelReplyPipeline,
      createPluginRuntimeStore,
      resolveControlCommandGate,
    } from "openclaw/plugin-sdk/compat";

    // Nachher (moderne fokussierte Imports)
    import { createChannelReplyPipeline } from "openclaw/plugin-sdk/channel-reply-pipeline";
    import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
    import { resolveControlCommandGate } from "openclaw/plugin-sdk/command-auth";
    ```

    Verwenden Sie für hostseitige Hilfsfunktionen die injizierte Plugin-Runtime, anstatt direkt
    zu importieren:

    ```typescript
    // Vorher (veraltete extension-api-Brücke)
    import { runEmbeddedPiAgent } from "openclaw/extension-api";
    const result = await runEmbeddedPiAgent({ sessionId, prompt });

    // Nachher (injizierte Runtime)
    const result = await api.runtime.agent.runEmbeddedPiAgent({ sessionId, prompt });
    ```

    Dasselbe Muster gilt für andere alte Bridge-Hilfsfunktionen:

    | Alter Import | Modernes Äquivalent |
    | --- | --- |
    | `resolveAgentDir` | `api.runtime.agent.resolveAgentDir` |
    | `resolveAgentWorkspaceDir` | `api.runtime.agent.resolveAgentWorkspaceDir` |
    | `resolveAgentIdentity` | `api.runtime.agent.resolveAgentIdentity` |
    | `resolveThinkingDefault` | `api.runtime.agent.resolveThinkingDefault` |
    | `resolveAgentTimeoutMs` | `api.runtime.agent.resolveAgentTimeoutMs` |
    | `ensureAgentWorkspace` | `api.runtime.agent.ensureAgentWorkspace` |
    | Hilfsfunktionen für den Sitzungsspeicher | `api.runtime.agent.session.*` |

  </Step>

  <Step title="Erstellen und testen">
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
  | `plugin-sdk/plugin-entry` | Kanonische Hilfsfunktion für Plugin-Einstiegspunkte | `definePluginEntry` |
  | `plugin-sdk/core` | Alter Sammel-Re-Export für Definitionen/Builder von Kanaleinstiegspunkten | `defineChannelPluginEntry`, `createChatChannelPlugin` |
  | `plugin-sdk/config-schema` | Export des Root-Konfigurationsschemas | `OpenClawSchema` |
  | `plugin-sdk/provider-entry` | Hilfsfunktion für Single-Provider-Einstiegspunkte | `defineSingleProviderPluginEntry` |
  | `plugin-sdk/channel-core` | Fokussierte Definitionen und Builder für Kanaleinstiegspunkte | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
  | `plugin-sdk/setup` | Gemeinsame Hilfsfunktionen für Setup-Assistenten | Allowlist-Prompts, Builder für Setup-Status |
  | `plugin-sdk/setup-runtime` | Laufzeit-Hilfsfunktionen zur Setup-Zeit | Importsichere Setup-Patch-Adapter, Lookup-Note-Hilfsfunktionen, `promptResolvedAllowFrom`, `splitSetupEntries`, delegierte Setup-Proxys |
  | `plugin-sdk/setup-adapter-runtime` | Hilfsfunktionen für Setup-Adapter | `createEnvPatchedAccountSetupAdapter` |
  | `plugin-sdk/setup-tools` | Hilfsfunktionen für Setup-Tools | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
  | `plugin-sdk/account-core` | Hilfsfunktionen für Mehrkonten | Hilfsfunktionen für Kontoliste/Konfiguration/Action-Gates |
  | `plugin-sdk/account-id` | Hilfsfunktionen für Konto-IDs | `DEFAULT_ACCOUNT_ID`, Normalisierung von Konto-IDs |
  | `plugin-sdk/account-resolution` | Hilfsfunktionen für Konto-Lookups | Hilfsfunktionen für Konto-Lookup + Standard-Fallback |
  | `plugin-sdk/account-helpers` | Schmale Kontohilfsfunktionen | Hilfsfunktionen für Kontoliste/Kontoaktionen |
  | `plugin-sdk/channel-setup` | Adapter für Setup-Assistenten | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard` sowie `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
  | `plugin-sdk/channel-pairing` | Grundbausteine für DM-Pairing | `createChannelPairingController` |
  | `plugin-sdk/channel-reply-pipeline` | Verkabelung für Antwortpräfix + Tippen | `createChannelReplyPipeline` |
  | `plugin-sdk/channel-config-helpers` | Fabriken für Konfigurationsadapter | `createHybridChannelConfigAdapter` |
  | `plugin-sdk/channel-config-schema` | Builder für Konfigurationsschemata | Typen für Kanal-Konfigurationsschemata |
  | `plugin-sdk/telegram-command-config` | Hilfsfunktionen für Telegram-Befehlskonfiguration | Normalisierung von Befehlsnamen, Kürzen von Beschreibungen, Validierung von Duplikaten/Konflikten |
  | `plugin-sdk/channel-policy` | Auflösung von Gruppen-/DM-Richtlinien | `resolveChannelGroupRequireMention` |
  | `plugin-sdk/channel-lifecycle` | Verfolgung des Kontostatus | `createAccountStatusSink` |
  | `plugin-sdk/inbound-envelope` | Hilfsfunktionen für eingehende Umschläge | Gemeinsame Hilfsfunktionen für Routen- und Umschlag-Builder |
  | `plugin-sdk/inbound-reply-dispatch` | Hilfsfunktionen für eingehende Antworten | Gemeinsame Hilfsfunktionen zum Aufzeichnen und Verteilen |
  | `plugin-sdk/messaging-targets` | Parsen von Nachrichtenzielen | Hilfsfunktionen zum Parsen/Abgleichen von Zielen |
  | `plugin-sdk/outbound-media` | Hilfsfunktionen für ausgehende Medien | Gemeinsames Laden ausgehender Medien |
  | `plugin-sdk/outbound-runtime` | Laufzeit-Hilfsfunktionen für ausgehende Vorgänge | Hilfsfunktionen für ausgehende Identität/Sende-Delegierung |
  | `plugin-sdk/thread-bindings-runtime` | Hilfsfunktionen für Thread-Bindings | Hilfsfunktionen für Lifecycle und Adapter von Thread-Bindings |
  | `plugin-sdk/agent-media-payload` | Alte Hilfsfunktionen für Medien-Payloads | Builder für Agent-Medien-Payloads für alte Feldlayouts |
  | `plugin-sdk/channel-runtime` | Veraltetes Kompatibilitäts-Shim | Nur alte Kanal-Laufzeitdienstprogramme |
  | `plugin-sdk/channel-send-result` | Typen für Sendeergebnisse | Typen für Antwortergebnisse |
  | `plugin-sdk/runtime-store` | Persistenter Plugin-Speicher | `createPluginRuntimeStore` |
  | `plugin-sdk/runtime` | Breite Laufzeit-Hilfsfunktionen | Hilfsfunktionen für Runtime/Logging/Backup/Plugin-Installation |
  | `plugin-sdk/runtime-env` | Schmale Hilfsfunktionen für Laufzeitumgebungen | Logger-/Laufzeitumgebungs-, Timeout-, Retry- und Backoff-Hilfsfunktionen |
  | `plugin-sdk/plugin-runtime` | Gemeinsame Plugin-Laufzeit-Hilfsfunktionen | Hilfsfunktionen für Plugin-Befehle/Hooks/HTTP/interaktive Abläufe |
  | `plugin-sdk/hook-runtime` | Hilfsfunktionen für Hook-Pipelines | Gemeinsame Hilfsfunktionen für Webhook-/interne Hook-Pipelines |
  | `plugin-sdk/lazy-runtime` | Hilfsfunktionen für Lazy Runtime | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeMethodBinder`, `createLazyRuntimeNamedExport`, `createLazyRuntimeSurface` |
  | `plugin-sdk/process-runtime` | Hilfsfunktionen für Prozesse | Gemeinsame Exec-Hilfsfunktionen |
  | `plugin-sdk/cli-runtime` | Hilfsfunktionen für CLI-Laufzeiten | Befehlsformatierung, Wartevorgänge, Versionshilfsfunktionen |
  | `plugin-sdk/gateway-runtime` | Hilfsfunktionen für Gateways | Gateway-Client- und Patch-Hilfsfunktionen für Kanalstatus |
  | `plugin-sdk/config-runtime` | Hilfsfunktionen für Konfigurationen | Hilfsfunktionen zum Laden/Schreiben von Konfigurationen |
  | `plugin-sdk/telegram-command-config` | Hilfsfunktionen für Telegram-Befehle | Fallback-stabile Hilfsfunktionen zur Telegram-Befehlsvalidierung, wenn die gebündelte Telegram-Vertragsoberfläche nicht verfügbar ist |
  | `plugin-sdk/approval-runtime` | Hilfsfunktionen für Approval-Prompts | Payloads für Exec-/Plugin-Approval, Hilfsfunktionen für Approval-Capabilities/-Profile, native Approval-Routing-/Runtime-Hilfsfunktionen |
  | `plugin-sdk/approval-auth-runtime` | Hilfsfunktionen für Approval-Authentifizierung | Approver-Auflösung, Authentifizierung von Aktionen im selben Chat |
  | `plugin-sdk/approval-client-runtime` | Hilfsfunktionen für Approval-Clients | Hilfsfunktionen für native Exec-Approval-Profile/-Filter |
  | `plugin-sdk/approval-delivery-runtime` | Hilfsfunktionen für Approval-Delivery | Adapter für native Approval-Capabilities/-Delivery |
  | `plugin-sdk/approval-gateway-runtime` | Hilfsfunktionen für Approval-Gateways | Gemeinsame Hilfsfunktion für die Auflösung von Approval-Gateways |
  | `plugin-sdk/approval-handler-adapter-runtime` | Hilfsfunktionen für Approval-Adapter | Leichtgewichtige Hilfsfunktionen zum Laden nativer Approval-Adapter für heiße Kanaleinstiegspunkte |
  | `plugin-sdk/approval-handler-runtime` | Hilfsfunktionen für Approval-Handler | Breitere Laufzeit-Hilfsfunktionen für Approval-Handler; bevorzugen Sie die schmaleren Adapter-/Gateway-Seams, wenn diese ausreichen |
  | `plugin-sdk/approval-native-runtime` | Hilfsfunktionen für Approval-Ziele | Hilfsfunktionen für native Approval-Ziel-/Kontobindungen |
  | `plugin-sdk/approval-reply-runtime` | Hilfsfunktionen für Approval-Antworten | Hilfsfunktionen für Antwort-Payloads bei Exec-/Plugin-Approval |
  | `plugin-sdk/channel-runtime-context` | Hilfsfunktionen für Kanal-Runtime-Context | Generische Hilfsfunktionen zum Registrieren/Abrufen/Beobachten von Kanal-Runtime-Contexts |
  | `plugin-sdk/security-runtime` | Hilfsfunktionen für Sicherheit | Gemeinsame Hilfsfunktionen für Trust, DM-Gating, externe Inhalte und Secret-Erfassung |
  | `plugin-sdk/ssrf-policy` | Hilfsfunktionen für SSRF-Richtlinien | Hilfsfunktionen für Host-Allowlist- und Private-Network-Richtlinien |
  | `plugin-sdk/ssrf-runtime` | Laufzeit-Hilfsfunktionen für SSRF | Hilfsfunktionen für Pinned Dispatcher, Guarded Fetch und SSRF-Richtlinien |
  | `plugin-sdk/collection-runtime` | Hilfsfunktionen für begrenzte Caches | `pruneMapToMaxSize` |
  | `plugin-sdk/diagnostic-runtime` | Hilfsfunktionen für Diagnose-Gating | `isDiagnosticFlagEnabled`, `isDiagnosticsEnabled` |
  | `plugin-sdk/error-runtime` | Hilfsfunktionen für Fehlerformatierung | `formatUncaughtError`, `isApprovalNotFoundError`, Hilfsfunktionen für Fehlergraphen |
  | `plugin-sdk/fetch-runtime` | Hilfsfunktionen für gewrapptes Fetch/Proxy | `resolveFetch`, Proxy-Hilfsfunktionen |
  | `plugin-sdk/host-runtime` | Hilfsfunktionen für Host-Normalisierung | `normalizeHostname`, `normalizeScpRemoteHost` |
  | `plugin-sdk/retry-runtime` | Hilfsfunktionen für Wiederholungen | `RetryConfig`, `retryAsync`, Richtlinien-Runner |
  | `plugin-sdk/allow-from` | Formatierung von Allowlists | `formatAllowFromLowercase` |
  | `plugin-sdk/allowlist-resolution` | Mapping von Allowlist-Eingaben | `mapAllowlistResolutionInputs` |
  | `plugin-sdk/command-auth` | Command-Gating- und Command-Surface-Hilfsfunktionen | `resolveControlCommandGate`, Hilfsfunktionen für Senderautorisierung, Hilfsfunktionen für Befehlsregistrierung |
  | `plugin-sdk/command-status` | Renderer für Befehlsstatus/-hilfe | `buildCommandsMessage`, `buildCommandsMessagePaginated`, `buildHelpMessage` |
  | `plugin-sdk/secret-input` | Parsen geheimer Eingaben | Hilfsfunktionen für geheime Eingaben |
  | `plugin-sdk/webhook-ingress` | Hilfsfunktionen für Webhook-Anfragen | Dienstprogramme für Webhook-Ziele |
  | `plugin-sdk/webhook-request-guards` | Hilfsfunktionen für Webhook-Body-Guards | Hilfsfunktionen zum Lesen/Begrenzen von Request-Bodys |
  | `plugin-sdk/reply-runtime` | Gemeinsame Antwort-Laufzeit | Eingehende Verteilung, Heartbeat, Antwortplanung, Chunking |
  | `plugin-sdk/reply-dispatch-runtime` | Schmale Hilfsfunktionen für Antwortverteilung | Hilfsfunktionen für Finalisierung + Provider-Verteilung |
  | `plugin-sdk/reply-history` | Hilfsfunktionen für Antwortverlauf | `buildHistoryContext`, `buildPendingHistoryContextFromMap`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` |
  | `plugin-sdk/reply-reference` | Planung von Antwortreferenzen | `createReplyReferencePlanner` |
  | `plugin-sdk/reply-chunking` | Hilfsfunktionen für Antwort-Chunks | Hilfsfunktionen für Text-/Markdown-Chunking |
  | `plugin-sdk/session-store-runtime` | Hilfsfunktionen für Sitzungsspeicher | Hilfsfunktionen für Speicherpfade + updated-at |
  | `plugin-sdk/state-paths` | Hilfsfunktionen für Zustandspfade | Hilfsfunktionen für Zustands- und OAuth-Verzeichnisse |
  | `plugin-sdk/routing` | Hilfsfunktionen für Routing/Sitzungsschlüssel | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId`, Hilfsfunktionen zur Normalisierung von Sitzungsschlüsseln |
  | `plugin-sdk/status-helpers` | Hilfsfunktionen für Kanalstatus | Builder für Zusammenfassungen von Kanal-/Kontostatus, Laufzeitzustandsstandards, Hilfsfunktionen für Issue-Metadaten |
  | `plugin-sdk/target-resolver-runtime` | Hilfsfunktionen für Zielauflösung | Gemeinsame Hilfsfunktionen für Zielauflösung |
  | `plugin-sdk/string-normalization-runtime` | Hilfsfunktionen für String-Normalisierung | Hilfsfunktionen für Slug-/String-Normalisierung |
  | `plugin-sdk/request-url` | Hilfsfunktionen für Request-URLs | String-URLs aus requestähnlichen Eingaben extrahieren |
  | `plugin-sdk/run-command` | Hilfsfunktionen für zeitgesteuerte Befehle | Runner für zeitgesteuerte Befehle mit normalisiertem stdout/stderr |
  | `plugin-sdk/param-readers` | Param-Reader | Gemeinsame Param-Reader für Tools/CLI |
  | `plugin-sdk/tool-payload` | Extraktion von Tool-Payloads | Normalisierte Payloads aus Tool-Ergebnisobjekten extrahieren |
  | `plugin-sdk/tool-send` | Extraktion von Tool-Sendewerten | Kanonische Sendefelder aus Tool-Argumenten extrahieren |
  | `plugin-sdk/temp-path` | Hilfsfunktionen für temporäre Pfade | Gemeinsame Hilfsfunktionen für temporäre Download-Pfade |
  | `plugin-sdk/logging-core` | Logging-Hilfsfunktionen | Subsystem-Logger und Redaktionshilfsfunktionen |
  | `plugin-sdk/markdown-table-runtime` | Hilfsfunktionen für Markdown-Tabellen | Hilfsfunktionen für Modi von Markdown-Tabellen |
  | `plugin-sdk/reply-payload` | Nachrichtenantworttypen | Antwort-Payload-Typen |
  | `plugin-sdk/provider-setup` | Kuratierte Hilfsfunktionen zum Setup lokaler/self-hosted Provider | Hilfsfunktionen für Discovery/Konfiguration self-hosted Provider |
  | `plugin-sdk/self-hosted-provider-setup` | Fokussierte Hilfsfunktionen zum Setup OpenAI-kompatibler self-hosted Provider | Dieselben Hilfsfunktionen für Discovery/Konfiguration self-hosted Provider |
  | `plugin-sdk/provider-auth-runtime` | Hilfsfunktionen für Provider-Runtime-Authentifizierung | Hilfsfunktionen zur Auflösung von API-Schlüsseln zur Laufzeit |
  | `plugin-sdk/provider-auth-api-key` | Hilfsfunktionen zum Setup von Provider-API-Schlüsseln | Hilfsfunktionen für API-Key-Onboarding/Profile-Schreiben |
  | `plugin-sdk/provider-auth-result` | Hilfsfunktionen für Provider-Auth-Ergebnisse | Standard-Builder für OAuth-Auth-Ergebnisse |
  | `plugin-sdk/provider-auth-login` | Interaktive Hilfsfunktionen für Provider-Login | Gemeinsame Hilfsfunktionen für interaktives Login |
  | `plugin-sdk/provider-env-vars` | Hilfsfunktionen für Provider-Umgebungsvariablen | Hilfsfunktionen zum Lookup von Provider-Auth-Umgebungsvariablen |
  | `plugin-sdk/provider-model-shared` | Gemeinsame Hilfsfunktionen für Provider-Modelle/-Replay | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, gemeinsame Builder für Replay-Richtlinien, Hilfsfunktionen für Provider-Endpunkte und Hilfsfunktionen zur Modell-ID-Normalisierung |
  | `plugin-sdk/provider-catalog-shared` | Gemeinsame Hilfsfunktionen für Provider-Kataloge | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
  | `plugin-sdk/provider-onboard` | Patches für Provider-Onboarding | Hilfsfunktionen für Onboarding-Konfiguration |
  | `plugin-sdk/provider-http` | Hilfsfunktionen für Provider-HTTP | Generische Hilfsfunktionen für Provider-HTTP/Endpoint-Capabilities |
  | `plugin-sdk/provider-web-fetch` | Hilfsfunktionen für Provider-Web-Fetch | Hilfsfunktionen für Registrierung/Cache von Web-Fetch-Providern |
  | `plugin-sdk/provider-web-search-config-contract` | Hilfsfunktionen für Provider-Websearch-Konfiguration | Schmale Hilfsfunktionen für Websearch-Konfiguration/Anmeldedaten für Provider, die keine Plugin-Aktivierungsverkabelung benötigen |
  | `plugin-sdk/provider-web-search-contract` | Hilfsfunktionen für Provider-Websearch-Verträge | Schmale Hilfsfunktionen für Verträge zu Websearch-Konfiguration/Anmeldedaten wie `createWebSearchProviderContractFields`, `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig` und bereichsbezogene Setter/Getter für Anmeldedaten |
  | `plugin-sdk/provider-web-search` | Hilfsfunktionen für Provider-Websearch | Hilfsfunktionen für Registrierung/Cache/Laufzeit von Websearch-Providern |
  | `plugin-sdk/provider-tools` | Hilfsfunktionen für Provider-Tool-/Schema-Kompatibilität | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, Gemini-Schema-Bereinigung + Diagnosen sowie xAI-Kompatibilitätshilfen wie `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
  | `plugin-sdk/provider-usage` | Hilfsfunktionen für Provider-Nutzung | `fetchClaudeUsage`, `fetchGeminiUsage`, `fetchGithubCopilotUsage` und andere Hilfsfunktionen für Provider-Nutzung |
  | `plugin-sdk/provider-stream` | Hilfsfunktionen für Provider-Stream-Wrapper | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, Typen für Stream-Wrapper und gemeinsame Wrapper-Hilfsfunktionen für Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
  | `plugin-sdk/keyed-async-queue` | Geordnete Async-Queue | `KeyedAsyncQueue` |
  | `plugin-sdk/media-runtime` | Gemeinsame Medien-Hilfsfunktionen | Hilfsfunktionen für Abruf/Transformation/Speicherung von Medien sowie Builder für Medien-Payloads |
  | `plugin-sdk/media-generation-runtime` | Gemeinsame Hilfsfunktionen für Mediengenerierung | Gemeinsame Hilfsfunktionen für Failover, Kandidatenauswahl und Hinweise bei fehlenden Modellen für Bild-/Video-/Musikgenerierung |
  | `plugin-sdk/media-understanding` | Hilfsfunktionen für Medienverständnis | Typen für Media-Understanding-Provider plus providerseitige Exporte für Bild-/Audio-Hilfsfunktionen |
  | `plugin-sdk/text-runtime` | Gemeinsame Text-Hilfsfunktionen | Entfernen von für Assistenten sichtbarem Text, Hilfsfunktionen für Markdown-Rendering/Chunking/Tabellen, Redaktionshilfsfunktionen, Hilfsfunktionen für Directive-Tags, Safe-Text-Dienstprogramme und verwandte Hilfsfunktionen für Text/Logging |
  | `plugin-sdk/text-chunking` | Hilfsfunktionen für Text-Chunking | Hilfsfunktion für Chunking ausgehender Texte |
  | `plugin-sdk/speech` | Hilfsfunktionen für Sprachausgabe | Typen für Speech-Provider plus providerseitige Hilfsfunktionen für Direktiven, Registry und Validierung |
  | `plugin-sdk/speech-core` | Gemeinsamer Kern für Sprachausgabe | Typen für Speech-Provider, Registry, Direktiven, Normalisierung |
  | `plugin-sdk/realtime-transcription` | Hilfsfunktionen für Echtzeit-Transkription | Provider-Typen und Registry-Hilfsfunktionen |
  | `plugin-sdk/realtime-voice` | Hilfsfunktionen für Echtzeit-Stimme | Provider-Typen und Registry-Hilfsfunktionen |
  | `plugin-sdk/image-generation-core` | Gemeinsamer Kern für Bildgenerierung | Typen, Failover-, Auth- und Registry-Hilfsfunktionen für Bildgenerierung |
  | `plugin-sdk/music-generation` | Hilfsfunktionen für Musikgenerierung | Typen für Music-Generation-Provider/Requests/Ergebnisse |
  | `plugin-sdk/music-generation-core` | Gemeinsamer Kern für Musikgenerierung | Typen für Musikgenerierung, Failover-Hilfsfunktionen, Provider-Lookup und Parsing von Modellreferenzen |
  | `plugin-sdk/video-generation` | Hilfsfunktionen für Videogenerierung | Typen für Video-Generation-Provider/Requests/Ergebnisse |
  | `plugin-sdk/video-generation-core` | Gemeinsamer Kern für Videogenerierung | Typen für Videogenerierung, Failover-Hilfsfunktionen, Provider-Lookup und Parsing von Modellreferenzen |
  | `plugin-sdk/interactive-runtime` | Hilfsfunktionen für interaktive Antworten | Normalisierung/Reduktion von Payloads interaktiver Antworten |
  | `plugin-sdk/channel-config-primitives` | Grundbausteine für Kanal-Konfiguration | Schmale Grundbausteine für Kanal-Konfigurationsschemata |
  | `plugin-sdk/channel-config-writes` | Hilfsfunktionen für Kanal-Konfigurationsschreibvorgänge | Hilfsfunktionen zur Autorisierung von Kanal-Konfigurationsschreibvorgängen |
  | `plugin-sdk/channel-plugin-common` | Gemeinsames Kanal-Präludium | Gemeinsame Exporte des Kanal-Plugin-Präludiums |
  | `plugin-sdk/channel-status` | Hilfsfunktionen für Kanalstatus | Gemeinsame Hilfsfunktionen für Snapshots/Zusammenfassungen des Kanalstatus |
  | `plugin-sdk/allowlist-config-edit` | Hilfsfunktionen für Allowlist-Konfigurationen | Hilfsfunktionen zum Bearbeiten/Lesen von Allowlist-Konfigurationen |
  | `plugin-sdk/group-access` | Hilfsfunktionen für Gruppenzugriff | Gemeinsame Hilfsfunktionen für Entscheidungen zum Gruppenzugriff |
  | `plugin-sdk/direct-dm` | Hilfsfunktionen für direkte DMs | Gemeinsame Hilfsfunktionen für Auth/Guards bei direkten DMs |
  | `plugin-sdk/extension-shared` | Gemeinsame Hilfsfunktionen für Erweiterungen | Primitive für passive Kanäle/Status und Ambient-Proxy-Hilfsfunktionen |
  | `plugin-sdk/webhook-targets` | Hilfsfunktionen für Webhook-Ziele | Registry für Webhook-Ziele und Hilfsfunktionen für die Routeninstallation |
  | `plugin-sdk/webhook-path` | Hilfsfunktionen für Webhook-Pfade | Hilfsfunktionen für die Normalisierung von Webhook-Pfaden |
  | `plugin-sdk/web-media` | Gemeinsame Hilfsfunktionen für Webmedien | Hilfsfunktionen zum Laden entfernter/lokaler Medien |
  | `plugin-sdk/zod` | Zod-Re-Export | Re-exportiertes `zod` für Plugin-SDK-Konsumenten |
  | `plugin-sdk/memory-core` | Gebündelte Hilfsfunktionen für memory-core | Hilfsoberfläche für Speicherverwaltung/Konfiguration/Dateien/CLI |
  | `plugin-sdk/memory-core-engine-runtime` | Laufzeit-Fassade für die Speicher-Engine | Laufzeit-Fassade für Speicherindex/Suche |
  | `plugin-sdk/memory-core-host-engine-foundation` | Host-Foundation-Engine für Speicher | Exporte der Host-Foundation-Engine für Speicher |
  | `plugin-sdk/memory-core-host-engine-embeddings` | Host-Embedding-Engine für Speicher | Exporte der Host-Embedding-Engine für Speicher |
  | `plugin-sdk/memory-core-host-engine-qmd` | Host-QMD-Engine für Speicher | Exporte der Host-QMD-Engine für Speicher |
  | `plugin-sdk/memory-core-host-engine-storage` | Host-Storage-Engine für Speicher | Exporte der Host-Storage-Engine für Speicher |
  | `plugin-sdk/memory-core-host-multimodal` | Hilfsfunktionen für multimodalen Speicher-Host | Hilfsfunktionen für multimodalen Speicher-Host |
  | `plugin-sdk/memory-core-host-query` | Hilfsfunktionen für Speicher-Host-Abfragen | Hilfsfunktionen für Speicher-Host-Abfragen |
  | `plugin-sdk/memory-core-host-secret` | Hilfsfunktionen für Speicher-Host-Secrets | Hilfsfunktionen für Speicher-Host-Secrets |
  | `plugin-sdk/memory-core-host-events` | Hilfsfunktionen für Ereignisjournale des Speicher-Hosts | Hilfsfunktionen für Ereignisjournale des Speicher-Hosts |
  | `plugin-sdk/memory-core-host-status` | Hilfsfunktionen für Speicher-Host-Status | Hilfsfunktionen für Speicher-Host-Status |
  | `plugin-sdk/memory-core-host-runtime-cli` | CLI-Laufzeit des Speicher-Hosts | CLI-Laufzeit-Hilfsfunktionen des Speicher-Hosts |
  | `plugin-sdk/memory-core-host-runtime-core` | Kernlaufzeit des Speicher-Hosts | Kernlaufzeit-Hilfsfunktionen des Speicher-Hosts |
  | `plugin-sdk/memory-core-host-runtime-files` | Datei-/Laufzeit-Hilfsfunktionen des Speicher-Hosts | Datei-/Laufzeit-Hilfsfunktionen des Speicher-Hosts |
  | `plugin-sdk/memory-host-core` | Alias für Kernlaufzeit des Speicher-Hosts | Anbieterneutraler Alias für Kernlaufzeit-Hilfsfunktionen des Speicher-Hosts |
  | `plugin-sdk/memory-host-events` | Alias für Ereignisjournale des Speicher-Hosts | Anbieterneutraler Alias für Hilfsfunktionen für Ereignisjournale des Speicher-Hosts |
  | `plugin-sdk/memory-host-files` | Alias für Datei-/Laufzeit des Speicher-Hosts | Anbieterneutraler Alias für Datei-/Laufzeit-Hilfsfunktionen des Speicher-Hosts |
  | `plugin-sdk/memory-host-markdown` | Hilfsfunktionen für verwaltetes Markdown | Gemeinsame Hilfsfunktionen für verwaltetes Markdown für speichernahe Plugins |
  | `plugin-sdk/memory-host-search` | Fassade für aktive Speichersuche | Lazy Runtime-Fassade des Search-Managers für aktiven Speicher |
  | `plugin-sdk/memory-host-status` | Alias für Speicher-Host-Status | Anbieterneutraler Alias für Hilfsfunktionen für Speicher-Host-Status |
  | `plugin-sdk/memory-lancedb` | Gebündelte Hilfsfunktionen für memory-lancedb | Hilfsoberfläche für memory-lancedb |
  | `plugin-sdk/testing` | Testdienstprogramme | Testhilfsfunktionen und Mocks |
</Accordion>

Diese Tabelle ist absichtlich nur die gängige Migrations-Teilmenge und nicht die vollständige SDK-
Oberfläche. Die vollständige Liste mit mehr als 200 Einstiegspunkten befindet sich in
`scripts/lib/plugin-sdk-entrypoints.json`.

Diese Liste enthält weiterhin einige Helper-Seams für gebündelte Plugins wie
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` und `plugin-sdk/matrix*`. Diese werden für
die Pflege gebündelter Plugins und aus Kompatibilitätsgründen weiterhin exportiert, sind aber
absichtlich nicht in der gängigen Migrationstabelle enthalten und nicht das empfohlene Ziel für
neuen Plugin-Code.

Dieselbe Regel gilt für andere Familien gebündelter Hilfsfunktionen wie:

- Browser-Support-Hilfsfunktionen: `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support`
- Matrix: `plugin-sdk/matrix*`
- LINE: `plugin-sdk/line*`
- IRC: `plugin-sdk/irc*`
- gebündelte Helper-/Plugin-Oberflächen wie `plugin-sdk/googlechat`,
  `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles*`,
  `plugin-sdk/mattermost*`, `plugin-sdk/msteams`,
  `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`,
  `plugin-sdk/twitch`,
  `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`,
  `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`,
  `plugin-sdk/thread-ownership` und `plugin-sdk/voice-call`

`plugin-sdk/github-copilot-token` stellt derzeit die schmale
Token-Hilfsoberfläche `DEFAULT_COPILOT_API_BASE_URL`,
`deriveCopilotApiBaseUrlFromToken` und `resolveCopilotApiToken` bereit.

Verwenden Sie den schmalsten Import, der zur Aufgabe passt. Wenn Sie keinen Export finden können,
prüfen Sie den Quellcode unter `src/plugin-sdk/` oder fragen Sie in Discord.

## Zeitplan für die Entfernung

| Wann | Was passiert |
| --- | --- |
| **Jetzt** | Veraltete Oberflächen geben Laufzeitwarnungen aus |
| **Nächste Hauptversion** | Veraltete Oberflächen werden entfernt; Plugins, die sie noch verwenden, schlagen fehl |

Alle Core-Plugins wurden bereits migriert. Externe Plugins sollten vor der nächsten Hauptversion
migrieren.

## Warnungen vorübergehend unterdrücken

Setzen Sie diese Umgebungsvariablen, während Sie an der Migration arbeiten:

```bash
OPENCLAW_SUPPRESS_PLUGIN_SDK_COMPAT_WARNING=1 openclaw gateway run
OPENCLAW_SUPPRESS_EXTENSION_API_WARNING=1 openclaw gateway run
```

Dies ist ein vorübergehender Ausweg, keine dauerhafte Lösung.

## Verwandt

- [Erste Schritte](/de/plugins/building-plugins) — Ihr erstes Plugin erstellen
- [SDK-Übersicht](/de/plugins/sdk-overview) — vollständige Referenz zu Unterpfad-Imports
- [Kanal-Plugins](/de/plugins/sdk-channel-plugins) — Kanal-Plugins erstellen
- [Provider-Plugins](/de/plugins/sdk-provider-plugins) — Provider-Plugins erstellen
- [Plugin-Interna](/de/plugins/architecture) — tiefer Einblick in die Architektur
- [Plugin-Manifest](/de/plugins/manifest) — Referenz zum Manifest-Schema
