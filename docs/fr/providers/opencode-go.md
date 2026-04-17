---
read_when:
    - Vous souhaitez utiliser le catalogue OpenCode Go
    - Vous avez besoin des références de modèles runtime pour les modèles hébergés par Go
summary: Utiliser le catalogue OpenCode Go avec la configuration OpenCode partagée
title: OpenCode Go
x-i18n:
    generated_at: "2026-04-12T23:31:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: d1f0f182de81729616ccc19125d93ba0445de2349daf7067b52e8c15b9d3539c
    source_path: providers/opencode-go.md
    workflow: 15
---

# OpenCode Go

OpenCode Go est le catalogue Go au sein d’[OpenCode](/fr/providers/opencode).
Il utilise la même `OPENCODE_API_KEY` que le catalogue Zen, mais conserve l’ID de fournisseur runtime
`opencode-go` afin que le routage amont par modèle reste correct.

| Propriété         | Valeur                        |
| ----------------- | ----------------------------- |
| Fournisseur runtime | `opencode-go`               |
| Auth              | `OPENCODE_API_KEY`            |
| Configuration parente | [OpenCode](/fr/providers/opencode) |

## Modèles pris en charge

| Référence de modèle       | Nom          |
| ------------------------- | ------------ |
| `opencode-go/kimi-k2.5`   | Kimi K2.5    |
| `opencode-go/glm-5`       | GLM 5        |
| `opencode-go/minimax-m2.5` | MiniMax M2.5 |

## Prise en main

<Tabs>
  <Tab title="Interactive">
    <Steps>
      <Step title="Exécuter l’onboarding">
        ```bash
        openclaw onboard --auth-choice opencode-go
        ```
      </Step>
      <Step title="Définir un modèle Go par défaut">
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

  <Tab title="Non-interactive">
    <Steps>
      <Step title="Transmettre directement la clé">
        ```bash
        openclaw onboard --opencode-go-api-key "$OPENCODE_API_KEY"
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
  env: { OPENCODE_API_KEY: "YOUR_API_KEY_HERE" }, // pragma: allowlist secret
  agents: { defaults: { model: { primary: "opencode-go/kimi-k2.5" } } },
}
```

## Notes avancées

<AccordionGroup>
  <Accordion title="Comportement de routage">
    OpenClaw gère automatiquement le routage par modèle lorsque la référence de modèle utilise
    `opencode-go/...`. Aucune configuration supplémentaire du fournisseur n’est requise.
  </Accordion>

  <Accordion title="Convention des références runtime">
    Les références runtime restent explicites : `opencode/...` pour Zen, `opencode-go/...` pour Go.
    Cela permet de conserver un routage amont correct par modèle dans les deux catalogues.
  </Accordion>

  <Accordion title="Identifiants partagés">
    La même `OPENCODE_API_KEY` est utilisée par les catalogues Zen et Go. Saisir
    la clé pendant la configuration enregistre les identifiants pour les deux fournisseurs runtime.
  </Accordion>
</AccordionGroup>

<Tip>
Voir [OpenCode](/fr/providers/opencode) pour la vue d’ensemble de l’onboarding partagé et la référence complète des catalogues
Zen + Go.
</Tip>

## Liens associés

<CardGroup cols={2}>
  <Card title="OpenCode (parent)" href="/fr/providers/opencode" icon="server">
    Onboarding partagé, vue d’ensemble du catalogue et notes avancées.
  </Card>
  <Card title="Model selection" href="/fr/concepts/model-providers" icon="layers">
    Choisir les fournisseurs, les références de modèles et le comportement de basculement.
  </Card>
</CardGroup>
