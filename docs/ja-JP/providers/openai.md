---
read_when:
    - OpenClawでOpenAI modelsを使いたいとき
    - API keyの代わりにCodexサブスクリプション認証を使いたいとき
summary: OpenClawでAPI keyまたはCodexサブスクリプション経由でOpenAIを使う
title: OpenAI
x-i18n:
    generated_at: "2026-04-07T04:46:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6a2ce1ce5f085fe55ec50b8d20359180b9002c9730820cd5b0e011c3bf807b64
    source_path: providers/openai.md
    workflow: 15
---

# OpenAI

OpenAIはGPT models向けの開発者APIを提供しています。Codexは、サブスクリプションアクセス用の**ChatGPT sign-in** または従量課金アクセス用の**API key** sign-inをサポートします。Codex cloudではChatGPT sign-inが必要です。
OpenAIは、OpenClawのような外部ツールやワークフローでのサブスクリプションOAuth利用を明示的にサポートしています。

## デフォルトの対話スタイル

OpenClawは、`openai/*` と
`openai-codex/*` の両方の実行に対して、小さなOpenAI固有のprompt overlayを追加できます。デフォルトでは、このoverlayはassistantを温かく、
協調的で、簡潔、直接的、かつ少し感情表現豊かに保ちつつ、
ベースのOpenClaw system promptは置き換えません。friendly overlayはまた、
全体の出力を簡潔に保ちながら、自然に合う場面ではたまにemojiを使うことも
許可します。

設定キー:

`plugins.entries.openai.config.personality`

許可される値:

- `"friendly"`: デフォルト。OpenAI固有overlayを有効にします。
- `"on"`: `"friendly"` の別名。
- `"off"`: overlayを無効にし、ベースのOpenClaw promptのみを使用します。

適用範囲:

- `openai/*` modelsに適用されます。
- `openai-codex/*` modelsに適用されます。
- 他のproviderには影響しません。

この動作はデフォルトで有効です。将来のローカルconfig変更でもこれを
維持したい場合は、明示的に `"friendly"` を残してください:

```json5
{
  plugins: {
    entries: {
      openai: {
        config: {
          personality: "friendly",
        },
      },
    },
  },
}
```

### OpenAI prompt overlayを無効にする

未変更のベースOpenClaw promptを使いたい場合は、overlayを `"off"` に設定します:

```json5
{
  plugins: {
    entries: {
      openai: {
        config: {
          personality: "off",
        },
      },
    },
  },
}
```

config CLIから直接設定することもできます:

```bash
openclaw config set plugins.entries.openai.config.personality off
```

OpenClawはこの設定を実行時に大文字小文字を区別せず正規化するため、
`"Off"` のような値でもfriendly overlayは無効になります。

## Option A: OpenAI API key（OpenAI Platform）

**最適な用途:** 直接APIアクセスと従量課金。
API keyはOpenAI dashboardから取得してください。

ルート概要:

- `openai/gpt-5.4` = 直接のOpenAI Platform APIルート
- `OPENAI_API_KEY`（または同等のOpenAI provider設定）が必要
- OpenClawでは、ChatGPT/Codex sign-inは `openai/*` ではなく `openai-codex/*` 経由になります

### CLIセットアップ

```bash
openclaw onboard --auth-choice openai-api-key
# または非対話
openclaw onboard --openai-api-key "$OPENAI_API_KEY"
```

### 設定スニペット

```json5
{
  env: { OPENAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

OpenAIの現在のAPI modelドキュメントでは、直接の
OpenAI API利用向けに `gpt-5.4` と `gpt-5.4-pro` が挙げられています。OpenClawはその両方を `openai/*` Responsesパス経由で転送します。
OpenClawは、古い `openai/gpt-5.3-codex-spark` 行を意図的に非表示にしています。
これは、直接のOpenAI API呼び出しではlive trafficで拒否されるためです。

OpenClawは、直接のOpenAI
APIパス上で `openai/gpt-5.3-codex-spark` を公開しません。`pi-ai` には引き続きそのmodelの組み込み行がありますが、live OpenAI API
リクエストは現在それを拒否します。OpenClawではSparkはCodex専用として扱われます。

## 画像生成

バンドルされた `openai` pluginは、共有
`image_generate` tool経由の画像生成も登録します。

- デフォルト画像model: `openai/gpt-image-1`
- Generate: 1リクエストあたり最大4画像
- Edit mode: 有効、最大5枚の参照画像
- `size` をサポート
- 現在のOpenAI固有の注意点: OpenClawは現在 `aspectRatio` または
  `resolution` の上書きをOpenAI Images APIへ転送しません

OpenAIをデフォルトの画像providerとして使うには:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "openai/gpt-image-1",
      },
    },
  },
}
```

共有toolの
パラメータ、provider選択、フェイルオーバー動作については [Image Generation](/ja-JP/tools/image-generation) を参照してください。

## 動画生成

バンドルされた `openai` pluginは、共有
`video_generate` tool経由の動画生成も登録します。

- デフォルト動画model: `openai/sora-2`
- モード: text-to-video、image-to-video、および単一動画の参照/編集フロー
- 現在の上限: 画像1枚または動画1本の参照入力
- 現在のOpenAI固有の注意点: OpenClawは現在、ネイティブOpenAI動画生成に対して `size`
  の上書きだけを転送します。`aspectRatio`、`resolution`、`audio`、`watermark` などの未対応の任意上書きは無視され、
  tool warningとして返されます。

OpenAIをデフォルトの動画providerとして使うには:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "openai/sora-2",
      },
    },
  },
}
```

共有toolの
パラメータ、provider選択、フェイルオーバー動作については [Video Generation](/ja-JP/tools/video-generation) を参照してください。

## Option B: OpenAI Code（Codex）サブスクリプション

**最適な用途:** API keyの代わりにChatGPT/Codexサブスクリプションアクセスを使うこと。
Codex cloudではChatGPT sign-inが必要であり、Codex CLIはChatGPTまたはAPI keyによるsign-inをサポートします。

ルート概要:

- `openai-codex/gpt-5.4` = ChatGPT/Codex OAuthルート
- 直接のOpenAI Platform API keyではなく、ChatGPT/Codex sign-inを使用
- `openai-codex/*` に対するprovider側の制限は、ChatGPT web/app体験とは異なる場合があります

### CLIセットアップ（Codex OAuth）

```bash
# ウィザードでCodex OAuthを実行
openclaw onboard --auth-choice openai-codex

# またはOAuthを直接実行
openclaw models auth login --provider openai-codex
```

### 設定スニペット（Codexサブスクリプション）

```json5
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
}
```

OpenAIの現在のCodexドキュメントでは、現在のCodex modelとして `gpt-5.4` が挙げられています。OpenClawは
これを、ChatGPT/Codex OAuth利用向けに `openai-codex/gpt-5.4` へマップします。

このルートは `openai/gpt-5.4` とは意図的に分離されています。直接の
OpenAI Platform APIパスを使いたい場合は、API key付きの `openai/*` を使ってください。ChatGPT/Codex sign-inを使いたい場合は、`openai-codex/*` を使ってください。

オンボーディングが既存のCodex CLIログインを再利用する場合、それらの認証情報は
引き続きCodex CLIによって管理されます。有効期限切れ時には、OpenClawはまず外部のCodexソースを再読み込みし、
providerがそれを更新できる場合は、OpenClaw専用の別コピーとして所有権を持つのではなく、
更新後の認証情報をCodexストレージへ書き戻します。

Codex Sparkを利用できるCodexアカウントなら、OpenClawは次もサポートします:

- `openai-codex/gpt-5.3-codex-spark`

OpenClawはCodex SparkをCodex専用として扱います。直接の
`openai/gpt-5.3-codex-spark` API-keyパスは公開しません。

OpenClawは、`pi-ai`
がそれを発見した場合にも `openai-codex/gpt-5.3-codex-spark` を保持します。これは権限依存かつ実験的なものとして扱ってください。Codex Sparkは
GPT-5.4 `/fast` とは別物であり、利用可否はサインインしているCodex /
ChatGPTアカウントに依存します。

### Codexコンテキストウィンドウ上限

OpenClawは、Codex model metadataと実行時コンテキスト上限を別の
値として扱います。

`openai-codex/gpt-5.4` では:

- ネイティブ `contextWindow`: `1050000`
- デフォルトの実行時 `contextTokens` 上限: `272000`

これにより、model metadataの正確性を保ちつつ、実運用ではレイテンシと品質特性が
より良い、より小さなデフォルト実行時ウィンドウを維持します。

別の実効上限を使いたい場合は、`models.providers.<provider>.models[].contextTokens` を設定してください:

```json5
{
  models: {
    providers: {
      "openai-codex": {
        models: [
          {
            id: "gpt-5.4",
            contextTokens: 160000,
          },
        ],
      },
    },
  },
}
```

`contextWindow` は、ネイティブmodel
metadataを宣言または上書きするときにのみ使ってください。実行時コンテキスト予算を制限したい場合は `contextTokens` を使ってください。

### デフォルトtransport

OpenClawはmodel streamingに `pi-ai` を使用します。`openai/*` と
`openai-codex/*` の両方で、デフォルトtransportは `"auto"`（WebSocket優先、その後
SSEフォールバック）です。

`"auto"` モードでは、OpenClawは初期の再試行可能なWebSocket失敗を1回だけ再試行してから
SSEにフォールバックします。強制 `"websocket"` モードでは、フォールバックの裏に隠さず
transport errorをそのまま表示します。

`"auto"` モードで接続時または初期ターンのWebSocket失敗が発生すると、OpenClawは
そのsessionのWebSocketパスを約60秒間degradedとしてマークし、
そのcool-down中の後続ターンは、transport間を行き来させる代わりにSSEで送信します。

ネイティブOpenAI系endpoint（`openai/*`、`openai-codex/*`、およびAzure
OpenAI Responses）では、OpenClawはリクエストに安定したsessionおよびturn identity stateも付与するため、
再試行、再接続、SSEフォールバックが同じ
conversation identityに揃ったまま維持されます。ネイティブOpenAI系ルートでは、これには安定した
session/turn request identity headerと、それに対応するtransport metadataが含まれます。

OpenClawはまた、OpenAI usage counterをtransport variant間で正規化してから
session/status surfaceに渡します。ネイティブOpenAI/Codex Responsesトラフィックは
usageを `input_tokens` / `output_tokens` または
`prompt_tokens` / `completion_tokens` のいずれかで報告する場合がありますが、
OpenClawはそれらを `/status`、`/usage`、session logs向けに同じ入力
および出力counterとして扱います。ネイティブ
WebSocketトラフィックで `total_tokens` が欠落している（または `0` と報告される）場合、OpenClawは
正規化された入力 + 出力合計にフォールバックするため、session/status表示は値が入ったままになります。

`agents.defaults.models.<provider/model>.params.transport` を設定できます:

- `"sse"`: SSEを強制
- `"websocket"`: WebSocketを強制
- `"auto"`: WebSocketを試し、その後SSEにフォールバック

`openai/*`（Responses API）については、OpenClawは
WebSocket transportが使われる場合に、デフォルトでWebSocket warm-upも有効にします（`openaiWsWarmup: true`）。

関連するOpenAIドキュメント:

- [Realtime API with WebSocket](https://platform.openai.com/docs/guides/realtime-websocket)
- [Streaming API responses (SSE)](https://platform.openai.com/docs/guides/streaming-responses)

```json5
{
  agents: {
    defaults: {
      model: { primary: "openai-codex/gpt-5.4" },
      models: {
        "openai-codex/gpt-5.4": {
          params: {
            transport: "auto",
          },
        },
      },
    },
  },
}
```

### OpenAI WebSocket warm-up

OpenAIのドキュメントではwarm-upは任意とされています。OpenClawでは、
WebSocket transport使用時の初回ターンのレイテンシを下げるため、`openai/*` に対してデフォルトで有効にしています。

### warm-upを無効にする

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            openaiWsWarmup: false,
          },
        },
      },
    },
  },
}
```

### warm-upを明示的に有効にする

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            openaiWsWarmup: true,
          },
        },
      },
    },
  },
}
```

### OpenAIとCodexのpriority processing

OpenAIのAPIは `service_tier=priority` によるpriority processingを公開しています。
OpenClawでは、ネイティブOpenAI/Codex Responses endpointにそのフィールドを渡すために
`agents.defaults.models["<provider>/<model>"].params.serviceTier`
を設定します。

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            serviceTier: "priority",
          },
        },
        "openai-codex/gpt-5.4": {
          params: {
            serviceTier: "priority",
          },
        },
      },
    },
  },
}
```

サポートされる値は `auto`、`default`、`flex`、`priority` です。

OpenClawは、ネイティブOpenAI/Codex endpointを指している場合、
`params.serviceTier` を直接の `openai/*` Responses
リクエストと `openai-codex/*` Codex Responsesリクエストの両方へ転送します。

重要な動作:

- 直接の `openai/*` は `api.openai.com` を対象にしている必要があります
- `openai-codex/*` は `chatgpt.com/backend-api` を対象にしている必要があります
- いずれかのproviderを別のbase URLまたはproxy経由にした場合、OpenClawは `service_tier` をそのままにします

### OpenAI fast mode

OpenClawは、`openai/*` と
`openai-codex/*` の両session向けに共有fast-modeトグルを公開しています:

- Chat/UI: `/fast status|on|off`
- Config: `agents.defaults.models["<provider>/<model>"].params.fastMode`

fast modeが有効なとき、OpenClawはそれをOpenAI priority processingへマップします:

- `api.openai.com` への直接の `openai/*` Responses呼び出しは `service_tier = "priority"` を送信します
- `chatgpt.com/backend-api` への `openai-codex/*` Responses呼び出しも `service_tier = "priority"` を送信します
- 既存のペイロード `service_tier` 値は保持されます
- fast modeは `reasoning` や `text.verbosity` を書き換えません

特にGPT 5.4では、最も一般的な設定は次のとおりです:

- `openai/gpt-5.4` または `openai-codex/gpt-5.4` を使っているsessionで `/fast on` を送る
- または `agents.defaults.models["openai/gpt-5.4"].params.fastMode = true` を設定する
- Codex OAuthも使うなら、`agents.defaults.models["openai-codex/gpt-5.4"].params.fastMode = true` も設定する

例:

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            fastMode: true,
          },
        },
        "openai-codex/gpt-5.4": {
          params: {
            fastMode: true,
          },
        },
      },
    },
  },
}
```

session overrideはconfigより優先されます。Sessions UIでsession overrideをクリアすると、
そのsessionは設定済みデフォルトに戻ります。

### ネイティブOpenAIとOpenAI互換ルートの違い

OpenClawは、直接のOpenAI、Codex、およびAzure OpenAI endpointを、
汎用的なOpenAI互換 `/v1` proxyとは異なるものとして扱います:

- ネイティブ `openai/*`、`openai-codex/*`、およびAzure OpenAIルートでは、
  reasoningを明示的に無効にした場合でも `reasoning: { effort: "none" }` をそのまま維持します
- ネイティブOpenAI系ルートではtool schemaがデフォルトでstrict modeになります
- 隠しOpenClaw attribution header（`originator`、`version`、および
  `User-Agent`）は、検証済みのネイティブOpenAI host
  （`api.openai.com`）とネイティブCodex host（`chatgpt.com/backend-api`）でのみ付与されます
- ネイティブOpenAI/Codexルートでは、
  `service_tier`、Responses `store`、OpenAI reasoning互換ペイロード、
  prompt-cache hintのようなOpenAI専用request shapingを維持します
- proxy形式のOpenAI互換ルートでは、より緩い互換動作を維持し、
  strictなtool schema、ネイティブ専用request shaping、隠し
  OpenAI/Codex attribution headerは強制しません

Azure OpenAIはtransportと互換動作の点ではネイティブルーティング側に残りますが、
隠しOpenAI/Codex attribution headerは受け取りません。

これにより、現在のネイティブOpenAI Responses動作を維持しつつ、
古いOpenAI互換shimをサードパーティの `/v1` backendへ強制しないようにしています。

### OpenAI Responsesのサーバー側compaction

直接のOpenAI Responses model（`api: "openai-responses"` を使い、
`baseUrl` が `api.openai.com` 上にある `openai/*`）では、OpenClawは現在、
OpenAIのサーバー側compaction payload hintを自動有効化します:

- `store: true` を強制（model compatが `supportsStore: false` を設定していない限り）
- `context_management: [{ type: "compaction", compact_threshold: ... }]` を注入

デフォルトでは、`compact_threshold` はmodel `contextWindow` の `70%` です（利用不可時は `80000`）。

### サーバー側compactionを明示的に有効にする

互換性のあるResponses model（たとえばAzure OpenAI Responses）で
`context_management` 注入を強制したい場合に使用します:

```json5
{
  agents: {
    defaults: {
      models: {
        "azure-openai-responses/gpt-5.4": {
          params: {
            responsesServerCompaction: true,
          },
        },
      },
    },
  },
}
```

### カスタムしきい値で有効にする

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            responsesServerCompaction: true,
            responsesCompactThreshold: 120000,
          },
        },
      },
    },
  },
}
```

### サーバー側compactionを無効にする

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            responsesServerCompaction: false,
          },
        },
      },
    },
  },
}
```

`responsesServerCompaction` が制御するのは `context_management` 注入だけです。
直接のOpenAI Responses modelでは、compatが
`supportsStore: false` を設定していない限り、引き続き `store: true` を強制します。

## 注意

- Model refは常に `provider/model` を使います（[/concepts/models](/ja-JP/concepts/models) を参照）。
- 認証の詳細と再利用ルールは [/concepts/oauth](/ja-JP/concepts/oauth) にあります。
