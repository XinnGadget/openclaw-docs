---
read_when:
    - Utilisation ou configuration des commandes de chat
    - Débogage du routage ou des autorisations des commandes
summary: 'Slash commands : texte vs natif, configuration et commandes prises en charge'
title: Slash commands
x-i18n:
    generated_at: "2026-04-12T23:33:24Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9ef6f54500fa2ce3b873a8398d6179a0882b8bf6fba38f61146c64671055505e
    source_path: tools/slash-commands.md
    workflow: 15
---

# Slash commands

Les commandes sont gérées par le Gateway. La plupart des commandes doivent être envoyées comme un message **autonome** qui commence par `/`.
La commande de chat bash réservée à l’hôte utilise `! <cmd>` (avec `/bash <cmd>` comme alias).

Il existe deux systèmes liés :

- **Commands** : messages autonomes `/...`.
- **Directives** : `/think`, `/fast`, `/verbose`, `/trace`, `/reasoning`, `/elevated`, `/exec`, `/model`, `/queue`.
  - Les directives sont retirées du message avant que le modèle ne le voie.
  - Dans les messages de chat normaux (pas uniquement des directives), elles sont traitées comme des « indications inline » et **ne** persistent **pas** les paramètres de session.
  - Dans les messages composés uniquement de directives (le message ne contient que des directives), elles persistent dans la session et répondent par un accusé de réception.
  - Les directives ne sont appliquées que pour les **expéditeurs autorisés**. Si `commands.allowFrom` est défini, c’est la seule
    liste d’autorisations utilisée ; sinon, l’autorisation provient des listes d’autorisations/appairages des canaux ainsi que de `commands.useAccessGroups`.
    Pour les expéditeurs non autorisés, les directives sont traitées comme du texte ordinaire.

Il existe aussi quelques **raccourcis inline** (expéditeurs autorisés/en liste d’autorisations uniquement) : `/help`, `/commands`, `/status`, `/whoami` (`/id`).
Ils s’exécutent immédiatement, sont retirés avant que le modèle ne voie le message, et le texte restant continue dans le flux normal.

## Configuration

```json5
{
  commands: {
    native: "auto",
    nativeSkills: "auto",
    text: true,
    bash: false,
    bashForegroundMs: 2000,
    config: false,
    mcp: false,
    plugins: false,
    debug: false,
    restart: true,
    ownerAllowFrom: ["discord:123456789012345678"],
    ownerDisplay: "raw",
    ownerDisplaySecret: "${OWNER_ID_HASH_SECRET}",
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    useAccessGroups: true,
  },
}
```

- `commands.text` (par défaut `true`) active l’analyse de `/...` dans les messages de chat.
  - Sur les surfaces sans commandes natives (WhatsApp/WebChat/Signal/iMessage/Google Chat/Microsoft Teams), les commandes texte fonctionnent quand même même si vous définissez cette valeur sur `false`.
- `commands.native` (par défaut `"auto"`) enregistre les commandes natives.
  - Auto : activé pour Discord/Telegram ; désactivé pour Slack (jusqu’à ce que vous ajoutiez des slash commands) ; ignoré pour les fournisseurs sans prise en charge native.
  - Définissez `channels.discord.commands.native`, `channels.telegram.commands.native` ou `channels.slack.commands.native` pour remplacer ce comportement par fournisseur (booléen ou `"auto"`).
  - `false` efface les commandes précédemment enregistrées sur Discord/Telegram au démarrage. Les commandes Slack sont gérées dans l’application Slack et ne sont pas supprimées automatiquement.
- `commands.nativeSkills` (par défaut `"auto"`) enregistre les commandes **skill** nativement lorsque c’est pris en charge.
  - Auto : activé pour Discord/Telegram ; désactivé pour Slack (Slack exige de créer une slash command par skill).
  - Définissez `channels.discord.commands.nativeSkills`, `channels.telegram.commands.nativeSkills` ou `channels.slack.commands.nativeSkills` pour remplacer ce comportement par fournisseur (booléen ou `"auto"`).
- `commands.bash` (par défaut `false`) active `! <cmd>` pour exécuter des commandes shell sur l’hôte (`/bash <cmd>` est un alias ; nécessite les listes d’autorisations `tools.elevated`).
- `commands.bashForegroundMs` (par défaut `2000`) contrôle combien de temps bash attend avant de passer en mode arrière-plan (`0` passe immédiatement en arrière-plan).
- `commands.config` (par défaut `false`) active `/config` (lecture/écriture de `openclaw.json`).
- `commands.mcp` (par défaut `false`) active `/mcp` (lecture/écriture de la configuration MCP gérée par OpenClaw sous `mcp.servers`).
- `commands.plugins` (par défaut `false`) active `/plugins` (découverte/statut des plugins ainsi que contrôles d’installation + activation/désactivation).
- `commands.debug` (par défaut `false`) active `/debug` (remplacements à l’exécution uniquement).
- `commands.restart` (par défaut `true`) active `/restart` ainsi que les actions d’outil de redémarrage du gateway.
- `commands.ownerAllowFrom` (facultatif) définit la liste d’autorisations explicite du propriétaire pour les surfaces de commande/d’outil réservées au propriétaire. Elle est distincte de `commands.allowFrom`.
- `commands.ownerDisplay` contrôle la manière dont les ID du propriétaire apparaissent dans le prompt système : `raw` ou `hash`.
- `commands.ownerDisplaySecret` définit facultativement le secret HMAC utilisé lorsque `commands.ownerDisplay="hash"`.
- `commands.allowFrom` (facultatif) définit une liste d’autorisations par fournisseur pour l’autorisation des commandes. Lorsqu’elle est configurée, c’est la
  seule source d’autorisation pour les commandes et directives (les listes d’autorisations/appairages des canaux et `commands.useAccessGroups`
  sont ignorés). Utilisez `"*"` pour une valeur par défaut globale ; les clés spécifiques au fournisseur la remplacent.
- `commands.useAccessGroups` (par défaut `true`) applique les listes d’autorisations/politiques pour les commandes lorsque `commands.allowFrom` n’est pas défini.

## Liste des commandes

Source de vérité actuelle :

- les commandes intégrées du noyau proviennent de `src/auto-reply/commands-registry.shared.ts`
- les commandes dock générées proviennent de `src/auto-reply/commands-registry.data.ts`
- les commandes de Plugin proviennent des appels `registerCommand()` des plugins
- la disponibilité réelle sur votre gateway dépend toujours des drapeaux de configuration, de la surface du canal et des plugins installés/activés

### Commandes intégrées du noyau

Commandes intégrées disponibles aujourd’hui :

- `/new [model]` démarre une nouvelle session ; `/reset` est l’alias de réinitialisation.
- `/compact [instructions]` compacte le contexte de session. Voir [/concepts/compaction](/fr/concepts/compaction).
- `/stop` interrompt l’exécution en cours.
- `/session idle <duration|off>` et `/session max-age <duration|off>` gèrent l’expiration de liaison au fil.
- `/think <off|minimal|low|medium|high|xhigh>` définit le niveau de réflexion. Alias : `/thinking`, `/t`.
- `/verbose on|off|full` active ou désactive la sortie verbeuse. Alias : `/v`.
- `/trace on|off` active ou désactive la sortie de trace du Plugin pour la session en cours.
- `/fast [status|on|off]` affiche ou définit le mode rapide.
- `/reasoning [on|off|stream]` active ou désactive la visibilité du raisonnement. Alias : `/reason`.
- `/elevated [on|off|ask|full]` active ou désactive le mode elevated. Alias : `/elev`.
- `/exec host=<auto|sandbox|gateway|node> security=<deny|allowlist|full> ask=<off|on-miss|always> node=<id>` affiche ou définit les valeurs par défaut d’exécution.
- `/model [name|#|status]` affiche ou définit le modèle.
- `/models [provider] [page] [limit=<n>|size=<n>|all]` liste les fournisseurs ou les modèles d’un fournisseur.
- `/queue <mode>` gère le comportement de la file (`steer`, `interrupt`, `followup`, `collect`, `steer-backlog`) ainsi que des options comme `debounce:2s cap:25 drop:summarize`.
- `/help` affiche le résumé d’aide court.
- `/commands` affiche le catalogue de commandes généré.
- `/tools [compact|verbose]` affiche ce que l’agent actuel peut utiliser maintenant.
- `/status` affiche l’état d’exécution, y compris l’utilisation/le quota du fournisseur lorsque disponible.
- `/tasks` liste les tâches d’arrière-plan actives/récentes pour la session en cours.
- `/context [list|detail|json]` explique comment le contexte est assemblé.
- `/export-session [path]` exporte la session en cours vers HTML. Alias : `/export`.
- `/whoami` affiche votre ID d’expéditeur. Alias : `/id`.
- `/skill <name> [input]` exécute un skill par son nom.
- `/allowlist [list|add|remove] ...` gère les entrées de liste d’autorisations. Texte uniquement.
- `/approve <id> <decision>` résout les demandes d’approbation d’exécution.
- `/btw <question>` pose une question annexe sans modifier le contexte futur de la session. Voir [/tools/btw](/fr/tools/btw).
- `/subagents list|kill|log|info|send|steer|spawn` gère les exécutions de sous-agents pour la session en cours.
- `/acp spawn|cancel|steer|close|sessions|status|set-mode|set|cwd|permissions|timeout|model|reset-options|doctor|install|help` gère les sessions ACP et les options d’exécution.
- `/focus <target>` lie le fil Discord actuel ou le topic/conversation Telegram à une cible de session.
- `/unfocus` supprime la liaison actuelle.
- `/agents` liste les agents liés à des fils pour la session en cours.
- `/kill <id|#|all>` interrompt un ou tous les sous-agents en cours d’exécution.
- `/steer <id|#> <message>` envoie une instruction de pilotage à un sous-agent en cours d’exécution. Alias : `/tell`.
- `/config show|get|set|unset` lit ou écrit `openclaw.json`. Réservé au propriétaire. Nécessite `commands.config: true`.
- `/mcp show|get|set|unset` lit ou écrit la configuration de serveur MCP gérée par OpenClaw sous `mcp.servers`. Réservé au propriétaire. Nécessite `commands.mcp: true`.
- `/plugins list|inspect|show|get|install|enable|disable` inspecte ou modifie l’état des plugins. `/plugin` est un alias. Écriture réservée au propriétaire. Nécessite `commands.plugins: true`.
- `/debug show|set|unset|reset` gère les remplacements de configuration à l’exécution uniquement. Réservé au propriétaire. Nécessite `commands.debug: true`.
- `/usage off|tokens|full|cost` contrôle le pied de page d’utilisation par réponse ou affiche un résumé local des coûts.
- `/tts on|off|status|provider|limit|summary|audio|help` contrôle le TTS. Voir [/tools/tts](/fr/tools/tts).
- `/restart` redémarre OpenClaw lorsqu’il est activé. Par défaut : activé ; définissez `commands.restart: false` pour le désactiver.
- `/activation mention|always` définit le mode d’activation des groupes.
- `/send on|off|inherit` définit la politique d’envoi. Réservé au propriétaire.
- `/bash <command>` exécute une commande shell sur l’hôte. Texte uniquement. Alias : `! <command>`. Nécessite `commands.bash: true` ainsi que les listes d’autorisations `tools.elevated`.
- `!poll [sessionId]` vérifie une tâche bash en arrière-plan.
- `!stop [sessionId]` arrête une tâche bash en arrière-plan.

### Commandes dock générées

Les commandes dock sont générées à partir de plugins de canal avec prise en charge des commandes natives. Ensemble intégré actuel :

- `/dock-discord` (alias : `/dock_discord`)
- `/dock-mattermost` (alias : `/dock_mattermost`)
- `/dock-slack` (alias : `/dock_slack`)
- `/dock-telegram` (alias : `/dock_telegram`)

### Commandes de Plugin intégrées

Les plugins intégrés peuvent ajouter davantage de slash commands. Commandes intégrées actuelles dans ce dépôt :

- `/dreaming [on|off|status|help]` active ou désactive le Dreaming de mémoire. Voir [Dreaming](/fr/concepts/dreaming).
- `/pair [qr|status|pending|approve|cleanup|notify]` gère le flux d’appairage/de configuration des appareils. Voir [Pairing](/fr/channels/pairing).
- `/phone status|arm <camera|screen|writes|all> [duration]|disarm` arme temporairement des commandes node de téléphone à haut risque.
- `/voice status|list [limit]|set <voiceId|name>` gère la configuration de voix Talk. Sur Discord, le nom de la commande native est `/talkvoice`.
- `/card ...` envoie des préréglages de cartes enrichies LINE. Voir [LINE](/fr/channels/line).
- `/codex status|models|threads|resume|compact|review|account|mcp|skills` inspecte et contrôle le harnais app-server Codex intégré. Voir [Codex Harness](/fr/plugins/codex-harness).
- Commandes réservées à QQBot :
  - `/bot-ping`
  - `/bot-version`
  - `/bot-help`
  - `/bot-upgrade`
  - `/bot-logs`

### Commandes Skills dynamiques

Les Skills invocables par l’utilisateur sont aussi exposés comme slash commands :

- `/skill <name> [input]` fonctionne toujours comme point d’entrée générique.
- les Skills peuvent aussi apparaître comme commandes directes telles que `/prose` lorsque le skill/le Plugin les enregistre.
- l’enregistrement natif des commandes skill est contrôlé par `commands.nativeSkills` et `channels.<provider>.commands.nativeSkills`.

Remarques :

- Les commandes acceptent un `:` facultatif entre la commande et les arguments (par ex. `/think: high`, `/send: on`, `/help:`).
- `/new <model>` accepte un alias de modèle, `provider/model` ou un nom de fournisseur (correspondance approximative) ; en l’absence de correspondance, le texte est traité comme corps du message.
- Pour la ventilation complète de l’utilisation par fournisseur, utilisez `openclaw status --usage`.
- `/allowlist add|remove` nécessite `commands.config=true` et respecte `configWrites` du canal.
- Dans les canaux à comptes multiples, les commandes `/allowlist --account <id>` orientées configuration et `/config set channels.<provider>.accounts.<id>...` respectent aussi `configWrites` du compte cible.
- `/usage` contrôle le pied de page d’utilisation par réponse ; `/usage cost` affiche un résumé local des coûts à partir des journaux de session OpenClaw.
- `/restart` est activé par défaut ; définissez `commands.restart: false` pour le désactiver.
- `/plugins install <spec>` accepte les mêmes spécifications de Plugin que `openclaw plugins install` : chemin/archive local, paquet npm ou `clawhub:<pkg>`.
- `/plugins enable|disable` met à jour la configuration du Plugin et peut demander un redémarrage.
- Commande native réservée à Discord : `/vc join|leave|status` contrôle les canaux vocaux (nécessite `channels.discord.voice` et des commandes natives ; indisponible en texte).
- Les commandes de liaison de fil Discord (`/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age`) exigent que les liaisons de fil effectives soient activées (`session.threadBindings.enabled` et/ou `channels.discord.threadBindings.enabled`).
- Référence de commande ACP et comportement d’exécution : [ACP Agents](/fr/tools/acp-agents).
- `/verbose` est destiné au débogage et à une visibilité supplémentaire ; laissez-le **désactivé** en usage normal.
- `/trace` est plus ciblé que `/verbose` : il ne révèle que les lignes de trace/débogage appartenant au Plugin et garde désactivé le bavardage verbeux normal des outils.
- `/fast on|off` persiste un remplacement de session. Utilisez l’option `inherit` de l’interface Sessions pour l’effacer et revenir aux valeurs par défaut de la configuration.
- `/fast` est spécifique au fournisseur : OpenAI/OpenAI Codex le mappe vers `service_tier=priority` sur les points de terminaison Responses natifs, tandis que les requêtes Anthropic publiques directes, y compris le trafic authentifié par OAuth envoyé à `api.anthropic.com`, le mappent vers `service_tier=auto` ou `standard_only`. Voir [OpenAI](/fr/providers/openai) et [Anthropic](/fr/providers/anthropic).
- Les résumés d’échec des outils sont toujours affichés lorsque c’est pertinent, mais le texte détaillé des échecs n’est inclus que lorsque `/verbose` est `on` ou `full`.
- `/reasoning`, `/verbose` et `/trace` sont risqués dans les contextes de groupe : ils peuvent révéler un raisonnement interne, des sorties d’outils ou des diagnostics de Plugin que vous n’aviez pas l’intention d’exposer. Préférez les laisser désactivés, surtout dans les discussions de groupe.
- `/model` persiste immédiatement le nouveau modèle de session.
- Si l’agent est inactif, l’exécution suivante l’utilise immédiatement.
- Si une exécution est déjà active, OpenClaw marque un basculement à chaud comme en attente et ne redémarre dans le nouveau modèle qu’à un point de reprise propre.
- Si l’activité des outils ou la sortie de réponse a déjà commencé, le basculement en attente peut rester en file jusqu’à une opportunité de reprise ultérieure ou jusqu’au prochain tour utilisateur.
- **Chemin rapide :** les messages ne contenant qu’une commande provenant d’expéditeurs en liste d’autorisations sont traités immédiatement (contournent la file + le modèle).
- **Exigence de mention dans les groupes :** les messages ne contenant qu’une commande provenant d’expéditeurs en liste d’autorisations contournent les exigences de mention.
- **Raccourcis inline (expéditeurs en liste d’autorisations uniquement) :** certaines commandes fonctionnent aussi lorsqu’elles sont intégrées dans un message normal et sont retirées avant que le modèle ne voie le texte restant.
  - Exemple : `hey /status` déclenche une réponse de statut, et le texte restant continue dans le flux normal.
- Actuellement : `/help`, `/commands`, `/status`, `/whoami` (`/id`).
- Les messages ne contenant qu’une commande et provenant d’expéditeurs non autorisés sont silencieusement ignorés, et les jetons inline `/...` sont traités comme du texte ordinaire.
- **Commandes Skills :** les Skills `user-invocable` sont exposés comme slash commands. Les noms sont normalisés en `a-z0-9_` (32 caractères max) ; les collisions reçoivent des suffixes numériques (par ex. `_2`).
  - `/skill <name> [input]` exécute un skill par son nom (utile lorsque les limites de commandes natives empêchent les commandes par skill).
  - Par défaut, les commandes skill sont transmises au modèle comme une requête normale.
  - Les Skills peuvent éventuellement déclarer `command-dispatch: tool` pour router la commande directement vers un outil (déterministe, sans modèle).
  - Exemple : `/prose` (Plugin OpenProse) — voir [OpenProse](/fr/prose).
- **Arguments de commandes natives :** Discord utilise l’autocomplétion pour les options dynamiques (et des menus à boutons lorsque vous omettez des arguments requis). Telegram et Slack affichent un menu à boutons lorsqu’une commande prend en charge des choix et que vous omettez l’argument.

## `/tools`

`/tools` répond à une question d’exécution, pas à une question de configuration : **ce que cet agent peut utiliser maintenant dans
cette conversation**.

- Le `/tools` par défaut est compact et optimisé pour une lecture rapide.
- `/tools verbose` ajoute de courtes descriptions.
- Les surfaces de commandes natives qui prennent en charge les arguments exposent le même changement de mode `compact|verbose`.
- Les résultats sont limités à la session, donc changer d’agent, de canal, de fil, d’autorisation d’expéditeur ou de modèle peut
  modifier la sortie.
- `/tools` inclut les outils réellement accessibles à l’exécution, y compris les outils du noyau, les outils de Plugin connectés et les outils propres au canal.

Pour modifier les profils et les remplacements, utilisez le panneau Tools de la Control UI ou les surfaces de configuration/catalogue
au lieu de traiter `/tools` comme un catalogue statique.

## Surfaces d’utilisation (ce qui s’affiche où)

- **Utilisation/quota du fournisseur** (exemple : « Claude 80 % restants ») apparaît dans `/status` pour le fournisseur du modèle actuel lorsque le suivi d’utilisation est activé. OpenClaw normalise les fenêtres des fournisseurs en `% restants` ; pour MiniMax, les champs de pourcentage exprimant uniquement le restant sont inversés avant affichage, et les réponses `model_remains` privilégient l’entrée du modèle de chat plus un libellé de plan étiqueté par modèle.
- Les **lignes tokens/cache** dans `/status` peuvent revenir à la dernière entrée d’utilisation de transcription lorsque l’instantané de session en direct est pauvre. Les valeurs en direct non nulles existantes restent prioritaires, et le repli sur la transcription peut aussi récupérer le libellé du modèle d’exécution actif ainsi qu’un total orienté prompt plus grand lorsque les totaux stockés sont absents ou plus petits.
- **Tokens/coût par réponse** est contrôlé par `/usage off|tokens|full` (ajouté aux réponses normales).
- `/model status` concerne les **modèles/l’authentification/les points de terminaison**, pas l’utilisation.

## Sélection de modèle (`/model`)

`/model` est implémenté comme une directive.

Exemples :

```
/model
/model list
/model 3
/model openai/gpt-5.4
/model opus@anthropic:default
/model status
```

Remarques :

- `/model` et `/model list` affichent un sélecteur compact numéroté (famille de modèles + fournisseurs disponibles).
- Sur Discord, `/model` et `/models` ouvrent un sélecteur interactif avec menus déroulants de fournisseur et de modèle plus une étape Submit.
- `/model <#>` sélectionne à partir de ce sélecteur (et préfère le fournisseur actuel lorsque c’est possible).
- `/model status` affiche la vue détaillée, y compris le point de terminaison configuré du fournisseur (`baseUrl`) et le mode API (`api`) lorsqu’ils sont disponibles.

## Remplacements de débogage

`/debug` vous permet de définir des remplacements de configuration **à l’exécution uniquement** (en mémoire, pas sur disque). Réservé au propriétaire. Désactivé par défaut ; activez-le avec `commands.debug: true`.

Exemples :

```
/debug show
/debug set messages.responsePrefix="[openclaw]"
/debug set channels.whatsapp.allowFrom=["+1555","+4477"]
/debug unset messages.responsePrefix
/debug reset
```

Remarques :

- Les remplacements s’appliquent immédiatement aux nouvelles lectures de configuration, mais **n’écrivent pas** dans `openclaw.json`.
- Utilisez `/debug reset` pour effacer tous les remplacements et revenir à la configuration sur disque.

## Sortie de trace du Plugin

`/trace` vous permet d’activer ou désactiver les **lignes de trace/débogage de Plugin limitées à la session** sans activer le mode verbeux complet.

Exemples :

```text
/trace
/trace on
/trace off
```

Remarques :

- `/trace` sans argument affiche l’état actuel de la trace de session.
- `/trace on` active les lignes de trace du Plugin pour la session en cours.
- `/trace off` les désactive à nouveau.
- Les lignes de trace du Plugin peuvent apparaître dans `/status` et sous forme de message de diagnostic de suivi après la réponse normale de l’assistant.
- `/trace` ne remplace pas `/debug` ; `/debug` gère toujours les remplacements de configuration à l’exécution uniquement.
- `/trace` ne remplace pas `/verbose` ; la sortie verbeuse normale des outils/statuts relève toujours de `/verbose`.

## Mises à jour de configuration

`/config` écrit dans votre configuration sur disque (`openclaw.json`). Réservé au propriétaire. Désactivé par défaut ; activez-le avec `commands.config: true`.

Exemples :

```
/config show
/config show messages.responsePrefix
/config get messages.responsePrefix
/config set messages.responsePrefix="[openclaw]"
/config unset messages.responsePrefix
```

Remarques :

- La configuration est validée avant écriture ; les changements invalides sont rejetés.
- Les mises à jour `/config` persistent après redémarrage.

## Mises à jour MCP

`/mcp` écrit les définitions de serveurs MCP gérées par OpenClaw sous `mcp.servers`. Réservé au propriétaire. Désactivé par défaut ; activez-le avec `commands.mcp: true`.

Exemples :

```text
/mcp show
/mcp show context7
/mcp set context7={"command":"uvx","args":["context7-mcp"]}
/mcp unset context7
```

Remarques :

- `/mcp` stocke la configuration dans la configuration OpenClaw, pas dans des paramètres de projet propres à Pi.
- Les adaptateurs d’exécution décident quels transports sont réellement exécutables.

## Mises à jour de plugins

`/plugins` permet aux opérateurs d’inspecter les plugins découverts et de basculer leur activation dans la configuration. Les flux en lecture seule peuvent utiliser `/plugin` comme alias. Désactivé par défaut ; activez-le avec `commands.plugins: true`.

Exemples :

```text
/plugins
/plugins list
/plugin show context7
/plugins enable context7
/plugins disable context7
```

Remarques :

- `/plugins list` et `/plugins show` utilisent une vraie découverte des plugins sur l’espace de travail actuel ainsi que sur la configuration sur disque.
- `/plugins enable|disable` met à jour uniquement la configuration du Plugin ; cela n’installe ni ne désinstalle les plugins.
- Après des changements d’activation/désactivation, redémarrez le gateway pour les appliquer.

## Notes sur les surfaces

- **Les commandes texte** s’exécutent dans la session de chat normale (les messages privés partagent `main`, les groupes ont leur propre session).
- **Les commandes natives** utilisent des sessions isolées :
  - Discord : `agent:<agentId>:discord:slash:<userId>`
  - Slack : `agent:<agentId>:slack:slash:<userId>` (préfixe configurable via `channels.slack.slashCommand.sessionPrefix`)
  - Telegram : `telegram:slash:<userId>` (cible la session de chat via `CommandTargetSessionKey`)
- **`/stop`** cible la session de chat active afin de pouvoir interrompre l’exécution en cours.
- **Slack :** `channels.slack.slashCommand` est toujours pris en charge pour une commande unique de type `/openclaw`. Si vous activez `commands.native`, vous devez créer une slash command Slack par commande intégrée (mêmes noms que `/help`). Les menus d’arguments de commandes pour Slack sont livrés sous forme de boutons Block Kit éphémères.
  - Exception native Slack : enregistrez `/agentstatus` (pas `/status`) car Slack réserve `/status`. Le texte `/status` fonctionne toujours dans les messages Slack.

## Questions annexes BTW

`/btw` est une **question annexe** rapide à propos de la session en cours.

Contrairement au chat normal :

- il utilise la session en cours comme contexte de fond,
- il s’exécute comme un appel ponctuel séparé **sans outils**,
- il ne modifie pas le contexte futur de la session,
- il n’est pas écrit dans l’historique de transcription,
- il est livré comme résultat annexe en direct au lieu d’un message normal de l’assistant.

Cela rend `/btw` utile lorsque vous voulez une clarification temporaire pendant que la tâche principale
continue.

Exemple :

```text
/btw qu’est-ce qu’on est en train de faire en ce moment ?
```

Voir [BTW Side Questions](/fr/tools/btw) pour le comportement complet et les détails
de l’expérience utilisateur côté client.
