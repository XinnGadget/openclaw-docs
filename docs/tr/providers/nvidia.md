---
read_when:
    - OpenClaw içinde açık modelleri ücretsiz kullanmak istiyorsunuz
    - NVIDIA_API_KEY kurulumuna ihtiyacınız var
summary: OpenClaw içinde NVIDIA'nın OpenAI uyumlu API'sini kullanın
title: NVIDIA
x-i18n:
    generated_at: "2026-04-08T02:17:35Z"
    model: gpt-5.4
    provider: openai
    source_hash: b00f8cedaf223a33ba9f6a6dd8cf066d88cebeea52d391b871e435026182228a
    source_path: providers/nvidia.md
    workflow: 15
---

# NVIDIA

NVIDIA, açık modeller için `https://integrate.api.nvidia.com/v1` adresinde ücretsiz bir OpenAI uyumlu API sağlar. [build.nvidia.com](https://build.nvidia.com/settings/api-keys) üzerinden alınan bir API anahtarı ile kimlik doğrulaması yapın.

## CLI kurulumu

Anahtarı bir kez dışa aktarın, ardından onboarding çalıştırın ve bir NVIDIA modeli ayarlayın:

```bash
export NVIDIA_API_KEY="nvapi-..."
openclaw onboard --auth-choice skip
openclaw models set nvidia/nvidia/nemotron-3-super-120b-a12b
```

Hâlâ `--token` geçiriyorsanız bunun shell geçmişine ve `ps` çıktısına düştüğünü unutmayın; mümkün olduğunda ortam değişkenini tercih edin.

## Yapılandırma parçacığı

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

## Model kimlikleri

| Model ref                                  | Ad                           | Bağlam  | En fazla çıktı |
| ------------------------------------------ | ---------------------------- | ------- | -------------- |
| `nvidia/nvidia/nemotron-3-super-120b-a12b` | NVIDIA Nemotron 3 Super 120B | 262,144 | 8,192          |
| `nvidia/moonshotai/kimi-k2.5`              | Kimi K2.5                    | 262,144 | 8,192          |
| `nvidia/minimaxai/minimax-m2.5`            | Minimax M2.5                 | 196,608 | 8,192          |
| `nvidia/z-ai/glm5`                         | GLM 5                        | 202,752 | 8,192          |

## Notlar

- OpenAI uyumlu `/v1` uç noktası; [build.nvidia.com](https://build.nvidia.com/) üzerinden bir API anahtarı kullanın.
- `NVIDIA_API_KEY` ayarlandığında sağlayıcı otomatik olarak etkinleşir.
- Paketlenmiş katalog statiktir; maliyetler kaynakta varsayılan olarak `0` olur.
