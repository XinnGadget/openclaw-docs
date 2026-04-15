---
read_when:
    - Vous voyez une clé de configuration `.experimental` et vous voulez savoir si elle est stable.
    - Vous voulez essayer des fonctionnalités d’exécution en préversion sans les confondre avec les valeurs par défaut normales.
    - Vous voulez un endroit unique pour trouver les indicateurs expérimentaux actuellement documentés.
summary: Que signifient les indicateurs expérimentaux dans OpenClaw et lesquels sont actuellement documentés ?
title: Fonctionnalités expérimentales
x-i18n:
    generated_at: "2026-04-15T14:40:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2d1c7b3d4cd56ef8a0bdab1deb9918e9b2c9a33f956d63193246087f8633dcf3
    source_path: concepts/experimental-features.md
    workflow: 15
---

# Fonctionnalités expérimentales

Les fonctionnalités expérimentales dans OpenClaw sont des **surfaces de préversion activées explicitement**. Elles sont
placées derrière des indicateurs explicites parce qu’elles ont encore besoin d’une utilisation réelle avant de
mériter une valeur par défaut stable ou un contrat public durable.

Traitez-les différemment d’une configuration normale :

- Laissez-les **désactivées par défaut** à moins que la documentation associée ne vous dise d’en essayer une.
- Attendez-vous à ce que leur **structure et leur comportement changent** plus rapidement que pour une configuration stable.
- Privilégiez d’abord la voie stable lorsqu’elle existe déjà.
- Si vous déployez OpenClaw à grande échelle, testez les indicateurs expérimentaux dans un environnement plus restreint
  avant de les intégrer dans une base de référence partagée.

## Indicateurs actuellement documentés

| Surface                  | Key                                                       | Use it when                                                                                                    | More                                                                                          |
| ------------------------ | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Environnement d’exécution des modèles locaux | `agents.defaults.experimental.localModelLean`             | Un backend local plus petit ou plus strict a du mal avec la surface complète des outils par défaut d’OpenClaw | [Modèles locaux](/fr/gateway/local-models)                                                       |
| Recherche en mémoire     | `agents.defaults.memorySearch.experimental.sessionMemory` | Vous voulez que `memory_search` indexe les transcriptions des sessions précédentes et acceptez le coût supplémentaire de stockage et d’indexation | [Référence de configuration de la mémoire](/fr/reference/memory-config#session-memory-search-experimental) |
| Outil de planification structurée | `tools.experimental.planTool`                             | Vous voulez que l’outil structuré `update_plan` soit exposé pour le suivi de travaux en plusieurs étapes dans les environnements d’exécution et interfaces compatibles | [Référence de configuration de la Gateway](/fr/gateway/configuration-reference#toolsexperimental) |

## Mode allégé pour modèles locaux

`agents.defaults.experimental.localModelLean: true` est une soupape de sécurité
pour les configurations de modèles locaux plus faibles. Il réduit les outils par défaut lourds comme
`browser`, `cron` et `message` afin que la structure du prompt soit plus petite et moins fragile
pour les backends compatibles OpenAI à petit contexte ou plus stricts.

Ce n’est intentionnellement **pas** la voie normale. Si votre backend gère correctement l’environnement d’exécution
complet, laissez cette option désactivée.

## Expérimental ne veut pas dire caché

Si une fonctionnalité est expérimentale, OpenClaw doit l’indiquer clairement dans la documentation et dans le
chemin de configuration lui-même. En revanche, il ne doit **pas** glisser un comportement de préversion dans un
paramètre qui semble stable et prétendre que c’est normal. C’est comme ça que les surfaces de configuration
deviennent désordonnées.
