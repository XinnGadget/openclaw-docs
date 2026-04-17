---
read_when:
    - OpenClaw で fal の画像生成を使いたい
    - '`FAL_KEY` の auth フローが必要です'
    - '`image_generate` または `video_generate` の fal デフォルト設定が欲しい'
summary: OpenClaw における fal の画像生成と動画生成のセットアップ
title: fal
x-i18n:
    generated_at: "2026-04-12T23:31:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: ff275233179b4808d625383efe04189ad9e92af09944ba39f1e953e77378e347
    source_path: providers/fal.md
    workflow: 15
---

# fal

OpenClaw には、ホスト型の画像生成および動画生成向けの、バンドル済み `fal` provider が含まれています。

| プロパティ | 値                                                            |
| -------- | ------------------------------------------------------------- |
| Provider | `fal`                                                         |
| Auth     | `FAL_KEY`（正式; `FAL_API_KEY` もフォールバックとして動作）   |
| API      | fal model endpoints                                           |

## はじめに

<Steps>
  <Step title="API キーを設定する">
    ```bash
    openclaw onboard --auth-choice fal-api-key
    ```
  </Step>
  <Step title="デフォルトの画像モデルを設定する">
    ```json5
    {
      agents: {
        defaults: {
          imageGenerationModel: {
            primary: "fal/fal-ai/flux/dev",
          },
        },
      },
    }
    ```
  </Step>
</Steps>

## 画像生成

バンドル済み `fal` 画像生成 provider のデフォルトは
`fal/fal-ai/flux/dev` です。

| 機能             | 値                         |
| -------------- | -------------------------- |
| 最大画像数      | リクエストごとに 4         |
| 編集モード      | 有効、参照画像 1 枚        |
| サイズ上書き    | サポートあり               |
| アスペクト比    | サポートあり               |
| 解像度          | サポートあり               |

<Warning>
fal の画像編集エンドポイントは `aspectRatio` の上書きを**サポートしていません**。
</Warning>

fal をデフォルトの画像 provider として使うには、次のようにします。

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "fal/fal-ai/flux/dev",
      },
    },
  },
}
```

## 動画生成

バンドル済み `fal` 動画生成 provider のデフォルトは
`fal/fal-ai/minimax/video-01-live` です。

| 機能       | 値                                                           |
| ---------- | ------------------------------------------------------------ |
| モード     | テキストから動画、単一画像参照                               |
| 実行方式   | 長時間実行ジョブ向けのキュー対応 submit/status/result フロー |

<AccordionGroup>
  <Accordion title="利用可能な動画モデル">
    **HeyGen video-agent:**

    - `fal/fal-ai/heygen/v2/video-agent`

    **Seedance 2.0:**

    - `fal/bytedance/seedance-2.0/fast/text-to-video`
    - `fal/bytedance/seedance-2.0/fast/image-to-video`
    - `fal/bytedance/seedance-2.0/text-to-video`
    - `fal/bytedance/seedance-2.0/image-to-video`

  </Accordion>

  <Accordion title="Seedance 2.0 の設定例">
    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "fal/bytedance/seedance-2.0/fast/text-to-video",
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="HeyGen video-agent の設定例">
    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "fal/fal-ai/heygen/v2/video-agent",
          },
        },
      },
    }
    ```
  </Accordion>
</AccordionGroup>

<Tip>
利用可能な fal モデルの完全な一覧（最近追加されたエントリーを含む）を確認するには、`openclaw models list --provider fal` を使用してください。
</Tip>

## 関連

<CardGroup cols={2}>
  <Card title="画像生成" href="/ja-JP/tools/image-generation" icon="image">
    共通の画像ツールパラメーターと provider 選択。
  </Card>
  <Card title="動画生成" href="/ja-JP/tools/video-generation" icon="video">
    共通の動画ツールパラメーターと provider 選択。
  </Card>
  <Card title="設定リファレンス" href="/ja-JP/gateway/configuration-reference#agent-defaults" icon="gear">
    画像および動画モデル選択を含むエージェントのデフォルト設定。
  </Card>
</CardGroup>
