---
read_when:
    - OpenClaw向けにZalo Personalをセットアップする場合
    - Zalo Personalのログインまたはメッセージフローをデバッグする場合
summary: native `zca-js`（QRログイン）を介したZalo個人アカウントのサポート、機能、設定
title: Zalo Personal
x-i18n:
    generated_at: "2026-04-08T02:14:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: 08f50edb2f4c6fe24972efe5e321f5fd0572c7d29af5c1db808151c7c943dc66
    source_path: channels/zalouser.md
    workflow: 15
---

# Zalo Personal（非公式）

ステータス: 実験的。この連携は、OpenClaw内でネイティブ`zca-js`を使用して**個人のZaloアカウント**を自動化します。

> **警告:** これは非公式の連携であり、アカウントの停止やBANにつながる可能性があります。自己責任で使用してください。

## バンドル済みプラグイン

Zalo Personalは現在のOpenClawリリースにバンドル済みプラグインとして含まれているため、通常の
パッケージ版ビルドでは別途インストールは不要です。

古いビルドまたはZalo Personalを含まないカスタムインストールを使用している場合は、
手動でインストールしてください。

- CLIでインストール: `openclaw plugins install @openclaw/zalouser`
- またはソースチェックアウトから: `openclaw plugins install ./path/to/local/zalouser-plugin`
- 詳細: [Plugins](/ja-JP/tools/plugin)

外部の`zca`/`openzca` CLIバイナリは不要です。

## クイックスタート（初心者向け）

1. Zalo Personalプラグインが利用可能であることを確認します。
   - 現在のパッケージ版OpenClawリリースにはすでにバンドルされています。
   - 古い/カスタムインストールでは、上記のコマンドで手動追加できます。
2. ログインします（QR、Gatewayマシン上で）。
   - `openclaw channels login --channel zalouser`
   - ZaloモバイルアプリでQRコードをスキャンします。
3. チャンネルを有効にします:

```json5
{
  channels: {
    zalouser: {
      enabled: true,
      dmPolicy: "pairing",
    },
  },
}
```

4. Gatewayを再起動します（またはセットアップを完了します）。
5. DMアクセスのデフォルトはpairingです。最初の接触時にペアリングコードを承認してください。

## これは何か

- `zca-js`を介して完全にインプロセスで動作します。
- ネイティブのイベントリスナーを使用して受信メッセージを受け取ります。
- JS APIを介して直接返信を送信します（テキスト/メディア/リンク）。
- Zalo Bot APIが利用できない「個人アカウント」のユースケース向けに設計されています。

## 命名

チャンネルIDは`zalouser`です。これは**個人のZaloユーザーアカウント**（非公式）を自動化することを明確にするためです。`zalo`は、将来追加される可能性のある公式Zalo API連携用に予約されています。

## IDの確認（ディレクトリ）

ディレクトリCLIを使用して、相手先/グループとそのIDを見つけます:

```bash
openclaw directory self --channel zalouser
openclaw directory peers list --channel zalouser --query "name"
openclaw directory groups list --channel zalouser --query "work"
```

## 制限事項

- 送信テキストは約2000文字ごとに分割されます（Zaloクライアントの制限）。
- ストリーミングはデフォルトでブロックされます。

## アクセス制御（DM）

`channels.zalouser.dmPolicy`でサポートされる値: `pairing | allowlist | open | disabled`（デフォルト: `pairing`）。

`channels.zalouser.allowFrom`にはユーザーIDまたは名前を指定できます。セットアップ時に、名前はプラグインのインプロセス連絡先検索を使ってIDに解決されます。

承認方法:

- `openclaw pairing list zalouser`
- `openclaw pairing approve zalouser <code>`

## グループアクセス（任意）

- デフォルト: `channels.zalouser.groupPolicy = "open"`（グループを許可）。未設定時のデフォルトを上書きするには`channels.defaults.groupPolicy`を使用します。
- 許可リストに制限するには:
  - `channels.zalouser.groupPolicy = "allowlist"`
  - `channels.zalouser.groups`（キーは安定したグループIDにするべきです。可能な場合、起動時に名前はIDに解決されます）
  - `channels.zalouser.groupAllowFrom`（許可されたグループ内でどの送信者がボットをトリガーできるかを制御します）
- すべてのグループをブロック: `channels.zalouser.groupPolicy = "disabled"`。
- configureウィザードではグループ許可リストを確認できます。
- 起動時に、OpenClawは許可リスト内のグループ/ユーザー名をIDに解決し、その対応関係をログに記録します。
- グループ許可リストのマッチングは、デフォルトではIDのみです。未解決の名前は、`channels.zalouser.dangerouslyAllowNameMatching: true`が有効でない限り、認可では無視されます。
- `channels.zalouser.dangerouslyAllowNameMatching: true`は、変更可能なグループ名によるマッチングを再有効化するブレークグラス互換モードです。
- `groupAllowFrom`が未設定の場合、ランタイムはグループ送信者チェックに`allowFrom`をフォールバックとして使用します。
- 送信者チェックは、通常のグループメッセージと制御コマンド（例: `/new`、`/reset`）の両方に適用されます。

例:

```json5
{
  channels: {
    zalouser: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["1471383327500481391"],
      groups: {
        "123456789": { allow: true },
        "Work Chat": { allow: true },
      },
    },
  },
}
```

### グループメンションゲーティング

- `channels.zalouser.groups.<group>.requireMention`は、グループ返信にメンションを必須にするかどうかを制御します。
- 解決順序: 正確なグループID/名前 -> 正規化されたグループslug -> `*` -> デフォルト（`true`）。
- これは、許可リスト対象のグループとオープングループモードの両方に適用されます。
- ボットメッセージの引用は、グループ起動における暗黙のメンションとしてカウントされます。
- 認可された制御コマンド（例: `/new`）は、メンションゲーティングをバイパスできます。
- メンションが必要なためにグループメッセージがスキップされた場合、OpenClawはそれを保留中のグループ履歴として保存し、次に処理されるグループメッセージに含めます。
- グループ履歴の上限はデフォルトで`messages.groupChat.historyLimit`（フォールバックは`50`）です。アカウント単位で上書きするには`channels.zalouser.historyLimit`を使用できます。

例:

```json5
{
  channels: {
    zalouser: {
      groupPolicy: "allowlist",
      groups: {
        "*": { allow: true, requireMention: true },
        "Work Chat": { allow: true, requireMention: false },
      },
    },
  },
}
```

## マルチアカウント

アカウントはOpenClawの状態内で`zalouser`プロファイルにマッピングされます。例:

```json5
{
  channels: {
    zalouser: {
      enabled: true,
      defaultAccount: "default",
      accounts: {
        work: { enabled: true, profile: "work" },
      },
    },
  },
}
```

## 入力中表示、リアクション、配信確認

- OpenClawは返信を送信する前に入力中イベントを送ります（ベストエフォート）。
- メッセージリアクションアクション`react`は、チャンネルアクションで`zalouser`に対応しています。
  - メッセージから特定のリアクション絵文字を削除するには`remove: true`を使用します。
  - リアクションの仕様: [Reactions](/ja-JP/tools/reactions)
- イベントメタデータを含む受信メッセージについては、OpenClawは配信済み + 既読確認を送信します（ベストエフォート）。

## トラブルシューティング

**ログイン状態が維持されない場合:**

- `openclaw channels status --probe`
- 再ログイン: `openclaw channels logout --channel zalouser && openclaw channels login --channel zalouser`

**許可リスト/グループ名が解決されなかった場合:**

- `allowFrom`/`groupAllowFrom`/`groups`には数値IDまたは正確な友だち名/グループ名を使用してください。

**古いCLIベースのセットアップからアップグレードした場合:**

- 古い外部`zca`プロセス前提は削除してください。
- このチャンネルは現在、外部CLIバイナリなしでOpenClaw内で完全に動作します。

## 関連

- [Channels Overview](/ja-JP/channels) — サポートされているすべてのチャンネル
- [Pairing](/ja-JP/channels/pairing) — DM認証とペアリングフロー
- [Groups](/ja-JP/channels/groups) — グループチャットの動作とメンションゲーティング
- [Channel Routing](/ja-JP/channels/channel-routing) — メッセージのセッションルーティング
- [Security](/ja-JP/gateway/security) — アクセスモデルとハードニング
