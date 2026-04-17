---
read_when:
    - Vous voulez comprendre comment fonctionne la mémoire
    - Vous voulez savoir quels fichiers de mémoire écrire
summary: Comment OpenClaw se souvient des choses d’une session à l’autre
title: Vue d’ensemble de la mémoire
x-i18n:
    generated_at: "2026-04-15T14:40:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: ad1adafe1d81f1703d24f48a9c9da2b25a0ebbd4aad4f65d8bde5df78195d55b
    source_path: concepts/memory.md
    workflow: 15
---

# Vue d’ensemble de la mémoire

OpenClaw se souvient des choses en écrivant des **fichiers Markdown simples** dans l’espace de travail de votre agent. Le modèle ne « se souvient » que de ce qui est enregistré sur le disque — il n’y a pas d’état caché.

## Fonctionnement

Votre agent dispose de trois fichiers liés à la mémoire :

- **`MEMORY.md`** — mémoire à long terme. Faits durables, préférences et décisions. Chargé au début de chaque session de message privé.
- **`memory/YYYY-MM-DD.md`** — notes quotidiennes. Contexte courant et observations. Les notes d’aujourd’hui et d’hier sont chargées automatiquement.
- **`DREAMS.md`** (optionnel) — journal des rêves et résumés des phases de Dreaming pour relecture humaine, y compris les entrées de remplissage rétrospectif ancrées dans l’historique.

Ces fichiers se trouvent dans l’espace de travail de l’agent (par défaut `~/.openclaw/workspace`).

<Tip>
Si vous voulez que votre agent se souvienne de quelque chose, demandez-le-lui simplement : « Souviens-toi que je préfère TypeScript. » Il l’écrira dans le fichier approprié.
</Tip>

## Outils de mémoire

L’agent dispose de deux outils pour travailler avec la mémoire :

- **`memory_search`** — trouve des notes pertinentes à l’aide de la recherche sémantique, même lorsque la formulation diffère de l’original.
- **`memory_get`** — lit un fichier de mémoire spécifique ou une plage de lignes.

Ces deux outils sont fournis par le Plugin de mémoire actif (par défaut : `memory-core`).

## Plugin compagnon Memory Wiki

Si vous voulez que la mémoire durable se comporte davantage comme une base de connaissances maintenue que comme de simples notes brutes, utilisez le Plugin intégré `memory-wiki`.

`memory-wiki` compile les connaissances durables dans un coffre wiki avec :

- une structure de pages déterministe
- des affirmations et preuves structurées
- le suivi des contradictions et de la fraîcheur
- des tableaux de bord générés
- des condensés compilés pour les consommateurs agent/runtime
- des outils natifs du wiki comme `wiki_search`, `wiki_get`, `wiki_apply` et `wiki_lint`

Il ne remplace pas le Plugin de mémoire actif. Le Plugin de mémoire actif reste responsable du rappel, de la promotion et de Dreaming. `memory-wiki` ajoute à côté une couche de connaissances riche en provenance.

Voir [Memory Wiki](/fr/plugins/memory-wiki).

## Recherche mémoire

Lorsqu’un fournisseur d’embeddings est configuré, `memory_search` utilise une **recherche hybride** — en combinant similarité vectorielle (sens sémantique) et correspondance par mots-clés (termes exacts comme les ID et les symboles de code). Cela fonctionne immédiatement dès que vous avez une clé API pour n’importe quel fournisseur pris en charge.

<Info>
OpenClaw détecte automatiquement votre fournisseur d’embeddings à partir des clés API disponibles. Si vous avez configuré une clé OpenAI, Gemini, Voyage ou Mistral, la recherche mémoire est activée automatiquement.
</Info>

Pour plus de détails sur le fonctionnement de la recherche, les options de réglage et la configuration du fournisseur, voir [Memory Search](/fr/concepts/memory-search).

## Backends mémoire

<CardGroup cols={3}>
<Card title="Intégré (par défaut)" icon="database" href="/fr/concepts/memory-builtin">
Basé sur SQLite. Fonctionne immédiatement avec la recherche par mots-clés, la similarité vectorielle et la recherche hybride. Aucune dépendance supplémentaire.
</Card>
<Card title="QMD" icon="search" href="/fr/concepts/memory-qmd">
Sidecar local-first avec reranking, expansion de requête et possibilité d’indexer des répertoires en dehors de l’espace de travail.
</Card>
<Card title="Honcho" icon="brain" href="/fr/concepts/memory-honcho">
Mémoire intersession native IA avec modélisation utilisateur, recherche sémantique et conscience multi-agent. Installation par Plugin.
</Card>
</CardGroup>

## Couche wiki de connaissances

<CardGroup cols={1}>
<Card title="Memory Wiki" icon="book" href="/fr/plugins/memory-wiki">
Compile la mémoire durable dans un coffre wiki riche en provenance avec affirmations, tableaux de bord, mode bridge et workflows compatibles avec Obsidian.
</Card>
</CardGroup>

## Vidage automatique de la mémoire

Avant que la [Compaction](/fr/concepts/compaction) ne résume votre conversation, OpenClaw exécute un tour silencieux qui rappelle à l’agent d’enregistrer le contexte important dans les fichiers de mémoire. Cette fonctionnalité est activée par défaut — vous n’avez rien à configurer.

<Tip>
Le vidage de la mémoire évite la perte de contexte pendant la compaction. Si votre agent a dans la conversation des faits importants qui ne sont pas encore écrits dans un fichier, ils seront enregistrés automatiquement avant que le résumé n’ait lieu.
</Tip>

## Dreaming

Dreaming est une passe optionnelle de consolidation en arrière-plan pour la mémoire. Elle collecte les signaux à court terme, évalue les candidats et ne promeut dans la mémoire à long terme (`MEMORY.md`) que les éléments qualifiés.

Elle est conçue pour maintenir un signal élevé dans la mémoire à long terme :

- **Opt-in** : désactivée par défaut.
- **Planifiée** : lorsqu’elle est activée, `memory-core` gère automatiquement une tâche Cron récurrente pour une phase complète de Dreaming.
- **À seuil** : les promotions doivent franchir des seuils de score, de fréquence de rappel et de diversité des requêtes.
- **Révisable** : les résumés de phase et les entrées du journal sont écrits dans `DREAMS.md` pour relecture humaine.

Pour le comportement des phases, les signaux de score et les détails du journal des rêves, voir [Dreaming](/fr/concepts/dreaming).

## Remplissage rétrospectif ancré dans l’historique et promotion en direct

Le système de Dreaming dispose désormais de deux voies de relecture étroitement liées :

- **Le Dreaming en direct** fonctionne à partir du magasin de Dreaming à court terme situé dans `memory/.dreams/` et correspond à ce que la phase profonde normale utilise pour décider de ce qui peut être promu dans `MEMORY.md`.
- **Le remplissage rétrospectif ancré dans l’historique** lit les anciennes notes `memory/YYYY-MM-DD.md` comme des fichiers journaliers autonomes et écrit une sortie de relecture structurée dans `DREAMS.md`.

Le remplissage rétrospectif ancré dans l’historique est utile lorsque vous voulez rejouer d’anciennes notes et examiner ce que le système considère comme durable sans modifier manuellement `MEMORY.md`.

Quand vous utilisez :

```bash
openclaw memory rem-backfill --path ./memory --stage-short-term
```

les candidats durables ancrés dans l’historique ne sont pas promus directement. Ils sont placés dans le même magasin de Dreaming à court terme que celui déjà utilisé par la phase profonde normale. Cela signifie que :

- `DREAMS.md` reste la surface de relecture humaine.
- le magasin à court terme reste la surface de classement orientée machine.
- `MEMORY.md` n’est toujours écrit que par la promotion profonde.

Si vous décidez que la relecture n’était pas utile, vous pouvez supprimer les artefacts mis en attente sans toucher aux entrées ordinaires du journal ni à l’état normal de rappel :

```bash
openclaw memory rem-backfill --rollback
openclaw memory rem-backfill --rollback-short-term
```

## CLI

```bash
openclaw memory status          # Vérifier l’état de l’index et le fournisseur
openclaw memory search "query"  # Rechercher depuis la ligne de commande
openclaw memory index --force   # Reconstruire l’index
```

## Pour aller plus loin

- [Builtin Memory Engine](/fr/concepts/memory-builtin) — backend SQLite par défaut
- [QMD Memory Engine](/fr/concepts/memory-qmd) — sidecar avancé local-first
- [Honcho Memory](/fr/concepts/memory-honcho) — mémoire intersession native IA
- [Memory Wiki](/fr/plugins/memory-wiki) — coffre de connaissances compilé et outils natifs du wiki
- [Memory Search](/fr/concepts/memory-search) — pipeline de recherche, fournisseurs et réglages
- [Dreaming](/fr/concepts/dreaming) — promotion en arrière-plan
  du rappel à court terme vers la mémoire à long terme
- [Référence de configuration de la mémoire](/fr/reference/memory-config) — tous les paramètres de configuration
- [Compaction](/fr/concepts/compaction) — comment la compaction interagit avec la mémoire
