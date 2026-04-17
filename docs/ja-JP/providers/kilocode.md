---
read_when:
    - 多くの LLM に対して 1 つの API キーを使いたい
    - OpenClaw で Kilo Gateway 経由でモデルを実行したい
summary: Kilo Gateway の統合 API を使って OpenClaw で多くのモデルにアクセスする
title: Kilocode
x-i18n:
    generated_at: "2026-04-12T23:31:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 32946f2187f3933115341cbe81006718b10583abc4deea7440b5e56366025f4a
    source_path: providers/kilocode.md
    workflow: 15
---

# Kilo Gateway

Kilo Gateway は、単一の
エンドポイントと API キーの背後で、多数のモデルにリクエストをルーティングする**統合 API**を提供します。OpenAI 互換なので、ほとんどの OpenAI SDK は base URL を切り替えるだけで動作します。

| Property | Value |
| -------- | ----- |
| プロバイダー | `kilocode` |
| 認証 | `KILOCODE_API_KEY` |
| API | OpenAI 互換 |
| ベース URL | `https://api.kilo.ai/api/gateway/` |

## はじめに

<Steps>
  <Step title="アカウントを作成する">
    [app.kilo.ai](https://app.kilo.ai) にアクセスし、サインインまたはアカウントを作成してから、API Keys に移動して新しいキーを生成します。
  </Step>
  <Step title="オンボーディングを実行する">
    ```bash
    openclaw onboard --auth-choice kilocode-api-key
    ```

    または、環境変数を直接設定します:

    ```bash
    export KILOCODE_API_KEY="<your-kilocode-api-key>" # pragma: allowlist secret
    ```

  </Step>
  <Step title="モデルが利用可能であることを確認する">
    ```bash
    openclaw models list --provider kilocode
    ```
  </Step>
</Steps>

## デフォルト モデル

デフォルト モデルは `kilocode/kilo/auto` です。これは Kilo Gateway によって管理される、プロバイダー所有のスマート ルーティング
モデルです。

<Note>
OpenClaw は `kilocode/kilo/auto` を安定したデフォルト ref として扱いますが、そのルートについて、タスクから上流モデルへのソースに裏付けられたマッピングは公開しません。`kilocode/kilo/auto` の背後にある正確な上流ルーティングは OpenClaw にハードコードされておらず、Kilo Gateway が管理します。
</Note>

## 利用可能なモデル

OpenClaw は起動時に Kilo Gateway から利用可能なモデルを動的に検出します。アカウントで利用可能なモデルの全一覧を見るには
`/models kilocode` を使用してください。

Gateway で利用可能な任意のモデルは、`kilocode/` プレフィックス付きで使用できます:

| Model ref | Notes |
| --------- | ----- |
| `kilocode/kilo/auto` | デフォルト — スマート ルーティング |
| `kilocode/anthropic/claude-sonnet-4` | Kilo 経由の Anthropic |
| `kilocode/openai/gpt-5.4` | Kilo 経由の OpenAI |
| `kilocode/google/gemini-3-pro-preview` | Kilo 経由の Google |
| ...and many more | すべて一覧表示するには `/models kilocode` を使用 |

<Tip>
起動時に、OpenClaw は `GET https://api.kilo.ai/api/gateway/models` を問い合わせ、検出したモデルを静的フォールバック カタログより前にマージします。バンドルされたフォールバックには常に `kilocode/kilo/auto`（`Kilo Auto`）が含まれ、`input: ["text", "image"]`、`reasoning: true`、`contextWindow: 1000000`、`maxTokens: 128000` が設定されています。
</Tip>

## 設定例

```json5
{
  env: { KILOCODE_API_KEY: "<your-kilocode-api-key>" }, // pragma: allowlist secret
  agents: {
    defaults: {
      model: { primary: "kilocode/kilo/auto" },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="トランスポートと互換性">
    Kilo Gateway はソース内で OpenRouter 互換として文書化されているため、
    ネイティブ OpenAI のリクエスト整形ではなく、プロキシ スタイルの OpenAI 互換パスに留まります。

    - Gemini ベースの Kilo ref はプロキシ Gemini パスに留まるため、OpenClaw は
      そこで Gemini の thought-signature サニタイズを維持しつつ、ネイティブ Gemini の
      リプレイ検証やブートストラップ リライトは有効にしません。
    - Kilo Gateway は内部的に、API キー付きの Bearer トークンを使用します。

  </Accordion>

  <Accordion title="ストリーム ラッパーと reasoning">
    Kilo の共有ストリーム ラッパーは、プロバイダー アプリ ヘッダーを追加し、
    サポートされる具体的な model ref に対してプロキシ reasoning ペイロードを正規化します。

    <Warning>
    `kilocode/kilo/auto` や、その他のプロキシ reasoning 非対応ヒントでは reasoning
    注入をスキップします。reasoning サポートが必要な場合は、
    `kilocode/anthropic/claude-sonnet-4` のような具体的な model ref を使用してください。
    </Warning>

  </Accordion>

  <Accordion title="トラブルシューティング">
    - 起動時にモデル検出が失敗した場合、OpenClaw は `kilocode/kilo/auto` を含むバンドル済み静的カタログにフォールバックします。
    - API キーが有効であり、Kilo アカウントで目的のモデルが有効になっていることを確認してください。
    - Gateway がデーモンとして実行される場合は、`KILOCODE_API_KEY` がそのプロセスで利用可能であることを確認してください（たとえば `~/.openclaw/.env` または `env.shellEnv` 経由）。
  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="モデル選択" href="/ja-JP/concepts/model-providers" icon="layers">
    プロバイダー、モデル ref、フェイルオーバー動作の選び方。
  </Card>
  <Card title="設定リファレンス" href="/ja-JP/gateway/configuration" icon="gear">
    OpenClaw の完全な設定リファレンス。
  </Card>
  <Card title="Kilo Gateway" href="https://app.kilo.ai" icon="arrow-up-right-from-square">
    Kilo Gateway のダッシュボード、API キー、アカウント管理。
  </Card>
</CardGroup>
