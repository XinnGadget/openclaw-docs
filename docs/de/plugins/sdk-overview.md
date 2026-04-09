---
read_when:
    - Sie müssen wissen, aus welchem SDK-Subpath Sie importieren sollen
    - Sie möchten eine Referenz für alle Registrierungsmethoden auf OpenClawPluginApi
    - Sie suchen einen bestimmten SDK-Export nach
sidebarTitle: SDK Overview
summary: Referenz zur Import-Zuordnung, Registrierungs-API und SDK-Architektur
title: Plugin SDK Überblick
x-i18n:
    generated_at: "2026-04-09T01:31:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: bf205af060971931df97dca4af5110ce173d2b7c12f56ad7c62d664a402f2381
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# Plugin SDK Überblick

Das Plugin SDK ist der typisierte Vertrag zwischen Plugins und dem Kern. Diese Seite ist die
Referenz für **was importiert werden soll** und **was registriert werden kann**.

<Tip>
  **Suchen Sie eine Schritt-für-Schritt-Anleitung?**
  - Erstes Plugin? Beginnen Sie mit [Getting Started](/de/plugins/building-plugins)
  - Channel-Plugin? Siehe [Channel Plugins](/de/plugins/sdk-channel-plugins)
  - Anbieter-Plugin? Siehe [Provider Plugins](/de/plugins/sdk-provider-plugins)
</Tip>

## Importkonvention

Importieren Sie immer aus einem bestimmten Subpath:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

Jeder Subpath ist ein kleines, in sich geschlossenes Modul. Das hält den Start schnell und
verhindert Probleme mit zirkulären Abhängigkeiten. Für Channel-spezifische Entry-/Build-Helfer
bevorzugen Sie `openclaw/plugin-sdk/channel-core`; verwenden Sie `openclaw/plugin-sdk/core` für
die breitere Dachoberfläche und gemeinsame Hilfsfunktionen wie
`buildChannelConfigSchema`.

Fügen Sie keine nach Anbietern benannten Convenience-Seams hinzu und hängen Sie nicht von solchen ab, wie
`openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp` oder
Channel-markenspezifischen Helper-Seams. Gebündelte Plugins sollten generische
SDK-Subpaths in ihren eigenen `api.ts`- oder `runtime-api.ts`-Barrels zusammensetzen, und der Kern
sollte entweder diese pluginlokalen Barrels verwenden oder einen schmalen generischen SDK-
Vertrag hinzufügen, wenn der Bedarf wirklich kanalübergreifend ist.

Die generierte Export-Zuordnung enthält weiterhin eine kleine Menge gebündelter Plugin-Helper-
Seams wie `plugin-sdk/feishu`, `plugin-sdk/feishu-setup`,
`plugin-sdk/zalo`, `plugin-sdk/zalo-setup` und `plugin-sdk/matrix*`. Diese
Subpaths existieren nur für die Wartung und Kompatibilität gebündelter Plugins; sie werden
absichtlich aus der allgemeinen Tabelle unten ausgelassen und sind nicht der empfohlene
Importpfad für neue Drittanbieter-Plugins.

## Subpath-Referenz

Die am häufigsten verwendeten Subpaths, nach Zweck gruppiert. Die generierte vollständige Liste mit
mehr als 200 Subpaths befindet sich in `scripts/lib/plugin-sdk-entrypoints.json`.

Reservierte gebündelte Plugin-Helper-Subpaths erscheinen weiterhin in dieser generierten Liste.
Behandeln Sie diese als Implementierungsdetail-/Kompatibilitätsoberflächen, sofern nicht eine Dokumentationsseite
sie ausdrücklich als öffentlich hervorhebt.

### Plugin-Einstiegspunkt

| Subpath                     | Wichtige Exporte                                                                                                                     |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `plugin-sdk/plugin-entry`   | `definePluginEntry`                                                                                                                  |
| `plugin-sdk/core`           | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema`  | `OpenClawSchema`                                                                                                                     |
| `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry`                                                                                                    |

<AccordionGroup>
  <Accordion title="Channel-Subpaths">
    | Subpath | Wichtige Exporte |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | Zod-Schema-Export für das Root-`openclaw.json` (`OpenClawSchema`) |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard` sowie `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | Gemeinsame Hilfsfunktionen für Einrichtungsassistenten, Allowlist-Aufforderungen, Builder für Einrichtungsstatus |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | Hilfsfunktionen für Mehrkonten-Konfiguration/Aktions-Gating, Hilfen für Standardkonto-Fallback |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`, Hilfsfunktionen zur Normalisierung von Konto-IDs |
    | `plugin-sdk/account-resolution` | Kontosuche + Hilfen für Standard-Fallback |
    | `plugin-sdk/account-helpers` | Schmale Hilfsfunktionen für Kontolisten/Kontoaktionen |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | Typen für Channel-Konfigurationsschemata |
    | `plugin-sdk/telegram-command-config` | Hilfsfunktionen zur Normalisierung/Validierung benutzerdefinierter Telegram-Befehle mit Fallback für gebündelte Verträge |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | Gemeinsame Hilfsfunktionen für eingehende Routen und Envelope-Builder |
    | `plugin-sdk/inbound-reply-dispatch` | Gemeinsame Hilfsfunktionen zum Aufzeichnen und Verteilen eingehender Nachrichten |
    | `plugin-sdk/messaging-targets` | Hilfsfunktionen zum Parsen/Abgleichen von Zielen |
    | `plugin-sdk/outbound-media` | Gemeinsame Hilfsfunktionen zum Laden ausgehender Medien |
    | `plugin-sdk/outbound-runtime` | Hilfsfunktionen für ausgehende Identitäten/Sende-Delegates |
    | `plugin-sdk/thread-bindings-runtime` | Hilfsfunktionen für Lebenszyklus und Adapter von Thread-Bindungen |
    | `plugin-sdk/agent-media-payload` | Legacy-Builder für Agent-Medien-Payloads |
    | `plugin-sdk/conversation-runtime` | Hilfsfunktionen für Konversations-/Thread-Bindung, Pairing und konfigurierte Bindungen |
    | `plugin-sdk/runtime-config-snapshot` | Hilfsfunktion für Laufzeit-Konfigurations-Snapshots |
    | `plugin-sdk/runtime-group-policy` | Hilfsfunktionen zur Auflösung von Laufzeit-Gruppenrichtlinien |
    | `plugin-sdk/channel-status` | Gemeinsame Hilfsfunktionen für Snapshots/Zusammenfassungen des Channel-Status |
    | `plugin-sdk/channel-config-primitives` | Schmale Primitive für Channel-Konfigurationsschemata |
    | `plugin-sdk/channel-config-writes` | Hilfsfunktionen zur Autorisierung von Channel-Konfigurationsschreibvorgängen |
    | `plugin-sdk/channel-plugin-common` | Gemeinsame Prelude-Exporte für Channel-Plugins |
    | `plugin-sdk/allowlist-config-edit` | Hilfsfunktionen zum Bearbeiten/Lesen der Allowlist-Konfiguration |
    | `plugin-sdk/group-access` | Gemeinsame Hilfsfunktionen für Entscheidungen über Gruppenzugriff |
    | `plugin-sdk/direct-dm` | Gemeinsame Hilfsfunktionen für Auth/Schutz bei Direktnachrichten |
    | `plugin-sdk/interactive-runtime` | Hilfsfunktionen zur Normalisierung/Reduktion interaktiver Antwort-Payloads |
    | `plugin-sdk/channel-inbound` | Hilfsfunktionen für eingehendes Debouncing, Mention-Abgleich, Mention-Richtlinien und Envelopes |
    | `plugin-sdk/channel-send-result` | Typen für Antwortergebnisse |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | Hilfsfunktionen zum Parsen/Abgleichen von Zielen |
    | `plugin-sdk/channel-contract` | Typen für Channel-Verträge |
    | `plugin-sdk/channel-feedback` | Verdrahtung für Feedback/Reaktionen |
    | `plugin-sdk/channel-secret-runtime` | Schmale Hilfsfunktionen für Secret-Verträge wie `collectSimpleChannelFieldAssignments`, `getChannelSurface`, `pushAssignment` sowie Secret-Zieltypen |
  </Accordion>

  <Accordion title="Anbieter-Subpaths">
    | Subpath | Wichtige Exporte |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | Kuratierte Hilfsfunktionen für die Einrichtung lokaler/selbst gehosteter Anbieter |
    | `plugin-sdk/self-hosted-provider-setup` | Fokussierte Hilfsfunktionen für die Einrichtung selbst gehosteter OpenAI-kompatibler Anbieter |
    | `plugin-sdk/cli-backend` | CLI-Backend-Standardwerte + Watchdog-Konstanten |
    | `plugin-sdk/provider-auth-runtime` | Hilfsfunktionen zur Laufzeit-Auflösung von API-Schlüsseln für Anbieter-Plugins |
    | `plugin-sdk/provider-auth-api-key` | Hilfsfunktionen für API-Schlüssel-Onboarding/Profilschreibvorgänge wie `upsertApiKeyProfile` |
    | `plugin-sdk/provider-auth-result` | Standard-Builder für OAuth-Authentifizierungsergebnisse |
    | `plugin-sdk/provider-auth-login` | Gemeinsame interaktive Login-Hilfsfunktionen für Anbieter-Plugins |
    | `plugin-sdk/provider-env-vars` | Hilfsfunktionen zur Suche von Auth-Umgebungsvariablen für Anbieter |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile`, `upsertApiKeyProfile`, `writeOAuthCredentials` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, gemeinsame Builder für Replay-Richtlinien, Hilfsfunktionen für Anbieter-Endpunkte und Hilfsfunktionen zur Modell-ID-Normalisierung wie `normalizeNativeXaiModelId` |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | Generische Hilfsfunktionen für HTTP-/Endpoint-Fähigkeiten von Anbietern |
    | `plugin-sdk/provider-web-fetch-contract` | Schmale Hilfsfunktionen für Web-Fetch-Konfigurations-/Auswahlverträge wie `enablePluginInConfig` und `WebFetchProviderPlugin` |
    | `plugin-sdk/provider-web-fetch` | Hilfsfunktionen für Registrierung/Cache von Web-Fetch-Anbietern |
    | `plugin-sdk/provider-web-search-config-contract` | Schmale Hilfsfunktionen für Websuche-Konfiguration/Berechtigungen für Anbieter, die keine Plugin-Aktivierungsverdrahtung benötigen |
    | `plugin-sdk/provider-web-search-contract` | Schmale Hilfsfunktionen für Websuche-Konfigurations-/Berechtigungsverträge wie `createWebSearchProviderContractFields`, `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig` und bereichsspezifische Setter/Getter für Berechtigungen |
    | `plugin-sdk/provider-web-search` | Hilfsfunktionen für Registrierung/Cache/Laufzeit von Websuche-Anbietern |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, Bereinigung + Diagnose für Gemini-Schemas und xAI-Kompatibilitätshelfer wie `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` und Ähnliches |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, Stream-Wrapper-Typen und gemeinsame Wrapper-Helfer für Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
    | `plugin-sdk/provider-onboard` | Hilfsfunktionen zum Patchen der Onboarding-Konfiguration |
    | `plugin-sdk/global-singleton` | Hilfsfunktionen für prozesslokale Singletons/Maps/Caches |
  </Accordion>

  <Accordion title="Auth- und Sicherheits-Subpaths">
    | Subpath | Wichtige Exporte |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`, Hilfsfunktionen für Befehlsregister, Hilfsfunktionen für Absenderautorisierung |
    | `plugin-sdk/command-status` | Builder für Befehls-/Hilfemeldungen wie `buildCommandsMessagePaginated` und `buildHelpMessage` |
    | `plugin-sdk/approval-auth-runtime` | Hilfsfunktionen für Auflöser von Genehmigern und gleiche-Chat-Aktionsauthentifizierung |
    | `plugin-sdk/approval-client-runtime` | Hilfsfunktionen für Profile/Filter der nativen Ausführungsfreigabe |
    | `plugin-sdk/approval-delivery-runtime` | Adapter für native Genehmigungsfunktionen/-auslieferung |
    | `plugin-sdk/approval-gateway-runtime` | Gemeinsame Hilfsfunktion zur Auflösung des Genehmigungs-Gateways |
    | `plugin-sdk/approval-handler-adapter-runtime` | Leichtgewichtige Hilfsfunktionen zum Laden nativer Genehmigungsadapter für schnelle Channel-Einstiegspunkte |
    | `plugin-sdk/approval-handler-runtime` | Breitere Laufzeit-Hilfsfunktionen für Genehmigungshandler; bevorzugen Sie die schmaleren Adapter-/Gateway-Seams, wenn sie ausreichen |
    | `plugin-sdk/approval-native-runtime` | Hilfsfunktionen für native Genehmigungsziele und Konto-Bindungen |
    | `plugin-sdk/approval-reply-runtime` | Hilfsfunktionen für Antwort-Payloads von Exec-/Plugin-Genehmigungen |
    | `plugin-sdk/command-auth-native` | Native Befehlsauthentifizierung + Hilfsfunktionen für native Sitzungsziele |
    | `plugin-sdk/command-detection` | Gemeinsame Hilfsfunktionen zur Befehlserkennung |
    | `plugin-sdk/command-surface` | Hilfsfunktionen zur Normalisierung von Befehlsinhalten und Befehlsoberflächen |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/channel-secret-runtime` | Schmale Hilfsfunktionen zur Sammlung von Secret-Verträgen für Secret-Oberflächen von Channels/Plugins |
    | `plugin-sdk/secret-ref-runtime` | Schmale Hilfsfunktionen für `coerceSecretRef` und SecretRef-Typisierung für Secret-Vertrags-/Konfigurations-Parsing |
    | `plugin-sdk/security-runtime` | Gemeinsame Hilfsfunktionen für Vertrauen, DM-Gating, externe Inhalte und Secret-Sammlung |
    | `plugin-sdk/ssrf-policy` | Hilfsfunktionen für Host-Allowlist und SSRF-Richtlinien für private Netzwerke |
    | `plugin-sdk/ssrf-runtime` | Hilfsfunktionen für angeheftete Dispatcher, SSRF-geschütztes Fetch und SSRF-Richtlinien |
    | `plugin-sdk/secret-input` | Hilfsfunktionen zum Parsen von Secret-Eingaben |
    | `plugin-sdk/webhook-ingress` | Hilfsfunktionen für Webhook-Anfragen/-Ziele |
    | `plugin-sdk/webhook-request-guards` | Hilfsfunktionen für Größe/Timeout von Request-Bodys |
  </Accordion>

  <Accordion title="Laufzeit- und Speicher-Subpaths">
    | Subpath | Wichtige Exporte |
    | --- | --- |
    | `plugin-sdk/runtime` | Breite Hilfsfunktionen für Laufzeit/Logging/Backups/Plugin-Installation |
    | `plugin-sdk/runtime-env` | Schmale Hilfsfunktionen für Laufzeitumgebung, Logger, Timeout, Retry und Backoff |
    | `plugin-sdk/channel-runtime-context` | Generische Hilfsfunktionen für Registrierung und Lookup von Channel-Laufzeitkontexten |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | Gemeinsame Hilfsfunktionen für Plugin-Befehle/Hooks/HTTP/Interaktivität |
    | `plugin-sdk/hook-runtime` | Gemeinsame Hilfsfunktionen für Webhook-/interne Hook-Pipelines |
    | `plugin-sdk/lazy-runtime` | Hilfsfunktionen für lazy Laufzeitimporte/-bindungen wie `createLazyRuntimeModule`, `createLazyRuntimeMethod` und `createLazyRuntimeSurface` |
    | `plugin-sdk/process-runtime` | Hilfsfunktionen für Prozessausführung |
    | `plugin-sdk/cli-runtime` | Hilfsfunktionen für CLI-Formatierung, Warten und Version |
    | `plugin-sdk/gateway-runtime` | Hilfsfunktionen für Gateway-Client und Channel-Status-Patches |
    | `plugin-sdk/config-runtime` | Hilfsfunktionen zum Laden/Schreiben von Konfiguration |
    | `plugin-sdk/telegram-command-config` | Normalisierung von Telegram-Befehlsnamen/-beschreibungen und Prüfungen auf Duplikate/Konflikte, auch wenn die gebündelte Telegram-Vertragsoberfläche nicht verfügbar ist |
    | `plugin-sdk/approval-runtime` | Hilfsfunktionen für Exec-/Plugin-Genehmigungen, Builder für Genehmigungsfähigkeiten, Hilfsfunktionen für Auth/Profile sowie native Routing-/Laufzeit-Helfer |
    | `plugin-sdk/reply-runtime` | Gemeinsame Laufzeit-Hilfsfunktionen für eingehende Nachrichten/Antworten, Chunking, Dispatch, Heartbeat, Antwortplanung |
    | `plugin-sdk/reply-dispatch-runtime` | Schmale Hilfsfunktionen für Dispatch/Abschluss von Antworten |
    | `plugin-sdk/reply-history` | Gemeinsame Hilfsfunktionen für den Antwortverlauf in kurzen Fenstern wie `buildHistoryContext`, `recordPendingHistoryEntry` und `clearHistoryEntriesIfEnabled` |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | Schmale Hilfsfunktionen für Text-/Markdown-Chunking |
    | `plugin-sdk/session-store-runtime` | Hilfsfunktionen für Pfade des Session-Stores und `updated-at` |
    | `plugin-sdk/state-paths` | Hilfsfunktionen für State-/OAuth-Verzeichnispfade |
    | `plugin-sdk/routing` | Hilfsfunktionen für Route/Session-Key/Konto-Bindung wie `resolveAgentRoute`, `buildAgentSessionKey` und `resolveDefaultAgentBoundAccountId` |
    | `plugin-sdk/status-helpers` | Gemeinsame Hilfsfunktionen für Zusammenfassungen des Channel-/Kontostatus, Standardwerte für Laufzeitzustände und Metadaten von Problemen |
    | `plugin-sdk/target-resolver-runtime` | Gemeinsame Hilfsfunktionen für Zielauflöser |
    | `plugin-sdk/string-normalization-runtime` | Hilfsfunktionen zur Slug-/String-Normalisierung |
    | `plugin-sdk/request-url` | Extrahieren von String-URLs aus fetch-/request-ähnlichen Eingaben |
    | `plugin-sdk/run-command` | Zeitgesteuerter Befehlsrunner mit normalisierten stdout-/stderr-Ergebnissen |
    | `plugin-sdk/param-readers` | Gemeinsame Leser für Tool-/CLI-Parameter |
    | `plugin-sdk/tool-payload` | Extrahieren normalisierter Payloads aus Tool-Ergebnisobjekten |
    | `plugin-sdk/tool-send` | Extrahieren kanonischer Sendefelder aus Tool-Argumenten |
    | `plugin-sdk/temp-path` | Gemeinsame Hilfsfunktionen für temporäre Download-Pfade |
    | `plugin-sdk/logging-core` | Hilfsfunktionen für Subsystem-Logger und Redaction |
    | `plugin-sdk/markdown-table-runtime` | Hilfsfunktionen für Modi von Markdown-Tabellen |
    | `plugin-sdk/json-store` | Kleine Hilfsfunktionen zum Lesen/Schreiben von JSON-Status |
    | `plugin-sdk/file-lock` | Reentrant-Hilfsfunktionen für Dateisperren |
    | `plugin-sdk/persistent-dedupe` | Hilfsfunktionen für festplattenbasierten Dedupe-Cache |
    | `plugin-sdk/acp-runtime` | Hilfsfunktionen für ACP-Laufzeit/Sitzungen und Reply-Dispatch |
    | `plugin-sdk/agent-config-primitives` | Schmale Primitive für Agent-Laufzeit-Konfigurationsschemata |
    | `plugin-sdk/boolean-param` | Nachsichtiger Leser für boolesche Parameter |
    | `plugin-sdk/dangerous-name-runtime` | Hilfsfunktionen zur Auflösung von Treffern bei gefährlichen Namen |
    | `plugin-sdk/device-bootstrap` | Hilfsfunktionen für Device-Bootstrap und Pairing-Token |
    | `plugin-sdk/extension-shared` | Gemeinsame Primitive für passive Channels, Status und Ambient-Proxy-Helfer |
    | `plugin-sdk/models-provider-runtime` | Hilfsfunktionen für Antworten von `/models`-Befehlen/Anbietern |
    | `plugin-sdk/skill-commands-runtime` | Hilfsfunktionen zum Auflisten von Skill-Befehlen |
    | `plugin-sdk/native-command-registry` | Hilfsfunktionen für Register/Build/Serialisierung nativer Befehle |
    | `plugin-sdk/provider-zai-endpoint` | Hilfsfunktionen zur Erkennung von Z.AI-Endpunkten |
    | `plugin-sdk/infra-runtime` | Hilfsfunktionen für Systemereignisse/Heartbeat |
    | `plugin-sdk/collection-runtime` | Kleine Hilfsfunktionen für begrenzte Caches |
    | `plugin-sdk/diagnostic-runtime` | Hilfsfunktionen für Diagnose-Flags und -Ereignisse |
    | `plugin-sdk/error-runtime` | Fehlergraph, Formatierung, gemeinsame Hilfsfunktionen zur Fehlerklassifizierung, `isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | Hilfsfunktionen für umhülltes Fetch, Proxy und angeheftetes Lookup |
    | `plugin-sdk/host-runtime` | Hilfsfunktionen zur Normalisierung von Hostnamen und SCP-Hosts |
    | `plugin-sdk/retry-runtime` | Hilfsfunktionen für Retry-Konfiguration und Retry-Runner |
    | `plugin-sdk/agent-runtime` | Hilfsfunktionen für Agent-Verzeichnis/Identität/Workspace |
    | `plugin-sdk/directory-runtime` | Konfigurationsgestützte Verzeichnisabfrage/Deduplizierung |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="Fähigkeits- und Test-Subpaths">
    | Subpath | Wichtige Exporte |
    | --- | --- |
    | `plugin-sdk/media-runtime` | Gemeinsame Hilfsfunktionen zum Abrufen/Transformieren/Speichern von Medien plus Builder für Medien-Payloads |
    | `plugin-sdk/media-generation-runtime` | Gemeinsame Hilfsfunktionen für Failover bei Mediengenerierung, Kandidatenauswahl und Meldungen bei fehlenden Modellen |
    | `plugin-sdk/media-understanding` | Typen für Media-Understanding-Anbieter plus anbieterseitige Exporte von Bild-/Audio-Hilfsfunktionen |
    | `plugin-sdk/text-runtime` | Gemeinsame Hilfsfunktionen für Text/Markdown/Logging wie das Entfernen von für Assistenten sichtbarem Text, Hilfen zum Rendern/Chunking von Markdown/Tabellen, Redaction-Helfer, Directive-Tag-Helfer und Safe-Text-Dienstprogramme |
    | `plugin-sdk/text-chunking` | Hilfsfunktion für ausgehendes Text-Chunking |
    | `plugin-sdk/speech` | Typen für Speech-Anbieter plus anbieterseitige Hilfsfunktionen für Direktiven, Register und Validierung |
    | `plugin-sdk/speech-core` | Gemeinsame Typen für Speech-Anbieter, Register-, Direktiven- und Normalisierungshilfen |
    | `plugin-sdk/realtime-transcription` | Typen für Realtime-Transcription-Anbieter und Register-Hilfen |
    | `plugin-sdk/realtime-voice` | Typen für Realtime-Voice-Anbieter und Register-Hilfen |
    | `plugin-sdk/image-generation` | Typen für Bildgenerierungsanbieter |
    | `plugin-sdk/image-generation-core` | Gemeinsame Typen und Hilfsfunktionen für Bildgenerierung, Failover, Auth und Register |
    | `plugin-sdk/music-generation` | Typen für Anbieter/Anfragen/Ergebnisse bei Musikgenerierung |
    | `plugin-sdk/music-generation-core` | Gemeinsame Typen und Hilfsfunktionen für Musikgenerierung, Failover, Anbieter-Lookup und Parsing von Modellreferenzen |
    | `plugin-sdk/video-generation` | Typen für Anbieter/Anfragen/Ergebnisse bei Videogenerierung |
    | `plugin-sdk/video-generation-core` | Gemeinsame Typen und Hilfsfunktionen für Videogenerierung, Failover, Anbieter-Lookup und Parsing von Modellreferenzen |
    | `plugin-sdk/webhook-targets` | Register für Webhook-Ziele und Hilfsfunktionen zur Routeninstallation |
    | `plugin-sdk/webhook-path` | Hilfsfunktionen zur Normalisierung von Webhook-Pfaden |
    | `plugin-sdk/web-media` | Gemeinsame Hilfsfunktionen zum Laden entfernter/lokaler Medien |
    | `plugin-sdk/zod` | Re-exportiertes `zod` für Plugin-SDK-Nutzer |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="Memory-Subpaths">
    | Subpath | Wichtige Exporte |
    | --- | --- |
    | `plugin-sdk/memory-core` | Gebündelte Hilfsoberfläche von memory-core für Manager-/Konfigurations-/Datei-/CLI-Hilfsfunktionen |
    | `plugin-sdk/memory-core-engine-runtime` | Laufzeit-Fassade für Memory-Index/Suche |
    | `plugin-sdk/memory-core-host-engine-foundation` | Exporte der Foundation-Engine des Memory-Hosts |
    | `plugin-sdk/memory-core-host-engine-embeddings` | Exporte der Embedding-Engine des Memory-Hosts |
    | `plugin-sdk/memory-core-host-engine-qmd` | Exporte der QMD-Engine des Memory-Hosts |
    | `plugin-sdk/memory-core-host-engine-storage` | Exporte der Storage-Engine des Memory-Hosts |
    | `plugin-sdk/memory-core-host-multimodal` | Multimodale Hilfsfunktionen des Memory-Hosts |
    | `plugin-sdk/memory-core-host-query` | Query-Hilfsfunktionen des Memory-Hosts |
    | `plugin-sdk/memory-core-host-secret` | Secret-Hilfsfunktionen des Memory-Hosts |
    | `plugin-sdk/memory-core-host-events` | Hilfsfunktionen für Event-Journale des Memory-Hosts |
    | `plugin-sdk/memory-core-host-status` | Status-Hilfsfunktionen des Memory-Hosts |
    | `plugin-sdk/memory-core-host-runtime-cli` | CLI-Laufzeit-Hilfsfunktionen des Memory-Hosts |
    | `plugin-sdk/memory-core-host-runtime-core` | Kern-Laufzeit-Hilfsfunktionen des Memory-Hosts |
    | `plugin-sdk/memory-core-host-runtime-files` | Datei-/Laufzeit-Hilfsfunktionen des Memory-Hosts |
    | `plugin-sdk/memory-host-core` | Herstellerneutraler Alias für Kern-Laufzeit-Hilfsfunktionen des Memory-Hosts |
    | `plugin-sdk/memory-host-events` | Herstellerneutraler Alias für Event-Journal-Hilfsfunktionen des Memory-Hosts |
    | `plugin-sdk/memory-host-files` | Herstellerneutraler Alias für Datei-/Laufzeit-Hilfsfunktionen des Memory-Hosts |
    | `plugin-sdk/memory-host-markdown` | Gemeinsame Hilfsfunktionen für verwaltetes Markdown für Memory-nahe Plugins |
    | `plugin-sdk/memory-host-search` | Aktive Memory-Laufzeit-Fassade für den Zugriff auf Search-Manager |
    | `plugin-sdk/memory-host-status` | Herstellerneutraler Alias für Status-Hilfsfunktionen des Memory-Hosts |
    | `plugin-sdk/memory-lancedb` | Gebündelte Hilfsoberfläche von memory-lancedb |
  </Accordion>

  <Accordion title="Reservierte gebündelte Helper-Subpaths">
    | Familie | Aktuelle Subpaths | Verwendungszweck |
    | --- | --- | --- |
    | Browser | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | Unterstützende Hilfsfunktionen für das gebündelte Browser-Plugin (`browser-support` bleibt das Kompatibilitäts-Barrel) |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | Gebündelte Matrix-Helper-/Laufzeitoberfläche |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | Gebündelte LINE-Helper-/Laufzeitoberfläche |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | Gebündelte IRC-Helper-Oberfläche |
    | Channel-spezifische Hilfsfunktionen | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | Gebündelte Channel-Kompatibilitäts-/Helper-Seams |
    | Auth-/plugin-spezifische Hilfsfunktionen | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | Gebündelte Funktions-/Plugin-Helper-Seams; `plugin-sdk/github-copilot-token` exportiert derzeit `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken` und `resolveCopilotApiToken` |
  </Accordion>
</AccordionGroup>

## Registrierungs-API

Der Callback `register(api)` erhält ein Objekt `OpenClawPluginApi` mit diesen
Methoden:

### Fähigkeitsregistrierung

| Methode                                          | Was registriert wird            |
| ------------------------------------------------ | ------------------------------- |
| `api.registerProvider(...)`                      | Textinferenz (LLM)              |
| `api.registerCliBackend(...)`                    | Lokales CLI-Inferenz-Backend    |
| `api.registerChannel(...)`                       | Messaging-Kanal                 |
| `api.registerSpeechProvider(...)`                | Text-to-Speech / STT-Synthese   |
| `api.registerRealtimeTranscriptionProvider(...)` | Streaming-Realtime-Transkription |
| `api.registerRealtimeVoiceProvider(...)`         | Duplex-Realtime-Sprachsitzungen |
| `api.registerMediaUnderstandingProvider(...)`    | Bild-/Audio-/Videoanalyse       |
| `api.registerImageGenerationProvider(...)`       | Bildgenerierung                 |
| `api.registerMusicGenerationProvider(...)`       | Musikgenerierung                |
| `api.registerVideoGenerationProvider(...)`       | Videogenerierung                |
| `api.registerWebFetchProvider(...)`              | Web-Fetch-/Scrape-Anbieter      |
| `api.registerWebSearchProvider(...)`             | Websuche                        |

### Tools und Befehle

| Methode                         | Was registriert wird                          |
| ------------------------------- | --------------------------------------------- |
| `api.registerTool(tool, opts?)` | Agent-Tool (erforderlich oder `{ optional: true }`) |
| `api.registerCommand(def)`      | Benutzerdefinierter Befehl (umgeht das LLM)   |

### Infrastruktur

| Methode                                        | Was registriert wird                |
| ---------------------------------------------- | ----------------------------------- |
| `api.registerHook(events, handler, opts?)`     | Event-Hook                          |
| `api.registerHttpRoute(params)`                | Gateway-HTTP-Endpunkt               |
| `api.registerGatewayMethod(name, handler)`     | Gateway-RPC-Methode                 |
| `api.registerCli(registrar, opts?)`            | CLI-Unterbefehl                     |
| `api.registerService(service)`                 | Hintergrunddienst                   |
| `api.registerInteractiveHandler(registration)` | Interaktiver Handler                |
| `api.registerMemoryPromptSupplement(builder)`  | Additiver promptnaher Memory-Abschnitt |
| `api.registerMemoryCorpusSupplement(adapter)`  | Additiver Such-/Lese-Korpus für Memory |

Reservierte Admin-Namespaces des Kerns (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`) bleiben immer `operator.admin`, auch wenn ein Plugin versucht, einen
engeren Scope für Gateway-Methoden zuzuweisen. Bevorzugen Sie plugin-spezifische Präfixe für
plugin-eigene Methoden.

### CLI-Registrierungsmetadaten

`api.registerCli(registrar, opts?)` akzeptiert zwei Arten von Metadaten auf oberster Ebene:

- `commands`: explizite Befehlswurzeln, die dem Registrar gehören
- `descriptors`: Parse-Zeit-Befehlsdeskriptoren für Root-CLI-Hilfe,
  Routing und lazy CLI-Registrierung von Plugins

Wenn ein Plugin-Befehl im normalen Root-CLI-Pfad lazy geladen bleiben soll,
geben Sie `descriptors` an, die jede Befehlswurzel auf oberster Ebene abdecken, die von diesem
Registrar bereitgestellt wird.

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
        description: "Matrix-Konten, Verifizierung, Geräte und Profilstatus verwalten",
        hasSubcommands: true,
      },
    ],
  },
);
```

Verwenden Sie `commands` allein nur dann, wenn Sie keine lazy Root-CLI-Registrierung benötigen.
Dieser eager-Kompatibilitätspfad wird weiterhin unterstützt, installiert jedoch keine
deskriptorbasierten Platzhalter für lazy Laden zur Parse-Zeit.

### Registrierung von CLI-Backends

`api.registerCliBackend(...)` ermöglicht es einem Plugin, die Standardkonfiguration für ein lokales
KI-CLI-Backend wie `codex-cli` zu besitzen.

- Die `id` des Backends wird zum Anbieterpräfix in Modellreferenzen wie `codex-cli/gpt-5`.
- Die `config` des Backends verwendet dieselbe Form wie `agents.defaults.cliBackends.<id>`.
- Nutzerkonfiguration hat weiterhin Vorrang. OpenClaw führt `agents.defaults.cliBackends.<id>` über dem
  Plugin-Standard zusammen, bevor die CLI ausgeführt wird.
- Verwenden Sie `normalizeConfig`, wenn ein Backend nach dem Zusammenführen Kompatibilitätsumschreibungen
  benötigt (zum Beispiel zur Normalisierung alter Flag-Formen).

### Exklusive Slots

| Methode                                    | Was registriert wird                                                                                                                                         |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `api.registerContextEngine(id, factory)`   | Kontext-Engine (jeweils nur eine aktiv). Der Callback `assemble()` erhält `availableTools` und `citationsMode`, damit die Engine Prompt-Ergänzungen anpassen kann. |
| `api.registerMemoryCapability(capability)` | Einheitliche Memory-Fähigkeit                                                                                                                               |
| `api.registerMemoryPromptSection(builder)` | Builder für Memory-Prompt-Abschnitte                                                                                                                        |
| `api.registerMemoryFlushPlan(resolver)`    | Resolver für Memory-Flush-Pläne                                                                                                                             |
| `api.registerMemoryRuntime(runtime)`       | Laufzeitadapter für Memory                                                                                                                                    |

### Memory-Embedding-Adapter

| Methode                                        | Was registriert wird                             |
| ---------------------------------------------- | ------------------------------------------------ |
| `api.registerMemoryEmbeddingProvider(adapter)` | Memory-Embedding-Adapter für das aktive Plugin   |

- `registerMemoryCapability` ist die bevorzugte exklusive API für Memory-Plugins.
- `registerMemoryCapability` kann auch `publicArtifacts.listArtifacts(...)` bereitstellen,
  sodass Begleit-Plugins exportierte Memory-Artefakte über
  `openclaw/plugin-sdk/memory-host-core` nutzen können, anstatt in ein bestimmtes
  privates Layout eines Memory-Plugins zu greifen.
- `registerMemoryPromptSection`, `registerMemoryFlushPlan` und
  `registerMemoryRuntime` sind Legacy-kompatible exklusive APIs für Memory-Plugins.
- `registerMemoryEmbeddingProvider` erlaubt es dem aktiven Memory-Plugin, einen
  oder mehrere Embedding-Adapter-IDs zu registrieren (zum Beispiel `openai`, `gemini` oder eine benutzerdefinierte plugin-definierte ID).
- Nutzerkonfiguration wie `agents.defaults.memorySearch.provider` und
  `agents.defaults.memorySearch.fallback` wird gegen diese registrierten
  Adapter-IDs aufgelöst.

### Ereignisse und Lebenszyklus

| Methode                                      | Was sie tut                  |
| -------------------------------------------- | ---------------------------- |
| `api.on(hookName, handler, opts?)`           | Typisierter Lebenszyklus-Hook |
| `api.onConversationBindingResolved(handler)` | Callback für aufgelöste Konversationsbindung |

### Entscheidungssemantik von Hooks

- `before_tool_call`: Die Rückgabe von `{ block: true }` ist endgültig. Sobald ein Handler dies setzt, werden Handler mit niedrigerer Priorität übersprungen.
- `before_tool_call`: Die Rückgabe von `{ block: false }` wird als keine Entscheidung behandelt (wie das Weglassen von `block`), nicht als Überschreibung.
- `before_install`: Die Rückgabe von `{ block: true }` ist endgültig. Sobald ein Handler dies setzt, werden Handler mit niedrigerer Priorität übersprungen.
- `before_install`: Die Rückgabe von `{ block: false }` wird als keine Entscheidung behandelt (wie das Weglassen von `block`), nicht als Überschreibung.
- `reply_dispatch`: Die Rückgabe von `{ handled: true, ... }` ist endgültig. Sobald ein Handler den Dispatch beansprucht, werden Handler mit niedrigerer Priorität und der Standardpfad für den Modelldispatch übersprungen.
- `message_sending`: Die Rückgabe von `{ cancel: true }` ist endgültig. Sobald ein Handler dies setzt, werden Handler mit niedrigerer Priorität übersprungen.
- `message_sending`: Die Rückgabe von `{ cancel: false }` wird als keine Entscheidung behandelt (wie das Weglassen von `cancel`), nicht als Überschreibung.

### API-Objektfelder

| Feld                     | Typ                        | Beschreibung                                                                                  |
| ------------------------ | -------------------------- | --------------------------------------------------------------------------------------------- |
| `api.id`                 | `string`                   | Plugin-ID                                                                                     |
| `api.name`               | `string`                   | Anzeigename                                                                                   |
| `api.version`            | `string?`                  | Plugin-Version (optional)                                                                     |
| `api.description`        | `string?`                  | Plugin-Beschreibung (optional)                                                                |
| `api.source`             | `string`                   | Quellpfad des Plugins                                                                         |
| `api.rootDir`            | `string?`                  | Root-Verzeichnis des Plugins (optional)                                                       |
| `api.config`             | `OpenClawConfig`           | Aktueller Konfigurations-Snapshot (aktiver In-Memory-Laufzeit-Snapshot, wenn verfügbar)      |
| `api.pluginConfig`       | `Record<string, unknown>`  | Plugin-spezifische Konfiguration aus `plugins.entries.<id>.config`                            |
| `api.runtime`            | `PluginRuntime`            | [Laufzeit-Hilfsfunktionen](/de/plugins/sdk-runtime)                                              |
| `api.logger`             | `PluginLogger`             | Bereichsgebundener Logger (`debug`, `info`, `warn`, `error`)                                  |
| `api.registrationMode`   | `PluginRegistrationMode`   | Aktueller Lademodus; `"setup-runtime"` ist das leichtgewichtige Start-/Einrichtungsfenster vor dem vollständigen Entry |
| `api.resolvePath(input)` | `(string) => string`       | Löst einen Pfad relativ zur Plugin-Wurzel auf                                                 |

## Konvention für interne Module

Verwenden Sie innerhalb Ihres Plugins lokale Barrel-Dateien für interne Importe:

```
my-plugin/
  api.ts            # Öffentliche Exporte für externe Konsumenten
  runtime-api.ts    # Nur interne Laufzeit-Exporte
  index.ts          # Plugin-Einstiegspunkt
  setup-entry.ts    # Leichtgewichtiger nur-für-Setup-Einstiegspunkt (optional)
```

<Warning>
  Importieren Sie Ihr eigenes Plugin niemals über `openclaw/plugin-sdk/<your-plugin>`
  aus Produktionscode. Leiten Sie interne Importe über `./api.ts` oder
  `./runtime-api.ts`. Der SDK-Pfad ist nur der externe Vertrag.
</Warning>

Öffentliche Oberflächen gebündelter Plugins mit geladener Fassade (`api.ts`, `runtime-api.ts`,
`index.ts`, `setup-entry.ts` und ähnliche öffentliche Entry-Dateien) bevorzugen jetzt den
aktiven Laufzeit-Konfigurations-Snapshot, wenn OpenClaw bereits läuft. Falls noch kein Laufzeit-
Snapshot existiert, greifen sie auf die auf dem Datenträger aufgelöste Konfigurationsdatei zurück.

Anbieter-Plugins können auch ein schmales pluginlokales Vertrags-Barrel bereitstellen, wenn ein
Helper absichtlich anbieterspezifisch ist und noch nicht in einen generischen SDK-
Subpath gehört. Aktuelles gebündeltes Beispiel: Der Anthropic-Anbieter behält seine Claude-
Stream-Helfer in seinem eigenen öffentlichen `api.ts`- / `contract-api.ts`-Seam, anstatt
Anthropic-Beta-Header- und `service_tier`-Logik in einen generischen
`plugin-sdk/*`-Vertrag zu übernehmen.

Weitere aktuelle gebündelte Beispiele:

- `@openclaw/openai-provider`: `api.ts` exportiert Anbieter-Builder,
  Hilfsfunktionen für Standardmodelle und Builder für Realtime-Anbieter
- `@openclaw/openrouter-provider`: `api.ts` exportiert den Anbieter-Builder sowie
  Hilfsfunktionen für Onboarding/Konfiguration

<Warning>
  Produktionscode von Erweiterungen sollte außerdem Importe von `openclaw/plugin-sdk/<other-plugin>`
  vermeiden. Wenn eine Hilfsfunktion wirklich gemeinsam genutzt wird, heben Sie sie in einen neutralen SDK-Subpath
  wie `openclaw/plugin-sdk/speech`, `.../provider-model-shared` oder eine andere
  fähigkeitsorientierte Oberfläche an, anstatt zwei Plugins miteinander zu koppeln.
</Warning>

## Verwandt

- [Entry Points](/de/plugins/sdk-entrypoints) — Optionen für `definePluginEntry` und `defineChannelPluginEntry`
- [Runtime Helpers](/de/plugins/sdk-runtime) — vollständige Referenz für den Namespace `api.runtime`
- [Setup and Config](/de/plugins/sdk-setup) — Paketierung, Manifeste, Konfigurationsschemata
- [Testing](/de/plugins/sdk-testing) — Testdienstprogramme und Lint-Regeln
- [SDK Migration](/de/plugins/sdk-migration) — Migration von veralteten Oberflächen
- [Plugin Internals](/de/plugins/architecture) — tiefergehende Architektur und Fähigkeitsmodell
