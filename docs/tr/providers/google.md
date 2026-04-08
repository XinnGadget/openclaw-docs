---
read_when:
    - OpenClaw ile Google Gemini modellerini kullanmak istiyorsunuz
    - API anahtarı veya OAuth kimlik doğrulama akışına ihtiyacınız var
summary: Google Gemini kurulumu (API anahtarı + OAuth, görüntü oluşturma, medya anlama, web araması)
title: Google (Gemini)
x-i18n:
    generated_at: "2026-04-08T02:17:14Z"
    model: gpt-5.4
    provider: openai
    source_hash: e9e558f5ce35c853e0240350be9a1890460c5f7f7fd30b05813a656497dee516
    source_path: providers/google.md
    workflow: 15
---

# Google (Gemini)

Google eklentisi, Google AI Studio üzerinden Gemini modellerine erişim sağlar; ayrıca
Gemini Grounding aracılığıyla görüntü oluşturma, medya anlama (görüntü/ses/video) ve web aramasını da destekler.

- Sağlayıcı: `google`
- Kimlik doğrulama: `GEMINI_API_KEY` veya `GOOGLE_API_KEY`
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

Alternatif bir sağlayıcı olan `google-gemini-cli`, API anahtarı yerine PKCE OAuth kullanır.
Bu resmi olmayan bir entegrasyondur; bazı kullanıcılar hesap
kısıtlamaları bildirmektedir. Riski size ait olmak üzere kullanın.

- Varsayılan model: `google-gemini-cli/gemini-3-flash-preview`
- Takma ad: `gemini-cli`
- Kurulum önkoşulu: yerel Gemini CLI `gemini` olarak kullanılabilir olmalıdır
  - Homebrew: `brew install gemini-cli`
  - npm: `npm install -g @google/gemini-cli`
- Giriş:

```bash
openclaw models auth login --provider google-gemini-cli --set-default
```

Ortam değişkenleri:

- `OPENCLAW_GEMINI_OAUTH_CLIENT_ID`
- `OPENCLAW_GEMINI_OAUTH_CLIENT_SECRET`

(Veya `GEMINI_CLI_*` varyantları.)

Gemini CLI OAuth istekleri girişten sonra başarısız olursa,
gateway host üzerinde `GOOGLE_CLOUD_PROJECT` veya `GOOGLE_CLOUD_PROJECT_ID` ayarlayın ve
yeniden deneyin.

Giriş, tarayıcı akışı başlamadan önce başarısız olursa, yerel `gemini`
komutunun kurulu olduğundan ve `PATH` üzerinde bulunduğundan emin olun. OpenClaw hem Homebrew kurulumlarını
hem de genel npm kurulumlarını, yaygın Windows/npm düzenleri dahil, destekler.

Gemini CLI JSON kullanım notları:

- Yanıt metni CLI JSON `response` alanından gelir.
- CLI `usage` alanını boş bıraktığında kullanım `stats` değerine geri döner.
- `stats.cached`, OpenClaw `cacheRead` değerine normalize edilir.
- `stats.input` eksikse OpenClaw giriş tokenlarını
  `stats.input_tokens - stats.cached` değerinden türetir.

## Yetenekler

| Yetenek               | Destekleniyor     |
| --------------------- | ----------------- |
| Sohbet tamamlamaları  | Evet              |
| Görüntü oluşturma     | Evet              |
| Müzik oluşturma       | Evet              |
| Görüntü anlama        | Evet              |
| Ses transkripsiyonu   | Evet              |
| Video anlama          | Evet              |
| Web araması (Grounding) | Evet            |
| Thinking/reasoning    | Evet (Gemini 3.1+) |

## Doğrudan Gemini önbellek yeniden kullanımı

Doğrudan Gemini API çalıştırmaları için (`api: "google-generative-ai"`), OpenClaw artık
yapılandırılmış bir `cachedContent` tanıtıcısını Gemini isteklerine iletir.

- Model başına veya genel parametreleri
  `cachedContent` ya da eski `cached_content` ile yapılandırın
- Her ikisi de varsa `cachedContent` önceliklidir
- Örnek değer: `cachedContents/prebuilt-context`
- Gemini önbellek isabeti kullanımı, üst akıştaki `cachedContentTokenCount` değerinden
  OpenClaw `cacheRead` alanına normalize edilir

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

## Görüntü oluşturma

Paketlenmiş `google` görüntü oluşturma sağlayıcısı varsayılan olarak
`google/gemini-3.1-flash-image-preview` kullanır.

- Ayrıca `google/gemini-3-pro-image-preview` desteklenir
- Oluşturma: istek başına en fazla 4 görüntü
- Düzenleme modu: etkin, en fazla 5 giriş görüntüsü
- Geometri denetimleri: `size`, `aspectRatio` ve `resolution`

Yalnızca OAuth kullanan `google-gemini-cli` sağlayıcısı ayrı bir metin çıkarımı
yüzeyidir. Görüntü oluşturma, medya anlama ve Gemini Grounding
`google` sağlayıcı kimliği üzerinde kalır.

Google'ı varsayılan görüntü sağlayıcısı olarak kullanmak için:

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

Paylaşılan araç
parametreleri, sağlayıcı seçimi ve yük devretme davranışı için [Görüntü Oluşturma](/tr/tools/image-generation) bölümüne bakın.

## Video oluşturma

Paketlenmiş `google` eklentisi ayrıca paylaşılan
`video_generate` aracı üzerinden video oluşturmayı kaydeder.

- Varsayılan video modeli: `google/veo-3.1-fast-generate-preview`
- Modlar: metinden videoya, görüntüden videoya ve tek videolu referans akışları
- `aspectRatio`, `resolution` ve `audio` desteklenir
- Mevcut süre sınırı: **4 ila 8 saniye**

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

Paylaşılan araç
parametreleri, sağlayıcı seçimi ve yük devretme davranışı için [Video Oluşturma](/tr/tools/video-generation) bölümüne bakın.

## Müzik oluşturma

Paketlenmiş `google` eklentisi ayrıca paylaşılan
`music_generate` aracı üzerinden müzik oluşturmayı kaydeder.

- Varsayılan müzik modeli: `google/lyria-3-clip-preview`
- Ayrıca `google/lyria-3-pro-preview` desteklenir
- Komut denetimleri: `lyrics` ve `instrumental`
- Çıkış biçimi: varsayılan olarak `mp3`, ayrıca `google/lyria-3-pro-preview` üzerinde `wav`
- Referans girdileri: en fazla 10 görüntü
- Oturum destekli çalıştırmalar, `action: "status"` dahil olmak üzere paylaşılan görev/durum akışı üzerinden ayrılır

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

Paylaşılan araç
parametreleri, sağlayıcı seçimi ve yük devretme davranışı için [Müzik Oluşturma](/tr/tools/music-generation) bölümüne bakın.

## Ortam notu

Gateway bir daemon olarak çalışıyorsa (launchd/systemd), `GEMINI_API_KEY`
değerinin bu sürece erişilebilir olduğundan emin olun (örneğin `~/.openclaw/.env` içinde veya
`env.shellEnv` aracılığıyla).
