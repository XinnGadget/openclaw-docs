---
read_when:
    - Vous voulez une solution de repli fiable lorsque les fournisseurs d’API échouent.
    - Vous exécutez Codex CLI ou d’autres CLI d’IA locaux et souhaitez les réutiliser.
    - Vous souhaitez comprendre le pont local loopback MCP pour l’accès aux outils du backend CLI.
summary: 'Backends CLI : repli local du CLI d’IA avec pont d’outil MCP optionnel'
title: Backends CLI
x-i18n:
    generated_at: "2026-04-16T19:31:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: 381273532a8622bc4628000a6fb999712b12af08faade2b5f2b7ac4cc7d23efe
    source_path: gateway/cli-backends.md
    workflow: 15
---

# Backends CLI (runtime de repli)

OpenClaw peut exécuter des **CLI d’IA locaux** comme **solution de repli en texte seul** lorsque les fournisseurs d’API sont indisponibles, limités en débit ou temporairement défaillants. Cette approche est volontairement prudente :

- **Les outils OpenClaw ne sont pas injectés directement**, mais les backends avec `bundleMcp: true`
  peuvent recevoir des outils Gateway via un pont MCP en local loopback.
- **Streaming JSONL** pour les CLI qui le prennent en charge.
- **Les sessions sont prises en charge** (pour que les tours de suivi restent cohérents).
- **Les images peuvent être transmises** si le CLI accepte des chemins d’image.

Cela est conçu comme un **filet de sécurité** plutôt que comme un chemin principal. Utilisez-le lorsque vous
voulez des réponses texte « qui fonctionnent toujours » sans dépendre d’API externes.

Si vous voulez un runtime harness complet avec contrôles de session ACP, tâches en arrière-plan,
liaison thread/conversation et sessions de codage externes persistantes, utilisez
[ACP Agents](/fr/tools/acp-agents) à la place. Les backends CLI ne sont pas ACP.

## Démarrage rapide pour débutants

Vous pouvez utiliser Codex CLI **sans aucune configuration** (le Plugin OpenAI intégré
enregistre un backend par défaut) :

```bash
openclaw agent --message "hi" --model codex-cli/gpt-5.4
```

Si votre Gateway s’exécute sous launchd/systemd et que `PATH` est minimal, ajoutez simplement le
chemin de commande :

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "codex-cli": {
          command: "/opt/homebrew/bin/codex",
        },
      },
    },
  },
}
```

C’est tout. Aucune clé, aucune configuration d’authentification supplémentaire n’est nécessaire au-delà du CLI lui-même.

Si vous utilisez un backend CLI intégré comme **fournisseur de messages principal** sur un
hôte Gateway, OpenClaw charge désormais automatiquement le Plugin intégré propriétaire lorsque votre configuration
référence explicitement ce backend dans une référence de modèle ou sous
`agents.defaults.cliBackends`.

## Utilisation comme solution de repli

Ajoutez un backend CLI à votre liste de repli afin qu’il ne s’exécute que lorsque les modèles principaux échouent :

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["codex-cli/gpt-5.4"],
      },
      models: {
        "anthropic/claude-opus-4-6": { alias: "Opus" },
        "codex-cli/gpt-5.4": {},
      },
    },
  },
}
```

Remarques :

- Si vous utilisez `agents.defaults.models` (liste d’autorisation), vous devez aussi y inclure vos modèles de backend CLI.
- Si le fournisseur principal échoue (authentification, limites de débit, délais d’expiration), OpenClaw
  essaiera ensuite le backend CLI.

## Vue d’ensemble de la configuration

Tous les backends CLI se trouvent sous :

```
agents.defaults.cliBackends
```

Chaque entrée est indexée par un **id de fournisseur** (par exemple `codex-cli`, `my-cli`).
L’id du fournisseur devient la partie gauche de votre référence de modèle :

```
<provider>/<model>
```

### Exemple de configuration

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "codex-cli": {
          command: "/opt/homebrew/bin/codex",
        },
        "my-cli": {
          command: "my-cli",
          args: ["--json"],
          output: "json",
          input: "arg",
          modelArg: "--model",
          modelAliases: {
            "claude-opus-4-6": "opus",
            "claude-sonnet-4-6": "sonnet",
          },
          sessionArg: "--session",
          sessionMode: "existing",
          sessionIdFields: ["session_id", "conversation_id"],
          systemPromptArg: "--system",
          // Les CLI de style Codex peuvent pointer vers un fichier de prompt à la place :
          // systemPromptFileConfigArg: "-c",
          // systemPromptFileConfigKey: "model_instructions_file",
          systemPromptWhen: "first",
          imageArg: "--image",
          imageMode: "repeat",
          serialize: true,
        },
      },
    },
  },
}
```

## Fonctionnement

1. **Sélectionne un backend** en fonction du préfixe du fournisseur (`codex-cli/...`).
2. **Construit un prompt système** à l’aide du même prompt OpenClaw + contexte d’espace de travail.
3. **Exécute le CLI** avec un id de session (si pris en charge) afin que l’historique reste cohérent.
4. **Analyse la sortie** (JSON ou texte brut) et renvoie le texte final.
5. **Persiste les ids de session** par backend, afin que les suivis réutilisent la même session CLI.

<Note>
Le backend intégré Anthropic `claude-cli` est de nouveau pris en charge. Le personnel d’Anthropic
nous a indiqué que l’utilisation de Claude CLI dans le style OpenClaw est de nouveau autorisée, donc OpenClaw considère
l’utilisation de `claude -p` comme approuvée pour cette intégration, sauf si Anthropic publie
une nouvelle politique.
</Note>

Le backend intégré OpenAI `codex-cli` transmet le prompt système d’OpenClaw via
la surcharge de configuration `model_instructions_file` de Codex (`-c
model_instructions_file="..."`). Codex n’expose pas de drapeau de style Claude
`--append-system-prompt`, donc OpenClaw écrit le prompt assemblé dans un
fichier temporaire pour chaque nouvelle session Codex CLI.

Le backend intégré Anthropic `claude-cli` reçoit l’instantané des Skills OpenClaw
de deux façons : le catalogue compact de Skills OpenClaw dans le prompt système ajouté, et
un Plugin Claude Code temporaire transmis avec `--plugin-dir`. Le Plugin ne contient
que les Skills éligibles pour cet agent/cette session, afin que le résolveur de Skills natif de Claude Code
voie le même ensemble filtré que celui qu’OpenClaw annoncerait autrement dans
le prompt. Les surcharges de variables d’environnement/de clé API des Skills sont toujours appliquées par OpenClaw à l’environnement
du processus enfant pendant l’exécution.

## Sessions

- Si le CLI prend en charge les sessions, définissez `sessionArg` (par ex. `--session-id`) ou
  `sessionArgs` (espace réservé `{sessionId}`) lorsque l’id doit être inséré
  dans plusieurs drapeaux.
- Si le CLI utilise une **sous-commande de reprise** avec des drapeaux différents, définissez
  `resumeArgs` (remplace `args` lors de la reprise) et éventuellement `resumeOutput`
  (pour les reprises non JSON).
- `sessionMode` :
  - `always` : toujours envoyer un id de session (nouvel UUID si aucun n’est stocké).
  - `existing` : envoyer un id de session uniquement si un id a déjà été stocké.
  - `none` : ne jamais envoyer d’id de session.

Remarques sur la sérialisation :

- `serialize: true` conserve l’ordre des exécutions sur la même voie.
- La plupart des CLI sérialisent sur une voie de fournisseur.
- OpenClaw abandonne la réutilisation de session CLI stockée lorsque l’état d’authentification du backend change, y compris lors d’une reconnexion, d’une rotation de jeton ou d’un changement d’identifiant de profil d’authentification.

## Images (transmission directe)

Si votre CLI accepte des chemins d’image, définissez `imageArg` :

```json5
imageArg: "--image",
imageMode: "repeat"
```

OpenClaw écrira les images base64 dans des fichiers temporaires. Si `imageArg` est défini, ces
chemins sont transmis comme arguments du CLI. Si `imageArg` est absent, OpenClaw ajoute les
chemins de fichiers au prompt (injection de chemin), ce qui suffit pour les CLI qui chargent automatiquement
les fichiers locaux à partir de simples chemins.

## Entrées / sorties

- `output: "json"` (par défaut) essaie d’analyser le JSON et d’en extraire le texte + l’id de session.
- Pour la sortie JSON de Gemini CLI, OpenClaw lit le texte de réponse depuis `response` et
  l’usage depuis `stats` lorsque `usage` est absent ou vide.
- `output: "jsonl"` analyse les flux JSONL (par exemple Codex CLI `--json`) et extrait le message final de l’agent ainsi que les identifiants de session
  lorsqu’ils sont présents.
- `output: "text"` traite stdout comme la réponse finale.

Modes d’entrée :

- `input: "arg"` (par défaut) transmet le prompt comme dernier argument du CLI.
- `input: "stdin"` envoie le prompt via stdin.
- Si le prompt est très long et que `maxPromptArgChars` est défini, stdin est utilisé.

## Valeurs par défaut (possédées par le Plugin)

Le Plugin OpenAI intégré enregistre également une valeur par défaut pour `codex-cli` :

- `command: "codex"`
- `args: ["exec","--json","--color","never","--sandbox","workspace-write","--skip-git-repo-check"]`
- `resumeArgs: ["exec","resume","{sessionId}","-c","sandbox_mode=\"workspace-write\"","--skip-git-repo-check"]`
- `output: "jsonl"`
- `resumeOutput: "text"`
- `modelArg: "--model"`
- `imageArg: "--image"`
- `sessionMode: "existing"`

Le Plugin Google intégré enregistre également une valeur par défaut pour `google-gemini-cli` :

- `command: "gemini"`
- `args: ["--output-format", "json", "--prompt", "{prompt}"]`
- `resumeArgs: ["--resume", "{sessionId}", "--output-format", "json", "--prompt", "{prompt}"]`
- `imageArg: "@"`
- `imagePathScope: "workspace"`
- `modelArg: "--model"`
- `sessionMode: "existing"`
- `sessionIdFields: ["session_id", "sessionId"]`

Prérequis : le Gemini CLI local doit être installé et disponible comme
`gemini` dans `PATH` (`brew install gemini-cli` ou
`npm install -g @google/gemini-cli`).

Remarques sur le JSON de Gemini CLI :

- Le texte de réponse est lu depuis le champ JSON `response`.
- L’usage revient à `stats` lorsque `usage` est absent ou vide.
- `stats.cached` est normalisé en `cacheRead` OpenClaw.
- Si `stats.input` est absent, OpenClaw dérive les jetons d’entrée à partir de
  `stats.input_tokens - stats.cached`.

Ne surchargez que si nécessaire (cas courant : chemin `command` absolu).

## Valeurs par défaut possédées par le Plugin

Les valeurs par défaut des backends CLI font désormais partie de la surface du Plugin :

- Les Plugins les enregistrent avec `api.registerCliBackend(...)`.
- Le `id` du backend devient le préfixe du fournisseur dans les références de modèle.
- La configuration utilisateur dans `agents.defaults.cliBackends.<id>` surcharge toujours la valeur par défaut du Plugin.
- Le nettoyage de configuration spécifique au backend reste possédé par le Plugin via le hook optionnel
  `normalizeConfig`.

Les Plugins qui ont besoin de petites adaptations de compatibilité de prompt/message peuvent déclarer
des transformations de texte bidirectionnelles sans remplacer un fournisseur ni un backend CLI :

```typescript
api.registerTextTransforms({
  input: [
    { from: /red basket/g, to: "blue basket" },
    { from: /paper ticket/g, to: "digital ticket" },
    { from: /left shelf/g, to: "right shelf" },
  ],
  output: [
    { from: /blue basket/g, to: "red basket" },
    { from: /digital ticket/g, to: "paper ticket" },
    { from: /right shelf/g, to: "left shelf" },
  ],
});
```

`input` réécrit le prompt système et le prompt utilisateur transmis au CLI. `output`
réécrit les deltas assistant streamés et le texte final analysé avant qu’OpenClaw ne gère
ses propres marqueurs de contrôle et la livraison au canal.

Pour les CLI qui émettent du JSONL compatible avec le stream-json de Claude Code, définissez
`jsonlDialect: "claude-stream-json"` dans la configuration de ce backend.

## Overlays bundle MCP

Les backends CLI ne reçoivent **pas** directement les appels d’outils OpenClaw, mais un backend peut
choisir d’utiliser un overlay de configuration MCP généré avec `bundleMcp: true`.

Comportement intégré actuel :

- `claude-cli` : fichier de configuration MCP strict généré
- `codex-cli` : surcharges de configuration en ligne pour `mcp_servers`
- `google-gemini-cli` : fichier de paramètres système Gemini généré

Lorsque bundle MCP est activé, OpenClaw :

- lance un serveur MCP HTTP en local loopback qui expose les outils Gateway au processus CLI
- authentifie le pont avec un jeton par session (`OPENCLAW_MCP_TOKEN`)
- limite l’accès aux outils à la session, au compte et au contexte de canal actuels
- charge les serveurs bundle-MCP activés pour l’espace de travail actuel
- les fusionne avec toute forme existante de configuration/paramètres MCP du backend
- réécrit la configuration de lancement en utilisant le mode d’intégration possédé par le backend depuis l’extension propriétaire

Si aucun serveur MCP n’est activé, OpenClaw injecte tout de même une configuration stricte lorsqu’un
backend choisit d’utiliser bundle MCP afin que les exécutions en arrière-plan restent isolées.

## Limites

- **Pas d’appels directs aux outils OpenClaw.** OpenClaw n’injecte pas d’appels d’outils dans
  le protocole du backend CLI. Les backends ne voient les outils Gateway que lorsqu’ils choisissent
  d’utiliser `bundleMcp: true`.
- **Le streaming est spécifique au backend.** Certains backends diffusent du JSONL en flux ; d’autres mettent en tampon
  jusqu’à la fin.
- **Les sorties structurées** dépendent du format JSON du CLI.
- **Les sessions Codex CLI** reprennent via une sortie texte (sans JSONL), ce qui est moins
  structuré que l’exécution initiale `--json`. Les sessions OpenClaw continuent de fonctionner
  normalement.

## Dépannage

- **CLI introuvable** : définissez `command` sur un chemin complet.
- **Nom de modèle incorrect** : utilisez `modelAliases` pour mapper `provider/model` → modèle CLI.
- **Pas de continuité de session** : assurez-vous que `sessionArg` est défini et que `sessionMode` n’est pas
  `none` (Codex CLI ne peut actuellement pas reprendre avec une sortie JSON).
- **Images ignorées** : définissez `imageArg` (et vérifiez que le CLI prend en charge les chemins de fichiers).
