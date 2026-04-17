---
read_when:
    - Vous souhaitez utiliser Qwen avec OpenClaw
    - Vous utilisiez auparavant Qwen OAuth
summary: Utiliser Qwen Cloud via le fournisseur qwen intégré d’OpenClaw
title: Qwen
x-i18n:
    generated_at: "2026-04-12T23:32:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: 5247f851ef891645df6572d748ea15deeea47cd1d75858bc0d044a2930065106
    source_path: providers/qwen.md
    workflow: 15
---

# Qwen

<Warning>

**Qwen OAuth a été supprimé.** L’intégration OAuth gratuite
(`qwen-portal`) qui utilisait les points de terminaison `portal.qwen.ai` n’est plus disponible.
Voir [Issue #49557](https://github.com/openclaw/openclaw/issues/49557) pour
le contexte.

</Warning>

OpenClaw traite désormais Qwen comme un fournisseur intégré de premier plan avec l’ID
canonique `qwen`. Le fournisseur intégré cible les points de terminaison Qwen Cloud / Alibaba DashScope et
Coding Plan, et conserve les ID hérités `modelstudio` comme alias de
compatibilité.

- Fournisseur : `qwen`
- Variable d’environnement préférée : `QWEN_API_KEY`
- Également acceptées pour compatibilité : `MODELSTUDIO_API_KEY`, `DASHSCOPE_API_KEY`
- Style d’API : compatible OpenAI

<Tip>
Si vous souhaitez utiliser `qwen3.6-plus`, privilégiez le point de terminaison **Standard (pay-as-you-go)**.
La prise en charge de Coding Plan peut être en retard par rapport au catalogue public.
</Tip>

## Prise en main

Choisissez votre type d’offre et suivez les étapes de configuration.

<Tabs>
  <Tab title="Coding Plan (abonnement)">
    **Idéal pour :** un accès par abonnement via le Qwen Coding Plan.

    <Steps>
      <Step title="Obtenir votre clé API">
        Créez ou copiez une clé API depuis [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys).
      </Step>
      <Step title="Exécuter l’onboarding">
        Pour le point de terminaison **Global** :

        ```bash
        openclaw onboard --auth-choice qwen-api-key
        ```

        Pour le point de terminaison **China** :

        ```bash
        openclaw onboard --auth-choice qwen-api-key-cn
        ```
      </Step>
      <Step title="Définir un modèle par défaut">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "qwen/qwen3.5-plus" },
            },
          },
        }
        ```
      </Step>
      <Step title="Vérifier que le modèle est disponible">
        ```bash
        openclaw models list --provider qwen
        ```
      </Step>
    </Steps>

    <Note>
    Les ID d’auth-choice hérités `modelstudio-*` et les références de modèles `modelstudio/...` fonctionnent toujours
    comme alias de compatibilité, mais les nouveaux flux de configuration doivent privilégier les ID d’auth-choice canoniques
    `qwen-*` et les références de modèles `qwen/...`.
    </Note>

  </Tab>

  <Tab title="Standard (pay-as-you-go)">
    **Idéal pour :** un accès à l’usage via le point de terminaison Standard Model Studio, y compris pour des modèles comme `qwen3.6-plus` qui peuvent ne pas être disponibles sur le Coding Plan.

    <Steps>
      <Step title="Obtenir votre clé API">
        Créez ou copiez une clé API depuis [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys).
      </Step>
      <Step title="Exécuter l’onboarding">
        Pour le point de terminaison **Global** :

        ```bash
        openclaw onboard --auth-choice qwen-standard-api-key
        ```

        Pour le point de terminaison **China** :

        ```bash
        openclaw onboard --auth-choice qwen-standard-api-key-cn
        ```
      </Step>
      <Step title="Définir un modèle par défaut">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "qwen/qwen3.5-plus" },
            },
          },
        }
        ```
      </Step>
      <Step title="Vérifier que le modèle est disponible">
        ```bash
        openclaw models list --provider qwen
        ```
      </Step>
    </Steps>

    <Note>
    Les ID d’auth-choice hérités `modelstudio-*` et les références de modèles `modelstudio/...` fonctionnent toujours
    comme alias de compatibilité, mais les nouveaux flux de configuration doivent privilégier les ID d’auth-choice canoniques
    `qwen-*` et les références de modèles `qwen/...`.
    </Note>

  </Tab>
</Tabs>

## Types d’offre et points de terminaison

| Offre                      | Région | Choix d’auth               | Point de terminaison                             |
| -------------------------- | ------ | -------------------------- | ------------------------------------------------ |
| Standard (pay-as-you-go)   | China  | `qwen-standard-api-key-cn` | `dashscope.aliyuncs.com/compatible-mode/v1`      |
| Standard (pay-as-you-go)   | Global | `qwen-standard-api-key`    | `dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| Coding Plan (abonnement)   | China  | `qwen-api-key-cn`          | `coding.dashscope.aliyuncs.com/v1`               |
| Coding Plan (abonnement)   | Global | `qwen-api-key`             | `coding-intl.dashscope.aliyuncs.com/v1`          |

Le fournisseur sélectionne automatiquement le point de terminaison en fonction de votre choix d’auth. Les choix
canoniques utilisent la famille `qwen-*` ; `modelstudio-*` reste réservé à la compatibilité.
Vous pouvez remplacer cela avec un `baseUrl` personnalisé dans la configuration.

<Tip>
**Gérer les clés :** [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys) |
**Documentation :** [docs.qwencloud.com](https://docs.qwencloud.com/developer-guides/getting-started/introduction)
</Tip>

## Catalogue intégré

OpenClaw inclut actuellement ce catalogue Qwen intégré. Le catalogue configuré dépend
du point de terminaison : les configurations Coding Plan omettent les modèles connus pour ne fonctionner que sur
le point de terminaison Standard.

| Référence de modèle         | Entrée      | Contexte  | Notes                                              |
| --------------------------- | ----------- | --------- | -------------------------------------------------- |
| `qwen/qwen3.5-plus`         | text, image | 1,000,000 | Modèle par défaut                                  |
| `qwen/qwen3.6-plus`         | text, image | 1,000,000 | Préférez les points de terminaison Standard lorsque vous avez besoin de ce modèle |
| `qwen/qwen3-max-2026-01-23` | text        | 262,144   | Gamme Qwen Max                                     |
| `qwen/qwen3-coder-next`     | text        | 262,144   | Code                                               |
| `qwen/qwen3-coder-plus`     | text        | 1,000,000 | Code                                               |
| `qwen/MiniMax-M2.5`         | text        | 1,000,000 | Raisonnement activé                                |
| `qwen/glm-5`                | text        | 202,752   | GLM                                                |
| `qwen/glm-4.7`              | text        | 202,752   | GLM                                                |
| `qwen/kimi-k2.5`            | text, image | 262,144   | Moonshot AI via Alibaba                            |

<Note>
La disponibilité peut encore varier selon le point de terminaison et l’offre de facturation, même lorsqu’un modèle est
présent dans le catalogue intégré.
</Note>

## Extensions multimodales

L’extension `qwen` expose également des capacités multimodales sur les points de terminaison DashScope **Standard**
(et non sur les points de terminaison Coding Plan) :

- **Compréhension vidéo** via `qwen-vl-max-latest`
- **Génération vidéo Wan** via `wan2.6-t2v` (par défaut), `wan2.6-i2v`, `wan2.6-r2v`, `wan2.6-r2v-flash`, `wan2.7-r2v`

Pour utiliser Qwen comme fournisseur vidéo par défaut :

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: { primary: "qwen/wan2.6-t2v" },
    },
  },
}
```

<Note>
Voir [Video Generation](/fr/tools/video-generation) pour les paramètres partagés de l’outil, la sélection du fournisseur et le comportement de basculement.
</Note>

## Avancé

<AccordionGroup>
  <Accordion title="Compréhension d’images et de vidéos">
    Le Plugin Qwen intégré enregistre la compréhension des médias pour les images et la vidéo
    sur les points de terminaison DashScope **Standard** (et non sur les points de terminaison Coding Plan).

    | Propriété          | Valeur                |
    | ------------------ | --------------------- |
    | Modèle             | `qwen-vl-max-latest`  |
    | Entrée prise en charge | Images, vidéo      |

    La compréhension des médias est résolue automatiquement à partir de l’auth Qwen configurée — aucune
    configuration supplémentaire n’est nécessaire. Assurez-vous d’utiliser un point de terminaison
    Standard (pay-as-you-go) pour la prise en charge de la compréhension des médias.

  </Accordion>

  <Accordion title="Disponibilité de Qwen 3.6 Plus">
    `qwen3.6-plus` est disponible sur les points de terminaison Model Studio Standard (pay-as-you-go) :

    - China : `dashscope.aliyuncs.com/compatible-mode/v1`
    - Global : `dashscope-intl.aliyuncs.com/compatible-mode/v1`

    Si les points de terminaison Coding Plan renvoient une erreur « unsupported model » pour
    `qwen3.6-plus`, passez à Standard (pay-as-you-go) au lieu du couple
    point de terminaison/clé Coding Plan.

  </Accordion>

  <Accordion title="Plan de capacités">
    L’extension `qwen` est en train d’être positionnée comme le fournisseur d’origine pour toute la surface Qwen
    Cloud, et pas seulement pour les modèles de code/texte.

    - **Modèles texte/chat :** intégrés maintenant
    - **Appel d’outils, sortie structurée, thinking :** hérités du transport compatible OpenAI
    - **Génération d’images :** prévue au niveau du Plugin fournisseur
    - **Compréhension image/vidéo :** intégrée maintenant sur le point de terminaison Standard
    - **Parole/audio :** prévue au niveau du Plugin fournisseur
    - **Embeddings/reranking mémoire :** prévus via la surface d’adaptateur d’embeddings
    - **Génération vidéo :** intégrée maintenant via la capacité partagée de génération vidéo

  </Accordion>

  <Accordion title="Détails de la génération vidéo">
    Pour la génération vidéo, OpenClaw mappe la région Qwen configurée vers l’hôte
    DashScope AIGC correspondant avant de soumettre la tâche :

    - Global/Intl : `https://dashscope-intl.aliyuncs.com`
    - China : `https://dashscope.aliyuncs.com`

    Cela signifie qu’un `models.providers.qwen.baseUrl` normal pointant vers l’un ou l’autre des hôtes Qwen
    Coding Plan ou Standard conserve malgré tout la génération vidéo sur le bon
    point de terminaison vidéo DashScope régional.

    Limites actuelles intégrées de génération vidéo Qwen :

    - Jusqu’à **1** vidéo de sortie par requête
    - Jusqu’à **1** image d’entrée
    - Jusqu’à **4** vidéos d’entrée
    - Jusqu’à **10 secondes** de durée
    - Prend en charge `size`, `aspectRatio`, `resolution`, `audio` et `watermark`
    - Le mode image/vidéo de référence exige actuellement des **URL http(s) distantes**. Les chemins de
      fichiers locaux sont rejetés d’emblée, car le point de terminaison vidéo DashScope n’accepte pas les tampons locaux téléversés pour ces références.

  </Accordion>

  <Accordion title="Compatibilité de l’usage du streaming">
    Les points de terminaison natifs Model Studio annoncent la compatibilité de l’usage du streaming sur le
    transport partagé `openai-completions`. OpenClaw s’appuie désormais sur les capacités des points de terminaison,
    de sorte que les ID de fournisseurs personnalisés compatibles DashScope ciblant les mêmes hôtes natifs
    héritent du même comportement d’usage du streaming au lieu
    d’exiger spécifiquement l’ID de fournisseur intégré `qwen`.

    La compatibilité native d’usage du streaming s’applique à la fois aux hôtes Coding Plan et
    aux hôtes Standard compatibles DashScope :

    - `https://coding.dashscope.aliyuncs.com/v1`
    - `https://coding-intl.dashscope.aliyuncs.com/v1`
    - `https://dashscope.aliyuncs.com/compatible-mode/v1`
    - `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`

  </Accordion>

  <Accordion title="Régions des points de terminaison multimodaux">
    Les surfaces multimodales (compréhension vidéo et génération vidéo Wan) utilisent les
    points de terminaison DashScope **Standard**, et non les points de terminaison Coding Plan :

    - URL de base Standard Global/Intl : `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
    - URL de base Standard China : `https://dashscope.aliyuncs.com/compatible-mode/v1`

  </Accordion>

  <Accordion title="Environnement et configuration daemon">
    Si la Gateway s’exécute comme un daemon (launchd/systemd), assurez-vous que `QWEN_API_KEY` est
    disponible pour ce processus (par exemple dans `~/.openclaw/.env` ou via
    `env.shellEnv`).
  </Accordion>
</AccordionGroup>

## Liens associés

<CardGroup cols={2}>
  <Card title="Model selection" href="/fr/concepts/model-providers" icon="layers">
    Choisir les fournisseurs, les références de modèles et le comportement de basculement.
  </Card>
  <Card title="Video generation" href="/fr/tools/video-generation" icon="video">
    Paramètres partagés de l’outil vidéo et sélection du fournisseur.
  </Card>
  <Card title="Alibaba (ModelStudio)" href="/fr/providers/alibaba" icon="cloud">
    Fournisseur ModelStudio hérité et notes de migration.
  </Card>
  <Card title="Troubleshooting" href="/fr/help/troubleshooting" icon="wrench">
    Dépannage général et FAQ.
  </Card>
</CardGroup>
