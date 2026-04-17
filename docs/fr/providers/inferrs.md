---
read_when:
    - Vous souhaitez exécuter OpenClaw sur un serveur inferrs local
    - Vous servez Gemma ou un autre modèle via inferrs
    - Vous avez besoin des indicateurs de compatibilité OpenClaw exacts pour inferrs
summary: Exécuter OpenClaw via inferrs (serveur local compatible OpenAI)
title: inferrs
x-i18n:
    generated_at: "2026-04-12T23:31:11Z"
    model: gpt-5.4
    provider: openai
    source_hash: 847dcc131fe51dfe163dcd60075dbfaa664662ea2a5c3986ccb08ddd37e8c31f
    source_path: providers/inferrs.md
    workflow: 15
---

# inferrs

[inferrs](https://github.com/ericcurtin/inferrs) peut servir des modèles locaux derrière une
API `/v1` compatible OpenAI. OpenClaw fonctionne avec `inferrs` via le chemin générique
`openai-completions`.

`inferrs` est actuellement mieux traité comme un backend OpenAI-compatible auto-hébergé personnalisé,
et non comme un Plugin fournisseur OpenClaw dédié.

## Prise en main

<Steps>
  <Step title="Démarrer inferrs avec un modèle">
    ```bash
    inferrs serve google/gemma-4-E2B-it \
      --host 127.0.0.1 \
      --port 8080 \
      --device metal
    ```
  </Step>
  <Step title="Vérifier que le serveur est accessible">
    ```bash
    curl http://127.0.0.1:8080/health
    curl http://127.0.0.1:8080/v1/models
    ```
  </Step>
  <Step title="Ajouter une entrée de fournisseur OpenClaw">
    Ajoutez une entrée de fournisseur explicite et faites pointer votre modèle par défaut vers elle. Voir l’exemple complet de configuration ci-dessous.
  </Step>
</Steps>

## Exemple complet de configuration

Cet exemple utilise Gemma 4 sur un serveur `inferrs` local.

```json5
{
  agents: {
    defaults: {
      model: { primary: "inferrs/google/gemma-4-E2B-it" },
      models: {
        "inferrs/google/gemma-4-E2B-it": {
          alias: "Gemma 4 (inferrs)",
        },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      inferrs: {
        baseUrl: "http://127.0.0.1:8080/v1",
        apiKey: "inferrs-local",
        api: "openai-completions",
        models: [
          {
            id: "google/gemma-4-E2B-it",
            name: "Gemma 4 E2B (inferrs)",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 131072,
            maxTokens: 4096,
            compat: {
              requiresStringContent: true,
            },
          },
        ],
      },
    },
  },
}
```

## Avancé

<AccordionGroup>
  <Accordion title="Pourquoi `requiresStringContent` est important">
    Certaines routes Chat Completions de `inferrs` n’acceptent que des
    `messages[].content` de type chaîne, et non des tableaux structurés de parties de contenu.

    <Warning>
    Si les exécutions OpenClaw échouent avec une erreur du type :

    ```text
    messages[1].content: invalid type: sequence, expected a string
    ```

    définissez `compat.requiresStringContent: true` dans votre entrée de modèle.
    </Warning>

    ```json5
    compat: {
      requiresStringContent: true
    }
    ```

    OpenClaw aplatira les parties de contenu purement textuelles en chaînes simples avant d’envoyer
    la requête.

  </Accordion>

  <Accordion title="Réserve concernant Gemma et le schéma d’outils">
    Certaines combinaisons actuelles de `inferrs` + Gemma acceptent de petites requêtes directes
    `/v1/chat/completions` mais échouent toujours sur des tours complets du runtime agent d’OpenClaw.

    Si cela se produit, essayez d’abord ceci :

    ```json5
    compat: {
      requiresStringContent: true,
      supportsTools: false
    }
    ```

    Cela désactive la surface de schéma d’outils d’OpenClaw pour le modèle et peut réduire la pression du prompt
    sur des backends locaux plus stricts.

    Si de petites requêtes directes fonctionnent toujours mais que des tours d’agent OpenClaw normaux continuent de
    planter dans `inferrs`, le problème restant relève généralement du comportement en amont du modèle/serveur
    plutôt que de la couche de transport d’OpenClaw.

  </Accordion>

  <Accordion title="Test smoke manuel">
    Une fois configuré, testez les deux couches :

    ```bash
    curl http://127.0.0.1:8080/v1/chat/completions \
      -H 'content-type: application/json' \
      -d '{"model":"google/gemma-4-E2B-it","messages":[{"role":"user","content":"What is 2 + 2?"}],"stream":false}'
    ```

    ```bash
    openclaw infer model run \
      --model inferrs/google/gemma-4-E2B-it \
      --prompt "What is 2 + 2? Reply with one short sentence." \
      --json
    ```

    Si la première commande fonctionne mais que la seconde échoue, consultez la section de dépannage ci-dessous.

  </Accordion>

  <Accordion title="Comportement de type proxy">
    `inferrs` est traité comme un backend `/v1` compatible OpenAI de type proxy, et non comme un
    point de terminaison OpenAI natif.

    - La mise en forme des requêtes réservée à OpenAI natif ne s’applique pas ici
    - Pas de `service_tier`, pas de `store` Responses, pas d’indices de cache de prompt, et pas de mise en forme de payload de compatibilité de raisonnement OpenAI
    - Les en-têtes d’attribution cachés d’OpenClaw (`originator`, `version`, `User-Agent`)
      ne sont pas injectés sur des `baseUrl` `inferrs` personnalisées

  </Accordion>
</AccordionGroup>

## Dépannage

<AccordionGroup>
  <Accordion title="`curl /v1/models` échoue">
    `inferrs` n’est pas en cours d’exécution, n’est pas accessible, ou n’est pas lié à l’hôte/port
    attendu. Assurez-vous que le serveur est démarré et à l’écoute sur l’adresse que vous avez
    configurée.
  </Accordion>

  <Accordion title="`messages[].content` attendait une chaîne">
    Définissez `compat.requiresStringContent: true` dans l’entrée de modèle. Voir la
    section `requiresStringContent` ci-dessus pour plus de détails.
  </Accordion>

  <Accordion title="Les appels directs à `/v1/chat/completions` réussissent mais `openclaw infer model run` échoue">
    Essayez de définir `compat.supportsTools: false` pour désactiver la surface du schéma d’outils.
    Voir la réserve ci-dessus sur le schéma d’outils de Gemma.
  </Accordion>

  <Accordion title="`inferrs` plante encore sur des tours d’agent plus volumineux">
    Si OpenClaw ne reçoit plus d’erreurs de schéma mais que `inferrs` plante encore sur des tours d’agent
    plus volumineux, considérez cela comme une limite en amont de `inferrs` ou du modèle. Réduisez
    la pression du prompt ou passez à un autre backend local ou à un autre modèle.
  </Accordion>
</AccordionGroup>

<Tip>
Pour une aide générale, voir [Troubleshooting](/fr/help/troubleshooting) et [FAQ](/fr/help/faq).
</Tip>

## Voir aussi

<CardGroup cols={2}>
  <Card title="Local models" href="/fr/gateway/local-models" icon="server">
    Exécuter OpenClaw sur des serveurs de modèles locaux.
  </Card>
  <Card title="Gateway troubleshooting" href="/fr/gateway/troubleshooting#local-openai-compatible-backend-passes-direct-probes-but-agent-runs-fail" icon="wrench">
    Déboguer les backends OpenAI compatibles locaux qui réussissent les sondes mais échouent lors des exécutions d’agent.
  </Card>
  <Card title="Model providers" href="/fr/concepts/model-providers" icon="layers">
    Vue d’ensemble de tous les fournisseurs, références de modèles et comportements de basculement.
  </Card>
</CardGroup>
