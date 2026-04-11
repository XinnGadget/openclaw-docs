---
read_when:
    - Bir OpenClaw plugin'i oluşturuyorsunuz
    - Bir plugin yapılandırma şeması sağlamanız veya plugin doğrulama hatalarında hata ayıklamanız gerekiyor
summary: Plugin manifesti + JSON şema gereksinimleri (katı yapılandırma doğrulaması)
title: Plugin Manifesti
x-i18n:
    generated_at: "2026-04-11T15:15:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: 42d454b560a8f6bf714c5d782f34216be1216d83d0a319d08d7349332c91a9e4
    source_path: plugins/manifest.md
    workflow: 15
---

# Plugin manifesti (`openclaw.plugin.json`)

Bu sayfa yalnızca **yerel OpenClaw plugin manifesti** içindir.

Uyumlu paket düzenleri için bkz. [Plugin paketleri](/tr/plugins/bundles).

Uyumlu paket biçimleri farklı manifest dosyaları kullanır:

- Codex paketi: `.codex-plugin/plugin.json`
- Claude paketi: `.claude-plugin/plugin.json` veya manifest içermeyen varsayılan Claude bileşen
  düzeni
- Cursor paketi: `.cursor-plugin/plugin.json`

OpenClaw bu paket düzenlerini de otomatik olarak algılar, ancak bunlar burada
açıklanan `openclaw.plugin.json` şemasına göre doğrulanmaz.

Uyumlu paketler için OpenClaw şu anda, düzen OpenClaw çalışma zamanı beklentileriyle
eşleştiğinde, paket meta verilerini ve bildirilen skill köklerini, Claude komut köklerini, Claude paketi `settings.json` varsayılanlarını,
Claude paketi LSP varsayılanlarını ve desteklenen hook paketlerini okur.

Her yerel OpenClaw plugin'i, **plugin kökünde** bir `openclaw.plugin.json` dosyası
bulundurmak **zorundadır**. OpenClaw bu manifesti, plugin yapılandırmasını
**plugin kodunu çalıştırmadan** doğrulamak için kullanır. Eksik veya geçersiz
manifestler plugin hatası olarak değerlendirilir ve yapılandırma doğrulamasını engeller.

Tam plugin sistemi kılavuzuna bakın: [Plugins](/tr/tools/plugin).
Yerel yetenek modeli ve güncel dış uyumluluk rehberi için:
[Yetenek modeli](/tr/plugins/architecture#public-capability-model).

## Bu dosya ne işe yarar

`openclaw.plugin.json`, OpenClaw'un plugin kodunuzu yüklemeden önce okuduğu
meta verilerdir.

Şunlar için kullanın:

- plugin kimliği
- yapılandırma doğrulaması
- plugin çalışma zamanını başlatmadan kullanılabilir olması gereken auth ve onboarding meta verileri
- çalışma zamanı yüklenmeden önce kontrol düzlemi yüzeylerinin inceleyebileceği düşük maliyetli etkinleştirme ipuçları
- çalışma zamanı yüklenmeden önce kurulum/onboarding yüzeylerinin inceleyebileceği düşük maliyetli kurulum tanımlayıcıları
- plugin çalışma zamanı yüklenmeden önce çözümlenmesi gereken takma ad ve otomatik etkinleştirme meta verileri
- çalışma zamanı yüklenmeden önce plugin'i otomatik etkinleştirmesi gereken kısa model ailesi sahipliği meta verileri
- paketlenmiş uyumluluk bağlantıları ve sözleşme kapsamı için kullanılan statik yetenek sahipliği anlık görüntüleri
- çalışma zamanı yüklenmeden katalog ve doğrulama yüzeylerine birleştirilmesi gereken kanala özgü yapılandırma meta verileri
- yapılandırma arayüzü ipuçları

Şunlar için kullanmayın:

- çalışma zamanı davranışını kaydetmek
- kod giriş noktalarını bildirmek
- npm kurulum meta verileri

Bunlar plugin kodunuza ve `package.json` dosyasına aittir.

## Minimal örnek

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
  "providerAuthAliases": {
    "openrouter-coding": "openrouter"
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

| Alan                                | Zorunlu | Tür                              | Anlamı                                                                                                                                                                                                       |
| ----------------------------------- | ------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `id`                                | Evet    | `string`                         | Kanonik plugin kimliği. Bu, `plugins.entries.<id>` içinde kullanılan kimliktir.                                                                                                                              |
| `configSchema`                      | Evet    | `object`                         | Bu plugin'in yapılandırması için satır içi JSON Şeması.                                                                                                                                                      |
| `enabledByDefault`                  | Hayır   | `true`                           | Paketlenmiş bir plugin'in varsayılan olarak etkin olduğunu belirtir. Plugin'i varsayılan olarak devre dışı bırakmak için bunu atlayın veya `true` dışındaki herhangi bir değere ayarlayın.                 |
| `legacyPluginIds`                   | Hayır   | `string[]`                       | Bu kanonik plugin kimliğine normalize edilen eski kimlikler.                                                                                                                                                 |
| `autoEnableWhenConfiguredProviders` | Hayır   | `string[]`                       | Auth, yapılandırma veya model başvuruları bunlardan bahsettiğinde bu plugin'i otomatik olarak etkinleştirmesi gereken provider kimlikleri.                                                                  |
| `kind`                              | Hayır   | `"memory"` \| `"context-engine"` | `plugins.slots.*` tarafından kullanılan özel bir plugin türünü bildirir.                                                                                                                                     |
| `channels`                          | Hayır   | `string[]`                       | Bu plugin'e ait kanal kimlikleri. Keşif ve yapılandırma doğrulaması için kullanılır.                                                                                                                         |
| `providers`                         | Hayır   | `string[]`                       | Bu plugin'e ait provider kimlikleri.                                                                                                                                                                         |
| `modelSupport`                      | Hayır   | `object`                         | Çalışma zamanından önce plugin'i otomatik yüklemek için kullanılan, manifest sahipli kısa model ailesi meta verileri.                                                                                        |
| `cliBackends`                       | Hayır   | `string[]`                       | Bu plugin'e ait CLI çıkarım backend kimlikleri. Açık yapılandırma başvurularından başlangıçta otomatik etkinleştirme için kullanılır.                                                                       |
| `commandAliases`                    | Hayır   | `object[]`                       | Çalışma zamanı yüklenmeden önce plugin farkındalıklı yapılandırma ve CLI tanılamaları üretmesi gereken, bu plugin'e ait komut adları.                                                                        |
| `providerAuthEnvVars`               | Hayır   | `Record<string, string[]>`       | OpenClaw'un plugin kodunu yüklemeden inceleyebileceği düşük maliyetli provider auth ortam değişkeni meta verileri.                                                                                          |
| `providerAuthAliases`               | Hayır   | `Record<string, string>`         | Auth araması için başka bir provider kimliğini yeniden kullanması gereken provider kimlikleri; örneğin temel provider API anahtarını ve auth profillerini paylaşan bir coding provider.                     |
| `channelEnvVars`                    | Hayır   | `Record<string, string[]>`       | OpenClaw'un plugin kodunu yüklemeden inceleyebileceği düşük maliyetli kanal ortam değişkeni meta verileri. Bunu, genel başlangıç/yapılandırma yardımcılarının görmesi gereken env tabanlı kanal kurulumu veya auth yüzeyleri için kullanın. |
| `providerAuthChoices`               | Hayır   | `object[]`                       | Onboarding seçicileri, tercih edilen provider çözümleme ve basit CLI bayrağı bağlama için düşük maliyetli auth seçeneği meta verileri.                                                                      |
| `activation`                        | Hayır   | `object`                         | Provider, komut, kanal, rota ve yetenek tetiklemeli yükleme için düşük maliyetli etkinleştirme ipuçları. Yalnızca meta veri; gerçek davranış yine plugin çalışma zamanına aittir.                           |
| `setup`                             | Hayır   | `object`                         | Keşif ve kurulum yüzeylerinin plugin çalışma zamanını yüklemeden inceleyebileceği düşük maliyetli kurulum/onboarding tanımlayıcıları.                                                                        |
| `contracts`                         | Hayır   | `object`                         | Speech, gerçek zamanlı transcription, gerçek zamanlı voice, media-understanding, image-generation, music-generation, video-generation, web-fetch, web search ve tool sahipliği için statik paketlenmiş yetenek anlık görüntüsü. |
| `channelConfigs`                    | Hayır   | `Record<string, object>`         | Çalışma zamanı yüklenmeden önce keşif ve doğrulama yüzeylerine birleştirilen, manifest sahipli kanal yapılandırma meta verileri.                                                                              |
| `skills`                            | Hayır   | `string[]`                       | Plugin köküne göre göreli olarak yüklenecek Skills dizinleri.                                                                                                                                                |
| `name`                              | Hayır   | `string`                         | İnsan tarafından okunabilir plugin adı.                                                                                                                                                                      |
| `description`                       | Hayır   | `string`                         | Plugin yüzeylerinde gösterilen kısa özet.                                                                                                                                                                    |
| `version`                           | Hayır   | `string`                         | Bilgilendirici plugin sürümü.                                                                                                                                                                                |
| `uiHints`                           | Hayır   | `Record<string, object>`         | Yapılandırma alanları için UI etiketleri, yer tutucular ve hassasiyet ipuçları.                                                                                                                              |

## providerAuthChoices başvurusu

Her `providerAuthChoices` girdisi bir onboarding veya auth seçeneğini açıklar.
OpenClaw bunu provider çalışma zamanı yüklenmeden önce okur.

| Alan                  | Zorunlu | Tür                                               | Anlamı                                                                                                     |
| --------------------- | ------- | ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `provider`            | Evet    | `string`                                          | Bu seçeneğin ait olduğu provider kimliği.                                                                  |
| `method`              | Evet    | `string`                                          | Yönlendirilecek auth yöntemi kimliği.                                                                      |
| `choiceId`            | Evet    | `string`                                          | Onboarding ve CLI akışlarında kullanılan kararlı auth seçeneği kimliği.                                   |
| `choiceLabel`         | Hayır   | `string`                                          | Kullanıcıya gösterilen etiket. Atlanırsa OpenClaw `choiceId` değerine geri döner.                         |
| `choiceHint`          | Hayır   | `string`                                          | Seçici için kısa yardımcı metin.                                                                           |
| `assistantPriority`   | Hayır   | `number`                                          | Daha düşük değerler, asistan tarafından yönlendirilen etkileşimli seçicilerde daha önce sıralanır.        |
| `assistantVisibility` | Hayır   | `"visible"` \| `"manual-only"`                    | Manuel CLI seçimine yine izin verirken seçeneği asistan seçicilerinden gizler.                            |
| `deprecatedChoiceIds` | Hayır   | `string[]`                                        | Kullanıcıları bu yerine geçen seçeneğe yönlendirmesi gereken eski seçenek kimlikleri.                     |
| `groupId`             | Hayır   | `string`                                          | İlgili seçenekleri gruplamak için isteğe bağlı grup kimliği.                                               |
| `groupLabel`          | Hayır   | `string`                                          | Bu grup için kullanıcıya gösterilen etiket.                                                                |
| `groupHint`           | Hayır   | `string`                                          | Grup için kısa yardımcı metin.                                                                             |
| `optionKey`           | Hayır   | `string`                                          | Basit tek bayraklı auth akışları için dahili seçenek anahtarı.                                             |
| `cliFlag`             | Hayır   | `string`                                          | `--openrouter-api-key` gibi CLI bayrağı adı.                                                               |
| `cliOption`           | Hayır   | `string`                                          | `--openrouter-api-key <key>` gibi tam CLI seçenek biçimi.                                                  |
| `cliDescription`      | Hayır   | `string`                                          | CLI yardımında kullanılan açıklama.                                                                        |
| `onboardingScopes`    | Hayır   | `Array<"text-inference" \| "image-generation">`   | Bu seçeneğin hangi onboarding yüzeylerinde görünmesi gerektiği. Atlanırsa varsayılan olarak `["text-inference"]` kullanılır. |

## commandAliases başvurusu

Bir plugin, kullanıcıların yanlışlıkla `plugins.allow` içine koyabileceği veya kök CLI komutu olarak çalıştırmayı deneyebileceği bir çalışma zamanı komut adına sahipse `commandAliases` kullanın. OpenClaw bu meta veriyi, plugin çalışma zamanı kodunu içe aktarmadan tanılama için kullanır.

```json
{
  "commandAliases": [
    {
      "name": "dreaming",
      "kind": "runtime-slash",
      "cliCommand": "memory"
    }
  ]
}
```

| Alan         | Zorunlu | Tür               | Anlamı                                                                      |
| ------------ | ------- | ----------------- | ---------------------------------------------------------------------------- |
| `name`       | Evet    | `string`          | Bu plugin'e ait komut adı.                                                   |
| `kind`       | Hayır   | `"runtime-slash"` | Takma adı, kök CLI komutu yerine bir sohbet slash komutu olarak işaretler.   |
| `cliCommand` | Hayır   | `string`          | Varsa, CLI işlemleri için önerilecek ilişkili kök CLI komutu.                |

## activation başvurusu

Plugin daha sonra hangi kontrol düzlemi olaylarının onu etkinleştirmesi gerektiğini düşük maliyetle bildirebiliyorsa `activation` kullanın.

Bu blok yalnızca meta veridir. Çalışma zamanı davranışını kaydetmez ve `register(...)`, `setupEntry` veya diğer çalışma zamanı/plugin giriş noktalarının yerine geçmez.

```json
{
  "activation": {
    "onProviders": ["openai"],
    "onCommands": ["models"],
    "onChannels": ["web"],
    "onRoutes": ["gateway-webhook"],
    "onCapabilities": ["provider", "tool"]
  }
}
```

| Alan             | Zorunlu | Tür                                                  | Anlamı                                                            |
| ---------------- | ------- | ---------------------------------------------------- | ----------------------------------------------------------------- |
| `onProviders`    | Hayır   | `string[]`                                           | İstendiğinde bu plugin'i etkinleştirmesi gereken provider kimlikleri. |
| `onCommands`     | Hayır   | `string[]`                                           | Bu plugin'i etkinleştirmesi gereken komut kimlikleri.             |
| `onChannels`     | Hayır   | `string[]`                                           | Bu plugin'i etkinleştirmesi gereken kanal kimlikleri.             |
| `onRoutes`       | Hayır   | `string[]`                                           | Bu plugin'i etkinleştirmesi gereken rota türleri.                 |
| `onCapabilities` | Hayır   | `Array<"provider" \| "channel" \| "tool" \| "hook">` | Kontrol düzlemi etkinleştirme planlamasında kullanılan geniş yetenek ipuçları. |

## setup başvurusu

Kurulum ve onboarding yüzeyleri çalışma zamanı yüklenmeden önce plugin'e ait düşük maliyetli meta verilere ihtiyaç duyuyorsa `setup` kullanın.

```json
{
  "setup": {
    "providers": [
      {
        "id": "openai",
        "authMethods": ["api-key"],
        "envVars": ["OPENAI_API_KEY"]
      }
    ],
    "cliBackends": ["openai-cli"],
    "configMigrations": ["legacy-openai-auth"],
    "requiresRuntime": false
  }
}
```

Üst düzey `cliBackends` geçerliliğini korur ve CLI çıkarım backend'lerini tanımlamaya devam eder. `setup.cliBackends`, yalnızca meta veri olarak kalması gereken kontrol düzlemi/kurulum akışları için kurulum odaklı tanımlayıcı yüzeyidir.

### setup.providers başvurusu

| Alan          | Zorunlu | Tür        | Anlamı                                                                                 |
| ------------- | ------- | ---------- | --------------------------------------------------------------------------------------- |
| `id`          | Evet    | `string`   | Kurulum veya onboarding sırasında gösterilen provider kimliği.                          |
| `authMethods` | Hayır   | `string[]` | Tam çalışma zamanı yüklenmeden bu provider'ın desteklediği kurulum/auth yöntem kimlikleri. |
| `envVars`     | Hayır   | `string[]` | Genel kurulum/durum yüzeylerinin plugin çalışma zamanı yüklenmeden kontrol edebileceği ortam değişkenleri. |

### setup alanları

| Alan               | Zorunlu | Tür        | Anlamı                                                                    |
| ------------------ | ------- | ---------- | -------------------------------------------------------------------------- |
| `providers`        | Hayır   | `object[]` | Kurulum ve onboarding sırasında gösterilen provider kurulum tanımlayıcıları. |
| `cliBackends`      | Hayır   | `string[]` | Tam çalışma zamanı etkinleştirmesi olmadan kullanılabilen kurulum zamanı backend kimlikleri. |
| `configMigrations` | Hayır   | `string[]` | Bu plugin'in kurulum yüzeyine ait yapılandırma geçişi kimlikleri.         |
| `requiresRuntime`  | Hayır   | `boolean`  | Tanımlayıcı aramasından sonra kurulumun hâlâ plugin çalışma zamanını çalıştırmaya ihtiyaç duyup duymadığı. |

## uiHints başvurusu

`uiHints`, yapılandırma alan adlarından küçük işleme ipuçlarına giden bir eşlemedir.

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

| Alan          | Tür        | Anlamı                                |
| ------------- | ---------- | ------------------------------------- |
| `label`       | `string`   | Kullanıcıya gösterilen alan etiketi.  |
| `help`        | `string`   | Kısa yardımcı metin.                  |
| `tags`        | `string[]` | İsteğe bağlı UI etiketleri.           |
| `advanced`    | `boolean`  | Alanı gelişmiş olarak işaretler.      |
| `sensitive`   | `boolean`  | Alanı gizli veya hassas olarak işaretler. |
| `placeholder` | `string`   | Form girdileri için yer tutucu metin. |

## contracts başvurusu

OpenClaw'un plugin çalışma zamanını içe aktarmadan okuyabildiği statik yetenek sahipliği meta verileri için yalnızca `contracts` kullanın.

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

| Alan                             | Tür        | Anlamı                                                         |
| -------------------------------- | ---------- | --------------------------------------------------------------- |
| `speechProviders`                | `string[]` | Bu plugin'in sahip olduğu speech provider kimlikleri.           |
| `realtimeTranscriptionProviders` | `string[]` | Bu plugin'in sahip olduğu gerçek zamanlı transcription provider kimlikleri. |
| `realtimeVoiceProviders`         | `string[]` | Bu plugin'in sahip olduğu gerçek zamanlı voice provider kimlikleri. |
| `mediaUnderstandingProviders`    | `string[]` | Bu plugin'in sahip olduğu media-understanding provider kimlikleri. |
| `imageGenerationProviders`       | `string[]` | Bu plugin'in sahip olduğu image-generation provider kimlikleri. |
| `videoGenerationProviders`       | `string[]` | Bu plugin'in sahip olduğu video-generation provider kimlikleri. |
| `webFetchProviders`              | `string[]` | Bu plugin'in sahip olduğu web-fetch provider kimlikleri.        |
| `webSearchProviders`             | `string[]` | Bu plugin'in sahip olduğu web-search provider kimlikleri.       |
| `tools`                          | `string[]` | Paketlenmiş sözleşme kontrolleri için bu plugin'in sahip olduğu ajan tool adları. |

## channelConfigs başvurusu

Bir kanal plugin'i çalışma zamanı yüklenmeden önce düşük maliyetli yapılandırma meta verilerine ihtiyaç duyuyorsa `channelConfigs` kullanın.

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

Her kanal girdisi şunları içerebilir:

| Alan         | Tür                      | Anlamı                                                                                      |
| ------------ | ------------------------ | ------------------------------------------------------------------------------------------- |
| `schema`      | `object`                 | `channels.<id>` için JSON Şeması. Bildirilen her kanal yapılandırma girdisi için zorunludur. |
| `uiHints`     | `Record<string, object>` | Bu kanal yapılandırma bölümü için isteğe bağlı UI etiketleri/yer tutucular/hassas ipuçları. |
| `label`       | `string`                 | Çalışma zamanı meta verileri hazır olmadığında seçici ve inceleme yüzeylerine birleştirilen kanal etiketi. |
| `description` | `string`                 | İnceleme ve katalog yüzeyleri için kısa kanal açıklaması.                                   |
| `preferOver`  | `string[]`               | Bu kanalın seçim yüzeylerinde geride bırakması gereken eski veya daha düşük öncelikli plugin kimlikleri. |

## modelSupport başvurusu

OpenClaw'un, plugin çalışma zamanı yüklenmeden önce `gpt-5.4` veya `claude-sonnet-4.6` gibi kısa model kimliklerinden provider plugin'inizi çıkarsaması gerekiyorsa `modelSupport` kullanın.

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

OpenClaw şu öncelik sırasını uygular:

- açık `provider/model` başvuruları, sahip olan `providers` manifest meta verilerini kullanır
- `modelPatterns`, `modelPrefixes` değerlerinden önce gelir
- paketlenmemiş bir plugin ile paketlenmiş bir plugin aynı anda eşleşirse, paketlenmemiş plugin kazanır
- kalan belirsizlik, kullanıcı veya yapılandırma bir provider belirtinceye kadar yok sayılır

Alanlar:

| Alan            | Tür        | Anlamı                                                                       |
| --------------- | ---------- | ----------------------------------------------------------------------------- |
| `modelPrefixes` | `string[]` | Kısa model kimliklerine karşı `startsWith` ile eşleştirilen önekler.          |
| `modelPatterns` | `string[]` | Profil soneki kaldırıldıktan sonra kısa model kimliklerine karşı eşleştirilen regex kaynakları. |

Eski üst düzey yetenek anahtarları kullanımdan kaldırılmıştır. `speechProviders`, `realtimeTranscriptionProviders`, `realtimeVoiceProviders`, `mediaUnderstandingProviders`, `imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders` ve `webSearchProviders` alanlarını `contracts` altına taşımak için `openclaw doctor --fix` kullanın; normal manifest yükleme artık bu üst düzey alanları yetenek sahipliği olarak değerlendirmez.

## Manifest ve package.json karşılaştırması

İki dosya farklı işler görür:

| Dosya                  | Kullanım amacı                                                                                                                     |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.plugin.json` | Plugin kodu çalışmadan önce var olması gereken keşif, yapılandırma doğrulaması, auth seçeneği meta verileri ve UI ipuçları       |
| `package.json`         | npm meta verileri, bağımlılık kurulumu ve giriş noktaları, kurulum engelleme, setup veya katalog meta verileri için kullanılan `openclaw` bloğu |

Bir meta verinin nereye ait olduğundan emin değilseniz şu kuralı kullanın:

- OpenClaw bunun plugin kodunu yüklemeden önce bilmek zorundaysa, `openclaw.plugin.json` içine koyun
- paketleme, giriş dosyaları veya npm kurulum davranışıyla ilgiliyse, `package.json` içine koyun

### Keşfi etkileyen package.json alanları

Bazı çalışma zamanı öncesi plugin meta verileri, kasıtlı olarak `openclaw.plugin.json` yerine `package.json` içindeki `openclaw` bloğunda bulunur.

Önemli örnekler:

| Alan                                                              | Anlamı                                                                                                                                       |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                             | Yerel plugin giriş noktalarını bildirir.                                                                                                     |
| `openclaw.setupEntry`                                             | Onboarding ve ertelenmiş kanal başlangıcı sırasında kullanılan hafif, yalnızca setup amaçlı giriş noktası.                                 |
| `openclaw.channel`                                                | Etiketler, belge yolları, takma adlar ve seçim metni gibi düşük maliyetli kanal katalog meta verileri.                                      |
| `openclaw.channel.configuredState`                                | Tam kanal çalışma zamanını yüklemeden "yalnızca env tabanlı kurulum zaten var mı?" sorusuna yanıt verebilen hafif yapılandırılmış durum denetleyici meta verileri. |
| `openclaw.channel.persistedAuthState`                             | Tam kanal çalışma zamanını yüklemeden "zaten giriş yapılmış bir şey var mı?" sorusuna yanıt verebilen hafif kalıcı auth durumu denetleyici meta verileri. |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | Paketlenmiş ve haricen yayımlanan plugin'ler için kurulum/güncelleme ipuçları.                                                              |
| `openclaw.install.defaultChoice`                                  | Birden fazla kurulum kaynağı mevcut olduğunda tercih edilen kurulum yolu.                                                                    |
| `openclaw.install.minHostVersion`                                 | `>=2026.3.22` gibi bir semver alt sınırı kullanan, desteklenen minimum OpenClaw host sürümü.                                                |
| `openclaw.install.allowInvalidConfigRecovery`                     | Yapılandırma geçersiz olduğunda dar kapsamlı bir paketlenmiş plugin yeniden kurulum kurtarma yoluna izin verir.                             |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | Başlangıç sırasında tam kanal plugin'inden önce yalnızca setup amaçlı kanal yüzeylerinin yüklenmesini sağlar.                              |

`openclaw.install.minHostVersion`, kurulum ve manifest kayıt defteri yükleme sırasında uygulanır. Geçersiz değerler reddedilir; daha yeni ama geçerli değerler, eski host'larda plugin'i atlar.

`openclaw.install.allowInvalidConfigRecovery` kasıtlı olarak dar kapsamlıdır. Rastgele bozuk yapılandırmaların kurulabilir olmasını sağlamaz. Bugün yalnızca, eksik paketlenmiş plugin yolu veya aynı paketlenmiş plugin için bayat bir `channels.<id>` girdisi gibi belirli eski paketlenmiş plugin yükseltme hatalarından kurulum akışlarının kurtulmasına izin verir. İlgisiz yapılandırma hataları yine kurulumu engeller ve operatörleri `openclaw doctor --fix` komutuna yönlendirir.

`openclaw.channel.persistedAuthState`, küçük bir denetleyici modülü için paket meta verisidir:

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

Setup, doctor veya yapılandırılmış durum akışlarının tam kanal plugin'i yüklenmeden önce ucuz bir evet/hayır auth yoklamasına ihtiyaç duyduğu durumlarda bunu kullanın. Hedef export, yalnızca kalıcı durumu okuyan küçük bir işlev olmalıdır; bunu tam kanal çalışma zamanı barrel'ı üzerinden yönlendirmeyin.

`openclaw.channel.configuredState`, düşük maliyetli yalnızca env tabanlı yapılandırılmış durum denetimleri için aynı biçimi izler:

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

Bir kanal env veya diğer küçük çalışma zamanı dışı girdilerden yapılandırılmış durumu yanıtlayabiliyorsa bunu kullanın. Denetim tam yapılandırma çözümlemesine veya gerçek kanal çalışma zamanına ihtiyaç duyuyorsa, bu mantığı onun yerine plugin `config.hasConfiguredState` hook'unda tutun.

## JSON Şema gereksinimleri

- **Her plugin bir JSON Şeması bulundurmak zorundadır**, yapılandırma kabul etmese bile.
- Boş bir şema kabul edilebilir (örneğin `{ "type": "object", "additionalProperties": false }`).
- Şemalar çalışma zamanında değil, yapılandırma okuma/yazma anında doğrulanır.

## Doğrulama davranışı

- Bilinmeyen `channels.*` anahtarları, kanal kimliği bir plugin manifesti tarafından bildirilmedikçe **hatadır**.
- `plugins.entries.<id>`, `plugins.allow`, `plugins.deny` ve `plugins.slots.*`, **keşfedilebilir** plugin kimliklerine başvurmak zorundadır. Bilinmeyen kimlikler **hatadır**.
- Bir plugin kuruluysa ancak bozuk veya eksik bir manifest ya da şemaya sahipse, doğrulama başarısız olur ve Doctor plugin hatasını bildirir.
- Plugin yapılandırması mevcutsa ancak plugin **devre dışıysa**, yapılandırma korunur ve Doctor + günlüklerde bir **uyarı** gösterilir.

Tam `plugins.*` şeması için bkz. [Yapılandırma başvurusu](/tr/gateway/configuration).

## Notlar

- Manifest, yerel dosya sistemi yüklemeleri dahil **yerel OpenClaw plugin'leri için zorunludur**.
- Çalışma zamanı yine plugin modülünü ayrı olarak yükler; manifest yalnızca keşif + doğrulama içindir.
- Yerel manifestler JSON5 ile ayrıştırılır; bu nedenle son değer hâlâ bir nesne olduğu sürece yorumlar, sondaki virgüller ve tırnaksız anahtarlar kabul edilir.
- Manifest yükleyici yalnızca belgelenmiş manifest alanlarını okur. Buraya özel üst düzey anahtarlar eklemekten kaçının.
- `providerAuthEnvVars`, env adlarını incelemek için plugin çalışma zamanını başlatmaması gereken auth yoklamaları, env işaretleyici doğrulaması ve benzeri provider auth yüzeyleri için düşük maliyetli meta veri yoludur.
- `providerAuthAliases`, provider varyantlarının başka bir provider'ın auth env değişkenlerini, auth profillerini, yapılandırma destekli auth'unu ve API anahtarı onboarding seçeneğini çekirdekte bu ilişkiyi sabit kodlamadan yeniden kullanmasını sağlar.
- `channelEnvVars`, env adlarını incelemek için plugin çalışma zamanını başlatmaması gereken shell env geri dönüşü, setup istemleri ve benzeri kanal yüzeyleri için düşük maliyetli meta veri yoludur.
- `providerAuthChoices`, provider çalışma zamanı yüklenmeden önce auth seçeneği seçicileri, `--auth-choice` çözümleme, tercih edilen provider eşleme ve basit onboarding CLI bayrağı kaydı için düşük maliyetli meta veri yoludur. Provider kodu gerektiren çalışma zamanı sihirbazı meta verileri için bkz.
  [Provider runtime hook'ları](/tr/plugins/architecture#provider-runtime-hooks).
- Özel plugin türleri `plugins.slots.*` üzerinden seçilir.
  - `kind: "memory"`, `plugins.slots.memory` tarafından seçilir.
  - `kind: "context-engine"`, `plugins.slots.contextEngine`
    tarafından seçilir (varsayılan: yerleşik `legacy`).
- Bir plugin bunlara ihtiyaç duymuyorsa `channels`, `providers`, `cliBackends` ve `skills` atlanabilir.
- Plugin'iniz yerel modüllere bağımlıysa, derleme adımlarını ve varsa paket yöneticisi izin listesi gereksinimlerini belgelendirin (örneğin pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`).

## İlgili

- [Plugin Oluşturma](/tr/plugins/building-plugins) — plugin'lerle çalışmaya başlama
- [Plugin Mimarisi](/tr/plugins/architecture) — iç mimari
- [SDK Genel Bakış](/tr/plugins/sdk-overview) — Plugin SDK başvurusu
