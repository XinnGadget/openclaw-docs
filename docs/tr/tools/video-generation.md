---
read_when:
    - Ajan üzerinden video oluşturma
    - Video oluşturma provider'larını ve modellerini yapılandırma
    - '`video_generate` tool parametrelerini anlama'
summary: 12 provider backend kullanarak metinden, görüntülerden veya mevcut videolardan video oluşturun
title: Video Oluşturma
x-i18n:
    generated_at: "2026-04-07T08:50:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: bf1224c59a5f1217f56cf2001870aca710a09268677dcd12aad2efbe476e47b7
    source_path: tools/video-generation.md
    workflow: 15
---

# Video Oluşturma

OpenClaw ajanları, metin prompt'larından, referans görüntülerden veya mevcut videolardan video oluşturabilir. On iki provider backend desteklenir ve her biri farklı model seçenekleri, giriş modları ve özellik kümeleri sunar. Ajan, yapılandırmanıza ve kullanılabilir API anahtarlarına göre doğru provider'ı otomatik olarak seçer.

<Note>
`video_generate` tool'u yalnızca en az bir video oluşturma provider'ı kullanılabilir olduğunda görünür. Ajan tool'larınızda bunu görmüyorsanız bir provider API anahtarı ayarlayın veya `agents.defaults.videoGenerationModel` yapılandırın.
</Note>

OpenClaw, video oluşturmayı üç çalışma zamanı modu olarak ele alır:

- referans medya içermeyen metinden videoya istekler için `generate`
- istek bir veya daha fazla referans görüntü içerdiğinde `imageToVideo`
- istek bir veya daha fazla referans video içerdiğinde `videoToVideo`

Provider'lar bu modların herhangi bir alt kümesini destekleyebilir. Tool, etkin
modu gönderimden önce doğrular ve desteklenen modları `action=list` içinde bildirir.

## Hızlı başlangıç

1. Desteklenen herhangi bir provider için bir API anahtarı ayarlayın:

```bash
export GEMINI_API_KEY="your-key"
```

2. İsteğe bağlı olarak varsayılan bir modeli sabitleyin:

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "google/veo-3.1-fast-generate-preview"
```

3. Ajana istekte bulunun:

> Gün batımında sörf yapan dost canlısı bir ıstakozun 5 saniyelik sinematik bir videosunu oluştur.

Ajan `video_generate` tool'unu otomatik olarak çağırır. Tool allowlist yapılandırması gerekmez.

## Video oluşturduğunuzda ne olur

Video oluşturma eşzamansızdır. Ajan bir oturumda `video_generate` çağırdığında:

1. OpenClaw isteği provider'a gönderir ve hemen bir görev kimliği döndürür.
2. Provider işi arka planda işler (genellikle provider'a ve çözünürlüğe bağlı olarak 30 saniye ile 5 dakika arasında).
3. Video hazır olduğunda OpenClaw aynı oturumu bir iç tamamlama olayıyla uyandırır.
4. Ajan tamamlanan videoyu özgün konuşmaya geri gönderir.

Bir iş yürürlükteyken aynı oturumda yinelenen `video_generate` çağrıları yeni bir oluşturma başlatmak yerine geçerli görev durumunu döndürür. CLI üzerinden ilerlemeyi kontrol etmek için `openclaw tasks list` veya `openclaw tasks show <taskId>` kullanın.

Oturum destekli ajan çalıştırmalarının dışında (örneğin doğrudan tool çağrıları), tool satır içi oluşturmaya geri döner ve aynı turda son medya yolunu döndürür.

### Görev yaşam döngüsü

Her `video_generate` isteği dört durumdan geçer:

1. **queued** -- görev oluşturuldu, provider'ın kabul etmesi bekleniyor.
2. **running** -- provider işliyor (genellikle provider'a ve çözünürlüğe bağlı olarak 30 saniye ile 5 dakika arasında).
3. **succeeded** -- video hazır; ajan uyanır ve videoyu konuşmaya gönderir.
4. **failed** -- provider hatası veya zaman aşımı; ajan hata ayrıntılarıyla uyanır.

Durumu CLI'dan kontrol edin:

```bash
openclaw tasks list
openclaw tasks show <taskId>
openclaw tasks cancel <taskId>
```

Yinelenmeyi önleme: geçerli oturum için bir video görevi zaten `queued` veya `running` durumundaysa `video_generate`, yeni bir görev başlatmak yerine mevcut görev durumunu döndürür. Yeni oluşturmayı tetiklemeden açıkça denetlemek için `action: "status"` kullanın.

## Desteklenen provider'lar

| Provider | Varsayılan model               | Metin | Görüntü ref        | Video ref        | API anahtarı                             |
| -------- | ------------------------------ | ----- | ------------------ | ---------------- | ---------------------------------------- |
| Alibaba  | `wan2.6-t2v`                   | Evet  | Evet (uzak URL)    | Evet (uzak URL)  | `MODELSTUDIO_API_KEY`                    |
| BytePlus | `seedance-1-0-lite-t2v-250428` | Evet  | 1 görüntü          | Hayır            | `BYTEPLUS_API_KEY`                       |
| ComfyUI  | `workflow`                     | Evet  | 1 görüntü          | Hayır            | `COMFY_API_KEY` veya `COMFY_CLOUD_API_KEY` |
| fal      | `fal-ai/minimax/video-01-live` | Evet  | 1 görüntü          | Hayır            | `FAL_KEY`                                |
| Google   | `veo-3.1-fast-generate-preview`| Evet  | 1 görüntü          | 1 video          | `GEMINI_API_KEY`                         |
| MiniMax  | `MiniMax-Hailuo-2.3`           | Evet  | 1 görüntü          | Hayır            | `MINIMAX_API_KEY`                        |
| OpenAI   | `sora-2`                       | Evet  | 1 görüntü          | 1 video          | `OPENAI_API_KEY`                         |
| Qwen     | `wan2.6-t2v`                   | Evet  | Evet (uzak URL)    | Evet (uzak URL)  | `QWEN_API_KEY`                           |
| Runway   | `gen4.5`                       | Evet  | 1 görüntü          | 1 video          | `RUNWAYML_API_SECRET`                    |
| Together | `Wan-AI/Wan2.2-T2V-A14B`       | Evet  | 1 görüntü          | Hayır            | `TOGETHER_API_KEY`                       |
| Vydra    | `veo3`                         | Evet  | 1 görüntü (`kling`)| Hayır            | `VYDRA_API_KEY`                          |
| xAI      | `grok-imagine-video`           | Evet  | 1 görüntü          | 1 video          | `XAI_API_KEY`                            |

Bazı provider'lar ek veya alternatif API anahtarı env değişkenlerini kabul eder. Ayrıntılar için ilgili [provider sayfalarına](#related) bakın.

Çalışma zamanında kullanılabilir provider'ları, modelleri ve
çalışma zamanı modlarını incelemek için `video_generate action=list` çalıştırın.

### Bildirilmiş yetenek matrisi

Bu, `video_generate`, sözleşme testleri
ve paylaşılan canlı tarama tarafından kullanılan açık mod sözleşmesidir.

| Provider | `generate` | `imageToVideo` | `videoToVideo` | Bugünkü paylaşılan canlı yollar                                                                                                          |
| -------- | ---------- | -------------- | -------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Alibaba  | Evet       | Evet           | Evet           | `generate`, `imageToVideo`; `videoToVideo` atlanır çünkü bu provider uzak `http(s)` video URL'leri gerektirir                           |
| BytePlus | Evet       | Evet           | Hayır          | `generate`, `imageToVideo`                                                                                                               |
| ComfyUI  | Evet       | Evet           | Hayır          | Paylaşılan taramada yok; iş akışına özgü kapsam Comfy testleriyle birlikte bulunur                                                      |
| fal      | Evet       | Evet           | Hayır          | `generate`, `imageToVideo`                                                                                                               |
| Google   | Evet       | Evet           | Evet           | `generate`, `imageToVideo`; paylaşılan `videoToVideo`, mevcut buffer destekli Gemini/Veo taraması bu girdiyi kabul etmediği için atlanır |
| MiniMax  | Evet       | Evet           | Hayır          | `generate`, `imageToVideo`                                                                                                               |
| OpenAI   | Evet       | Evet           | Evet           | `generate`, `imageToVideo`; paylaşılan `videoToVideo`, bu kuruluş/girdi yolu şu anda provider tarafında inpaint/remix erişimi gerektirdiği için atlanır |
| Qwen     | Evet       | Evet           | Evet           | `generate`, `imageToVideo`; `videoToVideo` atlanır çünkü bu provider uzak `http(s)` video URL'leri gerektirir                           |
| Runway   | Evet       | Evet           | Evet           | `generate`, `imageToVideo`; `videoToVideo` yalnızca seçilen model `runway/gen4_aleph` olduğunda çalışır                                |
| Together | Evet       | Evet           | Hayır          | `generate`, `imageToVideo`                                                                                                               |
| Vydra    | Evet       | Evet           | Hayır          | `generate`; paylaşılan `imageToVideo`, paketlenmiş `veo3` yalnızca metin olduğu ve paketlenmiş `kling` uzak görüntü URL'si gerektirdiği için atlanır |
| xAI      | Evet       | Evet           | Evet           | `generate`, `imageToVideo`; `videoToVideo` atlanır çünkü bu provider şu anda uzak MP4 URL'si gerektirir                                |

## Tool parametreleri

### Gerekli

| Parametre | Tür    | Açıklama                                                                  |
| --------- | ------ | ------------------------------------------------------------------------- |
| `prompt`  | string | Oluşturulacak videonun metin açıklaması (`action: "generate"` için gereklidir) |

### İçerik girdileri

| Parametre | Tür      | Açıklama                           |
| --------- | -------- | ---------------------------------- |
| `image`   | string   | Tek referans görüntü (yol veya URL) |
| `images`  | string[] | Birden çok referans görüntü (en fazla 5) |
| `video`   | string   | Tek referans video (yol veya URL)  |
| `videos`  | string[] | Birden çok referans video (en fazla 4) |

### Stil denetimleri

| Parametre        | Tür     | Açıklama                                                                |
| ---------------- | ------- | ----------------------------------------------------------------------- |
| `aspectRatio`    | string  | `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` |
| `resolution`     | string  | `480P`, `720P`, `768P` veya `1080P`                                    |
| `durationSeconds`| number  | Hedef süre saniye cinsinden (provider'ın desteklediği en yakın değere yuvarlanır) |
| `size`           | string  | Provider destekliyorsa boyut ipucu                                     |
| `audio`          | boolean | Destekleniyorsa oluşturulan sesi etkinleştirir                         |
| `watermark`      | boolean | Destekleniyorsa provider filigranını açar/kapatır                      |

### Gelişmiş

| Parametre | Tür    | Açıklama                                             |
| --------- | ------ | ---------------------------------------------------- |
| `action`  | string | `"generate"` (varsayılan), `"status"` veya `"list"` |
| `model`   | string | Provider/model geçersiz kılması (ör. `runway/gen4.5`) |
| `filename`| string | Çıktı dosya adı ipucu                                |

Tüm provider'lar tüm parametreleri desteklemez. OpenClaw zaten süreyi en yakın provider destekli değere normalize eder ve ayrıca geri dönüş provider'ı farklı bir denetim yüzeyi sunduğunda boyuttan en-boy oranına gibi çevrilmiş geometri ipuçlarını yeniden eşler. Gerçekten desteklenmeyen geçersiz kılmalar best-effort temelinde yok sayılır ve tool sonucunda uyarı olarak bildirilir. Sert yetenek sınırları (örneğin çok fazla referans girdisi) gönderimden önce başarısız olur.

Tool sonuçları uygulanan ayarları bildirir. OpenClaw, provider geri dönüşü sırasında süreyi veya geometriyi yeniden eşlediğinde döndürülen `durationSeconds`, `size`, `aspectRatio` ve `resolution` değerleri gönderilenleri yansıtır ve `details.normalization`, istenenden uygulanana yapılan çeviriyi yakalar.

Referans girdileri çalışma zamanı modunu da seçer:

- Referans medya yok: `generate`
- Herhangi bir görüntü referansı: `imageToVideo`
- Herhangi bir video referansı: `videoToVideo`

Karışık görüntü ve video referansları kararlı paylaşılan bir yetenek yüzeyi değildir.
İstek başına tek bir referans türünü tercih edin.

## Eylemler

- **generate** (varsayılan) -- verilen prompt ve isteğe bağlı referans girdilerden video oluşturur.
- **status** -- yeni bir oluşturma başlatmadan geçerli oturum için yürürlükteki video görevinin durumunu kontrol eder.
- **list** -- kullanılabilir provider'ları, modelleri ve bunların yeteneklerini gösterir.

## Model seçimi

Video oluşturulurken OpenClaw modeli şu sırayla çözümler:

1. **`model` tool parametresi** -- ajan bunu çağrıda belirtirse.
2. **`videoGenerationModel.primary`** -- yapılandırmadan.
3. **`videoGenerationModel.fallbacks`** -- sırayla denenir.
4. **Otomatik algılama** -- geçerli kimlik doğrulamaya sahip provider'ları kullanır; önce geçerli varsayılan provider, ardından geri kalan provider'lar alfabetik sırayla.

Bir provider başarısız olursa bir sonraki aday otomatik olarak denenir. Tüm adaylar başarısız olursa hata her denemeden ayrıntılar içerir.

Video oluşturmanın yalnızca açık `model`, `primary` ve `fallbacks`
girdilerini kullanmasını istiyorsanız `agents.defaults.mediaGenerationAutoProviderFallback: false` ayarlayın.

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

## Provider notları

| Provider | Notlar                                                                                                                                                     |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Alibaba  | DashScope/Model Studio eşzamansız uç noktasını kullanır. Referans görüntü ve videolar uzak `http(s)` URL'leri olmalıdır.                               |
| BytePlus | Yalnızca tek görüntü referansı.                                                                                                                           |
| ComfyUI  | İş akışı odaklı yerel veya bulut yürütme. Yapılandırılmış grafik üzerinden metinden videoya ve görüntüden videoya desteği sunar.                        |
| fal      | Uzun süren işler için kuyruk destekli akış kullanır. Yalnızca tek görüntü referansı.                                                                      |
| Google   | Gemini/Veo kullanır. Bir görüntü veya bir video referansını destekler.                                                                                    |
| MiniMax  | Yalnızca tek görüntü referansı.                                                                                                                           |
| OpenAI   | Yalnızca `size` geçersiz kılması iletilir. Diğer stil geçersiz kılmaları (`aspectRatio`, `resolution`, `audio`, `watermark`) uyarıyla birlikte yok sayılır. |
| Qwen     | Alibaba ile aynı DashScope backend'ini kullanır. Referans girdileri uzak `http(s)` URL'leri olmalıdır; yerel dosyalar baştan reddedilir.                |
| Runway   | Data URI'leri üzerinden yerel dosyaları destekler. Videodan videoya için `runway/gen4_aleph` gerekir. Yalnızca metin çalıştırmalarında `16:9` ve `9:16` en-boy oranları sunulur. |
| Together | Yalnızca tek görüntü referansı.                                                                                                                           |
| Vydra    | Kimlik doğrulamayı düşüren yönlendirmeleri önlemek için doğrudan `https://www.vydra.ai/api/v1` kullanır. `veo3` paketlenmiş olarak yalnızca metinden videoya sunulur; `kling` uzak görüntü URL'si gerektirir. |
| xAI      | Metinden videoya, görüntüden videoya ve uzak video düzenleme/uzatma akışlarını destekler.                                                                |

## Provider yetenek modları

Paylaşılan video oluşturma sözleşmesi artık provider'ların yalnızca düz toplu sınırlar yerine
moda özgü yetenekler bildirmesine izin verir. Yeni provider
uygulamaları açık mod bloklarını tercih etmelidir:

```typescript
capabilities: {
  generate: {
    maxVideos: 1,
    maxDurationSeconds: 10,
    supportsResolution: true,
  },
  imageToVideo: {
    enabled: true,
    maxVideos: 1,
    maxInputImages: 1,
    maxDurationSeconds: 5,
  },
  videoToVideo: {
    enabled: true,
    maxVideos: 1,
    maxInputVideos: 1,
    maxDurationSeconds: 5,
  },
}
```

`maxInputImages` ve `maxInputVideos` gibi düz toplu alanlar,
dönüşüm modu desteğini bildirmek için yeterli değildir. Provider'lar
`generate`, `imageToVideo` ve `videoToVideo` modlarını açıkça bildirmelidir; böylece canlı testler,
sözleşme testleri ve paylaşılan `video_generate` tool'u mod desteğini
deterministik olarak doğrulayabilir.

## Canlı testler

Paylaşılan paketlenmiş provider'lar için isteğe bağlı canlı kapsam:

```bash
OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts
```

Repo wrapper:

```bash
pnpm test:live:media video
```

Bu canlı dosya, eksik provider env değişkenlerini `~/.profile` içinden yükler,
varsayılan olarak saklanan auth profillerinden önce canlı/env API anahtarlarını tercih eder ve
yerel medyayla güvenle çalıştırabildiği bildirilen modları çalıştırır:

- taramadaki her provider için `generate`
- `capabilities.imageToVideo.enabled` olduğunda `imageToVideo`
- `capabilities.videoToVideo.enabled` olduğunda ve provider/model
  paylaşılan taramada buffer destekli yerel video girdisini kabul ettiğinde `videoToVideo`

Bugün paylaşılan `videoToVideo` canlı yolu şunu kapsar:

- yalnızca `runway/gen4_aleph` seçildiğinde `runway`

## Yapılandırma

Varsayılan video oluşturma modelini OpenClaw yapılandırmanızda ayarlayın:

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

- [Tools Overview](/tr/tools)
- [Background Tasks](/tr/automation/tasks) -- eşzamansız video oluşturma için görev takibi
- [Alibaba Model Studio](/tr/providers/alibaba)
- [BytePlus](/tr/concepts/model-providers#byteplus-international)
- [ComfyUI](/tr/providers/comfy)
- [fal](/tr/providers/fal)
- [Google (Gemini)](/tr/providers/google)
- [MiniMax](/tr/providers/minimax)
- [OpenAI](/tr/providers/openai)
- [Qwen](/tr/providers/qwen)
- [Runway](/tr/providers/runway)
- [Together AI](/tr/providers/together)
- [Vydra](/tr/providers/vydra)
- [xAI](/tr/providers/xai)
- [Configuration Reference](/tr/gateway/configuration-reference#agent-defaults)
- [Models](/tr/concepts/models)
