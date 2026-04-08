---
read_when:
    - モデル provider を選びたい場合
    - サポートされている LLM バックエンドの概要をすばやく確認したい場合
summary: OpenClaw がサポートするモデル provider（LLM）
title: Provider Directory
x-i18n:
    generated_at: "2026-04-08T02:18:15Z"
    model: gpt-5.4
    provider: openai
    source_hash: e7bee5528b7fc9a982b3d0eaa4930cb77f7bded19a47aec00572b6fcbd823a70
    source_path: providers/index.md
    workflow: 15
---

# Model Providers

OpenClaw は多くの LLM provider を利用できます。provider を選択して認証し、次に
デフォルトモデルを `provider/model` として設定してください。

チャットチャネルのドキュメント（WhatsApp/Telegram/Discord/Slack/Mattermost（plugin）/など）を探していますか？ [Channels](/ja-JP/channels) を参照してください。

## クイックスタート

1. provider で認証します（通常は `openclaw onboard` を使用します）。
2. デフォルトモデルを設定します:

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## provider ドキュメント

- [Alibaba Model Studio](/ja-JP/providers/alibaba)
- [Amazon Bedrock](/ja-JP/providers/bedrock)
- [Anthropic (API + Claude CLI)](/ja-JP/providers/anthropic)
- [Arcee AI (Trinity モデル)](/ja-JP/providers/arcee)
- [BytePlus (International)](/ja-JP/concepts/model-providers#byteplus-international)
- [Chutes](/ja-JP/providers/chutes)
- [ComfyUI](/ja-JP/providers/comfy)
- [Cloudflare AI Gateway](/ja-JP/providers/cloudflare-ai-gateway)
- [DeepSeek](/ja-JP/providers/deepseek)
- [fal](/ja-JP/providers/fal)
- [Fireworks](/ja-JP/providers/fireworks)
- [GitHub Copilot](/ja-JP/providers/github-copilot)
- [GLM モデル](/ja-JP/providers/glm)
- [Google (Gemini)](/ja-JP/providers/google)
- [Groq (LPU 推論)](/ja-JP/providers/groq)
- [Hugging Face (Inference)](/ja-JP/providers/huggingface)
- [inferrs (ローカルモデル)](/ja-JP/providers/inferrs)
- [Kilocode](/ja-JP/providers/kilocode)
- [LiteLLM (統合 Gateway)](/ja-JP/providers/litellm)
- [MiniMax](/ja-JP/providers/minimax)
- [Mistral](/ja-JP/providers/mistral)
- [Moonshot AI (Kimi + Kimi Coding)](/ja-JP/providers/moonshot)
- [NVIDIA](/ja-JP/providers/nvidia)
- [Ollama (クラウド + ローカルモデル)](/ja-JP/providers/ollama)
- [OpenAI (API + Codex)](/ja-JP/providers/openai)
- [OpenCode](/ja-JP/providers/opencode)
- [OpenCode Go](/ja-JP/providers/opencode-go)
- [OpenRouter](/ja-JP/providers/openrouter)
- [Perplexity (Web 検索)](/ja-JP/providers/perplexity-provider)
- [Qianfan](/ja-JP/providers/qianfan)
- [Qwen Cloud](/ja-JP/providers/qwen)
- [Runway](/ja-JP/providers/runway)
- [SGLang (ローカルモデル)](/ja-JP/providers/sglang)
- [StepFun](/ja-JP/providers/stepfun)
- [Synthetic](/ja-JP/providers/synthetic)
- [Together AI](/ja-JP/providers/together)
- [Venice (Venice AI、プライバシー重視)](/ja-JP/providers/venice)
- [Vercel AI Gateway](/ja-JP/providers/vercel-ai-gateway)
- [Vydra](/ja-JP/providers/vydra)
- [vLLM (ローカルモデル)](/ja-JP/providers/vllm)
- [Volcengine (Doubao)](/ja-JP/providers/volcengine)
- [xAI](/ja-JP/providers/xai)
- [Xiaomi](/ja-JP/providers/xiaomi)
- [Z.AI](/ja-JP/providers/zai)

## 共有概要ページ

- [Additional bundled variants](/ja-JP/providers/models#additional-bundled-provider-variants) - Anthropic Vertex、Copilot Proxy、Gemini CLI OAuth
- [Image Generation](/ja-JP/tools/image-generation) - 共有 `image_generate` tool、provider 選択、フェイルオーバー
- [Music Generation](/ja-JP/tools/music-generation) - 共有 `music_generate` tool、provider 選択、フェイルオーバー
- [Video Generation](/ja-JP/tools/video-generation) - 共有 `video_generate` tool、provider 選択、フェイルオーバー

## 文字起こし provider

- [Deepgram (音声文字起こし)](/ja-JP/providers/deepgram)

## コミュニティツール

- [Claude Max API Proxy](/ja-JP/providers/claude-max-api-proxy) - Claude サブスクリプション認証情報向けのコミュニティプロキシ（使用前に Anthropic のポリシー/利用規約を確認してください）

xAI、Groq、Mistral などを含む完全な provider カタログと高度な設定については、
[Model providers](/ja-JP/concepts/model-providers) を参照してください。
