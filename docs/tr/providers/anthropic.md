---
read_when:
    - OpenClaw içinde Anthropic modellerini kullanmak istiyorsunuz
summary: OpenClaw içinde API anahtarlarıyla Anthropic Claude kullanın
title: Anthropic
x-i18n:
    generated_at: "2026-04-06T03:10:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: bbc6c4938674aedf20ff944bc04e742c9a7e77a5ff10ae4f95b5718504c57c2d
    source_path: providers/anthropic.md
    workflow: 15
---

# Anthropic (Claude)

Anthropic, **Claude** model ailesini geliştirir ve bir API üzerinden erişim sağlar.
OpenClaw içinde yeni Anthropic kurulumu bir API anahtarı kullanmalıdır. Mevcut eski
Anthropic token profilleri zaten yapılandırılmışlarsa çalışma zamanında hâlâ
desteklenir.

<Warning>
OpenClaw içinde Anthropic için faturalama ayrımı şöyledir:

- **Anthropic API anahtarı**: normal Anthropic API faturalaması.
- **OpenClaw içindeki Claude abonelik kimlik doğrulaması**: Anthropic, OpenClaw kullanıcılarına
  **4 Nisan 2026, 12:00 PT / 20:00 BST** tarihinde bunun
  üçüncü taraf harness kullanımı sayıldığını ve **Extra Usage** gerektirdiğini söyledi (kullandıkça öde,
  abonelikten ayrı faturalandırılır).

Yerel yeniden üretimlerimiz bu ayrımı doğruluyor:

- doğrudan `claude -p` yine çalışabilir
- `claude -p --append-system-prompt ...`, istem OpenClaw'ı tanımladığında
  Extra Usage korumasını tetikleyebilir
- aynı OpenClaw benzeri system prompt,
  Anthropic SDK + `ANTHROPIC_API_KEY` yolunda bu engeli **yeniden üretmez**

Bu nedenle pratik kural şudur: **Anthropic API anahtarı veya Extra Usage ile Claude aboneliği**.
En net üretim yolunu istiyorsanız bir Anthropic API
anahtarı kullanın.

Anthropic'in güncel herkese açık belgeleri:

- [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference)
- [Claude Agent SDK overview](https://platform.claude.com/docs/en/agent-sdk/overview)

- [Using Claude Code with your Pro or Max plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- [Using Claude Code with your Team or Enterprise plan](https://support.anthropic.com/en/articles/11845131-using-claude-code-with-your-team-or-enterprise-plan/)

En net faturalama yolunu istiyorsanız bunun yerine bir Anthropic API anahtarı kullanın.
OpenClaw ayrıca [OpenAI
Codex](/tr/providers/openai), [Qwen Cloud Coding Plan](/tr/providers/qwen),
[MiniMax Coding Plan](/tr/providers/minimax) ve [Z.AI / GLM Coding
Plan](/tr/providers/glm) dahil diğer abonelik tarzı seçenekleri de destekler.
</Warning>

## Seçenek A: Anthropic API anahtarı

**En uygunu:** standart API erişimi ve kullanıma dayalı faturalama.
API anahtarınızı Anthropic Console içinde oluşturun.

### CLI kurulumu

```bash
openclaw onboard
# choose: Anthropic API key

# or non-interactive
openclaw onboard --anthropic-api-key "$ANTHROPIC_API_KEY"
```

### Anthropic yapılandırma parçacığı

```json5
{
  env: { ANTHROPIC_API_KEY: "sk-ant-..." },
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## Thinking varsayılanları (Claude 4.6)

- Anthropic Claude 4.6 modelleri, açık bir thinking düzeyi ayarlanmadığında OpenClaw içinde varsayılan olarak `adaptive` thinking kullanır.
- Mesaj başına (`/think:<level>`) veya model parametrelerinde bunu geçersiz kılabilirsiniz:
  `agents.defaults.models["anthropic/<model>"].params.thinking`.
- İlgili Anthropic belgeleri:
  - [Adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking)
  - [Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)

## Hızlı mod (Anthropic API)

OpenClaw'ın paylaşılan `/fast` anahtarı, `api.anthropic.com` adresine gönderilen API anahtarı ve OAuth ile kimliği doğrulanmış istekler dahil doğrudan herkese açık Anthropic trafiğini de destekler.

- `/fast on`, `service_tier: "auto"` ile eşlenir
- `/fast off`, `service_tier: "standard_only"` ile eşlenir
- Yapılandırma varsayılanı:

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-sonnet-4-6": {
          params: { fastMode: true },
        },
      },
    },
  },
}
```

Önemli sınırlar:

- OpenClaw, Anthropic hizmet katmanlarını yalnızca doğrudan `api.anthropic.com` istekleri için ekler. `anthropic/*` trafiğini bir proxy veya gateway üzerinden yönlendirirseniz, `/fast` `service_tier` değerini değiştirmez.
- Açık Anthropic `serviceTier` veya `service_tier` model parametreleri, ikisi birden ayarlandığında `/fast` varsayılanını geçersiz kılar.
- Anthropic, etkin katmanı yanıtta `usage.service_tier` altında bildirir. Priority Tier kapasitesi olmayan hesaplarda `service_tier: "auto"` yine de `standard` olarak çözümlenebilir.

## Prompt caching (Anthropic API)

OpenClaw, Anthropic'in prompt caching özelliğini destekler. Bu **yalnızca API** içindir; eski Anthropic token kimlik doğrulaması önbellek ayarlarına uymaz.

### Yapılandırma

Model yapılandırmanızda `cacheRetention` parametresini kullanın:

| Değer   | Önbellek Süresi | Açıklama                          |
| ------- | --------------- | --------------------------------- |
| `none`  | Önbellek yok    | Prompt caching devre dışı         |
| `short` | 5 dakika        | API anahtarı kimlik doğrulaması için varsayılan |
| `long`  | 1 saat          | Genişletilmiş önbellek            |

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" },
        },
      },
    },
  },
}
```

### Varsayılanlar

Anthropic API anahtarı kimlik doğrulaması kullanılırken, OpenClaw tüm Anthropic modelleri için otomatik olarak `cacheRetention: "short"` (5 dakikalık önbellek) uygular. Bunu, yapılandırmanızda açıkça `cacheRetention` ayarlayarak geçersiz kılabilirsiniz.

### Ajan başına cacheRetention geçersiz kılmaları

Model düzeyi parametrelerini temeliniz olarak kullanın, ardından belirli ajanları `agents.list[].params` ile geçersiz kılın.

```json5
{
  agents: {
    defaults: {
      model: { primary: "anthropic/claude-opus-4-6" },
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" }, // çoğu ajan için temel
        },
      },
    },
    list: [
      { id: "research", default: true },
      { id: "alerts", params: { cacheRetention: "none" } }, // yalnızca bu ajan için geçersiz kıl
    ],
  },
}
```

Önbellekle ilgili parametreler için yapılandırma birleştirme sırası:

1. `agents.defaults.models["provider/model"].params`
2. `agents.list[].params` (`id` eşleşirse, anahtar bazında geçersiz kılar)

Bu, bir ajanın uzun ömürlü bir önbelleği korurken aynı modeldeki başka bir ajanın, patlamalı/düşük yeniden kullanım trafiğinde yazma maliyetlerini önlemek için önbelleği devre dışı bırakmasına olanak tanır.

### Bedrock Claude notları

- Bedrock üzerindeki Anthropic Claude modelleri (`amazon-bedrock/*anthropic.claude*`), yapılandırıldığında `cacheRetention` geçişini kabul eder.
- Anthropic olmayan Bedrock modelleri çalışma zamanında zorunlu olarak `cacheRetention: "none"` olur.
- Anthropic API anahtarı akıllı varsayılanları, açık bir değer ayarlanmadığında Claude-on-Bedrock model başvuruları için de `cacheRetention: "short"` atar.

## 1M bağlam penceresi (Anthropic beta)

Anthropic'in 1M bağlam penceresi beta kapılıdır. OpenClaw içinde bunu
desteklenen Opus/Sonnet modelleri için model başına `params.context1m: true`
ile etkinleştirin.

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { context1m: true },
        },
      },
    },
  },
}
```

OpenClaw bunu Anthropic
isteklerinde `anthropic-beta: context-1m-2025-08-07` olarak eşler.

Bu yalnızca ilgili model için `params.context1m` açıkça `true` olarak ayarlandığında
etkinleşir.

Gereksinim: Anthropic bu kimlik bilgisi üzerinde uzun bağlam kullanımına izin vermelidir
(genellikle API anahtarı faturalaması veya OpenClaw'ın Claude-login yolu / Extra Usage etkin
eski token kimlik doğrulaması). Aksi halde Anthropic şu hatayı döndürür:
`HTTP 429: rate_limit_error: Extra usage is required for long context requests`.

Not: Anthropic şu anda eski Anthropic token kimlik doğrulaması (`sk-ant-oat-*`) kullanılırken
`context-1m-*` beta isteklerini reddeder. Bu eski kimlik doğrulama modu ile
`context1m: true` yapılandırırsanız, OpenClaw bir uyarı günlüğe kaydeder ve
gerekli OAuth betalarını korurken context1m beta
başlığını atlayarak standart bağlam penceresine geri döner.

## Kaldırıldı: Claude CLI arka ucu

Paketlenmiş Anthropic `claude-cli` arka ucu kaldırıldı.

- Anthropic'in 4 Nisan 2026 tarihli bildirimi, OpenClaw tarafından yönlendirilen Claude-login trafiğinin
  üçüncü taraf harness kullanımı olduğunu ve **Extra Usage** gerektirdiğini söylüyor.
- Yerel yeniden üretimlerimiz de doğrudan
  `claude -p --append-system-prompt ...` komutunun, eklenen
  istem OpenClaw'ı tanımladığında aynı korumaya takılabildiğini gösteriyor.
- Aynı OpenClaw benzeri system prompt,
  Anthropic SDK + `ANTHROPIC_API_KEY` yolunda bu korumaya takılmaz.
- OpenClaw içinde Anthropic trafiği için Anthropic API anahtarları kullanın.

## Notlar

- Anthropic'in herkese açık Claude Code belgeleri hâlâ
  `claude -p` gibi doğrudan CLI kullanımını belgeliyor, ancak Anthropic'in OpenClaw kullanıcılarına yönelik ayrı bildirimi,
  **OpenClaw** Claude-login yolunun üçüncü taraf harness kullanımı olduğunu ve
  **Extra Usage** gerektirdiğini söylüyor (abonelikten ayrı kullandıkça öde faturalaması).
  Yerel yeniden üretimlerimiz ayrıca doğrudan
  `claude -p --append-system-prompt ...` komutunun, eklenen
  istem OpenClaw'ı tanımladığında aynı korumaya takılabildiğini, aynı istem biçiminin ise
  Anthropic SDK + `ANTHROPIC_API_KEY` yolunda yeniden üretilemediğini gösteriyor. Üretim için
  bunun yerine Anthropic API anahtarlarını öneriyoruz.
- Anthropic setup-token, OpenClaw içinde eski/manuel bir yol olarak yeniden kullanılabilir durumdadır. Anthropic'in OpenClaw'a özgü faturalama bildirimi hâlâ geçerlidir, bu nedenle bu yolu Anthropic'in **Extra Usage** gerektirdiği beklentisiyle kullanın.
- Kimlik doğrulama ayrıntıları + yeniden kullanım kuralları [/concepts/oauth](/tr/concepts/oauth) içinde yer alır.

## Sorun giderme

**401 hataları / token aniden geçersiz**

- Eski Anthropic token kimlik doğrulaması süresi dolabilir veya iptal edilebilir.
- Yeni kurulumlar için bir Anthropic API anahtarına geçin.

**"anthropic" sağlayıcısı için API anahtarı bulunamadı**

- Kimlik doğrulama **ajan başınadır**. Yeni ajanlar ana ajanın anahtarlarını devralmaz.
- O ajan için onboarding'i yeniden çalıştırın veya gateway
  host üzerinde bir API anahtarı yapılandırın, sonra `openclaw models status` ile doğrulayın.

**`anthropic:default` profili için kimlik bilgisi bulunamadı**

- Hangi kimlik doğrulama profilinin etkin olduğunu görmek için `openclaw models status` komutunu çalıştırın.
- Onboarding'i yeniden çalıştırın veya o profil yolu için bir API anahtarı yapılandırın.

**Kullanılabilir kimlik doğrulama profili yok (tamamı cooldown/unavailable durumda)**

- `auth.unusableProfiles` için `openclaw models status --json` çıktısını kontrol edin.
- Anthropic hız sınırı cooldown'ları model kapsamlı olabilir; bu nedenle mevcut model cooldown durumundayken kardeş bir Anthropic
  modeli yine kullanılabilir olabilir.
- Başka bir Anthropic profili ekleyin veya cooldown süresinin dolmasını bekleyin.

Daha fazlası: [/gateway/troubleshooting](/tr/gateway/troubleshooting) ve [/help/faq](/tr/help/faq).
