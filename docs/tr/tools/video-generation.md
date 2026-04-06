---
read_when:
    - Ajan aracılığıyla video üretiyorsunuz
    - Video üretim sağlayıcılarını ve modellerini yapılandırıyorsunuz
    - video_generate araç parametrelerini anlamanız gerekiyor
summary: 12 sağlayıcı arka ucu kullanarak metinden, görsellerden veya mevcut videolardan video oluşturun
title: Video Üretimi
x-i18n:
    generated_at: "2026-04-06T03:14:20Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4afec87368232221db1aa5a3980254093d6a961b17271b2dcbf724e6bd455b16
    source_path: tools/video-generation.md
    workflow: 15
---

# Video Üretimi

OpenClaw ajanları metin prompt'larından, referans görsellerden veya mevcut videolardan video üretebilir. On iki sağlayıcı arka ucu desteklenir; her biri farklı model seçenekleri, girdi modları ve özellik kümeleri sunar. Ajan, yapılandırmanıza ve kullanılabilir API anahtarlarına göre doğru sağlayıcıyı otomatik olarak seçer.

<Note>
`video_generate` aracı yalnızca en az bir video üretim sağlayıcısı mevcut olduğunda görünür. Ajan araçlarınızda bunu görmüyorsanız bir sağlayıcı API anahtarı ayarlayın veya `agents.defaults.videoGenerationModel` yapılandırın.
</Note>

## Hızlı başlangıç

1. Desteklenen herhangi bir sağlayıcı için bir API anahtarı ayarlayın:

```bash
export GEMINI_API_KEY="your-key"
```

2. İsteğe bağlı olarak varsayılan bir modeli sabitleyin:

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "google/veo-3.1-fast-generate-preview"
```

3. Ajana sorun:

> Gün batımında sörf yapan dost canlısı bir ıstakozun 5 saniyelik sinematik bir videosunu oluştur.

Ajan `video_generate` aracını otomatik olarak çağırır. Araç allowlist yapılandırması gerekmez.

## Video oluşturduğunuzda ne olur

Video üretimi eşzamansızdır. Ajan bir oturumda `video_generate` çağırdığında:

1. OpenClaw isteği sağlayıcıya gönderir ve hemen bir görev kimliği döndürür.
2. Sağlayıcı işi arka planda işler (genellikle sağlayıcıya ve çözünürlüğe bağlı olarak 30 saniye ile 5 dakika arası).
3. Video hazır olduğunda OpenClaw aynı oturumu dahili bir tamamlama olayıyla uyandırır.
4. Ajan tamamlanan videoyu özgün konuşmaya geri gönderir.

Bir iş sürerken, aynı oturumdaki yinelenen `video_generate` çağrıları yeni bir üretim başlatmak yerine mevcut görev durumunu döndürür. İlerlemeyi CLI'dan kontrol etmek için `openclaw tasks list` veya `openclaw tasks show <taskId>` kullanın.

Oturum destekli ajan çalıştırmalarının dışında (örneğin doğrudan araç çağrıları), araç satır içi üretime geri döner ve son medya yolunu aynı turda döndürür.

## Desteklenen sağlayıcılar

| Sağlayıcı | Varsayılan model                | Metin | Görsel ref       | Video ref        | API anahtarı                             |
| --------- | ------------------------------- | ----- | ---------------- | ---------------- | ---------------------------------------- |
| Alibaba   | `wan2.6-t2v`                    | Evet  | Evet (uzak URL)  | Evet (uzak URL)  | `MODELSTUDIO_API_KEY`                    |
| BytePlus  | `seedance-1-0-lite-t2v-250428`  | Evet  | 1 görsel         | Hayır            | `BYTEPLUS_API_KEY`                       |
| ComfyUI   | `workflow`                      | Evet  | 1 görsel         | Hayır            | `COMFY_API_KEY` veya `COMFY_CLOUD_API_KEY` |
| fal       | `fal-ai/minimax/video-01-live`  | Evet  | 1 görsel         | Hayır            | `FAL_KEY`                                |
| Google    | `veo-3.1-fast-generate-preview` | Evet  | 1 görsel         | 1 video          | `GEMINI_API_KEY`                         |
| MiniMax   | `MiniMax-Hailuo-2.3`            | Evet  | 1 görsel         | Hayır            | `MINIMAX_API_KEY`                        |
| OpenAI    | `sora-2`                        | Evet  | 1 görsel         | 1 video          | `OPENAI_API_KEY`                         |
| Qwen      | `wan2.6-t2v`                    | Evet  | Evet (uzak URL)  | Evet (uzak URL)  | `QWEN_API_KEY`                           |
| Runway    | `gen4.5`                        | Evet  | 1 görsel         | 1 video          | `RUNWAYML_API_SECRET`                    |
| Together  | `Wan-AI/Wan2.2-T2V-A14B`        | Evet  | 1 görsel         | Hayır            | `TOGETHER_API_KEY`                       |
| Vydra     | `veo3`                          | Evet  | 1 görsel (`kling`) | Hayır          | `VYDRA_API_KEY`                          |
| xAI       | `grok-imagine-video`            | Evet  | 1 görsel         | 1 video          | `XAI_API_KEY`                            |

Bazı sağlayıcılar ek veya alternatif API anahtarı ortam değişkenlerini kabul eder. Ayrıntılar için ilgili [sağlayıcı sayfalarına](#related) bakın.

Çalışma zamanında kullanılabilir sağlayıcıları ve modelleri incelemek için `video_generate action=list` çalıştırın.

## Araç parametreleri

### Zorunlu

| Parametre | Tür    | Açıklama                                                                  |
| --------- | ------ | ------------------------------------------------------------------------- |
| `prompt`  | string | Oluşturulacak videonun metin açıklaması (`action: "generate"` için zorunlu) |

### İçerik girdileri

| Parametre | Tür      | Açıklama                            |
| --------- | -------- | ----------------------------------- |
| `image`   | string   | Tek referans görseli (yol veya URL) |
| `images`  | string[] | Birden çok referans görsel (en fazla 5) |
| `video`   | string   | Tek referans videosu (yol veya URL) |
| `videos`  | string[] | Birden çok referans video (en fazla 4) |

### Stil denetimleri

| Parametre        | Tür     | Açıklama                                                               |
| ---------------- | ------- | ---------------------------------------------------------------------- |
| `aspectRatio`    | string  | `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` |
| `resolution`     | string  | `480P`, `720P` veya `1080P`                                            |
| `durationSeconds`| number  | Saniye cinsinden hedef süre (sağlayıcının desteklediği en yakın değere yuvarlanır) |
| `size`           | string  | Sağlayıcı destekliyorsa boyut ipucu                                    |
| `audio`          | boolean | Destekleniyorsa üretilmiş sesi etkinleştirir                           |
| `watermark`      | boolean | Destekleniyorsa sağlayıcı filigranını açıp kapatır                     |

### Gelişmiş

| Parametre | Tür    | Açıklama                                              |
| --------- | ------ | ----------------------------------------------------- |
| `action`  | string | `"generate"` (varsayılan), `"status"` veya `"list"`   |
| `model`   | string | Sağlayıcı/model geçersiz kılması (ör. `runway/gen4.5`) |
| `filename`| string | Çıktı dosya adı ipucu                                 |

Tüm sağlayıcılar tüm parametreleri desteklemez. Desteklenmeyen geçersiz kılmalar en iyi çaba esasına göre yok sayılır ve araç sonucunda uyarı olarak bildirilir. Sert yetenek sınırları (örneğin çok fazla referans girdisi) gönderimden önce başarısız olur.

## Eylemler

- **generate** (varsayılan) -- verilen prompt ve isteğe bağlı referans girdilerinden bir video oluşturur.
- **status** -- yeni üretim başlatmadan geçerli oturum için devam eden video görevinin durumunu kontrol eder.
- **list** -- kullanılabilir sağlayıcıları, modelleri ve bunların yeteneklerini gösterir.

## Model seçimi

Video oluştururken OpenClaw modeli şu sırayla çözer:

1. **`model` araç parametresi** -- ajan çağrıda bir model belirtirse.
2. **`videoGenerationModel.primary`** -- yapılandırmadan.
3. **`videoGenerationModel.fallbacks`** -- sırayla denenir.
4. **Otomatik algılama** -- geçerli kimlik doğrulamaya sahip sağlayıcıları kullanır; önce geçerli varsayılan sağlayıcıdan, sonra kalan sağlayıcılardan alfabetik sırayla başlar.

Bir sağlayıcı başarısız olursa sonraki aday otomatik olarak denenir. Tüm adaylar başarısız olursa hata, her denemeden ayrıntılar içerir.

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "google/veo-3.1-fast-generate-preview",
        fallbacks: ["runway/gen4.5", "qwen/wan2.6-t2v"],
      },
    },
  },
}
```

## Sağlayıcı notları

| Sağlayıcı | Notlar                                                                                                                                    |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Alibaba   | DashScope/Model Studio eşzamansız uç noktasını kullanır. Referans görseller ve videolar uzak `http(s)` URL'leri olmalıdır.             |
| BytePlus  | Yalnızca tek görsel referansı.                                                                                                            |
| ComfyUI   | İş akışı odaklı yerel veya bulut yürütme. Yapılandırılmış grafik üzerinden metinden videoya ve görselden videoya desteği sunar.        |
| fal       | Uzun süren işler için kuyruk destekli akış kullanır. Yalnızca tek görsel referansı.                                                      |
| Google    | Gemini/Veo kullanır. Bir görsel veya bir video referansını destekler.                                                                     |
| MiniMax   | Yalnızca tek görsel referansı.                                                                                                            |
| OpenAI    | Yalnızca `size` geçersiz kılması iletilir. Diğer stil geçersiz kılmaları (`aspectRatio`, `resolution`, `audio`, `watermark`) uyarıyla yok sayılır. |
| Qwen      | Alibaba ile aynı DashScope arka ucunu kullanır. Referans girdileri uzak `http(s)` URL'leri olmalıdır; yerel dosyalar en baştan reddedilir. |
| Runway    | Data URI'ler üzerinden yerel dosyaları destekler. Videodan videoya için `runway/gen4_aleph` gerekir. Yalnızca metin çalıştırmalarında `16:9` ve `9:16` en-boy oranları sunulur. |
| Together  | Yalnızca tek görsel referansı.                                                                                                            |
| Vydra     | Kimlik doğrulamasını düşüren yönlendirmeleri önlemek için doğrudan `https://www.vydra.ai/api/v1` kullanır. `veo3` paketli olarak yalnızca metinden videoya gelir; `kling` uzak bir görsel URL'si gerektirir. |
| xAI       | Metinden videoya, görselden videoya ve uzak video düzenleme/uzatma akışlarını destekler.                                                 |

## Yapılandırma

Varsayılan video üretim modelini OpenClaw yapılandırmanızda ayarlayın:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "qwen/wan2.6-t2v",
        fallbacks: ["qwen/wan2.6-r2v-flash"],
      },
    },
  },
}
```

Veya CLI üzerinden:

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "qwen/wan2.6-t2v"
```

## İlgili

- [Araçlara Genel Bakış](/tr/tools)
- [Arka Plan Görevleri](/tr/automation/tasks) -- eşzamansız video üretimi için görev izleme
- [Alibaba Model Studio](/providers/alibaba)
- [BytePlus](/providers/byteplus)
- [ComfyUI](/providers/comfy)
- [fal](/providers/fal)
- [Google (Gemini)](/tr/providers/google)
- [MiniMax](/tr/providers/minimax)
- [OpenAI](/tr/providers/openai)
- [Qwen](/tr/providers/qwen)
- [Runway](/providers/runway)
- [Together AI](/tr/providers/together)
- [Vydra](/providers/vydra)
- [xAI](/tr/providers/xai)
- [Yapılandırma Başvurusu](/tr/gateway/configuration-reference#agent-defaults)
- [Modeller](/tr/concepts/models)
