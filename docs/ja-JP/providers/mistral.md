---
read_when:
    - OpenClaw で Mistral モデルを使用したい場合
    - Mistral API キーのオンボーディングと model ref が必要な場合
summary: OpenClaw で Mistral モデルと Voxtral 文字起こしを使用する
title: Mistral
x-i18n:
    generated_at: "2026-04-12T23:32:06Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0474f55587909ce9bbdd47b881262edbeb1b07eb3ed52de1090a8ec4d260c97b
    source_path: providers/mistral.md
    workflow: 15
---

# Mistral

OpenClaw は、テキスト/画像モデルのルーティング（`mistral/...`）と、
media understanding における Voxtral による音声文字起こしの両方で Mistral をサポートしています。
Mistral は memory embedding（`memorySearch.provider = "mistral"`）にも使用できます。

- Provider: `mistral`
- Auth: `MISTRAL_API_KEY`
- API: Mistral Chat Completions（`https://api.mistral.ai/v1`）

## はじめに

<Steps>
  <Step title="Get your API key">
    [Mistral Console](https://console.mistral.ai/) で API キーを作成します。
  </Step>
  <Step title="Run onboarding">
    ```bash
    openclaw onboard --auth-choice mistral-api-key
    ```

    または、キーを直接渡します:

    ```bash
    openclaw onboard --mistral-api-key "$MISTRAL_API_KEY"
    ```

  </Step>
  <Step title="Set a default model">
    ```json5
    {
      env: { MISTRAL_API_KEY: "sk-..." },
      agents: { defaults: { model: { primary: "mistral/mistral-large-latest" } } },
    }
    ```
  </Step>
  <Step title="Verify the model is available">
    ```bash
    openclaw models list --provider mistral
    ```
  </Step>
</Steps>

## 組み込み LLM カタログ

OpenClaw には現在、このバンドルされた Mistral カタログが含まれています:

| Model ref                        | Input       | Context | Max output | Notes                                                            |
| -------------------------------- | ----------- | ------- | ---------- | ---------------------------------------------------------------- |
| `mistral/mistral-large-latest`   | text, image | 262,144 | 16,384     | デフォルトモデル                                                 |
| `mistral/mistral-medium-2508`    | text, image | 262,144 | 8,192      | Mistral Medium 3.1                                               |
| `mistral/mistral-small-latest`   | text, image | 128,000 | 16,384     | Mistral Small 4; API の `reasoning_effort` による調整可能な reasoning |
| `mistral/pixtral-large-latest`   | text, image | 128,000 | 32,768     | Pixtral                                                          |
| `mistral/codestral-latest`       | text        | 256,000 | 4,096      | コーディング                                                     |
| `mistral/devstral-medium-latest` | text        | 262,144 | 32,768     | Devstral 2                                                       |
| `mistral/magistral-small`        | text        | 128,000 | 40,000     | reasoning 有効                                                   |

## 音声文字起こし（Voxtral）

media understanding パイプラインを通じて、音声文字起こしに Voxtral を使用します。

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        models: [{ provider: "mistral", model: "voxtral-mini-latest" }],
      },
    },
  },
}
```

<Tip>
media 文字起こしパスでは `/v1/audio/transcriptions` を使用します。Mistral のデフォルト音声モデルは `voxtral-mini-latest` です。
</Tip>

## 詳細設定

<AccordionGroup>
  <Accordion title="Adjustable reasoning (mistral-small-latest)">
    `mistral/mistral-small-latest` は Mistral Small 4 に対応し、Chat Completions API で `reasoning_effort` を通じた [adjustable reasoning](https://docs.mistral.ai/capabilities/reasoning/adjustable) をサポートします（`none` は出力内の追加 thinking を最小化し、`high` は最終回答の前に完全な thinking trace を表示します）。

    OpenClaw は、セッションの **thinking** レベルを Mistral の API に次のようにマッピングします:

    | OpenClaw thinking level                          | Mistral `reasoning_effort` |
    | ------------------------------------------------ | -------------------------- |
    | **off** / **minimal**                            | `none`                     |
    | **low** / **medium** / **high** / **xhigh** / **adaptive** | `high`             |

    <Note>
    他のバンドル済み Mistral カタログモデルでは、このパラメーターは使用されません。Mistral ネイティブの reasoning-first 動作が必要な場合は、引き続き `magistral-*` モデルを使用してください。
    </Note>

  </Accordion>

  <Accordion title="Memory embeddings">
    Mistral は `/v1/embeddings` を通じて memory embedding を提供できます（デフォルトモデル: `mistral-embed`）。

    ```json5
    {
      memorySearch: { provider: "mistral" },
    }
    ```

  </Accordion>

  <Accordion title="Auth and base URL">
    - Mistral の認証では `MISTRAL_API_KEY` を使用します。
    - provider の base URL のデフォルトは `https://api.mistral.ai/v1` です。
    - オンボーディングのデフォルトモデルは `mistral/mistral-large-latest` です。
    - Z.AI は API キーによる Bearer 認証を使用します。
  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="Model selection" href="/ja-JP/concepts/model-providers" icon="layers">
    provider、model ref、フェイルオーバー動作の選び方。
  </Card>
  <Card title="Media understanding" href="/tools/media-understanding" icon="microphone">
    音声文字起こしのセットアップと provider 選択。
  </Card>
</CardGroup>
