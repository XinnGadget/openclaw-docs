---
read_when:
    - Vous avez besoin d’une référence de configuration des modèles, fournisseur par fournisseur
    - Vous voulez des exemples de configurations ou des commandes d’intégration CLI pour les fournisseurs de modèles
summary: Vue d’ensemble des fournisseurs de modèles avec exemples de configurations + flux CLI
title: Fournisseurs de modèles
x-i18n:
    generated_at: "2026-04-13T08:50:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: 66ba688c4b4366eec07667571e835d4cfeee684896e2ffae11d601b5fa0a4b98
    source_path: concepts/model-providers.md
    workflow: 15
---

# Fournisseurs de modèles

Cette page couvre les **fournisseurs de LLM/modèles** (et non les canaux de discussion comme WhatsApp/Telegram).
Pour les règles de sélection de modèles, voir [/concepts/models](/fr/concepts/models).

## Règles rapides

- Les références de modèle utilisent `provider/model` (exemple : `opencode/claude-opus-4-6`).
- Si vous définissez `agents.defaults.models`, cela devient la liste d’autorisation.
- Assistants CLI : `openclaw onboard`, `openclaw models list`, `openclaw models set <provider/model>`.
- Les règles d’exécution de repli, les sondes de refroidissement et la persistance des remplacements de session sont documentées dans [/concepts/model-failover](/fr/concepts/model-failover).
- `models.providers.*.models[].contextWindow` est une métadonnée native du modèle ;
  `models.providers.*.models[].contextTokens` est la limite d’exécution effective.
- Les Plugins de fournisseur peuvent injecter des catalogues de modèles via `registerProvider({ catalog })` ;
  OpenClaw fusionne cette sortie dans `models.providers` avant d’écrire
  `models.json`.
- Les manifestes de fournisseur peuvent déclarer `providerAuthEnvVars` et
  `providerAuthAliases` afin que les sondes d’authentification génériques basées sur les variables d’environnement et les variantes de fournisseur
  n’aient pas besoin de charger l’exécution du Plugin. La map restante de variables d’environnement du cœur sert désormais
  uniquement aux fournisseurs non Plugin / cœur et à quelques cas de priorité générique tels
  que l’intégration Anthropic avec priorité à la clé API.
- Les Plugins de fournisseur peuvent également gérer le comportement d’exécution du fournisseur via
  `normalizeModelId`, `normalizeTransport`, `normalizeConfig`,
  `applyNativeStreamingUsageCompat`, `resolveConfigApiKey`,
  `resolveSyntheticAuth`, `shouldDeferSyntheticProfileAuth`,
  `resolveDynamicModel`, `prepareDynamicModel`,
  `normalizeResolvedModel`, `contributeResolvedModelCompat`,
  `capabilities`, `normalizeToolSchemas`,
  `inspectToolSchemas`, `resolveReasoningOutputMode`,
  `prepareExtraParams`, `createStreamFn`, `wrapStreamFn`,
  `resolveTransportTurnState`, `resolveWebSocketSessionPolicy`,
  `createEmbeddingProvider`, `formatApiKey`, `refreshOAuth`,
  `buildAuthDoctorHint`,
  `matchesContextOverflowError`, `classifyFailoverReason`,
  `isCacheTtlEligible`, `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `isBinaryThinking`, `supportsXHighThinking`,
  `resolveDefaultThinkingLevel`, `applyConfigDefaults`, `isModernModelRef`,
  `prepareRuntimeAuth`, `resolveUsageAuth`, `fetchUsageSnapshot`, and
  `onModelSelected`.
- Remarque : les `capabilities` d’exécution du fournisseur sont des métadonnées de runner partagées (famille de fournisseur, particularités de transcription/outillage, indications de transport/cache). Ce n’est pas
  la même chose que le [modèle de capacités public](/fr/plugins/architecture#public-capability-model)
  qui décrit ce qu’un Plugin enregistre (inférence de texte, parole, etc.).
- Le fournisseur `codex` inclus est associé au harnais d’agent Codex inclus.
  Utilisez `codex/gpt-*` lorsque vous souhaitez la connexion gérée par Codex, la découverte de modèles, la reprise native de fil,
  et l’exécution sur serveur d’application. Les références simples `openai/gpt-*` continuent
  d’utiliser le fournisseur OpenAI et le transport normal des fournisseurs OpenClaw.
  Les déploiements uniquement Codex peuvent désactiver le repli automatique PI avec
  `agents.defaults.embeddedHarness.fallback: "none"` ; voir
  [Codex Harness](/fr/plugins/codex-harness).

## Comportement de fournisseur géré par le Plugin

Les Plugins de fournisseur peuvent désormais gérer la plupart de la logique spécifique au fournisseur tandis qu’OpenClaw conserve
la boucle d’inférence générique.

Répartition typique :

- `auth[].run` / `auth[].runNonInteractive` : le fournisseur gère les flux
  d’intégration/connexion pour `openclaw onboard`, `openclaw models auth` et la configuration sans interface
- `wizard.setup` / `wizard.modelPicker` : le fournisseur gère les libellés des choix d’authentification,
  les alias hérités, les indications de liste d’autorisation d’intégration et les entrées de configuration dans les sélecteurs d’intégration/de modèle
- `catalog` : le fournisseur apparaît dans `models.providers`
- `normalizeModelId` : le fournisseur normalise les identifiants de modèle hérités/de préversion avant
  la recherche ou la canonicalisation
- `normalizeTransport` : le fournisseur normalise `api` / `baseUrl` de la famille de transport
  avant l’assemblage générique du modèle ; OpenClaw vérifie d’abord le fournisseur correspondant,
  puis les autres Plugins de fournisseur capables de hooks jusqu’à ce que l’un modifie réellement
  le transport
- `normalizeConfig` : le fournisseur normalise la configuration `models.providers.<id>` avant
  son utilisation à l’exécution ; OpenClaw vérifie d’abord le fournisseur correspondant, puis les autres
  Plugins de fournisseur capables de hooks jusqu’à ce que l’un modifie réellement la configuration. Si aucun
  hook de fournisseur ne réécrit la configuration, les assistants groupés de la famille Google
  normalisent encore les entrées de fournisseur Google prises en charge.
- `applyNativeStreamingUsageCompat` : le fournisseur applique des réécritures de compatibilité d’usage de streaming natif pilotées par le point de terminaison pour les fournisseurs de configuration
- `resolveConfigApiKey` : le fournisseur résout l’authentification par marqueur d’environnement pour les fournisseurs de configuration
  sans forcer le chargement complet de l’authentification d’exécution. `amazon-bedrock` dispose également ici
  d’un résolveur intégré de marqueurs d’environnement AWS, même si l’authentification d’exécution Bedrock utilise
  la chaîne par défaut du SDK AWS.
- `resolveSyntheticAuth` : le fournisseur peut exposer la disponibilité d’une authentification locale/autohébergée ou autre
  basée sur la configuration sans persister de secrets en clair
- `shouldDeferSyntheticProfileAuth` : le fournisseur peut marquer les espaces réservés de profil synthétique stockés
  comme ayant une priorité inférieure à l’authentification basée sur l’environnement/la configuration
- `resolveDynamicModel` : le fournisseur accepte des identifiants de modèle qui ne sont pas encore présents dans le
  catalogue statique local
- `prepareDynamicModel` : le fournisseur a besoin d’un rafraîchissement de métadonnées avant de retenter
  la résolution dynamique
- `normalizeResolvedModel` : le fournisseur a besoin de réécritures de transport ou d’URL de base
- `contributeResolvedModelCompat` : le fournisseur contribue des indicateurs de compatibilité pour ses
  modèles du fournisseur, même lorsqu’ils arrivent via un autre transport compatible
- `capabilities` : le fournisseur publie les particularités liées à la transcription, à l’outillage et à la famille de fournisseur
- `normalizeToolSchemas` : le fournisseur nettoie les schémas d’outils avant que le
  runner intégré ne les voie
- `inspectToolSchemas` : le fournisseur expose des avertissements de schéma spécifiques au transport
  après normalisation
- `resolveReasoningOutputMode` : le fournisseur choisit des contrats de sortie de raisonnement
  natifs ou balisés
- `prepareExtraParams` : le fournisseur applique des valeurs par défaut ou normalise les paramètres de requête par modèle
- `createStreamFn` : le fournisseur remplace le chemin de flux normal par un transport
  entièrement personnalisé
- `wrapStreamFn` : le fournisseur applique des wrappers de compatibilité pour en-têtes/corps/modèle de requête
- `resolveTransportTurnState` : le fournisseur fournit des en-têtes ou métadonnées de transport natives
  par tour
- `resolveWebSocketSessionPolicy` : le fournisseur fournit des en-têtes de session WebSocket natifs
  ou une politique de refroidissement de session
- `createEmbeddingProvider` : le fournisseur gère le comportement d’embedding mémoire lorsqu’il
  appartient au Plugin du fournisseur plutôt qu’au commutateur central d’embeddings du cœur
- `formatApiKey` : le fournisseur met en forme les profils d’authentification stockés dans la chaîne
  `apiKey` d’exécution attendue par le transport
- `refreshOAuth` : le fournisseur gère le rafraîchissement OAuth lorsque les rafraîchisseurs partagés `pi-ai`
  ne suffisent pas
- `buildAuthDoctorHint` : le fournisseur ajoute des indications de réparation lorsque l’actualisation OAuth
  échoue
- `matchesContextOverflowError` : le fournisseur reconnaît les erreurs de dépassement de fenêtre de contexte
  spécifiques au fournisseur que les heuristiques génériques manqueraient
- `classifyFailoverReason` : le fournisseur mappe les erreurs brutes spécifiques au fournisseur du transport/de l’API
  vers des raisons de repli telles que la limitation de débit ou la surcharge
- `isCacheTtlEligible` : le fournisseur décide quels identifiants de modèle amont prennent en charge le TTL du cache de prompt
- `buildMissingAuthMessage` : le fournisseur remplace l’erreur générique du magasin d’authentification
  par une indication de récupération spécifique au fournisseur
- `suppressBuiltInModel` : le fournisseur masque les lignes amont obsolètes et peut renvoyer une
  erreur gérée par le fournisseur pour les échecs de résolution directe
- `augmentModelCatalog` : le fournisseur ajoute des lignes de catalogue synthétiques/finales après
  la découverte et la fusion de configuration
- `isBinaryThinking` : le fournisseur gère l’expérience utilisateur de réflexion binaire activée/désactivée
- `supportsXHighThinking` : le fournisseur active `xhigh` pour les modèles sélectionnés
- `resolveDefaultThinkingLevel` : le fournisseur gère la politique `/think` par défaut pour une
  famille de modèles
- `applyConfigDefaults` : le fournisseur applique des valeurs par défaut globales spécifiques au fournisseur
  pendant la matérialisation de la configuration selon le mode d’authentification, l’environnement ou la famille de modèles
- `isModernModelRef` : le fournisseur gère la correspondance des modèles préférés en direct/de test smoke
- `prepareRuntimeAuth` : le fournisseur transforme un identifiant configuré en un jeton d’exécution
  de courte durée
- `resolveUsageAuth` : le fournisseur résout les identifiants d’usage/quota pour `/usage`
  et les surfaces associées de statut/rapport
- `fetchUsageSnapshot` : le fournisseur gère la récupération/l’analyse du point de terminaison d’usage tandis que le
  cœur continue de gérer l’enveloppe de résumé et la mise en forme
- `onModelSelected` : le fournisseur exécute des effets secondaires après sélection,
  comme la télémétrie ou la tenue de session gérée par le fournisseur

Exemples groupés actuels :

- `anthropic` : repli de compatibilité amont pour Claude 4.6, indications de réparation d’authentification, récupération du point de terminaison d’usage, métadonnées de TTL du cache/famille de fournisseur, et valeurs par défaut globales de configuration tenant compte de l’authentification
- `amazon-bedrock` : détection du dépassement de contexte gérée par le fournisseur et classification des raisons de repli pour les erreurs Bedrock spécifiques de limitation/pas prêt, plus la famille de rejeu partagée `anthropic-by-model` pour les garde-fous de politique de rejeu réservés à Claude sur le trafic Anthropic
- `anthropic-vertex` : garde-fous de politique de rejeu réservés à Claude sur le trafic de messages Anthropic
- `openrouter` : identifiants de modèle transmis tels quels, wrappers de requête, indications de capacités du fournisseur, assainissement des signatures de pensée Gemini sur le trafic Gemini proxifié, injection de raisonnement par proxy via la famille de flux `openrouter-thinking`, transfert des métadonnées de routage, et politique de TTL du cache
- `github-copilot` : intégration/connexion par appareil, repli de modèle de compatibilité amont, indications de transcription pour Claude thinking, échange de jeton d’exécution, et récupération du point de terminaison d’usage
- `openai` : repli de compatibilité amont pour GPT-5.4, normalisation directe du transport OpenAI, indications d’authentification manquante tenant compte de Codex, suppression de Spark, lignes de catalogue OpenAI/Codex synthétiques, politique de thinking/modèles en direct, normalisation des alias de jetons d’usage (`input` / `output` et familles `prompt` / `completion`), famille de flux partagée `openai-responses-defaults` pour les wrappers natifs OpenAI/Codex, métadonnées de famille de fournisseur, enregistrement groupé du fournisseur de génération d’images pour `gpt-image-1`, et enregistrement groupé du fournisseur de génération vidéo pour `sora-2`
- `google` et `google-gemini-cli` : repli de compatibilité amont pour Gemini 3.1, validation native du rejeu Gemini, assainissement du rejeu d’amorçage, mode de sortie de raisonnement balisé, correspondance des modèles modernes, enregistrement groupé du fournisseur de génération d’images pour les modèles Gemini image-preview, et enregistrement groupé du fournisseur de génération vidéo pour les modèles Veo ; Gemini CLI OAuth gère également la mise en forme des jetons de profil d’authentification, l’analyse des jetons d’usage et la récupération du point de terminaison de quota pour les surfaces d’usage
- `moonshot` : transport partagé, normalisation de charge utile de thinking gérée par le Plugin
- `kilocode` : transport partagé, en-têtes de requête gérés par le Plugin, normalisation de charge utile de raisonnement, assainissement des signatures de pensée Gemini proxifiées, et politique de TTL du cache
- `zai` : repli de compatibilité amont pour GLM-5, valeurs par défaut `tool_stream`, politique de TTL du cache, politique de thinking binaire/modèles en direct, et authentification d’usage + récupération du quota ; les identifiants inconnus `glm-5*` sont synthétisés à partir du modèle groupé `glm-4.7`
- `xai` : normalisation native du transport Responses, réécritures d’alias `/fast` pour les variantes rapides de Grok, `tool_stream` par défaut, nettoyage spécifique à xAI des schémas d’outils / charges utiles de raisonnement, et enregistrement groupé du fournisseur de génération vidéo pour `grok-imagine-video`
- `mistral` : métadonnées de capacités gérées par le Plugin
- `opencode` et `opencode-go` : métadonnées de capacités gérées par le Plugin plus assainissement des signatures de pensée Gemini proxifiées
- `alibaba` : catalogue de génération vidéo géré par le Plugin pour les références directes de modèles Wan telles que `alibaba/wan2.6-t2v`
- `byteplus` : catalogues gérés par le Plugin plus enregistrement groupé du fournisseur de génération vidéo pour les modèles Seedance texte-vers-vidéo/image-vers-vidéo
- `fal` : enregistrement groupé du fournisseur de génération vidéo pour des modèles vidéo tiers hébergés, enregistrement du fournisseur de génération d’images pour les modèles d’image FLUX, plus enregistrement groupé du fournisseur de génération vidéo pour des modèles vidéo tiers hébergés
- `cloudflare-ai-gateway`, `huggingface`, `kimi`, `nvidia`, `qianfan`,
  `stepfun`, `synthetic`, `venice`, `vercel-ai-gateway`, et `volcengine` :
  catalogues gérés par le Plugin uniquement
- `qwen` : catalogues gérés par le Plugin pour les modèles texte plus enregistrements partagés des fournisseurs d’analyse de médias et de génération vidéo pour ses surfaces multimodales ; la génération vidéo Qwen utilise les points de terminaison vidéo DashScope Standard avec des modèles Wan groupés tels que `wan2.6-t2v` et `wan2.7-r2v`
- `runway` : enregistrement du fournisseur de génération vidéo géré par le Plugin pour des modèles natifs Runway basés sur des tâches tels que `gen4.5`
- `minimax` : catalogues gérés par le Plugin, enregistrement groupé du fournisseur de génération vidéo pour les modèles vidéo Hailuo, enregistrement groupé du fournisseur de génération d’images pour `image-01`, sélection hybride de politique de rejeu Anthropic/OpenAI, et logique d’authentification/cliché d’usage
- `together` : catalogues gérés par le Plugin plus enregistrement groupé du fournisseur de génération vidéo pour les modèles vidéo Wan
- `xiaomi` : catalogues gérés par le Plugin plus logique d’authentification/cliché d’usage

Le Plugin `openai` groupé gère désormais les deux identifiants de fournisseur : `openai` et
`openai-codex`.

Cela couvre les fournisseurs qui s’intègrent encore dans les transports normaux d’OpenClaw. Un fournisseur
qui nécessite un exécuteur de requêtes totalement personnalisé relève d’une surface d’extension distincte et plus profonde.

## Rotation des clés API

- Prend en charge la rotation générique des fournisseurs pour certains fournisseurs.
- Configurez plusieurs clés via :
  - `OPENCLAW_LIVE_<PROVIDER>_KEY` (remplacement live unique, priorité la plus élevée)
  - `<PROVIDER>_API_KEYS` (liste séparée par des virgules ou des points-virgules)
  - `<PROVIDER>_API_KEY` (clé principale)
  - `<PROVIDER>_API_KEY_*` (liste numérotée, par exemple `<PROVIDER>_API_KEY_1`)
- Pour les fournisseurs Google, `GOOGLE_API_KEY` est également inclus comme solution de repli.
- L’ordre de sélection des clés préserve la priorité et déduplique les valeurs.
- Les requêtes sont relancées avec la clé suivante uniquement en cas de réponses de limitation de débit (par
  exemple `429`, `rate_limit`, `quota`, `resource exhausted`, `Too many
concurrent requests`, `ThrottlingException`, `concurrency limit reached`,
  `workers_ai ... quota limit exceeded`, ou des messages périodiques de limite d’usage).
- Les échecs hors limitation de débit échouent immédiatement ; aucune rotation de clé n’est tentée.
- Lorsque toutes les clés candidates échouent, l’erreur finale renvoyée est celle de la dernière tentative.

## Fournisseurs intégrés (catalogue pi-ai)

OpenClaw est livré avec le catalogue pi-ai. Ces fournisseurs ne nécessitent **aucune**
configuration `models.providers` ; définissez simplement l’authentification et choisissez un modèle.

### OpenAI

- Fournisseur : `openai`
- Authentification : `OPENAI_API_KEY`
- Rotation facultative : `OPENAI_API_KEYS`, `OPENAI_API_KEY_1`, `OPENAI_API_KEY_2`, plus `OPENCLAW_LIVE_OPENAI_KEY` (remplacement unique)
- Exemples de modèles : `openai/gpt-5.4`, `openai/gpt-5.4-pro`
- CLI : `openclaw onboard --auth-choice openai-api-key`
- Le transport par défaut est `auto` (WebSocket d’abord, repli SSE)
- Remplacez par modèle via `agents.defaults.models["openai/<model>"].params.transport` (`"sse"`, `"websocket"`, ou `"auto"`)
- Le préchauffage WebSocket OpenAI Responses est activé par défaut via `params.openaiWsWarmup` (`true`/`false`)
- Le traitement prioritaire OpenAI peut être activé via `agents.defaults.models["openai/<model>"].params.serviceTier`
- `/fast` et `params.fastMode` mappent les requêtes Responses directes `openai/*` vers `service_tier=priority` sur `api.openai.com`
- Utilisez `params.serviceTier` lorsque vous souhaitez un niveau explicite plutôt que le basculement partagé `/fast`
- Les en-têtes d’attribution OpenClaw masqués (`originator`, `version`,
  `User-Agent`) s’appliquent uniquement au trafic OpenAI natif vers `api.openai.com`, pas
  aux proxys génériques compatibles OpenAI
- Les routes OpenAI natives conservent également `store` de Responses, les indications de cache de prompt et
  la mise en forme de charge utile de compatibilité de raisonnement OpenAI ; les routes proxy ne le font pas
- `openai/gpt-5.3-codex-spark` est volontairement supprimé dans OpenClaw car l’API OpenAI en direct le rejette ; Spark est traité comme réservé à Codex

```json5
{
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

### Anthropic

- Fournisseur : `anthropic`
- Authentification : `ANTHROPIC_API_KEY`
- Rotation facultative : `ANTHROPIC_API_KEYS`, `ANTHROPIC_API_KEY_1`, `ANTHROPIC_API_KEY_2`, plus `OPENCLAW_LIVE_ANTHROPIC_KEY` (remplacement unique)
- Exemple de modèle : `anthropic/claude-opus-4-6`
- CLI : `openclaw onboard --auth-choice apiKey`
- Les requêtes Anthropic publiques directes prennent aussi en charge le basculement partagé `/fast` et `params.fastMode`, y compris le trafic authentifié par clé API et OAuth envoyé à `api.anthropic.com` ; OpenClaw mappe cela vers Anthropic `service_tier` (`auto` vs `standard_only`)
- Remarque Anthropic : le personnel d’Anthropic nous a indiqué que l’usage de type Claude CLI par OpenClaw est de nouveau autorisé, donc OpenClaw traite la réutilisation de Claude CLI et l’usage de `claude -p` comme autorisés pour cette intégration sauf si Anthropic publie une nouvelle politique.
- Le jeton d’installation Anthropic reste disponible en tant que chemin de jeton OpenClaw pris en charge, mais OpenClaw préfère désormais la réutilisation de Claude CLI et `claude -p` lorsque disponibles.

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

### OpenAI Code (Codex)

- Fournisseur : `openai-codex`
- Authentification : OAuth (ChatGPT)
- Exemple de modèle : `openai-codex/gpt-5.4`
- CLI : `openclaw onboard --auth-choice openai-codex` ou `openclaw models auth login --provider openai-codex`
- Le transport par défaut est `auto` (WebSocket d’abord, repli SSE)
- Remplacez par modèle via `agents.defaults.models["openai-codex/<model>"].params.transport` (`"sse"`, `"websocket"`, ou `"auto"`)
- `params.serviceTier` est également transmis sur les requêtes Responses Codex natives (`chatgpt.com/backend-api`)
- Les en-têtes d’attribution OpenClaw masqués (`originator`, `version`,
  `User-Agent`) sont uniquement ajoutés sur le trafic Codex natif vers
  `chatgpt.com/backend-api`, pas sur les proxys génériques compatibles OpenAI
- Partage le même basculement `/fast` et la même configuration `params.fastMode` que `openai/*` direct ; OpenClaw mappe cela vers `service_tier=priority`
- `openai-codex/gpt-5.3-codex-spark` reste disponible lorsque le catalogue OAuth Codex l’expose ; dépend des droits
- `openai-codex/gpt-5.4` conserve `contextWindow = 1050000` natif et une valeur d’exécution par défaut `contextTokens = 272000` ; remplacez la limite d’exécution avec `models.providers.openai-codex.models[].contextTokens`
- Remarque de politique : OpenAI Codex OAuth est explicitement pris en charge pour les outils/flux de travail externes comme OpenClaw.

```json5
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
}
```

```json5
{
  models: {
    providers: {
      "openai-codex": {
        models: [{ id: "gpt-5.4", contextTokens: 160000 }],
      },
    },
  },
}
```

### Autres options hébergées de type abonnement

- [Qwen Cloud](/fr/providers/qwen) : surface de fournisseur Qwen Cloud plus mapping des points de terminaison Alibaba DashScope et Coding Plan
- [MiniMax](/fr/providers/minimax) : accès MiniMax Coding Plan par OAuth ou clé API
- [GLM Models](/fr/providers/glm) : points de terminaison Z.AI Coding Plan ou API générale

### OpenCode

- Authentification : `OPENCODE_API_KEY` (ou `OPENCODE_ZEN_API_KEY`)
- Fournisseur d’exécution Zen : `opencode`
- Fournisseur d’exécution Go : `opencode-go`
- Exemples de modèles : `opencode/claude-opus-4-6`, `opencode-go/kimi-k2.5`
- CLI : `openclaw onboard --auth-choice opencode-zen` ou `openclaw onboard --auth-choice opencode-go`

```json5
{
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-6" } } },
}
```

### Google Gemini (clé API)

- Fournisseur : `google`
- Authentification : `GEMINI_API_KEY`
- Rotation facultative : `GEMINI_API_KEYS`, `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`, solution de repli `GOOGLE_API_KEY`, et `OPENCLAW_LIVE_GEMINI_KEY` (remplacement unique)
- Exemples de modèles : `google/gemini-3.1-pro-preview`, `google/gemini-3-flash-preview`
- Compatibilité : l’ancienne configuration OpenClaw utilisant `google/gemini-3.1-flash-preview` est normalisée en `google/gemini-3-flash-preview`
- CLI : `openclaw onboard --auth-choice gemini-api-key`
- Les exécutions Gemini directes acceptent aussi `agents.defaults.models["google/<model>"].params.cachedContent`
  (ou l’ancien `cached_content`) pour transférer un handle natif du fournisseur
  `cachedContents/...` ; les accès réussis au cache Gemini apparaissent comme `cacheRead` dans OpenClaw

### Google Vertex et Gemini CLI

- Fournisseurs : `google-vertex`, `google-gemini-cli`
- Authentification : Vertex utilise gcloud ADC ; Gemini CLI utilise son flux OAuth
- Attention : OAuth Gemini CLI dans OpenClaw est une intégration non officielle. Certains utilisateurs ont signalé des restrictions sur leur compte Google après l’utilisation de clients tiers. Consultez les conditions de Google et utilisez un compte non critique si vous choisissez de continuer.
- OAuth Gemini CLI est fourni dans le Plugin `google` groupé.
  - Installez d’abord Gemini CLI :
    - `brew install gemini-cli`
    - ou `npm install -g @google/gemini-cli`
  - Activer : `openclaw plugins enable google`
  - Connexion : `openclaw models auth login --provider google-gemini-cli --set-default`
  - Modèle par défaut : `google-gemini-cli/gemini-3-flash-preview`
  - Remarque : vous ne collez **pas** d’identifiant client ni de secret dans `openclaw.json`. Le flux de connexion CLI stocke
    les jetons dans des profils d’authentification sur l’hôte de la passerelle.
  - Si les requêtes échouent après la connexion, définissez `GOOGLE_CLOUD_PROJECT` ou `GOOGLE_CLOUD_PROJECT_ID` sur l’hôte de la passerelle.
  - Les réponses JSON Gemini CLI sont analysées à partir de `response` ; l’usage se replie sur
    `stats`, avec `stats.cached` normalisé en `cacheRead` OpenClaw.

### Z.AI (GLM)

- Fournisseur : `zai`
- Authentification : `ZAI_API_KEY`
- Exemple de modèle : `zai/glm-5.1`
- CLI : `openclaw onboard --auth-choice zai-api-key`
  - Alias : `z.ai/*` et `z-ai/*` sont normalisés en `zai/*`
  - `zai-api-key` détecte automatiquement le point de terminaison Z.AI correspondant ; `zai-coding-global`, `zai-coding-cn`, `zai-global` et `zai-cn` forcent une surface spécifique

### Vercel AI Gateway

- Fournisseur : `vercel-ai-gateway`
- Authentification : `AI_GATEWAY_API_KEY`
- Exemple de modèle : `vercel-ai-gateway/anthropic/claude-opus-4.6`
- CLI : `openclaw onboard --auth-choice ai-gateway-api-key`

### Kilo Gateway

- Fournisseur : `kilocode`
- Authentification : `KILOCODE_API_KEY`
- Exemple de modèle : `kilocode/kilo/auto`
- CLI : `openclaw onboard --auth-choice kilocode-api-key`
- URL de base : `https://api.kilo.ai/api/gateway/`
- Le catalogue statique de repli inclut `kilocode/kilo/auto` ; la découverte en direct via
  `https://api.kilo.ai/api/gateway/models` peut étendre davantage le catalogue
  d’exécution.
- Le routage amont exact derrière `kilocode/kilo/auto` est géré par Kilo Gateway,
  et non codé en dur dans OpenClaw.

Voir [/providers/kilocode](/fr/providers/kilocode) pour les détails de configuration.

### Autres Plugins de fournisseur groupés

- OpenRouter : `openrouter` (`OPENROUTER_API_KEY`)
- Exemple de modèle : `openrouter/auto`
- OpenClaw applique les en-têtes d’attribution d’application documentés par OpenRouter uniquement lorsque
  la requête cible réellement `openrouter.ai`
- Les marqueurs `cache_control` Anthropic spécifiques à OpenRouter sont également limités aux
  routes OpenRouter vérifiées, et non aux URL proxy arbitraires
- OpenRouter reste sur le chemin de style proxy compatible OpenAI, donc
  la mise en forme de requête native réservée à OpenAI (`serviceTier`, `store` de Responses,
  indications de cache de prompt, charges utiles de compatibilité de raisonnement OpenAI) n’est pas transférée
- Les références OpenRouter basées sur Gemini conservent uniquement l’assainissement des signatures de pensée Gemini proxifiées ;
  la validation de rejeu Gemini native et les réécritures d’amorçage restent désactivées
- Kilo Gateway : `kilocode` (`KILOCODE_API_KEY`)
- Exemple de modèle : `kilocode/kilo/auto`
- Les références Kilo basées sur Gemini conservent le même chemin
  d’assainissement des signatures de pensée Gemini proxifiées ; `kilocode/kilo/auto` et les autres indications
  de proxy sans prise en charge du raisonnement ignorent l’injection de raisonnement par proxy
- MiniMax : `minimax` (clé API) et `minimax-portal` (OAuth)
- Authentification : `MINIMAX_API_KEY` pour `minimax` ; `MINIMAX_OAUTH_TOKEN` ou `MINIMAX_API_KEY` pour `minimax-portal`
- Exemple de modèle : `minimax/MiniMax-M2.7` ou `minimax-portal/MiniMax-M2.7`
- La configuration d’intégration/de clé API MiniMax écrit des définitions explicites du modèle M2.7 avec
  `input: ["text", "image"]` ; le catalogue du fournisseur groupé conserve les références de chat
  en mode texte uniquement jusqu’à ce que cette configuration du fournisseur soit matérialisée
- Moonshot : `moonshot` (`MOONSHOT_API_KEY`)
- Exemple de modèle : `moonshot/kimi-k2.5`
- Kimi Coding : `kimi` (`KIMI_API_KEY` ou `KIMICODE_API_KEY`)
- Exemple de modèle : `kimi/kimi-code`
- Qianfan : `qianfan` (`QIANFAN_API_KEY`)
- Exemple de modèle : `qianfan/deepseek-v3.2`
- Qwen Cloud : `qwen` (`QWEN_API_KEY`, `MODELSTUDIO_API_KEY`, ou `DASHSCOPE_API_KEY`)
- Exemple de modèle : `qwen/qwen3.5-plus`
- NVIDIA : `nvidia` (`NVIDIA_API_KEY`)
- Exemple de modèle : `nvidia/nvidia/llama-3.1-nemotron-70b-instruct`
- StepFun : `stepfun` / `stepfun-plan` (`STEPFUN_API_KEY`)
- Exemples de modèles : `stepfun/step-3.5-flash`, `stepfun-plan/step-3.5-flash-2603`
- Together : `together` (`TOGETHER_API_KEY`)
- Exemple de modèle : `together/moonshotai/Kimi-K2.5`
- Venice : `venice` (`VENICE_API_KEY`)
- Xiaomi : `xiaomi` (`XIAOMI_API_KEY`)
- Exemple de modèle : `xiaomi/mimo-v2-flash`
- Vercel AI Gateway : `vercel-ai-gateway` (`AI_GATEWAY_API_KEY`)
- Hugging Face Inference : `huggingface` (`HUGGINGFACE_HUB_TOKEN` ou `HF_TOKEN`)
- Cloudflare AI Gateway : `cloudflare-ai-gateway` (`CLOUDFLARE_AI_GATEWAY_API_KEY`)
- Volcengine : `volcengine` (`VOLCANO_ENGINE_API_KEY`)
- Exemple de modèle : `volcengine-plan/ark-code-latest`
- BytePlus : `byteplus` (`BYTEPLUS_API_KEY`)
- Exemple de modèle : `byteplus-plan/ark-code-latest`
- xAI : `xai` (`XAI_API_KEY`)
  - Les requêtes xAI natives groupées utilisent le chemin xAI Responses
  - `/fast` ou `params.fastMode: true` réécrivent `grok-3`, `grok-3-mini`,
    `grok-4` et `grok-4-0709` vers leurs variantes `*-fast`
  - `tool_stream` est activé par défaut ; définissez
    `agents.defaults.models["xai/<model>"].params.tool_stream` sur `false` pour
    le désactiver
- Mistral : `mistral` (`MISTRAL_API_KEY`)
- Exemple de modèle : `mistral/mistral-large-latest`
- CLI : `openclaw onboard --auth-choice mistral-api-key`
- Groq : `groq` (`GROQ_API_KEY`)
- Cerebras : `cerebras` (`CEREBRAS_API_KEY`)
  - Les modèles GLM sur Cerebras utilisent les identifiants `zai-glm-4.7` et `zai-glm-4.6`.
  - URL de base compatible OpenAI : `https://api.cerebras.ai/v1`.
- GitHub Copilot : `github-copilot` (`COPILOT_GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_TOKEN`)
- Exemple de modèle Hugging Face Inference : `huggingface/deepseek-ai/DeepSeek-R1` ; CLI : `openclaw onboard --auth-choice huggingface-api-key`. Voir [Hugging Face (Inference)](/fr/providers/huggingface).

## Fournisseurs via `models.providers` (personnalisé / URL de base)

Utilisez `models.providers` (ou `models.json`) pour ajouter des fournisseurs **personnalisés** ou
des proxys compatibles OpenAI/Anthropic.

Beaucoup des Plugins de fournisseur groupés ci-dessous publient déjà un catalogue par défaut.
Utilisez des entrées explicites `models.providers.<id>` uniquement lorsque vous souhaitez remplacer l’
URL de base, les en-têtes ou la liste de modèles par défaut.

### Moonshot AI (Kimi)

Moonshot est fourni comme Plugin de fournisseur groupé. Utilisez le fournisseur intégré par
défaut, et ajoutez une entrée explicite `models.providers.moonshot` uniquement lorsque vous
devez remplacer l’URL de base ou les métadonnées du modèle :

- Fournisseur : `moonshot`
- Authentification : `MOONSHOT_API_KEY`
- Exemple de modèle : `moonshot/kimi-k2.5`
- CLI : `openclaw onboard --auth-choice moonshot-api-key` ou `openclaw onboard --auth-choice moonshot-api-key-cn`

Identifiants de modèle Kimi K2 :

[//]: # "moonshot-kimi-k2-model-refs:start"

- `moonshot/kimi-k2.5`
- `moonshot/kimi-k2-thinking`
- `moonshot/kimi-k2-thinking-turbo`
- `moonshot/kimi-k2-turbo`

[//]: # "moonshot-kimi-k2-model-refs:end"

```json5
{
  agents: {
    defaults: { model: { primary: "moonshot/kimi-k2.5" } },
  },
  models: {
    mode: "merge",
    providers: {
      moonshot: {
        baseUrl: "https://api.moonshot.ai/v1",
        apiKey: "${MOONSHOT_API_KEY}",
        api: "openai-completions",
        models: [{ id: "kimi-k2.5", name: "Kimi K2.5" }],
      },
    },
  },
}
```

### Kimi Coding

Kimi Coding utilise le point de terminaison compatible Anthropic de Moonshot AI :

- Fournisseur : `kimi`
- Authentification : `KIMI_API_KEY`
- Exemple de modèle : `kimi/kimi-code`

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: { model: { primary: "kimi/kimi-code" } },
  },
}
```

L’ancien `kimi/k2p5` reste accepté comme identifiant de modèle de compatibilité.

### Volcano Engine (Doubao)

Volcano Engine (火山引擎) fournit un accès à Doubao et à d’autres modèles en Chine.

- Fournisseur : `volcengine` (coding : `volcengine-plan`)
- Authentification : `VOLCANO_ENGINE_API_KEY`
- Exemple de modèle : `volcengine-plan/ark-code-latest`
- CLI : `openclaw onboard --auth-choice volcengine-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "volcengine-plan/ark-code-latest" } },
  },
}
```

L’intégration utilise par défaut la surface coding, mais le catalogue général `volcengine/*`
est enregistré en même temps.

Dans les sélecteurs de modèle d’intégration/configuration, le choix d’authentification Volcengine privilégie à la fois
les lignes `volcengine/*` et `volcengine-plan/*`. Si ces modèles ne sont pas encore chargés,
OpenClaw se replie sur le catalogue non filtré au lieu d’afficher un sélecteur
limité au fournisseur vide.

Modèles disponibles :

- `volcengine/doubao-seed-1-8-251228` (Doubao Seed 1.8)
- `volcengine/doubao-seed-code-preview-251028`
- `volcengine/kimi-k2-5-260127` (Kimi K2.5)
- `volcengine/glm-4-7-251222` (GLM 4.7)
- `volcengine/deepseek-v3-2-251201` (DeepSeek V3.2 128K)

Modèles coding (`volcengine-plan`) :

- `volcengine-plan/ark-code-latest`
- `volcengine-plan/doubao-seed-code`
- `volcengine-plan/kimi-k2.5`
- `volcengine-plan/kimi-k2-thinking`
- `volcengine-plan/glm-4.7`

### BytePlus (International)

BytePlus ARK fournit aux utilisateurs internationaux un accès aux mêmes modèles que Volcano Engine.

- Fournisseur : `byteplus` (coding : `byteplus-plan`)
- Authentification : `BYTEPLUS_API_KEY`
- Exemple de modèle : `byteplus-plan/ark-code-latest`
- CLI : `openclaw onboard --auth-choice byteplus-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "byteplus-plan/ark-code-latest" } },
  },
}
```

L’intégration utilise par défaut la surface coding, mais le catalogue général `byteplus/*`
est enregistré en même temps.

Dans les sélecteurs de modèle d’intégration/configuration, le choix d’authentification BytePlus privilégie à la fois
les lignes `byteplus/*` et `byteplus-plan/*`. Si ces modèles ne sont pas encore chargés,
OpenClaw se replie sur le catalogue non filtré au lieu d’afficher un sélecteur
limité au fournisseur vide.

Modèles disponibles :

- `byteplus/seed-1-8-251228` (Seed 1.8)
- `byteplus/kimi-k2-5-260127` (Kimi K2.5)
- `byteplus/glm-4-7-251222` (GLM 4.7)

Modèles coding (`byteplus-plan`) :

- `byteplus-plan/ark-code-latest`
- `byteplus-plan/doubao-seed-code`
- `byteplus-plan/kimi-k2.5`
- `byteplus-plan/kimi-k2-thinking`
- `byteplus-plan/glm-4.7`

### Synthetic

Synthetic fournit des modèles compatibles Anthropic derrière le fournisseur `synthetic` :

- Fournisseur : `synthetic`
- Authentification : `SYNTHETIC_API_KEY`
- Exemple de modèle : `synthetic/hf:MiniMaxAI/MiniMax-M2.5`
- CLI : `openclaw onboard --auth-choice synthetic-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "synthetic/hf:MiniMaxAI/MiniMax-M2.5" } },
  },
  models: {
    mode: "merge",
    providers: {
      synthetic: {
        baseUrl: "https://api.synthetic.new/anthropic",
        apiKey: "${SYNTHETIC_API_KEY}",
        api: "anthropic-messages",
        models: [{ id: "hf:MiniMaxAI/MiniMax-M2.5", name: "MiniMax M2.5" }],
      },
    },
  },
}
```

### MiniMax

MiniMax se configure via `models.providers` car il utilise des points de terminaison personnalisés :

- MiniMax OAuth (Global) : `--auth-choice minimax-global-oauth`
- MiniMax OAuth (CN) : `--auth-choice minimax-cn-oauth`
- Clé API MiniMax (Global) : `--auth-choice minimax-global-api`
- Clé API MiniMax (CN) : `--auth-choice minimax-cn-api`
- Authentification : `MINIMAX_API_KEY` pour `minimax` ; `MINIMAX_OAUTH_TOKEN` ou
  `MINIMAX_API_KEY` pour `minimax-portal`

Voir [/providers/minimax](/fr/providers/minimax) pour les détails de configuration, les options de modèle et les extraits de configuration.

Sur le chemin de streaming compatible Anthropic de MiniMax, OpenClaw désactive thinking par
défaut sauf si vous le définissez explicitement, et `/fast on` réécrit
`MiniMax-M2.7` en `MiniMax-M2.7-highspeed`.

Répartition des capacités gérées par le Plugin :

- Les valeurs par défaut texte/chat restent sur `minimax/MiniMax-M2.7`
- La génération d’images est `minimax/image-01` ou `minimax-portal/image-01`
- La compréhension d’images est gérée par le Plugin avec `MiniMax-VL-01` sur les deux chemins d’authentification MiniMax
- La recherche web reste sur l’identifiant de fournisseur `minimax`

### LM Studio

LM Studio est fourni comme Plugin de fournisseur groupé utilisant l’API native :

- Fournisseur : `lmstudio`
- Authentification : `LM_API_TOKEN`
- URL de base d’inférence par défaut : `http://localhost:1234/v1`

Ensuite, définissez un modèle (remplacez par l’un des identifiants renvoyés par `http://localhost:1234/api/v1/models`) :

```json5
{
  agents: {
    defaults: { model: { primary: "lmstudio/openai/gpt-oss-20b" } },
  },
}
```

OpenClaw utilise `/api/v1/models` et `/api/v1/models/load` natifs de LM Studio
pour la découverte + le chargement automatique, avec `/v1/chat/completions` pour l’inférence par défaut.
Voir [/providers/lmstudio](/fr/providers/lmstudio) pour la configuration et le dépannage.

### Ollama

Ollama est fourni comme Plugin de fournisseur groupé et utilise l’API native d’Ollama :

- Fournisseur : `ollama`
- Authentification : aucune requise (serveur local)
- Exemple de modèle : `ollama/llama3.3`
- Installation : [https://ollama.com/download](https://ollama.com/download)

```bash
# Installez Ollama, puis téléchargez un modèle :
ollama pull llama3.3
```

```json5
{
  agents: {
    defaults: { model: { primary: "ollama/llama3.3" } },
  },
}
```

Ollama est détecté localement à `http://127.0.0.1:11434` lorsque vous activez l’option avec
`OLLAMA_API_KEY`, et le Plugin de fournisseur groupé ajoute directement Ollama à
`openclaw onboard` et au sélecteur de modèle. Voir [/providers/ollama](/fr/providers/ollama)
pour l’intégration, le mode cloud/local et la configuration personnalisée.

### vLLM

vLLM est fourni comme Plugin de fournisseur groupé pour les serveurs locaux/autohébergés compatibles OpenAI
:

- Fournisseur : `vllm`
- Authentification : facultative (selon votre serveur)
- URL de base par défaut : `http://127.0.0.1:8000/v1`

Pour activer la découverte automatique en local (n’importe quelle valeur fonctionne si votre serveur n’impose pas l’authentification) :

```bash
export VLLM_API_KEY="vllm-local"
```

Ensuite, définissez un modèle (remplacez par l’un des identifiants renvoyés par `/v1/models`) :

```json5
{
  agents: {
    defaults: { model: { primary: "vllm/your-model-id" } },
  },
}
```

Voir [/providers/vllm](/fr/providers/vllm) pour plus de détails.

### SGLang

SGLang est fourni comme Plugin de fournisseur groupé pour les serveurs autohébergés rapides
compatibles OpenAI :

- Fournisseur : `sglang`
- Authentification : facultative (selon votre serveur)
- URL de base par défaut : `http://127.0.0.1:30000/v1`

Pour activer la découverte automatique en local (n’importe quelle valeur fonctionne si votre serveur n’impose pas
l’authentification) :

```bash
export SGLANG_API_KEY="sglang-local"
```

Ensuite, définissez un modèle (remplacez par l’un des identifiants renvoyés par `/v1/models`) :

```json5
{
  agents: {
    defaults: { model: { primary: "sglang/your-model-id" } },
  },
}
```

Voir [/providers/sglang](/fr/providers/sglang) pour plus de détails.

### Proxys locaux (LM Studio, vLLM, LiteLLM, etc.)

Exemple (compatible OpenAI) :

```json5
{
  agents: {
    defaults: {
      model: { primary: "lmstudio/my-local-model" },
      models: { "lmstudio/my-local-model": { alias: "Local" } },
    },
  },
  models: {
    providers: {
      lmstudio: {
        baseUrl: "http://localhost:1234/v1",
        apiKey: "${LM_API_TOKEN}",
        api: "openai-completions",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 200000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

Remarques :

- Pour les fournisseurs personnalisés, `reasoning`, `input`, `cost`, `contextWindow` et `maxTokens` sont facultatifs.
  Lorsqu’ils sont omis, OpenClaw utilise par défaut :
  - `reasoning: false`
  - `input: ["text"]`
  - `cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 }`
  - `contextWindow: 200000`
  - `maxTokens: 8192`
- Recommandé : définissez des valeurs explicites correspondant aux limites de votre proxy/modèle.
- Pour `api: "openai-completions"` sur des points de terminaison non natifs (tout `baseUrl` non vide dont l’hôte n’est pas `api.openai.com`), OpenClaw force `compat.supportsDeveloperRole: false` afin d’éviter les erreurs 400 du fournisseur pour les rôles `developer` non pris en charge.
- Les routes compatibles OpenAI de style proxy ignorent également la mise en forme de requête native réservée à OpenAI :
  pas de `service_tier`, pas de `store` Responses, pas d’indications de cache de prompt, pas de
  mise en forme de charge utile de compatibilité de raisonnement OpenAI, et pas d’en-têtes d’attribution OpenClaw masqués.
- Si `baseUrl` est vide/omis, OpenClaw conserve le comportement OpenAI par défaut (qui se résout vers `api.openai.com`).
- Par sécurité, une valeur explicite `compat.supportsDeveloperRole: true` est quand même remplacée sur les points de terminaison non natifs `openai-completions`.

## Exemples CLI

```bash
openclaw onboard --auth-choice opencode-zen
openclaw models set opencode/claude-opus-4-6
openclaw models list
```

Voir aussi : [/gateway/configuration](/fr/gateway/configuration) pour des exemples complets de configuration.

## Liens connexes

- [Models](/fr/concepts/models) — configuration des modèles et alias
- [Model Failover](/fr/concepts/model-failover) — chaînes de repli et comportement de nouvelle tentative
- [Configuration Reference](/fr/gateway/configuration-reference#agent-defaults) — clés de configuration des modèles
- [Providers](/fr/providers) — guides de configuration par fournisseur
