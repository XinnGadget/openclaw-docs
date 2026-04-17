---
read_when:
    - '`definePluginEntry` または `defineChannelPluginEntry` の正確な型シグネチャが必要です'
    - 登録モード（full と setup と CLI メタデータ）の違いを理解したい場合
    - エントリポイントのオプションを調べている場合
sidebarTitle: Entry Points
summary: definePluginEntry、defineChannelPluginEntry、defineSetupPluginEntry のリファレンス
title: Plugin エントリポイント
x-i18n:
    generated_at: "2026-04-15T19:41:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: aabca25bc9b8ff1b5bb4852bafe83640ffeba006ea6b6a8eff4e2c37a10f1fe4
    source_path: plugins/sdk-entrypoints.md
    workflow: 15
---

# Plugin エントリポイント

すべての Plugin はデフォルトのエントリオブジェクトをエクスポートします。SDK は、
それらを作成するための 3 つのヘルパーを提供します。

<Tip>
  **手順を追ったガイドをお探しですか？** ステップごとのガイドについては、[Channel Plugins](/ja-JP/plugins/sdk-channel-plugins)
  または [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins) を参照してください。
</Tip>

## `definePluginEntry`

**インポート:** `openclaw/plugin-sdk/plugin-entry`

provider plugins、tool plugins、hook plugins、およびメッセージングチャネル
**ではない** あらゆるもの向けです。

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

export default definePluginEntry({
  id: "my-plugin",
  name: "My Plugin",
  description: "Short summary",
  register(api) {
    api.registerProvider({
      /* ... */
    });
    api.registerTool({
      /* ... */
    });
  },
});
```

| フィールド      | 型                                                               | 必須 | デフォルト          |
| ---------------- | ---------------------------------------------------------------- | ---- | ------------------- |
| `id`             | `string`                                                         | はい | —                   |
| `name`           | `string`                                                         | はい | —                   |
| `description`    | `string`                                                         | はい | —                   |
| `kind`           | `string`                                                         | いいえ | —                 |
| `configSchema`   | `OpenClawPluginConfigSchema \| () => OpenClawPluginConfigSchema` | いいえ | 空のオブジェクトスキーマ |
| `register`       | `(api: OpenClawPluginApi) => void`                               | はい | —                   |

- `id` は `openclaw.plugin.json` マニフェストと一致している必要があります。
- `kind` は排他的スロット用です: `"memory"` または `"context-engine"`。
- `configSchema` は遅延評価のために関数にできます。
- OpenClaw は最初のアクセス時にそのスキーマを解決してメモ化するため、高コストなスキーマ
  ビルダーは 1 回しか実行されません。

## `defineChannelPluginEntry`

**インポート:** `openclaw/plugin-sdk/channel-core`

チャネル固有の配線を追加して `definePluginEntry` をラップします。
`api.registerChannel({ plugin })` を自動的に呼び出し、オプションのルートヘルプ CLI メタデータ
接続点を公開し、登録モードに応じて `registerFull` を制御します。

```typescript
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";

export default defineChannelPluginEntry({
  id: "my-channel",
  name: "My Channel",
  description: "Short summary",
  plugin: myChannelPlugin,
  setRuntime: setMyRuntime,
  registerCliMetadata(api) {
    api.registerCli(/* ... */);
  },
  registerFull(api) {
    api.registerGatewayMethod(/* ... */);
  },
});
```

| フィールド            | 型                                                               | 必須 | デフォルト          |
| --------------------- | ---------------------------------------------------------------- | ---- | ------------------- |
| `id`                  | `string`                                                         | はい | —                   |
| `name`                | `string`                                                         | はい | —                   |
| `description`         | `string`                                                         | はい | —                   |
| `plugin`              | `ChannelPlugin`                                                  | はい | —                   |
| `configSchema`        | `OpenClawPluginConfigSchema \| () => OpenClawPluginConfigSchema` | いいえ | 空のオブジェクトスキーマ |
| `setRuntime`          | `(runtime: PluginRuntime) => void`                               | いいえ | —                 |
| `registerCliMetadata` | `(api: OpenClawPluginApi) => void`                               | いいえ | —                 |
| `registerFull`        | `(api: OpenClawPluginApi) => void`                               | いいえ | —                 |

- `setRuntime` は登録中に呼び出されるため、ランタイム参照を保存できます
  （通常は `createPluginRuntimeStore` を介します）。CLI メタデータの
  取得中はスキップされます。
- `registerCliMetadata` は `api.registrationMode === "cli-metadata"` と
  `api.registrationMode === "full"` の両方で実行されます。
  これをチャネル所有の CLI 記述子の正式な配置場所として使用してください。そうすることで、
  ルートヘルプは非アクティベートのまま維持され、通常の CLI コマンド登録は完全な Plugin
  読み込みとの互換性を保てます。
- `registerFull` は `api.registrationMode === "full"` の場合にのみ実行されます。
  setup-only 読み込み中はスキップされます。
- `definePluginEntry` と同様に、`configSchema` は遅延ファクトリーにでき、
  OpenClaw は最初のアクセス時に解決済みスキーマをメモ化します。
- Plugin 所有のルート CLI コマンドについては、実際のコマンドを
  ルート CLI 解析ツリーから消さずに遅延読み込みにしたい場合、
  `api.registerCli(..., { descriptors: [...] })` を優先してください。チャネル Plugin
  では、それらの記述子は `registerCliMetadata(...)` から登録し、
  `registerFull(...)` はランタイム専用の処理に集中させてください。
- `registerFull(...)` でも gateway RPC メソッドを登録する場合は、
  Plugin 固有のプレフィックスにしてください。予約済みのコア管理名前空間
  （`config.*`、`exec.approvals.*`、`wizard.*`、`update.*`）は常に
  `operator.admin` に強制されます。

## `defineSetupPluginEntry`

**インポート:** `openclaw/plugin-sdk/channel-core`

軽量な `setup-entry.ts` ファイル向けです。ランタイムや CLI 配線なしで、
単に `{ plugin }` を返します。

```typescript
import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";

export default defineSetupPluginEntry(myChannelPlugin);
```

チャネルが無効化されている場合、未設定の場合、または遅延読み込みが有効な場合、
OpenClaw は完全なエントリの代わりにこれを読み込みます。これが重要になる場面については、
[Setup and Config](/ja-JP/plugins/sdk-setup#setup-entry) を参照してください。

実際には、`defineSetupPluginEntry(...)` を次のような絞り込まれた setup ヘルパー
群と組み合わせてください。

- `openclaw/plugin-sdk/setup-runtime`:
  import-safe な setup patch アダプター、lookup-note 出力、
  `promptResolvedAllowFrom`、`splitSetupEntries`、委譲された setup proxy
  などのランタイムセーフな setup ヘルパー向け
- `openclaw/plugin-sdk/channel-setup`:
  オプションのインストール用 setup サーフェス向け
- `openclaw/plugin-sdk/setup-tools`:
  setup/install CLI/archive/docs ヘルパー向け

重い SDK、CLI 登録、長寿命のランタイムサービスは完全なエントリに置いてください。

setup サーフェスとランタイムサーフェスを分離するバンドル済みワークスペースチャネルでは、
代わりに `openclaw/plugin-sdk/channel-entry-contract` の
`defineBundledChannelSetupEntry(...)` を使用できます。このコントラクトにより、
setup エントリは runtime setter を公開しつつ、setup-safe な
plugin/secrets エクスポートを保持できます。

```typescript
import { defineBundledChannelSetupEntry } from "openclaw/plugin-sdk/channel-entry-contract";

export default defineBundledChannelSetupEntry({
  importMetaUrl: import.meta.url,
  plugin: {
    specifier: "./channel-plugin-api.js",
    exportName: "myChannelPlugin",
  },
  runtime: {
    specifier: "./runtime-api.js",
    exportName: "setMyChannelRuntime",
  },
});
```

そのバンドル済みコントラクトは、完全なチャネルエントリが読み込まれる前に、
setup フローが本当に軽量な runtime setter を必要とする場合にのみ使用してください。

## 登録モード

`api.registrationMode` は、Plugin がどのように読み込まれたかを示します。

| モード            | タイミング                         | 登録すべきもの                                                                          |
| ----------------- | ---------------------------------- | --------------------------------------------------------------------------------------- |
| `"full"`          | 通常の Gateway 起動                | すべて                                                                                  |
| `"setup-only"`    | 無効化済み / 未設定のチャネル      | チャネル登録のみ                                                                        |
| `"setup-runtime"` | ランタイム利用可能な setup フロー  | チャネル登録に加えて、完全なエントリが読み込まれる前に必要な軽量ランタイムのみ         |
| `"cli-metadata"`  | ルートヘルプ / CLI メタデータ取得  | CLI 記述子のみ                                                                          |

`defineChannelPluginEntry` はこの分岐を自動的に処理します。チャネルに対して
`definePluginEntry` を直接使う場合は、自分でモードを確認してください。

```typescript
register(api) {
  if (api.registrationMode === "cli-metadata" || api.registrationMode === "full") {
    api.registerCli(/* ... */);
    if (api.registrationMode === "cli-metadata") return;
  }

  api.registerChannel({ plugin: myPlugin });
  if (api.registrationMode !== "full") return;

  // Heavy runtime-only registrations
  api.registerService(/* ... */);
}
```

`"setup-runtime"` は、setup-only の起動サーフェスが完全なバンドル済みチャネルランタイムに
再入せずに存在しなければならない期間として扱ってください。適しているのは、
チャネル登録、setup-safe な HTTP ルート、setup-safe な gateway メソッド、
委譲された setup ヘルパーです。重いバックグラウンドサービス、CLI レジストラー、
provider/client SDK のブートストラップは、引き続き `"full"` に属します。

特に CLI レジストラーについては:

- レジストラーが 1 つ以上のルートコマンドを所有しており、最初の呼び出し時に
  OpenClaw に実際の CLI モジュールを遅延読み込みさせたい場合は、
  `descriptors` を使用してください
- それらの記述子が、レジストラーによって公開されるすべてのトップレベルコマンドルートを
  カバーしていることを確認してください
- 即時互換パスでは `commands` 単独のみを使用してください

## Plugin の形状

OpenClaw は、読み込まれた Plugin をその登録動作によって分類します。

| 形状                  | 説明                                               |
| --------------------- | -------------------------------------------------- |
| **plain-capability**  | 1 種類の capability のみ（例: provider-only）      |
| **hybrid-capability** | 複数種類の capability（例: provider + speech）     |
| **hook-only**         | hooks のみで、capability はなし                    |
| **non-capability**    | Tools/commands/services はあるが capability はなし |

Plugin の形状を確認するには `openclaw plugins inspect <id>` を使用してください。

## 関連

- [SDK Overview](/ja-JP/plugins/sdk-overview) — 登録 API とサブパスのリファレンス
- [Runtime Helpers](/ja-JP/plugins/sdk-runtime) — `api.runtime` と `createPluginRuntimeStore`
- [Setup and Config](/ja-JP/plugins/sdk-setup) — マニフェスト、setup エントリ、遅延読み込み
- [Channel Plugins](/ja-JP/plugins/sdk-channel-plugins) — `ChannelPlugin` オブジェクトの構築
- [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins) — provider 登録と hooks
