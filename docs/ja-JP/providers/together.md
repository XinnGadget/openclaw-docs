---
read_when:
    - OpenClawでTogether AIを使いたい
    - APIキー環境変数またはCLI認証選択肢が必要である
summary: Together AIの設定（認証 + モデル選択）
title: Together AI
x-i18n:
    generated_at: "2026-04-06T03:12:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: b68fdc15bfcac8d59e3e0c06a39162abd48d9d41a9a64a0ac622cd8e3f80a595
    source_path: providers/together.md
    workflow: 15
---

# Together AI

[Together AI](https://together.ai)は、統一APIを通じてLlama、DeepSeek、Kimiなどの主要なオープンソースモデルへのアクセスを提供します。

- プロバイダー: `together`
- 認証: `TOGETHER_API_KEY`
- API: OpenAI互換
- ベースURL: `https://api.together.xyz/v1`

## クイックスタート

1. APIキーを設定します（推奨: Gateway用に保存します）:

```bash
openclaw onboard --auth-choice together-api-key
```

2. デフォルトモデルを設定します:

```json5
{
  agents: {
    defaults: {
      model: { primary: "together/moonshotai/Kimi-K2.5" },
    },
  },
}
```

## 非対話型の例

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice together-api-key \
  --together-api-key "$TOGETHER_API_KEY"
```

これにより、`together/moonshotai/Kimi-K2.5`がデフォルトモデルとして設定されます。

## 環境に関する注意

Gatewayがデーモン（launchd/systemd）として動作する場合は、`TOGETHER_API_KEY`がそのプロセスから利用可能であることを確認してください（たとえば`~/.openclaw/.env`または`env.shellEnv`経由）。

## 組み込みカタログ

OpenClawには現在、次のTogetherカタログがバンドルされています。

| Model ref                                                    | Name                                   | Input       | Context    | Notes                            |
| ------------------------------------------------------------ | -------------------------------------- | ----------- | ---------- | -------------------------------- |
| `together/moonshotai/Kimi-K2.5`                              | Kimi K2.5                              | text, image | 262,144    | デフォルトモデル; reasoning有効 |
| `together/zai-org/GLM-4.7`                                   | GLM 4.7 Fp8                            | text        | 202,752    | 汎用テキストモデル               |
| `together/meta-llama/Llama-3.3-70B-Instruct-Turbo`           | Llama 3.3 70B Instruct Turbo           | text        | 131,072    | 高速な指示モデル                 |
| `together/meta-llama/Llama-4-Scout-17B-16E-Instruct`         | Llama 4 Scout 17B 16E Instruct         | text, image | 10,000,000 | マルチモーダル                   |
| `together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | Llama 4 Maverick 17B 128E Instruct FP8 | text, image | 20,000,000 | マルチモーダル                   |
| `together/deepseek-ai/DeepSeek-V3.1`                         | DeepSeek V3.1                          | text        | 131,072    | 汎用テキストモデル               |
| `together/deepseek-ai/DeepSeek-R1`                           | DeepSeek R1                            | text        | 131,072    | reasoningモデル                  |
| `together/moonshotai/Kimi-K2-Instruct-0905`                  | Kimi K2-Instruct 0905                  | text        | 262,144    | セカンダリKimiテキストモデル     |

オンボーディングのプリセットでは、`together/moonshotai/Kimi-K2.5`がデフォルトモデルとして設定されます。

## 動画生成

バンドルされた`together`プラグインは、共有の`video_generate`ツールを通じた動画生成も登録します。

- デフォルト動画モデル: `together/Wan-AI/Wan2.2-T2V-A14B`
- モード: テキストから動画、および単一画像参照フロー
- `aspectRatio`と`resolution`をサポート

Togetherをデフォルトの動画プロバイダーとして使うには:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "together/Wan-AI/Wan2.2-T2V-A14B",
      },
    },
  },
}
```

共有ツールのパラメーター、プロバイダー選択、およびフェイルオーバー動作については、[Video Generation](/tools/video-generation)を参照してください。
