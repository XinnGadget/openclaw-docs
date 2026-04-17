---
read_when:
    - Sie erstellen ein OpenClaw-Plugin
    - Sie müssen ein Plugin-Konfigurationsschema bereitstellen oder Plugin-Validierungsfehler debuggen
summary: Plugin-Manifest + JSON-Schema-Anforderungen (strikte Konfigurationsvalidierung)
title: Plugin-Manifest
x-i18n:
    generated_at: "2026-04-15T06:21:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: ba2183bfa8802871e4ef33a0ebea290606e8351e9e83e25ee72456addb768730
    source_path: plugins/manifest.md
    workflow: 15
---

# Plugin-Manifest (`openclaw.plugin.json`)

Diese Seite gilt nur für das **native OpenClaw-Plugin-Manifest**.

Informationen zu kompatiblen Bundle-Layouts finden Sie unter [Plugin-Bundles](/de/plugins/bundles).

Kompatible Bundle-Formate verwenden andere Manifestdateien:

- Codex-Bundle: `.codex-plugin/plugin.json`
- Claude-Bundle: `.claude-plugin/plugin.json` oder das standardmäßige Claude-Komponenten-
  Layout ohne Manifest
- Cursor-Bundle: `.cursor-plugin/plugin.json`

OpenClaw erkennt diese Bundle-Layouts ebenfalls automatisch, sie werden jedoch nicht
gegen das hier beschriebene Schema für `openclaw.plugin.json` validiert.

Für kompatible Bundles liest OpenClaw derzeit Bundle-Metadaten sowie deklarierte
Skill-Stammverzeichnisse, Claude-Befehlsstammverzeichnisse, Claude-Bundle-Standardwerte aus `settings.json`,
Claude-Bundle-LSP-Standardwerte und unterstützte Hook-Pakete, wenn das Layout den
Laufzeiterwartungen von OpenClaw entspricht.

Jedes native OpenClaw-Plugin **muss** eine Datei `openclaw.plugin.json` im
**Plugin-Stammverzeichnis** bereitstellen. OpenClaw verwendet dieses Manifest, um die Konfiguration zu validieren,
**ohne Plugin-Code auszuführen**. Fehlende oder ungültige Manifeste werden als
Plugin-Fehler behandelt und blockieren die Konfigurationsvalidierung.

Den vollständigen Leitfaden zum Plugin-System finden Sie unter: [Plugins](/de/tools/plugin).
Zum nativen Fähigkeitsmodell und zur aktuellen Anleitung zur externen Kompatibilität:
[Fähigkeitsmodell](/de/plugins/architecture#public-capability-model).

## Was diese Datei macht

`openclaw.plugin.json` sind die Metadaten, die OpenClaw liest, bevor Ihr
Plugin-Code geladen wird.

Verwenden Sie sie für:

- Plugin-Identität
- Konfigurationsvalidierung
- Authentifizierungs- und Onboarding-Metadaten, die verfügbar sein sollen, ohne die Plugin-
  Laufzeit zu starten
- kostengünstige Aktivierungshinweise, die Control-Plane-Oberflächen vor dem Laden der Laufzeit
  prüfen können
- kostengünstige Setup-Deskriptoren, die Setup-/Onboarding-Oberflächen vor dem Laden der
  Laufzeit prüfen können
- Alias- und Metadaten zum automatischen Aktivieren, die aufgelöst werden sollen, bevor die Plugin-Laufzeit geladen wird
- Kurzschrift-Metadaten zur Besitzerschaft von Modellfamilien, die das
  Plugin vor dem Laden der Laufzeit automatisch aktivieren sollen
- statische Snapshots der Fähigkeitsbesitzerschaft, die für die gebündelte Kompatibilitätsverdrahtung und
  Vertragsabdeckung verwendet werden
- kostengünstige Metadaten für QA-Runner, die der gemeinsame `openclaw qa`-Host
  prüfen kann, bevor die Plugin-Laufzeit geladen wird
- kanalspezifische Konfigurationsmetadaten, die in Katalog- und Validierungsoberflächen
  zusammengeführt werden sollen, ohne die Laufzeit zu laden
- Hinweise für die Konfigurations-UI

Verwenden Sie sie nicht für:

- das Registrieren von Laufzeitverhalten
- das Deklarieren von Code-Einstiegspunkten
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
  "description": "OpenRouter provider plugin",
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
      "choiceLabel": "OpenRouter API key",
      "groupId": "openrouter",
      "groupLabel": "OpenRouter",
      "optionKey": "openrouterApiKey",
      "cliFlag": "--openrouter-api-key",
      "cliOption": "--openrouter-api-key <key>",
      "cliDescription": "OpenRouter API key",
      "onboardingScopes": ["text-inference"]
    }
  ],
  "uiHints": {
    "apiKey": {
      "label": "API key",
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
| `enabledByDefault`                  | Nein         | `true`                           | Kennzeichnet ein gebündeltes Plugin als standardmäßig aktiviert. Lassen Sie das Feld weg oder setzen Sie einen anderen Wert als `true`, damit das Plugin standardmäßig deaktiviert bleibt.                |
| `legacyPluginIds`                   | Nein         | `string[]`                       | Veraltete IDs, die auf diese kanonische Plugin-ID normalisiert werden.                                                                                                                                     |
| `autoEnableWhenConfiguredProviders` | Nein         | `string[]`                       | Provider-IDs, die dieses Plugin automatisch aktivieren sollen, wenn Authentifizierung, Konfiguration oder Modellreferenzen sie erwähnen.                                                                  |
| `kind`                              | Nein         | `"memory"` \| `"context-engine"` | Deklariert eine exklusive Plugin-Art, die von `plugins.slots.*` verwendet wird.                                                                                                                            |
| `channels`                          | Nein         | `string[]`                       | Kanal-IDs, die diesem Plugin gehören. Werden für Erkennung und Konfigurationsvalidierung verwendet.                                                                                                        |
| `providers`                         | Nein         | `string[]`                       | Provider-IDs, die diesem Plugin gehören.                                                                                                                                                                    |
| `modelSupport`                      | Nein         | `object`                         | Manifest-eigene Kurzschrift-Metadaten für Modellfamilien, mit denen das Plugin vor der Laufzeit automatisch geladen wird.                                                                                 |
| `cliBackends`                       | Nein         | `string[]`                       | CLI-Inferenz-Backend-IDs, die diesem Plugin gehören. Werden für die automatische Aktivierung beim Start aus expliziten Konfigurationsreferenzen verwendet.                                                |
| `commandAliases`                    | Nein         | `object[]`                       | Befehlsnamen, die diesem Plugin gehören und vor dem Laden der Laufzeit pluginbewusste Konfigurations- und CLI-Diagnosen erzeugen sollen.                                                                  |
| `providerAuthEnvVars`               | Nein         | `Record<string, string[]>`       | Kostengünstige Umgebungsmetadaten zur Provider-Authentifizierung, die OpenClaw ohne Laden von Plugin-Code prüfen kann.                                                                                    |
| `providerAuthAliases`               | Nein         | `Record<string, string>`         | Provider-IDs, die für die Authentifizierung eine andere Provider-ID wiederverwenden sollen, z. B. ein Coding-Provider, der denselben API-Schlüssel und dieselben Authentifizierungsprofile nutzt.        |
| `channelEnvVars`                    | Nein         | `Record<string, string[]>`       | Kostengünstige Kanal-Umgebungsmetadaten, die OpenClaw ohne Laden von Plugin-Code prüfen kann. Verwenden Sie dies für umgebungsgetriebene Kanal-Setups oder Authentifizierungsoberflächen, die generische Start-/Konfigurationshilfen sehen sollen. |
| `providerAuthChoices`               | Nein         | `object[]`                       | Kostengünstige Metadaten für Authentifizierungsoptionen für Onboarding-Auswahlen, bevorzugte Provider-Auflösung und einfache CLI-Flag-Verdrahtung.                                                       |
| `activation`                        | Nein         | `object`                         | Kostengünstige Aktivierungshinweise für provider-, befehls-, kanal-, routen- und fähigkeitsgetriggertes Laden. Nur Metadaten; das tatsächliche Verhalten gehört weiterhin der Plugin-Laufzeit.          |
| `setup`                             | Nein         | `object`                         | Kostengünstige Setup-/Onboarding-Deskriptoren, die Erkennungs- und Setup-Oberflächen ohne Laden der Plugin-Laufzeit prüfen können.                                                                       |
| `qaRunners`                         | Nein         | `object[]`                       | Kostengünstige QA-Runner-Deskriptoren, die vom gemeinsamen `openclaw qa`-Host verwendet werden, bevor die Plugin-Laufzeit geladen wird.                                                                  |
| `contracts`                         | Nein         | `object`                         | Statischer Snapshot gebündelter Fähigkeiten für Speech, Echtzeittranskription, Echtzeitstimme, Media Understanding, Bildgenerierung, Musikgenerierung, Videogenerierung, Web-Fetch, Websuche und Tool-Besitzerschaft. |
| `channelConfigs`                    | Nein         | `Record<string, object>`         | Manifest-eigene Kanal-Konfigurationsmetadaten, die vor dem Laden der Laufzeit in Erkennungs- und Validierungsoberflächen zusammengeführt werden.                                                         |
| `skills`                            | Nein         | `string[]`                       | Zu ladende Skills-Verzeichnisse, relativ zum Plugin-Stammverzeichnis.                                                                                                                                       |
| `name`                              | Nein         | `string`                         | Menschenlesbarer Plugin-Name.                                                                                                                                                                               |
| `description`                       | Nein         | `string`                         | Kurze Zusammenfassung, die in Plugin-Oberflächen angezeigt wird.                                                                                                                                            |
| `version`                           | Nein         | `string`                         | Informative Plugin-Version.                                                                                                                                                                                 |
| `uiHints`                           | Nein         | `Record<string, object>`         | UI-Beschriftungen, Platzhalter und Sensitivitätshinweise für Konfigurationsfelder.                                                                                                                         |

## Referenz zu `providerAuthChoices`

Jeder Eintrag in `providerAuthChoices` beschreibt eine Onboarding- oder Authentifizierungsoption.
OpenClaw liest diese Informationen, bevor die Provider-Laufzeit geladen wird.

| Feld                  | Erforderlich | Typ                                             | Bedeutung                                                                                                  |
| --------------------- | ------------ | ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `provider`            | Ja           | `string`                                        | Provider-ID, zu der diese Option gehört.                                                                   |
| `method`              | Ja           | `string`                                        | ID der Authentifizierungsmethode, an die weitergeleitet werden soll.                                       |
| `choiceId`            | Ja           | `string`                                        | Stabile ID der Authentifizierungsoption, die von Onboarding- und CLI-Abläufen verwendet wird.             |
| `choiceLabel`         | Nein         | `string`                                        | Benutzerseitige Beschriftung. Wenn sie weggelassen wird, verwendet OpenClaw stattdessen `choiceId`.       |
| `choiceHint`          | Nein         | `string`                                        | Kurzer Hilfetext für die Auswahl.                                                                          |
| `assistantPriority`   | Nein         | `number`                                        | Niedrigere Werte werden in assistentengesteuerten interaktiven Auswahlen früher sortiert.                 |
| `assistantVisibility` | Nein         | `"visible"` \| `"manual-only"`                  | Blendet die Option in Assistenten-Auswahlen aus, erlaubt aber weiterhin die manuelle Auswahl über die CLI. |
| `deprecatedChoiceIds` | Nein         | `string[]`                                      | Veraltete Options-IDs, die Benutzer zu dieser Ersatzoption umleiten sollen.                               |
| `groupId`             | Nein         | `string`                                        | Optionale Gruppen-ID zum Gruppieren verwandter Optionen.                                                   |
| `groupLabel`          | Nein         | `string`                                        | Benutzerseitige Beschriftung für diese Gruppe.                                                             |
| `groupHint`           | Nein         | `string`                                        | Kurzer Hilfetext für die Gruppe.                                                                           |
| `optionKey`           | Nein         | `string`                                        | Interner Optionsschlüssel für einfache Authentifizierungsabläufe mit einem einzelnen Flag.                |
| `cliFlag`             | Nein         | `string`                                        | Name des CLI-Flags, z. B. `--openrouter-api-key`.                                                          |
| `cliOption`           | Nein         | `string`                                        | Vollständige Form der CLI-Option, z. B. `--openrouter-api-key <key>`.                                     |
| `cliDescription`      | Nein         | `string`                                        | Beschreibung, die in der CLI-Hilfe verwendet wird.                                                         |
| `onboardingScopes`    | Nein         | `Array<"text-inference" \| "image-generation">` | In welchen Onboarding-Oberflächen diese Option erscheinen soll. Wenn das Feld fehlt, ist der Standardwert `["text-inference"]`. |

## Referenz zu `commandAliases`

Verwenden Sie `commandAliases`, wenn ein Plugin einen Laufzeit-Befehlsnamen besitzt, den Benutzer
versehentlich in `plugins.allow` eintragen oder als CLI-Befehl auf oberster Ebene ausführen möchten. OpenClaw
verwendet diese Metadaten für Diagnosen, ohne Laufzeitcode des Plugins zu importieren.

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

| Feld         | Erforderlich | Typ               | Bedeutung                                                                     |
| ------------ | ------------ | ----------------- | ----------------------------------------------------------------------------- |
| `name`       | Ja           | `string`          | Befehlsname, der zu diesem Plugin gehört.                                     |
| `kind`       | Nein         | `"runtime-slash"` | Kennzeichnet den Alias als Chat-Slash-Befehl statt als CLI-Befehl auf oberster Ebene. |
| `cliCommand` | Nein         | `string`          | Zugehöriger CLI-Befehl auf oberster Ebene, der für CLI-Operationen vorgeschlagen werden soll, falls vorhanden. |

## Referenz zu `activation`

Verwenden Sie `activation`, wenn das Plugin kostengünstig deklarieren kann, welche Control-Plane-Ereignisse
es später aktivieren sollen.

## Referenz zu `qaRunners`

Verwenden Sie `qaRunners`, wenn ein Plugin einen oder mehrere Transport-Runner unter dem
gemeinsamen Stamm `openclaw qa` bereitstellt. Halten Sie diese Metadaten kostengünstig und statisch; die Plugin-
Laufzeit bleibt weiterhin für die tatsächliche CLI-Registrierung über eine schlanke
`runtime-api.ts`-Oberfläche zuständig, die `qaRunnerCliRegistrations` exportiert.

```json
{
  "qaRunners": [
    {
      "commandName": "matrix",
      "description": "Run the Docker-backed Matrix live QA lane against a disposable homeserver"
    }
  ]
}
```

| Feld          | Erforderlich | Typ      | Bedeutung                                                              |
| ------------- | ------------ | -------- | ---------------------------------------------------------------------- |
| `commandName` | Ja           | `string` | Unterbefehl unter `openclaw qa`, zum Beispiel `matrix`.                |
| `description` | Nein         | `string` | Fallback-Hilfetext, der verwendet wird, wenn der gemeinsame Host einen Stub-Befehl benötigt. |

Dieser Block enthält nur Metadaten. Er registriert kein Laufzeitverhalten und
ersetzt nicht `register(...)`, `setupEntry` oder andere Laufzeit-/Plugin-Einstiegspunkte.
Aktuelle Verbraucher verwenden ihn als Eingrenzungshinweis vor einem breiteren Laden von Plugins, daher kosten
fehlende Aktivierungsmetadaten in der Regel nur Performance; sie sollten die Korrektheit
nicht verändern, solange die alten Fallbacks für Manifest-Besitzerschaft noch existieren.

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

| Feld             | Erforderlich | Typ                                                  | Bedeutung                                                              |
| ---------------- | ------------ | ---------------------------------------------------- | ---------------------------------------------------------------------- |
| `onProviders`    | Nein         | `string[]`                                           | Provider-IDs, die dieses Plugin aktivieren sollen, wenn sie angefordert werden. |
| `onCommands`     | Nein         | `string[]`                                           | Befehls-IDs, die dieses Plugin aktivieren sollen.                      |
| `onChannels`     | Nein         | `string[]`                                           | Kanal-IDs, die dieses Plugin aktivieren sollen.                        |
| `onRoutes`       | Nein         | `string[]`                                           | Routenarten, die dieses Plugin aktivieren sollen.                      |
| `onCapabilities` | Nein         | `Array<"provider" \| "channel" \| "tool" \| "hook">` | Allgemeine Fähigkeitshinweise, die von der Control-Plane-Aktivierungsplanung verwendet werden. |

Aktuelle Live-Verbraucher:

- befehlsgetriggerte CLI-Planung greift auf die alten Fallbacks
  `commandAliases[].cliCommand` oder `commandAliases[].name` zurück
- kanalgetriggerte Setup-/Kanal-Planung greift auf die alte Besitzerschaft über `channels[]`
  zurück, wenn explizite Kanal-Aktivierungsmetadaten fehlen
- providergetriggerte Setup-/Laufzeitplanung greift auf die alte
  Besitzerschaft über `providers[]` und `cliBackends[]` auf oberster Ebene zurück, wenn explizite Provider-
  Aktivierungsmetadaten fehlen

## Referenz zu `setup`

Verwenden Sie `setup`, wenn Setup- und Onboarding-Oberflächen kostengünstige plugin-eigene Metadaten
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

`cliBackends` auf oberster Ebene bleibt gültig und beschreibt weiterhin CLI-Inferenz-
Backends. `setup.cliBackends` ist die setupspezifische Deskriptoroberfläche für
Control-Plane-/Setup-Abläufe, die rein metadatenbasiert bleiben sollen.

Falls vorhanden, sind `setup.providers` und `setup.cliBackends` die bevorzugte
deskriptorbasierte Nachschlageoberfläche für die Setup-Erkennung. Wenn der Deskriptor nur
das Kandidaten-Plugin eingrenzt und das Setup weiterhin umfangreichere Laufzeit-Hooks zur Setup-Zeit
benötigt, setzen Sie `requiresRuntime: true` und lassen Sie `setup-api` als
Fallback-Ausführungspfad bestehen.

Da die Setup-Nachschlageoperation plugin-eigenen `setup-api`-Code ausführen kann, müssen normalisierte
Werte in `setup.providers[].id` und `setup.cliBackends[]` über alle
erkannten Plugins hinweg eindeutig bleiben. Mehrdeutige Besitzerschaft schlägt sicher fehl, anstatt anhand der
Erkennungsreihenfolge einen Gewinner auszuwählen.

### Referenz zu `setup.providers`

| Feld          | Erforderlich | Typ        | Bedeutung                                                                                 |
| ------------- | ------------ | ---------- | ----------------------------------------------------------------------------------------- |
| `id`          | Ja           | `string`   | Provider-ID, die während des Setups oder Onboardings bereitgestellt wird. Halten Sie normalisierte IDs global eindeutig. |
| `authMethods` | Nein         | `string[]` | Setup-/Authentifizierungsmethoden-IDs, die dieser Provider unterstützt, ohne die vollständige Laufzeit zu laden. |
| `envVars`     | Nein         | `string[]` | Umgebungsvariablen, die generische Setup-/Status-Oberflächen prüfen können, bevor die Plugin-Laufzeit geladen wird. |

### `setup`-Felder

| Feld               | Erforderlich | Typ        | Bedeutung                                                                                          |
| ------------------ | ------------ | ---------- | -------------------------------------------------------------------------------------------------- |
| `providers`        | Nein         | `object[]` | Provider-Setup-Deskriptoren, die während Setup und Onboarding bereitgestellt werden.               |
| `cliBackends`      | Nein         | `string[]` | Backend-IDs zur Setup-Zeit, die für die deskriptorbasierte Setup-Nachschlageoperation verwendet werden. Halten Sie normalisierte IDs global eindeutig. |
| `configMigrations` | Nein         | `string[]` | IDs von Konfigurationsmigrationen, die der Setup-Oberfläche dieses Plugins gehören.                |
| `requiresRuntime`  | Nein         | `boolean`  | Ob das Setup nach der Deskriptor-Nachschlageoperation weiterhin die Ausführung von `setup-api` benötigt. |

## Referenz zu `uiHints`

`uiHints` ist eine Zuordnung von Konfigurationsfeldnamen zu kleinen Rendering-Hinweisen.

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
| `label`       | `string`   | Benutzerseitige Feldbeschriftung.         |
| `help`        | `string`   | Kurzer Hilfetext.                         |
| `tags`        | `string[]` | Optionale UI-Tags.                        |
| `advanced`    | `boolean`  | Kennzeichnet das Feld als erweitert.      |
| `sensitive`   | `boolean`  | Kennzeichnet das Feld als geheim oder sensibel. |
| `placeholder` | `string`   | Platzhaltertext für Formulareingaben.     |

## Referenz zu `contracts`

Verwenden Sie `contracts` nur für statische Metadaten zur Fähigkeitsbesitzerschaft, die OpenClaw
lesen kann, ohne die Plugin-Laufzeit zu importieren.

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

| Feld                             | Typ        | Bedeutung                                                             |
| -------------------------------- | ---------- | --------------------------------------------------------------------- |
| `speechProviders`                | `string[]` | Speech-Provider-IDs, die diesem Plugin gehören.                       |
| `realtimeTranscriptionProviders` | `string[]` | IDs von Realtime-Transkriptions-Providern, die diesem Plugin gehören. |
| `realtimeVoiceProviders`         | `string[]` | IDs von Realtime-Voice-Providern, die diesem Plugin gehören.          |
| `mediaUnderstandingProviders`    | `string[]` | IDs von Media-Understanding-Providern, die diesem Plugin gehören.     |
| `imageGenerationProviders`       | `string[]` | IDs von Bildgenerierungs-Providern, die diesem Plugin gehören.        |
| `videoGenerationProviders`       | `string[]` | IDs von Videogenerierungs-Providern, die diesem Plugin gehören.       |
| `webFetchProviders`              | `string[]` | IDs von Web-Fetch-Providern, die diesem Plugin gehören.               |
| `webSearchProviders`             | `string[]` | IDs von Websuch-Providern, die diesem Plugin gehören.                 |
| `tools`                          | `string[]` | Namen von Agent-Tools, die diesem Plugin für gebündelte Vertragsprüfungen gehören. |

## Referenz zu `channelConfigs`

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
      "description": "Matrix homeserver connection",
      "preferOver": ["matrix-legacy"]
    }
  }
}
```

Jeder Kanaleintrag kann Folgendes enthalten:

| Feld          | Typ                      | Bedeutung                                                                                 |
| ------------- | ------------------------ | ----------------------------------------------------------------------------------------- |
| `schema`      | `object`                 | JSON-Schema für `channels.<id>`. Für jeden deklarierten Kanal-Konfigurationseintrag erforderlich. |
| `uiHints`     | `Record<string, object>` | Optionale UI-Beschriftungen/Platzhalter/Sensitivitätshinweise für diesen Abschnitt der Kanalkonfiguration. |
| `label`       | `string`                 | Kanalbeschriftung, die in Auswahl- und Prüfoberflächen zusammengeführt wird, wenn Laufzeitmetadaten noch nicht bereit sind. |
| `description` | `string`                 | Kurze Kanalbeschreibung für Prüf- und Katalogoberflächen.                                 |
| `preferOver`  | `string[]`               | Veraltete oder niedriger priorisierte Plugin-IDs, die dieser Kanal in Auswahloberflächen übertreffen soll. |

## Referenz zu `modelSupport`

Verwenden Sie `modelSupport`, wenn OpenClaw Ihr Provider-Plugin aus
Kurzschrift-Modell-IDs wie `gpt-5.4` oder `claude-sonnet-4.6` ableiten soll, bevor die Plugin-Laufzeit
geladen wird.

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

OpenClaw wendet folgende Rangfolge an:

- explizite Referenzen im Format `provider/model` verwenden die Manifest-Metadaten des besitzenden `providers`
- `modelPatterns` haben Vorrang vor `modelPrefixes`
- wenn ein nicht gebündeltes Plugin und ein gebündeltes Plugin beide passen, gewinnt das nicht gebündelte
  Plugin
- verbleibende Mehrdeutigkeiten werden ignoriert, bis der Benutzer oder die Konfiguration einen Provider angibt

Felder:

| Feld            | Typ        | Bedeutung                                                                      |
| --------------- | ---------- | ------------------------------------------------------------------------------ |
| `modelPrefixes` | `string[]` | Präfixe, die mit `startsWith` gegen Kurzschrift-Modell-IDs abgeglichen werden. |
| `modelPatterns` | `string[]` | Regex-Quellen, die nach dem Entfernen von Profilsuffixen gegen Kurzschrift-Modell-IDs abgeglichen werden. |

Veraltete Fähigkeiten-Schlüssel auf oberster Ebene sind deprecated. Verwenden Sie `openclaw doctor --fix`, um
`speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`,
`webFetchProviders` und `webSearchProviders` unter `contracts` zu
verschieben; das normale Laden von Manifesten behandelt diese Felder auf oberster Ebene nicht mehr als
Fähigkeitsbesitzerschaft.

## Manifest im Vergleich zu `package.json`

Die beiden Dateien erfüllen unterschiedliche Aufgaben:

| Datei                  | Verwendung                                                                                                                             |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.plugin.json` | Erkennung, Konfigurationsvalidierung, Metadaten für Authentifizierungsoptionen und UI-Hinweise, die vorhanden sein müssen, bevor Plugin-Code ausgeführt wird |
| `package.json`         | npm-Metadaten, Abhängigkeitsinstallation und der Block `openclaw`, der für Einstiegspunkte, Installationssteuerung, Setup oder Katalogmetadaten verwendet wird |

Wenn Sie unsicher sind, wohin ein Metadatenelement gehört, verwenden Sie diese Regel:

- wenn OpenClaw es wissen muss, bevor Plugin-Code geladen wird, gehört es in `openclaw.plugin.json`
- wenn es um Packaging, Einstiegsdateien oder das npm-Installationsverhalten geht, gehört es in `package.json`

### `package.json`-Felder, die die Erkennung beeinflussen

Einige Metadaten für Plugins vor der Laufzeit liegen absichtlich in `package.json` unter dem Block
`openclaw` statt in `openclaw.plugin.json`.

Wichtige Beispiele:

| Feld                                                              | Bedeutung                                                                                                                                   |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                             | Deklariert native Plugin-Einstiegspunkte.                                                                                                   |
| `openclaw.setupEntry`                                             | Leichtgewichtiger Einstiegspunkt nur für das Setup, der während des Onboardings und beim verzögerten Kanalstart verwendet wird.            |
| `openclaw.channel`                                                | Kostengünstige Metadaten für den Kanalkatalog wie Beschriftungen, Dokumentationspfade, Aliase und Auswahltexte.                            |
| `openclaw.channel.configuredState`                                | Kostengünstige Metadaten für den Prüfer des konfigurierten Zustands, der die Frage „existiert bereits ein nur über Umgebungsvariablen eingerichtetes Setup?“ beantworten kann, ohne die vollständige Kanal-Laufzeit zu laden. |
| `openclaw.channel.persistedAuthState`                             | Kostengünstige Metadaten für den Prüfer des persistenten Authentifizierungszustands, der die Frage „ist bereits irgendwo eine Anmeldung vorhanden?“ beantworten kann, ohne die vollständige Kanal-Laufzeit zu laden. |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | Installations-/Aktualisierungshinweise für gebündelte und extern veröffentlichte Plugins.                                                  |
| `openclaw.install.defaultChoice`                                  | Bevorzugter Installationspfad, wenn mehrere Installationsquellen verfügbar sind.                                                           |
| `openclaw.install.minHostVersion`                                 | Minimal unterstützte OpenClaw-Host-Version unter Verwendung einer SemVer-Untergrenze wie `>=2026.3.22`.                                    |
| `openclaw.install.allowInvalidConfigRecovery`                     | Erlaubt einen eng begrenzten Wiederherstellungspfad zur Neuinstallation gebündelter Plugins, wenn die Konfiguration ungültig ist.         |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | Ermöglicht, dass Setup-only-Kanaloberflächen vor dem vollständigen Kanal-Plugin beim Start geladen werden.                                 |

`openclaw.install.minHostVersion` wird während der Installation und beim Laden der Manifest-
Registry erzwungen. Ungültige Werte werden abgelehnt; neuere, aber gültige Werte überspringen das
Plugin auf älteren Hosts.

`openclaw.install.allowInvalidConfigRecovery` ist absichtlich eng begrenzt. Es
macht nicht beliebige fehlerhafte Konfigurationen installierbar. Derzeit erlaubt es Installations-
Abläufen nur, sich von bestimmten veralteten Upgrade-Fehlern gebündelter Plugins zu erholen, etwa einem
fehlenden Pfad zu einem gebündelten Plugin oder einem veralteten Eintrag `channels.<id>` für dasselbe
gebündelte Plugin. Nicht zusammenhängende Konfigurationsfehler blockieren die Installation weiterhin und schicken Operatoren
zu `openclaw doctor --fix`.

`openclaw.channel.persistedAuthState` ist Paketmetadaten für ein kleines
Prüfmodul:

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

Verwenden Sie es, wenn Setup-, Doctor- oder Prüfabläufe des konfigurierten Zustands eine kostengünstige Ja/Nein-
Authentifizierungsprüfung benötigen, bevor das vollständige Kanal-Plugin geladen wird. Das Zielexportobjekt sollte eine kleine
Funktion sein, die nur den persistenten Zustand liest; leiten Sie es nicht über das vollständige
Kanal-Laufzeit-Barrel.

`openclaw.channel.configuredState` folgt derselben Form für kostengünstige
Prüfungen eines nur über Umgebungsvariablen konfigurierten Zustands:

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

Verwenden Sie es, wenn ein Kanal den konfigurierten Zustand anhand von Umgebungsvariablen oder anderen kleinen
Nicht-Laufzeit-Eingaben beantworten kann. Wenn die Prüfung die vollständige Konfigurationsauflösung oder die echte
Kanal-Laufzeit benötigt, belassen Sie diese Logik stattdessen im Hook `config.hasConfiguredState`
des Plugins.

## JSON-Schema-Anforderungen

- **Jedes Plugin muss ein JSON-Schema bereitstellen**, auch wenn es keine Konfiguration akzeptiert.
- Ein leeres Schema ist zulässig, zum Beispiel `{ "type": "object", "additionalProperties": false }`.
- Schemas werden beim Lesen/Schreiben der Konfiguration validiert, nicht zur Laufzeit.

## Validierungsverhalten

- Unbekannte Schlüssel in `channels.*` sind **Fehler**, es sei denn, die Kanal-ID wird von
  einem Plugin-Manifest deklariert.
- `plugins.entries.<id>`, `plugins.allow`, `plugins.deny` und `plugins.slots.*`
  müssen auf **erkennbare** Plugin-IDs verweisen. Unbekannte IDs sind **Fehler**.
- Wenn ein Plugin installiert ist, aber ein fehlerhaftes oder fehlendes Manifest oder Schema hat,
  schlägt die Validierung fehl und Doctor meldet den Plugin-Fehler.
- Wenn eine Plugin-Konfiguration vorhanden ist, das Plugin aber **deaktiviert** ist, bleibt die Konfiguration erhalten und
  in Doctor sowie in den Logs wird eine **Warnung** angezeigt.

Die vollständige `plugins.*`-Schema-Referenz finden Sie unter [Konfigurationsreferenz](/de/gateway/configuration).

## Hinweise

- Das Manifest ist **für native OpenClaw-Plugins erforderlich**, einschließlich lokaler Dateisystem-Ladevorgänge.
- Die Laufzeit lädt das Plugin-Modul weiterhin separat; das Manifest dient nur
  der Erkennung und Validierung.
- Native Manifeste werden mit JSON5 geparst, daher werden Kommentare, nachgestellte Kommas und
  nicht in Anführungszeichen gesetzte Schlüssel akzeptiert, solange der endgültige Wert weiterhin ein Objekt ist.
- Nur dokumentierte Manifestfelder werden vom Manifest-Loader gelesen. Vermeiden Sie es,
  hier benutzerdefinierte Schlüssel auf oberster Ebene hinzuzufügen.
- `providerAuthEnvVars` ist der kostengünstige Metadatenpfad für Authentifizierungsprüfungen, die Validierung von
  Umgebungsmarkern und ähnliche Oberflächen zur Provider-Authentifizierung, die die Plugin-
  Laufzeit nicht starten sollten, nur um Umgebungsvariablennamen zu prüfen.
- `providerAuthAliases` ermöglicht es Provider-Varianten, die
  Authentifizierungs-Umgebungsvariablen, Authentifizierungsprofile, konfigurationsgestützte Authentifizierung und die
  Onboarding-Option für API-Schlüssel eines anderen Providers wiederzuverwenden, ohne diese Beziehung im Core fest zu codieren.
- `channelEnvVars` ist der kostengünstige Metadatenpfad für Shell-Umgebungsfallbacks, Setup-
  Aufforderungen und ähnliche Kanaloberflächen, die die Plugin-Laufzeit nicht starten sollten,
  nur um Umgebungsvariablennamen zu prüfen.
- `providerAuthChoices` ist der kostengünstige Metadatenpfad für Auswahlen von Authentifizierungsoptionen,
  die Auflösung von `--auth-choice`, die Zuordnung bevorzugter Provider und die einfache Registrierung von
  CLI-Flags für das Onboarding, bevor die Provider-Laufzeit geladen wird. Informationen zu Laufzeit-
  Wizard-Metadaten, die Provider-Code erfordern, finden Sie unter
  [Provider-Laufzeit-Hooks](/de/plugins/architecture#provider-runtime-hooks).
- Exklusive Plugin-Arten werden über `plugins.slots.*` ausgewählt.
  - `kind: "memory"` wird durch `plugins.slots.memory` ausgewählt.
  - `kind: "context-engine"` wird durch `plugins.slots.contextEngine`
    ausgewählt (Standard: eingebautes `legacy`).
- `channels`, `providers`, `cliBackends` und `skills` können weggelassen werden, wenn ein
  Plugin sie nicht benötigt.
- Wenn Ihr Plugin von nativen Modulen abhängt, dokumentieren Sie die Build-Schritte und alle
  Anforderungen an Zulassungslisten des Paketmanagers (zum Beispiel pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`).

## Verwandt

- [Plugins erstellen](/de/plugins/building-plugins) — Erste Schritte mit Plugins
- [Plugin-Architektur](/de/plugins/architecture) — interne Architektur
- [SDK-Überblick](/de/plugins/sdk-overview) — Referenz zum Plugin-SDK
