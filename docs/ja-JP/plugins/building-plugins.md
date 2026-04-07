---
read_when:
    - 新しいOpenClaw pluginを作成したい
    - plugin開発のクイックスタートが必要
    - OpenClawに新しいchannel、provider、tool、またはその他の機能を追加している
sidebarTitle: Getting Started
summary: 数分で最初のOpenClaw pluginを作成する
title: Pluginsの構築
x-i18n:
    generated_at: "2026-04-07T04:44:11Z"
    model: gpt-5.4
    provider: openai
    source_hash: 509c1f5abe1a0a74966054ed79b71a1a7ee637a43b1214c424acfe62ddf48eef
    source_path: plugins/building-plugins.md
    workflow: 15
---

# Pluginsの構築

pluginsは、新しい機能でOpenClawを拡張します: channels、model providers、
speech、realtime transcription、realtime voice、media understanding、image
generation、video generation、web fetch、web search、agent tools、またはその
任意の組み合わせです。

pluginをOpenClawリポジトリに追加する必要はありません。
[ClawHub](/ja-JP/tools/clawhub) またはnpmに公開し、ユーザーは
`openclaw plugins install <package-name>` でインストールできます。OpenClawはまずClawHubを試し、
自動的にnpmへフォールバックします。

## 前提条件

- Node >= 22 とパッケージマネージャー（npmまたはpnpm）
- TypeScript（ESM）の基本知識
- リポジトリ内pluginの場合: リポジトリをclone済みで、`pnpm install` を実行済み

## どの種類のpluginか

<CardGroup cols={3}>
  <Card title="Channel plugin" icon="messages-square" href="/ja-JP/plugins/sdk-channel-plugins">
    OpenClawをメッセージングプラットフォーム（Discord、IRCなど）に接続する
  </Card>
  <Card title="Provider plugin" icon="cpu" href="/ja-JP/plugins/sdk-provider-plugins">
    model provider（LLM、proxy、またはカスタムendpoint）を追加する
  </Card>
  <Card title="Tool / hook plugin" icon="wrench">
    agent tools、event hooks、またはservicesを登録する — 以下へ進む
  </Card>
</CardGroup>

channel pluginが任意であり、onboarding/setupの実行時にインストールされていない可能性がある場合は、
`openclaw/plugin-sdk/channel-setup` の
`createOptionalChannelSetupSurface(...)` を使用してください。これにより、
インストール要件を通知し、pluginがインストールされるまで実際の設定書き込みを安全に失敗させる
setup adapter + ウィザードの組が生成されます。

## クイックスタート: tool plugin

この手順では、agent toolを登録する最小限のpluginを作成します。channel
pluginとprovider pluginには、上でリンクした専用ガイドがあります。

<Steps>
  <Step title="パッケージとmanifestを作成する">
    <CodeGroup>
    ```json package.json
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

    ```json openclaw.plugin.json
    {
      "id": "my-plugin",
      "name": "My Plugin",
      "description": "Adds a custom tool to OpenClaw",
      "configSchema": {
        "type": "object",
        "additionalProperties": false
      }
    }
    ```
    </CodeGroup>

    すべてのpluginには、設定がなくてもmanifestが必要です。完全なスキーマは
    [Manifest](/ja-JP/plugins/manifest) を参照してください。ClawHubの正規の
    公開スニペットは `docs/snippets/plugin-publish/` にあります。

  </Step>

  <Step title="entry pointを書く">

    ```typescript
    // index.ts
    import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
    import { Type } from "@sinclair/typebox";

    export default definePluginEntry({
      id: "my-plugin",
      name: "My Plugin",
      description: "Adds a custom tool to OpenClaw",
      register(api) {
        api.registerTool({
          name: "my_tool",
          description: "Do a thing",
          parameters: Type.Object({ input: Type.String() }),
          async execute(_id, params) {
            return { content: [{ type: "text", text: `Got: ${params.input}` }] };
          },
        });
      },
    });
    ```

    `definePluginEntry` はchannel以外のplugins向けです。channelsには
    `defineChannelPluginEntry` を使用します — [Channel Plugins](/ja-JP/plugins/sdk-channel-plugins) を参照してください。
    完全なentry pointオプションについては、[Entry Points](/ja-JP/plugins/sdk-entrypoints) を参照してください。

  </Step>

  <Step title="テストして公開する">

    **外部plugin:** ClawHubで検証して公開し、その後インストールします:

    ```bash
    clawhub package publish your-org/your-plugin --dry-run
    clawhub package publish your-org/your-plugin
    openclaw plugins install clawhub:@myorg/openclaw-my-plugin
    ```

    OpenClawは、`@myorg/openclaw-my-plugin` のような
    bare package specに対しても、npmより先にClawHubを確認します。

    **リポジトリ内plugin:** バンドルされたplugin workspace tree配下に配置します — 自動的に検出されます。

    ```bash
    pnpm test -- <bundled-plugin-root>/my-plugin/
    ```

  </Step>
</Steps>

## Plugin capabilities

1つのpluginは、`api` オブジェクトを通じて任意の数のcapabilityを登録できます:

| Capability             | Registration method                              | 詳細ガイド                                                                    |
| ---------------------- | ------------------------------------------------ | ----------------------------------------------------------------------------- |
| Text inference (LLM)   | `api.registerProvider(...)`                      | [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins)                             |
| CLI inference backend  | `api.registerCliBackend(...)`                    | [CLI Backends](/ja-JP/gateway/cli-backends)                                         |
| Channel / messaging    | `api.registerChannel(...)`                       | [Channel Plugins](/ja-JP/plugins/sdk-channel-plugins)                               |
| Speech (TTS/STT)       | `api.registerSpeechProvider(...)`                | [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Realtime transcription | `api.registerRealtimeTranscriptionProvider(...)` | [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Realtime voice         | `api.registerRealtimeVoiceProvider(...)`         | [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Media understanding    | `api.registerMediaUnderstandingProvider(...)`    | [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Image generation       | `api.registerImageGenerationProvider(...)`       | [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Music generation       | `api.registerMusicGenerationProvider(...)`       | [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Video generation       | `api.registerVideoGenerationProvider(...)`       | [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Web fetch              | `api.registerWebFetchProvider(...)`              | [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Web search             | `api.registerWebSearchProvider(...)`             | [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Agent tools            | `api.registerTool(...)`                          | 以下                                                                          |
| Custom commands        | `api.registerCommand(...)`                       | [Entry Points](/ja-JP/plugins/sdk-entrypoints)                                      |
| Event hooks            | `api.registerHook(...)`                          | [Entry Points](/ja-JP/plugins/sdk-entrypoints)                                      |
| HTTP routes            | `api.registerHttpRoute(...)`                     | [Internals](/ja-JP/plugins/architecture#gateway-http-routes)                        |
| CLI subcommands        | `api.registerCli(...)`                           | [Entry Points](/ja-JP/plugins/sdk-entrypoints)                                      |

完全な登録APIについては、[SDK Overview](/ja-JP/plugins/sdk-overview#registration-api) を参照してください。

pluginが独自のGateway RPCメソッドを登録する場合は、
plugin固有のprefixを維持してください。coreのadmin namespace（`config.*`、
`exec.approvals.*`、`wizard.*`、`update.*`）は予約されたままで、pluginがより狭いscopeを要求しても、
常に `operator.admin` に解決されます。

覚えておくべきhook guardのセマンティクス:

- `before_tool_call`: `{ block: true }` は終端であり、より低い優先度のhandlerを停止します。
- `before_tool_call`: `{ block: false }` は未決定として扱われます。
- `before_tool_call`: `{ requireApproval: true }` はagent実行を一時停止し、exec approval overlay、Telegramボタン、Discord interactions、または任意のchannel上の `/approve` コマンドを通じてユーザーに承認を求めます。
- `before_install`: `{ block: true }` は終端であり、より低い優先度のhandlerを停止します。
- `before_install`: `{ block: false }` は未決定として扱われます。
- `message_sending`: `{ cancel: true }` は終端であり、より低い優先度のhandlerを停止します。
- `message_sending`: `{ cancel: false }` は未決定として扱われます。

`/approve` コマンドは、境界付きフォールバックでexec approvalとplugin approvalの両方を処理します。exec approval idが見つからない場合、
OpenClawは同じidでplugin approvalを再試行します。plugin approval forwardingは設定の `approvals.plugin` で個別に構成できます。

カスタムapproval処理で同じ境界付きフォールバックケースを検出する必要がある場合は、
approval-expiry文字列を手動で照合するのではなく、`openclaw/plugin-sdk/error-runtime` の
`isApprovalNotFoundError` を使用してください。

詳細は [SDK Overview hook decision semantics](/ja-JP/plugins/sdk-overview#hook-decision-semantics) を参照してください。

## Agent toolsの登録

toolsは、LLMが呼び出せる型付き関数です。必須（常に
利用可能）または任意（ユーザーのオプトイン）が可能です:

```typescript
register(api) {
  // Required tool — always available
  api.registerTool({
    name: "my_tool",
    description: "Do a thing",
    parameters: Type.Object({ input: Type.String() }),
    async execute(_id, params) {
      return { content: [{ type: "text", text: params.input }] };
    },
  });

  // Optional tool — user must add to allowlist
  api.registerTool(
    {
      name: "workflow_tool",
      description: "Run a workflow",
      parameters: Type.Object({ pipeline: Type.String() }),
      async execute(_id, params) {
        return { content: [{ type: "text", text: params.pipeline }] };
      },
    },
    { optional: true },
  );
}
```

ユーザーは設定で任意toolsを有効にします:

```json5
{
  tools: { allow: ["workflow_tool"] },
}
```

- tool名はcore toolsと衝突してはいけません（衝突したものはスキップされます）
- 副作用があるtoolsや追加バイナリが必要なtoolsには `optional: true` を使用してください
- ユーザーは `tools.allow` にplugin idを追加することで、そのpluginのすべてのtoolsを有効にできます

## Import規約

必ず、焦点の絞られた `openclaw/plugin-sdk/<subpath>` パスからimportしてください:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";

// Wrong: monolithic root (deprecated, will be removed)
import { ... } from "openclaw/plugin-sdk";
```

完全なsubpathリファレンスは [SDK Overview](/ja-JP/plugins/sdk-overview) を参照してください。

plugin内部では、内部importにローカルbarrelファイル（`api.ts`、`runtime-api.ts`）を使用してください —
SDK path経由で自分自身のpluginをimportしてはいけません。

provider pluginsでは、その継ぎ目が本当に汎用的でない限り、provider固有のhelperはそれらのpackage-root
barrelsに置いてください。現在のバンドル例:

- Anthropic: Claude stream wrappers と `service_tier` / beta helpers
- OpenAI: provider builders、default-model helpers、realtime providers
- OpenRouter: provider builder と onboarding/config helpers

helperが1つのバンドルprovider package内でしか有用でない場合は、
それを `openclaw/plugin-sdk/*` に昇格させるのではなく、その
package-root seam上に維持してください。

一部の生成済み `openclaw/plugin-sdk/<bundled-id>` helper seamsは、
バンドルpluginの保守と互換性のためにまだ存在しています。たとえば
`plugin-sdk/feishu-setup` や `plugin-sdk/zalo-setup` です。これらは、
新しいサードパーティpluginのデフォルトパターンではなく、予約されたsurfaceとして扱ってください。

## 提出前チェックリスト

<Check>**package.json** に正しい `openclaw` メタデータがある</Check>
<Check>**openclaw.plugin.json** manifestが存在し、有効である</Check>
<Check>entry pointが `defineChannelPluginEntry` または `definePluginEntry` を使用している</Check>
<Check>すべてのimportが焦点の絞られた `plugin-sdk/<subpath>` パスを使用している</Check>
<Check>内部importが、SDK self-importではなくローカルmoduleを使用している</Check>
<Check>テストが通る（`pnpm test -- <bundled-plugin-root>/my-plugin/`）</Check>
<Check>`pnpm check` が通る（リポジトリ内plugins）</Check>

## Beta Release Testing

1. [openclaw/openclaw](https://github.com/openclaw/openclaw/releases) のGitHub release tagを監視し、`Watch` > `Releases` から購読してください。beta tagは `v2026.3.N-beta.1` のような形式です。release告知のために、OpenClaw公式Xアカウント [@openclaw](https://x.com/openclaw) の通知を有効にすることもできます。
2. beta tagが出たら、できるだけ早くpluginをそのtagに対してテストしてください。stableまでの時間は通常わずか数時間です。
3. テスト後、`plugin-forum` Discord channel内の自分のpluginスレッドに、`all good` または何が壊れたかを投稿してください。まだスレッドがない場合は作成してください。
4. 何か壊れた場合は、`Beta blocker: <plugin-name> - <summary>` というタイトルでissueを作成または更新し、`beta-blocker` labelを付けてください。issueリンクをスレッドに貼ってください。
5. `main` に対して `fix(<plugin-id>): beta blocker - <summary>` というタイトルのPRを開き、PRとDiscordスレッドの両方でissueをリンクしてください。contributorはPRにlabelを付けられないため、titleがmaintainerとautomation向けのPR側シグナルになります。PRのあるblockerはマージされますが、ないものはそのまま出荷される可能性があります。maintainerはbeta testing中にこれらのスレッドを監視しています。
6. 無言はグリーンを意味します。期間を逃した場合、修正はおそらく次のサイクルで反映されます。

## 次のステップ

<CardGroup cols={2}>
  <Card title="Channel Plugins" icon="messages-square" href="/ja-JP/plugins/sdk-channel-plugins">
    メッセージングchannel pluginを構築する
  </Card>
  <Card title="Provider Plugins" icon="cpu" href="/ja-JP/plugins/sdk-provider-plugins">
    model provider pluginを構築する
  </Card>
  <Card title="SDK Overview" icon="book-open" href="/ja-JP/plugins/sdk-overview">
    import mapと登録APIのリファレンス
  </Card>
  <Card title="Runtime Helpers" icon="settings" href="/ja-JP/plugins/sdk-runtime">
    `api.runtime` 経由のTTS、search、subagent
  </Card>
  <Card title="Testing" icon="test-tubes" href="/ja-JP/plugins/sdk-testing">
    テストユーティリティとパターン
  </Card>
  <Card title="Plugin Manifest" icon="file-json" href="/ja-JP/plugins/manifest">
    完全なmanifestスキーマリファレンス
  </Card>
</CardGroup>

## 関連

- [Plugin Architecture](/ja-JP/plugins/architecture) — 内部アーキテクチャの詳細解説
- [SDK Overview](/ja-JP/plugins/sdk-overview) — Plugin SDKリファレンス
- [Manifest](/ja-JP/plugins/manifest) — plugin manifest形式
- [Channel Plugins](/ja-JP/plugins/sdk-channel-plugins) — channel pluginsの構築
- [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins) — provider pluginsの構築
