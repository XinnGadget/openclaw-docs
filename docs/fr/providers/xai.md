---
read_when:
    - Vous souhaitez utiliser les modèles Grok dans OpenClaw
    - Vous configurez l’authentification xAI ou les identifiants de modèle
summary: Utilisez les modèles xAI Grok dans OpenClaw
title: xAI
x-i18n:
    generated_at: "2026-04-12T23:33:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: 820fef290c67d9815e41a96909d567216f67ca0f01df1d325008fd04666ad255
    source_path: providers/xai.md
    workflow: 15
---

# xAI

OpenClaw inclut un Plugin fournisseur `xai` intégré pour les modèles Grok.

## Premiers pas

<Steps>
  <Step title="Créer une clé API">
    Créez une clé API dans la [console xAI](https://console.x.ai/).
  </Step>
  <Step title="Définir votre clé API">
    Définissez `XAI_API_KEY`, ou exécutez :

    ```bash
    openclaw onboard --auth-choice xai-api-key
    ```

  </Step>
  <Step title="Choisir un modèle">
    ```json5
    {
      agents: { defaults: { model: { primary: "xai/grok-4" } } },
    }
    ```
  </Step>
</Steps>

<Note>
OpenClaw utilise l’API xAI Responses comme transport xAI intégré. La même
clé `XAI_API_KEY` peut également alimenter `web_search` basé sur Grok, `x_search`
natif et `code_execution` distant.
Si vous stockez une clé xAI sous `plugins.entries.xai.config.webSearch.apiKey`,
le fournisseur de modèles xAI intégré réutilise également cette clé comme repli.
L’ajustement de `code_execution` se trouve sous `plugins.entries.xai.config.codeExecution`.
</Note>

## Catalogue de modèles intégré

OpenClaw inclut ces familles de modèles xAI prêtes à l’emploi :

| Family         | Model ids                                                                |
| -------------- | ------------------------------------------------------------------------ |
| Grok 3         | `grok-3`, `grok-3-fast`, `grok-3-mini`, `grok-3-mini-fast`               |
| Grok 4         | `grok-4`, `grok-4-0709`                                                  |
| Grok 4 Fast    | `grok-4-fast`, `grok-4-fast-non-reasoning`                               |
| Grok 4.1 Fast  | `grok-4-1-fast`, `grok-4-1-fast-non-reasoning`                           |
| Grok 4.20 Beta | `grok-4.20-beta-latest-reasoning`, `grok-4.20-beta-latest-non-reasoning` |
| Grok Code      | `grok-code-fast-1`                                                       |

Le Plugin résout aussi en transmission les nouveaux identifiants `grok-4*` et `grok-code-fast*` lorsqu’ils
suivent la même forme d’API.

<Tip>
`grok-4-fast`, `grok-4-1-fast` et les variantes `grok-4.20-beta-*` sont les
références Grok compatibles image actuelles dans le catalogue intégré.
</Tip>

### Correspondances du mode rapide

`/fast on` ou `agents.defaults.models["xai/<model>"].params.fastMode: true`
réécrit les requêtes xAI natives comme suit :

| Source model  | Cible du mode rapide |
| ------------- | -------------------- |
| `grok-3`      | `grok-3-fast`        |
| `grok-3-mini` | `grok-3-mini-fast`   |
| `grok-4`      | `grok-4-fast`        |
| `grok-4-0709` | `grok-4-fast`        |

### Alias de compatibilité hérités

Les alias hérités se normalisent toujours vers les identifiants canoniques intégrés :

| Legacy alias              | Canonical id                          |
| ------------------------- | ------------------------------------- |
| `grok-4-fast-reasoning`   | `grok-4-fast`                         |
| `grok-4-1-fast-reasoning` | `grok-4-1-fast`                       |
| `grok-4.20-reasoning`     | `grok-4.20-beta-latest-reasoning`     |
| `grok-4.20-non-reasoning` | `grok-4.20-beta-latest-non-reasoning` |

## Fonctionnalités

<AccordionGroup>
  <Accordion title="Recherche web">
    Le fournisseur de recherche web `grok` intégré utilise aussi `XAI_API_KEY` :

    ```bash
    openclaw config set tools.web.search.provider grok
    ```

  </Accordion>

  <Accordion title="Génération vidéo">
    Le Plugin `xai` intégré enregistre la génération vidéo via l’outil partagé
    `video_generate`.

    - Modèle vidéo par défaut : `xai/grok-imagine-video`
    - Modes : texte-vers-vidéo, image-vers-vidéo et flux distants d’édition/extension vidéo
    - Prend en charge `aspectRatio` et `resolution`

    <Warning>
    Les tampons vidéo locaux ne sont pas acceptés. Utilisez des URL distantes `http(s)` pour
    les entrées de référence vidéo et d’édition.
    </Warning>

    Pour utiliser xAI comme fournisseur vidéo par défaut :

    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "xai/grok-imagine-video",
          },
        },
      },
    }
    ```

    <Note>
    Consultez [Génération vidéo](/fr/tools/video-generation) pour les paramètres d’outil partagés,
    la sélection du fournisseur et le comportement de basculement.
    </Note>

  </Accordion>

  <Accordion title="Configuration de x_search">
    Le Plugin xAI intégré expose `x_search` comme outil OpenClaw pour rechercher
    du contenu sur X (anciennement Twitter) via Grok.

    Chemin de configuration : `plugins.entries.xai.config.xSearch`

    | Key                | Type    | Default            | Description                          |
    | ------------------ | ------- | ------------------ | ------------------------------------ |
    | `enabled`          | boolean | —                  | Activer ou désactiver x_search       |
    | `model`            | string  | `grok-4-1-fast`    | Modèle utilisé pour les requêtes x_search |
    | `inlineCitations`  | boolean | —                  | Inclure des citations en ligne dans les résultats |
    | `maxTurns`         | number  | —                  | Nombre maximal de tours              |
    | `timeoutSeconds`   | number  | —                  | Délai d’expiration de la requête en secondes |
    | `cacheTtlMinutes`  | number  | —                  | Durée de vie du cache en minutes     |

    ```json5
    {
      plugins: {
        entries: {
          xai: {
            config: {
              xSearch: {
                enabled: true,
                model: "grok-4-1-fast",
                inlineCitations: true,
              },
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Configuration de code_execution">
    Le Plugin xAI intégré expose `code_execution` comme outil OpenClaw pour
    l’exécution de code distante dans l’environnement sandbox de xAI.

    Chemin de configuration : `plugins.entries.xai.config.codeExecution`

    | Key               | Type    | Default            | Description                              |
    | ----------------- | ------- | ------------------ | ---------------------------------------- |
    | `enabled`         | boolean | `true` (si une clé est disponible) | Activer ou désactiver l’exécution de code |
    | `model`           | string  | `grok-4-1-fast`    | Modèle utilisé pour les requêtes d’exécution de code |
    | `maxTurns`        | number  | —                  | Nombre maximal de tours                  |
    | `timeoutSeconds`  | number  | —                  | Délai d’expiration de la requête en secondes |

    <Note>
    Il s’agit d’une exécution sandbox xAI distante, et non de [`exec`](/fr/tools/exec) en local.
    </Note>

    ```json5
    {
      plugins: {
        entries: {
          xai: {
            config: {
              codeExecution: {
                enabled: true,
                model: "grok-4-1-fast",
              },
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Limites connues">
    - L’authentification est uniquement par clé API pour le moment. Il n’existe pas encore de flux OAuth ou device-code xAI dans
      OpenClaw.
    - `grok-4.20-multi-agent-experimental-beta-0304` n’est pas pris en charge sur le
      chemin normal du fournisseur xAI car il nécessite une surface d’API amont
      différente du transport xAI OpenClaw standard.
  </Accordion>

  <Accordion title="Notes avancées">
    - OpenClaw applique automatiquement des correctifs de compatibilité spécifiques à xAI pour les schémas d’outils et les appels d’outils
      sur le chemin d’exécution partagé.
    - Les requêtes xAI natives utilisent par défaut `tool_stream: true`. Définissez
      `agents.defaults.models["xai/<model>"].params.tool_stream` sur `false` pour
      le désactiver.
    - L’enveloppe xAI intégrée supprime les drapeaux stricts de schéma d’outil non pris en charge et
      les clés de payload de raisonnement avant l’envoi des requêtes xAI natives.
    - `web_search`, `x_search` et `code_execution` sont exposés comme outils OpenClaw. OpenClaw active le built-in xAI spécifique dont il a besoin dans chaque requête
      d’outil au lieu d’attacher tous les outils natifs à chaque tour de chat.
    - `x_search` et `code_execution` appartiennent au Plugin xAI intégré plutôt que d’être codés en dur dans l’exécution du modèle cœur.
    - `code_execution` est une exécution sandbox xAI distante, et non
      [`exec`](/fr/tools/exec) en local.
  </Accordion>
</AccordionGroup>

## Associé

<CardGroup cols={2}>
  <Card title="Sélection du modèle" href="/fr/concepts/model-providers" icon="layers">
    Choisir les fournisseurs, les références de modèle et le comportement de basculement.
  </Card>
  <Card title="Génération vidéo" href="/fr/tools/video-generation" icon="video">
    Paramètres partagés de l’outil vidéo et sélection du fournisseur.
  </Card>
  <Card title="Tous les fournisseurs" href="/fr/providers/index" icon="grid-2">
    Vue d’ensemble plus large des fournisseurs.
  </Card>
  <Card title="Dépannage" href="/fr/help/troubleshooting" icon="wrench">
    Problèmes courants et correctifs.
  </Card>
</CardGroup>
