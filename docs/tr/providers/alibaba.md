---
read_when:
    - OpenClaw içinde Alibaba Wan video üretimini kullanmak istiyorsunuz
    - Video üretimi için Model Studio veya DashScope API anahtarı kurulumu yapmanız gerekiyor
summary: OpenClaw içinde Alibaba Model Studio Wan video üretimi
title: Alibaba Model Studio
x-i18n:
    generated_at: "2026-04-06T03:10:04Z"
    model: gpt-5.4
    provider: openai
    source_hash: 97a1eddc7cbd816776b9368f2a926b5ef9ee543f08d151a490023736f67dc635
    source_path: providers/alibaba.md
    workflow: 15
---

# Alibaba Model Studio

OpenClaw, Alibaba Model Studio / DashScope üzerinde Wan modelleri için paketlenmiş bir `alibaba` video-generation sağlayıcısıyla gelir.

- Sağlayıcı: `alibaba`
- Tercih edilen kimlik doğrulama: `MODELSTUDIO_API_KEY`
- Kabul edilen diğerleri: `DASHSCOPE_API_KEY`, `QWEN_API_KEY`
- API: DashScope / Model Studio eşzamansız video üretimi

## Hızlı başlangıç

1. Bir API anahtarı ayarlayın:

```bash
openclaw onboard --auth-choice qwen-standard-api-key
```

2. Varsayılan bir video modeli ayarlayın:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "alibaba/wan2.6-t2v",
      },
    },
  },
}
```

## Yerleşik Wan modelleri

Paketlenmiş `alibaba` sağlayıcısı şu anda şunları kaydeder:

- `alibaba/wan2.6-t2v`
- `alibaba/wan2.6-i2v`
- `alibaba/wan2.6-r2v`
- `alibaba/wan2.6-r2v-flash`
- `alibaba/wan2.7-r2v`

## Mevcut sınırlar

- İstek başına en fazla **1** çıktı videosu
- En fazla **1** giriş görseli
- En fazla **4** giriş videosu
- En fazla **10 saniye** süre
- `size`, `aspectRatio`, `resolution`, `audio` ve `watermark` desteklenir
- Referans görsel/video modu şu anda **uzak http(s) URL'leri** gerektirir

## Qwen ile ilişkisi

Paketlenmiş `qwen` sağlayıcısı da Wan video üretimi için Alibaba tarafından barındırılan DashScope uç noktalarını kullanır. Şunları kullanın:

- Kanonik Qwen sağlayıcı yüzeyini istiyorsanız `qwen/...`
- Doğrudan satıcıya ait Wan video yüzeyini istiyorsanız `alibaba/...`

## İlgili

- [Video Generation](/tools/video-generation)
- [Qwen](/tr/providers/qwen)
- [Configuration Reference](/tr/gateway/configuration-reference#agent-defaults)
