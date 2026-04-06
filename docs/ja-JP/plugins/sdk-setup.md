---
read_when:
    - プラグインにセットアップウィザードを追加している
    - setup-entry.tsとindex.tsの違いを理解する必要がある
    - プラグイン設定スキーマまたはpackage.jsonのopenclawメタデータを定義している
sidebarTitle: Setup and Config
summary: セットアップウィザード、setup-entry.ts、設定スキーマ、およびpackage.jsonメタデータ
title: プラグインのセットアップと設定
x-i18n:
    generated_at: "2026-04-06T03:11:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: eac2586516d27bcd94cc4c259fe6274c792b3f9938c7ddd6dbf04a6dbb988dc9
    source_path: plugins/sdk-setup.md
    workflow: 15
---

# プラグインのセットアップと設定

プラグインパッケージング（`package.json`メタデータ）、マニフェスト
（`openclaw.plugin.json`）、セットアップエントリー、および設定スキーマのリファレンスです。

<Tip>
  **手順ガイドを探していますか?** パッケージングを文脈付きで説明するハウツーガイドは次を参照してください:
  [Channel Plugins](/ja-JP/plugins/sdk-channel-plugins#step-1-package-and-manifest) と
  [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins#step-1-package-and-manifest)。
</Tip>

## パッケージメタデータ

プラグインシステムにプラグインが何を提供するかを伝えるため、`package.json`には`openclaw`フィールドが必要です。

**チャネルプラグイン:**

```json
{
  "name": "@myorg/openclaw-my-channel",
  "version": "1.0.0",
  "type": "module",
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "channel": {
      "id": "my-channel",
      "label": "My Channel",
      "blurb": "Short description of the channel."
    }
  }
}
```

**プロバイダープラグイン / ClawHub公開ベースライン:**

```json openclaw-clawhub-package.json
{
  "name": "@myorg/openclaw-my-plugin",
  "version": "1.0.0",
  "type": "module",
  "openclaw": {
    "extensions": ["./index.ts"],
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

プラグインをClawHubで外部公開する場合、これらの`compat`フィールドと`build`
フィールドは必須です。正式な公開用スニペットは
`docs/snippets/plugin-publish/`にあります。

### `openclaw`フィールド

| Field        | Type       | Description                                                                                              |
| ------------ | ---------- | -------------------------------------------------------------------------------------------------------- |
| `extensions` | `string[]` | エントリーポイントファイル（パッケージルートからの相対パス）                                             |
| `setupEntry` | `string`   | 軽量なセットアップ専用エントリー（任意）                                                                 |
| `channel`    | `object`   | セットアップ、ピッカー、クイックスタート、およびステータス画面向けのチャネルカタログメタデータ          |
| `providers`  | `string[]` | このプラグインが登録するプロバイダーid                                                                   |
| `install`    | `object`   | インストールヒント: `npmSpec`, `localPath`, `defaultChoice`, `minHostVersion`, `allowInvalidConfigRecovery` |
| `startup`    | `object`   | 起動時の動作フラグ                                                                                       |

### `openclaw.channel`

`openclaw.channel`は、ランタイム読み込み前のチャネル検出およびセットアップ画面向けの軽量なパッケージメタデータです。

| Field                                  | Type       | What it means                                                           |
| -------------------------------------- | ---------- | ----------------------------------------------------------------------- |
| `id`                                   | `string`   | 正式なチャネルid。                                                      |
| `label`                                | `string`   | 主チャネルラベル。                                                      |
| `selectionLabel`                       | `string`   | `label`と異なるべき場合のピッカー/セットアップ用ラベル。               |
| `detailLabel`                          | `string`   | より豊かなチャネルカタログおよびステータス画面向けの補助詳細ラベル。   |
| `docsPath`                             | `string`   | セットアップおよび選択リンク用のドキュメントパス。                     |
| `docsLabel`                            | `string`   | チャネルidと異なるべき場合にドキュメントリンクで使う上書きラベル。     |
| `blurb`                                | `string`   | 短いオンボーディング/カタログ説明。                                     |
| `order`                                | `number`   | チャネルカタログでの並び順。                                            |
| `aliases`                              | `string[]` | チャネル選択用の追加参照エイリアス。                                    |
| `preferOver`                           | `string[]` | このチャネルが上位に来るべき低優先度のプラグイン/チャネルid。           |
| `systemImage`                          | `string`   | チャネルUIカタログ用の任意のアイコン/system-image名。                   |
| `selectionDocsPrefix`                  | `string`   | 選択画面でのドキュメントリンク前に置く接頭辞テキスト。                  |
| `selectionDocsOmitLabel`               | `boolean`  | ラベル付きドキュメントリンクの代わりにドキュメントパスを直接表示する。  |
| `selectionExtras`                      | `string[]` | 選択文言に追加される短い文字列。                                        |
| `markdownCapable`                      | `boolean`  | 送信書式判断で、このチャネルをMarkdown対応として扱います。              |
| `exposure`                             | `object`   | セットアップ、設定済み一覧、およびドキュメント画面向けの可視性制御。    |
| `quickstartAllowFrom`                  | `boolean`  | このチャネルを標準クイックスタート`allowFrom`セットアップフローに含めます。 |
| `forceAccountBinding`                  | `boolean`  | アカウントが1つしかない場合でも、明示的なアカウントバインディングを要求します。 |
| `preferSessionLookupForAnnounceTarget` | `boolean`  | このチャネルの通知先解決でセッション検索を優先します。                  |

例:

```json
{
  "openclaw": {
    "channel": {
      "id": "my-channel",
      "label": "My Channel",
      "selectionLabel": "My Channel (self-hosted)",
      "detailLabel": "My Channel Bot",
      "docsPath": "/channels/my-channel",
      "docsLabel": "my-channel",
      "blurb": "Webhook-based self-hosted chat integration.",
      "order": 80,
      "aliases": ["mc"],
      "preferOver": ["my-channel-legacy"],
      "selectionDocsPrefix": "Guide:",
      "selectionExtras": ["Markdown"],
      "markdownCapable": true,
      "exposure": {
        "configured": true,
        "setup": true,
        "docs": true
      },
      "quickstartAllowFrom": true
    }
  }
}
```

`exposure`は次をサポートします。

- `configured`: 設定済み/ステータス系の一覧画面にそのチャネルを含める
- `setup`: 対話型セットアップ/設定ピッカーにそのチャネルを含める
- `docs`: ドキュメント/ナビゲーション画面でそのチャネルを公開向けとして扱う

`showConfigured`と`showInSetup`は、レガシーエイリアスとして引き続きサポートされます。`exposure`を推奨します。

### `openclaw.install`

`openclaw.install`はマニフェストメタデータではなく、パッケージメタデータです。

| Field                        | Type                 | What it means                                                                    |
| ---------------------------- | -------------------- | -------------------------------------------------------------------------------- |
| `npmSpec`                    | `string`             | インストール/更新フロー用の正式なnpm spec。                                      |
| `localPath`                  | `string`             | ローカル開発またはバンドルインストールパス。                                     |
| `defaultChoice`              | `"npm"` \| `"local"` | 両方利用可能な場合の優先インストール元。                                         |
| `minHostVersion`             | `string`             | `>=x.y.z`形式での最小サポートOpenClawバージョン。                                |
| `allowInvalidConfigRecovery` | `boolean`            | 特定の古い設定失敗からバンドルプラグイン再インストールフローが回復できるようにします。 |

`minHostVersion`が設定されている場合、インストールとマニフェストレジストリ読み込みの両方で強制されます。
古いホストではプラグインはスキップされ、無効なバージョン文字列は拒否されます。

`allowInvalidConfigRecovery`は壊れた設定全般を回避するものではありません。
これは限定的なバンドルプラグイン回復専用であり、再インストール/セットアップが、欠落したバンドルプラグインパスや、その同じプラグインに対する古い`channels.<id>`エントリーのような既知のアップグレード残骸を修復できるようにするためのものです。無関係な理由で設定が壊れている場合、インストールは引き続きフェイルクローズし、オペレーターに`openclaw doctor --fix`の実行を案内します。

### 完全読み込みの遅延

チャネルプラグインは、次の設定で遅延読み込みにオプトインできます。

```json
{
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "startup": {
      "deferConfiguredChannelFullLoadUntilAfterListen": true
    }
  }
}
```

有効にすると、OpenClawはlisten前の起動フェーズでは、すでに設定済みのチャネルに対しても`setupEntry`だけを読み込みます。完全なエントリーはGatewayがlistenを開始した後に読み込まれます。

<Warning>
  遅延読み込みを有効にするのは、`setupEntry`がGatewayがlisten開始前に必要とするすべて（チャネル登録、HTTPルート、Gatewayメソッド）を登録している場合だけにしてください。完全なエントリーが必要な起動capabilityを所有している場合は、デフォルト動作のままにしてください。
</Warning>

セットアップ/完全エントリーがGateway RPCメソッドを登録する場合は、プラグイン固有の接頭辞を維持してください。予約済みのコア管理名前空間（`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`）は引き続きコア所有であり、常に
`operator.admin`へ解決されます。

## プラグインマニフェスト

すべてのネイティブプラグインは、パッケージルートに`openclaw.plugin.json`を必ず含める必要があります。
OpenClawはこれを使って、プラグインコードを実行せずに設定を検証します。

```json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "description": "Adds My Plugin capabilities to OpenClaw",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "webhookSecret": {
        "type": "string",
        "description": "Webhook verification secret"
      }
    }
  }
}
```

チャネルプラグインでは、`kind`と`channels`を追加します。

```json
{
  "id": "my-channel",
  "kind": "channel",
  "channels": ["my-channel"],
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
```

設定がないプラグインでもスキーマは必須です。空のスキーマも有効です。

```json
{
  "id": "my-plugin",
  "configSchema": {
    "type": "object",
    "additionalProperties": false
  }
}
```

完全なスキーマリファレンスについては[Plugin Manifest](/ja-JP/plugins/manifest)を参照してください。

## ClawHub公開

プラグインパッケージには、パッケージ固有のClawHubコマンドを使ってください。

```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
```

従来のskill専用公開エイリアスはSkills用です。プラグインパッケージでは常に
`clawhub package publish`を使用してください。

## セットアップエントリー

`setup-entry.ts`ファイルは、セットアップ画面のみ（オンボーディング、設定修復、
無効化されたチャネルの検査）が必要なときにOpenClawが読み込む、`index.ts`の軽量な代替です。

```typescript
// setup-entry.ts
import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";
import { myChannelPlugin } from "./src/channel.js";

export default defineSetupPluginEntry(myChannelPlugin);
```

これにより、セットアップフロー中に重いランタイムコード（暗号ライブラリ、CLI登録、
バックグラウンドサービス）を読み込まずに済みます。

**OpenClawが完全なエントリーの代わりに`setupEntry`を使う場面:**

- チャネルは無効だが、セットアップ/オンボーディング画面が必要
- チャネルは有効だが未設定
- 遅延読み込みが有効（`deferConfiguredChannelFullLoadUntilAfterListen`）

**`setupEntry`が登録しなければならないもの:**

- チャネルプラグインオブジェクト（`defineSetupPluginEntry`経由）
- Gatewayのlisten前に必要なHTTPルート
- 起動中に必要なGatewayメソッド

これらの起動時Gatewayメソッドでも、`config.*`や`update.*`のような予約済みコア管理名前空間は避ける必要があります。

**`setupEntry`に含めるべきでないもの:**

- CLI登録
- バックグラウンドサービス
- 重いランタイムimport（crypto、SDK）
- 起動後にのみ必要なGatewayメソッド

### 狭いセットアップヘルパーimport

セットアップ専用のホットパスでは、セットアップ画面の一部だけが必要な場合、より広い
`plugin-sdk/setup`アンブレラではなく、狭いセットアップヘルパー境界を優先してください。

| Import path                        | Use it for                                                                                | Key exports                                                                                                                                                                                                                                                                                  |
| ---------------------------------- | ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/setup-runtime`         | `setupEntry` / 遅延チャネル起動でも利用可能なセットアップ時ランタイムヘルパー             | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
| `plugin-sdk/setup-adapter-runtime` | 環境認識型アカウントセットアップアダプター                                                | `createEnvPatchedAccountSetupAdapter`                                                                                                                                                                                                                                                        |
| `plugin-sdk/setup-tools`           | セットアップ/インストールCLI/アーカイブ/ドキュメントヘルパー                              | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR`                                                                                                                                                                                |

設定パッチヘルパー（`moveSingleAccountChannelSectionToDefaultAccount(...)`など）を含む完全な共有セットアップツールボックスが必要な場合は、より広い
`plugin-sdk/setup`境界を使用してください。

セットアップパッチアダプターは、import時にもホットパス安全性を維持します。バンドルされた単一アカウント昇格契約サーフェス検索は遅延評価されるため、`plugin-sdk/setup-runtime`をimportしても、アダプターが実際に使われる前にバンドル契約サーフェス検出を先行ロードしません。

### チャネル所有の単一アカウント昇格

チャネルが単一アカウントのトップレベル設定から
`channels.<id>.accounts.*`へアップグレードする際、共有のデフォルト動作では、昇格されたアカウントスコープ値を`accounts.default`へ移動します。

バンドルされたチャネルは、そのセットアップ契約サーフェスを通じてこの昇格を絞り込むか上書きできます。

- `singleAccountKeysToMove`: 昇格されたアカウントへ移動すべき追加のトップレベルキー
- `namedAccountPromotionKeys`: 名前付きアカウントがすでに存在する場合、これらのキーだけが昇格先アカウントへ移動し、共有ポリシー/配信キーはチャネルルートに残る
- `resolveSingleAccountPromotionTarget(...)`: どの既存アカウントが昇格値を受け取るかを選択

現在のバンドル例はMatrixです。既存の名前付きMatrixアカウントがちょうど1つある場合、または`defaultAccount`が`Ops`のような既存の非標準キーを指している場合、昇格では新しい`accounts.default`エントリーを作らず、そのアカウントを保持します。

## 設定スキーマ

プラグイン設定は、マニフェスト内のJSON Schemaに対して検証されます。ユーザーは次のようにプラグインを設定します。

```json5
{
  plugins: {
    entries: {
      "my-plugin": {
        config: {
          webhookSecret: "abc123",
        },
      },
    },
  },
}
```

プラグインは、登録中にこの設定を`api.pluginConfig`として受け取ります。

チャネル固有の設定には、代わりにチャネル設定セクションを使ってください。

```json5
{
  channels: {
    "my-channel": {
      token: "bot-token",
      allowFrom: ["user1", "user2"],
    },
  },
}
```

### チャネル設定スキーマの構築

`openclaw/plugin-sdk/core`の`buildChannelConfigSchema`を使うと、
Zodスキーマを、OpenClawが検証する`ChannelConfigSchema`ラッパーへ変換できます。

```typescript
import { z } from "zod";
import { buildChannelConfigSchema } from "openclaw/plugin-sdk/core";

const accountSchema = z.object({
  token: z.string().optional(),
  allowFrom: z.array(z.string()).optional(),
  accounts: z.object({}).catchall(z.any()).optional(),
  defaultAccount: z.string().optional(),
});

const configSchema = buildChannelConfigSchema(accountSchema);
```

## セットアップウィザード

チャネルプラグインは、`openclaw onboard`向けに対話型セットアップウィザードを提供できます。
ウィザードは`ChannelPlugin`上の`ChannelSetupWizard`オブジェクトです。

```typescript
import type { ChannelSetupWizard } from "openclaw/plugin-sdk/channel-setup";

const setupWizard: ChannelSetupWizard = {
  channel: "my-channel",
  status: {
    configuredLabel: "Connected",
    unconfiguredLabel: "Not configured",
    resolveConfigured: ({ cfg }) => Boolean((cfg.channels as any)?.["my-channel"]?.token),
  },
  credentials: [
    {
      inputKey: "token",
      providerHint: "my-channel",
      credentialLabel: "Bot token",
      preferredEnvVar: "MY_CHANNEL_BOT_TOKEN",
      envPrompt: "Use MY_CHANNEL_BOT_TOKEN from environment?",
      keepPrompt: "Keep current token?",
      inputPrompt: "Enter your bot token:",
      inspect: ({ cfg, accountId }) => {
        const token = (cfg.channels as any)?.["my-channel"]?.token;
        return {
          accountConfigured: Boolean(token),
          hasConfiguredValue: Boolean(token),
        };
      },
    },
  ],
};
```

`ChannelSetupWizard`型は、`credentials`, `textInputs`,
`dmPolicy`, `allowFrom`, `groupAccess`, `prepare`, `finalize`などをサポートします。
完全な例については、バンドルされたプラグインパッケージ（たとえばDiscordプラグインの`src/channel.setup.ts`）を参照してください。

標準的な
`note -> prompt -> parse -> merge -> patch`フローだけが必要なDM許可リストプロンプトには、`openclaw/plugin-sdk/setup`の共有セットアップヘルパー
`createPromptParsedAllowFromForAccount(...)`,
`createTopLevelChannelParsedAllowFromPrompt(...)`, および
`createNestedChannelParsedAllowFromPrompt(...)`を優先してください。

ラベル、スコア、および任意の追加行だけが異なるチャネルセットアップステータスブロックには、各プラグインで同じ`status`オブジェクトを手作業で作る代わりに、
`openclaw/plugin-sdk/setup`の`createStandardChannelSetupStatus(...)`を優先してください。

特定の文脈でのみ表示すべき任意セットアップ画面には、
`openclaw/plugin-sdk/channel-setup`の`createOptionalChannelSetupSurface`を使ってください。

```typescript
import { createOptionalChannelSetupSurface } from "openclaw/plugin-sdk/channel-setup";

const setupSurface = createOptionalChannelSetupSurface({
  channel: "my-channel",
  label: "My Channel",
  npmSpec: "@myorg/openclaw-my-channel",
  docsPath: "/channels/my-channel",
});
// { setupAdapter, setupWizard } を返します
```

`plugin-sdk/channel-setup`は、任意インストール画面の片側だけが必要な場合のために、より低レベルの
`createOptionalChannelSetupAdapter(...)`および
`createOptionalChannelSetupWizard(...)`ビルダーも公開しています。

生成される任意アダプター/ウィザードは、実際の設定書き込みではフェイルクローズします。`validateInput`,
`applyAccountConfig`, および `finalize` の間で1つの共通インストール必須メッセージを再利用し、`docsPath`が設定されていればドキュメントリンクを追加します。

バイナリ依存のセットアップUIでは、同じバイナリ/ステータス接着コードを各チャネルへ複製する代わりに、共有の委譲ヘルパーを優先してください。

- `createDetectedBinaryStatus(...)`: ラベル、ヒント、スコア、およびバイナリ検出だけが異なるステータスブロック向け
- `createCliPathTextInput(...)`: パスベースのテキスト入力向け
- `createDelegatedSetupWizardStatusResolvers(...)`,
  `createDelegatedPrepare(...)`, `createDelegatedFinalize(...)`, および
  `createDelegatedResolveConfigured(...)`: `setupEntry`がより重い完全ウィザードへ遅延的に転送する必要がある場合
- `createDelegatedTextInputShouldPrompt(...)`: `setupEntry`が`textInputs[*].shouldPrompt`判定だけを委譲する必要がある場合

## 公開とインストール

**外部プラグイン:** [ClawHub](/ja-JP/tools/clawhub)またはnpmへ公開してから、次のようにインストールします。

```bash
openclaw plugins install @myorg/openclaw-my-plugin
```

OpenClawは最初にClawHubを試し、自動的にnpmへフォールバックします。ClawHubを明示的に強制することもできます。

```bash
openclaw plugins install clawhub:@myorg/openclaw-my-plugin   # ClawHubのみ
```

対応する`npm:`上書きはありません。ClawHubフォールバック後にnpm経路を使いたい場合は、通常のnpmパッケージspecを使ってください。

```bash
openclaw plugins install @myorg/openclaw-my-plugin
```

**リポジトリ内プラグイン:** バンドルされたプラグインワークスペースツリー配下に置くと、ビルド中に自動検出されます。

**ユーザーがインストールできる形式:**

```bash
openclaw plugins install <package-name>
```

<Info>
  npm由来のインストールでは、`openclaw plugins install`は
  `npm install --ignore-scripts`（ライフサイクルスクリプトなし）を実行します。プラグイン依存ツリーは純粋なJS/TSに保ち、`postinstall`ビルドを必要とするパッケージは避けてください。
</Info>

## 関連

- [SDK Entry Points](/ja-JP/plugins/sdk-entrypoints) -- `definePluginEntry`および`defineChannelPluginEntry`
- [Plugin Manifest](/ja-JP/plugins/manifest) -- 完全なマニフェストスキーマリファレンス
- [Building Plugins](/ja-JP/plugins/building-plugins) -- ステップごとの導入ガイド
