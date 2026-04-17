---
read_when:
    - Vous voulez comprendre quelles fonctionnalités peuvent appeler des API payantes
    - Vous devez auditer les clés, les coûts et la visibilité de l’utilisation
    - Vous expliquez les rapports de coûts de /status ou /usage
summary: Vérifiez ce qui peut entraîner des coûts, quelles clés sont utilisées et comment consulter l’utilisation
title: Utilisation et coûts de l’API
x-i18n:
    generated_at: "2026-04-13T08:50:36Z"
    model: gpt-5.4
    provider: openai
    source_hash: f5077e74d38ef781ac7a72603e9f9e3829a628b95c5a9967915ab0f321565429
    source_path: reference/api-usage-costs.md
    workflow: 15
---

# Utilisation et coûts de l’API

Ce document répertorie les **fonctionnalités qui peuvent invoquer des clés API** et où leurs coûts apparaissent. Il se concentre sur les fonctionnalités d’OpenClaw qui peuvent générer une utilisation du fournisseur ou des appels d’API payants.

## Où les coûts apparaissent (chat + CLI)

**Instantané du coût par session**

- `/status` affiche le modèle actuel de la session, l’utilisation du contexte et les jetons de la dernière réponse.
- Si le modèle utilise une **authentification par clé API**, `/status` affiche aussi le **coût estimé** de la dernière réponse.
- Si les métadonnées de session en direct sont limitées, `/status` peut aussi récupérer les compteurs de jetons/cache et l’étiquette du modèle d’exécution actif à partir de la dernière entrée d’utilisation du transcript. Les valeurs en direct non nulles existantes restent prioritaires, et les totaux du transcript dimensionnés par prompt peuvent prévaloir lorsque les totaux stockés sont absents ou plus faibles.

**Pied de page de coût par message**

- `/usage full` ajoute un pied de page d’utilisation à chaque réponse, y compris le **coût estimé** (clé API uniquement).
- `/usage tokens` affiche uniquement les jetons ; les flux OAuth/jeton de type abonnement et les flux CLI masquent le coût en dollars.
- Remarque Gemini CLI : lorsque la CLI renvoie une sortie JSON, OpenClaw lit l’utilisation depuis `stats`, normalise `stats.cached` en `cacheRead`, et déduit les jetons d’entrée à partir de `stats.input_tokens - stats.cached` si nécessaire.

Remarque Anthropic : l’équipe Anthropic nous a indiqué que l’utilisation de Claude CLI de type OpenClaw est à nouveau autorisée, donc OpenClaw considère la réutilisation de Claude CLI et l’utilisation de `claude -p` comme approuvées pour cette intégration, sauf si Anthropic publie une nouvelle politique.
Anthropic n’expose toujours pas d’estimation en dollars par message qu’OpenClaw puisse afficher dans `/usage full`.

**Fenêtres d’utilisation CLI (quotas fournisseur)**

- `openclaw status --usage` et `openclaw channels list` affichent les **fenêtres d’utilisation** du fournisseur (instantanés de quota, pas les coûts par message).
- La sortie lisible est normalisée en `X% left` pour tous les fournisseurs.
- Fournisseurs de fenêtres d’utilisation actuellement pris en charge : Anthropic, GitHub Copilot, Gemini CLI, OpenAI Codex, MiniMax, Xiaomi et z.ai.
- Remarque MiniMax : ses champs bruts `usage_percent` / `usagePercent` signifient le quota restant, donc OpenClaw les inverse avant affichage. Les champs basés sur le comptage restent prioritaires lorsqu’ils sont présents. Si le fournisseur renvoie `model_remains`, OpenClaw privilégie l’entrée du modèle de chat, déduit l’étiquette de fenêtre à partir des horodatages si nécessaire, et inclut le nom du modèle dans l’étiquette du plan.
- L’authentification d’utilisation pour ces fenêtres de quota provient de hooks spécifiques au fournisseur lorsqu’ils sont disponibles ; sinon, OpenClaw revient à la correspondance des identifiants OAuth/clé API depuis les profils d’authentification, l’environnement ou la configuration.

Consultez [Utilisation des jetons et coûts](/fr/reference/token-use) pour les détails et des exemples.

## Comment les clés sont découvertes

OpenClaw peut récupérer les identifiants depuis :

- **Profils d’authentification** (par agent, stockés dans `auth-profiles.json`).
- **Variables d’environnement** (par exemple `OPENAI_API_KEY`, `BRAVE_API_KEY`, `FIRECRAWL_API_KEY`).
- **Configuration** (`models.providers.*.apiKey`, `plugins.entries.*.config.webSearch.apiKey`,
  `plugins.entries.firecrawl.config.webFetch.apiKey`, `memorySearch.*`,
  `talk.providers.*.apiKey`).
- **Skills** (`skills.entries.<name>.apiKey`) qui peuvent exporter des clés vers l’environnement du processus de la compétence.

## Fonctionnalités qui peuvent consommer des clés

### 1) Réponses du modèle principal (chat + outils)

Chaque réponse ou appel d’outil utilise le **fournisseur de modèle actuel** (OpenAI, Anthropic, etc.). Il s’agit de la principale source d’utilisation et de coût.

Cela inclut aussi les fournisseurs hébergés de type abonnement qui facturent tout de même en dehors de l’interface locale d’OpenClaw, comme **OpenAI Codex**, **Alibaba Cloud Model Studio
Coding Plan**, **MiniMax Coding Plan**, **Z.AI / GLM Coding Plan**, et le parcours Claude-login d’OpenClaw d’Anthropic avec **Extra Usage** activé.

Consultez [Modèles](/fr/providers/models) pour la configuration tarifaire et [Utilisation des jetons et coûts](/fr/reference/token-use) pour l’affichage.

### 2) Compréhension des médias (audio/image/vidéo)

Les médias entrants peuvent être résumés/transcrits avant l’exécution de la réponse. Cela utilise des API de modèle/fournisseur.

- Audio : OpenAI / Groq / Deepgram / Google / Mistral.
- Image : OpenAI / OpenRouter / Anthropic / Google / MiniMax / Moonshot / Qwen / Z.AI.
- Vidéo : Google / Qwen / Moonshot.

Consultez [Compréhension des médias](/fr/nodes/media-understanding).

### 3) Génération d’images et de vidéos

Les capacités de génération partagées peuvent aussi consommer des clés de fournisseur :

- Génération d’image : OpenAI / Google / fal / MiniMax
- Génération de vidéo : Qwen

La génération d’image peut déduire un fournisseur par défaut adossé à l’authentification lorsque
`agents.defaults.imageGenerationModel` n’est pas défini. La génération de vidéo exige actuellement
un `agents.defaults.videoGenerationModel` explicite tel que
`qwen/wan2.6-t2v`.

Consultez [Génération d’image](/fr/tools/image-generation), [Qwen Cloud](/fr/providers/qwen),
et [Modèles](/fr/concepts/models).

### 4) Embeddings de mémoire + recherche sémantique

La recherche sémantique en mémoire utilise des **API d’embeddings** lorsqu’elle est configurée pour des fournisseurs distants :

- `memorySearch.provider = "openai"` → embeddings OpenAI
- `memorySearch.provider = "gemini"` → embeddings Gemini
- `memorySearch.provider = "voyage"` → embeddings Voyage
- `memorySearch.provider = "mistral"` → embeddings Mistral
- `memorySearch.provider = "lmstudio"` → embeddings LM Studio (local/auto-hébergé)
- `memorySearch.provider = "ollama"` → embeddings Ollama (local/auto-hébergé ; généralement sans facturation d’API hébergée)
- Repli facultatif vers un fournisseur distant si les embeddings locaux échouent

Vous pouvez rester en local avec `memorySearch.provider = "local"` (aucune utilisation d’API).

Consultez [Mémoire](/fr/concepts/memory).

### 5) Outil de recherche web

`web_search` peut entraîner des frais d’utilisation selon votre fournisseur :

- **Brave Search API** : `BRAVE_API_KEY` ou `plugins.entries.brave.config.webSearch.apiKey`
- **Exa** : `EXA_API_KEY` ou `plugins.entries.exa.config.webSearch.apiKey`
- **Firecrawl** : `FIRECRAWL_API_KEY` ou `plugins.entries.firecrawl.config.webSearch.apiKey`
- **Gemini (Google Search)** : `GEMINI_API_KEY` ou `plugins.entries.google.config.webSearch.apiKey`
- **Grok (xAI)** : `XAI_API_KEY` ou `plugins.entries.xai.config.webSearch.apiKey`
- **Kimi (Moonshot)** : `KIMI_API_KEY`, `MOONSHOT_API_KEY`, ou `plugins.entries.moonshot.config.webSearch.apiKey`
- **MiniMax Search** : `MINIMAX_CODE_PLAN_KEY`, `MINIMAX_CODING_API_KEY`, `MINIMAX_API_KEY`, ou `plugins.entries.minimax.config.webSearch.apiKey`
- **Ollama Web Search** : sans clé par défaut, mais nécessite un hôte Ollama accessible plus `ollama signin` ; peut aussi réutiliser l’authentification bearer normale du fournisseur Ollama lorsque l’hôte l’exige
- **Perplexity Search API** : `PERPLEXITY_API_KEY`, `OPENROUTER_API_KEY`, ou `plugins.entries.perplexity.config.webSearch.apiKey`
- **Tavily** : `TAVILY_API_KEY` ou `plugins.entries.tavily.config.webSearch.apiKey`
- **DuckDuckGo** : solution de repli sans clé (sans facturation d’API, mais non officielle et basée sur HTML)
- **SearXNG** : `SEARXNG_BASE_URL` ou `plugins.entries.searxng.config.webSearch.baseUrl` (sans clé/auto-hébergé ; sans facturation d’API hébergée)

Les chemins de fournisseur hérités `tools.web.search.*` se chargent encore via le shim de compatibilité temporaire, mais ils ne sont plus la surface de configuration recommandée.

**Crédit gratuit Brave Search :** chaque forfait Brave inclut 5 $/mois de crédit gratuit renouvelable. Le forfait Search coûte 5 $ pour 1 000 requêtes, donc ce crédit couvre 1 000 requêtes/mois sans frais. Définissez votre limite d’utilisation dans le tableau de bord Brave pour éviter des frais inattendus.

Consultez [Outils web](/fr/tools/web).

### 5) Outil de récupération web (Firecrawl)

`web_fetch` peut appeler **Firecrawl** lorsqu’une clé API est présente :

- `FIRECRAWL_API_KEY` ou `plugins.entries.firecrawl.config.webFetch.apiKey`

Si Firecrawl n’est pas configuré, l’outil revient à une récupération directe + readability (aucune API payante).

Consultez [Outils web](/fr/tools/web).

### 6) Instantanés d’utilisation fournisseur (statut/santé)

Certaines commandes de statut appellent des **endpoints d’utilisation fournisseur** pour afficher les fenêtres de quota ou l’état de l’authentification.
Il s’agit généralement d’appels à faible volume, mais ils sollicitent tout de même les API du fournisseur :

- `openclaw status --usage`
- `openclaw models status --json`

Consultez [CLI des modèles](/cli/models).

### 7) Résumé de protection Compaction

La protection Compaction peut résumer l’historique de session à l’aide du **modèle actuel**, ce qui invoque des API de fournisseur lorsqu’elle s’exécute.

Consultez [Gestion des sessions + compaction](/fr/reference/session-management-compaction).

### 8) Analyse / sondage des modèles

`openclaw models scan` peut sonder les modèles OpenRouter et utilise `OPENROUTER_API_KEY` lorsque
le sondage est activé.

Consultez [CLI des modèles](/cli/models).

### 9) Talk (parole)

Le mode Talk peut invoquer **ElevenLabs** lorsqu’il est configuré :

- `ELEVENLABS_API_KEY` ou `talk.providers.elevenlabs.apiKey`

Consultez [Mode Talk](/fr/nodes/talk).

### 10) Skills (API tierces)

Les Skills peuvent stocker `apiKey` dans `skills.entries.<name>.apiKey`. Si une compétence utilise cette clé pour des API externes, elle peut entraîner des coûts selon le fournisseur de la compétence.

Consultez [Skills](/fr/tools/skills).
