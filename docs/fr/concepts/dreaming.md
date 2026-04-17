---
read_when:
    - Vous souhaitez que la promotion de la mémoire s’exécute automatiquement
    - Vous souhaitez comprendre le rôle de chaque phase de Dreaming
    - Vous souhaitez ajuster la consolidation sans polluer `MEMORY.md`
summary: Consolidation de la mémoire en arrière-plan avec des phases légères, profondes et REM, ainsi qu’un journal des rêves
title: Dreaming
x-i18n:
    generated_at: "2026-04-15T14:40:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: a5bcaec80f62e7611ed533094ef1917bd72c885f57252824db910e1f0496adc6
    source_path: concepts/dreaming.md
    workflow: 15
---

# Dreaming

Dreaming est le système de consolidation de la mémoire en arrière-plan dans `memory-core`.
Il aide OpenClaw à déplacer les signaux forts de mémoire à court terme vers une mémoire durable tout en
gardant le processus explicable et révisable.

Dreaming est **optionnel** et désactivé par défaut.

## Ce que Dreaming écrit

Dreaming conserve deux types de sortie :

- **État machine** dans `memory/.dreams/` (magasin de rappel, signaux de phase, points de contrôle d’ingestion, verrous).
- **Sortie lisible par des humains** dans `DREAMS.md` (ou le `dreams.md` existant) et des fichiers de rapport de phase facultatifs sous `memory/dreaming/<phase>/YYYY-MM-DD.md`.

La promotion à long terme continue d’écrire uniquement dans `MEMORY.md`.

## Modèle de phase

Dreaming utilise trois phases coopératives :

| Phase | Objectif                                  | Écriture durable  |
| ----- | ----------------------------------------- | ----------------- |
| Light | Trier et préparer le contenu récent à court terme | Non               |
| Deep  | Évaluer et promouvoir les candidats durables      | Oui (`MEMORY.md`) |
| REM   | Réfléchir aux thèmes et aux idées récurrentes     | Non               |

Ces phases sont des détails d’implémentation internes, pas des « modes »
séparés configurés par l’utilisateur.

### Phase Light

La phase Light ingère les signaux récents de mémoire quotidienne et les traces de rappel, les déduplique,
et prépare des lignes candidates.

- Lit l’état de rappel à court terme, les fichiers récents de mémoire quotidienne et les transcriptions de session expurgées lorsque disponibles.
- Écrit un bloc géré `## Light Sleep` lorsque le stockage inclut une sortie en ligne.
- Enregistre des signaux de renforcement pour le classement Deep ultérieur.
- N’écrit jamais dans `MEMORY.md`.

### Phase Deep

La phase Deep décide de ce qui devient de la mémoire à long terme.

- Classe les candidats à l’aide d’un score pondéré et de seuils de validation.
- Exige que `minScore`, `minRecallCount` et `minUniqueQueries` soient atteints.
- Réhydrate les extraits à partir des fichiers quotidiens actifs avant l’écriture, afin que les extraits obsolètes/supprimés soient ignorés.
- Ajoute les entrées promues à `MEMORY.md`.
- Écrit un résumé `## Deep Sleep` dans `DREAMS.md` et peut éventuellement écrire `memory/dreaming/deep/YYYY-MM-DD.md`.

### Phase REM

La phase REM extrait des motifs et des signaux réflexifs.

- Construit des résumés de thèmes et de réflexions à partir de traces récentes à court terme.
- Écrit un bloc géré `## REM Sleep` lorsque le stockage inclut une sortie en ligne.
- Enregistre des signaux de renforcement REM utilisés par le classement Deep.
- N’écrit jamais dans `MEMORY.md`.

## Ingestion des transcriptions de session

Dreaming peut ingérer des transcriptions de session expurgées dans le corpus de Dreaming. Lorsque
des transcriptions sont disponibles, elles sont injectées dans la phase Light avec les signaux de mémoire quotidienne
et les traces de rappel. Le contenu personnel et sensible est expurgé
avant ingestion.

## Journal des rêves

Dreaming conserve également un **journal des rêves** narratif dans `DREAMS.md`.
Après que chaque phase dispose de suffisamment de matière, `memory-core` exécute un tour
de sous-agent en arrière-plan en mode best-effort (en utilisant le modèle d’exécution par défaut) et ajoute une courte entrée de journal.

Ce journal est destiné à la lecture humaine dans l’interface Dreams, pas à servir de source de promotion.
Les artefacts de journal/rapport générés par Dreaming sont exclus de la
promotion à court terme. Seuls les extraits de mémoire fondés peuvent être promus dans
`MEMORY.md`.

Il existe également une voie de remplissage historique fondée pour les travaux de révision et de récupération :

- `memory rem-harness --path ... --grounded` prévisualise une sortie de journal fondée à partir de notes historiques `YYYY-MM-DD.md`.
- `memory rem-backfill --path ...` écrit des entrées de journal fondées réversibles dans `DREAMS.md`.
- `memory rem-backfill --path ... --stage-short-term` prépare des candidats durables fondés dans le même magasin de preuves à court terme que celui déjà utilisé par la phase Deep normale.
- `memory rem-backfill --rollback` et `--rollback-short-term` suppriment ces artefacts de remplissage préparés sans toucher aux entrées de journal ordinaires ni au rappel actif à court terme.

L’interface Control expose le même flux de remplissage/réinitialisation du journal afin que vous puissiez inspecter
les résultats dans la scène Dreams avant de décider si les candidats fondés
méritent une promotion. La scène affiche également une voie fondée distincte pour que vous puissiez voir
quelles entrées préparées à court terme proviennent de la relecture historique, quels éléments promus
ont été guidés par du contenu fondé, et effacer uniquement les entrées préparées fondées
sans toucher à l’état ordinaire actif à court terme.

## Signaux de classement Deep

Le classement Deep utilise six signaux de base pondérés ainsi qu’un renforcement par phase :

| Signal              | Poids | Description                                       |
| ------------------- | ----- | ------------------------------------------------- |
| Fréquence           | 0.24  | Nombre de signaux à court terme accumulés par l’entrée |
| Pertinence          | 0.30  | Qualité moyenne de récupération pour l’entrée     |
| Diversité des requêtes | 0.15  | Contextes distincts de requête/jour qui l’ont fait émerger |
| Récence             | 0.15  | Score de fraîcheur décroissant avec le temps      |
| Consolidation       | 0.10  | Force de récurrence sur plusieurs jours           |
| Richesse conceptuelle | 0.06  | Densité des balises de concept à partir de l’extrait/du chemin |

Les occurrences des phases Light et REM ajoutent un faible bonus décroissant avec le temps à partir de
`memory/.dreams/phase-signals.json`.

## Planification

Lorsqu’il est activé, `memory-core` gère automatiquement une tâche Cron pour un balayage Dreaming complet. Chaque balayage exécute les phases dans l’ordre : light -> REM -> deep.

Comportement de cadence par défaut :

| Paramètre            | Par défaut |
| -------------------- | ---------- |
| `dreaming.frequency` | `0 3 * * *` |

## Démarrage rapide

Activer Dreaming :

```json
{
  "plugins": {
    "entries": {
      "memory-core": {
        "config": {
          "dreaming": {
            "enabled": true
          }
        }
      }
    }
  }
}
```

Activer Dreaming avec une cadence de balayage personnalisée :

```json
{
  "plugins": {
    "entries": {
      "memory-core": {
        "config": {
          "dreaming": {
            "enabled": true,
            "timezone": "America/Los_Angeles",
            "frequency": "0 */6 * * *"
          }
        }
      }
    }
  }
}
```

## Commande slash

```
/dreaming status
/dreaming on
/dreaming off
/dreaming help
```

## Flux de travail CLI

Utilisez la promotion CLI pour prévisualiser ou appliquer manuellement :

```bash
openclaw memory promote
openclaw memory promote --apply
openclaw memory promote --limit 5
openclaw memory status --deep
```

La commande manuelle `memory promote` utilise par défaut les seuils de la phase Deep, sauf remplacement
par des indicateurs CLI.

Expliquer pourquoi un candidat spécifique serait ou ne serait pas promu :

```bash
openclaw memory promote-explain "router vlan"
openclaw memory promote-explain "router vlan" --json
```

Prévisualiser les réflexions REM, les vérités candidates et la sortie de promotion Deep sans
rien écrire :

```bash
openclaw memory rem-harness
openclaw memory rem-harness --json
```

## Valeurs par défaut clés

Tous les paramètres se trouvent sous `plugins.entries.memory-core.config.dreaming`.

| Clé         | Par défaut |
| ----------- | ---------- |
| `enabled`   | `false`    |
| `frequency` | `0 3 * * *` |

La politique de phase, les seuils et le comportement de stockage sont des détails d’implémentation
internes (pas une configuration destinée à l’utilisateur).

Voir la [référence de configuration de la mémoire](/fr/reference/memory-config#dreaming)
pour la liste complète des clés.

## Interface Dreams

Lorsqu’il est activé, l’onglet **Dreams** de Gateway affiche :

- l’état actuel d’activation de Dreaming
- l’état au niveau des phases et la présence d’un balayage géré
- les nombres d’éléments à court terme, fondés, de signaux et promus aujourd’hui
- l’heure de la prochaine exécution planifiée
- une voie de scène fondée distincte pour les entrées de relecture historique préparées
- un lecteur de journal des rêves extensible alimenté par `doctor.memory.dreamDiary`

## Liens associés

- [Mémoire](/fr/concepts/memory)
- [Recherche en mémoire](/fr/concepts/memory-search)
- [CLI memory](/cli/memory)
- [Référence de configuration de la mémoire](/fr/reference/memory-config)
