---
read_when:
    - OpenClawプラグインを構築している場合
    - プラグイン設定スキーマを提供する必要がある場合、またはプラグイン検証エラーをデバッグする場合
summary: プラグインmanifest + JSON Schema要件（厳格な設定検証）
title: プラグインmanifest
x-i18n:
    generated_at: "2026-04-07T04:45:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: 22d41b9f8748b1b1b066ee856be4a8f41e88b9a8bc073d74fc79d2bb0982f01a
    source_path: plugins/manifest.md
    workflow: 15
---

# プラグインmanifest（openclaw.plugin.json）

このページは、**ネイティブOpenClawプラグインmanifest** 専用です。

互換性のあるバンドルレイアウトについては、[Plugin bundles](/ja-JP/plugins/bundles) を参照してください。

互換バンドル形式では、異なるmanifestファイルを使用します:

- Codex bundle: `.codex-plugin/plugin.json`
- Claude bundle: `.claude-plugin/plugin.json` またはmanifestなしのデフォルトClaude component
  レイアウト
- Cursor bundle: `.cursor-plugin/plugin.json`

OpenClawはそれらのバンドルレイアウトも自動検出しますが、ここで説明する `openclaw.plugin.json` スキーマに対しては検証されません。

互換バンドルについては、現在のOpenClawは、レイアウトがOpenClawランタイムの想定と一致している場合に、バンドルメタデータに加えて、宣言された
skill root、Claude command root、Claude bundle の `settings.json` デフォルト、
Claude bundle LSPデフォルト、およびサポートされるhook packを読み取ります。

すべてのネイティブOpenClawプラグインは、**プラグインルート** に `openclaw.plugin.json` ファイルを **必ず** 含める必要があります。OpenClawはこのmanifestを使って、**プラグインコードを実行せずに** 設定を検証します。manifestが欠落している、または無効な場合はプラグインエラーとして扱われ、設定検証をブロックします。

完全なプラグインシステムガイドは [Plugins](/ja-JP/tools/plugin) を参照してください。
ネイティブのケーパビリティモデルと現在の外部互換性ガイダンスについては、
[Capability model](/ja-JP/plugins/architecture#public-capability-model) を参照してください。

## このファイルの役割

`openclaw.plugin.json` は、OpenClawがあなたの
プラグインコードを読み込む前に読むメタデータです。

用途:

- プラグインID
- 設定検証
- プラグインランタイムを起動せずに利用可能であるべき認証およびオンボーディングメタデータ
- プラグインランタイムの読み込み前に解決されるべきエイリアスおよび自動有効化メタデータ
- ランタイム読み込み前にプラグインを自動有効化すべき省略形モデルファミリー所有メタデータ
- バンドル互換配線と契約カバレッジに使用される静的ケーパビリティ所有スナップショット
- ランタイムを読み込まずにカタログおよび検証サーフェスへマージされるべきチャネル固有設定メタデータ
- 設定UIヒント

用途にしないもの:

- ランタイム動作の登録
- コードのentrypoint宣言
- npmインストールメタデータ

それらはプラグインコードおよび `package.json` に属します。

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

## より豊富な例

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

## トップレベルフィールドリファレンス

| Field                               | Required | Type                             | 意味                                                                                                                                                                                                         |
| ----------------------------------- | -------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `id`                                | Yes      | `string`                         | 正規のプラグインIDです。これは `plugins.entries.<id>` で使われるIDです。                                                                                                                                     |
| `configSchema`                      | Yes      | `object`                         | このプラグイン設定用のインラインJSON Schema。                                                                                                                                                                |
| `enabledByDefault`                  | No       | `true`                           | バンドル済みプラグインをデフォルトで有効としてマークします。デフォルトで無効のままにするには、省略するか、`true` 以外の値を設定します。                                                                    |
| `legacyPluginIds`                   | No       | `string[]`                       | この正規プラグインIDに正規化されるレガシーID。                                                                                                                                                               |
| `autoEnableWhenConfiguredProviders` | No       | `string[]`                       | 認証、設定、またはモデル参照がそれらに言及したときに、このプラグインを自動有効化すべきプロバイダーID。                                                                                                      |
| `kind`                              | No       | `"memory"` \| `"context-engine"` | `plugins.slots.*` で使用される排他的なプラグイン種別を宣言します。                                                                                                                                           |
| `channels`                          | No       | `string[]`                       | このプラグインが所有するチャネルID。検出と設定検証に使われます。                                                                                                                                             |
| `providers`                         | No       | `string[]`                       | このプラグインが所有するプロバイダーID。                                                                                                                                                                     |
| `modelSupport`                      | No       | `object`                         | ランタイム前にプラグインを自動読み込みするために使用される、manifest所有の省略形モデルファミリーメタデータ。                                                                                                 |
| `cliBackends`                       | No       | `string[]`                       | このプラグインが所有するCLI推論バックエンドID。明示的な設定参照からの起動時自動有効化に使われます。                                                                                                         |
| `providerAuthEnvVars`               | No       | `Record<string, string[]>`       | OpenClawがプラグインコードを読み込まずに検査できる、軽量なプロバイダー認証環境変数メタデータ。                                                                                                              |
| `channelEnvVars`                    | No       | `Record<string, string[]>`       | OpenClawがプラグインコードを読み込まずに検査できる、軽量なチャネル環境変数メタデータ。環境変数駆動のチャネル設定や、汎用的な起動/設定ヘルパーが認識すべき認証サーフェスに使用します。                    |
| `providerAuthChoices`               | No       | `object[]`                       | オンボーディングピッカー、preferred-provider解決、単純なCLIフラグ配線のための軽量な認証選択メタデータ。                                                                                                     |
| `contracts`                         | No       | `object`                         | speech、realtime transcription、realtime voice、media-understanding、image-generation、music-generation、video-generation、web-fetch、web search、およびツール所有権のための静的なバンドル済みケーパビリティスナップショット。 |
| `channelConfigs`                    | No       | `Record<string, object>`         | ランタイム読み込み前に検出および検証サーフェスへマージされる、manifest所有のチャネル設定メタデータ。                                                                                                        |
| `skills`                            | No       | `string[]`                       | 読み込むSkillディレクトリ。プラグインルートからの相対パス。                                                                                                                                                  |
| `name`                              | No       | `string`                         | 人が読めるプラグイン名。                                                                                                                                                                                     |
| `description`                       | No       | `string`                         | プラグインサーフェスに表示される短い要約。                                                                                                                                                                   |
| `version`                           | No       | `string`                         | 情報用のプラグインバージョン。                                                                                                                                                                               |
| `uiHints`                           | No       | `Record<string, object>`         | 設定フィールド用のUIラベル、プレースホルダー、機密性ヒント。                                                                                                                                                |

## providerAuthChoices リファレンス

各 `providerAuthChoices` エントリは、1つのオンボーディングまたは認証選択を記述します。
OpenClawはこれをプロバイダーランタイム読み込み前に読み取ります。

| Field                 | Required | Type                                            | 意味                                                                                                     |
| --------------------- | -------- | ----------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `provider`            | Yes      | `string`                                        | この選択が属するプロバイダーID。                                                                         |
| `method`              | Yes      | `string`                                        | ディスパッチ先の認証メソッドID。                                                                         |
| `choiceId`            | Yes      | `string`                                        | オンボーディングおよびCLIフローで使われる安定した認証選択ID。                                            |
| `choiceLabel`         | No       | `string`                                        | ユーザー向けラベル。省略時、OpenClawは `choiceId` にフォールバックします。                               |
| `choiceHint`          | No       | `string`                                        | ピッカー用の短い補助テキスト。                                                                           |
| `assistantPriority`   | No       | `number`                                        | assistant駆動の対話型ピッカーでは、値が小さいほど前に並びます。                                           |
| `assistantVisibility` | No       | `"visible"` \| `"manual-only"`                  | assistantピッカーからは非表示にしつつ、手動CLI選択は許可します。                                          |
| `deprecatedChoiceIds` | No       | `string[]`                                      | この置き換え先の選択へユーザーをリダイレクトすべきレガシーchoice id。                                     |
| `groupId`             | No       | `string`                                        | 関連する選択をグループ化するための任意のgroup id。                                                        |
| `groupLabel`          | No       | `string`                                        | そのグループのユーザー向けラベル。                                                                       |
| `groupHint`           | No       | `string`                                        | そのグループ用の短い補助テキスト。                                                                       |
| `optionKey`           | No       | `string`                                        | 単一フラグの単純な認証フロー用の内部オプションキー。                                                     |
| `cliFlag`             | No       | `string`                                        | `--openrouter-api-key` のようなCLIフラグ名。                                                             |
| `cliOption`           | No       | `string`                                        | `--openrouter-api-key <key>` のような完全なCLIオプション形。                                             |
| `cliDescription`      | No       | `string`                                        | CLIヘルプで使われる説明。                                                                                |
| `onboardingScopes`    | No       | `Array<"text-inference" \| "image-generation">` | この選択を表示すべきオンボーディングサーフェス。省略時は `["text-inference"]` がデフォルトです。         |

## uiHints リファレンス

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

各フィールドヒントには次を含められます:

| Field         | Type       | 意味                               |
| ------------- | ---------- | ---------------------------------- |
| `label`       | `string`   | ユーザー向けフィールドラベル。     |
| `help`        | `string`   | 短い補助テキスト。                 |
| `tags`        | `string[]` | 任意のUIタグ。                     |
| `advanced`    | `boolean`  | フィールドを高度な項目として扱います。 |
| `sensitive`   | `boolean`  | フィールドを秘密情報または機密情報として扱います。 |
| `placeholder` | `string`   | フォーム入力用のプレースホルダーテキスト。 |

## contracts リファレンス

`contracts` は、OpenClawがプラグインランタイムをインポートせずに
読み取れる静的なケーパビリティ所有メタデータにのみ使用してください。

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

各リストは任意です:

| Field                            | Type       | 意味                                                   |
| -------------------------------- | ---------- | ------------------------------------------------------ |
| `speechProviders`                | `string[]` | このプラグインが所有するspeech provider id。           |
| `realtimeTranscriptionProviders` | `string[]` | このプラグインが所有するrealtime-transcription provider id。 |
| `realtimeVoiceProviders`         | `string[]` | このプラグインが所有するrealtime-voice provider id。   |
| `mediaUnderstandingProviders`    | `string[]` | このプラグインが所有するmedia-understanding provider id。 |
| `imageGenerationProviders`       | `string[]` | このプラグインが所有するimage-generation provider id。 |
| `videoGenerationProviders`       | `string[]` | このプラグインが所有するvideo-generation provider id。 |
| `webFetchProviders`              | `string[]` | このプラグインが所有するweb-fetch provider id。        |
| `webSearchProviders`             | `string[]` | このプラグインが所有するweb-search provider id。       |
| `tools`                          | `string[]` | バンドル契約チェック用にこのプラグインが所有するagent tool名。 |

## channelConfigs リファレンス

`channelConfigs` は、チャネルプラグインがランタイム読み込み前に
軽量な設定メタデータを必要とする場合に使用します。

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

各チャネルエントリには次を含められます:

| Field         | Type                     | 意味                                                                                      |
| ------------- | ------------------------ | ----------------------------------------------------------------------------------------- |
| `schema`      | `object`                 | `channels.<id>` 用のJSON Schema。宣言された各チャネル設定エントリに必須です。            |
| `uiHints`     | `Record<string, object>` | そのチャネル設定セクション用の任意のUIラベル/プレースホルダー/機密性ヒント。             |
| `label`       | `string`                 | ランタイムメタデータが未準備のときに、pickerおよびinspectサーフェスへマージされるチャネルラベル。 |
| `description` | `string`                 | inspectおよびcatalogサーフェス向けの短いチャネル説明。                                   |
| `preferOver`  | `string[]`               | 選択サーフェスでこのチャネルが優先すべき、レガシーまたは低優先度のプラグインID。         |

## modelSupport リファレンス

`modelSupport` は、OpenClawが `gpt-5.4` や `claude-sonnet-4.6` のような
省略形モデルIDから、プラグインランタイム読み込み前にあなたのプロバイダープラグインを推測すべき場合に使用します。

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

OpenClawは次の優先順位を適用します:

- 明示的な `provider/model` 参照では、所有する `providers` manifestメタデータを使用します
- `modelPatterns` は `modelPrefixes` より優先されます
- バンドルされていないプラグインとバンドル済みプラグインの両方が一致する場合、バンドルされていないプラグインが優先されます
- 残る曖昧さは、ユーザーまたは設定がプロバイダーを指定するまで無視されます

フィールド:

| Field           | Type       | 意味                                                                 |
| --------------- | ---------- | -------------------------------------------------------------------- |
| `modelPrefixes` | `string[]` | 省略形モデルIDに対して `startsWith` で一致させるプレフィックス。     |
| `modelPatterns` | `string[]` | プロファイル接尾辞除去後の省略形モデルIDに対して一致させる正規表現ソース。 |

レガシーなトップレベルケーパビリティキーは非推奨です。`openclaw doctor --fix` を使って
`speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`,
`webFetchProviders`, および `webSearchProviders` を `contracts` の下へ
移動してください。通常のmanifest読み込みでは、これらのトップレベルフィールドを
ケーパビリティ所有権としてはもう扱いません。

## Manifest と package.json の違い

この2つのファイルは異なる役割を持ちます:

| File                   | 用途                                                                                                                                    |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.plugin.json` | 検出、設定検証、auth-choiceメタデータ、およびプラグインコード実行前に存在しなければならないUIヒント                                    |
| `package.json`         | npmメタデータ、依存関係のインストール、およびentrypoint、インストール制御、セットアップ、またはcatalogメタデータに使用される `openclaw` ブロック |

どこに置くべきメタデータか迷った場合は、次のルールを使ってください:

- OpenClawがプラグインコードを読み込む前に知っている必要があるなら、`openclaw.plugin.json` に入れます
- パッケージ化、entry file、またはnpmインストール動作に関するものなら、`package.json` に入れます

### 検出に影響する package.json フィールド

一部のランタイム前プラグインメタデータは、`openclaw.plugin.json` ではなく
`package.json` の `openclaw` ブロックに意図的に置かれます。

重要な例:

| Field                                                             | 意味                                                                                                                                         |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                             | ネイティブプラグインentrypointを宣言します。                                                                                                 |
| `openclaw.setupEntry`                                             | オンボーディングおよび遅延チャネル起動中に使われる、軽量なセットアップ専用entrypoint。                                                      |
| `openclaw.channel`                                                | ラベル、ドキュメントパス、エイリアス、選択用コピーなどの軽量チャネルcatalogメタデータ。                                                    |
| `openclaw.channel.configuredState`                                | 「環境変数のみのセットアップがすでに存在するか」を完全なチャネルランタイムを読み込まずに判定できる、軽量なconfigured-state checkerメタデータ。 |
| `openclaw.channel.persistedAuthState`                             | 「すでに何かサインイン済みか」を完全なチャネルランタイムを読み込まずに判定できる、軽量なpersisted-auth checkerメタデータ。                 |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | バンドル済みおよび外部公開プラグイン向けのインストール/更新ヒント。                                                                         |
| `openclaw.install.defaultChoice`                                  | 複数のインストール元がある場合の優先インストールパス。                                                                                      |
| `openclaw.install.minHostVersion`                                 | `>=2026.3.22` のようなsemver下限を使った、サポートされる最小OpenClawホストバージョン。                                                     |
| `openclaw.install.allowInvalidConfigRecovery`                     | 設定が無効な場合の限定的なバンドル済みプラグイン再インストール回復パスを許可します。                                                       |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | 起動中にフルチャネルプラグインより前に、セットアップ専用チャネルサーフェスを読み込めるようにします。                                       |

`openclaw.install.minHostVersion` は、インストール時およびmanifest
レジストリ読み込み時に強制されます。無効な値は拒否されます。有効だが新しすぎる値は、古いホストではそのプラグインをスキップします。

`openclaw.install.allowInvalidConfigRecovery` は意図的に限定的です。
これは任意の壊れた設定をインストール可能にするものではありません。現在は、欠落したバンドル済みプラグインパスや、その同じバンドル済みプラグインに対する古い `channels.<id>` エントリのような、特定の古いバンドル済みプラグイン更新失敗からのインストールフロー回復のみを許可します。無関係な設定エラーは引き続きインストールをブロックし、運用者に `openclaw doctor --fix` を案内します。

`openclaw.channel.persistedAuthState` は、小さなchecker
モジュールのためのpackageメタデータです:

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

セットアップ、doctor、またはconfigured-stateフローで、フルチャネルプラグイン読み込み前に軽量な yes/no の認証プローブが必要な場合に使用します。対象のexportは、永続化状態のみを読む小さな関数にしてください。フルチャネルランタイムbarrelを経由させないでください。

`openclaw.channel.configuredState` も同じ形で、軽量な環境変数のみの
configured check に使われます:

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

チャネルが、環境変数やその他の小さな非ランタイム入力からconfigured-stateを判定できる場合に使用します。チェックに完全な設定解決や実際の
チャネルランタイムが必要な場合は、そのロジックを代わりにプラグインの `config.hasConfiguredState`
hook に置いてください。

## JSON Schema 要件

- **すべてのプラグインはJSON Schemaを必ず含める必要があります**。設定を受け付けない場合でも同様です。
- 空のスキーマでも許容されます（例: `{ "type": "object", "additionalProperties": false }`）。
- スキーマはランタイム時ではなく、設定の読み取り/書き込み時に検証されます。

## 検証動作

- 不明な `channels.*` キーは **エラー** です。ただし、そのチャネルIDが
  プラグインmanifestで宣言されている場合を除きます。
- `plugins.entries.<id>`, `plugins.allow`, `plugins.deny`, および `plugins.slots.*`
  は、**検出可能な** プラグインIDを参照しなければなりません。不明なIDは **エラー** です。
- プラグインがインストール済みでも、manifestまたはスキーマが壊れている、または欠落している場合、
  検証は失敗し、Doctorがそのプラグインエラーを報告します。
- プラグイン設定が存在しても、プラグインが **無効** の場合、その設定は保持され、
  **警告** がDoctor + ログに表示されます。

完全な `plugins.*` スキーマについては [Configuration reference](/ja-JP/gateway/configuration) を参照してください。

## 注記

- manifestは、ローカルファイルシステム読み込みを含む **ネイティブOpenClawプラグインでは必須** です。
- ランタイムは引き続きプラグインモジュールを別途読み込みます。manifestは
  検出 + 検証専用です。
- ネイティブmanifestはJSON5で解析されるため、最終的な値がオブジェクトである限り、
  コメント、末尾カンマ、クォートなしキーを使用できます。
- manifestローダーが読み取るのは文書化されたmanifestフィールドのみです。ここに
  カスタムのトップレベルキーを追加するのは避けてください。
- `providerAuthEnvVars` は、認証プローブ、env-marker
  検証、および環境変数名を調べるだけのためにプラグインランタイムを起動すべきでない類似のprovider-authサーフェス向けの軽量メタデータパスです。
- `channelEnvVars` は、shell-envフォールバック、セットアップ
  プロンプト、および環境変数名を調べるだけのためにチャネルランタイムを起動すべきでない類似のチャネルサーフェス向けの軽量メタデータパスです。
- `providerAuthChoices` は、auth-choiceピッカー、
  `--auth-choice` 解決、preferred-providerマッピング、およびプロバイダーランタイム読み込み前の単純なオンボーディング
  CLIフラグ登録向けの軽量メタデータパスです。プロバイダーコードが必要なランタイム
  wizardメタデータについては、
  [Provider runtime hooks](/ja-JP/plugins/architecture#provider-runtime-hooks) を参照してください。
- 排他的プラグイン種別は `plugins.slots.*` を通じて選択されます。
  - `kind: "memory"` は `plugins.slots.memory` で選択されます。
  - `kind: "context-engine"` は `plugins.slots.contextEngine`
    で選択されます（デフォルト: 組み込み `legacy`）。
- `channels`, `providers`, `cliBackends`, および `skills` は、
  プラグインで不要な場合は省略できます。
- プラグインがネイティブモジュールに依存する場合は、ビルド手順と
  必要なパッケージマネージャー許可リスト要件（例: pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`）を文書化してください。

## 関連

- [Building Plugins](/ja-JP/plugins/building-plugins) — プラグインのはじめに
- [Plugin Architecture](/ja-JP/plugins/architecture) — 内部アーキテクチャ
- [SDK Overview](/ja-JP/plugins/sdk-overview) — Plugin SDKリファレンス
