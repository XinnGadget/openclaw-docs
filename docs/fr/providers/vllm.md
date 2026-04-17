---
read_when:
    - Vous souhaitez exécuter OpenClaw avec un serveur vLLM local
    - Vous voulez des points de terminaison `/v1` compatibles OpenAI avec vos propres modèles
summary: Exécuter OpenClaw avec vLLM (serveur local compatible OpenAI)
title: vLLM
x-i18n:
    generated_at: "2026-04-12T23:32:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: a43be9ae879158fcd69d50fb3a47616fd560e3c6fe4ecb3a109bdda6a63a6a80
    source_path: providers/vllm.md
    workflow: 15
---

# vLLM

vLLM peut servir des modèles open source (et certains modèles personnalisés) via une API HTTP **compatible OpenAI**. OpenClaw se connecte à vLLM à l’aide de l’API `openai-completions`.

OpenClaw peut aussi **détecter automatiquement** les modèles disponibles depuis vLLM lorsque vous l’activez avec `VLLM_API_KEY` (n’importe quelle valeur fonctionne si votre serveur n’impose pas d’authentification) et que vous ne définissez pas d’entrée explicite `models.providers.vllm`.

| Propriété        | Valeur                                   |
| ---------------- | ---------------------------------------- |
| ID du fournisseur | `vllm`                                  |
| API              | `openai-completions` (compatible OpenAI) |
| Authentification | variable d’environnement `VLLM_API_KEY`  |
| URL de base par défaut | `http://127.0.0.1:8000/v1`         |

## Premiers pas

<Steps>
  <Step title="Démarrer vLLM avec un serveur compatible OpenAI">
    Votre URL de base doit exposer des points de terminaison `/v1` (par ex. `/v1/models`, `/v1/chat/completions`). vLLM s’exécute généralement sur :

    ```
    http://127.0.0.1:8000/v1
    ```

  </Step>
  <Step title="Définir la variable d’environnement de clé API">
    N’importe quelle valeur fonctionne si votre serveur n’impose pas d’authentification :

    ```bash
    export VLLM_API_KEY="vllm-local"
    ```

  </Step>
  <Step title="Sélectionner un modèle">
    Remplacez par l’un des ID de modèle de votre vLLM :

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "vllm/your-model-id" },
        },
      },
    }
    ```

  </Step>
  <Step title="Vérifier que le modèle est disponible">
    ```bash
    openclaw models list --provider vllm
    ```
  </Step>
</Steps>

## Détection de modèles (fournisseur implicite)

Lorsque `VLLM_API_KEY` est défini (ou qu’un profil d’authentification existe) et que vous **ne** définissez **pas** `models.providers.vllm`, OpenClaw interroge :

```
GET http://127.0.0.1:8000/v1/models
```

et convertit les ID retournés en entrées de modèle.

<Note>
Si vous définissez explicitement `models.providers.vllm`, la détection automatique est ignorée et vous devez définir les modèles manuellement.
</Note>

## Configuration explicite (modèles manuels)

Utilisez une configuration explicite lorsque :

- vLLM s’exécute sur un hôte ou un port différent
- Vous voulez épingler les valeurs `contextWindow` ou `maxTokens`
- Votre serveur exige une vraie clé API (ou vous voulez contrôler les en-têtes)

```json5
{
  models: {
    providers: {
      vllm: {
        baseUrl: "http://127.0.0.1:8000/v1",
        apiKey: "${VLLM_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "your-model-id",
            name: "Modèle vLLM local",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 128000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

## Notes avancées

<AccordionGroup>
  <Accordion title="Comportement de type proxy">
    vLLM est traité comme un backend `/v1` compatible OpenAI de type proxy, et non comme un point de terminaison
    OpenAI natif. Cela signifie :

    | Comportement | Appliqué ? |
    |----------|----------|
    | Mise en forme native des requêtes OpenAI | Non |
    | `service_tier` | Non envoyé |
    | `store` de Responses | Non envoyé |
    | Indications de cache de prompt | Non envoyées |
    | Mise en forme de charge utile de compatibilité du raisonnement OpenAI | Non appliquée |
    | En-têtes d’attribution OpenClaw cachés | Non injectés sur les URL de base personnalisées |

  </Accordion>

  <Accordion title="URL de base personnalisée">
    Si votre serveur vLLM s’exécute sur un hôte ou un port non par défaut, définissez `baseUrl` dans la configuration explicite du fournisseur :

    ```json5
    {
      models: {
        providers: {
          vllm: {
            baseUrl: "http://192.168.1.50:9000/v1",
            apiKey: "${VLLM_API_KEY}",
            api: "openai-completions",
            models: [
              {
                id: "my-custom-model",
                name: "Modèle vLLM distant",
                reasoning: false,
                input: ["text"],
                contextWindow: 64000,
                maxTokens: 4096,
              },
            ],
          },
        },
      },
    }
    ```

  </Accordion>
</AccordionGroup>

## Dépannage

<AccordionGroup>
  <Accordion title="Serveur inaccessible">
    Vérifiez que le serveur vLLM est en cours d’exécution et accessible :

    ```bash
    curl http://127.0.0.1:8000/v1/models
    ```

    Si vous voyez une erreur de connexion, vérifiez l’hôte, le port et que vLLM a démarré avec le mode serveur compatible OpenAI.

  </Accordion>

  <Accordion title="Erreurs d’authentification sur les requêtes">
    Si les requêtes échouent avec des erreurs d’authentification, définissez une vraie `VLLM_API_KEY` correspondant à la configuration de votre serveur, ou configurez explicitement le fournisseur sous `models.providers.vllm`.

    <Tip>
    Si votre serveur vLLM n’impose pas d’authentification, toute valeur non vide pour `VLLM_API_KEY` fonctionne comme signal d’activation pour OpenClaw.
    </Tip>

  </Accordion>

  <Accordion title="Aucun modèle détecté">
    La détection automatique exige que `VLLM_API_KEY` soit défini **et** qu’aucune entrée explicite `models.providers.vllm` ne soit présente. Si vous avez défini le fournisseur manuellement, OpenClaw ignore la détection et utilise uniquement les modèles que vous avez déclarés.
  </Accordion>
</AccordionGroup>

<Warning>
Plus d’aide : [Dépannage](/fr/help/troubleshooting) et [FAQ](/fr/help/faq).
</Warning>

## Liés

<CardGroup cols={2}>
  <Card title="Sélection de modèle" href="/fr/concepts/model-providers" icon="layers">
    Choisir les fournisseurs, les références de modèle et le comportement de basculement.
  </Card>
  <Card title="OpenAI" href="/fr/providers/openai" icon="bolt">
    Fournisseur OpenAI natif et comportement des routes compatibles OpenAI.
  </Card>
  <Card title="OAuth et authentification" href="/fr/gateway/authentication" icon="key">
    Détails d’authentification et règles de réutilisation des identifiants.
  </Card>
  <Card title="Dépannage" href="/fr/help/troubleshooting" icon="wrench">
    Problèmes courants et comment les résoudre.
  </Card>
</CardGroup>
