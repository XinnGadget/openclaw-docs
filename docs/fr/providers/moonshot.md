---
read_when:
    - Vous voulez configurer Moonshot K2 (Moonshot Open Platform) par rapport à Kimi Coding
    - Vous devez comprendre les points de terminaison, les clés et les références de modèles distincts
    - Vous voulez une configuration prête à copier-coller pour l’un ou l’autre fournisseur
summary: Configurer Moonshot K2 vs Kimi Coding (fournisseurs séparés + clés distinctes)
title: Moonshot AI
x-i18n:
    generated_at: "2026-04-12T23:31:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3f261f83a9b37e4fffb0cd0803e0c64f27eae8bae91b91d8a781a030663076f8
    source_path: providers/moonshot.md
    workflow: 15
---

# Moonshot AI (Kimi)

Moonshot fournit l’API Kimi avec des points de terminaison compatibles OpenAI. Configurez le fournisseur et définissez le modèle par défaut sur `moonshot/kimi-k2.5`, ou utilisez Kimi Coding avec `kimi/kimi-code`.

<Warning>
Moonshot et Kimi Coding sont **des fournisseurs distincts**. Les clés ne sont pas interchangeables, les points de terminaison diffèrent, et les références de modèles diffèrent (`moonshot/...` vs `kimi/...`).
</Warning>

## Catalogue de modèles intégré

[//]: # "moonshot-kimi-k2-ids:start"

| Model ref                         | Nom                    | Raisonnement | Entrée      | Contexte | Sortie max |
| --------------------------------- | ---------------------- | ------------ | ----------- | -------- | ---------- |
| `moonshot/kimi-k2.5`              | Kimi K2.5              | Non          | text, image | 262,144  | 262,144    |
| `moonshot/kimi-k2-thinking`       | Kimi K2 Thinking       | Oui          | text        | 262,144  | 262,144    |
| `moonshot/kimi-k2-thinking-turbo` | Kimi K2 Thinking Turbo | Oui          | text        | 262,144  | 262,144    |
| `moonshot/kimi-k2-turbo`          | Kimi K2 Turbo          | Non          | text        | 256,000  | 16,384     |

[//]: # "moonshot-kimi-k2-ids:end"

## Démarrage

Choisissez votre fournisseur et suivez les étapes de configuration.

<Tabs>
  <Tab title="API Moonshot">
    **Idéal pour :** les modèles Kimi K2 via Moonshot Open Platform.

    <Steps>
      <Step title="Choisir votre région de point de terminaison">
        | Choix d’authentification | Point de terminaison         | Région        |
        | ------------------------ | ---------------------------- | ------------- |
        | `moonshot-api-key`       | `https://api.moonshot.ai/v1` | International |
        | `moonshot-api-key-cn`    | `https://api.moonshot.cn/v1` | Chine         |
      </Step>
      <Step title="Lancer l’onboarding">
        ```bash
        openclaw onboard --auth-choice moonshot-api-key
        ```

        Ou pour le point de terminaison Chine :

        ```bash
        openclaw onboard --auth-choice moonshot-api-key-cn
        ```
      </Step>
      <Step title="Définir un modèle par défaut">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "moonshot/kimi-k2.5" },
            },
          },
        }
        ```
      </Step>
      <Step title="Vérifier que les modèles sont disponibles">
        ```bash
        openclaw models list --provider moonshot
        ```
      </Step>
    </Steps>

    ### Exemple de configuration

    ```json5
    {
      env: { MOONSHOT_API_KEY: "sk-..." },
      agents: {
        defaults: {
          model: { primary: "moonshot/kimi-k2.5" },
          models: {
            // moonshot-kimi-k2-aliases:start
            "moonshot/kimi-k2.5": { alias: "Kimi K2.5" },
            "moonshot/kimi-k2-thinking": { alias: "Kimi K2 Thinking" },
            "moonshot/kimi-k2-thinking-turbo": { alias: "Kimi K2 Thinking Turbo" },
            "moonshot/kimi-k2-turbo": { alias: "Kimi K2 Turbo" },
            // moonshot-kimi-k2-aliases:end
          },
        },
      },
      models: {
        mode: "merge",
        providers: {
          moonshot: {
            baseUrl: "https://api.moonshot.ai/v1",
            apiKey: "${MOONSHOT_API_KEY}",
            api: "openai-completions",
            models: [
              // moonshot-kimi-k2-models:start
              {
                id: "kimi-k2.5",
                name: "Kimi K2.5",
                reasoning: false,
                input: ["text", "image"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 262144,
              },
              {
                id: "kimi-k2-thinking",
                name: "Kimi K2 Thinking",
                reasoning: true,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 262144,
              },
              {
                id: "kimi-k2-thinking-turbo",
                name: "Kimi K2 Thinking Turbo",
                reasoning: true,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 262144,
              },
              {
                id: "kimi-k2-turbo",
                name: "Kimi K2 Turbo",
                reasoning: false,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 256000,
                maxTokens: 16384,
              },
              // moonshot-kimi-k2-models:end
            ],
          },
        },
      },
    }
    ```

  </Tab>

  <Tab title="Kimi Coding">
    **Idéal pour :** les tâches orientées code via le point de terminaison Kimi Coding.

    <Note>
    Kimi Coding utilise une clé API différente et un préfixe de fournisseur différent (`kimi/...`) de Moonshot (`moonshot/...`). L’ancienne référence de modèle `kimi/k2p5` reste acceptée comme ID de compatibilité.
    </Note>

    <Steps>
      <Step title="Lancer l’onboarding">
        ```bash
        openclaw onboard --auth-choice kimi-code-api-key
        ```
      </Step>
      <Step title="Définir un modèle par défaut">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "kimi/kimi-code" },
            },
          },
        }
        ```
      </Step>
      <Step title="Vérifier que le modèle est disponible">
        ```bash
        openclaw models list --provider kimi
        ```
      </Step>
    </Steps>

    ### Exemple de configuration

    ```json5
    {
      env: { KIMI_API_KEY: "sk-..." },
      agents: {
        defaults: {
          model: { primary: "kimi/kimi-code" },
          models: {
            "kimi/kimi-code": { alias: "Kimi" },
          },
        },
      },
    }
    ```

  </Tab>
</Tabs>

## Recherche web Kimi

OpenClaw inclut également **Kimi** comme fournisseur `web_search`, adossé à la
recherche web Moonshot.

<Steps>
  <Step title="Lancer la configuration interactive de la recherche web">
    ```bash
    openclaw configure --section web
    ```

    Choisissez **Kimi** dans la section de recherche web pour stocker
    `plugins.entries.moonshot.config.webSearch.*`.

  </Step>
  <Step title="Configurer la région de recherche web et le modèle">
    La configuration interactive demande :

    | Paramètre           | Options                                                              |
    | ------------------- | -------------------------------------------------------------------- |
    | Région API          | `https://api.moonshot.ai/v1` (international) ou `https://api.moonshot.cn/v1` (Chine) |
    | Modèle de recherche web | Par défaut : `kimi-k2.5`                                        |

  </Step>
</Steps>

La configuration se trouve sous `plugins.entries.moonshot.config.webSearch` :

```json5
{
  plugins: {
    entries: {
      moonshot: {
        config: {
          webSearch: {
            apiKey: "sk-...", // or use KIMI_API_KEY / MOONSHOT_API_KEY
            baseUrl: "https://api.moonshot.ai/v1",
            model: "kimi-k2.5",
          },
        },
      },
    },
  },
  tools: {
    web: {
      search: {
        provider: "kimi",
      },
    },
  },
}
```

## Avancé

<AccordionGroup>
  <Accordion title="Mode de réflexion natif">
    Moonshot Kimi prend en charge un mode de réflexion natif binaire :

    - `thinking: { type: "enabled" }`
    - `thinking: { type: "disabled" }`

    Configurez-le par modèle via `agents.defaults.models.<provider/model>.params` :

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "moonshot/kimi-k2.5": {
              params: {
                thinking: { type: "disabled" },
              },
            },
          },
        },
      },
    }
    ```

    OpenClaw mappe également les niveaux d’exécution `/think` pour Moonshot :

    | Niveau `/think`     | Comportement Moonshot       |
    | ------------------- | --------------------------- |
    | `/think off`        | `thinking.type=disabled`    |
    | Tout niveau non off | `thinking.type=enabled`     |

    <Warning>
    Lorsque la réflexion Moonshot est activée, `tool_choice` doit être `auto` ou `none`. OpenClaw normalise les valeurs `tool_choice` incompatibles en `auto` pour assurer la compatibilité.
    </Warning>

  </Accordion>

  <Accordion title="Compatibilité de l’utilisation en streaming">
    Les points de terminaison Moonshot natifs (`https://api.moonshot.ai/v1` et
    `https://api.moonshot.cn/v1`) annoncent une compatibilité d’utilisation en streaming sur le
    transport partagé `openai-completions`. OpenClaw s’appuie sur les capacités du point de terminaison,
    de sorte que les ID de fournisseurs personnalisés compatibles ciblant les mêmes hôtes
    Moonshot natifs héritent du même comportement d’utilisation en streaming.
  </Accordion>

  <Accordion title="Référence des points de terminaison et des références de modèles">
    | Fournisseur    | Préfixe de référence de modèle | Point de terminaison         | Variable d’environnement d’authentification |
    | -------------- | ------------------------------ | ---------------------------- | ------------------------------------------- |
    | Moonshot       | `moonshot/`                    | `https://api.moonshot.ai/v1` | `MOONSHOT_API_KEY`                          |
    | Moonshot CN    | `moonshot/`                    | `https://api.moonshot.cn/v1` | `MOONSHOT_API_KEY`                          |
    | Kimi Coding    | `kimi/`                        | Point de terminaison Kimi Coding | `KIMI_API_KEY`                         |
    | Recherche web  | N/A                            | Identique à la région API Moonshot | `KIMI_API_KEY` ou `MOONSHOT_API_KEY`   |

    - La recherche web Kimi utilise `KIMI_API_KEY` ou `MOONSHOT_API_KEY`, et utilise par défaut `https://api.moonshot.ai/v1` avec le modèle `kimi-k2.5`.
    - Remplacez les métadonnées de tarification et de contexte dans `models.providers` si nécessaire.
    - Si Moonshot publie des limites de contexte différentes pour un modèle, ajustez `contextWindow` en conséquence.

  </Accordion>
</AccordionGroup>

## Liens associés

<CardGroup cols={2}>
  <Card title="Sélection du modèle" href="/fr/concepts/model-providers" icon="layers">
    Choisir les fournisseurs, les références de modèles et le comportement de basculement.
  </Card>
  <Card title="Recherche web" href="/tools/web-search" icon="magnifying-glass">
    Configuration des fournisseurs de recherche web, y compris Kimi.
  </Card>
  <Card title="Référence de configuration" href="/fr/gateway/configuration-reference" icon="gear">
    Schéma de configuration complet pour les fournisseurs, les modèles et les plugins.
  </Card>
  <Card title="Moonshot Open Platform" href="https://platform.moonshot.ai" icon="globe">
    Gestion des clés API Moonshot et documentation.
  </Card>
</CardGroup>
