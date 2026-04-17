---
read_when:
    - Vous souhaitez utiliser Fireworks avec OpenClaw
    - Vous avez besoin de la variable d’environnement de la clé API Fireworks ou de l’identifiant du modèle par défaut
summary: Configuration de Fireworks (authentification + sélection du modèle)
title: Fireworks
x-i18n:
    generated_at: "2026-04-12T23:30:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1a85d9507c19e275fdd846a303d844eda8045d008774d4dde1eae408e8716b6f
    source_path: providers/fireworks.md
    workflow: 15
---

# Fireworks

[Fireworks](https://fireworks.ai) expose des modèles open-weight et routés via une API compatible OpenAI. OpenClaw inclut un Plugin fournisseur Fireworks intégré.

| Property      | Value                                                  |
| ------------- | ------------------------------------------------------ |
| Provider      | `fireworks`                                            |
| Auth          | `FIREWORKS_API_KEY`                                    |
| API           | chat/completions compatible OpenAI                     |
| Base URL      | `https://api.fireworks.ai/inference/v1`                |
| Modèle par défaut | `fireworks/accounts/fireworks/routers/kimi-k2p5-turbo` |

## Premiers pas

<Steps>
  <Step title="Configurer l’authentification Fireworks via l’onboarding">
    ```bash
    openclaw onboard --auth-choice fireworks-api-key
    ```

    Cela stocke votre clé Fireworks dans la configuration OpenClaw et définit le modèle de démarrage Fire Pass comme modèle par défaut.

  </Step>
  <Step title="Vérifier que le modèle est disponible">
    ```bash
    openclaw models list --provider fireworks
    ```
  </Step>
</Steps>

## Exemple non interactif

Pour les configurations scriptées ou CI, passez toutes les valeurs sur la ligne de commande :

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice fireworks-api-key \
  --fireworks-api-key "$FIREWORKS_API_KEY" \
  --skip-health \
  --accept-risk
```

## Catalogue intégré

| Model ref                                              | Name                        | Input      | Context | Max output | Notes                                      |
| ------------------------------------------------------ | --------------------------- | ---------- | ------- | ---------- | ------------------------------------------ |
| `fireworks/accounts/fireworks/routers/kimi-k2p5-turbo` | Kimi K2.5 Turbo (Fire Pass) | text,image | 256,000 | 256,000    | Modèle de démarrage intégré par défaut sur Fireworks |

<Tip>
Si Fireworks publie un modèle plus récent, comme une nouvelle version de Qwen ou Gemma, vous pouvez y passer directement en utilisant son identifiant de modèle Fireworks sans attendre une mise à jour du catalogue intégré.
</Tip>

## Identifiants de modèle Fireworks personnalisés

OpenClaw accepte aussi des identifiants de modèle Fireworks dynamiques. Utilisez l’identifiant exact du modèle ou du routeur tel qu’affiché par Fireworks et préfixez-le avec `fireworks/`.

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "fireworks/accounts/fireworks/routers/kimi-k2p5-turbo",
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="Fonctionnement du préfixage des identifiants de modèle">
    Chaque référence de modèle Fireworks dans OpenClaw commence par `fireworks/`, suivi de l’identifiant exact ou du chemin du routeur depuis la plateforme Fireworks. Par exemple :

    - Modèle routeur : `fireworks/accounts/fireworks/routers/kimi-k2p5-turbo`
    - Modèle direct : `fireworks/accounts/fireworks/models/<model-name>`

    OpenClaw supprime le préfixe `fireworks/` lors de la construction de la requête API et envoie le chemin restant au point de terminaison Fireworks.

  </Accordion>

  <Accordion title="Note sur l’environnement">
    Si la Gateway s’exécute en dehors de votre shell interactif, assurez-vous que `FIREWORKS_API_KEY` est également disponible pour ce processus.

    <Warning>
    Une clé présente uniquement dans `~/.profile` n’aidera pas un démon launchd/systemd à moins que cet environnement n’y soit aussi importé. Définissez la clé dans `~/.openclaw/.env` ou via `env.shellEnv` pour garantir que le processus Gateway puisse la lire.
    </Warning>

  </Accordion>
</AccordionGroup>

## Associé

<CardGroup cols={2}>
  <Card title="Sélection du modèle" href="/fr/concepts/model-providers" icon="layers">
    Choisir les fournisseurs, les références de modèle et le comportement de basculement.
  </Card>
  <Card title="Dépannage" href="/fr/help/troubleshooting" icon="wrench">
    Dépannage général et FAQ.
  </Card>
</CardGroup>
