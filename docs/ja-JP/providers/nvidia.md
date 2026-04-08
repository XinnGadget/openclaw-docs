---
read_when:
    - OpenClaw でオープンモデルを無料で使いたい場合
    - NVIDIA_API_KEY のセットアップが必要な場合
summary: OpenClaw で NVIDIA の OpenAI 互換 API を使う
title: NVIDIA
x-i18n:
    generated_at: "2026-04-08T02:18:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: b00f8cedaf223a33ba9f6a6dd8cf066d88cebeea52d391b871e435026182228a
    source_path: providers/nvidia.md
    workflow: 15
---

# NVIDIA

NVIDIA は、オープンモデル向けに `https://integrate.api.nvidia.com/v1` で OpenAI 互換 API を無料提供しています。[build.nvidia.com](https://build.nvidia.com/settings/api-keys) で取得した API キーで認証してください。

## CLI セットアップ

キーを一度 export してから、オンボーディングを実行し、NVIDIA モデルを設定します:

```bash
export NVIDIA_API_KEY="nvapi-..."
openclaw onboard --auth-choice skip
openclaw models set nvidia/nvidia/nemotron-3-super-120b-a12b
```

それでも `--token` を渡す場合は、それがシェル履歴や `ps` 出力に残ることに注意してください。可能であれば env var を使うことを推奨します。

## config スニペット

```json5
{
  env: { NVIDIA_API_KEY: "nvapi-..." },
  models: {
    providers: {
      nvidia: {
        baseUrl: "https://integrate.api.nvidia.com/v1",
        api: "openai-completions",
      },
    },
  },
  agents: {
    defaults: {
      model: { primary: "nvidia/nvidia/nemotron-3-super-120b-a12b" },
    },
  },
}
```

## モデル ID

| Model ref                                  | Name                         | Context | Max output |
| ------------------------------------------ | ---------------------------- | ------- | ---------- |
| `nvidia/nvidia/nemotron-3-super-120b-a12b` | NVIDIA Nemotron 3 Super 120B | 262,144 | 8,192      |
| `nvidia/moonshotai/kimi-k2.5`              | Kimi K2.5                    | 262,144 | 8,192      |
| `nvidia/minimaxai/minimax-m2.5`            | Minimax M2.5                 | 196,608 | 8,192      |
| `nvidia/z-ai/glm5`                         | GLM 5                        | 202,752 | 8,192      |

## 注意

- OpenAI 互換の `/v1` エンドポイントです。[build.nvidia.com](https://build.nvidia.com/) の API キーを使用してください。
- `NVIDIA_API_KEY` が設定されると provider は自動的に有効になります。
- バンドルされたカタログは静的で、コストはソース内でデフォルト `0` です。
