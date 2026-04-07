---
read_when:
    - model providerを選びたいとき
    - サポートされているLLM backendの概要をすばやく確認したいとき
summary: OpenClawがサポートするmodel provider（LLM）
title: Provider Directory
x-i18n:
    generated_at: "2026-04-07T04:45:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: 39d9ace35fd9452a4fb510fd980d251b6e51480e4647f051020bee2f1f2222e1
    source_path: providers/index.md
    workflow: 15
---

# Model Providers

OpenClawは多くのLLM providerを利用できます。providerを選び、認証し、その後
デフォルトmodelを `provider/model` として設定してください。

チャットチャンネルのドキュメント（WhatsApp/Telegram/Discord/Slack/Mattermost (plugin) など）を探していますか？ [Channels](/ja-JP/channels) を参照してください。

## クイックスタート

1. providerで認証します（通常は `openclaw onboard` を使用）。
2. デフォルトmodelを設定します:

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## Providerドキュメント

- [Alibaba Model Studio](/ja-JP/providers/alibaba)
- [Amazon Bedrock](/ja-JP/providers/bedrock)
- [Anthropic (API + Claude CLI)](/ja-JP/providers/anthropic)
- [Arcee AI (Trinity models)](/ja-JP/providers/arcee)
- [BytePlus (International)](/ja-JP/concepts/model-providers#byteplus-international)
- [Chutes](/ja-JP/providers/chutes)
- [ComfyUI](/ja-JP/providers/comfy)
- [Cloudflare AI Gateway](/ja-JP/providers/cloudflare-ai-gateway)
- [DeepSeek](/ja-JP/providers/deepseek)
- [fal](/ja-JP/providers/fal)
- [Fireworks](/ja-JP/providers/fireworks)
- [GitHub Copilot](/ja-JP/providers/github-copilot)
- [GLM models](/ja-JP/providers/glm)
- [Google (Gemini)](/ja-JP/providers/google)
- [Groq (LPU inference)](/ja-JP/providers/groq)
- [Hugging Face (Inference)](/ja-JP/providers/huggingface)
- [Kilocode](/ja-JP/providers/kilocode)
- [LiteLLM (unified gateway)](/ja-JP/providers/litellm)
- [MiniMax](/ja-JP/providers/minimax)
- [Mistral](/ja-JP/providers/mistral)
- [Moonshot AI (Kimi + Kimi Coding)](/ja-JP/providers/moonshot)
- [NVIDIA](/ja-JP/providers/nvidia)
- [Ollama (cloud + local models)](/ja-JP/providers/ollama)
- [OpenAI (API + Codex)](/ja-JP/providers/openai)
- [OpenCode](/ja-JP/providers/opencode)
- [OpenCode Go](/ja-JP/providers/opencode-go)
- [OpenRouter](/ja-JP/providers/openrouter)
- [Perplexity (web search)](/ja-JP/providers/perplexity-provider)
- [Qianfan](/ja-JP/providers/qianfan)
- [Qwen Cloud](/ja-JP/providers/qwen)
- [Runway](/ja-JP/providers/runway)
- [SGLang (local models)](/ja-JP/providers/sglang)
- [StepFun](/ja-JP/providers/stepfun)
- [Synthetic](/ja-JP/providers/synthetic)
- [Together AI](/ja-JP/providers/together)
- [Venice (Venice AI, privacy-focused)](/ja-JP/providers/venice)
- [Vercel AI Gateway](/ja-JP/providers/vercel-ai-gateway)
- [Vydra](/ja-JP/providers/vydra)
- [vLLM (local models)](/ja-JP/providers/vllm)
- [Volcengine (Doubao)](/ja-JP/providers/volcengine)
- [xAI](/ja-JP/providers/xai)
- [Xiaomi](/ja-JP/providers/xiaomi)
- [Z.AI](/ja-JP/providers/zai)

## 共有概要ページ

- [Additional bundled variants](/ja-JP/providers/models#additional-bundled-provider-variants) - Anthropic Vertex、Copilot Proxy、Gemini CLI OAuth
- [Image Generation](/ja-JP/tools/image-generation) - 共有 `image_generate` tool、provider選択、フェイルオーバー
- [Music Generation](/ja-JP/tools/music-generation) - 共有 `music_generate` tool、provider選択、フェイルオーバー
- [Video Generation](/ja-JP/tools/video-generation) - 共有 `video_generate` tool、provider選択、フェイルオーバー

## 文字起こしprovider

- [Deepgram (audio transcription)](/ja-JP/providers/deepgram)

## コミュニティツール

- [Claude Max API Proxy](/ja-JP/providers/claude-max-api-proxy) - Claudeサブスクリプション認証情報向けのコミュニティproxy（使用前にAnthropicのポリシー/利用規約を確認してください）

完全なprovider catalog（xAI、Groq、Mistralなど）と高度な設定については、
[Model providers](/ja-JP/concepts/model-providers) を参照してください。
