---
read_when:
    - OpenClaw でローカルの ComfyUI ワークフローを使いたい
    - 画像、動画、または音楽ワークフローで Comfy Cloud を使いたい
    - バンドルされた comfy Plugin の設定キーが必要です
summary: OpenClaw での ComfyUI ワークフローによる画像、動画、音楽生成のセットアップ
title: ComfyUI
x-i18n:
    generated_at: "2026-04-12T23:30:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 85db395b171f37f80b34b22f3e7707bffc1fd9138e7d10687eef13eaaa55cf24
    source_path: providers/comfy.md
    workflow: 15
---

# ComfyUI

OpenClaw には、ワークフロー駆動の ComfyUI 実行に対応する、バンドルされた `comfy` Plugin が含まれています。この Plugin は完全にワークフロー駆動のため、OpenClaw は汎用的な `size`、`aspectRatio`、`resolution`、`durationSeconds`、または TTS 風の制御をグラフへマッピングしようとはしません。

| Property | Detail |
| --------------- | -------------------------------------------------------------------------------- |
| プロバイダー | `comfy` |
| モデル | `comfy/workflow` |
| 共通サーフェス | `image_generate`, `video_generate`, `music_generate` |
| 認証 | ローカル ComfyUI では不要、Comfy Cloud では `COMFY_API_KEY` または `COMFY_CLOUD_API_KEY` |
| API | ComfyUI `/prompt` / `/history` / `/view` および Comfy Cloud `/api/*` |

## サポート内容

- ワークフロー JSON からの画像生成
- アップロードされた参照画像 1 枚を使った画像編集
- ワークフロー JSON からの動画生成
- アップロードされた参照画像 1 枚を使った動画生成
- 共通の `music_generate` ツールによる音楽または音声生成
- 設定済みノード、または一致するすべての出力ノードからの出力ダウンロード

## はじめに

自分のマシンで ComfyUI を実行するか、Comfy Cloud を使うかを選んでください。

<Tabs>
  <Tab title="ローカル">
    **最適な用途:** 自分のマシンまたは LAN 上で ComfyUI インスタンスを実行する場合。

    <Steps>
      <Step title="ComfyUI をローカルで起動する">
        ローカルの ComfyUI インスタンスが起動していることを確認してください（デフォルトは `http://127.0.0.1:8188`）。
      </Step>
      <Step title="ワークフロー JSON を準備する">
        ComfyUI ワークフロー JSON ファイルをエクスポートするか作成します。プロンプト入力ノードと、OpenClaw が読み取る出力ノードのノード ID を控えてください。
      </Step>
      <Step title="プロバイダーを設定する">
        `mode: "local"` を設定し、ワークフロー ファイルを指定します。以下は最小の画像例です:

        ```json5
        {
          models: {
            providers: {
              comfy: {
                mode: "local",
                baseUrl: "http://127.0.0.1:8188",
                image: {
                  workflowPath: "./workflows/flux-api.json",
                  promptNodeId: "6",
                  outputNodeId: "9",
                },
              },
            },
          },
        }
        ```
      </Step>
      <Step title="デフォルト モデルを設定する">
        設定した機能用に、OpenClaw を `comfy/workflow` モデルへ向けます:

        ```json5
        {
          agents: {
            defaults: {
              imageGenerationModel: {
                primary: "comfy/workflow",
              },
            },
          },
        }
        ```
      </Step>
      <Step title="確認する">
        ```bash
        openclaw models list --provider comfy
        ```
      </Step>
    </Steps>

  </Tab>

  <Tab title="Comfy Cloud">
    **最適な用途:** ローカル GPU リソースを管理せずに Comfy Cloud 上でワークフローを実行する場合。

    <Steps>
      <Step title="API キーを取得する">
        [comfy.org](https://comfy.org) で登録し、アカウント ダッシュボードから API キーを生成します。
      </Step>
      <Step title="API キーを設定する">
        次のいずれかの方法でキーを指定します:

        ```bash
        # 環境変数（推奨）
        export COMFY_API_KEY="your-key"

        # 代替の環境変数
        export COMFY_CLOUD_API_KEY="your-key"

        # または config にインラインで設定
        openclaw config set models.providers.comfy.apiKey "your-key"
        ```
      </Step>
      <Step title="ワークフロー JSON を準備する">
        ComfyUI ワークフロー JSON ファイルをエクスポートするか作成します。プロンプト入力ノードと出力ノードのノード ID を控えてください。
      </Step>
      <Step title="プロバイダーを設定する">
        `mode: "cloud"` を設定し、ワークフロー ファイルを指定します:

        ```json5
        {
          models: {
            providers: {
              comfy: {
                mode: "cloud",
                image: {
                  workflowPath: "./workflows/flux-api.json",
                  promptNodeId: "6",
                  outputNodeId: "9",
                },
              },
            },
          },
        }
        ```

        <Tip>
        cloud モードでは `baseUrl` のデフォルトは `https://cloud.comfy.org` です。カスタムのクラウド エンドポイントを使う場合にのみ `baseUrl` を設定する必要があります。
        </Tip>
      </Step>
      <Step title="デフォルト モデルを設定する">
        ```json5
        {
          agents: {
            defaults: {
              imageGenerationModel: {
                primary: "comfy/workflow",
              },
            },
          },
        }
        ```
      </Step>
      <Step title="確認する">
        ```bash
        openclaw models list --provider comfy
        ```
      </Step>
    </Steps>

  </Tab>
</Tabs>

## 設定

Comfy は、共通のトップレベル接続設定と、機能ごとのワークフロー セクション（`image`、`video`、`music`）をサポートしています:

```json5
{
  models: {
    providers: {
      comfy: {
        mode: "local",
        baseUrl: "http://127.0.0.1:8188",
        image: {
          workflowPath: "./workflows/flux-api.json",
          promptNodeId: "6",
          outputNodeId: "9",
        },
        video: {
          workflowPath: "./workflows/video-api.json",
          promptNodeId: "12",
          outputNodeId: "21",
        },
        music: {
          workflowPath: "./workflows/music-api.json",
          promptNodeId: "3",
          outputNodeId: "18",
        },
      },
    },
  },
}
```

### 共通キー

| Key | Type | Description |
| --------------------- | ---------------------- | ------------------------------------------------------------------------------------- |
| `mode` | `"local"` または `"cloud"` | 接続モード。 |
| `baseUrl` | string | ローカルではデフォルトで `http://127.0.0.1:8188`、cloud では `https://cloud.comfy.org`。 |
| `apiKey` | string | オプションのインライン キー。`COMFY_API_KEY` / `COMFY_CLOUD_API_KEY` 環境変数の代替です。 |
| `allowPrivateNetwork` | boolean | cloud モードでプライベート/LAN の `baseUrl` を許可します。 |

### 機能ごとのキー

これらのキーは `image`、`video`、または `music` セクション内で適用されます:

| Key | Required | Default | Description |
| ---------------------------- | -------- | -------- | ---------------------------------------------------------------------------- |
| `workflow` または `workflowPath` | Yes | -- | ComfyUI ワークフロー JSON ファイルへのパス。 |
| `promptNodeId` | Yes | -- | テキスト プロンプトを受け取るノード ID。 |
| `promptInputName` | No | `"text"` | プロンプト ノード上の入力名。 |
| `outputNodeId` | No | -- | 出力を読み取るノード ID。省略した場合、一致するすべての出力ノードが使われます。 |
| `pollIntervalMs` | No | -- | ジョブ完了を確認するポーリング間隔（ミリ秒）。 |
| `timeoutMs` | No | -- | ワークフロー実行のタイムアウト（ミリ秒）。 |

`image` と `video` セクションでは、次もサポートされます:

| Key | Required | Default | Description |
| --------------------- | ------------------------------------ | --------- | --------------------------------------------------- |
| `inputImageNodeId` | 参照画像を渡す場合は Yes | -- | アップロードされた参照画像を受け取るノード ID。 |
| `inputImageInputName` | No | `"image"` | 画像ノード上の入力名。 |

## ワークフローの詳細

<AccordionGroup>
  <Accordion title="画像ワークフロー">
    デフォルトの画像モデルを `comfy/workflow` に設定します:

    ```json5
    {
      agents: {
        defaults: {
          imageGenerationModel: {
            primary: "comfy/workflow",
          },
        },
      },
    }
    ```

    **参照画像編集の例:**

    アップロードされた参照画像による画像編集を有効にするには、画像設定に `inputImageNodeId` を追加します:

    ```json5
    {
      models: {
        providers: {
          comfy: {
            image: {
              workflowPath: "./workflows/edit-api.json",
              promptNodeId: "6",
              inputImageNodeId: "7",
              inputImageInputName: "image",
              outputNodeId: "9",
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="動画ワークフロー">
    デフォルトの動画モデルを `comfy/workflow` に設定します:

    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "comfy/workflow",
          },
        },
      },
    }
    ```

    Comfy の動画ワークフローは、設定されたグラフを通じて text-to-video と image-to-video をサポートします。

    <Note>
    OpenClaw は入力動画を Comfy ワークフローへ渡しません。入力としてサポートされるのは、テキスト プロンプトと単一の参照画像のみです。
    </Note>

  </Accordion>

  <Accordion title="音楽ワークフロー">
    バンドルされた Plugin は、ワークフローで定義された音声または音楽出力用の音楽生成プロバイダーを登録し、共通の `music_generate` ツールを通じて公開します:

    ```text
    /tool music_generate prompt="Warm ambient synth loop with soft tape texture"
    ```

    `music` 設定セクションを使って、音声ワークフロー JSON と出力ノードを指定します。

  </Accordion>

  <Accordion title="後方互換性">
    既存のトップレベル画像設定（ネストされた `image` セクションなし）も引き続き動作します:

    ```json5
    {
      models: {
        providers: {
          comfy: {
            workflowPath: "./workflows/flux-api.json",
            promptNodeId: "6",
            outputNodeId: "9",
          },
        },
      },
    }
    ```

    OpenClaw は、このレガシー形式を画像ワークフロー設定として扱います。すぐに移行する必要はありませんが、新しいセットアップではネストされた `image` / `video` / `music` セクションを推奨します。

    <Tip>
    画像生成だけを使う場合、レガシーのフラット設定と新しいネストされた `image` セクションは機能的に同等です。
    </Tip>

  </Accordion>

  <Accordion title="ライブ テスト">
    バンドルされた Plugin にはオプトインのライブ カバレッジがあります:

    ```bash
    OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts
    ```

    ライブ テストでは、一致する Comfy ワークフロー セクションが設定されていない限り、個別の画像、動画、または音楽ケースはスキップされます。

  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="画像生成" href="/ja-JP/tools/image-generation" icon="image">
    画像生成ツールの設定と使い方。
  </Card>
  <Card title="動画生成" href="/ja-JP/tools/video-generation" icon="video">
    動画生成ツールの設定と使い方。
  </Card>
  <Card title="音楽生成" href="/ja-JP/tools/music-generation" icon="music">
    音楽および音声生成ツールのセットアップ。
  </Card>
  <Card title="プロバイダー ディレクトリ" href="/ja-JP/providers/index" icon="layers">
    すべてのプロバイダーとモデル ref の概要。
  </Card>
  <Card title="設定リファレンス" href="/ja-JP/gateway/configuration-reference#agent-defaults" icon="gear">
    エージェントのデフォルトを含む完全な設定リファレンス。
  </Card>
</CardGroup>
