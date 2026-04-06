---
read_when:
    - 新しい OpenClaw plugin を作成したい場合
    - plugin 開発のクイックスタートが必要な場合
    - OpenClaw に新しい channel、provider、tool、またはその他の capability を追加する場合
sidebarTitle: Getting Started
summary: 最初の OpenClaw plugin を数分で作成する
title: Plugins の構築
x-i18n:
    generated_at: "2026-04-06T03:09:42Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9be344cb300ecbcba08e593a95bcc93ab16c14b28a0ff0c29b26b79d8249146c
    source_path: plugins/building-plugins.md
    workflow: 15
---

# Plugins の構築

Plugins は OpenClaw を新しい capabilities で拡張します。channels、model providers、
speech、realtime transcription、realtime voice、media understanding、image
generation、video generation、web fetch、web search、agent tools、または
それらの任意の組み合わせに対応できます。

plugin を OpenClaw リポジトリに追加する必要はありません。
[ClawHub](/ja-JP/tools/clawhub) または npm に公開し、ユーザーは
`openclaw plugins install <package-name>` でインストールします。OpenClaw はまず ClawHub を試し、
自動的に npm へフォールバックします。

## 前提条件

- Node >= 22 とパッケージマネージャー（npm または pnpm）
- TypeScript（ESM）への習熟
- リポジトリ内 plugin の場合: リポジトリを clone し、`pnpm install` を実行済みであること

## どの種類の plugin ですか？

<CardGroup cols={3}>
  <Card title="Channel plugin" icon="messages-square" href="/ja-JP/plugins/sdk-channel-plugins">
    OpenClaw をメッセージングプラットフォーム（Discord、IRC など）に接続します
  </Card>
  <Card title="Provider plugin" icon="cpu" href="/ja-JP/plugins/sdk-provider-plugins">
    model provider（LLM、proxy、またはカスタム endpoint）を追加します
  </Card>
  <Card title="Tool / hook plugin" icon="wrench">
    agent tool、event hook、または service を登録します — 以下へ進んでください
  </Card>
</CardGroup>

channel plugin が任意であり、オンボーディング/セットアップ実行時に
インストールされていない可能性がある場合は、
`openclaw/plugin-sdk/channel-setup` の `createOptionalChannelSetupSurface(...)` を使用してください。これは、インストール要件を通知し、
plugin がインストールされるまで実際の設定書き込みを fail closed する
setup adapter + wizard ペアを生成します。

## クイックスタート: tool plugin

このウォークスルーでは、agent tool を登録する最小限の plugin を作成します。channel
plugin と provider plugin には、上記でリンクした専用ガイドがあります。

<Steps>
  <Step title="パッケージと manifest を作成する">
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

    すべての plugin には、設定がなくても manifest が必要です。完全なスキーマについては
    [Manifest](/ja-JP/plugins/manifest) を参照してください。ClawHub への正式な
    公開スニペットは `docs/snippets/plugin-publish/` にあります。

  </Step>

  <Step title="entry point を書く">

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

    `definePluginEntry` は非 channel plugins 用です。channels には
    `defineChannelPluginEntry` を使用してください — 詳しくは [Channel Plugins](/ja-JP/plugins/sdk-channel-plugins) を参照してください。
    entry point オプションの全体像は [Entry Points](/ja-JP/plugins/sdk-entrypoints) を参照してください。

  </Step>

  <Step title="テストして公開する">

    **外部 plugin:** ClawHub で検証して公開し、その後インストールします:

    ```bash
    clawhub package publish your-org/your-plugin --dry-run
    clawhub package publish your-org/your-plugin
    openclaw plugins install clawhub:@myorg/openclaw-my-plugin
    ```

    OpenClaw は `@myorg/openclaw-my-plugin` のような bare package spec でも、
    npm より先に ClawHub を確認します。

    **リポジトリ内 plugin:** バンドル plugin workspace tree 配下に配置します — 自動検出されます。

    ```bash
    pnpm test -- <bundled-plugin-root>/my-plugin/
    ```

  </Step>
</Steps>

## Plugin capabilities

1 つの plugin は、`api` オブジェクトを通じて任意の数の capability を登録できます:

| Capability             | Registration method                              | Detailed guide                                                                  |
| ---------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------- |
| Text inference (LLM)   | `api.registerProvider(...)`                      | [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins)                               |
| Channel / messaging    | `api.registerChannel(...)`                       | [Channel Plugins](/ja-JP/plugins/sdk-channel-plugins)                                 |
| Speech (TTS/STT)       | `api.registerSpeechProvider(...)`                | [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Realtime transcription | `api.registerRealtimeTranscriptionProvider(...)` | [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Realtime voice         | `api.registerRealtimeVoiceProvider(...)`         | [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Media understanding    | `api.registerMediaUnderstandingProvider(...)`    | [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Image generation       | `api.registerImageGenerationProvider(...)`       | [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Music generation       | `api.registerMusicGenerationProvider(...)`       | [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Video generation       | `api.registerVideoGenerationProvider(...)`       | [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Web fetch              | `api.registerWebFetchProvider(...)`              | [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Web search             | `api.registerWebSearchProvider(...)`             | [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Agent tools            | `api.registerTool(...)`                          | 以下                                                                           |
| Custom commands        | `api.registerCommand(...)`                       | [Entry Points](/ja-JP/plugins/sdk-entrypoints)                                        |
| Event hooks            | `api.registerHook(...)`                          | [Entry Points](/ja-JP/plugins/sdk-entrypoints)                                        |
| HTTP routes            | `api.registerHttpRoute(...)`                     | [Internals](/ja-JP/plugins/architecture#gateway-http-routes)                          |
| CLI subcommands        | `api.registerCli(...)`                           | [Entry Points](/ja-JP/plugins/sdk-entrypoints)                                        |

完全な registration API については、[SDK Overview](/ja-JP/plugins/sdk-overview#registration-api) を参照してください。

plugin がカスタム Gateway RPC メソッドを登録する場合は、それらを
plugin 固有の prefix に置いてください。コア管理 namespace（`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`）は予約済みであり、plugin が
より狭い scope を要求しても、常に `operator.admin` に解決されます。

覚えておくべき hook guard の意味論:

- `before_tool_call`: `{ block: true }` は終端であり、より低優先度の handler を停止します。
- `before_tool_call`: `{ block: false }` は未決定として扱われます。
- `before_tool_call`: `{ requireApproval: true }` は agent 実行を一時停止し、exec approval overlay、Telegram buttons、Discord interactions、または任意 channel 上の `/approve` コマンドを通じてユーザーに承認を求めます。
- `before_install`: `{ block: true }` は終端であり、より低優先度の handler を停止します。
- `before_install`: `{ block: false }` は未決定として扱われます。
- `message_sending`: `{ cancel: true }` は終端であり、より低優先度の handler を停止します。
- `message_sending`: `{ cancel: false }` は未決定として扱われます。

`/approve` コマンドは、境界付きフォールバックにより exec と plugin の両方の承認を処理します。exec approval id が見つからない場合、OpenClaw は同じ id を plugin approvals 経由で再試行します。plugin approval forwarding は、設定内の `approvals.plugin` で個別に設定できます。

カスタム approval 配線で同じ境界付きフォールバックケースを検出する必要がある場合は、
approval-expiry 文字列を手作業で照合するのではなく、
`openclaw/plugin-sdk/error-runtime` の `isApprovalNotFoundError` を優先して使用してください。

詳しくは [SDK Overview hook decision semantics](/ja-JP/plugins/sdk-overview#hook-decision-semantics) を参照してください。

## Agent tools の登録

Tools は LLM が呼び出せる型付き関数です。必須
（常に利用可能）にも、任意
（ユーザーが明示的に有効化）にもできます:

```typescript
register(api) {
  // 必須 tool — 常に利用可能
  api.registerTool({
    name: "my_tool",
    description: "Do a thing",
    parameters: Type.Object({ input: Type.String() }),
    async execute(_id, params) {
      return { content: [{ type: "text", text: params.input }] };
    },
  });

  // 任意 tool — ユーザーが allowlist に追加する必要があります
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

ユーザーは設定で任意 tool を有効にします:

```json5
{
  tools: { allow: ["workflow_tool"] },
}
```

- tool 名はコア tools と衝突してはいけません（衝突したものはスキップされます）
- 副作用がある tools や追加バイナリ要件がある tools には `optional: true` を使用してください
- ユーザーは `tools.allow` に plugin id を追加することで、その plugin のすべての tools を有効にできます

## import 規約

必ず、用途を絞った `openclaw/plugin-sdk/<subpath>` パスから import してください:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";

// Wrong: monolithic root (deprecated, will be removed)
import { ... } from "openclaw/plugin-sdk";
```

完全な subpath リファレンスについては、[SDK Overview](/ja-JP/plugins/sdk-overview) を参照してください。

plugin 内では、内部 import 用にローカル barrel file（`api.ts`, `runtime-api.ts`）を使用してください — 自分自身の plugin をその SDK path 経由で import してはいけません。

provider plugins では、provider 固有 helper はその seam が本当に汎用的でない限り、
それらの package-root barrel に置いてください。現在のバンドル例:

- Anthropic: Claude stream wrapper と `service_tier` / beta helper
- OpenAI: provider builder、default-model helper、realtime providers
- OpenRouter: provider builder と onboarding/config helper

helper が 1 つのバンドル provider package 内でしか有用でない場合は、
`openclaw/plugin-sdk/*` に昇格させるのではなく、その package-root seam に置いてください。

生成済みの `openclaw/plugin-sdk/<bundled-id>` helper seam の一部は、
バンドル plugin の保守と互換性のためにまだ存在しています。たとえば
`plugin-sdk/feishu-setup` や `plugin-sdk/zalo-setup` です。これらは、新しいサードパーティ plugin のデフォルトパターンではなく、予約済み surface として扱ってください。

## 提出前チェックリスト

<Check>**package.json** に正しい `openclaw` メタデータがある</Check>
<Check>**openclaw.plugin.json** manifest が存在し、有効である</Check>
<Check>entry point が `defineChannelPluginEntry` または `definePluginEntry` を使っている</Check>
<Check>すべての imports が用途を絞った `plugin-sdk/<subpath>` パスを使っている</Check>
<Check>内部 imports が SDK self-imports ではなくローカル module を使っている</Check>
<Check>テストが通る（`pnpm test -- <bundled-plugin-root>/my-plugin/`）</Check>
<Check>`pnpm check` が通る（リポジトリ内 plugins）</Check>

## ベータリリースのテスト

1. [openclaw/openclaw](https://github.com/openclaw/openclaw/releases) の GitHub リリースタグを監視し、`Watch` > `Releases` で購読してください。ベータタグは `v2026.3.N-beta.1` のような形式です。リリース告知については、公式 OpenClaw X アカウント [@openclaw](https://x.com/openclaw) の通知を有効にすることもできます。
2. ベータタグが現れたら、できるだけ早く plugin をそのタグでテストしてください。stable までの猶予は通常数時間しかありません。
3. テスト後、`plugin-forum` Discord channel の自分の plugin スレッドに、`all good` または何が壊れたかを書き込んでください。まだスレッドがない場合は作成してください。
4. 問題が壊れている場合は、`Beta blocker: <plugin-name> - <summary>` というタイトルの issue を新規作成または更新し、`beta-blocker` ラベルを付けてください。その issue リンクをスレッドに貼ってください。
5. `main` に対して `fix(<plugin-id>): beta blocker - <summary>` というタイトルの PR を作成し、issue を PR と Discord スレッドの両方でリンクしてください。コントリビューターは PR にラベルを付けられないため、このタイトルがメンテナーと自動化に対する PR 側のシグナルになります。PR がある blocker はマージされますが、PR がない blocker はそのまま出荷される可能性があります。メンテナーはベータテスト中、これらのスレッドを監視しています。
6. 反応がないことは green を意味します。期間を逃した場合、修正はおそらく次のサイクルに入ります。

## 次のステップ

<CardGroup cols={2}>
  <Card title="Channel Plugins" icon="messages-square" href="/ja-JP/plugins/sdk-channel-plugins">
    メッセージング channel plugin を構築する
  </Card>
  <Card title="Provider Plugins" icon="cpu" href="/ja-JP/plugins/sdk-provider-plugins">
    model provider plugin を構築する
  </Card>
  <Card title="SDK Overview" icon="book-open" href="/ja-JP/plugins/sdk-overview">
    import map と registration API リファレンス
  </Card>
  <Card title="Runtime Helpers" icon="settings" href="/ja-JP/plugins/sdk-runtime">
    api.runtime 経由の TTS、search、subagent
  </Card>
  <Card title="Testing" icon="test-tubes" href="/ja-JP/plugins/sdk-testing">
    テストユーティリティとパターン
  </Card>
  <Card title="Plugin Manifest" icon="file-json" href="/ja-JP/plugins/manifest">
    完全な manifest スキーマリファレンス
  </Card>
</CardGroup>

## 関連

- [Plugin Architecture](/ja-JP/plugins/architecture) — 内部アーキテクチャの詳細解説
- [SDK Overview](/ja-JP/plugins/sdk-overview) — Plugin SDK リファレンス
- [Manifest](/ja-JP/plugins/manifest) — plugin manifest 形式
- [Channel Plugins](/ja-JP/plugins/sdk-channel-plugins) — channel plugins の構築
- [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins) — provider plugins の構築
