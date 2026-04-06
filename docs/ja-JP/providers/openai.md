---
read_when:
    - OpenClaw で OpenAI モデルを使いたい場合
    - API キーではなく Codex サブスクリプション認証を使いたい場合
summary: OpenClaw で API キーまたは Codex サブスクリプション経由で OpenAI を使う
title: OpenAI
x-i18n:
    generated_at: "2026-04-06T03:12:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9e04db5787f6ed7b1eda04d965c10febae10809fc82ae4d9769e7163234471f5
    source_path: providers/openai.md
    workflow: 15
---

# OpenAI

OpenAI は GPT モデル向けの開発者 API を提供しています。Codex は、サブスクリプションアクセス向けの **ChatGPT サインイン**、または従量課金アクセス向けの **API キー** サインインに対応しています。Codex cloud では ChatGPT サインインが必要です。
OpenAI は、OpenClaw のような外部ツール/ワークフローでのサブスクリプション OAuth 利用を明示的にサポートしています。

## デフォルトの対話スタイル

OpenClaw は、`openai/*` と
`openai-codex/*` の両方の実行に対して、小さな OpenAI 固有のプロンプトオーバーレイを追加できます。デフォルトでは、このオーバーレイは assistant を適度に活性化し、
協調的で、簡潔で、直接的で、少し感情表現豊かに保ちつつ、
ベースの OpenClaw システムプロンプトは置き換えません。このフレンドリーなオーバーレイでは、自然に合う場合に限って時折絵文字も許可されますが、全体としては簡潔な出力を維持します。

設定キー:

`plugins.entries.openai.config.personality`

許可される値:

- `"friendly"`: デフォルト。OpenAI 固有のオーバーレイを有効にします。
- `"off"`: オーバーレイを無効にし、ベースの OpenClaw プロンプトのみを使います。

適用範囲:

- `openai/*` モデルに適用されます。
- `openai-codex/*` モデルに適用されます。
- 他の provider には影響しません。

この動作はデフォルトで有効です。将来のローカル設定変更でもこれを維持したい場合は、明示的に `"friendly"` を設定したままにしてください:

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

### OpenAI プロンプトオーバーレイを無効にする

変更されていないベースの OpenClaw プロンプトを使いたい場合は、オーバーレイを `"off"` に設定してください:

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

設定 CLI で直接設定することもできます:

```bash
openclaw config set plugins.entries.openai.config.personality off
```

## オプション A: OpenAI API キー（OpenAI Platform）

**最適な用途:** 直接 API アクセスと従量課金。
API キーは OpenAI ダッシュボードから取得してください。

### CLI セットアップ

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

OpenAI の現在の API モデルドキュメントでは、直接
OpenAI API 利用向けに `gpt-5.4` と `gpt-5.4-pro` が記載されています。OpenClaw はその両方を `openai/*` Responses パス経由で転送します。
OpenClaw は、古い `openai/gpt-5.3-codex-spark` 行を意図的に非表示にしています。これは直接 OpenAI API 呼び出しで本番トラフィック上拒否されるためです。

OpenClaw は、直接 OpenAI
API パスでは `openai/gpt-5.3-codex-spark` を公開しません。`pi-ai` にはそのモデルの組み込み行が依然として含まれていますが、現在の本番 OpenAI API
リクエストでは拒否されます。OpenClaw では Spark は Codex 専用として扱われます。

## 画像生成

バンドル `openai` plugin は、共有の
`image_generate` tool を通じて画像生成も登録します。

- デフォルト画像モデル: `openai/gpt-image-1`
- Generate: リクエストごとに最大 4 枚の画像
- Edit mode: 有効、最大 5 枚の参照画像
- `size` をサポート
- 現在の OpenAI 固有の注意点: OpenClaw は現在、`aspectRatio` または
  `resolution` の上書きを OpenAI Images API に転送しません

OpenAI をデフォルトの画像 provider として使うには:

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

共有 tool の
パラメーター、provider 選択、failover 動作については [Image Generation](/ja-JP/tools/image-generation) を参照してください。

## 動画生成

バンドル `openai` plugin は、共有の
`video_generate` tool を通じて動画生成も登録します。

- デフォルト動画モデル: `openai/sora-2`
- モード: text-to-video、image-to-video、単一動画参照/edit フロー
- 現在の制限: 画像または動画の参照入力は 1 つのみ
- 現在の OpenAI 固有の注意点: OpenClaw は現在、ネイティブ OpenAI 動画生成に対して `size`
  の上書きのみを転送します。`aspectRatio`、`resolution`、`audio`、`watermark` のような未対応の任意上書きは無視され、tool 警告として返されます。

OpenAI をデフォルトの動画 provider として使うには:

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

共有 tool の
パラメーター、provider 選択、failover 動作については [Video Generation](/tools/video-generation) を参照してください。

## オプション B: OpenAI Code（Codex）サブスクリプション

**最適な用途:** API キーの代わりに ChatGPT/Codex サブスクリプションアクセスを使う場合。
Codex cloud には ChatGPT サインインが必要ですが、Codex CLI は ChatGPT または API キーでのサインインに対応しています。

### CLI セットアップ（Codex OAuth）

```bash
# ウィザードで Codex OAuth を実行
openclaw onboard --auth-choice openai-codex

# または OAuth を直接実行
openclaw models auth login --provider openai-codex
```

### 設定スニペット（Codex サブスクリプション）

```json5
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
}
```

OpenAI の現在の Codex ドキュメントでは、現在の Codex モデルとして `gpt-5.4` が記載されています。OpenClaw
ではこれを ChatGPT/Codex OAuth 利用向けに `openai-codex/gpt-5.4` へマッピングしています。

オンボーディングで既存の Codex CLI ログインを再利用する場合、それらの認証情報は
Codex CLI によって引き続き管理されます。有効期限切れ時には、OpenClaw はまず外部の Codex ソースを再読み込みし、provider が更新可能な場合は、別の OpenClaw 専用コピーで所有権を持つのではなく、更新した認証情報を Codex ストレージへ書き戻します。

Codex アカウントに Codex Spark の利用権がある場合、OpenClaw は次にも対応します:

- `openai-codex/gpt-5.3-codex-spark`

OpenClaw は Codex Spark を Codex 専用として扱います。直接の
`openai/gpt-5.3-codex-spark` API キーパスは公開しません。

OpenClaw は、`pi-ai`
が `openai-codex/gpt-5.3-codex-spark` を検出した場合も、それを保持します。これは利用権依存かつ実験的なものとして扱ってください。Codex Spark は GPT-5.4 `/fast` とは別物であり、利用可否はサインインしている Codex /
ChatGPT アカウントに依存します。

### Codex コンテキストウィンドウ上限

OpenClaw は、Codex モデルメタデータと実行時コンテキスト上限を別の値として扱います。

`openai-codex/gpt-5.4` の場合:

- ネイティブ `contextWindow`: `1050000`
- デフォルトの実行時 `contextTokens` 上限: `272000`

これにより、モデルメタデータの正確性を保ちながら、実運用でより良いレイテンシと品質特性を持つ、より小さなデフォルト実行時ウィンドウを維持できます。

実効上限を変更したい場合は、`models.providers.<provider>.models[].contextTokens` を設定してください:

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

`contextWindow` は、ネイティブモデルメタデータを宣言または上書きするときにのみ使用してください。実行時コンテキスト予算を制限したい場合は `contextTokens` を使用してください。

### デフォルト transport

OpenClaw はモデルストリーミングに `pi-ai` を使用します。`openai/*` と
`openai-codex/*` の両方で、デフォルト transport は `"auto"`（WebSocket 優先、その後 SSE フォールバック）です。

`"auto"` モードでは、OpenClaw は SSE にフォールバックする前に、初期の再試行可能な WebSocket 失敗を 1 回だけ再試行します。強制 `"websocket"` モードでは、transport
エラーはフォールバックの背後に隠されず、直接表示されます。

`"auto"` モードで接続時またはターン初期の WebSocket 失敗が発生すると、OpenClaw はそのセッションの WebSocket パスを約 60 秒間劣化状態としてマークし、
transport 間で無駄に切り替え続ける代わりに、そのクールダウン中の後続ターンを SSE で送信します。

ネイティブ OpenAI 系 endpoint（`openai/*`、`openai-codex/*`、および Azure
OpenAI Responses）では、OpenClaw は安定したセッションおよびターン識別状態もリクエストに付加するため、再試行、再接続、SSE フォールバックが同じ会話識別子に揃えられたままになります。ネイティブ OpenAI 系ルートでは、これに安定したセッション/ターン request identity header と、一致する transport metadata が含まれます。

OpenClaw はまた、OpenAI の使用量カウンターを session/status surface に到達する前に transport バリアント間で正規化します。ネイティブ OpenAI/Codex Responses トラフィックは、使用量を `input_tokens` / `output_tokens` または
`prompt_tokens` / `completion_tokens` のどちらかで報告することがありますが、OpenClaw はこれらを `/status`、`/usage`、セッションログ向けに同じ入力/出力カウンターとして扱います。ネイティブ
WebSocket トラフィックが `total_tokens` を省略した場合（または `0` を報告した場合）、OpenClaw は正規化済みの入力 + 出力合計へフォールバックし、session/status 表示が空にならないようにします。

`agents.defaults.models.<provider/model>.params.transport` を設定できます:

- `"sse"`: SSE を強制
- `"websocket"`: WebSocket を強制
- `"auto"`: WebSocket を試してから SSE にフォールバック

`openai/*`（Responses API）では、OpenClaw は WebSocket transport 使用時に、
デフォルトで WebSocket warm-up（`openaiWsWarmup: true`）も有効にします。

関連する OpenAI ドキュメント:

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

OpenAI のドキュメントでは warm-up は任意とされています。OpenClaw は、
WebSocket transport 使用時の初回ターンのレイテンシを減らすため、
`openai/*` ではデフォルトでこれを有効にします。

### warm-up を無効にする

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

### warm-up を明示的に有効にする

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

### OpenAI と Codex の優先処理

OpenAI の API は `service_tier=priority` による優先処理を公開しています。OpenClaw
では、ネイティブ OpenAI/Codex Responses endpoint にそのフィールドを渡すには、
`agents.defaults.models["<provider>/<model>"].params.serviceTier` を設定します。

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

OpenClaw は `params.serviceTier` を、直接の `openai/*` Responses
リクエストと `openai-codex/*` Codex Responses リクエストの両方に転送します。ただし、それらのモデルがネイティブ OpenAI/Codex endpoint を指している場合に限ります。

重要な動作:

- 直接の `openai/*` は `api.openai.com` を対象にしている必要があります
- `openai-codex/*` は `chatgpt.com/backend-api` を対象にしている必要があります
- いずれかの provider を別の base URL または proxy 経由にした場合、OpenClaw は `service_tier` をそのままにします

### OpenAI fast mode

OpenClaw は、`openai/*` と
`openai-codex/*` セッションの両方に共通の fast-mode トグルを提供します:

- Chat/UI: `/fast status|on|off`
- 設定: `agents.defaults.models["<provider>/<model>"].params.fastMode`

fast mode が有効な場合、OpenClaw はそれを OpenAI の優先処理へマッピングします:

- `api.openai.com` への直接の `openai/*` Responses 呼び出しは `service_tier = "priority"` を送信します
- `chatgpt.com/backend-api` への `openai-codex/*` Responses 呼び出しも `service_tier = "priority"` を送信します
- 既存の payload `service_tier` 値は保持されます
- fast mode は `reasoning` や `text.verbosity` を書き換えません

特に GPT 5.4 では、最も一般的なセットアップは次のとおりです:

- `openai/gpt-5.4` または `openai-codex/gpt-5.4` を使うセッションで `/fast on` を送る
- または `agents.defaults.models["openai/gpt-5.4"].params.fastMode = true` を設定する
- Codex OAuth も使う場合は、`agents.defaults.models["openai-codex/gpt-5.4"].params.fastMode = true` も設定する

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

セッション上書きは設定より優先されます。Sessions UI でセッション上書きをクリアすると、そのセッションは設定済みデフォルトに戻ります。

### ネイティブ OpenAI と OpenAI 互換ルートの違い

OpenClaw は、直接の OpenAI、Codex、および Azure OpenAI endpoint を、
汎用の OpenAI 互換 `/v1` proxy とは異なるものとして扱います:

- ネイティブ `openai/*`、`openai-codex/*`、および Azure OpenAI ルートでは、
  reasoning を明示的に無効にした場合でも `reasoning: { effort: "none" }` をそのまま保持します
- ネイティブ OpenAI 系ルートでは tool schema をデフォルトで strict mode にします
- 非表示の OpenClaw attribution header（`originator`、`version`、および
  `User-Agent`）は、検証済みネイティブ OpenAI ホスト
  （`api.openai.com`）およびネイティブ Codex ホスト（`chatgpt.com/backend-api`）にのみ付加されます
- ネイティブ OpenAI/Codex ルートでは、`service_tier`、Responses `store`、OpenAI reasoning-compat payload、prompt-cache hint など、OpenAI 専用の request shaping を保持します
- proxy 形式の OpenAI 互換ルートでは、より緩い compat 動作を維持し、
  strict tool schema、ネイティブ専用 request shaping、または非表示の
  OpenAI/Codex attribution header を強制しません

Azure OpenAI は transport と compat 動作ではネイティブルーティングの区分に入りますが、非表示の OpenAI/Codex attribution header は受け取りません。

これにより、現在のネイティブ OpenAI Responses 動作を維持しつつ、
古い OpenAI 互換 shim をサードパーティ `/v1` バックエンドに強制しないようにしています。

### OpenAI Responses のサーバー側 compaction

直接の OpenAI Responses モデル（`api: "openai-responses"` を使う `openai/*` で、
`baseUrl` が `api.openai.com` の場合）では、OpenClaw は OpenAI のサーバー側
compaction payload hint を自動有効化します:

- `store: true` を強制します（model compat が `supportsStore: false` を設定していない限り）
- `context_management: [{ type: "compaction", compact_threshold: ... }]` を注入します

デフォルトでは、`compact_threshold` は model `contextWindow` の `70%`（利用できない場合は `80000`）です。

### サーバー側 compaction を明示的に有効にする

互換性のある Responses モデル（たとえば Azure OpenAI Responses）で
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

### サーバー側 compaction を無効にする

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

`responsesServerCompaction` は `context_management` 注入のみを制御します。
直接の OpenAI Responses モデルは、compat が
`supportsStore: false` を設定していない限り、引き続き `store: true` を強制します。

## 注意

- model ref は常に `provider/model` を使います（[/concepts/models](/ja-JP/concepts/models) を参照）。
- 認証の詳細 + 再利用ルールは [/concepts/oauth](/ja-JP/concepts/oauth) にあります。
