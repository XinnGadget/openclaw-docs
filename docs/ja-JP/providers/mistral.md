---
read_when:
    - OpenClaw で Mistral モデルを使いたい場合
    - Mistral API キーのオンボーディングとモデル参照が必要な場合
summary: OpenClaw で Mistral モデルと Voxtral 文字起こしを使う
title: Mistral
x-i18n:
    generated_at: "2026-04-08T02:18:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4e32a0eb2a37dba6383ba338b06a8d0be600e7443aa916225794ccb0fdf46aee
    source_path: providers/mistral.md
    workflow: 15
---

# Mistral

OpenClaw は、テキスト/画像モデルルーティング（`mistral/...`）と
media understanding における Voxtral による音声文字起こしの両方で Mistral をサポートしています。
Mistral はメモリ埋め込みにも使用できます（`memorySearch.provider = "mistral"`）。

## CLI セットアップ

```bash
openclaw onboard --auth-choice mistral-api-key
# または非対話モード
openclaw onboard --mistral-api-key "$MISTRAL_API_KEY"
```

## config スニペット（LLM provider）

```json5
{
  env: { MISTRAL_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "mistral/mistral-large-latest" } } },
}
```

## 組み込み LLM カタログ

OpenClaw には現在、このバンドル版 Mistral カタログが含まれています:

| Model ref                        | Input       | Context | Max output | Notes                                                            |
| -------------------------------- | ----------- | ------- | ---------- | ---------------------------------------------------------------- |
| `mistral/mistral-large-latest`   | text, image | 262,144 | 16,384     | デフォルトモデル                                                 |
| `mistral/mistral-medium-2508`    | text, image | 262,144 | 8,192      | Mistral Medium 3.1                                               |
| `mistral/mistral-small-latest`   | text, image | 128,000 | 16,384     | Mistral Small 4; API `reasoning_effort` による調整可能な推論     |
| `mistral/pixtral-large-latest`   | text, image | 128,000 | 32,768     | Pixtral                                                          |
| `mistral/codestral-latest`       | text        | 256,000 | 4,096      | コーディング                                                     |
| `mistral/devstral-medium-latest` | text        | 262,144 | 32,768     | Devstral 2                                                       |
| `mistral/magistral-small`        | text        | 128,000 | 40,000     | 推論対応                                                         |

## config スニペット（Voxtral による音声文字起こし）

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

## 調整可能な推論（`mistral-small-latest`）

`mistral/mistral-small-latest` は Mistral Small 4 に対応しており、Chat Completions API で `reasoning_effort` を通じた[調整可能な推論](https://docs.mistral.ai/capabilities/reasoning/adjustable)をサポートしています（`none` は出力内の追加思考を最小化し、`high` は最終回答の前に完全な思考トレースを表示します）。

OpenClaw はセッションの **thinking** レベルを Mistral の API に次のように対応付けます:

- **off** / **minimal** → `none`
- **low** / **medium** / **high** / **xhigh** / **adaptive** → `high`

他のバンドル版 Mistral カタログモデルではこのパラメーターは使用されません。Mistral ネイティブの推論優先動作が必要な場合は、引き続き `magistral-*` モデルを使用してください。

## 注意

- Mistral 認証には `MISTRAL_API_KEY` を使用します。
- provider ベース URL のデフォルトは `https://api.mistral.ai/v1` です。
- オンボーディング時のデフォルトモデルは `mistral/mistral-large-latest` です。
- Mistral の media-understanding におけるデフォルト音声モデルは `voxtral-mini-latest` です。
- media 文字起こしパスは `/v1/audio/transcriptions` を使用します。
- メモリ埋め込みパスは `/v1/embeddings` を使用します（デフォルトモデル: `mistral-embed`）。
