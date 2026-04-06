---
read_when:
    - 新しいモデルプロバイダープラグインを構築している
    - OpenAI互換プロキシまたはカスタムLLMをOpenClawに追加したい
    - プロバイダー認証、カタログ、runtime hooksを理解する必要がある
sidebarTitle: Provider Plugins
summary: OpenClaw用モデルプロバイダープラグインを構築するためのステップバイステップガイド
title: プロバイダープラグインの構築
x-i18n:
    generated_at: "2026-04-06T03:11:44Z"
    model: gpt-5.4
    provider: openai
    source_hash: 69500f46aa2cfdfe16e85b0ed9ee3c0032074be46f2d9c9d2940d18ae1095f47
    source_path: plugins/sdk-provider-plugins.md
    workflow: 15
---

# プロバイダープラグインの構築

このガイドでは、OpenClawにモデルプロバイダー
（LLM）を追加するプロバイダープラグインの構築方法を説明します。最後まで進めると、モデルカタログ、
APIキー認証、動的モデル解決を備えたプロバイダーが完成します。

<Info>
  まだOpenClawプラグインを一度も作成したことがない場合は、
  基本的なパッケージ
  構造とマニフェスト設定について、まず
  [はじめに](/ja-JP/plugins/building-plugins)を読んでください。
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

    マニフェストは`providerAuthEnvVars`を宣言することで、OpenClawが
    あなたのプラグインruntimeを読み込まずに認証情報を検出できるようにします。`modelSupport`は任意で、
    `acme-large`のような短縮モデルidから、
    runtime hooksが存在する前にOpenClawがあなたのプロバイダープラグインを自動ロードできるようにします。もし
    ClawHubでプロバイダーを公開する場合は、それらの`openclaw.compat`および`openclaw.build`フィールドが
    `package.json`で必須です。

  </Step>

  <Step title="プロバイダーを登録する">
    最小限のプロバイダーに必要なのは、`id`、`label`、`auth`、`catalog`です。

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
    `openclaw onboard --acme-ai-api-key <key>`を実行し、
    モデルとして`acme-ai/acme-large`を選択できるようになります。

    APIキー
    認証を伴う1つのテキストプロバイダーと、単一のcatalog-backed runtimeだけを登録するバンドルプロバイダーでは、より狭い
    `defineSingleProviderPluginEntry(...)`ヘルパーを優先してください。

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

    認証フローでオンボーディング中に`models.providers.*`、エイリアス、
    エージェントのデフォルトモデルもpatchする必要がある場合は、
    `openclaw/plugin-sdk/provider-onboard`のpresetヘルパーを使用してください。最も狭いヘルパーは
    `createDefaultModelPresetAppliers(...)`、
    `createDefaultModelsPresetAppliers(...)`、および
    `createModelCatalogPresetAppliers(...)`です。

    プロバイダーのネイティブendpointが
    通常の`openai-completions`トランスポート上でstreamed usage blocksをサポートする場合は、
    プロバイダーidチェックをハードコードする代わりに
    `openclaw/plugin-sdk/provider-catalog-shared`の共有catalog helpersを優先してください。`supportsNativeStreamingUsageCompat(...)`と
    `applyProviderNativeStreamingUsageCompat(...)`は
    endpoint capability mapからサポートを検出するため、ネイティブのMoonshot/DashScopeスタイルendpointも、
    プラグインがカスタムprovider idを使っていてもオプトインできます。

  </Step>

  <Step title="動的モデル解決を追加する">
    プロバイダーが任意のモデルID（プロキシやルーターのようなもの）を受け付ける場合は、
    `resolveDynamicModel`を追加します。

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

    解決にネットワーク呼び出しが必要な場合は、
    非同期ウォームアップ用に`prepareDynamicModel`を使ってください。完了後に
    `resolveDynamicModel`が再び実行されます。

  </Step>

  <Step title="runtime hooksを追加する（必要に応じて）">
    ほとんどのプロバイダーでは、`catalog` + `resolveDynamicModel`だけで十分です。プロバイダーで必要になったら
    hooksを段階的に追加してください。

    共有ヘルパーbuilderは、現在、最も一般的なreplay/tool-compat
    ファミリーをカバーしているため、通常プラグインでは各hookを
    1つずつ手作業で配線する必要はありません。

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
    | `openai-compatible` | OpenAI互換トランスポート向けの共有OpenAIスタイルreplay policy。tool-call-idのサニタイズ、assistant-first順序修正、そのトランスポートで必要な場合の汎用Geminiターン検証を含む |
    | `anthropic-by-model` | `modelId`で選ばれるClaude対応replay policy。Anthropic-messageトランスポートでは、解決されたモデルが実際にClaude idである場合にのみClaude固有のthinking-blockクリーンアップを適用 |
    | `google-gemini` | ネイティブGemini replay policyに加え、bootstrap replayサニタイズとtagged reasoning-outputモード |
    | `passthrough-gemini` | OpenAI互換プロキシトランスポート経由で動作するGeminiモデル向けのGemini thought-signatureサニタイズ。ネイティブGemini replay検証やbootstrap書き換えは有効にしない |
    | `hybrid-anthropic-openai` | 1つのプラグイン内でAnthropic-messageとOpenAI互換のモデルsurfaceを混在させるプロバイダー向けハイブリッドpolicy。任意のClaude専用thinking-blockドロップはAnthropic側にのみスコープされる |

    実際のバンドル例:

    - `google`: `google-gemini`
    - `openrouter`, `kilocode`, `opencode`, および `opencode-go`: `passthrough-gemini`
    - `amazon-bedrock` および `anthropic-vertex`: `anthropic-by-model`
    - `minimax`: `hybrid-anthropic-openai`
    - `moonshot`, `ollama`, `xai`, および `zai`: `openai-compatible`

    現在利用可能なstreamファミリー:

    | Family | 配線されるもの |
    | --- | --- |
    | `google-thinking` | 共有stream path上のGemini thinking payload正規化 |
    | `kilocode-thinking` | 共有proxy stream path上のKilo reasoning wrapper。`kilo/auto`および非対応proxy reasoning idsでは、挿入されたthinkingをスキップ |
    | `moonshot-thinking` | config + `/think` levelからのMoonshot binary native-thinking payloadマッピング |
    | `minimax-fast-mode` | 共有stream path上のMiniMax fast-mode model書き換え |
    | `openai-responses-defaults` | 共有ネイティブOpenAI/Codex Responses wrapper: attribution headers、`/fast`/`serviceTier`、text verbosity、ネイティブCodex web search、reasoning-compat payload整形、Responses context management |
    | `openrouter-thinking` | proxy route向けOpenRouter reasoning wrapper。非対応モデル/`auto`スキップは一元的に処理 |
    | `tool-stream-default-on` | Z.AIのように、明示的に無効化されない限りtool streamingを望むプロバイダー向けのデフォルトON `tool_stream` wrapper |

    実際のバンドル例:

    - `google`: `google-thinking`
    - `kilocode`: `kilocode-thinking`
    - `moonshot`: `moonshot-thinking`
    - `minimax` および `minimax-portal`: `minimax-fast-mode`
    - `openai` および `openai-codex`: `openai-responses-defaults`
    - `openrouter`: `openrouter-thinking`
    - `zai`: `tool-stream-default-on`

    `openclaw/plugin-sdk/provider-model-shared`は、replay-family
    enumに加え、それらのファミリーが利用する共有ヘルパーもエクスポートします。一般的な公開
    エクスポートには次が含まれます。

    - `ProviderReplayFamily`
    - `buildProviderReplayFamilyHooks(...)`
    - `buildOpenAICompatibleReplayPolicy(...)`、
      `buildAnthropicReplayPolicyForModel(...)`、
      `buildGoogleGeminiReplayPolicy(...)`、および
      `buildHybridAnthropicOrOpenAIReplayPolicy(...)`のような共有replay builders
    - `sanitizeGoogleGeminiReplayHistory(...)`
      および `resolveTaggedReasoningOutputMode()`のようなGemini replay helpers
    - `resolveProviderEndpoint(...)`、
      `normalizeProviderId(...)`, `normalizeGooglePreviewModelId(...)`, および
      `normalizeNativeXaiModelId(...)`のようなendpoint/model helpers

    `openclaw/plugin-sdk/provider-stream`は、family builderと、
    それらのファミリーが再利用する公開wrapper helpersの両方を公開します。一般的な公開エクスポート
    には次が含まれます。

    - `ProviderStreamFamily`
    - `buildProviderStreamFamilyHooks(...)`
    - `composeProviderStreamWrappers(...)`
    - 次のような共有OpenAI/Codex wrappers
      `createOpenAIAttributionHeadersWrapper(...)`、
      `createOpenAIFastModeWrapper(...)`、
      `createOpenAIServiceTierWrapper(...)`,
      `createOpenAIResponsesContextManagementWrapper(...)`, および
      `createCodexNativeWebSearchWrapper(...)`
    - `createOpenRouterWrapper(...)`、
      `createToolStreamWrapper(...)`, および `createMinimaxFastModeWrapper(...)`のような
      共有proxy/provider wrappers

    一部のstream helpersは、意図的にprovider-localのままにされています。現在のバンドル
    例: `@openclaw/anthropic-provider`は、
    公開`api.ts` /
    `contract-api.ts` seamから`wrapAnthropicProviderStream`、`resolveAnthropicBetas`、
    `resolveAnthropicFastMode`、`resolveAnthropicServiceTier`、および
    より低レベルのAnthropic wrapper buildersをエクスポートしています。これらのヘルパーがAnthropic専用のままなのは、
    Claude OAuth beta handlingと`context1m` gatingもエンコードしているためです。

    他のバンドルプロバイダーも、
    挙動がファミリー間できれいに共有されない場合は、トランスポート固有wrapperをローカルに保持しています。現在の例:
    バンドルxAIプラグインは、ネイティブxAI Responses整形を独自の
    `wrapStreamFn`内に保持しており、`/fast` alias書き換え、デフォルト`tool_stream`、
    非対応strict-toolクリーンアップ、およびxAI固有のreasoning-payload
    削除を含みます。

    `openclaw/plugin-sdk/provider-tools`は現在、1つの共有
    tool-schemaファミリーと、共有schema/compat helpersを公開しています。

    - `ProviderToolCompatFamily`は、現在の共有family一覧を文書化しています。
    - `buildProviderToolCompatFamilyHooks("gemini")`は、Gemini-safeなtool schemasを必要とするプロバイダー向けにGemini schema
      cleanup + diagnosticsを配線します。
    - `normalizeGeminiToolSchemas(...)`と`inspectGeminiToolSchemas(...)`は、
      基盤となる公開Gemini schema helpersです。
    - `resolveXaiModelCompatPatch()`は、バンドルxAI compat patchを返します:
      `toolSchemaProfile: "xai"`、非対応schema keywords、ネイティブ
      `web_search`サポート、およびHTML entity化されたtool-call引数のデコード。
    - `applyXaiModelCompat(model)`は、その同じxAI compat patchを、
      runnerに到達する前の解決済みモデルへ適用します。

    実際のバンドル例: xAIプラグインは、xAIルールをコアにハードコードする代わりに、
    そのcompat metadataの所有権をプロバイダー側に保つため、
    `normalizeResolvedModel`と`contributeResolvedModelCompat`を使用しています。

    同じpackage-rootパターンは、他のバンドルプロバイダーも支えています。

    - `@openclaw/openai-provider`: `api.ts`はprovider builders、
      default-model helpers、およびrealtime provider buildersをエクスポート
    - `@openclaw/openrouter-provider`: `api.ts`はprovider builder
      に加えてonboarding/config helpersをエクスポート

    <Tabs>
      <Tab title="トークン交換">
        推論呼び出しごとにトークン交換が必要なプロバイダーの場合:

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
        カスタムのリクエストヘッダーやbody変更が必要なプロバイダーの場合:

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
      <Tab title="ネイティブトランスポートID">
        汎用HTTPまたはWebSocketトランスポート上で
        ネイティブなリクエスト/セッションヘッダーやmetadataが必要なプロバイダーの場合:

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
      OpenClawはこの順序でhooksを呼び出します。ほとんどのプロバイダーが使うのは2〜3個だけです。

      | # | Hook | 使用するタイミング |
      | --- | --- | --- |
      | 1 | `catalog` | モデルカタログまたはbase URLデフォルト |
      | 2 | `applyConfigDefaults` | config materialization中のprovider所有グローバルデフォルト |
      | 3 | `normalizeModelId` | lookup前のレガシー/preview model-id aliasクリーンアップ |
      | 4 | `normalizeTransport` | 汎用モデル組み立て前のprovider-family `api` / `baseUrl`クリーンアップ |
      | 5 | `normalizeConfig` | `models.providers.<id>` configを正規化 |
      | 6 | `applyNativeStreamingUsageCompat` | config providers向けのネイティブstreaming-usage compat書き換え |
      | 7 | `resolveConfigApiKey` | provider所有のenv-marker auth解決 |
      | 8 | `resolveSyntheticAuth` | local/self-hostedまたはconfig-backed synthetic auth |
      | 9 | `shouldDeferSyntheticProfileAuth` | synthetic stored-profile placeholdersをenv/config authより後ろに下げる |
      | 10 | `resolveDynamicModel` | 任意のupstream model IDsを受け付ける |
      | 11 | `prepareDynamicModel` | 解決前の非同期metadata取得 |
      | 12 | `normalizeResolvedModel` | runner前のトランスポート書き換え |

    Runtime fallbackに関する注意:

    - `normalizeConfig`はまず一致したproviderを確認し、その後、
      実際にconfigを変更するprovider hook-capable provider pluginsを順に確認します。
      どのprovider hookもサポートされるGoogle-family config entryを書き換えない場合は、
      バンドルGoogle config normalizerが引き続き適用されます。
    - `resolveConfigApiKey`は、公開されていればprovider hookを使います。バンドル
      `amazon-bedrock`パスには、ここで組み込みのAWS env-marker resolverもありますが、
      Bedrock runtime auth自体は依然としてAWS SDK default
      chainを使います。
      | 13 | `contributeResolvedModelCompat` | 別の互換トランスポートの背後にあるvendor models向けcompat flags |
      | 14 | `capabilities` | レガシーな静的capability bag。互換性用のみ |
      | 15 | `normalizeToolSchemas` | 登録前のprovider所有tool-schema cleanup |
      | 16 | `inspectToolSchemas` | provider所有tool-schema diagnostics |
      | 17 | `resolveReasoningOutputMode` | taggedとnativeのreasoning-output contract |
      | 18 | `prepareExtraParams` | デフォルトリクエストparams |
      | 19 | `createStreamFn` | 完全にカスタムなStreamFn transport |
      | 20 | `wrapStreamFn` | 通常stream path上のカスタムheaders/body wrappers |
      | 21 | `resolveTransportTurnState` | ネイティブなターンごとのheaders/metadata |
      | 22 | `resolveWebSocketSessionPolicy` | ネイティブWSセッションheaders/cool-down |
      | 23 | `formatApiKey` | カスタムruntime token shape |
      | 24 | `refreshOAuth` | カスタムOAuth refresh |
      | 25 | `buildAuthDoctorHint` | auth修復ガイダンス |
      | 26 | `matchesContextOverflowError` | provider所有のoverflow検出 |
      | 27 | `classifyFailoverReason` | provider所有のrate-limit/overload分類 |
      | 28 | `isCacheTtlEligible` | prompt cache TTL gating |
      | 29 | `buildMissingAuthMessage` | カスタムmissing-authヒント |
      | 30 | `suppressBuiltInModel` | 古くなったupstream rowsを非表示 |
      | 31 | `augmentModelCatalog` | synthetic forward-compat rows |
      | 32 | `isBinaryThinking` | binary thinkingのオン/オフ |
      | 33 | `supportsXHighThinking` | `xhigh` reasoningサポート |
      | 34 | `resolveDefaultThinkingLevel` | デフォルト`/think` policy |
      | 35 | `isModernModelRef` | live/smoke model matching |
      | 36 | `prepareRuntimeAuth` | 推論前のトークン交換 |
      | 37 | `resolveUsageAuth` | カスタムusage credential parsing |
      | 38 | `fetchUsageSnapshot` | カスタムusage endpoint |
      | 39 | `createEmbeddingProvider` | memory/search向けprovider所有embedding adapter |
      | 40 | `buildReplayPolicy` | カスタムtranscript replay/compaction policy |
      | 41 | `sanitizeReplayHistory` | 汎用クリーンアップ後のprovider固有replay書き換え |
      | 42 | `validateReplayTurns` | embedded runner前の厳格なreplay-turn検証 |
      | 43 | `onModelSelected` | 選択後コールバック（例: telemetry） |

      プロンプトチューニングに関する注意:

      - `resolveSystemPromptContribution`により、プロバイダーは
        モデルファミリー向けのcache-awareな
        system-promptガイダンスを注入できます。挙動が1つのprovider/model
        familyに属し、安定/動的cache分割を維持すべき場合は、
        `before_prompt_build`よりこちらを優先してください。

      詳細な説明と実例については、
      [内部: Provider Runtime Hooks](/ja-JP/plugins/architecture#provider-runtime-hooks)を参照してください。
    </Accordion>

  </Step>

  <Step title="追加capabilitiesを追加する（任意）">
    <a id="step-5-add-extra-capabilities"></a>
    プロバイダープラグインは、テキスト推論に加えて、speech、realtime transcription、realtime
    voice、media understanding、image generation、video generation、web fetch、
    web searchを登録できます。

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
          maxVideos: 1,
          maxDurationSeconds: 10,
          supportsResolution: true,
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
    企業向けプラグイン（ベンダーごとに1プラグイン）に推奨される
    パターンです。[内部: Capability Ownership](/ja-JP/plugins/architecture#capability-ownership-model)を参照してください。

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

## ClawHubに公開する

プロバイダープラグインは、他の外部コードプラグインと同じ方法で公開します。

```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
```

ここではレガシーなskill専用publish aliasを使わないでください。プラグインパッケージは
`clawhub package publish`を使う必要があります。

## ファイル構成

```
<bundled-plugin-root>/acme-ai/
├── package.json              # openclaw.providers metadata
├── openclaw.plugin.json      # providerAuthEnvVarsを含むマニフェスト
├── index.ts                  # definePluginEntry + registerProvider
└── src/
    ├── provider.test.ts      # テスト
    └── usage.ts              # usage endpoint（任意）
```

## Catalog orderリファレンス

`catalog.order`は、組み込み
プロバイダーに対してあなたのcatalogがいつマージされるかを制御します。

| Order     | タイミング | 使用例 |
| --------- | ---------- | ------ |
| `simple`  | 最初のパス | プレーンなAPIキープロバイダー |
| `profile` | `simple`の後 | 認証profilesで制御されるプロバイダー |
| `paired`  | `profile`の後 | 関連する複数エントリを合成する |
| `late`    | 最後のパス | 既存プロバイダーを上書きする（競合時に勝つ） |

## 次のステップ

- [チャネルプラグイン](/ja-JP/plugins/sdk-channel-plugins) — プラグインがチャネルも提供する場合
- [SDK Runtime](/ja-JP/plugins/sdk-runtime) — `api.runtime` helpers（TTS、search、subagent）
- [SDK Overview](/ja-JP/plugins/sdk-overview) — 完全なsubpath importリファレンス
- [Plugin Internals](/ja-JP/plugins/architecture#provider-runtime-hooks) — hookの詳細とバンドル例
