---
read_when:
    - モデルプロバイダーを選びたい場合
    - LLM認証とモデル選択のクイックセットアップ例が欲しい場合
summary: OpenClawでサポートされるモデルプロバイダー（LLM）
title: モデルプロバイダー クイックスタート
x-i18n:
    generated_at: "2026-04-08T02:18:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: 59ee4c2f993fe0ae05fe34f52bc6f3e0fc9a76b10760f56b20ad251e25ee9f20
    source_path: providers/models.md
    workflow: 15
---

# モデルプロバイダー

OpenClawは多くのLLMプロバイダーを利用できます。1つ選んで認証し、その後
デフォルトモデルを `provider/model` として設定してください。

## クイックスタート（2ステップ）

1. プロバイダーで認証します（通常は `openclaw onboard` を使用します）。
2. デフォルトモデルを設定します:

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## サポートされているプロバイダー（スターターセット）

- [Alibaba Model Studio](/ja-JP/providers/alibaba)
- [Anthropic（API + Claude CLI）](/ja-JP/providers/anthropic)
- [Amazon Bedrock](/ja-JP/providers/bedrock)
- [BytePlus（International）](/ja-JP/concepts/model-providers#byteplus-international)
- [Chutes](/ja-JP/providers/chutes)
- [ComfyUI](/ja-JP/providers/comfy)
- [Cloudflare AI Gateway](/ja-JP/providers/cloudflare-ai-gateway)
- [fal](/ja-JP/providers/fal)
- [Fireworks](/ja-JP/providers/fireworks)
- [GLM models](/ja-JP/providers/glm)
- [MiniMax](/ja-JP/providers/minimax)
- [Mistral](/ja-JP/providers/mistral)
- [Moonshot AI（Kimi + Kimi Coding）](/ja-JP/providers/moonshot)
- [OpenAI（API + Codex）](/ja-JP/providers/openai)
- [OpenCode（Zen + Go）](/ja-JP/providers/opencode)
- [OpenRouter](/ja-JP/providers/openrouter)
- [Qianfan](/ja-JP/providers/qianfan)
- [Qwen](/ja-JP/providers/qwen)
- [Runway](/ja-JP/providers/runway)
- [StepFun](/ja-JP/providers/stepfun)
- [Synthetic](/ja-JP/providers/synthetic)
- [Vercel AI Gateway](/ja-JP/providers/vercel-ai-gateway)
- [Venice（Venice AI）](/ja-JP/providers/venice)
- [xAI](/ja-JP/providers/xai)
- [Z.AI](/ja-JP/providers/zai)

## 追加のバンドルされたプロバイダーバリアント

- `anthropic-vertex` - Vertex認証情報が利用可能な場合の、Google Vertex上の暗黙的なAnthropicサポート。個別のオンボーディング認証選択肢はありません
- `copilot-proxy` - ローカルのVS Code Copilot Proxyブリッジ。`openclaw onboard --auth-choice copilot-proxy` を使用します
- `google-gemini-cli` - 非公式のGemini CLI OAuthフロー。ローカルの `gemini` インストールが必要です（`brew install gemini-cli` または `npm install -g @google/gemini-cli`）。デフォルトモデルは `google-gemini-cli/gemini-3-flash-preview`。`openclaw onboard --auth-choice google-gemini-cli` または `openclaw models auth login --provider google-gemini-cli --set-default` を使用します

完全なプロバイダーカタログ（xAI、Groq、Mistralなど）と高度な設定については、
[Model providers](/ja-JP/concepts/model-providers)を参照してください。
