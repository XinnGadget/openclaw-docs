---
read_when:
    - メモリ検索プロバイダーまたは埋め込みモデルを設定したい場合
    - QMDバックエンドを設定したい場合
    - ハイブリッド検索、MMR、または時間減衰を調整したい場合
    - マルチモーダルメモリのインデックス作成を有効にしたい場合
summary: メモリ検索、埋め込みプロバイダー、QMD、ハイブリッド検索、マルチモーダルインデックス作成に関するすべての設定項目
title: メモリ設定リファレンス
x-i18n:
    generated_at: "2026-04-15T14:40:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: 334c3c4dac08e864487047d3822c75f96e9e7a97c38be4b4e0cd9e63c4489a53
    source_path: reference/memory-config.md
    workflow: 15
---

# メモリ設定リファレンス

このページでは、OpenClawのメモリ検索に関するすべての設定項目を一覧します。概念的な概要については、次を参照してください:

- [Memory Overview](/ja-JP/concepts/memory) -- メモリの仕組み
- [Builtin Engine](/ja-JP/concepts/memory-builtin) -- デフォルトのSQLiteバックエンド
- [QMD Engine](/ja-JP/concepts/memory-qmd) -- ローカルファーストのサイドカー
- [Memory Search](/ja-JP/concepts/memory-search) -- 検索パイプラインと調整
- [Active Memory](/ja-JP/concepts/active-memory) -- 対話型セッション向けにメモリサブエージェントを有効にする方法

特に注記がない限り、メモリ検索の設定はすべて`openclaw.json`の`agents.defaults.memorySearch`配下にあります。

**active memory**機能のトグルとサブエージェント設定を探している場合、それは`memorySearch`ではなく`plugins.entries.active-memory`配下にあります。

Active Memoryは2つのゲートモデルを使用します:

1. Pluginが有効化されており、現在のエージェントidを対象にしていること
2. リクエストが対象となる対話型の永続チャットセッションであること

有効化モデル、Plugin側の設定、トランスクリプトの永続化、安全なロールアウトパターンについては、[Active Memory](/ja-JP/concepts/active-memory)を参照してください。

---

## プロバイダーの選択

| Key        | Type      | Default          | 説明                                                                                                      |
| ---------- | --------- | ---------------- | --------------------------------------------------------------------------------------------------------- |
| `provider` | `string`  | 自動検出         | 埋め込みアダプターID: `bedrock`, `gemini`, `github-copilot`, `local`, `mistral`, `ollama`, `openai`, `voyage` |
| `model`    | `string`  | プロバイダーのデフォルト | 埋め込みモデル名                                                                                     |
| `fallback` | `string`  | `"none"`         | プライマリが失敗したときのフォールバックアダプターID                                                       |
| `enabled`  | `boolean` | `true`           | メモリ検索を有効または無効にする                                                                          |

### 自動検出の順序

`provider`が設定されていない場合、OpenClawは最初に利用可能なものを選択します:

1. `local` -- `memorySearch.local.modelPath`が設定されており、ファイルが存在する場合。
2. `github-copilot` -- GitHub Copilotトークンを解決できる場合（環境変数または認証プロファイル）。
3. `openai` -- OpenAIキーを解決できる場合。
4. `gemini` -- Geminiキーを解決できる場合。
5. `voyage` -- Voyageキーを解決できる場合。
6. `mistral` -- Mistralキーを解決できる場合。
7. `bedrock` -- AWS SDKの認証情報チェーンが解決される場合（インスタンスロール、アクセスキー、プロファイル、SSO、Web ID、または共有設定）。

`ollama`はサポートされていますが、自動検出はされません（明示的に設定してください）。

### APIキーの解決

リモート埋め込みにはAPIキーが必要です。代わりにBedrockはAWS SDKのデフォルト認証情報チェーンを使用します（インスタンスロール、SSO、アクセスキー）。

| Provider       | Env var                                            | Config key                        |
| -------------- | -------------------------------------------------- | --------------------------------- |
| Bedrock        | AWS認証情報チェーン                                 | APIキー不要                        |
| Gemini         | `GEMINI_API_KEY`                                   | `models.providers.google.apiKey`  |
| GitHub Copilot | `COPILOT_GITHUB_TOKEN`, `GH_TOKEN`, `GITHUB_TOKEN` | デバイスログイン経由の認証プロファイル |
| Mistral        | `MISTRAL_API_KEY`                                  | `models.providers.mistral.apiKey` |
| Ollama         | `OLLAMA_API_KEY` (プレースホルダー)                | --                                |
| OpenAI         | `OPENAI_API_KEY`                                   | `models.providers.openai.apiKey`  |
| Voyage         | `VOYAGE_API_KEY`                                   | `models.providers.voyage.apiKey`  |

Codex OAuthはチャット/補完のみを対象としており、埋め込みリクエストには対応しません。

---

## リモートエンドポイント設定

カスタムのOpenAI互換エンドポイントを使う場合や、プロバイダーのデフォルトを上書きする場合:

| Key              | Type     | 説明                                         |
| ---------------- | -------- | -------------------------------------------- |
| `remote.baseUrl` | `string` | カスタムAPIベースURL                         |
| `remote.apiKey`  | `string` | APIキーを上書き                              |
| `remote.headers` | `object` | 追加のHTTPヘッダー（プロバイダーのデフォルトとマージされる） |

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

## Gemini固有の設定

| Key                    | Type     | Default                | 説明                                       |
| ---------------------- | -------- | ---------------------- | ------------------------------------------ |
| `model`                | `string` | `gemini-embedding-001` | `gemini-embedding-2-preview`もサポート     |
| `outputDimensionality` | `number` | `3072`                 | Embedding 2では768、1536、3072を指定可能   |

<Warning>
`model`または`outputDimensionality`を変更すると、自動的に完全な再インデックスが実行されます。
</Warning>

---

## Bedrock埋め込み設定

BedrockはAWS SDKのデフォルト認証情報チェーンを使用します -- APIキーは不要です。
OpenClawがBedrock対応のインスタンスロールを持つEC2上で実行されている場合は、providerとmodelを設定するだけです:

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

| Key                    | Type     | Default                        | 説明                            |
| ---------------------- | -------- | ------------------------------ | ------------------------------- |
| `model`                | `string` | `amazon.titan-embed-text-v2:0` | 任意のBedrock埋め込みモデルID   |
| `outputDimensionality` | `number` | モデルのデフォルト             | Titan V2では256、512、1024      |

### サポートされているモデル

次のモデルがサポートされています（ファミリー検出と次元数デフォルトあり）:

| Model ID                                   | Provider   | Default Dims | Configurable Dims    |
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

スループット接尾辞付きのバリアント（例: `amazon.titan-embed-text-v1:2:8k`）は、ベースモデルの設定を継承します。

### 認証

Bedrock認証では、標準のAWS SDK認証情報解決順序を使用します:

1. 環境変数（`AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`）
2. SSOトークンキャッシュ
3. Web IDトークン認証情報
4. 共有認証情報ファイルと設定ファイル
5. ECSまたはEC2メタデータ認証情報

リージョンは`AWS_REGION`、`AWS_DEFAULT_REGION`、`amazon-bedrock`プロバイダーの`baseUrl`から解決され、どれもなければ`us-east-1`がデフォルトになります。

### IAM権限

IAMロールまたはユーザーには次が必要です:

```json
{
  "Effect": "Allow",
  "Action": "bedrock:InvokeModel",
  "Resource": "*"
}
```

最小権限にするには、`InvokeModel`の対象を特定のモデルに限定してください:

```
arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v2:0
```

---

## ローカル埋め込み設定

| Key                   | Type     | Default                | 説明                              |
| --------------------- | -------- | ---------------------- | --------------------------------- |
| `local.modelPath`     | `string` | 自動ダウンロード       | GGUFモデルファイルへのパス        |
| `local.modelCacheDir` | `string` | node-llama-cpp default | ダウンロードしたモデルのキャッシュディレクトリ |

デフォルトモデル: `embeddinggemma-300m-qat-Q8_0.gguf`（約0.6 GB、自動ダウンロード）。
ネイティブビルドが必要です: `pnpm approve-builds`の後に`pnpm rebuild node-llama-cpp`を実行してください。

---

## ハイブリッド検索設定

すべて`memorySearch.query.hybrid`配下です:

| Key                   | Type      | Default | 説明                               |
| --------------------- | --------- | ------- | ---------------------------------- |
| `enabled`             | `boolean` | `true`  | ハイブリッドBM25 + ベクトル検索を有効にする |
| `vectorWeight`        | `number`  | `0.7`   | ベクトルスコアの重み（0-1）        |
| `textWeight`          | `number`  | `0.3`   | BM25スコアの重み（0-1）            |
| `candidateMultiplier` | `number`  | `4`     | 候補プールサイズの倍率             |

### MMR（多様性）

| Key           | Type      | Default | 説明                                |
| ------------- | --------- | ------- | ----------------------------------- |
| `mmr.enabled` | `boolean` | `false` | MMR再ランキングを有効にする         |
| `mmr.lambda`  | `number`  | `0.7`   | 0 = 最大多様性、1 = 最大関連性      |

### Temporal decay（新しさ）

| Key                          | Type      | Default | 説明                        |
| ---------------------------- | --------- | ------- | --------------------------- |
| `temporalDecay.enabled`      | `boolean` | `false` | 新しさブーストを有効にする  |
| `temporalDecay.halfLifeDays` | `number`  | `30`    | N日ごとにスコアが半減する   |

エバーグリーンファイル（`MEMORY.md`、`memory/`内の日付なしファイル）は減衰されません。

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

## 追加のメモリパス

| Key          | Type       | 説明                                   |
| ------------ | ---------- | -------------------------------------- |
| `extraPaths` | `string[]` | インデックス対象に追加するディレクトリまたはファイル |

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

パスは絶対パスでもワークスペース相対でも指定できます。ディレクトリは`.md`ファイルを再帰的にスキャンします。シンボリックリンクの扱いはアクティブなバックエンドによって異なります。builtin engineはシンボリックリンクを無視し、QMDは基盤となるQMDスキャナーの動作に従います。

エージェント単位のクロスエージェントトランスクリプト検索には、`memory.qmd.paths`ではなく`agents.list[].memorySearch.qmd.extraCollections`を使用してください。これらの追加コレクションは同じ`{ path, name, pattern? }`の形に従いますが、エージェントごとにマージされ、パスが現在のワークスペース外を指している場合でも明示的な共有名を維持できます。
同じ解決済みパスが`memory.qmd.paths`と`memorySearch.qmd.extraCollections`の両方に現れる場合、QMDは最初のエントリを保持し、重複をスキップします。

---

## マルチモーダルメモリ（Gemini）

Gemini Embedding 2を使用して、Markdownと並行して画像や音声をインデックス化します:

| Key                       | Type       | Default    | 説明                                   |
| ------------------------- | ---------- | ---------- | -------------------------------------- |
| `multimodal.enabled`      | `boolean`  | `false`    | マルチモーダルインデックス作成を有効にする |
| `multimodal.modalities`   | `string[]` | --         | `["image"]`、`["audio"]`、または`["all"]` |
| `multimodal.maxFileBytes` | `number`   | `10000000` | インデックス作成対象の最大ファイルサイズ |

`extraPaths`内のファイルにのみ適用されます。デフォルトのメモリルートはMarkdownのみのままです。
`gemini-embedding-2-preview`が必要です。`fallback`は`"none"`でなければなりません。

サポートされる形式: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.heic`, `.heif`
（画像）; `.mp3`, `.wav`, `.ogg`, `.opus`, `.m4a`, `.aac`, `.flac`（音声）。

---

## 埋め込みキャッシュ

| Key                | Type      | Default | 説明                             |
| ------------------ | --------- | ------- | -------------------------------- |
| `cache.enabled`    | `boolean` | `false` | SQLiteにチャンク埋め込みをキャッシュする |
| `cache.maxEntries` | `number`  | `50000` | キャッシュする埋め込みの最大数   |

再インデックス作成やトランスクリプト更新時に、変更されていないテキストの再埋め込みを防ぎます。

---

## バッチインデックス作成

| Key                           | Type      | Default | 説明                     |
| ----------------------------- | --------- | ------- | ------------------------ |
| `remote.batch.enabled`        | `boolean` | `false` | バッチ埋め込みAPIを有効にする |
| `remote.batch.concurrency`    | `number`  | `2`     | 並列バッチジョブ数       |
| `remote.batch.wait`           | `boolean` | `true`  | バッチ完了を待機する     |
| `remote.batch.pollIntervalMs` | `number`  | --      | ポーリング間隔           |
| `remote.batch.timeoutMinutes` | `number`  | --      | バッチのタイムアウト     |

`openai`、`gemini`、`voyage`で利用できます。OpenAIのバッチは通常、大規模なバックフィルに対して最も高速かつ低コストです。

---

## セッションメモリ検索（experimental）

セッショントランスクリプトをインデックス化し、`memory_search`経由で表示します:

| Key                           | Type       | Default      | 説明                                      |
| ----------------------------- | ---------- | ------------ | ----------------------------------------- |
| `experimental.sessionMemory`  | `boolean`  | `false`      | セッションインデックス作成を有効にする    |
| `sources`                     | `string[]` | `["memory"]` | トランスクリプトを含めるには`"sessions"`を追加 |
| `sync.sessions.deltaBytes`    | `number`   | `100000`     | 再インデックス作成のバイトしきい値         |
| `sync.sessions.deltaMessages` | `number`   | `50`         | 再インデックス作成のメッセージしきい値     |

セッションインデックス作成はオプトインで、非同期に実行されます。結果はわずかに古い可能性があります。セッションログはディスク上に保存されるため、ファイルシステムアクセスを信頼境界として扱ってください。

---

## SQLiteベクトル高速化（sqlite-vec）

| Key                          | Type      | Default | 説明                                  |
| ---------------------------- | --------- | ------- | ------------------------------------- |
| `store.vector.enabled`       | `boolean` | `true`  | ベクトルクエリにsqlite-vecを使用する  |
| `store.vector.extensionPath` | `string`  | bundled | sqlite-vecのパスを上書きする          |

sqlite-vecが利用できない場合、OpenClawは自動的にインプロセスのコサイン類似度へフォールバックします。

---

## インデックスストレージ

| Key                   | Type     | Default                               | 説明                                        |
| --------------------- | -------- | ------------------------------------- | ------------------------------------------- |
| `store.path`          | `string` | `~/.openclaw/memory/{agentId}.sqlite` | インデックスの場所（`{agentId}`トークンをサポート） |
| `store.fts.tokenizer` | `string` | `unicode61`                           | FTS5トークナイザー（`unicode61`または`trigram`） |

---

## QMDバックエンド設定

有効にするには`memory.backend = "qmd"`を設定します。QMD設定はすべて
`memory.qmd`配下にあります:

| Key                      | Type      | Default  | 説明                                         |
| ------------------------ | --------- | -------- | -------------------------------------------- |
| `command`                | `string`  | `qmd`    | QMD実行可能ファイルのパス                    |
| `searchMode`             | `string`  | `search` | 検索コマンド: `search`, `vsearch`, `query`   |
| `includeDefaultMemory`   | `boolean` | `true`   | `MEMORY.md` + `memory/**/*.md`を自動インデックス化 |
| `paths[]`                | `array`   | --       | 追加パス: `{ name, path, pattern? }`         |
| `sessions.enabled`       | `boolean` | `false`  | セッショントランスクリプトをインデックス化   |
| `sessions.retentionDays` | `number`  | --       | トランスクリプト保持期間                     |
| `sessions.exportDir`     | `string`  | --       | エクスポートディレクトリ                     |

OpenClawは現在のQMDコレクションおよびMCPクエリ形式を優先しますが、必要に応じてレガシーの`--mask`コレクションフラグや古いMCPツール名にフォールバックすることで、古いQMDリリースも動作させます。

QMDモデルの上書きはOpenClaw設定ではなくQMD側で行います。QMDのモデルをグローバルに上書きする必要がある場合は、Gatewayランタイム環境で`QMD_EMBED_MODEL`、`QMD_RERANK_MODEL`、`QMD_GENERATE_MODEL`などの環境変数を設定してください。

### 更新スケジュール

| Key                       | Type      | Default | 説明                                 |
| ------------------------- | --------- | ------- | ------------------------------------ |
| `update.interval`         | `string`  | `5m`    | 更新間隔                             |
| `update.debounceMs`       | `number`  | `15000` | ファイル変更のデバウンス             |
| `update.onBoot`           | `boolean` | `true`  | 起動時に更新する                     |
| `update.waitForBootSync`  | `boolean` | `false` | 更新完了まで起動をブロックする       |
| `update.embedInterval`    | `string`  | --      | 埋め込み用の個別実行間隔             |
| `update.commandTimeoutMs` | `number`  | --      | QMDコマンドのタイムアウト            |
| `update.updateTimeoutMs`  | `number`  | --      | QMD更新処理のタイムアウト            |
| `update.embedTimeoutMs`   | `number`  | --      | QMD埋め込み処理のタイムアウト        |

### 制限

| Key                       | Type     | Default | 説明                         |
| ------------------------- | -------- | ------- | ---------------------------- |
| `limits.maxResults`       | `number` | `6`     | 検索結果の最大数             |
| `limits.maxSnippetChars`  | `number` | --      | スニペット長を制限する       |
| `limits.maxInjectedChars` | `number` | --      | 挿入する合計文字数を制限する |
| `limits.timeoutMs`        | `number` | `4000`  | 検索タイムアウト             |

### スコープ

どのセッションがQMD検索結果を受け取れるかを制御します。スキーマは
[`session.sendPolicy`](/ja-JP/gateway/configuration-reference#session)と同じです:

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

同梱されるデフォルト設定では、グループを引き続き拒否しつつ、ダイレクトセッションとチャネルセッションを許可します。

デフォルトはDMのみです。`match.keyPrefix`は正規化されたセッションキーに一致し、
`match.rawKeyPrefix`は`agent:<id>:`を含む生のキーに一致します。

### 引用

`memory.citations`はすべてのバックエンドに適用されます:

| Value            | Behavior                                          |
| ---------------- | ------------------------------------------------- |
| `auto` (default) | スニペットに`Source: <path#line>`フッターを含める |
| `on`             | 常にフッターを含める                              |
| `off`            | フッターを省略する（パスは内部的にエージェントへ渡される） |

### 完全なQMDの例

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

## Dreaming

Dreamingは`agents.defaults.memorySearch`ではなく、
`plugins.entries.memory-core.config.dreaming`配下で設定します。

Dreamingは1回のスケジュール済みスイープとして実行され、内部のlight/deep/REMフェーズは実装上の詳細として扱われます。

概念上の動作とスラッシュコマンドについては、[Dreaming](/ja-JP/concepts/dreaming)を参照してください。

### ユーザー設定

| Key         | Type      | Default     | 説明                                      |
| ----------- | --------- | ----------- | ----------------------------------------- |
| `enabled`   | `boolean` | `false`     | Dreaming全体を有効または無効にする        |
| `frequency` | `string`  | `0 3 * * *` | 完全なDreamingスイープの任意のCron実行間隔 |

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

注意:

- Dreamingはマシン状態を`memory/.dreams/`に書き込みます。
- Dreamingは人間が読めるナラティブ出力を`DREAMS.md`（または既存の`dreams.md`）に書き込みます。
- light/deep/REMフェーズのポリシーとしきい値は内部動作であり、ユーザー向け設定ではありません。
