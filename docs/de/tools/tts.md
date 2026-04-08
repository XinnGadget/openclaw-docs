---
read_when:
    - Aktivieren von Text-to-Speech für Antworten
    - Konfigurieren von TTS-Anbietern oder Limits
    - Verwenden von /tts-Befehlen
summary: Text-to-Speech (TTS) für ausgehende Antworten
title: Text-to-Speech
x-i18n:
    generated_at: "2026-04-08T06:02:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6e0fbcaf61282733c134f682e05a71f94d2169c03a85131ce9ad233c71a1e533
    source_path: tools/tts.md
    workflow: 15
---

# Text-to-Speech (TTS)

OpenClaw kann ausgehende Antworten mit ElevenLabs, Microsoft, MiniMax oder OpenAI in Audio umwandeln.
Es funktioniert überall dort, wo OpenClaw Audio senden kann.

## Unterstützte Dienste

- **ElevenLabs** (primärer oder Fallback-Anbieter)
- **Microsoft** (primärer oder Fallback-Anbieter; die aktuelle gebündelte Implementierung verwendet `node-edge-tts`)
- **MiniMax** (primärer oder Fallback-Anbieter; verwendet die T2A-v2-API)
- **OpenAI** (primärer oder Fallback-Anbieter; wird auch für Zusammenfassungen verwendet)

### Hinweise zu Microsoft Speech

Der gebündelte Microsoft-Speech-Anbieter verwendet derzeit den gehosteten
neuronalen TTS-Dienst von Microsoft Edge über die Bibliothek `node-edge-tts`. Es
handelt sich um einen gehosteten Dienst (nicht lokal), der Microsoft-Endpunkte
verwendet und keinen API-Schlüssel erfordert.
`node-edge-tts` stellt Sprachkonfigurationsoptionen und Ausgabeformate bereit,
aber nicht alle Optionen werden vom Dienst unterstützt. Alte Konfigurationen
und Direktiveneingaben mit `edge` funktionieren weiterhin und werden zu `microsoft` normalisiert.

Da dieser Pfad ein öffentlicher Webdienst ohne veröffentlichte SLA oder Quota
ist, sollte er als Best-Effort behandelt werden. Wenn Sie garantierte Limits
und Support benötigen, verwenden Sie OpenAI oder ElevenLabs.

## Optionale Schlüssel

Wenn Sie OpenAI, ElevenLabs oder MiniMax verwenden möchten:

- `ELEVENLABS_API_KEY` (oder `XI_API_KEY`)
- `MINIMAX_API_KEY`
- `OPENAI_API_KEY`

Microsoft Speech erfordert **keinen** API-Schlüssel.

Wenn mehrere Anbieter konfiguriert sind, wird der ausgewählte Anbieter zuerst verwendet und die anderen dienen als Fallback-Optionen.
Auto-Zusammenfassungen verwenden das konfigurierte `summaryModel` (oder `agents.defaults.model.primary`),
daher muss dieser Anbieter ebenfalls authentifiziert sein, wenn Sie Zusammenfassungen aktivieren.

## Dienst-Links

- [OpenAI Text-to-Speech guide](https://platform.openai.com/docs/guides/text-to-speech)
- [OpenAI Audio API reference](https://platform.openai.com/docs/api-reference/audio)
- [ElevenLabs Text to Speech](https://elevenlabs.io/docs/api-reference/text-to-speech)
- [ElevenLabs Authentication](https://elevenlabs.io/docs/api-reference/authentication)
- [MiniMax T2A v2 API](https://platform.minimaxi.com/document/T2A%20V2)
- [node-edge-tts](https://github.com/SchneeHertz/node-edge-tts)
- [Microsoft Speech output formats](https://learn.microsoft.com/azure/ai-services/speech-service/rest-text-to-speech#audio-outputs)

## Ist es standardmäßig aktiviert?

Nein. Auto‑TTS ist standardmäßig **deaktiviert**. Aktivieren Sie es in der Konfiguration mit
`messages.tts.auto` oder lokal mit `/tts on`.

Wenn `messages.tts.provider` nicht gesetzt ist, wählt OpenClaw den ersten konfigurierten
Speech-Anbieter in der Auto-Select-Reihenfolge der Registry aus.

## Konfiguration

Die TTS-Konfiguration befindet sich unter `messages.tts` in `openclaw.json`.
Das vollständige Schema finden Sie unter [Gateway-Konfiguration](/de/gateway/configuration).

### Minimale Konfiguration (Aktivieren + Anbieter)

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "elevenlabs",
    },
  },
}
```

### OpenAI primär mit ElevenLabs als Fallback

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "openai",
      summaryModel: "openai/gpt-4.1-mini",
      modelOverrides: {
        enabled: true,
      },
      providers: {
        openai: {
          apiKey: "openai_api_key",
          baseUrl: "https://api.openai.com/v1",
          model: "gpt-4o-mini-tts",
          voice: "alloy",
        },
        elevenlabs: {
          apiKey: "elevenlabs_api_key",
          baseUrl: "https://api.elevenlabs.io",
          voiceId: "voice_id",
          modelId: "eleven_multilingual_v2",
          seed: 42,
          applyTextNormalization: "auto",
          languageCode: "en",
          voiceSettings: {
            stability: 0.5,
            similarityBoost: 0.75,
            style: 0.0,
            useSpeakerBoost: true,
            speed: 1.0,
          },
        },
      },
    },
  },
}
```

### Microsoft primär (ohne API-Schlüssel)

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "microsoft",
      providers: {
        microsoft: {
          enabled: true,
          voice: "en-US-MichelleNeural",
          lang: "en-US",
          outputFormat: "audio-24khz-48kbitrate-mono-mp3",
          rate: "+10%",
          pitch: "-5%",
        },
      },
    },
  },
}
```

### MiniMax primär

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "minimax",
      providers: {
        minimax: {
          apiKey: "minimax_api_key",
          baseUrl: "https://api.minimax.io",
          model: "speech-2.8-hd",
          voiceId: "English_expressive_narrator",
          speed: 1.0,
          vol: 1.0,
          pitch: 0,
        },
      },
    },
  },
}
```

### Microsoft Speech deaktivieren

```json5
{
  messages: {
    tts: {
      providers: {
        microsoft: {
          enabled: false,
        },
      },
    },
  },
}
```

### Benutzerdefinierte Limits + prefs-Pfad

```json5
{
  messages: {
    tts: {
      auto: "always",
      maxTextLength: 4000,
      timeoutMs: 30000,
      prefsPath: "~/.openclaw/settings/tts.json",
    },
  },
}
```

### Nur nach einer eingehenden Sprachnachricht mit Audio antworten

```json5
{
  messages: {
    tts: {
      auto: "inbound",
    },
  },
}
```

### Auto-Zusammenfassung für lange Antworten deaktivieren

```json5
{
  messages: {
    tts: {
      auto: "always",
    },
  },
}
```

Führen Sie dann Folgendes aus:

```
/tts summary off
```

### Hinweise zu den Feldern

- `auto`: Auto‑TTS-Modus (`off`, `always`, `inbound`, `tagged`).
  - `inbound` sendet Audio nur nach einer eingehenden Sprachnachricht.
  - `tagged` sendet Audio nur, wenn die Antwort `[[tts]]`-Tags enthält.
- `enabled`: alter Schalter (doctor migriert dies zu `auto`).
- `mode`: `"final"` (Standard) oder `"all"` (einschließlich Tool-/Block-Antworten).
- `provider`: Speech-Anbieter-ID wie `"elevenlabs"`, `"microsoft"`, `"minimax"` oder `"openai"` (Fallback erfolgt automatisch).
- Wenn `provider` **nicht gesetzt** ist, verwendet OpenClaw den ersten konfigurierten Speech-Anbieter in der Auto-Select-Reihenfolge der Registry.
- Das alte `provider: "edge"` funktioniert weiterhin und wird zu `microsoft` normalisiert.
- `summaryModel`: optionales günstiges Modell für Auto-Zusammenfassungen; Standard ist `agents.defaults.model.primary`.
  - Akzeptiert `provider/model` oder einen konfigurierten Modellalias.
- `modelOverrides`: erlaubt dem Modell, TTS-Direktiven auszugeben (standardmäßig aktiviert).
  - `allowProvider` ist standardmäßig `false` (Anbieterwechsel ist Opt-in).
- `providers.<id>`: anbieterbezogene Einstellungen, nach Speech-Anbieter-ID gruppiert.
- Alte direkte Anbieterblöcke (`messages.tts.openai`, `messages.tts.elevenlabs`, `messages.tts.microsoft`, `messages.tts.edge`) werden beim Laden automatisch zu `messages.tts.providers.<id>` migriert.
- `maxTextLength`: hartes Limit für TTS-Eingaben (Zeichen). `/tts audio` schlägt fehl, wenn es überschritten wird.
- `timeoutMs`: Request-Timeout (ms).
- `prefsPath`: überschreibt den lokalen JSON-Pfad für Einstellungen (Anbieter/Limit/Zusammenfassung).
- `apiKey`-Werte greifen auf Umgebungsvariablen zurück (`ELEVENLABS_API_KEY`/`XI_API_KEY`, `MINIMAX_API_KEY`, `OPENAI_API_KEY`).
- `providers.elevenlabs.baseUrl`: überschreibt die ElevenLabs-API-Basis-URL.
- `providers.openai.baseUrl`: überschreibt den OpenAI-TTS-Endpunkt.
  - Auflösungsreihenfolge: `messages.tts.providers.openai.baseUrl` -> `OPENAI_TTS_BASE_URL` -> `https://api.openai.com/v1`
  - Nicht standardmäßige Werte werden als OpenAI-kompatible TTS-Endpunkte behandelt, daher werden benutzerdefinierte Modell- und Voice-Namen akzeptiert.
- `providers.elevenlabs.voiceSettings`:
  - `stability`, `similarityBoost`, `style`: `0..1`
  - `useSpeakerBoost`: `true|false`
  - `speed`: `0.5..2.0` (1.0 = normal)
- `providers.elevenlabs.applyTextNormalization`: `auto|on|off`
- `providers.elevenlabs.languageCode`: 2-stelliger ISO-639-1-Code (z. B. `en`, `de`)
- `providers.elevenlabs.seed`: Ganzzahl `0..4294967295` (Best-Effort-Determinismus)
- `providers.minimax.baseUrl`: überschreibt die MiniMax-API-Basis-URL (Standard `https://api.minimax.io`, env: `MINIMAX_API_HOST`).
- `providers.minimax.model`: TTS-Modell (Standard `speech-2.8-hd`, env: `MINIMAX_TTS_MODEL`).
- `providers.minimax.voiceId`: Voice-Kennung (Standard `English_expressive_narrator`, env: `MINIMAX_TTS_VOICE_ID`).
- `providers.minimax.speed`: Wiedergabegeschwindigkeit `0.5..2.0` (Standard 1.0).
- `providers.minimax.vol`: Lautstärke `(0, 10]` (Standard 1.0; muss größer als 0 sein).
- `providers.minimax.pitch`: Tonhöhenverschiebung `-12..12` (Standard 0).
- `providers.microsoft.enabled`: erlaubt die Nutzung von Microsoft Speech (Standard `true`; kein API-Schlüssel).
- `providers.microsoft.voice`: Name der Microsoft-Neural-Voice (z. B. `en-US-MichelleNeural`).
- `providers.microsoft.lang`: Sprachcode (z. B. `en-US`).
- `providers.microsoft.outputFormat`: Microsoft-Ausgabeformat (z. B. `audio-24khz-48kbitrate-mono-mp3`).
  - Gültige Werte finden Sie unter Microsoft Speech output formats; nicht alle Formate werden vom gebündelten Edge-basierten Transport unterstützt.
- `providers.microsoft.rate` / `providers.microsoft.pitch` / `providers.microsoft.volume`: Prozentzeichenfolgen (z. B. `+10%`, `-5%`).
- `providers.microsoft.saveSubtitles`: schreibt JSON-Untertitel neben die Audiodatei.
- `providers.microsoft.proxy`: Proxy-URL für Microsoft-Speech-Requests.
- `providers.microsoft.timeoutMs`: Überschreibung des Request-Timeouts (ms).
- `edge.*`: alter Alias für dieselben Microsoft-Einstellungen.

## Modellgesteuerte Überschreibungen (standardmäßig aktiviert)

Standardmäßig **kann** das Modell TTS-Direktiven für eine einzelne Antwort ausgeben.
Wenn `messages.tts.auto` auf `tagged` gesetzt ist, sind diese Direktiven erforderlich, um Audio auszulösen.

Wenn aktiviert, kann das Modell `[[tts:...]]`-Direktiven ausgeben, um die Voice
für eine einzelne Antwort zu überschreiben, sowie optional einen `[[tts:text]]...[[/tts:text]]`-Block,
um ausdrucksstarke Tags (Lachen, Gesangshinweise usw.) bereitzustellen, die nur im
Audio erscheinen sollen.

`provider=...`-Direktiven werden ignoriert, es sei denn, `modelOverrides.allowProvider: true`.

Beispiel für eine Antwort-Payload:

```
Here you go.

[[tts:voiceId=pMsXgVXv3BLzUgSXRplE model=eleven_v3 speed=1.1]]
[[tts:text]](laughs) Read the song once more.[[/tts:text]]
```

Verfügbare Direktivenschlüssel (wenn aktiviert):

- `provider` (registrierte Speech-Anbieter-ID, zum Beispiel `openai`, `elevenlabs`, `minimax` oder `microsoft`; erfordert `allowProvider: true`)
- `voice` (OpenAI-Voice) oder `voiceId` (ElevenLabs / MiniMax)
- `model` (OpenAI-TTS-Modell, ElevenLabs-Modell-ID oder MiniMax-Modell)
- `stability`, `similarityBoost`, `style`, `speed`, `useSpeakerBoost`
- `vol` / `volume` (MiniMax-Lautstärke, 0-10)
- `pitch` (MiniMax-Tonhöhe, -12 bis 12)
- `applyTextNormalization` (`auto|on|off`)
- `languageCode` (ISO 639-1)
- `seed`

Alle Modellüberschreibungen deaktivieren:

```json5
{
  messages: {
    tts: {
      modelOverrides: {
        enabled: false,
      },
    },
  },
}
```

Optionale Allowlist (Anbieterwechsel aktivieren, während andere Parameter konfigurierbar bleiben):

```json5
{
  messages: {
    tts: {
      modelOverrides: {
        enabled: true,
        allowProvider: true,
        allowSeed: false,
      },
    },
  },
}
```

## Benutzerspezifische Einstellungen

Slash-Befehle schreiben lokale Überschreibungen nach `prefsPath` (Standard:
`~/.openclaw/settings/tts.json`, überschreibbar mit `OPENCLAW_TTS_PREFS` oder
`messages.tts.prefsPath`).

Gespeicherte Felder:

- `enabled`
- `provider`
- `maxLength` (Zusammenfassungsschwelle; Standard 1500 Zeichen)
- `summarize` (Standard `true`)

Diese überschreiben `messages.tts.*` für diesen Host.

## Ausgabeformate (fest)

- **Feishu / Matrix / Telegram / WhatsApp**: Opus-Voice-Message (`opus_48000_64` von ElevenLabs, `opus` von OpenAI).
  - 48 kHz / 64 kbps ist ein guter Kompromiss für Voice-Messages.
- **Andere Kanäle**: MP3 (`mp3_44100_128` von ElevenLabs, `mp3` von OpenAI).
  - 44,1 kHz / 128 kbps ist die Standardbalance für klare Sprachwiedergabe.
- **MiniMax**: MP3 (Modell `speech-2.8-hd`, 32-kHz-Samplerate). Voice-Note-Format wird nativ nicht unterstützt; verwenden Sie OpenAI oder ElevenLabs für garantierte Opus-Voice-Messages.
- **Microsoft**: verwendet `microsoft.outputFormat` (Standard `audio-24khz-48kbitrate-mono-mp3`).
  - Der gebündelte Transport akzeptiert ein `outputFormat`, aber nicht alle Formate sind über den Dienst verfügbar.
  - Werte für das Ausgabeformat entsprechen Microsoft Speech output formats (einschließlich Ogg/WebM Opus).
  - Telegram `sendVoice` akzeptiert OGG/MP3/M4A; verwenden Sie OpenAI/ElevenLabs, wenn Sie garantierte Opus-Voice-Messages benötigen.
  - Wenn das konfigurierte Microsoft-Ausgabeformat fehlschlägt, versucht OpenClaw es erneut mit MP3.

OpenAI-/ElevenLabs-Ausgabeformate sind pro Kanal festgelegt (siehe oben).

## Verhalten von Auto-TTS

Wenn aktiviert, führt OpenClaw Folgendes aus:

- TTS wird übersprungen, wenn die Antwort bereits Medien oder eine `MEDIA:`-Direktive enthält.
- sehr kurze Antworten (< 10 Zeichen) werden übersprungen.
- lange Antworten werden, wenn aktiviert, mit `agents.defaults.model.primary` (oder `summaryModel`) zusammengefasst.
- das generierte Audio wird an die Antwort angehängt.

Wenn die Antwort `maxLength` überschreitet und die Zusammenfassung deaktiviert ist (oder kein API-Schlüssel für das
Zusammenfassungsmodell vorhanden ist), wird Audio
übersprungen und die normale Textantwort gesendet.

## Ablaufdiagramm

```
Reply -> TTS enabled?
  no  -> send text
  yes -> has media / MEDIA: / short?
          yes -> send text
          no  -> length > limit?
                   no  -> TTS -> attach audio
                   yes -> summary enabled?
                            no  -> send text
                            yes -> summarize (summaryModel or agents.defaults.model.primary)
                                      -> TTS -> attach audio
```

## Verwendung von Slash-Befehlen

Es gibt einen einzelnen Befehl: `/tts`.
Details zur Aktivierung finden Sie unter [Slash-Befehle](/de/tools/slash-commands).

Hinweis zu Discord: `/tts` ist ein integrierter Discord-Befehl, daher registriert OpenClaw dort
`/voice` als nativen Befehl. Textbasiertes `/tts ...` funktioniert weiterhin.

```
/tts off
/tts on
/tts status
/tts provider openai
/tts limit 2000
/tts summary off
/tts audio Hello from OpenClaw
```

Hinweise:

- Befehle erfordern einen autorisierten Absender (Allowlist-/Owner-Regeln gelten weiterhin).
- `commands.text` oder die Registrierung nativer Befehle muss aktiviert sein.
- Die Konfiguration `messages.tts.auto` akzeptiert `off|always|inbound|tagged`.
- `/tts on` schreibt die lokale TTS-Einstellung auf `always`; `/tts off` schreibt sie auf `off`.
- Verwenden Sie die Konfiguration, wenn Sie `inbound`- oder `tagged`-Standards möchten.
- `limit` und `summary` werden in lokalen Einstellungen gespeichert, nicht in der Hauptkonfiguration.
- `/tts audio` erzeugt eine einmalige Audioantwort (aktiviert TTS nicht dauerhaft).
- `/tts status` enthält Sichtbarkeit von Fallbacks für den neuesten Versuch:
  - erfolgreicher Fallback: `Fallback: <primary> -> <used>` plus `Attempts: ...`
  - Fehler: `Error: ...` plus `Attempts: ...`
  - detaillierte Diagnose: `Attempt details: provider:outcome(reasonCode) latency`
- OpenAI- und ElevenLabs-API-Fehler enthalten jetzt geparste Fehlerdetails des Anbieters und die Request-ID (wenn vom Anbieter zurückgegeben), die in TTS-Fehlern/Logs sichtbar gemacht werden.

## Agent-Tool

Das `tts`-Tool wandelt Text in Sprache um und gibt einen Audio-Anhang zur
Auslieferung der Antwort zurück. Wenn der Kanal Feishu, Matrix, Telegram oder WhatsApp ist,
wird das Audio als Voice-Message statt als Dateianhang gesendet.

## Gateway-RPC

Gateway-Methoden:

- `tts.status`
- `tts.enable`
- `tts.disable`
- `tts.convert`
- `tts.setProvider`
- `tts.providers`
