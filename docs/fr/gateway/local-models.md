---
read_when:
    - Vous souhaitez servir des modèles depuis votre propre machine GPU
    - Vous configurez LM Studio ou un proxy compatible OpenAI
    - Vous avez besoin des conseils les plus sûrs pour les modèles locaux
summary: Exécutez OpenClaw sur des LLM locaux (LM Studio, vLLM, LiteLLM, points de terminaison OpenAI personnalisés)
title: Modèles locaux
x-i18n:
    generated_at: "2026-04-13T08:50:46Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3ecb61b3e6e34d3666f9b688cd694d92c5fb211cf8c420fa876f7ccf5789154a
    source_path: gateway/local-models.md
    workflow: 15
---

# Modèles locaux

Le local est possible, mais OpenClaw attend un grand contexte ainsi que de solides défenses contre les injections de prompt. Les petites cartes tronquent le contexte et affaiblissent la sécurité. Visez haut : **≥2 Mac Studios au maximum de leur capacité ou une machine GPU équivalente (~30 k$+)**. Un seul GPU de **24 Go** ne fonctionne que pour des prompts plus légers avec une latence plus élevée. Utilisez la **variante de modèle la plus grande / pleine taille que vous pouvez exécuter** ; les checkpoints fortement quantifiés ou « small » augmentent le risque d’injection de prompt (voir [Sécurité](/fr/gateway/security)).

Si vous souhaitez la configuration locale avec le moins de friction, commencez par [LM Studio](/fr/providers/lmstudio) ou [Ollama](/fr/providers/ollama) et `openclaw onboard`. Cette page est le guide prescriptif pour les piles locales haut de gamme et les serveurs locaux personnalisés compatibles OpenAI.

## Recommandé : LM Studio + grand modèle local (API Responses)

La meilleure pile locale actuelle. Chargez un grand modèle dans LM Studio (par exemple, une version pleine taille de Qwen, DeepSeek ou Llama), activez le serveur local (par défaut `http://127.0.0.1:1234`), et utilisez l’API Responses pour garder le raisonnement séparé du texte final.

```json5
{
  agents: {
    defaults: {
      model: { primary: “lmstudio/my-local-model” },
      models: {
        “anthropic/claude-opus-4-6”: { alias: “Opus” },
        “lmstudio/my-local-model”: { alias: “Local” },
      },
    },
  },
  models: {
    mode: “merge”,
    providers: {
      lmstudio: {
        baseUrl: “http://127.0.0.1:1234/v1”,
        apiKey: “lmstudio”,
        api: “openai-responses”,
        models: [
          {
            id: “my-local-model”,
            name: “Local Model”,
            reasoning: false,
            input: [“text”],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 196608,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

**Liste de configuration**

- Installez LM Studio : [https://lmstudio.ai](https://lmstudio.ai)
- Dans LM Studio, téléchargez la **plus grande version de modèle disponible** (évitez les variantes « small » / fortement quantifiées), démarrez le serveur, confirmez que `http://127.0.0.1:1234/v1/models` l’affiche.
- Remplacez `my-local-model` par l’identifiant réel du modèle affiché dans LM Studio.
- Gardez le modèle chargé ; le chargement à froid ajoute de la latence au démarrage.
- Ajustez `contextWindow`/`maxTokens` si votre version de LM Studio diffère.
- Pour WhatsApp, restez sur l’API Responses afin que seul le texte final soit envoyé.

Gardez les modèles hébergés configurés même lorsque vous exécutez du local ; utilisez `models.mode: "merge"` afin que les solutions de repli restent disponibles.

### Configuration hybride : primaire hébergé, repli local

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-6",
        fallbacks: ["lmstudio/my-local-model", "anthropic/claude-opus-4-6"],
      },
      models: {
        "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
        "lmstudio/my-local-model": { alias: "Local" },
        "anthropic/claude-opus-4-6": { alias: "Opus" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      lmstudio: {
        baseUrl: "http://127.0.0.1:1234/v1",
        apiKey: "lmstudio",
        api: "openai-responses",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 196608,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

### Priorité au local avec filet de sécurité hébergé

Inversez l’ordre du primaire et du repli ; conservez le même bloc providers et `models.mode: "merge"` afin de pouvoir basculer vers Sonnet ou Opus lorsque la machine locale est indisponible.

### Hébergement régional / routage des données

- Des variantes MiniMax/Kimi/GLM hébergées existent aussi sur OpenRouter avec des points de terminaison fixés par région (par exemple, hébergés aux États-Unis). Choisissez la variante régionale là-bas pour conserver le trafic dans la juridiction souhaitée tout en utilisant `models.mode: "merge"` pour les replis Anthropic/OpenAI.
- Le tout-local reste la voie la plus forte pour la confidentialité ; le routage régional hébergé est l’option intermédiaire lorsque vous avez besoin de fonctionnalités du fournisseur tout en voulant garder le contrôle sur le flux de données.

## Autres proxys locaux compatibles OpenAI

vLLM, LiteLLM, OAI-proxy ou des passerelles personnalisées fonctionnent s’ils exposent un point de terminaison `/v1` de style OpenAI. Remplacez le bloc provider ci-dessus par votre point de terminaison et l’identifiant de modèle :

```json5
{
  models: {
    mode: "merge",
    providers: {
      local: {
        baseUrl: "http://127.0.0.1:8000/v1",
        apiKey: "sk-local",
        api: "openai-responses",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 120000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

Conservez `models.mode: "merge"` afin que les modèles hébergés restent disponibles en repli.

Remarque de comportement pour les backends `/v1` locaux / proxifiés :

- OpenClaw les traite comme des routes compatibles OpenAI de type proxy, et non comme des points de terminaison OpenAI natifs
- la mise en forme des requêtes propre à OpenAI natif ne s’applique pas ici : pas de `service_tier`, pas de `store` pour Responses, pas de mise en forme de charge utile de compatibilité de raisonnement OpenAI, et pas d’indices de cache de prompt
- les en-têtes d’attribution OpenClaw cachés (`originator`, `version`, `User-Agent`) ne sont pas injectés sur ces URL de proxy personnalisées

Notes de compatibilité pour les backends compatibles OpenAI plus stricts :

- Certains serveurs n’acceptent que `messages[].content` sous forme de chaîne sur Chat Completions, et non des tableaux structurés de parties de contenu. Définissez `models.providers.<provider>.models[].compat.requiresStringContent: true` pour ces points de terminaison.
- Certains backends locaux plus petits ou plus stricts sont instables avec la forme complète des prompts du runtime d’agent d’OpenClaw, en particulier lorsque des schémas d’outils sont inclus. Si le backend fonctionne pour de petits appels directs `/v1/chat/completions` mais échoue sur des tours d’agent OpenClaw normaux, essayez d’abord `models.providers.<provider>.models[].compat.supportsTools: false`.
- Si le backend échoue encore uniquement sur des exécutions OpenClaw plus volumineuses, le problème restant est généralement une limite en amont du modèle/serveur ou un bug du backend, et non de la couche de transport d’OpenClaw.

## Dépannage

- Gateway peut joindre le proxy ? `curl http://127.0.0.1:1234/v1/models`.
- Modèle LM Studio déchargé ? Rechargez-le ; le démarrage à froid est une cause fréquente de « blocage ».
- Erreurs de contexte ? Réduisez `contextWindow` ou augmentez la limite de votre serveur.
- Le serveur compatible OpenAI renvoie `messages[].content ... expected a string` ? Ajoutez `compat.requiresStringContent: true` sur cette entrée de modèle.
- Les petits appels directs `/v1/chat/completions` fonctionnent, mais `openclaw infer model run` échoue sur Gemma ou un autre modèle local ? Désactivez d’abord les schémas d’outils avec `compat.supportsTools: false`, puis retestez. Si le serveur plante encore uniquement sur de plus grands prompts OpenClaw, traitez cela comme une limite du serveur/modèle en amont.
- Sécurité : les modèles locaux contournent les filtres côté fournisseur ; gardez des agents ciblés et Compaction activé afin de limiter le rayon d’impact des injections de prompt.
