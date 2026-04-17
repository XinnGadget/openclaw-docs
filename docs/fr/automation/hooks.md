---
read_when:
    - Vous souhaitez une automatisation pilotée par les événements pour `/new`, `/reset`, `/stop` et les événements du cycle de vie des agents
    - Vous souhaitez créer, installer ou déboguer des points d’accroche
summary: 'Hooks : automatisation pilotée par les événements pour les commandes et les événements du cycle de vie'
title: Points d’accroche
x-i18n:
    generated_at: "2026-04-11T02:44:23Z"
    model: gpt-5.4
    provider: openai
    source_hash: 14296398e4042d442ebdf071a07c6be99d4afda7cbf3c2b934e76dc5539742c7
    source_path: automation/hooks.md
    workflow: 15
---

# Points d’accroche

Les points d’accroche sont de petits scripts qui s’exécutent lorsqu’un événement se produit dans la Gateway. Ils sont automatiquement détectés à partir de répertoires et peuvent être inspectés avec `openclaw hooks`.

Il existe deux types de points d’accroche dans OpenClaw :

- **Points d’accroche internes** (cette page) : s’exécutent dans la Gateway lorsque des événements d’agent se déclenchent, comme `/new`, `/reset`, `/stop` ou des événements du cycle de vie.
- **Webhooks** : points de terminaison HTTP externes qui permettent à d’autres systèmes de déclencher du travail dans OpenClaw. Consultez [Webhooks](/fr/automation/cron-jobs#webhooks).

Les points d’accroche peuvent aussi être inclus dans des plugins. `openclaw hooks list` affiche à la fois les points d’accroche autonomes et ceux gérés par des plugins.

## Démarrage rapide

```bash
# Lister les points d’accroche disponibles
openclaw hooks list

# Activer un point d’accroche
openclaw hooks enable session-memory

# Vérifier l’état des points d’accroche
openclaw hooks check

# Obtenir des informations détaillées
openclaw hooks info session-memory
```

## Types d’événements

| Événement                | Quand il se déclenche                           |
| ------------------------ | ----------------------------------------------- |
| `command:new`            | Commande `/new` émise                           |
| `command:reset`          | Commande `/reset` émise                         |
| `command:stop`           | Commande `/stop` émise                          |
| `command`                | Tout événement de commande (écouteur général)   |
| `session:compact:before` | Avant que la compaction résume l’historique     |
| `session:compact:after`  | Après la fin de la compaction                   |
| `session:patch`          | Quand les propriétés de session sont modifiées  |
| `agent:bootstrap`        | Avant l’injection des fichiers bootstrap        |
| `gateway:startup`        | Après le démarrage des canaux et le chargement des hooks |
| `message:received`       | Message entrant depuis n’importe quel canal     |
| `message:transcribed`    | Après la fin de la transcription audio          |
| `message:preprocessed`   | Après la fin de tout le traitement des médias et des liens |
| `message:sent`           | Message sortant distribué                       |

## Écrire des points d’accroche

### Structure d’un point d’accroche

Chaque point d’accroche est un répertoire contenant deux fichiers :

```
my-hook/
├── HOOK.md          # Métadonnées + documentation
└── handler.ts       # Implémentation du gestionnaire
```

### Format de HOOK.md

```markdown
---
name: my-hook
description: "Brève description de ce que fait ce point d’accroche"
metadata:
  { "openclaw": { "emoji": "🔗", "events": ["command:new"], "requires": { "bins": ["node"] } } }
---

# Mon point d’accroche

La documentation détaillée va ici.
```

**Champs de métadonnées** (`metadata.openclaw`) :

| Champ      | Description                                          |
| ---------- | ---------------------------------------------------- |
| `emoji`    | Emoji d’affichage pour la CLI                        |
| `events`   | Tableau des événements à écouter                     |
| `export`   | Export nommé à utiliser (par défaut `"default"`)     |
| `os`       | Plateformes requises (par ex. `["darwin", "linux"]`) |
| `requires` | `bins`, `anyBins`, `env` ou chemins `config` requis  |
| `always`   | Ignore les vérifications d’éligibilité (booléen)     |
| `install`  | Méthodes d’installation                              |

### Implémentation du gestionnaire

```typescript
const handler = async (event) => {
  if (event.type !== "command" || event.action !== "new") {
    return;
  }

  console.log(`[my-hook] Commande new déclenchée`);
  // Votre logique ici

  // Facultatif : envoyer un message à l’utilisateur
  event.messages.push("Point d’accroche exécuté !");
};

export default handler;
```

Chaque événement inclut : `type`, `action`, `sessionKey`, `timestamp`, `messages` (ajouter avec push pour envoyer à l’utilisateur) et `context` (données spécifiques à l’événement).

### Points clés du contexte d’événement

**Événements de commande** (`command:new`, `command:reset`) : `context.sessionEntry`, `context.previousSessionEntry`, `context.commandSource`, `context.workspaceDir`, `context.cfg`.

**Événements de message** (`message:received`) : `context.from`, `context.content`, `context.channelId`, `context.metadata` (données spécifiques au fournisseur, notamment `senderId`, `senderName`, `guildId`).

**Événements de message** (`message:sent`) : `context.to`, `context.content`, `context.success`, `context.channelId`.

**Événements de message** (`message:transcribed`) : `context.transcript`, `context.from`, `context.channelId`, `context.mediaPath`.

**Événements de message** (`message:preprocessed`) : `context.bodyForAgent` (corps final enrichi), `context.from`, `context.channelId`.

**Événements bootstrap** (`agent:bootstrap`) : `context.bootstrapFiles` (tableau modifiable), `context.agentId`.

**Événements de patch de session** (`session:patch`) : `context.sessionEntry`, `context.patch` (uniquement les champs modifiés), `context.cfg`. Seuls les clients privilégiés peuvent déclencher des événements de patch.

**Événements de compaction** : `session:compact:before` inclut `messageCount`, `tokenCount`. `session:compact:after` ajoute `compactedCount`, `summaryLength`, `tokensBefore`, `tokensAfter`.

## Détection des points d’accroche

Les points d’accroche sont détectés à partir de ces répertoires, par ordre de priorité d’écrasement croissante :

1. **Points d’accroche intégrés** : fournis avec OpenClaw
2. **Points d’accroche de plugin** : points d’accroche inclus dans des plugins installés
3. **Points d’accroche gérés** : `~/.openclaw/hooks/` (installés par l’utilisateur, partagés entre espaces de travail). Les répertoires supplémentaires provenant de `hooks.internal.load.extraDirs` ont cette même priorité.
4. **Points d’accroche d’espace de travail** : `<workspace>/hooks/` (par agent, désactivés par défaut jusqu’à activation explicite)

Les points d’accroche d’espace de travail peuvent ajouter de nouveaux noms de hooks, mais ne peuvent pas écraser des points d’accroche intégrés, gérés ou fournis par un plugin portant le même nom.

### Packs de points d’accroche

Les packs de points d’accroche sont des paquets npm qui exportent des hooks via `openclaw.hooks` dans `package.json`. Installez-les avec :

```bash
openclaw plugins install <path-or-spec>
```

Les spécifications npm sont limitées au registre (nom du paquet + version exacte facultative ou dist-tag). Les spécifications Git/URL/fichier et les plages semver sont rejetées.

## Points d’accroche intégrés

| Point d’accroche       | Événements                     | Ce qu’il fait                                         |
| ---------------------- | ------------------------------ | ----------------------------------------------------- |
| session-memory         | `command:new`, `command:reset` | Enregistre le contexte de session dans `<workspace>/memory/` |
| bootstrap-extra-files  | `agent:bootstrap`              | Injecte des fichiers bootstrap supplémentaires à partir de motifs glob |
| command-logger         | `command`                      | Journalise toutes les commandes dans `~/.openclaw/logs/commands.log` |
| boot-md                | `gateway:startup`              | Exécute `BOOT.md` au démarrage de la gateway          |

Activez n’importe quel point d’accroche intégré :

```bash
openclaw hooks enable <hook-name>
```

<a id="session-memory"></a>

### Détails de session-memory

Extrait les 15 derniers messages utilisateur/assistant, génère un slug de nom de fichier descriptif via LLM, puis enregistre le tout dans `<workspace>/memory/YYYY-MM-DD-slug.md`. Nécessite que `workspace.dir` soit configuré.

<a id="bootstrap-extra-files"></a>

### Configuration de bootstrap-extra-files

```json
{
  "hooks": {
    "internal": {
      "entries": {
        "bootstrap-extra-files": {
          "enabled": true,
          "paths": ["packages/*/AGENTS.md", "packages/*/TOOLS.md"]
        }
      }
    }
  }
}
```

Les chemins sont résolus relativement à l’espace de travail. Seuls les noms de base bootstrap reconnus sont chargés (`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md`, `MEMORY.md`).

<a id="command-logger"></a>

### Détails de command-logger

Journalise chaque commande slash dans `~/.openclaw/logs/commands.log`.

<a id="boot-md"></a>

### Détails de boot-md

Exécute `BOOT.md` depuis l’espace de travail actif au démarrage de la gateway.

## Hooks de plugin

Les plugins peuvent enregistrer des hooks via le Plugin SDK pour une intégration plus poussée : interception des appels d’outils, modification des prompts, contrôle du flux de messages, etc. Le Plugin SDK expose 28 hooks couvrant la résolution de modèles, le cycle de vie des agents, le flux des messages, l’exécution des outils, la coordination des sous-agents et le cycle de vie de la gateway.

Pour la référence complète des hooks de plugin, y compris `before_tool_call`, `before_agent_reply`, `before_install` et tous les autres hooks de plugin, consultez [Plugin Architecture](/fr/plugins/architecture#provider-runtime-hooks).

## Configuration

```json
{
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "session-memory": { "enabled": true },
        "command-logger": { "enabled": false }
      }
    }
  }
}
```

Variables d’environnement par hook :

```json
{
  "hooks": {
    "internal": {
      "entries": {
        "my-hook": {
          "enabled": true,
          "env": { "MY_CUSTOM_VAR": "value" }
        }
      }
    }
  }
}
```

Répertoires de hooks supplémentaires :

```json
{
  "hooks": {
    "internal": {
      "load": {
        "extraDirs": ["/path/to/more/hooks"]
      }
    }
  }
}
```

<Note>
L’ancien format de configuration en tableau `hooks.internal.handlers` reste pris en charge pour compatibilité descendante, mais les nouveaux hooks doivent utiliser le système basé sur la détection.
</Note>

## Référence CLI

```bash
# Lister tous les hooks (ajoutez --eligible, --verbose ou --json)
openclaw hooks list

# Afficher les informations détaillées d’un hook
openclaw hooks info <hook-name>

# Afficher le résumé d’éligibilité
openclaw hooks check

# Activer/désactiver
openclaw hooks enable <hook-name>
openclaw hooks disable <hook-name>
```

## Bonnes pratiques

- **Gardez les gestionnaires rapides.** Les hooks s’exécutent pendant le traitement des commandes. Déclenchez les tâches lourdes en arrière-plan avec `void processInBackground(event)`.
- **Gérez les erreurs proprement.** Encadrez les opérations risquées avec try/catch ; ne lancez pas d’exception pour que les autres gestionnaires puissent s’exécuter.
- **Filtrez tôt les événements.** Retournez immédiatement si le type/l’action d’événement n’est pas pertinent.
- **Utilisez des clés d’événement spécifiques.** Préférez `"events": ["command:new"]` à `"events": ["command"]` pour réduire la surcharge.

## Dépannage

### Hook non détecté

```bash
# Vérifier la structure du répertoire
ls -la ~/.openclaw/hooks/my-hook/
# Doit afficher : HOOK.md, handler.ts

# Lister tous les hooks détectés
openclaw hooks list
```

### Hook non éligible

```bash
openclaw hooks info my-hook
```

Vérifiez les binaires manquants (PATH), les variables d’environnement, les valeurs de configuration ou la compatibilité du système d’exploitation.

### Hook non exécuté

1. Vérifiez que le hook est activé : `openclaw hooks list`
2. Redémarrez votre processus gateway pour recharger les hooks.
3. Vérifiez les journaux de la gateway : `./scripts/clawlog.sh | grep hook`

## Lié

- [CLI Reference: hooks](/cli/hooks)
- [Webhooks](/fr/automation/cron-jobs#webhooks)
- [Plugin Architecture](/fr/plugins/architecture#provider-runtime-hooks) — référence complète des hooks de plugin
- [Configuration](/fr/gateway/configuration-reference#hooks)
