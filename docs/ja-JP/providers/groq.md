---
read_when:
    - OpenClaw で Groq を使いたい
    - API キーの環境変数または CLI の認証選択肢が必要です
summary: Groq のセットアップ（認証 + モデル選択）
title: Groq
x-i18n:
    generated_at: "2026-04-12T23:31:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: 613289efc36fedd002e1ebf9366e0e7119ea1f9e14a1dae773b90ea57100baee
    source_path: providers/groq.md
    workflow: 15
---

# Groq

[Groq](https://groq.com) は、カスタム LPU ハードウェアを使用して、オープンソース モデル
（Llama、Gemma、Mistral など）で超高速推論を提供します。OpenClaw は
OpenAI 互換 API を通じて Groq に接続します。

| Property | Value |
| -------- | ----- |
| プロバイダー | `groq` |
| 認証 | `GROQ_API_KEY` |
| API | OpenAI 互換 |

## はじめに

<Steps>
  <Step title="API キーを取得する">
    API キーは [console.groq.com/keys](https://console.groq.com/keys) で作成します。
  </Step>
  <Step title="API キーを設定する">
    ```bash
    export GROQ_API_KEY="gsk_..."
    ```
  </Step>
  <Step title="デフォルト モデルを設定する">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "groq/llama-3.3-70b-versatile" },
        },
      },
    }
    ```
  </Step>
</Steps>

### 設定ファイル例

```json5
{
  env: { GROQ_API_KEY: "gsk_..." },
  agents: {
    defaults: {
      model: { primary: "groq/llama-3.3-70b-versatile" },
    },
  },
}
```

## 利用可能なモデル

Groq のモデル カタログは頻繁に変わります。現在利用可能なモデルを確認するには `openclaw models list | grep groq`
を実行するか、
[console.groq.com/docs/models](https://console.groq.com/docs/models) を確認してください。

| Model | Notes |
| ----- | ----- |
| **Llama 3.3 70B Versatile** | 汎用用途、大きなコンテキスト |
| **Llama 3.1 8B Instant** | 高速、軽量 |
| **Gemma 2 9B** | コンパクトで高効率 |
| **Mixtral 8x7B** | MoE アーキテクチャ、強力な reasoning |

<Tip>
アカウントで利用可能なモデルの最新一覧を確認するには `openclaw models list --provider groq` を使用してください。
</Tip>

## 音声文字起こし

Groq は、高速な Whisper ベースの音声文字起こしも提供します。メディア理解プロバイダーとして設定すると、OpenClaw は共有の `tools.media.audio`
サーフェスを通じて、Groq の `whisper-large-v3-turbo`
モデルを使用して音声メッセージを文字起こしします。

```json5
{
  tools: {
    media: {
      audio: {
        models: [{ provider: "groq" }],
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="音声文字起こしの詳細">
    | Property | Value |
    |----------|-------|
    | 共通設定パス | `tools.media.audio` |
    | デフォルト ベース URL | `https://api.groq.com/openai/v1` |
    | デフォルト モデル | `whisper-large-v3-turbo` |
    | API エンドポイント | OpenAI 互換 `/audio/transcriptions` |
  </Accordion>

  <Accordion title="環境に関する注意">
    Gateway がデーモン（launchd/systemd）として実行される場合は、`GROQ_API_KEY` が
    そのプロセスで利用可能であることを確認してください（たとえば `~/.openclaw/.env` または
    `env.shellEnv` 経由）。

    <Warning>
    対話シェルでのみ設定されたキーは、デーモン管理された
    gateway プロセスからは見えません。永続的に利用できるようにするには、`~/.openclaw/.env` または `env.shellEnv` 設定を使用してください。
    </Warning>

  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="モデル選択" href="/ja-JP/concepts/model-providers" icon="layers">
    プロバイダー、モデル ref、フェイルオーバー動作の選び方。
  </Card>
  <Card title="設定リファレンス" href="/ja-JP/gateway/configuration-reference" icon="gear">
    プロバイダーと音声設定を含む完全な設定スキーマ。
  </Card>
  <Card title="Groq Console" href="https://console.groq.com" icon="arrow-up-right-from-square">
    Groq ダッシュボード、API ドキュメント、価格情報。
  </Card>
  <Card title="Groq モデル一覧" href="https://console.groq.com/docs/models" icon="list">
    公式の Groq モデル カタログ。
  </Card>
</CardGroup>
