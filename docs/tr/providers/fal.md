---
read_when:
    - OpenClaw'da fal görsel üretimini kullanmak istiyorsunuz
    - FAL_KEY kimlik doğrulama akışına ihtiyacınız var
    - image_generate veya video_generate için fal varsayılanlarını istiyorsunuz
summary: OpenClaw'da fal görsel ve video üretimi kurulumu
title: fal
x-i18n:
    generated_at: "2026-04-06T03:11:15Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1922907d2c8360c5877a56495323d54bd846d47c27a801155e3d11e3f5706fbd
    source_path: providers/fal.md
    workflow: 15
---

# fal

OpenClaw, barındırılan görsel ve video üretimi için paketli bir `fal` sağlayıcısıyla gelir.

- Sağlayıcı: `fal`
- Kimlik doğrulama: `FAL_KEY` (kanonik; `FAL_API_KEY` de yedek olarak çalışır)
- API: fal model uç noktaları

## Hızlı başlangıç

1. API anahtarını ayarlayın:

```bash
openclaw onboard --auth-choice fal-api-key
```

2. Varsayılan bir görsel modeli ayarlayın:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "fal/fal-ai/flux/dev",
      },
    },
  },
}
```

## Görsel üretimi

Paketli `fal` görsel üretim sağlayıcısı varsayılan olarak
`fal/fal-ai/flux/dev` kullanır.

- Üretim: istek başına en fazla 4 görsel
- Düzenleme modu: etkin, 1 referans görsel
- `size`, `aspectRatio` ve `resolution` desteklenir
- Mevcut düzenleme kısıtı: fal görsel düzenleme uç noktası
  `aspectRatio` geçersiz kılmalarını desteklemez

fal'i varsayılan görsel sağlayıcısı olarak kullanmak için:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "fal/fal-ai/flux/dev",
      },
    },
  },
}
```

## Video üretimi

Paketli `fal` video üretim sağlayıcısı varsayılan olarak
`fal/fal-ai/minimax/video-01-live` kullanır.

- Modlar: metinden videoya ve tek görsel referans akışları
- Çalışma zamanı: uzun süren işler için kuyruk destekli gönderim/durum/sonuç akışı

fal'i varsayılan video sağlayıcısı olarak kullanmak için:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "fal/fal-ai/minimax/video-01-live",
      },
    },
  },
}
```

## İlgili

- [Görsel Üretimi](/tr/tools/image-generation)
- [Video Üretimi](/tools/video-generation)
- [Yapılandırma Başvurusu](/tr/gateway/configuration-reference#agent-defaults)
