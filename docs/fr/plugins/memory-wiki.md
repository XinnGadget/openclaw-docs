---
read_when:
    - Vous souhaitez des connaissances persistantes au-delà de simples notes `MEMORY.md`
    - Vous configurez le Plugin memory-wiki intégré
    - Vous souhaitez comprendre `wiki_search`, `wiki_get` ou le mode bridge
summary: 'memory-wiki : coffre de connaissances compilé avec provenance, assertions, tableaux de bord et mode bridge'
title: Wiki mémoire
x-i18n:
    generated_at: "2026-04-12T23:28:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: 44d168a7096f744c56566ecac57499192eb101b4dd8a78e1b92f3aa0d6da3ad1
    source_path: plugins/memory-wiki.md
    workflow: 15
---

# Wiki mémoire

`memory-wiki` est un Plugin intégré qui transforme la mémoire durable en un
coffre de connaissances compilé.

Il **ne** remplace **pas** le Plugin Active Memory. Le Plugin de mémoire active continue
de gérer le rappel, la promotion, l’indexation et Dreaming. `memory-wiki` se place à ses côtés
et compile les connaissances durables dans un wiki navigable avec des pages déterministes,
des assertions structurées, de la provenance, des tableaux de bord et des résumés lisibles par machine.

Utilisez-le lorsque vous voulez que la mémoire se comporte davantage comme une couche de connaissances entretenue
et moins comme un empilement de fichiers Markdown.

## Ce qu’il ajoute

- Un coffre wiki dédié avec une disposition de page déterministe
- Des métadonnées structurées d’assertions et de preuves, pas seulement du texte
- La provenance, la confiance, les contradictions et les questions ouvertes au niveau des pages
- Des résumés compilés pour les consommateurs agent/runtime
- Des outils natifs au wiki pour search/get/apply/lint
- Un mode bridge facultatif qui importe les artefacts publics du Plugin de mémoire active
- Un mode de rendu compatible Obsidian facultatif et une intégration CLI

## Comment il s’intègre à la mémoire

Considérez la séparation ainsi :

| Couche                                                  | Gère                                                                                      |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Plugin Active Memory (`memory-core`, QMD, Honcho, etc.) | Rappel, recherche sémantique, promotion, Dreaming, runtime de la mémoire                  |
| `memory-wiki`                                           | Pages wiki compilées, synthèses riches en provenance, tableaux de bord, search/get/apply spécifiques au wiki |

Si le Plugin Active Memory expose des artefacts de rappel partagés, OpenClaw peut rechercher
dans les deux couches en un seul passage avec `memory_search corpus=all`.

Lorsque vous avez besoin d’un classement spécifique au wiki, de provenance ou d’un accès direct aux pages, utilisez plutôt les outils natifs au wiki.

## Modèle hybride recommandé

Une configuration par défaut solide pour les installations local-first est :

- QMD comme backend Active Memory pour le rappel et la recherche sémantique large
- `memory-wiki` en mode `bridge` pour des pages de connaissances synthétisées durables

Cette séparation fonctionne bien parce que chaque couche reste concentrée :

- QMD garde les notes brutes, les exports de session et les collections supplémentaires consultables
- `memory-wiki` compile les entités stables, les assertions, les tableaux de bord et les pages source

Règle pratique :

- utilisez `memory_search` lorsque vous voulez un passage large de rappel sur la mémoire
- utilisez `wiki_search` et `wiki_get` lorsque vous voulez des résultats wiki sensibles à la provenance
- utilisez `memory_search corpus=all` lorsque vous voulez qu’une recherche partagée couvre les deux couches

Si le mode bridge signale zéro artefact exporté, cela signifie que le Plugin Active Memory
n’expose pas encore d’entrées bridge publiques. Exécutez d’abord `openclaw wiki doctor`,
puis confirmez que le Plugin Active Memory prend en charge les artefacts publics.

## Modes de coffre

`memory-wiki` prend en charge trois modes de coffre :

### `isolated`

Coffre propre, sources propres, sans dépendance à `memory-core`.

Utilisez ce mode lorsque vous voulez que le wiki soit son propre magasin de connaissances organisé.

### `bridge`

Lit les artefacts mémoire publics et les événements mémoire depuis le Plugin Active Memory
via les jonctions publiques du Plugin SDK.

Utilisez ce mode lorsque vous voulez que le wiki compile et organise les
artefacts exportés du Plugin mémoire sans accéder aux éléments internes privés du Plugin.

Le mode bridge peut indexer :

- les artefacts mémoire exportés
- les rapports de rêve
- les notes quotidiennes
- les fichiers racine mémoire
- les journaux d’événements mémoire

### `unsafe-local`

Échappatoire explicite sur la même machine pour les chemins privés locaux.

Ce mode est volontairement expérimental et non portable. Utilisez-le uniquement si vous
comprenez la frontière de confiance et avez spécifiquement besoin d’un accès au système de fichiers local
que le mode bridge ne peut pas fournir.

## Disposition du coffre

Le Plugin initialise un coffre comme suit :

```text
<vault>/
  AGENTS.md
  WIKI.md
  index.md
  inbox.md
  entities/
  concepts/
  syntheses/
  sources/
  reports/
  _attachments/
  _views/
  .openclaw-wiki/
```

Le contenu géré reste à l’intérieur des blocs générés. Les blocs de notes humaines sont préservés.

Les principaux groupes de pages sont :

- `sources/` pour le matériau brut importé et les pages adossées au bridge
- `entities/` pour les choses, personnes, systèmes, projets et objets durables
- `concepts/` pour les idées, abstractions, modèles et politiques
- `syntheses/` pour les résumés compilés et les consolidations entretenues
- `reports/` pour les tableaux de bord générés

## Assertions structurées et preuves

Les pages peuvent contenir des `claims` en frontmatter structurés, pas seulement du texte libre.

Chaque assertion peut inclure :

- `id`
- `text`
- `status`
- `confidence`
- `evidence[]`
- `updatedAt`

Les entrées de preuve peuvent inclure :

- `sourceId`
- `path`
- `lines`
- `weight`
- `note`
- `updatedAt`

C’est ce qui fait agir le wiki davantage comme une couche de croyances que comme un simple
dépôt passif de notes. Les assertions peuvent être suivies, évaluées, contestées et rattachées aux sources.

## Pipeline de compilation

L’étape de compilation lit les pages du wiki, normalise les résumés et émet des
artefacts stables orientés machine sous :

- `.openclaw-wiki/cache/agent-digest.json`
- `.openclaw-wiki/cache/claims.jsonl`

Ces résumés existent afin que les agents et le code runtime n’aient pas à analyser les pages Markdown.

La sortie compilée alimente également :

- l’indexation wiki de premier passage pour les flux search/get
- la recherche d’id d’assertion jusqu’à la page propriétaire
- des compléments d’invite compacts
- la génération de rapports/tableaux de bord

## Tableaux de bord et rapports de santé

Lorsque `render.createDashboards` est activé, la compilation entretient des tableaux de bord sous `reports/`.

Les rapports intégrés incluent :

- `reports/open-questions.md`
- `reports/contradictions.md`
- `reports/low-confidence.md`
- `reports/claim-health.md`
- `reports/stale-pages.md`

Ces rapports suivent des éléments comme :

- des groupes de notes de contradiction
- des groupes d’assertions concurrentes
- des assertions sans preuve structurée
- des pages et assertions à faible confiance
- des données obsolètes ou à fraîcheur inconnue
- des pages avec des questions non résolues

## Recherche et récupération

`memory-wiki` prend en charge deux backends de recherche :

- `shared` : utiliser le flux de recherche mémoire partagé lorsque disponible
- `local` : rechercher le wiki localement

Il prend également en charge trois corpus :

- `wiki`
- `memory`
- `all`

Comportement important :

- `wiki_search` et `wiki_get` utilisent les résumés compilés comme premier passage lorsque possible
- les id d’assertion peuvent être résolus jusqu’à la page propriétaire
- les assertions contestées/obsolètes/récentes influencent le classement
- les étiquettes de provenance peuvent être conservées dans les résultats

Règle pratique :

- utilisez `memory_search corpus=all` pour un passage large unique de rappel
- utilisez `wiki_search` + `wiki_get` lorsque vous vous souciez du classement spécifique au wiki,
  de la provenance ou de la structure de croyances au niveau des pages

## Outils agent

Le Plugin enregistre ces outils :

- `wiki_status`
- `wiki_search`
- `wiki_get`
- `wiki_apply`
- `wiki_lint`

Leur rôle :

- `wiki_status` : mode de coffre actuel, santé, disponibilité de la CLI Obsidian
- `wiki_search` : rechercher dans les pages wiki et, lorsqu’il est configuré, dans les corpus mémoire partagés
- `wiki_get` : lire une page wiki par id/chemin ou se replier sur le corpus mémoire partagé
- `wiki_apply` : mutations ciblées de synthèse/métadonnées sans chirurgie libre de page
- `wiki_lint` : vérifications structurelles, lacunes de provenance, contradictions, questions ouvertes

Le Plugin enregistre également un complément de corpus mémoire non exclusif, de sorte que
`memory_search` et `memory_get` partagés peuvent atteindre le wiki lorsque le Plugin Active Memory prend en charge la sélection de corpus.

## Comportement des invites et du contexte

Lorsque `context.includeCompiledDigestPrompt` est activé, les sections d’invite mémoire
ajoutent un instantané compilé compact depuis `agent-digest.json`.

Cet instantané est volontairement petit et à fort signal :

- pages principales uniquement
- assertions principales uniquement
- nombre de contradictions
- nombre de questions
- qualificateurs de confiance/fraîcheur

Ceci est optionnel, car cela modifie la forme de l’invite et est principalement utile pour les moteurs de contexte
ou l’assemblage d’invite hérité qui consomment explicitement les compléments mémoire.

## Configuration

Placez la configuration sous `plugins.entries.memory-wiki.config` :

```json5
{
  plugins: {
    entries: {
      "memory-wiki": {
        enabled: true,
        config: {
          vaultMode: "isolated",
          vault: {
            path: "~/.openclaw/wiki/main",
            renderMode: "obsidian",
          },
          obsidian: {
            enabled: true,
            useOfficialCli: true,
            vaultName: "OpenClaw Wiki",
            openAfterWrites: false,
          },
          bridge: {
            enabled: false,
            readMemoryArtifacts: true,
            indexDreamReports: true,
            indexDailyNotes: true,
            indexMemoryRoot: true,
            followMemoryEvents: true,
          },
          ingest: {
            autoCompile: true,
            maxConcurrentJobs: 1,
            allowUrlIngest: true,
          },
          search: {
            backend: "shared",
            corpus: "wiki",
          },
          context: {
            includeCompiledDigestPrompt: false,
          },
          render: {
            preserveHumanBlocks: true,
            createBacklinks: true,
            createDashboards: true,
          },
        },
      },
    },
  },
}
```

Principaux réglages :

- `vaultMode` : `isolated`, `bridge`, `unsafe-local`
- `vault.renderMode` : `native` ou `obsidian`
- `bridge.readMemoryArtifacts` : importer les artefacts publics du Plugin Active Memory
- `bridge.followMemoryEvents` : inclure les journaux d’événements en mode bridge
- `search.backend` : `shared` ou `local`
- `search.corpus` : `wiki`, `memory` ou `all`
- `context.includeCompiledDigestPrompt` : ajouter un instantané compact du résumé aux sections d’invite mémoire
- `render.createBacklinks` : générer des blocs liés déterministes
- `render.createDashboards` : générer des pages de tableau de bord

### Exemple : QMD + mode bridge

Utilisez ceci lorsque vous voulez QMD pour le rappel et `memory-wiki` pour une
couche de connaissances entretenue :

```json5
{
  memory: {
    backend: "qmd",
      "memory-wiki": {
        enabled: true,
        config: {
          vaultMode: "bridge",
          bridge: {
            enabled: true,
            readMemoryArtifacts: true,
            indexDreamReports: true,
            indexDailyNotes: true,
            indexMemoryRoot: true,
            followMemoryEvents: true,
          },
          search: {
            backend: "shared",
            corpus: "all",
          },
          context: {
            includeCompiledDigestPrompt: false,
          },
        },
      },
    },
  },
}
```

Cela permet de garder :

- QMD chargé du rappel de la mémoire active
- `memory-wiki` concentré sur les pages compilées et les tableaux de bord
- une forme d’invite inchangée jusqu’à ce que vous activiez intentionnellement les invites de résumé compilé

## CLI

`memory-wiki` expose également une surface CLI de premier niveau :

```bash
openclaw wiki status
openclaw wiki doctor
openclaw wiki init
openclaw wiki ingest ./notes/alpha.md
openclaw wiki compile
openclaw wiki lint
openclaw wiki search "alpha"
openclaw wiki get entity.alpha
openclaw wiki apply synthesis "Alpha Summary" --body "..." --source-id source.alpha
openclaw wiki bridge import
openclaw wiki obsidian status
```

Voir [CLI: wiki](/cli/wiki) pour la référence de commande complète.

## Prise en charge d’Obsidian

Lorsque `vault.renderMode` vaut `obsidian`, le Plugin écrit du
Markdown compatible Obsidian et peut facultativement utiliser la CLI officielle `obsidian`.

Les flux pris en charge incluent :

- vérification de statut
- recherche dans le coffre
- ouverture d’une page
- invocation d’une commande Obsidian
- saut vers la note quotidienne

Ceci est facultatif. Le wiki continue de fonctionner en mode natif sans Obsidian.

## Workflow recommandé

1. Conservez votre Plugin Active Memory pour recall/promotion/Dreaming.
2. Activez `memory-wiki`.
3. Commencez avec le mode `isolated`, sauf si vous voulez explicitement le mode bridge.
4. Utilisez `wiki_search` / `wiki_get` lorsque la provenance est importante.
5. Utilisez `wiki_apply` pour des synthèses ciblées ou des mises à jour de métadonnées.
6. Exécutez `wiki_lint` après des modifications importantes.
7. Activez les tableaux de bord si vous voulez de la visibilité sur les éléments obsolètes/les contradictions.

## Documentation associée

- [Memory Overview](/fr/concepts/memory)
- [CLI: memory](/cli/memory)
- [CLI: wiki](/cli/wiki)
- [Plugin SDK overview](/fr/plugins/sdk-overview)
