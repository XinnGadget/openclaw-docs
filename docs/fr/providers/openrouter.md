---
read_when:
    - Vous souhaitez une seule clé API pour de nombreux LLMs
    - Vous souhaitez exécuter des modèles via OpenRouter dans OpenClaw
summary: Utiliser l’API unifiée d’OpenRouter pour accéder à de nombreux modèles dans OpenClaw
title: OpenRouter
x-i18n:
    generated_at: "2026-04-12T23:32:18Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9083c30b9e9846a9d4ef071c350576d4c3083475f4108871eabbef0b9bb9a368
    source_path: providers/openrouter.md
    workflow: 15
---

# OpenRouter

OpenRouter fournit une **API unifiée** qui achemine les requêtes vers de nombreux modèles derrière un seul
point de terminaison et une seule clé API. Elle est compatible OpenAI, donc la plupart des SDK OpenAI fonctionnent en changeant simplement la base URL.

## Premiers pas

<Steps>
  <Step title="Obtenir votre clé API">
    Créez une clé API sur [openrouter.ai/keys](https://openrouter.ai/keys).
  </Step>
  <Step title="Lancer l’intégration">
    ```bash
    openclaw onboard --auth-choice openrouter-api-key
    ```
  </Step>
  <Step title="(Facultatif) Basculer vers un modèle spécifique">
    L’intégration utilise par défaut `openrouter/auto`. Choisissez plus tard un modèle concret :

    ```bash
    openclaw models set openrouter/<provider>/<model>
    ```

  </Step>
</Steps>

## Exemple de configuration

```json5
{
  env: { OPENROUTER_API_KEY: "sk-or-..." },
  agents: {
    defaults: {
      model: { primary: "openrouter/auto" },
    },
  },
}
```

## Références de modèles

<Note>
Les références de modèle suivent le modèle `openrouter/<provider>/<model>`. Pour la liste complète des
fournisseurs et modèles disponibles, voir [/concepts/model-providers](/fr/concepts/model-providers).
</Note>

## Authentification et en-têtes

OpenRouter utilise en interne un jeton Bearer avec votre clé API.

Sur les vraies requêtes OpenRouter (`https://openrouter.ai/api/v1`), OpenClaw ajoute également
les en-têtes documentés d’attribution d’application d’OpenRouter :

| Header                    | Value                 |
| ------------------------- | --------------------- |
| `HTTP-Referer`            | `https://openclaw.ai` |
| `X-OpenRouter-Title`      | `OpenClaw`            |
| `X-OpenRouter-Categories` | `cli-agent`           |

<Warning>
Si vous redirigez le fournisseur OpenRouter vers un autre proxy ou une autre base URL, OpenClaw
n’injecte **pas** ces en-têtes spécifiques à OpenRouter ni les marqueurs de cache Anthropic.
</Warning>

## Notes avancées

<AccordionGroup>
  <Accordion title="Marqueurs de cache Anthropic">
    Sur les routes OpenRouter vérifiées, les références de modèle Anthropic conservent les
    marqueurs Anthropic `cache_control` spécifiques à OpenRouter qu’OpenClaw utilise pour
    une meilleure réutilisation du cache de prompt sur les blocs de prompt système/développeur.
  </Accordion>

  <Accordion title="Injection de réflexion / raisonnement">
    Sur les routes prises en charge autres que `auto`, OpenClaw mappe le niveau de réflexion sélectionné sur
    les charges utiles de raisonnement proxy d’OpenRouter. Les indications de modèle non pris en charge et
    `openrouter/auto` ignorent cette injection de raisonnement.
  </Accordion>

  <Accordion title="Mise en forme de requête propre à OpenAI">
    OpenRouter passe toujours par le chemin compatible OpenAI de style proxy, donc
    la mise en forme de requête native propre à OpenAI, comme `serviceTier`, `store` de Responses,
    les charges utiles de compatibilité de raisonnement OpenAI et les indications de cache de prompt, n’est pas transmise.
  </Accordion>

  <Accordion title="Routes basées sur Gemini">
    Les références OpenRouter basées sur Gemini restent sur le chemin proxy-Gemini : OpenClaw y conserve
    l’assainissement des signatures de réflexion Gemini, mais n’active pas la validation native du rejeu Gemini
    ni les réécritures bootstrap.
  </Accordion>

  <Accordion title="Métadonnées de routage fournisseur">
    Si vous transmettez le routage fournisseur OpenRouter dans les paramètres du modèle, OpenClaw le transfère
    comme métadonnées de routage OpenRouter avant l’exécution des wrappers de flux partagés.
  </Accordion>
</AccordionGroup>

## Lié à ce sujet

<CardGroup cols={2}>
  <Card title="Sélection de modèle" href="/fr/concepts/model-providers" icon="layers">
    Choisir les fournisseurs, les références de modèles et le comportement de failover.
  </Card>
  <Card title="Référence de configuration" href="/fr/gateway/configuration-reference" icon="gear">
    Référence complète de configuration pour les agents, les modèles et les fournisseurs.
  </Card>
</CardGroup>
