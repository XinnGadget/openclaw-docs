---
read_when:
    - Vous voulez une seule clé API pour de nombreux LLM
    - Vous voulez exécuter des modèles via Kilo Gateway dans OpenClaw
summary: Utiliser l’API unifiée de Kilo Gateway pour accéder à de nombreux modèles dans OpenClaw
title: Kilocode
x-i18n:
    generated_at: "2026-04-12T23:31:13Z"
    model: gpt-5.4
    provider: openai
    source_hash: 32946f2187f3933115341cbe81006718b10583abc4deea7440b5e56366025f4a
    source_path: providers/kilocode.md
    workflow: 15
---

# Kilo Gateway

Kilo Gateway fournit une **API unifiée** qui route les requêtes vers de nombreux modèles derrière un seul point de terminaison et une seule clé API. Elle est compatible OpenAI, donc la plupart des SDK OpenAI fonctionnent en changeant simplement l’URL de base.

| Propriété | Valeur                             |
| --------- | ---------------------------------- |
| Fournisseur | `kilocode`                       |
| Authentification | `KILOCODE_API_KEY`         |
| API       | Compatible OpenAI                  |
| URL de base | `https://api.kilo.ai/api/gateway/` |

## Démarrage

<Steps>
  <Step title="Créer un compte">
    Rendez-vous sur [app.kilo.ai](https://app.kilo.ai), connectez-vous ou créez un compte, puis accédez à API Keys et générez une nouvelle clé.
  </Step>
  <Step title="Lancer l’onboarding">
    ```bash
    openclaw onboard --auth-choice kilocode-api-key
    ```

    Ou définissez directement la variable d’environnement :

    ```bash
    export KILOCODE_API_KEY="<your-kilocode-api-key>" # pragma: allowlist secret
    ```

  </Step>
  <Step title="Vérifier que le modèle est disponible">
    ```bash
    openclaw models list --provider kilocode
    ```
  </Step>
</Steps>

## Modèle par défaut

Le modèle par défaut est `kilocode/kilo/auto`, un modèle de routage intelligent détenu par le fournisseur et géré par Kilo Gateway.

<Note>
OpenClaw traite `kilocode/kilo/auto` comme la référence par défaut stable, mais ne publie pas de correspondance documentée entre tâches et modèles en amont pour cette route. Le routage exact en amont derrière `kilocode/kilo/auto` appartient à Kilo Gateway et n’est pas codé en dur dans OpenClaw.
</Note>

## Modèles disponibles

OpenClaw découvre dynamiquement les modèles disponibles depuis Kilo Gateway au démarrage. Utilisez `/models kilocode` pour voir la liste complète des modèles disponibles avec votre compte.

Tout modèle disponible sur le gateway peut être utilisé avec le préfixe `kilocode/` :

| Référence du modèle                    | Remarques                         |
| -------------------------------------- | --------------------------------- |
| `kilocode/kilo/auto`                   | Par défaut — routage intelligent  |
| `kilocode/anthropic/claude-sonnet-4`   | Anthropic via Kilo                |
| `kilocode/openai/gpt-5.4`              | OpenAI via Kilo                   |
| `kilocode/google/gemini-3-pro-preview` | Google via Kilo                   |
| ...and many more                       | Use `/models kilocode` to list all |

<Tip>
Au démarrage, OpenClaw interroge `GET https://api.kilo.ai/api/gateway/models` et fusionne les modèles découverts avant le catalogue statique de secours. Le secours groupé inclut toujours `kilocode/kilo/auto` (`Kilo Auto`) avec `input: ["text", "image"]`, `reasoning: true`, `contextWindow: 1000000` et `maxTokens: 128000`.
</Tip>

## Exemple de configuration

```json5
{
  env: { KILOCODE_API_KEY: "<your-kilocode-api-key>" }, // pragma: allowlist secret
  agents: {
    defaults: {
      model: { primary: "kilocode/kilo/auto" },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="Transport et compatibilité">
    Kilo Gateway est documenté dans le code source comme compatible OpenRouter, il reste donc sur le chemin compatible OpenAI de type proxy plutôt que sur le façonnage natif des requêtes OpenAI.

    - Les références Kilo adossées à Gemini restent sur le chemin proxy-Gemini, donc OpenClaw y conserve l’assainissement des thought-signature Gemini sans activer la validation native de relecture Gemini ni les réécritures de bootstrap.
    - Kilo Gateway utilise en interne un jeton Bearer avec votre clé API.

  </Accordion>

  <Accordion title="Wrapper de flux et raisonnement">
    Le wrapper de flux partagé de Kilo ajoute l’en-tête de l’application fournisseur et normalise les charges utiles de raisonnement proxy pour les références de modèles concrètes prises en charge.

    <Warning>
    `kilocode/kilo/auto` et les autres indications proxy sans prise en charge du raisonnement ignorent l’injection de raisonnement. Si vous avez besoin de la prise en charge du raisonnement, utilisez une référence de modèle concrète telle que `kilocode/anthropic/claude-sonnet-4`.
    </Warning>

  </Accordion>

  <Accordion title="Dépannage">
    - Si la découverte des modèles échoue au démarrage, OpenClaw revient au catalogue statique groupé contenant `kilocode/kilo/auto`.
    - Confirmez que votre clé API est valide et que les modèles souhaités sont activés sur votre compte Kilo.
    - Lorsque le Gateway s’exécute comme un daemon, assurez-vous que `KILOCODE_API_KEY` est disponible pour ce processus (par exemple dans `~/.openclaw/.env` ou via `env.shellEnv`).
  </Accordion>
</AccordionGroup>

## Liens associés

<CardGroup cols={2}>
  <Card title="Sélection du modèle" href="/fr/concepts/model-providers" icon="layers">
    Choisir les fournisseurs, les références de modèles et le comportement de basculement.
  </Card>
  <Card title="Référence de configuration" href="/fr/gateway/configuration" icon="gear">
    Référence complète de configuration OpenClaw.
  </Card>
  <Card title="Kilo Gateway" href="https://app.kilo.ai" icon="arrow-up-right-from-square">
    Tableau de bord Kilo Gateway, clés API et gestion du compte.
  </Card>
</CardGroup>
