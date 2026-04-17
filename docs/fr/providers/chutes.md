---
read_when:
    - Vous voulez utiliser Chutes avec OpenClaw
    - Vous avez besoin du parcours de configuration OAuth ou par clé API
    - Vous voulez connaître le modèle par défaut, les alias ou le comportement de découverte
summary: Configuration de Chutes (OAuth ou clé API, découverte des modèles, alias)
title: Chutes
x-i18n:
    generated_at: "2026-04-12T23:29:46Z"
    model: gpt-5.4
    provider: openai
    source_hash: 07c52b1d1d2792412e6daabc92df5310434b3520116d9e0fd2ad26bfa5297e1c
    source_path: providers/chutes.md
    workflow: 15
---

# Chutes

[Chutes](https://chutes.ai) expose des catalogues de modèles open source via une API compatible OpenAI. OpenClaw prend en charge à la fois l’authentification OAuth dans le navigateur et l’authentification directe par clé API pour le fournisseur groupé `chutes`.

| Propriété | Valeur                       |
| --------- | ---------------------------- |
| Fournisseur | `chutes`                   |
| API       | Compatible OpenAI            |
| URL de base | `https://llm.chutes.ai/v1` |
| Authentification | OAuth ou clé API (voir ci-dessous) |

## Démarrage

<Tabs>
  <Tab title="OAuth">
    <Steps>
      <Step title="Lancer le flux d’onboarding OAuth">
        ```bash
        openclaw onboard --auth-choice chutes
        ```
        OpenClaw lance le flux navigateur localement, ou affiche un flux URL + collage de redirection sur les hôtes distants/sans interface. Les jetons OAuth sont actualisés automatiquement via les profils d’authentification OpenClaw.
      </Step>
      <Step title="Vérifier le modèle par défaut">
        Après l’onboarding, le modèle par défaut est défini sur
        `chutes/zai-org/GLM-4.7-TEE` et le catalogue Chutes groupé est
        enregistré.
      </Step>
    </Steps>
  </Tab>
  <Tab title="Clé API">
    <Steps>
      <Step title="Obtenir une clé API">
        Créez une clé sur
        [chutes.ai/settings/api-keys](https://chutes.ai/settings/api-keys).
      </Step>
      <Step title="Lancer le flux d’onboarding par clé API">
        ```bash
        openclaw onboard --auth-choice chutes-api-key
        ```
      </Step>
      <Step title="Vérifier le modèle par défaut">
        Après l’onboarding, le modèle par défaut est défini sur
        `chutes/zai-org/GLM-4.7-TEE` et le catalogue Chutes groupé est
        enregistré.
      </Step>
    </Steps>
  </Tab>
</Tabs>

<Note>
Les deux parcours d’authentification enregistrent le catalogue Chutes groupé et définissent le modèle par défaut sur `chutes/zai-org/GLM-4.7-TEE`. Variables d’environnement d’exécution : `CHUTES_API_KEY`, `CHUTES_OAUTH_TOKEN`.
</Note>

## Comportement de découverte

Lorsque l’authentification Chutes est disponible, OpenClaw interroge le catalogue Chutes avec cet identifiant et utilise les modèles découverts. Si la découverte échoue, OpenClaw revient à un catalogue statique groupé afin que l’onboarding et le démarrage continuent de fonctionner.

## Alias par défaut

OpenClaw enregistre trois alias pratiques pour le catalogue Chutes groupé :

| Alias           | Modèle cible                                          |
| --------------- | ----------------------------------------------------- |
| `chutes-fast`   | `chutes/zai-org/GLM-4.7-FP8`                          |
| `chutes-pro`    | `chutes/deepseek-ai/DeepSeek-V3.2-TEE`                |
| `chutes-vision` | `chutes/chutesai/Mistral-Small-3.2-24B-Instruct-2506` |

## Catalogue de démarrage intégré

Le catalogue de secours groupé inclut les références Chutes actuelles :

| Référence du modèle                                   |
| ----------------------------------------------------- |
| `chutes/zai-org/GLM-4.7-TEE`                          |
| `chutes/zai-org/GLM-5-TEE`                            |
| `chutes/deepseek-ai/DeepSeek-V3.2-TEE`                |
| `chutes/deepseek-ai/DeepSeek-R1-0528-TEE`             |
| `chutes/moonshotai/Kimi-K2.5-TEE`                     |
| `chutes/chutesai/Mistral-Small-3.2-24B-Instruct-2506` |
| `chutes/Qwen/Qwen3-Coder-Next-TEE`                    |
| `chutes/openai/gpt-oss-120b-TEE`                      |

## Exemple de configuration

```json5
{
  agents: {
    defaults: {
      model: { primary: "chutes/zai-org/GLM-4.7-TEE" },
      models: {
        "chutes/zai-org/GLM-4.7-TEE": { alias: "Chutes GLM 4.7" },
        "chutes/deepseek-ai/DeepSeek-V3.2-TEE": { alias: "Chutes DeepSeek V3.2" },
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="Remplacements OAuth">
    Vous pouvez personnaliser le flux OAuth avec des variables d’environnement facultatives :

    | Variable | Objectif |
    | -------- | ------- |
    | `CHUTES_CLIENT_ID` | ID client OAuth personnalisé |
    | `CHUTES_CLIENT_SECRET` | Secret client OAuth personnalisé |
    | `CHUTES_OAUTH_REDIRECT_URI` | URI de redirection personnalisée |
    | `CHUTES_OAUTH_SCOPES` | Portées OAuth personnalisées |

    Consultez la [documentation OAuth de Chutes](https://chutes.ai/docs/sign-in-with-chutes/overview)
    pour les exigences des applications de redirection et l’aide.

  </Accordion>

  <Accordion title="Remarques">
    - La découverte par clé API et par OAuth utilisent toutes deux le même identifiant de fournisseur `chutes`.
    - Les modèles Chutes sont enregistrés sous la forme `chutes/<model-id>`.
    - Si la découverte échoue au démarrage, le catalogue statique groupé est utilisé automatiquement.
  </Accordion>
</AccordionGroup>

## Liens associés

<CardGroup cols={2}>
  <Card title="Fournisseurs de modèles" href="/fr/concepts/model-providers" icon="layers">
    Règles des fournisseurs, références de modèles et comportement de basculement.
  </Card>
  <Card title="Référence de configuration" href="/fr/gateway/configuration-reference" icon="gear">
    Schéma de configuration complet, y compris les paramètres des fournisseurs.
  </Card>
  <Card title="Chutes" href="https://chutes.ai" icon="arrow-up-right-from-square">
    Tableau de bord Chutes et documentation de l’API.
  </Card>
  <Card title="Clés API Chutes" href="https://chutes.ai/settings/api-keys" icon="key">
    Créer et gérer des clés API Chutes.
  </Card>
</CardGroup>
