---
read_when:
    - モデルproviderを選びたいとき
    - LLM認証 + モデル選択のクイックセットアップ例が欲しいとき
summary: OpenClawがサポートするモデルprovider（LLM）
title: モデルproviderクイックスタート
x-i18n:
    generated_at: "2026-04-06T03:11:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: c0314fb1c754171e5fc252d30f7ba9bb6acdbb978d97e9249264d90351bac2e7
    source_path: providers/models.md
    workflow: 15
---

# モデルprovider

OpenClawは多くのLLM providerを利用できます。1つ選び、認証し、デフォルト
model を `provider/model` として設定してください。

## クイックスタート（2ステップ）

1. providerで認証します（通常は `openclaw onboard` を使用）。
2. デフォルトmodelを設定します。

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## サポートされるprovider（スターターセット）

- [Alibaba Model Studio](/providers/alibaba)
- [Anthropic (API + Claude CLI)](/ja-JP/providers/anthropic)
- [Amazon Bedrock](/ja-JP/providers/bedrock)
- [BytePlus (International)](/ja-JP/concepts/model-providers#byteplus-international)
- [Chutes](/ja-JP/providers/chutes)
- [ComfyUI](/providers/comfy)
- [Cloudflare AI Gateway](/ja-JP/providers/cloudflare-ai-gateway)
- [fal](/providers/fal)
- [Fireworks](/ja-JP/providers/fireworks)
- [GLM models](/ja-JP/providers/glm)
- [MiniMax](/ja-JP/providers/minimax)
- [Mistral](/ja-JP/providers/mistral)
- [Moonshot AI (Kimi + Kimi Coding)](/ja-JP/providers/moonshot)
- [OpenAI (API + Codex)](/ja-JP/providers/openai)
- [OpenCode (Zen + Go)](/ja-JP/providers/opencode)
- [OpenRouter](/ja-JP/providers/openrouter)
- [Qianfan](/ja-JP/providers/qianfan)
- [Qwen](/ja-JP/providers/qwen)
- [Runway](/providers/runway)
- [StepFun](/ja-JP/providers/stepfun)
- [Synthetic](/ja-JP/providers/synthetic)
- [Vercel AI Gateway](/ja-JP/providers/vercel-ai-gateway)
- [Venice (Venice AI)](/ja-JP/providers/venice)
- [xAI](/ja-JP/providers/xai)
- [Z.AI](/ja-JP/providers/zai)

## 追加のバンドルproviderバリアント

- `anthropic-vertex` - Vertex資格情報が利用可能な場合の暗黙的なGoogle Vertex上のAnthropicサポート。個別のオンボーディング認証選択は不要
- `copilot-proxy` - ローカルVS Code Copilot Proxyブリッジ。`openclaw onboard --auth-choice copilot-proxy` を使用

完全なproviderカタログ（xAI、Groq、Mistral など）と高度な設定については、
[Model providers](/ja-JP/concepts/model-providers) を参照してください。
