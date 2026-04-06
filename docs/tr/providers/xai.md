---
read_when:
    - OpenClaw içinde Grok modellerini kullanmak istiyorsunuz
    - xAI kimlik doğrulamasını veya model kimliklerini yapılandırıyorsunuz
summary: OpenClaw içinde xAI Grok modellerini kullanın
title: xAI
x-i18n:
    generated_at: "2026-04-06T03:12:07Z"
    model: gpt-5.4
    provider: openai
    source_hash: 64bc899655427cc10bdc759171c7d1ec25ad9f1e4f9d803f1553d3d586c6d71d
    source_path: providers/xai.md
    workflow: 15
---

# xAI

OpenClaw, Grok modelleri için paketlenmiş bir `xai` sağlayıcı eklentisiyle gelir.

## Kurulum

1. xAI konsolunda bir API anahtarı oluşturun.
2. `XAI_API_KEY` ayarlayın veya şunu çalıştırın:

```bash
openclaw onboard --auth-choice xai-api-key
```

3. Şunun gibi bir model seçin:

```json5
{
  agents: { defaults: { model: { primary: "xai/grok-4" } } },
}
```

OpenClaw artık paketlenmiş xAI taşıma katmanı olarak xAI Responses API'yi kullanır. Aynı
`XAI_API_KEY`, Grok destekli `web_search`, birinci sınıf `x_search`
ve uzak `code_execution` için de kullanılabilir.
Bir xAI anahtarını `plugins.entries.xai.config.webSearch.apiKey` altında saklarsanız,
paketlenmiş xAI model sağlayıcısı artık bu anahtarı fallback olarak da yeniden kullanır.
`code_execution` ayarı `plugins.entries.xai.config.codeExecution` altında bulunur.

## Mevcut paketlenmiş model kataloğu

OpenClaw artık varsayılan olarak şu xAI model ailelerini içerir:

- `grok-3`, `grok-3-fast`, `grok-3-mini`, `grok-3-mini-fast`
- `grok-4`, `grok-4-0709`
- `grok-4-fast`, `grok-4-fast-non-reasoning`
- `grok-4-1-fast`, `grok-4-1-fast-non-reasoning`
- `grok-4.20-beta-latest-reasoning`, `grok-4.20-beta-latest-non-reasoning`
- `grok-code-fast-1`

Eklenti ayrıca aynı API biçimini izlediklerinde daha yeni `grok-4*` ve `grok-code-fast*` kimliklerini de ileri çözümleme ile destekler.

Hızlı model notları:

- `grok-4-fast`, `grok-4-1-fast` ve `grok-4.20-beta-*` varyantları,
  paketlenmiş katalogdaki mevcut görsel destekli Grok başvurularıdır.
- `/fast on` veya `agents.defaults.models["xai/<model>"].params.fastMode: true`
  yerel xAI isteklerini şu şekilde yeniden yazar:
  - `grok-3` -> `grok-3-fast`
  - `grok-3-mini` -> `grok-3-mini-fast`
  - `grok-4` -> `grok-4-fast`
  - `grok-4-0709` -> `grok-4-fast`

Eski uyumluluk takma adları hâlâ kanonik paketlenmiş kimliklere normalize edilir. Örneğin:

- `grok-4-fast-reasoning` -> `grok-4-fast`
- `grok-4-1-fast-reasoning` -> `grok-4-1-fast`
- `grok-4.20-reasoning` -> `grok-4.20-beta-latest-reasoning`
- `grok-4.20-non-reasoning` -> `grok-4.20-beta-latest-non-reasoning`

## Web arama

Paketlenmiş `grok` web arama sağlayıcısı da `XAI_API_KEY` kullanır:

```bash
openclaw config set tools.web.search.provider grok
```

## Video üretimi

Paketlenmiş `xai` eklentisi ayrıca paylaşılan
`video_generate` aracı üzerinden video generation da kaydeder.

- Varsayılan video modeli: `xai/grok-imagine-video`
- Modlar: text-to-video, image-to-video ve uzak video düzenleme/uzatma akışları
- `aspectRatio` ve `resolution` desteklenir
- Mevcut sınır: yerel video arabellekleri kabul edilmez; video referansı/düzenleme girdileri için uzak `http(s)`
  URL'leri kullanın

xAI'ı varsayılan video sağlayıcısı olarak kullanmak için:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "xai/grok-imagine-video",
      },
    },
  },
}
```

Paylaşılan araç
parametreleri, sağlayıcı seçimi ve failover davranışı için [Video Generation](/tools/video-generation) bölümüne bakın.

## Bilinen sınırlamalar

- Kimlik doğrulama bugün yalnızca API anahtarıyla yapılır. OpenClaw içinde henüz xAI OAuth/device-code akışı yoktur.
- `grok-4.20-multi-agent-experimental-beta-0304`, standart OpenClaw xAI taşıma katmanından farklı bir upstream API yüzeyi gerektirdiği için normal xAI sağlayıcı yolunda desteklenmez.

## Notlar

- OpenClaw, paylaşılan çalıştırıcı yolunda xAI'ye özgü araç şeması ve araç çağrısı uyumluluk düzeltmelerini otomatik olarak uygular.
- Yerel xAI istekleri varsayılan olarak `tool_stream: true` kullanır. Bunu
  devre dışı bırakmak için `agents.defaults.models["xai/<model>"].params.tool_stream` değerini `false` yapın.
- Paketlenmiş xAI sarmalayıcısı, yerel xAI isteklerini göndermeden önce desteklenmeyen katı araç şeması bayraklarını ve
  reasoning payload anahtarlarını kaldırır.
- `web_search`, `x_search` ve `code_execution`, OpenClaw araçları olarak sunulur. OpenClaw, her sohbet turuna tüm yerel araçları eklemek yerine her araç isteği içinde ihtiyaç duyduğu belirli xAI yerleşik özelliğini etkinleştirir.
- `x_search` ve `code_execution`, çekirdek model çalışma zamanına sabit kodlanmak yerine paketlenmiş xAI eklentisine aittir.
- `code_execution`, yerel [`exec`](/tr/tools/exec) değil, uzak xAI sandbox yürütmesidir.
- Daha geniş sağlayıcı genel görünümü için [Model providers](/tr/providers/index) bölümüne bakın.
