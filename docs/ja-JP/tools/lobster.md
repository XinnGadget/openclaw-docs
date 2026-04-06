---
read_when:
    - 明示的な承認を伴う決定論的なマルチステップワークフローが必要
    - 以前のステップを再実行せずにワークフローを再開する必要がある
summary: 再開可能な承認ゲートを備えた、OpenClaw用の型付きワークフローruntime。
title: Lobster
x-i18n:
    generated_at: "2026-04-06T03:14:13Z"
    model: gpt-5.4
    provider: openai
    source_hash: c1014945d104ef8fdca0d30be89e35136def1b274c6403b06de29e8502b8124b
    source_path: tools/lobster.md
    workflow: 15
---

# Lobster

Lobsterは、OpenClawがマルチステップのtool sequenceを、明示的な承認チェックポイントを備えた単一の決定論的操作として実行できるようにするワークフローshellです。

Lobsterは、detached background workの一段上にあるauthoring layerです。個々のタスクより上のフローオーケストレーションについては、[Task Flow](/ja-JP/automation/taskflow)（`openclaw tasks flow`）を参照してください。タスク活動ledgerについては、[`openclaw tasks`](/ja-JP/automation/tasks)を参照してください。

## Hook

あなたのassistantは、自分自身を管理するtoolsを構築できます。ワークフローを依頼すれば、30分後にはCLIと、1回の呼び出しで動くパイプラインが手に入ります。Lobsterはその欠けていたピースです。決定論的なパイプライン、明示的な承認、そして再開可能な状態を提供します。

## なぜ必要なのか

現在、複雑なワークフローには多くの往復tool callが必要です。各callにはトークンコストがかかり、LLMはすべてのステップをオーケストレーションしなければなりません。Lobsterは、そのオーケストレーションを型付きruntimeへ移します。

- **多数のcallではなく1回のcall**: OpenClawは1回のLobster tool callを実行し、構造化された結果を受け取ります。
- **承認を内蔵**: 副作用（メール送信、コメント投稿など）は、明示的に承認されるまでワークフローを停止します。
- **再開可能**: 停止したワークフローはtokenを返し、すべてを再実行せずに承認して再開できます。

## なぜ通常のプログラムではなくDSLなのか

Lobsterは意図的に小さく作られています。目標は「新しい言語」ではなく、ファーストクラスの承認とresume tokenを備えた、予測可能でAIフレンドリーなpipeline specです。

- **approve/resumeが組み込み**: 通常のプログラムでも人に確認を求めることはできますが、永続的なtokenで_一時停止して再開する_ことは、そのruntimeを自前で発明しない限りできません。
- **決定論性 + 監査可能性**: パイプラインはデータなので、ログ化、差分確認、再実行、レビューが容易です。
- **AI向けの制約されたsurface**: 小さな文法 + JSONパイピングにより「創造的」なコードパスが減り、現実的な検証が可能になります。
- **安全ポリシーを内蔵**: タイムアウト、出力上限、sandboxチェック、許可リストは、各scriptではなくruntimeによって強制されます。
- **それでもプログラム可能**: 各ステップは任意のCLIまたはscriptを呼び出せます。JS/TSを使いたい場合は、コードから`.lobster` filesを生成してください。

## 仕組み

OpenClawは、組み込みrunnerを使ってLobsterワークフローを**プロセス内**で実行します。外部CLI subprocessは生成されません。ワークフローエンジンはgateway process内で実行され、JSON envelopeを直接返します。
承認待ちでpipelineが一時停止した場合、toolは後で継続できるよう`resumeToken`を返します。

## パターン: 小さなCLI + JSON pipes + 承認

JSONを話す小さなコマンドを作り、それらを1回のLobster callへ連結します。（以下のコマンド名は例です。自分のものに置き換えてください。）

```bash
inbox list --json
inbox categorize --json
inbox apply --json
```

```json
{
  "action": "run",
  "pipeline": "exec --json --shell 'inbox list --json' | exec --stdin json --shell 'inbox categorize --json' | exec --stdin json --shell 'inbox apply --json' | approve --preview-from-stdin --limit 5 --prompt 'Apply changes?'",
  "timeoutMs": 30000
}
```

pipelineが承認を要求した場合は、tokenで再開します。

```json
{
  "action": "resume",
  "token": "<resumeToken>",
  "approve": true
}
```

AIがワークフローを起動し、Lobsterがステップを実行します。承認ゲートにより、副作用は明示的かつ監査可能に保たれます。

例: 入力項目をtool callsへマッピングする:

```bash
gog.gmail.search --query 'newer_than:1d' \
  | openclaw.invoke --tool message --action send --each --item-key message --args-json '{"provider":"telegram","to":"..."}'
```

## JSON専用LLMステップ（llm-task）

ワークフロー内で**構造化されたLLMステップ**が必要な場合は、任意の
`llm-task`プラグインtoolを有効にし、Lobsterから呼び出してください。これにより、
workflowを決定論的に保ちながら、モデルによる分類/要約/下書きも可能になります。

toolを有効化する:

```json
{
  "plugins": {
    "entries": {
      "llm-task": { "enabled": true }
    }
  },
  "agents": {
    "list": [
      {
        "id": "main",
        "tools": { "allow": ["llm-task"] }
      }
    ]
  }
}
```

pipelineで使用する:

```lobster
openclaw.invoke --tool llm-task --action json --args-json '{
  "prompt": "Given the input email, return intent and draft.",
  "thinking": "low",
  "input": { "subject": "Hello", "body": "Can you help?" },
  "schema": {
    "type": "object",
    "properties": {
      "intent": { "type": "string" },
      "draft": { "type": "string" }
    },
    "required": ["intent", "draft"],
    "additionalProperties": false
  }
}'
```

詳細と設定オプションについては、[LLM Task](/ja-JP/tools/llm-task)を参照してください。

## ワークフローファイル（.lobster）

Lobsterは、`name`、`args`、`steps`、`env`、`condition`、`approval`フィールドを持つYAML/JSONワークフローファイルを実行できます。OpenClawのtool callでは、`pipeline`にファイルパスを設定します。

```yaml
name: inbox-triage
args:
  tag:
    default: "family"
steps:
  - id: collect
    command: inbox list --json
  - id: categorize
    command: inbox categorize --json
    stdin: $collect.stdout
  - id: approve
    command: inbox apply --approve
    stdin: $categorize.stdout
    approval: required
  - id: execute
    command: inbox apply --execute
    stdin: $categorize.stdout
    condition: $approve.approved
```

注意:

- `stdin: $step.stdout`と`stdin: $step.json`は、前のステップの出力を渡します。
- `condition`（または`when`）で、`$step.approved`に基づいてステップを制御できます。

## Lobsterをインストールする

バンドルされたLobsterワークフローはプロセス内で実行されるため、別個の`lobster` binaryは不要です。組み込みrunnerはLobsterプラグインとともに提供されます。

開発や外部pipelineのためにスタンドアロンのLobster CLIが必要な場合は、[Lobster repo](https://github.com/openclaw/lobster)からインストールし、`lobster`が`PATH`上にあることを確認してください。

## toolを有効にする

Lobsterは**任意の**プラグインtoolです（デフォルトでは有効ではありません）。

推奨（加算的、安全）:

```json
{
  "tools": {
    "alsoAllow": ["lobster"]
  }
}
```

またはagentごと:

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "tools": {
          "alsoAllow": ["lobster"]
        }
      }
    ]
  }
}
```

制限付きallowlist modeで実行する意図がない限り、`tools.allow: ["lobster"]`の使用は避けてください。

注意: allowlistは任意プラグイン向けのオプトインです。allowlistに
`lobster`のような
plugin toolsだけを指定した場合でも、OpenClawはcore toolsを有効のままにします。core
toolsも制限したい場合は、allowlistに希望するcore toolsまたはgroupsも含めてください。

## 例: Email triage

Lobsterなし:

```
User: "Check my email and draft replies"
→ openclaw calls gmail.list
→ LLM summarizes
→ User: "draft replies to #2 and #5"
→ LLM drafts
→ User: "send #2"
→ openclaw calls gmail.send
(repeat daily, no memory of what was triaged)
```

Lobsterあり:

```json
{
  "action": "run",
  "pipeline": "email.triage --limit 20",
  "timeoutMs": 30000
}
```

JSON envelopeを返します（省略版）:

```json
{
  "ok": true,
  "status": "needs_approval",
  "output": [{ "summary": "5 need replies, 2 need action" }],
  "requiresApproval": {
    "type": "approval_request",
    "prompt": "Send 2 draft replies?",
    "items": [],
    "resumeToken": "..."
  }
}
```

ユーザーが承認 → 再開:

```json
{
  "action": "resume",
  "token": "<resumeToken>",
  "approve": true
}
```

1つのワークフロー。決定論的。安全。

## tool parameters

### `run`

tool modeでpipelineを実行します。

```json
{
  "action": "run",
  "pipeline": "gog.gmail.search --query 'newer_than:1d' | email.triage",
  "cwd": "workspace",
  "timeoutMs": 30000,
  "maxStdoutBytes": 512000
}
```

args付きでワークフローファイルを実行する:

```json
{
  "action": "run",
  "pipeline": "/path/to/inbox-triage.lobster",
  "argsJson": "{\"tag\":\"family\"}"
}
```

### `resume`

承認後に停止したワークフローを継続します。

```json
{
  "action": "resume",
  "token": "<resumeToken>",
  "approve": true
}
```

### 任意入力

- `cwd`: pipeline用の相対working directory（gateway working directory内に留まる必要があります）。
- `timeoutMs`: この時間を超えた場合はワークフローを中止します（デフォルト: 20000）。
- `maxStdoutBytes`: 出力がこのサイズを超えた場合はワークフローを中止します（デフォルト: 512000）。
- `argsJson`: `lobster run --args-json`に渡されるJSON文字列（ワークフローファイルのみ）。

## 出力envelope

Lobsterは、次の3つのstatusのいずれかを持つJSON envelopeを返します。

- `ok` → 正常終了
- `needs_approval` → 一時停止中。再開には`requiresApproval.resumeToken`が必要
- `cancelled` → 明示的に拒否またはキャンセル

toolは、このenvelopeを`content`（整形JSON）と`details`（生オブジェクト）の両方で公開します。

## 承認

`requiresApproval`が存在する場合は、promptを確認して判断します。

- `approve: true` → 再開し、副作用を継続
- `approve: false` → キャンセルしてワークフローを終了

カスタムのjq/heredoc接着なしでJSONプレビューを承認要求へ添付するには、`approve --preview-from-stdin --limit N`を使用してください。resume tokenは現在コンパクトです。Lobsterはworkflow resume stateをstate dir配下に保存し、小さなtoken keyを返します。

## OpenProse

OpenProseはLobsterと相性が良く、`/prose`でマルチエージェント準備をオーケストレーションし、その後Lobster pipelineで決定論的な承認を実行できます。Prose programでLobsterが必要な場合は、`tools.subagents.tools`経由でsub-agentsに`lobster` toolを許可してください。[OpenProse](/ja-JP/prose)を参照してください。

## 安全性

- **ローカルのプロセス内のみ** — ワークフローはgateway process内で実行され、プラグイン自体からのnetwork callsはありません。
- **シークレットなし** — LobsterはOAuthを管理しません。代わりに、それを管理するOpenClaw toolsを呼び出します。
- **sandbox対応** — tool contextがsandbox化されている場合は無効になります。
- **堅牢化済み** — タイムアウトと出力上限は組み込みrunnerによって強制されます。

## トラブルシューティング

- **`lobster timed out`** → `timeoutMs`を増やすか、長いpipelineを分割してください。
- **`lobster output exceeded maxStdoutBytes`** → `maxStdoutBytes`を増やすか、出力サイズを減らしてください。
- **`lobster returned invalid JSON`** → pipelineがtool modeで実行され、JSONだけを出力していることを確認してください。
- **`lobster failed`** → 組み込みrunnerのエラー詳細についてgateway logsを確認してください。

## 詳しく知る

- [プラグイン](/ja-JP/tools/plugin)
- [プラグインtool authoring](/ja-JP/plugins/building-plugins#registering-agent-tools)

## ケーススタディ: コミュニティワークフロー

公開例の1つとして、3つのMarkdown vault（personal、partner、shared）を管理する「second brain」CLI + Lobster pipelinesがあります。このCLIは統計、inbox一覧、stale scan用にJSONを出力し、Lobsterはそれらのコマンドを`weekly-review`、`inbox-triage`、`memory-consolidation`、`shared-task-sync`のような承認ゲート付きワークフローへ連結します。利用可能なときはAIが判断（分類）を担当し、そうでない場合は決定論的ルールへフォールバックします。

- スレッド: [https://x.com/plattenschieber/status/2014508656335770033](https://x.com/plattenschieber/status/2014508656335770033)
- Repo: [https://github.com/bloomedai/brain-cli](https://github.com/bloomedai/brain-cli)

## 関連

- [Automation & Tasks](/ja-JP/automation) — Lobsterワークフローのスケジューリング
- [Automation Overview](/ja-JP/automation) — すべての自動化メカニズム
- [Tools Overview](/ja-JP/tools) — 利用可能なすべてのagent tools
