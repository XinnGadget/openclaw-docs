---
read_when:
    - Vous souhaitez une seule clé API pour de nombreux LLM
    - Vous avez besoin d’un guide de configuration pour Baidu Qianfan
summary: Utilisez l’API unifiée de Qianfan pour accéder à de nombreux modèles dans OpenClaw
title: Qianfan
x-i18n:
    generated_at: "2026-04-12T23:32:28Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1d0eeee9ec24b335c2fb8ac5e985a9edc35cfc5b2641c545cb295dd2de619f50
    source_path: providers/qianfan.md
    workflow: 15
---

# Qianfan

Qianfan est la plateforme MaaS de Baidu, fournissant une **API unifiée** qui route les requêtes vers de nombreux modèles derrière un unique
point de terminaison et une unique clé API. Elle est compatible OpenAI, donc la plupart des SDK OpenAI fonctionnent en changeant simplement l’URL de base.

| Property | Value                             |
| -------- | --------------------------------- |
| Provider | `qianfan`                         |
| Auth     | `QIANFAN_API_KEY`                 |
| API      | Compatible OpenAI                 |
| Base URL | `https://qianfan.baidubce.com/v2` |

## Premiers pas

<Steps>
  <Step title="Créer un compte Baidu Cloud">
    Inscrivez-vous ou connectez-vous dans la [Console Qianfan](https://console.bce.baidu.com/qianfan/ais/console/apiKey) et assurez-vous que l’accès à l’API Qianfan est activé.
  </Step>
  <Step title="Générer une clé API">
    Créez une nouvelle application ou sélectionnez-en une existante, puis générez une clé API. Le format de la clé est `bce-v3/ALTAK-...`.
  </Step>
  <Step title="Exécuter l’onboarding">
    ```bash
    openclaw onboard --auth-choice qianfan-api-key
    ```
  </Step>
  <Step title="Vérifier que le modèle est disponible">
    ```bash
    openclaw models list --provider qianfan
    ```
  </Step>
</Steps>

## Modèles disponibles

| Model ref                            | Input       | Context | Max output | Reasoning | Notes              |
| ------------------------------------ | ----------- | ------- | ---------- | --------- | ------------------ |
| `qianfan/deepseek-v3.2`              | text        | 98,304  | 32,768     | Oui       | Modèle par défaut  |
| `qianfan/ernie-5.0-thinking-preview` | text, image | 119,000 | 64,000     | Oui       | Multimodal         |

<Tip>
La référence de modèle intégrée par défaut est `qianfan/deepseek-v3.2`. Vous n’avez besoin de remplacer `models.providers.qianfan` que si vous avez besoin d’une URL de base personnalisée ou de métadonnées de modèle personnalisées.
</Tip>

## Exemple de configuration

```json5
{
  env: { QIANFAN_API_KEY: "bce-v3/ALTAK-..." },
  agents: {
    defaults: {
      model: { primary: "qianfan/deepseek-v3.2" },
      models: {
        "qianfan/deepseek-v3.2": { alias: "QIANFAN" },
      },
    },
  },
  models: {
    providers: {
      qianfan: {
        baseUrl: "https://qianfan.baidubce.com/v2",
        api: "openai-completions",
        models: [
          {
            id: "deepseek-v3.2",
            name: "DEEPSEEK V3.2",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 98304,
            maxTokens: 32768,
          },
          {
            id: "ernie-5.0-thinking-preview",
            name: "ERNIE-5.0-Thinking-Preview",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 119000,
            maxTokens: 64000,
          },
        ],
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="Transport et compatibilité">
    Qianfan fonctionne via le chemin de transport compatible OpenAI, et non via la mise en forme native des requêtes OpenAI. Cela signifie que les fonctionnalités standard du SDK OpenAI fonctionnent, mais que les paramètres spécifiques au fournisseur peuvent ne pas être transmis.
  </Accordion>

  <Accordion title="Catalogue et remplacements">
    Le catalogue intégré inclut actuellement `deepseek-v3.2` et `ernie-5.0-thinking-preview`. Ajoutez ou remplacez `models.providers.qianfan` uniquement lorsque vous avez besoin d’une URL de base personnalisée ou de métadonnées de modèle personnalisées.

    <Note>
    Les références de modèle utilisent le préfixe `qianfan/` (par exemple `qianfan/deepseek-v3.2`).
    </Note>

  </Accordion>

  <Accordion title="Dépannage">
    - Assurez-vous que votre clé API commence par `bce-v3/ALTAK-` et que l’accès à l’API Qianfan est activé dans la console Baidu Cloud.
    - Si les modèles ne sont pas listés, confirmez que le service Qianfan est activé sur votre compte.
    - L’URL de base par défaut est `https://qianfan.baidubce.com/v2`. Ne la modifiez que si vous utilisez un point de terminaison personnalisé ou un proxy.
  </Accordion>
</AccordionGroup>

## Associé

<CardGroup cols={2}>
  <Card title="Sélection du modèle" href="/fr/concepts/model-providers" icon="layers">
    Choisir les fournisseurs, les références de modèle et le comportement de basculement.
  </Card>
  <Card title="Référence de configuration" href="/fr/gateway/configuration" icon="gear">
    Référence complète de la configuration OpenClaw.
  </Card>
  <Card title="Configuration d’agent" href="/fr/concepts/agent" icon="robot">
    Configuration des valeurs par défaut des agents et des affectations de modèle.
  </Card>
  <Card title="Documentation API Qianfan" href="https://cloud.baidu.com/doc/qianfan-api/s/3m7of64lb" icon="arrow-up-right-from-square">
    Documentation officielle de l’API Qianfan.
  </Card>
</CardGroup>
