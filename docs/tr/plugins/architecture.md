---
read_when:
    - Yerel OpenClaw plugin'leri geliştiriyor veya hata ayıklıyorsunuz
    - Plugin yetenek modelini veya sahiplik sınırlarını anlamak istiyorsunuz
    - Plugin yükleme ardışık düzeni veya kayıt defteri üzerinde çalışıyorsunuz
    - Provider çalışma zamanı kancaları veya kanal plugin'leri uyguluyorsunuz
sidebarTitle: Internals
summary: 'Plugin iç yapıları: yetenek modeli, sahiplik, sözleşmeler, yükleme ardışık düzeni ve çalışma zamanı yardımcıları'
title: Plugin Internals
x-i18n:
    generated_at: "2026-04-07T08:50:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: a48b387152c5a6a9782c5aaa9d6c215c16adb7cb256302d3e85f80b03f9b6898
    source_path: plugins/architecture.md
    workflow: 15
---

# Plugin Internals

<Info>
  Bu, **derin mimari başvurusudur**. Pratik kılavuzlar için bkz.:
  - [Install and use plugins](/tr/tools/plugin) — kullanıcı kılavuzu
  - [Getting Started](/tr/plugins/building-plugins) — ilk plugin eğitimi
  - [Channel Plugins](/tr/plugins/sdk-channel-plugins) — bir mesajlaşma kanalı oluşturun
  - [Provider Plugins](/tr/plugins/sdk-provider-plugins) — bir model sağlayıcısı oluşturun
  - [SDK Overview](/tr/plugins/sdk-overview) — içe aktarma haritası ve kayıt API'si
</Info>

Bu sayfa, OpenClaw plugin sisteminin iç mimarisini kapsar.

## Genel yetenek modeli

Yetenekler, OpenClaw içindeki genel **yerel plugin** modelidir. Her
yerel OpenClaw plugin'i bir veya daha fazla yetenek türüne karşı kayıt olur:

| Capability             | Registration method                              | Example plugins                      |
| ---------------------- | ------------------------------------------------ | ------------------------------------ |
| Metin çıkarımı         | `api.registerProvider(...)`                      | `openai`, `anthropic`                |
| CLI çıkarım arka ucu   | `api.registerCliBackend(...)`                    | `openai`, `anthropic`                |
| Konuşma                | `api.registerSpeechProvider(...)`                | `elevenlabs`, `microsoft`            |
| Gerçek zamanlı yazıya dökme | `api.registerRealtimeTranscriptionProvider(...)` | `openai`                             |
| Gerçek zamanlı ses     | `api.registerRealtimeVoiceProvider(...)`         | `openai`                             |
| Medya anlama           | `api.registerMediaUnderstandingProvider(...)`    | `openai`, `google`                   |
| Görsel üretimi         | `api.registerImageGenerationProvider(...)`       | `openai`, `google`, `fal`, `minimax` |
| Müzik üretimi          | `api.registerMusicGenerationProvider(...)`       | `google`, `minimax`                  |
| Video üretimi          | `api.registerVideoGenerationProvider(...)`       | `qwen`                               |
| Web getirme            | `api.registerWebFetchProvider(...)`              | `firecrawl`                          |
| Web arama              | `api.registerWebSearchProvider(...)`             | `google`                             |
| Kanal / mesajlaşma     | `api.registerChannel(...)`                       | `msteams`, `matrix`                  |

Sıfır yetenek kaydı yapıp kanca, araç veya
hizmet sağlayan bir plugin, **legacy yalnızca-kancalı** plugin'dir. Bu desen hâlâ tamamen desteklenir.

### Harici uyumluluk duruşu

Yetenek modeli core'da yerleşmiştir ve bugün paketlenmiş/yerel plugin'ler
tarafından kullanılmaktadır, ancak harici plugin uyumluluğu için hâlâ
“dışa aktarıldı, dolayısıyla donduruldu” yaklaşımından daha sıkı bir ölçüt gerekir.

Geçerli yönlendirme:

- **mevcut harici plugin'ler:** kanca tabanlı entegrasyonları çalışır durumda tutun; bunu
  uyumluluk tabanı olarak kabul edin
- **yeni paketlenmiş/yerel plugin'ler:** satıcıya özgü içeri dalmalar veya
  yeni yalnızca-kancalı tasarımlar yerine açık yetenek kaydını tercih edin
- **yetenek kaydını benimseyen harici plugin'ler:** izinlidir, ancak belgeler bir
  sözleşmeyi açıkça kararlı olarak işaretlemedikçe yeteneğe özgü yardımcı yüzeyleri
  gelişmekte olan yüzeyler olarak değerlendirin

Pratik kural:

- yetenek kayıt API'leri amaçlanan yöndür
- legacy kancalar geçiş sırasında harici plugin'ler için en güvenli
  bozulmama yolu olarak kalır
- dışa aktarılan yardımcı alt yolların hepsi eşit değildir; tesadüfi yardımcı dışa aktarımlar yerine
  dar belgelenmiş sözleşmeyi tercih edin

### Plugin biçimleri

OpenClaw, yüklenen her plugin'i statik meta verilere değil,
gerçek kayıt davranışına göre bir biçime sınıflandırır:

- **plain-capability** -- tam olarak bir yetenek türü kaydeder (örneğin
  `mistral` gibi yalnızca sağlayıcı plugin'i)
- **hybrid-capability** -- birden çok yetenek türü kaydeder (örneğin
  `openai`, metin çıkarımı, konuşma, medya anlama ve görsel
  üretiminin sahibidir)
- **hook-only** -- yalnızca kanca kaydeder (türlü veya özel), yetenek,
  araç, komut veya hizmet kaydetmez
- **non-capability** -- araçlar, komutlar, hizmetler veya rotalar kaydeder ama
  yetenek kaydetmez

Bir plugin'in biçimini ve yetenek dökümünü görmek için `openclaw plugins inspect <id>` kullanın.
Ayrıntılar için [CLI reference](/cli/plugins#inspect) sayfasına bakın.

### Legacy kancalar

`before_agent_start` kancası, yalnızca-kancalı plugin'ler için bir uyumluluk yolu olarak desteklenmeye devam eder. Gerçek dünyadaki legacy plugin'ler buna hâlâ bağımlıdır.

Yön:

- çalışır durumda tutun
- legacy olarak belgeleyin
- model/sağlayıcı geçersiz kılma işleri için `before_model_resolve` kullanmayı tercih edin
- prompt değiştirme işleri için `before_prompt_build` kullanmayı tercih edin
- yalnızca gerçek kullanım düştüğünde ve fixture kapsamı geçiş güvenliğini kanıtladığında kaldırın

### Uyumluluk sinyalleri

`openclaw doctor` veya `openclaw plugins inspect <id>` çalıştırdığınızda,
şu etiketlerden birini görebilirsiniz:

| Signal                     | Meaning                                                      |
| -------------------------- | ------------------------------------------------------------ |
| **config valid**           | Yapılandırma düzgün ayrıştırılır ve plugin'ler çözümlenir    |
| **compatibility advisory** | Plugin desteklenen ama daha eski bir desen kullanır (örn. `hook-only`) |
| **legacy warning**         | Plugin, kullanımdan kaldırılmış olan `before_agent_start` kullanır |
| **hard error**             | Yapılandırma geçersizdir veya plugin yüklenemedi             |

Ne `hook-only` ne de `before_agent_start` bugün plugin'inizi bozmaz --
`hook-only` bir tavsiye sinyalidir ve `before_agent_start` yalnızca bir uyarı tetikler. Bu
sinyaller `openclaw status --all` ve `openclaw plugins doctor` içinde de görünür.

## Mimariye genel bakış

OpenClaw'ın plugin sistemi dört katmandan oluşur:

1. **Manifest + keşif**
   OpenClaw, yapılandırılmış yollardan, çalışma alanı köklerinden,
   genel uzantı köklerinden ve paketlenmiş uzantılardan aday plugin'leri bulur. Keşif,
   önce yerel `openclaw.plugin.json` manifest dosyalarını ve desteklenen paket manifest dosyalarını okur.
2. **Etkinleştirme + doğrulama**
   Core, keşfedilen bir plugin'in etkin, devre dışı, engelli veya
   bellek gibi özel bir yuva için seçili olup olmadığına karar verir.
3. **Çalışma zamanında yükleme**
   Yerel OpenClaw plugin'leri jiti aracılığıyla süreç içinde yüklenir ve
   yetenekleri merkezi bir kayıt defterine kaydeder. Uyumlu paketler, çalışma zamanı kodu içe aktarılmadan
   kayıt defteri kayıtlarına normalize edilir.
4. **Yüzey tüketimi**
   OpenClaw'ın geri kalanı kayıt defterini okuyarak araçları, kanalları, sağlayıcı
   kurulumunu, kancaları, HTTP rotalarını, CLI komutlarını ve hizmetleri açığa çıkarır.

Özellikle plugin CLI için, kök komut keşfi iki aşamaya ayrılır:

- ayrıştırma zamanı meta verileri `registerCli(..., { descriptors: [...] })` içinden gelir
- gerçek plugin CLI modülü tembel kalabilir ve ilk çağrıda kayıt olabilir

Bu, plugin'e ait CLI kodunu plugin içinde tutarken OpenClaw'ın ayrıştırmadan önce
kök komut adlarını ayırmasına olanak verir.

Önemli tasarım sınırı:

- keşif + yapılandırma doğrulama, plugin kodunu çalıştırmadan
  **manifest/şema meta verileri** üzerinden çalışabilmelidir
- yerel çalışma zamanı davranışı, plugin modülünün `register(api)` yolundan gelir

Bu ayrım, tam çalışma zamanı etkinleşmeden önce OpenClaw'ın yapılandırmayı doğrulamasına,
eksik/devre dışı plugin'leri açıklamasına ve
UI/şema ipuçları oluşturmasına olanak verir.

### Kanal plugin'leri ve paylaşılan message aracı

Kanal plugin'lerinin normal sohbet işlemleri için ayrı bir gönder/düzenle/tepki aracı kaydetmesi gerekmez. OpenClaw, core içinde tek bir paylaşılan `message` aracı tutar ve kanal plugin'leri bunun arkasındaki kanala özgü keşif ve yürütmenin sahibidir.

Geçerli sınır şöyledir:

- core, paylaşılan `message` araç barındırıcısının, prompt bağlantısının, oturum/iş parçacığı
  muhasebesinin ve yürütme sevkinin sahibidir
- kanal plugin'leri kapsamlı eylem keşfinin, yetenek keşfinin ve
  kanala özgü şema parçalarının sahibidir
- kanal plugin'leri, konuşma kimliklerinin iş parçacığı kimliklerini nasıl kodladığı veya üst konuşmalardan nasıl miras aldığı gibi
  sağlayıcıya özgü oturum konuşma dil bilgisinin sahibidir
- kanal plugin'leri son eylemi kendi eylem bağdaştırıcıları üzerinden yürütür

Kanal plugin'leri için SDK yüzeyi
`ChannelMessageActionAdapter.describeMessageTool(...)` yüzeyidir. Bu birleşik keşif
çağrısı, bir plugin'in görünür eylemlerini, yeteneklerini ve şema
katkılarını birlikte döndürmesine olanak tanır; böylece bu parçalar birbirinden kopmaz.

Core, çalışma zamanı kapsamını bu keşif adımına geçirir. Önemli alanlar şunları içerir:

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- güvenilir gelen `requesterSenderId`

Bu, bağlama duyarlı plugin'ler için önemlidir. Bir kanal, aktif hesap, mevcut oda/iş parçacığı/mesaj veya
güvenilir istekçi kimliğine göre message eylemlerini gizleyebilir ya da açığa çıkarabilir; core `message` aracı içinde
kanala özgü dallanmaları sabit kodlamaya gerek kalmaz.

Bu yüzden embedded-runner yönlendirme değişiklikleri hâlâ plugin işidir: runner,
mevcut sohbet/oturum kimliğini plugin keşif sınırına iletmekten sorumludur; böylece paylaşılan `message` aracı
mevcut tur için doğru kanala ait yüzeyi açığa çıkarır.

Kanala ait yürütme yardımcıları için, paketlenmiş plugin'ler yürütme
çalışma zamanını kendi uzantı modülleri içinde tutmalıdır. Core artık `src/agents/tools` altında Discord,
Slack, Telegram veya WhatsApp message-action çalışma zamanlarının sahibi değildir.
Ayrı `plugin-sdk/*-action-runtime` alt yolları yayımlamıyoruz ve paketlenmiş
plugin'ler kendi uzantı modüllerinden kendi yerel çalışma zamanı kodlarını doğrudan
içe aktarmalıdır.

Aynı sınır genel olarak sağlayıcı adlandırılmış SDK yüzeyleri için de geçerlidir: core,
Slack, Discord, Signal,
WhatsApp veya benzeri uzantılar için kanala özgü kolaylık barrel dosyalarını içe aktarmamalıdır. Core bir davranışa ihtiyaç duyuyorsa,
ya paketlenmiş plugin'in kendi `api.ts` / `runtime-api.ts` barrel'ını tüketmeli
ya da ihtiyacı paylaşılan SDK içinde dar bir genel yetenek hâline getirmelidir.

Özellikle anketler için iki yürütme yolu vardır:

- `outbound.sendPoll`, ortak anket modeline uyan kanallar için paylaşılan temel yoldur
- `actions.handleAction("poll")`, kanala özgü anket anlamları veya ek anket parametreleri için tercih edilen yoldur

Core artık paylaşılan anket ayrıştırmasını, plugin anket sevki eylemi reddettikten
sonraya erteler; böylece plugin'e ait anket işleyicileri, önce genel anket ayrıştırıcısı
engellemeden kanala özgü anket alanlarını kabul edebilir.

Tam başlangıç sırası için [Load pipeline](#load-pipeline) bölümüne bakın.

## Yetenek sahiplik modeli

OpenClaw, bir yerel plugin'i ilgisiz entegrasyonların bir torbası olarak değil,
bir **şirketin** veya bir **özelliğin** sahiplik sınırı olarak ele alır.

Bu şu anlama gelir:

- bir şirket plugin'i genellikle o şirketin OpenClaw'a yönelik
  tüm yüzeylerinin sahibi olmalıdır
- bir özellik plugin'i genellikle getirdiği özelliğin tüm yüzeyinin sahibi olmalıdır
- kanallar, sağlayıcı davranışını geçici biçimde yeniden uygulamak yerine
  paylaşılan core yeteneklerini tüketmelidir

Örnekler:

- paketlenmiş `openai` plugin'i OpenAI model-sağlayıcı davranışının ve OpenAI
  konuşma + gerçek zamanlı ses + medya anlama + görsel üretim davranışının sahibidir
- paketlenmiş `elevenlabs` plugin'i ElevenLabs konuşma davranışının sahibidir
- paketlenmiş `microsoft` plugin'i Microsoft konuşma davranışının sahibidir
- paketlenmiş `google` plugin'i Google model-sağlayıcı davranışının yanı sıra Google
  medya anlama + görsel üretim + web arama davranışının sahibidir
- paketlenmiş `firecrawl` plugin'i Firecrawl web-getirme davranışının sahibidir
- paketlenmiş `minimax`, `mistral`, `moonshot` ve `zai` plugin'leri kendi
  medya anlama arka uçlarının sahibidir
- `voice-call` plugin'i bir özellik plugin'idir: çağrı taşımasını, araçları,
  CLI'ı, rotaları ve Twilio medya akışı köprülemesini sahiplenir; ancak satıcı plugin'lerini doğrudan
  içe aktarmak yerine paylaşılan konuşma ile
  gerçek zamanlı yazıya dökme ve gerçek zamanlı ses yeteneklerini tüketir

Amaçlanan son durum şudur:

- OpenAI, metin modelleri, konuşma, görseller ve
  gelecekteki videoyu kapsasa bile tek bir plugin içinde yaşar
- başka bir satıcı da kendi yüzey alanı için aynısını yapabilir
- kanallar sağlayıcının hangi satıcı plugin'ine ait olduğunu umursamaz; core tarafından açığa çıkarılan
  paylaşılan yetenek sözleşmesini tüketir

Temel ayrım budur:

- **plugin** = sahiplik sınırı
- **capability** = birden çok plugin'in uygulayabildiği veya tüketebildiği core sözleşmesi

Dolayısıyla OpenClaw video gibi yeni bir alan eklerse, ilk soru
“hangi sağlayıcı video işlemeyi sabit kodlamalı?” değildir. İlk soru
“core video yetenek sözleşmesi nedir?” olmalıdır. O sözleşme bir kez oluştuğunda,
satıcı plugin'leri buna karşı kayıt olabilir ve kanal/özellik plugin'leri bunu tüketebilir.

Yetenek henüz yoksa, genellikle doğru adım şudur:

1. core içinde eksik yeteneği tanımlayın
2. bunu typed şekilde plugin API'si/çalışma zamanı üzerinden açığa çıkarın
3. kanalları/özellikleri bu yeteneğe bağlayın
4. satıcı plugin'lerinin uygulamaları kaydetmesine izin verin

Bu, sahipliği açık tutarken tek bir satıcıya veya tek seferlik
bir plugin'e özgü kod yoluna bağlı core davranışlardan kaçınır.

### Yetenek katmanlama

Kodun nereye ait olduğuna karar verirken şu zihinsel modeli kullanın:

- **core yetenek katmanı**: paylaşılan orkestrasyon, ilke, fallback, yapılandırma
  birleştirme kuralları, teslim semantiği ve typed sözleşmeler
- **satıcı plugin katmanı**: satıcıya özgü API'ler, auth, model katalogları, konuşma
  sentezi, görsel üretimi, gelecekteki video arka uçları, kullanım uç noktaları
- **kanal/özellik plugin katmanı**: Slack/Discord/voice-call/vb. entegrasyonu;
  core yeteneklerini tüketir ve bunları bir yüzey üzerinde sunar

Örneğin TTS şu şekildedir:

- core, yanıt zamanı TTS ilkesinin, fallback sırasının, tercihlerin ve kanal tesliminin sahibidir
- `openai`, `elevenlabs` ve `microsoft` sentez uygulamalarının sahibidir
- `voice-call`, telefon TTS çalışma zamanı yardımcısını tüketir

Aynı desen gelecekteki yetenekler için de tercih edilmelidir.

### Çok yetenekli şirket plugin örneği

Bir şirket plugin'i dışarıdan tutarlı görünmelidir. OpenClaw'ın modeller, konuşma, gerçek zamanlı yazıya dökme, gerçek zamanlı ses, medya
anlama, görsel üretimi, video üretimi, web getirme ve web arama için paylaşılan
sözleşmeleri varsa, bir satıcı tüm yüzeylerinin sahibi tek bir yerde olabilir:

```ts
import type { OpenClawPluginDefinition } from "openclaw/plugin-sdk/plugin-entry";
import {
  describeImageWithModel,
  transcribeOpenAiCompatibleAudio,
} from "openclaw/plugin-sdk/media-understanding";

const plugin: OpenClawPluginDefinition = {
  id: "exampleai",
  name: "ExampleAI",
  register(api) {
    api.registerProvider({
      id: "exampleai",
      // auth/model catalog/runtime hooks
    });

    api.registerSpeechProvider({
      id: "exampleai",
      // vendor speech config — implement the SpeechProviderPlugin interface directly
    });

    api.registerMediaUnderstandingProvider({
      id: "exampleai",
      capabilities: ["image", "audio", "video"],
      async describeImage(req) {
        return describeImageWithModel({
          provider: "exampleai",
          model: req.model,
          input: req.input,
        });
      },
      async transcribeAudio(req) {
        return transcribeOpenAiCompatibleAudio({
          provider: "exampleai",
          model: req.model,
          input: req.input,
        });
      },
    });

    api.registerWebSearchProvider(
      createPluginBackedWebSearchProvider({
        id: "exampleai-search",
        // credential + fetch logic
      }),
    );
  },
};

export default plugin;
```

Önemli olan tam yardımcı adları değildir. Biçim önemlidir:

- tek bir plugin satıcı yüzeyinin sahibidir
- core yine de yetenek sözleşmelerinin sahibidir
- kanallar ve özellik plugin'leri satıcı kodunu değil `api.runtime.*` yardımcılarını tüketir
- sözleşme testleri plugin'in sahip olduğunu iddia ettiği yetenekleri
  kaydettiğini doğrulayabilir

### Yetenek örneği: video anlama

OpenClaw, görsel/ses/video anlamayı zaten tek bir paylaşılan
yetenek olarak ele alır. Aynı sahiplik modeli burada da geçerlidir:

1. core medya anlama sözleşmesini tanımlar
2. satıcı plugin'leri, uygulanabildiği şekilde `describeImage`, `transcribeAudio` ve
   `describeVideo` kayıtlarını yapar
3. kanal ve özellik plugin'leri doğrudan satıcı koduna bağlanmak yerine
   paylaşılan core davranışını tüketir

Bu, bir sağlayıcının video varsayımlarını core'a gömmekten kaçınır. Plugin,
satıcı yüzeyinin sahibidir; core ise yetenek sözleşmesinin ve fallback davranışının sahibidir.

Video üretimi de aynı sıralamayı zaten kullanır: core typed
yetenek sözleşmesinin ve çalışma zamanı yardımcısının sahibidir; satıcı plugin'leri
`api.registerVideoGenerationProvider(...)` uygulamalarını buna karşı kaydeder.

Somut bir dağıtım denetim listesine mi ihtiyacınız var? Bkz.
[Capability Cookbook](/tr/plugins/architecture).

## Sözleşmeler ve yaptırım

Plugin API yüzeyi, kasıtlı olarak typed ve
`OpenClawPluginApi` içinde merkezileştirilmiştir. Bu sözleşme, desteklenen kayıt noktalarını ve
bir plugin'in güvenebileceği çalışma zamanı yardımcılarını tanımlar.

Bunun önemi:

- plugin yazarları tek bir kararlı iç standart elde eder
- core, aynı sağlayıcı kimliğini iki plugin'in kaydetmesi gibi yinelenen sahipliği reddedebilir
- başlangıç, hatalı kayıtlar için uygulanabilir tanılar gösterebilir
- sözleşme testleri, paketlenmiş plugin sahipliğini zorunlu kılabilir ve sessiz kaymayı önleyebilir

İki yaptırım katmanı vardır:

1. **çalışma zamanı kayıt yaptırımı**
   Plugin kayıt defteri, plugin'ler yüklenirken kayıtları doğrular. Örnekler:
   yinelenen sağlayıcı kimlikleri, yinelenen konuşma sağlayıcı kimlikleri ve
   hatalı kayıtlar tanımsız davranış yerine plugin tanıları üretir.
2. **sözleşme testleri**
   Paketlenmiş plugin'ler test çalıştırmaları sırasında sözleşme kayıtlarına alınır; böylece
   OpenClaw sahipliği açıkça doğrulayabilir. Bugün bu, model
   sağlayıcıları, konuşma sağlayıcıları, web arama sağlayıcıları ve paketlenmiş kayıt
   sahipliği için kullanılır.

Pratik etkisi şudur: OpenClaw hangi plugin'in hangi
yüzeyin sahibi olduğunu en baştan bilir. Bu, sahiplik
örtük değil; bildirilen, typed ve test edilebilir olduğundan core ve kanalların sorunsuz bileşim kurmasına olanak tanır.

### Bir sözleşmede ne bulunmalı

İyi plugin sözleşmeleri:

- typed'dır
- küçüktür
- yeteneğe özeldir
- core'a aittir
- birden çok plugin tarafından yeniden kullanılabilir
- satıcı bilgisi olmadan kanallar/özellikler tarafından tüketilebilir

Kötü plugin sözleşmeleri:

- core içinde gizlenmiş satıcıya özgü ilke
- kayıt defterini aşan tek seferlik plugin kaçış yolları
- bir satıcı uygulamasına doğrudan ulaşan kanal kodu
- `OpenClawPluginApi` veya
  `api.runtime` parçası olmayan geçici çalışma zamanı nesneleri

Emin değilseniz soyutlama düzeyini yükseltin: önce yeteneği tanımlayın, sonra
plugin'lerin buna bağlanmasına izin verin.

## Yürütme modeli

Yerel OpenClaw plugin'leri Gateway ile **süreç içinde** çalışır. Sandbox içinde
değildir. Yüklenmiş bir yerel plugin, core koduyla aynı süreç düzeyinde güven sınırına sahiptir.

Bunun sonuçları:

- yerel bir plugin araçlar, ağ işleyicileri, kancalar ve hizmetler kaydedebilir
- yerel bir plugin hatası gateway'i çökertebilir veya kararsızlaştırabilir
- kötü niyetli yerel bir plugin, OpenClaw süreci içinde keyfi kod çalıştırmaya denktir

Uyumlu paketler varsayılan olarak daha güvenlidir çünkü OpenClaw şu anda onları
meta veri/içerik paketleri olarak ele alır. Mevcut sürümlerde bu çoğunlukla paketlenmiş
Skills anlamına gelir.

Paketlenmemiş plugin'ler için izin listeleri ve açık kurulum/yükleme yolları kullanın.
Çalışma alanı plugin'lerini üretim varsayılanları değil,
geliştirme zamanı kodu olarak değerlendirin.

Paketlenmiş çalışma alanı paket adları için, plugin kimliğini npm
adına sabitli tutun: varsayılan olarak `@openclaw/<id>`, ya da
paket kasıtlı olarak daha dar bir plugin rolü açığa çıkarıyorsa
`-provider`, `-plugin`, `-speech`, `-sandbox` veya `-media-understanding` gibi onaylı typed son eklerden biri.

Önemli güven notu:

- `plugins.allow`, **plugin kimliklerine** güvenir; kaynak kökenine değil.
- Paketlenmiş bir plugin ile aynı kimliğe sahip bir çalışma alanı plugin'i,
  bu çalışma alanı plugin'i etkinleştirildiğinde/izin listesine alındığında kasıtlı olarak
  paketlenmiş kopyayı gölgeler.
- Bu normaldir ve yerel geliştirme, yama testi ve hotfix'ler için faydalıdır.

## Dışa aktarma sınırı

OpenClaw, uygulama kolaylıklarını değil, yetenekleri dışa aktarır.

Yetenek kaydını genel tutun. Sözleşme dışı yardımcı dışa aktarımları budayın:

- paketlenmiş plugin'e özgü yardımcı alt yollar
- genel API olması amaçlanmayan çalışma zamanı tesisat alt yolları
- satıcıya özgü kolaylık yardımcıları
- uygulama detayı olan kurulum/onboarding yardımcıları

Bazı paketlenmiş plugin yardımcı alt yolları, uyumluluk ve paketlenmiş plugin bakımı için üretilmiş SDK dışa aktarma
haritasında hâlâ kalmaktadır. Geçerli örnekler arasında
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` ve birkaç `plugin-sdk/matrix*` yüzeyi bulunur. Bunları,
yeni üçüncü taraf plugin'ler için önerilen SDK deseni olarak değil, ayrılmış uygulama detayı dışa aktarımları olarak değerlendirin.

## Load pipeline

Başlangıçta OpenClaw yaklaşık olarak şunları yapar:

1. aday plugin köklerini keşfeder
2. yerel veya uyumlu paket manifest dosyalarını ve paket meta verilerini okur
3. güvensiz adayları reddeder
4. plugin yapılandırmasını normalize eder (`plugins.enabled`, `allow`, `deny`, `entries`,
   `slots`, `load.paths`)
5. her aday için etkinleştirmeye karar verir
6. etkin yerel modülleri jiti aracılığıyla yükler
7. yerel `register(api)` (veya legacy takma adı olan `activate(api)`) kancalarını çağırır ve kayıtları plugin kayıt defterine toplar
8. kayıt defterini komutlara/çalışma zamanı yüzeylerine açığa çıkarır

<Note>
`activate`, `register` için legacy bir takma addır — yükleyici hangisi varsa onu çözümler (`def.register ?? def.activate`) ve aynı noktada çağırır. Tüm paketlenmiş plugin'ler `register` kullanır; yeni plugin'ler için `register` tercih edin.
</Note>

Güvenlik kapıları çalışma zamanı yürütmesinden **önce** gerçekleşir. Adaylar,
girdi plugin kökünden kaçıyorsa, yol herkes tarafından yazılabiliyorsa veya
paketlenmemiş plugin'ler için yol sahipliği şüpheli görünüyorsa engellenir.

### Önce manifest davranışı

Manifest kontrol düzlemi doğruluğunun kaynağıdır. OpenClaw bunu şu işler için kullanır:

- plugin'i tanımlamak
- bildirilen kanalları/skills/yapılandırma şemasını veya paket yeteneklerini keşfetmek
- `plugins.entries.<id>.config` değerini doğrulamak
- Control UI etiketlerini/yer tutucularını zenginleştirmek
- kurulum/katalog meta verilerini göstermek

Yerel plugin'ler için çalışma zamanı modülü veri düzlemi parçasıdır. Kanca, araç, komut veya sağlayıcı akışları gibi
gerçek davranışları kaydeder.

### Yükleyicinin önbelleğe aldıkları

OpenClaw, süreç içinde kısa süreli önbellekler tutar:

- keşif sonuçları
- manifest kayıt verileri
- yüklenmiş plugin kayıtları

Bu önbellekler ani başlangıç yükünü ve tekrarlanan komut maliyetini azaltır. Bunları
kalıcılık değil, kısa ömürlü performans önbellekleri olarak düşünmek güvenlidir.

Performans notu:

- Bu önbellekleri devre dışı bırakmak için `OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` veya
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1` ayarlayın.
- Önbellek pencerelerini `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` ve
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS` ile ayarlayın.

## Kayıt defteri modeli

Yüklenmiş plugin'ler doğrudan rastgele core global'lerini değiştirmez. Merkezi bir
plugin kayıt defterine kayıt olurlar.

Kayıt defteri şunları izler:

- plugin kayıtları (kimlik, kaynak, köken, durum, tanılar)
- araçlar
- legacy kancalar ve typed kancalar
- kanallar
- sağlayıcılar
- gateway RPC işleyicileri
- HTTP rotaları
- CLI kayıtçıları
- arka plan hizmetleri
- plugin'e ait komutlar

Sonra core özellikleri plugin modülleriyle doğrudan konuşmak yerine bu kayıt defterinden okur.
Bu, yüklemeyi tek yönlü tutar:

- plugin modülü -> kayıt defteri kaydı
- core çalışma zamanı -> kayıt defteri tüketimi

Bu ayrım bakım kolaylığı için önemlidir. Çoğu core yüzeyinin sadece tek bir
entegrasyon noktasına ihtiyaç duymasını sağlar: “kayıt defterini oku”,
“her plugin modülü için özel durum yaz” değil.

## Konuşma bağlama geri çağrıları

Bir konuşmayı bağlayan plugin'ler, bir onay çözüldüğünde tepki verebilir.

Bir bağlama isteği onaylandıktan veya reddedildikten sonra geri çağrı almak için
`api.onConversationBindingResolved(...)` kullanın:

```ts
export default {
  id: "my-plugin",
  register(api) {
    api.onConversationBindingResolved(async (event) => {
      if (event.status === "approved") {
        // A binding now exists for this plugin + conversation.
        console.log(event.binding?.conversationId);
        return;
      }

      // The request was denied; clear any local pending state.
      console.log(event.request.conversation.conversationId);
    });
  },
};
```

Geri çağrı yük alanları:

- `status`: `"approved"` veya `"denied"`
- `decision`: `"allow-once"`, `"allow-always"` veya `"deny"`
- `binding`: onaylanan istekler için çözümlenen bağlama
- `request`: özgün istek özeti, ayırma ipucu, gönderici kimliği ve
  konuşma meta verileri

Bu geri çağrı yalnızca bildirim içindir. Bir konuşmayı kimin bağlayabileceğini değiştirmez
ve core onay işlemesi tamamlandıktan sonra çalışır.

## Provider çalışma zamanı kancaları

Provider plugin'leri artık iki katmana sahiptir:

- manifest meta verileri: çalışma zamanı yüklemeden önce ucuz sağlayıcı ortam-auth araması için `providerAuthEnvVars`, çalışma zamanı yüklemeden önce ucuz kanal ortam/kurulum araması için `channelEnvVars`, ayrıca çalışma zamanı yüklemeden önce ucuz onboarding/auth-choice
  etiketleri ve CLI bayrağı meta verileri için `providerAuthChoices`
- yapılandırma zamanı kancaları: `catalog` / legacy `discovery` artı `applyConfigDefaults`
- çalışma zamanı kancaları: `normalizeModelId`, `normalizeTransport`,
  `normalizeConfig`,
  `applyNativeStreamingUsageCompat`, `resolveConfigApiKey`,
  `resolveSyntheticAuth`, `resolveExternalAuthProfiles`,
  `shouldDeferSyntheticProfileAuth`,
  `resolveDynamicModel`, `prepareDynamicModel`, `normalizeResolvedModel`,
  `contributeResolvedModelCompat`, `capabilities`,
  `normalizeToolSchemas`, `inspectToolSchemas`,
  `resolveReasoningOutputMode`, `prepareExtraParams`, `createStreamFn`,
  `wrapStreamFn`, `resolveTransportTurnState`,
  `resolveWebSocketSessionPolicy`, `formatApiKey`, `refreshOAuth`,
  `buildAuthDoctorHint`, `matchesContextOverflowError`,
  `classifyFailoverReason`, `isCacheTtlEligible`,
  `buildMissingAuthMessage`, `suppressBuiltInModel`, `augmentModelCatalog`,
  `isBinaryThinking`, `supportsXHighThinking`,
  `resolveDefaultThinkingLevel`, `isModernModelRef`, `prepareRuntimeAuth`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `createEmbeddingProvider`,
  `buildReplayPolicy`,
  `sanitizeReplayHistory`, `validateReplayTurns`, `onModelSelected`

OpenClaw hâlâ genel agent döngüsünün, failover'un, transkript işlemenin ve
araç ilkesinin sahibidir. Bu kancalar, bütünüyle özel bir çıkarım taşımasına ihtiyaç duymadan
sağlayıcıya özgü davranışlar için uzantı yüzeyidir.

Sağlayıcı, genel auth/status/model-picker yollarının sağlayıcı çalışma zamanını yüklemeden
görebilmesi gereken ortam tabanlı kimlik bilgilerine sahipse manifest `providerAuthEnvVars` kullanın.
Onboarding/auth-choice CLI yüzeylerinin sağlayıcının seçim kimliğini, grup etiketlerini ve basit
tek-bayraklı auth bağlantılarını sağlayıcı çalışma zamanını yüklemeden bilmesi gerekiyorsa manifest `providerAuthChoices` kullanın.
Sağlayıcı çalışma zamanı `envVars` alanını onboarding etiketleri veya OAuth
client-id/client-secret kurulum değişkenleri gibi operatöre dönük ipuçları için saklayın.

Bir kanalın, genel kabuk ortamı fallback'i, yapılandırma/durum kontrolleri veya kurulum istemlerinin
kanal çalışma zamanını yüklemeden görebilmesi gereken ortam güdümlü auth ya da kurulumu varsa
manifest `channelEnvVars` kullanın.

### Kanca sırası ve kullanım

Model/provider plugin'leri için OpenClaw kancaları kabaca bu sırayla çağırır.
“Ne zaman kullanılır” sütunu hızlı karar kılavuzudur.

| #   | Hook                              | Ne yapar                                                                                                       | Ne zaman kullanılır                                                                                                                         |
| --- | --------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `catalog`                         | `models.json` üretimi sırasında sağlayıcı yapılandırmasını `models.providers` içine yayımlar                  | Sağlayıcı bir katalogun veya temel URL varsayılanlarının sahibiyse                                                                          |
| 2   | `applyConfigDefaults`             | Yapılandırma somutlaştırma sırasında sağlayıcıya ait genel yapılandırma varsayılanlarını uygular              | Varsayılanlar auth moduna, ortama veya sağlayıcının model ailesi semantiğine bağlıysa                                                      |
| --  | _(built-in model lookup)_         | OpenClaw önce normal kayıt/katalog yolunu dener                                                               | _(plugin kancası değildir)_                                                                                                                 |
| 3   | `normalizeModelId`                | Aramadan önce legacy veya önizleme model-id takma adlarını normalize eder                                     | Sağlayıcı, kanonik model çözümlemesinden önce takma ad temizliğinin sahibiyse                                                              |
| 4   | `normalizeTransport`              | Genel model derlemesinden önce sağlayıcı ailesi `api` / `baseUrl` değerini normalize eder                    | Sağlayıcı, aynı taşıma ailesindeki özel sağlayıcı kimlikleri için taşıma temizliğinin sahibiyse                                            |
| 5   | `normalizeConfig`                 | Çalışma zamanı/sağlayıcı çözümlemesinden önce `models.providers.<id>` değerini normalize eder                 | Sağlayıcının plugin ile birlikte yaşaması gereken yapılandırma temizliğine ihtiyacı varsa; paketlenmiş Google ailesi yardımcıları da desteklenen Google yapılandırma girdilerini burada geriden destekler |
| 6   | `applyNativeStreamingUsageCompat` | Yapılandırma sağlayıcılarına yerel akış-kullanım uyumluluk yeniden yazımlarını uygular                        | Sağlayıcının uç nokta güdümlü yerel akış kullanım meta verisi düzeltmelerine ihtiyacı varsa                                                |
| 7   | `resolveConfigApiKey`             | Çalışma zamanı auth yüklemesinden önce yapılandırma sağlayıcıları için env-marker auth'u çözümler             | Sağlayıcının sağlayıcıya ait env-marker API-key çözümlemesi varsa; `amazon-bedrock` burada yerleşik bir AWS env-marker çözümleyicisine de sahiptir |
| 8   | `resolveSyntheticAuth`            | Düz metin kalıcılaştırmadan yerel/self-hosted veya yapılandırma destekli auth'u yüzeye çıkarır               | Sağlayıcı sentetik/yerel bir kimlik bilgisi işaretçisiyle çalışabiliyorsa                                                                   |
| 9   | `resolveExternalAuthProfiles`     | Sağlayıcıya ait harici auth profillerini bindirir; CLI/uygulama sahipli kimlik bilgileri için varsayılan `persistence` değeri `runtime-only` olur | Sağlayıcı kopyalanmış refresh token'ları kalıcılaştırmadan harici auth kimlik bilgilerini yeniden kullanıyorsa                            |
| 10  | `shouldDeferSyntheticProfileAuth` | Kayıtlı sentetik profil yer tutucularını env/yapılandırma destekli auth'un gerisine düşürür                  | Sağlayıcı, öncelik kazanmaması gereken sentetik yer tutucu profiller saklıyorsa                                                            |
| 11  | `resolveDynamicModel`             | Yerel kayıt defterinde henüz olmayan sağlayıcıya ait model kimlikleri için eşzamanlı fallback                | Sağlayıcı keyfi upstream model kimliklerini kabul ediyorsa                                                                                  |
| 12  | `prepareDynamicModel`             | Eşzamansız hazırlık yapar, sonra `resolveDynamicModel` yeniden çalışır                                        | Sağlayıcı bilinmeyen kimlikleri çözümlemeden önce ağ meta verisine ihtiyaç duyuyorsa                                                       |
| 13  | `normalizeResolvedModel`          | Embedded runner çözümlenen modeli kullanmadan önce son yeniden yazımı yapar                                   | Sağlayıcının taşıma yeniden yazımlarına ihtiyacı varsa ama yine de bir core taşıması kullanıyorsa                                          |
| 14  | `contributeResolvedModelCompat`   | Başka uyumlu bir taşımanın arkasındaki satıcı modelleri için uyumluluk bayrakları katkısı yapar             | Sağlayıcı, sağlayıcının kontrolünü devralmadan kendi modellerini vekil taşımalarda tanıyorsa                                               |
| 15  | `capabilities`                    | Paylaşılan core mantığı tarafından kullanılan sağlayıcıya ait transkript/araçlama meta verisi               | Sağlayıcı, transkript/sağlayıcı ailesi farklılıklarına ihtiyaç duyuyorsa                                                                   |
| 16  | `normalizeToolSchemas`            | Embedded runner görmeden önce araç şemalarını normalize eder                                                  | Sağlayıcı, taşıma ailesi şema temizliğine ihtiyaç duyuyorsa                                                                                |
| 17  | `inspectToolSchemas`              | Normalizasyondan sonra sağlayıcıya ait şema tanılarını açığa çıkarır                                         | Sağlayıcı, core'a sağlayıcıya özgü kurallar öğretmeden anahtar sözcük uyarıları istiyorsa                                                  |
| 18  | `resolveReasoningOutputMode`      | Yerel ve etiketli reasoning-output sözleşmesi arasında seçim yapar                                            | Sağlayıcı, yerel alanlar yerine etiketli reasoning/nihai çıktı istiyorsa                                                                   |
| 19  | `prepareExtraParams`              | Genel akış seçenek sarmalayıcılarından önce istek-param normalizasyonu yapar                                  | Sağlayıcı, varsayılan istek parametreleri veya sağlayıcı başına parametre temizliği istiyorsa                                              |
| 20  | `createStreamFn`                  | Normal akış yolunu tamamen özel bir taşıma ile değiştirir                                                     | Sağlayıcı yalnızca bir sarmalayıcıya değil, özel bir tel protokolüne ihtiyaç duyuyorsa                                                     |
| 21  | `wrapStreamFn`                    | Genel sarmalayıcılar uygulandıktan sonra akış sarmalayıcısı uygular                                          | Sağlayıcı, özel taşıma olmadan istek üst bilgisi/gövdesi/model uyumluluk sarmalayıcılarına ihtiyaç duyuyorsa                              |
| 22  | `resolveTransportTurnState`       | Yerel tur başına taşıma üst bilgileri veya meta verileri ekler                                                | Sağlayıcı, genel taşımaların sağlayıcıya özgü tur kimliği göndermesini istiyorsa                                                           |
| 23  | `resolveWebSocketSessionPolicy`   | Yerel WebSocket üst bilgileri veya oturum cooldown ilkesi ekler                                               | Sağlayıcı, genel WS taşımalarının oturum üst bilgilerini veya fallback ilkesini ayarlamasını istiyorsa                                     |
| 24  | `formatApiKey`                    | Auth-profile biçimlendiricisi: kayıtlı profil çalışma zamanı `apiKey` dizgesine dönüşür                      | Sağlayıcı ek auth meta verisi saklıyorsa ve özel bir çalışma zamanı token biçimine ihtiyaç duyuyorsa                                       |
| 25  | `refreshOAuth`                    | Özel yenileme uç noktaları veya yenileme-hatası ilkesi için OAuth yenileme geçersiz kılması                  | Sağlayıcı paylaşılan `pi-ai` yenileyicilerine uymuyorsa                                                                                    |
| 26  | `buildAuthDoctorHint`             | OAuth yenileme başarısız olduğunda eklenen onarım ipucu                                                      | Sağlayıcı, yenileme hatası sonrasında sağlayıcıya ait auth onarım yönlendirmesine ihtiyaç duyuyorsa                                       |
| 27  | `matchesContextOverflowError`     | Sağlayıcıya ait bağlam penceresi taşma eşleyicisi                                                            | Sağlayıcının ham taşma hataları genel sezgilerin kaçıracağı türdense                                                                       |
| 28  | `classifyFailoverReason`          | Sağlayıcıya ait failover nedeni sınıflandırması                                                              | Sağlayıcı, ham API/taşıma hatalarını rate-limit/overload/vb. nedenlere eşleyebiliyorsa                                                     |
| 29  | `isCacheTtlEligible`              | Proxy/backhaul sağlayıcılar için prompt-cache ilkesi                                                         | Sağlayıcının proxy'ye özgü cache TTL geçitlemesine ihtiyacı varsa                                                                          |
| 30  | `buildMissingAuthMessage`         | Genel eksik-auth kurtarma mesajının yerine geçen mesaj                                                       | Sağlayıcı, sağlayıcıya özgü eksik-auth kurtarma ipucuna ihtiyaç duyuyorsa                                                                  |
| 31  | `suppressBuiltInModel`            | Eski upstream model bastırma ve isteğe bağlı kullanıcıya dönük hata ipucu                                    | Sağlayıcı eski upstream satırlarını gizlemek veya yerlerine satıcı ipucu koymak istiyorsa                                                  |
| 32  | `augmentModelCatalog`             | Keşif sonrasında sentetik/nihai katalog satırları eklenir                                                    | Sağlayıcı `models list` ve seçicilerde sentetik ileri uyumluluk satırlarına ihtiyaç duyuyorsa                                             |
| 33  | `isBinaryThinking`                | İkili-thinking sağlayıcıları için açık/kapalı akıl yürütme anahtarı                                          | Sağlayıcı yalnızca ikili thinking açık/kapalı sunuyorsa                                                                                    |
| 34  | `supportsXHighThinking`           | Seçili modeller için `xhigh` akıl yürütme desteği                                                            | Sağlayıcı `xhigh` desteğini yalnızca model alt kümesinde istiyorsa                                                                         |
| 35  | `resolveDefaultThinkingLevel`     | Belirli bir model ailesi için varsayılan `/think` düzeyi                                                     | Sağlayıcı bir model ailesi için varsayılan `/think` ilkesinin sahibiyse                                                                    |
| 36  | `isModernModelRef`                | Canlı profil filtreleri ve smoke seçimi için modern-model eşleyicisi                                         | Sağlayıcı canlı/smoke tercih edilen model eşlemesinin sahibiyse                                                                            |
| 37  | `prepareRuntimeAuth`              | Çıkarımdan hemen önce yapılandırılmış bir kimlik bilgisini gerçek çalışma zamanı token/key değerine değiştirir | Sağlayıcı bir token değişimine veya kısa ömürlü istek kimlik bilgisine ihtiyaç duyuyorsa                                                   |
| 38  | `resolveUsageAuth`                | `/usage` ve ilgili durum yüzeyleri için kullanım/faturalama kimlik bilgilerini çözümler                      | Sağlayıcı özel kullanım/kota token ayrıştırmasına veya farklı bir kullanım kimlik bilgisine ihtiyaç duyuyorsa                              |
| 39  | `fetchUsageSnapshot`              | Auth çözümlendikten sonra sağlayıcıya özgü kullanım/kota anlık görüntülerini getirir ve normalize eder      | Sağlayıcı sağlayıcıya özgü bir kullanım uç noktası veya yük ayrıştırıcısı gerektiriyorsa                                                   |
| 40  | `createEmbeddingProvider`         | Bellek/arama için sağlayıcıya ait embedding bağdaştırıcısı oluşturur                                         | Bellek embedding davranışı sağlayıcı plugin'i ile birlikte yaşamalıdır                                                                     |
| 41  | `buildReplayPolicy`               | Sağlayıcı için transkript işlemeyi kontrol eden bir replay ilkesi döndürür                                   | Sağlayıcı özel transkript ilkesine ihtiyaç duyuyorsa (örneğin thinking bloklarının ayıklanması)                                            |
| 42  | `sanitizeReplayHistory`           | Genel transkript temizliğinden sonra replay geçmişini yeniden yazar                                          | Sağlayıcı, paylaşılan compaction yardımcılarının ötesinde sağlayıcıya özgü replay yeniden yazımlarına ihtiyaç duyuyorsa                    |
| 43  | `validateReplayTurns`             | Embedded runner öncesi son replay-turn doğrulaması veya yeniden şekillendirme yapar                         | Sağlayıcı taşıması, genel temizlemeden sonra daha sıkı tur doğrulamasına ihtiyaç duyuyorsa                                                 |
| 44  | `onModelSelected`                 | Sağlayıcıya ait seçim sonrası yan etkileri çalıştırır                                                        | Bir model etkin olduğunda sağlayıcının telemetriye veya sağlayıcıya ait duruma ihtiyacı varsa                                              |

`normalizeModelId`, `normalizeTransport` ve `normalizeConfig` önce eşleşen
provider plugin'ini denetler, sonra model kimliğini veya taşıma/yapılandırmayı gerçekten
değiştirene kadar kanca destekli diğer provider plugin'lerine düşer. Bu,
takma ad/uyumluluk sağlayıcı sarmalayıcılarının, çağıranın yeniden yazımın hangi
paketlenmiş plugin'e ait olduğunu bilmesini gerektirmeden çalışmasını sağlar. Desteklenen bir
Google ailesi yapılandırma girdisini hiçbir provider kancası yeniden yazmazsa,
paketlenmiş Google yapılandırma normalleştiricisi yine de bu uyumluluk temizliğini uygular.

Sağlayıcının tamamen özel bir tel protokolüne veya özel istek yürütücüsüne ihtiyacı varsa,
bu farklı bir uzantı sınıfıdır. Bu kancalar, OpenClaw'ın normal çıkarım döngüsü üzerinde çalışan
sağlayıcı davranışları içindir.

### Provider örneği

```ts
api.registerProvider({
  id: "example-proxy",
  label: "Example Proxy",
  auth: [],
  catalog: {
    order: "simple",
    run: async (ctx) => {
      const apiKey = ctx.resolveProviderApiKey("example-proxy").apiKey;
      if (!apiKey) {
        return null;
      }
      return {
        provider: {
          baseUrl: "https://proxy.example.com/v1",
          apiKey,
          api: "openai-completions",
          models: [{ id: "auto", name: "Auto" }],
        },
      };
    },
  },
  resolveDynamicModel: (ctx) => ({
    id: ctx.modelId,
    name: ctx.modelId,
    provider: "example-proxy",
    api: "openai-completions",
    baseUrl: "https://proxy.example.com/v1",
    reasoning: false,
    input: ["text"],
    cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
    contextWindow: 128000,
    maxTokens: 8192,
  }),
  prepareRuntimeAuth: async (ctx) => {
    const exchanged = await exchangeToken(ctx.apiKey);
    return {
      apiKey: exchanged.token,
      baseUrl: exchanged.baseUrl,
      expiresAt: exchanged.expiresAt,
    };
  },
  resolveUsageAuth: async (ctx) => {
    const auth = await ctx.resolveOAuthToken();
    return auth ? { token: auth.token } : null;
  },
  fetchUsageSnapshot: async (ctx) => {
    return await fetchExampleProxyUsage(ctx.token, ctx.timeoutMs, ctx.fetchFn);
  },
});
```

### Yerleşik örnekler

- Anthropic, `resolveDynamicModel`, `capabilities`, `buildAuthDoctorHint`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `isCacheTtlEligible`,
  `resolveDefaultThinkingLevel`, `applyConfigDefaults`, `isModernModelRef`,
  ve `wrapStreamFn` kullanır; çünkü Claude 4.6 ileri uyumluluğunun,
  sağlayıcı ailesi ipuçlarının, auth onarım yönlendirmesinin, kullanım uç noktası entegrasyonunun,
  prompt-cache uygunluğunun, auth farkında yapılandırma varsayılanlarının, Claude
  varsayılan/uyarlanabilir thinking ilkesinin ve beta üst bilgileri, `/fast` / `serviceTier`
  ve `context1m` için Anthropic'e özgü akış şekillendirmenin sahibidir.
- Anthropic'in Claude'a özgü akış yardımcıları şimdilik paketlenmiş plugin'in kendi
  genel `api.ts` / `contract-api.ts` yüzeyinde kalır. Bu paket yüzeyi,
  genel SDK'yı tek bir sağlayıcının beta-header kuralları etrafında genişletmek yerine
  `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
  `resolveAnthropicFastMode`, `resolveAnthropicServiceTier` ve daha düşük düzey
  Anthropic sarmalayıcı üreticilerini dışa aktarır.
- OpenAI, `resolveDynamicModel`, `normalizeResolvedModel` ve
  `capabilities` ile birlikte `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `supportsXHighThinking` ve `isModernModelRef`
  kullanır; çünkü GPT-5.4 ileri uyumluluğunun, doğrudan OpenAI
  `openai-completions` -> `openai-responses` normalizasyonunun, Codex farkında auth
  ipuçlarının, Spark bastırmanın, sentetik OpenAI liste satırlarının ve GPT-5 thinking /
  canlı model ilkesinin sahibidir; `openai-responses-defaults` akış ailesi ise atıf üst bilgileri,
  `/fast`/`serviceTier`, metin ayrıntılılığı, yerel Codex web arama,
  reasoning-compat yük şekillendirme ve Responses bağlam yönetimi için paylaşılan yerel OpenAI Responses sarmalayıcılarının sahibidir.
- OpenRouter, sağlayıcı pass-through olduğu ve
  OpenClaw'ın statik kataloğu güncellenmeden önce yeni model kimliklerini açığa çıkarabildiği için `catalog` ile birlikte `resolveDynamicModel` ve
  `prepareDynamicModel` kullanır; ayrıca sağlayıcıya özgü istek üst bilgilerini, yönlendirme meta verilerini,
  reasoning yamalarını ve prompt-cache ilkesini core dışında tutmak için
  `capabilities`, `wrapStreamFn` ve `isCacheTtlEligible` kullanır. Replay ilkesi
  `passthrough-gemini` ailesinden gelirken, `openrouter-thinking` akış ailesi
  proxy reasoning ekleme ve desteklenmeyen model / `auto` atlamalarının sahibidir.
- GitHub Copilot, sağlayıcıya ait cihaz girişi, model fallback davranışı, Claude transkript farklılıkları,
  GitHub token -> Copilot token değişimi ve sağlayıcıya ait kullanım uç noktası için
  `catalog`, `auth`, `resolveDynamicModel` ve `capabilities` ile birlikte
  `prepareRuntimeAuth` ve `fetchUsageSnapshot` kullanır.
- OpenAI Codex, hâlâ core OpenAI taşımaları üzerinde çalıştığı ancak taşıma/temel URL
  normalizasyonunun, OAuth yenileme fallback ilkesinin, varsayılan taşıma seçiminin,
  sentetik Codex katalog satırlarının ve ChatGPT kullanım uç noktası entegrasyonunun sahibi olduğu için
  `catalog`, `resolveDynamicModel`,
  `normalizeResolvedModel`, `refreshOAuth` ve `augmentModelCatalog` ile birlikte
  `prepareExtraParams`, `resolveUsageAuth` ve `fetchUsageSnapshot` kullanır; doğrudan OpenAI ile aynı
  `openai-responses-defaults` akış ailesini paylaşır.
- Google AI Studio ve Gemini CLI OAuth, `google-gemini` replay ailesi
  Gemini 3.1 ileri uyumluluk fallback'inin, yerel Gemini replay doğrulamasının, bootstrap replay temizliğinin, etiketli
  reasoning-output modunun ve modern-model eşleşmesinin sahibi olduğu için
  `resolveDynamicModel`,
  `buildReplayPolicy`, `sanitizeReplayHistory`,
  `resolveReasoningOutputMode`, `wrapStreamFn` ve `isModernModelRef` kullanır;
  `google-thinking` akış ailesi ise Gemini thinking yük normalizasyonunun sahibidir;
  Gemini CLI OAuth ayrıca token biçimlendirme, token ayrıştırma ve kota uç noktası
  bağlantısı için `formatApiKey`, `resolveUsageAuth` ve
  `fetchUsageSnapshot` kullanır.
- Anthropic Vertex, Claude'a özgü replay temizliğinin tüm `anthropic-messages` taşıması yerine
  Claude kimlikleriyle sınırlı kalması için
  `anthropic-by-model` replay ailesi üzerinden `buildReplayPolicy` kullanır.
- Amazon Bedrock, Anthropic-on-Bedrock trafiği için Bedrock'a özgü throttle/not-ready/context-overflow hata sınıflandırmasının sahibi olduğu için
  `buildReplayPolicy`, `matchesContextOverflowError`,
  `classifyFailoverReason` ve `resolveDefaultThinkingLevel` kullanır;
  replay ilkesi yine aynı Claude-only `anthropic-by-model` korumasını paylaşır.
- OpenRouter, Kilocode, Opencode ve Opencode Go, Gemini
  düşünce imzası temizliğine ihtiyaç duydukları ancak yerel Gemini replay doğrulamasına veya
  bootstrap yeniden yazımlarına ihtiyaç duymadıkları için
  `passthrough-gemini` replay ailesi üzerinden `buildReplayPolicy`
  kullanır; çünkü Gemini modellerini OpenAI uyumlu taşımalar üzerinden vekil geçirirler.
- MiniMax, bir sağlayıcının hem Anthropic-message hem de OpenAI uyumlu semantiklerin sahibi olduğu için
  `hybrid-anthropic-openai` replay ailesi üzerinden `buildReplayPolicy`
  kullanır; Anthropic tarafında Claude-only
  thinking-block düşürmeyi korurken reasoning çıktı modunu yeniden yerel değere geçersiz kılar ve
  `minimax-fast-mode` akış ailesi paylaşılan akış yolunda hızlı mod model yeniden yazımlarının sahibidir.
- Moonshot, paylaşılan
  OpenAI taşımasını kullanmaya devam ederken sağlayıcıya ait thinking yük normalizasyonuna ihtiyaç duyduğu için
  `catalog` ile birlikte `wrapStreamFn` kullanır; `moonshot-thinking` akış ailesi yapılandırmayı ve `/think` durumunu
  yerel ikili thinking yüküne eşler.
- Kilocode, sağlayıcıya ait istek üst bilgilerine,
  reasoning yük normalizasyonuna, Gemini transkript ipuçlarına ve Anthropic
  cache-TTL geçitlemesine ihtiyaç duyduğu için
  `catalog`, `capabilities`, `wrapStreamFn` ve
  `isCacheTtlEligible` kullanır; `kilocode-thinking` akış ailesi ise
  `kilo/auto` ve açık reasoning yüklerini desteklemeyen diğer vekil model kimliklerini atlarken
  paylaşılan vekil akış yolunda Kilo thinking eklemesini tutar.
- Z.AI, GLM-5 fallback'inin,
  `tool_stream` varsayılanlarının, ikili thinking UX'inin, modern-model eşleşmesinin ve hem
  kullanım auth'u hem kota getirme işlemlerinin sahibi olduğu için
  `resolveDynamicModel`, `prepareExtraParams`, `wrapStreamFn`,
  `isCacheTtlEligible`, `isBinaryThinking`, `isModernModelRef`,
  `resolveUsageAuth` ve `fetchUsageSnapshot` kullanır; `tool-stream-default-on`
  akış ailesi ise varsayılan açık `tool_stream` sarmalayıcısını sağlayıcı başına elle yazılmış yapıştırma kodu dışında tutar.
- xAI, yerel xAI Responses taşıma normalizasyonunun, Grok hızlı mod
  takma ad yeniden yazımlarının, varsayılan `tool_stream`, sıkı araç / reasoning-payload
  temizliğinin, plugin'e ait araçlar için fallback auth yeniden kullanımının, ileri uyumlu Grok
  model çözümlemesinin ve xAI tool-schema
  profili, desteklenmeyen şema anahtar sözcükleri, yerel `web_search` ve HTML-entity
  tool-call argüman çözme gibi sağlayıcıya ait uyumluluk yamalarının sahibi olduğu için
  `normalizeResolvedModel`, `normalizeTransport`,
  `contributeResolvedModelCompat`, `prepareExtraParams`, `wrapStreamFn`,
  `resolveSyntheticAuth`, `resolveDynamicModel` ve `isModernModelRef`
  kullanır.
- Mistral, OpenCode Zen ve OpenCode Go, transkript/araçlama farklılıklarını core dışında tutmak için
  yalnızca `capabilities` kullanır.
- `byteplus`, `cloudflare-ai-gateway`,
  `huggingface`, `kimi-coding`, `nvidia`, `qianfan`,
  `synthetic`, `together`, `venice`, `vercel-ai-gateway` ve `volcengine` gibi
  yalnızca katalog sağlayan paketlenmiş sağlayıcılar
  yalnızca `catalog` kullanır.
- Qwen, metin sağlayıcısı için `catalog` ile birlikte çok modlu yüzeyleri için paylaşılan medya anlama ve
  video üretim kayıtlarını kullanır.
- MiniMax ve Xiaomi, `/usage`
  davranışları sağlayıcıya ait olduğu için çıkarım hâlâ paylaşılan taşımalar üzerinden çalışsa da
  `catalog` ile birlikte kullanım kancalarını kullanır.

## Çalışma zamanı yardımcıları

Plugin'ler, `api.runtime` üzerinden seçili core yardımcılarına erişebilir. TTS için:

```ts
const clip = await api.runtime.tts.textToSpeech({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

const result = await api.runtime.tts.textToSpeechTelephony({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

const voices = await api.runtime.tts.listVoices({
  provider: "elevenlabs",
  cfg: api.config,
});
```

Notlar:

- `textToSpeech`, dosya/sesli not yüzeyleri için normal core TTS çıktı yükünü döndürür.
- Core `messages.tts` yapılandırmasını ve sağlayıcı seçimini kullanır.
- PCM ses arabelleği + örnekleme oranı döndürür. Plugin'ler sağlayıcılar için yeniden örnekleme/kodlama yapmalıdır.
- `listVoices`, sağlayıcı başına isteğe bağlıdır. Bunu satıcıya ait ses seçiciler veya kurulum akışları için kullanın.
- Ses listeleri, sağlayıcı farkında seçiciler için yerel ayar, cinsiyet ve kişilik etiketleri gibi daha zengin meta veriler içerebilir.
- Bugün telefon desteği OpenAI ve ElevenLabs'te vardır. Microsoft'ta yoktur.

Plugin'ler ayrıca `api.registerSpeechProvider(...)` üzerinden konuşma sağlayıcıları da kaydedebilir.

```ts
api.registerSpeechProvider({
  id: "acme-speech",
  label: "Acme Speech",
  isConfigured: ({ config }) => Boolean(config.messages?.tts),
  synthesize: async (req) => {
    return {
      audioBuffer: Buffer.from([]),
      outputFormat: "mp3",
      fileExtension: ".mp3",
      voiceCompatible: false,
    };
  },
});
```

Notlar:

- TTS ilkesini, fallback'leri ve yanıt teslimini core içinde tutun.
- Satıcıya ait sentez davranışı için konuşma sağlayıcılarını kullanın.
- Legacy Microsoft `edge` girdisi `microsoft` sağlayıcı kimliğine normalize edilir.
- Tercih edilen sahiplik modeli şirket odaklıdır: tek bir satıcı plugin'i,
  OpenClaw bu yetenek sözleşmelerini ekledikçe metin, konuşma, görsel ve gelecekteki medya sağlayıcılarının sahibi olabilir.

Görsel/ses/video anlama için plugin'ler genel bir anahtar/değer torbası yerine
tek bir typed medya anlama sağlayıcısı kaydeder:

```ts
api.registerMediaUnderstandingProvider({
  id: "google",
  capabilities: ["image", "audio", "video"],
  describeImage: async (req) => ({ text: "..." }),
  transcribeAudio: async (req) => ({ text: "..." }),
  describeVideo: async (req) => ({ text: "..." }),
});
```

Notlar:

- Orkestrasyonu, fallback'i, yapılandırmayı ve kanal bağlantısını core içinde tutun.
- Satıcı davranışını sağlayıcı plugin'inde tutun.
- Artımlı genişleme typed kalmalıdır: yeni isteğe bağlı yöntemler, yeni isteğe bağlı
  sonuç alanları, yeni isteğe bağlı yetenekler.
- Video üretimi de zaten aynı deseni izler:
  - core yetenek sözleşmesinin ve çalışma zamanı yardımcısının sahibidir
  - satıcı plugin'leri `api.registerVideoGenerationProvider(...)` kaydeder
  - özellik/kanal plugin'leri `api.runtime.videoGeneration.*` yüzeyini tüketir

Medya anlama çalışma zamanı yardımcıları için plugin'ler şunları çağırabilir:

```ts
const image = await api.runtime.mediaUnderstanding.describeImageFile({
  filePath: "/tmp/inbound-photo.jpg",
  cfg: api.config,
  agentDir: "/tmp/agent",
});

const video = await api.runtime.mediaUnderstanding.describeVideoFile({
  filePath: "/tmp/inbound-video.mp4",
  cfg: api.config,
});
```

Ses yazıya dökme için plugin'ler ya medya anlama çalışma zamanını
ya da eski STT takma adını kullanabilir:

```ts
const { text } = await api.runtime.mediaUnderstanding.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  // Optional when MIME cannot be inferred reliably:
  mime: "audio/ogg",
});
```

Notlar:

- `api.runtime.mediaUnderstanding.*`, görsel/ses/video anlama için tercih edilen paylaşılan yüzeydir.
- Core medya-anlama ses yapılandırmasını (`tools.media.audio`) ve sağlayıcı fallback sırasını kullanır.
- Yazıya dökme çıktısı üretilmediğinde `{ text: undefined }` döndürür (örneğin atlanan/desteklenmeyen girdiler).
- `api.runtime.stt.transcribeAudioFile(...)` bir uyumluluk takma adı olarak kalır.

Plugin'ler ayrıca `api.runtime.subagent` üzerinden arka planda alt agent çalıştırmaları başlatabilir:

```ts
const result = await api.runtime.subagent.run({
  sessionKey: "agent:main:subagent:search-helper",
  message: "Expand this query into focused follow-up searches.",
  provider: "openai",
  model: "gpt-4.1-mini",
  deliver: false,
});
```

Notlar:

- `provider` ve `model`, kalıcı oturum değişiklikleri değil, çalışma başına isteğe bağlı geçersiz kılmalardır.
- OpenClaw bu geçersiz kılma alanlarını yalnızca güvenilir çağıranlar için dikkate alır.
- Plugin'e ait fallback çalıştırmaları için operatörlerin `plugins.entries.<id>.subagent.allowModelOverride: true` ile açıkça izin vermesi gerekir.
- Güvenilir plugin'leri belirli kanonik `provider/model` hedefleriyle sınırlamak için `plugins.entries.<id>.subagent.allowedModels` kullanın veya açıkça herhangi bir hedefe izin vermek için `"*"` kullanın.
- Güvenilmeyen plugin alt agent çalıştırmaları yine de çalışır, ancak geçersiz kılma istekleri sessizce fallback yapmak yerine reddedilir.

Web arama için plugin'ler, agent araç bağlantısının içine ulaşmak yerine
paylaşılan çalışma zamanı yardımcısını tüketebilir:

```ts
const providers = api.runtime.webSearch.listProviders({
  config: api.config,
});

const result = await api.runtime.webSearch.search({
  config: api.config,
  args: {
    query: "OpenClaw plugin runtime helpers",
    count: 5,
  },
});
```

Plugin'ler ayrıca
`api.registerWebSearchProvider(...)` aracılığıyla web-search sağlayıcıları kaydedebilir.

Notlar:

- Sağlayıcı seçimini, kimlik bilgisi çözümlemesini ve paylaşılan istek semantiğini core içinde tutun.
- Satıcıya özgü arama taşımaları için web-search sağlayıcılarını kullanın.
- `api.runtime.webSearch.*`, özellik/kanal plugin'lerinin agent araç sarmalayıcısına bağımlı olmadan arama davranışına ihtiyaç duyduğu durumlar için tercih edilen paylaşılan yüzeydir.

### `api.runtime.imageGeneration`

```ts
const result = await api.runtime.imageGeneration.generate({
  config: api.config,
  args: { prompt: "A friendly lobster mascot", size: "1024x1024" },
});

const providers = api.runtime.imageGeneration.listProviders({
  config: api.config,
});
```

- `generate(...)`: yapılandırılmış görsel üretim sağlayıcı zincirini kullanarak bir görsel üretir.
- `listProviders(...)`: kullanılabilir görsel üretim sağlayıcılarını ve yeteneklerini listeler.

## Gateway HTTP rotaları

Plugin'ler `api.registerHttpRoute(...)` ile HTTP uç noktaları açığa çıkarabilir.

```ts
api.registerHttpRoute({
  path: "/acme/webhook",
  auth: "plugin",
  match: "exact",
  handler: async (_req, res) => {
    res.statusCode = 200;
    res.end("ok");
    return true;
  },
});
```

Rota alanları:

- `path`: gateway HTTP sunucusu altındaki rota yolu.
- `auth`: zorunlu. Normal gateway auth gerektirmek için `"gateway"`, plugin yönetimli auth/webhook doğrulaması için `"plugin"` kullanın.
- `match`: isteğe bağlı. `"exact"` (varsayılan) veya `"prefix"`.
- `replaceExisting`: isteğe bağlı. Aynı plugin'in kendi mevcut rota kaydını değiştirmesine izin verir.
- `handler`: rota isteği işlediğinde `true` döndürmelidir.

Notlar:

- `api.registerHttpHandler(...)` kaldırılmıştır ve plugin yükleme hatasına neden olur. Bunun yerine `api.registerHttpRoute(...)` kullanın.
- Plugin rotaları `auth` değerini açıkça belirtmelidir.
- Tam `path + match` çakışmaları, `replaceExisting: true` olmadıkça reddedilir ve bir plugin başka bir plugin'in rotasını değiştiremez.
- Farklı `auth` düzeylerine sahip örtüşen rotalar reddedilir. `exact`/`prefix` fallthrough zincirlerini yalnızca aynı auth düzeyinde tutun.
- `auth: "plugin"` rotaları otomatik olarak operatör çalışma zamanı kapsamları almaz. Bunlar ayrıcalıklı Gateway yardımcı çağrıları için değil,
  plugin yönetimli webhook'lar/imza doğrulaması içindir.
- `auth: "gateway"` rotaları bir Gateway istek çalışma zamanı kapsamı içinde çalışır, ancak bu kapsam kasıtlı olarak tutucudur:
  - paylaşılan gizli bearer auth (`gateway.auth.mode = "token"` / `"password"`) plugin-route çalışma zamanı kapsamlarını, çağıran `x-openclaw-scopes` gönderse bile `operator.write` üzerinde sabit tutar
  - güvenilir kimlik taşıyan HTTP modları (örneğin `trusted-proxy` veya özel ingress üzerinde `gateway.auth.mode = "none"`) `x-openclaw-scopes` değerini yalnızca üst bilgi açıkça mevcutsa dikkate alır
  - bu kimlik taşıyan plugin-route isteklerinde `x-openclaw-scopes` yoksa çalışma zamanı kapsamı `operator.write` değerine geri düşer
- Pratik kural: gateway-auth plugin rotasının örtük bir yönetici yüzeyi olduğunu varsaymayın. Rotanızın yalnızca yöneticiye özgü davranışa ihtiyacı varsa, kimlik taşıyan bir auth modu gerektirin ve açık `x-openclaw-scopes` üst bilgi sözleşmesini belgeleyin.

## Plugin SDK içe aktarma yolları

Plugin yazarken tek parça `openclaw/plugin-sdk` içe aktarımı yerine
SDK alt yollarını kullanın:

- Plugin kayıt ilkel öğeleri için `openclaw/plugin-sdk/plugin-entry`.
- Genel paylaşılan plugin'e dönük sözleşme için `openclaw/plugin-sdk/core`.
- Kök `openclaw.json` Zod şema dışa aktarımı
  (`OpenClawSchema`) için `openclaw/plugin-sdk/config-schema`.
- `openclaw/plugin-sdk/channel-setup`,
  `openclaw/plugin-sdk/setup-runtime`,
  `openclaw/plugin-sdk/setup-adapter-runtime`,
  `openclaw/plugin-sdk/setup-tools`,
  `openclaw/plugin-sdk/channel-pairing`,
  `openclaw/plugin-sdk/channel-contract`,
  `openclaw/plugin-sdk/channel-feedback`,
  `openclaw/plugin-sdk/channel-inbound`,
  `openclaw/plugin-sdk/channel-lifecycle`,
  `openclaw/plugin-sdk/channel-reply-pipeline`,
  `openclaw/plugin-sdk/command-auth`,
  `openclaw/plugin-sdk/secret-input` ve
  `openclaw/plugin-sdk/webhook-ingress` gibi kararlı kanal ilkel öğelerini; paylaşılan kurulum/auth/yanıt/webhook
  bağlantıları için kullanın. `channel-inbound`, debounce, mention eşleme,
  gelen mention-policy yardımcıları, zarf biçimlendirme ve gelen zarf
  bağlam yardımcıları için paylaşılan ana yerdir.
  `channel-setup`, dar isteğe bağlı kurulum yüzeyidir.
  `setup-runtime`, `setupEntry` /
  ertelenmiş başlangıç tarafından kullanılan çalışma zamanı güvenli kurulum yüzeyidir; içe aktarma açısından güvenli kurulum yama bağdaştırıcılarını da içerir.
  `setup-adapter-runtime`, ortam farkında hesap-kurulum bağdaştırıcı yüzeyidir.
  `setup-tools`, küçük CLI/arşiv/belge yardımcı yüzeyidir (`formatCliCommand`,
  `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`,
  `CONFIG_DIR`).
- `openclaw/plugin-sdk/channel-config-helpers`,
  `openclaw/plugin-sdk/allow-from`,
  `openclaw/plugin-sdk/channel-config-schema`,
  `openclaw/plugin-sdk/telegram-command-config`,
  `openclaw/plugin-sdk/channel-policy`,
  `openclaw/plugin-sdk/approval-runtime`,
  `openclaw/plugin-sdk/config-runtime`,
  `openclaw/plugin-sdk/infra-runtime`,
  `openclaw/plugin-sdk/agent-runtime`,
  `openclaw/plugin-sdk/lazy-runtime`,
  `openclaw/plugin-sdk/reply-history`,
  `openclaw/plugin-sdk/routing`,
  `openclaw/plugin-sdk/status-helpers`,
  `openclaw/plugin-sdk/text-runtime`,
  `openclaw/plugin-sdk/runtime-store` ve
  `openclaw/plugin-sdk/directory-runtime` gibi alan alt yollarını; paylaşılan çalışma zamanı/yapılandırma yardımcıları için kullanın.
  `telegram-command-config`, Telegram özel
  komut normalizasyonu/doğrulaması için dar genel yüzeydir ve paketlenmiş
  Telegram sözleşme yüzeyi geçici olarak kullanılamadığında bile kullanılabilir kalır.
  `text-runtime`, asistan tarafından görülebilen metin ayıklama,
  markdown render/parçalama yardımcıları, redaksiyon
  yardımcıları, directive-tag yardımcıları ve güvenli metin yardımcıları dahil paylaşılan metin/markdown/logging yüzeyidir.
- Onaya özgü kanal yüzeyleri plugin üzerinde tek bir `approvalCapability`
  sözleşmesini tercih etmelidir. Sonra core onay auth, teslim, render ve
  yerel yönlendirme davranışını ilgisiz plugin alanlarına karıştırmak yerine
  bu tek yetenek üzerinden okur.
- `openclaw/plugin-sdk/channel-runtime` kullanımdan kaldırılmıştır ve yalnızca
  daha eski plugin'ler için uyumluluk sarmalayıcısı olarak kalır. Yeni kod daha dar
  genel ilkel öğeleri içe aktarmalıdır ve depo kodu sarmalayıcıya yeni içe aktarımlar eklememelidir.
- Paketlenmiş uzantı iç yapıları özel kalır. Harici plugin'ler yalnızca
  `openclaw/plugin-sdk/*` alt yollarını kullanmalıdır. OpenClaw core/test kodu,
  `index.js`, `api.js`,
  `runtime-api.js`, `setup-entry.js` ve `login-qr-api.js` gibi dar kapsamlı dosyalar dahil olmak üzere
  bir plugin paket kökü altındaki depo genel giriş noktalarını kullanabilir.
  Core'dan veya başka bir uzantıdan asla bir plugin paketinin `src/*` yolunu içe aktarmayın.
- Depo giriş noktası ayrımı:
  `<plugin-package-root>/api.js` yardımcı/türler barrel dosyasıdır,
  `<plugin-package-root>/runtime-api.js` yalnızca çalışma zamanı barrel dosyasıdır,
  `<plugin-package-root>/index.js` paketlenmiş plugin girişidir,
  ve `<plugin-package-root>/setup-entry.js` kurulum plugin girişidir.
- Mevcut paketlenmiş provider örnekleri:
  - Anthropic, `wrapAnthropicProviderStream`, beta-header yardımcıları ve `service_tier`
    ayrıştırma gibi Claude akış yardımcıları için `api.js` / `contract-api.js` kullanır.
  - OpenAI, sağlayıcı oluşturucular, varsayılan model yardımcıları ve
    gerçek zamanlı sağlayıcı oluşturucular için `api.js` kullanır.
  - OpenRouter, sağlayıcı oluşturucusu ile birlikte onboarding/yapılandırma
    yardımcıları için `api.js` kullanır; `register.runtime.js` ise depo içi kullanım için
    genel `plugin-sdk/provider-stream` yardımcılarını yeniden dışa aktarabilir.
- Facade ile yüklenen genel giriş noktaları, varsa etkin çalışma zamanı yapılandırma anlık görüntüsünü tercih eder;
  OpenClaw henüz bir çalışma zamanı anlık görüntüsü sunmuyorsa
  disk üzerindeki çözümlenmiş yapılandırma dosyasına geri düşer.
- Genel paylaşılan ilkel öğeler, tercih edilen genel SDK sözleşmesi olmaya devam eder.
  Paketlenmiş kanala markalı yardımcı yüzeylerden küçük bir ayrılmış uyumluluk kümesi hâlâ vardır.
  Bunları yeni üçüncü taraf içe aktarma hedefleri olarak değil, paketlenmiş bakım/uyumluluk yüzeyleri olarak değerlendirin;
  yeni çapraz kanal sözleşmeleri yine genel `plugin-sdk/*` alt yollarına veya plugin-yerel `api.js` /
  `runtime-api.js` barrel dosyalarına inmelidir.

Uyumluluk notu:

- Yeni kod için kök `openclaw/plugin-sdk` barrel dosyasından kaçının.
- Önce dar ve kararlı ilkel öğeleri tercih edin. Yeni setup/pairing/reply/
  feedback/contract/inbound/threading/command/secret-input/webhook/infra/
  allowlist/status/message-tool alt yolları, yeni paketlenmiş ve harici plugin işleri için amaçlanan sözleşmedir.
  Hedef ayrıştırma/eşleme `openclaw/plugin-sdk/channel-targets` üzerinde olmalıdır.
  Message action geçitleri ve reaction message-id yardımcıları
  `openclaw/plugin-sdk/channel-actions` üzerinde yer almalıdır.
- Paketlenmiş uzantıya özgü yardımcı barrel dosyaları varsayılan olarak kararlı değildir. Bir
  yardımcı yalnızca paketlenmiş bir uzantı tarafından gerekiyorsa, bunu
  `openclaw/plugin-sdk/<extension>` içine yükseltmek yerine uzantının yerel `api.js` veya `runtime-api.js` yüzeyinin arkasında tutun.
- Yeni paylaşılan yardımcı yüzeyler kanala markalı değil, genel olmalıdır. Paylaşılan hedef
  ayrıştırma `openclaw/plugin-sdk/channel-targets` üzerinde yer alır; kanala özgü
  iç yapılar ise sahip plugin'in yerel `api.js` veya `runtime-api.js`
  yüzeyinin arkasında kalır.
- `image-generation`,
  `media-understanding` ve `speech` gibi yeteneğe özgü alt yollar bugün paketlenmiş/yerel plugin'ler tarafından kullanıldığı için vardır.
  Bunların varlığı tek başına dışa aktarılan her yardımcının uzun vadeli
  dondurulmuş bir harici sözleşme olduğu anlamına gelmez.

## Message araç şemaları

Plugin'ler, kanala özgü `describeMessageTool(...)` şema
katkılarının sahibi olmalıdır. Sağlayıcıya özgü alanları paylaşılan core yerine plugin içinde tutun.

Paylaşılan taşınabilir şema parçaları için,
`openclaw/plugin-sdk/channel-actions` üzerinden dışa aktarılan genel yardımcıları yeniden kullanın:

- düğme ızgarası tarzı yükler için `createMessageToolButtonsSchema()`
- yapılandırılmış kart yükleri için `createMessageToolCardSchema()`

Bir şema biçimi yalnızca bir sağlayıcı için anlamlıysa,
bunu paylaşılan SDK'ya yükseltmek yerine o plugin'in kendi kaynağında tanımlayın.

## Kanal hedef çözümleme

Kanal plugin'leri kanala özgü hedef semantiğinin sahibi olmalıdır. Paylaşılan
giden barındırıcıyı genel tutun ve sağlayıcı kuralları için mesajlaşma bağdaştırıcı yüzeyini kullanın:

- `messaging.inferTargetChatType({ to })`, normalize edilmiş bir hedefin
  dizin aramasından önce `direct`, `group` veya `channel` olarak ele alınıp alınmayacağına karar verir.
- `messaging.targetResolver.looksLikeId(raw, normalized)`, bir girdinin
  dizin araması yerine doğrudan kimlik benzeri çözümlemeye atlanması gerekip gerekmediğini core'a söyler.
- `messaging.targetResolver.resolveTarget(...)`, core normalizasyondan sonra veya
  dizin kaçırıldıktan sonra son sağlayıcıya ait çözümlemeye ihtiyaç duyduğunda plugin fallback yoludur.
- `messaging.resolveOutboundSessionRoute(...)`, hedef çözümlendikten sonra sağlayıcıya özgü oturum
  rota kurulumunun sahibidir.

Önerilen ayrım:

- Eşler/gruplar aranmasından önce gerçekleşmesi gereken kategori kararları için `inferTargetChatType` kullanın.
- “Bunu açık/yerel hedef kimliği olarak ele al” kontrolleri için `looksLikeId` kullanın.
- Geniş dizin araması için değil, sağlayıcıya özgü normalizasyon fallback'i için `resolveTarget` kullanın.
- Sohbet kimlikleri, iş parçacığı kimlikleri, JID'ler, handle'lar ve oda kimlikleri gibi sağlayıcıya özgü kimlikleri genel SDK alanlarında değil,
  `target` değerleri veya sağlayıcıya özgü parametreler içinde tutun.

## Yapılandırma destekli dizinler

Yapılandırmadan dizin girdileri türeten plugin'ler bu mantığı plugin içinde tutmalı
ve
`openclaw/plugin-sdk/directory-runtime` içindeki paylaşılan yardımcıları yeniden kullanmalıdır.

Bunu, bir kanalın aşağıdakiler gibi yapılandırma destekli eşlere/gruplara ihtiyaç duyduğu durumlarda kullanın:

- izin listesi güdümlü DM eşleri
- yapılandırılmış kanal/grup eşlemeleri
- hesap kapsamlı statik dizin fallback'leri

`directory-runtime` içindeki paylaşılan yardımcılar yalnızca genel işlemleri ele alır:

- sorgu filtreleme
- sınır uygulama
- tekilleştirme/normalizasyon yardımcıları
- `ChannelDirectoryEntry[]` oluşturma

Kanala özgü hesap inceleme ve kimlik normalizasyonu
plugin uygulamasında kalmalıdır.

## Provider katalogları

Provider plugin'leri, çıkarım için model kataloglarını
`registerProvider({ catalog: { run(...) { ... } } })` ile tanımlayabilir.

`catalog.run(...)`, OpenClaw'ın `models.providers` içine yazdığı ile aynı biçimi döndürür:

- tek bir sağlayıcı girdisi için `{ provider }`
- birden fazla sağlayıcı girdisi için `{ providers }`

Plugin, sağlayıcıya özgü model kimliklerinin, temel URL varsayılanlarının veya auth-kapılı model meta verilerinin sahibi olduğunda
`catalog` kullanın.

`catalog.order`, bir plugin'in kataloğunun OpenClaw'ın yerleşik örtük sağlayıcılarına göre
ne zaman birleşeceğini denetler:

- `simple`: düz API-key veya env güdümlü sağlayıcılar
- `profile`: auth profilleri mevcut olduğunda görünen sağlayıcılar
- `paired`: birbiriyle ilişkili birden çok sağlayıcı girdisi sentezleyen sağlayıcılar
- `late`: diğer örtük sağlayıcılardan sonra son geçiş

Daha geç gelen sağlayıcılar anahtar çakışmasında kazanır; böylece plugin'ler
aynı sağlayıcı kimliğine sahip yerleşik bir sağlayıcı girdisini kasıtlı olarak geçersiz kılabilir.

Uyumluluk:

- `discovery` legacy bir takma ad olarak hâlâ çalışır
- hem `catalog` hem `discovery` kayıtlıysa, OpenClaw `catalog` kullanır

## Salt okunur kanal inceleme

Plugin'iniz bir kanal kaydediyorsa, `resolveAccount(...)` yanında
`plugin.config.inspectAccount(cfg, accountId)` uygulamayı tercih edin.

Neden:

- `resolveAccount(...)` çalışma zamanı yoludur. Kimlik bilgilerinin
  tamamen somutlaştırıldığını varsayabilir ve gerekli gizli bilgiler eksikse hızlı başarısız olabilir.
- `openclaw status`, `openclaw status --all`,
  `openclaw channels status`, `openclaw channels resolve` ve doctor/yapılandırma
  onarım akışları gibi salt okunur komut yolları, yapılandırmayı açıklamak için
  çalışma zamanı kimlik bilgilerini somutlaştırmak zorunda olmamalıdır.

Önerilen `inspectAccount(...)` davranışı:

- Yalnızca açıklayıcı hesap durumu döndürün.
- `enabled` ve `configured` değerlerini koruyun.
- İlgili olduğunda şu gibi kimlik bilgisi kaynak/durum alanlarını ekleyin:
  - `tokenSource`, `tokenStatus`
  - `botTokenSource`, `botTokenStatus`
  - `appTokenSource`, `appTokenStatus`
  - `signingSecretSource`, `signingSecretStatus`
- Salt okunur kullanılabilirliği raporlamak için ham token değerlerini döndürmeniz gerekmez.
  `tokenStatus: "available"` döndürmek (ve eşleşen kaynak alanı ile)
  durum tarzı komutlar için yeterlidir.
- Bir kimlik bilgisi SecretRef yoluyla yapılandırılmış ama
  mevcut komut yolunda kullanılamıyorsa `configured_unavailable` kullanın.

Bu, salt okunur komutların “bu komut yolunda yapılandırılmış ama kullanılamıyor”
durumunu raporlamasını sağlar; çökmek veya hesabı yapılandırılmamış gibi yanlış raporlamak yerine.

## Paket paketleri

Bir plugin dizini, `openclaw.extensions` içeren bir `package.json` bulundurabilir:

```json
{
  "name": "my-pack",
  "openclaw": {
    "extensions": ["./src/safety.ts", "./src/tools.ts"],
    "setupEntry": "./src/setup-entry.ts"
  }
}
```

Her girdi bir plugin'e dönüşür. Paket birden çok uzantı listeliyorsa, plugin kimliği
`name/<fileBase>` olur.

Plugin'iniz npm bağımlılıkları içe aktarıyorsa, `node_modules`
kullanılabilir olsun diye onları o dizine kurun (`npm install` / `pnpm install`).

Güvenlik koruması: her `openclaw.extensions` girdisi, sembolik bağlantı çözümlemesinden sonra
plugin dizini içinde kalmalıdır. Paket dizininden kaçan girdiler
reddedilir.

Güvenlik notu: `openclaw plugins install`, plugin bağımlılıklarını
`npm install --omit=dev --ignore-scripts` ile kurar (yaşam döngüsü betikleri yok, çalışma zamanında geliştirme bağımlılıkları yoktur). Plugin bağımlılık
ağaçlarını "pure JS/TS" tutun ve `postinstall` derlemeleri gerektiren paketlerden kaçının.

İsteğe bağlı: `openclaw.setupEntry`, hafif bir yalnızca-kurulum modülüne işaret edebilir.
OpenClaw, devre dışı bir kanal plugin'i için kurulum yüzeylerine ihtiyaç duyduğunda veya
bir kanal plugin'i etkin ama hâlâ yapılandırılmamış olduğunda, tam plugin girişi yerine
`setupEntry` yükler. Bu, ana plugin girişiniz araçları, kancaları veya
diğer yalnızca çalışma zamanına özgü kodları da bağlıyorsa başlangıcı ve kurulumu hafif tutar.

İsteğe bağlı:
`openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`, gateway'in
dinleme öncesi başlangıç aşamasında yapılandırılmış bir kanal plugin'ini,
kanal zaten yapılandırılmış olsa bile aynı `setupEntry` yoluna alabilir.

Bunu yalnızca `setupEntry`, gateway dinlemeye başlamadan önce
var olması gereken başlangıç yüzeyini tamamen kapsıyorsa kullanın. Pratikte bu,
setup girişinin başlangıcın bağımlı olduğu her kanala ait yeteneği kaydetmesi gerektiği anlamına gelir; örneğin:

- kanal kaydının kendisi
- gateway dinlemeye başlamadan önce kullanılabilir olması gereken tüm HTTP rotaları
- aynı pencerede var olması gereken tüm gateway yöntemleri, araçlar veya hizmetler

Tam girişiniz hâlâ gerekli herhangi bir başlangıç yeteneğinin sahibiyse, bu bayrağı etkinleştirmeyin.
Plugin'i varsayılan davranışta bırakın ve OpenClaw'ın başlangıç sırasında
tam girişi yüklemesine izin verin.

Paketlenmiş kanallar ayrıca, tam kanal çalışma zamanı yüklenmeden önce core'un danışabileceği
yalnızca-kurulum sözleşme-yüzeyi yardımcıları yayımlayabilir. Geçerli kurulum yükseltme yüzeyi şudur:

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

Core, tam plugin girişini yüklemeden legacy tek hesaplı kanal
yapılandırmasını `channels.<id>.accounts.*` biçimine yükseltmesi gerektiğinde bu yüzeyi kullanır.
Matrix mevcut paketlenmiş örnektir: adlandırılmış hesaplar zaten varsa yalnızca auth/bootstrap anahtarlarını
adlandırılmış yükseltilmiş hesaba taşır ve her zaman
`accounts.default` oluşturmak yerine yapılandırılmış kanonik olmayan bir varsayılan-hesap anahtarını koruyabilir.

Bu kurulum yama bağdaştırıcıları, paketlenmiş sözleşme-yüzeyi keşfini tembel tutar.
İçe aktarma süresi hafif kalır; yükseltme yüzeyi modül içe aktarımı sırasında
paketlenmiş kanal başlangıcına yeniden girmek yerine yalnızca ilk kullanımda yüklenir.

Bu başlangıç yüzeyleri gateway RPC yöntemleri içerdiğinde, onları
plugin'e özgü bir ön ek üzerinde tutun. Core yönetici ad alanları (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) ayrılmış kalır ve bir plugin
daha dar bir kapsam istese bile her zaman `operator.admin` olarak çözümlenir.

Örnek:

```json
{
  "name": "@scope/my-channel",
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "startup": {
      "deferConfiguredChannelFullLoadUntilAfterListen": true
    }
  }
}
```

### Kanal katalog meta verileri

Kanal plugin'leri `openclaw.channel` aracılığıyla kurulum/keşif meta verisi ve
`openclaw.install` aracılığıyla kurulum ipuçları duyurabilir. Bu, core kataloğunu verisiz tutar.

Örnek:

```json
{
  "name": "@openclaw/nextcloud-talk",
  "openclaw": {
    "extensions": ["./index.ts"],
    "channel": {
      "id": "nextcloud-talk",
      "label": "Nextcloud Talk",
      "selectionLabel": "Nextcloud Talk (self-hosted)",
      "docsPath": "/channels/nextcloud-talk",
      "docsLabel": "nextcloud-talk",
      "blurb": "Self-hosted chat via Nextcloud Talk webhook bots.",
      "order": 65,
      "aliases": ["nc-talk", "nc"]
    },
    "install": {
      "npmSpec": "@openclaw/nextcloud-talk",
      "localPath": "<bundled-plugin-local-path>",
      "defaultChoice": "npm"
    }
  }
}
```

En az örneğin ötesinde faydalı `openclaw.channel` alanları şunlardır:

- `detailLabel`: daha zengin katalog/durum yüzeyleri için ikincil etiket
- `docsLabel`: belgeler bağlantısı için bağlantı metnini geçersiz kılar
- `preferOver`: bu katalog girdisinin daha alt öncelikli plugin/kanal kimliklerinin önüne geçmesi gereken durumlar
- `selectionDocsPrefix`, `selectionDocsOmitLabel`, `selectionExtras`: seçim yüzeyi metin denetimleri
- `markdownCapable`: giden biçimlendirme kararları için kanalı markdown yetenekli olarak işaretler
- `exposure.configured`: `false` olarak ayarlanırsa kanalı yapılandırılmış kanal listeleme yüzeylerinden gizler
- `exposure.setup`: `false` olarak ayarlanırsa kanalı etkileşimli kurulum/yapılandırma seçicilerinden gizler
- `exposure.docs`: belgeler gezinti yüzeyleri için kanalı iç/özel olarak işaretler
- `showConfigured` / `showInSetup`: uyumluluk için legacy takma adlar hâlâ kabul edilir; `exposure` tercih edin
- `quickstartAllowFrom`: kanalı standart quickstart `allowFrom` akışına alır
- `forceAccountBinding`: yalnızca bir hesap olsa bile açık hesap bağlaması gerektirir
- `preferSessionLookupForAnnounceTarget`: duyuru hedefi çözümlemede oturum aramasını tercih eder

OpenClaw ayrıca **harici kanal kataloglarını** da birleştirebilir (örneğin bir MPM
kayıt dışa aktarımı). Şu konumlardan birine bir JSON dosyası bırakın:

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

Ya da `OPENCLAW_PLUGIN_CATALOG_PATHS` (veya `OPENCLAW_MPM_CATALOG_PATHS`) değerini
bir veya daha fazla JSON dosyasına yönlendirin (virgül/noktalı virgül/`PATH` ile ayrılmış).
Her dosya şu biçimi içermelidir: `{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }`.
Ayrıştırıcı, `"entries"` anahtarı için legacy takma adlar olarak `"packages"` veya `"plugins"` değerlerini de kabul eder.

## Bağlam motoru plugin'leri

Bağlam motoru plugin'leri, alma, derleme
ve compaction için oturum bağlamı orkestrasyonunun sahibidir. Plugin'inizden
`api.registerContextEngine(id, factory)` ile kaydedin, ardından etkin motoru
`plugins.slots.contextEngine` ile seçin.

Bellek arama veya kanca eklemekten öteye geçip varsayılan bağlam
ardışık düzenini değiştirmek veya genişletmek istiyorsanız bunu kullanın.

```ts
import { buildMemorySystemPromptAddition } from "openclaw/plugin-sdk/core";

export default function (api) {
  api.registerContextEngine("lossless-claw", () => ({
    info: { id: "lossless-claw", name: "Lossless Claw", ownsCompaction: true },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages, availableTools, citationsMode }) {
      return {
        messages,
        estimatedTokens: 0,
        systemPromptAddition: buildMemorySystemPromptAddition({
          availableTools: availableTools ?? new Set(),
          citationsMode,
        }),
      };
    },
    async compact() {
      return { ok: true, compacted: false };
    },
  }));
}
```

Motorunuz compaction algoritmasının sahibi **değilse**, `compact()`
işlevini uygulanmış halde tutun ve açıkça devredin:

```ts
import {
  buildMemorySystemPromptAddition,
  delegateCompactionToRuntime,
} from "openclaw/plugin-sdk/core";

export default function (api) {
  api.registerContextEngine("my-memory-engine", () => ({
    info: {
      id: "my-memory-engine",
      name: "My Memory Engine",
      ownsCompaction: false,
    },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages, availableTools, citationsMode }) {
      return {
        messages,
        estimatedTokens: 0,
        systemPromptAddition: buildMemorySystemPromptAddition({
          availableTools: availableTools ?? new Set(),
          citationsMode,
        }),
      };
    },
    async compact(params) {
      return await delegateCompactionToRuntime(params);
    },
  }));
}
```

## Yeni bir yetenek ekleme

Bir plugin mevcut API'ye uymayan davranışa ihtiyaç duyduğunda,
plugin sistemini özel bir içeri dalma ile atlamayın. Eksik yeteneği ekleyin.

Önerilen sıra:

1. core sözleşmesini tanımlayın
   Core'un hangi paylaşılan davranışın sahibi olması gerektiğine karar verin: ilke, fallback, yapılandırma birleştirme,
   yaşam döngüsü, kanala dönük semantik ve çalışma zamanı yardımcı biçimi.
2. typed plugin kayıt/çalışma zamanı yüzeyleri ekleyin
   `OpenClawPluginApi` ve/veya `api.runtime` yüzeyini en küçük yararlı
   typed yetenek yüzeyiyle genişletin.
3. core + kanal/özellik tüketicilerini bağlayın
   Kanallar ve özellik plugin'leri yeni yeteneği bir satıcı uygulamasını doğrudan içe aktararak değil,
   core üzerinden tüketmelidir.
4. satıcı uygulamalarını kaydedin
   Sonra satıcı plugin'leri arka uçlarını bu yeteneğe karşı kaydeder.
5. sözleşme kapsamı ekleyin
   Sahipliğin ve kayıt biçiminin zamanla açık kalması için testler ekleyin.

OpenClaw bu şekilde görüş sahibi kalır ama tek bir
sağlayıcının dünya görüşüne sabit kodlanmış hale gelmez. Somut dosya denetim listesi ve çalışılmış örnek için
[Capability Cookbook](/tr/plugins/architecture) sayfasına bakın.

### Yetenek denetim listesi

Yeni bir yetenek eklediğinizde, uygulama genellikle şu
yüzeylere birlikte dokunmalıdır:

- `src/<capability>/types.ts` içindeki core sözleşme türleri
- `src/<capability>/runtime.ts` içindeki core runner/çalışma zamanı yardımcısı
- `src/plugins/types.ts` içindeki plugin API kayıt yüzeyi
- `src/plugins/registry.ts` içindeki plugin kayıt defteri bağlantısı
- özellik/kanal plugin'lerinin bunu tüketmesi gerektiğinde `src/plugins/runtime/*` içindeki
  plugin çalışma zamanı açığa çıkarımı
- `src/test-utils/plugin-registration.ts` içindeki yakalama/test yardımcıları
- `src/plugins/contracts/registry.ts` içindeki sahiplik/sözleşme doğrulamaları
- `docs/` içindeki operatör/plugin belgeleri

Bu yüzeylerden biri eksikse, bu genellikle yeteneğin henüz tam
entegre olmadığının işaretidir.

### Yetenek şablonu

Asgari desen:

```ts
// core contract
export type VideoGenerationProviderPlugin = {
  id: string;
  label: string;
  generateVideo: (req: VideoGenerationRequest) => Promise<VideoGenerationResult>;
};

// plugin API
api.registerVideoGenerationProvider({
  id: "openai",
  label: "OpenAI",
  async generateVideo(req) {
    return await generateOpenAiVideo(req);
  },
});

// shared runtime helper for feature/channel plugins
const clip = await api.runtime.videoGeneration.generate({
  prompt: "Show the robot walking through the lab.",
  cfg,
});
```

Sözleşme testi deseni:

```ts
expect(findVideoGenerationProviderIdsForPlugin("openai")).toEqual(["openai"]);
```

Bu, kuralı basit tutar:

- core yetenek sözleşmesinin + orkestrasyonun sahibidir
- satıcı plugin'leri satıcı uygulamalarının sahibidir
- özellik/kanal plugin'leri çalışma zamanı yardımcılarını tüketir
- sözleşme testleri sahipliği açık tutar
