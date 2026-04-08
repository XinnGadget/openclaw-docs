---
read_when:
    - 新しいメッセージングチャネルプラグインを構築している場合
    - OpenClawをメッセージングプラットフォームに接続したい場合
    - ChannelPluginアダプターサーフェスを理解する必要がある場合
sidebarTitle: Channel Plugins
summary: OpenClaw向けメッセージングチャネルプラグインを構築するためのステップバイステップガイド
title: チャネルプラグインの構築
x-i18n:
    generated_at: "2026-04-08T02:17:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: d23365b6d92006b30e671f9f0afdba40a2b88c845c5d2299d71c52a52985672f
    source_path: plugins/sdk-channel-plugins.md
    workflow: 15
---

# チャネルプラグインの構築

このガイドでは、OpenClawをメッセージングプラットフォームに接続するチャネルプラグインの構築手順を説明します。最後には、DMセキュリティ、
pairing、返信のスレッド化、アウトバウンドメッセージングを備えた動作するチャネルを手に入れられます。

<Info>
  まだOpenClawプラグインを一度も作成したことがない場合は、基本的なパッケージ
  構造とマニフェスト設定について、先に
  [はじめに](/ja-JP/plugins/building-plugins)を読んでください。
</Info>

## チャネルプラグインの仕組み

チャネルプラグインは、独自の send/edit/react ツールを必要としません。OpenClawは
共有の `message` ツールを1つcoreに保持します。プラグインが所有するのは次の部分です:

- **設定** — アカウント解決とセットアップウィザード
- **セキュリティ** — DMポリシーと許可リスト
- **pairing** — DM承認フロー
- **セッション文法** — プロバイダー固有の会話IDを、どのようにベースチャット、thread id、親フォールバックに対応付けるか
- **アウトバウンド** — テキスト、メディア、pollをプラットフォームへ送信
- **スレッド化** — 返信をどのようにスレッド化するか

coreは共有messageツール、プロンプト配線、外側のセッションキー形状、
汎用の `:thread:` 管理、およびディスパッチを所有します。

プラットフォームが会話ID内に追加スコープを保存する場合は、その解析を
`messaging.resolveSessionConversation(...)` を使ってプラグイン内に保持してください。これが、
`rawId` をベース会話ID、任意のthread id、明示的な `baseConversationId`、
および `parentConversationCandidates` に対応付けるための正規のフックです。
`parentConversationCandidates` を返す場合は、それらを最も狭い親から最も広い/ベース会話の順に並べてください。

チャネルレジストリが起動する前に同じ解析が必要なバンドルプラグインは、
一致する `resolveSessionConversation(...)` エクスポートを持つトップレベルの
`session-key-api.ts` ファイルを公開することもできます。coreは、ランタイムの
プラグインレジストリがまだ利用できない場合にのみ、そのブートストラップ安全なサーフェスを使います。

`messaging.resolveParentConversationCandidates(...)` は、
プラグインが汎用/raw id に加えて親フォールバックだけを必要とする場合の
レガシー互換フォールバックとして引き続き利用できます。両方のフックが存在する場合、
coreはまず `resolveSessionConversation(...).parentConversationCandidates` を使い、
正規フックがそれらを省略した場合にのみ
`resolveParentConversationCandidates(...)` へフォールバックします。

## 承認とチャネル機能

ほとんどのチャネルプラグインでは、承認専用コードは不要です。

- coreは、同一チャット内の `/approve`、共有承認ボタンペイロード、および汎用フォールバック配信を所有します。
- チャネルに承認固有の動作が必要な場合は、チャネルプラグイン上の1つの `approvalCapability` オブジェクトを優先してください。
- `ChannelPlugin.approvals` は削除されました。承認配信/ネイティブ/レンダリング/認証の情報は `approvalCapability` に置いてください。
- `plugin.auth` は login/logout 専用です。coreはそのオブジェクトから承認認証フックをもう読み取りません。
- `approvalCapability.authorizeActorAction` と `approvalCapability.getActionAvailabilityState` が正規の承認認証シームです。
- 同一チャットでの承認認証可用性には `approvalCapability.getActionAvailabilityState` を使ってください。
- チャネルがネイティブexec承認を公開する場合は、開始サーフェス/ネイティブクライアント状態が同一チャットの承認認証と異なるときに `approvalCapability.getExecInitiatingSurfaceState` を使ってください。coreはこのexec専用フックを使って `enabled` と `disabled` を区別し、開始元チャネルがネイティブexec承認をサポートするかを判断し、ネイティブクライアントのフォールバックガイダンスにそのチャネルを含めます。`createApproverRestrictedNativeApprovalCapability(...)` は一般的なケース向けにこれを埋めます。
- 重複するローカル承認プロンプトの非表示や、配信前の入力中インジケーター送信のようなチャネル固有のペイロードライフサイクル動作には、`outbound.shouldSuppressLocalPayloadPrompt` または `outbound.beforeDeliverPayload` を使ってください。
- `approvalCapability.delivery` はネイティブ承認ルーティングまたはフォールバック抑制にのみ使ってください。
- チャネル所有のネイティブ承認情報には `approvalCapability.nativeRuntime` を使ってください。ホットなチャネルエントリポイントでは、`createLazyChannelApprovalNativeRuntimeAdapter(...)` でこれを遅延化し、必要時にランタイムモジュールをインポートしつつ、coreが承認ライフサイクルを組み立てられるようにしてください。
- チャネルが共有レンダラーではなく、本当にカスタム承認ペイロードを必要とする場合にのみ `approvalCapability.render` を使ってください。
- チャネルが、ネイティブexec承認を有効にするために必要な正確な設定ノブを無効化パス返信で説明したい場合は `approvalCapability.describeExecApprovalSetup` を使ってください。このフックは `{ channel, channelLabel, accountId }` を受け取ります。名前付きアカウントチャネルでは、トップレベルのデフォルトではなく `channels.<channel>.accounts.<id>.execApprovals.*` のようなアカウントスコープのパスをレンダリングする必要があります。
- チャネルが既存設定から安定した所有者類似のDM identityを推測できる場合は、承認固有のcoreロジックを追加せずに同一チャットの `/approve` を制限するために `openclaw/plugin-sdk/approval-runtime` の `createResolvedApproverActionAuthAdapter` を使ってください。
- チャネルがネイティブ承認配信を必要とする場合、チャネルコードはターゲット正規化と転送/表示情報に集中させてください。`openclaw/plugin-sdk/approval-runtime` の `createChannelExecApprovalProfile`、`createChannelNativeOriginTargetResolver`、`createChannelApproverDmTargetResolver`、`createApproverRestrictedNativeApprovalCapability` を使ってください。チャネル固有の情報は `approvalCapability.nativeRuntime` の背後に置き、理想的には `createChannelApprovalNativeRuntimeAdapter(...)` または `createLazyChannelApprovalNativeRuntimeAdapter(...)` を介して提供してください。そうすることで、coreがハンドラーを組み立て、リクエストフィルタリング、ルーティング、重複排除、有効期限、Gateway購読、および別経路配信通知を所有できます。`nativeRuntime` はいくつかの小さなシームに分かれています:
- `availability` — アカウントが設定済みかどうか、およびリクエストを処理すべきかどうか
- `presentation` — 共有承認ビューモデルを保留中/解決済み/期限切れのネイティブペイロードまたは最終アクションへ対応付け
- `transport` — ネイティブ承認メッセージのターゲット準備と送信/更新/削除
- `interactions` — ネイティブボタンやreaction向けの任意の bind/unbind/clear-action フック
- `observe` — 任意の配信診断フック
- チャネルがclient、token、Bolt app、webhook受信側のようなランタイム所有オブジェクトを必要とする場合は、`openclaw/plugin-sdk/channel-runtime-context` を通じて登録してください。汎用ランタイムコンテキストレジストリにより、coreは承認固有のラッパー接着コードを追加することなく、チャネル起動状態から機能駆動ハンドラーをブートストラップできます。
- 機能駆動シームでまだ表現しきれない場合にのみ、より低レベルな `createChannelApprovalHandler` または `createChannelNativeApprovalRuntime` を使ってください。
- ネイティブ承認チャネルは、`accountId` と `approvalKind` の両方をそれらのヘルパー経由でルーティングする必要があります。`accountId` はマルチアカウント承認ポリシーを正しいbotアカウントにスコープし、`approvalKind` はcore内のハードコード分岐なしで exec と plugin 承認の動作をチャネル側で利用可能にします。
- coreは現在、承認再ルーティング通知も所有しています。チャネルプラグインは `createChannelNativeApprovalRuntime` から独自の「承認はDM / 別チャネルに送られました」というフォローアップメッセージを送信すべきではありません。代わりに、共有承認機能ヘルパーを通じて正確な起点 + approver-DM ルーティングを公開し、開始チャットへ通知を投稿する前に、coreに実際の配信結果を集約させてください。
- 配信された承認IDの種類はエンドツーエンドで保持してください。ネイティブクライアントは、チャネルローカル状態から exec と plugin 承認ルーティングを推測または書き換えるべきではありません。
- 異なる承認種類は、意図的に異なるネイティブサーフェスを公開してもかまいません。
  現在のバンドル例:
  - Slack は exec と plugin の両方のIDでネイティブ承認ルーティングを利用可能に保ちます。
  - Matrix は exec と plugin の承認で同じネイティブDM/チャネルルーティングと reaction UX を維持しつつ、承認種類ごとに認証を変えられるようにしています。
- `createApproverRestrictedNativeApprovalAdapter` は依然として互換ラッパーとして存在しますが、新しいコードでは機能ビルダーを優先し、プラグイン上に `approvalCapability` を公開してください。

ホットなチャネルエントリポイントでは、このファミリーの一部だけが必要な場合、
より狭いランタイムsubpathを優先してください:

- `openclaw/plugin-sdk/approval-auth-runtime`
- `openclaw/plugin-sdk/approval-client-runtime`
- `openclaw/plugin-sdk/approval-delivery-runtime`
- `openclaw/plugin-sdk/approval-gateway-runtime`
- `openclaw/plugin-sdk/approval-handler-adapter-runtime`
- `openclaw/plugin-sdk/approval-handler-runtime`
- `openclaw/plugin-sdk/approval-native-runtime`
- `openclaw/plugin-sdk/approval-reply-runtime`
- `openclaw/plugin-sdk/channel-runtime-context`

同様に、より広い包括サーフェスが不要な場合は、
`openclaw/plugin-sdk/setup-runtime`、
`openclaw/plugin-sdk/setup-adapter-runtime`、
`openclaw/plugin-sdk/reply-runtime`、
`openclaw/plugin-sdk/reply-dispatch-runtime`、
`openclaw/plugin-sdk/reply-reference`、
`openclaw/plugin-sdk/reply-chunking` を優先してください。

セットアップについては特に:

- `openclaw/plugin-sdk/setup-runtime` は、ランタイム安全なセットアップヘルパーをカバーします:
  import-safe なセットアップパッチアダプター（`createPatchedAccountSetupAdapter`,
  `createEnvPatchedAccountSetupAdapter`,
  `createSetupInputPresenceValidator`）、lookup-note 出力、
  `promptResolvedAllowFrom`、`splitSetupEntries`、および委譲された
  setup-proxy ビルダー
- `openclaw/plugin-sdk/setup-adapter-runtime` は、`createEnvPatchedAccountSetupAdapter` 向けの狭い env 対応アダプターシームです
- `openclaw/plugin-sdk/channel-setup` は、オプションインストールのセットアップ
  ビルダーと、いくつかのセットアップ安全プリミティブをカバーします:
  `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`,

チャネルが env 駆動のセットアップまたは認証をサポートし、汎用の起動/設定
フローがランタイム読み込み前にその env 名を知る必要がある場合は、
プラグインマニフェストで `channelEnvVars` として宣言してください。チャネルランタイムの
`envVars` またはローカル定数は、operator 向けコピー専用にしてください。
`createOptionalChannelSetupWizard`, `DEFAULT_ACCOUNT_ID`,
`createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries`

- より重い共有セットアップ/設定ヘルパー、たとえば
  `moveSingleAccountChannelSectionToDefaultAccount(...)`
  も必要な場合にのみ、より広い `openclaw/plugin-sdk/setup` シームを使ってください

チャネルがセットアップサーフェスで「まずこのプラグインをインストールしてください」と広告したいだけであれば、
`createOptionalChannelSetupSurface(...)` を優先してください。生成される
adapter/wizard は設定書き込みと最終化で fail closed になり、検証、最終化、ドキュメントリンクの文言全体で同じインストール必須メッセージを再利用します。

他のホットなチャネルパスでも、より広いレガシーサーフェスより狭いヘルパーを優先してください:

- マルチアカウント設定とデフォルトアカウントフォールバックには
  `openclaw/plugin-sdk/account-core`、
  `openclaw/plugin-sdk/account-id`、
  `openclaw/plugin-sdk/account-resolution`、
  `openclaw/plugin-sdk/account-helpers`
- インバウンドroute/envelope と
  record-and-dispatch 配線には
  `openclaw/plugin-sdk/inbound-envelope` と
  `openclaw/plugin-sdk/inbound-reply-dispatch`
- ターゲット解析/照合には `openclaw/plugin-sdk/messaging-targets`
- メディア読み込みとアウトバウンド
  identity/send delegate には `openclaw/plugin-sdk/outbound-media` と
  `openclaw/plugin-sdk/outbound-runtime`
- thread-binding ライフサイクル
  とアダプター登録には `openclaw/plugin-sdk/thread-bindings-runtime`
- レガシー agent/media
  ペイロードフィールド構造がまだ必要な場合にのみ `openclaw/plugin-sdk/agent-media-payload`
- Telegram カスタムコマンド
  正規化、重複/競合検証、およびフォールバック安定なコマンド
  設定コントラクトには `openclaw/plugin-sdk/telegram-command-config`

認証専用チャネルは通常、デフォルトパスで十分です: coreが承認を処理し、プラグインは outbound/auth 機能を公開するだけです。Matrix、Slack、Telegram、およびカスタムchat転送のようなネイティブ承認チャネルは、独自の承認ライフサイクルを作るのではなく、共有ネイティブヘルパーを使うべきです。

## インバウンドメンションポリシー

インバウンドメンション処理は、次の2層に分けてください:

- プラグイン所有の証拠収集
- 共有ポリシー評価

共有レイヤーには `openclaw/plugin-sdk/channel-inbound` を使ってください。

プラグインローカルロジックに適しているもの:

- bot への返信検出
- bot の引用検出
- thread 参加チェック
- サービス/システムメッセージの除外
- bot 参加の証明に必要なプラットフォームネイティブキャッシュ

共有ヘルパーに適しているもの:

- `requireMention`
- 明示的メンション結果
- 暗黙メンション許可リスト
- コマンドバイパス
- 最終的なスキップ判定

推奨フロー:

1. ローカルなメンション情報を計算する。
2. その情報を `resolveInboundMentionDecision({ facts, policy })` に渡す。
3. インバウンドゲートでは `decision.effectiveWasMentioned`、`decision.shouldBypassMention`、`decision.shouldSkip` を使う。

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

`api.runtime.channel.mentions` は、すでにランタイム注入に依存している
バンドルチャネルプラグイン向けに、同じ共有メンションヘルパーも公開します:

- `buildMentionRegexes`
- `matchesMentionPatterns`
- `matchesMentionWithExplicit`
- `implicitMentionKindWhen`
- `resolveInboundMentionDecision`

古い `resolveMentionGating*` ヘルパーは、
`openclaw/plugin-sdk/channel-inbound` 上に互換エクスポートとしてのみ残っています。新しいコードでは
`resolveInboundMentionDecision({ facts, policy })` を使ってください。

## ウォークスルー

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="パッケージとマニフェスト">
    標準的なプラグインファイルを作成します。`package.json` の `channel` フィールドが、
    これをチャネルプラグインにします。完全なパッケージメタデータサーフェスについては、
    [プラグインのセットアップと設定](/ja-JP/plugins/sdk-setup#openclawchannel)
    を参照してください:

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
    `ChannelPlugin` インターフェースには、多くの任意アダプターサーフェスがあります。まずは
    最小限の `id` と `setup` から始め、必要に応じてアダプターを追加してください。

    `src/channel.ts` を作成します:

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

    <Accordion title="createChatChannelPlugin が行うこと">
      低レベルのアダプターインターフェースを手動で実装する代わりに、
      宣言的なオプションを渡すと、ビルダーがそれらを組み合わせます:

      | オプション | 配線される内容 |
      | --- | --- |
      | `security.dm` | 設定フィールドからのスコープ付きDMセキュリティリゾルバー |
      | `pairing.text` | コード交換を伴うテキストベースのDM pairing フロー |
      | `threading` | 返信モードリゾルバー（固定、アカウントスコープ、またはカスタム） |
      | `outbound.attachedResults` | 結果メタデータ（message ID）を返す送信関数 |

      完全な制御が必要な場合は、宣言的オプションの代わりに生のアダプターオブジェクトを渡すこともできます。
    </Accordion>

  </Step>

  <Step title="エントリポイントを配線する">
    `index.ts` を作成します:

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

    チャネル所有のCLI記述子は `registerCliMetadata(...)` に置いてください。これによりOpenClawは、
    完全なチャネルランタイムを有効化せずにルートヘルプにそれらを表示でき、
    通常の完全ロードでも実際のコマンド登録に同じ記述子を使えます。
    `registerFull(...)` はランタイム専用の作業に維持してください。
    `registerFull(...)` がGateway RPCメソッドを登録する場合は、
    プラグイン固有のプレフィックスを使ってください。coreのadmin名前空間
    （`config.*`、`exec.approvals.*`、`wizard.*`、`update.*`）は予約済みで、
    常に `operator.admin` に解決されます。
    `defineChannelPluginEntry` は登録モードの分岐を自動的に処理します。すべての
    オプションについては
    [エントリポイント](/ja-JP/plugins/sdk-entrypoints#definechannelpluginentry)
    を参照してください。

  </Step>

  <Step title="セットアップエントリを追加する">
    オンボーディング中の軽量読み込み用に `setup-entry.ts` を作成します:

    ```typescript setup-entry.ts
    import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineSetupPluginEntry(acmeChatPlugin);
    ```

    チャネルが無効または未設定の場合、OpenClawは完全なエントリの代わりにこれを読み込みます。
    これにより、セットアップフロー中に重いランタイムコードを引き込まずに済みます。
    詳細は [セットアップと設定](/ja-JP/plugins/sdk-setup#setup-entry) を参照してください。

  </Step>

  <Step title="インバウンドメッセージを処理する">
    プラグインは、プラットフォームからメッセージを受信し、それをOpenClawへ転送する必要があります。
    一般的なパターンは、リクエストを検証し、チャネルのインバウンドハンドラーを通じて
    ディスパッチするwebhookです:

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
      インバウンドメッセージ処理はチャネル固有です。各チャネルプラグインが
      独自のインバウンドパイプラインを所有します。実際のパターンについては、
      バンドルチャネルプラグイン
      （たとえば Microsoft Teams または Google Chat プラグインパッケージ）を見てください。
    </Note>

  </Step>

<a id="step-6-test"></a>
<Step title="テスト">
`src/channel.test.ts` に同居テストを書きます:

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

    共有テストヘルパーについては、[Testing](/ja-JP/plugins/sdk-testing) を参照してください。

  </Step>
</Steps>

## ファイル構造

```
<bundled-plugin-root>/acme-chat/
├── package.json              # openclaw.channel metadata
├── openclaw.plugin.json      # Manifest with config schema
├── index.ts                  # defineChannelPluginEntry
├── setup-entry.ts            # defineSetupPluginEntry
├── api.ts                    # Public exports (optional)
├── runtime-api.ts            # Internal runtime exports (optional)
└── src/
    ├── channel.ts            # ChannelPlugin via createChatChannelPlugin
    ├── channel.test.ts       # Tests
    ├── client.ts             # Platform API client
    └── runtime.ts            # Runtime store (if needed)
```

## 高度なトピック

<CardGroup cols={2}>
  <Card title="スレッド化オプション" icon="git-branch" href="/ja-JP/plugins/sdk-entrypoints#registration-mode">
    固定、アカウントスコープ、またはカスタムの返信モード
  </Card>
  <Card title="Messageツール統合" icon="puzzle" href="/ja-JP/plugins/architecture#channel-plugins-and-the-shared-message-tool">
    describeMessageTool とアクション検出
  </Card>
  <Card title="ターゲット解決" icon="crosshair" href="/ja-JP/plugins/architecture#channel-target-resolution">
    inferTargetChatType, looksLikeId, resolveTarget
  </Card>
  <Card title="ランタイムヘルパー" icon="settings" href="/ja-JP/plugins/sdk-runtime">
    api.runtime 経由のTTS、STT、メディア、subagent
  </Card>
</CardGroup>

<Note>
一部のバンドルヘルパーシームは、バンドルプラグインの保守と
互換性のために依然として存在します。これらは新しいチャネルプラグイン向けの推奨パターンではありません。
そのバンドルプラグインファミリーを直接保守しているのでない限り、
共通SDKサーフェスの汎用チャネル/セットアップ/返信/ランタイムsubpathを優先してください。
</Note>

## 次のステップ

- [Provider Plugins](/ja-JP/plugins/sdk-provider-plugins) — プラグインがモデルも提供する場合
- [SDK Overview](/ja-JP/plugins/sdk-overview) — 完全なsubpath importリファレンス
- [SDK Testing](/ja-JP/plugins/sdk-testing) — テストユーティリティとコントラクトテスト
- [Plugin Manifest](/ja-JP/plugins/manifest) — 完全なマニフェストスキーマ
