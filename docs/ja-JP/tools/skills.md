---
read_when:
    - Skillsを追加または変更すること
    - Skillのゲーティングまたは読み込みルールを変更すること
summary: 'Skills: 管理対象とワークスペース、ゲーティングルール、および設定/環境変数の配線'
title: Skills
x-i18n:
    generated_at: "2026-04-11T02:48:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: b1eaf130966950b6eb24f859d9a77ecbf81c6cb80deaaa6a3a79d2c16d83115d
    source_path: tools/skills.md
    workflow: 15
---

# Skills（OpenClaw）

OpenClawは、エージェントにツールの使い方を教えるために**[AgentSkills](https://agentskills.io)互換**のskillフォルダーを使用します。各skillは、YAML frontmatterと指示を含む`SKILL.md`を持つディレクトリです。OpenClawは**バンドル版skills**と任意のローカル上書きを読み込み、環境、設定、バイナリの有無に基づいて読み込み時にフィルタリングします。

## 場所と優先順位

OpenClawは以下のソースからskillsを読み込みます:

1. **追加skillフォルダー**: `skills.load.extraDirs`で設定
2. **バンドル版skills**: インストール物（npmパッケージまたはOpenClaw.app）に同梱
3. **managed/local skills**: `~/.openclaw/skills`
4. **個人エージェントskills**: `~/.agents/skills`
5. **プロジェクトエージェントskills**: `<workspace>/.agents/skills`
6. **ワークスペースskills**: `<workspace>/skills`

skill名が競合した場合の優先順位は次のとおりです:

`<workspace>/skills`（最優先）→ `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → バンドル版skills → `skills.load.extraDirs`（最低優先）

## エージェントごとのskillsと共有skills

**マルチエージェント**構成では、各エージェントはそれぞれのワークスペースを持ちます。つまり:

- **エージェントごとのskills**は、そのエージェント専用の`<workspace>/skills`に置かれます。
- **プロジェクトエージェントskills**は`<workspace>/.agents/skills`に置かれ、
  通常のワークスペース`skills/`フォルダーより前にそのワークスペースへ適用されます。
- **個人エージェントskills**は`~/.agents/skills`に置かれ、
  そのマシン上のワークスペースをまたいで適用されます。
- **共有skills**は`~/.openclaw/skills`（managed/local）に置かれ、同じマシン上の**すべてのエージェント**から見えます。
- **共有フォルダー**は、複数のエージェントで使う共通skillsパックが欲しい場合、
  `skills.load.extraDirs`（最低優先）経由でも追加できます。

同じskill名が複数の場所に存在する場合は、通常の優先順位が適用されます:
workspaceが勝ち、その次にプロジェクトエージェントskills、個人エージェントskills、
managed/local、バンドル版、extra dirsの順です。

## エージェントskill許可リスト

skillの**配置場所**とskillの**可視性**は別の制御です。

- 配置場所/優先順位は、同名skillのどのコピーが勝つかを決定します。
- エージェント許可リストは、可視なskillsのうち、そのエージェントが実際にどれを使えるかを決定します。

共通のベースラインには`agents.defaults.skills`を使用し、その後
`agents.list[].skills`でエージェントごとに上書きします:

```json5
{
  agents: {
    defaults: {
      skills: ["github", "weather"],
    },
    list: [
      { id: "writer" }, // github, weatherを継承
      { id: "docs", skills: ["docs-search"] }, // デフォルトを置き換える
      { id: "locked-down", skills: [] }, // skillsなし
    ],
  },
}
```

ルール:

- デフォルトでskillsを無制限にするには`agents.defaults.skills`を省略します。
- `agents.defaults.skills`を継承するには`agents.list[].skills`を省略します。
- skillsなしにするには`agents.list[].skills: []`を設定します。
- 空でない`agents.list[].skills`リストは、そのエージェントの最終セットになります。
  デフォルトとはマージされません。

OpenClawは、有効なエージェントskillセットを、プロンプト構築、skillスラッシュコマンド検出、
サンドボックス同期、およびskillスナップショット全体に適用します。

## プラグイン + skills

プラグインは、`openclaw.plugin.json`に`skills`ディレクトリ
（プラグインルートからの相対パス）を列挙することで独自のskillsを同梱できます。プラグインskillsは、そのプラグインが有効なときに読み込まれます。現在、
これらのディレクトリは`skills.load.extraDirs`と同じ低優先順位のパスへマージされるため、
同名のバンドル版、managed、agent、またはworkspace skillがそれらを上書きします。
これらはプラグイン設定エントリーの`metadata.openclaw.requires.config`
でゲートできます。検出/設定については[Plugins](/ja-JP/tools/plugin)を、これらのskillsが教える
ツールサーフェスについては[Tools](/ja-JP/tools)を参照してください。

## ClawHub（インストール + 同期）

ClawHubはOpenClaw向けの公開skillsレジストリです。
[https://clawhub.ai](https://clawhub.ai)で閲覧できます。ネイティブの`openclaw skills`
コマンドを使ってskillsを検出/インストール/更新するか、公開/同期ワークフローが必要な場合は
別の`clawhub` CLIを使用してください。
完全ガイド: [ClawHub](/ja-JP/tools/clawhub)。

一般的なフロー:

- skillをワークスペースにインストールする:
  - `openclaw skills install <skill-slug>`
- インストール済みskillsをすべて更新する:
  - `openclaw skills update --all`
- 同期する（スキャン + 更新を公開）:
  - `clawhub sync --all`

ネイティブの`openclaw skills install`は、アクティブなワークスペースの`skills/`
ディレクトリへインストールします。別の`clawhub` CLIも、現在の作業ディレクトリ配下の`./skills`
へインストールし（または設定済みOpenClawワークスペースへフォールバックし）、
OpenClawは次のセッションでそれを`<workspace>/skills`として認識します。

## セキュリティに関する注意

- サードパーティskillsは**信頼されていないコード**として扱ってください。有効化する前に読んでください。
- 信頼されていない入力や危険なツールには、サンドボックス実行を優先してください。[Sandboxing](/ja-JP/gateway/sandboxing)を参照してください。
- ワークスペースおよびextra-dirのskill検出は、解決後のrealpathが設定済みルート内に収まる
  skillルートと`SKILL.md`ファイルのみを受け付けます。
- Gatewayバックエンドのskill依存関係インストール（`skills.install`、オンボーディング、
  Skills設定UI）は、インストーラーメタデータ実行前に組み込みの危険コードスキャナーを実行します。
  `critical`所見は、呼び出し側が明示的に危険上書きを設定しない限りデフォルトでブロックされます。
  suspicious所見は警告のみです。
- `openclaw skills install <slug>`は異なります。これはClawHubのskillフォルダーをワークスペースへダウンロードするだけで、
  上記のインストーラーメタデータ経路は使用しません。
- `skills.entries.*.env`と`skills.entries.*.apiKey`は、そのエージェントターンについてシークレットを**ホスト**
  プロセスへ注入します（サンドボックスではありません）。シークレットをプロンプトやログに入れないでください。
- より広い脅威モデルとチェックリストについては、[Security](/ja-JP/gateway/security)を参照してください。

## 形式（AgentSkills + Pi互換）

`SKILL.md`には最低限、以下を含める必要があります:

```markdown
---
name: image-lab
description: Generate or edit images via a provider-backed image workflow
---
```

注記:

- レイアウト/意図についてはAgentSkills仕様に従います。
- 埋め込みエージェントで使われるパーサーは、**単一行**のfrontmatterキーのみをサポートします。
- `metadata`は**単一行JSONオブジェクト**である必要があります。
- skillフォルダーパスを参照するには、指示内で`{baseDir}`を使用してください。
- 任意のfrontmatterキー:
  - `homepage` — macOS Skills UIで「Website」として表示されるURL（`metadata.openclaw.homepage`経由でもサポート）。
  - `user-invocable` — `true|false`（デフォルト: `true`）。`true`の場合、このskillはユーザースラッシュコマンドとして公開されます。
  - `disable-model-invocation` — `true|false`（デフォルト: `false`）。`true`の場合、このskillはモデルプロンプトから除外されます（ユーザー呼び出しでは引き続き利用可能）。
  - `command-dispatch` — `tool`（任意）。`tool`に設定すると、スラッシュコマンドはモデルをバイパスし、直接ツールへディスパッチします。
  - `command-tool` — `command-dispatch: tool`が設定されているときに呼び出すツール名。
  - `command-arg-mode` — `raw`（デフォルト）。ツールディスパッチ時、rawの引数文字列をそのままツールへ転送します（コアによる解析なし）。

    ツールは以下のparamsで呼び出されます:
    `{ command: "<raw args>", commandName: "<slash command>", skillName: "<skill name>" }`。

## ゲーティング（読み込み時フィルター）

OpenClawは、`metadata`（単一行JSON）を使って**読み込み時にskillsをフィルタリング**します:

```markdown
---
name: image-lab
description: Generate or edit images via a provider-backed image workflow
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["uv"], "env": ["GEMINI_API_KEY"], "config": ["browser.enabled"] },
        "primaryEnv": "GEMINI_API_KEY",
      },
  }
---
```

`metadata.openclaw`配下のフィールド:

- `always: true` — skillを常に含める（他のゲートをスキップ）。
- `emoji` — macOS Skills UIで使われる任意の絵文字。
- `homepage` — macOS Skills UIで「Website」として表示される任意のURL。
- `os` — 任意のプラットフォーム一覧（`darwin`, `linux`, `win32`）。設定されている場合、そのOS上でのみskillが有効候補になります。
- `requires.bins` — 一覧。各項目が`PATH`上に存在しなければなりません。
- `requires.anyBins` — 一覧。少なくとも1つが`PATH`上に存在しなければなりません。
- `requires.env` — 一覧。環境変数が存在する**か**、設定で提供されていなければなりません。
- `requires.config` — truthyでなければならない`openclaw.json`パスの一覧。
- `primaryEnv` — `skills.entries.<name>.apiKey`に関連付けられる環境変数名。
- `install` — macOS Skills UIで使われる任意のインストーラー仕様配列（brew/node/go/uv/download）。

サンドボックスに関する注記:

- `requires.bins`は、skill読み込み時に**ホスト**上で確認されます。
- エージェントがサンドボックス化されている場合、そのバイナリは**コンテナ内にも**
  存在しなければなりません。
  `agents.defaults.sandbox.docker.setupCommand`（またはカスタムイメージ）経由でインストールしてください。
  `setupCommand`は、コンテナ作成後に1回だけ実行されます。
  パッケージインストールには、ネットワークegress、書き込み可能なルートFS、およびサンドボックス内のrootユーザーも必要です。
  例: `summarize` skill（`skills/summarize/SKILL.md`）は、そこで実行するには
  サンドボックスコンテナ内に`summarize` CLIが必要です。

インストーラー例:

```markdown
---
name: gemini
description: Use Gemini CLI for coding assistance and Google search lookups.
metadata:
  {
    "openclaw":
      {
        "emoji": "♊️",
        "requires": { "bins": ["gemini"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "gemini-cli",
              "bins": ["gemini"],
              "label": "Install Gemini CLI (brew)",
            },
          ],
      },
  }
---
```

注記:

- 複数のインストーラーが列挙されている場合、gatewayは**単一の**優先オプションを選びます（brewが利用可能ならbrew、そうでなければnode）。
- すべてのインストーラーが`download`の場合、OpenClawは利用可能な成果物を確認できるよう各エントリーを一覧表示します。
- インストーラー仕様には、プラットフォームごとに選択肢を絞り込むための`os: ["darwin"|"linux"|"win32"]`を含められます。
- Nodeインストールは`openclaw.json`内の`skills.install.nodeManager`を尊重します
  （デフォルト: npm、選択肢: npm/pnpm/yarn/bun）。
  これは**skillインストール**にのみ影響します。Gatewayランタイムは引き続きNodeであるべきです
  （WhatsApp/TelegramにはBunは推奨されません）。
- Gatewayバックエンドのインストーラー選択は、node専用ではなく優先度駆動です:
  インストール仕様が複数種類を混在させている場合、OpenClawは
  `skills.install.preferBrew`が有効で`brew`が存在すればHomebrewを優先し、次に`uv`、その後
  設定済みnode manager、その後`go`や`download`のような他のフォールバックを選びます。
- すべてのinstall specが`download`の場合、OpenClawは
  1つの優先インストーラーにまとめず、すべてのダウンロードオプションを表示します。
- Goインストール: `go`がなく`brew`が利用可能な場合、gatewayはまずHomebrew経由でGoをインストールし、可能なら`GOBIN`をHomebrewの`bin`に設定します。
- Downloadインストール: `url`（必須）、`archive`（`tar.gz` | `tar.bz2` | `zip`）、`extract`（デフォルト: archive検出時は自動）、`stripComponents`、`targetDir`（デフォルト: `~/.openclaw/tools/<skillKey>`）。

`metadata.openclaw`が存在しない場合、そのskillは常に有効候補です（設定で無効化されている場合や、
バンドル版skillに対して`skills.allowBundled`でブロックされている場合を除く）。

## 設定上書き（`~/.openclaw/openclaw.json`）

バンドル版/managed skillsは、有効化したりenv値を供給したりできます:

```json5
{
  skills: {
    entries: {
      "image-lab": {
        enabled: true,
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" }, // または平文文字列
        env: {
          GEMINI_API_KEY: "GEMINI_KEY_HERE",
        },
        config: {
          endpoint: "https://example.invalid",
          model: "nano-pro",
        },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

注: skill名にハイフンが含まれる場合は、キーをクォートしてください（JSON5ではクォート付きキーが使えます）。

OpenClaw本体の中で標準の画像生成/編集を使いたい場合は、バンドル版skillではなく、
`agents.defaults.imageGenerationModel`と組み合わせたコアの
`image_generate`ツールを使用してください。ここでのskill例は、カスタムまたはサードパーティのワークフロー向けです。

ネイティブ画像解析には、`agents.defaults.imageModel`とともに`image`ツールを使ってください。
ネイティブ画像生成/編集には、
`agents.defaults.imageGenerationModel`とともに`image_generate`を使用してください。`openai/*`、`google/*`、
`fal/*`、またはその他のプロバイダー固有画像モデルを選ぶ場合は、そのプロバイダーの認証/API
キーも追加してください。

設定キーはデフォルトで**skill名**と一致します。skillが
`metadata.openclaw.skillKey`を定義している場合は、`skills.entries`配下でそのキーを使用してください。

ルール:

- `enabled: false`は、そのskillがバンドル済み/インストール済みでも無効化します。
- `env`: その変数がプロセスですでに設定されていない**場合にのみ**注入されます。
- `apiKey`: `metadata.openclaw.primaryEnv`を宣言しているskill向けの簡易指定です。
  平文文字列またはSecretRefオブジェクト（`{ source, provider, id }`）をサポートします。
- `config`: カスタムなskillごとのフィールド用の任意バッグです。カスタムキーはここに置かなければなりません。
- `allowBundled`: **バンドル版**skills専用の任意許可リストです。設定した場合、
  リスト内のバンドル版skillsだけが有効候補になります（managed/workspace skillsは影響を受けません）。

## 環境変数注入（エージェント実行ごと）

エージェント実行が始まると、OpenClawは以下を行います:

1. skillメタデータを読み取る。
2. `skills.entries.<key>.env`または`skills.entries.<key>.apiKey`を
   `process.env`に適用する。
3. **有効候補**skillsを使ってシステムプロンプトを構築する。
4. 実行終了後に元の環境を復元する。

これは**エージェント実行にスコープされた**ものであり、グローバルなシェル環境ではありません。

バンドル版`claude-cli`バックエンドでは、OpenClawは同じ
有効候補スナップショットを一時的なClaude Codeプラグインとして具体化し、
`--plugin-dir`とともに渡します。これによりClaude Codeはネイティブのskillリゾルバーを使えますが、
優先順位、エージェントごとの許可リスト、ゲーティング、および
`skills.entries.*`のenv/APIキー注入は引き続きOpenClawが所有します。他のCLIバックエンドは
プロンプトカタログのみを使用します。

## セッションスナップショット（パフォーマンス）

OpenClawは、**セッション開始時**に有効候補skillsをスナップショットし、同じセッション内の後続ターンではその一覧を再利用します。skillsまたは設定の変更は次の新規セッションで有効になります。

skills watcherが有効な場合や、新たな有効候補のリモートノードが現れた場合（後述）は、セッション途中でskillsが更新されることもあります。これは**ホットリロード**と考えてください。更新された一覧は次のエージェントターンで取り込まれます。

そのセッションに対する有効なエージェントskill許可リストが変更された場合、OpenClawは
可視skillsが現在のエージェントに揃うようスナップショットを更新します。

## リモートmacOSノード（Linux Gateway）

GatewayがLinux上で動作していても、**macOSノード**が接続されており、かつ**`system.run`が許可されている**
（Exec approvalsセキュリティが`deny`に設定されていない）場合、必要なバイナリがそのノード上に存在すれば、
OpenClawはmacOS専用skillsを有効候補として扱えます。エージェントは`exec`ツールを`host=node`付きで使って、
それらのskillsを実行するべきです。

これは、ノードがコマンドサポートを報告することと、`system.run`経由のbin probeに依存します。その後でmacOSノードがオフラインになっても、skillsは可視のままです。ノードが再接続するまで呼び出しは失敗する可能性があります。

## Skills watcher（自動更新）

デフォルトでは、OpenClawはskillフォルダーを監視し、`SKILL.md`ファイルが変更されるとskillsスナップショットを更新します。これは`skills.load`配下で設定します:

```json5
{
  skills: {
    load: {
      watch: true,
      watchDebounceMs: 250,
    },
  },
}
```

## トークンへの影響（skills一覧）

skillsが有効候補になると、OpenClawは利用可能なskillsのコンパクトなXML一覧を
システムプロンプトへ注入します（`pi-coding-agent`の`formatSkillsForPrompt`経由）。コストは決定的です:

- **ベースオーバーヘッド（1件以上のskillがある場合のみ）:** 195文字。
- **skillごと:** 97文字 + XMLエスケープ済みの`<name>`、`<description>`、`<location>`値の長さ。

式（文字数）:

```
total = 195 + Σ (97 + len(name_escaped) + len(description_escaped) + len(location_escaped))
```

注記:

- XMLエスケープは`& < > " '`をエンティティ（`&amp;`、`&lt;`など）へ展開するため、長さが増えます。
- トークン数はモデルのトークナイザーによって異なります。OpenAI風の大まかな見積もりでは約4文字/トークンなので、**97文字 ≈ 24トークン**/skillに加え、実際のフィールド長が加算されます。

## managed skillsのライフサイクル

OpenClawは、インストール物
（npmパッケージまたはOpenClaw.app）の一部として、ベースラインのskillsを**バンドル版skills**として同梱します。`~/.openclaw/skills`はローカル上書き用に存在します
（たとえば、バンドル版コピーを変更せずにskillを固定/パッチする場合など）。
workspace skillsはユーザー所有であり、名前が競合した場合は両方を上書きします。

## 設定リファレンス

完全な設定スキーマについては[Skills config](/ja-JP/tools/skills-config)を参照してください。

## もっとskillsを探していますか？

[https://clawhub.ai](https://clawhub.ai)を参照してください。

---

## 関連

- [Creating Skills](/ja-JP/tools/creating-skills) — カスタムskillsの構築
- [Skills Config](/ja-JP/tools/skills-config) — skill設定リファレンス
- [Slash Commands](/ja-JP/tools/slash-commands) — 利用可能なすべてのスラッシュコマンド
- [Plugins](/ja-JP/tools/plugin) — プラグインシステムの概要
