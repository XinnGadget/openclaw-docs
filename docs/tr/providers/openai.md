---
read_when:
    - OpenClaw içinde OpenAI modellerini kullanmak istiyorsunuz
    - API anahtarları yerine Codex abonelik auth kullanmak istiyorsunuz
summary: OpenAI'yi OpenClaw içinde API anahtarları veya Codex aboneliğiyle kullanın
title: OpenAI
x-i18n:
    generated_at: "2026-04-07T08:49:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6a2ce1ce5f085fe55ec50b8d20359180b9002c9730820cd5b0e011c3bf807b64
    source_path: providers/openai.md
    workflow: 15
---

# OpenAI

OpenAI, GPT modelleri için geliştirici API'leri sağlar. Codex, abonelik
erişimi için **ChatGPT oturum açmayı** veya kullanıma dayalı erişim için **API anahtarı**
oturum açmayı destekler. Codex cloud, ChatGPT oturum açmayı gerektirir.
OpenAI, OpenClaw gibi harici araçlar/iş akışlarında abonelik OAuth kullanımını açıkça destekler.

## Varsayılan etkileşim stili

OpenClaw, hem `openai/*` hem de
`openai-codex/*` çalıştırmaları için küçük bir OpenAI'ye özgü prompt katmanı ekleyebilir. Varsayılan olarak,
bu katman asistanı sıcak, iş birliğine açık, özlü, doğrudan ve biraz daha duygusal olarak ifade edici tutar;
ancak temel OpenClaw sistem prompt'unun yerini almaz. Samimi katman ayrıca,
genel çıktıyı özlü tutarken doğal uyduğunda ara sıra emoji kullanımına da izin verir.

Yapılandırma anahtarı:

`plugins.entries.openai.config.personality`

İzin verilen değerler:

- `"friendly"`: varsayılan; OpenAI'ye özgü katmanı etkinleştirir.
- `"on"`: `"friendly"` için takma ad.
- `"off"`: katmanı devre dışı bırakır ve yalnızca temel OpenClaw prompt'unu kullanır.

Kapsam:

- `openai/*` modellerine uygulanır.
- `openai-codex/*` modellerine uygulanır.
- Diğer sağlayıcıları etkilemez.

Bu davranış varsayılan olarak açıktır. Bunun gelecekteki yerel yapılandırma değişimlerinden
etkilenmemesini istiyorsanız `"friendly"` değerini açıkça koruyun:

```json5
{
  plugins: {
    entries: {
      openai: {
        config: {
          personality: "friendly",
        },
      },
    },
  },
}
```

### OpenAI prompt katmanını devre dışı bırakma

Değiştirilmemiş temel OpenClaw prompt'unu istiyorsanız katmanı `"off"` olarak ayarlayın:

```json5
{
  plugins: {
    entries: {
      openai: {
        config: {
          personality: "off",
        },
      },
    },
  },
}
```

Bunu doğrudan yapılandırma CLI ile de ayarlayabilirsiniz:

```bash
openclaw config set plugins.entries.openai.config.personality off
```

OpenClaw bu ayarı çalışma zamanında büyük/küçük harfe duyarsız şekilde normalleştirir, bu nedenle
`"Off"` gibi değerler de samimi katmanı devre dışı bırakır.

## Seçenek A: OpenAI API anahtarı (OpenAI Platform)

**Şunlar için en uygunu:** doğrudan API erişimi ve kullanıma dayalı faturalama.
API anahtarınızı OpenAI kontrol panelinden alın.

Yol özeti:

- `openai/gpt-5.4` = doğrudan OpenAI Platform API yolu
- `OPENAI_API_KEY` gerektirir (veya eşdeğer OpenAI sağlayıcı yapılandırması)
- OpenClaw içinde ChatGPT/Codex oturum açma, `openai/*` yerine `openai-codex/*` üzerinden yönlendirilir

### CLI kurulumu

```bash
openclaw onboard --auth-choice openai-api-key
# veya etkileşimsiz
openclaw onboard --openai-api-key "$OPENAI_API_KEY"
```

### Yapılandırma parçacığı

```json5
{
  env: { OPENAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

OpenAI'nin mevcut API model belgeleri, doğrudan
OpenAI API kullanımı için `gpt-5.4` ve `gpt-5.4-pro` listeler. OpenClaw her ikisini de
`openai/*` Responses yolu üzerinden iletir.
OpenClaw, eski `openai/gpt-5.3-codex-spark` satırını bilerek gizler;
çünkü doğrudan OpenAI API çağrıları bunu canlı trafikte reddeder.

OpenClaw, doğrudan OpenAI
API yolunda `openai/gpt-5.3-codex-spark` sunmaz. `pi-ai` hâlâ bu model için yerleşik bir satır
sağlar, ancak canlı OpenAI API
istekleri şu anda bunu reddeder. Spark, OpenClaw içinde yalnızca Codex olarak değerlendirilir.

## Görsel üretimi

Paketle gelen `openai` plugin'i ayrıca paylaşılan
`image_generate` tool'u üzerinden görsel üretimini de kaydeder.

- Varsayılan görsel modeli: `openai/gpt-image-1`
- Üretim: istek başına en fazla 4 görsel
- Düzenleme modu: etkin, en fazla 5 referans görsel
- `size` desteklenir
- OpenAI'ye özgü mevcut uyarı: OpenClaw şu anda `aspectRatio` veya
  `resolution` geçersiz kılmalarını OpenAI Images API'ye iletmez

OpenAI'yi varsayılan görsel sağlayıcısı olarak kullanmak için:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "openai/gpt-image-1",
      },
    },
  },
}
```

Paylaşılan tool
parametreleri, sağlayıcı seçimi ve yedekleme davranışı için [Image Generation](/tr/tools/image-generation) belgesine bakın.

## Video üretimi

Paketle gelen `openai` plugin'i ayrıca paylaşılan
`video_generate` tool'u üzerinden video üretimini de kaydeder.

- Varsayılan video modeli: `openai/sora-2`
- Modlar: text-to-video, image-to-video ve single-video reference/edit akışları
- Geçerli sınırlar: 1 görsel veya 1 video referans girdisi
- OpenAI'ye özgü mevcut uyarı: OpenClaw şu anda yerel OpenAI video üretimi için yalnızca `size`
  geçersiz kılmalarını iletir. `aspectRatio`, `resolution`, `audio` ve `watermark` gibi
  desteklenmeyen isteğe bağlı geçersiz kılmalar yok sayılır
  ve bir tool uyarısı olarak geri bildirilir.

OpenAI'yi varsayılan video sağlayıcısı olarak kullanmak için:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "openai/sora-2",
      },
    },
  },
}
```

Paylaşılan tool
parametreleri, sağlayıcı seçimi ve yedekleme davranışı için [Video Generation](/tr/tools/video-generation) belgesine bakın.

## Seçenek B: OpenAI Code (Codex) aboneliği

**Şunlar için en uygunu:** API anahtarı yerine ChatGPT/Codex abonelik erişimini kullanmak.
Codex cloud, ChatGPT oturum açmayı gerektirirken Codex CLI, ChatGPT veya API anahtarı ile oturum açmayı destekler.

Yol özeti:

- `openai-codex/gpt-5.4` = ChatGPT/Codex OAuth yolu
- Doğrudan OpenAI Platform API anahtarı değil, ChatGPT/Codex oturum açma kullanır
- `openai-codex/*` için sağlayıcı tarafı sınırlar, ChatGPT web/uygulama deneyiminden farklı olabilir

### CLI kurulumu (Codex OAuth)

```bash
# Sihirbaz içinde Codex OAuth çalıştırın
openclaw onboard --auth-choice openai-codex

# Veya OAuth'u doğrudan çalıştırın
openclaw models auth login --provider openai-codex
```

### Yapılandırma parçacığı (Codex aboneliği)

```json5
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
}
```

OpenAI'nin mevcut Codex belgeleri, güncel Codex modeli olarak `gpt-5.4` listeler. OpenClaw
bunu ChatGPT/Codex OAuth kullanımı için `openai-codex/gpt-5.4` ile eşler.

Bu yol bilerek `openai/gpt-5.4` yolundan ayrıdır. Doğrudan
OpenAI Platform API yolunu istiyorsanız API anahtarıyla `openai/*` kullanın. ChatGPT/Codex oturum açma istiyorsanız `openai-codex/*` kullanın.

Onboarding mevcut bir Codex CLI girişini yeniden kullanırsa, bu kimlik bilgileri
Codex CLI tarafından yönetilmeye devam eder. Süresi dolduğunda OpenClaw önce harici Codex kaynağını yeniden okur
ve sağlayıcı bunu yenileyebildiğinde, yenilenmiş kimlik bilgisini ayrı bir yalnızca OpenClaw kopyasında sahiplenmek yerine
yeniden Codex depolamasına yazar.

Codex hesabınız Codex Spark hakkına sahipse OpenClaw ayrıca şunu da destekler:

- `openai-codex/gpt-5.3-codex-spark`

OpenClaw, Codex Spark'ı yalnızca Codex olarak değerlendirir. Doğrudan bir
`openai/gpt-5.3-codex-spark` API anahtarı yolu sunmaz.

OpenClaw ayrıca `pi-ai`
bunu keşfettiğinde `openai-codex/gpt-5.3-codex-spark` değerini korur. Bunu hakka bağlı ve deneysel olarak değerlendirin: Codex Spark,
GPT-5.4 `/fast` özelliğinden ayrıdır ve kullanılabilirlik oturum açılmış Codex /
ChatGPT hesabına bağlıdır.

### Codex bağlam penceresi sınırı

OpenClaw, Codex model üst verisini ve çalışma zamanı bağlam sınırını ayrı
değerler olarak ele alır.

`openai-codex/gpt-5.4` için:

- yerel `contextWindow`: `1050000`
- varsayılan çalışma zamanı `contextTokens` sınırı: `272000`

Bu, model üst verisini doğru tutarken pratikte daha iyi gecikme ve kalite
özelliklerine sahip daha küçük varsayılan çalışma zamanı
penceresini korur.

Farklı bir etkin sınır istiyorsanız `models.providers.<provider>.models[].contextTokens` ayarlayın:

```json5
{
  models: {
    providers: {
      "openai-codex": {
        models: [
          {
            id: "gpt-5.4",
            contextTokens: 160000,
          },
        ],
      },
    },
  },
}
```

Yalnızca yerel model
üst verisini tanımlarken veya geçersiz kılarken `contextWindow` kullanın. Çalışma zamanı bağlam bütçesini sınırlamak istiyorsanız `contextTokens` kullanın.

### Varsayılan taşıma

OpenClaw model akışı için `pi-ai` kullanır. Hem `openai/*` hem de
`openai-codex/*` için varsayılan taşıma `"auto"` şeklindedir (önce WebSocket, sonra SSE
yedeklemesi).

`"auto"` modunda OpenClaw, SSE'ye yedeklemeden önce
erken ve yeniden denenebilir bir WebSocket hatasını da bir kez yeniden dener.
Zorlanmış `"websocket"` modu ise taşıma
hatalarını yedeklemenin arkasına gizlemek yerine doğrudan gösterir.

`"auto"` modunda bir bağlanma veya erken tur WebSocket hatasından sonra OpenClaw,
o oturumun WebSocket yolunu yaklaşık 60 saniye boyunca bozulmuş olarak işaretler ve
taşımalar arasında gidip gelmek yerine soğuma süresi boyunca sonraki
turları SSE üzerinden gönderir.

Yerel OpenAI ailesi uç noktaları için (`openai/*`, `openai-codex/*` ve Azure
OpenAI Responses), OpenClaw ayrıca isteklerine kararlı oturum ve tur kimlik durumu
ekler; böylece yeniden denemeler, yeniden bağlantılar ve SSE yedeklemesi aynı
konuşma kimliğiyle hizalı kalır. Yerel OpenAI ailesi yollarında buna kararlı
oturum/tur istek kimliği başlıkları ile eşleşen taşıma üst verileri dahildir.

OpenClaw ayrıca OpenAI kullanım sayaçlarını taşıma varyantları arasında
oturum/durum yüzeylerine ulaşmadan önce normalize eder. Yerel OpenAI/Codex Responses trafiği
kullanımı `input_tokens` / `output_tokens` veya
`prompt_tokens` / `completion_tokens` olarak bildirebilir; OpenClaw bunları `/status`, `/usage` ve oturum günlükleri için
aynı giriş ve çıkış sayaçları olarak değerlendirir.
Yerel WebSocket trafiği `total_tokens` değerini atladığında (veya `0` bildirdiğinde), OpenClaw
oturum/durum görünümlerinin dolu kalması için normalize edilmiş giriş + çıkış toplamına geri düşer.

`agents.defaults.models.<provider/model>.params.transport` ayarlayabilirsiniz:

- `"sse"`: SSE'yi zorla
- `"websocket"`: WebSocket'i zorla
- `"auto"`: WebSocket'i dene, sonra SSE'ye yedekle

`openai/*` için (Responses API), OpenClaw ayrıca WebSocket taşıması kullanıldığında
varsayılan olarak WebSocket ısındırmayı etkinleştirir (`openaiWsWarmup: true`).

İlgili OpenAI belgeleri:

- [Realtime API with WebSocket](https://platform.openai.com/docs/guides/realtime-websocket)
- [Streaming API responses (SSE)](https://platform.openai.com/docs/guides/streaming-responses)

```json5
{
  agents: {
    defaults: {
      model: { primary: "openai-codex/gpt-5.4" },
      models: {
        "openai-codex/gpt-5.4": {
          params: {
            transport: "auto",
          },
        },
      },
    },
  },
}
```

### OpenAI WebSocket ısındırma

OpenAI belgeleri ısındırmayı isteğe bağlı olarak tanımlar. OpenClaw,
WebSocket taşıması kullanılırken ilk tur gecikmesini azaltmak için bunu
`openai/*` için varsayılan olarak etkinleştirir.

### Isındırmayı devre dışı bırakma

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            openaiWsWarmup: false,
          },
        },
      },
    },
  },
}
```

### Isındırmayı açıkça etkinleştirme

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            openaiWsWarmup: true,
          },
        },
      },
    },
  },
}
```

### OpenAI ve Codex öncelikli işleme

OpenAI'nin API'si, `service_tier=priority` aracılığıyla öncelikli işleme sunar. OpenClaw'da,
bu alanı yerel OpenAI/Codex Responses uç noktalarına geçirmek için
`agents.defaults.models["<provider>/<model>"].params.serviceTier` ayarlayın.

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            serviceTier: "priority",
          },
        },
        "openai-codex/gpt-5.4": {
          params: {
            serviceTier: "priority",
          },
        },
      },
    },
  },
}
```

Desteklenen değerler `auto`, `default`, `flex` ve `priority` şeklindedir.

OpenClaw, `params.serviceTier` değerini hem doğrudan `openai/*` Responses
isteklerine hem de bu modeller yerel OpenAI/Codex uç noktalarını işaret ettiğinde
`openai-codex/*` Codex Responses isteklerine iletir.

Önemli davranış:

- doğrudan `openai/*`, `api.openai.com` hedefini kullanmalıdır
- `openai-codex/*`, `chatgpt.com/backend-api` hedefini kullanmalıdır
- sağlayıcılardan herhangi birini başka bir temel URL veya proxy üzerinden yönlendirirseniz, OpenClaw `service_tier` alanına dokunmaz

### OpenAI hızlı modu

OpenClaw, hem `openai/*` hem de
`openai-codex/*` oturumları için paylaşılan bir hızlı mod anahtarı sunar:

- Sohbet/UI: `/fast status|on|off`
- Yapılandırma: `agents.defaults.models["<provider>/<model>"].params.fastMode`

Hızlı mod etkinleştirildiğinde OpenClaw bunu OpenAI öncelikli işlemeye eşler:

- `api.openai.com` üzerindeki doğrudan `openai/*` Responses çağrıları `service_tier = "priority"` gönderir
- `chatgpt.com/backend-api` üzerindeki `openai-codex/*` Responses çağrıları da `service_tier = "priority"` gönderir
- mevcut yük `service_tier` değerleri korunur
- hızlı mod `reasoning` veya `text.verbosity` alanlarını yeniden yazmaz

Özellikle GPT 5.4 için en yaygın kurulum şudur:

- `openai/gpt-5.4` veya `openai-codex/gpt-5.4` kullanan bir oturumda `/fast on` gönderin
- veya `agents.defaults.models["openai/gpt-5.4"].params.fastMode = true` ayarlayın
- Codex OAuth da kullanıyorsanız `agents.defaults.models["openai-codex/gpt-5.4"].params.fastMode = true` değerini de ayarlayın

Örnek:

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            fastMode: true,
          },
        },
        "openai-codex/gpt-5.4": {
          params: {
            fastMode: true,
          },
        },
      },
    },
  },
}
```

Oturum geçersiz kılmaları yapılandırmaya üstün gelir. Sessions UI içinde
oturum geçersiz kılmasını temizlemek, oturumu yeniden yapılandırılmış varsayılana döndürür.

### Yerel OpenAI ile OpenAI uyumlu yollar karşılaştırması

OpenClaw, doğrudan OpenAI, Codex ve Azure OpenAI uç noktalarını
genel OpenAI uyumlu `/v1` proxy'lerinden farklı ele alır:

- yerel `openai/*`, `openai-codex/*` ve Azure OpenAI yolları,
  reasoning'i açıkça devre dışı bıraktığınızda `reasoning: { effort: "none" }` değerini korur
- yerel OpenAI ailesi yolları varsayılan olarak tool şemalarını strict moda alır
- gizli OpenClaw atıf başlıkları (`originator`, `version` ve
  `User-Agent`) yalnızca doğrulanmış yerel OpenAI host'larında
  (`api.openai.com`) ve yerel Codex host'larında (`chatgpt.com/backend-api`) eklenir
- yerel OpenAI/Codex yolları,
  `service_tier`, Responses `store`, OpenAI reasoning uyumluluk yükleri ve
  prompt önbellek ipuçları gibi yalnızca OpenAI'ye özgü istek şekillendirmelerini korur
- proxy tarzı OpenAI uyumlu yollar daha gevşek uyumluluk davranışını korur ve
  strict tool şemalarını, yalnızca yerel istek şekillendirmelerini veya gizli
  OpenAI/Codex atıf başlıklarını zorlamaz

Azure OpenAI, taşıma ve uyumluluk
davranışı için yerel yönlendirme kovasında kalır, ancak gizli OpenAI/Codex atıf başlıklarını almaz.

Bu, mevcut yerel OpenAI Responses davranışını korurken daha eski
OpenAI uyumlu shim'leri üçüncü taraf `/v1` arka uçlarına zorlamaz.

### OpenAI Responses sunucu tarafı sıkıştırma

Doğrudan OpenAI Responses modelleri için (`openai/*`, `api: "openai-responses"` kullanırken
ve `baseUrl` değeri `api.openai.com` üzerindeyken), OpenClaw artık OpenAI sunucu tarafı
sıkıştırma yükü ipuçlarını otomatik etkinleştirir:

- `store: true` değerini zorlar (`supportsStore: false` ayarlayan model uyumluluğu yoksa)
- `context_management: [{ type: "compaction", compact_threshold: ... }]` ekler

Varsayılan olarak `compact_threshold`, model `contextWindow` değerinin `%70`'idir
(veya bu yoksa `80000`).

### Sunucu tarafı sıkıştırmayı açıkça etkinleştirme

Uyumlu
Responses modellerinde (örneğin Azure OpenAI Responses) `context_management` eklemeyi zorlamak istediğinizde bunu kullanın:

```json5
{
  agents: {
    defaults: {
      models: {
        "azure-openai-responses/gpt-5.4": {
          params: {
            responsesServerCompaction: true,
          },
        },
      },
    },
  },
}
```

### Özel bir eşikle etkinleştirme

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            responsesServerCompaction: true,
            responsesCompactThreshold: 120000,
          },
        },
      },
    },
  },
}
```

### Sunucu tarafı sıkıştırmayı devre dışı bırakma

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            responsesServerCompaction: false,
          },
        },
      },
    },
  },
}
```

`responsesServerCompaction` yalnızca `context_management` eklemeyi kontrol eder.
Doğrudan OpenAI Responses modelleri, uyumluluk
`supportsStore: false` ayarlamadığı sürece yine de `store: true` zorlar.

## Notlar

- Model referansları her zaman `provider/model` kullanır (bkz. [/concepts/models](/tr/concepts/models)).
- Auth ayrıntıları + yeniden kullanım kuralları [/concepts/oauth](/tr/concepts/oauth) içindedir.
