---
read_when:
    - OpenClaw ile Together AI kullanmak istiyorsunuz
    - API anahtarı env değişkenine veya CLI kimlik doğrulama seçeneğine ihtiyacınız var
summary: Together AI kurulumu (kimlik doğrulama + model seçimi)
title: Together AI
x-i18n:
    generated_at: "2026-04-06T03:11:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: b68fdc15bfcac8d59e3e0c06a39162abd48d9d41a9a64a0ac622cd8e3f80a595
    source_path: providers/together.md
    workflow: 15
---

# Together AI

[Together AI](https://together.ai), Llama, DeepSeek, Kimi ve daha fazlası dahil önde gelen açık kaynaklı modellere birleşik bir API üzerinden erişim sağlar.

- Sağlayıcı: `together`
- Kimlik doğrulama: `TOGETHER_API_KEY`
- API: OpenAI uyumlu
- Temel URL: `https://api.together.xyz/v1`

## Hızlı başlangıç

1. API anahtarını ayarlayın (önerilen: Gateway için saklayın):

```bash
openclaw onboard --auth-choice together-api-key
```

2. Varsayılan bir model ayarlayın:

```json5
{
  agents: {
    defaults: {
      model: { primary: "together/moonshotai/Kimi-K2.5" },
    },
  },
}
```

## Etkileşimsiz örnek

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice together-api-key \
  --together-api-key "$TOGETHER_API_KEY"
```

Bu, varsayılan model olarak `together/moonshotai/Kimi-K2.5` ayarlar.

## Ortam notu

Gateway bir daemon olarak çalışıyorsa (launchd/systemd), `TOGETHER_API_KEY`
değerinin bu süreç için kullanılabilir olduğundan emin olun (örneğin `~/.openclaw/.env` içinde veya
`env.shellEnv` aracılığıyla).

## Yerleşik katalog

OpenClaw şu anda bu paketlenmiş Together kataloğuyla gelir:

| Model başvurusu                                            | Ad                                     | Girdi       | Bağlam     | Notlar                           |
| ---------------------------------------------------------- | -------------------------------------- | ----------- | ---------- | -------------------------------- |
| `together/moonshotai/Kimi-K2.5`                            | Kimi K2.5                              | metin, görsel | 262,144    | Varsayılan model; reasoning etkin |
| `together/zai-org/GLM-4.7`                                 | GLM 4.7 Fp8                            | metin       | 202,752    | Genel amaçlı metin modeli        |
| `together/meta-llama/Llama-3.3-70B-Instruct-Turbo`         | Llama 3.3 70B Instruct Turbo           | metin       | 131,072    | Hızlı instruction modeli         |
| `together/meta-llama/Llama-4-Scout-17B-16E-Instruct`       | Llama 4 Scout 17B 16E Instruct         | metin, görsel | 10,000,000 | Çok modlu                        |
| `together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | Llama 4 Maverick 17B 128E Instruct FP8 | metin, görsel | 20,000,000 | Çok modlu                        |
| `together/deepseek-ai/DeepSeek-V3.1`                       | DeepSeek V3.1                          | metin       | 131,072    | Genel metin modeli               |
| `together/deepseek-ai/DeepSeek-R1`                         | DeepSeek R1                            | metin       | 131,072    | Reasoning modeli                 |
| `together/moonshotai/Kimi-K2-Instruct-0905`                | Kimi K2-Instruct 0905                  | metin       | 262,144    | İkincil Kimi metin modeli        |

Onboarding hazır ayarı, varsayılan model olarak `together/moonshotai/Kimi-K2.5` ayarlar.

## Video üretimi

Paketlenmiş `together` eklentisi ayrıca paylaşılan
`video_generate` aracı üzerinden video generation da kaydeder.

- Varsayılan video modeli: `together/Wan-AI/Wan2.2-T2V-A14B`
- Modlar: text-to-video ve tek görsel referans akışları
- `aspectRatio` ve `resolution` desteklenir

Together'ı varsayılan video sağlayıcısı olarak kullanmak için:

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

Paylaşılan araç
parametreleri, sağlayıcı seçimi ve failover davranışı için [Video Generation](/tools/video-generation) bölümüne bakın.
