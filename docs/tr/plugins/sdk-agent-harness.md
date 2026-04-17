---
read_when:
    - Gömülü ajan çalışma zamanını veya harness kayıt defterini değiştiriyorsunuz
    - Bir paketlenmiş veya güvenilir plugin'den bir ajan harness'i kaydediyorsunuz
    - Codex plugin'inin model sağlayıcılarla nasıl ilişkili olduğunu anlamanız gerekir
sidebarTitle: Agent Harness
summary: Düşük seviyeli gömülü ajan yürütücüsünü değiştiren plugin'ler için deneysel SDK yüzeyi
title: Ajan Harness Plugin'leri
x-i18n:
    generated_at: "2026-04-12T00:18:56Z"
    model: gpt-5.4
    provider: openai
    source_hash: 62b88fd24ce8b600179db27e16e8d764a2cd7a14e5c5df76374c33121aa5e365
    source_path: plugins/sdk-agent-harness.md
    workflow: 15
---

# Ajan Harness Plugin'leri

Bir **ajan harness'i**, hazırlanmış bir OpenClaw ajan dönüşü için düşük seviyeli yürütücüdür. Bir model sağlayıcısı, bir kanal veya bir araç kayıt defteri değildir.

Bu yüzeyi yalnızca paketlenmiş veya güvenilir yerel plugin'ler için kullanın. Sözleşme hâlâ deneyseldir çünkü parametre türleri kasıtlı olarak mevcut gömülü çalıştırıcıyı yansıtır.

## Bir harness ne zaman kullanılmalı

Bir model ailesinin kendine ait yerel oturum çalışma zamanı varsa ve normal OpenClaw sağlayıcı taşıması yanlış soyutlamaysa bir ajan harness'i kaydedin.

Örnekler:

- iş parçacıklarını ve sıkıştırmayı sahiplenen yerel bir kodlama ajanı sunucusu
- yerel plan/muhakeme/araç olaylarını akış olarak iletmesi gereken yerel bir CLI veya daemon
- OpenClaw oturum dökümüne ek olarak kendi devam kimliğine ihtiyaç duyan bir model çalışma zamanı

Yalnızca yeni bir LLM API eklemek için bir harness kaydetmeyin. Normal HTTP veya WebSocket model API'leri için bir [sağlayıcı plugin'i](/tr/plugins/sdk-provider-plugins) oluşturun.

## Çekirdeğin hâlâ sahip olduğu alanlar

Bir harness seçilmeden önce OpenClaw şunları zaten çözümlemiştir:

- sağlayıcı ve model
- çalışma zamanı kimlik doğrulama durumu
- düşünme seviyesi ve bağlam bütçesi
- OpenClaw döküm/oturum dosyası
- çalışma alanı, sandbox ve araç ilkesi
- kanal yanıt callback'leri ve akış callback'leri
- model fallback ve canlı model değiştirme ilkesi

Bu ayrım kasıtlıdır. Bir harness hazırlanmış bir denemeyi çalıştırır; sağlayıcı seçmez, kanal teslimatını değiştirmez veya modelleri sessizce değiştirmez.

## Bir harness kaydetme

**İçe aktarma:** `openclaw/plugin-sdk/agent-harness`

```typescript
import type { AgentHarness } from "openclaw/plugin-sdk/agent-harness";
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

const myHarness: AgentHarness = {
  id: "my-harness",
  label: "My native agent harness",

  supports(ctx) {
    return ctx.provider === "my-provider"
      ? { supported: true, priority: 100 }
      : { supported: false };
  },

  async runAttempt(params) {
    // Start or resume your native thread.
    // Use params.prompt, params.tools, params.images, params.onPartialReply,
    // params.onAgentEvent, and the other prepared attempt fields.
    return await runMyNativeTurn(params);
  },
};

export default definePluginEntry({
  id: "my-native-agent",
  name: "My Native Agent",
  description: "Runs selected models through a native agent daemon.",
  register(api) {
    api.registerAgentHarness(myHarness);
  },
});
```

## Seçim ilkesi

OpenClaw, sağlayıcı/model çözümlemesinden sonra bir harness seçer:

1. `OPENCLAW_AGENT_RUNTIME=<id>` bu kimliğe sahip kayıtlı bir harness'i zorlar.
2. `OPENCLAW_AGENT_RUNTIME=pi` yerleşik PI harness'ini zorlar.
3. `OPENCLAW_AGENT_RUNTIME=auto` kayıtlı harness'lere çözümlenen sağlayıcıyı/modeli destekleyip desteklemediklerini sorar.
4. Hiçbir kayıtlı harness eşleşmezse OpenClaw, PI fallback devre dışı bırakılmadıkça PI kullanır.

Zorlanan plugin harness hataları çalıştırma hataları olarak görünür. `auto` modunda OpenClaw, seçilen plugin harness bir dönüş yan etkileri üretmeden önce başarısız olursa PI'ye fallback yapabilir. Bunun yerine bu fallback'i kesin hata hâline getirmek için `OPENCLAW_AGENT_HARNESS_FALLBACK=none` veya `embeddedHarness.fallback: "none"` ayarlayın.

Paketlenmiş Codex plugin'i, harness kimliği olarak `codex` kaydeder. Çekirdek bunu sıradan bir plugin harness kimliği olarak değerlendirir; Codex'e özgü takma adlar paylaşılan çalışma zamanı seçicisinde değil, plugin'de veya operatör yapılandırmasında yer almalıdır.

## Sağlayıcı artı harness eşleştirmesi

Çoğu harness ayrıca bir sağlayıcı da kaydetmelidir. Sağlayıcı; model başvurularını, kimlik doğrulama durumunu, model meta verilerini ve `/model` seçimini OpenClaw'un geri kalanına görünür kılar. Harness daha sonra `supports(...)` içinde bu sağlayıcıyı sahiplenir.

Paketlenmiş Codex plugin'i bu düzeni izler:

- sağlayıcı kimliği: `codex`
- kullanıcı model başvuruları: `codex/gpt-5.4`, `codex/gpt-5.2` veya Codex uygulama sunucusunun döndürdüğü başka bir model
- harness kimliği: `codex`
- kimlik doğrulama: sentetik sağlayıcı kullanılabilirliği, çünkü Codex harness'i yerel Codex giriş/oturumunu sahiplenir
- uygulama sunucusu isteği: OpenClaw çıplak model kimliğini Codex'e gönderir ve harness'in yerel uygulama sunucusu protokolüyle konuşmasına izin verir

Codex plugin'i ekleyicidir. Düz `openai/gpt-*` başvuruları OpenAI sağlayıcı başvuruları olarak kalır ve normal OpenClaw sağlayıcı yolunu kullanmaya devam eder. Codex tarafından yönetilen kimlik doğrulama, Codex model keşfi, yerel iş parçacıkları ve Codex uygulama sunucusu yürütmesi istediğinizde `codex/gpt-*` seçin. `/model`, OpenAI sağlayıcı kimlik bilgileri gerektirmeden Codex uygulama sunucusunun döndürdüğü Codex modelleri arasında geçiş yapabilir.

Operatör kurulumu, model öneki örnekleri ve yalnızca Codex yapılandırmaları için bkz. [Codex Harness](/tr/plugins/codex-harness).

OpenClaw, Codex uygulama sunucusunun `0.118.0` veya daha yeni sürümünü gerektirir. Codex plugin'i, uygulama sunucusunun başlatma el sıkışmasını kontrol eder ve daha eski veya sürümlendirilmemiş sunucuları engeller; böylece OpenClaw yalnızca test edildiği protokol yüzeyine karşı çalışır.

### Yerel Codex harness modu

Paketlenmiş `codex` harness'i, gömülü OpenClaw ajan dönüşleri için yerel Codex modudur. Önce paketlenmiş `codex` plugin'ini etkinleştirin ve yapılandırmanız kısıtlayıcı bir izin listesi kullanıyorsa `plugins.allow` içine `codex` ekleyin. Bu, `openai-codex/*` ile farklıdır:

- `openai-codex/*`, normal OpenClaw sağlayıcı yolu üzerinden ChatGPT/Codex OAuth kullanır.
- `codex/*`, paketlenmiş Codex sağlayıcısını kullanır ve dönüşü Codex uygulama sunucusu üzerinden yönlendirir.

Bu mod çalıştığında yerel iş parçacığı kimliği, devam etme davranışı, sıkıştırma ve uygulama sunucusu yürütmesi Codex'in kontrolündedir. OpenClaw ise sohbet kanalına, görünür döküm yansıtmasına, araç ilkesine, onaylara, medya teslimine ve oturum seçimine sahip olmaya devam eder. Codex uygulama sunucusu yolunun kullanıldığını ve PI fallback'in bozuk bir yerel harness'i gizlemediğini kanıtlamanız gerektiğinde `embeddedHarness.runtime: "codex"` ile birlikte `embeddedHarness.fallback: "none"` kullanın.

## PI fallback'i devre dışı bırakma

Varsayılan olarak OpenClaw, gömülü ajanları `{ runtime: "auto", fallback: "pi" }` olarak ayarlanmış `agents.defaults.embeddedHarness` ile çalıştırır. `auto` modunda kayıtlı plugin harness'ler bir sağlayıcı/model çiftini sahiplenebilir. Hiçbiri eşleşmezse veya otomatik seçilen bir plugin harness çıktı üretmeden önce başarısız olursa OpenClaw PI'ye fallback yapar.

Bir plugin harness'in çalıştırılan tek çalışma zamanı olduğunu kanıtlamanız gerektiğinde `fallback: "none"` ayarlayın. Bu, otomatik PI fallback'ini devre dışı bırakır; açık bir `runtime: "pi"` veya `OPENCLAW_AGENT_RUNTIME=pi` kullanımını engellemez.

Yalnızca Codex gömülü çalıştırmaları için:

```json
{
  "agents": {
    "defaults": {
      "model": "codex/gpt-5.4",
      "embeddedHarness": {
        "runtime": "codex",
        "fallback": "none"
      }
    }
  }
}
```

Herhangi bir kayıtlı plugin harness'in eşleşen modelleri sahiplenmesini istiyor ancak OpenClaw'un sessizce PI'ye fallback yapmasını asla istemiyorsanız `runtime: "auto"` olarak bırakın ve fallback'i devre dışı bırakın:

```json
{
  "agents": {
    "defaults": {
      "embeddedHarness": {
        "runtime": "auto",
        "fallback": "none"
      }
    }
  }
}
```

Ajan başına geçersiz kılmalar aynı yapıyı kullanır:

```json
{
  "agents": {
    "defaults": {
      "embeddedHarness": {
        "runtime": "auto",
        "fallback": "pi"
      }
    },
    "list": [
      {
        "id": "codex-only",
        "model": "codex/gpt-5.4",
        "embeddedHarness": {
          "runtime": "codex",
          "fallback": "none"
        }
      }
    ]
  }
}
```

`OPENCLAW_AGENT_RUNTIME` yapılandırılmış çalışma zamanını hâlâ geçersiz kılar. Ortamdan PI fallback'ini devre dışı bırakmak için `OPENCLAW_AGENT_HARNESS_FALLBACK=none` kullanın.

```bash
OPENCLAW_AGENT_RUNTIME=codex \
OPENCLAW_AGENT_HARNESS_FALLBACK=none \
openclaw gateway run
```

Fallback devre dışıyken, istenen harness kayıtlı değilse, çözümlenen sağlayıcıyı/modeli desteklemiyorsa veya dönüş yan etkileri üretmeden önce başarısız olursa bir oturum erken başarısız olur. Bu, yalnızca Codex dağıtımları ve Codex uygulama sunucusu yolunun gerçekten kullanıldığını kanıtlaması gereken canlı testler için kasıtlıdır.

Bu ayar yalnızca gömülü ajan harness'ini kontrol eder. Görsel, video, müzik, TTS, PDF veya diğer sağlayıcıya özgü model yönlendirmelerini devre dışı bırakmaz.

## Yerel oturumlar ve döküm yansıtması

Bir harness yerel bir oturum kimliği, iş parçacığı kimliği veya daemon tarafı devam etme belirteci tutabilir. Bu bağı açıkça OpenClaw oturumuyla ilişkilendirilmiş olarak tutun ve kullanıcıya görünür asistan/araç çıktısını OpenClaw dökümüne yansıtmaya devam edin.

OpenClaw dökümü şu alanlar için uyumluluk katmanı olarak kalır:

- kanalda görünür oturum geçmişi
- döküm arama ve indeksleme
- sonraki bir dönüşte yerleşik PI harness'ine geri dönme
- genel `/new`, `/reset` ve oturum silme davranışı

Harness'iniz bir sidecar bağı saklıyorsa, sahip OpenClaw oturumu sıfırlandığında OpenClaw'un bunu temizleyebilmesi için `reset(...)` uygulayın.

## Araç ve medya sonuçları

Çekirdek OpenClaw araç listesini oluşturur ve bunu hazırlanmış denemeye geçirir. Bir harness dinamik bir araç çağrısı yürüttüğünde, kanal medyasını kendiniz göndermek yerine araç sonucunu harness sonuç şekli üzerinden geri döndürün.

Bu, metin, görsel, video, müzik, TTS, onay ve mesajlaşma aracı çıktılarını PI destekli çalıştırmalarla aynı teslim yolunda tutar.

## Mevcut sınırlamalar

- Genel içe aktarma yolu geneldir, ancak bazı deneme/sonuç türü takma adları uyumluluk için hâlâ `Pi` adlarını taşır.
- Üçüncü taraf harness kurulumu deneyseldir. Yerel bir oturum çalışma zamanına ihtiyaç duyana kadar sağlayıcı plugin'lerini tercih edin.
- Harness değiştirme dönüşler arasında desteklenir. Yerel araçlar, onaylar, asistan metni veya mesaj göndermeleri başladıktan sonra dönüşün ortasında harness değiştirmeyin.

## İlgili

- [SDK Genel Bakış](/tr/plugins/sdk-overview)
- [Çalışma Zamanı Yardımcıları](/tr/plugins/sdk-runtime)
- [Sağlayıcı Plugin'leri](/tr/plugins/sdk-provider-plugins)
- [Codex Harness](/tr/plugins/codex-harness)
- [Model Sağlayıcıları](/tr/concepts/model-providers)
