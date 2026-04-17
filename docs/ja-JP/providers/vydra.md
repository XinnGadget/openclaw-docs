---
read_when:
    - OpenClawでVydraのメディア生成を使いたい場合
    - Vydra API キーの設定ガイダンスが必要な場合
summary: OpenClawでVydraの画像、動画、音声を使う
title: Vydra
x-i18n:
    generated_at: "2026-04-12T23:34:04Z"
    model: gpt-5.4
    provider: openai
    source_hash: ab623d14b656ce0b68d648a6393fcee3bb880077d6583e0d5c1012e91757f20e
    source_path: providers/vydra.md
    workflow: 15
---

# Vydra

バンドルされた Vydra Plugin は次を追加します:

- `vydra/grok-imagine` による画像生成
- `vydra/veo3` と `vydra/kling` による動画生成
- Vydra の ElevenLabs ベース TTS ルートによる音声合成

OpenClaw は、これら3つのケイパビリティすべてに同じ `VYDRA_API_KEY` を使用します。

<Warning>
base URL には `https://www.vydra.ai/api/v1` を使用してください。

Vydra の apex ホスト（`https://vydra.ai/api/v1`）は現在 `www` にリダイレクトします。一部の HTTP クライアントは、このホスト間リダイレクトで `Authorization` を落としてしまうため、有効な API キーが誤解を招く認証失敗に見えてしまいます。バンドルされた Plugin は、これを避けるために `www` の base URL を直接使用します。
</Warning>

## セットアップ

<Steps>
  <Step title="対話型オンボーディングを実行する">
    ```bash
    openclaw onboard --auth-choice vydra-api-key
    ```

    または、env var を直接設定します:

    ```bash
    export VYDRA_API_KEY="vydra_live_..."
    ```

  </Step>
  <Step title="デフォルトのケイパビリティを選ぶ">
    以下のケイパビリティ（画像、動画、音声）のうち1つ以上を選び、対応する設定を適用します。
  </Step>
</Steps>

## ケイパビリティ

<AccordionGroup>
  <Accordion title="画像生成">
    デフォルトの画像モデル:

    - `vydra/grok-imagine`

    デフォルトの画像プロバイダとして設定します:

    ```json5
    {
      agents: {
        defaults: {
          imageGenerationModel: {
            primary: "vydra/grok-imagine",
          },
        },
      },
    }
    ```

    現在のバンドル対応は text-to-image のみです。Vydra のホスト型 edit ルートはリモート画像 URL を想定しており、OpenClaw はまだバンドルされた Plugin に Vydra 固有のアップロードブリッジを追加していません。

    <Note>
    共有ツールパラメータ、プロバイダ選択、フェイルオーバー動作については [画像生成](/ja-JP/tools/image-generation) を参照してください。
    </Note>

  </Accordion>

  <Accordion title="動画生成">
    登録されている動画モデル:

    - text-to-video 用の `vydra/veo3`
    - image-to-video 用の `vydra/kling`

    Vydra をデフォルトの動画プロバイダとして設定します:

    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "vydra/veo3",
          },
        },
      },
    }
    ```

    注記:

    - `vydra/veo3` はバンドルでは text-to-video のみです。
    - `vydra/kling` は現在、リモート画像 URL 参照を必要とします。ローカルファイルアップロードは事前に拒否されます。
    - Vydra の現在の `kling` HTTP ルートは、`image_url` と `video_url` のどちらを必要とするかが一貫していません。バンドルされたプロバイダは、同じリモート画像 URL を両方のフィールドにマッピングします。
    - バンドルされた Plugin は保守的な方針を取り、アスペクト比、解像度、透かし、生成音声のような未文書化のスタイルノブは転送しません。

    <Note>
    共有ツールパラメータ、プロバイダ選択、フェイルオーバー動作については [動画生成](/ja-JP/tools/video-generation) を参照してください。
    </Note>

  </Accordion>

  <Accordion title="動画ライブテスト">
    プロバイダ固有のライブカバレッジ:

    ```bash
    OPENCLAW_LIVE_TEST=1 \
    OPENCLAW_LIVE_VYDRA_VIDEO=1 \
    pnpm test:live -- extensions/vydra/vydra.live.test.ts
    ```

    バンドルされた Vydra のライブファイルは現在、次をカバーしています:

    - `vydra/veo3` text-to-video
    - リモート画像 URL を使った `vydra/kling` image-to-video

    必要に応じてリモート画像フィクスチャを上書きします:

    ```bash
    export OPENCLAW_LIVE_VYDRA_KLING_IMAGE_URL="https://example.com/reference.png"
    ```

  </Accordion>

  <Accordion title="音声合成">
    Vydra を音声プロバイダとして設定します:

    ```json5
    {
      messages: {
        tts: {
          provider: "vydra",
          providers: {
            vydra: {
              apiKey: "${VYDRA_API_KEY}",
              voiceId: "21m00Tcm4TlvDq8ikWAM",
            },
          },
        },
      },
    }
    ```

    デフォルト:

    - モデル: `elevenlabs/tts`
    - voice id: `21m00Tcm4TlvDq8ikWAM`

    バンドルされた Plugin は現在、既知の正常動作するデフォルト音声を1つ公開しており、MP3 音声ファイルを返します。

  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="プロバイダ一覧" href="/ja-JP/providers/index" icon="list">
    利用可能なすべてのプロバイダを参照します。
  </Card>
  <Card title="画像生成" href="/ja-JP/tools/image-generation" icon="image">
    共有画像ツールパラメータとプロバイダ選択。
  </Card>
  <Card title="動画生成" href="/ja-JP/tools/video-generation" icon="video">
    共有動画ツールパラメータとプロバイダ選択。
  </Card>
  <Card title="設定リファレンス" href="/ja-JP/gateway/configuration-reference#agent-defaults" icon="gear">
    エージェントデフォルトとモデル設定。
  </Card>
</CardGroup>
