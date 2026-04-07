---
read_when:
    - Agent aracılığıyla müzik veya ses üretirken
    - Müzik üretimi sağlayıcılarını ve modellerini yapılandırırken
    - '`music_generate` araç parametrelerini anlamanız gerektiğinde'
summary: Workflow destekli plugin'ler dahil olmak üzere paylaşılan sağlayıcılarla müzik üretin
title: Müzik Üretimi
x-i18n:
    generated_at: "2026-04-07T08:50:46Z"
    model: gpt-5.4
    provider: openai
    source_hash: ce8da8dfc188efe8593ca5cbec0927dd1d18d2861a1a828df89c8541ccf1cb25
    source_path: tools/music-generation.md
    workflow: 15
---

# Müzik Üretimi

`music_generate` aracı, agent'ın Google,
MiniMax ve workflow ile yapılandırılmış ComfyUI gibi yapılandırılmış sağlayıcılar aracılığıyla
paylaşılan müzik üretimi yeteneğini kullanarak müzik veya ses oluşturmasına olanak tanır.

Paylaşılan sağlayıcı destekli agent oturumları için OpenClaw, müzik üretimini bir
arka plan görevi olarak başlatır, bunu görev ledger'ında izler, ardından parça hazır olduğunda
agent'ı yeniden uyandırır; böylece agent tamamlanan sesi özgün
kanala geri gönderebilir.

<Note>
Yerleşik paylaşılan araç yalnızca en az bir müzik üretimi sağlayıcısı kullanılabilir olduğunda görünür. Agent araçlarınızda `music_generate` görünmüyorsa, `agents.defaults.musicGenerationModel` yapılandırın veya bir sağlayıcı API anahtarı ayarlayın.
</Note>

## Hızlı başlangıç

### Paylaşılan sağlayıcı destekli üretim

1. En az bir sağlayıcı için bir API anahtarı ayarlayın; örneğin `GEMINI_API_KEY` veya
   `MINIMAX_API_KEY`.
2. İsteğe bağlı olarak tercih ettiğiniz modeli ayarlayın:

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

3. Agent'a şunu söyleyin: _"Neon bir şehirde gece sürüşü hakkında enerjik bir synthpop parçası üret."_

Agent `music_generate` aracını otomatik olarak çağırır. Araç allow-list ayarlaması gerekmez.

Oturum destekli agent çalıştırması olmayan doğrudan eşzamanlı bağlamlar için yerleşik
araç yine satır içi üretime geri döner ve araç sonucunda nihai medya yolunu döndürür.

Örnek prompt'lar:

```text
Vokalsiz, yumuşak yaylılarla sinematik bir piyano parçası üret.
```

```text
Gün doğumunda bir roket fırlatmak hakkında enerjik bir chiptune döngüsü üret.
```

### Workflow odaklı Comfy üretimi

Paketlenmiş `comfy` plugin'i, müzik üretimi sağlayıcı kayıt sistemi üzerinden
paylaşılan `music_generate` aracına bağlanır.

1. `models.providers.comfy.music` bölümünü bir workflow JSON'u ve
   prompt/çıktı düğümleriyle yapılandırın.
2. Comfy Cloud kullanıyorsanız, `COMFY_API_KEY` veya `COMFY_CLOUD_API_KEY` ayarlayın.
3. Agent'tan müzik isteyin veya aracı doğrudan çağırın.

Örnek:

```text
/tool music_generate prompt="Yumuşak teyp dokusuna sahip sıcak ambient synth döngüsü"
```

## Paylaşılan paketlenmiş sağlayıcı desteği

| Sağlayıcı | Varsayılan model       | Referans girdileri | Desteklenen kontroller                                  | API anahtarı                           |
| --------- | ---------------------- | ------------------ | ------------------------------------------------------- | -------------------------------------- |
| ComfyUI   | `workflow`             | En fazla 1 görüntü | Workflow tanımlı müzik veya ses                         | `COMFY_API_KEY`, `COMFY_CLOUD_API_KEY` |
| Google    | `lyria-3-clip-preview` | En fazla 10 görüntü| `lyrics`, `instrumental`, `format`                      | `GEMINI_API_KEY`, `GOOGLE_API_KEY`     |
| MiniMax   | `music-2.5+`           | Yok                | `lyrics`, `instrumental`, `durationSeconds`, `format=mp3` | `MINIMAX_API_KEY`                    |

### Bildirilmiş yetenek matrisi

Bu, `music_generate`, sözleşme testleri
ve paylaşılan canlı tarama tarafından kullanılan açık mod sözleşmesidir.

| Sağlayıcı | `generate` | `edit` | Düzenleme sınırı | Paylaşılan canlı lane'ler                                                    |
| --------- | ---------- | ------ | ---------------- | ----------------------------------------------------------------------------- |
| ComfyUI   | Yes        | Yes    | 1 görüntü        | Paylaşılan taramada yok; `extensions/comfy/comfy.live.test.ts` ile kapsanır   |
| Google    | Yes        | Yes    | 10 görüntü       | `generate`, `edit`                                                            |
| MiniMax   | Yes        | No     | None             | `generate`                                                                    |

Çalışma zamanında kullanılabilir paylaşılan sağlayıcıları ve modelleri incelemek için
`action: "list"` kullanın:

```text
/tool music_generate action=list
```

Etkin oturum destekli müzik görevini incelemek için
`action: "status"` kullanın:

```text
/tool music_generate action=status
```

Doğrudan üretim örneği:

```text
/tool music_generate prompt="Vinil dokusu ve hafif yağmurla rüya gibi lo-fi hip hop" instrumental=true
```

## Yerleşik araç parametreleri

| Parametre         | Tür      | Açıklama                                                                                         |
| ----------------- | -------- | ------------------------------------------------------------------------------------------------ |
| `prompt`          | string   | Müzik üretimi prompt'u (`action: "generate"` için gereklidir)                                   |
| `action`          | string   | `"generate"` (varsayılan), geçerli oturum görevi için `"status"` veya sağlayıcıları incelemek için `"list"` |
| `model`           | string   | Sağlayıcı/model geçersiz kılması, örn. `google/lyria-3-pro-preview` veya `comfy/workflow`       |
| `lyrics`          | string   | Sağlayıcı açık şarkı sözü girdisini desteklediğinde isteğe bağlı şarkı sözleri                  |
| `instrumental`    | boolean  | Sağlayıcı desteklediğinde yalnızca enstrümantal çıktı isteyin                                   |
| `image`           | string   | Tek bir referans görüntü yolu veya URL'si                                                       |
| `images`          | string[] | Birden çok referans görüntü (en fazla 10)                                                       |
| `durationSeconds` | number   | Sağlayıcı süre ipuçlarını desteklediğinde hedef süre saniye cinsinden                           |
| `format`          | string   | Sağlayıcı desteklediğinde çıktı biçimi ipucu (`mp3` veya `wav`)                                 |
| `filename`        | string   | Çıktı dosya adı ipucu                                                                            |

Tüm sağlayıcılar tüm parametreleri desteklemez. OpenClaw yine de gönderimden önce
girdi sayıları gibi katı sınırları doğrular. Bir sağlayıcı süreyi destekliyor ama
istenen değerden daha kısa bir maksimum kullanıyorsa, OpenClaw bunu otomatik olarak
desteklenen en yakın süreye sınırlar. Gerçekten desteklenmeyen isteğe bağlı ipuçları ise
seçilen sağlayıcı veya model bunları karşılayamadığında bir uyarıyla yok sayılır.

Araç sonuçları uygulanan ayarları bildirir. OpenClaw sağlayıcı fallback'i sırasında süreyi sınırlandırdığında, döndürülen `durationSeconds` gönderilen değeri yansıtır ve `details.normalization.durationSeconds` istekten uygulanan değere eşlemeyi gösterir.

## Paylaşılan sağlayıcı destekli yol için asenkron davranış

- Oturum destekli agent çalıştırmaları: `music_generate` bir arka plan görevi oluşturur, hemen bir başlatıldı/görev yanıtı döndürür ve tamamlanan parçayı daha sonra takip eden bir agent mesajında gönderir.
- Yinelenenleri önleme: bu arka plan görevi hâlâ `queued` veya `running` durumundayken, aynı oturumdaki sonraki `music_generate` çağrıları başka bir üretim başlatmak yerine görev durumunu döndürür.
- Durum sorgulama: yeni bir üretim başlatmadan etkin oturum destekli müzik görevini incelemek için `action: "status"` kullanın.
- Görev izleme: üretim için sıraya alınmış, çalışan ve son duruma ulaşmış görevleri incelemek üzere `openclaw tasks list` veya `openclaw tasks show <taskId>` kullanın.
- Tamamlama uyandırması: OpenClaw, modelin kullanıcıya dönük takibi kendisinin yazabilmesi için aynı oturuma dahili bir tamamlama olayı enjekte eder.
- Prompt ipucu: aynı oturumdaki sonraki kullanıcı/manuel turlar, bir müzik görevi zaten çalışıyorsa küçük bir çalışma zamanı ipucu alır; böylece model körlemesine yeniden `music_generate` çağırmaz.
- Oturumsuz fallback: gerçek bir agent oturumu olmayan doğrudan/yerel bağlamlar yine satır içi çalışır ve nihai ses sonucunu aynı turda döndürür.

### Görev yaşam döngüsü

Her `music_generate` isteği dört durumdan geçer:

1. **queued** -- görev oluşturuldu, sağlayıcının bunu kabul etmesi bekleniyor.
2. **running** -- sağlayıcı işliyor (genellikle sağlayıcıya ve süreye bağlı olarak 30 saniye ile 3 dakika arası).
3. **succeeded** -- parça hazır; agent uyanır ve bunu konuşmaya gönderir.
4. **failed** -- sağlayıcı hatası veya zaman aşımı; agent hata ayrıntılarıyla uyanır.

CLI içinden durumu kontrol edin:

```bash
openclaw tasks list
openclaw tasks show <taskId>
openclaw tasks cancel <taskId>
```

Yinelenenleri önleme: geçerli oturum için bir müzik görevi zaten `queued` veya `running` durumundaysa, `music_generate` yeni bir görev başlatmak yerine mevcut görev durumunu döndürür. Yeni bir üretimi tetiklemeden açıkça kontrol etmek için `action: "status"` kullanın.

## Yapılandırma

### Model seçimi

```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "google/lyria-3-clip-preview",
        fallbacks: ["minimax/music-2.5+"],
      },
    },
  },
}
```

### Sağlayıcı seçim sırası

Müzik üretirken OpenClaw sağlayıcıları şu sırayla dener:

1. Agent bir değer belirtirse araç çağrısından gelen `model` parametresi
2. Config'den gelen `musicGenerationModel.primary`
3. Sırayla `musicGenerationModel.fallbacks`
4. Yalnızca auth destekli sağlayıcı varsayılanlarını kullanarak otomatik algılama:
   - önce geçerli varsayılan sağlayıcı
   - ardından sağlayıcı kimliği sırasına göre kayıtlı kalan müzik üretimi sağlayıcıları

Bir sağlayıcı başarısız olursa, sonraki aday otomatik olarak denenir. Hepsi başarısız olursa,
hata her denemeden ayrıntıları içerir.

Müzik üretiminin yalnızca açık `model`, `primary` ve `fallbacks`
girdilerini kullanmasını istiyorsanız `agents.defaults.mediaGenerationAutoProviderFallback: false` ayarlayın.

## Sağlayıcı notları

- Google, Lyria 3 batch generation kullanır. Mevcut paketlenmiş akış;
  prompt, isteğe bağlı şarkı sözü metni ve isteğe bağlı referans görüntüleri destekler.
- MiniMax, batch `music_generation` uç noktasını kullanır. Mevcut paketlenmiş akış;
  prompt, isteğe bağlı şarkı sözleri, enstrümantal mod, süre yönlendirme ve
  mp3 çıktısını destekler.
- ComfyUI desteği workflow odaklıdır ve yapılandırılmış grafik ile
  prompt/çıktı alanları için düğüm eşlemesine bağlıdır.

## Sağlayıcı yetenek modları

Paylaşılan müzik üretimi sözleşmesi artık açık mod bildirimlerini destekler:

- yalnızca prompt ile üretim için `generate`
- istek bir veya daha fazla referans görüntü içerdiğinde `edit`

Yeni sağlayıcı uygulamaları açık mod bloklarını tercih etmelidir:

```typescript
capabilities: {
  generate: {
    maxTracks: 1,
    supportsLyrics: true,
    supportsFormat: true,
  },
  edit: {
    enabled: true,
    maxTracks: 1,
    maxInputImages: 1,
    supportsFormat: true,
  },
}
```

`maxInputImages`, `supportsLyrics` ve
`supportsFormat` gibi eski düz alanlar, düzenleme desteğini duyurmak için yeterli değildir. Sağlayıcılar,
canlı testlerin, sözleşme testlerinin ve
paylaşılan `music_generate` aracının mod desteğini deterministik biçimde doğrulayabilmesi için
`generate` ve `edit` modlarını açıkça bildirmelidir.

## Doğru yolu seçme

- Model seçimi, sağlayıcı failover'ı ve yerleşik asenkron görev/durum akışını istiyorsanız paylaşılan sağlayıcı destekli yolu kullanın.
- Özel bir workflow grafiğine veya paylaşılan paketlenmiş müzik yeteneğinin parçası olmayan bir sağlayıcıya ihtiyacınız varsa ComfyUI gibi bir plugin yolunu kullanın.
- ComfyUI'ya özgü davranışı hata ayıklıyorsanız [ComfyUI](/tr/providers/comfy) ile başlayın. Paylaşılan sağlayıcı davranışını hata ayıklıyorsanız [Google (Gemini)](/tr/providers/google) veya [MiniMax](/tr/providers/minimax) ile başlayın.

## Canlı testler

Paylaşılan paketlenmiş sağlayıcılar için isteğe bağlı canlı kapsam:

```bash
OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts
```

Depo sarmalayıcısı:

```bash
pnpm test:live:media music
```

Bu canlı dosya, eksik sağlayıcı env değişkenlerini `~/.profile` içinden yükler,
varsayılan olarak saklanan auth profilleri yerine canlı/env API anahtarlarını tercih eder
ve sağlayıcı düzenleme modunu etkinleştirdiğinde hem
`generate` hem de bildirilen `edit` kapsamını çalıştırır.

Bugün bunun anlamı şudur:

- `google`: `generate` artı `edit`
- `minimax`: yalnızca `generate`
- `comfy`: ayrı Comfy canlı kapsamı, paylaşılan sağlayıcı taraması değil

Paketlenmiş ComfyUI müzik yolu için isteğe bağlı canlı kapsam:

```bash
OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts
```

Comfy canlı dosyası, bu
bölümler yapılandırıldığında comfy görüntü ve video workflow'larını da kapsar.

## İlgili

- [Arka Plan Görevleri](/tr/automation/tasks) - ayrık `music_generate` çalıştırmaları için görev izleme
- [Configuration Reference](/tr/gateway/configuration-reference#agent-defaults) - `musicGenerationModel` config'i
- [ComfyUI](/tr/providers/comfy)
- [Google (Gemini)](/tr/providers/google)
- [MiniMax](/tr/providers/minimax)
- [Models](/tr/concepts/models) - model yapılandırması ve failover
- [Tools Overview](/tr/tools)
