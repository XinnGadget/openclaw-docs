---
read_when:
    - 新しいモデルプロバイダープラグインを構築している場合
    - OpenAI互換プロキシまたはカスタムLLMをOpenClawに追加したい場合
    - プロバイダー認証、カタログ、runtime hooksを理解する必要がある場合
sidebarTitle: Provider Plugins
summary: OpenClaw向けモデルプロバイダープラグインを構築するためのステップごとのガイド
title: プロバイダープラグインの構築
x-i18n:
    generated_at: "2026-04-07T04:46:06Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4da82a353e1bf4fe6dc09e14b8614133ac96565679627de51415926014bd3990
    source_path: plugins/sdk-provider-plugins.md
    workflow: 15
---

# プロバイダープラグインの構築

このガイドでは、OpenClawにモデルプロバイダー
（LLM）を追加するプロバイダープラグインの構築手順を説明します。最後には、モデルカタログ、
APIキー認証、動的モデル解決を備えたプロバイダーが完成します。

<Info>
  まだOpenClawプラグインを一度も構築したことがない場合は、まず
  基本的なパッケージ構造とマニフェスト設定について[はじめに](/ja-JP/plugins/building-plugins)を読んでください。
</Info>

## ウォークスルー

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="パッケージとマニフェスト">
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
      "description": "Acme AI model provider",
      "providers": ["acme-ai"],
      "modelSupport": {
        "modelPrefixes": ["acme-"]
      },
      "providerAuthEnvVars": {
        "acme-ai": ["ACME_AI_API_KEY"]
      },
      "providerAuthChoices": [
        {
          "provider": "acme-ai",
          "method": "api-key",
          "choiceId": "acme-ai-api-key",
          "choiceLabel": "Acme AI API key",
          "groupId": "acme-ai",
          "groupLabel": "Acme AI",
          "cliFlag": "--acme-ai-api-key",
          "cliOption": "--acme-ai-api-key <key>",
          "cliDescription": "Acme AI API key"
        }
      ],
      "configSchema": {
        "type": "object",
        "additionalProperties": false
      }
    }
    ```
    </CodeGroup>

    このマニフェストは`providerAuthEnvVars`を宣言し、OpenClawが
    プラグインruntimeを読み込まずに認証情報を検出できるようにします。`modelSupport`は任意で、
    `acme-large`のような短縮モデルidから、runtime hooksが存在する前に
    OpenClawがプロバイダープラグインを自動読み込みできるようにします。もしその
    プロバイダーをClawHubで公開するなら、`package.json`内のそれらの`openclaw.compat`と`openclaw.build`フィールドは
    必須です。

  </Step>

  <Step title="プロバイダーを登録する">
    最小限のプロバイダーには`id`、`label`、`auth`、`catalog`が必要です:

    ```typescript index.ts
    import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
    import { createProviderApiKeyAuthMethod } from "openclaw/plugin-sdk/provider-auth";

    export default definePluginEntry({
      id: "acme-ai",
      name: "Acme AI",
      description: "Acme AI model provider",
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
              label: "Acme AI API key",
              hint: "API key from your Acme AI dashboard",
              optionKey: "acmeAiApiKey",
              flagName: "--acme-ai-api-key",
              envVar: "ACME_AI_API_KEY",
              promptMessage: "Enter your Acme AI API key",
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

    これで動作するプロバイダーになります。ユーザーは
    `openclaw onboard --acme-ai-api-key <key>`を実行して、
    モデルとして`acme-ai/acme-large`を選択できるようになります。

    APIキー認証と単一のcatalog-backed runtimeを持つ
    1つのテキストプロバイダーだけを登録するバンドル済みプロバイダーでは、より狭い
    `defineSingleProviderPluginEntry(...)`ヘルパーを優先してください:

    ```typescript
    import { defineSingleProviderPluginEntry } from "openclaw/plugin-sdk/provider-entry";

    export default defineSingleProviderPluginEntry({
      id: "acme-ai",
      name: "Acme AI",
      description: "Acme AI model provider",
      provider: {
        label: "Acme AI",
        docsPath: "/providers/acme-ai",
        auth: [
          {
            methodId: "api-key",
            label: "Acme AI API key",
            hint: "API key from your Acme AI dashboard",
            optionKey: "acmeAiApiKey",
            flagName: "--acme-ai-api-key",
            envVar: "ACME_AI_API_KEY",
            promptMessage: "Enter your Acme AI API key",
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

    認証フローでオンボーディング中に`models.providers.*`、aliases、および
    エージェントのデフォルトモデルもパッチする必要がある場合は、
    `openclaw/plugin-sdk/provider-onboard`のpreset helpersを使用してください。最も狭いヘルパーは
    `createDefaultModelPresetAppliers(...)`、
    `createDefaultModelsPresetAppliers(...)`、および
    `createModelCatalogPresetAppliers(...)`です。

    プロバイダーのネイティブendpointが通常の
    `openai-completions` transport上でstreamed usage blocksをサポートする場合は、プロバイダーidチェックを
    ハードコードする代わりに、`openclaw/plugin-sdk/provider-catalog-shared`内の共有catalog helpersを優先してください。
    `supportsNativeStreamingUsageCompat(...)`と
    `applyProviderNativeStreamingUsageCompat(...)`は
    endpoint capability mapからサポートを検出するため、ネイティブのMoonshot/DashScope系endpointsも、
    プラグインがカスタムprovider idを使用していてもオプトインできます。

  </Step>

  <Step title="動的モデル解決を追加する">
    プロバイダーが任意のモデルID（プロキシやルーターのような）を受け入れる場合は、
    `resolveDynamicModel`を追加してください:

    ```typescript
    api.registerProvider({
      // ... id, label, auth, catalog from above

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

    解決にネットワーク呼び出しが必要な場合は、非同期の
    ウォームアップに`prepareDynamicModel`を使ってください。完了後に`resolveDynamicModel`が再度実行されます。

  </Step>

  <Step title="runtime hooksを追加する（必要に応じて）">
    ほとんどのプロバイダーでは`catalog` + `resolveDynamicModel`だけで十分です。必要に応じて
    hooksを段階的に追加してください。

    共有ヘルパービルダーは、現在では最も一般的なreplay/tool-compat
    ファミリーをカバーしているため、プラグインは通常、各hookを1つずつ手作業で配線する必要はありません:

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

    現在利用可能なreplayファミリー:

    | Family | 配線されるもの |
    | --- | --- |
    | `openai-compatible` | OpenAI互換transport向けの共有OpenAIスタイルreplay policy。tool-call-idのサニタイズ、assistant-first順序修正、およびtransportで必要な場合の汎用Geminiターン検証を含みます |
    | `anthropic-by-model` | `modelId`によって選ばれるClaude対応replay policy。Anthropic-message transportsでは、解決されたモデルが実際にClaude idである場合にのみ、Claude固有のthinking-block cleanupが適用されます |
    | `google-gemini` | ネイティブGemini replay policyに加え、bootstrap replay sanitationおよびtagged reasoning-output mode |
    | `passthrough-gemini` | OpenAI互換プロキシtransport経由で動作するGeminiモデル向けのGemini thought-signature sanitation。ネイティブGemini replay validationやbootstrap rewritesは有効にしません |
    | `hybrid-anthropic-openai` | 1つのプラグイン内でAnthropic-messageとOpenAI互換のモデル表面が混在するプロバイダー向けのハイブリッドpolicy。任意のClaude専用thinking-block削除はAnthropic側に限定されます |

    実際のバンドル済みの例:

    - `google`と`google-gemini-cli`: `google-gemini`
    - `openrouter`、`kilocode`、`opencode`、`opencode-go`: `passthrough-gemini`
    - `amazon-bedrock`と`anthropic-vertex`: `anthropic-by-model`
    - `minimax`: `hybrid-anthropic-openai`
    - `moonshot`、`ollama`、`xai`、`zai`: `openai-compatible`

    現在利用可能なstreamファミリー:

    | Family | 配線されるもの |
    | --- | --- |
    | `google-thinking` | 共有stream path上のGemini thinking payload正規化 |
    | `kilocode-thinking` | 共有proxy stream path上のKilo reasoning wrapper。`kilo/auto`および未対応のproxy reasoning idsではthinking挿入をスキップします |
    | `moonshot-thinking` | config + `/think` levelからのMoonshotバイナリnative-thinking payloadマッピング |
    | `minimax-fast-mode` | 共有stream path上のMiniMax fast-modeモデル書き換え |
    | `openai-responses-defaults` | 共有ネイティブOpenAI/Codex Responses wrappers: attribution headers、`/fast`/`serviceTier`、text verbosity、ネイティブCodex web search、reasoning-compat payload shaping、Responses context management |
    | `openrouter-thinking` | proxy routes向けのOpenRouter reasoning wrapper。未対応モデル/`auto`のスキップを中央管理します |
    | `tool-stream-default-on` | Z.AIのように、明示的に無効化されない限りtool streamingを望むプロバイダー向けのデフォルト有効`tool_stream` wrapper |

    実際のバンドル済みの例:

    - `google`と`google-gemini-cli`: `google-thinking`
    - `kilocode`: `kilocode-thinking`
    - `moonshot`: `moonshot-thinking`
    - `minimax`と`minimax-portal`: `minimax-fast-mode`
    - `openai`と`openai-codex`: `openai-responses-defaults`
    - `openrouter`: `openrouter-thinking`
    - `zai`: `tool-stream-default-on`

    `openclaw/plugin-sdk/provider-model-shared`は、replay-family
    enumと、それらのファミリーを構成する共有ヘルパーもエクスポートします。一般的な公開
    exportsには次のものがあります:

    - `ProviderReplayFamily`
    - `buildProviderReplayFamilyHooks(...)`
    - `buildOpenAICompatibleReplayPolicy(...)`、
      `buildAnthropicReplayPolicyForModel(...)`、
      `buildGoogleGeminiReplayPolicy(...)`、および
      `buildHybridAnthropicOrOpenAIReplayPolicy(...)`
      などの共有replay builders
    - `sanitizeGoogleGeminiReplayHistory(...)`
      および`resolveTaggedReasoningOutputMode()`
      などのGemini replay helpers
    - `resolveProviderEndpoint(...)`、
      `normalizeProviderId(...)`、`normalizeGooglePreviewModelId(...)`、および
      `normalizeNativeXaiModelId(...)`
      などのendpoint/model helpers

    `openclaw/plugin-sdk/provider-stream`は、family builderと、
    それらのファミリーが再利用する公開wrapper helpersの両方を公開します。一般的な公開exports
    には次のものがあります:

    - `ProviderStreamFamily`
    - `buildProviderStreamFamilyHooks(...)`
    - `composeProviderStreamWrappers(...)`
    - `createOpenAIAttributionHeadersWrapper(...)`、
      `createOpenAIFastModeWrapper(...)`、
      `createOpenAIServiceTierWrapper(...)`、
      `createOpenAIResponsesContextManagementWrapper(...)`、および
      `createCodexNativeWebSearchWrapper(...)`
      などの共有OpenAI/Codex wrappers
    - `createOpenRouterWrapper(...)`、
      `createToolStreamWrapper(...)`、および`createMinimaxFastModeWrapper(...)`
      などの共有proxy/provider wrappers

    一部のstream helpersは、意図的にprovider-localのままです。現在のバンドル済み
    例: `@openclaw/anthropic-provider`は
    公開`api.ts` / `contract-api.ts` seamから
    `wrapAnthropicProviderStream`、`resolveAnthropicBetas`、
    `resolveAnthropicFastMode`、`resolveAnthropicServiceTier`、および
    より低レベルのAnthropic wrapper buildersをエクスポートします。これらのhelpersが
    Anthropic固有のままなのは、Claude OAuth beta処理と
    `context1m` gatingも含んでいるためです。

    他のバンドル済みプロバイダーも、その動作がファミリー間できれいに共有されない場合は、
    transport固有のwrappersをローカルに保持しています。現在の例: バンドル済み
    xAIプラグインは、ネイティブxAI Responses shapingを独自の
    `wrapStreamFn`に保持しており、`/fast` alias rewrites、デフォルト`tool_stream`、
    未対応strict-tool cleanup、およびxAI固有のreasoning-payload
    削除を含みます。

    `openclaw/plugin-sdk/provider-tools`は現在、1つの共有
    tool-schemaファミリーと共有schema/compat helpersを公開しています:

    - `ProviderToolCompatFamily`は、現在の共有ファミリー一覧を文書化します。
    - `buildProviderToolCompatFamilyHooks("gemini")`は、Gemini安全なtool schemasを必要とするプロバイダー向けに
      Gemini schema cleanup + diagnosticsを配線します。
    - `normalizeGeminiToolSchemas(...)`と`inspectGeminiToolSchemas(...)`
      は、その基盤となる公開Gemini schema helpersです。
    - `resolveXaiModelCompatPatch()`は、バンドル済みxAI compat patchを返します:
      `toolSchemaProfile: "xai"`、未対応schema keywords、ネイティブ
      `web_search`サポート、およびHTML entityのtool-call argumentデコードです。
    - `applyXaiModelCompat(model)`は、その同じxAI compat patchを、
      実行前の解決済みモデルに適用します。

    実際のバンドル済みの例: xAIプラグインは、`normalizeResolvedModel`と
    `contributeResolvedModelCompat`を使って、そのcompat metadataを
    コアにxAIルールをハードコードするのではなく、プロバイダー側で管理しています。

    同じpackage-rootパターンは、他のバンドル済みプロバイダーも支えています:

    - `@openclaw/openai-provider`: `api.ts`はプロバイダービルダー、
      default-model helpers、およびrealtime provider buildersをエクスポートします
    - `@openclaw/openrouter-provider`: `api.ts`はprovider builder
      に加えてonboarding/config helpersもエクスポートします

    <Tabs>
      <Tab title="トークン交換">
        各推論呼び出し前にトークン交換が必要なプロバイダーの場合:

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
      <Tab title="カスタムヘッダー">
        カスタムのリクエストヘッダーまたはボディ変更が必要なプロバイダーの場合:

        ```typescript
        // wrapStreamFn returns a StreamFn derived from ctx.streamFn
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
      <Tab title="ネイティブtransport identity">
        汎用HTTPまたはWebSocket transport上でネイティブのrequest/session headersやmetadataが必要なプロバイダーの場合:

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
      <Tab title="使用量と課金">
        使用量/課金データを公開するプロバイダーの場合:

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

    <Accordion title="利用可能なすべてのprovider hooks">
      OpenClawはこの順序でhooksを呼び出します。ほとんどのプロバイダーは2〜3個しか使いません:

      | # | Hook | 使用する場面 |
      | --- | --- | --- |
      | 1 | `catalog` | モデルカタログまたはbase URLデフォルト |
      | 2 | `applyConfigDefaults` | config materialization中のprovider所有のグローバルデフォルト |
      | 3 | `normalizeModelId` | lookup前のレガシー/preview model-id alias cleanup |
      | 4 | `normalizeTransport` | 汎用モデル組み立て前のprovider-family `api` / `baseUrl` cleanup |
      | 5 | `normalizeConfig` | `models.providers.<id>` configを正規化 |
      | 6 | `applyNativeStreamingUsageCompat` | config providers向けネイティブstreaming-usage compat rewrites |
      | 7 | `resolveConfigApiKey` | provider所有のenv-marker auth resolution |
      | 8 | `resolveSyntheticAuth` | ローカル/セルフホストまたはconfig-backed synthetic auth |
      | 9 | `shouldDeferSyntheticProfileAuth` | syntheticなstored-profile placeholdersをenv/config authの後ろへ下げる |
      | 10 | `resolveDynamicModel` | 任意のupstream model IDsを受け入れる |
      | 11 | `prepareDynamicModel` | 解決前の非同期metadata取得 |
      | 12 | `normalizeResolvedModel` | runner前のtransport rewrites |

      runtimeフォールバックに関する注意:

      - `normalizeConfig`は最初に一致したproviderを確認し、その後、
      実際にconfigを変更するまで他のhook対応provider pluginsを確認します。
      どのprovider hookもサポート対象のGoogle系config entryを書き換えない場合は、
      バンドル済みGoogle config normalizerが引き続き適用されます。
    - `resolveConfigApiKey`は、公開されていればprovider hookを使用します。バンドル済みの
      `amazon-bedrock`パスには、ここに組み込みのAWS env-marker resolverもあります。
      Bedrock runtime auth自体は依然としてAWS SDKのdefault
      chainを使用しますが、それでも適用されます。
      | 13 | `contributeResolvedModelCompat` | 別の互換transportの背後にあるvendor models向けcompat flags |
      | 14 | `capabilities` | レガシーな静的capability bag。互換性用のみ |
      | 15 | `normalizeToolSchemas` | 登録前のprovider所有tool-schema cleanup |
      | 16 | `inspectToolSchemas` | provider所有tool-schema diagnostics |
      | 17 | `resolveReasoningOutputMode` | taggedとnativeのreasoning-output contract |
      | 18 | `prepareExtraParams` | デフォルトrequest params |
      | 19 | `createStreamFn` | 完全カスタムのStreamFn transport |
      | 20 | `wrapStreamFn` | 通常stream path上のカスタムheaders/body wrappers |
      | 21 | `resolveTransportTurnState` | ネイティブのターン単位headers/metadata |
      | 22 | `resolveWebSocketSessionPolicy` | ネイティブWS session headers/cool-down |
      | 23 | `formatApiKey` | カスタムruntime token shape |
      | 24 | `refreshOAuth` | カスタムOAuth refresh |
      | 25 | `buildAuthDoctorHint` | auth修復ガイダンス |
      | 26 | `matchesContextOverflowError` | provider所有のoverflow検出 |
      | 27 | `classifyFailoverReason` | provider所有のrate-limit/overload分類 |
      | 28 | `isCacheTtlEligible` | prompt cache TTL gating |
      | 29 | `buildMissingAuthMessage` | カスタムmissing-authヒント |
      | 30 | `suppressBuiltInModel` | 古くなったupstream rowsを非表示にする |
      | 31 | `augmentModelCatalog` | syntheticなforward-compat rows |
      | 32 | `isBinaryThinking` | バイナリthinking on/off |
      | 33 | `supportsXHighThinking` | `xhigh` reasoningサポート |
      | 34 | `resolveDefaultThinkingLevel` | デフォルト`/think` policy |
      | 35 | `isModernModelRef` | live/smokeモデル一致 |
      | 36 | `prepareRuntimeAuth` | 推論前のトークン交換 |
      | 37 | `resolveUsageAuth` | カスタムusage credential parsing |
      | 38 | `fetchUsageSnapshot` | カスタムusage endpoint |
      | 39 | `createEmbeddingProvider` | memory/search向けprovider所有embedding adapter |
      | 40 | `buildReplayPolicy` | カスタムtranscript replay/compaction policy |
      | 41 | `sanitizeReplayHistory` | 汎用cleanup後のprovider固有replay rewrites |
      | 42 | `validateReplayTurns` | embedded runner前の厳格なreplay-turn validation |
      | 43 | `onModelSelected` | 選択後コールバック（例: telemetry） |

      プロンプト調整に関する注意:

      - `resolveSystemPromptContribution`により、providerはモデルファミリー向けに
        cache-awareなsystem-prompt guidanceを注入できます。挙動が
        1つのprovider/model familyに属し、stable/dynamicなcache分割を維持すべき場合は、
        `before_prompt_build`よりこれを優先してください。

      詳細な説明と実例については、
      [Internals: Provider Runtime Hooks](/ja-JP/plugins/architecture#provider-runtime-hooks)を参照してください。
    </Accordion>

  </Step>

  <Step title="追加機能を加える（任意）">
    <a id="step-5-add-extra-capabilities"></a>
    プロバイダープラグインは、テキスト推論に加えて、speech、realtime transcription、realtime
    voice、media understanding、image generation、video generation、web fetch、
    web searchを登録できます:

    ```typescript
    register(api) {
      api.registerProvider({ id: "acme-ai", /* ... */ });

      api.registerSpeechProvider({
        id: "acme-ai",
        label: "Acme Speech",
        isConfigured: ({ config }) => Boolean(config.messages?.tts),
        synthesize: async (req) => ({
          audioBuffer: Buffer.from(/* PCM data */),
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
        describeImage: async (req) => ({ text: "A photo of..." }),
        transcribeAudio: async (req) => ({ text: "Transcript..." }),
      });

      api.registerImageGenerationProvider({
        id: "acme-ai",
        label: "Acme Images",
        generate: async (req) => ({ /* image result */ }),
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
        hint: "Fetch pages through Acme's rendering backend.",
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
          description: "Fetch a page through Acme Fetch.",
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

    OpenClawはこれを**hybrid-capability**プラグインとして分類します。これは
    企業向けプラグイン（ベンダーごとに1プラグイン）に推奨されるパターンです。
    [Internals: Capability Ownership](/ja-JP/plugins/architecture#capability-ownership-model)を参照してください。

    video generationについては、上記のmode-aware capability形状を優先してください:
    `generate`、`imageToVideo`、`videoToVideo`です。`maxInputImages`、
    `maxInputVideos`、`maxDurationSeconds`のようなフラットな集約フィールドだけでは、
    transform-mode supportや無効なモードをきれいに表現するには不十分です。

    music-generationプロバイダーも同じパターンに従う必要があります:
    プロンプトのみの生成には`generate`、reference-imageベースの
    生成には`edit`です。`maxInputImages`、
    `supportsLyrics`、`supportsFormat`のようなフラットな集約フィールドだけでは
    edit supportを表現するには不十分で、明示的な`generate` / `edit`
    ブロックが想定されるcontractです。

  </Step>

  <Step title="テスト">
    <a id="step-6-test"></a>
    ```typescript src/provider.test.ts
    import { describe, it, expect } from "vitest";
    // Export your provider config object from index.ts or a dedicated file
    import { acmeProvider } from "./provider.js";

    describe("acme-ai provider", () => {
      it("resolves dynamic models", () => {
        const model = acmeProvider.resolveDynamicModel!({
          modelId: "acme-beta-v3",
        } as any);
        expect(model.id).toBe("acme-beta-v3");
        expect(model.provider).toBe("acme-ai");
      });

      it("returns catalog when key is available", async () => {
        const result = await acmeProvider.catalog!.run({
          resolveProviderApiKey: () => ({ apiKey: "test-key" }),
        } as any);
        expect(result?.provider?.models).toHaveLength(2);
      });

      it("returns null catalog when no key", async () => {
        const result = await acmeProvider.catalog!.run({
          resolveProviderApiKey: () => ({ apiKey: undefined }),
        } as any);
        expect(result).toBeNull();
      });
    });
    ```

  </Step>
</Steps>

## ClawHubへの公開

プロバイダープラグインは、他の外部コードプラグインと同じ方法で公開します:

```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
```

ここではレガシーなskill専用publish aliasは使わないでください。プラグインパッケージでは
`clawhub package publish`を使用する必要があります。

## ファイル構成

```
<bundled-plugin-root>/acme-ai/
├── package.json              # openclaw.providers metadata
├── openclaw.plugin.json      # providerAuthEnvVarsを含むManifest
├── index.ts                  # definePluginEntry + registerProvider
└── src/
    ├── provider.test.ts      # Tests
    └── usage.ts              # Usage endpoint（任意）
```

## カタログ順序リファレンス

`catalog.order`は、組み込み
プロバイダーに対してあなたのcatalogがいつマージされるかを制御します:

| Order     | タイミング          | 使用例                                        |
| --------- | ------------- | ----------------------------------------------- |
| `simple`  | 最初のパス    | プレーンなAPIキープロバイダー                         |
| `profile` | simpleの後  | auth profilesで制御されるプロバイダー                |
| `paired`  | profileの後 | 複数の関連エントリを合成する             |
| `late`    | 最後のパス     | 既存プロバイダーを上書きする（衝突時に勝つ） |

## 次のステップ

- [Channel Plugins](/ja-JP/plugins/sdk-channel-plugins) — プラグインがチャネルも提供する場合
- [SDK Runtime](/ja-JP/plugins/sdk-runtime) — `api.runtime` helpers（TTS、search、subagent）
- [SDK Overview](/ja-JP/plugins/sdk-overview) — 完全なsubpath importリファレンス
- [Plugin Internals](/ja-JP/plugins/architecture#provider-runtime-hooks) — hookの詳細とバンドル済みの例
