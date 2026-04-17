---
read_when:
    - Vous souhaitez utiliser DeepSeek avec OpenClaw
    - Vous avez besoin de la variable d’environnement de clé API ou du choix d’auth CLI
summary: Configuration de DeepSeek (auth + sélection du modèle)
title: DeepSeek
x-i18n:
    generated_at: "2026-04-12T23:30:20Z"
    model: gpt-5.4
    provider: openai
    source_hash: ad06880bd1ab89f72f9e31f4927e2c099dcf6b4e0ff2b3fcc91a24468fbc089d
    source_path: providers/deepseek.md
    workflow: 15
---

# DeepSeek

[DeepSeek](https://www.deepseek.com) fournit de puissants modèles d’IA avec une API compatible OpenAI.

| Propriété | Valeur                     |
| --------- | -------------------------- |
| Fournisseur | `deepseek`               |
| Auth      | `DEEPSEEK_API_KEY`         |
| API       | Compatible OpenAI          |
| URL de base | `https://api.deepseek.com` |

## Prise en main

<Steps>
  <Step title="Obtenir votre clé API">
    Créez une clé API sur [platform.deepseek.com](https://platform.deepseek.com/api_keys).
  </Step>
  <Step title="Exécuter l’onboarding">
    ```bash
    openclaw onboard --auth-choice deepseek-api-key
    ```

    Cela vous demandera votre clé API et définira `deepseek/deepseek-chat` comme modèle par défaut.

  </Step>
  <Step title="Vérifier que les modèles sont disponibles">
    ```bash
    openclaw models list --provider deepseek
    ```
  </Step>
</Steps>

<AccordionGroup>
  <Accordion title="Configuration non interactive">
    Pour les installations scriptées ou headless, passez tous les drapeaux directement :

    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice deepseek-api-key \
      --deepseek-api-key "$DEEPSEEK_API_KEY" \
      --skip-health \
      --accept-risk
    ```

  </Accordion>
</AccordionGroup>

<Warning>
Si la Gateway s’exécute comme un daemon (launchd/systemd), assurez-vous que `DEEPSEEK_API_KEY`
est disponible pour ce processus (par exemple dans `~/.openclaw/.env` ou via
`env.shellEnv`).
</Warning>

## Catalogue intégré

| Référence de modèle          | Nom               | Entrée | Contexte | Sortie max | Notes                                                |
| ---------------------------- | ----------------- | ------ | -------- | ---------- | ---------------------------------------------------- |
| `deepseek/deepseek-chat`     | DeepSeek Chat     | text   | 131,072  | 8,192      | Modèle par défaut ; surface sans réflexion DeepSeek V3.2 |
| `deepseek/deepseek-reasoner` | DeepSeek Reasoner | text   | 131,072  | 65,536     | Surface V3.2 avec raisonnement activé                |

<Tip>
Les deux modèles intégrés annoncent actuellement la compatibilité avec l’usage du streaming dans le code source.
</Tip>

## Exemple de configuration

```json5
{
  env: { DEEPSEEK_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "deepseek/deepseek-chat" },
    },
  },
}
```

## Liens associés

<CardGroup cols={2}>
  <Card title="Model selection" href="/fr/concepts/model-providers" icon="layers">
    Choisir les fournisseurs, les références de modèles et le comportement de basculement.
  </Card>
  <Card title="Configuration reference" href="/fr/gateway/configuration-reference" icon="gear">
    Référence complète de configuration pour les agents, les modèles et les fournisseurs.
  </Card>
</CardGroup>
