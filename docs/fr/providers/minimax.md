---
read_when:
    - Vous souhaitez utiliser les modèles MiniMax dans OpenClaw
    - Vous avez besoin d’un guide de configuration MiniMax
summary: Utilisez des modèles MiniMax dans OpenClaw
title: MiniMax
x-i18n:
    generated_at: "2026-04-12T23:31:36Z"
    model: gpt-5.4
    provider: openai
    source_hash: ee9c89faf57384feb66cda30934000e5746996f24b59122db309318f42c22389
    source_path: providers/minimax.md
    workflow: 15
---

# MiniMax

Le fournisseur MiniMax d’OpenClaw utilise par défaut **MiniMax M2.7**.

MiniMax fournit également :

- Une synthèse vocale intégrée via T2A v2
- Une compréhension d’image intégrée via `MiniMax-VL-01`
- Une génération musicale intégrée via `music-2.5+`
- Un `web_search` intégré via l’API de recherche MiniMax Coding Plan

Répartition des fournisseurs :

| Provider ID      | Auth    | Capabilities                                                    |
| ---------------- | ------- | --------------------------------------------------------------- |
| `minimax`        | Clé API | Texte, génération d’images, compréhension d’images, voix, recherche web |
| `minimax-portal` | OAuth   | Texte, génération d’images, compréhension d’images             |

## Gamme de modèles

| Model                    | Type             | Description                              |
| ------------------------ | ---------------- | ---------------------------------------- |
| `MiniMax-M2.7`           | Chat (raisonnement) | Modèle de raisonnement hébergé par défaut |
| `MiniMax-M2.7-highspeed` | Chat (raisonnement) | Niveau de raisonnement M2.7 plus rapide  |
| `MiniMax-VL-01`          | Vision           | Modèle de compréhension d’image          |
| `image-01`               | Génération d’images | Texte-vers-image et édition image-vers-image |
| `music-2.5+`             | Génération musicale | Modèle musical par défaut               |
| `music-2.5`              | Génération musicale | Niveau précédent de génération musicale |
| `music-2.0`              | Génération musicale | Niveau historique de génération musicale |
| `MiniMax-Hailuo-2.3`     | Génération vidéo | Texte-vers-vidéo et flux de référence d’image |

## Premiers pas

Choisissez votre méthode d’authentification préférée et suivez les étapes de configuration.

<Tabs>
  <Tab title="OAuth (Coding Plan)">
    **Idéal pour :** configuration rapide avec MiniMax Coding Plan via OAuth, sans clé API.

    <Tabs>
      <Tab title="International">
        <Steps>
          <Step title="Exécuter l’onboarding">
            ```bash
            openclaw onboard --auth-choice minimax-global-oauth
            ```

            Cela authentifie contre `api.minimax.io`.
          </Step>
          <Step title="Vérifier que le modèle est disponible">
            ```bash
            openclaw models list --provider minimax-portal
            ```
          </Step>
        </Steps>
      </Tab>
      <Tab title="Chine">
        <Steps>
          <Step title="Exécuter l’onboarding">
            ```bash
            openclaw onboard --auth-choice minimax-cn-oauth
            ```

            Cela authentifie contre `api.minimaxi.com`.
          </Step>
          <Step title="Vérifier que le modèle est disponible">
            ```bash
            openclaw models list --provider minimax-portal
            ```
          </Step>
        </Steps>
      </Tab>
    </Tabs>

    <Note>
    Les configurations OAuth utilisent l’identifiant de fournisseur `minimax-portal`. Les références de modèle suivent la forme `minimax-portal/MiniMax-M2.7`.
    </Note>

    <Tip>
    Lien de parrainage pour MiniMax Coding Plan (10 % de réduction) : [MiniMax Coding Plan](https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link)
    </Tip>

  </Tab>

  <Tab title="Clé API">
    **Idéal pour :** MiniMax hébergé avec API compatible Anthropic.

    <Tabs>
      <Tab title="International">
        <Steps>
          <Step title="Exécuter l’onboarding">
            ```bash
            openclaw onboard --auth-choice minimax-global-api
            ```

            Cela configure `api.minimax.io` comme URL de base.
          </Step>
          <Step title="Vérifier que le modèle est disponible">
            ```bash
            openclaw models list --provider minimax
            ```
          </Step>
        </Steps>
      </Tab>
      <Tab title="Chine">
        <Steps>
          <Step title="Exécuter l’onboarding">
            ```bash
            openclaw onboard --auth-choice minimax-cn-api
            ```

            Cela configure `api.minimaxi.com` comme URL de base.
          </Step>
          <Step title="Vérifier que le modèle est disponible">
            ```bash
            openclaw models list --provider minimax
            ```
          </Step>
        </Steps>
      </Tab>
    </Tabs>

    ### Exemple de configuration

    ```json5
    {
      env: { MINIMAX_API_KEY: "sk-..." },
      agents: { defaults: { model: { primary: "minimax/MiniMax-M2.7" } } },
      models: {
        mode: "merge",
        providers: {
          minimax: {
            baseUrl: "https://api.minimax.io/anthropic",
            apiKey: "${MINIMAX_API_KEY}",
            api: "anthropic-messages",
            models: [
              {
                id: "MiniMax-M2.7",
                name: "MiniMax M2.7",
                reasoning: true,
                input: ["text", "image"],
                cost: { input: 0.3, output: 1.2, cacheRead: 0.06, cacheWrite: 0.375 },
                contextWindow: 204800,
                maxTokens: 131072,
              },
              {
                id: "MiniMax-M2.7-highspeed",
                name: "MiniMax M2.7 Highspeed",
                reasoning: true,
                input: ["text", "image"],
                cost: { input: 0.6, output: 2.4, cacheRead: 0.06, cacheWrite: 0.375 },
                contextWindow: 204800,
                maxTokens: 131072,
              },
            ],
          },
        },
      },
    }
    ```

    <Warning>
    Sur le chemin de streaming compatible Anthropic, OpenClaw désactive par défaut le thinking MiniMax sauf si vous définissez explicitement `thinking` vous-même. Le point de terminaison de streaming MiniMax émet `reasoning_content` dans des morceaux delta au style OpenAI au lieu des blocs de thinking Anthropic natifs, ce qui peut faire fuiter le raisonnement interne dans la sortie visible s’il reste activé implicitement.
    </Warning>

    <Note>
    Les configurations par clé API utilisent l’identifiant de fournisseur `minimax`. Les références de modèle suivent la forme `minimax/MiniMax-M2.7`.
    </Note>

  </Tab>
</Tabs>

## Configurer via `openclaw configure`

Utilisez l’assistant de configuration interactif pour définir MiniMax sans modifier le JSON :

<Steps>
  <Step title="Lancer l’assistant">
    ```bash
    openclaw configure
    ```
  </Step>
  <Step title="Sélectionner Model/auth">
    Choisissez **Model/auth** dans le menu.
  </Step>
  <Step title="Choisir une option d’authentification MiniMax">
    Sélectionnez l’une des options MiniMax disponibles :

    | Auth choice | Description |
    | --- | --- |
    | `minimax-global-oauth` | OAuth international (Coding Plan) |
    | `minimax-cn-oauth` | OAuth Chine (Coding Plan) |
    | `minimax-global-api` | Clé API internationale |
    | `minimax-cn-api` | Clé API Chine |

  </Step>
  <Step title="Choisir votre modèle par défaut">
    Sélectionnez votre modèle par défaut lorsqu’il est demandé.
  </Step>
</Steps>

## Capacités

### Génération d’images

Le Plugin MiniMax enregistre le modèle `image-01` pour l’outil `image_generate`. Il prend en charge :

- **Génération texte-vers-image** avec contrôle du ratio d’aspect
- **Édition image-vers-image** (référence de sujet) avec contrôle du ratio d’aspect
- Jusqu’à **9 images de sortie** par requête
- Jusqu’à **1 image de référence** par requête d’édition
- Ratios d’aspect pris en charge : `1:1`, `16:9`, `4:3`, `3:2`, `2:3`, `3:4`, `9:16`, `21:9`

Pour utiliser MiniMax pour la génération d’images, définissez-le comme fournisseur de génération d’images :

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: { primary: "minimax/image-01" },
    },
  },
}
```

Le Plugin utilise la même authentification `MINIMAX_API_KEY` ou OAuth que les modèles texte. Aucune configuration supplémentaire n’est nécessaire si MiniMax est déjà configuré.

`minimax` et `minimax-portal` enregistrent tous deux `image_generate` avec le même
modèle `image-01`. Les configurations par clé API utilisent `MINIMAX_API_KEY` ; les configurations OAuth peuvent utiliser
à la place le chemin d’authentification intégré `minimax-portal`.

Lorsque l’onboarding ou la configuration par clé API écrit des entrées explicites `models.providers.minimax`,
OpenClaw matérialise `MiniMax-M2.7` et
`MiniMax-M2.7-highspeed` avec `input: ["text", "image"]`.

Le catalogue texte MiniMax intégré lui-même reste une métadonnée texte uniquement jusqu’à
ce que cette configuration explicite du fournisseur existe. La compréhension d’image est exposée séparément
via le fournisseur média `MiniMax-VL-01` appartenant au Plugin.

<Note>
Consultez [Génération d’images](/fr/tools/image-generation) pour les paramètres d’outil partagés, la sélection du fournisseur et le comportement de basculement.
</Note>

### Génération musicale

Le Plugin `minimax` intégré enregistre également la génération musicale via l’outil partagé
`music_generate`.

- Modèle musical par défaut : `minimax/music-2.5+`
- Prend aussi en charge `minimax/music-2.5` et `minimax/music-2.0`
- Contrôles d’invite : `lyrics`, `instrumental`, `durationSeconds`
- Format de sortie : `mp3`
- Les exécutions adossées à une session sont détachées via le flux partagé de tâche/statut, y compris `action: "status"`

Pour utiliser MiniMax comme fournisseur musical par défaut :

```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "minimax/music-2.5+",
      },
    },
  },
}
```

<Note>
Consultez [Génération musicale](/fr/tools/music-generation) pour les paramètres d’outil partagés, la sélection du fournisseur et le comportement de basculement.
</Note>

### Génération vidéo

Le Plugin `minimax` intégré enregistre également la génération vidéo via l’outil partagé
`video_generate`.

- Modèle vidéo par défaut : `minimax/MiniMax-Hailuo-2.3`
- Modes : texte-vers-vidéo et flux de référence à image unique
- Prend en charge `aspectRatio` et `resolution`

Pour utiliser MiniMax comme fournisseur vidéo par défaut :

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "minimax/MiniMax-Hailuo-2.3",
      },
    },
  },
}
```

<Note>
Consultez [Génération vidéo](/fr/tools/video-generation) pour les paramètres d’outil partagés, la sélection du fournisseur et le comportement de basculement.
</Note>

### Compréhension d’image

Le Plugin MiniMax enregistre la compréhension d’image séparément du
catalogue texte :

| Provider ID      | Modèle d’image par défaut |
| ---------------- | ------------------------- |
| `minimax`        | `MiniMax-VL-01`           |
| `minimax-portal` | `MiniMax-VL-01`           |

C’est pourquoi le routage média automatique peut utiliser la compréhension d’image MiniMax même
lorsque le catalogue intégré du fournisseur texte affiche encore des références de chat M2.7 texte uniquement.

### Recherche web

Le Plugin MiniMax enregistre également `web_search` via l’API de recherche
MiniMax Coding Plan.

- Identifiant du fournisseur : `minimax`
- Résultats structurés : titres, URL, extraits, requêtes associées
- Variable d’environnement privilégiée : `MINIMAX_CODE_PLAN_KEY`
- Alias d’environnement accepté : `MINIMAX_CODING_API_KEY`
- Repli de compatibilité : `MINIMAX_API_KEY` lorsqu’il pointe déjà vers un jeton coding-plan
- Réutilisation de région : `plugins.entries.minimax.config.webSearch.region`, puis `MINIMAX_API_HOST`, puis les URL de base du fournisseur MiniMax
- La recherche reste sur l’identifiant de fournisseur `minimax` ; la configuration OAuth CN/globale peut toujours orienter indirectement la région via `models.providers.minimax-portal.baseUrl`

La configuration se trouve sous `plugins.entries.minimax.config.webSearch.*`.

<Note>
Consultez [Recherche MiniMax](/fr/tools/minimax-search) pour la configuration complète et l’utilisation de la recherche web.
</Note>

## Configuration avancée

<AccordionGroup>
  <Accordion title="Options de configuration">
    | Option | Description |
    | --- | --- |
    | `models.providers.minimax.baseUrl` | Préférez `https://api.minimax.io/anthropic` (compatible Anthropic) ; `https://api.minimax.io/v1` est facultatif pour les payloads compatibles OpenAI |
    | `models.providers.minimax.api` | Préférez `anthropic-messages` ; `openai-completions` est facultatif pour les payloads compatibles OpenAI |
    | `models.providers.minimax.apiKey` | Clé API MiniMax (`MINIMAX_API_KEY`) |
    | `models.providers.minimax.models` | Définissez `id`, `name`, `reasoning`, `contextWindow`, `maxTokens`, `cost` |
    | `agents.defaults.models` | Alias des modèles que vous souhaitez dans l’allowlist |
    | `models.mode` | Conservez `merge` si vous souhaitez ajouter MiniMax aux côtés des modèles intégrés |
  </Accordion>

  <Accordion title="Valeurs par défaut de thinking">
    Sur `api: "anthropic-messages"`, OpenClaw injecte `thinking: { type: "disabled" }` sauf si thinking est déjà explicitement défini dans les paramètres/la configuration.

    Cela empêche le point de terminaison de streaming MiniMax d’émettre `reasoning_content` dans des morceaux delta au style OpenAI, ce qui ferait fuiter le raisonnement interne dans la sortie visible.

  </Accordion>

  <Accordion title="Mode rapide">
    `/fast on` ou `params.fastMode: true` réécrit `MiniMax-M2.7` en `MiniMax-M2.7-highspeed` sur le chemin de flux compatible Anthropic.
  </Accordion>

  <Accordion title="Exemple de repli">
    **Idéal pour :** conserver votre modèle de dernière génération le plus puissant comme principal, avec un repli vers MiniMax M2.7. L’exemple ci-dessous utilise Opus comme modèle principal concret ; remplacez-le par votre modèle principal de dernière génération préféré.

    ```json5
    {
      env: { MINIMAX_API_KEY: "sk-..." },
      agents: {
        defaults: {
          models: {
            "anthropic/claude-opus-4-6": { alias: "primary" },
            "minimax/MiniMax-M2.7": { alias: "minimax" },
          },
          model: {
            primary: "anthropic/claude-opus-4-6",
            fallbacks: ["minimax/MiniMax-M2.7"],
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Détails d’utilisation de Coding Plan">
    - API d’utilisation Coding Plan : `https://api.minimaxi.com/v1/api/openplatform/coding_plan/remains` (nécessite une clé coding plan).
    - OpenClaw normalise l’utilisation du coding plan MiniMax vers le même affichage en `% restant` que celui utilisé par les autres fournisseurs. Les champs bruts `usage_percent` / `usagePercent` de MiniMax représentent le quota restant, et non le quota consommé ; OpenClaw les inverse donc. Les champs basés sur le nombre sont prioritaires lorsqu’ils sont présents.
    - Lorsque l’API renvoie `model_remains`, OpenClaw privilégie l’entrée du modèle de chat, dérive l’étiquette de fenêtre à partir de `start_time` / `end_time` si nécessaire, et inclut le nom du modèle sélectionné dans l’étiquette du forfait afin que les fenêtres coding plan soient plus faciles à distinguer.
    - Les instantanés d’utilisation traitent `minimax`, `minimax-cn` et `minimax-portal` comme la même surface de quota MiniMax, et privilégient l’OAuth MiniMax stocké avant de revenir aux variables d’environnement de clé Coding Plan.
  </Accordion>
</AccordionGroup>

## Notes

- Les références de modèle suivent le chemin d’authentification :
  - Configuration par clé API : `minimax/<model>`
  - Configuration OAuth : `minimax-portal/<model>`
- Modèle de chat par défaut : `MiniMax-M2.7`
- Modèle de chat alternatif : `MiniMax-M2.7-highspeed`
- L’onboarding et la configuration directe par clé API écrivent des définitions de modèle explicites avec `input: ["text", "image"]` pour les deux variantes M2.7
- Le catalogue intégré du fournisseur expose actuellement les références de chat comme des métadonnées texte uniquement jusqu’à ce qu’une configuration explicite du fournisseur MiniMax existe
- Mettez à jour les valeurs de tarification dans `models.json` si vous avez besoin d’un suivi des coûts exact
- Utilisez `openclaw models list` pour confirmer l’identifiant actuel du fournisseur, puis changez avec `openclaw models set minimax/MiniMax-M2.7` ou `openclaw models set minimax-portal/MiniMax-M2.7`

<Tip>
Lien de parrainage pour MiniMax Coding Plan (10 % de réduction) : [MiniMax Coding Plan](https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link)
</Tip>

<Note>
Consultez [Fournisseurs de modèles](/fr/concepts/model-providers) pour les règles des fournisseurs.
</Note>

## Dépannage

<AccordionGroup>
  <Accordion title='"Modèle inconnu : minimax/MiniMax-M2.7"'>
    Cela signifie généralement que le **fournisseur MiniMax n’est pas configuré** (aucune entrée de fournisseur correspondante et aucun profil d’authentification MiniMax/clé d’environnement MiniMax trouvé). Un correctif pour cette détection est présent dans **2026.1.12**. Corrigez cela en :

    - mettant à niveau vers **2026.1.12** (ou en exécutant depuis la source `main`), puis en redémarrant la Gateway ;
    - exécutant `openclaw configure` et en sélectionnant une option d’authentification **MiniMax**, ou
    - ajoutant manuellement le bloc `models.providers.minimax` ou `models.providers.minimax-portal` correspondant, ou
    - définissant `MINIMAX_API_KEY`, `MINIMAX_OAUTH_TOKEN` ou un profil d’authentification MiniMax afin que le fournisseur correspondant puisse être injecté.

    Assurez-vous que l’identifiant du modèle est **sensible à la casse** :

    - Chemin par clé API : `minimax/MiniMax-M2.7` ou `minimax/MiniMax-M2.7-highspeed`
    - Chemin OAuth : `minimax-portal/MiniMax-M2.7` ou `minimax-portal/MiniMax-M2.7-highspeed`

    Puis revérifiez avec :

    ```bash
    openclaw models list
    ```

  </Accordion>
</AccordionGroup>

<Note>
Plus d’aide : [Dépannage](/fr/help/troubleshooting) et [FAQ](/fr/help/faq).
</Note>

## Associé

<CardGroup cols={2}>
  <Card title="Sélection du modèle" href="/fr/concepts/model-providers" icon="layers">
    Choisir les fournisseurs, les références de modèle et le comportement de basculement.
  </Card>
  <Card title="Génération d’images" href="/fr/tools/image-generation" icon="image">
    Paramètres partagés de l’outil image et sélection du fournisseur.
  </Card>
  <Card title="Génération musicale" href="/fr/tools/music-generation" icon="music">
    Paramètres partagés de l’outil musique et sélection du fournisseur.
  </Card>
  <Card title="Génération vidéo" href="/fr/tools/video-generation" icon="video">
    Paramètres partagés de l’outil vidéo et sélection du fournisseur.
  </Card>
  <Card title="Recherche MiniMax" href="/fr/tools/minimax-search" icon="magnifying-glass">
    Configuration de la recherche web via MiniMax Coding Plan.
  </Card>
  <Card title="Dépannage" href="/fr/help/troubleshooting" icon="wrench">
    Dépannage général et FAQ.
  </Card>
</CardGroup>
