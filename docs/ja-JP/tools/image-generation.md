---
read_when:
    - エージェント経由で画像を生成するとき
    - 画像生成providerとmodelを設定するとき
    - image_generate toolのパラメーターを理解したいとき
summary: 設定済みprovider（OpenAI、Google Gemini、fal、MiniMax、ComfyUI、Vydra）を使って画像を生成・編集する
title: 画像生成
x-i18n:
    generated_at: "2026-04-06T03:13:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: dde416dd1441a06605db85b5813cf61ccfc525813d6db430b7b7dfa53d6a3134
    source_path: tools/image-generation.md
    workflow: 15
---

# 画像生成

`image_generate` toolを使うと、設定済みのproviderを使ってエージェントが画像を生成・編集できます。生成された画像は、エージェントの返信内でメディア添付として自動的に配信されます。

<Note>
このtoolは、少なくとも1つの画像生成providerが利用可能な場合にのみ表示されます。エージェントのtoolsに `image_generate` が表示されない場合は、`agents.defaults.imageGenerationModel` を設定するか、provider APIキーを設定してください。
</Note>

## クイックスタート

1. 少なくとも1つのproviderにAPIキーを設定します（たとえば `OPENAI_API_KEY` または `GEMINI_API_KEY`）。
2. 必要に応じて、優先するmodelを設定します。

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

3. エージェントにこう依頼します: _「親しみやすいロブスターマスコットの画像を生成して。」_

エージェントは自動的に `image_generate` を呼び出します。toolの許可リスト設定は不要です。providerが利用可能ならデフォルトで有効になります。

## サポートされるprovider

| Provider | デフォルトmodel                    | 編集対応                         | APIキー                                               |
| -------- | ---------------------------------- | -------------------------------- | ----------------------------------------------------- |
| OpenAI   | `gpt-image-1`                      | はい（最大5画像）                | `OPENAI_API_KEY`                                      |
| Google   | `gemini-3.1-flash-image-preview`   | はい                             | `GEMINI_API_KEY` または `GOOGLE_API_KEY`              |
| fal      | `fal-ai/flux/dev`                  | はい                             | `FAL_KEY`                                             |
| MiniMax  | `image-01`                         | はい（被写体参照）               | `MINIMAX_API_KEY` または MiniMax OAuth (`minimax-portal`) |
| ComfyUI  | `workflow`                         | はい（1画像、workflow設定依存）  | クラウドでは `COMFY_API_KEY` または `COMFY_CLOUD_API_KEY` |
| Vydra    | `grok-imagine`                     | いいえ                           | `VYDRA_API_KEY`                                       |

実行時に利用可能なproviderとmodelを確認するには、`action: "list"` を使ってください。

```
/tool image_generate action=list
```

## toolパラメーター

| Parameter     | Type     | 説明 |
| ------------- | -------- | ---- |
| `prompt`      | string   | 画像生成プロンプト（`action: "generate"` で必須） |
| `action`      | string   | `"generate"`（デフォルト）またはproviderを確認するための `"list"` |
| `model`       | string   | provider/model の上書き。例: `openai/gpt-image-1` |
| `image`       | string   | 編集モード用の単一参照画像パスまたはURL |
| `images`      | string[] | 編集モード用の複数参照画像（最大5枚） |
| `size`        | string   | サイズヒント: `1024x1024`, `1536x1024`, `1024x1536`, `1024x1792`, `1792x1024` |
| `aspectRatio` | string   | アスペクト比: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` |
| `resolution`  | string   | 解像度ヒント: `1K`, `2K`, または `4K` |
| `count`       | number   | 生成する画像数（1–4） |
| `filename`    | string   | 出力ファイル名ヒント |

すべてのproviderがすべてのパラメーターをサポートしているわけではありません。toolは各providerがサポートするものだけを渡し、それ以外は無視し、除外された上書き内容をtool結果で報告します。

## 設定

### model選択

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

### provider選択順序

画像を生成するとき、OpenClawは次の順序でproviderを試します。

1. tool call 内の **`model` パラメーター**（エージェントが指定した場合）
2. config内の **`imageGenerationModel.primary`**
3. 順番通りの **`imageGenerationModel.fallbacks`**
4. **自動検出** — 認証可能なproviderデフォルトのみを使用:
   - 現在のデフォルトproviderを最初に
   - 残りの登録済み画像生成providerをprovider-id順で

providerが失敗した場合（認証エラー、レート制限など）、次の候補が自動的に試されます。すべて失敗した場合、エラーには各試行の詳細が含まれます。

メモ:

- 自動検出は認証を考慮します。providerデフォルトが候補リストに入るのは、OpenClawが実際にそのproviderで認証できる場合のみです。
- 現在登録されているprovider、デフォルトmodel、および認証用env var のヒントを確認するには、`action: "list"` を使ってください。

### 画像編集

OpenAI、Google、fal、MiniMax、ComfyUI は参照画像の編集をサポートしています。参照画像パスまたはURLを渡してください。

```
「この写真を水彩画風にして」 + image: "/path/to/photo.jpg"
```

OpenAIとGoogleは `images` パラメーターで最大5枚の参照画像をサポートします。fal、MiniMax、ComfyUI は1枚をサポートします。

MiniMax画像生成は、両方のバンドル済みMiniMax認証パスから利用できます。

- APIキーセットアップ用の `minimax/image-01`
- OAuthセットアップ用の `minimax-portal/image-01`

## provider機能

| Capability            | OpenAI            | Google             | fal              | MiniMax                  | ComfyUI                              | Vydra |
| --------------------- | ----------------- | ------------------ | ---------------- | ------------------------ | ------------------------------------ | ----- |
| 生成                  | はい（最大4枚）   | はい（最大4枚）    | はい（最大4枚）  | はい（最大9枚）          | はい（workflow定義の出力）           | はい（1枚） |
| 編集/参照             | はい（最大5画像） | はい（最大5画像）  | はい（1画像）    | はい（1画像、被写体参照） | はい（1画像、workflow設定依存）      | いいえ |
| サイズ制御            | はい              | はい               | はい             | いいえ                   | いいえ                               | いいえ |
| アスペクト比          | いいえ            | はい               | はい（生成のみ） | はい                     | いいえ                               | いいえ |
| 解像度（1K/2K/4K）    | いいえ            | はい               | はい             | いいえ                   | いいえ                               | いいえ |

## 関連

- [Tools Overview](/ja-JP/tools) — 利用可能なすべてのエージェントtool
- [fal](/providers/fal) — fal画像/動画providerセットアップ
- [ComfyUI](/providers/comfy) — ローカルComfyUIおよびComfy Cloud workflowセットアップ
- [Google (Gemini)](/ja-JP/providers/google) — Gemini画像providerセットアップ
- [MiniMax](/ja-JP/providers/minimax) — MiniMax画像providerセットアップ
- [OpenAI](/ja-JP/providers/openai) — OpenAI Images providerセットアップ
- [Vydra](/providers/vydra) — Vydra画像、動画、音声セットアップ
- [Configuration Reference](/ja-JP/gateway/configuration-reference#agent-defaults) — `imageGenerationModel` config
- [Models](/ja-JP/concepts/models) — model設定とフェイルオーバー
