---
read_when:
    - 音声添付ファイル向けに Deepgram の speech-to-text を使用したい場合
    - 簡単な Deepgram 設定例が必要な場合
summary: 受信音声メモ向けの Deepgram 文字起こし
title: Deepgram
x-i18n:
    generated_at: "2026-04-12T23:30:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 091523d6669e3d258f07c035ec756bd587299b6c7025520659232b1b2c1e21a5
    source_path: providers/deepgram.md
    workflow: 15
---

# Deepgram（音声文字起こし）

Deepgram は speech-to-text API です。OpenClaw では、`tools.media.audio` を通じた**受信 audio/voice note の文字起こし**に使用されます。

有効にすると、OpenClaw は音声ファイルを Deepgram にアップロードし、文字起こし結果を reply pipeline（`{{Transcript}}` + `[Audio]` ブロック）に注入します。これは**ストリーミングではなく**、事前録音文字起こしエンドポイントを使用します。

| Detail        | Value                                                      |
| ------------- | ---------------------------------------------------------- |
| Website       | [deepgram.com](https://deepgram.com)                       |
| Docs          | [developers.deepgram.com](https://developers.deepgram.com) |
| Auth          | `DEEPGRAM_API_KEY`                                         |
| Default model | `nova-3`                                                   |

## はじめに

<Steps>
  <Step title="Set your API key">
    Deepgram API キーを環境変数に追加します:

    ```
    DEEPGRAM_API_KEY=dg_...
    ```

  </Step>
  <Step title="Enable the audio provider">
    ```json5
    {
      tools: {
        media: {
          audio: {
            enabled: true,
            models: [{ provider: "deepgram", model: "nova-3" }],
          },
        },
      },
    }
    ```
  </Step>
  <Step title="Send a voice note">
    接続済みチャネルのいずれかを通じて音声メッセージを送信します。OpenClaw はそれを
    Deepgram で文字起こしし、その transcript を reply pipeline に注入します。
  </Step>
</Steps>

## 設定オプション

| Option            | Path                                                         | Description                                  |
| ----------------- | ------------------------------------------------------------ | -------------------------------------------- |
| `model`           | `tools.media.audio.models[].model`                           | Deepgram model ID（デフォルト: `nova-3`）    |
| `language`        | `tools.media.audio.models[].language`                        | 言語ヒント（任意）                           |
| `detect_language` | `tools.media.audio.providerOptions.deepgram.detect_language` | 言語検出を有効にする（任意）                 |
| `punctuate`       | `tools.media.audio.providerOptions.deepgram.punctuate`       | 句読点を有効にする（任意）                   |
| `smart_format`    | `tools.media.audio.providerOptions.deepgram.smart_format`    | スマートフォーマットを有効にする（任意）     |

<Tabs>
  <Tab title="With language hint">
    ```json5
    {
      tools: {
        media: {
          audio: {
            enabled: true,
            models: [{ provider: "deepgram", model: "nova-3", language: "en" }],
          },
        },
      },
    }
    ```
  </Tab>
  <Tab title="With Deepgram options">
    ```json5
    {
      tools: {
        media: {
          audio: {
            enabled: true,
            providerOptions: {
              deepgram: {
                detect_language: true,
                punctuate: true,
                smart_format: true,
              },
            },
            models: [{ provider: "deepgram", model: "nova-3" }],
          },
        },
      },
    }
    ```
  </Tab>
</Tabs>

## 注意事項

<AccordionGroup>
  <Accordion title="Authentication">
    認証は標準の provider 認証順序に従います。最も簡単な方法は `DEEPGRAM_API_KEY` です。
  </Accordion>
  <Accordion title="Proxy and custom endpoints">
    プロキシを使用する場合は、`tools.media.audio.baseUrl` と
    `tools.media.audio.headers` でエンドポイントまたはヘッダーを上書きできます。
  </Accordion>
  <Accordion title="Output behavior">
    出力は、他の provider と同じ audio ルール（サイズ上限、タイムアウト、
    transcript 注入）に従います。
  </Accordion>
</AccordionGroup>

<Note>
Deepgram の文字起こしは**事前録音のみ**です（リアルタイムストリーミングではありません）。OpenClaw は完全な音声ファイルをアップロードし、全文の transcript を待ってから会話に注入します。
</Note>

## 関連

<CardGroup cols={2}>
  <Card title="Media tools" href="/tools/media" icon="photo-film">
    audio、image、video 処理パイプラインの概要。
  </Card>
  <Card title="Configuration" href="/ja-JP/gateway/configuration" icon="gear">
    media tool 設定を含む完全な設定リファレンス。
  </Card>
  <Card title="Troubleshooting" href="/ja-JP/help/troubleshooting" icon="wrench">
    よくある問題とデバッグ手順。
  </Card>
  <Card title="FAQ" href="/ja-JP/help/faq" icon="circle-question">
    OpenClaw セットアップに関するよくある質問。
  </Card>
</CardGroup>
