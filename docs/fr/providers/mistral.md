---
read_when:
    - Vous souhaitez utiliser des modèles Mistral dans OpenClaw
    - Vous avez besoin de l’onboarding avec clé API Mistral et des références de modèles
summary: Utiliser les modèles Mistral et la transcription Voxtral avec OpenClaw
title: Mistral
x-i18n:
    generated_at: "2026-04-12T23:31:35Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0474f55587909ce9bbdd47b881262edbeb1b07eb3ed52de1090a8ec4d260c97b
    source_path: providers/mistral.md
    workflow: 15
---

# Mistral

OpenClaw prend en charge Mistral à la fois pour le routage des modèles texte/image (`mistral/...`) et
la transcription audio via Voxtral dans la compréhension des médias.
Mistral peut aussi être utilisé pour les embeddings de mémoire (`memorySearch.provider = "mistral"`).

- Fournisseur : `mistral`
- Auth : `MISTRAL_API_KEY`
- API : Mistral Chat Completions (`https://api.mistral.ai/v1`)

## Prise en main

<Steps>
  <Step title="Obtenir votre clé API">
    Créez une clé API dans la [console Mistral](https://console.mistral.ai/).
  </Step>
  <Step title="Exécuter l’onboarding">
    ```bash
    openclaw onboard --auth-choice mistral-api-key
    ```

    Ou transmettez directement la clé :

    ```bash
    openclaw onboard --mistral-api-key "$MISTRAL_API_KEY"
    ```

  </Step>
  <Step title="Définir un modèle par défaut">
    ```json5
    {
      env: { MISTRAL_API_KEY: "sk-..." },
      agents: { defaults: { model: { primary: "mistral/mistral-large-latest" } } },
    }
    ```
  </Step>
  <Step title="Vérifier que le modèle est disponible">
    ```bash
    openclaw models list --provider mistral
    ```
  </Step>
</Steps>

## Catalogue LLM intégré

OpenClaw inclut actuellement ce catalogue Mistral intégré :

| Référence de modèle             | Entrée      | Contexte | Sortie max | Notes                                                             |
| -------------------------------- | ----------- | ------- | ---------- | ----------------------------------------------------------------- |
| `mistral/mistral-large-latest`   | text, image | 262,144 | 16,384     | Modèle par défaut                                                 |
| `mistral/mistral-medium-2508`    | text, image | 262,144 | 8,192      | Mistral Medium 3.1                                                |
| `mistral/mistral-small-latest`   | text, image | 128,000 | 16,384     | Mistral Small 4 ; raisonnement ajustable via l’API `reasoning_effort` |
| `mistral/pixtral-large-latest`   | text, image | 128,000 | 32,768     | Pixtral                                                           |
| `mistral/codestral-latest`       | text        | 256,000 | 4,096      | Code                                                              |
| `mistral/devstral-medium-latest` | text        | 262,144 | 32,768     | Devstral 2                                                        |
| `mistral/magistral-small`        | text        | 128,000 | 40,000     | Raisonnement activé                                               |

## Transcription audio (Voxtral)

Utilisez Voxtral pour la transcription audio via le pipeline de compréhension des médias.

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        models: [{ provider: "mistral", model: "voxtral-mini-latest" }],
      },
    },
  },
}
```

<Tip>
La voie de transcription média utilise `/v1/audio/transcriptions`. Le modèle audio par défaut pour Mistral est `voxtral-mini-latest`.
</Tip>

## Configuration avancée

<AccordionGroup>
  <Accordion title="Raisonnement ajustable (mistral-small-latest)">
    `mistral/mistral-small-latest` correspond à Mistral Small 4 et prend en charge le [raisonnement ajustable](https://docs.mistral.ai/capabilities/reasoning/adjustable) sur l’API Chat Completions via `reasoning_effort` (`none` réduit au minimum la réflexion supplémentaire dans la sortie ; `high` expose les traces de réflexion complètes avant la réponse finale).

    OpenClaw mappe le niveau de **thinking** de la session sur l’API Mistral :

    | Niveau de thinking OpenClaw                     | `reasoning_effort` Mistral |
    | ------------------------------------------------ | -------------------------- |
    | **off** / **minimal**                            | `none`                     |
    | **low** / **medium** / **high** / **xhigh** / **adaptive** | `high`             |

    <Note>
    Les autres modèles du catalogue Mistral intégré n’utilisent pas ce paramètre. Continuez à utiliser les modèles `magistral-*` lorsque vous souhaitez le comportement natif de Mistral orienté raisonnement en priorité.
    </Note>

  </Accordion>

  <Accordion title="Embeddings de mémoire">
    Mistral peut servir des embeddings de mémoire via `/v1/embeddings` (modèle par défaut : `mistral-embed`).

    ```json5
    {
      memorySearch: { provider: "mistral" },
    }
    ```

  </Accordion>

  <Accordion title="Auth et URL de base">
    - L’auth Mistral utilise `MISTRAL_API_KEY`.
    - L’URL de base du fournisseur est par défaut `https://api.mistral.ai/v1`.
    - Le modèle par défaut de l’onboarding est `mistral/mistral-large-latest`.
    - Z.AI utilise l’auth Bearer avec votre clé API.
  </Accordion>
</AccordionGroup>

## Liens associés

<CardGroup cols={2}>
  <Card title="Model selection" href="/fr/concepts/model-providers" icon="layers">
    Choisir les fournisseurs, les références de modèles et le comportement de basculement.
  </Card>
  <Card title="Media understanding" href="/tools/media-understanding" icon="microphone">
    Configuration de la transcription audio et sélection du fournisseur.
  </Card>
</CardGroup>
