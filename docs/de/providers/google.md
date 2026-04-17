---
read_when:
    - Sie möchten Google Gemini-Modelle mit OpenClaw verwenden.
    - Sie benötigen den API-Schlüssel oder den OAuth-Authentifizierungsablauf.
summary: Google Gemini-Einrichtung (API-Schlüssel + OAuth, Bildgenerierung, Medienverständnis, TTS, Websuche)
title: Google (Gemini)
x-i18n:
    generated_at: "2026-04-16T19:31:07Z"
    model: gpt-5.4
    provider: openai
    source_hash: ec2d62855f5e80efda758aad71bcaa95c38b1e41761fa1100d47a06c62881419
    source_path: providers/google.md
    workflow: 15
---

# Google (Gemini)

Das Google-Plugin bietet Zugriff auf Gemini-Modelle über Google AI Studio sowie
Bildgenerierung, Medienverständnis (Bild/Audio/Video), Text-to-Speech und Websuche über
Gemini Grounding.

- Anbieter: `google`
- Authentifizierung: `GEMINI_API_KEY` oder `GOOGLE_API_KEY`
- API: Google Gemini API
- Alternativer Anbieter: `google-gemini-cli` (OAuth)

## Erste Schritte

Wählen Sie Ihre bevorzugte Authentifizierungsmethode und befolgen Sie die Einrichtungsschritte.

<Tabs>
  <Tab title="API-Schlüssel">
    **Am besten geeignet für:** standardmäßigen Gemini-API-Zugriff über Google AI Studio.

    <Steps>
      <Step title="Onboarding ausführen">
        ```bash
        openclaw onboard --auth-choice gemini-api-key
        ```

        Oder den Schlüssel direkt übergeben:

        ```bash
        openclaw onboard --non-interactive \
          --mode local \
          --auth-choice gemini-api-key \
          --gemini-api-key "$GEMINI_API_KEY"
        ```
      </Step>
      <Step title="Ein Standardmodell festlegen">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "google/gemini-3.1-pro-preview" },
            },
          },
        }
        ```
      </Step>
      <Step title="Prüfen, ob das Modell verfügbar ist">
        ```bash
        openclaw models list --provider google
        ```
      </Step>
    </Steps>

    <Tip>
    Die Umgebungsvariablen `GEMINI_API_KEY` und `GOOGLE_API_KEY` werden beide unterstützt. Verwenden Sie diejenige, die Sie bereits konfiguriert haben.
    </Tip>

  </Tab>

  <Tab title="Gemini CLI (OAuth)">
    **Am besten geeignet für:** die Wiederverwendung einer bestehenden Gemini-CLI-Anmeldung über PKCE OAuth anstelle eines separaten API-Schlüssels.

    <Warning>
    Der Anbieter `google-gemini-cli` ist eine inoffizielle Integration. Einige Nutzer
    berichten von Kontoeinschränkungen, wenn OAuth auf diese Weise verwendet wird. Die Nutzung erfolgt auf eigenes Risiko.
    </Warning>

    <Steps>
      <Step title="Die Gemini CLI installieren">
        Der lokale Befehl `gemini` muss auf `PATH` verfügbar sein.

        ```bash
        # Homebrew
        brew install gemini-cli

        # oder npm
        npm install -g @google/gemini-cli
        ```

        OpenClaw unterstützt sowohl Homebrew-Installationen als auch globale npm-Installationen, einschließlich
        gängiger Windows/npm-Layouts.
      </Step>
      <Step title="Über OAuth anmelden">
        ```bash
        openclaw models auth login --provider google-gemini-cli --set-default
        ```
      </Step>
      <Step title="Prüfen, ob das Modell verfügbar ist">
        ```bash
        openclaw models list --provider google-gemini-cli
        ```
      </Step>
    </Steps>

    - Standardmodell: `google-gemini-cli/gemini-3-flash-preview`
    - Alias: `gemini-cli`

    **Umgebungsvariablen:**

    - `OPENCLAW_GEMINI_OAUTH_CLIENT_ID`
    - `OPENCLAW_GEMINI_OAUTH_CLIENT_SECRET`

    (Oder die Varianten `GEMINI_CLI_*`.)

    <Note>
    Wenn Gemini-CLI-OAuth-Anfragen nach der Anmeldung fehlschlagen, setzen Sie `GOOGLE_CLOUD_PROJECT` oder
    `GOOGLE_CLOUD_PROJECT_ID` auf dem Gateway-Host und versuchen Sie es erneut.
    </Note>

    <Note>
    Wenn die Anmeldung fehlschlägt, bevor der Browser-Ablauf startet, stellen Sie sicher, dass der lokale Befehl `gemini`
    installiert ist und sich auf `PATH` befindet.
    </Note>

    Der reine OAuth-Anbieter `google-gemini-cli` ist eine separate Oberfläche für Textinferenz.
    Bildgenerierung, Medienverständnis und Gemini Grounding bleiben auf der
    Anbieter-ID `google`.

  </Tab>
</Tabs>

## Fähigkeiten

| Fähigkeit              | Unterstützt       |
| ---------------------- | ----------------- |
| Chat-Completions       | Ja                |
| Bildgenerierung        | Ja                |
| Musikgenerierung       | Ja                |
| Text-to-Speech         | Ja                |
| Bildverständnis        | Ja                |
| Audiotranskription     | Ja                |
| Videoverständnis       | Ja                |
| Websuche (Grounding)   | Ja                |
| Thinking/Reasoning     | Ja (Gemini 3.1+)  |
| Gemma 4-Modelle        | Ja                |

<Tip>
Gemma 4-Modelle (zum Beispiel `gemma-4-26b-a4b-it`) unterstützen den Thinking-Modus. OpenClaw
schreibt `thinkingBudget` in ein unterstütztes Google-`thinkingLevel` für Gemma 4 um.
Wenn Thinking auf `off` gesetzt wird, bleibt Thinking deaktiviert, statt auf
`MINIMAL` abgebildet zu werden.
</Tip>

## Bildgenerierung

Der gebündelte Bildgenerierungsanbieter `google` verwendet standardmäßig
`google/gemini-3.1-flash-image-preview`.

- Unterstützt auch `google/gemini-3-pro-image-preview`
- Generierung: bis zu 4 Bilder pro Anfrage
- Bearbeitungsmodus: aktiviert, bis zu 5 Eingabebilder
- Geometriesteuerungen: `size`, `aspectRatio` und `resolution`

So verwenden Sie Google als Standardanbieter für Bilder:

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

<Note>
Siehe [Bildgenerierung](/de/tools/image-generation) für gemeinsame Tool-Parameter, Anbieterauswahl und Failover-Verhalten.
</Note>

## Videogenerierung

Das gebündelte `google`-Plugin registriert auch Videogenerierung über das gemeinsame
Tool `video_generate`.

- Standard-Videomodell: `google/veo-3.1-fast-generate-preview`
- Modi: Text-zu-Video-, Bild-zu-Video- und Einzelvideo-Referenzabläufe
- Unterstützt `aspectRatio`, `resolution` und `audio`
- Aktuelle Begrenzung der Dauer: **4 bis 8 Sekunden**

So verwenden Sie Google als Standardanbieter für Video:

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

<Note>
Siehe [Videogenerierung](/de/tools/video-generation) für gemeinsame Tool-Parameter, Anbieterauswahl und Failover-Verhalten.
</Note>

## Musikgenerierung

Das gebündelte `google`-Plugin registriert auch Musikgenerierung über das gemeinsame
Tool `music_generate`.

- Standard-Musikmodell: `google/lyria-3-clip-preview`
- Unterstützt auch `google/lyria-3-pro-preview`
- Prompt-Steuerungen: `lyrics` und `instrumental`
- Ausgabeformat: standardmäßig `mp3`, zusätzlich `wav` auf `google/lyria-3-pro-preview`
- Referenzeingaben: bis zu 10 Bilder
- Sitzungsbasierte Läufe werden über den gemeinsamen Task-/Status-Ablauf getrennt ausgeführt, einschließlich `action: "status"`

So verwenden Sie Google als Standardanbieter für Musik:

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

<Note>
Siehe [Musikgenerierung](/de/tools/music-generation) für gemeinsame Tool-Parameter, Anbieterauswahl und Failover-Verhalten.
</Note>

## Text-to-Speech

Der gebündelte Sprachanbieter `google` verwendet den Gemini-API-TTS-Pfad mit
`gemini-3.1-flash-tts-preview`.

- Standardstimme: `Kore`
- Authentifizierung: `messages.tts.providers.google.apiKey`, `models.providers.google.apiKey`, `GEMINI_API_KEY` oder `GOOGLE_API_KEY`
- Ausgabe: WAV für reguläre TTS-Anhänge, PCM für Talk/Telefonie
- Native Sprachnachrichten-Ausgabe: auf diesem Gemini-API-Pfad nicht unterstützt, da die API PCM statt Opus zurückgibt

So verwenden Sie Google als Standardanbieter für TTS:

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "google",
      providers: {
        google: {
          model: "gemini-3.1-flash-tts-preview",
          voiceName: "Kore",
        },
      },
    },
  },
}
```

Gemini API TTS akzeptiert ausdrucksstarke Audio-Tags in eckigen Klammern im Text, wie
`[whispers]` oder `[laughs]`. Um Tags aus der sichtbaren Chat-Antwort herauszuhalten und sie gleichzeitig
an TTS zu senden, setzen Sie sie in einen `[[tts:text]]...[[/tts:text]]`-Block:

```text
Hier ist der saubere Antworttext.

[[tts:text]][whispers] Hier ist die gesprochene Version.[[/tts:text]]
```

<Note>
Ein Google-Cloud-Console-API-Schlüssel, der auf die Gemini API beschränkt ist, ist für diesen
Anbieter gültig. Dies ist nicht der separate Cloud-Text-to-Speech-API-Pfad.
</Note>

## Erweiterte Konfiguration

<AccordionGroup>
  <Accordion title="Direkte Wiederverwendung des Gemini-Cache">
    Bei direkten Gemini-API-Läufen (`api: "google-generative-ai"`) gibt OpenClaw
    ein konfiguriertes `cachedContent`-Handle an Gemini-Anfragen weiter.

    - Konfigurieren Sie pro Modell oder global Parameter mit entweder
      `cachedContent` oder dem älteren `cached_content`
    - Wenn beide vorhanden sind, hat `cachedContent` Vorrang
    - Beispielwert: `cachedContents/prebuilt-context`
    - Die Gemini-Cache-Treffernutzung wird in OpenClaw-`cacheRead` normalisiert aus
      dem Upstream-Wert `cachedContentTokenCount`

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

  </Accordion>

  <Accordion title="Hinweise zur JSON-Nutzung der Gemini CLI">
    Bei Verwendung des OAuth-Anbieters `google-gemini-cli` normalisiert OpenClaw
    die JSON-Ausgabe der CLI wie folgt:

    - Der Antworttext stammt aus dem JSON-Feld `response` der CLI.
    - Die Nutzungsdaten greifen auf `stats` zurück, wenn die CLI `usage` leer lässt.
    - `stats.cached` wird in OpenClaw-`cacheRead` normalisiert.
    - Wenn `stats.input` fehlt, leitet OpenClaw Eingabetoken ab aus
      `stats.input_tokens - stats.cached`.

  </Accordion>

  <Accordion title="Umgebungs- und Daemon-Einrichtung">
    Wenn das Gateway als Daemon läuft (launchd/systemd), stellen Sie sicher, dass `GEMINI_API_KEY`
    diesem Prozess zur Verfügung steht (zum Beispiel in `~/.openclaw/.env` oder über
    `env.shellEnv`).
  </Accordion>
</AccordionGroup>

## Verwandte Themen

<CardGroup cols={2}>
  <Card title="Modellauswahl" href="/de/concepts/model-providers" icon="layers">
    Auswahl von Anbietern, Modell-Referenzen und Failover-Verhalten.
  </Card>
  <Card title="Bildgenerierung" href="/de/tools/image-generation" icon="image">
    Gemeinsame Bild-Tool-Parameter und Anbieterauswahl.
  </Card>
  <Card title="Videogenerierung" href="/de/tools/video-generation" icon="video">
    Gemeinsame Video-Tool-Parameter und Anbieterauswahl.
  </Card>
  <Card title="Musikgenerierung" href="/de/tools/music-generation" icon="music">
    Gemeinsame Musik-Tool-Parameter und Anbieterauswahl.
  </Card>
</CardGroup>
