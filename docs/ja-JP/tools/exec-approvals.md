---
read_when:
    - exec 承認や allowlist を設定する場合
    - macOS アプリで exec 承認 UX を実装する場合
    - sandbox 脱出プロンプトとその影響を確認する場合
summary: exec 承認、allowlist、sandbox 脱出プロンプト
title: Exec 承認
x-i18n:
    generated_at: "2026-04-08T02:21:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6041929185bab051ad873cc4822288cb7d6f0470e19e7ae7a16b70f76dfc2cd9
    source_path: tools/exec-approvals.md
    workflow: 15
---

# Exec 承認

Exec 承認は、sandbox 化されたエージェントが実ホスト（`gateway` または `node`）上で
コマンドを実行できるようにするための **companion app / node host のガードレール** です。安全インターロックのようなものと考えてください:
コマンドは、ポリシー + allowlist + （任意の）ユーザー承認のすべてが一致した場合にのみ許可されます。
Exec 承認は、ツールポリシーや elevated gating に **追加で** 適用されます（elevated が `full` に設定されている場合は承認をスキップします）。
実効ポリシーは `tools.exec.*` と承認デフォルトの **より厳しい方** です。承認フィールドが省略されている場合は、`tools.exec` の値が使われます。
host exec は、そのマシン上のローカル承認状態も使用します。ホストローカルの
`~/.openclaw/exec-approvals.json` に `ask: "always"` があると、セッションや設定のデフォルトが `ask: "on-miss"` を要求していても、引き続き毎回プロンプトが表示されます。
要求されたポリシー、ホストポリシーのソース、および実効結果を確認するには、
`openclaw approvals get`、`openclaw approvals get --gateway`、または
`openclaw approvals get --node <id|name|ip>` を使用してください。

companion app UI が **利用できない** 場合、プロンプトを必要とする要求はすべて
**ask fallback**（デフォルト: deny）によって処理されます。

ネイティブのチャット承認クライアントは、保留中の承認メッセージにチャネル固有の操作も
表示できます。たとえば Matrix は、承認プロンプトにリアクションショートカット
（`✅` は一度だけ許可、`❌` は拒否、利用可能な場合は `♾️` で常に許可）を追加しつつ、
フォールバックとしてメッセージ内の `/approve ...` コマンドも残せます。

## 適用される場所

Exec 承認は、実行ホスト上でローカルに強制されます。

- **gateway host** → gateway マシン上の `openclaw` プロセス
- **node host** → node runner（macOS companion app または headless node host）

信頼モデルに関する注意:

- Gateway 認証済みの呼び出し元は、その Gateway の信頼されたオペレーターです。
- ペアリング済み node は、その trusted operator capability を node host に拡張します。
- Exec 承認は、誤実行のリスクを減らしますが、ユーザー単位の認証境界ではありません。
- 承認済みの node-host 実行では、canonical な実行コンテキスト、すなわち canonical cwd、正確な argv、存在する場合の env
  バインディング、および該当する場合の固定された実行ファイルパスが結び付けられます。
- シェルスクリプトや、インタープリター / ランタイムによる直接ファイル実行については、OpenClaw は
  1 つの具体的なローカルファイル operand も結び付けようとします。承認後から実行前の間にその結び付けられたファイルが変化した場合、
  変更後の内容を実行するのではなく、その実行は拒否されます。
- このファイルバインディングは、意図的に best-effort であり、すべての
  インタープリター / ランタイムローダーパスに対する完全な意味論モデルではありません。承認モードで
  結び付けるべき具体的なローカルファイルを正確に 1 つ特定できない場合、完全にカバーしているふりをするのではなく、
  承認ベースの実行を発行すること自体を拒否します。

macOS の分割構成:

- **node host service** は `system.run` をローカル IPC 経由で **macOS app** に転送します。
- **macOS app** は承認を強制し、UI コンテキストでコマンドを実行します。

## 設定と保存場所

承認は、実行ホスト上のローカル JSON ファイルに保存されます。

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

## 承認不要の「YOLO」モード

承認プロンプトなしで host exec を実行したい場合は、**両方** のポリシーレイヤーを開く必要があります。

- OpenClaw 設定内の要求された exec ポリシー（`tools.exec.*`）
- `~/.openclaw/exec-approvals.json` 内の host-local approvals ポリシー

これは現在、明示的に厳しくしない限り、デフォルトの host 動作です。

- `tools.exec.security`: `gateway` / `node` 上では `full`
- `tools.exec.ask`: `off`
- host `askFallback`: `full`

重要な違い:

- `tools.exec.host=auto` は exec の実行場所を選びます。利用可能なら sandbox、そうでなければ gateway。
- YOLO は host exec の承認方法を選びます。`security=full` と `ask=off` です。
- YOLO モードでは、OpenClaw は、設定済み host exec ポリシーの上に、別個のヒューリスティックなコマンド難読化承認ゲートを追加しません。
- `auto` は、sandbox 化されたセッションから gateway へのルーティングを無条件の上書きにするものではありません。呼び出し単位の `host=node` 要求は `auto` から許可され、`host=gateway` は sandbox ランタイムが有効でない場合にのみ `auto` から許可されます。安定した non-auto のデフォルトが必要なら、`tools.exec.host` を設定するか、`/exec host=...` を明示的に使ってください。

より保守的な設定にしたい場合は、どちらかのレイヤーを `allowlist` / `on-miss`
または `deny` に戻してください。

gateway-host で永続的に「never prompt」にする設定:

```bash
openclaw config set tools.exec.host gateway
openclaw config set tools.exec.security full
openclaw config set tools.exec.ask off
openclaw gateway restart
```

次に、ホスト承認ファイルも一致するよう設定します。

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

node host の場合は、代わりにその node に同じ承認ファイルを適用してください。

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

セッション限定のショートカット:

- `/exec security=full ask=off` は現在のセッションだけを変更します。
- `/elevated full` は緊急時用のショートカットで、そのセッションでは exec 承認もスキップします。

ホスト承認ファイルの方が設定より厳しいままである場合、より厳しいホストポリシーが引き続き優先されます。

## ポリシーのつまみ

### Security (`exec.security`)

- **deny**: すべての host exec 要求をブロックします。
- **allowlist**: allowlist に含まれるコマンドのみ許可します。
- **full**: すべて許可します（elevated と同等）。

### Ask (`exec.ask`)

- **off**: プロンプトを一切表示しません。
- **on-miss**: allowlist に一致しない場合のみプロンプトを表示します。
- **always**: すべてのコマンドでプロンプトを表示します。
- 実効 ask モードが `always` の場合、`allow-always` の durable trust でもプロンプトは抑止されません

### Ask fallback (`askFallback`)

プロンプトが必要なのに UI に到達できない場合は、fallback が決定します。

- **deny**: ブロックします。
- **allowlist**: allowlist に一致する場合のみ許可します。
- **full**: 許可します。

### インラインインタープリター eval の強化 (`tools.exec.strictInlineEval`)

`tools.exec.strictInlineEval=true` の場合、OpenClaw は、インタープリターバイナリ自体が allowlist に入っていても、
インラインコード eval 形式を承認専用として扱います。

例:

- `python -c`
- `node -e`, `node --eval`, `node -p`
- `ruby -e`
- `perl -e`, `perl -E`
- `php -r`
- `lua -e`
- `osascript -e`

これは、1 つの安定したファイル operand にきれいに対応しないインタープリターローダーに対する defense-in-depth です。strict モードでは:

- これらのコマンドは引き続き明示的な承認が必要です。
- `allow-always` でも、それらの新しい allowlist エントリは自動的には永続化されません。

## Allowlist（エージェント単位）

Allowlists は **エージェント単位** です。複数のエージェントが存在する場合は、macOS app で
編集中のエージェントを切り替えてください。パターンは **大文字小文字を区別しない glob 一致** です。
パターンは **バイナリパス** に解決される必要があります（basename のみのエントリは無視されます）。
旧来の `agents.default` エントリは、ロード時に `agents.main` へ移行されます。
`echo ok && pwd` のようなシェルチェーンでも、トップレベルの各セグメントがすべて allowlist ルールを満たす必要があります。

例:

- `~/Projects/**/bin/peekaboo`
- `~/.local/bin/*`
- `/opt/homebrew/bin/rg`

各 allowlist エントリは次を追跡します。

- **id** UI 上の識別に使う安定した UUID（任意）
- **last used** タイムスタンプ
- **last used command**
- **last resolved path**

## Skills の CLI を自動許可

**Auto-allow skill CLIs** が有効な場合、既知の Skills で参照される実行ファイルは
node 上で allowlist 済みとして扱われます（macOS node または headless node host）。これは
Gateway RPC 経由の `skills.bins` を使ってスキルの bin 一覧を取得します。厳密な手動 allowlist が必要な場合は無効にしてください。

重要な信頼に関する注意:

- これは、手動のパス allowlist エントリとは別の **暗黙的な利便性 allowlist** です。
- これは、Gateway と node が同じ信頼境界にある trusted operator 環境を想定しています。
- 厳密な明示的信頼が必要なら、`autoAllowSkills: false` のままにして、手動のパス allowlist エントリだけを使ってください。

## Safe bins（stdin 専用）

`tools.exec.safeBins` は、明示的な allowlist エントリなしでも allowlist モードで実行できる、
**stdin 専用** のバイナリ（たとえば `cut`）の小さな一覧を定義します。safe bins は
位置引数のファイル引数や path 的なトークンを拒否するため、入力ストリームに対してのみ動作できます。
これは一般的な信頼リストではなく、ストリームフィルター向けの限定的な高速経路として扱ってください。
インタープリターやランタイムのバイナリ（たとえば `python3`、`node`、`ruby`、`bash`、`sh`、`zsh`）を `safeBins` に追加しては **いけません**。
コードを評価できる、サブコマンドを実行できる、または設計上ファイルを読めるコマンドについては、
明示的な allowlist エントリを優先し、承認プロンプトも有効のままにしてください。
カスタム safe bins は `tools.exec.safeBinProfiles.<bin>` に明示的なプロファイルを定義しなければなりません。
バリデーションは argv の形だけから決定論的に行われます（ホストファイルシステム上の存在確認は行いません）。これにより、
許可 / 拒否の違いからファイル存在オラクルのような振る舞いが生じるのを防ぎます。
デフォルトの safe bins では、ファイル指向オプションは拒否されます（たとえば `sort -o`、`sort --output`、
`sort --files0-from`、`sort --compress-program`、`sort --random-source`、
`sort --temporary-directory`/`-T`、`wc --files0-from`、`jq -f/--from-file`、
`grep -f/--file`）。
safe bins は、stdin 専用の動作を崩すオプションについても、バイナリごとの明示的なフラグポリシーを強制します
（たとえば `sort -o/--output/--compress-program` や grep の再帰フラグ）。
long option は safe-bin モードでは fail-closed で検証されます。不明なフラグや曖昧な
省略形は拒否されます。
safe-bin プロファイルで拒否されるフラグ:

[//]: # "SAFE_BIN_DENIED_FLAGS:START"

- `grep`: `--dereference-recursive`, `--directories`, `--exclude-from`, `--file`, `--recursive`, `-R`, `-d`, `-f`, `-r`
- `jq`: `--argfile`, `--from-file`, `--library-path`, `--rawfile`, `--slurpfile`, `-L`, `-f`
- `sort`: `--compress-program`, `--files0-from`, `--output`, `--random-source`, `--temporary-directory`, `-T`, `-o`
- `wc`: `--files0-from`

[//]: # "SAFE_BIN_DENIED_FLAGS:END"

safe bins は、実行時にも argv トークンを **リテラルテキスト** として扱うことを強制します
（stdin 専用セグメントでは glob 展開も `$VARS` 展開も行いません）。そのため `*` や `$HOME/...` のようなパターンを使って
ファイル読み取りを持ち込むことはできません。
safe bins は、信頼されたバイナリディレクトリ（システムデフォルト + 任意の
`tools.exec.safeBinTrustedDirs`）から解決される必要もあります。`PATH` エントリが自動で信頼されることはありません。
デフォルトの信頼済み safe-bin ディレクトリは意図的に最小限です: `/bin`、`/usr/bin`。
safe-bin 実行ファイルがパッケージマネージャー / ユーザーパス（たとえば
`/opt/homebrew/bin`、`/usr/local/bin`、`/opt/local/bin`、`/snap/bin`）にある場合は、それらを明示的に
`tools.exec.safeBinTrustedDirs` に追加してください。
シェルチェーンやリダイレクトは、allowlist モードで自動許可されません。

シェルチェーン（`&&`、`||`、`;`）は、トップレベルの各セグメントが allowlist を満たす場合に許可されます
（safe bins やスキル自動許可を含む）。リダイレクトは allowlist モードでは引き続き未対応です。
コマンド置換（`$()` / backticks）は allowlist 解析中に拒否され、double quotes 内でも拒否されます。リテラルな `$()` テキストが必要なら
single quotes を使ってください。
macOS companion-app 承認では、シェル制御または展開構文
（`&&`、`||`、`;`、`|`、`` ` ``、`$`、`<`、`>`、`(`、`)`）を含む生のシェルテキストは、
シェルバイナリ自体が allowlist に入っていない限り、allowlist miss として扱われます。
シェルラッパー（`bash|sh|zsh ... -c/-lc`）では、要求スコープの env 上書きは、小さな明示的 allowlist
（`TERM`、`LANG`、`LC_*`、`COLORTERM`、`NO_COLOR`、`FORCE_COLOR`）に縮小されます。
allowlist モードでの allow-always 判断では、既知のディスパッチラッパー
（`env`、`nice`、`nohup`、`stdbuf`、`timeout`）は、ラッパーパスではなく内部の実行ファイルパスを永続化します。シェル多重化バイナリ
（`busybox`、`toybox`）も、シェル applet（`sh`、`ash` など）では展開され、
多重化バイナリではなく内部の実行ファイルが永続化されます。ラッパーまたは
多重化バイナリを安全に展開できない場合、allowlist エントリは自動的には永続化されません。
`python3` や `node` のようなインタープリターを allowlist に入れる場合でも、インライン eval が明示承認を必要とするように
`tools.exec.strictInlineEval=true` を推奨します。strict モードでは、`allow-always` でも無害なインタープリター / スクリプト呼び出しは永続化できますが、インライン eval の運び手は自動では永続化されません。

デフォルトの safe bins:

[//]: # "SAFE_BIN_DEFAULTS:START"

`cut`, `uniq`, `head`, `tail`, `tr`, `wc`

[//]: # "SAFE_BIN_DEFAULTS:END"

`grep` と `sort` はデフォルト一覧には含まれません。opt in する場合でも、
非 stdin ワークフローには明示的な allowlist エントリを維持してください。
safe-bin モードの `grep` では、パターンは `-e` / `--regexp` で指定してください。位置引数のパターン形式は
拒否されるため、曖昧な位置引数としてファイル operand を紛れ込ませることはできません。

### Safe bins と allowlist の違い

| 話題 | `tools.exec.safeBins` | allowlist (`exec-approvals.json`) |
| ---------------- | ------------------------------------------------------ | ------------------------------------------------------------ |
| 目的 | 限定的な stdin フィルターを自動許可 | 特定の実行ファイルを明示的に信頼 |
| 一致方式 | 実行ファイル名 + safe-bin の argv ポリシー | 解決済み実行ファイルパスの glob パターン |
| 引数の範囲 | safe-bin プロファイルとリテラルトークン規則で制限 | パスマッチのみ。引数はそれ以外では利用者の責任 |
| 典型例 | `head`, `tail`, `tr`, `wc` | `jq`, `python3`, `node`, `ffmpeg`, カスタム CLI |
| 最適な用途 | パイプライン内の低リスクなテキスト変換 | より広い動作や副作用を持つ任意のツール |

設定場所:

- `safeBins` は設定から取得されます（`tools.exec.safeBins` またはエージェント単位の `agents.list[].tools.exec.safeBins`）。
- `safeBinTrustedDirs` は設定から取得されます（`tools.exec.safeBinTrustedDirs` またはエージェント単位の `agents.list[].tools.exec.safeBinTrustedDirs`）。
- `safeBinProfiles` は設定から取得されます（`tools.exec.safeBinProfiles` またはエージェント単位の `agents.list[].tools.exec.safeBinProfiles`）。エージェント単位のプロファイルキーはグローバルキーを上書きします。
- allowlist エントリは、ホストローカルの `~/.openclaw/exec-approvals.json` の `agents.<id>.allowlist` に保存されます（または Control UI / `openclaw approvals allowlist ...` 経由）。
- `openclaw security audit` は、インタープリター / ランタイムの bin が明示プロファイルなしで `safeBins` に含まれている場合、`tools.exec.safe_bins_interpreter_unprofiled` で警告します。
- `openclaw doctor --fix` は、足りないカスタム `safeBinProfiles.<bin>` エントリを `{}` としてひな形作成できます（その後で確認して厳しくしてください）。インタープリター / ランタイムの bin は自動ひな形作成されません。

カスタムプロファイルの例:
__OC_I18N_900004__
`jq` を明示的に `safeBins` に opt in した場合でも、OpenClaw は safe-bin
モードで `env` 組み込みを拒否します。これにより `jq -n env` でホストプロセスの環境をダンプすることは、
明示的な allowlist パスまたは承認プロンプトなしにはできません。

## Control UI での編集

**Control UI → Nodes → Exec approvals** カードを使って、デフォルト、エージェント単位の
上書き、および allowlist を編集してください。スコープ（Defaults または agent）を選び、
ポリシーを調整し、allowlist パターンを追加 / 削除してから **Save** を押します。UI には
各パターンごとの **last used** metadata が表示されるため、一覧を整理しやすくなっています。

ターゲットセレクターでは **Gateway**（ローカル承認）または **Node** を選びます。Node は
`system.execApprovals.get/set` を広告している必要があります（macOS app または headless node host）。
node がまだ exec approvals を広告していない場合は、そのローカルの
`~/.openclaw/exec-approvals.json` を直接編集してください。

CLI: `openclaw approvals` は gateway と node の両方の編集をサポートしています（[Approvals CLI](/cli/approvals) を参照）。

## 承認フロー

プロンプトが必要な場合、gateway は `exec.approval.requested` を operator client にブロードキャストします。
Control UI と macOS app は `exec.approval.resolve` でこれを処理し、その後 gateway は
承認された要求を node host に転送します。

`host=node` の場合、承認要求には canonical な `systemRunPlan` ペイロードが含まれます。gateway は
承認済み `system.run` 要求を転送するとき、その plan を authoritative な command / cwd / session コンテキストとして使用します。

これは async 承認の遅延において重要です。

- node exec パスは、最初に 1 つの canonical plan を準備します
- 承認レコードには、その plan とバインディング metadata が保存されます
- 一度承認されると、最終的に転送される `system.run` 呼び出しは、
  後からの呼び出し元編集を信頼するのではなく、保存済み plan を再利用します
- 承認要求作成後に呼び出し元が `command`、`rawCommand`、`cwd`、`agentId`、または
  `sessionKey` を変更した場合、gateway は承認不一致としてその転送実行を拒否します

## インタープリター / ランタイムコマンド

承認ベースのインタープリター / ランタイム実行は、意図的に保守的です。

- 正確な argv / cwd / env コンテキストは常に結び付けられます。
- 直接シェルスクリプト形式と直接ランタイムファイル形式は、1 つの具体的なローカル
  ファイルスナップショットへの best-effort バインディングが行われます。
- それでも 1 つの直接ローカルファイルに解決される一般的なパッケージマネージャーラッパー形式（たとえば
  `pnpm exec`、`pnpm node`、`npm exec`、`npx`）は、バインディング前に展開されます。
- OpenClaw がインタープリター / ランタイムコマンドに対して、正確に 1 つの具体的ローカルファイルを特定できない場合
  （たとえば package script、eval 形式、ランタイム固有のローダーチェーン、または曖昧な複数ファイル形式）、
  意味論的カバレッジがあると主張するのではなく、承認ベースの実行は拒否されます。
- そのようなワークフローでは、sandbox 化、別の host 境界、または
  より広いランタイム意味論をオペレーターが受け入れる明示的 trusted
  allowlist / full ワークフローを優先してください。

承認が必要な場合、exec ツールは承認 id を返してすぐに終了します。後で発生する system event
（`Exec finished` / `Exec denied`）との対応付けにはその id を使用してください。タイムアウトまでに決定が届かなければ、
その要求は承認タイムアウトとして扱われ、拒否理由として表面化されます。

### followup 配信動作

承認済み async exec が終了すると、OpenClaw は同じセッションに followup の `agent` ターンを送信します。

- 有効な外部配信ターゲットが存在する場合（配信可能なチャネルとターゲット `to`）、followup 配信はそのチャネルを使います。
- 外部ターゲットのない webchat 専用または internal-session フローでは、followup 配信はセッション内のみのままです（`deliver: false`）。
- 呼び出し元が明示的に strict external delivery を要求していて、解決可能な外部チャネルがない場合、要求は `INVALID_REQUEST` で失敗します。
- `bestEffortDeliver` が有効で、外部チャネルを解決できない場合、失敗する代わりに配信はセッション内のみに格下げされます。

確認ダイアログには次が含まれます。

- command + args
- cwd
- agent id
- 解決済み実行ファイルパス
- host + policy metadata

操作:

- **Allow once** → 今回だけ実行
- **Always allow** → allowlist に追加して実行
- **Deny** → ブロック

## チャットチャネルへの承認転送

exec 承認プロンプトは任意のチャットチャネル（プラグインチャネルを含む）へ転送でき、
`/approve` で承認できます。これは通常の outbound delivery pipeline を使います。

設定:
__OC_I18N_900005__
チャットでの返信:
__OC_I18N_900006__
`/approve` コマンドは exec 承認と plugin 承認の両方を処理します。ID が保留中の exec 承認に一致しない場合、
自動的に plugin 承認も確認します。

### Plugin 承認の転送

plugin 承認の転送は exec 承認と同じ delivery pipeline を使いますが、
`approvals.plugin` 配下に独立した設定を持ちます。一方を有効 / 無効にしても他方には影響しません。
__OC_I18N_900007__
設定形状は `approvals.exec` と同一です。`enabled`、`mode`、`agentFilter`、
`sessionFilter`、`targets` は同じように機能します。

共有インタラクティブ返信をサポートするチャネルでは、exec と
plugin 承認の両方で同じ承認ボタンが表示されます。共有インタラクティブ UI がないチャネルでは、
`/approve` 手順付きのプレーンテキストにフォールバックします。

### 任意のチャネルでの同一チャット承認

exec または plugin の承認要求が、配信可能なチャットサーフェスから発生した場合、
同じチャットでデフォルトで `/approve` を使って承認できるようになりました。これは Slack、Matrix、Microsoft Teams など、
既存の Web UI と terminal UI フローに加えたチャネルにも適用されます。

この共有テキストコマンド経路は、その会話の通常のチャネル認証モデルを使います。発生元のチャットが
すでにコマンド送信と返信受信を行えるなら、承認要求を保留にするためだけに
別個のネイティブ delivery adapter は不要です。

Discord と Telegram も同一チャットの `/approve` をサポートしていますが、
それらのチャネルでは、ネイティブ承認配信が無効でも、認可には引き続き解決済み approver 一覧が使われます。

Telegram など、Gateway を直接呼び出すネイティブ承認クライアントでは、
このフォールバックは意図的に「approval not found」失敗に限定されています。実際の
exec 承認の拒否 / エラーは、黙って plugin 承認として再試行されることはありません。

### ネイティブ承認配信

一部のチャネルはネイティブ承認クライアントとしても動作できます。ネイティブクライアントは、
共有の同一チャット `/approve` フローに加えて、approver DM、発生元チャットへの fanout、
チャネル固有のインタラクティブな承認 UX を追加します。

ネイティブの承認カード / ボタンが利用可能な場合、そのネイティブ UI が
エージェント向けの主経路です。ツール結果がチャット承認を利用できない、または
手動承認が唯一残る経路であると示していない限り、エージェントは重複するプレーンチャットの
`/approve` コマンドを併記すべきではありません。

汎用モデル:

- host exec ポリシーは、exec 承認が必要かどうかを引き続き決定します
- `approvals.exec` は、他のチャット宛先への承認プロンプト転送を制御します
- `channels.<channel>.execApprovals` は、そのチャネルがネイティブ承認クライアントとして動作するかを制御します

ネイティブ承認クライアントは、以下のすべてが真である場合に、DM-first 配信を自動有効化します。

- そのチャネルがネイティブ承認配信をサポートしている
- 明示的な `execApprovals.approvers` またはそのチャネルの文書化された
  fallback source から approver を解決できる
- `channels.<channel>.execApprovals.enabled` が未設定または `"auto"` である

ネイティブ承認クライアントを明示的に無効にするには `enabled: false` を設定してください。approver が解決される場合に
強制的に有効にするには `enabled: true` を設定してください。公開の発生元チャット配信は
`channels.<channel>.execApprovals.target` によって明示的に制御されます。

FAQ: [チャット承認用に exec 承認設定が 2 つあるのはなぜですか？](/help/faq#why-are-there-two-exec-approval-configs-for-chat-approvals)

- Discord: `channels.discord.execApprovals.*`
- Slack: `channels.slack.execApprovals.*`
- Telegram: `channels.telegram.execApprovals.*`

これらのネイティブ承認クライアントは、共有の
同一チャット `/approve` フローと共有承認ボタンに加えて、DM ルーティングと任意のチャネル fanout を追加します。

共有動作:

- Slack、Matrix、Microsoft Teams などの配信可能なチャットでは、
  同一チャット `/approve` に通常のチャネル認証モデルが使われます
- ネイティブ承認クライアントが自動有効化された場合、デフォルトのネイティブ配信先は approver DM です
- Discord と Telegram では、解決済み approver だけが承認または拒否できます
- Discord の approver は、明示的（`execApprovals.approvers`）または `commands.ownerAllowFrom` から推測できます
- Telegram の approver は、明示的（`execApprovals.approvers`）または既存の owner 設定
  （`allowFrom`、およびサポートされる場合は direct-message の `defaultTo`）から推測できます
- Slack の approver は、明示的（`execApprovals.approvers`）または `commands.ownerAllowFrom` から推測できます
- Slack のネイティブボタンは承認 id の種類を保持するため、`plugin:` id は
  2 段目の Slack ローカルフォールバック層なしで plugin 承認に解決できます
- Matrix のネイティブ DM / channel ルーティングとリアクションショートカットは exec と plugin 承認の両方を扱います。
  plugin の認可は引き続き `channels.matrix.dm.allowFrom` に由来します
- 要求者自身が approver である必要はありません
- 発生元チャットがすでにコマンドと返信をサポートしていれば、発生元チャットは `/approve` で直接承認できます
- ネイティブ Discord 承認ボタンは承認 id の種類でルーティングします。`plugin:` id は
  直接 plugin 承認に進み、それ以外はすべて exec 承認に進みます
- ネイティブ Telegram 承認ボタンは、`/approve` と同じ限定的な exec→plugin フォールバックに従います
- ネイティブ `target` が発生元チャット配信を有効にすると、承認プロンプトにはコマンドテキストが含まれます
- 保留中の exec 承認はデフォルトで 30 分後に期限切れになります
- オペレーター UI や設定済み承認クライアントのいずれも要求を受け取れない場合、プロンプトは `askFallback` にフォールバックします

Telegram のデフォルトは approver DM（`target: "dm"`）です。承認プロンプトも発生元の Telegram チャット / topic に
表示したい場合は、`channel` または `both` に切り替えられます。Telegram forum
topics では、OpenClaw は承認プロンプトと承認後の follow-up の両方で topic を維持します。

参照:

- [Discord](/channels/discord)
- [Telegram](/channels/telegram)

### macOS IPC フロー
__OC_I18N_900008__
セキュリティに関する注意:

- Unix socket のモードは `0600`、token は `exec-approvals.json` に保存されます。
- 同一 UID の peer チェック。
- challenge/response（nonce + HMAC token + request hash）+ 短い TTL。

## システムイベント

Exec のライフサイクルは system message として表面化されます。

- `Exec running`（コマンドが running notice threshold を超えた場合のみ）
- `Exec finished`
- `Exec denied`

これらは、node がイベントを報告した後、エージェントのセッションに投稿されます。
gateway-host exec 承認でも、コマンド終了時（および任意で、しきい値より長く動作した場合の実行中）に同じライフサイクルイベントが発行されます。
承認ゲート付き exec では、対応付けを容易にするため、これらのメッセージ内の `runId` として承認 id が再利用されます。

## 拒否された承認の動作

async exec 承認が拒否された場合、OpenClaw は、セッション内で以前に同じコマンドを実行した
古い結果をエージェントが再利用できないようにします。拒否理由は、利用可能なコマンド出力がないという明示的なガイダンス付きで渡されるため、
新しい出力があるかのように主張したり、以前の成功実行の古い結果を使って拒否されたコマンドを繰り返したりするのを防ぎます。

## 影響

- **full** は強力です。可能な限り allowlist を優先してください。
- **ask** を使うと、高速な承認を維持しつつ、人間がループに入れます。
- エージェント単位の allowlist により、あるエージェントの承認が他のエージェントへ漏れるのを防げます。
- 承認は、**認可された送信者** からの host exec 要求にのみ適用されます。未認可の送信者は `/exec` を発行できません。
- `/exec security=full` は認可済みオペレーター向けのセッション単位の利便機能であり、設計上承認をスキップします。
  host exec を完全に禁止したい場合は、承認 security を `deny` に設定するか、ツールポリシーで `exec` ツールを拒否してください。

関連:

- [Exec tool](/ja-JP/tools/exec)
- [Elevated mode](/ja-JP/tools/elevated)
- [Skills](/ja-JP/tools/skills)

## 関連

- [Exec](/ja-JP/tools/exec) — シェルコマンド実行ツール
- [Sandboxing](/ja-JP/gateway/sandboxing) — sandbox モードとワークスペースアクセス
- [Security](/ja-JP/gateway/security) — セキュリティモデルとハードニング
- [Sandbox vs Tool Policy vs Elevated](/ja-JP/gateway/sandbox-vs-tool-policy-vs-elevated) — それぞれをいつ使うか
