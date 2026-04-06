---
read_when:
    - OpenClawプラグインを構築している
    - プラグイン設定スキーマを提供する必要がある、またはプラグイン検証エラーをデバッグしたい
summary: プラグインマニフェスト + JSON Schema要件（厳格な設定検証）
title: プラグインマニフェスト
x-i18n:
    generated_at: "2026-04-06T03:10:16Z"
    model: gpt-5.4
    provider: openai
    source_hash: f6f915a761cdb5df77eba5d2ccd438c65445bd2ab41b0539d1200e63e8cf2c3a
    source_path: plugins/manifest.md
    workflow: 15
---

# プラグインマニフェスト（openclaw.plugin.json）

このページは、**ネイティブOpenClawプラグインマニフェスト**のみを対象としています。

互換バンドルのレイアウトについては、[Plugin bundles](/ja-JP/plugins/bundles)を参照してください。

互換バンドル形式では、別のマニフェストファイルを使用します。

- Codexバンドル: `.codex-plugin/plugin.json`
- Claudeバンドル: `.claude-plugin/plugin.json` またはマニフェストなしのデフォルトClaudeコンポーネントレイアウト
- Cursorバンドル: `.cursor-plugin/plugin.json`

OpenClawはこれらのバンドルレイアウトも自動検出しますが、ここで説明する`openclaw.plugin.json`スキーマに対しては検証されません。

互換バンドルについて、OpenClawは現在、レイアウトがOpenClawランタイムの期待に一致する場合、バンドルメタデータに加えて、宣言されたスキルルート、Claudeコマンドルート、Claudeバンドルの`settings.json`既定値、ClaudeバンドルのLSP既定値、およびサポートされるフックパックを読み取ります。

すべてのネイティブOpenClawプラグインは、**プラグインルート**に`openclaw.plugin.json`ファイルを**必ず**含める必要があります。OpenClawはこのマニフェストを使って、**プラグインコードを実行せずに**設定を検証します。マニフェストが欠落しているか無効な場合はプラグインエラーとして扱われ、設定検証がブロックされます。

完全なプラグインシステムガイドについては[Plugins](/ja-JP/tools/plugin)を参照してください。
ネイティブcapability modelおよび現在の外部互換性ガイダンスについては、
[Capability model](/ja-JP/plugins/architecture#public-capability-model)を参照してください。

## このファイルの役割

`openclaw.plugin.json`は、OpenClawがプラグインコードを読み込む前に読むメタデータです。

用途:

- プラグインの識別情報
- 設定の検証
- プラグインランタイムを起動せずに利用可能であるべき認証およびオンボーディングのメタデータ
- プラグインランタイムの読み込み前に解決されるべきエイリアスおよび自動有効化メタデータ
- ランタイム読み込み前にプラグインを自動アクティブ化すべき短縮モデルファミリー所有メタデータ
- バンドルされた互換配線と契約カバレッジに使われる、静的なcapability所有スナップショット
- ランタイムを読み込まずにカタログおよび検証サーフェスへマージされるべきチャネル固有の設定メタデータ
- 設定UIヒント

用途にしないもの:

- ランタイム動作の登録
- コードのエントリーポイント宣言
- npmインストールメタデータ

これらはプラグインコードと`package.json`に属します。

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
  "providerAuthEnvVars": {
    "openrouter": ["OPENROUTER_API_KEY"]
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

| Field                               | Required | Type                             | What it means                                                                                                                                                                                                |
| ----------------------------------- | -------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `id`                                | Yes      | `string`                         | 正式なプラグインidです。これは`plugins.entries.<id>`で使用されるidです。                                                                                                                                     |
| `configSchema`                      | Yes      | `object`                         | このプラグイン設定用のインラインJSON Schemaです。                                                                                                                                                            |
| `enabledByDefault`                  | No       | `true`                           | バンドルされたプラグインをデフォルトで有効とマークします。デフォルトで無効のままにするには、省略するか、`true`以外の値を設定してください。                                                                |
| `legacyPluginIds`                   | No       | `string[]`                       | この正式プラグインidへ正規化されるレガシーidです。                                                                                                                                                           |
| `autoEnableWhenConfiguredProviders` | No       | `string[]`                       | 認証、設定、またはモデル参照でそれらが言及されたとき、このプラグインを自動有効化すべきプロバイダーidです。                                                                                                 |
| `kind`                              | No       | `"memory"` \| `"context-engine"` | `plugins.slots.*`で使用される排他的なプラグイン種別を宣言します。                                                                                                                                            |
| `channels`                          | No       | `string[]`                       | このプラグインが所有するチャネルidです。検出と設定検証に使用されます。                                                                                                                                       |
| `providers`                         | No       | `string[]`                       | このプラグインが所有するプロバイダーidです。                                                                                                                                                                 |
| `modelSupport`                      | No       | `object`                         | ランタイム前にプラグインを自動ロードするために使われる、マニフェスト所有の短縮モデルファミリーメタデータです。                                                                                             |
| `providerAuthEnvVars`               | No       | `Record<string, string[]>`       | OpenClawがプラグインコードを読み込まずに調べられる、軽量なプロバイダー認証用環境変数メタデータです。                                                                                                        |
| `providerAuthChoices`               | No       | `object[]`                       | オンボーディングピッカー、優先プロバイダー解決、および単純なCLIフラグ配線のための軽量な認証選択メタデータです。                                                                                           |
| `contracts`                         | No       | `object`                         | 音声、リアルタイム文字起こし、リアルタイム音声、メディア理解、画像生成、音楽生成、動画生成、web-fetch、Web検索、およびツール所有のための静的なバンドルcapabilityスナップショットです。                 |
| `channelConfigs`                    | No       | `Record<string, object>`         | ランタイム読み込み前に検出および検証サーフェスへマージされる、マニフェスト所有のチャネル設定メタデータです。                                                                                                |
| `skills`                            | No       | `string[]`                       | プラグインルートからの相対パスで指定する、読み込むスキルディレクトリです。                                                                                                                                   |
| `name`                              | No       | `string`                         | 人が読めるプラグイン名です。                                                                                                                                                                                 |
| `description`                       | No       | `string`                         | プラグイン画面で表示される短い要約です。                                                                                                                                                                     |
| `version`                           | No       | `string`                         | 情報提供用のプラグインバージョンです。                                                                                                                                                                       |
| `uiHints`                           | No       | `Record<string, object>`         | 設定フィールド用のUIラベル、プレースホルダー、および機密性ヒントです。                                                                                                                                       |

## providerAuthChoicesリファレンス

各`providerAuthChoices`エントリーは、1つのオンボーディングまたは認証の選択肢を記述します。
OpenClawはこれをプロバイダーランタイムの読み込み前に読み取ります。

| Field                 | Required | Type                                            | What it means                                                                     |
| --------------------- | -------- | ----------------------------------------------- | --------------------------------------------------------------------------------- |
| `provider`            | Yes      | `string`                                        | この選択肢が属するプロバイダーidです。                                            |
| `method`              | Yes      | `string`                                        | ディスパッチ先となる認証メソッドidです。                                          |
| `choiceId`            | Yes      | `string`                                        | オンボーディングおよびCLIフローで使われる安定した認証選択idです。                 |
| `choiceLabel`         | No       | `string`                                        | ユーザー向けラベルです。省略時、OpenClawは`choiceId`にフォールバックします。      |
| `choiceHint`          | No       | `string`                                        | ピッカー用の短い補助テキストです。                                                |
| `assistantPriority`   | No       | `number`                                        | アシスタント主導の対話型ピッカーで、値が小さいほど先に並びます。                  |
| `assistantVisibility` | No       | `"visible"` \| `"manual-only"`                  | アシスタントピッカーからは隠しつつ、手動CLI選択は引き続き許可します。             |
| `deprecatedChoiceIds` | No       | `string[]`                                      | この置き換え先の選択肢へ誘導すべきレガシーなchoice idです。                       |
| `groupId`             | No       | `string`                                        | 関連する選択肢をグループ化するための任意のグループidです。                        |
| `groupLabel`          | No       | `string`                                        | そのグループのユーザー向けラベルです。                                            |
| `groupHint`           | No       | `string`                                        | そのグループ用の短い補助テキストです。                                            |
| `optionKey`           | No       | `string`                                        | 単純な単一フラグ認証フロー向けの内部オプションキーです。                          |
| `cliFlag`             | No       | `string`                                        | `--openrouter-api-key`のようなCLIフラグ名です。                                   |
| `cliOption`           | No       | `string`                                        | `--openrouter-api-key <key>`のような完全なCLIオプション形式です。                 |
| `cliDescription`      | No       | `string`                                        | CLIヘルプで使用される説明です。                                                   |
| `onboardingScopes`    | No       | `Array<"text-inference" \| "image-generation">` | この選択肢を表示すべきオンボーディング画面です。省略時は`["text-inference"]`です。 |

## uiHintsリファレンス

`uiHints`は、設定フィールド名から小さなレンダリングヒントへのマップです。

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

| Field         | Type       | What it means                     |
| ------------- | ---------- | --------------------------------- |
| `label`       | `string`   | ユーザー向けのフィールドラベル。  |
| `help`        | `string`   | 短い補助テキスト。                |
| `tags`        | `string[]` | 任意のUIタグ。                    |
| `advanced`    | `boolean`  | フィールドを高度設定として扱う。  |
| `sensitive`   | `boolean`  | フィールドを秘密または機密扱い。  |
| `placeholder` | `string`   | フォーム入力用のプレースホルダー。 |

## contractsリファレンス

`contracts`は、OpenClawがプラグインランタイムをimportせずに読める静的なcapability所有メタデータにのみ使用してください。

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

| Field                            | Type       | What it means                                 |
| -------------------------------- | ---------- | --------------------------------------------- |
| `speechProviders`                | `string[]` | このプラグインが所有する音声プロバイダーid。  |
| `realtimeTranscriptionProviders` | `string[]` | このプラグインが所有するリアルタイム文字起こしプロバイダーid。 |
| `realtimeVoiceProviders`         | `string[]` | このプラグインが所有するリアルタイム音声プロバイダーid。 |
| `mediaUnderstandingProviders`    | `string[]` | このプラグインが所有するメディア理解プロバイダーid。 |
| `imageGenerationProviders`       | `string[]` | このプラグインが所有する画像生成プロバイダーid。 |
| `videoGenerationProviders`       | `string[]` | このプラグインが所有する動画生成プロバイダーid。 |
| `webFetchProviders`              | `string[]` | このプラグインが所有するweb-fetchプロバイダーid。 |
| `webSearchProviders`             | `string[]` | このプラグインが所有するWeb検索プロバイダーid。 |
| `tools`                          | `string[]` | バンドル契約チェック向けにこのプラグインが所有するエージェントツール名。 |

## channelConfigsリファレンス

`channelConfigs`は、チャネルプラグインがランタイム読み込み前に軽量な設定メタデータを必要とする場合に使用します。

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

各チャネルエントリーには以下を含められます。

| Field         | Type                     | What it means                                                                                |
| ------------- | ------------------------ | -------------------------------------------------------------------------------------------- |
| `schema`      | `object`                 | `channels.<id>`用のJSON Schemaです。宣言された各チャネル設定エントリーで必須です。          |
| `uiHints`     | `Record<string, object>` | そのチャネル設定セクション用の任意のUIラベル/プレースホルダー/機密性ヒントです。           |
| `label`       | `string`                 | ランタイムメタデータの準備前に、ピッカーおよびinspect画面へマージされるチャネルラベルです。 |
| `description` | `string`                 | inspectおよびカタログ画面向けの短いチャネル説明です。                                       |
| `preferOver`  | `string[]`               | 選択画面でこのチャネルが上位に来るべき、レガシーまたは低優先度のプラグインidです。          |

## modelSupportリファレンス

`modelSupport`は、OpenClawが`gpt-5.4`や`claude-sonnet-4.6`のような短縮モデルidから、プラグインランタイム読み込み前にあなたのプロバイダープラグインを推定すべき場合に使用します。

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

OpenClawは次の優先順位を適用します。

- 明示的な`provider/model`参照は、所有元の`providers`マニフェストメタデータを使用する
- `modelPatterns`は`modelPrefixes`より優先される
- 1つの非バンドルプラグインと1つのバンドルプラグインの両方が一致する場合、非バンドルプラグインが優先される
- 残る曖昧さは、ユーザーまたは設定がプロバイダーを指定するまで無視される

フィールド:

| Field           | Type       | What it means                                                                  |
| --------------- | ---------- | ------------------------------------------------------------------------------ |
| `modelPrefixes` | `string[]` | 短縮モデルidに対して`startsWith`で一致させる接頭辞です。                       |
| `modelPatterns` | `string[]` | プロファイル接尾辞を除去した後の短縮モデルidに対して一致させる正規表現ソースです。 |

レガシーなトップレベルcapabilityキーは非推奨です。
`openclaw doctor --fix`を使って、`speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`,
`webFetchProviders`, および `webSearchProviders` を`contracts`配下へ移動してください。通常のマニフェスト読み込みでは、これらのトップレベルフィールドはもはやcapability所有として扱われません。

## マニフェストとpackage.jsonの違い

この2つのファイルは役割が異なります。

| File                   | Use it for                                                                                                 |
| ---------------------- | ---------------------------------------------------------------------------------------------------------- |
| `openclaw.plugin.json` | プラグインコード実行前に存在している必要がある検出、設定検証、認証選択メタデータ、およびUIヒント         |
| `package.json`         | npmメタデータ、依存関係のインストール、およびエントリーポイント、インストール制御、セットアップ、またはカタログメタデータに使われる`openclaw`ブロック |

どこに置くべきメタデータか迷う場合は、次のルールを使ってください。

- OpenClawがプラグインコードを読み込む前に知っている必要があるなら、`openclaw.plugin.json`に置く
- パッケージング、エントリーファイル、またはnpmインストール動作に関するものなら、`package.json`に置く

### 検出に影響するpackage.jsonフィールド

一部のランタイム前プラグインメタデータは、`openclaw.plugin.json`ではなく、`package.json`の
`openclaw`ブロック配下に意図的に置かれます。

重要な例:

| Field                                                             | What it means                                                                                                                               |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                             | ネイティブプラグインのエントリーポイントを宣言します。                                                                                      |
| `openclaw.setupEntry`                                             | オンボーディングおよび遅延チャネル起動中に使用される、軽量なセットアップ専用エントリーポイントです。                                      |
| `openclaw.channel`                                                | ラベル、ドキュメントパス、エイリアス、選択時コピーなどの軽量チャネルカタログメタデータです。                                               |
| `openclaw.channel.configuredState`                                | 「環境変数のみのセットアップがすでに存在するか」を完全なチャネルランタイム読み込みなしに答えられる、軽量なconfigured-state checkerメタデータです。 |
| `openclaw.channel.persistedAuthState`                             | 「すでに何かサインイン済みか」を完全なチャネルランタイム読み込みなしに答えられる、軽量なpersisted-auth checkerメタデータです。            |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | バンドルおよび外部公開プラグイン向けのインストール/更新ヒントです。                                                                          |
| `openclaw.install.defaultChoice`                                  | 複数のインストール元が利用可能な場合の優先インストール経路です。                                                                            |
| `openclaw.install.minHostVersion`                                 | `>=2026.3.22`のようなsemver下限で指定する、サポートされる最小のOpenClawホストバージョンです。                                             |
| `openclaw.install.allowInvalidConfigRecovery`                     | 設定が無効な場合に、限定的なバンドルプラグイン再インストール回復経路を許可します。                                                          |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | 起動中に、完全なチャネルプラグインの前にセットアップ専用チャネル画面を読み込めるようにします。                                            |

`openclaw.install.minHostVersion`は、インストール時とマニフェストレジストリ読み込み時に強制されます。
無効な値は拒否され、有効だが新しすぎる値の場合、古いホストではそのプラグインはスキップされます。

`openclaw.install.allowInvalidConfigRecovery`は意図的に限定的です。
これは任意の壊れた設定をインストール可能にするものではありません。現時点では、たとえばバンドルプラグインパスの欠落や、その同じバンドルプラグインに対する古い`channels.<id>`エントリーのような、特定の古いバンドルプラグイン更新失敗からインストールフローが回復できるようにするだけです。無関係な設定エラーは引き続きインストールをブロックし、オペレーターは`openclaw doctor --fix`へ案内されます。

`openclaw.channel.persistedAuthState`は、小さなcheckerモジュール用のパッケージメタデータです。

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

セットアップ、doctor、またはconfigured-stateフローで、完全なチャネルプラグイン読み込み前に軽量なyes/no認証プローブが必要な場合に使ってください。対象exportは、永続化された状態のみを読む小さな関数であるべきです。完全なチャネルランタイムbarrelを経由させないでください。

`openclaw.channel.configuredState`も同じ形で、軽量な環境変数のみのconfiguredチェックに使います。

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

チャネルが環境変数または他の小さな非ランタイム入力からconfigured-stateを判定できる場合に使ってください。完全な設定解決または実際のチャネルランタイムが必要な場合は、そのロジックを代わりにプラグインの`config.hasConfiguredState`フックに置いてください。

## JSON Schema要件

- **すべてのプラグインはJSON Schemaを必ず含める必要があります**。設定を受け付けない場合でも同様です。
- 空のスキーマも許容されます（例: `{ "type": "object", "additionalProperties": false }`）。
- スキーマはランタイム時ではなく、設定の読み取り/書き込み時に検証されます。

## 検証動作

- 不明な`channels.*`キーは、チャネルidがプラグインマニフェストで宣言されていない限り**エラー**です。
- `plugins.entries.<id>`, `plugins.allow`, `plugins.deny`, および `plugins.slots.*` は、**検出可能な**プラグインidを参照する必要があります。不明なidは**エラー**です。
- プラグインがインストール済みでも、マニフェストまたはスキーマが壊れているか欠落している場合、検証は失敗し、Doctorがそのプラグインエラーを報告します。
- プラグイン設定が存在していても、プラグインが**無効**の場合、設定は保持され、Doctor + ログで**警告**が表示されます。

完全な`plugins.*`スキーマについては[Configuration reference](/ja-JP/gateway/configuration)を参照してください。

## メモ

- マニフェストは、ローカルファイルシステムからの読み込みを含む**ネイティブOpenClawプラグインで必須**です。
- ランタイムは引き続きプラグインモジュールを別途読み込みます。マニフェストは検出 + 検証専用です。
- ネイティブマニフェストはJSON5で解析されるため、最終値がオブジェクトである限り、コメント、末尾カンマ、およびクォートなしキーが受け入れられます。
- マニフェストローダーが読み取るのは文書化されたマニフェストフィールドのみです。ここにカスタムのトップレベルキーを追加しないでください。
- `providerAuthEnvVars`は、認証プローブ、環境変数マーカー検証、および同様の、環境変数名を調べるだけのためにプロバイダーランタイムを起動すべきでないプロバイダー認証画面向けの軽量メタデータ経路です。
- `providerAuthChoices`は、認証選択ピッカー、`--auth-choice`解決、優先プロバイダーマッピング、およびプロバイダーランタイム読み込み前の単純なオンボーディングCLIフラグ登録向けの軽量メタデータ経路です。プロバイダーコードを必要とするランタイムウィザードメタデータについては、
  [Provider runtime hooks](/ja-JP/plugins/architecture#provider-runtime-hooks)を参照してください。
- 排他的プラグイン種別は`plugins.slots.*`を通じて選択されます。
  - `kind: "memory"`は`plugins.slots.memory`で選択されます。
  - `kind: "context-engine"`は`plugins.slots.contextEngine`で選択されます
    （デフォルト: 組み込みの`legacy`）。
- `channels`, `providers`, および `skills`は、
  プラグインで不要な場合は省略できます。
- プラグインがネイティブモジュールに依存する場合は、ビルド手順と、必要なパッケージマネージャー許可リスト要件（例: pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`）を文書化してください。

## 関連

- [Building Plugins](/ja-JP/plugins/building-plugins) — プラグインのはじめ方
- [Plugin Architecture](/ja-JP/plugins/architecture) — 内部アーキテクチャ
- [SDK Overview](/ja-JP/plugins/sdk-overview) — Plugin SDKリファレンス
