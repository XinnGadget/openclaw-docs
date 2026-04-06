---
read_when: You hit 'sandbox jail' or see a tool/elevated refusal and want the exact config key to change.
status: active
summary: 'ツールがブロックされる理由: サンドボックスランタイム、ツール許可/拒否ポリシー、昇格 exec ゲート'
title: Sandbox と Tool Policy と Elevated の違い
x-i18n:
    generated_at: "2026-04-06T03:07:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: 331f5b2f0d5effa1320125d9f29948e16d0deaffa59eb1e4f25a63481cbe22d6
    source_path: gateway/sandbox-vs-tool-policy-vs-elevated.md
    workflow: 15
---

# Sandbox と Tool Policy と Elevated の違い

OpenClaw には、関連はあるものの異なる 3 つの制御があります。

1. **Sandbox**（`agents.defaults.sandbox.*` / `agents.list[].sandbox.*`）は、**ツールをどこで実行するか**（Docker かホストか）を決定します。
2. **Tool policy**（`tools.*`、`tools.sandbox.tools.*`、`agents.list[].tools.*`）は、**どのツールを利用可能/許可するか**を決定します。
3. **Elevated**（`tools.elevated.*`、`agents.list[].tools.elevated.*`）は、サンドボックス化されているときに、サンドボックス外で実行するための **exec 専用のエスケープハッチ** です（デフォルトでは `gateway`、または exec ターゲットが `node` に設定されている場合は `node`）。

## クイックデバッグ

インスペクターを使って、OpenClaw が _実際に何をしているか_ を確認してください。

```bash
openclaw sandbox explain
openclaw sandbox explain --session agent:main:main
openclaw sandbox explain --agent work
openclaw sandbox explain --json
```

出力内容:

- 有効なサンドボックスモード/スコープ/ワークスペースアクセス
- セッションが現在サンドボックス化されているかどうか（main か non-main か）
- 有効なサンドボックスツール許可/拒否（およびそれが agent/global/default のどこから来たか）
- Elevated のゲートと修正用キーのパス

## Sandbox: ツールをどこで実行するか

サンドボックス化は `agents.defaults.sandbox.mode` で制御されます。

- `"off"`: すべてホスト上で実行されます。
- `"non-main"`: non-main セッションのみサンドボックス化されます（グループ/チャンネルでよくある「意外な挙動」）。
- `"all"`: すべてサンドボックス化されます。

完全なマトリクス（スコープ、ワークスペースマウント、イメージ）については [Sandboxing](/ja-JP/gateway/sandboxing) を参照してください。

### バインドマウント（セキュリティのクイックチェック）

- `docker.binds` はサンドボックスファイルシステムを_貫通_します。マウントしたものは、設定したモード（`:ro` または `:rw`）でコンテナ内から見えるようになります。
- モードを省略するとデフォルトは read-write です。ソース/シークレットには `:ro` を推奨します。
- `scope: "shared"` はエージェントごとのバインドを無視します（グローバルバインドのみが適用されます）。
- OpenClaw はバインド元を 2 回検証します。まず正規化されたソースパスで、次に最も深い既存祖先を通して解決した後でもう一度検証します。シンボリックリンク親を使ったエスケープでは、blocked-path や allowed-root のチェックは回避できません。
- 存在しない末端パスも安全に検査されます。`/workspace/alias-out/new-file` がシンボリックリンクされた親を通して blocked path や設定済み allowed roots の外に解決される場合、そのバインドは拒否されます。
- `/var/run/docker.sock` をバインドすると、実質的にサンドボックスへホスト制御を渡すことになります。意図的な場合にのみ行ってください。
- ワークスペースアクセス（`workspaceAccess: "ro"`/`"rw"`）はバインドモードとは独立しています。

## Tool policy: どのツールが存在し、呼び出せるか

重要なのは 2 つのレイヤーです。

- **Tool profile**: `tools.profile` と `agents.list[].tools.profile`（基本許可リスト）
- **Provider tool profile**: `tools.byProvider[provider].profile` と `agents.list[].tools.byProvider[provider].profile`
- **Global/per-agent tool policy**: `tools.allow`/`tools.deny` と `agents.list[].tools.allow`/`agents.list[].tools.deny`
- **Provider tool policy**: `tools.byProvider[provider].allow/deny` と `agents.list[].tools.byProvider[provider].allow/deny`
- **Sandbox tool policy**（サンドボックス化されているときにのみ適用）: `tools.sandbox.tools.allow`/`tools.sandbox.tools.deny` と `agents.list[].tools.sandbox.tools.*`

経験則:

- `deny` が常に優先されます。
- `allow` が空でない場合、それ以外はすべてブロックとして扱われます。
- Tool policy は最終的な停止点です。拒否された `exec` ツールを `/exec` で上書きすることはできません。
- `/exec` は認可された送信者に対してセッションデフォルトを変更するだけで、ツールアクセスを付与しません。
  Provider tool キーには、`provider`（例: `google-antigravity`）または `provider/model`（例: `openai/gpt-5.4`）のどちらも使用できます。

### Tool groups（ショートハンド）

Tool policy（global、agent、sandbox）は、複数のツールに展開される `group:*` エントリをサポートします。

```json5
{
  tools: {
    sandbox: {
      tools: {
        allow: ["group:runtime", "group:fs", "group:sessions", "group:memory"],
      },
    },
  },
}
```

利用可能なグループ:

- `group:runtime`: `exec`, `process`, `code_execution`（`bash` は `exec` のエイリアスとして受け入れられます）
- `group:fs`: `read`, `write`, `edit`, `apply_patch`
- `group:sessions`: `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `sessions_yield`, `subagents`, `session_status`
- `group:memory`: `memory_search`, `memory_get`
- `group:web`: `web_search`, `x_search`, `web_fetch`
- `group:ui`: `browser`, `canvas`
- `group:automation`: `cron`, `gateway`
- `group:messaging`: `message`
- `group:nodes`: `nodes`
- `group:agents`: `agents_list`
- `group:media`: `image`, `image_generate`, `video_generate`, `tts`
- `group:openclaw`: すべての組み込み OpenClaw ツール（provider plugin は除く）

## Elevated: exec 専用の「ホストで実行」

Elevated は追加のツールを付与しません。影響するのは `exec` のみです。

- サンドボックス化されている場合、`/elevated on`（または `elevated: true` を付けた `exec`）はサンドボックス外で実行されます（承認が引き続き必要な場合があります）。
- セッションの exec 承認をスキップするには `/elevated full` を使用します。
- すでに直接実行されている場合、elevated は実質的に no-op です（それでもゲートは適用されます）。
- Elevated は **skill スコープではなく**、ツールの allow/deny も上書きしません。
- Elevated は `host=auto` から任意のクロスホスト上書きを付与しません。通常の exec ターゲットルールに従い、設定済み/セッションターゲットがすでに `node` の場合にのみ `node` を維持します。
- `/exec` は elevated とは別です。認可された送信者に対して、セッションごとの exec デフォルトを調整するだけです。

ゲート:

- 有効化: `tools.elevated.enabled`（および必要に応じて `agents.list[].tools.elevated.enabled`）
- 送信者許可リスト: `tools.elevated.allowFrom.<provider>`（および必要に応じて `agents.list[].tools.elevated.allowFrom.<provider>`）

[Elevated Mode](/ja-JP/tools/elevated) も参照してください。

## よくある「sandbox jail」の修正

### 「Tool X blocked by sandbox tool policy」

修正用キー（いずれかを選択）:

- サンドボックスを無効化する: `agents.defaults.sandbox.mode=off`（またはエージェント単位で `agents.list[].sandbox.mode=off`）
- サンドボックス内でそのツールを許可する:
  - `tools.sandbox.tools.deny`（またはエージェント単位の `agents.list[].tools.sandbox.tools.deny`）から削除する
  - または `tools.sandbox.tools.allow`（またはエージェント単位の allow）に追加する

### 「main だと思っていたのに、なぜサンドボックス化されているのですか？」

`"non-main"` モードでは、グループ/チャンネルキーは main ではありません。main セッションキー（`sandbox explain` に表示されます）を使用するか、モードを `"off"` に切り替えてください。

## 関連項目

- [Sandboxing](/ja-JP/gateway/sandboxing) -- サンドボックスの完全なリファレンス（モード、スコープ、バックエンド、イメージ）
- [Multi-Agent Sandbox & Tools](/ja-JP/tools/multi-agent-sandbox-tools) -- エージェント単位の上書きと優先順位
- [Elevated Mode](/ja-JP/tools/elevated)
