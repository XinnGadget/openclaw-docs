---
read_when:
    - OpenClaw で Grok model を使いたい場合
    - xAI の認証または model id を設定しています
summary: OpenClaw で xAI Grok model を使う
title: xAI
x-i18n:
    generated_at: "2026-04-12T23:34:06Z"
    model: gpt-5.4
    provider: openai
    source_hash: 820fef290c67d9815e41a96909d567216f67ca0f01df1d325008fd04666ad255
    source_path: providers/xai.md
    workflow: 15
---

# xAI

OpenClaw には、Grok model 用のバンドル済み `xai` provider Plugin が含まれています。

## はじめに

<Steps>
  <Step title="API key を作成">
    [xAI console](https://console.x.ai/) で API key を作成します。
  </Step>
  <Step title="API key を設定">
    `XAI_API_KEY` を設定するか、次を実行します。

    ```bash
    openclaw onboard --auth-choice xai-api-key
    ```

  </Step>
  <Step title="model を選ぶ">
    ```json5
    {
      agents: { defaults: { model: { primary: "xai/grok-4" } } },
    }
    ```
  </Step>
</Steps>

<Note>
OpenClaw は、バンドル済み xAI トランスポートとして xAI Responses API を使用します。同じ
`XAI_API_KEY` は、Grok ベースの `web_search`、ファーストクラスの `x_search`、
およびリモート `code_execution` にも利用できます。
`plugins.entries.xai.config.webSearch.apiKey` に xAI キーを保存すると、
バンドル済み xAI model provider もそれをフォールバックとして再利用します。
`code_execution` の調整は `plugins.entries.xai.config.codeExecution` 配下にあります。
</Note>

## バンドル済み model catalog

OpenClaw には、次の xAI model ファミリーが標準で含まれています。

| Family         | Model ids                                                                |
| -------------- | ------------------------------------------------------------------------ |
| Grok 3         | `grok-3`, `grok-3-fast`, `grok-3-mini`, `grok-3-mini-fast`               |
| Grok 4         | `grok-4`, `grok-4-0709`                                                  |
| Grok 4 Fast    | `grok-4-fast`, `grok-4-fast-non-reasoning`                               |
| Grok 4.1 Fast  | `grok-4-1-fast`, `grok-4-1-fast-non-reasoning`                           |
| Grok 4.20 Beta | `grok-4.20-beta-latest-reasoning`, `grok-4.20-beta-latest-non-reasoning` |
| Grok Code      | `grok-code-fast-1`                                                       |

この Plugin は、同じ API 形状に従う新しい `grok-4*` および `grok-code-fast*` id も
フォワード解決します。

<Tip>
`grok-4-fast`、`grok-4-1-fast`、および `grok-4.20-beta-*` バリアントは、
現在バンドル済み catalog で image 対応の Grok 参照です。
</Tip>

### 高速モードのマッピング

`/fast on` または `agents.defaults.models["xai/<model>"].params.fastMode: true`
は、ネイティブ xAI リクエストを次のように書き換えます。

| Source model  | 高速モードの対象     |
| ------------- | ------------------ |
| `grok-3`      | `grok-3-fast`      |
| `grok-3-mini` | `grok-3-mini-fast` |
| `grok-4`      | `grok-4-fast`      |
| `grok-4-0709` | `grok-4-fast`      |

### レガシー互換エイリアス

レガシーエイリアスは引き続き正規のバンドル済み id に正規化されます。

| Legacy alias              | 正規 id                               |
| ------------------------- | ------------------------------------- |
| `grok-4-fast-reasoning`   | `grok-4-fast`                         |
| `grok-4-1-fast-reasoning` | `grok-4-1-fast`                       |
| `grok-4.20-reasoning`     | `grok-4.20-beta-latest-reasoning`     |
| `grok-4.20-non-reasoning` | `grok-4.20-beta-latest-non-reasoning` |

## 機能

<AccordionGroup>
  <Accordion title="Web 検索">
    バンドル済みの `grok` Web 検索 provider も `XAI_API_KEY` を使用します。

    ```bash
    openclaw config set tools.web.search.provider grok
    ```

  </Accordion>

  <Accordion title="動画生成">
    バンドル済みの `xai` Plugin は、共有
    `video_generate` ツールを通じて動画生成を登録します。

    - デフォルトの動画 model: `xai/grok-imagine-video`
    - モード: text-to-video、image-to-video、およびリモート動画の編集/延長フロー
    - `aspectRatio` と `resolution` をサポート

    <Warning>
    ローカル動画バッファは受け付けられません。
    動画参照および編集入力にはリモート `http(s)` URL を使用してください。
    </Warning>

    xAI をデフォルトの動画 provider として使うには:

    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "xai/grok-imagine-video",
          },
        },
      },
    }
    ```

    <Note>
    共有ツールパラメータ、
    provider 選択、およびフェイルオーバーの挙動については、[Video Generation](/ja-JP/tools/video-generation) を参照してください。
    </Note>

  </Accordion>

  <Accordion title="x_search 設定">
    バンドル済み xAI Plugin は、Grok 経由で
    X（旧 Twitter）コンテンツを検索するための OpenClaw ツールとして `x_search` を公開します。

    設定パス: `plugins.entries.xai.config.xSearch`

    | Key                | Type    | Default            | 説明                                |
    | ------------------ | ------- | ------------------ | ----------------------------------- |
    | `enabled`          | boolean | —                  | x_search を有効化または無効化       |
    | `model`            | string  | `grok-4-1-fast`    | x_search リクエストで使う model     |
    | `inlineCitations`  | boolean | —                  | 結果にインライン引用を含める        |
    | `maxTurns`         | number  | —                  | 最大会話ターン数                    |
    | `timeoutSeconds`   | number  | —                  | リクエストタイムアウト（秒）        |
    | `cacheTtlMinutes`  | number  | —                  | キャッシュの time-to-live（分）     |

    ```json5
    {
      plugins: {
        entries: {
          xai: {
            config: {
              xSearch: {
                enabled: true,
                model: "grok-4-1-fast",
                inlineCitations: true,
              },
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Code execution 設定">
    バンドル済み xAI Plugin は、xAI のサンドボックス環境で
    リモートコード実行を行う OpenClaw ツールとして `code_execution` を公開します。

    設定パス: `plugins.entries.xai.config.codeExecution`

    | Key               | Type    | Default            | 説明                                      |
    | ----------------- | ------- | ------------------ | ----------------------------------------- |
    | `enabled`         | boolean | `true`（キーが利用可能な場合） | code execution を有効化または無効化 |
    | `model`           | string  | `grok-4-1-fast`    | code execution リクエストで使う model |
    | `maxTurns`        | number  | —                  | 最大会話ターン数                           |
    | `timeoutSeconds`  | number  | —                  | リクエストタイムアウト（秒）               |

    <Note>
    これはリモート xAI サンドボックス実行であり、ローカルの [`exec`](/ja-JP/tools/exec) ではありません。
    </Note>

    ```json5
    {
      plugins: {
        entries: {
          xai: {
            config: {
              codeExecution: {
                enabled: true,
                model: "grok-4-1-fast",
              },
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="既知の制限">
    - 現時点で認証は API-key のみです。OpenClaw にはまだ xAI OAuth または device-code フローはありません。
    - `grok-4.20-multi-agent-experimental-beta-0304` は、標準の OpenClaw xAI トランスポートとは異なる上流 API
      サーフェスを必要とするため、通常の xAI provider パスではサポートされません。
  </Accordion>

  <Accordion title="高度な注記">
    - OpenClaw は、共有ランナーパス上で xAI 固有のツールスキーマおよびツールコール互換性修正を
      自動的に適用します。
    - ネイティブ xAI リクエストでは、デフォルトで `tool_stream: true` です。
      無効にするには `agents.defaults.models["xai/<model>"].params.tool_stream` を `false` に設定してください。
    - バンドル済み xAI ラッパーは、ネイティブ xAI リクエスト送信前に、
      未対応の strict ツールスキーマフラグと reasoning ペイロードキーを取り除きます。
    - `web_search`、`x_search`、`code_execution` は OpenClaw
      ツールとして公開されます。OpenClaw は、各ツール
      リクエスト内で必要な特定の xAI 組み込み機能だけを有効にし、すべてのネイティブツールを毎回の chat ターンに付与することはしません。
    - `x_search` と `code_execution` は、core model ランタイムに
      ハードコードされているのではなく、バンドル済み xAI Plugin が所有しています。
    - `code_execution` はリモート xAI サンドボックス実行であり、ローカルの
      [`exec`](/ja-JP/tools/exec) ではありません。
  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="model 選択" href="/ja-JP/concepts/model-providers" icon="layers">
    provider、model 参照、およびフェイルオーバーの挙動を選択します。
  </Card>
  <Card title="動画生成" href="/ja-JP/tools/video-generation" icon="video">
    共有動画ツールパラメータと provider 選択。
  </Card>
  <Card title="すべての provider" href="/ja-JP/providers/index" icon="grid-2">
    より広い provider 概要。
  </Card>
  <Card title="トラブルシューティング" href="/ja-JP/help/troubleshooting" icon="wrench">
    よくある問題と修正方法。
  </Card>
</CardGroup>
