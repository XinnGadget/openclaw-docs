---
read_when:
    - Vous souhaitez utiliser des modèles OpenAI dans OpenClaw
    - Vous souhaitez utiliser l’authentification par abonnement Codex plutôt que des clés d’API
    - Vous avez besoin d’un comportement d’exécution d’agent GPT-5 plus strict
summary: Utiliser OpenAI via des clés d’API ou un abonnement Codex dans OpenClaw
title: OpenAI
x-i18n:
    generated_at: "2026-04-12T23:31:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6aeb756618c5611fed56e4bf89015a2304ff2e21596104b470ec6e7cb459d1c9
    source_path: providers/openai.md
    workflow: 15
---

# OpenAI

OpenAI fournit des API développeur pour les modèles GPT. OpenClaw prend en charge deux modes d’authentification :

- **Clé d’API** — accès direct à OpenAI Platform avec facturation à l’usage (modèles `openai/*`)
- **Abonnement Codex** — connexion ChatGPT/Codex avec accès par abonnement (modèles `openai-codex/*`)

OpenAI prend explicitement en charge l’utilisation d’OAuth par abonnement dans des outils externes et des workflows comme OpenClaw.

## Prise en main

Choisissez votre méthode d’authentification préférée et suivez les étapes de configuration.

<Tabs>
  <Tab title="Clé d’API (OpenAI Platform)">
    **Idéal pour :** l’accès direct à l’API et la facturation à l’usage.

    <Steps>
      <Step title="Obtenir votre clé d’API">
        Créez ou copiez une clé d’API depuis le [tableau de bord OpenAI Platform](https://platform.openai.com/api-keys).
      </Step>
      <Step title="Exécuter l’onboarding">
        ```bash
        openclaw onboard --auth-choice openai-api-key
        ```

        Ou transmettez la clé directement :

        ```bash
        openclaw onboard --openai-api-key "$OPENAI_API_KEY"
        ```
      </Step>
      <Step title="Vérifier que le modèle est disponible">
        ```bash
        openclaw models list --provider openai
        ```
      </Step>
    </Steps>

    ### Résumé des routes

    | Model ref | Route | Auth |
    |-----------|-------|------|
    | `openai/gpt-5.4` | API OpenAI Platform directe | `OPENAI_API_KEY` |
    | `openai/gpt-5.4-pro` | API OpenAI Platform directe | `OPENAI_API_KEY` |

    <Note>
    La connexion ChatGPT/Codex passe par `openai-codex/*`, et non par `openai/*`.
    </Note>

    ### Exemple de configuration

    ```json5
    {
      env: { OPENAI_API_KEY: "sk-..." },
      agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
    }
    ```

    <Warning>
    OpenClaw n’expose **pas** `openai/gpt-5.3-codex-spark` sur la route API directe. Les requêtes live à l’API OpenAI rejettent ce modèle. Spark est réservé à Codex.
    </Warning>

  </Tab>

  <Tab title="Abonnement Codex">
    **Idéal pour :** utiliser votre abonnement ChatGPT/Codex au lieu d’une clé d’API distincte. Codex cloud nécessite une connexion ChatGPT.

    <Steps>
      <Step title="Exécuter l’OAuth Codex">
        ```bash
        openclaw onboard --auth-choice openai-codex
        ```

        Ou exécutez OAuth directement :

        ```bash
        openclaw models auth login --provider openai-codex
        ```
      </Step>
      <Step title="Définir le modèle par défaut">
        ```bash
        openclaw config set agents.defaults.model.primary openai-codex/gpt-5.4
        ```
      </Step>
      <Step title="Vérifier que le modèle est disponible">
        ```bash
        openclaw models list --provider openai-codex
        ```
      </Step>
    </Steps>

    ### Résumé des routes

    | Model ref | Route | Auth |
    |-----------|-------|------|
    | `openai-codex/gpt-5.4` | OAuth ChatGPT/Codex | Connexion Codex |
    | `openai-codex/gpt-5.3-codex-spark` | OAuth ChatGPT/Codex | Connexion Codex (selon les droits) |

    <Note>
    Cette route est volontairement distincte de `openai/gpt-5.4`. Utilisez `openai/*` avec une clé d’API pour un accès direct à Platform, et `openai-codex/*` pour un accès via abonnement Codex.
    </Note>

    ### Exemple de configuration

    ```json5
    {
      agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
    }
    ```

    <Tip>
    Si l’onboarding réutilise une connexion Codex CLI existante, ces identifiants restent gérés par Codex CLI. À l’expiration, OpenClaw relit d’abord la source Codex externe et réécrit l’identifiant actualisé dans le stockage Codex.
    </Tip>

    ### Plafond de fenêtre de contexte

    OpenClaw traite les métadonnées du modèle et le plafond de contexte du runtime comme deux valeurs distinctes.

    Pour `openai-codex/gpt-5.4` :

    - `contextWindow` natif : `1050000`
    - Plafond `contextTokens` par défaut du runtime : `272000`

    Le plafond par défaut plus faible offre en pratique de meilleures caractéristiques de latence et de qualité. Remplacez-le avec `contextTokens` :

    ```json5
    {
      models: {
        providers: {
          "openai-codex": {
            models: [{ id: "gpt-5.4", contextTokens: 160000 }],
          },
        },
      },
    }
    ```

    <Note>
    Utilisez `contextWindow` pour déclarer les métadonnées natives du modèle. Utilisez `contextTokens` pour limiter le budget de contexte du runtime.
    </Note>

  </Tab>
</Tabs>

## Génération d’images

Le Plugin `openai` intégré enregistre la génération d’images via l’outil `image_generate`.

| Capability                | Value                              |
| ------------------------- | ---------------------------------- |
| Default model             | `openai/gpt-image-1`               |
| Max images per request    | 4                                  |
| Edit mode                 | Activé (jusqu’à 5 images de référence) |
| Size overrides            | Pris en charge                     |
| Aspect ratio / resolution | Non transmis à l’API OpenAI Images |

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: { primary: "openai/gpt-image-1" },
    },
  },
}
```

<Note>
Voir [Image Generation](/fr/tools/image-generation) pour les paramètres partagés de l’outil, la sélection du fournisseur et le comportement de basculement.
</Note>

## Génération vidéo

Le Plugin `openai` intégré enregistre la génération vidéo via l’outil `video_generate`.

| Capability       | Value                                                                             |
| ---------------- | --------------------------------------------------------------------------------- |
| Default model    | `openai/sora-2`                                                                   |
| Modes            | Texte-vers-vidéo, image-vers-vidéo, édition d’une seule vidéo                     |
| Reference inputs | 1 image ou 1 vidéo                                                                |
| Size overrides   | Pris en charge                                                                    |
| Other overrides  | `aspectRatio`, `resolution`, `audio`, `watermark` sont ignorés avec un avertissement de l’outil |

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: { primary: "openai/sora-2" },
    },
  },
}
```

<Note>
Voir [Video Generation](/fr/tools/video-generation) pour les paramètres partagés de l’outil, la sélection du fournisseur et le comportement de basculement.
</Note>

## Superposition de personnalité

OpenClaw ajoute une petite superposition de prompt spécifique à OpenAI pour les exécutions `openai/*` et `openai-codex/*`. Cette superposition garde l’assistant chaleureux, collaboratif, concis et un peu plus expressif sur le plan émotionnel sans remplacer le prompt système de base.

| Value                  | Effect                                      |
| ---------------------- | ------------------------------------------- |
| `"friendly"` (default) | Active la superposition spécifique à OpenAI |
| `"on"`                 | Alias de `"friendly"`                       |
| `"off"`                | Utilise uniquement le prompt OpenClaw de base |

<Tabs>
  <Tab title="Config">
    ```json5
    {
      plugins: {
        entries: {
          openai: { config: { personality: "friendly" } },
        },
      },
    }
    ```
  </Tab>
  <Tab title="CLI">
    ```bash
    openclaw config set plugins.entries.openai.config.personality off
    ```
  </Tab>
</Tabs>

<Tip>
Les valeurs sont insensibles à la casse à l’exécution, donc `"Off"` et `"off"` désactivent toutes deux la superposition.
</Tip>

## Voix et parole

<AccordionGroup>
  <Accordion title="Synthèse vocale (TTS)">
    Le Plugin `openai` intégré enregistre la synthèse vocale pour la surface `messages.tts`.

    | Setting | Config path | Default |
    |---------|------------|---------|
    | Model | `messages.tts.providers.openai.model` | `gpt-4o-mini-tts` |
    | Voice | `messages.tts.providers.openai.voice` | `coral` |
    | Speed | `messages.tts.providers.openai.speed` | (non défini) |
    | Instructions | `messages.tts.providers.openai.instructions` | (non défini, `gpt-4o-mini-tts` uniquement) |
    | Format | `messages.tts.providers.openai.responseFormat` | `opus` pour les notes vocales, `mp3` pour les fichiers |
    | API key | `messages.tts.providers.openai.apiKey` | Utilise `OPENAI_API_KEY` comme repli |
    | Base URL | `messages.tts.providers.openai.baseUrl` | `https://api.openai.com/v1` |

    Modèles disponibles : `gpt-4o-mini-tts`, `tts-1`, `tts-1-hd`. Voix disponibles : `alloy`, `ash`, `ballad`, `cedar`, `coral`, `echo`, `fable`, `juniper`, `marin`, `onyx`, `nova`, `sage`, `shimmer`, `verse`.

    ```json5
    {
      messages: {
        tts: {
          providers: {
            openai: { model: "gpt-4o-mini-tts", voice: "coral" },
          },
        },
      },
    }
    ```

    <Note>
    Définissez `OPENAI_TTS_BASE_URL` pour remplacer l’URL de base TTS sans affecter le point de terminaison de l’API de chat.
    </Note>

  </Accordion>

  <Accordion title="Transcription temps réel">
    Le Plugin `openai` intégré enregistre la transcription temps réel pour le Plugin Voice Call.

    | Setting | Config path | Default |
    |---------|------------|---------|
    | Model | `plugins.entries.voice-call.config.streaming.providers.openai.model` | `gpt-4o-transcribe` |
    | Silence duration | `...openai.silenceDurationMs` | `800` |
    | VAD threshold | `...openai.vadThreshold` | `0.5` |
    | API key | `...openai.apiKey` | Utilise `OPENAI_API_KEY` comme repli |

    <Note>
    Utilise une connexion WebSocket vers `wss://api.openai.com/v1/realtime` avec de l’audio G.711 u-law.
    </Note>

  </Accordion>

  <Accordion title="Voix temps réel">
    Le Plugin `openai` intégré enregistre la voix temps réel pour le Plugin Voice Call.

    | Setting | Config path | Default |
    |---------|------------|---------|
    | Model | `plugins.entries.voice-call.config.realtime.providers.openai.model` | `gpt-realtime` |
    | Voice | `...openai.voice` | `alloy` |
    | Temperature | `...openai.temperature` | `0.8` |
    | VAD threshold | `...openai.vadThreshold` | `0.5` |
    | Silence duration | `...openai.silenceDurationMs` | `500` |
    | API key | `...openai.apiKey` | Utilise `OPENAI_API_KEY` comme repli |

    <Note>
    Prend en charge Azure OpenAI via les clés de configuration `azureEndpoint` et `azureDeployment`. Prend en charge l’appel d’outils bidirectionnel. Utilise le format audio G.711 u-law.
    </Note>

  </Accordion>
</AccordionGroup>

## Configuration avancée

<AccordionGroup>
  <Accordion title="Transport (WebSocket vs SSE)">
    OpenClaw utilise WebSocket en premier avec repli SSE (`"auto"`) pour `openai/*` et `openai-codex/*`.

    En mode `"auto"`, OpenClaw :
    - réessaie une fois en cas d’échec précoce de WebSocket avant de basculer vers SSE
    - après un échec, marque WebSocket comme dégradé pendant ~60 secondes et utilise SSE durant la période de refroidissement
    - attache des en-têtes stables d’identité de session et de tour pour les nouvelles tentatives et les reconnexions
    - normalise les compteurs d’usage (`input_tokens` / `prompt_tokens`) selon les variantes de transport

    | Value | Behavior |
    |-------|----------|
    | `"auto"` (default) | WebSocket d’abord, repli SSE |
    | `"sse"` | Force SSE uniquement |
    | `"websocket"` | Force WebSocket uniquement |

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "openai-codex/gpt-5.4": {
              params: { transport: "auto" },
            },
          },
        },
      },
    }
    ```

    Documentation OpenAI connexe :
    - [Realtime API with WebSocket](https://platform.openai.com/docs/guides/realtime-websocket)
    - [Streaming API responses (SSE)](https://platform.openai.com/docs/guides/streaming-responses)

  </Accordion>

  <Accordion title="Pré-chauffage WebSocket">
    OpenClaw active par défaut le pré-chauffage WebSocket pour `openai/*` afin de réduire la latence du premier tour.

    ```json5
    // Désactiver le pré-chauffage
    {
      agents: {
        defaults: {
          models: {
            "openai/gpt-5.4": {
              params: { openaiWsWarmup: false },
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Mode rapide">
    OpenClaw expose un commutateur partagé de mode rapide pour `openai/*` et `openai-codex/*` :

    - **Chat/UI :** `/fast status|on|off`
    - **Config :** `agents.defaults.models["<provider>/<model>"].params.fastMode`

    Lorsqu’il est activé, OpenClaw mappe le mode rapide sur le traitement prioritaire OpenAI (`service_tier = "priority"`). Les valeurs `service_tier` existantes sont conservées, et le mode rapide ne réécrit ni `reasoning` ni `text.verbosity`.

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "openai/gpt-5.4": { params: { fastMode: true } },
            "openai-codex/gpt-5.4": { params: { fastMode: true } },
          },
        },
      },
    }
    ```

    <Note>
    Les surcharges de session ont priorité sur la configuration. Effacer la surcharge de session dans l’interface Sessions rétablit la valeur par défaut configurée pour la session.
    </Note>

  </Accordion>

  <Accordion title="Traitement prioritaire (`service_tier`)">
    L’API d’OpenAI expose le traitement prioritaire via `service_tier`. Définissez-le par modèle dans OpenClaw :

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "openai/gpt-5.4": { params: { serviceTier: "priority" } },
            "openai-codex/gpt-5.4": { params: { serviceTier: "priority" } },
          },
        },
      },
    }
    ```

    Valeurs prises en charge : `auto`, `default`, `flex`, `priority`.

    <Warning>
    `serviceTier` n’est transmis qu’aux points de terminaison OpenAI natifs (`api.openai.com`) et aux points de terminaison Codex natifs (`chatgpt.com/backend-api`). Si vous faites passer l’un ou l’autre fournisseur par un proxy, OpenClaw laisse `service_tier` inchangé.
    </Warning>

  </Accordion>

  <Accordion title="Compaction côté serveur (API Responses)">
    Pour les modèles Responses OpenAI directs (`openai/*` sur `api.openai.com`), OpenClaw active automatiquement Compaction côté serveur :

    - Force `store: true` (sauf si la compatibilité du modèle définit `supportsStore: false`)
    - Injecte `context_management: [{ type: "compaction", compact_threshold: ... }]`
    - `compact_threshold` par défaut : 70 % de `contextWindow` (ou `80000` lorsqu’il n’est pas disponible)

    <Tabs>
      <Tab title="Activer explicitement">
        Utile pour les points de terminaison compatibles comme Azure OpenAI Responses :

        ```json5
        {
          agents: {
            defaults: {
              models: {
                "azure-openai-responses/gpt-5.4": {
                  params: { responsesServerCompaction: true },
                },
              },
            },
          },
        }
        ```
      </Tab>
      <Tab title="Seuil personnalisé">
        ```json5
        {
          agents: {
            defaults: {
              models: {
                "openai/gpt-5.4": {
                  params: {
                    responsesServerCompaction: true,
                    responsesCompactThreshold: 120000,
                  },
                },
              },
            },
          },
        }
        ```
      </Tab>
      <Tab title="Désactiver">
        ```json5
        {
          agents: {
            defaults: {
              models: {
                "openai/gpt-5.4": {
                  params: { responsesServerCompaction: false },
                },
              },
            },
          },
        }
        ```
      </Tab>
    </Tabs>

    <Note>
    `responsesServerCompaction` ne contrôle que l’injection de `context_management`. Les modèles Responses OpenAI directs forcent toujours `store: true` sauf si la compatibilité définit `supportsStore: false`.
    </Note>

  </Accordion>

  <Accordion title="Mode GPT agentique strict">
    Pour les exécutions de la famille GPT-5 sur `openai/*` et `openai-codex/*`, OpenClaw peut utiliser un contrat d’exécution embarqué plus strict :

    ```json5
    {
      agents: {
        defaults: {
          embeddedPi: { executionContract: "strict-agentic" },
        },
      },
    }
    ```

    Avec `strict-agentic`, OpenClaw :
    - ne considère plus un tour uniquement axé sur un plan comme une progression réussie lorsqu’une action d’outil est disponible
    - réessaie le tour avec une instruction orientée vers une action immédiate
    - active automatiquement `update_plan` pour les travaux substantiels
    - affiche un état bloqué explicite si le modèle continue à planifier sans agir

    <Note>
    Limité uniquement aux exécutions GPT-5 de type OpenAI et Codex. Les autres fournisseurs et les familles de modèles plus anciennes conservent le comportement par défaut.
    </Note>

  </Accordion>

  <Accordion title="Routes natives vs routes compatibles OpenAI">
    OpenClaw traite différemment les points de terminaison directs OpenAI, Codex et Azure OpenAI par rapport aux proxys génériques `/v1` compatibles OpenAI :

    **Routes natives** (`openai/*`, `openai-codex/*`, Azure OpenAI) :
    - conservent `reasoning: { effort: "none" }` intact lorsque le raisonnement est explicitement désactivé
    - utilisent par défaut des schémas d’outils en mode strict
    - joignent des en-têtes d’attribution cachés uniquement sur des hôtes natifs vérifiés
    - conservent la mise en forme des requêtes propre à OpenAI (`service_tier`, `store`, compatibilité du raisonnement, indices de cache de prompt)

    **Routes proxy/compatibles :**
    - utilisent un comportement de compatibilité plus souple
    - ne forcent pas les schémas d’outils stricts ni les en-têtes réservés aux routes natives

    Azure OpenAI utilise le transport natif et le comportement de compatibilité natif, mais ne reçoit pas les en-têtes d’attribution cachés.

  </Accordion>
</AccordionGroup>

## Connexe

<CardGroup cols={2}>
  <Card title="Model selection" href="/fr/concepts/model-providers" icon="layers">
    Choisir les fournisseurs, les références de modèles et le comportement de basculement.
  </Card>
  <Card title="Image generation" href="/fr/tools/image-generation" icon="image">
    Paramètres partagés de l’outil d’image et sélection du fournisseur.
  </Card>
  <Card title="Video generation" href="/fr/tools/video-generation" icon="video">
    Paramètres partagés de l’outil vidéo et sélection du fournisseur.
  </Card>
  <Card title="OAuth and auth" href="/fr/gateway/authentication" icon="key">
    Détails d’authentification et règles de réutilisation des identifiants.
  </Card>
</CardGroup>
