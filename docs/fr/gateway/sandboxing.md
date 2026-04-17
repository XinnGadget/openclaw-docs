---
read_when: You want a dedicated explanation of sandboxing or need to tune agents.defaults.sandbox.
status: active
summary: 'Comment fonctionne le sandboxing d’OpenClaw : modes, portées, accès à l’espace de travail et images'
title: Sandboxing
x-i18n:
    generated_at: "2026-04-14T02:08:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2573d0d7462f63a68eb1750e5432211522ff5b42989a17379d3e188468bbce52
    source_path: gateway/sandboxing.md
    workflow: 15
---

# Sandboxing

OpenClaw peut exécuter des **outils à l’intérieur de backends de sandbox** pour réduire le rayon d’impact.
Ceci est **facultatif** et contrôlé par la configuration (`agents.defaults.sandbox` ou
`agents.list[].sandbox`). Si le sandboxing est désactivé, les outils s’exécutent sur l’hôte.
Le Gateway reste sur l’hôte ; l’exécution des outils s’exécute dans une sandbox isolée
lorsqu’elle est activée.

Il ne s’agit pas d’une frontière de sécurité parfaite, mais cela limite de façon significative
l’accès au système de fichiers et aux processus lorsque le modèle fait quelque chose de stupide.

## Ce qui est sandboxé

- Exécution des outils (`exec`, `read`, `write`, `edit`, `apply_patch`, `process`, etc.).
- Navigateur sandboxé facultatif (`agents.defaults.sandbox.browser`).
  - Par défaut, le navigateur sandboxé démarre automatiquement (ce qui garantit que le CDP est joignable) lorsque l’outil de navigateur en a besoin.
    Configurez cela via `agents.defaults.sandbox.browser.autoStart` et `agents.defaults.sandbox.browser.autoStartTimeoutMs`.
  - Par défaut, les conteneurs du navigateur sandboxé utilisent un réseau Docker dédié (`openclaw-sandbox-browser`) au lieu du réseau global `bridge`.
    Configurez cela avec `agents.defaults.sandbox.browser.network`.
  - L’option facultative `agents.defaults.sandbox.browser.cdpSourceRange` restreint l’entrée CDP en bordure de conteneur avec une allowlist CIDR (par exemple `172.21.0.1/32`).
  - L’accès observateur noVNC est protégé par mot de passe par défaut ; OpenClaw émet une URL à jeton de courte durée qui sert une page d’amorçage locale et ouvre noVNC avec le mot de passe dans le fragment d’URL (pas dans les journaux de requête/en-tête).
  - `agents.defaults.sandbox.browser.allowHostControl` permet aux sessions sandboxées de cibler explicitement le navigateur hôte.
  - Des allowlists facultatives contrôlent `target: "custom"` : `allowedControlUrls`, `allowedControlHosts`, `allowedControlPorts`.

Non sandboxé :

- Le processus Gateway lui-même.
- Tout outil explicitement autorisé à s’exécuter en dehors de la sandbox (par ex. `tools.elevated`).
  - **L’exécution elevated contourne le sandboxing et utilise le chemin d’échappement configuré (`gateway` par défaut, ou `node` lorsque la cible d’exécution est `node`).**
  - Si le sandboxing est désactivé, `tools.elevated` ne change pas l’exécution (déjà sur l’hôte). Voir [Mode elevated](/fr/tools/elevated).

## Modes

`agents.defaults.sandbox.mode` contrôle **quand** le sandboxing est utilisé :

- `"off"` : aucun sandboxing.
- `"non-main"` : sandboxe uniquement les sessions **non principales** (par défaut si vous voulez des chats normaux sur l’hôte).
- `"all"` : chaque session s’exécute dans une sandbox.
  Remarque : `"non-main"` se base sur `session.mainKey` (valeur par défaut `"main"`), et non sur l’id de l’agent.
  Les sessions de groupe/canal utilisent leurs propres clés ; elles sont donc considérées comme non principales et seront sandboxées.

## Portée

`agents.defaults.sandbox.scope` contrôle **combien de conteneurs** sont créés :

- `"agent"` (par défaut) : un conteneur par agent.
- `"session"` : un conteneur par session.
- `"shared"` : un conteneur partagé par toutes les sessions sandboxées.

## Backend

`agents.defaults.sandbox.backend` contrôle **quel runtime** fournit la sandbox :

- `"docker"` (par défaut) : runtime de sandbox local basé sur Docker.
- `"ssh"` : runtime de sandbox distant générique basé sur SSH.
- `"openshell"` : runtime de sandbox basé sur OpenShell.

La configuration spécifique à SSH se trouve sous `agents.defaults.sandbox.ssh`.
La configuration spécifique à OpenShell se trouve sous `plugins.entries.openshell.config`.

### Choisir un backend

|                     | Docker                           | SSH                            | OpenShell                                           |
| ------------------- | -------------------------------- | ------------------------------ | --------------------------------------------------- |
| **Où il s’exécute** | Conteneur local                  | Tout hôte accessible en SSH    | Sandbox gérée par OpenShell                         |
| **Configuration**   | `scripts/sandbox-setup.sh`       | Clé SSH + hôte cible           | Plugin OpenShell activé                             |
| **Modèle d’espace de travail** | Montage bind ou copie               | Canonique à distance (amorçage unique) | `mirror` ou `remote`                                |
| **Contrôle réseau** | `docker.network` (par défaut : aucun) | Dépend de l’hôte distant       | Dépend d’OpenShell                                  |
| **Sandbox de navigateur** | Pris en charge                  | Non pris en charge             | Pas encore pris en charge                           |
| **Montages bind**   | `docker.binds`                   | N/A                            | N/A                                                 |
| **Idéal pour**      | Développement local, isolation complète | Déporter sur une machine distante | Sandboxes distantes gérées avec synchronisation bidirectionnelle facultative |

### Backend Docker

Le backend Docker est le runtime par défaut, exécutant localement les outils et les navigateurs sandboxés via le socket du daemon Docker (`/var/run/docker.sock`). L’isolation du conteneur sandbox est déterminée par les espaces de noms Docker.

**Contraintes Docker-out-of-Docker (DooD)** :
Si vous déployez le Gateway OpenClaw lui-même comme conteneur Docker, il orchestre des conteneurs sandbox frères en utilisant le socket Docker de l’hôte (DooD). Cela introduit une contrainte spécifique de correspondance des chemins :

- **La configuration nécessite des chemins hôte** : la configuration `workspace` dans `openclaw.json` DOIT contenir le **chemin absolu de l’hôte** (par exemple `/home/user/.openclaw/workspaces`), et non le chemin interne du conteneur Gateway. Lorsque OpenClaw demande au daemon Docker de lancer une sandbox, le daemon évalue les chemins par rapport à l’espace de noms du système hôte, et non à celui du Gateway.
- **Parité du pont FS (mappage de volume identique)** : le processus natif du Gateway OpenClaw écrit également des fichiers heartbeat et bridge dans le répertoire `workspace`. Comme le Gateway évalue exactement la même chaîne (le chemin hôte) depuis son propre environnement conteneurisé, le déploiement du Gateway DOIT inclure un mappage de volume identique reliant l’espace de noms hôte nativement (`-v /home/user/.openclaw:/home/user/.openclaw`).

Si vous mappez les chemins en interne sans parité absolue avec l’hôte, OpenClaw lève nativement une erreur de permission `EACCES` lorsqu’il tente d’écrire son heartbeat dans l’environnement du conteneur, car la chaîne de chemin complètement qualifiée n’existe pas nativement.

### Backend SSH

Utilisez `backend: "ssh"` lorsque vous voulez qu’OpenClaw sandboxe `exec`, les outils de fichiers et les lectures de médias sur
une machine arbitraire accessible en SSH.

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "all",
        backend: "ssh",
        scope: "session",
        workspaceAccess: "rw",
        ssh: {
          target: "user@gateway-host:22",
          workspaceRoot: "/tmp/openclaw-sandboxes",
          strictHostKeyChecking: true,
          updateHostKeys: true,
          identityFile: "~/.ssh/id_ed25519",
          certificateFile: "~/.ssh/id_ed25519-cert.pub",
          knownHostsFile: "~/.ssh/known_hosts",
          // Ou utilisez des SecretRefs / contenus inline au lieu de fichiers locaux :
          // identityData: { source: "env", provider: "default", id: "SSH_IDENTITY" },
          // certificateData: { source: "env", provider: "default", id: "SSH_CERTIFICATE" },
          // knownHostsData: { source: "env", provider: "default", id: "SSH_KNOWN_HOSTS" },
        },
      },
    },
  },
}
```

Comment cela fonctionne :

- OpenClaw crée une racine distante par portée sous `sandbox.ssh.workspaceRoot`.
- Lors de la première utilisation après création ou recréation, OpenClaw initialise cet espace de travail distant une fois à partir de l’espace de travail local.
- Ensuite, `exec`, `read`, `write`, `edit`, `apply_patch`, les lectures de médias du prompt et la préparation des médias entrants s’exécutent directement sur l’espace de travail distant via SSH.
- OpenClaw ne synchronise pas automatiquement les modifications distantes vers l’espace de travail local.

Éléments d’authentification :

- `identityFile`, `certificateFile`, `knownHostsFile` : utilisent des fichiers locaux existants et les transmettent via la configuration OpenSSH.
- `identityData`, `certificateData`, `knownHostsData` : utilisent des chaînes inline ou des SecretRefs. OpenClaw les résout via le snapshot runtime normal des secrets, les écrit dans des fichiers temporaires avec `0600`, puis les supprime à la fin de la session SSH.
- Si `*File` et `*Data` sont définis tous les deux pour le même élément, `*Data` l’emporte pour cette session SSH.

Il s’agit d’un modèle **canonique à distance**. L’espace de travail SSH distant devient l’état réel de la sandbox après l’amorçage initial.

Conséquences importantes :

- Les modifications locales sur l’hôte effectuées en dehors d’OpenClaw après l’étape d’amorçage ne sont pas visibles à distance tant que vous ne recréez pas la sandbox.
- `openclaw sandbox recreate` supprime la racine distante par portée et réamorce depuis le local lors de la prochaine utilisation.
- Le sandboxing du navigateur n’est pas pris en charge sur le backend SSH.
- Les paramètres `sandbox.docker.*` ne s’appliquent pas au backend SSH.

### Backend OpenShell

Utilisez `backend: "openshell"` lorsque vous voulez qu’OpenClaw sandboxe les outils dans un
environnement distant géré par OpenShell. Pour le guide d’installation complet, la référence de configuration
et la comparaison des modes d’espace de travail, consultez la
[page OpenShell dédiée](/fr/gateway/openshell).

OpenShell réutilise le même transport SSH central et le même bridge de système de fichiers distant que le
backend SSH générique, et ajoute le cycle de vie spécifique à OpenShell
(`sandbox create/get/delete`, `sandbox ssh-config`) ainsi que le mode d’espace de travail `mirror`
facultatif.

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "all",
        backend: "openshell",
        scope: "session",
        workspaceAccess: "rw",
      },
    },
  },
  plugins: {
    entries: {
      openshell: {
        enabled: true,
        config: {
          from: "openclaw",
          mode: "remote", // mirror | remote
          remoteWorkspaceDir: "/sandbox",
          remoteAgentWorkspaceDir: "/agent",
        },
      },
    },
  },
}
```

Modes OpenShell :

- `mirror` (par défaut) : l’espace de travail local reste canonique. OpenClaw synchronise les fichiers locaux vers OpenShell avant `exec` et resynchronise l’espace de travail distant après `exec`.
- `remote` : l’espace de travail OpenShell devient canonique après la création de la sandbox. OpenClaw initialise l’espace de travail distant une fois depuis l’espace de travail local, puis les outils de fichiers et `exec` s’exécutent directement sur la sandbox distante sans resynchroniser les changements en retour.

Détails du transport distant :

- OpenClaw demande à OpenShell la configuration SSH spécifique à la sandbox via `openshell sandbox ssh-config <name>`.
- Le cœur écrit cette configuration SSH dans un fichier temporaire, ouvre la session SSH, puis réutilise le même bridge de système de fichiers distant que celui utilisé par `backend: "ssh"`.
- En mode `mirror`, seul le cycle de vie diffère : synchronisation du local vers le distant avant `exec`, puis synchronisation inverse après `exec`.

Limites actuelles d’OpenShell :

- le navigateur sandboxé n’est pas encore pris en charge
- `sandbox.docker.binds` n’est pas pris en charge sur le backend OpenShell
- les paramètres runtime spécifiques à Docker sous `sandbox.docker.*` continuent de s’appliquer uniquement au backend Docker

#### Modes d’espace de travail

OpenShell a deux modèles d’espace de travail. C’est la partie la plus importante en pratique.

##### `mirror`

Utilisez `plugins.entries.openshell.config.mode: "mirror"` lorsque vous voulez que **l’espace de travail local reste canonique**.

Comportement :

- Avant `exec`, OpenClaw synchronise l’espace de travail local vers la sandbox OpenShell.
- Après `exec`, OpenClaw synchronise l’espace de travail distant vers l’espace de travail local.
- Les outils de fichiers fonctionnent toujours via le bridge de sandbox, mais l’espace de travail local reste la source de vérité entre les tours.

Utilisez ce mode lorsque :

- vous modifiez des fichiers localement en dehors d’OpenClaw et voulez que ces modifications apparaissent automatiquement dans la sandbox
- vous voulez que la sandbox OpenShell se comporte autant que possible comme le backend Docker
- vous voulez que l’espace de travail hôte reflète les écritures de la sandbox après chaque tour `exec`

Compromis :

- coût de synchronisation supplémentaire avant et après `exec`

##### `remote`

Utilisez `plugins.entries.openshell.config.mode: "remote"` lorsque vous voulez que **l’espace de travail OpenShell devienne canonique**.

Comportement :

- Lorsque la sandbox est créée pour la première fois, OpenClaw initialise l’espace de travail distant une fois depuis l’espace de travail local.
- Ensuite, `exec`, `read`, `write`, `edit` et `apply_patch` s’exécutent directement sur l’espace de travail OpenShell distant.
- OpenClaw **ne** synchronise **pas** les modifications distantes vers l’espace de travail local après `exec`.
- Les lectures de médias au moment du prompt continuent de fonctionner, car les outils de fichiers et de médias lisent via le bridge de sandbox au lieu de supposer un chemin local sur l’hôte.
- Le transport se fait via SSH dans la sandbox OpenShell renvoyée par `openshell sandbox ssh-config`.

Conséquences importantes :

- Si vous modifiez des fichiers sur l’hôte en dehors d’OpenClaw après l’étape d’amorçage, la sandbox distante **ne** verra **pas** automatiquement ces modifications.
- Si la sandbox est recréée, l’espace de travail distant est de nouveau initialisé à partir de l’espace de travail local.
- Avec `scope: "agent"` ou `scope: "shared"`, cet espace de travail distant est partagé à cette même portée.

Utilisez cela lorsque :

- la sandbox doit vivre principalement du côté distant OpenShell
- vous voulez réduire le surcoût de synchronisation à chaque tour
- vous ne voulez pas que des modifications locales sur l’hôte écrasent silencieusement l’état distant de la sandbox

Choisissez `mirror` si vous considérez la sandbox comme un environnement d’exécution temporaire.
Choisissez `remote` si vous considérez la sandbox comme le véritable espace de travail.

#### Cycle de vie OpenShell

Les sandboxes OpenShell sont toujours gérées via le cycle de vie normal des sandboxes :

- `openclaw sandbox list` affiche les runtimes OpenShell ainsi que les runtimes Docker
- `openclaw sandbox recreate` supprime le runtime actuel et laisse OpenClaw le recréer lors de la prochaine utilisation
- la logique de nettoyage est également adaptée au backend

Pour le mode `remote`, recréer est particulièrement important :

- recréer supprime l’espace de travail distant canonique pour cette portée
- l’utilisation suivante initialise un nouvel espace de travail distant à partir de l’espace de travail local

Pour le mode `mirror`, recréer réinitialise principalement l’environnement d’exécution distant
car l’espace de travail local reste canonique de toute façon.

## Accès à l’espace de travail

`agents.defaults.sandbox.workspaceAccess` contrôle **ce que la sandbox peut voir** :

- `"none"` (par défaut) : les outils voient un espace de travail de sandbox sous `~/.openclaw/sandboxes`.
- `"ro"` : monte l’espace de travail de l’agent en lecture seule sur `/agent` (désactive `write`/`edit`/`apply_patch`).
- `"rw"` : monte l’espace de travail de l’agent en lecture/écriture sur `/workspace`.

Avec le backend OpenShell :

- le mode `mirror` continue d’utiliser l’espace de travail local comme source canonique entre les tours `exec`
- le mode `remote` utilise l’espace de travail OpenShell distant comme source canonique après l’amorçage initial
- `workspaceAccess: "ro"` et `"none"` continuent de restreindre le comportement d’écriture de la même manière

Les médias entrants sont copiés dans l’espace de travail actif de la sandbox (`media/inbound/*`).
Remarque sur les Skills : l’outil `read` est enraciné dans la sandbox. Avec `workspaceAccess: "none"`,
OpenClaw recopie les Skills éligibles dans l’espace de travail de la sandbox (`.../skills`) afin
qu’ils puissent être lus. Avec `"rw"`, les Skills du workspace sont lisibles depuis
`/workspace/skills`.

## Montages bind personnalisés

`agents.defaults.sandbox.docker.binds` monte des répertoires hôte supplémentaires dans le conteneur.
Format : `host:container:mode` (par ex., `"/home/user/source:/source:rw"`).

Les binds globaux et par agent sont **fusionnés** (et non remplacés). Sous `scope: "shared"`, les binds par agent sont ignorés.

`agents.defaults.sandbox.browser.binds` monte des répertoires hôte supplémentaires dans le conteneur du **navigateur sandboxé** uniquement.

- Lorsqu’il est défini (y compris `[]`), il remplace `agents.defaults.sandbox.docker.binds` pour le conteneur du navigateur.
- Lorsqu’il est omis, le conteneur du navigateur revient à `agents.defaults.sandbox.docker.binds` (compatibilité ascendante).

Exemple (source en lecture seule + un répertoire de données supplémentaire) :

```json5
{
  agents: {
    defaults: {
      sandbox: {
        docker: {
          binds: ["/home/user/source:/source:ro", "/var/data/myapp:/data:ro"],
        },
      },
    },
    list: [
      {
        id: "build",
        sandbox: {
          docker: {
            binds: ["/mnt/cache:/cache:rw"],
          },
        },
      },
    ],
  },
}
```

Remarques de sécurité :

- Les binds contournent le système de fichiers de la sandbox : ils exposent des chemins hôte avec le mode que vous définissez (`:ro` ou `:rw`).
- OpenClaw bloque les sources de bind dangereuses (par exemple : `docker.sock`, `/etc`, `/proc`, `/sys`, `/dev`, ainsi que les montages parents qui les exposeraient).
- OpenClaw bloque aussi les racines courantes d’identifiants dans le répertoire personnel telles que `~/.aws`, `~/.cargo`, `~/.config`, `~/.docker`, `~/.gnupg`, `~/.netrc`, `~/.npm` et `~/.ssh`.
- La validation des binds ne repose pas uniquement sur une comparaison de chaînes. OpenClaw normalise le chemin source, puis le résout à nouveau via l’ancêtre existant le plus profond avant de revérifier les chemins bloqués et les racines autorisées.
- Cela signifie que les échappements via parent symlink échouent toujours de manière sûre, même lorsque la feuille finale n’existe pas encore. Exemple : `/workspace/run-link/new-file` se résout quand même en `/var/run/...` si `run-link` pointe vers cet emplacement.
- Les racines source autorisées sont canonisées de la même manière, donc un chemin qui semble seulement à l’intérieur de l’allowlist avant résolution des symlinks est tout de même rejeté comme `outside allowed roots`.
- Les montages sensibles (secrets, clés SSH, identifiants de service) devraient être en `:ro` sauf nécessité absolue.
- Combinez cela avec `workspaceAccess: "ro"` si vous n’avez besoin que d’un accès en lecture à l’espace de travail ; les modes de bind restent indépendants.
- Voir [Sandbox vs Tool Policy vs Elevated](/fr/gateway/sandbox-vs-tool-policy-vs-elevated) pour comprendre comment les binds interagissent avec la stratégie d’outils et l’exécution elevated.

## Images + configuration

Image Docker par défaut : `openclaw-sandbox:bookworm-slim`

Construisez-la une fois :

```bash
scripts/sandbox-setup.sh
```

Remarque : l’image par défaut **n’inclut pas** Node. Si une Skill a besoin de Node (ou
d’autres runtimes), intégrez une image personnalisée ou installez-les via
`sandbox.docker.setupCommand` (nécessite une sortie réseau + une racine accessible en écriture +
l’utilisateur root).

Si vous voulez une image de sandbox plus fonctionnelle avec des outils courants (par exemple
`curl`, `jq`, `nodejs`, `python3`, `git`), construisez :

```bash
scripts/sandbox-common-setup.sh
```

Ensuite, définissez `agents.defaults.sandbox.docker.image` sur
`openclaw-sandbox-common:bookworm-slim`.

Image du navigateur sandboxé :

```bash
scripts/sandbox-browser-setup.sh
```

Par défaut, les conteneurs Docker sandboxés s’exécutent **sans réseau**.
Remplacez cela avec `agents.defaults.sandbox.docker.network`.

L’image groupée du navigateur sandboxé applique également des valeurs de démarrage conservatrices pour Chromium
dans des charges de travail conteneurisées. Les valeurs par défaut actuelles du conteneur incluent :

- `--remote-debugging-address=127.0.0.1`
- `--remote-debugging-port=<derived from OPENCLAW_BROWSER_CDP_PORT>`
- `--user-data-dir=${HOME}/.chrome`
- `--no-first-run`
- `--no-default-browser-check`
- `--disable-3d-apis`
- `--disable-gpu`
- `--disable-dev-shm-usage`
- `--disable-background-networking`
- `--disable-extensions`
- `--disable-features=TranslateUI`
- `--disable-breakpad`
- `--disable-crash-reporter`
- `--disable-software-rasterizer`
- `--no-zygote`
- `--metrics-recording-only`
- `--renderer-process-limit=2`
- `--no-sandbox` et `--disable-setuid-sandbox` lorsque `noSandbox` est activé.
- Les trois drapeaux de durcissement graphique (`--disable-3d-apis`,
  `--disable-software-rasterizer`, `--disable-gpu`) sont facultatifs et utiles
  lorsque les conteneurs n’ont pas de prise en charge GPU. Définissez `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0`
  si votre charge de travail nécessite WebGL ou d’autres fonctionnalités 3D/navigateur.
- `--disable-extensions` est activé par défaut et peut être désactivé avec
  `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` pour les flux dépendants des extensions.
- `--renderer-process-limit=2` est contrôlé par
  `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>`, où `0` conserve la valeur par défaut de Chromium.

Si vous avez besoin d’un profil runtime différent, utilisez une image de navigateur personnalisée et fournissez
votre propre entrypoint. Pour les profils Chromium locaux (non conteneurisés), utilisez
`browser.extraArgs` pour ajouter des drapeaux de démarrage supplémentaires.

Valeurs de sécurité par défaut :

- `network: "host"` est bloqué.
- `network: "container:<id>"` est bloqué par défaut (risque de contournement par jonction d’espace de noms).
- Dérogation de dernier recours : `agents.defaults.sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true`.

Les installations Docker et le Gateway conteneurisé se trouvent ici :
[Docker](/fr/install/docker)

Pour les déploiements du Gateway Docker, `scripts/docker/setup.sh` peut initialiser la configuration de sandbox.
Définissez `OPENCLAW_SANDBOX=1` (ou `true`/`yes`/`on`) pour activer ce chemin. Vous pouvez
remplacer l’emplacement du socket avec `OPENCLAW_DOCKER_SOCKET`. Référence complète sur
l’installation et les variables d’environnement : [Docker](/fr/install/docker#agent-sandbox).

## setupCommand (configuration unique du conteneur)

`setupCommand` s’exécute **une seule fois** après la création du conteneur sandbox (et non à chaque exécution).
Il s’exécute à l’intérieur du conteneur via `sh -lc`.

Chemins :

- Global : `agents.defaults.sandbox.docker.setupCommand`
- Par agent : `agents.list[].sandbox.docker.setupCommand`

Pièges courants :

- La valeur par défaut de `docker.network` est `"none"` (aucune sortie réseau), donc les installations de paquets échoueront.
- `docker.network: "container:<id>"` nécessite `dangerouslyAllowContainerNamespaceJoin: true` et doit rester une dérogation exceptionnelle.
- `readOnlyRoot: true` empêche les écritures ; définissez `readOnlyRoot: false` ou intégrez une image personnalisée.
- `user` doit être root pour les installations de paquets (omettez `user` ou définissez `user: "0:0"`).
- L’exécution sandboxée n’hérite **pas** du `process.env` de l’hôte. Utilisez
  `agents.defaults.sandbox.docker.env` (ou une image personnalisée) pour les clés API des Skills.

## Stratégie d’outils + échappatoires

Les stratégies d’autorisation/refus des outils s’appliquent toujours avant les règles de sandbox. Si un outil est refusé
globalement ou par agent, le sandboxing ne le réactive pas.

`tools.elevated` est une échappatoire explicite qui exécute `exec` en dehors de la sandbox (`gateway` par défaut, ou `node` lorsque la cible d’exécution est `node`).
Les directives `/exec` ne s’appliquent qu’aux expéditeurs autorisés et persistent par session ; pour désactiver totalement
`exec`, utilisez un refus via la stratégie d’outils (voir [Sandbox vs Tool Policy vs Elevated](/fr/gateway/sandbox-vs-tool-policy-vs-elevated)).

Débogage :

- Utilisez `openclaw sandbox explain` pour inspecter le mode sandbox effectif, la stratégie d’outils et les clés de configuration de correction.
- Voir [Sandbox vs Tool Policy vs Elevated](/fr/gateway/sandbox-vs-tool-policy-vs-elevated) pour le modèle mental « pourquoi ceci est-il bloqué ? ».
  Gardez cela strictement verrouillé.

## Remplacements multi-agent

Chaque agent peut remplacer le sandboxing + les outils :
`agents.list[].sandbox` et `agents.list[].tools` (ainsi que `agents.list[].tools.sandbox.tools` pour la stratégie d’outils de sandbox).
Voir [Sandbox & Tools multi-agent](/fr/tools/multi-agent-sandbox-tools) pour la priorité.

## Exemple minimal d’activation

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none",
      },
    },
  },
}
```

## Documentation associée

- [OpenShell](/fr/gateway/openshell) -- configuration du backend de sandbox géré, modes d’espace de travail et référence de configuration
- [Configuration de sandbox](/fr/gateway/configuration-reference#agentsdefaultssandbox)
- [Sandbox vs Tool Policy vs Elevated](/fr/gateway/sandbox-vs-tool-policy-vs-elevated) -- déboguer « pourquoi ceci est-il bloqué ? »
- [Sandbox & Tools multi-agent](/fr/tools/multi-agent-sandbox-tools) -- remplacements par agent et priorité
- [Sécurité](/fr/gateway/security)
