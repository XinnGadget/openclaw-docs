---
read_when:
    - Bilder über den Agenten generieren
    - Anbieter und Modelle für die Bildgenerierung konfigurieren
    - Die Parameter des Tools `image_generate` verstehen
summary: Bilder mit konfigurierten Anbietern erstellen und bearbeiten (OpenAI, Google Gemini, fal, MiniMax, ComfyUI, Vydra)
title: Bildgenerierung
x-i18n:
    generated_at: "2026-04-06T06:21:07Z"
    model: gpt-5.4
    provider: openai
    source_hash: 903cc522c283a8da2cbd449ae3e25f349a74d00ecfdaf0f323fd8aa3f2107aea
    source_path: tools/image-generation.md
    workflow: 15
---

# Bildgenerierung

Das Tool `image_generate` ermöglicht es dem Agenten, Bilder mit Ihren konfigurierten Anbietern zu erstellen und zu bearbeiten. Generierte Bilder werden automatisch als Medienanhänge in der Antwort des Agenten bereitgestellt.

<Note>
Das Tool erscheint nur, wenn mindestens ein Anbieter für die Bildgenerierung verfügbar ist. Wenn `image_generate` nicht in den Tools Ihres Agenten angezeigt wird, konfigurieren Sie `agents.defaults.imageGenerationModel` oder richten Sie einen API-Schlüssel für einen Anbieter ein.
</Note>

## Schnellstart

1. Legen Sie für mindestens einen Anbieter einen API-Schlüssel fest (zum Beispiel `OPENAI_API_KEY` oder `GEMINI_API_KEY`).
2. Legen Sie optional Ihr bevorzugtes Modell fest:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "openai/gpt-image-1",
      },
    },
  },
}
```

3. Fragen Sie den Agenten: _„Erstelle ein Bild eines freundlichen Hummer-Maskottchens.“_

Der Agent ruft `image_generate` automatisch auf. Keine Tool-Positivliste erforderlich — es ist standardmäßig aktiviert, wenn ein Anbieter verfügbar ist.

## Unterstützte Anbieter

| Anbieter | Standardmodell                  | Bearbeitungsunterstützung          | API-Schlüssel                                          |
| -------- | -------------------------------- | ---------------------------------- | ----------------------------------------------------- |
| OpenAI   | `gpt-image-1`                    | Ja (bis zu 5 Bilder)               | `OPENAI_API_KEY`                                      |
| Google   | `gemini-3.1-flash-image-preview` | Ja                                 | `GEMINI_API_KEY` oder `GOOGLE_API_KEY`                |
| fal      | `fal-ai/flux/dev`                | Ja                                 | `FAL_KEY`                                             |
| MiniMax  | `image-01`                       | Ja (Subjektreferenz)               | `MINIMAX_API_KEY` oder MiniMax OAuth (`minimax-portal`) |
| ComfyUI  | `workflow`                       | Ja (1 Bild, im Workflow konfiguriert) | `COMFY_API_KEY` oder `COMFY_CLOUD_API_KEY` für die Cloud |
| Vydra    | `grok-imagine`                   | Nein                               | `VYDRA_API_KEY`                                       |

Verwenden Sie `action: "list"`, um verfügbare Anbieter und Modelle zur Laufzeit zu prüfen:

```
/tool image_generate action=list
```

## Tool-Parameter

| Parameter     | Typ      | Beschreibung                                                                         |
| ------------- | -------- | ------------------------------------------------------------------------------------ |
| `prompt`      | string   | Prompt für die Bildgenerierung (erforderlich für `action: "generate"`)               |
| `action`      | string   | `"generate"` (Standard) oder `"list"` zum Prüfen von Anbietern                       |
| `model`       | string   | Anbieter-/Modell-Überschreibung, z. B. `openai/gpt-image-1`                          |
| `image`       | string   | Einzelner Referenzbildpfad oder URL für den Bearbeitungsmodus                        |
| `images`      | string[] | Mehrere Referenzbilder für den Bearbeitungsmodus (bis zu 5)                          |
| `size`        | string   | Größenhinweis: `1024x1024`, `1536x1024`, `1024x1536`, `1024x1792`, `1792x1024`       |
| `aspectRatio` | string   | Seitenverhältnis: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` |
| `resolution`  | string   | Auflösungshinweis: `1K`, `2K` oder `4K`                                              |
| `count`       | number   | Anzahl der zu generierenden Bilder (1–4)                                             |
| `filename`    | string   | Hinweis für den Ausgabedateinamen                                                    |

Nicht alle Anbieter unterstützen alle Parameter. Das Tool übergibt, was jeder Anbieter unterstützt, ignoriert den Rest und meldet verworfene Überschreibungen im Tool-Ergebnis.

## Konfiguration

### Modellauswahl

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "openai/gpt-image-1",
        fallbacks: ["google/gemini-3.1-flash-image-preview", "fal/fal-ai/flux/dev"],
      },
    },
  },
}
```

### Reihenfolge der Anbieterauswahl

Beim Generieren eines Bildes versucht OpenClaw Anbieter in dieser Reihenfolge:

1. Parameter **`model`** aus dem Tool-Aufruf (wenn der Agent einen angibt)
2. **`imageGenerationModel.primary`** aus der Konfiguration
3. **`imageGenerationModel.fallbacks`** in Reihenfolge
4. **Automatische Erkennung** — verwendet nur authentifizierungsbasierte Anbieterstandards:
   - zuerst den aktuellen Standardanbieter
   - verbleibende registrierte Anbieter für Bildgenerierung in der Reihenfolge ihrer Anbieter-IDs

Wenn ein Anbieter fehlschlägt (Authentifizierungsfehler, Ratenbegrenzung usw.), wird automatisch der nächste Kandidat versucht. Wenn alle fehlschlagen, enthält der Fehler Details aus jedem Versuch.

Hinweise:

- Die automatische Erkennung ist authentifizierungsbewusst. Ein Anbieterstandard wird nur dann in die Kandidatenliste aufgenommen,
  wenn OpenClaw diesen Anbieter tatsächlich authentifizieren kann.
- Verwenden Sie `action: "list"`, um die aktuell registrierten Anbieter, ihre
  Standardmodelle und Hinweise zu Authentifizierungs-Umgebungsvariablen zu prüfen.

### Bildbearbeitung

OpenAI, Google, fal, MiniMax und ComfyUI unterstützen das Bearbeiten von Referenzbildern. Übergeben Sie einen Referenzbildpfad oder eine URL:

```
"Erstelle eine Aquarellversion dieses Fotos" + image: "/path/to/photo.jpg"
```

OpenAI und Google unterstützen bis zu 5 Referenzbilder über den Parameter `images`. fal, MiniMax und ComfyUI unterstützen 1.

Die Bildgenerierung mit MiniMax ist über beide gebündelten MiniMax-Authentifizierungspfade verfügbar:

- `minimax/image-01` für Setups mit API-Schlüssel
- `minimax-portal/image-01` für Setups mit OAuth

## Anbieterfunktionen

| Funktion              | OpenAI               | Google               | fal                 | MiniMax                    | ComfyUI                            | Vydra   |
| --------------------- | -------------------- | -------------------- | ------------------- | -------------------------- | ---------------------------------- | ------- |
| Generieren            | Ja (bis zu 4)        | Ja (bis zu 4)        | Ja (bis zu 4)       | Ja (bis zu 9)              | Ja (workflowdefinierte Ausgaben)   | Ja (1) |
| Bearbeiten/Referenz   | Ja (bis zu 5 Bilder) | Ja (bis zu 5 Bilder) | Ja (1 Bild)         | Ja (1 Bild, Subjektreferenz) | Ja (1 Bild, im Workflow konfiguriert) | Nein    |
| Größensteuerung       | Ja                   | Ja                   | Ja                  | Nein                       | Nein                               | Nein    |
| Seitenverhältnis      | Nein                 | Ja                   | Ja (nur Generierung) | Ja                        | Nein                               | Nein    |
| Auflösung (1K/2K/4K)  | Nein                 | Ja                   | Ja                  | Nein                       | Nein                               | Nein    |

## Verwandt

- [Tools Overview](/de/tools) — alle verfügbaren Agenten-Tools
- [fal](/de/providers/fal) — Einrichtung des fal-Anbieters für Bilder und Videos
- [ComfyUI](/de/providers/comfy) — Einrichtung lokaler ComfyUI- und Comfy-Cloud-Workflows
- [Google (Gemini)](/de/providers/google) — Einrichtung des Gemini-Bildanbieters
- [MiniMax](/de/providers/minimax) — Einrichtung des MiniMax-Bildanbieters
- [OpenAI](/de/providers/openai) — Einrichtung des OpenAI-Images-Anbieters
- [Vydra](/de/providers/vydra) — Einrichtung von Vydra für Bilder, Videos und Sprache
- [Configuration Reference](/de/gateway/configuration-reference#agent-defaults) — Konfiguration von `imageGenerationModel`
- [Models](/de/concepts/models) — Modellkonfiguration und Failover
