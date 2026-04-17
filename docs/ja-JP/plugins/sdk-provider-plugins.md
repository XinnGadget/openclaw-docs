---
read_when:
    - 新しいモデル provider plugin を構築する場合
    - OpenAI 互換プロキシまたはカスタム LLM を OpenClaw に追加したい場合
    - provider auth、catalog、およびランタイムフックを理解する必要があります
sidebarTitle: Provider Plugins
summary: OpenClaw 向けモデル provider plugin の構築手順ガイド
title: provider plugin の構築
x-i18n:
    generated_at: "2026-04-11T02:46:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: 06d7c5da6556dc3d9673a31142ff65eb67ddc97fc0c1a6f4826a2c7693ecd5e3
    source_path: plugins/sdk-provider-plugins.md
    workflow: 15
---

# provider plugin の構築

このガイドでは、OpenClaw にモデル provider
（LLM）を追加する provider plugin の構築手順を説明します。最終的には、モデル catalog、
API キー認証、および動的モデル解決を備えた provider が完成します。

<Info>
  まだ OpenClaw plugin を一度も作成したことがない場合は、まず
  基本的なパッケージ構造と manifest 設定について
  [はじめに](/ja-JP/plugins/building-plugins) を読んでください。
</Info>

<Tip>
  Provider plugin は OpenClaw の通常の推論ループにモデルを追加します。モデルを、
  スレッド、compaction、またはツールイベントを管理するネイティブなエージェントデーモン経由で実行する必要がある場合は、
  デーモンのプロトコル詳細を core に入れるのではなく、
  provider を [agent harness](/ja-JP/plugins/sdk-agent-harness)
  と組み合わせてください。
</Tip>

## ウォークスルー

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="パッケージと manifest">
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
      "providerAuthAliases": {
        "acme-ai-coding": "acme-ai"
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

    manifest は `providerAuthEnvVars` を宣言することで、OpenClaw が
    plugin ランタイムを読み込まずに認証情報を検出できるようにします。ある provider バリアントで別の provider id の auth を再利用させたい場合は、`providerAuthAliases`
    を追加してください。`modelSupport`
    は任意で、ランタイムフックが存在する前でも、`acme-large` のような短縮モデル id から OpenClaw が provider plugin を自動読み込みできるようにします。provider を
    ClawHub で公開する場合、これらの `openclaw.compat` および `openclaw.build` フィールドは
    `package.json` 内で必須です。

  </Step>

  <Step title="provider を登録する">
    最小限の provider に必要なのは、`id`、`label`、`auth`、および `catalog` です:

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

    これで動作する provider になります。ユーザーは
    `openclaw onboard --acme-ai-api-key <key>` を実行して、
    モデルとして `acme-ai/acme-large` を選択できるようになります。

    アップストリーム provider が OpenClaw と異なる制御トークンを使う場合は、
    ストリーム経路を置き換えるのではなく、小さな双方向テキスト変換を追加してください:

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

    `input` は、転送前に最終システムプロンプトとテキストメッセージ内容を書き換えます。
    `output` は、assistant テキスト差分と最終テキストを、OpenClaw が自身の
    制御マーカーやチャネル配信を解析する前に書き換えます。

    API キー認証と単一の catalog ベースランタイムを持つ
    1 つのテキスト provider だけを登録するバンドル provider では、より狭い
    `defineSingleProviderPluginEntry(...)` ヘルパーを優先してください:

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

    auth フローで、オンボーディング中に `models.providers.*`、aliases、
    およびエージェントのデフォルトモデルも更新する必要がある場合は、
    `openclaw/plugin-sdk/provider-onboard` の preset ヘルパーを使用してください。最も狭い
    ヘルパーは `createDefaultModelPresetAppliers(...)`、
    `createDefaultModelsPresetAppliers(...)`、および
    `createModelCatalogPresetAppliers(...)` です。

    provider ネイティブエンドポイントが、通常の
    `openai-completions` 転送でストリーミング usage ブロックをサポートしている場合は、provider-id チェックをハードコードするのではなく
    `openclaw/plugin-sdk/provider-catalog-shared` の共通 catalog ヘルパーを優先してください。
    `supportsNativeStreamingUsageCompat(...)` と
    `applyProviderNativeStreamingUsageCompat(...)` は、エンドポイント capability map からサポートを検出するため、custom provider id を使う plugin でも、ネイティブ Moonshot/DashScope 形式エンドポイントをオプトインさせられます。

  </Step>

  <Step title="動的モデル解決を追加する">
    provider が任意のモデル ID を受け付ける場合（プロキシやルーターのようなケース）は、
    `resolveDynamicModel` を追加します:

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

    解決にネットワーク呼び出しが必要な場合は、非同期ウォームアップ用に
    `prepareDynamicModel` を使ってください — 完了後に `resolveDynamicModel` が再度実行されます。

  </Step>

  <Step title="ランタイムフックを追加する（必要に応じて）">
    ほとんどの provider では `catalog` + `resolveDynamicModel` だけで十分です。provider に必要になったら、
    フックを段階的に追加してください。

    共通ヘルパービルダーは、現在最も一般的な replay/tool-compat
    ファミリーをカバーしているため、plugin では通常、各フックを 1 つずつ手作業で接続する必要はありません:

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

    現在利用可能な replay ファミリー:

    | ファミリー | 接続される内容 |
    | --- | --- |
    | `openai-compatible` | OpenAI 互換転送向けの共有 OpenAI スタイル replay ポリシー。tool-call-id のサニタイズ、assistant-first 順序の修正、およびその転送で必要な場合の汎用 Gemini ターン検証を含みます |
    | `anthropic-by-model` | `modelId` によって選ばれる Claude 対応 replay ポリシー。Anthropic-message 転送では、解決されたモデルが実際に Claude id の場合にのみ Claude 固有の thinking-block クリーンアップが適用されます |
    | `google-gemini` | ネイティブ Gemini replay ポリシーに加え、bootstrap replay サニタイズとタグ付き reasoning-output モード |
    | `passthrough-gemini` | OpenAI 互換プロキシ転送上で動作する Gemini モデル向けの Gemini thought-signature サニタイズ。ネイティブ Gemini replay 検証や bootstrap 書き換えは有効にしません |
    | `hybrid-anthropic-openai` | 1 つの plugin 内で Anthropic-message と OpenAI 互換のモデルサーフェスを混在させる provider 向けのハイブリッドポリシー。任意の Claude 専用 thinking-block 除去は Anthropic 側に限定されます |

    実際のバンドル例:

    - `google` と `google-gemini-cli`: `google-gemini`
    - `openrouter`、`kilocode`、`opencode`、および `opencode-go`: `passthrough-gemini`
    - `amazon-bedrock` と `anthropic-vertex`: `anthropic-by-model`
    - `minimax`: `hybrid-anthropic-openai`
    - `moonshot`、`ollama`、`xai`、および `zai`: `openai-compatible`

    現在利用可能なストリームファミリー:

    | ファミリー | 接続される内容 |
    | --- | --- |
    | `google-thinking` | 共有ストリーム経路上での Gemini thinking ペイロード正規化 |
    | `kilocode-thinking` | 共有プロキシストリーム経路上での Kilo reasoning ラッパー。`kilo/auto` と未対応のプロキシ reasoning id では注入された thinking をスキップ |
    | `moonshot-thinking` | config + `/think` レベルからの Moonshot バイナリ native-thinking ペイロードマッピング |
    | `minimax-fast-mode` | 共有ストリーム経路上での MiniMax fast-mode モデル書き換え |
    | `openai-responses-defaults` | 共有のネイティブ OpenAI/Codex Responses ラッパー: attribution headers、`/fast`/`serviceTier`、text verbosity、ネイティブ Codex web search、reasoning-compat ペイロード整形、および Responses コンテキスト管理 |
    | `openrouter-thinking` | プロキシ経路向けの OpenRouter reasoning ラッパー。未対応モデル/`auto` スキップは中央処理されます |
    | `tool-stream-default-on` | Z.AI のような provider 向けのデフォルト有効 `tool_stream` ラッパー。明示的に無効化されない限りツールストリーミングを使用 |

    実際のバンドル例:

    - `google` と `google-gemini-cli`: `google-thinking`
    - `kilocode`: `kilocode-thinking`
    - `moonshot`: `moonshot-thinking`
    - `minimax` と `minimax-portal`: `minimax-fast-mode`
    - `openai` と `openai-codex`: `openai-responses-defaults`
    - `openrouter`: `openrouter-thinking`
    - `zai`: `tool-stream-default-on`

    `openclaw/plugin-sdk/provider-model-shared` は、replay-family
    enum と、それらのファミリーの土台となる共有ヘルパーもエクスポートします。一般的な公開エクスポートには次が含まれます:

    - `ProviderReplayFamily`
    - `buildProviderReplayFamilyHooks(...)`
    - `buildOpenAICompatibleReplayPolicy(...)`、
      `buildAnthropicReplayPolicyForModel(...)`、
      `buildGoogleGeminiReplayPolicy(...)`、および
      `buildHybridAnthropicOrOpenAIReplayPolicy(...)` のような共有 replay ビルダー
    - `sanitizeGoogleGeminiReplayHistory(...)`
      や `resolveTaggedReasoningOutputMode()` のような Gemini replay ヘルパー
    - `resolveProviderEndpoint(...)`、
      `normalizeProviderId(...)`、`normalizeGooglePreviewModelId(...)`、および
      `normalizeNativeXaiModelId(...)` のような endpoint/model ヘルパー

    `openclaw/plugin-sdk/provider-stream` は、family builder と、
    それらのファミリーが再利用する公開ラッパーヘルパーの両方を公開します。一般的な公開エクスポート
    には次が含まれます:

    - `ProviderStreamFamily`
    - `buildProviderStreamFamilyHooks(...)`
    - `composeProviderStreamWrappers(...)`
    - `createOpenAIAttributionHeadersWrapper(...)`、
      `createOpenAIFastModeWrapper(...)`、
      `createOpenAIServiceTierWrapper(...)`、
      `createOpenAIResponsesContextManagementWrapper(...)`、および
      `createCodexNativeWebSearchWrapper(...)` のような共有 OpenAI/Codex ラッパー
    - `createOpenRouterWrapper(...)`、
      `createToolStreamWrapper(...)`、および `createMinimaxFastModeWrapper(...)` のような共有 proxy/provider ラッパー

    一部のストリームヘルパーは意図的に provider ローカルのままになっています。現在のバンドル
    例: `@openclaw/anthropic-provider` は
    `wrapAnthropicProviderStream`、`resolveAnthropicBetas`、
    `resolveAnthropicFastMode`、`resolveAnthropicServiceTier`、および
    より低レベルの Anthropic ラッパービルダーを公開 `api.ts` /
    `contract-api.ts` シームからエクスポートします。これらのヘルパーが Anthropic 固有のままなのは、
    Claude OAuth beta 処理と `context1m` ゲーティングもエンコードしているためです。

    他のバンドル provider も、動作がファミリー間でうまく共有できない場合は、
    転送固有ラッパーをローカルに保持します。現在の例: バンドルされた
    xAI plugin は、ネイティブ xAI Responses 整形を自身の
    `wrapStreamFn` 内に保持しています。これには `/fast` エイリアス書き換え、デフォルトの `tool_stream`、
    未対応 strict-tool クリーンアップ、および xAI 固有の reasoning-payload
    除去が含まれます。

    `openclaw/plugin-sdk/provider-tools` は現在、1つの共有
    tool-schema ファミリーと共有 schema/compat ヘルパーを公開しています:

    - `ProviderToolCompatFamily` は、現在の共有ファミリー一覧を文書化します。
    - `buildProviderToolCompatFamilyHooks("gemini")` は、Gemini-safe なツールスキーマが必要な provider 向けに Gemini スキーマ
      クリーンアップ + diagnostics を接続します。
    - `normalizeGeminiToolSchemas(...)` と `inspectGeminiToolSchemas(...)`
      は、その土台となる公開 Gemini スキーマヘルパーです。
    - `resolveXaiModelCompatPatch()` は、バンドルされた xAI compat patch を返します:
      `toolSchemaProfile: "xai"`、未対応スキーマキーワード、ネイティブ
      `web_search` サポート、および HTML entity のツール呼び出し引数デコードです。
    - `applyXaiModelCompat(model)` は、同じ xAI compat patch を
      解決済みモデルに適用してから runner に渡します。

    実際のバンドル例: xAI plugin は `normalizeResolvedModel` と
    `contributeResolvedModelCompat` を使い、その compat メタデータを
    core に xAI ルールをハードコードするのではなく provider 側で管理しています。

    同じ package-root パターンは、他のバンドル provider でも使われています:

    - `@openclaw/openai-provider`: `api.ts` は provider builder、
      default-model ヘルパー、および realtime provider builder をエクスポート
    - `@openclaw/openrouter-provider`: `api.ts` は provider builder
      に加えて onboarding/config ヘルパーをエクスポート

    <Tabs>
      <Tab title="トークン交換">
        各推論呼び出しの前にトークン交換が必要な provider の場合:

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
        カスタムリクエストヘッダーやボディ変更が必要な provider の場合:

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
      <Tab title="ネイティブ転送 ID">
        汎用 HTTP または WebSocket 転送上で、ネイティブの
        リクエスト/セッションヘッダーやメタデータが必要な provider の場合:

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
      <Tab title="使用量と請求">
        使用量/請求データを公開する provider の場合:

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

    <Accordion title="利用可能なすべての provider フック">
      OpenClaw は次の順序でフックを呼び出します。ほとんどの provider では 2〜3 個しか使いません:

      | # | フック | 使用するタイミング |
      | --- | --- | --- |
      | 1 | `catalog` | モデル catalog または base URL のデフォルト |
      | 2 | `applyConfigDefaults` | config マテリアライズ時の provider 所有グローバルデフォルト |
      | 3 | `normalizeModelId` | 参照前の legacy/preview model-id エイリアスクリーンアップ |
      | 4 | `normalizeTransport` | 汎用モデル組み立て前の provider-family `api` / `baseUrl` クリーンアップ |
      | 5 | `normalizeConfig` | `models.providers.<id>` config を正規化 |
      | 6 | `applyNativeStreamingUsageCompat` | config provider 向けネイティブ streaming-usage compat 書き換え |
      | 7 | `resolveConfigApiKey` | provider 所有の env-marker auth 解決 |
      | 8 | `resolveSyntheticAuth` | local/self-hosted または config ベースの synthetic auth |
      | 9 | `shouldDeferSyntheticProfileAuth` | synthetic な保存済み profile プレースホルダーを env/config auth より後ろに下げる |
      | 10 | `resolveDynamicModel` | 任意のアップストリームモデル ID を受け入れる |
      | 11 | `prepareDynamicModel` | 解決前の非同期メタデータ取得 |
      | 12 | `normalizeResolvedModel` | runner 前の転送書き換え |

    ランタイムフォールバックに関する注意:

    - `normalizeConfig` は、まず一致した provider を確認し、その後
      実際に config を変更するものが見つかるまで、他の
      フック対応 provider plugin を確認します。
      サポート対象の Google-family config エントリを書き換える provider フックがなければ、
      バンドルされた Google config normalizer が引き続き適用されます。
    - `resolveConfigApiKey` は、公開されている場合は provider フックを使います。バンドルされた
      `amazon-bedrock` 経路にも、ここに組み込みの AWS env-marker resolver がありますが、
      Bedrock ランタイム auth 自体は引き続き AWS SDK デフォルト
      チェーンを使います。
      | 13 | `contributeResolvedModelCompat` | 別の互換転送の背後にある vendor モデル向け compat フラグ |
      | 14 | `capabilities` | legacy な静的 capability バッグ。互換性専用 |
      | 15 | `normalizeToolSchemas` | 登録前の provider 所有ツールスキーマクリーンアップ |
      | 16 | `inspectToolSchemas` | provider 所有ツールスキーマ diagnostics |
      | 17 | `resolveReasoningOutputMode` | タグ付き vs ネイティブ reasoning-output 契約 |
      | 18 | `prepareExtraParams` | デフォルトリクエストパラメータ |
      | 19 | `createStreamFn` | 完全カスタムの StreamFn 転送 |
      | 20 | `wrapStreamFn` | 通常ストリーム経路上のカスタムヘッダー/ボディラッパー |
      | 21 | `resolveTransportTurnState` | ネイティブなターンごとのヘッダー/メタデータ |
      | 22 | `resolveWebSocketSessionPolicy` | ネイティブ WS セッションヘッダー/クールダウン |
      | 23 | `formatApiKey` | カスタムランタイムトークン形式 |
      | 24 | `refreshOAuth` | カスタム OAuth リフレッシュ |
      | 25 | `buildAuthDoctorHint` | auth 修復ガイダンス |
      | 26 | `matchesContextOverflowError` | provider 所有のオーバーフロー検出 |
      | 27 | `classifyFailoverReason` | provider 所有のレート制限/過負荷分類 |
      | 28 | `isCacheTtlEligible` | プロンプトキャッシュ TTL ゲーティング |
      | 29 | `buildMissingAuthMessage` | カスタムの認証欠落ヒント |
      | 30 | `suppressBuiltInModel` | 古くなったアップストリーム行を非表示 |
      | 31 | `augmentModelCatalog` | synthetic な forward-compat 行 |
      | 32 | `isBinaryThinking` | バイナリ thinking のオン/オフ |
      | 33 | `supportsXHighThinking` | `xhigh` reasoning サポート |
      | 34 | `resolveDefaultThinkingLevel` | デフォルト `/think` ポリシー |
      | 35 | `isModernModelRef` | live/smoke モデルマッチング |
      | 36 | `prepareRuntimeAuth` | 推論前のトークン交換 |
      | 37 | `resolveUsageAuth` | カスタム使用量認証情報解析 |
      | 38 | `fetchUsageSnapshot` | カスタム使用量エンドポイント |
      | 39 | `createEmbeddingProvider` | memory/search 用の provider 所有 embedding アダプター |
      | 40 | `buildReplayPolicy` | カスタム transcript replay/compaction ポリシー |
      | 41 | `sanitizeReplayHistory` | 汎用クリーンアップ後の provider 固有 replay 書き換え |
      | 42 | `validateReplayTurns` | 埋め込み runner 前の厳格な replay-turn 検証 |
      | 43 | `onModelSelected` | 選択後コールバック（例: telemetry） |

      プロンプトチューニングに関する注意:

      - `resolveSystemPromptContribution` を使うと、provider はモデルファミリー向けにキャッシュを意識した
        システムプロンプトガイダンスを注入できます。動作が 1 つの provider/モデル
        ファミリーに属し、安定/動的キャッシュ分割を維持すべき場合は、
        `before_prompt_build` よりこちらを優先してください。

      詳細な説明と実例については、
      [Internals: Provider Runtime Hooks](/ja-JP/plugins/architecture#provider-runtime-hooks) を参照してください。
    </Accordion>

  </Step>

  <Step title="追加機能を加える（任意）">
    <a id="step-5-add-extra-capabilities"></a>
    provider plugin は、テキスト推論に加えて、speech、realtime transcription、realtime
    voice、メディア理解、画像生成、動画生成、web fetch、
    および web search を登録できます:

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

    OpenClaw はこれを **hybrid-capability** plugin と分類します。これは
    会社単位の plugin（ベンダーごとに 1 plugin）に推奨される
    パターンです。
    [Internals: Capability Ownership](/ja-JP/plugins/architecture#capability-ownership-model) を参照してください。

    動画生成では、上記のようなモード認識 capability 形状を優先してください:
    `generate`、`imageToVideo`、`videoToVideo`。`maxInputImages`、`maxInputVideos`、`maxDurationSeconds` のような
    フラットな集約フィールドだけでは、
    transform-mode サポートや無効なモードを適切に表現できません。

    音楽生成 provider も同じパターンに従う必要があります:
    プロンプトのみの生成には `generate`、参照画像ベースの
    生成には `edit` を使用します。`maxInputImages`、
    `supportsLyrics`、`supportsFormat` のようなフラットな集約フィールドだけでは
    edit サポートを表現できません。明示的な `generate` / `edit`
    ブロックが期待される契約です。

  </Step>

  <Step title="テスト">
    <a id="step-6-test"></a>
    ```typescript src/provider.test.ts
    import { describe, it, expect } from "vitest";
    // index.ts または専用ファイルから provider config object を export してください
    import { acmeProvider } from "./provider.js";

    describe("acme-ai provider", () => {
      it("動的モデルを解決する", () => {
        const model = acmeProvider.resolveDynamicModel!({
          modelId: "acme-beta-v3",
        } as any);
        expect(model.id).toBe("acme-beta-v3");
        expect(model.provider).toBe("acme-ai");
      });

      it("キーがある場合に catalog を返す", async () => {
        const result = await acmeProvider.catalog!.run({
          resolveProviderApiKey: () => ({ apiKey: "test-key" }),
        } as any);
        expect(result?.provider?.models).toHaveLength(2);
      });

      it("キーがない場合は null catalog を返す", async () => {
        const result = await acmeProvider.catalog!.run({
          resolveProviderApiKey: () => ({ apiKey: undefined }),
        } as any);
        expect(result).toBeNull();
      });
    });
    ```

  </Step>
</Steps>

## ClawHub に公開する

provider plugin は、他の外部コード plugin と同じ方法で公開します:

```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
```

ここではレガシーな skill 専用 publish エイリアスを使わないでください。plugin パッケージでは
`clawhub package publish` を使う必要があります。

## ファイル構成

```
<bundled-plugin-root>/acme-ai/
├── package.json              # openclaw.providers メタデータ
├── openclaw.plugin.json      # provider auth メタデータを含む Manifest
├── index.ts                  # definePluginEntry + registerProvider
└── src/
    ├── provider.test.ts      # テスト
    └── usage.ts              # 使用量エンドポイント（任意）
```

## catalog order リファレンス

`catalog.order` は、組み込み
provider に対して catalog をいつマージするかを制御します:

| Order     | タイミング | 使用例 |
| --------- | ------------- | ----------------------------------------------- |
| `simple`  | 最初のパス | プレーンな API キー provider |
| `profile` | `simple` の後 | auth profile によって制御される provider |
| `paired`  | `profile` の後 | 複数の関連エントリを合成する |
| `late`    | 最後のパス | 既存の provider を上書きする（衝突時に優先） |

## 次のステップ

- [Channel Plugins](/ja-JP/plugins/sdk-channel-plugins) — plugin がチャネルも提供する場合
- [SDK Runtime](/ja-JP/plugins/sdk-runtime) — `api.runtime` ヘルパー（TTS、search、subagent）
- [SDK Overview](/ja-JP/plugins/sdk-overview) — 完全な subpath import リファレンス
- [Plugin Internals](/ja-JP/plugins/architecture#provider-runtime-hooks) — フック詳細とバンドル例
