---
x-i18n:
    generated_at: "2026-04-11T15:15:49Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2a8884fc2c304bf96d4675f0c1d1ff781d6dc1ae8c49d92ce08040c9c7709035
    source_path: reference/rich-output-protocol.md
    workflow: 15
---

# Rich-Output-Protokoll

Die Assistentenausgabe kann eine kleine Menge an Übermittlungs-/Render-Anweisungen enthalten:

- `MEDIA:` für die Zustellung von Anhängen
- `[[audio_as_voice]]` für Hinweise zur Audio-Wiedergabe
- `[[reply_to_current]]` / `[[reply_to:<id>]]` für Antwort-Metadaten
- `[embed ...]` für umfangreiches Rendering in der Control UI

Diese Anweisungen sind getrennt. `MEDIA:` sowie Antwort-/Sprach-Tags bleiben Übermittlungsmetadaten; `[embed ...]` ist der reine Rich-Render-Pfad für das Web.

## `[embed ...]`

`[embed ...]` ist die einzige agentenseitige Syntax für umfangreiches Rendering in der Control UI.

Selbstschließendes Beispiel:

```text
[embed ref="cv_123" title="Status" /]
```

Regeln:

- `[view ...]` ist für neue Ausgaben nicht mehr gültig.
- Embed-Shortcodes werden nur in der Nachrichtenoberfläche des Assistenten gerendert.
- Nur URL-basierte Embeds werden gerendert. Verwende `ref="..."` oder `url="..."`.
- Inline-HTML-Embed-Shortcodes in Blockform werden nicht gerendert.
- Die Web-UI entfernt den Shortcode aus dem sichtbaren Text und rendert das Embed inline.
- `MEDIA:` ist kein Alias für Embeds und sollte nicht für umfangreiches Embed-Rendering verwendet werden.

## Gespeicherte Rendering-Struktur

Der normalisierte/gespeicherte Inhaltsblock des Assistenten ist ein strukturiertes `canvas`-Element:

```json
{
  "type": "canvas",
  "preview": {
    "kind": "canvas",
    "surface": "assistant_message",
    "render": "url",
    "viewId": "cv_123",
    "url": "/__openclaw__/canvas/documents/cv_123/index.html",
    "title": "Status",
    "preferredHeight": 320
  }
}
```

Gespeicherte/gerenderte Rich-Blöcke verwenden direkt diese `canvas`-Struktur. `present_view` wird nicht erkannt.
