---
read_when:
    - OpenClaw içinde OpenAI modellerini kullanmak istiyorsunuz
    - API anahtarları yerine Codex abonelik kimlik doğrulaması istiyorsunuz
summary: OpenClaw içinde OpenAI'ı API anahtarları veya Codex aboneliği üzerinden kullanın
title: OpenAI
x-i18n:
    generated_at: "2026-04-06T03:12:28Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9e04db5787f6ed7b1eda04d965c10febae10809fc82ae4d9769e7163234471f5
    source_path: providers/openai.md
    workflow: 15
---

# OpenAI

OpenAI, GPT modelleri için geliştirici API'leri sağlar. Codex, abonelik
erişimi için **ChatGPT oturum açmayı** veya kullanıma dayalı erişim için **API anahtarı**
oturum açmayı destekler. Codex cloud, ChatGPT oturum açma gerektirir.
OpenAI, OpenClaw gibi harici araçlarda/iş akışlarında abonelik OAuth kullanımını açıkça destekler.

## Varsayılan etkileşim stili

OpenClaw, hem `openai/*` hem de
`openai-codex/*` çalıştırmaları için OpenAI'a özgü küçük bir istem katmanı ekleyebilir. Varsayılan olarak bu katman,
assistant'ı sıcak, iş birlikçi, kısa, doğrudan ve biraz daha duygusal olarak ifade edebilir
tutar; bunu yaparken temel OpenClaw sistem isteminin yerini almaz. Bu dostane katman ayrıca
genel çıktıyı kısa tutarken uygun olduğunda ara sıra emoji kullanımına da izin verir.

Yapılandırma anahtarı:

`plugins.entries.openai.config.personality`

İzin verilen değerler:

- `"friendly"`: varsayılan; OpenAI'a özgü katmanı etkinleştirir.
- `"off"`: katmanı devre dışı bırakır ve yalnızca temel OpenClaw istemini kullanır.

Kapsam:

- `openai/*` modellerine uygulanır.
- `openai-codex/*` modellerine uygulanır.
- Diğer sağlayıcıları etkilemez.

Bu davranış varsayılan olarak açıktır. Bunun gelecekteki yerel yapılandırma değişikliklerinden
etkilenmeden kalmasını istiyorsanız `"friendly"` değerini açıkça koruyun:

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

### OpenAI istem katmanını devre dışı bırakma

Değiştirilmemiş temel OpenClaw istemini istiyorsanız, katmanı `"off"` olarak ayarlayın:

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

Bunu doğrudan config CLI ile de ayarlayabilirsiniz:

```bash
openclaw config set plugins.entries.openai.config.personality off
```

## Seçenek A: OpenAI API anahtarı (OpenAI Platform)

**Şunun için en iyisi:** doğrudan API erişimi ve kullanıma dayalı faturalandırma.
API anahtarınızı OpenAI panosundan alın.

### CLI kurulumu

```bash
openclaw onboard --auth-choice openai-api-key
# veya etkileşimsiz
openclaw onboard --openai-api-key "$OPENAI_API_KEY"
```

### Yapılandırma örneği

```json5
{
  env: { OPENAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

OpenAI'ın mevcut API model belgelerinde, doğrudan
OpenAI API kullanımı için `gpt-5.4` ve `gpt-5.4-pro` listelenir. OpenClaw ikisini de
`openai/*` Responses yolu üzerinden iletir.
OpenClaw, eski `openai/gpt-5.3-codex-spark` satırını kasıtlı olarak gizler,
çünkü doğrudan OpenAI API çağrıları bunu canlı trafikte reddeder.

OpenClaw, doğrudan OpenAI
API yolunda `openai/gpt-5.3-codex-spark` modelini göstermez. `pi-ai` hâlâ bu model için yerleşik
bir satır gönderir, ancak canlı OpenAI API istekleri şu anda bunu reddeder.
OpenClaw içinde Spark yalnızca Codex olarak ele alınır.

## Görsel oluşturma

Paketlenmiş `openai` plugin'i ayrıca paylaşılan
`image_generate` aracı üzerinden görsel oluşturmayı da kaydeder.

- Varsayılan görsel modeli: `openai/gpt-image-1`
- Oluşturma: istek başına en fazla 4 görsel
- Düzenleme kipi: etkin, en fazla 5 referans görsel
- `size` desteklenir
- OpenAI'a özgü mevcut kısıt: OpenClaw bugün `aspectRatio` veya
  `resolution` geçersiz kılmalarını OpenAI Images API'ye iletmez

OpenAI'ı varsayılan görsel sağlayıcısı olarak kullanmak için:

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

Paylaşılan araç
parametreleri, sağlayıcı seçimi ve failover davranışı için bkz. [Görsel Oluşturma](/tr/tools/image-generation).

## Video oluşturma

Paketlenmiş `openai` plugin'i ayrıca paylaşılan
`video_generate` aracı üzerinden video oluşturmayı da kaydeder.

- Varsayılan video modeli: `openai/sora-2`
- Kipler: metinden videoya, görselden videoya ve tek videolu referans/düzenleme akışları
- Mevcut sınırlar: 1 görsel veya 1 video referans girdisi
- OpenAI'a özgü mevcut kısıt: OpenClaw şu anda yerel OpenAI video oluşturma için yalnızca `size`
  geçersiz kılmalarını iletir. `aspectRatio`, `resolution`, `audio` ve `watermark` gibi
  desteklenmeyen isteğe bağlı geçersiz kılmalar yok sayılır
  ve araç uyarısı olarak geri bildirilir.

OpenAI'ı varsayılan video sağlayıcısı olarak kullanmak için:

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

Paylaşılan araç
parametreleri, sağlayıcı seçimi ve failover davranışı için bkz. [Video Oluşturma](/tools/video-generation).

## Seçenek B: OpenAI Code (Codex) aboneliği

**Şunun için en iyisi:** API anahtarı yerine ChatGPT/Codex abonelik erişimini kullanmak.
Codex cloud ChatGPT oturum açma gerektirirken, Codex CLI ChatGPT veya API anahtarıyla oturum açmayı destekler.

### CLI kurulumu (Codex OAuth)

```bash
# Sihirbazda Codex OAuth çalıştırın
openclaw onboard --auth-choice openai-codex

# Veya OAuth'u doğrudan çalıştırın
openclaw models auth login --provider openai-codex
```

### Yapılandırma örneği (Codex aboneliği)

```json5
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
}
```

OpenAI'ın mevcut Codex belgelerinde `gpt-5.4`, güncel Codex modeli olarak listelenir. OpenClaw
bunu ChatGPT/Codex OAuth kullanımı için `openai-codex/gpt-5.4` olarak eşler.

Onboarding mevcut bir Codex CLI oturum açmasını yeniden kullanırsa, bu kimlik bilgileri
Codex CLI tarafından yönetilmeye devam eder. Süre dolduğunda OpenClaw önce
harici Codex kaynağını yeniden okur ve sağlayıcı bunu yenileyebiliyorsa, yenilenmiş kimlik bilgisini
ayrı bir yalnızca-OpenClaw kopyasında sahiplenmek yerine tekrar Codex depolamasına yazar.

Codex hesabınızın Codex Spark hakkı varsa, OpenClaw şunu da destekler:

- `openai-codex/gpt-5.3-codex-spark`

OpenClaw, Codex Spark'ı yalnızca Codex olarak ele alır. Doğrudan bir
`openai/gpt-5.3-codex-spark` API anahtarı yolu göstermez.

OpenClaw ayrıca `pi-ai`
bunu keşfettiğinde `openai-codex/gpt-5.3-codex-spark` modelini korur.
Bunu hakka bağlı ve deneysel olarak değerlendirin: Codex Spark,
GPT-5.4 `/fast`'ten ayrıdır ve kullanılabilirlik oturum açılmış Codex /
ChatGPT hesabına bağlıdır.

### Codex bağlam penceresi üst sınırı

OpenClaw, Codex model meta verisini ve çalışma zamanı bağlam üst sınırını ayrı
değerler olarak ele alır.

`openai-codex/gpt-5.4` için:

- yerel `contextWindow`: `1050000`
- varsayılan çalışma zamanı `contextTokens` üst sınırı: `272000`

Bu, model meta verisini doğru tutarken uygulamada daha iyi gecikme ve kalite özelliklerine
sahip daha küçük varsayılan çalışma zamanı penceresini korur.

Farklı bir etkin üst sınır istiyorsanız `models.providers.<provider>.models[].contextTokens` ayarlayın:

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

Yerel model
meta verisini tanımlarken veya geçersiz kılarken yalnızca `contextWindow` kullanın.
Çalışma zamanı bağlam bütçesini sınırlamak istediğinizde `contextTokens` kullanın.

### Taşıma varsayılanı

OpenClaw, model akışı için `pi-ai` kullanır. Hem `openai/*` hem de
`openai-codex/*` için varsayılan taşıma `"auto"`'dur (önce WebSocket, sonra SSE
geri dönüşü).

`"auto"` kipinde OpenClaw ayrıca SSE'ye geri dönmeden önce
erken, yeniden denenebilir bir WebSocket hatasını da yeniden dener. Zorunlu `"websocket"` kipi ise
taşıma hatalarını geri dönüş arkasına gizlemek yerine doğrudan gösterir.

`"auto"` kipinde bir bağlanma veya erken tur WebSocket hatasından sonra OpenClaw,
o oturumun WebSocket yolunu yaklaşık 60 saniye boyunca bozulmuş olarak işaretler ve
taşımalar arasında gidip gelmek yerine sonraki turları soğuma süresi boyunca
SSE üzerinden gönderir.

Yerel OpenAI ailesi uç noktaları için (`openai/*`, `openai-codex/*` ve Azure
OpenAI Responses), OpenClaw ayrıca isteklerle kararlı oturum ve tur kimlik durumu da
ekler; böylece yeniden denemeler, yeniden bağlanmalar ve SSE geri dönüşü aynı
konuşma kimliğiyle hizalı kalır. Yerel OpenAI ailesi rotalarında buna kararlı
oturum/tur istek kimliği üstbilgileri ile eşleşen taşıma meta verisi dahildir.

OpenClaw ayrıca OpenAI kullanım sayaçlarını taşıma çeşitleri arasında
oturum/durum yüzeylerine ulaşmadan önce normalleştirir. Yerel OpenAI/Codex Responses trafiği
kullanımı `input_tokens` / `output_tokens` veya
`prompt_tokens` / `completion_tokens` olarak bildirebilir; OpenClaw bunları
`/status`, `/usage` ve oturum günlükleri için aynı giriş ve çıkış sayaçları olarak ele alır.
Yerel WebSocket trafiği `total_tokens` değerini atladığında (veya `0` bildirdiğinde), OpenClaw
oturum/durum görüntülerinin dolu kalması için normalleştirilmiş giriş + çıkış toplamına geri döner.

Şunu ayarlayabilirsiniz: `agents.defaults.models.<provider/model>.params.transport`:

- `"sse"`: SSE'yi zorlar
- `"websocket"`: WebSocket'i zorlar
- `"auto"`: WebSocket'i dener, sonra SSE'ye geri döner

`openai/*` için (Responses API), OpenClaw ayrıca WebSocket taşıması
kullanıldığında varsayılan olarak WebSocket ısınmasını (`openaiWsWarmup: true`) etkinleştirir.

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

### OpenAI WebSocket ısınması

OpenAI belgeleri ısınmayı isteğe bağlı olarak açıklar. OpenClaw,
WebSocket taşıması kullanırken ilk tur gecikmesini azaltmak için bunu varsayılan olarak
`openai/*` için etkinleştirir.

### Isınmayı devre dışı bırakma

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

### Isınmayı açıkça etkinleştirme

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

OpenAI'ın API'si, `service_tier=priority` üzerinden öncelikli işleme sunar. OpenClaw içinde,
bu alanı yerel OpenAI/Codex Responses uç noktalarına iletmek için
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

Desteklenen değerler `auto`, `default`, `flex` ve `priority`'dir.

OpenClaw, `params.serviceTier` değerini hem doğrudan `openai/*` Responses
isteklerine hem de `openai-codex/*` Codex Responses isteklerine bu modeller
yerel OpenAI/Codex uç noktalarını gösterdiğinde iletir.

Önemli davranış:

- doğrudan `openai/*`, `api.openai.com` hedeflemelidir
- `openai-codex/*`, `chatgpt.com/backend-api` hedeflemelidir
- herhangi bir sağlayıcıyı başka bir temel URL veya proxy üzerinden yönlendirirseniz, OpenClaw `service_tier` değerine dokunmaz

### OpenAI hızlı kipi

OpenClaw, hem `openai/*` hem de
`openai-codex/*` oturumları için paylaşılan bir hızlı kip anahtarı sunar:

- Sohbet/UI: `/fast status|on|off`
- Yapılandırma: `agents.defaults.models["<provider>/<model>"].params.fastMode`

Hızlı kip etkin olduğunda OpenClaw bunu OpenAI öncelikli işlemeye eşler:

- `api.openai.com` adresine giden doğrudan `openai/*` Responses çağrıları `service_tier = "priority"` gönderir
- `chatgpt.com/backend-api` adresine giden `openai-codex/*` Responses çağrıları da `service_tier = "priority"` gönderir
- mevcut payload `service_tier` değerleri korunur
- hızlı kip, `reasoning` veya `text.verbosity` değerlerini yeniden yazmaz

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

Oturum geçersiz kılmaları yapılandırmadan önceliklidir. Sessions UI içinde oturum geçersiz kılmasını temizlemek,
oturumu yapılandırılmış varsayılana geri döndürür.

### Yerel OpenAI ile OpenAI uyumlu rotalar karşılaştırması

OpenClaw, doğrudan OpenAI, Codex ve Azure OpenAI uç noktalarını
genel OpenAI uyumlu `/v1` proxy'lerinden farklı ele alır:

- yerel `openai/*`, `openai-codex/*` ve Azure OpenAI rotaları,
  `reasoning` açıkça devre dışı bırakıldığında `reasoning: { effort: "none" }` değerini olduğu gibi korur
- yerel OpenAI ailesi rotaları araç şemalarını varsayılan olarak strict kipte kullanır
- gizli OpenClaw atıf üstbilgileri (`originator`, `version` ve
  `User-Agent`) yalnızca doğrulanmış yerel OpenAI host'larında
  (`api.openai.com`) ve yerel Codex host'larında (`chatgpt.com/backend-api`) eklenir
- yerel OpenAI/Codex rotaları,
  `service_tier`, Responses `store`, OpenAI reasoning uyumluluk payload'ları ve
  istem önbelleği ipuçları gibi yalnızca OpenAI'a özgü istek şekillendirmesini korur
- proxy tarzı OpenAI uyumlu rotalar daha gevşek uyumluluk davranışını korur ve
  strict araç şemalarını, yalnızca yerel istek şekillendirmesini veya gizli
  OpenAI/Codex atıf üstbilgilerini zorlamaz

Azure OpenAI, taşıma ve uyumluluk davranışı açısından yerel yönlendirme grubunda kalır,
ancak gizli OpenAI/Codex atıf üstbilgilerini almaz.

Bu, mevcut yerel OpenAI Responses davranışını korurken eski
OpenAI uyumlu shim'leri üçüncü taraf `/v1` arka uçlarına zorlamaz.

### OpenAI Responses sunucu tarafı sıkıştırma

Doğrudan OpenAI Responses modelleri için (`api: "openai-responses"` kullanan `openai/*`,
ve `baseUrl` değeri `api.openai.com` olanlar), OpenClaw artık OpenAI sunucu tarafı
sıkıştırma payload ipuçlarını otomatik olarak etkinleştirir:

- `store: true` değerini zorlar (`supportsStore: false` ayarlayan model uyumluluğu yoksa)
- `context_management: [{ type: "compaction", compact_threshold: ... }]` enjekte eder

Varsayılan olarak `compact_threshold`, model `contextWindow` değerinin `%70`'idir
(veya mevcut değilse `80000`).

### Sunucu tarafı sıkıştırmayı açıkça etkinleştirme

Uyumlu
Responses modellerinde `context_management` eklemeyi zorlamak istediğinizde bunu kullanın
(örneğin Azure OpenAI Responses):

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

`responsesServerCompaction` yalnızca `context_management` eklemesini denetler.
Doğrudan OpenAI Responses modelleri, uyumluluk `supportsStore: false`
ayarlamadığı sürece yine de `store: true` zorlar.

## Notlar

- Model başvuruları her zaman `provider/model` biçimini kullanır (bkz. [/concepts/models](/tr/concepts/models)).
- Kimlik doğrulama ayrıntıları + yeniden kullanım kuralları [/concepts/oauth](/tr/concepts/oauth) içinde yer alır.
