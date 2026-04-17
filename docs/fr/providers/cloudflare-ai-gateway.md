---
read_when:
    - Vous voulez utiliser Cloudflare AI Gateway avec OpenClaw
    - Vous avez besoin de l’ID de compte, de l’ID de Gateway ou de la variable d’environnement de la clé API
summary: Configuration de Cloudflare AI Gateway (authentification + sélection du modèle)
title: Cloudflare AI Gateway
x-i18n:
    generated_at: "2026-04-12T23:30:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: 12e9589fe74e6a6335370b9cf2361a464876a392a33f8317d7fd30c3f163b2e5
    source_path: providers/cloudflare-ai-gateway.md
    workflow: 15
---

# Cloudflare AI Gateway

Cloudflare AI Gateway se place devant les API des fournisseurs et vous permet d’ajouter des analyses, de la mise en cache et des contrôles. Pour Anthropic, OpenClaw utilise l’API Anthropic Messages via votre point de terminaison Gateway.

| Propriété     | Valeur                                                                                   |
| ------------- | ---------------------------------------------------------------------------------------- |
| Fournisseur   | `cloudflare-ai-gateway`                                                                  |
| URL de base   | `https://gateway.ai.cloudflare.com/v1/<account_id>/<gateway_id>/anthropic`              |
| Modèle par défaut | `cloudflare-ai-gateway/claude-sonnet-4-5`                                           |
| Clé API       | `CLOUDFLARE_AI_GATEWAY_API_KEY` (votre clé API fournisseur pour les requêtes via le Gateway) |

<Note>
Pour les modèles Anthropic routés via Cloudflare AI Gateway, utilisez votre **clé API Anthropic** comme clé du fournisseur.
</Note>

## Démarrage

<Steps>
  <Step title="Définir la clé API du fournisseur et les détails du Gateway">
    Lancez l’onboarding et choisissez l’option d’authentification Cloudflare AI Gateway :

    ```bash
    openclaw onboard --auth-choice cloudflare-ai-gateway-api-key
    ```

    Cela vous demandera votre ID de compte, votre ID de gateway et votre clé API.

  </Step>
  <Step title="Définir un modèle par défaut">
    Ajoutez le modèle à votre configuration OpenClaw :

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "cloudflare-ai-gateway/claude-sonnet-4-5" },
        },
      },
    }
    ```

  </Step>
  <Step title="Vérifier que le modèle est disponible">
    ```bash
    openclaw models list --provider cloudflare-ai-gateway
    ```
  </Step>
</Steps>

## Exemple non interactif

Pour les configurations scriptées ou CI, transmettez toutes les valeurs sur la ligne de commande :

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice cloudflare-ai-gateway-api-key \
  --cloudflare-ai-gateway-account-id "your-account-id" \
  --cloudflare-ai-gateway-gateway-id "your-gateway-id" \
  --cloudflare-ai-gateway-api-key "$CLOUDFLARE_AI_GATEWAY_API_KEY"
```

## Configuration avancée

<AccordionGroup>
  <Accordion title="Gateways authentifiés">
    Si vous avez activé l’authentification Gateway dans Cloudflare, ajoutez l’en-tête `cf-aig-authorization`. Cela s’ajoute **en plus de** votre clé API fournisseur.

    ```json5
    {
      models: {
        providers: {
          "cloudflare-ai-gateway": {
            headers: {
              "cf-aig-authorization": "Bearer <cloudflare-ai-gateway-token>",
            },
          },
        },
      },
    }
    ```

    <Tip>
    L’en-tête `cf-aig-authorization` authentifie auprès du Cloudflare Gateway lui-même, tandis que la clé API fournisseur (par exemple, votre clé Anthropic) authentifie auprès du fournisseur en amont.
    </Tip>

  </Accordion>

  <Accordion title="Remarque sur l’environnement">
    Si le Gateway s’exécute comme un daemon (launchd/systemd), assurez-vous que `CLOUDFLARE_AI_GATEWAY_API_KEY` est disponible pour ce processus.

    <Warning>
    Une clé présente uniquement dans `~/.profile` n’aidera pas un daemon launchd/systemd, sauf si cet environnement y est également importé. Définissez la clé dans `~/.openclaw/.env` ou via `env.shellEnv` pour vous assurer que le processus gateway peut la lire.
    </Warning>

  </Accordion>
</AccordionGroup>

## Liens associés

<CardGroup cols={2}>
  <Card title="Sélection du modèle" href="/fr/concepts/model-providers" icon="layers">
    Choisir les fournisseurs, les références de modèles et le comportement de basculement.
  </Card>
  <Card title="Dépannage" href="/fr/help/troubleshooting" icon="wrench">
    Dépannage général et FAQ.
  </Card>
</CardGroup>
