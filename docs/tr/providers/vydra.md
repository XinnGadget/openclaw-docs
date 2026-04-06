---
read_when:
    - OpenClaw içinde Vydra medya oluşturmayı istiyorsunuz
    - Vydra API anahtarı kurulumu rehberine ihtiyacınız var
summary: OpenClaw içinde Vydra görsel, video ve konuşma kullanın
title: Vydra
x-i18n:
    generated_at: "2026-04-06T03:11:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0fe999e8a5414b8a31a6d7d127bc6bcfc3b4492b8f438ab17dfa9680c5b079b7
    source_path: providers/vydra.md
    workflow: 15
---

# Vydra

Paketlenmiş Vydra plugin’i şunları ekler:

- `vydra/grok-imagine` üzerinden görsel oluşturma
- `vydra/veo3` ve `vydra/kling` üzerinden video oluşturma
- Vydra’nın ElevenLabs destekli TTS yolu üzerinden konuşma sentezi

OpenClaw, bu üç yetenek için de aynı `VYDRA_API_KEY` değerini kullanır.

## Önemli base URL

`https://www.vydra.ai/api/v1` kullanın.

Vydra’nın apex host’u (`https://vydra.ai/api/v1`) şu anda `www` adresine yönlendiriyor. Bazı HTTP istemcileri bu hostlar arası yönlendirmede `Authorization` üstbilgisini düşürür; bu da geçerli bir API anahtarını yanıltıcı bir auth hatasına dönüştürür. Paketlenmiş plugin bunu önlemek için doğrudan `www` base URL’ini kullanır.

## Kurulum

Etkileşimli onboarding:

```bash
openclaw onboard --auth-choice vydra-api-key
```

Veya env değişkenini doğrudan ayarlayın:

```bash
export VYDRA_API_KEY="vydra_live_..."
```

## Görsel oluşturma

Varsayılan görsel modeli:

- `vydra/grok-imagine`

Bunu varsayılan görsel provider’ı olarak ayarlayın:

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

Mevcut paketlenmiş destek yalnızca metinden görsele içindir. Vydra’nın barındırılan düzenleme yolları uzak görsel URL’leri bekler ve OpenClaw henüz paketlenmiş plugin içinde Vydra’ya özgü bir yükleme köprüsü eklemez.

Paylaşılan araç davranışı için bkz. [Image Generation](/tr/tools/image-generation).

## Video oluşturma

Kayıtlı video modelleri:

- metinden videoya için `vydra/veo3`
- görselden videoya için `vydra/kling`

Vydra’yı varsayılan video provider’ı olarak ayarlayın:

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

- `vydra/veo3`, paketlenmiş olarak yalnızca metinden videoya sunulur.
- `vydra/kling` şu anda uzak bir görsel URL referansı gerektirir. Yerel dosya yüklemeleri daha baştan reddedilir.
- Paketlenmiş plugin temkinli kalır ve en-boy oranı, çözünürlük, filigran veya oluşturulan ses gibi belgelenmemiş stil ayarlarını iletmez.

Paylaşılan araç davranışı için bkz. [Video Generation](/tools/video-generation).

## Konuşma sentezi

Vydra’yı konuşma provider’ı olarak ayarlayın:

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

- [Provider Directory](/tr/providers/index)
- [Image Generation](/tr/tools/image-generation)
- [Video Generation](/tools/video-generation)
