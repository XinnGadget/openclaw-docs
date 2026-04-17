---
read_when:
    - Vous voulez utiliser Arcee AI avec OpenClaw
    - Vous avez besoin de la variable d’environnement de la clé API ou de l’option d’authentification de la CLI
summary: Configuration d’Arcee AI (authentification + sélection du modèle)
title: Arcee AI
x-i18n:
    generated_at: "2026-04-12T23:29:20Z"
    model: gpt-5.4
    provider: openai
    source_hash: 68c5fddbe272c69611257ceff319c4de7ad21134aaf64582d60720a6f3b853cc
    source_path: providers/arcee.md
    workflow: 15
---

# Arcee AI

[Arcee AI](https://arcee.ai) permet d’accéder à la famille de modèles à mélange d’experts Trinity via une API compatible OpenAI. Tous les modèles Trinity sont sous licence Apache 2.0.

Les modèles Arcee AI peuvent être utilisés directement via la plateforme Arcee ou via [OpenRouter](/fr/providers/openrouter).

| Propriété | Valeur                                                                                |
| --------- | ------------------------------------------------------------------------------------- |
| Fournisseur | `arcee`                                                                             |
| Authentification | `ARCEEAI_API_KEY` (direct) ou `OPENROUTER_API_KEY` (via OpenRouter)         |
| API       | Compatible OpenAI                                                                     |
| URL de base | `https://api.arcee.ai/api/v1` (direct) ou `https://openrouter.ai/api/v1` (OpenRouter) |

## Démarrage

<Tabs>
  <Tab title="Direct (plateforme Arcee)">
    <Steps>
      <Step title="Obtenir une clé API">
        Créez une clé API sur [Arcee AI](https://chat.arcee.ai/).
      </Step>
      <Step title="Lancer l’onboarding">
        ```bash
        openclaw onboard --auth-choice arceeai-api-key
        ```
      </Step>
      <Step title="Définir un modèle par défaut">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "arcee/trinity-large-thinking" },
            },
          },
        }
        ```
      </Step>
    </Steps>
  </Tab>

  <Tab title="Via OpenRouter">
    <Steps>
      <Step title="Obtenir une clé API">
        Créez une clé API sur [OpenRouter](https://openrouter.ai/keys).
      </Step>
      <Step title="Lancer l’onboarding">
        ```bash
        openclaw onboard --auth-choice arceeai-openrouter
        ```
      </Step>
      <Step title="Définir un modèle par défaut">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "arcee/trinity-large-thinking" },
            },
          },
        }
        ```

        Les mêmes références de modèle fonctionnent à la fois pour les configurations directes et OpenRouter (par exemple `arcee/trinity-large-thinking`).
      </Step>
    </Steps>

  </Tab>
</Tabs>

## Configuration non interactive

<Tabs>
  <Tab title="Direct (plateforme Arcee)">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice arceeai-api-key \
      --arceeai-api-key "$ARCEEAI_API_KEY"
    ```
  </Tab>

  <Tab title="Via OpenRouter">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice arceeai-openrouter \
      --openrouter-api-key "$OPENROUTER_API_KEY"
    ```
  </Tab>
</Tabs>

## Catalogue intégré

OpenClaw inclut actuellement ce catalogue Arcee groupé :

| Référence du modèle           | Nom                    | Entrée | Contexte | Coût (entrée/sortie par 1M) | Remarques                                  |
| ----------------------------- | ---------------------- | ------ | -------- | --------------------------- | ------------------------------------------ |
| `arcee/trinity-large-thinking` | Trinity Large Thinking | text   | 256K     | $0.25 / $0.90               | Modèle par défaut ; raisonnement activé    |
| `arcee/trinity-large-preview` | Trinity Large Preview  | text   | 128K     | $0.25 / $1.00               | Usage général ; 400B paramètres, 13B actifs |
| `arcee/trinity-mini`          | Trinity Mini 26B       | text   | 128K     | $0.045 / $0.15              | Rapide et économique ; appel de fonctions  |

<Tip>
Le préréglage d’onboarding définit `arcee/trinity-large-thinking` comme modèle par défaut.
</Tip>

## Fonctionnalités prises en charge

| Fonctionnalité                                 | Prise en charge              |
| ---------------------------------------------- | ---------------------------- |
| Streaming                                      | Oui                          |
| Utilisation d’outils / appel de fonctions      | Oui                          |
| Sortie structurée (mode JSON et schéma JSON)   | Oui                          |
| Réflexion étendue                              | Oui (Trinity Large Thinking) |

<AccordionGroup>
  <Accordion title="Remarque sur l’environnement">
    Si le Gateway s’exécute comme un daemon (launchd/systemd), assurez-vous que `ARCEEAI_API_KEY`
    (ou `OPENROUTER_API_KEY`) est disponible pour ce processus (par exemple, dans
    `~/.openclaw/.env` ou via `env.shellEnv`).
  </Accordion>

  <Accordion title="Routage OpenRouter">
    Lors de l’utilisation de modèles Arcee via OpenRouter, les mêmes références de modèle `arcee/*` s’appliquent.
    OpenClaw gère le routage de manière transparente en fonction de votre choix d’authentification. Consultez la
    [documentation du fournisseur OpenRouter](/fr/providers/openrouter) pour les détails de configuration
    spécifiques à OpenRouter.
  </Accordion>
</AccordionGroup>

## Liens associés

<CardGroup cols={2}>
  <Card title="OpenRouter" href="/fr/providers/openrouter" icon="shuffle">
    Accédez aux modèles Arcee et à beaucoup d’autres via une seule clé API.
  </Card>
  <Card title="Sélection du modèle" href="/fr/concepts/model-providers" icon="layers">
    Choisir les fournisseurs, les références de modèles et le comportement de basculement.
  </Card>
</CardGroup>
