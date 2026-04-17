---
read_when:
    - 'exec承認またはallowlistを設定する_gsharedענדיקanalysis to=final code: null  天天中彩票可以assistant final to=all(final) code  പുറ്റിയ text'
    - macOSアプリでexec承認UXを実装する
    - サンドボックスエスケーププロンプトとその影響を確認する
summary: exec承認、allowlist、およびサンドボックスエスケーププロンプト
title: exec承認
x-i18n:
    generated_at: "2026-04-11T02:48:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: 5f4a2e2f1f3c13a1d1926c9de0720513ea8a74d1ca571dbe74b188d8c560c14c
    source_path: tools/exec-approvals.md
    workflow: 15
---

# exec承認

exec承認は、サンドボックス化されたagentが実ホスト（`gateway` または `node`）上でコマンドを実行できるようにするための**companion app / node hostのガードレール**です。安全インターロックのようなものと考えてください。コマンドは、ポリシー + allowlist + （任意の）ユーザー承認のすべてが許可した場合にのみ許可されます。exec承認は、ツールポリシーおよびelevatedゲーティングに**追加で**適用されます（`elevated` が `full` の場合を除き、この場合は承認をスキップします）。実効ポリシーは `tools.exec.*` と承認デフォルトの**より厳しい方**です。承認フィールドが省略された場合は、`tools.exec` の値が使われます。  
ホストexecは、そのマシン上のローカル承認状態も使用します。`~/.openclaw/exec-approvals.json` にあるホストローカルの `ask: "always"` は、セッションや設定デフォルトが `ask: "on-miss"` を要求していても、引き続き毎回プロンプトを表示します。  
要求されたポリシー、ホストポリシーのソース、および実効結果を確認するには、`openclaw approvals get`、`openclaw approvals get --gateway`、または `openclaw approvals get --node <id|name|ip>` を使用してください。  
ローカルマシンでは、`openclaw exec-policy show` が同じマージ済みビューを表示し、`openclaw exec-policy set|preset` でローカルの要求ポリシーとローカルホスト承認ファイルを一度に同期できます。ローカルscopeが `host=node` を要求した場合、`openclaw exec-policy show` は、そのscopeをローカル承認ファイルが実効的な信頼できる情報源であるかのように見せかけるのではなく、ランタイムではnode管理として報告します。

companion app UIが**利用できない**場合、プロンプトが必要なすべての要求は**ask fallback**（デフォルト: deny）によって処理されます。

ネイティブなチャット承認クライアントは、保留中の承認メッセージ上にチャネル固有の操作UIを出すこともできます。たとえばMatrixでは、承認プロンプト上にリアクションショートカット（`✅` で一度だけ許可、`❌` で拒否、利用可能な場合は `♾️` で常に許可）を出しつつ、フォールバックとしてメッセージ内の `/approve ...` コマンドも残せます。

## 適用される場所

exec承認は、実行ホスト上でローカルに適用されます。

- **gateway host** → Gatewayマシン上の `openclaw` プロセス
- **node host** → node runner（macOS companion app または headless node host）

信頼モデルに関する注意:

- Gatewayで認証された呼び出し元は、そのGatewayの信頼されたoperatorです。
- ペアリングされたnodeは、その信頼されたoperator能力をnode host上へ拡張します。
- exec承認は偶発的な実行リスクを減らしますが、ユーザーごとの認証境界ではありません。
- 承認済みのnode-host実行は、正規の実行コンテキストを束縛します: 正規のcwd、正確なargv、存在する場合のenv束縛、必要に応じた固定済み実行ファイルパス。
- シェルスクリプトおよびインタープリター/ランタイムによる直接ファイル実行については、OpenClawは1つの具体的なローカルファイルオペランドも束縛しようとします。承認後、実行前にその束縛ファイルが変更されていた場合、内容が変化したものを実行する代わりに、その実行は拒否されます。
- このファイル束縛は、すべてのインタープリター/ランタイムのローダーパスに対する完全な意味モデルではなく、意図的にベストエフォートです。承認モードで正確に1つの具体的なローカルファイルを束縛できない場合、完全にカバーされているふりをするのではなく、承認付き実行の発行を拒否します。

macOSでの分割:

- **node host service** は、ローカルIPC経由で `system.run` を**macOS app** に転送します。
- **macOS app** が承認を適用し、UIコンテキストでコマンドを実行します。

## 設定と保存場所

承認は、実行ホスト上のローカルJSONファイルに保存されます。

`~/.openclaw/exec-approvals.json`

スキーマ例:

```json
{
  "version": 1,
  "socket": {
    "path": "~/.openclaw/exec-approvals.sock",
    "token": "base64url-token"
  },
  "defaults": {
    "security": "deny",
    "ask": "on-miss",
    "askFallback": "deny",
    "autoAllowSkills": false
  },
  "agents": {
    "main": {
      "security": "allowlist",
      "ask": "on-miss",
      "askFallback": "deny",
      "autoAllowSkills": true,
      "allowlist": [
        {
          "id": "B0C8C0B3-2C2D-4F8A-9A3C-5A4B3C2D1E0F",
          "pattern": "~/Projects/**/bin/rg",
          "lastUsedAt": 1737150000000,
          "lastUsedCommand": "rg -n TODO",
          "lastResolvedPath": "/Users/user/Projects/.../bin/rg"
        }
      ]
    }
  }
}
```

## 承認なしの「YOLO」モード

承認プロンプトなしでホストexecを実行したい場合は、**両方**のポリシーレイヤーを開く必要があります。

- OpenClaw設定内の要求execポリシー（`tools.exec.*`）
- `~/.openclaw/exec-approvals.json` 内のホストローカル承認ポリシー

これは、明示的に厳しくしない限り、現在のデフォルトホスト動作です。

- `tools.exec.security`: `gateway`/`node` では `full`
- `tools.exec.ask`: `off`
- ホストの `askFallback`: `full`

重要な違い:

- `tools.exec.host=auto` は、execをどこで実行するかを選びます: 利用可能ならサンドボックス、そうでなければgateway。
- YOLOは、ホストexecをどう承認するかを選びます: `security=full` と `ask=off`。
- YOLOモードでは、OpenClawは設定済みホストexecポリシーの上に、別個のヒューリスティックなコマンド難読化承認ゲートを追加しません。
- `auto` は、サンドボックス化されたセッションからgatewayルーティングを自由に上書きできることを意味しません。呼び出しごとの `host=node` 要求は `auto` から許可され、`host=gateway` はサンドボックスランタイムがアクティブでない場合にのみ `auto` から許可されます。安定した非autoデフォルトが必要な場合は、`tools.exec.host` を設定するか、`/exec host=...` を明示的に使ってください。

より保守的な構成にしたい場合は、どちらか一方のレイヤーを `allowlist` / `on-miss` または `deny` に戻してください。

Gateway hostで「絶対にプロンプトを出さない」永続設定:

```bash
openclaw config set tools.exec.host gateway
openclaw config set tools.exec.security full
openclaw config set tools.exec.ask off
openclaw gateway restart
```

次に、ホスト承認ファイルも一致するように設定します。

```bash
openclaw approvals set --stdin <<'EOF'
{
  version: 1,
  defaults: {
    security: "full",
    ask: "off",
    askFallback: "full"
  }
}
EOF
```

現在のマシン上で同じGateway hostポリシーを適用するローカルショートカット:

```bash
openclaw exec-policy preset yolo
```

このローカルショートカットは次の両方を更新します。

- ローカルの `tools.exec.host/security/ask`
- ローカルの `~/.openclaw/exec-approvals.json` デフォルト

これは意図的にローカル専用です。Gateway hostまたはnode hostの承認をリモートで変更する必要がある場合は、引き続き `openclaw approvals set --gateway` または `openclaw approvals set --node <id|name|ip>` を使用してください。

node hostの場合は、同じ承認ファイルを代わりにそのnodeへ適用します。

```bash
openclaw approvals set --node <id|name|ip> --stdin <<'EOF'
{
  version: 1,
  defaults: {
    security: "full",
    ask: "off",
    askFallback: "full"
  }
}
EOF
```

重要なローカル専用の制限:

- `openclaw exec-policy` はnode承認を同期しない
- `openclaw exec-policy set --host node` は拒否される
- node exec承認はランタイム時にnodeから取得されるため、node向け更新には `openclaw approvals --node ...` を使用する必要がある

セッション限定のショートカット:

- `/exec security=full ask=off` は現在のセッションだけを変更する。
- `/elevated full` は、同じセッションでexec承認もスキップするbreak-glassショートカット。

ホスト承認ファイルが設定より厳しいままなら、引き続きそのより厳しいホストポリシーが優先されます。

## ポリシーノブ

### Security（`exec.security`）

- **deny**: すべてのホストexec要求をブロックする。
- **allowlist**: allowlistにあるコマンドだけを許可する。
- **full**: すべてを許可する（elevatedと同等）。

### Ask（`exec.ask`）

- **off**: プロンプトを一切表示しない。
- **on-miss**: allowlistが一致しない場合のみプロンプトを表示する。
- **always**: すべてのコマンドでプロンプトを表示する。
- 実効askモードが `always` の場合、`allow-always` の永続的な信頼はプロンプトを抑止しない

### Ask fallback（`askFallback`）

プロンプトが必要だが到達可能なUIがない場合、fallbackが次を決めます。

- **deny**: ブロックする。
- **allowlist**: allowlistが一致する場合のみ許可する。
- **full**: 許可する。

### インラインインタープリターevalの強化（`tools.exec.strictInlineEval`）

`tools.exec.strictInlineEval=true` の場合、OpenClawはインラインコードeval形式を、インタープリターバイナリー自体がallowlistに入っていても、承認専用として扱います。

例:

- `python -c`
- `node -e`, `node --eval`, `node -p`
- `ruby -e`
- `perl -e`, `perl -E`
- `php -r`
- `lua -e`
- `osascript -e`

これは、1つの安定したファイルオペランドへきれいに対応しないインタープリターローダーに対する多層防御です。strictモードでは:

- これらのコマンドには引き続き明示的な承認が必要です。
- `allow-always` は、それらに対して新しいallowlistエントリーを自動で永続化しません。

## Allowlist（agentごと）

allowlistは**agentごと**です。複数のagentが存在する場合は、macOS appで編集中のagentを切り替えてください。パターンは**大文字小文字を区別しないglob一致**です。パターンは**バイナリーパス**に解決される必要があります（basenameのみのエントリーは無視されます）。レガシーな `agents.default` エントリーは、読み込み時に `agents.main` へ移行されます。`echo ok && pwd` のようなシェル連結でも、トップレベルの各セグメントがallowlistルールを満たす必要があります。

例:

- `~/Projects/**/bin/peekaboo`
- `~/.local/bin/*`
- `/opt/homebrew/bin/rg`

各allowlistエントリーは次を追跡します。

- **id** UI識別用の安定したUUID（オプション）
- **last used** タイムスタンプ
- **last used command**
- **last resolved path**

## Skill CLIの自動許可

**Auto-allow skill CLIs** が有効な場合、既知のSkillsから参照される実行ファイルは、node上（macOS nodeまたはheadless node host）でallowlist済みとして扱われます。これは、Gateway RPC経由でskill binリストを取得するために `skills.bins` を使用します。厳密な手動allowlistだけにしたい場合は、これを無効にしてください。

重要な信頼に関する注意:

- これは、手動パスallowlistエントリーとは別の**暗黙の利便性allowlist**です。
- これは、Gatewayとnodeが同じ信頼境界内にある信頼済みoperator環境向けです。
- 厳密に明示的な信頼が必要な場合は、`autoAllowSkills: false` のままにして、手動パスallowlistエントリーのみを使用してください。

## Safe bins（stdin専用）

`tools.exec.safeBins` は、明示的なallowlistエントリーなしで、allowlistモードでも実行できる**stdin専用**バイナリー（例: `cut`）の小さなリストを定義します。safe binsは位置ファイル引数とパス風トークンを拒否するため、入力ストリームに対してのみ動作できます。これは汎用的な信頼リストではなく、ストリームフィルターのための狭い高速経路として扱ってください。  
インタープリターやランタイムのバイナリー（例: `python3`、`node`、`ruby`、`bash`、`sh`、`zsh`）を `safeBins` に追加してはいけません。  
コマンドがコードを評価できる、サブコマンドを実行できる、または設計上ファイルを読める場合は、明示的なallowlistエントリーを優先し、承認プロンプトを有効のままにしてください。  
カスタムsafe binsは、`tools.exec.safeBinProfiles.<bin>` で明示的なプロファイルを定義する必要があります。  
検証はargv形状のみから決定論的に行われ（ホストファイルシステムの存在確認は行いません）、これによりallow/denyの違いによるファイル存在oracle動作を防ぎます。  
デフォルトのsafe binsでは、ファイル指向オプションが拒否されます（例: `sort -o`, `sort --output`, `sort --files0-from`, `sort --compress-program`, `sort --random-source`, `sort --temporary-directory`/`-T`, `wc --files0-from`, `jq -f/--from-file`, `grep -f/--file`）。  
safe binsは、stdin専用の挙動を壊すオプションに対して、バイナリーごとの明示的なフラグポリシーも適用します（例: `sort -o/--output/--compress-program` と grepの再帰フラグ）。  
long optionはsafe-binモードでclosed fail検証されます。未知のフラグと曖昧な省略形は拒否されます。  
safe-binプロファイルごとの拒否フラグ:

[//]: # "SAFE_BIN_DENIED_FLAGS:START"

- `grep`: `--dereference-recursive`, `--directories`, `--exclude-from`, `--file`, `--recursive`, `-R`, `-d`, `-f`, `-r`
- `jq`: `--argfile`, `--from-file`, `--library-path`, `--rawfile`, `--slurpfile`, `-L`, `-f`
- `sort`: `--compress-program`, `--files0-from`, `--output`, `--random-source`, `--temporary-directory`, `-T`, `-o`
- `wc`: `--files0-from`

[//]: # "SAFE_BIN_DENIED_FLAGS:END"

safe binsは、stdin専用セグメントについて、実行時にargvトークンを**リテラルテキスト**として扱うことも強制します（glob展開も `$VARS` 展開もなし）。そのため、`*` や `$HOME/...` のようなパターンを使ってファイル読み取りを紛れ込ませることはできません。  
safe binsは、信頼されたバイナリーディレクトリから解決される必要もあります（システムデフォルトに加え、任意で `tools.exec.safeBinTrustedDirs`）。`PATH` エントリーが自動で信頼されることはありません。  
デフォルトの信頼済みsafe-binディレクトリは、意図的に最小限です: `/bin`, `/usr/bin`。  
safe-bin実行ファイルがpackage managerやユーザーパス（例: `/opt/homebrew/bin`, `/usr/local/bin`, `/opt/local/bin`, `/snap/bin`）にある場合は、それらを `tools.exec.safeBinTrustedDirs` に明示的に追加してください。  
allowlistモードでは、シェル連結とリダイレクトは自動許可されません。

シェル連結（`&&`, `||`, `;`）は、各トップレベルセグメントがallowlist要件を満たしている場合に許可されます（safe binsまたはskill自動許可を含む）。リダイレクトは、allowlistモードでは引き続き未サポートです。  
コマンド置換（`$()` / バッククォート）は、ダブルクォート内も含め、allowlist解析時に拒否されます。リテラルな `$()` テキストが必要なら、シングルクォートを使ってください。  
macOS companion-app承認では、シェル制御または展開構文（`&&`, `||`, `;`, `|`, `` ` ``, `$`, `<`, `>`, `(`, `)`）を含む生のシェルテキストは、シェルバイナリー自体がallowlistにない限り、allowlist missとして扱われます。  
シェルラッパー（`bash|sh|zsh ... -c/-lc`）では、リクエストスコープのenv上書きは、小さな明示的allowlist（`TERM`, `LANG`, `LC_*`, `COLORTERM`, `NO_COLOR`, `FORCE_COLOR`）へ縮小されます。  
allowlistモードでの `allow-always` 判断では、既知のdispatchラッパー（`env`, `nice`, `nohup`, `stdbuf`, `timeout`）は、ラッパーパスではなく内部の実行ファイルパスを永続化します。シェルマルチプレクサー（`busybox`, `toybox`）も、シェルアプレット（`sh`, `ash` など）についてアンラップされるため、マルチプレクサーバイナリーではなく内部実行ファイルが永続化されます。ラッパーまたはマルチプレクサーを安全にアンラップできない場合、allowlistエントリーは自動では永続化されません。  
`python3` や `node` のようなインタープリターをallowlistに入れる場合は、インラインevalに引き続き明示的承認を必要とさせるため、`tools.exec.strictInlineEval=true` を推奨します。strictモードでは、`allow-always` は安全なインタープリター/スクリプト呼び出しを引き続き永続化できますが、インラインevalキャリアは自動では永続化されません。

デフォルトのsafe bins:

[//]: # "SAFE_BIN_DEFAULTS:START"

`cut`, `uniq`, `head`, `tail`, `tr`, `wc`

[//]: # "SAFE_BIN_DEFAULTS:END"

`grep` と `sort` はデフォルトリストに含まれていません。これらをオプトインする場合は、stdin以外のワークフロー向けに明示的なallowlistエントリーを維持してください。  
safe-binモードの `grep` では、パターンは `-e`/`--regexp` で指定してください。位置指定のパターン形式は拒否されるため、ファイルオペランドを曖昧な位置引数として紛れ込ませることはできません。

### Safe binsとallowlistの違い

| Topic | `tools.exec.safeBins` | Allowlist (`exec-approvals.json`) |
| ---------------- | ------------------------------------------------------ | ------------------------------------------------------------ |
| Goal | 狭いstdinフィルターを自動許可する | 特定の実行ファイルを明示的に信頼する |
| Match type | 実行ファイル名 + safe-bin argvポリシー | 解決済み実行ファイルパスのglobパターン |
| Argument scope | safe-binプロファイルとリテラルトークン規則によって制限される | パスマッチのみ。引数はそれ以外では利用者の責任 |
| Typical examples | `head`, `tail`, `tr`, `wc` | `jq`, `python3`, `node`, `ffmpeg`, カスタムCLI |
| Best use | パイプライン内の低リスクなテキスト変換 | より広い挙動や副作用を持つ任意のツール |

設定場所:

- `safeBins` は設定から取得されます（`tools.exec.safeBins` またはagentごとの `agents.list[].tools.exec.safeBins`）。
- `safeBinTrustedDirs` は設定から取得されます（`tools.exec.safeBinTrustedDirs` またはagentごとの `agents.list[].tools.exec.safeBinTrustedDirs`）。
- `safeBinProfiles` は設定から取得されます（`tools.exec.safeBinProfiles` またはagentごとの `agents.list[].tools.exec.safeBinProfiles`）。agentごとのプロファイルキーはグローバルキーを上書きします。
- allowlistエントリーは、ホストローカルの `~/.openclaw/exec-approvals.json` の `agents.<id>.allowlist` に保存されます（またはControl UI / `openclaw approvals allowlist ...` 経由）。
- `openclaw security audit` は、インタープリター/ランタイムのbinが明示的なプロファイルなしで `safeBins` に現れると、`tools.exec.safe_bins_interpreter_unprofiled` で警告します。
- `openclaw doctor --fix` は、不足しているカスタム `safeBinProfiles.<bin>` エントリーを `{}` としてひな形作成できます（その後、確認してより厳しくしてください）。インタープリター/ランタイムのbinは自動ひな形作成されません。

カスタムプロファイル例:
__OC_I18N_900005__
`jq` を明示的に `safeBins` にオプトインした場合でも、safe-binモードではOpenClawは `env` builtinを拒否します。そのため、`jq -n env` でホストプロセス環境をダンプするには、明示的なallowlistパスまたは承認プロンプトが必要です。

## Control UIでの編集

**Control UI → Nodes → Exec approvals** カードを使って、デフォルト、agentごとの上書き、およびallowlistを編集します。scope（Defaultsまたはagent）を選び、ポリシーを調整し、allowlistパターンを追加/削除して、**Save** を押してください。UIには、リストを整理しやすいように、各パターンの **last used** メタデータが表示されます。

ターゲットセレクターでは、**Gateway**（ローカル承認）または **Node** を選びます。Nodeは `system.execApprovals.get/set` を通知している必要があります（macOS appまたはheadless node host）。  
nodeがまだexec承認を通知していない場合は、そのローカルの `~/.openclaw/exec-approvals.json` を直接編集してください。

CLI: `openclaw approvals` はgatewayまたはnodeの編集をサポートします（[Approvals CLI](/cli/approvals)を参照）。

## 承認フロー

プロンプトが必要な場合、Gatewayは `exec.approval.requested` をoperatorクライアントへブロードキャストします。  
Control UIとmacOS appは `exec.approval.resolve` でこれを解決し、その後Gatewayが承認済み要求をnode hostへ転送します。

`host=node` の場合、承認要求には正規の `systemRunPlan` ペイロードが含まれます。Gatewayは、承認済み `system.run` 要求を転送するとき、このplanを権威あるコマンド/cwd/セッションコンテキストとして使います。

これは、非同期承認の待機時間において重要です。

- node exec経路は、最初に1つの正規planを準備する
- 承認レコードは、そのplanと束縛メタデータを保存する
- 一度承認されると、最終的に転送される `system.run` 呼び出しは、後からの呼び出し元の編集を信頼せず、保存済みplanを再利用する
- 承認要求作成後に呼び出し元が `command`、`rawCommand`、`cwd`、`agentId`、または `sessionKey` を変更すると、Gatewayはその転送実行を承認不一致として拒否する

## インタープリター/ランタイムコマンド

承認付きのインタープリター/ランタイム実行は、意図的に保守的です。

- 正確なargv/cwd/envコンテキストは常に束縛されます。
- 直接シェルスクリプト形式および直接ランタイムファイル形式は、ベストエフォートで1つの具体的なローカルファイルスナップショットへ束縛されます。
- なお1つの直接ローカルファイルに解決される一般的なpackage managerラッパー形式（例: `pnpm exec`, `pnpm node`, `npm exec`, `npx`）は、束縛前にアンラップされます。
- OpenClawがインタープリター/ランタイムコマンドに対して正確に1つの具体的ローカルファイルを特定できない場合（例: package script、eval形式、ランタイム固有のローダーチェーン、または曖昧な複数ファイル形式）、意味的カバレッジがあると主張する代わりに、承認付き実行は拒否されます。
- そのようなワークフローでは、サンドボックス化、別のホスト境界、またはoperatorがより広いランタイム意味論を受け入れる明示的な信頼済みallowlist/fullワークフローを使ってください。

承認が必要な場合、execツールは承認idを返して即座に終了します。そのidを使って、後続のsystemイベント（`Exec finished` / `Exec denied`）を関連付けてください。タイムアウトまでに判断が届かなければ、その要求は承認タイムアウトとして扱われ、拒否理由として表示されます。

### フォローアップ配信の挙動

承認済みの非同期execが完了した後、OpenClawは同じセッションへフォローアップの `agent` ターンを送信します。

- 有効な外部配信ターゲット（配信可能なチャネル + ターゲット `to`）が存在する場合、フォローアップ配信はそのチャネルを使用します。
- 外部ターゲットのないwebchat専用または内部セッションフローでは、フォローアップ配信はセッション専用のままです（`deliver: false`）。
- 呼び出し元が、解決可能な外部チャネルなしで厳密な外部配信を明示的に要求した場合、その要求は `INVALID_REQUEST` で失敗します。
- `bestEffortDeliver` が有効で、外部チャネルを解決できない場合、失敗する代わりに配信はセッション専用へ格下げされます。

確認ダイアログには次が含まれます。

- command + args
- cwd
- agent id
- 解決済み実行ファイルパス
- host + ポリシーメタデータ

アクション:

- **Allow once** → 今回だけ実行
- **Always allow** → allowlistに追加して実行
- **Deny** → ブロック

## チャットチャネルへの承認転送

exec承認プロンプトは、任意のチャットチャネル（プラグインチャネルを含む）へ転送でき、`/approve` で承認できます。これは通常の送信配信パイプラインを使用します。

設定:
__OC_I18N_900006__
チャットで返信:
__OC_I18N_900007__
`/approve` コマンドは、exec承認とプラグイン承認の両方を扱います。IDが保留中のexec承認に一致しない場合、自動的にプラグイン承認を確認します。

### プラグイン承認の転送

プラグイン承認の転送はexec承認と同じ配信パイプラインを使いますが、`approvals.plugin` 配下に独立した設定を持ちます。一方を有効/無効にしても、もう一方には影響しません。
__OC_I18N_900008__
設定形状は `approvals.exec` と同一です。`enabled`、`mode`、`agentFilter`、`sessionFilter`、`targets` は同じように動作します。

共有の対話型返信をサポートするチャネルでは、exec承認とプラグイン承認の両方に同じ承認ボタンが表示されます。共有の対話型UIを持たないチャネルでは、`/approve` 手順付きのプレーンテキストへフォールバックします。

### 任意のチャネルでの同一チャット承認

execまたはプラグイン承認要求が配信可能なチャットサーフェスから発生した場合、同じチャットでデフォルトで `/approve` により承認できるようになりました。これは、既存のWeb UIおよびterminal UIフローに加えて、Slack、Matrix、Microsoft Teamsのようなチャネルにも適用されます。

この共有テキストコマンド経路は、その会話に対する通常のチャネル認証モデルを使います。発生元チャットがすでにコマンド送信と返信受信を行えるなら、承認要求を保留のままにするためだけに別個のネイティブ配信アダプターは不要です。

DiscordとTelegramも同一チャットの `/approve` をサポートしますが、これらのチャネルでは、ネイティブ承認配信が無効でも、認可には引き続き解決済みの承認者リストを使います。

Gatewayを直接呼び出すTelegramやその他のネイティブ承認クライアントでは、このフォールバックは意図的に「承認が見つからない」失敗に限定されています。実際のexec承認の拒否/エラーは、黙ってプラグイン承認として再試行されることはありません。

### ネイティブ承認配信

一部のチャネルはネイティブ承認クライアントとしても機能できます。ネイティブクライアントは、共有の同一チャット `/approve` フローに加えて、承認者DM、発生元チャットfanout、チャネル固有の対話型承認UXを追加します。

ネイティブ承認カード/ボタンが利用可能な場合、そのネイティブUIがagent向けの主要経路です。ツール結果にチャット承認が利用できない、または手動承認だけが残された経路だと示されていない限り、agentは重複したプレーンチャットの`/approve`コマンドも併せて出力するべきではありません。

一般的なモデル:

- exec承認が必要かどうかは、引き続きホストexecポリシーが決定する
- `approvals.exec` は、承認プロンプトを他のチャット宛先へ転送するかどうかを制御する
- `channels.<channel>.execApprovals` は、そのチャネルがネイティブ承認クライアントとして動作するかどうかを制御する

ネイティブ承認クライアントは、次のすべてが真の場合に、DM-first配信を自動有効化します。

- そのチャネルがネイティブ承認配信をサポートしている
- 明示的な `execApprovals.approvers` またはそのチャネルで文書化されたフォールバックソースから承認者を解決できる
- `channels.<channel>.execApprovals.enabled` が未設定、または `"auto"` である

ネイティブ承認クライアントを明示的に無効にするには `enabled: false` を設定します。承認者が解決できるときに強制的に有効にするには `enabled: true` を設定します。公開の発生元チャット配信は、引き続き `channels.<channel>.execApprovals.target` で明示的に制御します。

FAQ: [チャット承認にexec承認設定が2つあるのはなぜですか？](/help/faq#why-are-there-two-exec-approval-configs-for-chat-approvals)

- Discord: `channels.discord.execApprovals.*`
- Slack: `channels.slack.execApprovals.*`
- Telegram: `channels.telegram.execApprovals.*`

これらのネイティブ承認クライアントは、共有の同一チャット `/approve` フローと共有承認ボタンの上に、DMルーティングとオプションのチャネルfanoutを追加します。

共有される動作:

- Slack、Matrix、Microsoft Teams、および同様の配信可能なチャットは、同一チャット `/approve` に通常のチャネル認証モデルを使う
- ネイティブ承認クライアントが自動有効化されると、デフォルトのネイティブ配信先は承認者DMになる
- DiscordとTelegramでは、解決済み承認者だけが承認または拒否できる
- Discord承認者は、明示的（`execApprovals.approvers`）または `commands.ownerAllowFrom` から推定できる
- Telegram承認者は、明示的（`execApprovals.approvers`）または既存のowner設定（`allowFrom`、およびサポートされる場合はダイレクトメッセージの`defaultTo`）から推定できる
- Slack承認者は、明示的（`execApprovals.approvers`）または `commands.ownerAllowFrom` から推定できる
- Slackネイティブボタンは承認idのkindを保持するため、`plugin:` idは2つ目のSlackローカルフォールバック層なしでプラグイン承認へ解決できる
- MatrixのネイティブDM/チャネルルーティングとリアクションショートカットは、exec承認とプラグイン承認の両方を扱う。プラグイン認可は引き続き `channels.matrix.dm.allowFrom` から来る
- 要求者が承認者である必要はない
- 発生元チャットがすでにコマンドと返信をサポートしている場合、そのチャットから直接 `/approve` で承認できる
- ネイティブDiscord承認ボタンは承認id kindでルーティングする: `plugin:` idは直接プラグイン承認へ、それ以外はすべてexec承認へ進む
- ネイティブTelegram承認ボタンは、`/approve` と同じ限定的なexec-to-pluginフォールバックに従う
- ネイティブ `target` が発生元チャット配信を有効にすると、承認プロンプトにはコマンドテキストが含まれる
- 保留中のexec承認はデフォルトで30分後に期限切れになる
- operator UIまたは設定済み承認クライアントのどれも要求を受け付けられない場合、プロンプトは `askFallback` へフォールバックする

Telegramのデフォルトは承認者DM（`target: "dm"`）です。承認プロンプトを発生元のTelegramチャット/トピックにも表示したい場合は、`channel` または `both` に切り替えられます。Telegramフォーラムトピックでは、OpenClawは承認プロンプトと承認後フォローアップの両方でトピックを保持します。

参照:

- [Discord](/channels/discord)
- [Telegram](/channels/telegram)

### macOS IPCフロー
__OC_I18N_900009__
セキュリティに関する注意:

- Unixソケットモードは `0600`、トークンは `exec-approvals.json` に保存される。
- 同一UIDピアチェック。
- Challenge/response（nonce + HMACトークン + リクエストハッシュ）+ 短いTTL。

## システムイベント

execライフサイクルは、システムメッセージとして表示されます。

- `Exec running`（コマンドが実行中通知しきい値を超えた場合のみ）
- `Exec finished`
- `Exec denied`

これらは、nodeがイベントを報告した後にagentのセッションへ投稿されます。  
Gateway hostのexec承認も、コマンド完了時に同じライフサイクルイベントを出します（しきい値より長く実行中の場合はオプションで実行中イベントも出します）。  
承認ゲート付きexecは、関連付けしやすいように、これらのメッセージで承認idを `runId` として再利用します。

## 拒否された承認時の挙動

非同期exec承認が拒否された場合、OpenClawはagentがそのセッション内で同じコマンドの過去の実行結果を再利用するのを防ぎます。  
拒否理由は、コマンド出力が利用できないことを明示するガイダンス付きで渡されます。これにより、agentが新しい出力があると主張したり、以前に成功した実行の古い結果を使って拒否されたコマンドを繰り返したりするのを防ぎます。

## 影響

- **full** は強力です。可能な限りallowlistを優先してください。
- **ask** を使うと、高速に承認しつつ利用者が状況を把握できます。
- agentごとのallowlistにより、あるagentの承認が他のagentへ漏れるのを防げます。
- 承認は、**認可された送信者**からのホストexec要求にのみ適用されます。認可されていない送信者は `/exec` を発行できません。
- `/exec security=full` は認可済みoperator向けのセッションレベル便宜機能であり、設計上承認をスキップします。  
  ホストexecを強制的にブロックしたい場合は、承認securityを `deny` に設定するか、ツールポリシーで `exec` ツールを拒否してください。

関連:

- [Exec tool](/ja-JP/tools/exec)
- [Elevated mode](/ja-JP/tools/elevated)
- [Skills](/ja-JP/tools/skills)

## 関連

- [Exec](/ja-JP/tools/exec) — シェルコマンド実行ツール
- [Sandboxing](/ja-JP/gateway/sandboxing) — サンドボックスモードとワークスペースアクセス
- [Security](/ja-JP/gateway/security) — セキュリティモデルとハードニング
- [Sandbox vs Tool Policy vs Elevated](/ja-JP/gateway/sandbox-vs-tool-policy-vs-elevated) — それぞれをいつ使うか
