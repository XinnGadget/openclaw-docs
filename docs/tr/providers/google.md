---
read_when:
    - OpenClaw ile Google Gemini modellerini kullanmak istiyorsunuz
    - API anahtarı auth akışına ihtiyacınız var
summary: Google Gemini kurulumu (API anahtarı, görsel oluşturma, medya anlama, web search)
title: Google (Gemini)
x-i18n:
    generated_at: "2026-04-06T03:11:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: 358d33a68275b01ebd916a3621dd651619cb9a1d062e2fb6196a7f3c501c015a
    source_path: providers/google.md
    workflow: 15
---

# Google (Gemini)

Google plugin’i, Google AI Studio üzerinden Gemini modellerine erişim sağlar; ayrıca
Gemini Grounding aracılığıyla görsel oluşturma, medya anlama (görsel/ses/video) ve web search de sunar.

- Provider: `google`
- Auth: `GEMINI_API_KEY` veya `GOOGLE_API_KEY`
- API: Google Gemini API

## Hızlı başlangıç

1. API anahtarını ayarlayın:

```bash
openclaw onboard --auth-choice gemini-api-key
```

2. Varsayılan bir model ayarlayın:

```json5
{
  agents: {
    defaults: {
      model: { primary: "google/gemini-3.1-pro-preview" },
    },
  },
}
```

## Etkileşimsiz örnek

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice gemini-api-key \
  --gemini-api-key "$GEMINI_API_KEY"
```

## Yetenekler

| Yetenek                | Destek durumu     |
| ---------------------- | ----------------- |
| Sohbet tamamlamaları   | Evet              |
| Görsel oluşturma       | Evet              |
| Müzik oluşturma        | Evet              |
| Görsel anlama          | Evet              |
| Ses yazıya dökme       | Evet              |
| Video anlama           | Evet              |
| Web search (Grounding) | Evet              |
| Thinking/reasoning     | Evet (Gemini 3.1+) |

## Doğrudan Gemini önbellek yeniden kullanımı

Doğrudan Gemini API çalıştırmaları için (`api: "google-generative-ai"`), OpenClaw artık
yapılandırılmış bir `cachedContent` tanıtıcısını Gemini isteklerine iletir.

- Model başına veya global parametreleri `cachedContent` ya da eski
  `cached_content` ile yapılandırın
- Her ikisi de mevcutsa `cachedContent` kazanır
- Örnek değer: `cachedContents/prebuilt-context`
- Gemini önbellek isabeti kullanımı, upstream `cachedContentTokenCount`
  üzerinden OpenClaw `cacheRead` içine normalize edilir

Örnek:

```json5
{
  agents: {
    defaults: {
      models: {
        "google/gemini-2.5-pro": {
          params: {
            cachedContent: "cachedContents/prebuilt-context",
          },
        },
      },
    },
  },
}
```

## Görsel oluşturma

Paketlenmiş `google` görsel oluşturma provider’ı varsayılan olarak
`google/gemini-3.1-flash-image-preview` kullanır.

- Ayrıca `google/gemini-3-pro-image-preview` desteği vardır
- Oluşturma: istek başına en fazla 4 görsel
- Düzenleme kipi: etkin, en fazla 5 giriş görseli
- Geometri denetimleri: `size`, `aspectRatio` ve `resolution`

Görsel oluşturma, medya anlama ve Gemini Grounding, `google` provider kimliği
üzerinde kalır.

Google’ı varsayılan görsel provider’ı olarak kullanmak için:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "google/gemini-3.1-flash-image-preview",
      },
    },
  },
}
```

Paylaşılan araç parametreleri, provider seçimi ve yedeğe düşme davranışı için
bkz. [Image Generation](/tr/tools/image-generation).

## Video oluşturma

Paketlenmiş `google` plugin’i, paylaşılan `video_generate` aracı üzerinden video
oluşturmayı da kaydeder.

- Varsayılan video modeli: `google/veo-3.1-fast-generate-preview`
- Kipler: metinden videoya, görselden videoya ve tek videolu referans akışları
- `aspectRatio`, `resolution` ve `audio` desteklenir
- Mevcut süre sınırı: **4 ila 8 saniye**

Google’ı varsayılan video provider’ı olarak kullanmak için:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "google/veo-3.1-fast-generate-preview",
      },
    },
  },
}
```

Paylaşılan araç parametreleri, provider seçimi ve yedeğe düşme davranışı için
bkz. [Video Generation](/tools/video-generation).

## Müzik oluşturma

Paketlenmiş `google` plugin’i, paylaşılan `music_generate` aracı üzerinden müzik
oluşturmayı da kaydeder.

- Varsayılan müzik modeli: `google/lyria-3-clip-preview`
- Ayrıca `google/lyria-3-pro-preview` desteği vardır
- Komut denetimleri: `lyrics` ve `instrumental`
- Çıkış biçimi: varsayılan olarak `mp3`, ayrıca `google/lyria-3-pro-preview` üzerinde `wav`
- Referans girdileri: en fazla 10 görsel
- Oturum destekli çalıştırmalar, `action: "status"` dahil olmak üzere paylaşılan görev/durum akışı üzerinden ayrılır

Google’ı varsayılan müzik provider’ı olarak kullanmak için:

```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "google/lyria-3-clip-preview",
      },
    },
  },
}
```

Paylaşılan araç parametreleri, provider seçimi ve yedeğe düşme davranışı için
bkz. [Music Generation](/tools/music-generation).

## Ortam notu

Gateway bir daemon (launchd/systemd) olarak çalışıyorsa, `GEMINI_API_KEY`
değerinin o süreç için kullanılabilir olduğundan emin olun (örneğin `~/.openclaw/.env`
içinde veya `env.shellEnv` aracılığıyla).
