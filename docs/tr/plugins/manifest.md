---
read_when:
    - Bir OpenClaw eklentisi geliştiriyorsunuz
    - Bir eklenti yapılandırma şeması yayımlamanız veya eklenti doğrulama hatalarında hata ayıklamanız gerekiyor
summary: Eklenti manifestosu + JSON schema gereksinimleri (katı yapılandırma doğrulaması)
title: Eklenti Manifestosu
x-i18n:
    generated_at: "2026-04-07T08:47:25Z"
    model: gpt-5.4
    provider: openai
    source_hash: 22d41b9f8748b1b1b066ee856be4a8f41e88b9a8bc073d74fc79d2bb0982f01a
    source_path: plugins/manifest.md
    workflow: 15
---

# Eklenti manifestosu (`openclaw.plugin.json`)

Bu sayfa yalnızca **yerel OpenClaw eklenti manifestosu** içindir.

Uyumlu bundle düzenleri için [Plugin bundles](/tr/plugins/bundles) bölümüne bakın.

Uyumlu bundle biçimleri farklı manifest dosyaları kullanır:

- Codex bundle: `.codex-plugin/plugin.json`
- Claude bundle: `.claude-plugin/plugin.json` veya manifestosu olmayan varsayılan Claude bileşen
  düzeni
- Cursor bundle: `.cursor-plugin/plugin.json`

OpenClaw bu bundle düzenlerini de otomatik algılar, ancak bunlar burada açıklanan
`openclaw.plugin.json` şemasına göre doğrulanmaz.

Uyumlu bundle'lar için OpenClaw şu anda, düzen OpenClaw çalışma zamanı beklentileriyle eşleştiğinde,
bundle meta verilerini, bildirilen skill köklerini, Claude komut köklerini, Claude bundle `settings.json` varsayılanlarını,
Claude bundle LSP varsayılanlarını ve desteklenen hook paketlerini okur.

Her yerel OpenClaw eklentisi, **eklenti kökünde** bir `openclaw.plugin.json` dosyası
bulundurmak **zorundadır**. OpenClaw bu manifestoyu, yapılandırmayı
**eklenti kodunu çalıştırmadan** doğrulamak için kullanır. Eksik veya geçersiz manifestolar
eklenti hatası olarak değerlendirilir ve yapılandırma doğrulamasını engeller.

Tam eklenti sistemi kılavuzu için bkz.: [Plugins](/tr/tools/plugin).
Yerel yetenek modeli ve mevcut dış uyumluluk rehberi için:
[Capability model](/tr/plugins/architecture#public-capability-model).

## Bu dosya ne işe yarar

`openclaw.plugin.json`, OpenClaw'ın eklenti kodunuzu yüklemeden önce okuduğu
meta veridir.

Şunlar için kullanın:

- eklenti kimliği
- yapılandırma doğrulaması
- eklenti çalışma zamanı başlatılmadan kullanılabilir olması gereken kimlik doğrulama ve onboarding meta verileri
- eklenti çalışma zamanı yüklenmeden önce çözümlenmesi gereken takma ad ve otomatik etkinleştirme meta verileri
- çalışma zamanı yüklenmeden önce eklentiyi otomatik etkinleştirmesi gereken kısa model ailesi sahipliği meta verileri
- paketlenmiş uyumluluk bağlantıları ve sözleşme kapsamı için kullanılan statik yetenek sahipliği anlık görüntüleri
- çalışma zamanı yüklenmeden katalog ve doğrulama yüzeyleriyle birleştirilmesi gereken kanala özgü yapılandırma meta verileri
- yapılandırma UI ipuçları

Şunlar için kullanmayın:

- çalışma zamanı davranışını kaydetmek
- kod giriş noktalarını bildirmek
- npm kurulum meta verileri

Bunlar eklenti kodunuza ve `package.json` dosyasına aittir.

## En az örnek

```json
{
  "id": "voice-call",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
```

## Zengin örnek

```json
{
  "id": "openrouter",
  "name": "OpenRouter",
  "description": "OpenRouter provider plugin",
  "version": "1.0.0",
  "providers": ["openrouter"],
  "modelSupport": {
    "modelPrefixes": ["router-"]
  },
  "cliBackends": ["openrouter-cli"],
  "providerAuthEnvVars": {
    "openrouter": ["OPENROUTER_API_KEY"]
  },
  "channelEnvVars": {
    "openrouter-chatops": ["OPENROUTER_CHATOPS_TOKEN"]
  },
  "providerAuthChoices": [
    {
      "provider": "openrouter",
      "method": "api-key",
      "choiceId": "openrouter-api-key",
      "choiceLabel": "OpenRouter API key",
      "groupId": "openrouter",
      "groupLabel": "OpenRouter",
      "optionKey": "openrouterApiKey",
      "cliFlag": "--openrouter-api-key",
      "cliOption": "--openrouter-api-key <key>",
      "cliDescription": "OpenRouter API key",
      "onboardingScopes": ["text-inference"]
    }
  ],
  "uiHints": {
    "apiKey": {
      "label": "API key",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  },
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "apiKey": {
        "type": "string"
      }
    }
  }
}
```

## Üst düzey alan başvurusu

| Alan                                | Gerekli | Tür                              | Anlamı                                                                                                                                                                                                      |
| ----------------------------------- | ------- | -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                                | Evet    | `string`                         | Kanonik eklenti kimliği. `plugins.entries.<id>` içinde kullanılan kimlik budur.                                                                                                                            |
| `configSchema`                      | Evet    | `object`                         | Bu eklentinin yapılandırması için satır içi JSON Schema.                                                                                                                                                    |
| `enabledByDefault`                  | Hayır   | `true`                           | Paketlenmiş bir eklentiyi varsayılan olarak etkin işaretler. Varsayılan olarak devre dışı bırakmak için bunu atlayın veya `true` dışında bir değer ayarlayın.                                            |
| `legacyPluginIds`                   | Hayır   | `string[]`                       | Bu kanonik eklenti kimliğine normalize edilen eski kimlikler.                                                                                                                                               |
| `autoEnableWhenConfiguredProviders` | Hayır   | `string[]`                       | Kimlik doğrulama, yapılandırma veya model referansları bunlardan bahsettiğinde bu eklentiyi otomatik etkinleştirmesi gereken provider kimlikleri.                                                         |
| `kind`                              | Hayır   | `"memory"` \| `"context-engine"` | `plugins.slots.*` tarafından kullanılan, birbirini dışlayan bir eklenti türü bildirir.                                                                                                                    |
| `channels`                          | Hayır   | `string[]`                       | Bu eklentinin sahibi olduğu kanal kimlikleri. Keşif ve yapılandırma doğrulaması için kullanılır.                                                                                                           |
| `providers`                         | Hayır   | `string[]`                       | Bu eklentinin sahibi olduğu provider kimlikleri.                                                                                                                                                            |
| `modelSupport`                      | Hayır   | `object`                         | Çalışma zamanından önce eklentiyi otomatik yüklemek için kullanılan, manifestonun sahip olduğu kısa model ailesi meta verileri.                                                                            |
| `cliBackends`                       | Hayır   | `string[]`                       | Bu eklentinin sahibi olduğu CLI çıkarım backend kimlikleri. Açık yapılandırma referanslarından başlangıç otomatik etkinleştirmesi için kullanılır.                                                        |
| `providerAuthEnvVars`               | Hayır   | `Record<string, string[]>`       | OpenClaw'ın eklenti kodunu yüklemeden inceleyebileceği, düşük maliyetli provider kimlik doğrulama env meta verileri.                                                                                      |
| `channelEnvVars`                    | Hayır   | `Record<string, string[]>`       | OpenClaw'ın eklenti kodunu yüklemeden inceleyebileceği, düşük maliyetli kanal env meta verileri. Bunu, genel başlangıç/yapılandırma yardımcılarının görmesi gereken env tabanlı kanal kurulumu veya kimlik doğrulama yüzeyleri için kullanın. |
| `providerAuthChoices`               | Hayır   | `object[]`                       | Onboarding seçicileri, tercih edilen provider çözümlemesi ve basit CLI bayrağı bağlantısı için düşük maliyetli auth-choice meta verileri.                                                                 |
| `contracts`                         | Hayır   | `object`                         | Konuşma, gerçek zamanlı transkripsiyon, gerçek zamanlı ses, media-understanding, image-generation, music-generation, video-generation, web-fetch, web search ve tool sahipliği için statik paketlenmiş yetenek anlık görüntüsü. |
| `channelConfigs`                    | Hayır   | `Record<string, object>`         | Çalışma zamanı yüklenmeden önce keşif ve doğrulama yüzeyleriyle birleştirilen, manifestonun sahip olduğu kanal yapılandırma meta verileri.                                                                 |
| `skills`                            | Hayır   | `string[]`                       | Eklenti köküne göre göreli skill dizinleri.                                                                                                                                                                 |
| `name`                              | Hayır   | `string`                         | İnsan tarafından okunabilir eklenti adı.                                                                                                                                                                    |
| `description`                       | Hayır   | `string`                         | Eklenti yüzeylerinde gösterilen kısa özet.                                                                                                                                                                  |
| `version`                           | Hayır   | `string`                         | Bilgilendirici eklenti sürümü.                                                                                                                                                                              |
| `uiHints`                           | Hayır   | `Record<string, object>`         | Yapılandırma alanları için UI etiketleri, placeholder'lar ve hassasiyet ipuçları.                                                                                                                          |

## `providerAuthChoices` başvurusu

Her `providerAuthChoices` girişi bir onboarding veya kimlik doğrulama seçeneğini açıklar.
OpenClaw bunu provider çalışma zamanı yüklenmeden önce okur.

| Alan                  | Gerekli | Tür                                              | Anlamı                                                                                                  |
| --------------------- | ------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| `provider`            | Evet    | `string`                                         | Bu seçeneğin ait olduğu provider kimliği.                                                               |
| `method`              | Evet    | `string`                                         | Yönlendirme yapılacak kimlik doğrulama yöntemi kimliği.                                                 |
| `choiceId`            | Evet    | `string`                                         | Onboarding ve CLI akışları tarafından kullanılan kararlı auth-choice kimliği.                           |
| `choiceLabel`         | Hayır   | `string`                                         | Kullanıcıya görünen etiket. Atlanırsa OpenClaw `choiceId` değerine geri düşer.                         |
| `choiceHint`          | Hayır   | `string`                                         | Seçici için kısa yardımcı metin.                                                                        |
| `assistantPriority`   | Hayır   | `number`                                         | Yardımcı tarafından yönlendirilen etkileşimli seçicilerde daha düşük değerler önce sıralanır.          |
| `assistantVisibility` | Hayır   | `"visible"` \| `"manual-only"`                   | Manuel CLI seçimine izin vermeye devam ederken seçeneği yardımcı seçicilerinden gizler.                |
| `deprecatedChoiceIds` | Hayır   | `string[]`                                       | Kullanıcıların bu yeni seçenekle yeniden yönlendirilmesi gereken eski seçenek kimlikleri.              |
| `groupId`             | Hayır   | `string`                                         | İlgili seçenekleri gruplamak için isteğe bağlı grup kimliği.                                            |
| `groupLabel`          | Hayır   | `string`                                         | Bu grup için kullanıcıya görünen etiket.                                                                |
| `groupHint`           | Hayır   | `string`                                         | Grup için kısa yardımcı metin.                                                                          |
| `optionKey`           | Hayır   | `string`                                         | Basit tek bayraklı kimlik doğrulama akışları için iç seçenek anahtarı.                                  |
| `cliFlag`             | Hayır   | `string`                                         | `--openrouter-api-key` gibi CLI bayrak adı.                                                             |
| `cliOption`           | Hayır   | `string`                                         | `--openrouter-api-key <key>` gibi tam CLI seçenek biçimi.                                               |
| `cliDescription`      | Hayır   | `string`                                         | CLI yardımında kullanılan açıklama.                                                                     |
| `onboardingScopes`    | Hayır   | `Array<"text-inference" \| "image-generation">`  | Bu seçeneğin hangi onboarding yüzeylerinde görünmesi gerektiği. Atlanırsa varsayılan `["text-inference"]` olur. |

## `uiHints` başvurusu

`uiHints`, yapılandırma alanı adlarından küçük işleme ipuçlarına giden bir eşlemedir.

```json
{
  "uiHints": {
    "apiKey": {
      "label": "API key",
      "help": "Used for OpenRouter requests",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  }
}
```

Her alan ipucu şunları içerebilir:

| Alan          | Tür        | Anlamı                                  |
| ------------- | ---------- | --------------------------------------- |
| `label`       | `string`   | Kullanıcıya görünen alan etiketi.       |
| `help`        | `string`   | Kısa yardımcı metin.                    |
| `tags`        | `string[]` | İsteğe bağlı UI etiketleri.             |
| `advanced`    | `boolean`  | Alanı gelişmiş olarak işaretler.        |
| `sensitive`   | `boolean`  | Alanı gizli veya hassas olarak işaretler. |
| `placeholder` | `string`   | Form girişleri için placeholder metni.  |

## `contracts` başvurusu

`contracts` alanını yalnızca OpenClaw'ın eklenti çalışma zamanını içe aktarmadan
okuyabileceği statik yetenek sahipliği meta verileri için kullanın.

```json
{
  "contracts": {
    "speechProviders": ["openai"],
    "realtimeTranscriptionProviders": ["openai"],
    "realtimeVoiceProviders": ["openai"],
    "mediaUnderstandingProviders": ["openai", "openai-codex"],
    "imageGenerationProviders": ["openai"],
    "videoGenerationProviders": ["qwen"],
    "webFetchProviders": ["firecrawl"],
    "webSearchProviders": ["gemini"],
    "tools": ["firecrawl_search", "firecrawl_scrape"]
  }
}
```

Her liste isteğe bağlıdır:

| Alan                             | Tür        | Anlamı                                                     |
| -------------------------------- | ---------- | ---------------------------------------------------------- |
| `speechProviders`                | `string[]` | Bu eklentinin sahibi olduğu konuşma provider kimlikleri.   |
| `realtimeTranscriptionProviders` | `string[]` | Bu eklentinin sahibi olduğu gerçek zamanlı transkripsiyon provider kimlikleri. |
| `realtimeVoiceProviders`         | `string[]` | Bu eklentinin sahibi olduğu gerçek zamanlı ses provider kimlikleri. |
| `mediaUnderstandingProviders`    | `string[]` | Bu eklentinin sahibi olduğu media-understanding provider kimlikleri. |
| `imageGenerationProviders`       | `string[]` | Bu eklentinin sahibi olduğu image-generation provider kimlikleri. |
| `videoGenerationProviders`       | `string[]` | Bu eklentinin sahibi olduğu video-generation provider kimlikleri. |
| `webFetchProviders`              | `string[]` | Bu eklentinin sahibi olduğu web-fetch provider kimlikleri. |
| `webSearchProviders`             | `string[]` | Bu eklentinin sahibi olduğu web-search provider kimlikleri. |
| `tools`                          | `string[]` | Paketlenmiş sözleşme denetimleri için bu eklentinin sahibi olduğu ajan tool adları. |

## `channelConfigs` başvurusu

Bir kanal eklentisinin çalışma zamanı yüklenmeden önce düşük maliyetli yapılandırma meta verilerine
ihtiyacı olduğunda `channelConfigs` kullanın.

```json
{
  "channelConfigs": {
    "matrix": {
      "schema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "homeserverUrl": { "type": "string" }
        }
      },
      "uiHints": {
        "homeserverUrl": {
          "label": "Homeserver URL",
          "placeholder": "https://matrix.example.com"
        }
      },
      "label": "Matrix",
      "description": "Matrix homeserver connection",
      "preferOver": ["matrix-legacy"]
    }
  }
}
```

Her kanal girişi şunları içerebilir:

| Alan          | Tür                      | Anlamı                                                                                     |
| ------------- | ------------------------ | ------------------------------------------------------------------------------------------ |
| `schema`      | `object`                 | `channels.<id>` için JSON Schema. Bildirilen her kanal yapılandırma girişi için gereklidir. |
| `uiHints`     | `Record<string, object>` | O kanal yapılandırma bölümü için isteğe bağlı UI etiketleri/placeholder'lar/hassasiyet ipuçları. |
| `label`       | `string`                 | Çalışma zamanı meta verileri henüz hazır değilken seçici ve inceleme yüzeyleriyle birleştirilen kanal etiketi. |
| `description` | `string`                 | İnceleme ve katalog yüzeyleri için kısa kanal açıklaması.                                  |
| `preferOver`  | `string[]`               | Seçim yüzeylerinde bunun öncelikli olması gereken eski veya daha düşük öncelikli eklenti kimlikleri. |

## `modelSupport` başvurusu

OpenClaw, eklenti çalışma zamanı yüklenmeden önce `gpt-5.4` veya `claude-sonnet-4.6` gibi
kısa model kimliklerinden provider eklentinizi çıkarsın istiyorsanız
`modelSupport` kullanın.

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

OpenClaw şu öncelik sırasını uygular:

- açık `provider/model` referansları, sahibi olan `providers` manifest meta verilerini kullanır
- `modelPatterns`, `modelPrefixes` üzerinde önceliklidir
- bir paketlenmemiş eklenti ve bir paketlenmiş eklenti aynı anda eşleşirse paketlenmemiş
  eklenti kazanır
- kalan belirsizlik, kullanıcı veya yapılandırma bir provider belirtinceye kadar yok sayılır

Alanlar:

| Alan            | Tür        | Anlamı                                                                 |
| --------------- | ---------- | ---------------------------------------------------------------------- |
| `modelPrefixes` | `string[]` | Kısa model kimliklerine karşı `startsWith` ile eşleştirilen önekler.   |
| `modelPatterns` | `string[]` | Profil son ekleri kaldırıldıktan sonra kısa model kimliklerine karşı eşleştirilen regex kaynakları. |

Eski üst düzey yetenek anahtarları kullanım dışıdır. `speechProviders`,
`realtimeTranscriptionProviders`, `realtimeVoiceProviders`,
`mediaUnderstandingProviders`, `imageGenerationProviders`,
`videoGenerationProviders`, `webFetchProviders` ve `webSearchProviders`
alanlarını `contracts` altına taşımak için `openclaw doctor --fix` kullanın; normal
manifest yükleme artık bu üst düzey alanları yetenek sahipliği olarak
değerlendirmez.

## Manifesto ile `package.json` arasındaki fark

Bu iki dosya farklı görevler görür:

| Dosya                  | Kullanım amacı                                                                                                                     |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.plugin.json` | Eklenti kodu çalışmadan önce var olması gereken keşif, yapılandırma doğrulaması, auth-choice meta verileri ve UI ipuçları        |
| `package.json`         | npm meta verileri, bağımlılık kurulumu ve giriş noktaları, kurulum engelleme, setup veya katalog meta verileri için kullanılan `openclaw` bloğu |

Bir meta veri parçasının nereye ait olduğundan emin değilseniz şu kuralı kullanın:

- OpenClaw bunu eklenti kodunu yüklemeden önce bilmek zorundaysa `openclaw.plugin.json` içine koyun
- paketleme, giriş dosyaları veya npm kurulum davranışı ile ilgiliyse `package.json` içine koyun

### Keşfi etkileyen `package.json` alanları

Bazı çalışma zamanı öncesi eklenti meta verileri bilerek `openclaw.plugin.json` yerine
`package.json` içindeki `openclaw` bloğunda tutulur.

Önemli örnekler:

| Alan                                                              | Anlamı                                                                                                                                      |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                             | Yerel eklenti giriş noktalarını bildirir.                                                                                                   |
| `openclaw.setupEntry`                                             | Onboarding ve ertelenmiş kanal başlangıcı sırasında kullanılan hafif, yalnızca setup giriş noktası.                                        |
| `openclaw.channel`                                                | Etiketler, docs yolları, takma adlar ve seçim metni gibi düşük maliyetli kanal katalog meta verileri.                                      |
| `openclaw.channel.configuredState`                                | Tam kanal çalışma zamanını yüklemeden "yalnızca env ile kurulum zaten var mı?" sorusunu yanıtlayabilen hafif yapılandırılmış durum denetleyici meta verileri. |
| `openclaw.channel.persistedAuthState`                             | Tam kanal çalışma zamanını yüklemeden "zaten giriş yapılmış bir şey var mı?" sorusunu yanıtlayabilen hafif kalıcı kimlik doğrulama denetleyici meta verileri. |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | Paketlenmiş ve dışarıda yayımlanmış eklentiler için kurulum/güncelleme ipuçları.                                                           |
| `openclaw.install.defaultChoice`                                  | Birden çok kurulum kaynağı mevcut olduğunda tercih edilen kurulum yolu.                                                                     |
| `openclaw.install.minHostVersion`                                 | `>=2026.3.22` gibi bir semver alt sınırı kullanarak desteklenen en düşük OpenClaw host sürümü.                                             |
| `openclaw.install.allowInvalidConfigRecovery`                     | Yapılandırma geçersiz olduğunda dar kapsamlı bir paketlenmiş eklenti yeniden kurulum kurtarma yoluna izin verir.                           |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | Başlangıç sırasında tam kanal eklentisinden önce yalnızca setup kanal yüzeylerinin yüklenmesine izin verir.                               |

`openclaw.install.minHostVersion`, kurulum sırasında ve manifesto kayıt defteri yüklemesinde zorlanır.
Geçersiz değerler reddedilir; daha yeni ama geçerli değerler eski host'larda
eklenti atlanmasına neden olur.

`openclaw.install.allowInvalidConfigRecovery` bilerek dar tutulmuştur. Bu ayar
rastgele bozuk yapılandırmaları kurulabilir hâle getirmez. Bugün yalnızca, eksik
paketlenmiş eklenti yolu veya aynı paketlenmiş eklentiye ait bayat `channels.<id>` girişi gibi
belirli eski paketlenmiş eklenti yükseltme hatalarından kurulum akışlarının kurtulmasına izin verir.
İlgisiz yapılandırma hataları yine kurulumu engeller ve operatörleri
`openclaw doctor --fix` komutuna yönlendirir.

`openclaw.channel.persistedAuthState`, küçük bir denetleyici modül için paket meta verisidir:

```json
{
  "openclaw": {
    "channel": {
      "id": "whatsapp",
      "persistedAuthState": {
        "specifier": "./auth-presence",
        "exportName": "hasAnyWhatsAppAuth"
      }
    }
  }
}
```

Bunu, setup, doctor veya yapılandırılmış durum akışlarının tam kanal eklentisi yüklenmeden önce düşük maliyetli
bir evet/hayır kimlik doğrulama probe'una ihtiyaç duyduğu durumlarda kullanın. Hedef dışa aktarma yalnızca kalıcı durumu
okuyan küçük bir işlev olmalıdır; bunu tam kanal çalışma zamanı barrel'ı üzerinden yönlendirmeyin.

`openclaw.channel.configuredState`, düşük maliyetli yalnızca env yapılandırılmış denetimler için
aynı biçimi izler:

```json
{
  "openclaw": {
    "channel": {
      "id": "telegram",
      "configuredState": {
        "specifier": "./configured-state",
        "exportName": "hasTelegramConfiguredState"
      }
    }
  }
}
```

Bunu, bir kanal yapılandırılmış durumu env veya diğer küçük
çalışma zamanı dışı girdilerden yanıtlayabiliyorsa kullanın. Denetim tam yapılandırma çözümlemesi veya gerçek
kanal çalışma zamanı gerektiriyorsa, bu mantığı bunun yerine eklentinin `config.hasConfiguredState`
hook'unda tutun.

## JSON Schema gereksinimleri

- **Her eklenti bir JSON Schema yayımlamak zorundadır**, hiçbir yapılandırma kabul etmese bile.
- Boş bir şema kabul edilebilir (örneğin `{ "type": "object", "additionalProperties": false }`).
- Şemalar çalışma zamanında değil, yapılandırma okuma/yazma sırasında doğrulanır.

## Doğrulama davranışı

- Bilinmeyen `channels.*` anahtarları, kanal kimliği bir
  eklenti manifestosu tarafından bildirilmedikçe **hatadır**.
- `plugins.entries.<id>`, `plugins.allow`, `plugins.deny` ve `plugins.slots.*`
  alanları **keşfedilebilir** eklenti kimliklerine başvurmak zorundadır. Bilinmeyen kimlikler **hatadır**.
- Bir eklenti kuruluysa ama manifestosu veya şeması bozuk ya da eksikse,
  doğrulama başarısız olur ve Doctor eklenti hatasını bildirir.
- Eklenti yapılandırması varsa ama eklenti **devre dışıysa**, yapılandırma korunur ve
  Doctor + günlüklerde bir **uyarı** gösterilir.

Tam `plugins.*` şeması için [Configuration reference](/tr/gateway/configuration) bölümüne bakın.

## Notlar

- Manifesto, yerel dosya sistemi yüklemeleri dahil **yerel OpenClaw eklentileri için zorunludur**.
- Çalışma zamanı yine eklenti modülünü ayrı olarak yükler; manifesto yalnızca
  keşif + doğrulama içindir.
- Yerel manifestolar JSON5 ile ayrıştırılır, bu nedenle son değer hâlâ bir nesne olduğu sürece
  yorumlar, sondaki virgüller ve tırnaksız anahtarlar kabul edilir.
- Manifesto yükleyicisi yalnızca belgelenmiş manifesto alanlarını okur. Buraya
  özel üst düzey anahtarlar eklemekten kaçının.
- `providerAuthEnvVars`, kimlik doğrulama probe'ları, env işaretleyici
  doğrulaması ve env adlarını incelemek için eklenti çalışma zamanını başlatmaması gereken
  benzer provider kimlik doğrulama yüzeyleri için düşük maliyetli meta veri yoludur.
- `channelEnvVars`, shell env geri dönüşü, setup
  istemleri ve env adlarını incelemek için eklenti çalışma zamanını başlatmaması gereken
  benzer kanal yüzeyleri için düşük maliyetli meta veri yoludur.
- `providerAuthChoices`, auth-choice seçicileri,
  `--auth-choice` çözümlemesi, tercih edilen provider eşlemesi ve basit onboarding
  CLI bayrağı kaydı için provider çalışma zamanı yüklenmeden önce kullanılan düşük maliyetli meta veri yoludur. Provider kodu gerektiren çalışma zamanı sihirbazı
  meta verileri için
  [Provider runtime hooks](/tr/plugins/architecture#provider-runtime-hooks) bölümüne bakın.
- Birbirini dışlayan eklenti türleri `plugins.slots.*` üzerinden seçilir.
  - `kind: "memory"`, `plugins.slots.memory` ile seçilir.
  - `kind: "context-engine"`, `plugins.slots.contextEngine`
    ile seçilir (varsayılan: yerleşik `legacy`).
- `channels`, `providers`, `cliBackends` ve `skills`, bir
  eklenti bunlara ihtiyaç duymuyorsa atlanabilir.
- Eklentiniz yerel modüllere bağlıysa derleme adımlarını ve varsa
  paket yöneticisi allowlist gereksinimlerini belgeleyin (örneğin pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`).

## İlgili

- [Building Plugins](/tr/plugins/building-plugins) — eklentilere başlangıç
- [Plugin Architecture](/tr/plugins/architecture) — iç mimari
- [SDK Overview](/tr/plugins/sdk-overview) — Plugin SDK başvurusu
