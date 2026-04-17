---
read_when:
    - OpenClaw を初めてセットアップすること
    - 一般的な設定パターンを探すこと
    - 特定の設定セクションに移動すること
summary: '設定の概要: 一般的なタスク、クイックセットアップ、および完全なリファレンスへのリンク'
title: 設定
x-i18n:
    generated_at: "2026-04-11T02:44:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: e874be80d11b9123cac6ce597ec02667fbc798f622a076f68535a1af1f0e399c
    source_path: gateway/configuration.md
    workflow: 15
---

# 設定

OpenClaw は、`~/.openclaw/openclaw.json` から任意の <Tooltip tip="JSON5 はコメントと末尾カンマをサポートします">**JSON5**</Tooltip> 設定を読み込みます。

ファイルが存在しない場合、OpenClaw は安全なデフォルト値を使用します。設定を追加する一般的な理由は次のとおりです。

- チャンネルを接続し、誰がボットにメッセージを送れるかを制御する
- モデル、ツール、サンドボックス化、自動化（cron、hooks）を設定する
- セッション、メディア、ネットワーク、UI を調整する

利用可能なすべてのフィールドについては、[完全なリファレンス](/ja-JP/gateway/configuration-reference) を参照してください。

<Tip>
**設定が初めてですか？** 対話型セットアップには `openclaw onboard` から始めるか、完全なコピー＆ペースト用設定をまとめた [設定例](/ja-JP/gateway/configuration-examples) ガイドを確認してください。
</Tip>

## 最小構成

```json5
// ~/.openclaw/openclaw.json
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
  channels: { whatsapp: { allowFrom: ["+15555550123"] } },
}
```

## 設定の編集

<Tabs>
  <Tab title="対話型ウィザード">
    ```bash
    openclaw onboard       # 完全なオンボーディングフロー
    openclaw configure     # 設定ウィザード
    ```
  </Tab>
  <Tab title="CLI（ワンライナー）">
    ```bash
    openclaw config get agents.defaults.workspace
    openclaw config set agents.defaults.heartbeat.every "2h"
    openclaw config unset plugins.entries.brave.config.webSearch.apiKey
    ```
  </Tab>
  <Tab title="Control UI">
    [http://127.0.0.1:18789](http://127.0.0.1:18789) を開き、**Config** タブを使用します。
    Control UI は、ライブ設定スキーマからフォームをレンダリングします。これには、利用可能な場合はフィールドの
    `title` / `description` のドキュメントメタデータに加えて、plugin と channel のスキーマも含まれ、
    エスケープハッチとして **Raw JSON** エディターも提供されます。ドリルダウン UI やその他のツール向けに、
    Gateway は `config.schema.lookup` も公開しており、1 つのパスにスコープされたスキーマノードと、
    その直下の子要約を取得できます。
  </Tab>
  <Tab title="直接編集">
    `~/.openclaw/openclaw.json` を直接編集します。Gateway はこのファイルを監視し、変更を自動的に適用します（[ホットリロード](#config-hot-reload) を参照）。
  </Tab>
</Tabs>

## 厳格な検証

<Warning>
OpenClaw は、スキーマに完全に一致する設定のみを受け入れます。不明なキー、不正な型、無効な値があると、Gateway は**起動を拒否**します。ルートレベルの唯一の例外は `$schema`（文字列）で、エディターが JSON Schema メタデータを付与できるようにするためのものです。
</Warning>

スキーマツールに関する注記:

- `openclaw config schema` は、Control UI と設定検証で使用されるものと同じ JSON Schema ファミリーを出力します。
- そのスキーマ出力は、`openclaw.json` の正規の機械可読コントラクトとして扱ってください。この概要と設定リファレンスはその要約です。
- フィールドの `title` と `description` の値は、エディターやフォームツール向けにスキーマ出力へ引き継がれます。
- ネストしたオブジェクト、ワイルドカード（`*`）、配列要素（`[]`）の各エントリは、一致するフィールドドキュメントが存在する場合、同じドキュメントメタデータを継承します。
- `anyOf` / `oneOf` / `allOf` の合成ブランチも同じドキュメントメタデータを継承するため、union/intersection の各バリアントでも同じフィールドヘルプが維持されます。
- `config.schema.lookup` は、正規化された 1 つの設定パスについて、浅いスキーマノード（`title`、`description`、`type`、`enum`、`const`、一般的な境界値、および類似の検証フィールド）、一致した UI ヒントメタデータ、そしてドリルダウンツール向けの直下の子要約を返します。
- 実行時の plugin/channel スキーマは、gateway が現在のマニフェストレジストリを読み込める場合にマージされます。
- `pnpm config:docs:check` は、ドキュメント向け設定ベースライン成果物と現在のスキーマサーフェスとのドリフトを検出します。

検証に失敗した場合:

- Gateway は起動しません
- 診断コマンドのみが動作します（`openclaw doctor`、`openclaw logs`、`openclaw health`、`openclaw status`）
- 正確な問題を確認するには `openclaw doctor` を実行します
- 修復を適用するには `openclaw doctor --fix`（または `--yes`）を実行します

## 一般的なタスク

<AccordionGroup>
  <Accordion title="チャンネルをセットアップする（WhatsApp、Telegram、Discord など）">
    各チャンネルには、`channels.<provider>` の下に専用の設定セクションがあります。セットアップ手順については、各チャンネル専用ページを参照してください。

    - [WhatsApp](/ja-JP/channels/whatsapp) — `channels.whatsapp`
    - [Telegram](/ja-JP/channels/telegram) — `channels.telegram`
    - [Discord](/ja-JP/channels/discord) — `channels.discord`
    - [Feishu](/ja-JP/channels/feishu) — `channels.feishu`
    - [Google Chat](/ja-JP/channels/googlechat) — `channels.googlechat`
    - [Microsoft Teams](/ja-JP/channels/msteams) — `channels.msteams`
    - [Slack](/ja-JP/channels/slack) — `channels.slack`
    - [Signal](/ja-JP/channels/signal) — `channels.signal`
    - [iMessage](/ja-JP/channels/imessage) — `channels.imessage`
    - [Mattermost](/ja-JP/channels/mattermost) — `channels.mattermost`

    すべてのチャンネルは同じ DM ポリシーパターンを共有します。

    ```json5
    {
      channels: {
        telegram: {
          enabled: true,
          botToken: "123:abc",
          dmPolicy: "pairing",   // pairing | allowlist | open | disabled
          allowFrom: ["tg:123"], // allowlist/open の場合のみ
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="モデルを選択して設定する">
    プライマリモデルと任意のフォールバックを設定します。

    ```json5
    {
      agents: {
        defaults: {
          model: {
            primary: "anthropic/claude-sonnet-4-6",
            fallbacks: ["openai/gpt-5.4"],
          },
          models: {
            "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
            "openai/gpt-5.4": { alias: "GPT" },
          },
        },
      },
    }
    ```

    - `agents.defaults.models` はモデルカタログを定義し、`/model` の許可リストとしても機能します。
    - モデル参照は `provider/model` 形式を使用します（例: `anthropic/claude-opus-4-6`）。
    - `agents.defaults.imageMaxDimensionPx` は transcript/tool 画像の縮小サイズを制御します（デフォルトは `1200`）。値を小さくすると、スクリーンショットの多い実行で vision token 使用量を減らせることが一般的です。
    - チャット中のモデル切り替えについては [Models CLI](/ja-JP/concepts/models) を、認証ローテーションとフォールバック動作については [Model Failover](/ja-JP/concepts/model-failover) を参照してください。
    - カスタム/セルフホスト型 provider については、リファレンスの [Custom providers](/ja-JP/gateway/configuration-reference#custom-providers-and-base-urls) を参照してください。

  </Accordion>

  <Accordion title="誰がボットにメッセージを送れるかを制御する">
    DM アクセスは `dmPolicy` によってチャンネルごとに制御されます。

    - `"pairing"`（デフォルト）: 未知の送信者には承認用の一度限りのペアリングコードが送られます
    - `"allowlist"`: `allowFrom`（またはペア済みの許可ストア）に含まれる送信者のみ
    - `"open"`: すべての受信 DM を許可します（`allowFrom: ["*"]` が必要）
    - `"disabled"`: すべての DM を無視します

    グループでは、`groupPolicy` + `groupAllowFrom` またはチャンネル固有の許可リストを使用します。

    チャンネルごとの詳細については、[完全なリファレンス](/ja-JP/gateway/configuration-reference#dm-and-group-access) を参照してください。

  </Accordion>

  <Accordion title="グループチャットのメンションゲートを設定する">
    グループメッセージはデフォルトで**メンション必須**です。agent ごとにパターンを設定します。

    ```json5
    {
      agents: {
        list: [
          {
            id: "main",
            groupChat: {
              mentionPatterns: ["@openclaw", "openclaw"],
            },
          },
        ],
      },
      channels: {
        whatsapp: {
          groups: { "*": { requireMention: true } },
        },
      },
    }
    ```

    - **メタデータメンション**: ネイティブの @ メンション（WhatsApp のタップしてメンション、Telegram の @bot など）
    - **テキストパターン**: `mentionPatterns` 内の安全な regex パターン
    - チャンネルごとの上書きや self-chat モードについては、[完全なリファレンス](/ja-JP/gateway/configuration-reference#group-chat-mention-gating) を参照してください。

  </Accordion>

  <Accordion title="agent ごとに Skills を制限する">
    共有ベースラインには `agents.defaults.skills` を使用し、その後
    特定の agent を `agents.list[].skills` で上書きします。

    ```json5
    {
      agents: {
        defaults: {
          skills: ["github", "weather"],
        },
        list: [
          { id: "writer" }, // github, weather を継承
          { id: "docs", skills: ["docs-search"] }, // defaults を置き換える
          { id: "locked-down", skills: [] }, // Skills なし
        ],
      },
    }
    ```

    - デフォルトで Skills を無制限にするには、`agents.defaults.skills` を省略します。
    - defaults を継承するには、`agents.list[].skills` を省略します。
    - Skills を無効にするには、`agents.list[].skills: []` を設定します。
    - [Skills](/ja-JP/tools/skills)、[Skills config](/ja-JP/tools/skills-config)、および
      [設定リファレンス](/ja-JP/gateway/configuration-reference#agents-defaults-skills) を参照してください。

  </Accordion>

  <Accordion title="Gateway のチャンネルヘルス監視を調整する">
    stale に見えるチャンネルを gateway がどの程度積極的に再起動するかを制御します。

    ```json5
    {
      gateway: {
        channelHealthCheckMinutes: 5,
        channelStaleEventThresholdMinutes: 30,
        channelMaxRestartsPerHour: 10,
      },
      channels: {
        telegram: {
          healthMonitor: { enabled: false },
          accounts: {
            alerts: {
              healthMonitor: { enabled: true },
            },
          },
        },
      },
    }
    ```

    - ヘルス監視による再起動をグローバルに無効化するには、`gateway.channelHealthCheckMinutes: 0` を設定します。
    - `channelStaleEventThresholdMinutes` は、チェック間隔以上である必要があります。
    - グローバル監視を無効にせずに 1 つのチャンネルまたはアカウントだけ自動再起動を無効化するには、`channels.<provider>.healthMonitor.enabled` または `channels.<provider>.accounts.<id>.healthMonitor.enabled` を使用します。
    - 運用上のデバッグについては [Health Checks](/ja-JP/gateway/health) を、すべてのフィールドについては [完全なリファレンス](/ja-JP/gateway/configuration-reference#gateway) を参照してください。

  </Accordion>

  <Accordion title="セッションとリセットを設定する">
    セッションは会話の継続性と分離を制御します。

    ```json5
    {
      session: {
        dmScope: "per-channel-peer",  // 複数ユーザー向けに推奨
        threadBindings: {
          enabled: true,
          idleHours: 24,
          maxAgeHours: 0,
        },
        reset: {
          mode: "daily",
          atHour: 4,
          idleMinutes: 120,
        },
      },
    }
    ```

    - `dmScope`: `main`（共有）| `per-peer` | `per-channel-peer` | `per-account-channel-peer`
    - `threadBindings`: スレッドに紐づくセッションルーティングのグローバルデフォルトです（Discord は `/focus`、`/unfocus`、`/agents`、`/session idle`、`/session max-age` をサポートします）。
    - スコープ、ID リンク、送信ポリシーについては [Session Management](/ja-JP/concepts/session) を参照してください。
    - すべてのフィールドについては [完全なリファレンス](/ja-JP/gateway/configuration-reference#session) を参照してください。

  </Accordion>

  <Accordion title="サンドボックス化を有効にする">
    分離された Docker コンテナ内で agent セッションを実行します。

    ```json5
    {
      agents: {
        defaults: {
          sandbox: {
            mode: "non-main",  // off | non-main | all
            scope: "agent",    // session | agent | shared
          },
        },
      },
    }
    ```

    まずイメージをビルドします: `scripts/sandbox-setup.sh`

    完全なガイドについては [Sandboxing](/ja-JP/gateway/sandboxing) を、すべてのオプションについては [完全なリファレンス](/ja-JP/gateway/configuration-reference#agentsdefaultssandbox) を参照してください。

  </Accordion>

  <Accordion title="公式 iOS ビルド向けに relay ベースの push を有効にする">
    relay ベースの push は `openclaw.json` で設定します。

    gateway 設定に次を追加します。

    ```json5
    {
      gateway: {
        push: {
          apns: {
            relay: {
              baseUrl: "https://relay.example.com",
              // 任意。デフォルト: 10000
              timeoutMs: 10000,
            },
          },
        },
      },
    }
    ```

    CLI での同等操作:

    ```bash
    openclaw config set gateway.push.apns.relay.baseUrl https://relay.example.com
    ```

    これにより行われること:

    - gateway が外部 relay 経由で `push.test`、wake nudges、reconnect wakes を送信できるようにします。
    - ペアリングされた iOS アプリから転送された、登録スコープの send grant を使用します。gateway にデプロイ全体の relay token は不要です。
    - 各 relay ベースの登録は、iOS アプリがペアリングした gateway identity に紐付けられるため、別の gateway が保存済み登録を再利用することはできません。
    - ローカル/手動の iOS ビルドは direct APNs のままです。relay ベースの送信が適用されるのは、relay を通じて登録された公式配布ビルドのみです。
    - 公式/TestFlight iOS ビルドに組み込まれた relay base URL と一致している必要があります。これにより、登録トラフィックと送信トラフィックの両方が同じ relay デプロイメントに到達します。

    エンドツーエンドのフロー:

    1. 同じ relay base URL でコンパイルされた公式/TestFlight iOS ビルドをインストールします。
    2. gateway で `gateway.push.apns.relay.baseUrl` を設定します。
    3. iOS アプリを gateway にペアリングし、node セッションと operator セッションの両方を接続します。
    4. iOS アプリが gateway identity を取得し、App Attest とアプリのレシートを使って relay に登録し、その後 relay ベースの `push.apns.register` payload をペアリング済み gateway に公開します。
    5. gateway は relay handle と send grant を保存し、それらを `push.test`、wake nudges、reconnect wakes に使用します。

    運用上の注記:

    - iOS アプリを別の gateway に切り替える場合、アプリを再接続して、その gateway に紐付いた新しい relay 登録を公開できるようにします。
    - 別の relay デプロイメントを指す新しい iOS ビルドを配布した場合、アプリは古い relay origin を再利用する代わりに、キャッシュされた relay 登録を更新します。

    互換性に関する注記:

    - `OPENCLAW_APNS_RELAY_BASE_URL` と `OPENCLAW_APNS_RELAY_TIMEOUT_MS` は、一時的な env 上書きとして引き続き使用できます。
    - `OPENCLAW_APNS_RELAY_ALLOW_HTTP=true` は、loopback 専用の開発用エスケープハッチのままです。HTTP の relay URL を設定に永続化しないでください。

    エンドツーエンドのフローについては [iOS App](/ja-JP/platforms/ios#relay-backed-push-for-official-builds) を、relay のセキュリティモデルについては [Authentication and trust flow](/ja-JP/platforms/ios#authentication-and-trust-flow) を参照してください。

  </Accordion>

  <Accordion title="heartbeat（定期チェックイン）を設定する">
    ```json5
    {
      agents: {
        defaults: {
          heartbeat: {
            every: "30m",
            target: "last",
          },
        },
      },
    }
    ```

    - `every`: 期間文字列（`30m`、`2h`）。無効化するには `0m` を設定します。
    - `target`: `last` | `none` | `<channel-id>`（例: `discord`、`matrix`、`telegram`、`whatsapp`）
    - `directPolicy`: DM スタイルの heartbeat target に対して `allow`（デフォルト）または `block`
    - 完全なガイドについては [Heartbeat](/ja-JP/gateway/heartbeat) を参照してください。

  </Accordion>

  <Accordion title="cron ジョブを設定する">
    ```json5
    {
      cron: {
        enabled: true,
        maxConcurrentRuns: 2,
        sessionRetention: "24h",
        runLog: {
          maxBytes: "2mb",
          keepLines: 2000,
        },
      },
    }
    ```

    - `sessionRetention`: 完了した分離実行セッションを `sessions.json` から削除します（デフォルトは `24h`、無効化するには `false` を設定）。
    - `runLog`: `cron/runs/<jobId>.jsonl` をサイズと保持行数で削除します。
    - 機能概要と CLI 例については [Cron jobs](/ja-JP/automation/cron-jobs) を参照してください。

  </Accordion>

  <Accordion title="webhook（hooks）を設定する">
    Gateway で HTTP webhook エンドポイントを有効にします。

    ```json5
    {
      hooks: {
        enabled: true,
        token: "shared-secret",
        path: "/hooks",
        defaultSessionKey: "hook:ingress",
        allowRequestSessionKey: false,
        allowedSessionKeyPrefixes: ["hook:"],
        mappings: [
          {
            match: { path: "gmail" },
            action: "agent",
            agentId: "main",
            deliver: true,
          },
        ],
      },
    }
    ```

    セキュリティに関する注記:
    - すべての hook/webhook payload 内容は信頼できない入力として扱ってください。
    - 専用の `hooks.token` を使用してください。共有 Gateway token を使い回さないでください。
    - Hook 認証はヘッダーのみです（`Authorization: Bearer ...` または `x-openclaw-token`）。クエリ文字列の token は拒否されます。
    - `hooks.path` は `/` にできません。webhook 受信は `/hooks` のような専用サブパスにしてください。
    - 危険なコンテンツ回避フラグ（`hooks.gmail.allowUnsafeExternalContent`、`hooks.mappings[].allowUnsafeExternalContent`）は、厳密に限定したデバッグを行う場合を除き無効のままにしてください。
    - `hooks.allowRequestSessionKey` を有効にする場合は、呼び出し側が選ぶ session key を制限するために `hooks.allowedSessionKeyPrefixes` も設定してください。
    - hook 駆動の agent では、強力で最新のモデル階層と厳格な tool ポリシーを優先してください（たとえば、可能であればメッセージングのみ + サンドボックス化）。

    すべてのマッピングオプションと Gmail 統合については、[完全なリファレンス](/ja-JP/gateway/configuration-reference#hooks) を参照してください。

  </Accordion>

  <Accordion title="マルチエージェントルーティングを設定する">
    別々の workspace と session を持つ複数の分離された agent を実行します。

    ```json5
    {
      agents: {
        list: [
          { id: "home", default: true, workspace: "~/.openclaw/workspace-home" },
          { id: "work", workspace: "~/.openclaw/workspace-work" },
        ],
      },
      bindings: [
        { agentId: "home", match: { channel: "whatsapp", accountId: "personal" } },
        { agentId: "work", match: { channel: "whatsapp", accountId: "biz" } },
      ],
    }
    ```

    バインディングルールと agent ごとのアクセスプロファイルについては、[Multi-Agent](/ja-JP/concepts/multi-agent) と [完全なリファレンス](/ja-JP/gateway/configuration-reference#multi-agent-routing) を参照してください。

  </Accordion>

  <Accordion title="設定を複数ファイルに分割する（$include）">
    大きな設定を整理するには `$include` を使用します。

    ```json5
    // ~/.openclaw/openclaw.json
    {
      gateway: { port: 18789 },
      agents: { $include: "./agents.json5" },
      broadcast: {
        $include: ["./clients/a.json5", "./clients/b.json5"],
      },
    }
    ```

    - **単一ファイル**: そのオブジェクト全体を置き換えます
    - **ファイル配列**: 順番に deep-merge されます（後勝ち）
    - **兄弟キー**: include の後にマージされます（include された値を上書き）
    - **ネストした include**: 最大 10 階層までサポート
    - **相対パス**: include 元ファイルを基準に解決されます
    - **エラーハンドリング**: ファイル欠如、パースエラー、循環 include に対して明確なエラーを返します

  </Accordion>
</AccordionGroup>

## 設定のホットリロード

Gateway は `~/.openclaw/openclaw.json` を監視し、変更を自動的に適用します。ほとんどの設定では手動再起動は不要です。

### リロードモード

| モード                   | 動作                                                                                 |
| ---------------------- | ------------------------------------------------------------------------------------ |
| **`hybrid`**（デフォルト） | 安全な変更を即座にホット適用します。重要な変更では自動的に再起動します。                  |
| **`hot`**              | 安全な変更のみをホット適用します。再起動が必要な場合は警告を記録し、対応は自分で行います。 |
| **`restart`**          | 安全かどうかに関係なく、設定変更のたびに Gateway を再起動します。                       |
| **`off`**              | ファイル監視を無効にします。変更は次回の手動再起動で反映されます。                       |

```json5
{
  gateway: {
    reload: { mode: "hybrid", debounceMs: 300 },
  },
}
```

### ホット適用されるものと再起動が必要なもの

ほとんどのフィールドはダウンタイムなしでホット適用されます。`hybrid` モードでは、再起動が必要な変更は自動的に処理されます。

| カテゴリ             | フィールド                                                           | 再起動が必要? |
| ---------------- | ---------------------------------------------------------------- | ------- |
| Channels         | `channels.*`、`web`（WhatsApp）— すべての組み込みおよび extension channels | いいえ     |
| Agent & models   | `agent`、`agents`、`models`、`routing`                             | いいえ     |
| Automation       | `hooks`、`cron`、`agent.heartbeat`                                | いいえ     |
| Sessions & messages | `session`、`messages`                                          | いいえ     |
| Tools & media    | `tools`、`browser`、`skills`、`audio`、`talk`                       | いいえ     |
| UI & misc        | `ui`、`logging`、`identity`、`bindings`                           | いいえ     |
| Gateway server   | `gateway.*`（port、bind、auth、tailscale、TLS、HTTP）             | **はい** |
| Infrastructure   | `discovery`、`canvasHost`、`plugins`                              | **はい** |

<Note>
`gateway.reload` と `gateway.remote` は例外です。これらの変更では**再起動は発生しません**。
</Note>

## Config RPC（プログラムによる更新）

<Note>
control-plane の書き込み RPC（`config.apply`、`config.patch`、`update.run`）は、`deviceId+clientIp` ごとに **60 秒あたり 3 リクエスト** にレート制限されます。制限された場合、RPC は `retryAfterMs` を付けて `UNAVAILABLE` を返します。
</Note>

安全なデフォルトフロー:

- `config.schema.lookup`: 浅い
  スキーマノード、一致したヒントメタデータ、直下の子要約とともに、1 つのパスにスコープされた設定サブツリーを確認する
- `config.get`: 現在のスナップショット + hash を取得する
- `config.patch`: 推奨される部分更新パス
- `config.apply`: 設定全体を置き換える場合のみ
- `update.run`: 明示的な self-update + restart

設定全体を置き換えるのでない場合は、`config.schema.lookup`
の後に `config.patch` を優先してください。

<AccordionGroup>
  <Accordion title="config.apply（完全置換）">
    設定全体を検証して書き込み、Gateway を 1 ステップで再起動します。

    <Warning>
    `config.apply` は**設定全体**を置き換えます。部分更新には `config.patch` を、単一キーには `openclaw config set` を使用してください。
    </Warning>

    パラメータ:

    - `raw`（string）— 設定全体の JSON5 payload
    - `baseHash`（任意）— `config.get` からの設定 hash（設定が存在する場合は必須）
    - `sessionKey`（任意）— 再起動後の wake-up ping 用 session key
    - `note`（任意）— restart sentinel 用のメモ
    - `restartDelayMs`（任意）— 再起動までの遅延（デフォルト 2000）

    再起動リクエストは、すでに保留中/進行中のものがある場合はまとめられ、再起動サイクル間には 30 秒のクールダウンが適用されます。

    ```bash
    openclaw gateway call config.get --params '{}'  # payload.hash を取得
    openclaw gateway call config.apply --params '{
      "raw": "{ agents: { defaults: { workspace: \"~/.openclaw/workspace\" } } }",
      "baseHash": "<hash>",
      "sessionKey": "agent:main:whatsapp:direct:+15555550123"
    }'
    ```

  </Accordion>

  <Accordion title="config.patch（部分更新）">
    部分更新を既存の設定にマージします（JSON merge patch セマンティクス）。

    - オブジェクトは再帰的にマージされる
    - `null` はキーを削除する
    - 配列は置き換えられる

    パラメータ:

    - `raw`（string）— 変更するキーだけを含む JSON5
    - `baseHash`（必須）— `config.get` からの設定 hash
    - `sessionKey`、`note`、`restartDelayMs` — `config.apply` と同じ

    再起動動作は `config.apply` と同じです。保留中の再起動はまとめられ、再起動サイクル間には 30 秒のクールダウンがあります。

    ```bash
    openclaw gateway call config.patch --params '{
      "raw": "{ channels: { telegram: { groups: { \"*\": { requireMention: false } } } } }",
      "baseHash": "<hash>"
    }'
    ```

  </Accordion>
</AccordionGroup>

## 環境変数

OpenClaw は、親プロセスからの env vars に加えて、次も読み込みます。

- 現在の作業ディレクトリの `.env`（存在する場合）
- `~/.openclaw/.env`（グローバルフォールバック）

どちらのファイルも、既存の env vars を上書きしません。設定内でインライン env vars を設定することもできます。

```json5
{
  env: {
    OPENROUTER_API_KEY: "sk-or-...",
    vars: { GROQ_API_KEY: "gsk-..." },
  },
}
```

<Accordion title="シェル env のインポート（任意）">
  有効な場合、期待されるキーが設定されていないと、OpenClaw はログインシェルを実行し、不足しているキーのみをインポートします。

```json5
{
  env: {
    shellEnv: { enabled: true, timeoutMs: 15000 },
  },
}
```

環境変数での同等設定: `OPENCLAW_LOAD_SHELL_ENV=1`
</Accordion>

<Accordion title="設定値での env var 置換">
  任意の設定文字列値で `${VAR_NAME}` を使って env vars を参照できます。

```json5
{
  gateway: { auth: { token: "${OPENCLAW_GATEWAY_TOKEN}" } },
  models: { providers: { custom: { apiKey: "${CUSTOM_API_KEY}" } } },
}
```

ルール:

- 一致するのは大文字名のみ: `[A-Z_][A-Z0-9_]*`
- 存在しない/空の vars は読み込み時エラーになります
- リテラル出力にするには `$${VAR}` でエスケープします
- `$include` ファイル内でも動作します
- インライン置換: `"${BASE}/v1"` → `"https://api.example.com/v1"`

</Accordion>

<Accordion title="Secret refs（env、file、exec）">
  SecretRef オブジェクトをサポートするフィールドでは、次を使用できます。

```json5
{
  models: {
    providers: {
      openai: { apiKey: { source: "env", provider: "default", id: "OPENAI_API_KEY" } },
    },
  },
  skills: {
    entries: {
      "image-lab": {
        apiKey: {
          source: "file",
          provider: "filemain",
          id: "/skills/entries/image-lab/apiKey",
        },
      },
    },
  },
  channels: {
    googlechat: {
      serviceAccountRef: {
        source: "exec",
        provider: "vault",
        id: "channels/googlechat/serviceAccount",
      },
    },
  },
}
```

SecretRef の詳細（`env`/`file`/`exec` 用の `secrets.providers` を含む）は [Secrets Management](/ja-JP/gateway/secrets) にあります。
サポートされる認証情報パスは [SecretRef Credential Surface](/ja-JP/reference/secretref-credential-surface) に一覧があります。
</Accordion>

優先順位と取得元の完全な説明については [Environment](/ja-JP/help/environment) を参照してください。

## 完全なリファレンス

フィールドごとの完全なリファレンスについては、**[Configuration Reference](/ja-JP/gateway/configuration-reference)** を参照してください。

---

_関連: [設定例](/ja-JP/gateway/configuration-examples) · [Configuration Reference](/ja-JP/gateway/configuration-reference) · [Doctor](/ja-JP/gateway/doctor)_
