---
read_when:
    - Bir plugin'e kurulum sihirbazı ekliyorsunuz
    - setup-entry.ts ile index.ts arasındaki farkı anlamanız gerekiyor
    - Plugin yapılandırma şemalarını veya package.json içindeki openclaw meta verilerini tanımlıyorsunuz
sidebarTitle: Setup and Config
summary: Kurulum sihirbazları, setup-entry.ts, yapılandırma şemaları ve package.json meta verileri
title: Plugin Kurulumu ve Yapılandırması
x-i18n:
    generated_at: "2026-04-06T03:11:07Z"
    model: gpt-5.4
    provider: openai
    source_hash: eac2586516d27bcd94cc4c259fe6274c792b3f9938c7ddd6dbf04a6dbb988dc9
    source_path: plugins/sdk-setup.md
    workflow: 15
---

# Plugin Kurulumu ve Yapılandırması

Plugin paketleme (`package.json` meta verileri), manifestler
(`openclaw.plugin.json`), kurulum girişleri ve yapılandırma şemaları için başvuru.

<Tip>
  **Adım adım bir kılavuz mu arıyorsunuz?** Nasıl yapılır kılavuzları paketlemeyi bağlam içinde ele alır:
  [Kanal Plugin'leri](/tr/plugins/sdk-channel-plugins#step-1-package-and-manifest) ve
  [Sağlayıcı Plugin'leri](/tr/plugins/sdk-provider-plugins#step-1-package-and-manifest).
</Tip>

## Paket meta verileri

`package.json` dosyanızda, plugin sistemine
plugin'inizin ne sağladığını söyleyen bir `openclaw` alanı bulunmalıdır:

**Kanal plugin'i:**

```json
{
  "name": "@myorg/openclaw-my-channel",
  "version": "1.0.0",
  "type": "module",
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "channel": {
      "id": "my-channel",
      "label": "My Channel",
      "blurb": "Short description of the channel."
    }
  }
}
```

**Sağlayıcı plugin'i / ClawHub yayımlama temeli:**

```json openclaw-clawhub-package.json
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

Plugin'i ClawHub üzerinde harici olarak yayımlıyorsanız, bu `compat` ve `build`
alanları zorunludur. Kanonik yayımlama parçacıkları
`docs/snippets/plugin-publish/` içinde bulunur.

### `openclaw` alanları

| Alan         | Tür        | Açıklama                                                                                              |
| ------------ | ---------- | ----------------------------------------------------------------------------------------------------- |
| `extensions` | `string[]` | Giriş noktası dosyaları (paket kök dizinine göre göreli)                                              |
| `setupEntry` | `string`   | Hafif, yalnızca kurulum için giriş (isteğe bağlı)                                                     |
| `channel`    | `object`   | Kurulum, seçici, hızlı başlangıç ve durum yüzeyleri için kanal katalog meta verileri                  |
| `providers`  | `string[]` | Bu plugin tarafından kaydedilen sağlayıcı kimlikleri                                                  |
| `install`    | `object`   | Kurulum ipuçları: `npmSpec`, `localPath`, `defaultChoice`, `minHostVersion`, `allowInvalidConfigRecovery` |
| `startup`    | `object`   | Başlangıç davranışı bayrakları                                                                         |

### `openclaw.channel`

`openclaw.channel`, çalışma zamanı yüklenmeden önce kanal keşfi ve kurulum
yüzeyleri için düşük maliyetli paket meta verileridir.

| Alan                                   | Tür        | Anlamı                                                                        |
| -------------------------------------- | ---------- | ----------------------------------------------------------------------------- |
| `id`                                   | `string`   | Kanonik kanal kimliği.                                                        |
| `label`                                | `string`   | Birincil kanal etiketi.                                                       |
| `selectionLabel`                       | `string`   | `label` değerinden farklı olması gerektiğinde seçici/kurulum etiketi.         |
| `detailLabel`                          | `string`   | Daha zengin kanal katalogları ve durum yüzeyleri için ikincil ayrıntı etiketi.|
| `docsPath`                             | `string`   | Kurulum ve seçim bağlantıları için belge yolu.                                |
| `docsLabel`                            | `string`   | Kanal kimliğinden farklı olması gerektiğinde belgeler bağlantısı için geçersiz kılma etiketi. |
| `blurb`                                | `string`   | Kısa onboarding/katalog açıklaması.                                           |
| `order`                                | `number`   | Kanal kataloglarındaki sıralama düzeni.                                       |
| `aliases`                              | `string[]` | Kanal seçimi için ek arama diğer adları.                                      |
| `preferOver`                           | `string[]` | Bu kanalın geride bırakması gereken daha düşük öncelikli plugin/kanal kimlikleri. |
| `systemImage`                          | `string`   | Kanal UI katalogları için isteğe bağlı simge/sistem görseli adı.              |
| `selectionDocsPrefix`                  | `string`   | Seçim yüzeylerinde belge bağlantılarından önce gelen önek metin.              |
| `selectionDocsOmitLabel`               | `boolean`  | Seçim metninde etiketli belge bağlantısı yerine belge yolunu doğrudan gösterir. |
| `selectionExtras`                      | `string[]` | Seçim metnine eklenen ek kısa dizeler.                                        |
| `markdownCapable`                      | `boolean`  | Giden biçimlendirme kararları için kanalı markdown uyumlu olarak işaretler.   |
| `exposure`                             | `object`   | Kurulum, yapılandırılmış listeler ve belge yüzeyleri için kanal görünürlük denetimleri. |
| `quickstartAllowFrom`                  | `boolean`  | Bu kanalı standart hızlı başlangıç `allowFrom` kurulum akışına dahil eder.    |
| `forceAccountBinding`                  | `boolean`  | Yalnızca bir hesap olsa bile açık hesap bağlamasını zorunlu kılar.            |
| `preferSessionLookupForAnnounceTarget` | `boolean`  | Bu kanal için duyuru hedeflerini çözerken oturum aramasını tercih eder.       |

Örnek:

```json
{
  "openclaw": {
    "channel": {
      "id": "my-channel",
      "label": "My Channel",
      "selectionLabel": "My Channel (self-hosted)",
      "detailLabel": "My Channel Bot",
      "docsPath": "/channels/my-channel",
      "docsLabel": "my-channel",
      "blurb": "Webhook-based self-hosted chat integration.",
      "order": 80,
      "aliases": ["mc"],
      "preferOver": ["my-channel-legacy"],
      "selectionDocsPrefix": "Guide:",
      "selectionExtras": ["Markdown"],
      "markdownCapable": true,
      "exposure": {
        "configured": true,
        "setup": true,
        "docs": true
      },
      "quickstartAllowFrom": true
    }
  }
}
```

`exposure` şunları destekler:

- `configured`: kanalı yapılandırılmış/durum benzeri listeleme yüzeylerine dahil et
- `setup`: kanalı etkileşimli kurulum/yapılandırma seçicilerine dahil et
- `docs`: kanalı belge/gezinme yüzeylerinde herkese açık olarak işaretle

`showConfigured` ve `showInSetup` eski diğer adlar olarak desteklenmeye devam eder. Tercihen
`exposure` kullanın.

### `openclaw.install`

`openclaw.install`, manifest meta verisi değil, paket meta verisidir.

| Alan                         | Tür                  | Anlamı                                                                          |
| ---------------------------- | -------------------- | -------------------------------------------------------------------------------- |
| `npmSpec`                    | `string`             | Kurulum/güncelleme akışları için kanonik npm belirtimi.                         |
| `localPath`                  | `string`             | Yerel geliştirme veya paketli kurulum yolu.                                     |
| `defaultChoice`              | `"npm"` \| `"local"` | Her ikisi de mevcutsa tercih edilen kurulum kaynağı.                            |
| `minHostVersion`             | `string`             | `>=x.y.z` biçiminde desteklenen en düşük OpenClaw sürümü.                       |
| `allowInvalidConfigRecovery` | `boolean`            | Paketli plugin yeniden kurulum akışlarının belirli eski yapılandırma hatalarından kurtulmasını sağlar. |

`minHostVersion` ayarlanmışsa hem kurulum hem de manifest-kayıt defteri yükleme bunu
uygular. Eski ana bilgisayarlar plugin'i atlar; geçersiz sürüm dizeleri reddedilir.

`allowInvalidConfigRecovery`, bozuk yapılandırmalar için genel bir baypas değildir. Bu
yalnızca dar kapsamlı paketli plugin kurtarma içindir; böylece yeniden kurulum/kurulum,
eksik paketli plugin yolu veya aynı plugin için eski `channels.<id>`
girdisi gibi bilinen yükseltme kalıntılarını onarabilir. Yapılandırma
ilgisiz nedenlerle bozuksa kurulum yine kapalı güvenli şekilde başarısız olur ve operatöre `openclaw doctor --fix` çalıştırmasını söyler.

### Ertelenmiş tam yükleme

Kanal plugin'leri şu şekilde ertelenmiş yüklemeyi seçebilir:

```json
{
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "startup": {
      "deferConfiguredChannelFullLoadUntilAfterListen": true
    }
  }
}
```

Etkinleştirildiğinde OpenClaw, ön dinleme başlangıç
aşamasında, önceden yapılandırılmış kanallar için bile yalnızca `setupEntry` yükler. Tam giriş, gateway dinlemeye başladıktan sonra yüklenir.

<Warning>
  Ertelenmiş yüklemeyi yalnızca `setupEntry` dosyanız gateway'in
  dinlemeye başlamadan önce ihtiyaç duyduğu her şeyi kaydediyorsa etkinleştirin
  (kanal kaydı, HTTP yolları, gateway yöntemleri). Tam giriş gerekli başlangıç yeteneklerine sahipse
  varsayılan davranışı koruyun.
</Warning>

Kurulum/tam girişiniz gateway RPC yöntemleri kaydediyorsa bunları
plugin'e özgü bir önek altında tutun. Ayrılmış çekirdek yönetici ad alanları (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) çekirdeğe ait kalır ve her zaman
`operator.admin` değerine çözülür.

## Plugin manifesti

Her yerel plugin paket kök dizininde bir `openclaw.plugin.json` dosyası taşımalıdır.
OpenClaw bunu, plugin kodunu yürütmeden yapılandırmayı doğrulamak için kullanır.

```json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "description": "Adds My Plugin capabilities to OpenClaw",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "webhookSecret": {
        "type": "string",
        "description": "Webhook verification secret"
      }
    }
  }
}
```

Kanal plugin'leri için `kind` ve `channels` ekleyin:

```json
{
  "id": "my-channel",
  "kind": "channel",
  "channels": ["my-channel"],
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
```

Yapılandırması olmayan plugin'ler bile bir şema taşımalıdır. Boş bir şema geçerlidir:

```json
{
  "id": "my-plugin",
  "configSchema": {
    "type": "object",
    "additionalProperties": false
  }
}
```

Tam şema başvurusu için bkz. [Plugin Manifest](/tr/plugins/manifest).

## ClawHub'da yayımlama

Plugin paketleri için pakete özel ClawHub komutunu kullanın:

```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
```

Eski yalnızca-skill yayımlama diğer adı skill'ler içindir. Plugin paketleri
her zaman `clawhub package publish` kullanmalıdır.

## Kurulum girişi

`setup-entry.ts` dosyası, OpenClaw'ın yalnızca kurulum yüzeylerine ihtiyaç duyduğunda yüklediği
(index.ts'ye göre) hafif bir alternatiftir (onboarding, yapılandırma onarımı,
devre dışı kanal incelemesi).

```typescript
// setup-entry.ts
import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";
import { myChannelPlugin } from "./src/channel.js";

export default defineSetupPluginEntry(myChannelPlugin);
```

Bu, kurulum akışları sırasında ağır çalışma zamanı kodlarının (kripto kitaplıkları, CLI kayıtları,
arka plan servisleri) yüklenmesini önler.

**OpenClaw'ın tam giriş yerine `setupEntry` kullandığı durumlar:**

- Kanal devre dışıdır ancak kurulum/onboarding yüzeylerine ihtiyaç duyar
- Kanal etkindir ancak yapılandırılmamıştır
- Ertelenmiş yükleme etkindir (`deferConfiguredChannelFullLoadUntilAfterListen`)

**`setupEntry` tarafından kaydedilmesi gerekenler:**

- Kanal plugin nesnesi (`defineSetupPluginEntry` aracılığıyla)
- Gateway dinlemesinden önce gerekli olan tüm HTTP yolları
- Başlangıç sırasında gereken tüm gateway yöntemleri

Bu başlangıç gateway yöntemleri yine de `config.*` veya `update.*`
gibi ayrılmış çekirdek yönetici ad alanlarından kaçınmalıdır.

**`setupEntry` içinde OLMAMASI gerekenler:**

- CLI kayıtları
- Arka plan servisleri
- Ağır çalışma zamanı içe aktarımları (kripto, SDK'lar)
- Yalnızca başlangıç sonrası gereken gateway yöntemleri

### Dar kurulum yardımcı içe aktarımları

Sıcak yalnızca-kurulum yolları için, kurulum yüzeyinin yalnızca bir bölümüne ihtiyaç duyduğunuzda
daha geniş `plugin-sdk/setup` şemsiyesi yerine dar kurulum yardımcı bağlantı yüzeylerini tercih edin:

| İçe aktarma yolu                  | Şunun için kullanın                                                                    | Temel dışa aktarımlar                                                                                                                                                                                                                                                                              |
| --------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/setup-runtime`        | `setupEntry` / ertelenmiş kanal başlangıcında kullanılabilir kalan kurulum zamanı çalışma zamanı yardımcıları | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
| `plugin-sdk/setup-adapter-runtime` | ortam farkındalıklı hesap kurulum bağdaştırıcıları                                     | `createEnvPatchedAccountSetupAdapter`                                                                                                                                                                                                                                                              |
| `plugin-sdk/setup-tools`          | kurulum/yükleme CLI/arşiv/belge yardımcıları                                           | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR`                                                                                                                                                                                    |

Yapılandırma yama yardımcıları gibi tam paylaşılan kurulum
araç kutusunu istediğinizde daha geniş `plugin-sdk/setup` bağlantı yüzeyini kullanın; örneğin
`moveSingleAccountChannelSectionToDefaultAccount(...)`.

Kurulum yama bağdaştırıcıları içe aktarma sırasında sıcak yol için güvenli kalır. Bunların paketli
tek hesap yükseltme sözleşme-yüzeyi araması tembeldir; yani
`plugin-sdk/setup-runtime` içe aktarmak, bağdaştırıcı fiilen kullanılmadan önce paketli sözleşme-yüzeyi
keşfini erken yüklemez.

### Kanalın sahip olduğu tek hesap yükseltmesi

Bir kanal tek hesaplı üst düzey yapılandırmadan
`channels.<id>.accounts.*` yapısına yükseltildiğinde, varsayılan paylaşılan davranış
yükseltilen hesap kapsamlı değerleri `accounts.default` içine taşımaktır.

Paketli kanallar bu yükseltmeyi kurulum
sözleşme yüzeyleri üzerinden daraltabilir veya geçersiz kılabilir:

- `singleAccountKeysToMove`: yükseltilen
  hesaba taşınması gereken ek üst düzey anahtarlar
- `namedAccountPromotionKeys`: adlandırılmış hesaplar zaten varsa yalnızca bu
  anahtarlar yükseltilen hesaba taşınır; paylaşılan ilke/teslimat anahtarları kanal kökünde kalır
- `resolveSingleAccountPromotionTarget(...)`: yükseltilen değerleri hangi mevcut hesabın
  alacağını seçer

Mevcut paketli örnek Matrix'tir. Zaten tam olarak bir adlandırılmış Matrix hesabı
varsa veya `defaultAccount`, `Ops` gibi mevcut kanonik olmayan bir anahtarı
işaret ediyorsa yükseltme yeni bir `accounts.default` girdisi oluşturmak yerine bu hesabı korur.

## Yapılandırma şeması

Plugin yapılandırması, manifestinizdeki JSON Schema'ya göre doğrulanır. Kullanıcılar
plugin'leri şu şekilde yapılandırır:

```json5
{
  plugins: {
    entries: {
      "my-plugin": {
        config: {
          webhookSecret: "abc123",
        },
      },
    },
  },
}
```

Plugin'iniz bu yapılandırmayı kayıt sırasında `api.pluginConfig` olarak alır.

Kanala özgü yapılandırma için bunun yerine kanal yapılandırma bölümünü kullanın:

```json5
{
  channels: {
    "my-channel": {
      token: "bot-token",
      allowFrom: ["user1", "user2"],
    },
  },
}
```

### Kanal yapılandırma şemaları oluşturma

Bir Zod şemasını OpenClaw'ın doğruladığı `ChannelConfigSchema`
sarmalayıcısına dönüştürmek için `openclaw/plugin-sdk/core` içinden `buildChannelConfigSchema` kullanın:

```typescript
import { z } from "zod";
import { buildChannelConfigSchema } from "openclaw/plugin-sdk/core";

const accountSchema = z.object({
  token: z.string().optional(),
  allowFrom: z.array(z.string()).optional(),
  accounts: z.object({}).catchall(z.any()).optional(),
  defaultAccount: z.string().optional(),
});

const configSchema = buildChannelConfigSchema(accountSchema);
```

## Kurulum sihirbazları

Kanal plugin'leri `openclaw onboard` için etkileşimli kurulum sihirbazları sağlayabilir.
Sihirbaz, `ChannelPlugin` üzerindeki bir `ChannelSetupWizard` nesnesidir:

```typescript
import type { ChannelSetupWizard } from "openclaw/plugin-sdk/channel-setup";

const setupWizard: ChannelSetupWizard = {
  channel: "my-channel",
  status: {
    configuredLabel: "Connected",
    unconfiguredLabel: "Not configured",
    resolveConfigured: ({ cfg }) => Boolean((cfg.channels as any)?.["my-channel"]?.token),
  },
  credentials: [
    {
      inputKey: "token",
      providerHint: "my-channel",
      credentialLabel: "Bot token",
      preferredEnvVar: "MY_CHANNEL_BOT_TOKEN",
      envPrompt: "Use MY_CHANNEL_BOT_TOKEN from environment?",
      keepPrompt: "Keep current token?",
      inputPrompt: "Enter your bot token:",
      inspect: ({ cfg, accountId }) => {
        const token = (cfg.channels as any)?.["my-channel"]?.token;
        return {
          accountConfigured: Boolean(token),
          hasConfiguredValue: Boolean(token),
        };
      },
    },
  ],
};
```

`ChannelSetupWizard` türü `credentials`, `textInputs`,
`dmPolicy`, `allowFrom`, `groupAccess`, `prepare`, `finalize` ve daha fazlasını destekler.
Tam örnekler için paketli plugin paketlerine (örneğin Discord plugin'inin `src/channel.setup.ts` dosyasına) bakın.

Yalnızca standart
`not -> prompt -> parse -> merge -> patch` akışına ihtiyaç duyan DM izin listesi istemleri için
`openclaw/plugin-sdk/setup` içindeki paylaşılan kurulum
yardımcılarını tercih edin: `createPromptParsedAllowFromForAccount(...)`,
`createTopLevelChannelParsedAllowFromPrompt(...)` ve
`createNestedChannelParsedAllowFromPrompt(...)`.

Yalnızca etiketler, puanlar ve isteğe bağlı
ek satırlarda değişen kanal kurulum durum blokları için,
her plugin'de aynı `status` nesnesini elle yazmak yerine
`openclaw/plugin-sdk/setup` içinden `createStandardChannelSetupStatus(...)` kullanın.

Yalnızca belirli bağlamlarda görünmesi gereken isteğe bağlı kurulum yüzeyleri için
`openclaw/plugin-sdk/channel-setup` içinden
`createOptionalChannelSetupSurface` kullanın:

```typescript
import { createOptionalChannelSetupSurface } from "openclaw/plugin-sdk/channel-setup";

const setupSurface = createOptionalChannelSetupSurface({
  channel: "my-channel",
  label: "My Channel",
  npmSpec: "@myorg/openclaw-my-channel",
  docsPath: "/channels/my-channel",
});
// Returns { setupAdapter, setupWizard }
```

`plugin-sdk/channel-setup`, yalnızca bu isteğe bağlı kurulum yüzeyinin
yarısına ihtiyaç duyduğunuzda daha düşük seviyeli
`createOptionalChannelSetupAdapter(...)` ve
`createOptionalChannelSetupWizard(...)` oluşturucularını da sunar.

Üretilen isteğe bağlı bağdaştırıcı/sihirbaz, gerçek yapılandırma yazmalarında kapalı güvenli davranır. Bunlar
`validateInput`,
`applyAccountConfig` ve `finalize` arasında tek bir kurulum-gerekli iletisini yeniden kullanır ve `docsPath`
ayarlıysa bir belge bağlantısı ekler.

İkili dosya destekli kurulum arayüzleri için, her kanala aynı ikili/durum yapıştırıcısını
kopyalamak yerine paylaşılan devredilmiş yardımcıları tercih edin:

- yalnızca etiketler,
  ipuçları, puanlar ve ikili algılamasında değişen durum blokları için `createDetectedBinaryStatus(...)`
- yol destekli metin girişleri için `createCliPathTextInput(...)`
- `setupEntry` daha ağır bir tam sihirbaza tembel biçimde iletmek zorundaysa
  `createDelegatedSetupWizardStatusResolvers(...)`,
  `createDelegatedPrepare(...)`, `createDelegatedFinalize(...)` ve
  `createDelegatedResolveConfigured(...)`
- `setupEntry` yalnızca bir `textInputs[*].shouldPrompt` kararını
  devretmek zorundaysa `createDelegatedTextInputShouldPrompt(...)`

## Yayımlama ve kurulum

**Harici plugin'ler:** [ClawHub](/tr/tools/clawhub) veya npm üzerinde yayımlayın, sonra kurun:

```bash
openclaw plugins install @myorg/openclaw-my-plugin
```

OpenClaw önce ClawHub'ı dener ve sonra otomatik olarak npm'e geri döner. ClawHub'ı açıkça zorlamak için de şunu kullanabilirsiniz:

```bash
openclaw plugins install clawhub:@myorg/openclaw-my-plugin   # yalnızca ClawHub
```

Buna karşılık gelen bir `npm:` geçersiz kılması yoktur. ClawHub geri dönüşünden sonra npm yolunu
istediğinizde normal npm paket belirtimini kullanın:

```bash
openclaw plugins install @myorg/openclaw-my-plugin
```

**Repo içi plugin'ler:** paketli plugin çalışma alanı ağacı altına yerleştirin; derleme sırasında otomatik
olarak keşfedilirler.

**Kullanıcılar şunu kurabilir:**

```bash
openclaw plugins install <package-name>
```

<Info>
  npm kaynaklı kurulumlarda `openclaw plugins install`,
  `npm install --ignore-scripts` çalıştırır (yaşam döngüsü betikleri yoktur). Plugin bağımlılık
  ağaçlarını saf JS/TS tutun ve `postinstall` derlemeleri gerektiren paketlerden kaçının.
</Info>

## İlgili

- [SDK Giriş Noktaları](/tr/plugins/sdk-entrypoints) -- `definePluginEntry` ve `defineChannelPluginEntry`
- [Plugin Manifest](/tr/plugins/manifest) -- tam manifest şeması başvurusu
- [Plugin Oluşturma](/tr/plugins/building-plugins) -- adım adım başlangıç kılavuzu
