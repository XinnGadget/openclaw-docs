---
read_when:
    - Bir OpenClaw eklentisi geliştiriyorsunuz
    - Bir eklenti yapılandırma şeması yayımlamanız veya eklenti doğrulama hatalarında hata ayıklamanız gerekiyor
summary: Eklenti manifestosu + JSON Schema gereksinimleri (katı yapılandırma doğrulaması)
title: Eklenti Manifestosu
x-i18n:
    generated_at: "2026-04-06T03:09:56Z"
    model: gpt-5.4
    provider: openai
    source_hash: f6f915a761cdb5df77eba5d2ccd438c65445bd2ab41b0539d1200e63e8cf2c3a
    source_path: plugins/manifest.md
    workflow: 15
---

# Eklenti manifestosu (openclaw.plugin.json)

Bu sayfa yalnızca **yerel OpenClaw eklenti manifestosu** içindir.

Uyumlu paket düzenleri için [Plugin bundles](/tr/plugins/bundles) bölümüne bakın.

Uyumlu paket biçimleri farklı manifesto dosyaları kullanır:

- Codex paketi: `.codex-plugin/plugin.json`
- Claude paketi: `.claude-plugin/plugin.json` veya manifestosuz varsayılan Claude bileşeni
  düzeni
- Cursor paketi: `.cursor-plugin/plugin.json`

OpenClaw bu paket düzenlerini de otomatik algılar, ancak bunlar burada
açıklanan `openclaw.plugin.json` şemasına göre doğrulanmaz.

Uyumlu paketler için OpenClaw şu anda, düzen OpenClaw çalışma zamanı beklentileriyle
eşleştiğinde, paket meta verilerini ve bildirilen skill köklerini, Claude komut köklerini, Claude paket `settings.json` varsayılanlarını,
Claude paket LSP varsayılanlarını ve desteklenen hook paketlerini okur.

Her yerel OpenClaw eklentisi, **eklenti kökünde** bir `openclaw.plugin.json` dosyası
bulundurmak **zorundadır**. OpenClaw bu manifestoyu, eklenti kodunu
**çalıştırmadan** yapılandırmayı doğrulamak için kullanır. Eksik veya geçersiz manifestolar
eklenti hatası olarak değerlendirilir ve yapılandırma doğrulamasını engeller.

Tam eklenti sistemi kılavuzuna bakın: [Plugins](/tr/tools/plugin).
Yerel yetenek modeli ve mevcut dış uyumluluk rehberi için:
[Capability model](/tr/plugins/architecture#public-capability-model).

## Bu dosya ne yapar

`openclaw.plugin.json`, OpenClaw'ın eklenti kodunuzu yüklemeden önce okuduğu
meta verilerdir.

Şunlar için kullanın:

- eklenti kimliği
- yapılandırma doğrulaması
- eklenti çalışma zamanını başlatmadan kullanılabilir olması gereken kimlik doğrulama ve onboarding meta verileri
- eklenti çalışma zamanı yüklenmeden önce çözülmesi gereken takma ad ve otomatik etkinleştirme meta verileri
- çalışma zamanı yüklenmeden önce eklentiyi otomatik etkinleştirmesi gereken kısa model ailesi sahipliği meta verileri
- paketlenmiş uyumluluk bağlaması ve sözleşme kapsamı için kullanılan statik yetenek sahipliği anlık görüntüleri
- çalışma zamanını yüklemeden katalog ve doğrulama yüzeyleriyle birleştirilmesi gereken kanala özgü yapılandırma meta verileri
- yapılandırma UI ipuçları

Şunlar için kullanmayın:

- çalışma zamanı davranışını kaydetme
- kod giriş noktalarını bildirme
- npm kurulum meta verileri

Bunlar eklenti kodunuz ve `package.json` içine aittir.

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
  "description": "OpenRouter sağlayıcı eklentisi",
  "version": "1.0.0",
  "providers": ["openrouter"],
  "modelSupport": {
    "modelPrefixes": ["router-"]
  },
  "providerAuthEnvVars": {
    "openrouter": ["OPENROUTER_API_KEY"]
  },
  "providerAuthChoices": [
    {
      "provider": "openrouter",
      "method": "api-key",
      "choiceId": "openrouter-api-key",
      "choiceLabel": "OpenRouter API anahtarı",
      "groupId": "openrouter",
      "groupLabel": "OpenRouter",
      "optionKey": "openrouterApiKey",
      "cliFlag": "--openrouter-api-key",
      "cliOption": "--openrouter-api-key <key>",
      "cliDescription": "OpenRouter API anahtarı",
      "onboardingScopes": ["text-inference"]
    }
  ],
  "uiHints": {
    "apiKey": {
      "label": "API anahtarı",
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

| Alan                                | Zorunlu | Tür                              | Anlamı                                                                                                                                                                                                       |
| ----------------------------------- | ------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `id`                                | Evet    | `string`                         | Kanonik eklenti kimliği. Bu, `plugins.entries.<id>` içinde kullanılan kimliktir.                                                                                                                            |
| `configSchema`                      | Evet    | `object`                         | Bu eklentinin yapılandırması için satır içi JSON Schema.                                                                                                                                                    |
| `enabledByDefault`                  | Hayır   | `true`                           | Paketlenmiş bir eklentiyi varsayılan olarak etkin işaretler. Varsayılan olarak devre dışı bırakmak için bunu atlayın veya `true` dışındaki herhangi bir değere ayarlayın.                                 |
| `legacyPluginIds`                   | Hayır   | `string[]`                       | Bu kanonik eklenti kimliğine normalize edilen eski kimlikler.                                                                                                                                               |
| `autoEnableWhenConfiguredProviders` | Hayır   | `string[]`                       | Kimlik doğrulama, yapılandırma veya model başvuruları bunlardan bahsettiğinde bu eklentiyi otomatik etkinleştirmesi gereken sağlayıcı kimlikleri.                                                          |
| `kind`                              | Hayır   | `"memory"` \| `"context-engine"` | `plugins.slots.*` tarafından kullanılan özel bir eklenti türünü bildirir.                                                                                                                                   |
| `channels`                          | Hayır   | `string[]`                       | Bu eklentiye ait kanal kimlikleri. Keşif ve yapılandırma doğrulaması için kullanılır.                                                                                                                       |
| `providers`                         | Hayır   | `string[]`                       | Bu eklentiye ait sağlayıcı kimlikleri.                                                                                                                                                                       |
| `modelSupport`                      | Hayır   | `object`                         | Çalışma zamanından önce eklentiyi otomatik yüklemek için kullanılan, manifestoya ait kısa model ailesi meta verileri.                                                                                       |
| `providerAuthEnvVars`               | Hayır   | `Record<string, string[]>`       | OpenClaw'ın eklenti kodunu yüklemeden inceleyebileceği düşük maliyetli sağlayıcı kimlik doğrulama ortam meta verileri.                                                                                      |
| `providerAuthChoices`               | Hayır   | `object[]`                       | Onboarding seçicileri, tercih edilen sağlayıcı çözümlemesi ve basit CLI bayrağı bağlaması için düşük maliyetli kimlik doğrulama seçeneği meta verileri.                                                    |
| `contracts`                         | Hayır   | `object`                         | Konuşma, gerçek zamanlı transcription, gerçek zamanlı ses, media-understanding, image-generation, music-generation, video-generation, web-fetch, web search ve araç sahipliği için statik paketlenmiş yetenek anlık görüntüsü. |
| `channelConfigs`                    | Hayır   | `Record<string, object>`         | Çalışma zamanı yüklenmeden önce keşif ve doğrulama yüzeyleriyle birleştirilen, manifestoya ait kanal yapılandırma meta verileri.                                                                            |
| `skills`                            | Hayır   | `string[]`                       | Eklenti köküne göreli olarak yüklenecek skill dizinleri.                                                                                                                                                     |
| `name`                              | Hayır   | `string`                         | İnsan tarafından okunabilir eklenti adı.                                                                                                                                                                     |
| `description`                       | Hayır   | `string`                         | Eklenti yüzeylerinde gösterilen kısa özet.                                                                                                                                                                   |
| `version`                           | Hayır   | `string`                         | Bilgilendirme amaçlı eklenti sürümü.                                                                                                                                                                         |
| `uiHints`                           | Hayır   | `Record<string, object>`         | Yapılandırma alanları için UI etiketleri, yer tutucular ve hassasiyet ipuçları.                                                                                                                             |

## providerAuthChoices başvurusu

Her `providerAuthChoices` girdisi bir onboarding veya kimlik doğrulama seçeneğini açıklar.
OpenClaw bunu sağlayıcı çalışma zamanı yüklenmeden önce okur.

| Alan                  | Zorunlu | Tür                                             | Anlamı                                                                                             |
| --------------------- | ------- | ----------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `provider`            | Evet    | `string`                                        | Bu seçeneğin ait olduğu sağlayıcı kimliği.                                                         |
| `method`              | Evet    | `string`                                        | Yönlendirme yapılacak kimlik doğrulama yöntemi kimliği.                                            |
| `choiceId`            | Evet    | `string`                                        | Onboarding ve CLI akışları tarafından kullanılan kararlı kimlik doğrulama seçeneği kimliği.       |
| `choiceLabel`         | Hayır   | `string`                                        | Kullanıcıya dönük etiket. Atlanırsa OpenClaw `choiceId` değerine geri döner.                      |
| `choiceHint`          | Hayır   | `string`                                        | Seçici için kısa yardımcı metin.                                                                   |
| `assistantPriority`   | Hayır   | `number`                                        | Daha düşük değerler, asistan odaklı etkileşimli seçicilerde daha önce sıralanır.                  |
| `assistantVisibility` | Hayır   | `"visible"` \| `"manual-only"`                  | Manuel CLI seçimine izin verirken seçeneği asistan seçicilerinden gizler.                         |
| `deprecatedChoiceIds` | Hayır   | `string[]`                                      | Kullanıcıları bu değiştirme seçeneğine yönlendirmesi gereken eski seçenek kimlikleri.             |
| `groupId`             | Hayır   | `string`                                        | İlgili seçenekleri gruplamak için isteğe bağlı grup kimliği.                                      |
| `groupLabel`          | Hayır   | `string`                                        | O grup için kullanıcıya dönük etiket.                                                             |
| `groupHint`           | Hayır   | `string`                                        | Grup için kısa yardımcı metin.                                                                     |
| `optionKey`           | Hayır   | `string`                                        | Basit tek bayraklı kimlik doğrulama akışları için iç seçenek anahtarı.                            |
| `cliFlag`             | Hayır   | `string`                                        | `--openrouter-api-key` gibi CLI bayrak adı.                                                       |
| `cliOption`           | Hayır   | `string`                                        | `--openrouter-api-key <key>` gibi tam CLI seçenek biçimi.                                         |
| `cliDescription`      | Hayır   | `string`                                        | CLI yardımında kullanılan açıklama.                                                                |
| `onboardingScopes`    | Hayır   | `Array<"text-inference" \| "image-generation">` | Bu seçeneğin hangi onboarding yüzeylerinde görünmesi gerektiği. Atlanırsa varsayılan `["text-inference"]` olur. |

## uiHints başvurusu

`uiHints`, yapılandırma alan adlarından küçük işleme ipuçlarına giden bir eşlemedir.

```json
{
  "uiHints": {
    "apiKey": {
      "label": "API anahtarı",
      "help": "OpenRouter istekleri için kullanılır",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  }
}
```

Her alan ipucu şunları içerebilir:

| Alan          | Tür        | Anlamı                                  |
| ------------- | ---------- | --------------------------------------- |
| `label`       | `string`   | Kullanıcıya dönük alan etiketi.         |
| `help`        | `string`   | Kısa yardımcı metin.                    |
| `tags`        | `string[]` | İsteğe bağlı UI etiketleri.             |
| `advanced`    | `boolean`  | Alanı gelişmiş olarak işaretler.        |
| `sensitive`   | `boolean`  | Alanı gizli veya hassas olarak işaretler. |
| `placeholder` | `string`   | Form girdileri için yer tutucu metin.   |

## contracts başvurusu

`contracts` alanını yalnızca OpenClaw'ın
eklenti çalışma zamanını içe aktarmadan okuyabileceği statik yetenek sahipliği meta verileri için kullanın.

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
| `speechProviders`                | `string[]` | Bu eklentinin sahip olduğu konuşma sağlayıcı kimlikleri.   |
| `realtimeTranscriptionProviders` | `string[]` | Bu eklentinin sahip olduğu gerçek zamanlı transcription sağlayıcı kimlikleri. |
| `realtimeVoiceProviders`         | `string[]` | Bu eklentinin sahip olduğu gerçek zamanlı ses sağlayıcı kimlikleri. |
| `mediaUnderstandingProviders`    | `string[]` | Bu eklentinin sahip olduğu media-understanding sağlayıcı kimlikleri. |
| `imageGenerationProviders`       | `string[]` | Bu eklentinin sahip olduğu image-generation sağlayıcı kimlikleri. |
| `videoGenerationProviders`       | `string[]` | Bu eklentinin sahip olduğu video-generation sağlayıcı kimlikleri. |
| `webFetchProviders`              | `string[]` | Bu eklentinin sahip olduğu web-fetch sağlayıcı kimlikleri. |
| `webSearchProviders`             | `string[]` | Bu eklentinin sahip olduğu web-search sağlayıcı kimlikleri. |
| `tools`                          | `string[]` | Paketlenmiş sözleşme kontrolleri için bu eklentinin sahip olduğu ajan araç adları. |

## channelConfigs başvurusu

Bir kanal eklentisinin çalışma zamanı yüklenmeden önce düşük maliyetli yapılandırma meta verilerine ihtiyacı varsa `channelConfigs` kullanın.

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
          "label": "Homeserver URL'si",
          "placeholder": "https://matrix.example.com"
        }
      },
      "label": "Matrix",
      "description": "Matrix homeserver bağlantısı",
      "preferOver": ["matrix-legacy"]
    }
  }
}
```

Her kanal girdisi şunları içerebilir:

| Alan          | Tür                      | Anlamı                                                                                  |
| ------------- | ------------------------ | --------------------------------------------------------------------------------------- |
| `schema`      | `object`                 | `channels.<id>` için JSON Schema. Bildirilen her kanal yapılandırma girdisi için zorunludur. |
| `uiHints`     | `Record<string, object>` | Bu kanal yapılandırma bölümü için isteğe bağlı UI etiketleri/yer tutucular/hassasiyet ipuçları. |
| `label`       | `string`                 | Çalışma zamanı meta verileri hazır olmadığında seçici ve inceleme yüzeyleriyle birleştirilen kanal etiketi. |
| `description` | `string`                 | İnceleme ve katalog yüzeyleri için kısa kanal açıklaması.                              |
| `preferOver`  | `string[]`               | Bu kanalın seçim yüzeylerinde geride bırakması gereken eski veya daha düşük öncelikli eklenti kimlikleri. |

## modelSupport başvurusu

OpenClaw'ın sağlayıcı eklentinizi,
eklenti çalışma zamanı yüklenmeden önce, `gpt-5.4` veya `claude-sonnet-4.6` gibi
kısa model kimliklerinden çıkarmasını istiyorsanız `modelSupport` kullanın.

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

OpenClaw şu öncelik sırasını uygular:

- açık `provider/model` başvuruları, sahip olan `providers` manifesto meta verilerini kullanır
- `modelPatterns`, `modelPrefixes` değerlerinden daha önceliklidir
- paketlenmemiş bir eklenti ve paketlenmiş bir eklenti aynı anda eşleşirse, paketlenmemiş
  eklenti kazanır
- kalan belirsizlik, kullanıcı veya yapılandırma bir sağlayıcı belirtinceye kadar yok sayılır

Alanlar:

| Alan            | Tür        | Anlamı                                                                 |
| --------------- | ---------- | ---------------------------------------------------------------------- |
| `modelPrefixes` | `string[]` | Kısa model kimliklerine karşı `startsWith` ile eşleştirilen önekler.   |
| `modelPatterns` | `string[]` | Profil soneki kaldırıldıktan sonra kısa model kimliklerine karşı eşleştirilen regex kaynakları. |

Eski üst düzey yetenek anahtarları kullanımdan kaldırılmıştır. `speechProviders`,
`realtimeTranscriptionProviders`, `realtimeVoiceProviders`,
`mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`,
`webFetchProviders` ve `webSearchProviders` alanlarını `contracts` altına
taşımak için `openclaw doctor --fix` kullanın; normal manifesto yükleme artık bu üst düzey alanları yetenek
sahipliği olarak değerlendirmez.

## Manifesto ile package.json karşılaştırması

Bu iki dosya farklı görevler üstlenir:

| Dosya                  | Şunlar için kullanın                                                                                                              |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.plugin.json` | Eklenti kodu çalışmadan önce var olması gereken keşif, yapılandırma doğrulaması, kimlik doğrulama seçeneği meta verileri ve UI ipuçları |
| `package.json`         | npm meta verileri, bağımlılık kurulumu ve giriş noktaları, kurulum kısıtlaması, setup veya katalog meta verileri için kullanılan `openclaw` bloğu |

Bir meta veri parçasının nereye ait olduğundan emin değilseniz şu kuralı kullanın:

- OpenClaw bunu eklenti kodunu yüklemeden önce bilmek zorundaysa, `openclaw.plugin.json` içine koyun
- paketleme, giriş dosyaları veya npm kurulum davranışı ile ilgiliyse, `package.json` içine koyun

### package.json içinde keşfi etkileyen alanlar

Bazı çalışma zamanı öncesi eklenti meta verileri kasıtlı olarak
`openclaw.plugin.json` yerine `package.json` içindeki
`openclaw` bloğunda bulunur.

Önemli örnekler:

| Alan                                                              | Anlamı                                                                                                                                      |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                             | Yerel eklenti giriş noktalarını bildirir.                                                                                                   |
| `openclaw.setupEntry`                                             | Onboarding ve ertelenmiş kanal başlangıcı sırasında kullanılan, yalnızca setup amaçlı hafif giriş noktası.                                 |
| `openclaw.channel`                                                | Etiketler, belge yolları, takma adlar ve seçim metni gibi düşük maliyetli kanal katalog meta verileri.                                     |
| `openclaw.channel.configuredState`                                | Tam kanal çalışma zamanını yüklemeden "yalnızca env ile kurulum zaten mevcut mu?" sorusunu yanıtlayabilen hafif yapılandırılmış durum denetleyici meta verileri. |
| `openclaw.channel.persistedAuthState`                             | Tam kanal çalışma zamanını yüklemeden "zaten oturum açılmış bir şey var mı?" sorusunu yanıtlayabilen hafif kalıcı kimlik doğrulama durumu denetleyici meta verileri. |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | Paketlenmiş ve dışarıda yayımlanan eklentiler için kurulum/güncelleme ipuçları.                                                            |
| `openclaw.install.defaultChoice`                                  | Birden çok kurulum kaynağı mevcut olduğunda tercih edilen kurulum yolu.                                                                     |
| `openclaw.install.minHostVersion`                                 | `>=2026.3.22` gibi bir semver alt sınırı kullanan, desteklenen en düşük OpenClaw host sürümü.                                              |
| `openclaw.install.allowInvalidConfigRecovery`                     | Yapılandırma geçersiz olduğunda dar kapsamlı bir paketlenmiş eklenti yeniden kurulum kurtarma yoluna izin verir.                           |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | Başlangıç sırasında tam kanal eklentisinden önce yalnızca setup amaçlı kanal yüzeylerinin yüklenmesini sağlar.                             |

`openclaw.install.minHostVersion`, kurulum ve manifesto
kayıt defteri yükleme sırasında uygulanır. Geçersiz değerler reddedilir; daha yeni ama geçerli değerler ise
eski host'larda eklentiyi atlar.

`openclaw.install.allowInvalidConfigRecovery` bilerek dar kapsamlıdır. Keyfi bozuk yapılandırmaları kurulabilir hale getirmez.
Bugün yalnızca eksik bir paketlenmiş eklenti yolu veya aynı
paketlenmiş eklenti için eski bir `channels.<id>` girdisi gibi belirli eski paketlenmiş eklenti yükseltme hatalarından
kurulum akışlarının kurtulmasına izin verir. İlgisiz yapılandırma hataları yine kurulumu engeller ve operatörleri
`openclaw doctor --fix` komutuna yönlendirir.

`openclaw.channel.persistedAuthState`, küçük bir denetleyici
modülü için paket meta verisidir:

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

Setup, doctor veya yapılandırılmış durum akışlarının tam kanal eklentisi yüklenmeden önce
düşük maliyetli bir evet/hayır kimlik doğrulama yoklamasına ihtiyaç duyduğu durumlarda bunu kullanın. Hedef export yalnızca
kalıcı durumu okuyan küçük bir işlev olmalıdır; bunu tam kanal çalışma zamanı barrel'ı üzerinden yönlendirmeyin.

`openclaw.channel.configuredState`, düşük maliyetli yalnızca env tabanlı
yapılandırılmış kontroller için aynı biçimi izler:

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

Bir kanal yapılandırılmış durumu env veya diğer küçük
çalışma zamanı dışı girdilerden yanıtlayabiliyorsa bunu kullanın. Kontrol tam yapılandırma çözümlemesi veya gerçek
kanal çalışma zamanı gerektiriyorsa, bu mantığı onun yerine eklentinin `config.hasConfiguredState`
hook'unda tutun.

## JSON Schema gereksinimleri

- **Her eklenti bir JSON Schema yayımlamak zorundadır**, hiçbir yapılandırmayı kabul etmese bile.
- Boş bir şema kabul edilebilir (örneğin, `{ "type": "object", "additionalProperties": false }`).
- Şemalar çalışma zamanında değil, yapılandırma okuma/yazma sırasında doğrulanır.

## Doğrulama davranışı

- Bilinmeyen `channels.*` anahtarları, kanal kimliği bir
  eklenti manifestosu tarafından bildirilmemişse **hatadır**.
- `plugins.entries.<id>`, `plugins.allow`, `plugins.deny` ve `plugins.slots.*`
  **keşfedilebilir** eklenti kimliklerine başvurmalıdır. Bilinmeyen kimlikler **hatadır**.
- Bir eklenti kuruluysa ancak manifestosu veya şeması bozuk ya da eksikse,
  doğrulama başarısız olur ve Doctor eklenti hatasını bildirir.
- Eklenti yapılandırması varsa ancak eklenti **devre dışıysa**, yapılandırma korunur ve
  Doctor + günlüklerde bir **uyarı** gösterilir.

Tam `plugins.*` şeması için [Configuration reference](/tr/gateway/configuration) bölümüne bakın.

## Notlar

- Manifesto, yerel dosya sistemi yüklemeleri dahil **yerel OpenClaw eklentileri için zorunludur**.
- Çalışma zamanı yine eklenti modülünü ayrı olarak yükler; manifesto yalnızca
  keşif + doğrulama içindir.
- Yerel manifestolar JSON5 ile ayrıştırılır; bu nedenle son değer hâlâ bir nesne olduğu sürece
  yorumlar, sondaki virgüller ve tırnaksız anahtarlar kabul edilir.
- Manifesto yükleyicisi yalnızca belgelenmiş manifesto alanlarını okur. Buraya
  özel üst düzey anahtarlar eklemekten kaçının.
- `providerAuthEnvVars`, env adlarını incelemek için eklenti
  çalışma zamanını başlatmaması gereken kimlik doğrulama yoklamaları, env işaretleyici
  doğrulaması ve benzeri sağlayıcı kimlik doğrulama yüzeyleri için düşük maliyetli meta veri yoludur.
- `providerAuthChoices`, kimlik doğrulama seçeneği seçicileri,
  `--auth-choice` çözümlemesi, tercih edilen sağlayıcı eşlemesi ve sağlayıcı çalışma zamanı yüklenmeden önce basit onboarding
  CLI bayrağı kaydı için düşük maliyetli meta veri yoludur. Sağlayıcı kodu gerektiren çalışma zamanı sihirbaz
  meta verileri için
  [Provider runtime hooks](/tr/plugins/architecture#provider-runtime-hooks) bölümüne bakın.
- Özel eklenti türleri `plugins.slots.*` üzerinden seçilir.
  - `kind: "memory"`, `plugins.slots.memory` tarafından seçilir.
  - `kind: "context-engine"`, `plugins.slots.contextEngine`
    tarafından seçilir (varsayılan: yerleşik `legacy`).
- `channels`, `providers` ve `skills`, bir
  eklentinin bunlara ihtiyacı yoksa atlanabilir.
- Eklentiniz yerel modüllere bağımlıysa, derleme adımlarını ve tüm
  paket yöneticisi allowlist gereksinimlerini belgeleyin (örneğin, pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`).

## İlgili

- [Building Plugins](/tr/plugins/building-plugins) — eklentilere başlarken
- [Plugin Architecture](/tr/plugins/architecture) — iç mimari
- [SDK Overview](/tr/plugins/sdk-overview) — Plugin SDK başvurusu
