---
read_when:
    - APIプロバイダーが失敗したときの信頼できるフォールバックがほしい
    - Codex CLIやその他のローカルAI CLIを実行しており、それらを再利用したい
    - CLIバックエンドのツールアクセス向けMCP loopbackブリッジを理解したい
summary: 'CLIバックエンド: 任意のMCPツールブリッジを備えた、ローカルAI CLIフォールバック'
title: CLIバックエンド
x-i18n:
    generated_at: "2026-04-07T04:42:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: f061357f420455ad6ffaabe7fe28f1fb1b1769d73a4eb2e6f45c6eb3c2e36667
    source_path: gateway/cli-backends.md
    workflow: 15
---

# CLIバックエンド（フォールバックランタイム）

OpenClawは、APIプロバイダーが停止中、レート制限中、または一時的に不安定なときに、**ローカルAI CLI**を**テキスト専用のフォールバック**として実行できます。これは意図的に保守的な設計です:

- **OpenClaw toolsは直接注入されません**が、`bundleMcp: true` を持つバックエンドは
  loopback MCPブリッジ経由でGatewayツールを受け取ることができます。
- それをサポートするCLI向けの**JSONLストリーミング**。
- **セッションをサポート**しています（そのため後続ターンの一貫性が保たれます）。
- CLIが画像パスを受け付ける場合は、**画像をそのまま渡せます**。

これは主経路ではなく、**セーフティネット**として設計されています。外部APIに依存せずに「常に動作する」テキスト応答がほしいときに使ってください。

ACPセッション制御、バックグラウンドタスク、スレッド/会話のバインド、および永続的な外部コーディングセッションを備えた完全なハーネスランタイムが必要な場合は、代わりに [ACP Agents](/ja-JP/tools/acp-agents) を使ってください。CLIバックエンドはACPではありません。

## 初心者向けクイックスタート

設定なしでCodex CLIを使えます（バンドルされたOpenAIプラグインが
デフォルトバックエンドを登録します）:

```bash
openclaw agent --message "hi" --model codex-cli/gpt-5.4
```

Gatewayがlaunchd/systemd配下で動作しておりPATHが最小限の場合は、
コマンドパスだけ追加してください:

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "codex-cli": {
          command: "/opt/homebrew/bin/codex",
        },
      },
    },
  },
}
```

これだけです。CLI自体に必要なものを除いて、キーも追加の認証設定も不要です。

バンドルされたCLIバックエンドをGatewayホスト上の**主要メッセージプロバイダー**として使う場合、OpenClawは、そのバックエンドが設定内でモデル参照または
`agents.defaults.cliBackends` 配下に明示的に指定されていれば、所有するバンドル済みプラグインを自動で読み込みます。

## フォールバックとして使う

CLIバックエンドをフォールバック一覧に追加すると、主要モデルが失敗したときだけ実行されます:

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["codex-cli/gpt-5.4"],
      },
      models: {
        "anthropic/claude-opus-4-6": { alias: "Opus" },
        "codex-cli/gpt-5.4": {},
      },
    },
  },
}
```

注意:

- `agents.defaults.models`（allowlist）を使う場合は、CLIバックエンドのモデルもそこに含める必要があります。
- 主要プロバイダーが失敗した場合（認証、レート制限、タイムアウト）、OpenClawは次にCLIバックエンドを試します。

## 設定の概要

すべてのCLIバックエンドは次の配下にあります:

```
agents.defaults.cliBackends
```

各エントリーは**provider id**（例: `codex-cli`, `my-cli`）をキーにします。
このprovider idがモデル参照の左側になります:

```
<provider>/<model>
```

### 設定例

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "codex-cli": {
          command: "/opt/homebrew/bin/codex",
        },
        "my-cli": {
          command: "my-cli",
          args: ["--json"],
          output: "json",
          input: "arg",
          modelArg: "--model",
          modelAliases: {
            "claude-opus-4-6": "opus",
            "claude-sonnet-4-6": "sonnet",
          },
          sessionArg: "--session",
          sessionMode: "existing",
          sessionIdFields: ["session_id", "conversation_id"],
          systemPromptArg: "--system",
          systemPromptWhen: "first",
          imageArg: "--image",
          imageMode: "repeat",
          serialize: true,
        },
      },
    },
  },
}
```

## 仕組み

1. provider prefix（`codex-cli/...`）に基づいて**バックエンドを選択**します。
2. 同じOpenClawプロンプト + ワークスペースコンテキストを使って**system promptを構築**します。
3. 履歴の一貫性を保つため、（サポートされていれば）セッションid付きで**CLIを実行**します。
4. 出力（JSONまたはプレーンテキスト）を**解析**して、最終テキストを返します。
5. 後続入力で同じCLIセッションを再利用できるよう、バックエンドごとにセッションidを**永続化**します。

<Note>
バンドルされたAnthropic `claude-cli` バックエンドが再びサポートされました。Anthropicスタッフから、OpenClawスタイルのClaude CLI利用は再び許可されていると案内されているため、Anthropicが新しいポリシーを公開しない限り、OpenClawはこの連携における `claude -p` の使用を認められたものとして扱います。
</Note>

## セッション

- CLIがセッションをサポートする場合、`sessionArg`（例: `--session-id`）または
  `sessionArgs`（複数のフラグに `{sessionId}` を挿入する必要がある場合のプレースホルダー）を設定してください。
- CLIが異なるフラグを使う**resume subcommand**を使う場合は、
  `resumeArgs`（再開時に `args` を置き換えます）と、必要に応じて `resumeOutput`
  （JSON以外のresume向け）を設定してください。
- `sessionMode`:
  - `always`: 常にセッションidを送信します（保存済みのものがなければ新しいUUID）。
  - `existing`: 以前に保存されたセッションidがある場合のみ送信します。
  - `none`: セッションidを送信しません。

シリアライズに関する注意:

- `serialize: true` は同一レーンの実行順を保ちます。
- ほとんどのCLIは1つのprovider lane上でシリアライズされます。
- OpenClawは、再ログイン、トークンローテーション、または認証プロファイルの認証情報変更を含め、バックエンドの認証状態が変わると、保存済みCLIセッションの再利用を破棄します。

## 画像（そのまま渡す）

CLIが画像パスを受け付ける場合は、`imageArg` を設定してください:

```json5
imageArg: "--image",
imageMode: "repeat"
```

OpenClawはbase64画像を一時ファイルに書き出します。`imageArg` が設定されていれば、それらのパスがCLI引数として渡されます。`imageArg` がない場合、OpenClawはファイルパスをプロンプトに追加します（パス注入）。これは、プレーンなパスからローカルファイルを自動読み込みするCLIには十分です。

## 入力 / 出力

- `output: "json"`（デフォルト）はJSONを解析し、テキスト + セッションidの抽出を試みます。
- Gemini CLIのJSON出力では、`usage` が存在しないか空の場合、OpenClawは返信テキストを `response` から、使用量を `stats` から読み取ります。
- `output: "jsonl"` はJSONLストリーム（たとえば Codex CLI `--json`）を解析し、存在すれば最終的なエージェントメッセージとセッション識別子を抽出します。
- `output: "text"` はstdoutを最終応答として扱います。

入力モード:

- `input: "arg"`（デフォルト）は、プロンプトを最後のCLI引数として渡します。
- `input: "stdin"` は、プロンプトをstdin経由で送信します。
- プロンプトが非常に長く、`maxPromptArgChars` が設定されている場合は、stdinが使われます。

## デフォルト（プラグイン所有）

バンドルされたOpenAIプラグインは、`codex-cli` のデフォルトも登録します:

- `command: "codex"`
- `args: ["exec","--json","--color","never","--sandbox","workspace-write","--skip-git-repo-check"]`
- `resumeArgs: ["exec","resume","{sessionId}","--color","never","--sandbox","workspace-write","--skip-git-repo-check"]`
- `output: "jsonl"`
- `resumeOutput: "text"`
- `modelArg: "--model"`
- `imageArg: "--image"`
- `sessionMode: "existing"`

バンドルされたGoogleプラグインは、`google-gemini-cli` のデフォルトも登録します:

- `command: "gemini"`
- `args: ["--prompt", "--output-format", "json"]`
- `resumeArgs: ["--resume", "{sessionId}", "--prompt", "--output-format", "json"]`
- `modelArg: "--model"`
- `sessionMode: "existing"`
- `sessionIdFields: ["session_id", "sessionId"]`

前提条件: ローカルのGemini CLIがインストールされ、`PATH` 上で
`gemini` として利用可能である必要があります（`brew install gemini-cli` または
`npm install -g @google/gemini-cli`）。

Gemini CLIのJSONに関する注意:

- 返信テキストはJSONの `response` フィールドから読み取られます。
- 使用量は、`usage` が存在しない場合または空の場合に `stats` にフォールバックします。
- `stats.cached` はOpenClawの `cacheRead` に正規化されます。
- `stats.input` が存在しない場合、OpenClawは
  `stats.input_tokens - stats.cached` から入力トークンを導出します。

必要な場合のみ上書きしてください（一般的なのは `command` の絶対パスです）。

## プラグイン所有のデフォルト

CLIバックエンドのデフォルトは、現在プラグインサーフェスの一部です:

- プラグインは `api.registerCliBackend(...)` でそれらを登録します。
- バックエンドの `id` がモデル参照におけるprovider prefixになります。
- `agents.defaults.cliBackends.<id>` 内のユーザー設定は、引き続きプラグインのデフォルトを上書きします。
- バックエンド固有の設定クリーンアップは、オプションの
  `normalizeConfig` フックを通じて引き続きプラグイン所有です。

## bundle MCPオーバーレイ

CLIバックエンドは**OpenClaw tool calls**を直接受け取りませんが、バックエンドは
`bundleMcp: true` によって生成されたMCP設定オーバーレイへオプトインできます。

現在のバンドル済み挙動:

- `codex-cli`: bundle MCPオーバーレイなし
- `google-gemini-cli`: bundle MCPオーバーレイなし

bundle MCPが有効な場合、OpenClawは次を行います:

- GatewayツールをCLIプロセスに公開するloopback HTTP MCPサーバーを起動する
- セッションごとのトークン（`OPENCLAW_MCP_TOKEN`）でブリッジを認証する
- ツールアクセスを現在のセッション、アカウント、およびチャネルコンテキストに限定する
- 現在のワークスペースで有効なbundle-MCPサーバーを読み込む
- それらを既存のバックエンド `--mcp-config` とマージする
- CLI引数を書き換え、`--strict-mcp-config --mcp-config <generated-file>` を渡す

有効なMCPサーバーがない場合でも、バックエンドがbundle MCPへオプトインしていれば、バックグラウンド実行を分離したままにするため、OpenClawは厳格な設定を注入します。

## 制限事項

- **直接のOpenClaw tool callsはありません。** OpenClawは、CLIバックエンドプロトコルにツール呼び出しを注入しません。バックエンドが `bundleMcp: true` にオプトインした場合にのみ、Gatewayツールを見ることができます。
- **ストリーミングはバックエンド依存です。** JSONLをストリームするバックエンドもあれば、終了までバッファするものもあります。
- **構造化出力** はCLIのJSON形式に依存します。
- **Codex CLI sessions** はテキスト出力経由で再開されます（JSONLではありません）。そのため、初回の `--json` 実行よりも構造化度は低くなります。それでもOpenClawセッションは通常どおり動作します。

## トラブルシューティング

- **CLIが見つからない**: `command` をフルパスに設定してください。
- **モデル名が違う**: `modelAliases` を使って `provider/model` → CLIモデルへマッピングしてください。
- **セッション継続性がない**: `sessionArg` が設定され、`sessionMode` が
  `none` ではないことを確認してください（Codex CLIは現在JSON出力で再開できません）。
- **画像が無視される**: `imageArg` を設定し（CLIがファイルパスをサポートしていることも確認してください）。
