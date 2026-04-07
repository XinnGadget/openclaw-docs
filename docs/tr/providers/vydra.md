---
read_when:
    - OpenClaw içinde Vydra medya üretimi istiyorsunuz
    - Vydra API anahtarı kurulumu rehberine ihtiyacınız var
summary: OpenClaw içinde Vydra görüntü, video ve konuşma kullanımı
title: Vydra
x-i18n:
    generated_at: "2026-04-07T08:48:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: 24006a687ed6f9792e7b2b10927cc7ad71c735462a92ce03d5fa7c2b2ee2fcc2
    source_path: providers/vydra.md
    workflow: 15
---

# Vydra

Paketlenmiş Vydra plugin'i şunları ekler:

- `vydra/grok-imagine` üzerinden görüntü üretimi
- `vydra/veo3` ve `vydra/kling` üzerinden video üretimi
- Vydra'nın ElevenLabs destekli TTS rotası üzerinden konuşma sentezi

OpenClaw, bu üç yeteneğin tamamı için aynı `VYDRA_API_KEY` değerini kullanır.

## Önemli temel URL

`https://www.vydra.ai/api/v1` kullanın.

Vydra'nın apex host'u (`https://vydra.ai/api/v1`) şu anda `www` adresine yönlendiriyor. Bazı HTTP istemcileri bu hostlar arası yönlendirmede `Authorization` başlığını düşürüyor; bu da geçerli bir API anahtarını yanıltıcı bir kimlik doğrulama hatasına dönüştürüyor. Paketlenmiş plugin bunu önlemek için doğrudan `www` temel URL'sini kullanır.

## Kurulum

Etkileşimli onboarding:

```bash
openclaw onboard --auth-choice vydra-api-key
```

Veya env değişkenini doğrudan ayarlayın:

```bash
export VYDRA_API_KEY="vydra_live_..."
```

## Görüntü üretimi

Varsayılan görüntü modeli:

- `vydra/grok-imagine`

Bunu varsayılan görüntü sağlayıcısı olarak ayarlayın:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "vydra/grok-imagine",
      },
    },
  },
}
```

Mevcut paketlenmiş destek yalnızca metinden görüntüye içindir. Vydra'nın barındırılan düzenleme rotaları uzak görüntü URL'leri bekler ve OpenClaw henüz paketlenmiş plugin'de Vydra'ya özgü bir yükleme köprüsü eklemez.

Paylaşılan araç davranışı için bkz. [Image Generation](/tr/tools/image-generation).

## Video üretimi

Kayıtlı video modelleri:

- metinden videoya için `vydra/veo3`
- görüntüden videoya için `vydra/kling`

Vydra'yı varsayılan video sağlayıcısı olarak ayarlayın:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "vydra/veo3",
      },
    },
  },
}
```

Notlar:

- `vydra/veo3`, yalnızca metinden videoya olarak paketlenmiştir.
- `vydra/kling` şu anda uzak bir görüntü URL başvurusu gerektirir. Yerel dosya yüklemeleri en başta reddedilir.
- Vydra'nın mevcut `kling` HTTP rotası, `image_url` mı yoksa `video_url` mu gerektirdiği konusunda tutarsızlık gösterdi; paketlenmiş sağlayıcı aynı uzak görüntü URL'sini her iki alana da eşler.
- Paketlenmiş plugin temkinli kalır ve en-boy oranı, çözünürlük, watermark veya üretilmiş ses gibi belgelenmemiş stil ayarlarını iletmez.

Sağlayıcıya özgü canlı kapsam:

```bash
OPENCLAW_LIVE_TEST=1 \
OPENCLAW_LIVE_VYDRA_VIDEO=1 \
pnpm test:live -- extensions/vydra/vydra.live.test.ts
```

Paketlenmiş Vydra canlı dosyası artık şunları kapsar:

- `vydra/veo3` metinden videoya
- uzak bir görüntü URL'si kullanarak `vydra/kling` görüntüden videoya

Gerektiğinde uzak görüntü fixture'ını geçersiz kılın:

```bash
export OPENCLAW_LIVE_VYDRA_KLING_IMAGE_URL="https://example.com/reference.png"
```

Paylaşılan araç davranışı için bkz. [Video Generation](/tr/tools/video-generation).

## Konuşma sentezi

Vydra'yı konuşma sağlayıcısı olarak ayarlayın:

```json5
{
  messages: {
    tts: {
      provider: "vydra",
      providers: {
        vydra: {
          apiKey: "${VYDRA_API_KEY}",
          voiceId: "21m00Tcm4TlvDq8ikWAM",
        },
      },
    },
  },
}
```

Varsayılanlar:

- model: `elevenlabs/tts`
- voice id: `21m00Tcm4TlvDq8ikWAM`

Paketlenmiş plugin şu anda bilinen iyi bir varsayılan sesi sunar ve MP3 ses dosyaları döndürür.

## İlgili

- [Sağlayıcı Dizini](/tr/providers/index)
- [Image Generation](/tr/tools/image-generation)
- [Video Generation](/tr/tools/video-generation)
