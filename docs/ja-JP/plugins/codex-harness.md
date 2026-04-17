---
read_when:
    - バンドルされた Codex app-server ハーネスを使いたい場合
    - Codex のモデル参照と設定例が必要です
    - Codex 専用デプロイ向けに PI フォールバックを無効にしたい場合
summary: バンドルされた Codex app-server ハーネスを通じて OpenClaw の埋め込みエージェントターンを実行する
title: Codex ハーネス
x-i18n:
    generated_at: "2026-04-11T02:46:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: 60e1dcf4f1a00c63c3ef31d72feac44bce255421c032c58fa4fd67295b3daf23
    source_path: plugins/codex-harness.md
    workflow: 15
---

# Codex ハーネス

バンドルされた `codex` plugin により、OpenClaw は組み込み PI ハーネスの代わりに
Codex app-server を通して埋め込みエージェントターンを実行できます。

これは、低レベルのエージェントセッションを Codex に担わせたい場合に使用します: モデル
ディスカバリー、ネイティブスレッド再開、ネイティブ compaction、app-server 実行です。
OpenClaw は引き続き、チャットチャネル、セッションファイル、モデル選択、ツール、
approvals、メディア配信、および可視のトランスクリプトミラーを管理します。

このハーネスはデフォルトでオフです。`codex` plugin が
有効で、解決されたモデルが `codex/*` モデルである場合、または
`embeddedHarness.runtime: "codex"` か `OPENCLAW_AGENT_RUNTIME=codex` を明示的に強制した場合にのみ選択されます。
`codex/*` を一切設定しなければ、既存の PI、OpenAI、Anthropic、Gemini、local、
および custom-provider の実行は現在の動作を維持します。

## 正しいモデルプレフィックスを選ぶ

OpenClaw には、OpenAI アクセス用と Codex 形式アクセス用の別々の経路があります:

| モデル参照 | ランタイム経路 | 使用する場面 |
| ---------------------- | -------------------------------------------- | ----------------------------------------------------------------------- |
| `openai/gpt-5.4` | OpenClaw/PI 配線を通る OpenAI provider | `OPENAI_API_KEY` を使った直接の OpenAI Platform API アクセスが必要な場合。 |
| `openai-codex/gpt-5.4` | PI を通る OpenAI Codex OAuth provider | Codex app-server ハーネスなしで ChatGPT/Codex OAuth を使いたい場合。 |
| `codex/gpt-5.4` | バンドルされた Codex provider + Codex ハーネス | 埋め込みエージェントターンでネイティブな Codex app-server 実行を使いたい場合。 |

Codex ハーネスが引き受けるのは `codex/*` モデル参照だけです。既存の `openai/*`、
`openai-codex/*`、Anthropic、Gemini、xAI、local、および custom provider 参照は、
通常の経路のままです。

## 要件

- バンドルされた `codex` plugin が利用可能な OpenClaw。
- Codex app-server `0.118.0` 以降。
- app-server プロセスで利用可能な Codex auth。

この plugin は、古い app-server ハンドシェイクまたはバージョンなしの app-server ハンドシェイクをブロックします。これにより、
OpenClaw はテスト済みのプロトコルサーフェス上に保たれます。

ライブおよび Docker スモークテストでは、auth は通常 `OPENAI_API_KEY` と、
必要に応じて `~/.codex/auth.json` や
`~/.codex/config.toml` のような Codex CLI ファイルから取得されます。ローカルの Codex app-server と同じ auth 情報を使ってください。

## 最小構成

`codex/gpt-5.4` を使用し、バンドルされた plugin を有効化し、`codex` ハーネスを強制します:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
  agents: {
    defaults: {
      model: "codex/gpt-5.4",
      embeddedHarness: {
        runtime: "codex",
        fallback: "none",
      },
    },
  },
}
```

設定で `plugins.allow` を使用している場合は、そこにも `codex` を含めてください:

```json5
{
  plugins: {
    allow: ["codex"],
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
}
```

`agents.defaults.model` またはエージェントモデルを `codex/<model>` に設定しても、
バンドルされた `codex` plugin は自動的に有効になります。明示的な plugin エントリは、
共有設定でデプロイ意図を明確に示せるため、依然として有用です。

## 他のモデルを置き換えずに Codex を追加する

`codex/*` モデルには Codex、その他すべてには PI を使いたい場合は `runtime: "auto"` のままにします:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
  agents: {
    defaults: {
      model: {
        primary: "codex/gpt-5.4",
        fallbacks: ["openai/gpt-5.4", "anthropic/claude-opus-4-6"],
      },
      models: {
        "codex/gpt-5.4": { alias: "codex" },
        "codex/gpt-5.4-mini": { alias: "codex-mini" },
        "openai/gpt-5.4": { alias: "gpt" },
        "anthropic/claude-opus-4-6": { alias: "opus" },
      },
      embeddedHarness: {
        runtime: "auto",
        fallback: "pi",
      },
    },
  },
}
```

この構成では:

- `/model codex` または `/model codex/gpt-5.4` は Codex app-server ハーネスを使用します。
- `/model gpt` または `/model openai/gpt-5.4` は OpenAI provider 経路を使用します。
- `/model opus` は Anthropic provider 経路を使用します。
- Codex 以外のモデルが選択された場合、PI は互換性ハーネスのままです。

## Codex 専用デプロイ

すべての埋め込みエージェントターンが
Codex ハーネスを使うことを保証したい場合は、PI フォールバックを無効にします:

```json5
{
  agents: {
    defaults: {
      model: "codex/gpt-5.4",
      embeddedHarness: {
        runtime: "codex",
        fallback: "none",
      },
    },
  },
}
```

環境変数での上書き:

```bash
OPENCLAW_AGENT_RUNTIME=codex \
OPENCLAW_AGENT_HARNESS_FALLBACK=none \
openclaw gateway run
```

フォールバックを無効にすると、Codex plugin が無効、
要求されたモデルが `codex/*` 参照ではない、app-server が古すぎる、または
app-server を起動できない場合に、OpenClaw は早い段階で失敗します。

## エージェントごとの Codex

あるエージェントだけを Codex 専用にしつつ、デフォルトエージェントは通常の
自動選択を維持できます:

```json5
{
  agents: {
    defaults: {
      embeddedHarness: {
        runtime: "auto",
        fallback: "pi",
      },
    },
    list: [
      {
        id: "main",
        default: true,
        model: "anthropic/claude-opus-4-6",
      },
      {
        id: "codex",
        name: "Codex",
        model: "codex/gpt-5.4",
        embeddedHarness: {
          runtime: "codex",
          fallback: "none",
        },
      },
    ],
  },
}
```

通常のセッションコマンドを使ってエージェントとモデルを切り替えます。`/new` は新しい
OpenClaw セッションを作成し、Codex ハーネスは必要に応じてその sidecar app-server
スレッドを作成または再開します。`/reset` はそのスレッドの OpenClaw セッションバインディングをクリアします。

## モデルディスカバリー

デフォルトでは、Codex plugin は利用可能なモデルを app-server に問い合わせます。
ディスカバリーが失敗するかタイムアウトした場合は、バンドルされたフォールバックカタログを使用します:

- `codex/gpt-5.4`
- `codex/gpt-5.4-mini`
- `codex/gpt-5.2`

ディスカバリーは `plugins.entries.codex.config.discovery` で調整できます:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          discovery: {
            enabled: true,
            timeoutMs: 2500,
          },
        },
      },
    },
  },
}
```

起動時に Codex を probe せず、フォールバックカタログに固定したい場合は、
ディスカバリーを無効にします:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          discovery: {
            enabled: false,
          },
        },
      },
    },
  },
}
```

## app-server 接続とポリシー

デフォルトでは、この plugin は次のコマンドでローカルに Codex を起動します:

```bash
codex app-server --listen stdio://
```

このデフォルトを維持しつつ、Codex ネイティブポリシーだけを調整できます:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          appServer: {
            approvalPolicy: "on-request",
            sandbox: "workspace-write",
            serviceTier: "priority",
          },
        },
      },
    },
  },
}
```

すでに起動中の app-server には、WebSocket トランスポートを使用します:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          appServer: {
            transport: "websocket",
            url: "ws://127.0.0.1:39175",
            authToken: "${CODEX_APP_SERVER_TOKEN}",
            requestTimeoutMs: 60000,
          },
        },
      },
    },
  },
}
```

サポートされる `appServer` フィールド:

| フィールド | デフォルト | 意味 |
| ------------------- | ---------------------------------------- | ------------------------------------------------------------------------ |
| `transport` | `"stdio"` | `"stdio"` は Codex を起動します。`"websocket"` は `url` に接続します。 |
| `command` | `"codex"` | stdio トランスポート用の実行ファイル。 |
| `args` | `["app-server", "--listen", "stdio://"]` | stdio トランスポート用の引数。 |
| `url` | 未設定 | WebSocket app-server URL。 |
| `authToken` | 未設定 | WebSocket トランスポート用の Bearer token。 |
| `headers` | `{}` | 追加の WebSocket ヘッダー。 |
| `requestTimeoutMs` | `60000` | app-server コントロールプレーン呼び出しのタイムアウト。 |
| `approvalPolicy` | `"never"` | スレッド start/resume/turn に送信されるネイティブ Codex approval policy。 |
| `sandbox` | `"workspace-write"` | スレッド start/resume に送信されるネイティブ Codex sandbox モード。 |
| `approvalsReviewer` | `"user"` | ネイティブ approvals を Codex guardian にレビューさせるには `"guardian_subagent"` を使用します。 |
| `serviceTier` | 未設定 | 任意の Codex service tier。たとえば `"priority"`。 |

古い環境変数も、対応する設定フィールドが未設定なら、
ローカルテスト用のフォールバックとして引き続き利用できます:

- `OPENCLAW_CODEX_APP_SERVER_BIN`
- `OPENCLAW_CODEX_APP_SERVER_ARGS`
- `OPENCLAW_CODEX_APP_SERVER_APPROVAL_POLICY`
- `OPENCLAW_CODEX_APP_SERVER_SANDBOX`
- `OPENCLAW_CODEX_APP_SERVER_GUARDIAN=1`

再現可能なデプロイには設定の使用が推奨されます。

## よくあるレシピ

デフォルトの stdio トランスポートを使うローカル Codex:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
}
```

PI フォールバックを無効にした Codex 専用ハーネスの検証:

```json5
{
  embeddedHarness: {
    fallback: "none",
  },
  plugins: {
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
}
```

guardian レビュー付き Codex approvals:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          appServer: {
            approvalPolicy: "on-request",
            approvalsReviewer: "guardian_subagent",
            sandbox: "workspace-write",
          },
        },
      },
    },
  },
}
```

明示的なヘッダー付きのリモート app-server:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          appServer: {
            transport: "websocket",
            url: "ws://gateway-host:39175",
            headers: {
              "X-OpenClaw-Agent": "main",
            },
          },
        },
      },
    },
  },
}
```

モデル切り替えは引き続き OpenClaw が制御します。OpenClaw セッションが既存の Codex スレッドに接続されている場合、
次のターンでは、現在選択されている
`codex/*` モデル、provider、approval policy、sandbox、および service tier が
再び app-server に送信されます。`codex/gpt-5.4` から `codex/gpt-5.2` に切り替えると、
スレッドバインディングは維持されますが、Codex には新しく選択されたモデルで継続するよう要求します。

## Codex コマンド

バンドルされた plugin は、認可されたスラッシュコマンドとして `/codex` を登録します。これは
汎用的で、OpenClaw のテキストコマンドをサポートする任意のチャネルで動作します。

一般的な形式:

- `/codex status` は、ライブの app-server 接続性、モデル、アカウント、レート制限、MCP サーバー、および Skills を表示します。
- `/codex models` は、ライブの Codex app-server モデルを一覧表示します。
- `/codex threads [filter]` は、最近の Codex スレッドを一覧表示します。
- `/codex resume <thread-id>` は、現在の OpenClaw セッションを既存の Codex スレッドに接続します。
- `/codex compact` は、接続されたスレッドの compaction を Codex app-server に要求します。
- `/codex review` は、接続されたスレッドに対して Codex ネイティブレビューを開始します。
- `/codex account` は、アカウントとレート制限の状態を表示します。
- `/codex mcp` は、Codex app-server の MCP サーバー状態を一覧表示します。
- `/codex skills` は、Codex app-server の Skills を一覧表示します。

`/codex resume` は、ハーネスが通常ターンで使用するものと同じ sidecar バインディングファイルを書き込みます。
次のメッセージで、OpenClaw はその Codex スレッドを再開し、現在選択されている OpenClaw の
`codex/*` モデルを app-server に渡し、拡張履歴を有効のまま維持します。

コマンドサーフェスには Codex app-server `0.118.0` 以降が必要です。将来版またはカスタム app-server がその JSON-RPC メソッドを公開していない場合、個々の
制御メソッドは `unsupported by this Codex app-server` として報告されます。

## ツール、メディア、および compaction

Codex ハーネスが変更するのは、低レベルの埋め込みエージェント実行器のみです。

OpenClaw は引き続きツール一覧を構築し、ハーネスから動的なツール結果を受け取ります。テキスト、画像、動画、音楽、TTS、approvals、およびメッセージングツール出力は、
通常どおり OpenClaw の配信経路を通ります。

選択されたモデルが Codex ハーネスを使う場合、ネイティブスレッド compaction は
Codex app-server に委譲されます。OpenClaw は、チャネル履歴、検索、`/new`、`/reset`、および将来のモデルまたはハーネス切り替えのために、トランスクリプトミラーを維持します。この
ミラーには、ユーザープロンプト、最終 assistant テキスト、および
app-server が出力した場合の軽量な Codex reasoning または plan レコードが含まれます。

メディア生成に PI は不要です。画像、動画、音楽、PDF、TTS、およびメディア理解は、
引き続き `agents.defaults.imageGenerationModel`、`videoGenerationModel`、`pdfModel`、`messages.tts` のような対応する provider/model 設定を使用します。

## トラブルシューティング

**`/model` に Codex が表示されない:** `plugins.entries.codex.enabled` を有効にし、
`codex/*` モデル参照を設定するか、`plugins.allow` が `codex` を除外していないか確認してください。

**OpenClaw が PI にフォールバックする:** テスト中は `embeddedHarness.fallback: "none"` または
`OPENCLAW_AGENT_HARNESS_FALLBACK=none` を設定してください。

**app-server が拒否される:** app-server ハンドシェイクが
バージョン `0.118.0` 以降を報告するように Codex をアップグレードしてください。

**モデルディスカバリーが遅い:** `plugins.entries.codex.config.discovery.timeoutMs`
を下げるか、ディスカバリーを無効にしてください。

**WebSocket トランスポートがすぐに失敗する:** `appServer.url`、`authToken`、
およびリモート app-server が同じ Codex app-server プロトコルバージョンを話していることを確認してください。

**Codex 以外のモデルが PI を使う:** それは想定どおりです。Codex ハーネスが引き受けるのは
`codex/*` モデル参照だけです。

## 関連

- [Agent Harness Plugins](/ja-JP/plugins/sdk-agent-harness)
- [Model Providers](/ja-JP/concepts/model-providers)
- [Configuration Reference](/ja-JP/gateway/configuration-reference)
- [Testing](/ja-JP/help/testing#live-codex-app-server-harness-smoke)
