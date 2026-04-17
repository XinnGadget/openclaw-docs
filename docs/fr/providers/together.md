---
read_when:
    - Vous souhaitez utiliser Together AI avec OpenClaw
    - Vous avez besoin de la variable d’environnement de la clé API ou de l’option d’authentification CLI
summary: Configuration de Together AI (authentification + sélection du modèle)
title: Together AI
x-i18n:
    generated_at: "2026-04-12T23:32:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: 33531a1646443ac2e46ee1fbfbb60ec71093611b022618106e8e5435641680ac
    source_path: providers/together.md
    workflow: 15
---

# Together AI

[Together AI](https://together.ai) donne accès à des modèles open source de premier plan
tels que Llama, DeepSeek, Kimi, et d’autres via une API unifiée.

| Property | Value                         |
| -------- | ----------------------------- |
| Provider | `together`                    |
| Auth     | `TOGETHER_API_KEY`            |
| API      | Compatible OpenAI             |
| Base URL | `https://api.together.xyz/v1` |

## Premiers pas

<Steps>
  <Step title="Obtenir une clé API">
    Créez une clé API sur
    [api.together.ai/settings/api-keys](https://api.together.ai/settings/api-keys).
  </Step>
  <Step title="Exécuter l’onboarding">
    ```bash
    openclaw onboard --auth-choice together-api-key
    ```
  </Step>
  <Step title="Définir un modèle par défaut">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "together/moonshotai/Kimi-K2.5" },
        },
      },
    }
    ```
  </Step>
</Steps>

### Exemple non interactif

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice together-api-key \
  --together-api-key "$TOGETHER_API_KEY"
```

<Note>
Le préréglage d’onboarding définit `together/moonshotai/Kimi-K2.5` comme
modèle par défaut.
</Note>

## Catalogue intégré

OpenClaw inclut ce catalogue Together intégré :

| Model ref                                                    | Name                                   | Input       | Context    | Notes                                |
| ------------------------------------------------------------ | -------------------------------------- | ----------- | ---------- | ------------------------------------ |
| `together/moonshotai/Kimi-K2.5`                              | Kimi K2.5                              | text, image | 262,144    | Modèle par défaut ; raisonnement activé |
| `together/zai-org/GLM-4.7`                                   | GLM 4.7 Fp8                            | text        | 202,752    | Modèle texte généraliste             |
| `together/meta-llama/Llama-3.3-70B-Instruct-Turbo`           | Llama 3.3 70B Instruct Turbo           | text        | 131,072    | Modèle d’instruction rapide          |
| `together/meta-llama/Llama-4-Scout-17B-16E-Instruct`         | Llama 4 Scout 17B 16E Instruct         | text, image | 10,000,000 | Multimodal                           |
| `together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | Llama 4 Maverick 17B 128E Instruct FP8 | text, image | 20,000,000 | Multimodal                           |
| `together/deepseek-ai/DeepSeek-V3.1`                         | DeepSeek V3.1                          | text        | 131,072    | Modèle texte général                 |
| `together/deepseek-ai/DeepSeek-R1`                           | DeepSeek R1                            | text        | 131,072    | Modèle de raisonnement               |
| `together/moonshotai/Kimi-K2-Instruct-0905`                  | Kimi K2-Instruct 0905                  | text        | 262,144    | Modèle texte Kimi secondaire         |

## Génération vidéo

Le Plugin `together` intégré enregistre également la génération vidéo via l’outil partagé
`video_generate`.

| Property             | Value                                 |
| -------------------- | ------------------------------------- |
| Modèle vidéo par défaut  | `together/Wan-AI/Wan2.2-T2V-A14B` |
| Modes                | texte-vers-vidéo, référence à image unique |
| Paramètres pris en charge | `aspectRatio`, `resolution`      |

Pour utiliser Together comme fournisseur vidéo par défaut :

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "together/Wan-AI/Wan2.2-T2V-A14B",
      },
    },
  },
}
```

<Tip>
Consultez [Génération vidéo](/fr/tools/video-generation) pour les paramètres d’outil partagés,
la sélection du fournisseur et le comportement de basculement.
</Tip>

<AccordionGroup>
  <Accordion title="Note sur l’environnement">
    Si la Gateway s’exécute comme un démon (launchd/systemd), assurez-vous que
    `TOGETHER_API_KEY` est disponible pour ce processus (par exemple dans
    `~/.openclaw/.env` ou via `env.shellEnv`).

    <Warning>
    Les clés définies uniquement dans votre shell interactif ne sont pas visibles par les
    processus Gateway gérés par un démon. Utilisez `~/.openclaw/.env` ou la configuration `env.shellEnv` pour
    une disponibilité persistante.
    </Warning>

  </Accordion>

  <Accordion title="Dépannage">
    - Vérifiez que votre clé fonctionne : `openclaw models list --provider together`
    - Si les modèles n’apparaissent pas, confirmez que la clé API est définie dans le bon
      environnement pour votre processus Gateway.
    - Les références de modèle utilisent la forme `together/<model-id>`.
  </Accordion>
</AccordionGroup>

## Associé

<CardGroup cols={2}>
  <Card title="Fournisseurs de modèles" href="/fr/concepts/model-providers" icon="layers">
    Règles des fournisseurs, références de modèle et comportement de basculement.
  </Card>
  <Card title="Génération vidéo" href="/fr/tools/video-generation" icon="video">
    Paramètres partagés de l’outil de génération vidéo et sélection du fournisseur.
  </Card>
  <Card title="Référence de configuration" href="/fr/gateway/configuration-reference" icon="gear">
    Schéma de configuration complet, y compris les paramètres des fournisseurs.
  </Card>
  <Card title="Together AI" href="https://together.ai" icon="arrow-up-right-from-square">
    Tableau de bord Together AI, documentation API et tarification.
  </Card>
</CardGroup>
