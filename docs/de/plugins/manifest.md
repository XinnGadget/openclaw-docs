---
read_when:
    - Sie erstellen ein OpenClaw-Plugin
    - Sie müssen ein Plugin-Konfigurationsschema bereitstellen oder Fehler bei der Plugin-Validierung debuggen
summary: Anforderungen an Plugin-Manifest + JSON-Schema (strikte Konfigurationsvalidierung)
title: Plugin-Manifest
x-i18n:
    generated_at: "2026-04-09T01:29:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9a7ee4b621a801d2a8f32f8976b0e1d9433c7810eb360aca466031fc0ffb286a
    source_path: plugins/manifest.md
    workflow: 15
---

# Plugin-Manifest (openclaw.plugin.json)

Diese Seite gilt nur für das **native OpenClaw-Plugin-Manifest**.

Kompatible Bundle-Layouts finden Sie unter [Plugin-Bundles](/de/plugins/bundles).

Kompatible Bundle-Formate verwenden andere Manifestdateien:

- Codex-Bundle: `.codex-plugin/plugin.json`
- Claude-Bundle: `.claude-plugin/plugin.json` oder das standardmäßige Claude-Komponenten-
  Layout ohne Manifest
- Cursor-Bundle: `.cursor-plugin/plugin.json`

OpenClaw erkennt diese Bundle-Layouts ebenfalls automatisch, sie werden jedoch nicht
gegen das hier beschriebene Schema von `openclaw.plugin.json` validiert.

Für kompatible Bundles liest OpenClaw derzeit Bundle-Metadaten sowie deklarierte
Skill-Stammverzeichnisse, Claude-Befehlsstammverzeichnisse, Standardwerte aus
`settings.json` für Claude-Bundles, Standardwerte für Claude-Bundle-LSPs
und unterstützte Hook-Packs, wenn das Layout den Laufzeiterwartungen von
OpenClaw entspricht.

Jedes native OpenClaw-Plugin **muss** eine Datei `openclaw.plugin.json` im
**Plugin-Stammverzeichnis** bereitstellen. OpenClaw verwendet dieses Manifest, um die Konfiguration
**ohne Ausführung von Plugin-Code** zu validieren. Fehlende oder ungültige Manifeste werden als
Plugin-Fehler behandelt und blockieren die Konfigurationsvalidierung.

Den vollständigen Leitfaden zum Plugin-System finden Sie unter: [Plugins](/de/tools/plugin).
Zum nativen Fähigkeitsmodell und den aktuellen Hinweisen zur externen Kompatibilität:
[Fähigkeitsmodell](/de/plugins/architecture#public-capability-model).

## Wozu diese Datei dient

`openclaw.plugin.json` sind die Metadaten, die OpenClaw liest, bevor Ihr
Plugin-Code geladen wird.

Verwenden Sie sie für:

- Plugin-Identität
- Konfigurationsvalidierung
- Auth- und Onboarding-Metadaten, die verfügbar sein sollen, ohne die Plugin-
  Laufzeit zu starten
- Alias- und Autoaktivierungs-Metadaten, die aufgelöst werden sollen, bevor die
  Plugin-Laufzeit geladen wird
- Kurzform-Metadaten zur Modellfamilien-Zugehörigkeit, die das
  Plugin vor dem Laden der Laufzeit automatisch aktivieren sollen
- statische Snapshots zur Fähigkeitszuordnung, die für gebündelte Kompatibilitätsverdrahtung und
  Vertragsabdeckung verwendet werden
- kanalspezifische Konfigurationsmetadaten, die in Katalog- und Validierungsoberflächen
  zusammengeführt werden sollen, ohne die Laufzeit zu laden
- Hinweise für die Konfigurations-UI

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

| Feld                                | Erforderlich | Typ                              | Bedeutung                                                                                                                                                                                                    |
| ----------------------------------- | ------------ | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `id`                                | Ja           | `string`                         | Kanonische Plugin-ID. Dies ist die ID, die in `plugins.entries.<id>` verwendet wird.                                                                                                                        |
| `configSchema`                      | Ja           | `object`                         | Inline-JSON-Schema für die Konfiguration dieses Plugins.                                                                                                                                                     |
| `enabledByDefault`                  | Nein         | `true`                           | Kennzeichnet ein gebündeltes Plugin als standardmäßig aktiviert. Lassen Sie das Feld weg oder setzen Sie einen beliebigen Wert ungleich `true`, damit das Plugin standardmäßig deaktiviert bleibt.        |
| `legacyPluginIds`                   | Nein         | `string[]`                       | Legacy-IDs, die auf diese kanonische Plugin-ID normalisiert werden.                                                                                                                                          |
| `autoEnableWhenConfiguredProviders` | Nein         | `string[]`                       | Provider-IDs, die dieses Plugin automatisch aktivieren sollen, wenn Auth, Konfiguration oder Modellreferenzen sie erwähnen.                                                                                 |
| `kind`                              | Nein         | `"memory"` \| `"context-engine"` | Deklariert eine exklusive Plugin-Art, die von `plugins.slots.*` verwendet wird.                                                                                                                             |
| `channels`                          | Nein         | `string[]`                       | Kanal-IDs, die diesem Plugin gehören. Wird für Erkennung und Konfigurationsvalidierung verwendet.                                                                                                            |
| `providers`                         | Nein         | `string[]`                       | Provider-IDs, die diesem Plugin gehören.                                                                                                                                                                     |
| `modelSupport`                      | Nein         | `object`                         | Manifest-eigene Kurzform-Metadaten zu Modellfamilien, mit denen das Plugin vor der Laufzeit automatisch geladen wird.                                                                                       |
| `cliBackends`                       | Nein         | `string[]`                       | IDs von CLI-Inferenz-Backends, die diesem Plugin gehören. Wird für die automatische Aktivierung beim Start aus expliziten Konfigurationsreferenzen verwendet.                                              |
| `providerAuthEnvVars`               | Nein         | `Record<string, string[]>`       | Leichtgewichtige Metadaten zu Provider-Auth-Umgebungsvariablen, die OpenClaw ohne Laden von Plugin-Code prüfen kann.                                                                                        |
| `providerAuthAliases`               | Nein         | `Record<string, string>`         | Provider-IDs, die für die Auth-Suche eine andere Provider-ID wiederverwenden sollen, zum Beispiel ein Coding-Provider, der denselben API-Schlüssel und dieselben Auth-Profile wie der Basis-Provider teilt. |
| `channelEnvVars`                    | Nein         | `Record<string, string[]>`       | Leichtgewichtige Kanal-Metadaten zu Umgebungsvariablen, die OpenClaw ohne Laden von Plugin-Code prüfen kann. Verwenden Sie dies für umgebungsvariablengesteuerte Kanaleinrichtung oder Auth-Oberflächen, die generische Start-/Konfigurationshilfen sehen sollen. |
| `providerAuthChoices`               | Nein         | `object[]`                       | Leichtgewichtige Metadaten zu Auth-Auswahlen für Onboarding-Auswahlfelder, die Auflösung bevorzugter Provider und einfache Verdrahtung von CLI-Flags.                                                      |
| `contracts`                         | Nein         | `object`                         | Statischer Snapshot gebündelter Fähigkeiten für Sprach-, Echtzeit-Transkriptions-, Echtzeit-Sprach-, Medienverständnis-, Bildgenerierungs-, Musikgenerierungs-, Videogenerierungs-, Web-Fetch-, Web-Such- und Werkzeug-Zuständigkeit. |
| `channelConfigs`                    | Nein         | `Record<string, object>`         | Manifest-eigene Kanal-Konfigurationsmetadaten, die in Erkennungs- und Validierungsoberflächen zusammengeführt werden, bevor die Laufzeit geladen wird.                                                      |
| `skills`                            | Nein         | `string[]`                       | Skill-Verzeichnisse, die relativ zum Plugin-Stammverzeichnis geladen werden sollen.                                                                                                                          |
| `name`                              | Nein         | `string`                         | Menschenlesbarer Plugin-Name.                                                                                                                                                                                |
| `description`                       | Nein         | `string`                         | Kurze Zusammenfassung, die in Plugin-Oberflächen angezeigt wird.                                                                                                                                             |
| `version`                           | Nein         | `string`                         | Informative Plugin-Version.                                                                                                                                                                                  |
| `uiHints`                           | Nein         | `Record<string, object>`         | UI-Beschriftungen, Platzhalter und Hinweise zur Sensitivität für Konfigurationsfelder.                                                                                                                      |

## Referenz zu `providerAuthChoices`

Jeder Eintrag in `providerAuthChoices` beschreibt eine Onboarding- oder Auth-Auswahl.
OpenClaw liest diese, bevor die Provider-Laufzeit geladen wird.

| Feld                  | Erforderlich | Typ                                             | Bedeutung                                                                                                 |
| --------------------- | ------------ | ----------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `provider`            | Ja           | `string`                                        | Provider-ID, zu der diese Auswahl gehört.                                                                 |
| `method`              | Ja           | `string`                                        | ID der Auth-Methode, an die weitergeleitet wird.                                                          |
| `choiceId`            | Ja           | `string`                                        | Stabile ID der Auth-Auswahl, die von Onboarding- und CLI-Abläufen verwendet wird.                        |
| `choiceLabel`         | Nein         | `string`                                        | Benutzerseitige Beschriftung. Wenn weggelassen, greift OpenClaw auf `choiceId` zurück.                   |
| `choiceHint`          | Nein         | `string`                                        | Kurzer Hilfetext für das Auswahlfeld.                                                                     |
| `assistantPriority`   | Nein         | `number`                                        | Kleinere Werte werden in assistantgesteuerten interaktiven Auswahlfeldern früher sortiert.               |
| `assistantVisibility` | Nein         | `"visible"` \| `"manual-only"`                  | Blendet die Auswahl in Assistant-Auswahlfeldern aus, erlaubt aber weiterhin die manuelle Auswahl per CLI. |
| `deprecatedChoiceIds` | Nein         | `string[]`                                      | Legacy-IDs für Auswahlen, die Benutzer auf diese Ersatz-Auswahl umleiten sollen.                         |
| `groupId`             | Nein         | `string`                                        | Optionale Gruppen-ID zum Gruppieren verwandter Auswahlen.                                                |
| `groupLabel`          | Nein         | `string`                                        | Benutzerseitige Beschriftung für diese Gruppe.                                                            |
| `groupHint`           | Nein         | `string`                                        | Kurzer Hilfetext für die Gruppe.                                                                          |
| `optionKey`           | Nein         | `string`                                        | Interner Optionsschlüssel für einfache Auth-Abläufe mit nur einem Flag.                                  |
| `cliFlag`             | Nein         | `string`                                        | Name des CLI-Flags, etwa `--openrouter-api-key`.                                                          |
| `cliOption`           | Nein         | `string`                                        | Vollständige Form der CLI-Option, etwa `--openrouter-api-key <key>`.                                     |
| `cliDescription`      | Nein         | `string`                                        | Beschreibung, die in der CLI-Hilfe verwendet wird.                                                       |
| `onboardingScopes`    | Nein         | `Array<"text-inference" \| "image-generation">` | In welchen Onboarding-Oberflächen diese Auswahl erscheinen soll. Wenn weggelassen, lautet der Standard `["text-inference"]`. |

## Referenz zu `uiHints`

`uiHints` ist eine Zuordnung von Namen von Konfigurationsfeldern zu kleinen Darstellungs-Hinweisen.

```json
{
  "uiHints": {
    "apiKey": {
      "label": "API-Schlüssel",
      "help": "Wird für OpenRouter-Anfragen verwendet",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  }
}
```

Jeder Feldhinweis kann Folgendes enthalten:

| Feld          | Typ        | Bedeutung                               |
| ------------- | ---------- | --------------------------------------- |
| `label`       | `string`   | Benutzerseitige Feldbeschriftung.       |
| `help`        | `string`   | Kurzer Hilfetext.                       |
| `tags`        | `string[]` | Optionale UI-Tags.                      |
| `advanced`    | `boolean`  | Kennzeichnet das Feld als erweitert.    |
| `sensitive`   | `boolean`  | Kennzeichnet das Feld als geheim oder sensibel. |
| `placeholder` | `string`   | Platzhaltertext für Formulareingaben.   |

## Referenz zu `contracts`

Verwenden Sie `contracts` nur für statische Metadaten zur Fähigkeitszuordnung, die OpenClaw
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

| Feld                             | Typ        | Bedeutung                                                      |
| -------------------------------- | ---------- | -------------------------------------------------------------- |
| `speechProviders`                | `string[]` | IDs von Sprach-Providern, die diesem Plugin gehören.           |
| `realtimeTranscriptionProviders` | `string[]` | IDs von Echtzeit-Transkriptions-Providern, die diesem Plugin gehören. |
| `realtimeVoiceProviders`         | `string[]` | IDs von Echtzeit-Sprach-Providern, die diesem Plugin gehören.  |
| `mediaUnderstandingProviders`    | `string[]` | IDs von Providern für Medienverständnis, die diesem Plugin gehören. |
| `imageGenerationProviders`       | `string[]` | IDs von Bildgenerierungs-Providern, die diesem Plugin gehören. |
| `videoGenerationProviders`       | `string[]` | IDs von Videogenerierungs-Providern, die diesem Plugin gehören. |
| `webFetchProviders`              | `string[]` | IDs von Web-Fetch-Providern, die diesem Plugin gehören.        |
| `webSearchProviders`             | `string[]` | IDs von Web-Such-Providern, die diesem Plugin gehören.         |
| `tools`                          | `string[]` | Namen von Agentenwerkzeugen, die diesem Plugin für Prüfungen gebündelter Verträge gehören. |

## Referenz zu `channelConfigs`

Verwenden Sie `channelConfigs`, wenn ein Kanal-Plugin vor dem Laden der
Laufzeit leichtgewichtige Konfigurationsmetadaten benötigt.

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
          "label": "Homeserver-URL",
          "placeholder": "https://matrix.example.com"
        }
      },
      "label": "Matrix",
      "description": "Verbindung zum Matrix-Homeserver",
      "preferOver": ["matrix-legacy"]
    }
  }
}
```

Jeder Kanaleintrag kann Folgendes enthalten:

| Feld          | Typ                      | Bedeutung                                                                                  |
| ------------- | ------------------------ | ------------------------------------------------------------------------------------------ |
| `schema`      | `object`                 | JSON-Schema für `channels.<id>`. Für jeden deklarierten Kanal-Konfigurationseintrag erforderlich. |
| `uiHints`     | `Record<string, object>` | Optionale UI-Beschriftungen/Platzhalter/Hinweise zur Sensitivität für diesen Kanal-Konfigurationsabschnitt. |
| `label`       | `string`                 | Kanalbeschriftung, die in Auswahl- und Prüfoberflächen zusammengeführt wird, wenn Laufzeitmetadaten noch nicht bereit sind. |
| `description` | `string`                 | Kurze Kanalbeschreibung für Prüf- und Katalogoberflächen.                                 |
| `preferOver`  | `string[]`               | Legacy- oder Plugin-IDs mit niedrigerer Priorität, die dieser Kanal in Auswahloberflächen übertreffen soll. |

## Referenz zu `modelSupport`

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

OpenClaw wendet folgende Rangfolge an:

- explizite Referenzen `provider/model` verwenden die Manifest-Metadaten des zuständigen `providers`
- `modelPatterns` haben Vorrang vor `modelPrefixes`
- wenn sowohl ein nicht gebündeltes Plugin als auch ein gebündeltes Plugin passen, gewinnt das nicht gebündelte
  Plugin
- verbleibende Mehrdeutigkeit wird ignoriert, bis der Benutzer oder die Konfiguration einen Provider angibt

Felder:

| Feld            | Typ        | Bedeutung                                                                      |
| --------------- | ---------- | ------------------------------------------------------------------------------ |
| `modelPrefixes` | `string[]` | Präfixe, die mit `startsWith` gegen Kurzform-Modell-IDs abgeglichen werden.    |
| `modelPatterns` | `string[]` | Regex-Quellen, die nach dem Entfernen des Profilsuffixes gegen Kurzform-Modell-IDs abgeglichen werden. |

Legacy-Fähigkeitsschlüssel auf oberster Ebene sind veraltet. Verwenden Sie `openclaw doctor --fix`, um
`speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`,
`webFetchProviders` und `webSearchProviders` unter `contracts` zu
verschieben; das normale Laden des Manifests behandelt diese Felder auf oberster Ebene nicht mehr als
Zuständigkeit für Fähigkeiten.

## Manifest versus package.json

Die beiden Dateien erfüllen unterschiedliche Aufgaben:

| Datei                  | Verwenden Sie sie für                                                                                                                |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `openclaw.plugin.json` | Erkennung, Konfigurationsvalidierung, Metadaten zu Auth-Auswahlen und UI-Hinweise, die vorhanden sein müssen, bevor Plugin-Code ausgeführt wird |
| `package.json`         | npm-Metadaten, Abhängigkeitsinstallation und den Block `openclaw`, der für Einstiegspunkte, Installationssteuerung, Einrichtung oder Katalogmetadaten verwendet wird |

Wenn Sie nicht sicher sind, wohin ein Metadatum gehört, verwenden Sie diese Regel:

- wenn OpenClaw es kennen muss, bevor Plugin-Code geladen wird, gehört es in `openclaw.plugin.json`
- wenn es um Packaging, Einstiegsdateien oder das npm-Installationsverhalten geht, gehört es in `package.json`

### `package.json`-Felder, die die Erkennung beeinflussen

Einige Plugin-Metadaten vor der Laufzeit liegen absichtlich in `package.json` im
Block `openclaw` statt in `openclaw.plugin.json`.

Wichtige Beispiele:

| Feld                                                              | Bedeutung                                                                                                                                      |
| ----------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                             | Deklariert native Plugin-Einstiegspunkte.                                                                                                      |
| `openclaw.setupEntry`                                             | Leichtgewichtiger Einstiegspunkt nur für die Einrichtung, der während Onboarding und verzögertem Kanalstart verwendet wird.                  |
| `openclaw.channel`                                                | Leichtgewichtige Metadaten zum Kanalkatalog wie Beschriftungen, Dokumentationspfade, Aliase und Auswahltexte.                               |
| `openclaw.channel.configuredState`                                | Leichtgewichtige Metadaten für den Prüfer des konfigurierten Zustands, der beantworten kann: „Gibt es bereits eine rein umgebungsvariablenbasierte Einrichtung?“ ohne die vollständige Kanallaufzeit zu laden. |
| `openclaw.channel.persistedAuthState`                             | Leichtgewichtige Metadaten für den Prüfer des persistenten Auth-Zustands, der beantworten kann: „Ist bereits irgendetwas angemeldet?“ ohne die vollständige Kanallaufzeit zu laden. |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | Hinweise zur Installation/Aktualisierung für gebündelte und extern veröffentlichte Plugins.                                                  |
| `openclaw.install.defaultChoice`                                  | Bevorzugter Installationspfad, wenn mehrere Installationsquellen verfügbar sind.                                                             |
| `openclaw.install.minHostVersion`                                 | Mindestunterstützte OpenClaw-Hostversion mit einer Semver-Untergrenze wie `>=2026.3.22`.                                                     |
| `openclaw.install.allowInvalidConfigRecovery`                     | Erlaubt einen eng begrenzten Wiederherstellungspfad bei Neuinstallation gebündelter Plugins, wenn die Konfiguration ungültig ist.           |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | Ermöglicht das Laden von Kanaloberflächen nur für die Einrichtung vor dem vollständigen Kanal-Plugin beim Start.                             |

`openclaw.install.minHostVersion` wird während der Installation und beim Laden der
Manifest-Registry erzwungen. Ungültige Werte werden abgelehnt; neuere, aber gültige Werte überspringen das
Plugin auf älteren Hosts.

`openclaw.install.allowInvalidConfigRecovery` ist absichtlich eng begrenzt. Es
macht nicht beliebige defekte Konfigurationen installierbar. Derzeit erlaubt es nur Installationsabläufen,
sich von bestimmten veralteten Upgrade-Fehlern gebündelter Plugins zu erholen, etwa bei einem
fehlenden gebündelten Plugin-Pfad oder einem veralteten Eintrag `channels.<id>` für dasselbe
gebündelte Plugin. Nicht zusammenhängende Konfigurationsfehler blockieren die Installation weiterhin und verweisen Betreiber an
`openclaw doctor --fix`.

`openclaw.channel.persistedAuthState` ist Package-Metadaten für ein kleines
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

Verwenden Sie dies, wenn Einrichtung, Doctor oder Abläufe zum konfigurierten Zustand
eine leichte Ja/Nein-Auth-Prüfung benötigen, bevor das vollständige Kanal-Plugin geladen wird. Das Zielexport
sollte eine kleine Funktion sein, die nur den persistenten Zustand liest; leiten Sie sie nicht über die vollständige
Barrel-Datei der Kanallaufzeit.

`openclaw.channel.configuredState` hat dieselbe Struktur für leichtgewichtige Prüfungen des
konfigurierten Zustands nur über Umgebungsvariablen:

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

Verwenden Sie dies, wenn ein Kanal den konfigurierten Zustand aus Umgebungsvariablen oder anderen kleinen
Nicht-Laufzeit-Eingaben bestimmen kann. Wenn die Prüfung eine vollständige Konfigurationsauflösung oder die echte
Kanallaufzeit benötigt, belassen Sie diese Logik stattdessen im Hook `config.hasConfiguredState`
des Plugins.

## JSON-Schema-Anforderungen

- **Jedes Plugin muss ein JSON-Schema bereitstellen**, auch wenn es keine Konfiguration akzeptiert.
- Ein leeres Schema ist zulässig (zum Beispiel `{ "type": "object", "additionalProperties": false }`).
- Schemata werden beim Lesen/Schreiben der Konfiguration validiert, nicht zur Laufzeit.

## Validierungsverhalten

- Unbekannte Schlüssel unter `channels.*` sind **Fehler**, es sei denn, die Kanal-ID wird durch
  ein Plugin-Manifest deklariert.
- `plugins.entries.<id>`, `plugins.allow`, `plugins.deny` und `plugins.slots.*`
  müssen auf **erkennbare** Plugin-IDs verweisen. Unbekannte IDs sind **Fehler**.
- Wenn ein Plugin installiert ist, aber ein defektes oder fehlendes Manifest oder Schema hat,
  schlägt die Validierung fehl und Doctor meldet den Plugin-Fehler.
- Wenn eine Plugin-Konfiguration vorhanden ist, das Plugin aber **deaktiviert** ist, bleibt die Konfiguration erhalten und
  es wird in Doctor und in den Logs eine **Warnung** angezeigt.

Unter [Konfigurationsreferenz](/de/gateway/configuration) finden Sie das vollständige Schema für `plugins.*`.

## Hinweise

- Das Manifest ist **für native OpenClaw-Plugins erforderlich**, einschließlich lokaler Dateisystem-Ladevorgänge.
- Die Laufzeit lädt das Plugin-Modul weiterhin separat; das Manifest dient nur zur
  Erkennung und Validierung.
- Native Manifeste werden mit JSON5 geparst, daher sind Kommentare, nachgestellte Kommas und
  nicht in Anführungszeichen gesetzte Schlüssel zulässig, solange der endgültige Wert weiterhin ein Objekt ist.
- Nur dokumentierte Manifestfelder werden vom Manifest-Loader gelesen. Vermeiden Sie es,
  hier benutzerdefinierte Schlüssel auf oberster Ebene hinzuzufügen.
- `providerAuthEnvVars` ist der leichtgewichtige Metadatenpfad für Auth-Prüfungen, Validierung von
  Umgebungsvariablen-Markern und ähnliche Oberflächen für Provider-Auth, die die Plugin-
  Laufzeit nicht nur zum Prüfen von Umgebungsvariablennamen starten sollten.
- `providerAuthAliases` erlaubt es Provider-Varianten, die Auth-
  Umgebungsvariablen, Auth-Profile, konfigurationsgestützte Auth und die Onboarding-Auswahl für API-Schlüssel
  eines anderen Providers wiederzuverwenden, ohne diese Beziehung im Core fest zu codieren.
- `channelEnvVars` ist der leichtgewichtige Metadatenpfad für Shell-Umgebungsvariablen-Fallbacks, Einrichtungs-
  Prompts und ähnliche Kanaloberflächen, die die Plugin-Laufzeit nicht
  nur zum Prüfen von Umgebungsvariablennamen starten sollten.
- `providerAuthChoices` ist der leichtgewichtige Metadatenpfad für Auswahlfelder zu Auth-Auswahlen,
  die Auflösung von `--auth-choice`, die Zuordnung bevorzugter Provider und die einfache Registrierung von
  CLI-Flags für Onboarding, bevor die Provider-Laufzeit geladen wird. Für Metadaten des Laufzeitassistenten,
  die Provider-Code erfordern, siehe
  [Provider-Laufzeit-Hooks](/de/plugins/architecture#provider-runtime-hooks).
- Exklusive Plugin-Arten werden über `plugins.slots.*` ausgewählt.
  - `kind: "memory"` wird durch `plugins.slots.memory` ausgewählt.
  - `kind: "context-engine"` wird durch `plugins.slots.contextEngine`
    ausgewählt (Standard: integriertes `legacy`).
- `channels`, `providers`, `cliBackends` und `skills` können weggelassen werden, wenn ein
  Plugin sie nicht benötigt.
- Wenn Ihr Plugin von nativen Modulen abhängt, dokumentieren Sie die Build-Schritte und etwaige
  Anforderungen an die Package-Manager-Allowlist (zum Beispiel pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`).

## Verwandt

- [Plugins erstellen](/de/plugins/building-plugins) — erste Schritte mit Plugins
- [Plugin-Architektur](/de/plugins/architecture) — interne Architektur
- [SDK-Überblick](/de/plugins/sdk-overview) — Referenz zum Plugin-SDK
