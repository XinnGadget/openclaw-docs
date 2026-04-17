---
read_when:
    - Vous souhaitez configurer QMD comme backend de mémoire
    - Vous souhaitez des fonctionnalités de mémoire avancées comme le reranking ou des chemins indexés supplémentaires
summary: Sidecar de recherche local-first avec BM25, vecteurs, reranking et expansion de requête
title: Moteur de mémoire QMD
x-i18n:
    generated_at: "2026-04-12T23:28:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: 27afc996b959d71caed964a3cae437e0e29721728b30ebe7f014db124c88da04
    source_path: concepts/memory-qmd.md
    workflow: 15
---

# Moteur de mémoire QMD

[QMD](https://github.com/tobi/qmd) est un sidecar de recherche local-first qui s'exécute
aux côtés d'OpenClaw. Il combine BM25, la recherche vectorielle et le reranking dans un seul
binaire, et peut indexer du contenu au-delà des fichiers de mémoire de votre espace de travail.

## Ce qu'il ajoute par rapport au moteur intégré

- **Reranking et expansion de requête** pour une meilleure couverture.
- **Indexer des répertoires supplémentaires** -- documentation de projet, notes d'équipe, tout ce qui se trouve sur le disque.
- **Indexer les transcriptions de session** -- pour retrouver des conversations antérieures.
- **Entièrement local** -- fonctionne via Bun + node-llama-cpp, télécharge automatiquement les modèles GGUF.
- **Repli automatique** -- si QMD n'est pas disponible, OpenClaw revient au
  moteur intégré de manière transparente.

## Prise en main

### Prérequis

- Installer QMD : `npm install -g @tobilu/qmd` ou `bun install -g @tobilu/qmd`
- Une version de SQLite qui autorise les extensions (`brew install sqlite` sur macOS).
- QMD doit être présent dans le `PATH` de la passerelle.
- macOS et Linux fonctionnent immédiatement. Windows est mieux pris en charge via WSL2.

### Activer

```json5
{
  memory: {
    backend: "qmd",
  },
}
```

OpenClaw crée un répertoire personnel QMD autonome sous
`~/.openclaw/agents/<agentId>/qmd/` et gère automatiquement le cycle de vie du sidecar
-- les collections, les mises à jour et les exécutions d'embedding sont gérées pour vous.
Il privilégie les formes actuelles de collection QMD et de requête MCP, mais revient toujours à
l'ancien indicateur de collection `--mask` et aux anciens noms d'outils MCP si nécessaire.

## Fonctionnement du sidecar

- OpenClaw crée des collections à partir des fichiers de mémoire de votre espace de travail et de tous les
  `memory.qmd.paths` configurés, puis exécute `qmd update` + `qmd embed` au démarrage
  et périodiquement (par défaut toutes les 5 minutes).
- La collection d'espace de travail par défaut suit `MEMORY.md` ainsi que l'arborescence `memory/`.
  `memory.md` en minuscules reste une solution de secours d'amorçage, pas une collection QMD distincte.
- L'actualisation au démarrage s'exécute en arrière-plan afin de ne pas bloquer le démarrage du chat.
- Les recherches utilisent le `searchMode` configuré (par défaut : `search` ; prend aussi en charge
  `vsearch` et `query`). Si un mode échoue, OpenClaw réessaie avec `qmd query`.
- Si QMD échoue complètement, OpenClaw revient au moteur SQLite intégré.

<Info>
La première recherche peut être lente -- QMD télécharge automatiquement des modèles GGUF (~2 Go) pour le
reranking et l'expansion de requête lors de la première exécution de `qmd query`.
</Info>

## Remplacement des modèles

Les variables d'environnement des modèles QMD sont transmises inchangées depuis le processus de la passerelle,
vous pouvez donc ajuster QMD globalement sans ajouter de nouvelle configuration OpenClaw :

```bash
export QMD_EMBED_MODEL="hf:Qwen/Qwen3-Embedding-0.6B-GGUF/Qwen3-Embedding-0.6B-Q8_0.gguf"
export QMD_RERANK_MODEL="/absolute/path/to/reranker.gguf"
export QMD_GENERATE_MODEL="/absolute/path/to/generator.gguf"
```

Après avoir changé le modèle d'embedding, relancez les embeddings afin que l'index corresponde au
nouvel espace vectoriel.

## Indexation de chemins supplémentaires

Faites pointer QMD vers des répertoires supplémentaires pour les rendre interrogeables :

```json5
{
  memory: {
    backend: "qmd",
    qmd: {
      paths: [{ name: "docs", path: "~/notes", pattern: "**/*.md" }],
    },
  },
}
```

Les extraits issus de chemins supplémentaires apparaissent sous la forme `qmd/<collection>/<relative-path>` dans
les résultats de recherche. `memory_get` comprend ce préfixe et lit depuis la racine de collection correcte.

## Indexation des transcriptions de session

Activez l'indexation des sessions pour retrouver des conversations antérieures :

```json5
{
  memory: {
    backend: "qmd",
    qmd: {
      sessions: { enabled: true },
    },
  },
}
```

Les transcriptions sont exportées sous forme de tours User/Assistant nettoyés dans une collection QMD dédiée
sous `~/.openclaw/agents/<id>/qmd/sessions/`.

## Portée de recherche

Par défaut, les résultats de recherche QMD sont affichés dans les sessions directes et de canal
(pas dans les groupes). Configurez `memory.qmd.scope` pour modifier cela :

```json5
{
  memory: {
    qmd: {
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }],
      },
    },
  },
}
```

Lorsque la portée refuse une recherche, OpenClaw journalise un avertissement avec le canal dérivé et
le type de chat afin que les résultats vides soient plus faciles à diagnostiquer.

## Citations

Quand `memory.citations` vaut `auto` ou `on`, les extraits de recherche incluent un pied de page
`Source: <path#line>`. Définissez `memory.citations = "off"` pour omettre le pied de page
tout en transmettant le chemin à l'agent en interne.

## Quand l'utiliser

Choisissez QMD lorsque vous avez besoin :

- Du reranking pour des résultats de meilleure qualité.
- De rechercher dans la documentation du projet ou des notes en dehors de l'espace de travail.
- De retrouver des conversations de sessions passées.
- D'une recherche entièrement locale sans clés d'API.

Pour les configurations plus simples, le [moteur intégré](/fr/concepts/memory-builtin) fonctionne bien
sans dépendances supplémentaires.

## Dépannage

**QMD introuvable ?** Assurez-vous que le binaire est présent dans le `PATH` de la passerelle. Si OpenClaw
s'exécute comme service, créez un lien symbolique :
`sudo ln -s ~/.bun/bin/qmd /usr/local/bin/qmd`.

**Première recherche très lente ?** QMD télécharge les modèles GGUF lors de la première utilisation. Préchauffez-le
avec `qmd query "test"` en utilisant les mêmes répertoires XDG que ceux utilisés par OpenClaw.

**La recherche expire ?** Augmentez `memory.qmd.limits.timeoutMs` (valeur par défaut : 4000ms).
Définissez-la à `120000` pour du matériel plus lent.

**Résultats vides dans les discussions de groupe ?** Vérifiez `memory.qmd.scope` -- par défaut, il
autorise uniquement les sessions directes et de canal.

**Des dépôts temporaires visibles depuis l'espace de travail provoquent `ENAMETOOLONG` ou une indexation défaillante ?**
Le parcours QMD suit actuellement le comportement du scanner QMD sous-jacent plutôt que
les règles de liens symboliques du moteur intégré d'OpenClaw. Conservez les extractions temporaires de monorepo dans
des répertoires cachés comme `.tmp/` ou en dehors des racines QMD indexées jusqu'à ce que QMD expose
un parcours sûr face aux cycles ou des contrôles d'exclusion explicites.

## Configuration

Pour la surface de configuration complète (`memory.qmd.*`), les modes de recherche, les intervalles de mise à jour,
les règles de portée et tous les autres réglages, consultez la
[référence de configuration de la mémoire](/fr/reference/memory-config).
