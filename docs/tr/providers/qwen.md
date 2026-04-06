---
read_when:
    - Qwen'i OpenClaw ile kullanmak istiyorsunuz
    - Daha önce Qwen OAuth kullandınız
summary: Qwen Cloud'u OpenClaw'ın paketli qwen sağlayıcısı üzerinden kullanın
title: Qwen
x-i18n:
    generated_at: "2026-04-06T03:11:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: f175793693ab6a4c3f1f4d42040e673c15faf7603a500757423e9e06977c989d
    source_path: providers/qwen.md
    workflow: 15
---

# Qwen

<Warning>

**Qwen OAuth kaldırıldı.** `portal.qwen.ai` uç noktalarını kullanan
ücretsiz katman OAuth entegrasyonu
(`qwen-portal`) artık kullanılamıyor.
Arka plan için [Issue #49557](https://github.com/openclaw/openclaw/issues/49557) bölümüne bakın.

</Warning>

## Önerilen: Qwen Cloud

OpenClaw artık Qwen'i kanonik kimliği
`qwen` olan birinci sınıf paketli sağlayıcı olarak ele alıyor. Paketli sağlayıcı Qwen Cloud / Alibaba DashScope ve
Coding Plan uç noktalarını hedefler ve eski `modelstudio` kimliklerini
uyumluluk diğer adı olarak çalışır durumda tutar.

- Sağlayıcı: `qwen`
- Tercih edilen ortam değişkeni: `QWEN_API_KEY`
- Uyumluluk için kabul edilenler: `MODELSTUDIO_API_KEY`, `DASHSCOPE_API_KEY`
- API stili: OpenAI uyumlu

`qwen3.6-plus` kullanmak istiyorsanız **Standard (kullandıkça öde)** uç noktasını tercih edin.
Coding Plan desteği, herkese açık katalogun gerisinde kalabilir.

```bash
# Global Coding Plan endpoint
openclaw onboard --auth-choice qwen-api-key

# China Coding Plan endpoint
openclaw onboard --auth-choice qwen-api-key-cn

# Global Standard (pay-as-you-go) endpoint
openclaw onboard --auth-choice qwen-standard-api-key

# China Standard (pay-as-you-go) endpoint
openclaw onboard --auth-choice qwen-standard-api-key-cn
```

Eski `modelstudio-*` auth-choice kimlikleri ve `modelstudio/...` model başvuruları hâlâ
uyumluluk diğer adları olarak çalışır, ancak yeni kurulum akışları kanonik
`qwen-*` auth-choice kimliklerini ve `qwen/...` model başvurularını tercih etmelidir.

Onboarding sonrasında varsayılan bir model ayarlayın:

```json5
{
  agents: {
    defaults: {
      model: { primary: "qwen/qwen3.5-plus" },
    },
  },
}
```

## Plan türleri ve uç noktalar

| Plan                       | Bölge  | Auth choice                | Uç nokta                                         |
| -------------------------- | ------ | -------------------------- | ------------------------------------------------ |
| Standard (kullandıkça öde) | Çin    | `qwen-standard-api-key-cn` | `dashscope.aliyuncs.com/compatible-mode/v1`      |
| Standard (kullandıkça öde) | Global | `qwen-standard-api-key`    | `dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| Coding Plan (abonelik)     | Çin    | `qwen-api-key-cn`          | `coding.dashscope.aliyuncs.com/v1`               |
| Coding Plan (abonelik)     | Global | `qwen-api-key`             | `coding-intl.dashscope.aliyuncs.com/v1`          |

Sağlayıcı, auth choice seçiminize göre uç noktayı otomatik seçer. Kanonik
seçimler `qwen-*` ailesini kullanır; `modelstudio-*` ise yalnızca uyumluluk içindir.
Yapılandırmada özel bir `baseUrl` ile geçersiz kılabilirsiniz.

Yerel Model Studio uç noktaları, paylaşılan
`openai-completions` taşımasında akış kullanımı uyumluluğunu bildirir. OpenClaw artık bunu uç nokta
yeteneklerine göre anahtarlıyor; böylece aynı yerel ana bilgisayarları hedefleyen
DashScope uyumlu özel sağlayıcı kimlikleri, özellikle yerleşik `qwen` sağlayıcı kimliğini
gerektirmek yerine aynı yerel akış kullanımı davranışını devralır.

## API anahtarınızı alın

- **Anahtarları yönetin**: [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys)
- **Belgeler**: [docs.qwencloud.com](https://docs.qwencloud.com/developer-guides/getting-started/introduction)

## Yerleşik katalog

OpenClaw şu anda şu paketli Qwen kataloğunu sunar:

| Model başvurusu            | Girdi       | Bağlam    | Notlar                                             |
| -------------------------- | ----------- | --------- | -------------------------------------------------- |
| `qwen/qwen3.5-plus`        | metin, görsel | 1,000,000 | Varsayılan model                                   |
| `qwen/qwen3.6-plus`        | metin, görsel | 1,000,000 | Bu modele ihtiyacınız varsa Standard uç noktaları tercih edin |
| `qwen/qwen3-max-2026-01-23`| metin       | 262,144   | Qwen Max hattı                                     |
| `qwen/qwen3-coder-next`    | metin       | 262,144   | Kodlama                                            |
| `qwen/qwen3-coder-plus`    | metin       | 1,000,000 | Kodlama                                            |
| `qwen/MiniMax-M2.5`        | metin       | 1,000,000 | Akıl yürütme etkin                                 |
| `qwen/glm-5`               | metin       | 202,752   | GLM                                                |
| `qwen/glm-4.7`             | metin       | 202,752   | GLM                                                |
| `qwen/kimi-k2.5`           | metin, görsel | 262,144   | Alibaba üzerinden Moonshot AI                      |

Bir model paketli katalogda bulunsa bile, kullanılabilirlik uç noktaya ve faturalandırma planına göre yine de değişebilir.

Yerel akış kullanımı uyumluluğu hem Coding Plan ana bilgisayarları hem de
Standard DashScope uyumlu ana bilgisayarlar için geçerlidir:

- `https://coding.dashscope.aliyuncs.com/v1`
- `https://coding-intl.dashscope.aliyuncs.com/v1`
- `https://dashscope.aliyuncs.com/compatible-mode/v1`
- `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`

## Qwen 3.6 Plus kullanılabilirliği

`qwen3.6-plus`, Standard (kullandıkça öde) Model Studio
uç noktalarında kullanılabilir:

- Çin: `dashscope.aliyuncs.com/compatible-mode/v1`
- Global: `dashscope-intl.aliyuncs.com/compatible-mode/v1`

Coding Plan uç noktaları
`qwen3.6-plus` için "unsupported model" hatası döndürüyorsa, Coding Plan
uç noktası/anahtar çifti yerine Standard (kullandıkça öde) kullanın.

## Yetenek planı

`qwen` uzantısı, yalnızca kodlama/metin modelleri için değil, tüm Qwen
Cloud yüzeyi için üretici evi olarak konumlandırılıyor.

- Metin/sohbet modelleri: şu anda paketli
- Araç çağırma, yapılandırılmış çıktı, düşünme: OpenAI uyumlu taşımadan devralınır
- Görsel üretimi: sağlayıcı-plugin katmanında planlanıyor
- Görsel/video anlama: şu anda Standard uç noktasında paketli
- Konuşma/ses: sağlayıcı-plugin katmanında planlanıyor
- Bellek embedding'leri/reranking: embedding bağdaştırıcı yüzeyi üzerinden planlanıyor
- Video üretimi: şu anda paylaşılan video üretim yeteneği üzerinden paketli

## Çok kipli eklentiler

`qwen` uzantısı artık ayrıca şunları da sunar:

- `qwen-vl-max-latest` üzerinden video anlama
- Şu modeller üzerinden Wan video üretimi:
  - `wan2.6-t2v` (varsayılan)
  - `wan2.6-i2v`
  - `wan2.6-r2v`
  - `wan2.6-r2v-flash`
  - `wan2.7-r2v`

Bu çok kipli yüzeyler **Standard** DashScope uç noktalarını kullanır, Coding Plan uç noktalarını değil.

- Global/Uluslararası Standard base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Çin Standard base URL: `https://dashscope.aliyuncs.com/compatible-mode/v1`

Video üretimi için OpenClaw, işi göndermeden önce yapılandırılmış Qwen bölgesini
eşleşen DashScope AIGC ana bilgisayarına eşler:

- Global/Uluslararası: `https://dashscope-intl.aliyuncs.com`
- Çin: `https://dashscope.aliyuncs.com`

Bu da, Coding Plan veya Standard Qwen ana bilgisayarlarından birine işaret eden normal bir
`models.providers.qwen.baseUrl` değerinin bile video üretimini doğru
bölgesel DashScope video uç noktasında tutacağı anlamına gelir.

Video üretimi için varsayılan modeli açıkça ayarlayın:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: { primary: "qwen/wan2.6-t2v" },
    },
  },
}
```

Mevcut paketli Qwen video üretim sınırları:

- İstek başına en fazla **1** çıktı videosu
- En fazla **1** girdi görseli
- En fazla **4** girdi videosu
- En fazla **10 saniye** süre
- `size`, `aspectRatio`, `resolution`, `audio` ve `watermark` desteklenir
- Referans görsel/video modu şu anda **uzak http(s) URL'leri** gerektirir. Yerel
  dosya yolları en baştan reddedilir çünkü DashScope video uç noktası bu referanslar için
  yüklenmiş yerel tamponları kabul etmez.

Paylaşılan araç
parametreleri, sağlayıcı seçimi ve failover davranışı için bkz. [Video Üretimi](/tools/video-generation).

## Ortam notu

Gateway bir daemon olarak çalışıyorsa (launchd/systemd), `QWEN_API_KEY` değerinin
bu süreç için erişilebilir olduğundan emin olun (örneğin `~/.openclaw/.env` içinde veya
`env.shellEnv` aracılığıyla).
