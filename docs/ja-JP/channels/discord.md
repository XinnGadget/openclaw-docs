---
read_when:
    - Discordチャンネル機能に取り組んでいるとき
summary: Discordボットのサポート状況、機能、設定
title: Discord
x-i18n:
    generated_at: "2026-04-06T03:08:06Z"
    model: gpt-5.4
    provider: openai
    source_hash: 54af2176a1b4fa1681e3f07494def0c652a2730165058848000e71a59e2a9d08
    source_path: channels/discord.md
    workflow: 15
---

# Discord (Bot API)

ステータス: 公式Discord Gateway経由でDMおよびギルドチャンネルに対応済みです。

<CardGroup cols={3}>
  <Card title="ペアリング" icon="link" href="/ja-JP/channels/pairing">
    Discord DMはデフォルトでペアリングモードになります。
  </Card>
  <Card title="スラッシュコマンド" icon="terminal" href="/ja-JP/tools/slash-commands">
    ネイティブコマンドの動作とコマンドカタログ。
  </Card>
  <Card title="チャンネルのトラブルシューティング" icon="wrench" href="/ja-JP/channels/troubleshooting">
    チャンネル横断の診断と修復フロー。
  </Card>
</CardGroup>

## クイックセットアップ

新しいアプリケーションを作成してボットを追加し、そのボットをあなたのサーバーに追加してOpenClawとペアリングする必要があります。ボットは自分専用のプライベートサーバーに追加することをおすすめします。まだ持っていない場合は、まず[サーバーを作成](https://support.discord.com/hc/en-us/articles/204849977-How-do-I-create-a-server)してください（**Create My Own > For me and my friends** を選択）。

<Steps>
  <Step title="Discordアプリケーションとボットを作成する">
    [Discord Developer Portal](https://discord.com/developers/applications) に移動し、**New Application** をクリックします。「OpenClaw」のような名前を付けてください。

    サイドバーで **Bot** をクリックします。**Username** は、OpenClawエージェントに付けている名前に設定します。

  </Step>

  <Step title="特権インテントを有効にする">
    引き続き **Bot** ページで、下にスクロールして **Privileged Gateway Intents** を有効にします。

    - **Message Content Intent**（必須）
    - **Server Members Intent**（推奨。ロールの許可リストと名前からIDへの照合に必要）
    - **Presence Intent**（任意。プレゼンス更新が必要な場合のみ）

  </Step>

  <Step title="ボットトークンをコピーする">
    **Bot** ページの上部に戻り、**Reset Token** をクリックします。

    <Note>
    名前とは異なり、これは最初のトークンを生成するだけであり、何かが「リセット」されるわけではありません。
    </Note>

    トークンをコピーしてどこかに保存してください。これが **Bot Token** で、すぐに必要になります。

  </Step>

  <Step title="招待URLを生成してボットをサーバーに追加する">
    サイドバーで **OAuth2** をクリックします。サーバーにボットを追加するための適切な権限を持つ招待URLを生成します。

    下にスクロールして **OAuth2 URL Generator** で次を有効にします。

    - `bot`
    - `applications.commands`

    その下に **Bot Permissions** セクションが表示されます。以下を有効にします。

    - View Channels
    - Send Messages
    - Read Message History
    - Embed Links
    - Attach Files
    - Add Reactions（任意）

    下部に生成されたURLをコピーし、ブラウザに貼り付けてサーバーを選択し、**Continue** をクリックして接続します。これでDiscordサーバー内にボットが表示されるはずです。

  </Step>

  <Step title="Developer Modeを有効にしてIDを収集する">
    Discordアプリに戻り、内部IDをコピーできるようにDeveloper Modeを有効にする必要があります。

    1. **User Settings**（アバターの横の歯車アイコン）→ **Advanced** → **Developer Mode** をオンにする
    2. サイドバーの **server icon** を右クリック → **Copy Server ID**
    3. 自分の **avatar** を右クリック → **Copy User ID**

    **Server ID** と **User ID** を Bot Token と一緒に保存してください。次のステップでこの3つすべてをOpenClawに送ります。

  </Step>

  <Step title="サーバーメンバーからのDMを許可する">
    ペアリングを機能させるには、DiscordでボットがあなたにDMを送れる必要があります。**server icon** を右クリック → **Privacy Settings** → **Direct Messages** をオンにします。

    これにより、サーバーメンバー（ボットを含む）があなたにDMを送れるようになります。OpenClawでDiscord DMを使いたい場合は、これを有効のままにしてください。ギルドチャンネルだけを使う予定であれば、ペアリング後にDMを無効にできます。

  </Step>

  <Step title="ボットトークンを安全に設定する（チャットで送信しないでください）">
    Discordボットトークンは秘密情報です（パスワードのようなものです）。エージェントにメッセージを送る前に、OpenClawを実行しているマシンで設定してください。

```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"
openclaw config set channels.discord.token --ref-provider default --ref-source env --ref-id DISCORD_BOT_TOKEN --dry-run
openclaw config set channels.discord.token --ref-provider default --ref-source env --ref-id DISCORD_BOT_TOKEN
openclaw config set channels.discord.enabled true --strict-json
openclaw gateway
```

    OpenClawがすでにバックグラウンドサービスとして実行中の場合は、OpenClaw Macアプリから再起動するか、`openclaw gateway run` プロセスを停止して再起動してください。

  </Step>

  <Step title="OpenClawを設定してペアリングする">

    <Tabs>
      <Tab title="エージェントに依頼する">
        既存の任意のチャンネル（例: Telegram）でOpenClawエージェントと会話し、設定を依頼します。Discordが最初のチャンネルである場合は、代わりにCLI / configタブを使用してください。

        > 「Discordボットトークンはすでにconfigに設定しました。User ID `<user_id>` と Server ID `<server_id>` を使ってDiscordセットアップを完了してください。」
      </Tab>
      <Tab title="CLI / config">
        ファイルベースの設定を使いたい場合は、以下を設定します。

```json5
{
  channels: {
    discord: {
      enabled: true,
      token: {
        source: "env",
        provider: "default",
        id: "DISCORD_BOT_TOKEN",
      },
    },
  },
}
```

        デフォルトアカウント用の環境変数フォールバック:

```bash
DISCORD_BOT_TOKEN=...
```

        プレーンテキストの `token` 値にも対応しています。`channels.discord.token` には、env/file/exec provider 全体で SecretRef 値も使用できます。詳しくは [Secrets Management](/ja-JP/gateway/secrets) を参照してください。

      </Tab>
    </Tabs>

  </Step>

  <Step title="最初のDMペアリングを承認する">
    Gatewayが起動するまで待ち、その後DiscordでボットにDMを送ってください。ボットがペアリングコードを返します。

    <Tabs>
      <Tab title="エージェントに依頼する">
        既存のチャンネルでそのペアリングコードをエージェントに送信します。

        > 「このDiscordペアリングコードを承認してください: `<CODE>`」
      </Tab>
      <Tab title="CLI">

```bash
openclaw pairing list discord
openclaw pairing approve discord <CODE>
```

      </Tab>
    </Tabs>

    ペアリングコードの有効期限は1時間です。

    これでDiscord上でDM経由でエージェントと会話できるはずです。

  </Step>
</Steps>

<Note>
トークン解決はアカウント対応です。config内のトークン値は環境変数フォールバックより優先されます。`DISCORD_BOT_TOKEN` はデフォルトアカウントでのみ使用されます。
高度な送信呼び出し（message tool/channel actions）では、明示的な呼び出しごとの `token` がその呼び出しに使われます。これは送信および読み取り/プローブ系アクション（たとえば read/search/fetch/thread/pins/permissions）に適用されます。アカウントポリシーや再試行設定は、アクティブなランタイムスナップショットで選択されたアカウントから引き続き取得されます。
</Note>

## 推奨: ギルドワークスペースを設定する

DMが機能したら、Discordサーバーをフルワークスペースとして設定できます。各チャンネルが独自のコンテキストを持つ独立したエージェントセッションになります。これは、あなたとボットだけのプライベートサーバーにおすすめです。

<Steps>
  <Step title="サーバーをギルド許可リストに追加する">
    これにより、エージェントはDMだけでなく、サーバー上の任意のチャンネルで応答できるようになります。

    <Tabs>
      <Tab title="エージェントに依頼する">
        > 「私のDiscord Server ID `<server_id>` をギルド許可リストに追加して」
      </Tab>
      <Tab title="Config">

```json5
{
  channels: {
    discord: {
      groupPolicy: "allowlist",
      guilds: {
        YOUR_SERVER_ID: {
          requireMention: true,
          users: ["YOUR_USER_ID"],
        },
      },
    },
  },
}
```

      </Tab>
    </Tabs>

  </Step>

  <Step title="@mentionなしで応答を許可する">
    デフォルトでは、エージェントはギルドチャンネル内で @mention された場合にのみ応答します。プライベートサーバーでは、すべてのメッセージに応答するようにしたいはずです。

    <Tabs>
      <Tab title="エージェントに依頼する">
        > 「このサーバーでは、@mentioned しなくてもエージェントが応答できるようにして」
      </Tab>
      <Tab title="Config">
        ギルド設定で `requireMention: false` を設定します。

```json5
{
  channels: {
    discord: {
      guilds: {
        YOUR_SERVER_ID: {
          requireMention: false,
        },
      },
    },
  },
}
```

      </Tab>
    </Tabs>

  </Step>

  <Step title="ギルドチャンネルでのメモリー利用を計画する">
    デフォルトでは、長期メモリー（MEMORY.md）はDMセッションでのみ読み込まれます。ギルドチャンネルでは MEMORY.md は自動読み込みされません。

    <Tabs>
      <Tab title="エージェントに依頼する">
        > 「Discordチャンネルで質問するとき、MEMORY.md から長期コンテキストが必要なら memory_search または memory_get を使って。」
      </Tab>
      <Tab title="手動">
        すべてのチャンネルで共有コンテキストが必要な場合は、安定した指示を `AGENTS.md` または `USER.md` に入れてください（これらはすべてのセッションに注入されます）。長期メモは `MEMORY.md` に保存し、必要に応じてメモリーツールでアクセスしてください。
      </Tab>
    </Tabs>

  </Step>
</Steps>

次に、Discordサーバー上にいくつかチャンネルを作成して会話を始めてください。エージェントはチャンネル名を認識でき、各チャンネルには独立したセッションが割り当てられます。つまり、`#coding`、`#home`、`#research` など、ワークフローに合った形で設定できます。

## ランタイムモデル

- GatewayがDiscord接続を管理します。
- 返信ルーティングは決定的です: Discordからの受信返信はDiscordに返されます。
- デフォルトでは（`session.dmScope=main`）、ダイレクトチャットはエージェントのメインセッション（`agent:main:main`）を共有します。
- ギルドチャンネルは独立したセッションキーです（`agent:<agentId>:discord:channel:<channelId>`）。
- グループDMはデフォルトで無視されます（`channels.discord.dm.groupEnabled=false`）。
- ネイティブスラッシュコマンドは独立したコマンドセッション（`agent:<agentId>:discord:slash:<userId>`）で実行されますが、ルーティングされた会話セッションへの `CommandTargetSessionKey` は引き続き保持されます。

## フォーラムチャンネル

Discordのフォーラムチャンネルとメディアチャンネルは、スレッド投稿のみ受け付けます。OpenClawはそれらを作成するために2つの方法をサポートしています。

- フォーラム親（`channel:<forumId>`）にメッセージを送信してスレッドを自動作成する。スレッドタイトルには、メッセージ内の最初の空でない行が使われます。
- `openclaw message thread create` を使ってスレッドを直接作成する。フォーラムチャンネルでは `--message-id` を渡さないでください。

例: フォーラム親に送信してスレッドを作成する

```bash
openclaw message send --channel discord --target channel:<forumId> \
  --message "Topic title\nBody of the post"
```

例: フォーラムスレッドを明示的に作成する

```bash
openclaw message thread create --channel discord --target channel:<forumId> \
  --thread-name "Topic title" --message "Body of the post"
```

フォーラム親はDiscordコンポーネントを受け付けません。コンポーネントが必要な場合は、スレッド自体（`channel:<threadId>`）に送信してください。

## インタラクティブコンポーネント

OpenClawはエージェントメッセージに対してDiscord components v2コンテナをサポートしています。`components` ペイロード付きでmessage toolを使ってください。インタラクション結果は通常の受信メッセージとしてエージェントにルーティングされ、既存のDiscord `replyToMode` 設定に従います。

サポートされているブロック:

- `text`, `section`, `separator`, `actions`, `media-gallery`, `file`
- アクション行では最大5個のボタン、または単一のセレクトメニューを使用可能
- セレクト種別: `string`, `user`, `role`, `mentionable`, `channel`

デフォルトでは、コンポーネントは単回使用です。`components.reusable=true` を設定すると、ボタン、セレクト、フォームを有効期限が切れるまで複数回使えるようになります。

誰がボタンをクリックできるか制限するには、そのボタンに `allowedUsers` を設定します（DiscordユーザーID、タグ、または `*`）。設定されている場合、一致しないユーザーには一時的な拒否メッセージが返されます。

`/model` および `/models` スラッシュコマンドは、providerとmodelのドロップダウン、およびSubmitステップを備えたインタラクティブなモデルピッカーを開きます。ピッカーの返信はエフェメラルで、呼び出したユーザーだけが使用できます。

ファイル添付:

- `file` ブロックは添付参照（`attachment://<filename>`）を指している必要があります
- `media`/`path`/`filePath` 経由で添付を指定します（単一ファイル）。複数ファイルには `media-gallery` を使用します
- 添付参照と一致させる必要がある場合は、`filename` を使ってアップロード名を上書きします

モーダルフォーム:

- 最大5フィールドまでの `components.modal` を追加します
- フィールド種別: `text`, `checkbox`, `radio`, `select`, `role-select`, `user-select`
- OpenClawはトリガーボタンを自動で追加します

例:

```json5
{
  channel: "discord",
  action: "send",
  to: "channel:123456789012345678",
  message: "Optional fallback text",
  components: {
    reusable: true,
    text: "Choose a path",
    blocks: [
      {
        type: "actions",
        buttons: [
          {
            label: "Approve",
            style: "success",
            allowedUsers: ["123456789012345678"],
          },
          { label: "Decline", style: "danger" },
        ],
      },
      {
        type: "actions",
        select: {
          type: "string",
          placeholder: "Pick an option",
          options: [
            { label: "Option A", value: "a" },
            { label: "Option B", value: "b" },
          ],
        },
      },
    ],
    modal: {
      title: "Details",
      triggerLabel: "Open form",
      fields: [
        { type: "text", label: "Requester" },
        {
          type: "select",
          label: "Priority",
          options: [
            { label: "Low", value: "low" },
            { label: "High", value: "high" },
          ],
        },
      ],
    },
  },
}
```

## アクセス制御とルーティング

<Tabs>
  <Tab title="DMポリシー">
    `channels.discord.dmPolicy` はDMアクセスを制御します（旧式: `channels.discord.dm.policy`）。

    - `pairing`（デフォルト）
    - `allowlist`
    - `open`（`channels.discord.allowFrom` に `"*"` を含める必要があります。旧式: `channels.discord.dm.allowFrom`）
    - `disabled`

    DMポリシーがopenでない場合、未知のユーザーはブロックされます（`pairing` モードではペアリングを促されます）。

    マルチアカウントの優先順位:

    - `channels.discord.accounts.default.allowFrom` は `default` アカウントにのみ適用されます。
    - 名前付きアカウントは、自身の `allowFrom` が未設定の場合に `channels.discord.allowFrom` を継承します。
    - 名前付きアカウントは `channels.discord.accounts.default.allowFrom` を継承しません。

    配信用のDMターゲット形式:

    - `user:<id>`
    - `<@id>` メンション

    数字のみのIDは曖昧なため、明示的な user/channel ターゲット種別が指定されていない限り拒否されます。

  </Tab>

  <Tab title="ギルドポリシー">
    ギルドの処理は `channels.discord.groupPolicy` で制御されます。

    - `open`
    - `allowlist`
    - `disabled`

    `channels.discord` が存在する場合の安全なベースラインは `allowlist` です。

    `allowlist` の動作:

    - ギルドは `channels.discord.guilds` に一致する必要があります（`id` 推奨、slug も可）
    - 任意の送信者許可リスト: `users`（安定したID推奨）および `roles`（ロールIDのみ）。いずれかが設定されている場合、送信者は `users` または `roles` のどちらかに一致すれば許可されます
    - 直接の名前/タグ照合はデフォルトで無効です。緊急時の互換モードとしてのみ `channels.discord.dangerouslyAllowNameMatching: true` を有効にしてください
    - `users` では名前/タグにも対応していますが、IDの方が安全です。名前/タグのエントリが使われている場合、`openclaw security audit` が警告します
    - ギルドに `channels` が設定されている場合、一覧にないチャンネルは拒否されます
    - ギルドに `channels` ブロックがない場合、その許可リスト対象ギルド内のすべてのチャンネルが許可されます

    例:

```json5
{
  channels: {
    discord: {
      groupPolicy: "allowlist",
      guilds: {
        "123456789012345678": {
          requireMention: true,
          ignoreOtherMentions: true,
          users: ["987654321098765432"],
          roles: ["123456789012345678"],
          channels: {
            general: { allow: true },
            help: { allow: true, requireMention: true },
          },
        },
      },
    },
  },
}
```

    `DISCORD_BOT_TOKEN` だけを設定し、`channels.discord` ブロックを作成しない場合、ランタイムフォールバックは `groupPolicy="allowlist"` になります（ログに警告が出ます）。これは `channels.defaults.groupPolicy` が `open` でも同じです。

  </Tab>

  <Tab title="メンションとグループDM">
    ギルドメッセージはデフォルトでメンション必須です。

    メンション検出には以下が含まれます。

    - 明示的なボットメンション
    - 設定されたメンションパターン（`agents.list[].groupChat.mentionPatterns`、フォールバックは `messages.groupChat.mentionPatterns`）
    - 対応ケースでの暗黙的な bot への返信動作

    `requireMention` はギルド/チャンネルごとに設定します（`channels.discord.guilds...`）。
    `ignoreOtherMentions` を設定すると、別のユーザー/ロールには言及しているがボットには言及していないメッセージを任意で破棄します（@everyone/@here は除く）。

    グループDM:

    - デフォルト: 無視される（`dm.groupEnabled=false`）
    - 任意の許可リスト: `dm.groupChannels`（チャンネルIDまたはslug）

  </Tab>
</Tabs>

### ロールベースのエージェントルーティング

`bindings[].match.roles` を使うと、DiscordギルドメンバーをロールIDごとに異なるエージェントへルーティングできます。ロールベースのbindingはロールIDのみに対応し、peerまたはparent-peer bindingの後、guild-only bindingの前に評価されます。bindingが他のmatchフィールドも設定している場合（たとえば `peer` + `guildId` + `roles`）、設定されたすべてのフィールドが一致する必要があります。

```json5
{
  bindings: [
    {
      agentId: "opus",
      match: {
        channel: "discord",
        guildId: "123456789012345678",
        roles: ["111111111111111111"],
      },
    },
    {
      agentId: "sonnet",
      match: {
        channel: "discord",
        guildId: "123456789012345678",
      },
    },
  ],
}
```

## Developer Portalのセットアップ

<AccordionGroup>
  <Accordion title="アプリとボットを作成する">

    1. Discord Developer Portal -> **Applications** -> **New Application**
    2. **Bot** -> **Add Bot**
    3. ボットトークンをコピー

  </Accordion>

  <Accordion title="特権インテント">
    **Bot -> Privileged Gateway Intents** で以下を有効にします。

    - Message Content Intent
    - Server Members Intent（推奨）

    Presence intent は任意で、プレゼンス更新を受信したい場合にのみ必要です。ボットのプレゼンス設定（`setPresence`）には、メンバー向けのプレゼンス更新受信を有効にする必要はありません。

  </Accordion>

  <Accordion title="OAuthスコープとベースライン権限">
    OAuth URL generator:

    - scopes: `bot`, `applications.commands`

    一般的なベースライン権限:

    - View Channels
    - Send Messages
    - Read Message History
    - Embed Links
    - Attach Files
    - Add Reactions（任意）

    明示的に必要でない限り、`Administrator` は避けてください。

  </Accordion>

  <Accordion title="IDをコピーする">
    Discord Developer Modeを有効にしてから、以下をコピーします。

    - server ID
    - channel ID
    - user ID

    監査やプローブを確実に行うため、OpenClaw設定では数字のIDを推奨します。

  </Accordion>
</AccordionGroup>

## ネイティブコマンドとコマンド認証

- `commands.native` のデフォルトは `"auto"` で、Discordでは有効です。
- チャンネルごとの上書き: `channels.discord.commands.native`。
- `commands.native=false` は、以前に登録されたDiscordネイティブコマンドを明示的にクリアします。
- ネイティブコマンド認証には、通常のメッセージ処理と同じDiscord許可リスト/ポリシーが使われます。
- 権限のないユーザーにもDiscord UI上ではコマンドが見える場合がありますが、実行時にはOpenClawの認証が適用され、「not authorized」が返されます。

コマンドカタログと動作については、[Slash commands](/ja-JP/tools/slash-commands) を参照してください。

デフォルトのスラッシュコマンド設定:

- `ephemeral: true`

## 機能の詳細

<AccordionGroup>
  <Accordion title="返信タグとネイティブ返信">
    Discordはエージェント出力内の返信タグをサポートしています。

    - `[[reply_to_current]]`
    - `[[reply_to:<id>]]`

    制御するのは `channels.discord.replyToMode` です。

    - `off`（デフォルト）
    - `first`
    - `all`
    - `batched`

    注: `off` は暗黙的な返信スレッディングを無効にします。明示的な `[[reply_to_*]]` タグは引き続き尊重されます。
    `first` は、そのターンの最初の送信Discordメッセージに常に暗黙のネイティブ返信参照を付与します。
    `batched` は、受信ターンが複数メッセージのデバウンス済みバッチだった場合にのみ、Discordの暗黙のネイティブ返信参照を付与します。これは、ネイティブ返信を主に曖昧で短時間に集中するチャット向けに使いたい場合に有用で、単一メッセージのターンすべてに対して付ける必要がない場合に向いています。

    メッセージIDはコンテキスト/履歴に公開されるため、エージェントは特定のメッセージを対象にできます。

  </Accordion>

  <Accordion title="ライブストリームプレビュー">
    OpenClawは、一時メッセージを送信してテキスト到着に応じて編集することで、返信ドラフトをストリーミングできます。

    - `channels.discord.streaming` はプレビューのストリーミングを制御します（`off` | `partial` | `block` | `progress`、デフォルト: `off`）。
    - デフォルトが `off` のままなのは、Discordのプレビュー編集が特に複数のボットやGatewayが同じアカウントまたはギルドトラフィックを共有している場合に、レート制限へすぐ到達しうるためです。
    - `progress` はチャンネル横断の一貫性のために受け付けられ、Discordでは `partial` にマッピングされます。
    - `channels.discord.streamMode` は旧式の別名で、自動移行されます。
    - `partial` は、トークン到着に応じて単一のプレビューメッセージを編集します。
    - `block` はドラフトサイズのチャンクを出力します（サイズと区切り位置は `draftChunk` で調整）。

    例:

```json5
{
  channels: {
    discord: {
      streaming: "partial",
    },
  },
}
```

    `block` モードのチャンク分割デフォルト（`channels.discord.textChunkLimit` に合わせて制限されます）:

```json5
{
  channels: {
    discord: {
      streaming: "block",
      draftChunk: {
        minChars: 200,
        maxChars: 800,
        breakPreference: "paragraph",
      },
    },
  },
}
```

    プレビューのストリーミングはテキスト専用です。メディア返信は通常配信にフォールバックします。

    注: プレビューのストリーミングはブロックストリーミングとは別です。Discordでブロックストリーミングが明示的に有効になっている場合、OpenClawは二重ストリーミングを避けるためプレビューストリームをスキップします。

  </Accordion>

  <Accordion title="履歴、コンテキスト、スレッド動作">
    ギルドの履歴コンテキスト:

    - `channels.discord.historyLimit` デフォルト `20`
    - フォールバック: `messages.groupChat.historyLimit`
    - `0` で無効化

    DM履歴の制御:

    - `channels.discord.dmHistoryLimit`
    - `channels.discord.dms["<user_id>"].historyLimit`

    スレッド動作:

    - Discordスレッドはチャンネルセッションとしてルーティングされます
    - 親スレッドのメタデータは親セッションのリンクに使用できます
    - スレッド固有のエントリがない限り、スレッド設定は親チャンネル設定を継承します

    チャンネルトピックは **信頼されない** コンテキストとして注入されます（システムプロンプトとしてではありません）。
    返信および引用メッセージのコンテキストは現在、受信したまま保持されます。
    Discordの許可リストは主に「誰がエージェントを起動できるか」を制御するものであり、完全な補助コンテキストの秘匿境界ではありません。

  </Accordion>

  <Accordion title="サブエージェント用のスレッド境界セッション">
    Discordでは、スレッドをセッションターゲットに結び付けられるため、そのスレッド内の後続メッセージは同じセッション（サブエージェントセッションを含む）へルーティングされ続けます。

    コマンド:

    - `/focus <target>` 現在/新規スレッドをサブエージェント/セッションターゲットにバインド
    - `/unfocus` 現在のスレッドbindingを解除
    - `/agents` アクティブな実行とbinding状態を表示
    - `/session idle <duration|off>` フォーカスされたbindingの非アクティブ時自動unfocusを確認/更新
    - `/session max-age <duration|off>` フォーカスされたbindingの最大有効期間を確認/更新

    Config:

```json5
{
  session: {
    threadBindings: {
      enabled: true,
      idleHours: 24,
      maxAgeHours: 0,
    },
  },
  channels: {
    discord: {
      threadBindings: {
        enabled: true,
        idleHours: 24,
        maxAgeHours: 0,
        spawnSubagentSessions: false, // opt-in
      },
    },
  },
}
```

    注:

    - `session.threadBindings.*` はグローバルデフォルトを設定します。
    - `channels.discord.threadBindings.*` はDiscordの動作を上書きします。
    - `spawnSubagentSessions` をtrueにしないと、`sessions_spawn({ thread: true })` 用のスレッド自動作成/バインドは行われません。
    - `spawnAcpSessions` をtrueにしないと、ACP用のスレッド自動作成/バインド（`/acp spawn ... --thread ...` または `sessions_spawn({ runtime: "acp", thread: true })`）は行われません。
    - アカウントでthread bindingsが無効な場合、`/focus` および関連するスレッドbinding操作は利用できません。

    詳しくは [Sub-agents](/ja-JP/tools/subagents)、[ACP Agents](/ja-JP/tools/acp-agents)、[Configuration Reference](/ja-JP/gateway/configuration-reference) を参照してください。

  </Accordion>

  <Accordion title="永続的なACPチャンネルbinding">
    安定した「常時オン」のACPワークスペースには、Discord会話を対象とするトップレベルの型付きACP bindingを設定します。

    Config path:

    - `bindings[]` に `type: "acp"` と `match.channel: "discord"` を指定

    例:

```json5
{
  agents: {
    list: [
      {
        id: "codex",
        runtime: {
          type: "acp",
          acp: {
            agent: "codex",
            backend: "acpx",
            mode: "persistent",
            cwd: "/workspace/openclaw",
          },
        },
      },
    ],
  },
  bindings: [
    {
      type: "acp",
      agentId: "codex",
      match: {
        channel: "discord",
        accountId: "default",
        peer: { kind: "channel", id: "222222222222222222" },
      },
      acp: { label: "codex-main" },
    },
  ],
  channels: {
    discord: {
      guilds: {
        "111111111111111111": {
          channels: {
            "222222222222222222": {
              requireMention: false,
            },
          },
        },
      },
    },
  },
}
```

    注:

    - `/acp spawn codex --bind here` は、現在のDiscordチャンネルまたはスレッドをその場でバインドし、今後のメッセージも同じACPセッションへルーティングし続けます。
    - これは「新しいCodex ACPセッションを開始する」ことも意味しえますが、それ自体で新しいDiscordスレッドを作成するわけではありません。既存のチャンネルがそのままチャット面になります。
    - Codexは依然として自身の `cwd` またはディスク上のbackend workspace で実行される場合があります。そのworkspaceはDiscordスレッドではなく、ランタイム状態です。
    - スレッドメッセージは親チャンネルのACP bindingを継承できます。
    - バインドされたチャンネルまたはスレッドでは、`/new` と `/reset` は同じACPセッションをその場でリセットします。
    - 一時的なスレッドbindingも引き続き機能し、アクティブな間はターゲット解決を上書きできます。
    - `spawnAcpSessions` が必要なのは、OpenClawが `--thread auto|here` 経由で子スレッドを作成/バインドする必要がある場合だけです。現在のチャンネルでの `/acp spawn ... --bind here` には不要です。

    binding動作の詳細は [ACP Agents](/ja-JP/tools/acp-agents) を参照してください。

  </Accordion>

  <Accordion title="リアクション通知">
    ギルドごとのリアクション通知モード:

    - `off`
    - `own`（デフォルト）
    - `all`
    - `allowlist`（`guilds.<id>.users` を使用）

    リアクションイベントはシステムイベントに変換され、ルーティングされたDiscordセッションに添付されます。

  </Accordion>

  <Accordion title="確認リアクション">
    `ackReaction` は、OpenClawが受信メッセージを処理している間に確認用の絵文字リアクションを送信します。

    解決順序:

    - `channels.discord.accounts.<accountId>.ackReaction`
    - `channels.discord.ackReaction`
    - `messages.ackReaction`
    - エージェント識別用の絵文字フォールバック（`agents.list[].identity.emoji`、なければ "👀"）

    注:

    - DiscordはUnicode絵文字またはカスタム絵文字名を受け付けます。
    - チャンネルまたはアカウントでリアクションを無効にするには `""` を使います。

  </Accordion>

  <Accordion title="Config書き込み">
    チャンネル起点のconfig書き込みはデフォルトで有効です。

    これは `/config set|unset` フローに影響します（コマンド機能が有効な場合）。

    無効化:

```json5
{
  channels: {
    discord: {
      configWrites: false,
    },
  },
}
```

  </Accordion>

  <Accordion title="Gatewayプロキシ">
    `channels.discord.proxy` を使うと、Discord GatewayのWebSocketトラフィックと起動時REST参照（application ID + allowlist 解決）をHTTP(S)プロキシ経由にできます。

```json5
{
  channels: {
    discord: {
      proxy: "http://proxy.example:8080",
    },
  },
}
```

    アカウントごとの上書き:

```json5
{
  channels: {
    discord: {
      accounts: {
        primary: {
          proxy: "http://proxy.example:8080",
        },
      },
    },
  },
}
```

  </Accordion>

  <Accordion title="PluralKitサポート">
    PluralKit解決を有効にすると、プロキシされたメッセージをシステムメンバーのアイデンティティにマッピングできます。

```json5
{
  channels: {
    discord: {
      pluralkit: {
        enabled: true,
        token: "pk_live_...", // optional; needed for private systems
      },
    },
  },
}
```

    注:

    - 許可リストでは `pk:<memberId>` を使用できます
    - メンバー表示名は `channels.discord.dangerouslyAllowNameMatching: true` の場合のみ、name/slug で照合されます
    - 参照には元のメッセージIDが使われ、時間ウィンドウ制限があります
    - 参照に失敗した場合、プロキシメッセージはボットメッセージとして扱われ、`allowBots=true` でない限り破棄されます

  </Accordion>

  <Accordion title="プレゼンス設定">
    ステータスまたはアクティビティフィールドを設定したとき、または自動プレゼンスを有効にしたときにプレゼンス更新が適用されます。

    ステータスのみの例:

```json5
{
  channels: {
    discord: {
      status: "idle",
    },
  },
}
```

    アクティビティの例（カスタムステータスがデフォルトのアクティビティ種別です）:

```json5
{
  channels: {
    discord: {
      activity: "Focus time",
      activityType: 4,
    },
  },
}
```

    ストリーミングの例:

```json5
{
  channels: {
    discord: {
      activity: "Live coding",
      activityType: 1,
      activityUrl: "https://twitch.tv/openclaw",
    },
  },
}
```

    アクティビティ種別マップ:

    - 0: Playing
    - 1: Streaming（`activityUrl` が必要）
    - 2: Listening
    - 3: Watching
    - 4: Custom（アクティビティテキストをステータス状態として使用。絵文字は任意）
    - 5: Competing

    自動プレゼンスの例（ランタイム健全性シグナル）:

```json5
{
  channels: {
    discord: {
      autoPresence: {
        enabled: true,
        intervalMs: 30000,
        minUpdateIntervalMs: 15000,
        exhaustedText: "token exhausted",
      },
    },
  },
}
```

    自動プレゼンスはランタイムの可用性をDiscordステータスにマッピングします: healthy => online、degraded または unknown => idle、exhausted または unavailable => dnd。任意のテキスト上書き:

    - `autoPresence.healthyText`
    - `autoPresence.degradedText`
    - `autoPresence.exhaustedText`（`{reason}` プレースホルダー対応）

  </Accordion>

  <Accordion title="Discordでの承認">
    DiscordはDMでのボタンベース承認処理をサポートし、任意で承認プロンプトを元のチャンネルに投稿することもできます。

    Config path:

    - `channels.discord.execApprovals.enabled`
    - `channels.discord.execApprovals.approvers`（任意。可能な場合は `commands.ownerAllowFrom` にフォールバック）
    - `channels.discord.execApprovals.target`（`dm` | `channel` | `both`、デフォルト: `dm`）
    - `agentFilter`, `sessionFilter`, `cleanupAfterResolve`

    Discordは、`enabled` が未設定または `"auto"` で、`execApprovals.approvers` または `commands.ownerAllowFrom` から少なくとも1人の承認者を解決できる場合、ネイティブexec承認を自動で有効にします。Discordはチャンネルの `allowFrom`、旧式の `dm.allowFrom`、またはダイレクトメッセージの `defaultTo` からexec承認者を推測しません。Discordをネイティブ承認クライアントとして明示的に無効にするには `enabled: false` を設定してください。

    `target` が `channel` または `both` の場合、承認プロンプトはチャンネル内に表示されます。解決された承認者だけがボタンを使用でき、他のユーザーにはエフェメラルな拒否メッセージが表示されます。承認プロンプトにはコマンド本文が含まれるため、チャンネル配信は信頼できるチャンネルでのみ有効にしてください。チャンネルIDをセッションキーから導出できない場合、OpenClawはDM配信にフォールバックします。

    Discordは、他のチャットチャンネルで使われる共通の承認ボタンも描画します。ネイティブDiscordアダプターは主に、承認者DMルーティングとチャンネルへのファンアウトを追加します。
    それらのボタンが存在する場合、それらが主要な承認UXになります。OpenClawが手動 `/approve` コマンドを含めるべきなのは、ツール結果がチャット承認を利用不可と示した場合、または手動承認が唯一の経路である場合だけです。

    このハンドラーのGateway認証は、他のGatewayクライアントと同じ共有資格情報解決契約を使います。

    - env優先のローカル認証（`OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`、次に `gateway.auth.*`）
    - local mode では、`gateway.auth.*` が未設定の場合のみ `gateway.remote.*` をフォールバックとして使えます。設定済みだが未解決のローカルSecretRefはfail closedします
    - 適用可能な場合は `gateway.remote.*` によるremote-mode サポート
    - URL上書きは安全に上書きされます: CLI上書きでは暗黙の資格情報を再利用せず、env上書きではenv資格情報のみを使います

    承認解決の動作:

    - `plugin:` で始まるIDは `plugin.approval.resolve` 経由で解決されます。
    - それ以外のIDは `exec.approval.resolve` 経由で解決されます。
    - Discordはここで追加の exec-to-plugin フォールバックを行いません。どのGatewayメソッドを呼ぶかはIDプレフィックスで決まります。

    Exec承認の有効期限はデフォルトで30分です。承認が不明な承認IDで失敗する場合は、承認者解決、機能有効化、および配信された承認ID種別が保留中リクエストと一致していることを確認してください。

    関連ドキュメント: [Exec approvals](/ja-JP/tools/exec-approvals)

  </Accordion>
</AccordionGroup>

## Toolsとアクションゲート

Discord message actions には、メッセージ送信、チャンネル管理、モデレーション、プレゼンス、メタデータの各アクションが含まれます。

主要な例:

- メッセージング: `sendMessage`, `readMessages`, `editMessage`, `deleteMessage`, `threadReply`
- リアクション: `react`, `reactions`, `emojiList`
- モデレーション: `timeout`, `kick`, `ban`
- プレゼンス: `setPresence`

アクションゲートは `channels.discord.actions.*` 配下にあります。

デフォルトのゲート動作:

| Action group                                                                                                                                                             | Default  |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------- |
| reactions, messages, threads, pins, polls, search, memberInfo, roleInfo, channelInfo, channels, voiceStatus, events, stickers, emojiUploads, stickerUploads, permissions | enabled  |
| roles                                                                                                                                                                    | disabled |
| moderation                                                                                                                                                               | disabled |
| presence                                                                                                                                                                 | disabled |

## Components v2 UI

OpenClawはexec承認とクロスコンテキストマーカーのためにDiscord components v2を使用します。Discord message actions もカスタムUI用に `components` を受け付けられます（高度な機能であり、discord tool 経由でコンポーネントペイロードを構築する必要があります）。一方、旧来の `embeds` も引き続き使用できますが、おすすめしません。

- `channels.discord.ui.components.accentColor` は、Discordコンポーネントコンテナで使われるアクセントカラー（hex）を設定します。
- アカウントごとに設定するには `channels.discord.accounts.<id>.ui.components.accentColor` を使います。
- components v2が存在する場合、`embeds` は無視されます。

例:

```json5
{
  channels: {
    discord: {
      ui: {
        components: {
          accentColor: "#5865F2",
        },
      },
    },
  },
}
```

## ボイスチャンネル

OpenClawは、リアルタイムで継続的な会話のためにDiscordボイスチャンネルへ参加できます。これはボイスメッセージ添付とは別機能です。

要件:

- ネイティブコマンド（`commands.native` または `channels.discord.commands.native`）を有効にする。
- `channels.discord.voice` を設定する。
- ボットには対象ボイスチャンネルで Connect と Speak 権限が必要です。

セッションを制御するには、Discord専用のネイティブコマンド `/vc join|leave|status` を使います。このコマンドはアカウントのデフォルトエージェントを使用し、他のDiscordコマンドと同じ許可リストおよびグループポリシールールに従います。

自動参加の例:

```json5
{
  channels: {
    discord: {
      voice: {
        enabled: true,
        autoJoin: [
          {
            guildId: "123456789012345678",
            channelId: "234567890123456789",
          },
        ],
        daveEncryption: true,
        decryptionFailureTolerance: 24,
        tts: {
          provider: "openai",
          openai: { voice: "alloy" },
        },
      },
    },
  },
}
```

注:

- `voice.tts` はボイス再生に対してのみ `messages.tts` を上書きします。
- 音声文字起こしターンは、Discord `allowFrom`（または `dm.allowFrom`）からオーナーステータスを導出します。オーナー以外の話者はオーナー専用ツール（たとえば `gateway` や `cron`）にアクセスできません。
- Voiceはデフォルトで有効です。無効にするには `channels.discord.voice.enabled=false` を設定します。
- `voice.daveEncryption` と `voice.decryptionFailureTolerance` は `@discordjs/voice` の参加オプションへそのまま渡されます。
- 未設定の場合、`@discordjs/voice` のデフォルトは `daveEncryption=true` と `decryptionFailureTolerance=24` です。
- OpenClawは受信復号失敗も監視し、短時間に繰り返し失敗した場合はボイスチャンネルから退出・再参加して自動復旧します。
- 受信ログに `DecryptionFailed(UnencryptedWhenPassthroughDisabled)` が繰り返し表示される場合、これは [discord.js #11419](https://github.com/discordjs/discord.js/issues/11419) で追跡されている上流の `@discordjs/voice` 受信バグである可能性があります。

## ボイスメッセージ

Discordのボイスメッセージには波形プレビューが表示され、OGG/Opus音声とメタデータが必要です。OpenClawは波形を自動生成しますが、音声ファイルを調査および変換するために、Gatewayホストで `ffmpeg` と `ffprobe` が利用可能である必要があります。

要件と制約:

- **ローカルファイルパス** を指定してください（URLは拒否されます）。
- テキストコンテンツは省略してください（Discordでは同一ペイロード内でテキストとボイスメッセージを同時に送れません）。
- 任意の音声形式を受け付けます。必要に応じてOpenClawがOGG/Opusへ変換します。

例:

```bash
message(action="send", channel="discord", target="channel:123", path="/path/to/audio.mp3", asVoice=true)
```

## トラブルシューティング

<AccordionGroup>
  <Accordion title="許可されていないインテントを使用した、またはボットがギルドメッセージを見られない">

    - Message Content Intentを有効にする
    - user/member 解決に依存する場合は Server Members Intent を有効にする
    - インテント変更後にGatewayを再起動する

  </Accordion>

  <Accordion title="ギルドメッセージが予期せずブロックされる">

    - `groupPolicy` を確認する
    - `channels.discord.guilds` 配下のギルド許可リストを確認する
    - ギルドの `channels` マップが存在する場合、一覧にあるチャンネルのみ許可される
    - `requireMention` の動作とメンションパターンを確認する

    便利なチェック:

```bash
openclaw doctor
openclaw channels status --probe
openclaw logs --follow
```

  </Accordion>

  <Accordion title="Require mention を false にしてもまだブロックされる">
    よくある原因:

    - 一致するギルド/チャンネル許可リストがない状態での `groupPolicy="allowlist"`
    - `requireMention` が誤った場所に設定されている（`channels.discord.guilds` またはチャンネルエントリ配下である必要があります）
    - 送信者がギルド/チャンネルの `users` 許可リストでブロックされている

  </Accordion>

  <Accordion title="長時間実行ハンドラーがタイムアウトする、または返信が重複する">

    典型的なログ:

    - `Listener DiscordMessageListener timed out after 30000ms for event MESSAGE_CREATE`
    - `Slow listener detected ...`
    - `discord inbound worker timed out after ...`

    リスナーバジェットのノブ:

    - 単一アカウント: `channels.discord.eventQueue.listenerTimeout`
    - マルチアカウント: `channels.discord.accounts.<accountId>.eventQueue.listenerTimeout`

    Worker実行タイムアウトのノブ:

    - 単一アカウント: `channels.discord.inboundWorker.runTimeoutMs`
    - マルチアカウント: `channels.discord.accounts.<accountId>.inboundWorker.runTimeoutMs`
    - デフォルト: `1800000`（30分）。無効化するには `0` を設定

    推奨ベースライン:

```json5
{
  channels: {
    discord: {
      accounts: {
        default: {
          eventQueue: {
            listenerTimeout: 120000,
          },
          inboundWorker: {
            runTimeoutMs: 1800000,
          },
        },
      },
    },
  },
}
```

    遅いリスナーセットアップには `eventQueue.listenerTimeout` を使い、
    キューに入ったエージェントターン用に別の安全弁が必要な場合にのみ `inboundWorker.runTimeoutMs`
    を使ってください。

  </Accordion>

  <Accordion title="権限監査の不一致">
    `channels status --probe` の権限チェックは数字のチャンネルIDでのみ機能します。

    slugキーを使用している場合でもランタイム照合は機能する場合がありますが、probeでは権限を完全には検証できません。

  </Accordion>

  <Accordion title="DMとペアリングの問題">

    - DM無効: `channels.discord.dm.enabled=false`
    - DMポリシー無効: `channels.discord.dmPolicy="disabled"`（旧式: `channels.discord.dm.policy`）
    - `pairing` モードでペアリング承認待ち

  </Accordion>

  <Accordion title="Bot to bot ループ">
    デフォルトでは、ボットが作成したメッセージは無視されます。

    `channels.discord.allowBots=true` を設定する場合は、ループ動作を避けるために厳格なメンションルールと許可リストルールを使ってください。
    ボットへのメンションを含むボットメッセージだけを受け付けるには、`channels.discord.allowBots="mentions"` を推奨します。

  </Accordion>

  <Accordion title="DecryptionFailed(...) による音声STTドロップ">

    - OpenClawを最新に保つ（`openclaw update`）ことで、Discordボイス受信の復旧ロジックが含まれます
    - `channels.discord.voice.daveEncryption=true`（デフォルト）を確認する
    - `channels.discord.voice.decryptionFailureTolerance=24`（上流デフォルト）から始め、必要な場合にのみ調整する
    - 以下のログを監視する:
      - `discord voice: DAVE decrypt failures detected`
      - `discord voice: repeated decrypt failures; attempting rejoin`
    - 自動再参加後も失敗が続く場合は、ログを収集して [discord.js #11419](https://github.com/discordjs/discord.js/issues/11419) と比較してください

  </Accordion>
</AccordionGroup>

## 設定リファレンスへのポインタ

主要なリファレンス:

- [Configuration reference - Discord](/ja-JP/gateway/configuration-reference#discord)

重要度の高いDiscordフィールド:

- 起動/認証: `enabled`, `token`, `accounts.*`, `allowBots`
- ポリシー: `groupPolicy`, `dm.*`, `guilds.*`, `guilds.*.channels.*`
- コマンド: `commands.native`, `commands.useAccessGroups`, `configWrites`, `slashCommand.*`
- イベントキュー: `eventQueue.listenerTimeout`（リスナーバジェット）、`eventQueue.maxQueueSize`, `eventQueue.maxConcurrency`
- inbound worker: `inboundWorker.runTimeoutMs`
- 返信/履歴: `replyToMode`, `historyLimit`, `dmHistoryLimit`, `dms.*.historyLimit`
- 配信: `textChunkLimit`, `chunkMode`, `maxLinesPerMessage`
- ストリーミング: `streaming`（旧式の別名: `streamMode`）、`draftChunk`, `blockStreaming`, `blockStreamingCoalesce`
- メディア/再試行: `mediaMaxMb`, `retry`
  - `mediaMaxMb` はDiscordへの送信アップロードを制限します（デフォルト: `100MB`）
- アクション: `actions.*`
- プレゼンス: `activity`, `status`, `activityType`, `activityUrl`
- UI: `ui.components.accentColor`
- 機能: `threadBindings`, トップレベル `bindings[]`（`type: "acp"`）、`pluralkit`, `execApprovals`, `intents`, `agentComponents`, `heartbeat`, `responsePrefix`

## 安全性と運用

- ボットトークンは秘密情報として扱ってください（監視された環境では `DISCORD_BOT_TOKEN` 推奨）。
- Discord権限は最小権限で付与してください。
- コマンドのデプロイ/状態が古い場合は、Gatewayを再起動し、`openclaw channels status --probe` で再確認してください。

## 関連

- [ペアリング](/ja-JP/channels/pairing)
- [グループ](/ja-JP/channels/groups)
- [チャンネルルーティング](/ja-JP/channels/channel-routing)
- [セキュリティ](/ja-JP/gateway/security)
- [マルチエージェントルーティング](/ja-JP/concepts/multi-agent)
- [トラブルシューティング](/ja-JP/channels/troubleshooting)
- [スラッシュコマンド](/ja-JP/tools/slash-commands)
