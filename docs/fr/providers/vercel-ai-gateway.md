---
read_when:
    - Vous souhaitez utiliser Vercel AI Gateway avec OpenClaw
    - Vous avez besoin de la variable d'environnement de clé API ou du choix d'authentification du CLI
summary: Configuration de Vercel AI Gateway (authentification + sélection de modèle)
title: Vercel AI Gateway
x-i18n:
    generated_at: "2026-04-12T23:32:56Z"
    model: gpt-5.4
    provider: openai
    source_hash: 48c206a645d7a62e201a35ae94232323c8570fdae63129231c38d363ea78a60b
    source_path: providers/vercel-ai-gateway.md
    workflow: 15
---

# Vercel AI Gateway

Le [Vercel AI Gateway](https://vercel.com/ai-gateway) fournit une API unifiée pour
accéder à des centaines de modèles via un point de terminaison unique.

| Propriété      | Valeur                            |
| ------------- | -------------------------------- |
| Fournisseur      | `vercel-ai-gateway`              |
| Authentification          | `AI_GATEWAY_API_KEY`             |
| API           | Compatible Anthropic Messages    |
| Catalogue de modèles | Découvert automatiquement via `/v1/models` |

<Tip>
OpenClaw découvre automatiquement le catalogue Gateway `/v1/models`, donc
`/models vercel-ai-gateway` inclut des références de modèles actuelles comme
`vercel-ai-gateway/openai/gpt-5.4`.
</Tip>

## Prise en main

<Steps>
  <Step title="Définir la clé API">
    Lancez l'onboarding et choisissez l'option d'authentification AI Gateway :

    ```bash
    openclaw onboard --auth-choice ai-gateway-api-key
    ```

  </Step>
  <Step title="Définir un modèle par défaut">
    Ajoutez le modèle à votre configuration OpenClaw :

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "vercel-ai-gateway/anthropic/claude-opus-4.6" },
        },
      },
    }
    ```

  </Step>
  <Step title="Vérifier que le modèle est disponible">
    ```bash
    openclaw models list --provider vercel-ai-gateway
    ```
  </Step>
</Steps>

## Exemple non interactif

Pour des configurations scriptées ou de CI, passez toutes les valeurs sur la ligne de commande :

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice ai-gateway-api-key \
  --ai-gateway-api-key "$AI_GATEWAY_API_KEY"
```

## Raccourci d'ID de modèle

OpenClaw accepte des références de modèle Claude abrégées Vercel et les normalise à l'exécution :

| Entrée abrégée                     | Référence de modèle normalisée                          |
| ----------------------------------- | --------------------------------------------- |
| `vercel-ai-gateway/claude-opus-4.6` | `vercel-ai-gateway/anthropic/claude-opus-4.6` |
| `vercel-ai-gateway/opus-4.6`        | `vercel-ai-gateway/anthropic/claude-opus-4-6` |

<Tip>
Vous pouvez utiliser soit la forme abrégée, soit la référence de modèle pleinement qualifiée dans votre
configuration. OpenClaw résout automatiquement la forme canonique.
</Tip>

## Notes avancées

<AccordionGroup>
  <Accordion title="Variable d'environnement pour les processus daemon">
    Si la passerelle OpenClaw s'exécute comme daemon (launchd/systemd), assurez-vous que
    `AI_GATEWAY_API_KEY` est disponible pour ce processus.

    <Warning>
    Une clé définie uniquement dans `~/.profile` ne sera pas visible pour un daemon launchd/systemd
    à moins que cet environnement ne soit explicitement importé. Définissez la clé dans
    `~/.openclaw/.env` ou via `env.shellEnv` pour vous assurer que le processus de la passerelle peut
    la lire.
    </Warning>

  </Accordion>

  <Accordion title="Routage du fournisseur">
    Vercel AI Gateway route les requêtes vers le fournisseur upstream en fonction du préfixe de la
    référence de modèle. Par exemple, `vercel-ai-gateway/anthropic/claude-opus-4.6` est routé
    via Anthropic, tandis que `vercel-ai-gateway/openai/gpt-5.4` est routé via
    OpenAI. Votre unique `AI_GATEWAY_API_KEY` gère l'authentification pour tous les
    fournisseurs upstream.
  </Accordion>
</AccordionGroup>

## Voir aussi

<CardGroup cols={2}>
  <Card title="Sélection de modèle" href="/fr/concepts/model-providers" icon="layers">
    Choisir les fournisseurs, les références de modèles et le comportement de basculement.
  </Card>
  <Card title="Dépannage" href="/fr/help/troubleshooting" icon="wrench">
    Dépannage général et FAQ.
  </Card>
</CardGroup>
