---
read_when:
    - Google Gemini modellerini OpenClaw ile kullanmak istiyorsunuz
    - API anahtarı veya OAuth auth akışına ihtiyacınız var
summary: Google Gemini kurulumu (API anahtarı + OAuth, görsel üretimi, medya anlama, web arama)
title: Google (Gemini)
x-i18n:
    generated_at: "2026-04-07T08:48:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: 36cc7c7d8d19f6d4a3fb223af36c8402364fc309d14ffe922bd004203ceb1754
    source_path: providers/google.md
    workflow: 15
---

# Google (Gemini)

Google plugin'i, Google AI Studio üzerinden Gemini modellerine erişim sağlar; ayrıca
Gemini Grounding aracılığıyla görsel üretimi, medya anlama (görsel/ses/video) ve web aramayı da destekler.

- Sağlayıcı: `google`
- Auth: `GEMINI_API_KEY` veya `GOOGLE_API_KEY`
- API: Google Gemini API
- Alternatif sağlayıcı: `google-gemini-cli` (OAuth)

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

## OAuth (Gemini CLI)

Alternatif bir sağlayıcı olan `google-gemini-cli`, API
anahtarı yerine PKCE OAuth kullanır. Bu resmi olmayan bir entegrasyondur; bazı kullanıcılar
hesap kısıtlamaları bildirmektedir. Riski size aittir.

- Varsayılan model: `google-gemini-cli/gemini-3.1-pro-preview`
- Takma ad: `gemini-cli`
- Kurulum ön koşulu: `gemini` adıyla erişilebilen yerel Gemini CLI
  - Homebrew: `brew install gemini-cli`
  - npm: `npm install -g @google/gemini-cli`
- Giriş yapma:

```bash
openclaw models auth login --provider google-gemini-cli --set-default
```

Ortam değişkenleri:

- `OPENCLAW_GEMINI_OAUTH_CLIENT_ID`
- `OPENCLAW_GEMINI_OAUTH_CLIENT_SECRET`

(Veya `GEMINI_CLI_*` varyantları.)

Gemini CLI OAuth istekleri giriş yaptıktan sonra başarısız olursa,
gateway host üzerinde `GOOGLE_CLOUD_PROJECT` veya `GOOGLE_CLOUD_PROJECT_ID` ayarlayın ve
yeniden deneyin.

Tarayıcı akışı başlamadan önce giriş başarısız olursa, yerel `gemini`
komutunun kurulu ve `PATH` içinde olduğundan emin olun. OpenClaw hem Homebrew kurulumlarını
hem de genel npm kurulumlarını, yaygın Windows/npm düzenleri dahil olmak üzere destekler.

Gemini CLI JSON kullanım notları:

- Yanıt metni, CLI JSON içindeki `response` alanından gelir.
- CLI, `usage` alanını boş bıraktığında kullanım verisi `stats` alanına geri düşer.
- `stats.cached`, OpenClaw `cacheRead` değerine normalize edilir.
- `stats.input` eksikse, OpenClaw giriş token'larını
  `stats.input_tokens - stats.cached` değerinden türetir.

## Yetenekler

| Yetenek                | Destekleniyor     |
| ---------------------- | ----------------- |
| Sohbet tamamlama       | Evet              |
| Görsel üretimi         | Evet              |
| Müzik üretimi          | Evet              |
| Görsel anlama          | Evet              |
| Ses transkripsiyonu    | Evet              |
| Video anlama           | Evet              |
| Web arama (Grounding)  | Evet              |
| Thinking/reasoning     | Evet (Gemini 3.1+) |

## Doğrudan Gemini önbellek yeniden kullanımı

Doğrudan Gemini API çalıştırmaları için (`api: "google-generative-ai"`), OpenClaw artık
yapılandırılmış bir `cachedContent` tanıtıcısını Gemini isteklerine aktarır.

- Model başına veya genel parametreleri
  `cachedContent` veya eski `cached_content` ile yapılandırın
- Her ikisi de varsa, `cachedContent` önceliklidir
- Örnek değer: `cachedContents/prebuilt-context`
- Gemini önbellek isabeti kullanımı, yukarı akıştaki `cachedContentTokenCount` değerinden
  OpenClaw `cacheRead` değerine normalize edilir

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

## Görsel üretimi

Paketle gelen `google` görsel üretimi sağlayıcısı varsayılan olarak
`google/gemini-3.1-flash-image-preview` kullanır.

- Ayrıca `google/gemini-3-pro-image-preview` desteği de vardır
- Üretim: istek başına en fazla 4 görsel
- Düzenleme modu: etkin, en fazla 5 giriş görseli
- Geometri denetimleri: `size`, `aspectRatio` ve `resolution`

Yalnızca OAuth kullanan `google-gemini-cli` sağlayıcısı ayrı bir metin çıkarımı
yüzeyidir. Görsel üretimi, medya anlama ve Gemini Grounding,
`google` sağlayıcı kimliğinde kalır.

Google'ı varsayılan görsel sağlayıcısı olarak kullanmak için:

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

Paylaşılan tool
parametreleri, sağlayıcı seçimi ve yedekleme davranışı için [Image Generation](/tr/tools/image-generation) belgesine bakın.

## Video üretimi

Paketle gelen `google` plugin'i ayrıca paylaşılan
`video_generate` tool'u üzerinden video üretimini de kaydeder.

- Varsayılan video modeli: `google/veo-3.1-fast-generate-preview`
- Modlar: text-to-video, image-to-video ve single-video reference akışları
- `aspectRatio`, `resolution` ve `audio` desteklenir
- Geçerli süre sınırlaması: **4 ila 8 saniye**

Google'ı varsayılan video sağlayıcısı olarak kullanmak için:

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

Paylaşılan tool
parametreleri, sağlayıcı seçimi ve yedekleme davranışı için [Video Generation](/tr/tools/video-generation) belgesine bakın.

## Müzik üretimi

Paketle gelen `google` plugin'i ayrıca paylaşılan
`music_generate` tool'u üzerinden müzik üretimini de kaydeder.

- Varsayılan müzik modeli: `google/lyria-3-clip-preview`
- Ayrıca `google/lyria-3-pro-preview` desteği de vardır
- Prompt denetimleri: `lyrics` ve `instrumental`
- Çıktı biçimi: varsayılan olarak `mp3`, ayrıca `google/lyria-3-pro-preview` üzerinde `wav`
- Referans girdileri: en fazla 10 görsel
- Oturum destekli çalıştırmalar, `action: "status"` dahil olmak üzere paylaşılan görev/durum akışı üzerinden ayrıştırılır

Google'ı varsayılan müzik sağlayıcısı olarak kullanmak için:

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

Paylaşılan tool
parametreleri, sağlayıcı seçimi ve yedekleme davranışı için [Music Generation](/tr/tools/music-generation) belgesine bakın.

## Ortam notu

Gateway bir daemon olarak çalışıyorsa (launchd/systemd), `GEMINI_API_KEY`
değerinin bu süreç için erişilebilir olduğundan emin olun (örneğin `~/.openclaw/.env` içinde veya
`env.shellEnv` aracılığıyla).
