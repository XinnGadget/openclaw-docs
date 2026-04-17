---
read_when:
    - OpenClaw で Alibaba Wan の動画生成を使いたい
    - 動画生成のために Model Studio または DashScope の API キー設定が必要です
summary: OpenClaw における Alibaba Model Studio Wan の動画生成
title: Alibaba Model Studio
x-i18n:
    generated_at: "2026-04-12T23:29:24Z"
    model: gpt-5.4
    provider: openai
    source_hash: a6e97d929952cdba7740f5ab3f6d85c18286b05596a4137bf80bbc8b54f32662
    source_path: providers/alibaba.md
    workflow: 15
---

# Alibaba Model Studio

OpenClaw には、Alibaba Model Studio / DashScope 上の Wan モデル向けの、バンドル済み `alibaba` 動画生成 provider が含まれています。

- Provider: `alibaba`
- 推奨 auth: `MODELSTUDIO_API_KEY`
- こちらも利用可能: `DASHSCOPE_API_KEY`, `QWEN_API_KEY`
- API: DashScope / Model Studio 非同期動画生成

## はじめに

<Steps>
  <Step title="API キーを設定する">
    ```bash
    openclaw onboard --auth-choice qwen-standard-api-key
    ```
  </Step>
  <Step title="デフォルトの動画モデルを設定する">
    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "alibaba/wan2.6-t2v",
          },
        },
      },
    }
    ```
  </Step>
  <Step title="provider が利用可能であることを確認する">
    ```bash
    openclaw models list --provider alibaba
    ```
  </Step>
</Steps>

<Note>
利用可能な auth キー（`MODELSTUDIO_API_KEY`、`DASHSCOPE_API_KEY`、`QWEN_API_KEY`）のどれでも動作します。`qwen-standard-api-key` のオンボーディング選択では、共有 DashScope 認証情報が設定されます。
</Note>

## 組み込み Wan モデル

バンドル済み `alibaba` provider は現在、次を登録しています。

| Model ref                  | モード                      |
| -------------------------- | --------------------------- |
| `alibaba/wan2.6-t2v`       | テキストから動画            |
| `alibaba/wan2.6-i2v`       | 画像から動画                |
| `alibaba/wan2.6-r2v`       | 参照から動画                |
| `alibaba/wan2.6-r2v-flash` | 参照から動画（高速）        |
| `alibaba/wan2.7-r2v`       | 参照から動画                |

## 現在の制限

| パラメーター          | 制限                                                      |
| --------------------- | --------------------------------------------------------- |
| 出力動画              | リクエストごとに最大 **1**                                |
| 入力画像              | 最大 **1**                                                |
| 入力動画              | 最大 **4**                                                |
| 長さ                  | 最大 **10 秒**                                            |
| サポートされる制御    | `size`, `aspectRatio`, `resolution`, `audio`, `watermark` |
| 参照画像/動画         | リモート `http(s)` URL のみ                               |

<Warning>
参照画像/動画モードでは、現在 **リモート http(s) URL** が必要です。参照入力としてローカルファイルパスはサポートされていません。
</Warning>

## 高度な設定

<AccordionGroup>
  <Accordion title="Qwen との関係">
    バンドル済み `qwen` provider も、Wan 動画生成に Alibaba ホストの DashScope エンドポイントを使用します。次のように使い分けてください。

    - 標準的な Qwen provider サーフェスを使いたい場合は `qwen/...`
    - vendor が直接所有する Wan 動画サーフェスを使いたい場合は `alibaba/...`

    詳細は [Qwen provider ドキュメント](/ja-JP/providers/qwen) を参照してください。

  </Accordion>

  <Accordion title="auth キーの優先順位">
    OpenClaw は次の順序で auth キーを確認します。

    1. `MODELSTUDIO_API_KEY`（推奨）
    2. `DASHSCOPE_API_KEY`
    3. `QWEN_API_KEY`

    これらのいずれでも `alibaba` provider を認証できます。

  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="動画生成" href="/ja-JP/tools/video-generation" icon="video">
    共通の動画ツールパラメーターと provider 選択。
  </Card>
  <Card title="Qwen" href="/ja-JP/providers/qwen" icon="microchip">
    Qwen provider のセットアップと DashScope 統合。
  </Card>
  <Card title="設定リファレンス" href="/ja-JP/gateway/configuration-reference#agent-defaults" icon="gear">
    エージェントのデフォルト設定とモデル構成。
  </Card>
</CardGroup>
