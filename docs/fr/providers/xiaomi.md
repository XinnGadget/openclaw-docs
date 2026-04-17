---
read_when:
    - Vous voulez utiliser les modèles Xiaomi MiMo dans OpenClaw
    - Vous avez besoin de configurer `XIAOMI_API_KEY`
summary: Utiliser les modèles Xiaomi MiMo avec OpenClaw
title: Xiaomi MiMo
x-i18n:
    generated_at: "2026-04-12T23:33:13Z"
    model: gpt-5.4
    provider: openai
    source_hash: cd5a526764c796da7e1fff61301bc2ec618e1cf3857894ba2ef4b6dd9c4dc339
    source_path: providers/xiaomi.md
    workflow: 15
---

# Xiaomi MiMo

Xiaomi MiMo est la plateforme API pour les modèles **MiMo**. OpenClaw utilise le point de terminaison Xiaomi compatible OpenAI avec une authentification par clé API.

| Propriété | Valeur                          |
| --------- | ------------------------------- |
| Fournisseur | `xiaomi`                      |
| Authentification | `XIAOMI_API_KEY`         |
| API       | Compatible OpenAI               |
| URL de base | `https://api.xiaomimimo.com/v1` |

## Démarrage

<Steps>
  <Step title="Obtenir une clé API">
    Créez une clé API dans la [console Xiaomi MiMo](https://platform.xiaomimimo.com/#/console/api-keys).
  </Step>
  <Step title="Lancer l’onboarding">
    ```bash
    openclaw onboard --auth-choice xiaomi-api-key
    ```

    Ou transmettez directement la clé :

    ```bash
    openclaw onboard --auth-choice xiaomi-api-key --xiaomi-api-key "$XIAOMI_API_KEY"
    ```

  </Step>
  <Step title="Vérifier que le modèle est disponible">
    ```bash
    openclaw models list --provider xiaomi
    ```
  </Step>
</Steps>

## Modèles disponibles

| Référence du modèle    | Entrée      | Contexte  | Sortie max | Raisonnement | Remarques        |
| ---------------------- | ----------- | --------- | ---------- | ------------ | ---------------- |
| `xiaomi/mimo-v2-flash` | text        | 262,144   | 8,192      | Non          | Modèle par défaut |
| `xiaomi/mimo-v2-pro`   | text        | 1,048,576 | 32,000     | Oui          | Contexte étendu  |
| `xiaomi/mimo-v2-omni`  | text, image | 262,144   | 32,000     | Oui          | Multimodal       |

<Tip>
La référence de modèle par défaut est `xiaomi/mimo-v2-flash`. Le fournisseur est injecté automatiquement lorsque `XIAOMI_API_KEY` est défini ou lorsqu’un profil d’authentification existe.
</Tip>

## Exemple de configuration

```json5
{
  env: { XIAOMI_API_KEY: "your-key" },
  agents: { defaults: { model: { primary: "xiaomi/mimo-v2-flash" } } },
  models: {
    mode: "merge",
    providers: {
      xiaomi: {
        baseUrl: "https://api.xiaomimimo.com/v1",
        api: "openai-completions",
        apiKey: "XIAOMI_API_KEY",
        models: [
          {
            id: "mimo-v2-flash",
            name: "Xiaomi MiMo V2 Flash",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 8192,
          },
          {
            id: "mimo-v2-pro",
            name: "Xiaomi MiMo V2 Pro",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 1048576,
            maxTokens: 32000,
          },
          {
            id: "mimo-v2-omni",
            name: "Xiaomi MiMo V2 Omni",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 32000,
          },
        ],
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="Comportement d’injection automatique">
    Le fournisseur `xiaomi` est injecté automatiquement lorsque `XIAOMI_API_KEY` est défini dans votre environnement ou lorsqu’un profil d’authentification existe. Vous n’avez pas besoin de configurer manuellement le fournisseur, sauf si vous voulez remplacer les métadonnées du modèle ou l’URL de base.
  </Accordion>

  <Accordion title="Détails des modèles">
    - **mimo-v2-flash** — léger et rapide, idéal pour les tâches textuelles générales. Pas de prise en charge du raisonnement.
    - **mimo-v2-pro** — prend en charge le raisonnement avec une fenêtre de contexte de 1M tokens pour les charges de travail sur de longs documents.
    - **mimo-v2-omni** — modèle multimodal avec raisonnement activé qui accepte à la fois des entrées texte et image.

    <Note>
    Tous les modèles utilisent le préfixe `xiaomi/` (par exemple `xiaomi/mimo-v2-pro`).
    </Note>

  </Accordion>

  <Accordion title="Dépannage">
    - Si les modèles n’apparaissent pas, confirmez que `XIAOMI_API_KEY` est défini et valide.
    - Lorsque le Gateway s’exécute comme un daemon, assurez-vous que la clé est disponible pour ce processus (par exemple dans `~/.openclaw/.env` ou via `env.shellEnv`).

    <Warning>
    Les clés définies uniquement dans votre shell interactif ne sont pas visibles pour les processus gateway gérés par daemon. Utilisez `~/.openclaw/.env` ou la configuration `env.shellEnv` pour une disponibilité persistante.
    </Warning>

  </Accordion>
</AccordionGroup>

## Liens associés

<CardGroup cols={2}>
  <Card title="Sélection du modèle" href="/fr/concepts/model-providers" icon="layers">
    Choisir les fournisseurs, les références de modèles et le comportement de basculement.
  </Card>
  <Card title="Référence de configuration" href="/fr/gateway/configuration" icon="gear">
    Référence complète de configuration OpenClaw.
  </Card>
  <Card title="Console Xiaomi MiMo" href="https://platform.xiaomimimo.com" icon="arrow-up-right-from-square">
    Tableau de bord Xiaomi MiMo et gestion des clés API.
  </Card>
</CardGroup>
