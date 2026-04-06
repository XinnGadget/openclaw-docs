---
read_when:
    - Aracı üzerinden müzik veya ses üretme
    - Müzik üretimi sağlayıcılarını ve modellerini yapılandırma
    - '`music_generate` aracı parametrelerini anlama'
summary: İş akışı destekli eklentiler dahil, paylaşılan sağlayıcılarla müzik üretin
title: Müzik Üretimi
x-i18n:
    generated_at: "2026-04-06T03:13:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: a03de8aa75cfb7248eb0c1d969fb2a6da06117967d097e6f6e95771d0f017ae1
    source_path: tools/music-generation.md
    workflow: 15
---

# Müzik Üretimi

`music_generate` aracı, aracının Google,
MiniMax ve iş akışı yapılandırılmış ComfyUI gibi yapılandırılmış sağlayıcılar aracılığıyla
paylaşılan müzik üretimi yeteneği üzerinden müzik veya ses oluşturmasına olanak tanır.

Paylaşılan sağlayıcı destekli aracı oturumları için OpenClaw, müzik üretimini bir
arka plan görevi olarak başlatır, görev defterinde izler, ardından parça hazır olduğunda
aracıyı yeniden uyandırır; böylece aracı bitmiş sesi
özgün kanala geri gönderebilir.

<Note>
Yerleşik paylaşılan araç yalnızca en az bir müzik üretimi sağlayıcısı mevcut olduğunda görünür. Aracınızın araçlarında `music_generate` görmüyorsanız `agents.defaults.musicGenerationModel` yapılandırın veya bir sağlayıcı API anahtarı ayarlayın.
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

3. Aracıya şunu sorun: _"Neon bir şehirde gece sürüşü hakkında tempolu bir synthpop parçası
   üret."_

Aracı `music_generate` aracını otomatik olarak çağırır. Araç izin listesine ekleme gerekmez.

Oturum destekli aracı çalıştırması olmayan doğrudan eşzamanlı bağlamlarda, yerleşik
araç yine de satır içi üretime geri döner ve araç sonucunda son medya yolunu
döndürür.

Örnek promptlar:

```text
Yumuşak yaylılar içeren ve vokalsiz sinematik bir piyano parçası üret.
```

```text
Gün doğumunda roket fırlatma hakkında enerjik bir chiptune döngüsü üret.
```

### İş akışı odaklı Comfy üretimi

Paketlenmiş `comfy` eklentisi, paylaşılan `music_generate` aracına
müzik üretimi sağlayıcı kaydı üzerinden bağlanır.

1. `models.providers.comfy.music` içinde bir iş akışı JSON'u ve
   prompt/çıktı düğümleri yapılandırın.
2. Comfy Cloud kullanıyorsanız `COMFY_API_KEY` veya `COMFY_CLOUD_API_KEY` ayarlayın.
3. Aracıdan müzik isteyin veya aracı doğrudan çağırın.

Örnek:

```text
/tool music_generate prompt="Yumuşak teyp dokusuna sahip sıcak ambient synth döngüsü"
```

## Paylaşılan paketlenmiş sağlayıcı desteği

| Sağlayıcı | Varsayılan model       | Referans girdileri | Desteklenen denetimler                                  | API anahtarı                           |
| --------- | ---------------------- | ------------------ | ------------------------------------------------------- | -------------------------------------- |
| ComfyUI   | `workflow`             | En fazla 1 görsel  | İş akışı tanımlı müzik veya ses                         | `COMFY_API_KEY`, `COMFY_CLOUD_API_KEY` |
| Google    | `lyria-3-clip-preview` | En fazla 10 görsel | `lyrics`, `instrumental`, `format`                      | `GEMINI_API_KEY`, `GOOGLE_API_KEY`     |
| MiniMax   | `music-2.5+`           | Yok                | `lyrics`, `instrumental`, `durationSeconds`, `format=mp3` | `MINIMAX_API_KEY`                    |

Çalışma zamanında mevcut paylaşılan sağlayıcıları ve modelleri incelemek için
`action: "list"` kullanın:

```text
/tool music_generate action=list
```

Etkin oturum destekli müzik görevini incelemek için `action: "status"` kullanın:

```text
/tool music_generate action=status
```

Doğrudan üretim örneği:

```text
/tool music_generate prompt="Vinil dokusu ve hafif yağmur içeren düşsel lo-fi hip hop" instrumental=true
```

## Yerleşik araç parametreleri

| Parametre         | Tür      | Açıklama                                                                                         |
| ----------------- | -------- | ------------------------------------------------------------------------------------------------ |
| `prompt`          | string   | Müzik üretimi promptu (`action: "generate"` için gereklidir)                                     |
| `action`          | string   | `"generate"` (varsayılan), geçerli oturum görevi için `"status"` veya sağlayıcıları incelemek için `"list"` |
| `model`           | string   | Sağlayıcı/model geçersiz kılması; örn. `google/lyria-3-pro-preview` veya `comfy/workflow`        |
| `lyrics`          | string   | Sağlayıcı açık söz girişi destekliyorsa isteğe bağlı sözler                                     |
| `instrumental`    | boolean  | Sağlayıcı destekliyorsa yalnızca enstrümantal çıktı isteyin                                      |
| `image`           | string   | Tek referans görsel yolu veya URL'si                                                             |
| `images`          | string[] | Birden çok referans görsel (en fazla 10)                                                         |
| `durationSeconds` | number   | Sağlayıcı süre ipuçlarını destekliyorsa saniye cinsinden hedef süre                              |
| `format`          | string   | Sağlayıcı destekliyorsa çıktı biçimi ipucu (`mp3` veya `wav`)                                    |
| `filename`        | string   | Çıktı dosya adı ipucu                                                                             |

Tüm sağlayıcılar tüm parametreleri desteklemez. OpenClaw yine de gönderimden önce
girdi sayısı gibi katı sınırları doğrular, ancak desteklenmeyen isteğe bağlı ipuçları
seçilen sağlayıcı veya model bunları yerine getiremiyorsa bir uyarıyla yok sayılır.

## Paylaşılan sağlayıcı destekli yol için eşzamansız davranış

- Oturum destekli aracı çalıştırmaları: `music_generate` bir arka plan görevi oluşturur, hemen başlatıldı/görev yanıtı döndürür ve tamamlanan parçayı daha sonra takip eden bir aracı mesajında gönderir.
- Yinelenmeyi önleme: bu arka plan görevi hâlâ `queued` veya `running` durumundayken aynı oturumdaki sonraki `music_generate` çağrıları başka bir üretim başlatmak yerine görev durumunu döndürür.
- Durum sorgulama: yeni bir görev başlatmadan etkin oturum destekli müzik görevini incelemek için `action: "status"` kullanın.
- Görev izleme: üretimin kuyrukta, çalışıyor veya sonlanmış durumunu incelemek için `openclaw tasks list` veya `openclaw tasks show <taskId>` kullanın.
- Tamamlama uyandırması: OpenClaw aynı oturuma dahili bir tamamlama olayı geri enjekte eder; böylece model kullanıcıya dönük takibi kendisi yazabilir.
- Prompt ipucu: aynı oturumdaki sonraki kullanıcı/el ile dönüşler, bir müzik görevi zaten sürüyorsa küçük bir çalışma zamanı ipucu alır; böylece model körü körüne yeniden `music_generate` çağırmaz.
- Oturumsuz geri dönüş: gerçek bir aracı oturumu olmayan doğrudan/yerel bağlamlar yine satır içinde çalışır ve son ses sonucunu aynı dönüşte döndürür.

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

Müzik üretilirken OpenClaw sağlayıcıları şu sırada dener:

1. Aracı bir model belirtirse, araç çağrısından gelen `model` parametresi
2. Yapılandırmadan gelen `musicGenerationModel.primary`
3. Sırayla `musicGenerationModel.fallbacks`
4. Yalnızca kimlik doğrulama destekli sağlayıcı varsayılanlarını kullanan otomatik algılama:
   - önce geçerli varsayılan sağlayıcı
   - ardından sağlayıcı kimliği sırasına göre kalan kayıtlı müzik üretimi sağlayıcıları

Bir sağlayıcı başarısız olursa sonraki aday otomatik olarak denenir. Hepsi başarısız olursa
hata her denemenin ayrıntılarını içerir.

## Sağlayıcı notları

- Google, Lyria 3 toplu üretimi kullanır. Geçerli paketlenmiş akış
  prompt, isteğe bağlı söz metni ve isteğe bağlı referans görselleri destekler.
- MiniMax, toplu `music_generation` uç noktasını kullanır. Geçerli paketlenmiş akış
  prompt, isteğe bağlı sözler, enstrümantal kip, süre yönlendirme ve
  mp3 çıktısını destekler.
- ComfyUI desteği iş akışı odaklıdır ve yapılandırılmış grafik ile
  prompt/çıktı alanları için düğüm eşlemesine bağlıdır.

## Doğru yolu seçme

- Model seçimi, sağlayıcı geri dönüşü ve yerleşik eşzamansız görev/durum akışını istediğinizde paylaşılan sağlayıcı destekli yolu kullanın.
- Özel bir iş akışı grafiğine veya paylaşılan paketlenmiş müzik yeteneğinin parçası olmayan bir sağlayıcıya ihtiyacınız olduğunda ComfyUI gibi bir eklenti yolunu kullanın.
- ComfyUI'ya özgü davranışta hata ayıklıyorsanız [ComfyUI](/providers/comfy) bölümüne bakın. Paylaşılan sağlayıcı davranışında hata ayıklıyorsanız [Google (Gemini)](/tr/providers/google) veya [MiniMax](/tr/providers/minimax) ile başlayın.

## Canlı testler

Paylaşılan paketlenmiş sağlayıcılar için isteğe bağlı canlı kapsam:

```bash
OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts
```

Paketlenmiş ComfyUI müzik yolu için isteğe bağlı canlı kapsam:

```bash
OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts
```

Comfy canlı dosyası ayrıca, bu
bölümler yapılandırıldığında comfy görsel ve video iş akışlarını da kapsar.

## İlgili

- [Arka Plan Görevleri](/tr/automation/tasks) - ayrılmış `music_generate` çalıştırmaları için görev izleme
- [Yapılandırma Başvurusu](/tr/gateway/configuration-reference#agent-defaults) - `musicGenerationModel` yapılandırması
- [ComfyUI](/providers/comfy)
- [Google (Gemini)](/tr/providers/google)
- [MiniMax](/tr/providers/minimax)
- [Models](/tr/concepts/models) - model yapılandırması ve geri dönüş
- [Araçlara Genel Bakış](/tr/tools)
