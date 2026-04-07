---
read_when:
    - メディア機能の概要を探しているとき
    - どのメディアproviderを設定するか決めているとき
    - 非同期メディア生成の仕組みを理解したいとき
summary: メディア生成、理解、音声機能の統合ランディングページ
title: Media Overview
x-i18n:
    generated_at: "2026-04-07T04:47:09Z"
    model: gpt-5.4
    provider: openai
    source_hash: cfee08eb91ec3e827724c8fa99bff7465356f6f1ac1b146562f35651798e3fd6
    source_path: tools/media-overview.md
    workflow: 15
---

# メディア生成と理解

OpenClawは画像、動画、音楽を生成し、受信メディア（画像、音声、動画）を理解し、text-to-speechで返信を音声化できます。すべてのメディア機能はtool駆動です。agentは会話に基づいてそれらをいつ使うかを判断し、各toolは対応するproviderが少なくとも1つ設定されている場合にのみ表示されます。

## 機能一覧

| Capability           | Tool             | Providers                                                                                    | What it does                                            |
| -------------------- | ---------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| Image generation     | `image_generate` | ComfyUI, fal, Google, MiniMax, OpenAI, Vydra                                                 | テキストプロンプトまたは参照から画像を作成または編集する |
| Video generation     | `video_generate` | Alibaba, BytePlus, ComfyUI, fal, Google, MiniMax, OpenAI, Qwen, Runway, Together, Vydra, xAI | テキスト、画像、既存の動画から動画を作成する    |
| Music generation     | `music_generate` | ComfyUI, Google, MiniMax                                                                     | テキストプロンプトから音楽または音声トラックを作成する         |
| Text-to-speech (TTS) | `tts`            | ElevenLabs, Microsoft, MiniMax, OpenAI                                                       | 送信返信を音声に変換する               |
| Media understanding  | (automatic)      | Any vision/audio-capable model provider, plus CLI fallbacks                                  | 受信した画像、音声、動画を要約する             |

## Provider機能マトリクス

この表は、プラットフォーム全体で各providerがどのメディア機能をサポートしているかを示します。

| Provider   | Image | Video | Music | TTS | STT / Transcription | Media Understanding |
| ---------- | ----- | ----- | ----- | --- | ------------------- | ------------------- |
| Alibaba    |       | Yes   |       |     |                     |                     |
| BytePlus   |       | Yes   |       |     |                     |                     |
| ComfyUI    | Yes   | Yes   | Yes   |     |                     |                     |
| Deepgram   |       |       |       |     | Yes                 |                     |
| ElevenLabs |       |       |       | Yes |                     |                     |
| fal        | Yes   | Yes   |       |     |                     |                     |
| Google     | Yes   | Yes   | Yes   |     |                     | Yes                 |
| Microsoft  |       |       |       | Yes |                     |                     |
| MiniMax    | Yes   | Yes   | Yes   | Yes |                     |                     |
| OpenAI     | Yes   | Yes   |       | Yes | Yes                 | Yes                 |
| Qwen       |       | Yes   |       |     |                     |                     |
| Runway     |       | Yes   |       |     |                     |                     |
| Together   |       | Yes   |       |     |                     |                     |
| Vydra      | Yes   | Yes   |       |     |                     |                     |
| xAI        |       | Yes   |       |     |                     |                     |

<Note>
メディア理解では、provider configに登録されたvision対応またはaudio対応のmodelを使用します。上の表では、専用のメディア理解サポートを持つproviderを強調しています。multimodal modelsを持つほとんどのLLM provider（Anthropic、Google、OpenAIなど）は、アクティブな返信modelとして設定されていれば、受信メディアも理解できます。
</Note>

## 非同期生成の仕組み

providerの処理には通常30秒から数分かかるため、動画生成と音楽生成はバックグラウンドタスクとして実行されます。agentが `video_generate` または `music_generate` を呼び出すと、OpenClawはproviderへリクエストを送信し、ただちにtask IDを返して、そのジョブをtask ledgerで追跡します。ジョブの実行中もagentは他のメッセージへの応答を続けます。providerの処理が完了すると、OpenClawはagentを再開し、元のチャンネルに完成したメディアを投稿できるようにします。画像生成とTTSは同期的で、返信内でそのまま完了します。

## クイックリンク

- [Image Generation](/ja-JP/tools/image-generation) -- 画像の生成と編集
- [Video Generation](/ja-JP/tools/video-generation) -- text-to-video、image-to-video、video-to-video
- [Music Generation](/ja-JP/tools/music-generation) -- 音楽と音声トラックの作成
- [Text-to-Speech](/ja-JP/tools/tts) -- 返信を音声に変換
- [Media Understanding](/ja-JP/nodes/media-understanding) -- 受信した画像、音声、動画の理解
