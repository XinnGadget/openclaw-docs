---
read_when:
    - Vous créez un nouveau plugin de fournisseur de modèles
    - Vous voulez ajouter un proxy compatible OpenAI ou un LLM personnalisé à OpenClaw
    - Vous devez comprendre l’authentification des fournisseurs, les catalogues et les hooks d’exécution
sidebarTitle: Provider Plugins
summary: Guide étape par étape pour créer un plugin de fournisseur de modèles pour OpenClaw
title: Création de plugins de fournisseur
x-i18n:
    generated_at: "2026-04-11T02:46:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: 06d7c5da6556dc3d9673a31142ff65eb67ddc97fc0c1a6f4826a2c7693ecd5e3
    source_path: plugins/sdk-provider-plugins.md
    workflow: 15
---

# Création de plugins de fournisseur

Ce guide vous accompagne dans la création d’un plugin de fournisseur qui ajoute un fournisseur de modèles
(LLM) à OpenClaw. À la fin, vous disposerez d’un fournisseur avec un catalogue de modèles,
une authentification par clé API et une résolution dynamique des modèles.

<Info>
  Si vous n’avez encore créé aucun plugin OpenClaw, lisez d’abord
  [Getting Started](/fr/plugins/building-plugins) pour la structure de package de base
  et la configuration du manifeste.
</Info>

<Tip>
  Les plugins de fournisseur ajoutent des modèles à la boucle d’inférence normale d’OpenClaw. Si le modèle
  doit s’exécuter via un démon d’agent natif qui gère les threads, la compaction ou les événements
  d’outil, associez le fournisseur à un [harnais d’agent](/fr/plugins/sdk-agent-harness)
  au lieu de mettre les détails du protocole du démon dans le cœur.
</Tip>

## Procédure pas à pas

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="Package et manifeste">
    <CodeGroup>
    ```json package.json
    {
      "name": "@myorg/openclaw-acme-ai",
      "version": "1.0.0",
      "type": "module",
      "openclaw": {
        "extensions": ["./index.ts"],
        "providers": ["acme-ai"],
        "compat": {
          "pluginApi": ">=2026.3.24-beta.2",
          "minGatewayVersion": "2026.3.24-beta.2"
        },
        "build": {
          "openclawVersion": "2026.3.24-beta.2",
          "pluginSdkVersion": "2026.3.24-beta.2"
        }
      }
    }
    ```

    ```json openclaw.plugin.json
    {
      "id": "acme-ai",
      "name": "Acme AI",
      "description": "Fournisseur de modèles Acme AI",
      "providers": ["acme-ai"],
      "modelSupport": {
        "modelPrefixes": ["acme-"]
      },
      "providerAuthEnvVars": {
        "acme-ai": ["ACME_AI_API_KEY"]
      },
      "providerAuthAliases": {
        "acme-ai-coding": "acme-ai"
      },
      "providerAuthChoices": [
        {
          "provider": "acme-ai",
          "method": "api-key",
          "choiceId": "acme-ai-api-key",
          "choiceLabel": "Clé API Acme AI",
          "groupId": "acme-ai",
          "groupLabel": "Acme AI",
          "cliFlag": "--acme-ai-api-key",
          "cliOption": "--acme-ai-api-key <key>",
          "cliDescription": "Clé API Acme AI"
        }
      ],
      "configSchema": {
        "type": "object",
        "additionalProperties": false
      }
    }
    ```
    </CodeGroup>

    Le manifeste déclare `providerAuthEnvVars` afin qu’OpenClaw puisse détecter
    les identifiants sans charger l’exécution de votre plugin. Ajoutez `providerAuthAliases`
    lorsqu’une variante de fournisseur doit réutiliser l’authentification d’un autre identifiant de fournisseur. `modelSupport`
    est facultatif et permet à OpenClaw de charger automatiquement votre plugin de fournisseur à partir
    d’identifiants de modèle abrégés comme `acme-large` avant que les hooks d’exécution n’existent. Si vous publiez le
    fournisseur sur ClawHub, les champs `openclaw.compat` et `openclaw.build`
    sont requis dans `package.json`.

  </Step>

  <Step title="Enregistrer le fournisseur">
    Un fournisseur minimal a besoin de `id`, `label`, `auth` et `catalog` :

    ```typescript index.ts
    import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
    import { createProviderApiKeyAuthMethod } from "openclaw/plugin-sdk/provider-auth";

    export default definePluginEntry({
      id: "acme-ai",
      name: "Acme AI",
      description: "Fournisseur de modèles Acme AI",
      register(api) {
        api.registerProvider({
          id: "acme-ai",
          label: "Acme AI",
          docsPath: "/providers/acme-ai",
          envVars: ["ACME_AI_API_KEY"],

          auth: [
            createProviderApiKeyAuthMethod({
              providerId: "acme-ai",
              methodId: "api-key",
              label: "Clé API Acme AI",
              hint: "Clé API depuis votre tableau de bord Acme AI",
              optionKey: "acmeAiApiKey",
              flagName: "--acme-ai-api-key",
              envVar: "ACME_AI_API_KEY",
              promptMessage: "Saisissez votre clé API Acme AI",
              defaultModel: "acme-ai/acme-large",
            }),
          ],

          catalog: {
            order: "simple",
            run: async (ctx) => {
              const apiKey =
                ctx.resolveProviderApiKey("acme-ai").apiKey;
              if (!apiKey) return null;
              return {
                provider: {
                  baseUrl: "https://api.acme-ai.com/v1",
                  apiKey,
                  api: "openai-completions",
                  models: [
                    {
                      id: "acme-large",
                      name: "Acme Large",
                      reasoning: true,
                      input: ["text", "image"],
                      cost: { input: 3, output: 15, cacheRead: 0.3, cacheWrite: 3.75 },
                      contextWindow: 200000,
                      maxTokens: 32768,
                    },
                    {
                      id: "acme-small",
                      name: "Acme Small",
                      reasoning: false,
                      input: ["text"],
                      cost: { input: 1, output: 5, cacheRead: 0.1, cacheWrite: 1.25 },
                      contextWindow: 128000,
                      maxTokens: 8192,
                    },
                  ],
                },
              };
            },
          },
        });
      },
    });
    ```

    C’est un fournisseur fonctionnel. Les utilisateurs peuvent désormais exécuter
    `openclaw onboard --acme-ai-api-key <key>` et sélectionner
    `acme-ai/acme-large` comme modèle.

    Si le fournisseur amont utilise des jetons de contrôle différents de ceux d’OpenClaw, ajoutez une
    petite transformation de texte bidirectionnelle au lieu de remplacer le chemin de flux :

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

    `input` réécrit l’invite système finale et le contenu des messages texte avant
    le transport. `output` réécrit les deltas de texte de l’assistant et le texte final avant
    qu’OpenClaw n’analyse ses propres marqueurs de contrôle ou la livraison au canal.

    Pour les fournisseurs intégrés qui enregistrent seulement un fournisseur de texte avec authentification
    par clé API plus une seule exécution adossée à un catalogue, préférez l’assistant plus étroit
    `defineSingleProviderPluginEntry(...)` :

    ```typescript
    import { defineSingleProviderPluginEntry } from "openclaw/plugin-sdk/provider-entry";

    export default defineSingleProviderPluginEntry({
      id: "acme-ai",
      name: "Acme AI",
      description: "Fournisseur de modèles Acme AI",
      provider: {
        label: "Acme AI",
        docsPath: "/providers/acme-ai",
        auth: [
          {
            methodId: "api-key",
            label: "Clé API Acme AI",
            hint: "Clé API depuis votre tableau de bord Acme AI",
            optionKey: "acmeAiApiKey",
            flagName: "--acme-ai-api-key",
            envVar: "ACME_AI_API_KEY",
            promptMessage: "Saisissez votre clé API Acme AI",
            defaultModel: "acme-ai/acme-large",
          },
        ],
        catalog: {
          buildProvider: () => ({
            api: "openai-completions",
            baseUrl: "https://api.acme-ai.com/v1",
            models: [{ id: "acme-large", name: "Acme Large" }],
          }),
        },
      },
    });
    ```

    Si votre flux d’authentification doit aussi corriger `models.providers.*`, les alias et
    le modèle par défaut de l’agent pendant l’intégration, utilisez les assistants prédéfinis de
    `openclaw/plugin-sdk/provider-onboard`. Les assistants les plus ciblés sont
    `createDefaultModelPresetAppliers(...)`,
    `createDefaultModelsPresetAppliers(...)` et
    `createModelCatalogPresetAppliers(...)`.

    Lorsqu’un point de terminaison natif de fournisseur prend en charge les blocs d’utilisation en streaming sur le
    transport normal `openai-completions`, préférez les assistants de catalogue partagés dans
    `openclaw/plugin-sdk/provider-catalog-shared` au lieu de coder en dur des vérifications d’identifiant
    de fournisseur. `supportsNativeStreamingUsageCompat(...)` et
    `applyProviderNativeStreamingUsageCompat(...)` détectent la prise en charge à partir de la carte des capacités du point de terminaison, de sorte que les points de terminaison natifs de type Moonshot/DashScope continuent
    d’être activés même lorsqu’un plugin utilise un identifiant de fournisseur personnalisé.

  </Step>

  <Step title="Ajouter la résolution dynamique des modèles">
    Si votre fournisseur accepte des identifiants de modèle arbitraires (comme un proxy ou un routeur),
    ajoutez `resolveDynamicModel` :

    ```typescript
    api.registerProvider({
      // ... id, label, auth, catalog ci-dessus

      resolveDynamicModel: (ctx) => ({
        id: ctx.modelId,
        name: ctx.modelId,
        provider: "acme-ai",
        api: "openai-completions",
        baseUrl: "https://api.acme-ai.com/v1",
        reasoning: false,
        input: ["text"],
        cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
        contextWindow: 128000,
        maxTokens: 8192,
      }),
    });
    ```

    Si la résolution nécessite un appel réseau, utilisez `prepareDynamicModel` pour un
    préchauffage asynchrone — `resolveDynamicModel` s’exécute de nouveau après son achèvement.

  </Step>

  <Step title="Ajouter des hooks d’exécution (si nécessaire)">
    La plupart des fournisseurs n’ont besoin que de `catalog` + `resolveDynamicModel`. Ajoutez des hooks
    progressivement selon les besoins de votre fournisseur.

    Les constructeurs d’assistants partagés couvrent désormais les familles de rejeu/compatibilité des outils
    les plus courantes, de sorte que les plugins n’ont généralement pas besoin de câbler chaque hook à la main :

    ```typescript
    import { buildProviderReplayFamilyHooks } from "openclaw/plugin-sdk/provider-model-shared";
    import { buildProviderStreamFamilyHooks } from "openclaw/plugin-sdk/provider-stream";
    import { buildProviderToolCompatFamilyHooks } from "openclaw/plugin-sdk/provider-tools";

    const GOOGLE_FAMILY_HOOKS = {
      ...buildProviderReplayFamilyHooks({ family: "google-gemini" }),
      ...buildProviderStreamFamilyHooks("google-thinking"),
      ...buildProviderToolCompatFamilyHooks("gemini"),
    };

    api.registerProvider({
      id: "acme-gemini-compatible",
      // ...
      ...GOOGLE_FAMILY_HOOKS,
    });
    ```

    Familles de rejeu disponibles aujourd’hui :

    | Famille | Ce qu’elle câble |
    | --- | --- |
    | `openai-compatible` | Politique de rejeu partagée de style OpenAI pour les transports compatibles OpenAI, y compris l’assainissement des identifiants d’appel d’outil, les corrections d’ordre assistant-en-premier et la validation générique des tours Gemini lorsque le transport en a besoin |
    | `anthropic-by-model` | Politique de rejeu sensible à Claude choisie par `modelId`, de sorte que les transports de messages Anthropic n’obtiennent le nettoyage des blocs de réflexion propres à Claude que lorsque le modèle résolu est réellement un identifiant Claude |
    | `google-gemini` | Politique de rejeu Gemini native plus assainissement du rejeu d’amorçage et mode de sortie du raisonnement balisé |
    | `passthrough-gemini` | Assainissement de la signature de pensée Gemini pour les modèles Gemini exécutés via des transports proxy compatibles OpenAI ; n’active pas la validation native du rejeu Gemini ni les réécritures d’amorçage |
    | `hybrid-anthropic-openai` | Politique hybride pour les fournisseurs qui mélangent dans un même plugin des surfaces de modèles de messages Anthropic et de compatibilité OpenAI ; la suppression facultative des blocs de réflexion réservés à Claude reste limitée au côté Anthropic |

    Exemples intégrés réels :

    - `google` et `google-gemini-cli` : `google-gemini`
    - `openrouter`, `kilocode`, `opencode` et `opencode-go` : `passthrough-gemini`
    - `amazon-bedrock` et `anthropic-vertex` : `anthropic-by-model`
    - `minimax` : `hybrid-anthropic-openai`
    - `moonshot`, `ollama`, `xai` et `zai` : `openai-compatible`

    Familles de flux disponibles aujourd’hui :

    | Famille | Ce qu’elle câble |
    | --- | --- |
    | `google-thinking` | Normalisation de la charge utile de réflexion Gemini sur le chemin de flux partagé |
    | `kilocode-thinking` | Wrapper de raisonnement Kilo sur le chemin de flux proxy partagé, avec `kilo/auto` et les identifiants de raisonnement proxy non pris en charge qui ignorent la réflexion injectée |
    | `moonshot-thinking` | Mappage de la charge utile native de réflexion binaire Moonshot à partir de la configuration + du niveau `/think` |
    | `minimax-fast-mode` | Réécriture du modèle en mode rapide MiniMax sur le chemin de flux partagé |
    | `openai-responses-defaults` | Wrappers natifs partagés OpenAI/Codex Responses : en-têtes d’attribution, `/fast`/`serviceTier`, verbosité du texte, recherche web Codex native, façonnage de charge utile de compatibilité de raisonnement et gestion du contexte Responses |
    | `openrouter-thinking` | Wrapper de raisonnement OpenRouter pour les routes proxy, avec les sauts pour modèles non pris en charge/`auto` gérés de manière centralisée |
    | `tool-stream-default-on` | Wrapper `tool_stream` activé par défaut pour les fournisseurs comme Z.AI qui veulent le streaming d’outils sauf s’il est explicitement désactivé |

    Exemples intégrés réels :

    - `google` et `google-gemini-cli` : `google-thinking`
    - `kilocode` : `kilocode-thinking`
    - `moonshot` : `moonshot-thinking`
    - `minimax` et `minimax-portal` : `minimax-fast-mode`
    - `openai` et `openai-codex` : `openai-responses-defaults`
    - `openrouter` : `openrouter-thinking`
    - `zai` : `tool-stream-default-on`

    `openclaw/plugin-sdk/provider-model-shared` exporte aussi l’énumération des familles de rejeu
    ainsi que les assistants partagés à partir desquels ces familles sont construites. Les
    exports publics courants comprennent :

    - `ProviderReplayFamily`
    - `buildProviderReplayFamilyHooks(...)`
    - des constructeurs de rejeu partagés tels que `buildOpenAICompatibleReplayPolicy(...)`,
      `buildAnthropicReplayPolicyForModel(...)`,
      `buildGoogleGeminiReplayPolicy(...)` et
      `buildHybridAnthropicOrOpenAIReplayPolicy(...)`
    - des assistants de rejeu Gemini tels que `sanitizeGoogleGeminiReplayHistory(...)`
      et `resolveTaggedReasoningOutputMode()`
    - des assistants de point de terminaison/modèle tels que `resolveProviderEndpoint(...)`,
      `normalizeProviderId(...)`, `normalizeGooglePreviewModelId(...)` et
      `normalizeNativeXaiModelId(...)`

    `openclaw/plugin-sdk/provider-stream` expose à la fois le constructeur de famille et
    les assistants de wrapper publics réutilisés par ces familles. Les exports publics
    courants comprennent :

    - `ProviderStreamFamily`
    - `buildProviderStreamFamilyHooks(...)`
    - `composeProviderStreamWrappers(...)`
    - des wrappers OpenAI/Codex partagés tels que
      `createOpenAIAttributionHeadersWrapper(...)`,
      `createOpenAIFastModeWrapper(...)`,
      `createOpenAIServiceTierWrapper(...)`,
      `createOpenAIResponsesContextManagementWrapper(...)` et
      `createCodexNativeWebSearchWrapper(...)`
    - des wrappers proxy/fournisseur partagés tels que `createOpenRouterWrapper(...)`,
      `createToolStreamWrapper(...)` et `createMinimaxFastModeWrapper(...)`

    Certains assistants de flux restent volontairement locaux au fournisseur. Exemple intégré
    actuel : `@openclaw/anthropic-provider` exporte
    `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
    `resolveAnthropicFastMode`, `resolveAnthropicServiceTier` et les
    constructeurs de wrappers Anthropic de plus bas niveau depuis sa surface publique `api.ts` /
    `contract-api.ts`. Ces assistants restent spécifiques à Anthropic, car
    ils encodent aussi la gestion des bêtas Claude OAuth et le contrôle `context1m`.

    D’autres fournisseurs intégrés gardent aussi des wrappers spécifiques au transport en local lorsque
    le comportement n’est pas proprement partageable entre familles. Exemple actuel : le
    plugin xAI intégré conserve le façonnage natif xAI Responses dans son propre
    `wrapStreamFn`, y compris les réécritures d’alias `/fast`, le `tool_stream` par défaut,
    le nettoyage strict des outils non pris en charge et la suppression
    de la charge utile de raisonnement spécifique à xAI.

    `openclaw/plugin-sdk/provider-tools` expose actuellement une famille partagée
    de schémas d’outil ainsi que des assistants partagés de schéma/compatibilité :

    - `ProviderToolCompatFamily` documente aujourd’hui l’inventaire partagé des familles.
    - `buildProviderToolCompatFamilyHooks("gemini")` câble le nettoyage des schémas Gemini
      + les diagnostics pour les fournisseurs qui ont besoin de schémas d’outil sûrs pour Gemini.
    - `normalizeGeminiToolSchemas(...)` et `inspectGeminiToolSchemas(...)`
      sont les assistants publics sous-jacents pour les schémas Gemini.
    - `resolveXaiModelCompatPatch()` renvoie le correctif de compatibilité xAI intégré :
      `toolSchemaProfile: "xai"`, mots-clés de schéma non pris en charge, prise en charge native de
      `web_search` et décodage des arguments d’appel d’outil avec entités HTML.
    - `applyXaiModelCompat(model)` applique ce même correctif de compatibilité xAI à un
      modèle résolu avant qu’il n’atteigne le runner.

    Exemple intégré réel : le plugin xAI utilise `normalizeResolvedModel` plus
    `contributeResolvedModelCompat` pour que ces métadonnées de compatibilité restent
    gérées par le fournisseur au lieu de coder en dur les règles xAI dans le cœur.

    Le même modèle de racine de package soutient aussi d’autres fournisseurs intégrés :

    - `@openclaw/openai-provider` : `api.ts` exporte des constructeurs de fournisseur,
      des assistants de modèle par défaut et des constructeurs de fournisseur temps réel
    - `@openclaw/openrouter-provider` : `api.ts` exporte le constructeur de fournisseur
      ainsi que des assistants d’intégration/configuration

    <Tabs>
      <Tab title="Échange de jetons">
        Pour les fournisseurs qui nécessitent un échange de jeton avant chaque appel d’inférence :

        ```typescript
        prepareRuntimeAuth: async (ctx) => {
          const exchanged = await exchangeToken(ctx.apiKey);
          return {
            apiKey: exchanged.token,
            baseUrl: exchanged.baseUrl,
            expiresAt: exchanged.expiresAt,
          };
        },
        ```
      </Tab>
      <Tab title="En-têtes personnalisés">
        Pour les fournisseurs qui nécessitent des en-têtes de requête personnalisés ou des modifications du corps :

        ```typescript
        // wrapStreamFn renvoie un StreamFn dérivé de ctx.streamFn
        wrapStreamFn: (ctx) => {
          if (!ctx.streamFn) return undefined;
          const inner = ctx.streamFn;
          return async (params) => {
            params.headers = {
              ...params.headers,
              "X-Acme-Version": "2",
            };
            return inner(params);
          };
        },
        ```
      </Tab>
      <Tab title="Identité de transport native">
        Pour les fournisseurs qui nécessitent des en-têtes ou métadonnées natives de requête/session sur
        des transports HTTP ou WebSocket génériques :

        ```typescript
        resolveTransportTurnState: (ctx) => ({
          headers: {
            "x-request-id": ctx.turnId,
          },
          metadata: {
            session_id: ctx.sessionId ?? "",
            turn_id: ctx.turnId,
          },
        }),
        resolveWebSocketSessionPolicy: (ctx) => ({
          headers: {
            "x-session-id": ctx.sessionId ?? "",
          },
          degradeCooldownMs: 60_000,
        }),
        ```
      </Tab>
      <Tab title="Utilisation et facturation">
        Pour les fournisseurs qui exposent des données d’utilisation/facturation :

        ```typescript
        resolveUsageAuth: async (ctx) => {
          const auth = await ctx.resolveOAuthToken();
          return auth ? { token: auth.token } : null;
        },
        fetchUsageSnapshot: async (ctx) => {
          return await fetchAcmeUsage(ctx.token, ctx.timeoutMs);
        },
        ```
      </Tab>
    </Tabs>

    <Accordion title="Tous les hooks de fournisseur disponibles">
      OpenClaw appelle les hooks dans cet ordre. La plupart des fournisseurs n’en utilisent que 2 ou 3 :

      | # | Hook | Quand l’utiliser |
      | --- | --- | --- |
      | 1 | `catalog` | Catalogue de modèles ou valeurs par défaut d’URL de base |
      | 2 | `applyConfigDefaults` | Valeurs par défaut globales gérées par le fournisseur pendant la matérialisation de la configuration |
      | 3 | `normalizeModelId` | Nettoyage des alias d’identifiant de modèle hérités/de préversion avant la recherche |
      | 4 | `normalizeTransport` | Nettoyage de la famille de fournisseur `api` / `baseUrl` avant l’assemblage générique du modèle |
      | 5 | `normalizeConfig` | Normaliser la configuration `models.providers.<id>` |
      | 6 | `applyNativeStreamingUsageCompat` | Réécritures de compatibilité d’utilisation en streaming natif pour les fournisseurs de configuration |
      | 7 | `resolveConfigApiKey` | Résolution d’authentification par marqueur d’environnement gérée par le fournisseur |
      | 8 | `resolveSyntheticAuth` | Authentification synthétique locale/autohébergée ou adossée à la configuration |
      | 9 | `shouldDeferSyntheticProfileAuth` | Placer les espaces réservés de profil stockés synthétiques derrière l’authentification d’environnement/de configuration |
      | 10 | `resolveDynamicModel` | Accepter des identifiants de modèle amont arbitraires |
      | 11 | `prepareDynamicModel` | Récupération asynchrone de métadonnées avant la résolution |
      | 12 | `normalizeResolvedModel` | Réécritures de transport avant le runner |

    Remarques sur le repli à l’exécution :

    - `normalizeConfig` vérifie d’abord le fournisseur correspondant, puis les autres
      plugins de fournisseur compatibles avec les hooks jusqu’à ce que l’un d’eux modifie réellement la configuration.
      Si aucun hook de fournisseur ne réécrit une entrée de configuration prise en charge de la famille Google, le
      normaliseur de configuration Google intégré s’applique encore.
    - `resolveConfigApiKey` utilise le hook du fournisseur lorsqu’il est exposé. Le chemin intégré
      `amazon-bedrock` dispose aussi ici d’un résolveur intégré de marqueur d’environnement AWS,
      même si l’authentification d’exécution Bedrock elle-même utilise toujours la chaîne
      par défaut du SDK AWS.
      | 13 | `contributeResolvedModelCompat` | Drapeaux de compatibilité pour les modèles fournisseur derrière un autre transport compatible |
      | 14 | `capabilities` | Ancien ensemble statique de capacités ; compatibilité uniquement |
      | 15 | `normalizeToolSchemas` | Nettoyage des schémas d’outil géré par le fournisseur avant l’enregistrement |
      | 16 | `inspectToolSchemas` | Diagnostics de schémas d’outil gérés par le fournisseur |
      | 17 | `resolveReasoningOutputMode` | Contrat de sortie de raisonnement balisé ou natif |
      | 18 | `prepareExtraParams` | Paramètres de requête par défaut |
      | 19 | `createStreamFn` | Transport StreamFn entièrement personnalisé |
      | 20 | `wrapStreamFn` | Wrappers personnalisés d’en-têtes/corps sur le chemin de flux normal |
      | 21 | `resolveTransportTurnState` | En-têtes/métadonnées natives par tour |
      | 22 | `resolveWebSocketSessionPolicy` | En-têtes de session WS natives/refroidissement |
      | 23 | `formatApiKey` | Forme personnalisée du jeton d’exécution |
      | 24 | `refreshOAuth` | Actualisation OAuth personnalisée |
      | 25 | `buildAuthDoctorHint` | Indications de réparation d’authentification |
      | 26 | `matchesContextOverflowError` | Détection de dépassement gérée par le fournisseur |
      | 27 | `classifyFailoverReason` | Classification de limitation de débit/surcharge gérée par le fournisseur |
      | 28 | `isCacheTtlEligible` | Contrôle TTL du cache d’invite |
      | 29 | `buildMissingAuthMessage` | Indication personnalisée d’authentification manquante |
      | 30 | `suppressBuiltInModel` | Masquer les lignes amont obsolètes |
      | 31 | `augmentModelCatalog` | Lignes synthétiques de compatibilité anticipée |
      | 32 | `isBinaryThinking` | Réflexion binaire activée/désactivée |
      | 33 | `supportsXHighThinking` | Prise en charge du raisonnement `xhigh` |
      | 34 | `resolveDefaultThinkingLevel` | Politique `/think` par défaut |
      | 35 | `isModernModelRef` | Correspondance des modèles en direct/en test de fumée |
      | 36 | `prepareRuntimeAuth` | Échange de jeton avant l’inférence |
      | 37 | `resolveUsageAuth` | Analyse personnalisée des identifiants d’utilisation |
      | 38 | `fetchUsageSnapshot` | Point de terminaison d’utilisation personnalisé |
      | 39 | `createEmbeddingProvider` | Adaptateur d’embedding géré par le fournisseur pour la mémoire/la recherche |
      | 40 | `buildReplayPolicy` | Politique personnalisée de rejeu/compaction de transcription |
      | 41 | `sanitizeReplayHistory` | Réécritures de rejeu spécifiques au fournisseur après le nettoyage générique |
      | 42 | `validateReplayTurns` | Validation stricte des tours de rejeu avant le runner intégré |
      | 43 | `onModelSelected` | Callback après sélection (par exemple télémétrie) |

      Remarque sur l’ajustement des prompts :

      - `resolveSystemPromptContribution` permet à un fournisseur d’injecter des
        indications d’invite système tenant compte du cache pour une famille de modèles. Préférez-le à
        `before_prompt_build` lorsque le comportement appartient à un fournisseur/une famille de modèles
        et doit préserver la séparation stable/dynamique du cache.

      Pour des descriptions détaillées et des exemples réels, voir
      [Internals: Provider Runtime Hooks](/fr/plugins/architecture#provider-runtime-hooks).
    </Accordion>

  </Step>

  <Step title="Ajouter des capacités supplémentaires (facultatif)">
    <a id="step-5-add-extra-capabilities"></a>
    Un plugin de fournisseur peut enregistrer la parole, la transcription temps réel, la voix en temps réel,
    la compréhension multimédia, la génération d’images, la génération vidéo, la récupération web
    et la recherche web en plus de l’inférence de texte :

    ```typescript
    register(api) {
      api.registerProvider({ id: "acme-ai", /* ... */ });

      api.registerSpeechProvider({
        id: "acme-ai",
        label: "Acme Speech",
        isConfigured: ({ config }) => Boolean(config.messages?.tts),
        synthesize: async (req) => ({
          audioBuffer: Buffer.from(/* données PCM */),
          outputFormat: "mp3",
          fileExtension: ".mp3",
          voiceCompatible: false,
        }),
      });

      api.registerRealtimeTranscriptionProvider({
        id: "acme-ai",
        label: "Acme Realtime Transcription",
        isConfigured: () => true,
        createSession: (req) => ({
          connect: async () => {},
          sendAudio: () => {},
          close: () => {},
          isConnected: () => true,
        }),
      });

      api.registerRealtimeVoiceProvider({
        id: "acme-ai",
        label: "Acme Realtime Voice",
        isConfigured: ({ providerConfig }) => Boolean(providerConfig.apiKey),
        createBridge: (req) => ({
          connect: async () => {},
          sendAudio: () => {},
          setMediaTimestamp: () => {},
          submitToolResult: () => {},
          acknowledgeMark: () => {},
          close: () => {},
          isConnected: () => true,
        }),
      });

      api.registerMediaUnderstandingProvider({
        id: "acme-ai",
        capabilities: ["image", "audio"],
        describeImage: async (req) => ({ text: "Une photo de..." }),
        transcribeAudio: async (req) => ({ text: "Transcription..." }),
      });

      api.registerImageGenerationProvider({
        id: "acme-ai",
        label: "Acme Images",
        generate: async (req) => ({ /* résultat image */ }),
      });

      api.registerVideoGenerationProvider({
        id: "acme-ai",
        label: "Acme Video",
        capabilities: {
          generate: {
            maxVideos: 1,
            maxDurationSeconds: 10,
            supportsResolution: true,
          },
          imageToVideo: {
            enabled: true,
            maxVideos: 1,
            maxInputImages: 1,
            maxDurationSeconds: 5,
          },
          videoToVideo: {
            enabled: false,
          },
        },
        generateVideo: async (req) => ({ videos: [] }),
      });

      api.registerWebFetchProvider({
        id: "acme-ai-fetch",
        label: "Acme Fetch",
        hint: "Récupérer des pages via le backend de rendu d’Acme.",
        envVars: ["ACME_FETCH_API_KEY"],
        placeholder: "acme-...",
        signupUrl: "https://acme.example.com/fetch",
        credentialPath: "plugins.entries.acme.config.webFetch.apiKey",
        getCredentialValue: (fetchConfig) => fetchConfig?.acme?.apiKey,
        setCredentialValue: (fetchConfigTarget, value) => {
          const acme = (fetchConfigTarget.acme ??= {});
          acme.apiKey = value;
        },
        createTool: () => ({
          description: "Récupérer une page via Acme Fetch.",
          parameters: {},
          execute: async (args) => ({ content: [] }),
        }),
      });

      api.registerWebSearchProvider({
        id: "acme-ai-search",
        label: "Acme Search",
        search: async (req) => ({ content: [] }),
      });
    }
    ```

    OpenClaw classe cela comme un plugin à **capacités hybrides**. C’est le
    modèle recommandé pour les plugins d’entreprise (un plugin par fournisseur). Voir
    [Internals: Capability Ownership](/fr/plugins/architecture#capability-ownership-model).

    Pour la génération vidéo, privilégiez la forme de capacités sensible au mode montrée ci-dessus :
    `generate`, `imageToVideo` et `videoToVideo`. Les champs agrégés plats tels
    que `maxInputImages`, `maxInputVideos` et `maxDurationSeconds` ne
    suffisent pas à annoncer proprement la prise en charge des modes de transformation ou les modes désactivés.

    Les fournisseurs de génération musicale doivent suivre le même modèle :
    `generate` pour la génération à partir de prompt seul et `edit` pour la génération
    basée sur une image de référence. Les champs agrégés plats tels que `maxInputImages`,
    `supportsLyrics` et `supportsFormat` ne suffisent pas à annoncer la prise en charge de la modification ;
    des blocs explicites `generate` / `edit` sont le contrat attendu.

  </Step>

  <Step title="Tester">
    <a id="step-6-test"></a>
    ```typescript src/provider.test.ts
    import { describe, it, expect } from "vitest";
    // Exportez votre objet de configuration de fournisseur depuis index.ts ou un fichier dédié
    import { acmeProvider } from "./provider.js";

    describe("fournisseur acme-ai", () => {
      it("résout les modèles dynamiques", () => {
        const model = acmeProvider.resolveDynamicModel!({
          modelId: "acme-beta-v3",
        } as any);
        expect(model.id).toBe("acme-beta-v3");
        expect(model.provider).toBe("acme-ai");
      });

      it("renvoie le catalogue lorsqu’une clé est disponible", async () => {
        const result = await acmeProvider.catalog!.run({
          resolveProviderApiKey: () => ({ apiKey: "test-key" }),
        } as any);
        expect(result?.provider?.models).toHaveLength(2);
      });

      it("renvoie un catalogue nul lorsqu’il n’y a pas de clé", async () => {
        const result = await acmeProvider.catalog!.run({
          resolveProviderApiKey: () => ({ apiKey: undefined }),
        } as any);
        expect(result).toBeNull();
      });
    });
    ```

  </Step>
</Steps>

## Publier sur ClawHub

Les plugins de fournisseur se publient comme n’importe quel autre plugin de code externe :

```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
```

N’utilisez pas ici l’ancien alias de publication réservé aux Skills ; les packages de plugin doivent utiliser
`clawhub package publish`.

## Structure des fichiers

```
<bundled-plugin-root>/acme-ai/
├── package.json              # métadonnées openclaw.providers
├── openclaw.plugin.json      # Manifeste avec les métadonnées d’authentification du fournisseur
├── index.ts                  # definePluginEntry + registerProvider
└── src/
    ├── provider.test.ts      # Tests
    └── usage.ts              # Point de terminaison d’utilisation (facultatif)
```

## Référence de l’ordre des catalogues

`catalog.order` contrôle le moment où votre catalogue est fusionné par rapport aux
fournisseurs intégrés :

| Ordre     | Moment          | Cas d’usage                                      |
| --------- | --------------- | ----------------------------------------------- |
| `simple`  | Première passe  | Fournisseurs simples à clé API                  |
| `profile` | Après simple    | Fournisseurs conditionnés par des profils d’authentification |
| `paired`  | Après profile   | Synthétiser plusieurs entrées liées             |
| `late`    | Dernière passe  | Remplacer des fournisseurs existants (gagne en cas de collision) |

## Étapes suivantes

- [Plugins de canal](/fr/plugins/sdk-channel-plugins) — si votre plugin fournit aussi un canal
- [SDK Runtime](/fr/plugins/sdk-runtime) — assistants `api.runtime` (TTS, recherche, sous-agent)
- [Vue d’ensemble du SDK](/fr/plugins/sdk-overview) — référence complète des importations de sous-chemins
- [Internes des plugins](/fr/plugins/architecture#provider-runtime-hooks) — détails des hooks et exemples intégrés
