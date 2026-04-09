---
read_when:
    - Sie möchten Google-Gemini-Modelle mit OpenClaw verwenden
    - Sie benötigen den Auth-Ablauf mit API-Schlüssel oder OAuth
summary: Einrichtung von Google Gemini (API-Schlüssel + OAuth, Bildgenerierung, Medienverständnis, Websuche)
title: Google (Gemini)
x-i18n:
    generated_at: "2026-04-09T01:30:26Z"
    model: gpt-5.4
    provider: openai
    source_hash: fad2ff68987301bd86145fa6e10de8c7b38d5bd5dbcd13db9c883f7f5b9a4e01
    source_path: providers/google.md
    workflow: 15
---

# Google (Gemini)

Das Google-Plugin bietet Zugriff auf Gemini-Modelle über Google AI Studio sowie
Bildgenerierung, Medienverständnis (Bild/Audio/Video) und Websuche über
Gemini Grounding.

- Provider: `google`
- Auth: `GEMINI_API_KEY` oder `GOOGLE_API_KEY`
- API: Google Gemini API
- Alternativer Provider: `google-gemini-cli` (OAuth)

## Schnellstart

1. Setzen Sie den API-Schlüssel:

```bash
openclaw onboard --auth-choice gemini-api-key
```

2. Legen Sie ein Standardmodell fest:

```json5
{
  agents: {
    defaults: {
      model: { primary: "google/gemini-3.1-pro-preview" },
    },
  },
}
```

## Nicht interaktives Beispiel

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice gemini-api-key \
  --gemini-api-key "$GEMINI_API_KEY"
```

## OAuth (Gemini CLI)

Ein alternativer Provider `google-gemini-cli` verwendet PKCE-OAuth statt eines API-
Schlüssels. Dies ist eine inoffizielle Integration; einige Benutzer berichten von
Kontoeinschränkungen. Die Nutzung erfolgt auf eigenes Risiko.

- Standardmodell: `google-gemini-cli/gemini-3-flash-preview`
- Alias: `gemini-cli`
- Installationsvoraussetzung: lokale Gemini CLI, verfügbar als `gemini`
  - Homebrew: `brew install gemini-cli`
  - npm: `npm install -g @google/gemini-cli`
- Anmeldung:

```bash
openclaw models auth login --provider google-gemini-cli --set-default
```

Umgebungsvariablen:

- `OPENCLAW_GEMINI_OAUTH_CLIENT_ID`
- `OPENCLAW_GEMINI_OAUTH_CLIENT_SECRET`

(Oder die Varianten `GEMINI_CLI_*`.)

Wenn OAuth-Anfragen der Gemini CLI nach der Anmeldung fehlschlagen, setzen Sie
`GOOGLE_CLOUD_PROJECT` oder `GOOGLE_CLOUD_PROJECT_ID` auf dem Gateway-Host und
versuchen Sie es erneut.

Wenn die Anmeldung fehlschlägt, bevor der Browser-Ablauf startet, stellen Sie sicher, dass der lokale Befehl `gemini`
installiert ist und sich auf `PATH` befindet. OpenClaw unterstützt sowohl Homebrew-Installationen
als auch globale npm-Installationen, einschließlich gängiger Windows-/npm-Layouts.

Hinweise zur JSON-Nutzung der Gemini CLI:

- Der Antworttext stammt aus dem JSON-Feld `response` der CLI.
- Die Nutzung greift auf `stats` zurück, wenn die CLI `usage` leer lässt.
- `stats.cached` wird in OpenClaw-`cacheRead` normalisiert.
- Wenn `stats.input` fehlt, leitet OpenClaw die Eingabe-Token aus
  `stats.input_tokens - stats.cached` ab.

## Fähigkeiten

| Fähigkeit              | Unterstützt       |
| ---------------------- | ----------------- |
| Chat-Completions       | Ja                |
| Bildgenerierung        | Ja                |
| Musikgenerierung       | Ja                |
| Bildverständnis        | Ja                |
| Audio-Transkription    | Ja                |
| Videoverständnis       | Ja                |
| Websuche (Grounding)   | Ja                |
| Thinking/Reasoning     | Ja (Gemini 3.1+)  |
| Gemma 4-Modelle        | Ja                |

Gemma 4-Modelle (zum Beispiel `gemma-4-26b-a4b-it`) unterstützen den Thinking-Modus. OpenClaw schreibt `thinkingBudget` für Gemma 4 in ein unterstütztes Google-`thinkingLevel` um. Wenn Thinking auf `off` gesetzt wird, bleibt Thinking deaktiviert, statt auf `MINIMAL` abgebildet zu werden.

## Direkte Wiederverwendung des Gemini-Caches

Für direkte Gemini-API-Läufe (`api: "google-generative-ai"`) gibt OpenClaw jetzt
einen konfigurierten `cachedContent`-Handle an Gemini-Anfragen weiter.

- Konfigurieren Sie pro Modell oder global Parameter mit entweder
  `cachedContent` oder dem Legacy-Wert `cached_content`
- Wenn beide vorhanden sind, hat `cachedContent` Vorrang
- Beispielwert: `cachedContents/prebuilt-context`
- Die Nutzung bei Gemini-Cache-Treffern wird in OpenClaw-`cacheRead` aus
  `cachedContentTokenCount` des Upstreams normalisiert

Beispiel:

```json5
{
  agents: {
    defaults: {
      models: {
        "google/gemini-2.5-pro": {
          params: {
            cachedContent: "cachedContents/prebuilt-context",
          },
        },
      },
    },
  },
}
```

## Bildgenerierung

Der gebündelte Provider `google` für Bildgenerierung verwendet standardmäßig
`google/gemini-3.1-flash-image-preview`.

- Unterstützt auch `google/gemini-3-pro-image-preview`
- Generierung: bis zu 4 Bilder pro Anfrage
- Bearbeitungsmodus: aktiviert, bis zu 5 Eingabebilder
- Geometriesteuerungen: `size`, `aspectRatio` und `resolution`

Der nur per OAuth nutzbare Provider `google-gemini-cli` ist eine separate Oberfläche
für Textinferenz. Bildgenerierung, Medienverständnis und Gemini Grounding bleiben auf
der Provider-ID `google`.

So verwenden Sie Google als Standardprovider für Bilder:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "google/gemini-3.1-flash-image-preview",
      },
    },
  },
}
```

Unter [Bildgenerierung](/de/tools/image-generation) finden Sie die gemeinsamen Werkzeug-
Parameter, die Providerauswahl und das Failover-Verhalten.

## Videogenerierung

Das gebündelte Plugin `google` registriert außerdem Videogenerierung über das gemeinsame
Werkzeug `video_generate`.

- Standard-Videomodell: `google/veo-3.1-fast-generate-preview`
- Modi: Text-zu-Video-, Bild-zu-Video- und Referenzabläufe mit einem einzelnen Video
- Unterstützt `aspectRatio`, `resolution` und `audio`
- Aktuelle Begrenzung der Dauer: **4 bis 8 Sekunden**

So verwenden Sie Google als Standardprovider für Videos:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "google/veo-3.1-fast-generate-preview",
      },
    },
  },
}
```

Unter [Videogenerierung](/de/tools/video-generation) finden Sie die gemeinsamen Werkzeug-
Parameter, die Providerauswahl und das Failover-Verhalten.

## Musikgenerierung

Das gebündelte Plugin `google` registriert außerdem Musikgenerierung über das gemeinsame
Werkzeug `music_generate`.

- Standard-Musikmodell: `google/lyria-3-clip-preview`
- Unterstützt auch `google/lyria-3-pro-preview`
- Prompt-Steuerungen: `lyrics` und `instrumental`
- Ausgabeformat: standardmäßig `mp3`, zusätzlich `wav` bei `google/lyria-3-pro-preview`
- Referenzeingaben: bis zu 10 Bilder
- Sitzungsbasierte Läufe werden über den gemeinsamen Aufgaben-/Statusablauf abgekoppelt, einschließlich `action: "status"`

So verwenden Sie Google als Standardprovider für Musik:

```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "google/lyria-3-clip-preview",
      },
    },
  },
}
```

Unter [Musikgenerierung](/de/tools/music-generation) finden Sie die gemeinsamen Werkzeug-
Parameter, die Providerauswahl und das Failover-Verhalten.

## Hinweis zur Umgebung

Wenn das Gateway als Daemon (launchd/systemd) läuft, stellen Sie sicher, dass `GEMINI_API_KEY`
diesem Prozess zur Verfügung steht (zum Beispiel in `~/.openclaw/.env` oder über
`env.shellEnv`).
