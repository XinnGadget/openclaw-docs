---
x-i18n:
    generated_at: "2026-04-11T15:15:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2a8884fc2c304bf96d4675f0c1d1ff781d6dc1ae8c49d92ce08040c9c7709035
    source_path: reference/rich-output-protocol.md
    workflow: 15
---

# Protocole de sortie enrichie

La sortie de l’assistant peut inclure un petit ensemble de directives de livraison/rendu :

- `MEDIA:` pour la livraison de pièces jointes
- `[[audio_as_voice]]` pour les indications de présentation audio
- `[[reply_to_current]]` / `[[reply_to:<id>]]` pour les métadonnées de réponse
- `[embed ...]` pour le rendu enrichi dans l’interface de contrôle

Ces directives sont distinctes. `MEDIA:` et les balises de réponse/voix restent des métadonnées de livraison ; `[embed ...]` est le chemin de rendu enrichi réservé au web.

## `[embed ...]`

`[embed ...]` est la seule syntaxe de rendu enrichi destinée aux agents pour l’interface de contrôle.

Exemple autofermant :

```text
[embed ref="cv_123" title="Status" /]
```

Règles :

- `[view ...]` n’est plus valide pour les nouvelles sorties.
- Les shortcodes embed s’affichent uniquement dans la surface de message de l’assistant.
- Seuls les embeds adossés à une URL sont rendus. Utilisez `ref="..."` ou `url="..."`.
- Les shortcodes embed en HTML inline sous forme de bloc ne sont pas rendus.
- L’interface web supprime le shortcode du texte visible et rend l’embed en ligne.
- `MEDIA:` n’est pas un alias d’embed et ne doit pas être utilisé pour le rendu enrichi d’embed.

## Forme de rendu stockée

Le bloc de contenu normalisé/stocké de l’assistant est un élément structuré `canvas` :

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

Les blocs enrichis stockés/rendus utilisent directement cette forme `canvas`. `present_view` n’est pas reconnu.
