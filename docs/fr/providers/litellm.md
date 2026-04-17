---
read_when:
    - Vous souhaitez faire passer OpenClaw par un proxy LiteLLM
    - Vous avez besoin du suivi des coûts, de la journalisation ou du routage des modèles via LiteLLM
summary: Exécutez OpenClaw via le proxy LiteLLM pour un accès unifié aux modèles et le suivi des coûts
title: LiteLLM
x-i18n:
    generated_at: "2026-04-12T23:31:13Z"
    model: gpt-5.4
    provider: openai
    source_hash: 766692eb83a1be83811d8e09a970697530ffdd4f3392247cfb2927fd590364a0
    source_path: providers/litellm.md
    workflow: 15
---

# LiteLLM

[LiteLLM](https://litellm.ai) est une passerelle LLM open source qui fournit une API unifiée vers plus de 100 fournisseurs de modèles. Faites passer OpenClaw par LiteLLM pour obtenir un suivi centralisé des coûts, de la journalisation, et la flexibilité de changer de backend sans modifier votre configuration OpenClaw.

<Tip>
**Pourquoi utiliser LiteLLM avec OpenClaw ?**

- **Suivi des coûts** — Voir exactement ce que dépense OpenClaw sur l’ensemble des modèles
- **Routage des modèles** — Basculer entre Claude, GPT-4, Gemini, Bedrock sans modifier la configuration
- **Clés virtuelles** — Créer des clés avec des limites de dépenses pour OpenClaw
- **Journalisation** — Journaux complets des requêtes/réponses pour le débogage
- **Basculements** — Basculement automatique si votre fournisseur principal est indisponible
  </Tip>

## Démarrage rapide

<Tabs>
  <Tab title="Onboarding (recommandé)">
    **Idéal pour :** le moyen le plus rapide d’obtenir une configuration LiteLLM fonctionnelle.

    <Steps>
      <Step title="Exécuter l’onboarding">
        ```bash
        openclaw onboard --auth-choice litellm-api-key
        ```
      </Step>
    </Steps>

  </Tab>

  <Tab title="Configuration manuelle">
    **Idéal pour :** un contrôle total sur l’installation et la configuration.

    <Steps>
      <Step title="Démarrer le proxy LiteLLM">
        ```bash
        pip install 'litellm[proxy]'
        litellm --model claude-opus-4-6
        ```
      </Step>
      <Step title="Pointer OpenClaw vers LiteLLM">
        ```bash
        export LITELLM_API_KEY="your-litellm-key"

        openclaw
        ```

        C’est tout. OpenClaw passe maintenant par LiteLLM.
      </Step>
    </Steps>

  </Tab>
</Tabs>

## Configuration

### Variables d’environnement

```bash
export LITELLM_API_KEY="sk-litellm-key"
```

### Fichier de configuration

```json5
{
  models: {
    providers: {
      litellm: {
        baseUrl: "http://localhost:4000",
        apiKey: "${LITELLM_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "claude-opus-4-6",
            name: "Claude Opus 4.6",
            reasoning: true,
            input: ["text", "image"],
            contextWindow: 200000,
            maxTokens: 64000,
          },
          {
            id: "gpt-4o",
            name: "GPT-4o",
            reasoning: false,
            input: ["text", "image"],
            contextWindow: 128000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
  agents: {
    defaults: {
      model: { primary: "litellm/claude-opus-4-6" },
    },
  },
}
```

## Sujets avancés

<AccordionGroup>
  <Accordion title="Clés virtuelles">
    Créez une clé dédiée à OpenClaw avec des limites de dépenses :

    ```bash
    curl -X POST "http://localhost:4000/key/generate" \
      -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
      -H "Content-Type: application/json" \
      -d '{
        "key_alias": "openclaw",
        "max_budget": 50.00,
        "budget_duration": "monthly"
      }'
    ```

    Utilisez la clé générée comme `LITELLM_API_KEY`.

  </Accordion>

  <Accordion title="Routage des modèles">
    LiteLLM peut router les requêtes de modèle vers différents backends. Configurez cela dans votre `config.yaml` LiteLLM :

    ```yaml
    model_list:
      - model_name: claude-opus-4-6
        litellm_params:
          model: claude-opus-4-6
          api_key: os.environ/ANTHROPIC_API_KEY

      - model_name: gpt-4o
        litellm_params:
          model: gpt-4o
          api_key: os.environ/OPENAI_API_KEY
    ```

    OpenClaw continue de demander `claude-opus-4-6` — LiteLLM se charge du routage.

  </Accordion>

  <Accordion title="Afficher l’utilisation">
    Consultez le tableau de bord LiteLLM ou l’API :

    ```bash
    # Informations sur la clé
    curl "http://localhost:4000/key/info" \
      -H "Authorization: Bearer sk-litellm-key"

    # Journaux de dépenses
    curl "http://localhost:4000/spend/logs" \
      -H "Authorization: Bearer $LITELLM_MASTER_KEY"
    ```

  </Accordion>

  <Accordion title="Notes sur le comportement du proxy">
    - LiteLLM s’exécute sur `http://localhost:4000` par défaut
    - OpenClaw se connecte via le point de terminaison `/v1`
      compatible OpenAI de style proxy de LiteLLM
    - La mise en forme des requêtes native uniquement OpenAI ne s’applique pas via LiteLLM :
      pas de `service_tier`, pas de `store` Responses, pas d’indices de cache d’invite, et pas de
      mise en forme de payload de compatibilité de raisonnement OpenAI
    - Les en-têtes d’attribution cachés OpenClaw (`originator`, `version`, `User-Agent`)
      ne sont pas injectés sur les URL de base LiteLLM personnalisées
  </Accordion>
</AccordionGroup>

<Note>
Pour la configuration générale des fournisseurs et le comportement de basculement, consultez [Fournisseurs de modèles](/fr/concepts/model-providers).
</Note>

## Associé

<CardGroup cols={2}>
  <Card title="Documentation LiteLLM" href="https://docs.litellm.ai" icon="book">
    Documentation officielle LiteLLM et référence API.
  </Card>
  <Card title="Fournisseurs de modèles" href="/fr/concepts/model-providers" icon="layers">
    Vue d’ensemble de tous les fournisseurs, références de modèles et comportement de basculement.
  </Card>
  <Card title="Configuration" href="/fr/gateway/configuration" icon="gear">
    Référence de configuration complète.
  </Card>
  <Card title="Sélection du modèle" href="/fr/concepts/models" icon="brain">
    Comment choisir et configurer les modèles.
  </Card>
</CardGroup>
