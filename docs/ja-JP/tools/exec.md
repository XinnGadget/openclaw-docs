---
read_when:
    - exec tool を使用または変更している
    - stdin または TTY の動作をデバッグしている
summary: Exec tool の使い方、stdin モード、TTY サポート
title: Exec Tool
x-i18n:
    generated_at: "2026-04-06T03:13:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: 28388971c627292dba9bf65ae38d7af8cde49a33bb3b5fc8b20da4f0e350bedd
    source_path: tools/exec.md
    workflow: 15
---

# Exec Tool

workspace でシェルコマンドを実行します。`process` によるフォアグラウンド + バックグラウンド実行をサポートします。
`process` が許可されていない場合、`exec` は同期的に実行され、`yieldMs`/`background` を無視します。
バックグラウンドセッションはエージェントごとにスコープされます。`process` は同じエージェントのセッションのみを参照します。

## パラメーター

- `command`（必須）
- `workdir`（デフォルトは cwd）
- `env`（キー/値の上書き）
- `yieldMs`（デフォルト 10000）: 遅延後に自動でバックグラウンド化
- `background`（bool）: すぐにバックグラウンド化
- `timeout`（秒、デフォルト 1800）: 期限切れで kill
- `pty`（bool）: 利用可能な場合は疑似ターミナルで実行（TTY 専用 CLI、coding agents、terminal UIs）
- `host`（`auto | sandbox | gateway | node`）: 実行場所
- `security`（`deny | allowlist | full`）: `gateway`/`node` の適用モード
- `ask`（`off | on-miss | always`）: `gateway`/`node` の承認プロンプト
- `node`（string）: `host=node` 用の node id/name
- `elevated`（bool）: elevated mode を要求する（設定済み host path 上でサンドボックスを抜ける）。`security=full` が強制されるのは、elevated が `full` に解決される場合のみです

注記:

- `host` のデフォルトは `auto` です: セッションで sandbox runtime が有効なら sandbox、そうでなければ gateway。
- `auto` はデフォルトのルーティング戦略であり、ワイルドカードではありません。呼び出しごとの `host=node` は `auto` から許可されます。呼び出しごとの `host=gateway` は sandbox runtime が有効でない場合にのみ許可されます。
- 追加設定がなくても、`host=auto` はそのまま「普通に動作」します。sandbox がなければ `gateway` に解決され、動作中の sandbox があれば sandbox に留まります。
- `elevated` は、設定済み host path 上で sandbox を抜けます。デフォルトでは `gateway`、`tools.exec.host=node` の場合（またはセッションデフォルトが `host=node` の場合）は `node` です。現在のセッション/provider で elevated access が有効な場合にのみ利用できます。
- `gateway`/`node` の承認は `~/.openclaw/exec-approvals.json` で制御されます。
- `node` には paired node（companion app または headless node host）が必要です。
- 複数の nodes が利用可能な場合は、1 つ選ぶために `exec.node` または `tools.exec.node` を設定してください。
- `exec host=node` は nodes 用の唯一の shell-execution path です。レガシーな `nodes.run` wrapper は削除されました。
- 非 Windows ホストでは、exec は `SHELL` が設定されていればそれを使用します。`SHELL` が `fish` の場合は、
  fish 非互換スクリプトを避けるため、`PATH` から `bash`（または `sh`）を優先し、
  どちらも存在しない場合のみ `SHELL` にフォールバックします。
- Windows ホストでは、exec は PowerShell 7（`pwsh`）の検出を優先し（Program Files、ProgramW6432、その後 PATH）、
  次に Windows PowerShell 5.1 にフォールバックします。
- ホスト実行（`gateway`/`node`）では、バイナリハイジャックや注入コードを防ぐため、
  `env.PATH` と loader 上書き（`LD_*`/`DYLD_*`）を拒否します。
- OpenClaw は、生成されたコマンド環境（PTY と sandbox 実行を含む）に `OPENCLAW_SHELL=exec` を設定するため、shell/profile ルールは exec-tool コンテキストを検出できます。
- 重要: sandboxing はデフォルトで**無効**です。sandboxing が無効な場合、暗黙の `host=auto` は
  `gateway` に解決されます。明示的な `host=sandbox` は、gateway host 上で黙って
  実行するのではなく、クローズドに失敗します。sandboxing を有効にするか、承認付きで `host=gateway` を使用してください。
- スクリプトの事前チェック（一般的な Python/Node の shell-syntax ミス向け）は、
  有効な `workdir` 境界内のファイルだけを検査します。スクリプトパスが `workdir` の外に解決される場合、
  そのファイルの事前チェックはスキップされます。
- すぐに始まる長時間作業については、一度だけ開始し、自動完了 wake が有効なら、
  コマンドが出力を出すか失敗したときの自動 wake に任せてください。
  ログ、状態、入力、介入には `process` を使用してください。sleep ループ、
  timeout ループ、反復ポーリングでスケジューリングをエミュレートしないでください。
- 後で実行すべき作業やスケジュールされた作業には、
  `exec` の sleep/delay パターンではなく cron を使用してください。

## 設定

- `tools.exec.notifyOnExit`（デフォルト: true）: true の場合、バックグラウンド化された exec セッションは終了時に system event をキューし、heartbeat を要求します。
- `tools.exec.approvalRunningNoticeMs`（デフォルト: 10000）: 承認ゲート付き exec がこれより長く実行されたとき、1 回だけ「running」通知を出します（0 で無効）。
- `tools.exec.host`（デフォルト: `auto`。sandbox runtime が有効なら `sandbox`、そうでなければ `gateway` に解決）
- `tools.exec.security`（デフォルト: sandbox では `deny`、未設定時の gateway + node では `full`）
- `tools.exec.ask`（デフォルト: `off`）
- 承認なしの host exec は gateway + node のデフォルトです。承認/allowlist 動作が必要な場合は、`tools.exec.*` とホスト側の `~/.openclaw/exec-approvals.json` の両方を厳しくしてください。[Exec approvals](/ja-JP/tools/exec-approvals#no-approval-yolo-mode) を参照してください。
- YOLO は `host=auto` ではなく、host-policy のデフォルト（`security=full`, `ask=off`）から来ます。gateway または node へのルーティングを強制したい場合は、`tools.exec.host` を設定するか `/exec host=...` を使用してください。
- `security=full` かつ `ask=off` モードでは、host exec は設定済みポリシーに直接従います。追加の heuristic な command-obfuscation prefilter はありません。
- `tools.exec.node`（デフォルト: 未設定）
- `tools.exec.strictInlineEval`（デフォルト: false）: true の場合、`python -c`、`node -e`、`ruby -e`、`perl -e`、`php -r`、`lua -e`、`osascript -e` などの inline interpreter eval 形式は常に明示的承認が必要です。`allow-always` は引き続き無害な interpreter/script invocations を永続化できますが、inline-eval 形式は毎回プロンプトが出ます。
- `tools.exec.pathPrepend`: exec 実行時に `PATH` の先頭に追加するディレクトリのリスト（gateway + sandbox のみ）。
- `tools.exec.safeBins`: 明示的 allowlist エントリなしで実行できる stdin-only の safe binaries。動作の詳細は [Safe bins](/ja-JP/tools/exec-approvals#safe-bins-stdin-only) を参照してください。
- `tools.exec.safeBinTrustedDirs`: `safeBins` のパスチェックで信頼する追加の明示ディレクトリ。`PATH` エントリは自動的には信頼されません。組み込みデフォルトは `/bin` と `/usr/bin` です。
- `tools.exec.safeBinProfiles`: safe bin ごとの任意の custom argv policy（`minPositional`, `maxPositional`, `allowedValueFlags`, `deniedFlags`）。

例:

```json5
{
  tools: {
    exec: {
      pathPrepend: ["~/bin", "/opt/oss/bin"],
    },
  },
}
```

### PATH の扱い

- `host=gateway`: login-shell の `PATH` を exec 環境にマージします。`env.PATH` の上書きは
  host 実行では拒否されます。daemon 自体は引き続き最小限の `PATH` で実行されます:
  - macOS: `/opt/homebrew/bin`, `/usr/local/bin`, `/usr/bin`, `/bin`
  - Linux: `/usr/local/bin`, `/usr/bin`, `/bin`
- `host=sandbox`: コンテナ内で `sh -lc`（login shell）を実行するため、`/etc/profile` が `PATH` をリセットする場合があります。
  OpenClaw は、内部 env var を介して profile 読み込み後に `env.PATH` を先頭追加します（shell interpolation なし）。
  `tools.exec.pathPrepend` もここで適用されます。
- `host=node`: 渡したブロックされていない env 上書きだけが node に送られます。`env.PATH` の上書きは
  host 実行では拒否され、node hosts では無視されます。node 上で追加の PATH エントリが必要なら、
  node host service の環境（systemd/launchd）を設定するか、標準的な場所に tools をインストールしてください。

エージェントごとの node binding（config では agent list index を使用）:

```bash
openclaw config get agents.list
openclaw config set agents.list[0].tools.exec.node "node-id-or-name"
```

Control UI: Nodes タブには、同じ設定用の小さな「Exec node binding」パネルがあります。

## セッション上書き（`/exec`）

`/exec` を使うと、`host`、`security`、`ask`、`node` の**セッションごとの**
デフォルトを設定できます。
現在の値を表示するには、引数なしで `/exec` を送信してください。

例:

```
/exec host=auto security=allowlist ask=on-miss node=mac-1
```

## 認可モデル

`/exec` は **authorized senders** に対してのみ有効です（channel allowlists/pairing と `commands.useAccessGroups`）。
これは**セッション状態のみ**を更新し、config には書き込みません。exec を完全に無効にするには、tool
policy（`tools.deny: ["exec"]` またはエージェント単位）で拒否してください。明示的に
`security=full` と `ask=off` を設定しない限り、host approvals は引き続き適用されます。

## Exec approvals（companion app / node host）

sandbox 化されたエージェントでは、exec が gateway または node host 上で実行される前に、
リクエストごとの承認を要求できます。
ポリシー、allowlist、UI フローについては [Exec approvals](/ja-JP/tools/exec-approvals) を参照してください。

承認が必要な場合、exec tool は
`status: "approval-pending"` と approval id を返してすぐに終了します。承認後（または拒否 / timeout 後）、
Gateway は system events（`Exec finished` / `Exec denied`）を発行します。コマンドが
`tools.exec.approvalRunningNoticeMs` より長く実行されている場合、1 回だけ `Exec running`
通知が発行されます。ネイティブの承認カード/ボタンがあるチャンネルでは、エージェントはまずその
ネイティブ UI に依存し、tool
result がチャット承認を利用できない、または手動承認が唯一の経路であると明示している場合にのみ、
手動の `/approve` コマンドを含めるべきです。

## Allowlist + safe bins

手動 allowlist の適用は、**解決済みバイナリパスのみ**に一致します（basename 一致はなし）。
`security=allowlist` の場合、すべてのパイプラインセグメントが
allowlist または safe bin であるときにのみ、シェルコマンドは自動許可されます。
チェイン（`;`, `&&`, `||`）とリダイレクトは、
すべてのトップレベルセグメントが allowlist を満たす場合にのみ allowlist mode で許可されます
（safe bins を含む）。
リダイレクトは引き続き未サポートです。
永続的な `allow-always` の信頼でもこのルールは回避できません。チェインされたコマンドでは、
すべてのトップレベルセグメントが一致する必要があります。

`autoAllowSkills` は exec approvals における別の convenience path です。これは
手動パス allowlist エントリとは同じではありません。厳密な明示的信頼が必要なら、
`autoAllowSkills` は無効のままにしてください。

2 つの制御は用途を分けて使ってください。

- `tools.exec.safeBins`: 小さな stdin-only のストリームフィルター。
- `tools.exec.safeBinTrustedDirs`: safe-bin 実行ファイルパス用の明示的な追加信頼ディレクトリ。
- `tools.exec.safeBinProfiles`: custom safe bins 用の明示的 argv policy。
- allowlist: 実行ファイルパスへの明示的信頼。

`safeBins` を汎用 allowlist として扱わず、interpreter/runtime binaries（例: `python3`, `node`, `ruby`, `bash`）を追加しないでください。これらが必要なら、明示的 allowlist entries を使い、承認プロンプトを有効のままにしてください。
`openclaw security audit` は、interpreter/runtime `safeBins` entries に明示的 profiles が不足している場合に警告し、`openclaw doctor --fix` は不足している custom `safeBinProfiles` entries をひな形生成できます。
`openclaw security audit` と `openclaw doctor` は、`jq` のような広い動作を持つ bins を明示的に `safeBins` に戻した場合にも警告します。
interpreter を明示的に allowlist する場合は、inline code-eval 形式で毎回新しい承認が必要になるよう、`tools.exec.strictInlineEval` を有効にしてください。

完全なポリシーの詳細と例については、[Exec approvals](/ja-JP/tools/exec-approvals#safe-bins-stdin-only) と [Safe bins versus allowlist](/ja-JP/tools/exec-approvals#safe-bins-versus-allowlist) を参照してください。

## 例

フォアグラウンド:

```json
{ "tool": "exec", "command": "ls -la" }
```

バックグラウンド + poll:

```json
{"tool":"exec","command":"npm run build","yieldMs":1000}
{"tool":"process","action":"poll","sessionId":"<id>"}
```

ポーリングはオンデマンドの状態確認用であり、待機ループ用ではありません。自動完了 wake
が有効であれば、コマンドは出力を出すか失敗したときにセッションを wake できます。

キー送信（tmux スタイル）:

```json
{"tool":"process","action":"send-keys","sessionId":"<id>","keys":["Enter"]}
{"tool":"process","action":"send-keys","sessionId":"<id>","keys":["C-c"]}
{"tool":"process","action":"send-keys","sessionId":"<id>","keys":["Up","Up","Enter"]}
```

Submit（CR のみ送信）:

```json
{ "tool": "process", "action": "submit", "sessionId": "<id>" }
```

Paste（デフォルトで bracketed）:

```json
{ "tool": "process", "action": "paste", "sessionId": "<id>", "text": "line1\nline2\n" }
```

## apply_patch

`apply_patch` は、構造化された複数ファイル編集のための `exec` の subtool です。
OpenAI および OpenAI Codex models ではデフォルトで有効です。無効化したい、
または特定の models に制限したい場合にのみ config を使用してください。

```json5
{
  tools: {
    exec: {
      applyPatch: { workspaceOnly: true, allowModels: ["gpt-5.4"] },
    },
  },
}
```

注記:

- OpenAI/OpenAI Codex models でのみ利用可能です。
- tool policy は引き続き適用されます。`allow: ["write"]` は暗黙的に `apply_patch` も許可します。
- config は `tools.exec.applyPatch` 配下にあります。
- `tools.exec.applyPatch.enabled` のデフォルトは `true` です。OpenAI models で tool を無効化するには `false` に設定してください。
- `tools.exec.applyPatch.workspaceOnly` のデフォルトは `true`（workspace 内に限定）です。workspace directory 外への書き込み/削除を意図的に許可したい場合にのみ `false` に設定してください。

## 関連

- [Exec approvals](/ja-JP/tools/exec-approvals) — シェルコマンドの承認ゲート
- [Sandboxing](/ja-JP/gateway/sandboxing) — sandbox 化された環境でコマンドを実行する
- [Background Process](/ja-JP/gateway/background-process) — 長時間実行の exec と process tool
- [Security](/ja-JP/gateway/security) — tool policy と elevated access
