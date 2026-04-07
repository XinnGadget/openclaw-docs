---
read_when:
    - 新しいメッセージングチャネルプラグインを構築している場合
    - OpenClawをメッセージングプラットフォームに接続したい場合
    - ChannelPluginアダプターの表面を理解する必要がある場合
sidebarTitle: Channel Plugins
summary: OpenClaw向けメッセージングチャネルプラグインを構築するためのステップごとのガイド
title: チャネルプラグインの構築
x-i18n:
    generated_at: "2026-04-07T04:44:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: 25ac0591d9b0ba401925b29ae4b9572f18b2cbffc2b6ca6ed5252740e7cf97e9
    source_path: plugins/sdk-channel-plugins.md
    workflow: 15
---

# チャネルプラグインの構築

このガイドでは、OpenClawをメッセージングプラットフォームに接続するチャネルプラグインの構築手順を説明します。最後には、DMセキュリティ、ペアリング、返信スレッド化、送信メッセージングを備えた動作するチャネルが完成します。

<Info>
  まだOpenClawプラグインを一度も構築したことがない場合は、まず
  基本的なパッケージ構造とマニフェスト設定について[はじめに](/ja-JP/plugins/building-plugins)を読んでください。
</Info>

## チャネルプラグインの仕組み

チャネルプラグインは独自のsend/edit/react toolsを必要としません。OpenClawはコア内で1つの共有`message` toolを維持します。プラグインが担当するのは次の項目です:

- **Config** — アカウント解決とセットアップウィザード
- **Security** — DMポリシーとallowlists
- **Pairing** — DM承認フロー
- **Session grammar** — プロバイダー固有の会話idが、ベースチャット、thread ids、親フォールバックにどのように対応付けられるか
- **Outbound** — プラットフォームへのテキスト、メディア、投票の送信
- **Threading** — 返信のスレッド化方法

コアは、共有message tool、プロンプト配線、外側のsession-key形状、汎用的な`:thread:`管理、およびディスパッチを担当します。

プラットフォームが会話id内に追加のスコープを保存する場合は、その解析をプラグイン内の`messaging.resolveSessionConversation(...)`に保持してください。これは、`rawId`をベース会話id、任意のthread id、明示的な`baseConversationId`、および任意の`parentConversationCandidates`へ対応付けるための正式なフックです。`parentConversationCandidates`を返す場合は、最も狭い親から最も広い/ベース会話までの順序を維持してください。

チャネルレジストリの起動前に同じ解析が必要なバンドル済みプラグインは、一致する`resolveSessionConversation(...)`エクスポートを持つトップレベルの`session-key-api.ts`ファイルを公開することもできます。コアは、実行時プラグインレジストリがまだ利用できない場合にのみ、そのbootstrap-safeな表面を使用します。

`messaging.resolveParentConversationCandidates(...)`は、プラグインが汎用/raw idの上に親フォールバックだけを必要とする場合の、レガシー互換フォールバックとして引き続き利用できます。両方のフックが存在する場合、コアはまず`resolveSessionConversation(...).parentConversationCandidates`を使用し、その正式なフックがそれらを省略した場合にのみ`resolveParentConversationCandidates(...)`へフォールバックします。

## Approvalsとチャネル機能

ほとんどのチャネルプラグインでは、approval専用コードは不要です。

- コアはsame-chat `/approve`、共有approval button payloads、汎用フォールバック配信を担当します。
- チャネルがapproval固有の動作を必要とする場合は、チャネルプラグイン上の1つの`approvalCapability`オブジェクトを優先してください。
- `approvalCapability.authorizeActorAction`と`approvalCapability.getActionAvailabilityState`が正式なapproval-auth seamです。
- チャネルがネイティブexec approvalsを公開する場合、ネイティブtransportが完全に`approvalCapability.native`配下にあっても、`approvalCapability.getActionAvailabilityState`を実装してください。コアはこの可用性フックを使用して`enabled`と`disabled`を区別し、開始元チャネルがネイティブapprovalsをサポートするかどうかを判断し、ネイティブクライアントのフォールバック案内にそのチャネルを含めます。
- 重複するローカルapprovalプロンプトの非表示や配信前の入力中インジケーター送信など、チャネル固有のpayloadライフサイクル動作には`outbound.shouldSuppressLocalPayloadPrompt`または`outbound.beforeDeliverPayload`を使用してください。
- `approvalCapability.delivery`は、ネイティブapprovalルーティングまたはフォールバック抑制にのみ使用してください。
- `approvalCapability.render`は、共有rendererではなくチャネルが本当にカスタムapproval payloadsを必要とする場合にのみ使用してください。
- チャネルが、ネイティブexec approvalsを有効にするために必要な正確なconfig knobsをdisabled-path replyで説明したい場合は、`approvalCapability.describeExecApprovalSetup`を使用してください。このフックは`{ channel, channelLabel, accountId }`を受け取ります。名前付きアカウントのチャネルでは、トップレベルのデフォルトではなく、`channels.<channel>.accounts.<id>.execApprovals.*`のようなアカウントスコープのパスを表示する必要があります。
- チャネルが既存configから安定したowner類似のDM identityを推定できる場合は、approval固有のコアロジックを追加せずにsame-chat `/approve`を制限するため、`openclaw/plugin-sdk/approval-runtime`の`createResolvedApproverActionAuthAdapter`を使用してください。
- チャネルがネイティブapproval配信を必要とする場合は、チャネルコードをターゲット正規化とtransport hooksに集中させてください。`openclaw/plugin-sdk/approval-runtime`の`createChannelExecApprovalProfile`、`createChannelNativeOriginTargetResolver`、`createChannelApproverDmTargetResolver`、`createApproverRestrictedNativeApprovalCapability`、`createChannelNativeApprovalRuntime`を使用して、コアがリクエストフィルタリング、ルーティング、重複排除、有効期限、Gateway購読を担当するようにしてください。
- ネイティブapprovalチャネルは、`accountId`と`approvalKind`の両方をそれらのヘルパーに渡す必要があります。`accountId`はマルチアカウントapproval policyを正しいbotアカウントにスコープし、`approvalKind`はexecとplugin approvalの動作をコア内のハードコード分岐なしでチャネルに利用可能にします。
- 配信されたapproval id kindをエンドツーエンドで保持してください。ネイティブクライアントは、チャネルローカル状態からexecとplugin approvalルーティングを推測または書き換えるべきではありません。
- 異なるapproval kindは、意図的に異なるネイティブ表面を公開できます。
  現在のバンドル済みの例:
  - Slackは、execとplugin idsの両方でネイティブapprovalルーティングを利用可能に保ちます。
  - Matrixは、ネイティブDM/チャネルルーティングをexec approvalsのみに保ち、plugin approvalsは共有same-chat `/approve`パスに残します。
- `createApproverRestrictedNativeApprovalAdapter`は互換ラッパーとして引き続き存在しますが、新しいコードではcapability builderを優先し、プラグイン上に`approvalCapability`を公開してください。

ホットなチャネルエントリポイントでは、そのファミリーの一部だけが必要な場合、より狭いruntime subpathsを優先してください:

- `openclaw/plugin-sdk/approval-auth-runtime`
- `openclaw/plugin-sdk/approval-client-runtime`
- `openclaw/plugin-sdk/approval-delivery-runtime`
- `openclaw/plugin-sdk/approval-native-runtime`
- `openclaw/plugin-sdk/approval-reply-runtime`

同様に、より広いアンブレラ表面が不要な場合は、`openclaw/plugin-sdk/setup-runtime`、`openclaw/plugin-sdk/setup-adapter-runtime`、`openclaw/plugin-sdk/reply-runtime`、`openclaw/plugin-sdk/reply-dispatch-runtime`、`openclaw/plugin-sdk/reply-reference`、`openclaw/plugin-sdk/reply-chunking`を優先してください。

セットアップに特化すると:

- `openclaw/plugin-sdk/setup-runtime`は、runtime-safeなセットアップヘルパーを扱います:
  import-safe setup patch adapters（`createPatchedAccountSetupAdapter`、
  `createEnvPatchedAccountSetupAdapter`、
  `createSetupInputPresenceValidator`）、lookup-note出力、
  `promptResolvedAllowFrom`、`splitSetupEntries`、および委譲された
  setup-proxy builders
- `openclaw/plugin-sdk/setup-adapter-runtime`は、`createEnvPatchedAccountSetupAdapter`向けの狭いenv-aware adapter seamです
- `openclaw/plugin-sdk/channel-setup`は、optional-install setup
  buildersに加えていくつかのsetup-safe primitivesを扱います:
  `createOptionalChannelSetupSurface`、`createOptionalChannelSetupAdapter`、

チャネルがenv-driven setupやauthをサポートし、汎用の起動/configフローがruntime読み込み前にそれらのenv名を知る必要がある場合は、プラグインマニフェストの`channelEnvVars`でそれらを宣言してください。チャネルruntimeの`envVars`またはローカル定数は、オペレーター向けコピー専用にしてください。
`createOptionalChannelSetupWizard`、`DEFAULT_ACCOUNT_ID`、
`createTopLevelChannelDmPolicy`、`setSetupChannelEnabled`、および
`splitSetupEntries`

- より重い共有setup/config helpers、たとえば
  `moveSingleAccountChannelSectionToDefaultAccount(...)`
  も必要な場合にのみ、より広い`openclaw/plugin-sdk/setup` seamを使用してください

チャネルがセットアップ表面で単に「まずこのプラグインをインストールしてください」と案内したいだけなら、`createOptionalChannelSetupSurface(...)`を優先してください。生成されるadapter/wizardはconfig書き込みと最終化でfail closedとなり、検証、最終化、docs-link copy全体で同じinstall-requiredメッセージを再利用します。

その他のホットなチャネルパスでも、より広いレガシー表面より狭いヘルパーを優先してください:

- マルチアカウントconfigと
  default-accountフォールバックには`openclaw/plugin-sdk/account-core`、
  `openclaw/plugin-sdk/account-id`、
  `openclaw/plugin-sdk/account-resolution`、および
  `openclaw/plugin-sdk/account-helpers`
- 受信route/envelopeと
  record-and-dispatch配線には`openclaw/plugin-sdk/inbound-envelope`と
  `openclaw/plugin-sdk/inbound-reply-dispatch`
- ターゲット解析/一致には`openclaw/plugin-sdk/messaging-targets`
- メディア読み込みと送信
  identity/send delegatesには`openclaw/plugin-sdk/outbound-media`と
  `openclaw/plugin-sdk/outbound-runtime`
- thread-bindingライフサイクル
  とadapter registrationには`openclaw/plugin-sdk/thread-bindings-runtime`
- レガシーなagent/media
  payload field layoutが引き続き必要な場合にのみ`openclaw/plugin-sdk/agent-media-payload`
- Telegramカスタムコマンドの
  正規化、重複/競合検証、およびフォールバック安定なcommand
  config contractには`openclaw/plugin-sdk/telegram-command-config`

auth専用チャネルは通常、デフォルトパスで十分です。コアがapprovalsを処理し、プラグインは送信/auth capabilitiesを公開するだけです。Matrix、Slack、Telegram、カスタムチャットtransportのようなネイティブapprovalチャネルでは、独自にapproval lifecycleを実装するのではなく、共有のネイティブヘルパーを使用する必要があります。

## ウォークスルー

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="パッケージとマニフェスト">
    標準的なプラグインファイルを作成します。`package.json`内の`channel`フィールドが、
    これをチャネルプラグインにする要素です。完全なパッケージメタデータ表面については、
    [Plugin Setup and Config](/ja-JP/plugins/sdk-setup#openclawchannel)を参照してください:

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
    `ChannelPlugin`インターフェースには、多数の任意adapter surfacesがあります。まず
    最小限の`id`と`setup`から始め、必要に応じてadaptersを追加してください。

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

    <Accordion title="createChatChannelPluginが行ってくれること">
      低レベルのadapter interfacesを手動実装する代わりに、
      宣言的なオプションを渡すと、builderがそれらを構成します:

      | Option | 配線されるもの |
      | --- | --- |
      | `security.dm` | config fieldsからのスコープ付きDM security resolver |
      | `pairing.text` | コード交換を伴うテキストベースのDM pairing flow |
      | `threading` | reply-to-mode resolver（固定、account-scoped、またはcustom） |
      | `outbound.attachedResults` | 結果メタデータ（message IDs）を返すsend functions |

      完全に制御したい場合は、宣言的オプションの代わりに生のadapter objectsを渡すこともできます。
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

    チャネル所有のCLI descriptorsは`registerCliMetadata(...)`に置いてください。これによりOpenClawは、
    完全なチャネルruntimeを有効化せずにそれらをルートヘルプに表示でき、
    通常の完全読み込みでも実際のコマンド登録のため同じdescriptorsを取得できます。
    `registerFull(...)`はruntime専用の処理に保持してください。
    `registerFull(...)`がGateway RPC methodsを登録する場合は、
    プラグイン固有のprefixを使用してください。コア管理namespaces（`config.*`、
    `exec.approvals.*`、`wizard.*`、`update.*`）は予約済みであり、常に
    `operator.admin`に解決されます。
    `defineChannelPluginEntry`は登録モードの分割を自動的に処理します。すべての
    オプションについては[Entry Points](/ja-JP/plugins/sdk-entrypoints#definechannelpluginentry)を参照してください。

  </Step>

  <Step title="セットアップエントリを追加する">
    オンボーディング中の軽量読み込み用に`setup-entry.ts`を作成します:

    ```typescript setup-entry.ts
    import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineSetupPluginEntry(acmeChatPlugin);
    ```

    OpenClawは、チャネルが無効または未設定の場合、完全なエントリの代わりにこれを読み込みます。
    これにより、セットアップフロー中に重いruntime codeを引き込むのを避けられます。
    詳細は[Setup and Config](/ja-JP/plugins/sdk-setup#setup-entry)を参照してください。

  </Step>

  <Step title="受信メッセージを処理する">
    プラグインは、プラットフォームからメッセージを受信し、それを
    OpenClawへ転送する必要があります。典型的なパターンは、リクエストを検証し、
    チャネルの受信ハンドラー経由でディスパッチするwebhookです:

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
      受信メッセージ処理はチャネル固有です。各チャネルプラグインが
      独自の受信パイプラインを担当します。実際のパターンについては、
      バンドル済みチャネルプラグイン
      （たとえばMicrosoft TeamsまたはGoogle Chatプラグインパッケージ）を参照してください。
    </Note>

  </Step>

<a id="step-6-test"></a>
<Step title="テスト">
`src/channel.test.ts`にcolocated testsを書きます:

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

    共有test helpersについては、[Testing](/ja-JP/plugins/sdk-testing)を参照してください。

  </Step>
</Steps>

## ファイル構成

```
<bundled-plugin-root>/acme-chat/
├── package.json              # openclaw.channel metadata
├── openclaw.plugin.json      # config schemaを含むManifest
├── index.ts                  # defineChannelPluginEntry
├── setup-entry.ts            # defineSetupPluginEntry
├── api.ts                    # Public exports（任意）
├── runtime-api.ts            # Internal runtime exports（任意）
└── src/
    ├── channel.ts            # createChatChannelPlugin経由のChannelPlugin
    ├── channel.test.ts       # Tests
    ├── client.ts             # Platform API client
    └── runtime.ts            # Runtime store（必要な場合）
```

## 高度なトピック

<CardGroup cols={2}>
  <Card title="スレッド化オプション" icon="git-branch" href="/ja-JP/plugins/sdk-entrypoints#registration-mode">
    固定、account-scoped、またはcustom reply modes
  </Card>
  <Card title="Message tool統合" icon="puzzle" href="/ja-JP/plugins/architecture#channel-plugins-and-the-shared-message-tool">
    describeMessageToolとaction discovery
  </Card>
  <Card title="ターゲット解決" icon="crosshair" href="/ja-JP/plugins/architecture#channel-target-resolution">
    inferTargetChatType、looksLikeId、resolveTarget
  </Card>
  <Card title="Runtime helpers" icon="settings" href="/ja-JP/plugins/sdk-runtime">
    TTS、STT、media、api.runtime経由のsubagent
  </Card>
</CardGroup>

<Note>
一部のバンドル済みhelper seamsは、バンドル済みプラグインの保守と
互換性のために引き続き存在します。これらは新しいチャネルプラグインに推奨されるパターンではありません。
そのバンドル済みプラグインファミリーを直接保守している場合を除き、
共通SDK表面の汎用channel/setup/reply/runtime subpathsを優先してください。
</Note>

## 次のステップ

- [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins) — プラグインがモデルも提供する場合
- [SDK Overview](/ja-JP/plugins/sdk-overview) — 完全なsubpath importリファレンス
- [SDK Testing](/ja-JP/plugins/sdk-testing) — test utilitiesとcontract tests
- [Plugin Manifest](/ja-JP/plugins/manifest) — 完全なmanifest schema
