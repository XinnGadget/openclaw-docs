---
read_when:
    - Yeni bir OpenClaw plugin'i oluşturmak istiyorsunuz
    - Plugin geliştirme için hızlı bir başlangıca ihtiyacınız var
    - OpenClaw'a yeni bir kanal, sağlayıcı, araç veya başka bir yetenek ekliyorsunuz
sidebarTitle: Getting Started
summary: İlk OpenClaw plugin'inizi dakikalar içinde oluşturun
title: Plugin Geliştirme
x-i18n:
    generated_at: "2026-04-07T08:47:01Z"
    model: gpt-5.4
    provider: openai
    source_hash: 509c1f5abe1a0a74966054ed79b71a1a7ee637a43b1214c424acfe62ddf48eef
    source_path: plugins/building-plugins.md
    workflow: 15
---

# Plugin Geliştirme

Plugin'ler OpenClaw'ı yeni yeteneklerle genişletir: kanallar, model sağlayıcıları,
konuşma, gerçek zamanlı transkripsiyon, gerçek zamanlı ses, medya anlama, görsel
üretimi, video üretimi, web getirme, web araması, ajan araçları veya bunların
herhangi bir kombinasyonu.

Plugin'inizi OpenClaw deposuna eklemeniz gerekmez. Onu
[ClawHub](/tr/tools/clawhub) veya npm üzerinde yayınlayın; kullanıcılar da
`openclaw plugins install <package-name>` ile kurar. OpenClaw önce ClawHub'ı dener ve
ardından otomatik olarak npm'e fallback yapar.

## Ön koşullar

- Node >= 22 ve bir paket yöneticisi (npm veya pnpm)
- TypeScript (ESM) bilgisi
- Repo içi plugin'ler için: deponun klonlanmış olması ve `pnpm install` çalıştırılmış olması

## Ne tür bir plugin?

<CardGroup cols={3}>
  <Card title="Kanal plugin'i" icon="messages-square" href="/tr/plugins/sdk-channel-plugins">
    OpenClaw'ı bir mesajlaşma platformuna bağlayın (Discord, IRC vb.)
  </Card>
  <Card title="Sağlayıcı plugin'i" icon="cpu" href="/tr/plugins/sdk-provider-plugins">
    Bir model sağlayıcısı ekleyin (LLM, proxy veya özel uç nokta)
  </Card>
  <Card title="Araç / hook plugin'i" icon="wrench">
    Ajan araçlarını, olay hook'larını veya hizmetleri kaydedin — aşağıdan devam edin
  </Card>
</CardGroup>

Bir kanal plugin'i isteğe bağlıysa ve onboarding/kurulum
çalıştığında kurulu olmayabilirse,
`openclaw/plugin-sdk/channel-setup` içinden `createOptionalChannelSetupSurface(...)` kullanın. Bu,
kurulum gereksinimini duyuran bir kurulum bağdaştırıcısı + sihirbaz çifti üretir ve
plugin kurulana kadar gerçek yapılandırma yazımlarında kapalı şekilde başarısız olur.

## Hızlı başlangıç: araç plugin'i

Bu rehber, bir ajan aracı kaydeden minimal bir plugin oluşturur. Kanal
ve sağlayıcı plugin'leri için yukarıda bağlantısı verilen özel kılavuzlar vardır.

<Steps>
  <Step title="Paketi ve manifest'i oluşturun">
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

    Her plugin'in, yapılandırması olmasa bile bir manifest'e ihtiyacı vardır. Tam
    şema için bkz. [Manifest](/tr/plugins/manifest). Kanonik ClawHub
    yayınlama parçacıkları `docs/snippets/plugin-publish/` içinde yer alır.

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

    `definePluginEntry`, kanal olmayan plugin'ler içindir. Kanallar için
    `defineChannelPluginEntry` kullanın — bkz. [Channel Plugins](/tr/plugins/sdk-channel-plugins).
    Tam giriş noktası seçenekleri için bkz. [Entry Points](/tr/plugins/sdk-entrypoints).

  </Step>

  <Step title="Test edin ve yayınlayın">

    **Harici plugin'ler:** ClawHub ile doğrulayın ve yayınlayın, ardından kurun:

    ```bash
    clawhub package publish your-org/your-plugin --dry-run
    clawhub package publish your-org/your-plugin
    openclaw plugins install clawhub:@myorg/openclaw-my-plugin
    ```

    OpenClaw, `@myorg/openclaw-my-plugin` gibi çıplak paket belirtimleri için
    npm'den önce ClawHub'ı da kontrol eder.

    **Repo içi plugin'ler:** birlikte gelen plugin workspace ağacının altına yerleştirin — otomatik olarak keşfedilir.

    ```bash
    pnpm test -- <bundled-plugin-root>/my-plugin/
    ```

  </Step>
</Steps>

## Plugin yetenekleri

Tek bir plugin, `api` nesnesi aracılığıyla istediği kadar yetenek kaydedebilir:

| Yetenek               | Kayıt yöntemi                                    | Ayrıntılı kılavuz                                                               |
| --------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------- |
| Metin çıkarımı (LLM)  | `api.registerProvider(...)`                      | [Provider Plugins](/tr/plugins/sdk-provider-plugins)                               |
| CLI çıkarım arka ucu  | `api.registerCliBackend(...)`                    | [CLI Backends](/tr/gateway/cli-backends)                                           |
| Kanal / mesajlaşma    | `api.registerChannel(...)`                       | [Channel Plugins](/tr/plugins/sdk-channel-plugins)                                 |
| Konuşma (TTS/STT)     | `api.registerSpeechProvider(...)`                | [Provider Plugins](/tr/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Gerçek zamanlı transkripsiyon | `api.registerRealtimeTranscriptionProvider(...)` | [Provider Plugins](/tr/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Gerçek zamanlı ses    | `api.registerRealtimeVoiceProvider(...)`         | [Provider Plugins](/tr/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Medya anlama          | `api.registerMediaUnderstandingProvider(...)`    | [Provider Plugins](/tr/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Görsel üretimi        | `api.registerImageGenerationProvider(...)`       | [Provider Plugins](/tr/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Müzik üretimi         | `api.registerMusicGenerationProvider(...)`       | [Provider Plugins](/tr/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Video üretimi         | `api.registerVideoGenerationProvider(...)`       | [Provider Plugins](/tr/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Web getirme           | `api.registerWebFetchProvider(...)`              | [Provider Plugins](/tr/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Web araması           | `api.registerWebSearchProvider(...)`             | [Provider Plugins](/tr/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Ajan araçları         | `api.registerTool(...)`                          | Aşağıda                                                                         |
| Özel komutlar         | `api.registerCommand(...)`                       | [Entry Points](/tr/plugins/sdk-entrypoints)                                        |
| Olay hook'ları        | `api.registerHook(...)`                          | [Entry Points](/tr/plugins/sdk-entrypoints)                                        |
| HTTP rotaları         | `api.registerHttpRoute(...)`                     | [Internals](/tr/plugins/architecture#gateway-http-routes)                          |
| CLI alt komutları     | `api.registerCli(...)`                           | [Entry Points](/tr/plugins/sdk-entrypoints)                                        |

Tam kayıt API'si için bkz. [SDK Overview](/tr/plugins/sdk-overview#registration-api).

Plugin'iniz özel gateway RPC yöntemleri kaydediyorsa, bunları
plugin'e özgü bir önek altında tutun. Çekirdek yönetici ad alanları (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) ayrılmış kalır ve bir plugin daha dar
bir kapsam istese bile her zaman `operator.admin` olarak çözülür.

Akılda tutulması gereken hook koruma semantiği:

- `before_tool_call`: `{ block: true }` terminaldir ve daha düşük öncelikli işleyicileri durdurur.
- `before_tool_call`: `{ block: false }` karar yokmuş gibi değerlendirilir.
- `before_tool_call`: `{ requireApproval: true }` ajan yürütmesini duraklatır ve kullanıcıdan exec approval overlay, Telegram düğmeleri, Discord etkileşimleri veya herhangi bir kanaldaki `/approve` komutu aracılığıyla onay ister.
- `before_install`: `{ block: true }` terminaldir ve daha düşük öncelikli işleyicileri durdurur.
- `before_install`: `{ block: false }` karar yokmuş gibi değerlendirilir.
- `message_sending`: `{ cancel: true }` terminaldir ve daha düşük öncelikli işleyicileri durdurur.
- `message_sending`: `{ cancel: false }` karar yokmuş gibi değerlendirilir.

`/approve` komutu, sınırlandırılmış fallback ile hem exec hem de plugin onaylarını işler: bir exec approval kimliği bulunamadığında, OpenClaw aynı kimliği plugin onayları üzerinden yeniden dener. Plugin onay yönlendirmesi, yapılandırmada `approvals.plugin` aracılığıyla bağımsız olarak yapılandırılabilir.

Özel onay altyapısının aynı sınırlandırılmış fallback durumunu algılaması gerekiyorsa,
onay süresi dolma dizgelerini elle eşleştirmek yerine
`openclaw/plugin-sdk/error-runtime` içinden `isApprovalNotFoundError` kullanın.

Ayrıntılar için bkz. [SDK Overview hook decision semantics](/tr/plugins/sdk-overview#hook-decision-semantics).

## Ajan araçlarını kaydetme

Araçlar, LLM'nin çağırabileceği türlendirilmiş işlevlerdir. Zorunlu (her zaman
kullanılabilir) veya isteğe bağlı (kullanıcının katılımı gerekir) olabilirler:

```typescript
register(api) {
  // Required tool — always available
  api.registerTool({
    name: "my_tool",
    description: "Do a thing",
    parameters: Type.Object({ input: Type.String() }),
    async execute(_id, params) {
      return { content: [{ type: "text", text: params.input }] };
    },
  });

  // Optional tool — user must add to allowlist
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
- Yan etkileri veya ek ikili gereksinimleri olan araçlar için `optional: true` kullanın
- Kullanıcılar, `tools.allow` içine plugin kimliğini ekleyerek bir plugin'deki tüm araçları etkinleştirebilir

## Import kuralları

Her zaman odaklanmış `openclaw/plugin-sdk/<subpath>` yollarından import edin:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";

// Wrong: monolithic root (deprecated, will be removed)
import { ... } from "openclaw/plugin-sdk";
```

Tam alt yol başvurusu için bkz. [SDK Overview](/tr/plugins/sdk-overview).

Plugin'inizin içinde, dahili import'lar için yerel barrel dosyalarını (`api.ts`, `runtime-api.ts`) kullanın —
kendi plugin'inizi asla kendi SDK yolu üzerinden import etmeyin.

Sağlayıcı plugin'leri için, gerçekten genel bir yüzey değilse sağlayıcıya özgü yardımcıları bu paket kökü
barrel dosyalarında tutun. Güncel birlikte gelen örnekler:

- Anthropic: Claude akış sarmalayıcıları ve `service_tier` / beta yardımcıları
- OpenAI: sağlayıcı oluşturucular, varsayılan model yardımcıları, gerçek zamanlı sağlayıcılar
- OpenRouter: sağlayıcı oluşturucu ve onboarding/config yardımcıları

Bir yardımcı yalnızca tek bir birlikte gelen sağlayıcı paketi içinde yararlıysa,
onu `openclaw/plugin-sdk/*` içine yükseltmek yerine o
paket kökü yüzeyinde tutun.

Üretilmiş bazı `openclaw/plugin-sdk/<bundled-id>` yardımcı yüzeyleri,
birlikte gelen plugin bakımı ve uyumluluk için hâlâ mevcuttur; örneğin
`plugin-sdk/feishu-setup` veya `plugin-sdk/zalo-setup`. Bunları,
yeni üçüncü taraf plugin'ler için varsayılan desen olarak değil, ayrılmış
yüzeyler olarak değerlendirin.

## Gönderim öncesi kontrol listesi

<Check>**package.json** dosyasında doğru `openclaw` meta verileri var</Check>
<Check>**openclaw.plugin.json** manifest'i mevcut ve geçerli</Check>
<Check>Giriş noktası `defineChannelPluginEntry` veya `definePluginEntry` kullanıyor</Check>
<Check>Tüm import'lar odaklanmış `plugin-sdk/<subpath>` yollarını kullanıyor</Check>
<Check>Dahili import'lar SDK self-import'ları değil, yerel modüller kullanıyor</Check>
<Check>Testler geçiyor (`pnpm test -- <bundled-plugin-root>/my-plugin/`)</Check>
<Check>`pnpm check` geçiyor (repo içi plugin'ler)</Check>

## Beta Sürüm Testi

1. [openclaw/openclaw](https://github.com/openclaw/openclaw/releases) üzerindeki GitHub sürüm etiketlerini izleyin ve `Watch` > `Releases` üzerinden abone olun. Beta etiketleri `v2026.3.N-beta.1` gibi görünür. Sürüm duyuruları için resmi OpenClaw X hesabı [@openclaw](https://x.com/openclaw) bildirimlerini de açabilirsiniz.
2. Eşit görünür görünmez plugin'inizi beta etikete karşı test edin. Kararlı sürümden önceki pencere genellikle yalnızca birkaç saattir.
3. Testten sonra `plugin-forum` Discord kanalındaki plugin dizinizde `all good` veya neyin bozulduğunu yazarak paylaşım yapın. Henüz bir diziniz yoksa oluşturun.
4. Bir şey bozulursa, `Beta blocker: <plugin-name> - <summary>` başlıklı bir issue açın veya mevcut bir issue'yu güncelleyin ve `beta-blocker` etiketini uygulayın. Issue bağlantısını dizinize ekleyin.
5. `main` için `fix(<plugin-id>): beta blocker - <summary>` başlıklı bir PR açın ve issue'yu hem PR içinde hem de Discord dizinizde bağlayın. Katkıda bulunanlar PR'leri etiketleyemez, bu nedenle başlık bakımcılar ve otomasyon için PR tarafındaki sinyaldir. PR'si olan engelleyiciler birleştirilir; olmayanlar yine de yayına girebilir. Bakımcılar beta testi sırasında bu dizileri izler.
6. Sessizlik yeşil anlamına gelir. Bu pencereyi kaçırırsanız, düzeltmeniz büyük olasılıkla bir sonraki döngüye kalır.

## Sonraki adımlar

<CardGroup cols={2}>
  <Card title="Kanal Plugin'leri" icon="messages-square" href="/tr/plugins/sdk-channel-plugins">
    Bir mesajlaşma kanal plugin'i oluşturun
  </Card>
  <Card title="Sağlayıcı Plugin'leri" icon="cpu" href="/tr/plugins/sdk-provider-plugins">
    Bir model sağlayıcı plugin'i oluşturun
  </Card>
  <Card title="SDK Genel Bakış" icon="book-open" href="/tr/plugins/sdk-overview">
    Import eşlemi ve kayıt API başvurusu
  </Card>
  <Card title="Çalışma Zamanı Yardımcıları" icon="settings" href="/tr/plugins/sdk-runtime">
    api.runtime üzerinden TTS, arama, alt ajan
  </Card>
  <Card title="Test" icon="test-tubes" href="/tr/plugins/sdk-testing">
    Test yardımcıları ve kalıpları
  </Card>
  <Card title="Plugin Manifest'i" icon="file-json" href="/tr/plugins/manifest">
    Tam manifest şeması başvurusu
  </Card>
</CardGroup>

## İlgili

- [Plugin Mimarisi](/tr/plugins/architecture) — dahili mimariye derin bakış
- [SDK Genel Bakış](/tr/plugins/sdk-overview) — Plugin SDK başvurusu
- [Manifest](/tr/plugins/manifest) — plugin manifest biçimi
- [Channel Plugins](/tr/plugins/sdk-channel-plugins) — kanal plugin'leri geliştirme
- [Provider Plugins](/tr/plugins/sdk-provider-plugins) — sağlayıcı plugin'leri geliştirme
