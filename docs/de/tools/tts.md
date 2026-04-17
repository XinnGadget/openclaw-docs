---
read_when:
    - Aktivieren von Text-to-Speech für Antworten
    - Konfigurieren von TTS-Anbietern oder -Limits
    - Verwenden von `/tts`-Befehlen
summary: Text-to-Speech (TTS) für ausgehende Antworten
title: Text-to-Speech
x-i18n:
    generated_at: "2026-04-16T19:31:09Z"
    model: gpt-5.4
    provider: openai
    source_hash: de7c1dc8831c1ba307596afd48cb4d36f844724887a13b17e35f41ef5174a86f
    source_path: tools/tts.md
    workflow: 15
---

# Text-to-Speech (TTS)

OpenClaw kann ausgehende Antworten mit ElevenLabs, Google Gemini, Microsoft, MiniMax oder OpenAI in Audio umwandeln.
Es funktioniert überall dort, wo OpenClaw Audio senden kann.

## Unterstützte Dienste

- **ElevenLabs** (primärer oder Fallback-Anbieter)
- **Google Gemini** (primärer oder Fallback-Anbieter; verwendet Gemini API TTS)
- **Microsoft** (primärer oder Fallback-Anbieter; die aktuelle gebündelte Implementierung verwendet `node-edge-tts`)
- **MiniMax** (primärer oder Fallback-Anbieter; verwendet die T2A v2 API)
- **OpenAI** (primärer oder Fallback-Anbieter; wird auch für Zusammenfassungen verwendet)

### Hinweise zu Microsoft Speech

Der gebündelte Microsoft-Sprachanbieter verwendet derzeit den gehosteten
neuronalen TTS-Dienst von Microsoft Edge über die Bibliothek `node-edge-tts`. Es handelt sich um einen gehosteten Dienst (nicht
lokal), der Microsoft-Endpunkte verwendet und keinen API-Schlüssel erfordert.
`node-edge-tts` stellt Sprachkonfigurationsoptionen und Ausgabeformate bereit,
aber nicht alle Optionen werden vom Dienst unterstützt. Legacy-Konfiguration und Direktiven-Eingaben
mit `edge` funktionieren weiterhin und werden zu `microsoft` normalisiert.

Da dieser Pfad ein öffentlicher Webdienst ohne veröffentlichte SLA oder Quoten ist,
solltest du ihn als Best-Effort betrachten. Wenn du garantierte Limits und Support benötigst, verwende OpenAI
oder ElevenLabs.

## Optionale Schlüssel

Wenn du OpenAI, ElevenLabs, Google Gemini oder MiniMax verwenden möchtest:

- `ELEVENLABS_API_KEY` (oder `XI_API_KEY`)
- `GEMINI_API_KEY` (oder `GOOGLE_API_KEY`)
- `MINIMAX_API_KEY`
- `OPENAI_API_KEY`

Microsoft Speech benötigt **keinen** API-Schlüssel.

Wenn mehrere Anbieter konfiguriert sind, wird zuerst der ausgewählte Anbieter verwendet, die anderen dienen als Fallback-Optionen.
Die automatische Zusammenfassung verwendet das konfigurierte `summaryModel` (oder `agents.defaults.model.primary`),
daher muss dieser Anbieter ebenfalls authentifiziert sein, wenn du Zusammenfassungen aktivierst.

## Dienst-Links

- [OpenAI Text-to-Speech guide](https://platform.openai.com/docs/guides/text-to-speech)
- [OpenAI Audio API reference](https://platform.openai.com/docs/api-reference/audio)
- [ElevenLabs Text to Speech](https://elevenlabs.io/docs/api-reference/text-to-speech)
- [ElevenLabs Authentication](https://elevenlabs.io/docs/api-reference/authentication)
- [MiniMax T2A v2 API](https://platform.minimaxi.com/document/T2A%20V2)
- [node-edge-tts](https://github.com/SchneeHertz/node-edge-tts)
- [Microsoft Speech output formats](https://learn.microsoft.com/azure/ai-services/speech-service/rest-text-to-speech#audio-outputs)

## Ist es standardmäßig aktiviert?

Nein. Auto‑TTS ist standardmäßig **deaktiviert**. Aktiviere es in der Konfiguration mit
`messages.tts.auto` oder lokal mit `/tts on`.

Wenn `messages.tts.provider` nicht gesetzt ist, wählt OpenClaw den ersten konfigurierten
Sprachanbieter in der Auto-Select-Reihenfolge des Registrys aus.

## Konfiguration

Die TTS-Konfiguration befindet sich unter `messages.tts` in `openclaw.json`.
Das vollständige Schema findest du unter [Gateway-Konfiguration](/de/gateway/configuration).

### Minimale Konfiguration (Aktivierung + Anbieter)

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

### OpenAI als primärer Anbieter mit ElevenLabs als Fallback

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

### Microsoft als primärer Anbieter (kein API-Schlüssel)

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

### MiniMax als primärer Anbieter

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

### Google Gemini als primärer Anbieter

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "google",
      providers: {
        google: {
          apiKey: "gemini_api_key",
          model: "gemini-3.1-flash-tts-preview",
          voiceName: "Kore",
        },
      },
    },
  },
}
```

Google Gemini TTS verwendet den Gemini-API-Schlüsselpfad. Ein API-Schlüssel aus der Google Cloud Console,
der auf die Gemini API beschränkt ist, ist hier gültig, und es ist derselbe Schlüsseltyp,
der vom gebündelten Google-Bildgenerierungsanbieter verwendet wird. Die Auflösungsreihenfolge ist
`messages.tts.providers.google.apiKey` -> `models.providers.google.apiKey` ->
`GEMINI_API_KEY` -> `GOOGLE_API_KEY`.

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

### Benutzerdefinierte Limits + Prefs-Pfad

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

### Nur mit Audio antworten nach einer eingehenden Sprachnachricht

```json5
{
  messages: {
    tts: {
      auto: "inbound",
    },
  },
}
```

### Automatische Zusammenfassung für lange Antworten deaktivieren

```json5
{
  messages: {
    tts: {
      auto: "always",
    },
  },
}
```

Dann ausführen:

```
/tts summary off
```

### Hinweise zu den Feldern

- `auto`: Auto‑TTS-Modus (`off`, `always`, `inbound`, `tagged`).
  - `inbound` sendet Audio nur nach einer eingehenden Sprachnachricht.
  - `tagged` sendet Audio nur, wenn die Antwort `[[tts:key=value]]`-Direktiven oder einen `[[tts:text]]...[[/tts:text]]`-Block enthält.
- `enabled`: Legacy-Schalter (doctor migriert dies zu `auto`).
- `mode`: `"final"` (Standard) oder `"all"` (einschließlich Tool-/Block-Antworten).
- `provider`: Sprachanbieter-ID wie `"elevenlabs"`, `"google"`, `"microsoft"`, `"minimax"` oder `"openai"` (Fallback erfolgt automatisch).
- Wenn `provider` **nicht gesetzt** ist, verwendet OpenClaw den ersten konfigurierten Sprachanbieter in der Auto-Select-Reihenfolge des Registrys.
- Das Legacy-`provider: "edge"` funktioniert weiterhin und wird zu `microsoft` normalisiert.
- `summaryModel`: optionales günstiges Modell für die automatische Zusammenfassung; standardmäßig `agents.defaults.model.primary`.
  - Akzeptiert `provider/model` oder einen konfigurierten Modellalias.
- `modelOverrides`: erlaubt dem Modell, TTS-Direktiven auszugeben (standardmäßig aktiviert).
  - `allowProvider` ist standardmäßig `false` (Anbieterwechsel ist Opt-in).
- `providers.<id>`: anbieterinterne Einstellungen, verschlüsselt nach Sprachanbieter-ID.
- Legacy-direkte Anbieterblöcke (`messages.tts.openai`, `messages.tts.elevenlabs`, `messages.tts.microsoft`, `messages.tts.edge`) werden beim Laden automatisch zu `messages.tts.providers.<id>` migriert.
- `maxTextLength`: harte Obergrenze für TTS-Eingaben (Zeichen). `/tts audio` schlägt fehl, wenn diese überschritten wird.
- `timeoutMs`: Anfrage-Timeout (ms).
- `prefsPath`: überschreibt den lokalen JSON-Pfad für Prefs (Anbieter/Limit/Zusammenfassung).
- `apiKey`-Werte greifen auf Umgebungsvariablen zurück (`ELEVENLABS_API_KEY`/`XI_API_KEY`, `GEMINI_API_KEY`/`GOOGLE_API_KEY`, `MINIMAX_API_KEY`, `OPENAI_API_KEY`).
- `providers.elevenlabs.baseUrl`: überschreibt die ElevenLabs-API-Basis-URL.
- `providers.openai.baseUrl`: überschreibt den OpenAI-TTS-Endpunkt.
  - Auflösungsreihenfolge: `messages.tts.providers.openai.baseUrl` -> `OPENAI_TTS_BASE_URL` -> `https://api.openai.com/v1`
  - Nicht standardmäßige Werte werden als OpenAI-kompatible TTS-Endpunkte behandelt, daher werden benutzerdefinierte Modell- und Stimmnamen akzeptiert.
- `providers.elevenlabs.voiceSettings`:
  - `stability`, `similarityBoost`, `style`: `0..1`
  - `useSpeakerBoost`: `true|false`
  - `speed`: `0.5..2.0` (1.0 = normal)
- `providers.elevenlabs.applyTextNormalization`: `auto|on|off`
- `providers.elevenlabs.languageCode`: 2-stelliger ISO-639-1-Code (z. B. `en`, `de`)
- `providers.elevenlabs.seed`: Ganzzahl `0..4294967295` (Best-Effort-Determinismus)
- `providers.minimax.baseUrl`: überschreibt die MiniMax-API-Basis-URL (Standard `https://api.minimax.io`, Umgebungsvariable: `MINIMAX_API_HOST`).
- `providers.minimax.model`: TTS-Modell (Standard `speech-2.8-hd`, Umgebungsvariable: `MINIMAX_TTS_MODEL`).
- `providers.minimax.voiceId`: Stimmkennung (Standard `English_expressive_narrator`, Umgebungsvariable: `MINIMAX_TTS_VOICE_ID`).
- `providers.minimax.speed`: Wiedergabegeschwindigkeit `0.5..2.0` (Standard 1.0).
- `providers.minimax.vol`: Lautstärke `(0, 10]` (Standard 1.0; muss größer als 0 sein).
- `providers.minimax.pitch`: Tonhöhenverschiebung `-12..12` (Standard 0).
- `providers.google.model`: Gemini-TTS-Modell (Standard `gemini-3.1-flash-tts-preview`).
- `providers.google.voiceName`: Name der vorgefertigten Gemini-Stimme (Standard `Kore`; `voice` wird ebenfalls akzeptiert).
- `providers.google.baseUrl`: überschreibt die Gemini-API-Basis-URL. Nur `https://generativelanguage.googleapis.com` wird akzeptiert.
  - Wenn `messages.tts.providers.google.apiKey` ausgelassen wird, kann TTS vor dem Fallback auf Umgebungsvariablen `models.providers.google.apiKey` wiederverwenden.
- `providers.microsoft.enabled`: erlaubt die Verwendung von Microsoft Speech (Standard `true`; kein API-Schlüssel).
- `providers.microsoft.voice`: Name der neuronalen Microsoft-Stimme (z. B. `en-US-MichelleNeural`).
- `providers.microsoft.lang`: Sprachcode (z. B. `en-US`).
- `providers.microsoft.outputFormat`: Microsoft-Ausgabeformat (z. B. `audio-24khz-48kbitrate-mono-mp3`).
  - Siehe Microsoft Speech output formats für gültige Werte; nicht alle Formate werden vom gebündelten Edge-basierten Transport unterstützt.
- `providers.microsoft.rate` / `providers.microsoft.pitch` / `providers.microsoft.volume`: Prozentzeichenfolgen (z. B. `+10%`, `-5%`).
- `providers.microsoft.saveSubtitles`: schreibt JSON-Untertitel zusammen mit der Audiodatei.
- `providers.microsoft.proxy`: Proxy-URL für Microsoft-Speech-Anfragen.
- `providers.microsoft.timeoutMs`: überschreibt das Anfrage-Timeout (ms).
- `edge.*`: Legacy-Alias für dieselben Microsoft-Einstellungen.

## Modellgesteuerte Overrides (standardmäßig aktiviert)

Standardmäßig **kann** das Modell TTS-Direktiven für eine einzelne Antwort ausgeben.
Wenn `messages.tts.auto` auf `tagged` gesetzt ist, sind diese Direktiven erforderlich, um Audio auszulösen.

Wenn aktiviert, kann das Modell `[[tts:...]]`-Direktiven ausgeben, um die Stimme
für eine einzelne Antwort zu überschreiben, sowie optional einen `[[tts:text]]...[[/tts:text]]`-Block,
um expressive Tags (Lachen, Gesangshinweise usw.) bereitzustellen, die nur im
Audio erscheinen sollen.

`provider=...`-Direktiven werden ignoriert, sofern nicht `modelOverrides.allowProvider: true` gesetzt ist.

Beispiel für eine Antwort-Payload:

```
Hier ist sie.

[[tts:voiceId=pMsXgVXv3BLzUgSXRplE model=eleven_v3 speed=1.1]]
[[tts:text]](lacht) Lies das Lied noch einmal vor.[[/tts:text]]
```

Verfügbare Direktivschlüssel (wenn aktiviert):

- `provider` (registrierte Sprachanbieter-ID, zum Beispiel `openai`, `elevenlabs`, `google`, `minimax` oder `microsoft`; erfordert `allowProvider: true`)
- `voice` (OpenAI-Stimme), `voiceName` / `voice_name` / `google_voice` (Google-Stimme) oder `voiceId` (ElevenLabs / MiniMax)
- `model` (OpenAI-TTS-Modell, ElevenLabs-Modell-ID oder MiniMax-Modell) oder `google_model` (Google-TTS-Modell)
- `stability`, `similarityBoost`, `style`, `speed`, `useSpeakerBoost`
- `vol` / `volume` (MiniMax-Lautstärke, 0-10)
- `pitch` (MiniMax-Tonhöhe, -12 bis 12)
- `applyTextNormalization` (`auto|on|off`)
- `languageCode` (ISO 639-1)
- `seed`

Alle modellgesteuerten Overrides deaktivieren:

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

Optionale Allowlist (Anbieterwechsel aktivieren, während andere Parameter weiterhin konfigurierbar bleiben):

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

Slash-Befehle schreiben lokale Overrides nach `prefsPath` (Standard:
`~/.openclaw/settings/tts.json`, überschreibbar mit `OPENCLAW_TTS_PREFS` oder
`messages.tts.prefsPath`).

Gespeicherte Felder:

- `enabled`
- `provider`
- `maxLength` (Schwellenwert für Zusammenfassungen; Standard 1500 Zeichen)
- `summarize` (Standard `true`)

Diese überschreiben `messages.tts.*` für diesen Host.

## Ausgabeformate (fest)

- **Feishu / Matrix / Telegram / WhatsApp**: Opus-Sprachnachricht (`opus_48000_64` von ElevenLabs, `opus` von OpenAI).
  - 48 kHz / 64 kbps ist ein guter Kompromiss für Sprachnachrichten.
- **Andere Kanäle**: MP3 (`mp3_44100_128` von ElevenLabs, `mp3` von OpenAI).
  - 44,1 kHz / 128 kbps ist die Standardbalance für Sprachverständlichkeit.
- **MiniMax**: MP3 (`speech-2.8-hd`-Modell, 32-kHz-Abtastrate). Voice-Note-Format wird nativ nicht unterstützt; verwende OpenAI oder ElevenLabs für garantierte Opus-Sprachnachrichten.
- **Google Gemini**: Gemini API TTS gibt rohes 24-kHz-PCM zurück. OpenClaw verpackt es als WAV für Audioanhänge und gibt PCM direkt für Talk/Telephonie zurück. Das native Opus-Voice-Note-Format wird auf diesem Weg nicht unterstützt.
- **Microsoft**: verwendet `microsoft.outputFormat` (Standard `audio-24khz-48kbitrate-mono-mp3`).
  - Der gebündelte Transport akzeptiert ein `outputFormat`, aber nicht alle Formate sind vom Dienst verfügbar.
  - Werte für das Ausgabeformat entsprechen den Microsoft Speech output formats (einschließlich Ogg/WebM Opus).
  - Telegram `sendVoice` akzeptiert OGG/MP3/M4A; verwende OpenAI/ElevenLabs, wenn du
    garantierte Opus-Sprachnachrichten benötigst.
  - Wenn das konfigurierte Microsoft-Ausgabeformat fehlschlägt, versucht OpenClaw es erneut mit MP3.

Die OpenAI-/ElevenLabs-Ausgabeformate sind je Kanal festgelegt (siehe oben).

## Verhalten von Auto-TTS

Wenn aktiviert, führt OpenClaw Folgendes aus:

- überspringt TTS, wenn die Antwort bereits Medien oder eine `MEDIA:`-Direktive enthält.
- überspringt sehr kurze Antworten (< 10 Zeichen).
- fasst lange Antworten bei Aktivierung mit `agents.defaults.model.primary` (oder `summaryModel`) zusammen.
- hängt das generierte Audio an die Antwort an.

Wenn die Antwort `maxLength` überschreitet und die Zusammenfassung deaktiviert ist (oder kein API-Schlüssel für das
Zusammenfassungsmodell vorhanden ist), wird Audio
übersprungen und die normale Textantwort gesendet.

## Ablaufdiagramm

```
Antwort -> TTS aktiviert?
  nein -> Text senden
  ja   -> Medien / MEDIA: / kurz vorhanden?
          ja   -> Text senden
          nein -> Länge > Limit?
                   nein -> TTS -> Audio anhängen
                   ja   -> Zusammenfassung aktiviert?
                            nein -> Text senden
                            ja   -> zusammenfassen (summaryModel oder agents.defaults.model.primary)
                                      -> TTS -> Audio anhängen
```

## Verwendung von Slash-Befehlen

Es gibt einen einzigen Befehl: `/tts`.
Details zur Aktivierung findest du unter [Slash-Befehle](/de/tools/slash-commands).

Hinweis zu Discord: `/tts` ist ein integrierter Discord-Befehl, daher registriert OpenClaw
dort `/voice` als nativen Befehl. Textbasiertes `/tts ...` funktioniert weiterhin.

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
- Verwende die Konfiguration, wenn du `inbound`- oder `tagged`-Standards möchtest.
- `limit` und `summary` werden in lokalen Prefs gespeichert, nicht in der Hauptkonfiguration.
- `/tts audio` erzeugt eine einmalige Audioantwort (aktiviert TTS nicht).
- `/tts status` enthält Fallback-Sichtbarkeit für den letzten Versuch:
  - erfolgreiches Fallback: `Fallback: <primary> -> <used>` plus `Attempts: ...`
  - Fehler: `Error: ...` plus `Attempts: ...`
  - detaillierte Diagnose: `Attempt details: provider:outcome(reasonCode) latency`
- Fehler von OpenAI- und ElevenLabs-APIs enthalten jetzt geparste Anbieterdetails und die Request-ID (wenn vom Anbieter zurückgegeben), die in TTS-Fehlern/Logs angezeigt werden.

## Agent-Tool

Das Tool `tts` wandelt Text in Sprache um und gibt einen Audioanhang für
die Antwortzustellung zurück. Wenn der Kanal Feishu, Matrix, Telegram oder WhatsApp ist,
wird das Audio als Sprachnachricht statt als Dateianhang zugestellt.

## Gateway RPC

Gateway-Methoden:

- `tts.status`
- `tts.enable`
- `tts.disable`
- `tts.convert`
- `tts.setProvider`
- `tts.providers`
