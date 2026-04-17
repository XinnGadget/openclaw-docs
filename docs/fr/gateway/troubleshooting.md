---
read_when:
    - Le centre de dépannage vous a orienté ici pour un diagnostic plus approfondi
    - Vous avez besoin de sections de guide basées sur les symptômes, stables, avec des commandes exactes
summary: Guide de dépannage approfondi pour la gateway, les canaux, l’automatisation, les nœuds et le navigateur
title: Dépannage
x-i18n:
    generated_at: "2026-04-11T02:45:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7ef2faccba26ede307861504043a6415bc1f12dc64407771106f63ddc5b107f5
    source_path: gateway/troubleshooting.md
    workflow: 15
---

# Dépannage de la gateway

Cette page est le guide approfondi.
Commencez par [/help/troubleshooting](/fr/help/troubleshooting) si vous voulez d’abord le flux de triage rapide.

## Échelle de commandes

Exécutez-les d’abord, dans cet ordre :

```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
openclaw channels status --probe
```

Signaux attendus d’un état sain :

- `openclaw gateway status` affiche `Runtime: running` et `RPC probe: ok`.
- `openclaw doctor` ne signale aucun problème bloquant de configuration/service.
- `openclaw channels status --probe` affiche l’état de transport en direct par compte et,
  lorsque c’est pris en charge, des résultats de sonde/audit tels que `works` ou `audit ok`.

## Anthropic 429 : usage supplémentaire requis pour un long contexte

Utilisez cette section lorsque les journaux/erreurs incluent :
`HTTP 429: rate_limit_error: Extra usage is required for long context requests`.

```bash
openclaw logs --follow
openclaw models status
openclaw config get agents.defaults.models
```

Recherchez :

- Le modèle Anthropic Opus/Sonnet sélectionné a `params.context1m: true`.
- L’identifiant Anthropic actuel n’est pas éligible à l’usage en long contexte.
- Les requêtes échouent uniquement sur les longues sessions/exécutions de modèle qui nécessitent la voie bêta 1M.

Options de correction :

1. Désactivez `context1m` pour ce modèle afin de revenir à la fenêtre de contexte normale.
2. Utilisez un identifiant Anthropic éligible aux requêtes en long contexte, ou passez à une clé API Anthropic.
3. Configurez des modèles de secours afin que les exécutions continuent lorsque les requêtes Anthropic en long contexte sont rejetées.

Voir aussi :

- [/providers/anthropic](/fr/providers/anthropic)
- [/reference/token-use](/fr/reference/token-use)
- [/help/faq#why-am-i-seeing-http-429-ratelimiterror-from-anthropic](/fr/help/faq#why-am-i-seeing-http-429-ratelimiterror-from-anthropic)

## Un backend local compatible OpenAI réussit les sondes directes, mais les exécutions d’agent échouent

Utilisez cette section lorsque :

- `curl ... /v1/models` fonctionne
- de petits appels directs à `/v1/chat/completions` fonctionnent
- les exécutions de modèle OpenClaw échouent uniquement sur des tours d’agent normaux

```bash
curl http://127.0.0.1:1234/v1/models
curl http://127.0.0.1:1234/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"model":"<id>","messages":[{"role":"user","content":"hi"}],"stream":false}'
openclaw infer model run --model <provider/model> --prompt "hi" --json
openclaw logs --follow
```

Recherchez :

- les petits appels directs réussissent, mais les exécutions OpenClaw échouent uniquement avec des prompts plus volumineux
- des erreurs du backend indiquant que `messages[].content` attend une chaîne
- des plantages du backend qui n’apparaissent qu’avec un plus grand nombre de jetons de prompt ou avec les prompts complets du runtime d’agent

Signatures courantes :

- `messages[...].content: invalid type: sequence, expected a string` → le backend
  rejette des parties de contenu structurées de Chat Completions. Correctif : définissez
  `models.providers.<provider>.models[].compat.requiresStringContent: true`.
- les petites requêtes directes réussissent, mais les exécutions d’agent OpenClaw échouent avec des plantages de backend/modèle
  (par exemple Gemma sur certaines versions de `inferrs`) → le transport OpenClaw est
  probablement déjà correct ; le backend échoue sur la forme plus volumineuse du prompt du runtime d’agent.
- les échecs diminuent après avoir désactivé les outils mais ne disparaissent pas → les schémas d’outils faisaient
  partie de la pression, mais le problème restant relève toujours de la capacité du modèle/serveur en amont ou d’un bug backend.

Options de correction :

1. Définissez `compat.requiresStringContent: true` pour les backends Chat Completions qui n’acceptent que des chaînes.
2. Définissez `compat.supportsTools: false` pour les modèles/backends qui ne peuvent pas gérer
   de manière fiable la surface de schéma d’outils d’OpenClaw.
3. Réduisez la pression sur le prompt lorsque c’est possible : bootstrap d’espace de travail plus petit, historique de session plus court, modèle local plus léger, ou backend avec un meilleur support du long contexte.
4. Si les petites requêtes directes continuent de réussir alors que les tours d’agent OpenClaw plantent toujours dans le backend, traitez cela comme une limitation du serveur/modèle en amont et ouvrez-y un rapport avec une reproduction incluant la forme de payload acceptée.

Voir aussi :

- [/gateway/local-models](/fr/gateway/local-models)
- [/gateway/configuration](/fr/gateway/configuration)
- [/gateway/configuration-reference#openai-compatible-endpoints](/fr/gateway/configuration-reference#openai-compatible-endpoints)

## Aucune réponse

Si les canaux sont actifs mais que rien ne répond, vérifiez le routage et la politique avant de reconnecter quoi que ce soit.

```bash
openclaw status
openclaw channels status --probe
openclaw pairing list --channel <channel> [--account <id>]
openclaw config get channels
openclaw logs --follow
```

Recherchez :

- Appairage en attente pour les expéditeurs de messages privés.
- Contrôle des mentions de groupe (`requireMention`, `mentionPatterns`).
- Incohérences de liste d’autorisation de canal/groupe.

Signatures courantes :

- `drop guild message (mention required` → message de groupe ignoré jusqu’à mention.
- `pairing request` → l’expéditeur a besoin d’une approbation.
- `blocked` / `allowlist` → expéditeur/canal filtré par la politique.

Voir aussi :

- [/channels/troubleshooting](/fr/channels/troubleshooting)
- [/channels/pairing](/fr/channels/pairing)
- [/channels/groups](/fr/channels/groups)

## Connectivité de l’interface de contrôle du tableau de bord

Lorsque le tableau de bord/l’interface de contrôle ne se connecte pas, validez l’URL, le mode d’authentification et les hypothèses de contexte sécurisé.

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --json
```

Recherchez :

- URL de sonde et URL du tableau de bord correctes.
- Incohérence de mode d’authentification/jeton entre le client et la gateway.
- Utilisation de HTTP là où une identité d’appareil est requise.

Signatures courantes :

- `device identity required` → contexte non sécurisé ou authentification d’appareil manquante.
- `origin not allowed` → l’`Origin` du navigateur n’est pas dans `gateway.controlUi.allowedOrigins`
  (ou vous vous connectez depuis une origine de navigateur non-loopback sans
  liste d’autorisation explicite).
- `device nonce required` / `device nonce mismatch` → le client n’achève pas le
  flux d’authentification d’appareil basé sur challenge (`connect.challenge` + `device.nonce`).
- `device signature invalid` / `device signature expired` → le client a signé le mauvais
  payload (ou un horodatage périmé) pour le handshake actuel.
- `AUTH_TOKEN_MISMATCH` avec `canRetryWithDeviceToken=true` → le client peut faire une nouvelle tentative de confiance avec un jeton d’appareil en cache.
- Cette nouvelle tentative avec jeton en cache réutilise l’ensemble de portées en cache stocké avec le
  jeton d’appareil appairé. Les appelants avec `deviceToken` explicite / `scopes` explicites conservent leur
  ensemble de portées demandé.
- En dehors de cette voie de nouvelle tentative, la priorité d’authentification à la connexion est d’abord
  le jeton/mot de passe partagé explicite, puis le `deviceToken` explicite, puis le jeton d’appareil stocké,
  puis le jeton de bootstrap.
- Sur la voie asynchrone Tailscale Serve Control UI, les tentatives échouées pour le même
  `{scope, ip}` sont sérialisées avant que le limiteur n’enregistre l’échec. Deux mauvaises nouvelles tentatives concurrentes depuis le même client peuvent donc faire apparaître `retry later`
  à la deuxième tentative au lieu de deux simples incohérences.
- `too many failed authentication attempts (retry later)` depuis un client loopback d’origine navigateur
  → les échecs répétés depuis cette même `Origin` normalisée sont temporairement bloqués ; une autre origine localhost utilise un compartiment distinct.
- `unauthorized` répété après cette nouvelle tentative → dérive du jeton partagé/du jeton d’appareil ; actualisez la configuration du jeton et réapprouvez/faites tourner le jeton d’appareil si nécessaire.
- `gateway connect failed:` → cible hôte/port/url incorrecte.

### Carte rapide des codes de détail d’authentification

Utilisez `error.details.code` de la réponse `connect` échouée pour choisir l’action suivante :

| Code de détail               | Signification                                            | Action recommandée                                                                                                                                                                                                                                                                        |
| ---------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `AUTH_TOKEN_MISSING`         | Le client n’a pas envoyé un jeton partagé requis.        | Collez/définissez le jeton dans le client et réessayez. Pour les chemins du tableau de bord : `openclaw config get gateway.auth.token` puis collez-le dans les paramètres de l’interface de contrôle.                                                                                  |
| `AUTH_TOKEN_MISMATCH`        | Le jeton partagé ne correspond pas au jeton d’authentification de la gateway. | Si `canRetryWithDeviceToken=true`, autorisez une nouvelle tentative de confiance. Les nouvelles tentatives avec jeton en cache réutilisent les portées approuvées stockées ; les appelants avec `deviceToken` / `scopes` explicites conservent les portées demandées. Si cela échoue encore, exécutez la [checklist de récupération après dérive de jeton](/cli/devices#token-drift-recovery-checklist). |
| `AUTH_DEVICE_TOKEN_MISMATCH` | Le jeton par appareil en cache est périmé ou révoqué.    | Faites tourner/réapprouvez le jeton d’appareil via le [CLI devices](/cli/devices), puis reconnectez-vous.                                                                                                                                                                                |
| `PAIRING_REQUIRED`           | L’identité de l’appareil est connue mais non approuvée pour ce rôle. | Approuvez la demande en attente : `openclaw devices list` puis `openclaw devices approve <requestId>`.                                                                                                                                                                                   |

Vérification de migration vers l’authentification d’appareil v2 :

```bash
openclaw --version
openclaw doctor
openclaw gateway status
```

Si les journaux affichent des erreurs de nonce/signature, mettez à jour le client qui se connecte et vérifiez qu’il :

1. attend `connect.challenge`
2. signe le payload lié au challenge
3. envoie `connect.params.device.nonce` avec le même nonce de challenge

Si `openclaw devices rotate` / `revoke` / `remove` est refusé de manière inattendue :

- les sessions à jeton d’appareil appairé peuvent gérer uniquement **leur propre**
  appareil, sauf si l’appelant a aussi `operator.admin`
- `openclaw devices rotate --scope ...` ne peut demander que des portées opérateur que
  la session appelante détient déjà

Voir aussi :

- [/web/control-ui](/web/control-ui)
- [/gateway/configuration](/fr/gateway/configuration) (modes d’authentification de la gateway)
- [/gateway/trusted-proxy-auth](/fr/gateway/trusted-proxy-auth)
- [/gateway/remote](/fr/gateway/remote)
- [/cli/devices](/cli/devices)

## Le service gateway n’est pas en cours d’exécution

Utilisez cette section lorsque le service est installé mais que le processus ne reste pas actif.

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --deep   # analyse aussi les services au niveau système
```

Recherchez :

- `Runtime: stopped` avec indices de sortie.
- Incohérence de configuration de service (`Config (cli)` vs `Config (service)`).
- Conflits de port/écoute.
- Installations launchd/systemd/schtasks supplémentaires lorsque `--deep` est utilisé.
- Indices de nettoyage `Other gateway-like services detected (best effort)`.

Signatures courantes :

- `Gateway start blocked: set gateway.mode=local` ou `existing config is missing gateway.mode` → le mode gateway local n’est pas activé, ou le fichier de configuration a été écrasé et a perdu `gateway.mode`. Correctif : définissez `gateway.mode="local"` dans votre configuration, ou relancez `openclaw onboard --mode local` / `openclaw setup` pour réappliquer la configuration attendue du mode local. Si vous exécutez OpenClaw via Podman, le chemin de configuration par défaut est `~/.openclaw/openclaw.json`.
- `refusing to bind gateway ... without auth` → liaison non-loopback sans chemin d’authentification gateway valide (jeton/mot de passe, ou trusted-proxy lorsque configuré).
- `another gateway instance is already listening` / `EADDRINUSE` → conflit de port.
- `Other gateway-like services detected (best effort)` → il existe des unités launchd/systemd/schtasks obsolètes ou parallèles. La plupart des configurations doivent conserver une seule gateway par machine ; si vous en avez réellement besoin de plusieurs, isolez les ports + la configuration/l’état/l’espace de travail. Voir [/gateway#multiple-gateways-same-host](/fr/gateway#multiple-gateways-same-host).

Voir aussi :

- [/gateway/background-process](/fr/gateway/background-process)
- [/gateway/configuration](/fr/gateway/configuration)
- [/gateway/doctor](/fr/gateway/doctor)

## Avertissements de sonde de la gateway

Utilisez cette section lorsque `openclaw gateway probe` atteint bien quelque chose, mais affiche quand même un bloc d’avertissement.

```bash
openclaw gateway probe
openclaw gateway probe --json
openclaw gateway probe --ssh user@gateway-host
```

Recherchez :

- `warnings[].code` et `primaryTargetId` dans la sortie JSON.
- Si l’avertissement concerne le fallback SSH, plusieurs gateways, des portées manquantes, ou des références d’authentification non résolues.

Signatures courantes :

- `SSH tunnel failed to start; falling back to direct probes.` → la configuration SSH a échoué, mais la commande a quand même essayé les cibles directes configurées/en loopback.
- `multiple reachable gateways detected` → plus d’une cible a répondu. En général, cela indique une configuration multi-gateway intentionnelle ou des écouteurs obsolètes/dupliqués.
- `Probe diagnostics are limited by gateway scopes (missing operator.read)` → la connexion a réussi, mais le RPC détaillé est limité par les portées ; appairez une identité d’appareil ou utilisez des identifiants avec `operator.read`.
- texte d’avertissement de SecretRef non résolu pour `gateway.auth.*` / `gateway.remote.*` → le matériel d’authentification n’était pas disponible dans ce chemin de commande pour la cible en échec.

Voir aussi :

- [/cli/gateway](/cli/gateway)
- [/gateway#multiple-gateways-same-host](/fr/gateway#multiple-gateways-same-host)
- [/gateway/remote](/fr/gateway/remote)

## Canal connecté mais messages qui ne circulent pas

Si l’état du canal est connecté mais que le flux de messages est interrompu, concentrez-vous sur la politique, les autorisations et les règles de livraison spécifiques au canal.

```bash
openclaw channels status --probe
openclaw pairing list --channel <channel> [--account <id>]
openclaw status --deep
openclaw logs --follow
openclaw config get channels
```

Recherchez :

- Politique DM (`pairing`, `allowlist`, `open`, `disabled`).
- Liste d’autorisation de groupe et exigences de mention.
- Permissions/portées API du canal manquantes.

Signatures courantes :

- `mention required` → message ignoré par la politique de mention de groupe.
- traces `pairing` / d’approbation en attente → l’expéditeur n’est pas approuvé.
- `missing_scope`, `not_in_channel`, `Forbidden`, `401/403` → problème d’authentification/autorisations du canal.

Voir aussi :

- [/channels/troubleshooting](/fr/channels/troubleshooting)
- [/channels/whatsapp](/fr/channels/whatsapp)
- [/channels/telegram](/fr/channels/telegram)
- [/channels/discord](/fr/channels/discord)

## Livraison cron et heartbeat

Si cron ou heartbeat ne s’est pas exécuté ou n’a pas été livré, vérifiez d’abord l’état du planificateur, puis la cible de livraison.

```bash
openclaw cron status
openclaw cron list
openclaw cron runs --id <jobId> --limit 20
openclaw system heartbeat last
openclaw logs --follow
```

Recherchez :

- Cron activé et prochaine activation présente.
- État de l’historique d’exécution des jobs (`ok`, `skipped`, `error`).
- Raisons de saut de heartbeat (`quiet-hours`, `requests-in-flight`, `alerts-disabled`, `empty-heartbeat-file`, `no-tasks-due`).

Signatures courantes :

- `cron: scheduler disabled; jobs will not run automatically` → cron désactivé.
- `cron: timer tick failed` → l’impulsion du planificateur a échoué ; vérifiez les erreurs de fichiers/journaux/runtime.
- `heartbeat skipped` avec `reason=quiet-hours` → hors de la fenêtre d’heures actives.
- `heartbeat skipped` avec `reason=empty-heartbeat-file` → `HEARTBEAT.md` existe mais ne contient que des lignes vides / en-têtes markdown, donc OpenClaw ignore l’appel au modèle.
- `heartbeat skipped` avec `reason=no-tasks-due` → `HEARTBEAT.md` contient un bloc `tasks:`, mais aucune tâche n’est due à cette impulsion.
- `heartbeat: unknown accountId` → id de compte invalide pour la cible de livraison heartbeat.
- `heartbeat skipped` avec `reason=dm-blocked` → la cible heartbeat a été résolue en destination de type DM alors que `agents.defaults.heartbeat.directPolicy` (ou la surcharge par agent) est défini sur `block`.

Voir aussi :

- [/automation/cron-jobs#troubleshooting](/fr/automation/cron-jobs#troubleshooting)
- [/automation/cron-jobs](/fr/automation/cron-jobs)
- [/gateway/heartbeat](/fr/gateway/heartbeat)

## Échec d’un outil de nœud appairé

Si un nœud est appairé mais que les outils échouent, isolez l’état de premier plan, les permissions et l’état d’approbation.

```bash
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
openclaw approvals get --node <idOrNameOrIp>
openclaw logs --follow
openclaw status
```

Recherchez :

- Nœud en ligne avec les capacités attendues.
- Autorisations système accordées pour caméra/micro/localisation/écran.
- État des approbations d’exécution et de la liste d’autorisation.

Signatures courantes :

- `NODE_BACKGROUND_UNAVAILABLE` → l’app du nœud doit être au premier plan.
- `*_PERMISSION_REQUIRED` / `LOCATION_PERMISSION_REQUIRED` → autorisation système manquante.
- `SYSTEM_RUN_DENIED: approval required` → approbation d’exécution en attente.
- `SYSTEM_RUN_DENIED: allowlist miss` → commande bloquée par la liste d’autorisation.

Voir aussi :

- [/nodes/troubleshooting](/fr/nodes/troubleshooting)
- [/nodes/index](/fr/nodes/index)
- [/tools/exec-approvals](/fr/tools/exec-approvals)

## Échec de l’outil navigateur

Utilisez cette section lorsque les actions de l’outil navigateur échouent alors que la gateway elle-même est saine.

```bash
openclaw browser status
openclaw browser start --browser-profile openclaw
openclaw browser profiles
openclaw logs --follow
openclaw doctor
```

Recherchez :

- Si `plugins.allow` est défini et inclut `browser`.
- Un chemin d’exécutable du navigateur valide.
- L’accessibilité du profil CDP.
- La disponibilité de Chrome local pour les profils `existing-session` / `user`.

Signatures courantes :

- `unknown command "browser"` ou `unknown command 'browser'` → le plugin navigateur intégré est exclu par `plugins.allow`.
- outil navigateur manquant / indisponible alors que `browser.enabled=true` → `plugins.allow` exclut `browser`, donc le plugin n’a jamais été chargé.
- `Failed to start Chrome CDP on port` → le processus du navigateur n’a pas pu être lancé.
- `browser.executablePath not found` → le chemin configuré est invalide.
- `browser.cdpUrl must be http(s) or ws(s)` → l’URL CDP configurée utilise un schéma non pris en charge tel que `file:` ou `ftp:`.
- `browser.cdpUrl has invalid port` → l’URL CDP configurée contient un port invalide ou hors plage.
- `No Chrome tabs found for profile="user"` → le profil d’attachement Chrome MCP n’a aucun onglet Chrome local ouvert.
- `Remote CDP for profile "<name>" is not reachable` → le point de terminaison CDP distant configuré n’est pas accessible depuis l’hôte gateway.
- `Browser attachOnly is enabled ... not reachable` ou `Browser attachOnly is enabled and CDP websocket ... is not reachable` → le profil en attachement seul n’a aucune cible accessible, ou le point de terminaison HTTP a répondu mais le WebSocket CDP n’a toujours pas pu être ouvert.
- `Playwright is not available in this gateway build; '<feature>' is unsupported.` → l’installation actuelle de la gateway n’inclut pas le package Playwright complet ; les instantanés ARIA et les captures d’écran de page de base peuvent toujours fonctionner, mais la navigation, les instantanés IA, les captures d’écran d’élément par sélecteur CSS et l’export PDF restent indisponibles.
- `fullPage is not supported for element screenshots` → la requête de capture d’écran a mélangé `--full-page` avec `--ref` ou `--element`.
- `element screenshots are not supported for existing-session profiles; use ref from snapshot.` → les appels de capture d’écran Chrome MCP / `existing-session` doivent utiliser une capture de page ou un `--ref` d’instantané, pas un `--element` CSS.
- `existing-session file uploads do not support element selectors; use ref/inputRef.` → les hooks d’envoi de fichiers Chrome MCP nécessitent des refs d’instantané, pas des sélecteurs CSS.
- `existing-session file uploads currently support one file at a time.` → envoyez un seul téléversement par appel sur les profils Chrome MCP.
- `existing-session dialog handling does not support timeoutMs.` → les hooks de dialogue sur les profils Chrome MCP ne prennent pas en charge les surcharges de délai.
- `response body is not supported for existing-session profiles yet.` → `responsebody` nécessite encore un navigateur géré ou un profil CDP brut.
- surcharges persistantes de viewport / mode sombre / langue / hors ligne sur des profils en attachement seul ou CDP distant → exécutez `openclaw browser stop --browser-profile <name>` pour fermer la session de contrôle active et libérer l’état d’émulation Playwright/CDP sans redémarrer toute la gateway.

Voir aussi :

- [/tools/browser-linux-troubleshooting](/fr/tools/browser-linux-troubleshooting)
- [/tools/browser](/fr/tools/browser)

## Si vous avez effectué une mise à niveau et que quelque chose s’est soudainement cassé

La plupart des cassures après mise à niveau sont dues à une dérive de configuration ou à des valeurs par défaut plus strictes désormais appliquées.

### 1) Le comportement d’authentification et de surcharge d’URL a changé

```bash
openclaw gateway status
openclaw config get gateway.mode
openclaw config get gateway.remote.url
openclaw config get gateway.auth.mode
```

À vérifier :

- Si `gateway.mode=remote`, les appels CLI peuvent cibler le remote alors que votre service local fonctionne bien.
- Les appels explicites avec `--url` ne reviennent pas aux identifiants stockés.

Signatures courantes :

- `gateway connect failed:` → mauvaise URL cible.
- `unauthorized` → point de terminaison accessible mais mauvaise authentification.

### 2) Les garde-fous de bind et d’authentification sont plus stricts

```bash
openclaw config get gateway.bind
openclaw config get gateway.auth.mode
openclaw config get gateway.auth.token
openclaw gateway status
openclaw logs --follow
```

À vérifier :

- Les binds non-loopback (`lan`, `tailnet`, `custom`) nécessitent un chemin d’authentification gateway valide : authentification par jeton/mot de passe partagé, ou déploiement `trusted-proxy` non-loopback correctement configuré.
- Les anciennes clés comme `gateway.token` ne remplacent pas `gateway.auth.token`.

Signatures courantes :

- `refusing to bind gateway ... without auth` → bind non-loopback sans chemin d’authentification gateway valide.
- `RPC probe: failed` alors que le runtime est en cours d’exécution → gateway active mais inaccessible avec l’authentification/l’URL actuelles.

### 3) L’état d’appairage et d’identité d’appareil a changé

```bash
openclaw devices list
openclaw pairing list --channel <channel> [--account <id>]
openclaw logs --follow
openclaw doctor
```

À vérifier :

- Approbations d’appareil en attente pour tableau de bord/nœuds.
- Approbations d’appairage DM en attente après des changements de politique ou d’identité.

Signatures courantes :

- `device identity required` → authentification d’appareil non satisfaite.
- `pairing required` → expéditeur/appareil doit être approuvé.

Si la configuration du service et le runtime ne concordent toujours pas après ces vérifications, réinstallez les métadonnées du service à partir du même répertoire de profil/d’état :

```bash
openclaw gateway install --force
openclaw gateway restart
```

Voir aussi :

- [/gateway/pairing](/fr/gateway/pairing)
- [/gateway/authentication](/fr/gateway/authentication)
- [/gateway/background-process](/fr/gateway/background-process)
