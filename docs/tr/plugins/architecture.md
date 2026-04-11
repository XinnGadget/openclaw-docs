---
read_when:
    - Yerel OpenClaw plugin’lerini oluşturma veya hata ayıklama
    - Plugin yetenek modelini veya sahiplik sınırlarını anlama
    - Plugin yükleme işlem hattı veya kayıt defteri üzerinde çalışma
    - Sağlayıcı çalışma zamanı kancalarını veya kanal plugin’lerini uygulama
sidebarTitle: Internals
summary: 'Plugin iç bileşenleri: yetenek modeli, sahiplik, sözleşmeler, yükleme işlem hattı ve çalışma zamanı yardımcıları'
title: Plugin İç Bileşenleri
x-i18n:
    generated_at: "2026-04-11T15:16:00Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7cac67984d0d729c0905bcf5c18372fb0d9b02bbd3a531580b7e2ef483ef40a6
    source_path: plugins/architecture.md
    workflow: 15
---

# Plugin İç Bileşenleri

<Info>
  Bu, **derin mimari başvuru** sayfasıdır. Pratik kılavuzlar için şunlara bakın:
  - [Plugin’leri yükleme ve kullanma](/tr/tools/plugin) — kullanıcı kılavuzu
  - [Başlangıç](/tr/plugins/building-plugins) — ilk plugin öğreticisi
  - [Kanal Plugin’leri](/tr/plugins/sdk-channel-plugins) — bir mesajlaşma kanalı oluşturun
  - [Sağlayıcı Plugin’leri](/tr/plugins/sdk-provider-plugins) — bir model sağlayıcısı oluşturun
  - [SDK Genel Bakış](/tr/plugins/sdk-overview) — içe aktarma eşlemesi ve kayıt API’si
</Info>

Bu sayfa, OpenClaw plugin sisteminin iç mimarisini kapsar.

## Genel yetenek modeli

Yetenekler, OpenClaw içindeki genel **yerel plugin** modelidir. Her
yerel OpenClaw plugin’i bir veya daha fazla yetenek türüne kayıt olur:

| Yetenek               | Kayıt yöntemi                                    | Örnek plugin’ler                     |
| --------------------- | ------------------------------------------------ | ------------------------------------ |
| Metin çıkarımı        | `api.registerProvider(...)`                      | `openai`, `anthropic`                |
| CLI çıkarım arka ucu  | `api.registerCliBackend(...)`                    | `openai`, `anthropic`                |
| Konuşma               | `api.registerSpeechProvider(...)`                | `elevenlabs`, `microsoft`            |
| Gerçek zamanlı yazıya dökme | `api.registerRealtimeTranscriptionProvider(...)` | `openai`                             |
| Gerçek zamanlı ses    | `api.registerRealtimeVoiceProvider(...)`         | `openai`                             |
| Medya anlama          | `api.registerMediaUnderstandingProvider(...)`    | `openai`, `google`                   |
| Görsel oluşturma      | `api.registerImageGenerationProvider(...)`       | `openai`, `google`, `fal`, `minimax` |
| Müzik oluşturma       | `api.registerMusicGenerationProvider(...)`       | `google`, `minimax`                  |
| Video oluşturma       | `api.registerVideoGenerationProvider(...)`       | `qwen`                               |
| Web getirme           | `api.registerWebFetchProvider(...)`              | `firecrawl`                          |
| Web arama             | `api.registerWebSearchProvider(...)`             | `google`                             |
| Kanal / mesajlaşma    | `api.registerChannel(...)`                       | `msteams`, `matrix`                  |

Sıfır yetenek kaydeden ancak kancalar, araçlar veya
servisler sağlayan bir plugin, **eski yalnızca-kanca** plugin’idir. Bu desen hâlâ tamamen desteklenmektedir.

### Harici uyumluluk yaklaşımı

Yetenek modeli çekirdeğe eklenmiştir ve bugün paketlenmiş/yerel plugin’ler
tarafından kullanılmaktadır, ancak harici plugin uyumluluğu için
“dışa aktarılıyor, dolayısıyla dondurulmuştur” yaklaşımından daha sıkı bir çıta gerekir.

Güncel yönlendirme:

- **mevcut harici plugin’ler:** kanca tabanlı entegrasyonları çalışır durumda tutun; bunu
  uyumluluk tabanı olarak değerlendirin
- **yeni paketlenmiş/yerel plugin’ler:** satıcıya özgü iç erişimler veya yeni yalnızca-kanca tasarımları yerine
  açık yetenek kaydını tercih edin
- **yetenek kaydını benimseyen harici plugin’ler:** izin verilir, ancak belgeler bir sözleşmeyi açıkça kararlı olarak işaretlemedikçe
  yeteneğe özgü yardımcı yüzeyleri gelişen yapılar olarak değerlendirin

Pratik kural:

- yetenek kayıt API’leri hedeflenen yöndür
- geçiş sürecinde, eski kancalar harici plugin’ler için kesintisizliğin en güvenli yoludur
- dışa aktarılan yardımcı alt yolların hepsi eşdeğer değildir; tesadüfi yardımcı dışa aktarımlarını değil,
  dar ve belgelenmiş sözleşmeyi tercih edin

### Plugin biçimleri

OpenClaw, yüklenen her plugin’i gerçek
kayıt davranışına göre bir biçime ayırır (yalnızca statik meta verilere göre değil):

- **plain-capability** -- tam olarak bir yetenek türü kaydeder (örneğin,
  `mistral` gibi yalnızca sağlayıcı olan bir plugin)
- **hybrid-capability** -- birden fazla yetenek türü kaydeder (örneğin
  `openai`, metin çıkarımı, konuşma, medya anlama ve görsel
  oluşturmayı sahiplenir)
- **hook-only** -- yalnızca kancalar kaydeder (türlü veya özel), yetenek,
  araç, komut ya da servis kaydetmez
- **non-capability** -- yetenek olmadan araçlar, komutlar, servisler veya rotalar kaydeder

Bir plugin’in biçimini ve yetenek
dökümünü görmek için `openclaw plugins inspect <id>` komutunu kullanın. Ayrıntılar için [CLI başvurusu](/cli/plugins#inspect) sayfasına bakın.

### Eski kancalar

`before_agent_start` kancası, yalnızca-kanca plugin’leri için bir uyumluluk yolu olarak desteklenmeye devam eder. Eski gerçek dünya plugin’leri hâlâ buna bağımlıdır.

Yön:

- çalışır durumda tutun
- eski olarak belgelendirin
- model/sağlayıcı geçersiz kılma işleri için `before_model_resolve` kullanmayı tercih edin
- istem değiştirme işleri için `before_prompt_build` kullanmayı tercih edin
- yalnızca gerçek kullanım azaldığında ve fixture kapsamı geçiş güvenliğini kanıtladığında kaldırın

### Uyumluluk sinyalleri

`openclaw doctor` veya `openclaw plugins inspect <id>` komutunu çalıştırdığınızda,
şu etiketlerden birini görebilirsiniz:

| Sinyal                     | Anlamı                                                       |
| -------------------------- | ------------------------------------------------------------ |
| **config valid**           | Yapılandırma sorunsuz ayrıştırılır ve plugin’ler çözülür     |
| **compatibility advisory** | Plugin desteklenen ancak daha eski bir desen kullanıyor (ör. `hook-only`) |
| **legacy warning**         | Plugin, kullanımdan kaldırılmış olan `before_agent_start` kullanıyor |
| **hard error**             | Yapılandırma geçersiz veya plugin yüklenemedi                |

Ne `hook-only` ne de `before_agent_start` bugün plugin’inizi bozmaz --
`hook-only` bir tavsiye niteliğindedir ve `before_agent_start` yalnızca uyarı üretir. Bu
sinyaller `openclaw status --all` ve `openclaw plugins doctor` içinde de görünür.

## Mimariye genel bakış

OpenClaw’ın plugin sistemi dört katmana sahiptir:

1. **Manifest + keşif**
   OpenClaw, yapılandırılmış yollardan, çalışma alanı köklerinden,
   genel uzantı köklerinden ve paketlenmiş uzantılardan aday plugin’leri bulur.
   Keşif önce yerel `openclaw.plugin.json` manifestlerini ve desteklenen paket manifestlerini okur.
2. **Etkinleştirme + doğrulama**
   Çekirdek, keşfedilen bir plugin’in etkin, devre dışı, engellenmiş
   veya bellek gibi özel bir yuva için seçilmiş olup olmadığına karar verir.
3. **Çalışma zamanı yükleme**
   Yerel OpenClaw plugin’leri jiti aracılığıyla süreç içinde yüklenir ve
   yetenekleri merkezi bir kayıt defterine kaydeder. Uyumlu paketler, çalışma zamanı kodu içe aktarılmadan
   kayıt defteri kayıtlarına normalize edilir.
4. **Yüzey tüketimi**
   OpenClaw’ın geri kalanı, araçları, kanalları, sağlayıcı
   kurulumunu, kancaları, HTTP rotalarını, CLI komutlarını ve servisleri sunmak için kayıt defterini okur.

Özellikle plugin CLI için, kök komut keşfi iki aşamada bölünür:

- ayrıştırma zamanı meta verisi `registerCli(..., { descriptors: [...] })` üzerinden gelir
- gerçek plugin CLI modülü tembel kalabilir ve ilk çağrıda kaydolabilir

Bu, plugin’e ait CLI kodunu plugin’in içinde tutarken OpenClaw’ın
ayrıştırmadan önce kök komut adlarını ayırmasına olanak tanır.

Önemli tasarım sınırı:

- keşif + yapılandırma doğrulaması, plugin kodunu çalıştırmadan
  **manifest/şema meta verilerinden** çalışabilmelidir
- yerel çalışma zamanı davranışı, plugin modülünün `register(api)` yolundan gelir

Bu ayrım, OpenClaw’ın yapılandırmayı doğrulamasına, eksik/devre dışı plugin’leri açıklamasına ve
tam çalışma zamanı etkinleşmeden önce UI/şema ipuçları oluşturmasına olanak tanır.

### Kanal plugin’leri ve paylaşılan message aracı

Kanal plugin’lerinin, normal sohbet eylemleri için ayrı bir gönder/düzenle/tepki aracı kaydetmesi gerekmez. OpenClaw, çekirdekte tek bir paylaşılan `message` aracı tutar ve kanal plugin’leri bunun arkasındaki kanala özgü keşif ve yürütmeyi sahiplenir.

Mevcut sınır şöyledir:

- çekirdek, paylaşılan `message` araç ana makinesini, istem kablolamasını, oturum/iş parçacığı
  kayıtlarını ve yürütme sevkini sahiplenir
- kanal plugin’leri kapsamlı eylem keşfini, yetenek keşfini ve
  kanala özgü tüm şema parçalarını sahiplenir
- kanal plugin’leri, konuşma kimliklerinin iş parçacığı kimliklerini nasıl kodladığı veya üst konuşmalardan nasıl miras aldığı gibi
  sağlayıcıya özgü oturum konuşma dil bilgisini sahiplenir
- kanal plugin’leri son eylemi kendi eylem bağdaştırıcıları üzerinden yürütür

Kanal plugin’leri için SDK yüzeyi
`ChannelMessageActionAdapter.describeMessageTool(...)` şeklindedir. Bu birleşik keşif
çağrısı, bir plugin’in görünür eylemlerini, yeteneklerini ve şema katkılarını
birlikte döndürmesine olanak tanır; böylece bu parçalar birbirinden kopmaz.

Çekirdek, çalışma zamanı kapsamını bu keşif adımına aktarır. Önemli alanlar şunlardır:

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- güvenilir gelen `requesterSenderId`

Bu, bağlama duyarlı plugin’ler için önemlidir. Bir kanal,
çekirdekteki `message` aracında kanala özgü dallanmaları sabit kodlamadan,
etkin hesaba, geçerli odaya/iş parçacığına/mesaja veya
güvenilir istek sahibi kimliğine göre mesaj eylemlerini gizleyebilir ya da gösterebilir.

Bu nedenle gömülü çalıştırıcı yönlendirme değişiklikleri hâlâ plugin işidir: çalıştırıcı,
paylaşılan `message` aracının geçerli tur için doğru kanala ait
yüzeyi göstermesi amacıyla mevcut sohbet/oturum kimliğini plugin
keşif sınırına iletmekten sorumludur.

Kanala ait yürütme yardımcıları için, paketlenmiş plugin’ler yürütme
çalışma zamanını kendi uzantı modülleri içinde tutmalıdır. Çekirdek artık `src/agents/tools` altında
Discord, Slack, Telegram veya WhatsApp mesaj-eylemi çalışma zamanlarını sahiplenmez.
Ayrı `plugin-sdk/*-action-runtime` alt yolları yayımlamıyoruz ve paketlenmiş
plugin’ler kendi yerel çalışma zamanı kodlarını doğrudan
uzantıya ait modüllerinden içe aktarmalıdır.

Aynı sınır, genel olarak sağlayıcı adlı SDK yüzeyleri için de geçerlidir: çekirdek,
Slack, Discord, Signal, WhatsApp veya benzeri uzantılar için kanala özgü kolaylık paketlerini içe aktarmamalıdır.
Çekirdeğin bir davranışa ihtiyacı varsa ya paketlenmiş plugin’in kendi `api.ts` / `runtime-api.ts`
paketini tüketmeli ya da ihtiyacı paylaşılan SDK’da dar bir genel yeteneğe dönüştürmelidir.

Özellikle anketler için iki yürütme yolu vardır:

- `outbound.sendPoll`, ortak anket modeline uyan kanallar için paylaşılan temel yoldur
- `actions.handleAction("poll")`, kanala özgü anket anlambilimi veya ek anket parametreleri için tercih edilen yoldur

Çekirdek artık, plugin’e ait anket gönderimi eylemi reddettikten sonra
paylaşılan anket ayrıştırmasını erteler; böylece plugin’e ait anket işleyicileri,
önce genel anket ayrıştırıcısı tarafından engellenmeden kanala özgü anket alanlarını kabul edebilir.

Tam başlangıç dizisi için [Yükleme işlem hattı](#load-pipeline) bölümüne bakın.

## Yetenek sahipliği modeli

OpenClaw, yerel bir plugin’i ilgisiz entegrasyonların karışık bir topluluğu olarak değil,
bir **şirketin** veya bir **özelliğin** sahiplik sınırı olarak ele alır.

Bu şu anlama gelir:

- bir şirket plugin’i genellikle o şirketin OpenClaw’a dönük tüm
  yüzeylerine sahip olmalıdır
- bir özellik plugin’i genellikle sunduğu özelliğin tam yüzeyine sahip olmalıdır
- kanallar, sağlayıcı davranışını geçici olarak yeniden uygulamak yerine paylaşılan çekirdek yetenekleri tüketmelidir

Örnekler:

- paketlenmiş `openai` plugin’i, OpenAI model-sağlayıcı davranışını ve OpenAI
  konuşma + gerçek zamanlı ses + medya anlama + görsel oluşturma davranışını sahiplenir
- paketlenmiş `elevenlabs` plugin’i ElevenLabs konuşma davranışını sahiplenir
- paketlenmiş `microsoft` plugin’i Microsoft konuşma davranışını sahiplenir
- paketlenmiş `google` plugin’i, Google model-sağlayıcı davranışının yanı sıra Google
  medya anlama + görsel oluşturma + web arama davranışını sahiplenir
- paketlenmiş `firecrawl` plugin’i Firecrawl web-getirme davranışını sahiplenir
- paketlenmiş `minimax`, `mistral`, `moonshot` ve `zai` plugin’leri kendi
  medya anlama arka uçlarına sahiptir
- paketlenmiş `qwen` plugin’i, Qwen metin-sağlayıcı davranışının yanı sıra
  medya anlama ve video oluşturma davranışını sahiplenir
- `voice-call` plugin’i bir özellik plugin’idir: çağrı aktarımını, araçları,
  CLI’yi, rotaları ve Twilio medya-akışı köprüsünü sahiplenir, ancak satıcı plugin’lerini doğrudan
  içe aktarmak yerine paylaşılan konuşma ile gerçek zamanlı yazıya dökme ve gerçek zamanlı ses yeteneklerini tüketir

Hedeflenen son durum şudur:

- OpenAI, metin modellerini, konuşmayı, görselleri ve gelecekte videoyu kapsasa bile tek bir plugin içinde yer alır
- başka bir satıcı da kendi yüzey alanı için aynısını yapabilir
- kanallar, sağlayıcının hangi satıcı plugin’ine ait olduğunu umursamaz; çekirdek tarafından sunulan
  paylaşılan yetenek sözleşmesini tüketirler

Temel ayrım şudur:

- **plugin** = sahiplik sınırı
- **capability** = birden çok plugin’in uygulayabildiği veya tüketebildiği çekirdek sözleşmesi

Dolayısıyla OpenClaw, video gibi yeni bir alan eklediğinde ilk soru
“hangi sağlayıcı video işleyişini sabit kodlamalı?” değildir. İlk soru “çekirdekteki
video yetenek sözleşmesi nedir?” olmalıdır. Bu sözleşme var olduğunda, satıcı plugin’leri
ona kayıt olabilir ve kanal/özellik plugin’leri bunu tüketebilir.

Yetenek henüz mevcut değilse, doğru adım genellikle şudur:

1. eksik yeteneği çekirdekte tanımlamak
2. bunu plugin API’si/çalışma zamanı üzerinden türlenmiş şekilde sunmak
3. kanalları/özellikleri bu yeteneğe göre bağlamak
4. satıcı plugin’lerinin uygulamaları kaydetmesine izin vermek

Bu yaklaşım, sahipliği açık tutarken çekirdek davranışının
tek bir satıcıya veya bir defalık plugin’e özgü bir kod yoluna bağımlı olmasını önler.

### Yetenek katmanlaması

Kodun nereye ait olduğuna karar verirken şu zihinsel modeli kullanın:

- **çekirdek yetenek katmanı**: paylaşılan orkestrasyon, politika, geri dönüş, yapılandırma
  birleştirme kuralları, teslim semantiği ve türlenmiş sözleşmeler
- **satıcı plugin katmanı**: satıcıya özgü API’ler, kimlik doğrulama, model katalogları, konuşma
  sentezi, görsel üretimi, gelecekteki video arka uçları, kullanım uç noktaları
- **kanal/özellik plugin katmanı**: Slack/Discord/voice-call/vb. entegrasyonu;
  çekirdek yetenekleri tüketir ve bunları bir yüzeyde sunar

Örneğin TTS şu yapıyı izler:

- çekirdek, yanıt zamanındaki TTS politikasını, geri dönüş sırasını, tercihleri ve kanal teslimini sahiplenir
- `openai`, `elevenlabs` ve `microsoft` sentez uygulamalarını sahiplenir
- `voice-call`, telefon TTS çalışma zamanı yardımcısını tüketir

Aynı desen gelecekteki yetenekler için de tercih edilmelidir.

### Çok yetenekli şirket plugin’i örneği

Bir şirket plugin’i dışarıdan bakıldığında bütünlüklü hissettirmelidir. OpenClaw’da
modeller, konuşma, gerçek zamanlı yazıya dökme, gerçek zamanlı ses, medya
anlama, görsel oluşturma, video oluşturma, web getirme ve web arama için paylaşılan
sözleşmeler varsa, bir satıcı tüm yüzeylerine tek bir yerden sahip olabilir:

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

Önemli olan tam yardımcı adları değildir. Önemli olan yapı şeklidir:

- tek bir plugin satıcı yüzeyine sahip olur
- çekirdek yine de yetenek sözleşmelerine sahip olur
- kanallar ve özellik plugin’leri satıcı kodunu değil, `api.runtime.*` yardımcılarını tüketir
- sözleşme testleri, plugin’in sahip olduğunu iddia ettiği yetenekleri kaydettiğini
  doğrulayabilir

### Yetenek örneği: video anlama

OpenClaw, görsel/ses/video anlamayı zaten tek bir paylaşılan
yetenek olarak ele alır. Aynı sahiplik modeli burada da geçerlidir:

1. çekirdek medya-anlama sözleşmesini tanımlar
2. satıcı plugin’leri uygun olduğu durumlarda `describeImage`, `transcribeAudio` ve
   `describeVideo` kaydeder
3. kanal ve özellik plugin’leri doğrudan satıcı koduna bağlanmak yerine
   paylaşılan çekirdek davranışını tüketir

Bu, tek bir sağlayıcının video varsayımlarının çekirdeğe gömülmesini önler. Plugin,
satıcı yüzeyine sahip olur; çekirdek ise yetenek sözleşmesine ve geri dönüş davranışına sahip olur.

Video oluşturma zaten aynı sırayı kullanır: çekirdek, türlenmiş
yetenek sözleşmesine ve çalışma zamanı yardımcısına sahiptir ve satıcı plugin’leri
`api.registerVideoGenerationProvider(...)` uygulamalarını buna karşı kaydeder.

Somut bir devreye alma denetim listesine mi ihtiyacınız var? Bkz.
[Capability Cookbook](/tr/plugins/architecture).

## Sözleşmeler ve zorunlu uygulama

Plugin API yüzeyi, kasıtlı olarak türlenmiştir ve
`OpenClawPluginApi` içinde merkezileştirilmiştir. Bu sözleşme, desteklenen kayıt noktalarını ve
bir plugin’in güvenebileceği çalışma zamanı yardımcılarını tanımlar.

Bunun önemi:

- plugin yazarları tek bir kararlı iç standart elde eder
- çekirdek, aynı sağlayıcı kimliğini iki plugin’in kaydetmesi gibi
  yinelenen sahiplikleri reddedebilir
- başlangıç, hatalı kayıtlar için uygulanabilir tanı bilgileri gösterebilir
- sözleşme testleri, paketlenmiş plugin sahipliğini zorunlu kılabilir ve sessiz kaymayı önleyebilir

İki zorunlu uygulama katmanı vardır:

1. **çalışma zamanı kayıt zorunluluğu**
   Plugin kayıt defteri, plugin’ler yüklenirken kayıtları doğrular. Örnekler:
   yinelenen sağlayıcı kimlikleri, yinelenen konuşma sağlayıcısı kimlikleri ve hatalı
   kayıtlar, tanımsız davranış yerine plugin tanı bilgileri üretir.
2. **sözleşme testleri**
   Paketlenmiş plugin’ler, test çalıştırmaları sırasında sözleşme kayıt defterlerinde yakalanır; böylece
   OpenClaw sahipliği açıkça doğrulayabilir. Bugün bu, model
   sağlayıcıları, konuşma sağlayıcıları, web arama sağlayıcıları ve paketlenmiş kayıt
   sahipliği için kullanılmaktadır.

Bunun pratik etkisi, OpenClaw’ın baştan itibaren hangi plugin’in hangi
yüzeye sahip olduğunu bilmesidir. Bu sayede çekirdek ve kanallar sorunsuz biçimde birleşebilir;
çünkü sahiplik örtük değil, bildirilmiş, türlenmiş ve test edilebilirdir.

### Bir sözleşmede ne bulunmalıdır

İyi plugin sözleşmeleri şunlardır:

- türlenmiş
- küçük
- yeteneğe özgü
- çekirdeğe ait
- birden çok plugin tarafından yeniden kullanılabilir
- satıcı bilgisi olmadan kanallar/özellikler tarafından tüketilebilir

Kötü plugin sözleşmeleri şunlardır:

- çekirdekte gizlenmiş satıcıya özgü politika
- kayıt defterini baypas eden tek seferlik plugin kaçış kapıları
- kanal kodunun doğrudan satıcı uygulamasına ulaşması
- `OpenClawPluginApi` veya
  `api.runtime` parçası olmayan geçici çalışma zamanı nesneleri

Emin değilseniz soyutlama düzeyini yükseltin: önce yeteneği tanımlayın, sonra
plugin’lerin buna bağlanmasına izin verin.

## Yürütme modeli

Yerel OpenClaw plugin’leri, Gateway ile **aynı süreç içinde** çalışır. Yalıtılmış
değillerdir. Yüklenmiş bir yerel plugin, çekirdek kodla aynı süreç düzeyinde güven sınırına sahiptir.

Sonuçları:

- bir yerel plugin araçlar, ağ işleyicileri, kancalar ve servisler kaydedebilir
- bir yerel plugin hatası gateway’i çökertilebilir veya kararsızlaştırabilir
- kötü amaçlı bir yerel plugin, OpenClaw süreci içinde keyfi kod yürütmeye eşdeğerdir

Uyumlu paketler varsayılan olarak daha güvenlidir; çünkü OpenClaw şu anda bunları
meta veri/içerik paketleri olarak ele alır. Güncel sürümlerde bu çoğunlukla
paketlenmiş Skills anlamına gelir.

Paketlenmemiş plugin’ler için izin listelerini ve açık kurulum/yükleme yollarını kullanın. Çalışma alanı plugin’lerini
üretim varsayılanları değil, geliştirme zamanı kodu olarak değerlendirin.

Paketlenmiş çalışma alanı paket adları için, plugin kimliğini npm
adına bağlayın: varsayılan olarak `@openclaw/<id>`, ya da paket
kasıtlı olarak daha dar bir plugin rolü sunuyorsa `-provider`, `-plugin`, `-speech`, `-sandbox` veya
`-media-understanding` gibi onaylı türlenmiş sonekler.

Önemli güven notu:

- `plugins.allow`, **kaynak kökenine** değil **plugin kimliklerine** güvenir.
- Paketlenmiş bir plugin ile aynı kimliğe sahip bir çalışma alanı plugin’i, bu çalışma alanı plugin’i etkinleştirildiğinde/izin listesine alındığında
  paketlenmiş kopyayı kasıtlı olarak gölgeler.
- Bu normaldir ve yerel geliştirme, yama testi ve hızlı düzeltmeler için faydalıdır.

## Dışa aktarma sınırı

OpenClaw, uygulama kolaylıklarını değil, yetenekleri dışa aktarır.

Yetenek kaydını genel tutun. Sözleşme dışı yardımcı dışa aktarımları azaltın:

- paketlenmiş plugin’e özgü yardımcı alt yollar
- genel API olması amaçlanmayan çalışma zamanı tesisat alt yolları
- satıcıya özgü kolaylık yardımcıları
- uygulama ayrıntısı olan kurulum/ilk yapılandırma yardımcıları

Bazı paketlenmiş plugin yardımcı alt yolları, uyumluluk ve paketlenmiş plugin bakımı için oluşturulmuş SDK dışa aktarma
eşlemesinde hâlâ kalmaktadır. Güncel örnekler arasında
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` ve birkaç `plugin-sdk/matrix*` yüzeyi bulunur. Bunları,
yeni üçüncü taraf plugin’ler için önerilen SDK deseni olarak değil, ayrılmış
uygulama ayrıntısı dışa aktarımları olarak değerlendirin.

## Yükleme işlem hattı

Başlangıçta OpenClaw kabaca şunları yapar:

1. aday plugin köklerini keşfeder
2. yerel veya uyumlu paket manifestlerini ve paket meta verilerini okur
3. güvenli olmayan adayları reddeder
4. plugin yapılandırmasını normalize eder (`plugins.enabled`, `allow`, `deny`, `entries`,
   `slots`, `load.paths`)
5. her aday için etkinleştirme durumuna karar verir
6. etkin yerel modülleri jiti aracılığıyla yükler
7. yerel `register(api)` (veya `activate(api)` — eski bir takma ad) kancalarını çağırır ve kayıtları plugin kayıt defterinde toplar
8. kayıt defterini komut/çalışma zamanı yüzeylerine sunar

<Note>
`activate`, `register` için eski bir takma addır — yükleyici hangisi mevcutsa onu çözer (`def.register ?? def.activate`) ve aynı noktada çağırır. Tüm paketlenmiş plugin’ler `register` kullanır; yeni plugin’ler için `register` tercih edin.
</Note>

Güvenlik kapıları **çalışma zamanı yürütmesinden önce** devreye girer. Giriş plugin kökünden çıkıyorsa,
yol dünya tarafından yazılabilirse veya paketlenmemiş plugin’ler için yol
sahipliği şüpheli görünüyorsa adaylar engellenir.

### Önce manifest davranışı

Manifest, kontrol düzlemi için doğruluk kaynağıdır. OpenClaw bunu şunlar için kullanır:

- plugin’i tanımlamak
- bildirilen kanalları/Skills/yapılandırma şemasını veya paket yeteneklerini keşfetmek
- `plugins.entries.<id>.config` değerini doğrulamak
- Control UI etiketlerini/yer tutucularını zenginleştirmek
- kurulum/katalog meta verilerini göstermek
- plugin çalışma zamanını yüklemeden düşük maliyetli etkinleştirme ve kurulum tanımlayıcılarını korumak

Yerel plugin’lerde çalışma zamanı modülü veri düzlemi parçasıdır. Kancalar, araçlar, komutlar veya sağlayıcı akışları gibi
gerçek davranışları kaydeder.

İsteğe bağlı manifest `activation` ve `setup` blokları kontrol düzleminde kalır.
Bunlar etkinleştirme planlaması ve kurulum keşfi için yalnızca meta veri tanımlayıcılarıdır;
çalışma zamanı kaydının, `register(...)` işlevinin veya `setupEntry` işlevinin yerine geçmezler.

### Yükleyicinin önbelleğe aldığı şeyler

OpenClaw, süreç içinde kısa ömürlü önbellekleri şunlar için tutar:

- keşif sonuçları
- manifest kayıt defteri verileri
- yüklenmiş plugin kayıt defterleri

Bu önbellekler ani başlangıç yükünü ve tekrarlanan komut ek yükünü azaltır. Bunları
kalıcılık olarak değil, kısa ömürlü performans önbellekleri olarak düşünmek güvenlidir.

Performans notu:

- Bu önbellekleri devre dışı bırakmak için `OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` veya
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1` ayarlayın.
- Önbellek pencerelerini `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` ve
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS` ile ayarlayın.

## Kayıt defteri modeli

Yüklenmiş plugin’ler rastgele çekirdek genel durumlarını doğrudan değiştirmez. Merkezi bir
plugin kayıt defterine kayıt olurlar.

Kayıt defteri şunları izler:

- plugin kayıtları (kimlik, kaynak, köken, durum, tanı bilgileri)
- araçlar
- eski kancalar ve türlenmiş kancalar
- kanallar
- sağlayıcılar
- gateway RPC işleyicileri
- HTTP rotaları
- CLI kaydedicileri
- arka plan servisleri
- plugin’e ait komutlar

Daha sonra çekirdek özellikler, plugin modülleriyle doğrudan konuşmak yerine bu kayıt defterinden okur.
Bu, yüklemeyi tek yönlü tutar:

- plugin modülü -> kayıt defterine kayıt
- çekirdek çalışma zamanı -> kayıt defterinden tüketim

Bu ayrım bakım yapılabilirlik için önemlidir. Bu, çoğu çekirdek yüzeyin yalnızca tek bir
entegrasyon noktasına ihtiyaç duyması anlamına gelir: “kayıt defterini oku”;
“her plugin modülü için özel durum yaz” değil.

## Konuşma bağlama geri çağrıları

Bir konuşmayı bağlayan plugin’ler, bir onay çözümlendiğinde tepki verebilir.

Bağlama isteği onaylandıktan veya reddedildikten sonra bir geri çağrı almak için
`api.onConversationBindingResolved(...)` kullanın:

```ts
export default {
  id: "my-plugin",
  register(api) {
    api.onConversationBindingResolved(async (event) => {
      if (event.status === "approved") {
        // Artık bu plugin + conversation için bir bağlama var.
        console.log(event.binding?.conversationId);
        return;
      }

      // İstek reddedildi; yerel bekleyen durumu temizleyin.
      console.log(event.request.conversation.conversationId);
    });
  },
};
```

Geri çağrı yükü alanları:

- `status`: `"approved"` veya `"denied"`
- `decision`: `"allow-once"`, `"allow-always"` veya `"deny"`
- `binding`: onaylanan istekler için çözümlenmiş bağlama
- `request`: özgün istek özeti, ayırma ipucu, gönderen kimliği ve
  konuşma meta verileri

Bu geri çağrı yalnızca bildirim amaçlıdır. Bir konuşmayı kimin bağlayabileceğini değiştirmez
ve çekirdek onay işleme tamamlandıktan sonra çalışır.

## Sağlayıcı çalışma zamanı kancaları

Sağlayıcı plugin’lerinin artık iki katmanı vardır:

- manifest meta verileri: çalışma zamanı yüklenmeden önce ucuz sağlayıcı ortam kimlik doğrulama araması için `providerAuthEnvVars`,
  kimlik doğrulamayı paylaşan sağlayıcı varyantları için `providerAuthAliases`,
  çalışma zamanı yüklenmeden önce ucuz kanal ortamı/kurulum araması için `channelEnvVars`,
  ayrıca çalışma zamanı yüklenmeden önce ucuz ilk kurulum/kimlik doğrulama seçimi etiketleri ve
  CLI bayrak meta verileri için `providerAuthChoices`
- yapılandırma zamanı kancaları: `catalog` / eski `discovery` ile `applyConfigDefaults`
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

OpenClaw hâlâ genel ajan döngüsüne, yük devrine, döküm işleme sürecine ve
araç politikasına sahiptir. Bu kancalar, tam bir özel çıkarım aktarımına ihtiyaç
duymadan sağlayıcıya özgü davranış için uzantı yüzeyidir.

Sağlayıcının, genel kimlik doğrulama/durum/model seçici yollarının
plugin çalışma zamanını yüklemeden görebilmesi gereken ortam tabanlı kimlik bilgileri varsa
manifest `providerAuthEnvVars` kullanın. Bir sağlayıcı kimliği başka bir sağlayıcı kimliğinin
ortam değişkenlerini, kimlik doğrulama profillerini, yapılandırma destekli kimlik doğrulamayı ve API anahtarı ilk kurulum seçimini yeniden kullanacaksa
manifest `providerAuthAliases` kullanın. İlk kurulum/kimlik doğrulama seçimi
CLI yüzeylerinin, sağlayıcının seçim kimliğini, grup etiketlerini ve basit
tek bayraklı kimlik doğrulama bağlantısını sağlayıcı çalışma zamanını yüklemeden bilmesi gerektiğinde
manifest `providerAuthChoices` kullanın. Sağlayıcı çalışma zamanı
`envVars` alanını, ilk kurulum etiketleri veya OAuth
istemci kimliği/istemci sırrı kurulum değişkenleri gibi operatöre dönük ipuçları için koruyun.

Bir kanalın, genel kabuk-ortamı geri dönüşü, yapılandırma/durum denetimleri veya kurulum istemlerinin
kanal çalışma zamanını yüklemeden görmesi gereken ortam güdümlü kimlik doğrulaması veya kurulumu varsa
manifest `channelEnvVars` kullanın.

### Kanca sırası ve kullanım

Model/sağlayıcı plugin’leri için OpenClaw, kancaları kabaca şu sırayla çağırır.
“Ne zaman kullanılır” sütunu hızlı karar kılavuzudur.

| #   | Kanca                             | Ne yapar                                                                                                       | Ne zaman kullanılır                                                                                                                         |
| --- | --------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `catalog`                         | `models.json` oluşturulurken sağlayıcı yapılandırmasını `models.providers` içine yayımlar                     | Sağlayıcının bir kataloğa veya temel URL varsayılanlarına sahip olduğu durumlarda                                                           |
| 2   | `applyConfigDefaults`             | Yapılandırma somutlaştırması sırasında sağlayıcıya ait genel yapılandırma varsayılanlarını uygular            | Varsayılanlar kimlik doğrulama moduna, ortama veya sağlayıcı model ailesi anlambilimine bağlıysa                                           |
| --  | _(yerleşik model araması)_        | OpenClaw önce normal kayıt defteri/katalog yolunu dener                                                       | _(bir plugin kancası değildir)_                                                                                                             |
| 3   | `normalizeModelId`                | Aramadan önce eski veya önizleme model kimliği takma adlarını normalleştirir                                  | Sağlayıcı, kanonik model çözümlemesinden önce takma ad temizliğine sahipse                                                                  |
| 4   | `normalizeTransport`              | Genel model birleştirmesinden önce sağlayıcı ailesine ait `api` / `baseUrl` değerlerini normalleştirir       | Sağlayıcı, aynı aktarım ailesindeki özel sağlayıcı kimlikleri için aktarım temizliğini sahipleniyorsa                                      |
| 5   | `normalizeConfig`                 | Çalışma zamanı/sağlayıcı çözümlemesinden önce `models.providers.<id>` değerini normalleştirir                 | Sağlayıcının plugin ile birlikte yaşaması gereken yapılandırma temizliğine ihtiyacı varsa; paketlenmiş Google ailesi yardımcıları da desteklenen Google yapılandırma girdilerini arka planda destekler |
| 6   | `applyNativeStreamingUsageCompat` | Yerel akış kullanımı uyumluluk yeniden yazımlarını yapılandırma sağlayıcılarına uygular                       | Sağlayıcının uç nokta güdümlü yerel akış kullanım meta verisi düzeltmelerine ihtiyacı varsa                                                |
| 7   | `resolveConfigApiKey`             | Çalışma zamanı kimlik doğrulaması yüklenmeden önce yapılandırma sağlayıcıları için ortam işaretleyicili kimlik doğrulamayı çözümler | Sağlayıcının sağlayıcıya ait ortam işaretleyicili API anahtarı çözümlemesine ihtiyacı varsa; `amazon-bedrock` için de burada yerleşik bir AWS ortam işaretleyici çözümleyicisi bulunur |
| 8   | `resolveSyntheticAuth`            | Düz metni kalıcılaştırmadan yerel/kendi kendine barındırılan veya yapılandırma destekli kimlik doğrulamayı görünür kılar | Sağlayıcı sentetik/yerel bir kimlik bilgisi işaretleyicisiyle çalışabiliyorsa                                                              |
| 9   | `resolveExternalAuthProfiles`     | Sağlayıcıya ait harici kimlik doğrulama profillerini bindirir; varsayılan `persistence`, CLI/uygulamaya ait kimlik bilgileri için `runtime-only` olur | Sağlayıcı, kopyalanmış yenileme belirteçlerini kalıcılaştırmadan harici kimlik doğrulama kimlik bilgilerini yeniden kullanıyorsa          |
| 10  | `shouldDeferSyntheticProfileAuth` | Kaydedilmiş sentetik profil yer tutucularını ortam/yapılandırma destekli kimlik doğrulamanın arkasına indirir | Sağlayıcı, öncelik kazanmaması gereken sentetik yer tutucu profiller saklıyorsa                                                             |
| 11  | `resolveDynamicModel`             | Henüz yerel kayıt defterinde olmayan sağlayıcıya ait model kimlikleri için eşzamanlı geri dönüş sağlar        | Sağlayıcı, yukarı akıştan gelen keyfi model kimliklerini kabul ediyorsa                                                                     |
| 12  | `prepareDynamicModel`             | Zaman uyumsuz hazırlık yapar, ardından `resolveDynamicModel` yeniden çalışır                                  | Sağlayıcının bilinmeyen kimlikleri çözümlemeden önce ağ meta verisine ihtiyacı varsa                                                        |
| 13  | `normalizeResolvedModel`          | Gömülü çalıştırıcı çözümlenmiş modeli kullanmadan önce son yeniden yazımı yapar                              | Sağlayıcının aktarım yeniden yazımlarına ihtiyacı varsa ancak yine de çekirdek bir aktarım kullanıyorsa                                    |
| 14  | `contributeResolvedModelCompat`   | Başka bir uyumlu aktarım arkasındaki satıcı modelleri için uyumluluk bayrakları katkısı sağlar                | Sağlayıcı, sağlayıcıyı devralmadan ara sunucu aktarımlarındaki kendi modellerini tanıyorsa                                                  |
| 15  | `capabilities`                    | Paylaşılan çekirdek mantığı tarafından kullanılan, sağlayıcıya ait döküm/araç meta verileri                  | Sağlayıcının döküm/sağlayıcı ailesi tuhaflıklarına ihtiyacı varsa                                                                           |
| 16  | `normalizeToolSchemas`            | Gömülü çalıştırıcı bunları görmeden önce araç şemalarını normalleştirir                                        | Sağlayıcının aktarım ailesine ait şema temizliğine ihtiyacı varsa                                                                           |
| 17  | `inspectToolSchemas`              | Normalleştirmeden sonra sağlayıcıya ait şema tanılarını görünür kılar                                         | Sağlayıcı, çekirdeğe sağlayıcıya özgü kurallar öğretmeden anahtar sözcük uyarıları istiyorsa                                                |
| 18  | `resolveReasoningOutputMode`      | Yerel ile etiketli akıl yürütme çıktısı sözleşmesi arasında seçim yapar                                        | Sağlayıcının yerel alanlar yerine etiketli akıl yürütme/nihai çıktı istemesi durumunda                                                     |
| 19  | `prepareExtraParams`              | Genel akış seçenek sarmalayıcılarından önce istek parametresi normalleştirmesi yapar                          | Sağlayıcının varsayılan istek parametrelerine veya sağlayıcı başına parametre temizliğine ihtiyacı varsa                                   |
| 20  | `createStreamFn`                  | Normal akış yolunu özel bir aktarımla tamamen değiştirir                                                       | Sağlayıcının yalnızca bir sarmalayıcıya değil, özel bir kablo protokolüne ihtiyacı varsa                                                   |
| 21  | `wrapStreamFn`                    | Genel sarmalayıcılar uygulandıktan sonra akışı sarar                                                           | Sağlayıcının özel bir aktarım olmadan istek üst bilgileri/gövdesi/model uyumluluğu sarmalayıcılarına ihtiyacı varsa                        |
| 22  | `resolveTransportTurnState`       | Yerel tur başına aktarım üst bilgilerini veya meta veriyi ekler                                               | Sağlayıcının genel aktarımların sağlayıcıya özgü tur kimliğini göndermesini istemesi durumunda                                             |
| 23  | `resolveWebSocketSessionPolicy`   | Yerel WebSocket üst bilgilerini veya oturum soğuma politikasını ekler                                         | Sağlayıcının genel WS aktarımlarını oturum üst bilgileri veya geri dönüş politikası için ayarlamak istemesi durumunda                     |
| 24  | `formatApiKey`                    | Kimlik doğrulama profili biçimlendiricisi: kaydedilmiş profil, çalışma zamanındaki `apiKey` dizesine dönüşür | Sağlayıcı ek kimlik doğrulama meta verisi saklıyorsa ve özel bir çalışma zamanı belirteci biçimine ihtiyaç duyuyorsa                      |
| 25  | `refreshOAuth`                    | Özel yenileme uç noktaları veya yenileme-hatası politikası için OAuth yenilemesini geçersiz kılar             | Sağlayıcı paylaşılan `pi-ai` yenileyicilerine uymuyorsa                                                                                     |
| 26  | `buildAuthDoctorHint`             | OAuth yenilemesi başarısız olduğunda eklenen onarım ipucu                                                      | Sağlayıcının yenileme hatasından sonra sağlayıcıya ait kimlik doğrulama onarım yönlendirmesine ihtiyacı varsa                             |
| 27  | `matchesContextOverflowError`     | Sağlayıcıya ait bağlam penceresi taşması eşleyicisi                                                            | Sağlayıcının genel sezgilerin kaçıracağı ham taşma hataları varsa                                                                           |
| 28  | `classifyFailoverReason`          | Sağlayıcıya ait yük devri nedeni sınıflandırması                                                               | Sağlayıcının ham API/aktarım hatalarını hız sınırı/aşırı yük/vb. nedenlere eşleyebilmesi durumunda                                        |
| 29  | `isCacheTtlEligible`              | Ara sunucu/arka taşıma sağlayıcıları için istem önbelleği politikası                                           | Sağlayıcının ara sunucuya özgü önbellek TTL geçitlemesine ihtiyacı varsa                                                                    |
| 30  | `buildMissingAuthMessage`         | Genel eksik kimlik doğrulama kurtarma iletisinin yerine geçer                                                  | Sağlayıcının sağlayıcıya özgü eksik kimlik doğrulama kurtarma ipucuna ihtiyacı varsa                                                       |
| 31  | `suppressBuiltInModel`            | Eski yukarı akış modelini bastırma ve isteğe bağlı kullanıcıya dönük hata ipucu                               | Sağlayıcının eski yukarı akış satırlarını gizlemesi veya bunları bir satıcı ipucuyla değiştirmesi gerekiyorsa                              |
| 32  | `augmentModelCatalog`             | Keşiften sonra eklenen sentetik/nihai katalog satırları                                                        | Sağlayıcının `models list` ve seçiciler içinde sentetik ileri uyumluluk satırlarına ihtiyacı varsa                                        |
| 33  | `isBinaryThinking`                | İkili düşünme sağlayıcıları için açık/kapalı akıl yürütme geçişi                                                | Sağlayıcı yalnızca ikili düşünme açık/kapalı desteği sunuyorsa                                                                              |
| 34  | `supportsXHighThinking`           | Seçili modeller için `xhigh` akıl yürütme desteği                                                              | Sağlayıcı yalnızca modellerin bir alt kümesinde `xhigh` istiyorsa                                                                           |
| 35  | `resolveDefaultThinkingLevel`     | Belirli bir model ailesi için varsayılan `/think` düzeyi                                                       | Sağlayıcı bir model ailesi için varsayılan `/think` politikasına sahipse                                                                    |
| 36  | `isModernModelRef`                | Canlı profil filtreleri ve smoke seçimi için modern-model eşleyicisi                                           | Sağlayıcı canlı/smoke tercih edilen model eşlemesini sahipleniyorsa                                                                         |
| 37  | `prepareRuntimeAuth`              | Çıkarımdan hemen önce yapılandırılmış bir kimlik bilgisini gerçek çalışma zamanı belirtecine/anahtarına dönüştürür | Sağlayıcının bir belirteç değişimine veya kısa ömürlü istek kimlik bilgisine ihtiyacı varsa                                                |
| 38  | `resolveUsageAuth`                | `/usage` ve ilgili durum yüzeyleri için kullanım/faturalama kimlik bilgilerini çözümler                       | Sağlayıcının özel kullanım/kota belirteci ayrıştırmasına veya farklı bir kullanım kimlik bilgisine ihtiyacı varsa                          |
| 39  | `fetchUsageSnapshot`              | Kimlik doğrulama çözümlendikten sonra sağlayıcıya özgü kullanım/kota anlık görüntülerini getirir ve normalleştirir | Sağlayıcının sağlayıcıya özgü bir kullanım uç noktasına veya yük ayrıştırıcısına ihtiyacı varsa                                           |
| 40  | `createEmbeddingProvider`         | Bellek/arama için sağlayıcıya ait bir embedding bağdaştırıcısı oluşturur                                       | Bellek embedding davranışı sağlayıcı plugin’iyle birlikte bulunmalıdır                                                                      |
| 41  | `buildReplayPolicy`               | Sağlayıcı için döküm işlemeyi denetleyen bir replay politikası döndürür                                        | Sağlayıcının özel döküm politikasına ihtiyacı varsa (örneğin, düşünme bloğu çıkarma)                                                       |
| 42  | `sanitizeReplayHistory`           | Genel döküm temizliğinden sonra replay geçmişini yeniden yazar                                                 | Sağlayıcının paylaşılan sıkıştırma yardımcılarının ötesinde sağlayıcıya özgü replay yeniden yazımlarına ihtiyacı varsa                    |
| 43  | `validateReplayTurns`             | Gömülü çalıştırıcıdan önce son replay turu doğrulaması veya yeniden şekillendirmesi yapar                     | Sağlayıcı aktarımının, genel temizlemeden sonra daha sıkı tur doğrulamasına ihtiyacı varsa                                                 |
| 44  | `onModelSelected`                 | Sağlayıcıya ait seçim sonrası yan etkileri çalıştırır                                                          | Bir model etkin olduğunda sağlayıcının telemetriye veya sağlayıcıya ait duruma ihtiyacı varsa                                              |

`normalizeModelId`, `normalizeTransport` ve `normalizeConfig` önce
eşleşen sağlayıcı plugin’ini denetler, ardından model kimliğini veya aktarımı/yapılandırmayı gerçekten değiştiren biri bulunana kadar
kanca destekli diğer sağlayıcı plugin’lerine düşer. Bu, çağıranın yeniden yazımı hangi
paketlenmiş plugin’in sahiplendiğini bilmesini gerektirmeden takma ad/uyumluluk
sağlayıcı köprülerinin çalışmasını sağlar. Desteklenen bir Google ailesi yapılandırma girdisini
hiçbir sağlayıcı kancası yeniden yazmazsa, paketlenmiş Google yapılandırma normalleştiricisi yine de
bu uyumluluk temizliğini uygular.

Sağlayıcının tamamen özel bir kablo protokolüne veya özel bir istek yürütücüsüne ihtiyacı varsa,
bu farklı bir uzantı sınıfıdır. Bu kancalar, hâlâ OpenClaw’ın normal
çıkarım döngüsü üzerinde çalışan sağlayıcı davranışları içindir.

### Sağlayıcı örneği

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

- Anthropic, Claude 4.6 ileri uyumluluğuna,
  sağlayıcı ailesi ipuçlarına, kimlik doğrulama onarım yönlendirmesine, kullanım uç noktası entegrasyonuna,
  istem önbelleği uygunluğuna, kimlik doğrulama farkında yapılandırma varsayılanlarına, Claude
  varsayılan/uyarlanabilir düşünme politikasına ve
  beta üst bilgileri, `/fast` / `serviceTier` ve `context1m` için Anthropic’e özgü akış şekillendirmesine sahip olduğu için
  `resolveDynamicModel`, `capabilities`, `buildAuthDoctorHint`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `isCacheTtlEligible`,
  `resolveDefaultThinkingLevel`, `applyConfigDefaults`, `isModernModelRef`
  ve `wrapStreamFn` kullanır.
- Anthropic’in Claude’a özgü akış yardımcıları şimdilik
  paketlenmiş plugin’in kendi genel `api.ts` / `contract-api.ts` yüzeyinde kalır. Bu paket yüzeyi,
  genel SDK’yı tek bir sağlayıcının beta üst bilgisi kuralları etrafında genişletmek yerine
  `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
  `resolveAnthropicFastMode`, `resolveAnthropicServiceTier` ve daha alt düzey
  Anthropic sarmalayıcı oluşturucularını dışa aktarır.
- OpenAI, GPT-5.4 ileri uyumluluğuna, doğrudan OpenAI
  `openai-completions` -> `openai-responses` normalleştirmesine, Codex farkında kimlik doğrulama
  ipuçlarına, Spark bastırmasına, sentetik OpenAI liste satırlarına ve GPT-5 düşünme /
  canlı model politikasına sahip olduğu için `resolveDynamicModel`, `normalizeResolvedModel` ve
  `capabilities` ile birlikte `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `supportsXHighThinking` ve `isModernModelRef`
  kullanır; `openai-responses-defaults` akış ailesi ise
  ilişkilendirme üst bilgileri, `/fast`/`serviceTier`, metin ayrıntı düzeyi, yerel Codex web araması,
  akıl yürütme uyumluluğu yük şekillendirmesi ve Responses bağlam yönetimi için
  paylaşılan yerel OpenAI Responses sarmalayıcılarına sahiptir.
- OpenRouter, sağlayıcı geçişli olduğu ve OpenClaw’ın statik kataloğu güncellenmeden önce yeni
  model kimliklerini açığa çıkarabildiği için `catalog` ile birlikte
  `resolveDynamicModel` ve `prepareDynamicModel` kullanır; ayrıca
  sağlayıcıya özgü istek üst bilgilerini, yönlendirme meta verilerini, akıl yürütme yamalarını ve
  istem önbelleği politikasını çekirdeğin dışında tutmak için
  `capabilities`, `wrapStreamFn` ve `isCacheTtlEligible` kullanır. Replay politikası
  `passthrough-gemini` ailesinden gelirken, `openrouter-thinking` akış ailesi
  ara sunucu akıl yürütme eklemesine ve desteklenmeyen model / `auto` atlamalarına sahiptir.
- GitHub Copilot, sağlayıcıya ait cihazla giriş, model geri dönüş davranışı, Claude döküm
  tuhaflıkları, GitHub belirteci -> Copilot belirteci değişimi ve sağlayıcıya ait
  kullanım uç noktasına ihtiyaç duyduğu için `catalog`, `auth`, `resolveDynamicModel` ve
  `capabilities` ile birlikte `prepareRuntimeAuth` ve `fetchUsageSnapshot` kullanır.
- OpenAI Codex, hâlâ çekirdek OpenAI aktarımları üzerinde çalışsa da aktarım/temel URL
  normalleştirmesine, OAuth yenileme geri dönüş politikasına, varsayılan aktarım seçimine,
  sentetik Codex katalog satırlarına ve ChatGPT kullanım uç noktası entegrasyonuna sahip olduğu için
  `catalog`, `resolveDynamicModel`,
  `normalizeResolvedModel`, `refreshOAuth` ve `augmentModelCatalog` ile birlikte
  `prepareExtraParams`, `resolveUsageAuth` ve `fetchUsageSnapshot` kullanır;
  doğrudan OpenAI ile aynı `openai-responses-defaults` akış ailesini paylaşır.
- Google AI Studio ve Gemini CLI OAuth,
  `google-gemini` replay ailesi Gemini 3.1 ileri uyumluluk geri dönüşüne,
  yerel Gemini replay doğrulamasına, önyükleme replay temizliğine, etiketli
  akıl yürütme çıktı moduna ve modern-model eşlemesine sahip olduğu için
  `resolveDynamicModel`,
  `buildReplayPolicy`, `sanitizeReplayHistory`,
  `resolveReasoningOutputMode`, `wrapStreamFn` ve `isModernModelRef` kullanır;
  `google-thinking` akış ailesi ise Gemini düşünme yükü normalleştirmesine sahiptir;
  Gemini CLI OAuth ayrıca belirteç biçimlendirme, belirteç ayrıştırma ve kota uç noktası
  bağlantısı için `formatApiKey`, `resolveUsageAuth` ve
  `fetchUsageSnapshot` kullanır.
- Anthropic Vertex, Claude’a özgü replay temizliğinin her `anthropic-messages` aktarımı yerine
  yalnızca Claude kimlikleriyle sınırlı kalması için
  `anthropic-by-model` replay ailesi üzerinden `buildReplayPolicy` kullanır.
- Amazon Bedrock, Anthropic-on-Bedrock trafiği için
  Bedrock’a özgü kısma/hazır değil/bağlam taşması hata sınıflandırmasına sahip olduğu için
  `buildReplayPolicy`, `matchesContextOverflowError`,
  `classifyFailoverReason` ve `resolveDefaultThinkingLevel` kullanır;
  replay politikası ise yine aynı
  yalnızca Claude’a özel `anthropic-by-model` korumasını paylaşır.
- OpenRouter, Kilocode, Opencode ve Opencode Go, Gemini
  modellerini OpenAI uyumlu aktarımlar üzerinden ara sunucuya yönlendirdikleri ve
  yerel Gemini replay doğrulaması veya önyükleme yeniden yazımları olmadan Gemini
  düşünce-imzası temizliğine ihtiyaç duydukları için
  `passthrough-gemini` replay ailesi üzerinden `buildReplayPolicy` kullanır.
- MiniMax, bir sağlayıcı hem Anthropic-message hem de OpenAI uyumlu semantiğe sahip olduğu için
  `hybrid-anthropic-openai` replay ailesi üzerinden `buildReplayPolicy`
  kullanır; Anthropic tarafında yalnızca Claude’a özgü
  düşünme bloğu bırakmayı korurken akıl yürütme çıktı modunu yeniden yerel moda döndürür
  ve `minimax-fast-mode` akış ailesi paylaşılan akış yolundaki
  hızlı mod model yeniden yazımlarına sahiptir.
- Moonshot, hâlâ paylaşılan
  OpenAI aktarımını kullandığı ancak sağlayıcıya ait düşünme yükü normalleştirmesine ihtiyaç duyduğu için
  `catalog` ile birlikte `wrapStreamFn` kullanır; `moonshot-thinking` akış ailesi
  yapılandırma ile `/think` durumunu kendi yerel ikili düşünme yüküne eşler.
- Kilocode, sağlayıcıya ait istek üst bilgilerine,
  akıl yürütme yükü normalleştirmesine, Gemini döküm ipuçlarına ve Anthropic
  önbellek-TTL geçitlemesine ihtiyaç duyduğu için `catalog`, `capabilities`, `wrapStreamFn` ve
  `isCacheTtlEligible` kullanır; `kilocode-thinking` akış ailesi
  Kilo düşünme eklemesini, açık akıl yürütme yüklerini desteklemeyen `kilo/auto` ve
  diğer ara sunucu model kimliklerini atlarken, paylaşılan ara sunucu akış yolunda tutar.
- Z.AI, GLM-5 geri dönüşüne,
  `tool_stream` varsayılanlarına, ikili düşünme UX’ine, modern-model eşlemesine ve hem
  kullanım kimlik doğrulaması hem de kota getirmeye sahip olduğu için `resolveDynamicModel`, `prepareExtraParams`, `wrapStreamFn`,
  `isCacheTtlEligible`, `isBinaryThinking`, `isModernModelRef`,
  `resolveUsageAuth` ve `fetchUsageSnapshot` kullanır; `tool-stream-default-on`
  akış ailesi varsayılan açık `tool_stream` sarmalayıcısını
  sağlayıcı başına el yazımı yapıştırıcıların dışında tutar.
- xAI, yerel xAI Responses aktarım normalleştirmesine, Grok hızlı mod
  takma ad yeniden yazımlarına, varsayılan `tool_stream` ayarına, sıkı araç / akıl yürütme yükü
  temizliğine, plugin’e ait araçlar için geri dönüş kimlik doğrulama yeniden kullanımına, ileri uyumlu Grok
  model çözümlemesine ve xAI araç şeması
  profili, desteklenmeyen şema anahtar sözcükleri, yerel `web_search` ve HTML varlığı
  araç çağrısı bağımsız değişken çözümleme gibi sağlayıcıya ait uyumluluk yamalarına sahip olduğu için
  `normalizeResolvedModel`, `normalizeTransport`,
  `contributeResolvedModelCompat`, `prepareExtraParams`, `wrapStreamFn`,
  `resolveSyntheticAuth`, `resolveDynamicModel` ve `isModernModelRef`
  kullanır.
- Mistral, OpenCode Zen ve OpenCode Go, döküm/araç tuhaflıklarını çekirdeğin dışında tutmak için yalnızca `capabilities` kullanır.
- `byteplus`, `cloudflare-ai-gateway`,
  `huggingface`, `kimi-coding`, `nvidia`, `qianfan`,
  `synthetic`, `together`, `venice`, `vercel-ai-gateway` ve `volcengine` gibi yalnızca katalog kullanan paketlenmiş sağlayıcılar
  yalnızca `catalog` kullanır.
- Qwen, metin sağlayıcısı için `catalog` ile birlikte çok modlu yüzeyleri için
  paylaşılan medya-anlama ve video-oluşturma kayıtlarını kullanır.
- MiniMax ve Xiaomi, çıkarım hâlâ paylaşılan
  aktarımlar üzerinden çalışsa da `/usage`
  davranışları plugin’e ait olduğu için `catalog` ile birlikte kullanım kancalarını kullanır.

## Çalışma zamanı yardımcıları

Plugin’ler, seçilmiş çekirdek yardımcılarına `api.runtime` üzerinden erişebilir. TTS için:

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

- `textToSpeech`, dosya/sesli not yüzeyleri için normal çekirdek TTS çıktı yükünü döndürür.
- Çekirdek `messages.tts` yapılandırmasını ve sağlayıcı seçimini kullanır.
- PCM ses arabelleği + örnekleme hızı döndürür. Plugin’ler sağlayıcılar için yeniden örnekleme/kodlama yapmalıdır.
- `listVoices`, sağlayıcı başına isteğe bağlıdır. Bunu satıcıya ait ses seçicileri veya kurulum akışları için kullanın.
- Ses listeleri, sağlayıcı farkında seçiciler için yerel ayar, cinsiyet ve kişilik etiketleri gibi daha zengin meta veriler içerebilir.
- Bugün telefon desteğini OpenAI ve ElevenLabs sağlar. Microsoft sağlamaz.

Plugin’ler ayrıca `api.registerSpeechProvider(...)` üzerinden konuşma sağlayıcıları kaydedebilir.

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

- TTS politikasını, geri dönüşü ve yanıt teslimini çekirdekte tutun.
- Satıcıya ait sentez davranışı için konuşma sağlayıcılarını kullanın.
- Eski Microsoft `edge` girdisi `microsoft` sağlayıcı kimliğine normalleştirilir.
- Tercih edilen sahiplik modeli şirket odaklıdır: OpenClaw bu
  yetenek sözleşmelerini ekledikçe, tek bir satıcı plugin’i
  metin, konuşma, görsel ve gelecekteki medya sağlayıcılarına sahip olabilir.

Görsel/ses/video anlama için plugin’ler, genel bir anahtar/değer torbası yerine
tek bir türlenmiş medya-anlama sağlayıcısı kaydeder:

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

- Orkestrasyonu, geri dönüşü, yapılandırmayı ve kanal bağlantısını çekirdekte tutun.
- Satıcı davranışını sağlayıcı plugin’inde tutun.
- Artımlı genişleme türlenmiş kalmalıdır: yeni isteğe bağlı yöntemler, yeni isteğe bağlı
  sonuç alanları, yeni isteğe bağlı yetenekler.
- Video oluşturma zaten aynı deseni izler:
  - çekirdek yetenek sözleşmesine ve çalışma zamanı yardımcısına sahiptir
  - satıcı plugin’leri `api.registerVideoGenerationProvider(...)` kaydeder
  - özellik/kanal plugin’leri `api.runtime.videoGeneration.*` kullanır

Medya-anlama çalışma zamanı yardımcıları için plugin’ler şunları çağırabilir:

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

Ses yazıya dökme için plugin’ler medya-anlama çalışma zamanını
veya eski STT takma adını kullanabilir:

```ts
const { text } = await api.runtime.mediaUnderstanding.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  // MIME güvenilir şekilde çıkarılamadığında isteğe bağlıdır:
  mime: "audio/ogg",
});
```

Notlar:

- `api.runtime.mediaUnderstanding.*`,
  görsel/ses/video anlama için tercih edilen paylaşılan yüzeydir.
- Çekirdek medya-anlama ses yapılandırmasını (`tools.media.audio`) ve sağlayıcı geri dönüş sırasını kullanır.
- Yazıya dökme çıktısı üretilmediğinde `{ text: undefined }` döndürür (örneğin, atlanan/desteklenmeyen girdi).
- `api.runtime.stt.transcribeAudioFile(...)` bir uyumluluk takma adı olarak kalır.

Plugin’ler ayrıca `api.runtime.subagent` üzerinden arka plan alt ajan çalıştırmaları başlatabilir:

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

- `provider` ve `model`, kalıcı oturum değişiklikleri değil, çalıştırma başına isteğe bağlı geçersiz kılmalardır.
- OpenClaw bu geçersiz kılma alanlarını yalnızca güvenilir çağıranlar için dikkate alır.
- Plugin’e ait geri dönüş çalıştırmaları için operatörlerin `plugins.entries.<id>.subagent.allowModelOverride: true` ile açıkça izin vermesi gerekir.
- Güvenilir plugin’leri belirli kanonik `provider/model` hedefleriyle sınırlamak için `plugins.entries.<id>.subagent.allowedModels` kullanın veya herhangi bir hedefe açıkça izin vermek için `"*"` kullanın.
- Güvenilmeyen plugin alt ajan çalıştırmaları yine de çalışır, ancak geçersiz kılma istekleri sessizce geri dönmek yerine reddedilir.

Web araması için plugin’ler, ajan araç bağlantısına
erişmek yerine paylaşılan çalışma zamanı yardımcısını kullanabilir:

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

Plugin’ler ayrıca
`api.registerWebSearchProvider(...)` üzerinden web arama sağlayıcıları kaydedebilir.

Notlar:

- Sağlayıcı seçimini, kimlik bilgisi çözümlemesini ve paylaşılan istek semantiğini çekirdekte tutun.
- Satıcıya özgü arama aktarımları için web arama sağlayıcılarını kullanın.
- `api.runtime.webSearch.*`, arama davranışına ajan araç sarmalayıcısına bağımlı olmadan ihtiyaç duyan özellik/kanal plugin’leri için tercih edilen paylaşılan yüzeydir.

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

- `generate(...)`: yapılandırılmış görsel oluşturma sağlayıcı zincirini kullanarak bir görsel oluşturur.
- `listProviders(...)`: kullanılabilir görsel oluşturma sağlayıcılarını ve yeteneklerini listeler.

## Gateway HTTP rotaları

Plugin’ler `api.registerHttpRoute(...)` ile HTTP uç noktaları sunabilir.

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
- `auth`: gereklidir. Normal gateway kimlik doğrulamasını gerektirmek için `"gateway"` veya plugin tarafından yönetilen kimlik doğrulama/webhook doğrulaması için `"plugin"` kullanın.
- `match`: isteğe bağlıdır. `"exact"` (varsayılan) veya `"prefix"`.
- `replaceExisting`: isteğe bağlıdır. Aynı plugin’in kendi mevcut rota kaydını değiştirmesine izin verir.
- `handler`: rota isteği işlediyse `true` döndürmelidir.

Notlar:

- `api.registerHttpHandler(...)` kaldırılmıştır ve plugin yükleme hatasına neden olur. Bunun yerine `api.registerHttpRoute(...)` kullanın.
- Plugin rotaları `auth` değerini açıkça bildirmelidir.
- Kesin `path + match` çakışmaları, `replaceExisting: true` olmadıkça reddedilir ve bir plugin başka bir plugin’in rotasını değiştiremez.
- Farklı `auth` düzeylerine sahip çakışan rotalar reddedilir. `exact`/`prefix` ardışık geçiş zincirlerini yalnızca aynı kimlik doğrulama düzeyinde tutun.
- `auth: "plugin"` rotaları operatör çalışma zamanı kapsamlarını otomatik olarak almaz. Bunlar ayrıcalıklı Gateway yardımcı çağrıları için değil, plugin tarafından yönetilen webhook’lar/imza doğrulaması içindir.
- `auth: "gateway"` rotaları bir Gateway istek çalışma zamanı kapsamı içinde çalışır, ancak bu kapsam kasıtlı olarak temkinlidir:
  - paylaşılan gizli taşıyıcı kimlik doğrulaması (`gateway.auth.mode = "token"` / `"password"`), çağıran `x-openclaw-scopes` gönderse bile plugin-rotası çalışma zamanı kapsamlarını `operator.write` değerine sabitler
  - güvenilir kimlik taşıyan HTTP kipleri (örneğin `trusted-proxy` veya özel bir girişte `gateway.auth.mode = "none"`), `x-openclaw-scopes` yalnızca üst bilgi açıkça mevcutsa dikkate alır
  - bu kimlik taşıyan plugin-rotası isteklerinde `x-openclaw-scopes` yoksa, çalışma zamanı kapsamı `operator.write` değerine geri döner
- Pratik kural: gateway kimlik doğrulamalı bir plugin rotasının örtük bir yönetici yüzeyi olduğunu varsaymayın. Rotanızın yalnızca yöneticiye özel davranışa ihtiyacı varsa, kimlik taşıyan bir kimlik doğrulama kipi gerektirin ve açık `x-openclaw-scopes` üst bilgi sözleşmesini belgelendirin.

## Plugin SDK içe aktarma yolları

Plugin yazarken tek parça `openclaw/plugin-sdk` içe aktarması yerine
SDK alt yollarını kullanın:

- plugin kayıt ilkel öğeleri için `openclaw/plugin-sdk/plugin-entry`.
- genel paylaşılan plugin odaklı sözleşme için `openclaw/plugin-sdk/core`.
- kök `openclaw.json` Zod şema
  dışa aktarımı (`OpenClawSchema`) için `openclaw/plugin-sdk/config-schema`.
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
  `openclaw/plugin-sdk/webhook-ingress` gibi kararlı kanal ilkel öğeleri, paylaşılan kurulum/kimlik doğrulama/yanıt/webhook
  bağlantısı içindir. `channel-inbound`, debounce, bahsetme eşleme,
  gelen bahsetme politikası yardımcıları, zarf biçimlendirme ve gelen zarf
  bağlam yardımcıları için paylaşılan merkezdir.
  `channel-setup`, dar isteğe bağlı kurulum yüzeyidir.
  `setup-runtime`, `setupEntry` /
  ertelenmiş başlangıç tarafından kullanılan çalışma zamanı güvenli kurulum yüzeyidir; içe aktarma güvenli kurulum yama bağdaştırıcılarını da içerir.
  `setup-adapter-runtime`, ortam farkında hesap kurulum bağdaştırıcı yüzeyidir.
  `setup-tools`, küçük CLI/arşiv/belge yardımcı yüzeyidir (`formatCliCommand`,
  `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`,
  `CONFIG_DIR`).
- `openclaw/plugin-sdk/channel-config-helpers`,
  `openclaw/plugin-sdk/allow-from`,
  `openclaw/plugin-sdk/channel-config-schema`,
  `openclaw/plugin-sdk/telegram-command-config`,
  `openclaw/plugin-sdk/channel-policy`,
  `openclaw/plugin-sdk/approval-gateway-runtime`,
  `openclaw/plugin-sdk/approval-handler-adapter-runtime`,
  `openclaw/plugin-sdk/approval-handler-runtime`,
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
  `openclaw/plugin-sdk/directory-runtime` gibi alan alt yolları, paylaşılan çalışma zamanı/yapılandırma yardımcıları içindir.
  `telegram-command-config`, Telegram özel
  komut normalleştirme/doğrulama için dar genel yüzeydir ve paketlenmiş
  Telegram sözleşme yüzeyi geçici olarak kullanılamasa bile kullanılabilir durumda kalır.
  `text-runtime`, yardımcıya görünür metin çıkarma, markdown işleme/parçalama yardımcıları, sansürleme
  yardımcıları, yönerge etiketi yardımcıları ve güvenli metin yardımcılarını içeren
  paylaşılan metin/markdown/günlükleme yüzeyidir.
- Onaya özgü kanal yüzeyleri plugin üzerinde tek bir `approvalCapability`
  sözleşmesini tercih etmelidir. Böylece çekirdek, onay davranışını ilgisiz plugin alanlarına karıştırmak yerine
  onay kimlik doğrulamasını, teslimi, işlemesini, yerel yönlendirmeyi ve
  tembel yerel işleyici davranışını bu tek yetenek üzerinden okur.
- `openclaw/plugin-sdk/channel-runtime` kullanımdan kaldırılmıştır ve yalnızca
  eski plugin’ler için bir uyumluluk köprüsü olarak kalır. Yeni kod bunun yerine daha dar
  genel ilkel öğeleri içe aktarmalıdır ve repo kodu köprüye yeni içe aktarmalar eklememelidir.
- Paketlenmiş uzantı iç bileşenleri özel kalır. Harici plugin’ler yalnızca
  `openclaw/plugin-sdk/*` alt yollarını kullanmalıdır. OpenClaw çekirdek/test kodu,
  `index.js`, `api.js`,
  `runtime-api.js`, `setup-entry.js` ve
  `login-qr-api.js` gibi dar kapsamlı dosyalar gibi, bir plugin paketi kökü altındaki repo
  genel giriş noktalarını kullanabilir. Çekirdekten veya başka
  bir uzantıdan asla bir plugin paketinin `src/*` yolunu içe aktarmayın.
- Repo giriş noktası ayrımı:
  `<plugin-package-root>/api.js` yardımcı/tür paketi,
  `<plugin-package-root>/runtime-api.js` yalnızca çalışma zamanı paketi,
  `<plugin-package-root>/index.js` paketlenmiş plugin girişi
  ve `<plugin-package-root>/setup-entry.js` kurulum plugin girişidir.
- Güncel paketlenmiş sağlayıcı örnekleri:
  - Anthropic, `wrapAnthropicProviderStream`, beta-header yardımcıları ve `service_tier`
    ayrıştırması gibi Claude akış yardımcıları için `api.js` / `contract-api.js` kullanır.
  - OpenAI, sağlayıcı oluşturucular, varsayılan model yardımcıları ve
    gerçek zamanlı sağlayıcı oluşturucular için `api.js` kullanır.
  - OpenRouter, sağlayıcı oluşturucusu ile birlikte ilk kurulum/yapılandırma
    yardımcıları için `api.js` kullanır; buna karşılık `register.runtime.js` repo içi kullanım için yine de genel
    `plugin-sdk/provider-stream` yardımcılarını yeniden dışa aktarabilir.
- Cephe yüklemeli genel giriş noktaları, biri varsa etkin çalışma zamanı yapılandırma anlık görüntüsünü tercih eder,
  sonra OpenClaw henüz çalışma zamanı anlık görüntüsü sunmadığında diskte çözülmüş yapılandırma dosyasına geri döner.
- Genel paylaşılan ilkel öğeler tercih edilen genel SDK sözleşmesi olarak kalır. Paketlenmiş kanal markalı yardımcı yüzeylerin
  küçük, ayrılmış bir uyumluluk kümesi hâlâ vardır. Bunları yeni
  üçüncü taraf içe aktarma hedefleri olarak değil, paketlenmiş bakım/uyumluluk yüzeyleri olarak değerlendirin;
  yeni çapraz kanal sözleşmeleri yine de genel `plugin-sdk/*` alt yollarına veya plugin’e yerel `api.js` /
  `runtime-api.js` paketlerine eklenmelidir.

Uyumluluk notu:

- Yeni kod için kök `openclaw/plugin-sdk` paketini kullanmaktan kaçının.
- Önce dar ve kararlı ilkel öğeleri tercih edin. Daha yeni setup/pairing/reply/
  feedback/contract/inbound/threading/command/secret-input/webhook/infra/
  allowlist/status/message-tool alt yolları, yeni
  paketlenmiş ve harici plugin çalışmaları için hedeflenen sözleşmedir.
  Hedef ayrıştırma/eşleme `openclaw/plugin-sdk/channel-targets` üzerinde yer almalıdır.
  Mesaj eylemi kapıları ve tepki mesaj kimliği yardımcıları ise
  `openclaw/plugin-sdk/channel-actions` üzerinde yer almalıdır.
- Paketlenmiş uzantıya özgü yardımcı paketler varsayılan olarak kararlı değildir. Bir
  yardımcı yalnızca paketlenmiş bir uzantı tarafından gerekiyorsa, bunu
  `openclaw/plugin-sdk/<extension>` içine taşımak yerine uzantının
  yerel `api.js` veya `runtime-api.js` yüzeyinin arkasında tutun.
- Yeni paylaşılan yardımcı yüzeyleri kanal markalı değil, genel olmalıdır. Paylaşılan hedef
  ayrıştırma `openclaw/plugin-sdk/channel-targets` üzerinde yer almalıdır; kanala özgü
  iç bileşenler ise sahip olan plugin’in yerel `api.js` veya `runtime-api.js`
  yüzeyinin arkasında kalmalıdır.
- `image-generation`,
  `media-understanding` ve `speech` gibi yeteneğe özgü alt yollar mevcuttur; çünkü paketlenmiş/yerel plugin’ler
  bunları bugün kullanmaktadır. Bunların varlığı, tek başına, dışa aktarılan her yardımcının
  uzun vadede dondurulmuş bir harici sözleşme olduğu anlamına gelmez.

## Message aracı şemaları

Plugin’ler, kanala özgü `describeMessageTool(...)` şema
katkılarına sahip olmalıdır. Sağlayıcıya özgü alanları paylaşılan çekirdekte değil, plugin içinde tutun.

Paylaşılan taşınabilir şema parçaları için,
`openclaw/plugin-sdk/channel-actions` üzerinden dışa aktarılan genel yardımcıları yeniden kullanın:

- düğme ızgarası tarzı yükler için `createMessageToolButtonsSchema()`
- yapılandırılmış kart yükleri için `createMessageToolCardSchema()`

Bir şema biçimi yalnızca tek bir sağlayıcı için anlamlıysa, bunu paylaşılan SDK’ya
taşımak yerine o plugin’in kendi kaynağında tanımlayın.

## Kanal hedef çözümleme

Kanal plugin’leri kanala özgü hedef anlambilimine sahip olmalıdır. Paylaşılan
giden ana makineyi genel tutun ve sağlayıcı kuralları için mesajlaşma bağdaştırıcı yüzeyini kullanın:

- `messaging.inferTargetChatType({ to })`, normalleştirilmiş bir hedefin
  dizin aramasından önce `direct`, `group` veya `channel` olarak ele alınıp alınmayacağına karar verir.
- `messaging.targetResolver.looksLikeId(raw, normalized)`, bir
  girdinin dizin araması yerine doğrudan kimlik benzeri çözümlemeye geçip geçmemesi gerektiğini çekirdeğe bildirir.
- `messaging.targetResolver.resolveTarget(...)`, çekirdeğin normalleştirmeden sonra veya
  dizin kaçırmasından sonra sağlayıcıya ait son çözümlemeye ihtiyaç duyduğunda plugin geri dönüş yoludur.
- `messaging.resolveOutboundSessionRoute(...)`, bir hedef çözümlendikten sonra sağlayıcıya özgü oturum
  rota kurulumuna sahiptir.

Önerilen ayrım:

- Eşler/gruplar aranmasından önce gerçekleşmesi gereken kategori kararları için `inferTargetChatType` kullanın.
- “Bunu açık/yerel bir hedef kimliği olarak ele al” denetimleri için `looksLikeId` kullanın.
- Geniş dizin araması için değil, sağlayıcıya özgü normalleştirme geri dönüşü için `resolveTarget` kullanın.
- Sohbet kimlikleri, iş parçacığı kimlikleri, JID’ler, tanıtıcılar ve oda kimlikleri gibi sağlayıcıya özgü yerel kimlikleri
  genel SDK alanlarında değil, `target` değerleri veya sağlayıcıya özgü parametreler içinde tutun.

## Yapılandırma destekli dizinler

Yapılandırmadan dizin girdileri türeten plugin’ler bu mantığı plugin içinde tutmalı
ve `openclaw/plugin-sdk/directory-runtime`
altındaki paylaşılan yardımcıları yeniden kullanmalıdır.

Bunu, bir kanalın şu tür yapılandırma destekli eşlere/gruplara ihtiyaç duyduğu durumlarda kullanın:

- izin listesi güdümlü DM eşleri
- yapılandırılmış kanal/grup eşlemeleri
- hesap kapsamlı statik dizin geri dönüşleri

`directory-runtime` içindeki paylaşılan yardımcılar yalnızca genel işlemleri yürütür:

- sorgu filtreleme
- sınır uygulama
- yinelenen kaldırma/normalleştirme yardımcıları
- `ChannelDirectoryEntry[]` oluşturma

Kanala özgü hesap incelemesi ve kimlik normalleştirmesi plugin uygulamasında kalmalıdır.

## Sağlayıcı katalogları

Sağlayıcı plugin’leri, çıkarım için model kataloglarını
`registerProvider({ catalog: { run(...) { ... } } })` ile tanımlayabilir.

`catalog.run(...)`, OpenClaw’ın
`models.providers` içine yazdığı yapının aynısını döndürür:

- tek bir sağlayıcı girdisi için `{ provider }`
- birden çok sağlayıcı girdisi için `{ providers }`

Plugin sağlayıcıya özgü model kimliklerine, temel URL
varsayılanlarına veya kimlik doğrulama kapılı model meta verilerine sahipse `catalog` kullanın.

`catalog.order`, bir plugin kataloğunun OpenClaw’ın
yerleşik örtük sağlayıcılarına göre ne zaman birleştirileceğini denetler:

- `simple`: düz API anahtarlı veya ortam güdümlü sağlayıcılar
- `profile`: kimlik doğrulama profilleri mevcut olduğunda görünen sağlayıcılar
- `paired`: birden çok ilişkili sağlayıcı girdisini sentezleyen sağlayıcılar
- `late`: diğer örtük sağlayıcılardan sonra son geçiş

Daha sonraki sağlayıcılar anahtar çakışmasında kazanır; böylece plugin’ler aynı sağlayıcı kimliğiyle
yerleşik bir sağlayıcı girdisini kasıtlı olarak geçersiz kılabilir.

Uyumluluk:

- `discovery`, eski bir takma ad olarak hâlâ çalışır
- hem `catalog` hem de `discovery` kaydedilmişse OpenClaw `catalog` kullanır

## Salt okunur kanal incelemesi

Plugin’iniz bir kanal kaydediyorsa,
`resolveAccount(...)` ile birlikte `plugin.config.inspectAccount(cfg, accountId)` uygulamayı tercih edin.

Neden:

- `resolveAccount(...)` çalışma zamanı yoludur. Kimlik bilgilerinin
  tamamen somutlaştırıldığını varsayabilir ve gerekli gizli değerler eksik olduğunda hızlıca başarısız olabilir.
- `openclaw status`, `openclaw status --all`,
  `openclaw channels status`, `openclaw channels resolve` ve doctor/config
  onarım akışları gibi salt okunur komut yolları, yalnızca yapılandırmayı
  açıklamak için çalışma zamanı kimlik bilgilerini somutlaştırmak zorunda kalmamalıdır.

Önerilen `inspectAccount(...)` davranışı:

- Yalnızca açıklayıcı hesap durumunu döndürün.
- `enabled` ve `configured` değerlerini koruyun.
- Gerekli olduğunda kimlik bilgisi kaynağı/durum alanlarını ekleyin; örneğin:
  - `tokenSource`, `tokenStatus`
  - `botTokenSource`, `botTokenStatus`
  - `appTokenSource`, `appTokenStatus`
  - `signingSecretSource`, `signingSecretStatus`
- Salt okunur kullanılabilirliği bildirmek için ham belirteç değerlerini döndürmeniz gerekmez.
  Durum tarzı komutlar için `tokenStatus: "available"` döndürmek
  (ve eşleşen kaynak alanı) yeterlidir.
- Bir kimlik bilgisi SecretRef üzerinden yapılandırılmışsa ancak
  mevcut komut yolunda kullanılamıyorsa `configured_unavailable` kullanın.

Bu, salt okunur komutların çökmesi veya hesabı yanlış biçimde yapılandırılmamış olarak
bildirmesi yerine “yapılandırılmış ancak bu komut yolunda kullanılamıyor”
şeklinde rapor vermesini sağlar.

## Paket paketleri

Bir plugin dizini, `openclaw.extensions` içeren bir `package.json` dosyası içerebilir:

```json
{
  "name": "my-pack",
  "openclaw": {
    "extensions": ["./src/safety.ts", "./src/tools.ts"],
    "setupEntry": "./src/setup-entry.ts"
  }
}
```

Her girdi bir plugin’e dönüşür. Paket birden çok uzantı listeliyorsa plugin kimliği
`name/<fileBase>` olur.

Plugin’iniz npm bağımlılıkları içe aktarıyorsa, `node_modules`
kullanılabilir olsun diye bunları o dizinde kurun (`npm install` / `pnpm install`).

Güvenlik korkuluğu: her `openclaw.extensions` girdisi, sembolik bağlantı çözümlemesinden sonra
plugin dizini içinde kalmalıdır. Paket dizininden çıkan girdiler
reddedilir.

Güvenlik notu: `openclaw plugins install`, plugin bağımlılıklarını
`npm install --omit=dev --ignore-scripts` ile kurar (yaşam döngüsü betikleri yok, çalışma zamanında geliştirme bağımlılıkları yok). Plugin bağımlılık
ağaçlarını “saf JS/TS” tutun ve `postinstall` derlemeleri gerektiren paketlerden kaçının.

İsteğe bağlı: `openclaw.setupEntry`, hafif bir yalnızca kurulum modülünü işaret edebilir.
OpenClaw, devre dışı bir kanal plugin’i için kurulum yüzeylerine ihtiyaç duyduğunda veya
bir kanal plugin’i etkin ancak hâlâ yapılandırılmamış olduğunda,
tam plugin girdisi yerine `setupEntry` yükler. Bu, ana plugin girdiniz aynı zamanda araçlar, kancalar veya başka yalnızca çalışma zamanı
kodları da bağlıyorsa başlangıcı ve kurulumu daha hafif tutar.

İsteğe bağlı: `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`,
bir kanal plugin’ini, kanal zaten yapılandırılmış olsa bile, gateway’in
dinleme öncesi başlangıç aşamasında aynı `setupEntry` yoluna dahil edebilir.

Bunu yalnızca `setupEntry`, gateway dinlemeye başlamadan
önce var olması gereken başlangıç yüzeyini tamamen kapsıyorsa kullanın. Pratikte bu, kurulum girdisinin başlangıcın bağlı olduğu
kanala ait tüm yetenekleri kaydetmesi gerektiği anlamına gelir; örneğin:

- kanal kaydının kendisi
- gateway dinlemeye başlamadan önce kullanılabilir olması gereken tüm HTTP rotaları
- aynı zaman penceresinde var olması gereken tüm gateway yöntemleri, araçlar veya servisler

Tam girdiniz hâlâ gerekli herhangi bir başlangıç yeteneğine sahipse bu bayrağı
etkinleştirmeyin. Plugin’i varsayılan davranışta bırakın ve OpenClaw’ın başlangıç sırasında
tam girdiyi yüklemesine izin verin.

Paketlenmiş kanallar, çekirdeğin tam kanal çalışma zamanı yüklenmeden önce
danışabileceği yalnızca kurulum amaçlı sözleşme-yüzeyi yardımcıları da yayımlayabilir. Güncel kurulum
yükseltme yüzeyi şudur:

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

Çekirdek bu yüzeyi, tam plugin girdisini yüklemeden
eski tek hesaplı kanal yapılandırmasını `channels.<id>.accounts.*` içine yükseltmesi gerektiğinde kullanır.
Mevcut paketlenmiş örnek Matrix’tir: adlandırılmış hesaplar zaten varken yalnızca auth/bootstrap anahtarlarını
adlandırılmış bir yükseltilmiş hesaba taşır ve her zaman
`accounts.default` oluşturmaktansa yapılandırılmış kanonik olmayan bir varsayılan hesap anahtarını koruyabilir.

Bu kurulum yama bağdaştırıcıları, paketlenmiş sözleşme-yüzeyi keşfini tembel tutar.
İçe aktarma zamanı hafif kalır; yükseltme yüzeyi modül içe aktarmasında paketlenmiş kanal başlangıcına yeniden girmek yerine
yalnızca ilk kullanımda yüklenir.

Bu başlangıç yüzeyleri gateway RPC yöntemlerini içerdiğinde, bunları
plugin’e özgü bir ön ek üzerinde tutun. Çekirdek yönetici ad alanları (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) ayrılmış kalır ve bir plugin daha dar bir kapsam istese bile
her zaman `operator.admin` değerine çözülür.

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

Kanal plugin’leri `openclaw.channel` üzerinden kurulum/keşif meta verileri ve
`openclaw.install` üzerinden kurulum ipuçları tanıtabilir. Bu, çekirdeği katalog verisinden bağımsız tutar.

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

Asgari örneğin ötesinde kullanışlı `openclaw.channel` alanları:

- `detailLabel`: daha zengin katalog/durum yüzeyleri için ikincil etiket
- `docsLabel`: belge bağlantısı için bağlantı metnini geçersiz kılar
- `preferOver`: bu katalog girdisinin önüne geçmesi gereken daha düşük öncelikli plugin/kanal kimlikleri
- `selectionDocsPrefix`, `selectionDocsOmitLabel`, `selectionExtras`: seçim yüzeyi metin denetimleri
- `markdownCapable`: giden biçimlendirme kararları için kanalı markdown yetenekli olarak işaretler
- `exposure.configured`: `false` olduğunda kanalı yapılandırılmış kanal listeleme yüzeylerinden gizler
- `exposure.setup`: `false` olduğunda kanalı etkileşimli kurulum/yapılandırma seçicilerinden gizler
- `exposure.docs`: belge gezinme yüzeyleri için kanalı iç/özel olarak işaretler
- `showConfigured` / `showInSetup`: eski takma adlar uyumluluk için hâlâ kabul edilir; `exposure` tercih edin
- `quickstartAllowFrom`: kanalı standart hızlı başlangıç `allowFrom` akışına dahil eder
- `forceAccountBinding`: yalnızca bir hesap olsa bile açık hesap bağlamasını zorunlu kılar
- `preferSessionLookupForAnnounceTarget`: duyuru hedefleri çözülürken oturum aramasını tercih eder

OpenClaw ayrıca **harici kanal kataloglarını** da birleştirebilir (örneğin, bir MPM
kayıt defteri dışa aktarımı). Şu konumlardan birine bir JSON dosyası bırakın:

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

Veya `OPENCLAW_PLUGIN_CATALOG_PATHS` (ya da `OPENCLAW_MPM_CATALOG_PATHS`) değişkenini
bir veya daha fazla JSON dosyasına yönlendirin (virgül/noktalı virgül/`PATH` ile ayrılmış). Her dosya
`{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }` içermelidir. Ayrıştırıcı, `"entries"` anahtarı için eski takma adlar olarak `"packages"` veya `"plugins"` değerlerini de kabul eder.

## Bağlam motoru plugin’leri

Bağlam motoru plugin’leri, alım, birleştirme ve sıkıştırma için oturum bağlamı orkestrasyonuna sahiptir.
Bunları plugin’inizden
`api.registerContextEngine(id, factory)` ile kaydedin, ardından etkin motoru
`plugins.slots.contextEngine` ile seçin.

Bunu, plugin’inizin yalnızca bellek araması veya kancalar eklemek yerine
varsayılan bağlam işlem hattısını değiştirmesi ya da genişletmesi gerektiğinde kullanın.

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

Motorunuz sıkıştırma algoritmasına **sahip değilse**, `compact()`
uygulamasını koruyun ve bunu açıkça devredin:

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

Bir plugin’in mevcut API’ye uymayan bir davranışa ihtiyacı olduğunda,
plugin sistemini özel bir iç erişimle baypas etmeyin. Eksik yeteneği ekleyin.

Önerilen sıra:

1. çekirdek sözleşmeyi tanımlayın
   Çekirdeğin hangi paylaşılan davranışa sahip olması gerektiğine karar verin: politika, geri dönüş, yapılandırma birleştirme,
   yaşam döngüsü, kanala dönük anlambilim ve çalışma zamanı yardımcı şekli.
2. türlenmiş plugin kayıt/çalışma zamanı yüzeyleri ekleyin
   `OpenClawPluginApi` ve/veya `api.runtime` yüzeyini, yararlı olan en küçük
   türlenmiş yetenek yüzeyiyle genişletin.
3. çekirdek + kanal/özellik tüketicilerini bağlayın
   Kanallar ve özellik plugin’leri yeni yeteneği doğrudan bir satıcı uygulamasını içe aktararak değil,
   çekirdek üzerinden tüketmelidir.
4. satıcı uygulamalarını kaydedin
   Ardından satıcı plugin’leri arka uçlarını bu yeteneğe karşı kaydeder.
5. sözleşme kapsamı ekleyin
   Sahipliğin ve kayıt şeklinin zaman içinde açık kalması için testler ekleyin.

OpenClaw bu şekilde görüş sahibi kalırken tek bir
sağlayıcının bakış açısına sabit kodlanmış hâle gelmez. Somut bir dosya denetim listesi ve işlenmiş örnek için
[Capability Cookbook](/tr/plugins/architecture) sayfasına bakın.

### Yetenek denetim listesi

Yeni bir yetenek eklediğinizde, uygulama genellikle şu
yüzeylere birlikte dokunmalıdır:

- `src/<capability>/types.ts` içindeki çekirdek sözleşme türleri
- `src/<capability>/runtime.ts` içindeki çekirdek çalıştırıcı/çalışma zamanı yardımcısı
- `src/plugins/types.ts` içindeki plugin API kayıt yüzeyi
- `src/plugins/registry.ts` içindeki plugin kayıt defteri bağlantısı
- özellik/kanal
  plugin’lerinin bunu tüketmesi gerektiğinde `src/plugins/runtime/*` içindeki plugin çalışma zamanı gösterimi
- `src/test-utils/plugin-registration.ts` içindeki yakalama/test yardımcıları
- `src/plugins/contracts/registry.ts` içindeki sahiplik/sözleşme doğrulamaları
- `docs/` içindeki operatör/plugin belgeleri

Bu yüzeylerden biri eksikse, bu genellikle yeteneğin
henüz tam olarak entegre edilmediğinin işaretidir.

### Yetenek şablonu

Asgari desen:

```ts
// çekirdek sözleşme
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

// özellik/kanal plugin’leri için paylaşılan çalışma zamanı yardımcısı
const clip = await api.runtime.videoGeneration.generate({
  prompt: "Show the robot walking through the lab.",
  cfg,
});
```

Sözleşme test deseni:

```ts
expect(findVideoGenerationProviderIdsForPlugin("openai")).toEqual(["openai"]);
```

Bu kuralı basit tutar:

- çekirdek, yetenek sözleşmesine + orkestrasyona sahiptir
- satıcı plugin’leri satıcı uygulamalarına sahiptir
- özellik/kanal plugin’leri çalışma zamanı yardımcılarını tüketir
- sözleşme testleri sahipliği açık tutar
