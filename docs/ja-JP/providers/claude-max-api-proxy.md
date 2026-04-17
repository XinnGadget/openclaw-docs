---
read_when:
    - Claude Max サブスクリプションを OpenAI 互換ツールで使いたい場合
    - Claude Code CLI をラップするローカル API サーバーが欲しい場合
    - サブスクリプションベースの Anthropic アクセスと API キーベースのアクセスを比較検討したい場合
summary: Claude サブスクリプション認証情報を OpenAI 互換エンドポイントとして公開するコミュニティプロキシ
title: Claude Max API プロキシ
x-i18n:
    generated_at: "2026-04-12T23:30:35Z"
    model: gpt-5.4
    provider: openai
    source_hash: 534bc3d189e68529fb090258eb0d6db6d367eb7e027ad04b1f0be55f6aa7d889
    source_path: providers/claude-max-api-proxy.md
    workflow: 15
---

# Claude Max API プロキシ

**claude-max-api-proxy** は、Claude Max/Pro サブスクリプションを OpenAI 互換 API エンドポイントとして公開するコミュニティツールです。これにより、OpenAI API 形式をサポートする任意のツールでサブスクリプションを使用できます。

<Warning>
この経路は技術的な互換性のためのものにすぎません。Anthropic は過去に Claude Code 以外での一部のサブスクリプション利用をブロックしたことがあります。これを使用するかどうかは自身で判断し、依存する前に Anthropic の最新の利用規約を確認してください。
</Warning>

## なぜこれを使うのか

| アプローチ | コスト | 最適な用途 |
| ----------------------- | --------------------------------------------------- | ------------------------------------------ |
| Anthropic API | 従量課金（Opus では入力約 $15/M、出力約 $75/M） | 本番アプリ、高ボリューム |
| Claude Max サブスクリプション | 月額定額 $200 | 個人利用、開発、無制限利用 |

Claude Max サブスクリプションを持っていて、それを OpenAI 互換ツールで使いたい場合、このプロキシは一部のワークフローでコストを下げられる可能性があります。本番利用では、API キーのほうがポリシー上より明確な経路です。

## 仕組み

```
Your App → claude-max-api-proxy → Claude Code CLI → Anthropic (via subscription)
     (OpenAI format)              (converts format)      (uses your login)
```

このプロキシは以下を行います。

1. `http://localhost:3456/v1/chat/completions` で OpenAI 形式のリクエストを受け付けます
2. それらを Claude Code CLI コマンドに変換します
3. OpenAI 形式でレスポンスを返します（ストリーミング対応）

## はじめに

<Steps>
  <Step title="プロキシをインストールする">
    Node.js 20+ と Claude Code CLI が必要です。

    ```bash
    npm install -g claude-max-api-proxy

    # Claude CLI が認証済みであることを確認
    claude --version
    ```

  </Step>
  <Step title="サーバーを起動する">
    ```bash
    claude-max-api
    # サーバーは http://localhost:3456 で実行されます
    ```
  </Step>
  <Step title="プロキシをテストする">
    ```bash
    # ヘルスチェック
    curl http://localhost:3456/health

    # モデル一覧
    curl http://localhost:3456/v1/models

    # チャット補完
    curl http://localhost:3456/v1/chat/completions \
      -H "Content-Type: application/json" \
      -d '{
        "model": "claude-opus-4",
        "messages": [{"role": "user", "content": "Hello!"}]
      }'
    ```

  </Step>
  <Step title="OpenClaw を設定する">
    カスタムの OpenAI 互換エンドポイントとして、このプロキシを OpenClaw から参照するよう設定します。

    ```json5
    {
      env: {
        OPENAI_API_KEY: "not-needed",
        OPENAI_BASE_URL: "http://localhost:3456/v1",
      },
      agents: {
        defaults: {
          model: { primary: "openai/claude-opus-4" },
        },
      },
    }
    ```

  </Step>
</Steps>

## 利用可能なモデル

| モデル ID | 対応先 |
| ----------------- | --------------- |
| `claude-opus-4` | Claude Opus 4 |
| `claude-sonnet-4` | Claude Sonnet 4 |
| `claude-haiku-4` | Claude Haiku 4 |

## 高度な内容

<AccordionGroup>
  <Accordion title="プロキシ形式の OpenAI 互換に関する注意">
    この経路は、他のカスタム `/v1` バックエンドと同じプロキシ形式の OpenAI 互換ルートを使用します。

    - ネイティブな OpenAI 専用リクエスト整形は適用されません
    - `service_tier`、Responses の `store`、プロンプトキャッシュヒント、OpenAI 推論互換ペイロード整形はありません
    - 非表示の OpenClaw attribution ヘッダー（`originator`、`version`、`User-Agent`）はプロキシ URL に注入されません

  </Accordion>

  <Accordion title="LaunchAgent で macOS 上で自動起動する">
    プロキシを自動実行する LaunchAgent を作成します。

    ```bash
    cat > ~/Library/LaunchAgents/com.claude-max-api.plist << 'EOF'
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
      <key>Label</key>
      <string>com.claude-max-api</string>
      <key>RunAtLoad</key>
      <true/>
      <key>KeepAlive</key>
      <true/>
      <key>ProgramArguments</key>
      <array>
        <string>/usr/local/bin/node</string>
        <string>/usr/local/lib/node_modules/claude-max-api-proxy/dist/server/standalone.js</string>
      </array>
      <key>EnvironmentVariables</key>
      <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/opt/homebrew/bin:~/.local/bin:/usr/bin:/bin</string>
      </dict>
    </dict>
    </plist>
    EOF

    launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.claude-max-api.plist
    ```

  </Accordion>
</AccordionGroup>

## リンク

- **npm:** [https://www.npmjs.com/package/claude-max-api-proxy](https://www.npmjs.com/package/claude-max-api-proxy)
- **GitHub:** [https://github.com/atalovesyou/claude-max-api-proxy](https://github.com/atalovesyou/claude-max-api-proxy)
- **Issues:** [https://github.com/atalovesyou/claude-max-api-proxy/issues](https://github.com/atalovesyou/claude-max-api-proxy/issues)

## 注意

- これは **コミュニティツール** であり、Anthropic または OpenClaw が公式にサポートするものではありません
- Claude Code CLI で認証済みの、有効な Claude Max/Pro サブスクリプションが必要です
- このプロキシはローカルで実行され、データをサードパーティのサーバーには送信しません
- ストリーミングレスポンスは完全にサポートされています

<Note>
Claude CLI または API キーを使うネイティブな Anthropic 統合については、[Anthropic provider](/ja-JP/providers/anthropic) を参照してください。OpenAI/Codex サブスクリプションについては、[OpenAI provider](/ja-JP/providers/openai) を参照してください。
</Note>

## 関連

<CardGroup cols={2}>
  <Card title="Anthropic provider" href="/ja-JP/providers/anthropic" icon="bolt">
    Claude CLI または API キーを使うネイティブな OpenClaw 統合。
  </Card>
  <Card title="OpenAI provider" href="/ja-JP/providers/openai" icon="robot">
    OpenAI/Codex サブスクリプション向け。
  </Card>
  <Card title="Model providers" href="/ja-JP/concepts/model-providers" icon="layers">
    すべての provider、モデル参照、フェイルオーバー動作の概要。
  </Card>
  <Card title="Configuration" href="/ja-JP/gateway/configuration" icon="gear">
    完全な設定リファレンス。
  </Card>
</CardGroup>
