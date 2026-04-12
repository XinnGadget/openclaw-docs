---
read_when:
    - OpenClawプラグインを構築しています
    - プラグイン設定スキーマを提供する必要がある場合や、プラグイン検証エラーをデバッグする場合があります
summary: プラグインマニフェスト + JSON スキーマ要件（厳格な設定検証）
title: プラグインマニフェスト
x-i18n:
    generated_at: "2026-04-12T04:43:44Z"
    model: gpt-5.4
    provider: openai
    source_hash: bf666b0f41f07641375a248f52e29ba6a68c3ec20404bedb6b52a20a5cd92e91
    source_path: plugins/manifest.md
    workflow: 15
---

# プラグインマニフェスト (`openclaw.plugin.json`)

このページは、**ネイティブなOpenClawプラグインマニフェスト**のみを対象としています。

互換性のあるバンドルレイアウトについては、[Plugin bundles](/ja-JP/plugins/bundles) を参照してください。

互換バンドル形式では、異なるマニフェストファイルを使用します。

- Codex バンドル: `.codex-plugin/plugin.json`
- Claude バンドル: `.claude-plugin/plugin.json` または、マニフェストのないデフォルトの Claude コンポーネント
  レイアウト
- Cursor バンドル: `.cursor-plugin/plugin.json`

OpenClaw はそれらのバンドルレイアウトも自動検出しますが、ここで説明する `openclaw.plugin.json` スキーマに照らして検証されるわけではありません。

互換バンドルについては、OpenClaw は現在、レイアウトが OpenClaw ランタイムの想定に一致する場合に、バンドルメタデータに加えて、宣言された
skill ルート、Claude コマンドルート、Claude バンドルの `settings.json` デフォルト、
Claude バンドルの LSP デフォルト、およびサポートされているフックパックを読み取ります。

すべてのネイティブ OpenClaw プラグインは、**プラグインルート**に `openclaw.plugin.json` ファイルを**必ず**含める必要があります。OpenClaw はこのマニフェストを使用して、**プラグインコードを実行せずに**設定を検証します。マニフェストが欠落している、または無効な場合は、プラグインエラーとして扱われ、設定検証がブロックされます。

プラグインシステム全体のガイドは [Plugins](/ja-JP/tools/plugin) を参照してください。
ネイティブな capability モデルと、現在の外部互換性ガイダンスについては、
[Capability model](/ja-JP/plugins/architecture#public-capability-model) を参照してください。

## このファイルの役割

`openclaw.plugin.json` は、OpenClaw がプラグインコードを読み込む前に読み取るメタデータです。

用途:

- プラグインの識別情報
- 設定検証
- プラグインランタイムを起動しなくても利用可能であるべき認証およびオンボーディングのメタデータ
- ランタイム読み込み前に control-plane サーフェスが確認できる、軽量な有効化ヒント
- ランタイム読み込み前にセットアップ/オンボーディングサーフェスが確認できる、軽量なセットアップ記述子
- プラグインランタイム読み込み前に解決されるべきエイリアスおよび自動有効化メタデータ
- ランタイム読み込み前にプラグインを自動有効化する必要がある、短縮形の model-family 所有メタデータ
- バンドルされた互換配線と契約カバレッジに使われる、静的な capability 所有スナップショット
- ランタイムを読み込まずにカタログおよび検証サーフェスにマージされるべき、チャネル固有の設定メタデータ
- 設定 UI ヒント

用途ではないもの:

- ランタイム動作の登録
- コードエントリーポイントの宣言
- npm install メタデータ

これらはプラグインコードと `package.json` に属します。

## 最小例

```json
{
  "id": "voice-call",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
```

## 詳細な例

```json
{
  "id": "openrouter",
  "name": "OpenRouter",
  "description": "OpenRouter provider plugin",
  "version": "1.0.0",
  "providers": ["openrouter"],
  "modelSupport": {
    "modelPrefixes": ["router-"]
  },
  "cliBackends": ["openrouter-cli"],
  "providerAuthEnvVars": {
    "openrouter": ["OPENROUTER_API_KEY"]
  },
  "providerAuthAliases": {
    "openrouter-coding": "openrouter"
  },
  "channelEnvVars": {
    "openrouter-chatops": ["OPENROUTER_CHATOPS_TOKEN"]
  },
  "providerAuthChoices": [
    {
      "provider": "openrouter",
      "method": "api-key",
      "choiceId": "openrouter-api-key",
      "choiceLabel": "OpenRouter API key",
      "groupId": "openrouter",
      "groupLabel": "OpenRouter",
      "optionKey": "openrouterApiKey",
      "cliFlag": "--openrouter-api-key",
      "cliOption": "--openrouter-api-key <key>",
      "cliDescription": "OpenRouter API key",
      "onboardingScopes": ["text-inference"]
    }
  ],
  "uiHints": {
    "apiKey": {
      "label": "API key",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  },
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "apiKey": {
        "type": "string"
      }
    }
  }
}
```

## トップレベルフィールドのリファレンス

| フィールド                            | 必須     | 型                               | 意味                                                                                                                                                                                                         |
| ------------------------------------- | -------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `id`                                  | はい     | `string`                         | 正規のプラグイン ID。これは `plugins.entries.<id>` で使われる ID です。                                                                                                                                      |
| `configSchema`                        | はい     | `object`                         | このプラグイン設定用のインライン JSON Schema。                                                                                                                                                               |
| `enabledByDefault`                    | いいえ   | `true`                           | バンドルされたプラグインをデフォルトで有効としてマークします。デフォルトで無効のままにするには、省略するか、`true` 以外の値を設定します。                                                                  |
| `legacyPluginIds`                     | いいえ   | `string[]`                       | この正規プラグイン ID に正規化されるレガシー ID。                                                                                                                                                            |
| `autoEnableWhenConfiguredProviders`   | いいえ   | `string[]`                       | 認証、設定、またはモデル参照で言及されたときに、このプラグインを自動有効化すべきプロバイダー ID。                                                                                                            |
| `kind`                                | いいえ   | `"memory"` \| `"context-engine"` | `plugins.slots.*` で使われる排他的なプラグイン種別を宣言します。                                                                                                                                             |
| `channels`                            | いいえ   | `string[]`                       | このプラグインが所有するチャネル ID。検出および設定検証に使用されます。                                                                                                                                      |
| `providers`                           | いいえ   | `string[]`                       | このプラグインが所有するプロバイダー ID。                                                                                                                                                                     |
| `modelSupport`                        | いいえ   | `object`                         | ランタイムの前にプラグインを自動読み込みするために使われる、マニフェスト所有の短縮形 model-family メタデータ。                                                                                                |
| `cliBackends`                         | いいえ   | `string[]`                       | このプラグインが所有する CLI 推論バックエンド ID。明示的な設定参照からの起動時自動有効化に使用されます。                                                                                                     |
| `commandAliases`                      | いいえ   | `object[]`                       | ランタイム読み込み前に、プラグイン対応の設定および CLI 診断を生成すべき、このプラグインが所有するコマンド名。                                                                                                |
| `providerAuthEnvVars`                 | いいえ   | `Record<string, string[]>`       | OpenClaw がプラグインコードを読み込まずに確認できる、軽量なプロバイダー認証 env メタデータ。                                                                                                                 |
| `providerAuthAliases`                 | いいえ   | `Record<string, string>`         | 認証参照のために別のプロバイダー ID を再利用すべきプロバイダー ID。たとえば、ベースプロバイダーの API キーと認証プロファイルを共有する coding プロバイダーなどです。                                      |
| `channelEnvVars`                      | いいえ   | `Record<string, string[]>`       | OpenClaw がプラグインコードを読み込まずに確認できる、軽量なチャネル env メタデータ。env 駆動のチャネルセットアップや、汎用の起動/設定ヘルパーが認識すべき認証サーフェスに使用します。                      |
| `providerAuthChoices`                 | いいえ   | `object[]`                       | オンボーディングピッカー、優先プロバイダー解決、および単純な CLI フラグ配線のための、軽量な認証選択メタデータ。                                                                                              |
| `activation`                          | いいえ   | `object`                         | プロバイダー、コマンド、チャネル、ルート、および capability トリガー読み込みのための軽量な有効化ヒント。メタデータのみであり、実際の動作は引き続きプラグインランタイムが所有します。                        |
| `setup`                               | いいえ   | `object`                         | 検出およびセットアップサーフェスがプラグインランタイムを読み込まずに確認できる、軽量なセットアップ/オンボーディング記述子。                                                                                 |
| `contracts`                           | いいえ   | `object`                         | speech、realtime transcription、realtime voice、media-understanding、image-generation、music-generation、video-generation、web-fetch、web search、およびツール所有権のための静的なバンドル capability スナップショット。 |
| `channelConfigs`                      | いいえ   | `Record<string, object>`         | ランタイム読み込み前に、検出および検証サーフェスにマージされるマニフェスト所有のチャネル設定メタデータ。                                                                                                     |
| `skills`                              | いいえ   | `string[]`                       | 読み込む Skills ディレクトリ。プラグインルートからの相対パスです。                                                                                                                                           |
| `name`                                | いいえ   | `string`                         | 人間が読めるプラグイン名。                                                                                                                                                                                    |
| `description`                         | いいえ   | `string`                         | プラグインサーフェスに表示される短い概要。                                                                                                                                                                    |
| `version`                             | いいえ   | `string`                         | 情報提供用のプラグインバージョン。                                                                                                                                                                            |
| `uiHints`                             | いいえ   | `Record<string, object>`         | 設定フィールドの UI ラベル、プレースホルダー、および機密性ヒント。                                                                                                                                            |

## `providerAuthChoices` リファレンス

各 `providerAuthChoices` エントリは、1 つのオンボーディングまたは認証の選択肢を表します。
OpenClaw はこれをプロバイダーランタイムの読み込み前に読み取ります。

| フィールド              | 必須     | 型                                              | 意味                                                                                                     |
| ----------------------- | -------- | ----------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `provider`              | はい     | `string`                                        | この選択肢が属するプロバイダー ID。                                                                      |
| `method`                | はい     | `string`                                        | ディスパッチ先の認証メソッド ID。                                                                        |
| `choiceId`              | はい     | `string`                                        | オンボーディングおよび CLI フローで使われる安定した認証選択 ID。                                         |
| `choiceLabel`           | いいえ   | `string`                                        | ユーザー向けラベル。省略した場合、OpenClaw は `choiceId` にフォールバックします。                        |
| `choiceHint`            | いいえ   | `string`                                        | ピッカー向けの短い補足テキスト。                                                                         |
| `assistantPriority`     | いいえ   | `number`                                        | アシスタント主導のインタラクティブピッカーで、値が小さいほど先に並びます。                               |
| `assistantVisibility`   | いいえ   | `"visible"` \| `"manual-only"`                  | 手動 CLI 選択は許可したまま、アシスタントピッカーからこの選択肢を隠します。                              |
| `deprecatedChoiceIds`   | いいえ   | `string[]`                                      | ユーザーをこの置き換え先の選択肢へリダイレクトすべき、レガシーな選択 ID。                                |
| `groupId`               | いいえ   | `string`                                        | 関連する選択肢をグループ化するための任意のグループ ID。                                                  |
| `groupLabel`            | いいえ   | `string`                                        | そのグループのユーザー向けラベル。                                                                       |
| `groupHint`             | いいえ   | `string`                                        | グループ向けの短い補足テキスト。                                                                         |
| `optionKey`             | いいえ   | `string`                                        | 単一フラグのシンプルな認証フロー向けの内部オプションキー。                                               |
| `cliFlag`               | いいえ   | `string`                                        | `--openrouter-api-key` のような CLI フラグ名。                                                           |
| `cliOption`             | いいえ   | `string`                                        | `--openrouter-api-key <key>` のような完全な CLI オプション形。                                           |
| `cliDescription`        | いいえ   | `string`                                        | CLI ヘルプで使われる説明。                                                                               |
| `onboardingScopes`      | いいえ   | `Array<"text-inference" \| "image-generation">` | この選択肢を表示すべきオンボーディングサーフェス。省略した場合、デフォルトは `["text-inference"]` です。 |

## `commandAliases` リファレンス

ユーザーがプラグイン所有のランタイムコマンド名を誤って `plugins.allow` に入れたり、ルート CLI コマンドとして実行しようとしたりする可能性がある場合は、`commandAliases` を使用します。OpenClaw はこのメタデータを、プラグインランタイムコードをインポートせずに診断に使用します。

```json
{
  "commandAliases": [
    {
      "name": "dreaming",
      "kind": "runtime-slash",
      "cliCommand": "memory"
    }
  ]
}
```

| フィールド   | 必須     | 型                | 意味                                                                           |
| ------------ | -------- | ----------------- | ------------------------------------------------------------------------------ |
| `name`       | はい     | `string`          | このプラグインに属するコマンド名。                                             |
| `kind`       | いいえ   | `"runtime-slash"` | このエイリアスを、ルート CLI コマンドではなくチャットスラッシュコマンドとして示します。 |
| `cliCommand` | いいえ   | `string`          | 存在する場合、CLI 操作向けに提案する関連ルート CLI コマンド。                  |

## `activation` リファレンス

プラグインが後で有効化すべき control-plane イベントを軽量に宣言できる場合は、`activation` を使用します。

このブロックはメタデータのみです。ランタイム動作は登録せず、`register(...)`、`setupEntry`、その他のランタイム/プラグインエントリーポイントの代わりにもなりません。

```json
{
  "activation": {
    "onProviders": ["openai"],
    "onCommands": ["models"],
    "onChannels": ["web"],
    "onRoutes": ["gateway-webhook"],
    "onCapabilities": ["provider", "tool"]
  }
}
```

| フィールド       | 必須     | 型                                                   | 意味                                                                |
| ---------------- | -------- | ---------------------------------------------------- | ------------------------------------------------------------------- |
| `onProviders`    | いいえ   | `string[]`                                           | 要求時にこのプラグインを有効化すべきプロバイダー ID。               |
| `onCommands`     | いいえ   | `string[]`                                           | このプラグインを有効化すべきコマンド ID。                           |
| `onChannels`     | いいえ   | `string[]`                                           | このプラグインを有効化すべきチャネル ID。                           |
| `onRoutes`       | いいえ   | `string[]`                                           | このプラグインを有効化すべきルート種別。                            |
| `onCapabilities` | いいえ   | `Array<"provider" \| "channel" \| "tool" \| "hook">` | control-plane の有効化計画で使われる、大まかな capability ヒント。 |

## `setup` リファレンス

セットアップおよびオンボーディングサーフェスで、ランタイム読み込み前に軽量なプラグイン所有メタデータが必要な場合は、`setup` を使用します。

```json
{
  "setup": {
    "providers": [
      {
        "id": "openai",
        "authMethods": ["api-key"],
        "envVars": ["OPENAI_API_KEY"]
      }
    ],
    "cliBackends": ["openai-cli"],
    "configMigrations": ["legacy-openai-auth"],
    "requiresRuntime": false
  }
}
```

トップレベルの `cliBackends` は引き続き有効であり、CLI 推論バックエンドを記述し続けます。`setup.cliBackends` は、メタデータ専用のままにすべき control-plane/セットアップフロー向けの、セットアップ固有の記述子サーフェスです。

`setup.providers` と `setup.cliBackends` が存在する場合、これらはセットアップ検出のための優先される記述子優先ルックアップサーフェスです。記述子が候補プラグインの絞り込みだけを行い、セットアップにさらに豊富なセットアップ時ランタイムフックが必要な場合は、`requiresRuntime: true` を設定し、フォールバック実行パスとして `setup-api` を維持してください。

セットアップのルックアップではプラグイン所有の `setup-api` コードを実行できるため、正規化された `setup.providers[].id` および `setup.cliBackends[]` の値は、検出されたプラグイン全体で一意でなければなりません。所有権が曖昧な場合は、検出順から勝者を選ぶのではなく、クローズドに失敗します。

### `setup.providers` リファレンス

| フィールド    | 必須     | 型         | 意味                                                                                 |
| ------------- | -------- | ---------- | ------------------------------------------------------------------------------------ |
| `id`          | はい     | `string`   | セットアップまたはオンボーディング中に公開されるプロバイダー ID。正規化された ID はグローバルで一意に保ってください。 |
| `authMethods` | いいえ   | `string[]` | 完全なランタイムを読み込まずにこのプロバイダーがサポートする、セットアップ/認証メソッド ID。 |
| `envVars`     | いいえ   | `string[]` | 汎用のセットアップ/ステータスサーフェスが、プラグインランタイムの読み込み前に確認できる env var。 |

### `setup` フィールド

| フィールド         | 必須     | 型         | 意味                                                                                                 |
| ------------------ | -------- | ---------- | ---------------------------------------------------------------------------------------------------- |
| `providers`        | いいえ   | `object[]` | セットアップおよびオンボーディング中に公開されるプロバイダーセットアップ記述子。                     |
| `cliBackends`      | いいえ   | `string[]` | 記述子優先のセットアップルックアップで使われるセットアップ時バックエンド ID。正規化された ID はグローバルで一意に保ってください。 |
| `configMigrations` | いいえ   | `string[]` | このプラグインのセットアップサーフェスが所有する設定マイグレーション ID。                            |
| `requiresRuntime`  | いいえ   | `boolean`  | 記述子ルックアップ後もセットアップに `setup-api` の実行が必要かどうか。                              |

## `uiHints` リファレンス

`uiHints` は、設定フィールド名から小さなレンダリングヒントへのマップです。

```json
{
  "uiHints": {
    "apiKey": {
      "label": "API key",
      "help": "Used for OpenRouter requests",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  }
}
```

各フィールドヒントには以下を含められます。

| フィールド    | 型         | 意味                                  |
| ------------- | ---------- | ------------------------------------- |
| `label`       | `string`   | ユーザー向けのフィールドラベル。      |
| `help`        | `string`   | 短い補足テキスト。                    |
| `tags`        | `string[]` | 任意の UI タグ。                      |
| `advanced`    | `boolean`  | このフィールドを高度な項目として示します。 |
| `sensitive`   | `boolean`  | このフィールドを秘密情報または機密情報として示します。 |
| `placeholder` | `string`   | フォーム入力用のプレースホルダーテキスト。 |

## `contracts` リファレンス

`contracts` は、OpenClaw がプラグインランタイムをインポートせずに読み取れる、静的な capability 所有メタデータにのみ使用してください。

```json
{
  "contracts": {
    "speechProviders": ["openai"],
    "realtimeTranscriptionProviders": ["openai"],
    "realtimeVoiceProviders": ["openai"],
    "mediaUnderstandingProviders": ["openai", "openai-codex"],
    "imageGenerationProviders": ["openai"],
    "videoGenerationProviders": ["qwen"],
    "webFetchProviders": ["firecrawl"],
    "webSearchProviders": ["gemini"],
    "tools": ["firecrawl_search", "firecrawl_scrape"]
  }
}
```

各リストは任意です。

| フィールド                       | 型         | 意味                                                         |
| -------------------------------- | ---------- | ------------------------------------------------------------ |
| `speechProviders`                | `string[]` | このプラグインが所有する speech プロバイダー ID。            |
| `realtimeTranscriptionProviders` | `string[]` | このプラグインが所有する realtime-transcription プロバイダー ID。 |
| `realtimeVoiceProviders`         | `string[]` | このプラグインが所有する realtime-voice プロバイダー ID。    |
| `mediaUnderstandingProviders`    | `string[]` | このプラグインが所有する media-understanding プロバイダー ID。 |
| `imageGenerationProviders`       | `string[]` | このプラグインが所有する image-generation プロバイダー ID。   |
| `videoGenerationProviders`       | `string[]` | このプラグインが所有する video-generation プロバイダー ID。   |
| `webFetchProviders`              | `string[]` | このプラグインが所有する web-fetch プロバイダー ID。          |
| `webSearchProviders`             | `string[]` | このプラグインが所有する web-search プロバイダー ID。         |
| `tools`                          | `string[]` | バンドル契約チェックのためにこのプラグインが所有するエージェントツール名。 |

## `channelConfigs` リファレンス

チャネルプラグインがランタイム読み込み前に軽量な設定メタデータを必要とする場合は、`channelConfigs` を使用します。

```json
{
  "channelConfigs": {
    "matrix": {
      "schema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "homeserverUrl": { "type": "string" }
        }
      },
      "uiHints": {
        "homeserverUrl": {
          "label": "Homeserver URL",
          "placeholder": "https://matrix.example.com"
        }
      },
      "label": "Matrix",
      "description": "Matrix homeserver connection",
      "preferOver": ["matrix-legacy"]
    }
  }
}
```

各チャネルエントリには以下を含められます。

| フィールド    | 型                       | 意味                                                                                     |
| ------------- | ------------------------ | ---------------------------------------------------------------------------------------- |
| `schema`      | `object`                 | `channels.<id>` 用の JSON Schema。宣言された各チャネル設定エントリで必須です。           |
| `uiHints`     | `Record<string, object>` | そのチャネル設定セクション向けの任意の UI ラベル / プレースホルダー / 機密性ヒント。     |
| `label`       | `string`                 | ランタイムメタデータが準備できていないときに、ピッカーおよび確認サーフェスにマージされるチャネルラベル。 |
| `description` | `string`                 | 確認およびカタログサーフェス向けの短いチャネル説明。                                     |
| `preferOver`  | `string[]`               | 選択サーフェスでこのチャネルが優先されるべき、レガシーまたは優先度の低いプラグイン ID。   |

## `modelSupport` リファレンス

プラグインランタイムの読み込み前に、OpenClaw が `gpt-5.4` や `claude-sonnet-4.6` のような短縮形モデル ID からプロバイダープラグインを推測すべき場合は、`modelSupport` を使用します。

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

OpenClaw は次の優先順位を適用します。

- 明示的な `provider/model` 参照では、所有している `providers` マニフェストメタデータを使用します
- `modelPatterns` は `modelPrefixes` より優先されます
- 1 つの非バンドルプラグインと 1 つのバンドルプラグインの両方が一致する場合、非バンドルプラグインが優先されます
- 残る曖昧さは、ユーザーまたは設定がプロバイダーを指定するまで無視されます

フィールド:

| フィールド      | 型         | 意味                                                                            |
| --------------- | ---------- | ------------------------------------------------------------------------------- |
| `modelPrefixes` | `string[]` | 短縮形モデル ID に対して `startsWith` で照合されるプレフィックス。              |
| `modelPatterns` | `string[]` | プロファイル接尾辞を除去した後の短縮形モデル ID に対して照合される正規表現ソース。 |

レガシーなトップレベル capability キーは非推奨です。`openclaw doctor --fix` を使って、`speechProviders`、`realtimeTranscriptionProviders`、
`realtimeVoiceProviders`、`mediaUnderstandingProviders`、
`imageGenerationProviders`、`videoGenerationProviders`、
`webFetchProviders`、および `webSearchProviders` を `contracts` の下へ移動してください。通常の
マニフェスト読み込みでは、これらのトップレベルフィールドを capability
所有権としては扱わなくなりました。

## マニフェストと package.json の違い

この 2 つのファイルは、異なる役割を持っています。

| ファイル                 | 用途                                                                                                                                   |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.plugin.json`   | 検出、設定検証、認証選択メタデータ、およびプラグインコード実行前に存在している必要がある UI ヒント                                   |
| `package.json`           | npm メタデータ、依存関係のインストール、およびエントリーポイント、インストール制御、セットアップ、またはカタログメタデータに使用される `openclaw` ブロック |

どこにメタデータを置くべきか迷った場合は、次のルールを使ってください。

- OpenClaw がプラグインコードを読み込む前に知っている必要があるなら、`openclaw.plugin.json` に置きます
- パッケージング、エントリーファイル、または npm install の動作に関するものなら、`package.json` に置きます

### 検出に影響する `package.json` フィールド

一部のランタイム前プラグインメタデータは、`openclaw.plugin.json` ではなく、`package.json` の
`openclaw` ブロック配下に意図的に置かれています。

重要な例:

| フィールド                                                           | 意味                                                                                                                                         |
| -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                                | ネイティブプラグインのエントリーポイントを宣言します。                                                                                        |
| `openclaw.setupEntry`                                                | オンボーディングおよび遅延チャネル起動中に使用される、軽量なセットアップ専用エントリーポイント。                                              |
| `openclaw.channel`                                                   | ラベル、ドキュメントパス、エイリアス、選択時の文言などの軽量なチャネルカタログメタデータ。                                                    |
| `openclaw.channel.configuredState`                                   | フルチャネルランタイムを読み込まずに「env のみのセットアップがすでに存在するか？」に答えられる、軽量な configured-state チェッカーメタデータ。 |
| `openclaw.channel.persistedAuthState`                                | フルチャネルランタイムを読み込まずに「すでにサインイン済みのものがあるか？」に答えられる、軽量な永続化認証チェッカーメタデータ。              |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`            | バンドル済みおよび外部公開プラグイン向けのインストール / 更新ヒント。                                                                         |
| `openclaw.install.defaultChoice`                                     | 複数のインストール元がある場合の優先インストールパス。                                                                                       |
| `openclaw.install.minHostVersion`                                    | `>=2026.3.22` のような semver 下限で表す、サポートされる最小 OpenClaw ホストバージョン。                                                     |
| `openclaw.install.allowInvalidConfigRecovery`                        | 設定が無効な場合に限定された、バンドルプラグインの再インストール回復パスを許可します。                                                       |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`    | 起動中に、フルチャネルプラグインより先にセットアップ専用チャネルサーフェスを読み込めるようにします。                                         |

`openclaw.install.minHostVersion` は、インストール時およびマニフェスト
レジストリ読み込み時に適用されます。無効な値は拒否されます。有効ではあるがより新しい値の場合、古いホストではそのプラグインをスキップします。

`openclaw.install.allowInvalidConfigRecovery` は、意図的に範囲が限定されています。
これによって任意の壊れた設定がインストール可能になるわけではありません。現在のところ、
同じバンドルプラグインに対するバンドルプラグインパスの欠落や古い `channels.<id>`
エントリなど、特定の古いバンドルプラグイン更新失敗からの回復をインストールフローで許可するだけです。
無関係な設定エラーは引き続きインストールをブロックし、オペレーターを
`openclaw doctor --fix` へ案内します。

`openclaw.channel.persistedAuthState` は、小さなチェッカーモジュール用のパッケージメタデータです。

```json
{
  "openclaw": {
    "channel": {
      "id": "whatsapp",
      "persistedAuthState": {
        "specifier": "./auth-presence",
        "exportName": "hasAnyWhatsAppAuth"
      }
    }
  }
}
```

これは、セットアップ、doctor、または configured-state フローで、フルチャネルプラグインの読み込み前に、軽量な yes/no 認証プローブが必要な場合に使用します。対象の export は、永続化された状態のみを読み取る小さな関数にしてください。フルチャネルランタイムバレル経由にしないでください。

`openclaw.channel.configuredState` も、軽量な env-only
configured チェック向けに同じ形に従います。

```json
{
  "openclaw": {
    "channel": {
      "id": "telegram",
      "configuredState": {
        "specifier": "./configured-state",
        "exportName": "hasTelegramConfiguredState"
      }
    }
  }
}
```

これは、チャネルが env またはその他の小さな非ランタイム入力から configured-state に答えられる場合に使用します。チェックに完全な設定解決または実際のチャネルランタイムが必要な場合は、そのロジックを代わりにプラグインの `config.hasConfiguredState` フック内に置いてください。

## JSON Schema の要件

- **すべてのプラグインは JSON Schema を必ず提供する必要があります**。設定を受け付けない場合でも同様です。
- 空のスキーマでも構いません（例: `{ "type": "object", "additionalProperties": false }`）。
- スキーマはランタイム時ではなく、設定の読み取り / 書き込み時に検証されます。

## 検証動作

- 不明な `channels.*` キーは、チャネル ID がプラグインマニフェストで宣言されていない限り、**エラー**です。
- `plugins.entries.<id>`、`plugins.allow`、`plugins.deny`、および `plugins.slots.*` は、**検出可能な**プラグイン ID を参照していなければなりません。不明な ID は **エラー** です。
- プラグインがインストールされていても、マニフェストまたはスキーマが壊れている、または欠落している場合、検証は失敗し、Doctor がそのプラグインエラーを報告します。
- プラグイン設定が存在していても、そのプラグインが**無効**の場合、設定は保持され、Doctor + ログで**警告**が表示されます。

完全な `plugins.*` スキーマについては、[Configuration reference](/ja-JP/gateway/configuration) を参照してください。

## 注意

- マニフェストは、ローカルファイルシステム読み込みを含む**ネイティブ OpenClaw プラグインで必須**です。
- ランタイムは引き続きプラグインモジュールを別途読み込みます。マニフェストは
  検出 + 検証専用です。
- ネイティブマニフェストは JSON5 で解析されるため、最終的な値が引き続きオブジェクトである限り、
  コメント、末尾のカンマ、引用符なしキーが許容されます。
- マニフェストローダーが読み取るのは、文書化されたマニフェストフィールドのみです。ここに
  カスタムのトップレベルキーを追加しないでください。
- `providerAuthEnvVars` は、認証プローブ、env-marker
  検証、および env 名を確認するだけのためにプラグインランタイムを起動すべきでない同様の provider-auth サーフェス向けの、軽量メタデータパスです。
- `providerAuthAliases` は、コアにその関係をハードコードせずに、プロバイダーバリアントが別のプロバイダーの認証
  env var、認証プロファイル、設定ベース認証、および API キーのオンボーディング選択肢を再利用できるようにします。
- `channelEnvVars` は、シェル env フォールバック、セットアップ
  プロンプト、および env 名を確認するだけのためにチャネルランタイムを起動すべきでない同様のチャネルサーフェス向けの、軽量メタデータパスです。
- `providerAuthChoices` は、認証選択ピッカー、
  `--auth-choice` 解決、優先プロバイダーマッピング、およびプロバイダーランタイム読み込み前の単純なオンボーディング
  CLI フラグ登録向けの、軽量メタデータパスです。プロバイダーコードが必要なランタイム
  ウィザードメタデータについては、
  [Provider runtime hooks](/ja-JP/plugins/architecture#provider-runtime-hooks) を参照してください。
- 排他的なプラグイン種別は `plugins.slots.*` を通じて選択されます。
  - `kind: "memory"` は `plugins.slots.memory` で選択されます。
  - `kind: "context-engine"` は `plugins.slots.contextEngine`
    で選択されます（デフォルト: 組み込みの `legacy`）。
- `channels`、`providers`、`cliBackends`、および `skills` は、プラグインが
  それらを必要としない場合は省略できます。
- プラグインがネイティブモジュールに依存している場合は、ビルド手順と、
  パッケージマネージャーの allowlist 要件（たとえば pnpm の `allow-build-scripts`
  - `pnpm rebuild <package>`）を文書化してください。

## 関連

- [Building Plugins](/ja-JP/plugins/building-plugins) — プラグインのはじめに
- [Plugin Architecture](/ja-JP/plugins/architecture) — 内部アーキテクチャ
- [SDK Overview](/ja-JP/plugins/sdk-overview) — Plugin SDK リファレンス
