---
read_when:
    - APIプロバイダーが失敗したときに信頼できるフォールバックが必要な場合
    - Codex CLIまたは他のローカルAI CLIを実行していて、それらを再利用したい場合
    - CLIバックエンドのツールアクセス向けMCP loopbackブリッジを理解したい場合
summary: 'CLIバックエンド: オプションのMCPツールブリッジを備えたローカルAI CLIフォールバック'
title: CLIバックエンド
x-i18n:
    generated_at: "2026-04-08T02:14:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: b0e8c41f5f5a8e34466f6b765e5c08585ef1788fa9e9d953257324bcc6cbc414
    source_path: gateway/cli-backends.md
    workflow: 15
---

# CLIバックエンド（フォールバックランタイム）

OpenClawは、APIプロバイダーが停止している、レート制限されている、
または一時的に不安定なときに、**ローカルAI CLI**を**テキスト専用フォールバック**として実行できます。
これは意図的に保守的な設計です:

- **OpenClawツールは直接注入されません**が、`bundleMcp: true` を持つバックエンドは
  loopback MCPブリッジ経由でGatewayツールを受け取ることができます。
- これに対応するCLI向けの**JSONLストリーミング**。
- **セッションに対応**しています（そのため、後続のターンでも一貫性が保たれます）。
- CLIが画像パスを受け付ける場合は、**画像をそのまま渡す**ことができます。

これは主要な経路ではなく、**セーフティネット**として設計されています。
外部APIに依存せずに「常に動く」テキスト応答が必要なときに使ってください。

ACPセッション制御、バックグラウンドタスク、
thread/conversationバインディング、永続的な外部コーディングセッションを備えた
完全なハーネスランタイムが必要な場合は、
代わりに[ACP Agents](/ja-JP/tools/acp-agents)を使用してください。CLIバックエンドはACPではありません。

## 初心者向けクイックスタート

Codex CLIは**設定なし**で使えます（バンドルされたOpenAIプラグインが
デフォルトのバックエンドを登録します）:

```bash
openclaw agent --message "hi" --model codex-cli/gpt-5.4
```

Gatewayがlaunchd/systemd配下で動作していてPATHが最小限の場合は、
コマンドパスだけを追加してください:

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

これで完了です。CLI自体に必要なものを除いて、キーも追加の認証設定も不要です。

Gatewayホスト上で、バンドルされたCLIバックエンドを**主要なメッセージプロバイダー**として使用する場合、
OpenClawは、設定でそのバックエンドがモデル参照内または
`agents.defaults.cliBackends` 配下に明示的に指定されていれば、
その所有元のバンドルプラグインを自動で読み込みます。

## フォールバックとして使用する

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

- `agents.defaults.models`（許可リスト）を使う場合は、CLIバックエンドのモデルもそこに含める必要があります。
- 主要プロバイダーが失敗した場合（認証、レート制限、タイムアウト）、OpenClawは
  次にCLIバックエンドを試します。

## 設定の概要

すべてのCLIバックエンドは次の配下にあります:

```
agents.defaults.cliBackends
```

各エントリは**provider id**（例: `codex-cli`, `my-cli`）をキーとして持ちます。
provider idはモデル参照の左側になります:

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

1. providerプレフィックス（`codex-cli/...`）に基づいて**バックエンドを選択**します。
2. 同じOpenClawプロンプトとワークスペースコンテキストを使って**システムプロンプトを構築**します。
3. 履歴の一貫性が保たれるよう、対応していればセッションID付きで**CLIを実行**します。
4. 出力（JSONまたはプレーンテキスト）を**解析**し、最終テキストを返します。
5. バックエンドごとにセッションIDを**永続化**し、後続のやり取りで同じCLIセッションを再利用します。

<Note>
バンドルされたAnthropic `claude-cli` バックエンドが再びサポートされました。Anthropicのスタッフから、
OpenClawスタイルのClaude CLI利用は再び許可されていると聞いているため、Anthropicが
新しいポリシーを公開しない限り、OpenClawはこの統合における `claude -p` の使用を
正式に認められたものとして扱います。
</Note>

## セッション

- CLIがセッションに対応している場合は、`sessionArg`（例: `--session-id`）または
  `sessionArgs`（プレースホルダー `{sessionId}`）を設定してください。これはIDを
  複数のフラグに挿入する必要がある場合に使います。
- CLIが異なるフラグを持つ**resumeサブコマンド**を使う場合は、
  `resumeArgs`（再開時に `args` を置き換えます）を設定し、必要であれば
  `resumeOutput`（非JSONの再開用）も設定してください。
- `sessionMode`:
  - `always`: 常にセッションIDを送信します（保存済みのものがなければ新しいUUID）。
  - `existing`: 以前に保存されたセッションIDがある場合にのみ送信します。
  - `none`: セッションIDを送信しません。

シリアライズに関する注意:

- `serialize: true` は、同じレーンでの実行順を維持します。
- ほとんどのCLIは1つのproviderレーンでシリアライズされます。
- OpenClawは、バックエンドの認証状態が変わると、保存済みCLIセッションの再利用を破棄します。これには
  再ログイン、トークンのローテーション、認証プロファイル資格情報の変更が含まれます。

## 画像（そのまま受け渡し）

CLIが画像パスを受け付ける場合は、`imageArg` を設定してください:

```json5
imageArg: "--image",
imageMode: "repeat"
```

OpenClawはbase64画像を一時ファイルに書き出します。`imageArg` が設定されていれば、
それらのパスはCLI引数として渡されます。`imageArg` がない場合、OpenClawは
ファイルパスをプロンプトに追記します（パス注入）。これは、プレーンなパスから
ローカルファイルを自動読み込みするCLIには十分です。

## 入力 / 出力

- `output: "json"`（デフォルト）は、JSONを解析してテキストとセッションIDの抽出を試みます。
- Gemini CLIのJSON出力については、`usage` が存在しないか空の場合、
  OpenClawは返信テキストを `response` から、使用量を `stats` から読み取ります。
- `output: "jsonl"` はJSONLストリーム（たとえばCodex CLI `--json`）を解析し、存在する場合は最終エージェントメッセージとセッション
  識別子を抽出します。
- `output: "text"` は、stdoutを最終応答として扱います。

入力モード:

- `input: "arg"`（デフォルト）は、最後のCLI引数としてプロンプトを渡します。
- `input: "stdin"` は、stdin経由でプロンプトを送信します。
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

バンドルされたGoogleプラグインも、`google-gemini-cli` のデフォルトを登録します:

- `command: "gemini"`
- `args: ["--output-format", "json", "--prompt", "{prompt}"]`
- `resumeArgs: ["--resume", "{sessionId}", "--output-format", "json", "--prompt", "{prompt}"]`
- `imageArg: "@"`
- `imagePathScope: "workspace"`
- `modelArg: "--model"`
- `sessionMode: "existing"`
- `sessionIdFields: ["session_id", "sessionId"]`

前提条件: ローカルのGemini CLIがインストールされ、`PATH` 上で
`gemini` として利用可能である必要があります（`brew install gemini-cli` または
`npm install -g @google/gemini-cli`）。

Gemini CLIのJSONに関する注意:

- 返信テキストはJSONの `response` フィールドから読み取られます。
- 使用量は、`usage` が存在しないか空の場合に `stats` へフォールバックします。
- `stats.cached` はOpenClawの `cacheRead` に正規化されます。
- `stats.input` がない場合、OpenClawは
  `stats.input_tokens - stats.cached` から入力トークン数を導出します。

必要な場合にのみ上書きしてください（よくあるのは絶対 `command` パスです）。

## プラグイン所有のデフォルト

CLIバックエンドのデフォルトは、現在ではプラグインサーフェスの一部です:

- プラグインは `api.registerCliBackend(...)` でこれらを登録します。
- バックエンドの `id` は、モデル参照のproviderプレフィックスになります。
- `agents.defaults.cliBackends.<id>` にあるユーザー設定は、引き続きプラグインのデフォルトを上書きします。
- バックエンド固有の設定クリーンアップは、オプションの
  `normalizeConfig` フックを通じてプラグイン所有のまま維持されます。

## Bundle MCPオーバーレイ

CLIバックエンドは**OpenClawツール呼び出しを直接**受け取りませんが、バックエンドは
`bundleMcp: true` によって生成されたMCP設定オーバーレイにオプトインできます。

現在のバンドル動作:

- `claude-cli`: 生成されるstrict MCP設定ファイル
- `codex-cli`: `mcp_servers` 向けのインライン設定オーバーライド
- `google-gemini-cli`: 生成されるGeminiシステム設定ファイル

bundle MCPが有効な場合、OpenClawは次を行います:

- GatewayツールをCLIプロセスに公開するloopback HTTP MCPサーバーを起動する
- セッションごとのトークン（`OPENCLAW_MCP_TOKEN`）でブリッジを認証する
- 現在のセッション、アカウント、チャネルコンテキストにツールアクセスを限定する
- 現在のワークスペースで有効なbundle-MCPサーバーを読み込む
- それらを既存のバックエンドMCP設定/設定形状とマージする
- 所有元extensionのバックエンド所有統合モードを使って起動設定を書き換える

MCPサーバーが1つも有効でない場合でも、バックエンドがbundle MCPにオプトインしていれば、
OpenClawはバックグラウンド実行を分離したままにするためstrict設定を注入します。

## 制限事項

- **OpenClawツール呼び出しの直接利用はありません。** OpenClawは
  CLIバックエンドプロトコルにツール呼び出しを注入しません。バックエンドがGatewayツールを見るのは、
  `bundleMcp: true` にオプトインした場合だけです。
- **ストリーミングはバックエンド依存です。** JSONLをストリームするバックエンドもあれば、
  終了までバッファするバックエンドもあります。
- **構造化出力**はCLIのJSON形式に依存します。
- **Codex CLIセッション**はテキスト出力で再開されます（JSONLではありません）。そのため、
  初回の `--json` 実行より構造化が弱くなります。それでもOpenClawのセッションは通常どおり機能します。

## トラブルシューティング

- **CLIが見つからない**: `command` にフルパスを設定してください。
- **モデル名が間違っている**: `modelAliases` を使って `provider/model` → CLIモデル にマッピングしてください。
- **セッションの継続性がない**: `sessionArg` が設定されていて、`sessionMode` が
  `none` でないことを確認してください（Codex CLIは現在JSON出力で再開できません）。
- **画像が無視される**: `imageArg` を設定し（CLIがファイルパスに対応していることも確認してください）。
