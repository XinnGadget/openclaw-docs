---
read_when:
    - Videos über den Agenten generieren
    - Provider und Modelle für die Videogenerierung konfigurieren
    - Die Parameter des Tools `video_generate` verstehen
summary: Erzeugen Sie Videos aus Text, Bildern oder vorhandenen Videos mit 12 Provider-Backends
title: Videogenerierung
x-i18n:
    generated_at: "2026-04-06T06:21:15Z"
    model: gpt-5.4
    provider: openai
    source_hash: 90d8a392b35adbd899232b02c55c10895b9d7ffc9858d6ca448f2e4e4a57f12f
    source_path: tools/video-generation.md
    workflow: 15
---

# Videogenerierung

OpenClaw-Agenten können Videos aus Text-Prompts, Referenzbildern oder vorhandenen Videos erzeugen. Zwölf Provider-Backends werden unterstützt, jeweils mit unterschiedlichen Modelloptionen, Eingabemodi und Funktionsumfängen. Der Agent wählt automatisch den richtigen Provider basierend auf Ihrer Konfiguration und den verfügbaren API-Schlüsseln aus.

<Note>
Das Tool `video_generate` wird nur angezeigt, wenn mindestens ein Provider für die Videogenerierung verfügbar ist. Wenn Sie es in Ihren Agenten-Tools nicht sehen, legen Sie einen API-Schlüssel für einen Provider fest oder konfigurieren Sie `agents.defaults.videoGenerationModel`.
</Note>

## Schnellstart

1. Legen Sie einen API-Schlüssel für einen beliebigen unterstützten Provider fest:

```bash
export GEMINI_API_KEY="your-key"
```

2. Optional ein Standardmodell festlegen:

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "google/veo-3.1-fast-generate-preview"
```

3. Fragen Sie den Agenten:

> Erzeuge ein 5-sekündiges cineastisches Video von einem freundlichen Hummer, der bei Sonnenuntergang surft.

Der Agent ruft `video_generate` automatisch auf. Kein Tool-Allowlisting ist erforderlich.

## Was passiert, wenn Sie ein Video erzeugen

Die Videogenerierung erfolgt asynchron. Wenn der Agent in einer Sitzung `video_generate` aufruft:

1. OpenClaw sendet die Anfrage an den Provider und gibt sofort eine Aufgaben-ID zurück.
2. Der Provider verarbeitet den Auftrag im Hintergrund (typischerweise 30 Sekunden bis 5 Minuten, abhängig von Provider und Auflösung).
3. Wenn das Video bereit ist, weckt OpenClaw dieselbe Sitzung mit einem internen Abschlussereignis auf.
4. Der Agent postet das fertige Video zurück in die ursprüngliche Unterhaltung.

Während ein Auftrag läuft, geben doppelte `video_generate`-Aufrufe in derselben Sitzung den aktuellen Aufgabenstatus zurück, anstatt eine weitere Generierung zu starten. Verwenden Sie `openclaw tasks list` oder `openclaw tasks show <taskId>`, um den Fortschritt über die CLI zu prüfen.

Außerhalb von sitzungsbasierten Agenten-Ausführungen (zum Beispiel bei direkten Tool-Aufrufen) greift das Tool auf die Inline-Generierung zurück und gibt im selben Durchlauf den endgültigen Medienpfad zurück.

## Unterstützte Provider

| Provider | Standardmodell                 | Text | Bildreferenz      | Videoreferenz    | API-Schlüssel                            |
| -------- | ------------------------------ | ---- | ----------------- | ---------------- | ---------------------------------------- |
| Alibaba  | `wan2.6-t2v`                   | Ja   | Ja (Remote-URL)   | Ja (Remote-URL)  | `MODELSTUDIO_API_KEY`                    |
| BytePlus | `seedance-1-0-lite-t2v-250428` | Ja   | 1 Bild            | Nein             | `BYTEPLUS_API_KEY`                       |
| ComfyUI  | `workflow`                     | Ja   | 1 Bild            | Nein             | `COMFY_API_KEY` oder `COMFY_CLOUD_API_KEY` |
| fal      | `fal-ai/minimax/video-01-live` | Ja   | 1 Bild            | Nein             | `FAL_KEY`                                |
| Google   | `veo-3.1-fast-generate-preview` | Ja  | 1 Bild            | 1 Video          | `GEMINI_API_KEY`                         |
| MiniMax  | `MiniMax-Hailuo-2.3`           | Ja   | 1 Bild            | Nein             | `MINIMAX_API_KEY`                        |
| OpenAI   | `sora-2`                       | Ja   | 1 Bild            | 1 Video          | `OPENAI_API_KEY`                         |
| Qwen     | `wan2.6-t2v`                   | Ja   | Ja (Remote-URL)   | Ja (Remote-URL)  | `QWEN_API_KEY`                           |
| Runway   | `gen4.5`                       | Ja   | 1 Bild            | 1 Video          | `RUNWAYML_API_SECRET`                    |
| Together | `Wan-AI/Wan2.2-T2V-A14B`       | Ja   | 1 Bild            | Nein             | `TOGETHER_API_KEY`                       |
| Vydra    | `veo3`                         | Ja   | 1 Bild (`kling`)  | Nein             | `VYDRA_API_KEY`                          |
| xAI      | `grok-imagine-video`           | Ja   | 1 Bild            | 1 Video          | `XAI_API_KEY`                            |

Einige Provider akzeptieren zusätzliche oder alternative API-Schlüssel-Umgebungsvariablen. Weitere Details finden Sie auf den einzelnen [Provider-Seiten](#related).

Führen Sie `video_generate action=list` aus, um verfügbare Provider und Modelle zur Laufzeit anzuzeigen.

## Tool-Parameter

### Erforderlich

| Parameter | Typ    | Beschreibung                                                                |
| --------- | ------ | --------------------------------------------------------------------------- |
| `prompt`  | string | Textbeschreibung des zu erzeugenden Videos (erforderlich für `action: "generate"`) |

### Inhaltseingaben

| Parameter | Typ      | Beschreibung                           |
| --------- | -------- | -------------------------------------- |
| `image`   | string   | Einzelnes Referenzbild (Pfad oder URL) |
| `images`  | string[] | Mehrere Referenzbilder (bis zu 5)      |
| `video`   | string   | Einzelnes Referenzvideo (Pfad oder URL) |
| `videos`  | string[] | Mehrere Referenzvideos (bis zu 4)      |

### Stilsteuerungen

| Parameter         | Typ     | Beschreibung                                                           |
| ----------------- | ------- | ---------------------------------------------------------------------- |
| `aspectRatio`     | string  | `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` |
| `resolution`      | string  | `480P`, `720P` oder `1080P`                                            |
| `durationSeconds` | number  | Zieldauer in Sekunden (auf den nächsten vom Provider unterstützten Wert gerundet) |
| `size`            | string  | Größenhinweis, wenn der Provider dies unterstützt                      |
| `audio`           | boolean | Generierten Ton aktivieren, wenn unterstützt                           |
| `watermark`       | boolean | Wasserzeichen des Providers aktivieren/deaktivieren, wenn unterstützt  |

### Erweitert

| Parameter  | Typ    | Beschreibung                                      |
| ---------- | ------ | ------------------------------------------------- |
| `action`   | string | `"generate"` (Standard), `"status"` oder `"list"` |
| `model`    | string | Provider-/Modell-Override (z. B. `runway/gen4.5`) |
| `filename` | string | Hinweis für den Ausgabedateinamen                 |

Nicht alle Provider unterstützen alle Parameter. Nicht unterstützte Overrides werden nach bestem Bemühen ignoriert und als Warnungen im Tool-Ergebnis gemeldet. Harte Funktionsgrenzen (wie zu viele Referenzeingaben) schlagen vor dem Absenden fehl.

## Aktionen

- **generate** (Standard) -- erzeugt ein Video aus dem angegebenen Prompt und optionalen Referenzeingaben.
- **status** -- prüft den Status der laufenden Videoaufgabe für die aktuelle Sitzung, ohne eine weitere Generierung zu starten.
- **list** -- zeigt verfügbare Provider, Modelle und ihre Fähigkeiten an.

## Modellauswahl

Beim Erzeugen eines Videos löst OpenClaw das Modell in dieser Reihenfolge auf:

1. **`model`-Tool-Parameter** -- wenn der Agent beim Aufruf einen angibt.
2. **`videoGenerationModel.primary`** -- aus der Konfiguration.
3. **`videoGenerationModel.fallbacks`** -- wird der Reihe nach versucht.
4. **Automatische Erkennung** -- verwendet Provider mit gültiger Authentifizierung, beginnend mit dem aktuellen Standard-Provider, danach die übrigen Provider in alphabetischer Reihenfolge.

Wenn ein Provider fehlschlägt, wird automatisch der nächste Kandidat versucht. Wenn alle Kandidaten fehlschlagen, enthält der Fehler Details zu jedem Versuch.

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

| Provider | Hinweise                                                                                                                                                    |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Alibaba  | Verwendet den asynchronen DashScope-/Model-Studio-Endpunkt. Referenzbilder und -videos müssen entfernte `http(s)`-URLs sein.                              |
| BytePlus | Nur eine einzelne Bildreferenz.                                                                                                                             |
| ComfyUI  | Workflow-gesteuerte lokale oder Cloud-Ausführung. Unterstützt Text-zu-Video und Bild-zu-Video über den konfigurierten Graphen.                            |
| fal      | Verwendet einen warteschlangenbasierten Ablauf für lang laufende Aufträge. Nur eine einzelne Bildreferenz.                                                 |
| Google   | Verwendet Gemini/Veo. Unterstützt ein Bild oder eine Videoreferenz.                                                                                         |
| MiniMax  | Nur eine einzelne Bildreferenz.                                                                                                                             |
| OpenAI   | Nur der Override `size` wird weitergeleitet. Andere Stil-Overrides (`aspectRatio`, `resolution`, `audio`, `watermark`) werden mit einer Warnung ignoriert. |
| Qwen     | Dasselbe DashScope-Backend wie Alibaba. Referenzeingaben müssen entfernte `http(s)`-URLs sein; lokale Dateien werden vorab abgelehnt.                     |
| Runway   | Unterstützt lokale Dateien über Daten-URIs. Video-zu-Video erfordert `runway/gen4_aleph`. Reine Textläufe bieten die Seitenverhältnisse `16:9` und `9:16`. |
| Together | Nur eine einzelne Bildreferenz.                                                                                                                             |
| Vydra    | Verwendet `https://www.vydra.ai/api/v1` direkt, um Weiterleitungen zu vermeiden, bei denen die Authentifizierung verloren geht. `veo3` ist nur als Text-zu-Video gebündelt; `kling` erfordert eine entfernte Bild-URL. |
| xAI      | Unterstützt Text-zu-Video, Bild-zu-Video und entfernte Abläufe zum Bearbeiten/Erweitern von Videos.                                                        |

## Konfiguration

Legen Sie das Standardmodell für die Videogenerierung in Ihrer OpenClaw-Konfiguration fest:

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

## Verwandt

- [Tools-Übersicht](/de/tools)
- [Hintergrundaufgaben](/de/automation/tasks) -- Aufgabenverfolgung für die asynchrone Videogenerierung
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
- [Konfigurationsreferenz](/de/gateway/configuration-reference#agent-defaults)
- [Modelle](/de/concepts/models)
