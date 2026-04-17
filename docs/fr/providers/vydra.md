---
read_when:
    - Vous souhaitez la génération de médias Vydra dans OpenClaw
    - Vous avez besoin d’instructions pour la configuration de la clé API Vydra
summary: Utiliser l’image, la vidéo et la voix Vydra dans OpenClaw
title: Vydra
x-i18n:
    generated_at: "2026-04-12T23:33:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: ab623d14b656ce0b68d648a6393fcee3bb880077d6583e0d5c1012e91757f20e
    source_path: providers/vydra.md
    workflow: 15
---

# Vydra

Le Plugin Vydra bundled ajoute :

- La génération d’images via `vydra/grok-imagine`
- La génération de vidéos via `vydra/veo3` et `vydra/kling`
- La synthèse vocale via la route TTS de Vydra adossée à ElevenLabs

OpenClaw utilise la même `VYDRA_API_KEY` pour ces trois capacités.

<Warning>
Utilisez `https://www.vydra.ai/api/v1` comme base URL.

L’hôte apex de Vydra (`https://vydra.ai/api/v1`) redirige actuellement vers `www`. Certains clients HTTP suppriment `Authorization` lors de cette redirection entre hôtes, ce qui transforme une clé API valide en un échec d’authentification trompeur. Le plugin bundled utilise directement la base URL `www` pour éviter cela.
</Warning>

## Configuration

<Steps>
  <Step title="Lancer l’intégration interactive">
    ```bash
    openclaw onboard --auth-choice vydra-api-key
    ```

    Ou définissez directement la variable d’environnement :

    ```bash
    export VYDRA_API_KEY="vydra_live_..."
    ```

  </Step>
  <Step title="Choisir une capacité par défaut">
    Choisissez une ou plusieurs des capacités ci-dessous (image, vidéo ou voix) et appliquez la configuration correspondante.
  </Step>
</Steps>

## Capacités

<AccordionGroup>
  <Accordion title="Génération d’images">
    Modèle d’image par défaut :

    - `vydra/grok-imagine`

    Définissez-le comme fournisseur d’images par défaut :

    ```json5
    {
      agents: {
        defaults: {
          imageGenerationModel: {
            primary: "vydra/grok-imagine",
          },
        },
      },
    }
    ```

    La prise en charge bundled actuelle couvre uniquement le texte vers image. Les routes d’édition hébergées de Vydra attendent des URL d’image distantes, et OpenClaw n’ajoute pas encore de pont de téléversement spécifique à Vydra dans le plugin bundled.

    <Note>
    Voir [Génération d’images](/fr/tools/image-generation) pour les paramètres d’outil partagés, la sélection du fournisseur et le comportement de failover.
    </Note>

  </Accordion>

  <Accordion title="Génération de vidéos">
    Modèles vidéo enregistrés :

    - `vydra/veo3` pour le texte vers vidéo
    - `vydra/kling` pour l’image vers vidéo

    Définissez Vydra comme fournisseur vidéo par défaut :

    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "vydra/veo3",
          },
        },
      },
    }
    ```

    Remarques :

    - `vydra/veo3` est bundled uniquement en texte vers vidéo.
    - `vydra/kling` nécessite actuellement une référence d’URL d’image distante. Les téléversements de fichiers locaux sont rejetés d’emblée.
    - La route HTTP `kling` actuelle de Vydra n’est pas cohérente quant à savoir si elle exige `image_url` ou `video_url` ; le fournisseur bundled mappe la même URL d’image distante dans les deux champs.
    - Le plugin bundled reste prudent et ne transmet pas les réglages de style non documentés tels que le ratio d’aspect, la résolution, le filigrane ou l’audio généré.

    <Note>
    Voir [Génération vidéo](/fr/tools/video-generation) pour les paramètres d’outil partagés, la sélection du fournisseur et le comportement de failover.
    </Note>

  </Accordion>

  <Accordion title="Tests live vidéo">
    Couverture live spécifique au fournisseur :

    ```bash
    OPENCLAW_LIVE_TEST=1 \
    OPENCLAW_LIVE_VYDRA_VIDEO=1 \
    pnpm test:live -- extensions/vydra/vydra.live.test.ts
    ```

    Le fichier live Vydra bundled couvre désormais :

    - `vydra/veo3` texte vers vidéo
    - `vydra/kling` image vers vidéo à l’aide d’une URL d’image distante

    Remplacez le fixture d’image distante si nécessaire :

    ```bash
    export OPENCLAW_LIVE_VYDRA_KLING_IMAGE_URL="https://example.com/reference.png"
    ```

  </Accordion>

  <Accordion title="Synthèse vocale">
    Définissez Vydra comme fournisseur de voix :

    ```json5
    {
      messages: {
        tts: {
          provider: "vydra",
          providers: {
            vydra: {
              apiKey: "${VYDRA_API_KEY}",
              voiceId: "21m00Tcm4TlvDq8ikWAM",
            },
          },
        },
      },
    }
    ```

    Valeurs par défaut :

    - Modèle : `elevenlabs/tts`
    - Id de voix : `21m00Tcm4TlvDq8ikWAM`

    Le plugin bundled expose actuellement une voix par défaut connue pour bien fonctionner et renvoie des fichiers audio MP3.

  </Accordion>
</AccordionGroup>

## Lié à ce sujet

<CardGroup cols={2}>
  <Card title="Répertoire des fournisseurs" href="/fr/providers/index" icon="list">
    Parcourir tous les fournisseurs disponibles.
  </Card>
  <Card title="Génération d’images" href="/fr/tools/image-generation" icon="image">
    Paramètres d’outil d’image partagés et sélection du fournisseur.
  </Card>
  <Card title="Génération vidéo" href="/fr/tools/video-generation" icon="video">
    Paramètres d’outil vidéo partagés et sélection du fournisseur.
  </Card>
  <Card title="Référence de configuration" href="/fr/gateway/configuration-reference#agent-defaults" icon="gear">
    Valeurs par défaut de l’agent et configuration des modèles.
  </Card>
</CardGroup>
