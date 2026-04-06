---
read_when:
    - memory search providerまたはembedding modelを設定したいとき
    - QMDバックエンドを設定したいとき
    - ハイブリッド検索、MMR、または時間減衰を調整したいとき
    - マルチモーダルmemory indexingを有効にしたいとき
summary: memory search、埋め込みprovider、QMD、ハイブリッド検索、マルチモーダルインデックスのすべての設定ノブ
title: Memory設定リファレンス
x-i18n:
    generated_at: "2026-04-06T03:13:09Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0de0b85125443584f4e575cf673ca8d9bd12ecd849d73c537f4a17545afa93fd
    source_path: reference/memory-config.md
    workflow: 15
---

# Memory設定リファレンス

このページでは、OpenClawのmemory searchに関するすべての設定ノブを一覧にしています。概念的な概要については、次を参照してください。

- [Memory Overview](/ja-JP/concepts/memory) -- memoryの仕組み
- [Builtin Engine](/ja-JP/concepts/memory-builtin) -- デフォルトのSQLiteバックエンド
- [QMD Engine](/ja-JP/concepts/memory-qmd) -- ローカルファーストのサイドカー
- [Memory Search](/ja-JP/concepts/memory-search) -- 検索パイプラインとチューニング

特記がない限り、memory search設定はすべて `openclaw.json` の
`agents.defaults.memorySearch` 配下にあります。

---

## Provider選択

| Key        | Type      | Default          | 説明 |
| ---------- | --------- | ---------------- | ---- |
| `provider` | `string`  | auto-detected    | EmbeddingアダプターID: `openai`, `gemini`, `voyage`, `mistral`, `bedrock`, `ollama`, `local` |
| `model`    | `string`  | provider default | Embedding model名 |
| `fallback` | `string`  | `"none"`         | プライマリ失敗時のフォールバックアダプターID |
| `enabled`  | `boolean` | `true`           | memory searchの有効/無効 |

### 自動検出順序

`provider` が設定されていない場合、OpenClawは最初に利用可能なものを選択します。

1. `local` -- `memorySearch.local.modelPath` が設定され、ファイルが存在する場合。
2. `openai` -- OpenAIキーを解決できる場合。
3. `gemini` -- Geminiキーを解決できる場合。
4. `voyage` -- Voyageキーを解決できる場合。
5. `mistral` -- Mistralキーを解決できる場合。
6. `bedrock` -- AWS SDK credential chain が解決できる場合（インスタンスロール、access keys、profile、SSO、web identity、またはshared config）。

`ollama` はサポートされていますが自動検出はされません（明示的に設定してください）。

### APIキー解決

リモートembeddingにはAPIキーが必要です。代わりにBedrockはAWS SDK default
credential chain を使用します（インスタンスロール、SSO、access keys）。

| Provider | Env var                        | Config key                        |
| -------- | ------------------------------ | --------------------------------- |
| OpenAI   | `OPENAI_API_KEY`               | `models.providers.openai.apiKey`  |
| Gemini   | `GEMINI_API_KEY`               | `models.providers.google.apiKey`  |
| Voyage   | `VOYAGE_API_KEY`               | `models.providers.voyage.apiKey`  |
| Mistral  | `MISTRAL_API_KEY`              | `models.providers.mistral.apiKey` |
| Bedrock  | AWS credential chain           | APIキー不要 |
| Ollama   | `OLLAMA_API_KEY` (placeholder) | --                                |

Codex OAuth は chat/completions のみを対象としており、embedding
request は満たしません。

---

## リモートエンドポイント設定

カスタムOpenAI互換エンドポイント、またはproviderデフォルトを上書きする場合:

| Key              | Type     | 説明 |
| ---------------- | -------- | ---- |
| `remote.baseUrl` | `string` | カスタムAPI base URL |
| `remote.apiKey`  | `string` | APIキーを上書き |
| `remote.headers` | `object` | 追加のHTTPヘッダー（providerデフォルトとマージ） |

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "openai",
        model: "text-embedding-3-small",
        remote: {
          baseUrl: "https://api.example.com/v1/",
          apiKey: "YOUR_KEY",
        },
      },
    },
  },
}
```

---

## Gemini固有設定

| Key                    | Type     | Default                | 説明 |
| ---------------------- | -------- | ---------------------- | ---- |
| `model`                | `string` | `gemini-embedding-001` | `gemini-embedding-2-preview` もサポート |
| `outputDimensionality` | `number` | `3072`                 | Embedding 2では 768、1536、または 3072 |

<Warning>
model または `outputDimensionality` を変更すると、自動的に完全再インデックスが実行されます。
</Warning>

---

## Bedrock embedding設定

BedrockはAWS SDK default credential chain を使用します -- APIキーは不要です。
Bedrockが有効なインスタンスロールを持つEC2上でOpenClawを実行している場合は、
provider と model を設定するだけです。

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "bedrock",
        model: "amazon.titan-embed-text-v2:0",
      },
    },
  },
}
```

| Key                    | Type     | Default                        | 説明 |
| ---------------------- | -------- | ------------------------------ | ---- |
| `model`                | `string` | `amazon.titan-embed-text-v2:0` | 任意のBedrock embedding model ID |
| `outputDimensionality` | `number` | model default                  | Titan V2では 256、512、または 1024 |

### サポートされるモデル

次のモデルがサポートされています（ファミリー検出および次元デフォルト付き）。

| Model ID                                   | Provider   | Default Dims | 設定可能なDims |
| ------------------------------------------ | ---------- | ------------ | -------------------- |
| `amazon.titan-embed-text-v2:0`             | Amazon     | 1024         | 256, 512, 1024       |
| `amazon.titan-embed-text-v1`               | Amazon     | 1536         | --                   |
| `amazon.titan-embed-g1-text-02`            | Amazon     | 1536         | --                   |
| `amazon.titan-embed-image-v1`              | Amazon     | 1024         | --                   |
| `amazon.nova-2-multimodal-embeddings-v1:0` | Amazon     | 1024         | 256, 384, 1024, 3072 |
| `cohere.embed-english-v3`                  | Cohere     | 1024         | --                   |
| `cohere.embed-multilingual-v3`             | Cohere     | 1024         | --                   |
| `cohere.embed-v4:0`                        | Cohere     | 1536         | 256-1536             |
| `twelvelabs.marengo-embed-3-0-v1:0`        | TwelveLabs | 512          | --                   |
| `twelvelabs.marengo-embed-2-7-v1:0`        | TwelveLabs | 1024         | --                   |

スループット接尾辞付きバリアント（例: `amazon.titan-embed-text-v1:2:8k`）は、
ベースモデルの設定を継承します。

### 認証

Bedrock認証は標準のAWS SDK資格情報解決順序を使用します。

1. 環境変数（`AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`）
2. SSOトークンキャッシュ
3. Web identity token 資格情報
4. Shared credentials と config ファイル
5. ECSまたはEC2メタデータ資格情報

リージョンは `AWS_REGION`、`AWS_DEFAULT_REGION`、`amazon-bedrock`
provider の `baseUrl` から解決され、なければ `us-east-1` が使われます。

### IAM権限

IAMロールまたはユーザーには次が必要です。

```json
{
  "Effect": "Allow",
  "Action": "bedrock:InvokeModel",
  "Resource": "*"
}
```

最小権限にするには、`InvokeModel` を特定modelに限定してください。

```
arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v2:0
```

---

## ローカルembedding設定

| Key                   | Type     | Default                | 説明 |
| --------------------- | -------- | ---------------------- | ---- |
| `local.modelPath`     | `string` | auto-downloaded        | GGUF modelファイルへのパス |
| `local.modelCacheDir` | `string` | node-llama-cpp default | ダウンロード済みmodelのキャッシュディレクトリ |

デフォルトmodel: `embeddinggemma-300m-qat-Q8_0.gguf`（約0.6 GB、自動ダウンロード）。
ネイティブビルドが必要です: `pnpm approve-builds` の後に `pnpm rebuild node-llama-cpp`。

---

## ハイブリッド検索設定

すべて `memorySearch.query.hybrid` 配下です。

| Key                   | Type      | Default | 説明 |
| --------------------- | --------- | ------- | ---- |
| `enabled`             | `boolean` | `true`  | ハイブリッドBM25 + ベクトル検索を有効化 |
| `vectorWeight`        | `number`  | `0.7`   | ベクトルスコアの重み（0-1） |
| `textWeight`          | `number`  | `0.3`   | BM25スコアの重み（0-1） |
| `candidateMultiplier` | `number`  | `4`     | 候補プールサイズの倍率 |

### MMR（多様性）

| Key           | Type      | Default | 説明 |
| ------------- | --------- | ------- | ---- |
| `mmr.enabled` | `boolean` | `false` | MMR再ランキングを有効化 |
| `mmr.lambda`  | `number`  | `0.7`   | 0 = 最大多様性、1 = 最大関連性 |

### 時間減衰（新しさ）

| Key                          | Type      | Default | 説明 |
| ---------------------------- | --------- | ------- | ---- |
| `temporalDecay.enabled`      | `boolean` | `false` | 新しさブーストを有効化 |
| `temporalDecay.halfLifeDays` | `number`  | `30`    | N日ごとにスコアが半減 |

常設ファイル（`MEMORY.md`、`memory/` 内の非日付ファイル）は減衰しません。

### 完全な例

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        query: {
          hybrid: {
            vectorWeight: 0.7,
            textWeight: 0.3,
            mmr: { enabled: true, lambda: 0.7 },
            temporalDecay: { enabled: true, halfLifeDays: 30 },
          },
        },
      },
    },
  },
}
```

---

## 追加のmemoryパス

| Key          | Type       | 説明 |
| ------------ | ---------- | ---- |
| `extraPaths` | `string[]` | インデックス対象にする追加ディレクトリまたはファイル |

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        extraPaths: ["../team-docs", "/srv/shared-notes"],
      },
    },
  },
}
```

パスは絶対パスまたはworkspace相対パスを指定できます。ディレクトリは
`.md` ファイルを再帰的に走査します。symlinkの扱いは有効なバックエンドに依存します。
builtin engine はsymlinkを無視し、QMDは基盤となるQMD
scannerの動作に従います。

エージェントスコープのクロスエージェントtranscript検索には、
`memory.qmd.paths` の代わりに
`agents.list[].memorySearch.qmd.extraCollections` を使用してください。
これらの追加コレクションは同じ `{ path, name, pattern? }` 形式に従いますが、
エージェントごとにマージされ、パスが現在のworkspace外を指している場合でも明示的な共有名を保持できます。
同じ解決済みパスが `memory.qmd.paths` と
`memorySearch.qmd.extraCollections` の両方に存在する場合、
QMDは最初のエントリを保持し、重複をスキップします。

---

## マルチモーダルmemory（Gemini）

Gemini Embedding 2を使用して、Markdownと一緒に画像と音声をインデックスします。

| Key                       | Type       | Default    | 説明 |
| ------------------------- | ---------- | ---------- | ---- |
| `multimodal.enabled`      | `boolean`  | `false`    | マルチモーダルインデックスを有効化 |
| `multimodal.modalities`   | `string[]` | --         | `["image"]`, `["audio"]`, または `["all"]` |
| `multimodal.maxFileBytes` | `number`   | `10000000` | インデックス対象の最大ファイルサイズ |

`extraPaths` 内のファイルにのみ適用されます。デフォルトのmemoryルートはMarkdownのみのままです。
`gemini-embedding-2-preview` が必要です。`fallback` は `"none"` でなければなりません。

サポート形式: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.heic`, `.heif`
（画像）、`.mp3`, `.wav`, `.ogg`, `.opus`, `.m4a`, `.aac`, `.flac`（音声）。

---

## Embeddingキャッシュ

| Key                | Type      | Default | 説明 |
| ------------------ | --------- | ------- | ---- |
| `cache.enabled`    | `boolean` | `false` | SQLiteにchunk embeddingをキャッシュ |
| `cache.maxEntries` | `number`  | `50000` | embeddingの最大キャッシュ件数 |

再インデックスやtranscript更新時に、変更されていないテキストの再embeddingを防ぎます。

---

## バッチインデックス

| Key                           | Type      | Default | 説明 |
| ----------------------------- | --------- | ------- | ---- |
| `remote.batch.enabled`        | `boolean` | `false` | バッチembedding APIを有効化 |
| `remote.batch.concurrency`    | `number`  | `2`     | 並列バッチジョブ数 |
| `remote.batch.wait`           | `boolean` | `true`  | バッチ完了を待機 |
| `remote.batch.pollIntervalMs` | `number`  | --      | ポーリング間隔 |
| `remote.batch.timeoutMinutes` | `number`  | --      | バッチタイムアウト |

`openai`、`gemini`、`voyage` で利用できます。OpenAI batch は通常、
大規模バックフィルで最も高速かつ低コストです。

---

## セッションmemory search（実験的）

セッションtranscriptをインデックスし、`memory_search` 経由で参照できるようにします。

| Key                           | Type       | Default      | 説明 |
| ----------------------------- | ---------- | ------------ | ---- |
| `experimental.sessionMemory`  | `boolean`  | `false`      | セッションインデックスを有効化 |
| `sources`                     | `string[]` | `["memory"]` | transcriptを含めるには `"sessions"` を追加 |
| `sync.sessions.deltaBytes`    | `number`   | `100000`     | 再インデックスのバイト閾値 |
| `sync.sessions.deltaMessages` | `number`   | `50`         | 再インデックスのメッセージ閾値 |

セッションインデックスはオプトインで、非同期に実行されます。結果はわずかに
古い場合があります。セッションログはディスク上にあるため、ファイルシステムアクセスを信頼境界として扱ってください。

---

## SQLiteベクトル高速化（sqlite-vec）

| Key                          | Type      | Default | 説明 |
| ---------------------------- | --------- | ------- | ---- |
| `store.vector.enabled`       | `boolean` | `true`  | ベクトルクエリにsqlite-vecを使用 |
| `store.vector.extensionPath` | `string`  | bundled | sqlite-vecパスを上書き |

sqlite-vec が利用できない場合、OpenClawは自動的にインプロセスの
コサイン類似度へフォールバックします。

---

## インデックス保存先

| Key                   | Type     | Default                               | 説明 |
| --------------------- | -------- | ------------------------------------- | ---- |
| `store.path`          | `string` | `~/.openclaw/memory/{agentId}.sqlite` | インデックス保存場所（`{agentId}` トークン対応） |
| `store.fts.tokenizer` | `string` | `unicode61`                           | FTS5 tokenizer（`unicode61` または `trigram`） |

---

## QMDバックエンド設定

有効にするには `memory.backend = "qmd"` を設定します。QMD設定はすべて
`memory.qmd` 配下にあります。

| Key                      | Type      | Default  | 説明 |
| ------------------------ | --------- | -------- | ---- |
| `command`                | `string`  | `qmd`    | QMD実行ファイルパス |
| `searchMode`             | `string`  | `search` | 検索コマンド: `search`, `vsearch`, `query` |
| `includeDefaultMemory`   | `boolean` | `true`   | `MEMORY.md` + `memory/**/*.md` を自動インデックス |
| `paths[]`                | `array`   | --       | 追加パス: `{ name, path, pattern? }` |
| `sessions.enabled`       | `boolean` | `false`  | セッションtranscriptをインデックス |
| `sessions.retentionDays` | `number`  | --       | transcript保持期間 |
| `sessions.exportDir`     | `string`  | --       | エクスポートディレクトリ |

OpenClawは、現在のQMD collection とMCP query 形式を優先しますが、
必要に応じてレガシーな `--mask` collection フラグと古いMCP tool名にフォールバックすることで、
古いQMDリリースも動作し続けるようにしています。

QMD model上書きはOpenClaw config ではなくQMD側に保持されます。QMDのmodelを
グローバルに上書きしたい場合は、
Gatewayランタイム環境で `QMD_EMBED_MODEL`、`QMD_RERANK_MODEL`、`QMD_GENERATE_MODEL`
のような環境変数を設定してください。

### 更新スケジュール

| Key                       | Type      | Default | 説明 |
| ------------------------- | --------- | ------- | ---- |
| `update.interval`         | `string`  | `5m`    | 更新間隔 |
| `update.debounceMs`       | `number`  | `15000` | ファイル変更のデバウンス |
| `update.onBoot`           | `boolean` | `true`  | 起動時に更新 |
| `update.waitForBootSync`  | `boolean` | `false` | 更新完了まで起動をブロック |
| `update.embedInterval`    | `string`  | --      | embedding専用の更新間隔 |
| `update.commandTimeoutMs` | `number`  | --      | QMDコマンドのタイムアウト |
| `update.updateTimeoutMs`  | `number`  | --      | QMD update操作のタイムアウト |
| `update.embedTimeoutMs`   | `number`  | --      | QMD embed操作のタイムアウト |

### 制限

| Key                       | Type     | Default | 説明 |
| ------------------------- | -------- | ------- | ---- |
| `limits.maxResults`       | `number` | `6`     | 最大検索結果数 |
| `limits.maxSnippetChars`  | `number` | --      | スニペット長を制限 |
| `limits.maxInjectedChars` | `number` | --      | 注入される総文字数を制限 |
| `limits.timeoutMs`        | `number` | `4000`  | 検索タイムアウト |

### スコープ

どのセッションがQMD検索結果を受け取れるかを制御します。スキーマは
[`session.sendPolicy`](/ja-JP/gateway/configuration-reference#session) と同じです。

```json5
{
  memory: {
    qmd: {
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }],
      },
    },
  },
}
```

デフォルトはDMのみです。`match.keyPrefix` は正規化されたsession key に一致し、
`match.rawKeyPrefix` は `agent:<id>:` を含む生のkey に一致します。

### Citations

`memory.citations` はすべてのバックエンドに適用されます。

| Value            | 動作 |
| ---------------- | --------------------------------------------------- |
| `auto` (default) | スニペットに `Source: <path#line>` フッターを含める |
| `on`             | 常にフッターを含める |
| `off`            | フッターを省略する（パスは引き続き内部的にエージェントへ渡される） |

### 完全なQMD例

```json5
{
  memory: {
    backend: "qmd",
    citations: "auto",
    qmd: {
      includeDefaultMemory: true,
      update: { interval: "5m", debounceMs: 15000 },
      limits: { maxResults: 6, timeoutMs: 4000 },
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }],
      },
      paths: [{ name: "docs", path: "~/notes", pattern: "**/*.md" }],
    },
  },
}
```

---

## Dreaming（実験的）

Dreamingは `agents.defaults.memorySearch` 配下ではなく、
`plugins.entries.memory-core.config.dreaming` 配下で設定します。

Dreamingは1回のスケジュールされたスイープとして実行され、内部のlight/deep/REMフェーズは
実装の詳細として扱われます。

概念的な動作とスラッシュコマンドについては、[Dreaming](/concepts/dreaming) を参照してください。

### ユーザー設定

| Key         | Type      | Default     | 説明 |
| ----------- | --------- | ----------- | ---- |
| `enabled`   | `boolean` | `false`     | Dreaming全体を有効または無効にする |
| `frequency` | `string`  | `0 3 * * *` | 完全なDreamingスイープの任意のcron頻度 |

### 例

```json5
{
  plugins: {
    entries: {
      "memory-core": {
        config: {
          dreaming: {
            enabled: true,
            frequency: "0 3 * * *",
          },
        },
      },
    },
  },
}
```

メモ:

- Dreamingはマシン状態を `memory/.dreams/` に書き込みます。
- Dreamingは人が読める物語出力を `DREAMS.md`（または既存の `dreams.md`）に書き込みます。
- light/deep/REMフェーズのポリシーと閾値は内部動作であり、ユーザー向けconfigではありません。
