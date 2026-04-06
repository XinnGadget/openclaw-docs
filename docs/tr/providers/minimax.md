---
read_when:
    - OpenClaw içinde MiniMax modellerini istiyorsunuz
    - MiniMax kurulum rehberine ihtiyacınız var
summary: OpenClaw içinde MiniMax modellerini kullanın
title: MiniMax
x-i18n:
    generated_at: "2026-04-06T03:12:06Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9ca35c43cdde53f6f09d9e12d48ce09e4c099cf8cbe1407ac6dbb45b1422507e
    source_path: providers/minimax.md
    workflow: 15
---

# MiniMax

OpenClaw'ın MiniMax sağlayıcısı varsayılan olarak **MiniMax M2.7** kullanır.

MiniMax ayrıca şunları da sağlar:

- T2A v2 aracılığıyla paketlenmiş konuşma sentezi
- `MiniMax-VL-01` aracılığıyla paketlenmiş görsel anlama
- `music-2.5+` aracılığıyla paketlenmiş müzik üretimi
- MiniMax Coding Plan arama API'si aracılığıyla paketlenmiş `web_search`

Sağlayıcı ayrımı:

- `minimax`: API anahtarlı metin sağlayıcısı, ayrıca paketlenmiş görsel üretimi, görsel anlama, konuşma ve web araması
- `minimax-portal`: OAuth metin sağlayıcısı, ayrıca paketlenmiş görsel üretimi ve görsel anlama

## Model ailesi

- `MiniMax-M2.7`: varsayılan barındırılan muhakeme modeli.
- `MiniMax-M2.7-highspeed`: daha hızlı M2.7 muhakeme katmanı.
- `image-01`: görsel üretim modeli (üretme ve görselden görsele düzenleme).

## Görsel üretimi

MiniMax eklentisi, `image_generate` aracı için `image-01` modelini kaydeder. Şunları destekler:

- En-boy oranı denetimiyle **metinden görsele üretim**.
- En-boy oranı denetimiyle **görselden görsele düzenleme** (özne referansı).
- İstek başına en fazla **9 çıktı görseli**.
- Düzenleme isteği başına en fazla **1 referans görsel**.
- Desteklenen en-boy oranları: `1:1`, `16:9`, `4:3`, `3:2`, `2:3`, `3:4`, `9:16`, `21:9`.

MiniMax'i görsel üretimi için kullanmak üzere onu görsel üretimi sağlayıcısı olarak ayarlayın:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: { primary: "minimax/image-01" },
    },
  },
}
```

Eklenti, metin modelleriyle aynı `MINIMAX_API_KEY` veya OAuth kimlik doğrulamasını kullanır. MiniMax zaten kurulmuşsa ek yapılandırma gerekmez.

Hem `minimax` hem de `minimax-portal`, aynı
`image-01` modeliyle `image_generate` kaydeder. API anahtarlı kurulumlar `MINIMAX_API_KEY` kullanır; OAuth kurulumları bunun yerine
paketlenmiş `minimax-portal` kimlik doğrulama yolunu kullanabilir.

Başlangıç veya API anahtarı kurulumu açık `models.providers.minimax`
girdileri yazdığında OpenClaw, `MiniMax-M2.7` ve
`MiniMax-M2.7-highspeed` modellerini `input: ["text", "image"]` ile somutlaştırır.

Yerleşik paketlenmiş MiniMax metin kataloğunun kendisi ise bu açık sağlayıcı yapılandırması oluşana kadar
yalnızca metin meta verisi olarak kalır. Görsel anlama, eklentiye ait `MiniMax-VL-01` medya sağlayıcısı aracılığıyla
ayrı olarak sunulur.

Paylaşılan araç
parametreleri, sağlayıcı seçimi ve geri dönüş davranışı için bkz. [Görsel Üretimi](/tr/tools/image-generation).

## Müzik üretimi

Paketlenmiş `minimax` eklentisi ayrıca paylaşılan
`music_generate` aracı aracılığıyla müzik üretimini de kaydeder.

- Varsayılan müzik modeli: `minimax/music-2.5+`
- Ayrıca `minimax/music-2.5` ve `minimax/music-2.0` desteklenir
- Prompt denetimleri: `lyrics`, `instrumental`, `durationSeconds`
- Çıktı biçimi: `mp3`
- Oturum destekli çalıştırmalar, `action: "status"` dahil olmak üzere paylaşılan görev/durum akışı üzerinden ayrılır

MiniMax'i varsayılan müzik sağlayıcısı olarak kullanmak için:

```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "minimax/music-2.5+",
      },
    },
  },
}
```

Paylaşılan araç
parametreleri, sağlayıcı seçimi ve geri dönüş davranışı için bkz. [Müzik Üretimi](/tools/music-generation).

## Video üretimi

Paketlenmiş `minimax` eklentisi ayrıca paylaşılan
`video_generate` aracı aracılığıyla video üretimini de kaydeder.

- Varsayılan video modeli: `minimax/MiniMax-Hailuo-2.3`
- Kipler: metinden videoya ve tek görsel referans akışları
- `aspectRatio` ve `resolution` desteklenir

MiniMax'i varsayılan video sağlayıcısı olarak kullanmak için:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "minimax/MiniMax-Hailuo-2.3",
      },
    },
  },
}
```

Paylaşılan araç
parametreleri, sağlayıcı seçimi ve geri dönüş davranışı için bkz. [Video Üretimi](/tools/video-generation).

## Görsel anlama

MiniMax eklentisi, görsel anlamayı metin
kataloğundan ayrı olarak kaydeder:

- `minimax`: varsayılan görsel modeli `MiniMax-VL-01`
- `minimax-portal`: varsayılan görsel modeli `MiniMax-VL-01`

Bu nedenle otomatik medya yönlendirmesi, paketlenmiş metin sağlayıcı kataloğu hâlâ yalnızca metin M2.7 sohbet başvurularını gösterse bile
MiniMax görsel anlamayı kullanabilir.

## Web araması

MiniMax eklentisi ayrıca MiniMax Coding Plan
arama API'si aracılığıyla `web_search` kaydeder.

- Sağlayıcı kimliği: `minimax`
- Yapılandırılmış sonuçlar: başlıklar, URL'ler, parçacıklar, ilgili sorgular
- Tercih edilen ortam değişkeni: `MINIMAX_CODE_PLAN_KEY`
- Kabul edilen ortam takma adı: `MINIMAX_CODING_API_KEY`
- Uyumluluk geri dönüşü: zaten coding-plan belirtecini işaret ediyorsa `MINIMAX_API_KEY`
- Bölge yeniden kullanımı: `plugins.entries.minimax.config.webSearch.region`, ardından `MINIMAX_API_HOST`, ardından MiniMax sağlayıcı temel URL'leri
- Arama, `minimax` sağlayıcı kimliği üzerinde kalır; OAuth CN/global kurulum yine de bölgeyi dolaylı olarak `models.providers.minimax-portal.baseUrl` aracılığıyla yönlendirebilir

Yapılandırma `plugins.entries.minimax.config.webSearch.*` altında bulunur.
Bkz. [MiniMax Search](/tr/tools/minimax-search).

## Bir kurulum seçin

### MiniMax OAuth (Coding Plan) - önerilen

**Şunun için en iyisi:** OAuth üzerinden MiniMax Coding Plan ile hızlı kurulum, API anahtarı gerekmez.

Açık bölgesel OAuth seçeneğiyle kimlik doğrulayın:

```bash
openclaw onboard --auth-choice minimax-global-oauth
# veya
openclaw onboard --auth-choice minimax-cn-oauth
```

Seçenek eşlemesi:

- `minimax-global-oauth`: Uluslararası kullanıcılar (`api.minimax.io`)
- `minimax-cn-oauth`: Çin'deki kullanıcılar (`api.minimaxi.com`)

Ayrıntılar için OpenClaw deposundaki MiniMax eklenti paketi README dosyasına bakın.

### MiniMax M2.7 (API anahtarı)

**Şunun için en iyisi:** Anthropic uyumlu API ile barındırılan MiniMax.

CLI ile yapılandırın:

- Etkileşimli başlangıç:

```bash
openclaw onboard --auth-choice minimax-global-api
# veya
openclaw onboard --auth-choice minimax-cn-api
```

- `minimax-global-api`: Uluslararası kullanıcılar (`api.minimax.io`)
- `minimax-cn-api`: Çin'deki kullanıcılar (`api.minimaxi.com`)

```json5
{
  env: { MINIMAX_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "minimax/MiniMax-M2.7" } } },
  models: {
    mode: "merge",
    providers: {
      minimax: {
        baseUrl: "https://api.minimax.io/anthropic",
        apiKey: "${MINIMAX_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "MiniMax-M2.7",
            name: "MiniMax M2.7",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0.3, output: 1.2, cacheRead: 0.06, cacheWrite: 0.375 },
            contextWindow: 204800,
            maxTokens: 131072,
          },
          {
            id: "MiniMax-M2.7-highspeed",
            name: "MiniMax M2.7 Highspeed",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0.6, output: 2.4, cacheRead: 0.06, cacheWrite: 0.375 },
            contextWindow: 204800,
            maxTokens: 131072,
          },
        ],
      },
    },
  },
}
```

Anthropic uyumlu akış yolunda OpenClaw artık,
`thinking` değerini kendiniz açıkça ayarlamadığınız sürece MiniMax
düşünmesini varsayılan olarak devre dışı bırakır. MiniMax'in
akış uç noktası, yerel Anthropic düşünme blokları yerine OpenAI tarzı delta parçalarında `reasoning_content`
çıkarır; bu da örtük olarak etkin bırakılırsa dahili muhakemenin
görünür çıktıya sızmasına neden olabilir.

### Geri dönüş olarak MiniMax M2.7 (örnek)

**Şunun için en iyisi:** En güçlü en yeni nesil modelinizi birincil tutup MiniMax M2.7'ye geri düşmek.
Aşağıdaki örnek somut bir birincil olarak Opus kullanır; bunu tercih ettiğiniz en yeni nesil birincil modelle değiştirin.

```json5
{
  env: { MINIMAX_API_KEY: "sk-..." },
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": { alias: "primary" },
        "minimax/MiniMax-M2.7": { alias: "minimax" },
      },
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["minimax/MiniMax-M2.7"],
      },
    },
  },
}
```

## `openclaw configure` ile yapılandırın

JSON düzenlemeden MiniMax ayarlamak için etkileşimli yapılandırma sihirbazını kullanın:

1. `openclaw configure` komutunu çalıştırın.
2. **Model/auth** seçin.
3. Bir **MiniMax** kimlik doğrulama seçeneği seçin.
4. İstendiğinde varsayılan modelinizi seçin.

Sihirbaz/CLI içindeki güncel MiniMax kimlik doğrulama seçenekleri:

- `minimax-global-oauth`
- `minimax-cn-oauth`
- `minimax-global-api`
- `minimax-cn-api`

## Yapılandırma seçenekleri

- `models.providers.minimax.baseUrl`: `https://api.minimax.io/anthropic` tercih edilir (Anthropic uyumlu); `https://api.minimax.io/v1`, OpenAI uyumlu yükler için isteğe bağlıdır.
- `models.providers.minimax.api`: `anthropic-messages` tercih edilir; `openai-completions`, OpenAI uyumlu yükler için isteğe bağlıdır.
- `models.providers.minimax.apiKey`: MiniMax API anahtarı (`MINIMAX_API_KEY`).
- `models.providers.minimax.models`: `id`, `name`, `reasoning`, `contextWindow`, `maxTokens`, `cost` tanımlayın.
- `agents.defaults.models`: izin listesinde olmasını istediğiniz modellere takma ad verin.
- `models.mode`: MiniMax'i yerleşiklerle birlikte eklemek istiyorsanız `merge` olarak tutun.

## Notlar

- Model başvuruları kimlik doğrulama yolunu izler:
  - API anahtarı kurulumu: `minimax/<model>`
  - OAuth kurulumu: `minimax-portal/<model>`
- Varsayılan sohbet modeli: `MiniMax-M2.7`
- Alternatif sohbet modeli: `MiniMax-M2.7-highspeed`
- `api: "anthropic-messages"` üzerinde OpenClaw,
  düşünme zaten
  parametrelerde/yapılandırmada açıkça ayarlanmamışsa `thinking: { type: "disabled" }`
  ekler.
- `/fast on` veya `params.fastMode: true`, Anthropic uyumlu akış yolunda
  `MiniMax-M2.7` modelini `MiniMax-M2.7-highspeed` olarak yeniden yazar.
- Başlangıç ve doğrudan API anahtarı kurulumu, her iki M2.7 varyantı için
  `input: ["text", "image"]` ile açık model tanımları yazar
- Paketlenmiş sağlayıcı kataloğu şu anda
  açık MiniMax sağlayıcı yapılandırması oluşana kadar sohbet başvurularını yalnızca metin meta verisi olarak sunar
- Coding Plan kullanım API'si: `https://api.minimaxi.com/v1/api/openplatform/coding_plan/remains` (bir coding plan anahtarı gerektirir).
- OpenClaw, MiniMax coding-plan kullanımını diğer sağlayıcıların kullandığı aynı
  `% kaldı` görünümüne normalize eder. MiniMax'in ham `usage_percent` / `usagePercent`
  alanları, tüketilen kota değil, kalan kotadır; bu yüzden OpenClaw bunları tersine çevirir.
  Sayı tabanlı alanlar varsa önceliklidir. API `model_remains` döndürdüğünde,
  OpenClaw sohbet modeli girdisini tercih eder, gerektiğinde pencere etiketini
  `start_time` / `end_time` değerlerinden türetir ve coding-plan pencerelerini ayırt etmeyi kolaylaştırmak için
  plan etiketine seçilen model adını ekler.
- Kullanım anlık görüntüleri `minimax`, `minimax-cn` ve `minimax-portal` değerlerini
  aynı MiniMax kota yüzeyi olarak ele alır ve Coding Plan anahtarı ortam değişkenlerine geri dönmeden önce
  depolanmış MiniMax OAuth'u tercih eder.
- Tam maliyet takibi gerekiyorsa `models.json` içindeki fiyatlandırma değerlerini güncelleyin.
- MiniMax Coding Plan için yönlendirme bağlantısı (%10 indirim): [https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link](https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link)
- Sağlayıcı kuralları için bkz. [/concepts/model-providers](/tr/concepts/model-providers).
- Geçerli sağlayıcı kimliğini doğrulamak için `openclaw models list` kullanın, ardından
  `openclaw models set minimax/MiniMax-M2.7` veya
  `openclaw models set minimax-portal/MiniMax-M2.7` ile değiştirin.

## Sorun giderme

### "Unknown model: minimax/MiniMax-M2.7"

Bu genellikle **MiniMax sağlayıcısının yapılandırılmadığı** anlamına gelir (eşleşen
sağlayıcı girdisi yok ve MiniMax kimlik doğrulama profili/ortam anahtarı bulunamadı). Bu
algılama için bir düzeltme **2026.1.12** sürümündedir. Şunları yaparak düzeltin:

- **2026.1.12** sürümüne yükseltin (veya kaynak koddan `main` çalıştırın), ardından gateway'i yeniden başlatın.
- `openclaw configure` çalıştırıp bir **MiniMax** kimlik doğrulama seçeneği seçin, veya
- Eşleşen `models.providers.minimax` veya
  `models.providers.minimax-portal` bloğunu el ile ekleyin, veya
- `MINIMAX_API_KEY`, `MINIMAX_OAUTH_TOKEN` veya bir MiniMax kimlik doğrulama profili ayarlayın;
  böylece eşleşen sağlayıcı eklenebilir.

Model kimliğinin **büyük/küçük harfe duyarlı** olduğundan emin olun:

- API anahtarı yolu: `minimax/MiniMax-M2.7` veya `minimax/MiniMax-M2.7-highspeed`
- OAuth yolu: `minimax-portal/MiniMax-M2.7` veya
  `minimax-portal/MiniMax-M2.7-highspeed`

Ardından tekrar şununla denetleyin:

```bash
openclaw models list
```
