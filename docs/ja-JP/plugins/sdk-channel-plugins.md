---
read_when:
    - 新しいメッセージングチャネルPluginを構築しています
    - OpenClawをメッセージングプラットフォームに接続したいと考えています
    - ChannelPluginアダプターの表面を理解する必要があります
sidebarTitle: Channel Plugins
summary: OpenClaw向けメッセージングチャネルPluginを構築するためのステップごとのガイド
title: チャネルPluginの構築
x-i18n:
    generated_at: "2026-04-15T19:41:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: 80e47e61d1e47738361692522b79aff276544446c58a7b41afe5296635dfad4b
    source_path: plugins/sdk-channel-plugins.md
    workflow: 15
---

# チャネルPluginの構築

このガイドでは、OpenClawをメッセージングプラットフォームに接続するチャネルpluginの構築方法を説明します。最終的には、DMセキュリティ、ペアリング、返信スレッド化、送信メッセージングを備えた動作するチャネルを完成させます。

<Info>
  OpenClaw pluginをこれまでに一度も構築したことがない場合は、基本的なパッケージ構造とマニフェスト設定について、まず
  [はじめに](/ja-JP/plugins/building-plugins)を読んでください。
</Info>

## チャネルPluginの仕組み

チャネルpluginには、独自の送信・編集・リアクションツールは不要です。OpenClawは、コアに1つの共有`message`ツールを保持しています。pluginが担うのは次の項目です。

- **Config** — アカウント解決とセットアップウィザード
- **Security** — DMポリシーと許可リスト
- **Pairing** — DM承認フロー
- **Session grammar** — プロバイダー固有の会話IDを、ベースチャット、スレッドID、親フォールバックにどのように対応付けるか
- **Outbound** — テキスト、メディア、投票をプラットフォームへ送信すること
- **Threading** — 返信をどのようにスレッド化するか

コアは、共有messageツール、プロンプト配線、外側のセッションキー形状、汎用的な`:thread:`管理、ディスパッチを担います。

チャネルがメディアソースを運ぶmessage-toolパラメーターを追加する場合は、それらのパラメーター名を`describeMessageTool(...).mediaSourceParams`を通じて公開してください。コアはその明示的なリストを、サンドボックスパスの正規化と送信メディアアクセス方針に使用するため、plugin側でプロバイダー固有のアバター、添付ファイル、またはカバー画像パラメーターのために共有コアの特別扱いを追加する必要はありません。
できれば、`{ "set-profile": ["avatarUrl", "avatarPath"] }`のようなアクションキー付きマップを返してください。そうすることで、無関係なアクションが別のアクションのメディア引数を継承しません。意図的にすべての公開アクションで共有されるパラメーターであれば、フラットな配列でも引き続き利用できます。

プラットフォームが会話IDの中に追加のスコープを保存する場合は、その解析をplugin内で`messaging.resolveSessionConversation(...)`を使って行ってください。これは、`rawId`をベース会話ID、任意のスレッドID、明示的な`baseConversationId`、および任意の`parentConversationCandidates`に対応付けるための正規のフックです。
`parentConversationCandidates`を返す場合は、最も狭い親から最も広い/ベース会話までの順に並べてください。

チャネルレジストリが起動する前に同じ解析を必要とする同梱pluginは、一致する`resolveSessionConversation(...)`エクスポートを持つトップレベルの`session-key-api.ts`ファイルも公開できます。コアは、実行時pluginレジストリがまだ利用できない場合に限って、このブートストラップ安全なサーフェスを使用します。

`messaging.resolveParentConversationCandidates(...)`は、pluginが汎用/生のIDに加えて親フォールバックだけを必要とする場合の、レガシー互換フォールバックとして引き続き利用できます。両方のフックが存在する場合、コアはまず`resolveSessionConversation(...).parentConversationCandidates`を使用し、正規フックがそれらを省略した場合にのみ`resolveParentConversationCandidates(...)`へフォールバックします。

## 承認とチャネル機能

ほとんどのチャネルpluginでは、承認固有のコードは不要です。

- コアは、同一チャット内の`/approve`、共有承認ボタンのペイロード、汎用フォールバック配信を担います。
- チャネルが承認固有の動作を必要とする場合は、チャネルplugin上で1つの`approvalCapability`オブジェクトを使うようにしてください。
- `ChannelPlugin.approvals`は削除されました。承認の配信/ネイティブ/レンダリング/認証に関する情報は`approvalCapability`に置いてください。
- `plugin.auth`はlogin/logout専用です。コアはもはやそのオブジェクトから承認認証フックを読み取りません。
- `approvalCapability.authorizeActorAction`と`approvalCapability.getActionAvailabilityState`が、正規の承認認証シームです。
- 同一チャット承認の認証可用性には`approvalCapability.getActionAvailabilityState`を使用してください。
- チャネルがネイティブexec承認を公開する場合、開始サーフェス/ネイティブクライアント状態が同一チャット承認認証と異なるときは、`approvalCapability.getExecInitiatingSurfaceState`を使用してください。コアはこのexec固有フックを使って、開始チャネルがネイティブexec承認をサポートしているかどうかを判定し、`enabled`と`disabled`を区別し、ネイティブクライアントのフォールバック案内にそのチャネルを含めます。`createApproverRestrictedNativeApprovalCapability(...)`は、一般的なケース向けにこれを補います。
- 重複するローカル承認プロンプトの非表示や、配信前の入力中インジケーター送信など、チャネル固有のペイロードライフサイクル動作には、`outbound.shouldSuppressLocalPayloadPrompt`または`outbound.beforeDeliverPayload`を使用してください。
- `approvalCapability.delivery`は、ネイティブ承認ルーティングまたはフォールバック抑制にのみ使用してください。
- チャネル所有のネイティブ承認情報には`approvalCapability.nativeRuntime`を使用してください。ホットなチャネルエントリーポイントでは、`createLazyChannelApprovalNativeRuntimeAdapter(...)`でこれを遅延化してください。これにより、コアが承認ライフサイクルを組み立てつつ、必要時に実行時モジュールをimportできます。
- チャネルが共有レンダラーの代わりに本当にカスタム承認ペイロードを必要とする場合にのみ、`approvalCapability.render`を使用してください。
- チャネルが、無効パスの返信でネイティブexec承認を有効化するために必要な正確なconfigノブを説明したい場合は、`approvalCapability.describeExecApprovalSetup`を使用してください。このフックは`{ channel, channelLabel, accountId }`を受け取ります。名前付きアカウントのチャネルは、トップレベルのデフォルトではなく、`channels.<channel>.accounts.<id>.execApprovals.*`のようなアカウントスコープ付きパスを描画する必要があります。
- チャネルが既存configから安定したオーナー的DMアイデンティティを推論できる場合は、承認固有のコアロジックを追加せずに同一チャット`/approve`を制限するため、`openclaw/plugin-sdk/approval-runtime`の`createResolvedApproverActionAuthAdapter`を使用してください。
- チャネルがネイティブ承認配信を必要とする場合、チャネルコードはターゲット正規化と転送/表示情報に集中させてください。`openclaw/plugin-sdk/approval-runtime`の`createChannelExecApprovalProfile`、`createChannelNativeOriginTargetResolver`、`createChannelApproverDmTargetResolver`、`createApproverRestrictedNativeApprovalCapability`を使用してください。チャネル固有の情報は`approvalCapability.nativeRuntime`の背後に置き、理想的には`createChannelApprovalNativeRuntimeAdapter(...)`または`createLazyChannelApprovalNativeRuntimeAdapter(...)`を通してください。そうすることで、コアがハンドラーを組み立て、リクエストフィルタリング、ルーティング、重複排除、有効期限、Gateway購読、別経路通知を担えます。`nativeRuntime`はいくつかのより小さなシームに分かれています。
- `availability` — アカウントが設定されているか、およびリクエストを処理すべきかどうか
- `presentation` — 共有承認ビューモデルを、保留/解決済み/期限切れのネイティブペイロードまたは最終アクションへ対応付ける
- `transport` — ターゲットを準備し、ネイティブ承認メッセージを送信/更新/削除する
- `interactions` — ネイティブボタンやリアクションのための任意のbind/unbind/clear-actionフック
- `observe` — 任意の配信診断フック
- チャネルがクライアント、トークン、Boltアプリ、Webhook受信側のような実行時所有オブジェクトを必要とする場合は、`openclaw/plugin-sdk/channel-runtime-context`を通じて登録してください。汎用のruntime-contextレジストリにより、コアは承認固有のラッパー接着コードを追加せずに、チャネル起動状態からcapability駆動ハンドラーをブートストラップできます。
- capability駆動シームだけではまだ表現力が足りない場合にのみ、下位レベルの`createChannelApprovalHandler`または`createChannelNativeApprovalRuntime`に手を伸ばしてください。
- ネイティブ承認チャネルは、`accountId`と`approvalKind`の両方をそれらのヘルパーに渡す必要があります。`accountId`は複数アカウント承認ポリシーを正しいbotアカウントにスコープし、`approvalKind`はコア内のハードコード分岐なしでexec対plugin承認動作をチャネルで利用可能にします。
- コアは現在、承認の再ルーティング通知も担います。チャネルpluginは、`createChannelNativeApprovalRuntime`から独自の「承認はDM/別チャネルへ送られました」フォローアップメッセージを送信すべきではありません。代わりに、共有承認capabilityヘルパーを通じて正確な発信元+承認者DMルーティングを公開し、開始チャットへ通知を投稿する前に実際の配信をコアに集約させてください。
- 配信済み承認IDの種類は、エンドツーエンドで保持してください。ネイティブクライアントは、チャネルローカル状態からexec対plugin承認ルーティングを推測したり書き換えたりしてはいけません。
- 異なる承認種別は、意図的に異なるネイティブサーフェスを公開できます。
  現在の同梱例:
  - Slackは、execとpluginの両方のIDに対してネイティブ承認ルーティングを利用可能に保っています。
  - Matrixは、execとpluginの承認で認証を異ならせつつ、同じネイティブDM/チャネルルーティングとリアクションUXを維持しています。
- `createApproverRestrictedNativeApprovalAdapter`は互換ラッパーとして引き続き存在しますが、新しいコードではcapability builderを優先し、plugin上に`approvalCapability`を公開してください。

ホットなチャネルエントリーポイントでは、そのファミリーの一部だけが必要な場合、より狭いruntimeサブパスを優先してください。

- `openclaw/plugin-sdk/approval-auth-runtime`
- `openclaw/plugin-sdk/approval-client-runtime`
- `openclaw/plugin-sdk/approval-delivery-runtime`
- `openclaw/plugin-sdk/approval-gateway-runtime`
- `openclaw/plugin-sdk/approval-handler-adapter-runtime`
- `openclaw/plugin-sdk/approval-handler-runtime`
- `openclaw/plugin-sdk/approval-native-runtime`
- `openclaw/plugin-sdk/approval-reply-runtime`
- `openclaw/plugin-sdk/channel-runtime-context`

同様に、より広い傘型サーフェスが不要な場合は、`openclaw/plugin-sdk/setup-runtime`、`openclaw/plugin-sdk/setup-adapter-runtime`、`openclaw/plugin-sdk/reply-runtime`、`openclaw/plugin-sdk/reply-dispatch-runtime`、`openclaw/plugin-sdk/reply-reference`、`openclaw/plugin-sdk/reply-chunking`を優先してください。

セットアップについては、特に次のとおりです。

- `openclaw/plugin-sdk/setup-runtime`は、runtime-safeなセットアップヘルパーを扱います:
  import-safeなセットアップパッチアダプター（`createPatchedAccountSetupAdapter`、
  `createEnvPatchedAccountSetupAdapter`,
  `createSetupInputPresenceValidator`）、lookup-note出力、
  `promptResolvedAllowFrom`、`splitSetupEntries`、委譲された
  setup-proxy builder
- `openclaw/plugin-sdk/setup-adapter-runtime`は、`createEnvPatchedAccountSetupAdapter`向けの狭いenv対応アダプターシームです
- `openclaw/plugin-sdk/channel-setup`は、オプションインストールのセットアップbuilderと、いくつかのセットアップ安全なプリミティブを扱います:
  `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`,

チャネルがenv駆動のセットアップまたは認証をサポートし、汎用の起動/configフローがruntimeロード前にそれらのenv名を知る必要がある場合は、pluginマニフェストで`channelEnvVars`として宣言してください。チャネルruntimeの`envVars`またはローカル定数は、運用者向けコピー専用にしてください。
`createOptionalChannelSetupWizard`, `DEFAULT_ACCOUNT_ID`,
`createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, および
`splitSetupEntries`

- より重い共有セットアップ/configヘルパー、たとえば
  `moveSingleAccountChannelSectionToDefaultAccount(...)`も必要な場合にのみ、より広い`openclaw/plugin-sdk/setup`シームを使用してください

チャネルがセットアップサーフェス内で「まずこのpluginをインストールしてください」と告知したいだけなら、`createOptionalChannelSetupSurface(...)`を優先してください。生成されるアダプター/ウィザードはconfig書き込みと最終化でフェイルクローズし、検証、最終化、ドキュメントリンク文言の各所で同じインストール必須メッセージを再利用します。

その他のホットなチャネルパスでも、より広いレガシーサーフェスより狭いヘルパーを優先してください。

- `openclaw/plugin-sdk/account-core`、
  `openclaw/plugin-sdk/account-id`、
  `openclaw/plugin-sdk/account-resolution`、および
  `openclaw/plugin-sdk/account-helpers` は、複数アカウントconfigと
  デフォルトアカウントフォールバック向けです
- `openclaw/plugin-sdk/inbound-envelope` と
  `openclaw/plugin-sdk/inbound-reply-dispatch` は、受信ルート/エンベロープと
  record-and-dispatch配線向けです
- `openclaw/plugin-sdk/messaging-targets` は、ターゲット解析/マッチング向けです
- `openclaw/plugin-sdk/outbound-media` と
  `openclaw/plugin-sdk/outbound-runtime` は、メディア読み込みと送信
  アイデンティティ/送信デリゲート向けです
- `openclaw/plugin-sdk/thread-bindings-runtime` は、スレッドバインディングのライフサイクル
  とアダプター登録向けです
- `openclaw/plugin-sdk/agent-media-payload` は、レガシーなagent/media
  ペイロードのフィールドレイアウトが依然必要な場合にのみ使用してください
- `openclaw/plugin-sdk/telegram-command-config` は、Telegramカスタムコマンドの
  正規化、重複/競合検証、およびフォールバック安定なコマンド
  config契約向けです

認証専用チャネルは通常、デフォルトのパスで十分です。コアが承認を処理し、pluginは送信/認証capabilityを公開するだけです。Matrix、Slack、Telegram、カスタムチャット転送のようなネイティブ承認チャネルは、独自の承認ライフサイクルを実装するのではなく、共有ネイティブヘルパーを使うべきです。

## 受信メンションポリシー

受信メンション処理は、次の2層に分けてください。

- plugin所有の証拠収集
- 共有ポリシー評価

共有レイヤーには`openclaw/plugin-sdk/channel-inbound`を使用してください。

pluginローカルロジックに適しているもの:

- botへの返信検出
- bot引用の検出
- スレッド参加チェック
- サービス/システムメッセージの除外
- bot参加を証明するために必要なプラットフォームネイティブキャッシュ

共有ヘルパーに適しているもの:

- `requireMention`
- 明示的メンション結果
- 暗黙的メンション許可リスト
- コマンドバイパス
- 最終スキップ判定

推奨フロー:

1. ローカルのメンション情報を計算します。
2. その情報を`resolveInboundMentionDecision({ facts, policy })`に渡します。
3. 受信ゲートでは`decision.effectiveWasMentioned`、`decision.shouldBypassMention`、`decision.shouldSkip`を使用します。

```typescript
import {
  implicitMentionKindWhen,
  matchesMentionWithExplicit,
  resolveInboundMentionDecision,
} from "openclaw/plugin-sdk/channel-inbound";

const mentionMatch = matchesMentionWithExplicit(text, {
  mentionRegexes,
  mentionPatterns,
});

const facts = {
  canDetectMention: true,
  wasMentioned: mentionMatch.matched,
  hasAnyMention: mentionMatch.hasExplicitMention,
  implicitMentionKinds: [
    ...implicitMentionKindWhen("reply_to_bot", isReplyToBot),
    ...implicitMentionKindWhen("quoted_bot", isQuoteOfBot),
  ],
};

const decision = resolveInboundMentionDecision({
  facts,
  policy: {
    isGroup,
    requireMention,
    allowedImplicitMentionKinds: requireExplicitMention ? [] : ["reply_to_bot", "quoted_bot"],
    allowTextCommands,
    hasControlCommand,
    commandAuthorized,
  },
});

if (decision.shouldSkip) return;
```

`api.runtime.channel.mentions`は、すでにruntime injectionに依存している同梱チャネルplugin向けに、同じ共有メンションヘルパーを公開します。

- `buildMentionRegexes`
- `matchesMentionPatterns`
- `matchesMentionWithExplicit`
- `implicitMentionKindWhen`
- `resolveInboundMentionDecision`

古い`resolveMentionGating*`ヘルパーは、互換エクスポート専用として`openclaw/plugin-sdk/channel-inbound`に引き続き残っています。新しいコードでは`resolveInboundMentionDecision({ facts, policy })`を使用してください。

## ウォークスルー

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="パッケージとマニフェスト">
    標準のpluginファイルを作成します。`package.json`内の`channel`フィールドが、これをチャネルpluginにする要素です。完全なパッケージメタデータのサーフェスについては、
    [Plugin Setup and Config](/ja-JP/plugins/sdk-setup#openclaw-channel)を参照してください。

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

  <Step title="チャネルpluginオブジェクトを構築する">
    `ChannelPlugin`インターフェースには、多数のオプションのアダプターサーフェスがあります。まずは最小限、つまり`id`と`setup`から始め、必要に応じてアダプターを追加してください。

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
      低レベルのアダプターインターフェースを手動で実装する代わりに、宣言的なオプションを渡すと、builderがそれらを組み合わせます。

      | オプション | 配線される内容 |
      | --- | --- |
      | `security.dm` | configフィールドからスコープ付きDMセキュリティリゾルバー |
      | `pairing.text` | コード交換を伴うテキストベースのDMペアリングフロー |
      | `threading` | reply-to-modeリゾルバー（固定、アカウントスコープ、またはカスタム） |
      | `outbound.attachedResults` | 結果メタデータ（メッセージID）を返す送信関数 |

      完全な制御が必要な場合は、宣言的オプションの代わりに生のアダプターオブジェクトを渡すこともできます。
    </Accordion>

  </Step>

  <Step title="エントリーポイントを配線する">
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

    チャネル所有のCLI descriptorは`registerCliMetadata(...)`に置いてください。これにより、OpenClawは完全なチャネルruntimeを起動せずにルートヘルプでそれらを表示でき、通常の完全ロードでも実際のコマンド登録に同じdescriptorを利用できます。`registerFull(...)`はruntime専用の処理に使ってください。
    `registerFull(...)`がGateway RPCメソッドを登録する場合は、plugin固有のプレフィックスを使用してください。コア管理名前空間（`config.*`、`exec.approvals.*`、`wizard.*`、`update.*`）は予約されており、常に`operator.admin`に解決されます。
    `defineChannelPluginEntry`は、この登録モード分割を自動的に処理します。すべてのオプションについては
    [Entry Points](/ja-JP/plugins/sdk-entrypoints#definechannelpluginentry)を参照してください。

  </Step>

  <Step title="セットアップエントリを追加する">
    オンボーディング中の軽量ロード用に`setup-entry.ts`を作成します:

    ```typescript setup-entry.ts
    import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineSetupPluginEntry(acmeChatPlugin);
    ```

    OpenClawは、チャネルが無効または未設定のときに、完全なエントリの代わりにこれをロードします。これにより、セットアップフロー中に重いruntimeコードを引き込まずに済みます。詳細は[Setup and Config](/ja-JP/plugins/sdk-setup#setup-entry)を参照してください。

    セットアップ安全なエクスポートをサイドカーモジュールに分離している同梱workspaceチャネルは、
    `openclaw/plugin-sdk/channel-entry-contract`の`defineBundledChannelSetupEntry(...)`を使用できます。これは、明示的なセットアップ時runtime setterも必要な場合に有効です。

  </Step>

  <Step title="受信メッセージを処理する">
    pluginは、プラットフォームからメッセージを受信し、それをOpenClawへ転送する必要があります。一般的なパターンは、リクエストを検証し、チャネルの受信ハンドラーを通じてディスパッチするWebhookです。

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
      受信メッセージ処理はチャネル固有です。各チャネルpluginが独自の受信パイプラインを所有します。実際のパターンについては、同梱チャネルplugin
      （たとえばMicrosoft TeamsまたはGoogle Chatのpluginパッケージ）を見てください。
    </Note>

  </Step>

<a id="step-6-test"></a>
<Step title="テスト">
`src/channel.test.ts`に同居テストを書いてください:

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

    共有テストヘルパーについては、[Testing](/ja-JP/plugins/sdk-testing)を参照してください。

  </Step>
</Steps>

## ファイル構成

```
<bundled-plugin-root>/acme-chat/
├── package.json              # openclaw.channel メタデータ
├── openclaw.plugin.json      # configスキーマを含むマニフェスト
├── index.ts                  # defineChannelPluginEntry
├── setup-entry.ts            # defineSetupPluginEntry
├── api.ts                    # 公開エクスポート（任意）
├── runtime-api.ts            # 内部runtimeエクスポート（任意）
└── src/
    ├── channel.ts            # createChatChannelPluginによるChannelPlugin
    ├── channel.test.ts       # テスト
    ├── client.ts             # プラットフォームAPIクライアント
    └── runtime.ts            # runtimeストア（必要な場合）
```

## 高度なトピック

<CardGroup cols={2}>
  <Card title="スレッド化オプション" icon="git-branch" href="/ja-JP/plugins/sdk-entrypoints#registration-mode">
    固定、アカウントスコープ、またはカスタムの返信モード
  </Card>
  <Card title="messageツール統合" icon="puzzle" href="/ja-JP/plugins/architecture#channel-plugins-and-the-shared-message-tool">
    describeMessageTool とアクションディスカバリー
  </Card>
  <Card title="ターゲット解決" icon="crosshair" href="/ja-JP/plugins/architecture#channel-target-resolution">
    inferTargetChatType, looksLikeId, resolveTarget
  </Card>
  <Card title="runtimeヘルパー" icon="settings" href="/ja-JP/plugins/sdk-runtime">
    api.runtime を介したTTS、STT、メディア、subagent
  </Card>
</CardGroup>

<Note>
一部の同梱ヘルパーシームは、同梱pluginの保守と互換性のために引き続き存在します。これらは新しいチャネルpluginに推奨されるパターンではありません。その同梱pluginファミリーを直接保守しているのでない限り、共通SDKサーフェスの汎用的なchannel/setup/reply/runtimeサブパスを優先してください。
</Note>

## 次のステップ

- [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins) — pluginがモデルも提供する場合
- [SDK Overview](/ja-JP/plugins/sdk-overview) — 完全なサブパスimportリファレンス
- [SDK Testing](/ja-JP/plugins/sdk-testing) — テストユーティリティと契約テスト
- [Plugin Manifest](/ja-JP/plugins/manifest) — 完全なマニフェストスキーマ
