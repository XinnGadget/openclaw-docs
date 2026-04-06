---
read_when:
    - モデルプロバイダーを選びたい
    - サポートされているLLMバックエンドの概要をすばやく確認したい
summary: OpenClawがサポートするモデルプロバイダー（LLM）
title: プロバイダーディレクトリ
x-i18n:
    generated_at: "2026-04-06T03:11:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7271157a6ab5418672baff62bfd299572fd010f75aad529267095c6e55903882
    source_path: providers/index.md
    workflow: 15
---

# モデルプロバイダー

OpenClawは多くのLLMプロバイダーを利用できます。プロバイダーを選び、認証し、デフォルトモデルを`provider/model`として設定してください。

チャットチャネルのドキュメント（WhatsApp/Telegram/Discord/Slack/Mattermost (plugin)など）を探していますか? [Channels](/ja-JP/channels)を参照してください。

## クイックスタート

1. プロバイダーで認証します（通常は`openclaw onboard`を使用）。
2. デフォルトモデルを設定します:

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## プロバイダードキュメント

- [Alibaba Model Studio](/providers/alibaba)
- [Amazon Bedrock](/ja-JP/providers/bedrock)
- [Anthropic (API + Claude CLI)](/ja-JP/providers/anthropic)
- [BytePlus (International)](/ja-JP/concepts/model-providers#byteplus-international)
- [Chutes](/ja-JP/providers/chutes)
- [ComfyUI](/providers/comfy)
- [Cloudflare AI Gateway](/ja-JP/providers/cloudflare-ai-gateway)
- [DeepSeek](/ja-JP/providers/deepseek)
- [fal](/providers/fal)
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
- [Runway](/providers/runway)
- [SGLang (local models)](/ja-JP/providers/sglang)
- [StepFun](/ja-JP/providers/stepfun)
- [Synthetic](/ja-JP/providers/synthetic)
- [Together AI](/ja-JP/providers/together)
- [Venice (Venice AI, privacy-focused)](/ja-JP/providers/venice)
- [Vercel AI Gateway](/ja-JP/providers/vercel-ai-gateway)
- [Vydra](/providers/vydra)
- [vLLM (local models)](/ja-JP/providers/vllm)
- [Volcengine (Doubao)](/ja-JP/providers/volcengine)
- [xAI](/ja-JP/providers/xai)
- [Xiaomi](/ja-JP/providers/xiaomi)
- [Z.AI](/ja-JP/providers/zai)

## 共有の概要ページ

- [Additional bundled variants](/ja-JP/providers/models#additional-bundled-provider-variants) - Anthropic Vertex、Copilot Proxy、Gemini CLI OAuth
- [Image Generation](/ja-JP/tools/image-generation) - 共有`image_generate`ツール、プロバイダー選択、およびフェイルオーバー
- [Music Generation](/tools/music-generation) - 共有`music_generate`ツール、プロバイダー選択、およびフェイルオーバー
- [Video Generation](/tools/video-generation) - 共有`video_generate`ツール、プロバイダー選択、およびフェイルオーバー

## 文字起こしプロバイダー

- [Deepgram (audio transcription)](/ja-JP/providers/deepgram)

## コミュニティツール

- [Claude Max API Proxy](/ja-JP/providers/claude-max-api-proxy) - Claudeサブスクリプション認証情報向けのコミュニティプロキシ（使用前にAnthropicのポリシー/利用規約を確認してください）

完全なプロバイダーカタログ（xAI、Groq、Mistralなど）と高度な設定については、
[Model providers](/ja-JP/concepts/model-providers)を参照してください。
