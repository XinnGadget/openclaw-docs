---
read_when:
    - Vous souhaitez utiliser la reconnaissance vocale Deepgram pour les pièces jointes audio
    - Vous avez besoin d’un exemple rapide de configuration Deepgram
summary: Transcription Deepgram pour les notes vocales entrantes
title: Deepgram
x-i18n:
    generated_at: "2026-04-12T23:30:18Z"
    model: gpt-5.4
    provider: openai
    source_hash: 091523d6669e3d258f07c035ec756bd587299b6c7025520659232b1b2c1e21a5
    source_path: providers/deepgram.md
    workflow: 15
---

# Deepgram (Transcription audio)

Deepgram est une API de reconnaissance vocale. Dans OpenClaw, elle est utilisée pour la **transcription
des fichiers audio/notes vocales entrants** via `tools.media.audio`.

Lorsqu’elle est activée, OpenClaw envoie le fichier audio à Deepgram et injecte la transcription
dans le pipeline de réponse (`{{Transcript}}` + bloc `[Audio]`). Ce n’est **pas du streaming** ;
cela utilise le point de terminaison de transcription préenregistrée.

| Detail        | Value                                                      |
| ------------- | ---------------------------------------------------------- |
| Site web      | [deepgram.com](https://deepgram.com)                       |
| Documentation | [developers.deepgram.com](https://developers.deepgram.com) |
| Auth          | `DEEPGRAM_API_KEY`                                         |
| Modèle par défaut | `nova-3`                                               |

## Premiers pas

<Steps>
  <Step title="Définir votre clé API">
    Ajoutez votre clé API Deepgram à l’environnement :

    ```
    DEEPGRAM_API_KEY=dg_...
    ```

  </Step>
  <Step title="Activer le fournisseur audio">
    ```json5
    {
      tools: {
        media: {
          audio: {
            enabled: true,
            models: [{ provider: "deepgram", model: "nova-3" }],
          },
        },
      },
    }
    ```
  </Step>
  <Step title="Envoyer une note vocale">
    Envoyez un message audio via n’importe quel canal connecté. OpenClaw le transcrit
    via Deepgram et injecte la transcription dans le pipeline de réponse.
  </Step>
</Steps>

## Options de configuration

| Option            | Path                                                         | Description                            |
| ----------------- | ------------------------------------------------------------ | -------------------------------------- |
| `model`           | `tools.media.audio.models[].model`                           | Identifiant de modèle Deepgram (par défaut : `nova-3`) |
| `language`        | `tools.media.audio.models[].language`                        | Indication de langue (facultatif)      |
| `detect_language` | `tools.media.audio.providerOptions.deepgram.detect_language` | Activer la détection de langue (facultatif) |
| `punctuate`       | `tools.media.audio.providerOptions.deepgram.punctuate`       | Activer la ponctuation (facultatif)    |
| `smart_format`    | `tools.media.audio.providerOptions.deepgram.smart_format`    | Activer le formatage intelligent (facultatif) |

<Tabs>
  <Tab title="Avec indication de langue">
    ```json5
    {
      tools: {
        media: {
          audio: {
            enabled: true,
            models: [{ provider: "deepgram", model: "nova-3", language: "en" }],
          },
        },
      },
    }
    ```
  </Tab>
  <Tab title="Avec options Deepgram">
    ```json5
    {
      tools: {
        media: {
          audio: {
            enabled: true,
            providerOptions: {
              deepgram: {
                detect_language: true,
                punctuate: true,
                smart_format: true,
              },
            },
            models: [{ provider: "deepgram", model: "nova-3" }],
          },
        },
      },
    }
    ```
  </Tab>
</Tabs>

## Notes

<AccordionGroup>
  <Accordion title="Authentification">
    L’authentification suit l’ordre standard d’authentification du fournisseur. `DEEPGRAM_API_KEY` est
    le chemin le plus simple.
  </Accordion>
  <Accordion title="Proxy et points de terminaison personnalisés">
    Remplacez les points de terminaison ou les en-têtes avec `tools.media.audio.baseUrl` et
    `tools.media.audio.headers` lors de l’utilisation d’un proxy.
  </Accordion>
  <Accordion title="Comportement de sortie">
    La sortie suit les mêmes règles audio que les autres fournisseurs (limites de taille, délais d’expiration,
    injection de transcription).
  </Accordion>
</AccordionGroup>

<Note>
La transcription Deepgram est **préenregistrée uniquement** (pas de streaming en temps réel). OpenClaw
envoie le fichier audio complet et attend la transcription complète avant de l’injecter
dans la conversation.
</Note>

## Associé

<CardGroup cols={2}>
  <Card title="Outils média" href="/tools/media" icon="photo-film">
    Vue d’ensemble du pipeline de traitement audio, image et vidéo.
  </Card>
  <Card title="Configuration" href="/fr/gateway/configuration" icon="gear">
    Référence de configuration complète, y compris les paramètres des outils média.
  </Card>
  <Card title="Dépannage" href="/fr/help/troubleshooting" icon="wrench">
    Problèmes courants et étapes de débogage.
  </Card>
  <Card title="FAQ" href="/fr/help/faq" icon="circle-question">
    Questions fréquentes sur la configuration d’OpenClaw.
  </Card>
</CardGroup>
