---
read_when:
    - Videos über den Agenten generieren
    - Anbieter und Modelle für die Videogenerierung konfigurieren
    - Die Parameter des Tools `video_generate` verstehen
summary: Generiere Videos aus Text, Bildern oder vorhandenen Videos mit 14 Provider-Backends.
title: Videogenerierung
x-i18n:
    generated_at: "2026-04-15T06:22:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: c182f24b25e44f157a820e82a1f7422247f26125956944b5eb98613774268cfe
    source_path: tools/video-generation.md
    workflow: 15
---

# Videogenerierung

OpenClaw-Agenten können Videos aus Text-Prompts, Referenzbildern oder vorhandenen Videos generieren. Vierzehn Provider-Backends werden unterstützt, jeweils mit unterschiedlichen Modelloptionen, Eingabemodi und Funktionsumfängen. Der Agent wählt anhand deiner Konfiguration und der verfügbaren API-Schlüssel automatisch den richtigen Provider aus.

<Note>
Das Tool `video_generate` erscheint nur, wenn mindestens ein Provider für Videogenerierung verfügbar ist. Wenn du es in deinen Agenten-Tools nicht siehst, setze einen Provider-API-Schlüssel oder konfiguriere `agents.defaults.videoGenerationModel`.
</Note>

OpenClaw behandelt die Videogenerierung als drei Laufzeitmodi:

- `generate` für Text-zu-Video-Anfragen ohne Referenzmedien
- `imageToVideo`, wenn die Anfrage ein oder mehrere Referenzbilder enthält
- `videoToVideo`, wenn die Anfrage ein oder mehrere Referenzvideos enthält

Provider können eine beliebige Teilmenge dieser Modi unterstützen. Das Tool validiert den aktiven
Modus vor dem Absenden und meldet unterstützte Modi in `action=list`.

## Schnellstart

1. Setze einen API-Schlüssel für einen beliebigen unterstützten Provider:

```bash
export GEMINI_API_KEY="your-key"
```

2. Optional ein Standardmodell festlegen:

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "google/veo-3.1-fast-generate-preview"
```

3. Frage den Agenten:

> Generiere ein 5-sekündiges cineastisches Video eines freundlichen Hummers, der bei Sonnenuntergang surft.

Der Agent ruft `video_generate` automatisch auf. Keine Tool-Allowlist erforderlich.

## Was passiert, wenn du ein Video generierst

Die Videogenerierung ist asynchron. Wenn der Agent `video_generate` in einer Sitzung aufruft:

1. OpenClaw sendet die Anfrage an den Provider und gibt sofort eine Aufgaben-ID zurück.
2. Der Provider verarbeitet den Auftrag im Hintergrund (typischerweise 30 Sekunden bis 5 Minuten, je nach Provider und Auflösung).
3. Wenn das Video bereit ist, aktiviert OpenClaw dieselbe Sitzung mit einem internen Abschlussereignis erneut.
4. Der Agent postet das fertige Video zurück in die ursprüngliche Unterhaltung.

Während ein Auftrag läuft, geben doppelte `video_generate`-Aufrufe in derselben Sitzung den aktuellen Aufgabenstatus zurück, statt eine weitere Generierung zu starten. Verwende `openclaw tasks list` oder `openclaw tasks show <taskId>`, um den Fortschritt über die CLI zu prüfen.

Außerhalb sitzungsbasierter Agentenläufe (zum Beispiel direkte Tool-Aufrufe) fällt das Tool auf eine Inline-Generierung zurück und gibt den endgültigen Medienpfad im selben Durchgang zurück.

### Aufgabenlebenszyklus

Jede `video_generate`-Anfrage durchläuft vier Zustände:

1. **queued** -- Aufgabe erstellt, wartet darauf, dass der Provider sie annimmt.
2. **running** -- der Provider verarbeitet sie (typischerweise 30 Sekunden bis 5 Minuten, je nach Provider und Auflösung).
3. **succeeded** -- Video bereit; der Agent wird aktiviert und postet es in die Unterhaltung.
4. **failed** -- Provider-Fehler oder Zeitüberschreitung; der Agent wird mit Fehlerdetails aktiviert.

Status über die CLI prüfen:

```bash
openclaw tasks list
openclaw tasks show <taskId>
openclaw tasks cancel <taskId>
```

Verhinderung von Duplikaten: Wenn für die aktuelle Sitzung bereits eine Videoaufgabe `queued` oder `running` ist, gibt `video_generate` den vorhandenen Aufgabenstatus zurück, statt eine neue zu starten. Verwende `action: "status"`, um dies explizit zu prüfen, ohne eine neue Generierung auszulösen.

## Unterstützte Provider

| Provider              | Standardmodell                 | Text | Bildreferenz                                        | Videoreferenz   | API-Schlüssel                            |
| --------------------- | ------------------------------ | ---- | --------------------------------------------------- | --------------- | ---------------------------------------- |
| Alibaba               | `wan2.6-t2v`                   | Ja   | Ja (Remote-URL)                                     | Ja (Remote-URL) | `MODELSTUDIO_API_KEY`                    |
| BytePlus (1.0)        | `seedance-1-0-pro-250528`      | Ja   | Bis zu 2 Bilder (nur I2V-Modelle; erster + letzter Frame) | Nein            | `BYTEPLUS_API_KEY`                       |
| BytePlus Seedance 1.5 | `seedance-1-5-pro-251215`      | Ja   | Bis zu 2 Bilder (erster + letzter Frame über Rolle) | Nein            | `BYTEPLUS_API_KEY`                       |
| BytePlus Seedance 2.0 | `dreamina-seedance-2-0-260128` | Ja   | Bis zu 9 Referenzbilder                             | Bis zu 3 Videos | `BYTEPLUS_API_KEY`                       |
| ComfyUI               | `workflow`                     | Ja   | 1 Bild                                              | Nein            | `COMFY_API_KEY` oder `COMFY_CLOUD_API_KEY` |
| fal                   | `fal-ai/minimax/video-01-live` | Ja   | 1 Bild                                              | Nein            | `FAL_KEY`                                |
| Google                | `veo-3.1-fast-generate-preview` | Ja  | 1 Bild                                              | 1 Video         | `GEMINI_API_KEY`                         |
| MiniMax               | `MiniMax-Hailuo-2.3`           | Ja   | 1 Bild                                              | Nein            | `MINIMAX_API_KEY`                        |
| OpenAI                | `sora-2`                       | Ja   | 1 Bild                                              | 1 Video         | `OPENAI_API_KEY`                         |
| Qwen                  | `wan2.6-t2v`                   | Ja   | Ja (Remote-URL)                                     | Ja (Remote-URL) | `QWEN_API_KEY`                           |
| Runway                | `gen4.5`                       | Ja   | 1 Bild                                              | 1 Video         | `RUNWAYML_API_SECRET`                    |
| Together              | `Wan-AI/Wan2.2-T2V-A14B`       | Ja   | 1 Bild                                              | Nein            | `TOGETHER_API_KEY`                       |
| Vydra                 | `veo3`                         | Ja   | 1 Bild (`kling`)                                    | Nein            | `VYDRA_API_KEY`                          |
| xAI                   | `grok-imagine-video`           | Ja   | 1 Bild                                              | 1 Video         | `XAI_API_KEY`                            |

Einige Provider akzeptieren zusätzliche oder alternative API-Schlüssel-Umgebungsvariablen. Sieh auf den einzelnen [Provider-Seiten](#related) nach Details.

Führe `video_generate action=list` aus, um verfügbare Provider, Modelle und
Laufzeitmodi zur Laufzeit zu prüfen.

### Deklarierte Fähigkeitsmatrix

Dies ist der explizite Modusvertrag, der von `video_generate`, Vertragstests
und dem gemeinsamen Live-Sweep verwendet wird.

| Provider | `generate` | `imageToVideo` | `videoToVideo` | Gemeinsame Live-Kanäle heute                                                                                                                   |
| -------- | ---------- | -------------- | -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Alibaba  | Ja         | Ja             | Ja             | `generate`, `imageToVideo`; `videoToVideo` übersprungen, weil dieser Provider Remote-`http(s)`-Video-URLs benötigt                            |
| BytePlus | Ja         | Ja             | Nein           | `generate`, `imageToVideo`                                                                                                                      |
| ComfyUI  | Ja         | Ja             | Nein           | Nicht im gemeinsamen Sweep; workflowspezifische Abdeckung liegt bei den Comfy-Tests                                                           |
| fal      | Ja         | Ja             | Nein           | `generate`, `imageToVideo`                                                                                                                      |
| Google   | Ja         | Ja             | Ja             | `generate`, `imageToVideo`; gemeinsames `videoToVideo` übersprungen, weil der aktuelle bufferbasierte Gemini/Veo-Sweep diese Eingabe nicht akzeptiert |
| MiniMax  | Ja         | Ja             | Nein           | `generate`, `imageToVideo`                                                                                                                      |
| OpenAI   | Ja         | Ja             | Ja             | `generate`, `imageToVideo`; gemeinsames `videoToVideo` übersprungen, weil dieser Org-/Eingabepfad derzeit providerseitigen Inpaint-/Remix-Zugriff benötigt |
| Qwen     | Ja         | Ja             | Ja             | `generate`, `imageToVideo`; `videoToVideo` übersprungen, weil dieser Provider Remote-`http(s)`-Video-URLs benötigt                            |
| Runway   | Ja         | Ja             | Ja             | `generate`, `imageToVideo`; `videoToVideo` läuft nur, wenn das ausgewählte Modell `runway/gen4_aleph` ist                                     |
| Together | Ja         | Ja             | Nein           | `generate`, `imageToVideo`                                                                                                                      |
| Vydra    | Ja         | Ja             | Nein           | `generate`; gemeinsames `imageToVideo` übersprungen, weil das gebündelte `veo3` nur Text unterstützt und das gebündelte `kling` eine Remote-Bild-URL benötigt |
| xAI      | Ja         | Ja             | Ja             | `generate`, `imageToVideo`; `videoToVideo` übersprungen, weil dieser Provider derzeit eine Remote-MP4-URL benötigt                            |

## Tool-Parameter

### Erforderlich

| Parameter | Typ    | Beschreibung                                                                     |
| --------- | ------ | -------------------------------------------------------------------------------- |
| `prompt`  | string | Textbeschreibung des zu generierenden Videos (erforderlich für `action: "generate"`) |

### Inhaltseingaben

| Parameter    | Typ      | Beschreibung                                                                                                                         |
| ------------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `image`      | string   | Einzelnes Referenzbild (Pfad oder URL)                                                                                               |
| `images`     | string[] | Mehrere Referenzbilder (bis zu 9)                                                                                                    |
| `imageRoles` | string[] | Optionale Rollenhints pro Position parallel zur kombinierten Bildliste. Kanonische Werte: `first_frame`, `last_frame`, `reference_image` |
| `video`      | string   | Einzelnes Referenzvideo (Pfad oder URL)                                                                                              |
| `videos`     | string[] | Mehrere Referenzvideos (bis zu 4)                                                                                                    |
| `videoRoles` | string[] | Optionale Rollenhints pro Position parallel zur kombinierten Videoliste. Kanonischer Wert: `reference_video`                        |
| `audioRef`   | string   | Einzelne Referenz-Audiodatei (Pfad oder URL). Wird z. B. für Hintergrundmusik oder Stimmreferenz verwendet, wenn der Provider Audioeingaben unterstützt |
| `audioRefs`  | string[] | Mehrere Referenz-Audiodateien (bis zu 3)                                                                                             |
| `audioRoles` | string[] | Optionale Rollenhints pro Position parallel zur kombinierten Audioliste. Kanonischer Wert: `reference_audio`                        |

Rollenhinweise werden unverändert an den Provider weitergeleitet. Kanonische Werte stammen aus
der Union `VideoGenerationAssetRole`, aber Provider können zusätzliche
Rollen-Strings akzeptieren. `*Roles`-Arrays dürfen nicht mehr Einträge als die
entsprechende Referenzliste haben; Off-by-one-Fehler schlagen mit einer klaren Fehlermeldung fehl.
Verwende einen leeren String, um einen Slot ungesetzt zu lassen.

### Stilsteuerung

| Parameter         | Typ     | Beschreibung                                                                            |
| ----------------- | ------- | --------------------------------------------------------------------------------------- |
| `aspectRatio`     | string  | `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` oder `adaptive` |
| `resolution`      | string  | `480P`, `720P`, `768P` oder `1080P`                                                     |
| `durationSeconds` | number  | Zieldauer in Sekunden (auf den nächsten vom Provider unterstützten Wert gerundet)       |
| `size`            | string  | Größenhinweis, wenn der Provider dies unterstützt                                       |
| `audio`           | boolean | Generierten Ton in der Ausgabe aktivieren, wenn unterstützt. Unterschieden von `audioRef*` (Eingaben) |
| `watermark`       | boolean | Wasserzeichen des Providers umschalten, wenn unterstützt                                |

`adaptive` ist ein providerspezifischer Sentinel-Wert: Er wird unverändert an
Provider weitergeleitet, die `adaptive` in ihren Fähigkeiten deklarieren (z. B. verwendet BytePlus
Seedance ihn, um das Seitenverhältnis automatisch aus den Abmessungen des
Eingabebilds zu erkennen). Provider, die ihn nicht deklarieren, geben den Wert über
`details.ignoredOverrides` im Tool-Ergebnis aus, sodass das Ignorieren sichtbar ist.

### Erweitert

| Parameter         | Typ    | Beschreibung                                                                                                                                                                                                                                                                                                                                           |
| ----------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `action`          | string | `"generate"` (Standard), `"status"` oder `"list"`                                                                                                                                                                                                                                                                                                      |
| `model`           | string | Provider-/Modell-Override (z. B. `runway/gen4.5`)                                                                                                                                                                                                                                                                                                      |
| `filename`        | string | Hinweis für den Ausgabedateinamen                                                                                                                                                                                                                                                                                                                      |
| `providerOptions` | object | Providerspezifische Optionen als JSON-Objekt (z. B. `{"seed": 42, "draft": true}`). Provider, die ein typisiertes Schema deklarieren, validieren Schlüssel und Typen; unbekannte Schlüssel oder Nichtübereinstimmungen überspringen den Kandidaten während des Fallbacks. Provider ohne deklariertes Schema erhalten die Optionen unverändert. Führe `video_generate action=list` aus, um zu sehen, was jeder Provider akzeptiert |

Nicht alle Provider unterstützen alle Parameter. OpenClaw normalisiert die Dauer bereits auf den nächstgelegenen vom Provider unterstützten Wert und ordnet außerdem übersetzte Geometriehinweise wie Größe-zu-Seitenverhältnis neu zu, wenn ein Fallback-Provider eine andere Steuerungsoberfläche bereitstellt. Wirklich nicht unterstützte Overrides werden nach bestem Aufwand ignoriert und als Warnungen im Tool-Ergebnis gemeldet. Harte Fähigkeitsgrenzen (wie zu viele Referenzeingaben) schlagen vor dem Absenden fehl.

Tool-Ergebnisse melden die angewendeten Einstellungen. Wenn OpenClaw Dauer oder Geometrie während des Provider-Fallbacks neu zuordnet, spiegeln die zurückgegebenen Werte `durationSeconds`, `size`, `aspectRatio` und `resolution` wider, was gesendet wurde, und `details.normalization` erfasst die Übersetzung von angefordert zu angewendet.

Referenzeingaben wählen außerdem den Laufzeitmodus aus:

- Keine Referenzmedien: `generate`
- Beliebige Bildreferenz: `imageToVideo`
- Beliebige Videoreferenz: `videoToVideo`
- Referenz-Audioeingaben ändern den aufgelösten Modus nicht; sie werden zusätzlich zu dem Modus angewendet, den die Bild-/Videoreferenzen auswählen, und funktionieren nur mit Providern, die `maxInputAudios` deklarieren

Gemischte Bild- und Videoreferenzen sind keine stabile gemeinsam genutzte Fähigkeitsoberfläche.
Bevorzuge pro Anfrage einen Referenztyp.

#### Fallback und typisierte Optionen

Einige Fähigkeitsprüfungen werden auf der Fallback-Ebene statt an der
Tool-Grenze angewendet, damit eine Anfrage, die die Grenzen des primären Providers
überschreitet, trotzdem auf einem geeigneten Fallback ausgeführt werden kann:

- Wenn der aktive Kandidat kein `maxInputAudios` deklariert (oder es als
  `0` deklariert), wird er übersprungen, wenn die Anfrage Audio-Referenzen enthält, und der
  nächste Kandidat wird versucht.
- Wenn `maxDurationSeconds` des aktiven Kandidaten unter den angeforderten
  `durationSeconds` liegt und der Kandidat keine Liste
  `supportedDurationSeconds` deklariert, wird er übersprungen.
- Wenn die Anfrage `providerOptions` enthält und der aktive Kandidat
  ausdrücklich ein typisiertes Schema für `providerOptions` deklariert, wird der Kandidat
  übersprungen, wenn die angegebenen Schlüssel nicht im Schema enthalten sind oder die Werttypen nicht
  übereinstimmen. Provider, die noch kein Schema deklariert haben, erhalten die
  Optionen unverändert (rückwärtskompatible Durchreichung). Ein Provider kann
  ausdrücklich auf alle Provider-Optionen verzichten, indem er ein leeres Schema
  deklariert (`capabilities.providerOptions: {}`), was dasselbe Überspringen wie bei einem
  Typkonflikt verursacht.

Der erste Überspringgrund in einer Anfrage wird mit `warn` protokolliert, damit Operatoren sehen,
wann ihr primärer Provider übergangen wurde; nachfolgende Überspringe werden mit
`debug` protokolliert, damit lange Fallback-Ketten ruhig bleiben. Wenn jeder Kandidat übersprungen wird,
enthält der aggregierte Fehler den Überspringgrund für jeden einzelnen.

## Aktionen

- **generate** (Standard) -- ein Video aus dem angegebenen Prompt und optionalen Referenzeingaben erstellen.
- **status** -- den Status der laufenden Videoaufgabe für die aktuelle Sitzung prüfen, ohne eine weitere Generierung zu starten.
- **list** -- verfügbare Provider, Modelle und ihre Fähigkeiten anzeigen.

## Modellauswahl

Beim Generieren eines Videos löst OpenClaw das Modell in dieser Reihenfolge auf:

1. **`model`-Tool-Parameter** -- wenn der Agent im Aufruf einen angibt.
2. **`videoGenerationModel.primary`** -- aus der Konfiguration.
3. **`videoGenerationModel.fallbacks`** -- werden der Reihe nach versucht.
4. **Automatische Erkennung** -- verwendet Provider mit gültiger Authentifizierung, beginnend mit dem aktuellen Standard-Provider, dann die übrigen Provider in alphabetischer Reihenfolge.

Wenn ein Provider fehlschlägt, wird automatisch der nächste Kandidat versucht. Wenn alle Kandidaten fehlschlagen, enthält der Fehler Details zu jedem Versuch.

Setze `agents.defaults.mediaGenerationAutoProviderFallback: false`, wenn du möchtest,
dass die Videogenerierung nur die expliziten Einträge `model`, `primary` und `fallbacks`
verwendet.

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "google/veo-3.1-fast-generate-preview",
        fallbacks: ["runway/gen4.5", "qwen/wan2.6-t2v"],
      },
    },
  },
}
```

## Hinweise zu Providern

| Provider              | Hinweise                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Alibaba               | Verwendet den asynchronen DashScope-/Model-Studio-Endpunkt. Referenzbilder und -videos müssen Remote-`http(s)`-URLs sein.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| BytePlus (1.0)        | Provider-ID `byteplus`. Modelle: `seedance-1-0-pro-250528` (Standard), `seedance-1-0-pro-t2v-250528`, `seedance-1-0-pro-fast-251015`, `seedance-1-0-lite-t2v-250428`, `seedance-1-0-lite-i2v-250428`. T2V-Modelle (`*-t2v-*`) akzeptieren keine Bildeingaben; I2V-Modelle und allgemeine `*-pro-*`-Modelle unterstützen ein einzelnes Referenzbild (erster Frame). Übergib das Bild positionell oder setze `role: "first_frame"`. T2V-Modell-IDs werden automatisch auf die entsprechende I2V-Variante umgestellt, wenn ein Bild angegeben wird. Unterstützte `providerOptions`-Schlüssel: `seed` (number), `draft` (boolean, erzwingt 480p), `camera_fixed` (boolean). |
| BytePlus Seedance 1.5 | Erfordert das Plugin [`@openclaw/byteplus-modelark`](https://www.npmjs.com/package/@openclaw/byteplus-modelark). Provider-ID `byteplus-seedance15`. Modell: `seedance-1-5-pro-251215`. Verwendet die vereinheitlichte API `content[]`. Unterstützt höchstens 2 Eingabebilder (first_frame + last_frame). Alle Eingaben müssen Remote-`https://`-URLs sein. Setze `role: "first_frame"` / `"last_frame"` für jedes Bild oder übergib Bilder positionell. `aspectRatio: "adaptive"` erkennt das Verhältnis automatisch aus dem Eingabebild. `audio: true` wird auf `generate_audio` abgebildet. `providerOptions.seed` (number) wird weitergeleitet.                                                                 |
| BytePlus Seedance 2.0 | Erfordert das Plugin [`@openclaw/byteplus-modelark`](https://www.npmjs.com/package/@openclaw/byteplus-modelark). Provider-ID `byteplus-seedance2`. Modelle: `dreamina-seedance-2-0-260128`, `dreamina-seedance-2-0-fast-260128`. Verwendet die vereinheitlichte API `content[]`. Unterstützt bis zu 9 Referenzbilder, 3 Referenzvideos und 3 Referenz-Audiodateien. Alle Eingaben müssen Remote-`https://`-URLs sein. Setze `role` für jedes Asset — unterstützte Werte: `"first_frame"`, `"last_frame"`, `"reference_image"`, `"reference_video"`, `"reference_audio"`. `aspectRatio: "adaptive"` erkennt das Verhältnis automatisch aus dem Eingabebild. `audio: true` wird auf `generate_audio` abgebildet. `providerOptions.seed` (number) wird weitergeleitet. |
| ComfyUI               | Workflow-gesteuerte lokale oder Cloud-Ausführung. Unterstützt Text-zu-Video und Bild-zu-Video über den konfigurierten Graphen.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| fal                   | Verwendet einen queuebasierten Ablauf für lang laufende Aufträge. Nur eine einzelne Bildreferenz.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Google                | Verwendet Gemini/Veo. Unterstützt ein Bild oder ein Video als Referenz.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| MiniMax               | Nur eine einzelne Bildreferenz.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| OpenAI                | Nur das Override `size` wird weitergeleitet. Andere Stil-Overrides (`aspectRatio`, `resolution`, `audio`, `watermark`) werden mit einer Warnung ignoriert.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Qwen                  | Gleiches DashScope-Backend wie Alibaba. Referenzeingaben müssen Remote-`http(s)`-URLs sein; lokale Dateien werden vorab zurückgewiesen.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Runway                | Unterstützt lokale Dateien über Daten-URIs. Video-zu-Video erfordert `runway/gen4_aleph`. Rein textbasierte Läufe bieten die Seitenverhältnisse `16:9` und `9:16`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Together              | Nur eine einzelne Bildreferenz.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| Vydra                 | Verwendet `https://www.vydra.ai/api/v1` direkt, um Redirects zu vermeiden, bei denen die Authentifizierung verloren geht. `veo3` ist gebündelt nur als Text-zu-Video; `kling` erfordert eine Remote-Bild-URL.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| xAI                   | Unterstützt Text-zu-Video, Bild-zu-Video und Remote-Video-Bearbeitungs-/Erweiterungsabläufe.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |

## Provider-Fähigkeitsmodi

Der gemeinsame Vertrag für Videogenerierung erlaubt Providern jetzt, modusspezifische
Fähigkeiten zu deklarieren, statt nur flache aggregierte Grenzwerte. Neue Provider-
Implementierungen sollten explizite Modusblöcke bevorzugen:

```typescript
capabilities: {
  generate: {
    maxVideos: 1,
    maxDurationSeconds: 10,
    supportsResolution: true,
  },
  imageToVideo: {
    enabled: true,
    maxVideos: 1,
    maxInputImages: 1,
    maxDurationSeconds: 5,
  },
  videoToVideo: {
    enabled: true,
    maxVideos: 1,
    maxInputVideos: 1,
    maxDurationSeconds: 5,
  },
}
```

Flache aggregierte Felder wie `maxInputImages` und `maxInputVideos` reichen nicht
aus, um die Unterstützung von Transformationsmodi anzugeben. Provider sollten
`generate`, `imageToVideo` und `videoToVideo` explizit deklarieren, damit Live-Tests,
Vertragstests und das gemeinsame Tool `video_generate` die Modusunterstützung
deterministisch validieren können.

## Live-Tests

Opt-in-Live-Abdeckung für die gemeinsam gebündelten Provider:

```bash
OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts
```

Repo-Wrapper:

```bash
pnpm test:live:media video
```

Diese Live-Datei lädt fehlende Provider-Umgebungsvariablen aus `~/.profile`, bevorzugt
standardmäßig Live-/Umgebungs-API-Schlüssel vor gespeicherten Auth-Profilen und führt
standardmäßig einen release-sicheren Smoke-Test aus:

- `generate` für jeden Nicht-FAL-Provider im Sweep
- ein einsekündiger Hummer-Prompt
- operationsbezogene Obergrenze pro Provider aus `OPENCLAW_LIVE_VIDEO_GENERATION_TIMEOUT_MS`
  (`180000` standardmäßig)

FAL ist Opt-in, weil providerseitige Queue-Latenz die Release-Zeit dominieren kann:

```bash
pnpm test:live:media video --video-providers fal
```

Setze `OPENCLAW_LIVE_VIDEO_GENERATION_FULL_MODES=1`, um zusätzlich deklarierte Transformations-
modi auszuführen, die der gemeinsame Sweep sicher mit lokalen Medien testen kann:

- `imageToVideo`, wenn `capabilities.imageToVideo.enabled`
- `videoToVideo`, wenn `capabilities.videoToVideo.enabled` ist und der Provider/das Modell
  im gemeinsamen Sweep bufferbasierte lokale Videoeingaben akzeptiert

Heute deckt der gemeinsame Live-Kanal `videoToVideo` Folgendes ab:

- `runway` nur, wenn du `runway/gen4_aleph` auswählst

## Konfiguration

Lege das Standardmodell für die Videogenerierung in deiner OpenClaw-Konfiguration fest:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "qwen/wan2.6-t2v",
        fallbacks: ["qwen/wan2.6-r2v-flash"],
      },
    },
  },
}
```

Oder über die CLI:

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "qwen/wan2.6-t2v"
```

## Verwandte Themen

- [Tools Overview](/de/tools)
- [Hintergrundaufgaben](/de/automation/tasks) -- Aufgabenverfolgung für asynchrone Videogenerierung
- [Alibaba Model Studio](/de/providers/alibaba)
- [BytePlus](/de/concepts/model-providers#byteplus-international)
- [ComfyUI](/de/providers/comfy)
- [fal](/de/providers/fal)
- [Google (Gemini)](/de/providers/google)
- [MiniMax](/de/providers/minimax)
- [OpenAI](/de/providers/openai)
- [Qwen](/de/providers/qwen)
- [Runway](/de/providers/runway)
- [Together AI](/de/providers/together)
- [Vydra](/de/providers/vydra)
- [xAI](/de/providers/xai)
- [Configuration Reference](/de/gateway/configuration-reference#agent-defaults)
- [Modelle](/de/concepts/models)
