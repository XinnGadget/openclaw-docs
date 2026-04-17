---
read_when:
    - アクセスや自動化を拡大する機能の追加
summary: シェルアクセスを持つ AI Gateway を実行する際のセキュリティ上の考慮事項と脅威モデル
title: セキュリティ
x-i18n:
    generated_at: "2026-04-12T23:28:28Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7f3ef693813b696be2e24bcc333c8ee177fa56c3cb06c5fac12a0bd220a29917
    source_path: gateway/security/index.md
    workflow: 15
---

# セキュリティ

<Warning>
**パーソナルアシスタントの信頼モデル:** このガイダンスは、Gateway ごとに 1 つの信頼されたオペレーター境界（単一ユーザー / パーソナルアシスタントモデル）を前提としています。
OpenClaw は、複数の敵対的ユーザーが 1 つのエージェント / Gateway を共有する状況における、敵対的なマルチテナント用セキュリティ境界では**ありません**。
信頼度が混在する環境や敵対的ユーザー環境で運用する必要がある場合は、信頼境界を分離してください（別々の Gateway + 認証情報、理想的には別々の OS ユーザー / ホスト）。
</Warning>

**このページの内容:** [信頼モデル](#scope-first-personal-assistant-security-model) | [クイック監査](#quick-check-openclaw-security-audit) | [強化されたベースライン](#hardened-baseline-in-60-seconds) | [DM アクセスモデル](#dm-access-model-pairing-allowlist-open-disabled) | [設定の強化](#configuration-hardening-examples) | [インシデント対応](#incident-response)

## まず範囲を確認: パーソナルアシスタントのセキュリティモデル

OpenClaw のセキュリティガイダンスは、**パーソナルアシスタント**としてのデプロイを前提としています。つまり、信頼された 1 つのオペレーター境界があり、その中に複数のエージェントが存在する可能性がある構成です。

- サポートされるセキュリティ態勢: Gateway ごとに 1 つのユーザー / 信頼境界（境界ごとに 1 つの OS ユーザー / ホスト / VPS を推奨）。
- サポートされないセキュリティ境界: 相互に信頼していない、または敵対的なユーザーが共有する 1 つの Gateway / エージェント。
- 敵対的ユーザーの分離が必要な場合は、信頼境界ごとに分割してください（別々の Gateway + 認証情報、理想的には別々の OS ユーザー / ホスト）。
- 複数の信頼していないユーザーが 1 つのツール有効化エージェントにメッセージできる場合、そのエージェントに委任された同じツール権限を共有しているものとして扱ってください。

このページでは、この**モデルの範囲内**での強化について説明します。1 つの共有 Gateway 上での敵対的マルチテナント分離を主張するものではありません。

## クイックチェック: `openclaw security audit`

関連項目: [形式検証（セキュリティモデル）](/ja-JP/security/formal-verification)

これを定期的に実行してください（特に設定を変更した後や、ネットワークの公開面を増やした後）。

```bash
openclaw security audit
openclaw security audit --deep
openclaw security audit --fix
openclaw security audit --json
```

`security audit --fix` は意図的に対象を絞っています。一般的なオープングループポリシーを許可リストに切り替え、`logging.redactSensitive: "tools"` を復元し、state/config/include-file の権限を厳格化し、Windows 上で実行している場合は POSIX の `chmod` ではなく Windows ACL のリセットを使用します。

一般的な落とし穴（Gateway 認証の露出、ブラウザ制御の露出、権限の強い許可リスト、ファイルシステム権限、緩い exec 承認、オープンチャネルのツール露出）を検出します。

OpenClaw は製品であると同時に実験でもあります。最先端モデルの動作を、実際のメッセージング面と実際のツールに接続しているからです。**「完全に安全」な設定はありません。** 目標は、次の点について意図的であることです。

- 誰がボットと対話できるか
- ボットがどこで行動できるか
- ボットが何に触れられるか

まずは機能する最小限のアクセスから始め、確信が持てるようになってから段階的に広げてください。

### デプロイとホストの信頼

OpenClaw は、ホストと設定境界が信頼されていることを前提としています。

- 誰かが Gateway ホストの state/config（`openclaw.json` を含む `~/.openclaw`）を変更できるなら、その人は信頼されたオペレーターとして扱ってください。
- 相互に信頼していない / 敵対的な複数のオペレーターのために 1 つの Gateway を実行することは、**推奨される構成ではありません**。
- 信頼度が混在するチームでは、別々の Gateway（または最低でも別々の OS ユーザー / ホスト）で信頼境界を分離してください。
- 推奨されるデフォルト: マシン / ホスト（または VPS）ごとに 1 ユーザー、そのユーザーに対して 1 Gateway、その Gateway 内に 1 つ以上のエージェント。
- 1 つの Gateway インスタンス内では、認証済みオペレーターアクセスは信頼されたコントロールプレーンのロールであり、ユーザー単位のテナントロールではありません。
- セッション識別子（`sessionKey`、セッション ID、ラベル）はルーティングセレクターであり、認可トークンではありません。
- 複数人が 1 つのツール有効化エージェントにメッセージできる場合、その全員が同じ権限セットを操作できます。ユーザー単位のセッション / メモリー分離はプライバシーには役立ちますが、共有エージェントをユーザー単位のホスト認可に変えるものではありません。

### 共有 Slack ワークスペース: 実際のリスク

「Slack の全員がボットにメッセージできる」場合、中核となるリスクは委任されたツール権限です。

- 許可された送信者は誰でも、エージェントのポリシー内でツール呼び出し（`exec`、ブラウザ、ネットワーク / ファイルツール）を誘発できます。
- ある送信者からのプロンプト / コンテンツインジェクションによって、共有 state、デバイス、または出力に影響するアクションが発生する可能性があります。
- 1 つの共有エージェントが機密の認証情報 / ファイルを持っている場合、許可された送信者は誰でも、ツール使用を通じてそれらの流出を誘導できる可能性があります。

チームワークフローには最小限のツールを備えた別々のエージェント / Gateway を使い、個人データを扱うエージェントは非公開に保ってください。

### 会社共有エージェント: 許容されるパターン

これは、そのエージェントを使用する全員が同じ信頼境界内にあり（たとえば 1 つの会社チーム）、そのエージェントのスコープが厳密に業務に限定されている場合には許容されます。

- 専用のマシン / VM / コンテナ上で実行する。
- そのランタイム専用の OS ユーザー + 専用のブラウザ / プロファイル / アカウントを使用する。
- そのランタイムで個人の Apple / Google アカウントや個人用パスワードマネージャー / ブラウザプロファイルにサインインしない。

同じランタイム上で個人 ID と会社 ID を混在させると、分離が崩れ、個人データ露出のリスクが高まります。

## Gateway と node の信頼概念

Gateway と node は役割が異なるものの、1 つのオペレーター信頼ドメインとして扱ってください。

- **Gateway** はコントロールプレーンおよびポリシー面です（`gateway.auth`、ツールポリシー、ルーティング）。
- **Node** はその Gateway とペアリングされたリモート実行面です（コマンド、デバイスアクション、ホストローカル機能）。
- Gateway に認証された呼び出し元は、Gateway スコープで信頼されます。ペアリング後、node アクションはその node 上での信頼されたオペレーターアクションになります。
- `sessionKey` はルーティング / コンテキスト選択であり、ユーザー単位の認証ではありません。
- Exec 承認（許可リスト + ask）はオペレーター意図のためのガードレールであり、敵対的マルチテナント分離ではありません。
- 信頼された単一オペレーター環境向けの OpenClaw の製品デフォルトでは、`gateway` / `node` 上のホスト exec は承認プロンプトなしで許可されます（より厳格にしない限り `security="full"`、`ask="off"`）。このデフォルトは意図的な UX であり、それ自体は脆弱性ではありません。
- Exec 承認は、正確なリクエストコンテキストと、ベストエフォートの直接ローカルファイルオペランドに結び付きます。すべてのランタイム / インタープリターのローダーパスを意味的にモデル化するものではありません。強い境界が必要なら、サンドボックス化とホスト分離を使用してください。

敵対的ユーザーの分離が必要な場合は、OS ユーザー / ホストごとに信頼境界を分離し、別々の Gateway を実行してください。

## 信頼境界マトリクス

リスクをトリアージする際のクイックモデルとしてこれを使用してください。

| 境界または制御 | 意味 | よくある誤解 |
| --- | --- | --- |
| `gateway.auth`（token/password/trusted-proxy/device auth） | Gateway API への呼び出し元を認証する | 「安全にするにはすべてのフレームでメッセージごとの署名が必要」 |
| `sessionKey` | コンテキスト / セッション選択のためのルーティングキー | 「Session key はユーザー認証境界だ」 |
| プロンプト / コンテンツのガードレール | モデル悪用リスクを低減する | 「プロンプトインジェクションだけで認証バイパスが証明される」 |
| `canvas.eval` / browser evaluate | 有効化された場合の意図的なオペレーター機能 | 「どんな JS eval プリミティブでも、この信頼モデルでは自動的に脆弱性になる」 |
| ローカル TUI の `!` シェル | 明示的にオペレーターがトリガーするローカル実行 | 「ローカルシェルの便利コマンドはリモートインジェクションだ」 |
| Node のペアリングと node コマンド | ペアリングされたデバイス上でのオペレーターレベルのリモート実行 | 「リモートデバイス制御はデフォルトで信頼されないユーザーアクセスとして扱うべきだ」 |

## 設計上、脆弱性ではないもの

以下のパターンはよく報告されますが、実際の境界バイパスが示されない限り、通常は no-action としてクローズされます。

- ポリシー / 認証 / サンドボックスのバイパスを伴わない、プロンプトインジェクションのみのチェーン。
- 1 つの共有ホスト / 設定上での敵対的マルチテナント運用を前提とした主張。
- 共有 Gateway 構成で、通常のオペレーター read-path アクセス（たとえば `sessions.list` / `sessions.preview` / `chat.history`）を IDOR と分類する主張。
- localhost 限定デプロイに関する指摘（たとえば loopback 限定 Gateway における HSTS）。
- このリポジトリに存在しない受信パスに対する、Discord 受信 webhook 署名の指摘。
- `system.run` に対する隠れた第 2 のコマンド単位承認レイヤーとして node pairing メタデータを扱う報告。ただし、実際の実行境界は依然として Gateway のグローバル node コマンドポリシーと node 自身の exec 承認です。
- `sessionKey` を認証トークンとして扱う「ユーザー単位認可の欠如」に関する指摘。

## 研究者向け事前チェックリスト

GHSA を開く前に、次のすべてを確認してください。

1. 再現が最新の `main` または最新リリースでも有効である。
2. 報告に正確なコードパス（`file`、関数、行範囲）とテストしたバージョン / コミットが含まれている。
3. 影響が文書化された信頼境界を越えている（単なるプロンプトインジェクションではない）。
4. 主張が [Out of Scope](https://github.com/openclaw/openclaw/blob/main/SECURITY.md#out-of-scope) に挙げられていない。
5. 既存のアドバイザリを重複確認した（該当する場合は正規の GHSA を再利用する）。
6. デプロイ前提（loopback / local か公開か、信頼されたオペレーターか信頼されていないオペレーターか）が明示されている。

## 60 秒でできる強化ベースライン

まずこのベースラインを使用し、その後、信頼されたエージェントごとに必要なツールだけを選択的に再有効化してください。

```json5
{
  gateway: {
    mode: "local",
    bind: "loopback",
    auth: { mode: "token", token: "replace-with-long-random-token" },
  },
  session: {
    dmScope: "per-channel-peer",
  },
  tools: {
    profile: "messaging",
    deny: ["group:automation", "group:runtime", "group:fs", "sessions_spawn", "sessions_send"],
    fs: { workspaceOnly: true },
    exec: { security: "deny", ask: "always" },
    elevated: { enabled: false },
  },
  channels: {
    whatsapp: { dmPolicy: "pairing", groups: { "*": { requireMention: true } } },
  },
}
```

これにより、Gateway は local-only に保たれ、DM は分離され、コントロールプレーン / ランタイムツールはデフォルトで無効になります。

## 共有受信箱のクイックルール

複数人があなたのボットに DM できる場合:

- `session.dmScope: "per-channel-peer"`（またはマルチアカウントチャネルなら `"per-account-channel-peer"`）を設定してください。
- `dmPolicy: "pairing"` または厳格な許可リストを維持してください。
- 共有 DM と広範なツールアクセスを決して組み合わせないでください。
- これは協調的 / 共有受信箱を強化しますが、ユーザーがホスト / 設定への書き込みアクセスを共有する場合の、敵対的コテナント分離を目的とした設計ではありません。

## コンテキスト可視性モデル

OpenClaw は 2 つの概念を分離しています。

- **トリガー認可**: 誰がエージェントをトリガーできるか（`dmPolicy`、`groupPolicy`、許可リスト、メンションゲート）。
- **コンテキスト可視性**: どの補足コンテキストがモデル入力に注入されるか（返信本文、引用テキスト、スレッド履歴、転送メタデータ）。

許可リストはトリガーとコマンド認可を制御します。`contextVisibility` 設定は、補足コンテキスト（引用返信、スレッドルート、取得された履歴）を、どのようにフィルタリングするかを制御します。

- `contextVisibility: "all"`（デフォルト）は、受信した補足コンテキストをそのまま保持します。
- `contextVisibility: "allowlist"` は、アクティブな許可リストチェックで許可された送信者に補足コンテキストをフィルタリングします。
- `contextVisibility: "allowlist_quote"` は `allowlist` と同様ですが、明示的な引用返信を 1 つだけ保持します。

`contextVisibility` はチャネルごと、またはルーム / 会話ごとに設定してください。設定の詳細は [グループチャット](/ja-JP/channels/groups#context-visibility-and-allowlists) を参照してください。

アドバイザリのトリアージ指針:

- 「モデルが、許可リストにない送信者からの引用や履歴テキストを見られる」ことだけを示す主張は、`contextVisibility` で対処可能な強化項目であり、それ自体では認証やサンドボックス境界のバイパスではありません。
- セキュリティ影響があると見なされるには、報告は依然として、実証された信頼境界バイパス（認証、ポリシー、サンドボックス、承認、またはその他の文書化された境界）を必要とします。

## 監査がチェックする内容（高レベル）

- **受信アクセス**（DM ポリシー、グループポリシー、許可リスト）: 見知らぬ相手がボットをトリガーできますか？
- **ツールの影響範囲**（権限の強いツール + オープンなルーム）: プロンプトインジェクションがシェル / ファイル / ネットワーク操作に発展する可能性がありますか？
- **Exec 承認のドリフト**（`security=full`、`autoAllowSkills`、`strictInlineEval` のないインタープリター許可リスト）: ホスト exec のガードレールは、今も意図したとおりに機能していますか？
  - `security="full"` は広範な姿勢に関する警告であり、バグの証明ではありません。これは信頼されたパーソナルアシスタント構成向けに選ばれたデフォルトです。脅威モデルで承認や許可リストのガードレールが必要な場合にのみ厳格化してください。
- **ネットワーク露出**（Gateway の bind/auth、Tailscale Serve/Funnel、弱い / 短い認証トークン）。
- **ブラウザ制御の露出**（リモート node、リレーポート、リモート CDP エンドポイント）。
- **ローカルディスクの衛生状態**（権限、symlink、設定 include、「同期フォルダー」パス）。
- **Plugin**（明示的な許可リストなしで拡張が存在する）。
- **ポリシードリフト / 誤設定**（sandbox docker 設定はあるが sandbox モードがオフ、`gateway.nodes.denyCommands` パターンが無効なのは一致が正確なコマンド名のみに対して行われ（たとえば `system.run`）、シェルテキストを検査しないため、危険な `gateway.nodes.allowCommands` エントリ、グローバルな `tools.profile="minimal"` がエージェントごとのプロファイルで上書きされる、拡張 Plugin ツールが緩いツールポリシー下で到達可能）。
- **ランタイム期待値のドリフト**（たとえば、`tools.exec.host` のデフォルトが `auto` になったのに、暗黙の exec が依然として `sandbox` を意味すると想定している、または sandbox モードがオフなのに明示的に `tools.exec.host="sandbox"` を設定している）。
- **モデル衛生**（設定されたモデルがレガシーに見える場合に警告。ハードブロックではありません）。

`--deep` で実行すると、OpenClaw はベストエフォートで live Gateway プローブも試みます。

## 認証情報ストレージマップ

アクセスを監査したり、何をバックアップするかを判断したりする際の参考にしてください。

- **WhatsApp**: `~/.openclaw/credentials/whatsapp/<accountId>/creds.json`
- **Telegram bot token**: config/env または `channels.telegram.tokenFile`（通常ファイルのみ。symlink は拒否）
- **Discord bot token**: config/env または SecretRef（env/file/exec プロバイダー）
- **Slack トークン**: config/env（`channels.slack.*`）
- **ペアリング許可リスト**:
  - `~/.openclaw/credentials/<channel>-allowFrom.json`（デフォルトアカウント）
  - `~/.openclaw/credentials/<channel>-<accountId>-allowFrom.json`（デフォルト以外のアカウント）
- **モデル認証プロファイル**: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- **ファイルベースのシークレットペイロード（任意）**: `~/.openclaw/secrets.json`
- **レガシー OAuth インポート**: `~/.openclaw/credentials/oauth.json`

## セキュリティ監査チェックリスト

監査で検出結果が表示されたら、次の優先順位で対処してください。

1. **「open」なもの + ツール有効**: まず DM / グループをロックダウンしてください（pairing / 許可リスト）。その後、ツールポリシー / sandbox 化を厳格化します。
2. **公開ネットワーク露出**（LAN bind、Funnel、認証なし）: 直ちに修正してください。
3. **ブラウザ制御のリモート露出**: オペレーターアクセスと同等に扱ってください（tailnet 限定、node は意図的にペアリングし、公開露出は避ける）。
4. **権限**: state / config / credentials / auth が group / world-readable でないことを確認してください。
5. **Plugin / 拡張**: 明示的に信頼するものだけをロードしてください。
6. **モデル選択**: ツールを持つボットには、最新の、命令耐性が強化されたモデルを優先してください。

## セキュリティ監査用語集

実運用環境で表示される可能性が高い、高シグナルの `checkId` 値（網羅的ではありません）:

| `checkId` | Severity | 重要な理由 | 主な修正キー / パス | 自動修正 |
| --- | --- | --- | --- | --- |
| `fs.state_dir.perms_world_writable` | critical | 他のユーザー / プロセスが OpenClaw の完全な state を変更できる | `~/.openclaw` のファイルシステム権限 | yes |
| `fs.state_dir.perms_group_writable` | warn | 同じ group のユーザーが OpenClaw の完全な state を変更できる | `~/.openclaw` のファイルシステム権限 | yes |
| `fs.state_dir.perms_readable` | warn | state ディレクトリを他者が読める | `~/.openclaw` のファイルシステム権限 | yes |
| `fs.state_dir.symlink` | warn | state ディレクトリのターゲットが別の信頼境界になる | state ディレクトリのファイルシステムレイアウト | no |
| `fs.config.perms_writable` | critical | 他者が認証 / ツールポリシー / 設定を変更できる | `~/.openclaw/openclaw.json` のファイルシステム権限 | yes |
| `fs.config.symlink` | warn | config のターゲットが別の信頼境界になる | config ファイルのファイルシステムレイアウト | no |
| `fs.config.perms_group_readable` | warn | 同じ group のユーザーが config のトークン / 設定を読める | config ファイルのファイルシステム権限 | yes |
| `fs.config.perms_world_readable` | critical | config からトークン / 設定が露出する可能性がある | config ファイルのファイルシステム権限 | yes |
| `fs.config_include.perms_writable` | critical | config include ファイルを他者が変更できる | `openclaw.json` から参照される include ファイルの権限 | yes |
| `fs.config_include.perms_group_readable` | warn | 同じ group のユーザーが include されたシークレット / 設定を読める | `openclaw.json` から参照される include ファイルの権限 | yes |
| `fs.config_include.perms_world_readable` | critical | include されたシークレット / 設定が world-readable になっている | `openclaw.json` から参照される include ファイルの権限 | yes |
| `fs.auth_profiles.perms_writable` | critical | 他者が保存されたモデル認証情報を注入または置き換えできる | `agents/<agentId>/agent/auth-profiles.json` の権限 | yes |
| `fs.auth_profiles.perms_readable` | warn | 他者が API キーや OAuth トークンを読める | `agents/<agentId>/agent/auth-profiles.json` の権限 | yes |
| `fs.credentials_dir.perms_writable` | critical | 他者がチャネルのペアリング / 認証情報 state を変更できる | `~/.openclaw/credentials` のファイルシステム権限 | yes |
| `fs.credentials_dir.perms_readable` | warn | 他者がチャネル認証情報の state を読める | `~/.openclaw/credentials` のファイルシステム権限 | yes |
| `fs.sessions_store.perms_readable` | warn | 他者がセッショントランスクリプト / メタデータを読める | セッションストアの権限 | yes |
| `fs.log_file.perms_readable` | warn | 他者が、秘匿化されていても依然として機微なログを読める | Gateway ログファイルの権限 | yes |
| `fs.synced_dir` | warn | iCloud / Dropbox / Drive 上の state / config により、トークン / トランスクリプト露出が広がる | config / state を同期フォルダーから移動する | no |
| `gateway.bind_no_auth` | critical | 共有シークレットなしでリモート bind している | `gateway.bind`、`gateway.auth.*` | no |
| `gateway.loopback_no_auth` | critical | リバースプロキシされた loopback が未認証になる可能性がある | `gateway.auth.*`、プロキシ設定 | no |
| `gateway.trusted_proxies_missing` | warn | リバースプロキシヘッダーは存在するが信頼されていない | `gateway.trustedProxies` | no |
| `gateway.http.no_auth` | warn/critical | `auth.mode="none"` で Gateway HTTP API に到達できる | `gateway.auth.mode`、`gateway.http.endpoints.*` | no |
| `gateway.http.session_key_override_enabled` | info | HTTP API 呼び出し元が `sessionKey` を上書きできる | `gateway.http.allowSessionKeyOverride` | no |
| `gateway.tools_invoke_http.dangerous_allow` | warn/critical | HTTP API 経由で危険なツールを再有効化する | `gateway.tools.allow` | no |
| `gateway.nodes.allow_commands_dangerous` | warn/critical | 影響の大きい node コマンド（camera/screen/contacts/calendar/SMS）を有効化する | `gateway.nodes.allowCommands` | no |
| `gateway.nodes.deny_commands_ineffective` | warn | パターン風の deny エントリがシェルテキストや group に一致しない | `gateway.nodes.denyCommands` | no |
| `gateway.tailscale_funnel` | critical | パブリックインターネットに露出する | `gateway.tailscale.mode` | no |
| `gateway.tailscale_serve` | info | Serve により tailnet への露出が有効になっている | `gateway.tailscale.mode` | no |
| `gateway.control_ui.allowed_origins_required` | critical | loopback 以外の Control UI に明示的なブラウザ origin 許可リストがない | `gateway.controlUi.allowedOrigins` | no |
| `gateway.control_ui.allowed_origins_wildcard` | warn/critical | `allowedOrigins=["*"]` によりブラウザ origin 許可リストが無効化される | `gateway.controlUi.allowedOrigins` | no |
| `gateway.control_ui.host_header_origin_fallback` | warn/critical | Host ヘッダー origin フォールバックを有効化している（DNS rebinding 強化の後退） | `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback` | no |
| `gateway.control_ui.insecure_auth` | warn | insecure-auth 互換トグルが有効になっている | `gateway.controlUi.allowInsecureAuth` | no |
| `gateway.control_ui.device_auth_disabled` | critical | デバイス ID チェックを無効化する | `gateway.controlUi.dangerouslyDisableDeviceAuth` | no |
| `gateway.real_ip_fallback_enabled` | warn/critical | `X-Real-IP` フォールバックを信頼すると、プロキシ誤設定経由で送信元 IP スプーフィングが可能になる場合がある | `gateway.allowRealIpFallback`、`gateway.trustedProxies` | no |
| `gateway.token_too_short` | warn | 短い共有トークンは総当たりしやすい | `gateway.auth.token` | no |
| `gateway.auth_no_rate_limit` | warn | レート制限のない公開認証は総当たりリスクを高める | `gateway.auth.rateLimit` | no |
| `gateway.trusted_proxy_auth` | critical | プロキシ ID が認証境界になる | `gateway.auth.mode="trusted-proxy"` | no |
| `gateway.trusted_proxy_no_proxies` | critical | 信頼済みプロキシ IP のない trusted-proxy 認証は安全ではない | `gateway.trustedProxies` | no |
| `gateway.trusted_proxy_no_user_header` | critical | trusted-proxy 認証がユーザー ID を安全に解決できない | `gateway.auth.trustedProxy.userHeader` | no |
| `gateway.trusted_proxy_no_allowlist` | warn | trusted-proxy 認証が認証済みの任意の上流ユーザーを受け入れる | `gateway.auth.trustedProxy.allowUsers` | no |
| `gateway.probe_auth_secretref_unavailable` | warn | Deep probe がこのコマンドパスで auth SecretRef を解決できなかった | deep-probe auth ソース / SecretRef の可用性 | no |
| `gateway.probe_failed` | warn/critical | live Gateway プローブに失敗した | gateway の到達可能性 / 認証 | no |
| `discovery.mdns_full_mode` | warn/critical | mDNS full モードがローカルネットワーク上で `cliPath` / `sshPort` メタデータを広告する | `discovery.mdns.mode`、`gateway.bind` | no |
| `config.insecure_or_dangerous_flags` | warn | 安全でない / 危険なデバッグフラグがいずれか有効になっている | 複数のキー（詳細は検出結果を参照） | no |
| `config.secrets.gateway_password_in_config` | warn | Gateway パスワードが config に直接保存されている | `gateway.auth.password` | no |
| `config.secrets.hooks_token_in_config` | warn | Hook bearer token が config に直接保存されている | `hooks.token` | no |
| `hooks.token_reuse_gateway_token` | critical | Hook の受信トークンが Gateway 認証の解除にも使える | `hooks.token`、`gateway.auth.token` | no |
| `hooks.token_too_short` | warn | Hook 受信に対する総当たりが容易になる | `hooks.token` | no |
| `hooks.default_session_key_unset` | warn | Hook エージェントの実行が、リクエストごとに生成されるセッションへファンアウトする | `hooks.defaultSessionKey` | no |
| `hooks.allowed_agent_ids_unrestricted` | warn/critical | 認証済みの Hook 呼び出し元が、設定済みの任意のエージェントにルーティングできる | `hooks.allowedAgentIds` | no |
| `hooks.request_session_key_enabled` | warn/critical | 外部呼び出し元が `sessionKey` を選択できる | `hooks.allowRequestSessionKey` | no |
| `hooks.request_session_key_prefixes_missing` | warn/critical | 外部セッションキーの形式に制限がない | `hooks.allowedSessionKeyPrefixes` | no |
| `hooks.path_root` | critical | Hook パスが `/` であり、受信が衝突または誤ルーティングしやすい | `hooks.path` | no |
| `hooks.installs_unpinned_npm_specs` | warn | Hook インストール記録が不変の npm spec に固定されていない | Hook インストールメタデータ | no |
| `hooks.installs_missing_integrity` | warn | Hook インストール記録に integrity メタデータがない | Hook インストールメタデータ | no |
| `hooks.installs_version_drift` | warn | Hook インストール記録がインストール済みパッケージとずれている | Hook インストールメタデータ | no |
| `logging.redact_off` | warn | 機密値がログ / status に漏れる | `logging.redactSensitive` | yes |
| `browser.control_invalid_config` | warn | ブラウザ制御の config が実行前の時点で無効 | `browser.*` | no |
| `browser.control_no_auth` | critical | トークン / パスワード認証なしでブラウザ制御が公開されている | `gateway.auth.*` | no |
| `browser.remote_cdp_http` | warn | プレーン HTTP 上のリモート CDP には転送時の暗号化がない | ブラウザプロファイルの `cdpUrl` | no |
| `browser.remote_cdp_private_host` | warn | リモート CDP が private / internal ホストを対象にしている | ブラウザプロファイルの `cdpUrl`、`browser.ssrfPolicy.*` | no |
| `sandbox.docker_config_mode_off` | warn | Sandbox Docker の config は存在するが非アクティブ | `agents.*.sandbox.mode` | no |
| `sandbox.bind_mount_non_absolute` | warn | 相対 bind mount は予測しにくい形で解決される可能性がある | `agents.*.sandbox.docker.binds[]` | no |
| `sandbox.dangerous_bind_mount` | critical | Sandbox の bind mount ターゲットが、ブロック対象のシステム、認証情報、または Docker socket パスになっている | `agents.*.sandbox.docker.binds[]` | no |
| `sandbox.dangerous_network_mode` | critical | Sandbox Docker ネットワークが `host` または `container:*` の namespace-join モードを使用している | `agents.*.sandbox.docker.network` | no |
| `sandbox.dangerous_seccomp_profile` | critical | Sandbox seccomp プロファイルがコンテナ分離を弱める | `agents.*.sandbox.docker.securityOpt` | no |
| `sandbox.dangerous_apparmor_profile` | critical | Sandbox AppArmor プロファイルがコンテナ分離を弱める | `agents.*.sandbox.docker.securityOpt` | no |
| `sandbox.browser_cdp_bridge_unrestricted` | warn | Sandbox のブラウザブリッジが送信元レンジ制限なしで公開されている | `sandbox.browser.cdpSourceRange` | no |
| `sandbox.browser_container.non_loopback_publish` | critical | 既存のブラウザコンテナが non-loopback インターフェース上に CDP を公開している | ブラウザ sandbox コンテナの publish 設定 | no |
| `sandbox.browser_container.hash_label_missing` | warn | 既存のブラウザコンテナが現在の config-hash ラベル導入前のもの | `openclaw sandbox recreate --browser --all` | no |
| `sandbox.browser_container.hash_epoch_stale` | warn | 既存のブラウザコンテナが現在のブラウザ config epoch より古い | `openclaw sandbox recreate --browser --all` | no |
| `tools.exec.host_sandbox_no_sandbox_defaults` | warn | `exec host=sandbox` は sandbox がオフのときクローズドフェイルする | `tools.exec.host`、`agents.defaults.sandbox.mode` | no |
| `tools.exec.host_sandbox_no_sandbox_agents` | warn | エージェントごとの `exec host=sandbox` は sandbox がオフのときクローズドフェイルする | `agents.list[].tools.exec.host`、`agents.list[].sandbox.mode` | no |
| `tools.exec.security_full_configured` | warn/critical | ホスト exec が `security="full"` で実行されている | `tools.exec.security`、`agents.list[].tools.exec.security` | no |
| `tools.exec.auto_allow_skills_enabled` | warn | Exec 承認が skill bin を暗黙的に信頼している | `~/.openclaw/exec-approvals.json` | no |
| `tools.exec.allowlist_interpreter_without_strict_inline_eval` | warn | インタープリター許可リストが、再承認を強制せずに inline eval を許可している | `tools.exec.strictInlineEval`、`agents.list[].tools.exec.strictInlineEval`、exec 承認許可リスト | no |
| `tools.exec.safe_bins_interpreter_unprofiled` | warn | `safeBins` 内のインタープリター / ランタイム bin に明示的プロファイルがなく、exec リスクが広がる | `tools.exec.safeBins`、`tools.exec.safeBinProfiles`、`agents.list[].tools.exec.*` | no |
| `tools.exec.safe_bins_broad_behavior` | warn | `safeBins` 内の広範な動作を持つツールが、低リスクな stdin-filter 信頼モデルを弱める | `tools.exec.safeBins`、`agents.list[].tools.exec.safeBins` | no |
| `tools.exec.safe_bin_trusted_dirs_risky` | warn | `safeBinTrustedDirs` に変更可能またはリスクの高いディレクトリが含まれている | `tools.exec.safeBinTrustedDirs`、`agents.list[].tools.exec.safeBinTrustedDirs` | no |
| `skills.workspace.symlink_escape` | warn | workspace の `skills/**/SKILL.md` が workspace ルート外を解決している（symlink-chain drift） | workspace `skills/**` のファイルシステム状態 | no |
| `plugins.extensions_no_allowlist` | warn | 拡張が明示的な Plugin 許可リストなしでインストールされている | `plugins.allowlist` | no |
| `plugins.installs_unpinned_npm_specs` | warn | Plugin インストール記録が不変の npm spec に固定されていない | Plugin インストールメタデータ | no |
| `plugins.installs_missing_integrity` | warn | Plugin インストール記録に integrity メタデータがない | Plugin インストールメタデータ | no |
| `plugins.installs_version_drift` | warn | Plugin インストール記録がインストール済みパッケージとずれている | Plugin インストールメタデータ | no |
| `plugins.code_safety` | warn/critical | Plugin コードスキャンで、不審または危険なパターンが見つかった | Plugin コード / インストール元 | no |
| `plugins.code_safety.entry_path` | warn | Plugin のエントリパスが hidden または `node_modules` の場所を指している | Plugin マニフェストの `entry` | no |
| `plugins.code_safety.entry_escape` | critical | Plugin エントリが Plugin ディレクトリ外に逸脱している | Plugin マニフェストの `entry` | no |
| `plugins.code_safety.scan_failed` | warn | Plugin コードスキャンを完了できなかった | Plugin 拡張パス / スキャン環境 | no |
| `skills.code_safety` | warn/critical | Skills インストーラーメタデータ / コードに、不審または危険なパターンが含まれている | skill インストール元 | no |
| `skills.code_safety.scan_failed` | warn | skill コードスキャンを完了できなかった | skill スキャン環境 | no |
| `security.exposure.open_channels_with_exec` | warn/critical | 共有 / 公開ルームから exec 有効エージェントに到達できる | `channels.*.dmPolicy`、`channels.*.groupPolicy`、`tools.exec.*`、`agents.list[].tools.exec.*` | no |
| `security.exposure.open_groups_with_elevated` | critical | オープングループ + 権限の強いツールにより、影響の大きいプロンプトインジェクション経路が生まれる | `channels.*.groupPolicy`、`tools.elevated.*` | no |
| `security.exposure.open_groups_with_runtime_or_fs` | critical/warn | オープングループから、sandbox / workspace ガードなしでコマンド / ファイルツールに到達できる | `channels.*.groupPolicy`、`tools.profile/deny`、`tools.fs.workspaceOnly`、`agents.*.sandbox.mode` | no |
| `security.trust_model.multi_user_heuristic` | warn | Gateway の信頼モデルはパーソナルアシスタントなのに、config がマルチユーザーに見える | 信頼境界を分離する、または共有ユーザー向け強化（`sandbox.mode`、tool deny / workspace スコープ） | no |
| `tools.profile_minimal_overridden` | warn | エージェント上書きによりグローバルな minimal プロファイルがバイパスされる | `agents.list[].tools.profile` | no |
| `plugins.tools_reachable_permissive_policy` | warn | 緩いポリシーのコンテキストで拡張ツールに到達できる | `tools.profile` + tool allow / deny | no |
| `models.legacy` | warn | レガシーモデルファミリーがまだ設定されている | モデル選択 | no |
| `models.weak_tier` | warn | 設定されたモデルが現在推奨されるティアを下回っている | モデル選択 | no |
| `models.small_params` | critical/info | 小規模モデル + 安全でないツール面により、インジェクションリスクが高まる | モデル選択 + sandbox / ツールポリシー | no |
| `summary.attack_surface` | info | 認証、チャネル、ツール、露出姿勢のロールアップ要約 | 複数のキー（詳細は検出結果を参照） | no |

## HTTP 経由の Control UI

Control UI がデバイス ID を生成するには、**セキュアコンテキスト**（HTTPS または localhost）が必要です。`gateway.controlUi.allowInsecureAuth` はローカル互換用のトグルです。

- localhost では、ページが非セキュアな HTTP 経由で読み込まれた場合でも、デバイス ID なしで Control UI 認証を許可します。
- これはペアリングチェックをバイパスしません。
- リモート（非 localhost）のデバイス ID 要件は緩和しません。

HTTPS（Tailscale Serve）を優先するか、`127.0.0.1` で UI を開いてください。

非常時専用として、`gateway.controlUi.dangerouslyDisableDeviceAuth` はデバイス ID チェックを完全に無効化します。これは重大なセキュリティ低下です。積極的にデバッグしていて、すぐに元へ戻せる場合を除き、オフのままにしてください。

これらの危険なフラグとは別に、`gateway.auth.mode: "trusted-proxy"` が成功すると、デバイス ID なしで**オペレーター** Control UI セッションを許可できます。これは意図された auth-mode の動作であり、`allowInsecureAuth` の近道ではありません。また、node-role の Control UI セッションには依然として適用されません。

`openclaw security audit` は、この設定が有効な場合に警告します。

## 安全でない / 危険なフラグの概要

`openclaw security audit` は、既知の安全でない / 危険なデバッグスイッチが有効な場合、`config.insecure_or_dangerous_flags` を含めます。このチェックは現在、以下を集約します。

- `gateway.controlUi.allowInsecureAuth=true`
- `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback=true`
- `gateway.controlUi.dangerouslyDisableDeviceAuth=true`
- `hooks.gmail.allowUnsafeExternalContent=true`
- `hooks.mappings[<index>].allowUnsafeExternalContent=true`
- `tools.exec.applyPatch.workspaceOnly=false`
- `plugins.entries.acpx.config.permissionMode=approve-all`

OpenClaw の config schema で定義されている完全な `dangerous*` / `dangerously*` config キー:

- `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback`
- `gateway.controlUi.dangerouslyDisableDeviceAuth`
- `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork`
- `channels.discord.dangerouslyAllowNameMatching`
- `channels.discord.accounts.<accountId>.dangerouslyAllowNameMatching`
- `channels.slack.dangerouslyAllowNameMatching`
- `channels.slack.accounts.<accountId>.dangerouslyAllowNameMatching`
- `channels.googlechat.dangerouslyAllowNameMatching`
- `channels.googlechat.accounts.<accountId>.dangerouslyAllowNameMatching`
- `channels.msteams.dangerouslyAllowNameMatching`
- `channels.synology-chat.dangerouslyAllowNameMatching`（拡張チャネル）
- `channels.synology-chat.accounts.<accountId>.dangerouslyAllowNameMatching`（拡張チャネル）
- `channels.synology-chat.dangerouslyAllowInheritedWebhookPath`（拡張チャネル）
- `channels.zalouser.dangerouslyAllowNameMatching`（拡張チャネル）
- `channels.zalouser.accounts.<accountId>.dangerouslyAllowNameMatching`（拡張チャネル）
- `channels.irc.dangerouslyAllowNameMatching`（拡張チャネル）
- `channels.irc.accounts.<accountId>.dangerouslyAllowNameMatching`（拡張チャネル）
- `channels.mattermost.dangerouslyAllowNameMatching`（拡張チャネル）
- `channels.mattermost.accounts.<accountId>.dangerouslyAllowNameMatching`（拡張チャネル）
- `channels.telegram.network.dangerouslyAllowPrivateNetwork`
- `channels.telegram.accounts.<accountId>.network.dangerouslyAllowPrivateNetwork`
- `agents.defaults.sandbox.docker.dangerouslyAllowReservedContainerTargets`
- `agents.defaults.sandbox.docker.dangerouslyAllowExternalBindSources`
- `agents.defaults.sandbox.docker.dangerouslyAllowContainerNamespaceJoin`
- `agents.list[<index>].sandbox.docker.dangerouslyAllowReservedContainerTargets`
- `agents.list[<index>].sandbox.docker.dangerouslyAllowExternalBindSources`
- `agents.list[<index>].sandbox.docker.dangerouslyAllowContainerNamespaceJoin`

## リバースプロキシ設定

Gateway をリバースプロキシ（nginx、Caddy、Traefik など）の背後で実行する場合は、転送されたクライアント IP を正しく扱うために `gateway.trustedProxies` を設定してください。

Gateway は、`trustedProxies` に**含まれていない**アドレスからのプロキシヘッダーを検出すると、その接続をローカルクライアントとして**扱いません**。Gateway 認証が無効な場合、それらの接続は拒否されます。これにより、プロキシ経由の接続が localhost から来たように見えて自動的に信頼されてしまう認証バイパスを防ぎます。

`gateway.trustedProxies` は `gateway.auth.mode: "trusted-proxy"` にも使われますが、この auth モードはより厳格です。

- trusted-proxy auth は**loopback 発信元プロキシに対してクローズドフェイル**します
- 同一ホスト上の loopback リバースプロキシは、ローカルクライアント検出と転送 IP 処理のために引き続き `gateway.trustedProxies` を使用できます
- 同一ホスト上の loopback リバースプロキシでは、`gateway.auth.mode: "trusted-proxy"` ではなく token/password auth を使用してください

```yaml
gateway:
  trustedProxies:
    - "10.0.0.1" # reverse proxy IP
  # 任意。デフォルトは false。
  # プロキシが X-Forwarded-For を提供できない場合のみ有効にしてください。
  allowRealIpFallback: false
  auth:
    mode: password
    password: ${OPENCLAW_GATEWAY_PASSWORD}
```

`trustedProxies` が設定されている場合、Gateway はクライアント IP の決定に `X-Forwarded-For` を使用します。`X-Real-IP` は、`gateway.allowRealIpFallback: true` が明示的に設定されない限り、デフォルトでは無視されます。

適切なリバースプロキシの動作（受信した転送ヘッダーを上書きする）:

```nginx
proxy_set_header X-Forwarded-For $remote_addr;
proxy_set_header X-Real-IP $remote_addr;
```

不適切なリバースプロキシの動作（信頼されていない転送ヘッダーを追加 / 保持する）:

```nginx
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
```

## HSTS と origin に関する注記

- OpenClaw Gateway は local / loopback 優先です。TLS 終端をリバースプロキシで行う場合は、プロキシの前にある HTTPS ドメイン側で HSTS を設定してください。
- Gateway 自身が HTTPS を終端する場合、`gateway.http.securityHeaders.strictTransportSecurity` を設定して、OpenClaw レスポンスから HSTS ヘッダーを送出できます。
- 詳細なデプロイガイダンスは [Trusted Proxy Auth](/ja-JP/gateway/trusted-proxy-auth#tls-termination-and-hsts) にあります。
- loopback 以外の Control UI デプロイでは、デフォルトで `gateway.controlUi.allowedOrigins` が必要です。
- `gateway.controlUi.allowedOrigins: ["*"]` は、明示的な allow-all のブラウザ origin ポリシーであり、強化されたデフォルトではありません。厳密に管理されたローカルテスト以外では避けてください。
- loopback 上のブラウザ origin 認証失敗も、一般的な loopback 免除が有効な場合でもレート制限されますが、ロックアウトキーは 1 つの共有 localhost バケットではなく、正規化された `Origin` 値ごとにスコープされます。
- `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback=true` は Host ヘッダー origin フォールバックモードを有効にします。危険な、オペレーター選択型ポリシーとして扱ってください。
- DNS rebinding とプロキシ Host ヘッダーの挙動は、デプロイ強化の懸念事項として扱ってください。`trustedProxies` は厳密に保ち、Gateway をパブリックインターネットへ直接公開しないでください。

## ローカルセッションログはディスク上に保存される

OpenClaw はセッショントランスクリプトを `~/.openclaw/agents/<agentId>/sessions/*.jsonl` の下にディスク保存します。
これはセッション継続性と（任意で）セッションメモリーのインデックス化のために必要ですが、同時に
**ファイルシステムアクセスを持つ任意のプロセス / ユーザーがそれらのログを読める**ことも意味します。ディスクアクセスを信頼
境界として扱い、`~/.openclaw` の権限を厳格化してください（以下の監査セクションを参照）。エージェント間で
より強い分離が必要な場合は、別々の OS ユーザーまたは別々のホストで実行してください。

## Node 実行（`system.run`）

macOS node がペアリングされている場合、Gateway はその node 上で `system.run` を呼び出せます。これは Mac 上での**リモートコード実行**です。

- node のペアリング（承認 + トークン）が必要です。
- Gateway の node ペアリングは、コマンド単位の承認面ではありません。これは node の ID / 信頼とトークン発行を確立します。
- Gateway は `gateway.nodes.allowCommands` / `denyCommands` を介して、粗い粒度のグローバル node コマンドポリシーを適用します。
- Mac 側では **Settings → Exec approvals** で制御します（security + ask + allowlist）。
- node ごとの `system.run` ポリシーは、その node 自身の exec 承認ファイル（`exec.approvals.node.*`）であり、Gateway のグローバルなコマンド ID ポリシーより厳格な場合も緩い場合もあります。
- `security="full"` かつ `ask="off"` で動作する node は、デフォルトの信頼されたオペレーターモデルに従っています。デプロイで明示的により厳しい承認または許可リスト方針が必要でない限り、これは想定どおりの動作として扱ってください。
- 承認モードは、正確なリクエストコンテキストと、可能であれば 1 つの具体的なローカルスクリプト / ファイルオペランドに結び付きます。OpenClaw がインタープリター / ランタイムコマンドに対して、ちょうど 1 つの直接ローカルファイルを正確に識別できない場合、承認ベースの実行は、完全な意味的カバレッジを約束するのではなく拒否されます。
- `host=node` の場合、承認ベースの実行では、正規化された準備済み `systemRunPlan` も保存されます。後から承認された転送では、その保存済みプランが再利用され、承認リクエスト作成後のコマンド / cwd / セッションコンテキストに対する呼び出し元の編集は Gateway 検証で拒否されます。
- リモート実行を望まない場合は、security を **deny** に設定し、その Mac の node ペアリングを削除してください。

この区別はトリアージで重要です。

- 再接続したペアリング済み node が別のコマンドリストを広告していても、それ自体は脆弱性ではありません。実際の実行境界を Gateway のグローバルポリシーと node のローカル exec 承認が引き続き強制している限り問題ありません。
- node pairing メタデータを隠れた第 2 のコマンド単位承認レイヤーとして扱う報告は、通常はポリシー / UX の混同であり、セキュリティ境界バイパスではありません。

## Dynamic Skills（watcher / remote nodes）

OpenClaw はセッション途中で Skills リストを更新できます。

- **Skills watcher**: `SKILL.md` の変更により、次のエージェントターンで Skills スナップショットが更新されることがあります。
- **Remote nodes**: macOS node を接続すると、macOS 専用 Skills が対象になることがあります（bin プローブに基づく）。

Skill フォルダーは**信頼されたコード**として扱い、変更できる相手を制限してください。

## 脅威モデル

AI アシスタントは以下を実行できます。

- 任意のシェルコマンドを実行する
- ファイルを読み書きする
- ネットワークサービスにアクセスする
- 誰にでもメッセージを送る（WhatsApp アクセスを与えた場合）

あなたにメッセージする相手は以下を試みる可能性があります。

- AI をだまして有害なことをさせる
- あなたのデータへのアクセスをソーシャルエンジニアリングする
- インフラの詳細を探る

## 中核概念: 知能より前にアクセス制御

ここでの失敗の大半は巧妙な攻撃ではなく、「誰かがボットにメッセージし、ボットがその依頼どおりに動いた」というものです。

OpenClaw の考え方:

- **まず ID:** 誰がボットと対話できるかを決める（DM pairing / 許可リスト / 明示的な `open`）。
- **次にスコープ:** ボットがどこで行動できるかを決める（グループ許可リスト + メンションゲート、ツール、sandbox 化、デバイス権限）。
- **最後にモデル:** モデルは操作されうる前提に立ち、その操作による影響範囲が限定されるように設計する。

## コマンド認可モデル

スラッシュコマンドとディレクティブは、**認可された送信者**に対してのみ受け付けられます。認可は、
チャネルの許可リスト / pairing と `commands.useAccessGroups` から導出されます（[Configuration](/ja-JP/gateway/configuration)
および [Slash commands](/ja-JP/tools/slash-commands) を参照）。チャネル許可リストが空、または `"*"` を含む場合、
そのチャネルのコマンドは実質的にオープンになります。

`/exec` は、認可されたオペレーター向けのセッション限定の便宜機能です。これは config に書き込んだり、
他のセッションを変更したりはしません。

## コントロールプレーンツールのリスク

2 つの組み込みツールは、永続的なコントロールプレーン変更を行う可能性があります。

- `gateway` は `config.schema.lookup` / `config.get` で config を検査でき、`config.apply`、`config.patch`、`update.run` で永続的変更を加えることができます。
- `cron` は、元の chat / task が終了した後も動き続けるスケジュールジョブを作成できます。

owner-only の `gateway` ランタイムツールは、依然として
`tools.exec.ask` または `tools.exec.security` の書き換えを拒否します。レガシーの `tools.bash.*` エイリアスは、
書き込み前に同じ保護された exec パスへ正規化されます。

信頼されていないコンテンツを扱うエージェント / サーフェスでは、デフォルトでこれらを deny してください。

```json5
{
  tools: {
    deny: ["gateway", "cron", "sessions_spawn", "sessions_send"],
  },
}
```

`commands.restart=false` は restart アクションだけをブロックします。`gateway` の config / update アクションは無効化しません。

## Plugins / 拡張

Plugins は Gateway と**同一プロセス内**で実行されます。信頼されたコードとして扱ってください。

- 信頼できるソースからのみ Plugin をインストールしてください。
- 明示的な `plugins.allow` 許可リストを優先してください。
- 有効化する前に Plugin の config を確認してください。
- Plugin を変更したら Gateway を再起動してください。
- Plugin をインストールまたは更新する場合（`openclaw plugins install <package>`、`openclaw plugins update <id>`）、信頼されていないコードを実行するのと同じように扱ってください。
  - インストールパスは、アクティブな Plugin インストールルート配下にある Plugin ごとのディレクトリです。
  - OpenClaw はインストール / 更新前に組み込みの危険コードスキャンを実行します。`critical` の検出結果はデフォルトでブロックされます。
  - OpenClaw は `npm pack` を使用し、その後そのディレクトリ内で `npm install --omit=dev` を実行します（npm lifecycle script はインストール中にコードを実行できます）。
  - 固定された厳密なバージョン（`@scope/pkg@1.2.3`）を優先し、有効化する前に展開されたコードをディスク上で確認してください。
  - `--dangerously-force-unsafe-install` は、Plugin のインストール / 更新フローにおける組み込みスキャンの誤検知に対する非常時専用です。これは Plugin の `before_install` hook ポリシーブロックも、スキャン失敗もバイパスしません。
  - Gateway を介した skill 依存関係インストールも、同じ危険 / 不審の区分に従います。組み込みの `critical` 検出結果は、呼び出し元が明示的に `dangerouslyForceUnsafeInstall` を設定しない限りブロックされ、不審な検出結果は引き続き警告のみです。`openclaw skills install` は、別個の ClawHub skill ダウンロード / インストールフローのままです。

詳細: [Plugins](/ja-JP/tools/plugin)

<a id="dm-access-model-pairing-allowlist-open-disabled"></a>

## DM アクセスモデル（pairing / allowlist / open / disabled）

現在 DM に対応しているすべてのチャネルは、メッセージが処理される**前に**受信 DM を制御する DM ポリシー（`dmPolicy` または `*.dm.policy`）をサポートしています。

- `pairing`（デフォルト）: 未知の送信者には短いペアリングコードが送られ、承認されるまでボットはそのメッセージを無視します。コードは 1 時間で期限切れになり、新しいリクエストが作成されるまで、繰り返しの DM でコードは再送されません。保留中リクエストはデフォルトで**チャネルごとに 3 件**までです。
- `allowlist`: 未知の送信者はブロックされます（ペアリングハンドシェイクなし）。
- `open`: 誰でも DM できるようにします（公開）。**チャネル許可リストに `"*"` を含める必要があります**（明示的な opt-in）。
- `disabled`: 受信 DM を完全に無視します。

CLI で承認します。

```bash
openclaw pairing list <channel>
openclaw pairing approve <channel> <code>
```

詳細とディスク上のファイル: [Pairing](/ja-JP/channels/pairing)

## DM セッション分離（マルチユーザーモード）

デフォルトでは、OpenClaw は**すべての DM を main セッションにルーティング**するため、アシスタントはデバイスやチャネルをまたいで継続性を維持できます。**複数人**がボットに DM できる場合（オープン DM または複数人の許可リスト）、DM セッションの分離を検討してください。

```json5
{
  session: { dmScope: "per-channel-peer" },
}
```

これにより、グループチャットを分離したまま、ユーザー間のコンテキスト漏えいを防げます。

これはメッセージングコンテキストの境界であり、ホスト管理者の境界ではありません。ユーザー同士が敵対的で、同じ Gateway ホスト / config を共有する場合は、信頼境界ごとに別々の Gateway を実行してください。

### セキュア DM モード（推奨）

上のスニペットを**セキュア DM モード**として扱ってください。

- デフォルト: `session.dmScope: "main"`（すべての DM が 1 つのセッションを共有し、継続性を保つ）
- ローカル CLI オンボーディングのデフォルト: 未設定時に `session.dmScope: "per-channel-peer"` を書き込みます（既存の明示値は維持）
- セキュア DM モード: `session.dmScope: "per-channel-peer"`（各チャネル + 送信者ペアごとに分離された DM コンテキスト）
- チャネル横断の peer 分離: `session.dmScope: "per-peer"`（同じ種類の全チャネルをまたいで、送信者ごとに 1 セッション）

同じチャネル上で複数アカウントを運用する場合は、代わりに `per-account-channel-peer` を使用してください。同じ人物が複数チャネルから連絡してくる場合は、`session.identityLinks` を使ってそれらの DM セッションを 1 つの正規 ID に統合してください。詳細は [Session Management](/ja-JP/concepts/session) と [Configuration](/ja-JP/gateway/configuration) を参照してください。

## 許可リスト（DM + groups）- 用語

OpenClaw には、「誰が自分をトリガーできるか」に関する 2 つの別個のレイヤーがあります。

- **DM 許可リスト**（`allowFrom` / `channels.discord.allowFrom` / `channels.slack.allowFrom`; レガシー: `channels.discord.dm.allowFrom`, `channels.slack.dm.allowFrom`）: ダイレクトメッセージでボットと対話できる相手。
  - `dmPolicy="pairing"` の場合、承認は `~/.openclaw/credentials/` 配下のアカウントスコープ付きペアリング許可リストストア（デフォルトアカウントは `<channel>-allowFrom.json`、デフォルト以外のアカウントは `<channel>-<accountId>-allowFrom.json`）に書き込まれ、config の許可リストとマージされます。
- **グループ許可リスト**（チャネル固有）: どのグループ / チャネル / guild からボットがそもそもメッセージを受け入れるか。
  - 一般的なパターン:
    - `channels.whatsapp.groups`, `channels.telegram.groups`, `channels.imessage.groups`: `requireMention` のようなグループごとのデフォルト。設定されている場合、グループ許可リストとしても機能します（全許可を維持するには `"*"` を含めます）。
    - `groupPolicy="allowlist"` + `groupAllowFrom`: グループセッション**内**で誰がボットをトリガーできるかを制限します（WhatsApp/Telegram/Signal/iMessage/Microsoft Teams）。
    - `channels.discord.guilds` / `channels.slack.channels`: サーフェスごとの許可リスト + メンションのデフォルト。
  - グループチェックは次の順に実行されます。最初に `groupPolicy` / グループ許可リスト、次にメンション / 返信アクティベーション。
  - ボットメッセージへの返信（暗黙的メンション）であっても、`groupAllowFrom` のような送信者許可リストはバイパスされません。
  - **セキュリティ注記:** `dmPolicy="open"` と `groupPolicy="open"` は最後の手段として扱ってください。これらはほとんど使うべきではありません。ルームの全メンバーを完全に信頼している場合を除き、pairing + 許可リストを優先してください。

詳細: [Configuration](/ja-JP/gateway/configuration) および [Groups](/ja-JP/channels/groups)

## プロンプトインジェクション（それが何で、なぜ重要か）

プロンプトインジェクションとは、攻撃者がモデルを操作して危険なことをさせるメッセージを作ることです（「指示を無視しろ」「ファイルシステムを吐き出せ」「このリンクを開いてコマンドを実行しろ」など）。

強力なシステムプロンプトがあっても、**プロンプトインジェクションは解決済みではありません**。システムプロンプトのガードレールはあくまでソフトなガイダンスであり、ハードな強制はツールポリシー、exec 承認、sandbox 化、チャネル許可リストによって行われます（そしてオペレーターは設計上これらを無効化できます）。実際に有効なのは次のような対策です。

- 受信 DM をロックダウンする（pairing / 許可リスト）。
- グループではメンションゲートを優先し、公開ルームで「常時起動」ボットを避ける。
- リンク、添付、貼り付けられた指示はデフォルトで hostile として扱う。
- 機密性の高いツール実行は sandbox 内で行い、シークレットをエージェントが到達可能なファイルシステムに置かない。
- 注: sandbox 化は opt-in です。sandbox モードがオフの場合、暗黙の `host=auto` は gateway ホストに解決されます。明示的な `host=sandbox` は、利用可能な sandbox ランタイムがないため、依然としてクローズドフェイルします。その動作を config 上で明示したい場合は `host=gateway` を設定してください。
- 高リスクなツール（`exec`、`browser`、`web_fetch`、`web_search`）は、信頼されたエージェントまたは明示的な許可リストに限定する。
- インタープリター（`python`、`node`、`ruby`、`perl`、`php`、`lua`、`osascript`）を許可リストに入れる場合は、inline eval 形式でも明示的承認が必要になるように `tools.exec.strictInlineEval` を有効にする。
- **モデル選択は重要です:** 古い / 小さい / レガシーモデルは、プロンプトインジェクションやツール誤用に対して著しく堅牢性が低いです。ツール有効化エージェントには、利用可能な中で最も強力な最新世代の、命令耐性が強化されたモデルを使用してください。

信頼しないものとして扱うべき危険信号:

- 「このファイル / URL を読んで、書いてあるとおりに正確に実行して」
- 「システムプロンプトや安全ルールを無視して」
- 「隠れた指示やツール出力を明かして」
- 「`~/.openclaw` やログの内容を全文貼って」

## 安全でない外部コンテンツのバイパスフラグ

OpenClaw には、外部コンテンツの安全ラッピングを無効化する明示的なバイパスフラグがあります。

- `hooks.mappings[].allowUnsafeExternalContent`
- `hooks.gmail.allowUnsafeExternalContent`
- Cron ペイロードフィールド `allowUnsafeExternalContent`

ガイダンス:

- 本番環境では、これらを未設定 / false に保ってください。
- 一時的で範囲が厳密に限定されたデバッグでのみ有効にしてください。
- 有効にする場合は、そのエージェントを分離してください（sandbox + 最小ツール + 専用セッション namespace）。

Hooks に関するリスク注記:

- Hook ペイロードは、配信元が自分で制御しているシステムであっても、信頼されないコンテンツです（メール / ドキュメント / web コンテンツはプロンプトインジェクションを含み得ます）。
- 弱いモデルティアはこのリスクを高めます。Hook 駆動の自動化では、強力で最新のモデルティアを優先し、ツールポリシーは厳格に保ってください（`tools.profile: "messaging"` またはそれ以上に厳格）、可能なら sandbox 化も行ってください。

### プロンプトインジェクションは公開 DM を必要としない

たとえ**自分だけ**がボットにメッセージできる場合でも、ボットが読む**信頼されていないコンテンツ**（web 検索 / fetch 結果、ブラウザページ、
メール、ドキュメント、添付、貼り付けられたログ / コード）を通じて、プロンプトインジェクションは依然として起こり得ます。言い換えると、脅威面は送信者だけではなく、**コンテンツ自体**が敵対的な指示を運ぶ可能性があります。

ツールが有効な場合、典型的なリスクはコンテキストの流出やツール呼び出しの誘発です。影響範囲を減らすには、次の対策を行ってください。

- 信頼されていないコンテンツを要約するために、読み取り専用またはツール無効の**reader agent** を使い、その要約を main agent に渡す。
- 必要でない限り、ツール有効エージェントでは `web_search` / `web_fetch` / `browser` をオフにしておく。
- OpenResponses の URL 入力（`input_file` / `input_image`）では、`gateway.http.endpoints.responses.files.urlAllowlist` と
  `gateway.http.endpoints.responses.images.urlAllowlist` を厳格に設定し、`maxUrlParts` は低く保ってください。
  空の許可リストは未設定として扱われます。URL フェッチを完全に無効化したい場合は、`files.allowUrl: false` / `images.allowUrl: false`
  を使用してください。
- OpenResponses のファイル入力では、デコードされた `input_file` テキストも引き続き
  **信頼されていない外部コンテンツ**として注入されます。Gateway がそれをローカルでデコードしたからといって、
  ファイルテキストが信頼できると考えないでください。注入されるブロックには依然として、明示的な
  `<<<EXTERNAL_UNTRUSTED_CONTENT ...>>>` 境界マーカーと `Source: External`
  メタデータが付与されます。ただし、この経路では長い `SECURITY NOTICE:` バナーは省略されます。
- 同じマーカーベースのラッピングは、media-understanding が添付ドキュメントからテキストを抽出して、そのテキストを media prompt に追加する場合にも適用されます。
- 信頼されていない入力に触れるエージェントでは、sandbox 化と厳格なツール許可リストを有効にする。
- シークレットをプロンプトに入れず、gateway ホスト上の env / config 経由で渡す。

### モデルの強さ（セキュリティ注記）

プロンプトインジェクションへの耐性は、モデルティア間で**一様ではありません**。一般に、小型 / 低価格のモデルほど、特に敵対的プロンプト下では、ツール誤用や指示ハイジャックに対して脆弱です。

<Warning>
ツール有効化エージェントや、信頼されていないコンテンツを読むエージェントでは、古い / 小さいモデルにおけるプロンプトインジェクションリスクはしばしば高すぎます。そのようなワークロードを弱いモデルティアで実行しないでください。
</Warning>

推奨事項:

- ツールを実行できる、またはファイル / ネットワークに触れられるボットには、**最新世代の最上位モデル**を使用してください。
- ツール有効化エージェントや信頼されていない受信箱には、**古い / 弱い / 小さいティアを使わないでください**。プロンプトインジェクションリスクが高すぎます。
- 小さいモデルを使わざるを得ない場合は、**影響範囲を縮小**してください（読み取り専用ツール、強力な sandbox 化、最小限のファイルシステムアクセス、厳格な許可リスト）。
- 小規模モデルを実行する場合は、**すべてのセッションで sandbox 化を有効にし**、入力が厳密に制御されていない限り **web_search / web_fetch / browser を無効化**してください。
- 信頼された入力のみでツールを使わない chat-only のパーソナルアシスタントであれば、小さいモデルでも通常は問題ありません。

<a id="reasoning-verbose-output-in-groups"></a>

## グループでの reasoning と verbose 出力

`/reasoning`、`/verbose`、`/trace` は、本来パブリックチャネル向けではない内部 reasoning、ツール
出力、または Plugin 診断情報を露出する可能性があります。グループ設定では、これらを**デバッグ専用**
として扱い、明示的に必要な場合を除いてオフにしてください。

ガイダンス:

- パブリックルームでは `/reasoning`、`/verbose`、`/trace` を無効のままにしてください。
- 有効にする場合は、信頼された DM または厳密に制御されたルームでのみ行ってください。
- 忘れないでください: verbose と trace 出力には、ツール引数、URL、Plugin 診断、モデルが見たデータが含まれることがあります。

## 設定の強化（例）

### 0) ファイル権限

Gateway ホスト上では config + state を非公開に保ってください。

- `~/.openclaw/openclaw.json`: `600`（ユーザーのみ読み書き）
- `~/.openclaw`: `700`（ユーザーのみ）

`openclaw doctor` はこれらの権限について警告し、厳格化を提案できます。

### 0.4) ネットワーク露出（bind + port + firewall）

Gateway は **WebSocket + HTTP** を単一ポートで多重化します。

- デフォルト: `18789`
- Config / flags / env: `gateway.port`、`--port`、`OPENCLAW_GATEWAY_PORT`

この HTTP サーフェスには Control UI と canvas host が含まれます。

- Control UI（SPA アセット）（デフォルトのベースパス `/`）
- Canvas host: `/__openclaw__/canvas/` および `/__openclaw__/a2ui/`（任意の HTML / JS。信頼されないコンテンツとして扱ってください）

通常のブラウザで canvas コンテンツを読み込む場合は、他の信頼されていない web ページと同じように扱ってください。

- canvas host を信頼されていないネットワーク / ユーザーに公開しないでください。
- 影響を十分理解していない限り、canvas コンテンツを権限のある web サーフェスと同じ origin にしないでください。

bind モードは Gateway がどこで待ち受けるかを制御します。

- `gateway.bind: "loopback"`（デフォルト）: ローカルクライアントのみ接続できます。
- loopback 以外の bind（`"lan"`、`"tailnet"`、`"custom"`）は攻撃面を広げます。これらを使うのは、gateway auth（共有 token / password または正しく設定された非 loopback trusted proxy）と、実際の firewall がある場合だけにしてください。

経験則:

- LAN bind より Tailscale Serve を優先してください（Serve では Gateway を loopback に保ったまま、Tailscale がアクセスを処理します）。
- どうしても LAN に bind する必要がある場合は、そのポートを送信元 IP の厳格な許可リストで firewall 制御してください。広くポートフォワードしないでください。
- 認証なしの Gateway を `0.0.0.0` で公開してはいけません。

### 0.4.1) Docker のポート公開 + UFW（`DOCKER-USER`）

VPS 上で Docker を使って OpenClaw を実行する場合、公開されたコンテナポート
（`-p HOST:CONTAINER` または Compose の `ports:`）は、ホストの `INPUT` ルールだけでなく
Docker の転送チェーンを経由してルーティングされることを忘れないでください。

Docker トラフィックを firewall ポリシーと整合させるには、
`DOCKER-USER` でルールを強制してください（このチェーンは Docker 自身の accept ルールより前に評価されます）。
多くの最近のディストリビューションでは、`iptables` / `ip6tables` は `iptables-nft` フロントエンドを使っており、
それでもこれらのルールは nftables バックエンドに適用されます。

最小限の許可リスト例（IPv4）:

```bash
# /etc/ufw/after.rules（独立した *filter セクションとして追記）
*filter
:DOCKER-USER - [0:0]
-A DOCKER-USER -m conntrack --ctstate ESTABLISHED,RELATED -j RETURN
-A DOCKER-USER -s 127.0.0.0/8 -j RETURN
-A DOCKER-USER -s 10.0.0.0/8 -j RETURN
-A DOCKER-USER -s 172.16.0.0/12 -j RETURN
-A DOCKER-USER -s 192.168.0.0/16 -j RETURN
-A DOCKER-USER -s 100.64.0.0/10 -j RETURN
-A DOCKER-USER -p tcp --dport 80 -j RETURN
-A DOCKER-USER -p tcp --dport 443 -j RETURN
-A DOCKER-USER -m conntrack --ctstate NEW -j DROP
-A DOCKER-USER -j RETURN
COMMIT
```

IPv6 には別のテーブルがあります。Docker IPv6 が有効なら、
`/etc/ufw/after6.rules` に対応するポリシーも追加してください。

ドキュメントのスニペットで `eth0` のようなインターフェース名をハードコードしないでください。インターフェース名は
VPS イメージごとに異なります（`ens3`、`enp*` など）。不一致があると、deny ルールが意図せず
スキップされることがあります。

リロード後の簡易検証:

```bash
ufw reload
iptables -S DOCKER-USER
ip6tables -S DOCKER-USER
nmap -sT -p 1-65535 <public-ip> --open
```

外部から見える想定ポートは、意図的に公開したものだけであるべきです（ほとんどの
構成では SSH + リバースプロキシのポート）。

### 0.4.2) mDNS / Bonjour ディスカバリー（情報漏えい）

Gateway はローカルデバイスディスカバリーのために、mDNS（5353 番ポートの `_openclaw-gw._tcp`）で自身の存在をブロードキャストします。full モードでは、運用上の詳細を露出しうる TXT レコードが含まれます。

- `cliPath`: CLI バイナリへの完全なファイルシステムパス（ユーザー名とインストール場所が分かる）
- `sshPort`: ホスト上の SSH 利用可能性を広告する
- `displayName`、`lanHost`: ホスト名情報

**運用セキュリティ上の考慮:** インフラの詳細をブロードキャストすると、ローカルネットワーク上の誰にとっても偵察が容易になります。「無害」に見えるファイルシステムパスや SSH 利用可否の情報でも、攻撃者による環境把握に役立ちます。

**推奨事項:**

1. **minimal モード**（デフォルト、公開される Gateway に推奨）: mDNS ブロードキャストから機微なフィールドを省きます。

   ```json5
   {
     discovery: {
       mdns: { mode: "minimal" },
     },
   }
   ```

2. ローカルデバイスディスカバリーが不要なら、**完全に無効化**してください。

   ```json5
   {
     discovery: {
       mdns: { mode: "off" },
     },
   }
   ```

3. **full モード**（opt-in）: TXT レコードに `cliPath` + `sshPort` を含めます。

   ```json5
   {
     discovery: {
       mdns: { mode: "full" },
     },
   }
   ```

4. **環境変数**（代替手段）: config を変更せずに mDNS を無効化するには、`OPENCLAW_DISABLE_BONJOUR=1` を設定してください。

minimal モードでは、Gateway は引き続きデバイスディスカバリーに十分な情報（`role`、`gatewayPort`、`transport`）をブロードキャストしますが、`cliPath` と `sshPort` は省略します。CLI パス情報が必要なアプリは、代わりに認証済み WebSocket 接続経由で取得できます。

### 0.5) Gateway WebSocket をロックダウンする（ローカル認証）

Gateway 認証はデフォルトで**必須**です。有効な gateway auth パスが設定されていない場合、
Gateway は WebSocket 接続を拒否します（fail-closed）。

オンボーディングでは、デフォルトで token が生成されるため（loopback であっても）、
ローカルクライアントも認証が必要です。

**すべての** WS クライアントに認証を要求するには token を設定してください。

```json5
{
  gateway: {
    auth: { mode: "token", token: "your-token" },
  },
}
```

Doctor は token を生成できます: `openclaw doctor --generate-gateway-token`。

注: `gateway.remote.token` / `.password` はクライアント認証情報ソースです。
それ自体ではローカル WS アクセスを保護しません。
ローカル呼び出しパスは、`gateway.auth.*` が未設定のときにのみ `gateway.remote.*` をフォールバックとして使用できます。
`gateway.auth.token` / `gateway.auth.password` が SecretRef 経由で明示的に設定され、未解決の場合、
解決はクローズドフェイルします（remote フォールバックで隠されることはありません）。
任意: `wss://` を使用する場合は `gateway.remote.tlsFingerprint` で remote TLS をピン留めできます。
平文の `ws://` はデフォルトで loopback-only です。信頼できる private-network
パスでは、非常時対応としてクライアントプロセス上で `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1` を設定してください。

ローカルデバイスペアリング:

- 同一ホスト上のクライアントを円滑にするため、直接のローカル loopback 接続に対するデバイスペアリングは自動承認されます。
- OpenClaw には、信頼された共有シークレットヘルパーフロー向けの、狭く限定された backend / container-local self-connect パスもあります。
- Tailnet および LAN 接続は、同一ホストの tailnet bind を含めて remote として扱われるため、依然として承認が必要です。

認証モード:

- `gateway.auth.mode: "token"`: 共有 bearer token（ほとんどの構成に推奨）。
- `gateway.auth.mode: "password"`: パスワード認証（env 経由の設定推奨: `OPENCLAW_GATEWAY_PASSWORD`）。
- `gateway.auth.mode: "trusted-proxy"`: ID 対応のリバースプロキシがユーザーを認証し、ヘッダー経由で ID を渡すことを信頼します（[Trusted Proxy Auth](/ja-JP/gateway/trusted-proxy-auth) を参照）。

ローテーションチェックリスト（token / password）:

1. 新しいシークレットを生成 / 設定する（`gateway.auth.token` または `OPENCLAW_GATEWAY_PASSWORD`）。
2. Gateway を再起動する（または macOS app が Gateway を監視しているならその app を再起動する）。
3. remote クライアントを更新する（Gateway を呼び出すマシンの `gateway.remote.token` / `.password`）。
4. 古い認証情報では接続できなくなったことを確認する。

### 0.6) Tailscale Serve の ID ヘッダー

`gateway.auth.allowTailscale` が `true`（Serve のデフォルト）である場合、OpenClaw は
Control UI / WebSocket 認証のために Tailscale Serve の ID ヘッダー（`tailscale-user-login`）を受け入れます。OpenClaw は、
`x-forwarded-for` アドレスをローカル Tailscale デーモン（`tailscale whois`）経由で解決し、
それをヘッダーと照合することで ID を検証します。これは、loopback に到達し、かつ
Tailscale によって注入された `x-forwarded-for`、`x-forwarded-proto`、`x-forwarded-host` を含むリクエストに対してのみ発動します。
この非同期 ID チェック経路では、同じ `{scope, ip}` に対する失敗した試行は、
リミッターが失敗を記録する前に直列化されます。そのため、1 つの Serve クライアントからの
同時の不正リトライでは、2 回の単純な不一致として競合するのではなく、2 回目の試行が直ちにロックアウトされることがあります。
HTTP API エンドポイント（たとえば `/v1/*`、`/tools/invoke`、`/api/channels/*`）
は Tailscale の ID ヘッダー認証を**使用しません**。それらは引き続き Gateway の
設定済み HTTP auth モードに従います。

重要な境界の注記:

- Gateway HTTP bearer auth は、実質的に all-or-nothing のオペレーターアクセスです。
- `/v1/chat/completions`、`/v1/responses`、または `/api/channels/*` を呼び出せる認証情報は、その Gateway に対するフルアクセスのオペレーターシークレットとして扱ってください。
- OpenAI 互換 HTTP サーフェスでは、共有シークレット bearer auth は完全なデフォルトのオペレータースコープ（`operator.admin`、`operator.approvals`、`operator.pairing`、`operator.read`、`operator.talk.secrets`、`operator.write`）と、エージェントターン向けの owner セマンティクスを復元します。より狭い `x-openclaw-scopes` 値を指定しても、この共有シークレット経路では権限は縮小されません。
- HTTP 上のリクエスト単位スコープセマンティクスは、trusted proxy auth やプライベートな受信での `gateway.auth.mode="none"` のような、ID を持つモードから来たリクエストにのみ適用されます。
- これらの ID を持つモードでは、`x-openclaw-scopes` を省略すると通常のデフォルトオペレータースコープセットにフォールバックします。より狭いスコープセットを使いたい場合は、そのヘッダーを明示的に送信してください。
- `/tools/invoke` も同じ共有シークレットルールに従います。つまり token / password bearer auth はそこでもフルオペレーターアクセスとして扱われ、一方で ID を持つモードでは引き続き宣言されたスコープが尊重されます。
- これらの認証情報を信頼されていない呼び出し元と共有しないでください。信頼境界ごとに別々の Gateway を使うことを優先してください。

**信頼前提:** token なしの Serve auth は Gateway ホストが信頼されていることを前提としています。
これを、同一ホスト上の敵対的プロセスに対する保護と見なしてはいけません。信頼されていない
ローカルコードが Gateway ホスト上で動く可能性がある場合は、`gateway.auth.allowTailscale`
を無効にし、`gateway.auth.mode: "token"` または
`"password"` による明示的な共有シークレット認証を必須にしてください。

**セキュリティルール:** これらのヘッダーを自分のリバースプロキシから転送しないでください。Gateway の前段で TLS 終端や
プロキシを行う場合は、`gateway.auth.allowTailscale` を無効化し、代わりに共有シークレット認証（`gateway.auth.mode:
"token"` または `"password"`）または [Trusted Proxy Auth](/ja-JP/gateway/trusted-proxy-auth)
を使用してください。

信頼済みプロキシ:

- Gateway の前段で TLS を終端する場合は、`gateway.trustedProxies` にプロキシ IP を設定してください。
- OpenClaw はそれらの IP からの `x-forwarded-for`（または `x-real-ip`）を信頼し、ローカルペアリングチェックと HTTP 認証 / ローカルチェックのためにクライアント IP を決定します。
- プロキシが `x-forwarded-for` を**上書き**し、Gateway ポートへの直接アクセスをブロックすることを確認してください。

[Tailscale](/ja-JP/gateway/tailscale) および [Web overview](/web) も参照してください。

### 0.6.1) node host 経由のブラウザ制御（推奨）

Gateway が remote で、ブラウザが別マシン上で動作している場合は、ブラウザマシン上で **node host**
を実行し、Gateway にブラウザアクションをプロキシさせてください（[Browser tool](/ja-JP/tools/browser) を参照）。
node のペアリングは管理者アクセスとして扱ってください。

推奨パターン:

- Gateway と node host を同じ tailnet（Tailscale）上に置く。
- node は意図的にペアリングし、ブラウザプロキシルーティングが不要なら無効にする。

避けるべきこと:

- relay / control ポートを LAN やパブリックインターネットに公開すること。
- ブラウザ制御エンドポイントに Tailscale Funnel を使うこと（公開露出）。

### 0.7) ディスク上のシークレット（機微データ）

`~/.openclaw/`（または `$OPENCLAW_STATE_DIR/`）配下のものは、シークレットまたは private データを含みうると考えてください。

- `openclaw.json`: config に token（gateway、remote gateway）、プロバイダー設定、許可リストが含まれる場合があります。
- `credentials/**`: チャネル認証情報（例: WhatsApp creds）、ペアリング許可リスト、レガシー OAuth インポート。
- `agents/<agentId>/agent/auth-profiles.json`: API キー、token プロファイル、OAuth トークン、および任意の `keyRef` / `tokenRef`。
- `secrets.json`（任意）: `file` SecretRef プロバイダー（`secrets.providers`）で使用されるファイルベースのシークレットペイロード。
- `agents/<agentId>/agent/auth.json`: レガシー互換ファイル。静的な `api_key` エントリは検出時にスクラブされます。
- `agents/<agentId>/sessions/**`: セッショントランスクリプト（`*.jsonl`）+ ルーティングメタデータ（`sessions.json`）。private メッセージやツール出力を含むことがあります。
- バンドルされた Plugin パッケージ: インストール済み Plugin（およびその `node_modules/`）。
- `sandboxes/**`: ツール sandbox ワークスペース。sandbox 内で読み書きしたファイルのコピーが蓄積することがあります。

強化のヒント:

- 権限は厳格に保ってください（ディレクトリは `700`、ファイルは `600`）。
- Gateway ホストではフルディスク暗号化を使用してください。
- ホストを共有する場合、Gateway 専用の OS ユーザーアカウントを優先してください。

### 0.8) ログ + トランスクリプト（redaction + retention）

アクセス制御が正しくても、ログやトランスクリプトは機密情報を漏らす可能性があります。

- Gateway ログにはツール要約、エラー、URL が含まれることがあります。
- セッショントランスクリプトには、貼り付けられたシークレット、ファイル内容、コマンド出力、リンクが含まれることがあります。

推奨事項:

- ツール要約の redaction を有効にしておいてください（`logging.redactSensitive: "tools"`; デフォルト）。
- 環境固有のパターンは `logging.redactPatterns` で追加してください（token、ホスト名、内部 URL）。
- 診断情報を共有する際は、生ログより `openclaw status --all` を優先してください（貼り付けしやすく、シークレットは秘匿化されます）。
- 長期保持が不要なら、古いセッショントランスクリプトとログファイルを削除してください。

詳細: [Logging](/ja-JP/gateway/logging)

### 1) DM: デフォルトで pairing

```json5
{
  channels: { whatsapp: { dmPolicy: "pairing" } },
}
```

### 2) グループ: どこでもメンション必須

```json
{
  "channels": {
    "whatsapp": {
      "groups": {
        "*": { "requireMention": true }
      }
    }
  },
  "agents": {
    "list": [
      {
        "id": "main",
        "groupChat": { "mentionPatterns": ["@openclaw", "@mybot"] }
      }
    ]
  }
}
```

グループチャットでは、明示的にメンションされたときだけ応答します。

### 3) 番号を分ける（WhatsApp、Signal、Telegram）

電話番号ベースのチャネルでは、AI を個人用番号とは別の電話番号で運用することを検討してください。

- 個人用番号: あなたの会話は非公開のまま
- ボット用番号: AI が適切な境界のもとで処理する

### 4) 読み取り専用モード（sandbox + tools 経由）

以下を組み合わせることで、読み取り専用プロファイルを構築できます。

- `agents.defaults.sandbox.workspaceAccess: "ro"`（または workspace アクセスなしなら `"none"`）
- `write`、`edit`、`apply_patch`、`exec`、`process` などをブロックする tool allow / deny リスト

追加の強化オプション:

- `tools.exec.applyPatch.workspaceOnly: true`（デフォルト）: sandbox 化がオフでも、`apply_patch` が workspace ディレクトリ外に書き込み / 削除できないようにします。`apply_patch` で workspace 外のファイルに触れさせたい意図がある場合にのみ `false` に設定してください。
- `tools.fs.workspaceOnly: true`（任意）: `read` / `write` / `edit` / `apply_patch` のパスと、ネイティブ prompt image 自動ロードパスを workspace ディレクトリに制限します（現在絶対パスを許可していて、単一のガードレールを追加したい場合に有用です）。
- ファイルシステムルートは狭く保ってください。エージェント workspace / sandbox workspace にホームディレクトリのような広いルートを使うのは避けてください。広いルートは、ローカルの機密ファイル（たとえば `~/.openclaw` 配下の state / config）をファイルシステムツールに露出する可能性があります。

### 5) セキュアベースライン（コピー / ペースト用）

Gateway を非公開に保ち、DM に pairing を要求し、常時起動のグループボットを避ける「安全なデフォルト」設定の 1 例です。

```json5
{
  gateway: {
    mode: "local",
    bind: "loopback",
    port: 18789,
    auth: { mode: "token", token: "your-long-random-token" },
  },
  channels: {
    whatsapp: {
      dmPolicy: "pairing",
      groups: { "*": { requireMention: true } },
    },
  },
}
```

ツール実行も「より安全なデフォルト」にしたい場合は、owner 以外のエージェント向けに sandbox + 危険なツールの deny を追加してください（例は以下の「エージェントごとのアクセスプロファイル」を参照）。

chat 駆動のエージェントターン向けの組み込みベースライン: owner 以外の送信者は `cron` または `gateway` ツールを使用できません。

## sandbox 化（推奨）

専用ドキュメント: [Sandboxing](/ja-JP/gateway/sandboxing)

相補的な 2 つのアプローチがあります。

- **Gateway 全体を Docker で実行する**（コンテナ境界）: [Docker](/ja-JP/install/docker)
- **ツール sandbox**（`agents.defaults.sandbox`、host gateway + Docker で分離されたツール）: [Sandboxing](/ja-JP/gateway/sandboxing)

注: エージェント間アクセスを防ぐには、`agents.defaults.sandbox.scope` を `"agent"`（デフォルト）
のままにするか、より厳密なセッション単位の分離として `"session"` を使用してください。`scope: "shared"` は
単一のコンテナ / workspace を使用します。

sandbox 内でのエージェント workspace アクセスも検討してください。

- `agents.defaults.sandbox.workspaceAccess: "none"`（デフォルト）では、エージェント workspace へのアクセスを禁止し、ツールは `~/.openclaw/sandboxes` 配下の sandbox workspace に対して動作します
- `agents.defaults.sandbox.workspaceAccess: "ro"` は、エージェント workspace を `/agent` に読み取り専用でマウントします（`write` / `edit` / `apply_patch` を無効化）
- `agents.defaults.sandbox.workspaceAccess: "rw"` は、エージェント workspace を `/workspace` に読み書き可能でマウントします
- 追加の `sandbox.docker.binds` は、正規化および canonicalize されたソースパスに対して検証されます。親 symlink トリックや canonical home alias も、`/etc`、`/var/run`、または OS ホーム配下の認証情報ディレクトリのようなブロック対象ルートに解決される場合は、依然としてクローズドフェイルします。

重要: `tools.elevated` は、sandbox の外で exec を実行するグローバルなベースラインの escape hatch です。実効 host はデフォルトで `gateway`、exec ターゲットが `node` に設定されている場合は `node` です。`tools.elevated.allowFrom` は厳格に保ち、見知らぬ相手に対して有効にしないでください。`agents.list[].tools.elevated` を使えば、エージェントごとに elevated をさらに制限できます。詳細は [Elevated Mode](/ja-JP/tools/elevated) を参照してください。

### サブエージェント委譲のガードレール

セッションツールを許可する場合、委譲されたサブエージェント実行も別の境界判断として扱ってください。

- エージェントが本当に委譲を必要としない限り、`sessions_spawn` を deny してください。
- `agents.defaults.subagents.allowAgents` と、エージェントごとの `agents.list[].subagents.allowAgents` 上書きは、既知の安全なターゲットエージェントに限定してください。
- 必ず sandbox 化を維持すべきワークフローでは、`sessions_spawn` を `sandbox: "require"` で呼び出してください（デフォルトは `inherit`）。
- `sandbox: "require"` は、ターゲットの子ランタイムが sandbox 化されていない場合に即座に失敗します。

## ブラウザ制御のリスク

ブラウザ制御を有効にすると、モデルに実際のブラウザを操作する能力を与えることになります。
そのブラウザプロファイルにログイン済みセッションが含まれている場合、モデルは
それらのアカウントやデータにアクセスできます。ブラウザプロファイルは**機微な state**として扱ってください。

- エージェント専用のプロファイルを優先してください（デフォルトの `openclaw` プロファイル）。
- エージェントに、自分の個人用 daily-driver プロファイルを使わせないでください。
- sandbox 化されたエージェントでは、信頼していない限り host ブラウザ制御を無効にしておいてください。
- スタンドアロンの loopback ブラウザ制御 API は共有シークレット auth のみを受け付けます
  （gateway token bearer auth または gateway password）。trusted-proxy や Tailscale Serve の ID ヘッダーは消費しません。
- ブラウザのダウンロードは信頼されていない入力として扱い、分離されたダウンロードディレクトリを優先してください。
- 可能なら、エージェントプロファイルではブラウザ同期 / パスワードマネージャーを無効にしてください（影響範囲を減らせます）。
- remote Gateway では、「ブラウザ制御」は、そのプロファイルが到達できるものへの「オペレーターアクセス」と同等だと考えてください。
- Gateway と node host は tailnet-only に保ち、ブラウザ制御ポートを LAN やパブリックインターネットに公開しないでください。
- 必要がない場合はブラウザプロキシルーティングを無効にしてください（`gateway.nodes.browser.mode="off"`）。
- Chrome MCP の既存セッションモードは**より安全ではありません**。そのホストの Chrome プロファイルが到達できるものに対して、あなたとして動作できます。

### ブラウザ SSRF ポリシー（デフォルトで strict）

OpenClaw のブラウザナビゲーションポリシーは、デフォルトで strict です。private / internal 宛先は、明示的に opt-in しない限り引き続きブロックされます。

- デフォルト: `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork` は未設定であり、ブラウザナビゲーションは private / internal / special-use 宛先を引き続きブロックします。
- レガシーエイリアス: `browser.ssrfPolicy.allowPrivateNetwork` も互換性のために引き続き受け付けられます。
- opt-in モード: private / internal / special-use 宛先を許可するには `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork: true` を設定してください。
- strict モードでは、明示的な例外に `hostnameAllowlist`（`*.example.com` のようなパターン）と `allowedHostnames`（`localhost` のようなブロック対象名を含む厳密なホスト例外）を使用してください。
- リダイレクトベースの pivot を減らすため、ナビゲーションはリクエスト前にチェックされ、ナビゲーション後の最終 `http(s)` URL に対してもベストエフォートで再チェックされます。

strict ポリシーの例:

```json5
{
  browser: {
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: false,
      hostnameAllowlist: ["*.example.com", "example.com"],
      allowedHostnames: ["localhost"],
    },
  },
}
```

## エージェントごとのアクセスプロファイル（multi-agent）

マルチエージェントルーティングでは、各エージェントごとに独自の sandbox + ツールポリシーを持てます。
これを使って、エージェントごとに **フルアクセス**、**読み取り専用**、**アクセスなし** を与えてください。
詳細と優先順位ルールは [Multi-Agent Sandbox & Tools](/ja-JP/tools/multi-agent-sandbox-tools) を参照してください。

一般的なユースケース:

- 個人用エージェント: フルアクセス、sandbox なし
- 家族 / 仕事用エージェント: sandbox 化 + 読み取り専用ツール
- 公開エージェント: sandbox 化 + ファイルシステム / シェルツールなし

### 例: フルアクセス（sandbox なし）

```json5
{
  agents: {
    list: [
      {
        id: "personal",
        workspace: "~/.openclaw/workspace-personal",
        sandbox: { mode: "off" },
      },
    ],
  },
}
```

### 例: 読み取り専用ツール + 読み取り専用 workspace

```json5
{
  agents: {
    list: [
      {
        id: "family",
        workspace: "~/.openclaw/workspace-family",
        sandbox: {
          mode: "all",
          scope: "agent",
          workspaceAccess: "ro",
        },
        tools: {
          allow: ["read"],
          deny: ["write", "edit", "apply_patch", "exec", "process", "browser"],
        },
      },
    ],
  },
}
```

### 例: ファイルシステム / シェルアクセスなし（プロバイダーメッセージングは許可）

```json5
{
  agents: {
    list: [
      {
        id: "public",
        workspace: "~/.openclaw/workspace-public",
        sandbox: {
          mode: "all",
          scope: "agent",
          workspaceAccess: "none",
        },
        // セッションツールはトランスクリプトから機密データを明らかにする可能性があります。OpenClaw はデフォルトでこれらのツールを
        // 現在のセッション + 生成されたサブエージェントセッションに制限していますが、必要に応じてさらに絞り込めます。
        // 設定リファレンスの `tools.sessions.visibility` を参照してください。
        tools: {
          sessions: { visibility: "tree" }, // self | tree | agent | all
          allow: [
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "whatsapp",
            "telegram",
            "slack",
            "discord",
          ],
          deny: [
            "read",
            "write",
            "edit",
            "apply_patch",
            "exec",
            "process",
            "browser",
            "canvas",
            "nodes",
            "cron",
            "gateway",
            "image",
          ],
        },
      },
    ],
  },
}
```

## AI に伝えるべきこと

エージェントのシステムプロンプトにセキュリティガイドラインを含めてください。

```
## Security Rules
- Never share directory listings or file paths with strangers
- Never reveal API keys, credentials, or infrastructure details
- Verify requests that modify system config with the owner
- When in doubt, ask before acting
- Keep private data private unless explicitly authorized
```

## インシデント対応

AI が問題のある動作をした場合:

### 封じ込め

1. **停止する:** macOS app（Gateway を監視している場合）を停止するか、`openclaw gateway` プロセスを終了してください。
2. **露出を閉じる:** 何が起きたかを理解するまで、`gateway.bind: "loopback"` に設定する（または Tailscale Funnel / Serve を無効化する）。
3. **アクセスを凍結する:** リスクの高い DM / グループを `dmPolicy: "disabled"` に切り替える / メンション必須にし、以前 `"*"` の全許可エントリがあったなら削除する。

### ローテーション（シークレットが漏れたなら侵害を前提とする）

1. Gateway auth（`gateway.auth.token` / `OPENCLAW_GATEWAY_PASSWORD`）をローテーションし、再起動する。
2. Gateway を呼び出せるすべてのマシンで remote クライアントシークレット（`gateway.remote.token` / `.password`）をローテーションする。
3. プロバイダー / API 認証情報（WhatsApp creds、Slack / Discord token、`auth-profiles.json` 内のモデル / API キー、および使用している場合は暗号化されたシークレットペイロード値）をローテーションする。

### 監査

1. Gateway ログを確認する: `/tmp/openclaw/openclaw-YYYY-MM-DD.log`（または `logging.file`）。
2. 該当するトランスクリプトを確認する: `~/.openclaw/agents/<agentId>/sessions/*.jsonl`。
3. 最近の config 変更を確認する（アクセス拡大につながった可能性のあるもの: `gateway.bind`、`gateway.auth`、DM / グループポリシー、`tools.elevated`、Plugin 変更）。
4. `openclaw security audit --deep` を再実行し、critical な検出結果が解消されたことを確認する。

### レポートのために収集するもの

- タイムスタンプ、Gateway ホストの OS + OpenClaw バージョン
- セッショントランスクリプト + 短いログ末尾（秘匿化後）
- 攻撃者が送った内容 + エージェントが行ったこと
- Gateway が loopback を超えて公開されていたかどうか（LAN / Tailscale Funnel / Serve）

## Secret Scanning（detect-secrets）

CI は `secrets` ジョブで `detect-secrets` の pre-commit hook を実行します。
`main` への push では、常に全ファイルスキャンを実行します。プルリクエストでは、ベースコミットが利用可能な場合は
変更ファイルのみの高速パスを使用し、そうでない場合は全ファイルスキャンにフォールバックします。失敗した場合、
まだベースラインに入っていない新しい候補があることを意味します。

### CI が失敗した場合

1. ローカルで再現する:

   ```bash
   pre-commit run --all-files detect-secrets
   ```

2. ツールを理解する:
   - pre-commit 内の `detect-secrets` は、リポジトリの
     baseline と除外設定を使って `detect-secrets-hook` を実行します。
   - `detect-secrets audit` は対話型レビューを開き、各 baseline
     項目を本物または false positive としてマークできます。
3. 本物のシークレットについては、ローテーション / 削除してから、スキャンを再実行して baseline を更新します。
4. false positive については、対話型 audit を実行して false としてマークします:

   ```bash
   detect-secrets audit .secrets.baseline
   ```

5. 新しい除外設定が必要な場合は、それらを `.detect-secrets.cfg` に追加し、
   対応する `--exclude-files` / `--exclude-lines` フラグで baseline を再生成してください（config
   ファイルは参照用のみです。detect-secrets は自動では読み込みません）。

更新後の `.secrets.baseline` が意図した状態を反映したら、それをコミットしてください。

## セキュリティ問題の報告

OpenClaw に脆弱性を見つけましたか？ 責任ある方法で報告してください。

1. メール: [security@openclaw.ai](mailto:security@openclaw.ai)
2. 修正されるまで公開投稿しない
3. ご希望であれば匿名にも対応しますが、通常はクレジットを記載します
