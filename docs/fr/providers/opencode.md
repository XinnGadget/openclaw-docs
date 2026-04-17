---
read_when:
    - Vous souhaitez un accès aux modèles hébergés par OpenCode
    - Vous souhaitez choisir entre les catalogues Zen et Go
summary: Utiliser les catalogues OpenCode Zen et Go avec OpenClaw
title: OpenCode
x-i18n:
    generated_at: "2026-04-12T23:32:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: a68444d8c403c3caba4a18ea47f078c7a4c163f874560e1fad0e818afb6e0e60
    source_path: providers/opencode.md
    workflow: 15
---

# OpenCode

OpenCode expose deux catalogues hébergés dans OpenClaw :

| Catalogue | Préfixe          | Fournisseur runtime |
| --------- | ---------------- | ------------------- |
| **Zen**   | `opencode/...`   | `opencode`          |
| **Go**    | `opencode-go/...` | `opencode-go`      |

Les deux catalogues utilisent la même clé API OpenCode. OpenClaw conserve des ID de fournisseur runtime
distincts afin que le routage amont par modèle reste correct, mais l’onboarding et la documentation les traitent
comme une configuration OpenCode unique.

## Prise en main

<Tabs>
  <Tab title="Catalogue Zen">
    **Idéal pour :** le proxy multi-modèle OpenCode organisé (Claude, GPT, Gemini).

    <Steps>
      <Step title="Exécuter l’onboarding">
        ```bash
        openclaw onboard --auth-choice opencode-zen
        ```

        Ou transmettez directement la clé :

        ```bash
        openclaw onboard --opencode-zen-api-key "$OPENCODE_API_KEY"
        ```
      </Step>
      <Step title="Définir un modèle Zen comme modèle par défaut">
        ```bash
        openclaw config set agents.defaults.model.primary "opencode/claude-opus-4-6"
        ```
      </Step>
      <Step title="Vérifier que les modèles sont disponibles">
        ```bash
        openclaw models list --provider opencode
        ```
      </Step>
    </Steps>

  </Tab>

  <Tab title="Catalogue Go">
    **Idéal pour :** la gamme Kimi, GLM et MiniMax hébergée par OpenCode.

    <Steps>
      <Step title="Exécuter l’onboarding">
        ```bash
        openclaw onboard --auth-choice opencode-go
        ```

        Ou transmettez directement la clé :

        ```bash
        openclaw onboard --opencode-go-api-key "$OPENCODE_API_KEY"
        ```
      </Step>
      <Step title="Définir un modèle Go comme modèle par défaut">
        ```bash
        openclaw config set agents.defaults.model.primary "opencode-go/kimi-k2.5"
        ```
      </Step>
      <Step title="Vérifier que les modèles sont disponibles">
        ```bash
        openclaw models list --provider opencode-go
        ```
      </Step>
    </Steps>

  </Tab>
</Tabs>

## Exemple de configuration

```json5
{
  env: { OPENCODE_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-6" } } },
}
```

## Catalogues

### Zen

| Propriété         | Valeur                                                                  |
| ----------------- | ----------------------------------------------------------------------- |
| Fournisseur runtime | `opencode`                                                            |
| Exemples de modèles | `opencode/claude-opus-4-6`, `opencode/gpt-5.4`, `opencode/gemini-3-pro` |

### Go

| Propriété         | Valeur                                                                     |
| ----------------- | -------------------------------------------------------------------------- |
| Fournisseur runtime | `opencode-go`                                                             |
| Exemples de modèles | `opencode-go/kimi-k2.5`, `opencode-go/glm-5`, `opencode-go/minimax-m2.5` |

## Notes avancées

<AccordionGroup>
  <Accordion title="Alias de clé API">
    `OPENCODE_ZEN_API_KEY` est également pris en charge comme alias de `OPENCODE_API_KEY`.
  </Accordion>

  <Accordion title="Identifiants partagés">
    Saisir une seule clé OpenCode pendant la configuration enregistre les identifiants pour les deux fournisseurs runtime. Vous n’avez pas besoin d’exécuter l’onboarding de chaque catalogue séparément.
  </Accordion>

  <Accordion title="Facturation et tableau de bord">
    Vous vous connectez à OpenCode, ajoutez les informations de facturation et copiez votre clé API. La facturation
    et la disponibilité du catalogue sont gérées depuis le tableau de bord OpenCode.
  </Accordion>

  <Accordion title="Comportement de rejeu Gemini">
    Les références OpenCode adossées à Gemini restent sur la voie proxy-Gemini, donc OpenClaw conserve
    l’assainissement de la signature de réflexion Gemini à cet endroit sans activer la validation de rejeu Gemini native
    ni les réécritures de bootstrap.
  </Accordion>

  <Accordion title="Comportement de rejeu non-Gemini">
    Les références OpenCode non-Gemini conservent la politique minimale de rejeu compatible OpenAI.
  </Accordion>
</AccordionGroup>

<Tip>
Saisir une seule clé OpenCode pendant la configuration enregistre les identifiants pour les fournisseurs runtime Zen et
Go, vous n’avez donc besoin d’exécuter l’onboarding qu’une seule fois.
</Tip>

## Liens associés

<CardGroup cols={2}>
  <Card title="Model selection" href="/fr/concepts/model-providers" icon="layers">
    Choisir les fournisseurs, les références de modèles et le comportement de basculement.
  </Card>
  <Card title="Configuration reference" href="/fr/gateway/configuration-reference" icon="gear">
    Référence complète de configuration pour les agents, les modèles et les fournisseurs.
  </Card>
</CardGroup>
