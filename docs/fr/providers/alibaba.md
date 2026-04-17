---
read_when:
    - Vous voulez utiliser la génération vidéo Wan d’Alibaba dans OpenClaw
    - Vous avez besoin d’une configuration de clé API Model Studio ou DashScope pour la génération vidéo
summary: Génération vidéo Wan d’Alibaba Model Studio dans OpenClaw
title: Alibaba Model Studio
x-i18n:
    generated_at: "2026-04-12T23:28:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: a6e97d929952cdba7740f5ab3f6d85c18286b05596a4137bf80bbc8b54f32662
    source_path: providers/alibaba.md
    workflow: 15
---

# Alibaba Model Studio

OpenClaw inclut un fournisseur groupé de génération vidéo `alibaba` pour les modèles Wan sur Alibaba Model Studio / DashScope.

- Fournisseur : `alibaba`
- Authentification préférée : `MODELSTUDIO_API_KEY`
- Également acceptées : `DASHSCOPE_API_KEY`, `QWEN_API_KEY`
- API : génération vidéo asynchrone DashScope / Model Studio

## Démarrage

<Steps>
  <Step title="Définir une clé API">
    ```bash
    openclaw onboard --auth-choice qwen-standard-api-key
    ```
  </Step>
  <Step title="Définir un modèle vidéo par défaut">
    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "alibaba/wan2.6-t2v",
          },
        },
      },
    }
    ```
  </Step>
  <Step title="Vérifier que le fournisseur est disponible">
    ```bash
    openclaw models list --provider alibaba
    ```
  </Step>
</Steps>

<Note>
N’importe laquelle des clés d’authentification acceptées (`MODELSTUDIO_API_KEY`, `DASHSCOPE_API_KEY`, `QWEN_API_KEY`) fonctionnera. L’option d’onboarding `qwen-standard-api-key` configure l’identifiant DashScope partagé.
</Note>

## Modèles Wan intégrés

Le fournisseur groupé `alibaba` enregistre actuellement :

| Référence du modèle      | Mode                         |
| ------------------------ | ---------------------------- |
| `alibaba/wan2.6-t2v`     | Texte vers vidéo             |
| `alibaba/wan2.6-i2v`     | Image vers vidéo             |
| `alibaba/wan2.6-r2v`     | Référence vers vidéo         |
| `alibaba/wan2.6-r2v-flash` | Référence vers vidéo (rapide) |
| `alibaba/wan2.7-r2v`     | Référence vers vidéo         |

## Limites actuelles

| Paramètre               | Limite                                                    |
| ----------------------- | --------------------------------------------------------- |
| Vidéos de sortie        | Jusqu’à **1** par requête                                 |
| Images d’entrée         | Jusqu’à **1**                                             |
| Vidéos d’entrée         | Jusqu’à **4**                                             |
| Durée                   | Jusqu’à **10 secondes**                                   |
| Contrôles pris en charge | `size`, `aspectRatio`, `resolution`, `audio`, `watermark` |
| Image/vidéo de référence | URLs `http(s)` distantes uniquement                       |

<Warning>
Le mode image/vidéo de référence exige actuellement des **URLs distantes http(s)**. Les chemins de fichiers locaux ne sont pas pris en charge pour les entrées de référence.
</Warning>

## Configuration avancée

<AccordionGroup>
  <Accordion title="Relation avec Qwen">
    Le fournisseur groupé `qwen` utilise également des points de terminaison DashScope hébergés par Alibaba pour la génération vidéo Wan. Utilisez :

    - `qwen/...` lorsque vous voulez la surface canonique du fournisseur Qwen
    - `alibaba/...` lorsque vous voulez la surface vidéo Wan directe détenue par le fournisseur

    Consultez la [documentation du fournisseur Qwen](/fr/providers/qwen) pour plus de détails.

  </Accordion>

  <Accordion title="Priorité des clés d’authentification">
    OpenClaw vérifie les clés d’authentification dans cet ordre :

    1. `MODELSTUDIO_API_KEY` (préférée)
    2. `DASHSCOPE_API_KEY`
    3. `QWEN_API_KEY`

    N’importe laquelle de ces clés authentifiera le fournisseur `alibaba`.

  </Accordion>
</AccordionGroup>

## Liens associés

<CardGroup cols={2}>
  <Card title="Génération vidéo" href="/fr/tools/video-generation" icon="video">
    Paramètres partagés de l’outil vidéo et sélection du fournisseur.
  </Card>
  <Card title="Qwen" href="/fr/providers/qwen" icon="microchip">
    Configuration du fournisseur Qwen et intégration DashScope.
  </Card>
  <Card title="Référence de configuration" href="/fr/gateway/configuration-reference#agent-defaults" icon="gear">
    Valeurs par défaut de l’agent et configuration des modèles.
  </Card>
</CardGroup>
