---
read_when:
    - Vous devez inspecter la sortie brute du modèle pour détecter les fuites de raisonnement
    - Vous voulez exécuter le Gateway en mode watch pendant vos itérations
    - Vous avez besoin d’un flux de travail de débogage reproductible
summary: 'Outils de débogage : mode watch, flux bruts du modèle et traçage des fuites de raisonnement'
title: Débogage
x-i18n:
    generated_at: "2026-04-12T23:28:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: bc31ce9b41e92a14c4309f32df569b7050b18024f83280930e53714d3bfcd5cc
    source_path: help/debugging.md
    workflow: 15
---

# Débogage

Cette page présente des aides au débogage pour la sortie en streaming, en particulier lorsqu’un fournisseur mélange le raisonnement au texte normal.

## Remplacements de débogage à l’exécution

Utilisez `/debug` dans le chat pour définir des remplacements de configuration **uniquement à l’exécution** (en mémoire, pas sur le disque).
`/debug` est désactivé par défaut ; activez-le avec `commands.debug: true`.
C’est pratique lorsque vous devez activer ou désactiver des réglages peu courants sans modifier `openclaw.json`.

Exemples :

```
/debug show
/debug set messages.responsePrefix="[openclaw]"
/debug unset messages.responsePrefix
/debug reset
```

`/debug reset` efface tous les remplacements et rétablit la configuration stockée sur le disque.

## Sortie de trace de session

Utilisez `/trace` lorsque vous voulez voir les lignes de trace/de débogage appartenant aux plugins dans une session sans activer le mode verbeux complet.

Exemples :

```text
/trace
/trace on
/trace off
```

Utilisez `/trace` pour les diagnostics de plugins, comme les résumés de débogage de Active Memory.
Continuez d’utiliser `/verbose` pour la sortie normale verbeuse des statuts/outils, et continuez d’utiliser `/debug` pour les remplacements de configuration uniquement à l’exécution.

## Mode watch du Gateway

Pour itérer rapidement, exécutez le gateway sous le watcher de fichiers :

```bash
pnpm gateway:watch
```

Cela correspond à :

```bash
node scripts/watch-node.mjs gateway --force
```

Le watcher redémarre en cas de modification des fichiers pertinents pour la compilation sous `src/`, des fichiers source d’extensions,
du `package.json` des extensions et des métadonnées `openclaw.plugin.json`, de `tsconfig.json`,
de `package.json` et de `tsdown.config.ts`. Les modifications des métadonnées d’extension redémarrent le
gateway sans forcer une reconstruction `tsdown` ; les modifications du code source et de configuration
reconstruisent toujours `dist` d’abord.

Ajoutez tous les drapeaux CLI du gateway après `gateway:watch` et ils seront transmis à chaque redémarrage.
Relancer la même commande watch pour le même dépôt/jeu de drapeaux remplace désormais
l’ancien watcher au lieu de laisser des processus parents de watcher en double.

## Profil de dev + gateway de dev (`--dev`)

Utilisez le profil de dev pour isoler l’état et démarrer un environnement sûr et jetable pour le
débogage. Il existe **deux** drapeaux `--dev` :

- **`--dev` global (profil) :** isole l’état sous `~/.openclaw-dev` et
  définit par défaut le port du gateway sur `19001` (les ports dérivés se décalent avec lui).
- **`gateway --dev` :** indique au Gateway de créer automatiquement une configuration par défaut +
  un espace de travail s’ils sont absents (et d’ignorer `BOOTSTRAP.md`).

Flux recommandé (profil de dev + bootstrap de dev) :

```bash
pnpm gateway:dev
OPENCLAW_PROFILE=dev openclaw tui
```

Si vous n’avez pas encore d’installation globale, exécutez la CLI via `pnpm openclaw ...`.

Voici ce que cela fait :

1. **Isolation du profil** (`--dev` global)
   - `OPENCLAW_PROFILE=dev`
   - `OPENCLAW_STATE_DIR=~/.openclaw-dev`
   - `OPENCLAW_CONFIG_PATH=~/.openclaw-dev/openclaw.json`
   - `OPENCLAW_GATEWAY_PORT=19001` (les ports du navigateur/canvas se décalent en conséquence)

2. **Bootstrap de dev** (`gateway --dev`)
   - Écrit une configuration minimale si elle est absente (`gateway.mode=local`, bind loopback).
   - Définit `agent.workspace` sur l’espace de travail de dev.
   - Définit `agent.skipBootstrap=true` (pas de `BOOTSTRAP.md`).
   - Initialise les fichiers de l’espace de travail s’ils sont absents :
     `AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`.
   - Identité par défaut : **C3‑PO** (droïde de protocole).
   - Ignore les fournisseurs de canaux en mode dev (`OPENCLAW_SKIP_CHANNELS=1`).

Flux de réinitialisation (nouveau départ) :

```bash
pnpm gateway:dev:reset
```

Remarque : `--dev` est un drapeau de profil **global** et il est consommé par certains runners.
Si vous devez l’écrire explicitement, utilisez la forme avec variable d’environnement :

```bash
OPENCLAW_PROFILE=dev openclaw gateway --dev --reset
```

`--reset` efface la configuration, les identifiants, les sessions et l’espace de travail de dev (en utilisant
`trash`, pas `rm`), puis recrée l’environnement de dev par défaut.

Astuce : si un gateway non-dev est déjà en cours d’exécution (launchd/systemd), arrêtez-le d’abord :

```bash
openclaw gateway stop
```

## Journalisation du flux brut (OpenClaw)

OpenClaw peut journaliser le **flux brut de l’assistant** avant tout filtrage/formatage.
C’est la meilleure façon de voir si le raisonnement arrive sous forme de deltas de texte brut
(ou sous forme de blocs de réflexion séparés).

Activez-la via la CLI :

```bash
pnpm gateway:watch --raw-stream
```

Remplacement de chemin facultatif :

```bash
pnpm gateway:watch --raw-stream --raw-stream-path ~/.openclaw/logs/raw-stream.jsonl
```

Variables d’environnement équivalentes :

```bash
OPENCLAW_RAW_STREAM=1
OPENCLAW_RAW_STREAM_PATH=~/.openclaw/logs/raw-stream.jsonl
```

Fichier par défaut :

`~/.openclaw/logs/raw-stream.jsonl`

## Journalisation des fragments bruts (pi-mono)

Pour capturer les **fragments OpenAI-compat bruts** avant qu’ils ne soient analysés en blocs,
pi-mono expose un logger distinct :

```bash
PI_RAW_STREAM=1
```

Chemin facultatif :

```bash
PI_RAW_STREAM_PATH=~/.pi-mono/logs/raw-openai-completions.jsonl
```

Fichier par défaut :

`~/.pi-mono/logs/raw-openai-completions.jsonl`

> Remarque : ceci n’est émis que par les processus utilisant le fournisseur
> `openai-completions` de pi-mono.

## Notes de sécurité

- Les journaux de flux bruts peuvent inclure les prompts complets, la sortie des outils et les données utilisateur.
- Conservez les journaux en local et supprimez-les après le débogage.
- Si vous partagez des journaux, supprimez d’abord les secrets et les données personnelles identifiables.
