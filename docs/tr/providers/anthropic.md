---
read_when:
    - OpenClaw içinde Anthropic modellerini kullanmak istiyorsanız
summary: OpenClaw içinde Anthropic Claude'u API anahtarları veya Claude CLI ile kullanın
title: Anthropic
x-i18n:
    generated_at: "2026-04-07T08:48:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: 423928fd36c66729985208d4d3f53aff1f94f63b908df85072988bdc41d5cf46
    source_path: providers/anthropic.md
    workflow: 15
---

# Anthropic (Claude)

Anthropic, **Claude** model ailesini geliştirir ve API ile
Claude CLI üzerinden erişim sağlar. OpenClaw içinde hem Anthropic API anahtarları hem de
Claude CLI yeniden kullanımı desteklenir. Mevcut eski Anthropic token profilleri,
zaten yapılandırılmışlarsa çalışma zamanında hâlâ dikkate alınır.

<Warning>
Anthropic personeli bize OpenClaw tarzı Claude CLI kullanımına yeniden izin verildiğini söyledi; bu nedenle
Anthropic yeni bir politika yayımlamadığı sürece OpenClaw, Claude CLI yeniden kullanımını ve `claude -p` kullanımını
bu entegrasyon için onaylanmış kabul eder.

Uzun ömürlü gateway ana makineleri için Anthropic API anahtarları hâlâ en açık ve
en öngörülebilir üretim yoludur. Zaten ana makinede Claude CLI kullanıyorsanız,
OpenClaw bu oturumu doğrudan yeniden kullanabilir.

Anthropic'in mevcut herkese açık belgeleri:

- [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference)
- [Claude Agent SDK overview](https://platform.claude.com/docs/en/agent-sdk/overview)

- [Using Claude Code with your Pro or Max plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- [Using Claude Code with your Team or Enterprise plan](https://support.anthropic.com/en/articles/11845131-using-claude-code-with-your-team-or-enterprise-plan/)

En açık faturalandırma yolunu istiyorsanız bunun yerine bir Anthropic API anahtarı kullanın.
OpenClaw ayrıca [OpenAI
Codex](/tr/providers/openai), [Qwen Cloud Coding Plan](/tr/providers/qwen),
[MiniMax Coding Plan](/tr/providers/minimax) ve [Z.AI / GLM Coding
Plan](/tr/providers/glm) dahil olmak üzere başka abonelik tarzı seçenekleri de destekler.
</Warning>

## Seçenek A: Anthropic API anahtarı

**En iyisi:** standart API erişimi ve kullanıma dayalı faturalandırma.
API anahtarınızı Anthropic Console içinde oluşturun.

### CLI kurulumu

```bash
openclaw onboard
# choose: Anthropic API key

# or non-interactive
openclaw onboard --anthropic-api-key "$ANTHROPIC_API_KEY"
```

### Anthropic yapılandırma örneği

```json5
{
  env: { ANTHROPIC_API_KEY: "sk-ant-..." },
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## Thinking varsayılanları (Claude 4.6)

- Anthropic Claude 4.6 modelleri, açık bir thinking düzeyi ayarlanmadığında OpenClaw içinde varsayılan olarak `adaptive` thinking kullanır.
- Bunu mesaj başına (`/think:<level>`) veya model parametrelerinde geçersiz kılabilirsiniz:
  `agents.defaults.models["anthropic/<model>"].params.thinking`.
- İlgili Anthropic belgeleri:
  - [Adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking)
  - [Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)

## Hızlı mod (Anthropic API)

OpenClaw'ın paylaşılan `/fast` anahtarı, `api.anthropic.com` adresine gönderilen API anahtarı ve OAuth kimlik doğrulamalı istekler dahil, doğrudan herkese açık Anthropic trafiğini de destekler.

- `/fast on`, `service_tier: "auto"` değerine eşlenir
- `/fast off`, `service_tier: "standard_only"` değerine eşlenir
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

- OpenClaw, Anthropic hizmet katmanlarını yalnızca doğrudan `api.anthropic.com` istekleri için ekler. `anthropic/*` trafiğini bir proxy veya gateway üzerinden yönlendirirseniz `/fast`, `service_tier` değerine dokunmaz.
- Açık Anthropic `serviceTier` veya `service_tier` model parametreleri, ikisi birden ayarlandığında `/fast` varsayılanını geçersiz kılar.
- Anthropic, etkili katmanı yanıtta `usage.service_tier` altında bildirir. Priority Tier kapasitesi olmayan hesaplarda `service_tier: "auto"` yine de `standard` olarak çözümlenebilir.

## Prompt caching (Anthropic API)

OpenClaw, Anthropic'in prompt caching özelliğini destekler. Bu özellik **yalnızca API** içindir; eski Anthropic token kimlik doğrulaması önbellek ayarlarını dikkate almaz.

### Yapılandırma

Model yapılandırmanızda `cacheRetention` parametresini kullanın:

| Değer   | Önbellek Süresi | Açıklama                    |
| ------- | --------------- | --------------------------- |
| `none`  | Önbellek yok    | Prompt caching'i devre dışı bırak |
| `short` | 5 dakika        | API Key kimlik doğrulaması için varsayılan |
| `long`  | 1 saat          | Genişletilmiş önbellek      |

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

Anthropic API Key kimlik doğrulaması kullanılırken OpenClaw, tüm Anthropic modelleri için otomatik olarak `cacheRetention: "short"` (5 dakikalık önbellek) uygular. Bunu, yapılandırmanızda açıkça `cacheRetention` ayarlayarak geçersiz kılabilirsiniz.

### Ajan başına cacheRetention geçersiz kılmaları

Temel olarak model düzeyi parametreleri kullanın, ardından belirli ajanları `agents.list[].params` üzerinden geçersiz kılın.

```json5
{
  agents: {
    defaults: {
      model: { primary: "anthropic/claude-opus-4-6" },
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" }, // çoğu ajan için temel ayar
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

Bu, aynı modeli kullanan bir ajanın uzun ömürlü önbellek tutmasına izin verirken, başka bir ajanın ani/düşük yeniden kullanım trafiğinde yazma maliyetlerinden kaçınmak için önbelleği devre dışı bırakmasını sağlar.

### Bedrock Claude notları

- Bedrock üzerindeki Anthropic Claude modelleri (`amazon-bedrock/*anthropic.claude*`), yapılandırıldığında `cacheRetention` geçişini kabul eder.
- Anthropic olmayan Bedrock modelleri çalışma zamanında zorla `cacheRetention: "none"` olarak ayarlanır.
- Açık değer ayarlanmadığında Anthropic API anahtarı akıllı varsayılanları, Claude-on-Bedrock model başvuruları için de `cacheRetention: "short"` değerini başlatır.

## 1M bağlam penceresi (Anthropic beta)

Anthropic'in 1M bağlam penceresi beta geçitlidir. OpenClaw içinde bunu desteklenen
Opus/Sonnet modelleri için model başına `params.context1m: true` ile etkinleştirin.

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

OpenClaw bunu Anthropic isteklerinde
`anthropic-beta: context-1m-2025-08-07` değerine eşler.

Bu yalnızca ilgili model için `params.context1m` açıkça `true` olarak ayarlandığında etkinleşir.

Gereklilik: Anthropic, o kimlik bilgisi için uzun bağlam kullanımına izin vermelidir.

Not: Anthropic şu anda eski Anthropic token kimlik doğrulaması (`sk-ant-oat-*`) kullanıldığında
`context-1m-*` beta isteklerini reddeder. Bu eski kimlik doğrulama moduyla
`context1m: true` yapılandırırsanız OpenClaw bir uyarı kaydeder ve
gerekli OAuth betalarını koruyup context1m beta
başlığını atlayarak standart bağlam penceresine geri döner.

## Claude CLI backend

Paketlenmiş Anthropic `claude-cli` backend'i OpenClaw içinde desteklenir.

- Anthropic personeli bize bu kullanıma yeniden izin verildiğini söyledi.
- Bu nedenle OpenClaw, Anthropic yeni bir politika yayımlamadığı sürece
  Claude CLI yeniden kullanımını ve `claude -p` kullanımını
  bu entegrasyon için onaylanmış kabul eder.
- Anthropic API anahtarları, her zaman açık gateway
  ana makineleri ve açık sunucu tarafı faturalandırma denetimi için en açık üretim yolu olmaya devam eder.
- Kurulum ve çalışma zamanı ayrıntıları [/gateway/cli-backends](/tr/gateway/cli-backends) içindedir.

## Notlar

- Anthropic'in herkese açık Claude Code belgeleri hâlâ
  `claude -p` gibi doğrudan CLI kullanımını belgeliyor ve Anthropic personeli bize OpenClaw tarzı Claude CLI kullanımına
  yeniden izin verildiğini söyledi. Anthropic
  yeni bir politika değişikliği yayımlamadığı sürece bu yönlendirmeyi yerleşmiş kabul ediyoruz.
- Anthropic setup-token, OpenClaw içinde desteklenen bir token-auth yolu olarak kullanılmaya devam eder, ancak OpenClaw artık mümkün olduğunda Claude CLI yeniden kullanımını ve `claude -p` kullanımını tercih eder.
- Kimlik doğrulama ayrıntıları + yeniden kullanım kuralları [/concepts/oauth](/tr/concepts/oauth) içindedir.

## Sorun giderme

**401 hataları / token aniden geçersiz**

- Anthropic token kimlik doğrulaması süresi dolabilir veya iptal edilebilir.
- Yeni kurulumlar için Anthropic API anahtarına geçin.

**Provider "anthropic" için API anahtarı bulunamadı**

- Kimlik doğrulama **ajan başınadır**. Yeni ajanlar ana ajanın anahtarlarını devralmaz.
- O ajan için onboarding'i yeniden çalıştırın veya gateway
  ana makinesinde bir API anahtarı yapılandırın, ardından `openclaw models status` ile doğrulayın.

**`anthropic:default` profili için kimlik bilgisi bulunamadı**

- Hangi auth profilinin etkin olduğunu görmek için `openclaw models status` çalıştırın.
- Onboarding'i yeniden çalıştırın veya o profil yolu için bir API anahtarı yapılandırın.

**Kullanılabilir auth profili yok (hepsi cooldown/unavailable durumunda)**

- `auth.unusableProfiles` değerini görmek için `openclaw models status --json` komutunu kontrol edin.
- Anthropic rate-limit cooldown'ları model kapsamlı olabilir; bu nedenle geçerli model cooldown durumundayken kardeş bir Anthropic
  modeli hâlâ kullanılabilir olabilir.
- Başka bir Anthropic profili ekleyin veya cooldown süresinin dolmasını bekleyin.

Daha fazlası: [/gateway/troubleshooting](/tr/gateway/troubleshooting) ve [/help/faq](/tr/help/faq).
