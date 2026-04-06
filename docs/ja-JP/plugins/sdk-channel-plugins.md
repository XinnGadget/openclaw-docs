---
read_when:
    - 新しいメッセージングチャネルプラグインを構築している
    - OpenClawをメッセージングプラットフォームに接続したい
    - ChannelPluginアダプターsurfaceを理解する必要がある
sidebarTitle: Channel Plugins
summary: OpenClaw用メッセージングチャネルプラグインを構築するためのステップバイステップガイド
title: チャネルプラグインの構築
x-i18n:
    generated_at: "2026-04-06T03:10:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: 66b52c10945a8243d803af3bf7e1ea0051869ee92eda2af5718d9bb24fbb8552
    source_path: plugins/sdk-channel-plugins.md
    workflow: 15
---

# チャネルプラグインの構築

このガイドでは、OpenClawをメッセージングプラットフォームに接続するチャネルプラグインの構築方法を説明します。最後まで進めると、DMセキュリティ、
ペアリング、返信スレッド化、送信メッセージングを備えた動作するチャネルが完成します。

<Info>
  まだOpenClawプラグインを一度も作成したことがない場合は、まず
  基本的なパッケージ構造とマニフェスト設定について
  [はじめに](/ja-JP/plugins/building-plugins)を読んでください。
</Info>

## チャネルプラグインの仕組み

チャネルプラグインは、独自のsend/edit/reactツールを必要としません。OpenClawは
共有の`message`ツールを1つコアに保持します。プラグインが担当するのは次の部分です。

- **Config** — アカウント解決とセットアップウィザード
- **Security** — DMポリシーと許可リスト
- **Pairing** — DM承認フロー
- **Session grammar** — プロバイダー固有の会話idをベースチャット、スレッドid、親フォールバックにどう対応付けるか
- **Outbound** — プラットフォームへのテキスト、メディア、投票の送信
- **Threading** — 返信をどうスレッド化するか

コアは、共有message tool、プロンプト配線、外側のセッションキー形状、
汎用`:thread:`管理、およびディスパッチを担当します。

プラットフォームが会話idの中に追加のスコープを保存する場合、その解析は
プラグイン内の`messaging.resolveSessionConversation(...)`に保持してください。これが
`rawId`をベース会話id、任意のスレッド
id、明示的な`baseConversationId`、および任意の`parentConversationCandidates`へ対応付けるための
正式なフックです。
`parentConversationCandidates`を返す場合は、
最も狭い親から最も広い/ベース会話までの順に並べてください。

チャネルレジストリが起動する前に同じ解析が必要なバンドルプラグインは、
一致する
`resolveSessionConversation(...)`エクスポートを持つトップレベルの`session-key-api.ts`ファイルを公開することもできます。コアは、
実行時プラグインレジストリがまだ利用できない場合にのみ、そのブートストラップ安全なsurfaceを使用します。

`messaging.resolveParentConversationCandidates(...)`は、
プラグインが汎用/raw idの上に親フォールバックだけを必要とする場合の
レガシー互換フォールバックとして引き続き利用できます。両方のフックが存在する場合、コアは
まず`resolveSessionConversation(...).parentConversationCandidates`を使い、正式なフックが
それらを省略した場合にのみ
`resolveParentConversationCandidates(...)`へフォールバックします。

## 承認とチャネル機能

ほとんどのチャネルプラグインでは、承認専用コードは不要です。

- コアは同一チャット内の`/approve`、共有承認ボタンpayload、汎用フォールバック配信を担当します。
- チャネルに承認固有の挙動が必要な場合は、チャネルプラグイン上の1つの`approvalCapability`オブジェクトを優先してください。
- `approvalCapability.authorizeActorAction`と`approvalCapability.getActionAvailabilityState`が正式な承認認可seamです。
- チャネルがネイティブexec承認を公開する場合は、ネイティブトランスポートが完全に`approvalCapability.native`配下にある場合でも、`approvalCapability.getActionAvailabilityState`を実装してください。コアはこのavailabilityフックを使って`enabled`と`disabled`を区別し、開始元チャネルがネイティブ承認をサポートするかどうかを判断し、ネイティブクライアントのフォールバックガイダンスにそのチャネルを含めます。
- 重複するローカル承認プロンプトの非表示や、配信前の入力中インジケーター送信のようなチャネル固有のpayloadライフサイクル挙動には、`outbound.shouldSuppressLocalPayloadPrompt`または`outbound.beforeDeliverPayload`を使ってください。
- `approvalCapability.delivery`は、ネイティブ承認ルーティングまたはフォールバック抑制にのみ使ってください。
- `approvalCapability.render`は、共有レンダラーではなく本当にチャネル独自の承認payloadが必要な場合にのみ使ってください。
- チャネルが、無効パスの返信でネイティブexec承認を有効にするために必要な正確なconfigノブを説明したい場合は、`approvalCapability.describeExecApprovalSetup`を使ってください。このフックは`{ channel, channelLabel, accountId }`を受け取ります。名前付きアカウントのあるチャネルでは、トップレベルデフォルトではなく`channels.<channel>.accounts.<id>.execApprovals.*`のようなアカウントスコープ付きパスをレンダリングする必要があります。
- チャネルが既存configから安定したowner相当のDM identityを推論できる場合は、承認固有のコアロジックを追加せずに同一チャット`/approve`を制限するため、`openclaw/plugin-sdk/approval-runtime`の`createResolvedApproverActionAuthAdapter`を使ってください。
- チャネルがネイティブ承認配信を必要とする場合は、チャネルコードは対象の正規化とトランスポートフックに集中させてください。`openclaw/plugin-sdk/approval-runtime`の`createChannelExecApprovalProfile`、`createChannelNativeOriginTargetResolver`、`createChannelApproverDmTargetResolver`、`createApproverRestrictedNativeApprovalCapability`、`createChannelNativeApprovalRuntime`を使い、リクエストフィルタリング、ルーティング、重複排除、有効期限、Gateway購読はコアに任せてください。
- ネイティブ承認チャネルは、`accountId`と`approvalKind`の両方をそれらのヘルパー経由でルーティングする必要があります。`accountId`はマルチアカウント承認ポリシーを正しいボットアカウントにスコープし、`approvalKind`はコアにハードコード分岐を入れずにexec承認とプラグイン承認の挙動をチャネルで利用可能にします。
- 配信された承認id種別をエンドツーエンドで保持してください。ネイティブクライアントは、
  チャネルローカル状態からexec承認とプラグイン承認のルーティングを推測または書き換えるべきではありません。
- 承認種別ごとに意図的に異なるネイティブsurfaceを公開できます。
  現在のバンドル例:
  - Slackは、exec idとplugin idの両方でネイティブ承認ルーティングを利用可能なままにしています。
  - Matrixは、exec承認に対してのみネイティブDM/チャネルルーティングを保持し、
    plugin承認は共有の同一チャット`/approve`パスに任せています。
- `createApproverRestrictedNativeApprovalAdapter`は互換ラッパーとして引き続き存在しますが、新しいコードではcapability builderを優先し、プラグイン上で`approvalCapability`を公開してください。

ホットなチャネルエントリポイントでは、そのファミリーの一部だけが必要な場合、
より狭いruntime subpathを優先してください。

- `openclaw/plugin-sdk/approval-auth-runtime`
- `openclaw/plugin-sdk/approval-client-runtime`
- `openclaw/plugin-sdk/approval-delivery-runtime`
- `openclaw/plugin-sdk/approval-native-runtime`
- `openclaw/plugin-sdk/approval-reply-runtime`

同様に、より広いumbrella
surfaceが不要な場合は、`openclaw/plugin-sdk/setup-runtime`、
`openclaw/plugin-sdk/setup-adapter-runtime`、
`openclaw/plugin-sdk/reply-runtime`、
`openclaw/plugin-sdk/reply-dispatch-runtime`、
`openclaw/plugin-sdk/reply-reference`、および
`openclaw/plugin-sdk/reply-chunking`を優先してください。

特にsetupについては:

- `openclaw/plugin-sdk/setup-runtime`は、runtime-safeなsetupヘルパーを扱います:
  import-safeなsetup patch adapters（`createPatchedAccountSetupAdapter`、
  `createEnvPatchedAccountSetupAdapter`、
  `createSetupInputPresenceValidator`）、lookup-note出力、
  `promptResolvedAllowFrom`、`splitSetupEntries`、および委譲された
  setup-proxy builders
- `openclaw/plugin-sdk/setup-adapter-runtime`は、`createEnvPatchedAccountSetupAdapter`向けの
  狭いenv-aware adapter seamです
- `openclaw/plugin-sdk/channel-setup`は、optional-install setup
  buildersと、いくつかのsetup-safe primitivesを扱います:
  `createOptionalChannelSetupSurface`、`createOptionalChannelSetupAdapter`、
  `createOptionalChannelSetupWizard`、`DEFAULT_ACCOUNT_ID`、
  `createTopLevelChannelDmPolicy`、`setSetupChannelEnabled`、および
  `splitSetupEntries`
- より重い共有setup/configヘルパー、たとえば
  `moveSingleAccountChannelSectionToDefaultAccount(...)`も必要な場合にのみ、
  より広い`openclaw/plugin-sdk/setup` seamを使ってください

チャネルがsetup surfaceで単に「まずこのpluginをインストールしてください」と案内したいだけなら、`createOptionalChannelSetupSurface(...)`を優先してください。生成される
adapter/wizardはconfig書き込みと最終化でfail closedし、検証、finalize、docs-link
copyの全体で同じインストール必須メッセージを再利用します。

他のホットなチャネルパスでも、より広いレガシー
surfaceより狭いヘルパーを優先してください。

- `openclaw/plugin-sdk/account-core`、
  `openclaw/plugin-sdk/account-id`、
  `openclaw/plugin-sdk/account-resolution`、および
  `openclaw/plugin-sdk/account-helpers`は、マルチアカウントconfigと
  default-account fallback向け
- `openclaw/plugin-sdk/inbound-envelope`および
  `openclaw/plugin-sdk/inbound-reply-dispatch`は、受信route/envelopeと
  record-and-dispatch配線向け
- `openclaw/plugin-sdk/messaging-targets`はtarget解析/照合向け
- `openclaw/plugin-sdk/outbound-media`および
  `openclaw/plugin-sdk/outbound-runtime`はメディア読み込みと送信
  identity/send delegates向け
- `openclaw/plugin-sdk/thread-bindings-runtime`はスレッドバインディングのライフサイクル
  とadapter登録向け
- `openclaw/plugin-sdk/agent-media-payload`は、レガシーなagent/media
  payloadフィールドレイアウトが依然必要な場合のみ
- `openclaw/plugin-sdk/telegram-command-config`は、Telegramカスタムコマンドの
  正規化、重複/競合検証、およびfallback-stableなcommand
  config contract向け

認証専用チャネルは通常、デフォルトパスで十分です。承認はコアが処理し、プラグインは送信/認証capabilitiesを公開するだけです。Matrix、Slack、Telegram、カスタムチャットトランスポートのようなネイティブ承認チャネルでは、独自に承認ライフサイクルを組むのではなく、共有ネイティブヘルパーを使うべきです。

## ウォークスルー

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="パッケージとマニフェスト">
    標準のプラグインファイルを作成します。`package.json`内の`channel`フィールドが、
    これをチャネルプラグインにします。完全なパッケージメタデータsurfaceについては、
    [プラグインのセットアップと設定](/ja-JP/plugins/sdk-setup#openclawchannel)を参照してください。

    <CodeGroup>
    ```json package.json
    {
      "name": "@myorg/openclaw-acme-chat",
      "version": "1.0.0",
      "type": "module",
      "openclaw": {
        "extensions": ["./index.ts"],
        "setupEntry": "./setup-entry.ts",
        "channel": {
          "id": "acme-chat",
          "label": "Acme Chat",
          "blurb": "Connect OpenClaw to Acme Chat."
        }
      }
    }
    ```

    ```json openclaw.plugin.json
    {
      "id": "acme-chat",
      "kind": "channel",
      "channels": ["acme-chat"],
      "name": "Acme Chat",
      "description": "Acme Chat channel plugin",
      "configSchema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "acme-chat": {
            "type": "object",
            "properties": {
              "token": { "type": "string" },
              "allowFrom": {
                "type": "array",
                "items": { "type": "string" }
              }
            }
          }
        }
      }
    }
    ```
    </CodeGroup>

  </Step>

  <Step title="チャネルプラグインオブジェクトを構築する">
    `ChannelPlugin`インターフェースには、多くの任意adapter surfaceがあります。まず
    最小構成の`id`と`setup`から始め、必要に応じてadapterを追加してください。

    `src/channel.ts`を作成します:

    ```typescript src/channel.ts
    import {
      createChatChannelPlugin,
      createChannelPluginBase,
    } from "openclaw/plugin-sdk/channel-core";
    import type { OpenClawConfig } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatApi } from "./client.js"; // your platform API client

    type ResolvedAccount = {
      accountId: string | null;
      token: string;
      allowFrom: string[];
      dmPolicy: string | undefined;
    };

    function resolveAccount(
      cfg: OpenClawConfig,
      accountId?: string | null,
    ): ResolvedAccount {
      const section = (cfg.channels as Record<string, any>)?.["acme-chat"];
      const token = section?.token;
      if (!token) throw new Error("acme-chat: token is required");
      return {
        accountId: accountId ?? null,
        token,
        allowFrom: section?.allowFrom ?? [],
        dmPolicy: section?.dmSecurity,
      };
    }

    export const acmeChatPlugin = createChatChannelPlugin<ResolvedAccount>({
      base: createChannelPluginBase({
        id: "acme-chat",
        setup: {
          resolveAccount,
          inspectAccount(cfg, accountId) {
            const section =
              (cfg.channels as Record<string, any>)?.["acme-chat"];
            return {
              enabled: Boolean(section?.token),
              configured: Boolean(section?.token),
              tokenStatus: section?.token ? "available" : "missing",
            };
          },
        },
      }),

      // DM security: who can message the bot
      security: {
        dm: {
          channelKey: "acme-chat",
          resolvePolicy: (account) => account.dmPolicy,
          resolveAllowFrom: (account) => account.allowFrom,
          defaultPolicy: "allowlist",
        },
      },

      // Pairing: approval flow for new DM contacts
      pairing: {
        text: {
          idLabel: "Acme Chat username",
          message: "Send this code to verify your identity:",
          notify: async ({ target, code }) => {
            await acmeChatApi.sendDm(target, `Pairing code: ${code}`);
          },
        },
      },

      // Threading: how replies are delivered
      threading: { topLevelReplyToMode: "reply" },

      // Outbound: send messages to the platform
      outbound: {
        attachedResults: {
          sendText: async (params) => {
            const result = await acmeChatApi.sendMessage(
              params.to,
              params.text,
            );
            return { messageId: result.id };
          },
        },
        base: {
          sendMedia: async (params) => {
            await acmeChatApi.sendFile(params.to, params.filePath);
          },
        },
      },
    });
    ```

    <Accordion title="createChatChannelPluginがしてくれること">
      低レベルadapterインターフェースを手動実装する代わりに、
      宣言的なオプションを渡すと、builderがそれらを合成します。

      | Option | 何を配線するか |
      | --- | --- |
      | `security.dm` | configフィールドからのスコープ付きDMセキュリティリゾルバー |
      | `pairing.text` | コード交換を伴うテキストベースのDMペアリングフロー |
      | `threading` | reply-to-modeリゾルバー（固定、アカウントスコープ、またはカスタム） |
      | `outbound.attachedResults` | 結果メタデータ（message IDs）を返すsend関数 |

      完全に制御したい場合は、宣言的オプションの代わりに生のadapter objectを渡すこともできます。
    </Accordion>

  </Step>

  <Step title="エントリポイントを配線する">
    `index.ts`を作成します:

    ```typescript index.ts
    import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineChannelPluginEntry({
      id: "acme-chat",
      name: "Acme Chat",
      description: "Acme Chat channel plugin",
      plugin: acmeChatPlugin,
      registerCliMetadata(api) {
        api.registerCli(
          ({ program }) => {
            program
              .command("acme-chat")
              .description("Acme Chat management");
          },
          {
            descriptors: [
              {
                name: "acme-chat",
                description: "Acme Chat management",
                hasSubcommands: false,
              },
            ],
          },
        );
      },
      registerFull(api) {
        api.registerGatewayMethod(/* ... */);
      },
    });
    ```

    チャネル所有のCLI descriptorは`registerCliMetadata(...)`に置いてください。これによりOpenClawは、
    完全なチャネルruntimeを有効化せずにそれらをルートヘルプに表示でき、
    通常の完全ロード時にも実際のコマンド登録のために同じdescriptorを取得できます。
    `registerFull(...)`はruntime専用作業のために保持してください。
    `registerFull(...)`がGateway RPCメソッドを登録する場合は、
    plugin固有のprefixを使ってください。コア管理namespace（`config.*`、
    `exec.approvals.*`, `wizard.*`, `update.*`）は予約されており、常に
    `operator.admin`に解決されます。
    `defineChannelPluginEntry`は登録モード分割を自動処理します。すべての
    オプションについては[Entry Points](/ja-JP/plugins/sdk-entrypoints#definechannelpluginentry)を参照してください。

  </Step>

  <Step title="setup entryを追加する">
    オンボーディング中の軽量ロードのために`setup-entry.ts`を作成します:

    ```typescript setup-entry.ts
    import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineSetupPluginEntry(acmeChatPlugin);
    ```

    OpenClawは、チャネルが無効または未設定の場合、完全なentryの代わりにこれを読み込みます。
    これにより、setupフロー中に重いruntimeコードを引き込まずに済みます。
    詳細は[セットアップと設定](/ja-JP/plugins/sdk-setup#setup-entry)を参照してください。

  </Step>

  <Step title="受信メッセージを処理する">
    プラグインは、プラットフォームからメッセージを受信し、それを
    OpenClawへ転送する必要があります。典型的なパターンは、リクエストを検証し、
    そのチャネルの受信ハンドラーを通してディスパッチするWebhookです。

    ```typescript
    registerFull(api) {
      api.registerHttpRoute({
        path: "/acme-chat/webhook",
        auth: "plugin", // plugin-managed auth (verify signatures yourself)
        handler: async (req, res) => {
          const event = parseWebhookPayload(req);

          // Your inbound handler dispatches the message to OpenClaw.
          // The exact wiring depends on your platform SDK —
          // see a real example in the bundled Microsoft Teams or Google Chat plugin package.
          await handleAcmeChatInbound(api, event);

          res.statusCode = 200;
          res.end("ok");
          return true;
        },
      });
    }
    ```

    <Note>
      受信メッセージ処理はチャネル固有です。各チャネルプラグインは
      独自の受信パイプラインを持ちます。実際のパターンについては、
      バンドルチャネルプラグイン
      （たとえばMicrosoft TeamsまたはGoogle Chatプラグインパッケージ）を確認してください。
    </Note>

  </Step>

<a id="step-6-test"></a>
<Step title="テスト">
`src/channel.test.ts`に同一配置テストを書きます:

    ```typescript src/channel.test.ts
    import { describe, it, expect } from "vitest";
    import { acmeChatPlugin } from "./channel.js";

    describe("acme-chat plugin", () => {
      it("resolves account from config", () => {
        const cfg = {
          channels: {
            "acme-chat": { token: "test-token", allowFrom: ["user1"] },
          },
        } as any;
        const account = acmeChatPlugin.setup!.resolveAccount(cfg, undefined);
        expect(account.token).toBe("test-token");
      });

      it("inspects account without materializing secrets", () => {
        const cfg = {
          channels: { "acme-chat": { token: "test-token" } },
        } as any;
        const result = acmeChatPlugin.setup!.inspectAccount!(cfg, undefined);
        expect(result.configured).toBe(true);
        expect(result.tokenStatus).toBe("available");
      });

      it("reports missing config", () => {
        const cfg = { channels: {} } as any;
        const result = acmeChatPlugin.setup!.inspectAccount!(cfg, undefined);
        expect(result.configured).toBe(false);
      });
    });
    ```

    ```bash
    pnpm test -- <bundled-plugin-root>/acme-chat/
    ```

    共有テストヘルパーについては、[テスト](/ja-JP/plugins/sdk-testing)を参照してください。

  </Step>
</Steps>

## ファイル構成

```
<bundled-plugin-root>/acme-chat/
├── package.json              # openclaw.channel metadata
├── openclaw.plugin.json      # config schemaを含むマニフェスト
├── index.ts                  # defineChannelPluginEntry
├── setup-entry.ts            # defineSetupPluginEntry
├── api.ts                    # 公開エクスポート（任意）
├── runtime-api.ts            # 内部runtimeエクスポート（任意）
└── src/
    ├── channel.ts            # createChatChannelPlugin経由のChannelPlugin
    ├── channel.test.ts       # テスト
    ├── client.ts             # プラットフォームAPIクライアント
    └── runtime.ts            # runtime store（必要な場合）
```

## 高度なトピック

<CardGroup cols={2}>
  <Card title="Threading options" icon="git-branch" href="/ja-JP/plugins/sdk-entrypoints#registration-mode">
    固定、アカウントスコープ、またはカスタムのreply mode
  </Card>
  <Card title="Message tool integration" icon="puzzle" href="/ja-JP/plugins/architecture#channel-plugins-and-the-shared-message-tool">
    describeMessageToolとaction discovery
  </Card>
  <Card title="Target resolution" icon="crosshair" href="/ja-JP/plugins/architecture#channel-target-resolution">
    inferTargetChatType、looksLikeId、resolveTarget
  </Card>
  <Card title="Runtime helpers" icon="settings" href="/ja-JP/plugins/sdk-runtime">
    api.runtime経由のTTS、STT、media、subagent
  </Card>
</CardGroup>

<Note>
一部のバンドルヘルパーseamは、バンドルプラグインの保守と
互換性のために今も存在します。これらは新しいチャネルプラグイン向けの推奨パターンではありません。
そのバンドルプラグインファミリーを直接保守しているのでない限り、
共通SDK surfaceの汎用channel/setup/reply/runtime subpathを優先してください。
</Note>

## 次のステップ

- [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins) — プラグインがモデルも提供する場合
- [SDK Overview](/ja-JP/plugins/sdk-overview) — 完全なsubpath importリファレンス
- [SDK Testing](/ja-JP/plugins/sdk-testing) — テストユーティリティとcontract tests
- [Plugin Manifest](/ja-JP/plugins/manifest) — 完全なマニフェストschema
