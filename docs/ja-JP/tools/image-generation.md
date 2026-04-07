---
read_when:
    - エージェント経由で画像を生成する場合
    - 画像生成プロバイダーとモデルを設定する場合
    - image_generateツールのパラメーターを理解する場合
summary: 設定済みプロバイダー（OpenAI、Google Gemini、fal、MiniMax、ComfyUI、Vydra）を使って画像を生成・編集する
title: 画像生成
x-i18n:
    generated_at: "2026-04-07T04:47:25Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8f7303c199d46e63e88f5f9567478a1025631afb03cb35f44344c12370365e57
    source_path: tools/image-generation.md
    workflow: 15
---

# 画像生成

`image_generate` ツールを使うと、エージェントは設定済みのプロバイダーを使って画像を作成・編集できます。生成された画像は、エージェントの返信内でメディア添付として自動的に配信されます。

<Note>
このツールは、少なくとも1つの画像生成プロバイダーが利用可能な場合にのみ表示されます。エージェントのツールに `image_generate` が表示されない場合は、`agents.defaults.imageGenerationModel` を設定するか、プロバイダーのAPIキーを設定してください。
</Note>

## クイックスタート

1. 少なくとも1つのプロバイダーにAPIキーを設定します（例: `OPENAI_API_KEY` または `GEMINI_API_KEY`）。
2. 必要に応じて、優先するモデルを設定します:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "openai/gpt-image-1",
      },
    },
  },
}
```

3. エージェントに依頼します: _「Generate an image of a friendly lobster mascot.」_

エージェントは自動的に `image_generate` を呼び出します。ツールの許可リスト設定は不要です。プロバイダーが利用可能な場合、デフォルトで有効になります。

## サポートされるプロバイダー

| Provider | Default model                    | Edit support                       | API key                                               |
| -------- | -------------------------------- | ---------------------------------- | ----------------------------------------------------- |
| OpenAI   | `gpt-image-1`                    | Yes (up to 5 images)               | `OPENAI_API_KEY`                                      |
| Google   | `gemini-3.1-flash-image-preview` | Yes                                | `GEMINI_API_KEY` or `GOOGLE_API_KEY`                  |
| fal      | `fal-ai/flux/dev`                | Yes                                | `FAL_KEY`                                             |
| MiniMax  | `image-01`                       | Yes (subject reference)            | `MINIMAX_API_KEY` or MiniMax OAuth (`minimax-portal`) |
| ComfyUI  | `workflow`                       | Yes (1 image, workflow-configured) | `COMFY_API_KEY` or `COMFY_CLOUD_API_KEY` for cloud    |
| Vydra    | `grok-imagine`                   | No                                 | `VYDRA_API_KEY`                                       |

実行時に利用可能なプロバイダーとモデルを確認するには、`action: "list"` を使用してください:

```
/tool image_generate action=list
```

## ツールパラメーター

| Parameter     | Type     | Description                                                                           |
| ------------- | -------- | ------------------------------------------------------------------------------------- |
| `prompt`      | string   | 画像生成プロンプト（`action: "generate"` の場合は必須）                               |
| `action`      | string   | `"generate"`（デフォルト）または、プロバイダーを確認するための `"list"`               |
| `model`       | string   | `openai/gpt-image-1` のような provider/model 上書き                                   |
| `image`       | string   | 編集モード用の単一参照画像パスまたはURL                                               |
| `images`      | string[] | 編集モード用の複数参照画像（最大5枚）                                                 |
| `size`        | string   | サイズヒント: `1024x1024`, `1536x1024`, `1024x1536`, `1024x1792`, `1792x1024`         |
| `aspectRatio` | string   | アスペクト比: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` |
| `resolution`  | string   | 解像度ヒント: `1K`, `2K`, または `4K`                                                 |
| `count`       | number   | 生成する画像数（1〜4）                                                                |
| `filename`    | string   | 出力ファイル名のヒント                                                                |

すべてのプロバイダーがすべてのパラメーターをサポートしているわけではありません。フォールバックプロバイダーが、正確に要求されたものではなく近いジオメトリオプションをサポートしている場合、OpenClawは送信前に最も近いサポート済みのサイズ、アスペクト比、または解像度へ再マッピングします。本当にサポートされていない上書きは、引き続きツール結果で報告されます。

ツール結果には、適用された設定が報告されます。OpenClawがプロバイダーフォールバック中にジオメトリを再マッピングした場合、返される `size`、`aspectRatio`、`resolution` の値には実際に送信された内容が反映され、`details.normalization` には要求値から適用値への変換が記録されます。

## 設定

### モデル選択

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "openai/gpt-image-1",
        fallbacks: ["google/gemini-3.1-flash-image-preview", "fal/fal-ai/flux/dev"],
      },
    },
  },
}
```

### プロバイダー選択順

画像を生成するとき、OpenClawは次の順序でプロバイダーを試します:

1. ツール呼び出し内の **`model` パラメーター**（エージェントが指定した場合）
2. 設定内の **`imageGenerationModel.primary`**
3. **`imageGenerationModel.fallbacks`** を順に
4. **自動検出** — 認証済みのプロバイダーデフォルトのみを使用:
   - 現在のデフォルトプロバイダーを最初に
   - 残りの登録済み画像生成プロバイダーを provider-id 順に

プロバイダーが失敗した場合（認証エラー、レート制限など）、次の候補が自動的に試されます。すべて失敗した場合、エラーには各試行の詳細が含まれます。

注記:

- 自動検出は認証を認識します。OpenClawがそのプロバイダーを実際に認証できる場合にのみ、プロバイダーデフォルトが候補リストに入ります。
- 自動検出はデフォルトで有効です。画像生成で明示的な `model`、`primary`、`fallbacks`
  エントリのみを使いたい場合は、`agents.defaults.mediaGenerationAutoProviderFallback: false` を設定してください。
- `action: "list"` を使うと、現在登録されているプロバイダー、その
  デフォルトモデル、認証用環境変数ヒントを確認できます。

### 画像編集

OpenAI、Google、fal、MiniMax、ComfyUIは、参照画像の編集をサポートしています。参照画像のパスまたはURLを渡してください:

```
"Generate a watercolor version of this photo" + image: "/path/to/photo.jpg"
```

OpenAIとGoogleは、`images` パラメーターにより最大5枚の参照画像をサポートします。fal、MiniMax、ComfyUIは1枚をサポートします。

MiniMax画像生成は、バンドル済みのMiniMax認証パスの両方から利用できます:

- APIキー構成用の `minimax/image-01`
- OAuth構成用の `minimax-portal/image-01`

## プロバイダー機能

| Capability            | OpenAI               | Google               | fal                 | MiniMax                    | ComfyUI                            | Vydra   |
| --------------------- | -------------------- | -------------------- | ------------------- | -------------------------- | ---------------------------------- | ------- |
| 生成                  | Yes (up to 4)        | Yes (up to 4)        | Yes (up to 4)       | Yes (up to 9)              | Yes (workflow-defined outputs)     | Yes (1) |
| 編集/参照             | Yes (up to 5 images) | Yes (up to 5 images) | Yes (1 image)       | Yes (1 image, subject ref) | Yes (1 image, workflow-configured) | No      |
| サイズ制御            | Yes                  | Yes                  | Yes                 | No                         | No                                 | No      |
| アスペクト比          | No                   | Yes                  | Yes (generate only) | Yes                        | No                                 | No      |
| 解像度（1K/2K/4K）    | No                   | Yes                  | Yes                 | No                         | No                                 | No      |

## 関連

- [Tools Overview](/ja-JP/tools) — 利用可能なすべてのエージェントツール
- [fal](/ja-JP/providers/fal) — fal画像/動画プロバイダーのセットアップ
- [ComfyUI](/ja-JP/providers/comfy) — ローカルComfyUIおよびComfy Cloudワークフローのセットアップ
- [Google (Gemini)](/ja-JP/providers/google) — Gemini画像プロバイダーのセットアップ
- [MiniMax](/ja-JP/providers/minimax) — MiniMax画像プロバイダーのセットアップ
- [OpenAI](/ja-JP/providers/openai) — OpenAI Imagesプロバイダーのセットアップ
- [Vydra](/ja-JP/providers/vydra) — Vydra画像、動画、speechのセットアップ
- [Configuration Reference](/ja-JP/gateway/configuration-reference#agent-defaults) — `imageGenerationModel` 設定
- [Models](/ja-JP/concepts/models) — モデル設定とフェイルオーバー
