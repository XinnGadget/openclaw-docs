---
read_when:
    - Yeni bir OpenClaw plugin'i oluşturmak istiyorsunuz
    - Plugin geliştirme için hızlı bir başlangıca ihtiyacınız var
    - OpenClaw'a yeni bir kanal, sağlayıcı, araç veya başka bir yetenek ekliyorsunuz
sidebarTitle: Getting Started
summary: İlk OpenClaw plugin'inizi dakikalar içinde oluşturun
title: Plugin Geliştirme
x-i18n:
    generated_at: "2026-04-06T03:09:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9be344cb300ecbcba08e593a95bcc93ab16c14b28a0ff0c29b26b79d8249146c
    source_path: plugins/building-plugins.md
    workflow: 15
---

# Plugin Geliştirme

Plugin'ler, OpenClaw'ı yeni yeteneklerle genişletir: kanallar, model sağlayıcıları,
konuşma, gerçek zamanlı transkripsiyon, gerçek zamanlı ses, medya anlama, görsel
oluşturma, video oluşturma, web getirme, web arama, agent araçları veya
bunların herhangi bir birleşimi.

Plugin'inizi OpenClaw deposuna eklemeniz gerekmez. Şuraya yayımlayın:
[ClawHub](/tr/tools/clawhub) veya npm, kullanıcılar da
`openclaw plugins install <package-name>` ile kurar. OpenClaw önce ClawHub'ı dener ve
ardından otomatik olarak npm'ye geri döner.

## Önkoşullar

- Node >= 22 ve bir paket yöneticisi (npm veya pnpm)
- TypeScript (ESM) konusunda aşinalık
- Depo içi plugin'ler için: deponun klonlanmış ve `pnpm install` işleminin yapılmış olması

## Ne tür bir plugin?

<CardGroup cols={3}>
  <Card title="Kanal plugin'i" icon="messages-square" href="/tr/plugins/sdk-channel-plugins">
    OpenClaw'ı bir mesajlaşma platformuna bağlayın (Discord, IRC vb.)
  </Card>
  <Card title="Sağlayıcı plugin'i" icon="cpu" href="/tr/plugins/sdk-provider-plugins">
    Bir model sağlayıcısı ekleyin (LLM, proxy veya özel uç nokta)
  </Card>
  <Card title="Araç / hook plugin'i" icon="wrench">
    Agent araçları, olay hook'ları veya hizmetler kaydedin — aşağıdan devam edin
  </Card>
</CardGroup>

Bir kanal plugin'i isteğe bağlıysa ve onboarding/kurulum çalıştığında
kurulu olmayabilecekse,
`openclaw/plugin-sdk/channel-setup` içinden `createOptionalChannelSetupSurface(...)` kullanın. Bu,
kurulum gereksinimini bildiren ve plugin kurulana kadar gerçek yapılandırma yazımlarında
kapalı kalacak şekilde başarısız olan bir kurulum bağdaştırıcısı + sihirbaz çifti üretir.

## Hızlı başlangıç: araç plugin'i

Bu rehber, bir agent aracı kaydeden minimal bir plugin oluşturur. Kanal
ve sağlayıcı plugin'leri için yukarıda bağlantısı verilen özel kılavuzlar vardır.

<Steps>
  <Step title="Paket ve manifest dosyasını oluşturun">
    <CodeGroup>
    ```json package.json
    {
      "name": "@myorg/openclaw-my-plugin",
      "version": "1.0.0",
      "type": "module",
      "openclaw": {
        "extensions": ["./index.ts"],
        "compat": {
          "pluginApi": ">=2026.3.24-beta.2",
          "minGatewayVersion": "2026.3.24-beta.2"
        },
        "build": {
          "openclawVersion": "2026.3.24-beta.2",
          "pluginSdkVersion": "2026.3.24-beta.2"
        }
      }
    }
    ```

    ```json openclaw.plugin.json
    {
      "id": "my-plugin",
      "name": "My Plugin",
      "description": "Adds a custom tool to OpenClaw",
      "configSchema": {
        "type": "object",
        "additionalProperties": false
      }
    }
    ```
    </CodeGroup>

    Her plugin'in, yapılandırması olmasa bile bir manifest dosyasına ihtiyacı vardır. Tam
    şema için [Manifest](/tr/plugins/manifest) sayfasına bakın. Kanonik ClawHub
    yayımlama parçacıkları `docs/snippets/plugin-publish/` içinde bulunur.

  </Step>

  <Step title="Giriş noktasını yazın">

    ```typescript
    // index.ts
    import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
    import { Type } from "@sinclair/typebox";

    export default definePluginEntry({
      id: "my-plugin",
      name: "My Plugin",
      description: "Adds a custom tool to OpenClaw",
      register(api) {
        api.registerTool({
          name: "my_tool",
          description: "Do a thing",
          parameters: Type.Object({ input: Type.String() }),
          async execute(_id, params) {
            return { content: [{ type: "text", text: `Got: ${params.input}` }] };
          },
        });
      },
    });
    ```

    `definePluginEntry`, kanal dışı plugin'ler içindir. Kanallar için
    `defineChannelPluginEntry` kullanın — bkz. [Kanal Plugin'leri](/tr/plugins/sdk-channel-plugins).
    Tam giriş noktası seçenekleri için bkz. [Giriş Noktaları](/tr/plugins/sdk-entrypoints).

  </Step>

  <Step title="Test edin ve yayımlayın">

    **Harici plugin'ler:** ClawHub ile doğrulayın ve yayımlayın, ardından kurun:

    ```bash
    clawhub package publish your-org/your-plugin --dry-run
    clawhub package publish your-org/your-plugin
    openclaw plugins install clawhub:@myorg/openclaw-my-plugin
    ```

    OpenClaw ayrıca
    `@myorg/openclaw-my-plugin` gibi çıplak paket tanımları için npm'den önce ClawHub'ı denetler.

    **Depo içi plugin'ler:** paketlenmiş plugin çalışma alanı ağacının altına yerleştirin — otomatik olarak keşfedilir.

    ```bash
    pnpm test -- <bundled-plugin-root>/my-plugin/
    ```

  </Step>
</Steps>

## Plugin yetenekleri

Tek bir plugin, `api` nesnesi üzerinden istediği sayıda yetenek kaydedebilir:

| Yetenek               | Kayıt yöntemi                                   | Ayrıntılı kılavuz                                                                 |
| --------------------- | ------------------------------------------------ | --------------------------------------------------------------------------------- |
| Metin çıkarımı (LLM)  | `api.registerProvider(...)`                      | [Sağlayıcı Plugin'leri](/tr/plugins/sdk-provider-plugins)                            |
| Kanal / mesajlaşma    | `api.registerChannel(...)`                       | [Kanal Plugin'leri](/tr/plugins/sdk-channel-plugins)                                 |
| Konuşma (TTS/STT)     | `api.registerSpeechProvider(...)`                | [Sağlayıcı Plugin'leri](/tr/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Gerçek zamanlı transkripsiyon | `api.registerRealtimeTranscriptionProvider(...)` | [Sağlayıcı Plugin'leri](/tr/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Gerçek zamanlı ses    | `api.registerRealtimeVoiceProvider(...)`         | [Sağlayıcı Plugin'leri](/tr/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Medya anlama          | `api.registerMediaUnderstandingProvider(...)`    | [Sağlayıcı Plugin'leri](/tr/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Görsel oluşturma      | `api.registerImageGenerationProvider(...)`       | [Sağlayıcı Plugin'leri](/tr/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Müzik oluşturma       | `api.registerMusicGenerationProvider(...)`       | [Sağlayıcı Plugin'leri](/tr/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Video oluşturma       | `api.registerVideoGenerationProvider(...)`       | [Sağlayıcı Plugin'leri](/tr/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Web getirme           | `api.registerWebFetchProvider(...)`              | [Sağlayıcı Plugin'leri](/tr/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Web arama             | `api.registerWebSearchProvider(...)`             | [Sağlayıcı Plugin'leri](/tr/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Agent araçları        | `api.registerTool(...)`                          | Aşağıda                                                                            |
| Özel komutlar         | `api.registerCommand(...)`                       | [Giriş Noktaları](/tr/plugins/sdk-entrypoints)                                        |
| Olay hook'ları        | `api.registerHook(...)`                          | [Giriş Noktaları](/tr/plugins/sdk-entrypoints)                                        |
| HTTP rotaları         | `api.registerHttpRoute(...)`                     | [Dahili Yapı](/tr/plugins/architecture#gateway-http-routes)                           |
| CLI alt komutları     | `api.registerCli(...)`                           | [Giriş Noktaları](/tr/plugins/sdk-entrypoints)                                        |

Tam kayıt API'si için bkz. [SDK Overview](/tr/plugins/sdk-overview#registration-api).

Plugin'iniz özel gateway RPC yöntemleri kaydediyorsa, bunları
plugin'e özgü bir ön ek altında tutun. Çekirdek yönetici ad alanları (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) ayrılmıştır ve bir plugin daha dar bir kapsam istese bile her zaman
`operator.admin` olarak çözülür.

Aklınızda bulundurmanız gereken hook guard semantiği:

- `before_tool_call`: `{ block: true }` terminaldir ve daha düşük öncelikli işleyicileri durdurur.
- `before_tool_call`: `{ block: false }` karar verilmemiş olarak ele alınır.
- `before_tool_call`: `{ requireApproval: true }` agent yürütmesini duraklatır ve kullanıcıdan exec onay katmanı, Telegram düğmeleri, Discord etkileşimleri veya herhangi bir kanalda `/approve` komutu üzerinden onay ister.
- `before_install`: `{ block: true }` terminaldir ve daha düşük öncelikli işleyicileri durdurur.
- `before_install`: `{ block: false }` karar verilmemiş olarak ele alınır.
- `message_sending`: `{ cancel: true }` terminaldir ve daha düşük öncelikli işleyicileri durdurur.
- `message_sending`: `{ cancel: false }` karar verilmemiş olarak ele alınır.

`/approve` komutu hem exec hem de plugin onaylarını sınırlı geri dönüş ile işler: bir exec onay kimliği bulunamadığında, OpenClaw aynı kimliği plugin onayları üzerinden yeniden dener. Plugin onayı yönlendirmesi yapılandırmada `approvals.plugin` üzerinden bağımsız olarak yapılandırılabilir.

Özel onay altyapınızın aynı sınırlı geri dönüş durumunu algılaması gerekiyorsa,
onay süresi dolma dizelerini el ile eşleştirmek yerine
`openclaw/plugin-sdk/error-runtime` içinden `isApprovalNotFoundError` kullanın.

Ayrıntılar için bkz. [SDK Overview hook decision semantics](/tr/plugins/sdk-overview#hook-decision-semantics).

## Agent araçlarını kaydetme

Araçlar, LLM'nin çağırabildiği türlendirilmiş işlevlerdir. Gerekli olabilirler (her zaman
kullanılabilir) veya isteğe bağlı olabilirler (kullanıcı isteğe bağlı olarak etkinleştirir):

```typescript
register(api) {
  // Gerekli araç — her zaman kullanılabilir
  api.registerTool({
    name: "my_tool",
    description: "Do a thing",
    parameters: Type.Object({ input: Type.String() }),
    async execute(_id, params) {
      return { content: [{ type: "text", text: params.input }] };
    },
  });

  // İsteğe bağlı araç — kullanıcının izin listesine eklemesi gerekir
  api.registerTool(
    {
      name: "workflow_tool",
      description: "Run a workflow",
      parameters: Type.Object({ pipeline: Type.String() }),
      async execute(_id, params) {
        return { content: [{ type: "text", text: params.pipeline }] };
      },
    },
    { optional: true },
  );
}
```

Kullanıcılar isteğe bağlı araçları yapılandırmada etkinleştirir:

```json5
{
  tools: { allow: ["workflow_tool"] },
}
```

- Araç adları çekirdek araçlarla çakışmamalıdır (çakışmalar atlanır)
- Yan etkilere veya ek ikili gereksinimlere sahip araçlar için `optional: true` kullanın
- Kullanıcılar `tools.allow` içine plugin kimliğini ekleyerek bir plugin'deki tüm araçları etkinleştirebilir

## İçe aktarma kuralları

Her zaman odaklı `openclaw/plugin-sdk/<subpath>` yollarından içe aktarın:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";

// Yanlış: tek parça kök (kullanım dışı, kaldırılacak)
import { ... } from "openclaw/plugin-sdk";
```

Tam alt yol başvurusu için bkz. [SDK Overview](/tr/plugins/sdk-overview).

Plugin'inizin içinde, dahili içe aktarmalar için yerel barrel dosyaları (`api.ts`, `runtime-api.ts`) kullanın — kendi plugin'inizi asla kendi SDK yolu üzerinden içe aktarmayın.

Sağlayıcı plugin'leri için, sağlayıcıya özgü yardımcıları bu paket kökü
barrel'larında tutun; ancak arayüz gerçekten genelse farklıdır. Mevcut paketlenmiş örnekler:

- Anthropic: Claude akış sarmalayıcıları ve `service_tier` / beta yardımcıları
- OpenAI: sağlayıcı oluşturucular, varsayılan model yardımcıları, gerçek zamanlı sağlayıcılar
- OpenRouter: sağlayıcı oluşturucu ile onboarding/yapılandırma yardımcıları

Bir yardımcı yalnızca tek bir paketlenmiş sağlayıcı paketi içinde kullanışlıysa,
onu `openclaw/plugin-sdk/*` içine taşımak yerine o paket kökü arayüzünde tutun.

Bazı oluşturulmuş `openclaw/plugin-sdk/<bundled-id>` yardımcı arayüzleri, paketlenmiş plugin bakımı ve uyumluluğu için hâlâ mevcuttur; örneğin
`plugin-sdk/feishu-setup` veya `plugin-sdk/zalo-setup`. Bunları,
yeni üçüncü taraf plugin'leri için varsayılan kalıp olarak değil, ayrılmış
yüzeyler olarak değerlendirin.

## Gönderim öncesi kontrol listesi

<Check>**package.json** doğru `openclaw` meta verisine sahip</Check>
<Check>**openclaw.plugin.json** manifest dosyası mevcut ve geçerli</Check>
<Check>Giriş noktası `defineChannelPluginEntry` veya `definePluginEntry` kullanıyor</Check>
<Check>Tüm içe aktarmalar odaklı `plugin-sdk/<subpath>` yollarını kullanıyor</Check>
<Check>Dahili içe aktarmalar SDK self-import yerine yerel modülleri kullanıyor</Check>
<Check>Testler geçiyor (`pnpm test -- <bundled-plugin-root>/my-plugin/`)</Check>
<Check>`pnpm check` geçiyor (depo içi plugin'ler)</Check>

## Beta Sürüm Testi

1. [openclaw/openclaw](https://github.com/openclaw/openclaw/releases) üzerindeki GitHub sürüm etiketlerini izleyin ve `Watch` > `Releases` ile abone olun. Beta etiketleri `v2026.3.N-beta.1` gibi görünür. Sürüm duyuruları için resmi OpenClaw X hesabı [@openclaw](https://x.com/openclaw) bildirimlerini de açabilirsiniz.
2. Etiket görünür görünmez plugin'inizi beta etikete karşı test edin. Kararlı sürümden önceki pencere genellikle yalnızca birkaç saattir.
3. Testten sonra `plugin-forum` Discord kanalında plugin'inizin başlığı altında ya `all good` ya da neyin bozulduğunu yazın. Henüz bir başlığınız yoksa oluşturun.
4. Bir şey bozulursa, `Beta blocker: <plugin-name> - <summary>` başlıklı bir issue açın veya güncelleyin ve `beta-blocker` etiketini uygulayın. Issue bağlantısını başlığınıza koyun.
5. `main` için `fix(<plugin-id>): beta blocker - <summary>` başlıklı bir PR açın ve issue bağlantısını hem PR'a hem de Discord başlığınıza ekleyin. Katkıda bulunanlar PR'ları etiketleyemez, bu nedenle başlık bakımcılar ve otomasyon için PR tarafı sinyalidir. PR'ı olan engelleyiciler birleştirilir; olmayanlar yine de yayımlanabilir. Bakımcılar beta testi sırasında bu başlıkları izler.
6. Sessizlik yeşil demektir. Pencereyi kaçırırsanız, düzeltmeniz büyük olasılıkla sonraki döngüde yer alır.

## Sonraki adımlar

<CardGroup cols={2}>
  <Card title="Kanal Plugin'leri" icon="messages-square" href="/tr/plugins/sdk-channel-plugins">
    Bir mesajlaşma kanalı plugin'i geliştirin
  </Card>
  <Card title="Sağlayıcı Plugin'leri" icon="cpu" href="/tr/plugins/sdk-provider-plugins">
    Bir model sağlayıcı plugin'i geliştirin
  </Card>
  <Card title="SDK Overview" icon="book-open" href="/tr/plugins/sdk-overview">
    İçe aktarma eşlemesi ve kayıt API başvurusu
  </Card>
  <Card title="Çalışma Zamanı Yardımcıları" icon="settings" href="/tr/plugins/sdk-runtime">
    `api.runtime` üzerinden TTS, arama, alt agent
  </Card>
  <Card title="Test" icon="test-tubes" href="/tr/plugins/sdk-testing">
    Test yardımcıları ve kalıpları
  </Card>
  <Card title="Plugin Manifest" icon="file-json" href="/tr/plugins/manifest">
    Tam manifest şeması başvurusu
  </Card>
</CardGroup>

## İlgili

- [Plugin Mimarisi](/tr/plugins/architecture) — dahili mimariye derin bakış
- [SDK Overview](/tr/plugins/sdk-overview) — Plugin SDK başvurusu
- [Manifest](/tr/plugins/manifest) — plugin manifest biçimi
- [Kanal Plugin'leri](/tr/plugins/sdk-channel-plugins) — kanal plugin'leri geliştirme
- [Sağlayıcı Plugin'leri](/tr/plugins/sdk-provider-plugins) — sağlayıcı plugin'leri geliştirme
