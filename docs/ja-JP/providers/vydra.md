---
read_when:
    - OpenClawでVydraのメディア生成を使いたい場合
    - Vydra APIキーのセットアップ手順が必要な場合
summary: OpenClawでVydraの画像、動画、音声を使う
title: Vydra
x-i18n:
    generated_at: "2026-04-07T04:45:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: 24006a687ed6f9792e7b2b10927cc7ad71c735462a92ce03d5fa7c2b2ee2fcc2
    source_path: providers/vydra.md
    workflow: 15
---

# Vydra

バンドル済みのVydra pluginは、次を追加します。

- `vydra/grok-imagine`による画像生成
- `vydra/veo3`および`vydra/kling`による動画生成
- VydraのElevenLabsベースTTSルートによる音声合成

OpenClawは、この3つの機能すべてで同じ`VYDRA_API_KEY`を使用します。

## 重要なベースURL

`https://www.vydra.ai/api/v1`を使用してください。

Vydraのapexホスト（`https://vydra.ai/api/v1`）は現在`www`へリダイレクトします。一部のHTTPクライアントは、そのクロスホストリダイレクト時に`Authorization`を落とすため、有効なAPIキーが誤解を招く認証失敗に見えることがあります。バンドル済みpluginは、これを避けるために`www`のベースURLを直接使用します。

## セットアップ

対話型オンボーディング:

```bash
openclaw onboard --auth-choice vydra-api-key
```

または、env varを直接設定します。

```bash
export VYDRA_API_KEY="vydra_live_..."
```

## 画像生成

デフォルトの画像モデル:

- `vydra/grok-imagine`

これをデフォルトの画像プロバイダーとして設定します。

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

現在のバンドル済みサポートはtext-to-imageのみです。Vydraのホスト型編集ルートはリモート画像URLを想定しており、OpenClawはまだバンドル済みpluginにVydra専用のアップロードブリッジを追加していません。

共有ツール動作については、[Image Generation](/ja-JP/tools/image-generation)を参照してください。

## 動画生成

登録済み動画モデル:

- text-to-video用の`vydra/veo3`
- image-to-video用の`vydra/kling`

Vydraをデフォルトの動画プロバイダーとして設定します。

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

注意:

- `vydra/veo3`はバンドル済みではtext-to-video専用です。
- `vydra/kling`は現在、リモート画像URL参照を必要とします。ローカルファイルアップロードは事前に拒否されます。
- Vydraの現在の`kling` HTTPルートは、`image_url`と`video_url`のどちらを要求するかが一貫していません。バンドル済みproviderは、同じリモート画像URLを両方のフィールドへマッピングします。
- バンドル済みpluginは保守的なままで、aspect ratio、resolution、watermark、生成音声のような文書化されていないスタイル指定は転送しません。

プロバイダー固有のライブカバレッジ:

```bash
OPENCLAW_LIVE_TEST=1 \
OPENCLAW_LIVE_VYDRA_VIDEO=1 \
pnpm test:live -- extensions/vydra/vydra.live.test.ts
```

バンドル済みのVydraライブファイルは現在、次をカバーしています。

- `vydra/veo3` text-to-video
- リモート画像URLを使用した`vydra/kling` image-to-video

必要に応じて、リモート画像フィクスチャをオーバーライドします。

```bash
export OPENCLAW_LIVE_VYDRA_KLING_IMAGE_URL="https://example.com/reference.png"
```

共有ツール動作については、[Video Generation](/ja-JP/tools/video-generation)を参照してください。

## 音声合成

Vydraを音声プロバイダーとして設定します。

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

バンドル済みpluginは現在、動作確認済みのデフォルト音声を1つ公開しており、MP3音声ファイルを返します。

## 関連

- [Provider Directory](/ja-JP/providers/index)
- [Image Generation](/ja-JP/tools/image-generation)
- [Video Generation](/ja-JP/tools/video-generation)
