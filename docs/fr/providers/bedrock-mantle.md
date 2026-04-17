---
read_when:
    - Vous souhaitez utiliser des modèles OSS hébergés sur Bedrock Mantle avec OpenClaw
    - Vous avez besoin du point de terminaison Mantle compatible OpenAI pour GPT-OSS, Qwen, Kimi ou GLM
summary: Utiliser les modèles Amazon Bedrock Mantle (compatibles OpenAI) avec OpenClaw
title: Amazon Bedrock Mantle
x-i18n:
    generated_at: "2026-04-12T23:29:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: 27e602b6f6a3ae92427de135cb9df6356e0daaea6b6fe54723a7542dd0d5d21e
    source_path: providers/bedrock-mantle.md
    workflow: 15
---

# Amazon Bedrock Mantle

OpenClaw inclut un fournisseur **Amazon Bedrock Mantle** intégré qui se connecte au
point de terminaison Mantle compatible OpenAI. Mantle héberge des modèles open source et
tiers (GPT-OSS, Qwen, Kimi, GLM et similaires) via une surface standard
`/v1/chat/completions` reposant sur l’infrastructure Bedrock.

| Propriété        | Valeur                                                                              |
| ---------------- | ----------------------------------------------------------------------------------- |
| ID du fournisseur | `amazon-bedrock-mantle`                                                            |
| API              | `openai-completions` (compatible OpenAI)                                            |
| Auth             | `AWS_BEARER_TOKEN_BEDROCK` explicite ou génération de bearer token via la chaîne d’identifiants IAM |
| Région par défaut | `us-east-1` (remplacez avec `AWS_REGION` ou `AWS_DEFAULT_REGION`)                  |

## Prise en main

Choisissez votre méthode d’auth préférée et suivez les étapes de configuration.

<Tabs>
  <Tab title="Bearer token explicite">
    **Idéal pour :** les environnements où vous disposez déjà d’un bearer token Mantle.

    <Steps>
      <Step title="Définir le bearer token sur l’hôte gateway">
        ```bash
        export AWS_BEARER_TOKEN_BEDROCK="..."
        ```

        Vous pouvez également définir une région (par défaut `us-east-1`) :

        ```bash
        export AWS_REGION="us-west-2"
        ```
      </Step>
      <Step title="Vérifier que les modèles sont détectés">
        ```bash
        openclaw models list
        ```

        Les modèles détectés apparaissent sous le fournisseur `amazon-bedrock-mantle`. Aucune
        configuration supplémentaire n’est requise sauf si vous souhaitez remplacer les valeurs par défaut.
      </Step>
    </Steps>

  </Tab>

  <Tab title="Identifiants IAM">
    **Idéal pour :** l’utilisation d’identifiants compatibles AWS SDK (configuration partagée, SSO, identité web, rôles d’instance ou de tâche).

    <Steps>
      <Step title="Configurer les identifiants AWS sur l’hôte gateway">
        Toute source d’auth compatible AWS SDK fonctionne :

        ```bash
        export AWS_PROFILE="default"
        export AWS_REGION="us-west-2"
        ```
      </Step>
      <Step title="Vérifier que les modèles sont détectés">
        ```bash
        openclaw models list
        ```

        OpenClaw génère automatiquement un bearer token Mantle à partir de la chaîne d’identifiants.
      </Step>
    </Steps>

    <Tip>
    Lorsque `AWS_BEARER_TOKEN_BEDROCK` n’est pas défini, OpenClaw génère le bearer token pour vous à partir de la chaîne d’identifiants par défaut AWS, y compris les profils partagés d’identifiants/configuration, SSO, identité web, ainsi que les rôles d’instance ou de tâche.
    </Tip>

  </Tab>
</Tabs>

## Détection automatique des modèles

Lorsque `AWS_BEARER_TOKEN_BEDROCK` est défini, OpenClaw l’utilise directement. Sinon,
OpenClaw tente de générer un bearer token Mantle à partir de la chaîne d’identifiants AWS par défaut.
Il détecte ensuite les modèles Mantle disponibles en interrogeant le
point de terminaison régional `/v1/models`.

| Comportement         | Détail                    |
| -------------------- | ------------------------- |
| Cache de détection   | Résultats mis en cache pendant 1 heure |
| Actualisation du token IAM | Toutes les heures      |

<Note>
Le bearer token est le même `AWS_BEARER_TOKEN_BEDROCK` que celui utilisé par le fournisseur standard [Amazon Bedrock](/fr/providers/bedrock).
</Note>

### Régions prises en charge

`us-east-1`, `us-east-2`, `us-west-2`, `ap-northeast-1`,
`ap-south-1`, `ap-southeast-3`, `eu-central-1`, `eu-west-1`, `eu-west-2`,
`eu-south-1`, `eu-north-1`, `sa-east-1`.

## Configuration manuelle

Si vous préférez une configuration explicite à la détection automatique :

```json5
{
  models: {
    providers: {
      "amazon-bedrock-mantle": {
        baseUrl: "https://bedrock-mantle.us-east-1.api.aws/v1",
        api: "openai-completions",
        auth: "api-key",
        apiKey: "env:AWS_BEARER_TOKEN_BEDROCK",
        models: [
          {
            id: "gpt-oss-120b",
            name: "GPT-OSS 120B",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 32000,
            maxTokens: 4096,
          },
        ],
      },
    },
  },
}
```

## Notes avancées

<AccordionGroup>
  <Accordion title="Prise en charge du raisonnement">
    La prise en charge du raisonnement est déduite à partir des ID de modèle contenant des motifs comme
    `thinking`, `reasoner` ou `gpt-oss-120b`. OpenClaw définit `reasoning: true`
    automatiquement pour les modèles correspondants lors de la détection.
  </Accordion>

  <Accordion title="Indisponibilité du point de terminaison">
    Si le point de terminaison Mantle est indisponible ou ne renvoie aucun modèle, le fournisseur est
    ignoré silencieusement. OpenClaw ne renvoie pas d’erreur ; les autres fournisseurs configurés
    continuent de fonctionner normalement.
  </Accordion>

  <Accordion title="Relation avec le fournisseur Amazon Bedrock">
    Bedrock Mantle est un fournisseur distinct du fournisseur standard
    [Amazon Bedrock](/fr/providers/bedrock). Mantle utilise une
    surface `/v1` compatible OpenAI, tandis que le fournisseur Bedrock standard utilise
    l’API Bedrock native.

    Les deux fournisseurs partagent le même identifiant `AWS_BEARER_TOKEN_BEDROCK` lorsqu’il
    est présent.

  </Accordion>
</AccordionGroup>

## Liens associés

<CardGroup cols={2}>
  <Card title="Amazon Bedrock" href="/fr/providers/bedrock" icon="cloud">
    Fournisseur Bedrock natif pour Anthropic Claude, Titan et d’autres modèles.
  </Card>
  <Card title="Sélection des modèles" href="/fr/concepts/model-providers" icon="layers">
    Choisir les fournisseurs, les références de modèles et le comportement de basculement.
  </Card>
  <Card title="OAuth et auth" href="/fr/gateway/authentication" icon="key">
    Détails d’auth et règles de réutilisation des identifiants.
  </Card>
  <Card title="Dépannage" href="/fr/help/troubleshooting" icon="wrench">
    Problèmes courants et comment les résoudre.
  </Card>
</CardGroup>
