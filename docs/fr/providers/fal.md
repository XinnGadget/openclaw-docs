---
read_when:
    - Vous souhaitez utiliser la génération d’images fal dans OpenClaw
    - Vous avez besoin du flux d’auth `FAL_KEY`
    - Vous souhaitez les valeurs par défaut fal pour `image_generate` ou `video_generate`
summary: Configuration de la génération d’images et de vidéos fal dans OpenClaw
title: fal
x-i18n:
    generated_at: "2026-04-12T23:30:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: ff275233179b4808d625383efe04189ad9e92af09944ba39f1e953e77378e347
    source_path: providers/fal.md
    workflow: 15
---

# fal

OpenClaw inclut un fournisseur `fal` intégré pour la génération hébergée d’images et de vidéos.

| Propriété | Valeur                                                        |
| --------- | ------------------------------------------------------------- |
| Fournisseur | `fal`                                                       |
| Auth      | `FAL_KEY` (canonique ; `FAL_API_KEY` fonctionne aussi en repli) |
| API       | points de terminaison de modèles fal                          |

## Prise en main

<Steps>
  <Step title="Définir la clé API">
    ```bash
    openclaw onboard --auth-choice fal-api-key
    ```
  </Step>
  <Step title="Définir un modèle d’image par défaut">
    ```json5
    {
      agents: {
        defaults: {
          imageGenerationModel: {
            primary: "fal/fal-ai/flux/dev",
          },
        },
      },
    }
    ```
  </Step>
</Steps>

## Génération d’images

Le fournisseur intégré de génération d’images `fal` utilise par défaut
`fal/fal-ai/flux/dev`.

| Capacité         | Valeur                     |
| ---------------- | -------------------------- |
| Nombre max d’images | 4 par requête           |
| Mode édition     | Activé, 1 image de référence |
| Remplacements de taille | Pris en charge       |
| Ratio d’aspect   | Pris en charge             |
| Résolution       | Prise en charge            |

<Warning>
Le point de terminaison d’édition d’image fal ne prend **pas** en charge les remplacements `aspectRatio`.
</Warning>

Pour utiliser fal comme fournisseur d’images par défaut :

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "fal/fal-ai/flux/dev",
      },
    },
  },
}
```

## Génération de vidéos

Le fournisseur intégré de génération de vidéos `fal` utilise par défaut
`fal/fal-ai/minimax/video-01-live`.

| Capacité | Valeur                                                        |
| -------- | ------------------------------------------------------------- |
| Modes    | Texte vers vidéo, image de référence unique                   |
| Runtime  | Flux submit/status/result adossé à une file d’attente pour les tâches longues |

<AccordionGroup>
  <Accordion title="Modèles vidéo disponibles">
    **HeyGen video-agent :**

    - `fal/fal-ai/heygen/v2/video-agent`

    **Seedance 2.0 :**

    - `fal/bytedance/seedance-2.0/fast/text-to-video`
    - `fal/bytedance/seedance-2.0/fast/image-to-video`
    - `fal/bytedance/seedance-2.0/text-to-video`
    - `fal/bytedance/seedance-2.0/image-to-video`

  </Accordion>

  <Accordion title="Exemple de configuration Seedance 2.0">
    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "fal/bytedance/seedance-2.0/fast/text-to-video",
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="Exemple de configuration HeyGen video-agent">
    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "fal/fal-ai/heygen/v2/video-agent",
          },
        },
      },
    }
    ```
  </Accordion>
</AccordionGroup>

<Tip>
Utilisez `openclaw models list --provider fal` pour voir la liste complète des modèles fal
disponibles, y compris les entrées ajoutées récemment.
</Tip>

## Liens associés

<CardGroup cols={2}>
  <Card title="Image generation" href="/fr/tools/image-generation" icon="image">
    Paramètres partagés de l’outil d’image et sélection du fournisseur.
  </Card>
  <Card title="Video generation" href="/fr/tools/video-generation" icon="video">
    Paramètres partagés de l’outil vidéo et sélection du fournisseur.
  </Card>
  <Card title="Configuration reference" href="/fr/gateway/configuration-reference#agent-defaults" icon="gear">
    Valeurs par défaut de l’agent, y compris la sélection des modèles d’image et de vidéo.
  </Card>
</CardGroup>
