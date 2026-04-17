---
read_when:
    - Ajouter ou modifier des Skillsրեցნილ_translation error
    - Modifier le filtrage des Skills ou les règles de chargement
summary: 'Skills : gérées ou workspace, règles de filtrage et configuration/env wiring'
title: Skills
x-i18n:
    generated_at: "2026-04-11T02:48:00Z"
    model: gpt-5.4
    provider: openai
    source_hash: b1eaf130966950b6eb24f859d9a77ecbf81c6cb80deaaa6a3a79d2c16d83115d
    source_path: tools/skills.md
    workflow: 15
---

# Skills (OpenClaw)

OpenClaw utilise des dossiers de Skills **compatibles avec [AgentSkills](https://agentskills.io)** pour apprendre à l'agent à utiliser les outils. Chaque Skill est un répertoire contenant un `SKILL.md` avec un frontmatter YAML et des instructions. OpenClaw charge les **Skills intégrées** ainsi que des remplacements locaux facultatifs, puis les filtre au chargement selon l'environnement, la configuration et la présence des binaires.

## Emplacements et priorité

OpenClaw charge les Skills depuis ces sources :

1. **Dossiers de Skills supplémentaires** : configurés avec `skills.load.extraDirs`
2. **Skills intégrées** : livrées avec l'installation (package npm ou OpenClaw.app)
3. **Skills gérées/locales** : `~/.openclaw/skills`
4. **Skills agent personnelles** : `~/.agents/skills`
5. **Skills agent de projet** : `<workspace>/.agents/skills`
6. **Skills workspace** : `<workspace>/skills`

En cas de conflit de nom de Skill, la priorité est :

`<workspace>/skills` (la plus élevée) → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → Skills intégrées → `skills.load.extraDirs` (la plus basse)

## Skills par agent ou partagées

Dans les configurations **multi-agent**, chaque agent a son propre workspace. Cela signifie :

- Les **Skills par agent** se trouvent dans `<workspace>/skills` pour cet agent uniquement.
- Les **Skills agent de projet** se trouvent dans `<workspace>/.agents/skills` et s'appliquent à
  ce workspace avant le dossier `skills/` normal du workspace.
- Les **Skills agent personnelles** se trouvent dans `~/.agents/skills` et s'appliquent à tous les
  workspaces de cette machine.
- Les **Skills partagées** se trouvent dans `~/.openclaw/skills` (gérées/locales) et sont visibles
  pour **tous les agents** sur la même machine.
- Des **dossiers partagés** peuvent aussi être ajoutés via `skills.load.extraDirs` (priorité
  la plus basse) si vous voulez un pack commun de Skills utilisé par plusieurs agents.

Si le même nom de Skill existe à plusieurs endroits, la priorité habituelle
s'applique : le workspace l'emporte, puis les Skills agent de projet, puis les Skills agent personnelles,
puis les Skills gérées/locales, puis les intégrées, puis les répertoires supplémentaires.

## Listes d'autorisation de Skills par agent

L'**emplacement** d'une Skill et sa **visibilité** sont deux contrôles distincts.

- L'emplacement/la priorité décide quelle copie d'une Skill portant le même nom l'emporte.
- Les listes d'autorisation d'agent décident quelles Skills visibles un agent peut réellement utiliser.

Utilisez `agents.defaults.skills` pour une base partagée, puis remplacez-la par agent avec
`agents.list[].skills` :

```json5
{
  agents: {
    defaults: {
      skills: ["github", "weather"],
    },
    list: [
      { id: "writer" }, // hérite de github, weather
      { id: "docs", skills: ["docs-search"] }, // remplace les valeurs par défaut
      { id: "locked-down", skills: [] }, // aucune Skills
    ],
  },
}
```

Règles :

- Omettez `agents.defaults.skills` pour des Skills non restreintes par défaut.
- Omettez `agents.list[].skills` pour hériter de `agents.defaults.skills`.
- Définissez `agents.list[].skills: []` pour aucune Skills.
- Une liste non vide `agents.list[].skills` est l'ensemble final pour cet agent ; elle
  n'est pas fusionnée avec les valeurs par défaut.

OpenClaw applique l'ensemble de Skills effectif de l'agent à la construction des invites, à la
découverte des commandes slash de Skills, à la synchronisation du sandbox et aux instantanés de Skills.

## Plugins + Skills

Les plugins peuvent livrer leurs propres Skills en listant des répertoires `skills` dans
`openclaw.plugin.json` (chemins relatifs à la racine du plugin). Les Skills de plugin se chargent
lorsque le plugin est activé. Aujourd'hui, ces répertoires sont fusionnés dans le même chemin de
faible priorité que `skills.load.extraDirs`, de sorte qu'une Skill intégrée, gérée,
agent ou workspace portant le même nom les remplace.
Vous pouvez les filtrer via `metadata.openclaw.requires.config` sur l'entrée de configuration
du plugin. Voir [Plugins](/fr/tools/plugin) pour la découverte/configuration et [Tools](/fr/tools) pour la
surface d'outils que ces Skills enseignent.

## ClawHub (installation + synchronisation)

ClawHub est le registre public de Skills pour OpenClaw. Parcourez-le sur
[https://clawhub.ai](https://clawhub.ai). Utilisez les commandes natives `openclaw skills`
pour découvrir/installer/mettre à jour des Skills, ou la CLI séparée `clawhub` lorsque
vous avez besoin de workflows de publication/synchronisation.
Guide complet : [ClawHub](/fr/tools/clawhub).

Flux courants :

- Installer une Skill dans votre workspace :
  - `openclaw skills install <skill-slug>`
- Mettre à jour toutes les Skills installées :
  - `openclaw skills update --all`
- Synchroniser (analyser + publier les mises à jour) :
  - `clawhub sync --all`

La commande native `openclaw skills install` installe dans le répertoire `skills/` du workspace actif.
La CLI séparée `clawhub` installe également dans `./skills` sous votre
répertoire de travail actuel (ou se replie sur le workspace OpenClaw configuré).
OpenClaw le prendra en compte comme `<workspace>/skills` à la session suivante.

## Remarques de sécurité

- Traitez les Skills tierces comme du **code non fiable**. Lisez-les avant de les activer.
- Préférez des exécutions en sandbox pour les entrées non fiables et les outils risqués. Voir [Sandboxing](/fr/gateway/sandboxing).
- La découverte de Skills dans le workspace et les répertoires supplémentaires n'accepte que les racines de Skill et les fichiers `SKILL.md` dont le realpath résolu reste dans la racine configurée.
- Les installations de dépendances de Skills via Gateway (`skills.install`, onboarding, et l'interface des paramètres Skills) exécutent le scanner intégré de code dangereux avant d'exécuter les métadonnées d'installation. Les détections `critical` bloquent par défaut, sauf si l'appelant définit explicitement la surcharge dangereuse ; les détections suspectes n'émettent encore qu'un avertissement.
- `openclaw skills install <slug>` est différent : il télécharge un dossier de Skill ClawHub dans le workspace et n'utilise pas le chemin de métadonnées d'installation ci-dessus.
- `skills.entries.*.env` et `skills.entries.*.apiKey` injectent des secrets dans le processus **hôte**
  pour ce tour d'agent (pas dans le sandbox). Gardez les secrets hors des invites et des journaux.
- Pour un modèle de menace plus large et des checklists, voir [Security](/fr/gateway/security).

## Format (AgentSkills + compatible PI)

`SKILL.md` doit inclure au minimum :

```markdown
---
name: image-lab
description: Generate or edit images via a provider-backed image workflow
---
```

Remarques :

- Nous suivons la spécification AgentSkills pour la disposition/l'intention.
- L'analyseur utilisé par l'agent intégré prend en charge uniquement les clés de frontmatter **sur une seule ligne**.
- `metadata` doit être un **objet JSON sur une seule ligne**.
- Utilisez `{baseDir}` dans les instructions pour référencer le chemin du dossier de la Skill.
- Clés de frontmatter facultatives :
  - `homepage` — URL affichée comme « Website » dans l'interface Skills macOS (également prise en charge via `metadata.openclaw.homepage`).
  - `user-invocable` — `true|false` (par défaut : `true`). Quand `true`, la Skill est exposée comme commande slash utilisateur.
  - `disable-model-invocation` — `true|false` (par défaut : `false`). Quand `true`, la Skill est exclue de l'invite du modèle (elle reste disponible via invocation utilisateur).
  - `command-dispatch` — `tool` (facultatif). Lorsqu'il est défini sur `tool`, la commande slash contourne le modèle et répartit directement vers un outil.
  - `command-tool` — nom de l'outil à invoquer lorsque `command-dispatch: tool` est défini.
  - `command-arg-mode` — `raw` (par défaut). Pour la répartition vers un outil, transmet la chaîne brute d'arguments à l'outil (aucune analyse par le cœur).

    L'outil est invoqué avec les paramètres :
    `{ command: "<raw args>", commandName: "<slash command>", skillName: "<skill name>" }`.

## Filtrage (filtres au chargement)

OpenClaw **filtre les Skills au chargement** à l'aide de `metadata` (JSON sur une seule ligne) :

```markdown
---
name: image-lab
description: Generate or edit images via a provider-backed image workflow
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["uv"], "env": ["GEMINI_API_KEY"], "config": ["browser.enabled"] },
        "primaryEnv": "GEMINI_API_KEY",
      },
  }
---
```

Champs sous `metadata.openclaw` :

- `always: true` — inclure toujours la Skill (ignore les autres filtres).
- `emoji` — emoji facultatif utilisé par l'interface Skills macOS.
- `homepage` — URL facultative affichée comme « Website » dans l'interface Skills macOS.
- `os` — liste facultative de plateformes (`darwin`, `linux`, `win32`). Si elle est définie, la Skill n'est éligible que sur ces OS.
- `requires.bins` — liste ; chacun doit exister sur `PATH`.
- `requires.anyBins` — liste ; au moins un doit exister sur `PATH`.
- `requires.env` — liste ; la variable d'environnement doit exister **ou** être fournie dans la configuration.
- `requires.config` — liste de chemins `openclaw.json` qui doivent être truthy.
- `primaryEnv` — nom de variable d'environnement associé à `skills.entries.<name>.apiKey`.
- `install` — tableau facultatif de spécifications d'installation utilisé par l'interface Skills macOS (brew/node/go/uv/download).

Remarque sur le sandboxing :

- `requires.bins` est vérifié sur l'**hôte** au chargement de la Skill.
- Si un agent est dans un sandbox, le binaire doit aussi exister **dans le conteneur**.
  Installez-le via `agents.defaults.sandbox.docker.setupCommand` (ou une image personnalisée).
  `setupCommand` s'exécute une fois après la création du conteneur.
  Les installations de packages nécessitent aussi un accès réseau sortant, un système de fichiers racine accessible en écriture et un utilisateur root dans le sandbox.
  Exemple : la Skill `summarize` (`skills/summarize/SKILL.md`) a besoin de la CLI `summarize`
  dans le conteneur sandbox pour s'y exécuter.

Exemple d'installateur :

```markdown
---
name: gemini
description: Use Gemini CLI for coding assistance and Google search lookups.
metadata:
  {
    "openclaw":
      {
        "emoji": "♊️",
        "requires": { "bins": ["gemini"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "gemini-cli",
              "bins": ["gemini"],
              "label": "Install Gemini CLI (brew)",
            },
          ],
      },
  }
---
```

Remarques :

- Si plusieurs installateurs sont listés, la gateway choisit une **seule** option préférée (brew si disponible, sinon node).
- Si tous les installateurs sont de type `download`, OpenClaw liste chaque entrée pour que vous puissiez voir les artefacts disponibles.
- Les spécifications d'installation peuvent inclure `os: ["darwin"|"linux"|"win32"]` pour filtrer les options par plateforme.
- Les installations node respectent `skills.install.nodeManager` dans `openclaw.json` (par défaut : npm ; options : npm/pnpm/yarn/bun).
  Cela n'affecte que les **installations de Skills** ; l'exécution de la Gateway doit toujours être sur Node
  (Bun n'est pas recommandé pour WhatsApp/Telegram).
- La sélection d'installateur via Gateway est pilotée par les préférences, pas uniquement par node :
  lorsque les spécifications d'installation mélangent plusieurs types, OpenClaw préfère Homebrew lorsque
  `skills.install.preferBrew` est activé et que `brew` existe, puis `uv`, puis le
  gestionnaire node configuré, puis d'autres solutions de secours comme `go` ou `download`.
- Si toutes les spécifications d'installation sont `download`, OpenClaw affiche toutes les options de téléchargement
  au lieu de les réduire à un seul installateur préféré.
- Installations Go : si `go` est absent et que `brew` est disponible, la gateway installe d'abord Go via Homebrew et définit `GOBIN` sur le répertoire `bin` de Homebrew quand c'est possible.
- Installations par téléchargement : `url` (obligatoire), `archive` (`tar.gz` | `tar.bz2` | `zip`), `extract` (par défaut : auto lorsqu'une archive est détectée), `stripComponents`, `targetDir` (par défaut : `~/.openclaw/tools/<skillKey>`).

Si aucun `metadata.openclaw` n'est présent, la Skill est toujours éligible (sauf
si elle est désactivée dans la configuration ou bloquée par `skills.allowBundled` pour les Skills intégrées).

## Surcharges de configuration (`~/.openclaw/openclaw.json`)

Les Skills intégrées/gérées peuvent être activées/désactivées et recevoir des valeurs d'environnement :

```json5
{
  skills: {
    entries: {
      "image-lab": {
        enabled: true,
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" }, // ou chaîne en clair
        env: {
          GEMINI_API_KEY: "GEMINI_KEY_HERE",
        },
        config: {
          endpoint: "https://example.invalid",
          model: "nano-pro",
        },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

Remarque : si le nom de la Skill contient des traits d'union, mettez la clé entre guillemets (JSON5 autorise les clés entre guillemets).

Si vous voulez une génération/édition d'images standard dans OpenClaw lui-même, utilisez l'outil principal
`image_generate` avec `agents.defaults.imageGenerationModel` au lieu d'une
Skill intégrée. Les exemples de Skills ici concernent des workflows personnalisés ou tiers.

Pour l'analyse native d'images, utilisez l'outil `image` avec `agents.defaults.imageModel`.
Pour la génération/édition native d'images, utilisez `image_generate` avec
`agents.defaults.imageGenerationModel`. Si vous choisissez `openai/*`, `google/*`,
`fal/*` ou un autre modèle d'image spécifique à un provider, ajoutez aussi l'authentification/la clé API
de ce provider.

Les clés de configuration correspondent au **nom de la Skill** par défaut. Si une Skill définit
`metadata.openclaw.skillKey`, utilisez cette clé sous `skills.entries`.

Règles :

- `enabled: false` désactive la Skill même si elle est intégrée/installée.
- `env` : injecté **uniquement si** la variable n'est pas déjà définie dans le processus.
- `apiKey` : raccourci pratique pour les Skills qui déclarent `metadata.openclaw.primaryEnv`.
  Prend en charge une chaîne en clair ou un objet SecretRef (`{ source, provider, id }`).
- `config` : conteneur facultatif pour des champs personnalisés par Skill ; les clés personnalisées doivent s'y trouver.
- `allowBundled` : liste d'autorisation facultative pour les **Skills intégrées** uniquement. Si elle est définie, seules
  les Skills intégrées présentes dans la liste sont éligibles (les Skills gérées/workspace ne sont pas affectées).

## Injection d'environnement (par exécution d'agent)

Lorsqu'une exécution d'agent démarre, OpenClaw :

1. Lit les métadonnées de la Skill.
2. Applique toute valeur `skills.entries.<key>.env` ou `skills.entries.<key>.apiKey` à
   `process.env`.
3. Construit l'invite système avec les Skills **éligibles**.
4. Restaure l'environnement d'origine après la fin de l'exécution.

Cela est **limité à l'exécution de l'agent**, et non à un environnement shell global.

Pour le backend intégré `claude-cli`, OpenClaw matérialise également le même
instantané éligible comme plugin Claude Code temporaire et le transmet avec
`--plugin-dir`. Claude Code peut alors utiliser son résolveur natif de Skills tandis
qu'OpenClaw conserve la priorité, les listes d'autorisation par agent, le filtrage et
l'injection d'env/clés API `skills.entries.*`. Les autres backends CLI utilisent uniquement
le catalogue de l'invite.

## Instantané de session (performance)

OpenClaw capture un instantané des Skills éligibles **au démarrage d'une session** et réutilise cette liste pour les tours suivants de la même session. Les changements de Skills ou de configuration prennent effet à la prochaine nouvelle session.

Les Skills peuvent aussi s'actualiser en cours de session lorsque le watcher de Skills est activé ou lorsqu'un nouveau nœud distant éligible apparaît (voir ci-dessous). Considérez cela comme un **rechargement à chaud** : la liste actualisée est prise en compte au tour d'agent suivant.

Si la liste d'autorisation effective des Skills de l'agent change pour cette session, OpenClaw
actualise l'instantané afin que les Skills visibles restent alignées avec l'agent
actuel.

## Nœuds macOS distants (gateway Linux)

Si la Gateway s'exécute sur Linux mais qu'un **nœud macOS** est connecté **avec `system.run` autorisé** (la sécurité des approbations Exec n'est pas définie sur `deny`), OpenClaw peut traiter les Skills réservées à macOS comme éligibles lorsque les binaires requis sont présents sur ce nœud. L'agent doit exécuter ces Skills via l'outil `exec` avec `host=node`.

Cela repose sur le fait que le nœud signale la prise en charge de ses commandes et sur une sonde de binaire via `system.run`. Si le nœud macOS se déconnecte ensuite, les Skills restent visibles ; les invocations peuvent échouer jusqu'à la reconnexion du nœud.

## Watcher de Skills (actualisation automatique)

Par défaut, OpenClaw surveille les dossiers de Skills et met à jour l'instantané de Skills lorsque des fichiers `SKILL.md` changent. Configurez cela sous `skills.load` :

```json5
{
  skills: {
    load: {
      watch: true,
      watchDebounceMs: 250,
    },
  },
}
```

## Impact sur les jetons (liste des Skills)

Lorsque des Skills sont éligibles, OpenClaw injecte une liste XML compacte des Skills disponibles dans l'invite système (via `formatSkillsForPrompt` dans `pi-coding-agent`). Le coût est déterministe :

- **Surcharge de base (uniquement lorsqu'il y a ≥1 Skill)** : 195 caractères.
- **Par Skill** : 97 caractères + la longueur des valeurs XML-escaped `<name>`, `<description>` et `<location>`.

Formule (caractères) :

```
total = 195 + Σ (97 + len(name_escaped) + len(description_escaped) + len(location_escaped))
```

Remarques :

- L'échappement XML transforme `& < > " '` en entités (`&amp;`, `&lt;`, etc.), ce qui augmente la longueur.
- Le nombre de jetons varie selon le tokenizer du modèle. Une estimation grossière de type OpenAI est d'environ 4 caractères/jeton, donc **97 caractères ≈ 24 jetons** par Skill, plus la longueur réelle de vos champs.

## Cycle de vie des Skills gérées

OpenClaw livre un ensemble de base de Skills comme **Skills intégrées** avec l'installation
(package npm ou OpenClaw.app). `~/.openclaw/skills` existe pour les remplacements
locaux (par exemple, épingler/patcher une Skill sans modifier la copie
intégrée). Les Skills workspace appartiennent à l'utilisateur et remplacent les deux en cas de conflit de nom.

## Référence de configuration

Consultez [Configuration des Skills](/fr/tools/skills-config) pour le schéma complet de configuration.

## Vous cherchez plus de Skills ?

Parcourez [https://clawhub.ai](https://clawhub.ai).

---

## Voir aussi

- [Créer des Skills](/fr/tools/creating-skills) — créer des Skills personnalisées
- [Configuration des Skills](/fr/tools/skills-config) — référence de configuration des Skills
- [Commandes slash](/fr/tools/slash-commands) — toutes les commandes slash disponibles
- [Plugins](/fr/tools/plugin) — vue d'ensemble du système de plugin
