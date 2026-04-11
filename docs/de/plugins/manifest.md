---
read_when:
    - Sie erstellen ein OpenClaw-Plugin
    - Sie müssen ein Plugin-Konfigurationsschema bereitstellen oder Fehler bei der Plugin-Validierung beheben
summary: Plugin-Manifest- und JSON-Schema-Anforderungen (strikte Konfigurationsvalidierung)
title: Plugin-Manifest
x-i18n:
    generated_at: "2026-04-11T15:15:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: 42d454b560a8f6bf714c5d782f34216be1216d83d0a319d08d7349332c91a9e4
    source_path: plugins/manifest.md
    workflow: 15
---

# Plugin-Manifest (`openclaw.plugin.json`)

Diese Seite gilt nur für das **native OpenClaw-Plugin-Manifest**.

Kompatible Bundle-Layouts finden Sie unter [Plugin-Bundles](/de/plugins/bundles).

Kompatible Bundle-Formate verwenden andere Manifestdateien:

- Codex-Bundle: `.codex-plugin/plugin.json`
- Claude-Bundle: `.claude-plugin/plugin.json` oder das standardmäßige Claude-Komponenten-
  Layout ohne Manifest
- Cursor-Bundle: `.cursor-plugin/plugin.json`

OpenClaw erkennt diese Bundle-Layouts ebenfalls automatisch, sie werden jedoch nicht
gegen das hier beschriebene `openclaw.plugin.json`-Schema validiert.

Für kompatible Bundles liest OpenClaw derzeit Bundle-Metadaten sowie deklarierte
Skill-Stammverzeichnisse, Claude-Befehls-Stammverzeichnisse, Claude-Bundle-
`settings.json`-Standardwerte, Claude-Bundle-LSP-Standardwerte und unterstützte Hook-Pakete,
wenn das Layout den Laufzeiterwartungen von OpenClaw entspricht.

Jedes native OpenClaw-Plugin **muss** eine `openclaw.plugin.json`-Datei im
**Plugin-Stammverzeichnis** bereitstellen. OpenClaw verwendet dieses Manifest, um die Konfiguration
**ohne Ausführung von Plugin-Code** zu validieren. Fehlende oder ungültige Manifeste werden als
Plugin-Fehler behandelt und blockieren die Konfigurationsvalidierung.

Den vollständigen Leitfaden zum Plugin-System finden Sie unter: [Plugins](/de/tools/plugin).
Zum nativen Fähigkeitsmodell und zur aktuellen Anleitung für externe Kompatibilität:
[Fähigkeitsmodell](/de/plugins/architecture#public-capability-model).

## Was diese Datei macht

`openclaw.plugin.json` sind die Metadaten, die OpenClaw liest, bevor Ihr
Plugin-Code geladen wird.

Verwenden Sie sie für:

- Plugin-Identität
- Konfigurationsvalidierung
- Authentifizierungs- und Onboarding-Metadaten, die verfügbar sein sollen, ohne die Plugin-
  Laufzeit zu starten
- kostengünstige Aktivierungshinweise, die von Control-Plane-Oberflächen vor dem Laden der Laufzeit geprüft werden können
- kostengünstige Einrichtungsdeskriptoren, die von Einrichtungs-/Onboarding-Oberflächen vor dem Laden der Laufzeit geprüft werden können
- Alias- und Auto-Aktivierungs-Metadaten, die aufgelöst werden sollen, bevor die Plugin-Laufzeit geladen wird
- Kurzform-Metadaten zur Eigentümerschaft von Modellfamilien, die das
  Plugin vor dem Laden der Laufzeit automatisch aktivieren sollen
- statische Snapshots der Fähigkeitszuordnung, die für gebündelte Kompatibilitätsverdrahtung und Vertragsabdeckung verwendet werden
- kanalspezifische Konfigurationsmetadaten, die in Katalog- und Validierungsoberflächen
  zusammengeführt werden sollen, ohne die Laufzeit zu laden
- Hinweise für die Konfigurations-Benutzeroberfläche

Verwenden Sie sie nicht für:

- Registrierung von Laufzeitverhalten
- Deklaration von Code-Einstiegspunkten
- npm-Installationsmetadaten

Diese gehören in Ihren Plugin-Code und in `package.json`.

## Minimales Beispiel

```json
{
  "id": "voice-call",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
```

## Umfangreiches Beispiel

```json
{
  "id": "openrouter",
  "name": "OpenRouter",
  "description": "OpenRouter-Provider-Plugin",
  "version": "1.0.0",
  "providers": ["openrouter"],
  "modelSupport": {
    "modelPrefixes": ["router-"]
  },
  "cliBackends": ["openrouter-cli"],
  "providerAuthEnvVars": {
    "openrouter": ["OPENROUTER_API_KEY"]
  },
  "providerAuthAliases": {
    "openrouter-coding": "openrouter"
  },
  "channelEnvVars": {
    "openrouter-chatops": ["OPENROUTER_CHATOPS_TOKEN"]
  },
  "providerAuthChoices": [
    {
      "provider": "openrouter",
      "method": "api-key",
      "choiceId": "openrouter-api-key",
      "choiceLabel": "OpenRouter-API-Schlüssel",
      "groupId": "openrouter",
      "groupLabel": "OpenRouter",
      "optionKey": "openrouterApiKey",
      "cliFlag": "--openrouter-api-key",
      "cliOption": "--openrouter-api-key <key>",
      "cliDescription": "OpenRouter-API-Schlüssel",
      "onboardingScopes": ["text-inference"]
    }
  ],
  "uiHints": {
    "apiKey": {
      "label": "API-Schlüssel",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  },
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "apiKey": {
        "type": "string"
      }
    }
  }
}
```

## Referenz der Felder auf oberster Ebene

| Feld                                | Erforderlich | Typ                              | Bedeutung                                                                                                                                                                                                   |
| ----------------------------------- | ------------ | -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                                | Ja           | `string`                         | Kanonische Plugin-ID. Dies ist die ID, die in `plugins.entries.<id>` verwendet wird.                                                                                                                       |
| `configSchema`                      | Ja           | `object`                         | Inline-JSON-Schema für die Konfiguration dieses Plugins.                                                                                                                                                    |
| `enabledByDefault`                  | Nein         | `true`                           | Kennzeichnet ein gebündeltes Plugin als standardmäßig aktiviert. Lassen Sie das Feld weg oder setzen Sie einen anderen Wert als `true`, damit das Plugin standardmäßig deaktiviert bleibt.               |
| `legacyPluginIds`                   | Nein         | `string[]`                       | Veraltete IDs, die auf diese kanonische Plugin-ID normalisiert werden.                                                                                                                                      |
| `autoEnableWhenConfiguredProviders` | Nein         | `string[]`                       | Provider-IDs, die dieses Plugin automatisch aktivieren sollen, wenn Authentifizierung, Konfiguration oder Modellreferenzen sie erwähnen.                                                                  |
| `kind`                              | Nein         | `"memory"` \| `"context-engine"` | Deklariert einen exklusiven Plugin-Typ, der von `plugins.slots.*` verwendet wird.                                                                                                                          |
| `channels`                          | Nein         | `string[]`                       | Kanal-IDs, die diesem Plugin gehören. Wird für Erkennung und Konfigurationsvalidierung verwendet.                                                                                                          |
| `providers`                         | Nein         | `string[]`                       | Provider-IDs, die diesem Plugin gehören.                                                                                                                                                                    |
| `modelSupport`                      | Nein         | `object`                         | Dem Manifest gehörende Kurzform-Metadaten zu Modellfamilien, die verwendet werden, um das Plugin vor der Laufzeit automatisch zu laden.                                                                   |
| `cliBackends`                       | Nein         | `string[]`                       | CLI-Inferenz-Backend-IDs, die diesem Plugin gehören. Wird für die automatische Aktivierung beim Start aus expliziten Konfigurationsreferenzen verwendet.                                                  |
| `commandAliases`                    | Nein         | `object[]`                       | Befehlsnamen, die diesem Plugin gehören und noch vor dem Laden der Laufzeit pluginbewusste Konfigurations- und CLI-Diagnosen erzeugen sollen.                                                             |
| `providerAuthEnvVars`               | Nein         | `Record<string, string[]>`       | Kostengünstige Umgebungsvariablen-Metadaten für Provider-Authentifizierung, die OpenClaw ohne Laden von Plugin-Code prüfen kann.                                                                          |
| `providerAuthAliases`               | Nein         | `Record<string, string>`         | Provider-IDs, die für die Authentifizierung eine andere Provider-ID wiederverwenden sollen, zum Beispiel ein Coding-Provider, der den API-Schlüssel und die Authentifizierungsprofile des Basis-Providers teilt. |
| `channelEnvVars`                    | Nein         | `Record<string, string[]>`       | Kostengünstige Umgebungsvariablen-Metadaten für Kanäle, die OpenClaw ohne Laden von Plugin-Code prüfen kann. Verwenden Sie dies für env-gesteuerte Kanaleinrichtung oder Authentifizierungsoberflächen, die generische Start-/Konfigurationshilfen sehen sollen. |
| `providerAuthChoices`               | Nein         | `object[]`                       | Kostengünstige Metadaten zu Authentifizierungsoptionen für Onboarding-Auswahlen, bevorzugte Provider-Auflösung und einfache Verdrahtung von CLI-Flags.                                                   |
| `activation`                        | Nein         | `object`                         | Kostengünstige Aktivierungshinweise für provider-, befehls-, kanal-, routing- und fähigkeitsausgelöstes Laden. Nur Metadaten; das tatsächliche Verhalten bleibt Eigentum der Plugin-Laufzeit.           |
| `setup`                             | Nein         | `object`                         | Kostengünstige Einrichtungs-/Onboarding-Deskriptoren, die von Erkennungs- und Einrichtungsoberflächen geprüft werden können, ohne die Plugin-Laufzeit zu laden.                                          |
| `contracts`                         | Nein         | `object`                         | Statischer Snapshot gebündelter Fähigkeiten für speech, realtime transcription, realtime voice, media-understanding, image-generation, music-generation, video-generation, web-fetch, Websuche und Tool-Eigentümerschaft. |
| `channelConfigs`                    | Nein         | `Record<string, object>`         | Dem Manifest gehörende Kanal-Konfigurationsmetadaten, die vor dem Laden der Laufzeit in Erkennungs- und Validierungsoberflächen zusammengeführt werden.                                                   |
| `skills`                            | Nein         | `string[]`                       | Zu ladende Skills-Verzeichnisse, relativ zum Plugin-Stammverzeichnis.                                                                                                                                       |
| `name`                              | Nein         | `string`                         | Lesbarer Plugin-Name.                                                                                                                                                                                       |
| `description`                       | Nein         | `string`                         | Kurze Zusammenfassung, die in Plugin-Oberflächen angezeigt wird.                                                                                                                                             |
| `version`                           | Nein         | `string`                         | Informative Plugin-Version.                                                                                                                                                                                 |
| `uiHints`                           | Nein         | `Record<string, object>`         | UI-Beschriftungen, Platzhalter und Hinweise zur Vertraulichkeit für Konfigurationsfelder.                                                                                                                  |

## Referenz für `providerAuthChoices`

Jeder Eintrag in `providerAuthChoices` beschreibt eine Onboarding- oder Authentifizierungsoption.
OpenClaw liest dies, bevor die Provider-Laufzeit geladen wird.

| Feld                  | Erforderlich | Typ                                             | Bedeutung                                                                                                  |
| --------------------- | ------------ | ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `provider`            | Ja           | `string`                                        | Provider-ID, zu der diese Option gehört.                                                                   |
| `method`              | Ja           | `string`                                        | ID der Authentifizierungsmethode, an die weitergeleitet werden soll.                                       |
| `choiceId`            | Ja           | `string`                                        | Stabile ID der Authentifizierungsoption, die von Onboarding- und CLI-Abläufen verwendet wird.             |
| `choiceLabel`         | Nein         | `string`                                        | Benutzerseitige Bezeichnung. Wenn sie weggelassen wird, verwendet OpenClaw stattdessen `choiceId`.        |
| `choiceHint`          | Nein         | `string`                                        | Kurzer Hilfetext für die Auswahl.                                                                          |
| `assistantPriority`   | Nein         | `number`                                        | Niedrigere Werte werden in assistentengesteuerten interaktiven Auswahlen früher sortiert.                 |
| `assistantVisibility` | Nein         | `"visible"` \| `"manual-only"`                  | Blendet die Option in Assistenten-Auswahlen aus, erlaubt aber weiterhin die manuelle Auswahl über die CLI. |
| `deprecatedChoiceIds` | Nein         | `string[]`                                      | Veraltete Options-IDs, die Benutzer zu dieser Ersatzoption umleiten sollen.                                |
| `groupId`             | Nein         | `string`                                        | Optionale Gruppen-ID zum Gruppieren verwandter Optionen.                                                   |
| `groupLabel`          | Nein         | `string`                                        | Benutzerseitige Bezeichnung für diese Gruppe.                                                              |
| `groupHint`           | Nein         | `string`                                        | Kurzer Hilfetext für die Gruppe.                                                                           |
| `optionKey`           | Nein         | `string`                                        | Interner Optionsschlüssel für einfache Authentifizierungsabläufe mit nur einem Flag.                       |
| `cliFlag`             | Nein         | `string`                                        | Name des CLI-Flags, z. B. `--openrouter-api-key`.                                                          |
| `cliOption`           | Nein         | `string`                                        | Vollständige Form der CLI-Option, z. B. `--openrouter-api-key <key>`.                                      |
| `cliDescription`      | Nein         | `string`                                        | Beschreibung, die in der CLI-Hilfe verwendet wird.                                                         |
| `onboardingScopes`    | Nein         | `Array<"text-inference" \| "image-generation">` | In welchen Onboarding-Oberflächen diese Option erscheinen soll. Wenn weggelassen, ist der Standardwert `["text-inference"]`. |

## Referenz für `commandAliases`

Verwenden Sie `commandAliases`, wenn ein Plugin einen Laufzeit-Befehlsnamen besitzt, den Benutzer
versehentlich in `plugins.allow` eintragen oder als CLI-Stammbefehl ausführen
möchten. OpenClaw verwendet diese Metadaten für Diagnosen, ohne Plugin-Laufzeitcode zu importieren.

```json
{
  "commandAliases": [
    {
      "name": "dreaming",
      "kind": "runtime-slash",
      "cliCommand": "memory"
    }
  ]
}
```

| Feld         | Erforderlich | Typ               | Bedeutung                                                                 |
| ------------ | ------------ | ----------------- | ------------------------------------------------------------------------- |
| `name`       | Ja           | `string`          | Befehlsname, der zu diesem Plugin gehört.                                 |
| `kind`       | Nein         | `"runtime-slash"` | Kennzeichnet den Alias als Chat-Slash-Befehl statt als CLI-Stammbefehl.   |
| `cliCommand` | Nein         | `string`          | Zugehöriger CLI-Stammbefehl, der für CLI-Vorgänge empfohlen werden kann, falls vorhanden. |

## Referenz für `activation`

Verwenden Sie `activation`, wenn das Plugin kostengünstig deklarieren kann, welche Control-Plane-Ereignisse
es später aktivieren sollen.

Dieser Block enthält nur Metadaten. Er registriert kein Laufzeitverhalten und
ersetzt nicht `register(...)`, `setupEntry` oder andere Laufzeit-/Plugin-Einstiegspunkte.

```json
{
  "activation": {
    "onProviders": ["openai"],
    "onCommands": ["models"],
    "onChannels": ["web"],
    "onRoutes": ["gateway-webhook"],
    "onCapabilities": ["provider", "tool"]
  }
}
```

| Feld             | Erforderlich | Typ                                                  | Bedeutung                                                         |
| ---------------- | ------------ | ---------------------------------------------------- | ----------------------------------------------------------------- |
| `onProviders`    | Nein         | `string[]`                                           | Provider-IDs, die dieses Plugin bei Anforderung aktivieren sollen. |
| `onCommands`     | Nein         | `string[]`                                           | Befehls-IDs, die dieses Plugin aktivieren sollen.                  |
| `onChannels`     | Nein         | `string[]`                                           | Kanal-IDs, die dieses Plugin aktivieren sollen.                    |
| `onRoutes`       | Nein         | `string[]`                                           | Routenarten, die dieses Plugin aktivieren sollen.                  |
| `onCapabilities` | Nein         | `Array<"provider" \| "channel" \| "tool" \| "hook">` | Allgemeine Fähigkeitshinweise, die bei der Aktivierungsplanung der Control Plane verwendet werden. |

## Referenz für `setup`

Verwenden Sie `setup`, wenn Einrichtungs- und Onboarding-Oberflächen kostengünstige, dem Plugin gehörende Metadaten
benötigen, bevor die Laufzeit geladen wird.

```json
{
  "setup": {
    "providers": [
      {
        "id": "openai",
        "authMethods": ["api-key"],
        "envVars": ["OPENAI_API_KEY"]
      }
    ],
    "cliBackends": ["openai-cli"],
    "configMigrations": ["legacy-openai-auth"],
    "requiresRuntime": false
  }
}
```

Das Top-Level-Feld `cliBackends` bleibt gültig und beschreibt weiterhin CLI-Inferenz-
Backends. `setup.cliBackends` ist die einrichtungsspezifische Deskriptoroberfläche für
Control-Plane-/Einrichtungsabläufe, die nur Metadaten bleiben soll.

### Referenz für `setup.providers`

| Feld          | Erforderlich | Typ        | Bedeutung                                                                                |
| ------------- | ------------ | ---------- | ---------------------------------------------------------------------------------------- |
| `id`          | Ja           | `string`   | Provider-ID, die während der Einrichtung oder des Onboardings bereitgestellt wird.       |
| `authMethods` | Nein         | `string[]` | IDs von Einrichtungs-/Authentifizierungsmethoden, die dieser Provider ohne vollständige Laufzeit unterstützt. |
| `envVars`     | Nein         | `string[]` | Umgebungsvariablen, die generische Einrichtungs-/Statusoberflächen prüfen können, bevor die Plugin-Laufzeit geladen wird. |

### `setup`-Felder

| Feld               | Erforderlich | Typ        | Bedeutung                                                                   |
| ------------------ | ------------ | ---------- | --------------------------------------------------------------------------- |
| `providers`        | Nein         | `object[]` | Provider-Einrichtungsdeskriptoren, die während Einrichtung und Onboarding bereitgestellt werden. |
| `cliBackends`      | Nein         | `string[]` | Backend-IDs zur Einrichtungszeit, die ohne vollständige Laufzeitaktivierung verfügbar sind. |
| `configMigrations` | Nein         | `string[]` | IDs von Konfigurationsmigrationen, die der Einrichtungsoberfläche dieses Plugins gehören. |
| `requiresRuntime`  | Nein         | `boolean`  | Ob die Einrichtung nach dem Nachschlagen des Deskriptors weiterhin die Ausführung der Plugin-Laufzeit erfordert. |

## Referenz für `uiHints`

`uiHints` ist eine Zuordnung von Konfigurationsfeldnamen zu kleinen Darstellungshinweisen.

```json
{
  "uiHints": {
    "apiKey": {
      "label": "API key",
      "help": "Used for OpenRouter requests",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  }
}
```

Jeder Feldhinweis kann Folgendes enthalten:

| Feld          | Typ        | Bedeutung                                 |
| ------------- | ---------- | ----------------------------------------- |
| `label`       | `string`   | Benutzerseitige Feldbezeichnung.          |
| `help`        | `string`   | Kurzer Hilfetext.                         |
| `tags`        | `string[]` | Optionale UI-Tags.                        |
| `advanced`    | `boolean`  | Kennzeichnet das Feld als erweitert.      |
| `sensitive`   | `boolean`  | Kennzeichnet das Feld als geheim oder sensibel. |
| `placeholder` | `string`   | Platzhaltertext für Formulareingaben.     |

## Referenz für `contracts`

Verwenden Sie `contracts` nur für statische Metadaten zur Fähigkeitszuordnung, die OpenClaw
ohne Import der Plugin-Laufzeit lesen kann.

```json
{
  "contracts": {
    "speechProviders": ["openai"],
    "realtimeTranscriptionProviders": ["openai"],
    "realtimeVoiceProviders": ["openai"],
    "mediaUnderstandingProviders": ["openai", "openai-codex"],
    "imageGenerationProviders": ["openai"],
    "videoGenerationProviders": ["qwen"],
    "webFetchProviders": ["firecrawl"],
    "webSearchProviders": ["gemini"],
    "tools": ["firecrawl_search", "firecrawl_scrape"]
  }
}
```

Jede Liste ist optional:

| Feld                             | Typ        | Bedeutung                                                   |
| -------------------------------- | ---------- | ----------------------------------------------------------- |
| `speechProviders`                | `string[]` | Speech-Provider-IDs, die diesem Plugin gehören.             |
| `realtimeTranscriptionProviders` | `string[]` | Realtime-Transcription-Provider-IDs, die diesem Plugin gehören. |
| `realtimeVoiceProviders`         | `string[]` | Realtime-Voice-Provider-IDs, die diesem Plugin gehören.     |
| `mediaUnderstandingProviders`    | `string[]` | Media-understanding-Provider-IDs, die diesem Plugin gehören. |
| `imageGenerationProviders`       | `string[]` | Image-generation-Provider-IDs, die diesem Plugin gehören.   |
| `videoGenerationProviders`       | `string[]` | Video-generation-Provider-IDs, die diesem Plugin gehören.   |
| `webFetchProviders`              | `string[]` | Web-fetch-Provider-IDs, die diesem Plugin gehören.          |
| `webSearchProviders`             | `string[]` | Web-search-Provider-IDs, die diesem Plugin gehören.         |
| `tools`                          | `string[]` | Namen von Agent-Tools, die diesem Plugin für gebündelte Vertragsprüfungen gehören. |

## Referenz für `channelConfigs`

Verwenden Sie `channelConfigs`, wenn ein Kanal-Plugin kostengünstige Konfigurationsmetadaten benötigt, bevor
die Laufzeit geladen wird.

```json
{
  "channelConfigs": {
    "matrix": {
      "schema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "homeserverUrl": { "type": "string" }
        }
      },
      "uiHints": {
        "homeserverUrl": {
          "label": "Homeserver URL",
          "placeholder": "https://matrix.example.com"
        }
      },
      "label": "Matrix",
      "description": "Matrix-Homeserver-Verbindung",
      "preferOver": ["matrix-legacy"]
    }
  }
}
```

Jeder Kanaleintrag kann Folgendes enthalten:

| Feld          | Typ                      | Bedeutung                                                                                  |
| ------------- | ------------------------ | ------------------------------------------------------------------------------------------ |
| `schema`      | `object`                 | JSON-Schema für `channels.<id>`. Für jeden deklarierten Kanal-Konfigurationseintrag erforderlich. |
| `uiHints`     | `Record<string, object>` | Optionale UI-Beschriftungen/Platzhalter/Hinweise zur Vertraulichkeit für diesen Abschnitt der Kanal-Konfiguration. |
| `label`       | `string`                 | Kanalbezeichnung, die in Auswahl- und Prüfoberflächen zusammengeführt wird, wenn Laufzeitmetadaten noch nicht bereit sind. |
| `description` | `string`                 | Kurze Kanalbeschreibung für Prüf- und Katalogoberflächen.                                  |
| `preferOver`  | `string[]`               | Veraltete oder niedriger priorisierte Plugin-IDs, die dieser Kanal in Auswahloberflächen übertreffen soll. |

## Referenz für `modelSupport`

Verwenden Sie `modelSupport`, wenn OpenClaw Ihr Provider-Plugin aus
Kurzform-Modell-IDs wie `gpt-5.4` oder `claude-sonnet-4.6` ableiten soll, bevor die Plugin-Laufzeit
geladen wird.

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

OpenClaw wendet diese Rangfolge an:

- explizite `provider/model`-Referenzen verwenden die zugehörigen `providers`-Manifestmetadaten
- `modelPatterns` haben Vorrang vor `modelPrefixes`
- wenn ein nicht gebündeltes Plugin und ein gebündeltes Plugin beide passen, gewinnt das nicht gebündelte
  Plugin
- verbleibende Mehrdeutigkeit wird ignoriert, bis der Benutzer oder die Konfiguration einen Provider angibt

Felder:

| Feld            | Typ        | Bedeutung                                                                      |
| --------------- | ---------- | ------------------------------------------------------------------------------ |
| `modelPrefixes` | `string[]` | Präfixe, die mit `startsWith` gegen Kurzform-Modell-IDs abgeglichen werden.    |
| `modelPatterns` | `string[]` | Regex-Quellen, die nach Entfernen des Profilsuffixes mit Kurzform-Modell-IDs abgeglichen werden. |

Veraltete Fähigkeits-Schlüssel auf oberster Ebene sind deprecated. Verwenden Sie `openclaw doctor --fix`, um
`speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`,
`webFetchProviders` und `webSearchProviders` unter `contracts` zu
verschieben; das normale Laden des Manifests behandelt diese Felder auf oberster Ebene nicht mehr als
Fähigkeitszuordnung.

## Manifest im Vergleich zu package.json

Die beiden Dateien erfüllen unterschiedliche Aufgaben:

| Datei                  | Verwendung                                                                                                                             |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.plugin.json` | Erkennung, Konfigurationsvalidierung, Metadaten zu Authentifizierungsoptionen und UI-Hinweise, die vorhanden sein müssen, bevor Plugin-Code ausgeführt wird |
| `package.json`         | npm-Metadaten, Installation von Abhängigkeiten und der `openclaw`-Block für Einstiegspunkte, Installationsfreigabe, Einrichtung oder Katalogmetadaten |

Wenn Sie nicht sicher sind, wohin ein Metadatum gehört, verwenden Sie diese Regel:

- wenn OpenClaw es kennen muss, bevor Plugin-Code geladen wird, gehört es in `openclaw.plugin.json`
- wenn es um Paketierung, Einstiegsdateien oder das npm-Installationsverhalten geht, gehört es in `package.json`

### `package.json`-Felder, die die Erkennung beeinflussen

Einige Metadaten von Plugins vor der Laufzeit befinden sich absichtlich in `package.json` unter dem
`openclaw`-Block statt in `openclaw.plugin.json`.

Wichtige Beispiele:

| Feld                                                              | Bedeutung                                                                                                                                     |
| ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                             | Deklariert native Plugin-Einstiegspunkte.                                                                                                     |
| `openclaw.setupEntry`                                             | Leichtgewichtiger Einstiegspunkt nur für die Einrichtung, verwendet während des Onboardings und beim verzögerten Kanalstart.                |
| `openclaw.channel`                                                | Kostengünstige Katalogmetadaten für Kanäle wie Bezeichnungen, Dokumentationspfade, Aliasse und Auswahltexte.                                |
| `openclaw.channel.configuredState`                                | Leichtgewichtige Metadaten für die Prüfung des konfigurierten Zustands, die „existiert bereits eine env-only-Einrichtung?“ beantworten können, ohne die vollständige Kanal-Laufzeit zu laden. |
| `openclaw.channel.persistedAuthState`                             | Leichtgewichtige Metadaten für die Prüfung des persistenten Authentifizierungszustands, die „ist bereits irgendwo eine Anmeldung vorhanden?“ beantworten können, ohne die vollständige Kanal-Laufzeit zu laden. |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | Hinweise zur Installation/Aktualisierung für gebündelte und extern veröffentlichte Plugins.                                                  |
| `openclaw.install.defaultChoice`                                  | Bevorzugter Installationspfad, wenn mehrere Installationsquellen verfügbar sind.                                                             |
| `openclaw.install.minHostVersion`                                 | Minimal unterstützte OpenClaw-Host-Version, mit einer SemVer-Untergrenze wie `>=2026.3.22`.                                                 |
| `openclaw.install.allowInvalidConfigRecovery`                     | Erlaubt einen eng begrenzten Wiederherstellungspfad zur Neuinstallation gebündelter Plugins, wenn die Konfiguration ungültig ist.           |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | Erlaubt das Laden von Kanaloberflächen nur für die Einrichtung vor dem vollständigen Kanal-Plugin beim Start.                               |

`openclaw.install.minHostVersion` wird während der Installation und beim Laden der Manifest-
Registry erzwungen. Ungültige Werte werden abgelehnt; neuere, aber gültige Werte überspringen das
Plugin auf älteren Hosts.

`openclaw.install.allowInvalidConfigRecovery` ist absichtlich eng begrenzt. Es macht
nicht beliebige fehlerhafte Konfigurationen installierbar. Derzeit erlaubt es nur Installationsabläufen,
sich von bestimmten veralteten Upgrade-Fehlern gebündelter Plugins zu erholen, zum Beispiel einem
fehlenden Pfad zu einem gebündelten Plugin oder einem veralteten `channels.<id>`-Eintrag für dasselbe
gebündelte Plugin. Nicht zusammenhängende Konfigurationsfehler blockieren weiterhin die Installation und verweisen Operatoren
auf `openclaw doctor --fix`.

`openclaw.channel.persistedAuthState` ist Paketmetadaten für ein kleines Prüfmodul:

```json
{
  "openclaw": {
    "channel": {
      "id": "whatsapp",
      "persistedAuthState": {
        "specifier": "./auth-presence",
        "exportName": "hasAnyWhatsAppAuth"
      }
    }
  }
}
```

Verwenden Sie dies, wenn Einrichtungs-, Doctor- oder configured-state-Abläufe eine kostengünstige Ja/Nein-
Auth-Prüfung benötigen, bevor das vollständige Kanal-Plugin geladen wird. Das Zielexport sollte eine kleine
Funktion sein, die nur persistenten Zustand liest; leiten Sie dies nicht über das vollständige
Kanal-Laufzeit-Barrel.

`openclaw.channel.configuredState` verwendet dieselbe Form für kostengünstige env-only-
Prüfungen des konfigurierten Zustands:

```json
{
  "openclaw": {
    "channel": {
      "id": "telegram",
      "configuredState": {
        "specifier": "./configured-state",
        "exportName": "hasTelegramConfiguredState"
      }
    }
  }
}
```

Verwenden Sie dies, wenn ein Kanal den konfigurierten Zustand aus env oder anderen kleinen
Nicht-Laufzeiteingaben beantworten kann. Wenn die Prüfung vollständige Konfigurationsauflösung oder die echte
Kanal-Laufzeit benötigt, belassen Sie diese Logik stattdessen im Hook `config.hasConfiguredState`
des Plugins.

## JSON-Schema-Anforderungen

- **Jedes Plugin muss ein JSON-Schema bereitstellen**, auch wenn es keine Konfiguration akzeptiert.
- Ein leeres Schema ist zulässig (zum Beispiel `{ "type": "object", "additionalProperties": false }`).
- Schemata werden beim Lesen/Schreiben der Konfiguration validiert, nicht zur Laufzeit.

## Validierungsverhalten

- Unbekannte `channels.*`-Schlüssel sind **Fehler**, es sei denn, die Kanal-ID wird durch
  ein Plugin-Manifest deklariert.
- `plugins.entries.<id>`, `plugins.allow`, `plugins.deny` und `plugins.slots.*`
  müssen auf **erkennbare** Plugin-IDs verweisen. Unbekannte IDs sind **Fehler**.
- Wenn ein Plugin installiert ist, aber ein fehlerhaftes oder fehlendes Manifest oder Schema hat,
  schlägt die Validierung fehl und Doctor meldet den Plugin-Fehler.
- Wenn eine Plugin-Konfiguration existiert, das Plugin aber **deaktiviert** ist, bleibt die Konfiguration erhalten und
  in Doctor + Protokollen wird eine **Warnung** angezeigt.

Die vollständige `plugins.*`-Schema-Referenz finden Sie unter [Konfigurationsreferenz](/de/gateway/configuration).

## Hinweise

- Das Manifest ist **für native OpenClaw-Plugins erforderlich**, einschließlich lokaler Dateisystem-Ladevorgänge.
- Die Laufzeit lädt das Plugin-Modul weiterhin separat; das Manifest dient nur der
  Erkennung + Validierung.
- Native Manifeste werden mit JSON5 geparst, daher sind Kommentare, nachgestellte Kommas und
  nicht in Anführungszeichen gesetzte Schlüssel zulässig, solange der endgültige Wert weiterhin ein Objekt ist.
- Nur dokumentierte Manifestfelder werden vom Manifest-Loader gelesen. Vermeiden Sie es,
  hier benutzerdefinierte Schlüssel auf oberster Ebene hinzuzufügen.
- `providerAuthEnvVars` ist der kostengünstige Metadatenpfad für Authentifizierungsprüfungen, env-marker-
  Validierung und ähnliche Oberflächen für Provider-Authentifizierung, die die Plugin-Laufzeit nicht starten sollten,
  nur um env-Namen zu prüfen.
- `providerAuthAliases` erlaubt es Provider-Varianten, die Authentifizierungs-
  Umgebungsvariablen, Authentifizierungsprofile, konfigurationsgestützte Authentifizierung und API-Schlüssel-Onboarding-Optionen eines anderen Providers wiederzuverwenden,
  ohne diese Beziehung im Core fest zu codieren.
- `channelEnvVars` ist der kostengünstige Metadatenpfad für Shell-env-Fallback, Einrichtungs-
  Eingabeaufforderungen und ähnliche Kanaloberflächen, die die Plugin-Laufzeit nicht starten sollten,
  nur um env-Namen zu prüfen.
- `providerAuthChoices` ist der kostengünstige Metadatenpfad für Auswahlfelder von Authentifizierungsoptionen,
  die Auflösung von `--auth-choice`, bevorzugte Provider-Zuordnung und die einfache Registrierung von
  Onboarding-CLI-Flags, bevor die Provider-Laufzeit geladen wird. Informationen für Laufzeit-
  Assistenten, die Provider-Code erfordern, finden Sie unter
  [Provider-Laufzeit-Hooks](/de/plugins/architecture#provider-runtime-hooks).
- Exklusive Plugin-Arten werden über `plugins.slots.*` ausgewählt.
  - `kind: "memory"` wird über `plugins.slots.memory` ausgewählt.
  - `kind: "context-engine"` wird über `plugins.slots.contextEngine`
    ausgewählt (Standard: integriertes `legacy`).
- `channels`, `providers`, `cliBackends` und `skills` können weggelassen werden, wenn ein
  Plugin sie nicht benötigt.
- Wenn Ihr Plugin von nativen Modulen abhängt, dokumentieren Sie die Build-Schritte und alle
  Anforderungen an die Paketmanager-Allowlist (zum Beispiel pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`).

## Verwandt

- [Plugins erstellen](/de/plugins/building-plugins) — Erste Schritte mit Plugins
- [Plugin-Architektur](/de/plugins/architecture) — interne Architektur
- [SDK-Übersicht](/de/plugins/sdk-overview) — Referenz zum Plugin SDK
