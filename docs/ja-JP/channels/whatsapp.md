---
read_when:
    - WhatsApp/webチャネルの動作または受信トレイルーティングに取り組んでいる場合
summary: WhatsAppチャネルのサポート、アクセス制御、配信動作、運用
title: WhatsApp
x-i18n:
    generated_at: "2026-04-07T04:41:46Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9e2ce84d869ace6c0bebd9ec17bdbbef997a5c31e5da410b02a19a0f103f7359
    source_path: channels/whatsapp.md
    workflow: 15
---

# WhatsApp（Webチャネル）

ステータス: WhatsApp Web（Baileys）経由で本番運用対応。Gatewayがリンクされたセッションを管理します。

## インストール（必要時）

- オンボーディング（`openclaw onboard`）および `openclaw channels add --channel whatsapp` では、
  初めて選択したときにWhatsAppプラグインのインストールを促します。
- `openclaw channels login --channel whatsapp` でも、
  プラグインがまだ存在しない場合はインストールフローが提示されます。
- 開発チャネル + git checkout: デフォルトでローカルのプラグインパスを使用します。
- Stable/Beta: デフォルトで npm パッケージ `@openclaw/whatsapp` を使用します。

手動インストールも引き続き利用できます:

```bash
openclaw plugins install @openclaw/whatsapp
```

<CardGroup cols={3}>
  <Card title="ペアリング" icon="link" href="/ja-JP/channels/pairing">
    未知の送信者に対するデフォルトのDMポリシーはペアリングです。
  </Card>
  <Card title="チャネルのトラブルシューティング" icon="wrench" href="/ja-JP/channels/troubleshooting">
    チャネル横断の診断と修復プレイブック。
  </Card>
  <Card title="Gateway設定" icon="settings" href="/ja-JP/gateway/configuration">
    完全なチャネル設定パターンと例。
  </Card>
</CardGroup>

## クイックセットアップ

<Steps>
  <Step title="WhatsAppアクセスポリシーを設定する">

```json5
{
  channels: {
    whatsapp: {
      dmPolicy: "pairing",
      allowFrom: ["+15551234567"],
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15551234567"],
    },
  },
}
```

  </Step>

  <Step title="WhatsAppをリンクする（QR）">

```bash
openclaw channels login --channel whatsapp
```

    特定のアカウントの場合:

```bash
openclaw channels login --channel whatsapp --account work
```

  </Step>

  <Step title="Gatewayを起動する">

```bash
openclaw gateway
```

  </Step>

  <Step title="最初のペアリング要求を承認する（ペアリングモード使用時）">

```bash
openclaw pairing list whatsapp
openclaw pairing approve whatsapp <CODE>
```

    ペアリング要求は1時間後に期限切れになります。保留中の要求はチャネルごとに3件までです。

  </Step>
</Steps>

<Note>
OpenClawは、可能であればWhatsAppを別番号で運用することを推奨します。（チャネルのメタデータとセットアップフローはその構成向けに最適化されていますが、個人番号での構成にも対応しています。）
</Note>

## デプロイパターン

<AccordionGroup>
  <Accordion title="専用番号（推奨）">
    これは最もクリーンな運用モードです:

    - OpenClaw専用のWhatsApp ID
    - より明確なDM許可リストとルーティング境界
    - セルフチャットの混乱が起きる可能性が低い

    最小限のポリシーパターン:

    ```json5
    {
      channels: {
        whatsapp: {
          dmPolicy: "allowlist",
          allowFrom: ["+15551234567"],
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="個人番号フォールバック">
    オンボーディングは個人番号モードに対応しており、セルフチャットに適したベースラインを書き込みます:

    - `dmPolicy: "allowlist"`
    - `allowFrom` にあなたの個人番号を含める
    - `selfChatMode: true`

    実行時には、セルフチャット保護はリンクされた自分の番号と `allowFrom` に基づいて動作します。

  </Accordion>

  <Accordion title="WhatsApp Web専用のチャネルスコープ">
    現在のOpenClawチャネルアーキテクチャでは、メッセージングプラットフォームのチャネルはWhatsApp Webベース（`Baileys`）です。

    組み込みのチャットチャネルレジストリには、別個のTwilio WhatsAppメッセージングチャネルはありません。

  </Accordion>
</AccordionGroup>

## 実行時モデル

- GatewayがWhatsAppソケットと再接続ループを管理します。
- 送信メッセージには、対象アカウントのアクティブなWhatsAppリスナーが必要です。
- ステータスチャットとブロードキャストチャットは無視されます（`@status`, `@broadcast`）。
- ダイレクトチャットはDMセッションルールを使用します（`session.dmScope`; デフォルトの `main` ではDMはエージェントのメインセッションに集約されます）。
- グループセッションは分離されます（`agent:<agentId>:whatsapp:group:<jid>`）。
- WhatsApp Webトランスポートは、Gatewayホスト上の標準プロキシ環境変数（`HTTPS_PROXY`, `HTTP_PROXY`, `NO_PROXY` / 小文字版）を尊重します。チャネル固有のWhatsAppプロキシ設定より、ホストレベルのプロキシ設定を推奨します。

## アクセス制御とアクティベーション

<Tabs>
  <Tab title="DMポリシー">
    `channels.whatsapp.dmPolicy` はダイレクトチャットのアクセスを制御します:

    - `pairing`（デフォルト）
    - `allowlist`
    - `open`（`allowFrom` に `"*"` を含める必要があります）
    - `disabled`

    `allowFrom` はE.164形式の番号を受け付けます（内部で正規化されます）。

    複数アカウントの上書き: `channels.whatsapp.accounts.<id>.dmPolicy`（および `allowFrom`）は、そのアカウントに対してチャネルレベルのデフォルトより優先されます。

    実行時動作の詳細:

    - ペアリングはチャネル許可ストアに永続化され、設定された `allowFrom` とマージされます
    - 許可リストが設定されていない場合、リンクされた自分の番号はデフォルトで許可されます
    - 送信側の `fromMe` DM は自動ペアリングされません

  </Tab>

  <Tab title="グループポリシー + 許可リスト">
    グループアクセスには2つのレイヤーがあります:

    1. **グループメンバーシップ許可リスト**（`channels.whatsapp.groups`）
       - `groups` が省略されている場合、すべてのグループが対象になります
       - `groups` が存在する場合、グループ許可リストとして機能します（`"*"` 使用可）

    2. **グループ送信者ポリシー**（`channels.whatsapp.groupPolicy` + `groupAllowFrom`）
       - `open`: 送信者許可リストをバイパス
       - `allowlist`: 送信者は `groupAllowFrom`（または `*`）に一致する必要があります
       - `disabled`: すべてのグループ受信をブロック

    送信者許可リストのフォールバック:

    - `groupAllowFrom` が未設定の場合、実行時には利用可能であれば `allowFrom` にフォールバックします
    - 送信者許可リストは、メンション/返信によるアクティベーションより前に評価されます

    注: `channels.whatsapp` ブロック自体がまったく存在しない場合、`channels.defaults.groupPolicy` が設定されていても、実行時のグループポリシーのフォールバックは `allowlist` になります（警告ログあり）。

  </Tab>

  <Tab title="メンション + /activation">
    グループ返信はデフォルトでメンションが必要です。

    メンション検出には以下が含まれます:

    - ボットIDに対する明示的なWhatsAppメンション
    - 設定されたメンション正規表現パターン（`agents.list[].groupChat.mentionPatterns`、フォールバックは `messages.groupChat.mentionPatterns`）
    - 暗黙的なボットへの返信検出（返信送信者がボットIDに一致）

    セキュリティに関する注記:

    - 引用/返信はメンションゲートを満たすだけであり、送信者の認可は付与しません
    - `groupPolicy: "allowlist"` の場合、許可リストにない送信者は、許可リスト済みユーザーのメッセージに返信したとしても引き続きブロックされます

    セッションレベルのアクティベーションコマンド:

    - `/activation mention`
    - `/activation always`

    `activation` はセッション状態を更新します（グローバル設定ではありません）。オーナー制限付きです。

  </Tab>
</Tabs>

## 個人番号とセルフチャットの動作

リンクされた自分の番号が `allowFrom` にも含まれている場合、WhatsAppのセルフチャット保護が有効になります:

- セルフチャットのターンでは既読受信通知をスキップ
- 本来なら自分自身を通知してしまうメンションJID自動トリガー動作を無視
- `messages.responsePrefix` が未設定の場合、セルフチャット返信はデフォルトで `[{identity.name}]` または `[openclaw]`

## メッセージ正規化とコンテキスト

<AccordionGroup>
  <Accordion title="受信エンベロープ + 返信コンテキスト">
    受信したWhatsAppメッセージは共有の受信エンベロープでラップされます。

    引用返信が存在する場合、コンテキストは次の形式で付加されます:

    ```text
    [Replying to <sender> id:<stanzaId>]
    <quoted body or media placeholder>
    [/Replying]
    ```

    利用可能な場合は返信メタデータ項目も設定されます（`ReplyToId`, `ReplyToBody`, `ReplyToSender`, sender JID/E.164）。

  </Accordion>

  <Accordion title="メディアプレースホルダーと位置情報/連絡先の抽出">
    メディアのみの受信メッセージは、次のようなプレースホルダーで正規化されます:

    - `<media:image>`
    - `<media:video>`
    - `<media:audio>`
    - `<media:document>`
    - `<media:sticker>`

    位置情報と連絡先のペイロードは、ルーティング前にテキストコンテキストへ正規化されます。

  </Accordion>

  <Accordion title="保留中グループ履歴の注入">
    グループでは、未処理メッセージをバッファリングし、ボットが最終的にトリガーされたときにコンテキストとして注入できます。

    - デフォルト上限: `50`
    - 設定: `channels.whatsapp.historyLimit`
    - フォールバック: `messages.groupChat.historyLimit`
    - `0` で無効化

    注入マーカー:

    - `[Chat messages since your last reply - for context]`
    - `[Current message - respond to this]`

  </Accordion>

  <Accordion title="既読受信通知">
    既読受信通知は、受理された受信WhatsAppメッセージに対してデフォルトで有効です。

    グローバルに無効化する場合:

    ```json5
    {
      channels: {
        whatsapp: {
          sendReadReceipts: false,
        },
      },
    }
    ```

    アカウント単位の上書き:

    ```json5
    {
      channels: {
        whatsapp: {
          accounts: {
            work: {
              sendReadReceipts: false,
            },
          },
        },
      },
    }
    ```

    セルフチャットのターンでは、グローバルに有効でも既読受信通知はスキップされます。

  </Accordion>
</AccordionGroup>

## 配信、分割、メディア

<AccordionGroup>
  <Accordion title="テキスト分割">
    - デフォルトの分割上限: `channels.whatsapp.textChunkLimit = 4000`
    - `channels.whatsapp.chunkMode = "length" | "newline"`
    - `newline` モードは段落境界（空行）を優先し、その後、長さに安全な分割へフォールバックします
  </Accordion>

  <Accordion title="送信メディアの動作">
    - 画像、動画、音声（PTTボイスノート）、ドキュメントのペイロードをサポート
    - `audio/ogg` は、ボイスノート互換性のため `audio/ogg; codecs=opus` に書き換えられます
    - アニメーションGIF再生は、動画送信時に `gifPlayback: true` を通じてサポートされます
    - 複数メディア返信ペイロード送信時、キャプションは最初のメディア項目に適用されます
    - メディアソースには HTTP(S)、`file://`、ローカルパスを使用できます
  </Accordion>

  <Accordion title="メディアサイズ制限とフォールバック動作">
    - 受信メディア保存上限: `channels.whatsapp.mediaMaxMb`（デフォルト `50`）
    - 送信メディア送信上限: `channels.whatsapp.mediaMaxMb`（デフォルト `50`）
    - アカウント単位の上書きには `channels.whatsapp.accounts.<accountId>.mediaMaxMb` を使用します
    - 画像は制限に収まるよう自動最適化されます（リサイズ/画質スイープ）
    - メディア送信失敗時、先頭項目のフォールバックにより、応答を黙って落とす代わりに警告テキストを送信します
  </Accordion>
</AccordionGroup>

## リアクションレベル

`channels.whatsapp.reactionLevel` は、エージェントがWhatsAppで絵文字リアクションをどの程度広く使うかを制御します:

| レベル        | Ackリアクション | エージェント主導リアクション | 説明                                             |
| ------------- | --------------- | ---------------------------- | ------------------------------------------------ |
| `"off"`       | いいえ          | いいえ                       | リアクションをまったく使用しない                 |
| `"ack"`       | はい            | いいえ                       | Ackリアクションのみ（返信前の受領確認）          |
| `"minimal"`   | はい            | はい（控えめ）               | Ack + 保守的ガイダンスによるエージェントリアクション |
| `"extensive"` | はい            | はい（推奨）                 | Ack + 積極的ガイダンスによるエージェントリアクション |

デフォルト: `"minimal"`。

アカウント単位の上書きには `channels.whatsapp.accounts.<id>.reactionLevel` を使用します。

```json5
{
  channels: {
    whatsapp: {
      reactionLevel: "ack",
    },
  },
}
```

## 確認リアクション

WhatsAppは、`channels.whatsapp.ackReaction` により、受信時に即時のackリアクションをサポートします。
Ackリアクションは `reactionLevel` によって制御され、`reactionLevel` が `"off"` の場合は抑制されます。

```json5
{
  channels: {
    whatsapp: {
      ackReaction: {
        emoji: "👀",
        direct: true,
        group: "mentions", // always | mentions | never
      },
    },
  },
}
```

動作に関する注記:

- 受信が受理された直後に送信されます（返信前）
- 失敗はログに記録されますが、通常の返信配信はブロックしません
- グループモード `mentions` は、メンショントリガーされたターンでリアクションします。グループアクティベーション `always` はこのチェックをバイパスとして機能します
- WhatsAppは `channels.whatsapp.ackReaction` を使用します（従来の `messages.ackReaction` はここでは使用されません）

## 複数アカウントと認証情報

<AccordionGroup>
  <Accordion title="アカウント選択とデフォルト">
    - アカウントIDは `channels.whatsapp.accounts` から取得されます
    - デフォルトのアカウント選択: `default` が存在する場合はそれ、そうでなければ最初に設定されたアカウントID（ソート順）
    - アカウントIDは検索用に内部で正規化されます
  </Accordion>

  <Accordion title="認証情報パスと従来互換性">
    - 現在の認証パス: `~/.openclaw/credentials/whatsapp/<accountId>/creds.json`
    - バックアップファイル: `creds.json.bak`
    - `~/.openclaw/credentials/` 内の従来のデフォルト認証も、デフォルトアカウントフロー向けに引き続き認識/移行されます
  </Accordion>

  <Accordion title="ログアウト動作">
    `openclaw channels logout --channel whatsapp [--account <id>]` は、そのアカウントのWhatsApp認証状態をクリアします。

    従来の認証ディレクトリでは、`oauth.json` は保持され、Baileys認証ファイルは削除されます。

  </Accordion>
</AccordionGroup>

## ツール、アクション、設定書き込み

- エージェントのツールサポートには、WhatsAppリアクションアクション（`react`）が含まれます。
- アクションゲート:
  - `channels.whatsapp.actions.reactions`
  - `channels.whatsapp.actions.polls`
- チャネル起点の設定書き込みはデフォルトで有効です（`channels.whatsapp.configWrites=false` で無効化）。

## トラブルシューティング

<AccordionGroup>
  <Accordion title="リンクされていない（QRが必要）">
    症状: チャネルステータスで未リンクと表示されます。

    修正:

    ```bash
    openclaw channels login --channel whatsapp
    openclaw channels status
    ```

  </Accordion>

  <Accordion title="リンク済みだが切断される / 再接続ループ">
    症状: リンク済みアカウントで切断や再接続試行が繰り返されます。

    修正:

    ```bash
    openclaw doctor
    openclaw logs --follow
    ```

    必要に応じて、`channels login` で再リンクしてください。

  </Accordion>

  <Accordion title="送信時にアクティブなリスナーがない">
    対象アカウントにアクティブなGatewayリスナーが存在しない場合、送信は即座に失敗します。

    Gatewayが実行中であり、アカウントがリンクされていることを確認してください。

  </Accordion>

  <Accordion title="グループメッセージが予期せず無視される">
    次の順で確認してください:

    - `groupPolicy`
    - `groupAllowFrom` / `allowFrom`
    - `groups` 許可リスト項目
    - メンションゲート（`requireMention` + メンションパターン）
    - `openclaw.json`（JSON5）の重複キー: 後の項目が前の項目を上書きするため、スコープごとに `groupPolicy` は1つだけにしてください

  </Accordion>

  <Accordion title="Bun実行時警告">
    WhatsApp GatewayランタイムではNodeを使用してください。Bunは、安定したWhatsApp/Telegram Gateway運用には非互換として扱われます。
  </Accordion>
</AccordionGroup>

## 設定リファレンスの参照先

主要リファレンス:

- [設定リファレンス - WhatsApp](/ja-JP/gateway/configuration-reference#whatsapp)

高重要度のWhatsAppフィールド:

- アクセス: `dmPolicy`, `allowFrom`, `groupPolicy`, `groupAllowFrom`, `groups`
- 配信: `textChunkLimit`, `chunkMode`, `mediaMaxMb`, `sendReadReceipts`, `ackReaction`, `reactionLevel`
- 複数アカウント: `accounts.<id>.enabled`, `accounts.<id>.authDir`, アカウントレベルの上書き
- 運用: `configWrites`, `debounceMs`, `web.enabled`, `web.heartbeatSeconds`, `web.reconnect.*`
- セッション動作: `session.dmScope`, `historyLimit`, `dmHistoryLimit`, `dms.<id>.historyLimit`

## 関連

- [ペアリング](/ja-JP/channels/pairing)
- [グループ](/ja-JP/channels/groups)
- [セキュリティ](/ja-JP/gateway/security)
- [チャネルルーティング](/ja-JP/channels/channel-routing)
- [マルチエージェントルーティング](/ja-JP/concepts/multi-agent)
- [トラブルシューティング](/ja-JP/channels/troubleshooting)
