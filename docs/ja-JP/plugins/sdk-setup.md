---
read_when:
    - Plugin にセットアップ ウィザードを追加しています
    - '`setup-entry.ts` と `index.ts` の違いを理解する必要があります'
    - Plugin の設定スキーマまたは `package.json` の openclaw メタデータを定義しています
sidebarTitle: Setup and Config
summary: セットアップ ウィザード、setup-entry.ts、設定スキーマ、package.json メタデータ
title: Plugin セットアップと設定
x-i18n:
    generated_at: "2026-04-15T19:41:42Z"
    model: gpt-5.4
    provider: openai
    source_hash: ddf28e25e381a4a38ac478e531586f59612e1a278732597375f87c2eeefc521b
    source_path: plugins/sdk-setup.md
    workflow: 15
---

# Plugin セットアップと設定

Plugin パッケージング（`package.json` メタデータ）、マニフェスト
（`openclaw.plugin.json`）、セットアップ エントリ、設定スキーマのリファレンスです。

<Tip>
  **手順を追った説明を探していますか？** ハウツー ガイドでは、パッケージングを文脈の中で扱っています：
  [Channel Plugins](/ja-JP/plugins/sdk-channel-plugins#step-1-package-and-manifest) と
  [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins#step-1-package-and-manifest)。
</Tip>

## パッケージ メタデータ

`package.json` には、Plugin システムにこの Plugin が何を提供するかを伝える
`openclaw` フィールドが必要です。

**Channel Plugin:**

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

**Provider Plugin / ClawHub 公開ベースライン:**

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

Plugin を ClawHub で外部公開する場合、これらの `compat` フィールドと `build`
フィールドは必須です。正式な公開用スニペットは
`docs/snippets/plugin-publish/` にあります。

### `openclaw` フィールド

| フィールド | 型         | 説明                                                                                                   |
| ---------- | ---------- | ------------------------------------------------------------------------------------------------------ |
| `extensions` | `string[]` | エントリ ポイント ファイル（パッケージ ルートからの相対パス）                                         |
| `setupEntry` | `string`   | 軽量なセットアップ専用エントリ（任意）                                                                 |
| `channel`    | `object`   | セットアップ、ピッカー、クイックスタート、ステータス画面向けの Channel カタログ メタデータ            |
| `providers`  | `string[]` | この Plugin によって登録される Provider ID                                                             |
| `install`    | `object`   | インストール ヒント: `npmSpec`, `localPath`, `defaultChoice`, `minHostVersion`, `allowInvalidConfigRecovery` |
| `startup`    | `object`   | 起動時の動作フラグ                                                                                     |

### `openclaw.channel`

`openclaw.channel` は、ランタイムが読み込まれる前に Channel の検出とセットアップ画面で使われる、
低コストなパッケージ メタデータです。

| フィールド                               | 型         | 意味                                                                          |
| ---------------------------------------- | ---------- | ----------------------------------------------------------------------------- |
| `id`                                     | `string`   | 正式な Channel ID。                                                           |
| `label`                                  | `string`   | 主要な Channel ラベル。                                                       |
| `selectionLabel`                         | `string`   | `label` と異なる必要がある場合の、ピッカー/セットアップ用ラベル。            |
| `detailLabel`                            | `string`   | より充実した Channel カタログやステータス画面向けの補助ラベル。               |
| `docsPath`                               | `string`   | セットアップや選択リンク用のドキュメント パス。                               |
| `docsLabel`                              | `string`   | Channel ID と異なる必要がある場合に、ドキュメント リンクで使う上書きラベル。  |
| `blurb`                                  | `string`   | 短いオンボーディング/カタログ説明。                                           |
| `order`                                  | `number`   | Channel カタログでの並び順。                                                  |
| `aliases`                                | `string[]` | Channel 選択用の追加の検索別名。                                              |
| `preferOver`                             | `string[]` | この Channel が優先されるべき、より優先度の低い Plugin/Channel ID。           |
| `systemImage`                            | `string`   | Channel UI カタログ用の任意のアイコン/system-image 名。                       |
| `selectionDocsPrefix`                    | `string`   | 選択画面でドキュメント リンクの前に付ける接頭辞テキスト。                     |
| `selectionDocsOmitLabel`                 | `boolean`  | ラベル付きのドキュメント リンクではなく、ドキュメント パスを直接表示します。  |
| `selectionExtras`                        | `string[]` | 選択テキストに追加される短い追加文字列。                                      |
| `markdownCapable`                        | `boolean`  | 送信時の書式設定判断のため、この Channel が Markdown 対応であることを示します。 |
| `exposure`                               | `object`   | セットアップ、設定済み一覧、ドキュメント画面向けの Channel 表示制御。          |
| `quickstartAllowFrom`                    | `boolean`  | この Channel を標準のクイックスタート `allowFrom` セットアップ フローに含めます。 |
| `forceAccountBinding`                    | `boolean`  | アカウントが 1 つしかない場合でも、明示的なアカウント バインディングを必須にします。 |
| `preferSessionLookupForAnnounceTarget`   | `boolean`  | この Channel の告知先解決時に、セッション検索を優先します。                   |

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

`exposure` では以下をサポートします。

- `configured`: 設定済み/ステータス形式の一覧画面に Channel を含める
- `setup`: 対話型のセットアップ/設定ピッカーに Channel を含める
- `docs`: ドキュメント/ナビゲーション画面で Channel を公開対象として扱う

`showConfigured` と `showInSetup` もレガシー エイリアスとして引き続きサポートされます。  
`exposure` を優先してください。

### `openclaw.install`

`openclaw.install` はマニフェスト メタデータではなく、パッケージ メタデータです。

| フィールド                   | 型                   | 意味                                                                             |
| ---------------------------- | -------------------- | -------------------------------------------------------------------------------- |
| `npmSpec`                    | `string`             | インストール/更新フローで使う正式な npm spec。                                   |
| `localPath`                  | `string`             | ローカル開発用またはバンドル済みインストール パス。                              |
| `defaultChoice`              | `"npm"` \| `"local"` | 両方利用可能な場合の推奨インストール元。                                         |
| `minHostVersion`             | `string`             | `>=x.y.z` 形式で表す、サポートされる最小 OpenClaw バージョン。                   |
| `allowInvalidConfigRecovery` | `boolean`            | バンドル済み Plugin の再インストール フローで、特定の古い設定不整合からの回復を許可します。 |

`minHostVersion` が設定されている場合、インストール時とマニフェスト レジストリ読み込み時の両方で
それが適用されます。古いホストはその Plugin をスキップし、不正なバージョン文字列は拒否されます。

`allowInvalidConfigRecovery` は、壊れた設定全般に対する一般的なバイパスではありません。  
これは、同じ Plugin に対応するバンドル済み Plugin パスの欠落や古い `channels.<id>`
エントリのような、既知のアップグレード残骸を再インストール/セットアップで修復できるようにする、
限定的なバンドル済み Plugin 回復専用です。無関係な理由で設定が壊れている場合、
インストールは引き続き安全側で失敗し、オペレーターに `openclaw doctor --fix` の実行を案内します。

### 完全ロードの遅延

Channel Plugin は、以下のように遅延読み込みを有効にできます。

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

これを有効にすると、OpenClaw は、すでに設定済みの Channel であっても、
リッスン開始前の起動フェーズでは `setupEntry` のみを読み込みます。完全なエントリは
Gateway がリッスンを開始した後に読み込まれます。

<Warning>
  遅延読み込みを有効にするのは、`setupEntry` が Gateway のリッスン開始前に必要なすべて
  （Channel 登録、HTTP ルート、Gateway メソッド）を登録する場合に限ってください。
  必要な起動機能を完全なエントリが担っている場合は、デフォルトの動作を維持してください。
</Warning>

セットアップ エントリまたは完全エントリで Gateway RPC メソッドを登録する場合は、
Plugin 固有の接頭辞を付けてください。予約済みのコア管理名前空間（`config.*`、
`exec.approvals.*`, `wizard.*`, `update.*`）はコア側の所有のままであり、常に
`operator.admin` に解決されます。

## Plugin マニフェスト

すべてのネイティブ Plugin は、パッケージ ルートに `openclaw.plugin.json` を含める必要があります。  
OpenClaw はこれを使って、Plugin コードを実行せずに設定を検証します。

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

Channel Plugin の場合は、`kind` と `channels` を追加します。

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

設定を持たない Plugin でも、スキーマを含める必要があります。空のスキーマも有効です。

```json
{
  "id": "my-plugin",
  "configSchema": {
    "type": "object",
    "additionalProperties": false
  }
}
```

完全なスキーマ リファレンスについては、[Plugin Manifest](/ja-JP/plugins/manifest) を参照してください。

## ClawHub 公開

Plugin パッケージでは、パッケージ専用の ClawHub コマンドを使用します。

```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
```

旧来の skill 専用公開エイリアスは Skills 用です。Plugin パッケージでは、
常に `clawhub package publish` を使用してください。

## セットアップ エントリ

`setup-entry.ts` ファイルは `index.ts` の軽量な代替で、OpenClaw がセットアップ画面
（オンボーディング、設定修復、無効化された Channel の確認）だけを必要とする場合に
読み込まれます。

```typescript
// setup-entry.ts
import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";
import { myChannelPlugin } from "./src/channel.js";

export default defineSetupPluginEntry(myChannelPlugin);
```

これにより、セットアップ フロー中に重いランタイム コード（暗号ライブラリ、CLI 登録、
バックグラウンド サービス）を読み込まずに済みます。

セットアップ安全なエクスポートをサイドカー モジュールに保持しているバンドル済みワークスペース Channel では、
`defineSetupPluginEntry(...)` の代わりに
`openclaw/plugin-sdk/channel-entry-contract` の
`defineBundledChannelSetupEntry(...)` を使えます。このバンドル済みコントラクトは、
任意の `runtime` エクスポートもサポートしており、セットアップ時のランタイム配線を
軽量かつ明示的に保てます。

**OpenClaw が完全なエントリではなく `setupEntry` を使う場合:**

- Channel は無効化されているが、セットアップ/オンボーディング画面が必要な場合
- Channel は有効だが未設定の場合
- 遅延読み込みが有効な場合（`deferConfiguredChannelFullLoadUntilAfterListen`）

**`setupEntry` が登録しなければならないもの:**

- Channel Plugin オブジェクト（`defineSetupPluginEntry` 経由）
- Gateway のリッスン前に必要な HTTP ルート
- 起動時に必要な Gateway メソッド

これらの起動時 Gateway メソッドでも、`config.*` や `update.*` のような
予約済みコア管理名前空間は引き続き避ける必要があります。

**`setupEntry` に含めるべきではないもの:**

- CLI 登録
- バックグラウンド サービス
- 重いランタイム import（crypto、SDK）
- 起動後にのみ必要な Gateway メソッド

### 狭いセットアップ ヘルパー import

セットアップ専用のホット パスでは、セットアップ画面の一部だけが必要な場合、
より広い `plugin-sdk/setup` アンブレラではなく、より狭いセットアップ ヘルパーの境界を優先してください。

| import パス                        | 用途                                                                                     | 主な export                                                                                                                                                                                                                                                                                  |
| ---------------------------------- | ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/setup-runtime`         | `setupEntry` / 遅延 Channel 起動でも利用可能な、セットアップ時ランタイム ヘルパー       | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
| `plugin-sdk/setup-adapter-runtime` | 環境対応のアカウント セットアップ アダプター                                             | `createEnvPatchedAccountSetupAdapter`                                                                                                                                                                                                                                                        |
| `plugin-sdk/setup-tools`           | セットアップ/インストール用 CLI/アーカイブ/ドキュメント ヘルパー                         | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR`                                                                                                                                                                                |

設定パッチ ヘルパー（例:
`moveSingleAccountChannelSectionToDefaultAccount(...)`）を含む共有セットアップ ツールボックス全体が必要な場合は、
より広い `plugin-sdk/setup` 境界を使用してください。

セットアップ パッチ アダプターは import 時もホット パスで安全なままです。これらのバンドル済み
単一アカウント昇格コントラクト画面ルックアップは遅延されるため、
`plugin-sdk/setup-runtime` を import しても、アダプターが実際に使われる前に
バンドル済みコントラクト画面検出が即座に読み込まれることはありません。

### Channel 所有の単一アカウント昇格

Channel が単一アカウントのトップレベル設定から
`channels.<id>.accounts.*` にアップグレードする場合、共有のデフォルト動作では、
昇格されたアカウント スコープ値を `accounts.default` に移動します。

バンドル済み Channel は、セットアップ コントラクト画面を通じてその昇格を
絞り込んだり上書きしたりできます。

- `singleAccountKeysToMove`: 昇格されたアカウントに移動すべき追加のトップレベル キー
- `namedAccountPromotionKeys`: 名前付きアカウントがすでに存在する場合、これらの
  キーだけが昇格されたアカウントに移動されます。共有のポリシー/配信キーは
  Channel ルートに残ります
- `resolveSingleAccountPromotionTarget(...)`: どの既存アカウントが昇格された値を
  受け取るかを選択します

現在のバンドル済みの例は Matrix です。名前付き Matrix アカウントがちょうど 1 つ
すでに存在する場合、または `defaultAccount` が `Ops` のような既存の非標準キーを
指している場合、昇格では新しい `accounts.default` エントリを作成せず、
そのアカウントを維持します。

## 設定スキーマ

Plugin 設定は、マニフェスト内の JSON Schema に対して検証されます。ユーザーは
次のように Plugin を設定します。

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

Plugin は登録時に、この設定を `api.pluginConfig` として受け取ります。

Channel 固有の設定では、代わりに Channel 設定セクションを使います。

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

### Channel 設定スキーマの構築

`openclaw/plugin-sdk/core` の `buildChannelConfigSchema` を使うと、
Zod スキーマを OpenClaw が検証する `ChannelConfigSchema` ラッパーに変換できます。

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

## セットアップ ウィザード

Channel Plugin は `openclaw onboard` 向けに対話型セットアップ ウィザードを提供できます。
ウィザードは `ChannelPlugin` 上の `ChannelSetupWizard` オブジェクトです。

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

`ChannelSetupWizard` 型は、`credentials`、`textInputs`、
`dmPolicy`、`allowFrom`、`groupAccess`、`prepare`、`finalize` などをサポートします。
完全な例については、バンドル済み Plugin パッケージ
（たとえば Discord Plugin の `src/channel.setup.ts`）を参照してください。

標準の
`note -> prompt -> parse -> merge -> patch` フローだけが必要な DM 許可リスト プロンプトでは、
`openclaw/plugin-sdk/setup` の共有セットアップ ヘルパー
`createPromptParsedAllowFromForAccount(...)`、
`createTopLevelChannelParsedAllowFromPrompt(...)`、
`createNestedChannelParsedAllowFromPrompt(...)` を優先してください。

ラベル、スコア、任意の追加行だけが異なる Channel セットアップ ステータス ブロックでは、
各 Plugin で同じ `status` オブジェクトを手書きする代わりに、
`openclaw/plugin-sdk/setup` の
`createStandardChannelSetupStatus(...)` を優先してください。

特定の文脈でのみ表示されるべき任意のセットアップ画面では、
`openclaw/plugin-sdk/channel-setup` の
`createOptionalChannelSetupSurface` を使います。

```typescript
import { createOptionalChannelSetupSurface } from "openclaw/plugin-sdk/channel-setup";

const setupSurface = createOptionalChannelSetupSurface({
  channel: "my-channel",
  label: "My Channel",
  npmSpec: "@myorg/openclaw-my-channel",
  docsPath: "/channels/my-channel",
});
// Returns { setupAdapter, setupWizard }
```

`plugin-sdk/channel-setup` は、下位レベルの
`createOptionalChannelSetupAdapter(...)` と
`createOptionalChannelSetupWizard(...)` ビルダーも公開しており、
その任意インストール画面の片方だけが必要な場合に使えます。

生成された任意アダプター/ウィザードは、実際の設定書き込み時には安全側で失敗します。
これらは `validateInput`、`applyAccountConfig`、`finalize` の間で
1 つのインストール必須メッセージを再利用し、`docsPath` が設定されている場合は
ドキュメント リンクを追加します。

バイナリ ベースのセットアップ UI では、同じバイナリ/ステータス用の接着コードを
各 Channel に複製するのではなく、共有の委譲ヘルパーを優先してください。

- `createDetectedBinaryStatus(...)`: ラベル、ヒント、スコア、バイナリ検出だけが異なる
  ステータス ブロック向け
- `createCliPathTextInput(...)`: パス ベースのテキスト入力向け
- `createDelegatedSetupWizardStatusResolvers(...)`、
  `createDelegatedPrepare(...)`、`createDelegatedFinalize(...)`、
  `createDelegatedResolveConfigured(...)`:
  `setupEntry` が、より重い完全ウィザードへ遅延的に転送する必要がある場合
- `createDelegatedTextInputShouldPrompt(...)`:
  `setupEntry` が `textInputs[*].shouldPrompt` の判断だけを委譲する必要がある場合

## 公開とインストール

**外部 Plugin:** [ClawHub](/ja-JP/tools/clawhub) または npm に公開し、その後インストールします。

```bash
openclaw plugins install @myorg/openclaw-my-plugin
```

OpenClaw は最初に ClawHub を試し、自動的に npm にフォールバックします。
ClawHub を明示的に強制することもできます。

```bash
openclaw plugins install clawhub:@myorg/openclaw-my-plugin   # ClawHub only
```

対応する `npm:` 上書きはありません。ClawHub フォールバック後に npm 経路を使いたい場合は、
通常の npm パッケージ spec を使ってください。

```bash
openclaw plugins install @myorg/openclaw-my-plugin
```

**リポジトリ内 Plugin:** バンドル済み Plugin ワークスペース ツリー配下に置くと、
ビルド時に自動的に検出されます。

**ユーザーがインストールできるもの:**

```bash
openclaw plugins install <package-name>
```

<Info>
  npm 由来のインストールでは、`openclaw plugins install` は
  `npm install --ignore-scripts`（ライフサイクル スクリプトなし）を実行します。
  Plugin 依存ツリーは純粋な JS/TS に保ち、`postinstall` ビルドが必要な
  パッケージは避けてください。
</Info>

## 関連

- [SDK Entry Points](/ja-JP/plugins/sdk-entrypoints) -- `definePluginEntry` と `defineChannelPluginEntry`
- [Plugin Manifest](/ja-JP/plugins/manifest) -- 完全なマニフェスト スキーマ リファレンス
- [Building Plugins](/ja-JP/plugins/building-plugins) -- ステップごとの はじめに ガイド
