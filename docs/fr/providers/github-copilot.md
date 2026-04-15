---
read_when:
    - Vous souhaitez utiliser GitHub Copilot comme fournisseur de modèles
    - Vous avez besoin du flux `openclaw models auth login-github-copilot`.
summary: Connectez-vous à GitHub Copilot depuis OpenClaw en utilisant le flux d’appareil
title: GitHub Copilot
x-i18n:
    generated_at: "2026-04-15T14:40:31Z"
    model: gpt-5.4
    provider: openai
    source_hash: b8258fecff22fb73b057de878462941f6eb86d0c5f775c5eac4840e95ba5eccf
    source_path: providers/github-copilot.md
    workflow: 15
---

# GitHub Copilot

GitHub Copilot est l’assistant de programmation par IA de GitHub. Il fournit un accès aux modèles Copilot pour votre compte et votre forfait GitHub. OpenClaw peut utiliser Copilot comme fournisseur de modèles de deux façons différentes.

## Deux façons d’utiliser Copilot dans OpenClaw

<Tabs>
  <Tab title="Fournisseur intégré (github-copilot)">
    Utilisez le flux natif de connexion par appareil pour obtenir un jeton GitHub, puis l’échanger contre des jetons d’API Copilot lors de l’exécution d’OpenClaw. Il s’agit du chemin **par défaut** et du plus simple, car il ne nécessite pas VS Code.

    <Steps>
      <Step title="Exécuter la commande de connexion">
        ```bash
        openclaw models auth login-github-copilot
        ```

        Il vous sera demandé de visiter une URL et de saisir un code à usage unique. Gardez le terminal ouvert jusqu’à la fin de l’opération.
      </Step>
      <Step title="Définir un modèle par défaut">
        ```bash
        openclaw models set github-copilot/gpt-4o
        ```

        Ou dans la configuration :

        ```json5
        {
          agents: { defaults: { model: { primary: "github-copilot/gpt-4o" } } },
        }
        ```
      </Step>
    </Steps>

  </Tab>

  <Tab title="Plugin Copilot Proxy (copilot-proxy)">
    Utilisez l’extension VS Code **Copilot Proxy** comme pont local. OpenClaw communique avec le point de terminaison `/v1` du proxy et utilise la liste de modèles que vous y configurez.

    <Note>
    Choisissez cette option si vous utilisez déjà Copilot Proxy dans VS Code ou si vous devez passer par lui. Vous devez activer le Plugin et laisser l’extension VS Code en cours d’exécution.
    </Note>

  </Tab>
</Tabs>

## Indicateurs facultatifs

| Flag            | Description                                         |
| --------------- | --------------------------------------------------- |
| `--yes`         | Ignorer l’invite de confirmation                    |
| `--set-default` | Appliquer également le modèle par défaut recommandé du fournisseur |

```bash
# Ignorer la confirmation
openclaw models auth login-github-copilot --yes

# Se connecter et définir le modèle par défaut en une seule étape
openclaw models auth login --provider github-copilot --method device --set-default
```

<AccordionGroup>
  <Accordion title="TTY interactif requis">
    Le flux de connexion par appareil nécessite un TTY interactif. Exécutez-le directement dans un terminal, et non dans un script non interactif ou un pipeline CI.
  </Accordion>

  <Accordion title="La disponibilité des modèles dépend de votre forfait">
    La disponibilité des modèles Copilot dépend de votre forfait GitHub. Si un modèle est refusé, essayez un autre identifiant (par exemple `github-copilot/gpt-4.1`).
  </Accordion>

  <Accordion title="Sélection du transport">
    Les identifiants de modèles Claude utilisent automatiquement le transport Anthropic Messages. Les modèles GPT, de série o et Gemini conservent le transport OpenAI Responses. OpenClaw sélectionne le transport correct en fonction de la référence du modèle.
  </Accordion>

  <Accordion title="Ordre de résolution des variables d’environnement">
    OpenClaw résout l’authentification Copilot à partir des variables d’environnement dans l’ordre de priorité suivant :

    | Priority | Variable              | Notes                            |
    | -------- | --------------------- | -------------------------------- |
    | 1        | `COPILOT_GITHUB_TOKEN` | Priorité la plus élevée, spécifique à Copilot |
    | 2        | `GH_TOKEN`            | Jeton GitHub CLI (repli)         |
    | 3        | `GITHUB_TOKEN`        | Jeton GitHub standard (priorité la plus basse)   |

    Lorsque plusieurs variables sont définies, OpenClaw utilise celle ayant la priorité la plus élevée.
    Le flux de connexion par appareil (`openclaw models auth login-github-copilot`) stocke
    son jeton dans le magasin de profils d’authentification et a priorité sur toutes les variables d’environnement.

  </Accordion>

  <Accordion title="Stockage du jeton">
    La connexion stocke un jeton GitHub dans le magasin de profils d’authentification et l’échange contre un jeton d’API Copilot lors de l’exécution d’OpenClaw. Vous n’avez pas besoin de gérer le jeton manuellement.
  </Accordion>
</AccordionGroup>

<Warning>
Nécessite un TTY interactif. Exécutez la commande de connexion directement dans un terminal, et non dans un script sans interface ou une tâche CI.
</Warning>

## Intégrations de recherche en mémoire

GitHub Copilot peut également servir de fournisseur d’intégrations pour la
[recherche en mémoire](/fr/concepts/memory-search). Si vous avez un abonnement Copilot et
vous êtes connecté, OpenClaw peut l’utiliser pour les intégrations sans clé d’API distincte.

### Détection automatique

Lorsque `memorySearch.provider` vaut `"auto"` (par défaut), GitHub Copilot est essayé
avec une priorité de 15 -- après les intégrations locales mais avant OpenAI et les autres fournisseurs payants. Si un jeton GitHub est disponible, OpenClaw découvre les modèles
d’intégration disponibles via l’API Copilot et sélectionne automatiquement le meilleur.

### Configuration explicite

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "github-copilot",
        // Facultatif : remplacer le modèle détecté automatiquement
        model: "text-embedding-3-small",
      },
    },
  },
}
```

### Fonctionnement

1. OpenClaw résout votre jeton GitHub (à partir des variables d’environnement ou du profil d’authentification).
2. L’échange contre un jeton d’API Copilot de courte durée.
3. Interroge le point de terminaison Copilot `/models` pour découvrir les modèles d’intégration disponibles.
4. Sélectionne le meilleur modèle (préfère `text-embedding-3-small`).
5. Envoie les requêtes d’intégration au point de terminaison Copilot `/embeddings`.

La disponibilité des modèles dépend de votre forfait GitHub. Si aucun modèle d’intégration n’est
disponible, OpenClaw ignore Copilot et essaie le fournisseur suivant.

## Associé

<CardGroup cols={2}>
  <Card title="Sélection du modèle" href="/fr/concepts/model-providers" icon="layers">
    Choisir les fournisseurs, les références de modèles et le comportement de basculement.
  </Card>
  <Card title="OAuth et authentification" href="/fr/gateway/authentication" icon="key">
    Détails sur l’authentification et règles de réutilisation des identifiants.
  </Card>
</CardGroup>
