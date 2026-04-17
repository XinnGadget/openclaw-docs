---
read_when:
    - Vous souhaitez utiliser des modèles GLM dans OpenClaw
    - Vous avez besoin de la convention de nommage des modèles et de la configuration
summary: Vue d’ensemble de la famille de modèles GLM et comment l’utiliser dans OpenClaw
title: GLM (Zhipu)
x-i18n:
    generated_at: "2026-04-12T23:30:46Z"
    model: gpt-5.4
    provider: openai
    source_hash: b38f0896c900fae3cf3458ff99938d73fa46973a057d1dd373ae960cb7d2e9b5
    source_path: providers/glm.md
    workflow: 15
---

# Modèles GLM

GLM est une **famille de modèles** (et non une entreprise) disponible via la plateforme Z.AI. Dans OpenClaw, les modèles GLM
sont accessibles via le fournisseur `zai` et des ID de modèle comme `zai/glm-5`.

## Prise en main

<Steps>
  <Step title="Choisir une voie d’auth et exécuter l’onboarding">
    Choisissez l’option d’onboarding correspondant à votre offre et à votre région Z.AI :

    | Choix d’auth | Idéal pour |
    | ----------- | -------- |
    | `zai-api-key` | Configuration générique par clé API avec détection automatique du point de terminaison |
    | `zai-coding-global` | Utilisateurs de l’offre Coding (global) |
    | `zai-coding-cn` | Utilisateurs de l’offre Coding (région Chine) |
    | `zai-global` | API générale (global) |
    | `zai-cn` | API générale (région Chine) |

    ```bash
    # Exemple : détection automatique générique
    openclaw onboard --auth-choice zai-api-key

    # Exemple : offre Coding globale
    openclaw onboard --auth-choice zai-coding-global
    ```

  </Step>
  <Step title="Définir GLM comme modèle par défaut">
    ```bash
    openclaw config set agents.defaults.model.primary "zai/glm-5.1"
    ```
  </Step>
  <Step title="Vérifier que les modèles sont disponibles">
    ```bash
    openclaw models list --provider zai
    ```
  </Step>
</Steps>

## Exemple de configuration

```json5
{
  env: { ZAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "zai/glm-5.1" } } },
}
```

<Tip>
`zai-api-key` permet à OpenClaw de détecter le point de terminaison Z.AI correspondant à partir de la clé et
d’appliquer automatiquement la bonne URL de base. Utilisez les choix régionaux explicites lorsque
vous voulez forcer une surface Coding Plan spécifique ou une surface d’API générale.
</Tip>

## Modèles GLM intégrés

OpenClaw initialise actuellement le fournisseur `zai` intégré avec ces références GLM :

| Modèle          | Modèle           |
| --------------- | ---------------- |
| `glm-5.1`       | `glm-4.7`        |
| `glm-5`         | `glm-4.7-flash`  |
| `glm-5-turbo`   | `glm-4.7-flashx` |
| `glm-5v-turbo`  | `glm-4.6`        |
| `glm-4.5`       | `glm-4.6v`       |
| `glm-4.5-air`   |                  |
| `glm-4.5-flash` |                  |
| `glm-4.5v`      |                  |

<Note>
La référence de modèle intégrée par défaut est `zai/glm-5.1`. Les versions GLM et leur disponibilité
peuvent changer ; consultez la documentation de Z.AI pour les informations les plus récentes.
</Note>

## Notes avancées

<AccordionGroup>
  <Accordion title="Détection automatique du point de terminaison">
    Lorsque vous utilisez le choix d’auth `zai-api-key`, OpenClaw inspecte le format de la clé
    pour déterminer la bonne URL de base Z.AI. Les choix régionaux explicites
    (`zai-coding-global`, `zai-coding-cn`, `zai-global`, `zai-cn`) remplacent
    la détection automatique et épinglent directement le point de terminaison.
  </Accordion>

  <Accordion title="Détails du fournisseur">
    Les modèles GLM sont servis par le fournisseur runtime `zai`. Pour la configuration complète du fournisseur,
    les points de terminaison régionaux et les capacités supplémentaires, voir
    la [documentation du fournisseur Z.AI](/fr/providers/zai).
  </Accordion>
</AccordionGroup>

## Liens associés

<CardGroup cols={2}>
  <Card title="Z.AI provider" href="/fr/providers/zai" icon="server">
    Configuration complète du fournisseur Z.AI et points de terminaison régionaux.
  </Card>
  <Card title="Model selection" href="/fr/concepts/model-providers" icon="layers">
    Choisir les fournisseurs, les références de modèles et le comportement de basculement.
  </Card>
</CardGroup>
