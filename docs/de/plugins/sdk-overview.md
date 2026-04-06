---
read_when:
    - Sie müssen wissen, aus welchem SDK-Subpath importiert werden soll
    - Sie möchten eine Referenz für alle Registrierungsmethoden in OpenClawPluginApi
    - Sie schlagen einen bestimmten SDK-Export nach
sidebarTitle: SDK Overview
summary: Import-Map, Referenz zur Registrierungs-API und SDK-Architektur
title: Überblick über das Plugin SDK
x-i18n:
    generated_at: "2026-04-06T06:22:17Z"
    model: gpt-5.4
    provider: openai
    source_hash: acd2887ef52c66b2f234858d812bb04197ecd0bfb3e4f7bf3622f8fdc765acad
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# Überblick über das Plugin SDK

Das Plugin SDK ist der typisierte Vertrag zwischen Plugins und dem Core. Diese Seite ist die
Referenz dafür, **was importiert werden soll** und **was Sie registrieren können**.

<Tip>
  **Suchen Sie nach einer Schritt-für-Schritt-Anleitung?**
  - Erstes Plugin? Beginnen Sie mit [Erste Schritte](/de/plugins/building-plugins)
  - Channel-Plugin? Siehe [Channel Plugins](/de/plugins/sdk-channel-plugins)
  - Provider-Plugin? Siehe [Provider Plugins](/de/plugins/sdk-provider-plugins)
</Tip>

## Importkonvention

Importieren Sie immer aus einem spezifischen Subpath:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

Jeder Subpath ist ein kleines, in sich geschlossenes Modul. Das hält den Start schnell und
verhindert Probleme mit zirkulären Abhängigkeiten. Für kanalbezogene Entry-/Build-Helper
bevorzugen Sie `openclaw/plugin-sdk/channel-core`; verwenden Sie `openclaw/plugin-sdk/core`
für die breitere Oberflächen-API und gemeinsam genutzte Helper wie
`buildChannelConfigSchema`.

Fügen Sie keine nach Providern benannten Convenience-Seams hinzu und machen Sie sich nicht von ihnen abhängig, wie etwa
`openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp` oder
kanalmarkenspezifischen Helper-Seams. Gebündelte Plugins sollten generische
SDK-Subpaths in ihren eigenen `api.ts`- oder `runtime-api.ts`-Barrels zusammensetzen, und der Core
sollte entweder diese pluginlokalen Barrels verwenden oder einen schmalen generischen SDK-
Vertrag hinzufügen, wenn der Bedarf wirklich kanalübergreifend ist.

Die generierte Export-Map enthält weiterhin eine kleine Gruppe von Helper-
Seams für gebündelte Plugins wie `plugin-sdk/feishu`, `plugin-sdk/feishu-setup`,
`plugin-sdk/zalo`, `plugin-sdk/zalo-setup` und `plugin-sdk/matrix*`. Diese
Subpaths existieren nur für die Wartung gebündelter Plugins und für Kompatibilität; sie werden
in der allgemeinen Tabelle unten bewusst ausgelassen und sind nicht der empfohlene
Importpfad für neue Drittanbieter-Plugins.

## Subpath-Referenz

Die am häufigsten verwendeten Subpaths, nach Zweck gruppiert. Die generierte vollständige Liste von
mehr als 200 Subpaths befindet sich in `scripts/lib/plugin-sdk-entrypoints.json`.

Reservierte Helper-Subpaths für gebündelte Plugins erscheinen weiterhin in dieser generierten Liste.
Behandeln Sie diese als Implementierungsdetail-/Kompatibilitätsoberflächen, sofern eine Dokumentationsseite
nicht ausdrücklich einen davon als öffentlich hervorhebt.

### Plugin-Einstiegspunkt

| Subpath                     | Wichtige Exporte                                                                                                                      |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/plugin-entry`   | `definePluginEntry`                                                                                                                    |
| `plugin-sdk/core`           | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema`  | `OpenClawSchema`                                                                                                                       |
| `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry`                                                                                                      |

<AccordionGroup>
  <Accordion title="Channel-Subpaths">
    | Subpath | Wichtige Exporte |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | Root-`openclaw.json`-Zod-Schema-Export (`OpenClawSchema`) |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, sowie `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | Gemeinsam genutzte Setup-Wizard-Helper, Allowlist-Prompts, Builder für Setup-Status |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | Helper für Multi-Account-Konfigurations-/Action-Gates, Helper für den Fallback auf Standardkonten |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`, Normalisierungs-Helper für Konto-IDs |
    | `plugin-sdk/account-resolution` | Konto-Lookup plus Helper für Standard-Fallback |
    | `plugin-sdk/account-helpers` | Schmale Helper für Kontolisten-/Kontoaktionen |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | Typen für Channel-Konfigurationsschemas |
    | `plugin-sdk/telegram-command-config` | Normalisierungs-/Validierungs-Helper für benutzerdefinierte Telegram-Befehle mit Fallback für gebündelte Verträge |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | Gemeinsam genutzte Helper für Inbound-Routen und Envelope-Builder |
    | `plugin-sdk/inbound-reply-dispatch` | Gemeinsam genutzte Helper zum Aufzeichnen und Weiterleiten eingehender Daten |
    | `plugin-sdk/messaging-targets` | Helper zum Parsen/Abgleichen von Zielen |
    | `plugin-sdk/outbound-media` | Gemeinsam genutzte Helper zum Laden ausgehender Medien |
    | `plugin-sdk/outbound-runtime` | Helper für ausgehende Identität/Sende-Delegation |
    | `plugin-sdk/thread-bindings-runtime` | Lifecycle- und Adapter-Helper für Thread-Bindings |
    | `plugin-sdk/agent-media-payload` | Legacy-Builder für Agent-Medien-Payloads |
    | `plugin-sdk/conversation-runtime` | Konversations-/Thread-Binding-, Pairing- und konfigurierte Binding-Helper |
    | `plugin-sdk/runtime-config-snapshot` | Helper für Runtime-Konfigurations-Snapshots |
    | `plugin-sdk/runtime-group-policy` | Helper zur Auflösung von Runtime-Gruppenrichtlinien |
    | `plugin-sdk/channel-status` | Gemeinsam genutzte Helper für Snapshots/Zusammenfassungen des Channel-Status |
    | `plugin-sdk/channel-config-primitives` | Schmale Primitive für Channel-Konfigurationsschemas |
    | `plugin-sdk/channel-config-writes` | Autorisierungs-Helper für Schreibvorgänge in Channel-Konfigurationen |
    | `plugin-sdk/channel-plugin-common` | Gemeinsam genutzte Prelude-Exporte für Channel-Plugins |
    | `plugin-sdk/allowlist-config-edit` | Helper zum Bearbeiten/Lesen von Allowlist-Konfigurationen |
    | `plugin-sdk/group-access` | Gemeinsam genutzte Entscheidungs-Helper für Gruppenzugriff |
    | `plugin-sdk/direct-dm` | Gemeinsam genutzte Auth-/Guard-Helper für direkte DMs |
    | `plugin-sdk/interactive-runtime` | Helper zur Normalisierung/Reduktion interaktiver Antwort-Payloads |
    | `plugin-sdk/channel-inbound` | Debounce-, Mention-Matching- und Envelope-Helper |
    | `plugin-sdk/channel-send-result` | Typen für Antwortergebnisse |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | Helper zum Parsen/Abgleichen von Zielen |
    | `plugin-sdk/channel-contract` | Typen für Channel-Verträge |
    | `plugin-sdk/channel-feedback` | Verdrahtung von Feedback/Reaktionen |
  </Accordion>

  <Accordion title="Provider-Subpaths">
    | Subpath | Wichtige Exporte |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | Kuratierte Setup-Helper für lokale/selbstgehostete Provider |
    | `plugin-sdk/self-hosted-provider-setup` | Fokussierte Setup-Helper für selbstgehostete OpenAI-kompatible Provider |
    | `plugin-sdk/provider-auth-runtime` | Runtime-Helper zur Auflösung von API-Schlüsseln für Provider-Plugins |
    | `plugin-sdk/provider-auth-api-key` | Helper für API-Key-Onboarding/Profilschreibvorgänge |
    | `plugin-sdk/provider-auth-result` | Standard-Builder für OAuth-Authentifizierungsergebnisse |
    | `plugin-sdk/provider-auth-login` | Gemeinsam genutzte interaktive Login-Helper für Provider-Plugins |
    | `plugin-sdk/provider-env-vars` | Helper zum Lookup von Auth-Umgebungsvariablen für Provider |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, gemeinsam genutzte Replay-Policy-Builder, Helper für Provider-Endpunkte und Helper zur Normalisierung von Modell-IDs wie `normalizeNativeXaiModelId` |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | Generische Helper für HTTP-/Endpunkt-Fähigkeiten von Providern |
    | `plugin-sdk/provider-web-fetch` | Helper für Registrierung/Cache von Web-Fetch-Providern |
    | `plugin-sdk/provider-web-search` | Helper für Registrierung/Cache/Konfiguration von Web-Such-Providern |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, Gemini-Schema-Bereinigung plus Diagnostik und xAI-Kompatibilitäts-Helper wie `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` und Ähnliches |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, Stream-Wrapper-Typen und gemeinsam genutzte Wrapper-Helper für Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
    | `plugin-sdk/provider-onboard` | Helper zum Patchen der Onboarding-Konfiguration |
    | `plugin-sdk/global-singleton` | Prozesslokale Singleton-/Map-/Cache-Helper |
  </Accordion>

  <Accordion title="Subpaths für Auth und Sicherheit">
    | Subpath | Wichtige Exporte |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`, Helper für Befehlsregister, Helper zur Sender-Autorisierung |
    | `plugin-sdk/approval-auth-runtime` | Helper zur Auflösung von Genehmigenden und zur Action-Auth im selben Chat |
    | `plugin-sdk/approval-client-runtime` | Helper für native Exec-Genehmigungsprofile/-filter |
    | `plugin-sdk/approval-delivery-runtime` | Native Adapter für Genehmigungsfähigkeiten/-zustellung |
    | `plugin-sdk/approval-native-runtime` | Native Helper für Genehmigungsziele und Kontobindung |
    | `plugin-sdk/approval-reply-runtime` | Helper für Exec-/Plugin-Genehmigungs-Antwort-Payloads |
    | `plugin-sdk/command-auth-native` | Native Befehlsauthentifizierung plus native Session-Ziel-Helper |
    | `plugin-sdk/command-detection` | Gemeinsam genutzte Helper zur Befehlserkennung |
    | `plugin-sdk/command-surface` | Helper für Befehls-Body-Normalisierung und Befehlsoberfläche |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/security-runtime` | Gemeinsam genutzte Helper für Vertrauensmodell, DM-Gating, externe Inhalte und Secret-Erfassung |
    | `plugin-sdk/ssrf-policy` | Helper für Host-Allowlists und SSRF-Richtlinien für private Netzwerke |
    | `plugin-sdk/ssrf-runtime` | Helper für Pinned Dispatcher, SSRF-geschütztes Fetch und SSRF-Richtlinien |
    | `plugin-sdk/secret-input` | Helper zum Parsen von Secret-Eingaben |
    | `plugin-sdk/webhook-ingress` | Helper für Webhook-Anfragen/-Ziele |
    | `plugin-sdk/webhook-request-guards` | Helper für Body-Größe/Timeout von Anfragen |
  </Accordion>

  <Accordion title="Subpaths für Runtime und Speicher">
    | Subpath | Wichtige Exporte |
    | --- | --- |
    | `plugin-sdk/runtime` | Breite Runtime-/Logging-/Backup-/Plugin-Install-Helper |
    | `plugin-sdk/runtime-env` | Schmale Helper für Runtime-Umgebung, Logger, Timeout, Retry und Backoff |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | Gemeinsam genutzte Helper für Plugin-Befehle/-Hooks/-HTTP/-Interaktivität |
    | `plugin-sdk/hook-runtime` | Gemeinsam genutzte Pipeline-Helper für Webhooks/interne Hooks |
    | `plugin-sdk/lazy-runtime` | Helper für Lazy-Runtime-Import/Binding wie `createLazyRuntimeModule`, `createLazyRuntimeMethod` und `createLazyRuntimeSurface` |
    | `plugin-sdk/process-runtime` | Prozess-Exec-Helper |
    | `plugin-sdk/cli-runtime` | Helper für CLI-Formatierung, Warten und Versionen |
    | `plugin-sdk/gateway-runtime` | Helper für Gateway-Client und Patches des Channel-Status |
    | `plugin-sdk/config-runtime` | Helper zum Laden/Schreiben von Konfigurationen |
    | `plugin-sdk/telegram-command-config` | Normalisierung von Telegram-Befehlsnamen/-beschreibungen sowie Prüfungen auf Duplikate/Konflikte, auch wenn die gebündelte Telegram-Vertragsoberfläche nicht verfügbar ist |
    | `plugin-sdk/approval-runtime` | Helper für Exec-/Plugin-Genehmigungen, Builder für Genehmigungsfähigkeiten, Auth-/Profil-Helper, native Routing-/Runtime-Helper |
    | `plugin-sdk/reply-runtime` | Gemeinsam genutzte Inbound-/Antwort-Runtime-Helper, Chunking, Dispatch, Heartbeat, Antwortplaner |
    | `plugin-sdk/reply-dispatch-runtime` | Schmale Helper für Reply-Dispatch/Finalisierung |
    | `plugin-sdk/reply-history` | Gemeinsam genutzte Helper für Antwortverlauf in kurzen Zeitfenstern wie `buildHistoryContext`, `recordPendingHistoryEntry` und `clearHistoryEntriesIfEnabled` |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | Schmale Helper für Text-/Markdown-Chunking |
    | `plugin-sdk/session-store-runtime` | Helper für Session-Store-Pfade und `updated-at` |
    | `plugin-sdk/state-paths` | Pfad-Helper für Status-/OAuth-Verzeichnisse |
    | `plugin-sdk/routing` | Helper für Routen-/Session-Key-/Kontobindung wie `resolveAgentRoute`, `buildAgentSessionKey` und `resolveDefaultAgentBoundAccountId` |
    | `plugin-sdk/status-helpers` | Gemeinsam genutzte Helper für Zusammenfassungen des Channel-/Kontostatus, Runtime-Status-Standards und Issue-Metadaten |
    | `plugin-sdk/target-resolver-runtime` | Gemeinsam genutzte Helper zur Zielauflösung |
    | `plugin-sdk/string-normalization-runtime` | Helper zur Slug-/String-Normalisierung |
    | `plugin-sdk/request-url` | String-URLs aus fetch-/request-ähnlichen Eingaben extrahieren |
    | `plugin-sdk/run-command` | Zeitgesteuerter Befehlsrunner mit normalisierten stdout-/stderr-Ergebnissen |
    | `plugin-sdk/param-readers` | Allgemeine Reader für Tool-/CLI-Parameter |
    | `plugin-sdk/tool-send` | Kanonische Send-Zielfelder aus Tool-Argumenten extrahieren |
    | `plugin-sdk/temp-path` | Gemeinsam genutzte Helper für temporäre Download-Pfade |
    | `plugin-sdk/logging-core` | Helper für Subsystem-Logger und Redaction |
    | `plugin-sdk/markdown-table-runtime` | Helper für Modi von Markdown-Tabellen |
    | `plugin-sdk/json-store` | Kleine Helper zum Lesen/Schreiben von JSON-Status |
    | `plugin-sdk/file-lock` | Re-entrant-Dateisperren-Helper |
    | `plugin-sdk/persistent-dedupe` | Helper für festplattenbasierte Dedupe-Caches |
    | `plugin-sdk/acp-runtime` | ACP-Runtime-/Session- und Reply-Dispatch-Helper |
    | `plugin-sdk/agent-config-primitives` | Schmale Primitive für Agent-Runtime-Konfigurationsschemas |
    | `plugin-sdk/boolean-param` | Toleranter Reader für boolesche Parameter |
    | `plugin-sdk/dangerous-name-runtime` | Helper zur Auflösung von Übereinstimmungen bei gefährlichen Namen |
    | `plugin-sdk/device-bootstrap` | Helper für Geräte-Bootstrap und Pairing-Tokens |
    | `plugin-sdk/extension-shared` | Gemeinsam genutzte Primitive für passive Channels und Status-Helper |
    | `plugin-sdk/models-provider-runtime` | Helper für `/models`-Befehle und Provider-Antworten |
    | `plugin-sdk/skill-commands-runtime` | Helper zum Auflisten von Skill-Befehlen |
    | `plugin-sdk/native-command-registry` | Native Helper für Befehlsregister/-Build/-Serialisierung |
    | `plugin-sdk/provider-zai-endpoint` | Helper zur Erkennung von Z.AI-Endpunkten |
    | `plugin-sdk/infra-runtime` | Helper für Systemereignisse/Heartbeat |
    | `plugin-sdk/collection-runtime` | Kleine Helper für begrenzte Caches |
    | `plugin-sdk/diagnostic-runtime` | Helper für Diagnose-Flags und -Ereignisse |
    | `plugin-sdk/error-runtime` | Fehlergraph, Formatierung, gemeinsam genutzte Helper zur Fehlerklassifizierung, `isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | Helper für Wrapped Fetch, Proxy und Pinned Lookup |
    | `plugin-sdk/host-runtime` | Helper zur Normalisierung von Hostnamen und SCP-Hosts |
    | `plugin-sdk/retry-runtime` | Helper für Retry-Konfiguration und Retry-Runner |
    | `plugin-sdk/agent-runtime` | Helper für Agent-Verzeichnisse, -Identität und -Workspace |
    | `plugin-sdk/directory-runtime` | Konfigurationsgestützte Verzeichnisabfrage/Deduplizierung |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="Subpaths für Fähigkeiten und Tests">
    | Subpath | Wichtige Exporte |
    | --- | --- |
    | `plugin-sdk/media-runtime` | Gemeinsam genutzte Helper zum Abrufen/Transformieren/Speichern von Medien sowie Builder für Medien-Payloads |
    | `plugin-sdk/media-generation-runtime` | Gemeinsam genutzte Failover-Helper für Mediengenerierung, Kandidatenauswahl und Meldungen für fehlende Modelle |
    | `plugin-sdk/media-understanding` | Typen für Media-Understanding-Provider sowie Provider-seitige Exporte für Bild-/Audio-Helper |
    | `plugin-sdk/text-runtime` | Gemeinsam genutzte Helper für Text/Markdown/Logging wie das Entfernen von für Assistenten sichtbarem Text, Helper für Markdown-Rendering/Chunking/Tabellen, Redaction-Helper, Directive-Tag-Helper und Safe-Text-Utilities |
    | `plugin-sdk/text-chunking` | Helper für Chunking ausgehender Texte |
    | `plugin-sdk/speech` | Typen für Speech-Provider sowie Provider-seitige Helper für Direktiven, Register und Validierung |
    | `plugin-sdk/speech-core` | Gemeinsam genutzte Typen, Register-, Direktiven- und Normalisierungs-Helper für Speech-Provider |
    | `plugin-sdk/realtime-transcription` | Typen für Realtime-Transcription-Provider und Register-Helper |
    | `plugin-sdk/realtime-voice` | Typen für Realtime-Voice-Provider und Register-Helper |
    | `plugin-sdk/image-generation` | Typen für Image-Generation-Provider |
    | `plugin-sdk/image-generation-core` | Gemeinsam genutzte Typen, Failover-, Auth- und Register-Helper für Bildgenerierung |
    | `plugin-sdk/music-generation` | Typen für Music-Generation-Provider/-Requests/-Ergebnisse |
    | `plugin-sdk/music-generation-core` | Gemeinsam genutzte Typen, Failover-Helper, Provider-Lookup und Parsing von Modellreferenzen für Musikgenerierung |
    | `plugin-sdk/video-generation` | Typen für Video-Generation-Provider/-Requests/-Ergebnisse |
    | `plugin-sdk/video-generation-core` | Gemeinsam genutzte Typen, Failover-Helper, Provider-Lookup und Parsing von Modellreferenzen für Videogenerierung |
    | `plugin-sdk/webhook-targets` | Webhook-Zielregister und Helper zur Routeninstallation |
    | `plugin-sdk/webhook-path` | Helper zur Normalisierung von Webhook-Pfaden |
    | `plugin-sdk/web-media` | Gemeinsam genutzte Helper zum Laden entfernter/lokaler Medien |
    | `plugin-sdk/zod` | Re-exportiertes `zod` für Plugin-SDK-Konsumenten |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="Subpaths für Memory">
    | Subpath | Wichtige Exporte |
    | --- | --- |
    | `plugin-sdk/memory-core` | Gebündelte Hilfsoberfläche von memory-core für Manager-/Konfigurations-/Datei-/CLI-Helper |
    | `plugin-sdk/memory-core-engine-runtime` | Runtime-Fassade für Memory-Index/Suche |
    | `plugin-sdk/memory-core-host-engine-foundation` | Exporte der Foundation-Engine des Memory-Hosts |
    | `plugin-sdk/memory-core-host-engine-embeddings` | Exporte der Embedding-Engine des Memory-Hosts |
    | `plugin-sdk/memory-core-host-engine-qmd` | Exporte der QMD-Engine des Memory-Hosts |
    | `plugin-sdk/memory-core-host-engine-storage` | Exporte der Storage-Engine des Memory-Hosts |
    | `plugin-sdk/memory-core-host-multimodal` | Multimodale Helper des Memory-Hosts |
    | `plugin-sdk/memory-core-host-query` | Query-Helper des Memory-Hosts |
    | `plugin-sdk/memory-core-host-secret` | Secret-Helper des Memory-Hosts |
    | `plugin-sdk/memory-core-host-events` | Helper für Event-Journale des Memory-Hosts |
    | `plugin-sdk/memory-core-host-status` | Status-Helper des Memory-Hosts |
    | `plugin-sdk/memory-core-host-runtime-cli` | CLI-Runtime-Helper des Memory-Hosts |
    | `plugin-sdk/memory-core-host-runtime-core` | Core-Runtime-Helper des Memory-Hosts |
    | `plugin-sdk/memory-core-host-runtime-files` | Datei-/Runtime-Helper des Memory-Hosts |
    | `plugin-sdk/memory-host-core` | Herstellerneutraler Alias für Core-Runtime-Helper des Memory-Hosts |
    | `plugin-sdk/memory-host-events` | Herstellerneutraler Alias für Helper für Event-Journale des Memory-Hosts |
    | `plugin-sdk/memory-host-files` | Herstellerneutraler Alias für Datei-/Runtime-Helper des Memory-Hosts |
    | `plugin-sdk/memory-host-markdown` | Gemeinsam genutzte Managed-Markdown-Helper für memory-nahe Plugins |
    | `plugin-sdk/memory-host-search` | Aktive Memory-Runtime-Fassade für den Zugriff auf Search-Manager |
    | `plugin-sdk/memory-host-status` | Herstellerneutraler Alias für Status-Helper des Memory-Hosts |
    | `plugin-sdk/memory-lancedb` | Gebündelte Hilfsoberfläche von memory-lancedb |
  </Accordion>

  <Accordion title="Reservierte Helper-Subpaths für gebündelte Plugins">
    | Family | Aktuelle Subpaths | Vorgesehene Verwendung |
    | --- | --- | --- |
    | Browser | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | Support-Helper für das gebündelte Browser-Plugin (`browser-support` bleibt das Kompatibilitäts-Barrel) |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | Helper-/Runtime-Oberfläche des gebündelten Matrix-Plugins |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | Helper-/Runtime-Oberfläche des gebündelten LINE-Plugins |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | Hilfsoberfläche des gebündelten IRC-Plugins |
    | Channelspezifische Helper | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | Kompatibilitäts-/Helper-Seams für gebündelte Channels |
    | Auth-/pluginspezifische Helper | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | Helper-Seams für gebündelte Features/Plugins; `plugin-sdk/github-copilot-token` exportiert derzeit `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken` und `resolveCopilotApiToken` |
  </Accordion>
</AccordionGroup>

## Registrierungs-API

Der Callback `register(api)` erhält ein `OpenClawPluginApi`-Objekt mit diesen
Methoden:

### Registrierung von Fähigkeiten

| Methode                                          | Was registriert wird             |
| ------------------------------------------------ | -------------------------------- |
| `api.registerProvider(...)`                      | Textinferenz (LLM)               |
| `api.registerChannel(...)`                       | Messaging-Channel                |
| `api.registerSpeechProvider(...)`                | Text-to-Speech- / STT-Synthese   |
| `api.registerRealtimeTranscriptionProvider(...)` | Streamende Realtime-Transkription |
| `api.registerRealtimeVoiceProvider(...)`         | Duplex-Realtime-Voice-Sitzungen  |
| `api.registerMediaUnderstandingProvider(...)`    | Bild-/Audio-/Videoanalyse        |
| `api.registerImageGenerationProvider(...)`       | Bildgenerierung                  |
| `api.registerMusicGenerationProvider(...)`       | Musikgenerierung                 |
| `api.registerVideoGenerationProvider(...)`       | Videogenerierung                 |
| `api.registerWebFetchProvider(...)`              | Web-Fetch-/Scrape-Provider       |
| `api.registerWebSearchProvider(...)`             | Websuche                         |

### Tools und Befehle

| Methode                         | Was registriert wird                          |
| ------------------------------ | --------------------------------------------- |
| `api.registerTool(tool, opts?)` | Agent-Tool (erforderlich oder `{ optional: true }`) |
| `api.registerCommand(def)`      | Benutzerdefinierter Befehl (umgeht das LLM)   |

### Infrastruktur

| Methode                                        | Was registriert wird                   |
| --------------------------------------------- | -------------------------------------- |
| `api.registerHook(events, handler, opts?)`     | Event-Hook                             |
| `api.registerHttpRoute(params)`                | Gateway-HTTP-Endpunkt                  |
| `api.registerGatewayMethod(name, handler)`     | Gateway-RPC-Methode                    |
| `api.registerCli(registrar, opts?)`            | CLI-Unterbefehl                        |
| `api.registerService(service)`                 | Hintergrunddienst                      |
| `api.registerInteractiveHandler(registration)` | Interaktiver Handler                   |
| `api.registerMemoryPromptSupplement(builder)`  | Additiver, memory-naher Prompt-Abschnitt |
| `api.registerMemoryCorpusSupplement(adapter)`  | Additiver Such-/Lese-Korpus für Memory |

Reservierte Core-Admin-Namespaces (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`) bleiben immer `operator.admin`, auch wenn ein Plugin versucht, einen
engeren Scope für Gateway-Methoden zuzuweisen. Bevorzugen Sie pluginspezifische Präfixe für
plugin-eigene Methoden.

### CLI-Registrierungsmetadaten

`api.registerCli(registrar, opts?)` akzeptiert zwei Arten von Metadaten auf oberster Ebene:

- `commands`: explizite Befehlswurzeln, die dem Registrar gehören
- `descriptors`: Parse-Zeit-Befehlsdeskriptoren für Root-CLI-Hilfe,
  Routing und verzögerte Registrierung von Plugin-CLI

Wenn ein Plugin-Befehl im normalen Root-CLI-Pfad lazy geladen bleiben soll,
geben Sie `descriptors` an, die jede Befehlswurzel auf oberster Ebene abdecken, die durch diesen
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

Verwenden Sie `commands` allein nur dann, wenn Sie keine lazy Registrierung der Root-CLI benötigen.
Dieser eager Kompatibilitätspfad wird weiterhin unterstützt, aber er installiert keine
descriptor-gestützten Platzhalter für verzögertes Laden zur Parse-Zeit.

### Exklusive Slots

| Methode                                    | Was registriert wird                  |
| ------------------------------------------ | ------------------------------------- |
| `api.registerContextEngine(id, factory)`   | Kontext-Engine (jeweils nur eine aktiv) |
| `api.registerMemoryPromptSection(builder)` | Builder für Memory-Prompt-Abschnitte  |
| `api.registerMemoryFlushPlan(resolver)`    | Resolver für Memory-Flush-Pläne       |
| `api.registerMemoryRuntime(runtime)`       | Adapter für die Memory-Runtime        |

### Memory-Embedding-Adapter

| Methode                                        | Was registriert wird                                 |
| --------------------------------------------- | ---------------------------------------------------- |
| `api.registerMemoryEmbeddingProvider(adapter)` | Memory-Embedding-Adapter für das aktive Plugin       |

- `registerMemoryPromptSection`, `registerMemoryFlushPlan` und
  `registerMemoryRuntime` sind exklusiv für Memory-Plugins.
- `registerMemoryEmbeddingProvider` erlaubt dem aktiven Memory-Plugin, einen
  oder mehrere Embedding-Adapter-IDs zu registrieren (zum Beispiel `openai`, `gemini` oder eine
  benutzerdefinierte, vom Plugin definierte ID).
- Benutzerkonfigurationen wie `agents.defaults.memorySearch.provider` und
  `agents.defaults.memorySearch.fallback` werden gegen diese registrierten
  Adapter-IDs aufgelöst.

### Ereignisse und Lifecycle

| Methode                                      | Was sie macht                 |
| -------------------------------------------- | ----------------------------- |
| `api.on(hookName, handler, opts?)`           | Typisierter Lifecycle-Hook    |
| `api.onConversationBindingResolved(handler)` | Callback für Konversationsbindung |

### Hook-Entscheidungssemantik

- `before_tool_call`: Die Rückgabe von `{ block: true }` ist final. Sobald ein Handler dies setzt, werden Handler mit niedrigerer Priorität übersprungen.
- `before_tool_call`: Die Rückgabe von `{ block: false }` wird als keine Entscheidung behandelt (wie das Weglassen von `block`), nicht als Überschreibung.
- `before_install`: Die Rückgabe von `{ block: true }` ist final. Sobald ein Handler dies setzt, werden Handler mit niedrigerer Priorität übersprungen.
- `before_install`: Die Rückgabe von `{ block: false }` wird als keine Entscheidung behandelt (wie das Weglassen von `block`), nicht als Überschreibung.
- `reply_dispatch`: Die Rückgabe von `{ handled: true, ... }` ist final. Sobald ein Handler den Dispatch übernimmt, werden Handler mit niedrigerer Priorität und der Standard-Model-Dispatch-Pfad übersprungen.
- `message_sending`: Die Rückgabe von `{ cancel: true }` ist final. Sobald ein Handler dies setzt, werden Handler mit niedrigerer Priorität übersprungen.
- `message_sending`: Die Rückgabe von `{ cancel: false }` wird als keine Entscheidung behandelt (wie das Weglassen von `cancel`), nicht als Überschreibung.

### Felder des API-Objekts

| Feld                     | Typ                       | Beschreibung                                                                                |
| ------------------------ | ------------------------- | ------------------------------------------------------------------------------------------- |
| `api.id`                 | `string`                  | Plugin-ID                                                                                   |
| `api.name`               | `string`                  | Anzeigename                                                                                 |
| `api.version`            | `string?`                 | Plugin-Version (optional)                                                                   |
| `api.description`        | `string?`                 | Plugin-Beschreibung (optional)                                                              |
| `api.source`             | `string`                  | Plugin-Quellpfad                                                                            |
| `api.rootDir`            | `string?`                 | Plugin-Root-Verzeichnis (optional)                                                          |
| `api.config`             | `OpenClawConfig`          | Aktueller Konfigurations-Snapshot (aktiver In-Memory-Runtime-Snapshot, falls verfügbar)    |
| `api.pluginConfig`       | `Record<string, unknown>` | Pluginspezifische Konfiguration aus `plugins.entries.<id>.config`                           |
| `api.runtime`            | `PluginRuntime`           | [Runtime-Helper](/de/plugins/sdk-runtime)                                                      |
| `api.logger`             | `PluginLogger`            | Bereichsspezifischer Logger (`debug`, `info`, `warn`, `error`)                              |
| `api.registrationMode`   | `PluginRegistrationMode`  | Aktueller Lademodus; `"setup-runtime"` ist das leichtgewichtige Start-/Setup-Fenster vor dem vollständigen Entry |
| `api.resolvePath(input)` | `(string) => string`      | Pfad relativ zum Plugin-Root auflösen                                                       |

## Interne Modulkonvention

Verwenden Sie innerhalb Ihres Plugins lokale Barrel-Dateien für interne Importe:

```
my-plugin/
  api.ts            # Öffentliche Exporte für externe Konsumenten
  runtime-api.ts    # Nur interne Runtime-Exporte
  index.ts          # Plugin-Einstiegspunkt
  setup-entry.ts    # Leichtgewichtiger, nur für Setup gedachter Einstiegspunkt (optional)
```

<Warning>
  Importieren Sie Ihr eigenes Plugin niemals über `openclaw/plugin-sdk/<your-plugin>`
  aus Produktionscode. Leiten Sie interne Importe über `./api.ts` oder
  `./runtime-api.ts`. Der SDK-Pfad ist nur der externe Vertrag.
</Warning>

Öffentliche Oberflächen facadengeladener gebündelter Plugins (`api.ts`, `runtime-api.ts`,
`index.ts`, `setup-entry.ts` und ähnliche öffentliche Entry-Dateien) bevorzugen nun den
aktiven Runtime-Konfigurations-Snapshot, wenn OpenClaw bereits läuft. Wenn noch kein Runtime-
Snapshot existiert, greifen sie auf die auf der Festplatte aufgelöste Konfigurationsdatei zurück.

Provider-Plugins können auch ein schmales, pluginlokales Vertrags-Barrel bereitstellen, wenn ein
Helper absichtlich providerspezifisch ist und noch nicht in einen generischen SDK-
Subpath gehört. Aktuelles gebündeltes Beispiel: Der Anthropic-Provider behält seine Claude-
Stream-Helper in seiner eigenen öffentlichen `api.ts`- / `contract-api.ts`-Seam, anstatt
Anthropic-Beta-Header- und `service_tier`-Logik in einen generischen
`plugin-sdk/*`-Vertrag zu übernehmen.

Weitere aktuelle gebündelte Beispiele:

- `@openclaw/openai-provider`: `api.ts` exportiert Provider-Builder,
  Standardmodell-Helper und Realtime-Provider-Builder
- `@openclaw/openrouter-provider`: `api.ts` exportiert den Provider-Builder plus
  Onboarding-/Konfigurations-Helper

<Warning>
  Produktionscode von Extensions sollte außerdem Importe über `openclaw/plugin-sdk/<other-plugin>`
  vermeiden. Wenn ein Helper wirklich gemeinsam genutzt wird, verschieben Sie ihn in einen neutralen SDK-Subpath
  wie `openclaw/plugin-sdk/speech`, `.../provider-model-shared` oder eine andere
  fähigkeitsorientierte Oberfläche, anstatt zwei Plugins miteinander zu koppeln.
</Warning>

## Verwandte Themen

- [Einstiegspunkte](/de/plugins/sdk-entrypoints) — Optionen für `definePluginEntry` und `defineChannelPluginEntry`
- [Runtime-Helper](/de/plugins/sdk-runtime) — vollständige Referenz des `api.runtime`-Namespace
- [Setup und Konfiguration](/de/plugins/sdk-setup) — Packaging, Manifeste, Konfigurationsschemas
- [Tests](/de/plugins/sdk-testing) — Test-Utilities und Lint-Regeln
- [SDK-Migration](/de/plugins/sdk-migration) — Migration von veralteten Oberflächen
- [Plugin-Interna](/de/plugins/architecture) — tiefe Architektur und Fähigkeitsmodell
