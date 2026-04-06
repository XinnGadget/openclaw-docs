---
read_when:
    - OpenClawでGrokモデルを使いたい
    - xAIの認証またはモデルidを設定している
summary: OpenClawでxAI Grokモデルを使う
title: xAI
x-i18n:
    generated_at: "2026-04-06T03:12:28Z"
    model: gpt-5.4
    provider: openai
    source_hash: 64bc899655427cc10bdc759171c7d1ec25ad9f1e4f9d803f1553d3d586c6d71d
    source_path: providers/xai.md
    workflow: 15
---

# xAI

OpenClawには、Grokモデル用のバンドルされた`xai`プロバイダープラグインが含まれています。

## セットアップ

1. xAIコンソールでAPIキーを作成します。
2. `XAI_API_KEY`を設定するか、次を実行します:

```bash
openclaw onboard --auth-choice xai-api-key
```

3. 次のようなモデルを選択します:

```json5
{
  agents: { defaults: { model: { primary: "xai/grok-4" } } },
}
```

OpenClawは現在、バンドルされたxAIトランスポートとしてxAI Responses APIを使用します。同じ
`XAI_API_KEY`は、Grokベースの`web_search`、ファーストクラスの`x_search`、およびリモートの`code_execution`にも使用できます。
`plugins.entries.xai.config.webSearch.apiKey`配下にxAIキーを保存した場合、バンドルされたxAIモデルプロバイダーはそのキーもフォールバックとして再利用します。
`code_execution`の調整項目は`plugins.entries.xai.config.codeExecution`配下にあります。

## 現在のバンドルモデルカタログ

OpenClawには現在、これらのxAIモデルファミリーが標準で含まれています。

- `grok-3`, `grok-3-fast`, `grok-3-mini`, `grok-3-mini-fast`
- `grok-4`, `grok-4-0709`
- `grok-4-fast`, `grok-4-fast-non-reasoning`
- `grok-4-1-fast`, `grok-4-1-fast-non-reasoning`
- `grok-4.20-beta-latest-reasoning`, `grok-4.20-beta-latest-non-reasoning`
- `grok-code-fast-1`

このプラグインは、同じAPI形状に従う新しい`grok-4*`および`grok-code-fast*` idも前方解決します。

高速モデルに関するメモ:

- `grok-4-fast`、`grok-4-1-fast`、および`grok-4.20-beta-*`バリアントは、現在バンドルカタログ内で画像対応のGrok参照です。
- `/fast on`または`agents.defaults.models["xai/<model>"].params.fastMode: true`
  は、ネイティブxAIリクエストを次のように書き換えます:
  - `grok-3` -> `grok-3-fast`
  - `grok-3-mini` -> `grok-3-mini-fast`
  - `grok-4` -> `grok-4-fast`
  - `grok-4-0709` -> `grok-4-fast`

レガシー互換エイリアスは引き続き正式なバンドルidへ正規化されます。たとえば:

- `grok-4-fast-reasoning` -> `grok-4-fast`
- `grok-4-1-fast-reasoning` -> `grok-4-1-fast`
- `grok-4.20-reasoning` -> `grok-4.20-beta-latest-reasoning`
- `grok-4.20-non-reasoning` -> `grok-4.20-beta-latest-non-reasoning`

## Web検索

バンドルされた`grok` Web検索プロバイダーも`XAI_API_KEY`を使います:

```bash
openclaw config set tools.web.search.provider grok
```

## 動画生成

バンドルされた`xai`プラグインは、共有の`video_generate`ツールを通じた動画生成も登録します。

- デフォルト動画モデル: `xai/grok-imagine-video`
- モード: テキストから動画、画像から動画、およびリモート動画の編集/延長フロー
- `aspectRatio`と`resolution`をサポート
- 現在の制限: ローカル動画バッファーは受け付けられません。動画参照/編集入力にはリモートの`http(s)` URLを使用してください

xAIをデフォルトの動画プロバイダーとして使うには:

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

共有ツールのパラメーター、プロバイダー選択、およびフェイルオーバー動作については、[Video Generation](/tools/video-generation)を参照してください。

## 既知の制限

- 認証は現在APIキーのみです。OpenClawにはまだxAIのOAuth/device-codeフローはありません。
- `grok-4.20-multi-agent-experimental-beta-0304`は、標準のOpenClaw xAIトランスポートとは異なる上流APIサーフェスを必要とするため、通常のxAIプロバイダー経路ではサポートされていません。

## メモ

- OpenClawは、共有ランナー経路上でxAI固有のツールスキーマおよびツール呼び出し互換修正を自動的に適用します。
- ネイティブxAIリクエストでは、デフォルトで`tool_stream: true`になります。無効にするには、
  `agents.defaults.models["xai/<model>"].params.tool_stream`を`false`に設定してください。
- バンドルされたxAIラッパーは、ネイティブxAIリクエスト送信前に、未対応の厳格なツールスキーマフラグとreasoningペイロードキーを削除します。
- `web_search`、`x_search`、および`code_execution`はOpenClawツールとして公開されています。OpenClawは、各ツールリクエスト内で必要な特定のxAI組み込み機能だけを有効化し、すべてのネイティブツールをすべてのチャットターンに付与することはありません。
- `x_search`と`code_execution`は、コアモデルランタイムにハードコードされているのではなく、バンドルされたxAIプラグインが所有しています。
- `code_execution`はリモートのxAIサンドボックス実行であり、ローカルの[`exec`](/ja-JP/tools/exec)ではありません。
- より広いプロバイダー概要については、[Model providers](/ja-JP/providers/index)を参照してください。
