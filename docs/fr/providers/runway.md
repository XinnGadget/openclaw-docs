---
read_when:
    - Vous souhaitez utiliser la génération vidéo Runway dans OpenClaw
    - Vous avez besoin de la configuration de la clé API / des variables d’environnement Runway
    - Vous souhaitez faire de Runway le fournisseur vidéo par défaut
summary: Configuration de la génération vidéo Runway dans OpenClaw
title: Runway
x-i18n:
    generated_at: "2026-04-12T23:32:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: fb9a2d26687920544222b0769f314743af245629fd45b7f456c0161a47476176
    source_path: providers/runway.md
    workflow: 15
---

# Runway

OpenClaw inclut un fournisseur bundled `runway` pour la génération vidéo hébergée.

| Property    | Value                                                             |
| ----------- | ----------------------------------------------------------------- |
| Id du fournisseur | `runway`                                                          |
| Auth        | `RUNWAYML_API_SECRET` (canonique) ou `RUNWAY_API_KEY`             |
| API         | Génération vidéo Runway basée sur des tâches (`GET /v1/tasks/{id}` avec interrogation) |

## Premiers pas

<Steps>
  <Step title="Définir la clé API">
    ```bash
    openclaw onboard --auth-choice runway-api-key
    ```
  </Step>
  <Step title="Définir Runway comme fournisseur vidéo par défaut">
    ```bash
    openclaw config set agents.defaults.videoGenerationModel.primary "runway/gen4.5"
    ```
  </Step>
  <Step title="Générer une vidéo">
    Demandez à l’agent de générer une vidéo. Runway sera utilisé automatiquement.
  </Step>
</Steps>

## Modes pris en charge

| Mode           | Modèle              | Entrée de référence         |
| -------------- | ------------------ | ----------------------- |
| Texte vers vidéo  | `gen4.5` (par défaut) | Aucune                    |
| Image vers vidéo | `gen4.5`           | 1 image locale ou distante |
| Vidéo vers vidéo | `gen4_aleph`       | 1 vidéo locale ou distante |

<Note>
Les références locales d’image et de vidéo sont prises en charge via des URI de données. Les exécutions en texte seul
exposent actuellement les formats `16:9` et `9:16`.
</Note>

<Warning>
Le mode vidéo vers vidéo nécessite actuellement spécifiquement `runway/gen4_aleph`.
</Warning>

## Configuration

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "runway/gen4.5",
      },
    },
  },
}
```

## Notes avancées

<AccordionGroup>
  <Accordion title="Alias de variables d’environnement">
    OpenClaw reconnaît à la fois `RUNWAYML_API_SECRET` (canonique) et `RUNWAY_API_KEY`.
    L’une ou l’autre variable authentifiera le fournisseur Runway.
  </Accordion>

  <Accordion title="Interrogation des tâches">
    Runway utilise une API basée sur des tâches. Après avoir soumis une demande de génération, OpenClaw
    interroge `GET /v1/tasks/{id}` jusqu’à ce que la vidéo soit prête. Aucune configuration supplémentaire
    n’est nécessaire pour ce comportement d’interrogation.
  </Accordion>
</AccordionGroup>

## Lié à ce sujet

<CardGroup cols={2}>
  <Card title="Génération vidéo" href="/fr/tools/video-generation" icon="video">
    Paramètres d’outil partagés, sélection du fournisseur et comportement asynchrone.
  </Card>
  <Card title="Référence de configuration" href="/fr/gateway/configuration-reference#agent-defaults" icon="gear">
    Paramètres par défaut de l’agent, y compris le modèle de génération vidéo.
  </Card>
</CardGroup>
