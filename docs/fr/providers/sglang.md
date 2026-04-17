---
read_when:
    - Vous souhaitez exécuter OpenClaw sur un serveur SGLang local
    - Vous souhaitez des points de terminaison `/v1` compatibles OpenAI avec vos propres modèles
summary: Exécuter OpenClaw avec SGLang (serveur auto-hébergé compatible OpenAI)
title: SGLang
x-i18n:
    generated_at: "2026-04-12T23:32:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: e0a2e50a499c3d25dcdc3af425fb023c6e3f19ed88f533ecf0eb8a2cb7ec8b0d
    source_path: providers/sglang.md
    workflow: 15
---

# SGLang

SGLang peut servir des modèles open source via une API HTTP **compatible OpenAI**.
OpenClaw peut se connecter à SGLang en utilisant l'API `openai-completions`.

OpenClaw peut également **découvrir automatiquement** les modèles disponibles depuis SGLang lorsque vous activez cette option
avec `SGLANG_API_KEY` (n'importe quelle valeur fonctionne si votre serveur n'impose pas d'authentification)
et que vous ne définissez pas d'entrée explicite `models.providers.sglang`.

## Prise en main

<Steps>
  <Step title="Démarrer SGLang">
    Lancez SGLang avec un serveur compatible OpenAI. Votre URL de base doit exposer
    des points de terminaison `/v1` (par exemple `/v1/models`, `/v1/chat/completions`). SGLang
    s'exécute généralement sur :

    - `http://127.0.0.1:30000/v1`

  </Step>
  <Step title="Définir une clé API">
    N'importe quelle valeur fonctionne si aucune authentification n'est configurée sur votre serveur :

    ```bash
    export SGLANG_API_KEY="sglang-local"
    ```

  </Step>
  <Step title="Lancer l'onboarding ou définir directement un modèle">
    ```bash
    openclaw onboard
    ```

    Ou configurez le modèle manuellement :

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "sglang/your-model-id" },
        },
      },
    }
    ```

  </Step>
</Steps>

## Découverte de modèles (fournisseur implicite)

Lorsque `SGLANG_API_KEY` est défini (ou qu'un profil d'authentification existe) et que vous **ne**
définissez **pas** `models.providers.sglang`, OpenClaw interrogera :

- `GET http://127.0.0.1:30000/v1/models`

et convertira les IDs renvoyés en entrées de modèle.

<Note>
Si vous définissez explicitement `models.providers.sglang`, la découverte automatique est ignorée et
vous devez définir les modèles manuellement.
</Note>

## Configuration explicite (modèles manuels)

Utilisez une configuration explicite lorsque :

- SGLang s'exécute sur un autre hôte/port.
- Vous souhaitez épingler les valeurs `contextWindow`/`maxTokens`.
- Votre serveur exige une vraie clé API (ou vous souhaitez contrôler les en-têtes).

```json5
{
  models: {
    providers: {
      sglang: {
        baseUrl: "http://127.0.0.1:30000/v1",
        apiKey: "${SGLANG_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "your-model-id",
            name: "Modèle SGLang local",
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

## Configuration avancée

<AccordionGroup>
  <Accordion title="Comportement de type proxy">
    SGLang est traité comme un backend `/v1` compatible OpenAI de type proxy, et non comme un
    point de terminaison OpenAI natif.

    | Comportement | SGLang |
    |----------|--------|
    | Mise en forme des requêtes réservée à OpenAI | Non appliquée |
    | `service_tier`, `store` de Responses, indices de cache d'invite | Non envoyés |
    | Mise en forme de charge utile compatible raisonnement | Non appliquée |
    | En-têtes d'attribution masqués (`originator`, `version`, `User-Agent`) | Non injectés sur les URL de base SGLang personnalisées |

  </Accordion>

  <Accordion title="Dépannage">
    **Serveur inaccessible**

    Vérifiez que le serveur est en cours d'exécution et répond :

    ```bash
    curl http://127.0.0.1:30000/v1/models
    ```

    **Erreurs d'authentification**

    Si les requêtes échouent avec des erreurs d'authentification, définissez une vraie `SGLANG_API_KEY` correspondant
    à la configuration de votre serveur, ou configurez explicitement le fournisseur dans
    `models.providers.sglang`.

    <Tip>
    Si vous exécutez SGLang sans authentification, toute valeur non vide pour
    `SGLANG_API_KEY` suffit pour activer la découverte de modèles.
    </Tip>

  </Accordion>
</AccordionGroup>

## Voir aussi

<CardGroup cols={2}>
  <Card title="Sélection de modèle" href="/fr/concepts/model-providers" icon="layers">
    Choisir les fournisseurs, les références de modèles et le comportement de basculement.
  </Card>
  <Card title="Référence de configuration" href="/fr/gateway/configuration-reference" icon="gear">
    Schéma de configuration complet, y compris les entrées de fournisseur.
  </Card>
</CardGroup>
