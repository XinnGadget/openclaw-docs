---
read_when:
    - exec承認または許可リストを設定している
    - macOSアプリでexec承認UXを実装している
    - サンドボックス脱出プロンプトとその影響を確認している
summary: exec承認、許可リスト、およびサンドボックス脱出プロンプト
title: Exec承認
x-i18n:
    generated_at: "2026-04-06T03:14:49Z"
    model: gpt-5.4
    provider: openai
    source_hash: 39e91cd5c7615bdb9a6b201a85bde7514327910f6f12da5a4b0532bceb229c22
    source_path: tools/exec-approvals.md
    workflow: 15
---

# Exec承認

Exec承認は、サンドボックス化されたエージェントが実ホスト（`gateway`または`node`）上でコマンドを実行できるようにするための**companion app / node hostガードレール**です。安全インターロックのようなものと考えてください。コマンドは、ポリシー + 許可リスト + （任意の）ユーザー承認のすべてが同意した場合にのみ許可されます。
Exec承認は、ツールポリシーおよび昇格ゲーティングに**追加**されるものです（ただし、elevatedが`full`に設定されている場合は承認をスキップします）。実効ポリシーは`tools.exec.*`と承認デフォルトの**より厳しい方**です。承認フィールドが省略された場合は、`tools.exec`の値が使用されます。
ホストexecは、そのマシン上のローカル承認状態も使用します。
`~/.openclaw/exec-approvals.json`内のホストローカル`ask: "always"`は、セッションまたは設定デフォルトが`ask: "on-miss"`を要求していても、引き続き毎回プロンプトを表示します。
要求されたポリシー、ホストポリシーソース、および実効結果を確認するには、`openclaw approvals get`、`openclaw approvals get --gateway`、または
`openclaw approvals get --node <id|name|ip>`を使用してください。

companion app UIが**利用できない**場合、プロンプトが必要な要求はすべて
**ask fallback**（デフォルト: deny）で解決されます。

ネイティブチャット承認クライアントは、保留中の承認メッセージ上にチャネル固有の操作も表示できます。たとえば、Matrixは承認プロンプト上にリアクションショートカット（`✅` 一度だけ許可、`❌` 拒否、利用可能な場合は `♾️` 常に許可）を配置しつつ、フォールバックとしてメッセージ内の`/approve ...`コマンドも残せます。

## 適用される場所

Exec承認は、実行ホスト上でローカルに強制されます。

- **Gatewayホスト** → Gatewayマシン上の`openclaw`プロセス
- **ノードホスト** → ノードランナー（macOS companion appまたはヘッドレスノードホスト）

信頼モデルに関するメモ:

- Gateway認証された呼び出し元は、そのGatewayの信頼されたオペレーターです。
- ペアリング済みノードは、その信頼されたオペレーター能力をノードホストへ拡張します。
- Exec承認は偶発的な実行リスクを減らしますが、ユーザーごとの認証境界ではありません。
- 承認済みノードホスト実行は、正規の実行コンテキストを拘束します: 正規cwd、正確なargv、存在する場合のenvバインディング、および適用可能な場合の固定実行ファイルパス。
- シェルスクリプトおよび直接のインタープリター/ランタイムファイル呼び出しについて、OpenClawは1つの具体的なローカルファイルオペランドも拘束しようとします。その拘束されたファイルが承認後から実行前の間に変更された場合、その実行はドリフトした内容を実行する代わりに拒否されます。
- このファイル拘束は、意図的にベストエフォートであり、あらゆるインタープリター/ランタイムローダーパスの完全な意味モデルではありません。承認モードが正確に1つの具体的なローカルファイルを拘束できない場合、完全なカバレッジがあるふりをする代わりに、承認裏付け付き実行の発行を拒否します。

macOSの分割:

- **node host service**は、ローカルIPC経由で`system.run`を**macOS app**へ転送します。
- **macOS app**が、承認を強制し、UIコンテキストでコマンドを実行します。

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

## 承認不要の「YOLO」モード

承認プロンプトなしでホストexecを実行したい場合は、**両方**のポリシーレイヤーを開く必要があります。

- OpenClaw設定内の要求されたexecポリシー（`tools.exec.*`）
- `~/.openclaw/exec-approvals.json`内のホストローカル承認ポリシー

これは現在、明示的に厳しくしない限りデフォルトのホスト動作です。

- `tools.exec.security`: `gateway`/`node`では`full`
- `tools.exec.ask`: `off`
- ホスト`askFallback`: `full`

重要な違い:

- `tools.exec.host=auto`は、execをどこで実行するかを選びます: 利用可能ならサンドボックス、そうでなければgateway。
- YOLOは、ホストexecがどのように承認されるかを選びます: `security=full`かつ`ask=off`。
- YOLOモードでは、OpenClawは、設定されたホストexecポリシーに加えて別個のヒューリスティックなコマンド難読化承認ゲートを追加しません。
- `auto`は、サンドボックス化されたセッションからgatewayルーティングへの自由な上書きを意味しません。呼び出しごとの`host=node`要求は`auto`から許可され、`host=gateway`はサンドボックスランタイムが有効でない場合にのみ`auto`から許可されます。安定した非autoデフォルトが必要なら、`tools.exec.host`を設定するか、明示的に`/exec host=...`を使ってください。

より保守的なセットアップにしたい場合は、いずれかのレイヤーを`allowlist` / `on-miss`
または`deny`へ戻してください。

永続的なGatewayホスト「決してプロンプトを出さない」設定:

```bash
openclaw config set tools.exec.host gateway
openclaw config set tools.exec.security full
openclaw config set tools.exec.ask off
openclaw gateway restart
```

次に、ホスト承認ファイルも一致させます。

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

ノードホストの場合は、代わりにそのノードで同じ承認ファイルを適用します。

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

- `/exec security=full ask=off`は現在のセッションだけを変更します。
- `/elevated full`は、同じくそのセッションのexec承認もスキップする緊急回避ショートカットです。

ホスト承認ファイルが設定より厳しいままであれば、より厳しいホストポリシーが引き続き優先されます。

## ポリシー設定項目

### Security（`exec.security`）

- **deny**: すべてのホストexec要求をブロックします。
- **allowlist**: 許可リストにあるコマンドのみ許可します。
- **full**: すべて許可します（elevatedと同等）。

### Ask（`exec.ask`）

- **off**: プロンプトを表示しません。
- **on-miss**: 許可リストに一致しない場合のみプロンプトを表示します。
- **always**: すべてのコマンドでプロンプトを表示します。
- 実効askモードが`always`の場合、`allow-always`の永続信頼でもプロンプトは抑制されません

### Ask fallback（`askFallback`）

プロンプトが必要だが到達可能なUIがない場合、fallbackが次を決めます。

- **deny**: ブロックします。
- **allowlist**: 許可リストに一致する場合のみ許可します。
- **full**: 許可します。

### インラインインタープリターevalのハードニング（`tools.exec.strictInlineEval`）

`tools.exec.strictInlineEval=true`の場合、OpenClawは、インラインコードeval形式を、インタープリターバイナリ自体が許可リストにあっても承認専用として扱います。

例:

- `python -c`
- `node -e`, `node --eval`, `node -p`
- `ruby -e`
- `perl -e`, `perl -E`
- `php -r`
- `lua -e`
- `osascript -e`

これは、1つの安定したファイルオペランドへきれいにマップされないインタープリターローダーへの多層防御です。strictモードでは:

- これらのコマンドには引き続き明示的な承認が必要です。
- `allow-always`は、それらに対して新しい許可リストエントリーを自動永続化しません。

## 許可リスト（エージェント単位）

許可リストは**エージェント単位**です。複数のエージェントが存在する場合、macOSアプリで編集中のエージェントを切り替えてください。パターンは**大文字小文字を区別しないglob一致**です。
パターンは**バイナリパス**へ解決される必要があります（basenameのみのエントリーは無視されます）。
レガシーな`agents.default`エントリーは、読み込み時に`agents.main`へ移行されます。
`echo ok && pwd`のようなシェルチェーンでも、各トップレベルセグメントが許可リスト規則を満たす必要があります。

例:

- `~/Projects/**/bin/peekaboo`
- `~/.local/bin/*`
- `/opt/homebrew/bin/rg`

各許可リストエントリーは以下を追跡します。

- **id** UI識別に使う安定したUUID（任意）
- **last used** タイムスタンプ
- **last used command**
- **last resolved path**

## Skills CLIの自動許可

**Auto-allow skill CLIs**が有効な場合、既知のSkillsから参照される実行ファイルは、ノード（macOSノードまたはヘッドレスノードホスト）上で許可リスト済みとして扱われます。これは、Gateway RPC経由の`skills.bins`を使ってスキルbin一覧を取得します。厳格な手動許可リストだけを使いたい場合は、これを無効にしてください。

重要な信頼に関するメモ:

- これは手動パス許可リストエントリーとは別の、**暗黙の利便性許可リスト**です。
- これは、Gatewayとノードが同じ信頼境界にある信頼済みオペレーター環境向けです。
- 厳格な明示的信頼が必要な場合は、`autoAllowSkills: false`のままにし、手動パス許可リストエントリーだけを使用してください。

## Safe bins（stdin専用）

`tools.exec.safeBins`は、allowlistモードで**明示的な許可リストエントリーなしに**実行できる、小さな**stdin専用**バイナリ一覧（たとえば`cut`）を定義します。safe binsは位置ファイル引数とパス風トークンを拒否するため、受信ストリーム上でのみ動作できます。
これは一般的な信頼リストではなく、ストリームフィルター用の限定的な高速経路として扱ってください。
`python3`, `node`, `ruby`, `bash`, `sh`, `zsh`のようなインタープリターやランタイムのバイナリを`safeBins`に追加しないでください。
コマンドが設計上コード評価、サブコマンド実行、またはファイル読み取りを行える場合は、明示的な許可リストエントリーを優先し、承認プロンプトを有効のままにしてください。
カスタムsafe binsは、`tools.exec.safeBinProfiles.<bin>`に明示的なプロファイルを定義する必要があります。
検証はargv形状のみから決定論的に行われます（ホストファイルシステム存在確認なし）。これにより、allow/deny差分によるファイル存在オラクル動作を防ぎます。
デフォルトsafe binsではファイル指向オプションは拒否されます（例: `sort -o`, `sort --output`,
`sort --files0-from`, `sort --compress-program`, `sort --random-source`,
`sort --temporary-directory`/`-T`, `wc --files0-from`, `jq -f/--from-file`,
`grep -f/--file`）。
safe binsは、stdin専用動作を壊すオプションに対して、バイナリごとの明示的フラグポリシーも強制します（例: `sort -o/--output/--compress-program`およびgrepの再帰フラグ）。
長いオプションはsafe-binモードでフェイルクローズ検証されます。不明なフラグと曖昧な省略形は拒否されます。
safe-binプロファイルごとの拒否フラグ:

[//]: # "SAFE_BIN_DENIED_FLAGS:START"

- `grep`: `--dereference-recursive`, `--directories`, `--exclude-from`, `--file`, `--recursive`, `-R`, `-d`, `-f`, `-r`
- `jq`: `--argfile`, `--from-file`, `--library-path`, `--rawfile`, `--slurpfile`, `-L`, `-f`
- `sort`: `--compress-program`, `--files0-from`, `--output`, `--random-source`, `--temporary-directory`, `-T`, `-o`
- `wc`: `--files0-from`

[//]: # "SAFE_BIN_DENIED_FLAGS:END"

safe binsは、実行時にargvトークンを**リテラルテキスト**として扱うことも強制します（グロブ展開なし、`$VARS`展開なし）。そのため、`*`や`$HOME/...`のようなパターンでファイル読み取りを密輸できません。
safe binsは、信頼されたバイナリディレクトリ（システムデフォルト + 任意の`tools.exec.safeBinTrustedDirs`）から解決される必要もあります。`PATH`エントリーが自動的に信頼されることはありません。
デフォルトの信頼safe-binディレクトリは意図的に最小です: `/bin`, `/usr/bin`。
safe-bin実行ファイルがパッケージマネージャー/ユーザーパス（たとえば
`/opt/homebrew/bin`, `/usr/local/bin`, `/opt/local/bin`, `/snap/bin`）にある場合は、それらを明示的に
`tools.exec.safeBinTrustedDirs`へ追加してください。
シェルチェーンとリダイレクトは、allowlistモードで自動許可されません。

シェルチェーン（`&&`, `||`, `;`）は、すべてのトップレベルセグメントが許可リスト条件を満たす場合に許可されます
（safe binsまたはskill自動許可を含む）。リダイレクトはallowlistモードでは引き続き未対応です。
コマンド置換（`$()` / バッククォート）は、二重引用符内を含めallowlist解析中に拒否されます。リテラルの`$()`テキストが必要なら単一引用符を使用してください。
macOS companion-app承認では、シェル制御または展開構文（`&&`, `||`, `;`, `|`, `` ` ``, `$`, `<`, `>`, `(`, `)`）を含む生のシェルテキストは、シェルバイナリ自体が許可リストにない限り、allowlistミスとして扱われます。
シェルラッパー（`bash|sh|zsh ... -c/-lc`）では、リクエストスコープのenv上書きは、小さな明示的許可リスト（`TERM`, `LANG`, `LC_*`, `COLORTERM`, `NO_COLOR`, `FORCE_COLOR`）へ縮小されます。
allowlistモードでのallow-always決定では、既知のディスパッチラッパー
（`env`, `nice`, `nohup`, `stdbuf`, `timeout`）は、ラッパーパスではなく内側の実行ファイルパスを永続化します。シェルマルチプレクサー（`busybox`, `toybox`）も、シェルアプレット（`sh`, `ash`,
など）ではアンラップされ、マルチプレクサーバイナリではなく内側の実行ファイルが永続化されます。ラッパーまたはマルチプレクサーを安全にアンラップできない場合、許可リストエントリーは自動永続化されません。
`python3`や`node`のようなインタープリターを許可リストに入れる場合でも、インラインevalには明示的承認が必要になるよう`tools.exec.strictInlineEval=true`を推奨します。strictモードでは、`allow-always`は無害なインタープリター/スクリプト呼び出しを永続化できますが、インラインevalキャリアは自動永続化されません。

デフォルトsafe bins:

[//]: # "SAFE_BIN_DEFAULTS:START"

`cut`, `uniq`, `head`, `tail`, `tr`, `wc`

[//]: # "SAFE_BIN_DEFAULTS:END"

`grep`と`sort`はデフォルト一覧に含まれていません。オプトインする場合でも、
stdin以外のワークフローには明示的な許可リストエントリーを維持してください。
safe-binモードの`grep`では、パターンは`-e`/`--regexp`で指定してください。位置パターン形式は拒否されるため、ファイルオペランドを曖昧な位置引数として密輸できません。

### Safe binsと許可リストの違い

| Topic            | `tools.exec.safeBins`                              | Allowlist (`exec-approvals.json`)                     |
| ---------------- | -------------------------------------------------- | ----------------------------------------------------- |
| Goal             | 限定的なstdinフィルターを自動許可                  | 特定の実行ファイルを明示的に信頼                      |
| Match type       | 実行ファイル名 + safe-bin argvポリシー             | 解決された実行ファイルパスのglobパターン              |
| Argument scope   | safe-binプロファイルとリテラルトークン規則で制限   | パスマッチのみ。引数はそれ以外では利用者の責任        |
| Typical examples | `head`, `tail`, `tr`, `wc`                         | `jq`, `python3`, `node`, `ffmpeg`, カスタムCLI        |
| Best use         | 低リスクなテキスト変換パイプライン                 | より広い動作や副作用を持つ任意のツール                |

設定場所:

- `safeBins`は設定から取得されます（`tools.exec.safeBins`またはエージェント単位の`agents.list[].tools.exec.safeBins`）。
- `safeBinTrustedDirs`は設定から取得されます（`tools.exec.safeBinTrustedDirs`またはエージェント単位の`agents.list[].tools.exec.safeBinTrustedDirs`）。
- `safeBinProfiles`は設定から取得されます（`tools.exec.safeBinProfiles`またはエージェント単位の`agents.list[].tools.exec.safeBinProfiles`）。エージェント単位のプロファイルキーはグローバルキーを上書きします。
- 許可リストエントリーは、ホストローカルの`~/.openclaw/exec-approvals.json`の`agents.<id>.allowlist`に保存されます（またはControl UI / `openclaw approvals allowlist ...`経由）。
- `openclaw security audit`は、明示的なプロファイルなしでインタープリター/ランタイムbinが`safeBins`に現れた場合、`tools.exec.safe_bins_interpreter_unprofiled`で警告します。
- `openclaw doctor --fix`は、欠落しているカスタム`safeBinProfiles.<bin>`エントリーを`{}`として雛形生成できます（その後で確認し、より厳しくしてください）。インタープリター/ランタイムbinは自動雛形生成されません。

カスタムプロファイル例:
__OC_I18N_900004__
`jq`を明示的に`safeBins`へオプトインした場合でも、OpenClawはsafe-bin
モードで`env`ビルトインを拒否するため、`jq -n env`は明示的な許可リストパスまたは承認プロンプトなしではホストプロセス環境をダンプできません。

## Control UIでの編集

**Control UI → Nodes → Exec approvals**カードを使って、デフォルト、エージェント単位の上書き、および許可リストを編集してください。スコープ（Defaultsまたはエージェント）を選び、ポリシーを調整し、許可リストパターンを追加/削除してから、**Save**します。UIにはパターンごとの**last used**メタデータが表示されるため、一覧を整理しやすくなります。

ターゲットセレクターでは、**Gateway**（ローカル承認）または**Node**を選択します。ノードは`system.execApprovals.get/set`を広告している必要があります（macOS appまたはヘッドレスノードホスト）。
ノードがまだexec承認を広告していない場合は、そのローカル
`~/.openclaw/exec-approvals.json`を直接編集してください。

CLI: `openclaw approvals`はgatewayまたはnodeの編集をサポートします（[Approvals CLI](/cli/approvals)を参照）。

## 承認フロー

プロンプトが必要な場合、Gatewayは`exec.approval.requested`をオペレータークライアントへブロードキャストします。
Control UIとmacOSアプリはそれを`exec.approval.resolve`で解決し、続いてGatewayが承認済み要求をノードホストへ転送します。

`host=node`の場合、承認要求には正規の`systemRunPlan`ペイロードが含まれます。Gatewayは、承認済み`system.run`
要求を転送する際に、そのplanを正式なコマンド/cwd/セッションコンテキストとして使用します。

これは非同期承認の遅延に対して重要です。

- ノードexec経路は、最初に1つの正規planを準備します
- 承認レコードは、そのplanとその拘束メタデータを保存します
- 承認後、最終的に転送される`system.run`呼び出しは、後からの呼び出し元編集を信頼するのではなく、保存されたplanを再利用します
- 承認要求作成後に呼び出し元が`command`、`rawCommand`、`cwd`、`agentId`、または
  `sessionKey`を変更した場合、Gatewayはその転送実行を承認不一致として拒否します

## インタープリター/ランタイムコマンド

承認裏付け付きのインタープリター/ランタイム実行は、意図的に保守的です。

- 正確なargv/cwd/envコンテキストは常に拘束されます。
- 直接シェルスクリプトおよび直接ランタイムファイル形式は、1つの具体的なローカルファイルスナップショットへベストエフォートで拘束されます。
- 依然として1つの直接ローカルファイルへ解決される一般的なパッケージマネージャーラッパー形式（たとえば
  `pnpm exec`, `pnpm node`, `npm exec`, `npx`）は、拘束前にアンラップされます。
- OpenClawがインタープリター/ランタイムコマンドに対して正確に1つの具体的なローカルファイルを特定できない場合（たとえばパッケージスクリプト、eval形式、ランタイム固有ローダーチェーン、または曖昧な複数ファイル形式）、意味論的カバレッジがあると主張する代わりに、承認裏付け付き実行は拒否されます。
- そのようなワークフローには、サンドボックス化、別のホスト境界、またはオペレーターがより広いランタイム意味論を受け入れる明示的な信頼済み
  allowlist/fullワークフローを推奨します。

承認が必要な場合、execツールは承認idとともに即座に戻ります。そのidを使って後続のシステムイベント（`Exec finished` / `Exec denied`）を関連付けてください。タイムアウト前に決定が届かない場合、その要求は承認タイムアウトとして扱われ、拒否理由として表示されます。

### フォローアップ配信動作

承認済みの非同期execが完了した後、OpenClawは同じセッションへフォローアップの`agent`ターンを送信します。

- 有効な外部配信先（配信可能チャネル + ターゲット`to`）が存在する場合、フォローアップ配信はそのチャネルを使います。
- webchat専用または外部ターゲットのない内部セッションフローでは、フォローアップ配信はセッション限定のままです（`deliver: false`）。
- 解決可能な外部チャネルがない状態で呼び出し元が明示的に厳格な外部配信を要求した場合、その要求は`INVALID_REQUEST`で失敗します。
- `bestEffortDeliver`が有効で外部チャネルを解決できない場合、配信は失敗ではなくセッション限定へダウングレードされます。

確認ダイアログには以下が含まれます。

- command + args
- cwd
- agent id
- 解決済み実行ファイルパス
- host + policyメタデータ

アクション:

- **Allow once** → 今すぐ実行
- **Always allow** → 許可リストへ追加して実行
- **Deny** → ブロック

## チャットチャネルへの承認転送

任意のチャットチャネル（プラグインチャネルを含む）へexec承認プロンプトを転送し、
`/approve`で承認できます。これは通常の送信配信パイプラインを使用します。

設定:
__OC_I18N_900005__
チャットで返信:
__OC_I18N_900006__
`/approve`コマンドは、exec承認とプラグイン承認の両方を処理します。IDが保留中のexec承認に一致しない場合、自動的にプラグイン承認も確認します。

### プラグイン承認転送

プラグイン承認転送はexec承認と同じ配信パイプラインを使用しますが、`approvals.plugin`配下に独立した設定を持ちます。一方を有効または無効にしても、他方には影響しません。
__OC_I18N_900007__
設定形状は`approvals.exec`と同一です: `enabled`, `mode`, `agentFilter`,
`sessionFilter`, および `targets` は同じように動作します。

共有インタラクティブ返信をサポートするチャネルでは、exec承認とプラグイン承認の両方に同じ承認ボタンが表示されます。共有インタラクティブUIのないチャネルでは、`/approve`
手順を含むプレーンテキストへフォールバックします。

### 任意チャネルでの同一チャット承認

配信可能なチャット画面からexecまたはプラグイン承認要求が発生した場合、同じチャットでデフォルトで`/approve`を使って承認できるようになりました。これは、既存のWeb UIおよびターミナルUIフローに加え、Slack、Matrix、Microsoft Teamsなどのチャネルにも適用されます。

この共有テキストコマンド経路は、その会話の通常のチャネル認証モデルを使用します。元のチャットがすでにコマンド送信と返信受信を行えるなら、承認要求を保留にするためだけに別個のネイティブ配信アダプターは不要です。

DiscordとTelegramも同一チャット`/approve`をサポートしますが、これらのチャネルではネイティブ承認配信が無効でも、承認権限の判定には引き続き解決済み承認者一覧が使われます。

Telegramおよび、Gatewayを直接呼び出す他のネイティブ承認クライアントでは、
このフォールバックは意図的に「承認が見つからない」失敗に限定されます。実際の
exec承認の拒否/エラーは、無言でプラグイン承認として再試行されません。

### ネイティブ承認配信

一部のチャネルはネイティブ承認クライアントとしても機能します。ネイティブクライアントは、共有の同一チャット`/approve`
フローに加えて、承認者DM、元チャットへのファンアウト、およびチャネル固有の対話型承認UXを追加します。

ネイティブ承認カード/ボタンが利用可能な場合、そのネイティブUIがエージェント向けの主要経路です。ツール結果がチャット承認は利用不可であるか、手動承認だけが残る唯一の経路であると示していない限り、エージェントは重複するプレーンチャットの
`/approve`コマンドも併記すべきではありません。

汎用モデル:

- exec承認が必要かどうかは、引き続きホストexecポリシーが決定します
- `approvals.exec`は、他のチャット宛先への承認プロンプト転送を制御します
- `channels.<channel>.execApprovals`は、そのチャネルがネイティブ承認クライアントとして機能するかどうかを制御します

ネイティブ承認クライアントは、次のすべてが真の場合にDM優先配信を自動有効化します。

- そのチャネルがネイティブ承認配信をサポートしている
- 明示的な`execApprovals.approvers`またはそのチャネルで文書化されたフォールバックソースから承認者を解決できる
- `channels.<channel>.execApprovals.enabled`が未設定または`"auto"`である

ネイティブ承認クライアントを明示的に無効にするには`enabled: false`を設定してください。承認者が解決できるときに強制有効化するには`enabled: true`を設定してください。公開の元チャット配信は、`channels.<channel>.execApprovals.target`を通じて明示的に維持されます。

FAQ: [チャット承認にexec承認設定が2つあるのはなぜですか?](/help/faq#why-are-there-two-exec-approval-configs-for-chat-approvals)

- Discord: `channels.discord.execApprovals.*`
- Slack: `channels.slack.execApprovals.*`
- Telegram: `channels.telegram.execApprovals.*`

これらのネイティブ承認クライアントは、共有の同一チャット`/approve`フローおよび共有承認ボタンに加えて、DMルーティングと任意のチャネルファンアウトを追加します。

共有動作:

- Slack、Matrix、Microsoft Teams、および同様の配信可能チャットは、同一チャット`/approve`に通常のチャネル認証モデルを使用します
- ネイティブ承認クライアントが自動有効化される場合、デフォルトのネイティブ配信先は承認者DMです
- DiscordおよびTelegramでは、解決済み承認者だけが承認または拒否できます
- Discord承認者は、明示的な`execApprovals.approvers`または`commands.ownerAllowFrom`から推定できます
- Telegram承認者は、明示的な`execApprovals.approvers`または既存のowner設定（`allowFrom`、およびサポートされている場合はダイレクトメッセージの`defaultTo`）から推定できます
- Slack承認者は、明示的な`execApprovals.approvers`または`commands.ownerAllowFrom`から推定できます
- Slackネイティブボタンは承認id種別を保持するため、`plugin:` idは第2のSlackローカルフォールバック層なしでプラグイン承認を解決できます
- MatrixネイティブDM/チャネルルーティングはexec専用です。Matrixのプラグイン承認は、共有の同一チャット`/approve`および任意の`approvals.plugin`転送経路に残ります
- 要求者が承認者である必要はありません
- 元のチャットがすでにコマンドと返信をサポートしていれば、そのチャットから`/approve`で直接承認できます
- ネイティブDiscord承認ボタンは、承認id種別でルーティングされます: `plugin:` idはプラグイン承認へ直接送られ、それ以外はすべてexec承認へ送られます
- ネイティブTelegram承認ボタンは、`/approve`と同じ限定的なexecからpluginへのフォールバックに従います
- ネイティブ`target`で元チャット配信を有効にすると、承認プロンプトにはコマンドテキストが含まれます
- 保留中のexec承認はデフォルトで30分後に期限切れになります
- オペレーターUIまたは設定済み承認クライアントが要求を受け取れない場合、プロンプトは`askFallback`へフォールバックします

Telegramはデフォルトで承認者DM（`target: "dm"`）です。承認プロンプトも元のTelegramチャット/トピックに表示したい場合は、`channel`または`both`へ切り替えられます。Telegramフォーラムトピックでは、OpenClawは承認プロンプトと承認後フォローアップの両方でトピックを保持します。

参照:

- [Discord](/channels/discord)
- [Telegram](/channels/telegram)

### macOS IPCフロー
__OC_I18N_900008__
セキュリティに関するメモ:

- Unixソケットのモードは`0600`、トークンは`exec-approvals.json`に保存されます。
- 同一UIDピアチェック。
- チャレンジ/レスポンス（nonce + HMAC token + request hash）+ 短いTTL。

## システムイベント

Execライフサイクルはシステムメッセージとして表示されます。

- `Exec running`（コマンドがrunning通知しきい値を超えた場合のみ）
- `Exec finished`
- `Exec denied`

これらは、ノードがイベントを報告した後にエージェントのセッションへ投稿されます。
Gatewayホストのexec承認も、コマンド終了時に同じライフサイクルイベントを発行します（必要に応じて、しきい値を超える長時間実行時にも発行します）。
承認ゲート付きexecは、関連付けを容易にするため、これらのメッセージで承認idを`runId`として再利用します。

## 承認拒否時の動作

非同期exec承認が拒否された場合、OpenClawは、セッション内で同じコマンドの以前の実行からの出力をエージェントが再利用することを防ぎます。拒否理由は、利用可能なコマンド出力がないことを明示するガイダンス付きで渡されるため、エージェントが新しい出力があると主張したり、以前成功した実行の古い結果を使って拒否されたコマンドを繰り返したりすることを防ぎます。

## 影響

- **full**は強力です。可能な限り許可リストを優先してください。
- **ask**は、迅速な承認を可能にしつつ利用者をループ内に保ちます。
- エージェント単位の許可リストにより、あるエージェントの承認が他へ漏れることを防ぎます。
- 承認は、**認可済み送信者**からのホストexec要求にのみ適用されます。未認可送信者は`/exec`を発行できません。
- `/exec security=full`は認可済みオペレーター向けのセッションレベル便利機能であり、設計上承認をスキップします。
  ホストexecを確実にブロックするには、承認securityを`deny`に設定するか、ツールポリシーで`exec`ツールを拒否してください。

関連:

- [Exec tool](/ja-JP/tools/exec)
- [Elevated mode](/ja-JP/tools/elevated)
- [Skills](/ja-JP/tools/skills)

## 関連

- [Exec](/ja-JP/tools/exec) — シェルコマンド実行ツール
- [Sandboxing](/ja-JP/gateway/sandboxing) — サンドボックスモードとワークスペースアクセス
- [Security](/ja-JP/gateway/security) — セキュリティモデルとハードニング
- [Sandbox vs Tool Policy vs Elevated](/ja-JP/gateway/sandbox-vs-tool-policy-vs-elevated) — それぞれを使う場面
