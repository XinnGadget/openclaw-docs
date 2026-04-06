---
read_when:
    - OpenClawでQwenを使いたい
    - 以前にQwen OAuthを使っていた
summary: OpenClawのバンドルqwenプロバイダー経由でQwen Cloudを使用する
title: Qwen
x-i18n:
    generated_at: "2026-04-06T03:12:14Z"
    model: gpt-5.4
    provider: openai
    source_hash: f175793693ab6a4c3f1f4d42040e673c15faf7603a500757423e9e06977c989d
    source_path: providers/qwen.md
    workflow: 15
---

# Qwen

<Warning>

**Qwen OAuthは削除されました。** `portal.qwen.ai`エンドポイントを使用していた
無料枠のOAuth統合
（`qwen-portal`）は、現在は利用できません。
背景については
[Issue #49557](https://github.com/openclaw/openclaw/issues/49557)を参照してください。

</Warning>

## 推奨: Qwen Cloud

OpenClawは現在、Qwenを正式なid
`qwen`を持つファーストクラスのバンドルプロバイダーとして扱います。バンドルプロバイダーはQwen Cloud / Alibaba DashScopeおよび
Coding Planエンドポイントを対象とし、レガシーな`modelstudio` idも
互換エイリアスとして引き続き機能します。

- プロバイダー: `qwen`
- 推奨env var: `QWEN_API_KEY`
- 互換性のために受け付けられるもの: `MODELSTUDIO_API_KEY`, `DASHSCOPE_API_KEY`
- APIスタイル: OpenAI互換

`qwen3.6-plus`を使いたい場合は、**Standard（従量課金）**エンドポイントを推奨します。
Coding Planサポートは公開カタログより遅れることがあります。

```bash
# Global Coding Plan endpoint
openclaw onboard --auth-choice qwen-api-key

# China Coding Plan endpoint
openclaw onboard --auth-choice qwen-api-key-cn

# Global Standard (pay-as-you-go) endpoint
openclaw onboard --auth-choice qwen-standard-api-key

# China Standard (pay-as-you-go) endpoint
openclaw onboard --auth-choice qwen-standard-api-key-cn
```

レガシーな`modelstudio-*` auth-choice idおよび`modelstudio/...` model refも
互換エイリアスとして引き続き機能しますが、新しいセットアップフローでは正式な
`qwen-*` auth-choice idと`qwen/...` model refを優先してください。

オンボーディング後、デフォルトモデルを設定します:

```json5
{
  agents: {
    defaults: {
      model: { primary: "qwen/qwen3.5-plus" },
    },
  },
}
```

## プラン種別とエンドポイント

| Plan                       | Region | Auth choice                | Endpoint                                         |
| -------------------------- | ------ | -------------------------- | ------------------------------------------------ |
| Standard (pay-as-you-go)   | China  | `qwen-standard-api-key-cn` | `dashscope.aliyuncs.com/compatible-mode/v1`      |
| Standard (pay-as-you-go)   | Global | `qwen-standard-api-key`    | `dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| Coding Plan (subscription) | China  | `qwen-api-key-cn`          | `coding.dashscope.aliyuncs.com/v1`               |
| Coding Plan (subscription) | Global | `qwen-api-key`             | `coding-intl.dashscope.aliyuncs.com/v1`          |

このプロバイダーは、選択したauth choiceに基づいてエンドポイントを自動選択します。正式な
choiceは`qwen-*`ファミリーを使い、`modelstudio-*`は互換性専用のままです。
configでカスタム`baseUrl`を使って上書きすることもできます。

ネイティブModel Studioエンドポイントは、
共有`openai-completions`トランスポート上でstreaming usage compatibilityを公開します。OpenClawは現在これを
endpoint capabilitiesに基づいて判定するため、同じネイティブホストを対象とするDashScope互換のカスタムprovider idも、
組み込みの`qwen` provider idを特に必要とせず、同じstreaming-usage挙動を継承します。

## APIキーを取得する

- **キー管理**: [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys)
- **ドキュメント**: [docs.qwencloud.com](https://docs.qwencloud.com/developer-guides/getting-started/introduction)

## 組み込みカタログ

OpenClawは現在、このバンドルQwenカタログを同梱しています:

| Model ref                   | Input       | Context   | Notes                                              |
| --------------------------- | ----------- | --------- | -------------------------------------------------- |
| `qwen/qwen3.5-plus`         | text, image | 1,000,000 | デフォルトモデル                                   |
| `qwen/qwen3.6-plus`         | text, image | 1,000,000 | このモデルが必要な場合はStandardエンドポイントを推奨 |
| `qwen/qwen3-max-2026-01-23` | text        | 262,144   | Qwen Max系                                         |
| `qwen/qwen3-coder-next`     | text        | 262,144   | コーディング                                       |
| `qwen/qwen3-coder-plus`     | text        | 1,000,000 | コーディング                                       |
| `qwen/MiniMax-M2.5`         | text        | 1,000,000 | reasoning有効                                      |
| `qwen/glm-5`                | text        | 202,752   | GLM                                                |
| `qwen/glm-4.7`              | text        | 202,752   | GLM                                                |
| `qwen/kimi-k2.5`            | text, image | 262,144   | Alibaba経由のMoonshot AI                           |

モデルがバンドルカタログに
存在していても、利用可否はエンドポイントと課金プランによって変わることがあります。

ネイティブstreaming usage compatibilityは、Coding Planホストと
Standard DashScope互換ホストの両方に適用されます:

- `https://coding.dashscope.aliyuncs.com/v1`
- `https://coding-intl.dashscope.aliyuncs.com/v1`
- `https://dashscope.aliyuncs.com/compatible-mode/v1`
- `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`

## Qwen 3.6 Plusの利用可否

`qwen3.6-plus`は、Standard（従量課金）Model Studio
エンドポイントで利用できます:

- China: `dashscope.aliyuncs.com/compatible-mode/v1`
- Global: `dashscope-intl.aliyuncs.com/compatible-mode/v1`

Coding Planエンドポイントが
`qwen3.6-plus`に対して「unsupported model」エラーを返す場合は、Coding Planの
エンドポイント/キー組ではなく、Standard（従量課金）へ切り替えてください。

## 機能プラン

`qwen`拡張は、コーディング/テキストモデルだけでなく、
完全なQwen
Cloud surface全体のベンダーホームとして位置付けられています。

- テキスト/チャットモデル: 現在バンドル済み
- Tool calling、structured output、thinking: OpenAI互換トランスポートから継承
- 画像生成: provider-pluginレイヤーで対応予定
- 画像/動画理解: Standardエンドポイントで現在バンドル済み
- 音声/音響: provider-pluginレイヤーで対応予定
- メモリembeddings/reranking: embedding adapter surface経由で対応予定
- 動画生成: 共有video-generation capability経由で現在バンドル済み

## マルチモーダル追加機能

`qwen`拡張は現在、以下も公開しています:

- `qwen-vl-max-latest`による動画理解
- Wan動画生成:
  - `wan2.6-t2v`（デフォルト）
  - `wan2.6-i2v`
  - `wan2.6-r2v`
  - `wan2.6-r2v-flash`
  - `wan2.7-r2v`

これらのマルチモーダルsurfaceは、Coding Planエンドポイントではなく
**Standard** DashScopeエンドポイントを使用します。

- Global/Intl Standard base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- China Standard base URL: `https://dashscope.aliyuncs.com/compatible-mode/v1`

動画生成では、OpenClawはジョブ送信前に、設定されたQwenリージョンを対応する
DashScope AIGCホストへマッピングします:

- Global/Intl: `https://dashscope-intl.aliyuncs.com`
- China: `https://dashscope.aliyuncs.com`

つまり、Coding PlanまたはStandard Qwenホストのいずれかを指す通常の
`models.providers.qwen.baseUrl`であっても、動画生成は引き続き正しい
リージョンのDashScope動画エンドポイントを使用します。

動画生成では、デフォルトモデルを明示的に設定してください:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: { primary: "qwen/wan2.6-t2v" },
    },
  },
}
```

現在バンドルされているQwen動画生成の制限:

- リクエストごとに最大 **1** 本の出力動画
- 最大 **1** 枚の入力画像
- 最大 **4** 本の入力動画
- 最大 **10秒** の長さ
- `size`、`aspectRatio`、`resolution`、`audio`、`watermark`をサポート
- 参照画像/動画モードは現在 **リモートhttp(s) URL** が必要です。ローカル
  ファイルパスは事前に拒否されます。これはDashScope動画エンドポイントが、それらの参照に対して
  アップロードされたローカルbufferを受け付けないためです。

共有ツールの
パラメーター、プロバイダー選択、フェイルオーバー挙動については、[動画生成](/tools/video-generation)を参照してください。

## 環境に関する注意

Gatewayがdaemon（launchd/systemd）として動作している場合は、`QWEN_API_KEY`が
そのプロセスから利用可能であることを確認してください（たとえば`~/.openclaw/.env`または
`env.shellEnv`経由）。
