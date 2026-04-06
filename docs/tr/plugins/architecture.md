---
read_when:
    - Yerel OpenClaw plugin'leri oluştururken veya hata ayıklarken
    - Plugin yetenek modelini veya sahiplik sınırlarını anlamaya çalışırken
    - Plugin yükleme hattı veya kayıt defteri üzerinde çalışırken
    - Sağlayıcı çalışma zamanı hook'larını veya kanal plugin'lerini uygularken
sidebarTitle: Internals
summary: 'Plugin iç yapıları: yetenek modeli, sahiplik, sözleşmeler, yükleme hattı ve çalışma zamanı yardımcıları'
title: Plugin İç Yapıları
x-i18n:
    generated_at: "2026-04-06T03:13:18Z"
    model: gpt-5.4
    provider: openai
    source_hash: d39158455701dedfb75f6c20b8c69fd36ed9841f1d92bed1915f448df57fd47b
    source_path: plugins/architecture.md
    workflow: 15
---

# Plugin İç Yapıları

<Info>
  Bu, **derin mimari başvuru** sayfasıdır. Pratik kılavuzlar için bkz.:
  - [Plugin yükleme ve kullanma](/tr/tools/plugin) — kullanıcı kılavuzu
  - [Başlangıç](/tr/plugins/building-plugins) — ilk plugin öğreticisi
  - [Kanal Plugin'leri](/tr/plugins/sdk-channel-plugins) — bir mesajlaşma kanalı oluşturun
  - [Sağlayıcı Plugin'leri](/tr/plugins/sdk-provider-plugins) — bir model sağlayıcısı oluşturun
  - [SDK Genel Bakışı](/tr/plugins/sdk-overview) — içe aktarma haritası ve kayıt API'si
</Info>

Bu sayfa, OpenClaw plugin sisteminin iç mimarisini kapsar.

## Genel yetenek modeli

Yetenekler, OpenClaw içindeki genel **yerel plugin** modelidir. Her
yerel OpenClaw plugin'i bir veya daha fazla yetenek türüne karşı kayıt olur:

| Yetenek               | Kayıt yöntemi                                    | Örnek plugin'ler                    |
| --------------------- | ------------------------------------------------ | ----------------------------------- |
| Metin çıkarımı        | `api.registerProvider(...)`                      | `openai`, `anthropic`               |
| Konuşma               | `api.registerSpeechProvider(...)`                | `elevenlabs`, `microsoft`           |
| Gerçek zamanlı transkripsiyon | `api.registerRealtimeTranscriptionProvider(...)` | `openai`                    |
| Gerçek zamanlı ses    | `api.registerRealtimeVoiceProvider(...)`         | `openai`                            |
| Medya anlama          | `api.registerMediaUnderstandingProvider(...)`    | `openai`, `google`                  |
| Görsel üretimi        | `api.registerImageGenerationProvider(...)`       | `openai`, `google`, `fal`, `minimax` |
| Müzik üretimi         | `api.registerMusicGenerationProvider(...)`       | `google`, `minimax`                 |
| Video üretimi         | `api.registerVideoGenerationProvider(...)`       | `qwen`                              |
| Web getirme           | `api.registerWebFetchProvider(...)`              | `firecrawl`                         |
| Web arama             | `api.registerWebSearchProvider(...)`             | `google`                            |
| Kanal / mesajlaşma    | `api.registerChannel(...)`                       | `msteams`, `matrix`                 |

Sıfır yetenek kaydeden ama hook'lar, araçlar veya
hizmetler sağlayan bir plugin, **eski yalnızca hook** plugin'idir. Bu desen hâlâ tamamen desteklenir.

### Harici uyumluluk duruşu

Yetenek modeli çekirdeğe yerleştirildi ve bugün paketlenmiş/yerel plugin'ler tarafından
kullanılıyor, ancak harici plugin uyumluluğu hâlâ
"içeri aktarılıyor, dolayısıyla dondurulmuştur" seviyesinden daha sıkı bir çıtaya ihtiyaç duyuyor.

Mevcut kılavuz:

- **mevcut harici plugin'ler:** hook tabanlı entegrasyonların çalışmasını sürdürün; bunu
  uyumluluk tabanı olarak kabul edin
- **yeni paketlenmiş/yerel plugin'ler:** satıcıya özgü içeri uzanma veya
  yeni yalnızca hook tasarımları yerine açık yetenek kaydını tercih edin
- **yetenek kaydını benimseyen harici plugin'ler:** izin verilir, ancak
  belgelerde bir sözleşme açıkça kararlı olarak işaretlenmedikçe
  yeteneğe özgü yardımcı yüzeyleri gelişen yüzeyler olarak değerlendirin

Pratik kural:

- yetenek kayıt API'leri amaçlanan yöndür
- geçiş sürecinde harici plugin'ler için en güvenli, kırılmasız yol eski hook'lardır
- dışa aktarılan yardımcı alt yolların hepsi eşdeğer değildir; rastlantısal yardımcı dışa aktarımlar değil,
  dar belgelenmiş sözleşme tercih edilmelidir

### Plugin şekilleri

OpenClaw, yüklenen her plugin'i gerçek
kayıt davranışına göre bir şekle sınıflandırır (yalnızca statik meta veriye göre değil):

- **plain-capability** -- tam olarak bir yetenek türü kaydeder (örneğin
  `mistral` gibi yalnızca sağlayıcı olan bir plugin)
- **hybrid-capability** -- birden fazla yetenek türü kaydeder (örneğin
  `openai`, metin çıkarımı, konuşma, medya anlama ve görsel
  üretiminin sahibidir)
- **hook-only** -- yalnızca hook'lar kaydeder (türlenmiş veya özel), yetenek,
  araç, komut veya hizmet kaydetmez
- **non-capability** -- yetenek kaydetmeden araçlar, komutlar, hizmetler veya rotalar kaydeder

Bir plugin'in şeklini ve yetenek
dökümünü görmek için `openclaw plugins inspect <id>` kullanın. Ayrıntılar için [CLI başvurusu](/cli/plugins#inspect) bölümüne bakın.

### Eski hook'lar

`before_agent_start` hook'u, yalnızca hook kullanan plugin'ler için bir uyumluluk yolu olarak desteklenmeye devam eder. Gerçek dünyadaki eski plugin'ler hâlâ buna bağımlıdır.

Yön:

- çalışır durumda tutun
- eski olarak belgelendirin
- model/sağlayıcı geçersiz kılma işleri için `before_model_resolve` tercih edin
- istem değişikliği işleri için `before_prompt_build` tercih edin
- yalnızca gerçek kullanım azalınca ve fixture kapsamı geçiş güvenliğini kanıtlayınca kaldırın

### Uyumluluk sinyalleri

`openclaw doctor` veya `openclaw plugins inspect <id>` çalıştırdığınızda,
şu etiketlerden birini görebilirsiniz:

| Sinyal                     | Anlamı                                                     |
| -------------------------- | ---------------------------------------------------------- |
| **config valid**           | Yapılandırma sorunsuz ayrıştırılır ve plugin'ler çözülür   |
| **compatibility advisory** | Plugin desteklenen ama daha eski bir desen kullanır (örn. `hook-only`) |
| **legacy warning**         | Plugin, kullanımdan kaldırılmış `before_agent_start` kullanır |
| **hard error**             | Yapılandırma geçersizdir veya plugin yüklenememiştir       |

Ne `hook-only` ne de `before_agent_start` bugün plugin'inizi bozmaz --
`hook-only` tavsiye niteliğindedir ve `before_agent_start` yalnızca bir uyarı üretir. Bu
sinyaller ayrıca `openclaw status --all` ve `openclaw plugins doctor` içinde de görünür.

## Mimari genel bakış

OpenClaw'ın plugin sistemi dört katmandan oluşur:

1. **Manifest + keşif**
   OpenClaw, yapılandırılmış yollar, çalışma alanı kökleri,
   genel uzantı kökleri ve paketlenmiş uzantılardan aday plugin'leri bulur. Keşif önce yerel
   `openclaw.plugin.json` manifestlerini ve desteklenen paket manifestlerini okur.
2. **Etkinleştirme + doğrulama**
   Çekirdek, keşfedilen bir plugin'in etkin mi, devre dışı mı, engelli mi olduğunu veya
   bellek gibi özel bir yuva için seçilip seçilmediğini belirler.
3. **Çalışma zamanı yükleme**
   Yerel OpenClaw plugin'leri jiti aracılığıyla süreç içinde yüklenir ve
   yetenekleri merkezi bir kayıt defterine kaydeder. Uyumlu paketler, çalışma zamanı kodu içe aktarılmadan
   kayıt defteri kayıtlarına normalize edilir.
4. **Yüzey tüketimi**
   OpenClaw'ın geri kalanı, araçları, kanalları, sağlayıcı
   kurulumunu, hook'ları, HTTP rotalarını, CLI komutlarını ve hizmetleri açığa çıkarmak için kayıt defterini okur.

Özellikle plugin CLI için, kök komut keşfi iki aşamaya ayrılır:

- ayrıştırma zamanı meta verisi `registerCli(..., { descriptors: [...] })` içinden gelir
- gerçek plugin CLI modülü tembel kalabilir ve ilk çağrıda kayıt olabilir

Bu, kök komut adlarını ayrıştırmadan önce OpenClaw'ın ayırmasına izin verirken
plugin'e ait CLI kodunu plugin içinde tutar.

Önemli tasarım sınırı:

- keşif + yapılandırma doğrulaması, plugin kodu çalıştırılmadan **manifest/şema meta verisi**
  üzerinden çalışabilmelidir
- yerel çalışma zamanı davranışı, plugin modülünün `register(api)` yolundan gelir

Bu ayrım, tam çalışma zamanı etkinleşmeden önce OpenClaw'ın yapılandırmayı doğrulamasını,
eksik/devre dışı plugin'leri açıklamasını ve UI/şema ipuçları oluşturmasını sağlar.

### Kanal plugin'leri ve paylaşılan mesaj aracı

Kanal plugin'lerinin, normal sohbet işlemleri için ayrı bir gönder/düzenle/tepki aracı kaydetmesi gerekmez.
OpenClaw çekirdekte tek bir paylaşılan `message` aracını tutar ve kanal plugin'leri bunun arkasındaki
kanala özgü keşif ve yürütmenin sahibidir.

Mevcut sınır:

- çekirdek, paylaşılan `message` araç host'unun, istem bağlamasının, oturum/ileti dizisi
  kaydının ve yürütme dağıtımının sahibidir
- kanal plugin'leri kapsamlı işlem keşfi, yetenek keşfi ve
  kanala özgü tüm şema parçalarının sahibidir
- kanal plugin'leri, sohbet kimliklerinin ileti dizisi kimliklerini nasıl kodladığı veya
  üst sohbetlerden nasıl miras aldığı gibi sağlayıcıya özgü oturum konuşma dil bilgisinin sahibidir
- kanal plugin'leri son işlemi kendi işlem bağdaştırıcıları üzerinden yürütür

Kanal plugin'leri için SDK yüzeyi
`ChannelMessageActionAdapter.describeMessageTool(...)` şeklindedir. Bu birleşik keşif çağrısı, bir plugin'in
görünür işlemlerini, yeteneklerini ve şema katkılarını birlikte döndürmesini sağlar;
böylece bu parçalar birbirinden kopmaz.

Çekirdek, çalışma zamanı kapsamını bu keşif adımına geçirir. Önemli alanlar şunları içerir:

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- güvenilen gelen `requesterSenderId`

Bu, bağlama duyarlı plugin'ler için önemlidir. Bir kanal, etkin hesaba,
mevcut odaya/ileti dizisine/mesaja veya güvenilir istekte bulunan kimliğine göre
çekirdek `message` aracında kanala özgü dallar kodlamadan mesaj işlemlerini gizleyebilir veya açığa çıkarabilir.

Bu nedenle gömülü-runner yönlendirme değişiklikleri hâlâ plugin işidir: runner,
paylaşılan `message` aracının mevcut tur için doğru kanala ait yüzeyi açığa çıkarması için
mevcut sohbet/oturum kimliğini plugin keşif sınırına iletmekten sorumludur.

Kanala ait yürütme yardımcıları için, paketlenmiş plugin'ler yürütme
çalışma zamanını kendi uzantı modülleri içinde tutmalıdır. Çekirdek artık
`src/agents/tools` altında Discord, Slack, Telegram veya WhatsApp mesaj-işlem çalışma zamanlarının sahibi değildir.
Ayrı `plugin-sdk/*-action-runtime` alt yolları yayımlamıyoruz ve paketlenmiş
plugin'ler kendi yerel çalışma zamanı kodlarını doğrudan kendi
uzantı modüllerinden içe aktarmalıdır.

Aynı sınır genel olarak sağlayıcı adlandırılmış SDK yüzeyleri için de geçerlidir:
çekirdek, Slack, Discord, Signal,
WhatsApp veya benzeri uzantılar için kanala özgü kolaylık barrel'lerini içe aktarmamalıdır.
Çekirdeğin bir davranışa ihtiyacı varsa, ya paketlenmiş plugin'in kendi
`api.ts` / `runtime-api.ts` barrel'ini tüketmeli ya da bu ihtiyacı
paylaşılan SDK'da dar bir genel yetenek haline getirmelidir.

Özellikle anketler için iki yürütme yolu vardır:

- `outbound.sendPoll`, ortak
  anket modeline uyan kanallar için paylaşılan taban davranıştır
- `actions.handleAction("poll")`, kanala özgü
  anket anlambilimi veya ek anket parametreleri için tercih edilen yoldur

Çekirdek artık, plugin'e ait anket işleyicileri generic anket ayrıştırıcısı tarafından
önce engellenmeden kanala özgü anket alanlarını kabul edebilsin diye, paylaşılan anket ayrıştırmasını
plugin anket dağıtımı işlemi reddettikten sonraya erteler.

Tam başlangıç sırası için [Yükleme hattı](#load-pipeline) bölümüne bakın.

## Yetenek sahiplik modeli

OpenClaw, yerel bir plugin'i ilgisiz entegrasyonların
karma bir torbası olarak değil, bir **şirketin** veya bir
**özelliğin** sahiplik sınırı olarak ele alır.

Bu şu anlama gelir:

- bir şirket plugin'i genellikle o şirketin tüm OpenClaw'a dönük
  yüzeylerinin sahibi olmalıdır
- bir özellik plugin'i genellikle getirdiği tam özellik yüzeyinin sahibi olmalıdır
- kanallar, sağlayıcı davranışını geçici olarak yeniden uygulamak yerine paylaşılan çekirdek yetenekleri tüketmelidir

Örnekler:

- paketlenmiş `openai` plugin'i OpenAI model-sağlayıcı davranışının ve OpenAI
  konuşma + gerçek zamanlı ses + medya anlama + görsel üretimi davranışının sahibidir
- paketlenmiş `elevenlabs` plugin'i ElevenLabs konuşma davranışının sahibidir
- paketlenmiş `microsoft` plugin'i Microsoft konuşma davranışının sahibidir
- paketlenmiş `google` plugin'i Google model-sağlayıcı davranışının yanı sıra Google
  medya anlama + görsel üretimi + web arama davranışının sahibidir
- paketlenmiş `firecrawl` plugin'i Firecrawl web-getirme davranışının sahibidir
- paketlenmiş `minimax`, `mistral`, `moonshot` ve `zai` plugin'leri kendi
  medya anlama arka uçlarının sahibidir
- paketlenmiş `qwen` plugin'i Qwen metin-sağlayıcı davranışının yanı sıra
  medya anlama ve video üretimi davranışının sahibidir
- `voice-call` plugin'i bir özellik plugin'idir: çağrı taşıma katmanının, araçların,
  CLI'ın, rotaların ve Twilio medya-akışı köprülemesinin sahibidir; ancak satıcı plugin'lerini doğrudan
  içe aktarmak yerine paylaşılan konuşma ile gerçek zamanlı transkripsiyon ve gerçek zamanlı ses yeteneklerini tüketir

Amaçlanan son durum şudur:

- OpenAI, metin modelleri, konuşma, görseller ve
  gelecekteki video alanlarını kapsasa bile tek bir plugin içinde yaşar
- başka bir satıcı kendi yüzey alanı için aynı şeyi yapabilir
- kanallar, sağlayıcının hangi satıcı plugin'ine ait olduğunu umursamaz; çekirdeğin açığa çıkardığı
  paylaşılan yetenek sözleşmesini tüketir

Temel ayrım budur:

- **plugin** = sahiplik sınırı
- **yetenek** = birden fazla plugin'in uygulayabileceği veya tüketebileceği çekirdek sözleşme

Dolayısıyla OpenClaw videoya benzer yeni bir alan eklerse ilk soru
"hangi sağlayıcı video işlemeyi sabit kodlamalı?" değildir. İlk soru
"çekirdek video yetenek sözleşmesi nedir?" olmalıdır. Bu sözleşme var olduğunda,
satıcı plugin'leri buna karşı kayıt olabilir ve kanal/özellik plugin'leri bunu tüketebilir.

Yetenek henüz yoksa doğru adım genellikle şudur:

1. eksik yeteneği çekirdekte tanımlayın
2. bunu plugin API'si/çalışma zamanı üzerinden türlenmiş şekilde açığa çıkarın
3. kanalları/özellikleri bu yeteneğe karşı bağlayın
4. satıcı plugin'lerinin uygulamalar kaydetmesine izin verin

Bu, sahipliği açık tutarken çekirdek davranışın tek bir satıcıya veya
tek seferlik plugin'e özgü bir kod yoluna bağımlı olmasını önler.

### Yetenek katmanlaması

Kodun nereye ait olduğuna karar verirken şu zihinsel modeli kullanın:

- **çekirdek yetenek katmanı**: paylaşılan orkestrasyon, ilke, fallback, yapılandırma
  birleştirme kuralları, teslimat anlambilimi ve türlenmiş sözleşmeler
- **satıcı plugin katmanı**: satıcıya özgü API'ler, kimlik doğrulama, model katalogları, konuşma
  sentezi, görsel üretimi, gelecekteki video arka uçları, kullanım uç noktaları
- **kanal/özellik plugin katmanı**: Slack/Discord/voice-call/vb. entegrasyonu;
  çekirdek yetenekleri tüketir ve bunları bir yüzey üzerinde sunar

Örneğin TTS şu yapıyı izler:

- çekirdek, yanıt zamanı TTS ilkesinin, fallback sırasının, tercihlerin ve kanal teslimatının sahibidir
- `openai`, `elevenlabs` ve `microsoft`, sentez uygulamalarının sahibidir
- `voice-call`, telefon TTS çalışma zamanı yardımcısını tüketir

Gelecekteki yetenekler için de aynı desen tercih edilmelidir.

### Çok yetenekli şirket plugin'i örneği

Bir şirket plugin'i dışarıdan tutarlı görünmelidir. OpenClaw; modeller, konuşma,
gerçek zamanlı transkripsiyon, gerçek zamanlı ses, medya anlama,
görsel üretimi, video üretimi, web getirme ve web arama için paylaşılan
sözleşmelere sahipse, bir satıcı tüm yüzeylerinin sahibi tek yerde olabilir:

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

Önemli olan tam yardımcı adları değildir. Önemli olan yapı:

- tek bir plugin satıcı yüzeyinin sahibidir
- çekirdek yine de yetenek sözleşmelerinin sahibidir
- kanallar ve özellik plugin'leri satıcı kodunu değil `api.runtime.*` yardımcılarını tüketir
- sözleşme testleri, plugin'in sahip olduğunu iddia ettiği yetenekleri kaydettiğini doğrulayabilir

### Yetenek örneği: video anlama

OpenClaw hâlihazırda görsel/ses/video anlamayı tek bir paylaşılan
yetenek olarak ele alır. Aynı sahiplik modeli burada da geçerlidir:

1. çekirdek medya-anlama sözleşmesini tanımlar
2. satıcı plugin'leri uygun olduğunda `describeImage`, `transcribeAudio` ve
   `describeVideo` kaydeder
3. kanal ve özellik plugin'leri satıcı koduna doğrudan bağlanmak yerine
   paylaşılan çekirdek davranışı tüketir

Bu, bir sağlayıcının video varsayımlarının çekirdeğe gömülmesini önler. Plugin satıcı yüzeyinin;
çekirdek ise yetenek sözleşmesi ve fallback davranışının sahibidir.

Video üretimi de aynı sıralamayı zaten kullanır: çekirdek türlenmiş
yetenek sözleşmesinin ve çalışma zamanı yardımcısının sahibidir, satıcı plugin'leri ise
buna karşı `api.registerVideoGenerationProvider(...)` uygulamaları kaydeder.

Somut bir yaygınlaştırma kontrol listesine mi ihtiyacınız var? Bkz.
[Capability Cookbook](/tr/plugins/architecture).

## Sözleşmeler ve zorunlu uygulama

Plugin API yüzeyi, kasıtlı olarak türlenmiş ve
`OpenClawPluginApi` içinde merkezileştirilmiştir. Bu sözleşme, desteklenen kayıt noktalarını ve
bir plugin'in güvenebileceği çalışma zamanı yardımcılarını tanımlar.

Bunun önemi:

- plugin yazarları tek bir kararlı iç standart elde eder
- çekirdek, aynı sağlayıcı kimliğini iki plugin'in kaydetmesi gibi
  yinelenen sahipliği reddedebilir
- başlangıç, hatalı kayıtlar için uygulanabilir tanılama bilgileri gösterebilir
- sözleşme testleri, paketlenmiş plugin sahipliğini zorunlu kılabilir ve sessiz sapmaları önleyebilir

İki zorunlu uygulama katmanı vardır:

1. **çalışma zamanı kayıt zorunluluğu**
   Plugin kayıt defteri, plugin'ler yüklenirken kayıtları doğrular. Örnekler:
   yinelenen sağlayıcı kimlikleri, yinelenen konuşma sağlayıcı kimlikleri ve hatalı
   kayıtlar; tanımsız davranış yerine plugin tanılarına yol açar.
2. **sözleşme testleri**
   Paketlenmiş plugin'ler test çalıştırmaları sırasında sözleşme kayıt defterlerinde yakalanır; böylece
   OpenClaw sahipliği açıkça doğrulayabilir. Bugün bu model
   sağlayıcıları, konuşma sağlayıcılarını, web arama sağlayıcılarını ve paketlenmiş kayıt sahipliğini
   doğrulamak için kullanılır.

Pratik etkisi şudur: OpenClaw, hangi plugin'in hangi
yüzeyin sahibi olduğunu en baştan bilir. Bu, çekirdek ve kanalların sorunsuz
birleşmesine izin verir; çünkü sahiplik örtük değil, beyan edilmiş, türlenmiş ve test edilebilirdir.

### Bir sözleşmede neler yer almalıdır

İyi plugin sözleşmeleri şunlardır:

- türlenmiş
- küçük
- yeteneğe özgü
- çekirdeğe ait
- birden fazla plugin tarafından yeniden kullanılabilir
- satıcı bilgisi olmadan kanal/özellikler tarafından tüketilebilir

Kötü plugin sözleşmeleri şunlardır:

- çekirdekte gizlenen satıcıya özgü ilke
- kayıt defterini baypas eden tek seferlik plugin kaçış kapıları
- kanal kodunun doğrudan bir satıcı uygulamasına ulaşması
- `OpenClawPluginApi` veya
  `api.runtime` parçası olmayan geçici çalışma zamanı nesneleri

Kararsız kaldığınızda soyutlama seviyesini yükseltin: önce yeteneği tanımlayın, sonra
plugin'lerin buna eklenmesine izin verin.

## Yürütme modeli

Yerel OpenClaw plugin'leri Gateway ile **süreç içinde** çalışır. Sandbox içinde değildir.
Yüklenen bir yerel plugin, çekirdek kodla aynı süreç düzeyi güven sınırına sahiptir.

Sonuçlar:

- yerel bir plugin araçlar, ağ işleyicileri, hook'lar ve hizmetler kaydedebilir
- yerel bir plugin hatası gateway'i çökertebilir veya kararsızlaştırabilir
- kötü amaçlı bir yerel plugin, OpenClaw süreci içinde rastgele kod yürütmeye eşdeğerdir

Uyumlu paketler varsayılan olarak daha güvenlidir; çünkü OpenClaw şu anda bunları
meta veri/içerik paketleri olarak ele alır. Mevcut sürümlerde bu çoğunlukla paketlenmiş
Skills anlamına gelir.

Paketlenmemiş plugin'ler için allowlist ve açık kurulum/yükleme yolları kullanın. Çalışma alanı plugin'lerini
üretim varsayılanları değil, geliştirme zamanı kodu olarak ele alın.

Paketlenmiş çalışma alanı paket adları için plugin kimliğini npm
adında sabit tutun: varsayılan olarak `@openclaw/<id>` veya
paket kasıtlı olarak daha dar bir plugin rolü açığa çıkarıyorsa onaylı tür sonekleri
`-provider`, `-plugin`, `-speech`, `-sandbox` veya `-media-understanding`.

Önemli güven notu:

- `plugins.allow`, **plugin kimliklerine** güvenir; kaynak kökenine değil.
- Paketlenmiş bir plugin ile aynı kimliğe sahip bir çalışma alanı plugin'i,
  etkinleştirildiğinde/allowlist'e alındığında paketlenmiş kopyanın üstüne kasıtlı olarak yazar.
- Bu normaldir ve yerel geliştirme, yama testi ve hotfix'ler için faydalıdır.

## Dışa aktarma sınırı

OpenClaw, uygulama kolaylığı değil, yetenekleri dışa aktarır.

Yetenek kaydını genel tutun. Sözleşme dışı yardımcı dışa aktarımlarını azaltın:

- paketlenmiş plugin'e özgü yardımcı alt yollar
- genel API olarak amaçlanmayan çalışma zamanı altyapı alt yolları
- satıcıya özgü kolaylık yardımcıları
- uygulama ayrıntısı olan kurulum/onboarding yardımcıları

Bazı paketlenmiş plugin yardımcı alt yolları, uyumluluk ve paketlenmiş plugin bakım için
oluşturulmuş SDK dışa aktarma haritasında hâlâ kalmaktadır. Mevcut örnekler arasında
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` ve birkaç `plugin-sdk/matrix*` yüzeyi vardır. Bunları
yeni üçüncü taraf plugin'ler için önerilen SDK deseni olarak değil,
ayrılmış uygulama ayrıntısı dışa aktarımları olarak değerlendirin.

## Yükleme hattı

Başlangıçta OpenClaw kabaca şunları yapar:

1. aday plugin köklerini keşfeder
2. yerel veya uyumlu paket manifestlerini ve paket meta verisini okur
3. güvensiz adayları reddeder
4. plugin yapılandırmasını normalize eder (`plugins.enabled`, `allow`, `deny`, `entries`,
   `slots`, `load.paths`)
5. her aday için etkinleştirmeye karar verir
6. etkin yerel modülleri jiti aracılığıyla yükler
7. yerel `register(api)` (veya eski takma ad olarak `activate(api)`) hook'larını çağırır ve kayıtları plugin kayıt defterinde toplar
8. kayıt defterini komut/çalışma zamanı yüzeylerine açar

<Note>
`activate`, `register` için eski bir takma addır — yükleyici mevcut olanı (`def.register ?? def.activate`) çözümler ve aynı noktada çağırır. Tüm paketlenmiş plugin'ler `register` kullanır; yeni plugin'ler için `register` tercih edin.
</Note>

Güvenlik kapıları, çalışma zamanı yürütmesinden **önce** gerçekleşir. Girdi plugin kökünden kaçıyorsa,
yol herkes tarafından yazılabiliyorsa veya paketlenmemiş plugin'ler için yol sahipliği şüpheli görünüyorsa adaylar engellenir.

### Önce manifest davranışı

Manifest, kontrol düzleminin tek doğruluk kaynağıdır. OpenClaw bunu şu amaçlarla kullanır:

- plugin'i tanımlamak
- beyan edilen kanalları/Skills/yapılandırma şemasını veya paket yeteneklerini keşfetmek
- `plugins.entries.<id>.config` değerini doğrulamak
- Control UI etiketlerini/yer tutucularını zenginleştirmek
- kurulum/katalog meta verilerini göstermek

Yerel plugin'ler için çalışma zamanı modülü veri düzlemi kısmıdır. Bu modül hook'lar, araçlar, komutlar veya sağlayıcı akışları gibi
gerçek davranışları kaydeder.

### Yükleyicinin önbelleğe aldığı şeyler

OpenClaw şu şeyler için kısa süreli süreç içi önbellekler tutar:

- keşif sonuçları
- manifest kayıt defteri verileri
- yüklenmiş plugin kayıt defterleri

Bu önbellekler, ani başlangıç yükünü ve tekrarlanan komut maliyetini azaltır. Bunları
kalıcılık değil, kısa ömürlü performans önbellekleri olarak düşünmek güvenlidir.

Performans notu:

- Bu önbellekleri devre dışı bırakmak için `OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` veya
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1` ayarlayın.
- Önbellek pencerelerini `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` ve
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS` ile ayarlayın.

## Kayıt defteri modeli

Yüklenen plugin'ler rastgele çekirdek globalleri doğrudan değiştirmez. Bunun yerine merkezi bir
plugin kayıt defterine kayıt olurlar.

Kayıt defteri şunları izler:

- plugin kayıtları (kimlik, kaynak, köken, durum, tanılar)
- araçlar
- eski hook'lar ve türlenmiş hook'lar
- kanallar
- sağlayıcılar
- gateway RPC işleyicileri
- HTTP rotaları
- CLI kayıtçıları
- arka plan hizmetleri
- plugin'e ait komutlar

Çekirdek özellikler daha sonra plugin modülleriyle doğrudan konuşmak yerine bu kayıt defterinden okur.
Bu, yüklemenin tek yönlü kalmasını sağlar:

- plugin modülü -> kayıt defteri kaydı
- çekirdek çalışma zamanı -> kayıt defteri tüketimi

Bu ayrım bakım yapılabilirlik açısından önemlidir. Çoğu çekirdek yüzeyin
"her plugin modülü için özel durum yaz" yerine yalnızca bir entegrasyon noktasına, yani
"kayıt defterini oku" yaklaşımına ihtiyaç duyması anlamına gelir.

## Sohbet bağlama geri çağrıları

Bir sohbet bağlayan plugin'ler, bir onay çözüldüğünde tepki verebilir.

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
- `binding`: onaylanmış istekler için çözülmüş bağlama
- `request`: özgün istek özeti, ayırma ipucu, gönderen kimliği ve
  sohbet meta verisi

Bu geri çağrı yalnızca bildirim amaçlıdır. Bir sohbeti kimin bağlayabileceğini değiştirmez
ve çekirdeğin onay işlemesi tamamlandıktan sonra çalışır.

## Sağlayıcı çalışma zamanı hook'ları

Sağlayıcı plugin'lerinin artık iki katmanı vardır:

- manifest meta verisi: çalışma zamanı yüklenmeden önce ucuz env-auth araması için `providerAuthEnvVars`,
  ayrıca çalışma zamanı yüklenmeden önce ucuz onboarding/auth-choice
  etiketleri ve CLI bayrak meta verisi için `providerAuthChoices`
- yapılandırma zamanı hook'ları: `catalog` / eski `discovery` artı `applyConfigDefaults`
- çalışma zamanı hook'ları: `normalizeModelId`, `normalizeTransport`,
  `normalizeConfig`,
  `applyNativeStreamingUsageCompat`, `resolveConfigApiKey`,
  `resolveSyntheticAuth`, `shouldDeferSyntheticProfileAuth`,
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

OpenClaw hâlâ genel ajan döngüsünün, failover'ın, transcript işlemenin ve
araç ilkesinin sahibidir. Bu hook'lar, tamamen özel bir çıkarım taşıma katmanına ihtiyaç duymadan
sağlayıcıya özgü davranış için uzantı yüzeyidir.

Sağlayıcı, genel auth/durum/model-seçici yollarının
plugin çalışma zamanını yüklemeden görmesi gereken env tabanlı kimlik bilgilerine sahipse manifest
`providerAuthEnvVars` kullanın. Onboarding/auth-choice CLI
yüzeylerinin sağlayıcının seçim kimliğini, grup etiketlerini ve basit
tek bayraklı auth bağlantısını çalışma zamanı yüklenmeden bilmesi gerekiyorsa manifest
`providerAuthChoices` kullanın. Operatöre dönük ipuçları; örneğin onboarding etiketleri veya OAuth
client-id/client-secret kurulum değişkenleri için sağlayıcı çalışma zamanı
`envVars` değerini koruyun.

### Hook sırası ve kullanım

Model/sağlayıcı plugin'leri için OpenClaw bu hook'ları kabaca şu sırada çağırır.
"Ne zaman kullanılır" sütunu hızlı karar kılavuzudur.

| #   | Hook                              | Ne yapar                                                                                 | Ne zaman kullanılır                                                                                                                         |
| --- | --------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `catalog`                         | `models.json` üretimi sırasında sağlayıcı yapılandırmasını `models.providers` içinde yayımlar | Sağlayıcı bir kataloğun veya temel URL varsayılanlarının sahibiyse                                                                          |
| 2   | `applyConfigDefaults`             | Yapılandırma somutlaştırması sırasında sağlayıcıya ait genel yapılandırma varsayılanlarını uygular | Varsayılanlar auth modu, env veya sağlayıcı model ailesi anlambilimine bağlıysa                                                             |
| --  | _(yerleşik model araması)_        | OpenClaw önce normal kayıt defteri/katalog yolunu dener                                  | _(plugin hook'u değil)_                                                                                                                     |
| 3   | `normalizeModelId`                | Aramadan önce eski veya önizleme model kimliği takma adlarını normalize eder            | Sağlayıcı, kanonik model çözümlemeden önce takma ad temizliğinin sahibiyse                                                                  |
| 4   | `normalizeTransport`              | Genel model birleştirmeden önce sağlayıcı ailesi `api` / `baseUrl` değerini normalize eder | Sağlayıcı, aynı taşıma ailesindeki özel sağlayıcı kimlikleri için taşıma temizliğinin sahibiyse                                           |
| 5   | `normalizeConfig`                 | Çalışma zamanı/sağlayıcı çözümlemesinden önce `models.providers.<id>` değerini normalize eder | Plugin ile yaşaması gereken yapılandırma temizliği gerekiyorsa; paketlenmiş Google ailesi yardımcıları desteklenen Google yapılandırma girdilerini de arka planda düzeltir |
| 6   | `applyNativeStreamingUsageCompat` | Yapılandırma sağlayıcılarına yerel streaming-usage uyumluluk yeniden yazımlarını uygular | Sağlayıcının, uç nokta kaynaklı yerel streaming usage meta verisi düzeltmelerine ihtiyacı varsa                                            |
| 7   | `resolveConfigApiKey`             | Çalışma zamanı auth yüklemesinden önce yapılandırma sağlayıcıları için env-marker auth'u çözümler | Sağlayıcının kendi env-marker API anahtarı çözümlemesi varsa; `amazon-bedrock` da burada yerleşik AWS env-marker çözücüye sahiptir        |
| 8   | `resolveSyntheticAuth`            | Düz metin saklamadan yerel/self-hosted veya yapılandırma destekli auth'u açığa çıkarır  | Sağlayıcı sentetik/yerel bir kimlik bilgisi işaretleyicisiyle çalışabiliyorsa                                                               |
| 9   | `shouldDeferSyntheticProfileAuth` | Saklanan sentetik profil yer tutucularını env/yapılandırma destekli auth'un arkasına indirir | Sağlayıcı, öncelik kazanmaması gereken sentetik yer tutucu profiller saklıyorsa                                                             |
| 10  | `resolveDynamicModel`             | Henüz yerel kayıt defterinde olmayan sağlayıcıya ait model kimlikleri için eşzamanlı fallback | Sağlayıcı keyfi upstream model kimliklerini kabul ediyorsa                                                                                  |
| 11  | `prepareDynamicModel`             | Eşzamansız ısınma yapar, sonra `resolveDynamicModel` tekrar çalışır                      | Sağlayıcı bilinmeyen kimlikleri çözmeden önce ağ meta verisine ihtiyaç duyuyorsa                                                            |
| 12  | `normalizeResolvedModel`          | Gömülü runner çözülmüş modeli kullanmadan önce son yeniden yazımı yapar                 | Sağlayıcı taşıma yeniden yazımlarına ihtiyaç duyuyor ama yine de çekirdek bir taşıma kullanıyorsa                                          |
| 13  | `contributeResolvedModelCompat`   | Başka bir uyumlu taşıma arkasındaki satıcı modelleri için uyumluluk bayrakları katkısı yapar | Sağlayıcı kendi modellerini sağlayıcıyı devralmadan proxy taşımalarda tanıyorsa                                                            |
| 14  | `capabilities`                    | Paylaşılan çekirdek mantığı tarafından kullanılan sağlayıcıya ait transcript/tooling meta verisi | Sağlayıcının transcript/sağlayıcı ailesi tuhaflıklarına ihtiyacı varsa                                                                      |
| 15  | `normalizeToolSchemas`            | Gömülü runner görmeden önce araç şemalarını normalize eder                              | Sağlayıcı taşıma ailesi şema temizliğine ihtiyaç duyuyorsa                                                                                  |
| 16  | `inspectToolSchemas`              | Normalizasyondan sonra sağlayıcıya ait şema tanılarını açığa çıkarır                    | Sağlayıcı, çekirdeğe sağlayıcıya özgü kurallar öğretmeden anahtar sözcük uyarıları istiyorsa                                              |
| 17  | `resolveReasoningOutputMode`      | Yerel ile etiketli reasoning-output sözleşmesi arasında seçim yapar                     | Sağlayıcı, yerel alanlar yerine etiketli reasoning/final output'a ihtiyaç duyuyorsa                                                        |
| 18  | `prepareExtraParams`              | Genel akış seçenek sarmalayıcılarından önce istek parametresi normalizasyonu            | Sağlayıcı varsayılan istek parametrelerine veya sağlayıcı başına parametre temizliğine ihtiyaç duyuyorsa                                  |
| 19  | `createStreamFn`                  | Normal akış yolunu tamamen özel bir taşıma ile değiştirir                               | Sağlayıcı yalnızca sarmalayıcı değil, özel bir wire protocol'e ihtiyaç duyuyorsa                                                            |
| 20  | `wrapStreamFn`                    | Genel sarmalayıcılar uygulandıktan sonra akış sarmalayıcısı                             | Sağlayıcı özel bir taşıma olmadan istek başlıkları/gövdesi/model uyumluluk sarmalayıcılarına ihtiyaç duyuyorsa                             |
| 21  | `resolveTransportTurnState`       | Yerel tur başına taşıma başlıkları veya meta veri ekler                                 | Sağlayıcı genel taşımalara sağlayıcıya özgü tur kimliği göndermek istiyorsa                                                                 |
| 22  | `resolveWebSocketSessionPolicy`   | Yerel WebSocket başlıkları veya oturum soğuma ilkesi ekler                              | Sağlayıcı genel WS taşımalarında oturum başlıklarını veya fallback ilkesini ayarlamak istiyorsa                                            |
| 23  | `formatApiKey`                    | Auth-profil biçimlendirici: saklanan profil çalışma zamanı `apiKey` dizgesine dönüşür   | Sağlayıcı ek auth meta verisi saklıyor ve özel bir çalışma zamanı token biçimine ihtiyaç duyuyorsa                                         |
| 24  | `refreshOAuth`                    | Özel yenileme uç noktaları veya yenileme başarısızlığı ilkesi için OAuth yenileme geçersiz kılması | Sağlayıcı paylaşılan `pi-ai` yenileyicilerine uymuyorsa                                                                                     |
| 25  | `buildAuthDoctorHint`             | OAuth yenilemesi başarısız olduğunda eklenecek onarım ipucu oluşturur                   | Sağlayıcının, yenileme başarısızlığından sonra kendine ait auth onarım kılavuzuna ihtiyacı varsa                                           |
| 26  | `matchesContextOverflowError`     | Sağlayıcıya ait bağlam penceresi aşımı eşleştiricisi                                    | Sağlayıcının, genel buluşsal yöntemlerin kaçıracağı ham taşma hataları varsa                                                               |
| 27  | `classifyFailoverReason`          | Sağlayıcıya ait failover nedeni sınıflandırması                                         | Sağlayıcı ham API/taşıma hatalarını oran sınırı/aşırı yük/vb. olarak eşleyebiliyorsa                                                       |
| 28  | `isCacheTtlEligible`              | Proxy/backhaul sağlayıcıları için istem önbelleği ilkesi                               | Sağlayıcı proxy'ye özgü önbellek TTL kapılamasına ihtiyaç duyuyorsa                                                                         |
| 29  | `buildMissingAuthMessage`         | Genel eksik auth kurtarma mesajının yerine geçer                                        | Sağlayıcının sağlayıcıya özgü eksik auth kurtarma ipucuna ihtiyacı varsa                                                                   |
| 30  | `suppressBuiltInModel`            | Bayat upstream model bastırma ve isteğe bağlı kullanıcıya dönük hata ipucu              | Sağlayıcı bayat upstream satırları gizlemek veya bunları satıcı ipucuyla değiştirmek istiyorsa                                             |
| 31  | `augmentModelCatalog`             | Keşiften sonra sentetik/nihai katalog satırlarını ekler                                 | Sağlayıcının `models list` ve seçiciler içinde sentetik ileri uyum satırlarına ihtiyacı varsa                                              |
| 32  | `isBinaryThinking`                | İkili düşünme sağlayıcıları için aç/kapat reasoning geçişi                              | Sağlayıcı yalnızca ikili düşünme aç/kapat sunuyorsa                                                                                        |
| 33  | `supportsXHighThinking`           | Seçili modeller için `xhigh` reasoning desteği                                          | Sağlayıcı yalnızca model alt kümesinde `xhigh` istiyorsa                                                                                    |
| 34  | `resolveDefaultThinkingLevel`     | Belirli bir model ailesi için varsayılan `/think` seviyesi                              | Sağlayıcı, model ailesi için varsayılan `/think` ilkesinin sahibiyse                                                                        |
| 35  | `isModernModelRef`                | Canlı profil filtreleri ve smoke seçimi için modern model eşleştiricisi                 | Sağlayıcı canlı/smoke tercih edilen model eşlemesinin sahibiyse                                                                             |
| 36  | `prepareRuntimeAuth`              | Çıkarımdan hemen önce yapılandırılmış bir kimlik bilgisini gerçek çalışma zamanı token/anahtarına dönüştürür | Sağlayıcı token değişimi veya kısa ömürlü istek kimlik bilgisine ihtiyaç duyuyorsa                                                         |
| 37  | `resolveUsageAuth`                | `/usage` ve ilgili durum yüzeyleri için kullanım/faturalama kimlik bilgilerini çözümler | Sağlayıcı özel kullanım/kota token ayrıştırmasına veya farklı bir kullanım kimlik bilgisine ihtiyaç duyuyorsa                              |
| 38  | `fetchUsageSnapshot`              | Auth çözüldükten sonra sağlayıcıya özgü kullanım/kota anlık görüntülerini getirip normalize eder | Sağlayıcıya özgü bir kullanım uç noktasına veya yük ayrıştırıcısına ihtiyaç duyuyorsa                                                      |
| 39  | `createEmbeddingProvider`         | Bellek/arama için sağlayıcıya ait embedding bağdaştırıcısı oluşturur                    | Bellek embedding davranışı sağlayıcı plugin'iyle birlikte olmalıdır                                                                         |
| 40  | `buildReplayPolicy`               | Sağlayıcı için transcript işleme kontrolü yapan bir replay ilkesi döndürür              | Sağlayıcı özel transcript ilkesine ihtiyaç duyuyorsa (örneğin düşünme bloklarını ayıklama)                                                 |
| 41  | `sanitizeReplayHistory`           | Genel transcript temizliğinden sonra replay geçmişini yeniden yazar                     | Sağlayıcı paylaşılan sıkıştırma yardımcılarının ötesinde sağlayıcıya özgü replay yeniden yazımlarına ihtiyaç duyuyorsa                     |
| 42  | `validateReplayTurns`             | Gömülü runner öncesi son replay-tur doğrulaması veya yeniden şekillendirme              | Sağlayıcı taşımasının genel sanitasyondan sonra daha sıkı tur doğrulamasına ihtiyacı varsa                                                  |
| 43  | `onModelSelected`                 | Sağlayıcıya ait seçim sonrası yan etkileri çalıştırır                                   | Bir model etkin olduğunda sağlayıcının telemetriye veya sağlayıcıya ait duruma ihtiyacı varsa                                              |

`normalizeModelId`, `normalizeTransport` ve `normalizeConfig` önce
eşleşen sağlayıcı plugin'ini kontrol eder, ardından model kimliğini veya taşıma/yapılandırmayı
gerçekte değiştiren biri olana kadar hook destekli diğer sağlayıcı plugin'lerine düşer. Bu,
çağıranın hangi paketlenmiş plugin'in yeniden yazımın sahibi olduğunu bilmesini gerektirmeden
takma ad/uyumluluk sağlayıcı shim'lerinin çalışmasını sağlar. Hiçbir sağlayıcı hook'u desteklenen bir
Google ailesi yapılandırma girdisini yeniden yazmazsa, paketlenmiş Google yapılandırma normalleştiricisi
bu uyumluluk temizliğini yine de uygular.

Sağlayıcının tamamen özel bir wire protocol'e veya özel bir istek yürütücüsüne ihtiyacı varsa,
bu farklı bir uzantı sınıfıdır. Bu hook'lar, hâlâ OpenClaw'ın normal çıkarım döngüsü üzerinde çalışan
sağlayıcı davranışı içindir.

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

- Anthropic; Claude 4.6 ileri uyumluluğunun,
  sağlayıcı ailesi ipuçlarının, auth onarım kılavuzunun, kullanım uç noktası entegrasyonunun,
  istem önbelleği uygunluğunun, auth farkındalıklı yapılandırma varsayılanlarının, Claude
  varsayılan/uyarlamalı düşünme ilkesinin ve beta başlıkları,
  `/fast` / `serviceTier` ve `context1m` için Anthropic'e özgü akış şekillendirmenin sahibi olduğu için
  `resolveDynamicModel`, `capabilities`, `buildAuthDoctorHint`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `isCacheTtlEligible`,
  `resolveDefaultThinkingLevel`, `applyConfigDefaults`, `isModernModelRef`
  ve `wrapStreamFn` kullanır.
- Anthropic'in Claude'a özgü akış yardımcıları şimdilik paketlenmiş plugin'in kendi
  genel `api.ts` / `contract-api.ts` yüzeyinde kalır. Bu paket yüzeyi,
  bir sağlayıcının beta-header kuralları etrafında genel SDK'yı genişletmek yerine
  `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
  `resolveAnthropicFastMode`, `resolveAnthropicServiceTier` ve alt düzey
  Anthropic sarmalayıcı oluşturucularını dışa aktarır.
- OpenAI; GPT-5.4 ileri uyumluluğunun, doğrudan OpenAI
  `openai-completions` -> `openai-responses` normalizasyonunun, Codex farkındalıklı auth
  ipuçlarının, Spark bastırmasının, sentetik OpenAI liste satırlarının ve GPT-5 düşünme /
  canlı model ilkesinin sahibi olduğu için `resolveDynamicModel`, `normalizeResolvedModel` ve
  `capabilities` ile birlikte `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `supportsXHighThinking` ve `isModernModelRef`
  kullanır; `openai-responses-defaults` akış ailesi ise ilişkilendirme başlıkları,
  `/fast`/`serviceTier`, metin ayrıntı seviyesi, yerel Codex web araması,
  reasoning-compat yük şekillendirme ve Responses bağlam yönetimi için
  paylaşılan yerel OpenAI Responses sarmalayıcılarının sahibidir.
- OpenRouter; sağlayıcı passthrough olduğundan ve OpenClaw'ın statik kataloğu güncellenmeden önce yeni
  model kimlikleri açığa çıkarabildiğinden `catalog` ile birlikte `resolveDynamicModel` ve
  `prepareDynamicModel` kullanır; ayrıca sağlayıcıya özgü istek başlıklarını,
  yönlendirme meta verisini, reasoning yamalarını ve
  istem önbelleği ilkesini çekirdek dışında tutmak için `capabilities`, `wrapStreamFn` ve `isCacheTtlEligible` kullanır. Replay ilkesi
  `passthrough-gemini` ailesinden gelirken, `openrouter-thinking` akış ailesi
  proxy reasoning enjeksiyonunun ve desteklenmeyen model / `auto` atlamalarının sahibidir.
- GitHub Copilot; sağlayıcıya ait aygıt girişi, model fallback davranışı, Claude transcript tuhaflıkları,
  GitHub token -> Copilot token değişimi ve sağlayıcıya ait kullanım uç noktası gerektiği için
  `catalog`, `auth`, `resolveDynamicModel` ve
  `capabilities` ile birlikte `prepareRuntimeAuth` ve `fetchUsageSnapshot` kullanır.
- OpenAI Codex; çekirdek OpenAI taşımaları üzerinde çalışmaya devam ettiği halde kendi taşıma/base URL
  normalizasyonunun, OAuth yenileme fallback ilkesinin, varsayılan taşıma seçiminin,
  sentetik Codex katalog satırlarının ve ChatGPT kullanım uç noktası entegrasyonunun sahibi olduğu için
  `catalog`, `resolveDynamicModel`,
  `normalizeResolvedModel`, `refreshOAuth` ve `augmentModelCatalog` ile birlikte
  `prepareExtraParams`, `resolveUsageAuth` ve `fetchUsageSnapshot` kullanır;
  doğrudan OpenAI ile aynı `openai-responses-defaults` akış ailesini paylaşır.
- Google AI Studio ve Gemini CLI OAuth; `google-gemini` replay ailesi Gemini 3.1 ileri uyumluluk fallback'inin,
  yerel Gemini replay doğrulamasının, bootstrap replay sanitasyonunun,
  etiketli reasoning-output modunun ve modern-model eşlemesinin sahibi olduğu için
  `resolveDynamicModel`,
  `buildReplayPolicy`, `sanitizeReplayHistory`,
  `resolveReasoningOutputMode`, `wrapStreamFn` ve `isModernModelRef` kullanır; ayrıca
  `google-thinking` akış ailesi Gemini düşünme yükü normalizasyonunun sahibidir;
  Gemini CLI OAuth ayrıca token biçimlendirme, token ayrıştırma ve kota uç noktası
  bağlantısı için `formatApiKey`, `resolveUsageAuth` ve
  `fetchUsageSnapshot` kullanır.
- Anthropic Vertex, Claude'a özgü replay temizliğinin her `anthropic-messages`
  taşımaya değil Claude kimliklerine özgü kalması için
  `anthropic-by-model` replay ailesi üzerinden `buildReplayPolicy` kullanır.
- Amazon Bedrock; Anthropic-on-Bedrock trafiği için Bedrock'a özgü throttle/not-ready/context-overflow
  hata sınıflandırmasının sahibi olduğu için
  `buildReplayPolicy`, `matchesContextOverflowError`,
  `classifyFailoverReason` ve `resolveDefaultThinkingLevel` kullanır;
  replay ilkesi yine aynı Claude-only `anthropic-by-model` korumasını paylaşır.
- OpenRouter, Kilocode, Opencode ve Opencode Go; Gemini
  modellerini OpenAI uyumlu taşımalar üzerinden proxy'ledikleri ve yerel Gemini replay doğrulaması veya
  bootstrap yeniden yazımları olmadan Gemini thought-signature sanitasyonuna ihtiyaç duydukları için
  `passthrough-gemini` replay ailesi üzerinden `buildReplayPolicy` kullanır.
- MiniMax; bir sağlayıcı hem Anthropic-message hem de OpenAI uyumlu anlambilimin sahibi olduğu için
  `hybrid-anthropic-openai` replay ailesi üzerinden `buildReplayPolicy`
  kullanır; Anthropic tarafında Claude-only
  thinking-block düşürmeyi korurken reasoning output modunu tekrar yerel moda geçirir ve
  `minimax-fast-mode` akış ailesi paylaşılan akış yolunda hızlı mod model yeniden yazımlarının sahibidir.
- Moonshot; paylaşılan OpenAI taşımayı kullanmaya devam ettiği halde sağlayıcıya ait düşünme yükü
  normalizasyonuna ihtiyaç duyduğu için `catalog` ile birlikte `wrapStreamFn` kullanır; `moonshot-thinking`
  akış ailesi, yapılandırmayı ve `/think` durumunu yerel ikili düşünme yüküne eşler.
- Kilocode; sağlayıcıya ait istek başlıkları,
  reasoning yükü normalizasyonu, Gemini transcript ipuçları ve Anthropic
  önbellek-TTL kapılamasına ihtiyaç duyduğu için `catalog`, `capabilities`, `wrapStreamFn` ve
  `isCacheTtlEligible` kullanır; `kilocode-thinking` akış ailesi,
  açık reasoning yüklerini desteklemeyen `kilo/auto` ve diğer proxy model kimliklerini atlayarak
  Kilo thinking enjeksiyonunu paylaşılan proxy akış yolunda tutar.
- Z.AI; GLM-5 fallback'inin,
  `tool_stream` varsayılanlarının, ikili thinking UX'inin, modern-model eşlemesinin ve hem
  kullanım auth'u hem kota getirme işleminin sahibi olduğu için `resolveDynamicModel`, `prepareExtraParams`, `wrapStreamFn`,
  `isCacheTtlEligible`, `isBinaryThinking`, `isModernModelRef`,
  `resolveUsageAuth` ve `fetchUsageSnapshot` kullanır; `tool-stream-default-on` akış ailesi,
  varsayılan açık `tool_stream` sarmalayıcısını sağlayıcı başına elle yazılmış yapıştırma kodunun dışında tutar.
- xAI; yerel xAI Responses taşıma normalizasyonunun, Grok fast-mode
  takma ad yeniden yazımlarının, varsayılan `tool_stream`'ün, strict-tool / reasoning-payload
  temizliğinin, plugin'e ait araçlar için fallback auth yeniden kullanımının, ileri uyumlu Grok
  model çözümlemesinin ve xAI araç-şema
  profili, desteklenmeyen şema anahtar sözcükleri, yerel `web_search` ve HTML-entity
  araç çağrısı bağımsız değişken çözümleme gibi sağlayıcıya ait uyumluluk yamalarının sahibi olduğu için
  `normalizeResolvedModel`, `normalizeTransport`,
  `contributeResolvedModelCompat`, `prepareExtraParams`, `wrapStreamFn`,
  `resolveSyntheticAuth`, `resolveDynamicModel` ve `isModernModelRef`
  kullanır.
- Mistral, OpenCode Zen ve OpenCode Go; transcript/tooling tuhaflıklarını çekirdeğin dışında tutmak için yalnızca `capabilities` kullanır.
- `byteplus`, `cloudflare-ai-gateway`,
  `huggingface`, `kimi-coding`, `nvidia`, `qianfan`,
  `synthetic`, `together`, `venice`, `vercel-ai-gateway` ve `volcengine` gibi
  yalnızca katalog sağlayan paketlenmiş sağlayıcılar yalnızca
  `catalog` kullanır.
- Qwen, metin sağlayıcısı için `catalog` ve çok modlu yüzeyleri için
  paylaşılan medya-anlama ile video üretimi kayıtlarını kullanır.
- MiniMax ve Xiaomi, çıkarım hâlâ paylaşılan taşımalar üzerinden çalışsa da `/usage`
  davranışları plugin'e ait olduğu için `catalog` ile birlikte kullanım hook'ları kullanır.

## Çalışma zamanı yardımcıları

Plugin'ler, `api.runtime` üzerinden seçili çekirdek yardımcılarına erişebilir. TTS için:

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
- PCM ses arabelleği + örnekleme hızı döndürür. Plugin'ler sağlayıcılar için yeniden örneklemeli/kodlamalıdır.
- `listVoices`, sağlayıcı başına isteğe bağlıdır. Bunu satıcıya ait ses seçicileri veya kurulum akışları için kullanın.
- Ses listeleri, sağlayıcı farkındalıklı seçiciler için yerel ayar, cinsiyet ve kişilik etiketleri gibi daha zengin meta veriler içerebilir.
- Bugün telefonu destekleyenler OpenAI ve ElevenLabs'tır. Microsoft desteklemez.

Plugin'ler ayrıca `api.registerSpeechProvider(...)` aracılığıyla konuşma sağlayıcıları kaydedebilir.

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

- TTS ilkesini, fallback'i ve yanıt teslimatını çekirdekte tutun.
- Satıcıya ait sentez davranışı için konuşma sağlayıcılarını kullanın.
- Eski Microsoft `edge` girdisi, `microsoft` sağlayıcı kimliğine normalize edilir.
- Tercih edilen sahiplik modeli şirket odaklıdır: OpenClaw bu
  yetenek sözleşmelerini ekledikçe tek bir satıcı plugin'i metin, konuşma, görsel ve gelecekteki medya sağlayıcılarının sahibi olabilir.

Görsel/ses/video anlama için plugin'ler,
genel bir anahtar/değer torbası yerine tek bir türlenmiş
medya-anlama sağlayıcısı kaydeder:

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

- Orkestrasyonu, fallback'i, yapılandırmayı ve kanal bağlantısını çekirdekte tutun.
- Satıcı davranışını sağlayıcı plugin'inde tutun.
- Toplamalı genişleme türlenmiş kalmalıdır: yeni isteğe bağlı yöntemler, yeni isteğe bağlı
  sonuç alanları, yeni isteğe bağlı yetenekler.
- Video üretimi zaten aynı deseni izler:
  - çekirdek yetenek sözleşmesinin ve çalışma zamanı yardımcısının sahibidir
  - satıcı plugin'leri `api.registerVideoGenerationProvider(...)` kaydeder
  - özellik/kanal plugin'leri `api.runtime.videoGeneration.*` tüketir

Medya-anlama çalışma zamanı yardımcıları için plugin'ler şunu çağırabilir:

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

Ses transkripsiyonu için plugin'ler ya medya-anlama çalışma zamanını
ya da daha eski STT takma adını kullanabilir:

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
- Çekirdek medya-anlama ses yapılandırmasını (`tools.media.audio`) ve sağlayıcı fallback sırasını kullanır.
- Hiçbir transkripsiyon çıktısı üretilmediğinde `{ text: undefined }` döndürür (örneğin atlanan/desteklenmeyen girdi).
- `api.runtime.stt.transcribeAudioFile(...)`, uyumluluk takma adı olarak kalır.

Plugin'ler ayrıca `api.runtime.subagent` aracılığıyla arka plan alt ajan çalıştırmaları da başlatabilir:

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
- OpenClaw bu geçersiz kılma alanlarını yalnızca güvenilen çağıranlar için dikkate alır.
- Plugin'e ait fallback çalıştırmaları için operatörlerin `plugins.entries.<id>.subagent.allowModelOverride: true` ile açıkça izin vermesi gerekir.
- Güvenilen plugin'leri belirli kanonik `provider/model` hedefleriyle sınırlamak için `plugins.entries.<id>.subagent.allowedModels`, herhangi bir hedefe açıkça izin vermek için ise `"*"` kullanın.
- Güvenilmeyen plugin alt ajan çalıştırmaları yine de çalışır, ancak geçersiz kılma istekleri sessizce fallback yapmak yerine reddedilir.

Web arama için plugin'ler,
ajan araç bağlantısına uzanmak yerine paylaşılan çalışma zamanı yardımcısını tüketebilir:

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
`api.registerWebSearchProvider(...)` aracılığıyla web-arama sağlayıcıları kaydedebilir.

Notlar:

- Sağlayıcı seçimini, kimlik bilgisi çözümlemesini ve paylaşılan istek anlambilimini çekirdekte tutun.
- Satıcıya özgü arama taşımaları için web-arama sağlayıcılarını kullanın.
- `api.runtime.webSearch.*`, ajan araç sarmalayıcısına bağımlı olmadan arama davranışına ihtiyaç duyan özellik/kanal plugin'leri için tercih edilen paylaşılan yüzeydir.

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
- `auth`: zorunlu. Normal gateway auth istemek için `"gateway"`, plugin tarafından yönetilen auth/webhook doğrulaması için `"plugin"` kullanın.
- `match`: isteğe bağlı. `"exact"` (varsayılan) veya `"prefix"`.
- `replaceExisting`: isteğe bağlı. Aynı plugin'in kendi mevcut rota kaydını değiştirmesine izin verir.
- `handler`: rota isteği işlediyse `true` döndürmelidir.

Notlar:

- `api.registerHttpHandler(...)` kaldırıldı ve plugin yükleme hatasına yol açar. Bunun yerine `api.registerHttpRoute(...)` kullanın.
- Plugin rotaları `auth` değerini açıkça beyan etmelidir.
- Tam `path + match` çakışmaları, `replaceExisting: true` olmadıkça reddedilir ve bir plugin başka bir plugin'in rotasını değiştiremez.
- Farklı `auth` seviyelerine sahip örtüşen rotalar reddedilir. `exact`/`prefix` geçiş zincirlerini yalnızca aynı auth seviyesinde tutun.
- `auth: "plugin"` rotaları otomatik olarak operatör çalışma zamanı kapsamları almaz. Bunlar ayrıcalıklı Gateway yardımcı çağrıları için değil, plugin tarafından yönetilen webhook/imza doğrulaması içindir.
- `auth: "gateway"` rotaları bir Gateway istek çalışma zamanı kapsamı içinde çalışır, ancak bu kapsam kasıtlı olarak muhafazakârdır:
  - paylaşılan gizli bearer auth (`gateway.auth.mode = "token"` / `"password"`) kullanıldığında, çağıran `x-openclaw-scopes` gönderse bile plugin-rotası çalışma zamanı kapsamı `operator.write` değerine sabitlenir
  - güvenilir kimlik taşıyan HTTP modları (örneğin `trusted-proxy` veya özel bir girişte `gateway.auth.mode = "none"`) yalnızca başlık açıkça mevcut olduğunda `x-openclaw-scopes` değerine uyar
  - bu kimlik taşıyan plugin-rotası isteklerinde `x-openclaw-scopes` yoksa, çalışma zamanı kapsamı `operator.write` değerine fallback yapar
- Pratik kural: gateway-auth kullanan bir plugin rotasının örtük yönetici yüzeyi olduğunu varsaymayın. Rotanız yalnızca yöneticiye özel davranış gerektiriyorsa, kimlik taşıyan bir auth modu isteyin ve açık `x-openclaw-scopes` başlık sözleşmesini belgeleyin.

## Plugin SDK içe aktarma yolları

Plugin yazarken, tek parça `openclaw/plugin-sdk` içe aktarması yerine
SDK alt yollarını kullanın:

- Plugin kayıt primitifleri için `openclaw/plugin-sdk/plugin-entry`.
- Genel paylaşılan plugin'e dönük sözleşme için `openclaw/plugin-sdk/core`.
- Kök `openclaw.json` Zod şema
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
  `openclaw/plugin-sdk/webhook-ingress` gibi kararlı kanal primitifleri; paylaşılan kurulum/auth/yanıt/webhook
  bağlantısı için kullanılır. `channel-inbound`, debounce, mention eşleme,
  envelope biçimlendirme ve gelen envelope bağlam yardımcıları için paylaşılan ana yerdir.
  `channel-setup`, dar isteğe bağlı kurulum yüzeyidir.
  `setup-runtime`, `setupEntry` /
  ertelenmiş başlangıç tarafından kullanılan çalışma zamanı güvenli kurulum yüzeyidir; içe aktarma güvenli kurulum yama bağdaştırıcılarını da içerir.
  `setup-adapter-runtime`, env farkındalıklı hesap-kurulum bağdaştırıcı yüzeyidir.
  `setup-tools`, küçük CLI/arşiv/belgeler yardımcı yüzeyidir (`formatCliCommand`,
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
  `openclaw/plugin-sdk/directory-runtime` gibi alan alt yolları; paylaşılan çalışma zamanı/yapılandırma yardımcıları içindir.
  `telegram-command-config`, Telegram özel
  komut normalizasyonu/doğrulaması için dar genel yüzeydir ve paketlenmiş
  Telegram sözleşme yüzeyi geçici olarak kullanılamıyor olsa bile erişilebilir kalır.
  `text-runtime`, assistant-visible-text ayıklama,
  markdown render/parçalama yardımcıları, redaksiyon
  yardımcıları, direktif-etiket yardımcıları ve güvenli metin yardımcıları dahil olmak üzere
  paylaşılan metin/markdown/loglama yüzeyidir.
- Onaya özgü kanal yüzeyleri, plugin üzerinde tek bir `approvalCapability`
  sözleşmesini tercih etmelidir. Çekirdek daha sonra onay auth, teslimat, render ve
  yerel yönlendirme davranışını ilgisiz plugin alanlarına karıştırmak yerine bu tek yetenek üzerinden okur.
- `openclaw/plugin-sdk/channel-runtime` kullanımdan kaldırılmıştır ve
  yalnızca eski plugin'ler için uyumluluk shim'i olarak kalır. Yeni kod bunun yerine
  daha dar genel primitifleri içe aktarmalıdır ve depo kodu shim için yeni
  içe aktarmalar eklememelidir.
- Paketlenmiş uzantı iç yapıları özel kalır. Harici plugin'ler yalnızca
  `openclaw/plugin-sdk/*` alt yollarını kullanmalıdır. OpenClaw çekirdek/test kodu,
  bir plugin paket kökü altındaki `index.js`, `api.js`,
  `runtime-api.js`, `setup-entry.js` ve `login-qr-api.js` gibi dar kapsamlı
  dosyalar gibi depo genel giriş noktalarını kullanabilir. Çekirdekten veya başka bir uzantıdan
  bir plugin paketinin `src/*` yolunu asla içe aktarmayın.
- Depo giriş noktası ayrımı:
  `<plugin-package-root>/api.js` yardımcı/tür barrel'idir,
  `<plugin-package-root>/runtime-api.js` yalnızca çalışma zamanı barrel'idir,
  `<plugin-package-root>/index.js` paketlenmiş plugin girişidir,
  ve `<plugin-package-root>/setup-entry.js` kurulum plugin girişidir.
- Mevcut paketlenmiş sağlayıcı örnekleri:
  - Anthropic, `wrapAnthropicProviderStream`, beta-header yardımcıları ve `service_tier`
    ayrıştırması gibi Claude akış yardımcıları için `api.js` / `contract-api.js` kullanır.
  - OpenAI, sağlayıcı oluşturucular, varsayılan model yardımcıları ve
    gerçek zamanlı sağlayıcı oluşturucular için `api.js` kullanır.
  - OpenRouter, onboarding/yapılandırma
    yardımcılarıyla birlikte kendi sağlayıcı oluşturucusu için `api.js` kullanır; `register.runtime.js` ise depo içi kullanım için
    genel `plugin-sdk/provider-stream` yardımcılarını yine dışa aktarabilir.
- Facade ile yüklenen genel giriş noktaları, biri mevcutsa etkin çalışma zamanı yapılandırma anlık görüntüsünü
  tercih eder; OpenClaw henüz bir çalışma zamanı anlık görüntüsü sunmuyorsa diskteki çözülmüş yapılandırma dosyasına fallback yapar.
- Genel paylaşılan primitifler, tercih edilen genel SDK sözleşmesi olmaya devam eder. Paketlenmiş kanala markalı küçük bir ayrılmış uyumluluk yardımcı yüzeyleri kümesi
  hâlâ vardır. Bunları yeni
  üçüncü taraf içe aktarma hedefleri olarak değil, paketlenmiş bakım/uyumluluk yüzeyleri olarak ele alın;
  yeni kanallar arası sözleşmeler yine genel `plugin-sdk/*` alt yollarına veya
  plugin'e yerel `api.js` / `runtime-api.js` barrel'lerine gitmelidir.

Uyumluluk notu:

- Yeni kod için kök `openclaw/plugin-sdk` barrel'inden kaçının.
- Önce dar kararlı primitifleri tercih edin. Daha yeni kurulum/eşleme/yanıt/
  geri bildirim/sözleşme/gelen/iş parçacığı/komut/secret-input/webhook/infra/
  allowlist/durum/mesaj-aracı alt yolları, yeni
  paketlenmiş ve harici plugin çalışmaları için amaçlanan sözleşmedir.
  Hedef ayrıştırma/eşleme `openclaw/plugin-sdk/channel-targets` üzerinde olmalıdır.
  Mesaj işlem kapıları ve tepki message-id yardımcıları
  `openclaw/plugin-sdk/channel-actions` üzerinde olmalıdır.
- Paketlenmiş uzantıya özgü yardımcı barrel'leri varsayılan olarak kararlı değildir. Eğer bir
  yardımcı yalnızca paketlenmiş bir uzantı tarafından gerekiyorsa, onu
  `openclaw/plugin-sdk/<extension>` içine taşımak yerine uzantının yerel `api.js` veya `runtime-api.js` yüzeyinin arkasında tutun.
- Yeni paylaşılan yardımcı yüzeyleri, kanala markalı değil genel olmalıdır. Paylaşılan hedef
  ayrıştırma `openclaw/plugin-sdk/channel-targets` üzerinde olmalıdır; kanala özgü
  iç yapılar sahip plugin'in yerel `api.js` veya `runtime-api.js`
  yüzeyinin arkasında kalmalıdır.
- `image-generation`,
  `media-understanding` ve `speech` gibi yeteneğe özgü alt yollar,
  paketlenmiş/yerel plugin'ler bunları bugün kullandığı için vardır. Bunların varlığı tek başına
  her dışa aktarılan yardımcının uzun vadeli donmuş bir harici sözleşme olduğu anlamına gelmez.

## Mesaj aracı şemaları

Plugin'ler kanala özgü `describeMessageTool(...)` şema
katkılarının sahibi olmalıdır. Sağlayıcıya özgü alanları paylaşılan çekirdekte değil plugin içinde tutun.

Paylaşılan taşınabilir şema parçaları için,
`openclaw/plugin-sdk/channel-actions` üzerinden dışa aktarılan genel yardımcıları yeniden kullanın:

- düğme-ızgarası tarzı yükler için `createMessageToolButtonsSchema()`
- yapılandırılmış kart yükleri için `createMessageToolCardSchema()`

Bir şema şekli yalnızca tek bir sağlayıcı için anlamlıysa, bunu paylaşılan SDK'ya taşımak yerine
o plugin'in kendi kaynağında tanımlayın.

## Kanal hedef çözümleme

Kanal plugin'leri, kanala özgü hedef anlambiliminin sahibi olmalıdır. Paylaşılan
giden host'u genel tutun ve sağlayıcı kuralları için mesajlaşma bağdaştırıcı yüzeyini kullanın:

- `messaging.inferTargetChatType({ to })`, normalize edilmiş bir hedefin
  dizin aramasından önce `direct`, `group` veya `channel` olarak mı ele alınacağına karar verir.
- `messaging.targetResolver.looksLikeId(raw, normalized)`, bir girdinin
  dizin araması yerine doğrudan kimlik benzeri çözümlemeye geçip geçmeyeceğini çekirdeğe bildirir.
- `messaging.targetResolver.resolveTarget(...)`, normalizasyondan sonra veya
  dizin isabetsiz kaldığında çekirdeğin son sağlayıcıya ait çözümlemeye ihtiyaç duyduğu durumda plugin fallback'idir.
- `messaging.resolveOutboundSessionRoute(...)`, bir hedef çözüldüğünde
  sağlayıcıya özgü oturum rota oluşturmanın sahibidir.

Önerilen ayrım:

- Eşler/gruplar aranmasından önce yapılması gereken kategori kararları için `inferTargetChatType` kullanın.
- "Buna açık/yerel hedef kimliği gibi davran" kontrolleri için `looksLikeId` kullanın.
- Sağlayıcıya özgü normalizasyon fallback'i için `resolveTarget` kullanın; geniş dizin araması için değil.
- Sohbet kimlikleri, ileti dizisi kimlikleri, JID'ler, kullanıcı adları ve oda kimlikleri gibi
  sağlayıcıya özgü yerel kimlikleri genel SDK alanlarında değil,
  `target` değerleri veya sağlayıcıya özgü parametreler içinde tutun.

## Yapılandırma destekli dizinler

Yapılandırmadan dizin girdileri türeten plugin'ler, bu mantığı plugin içinde tutmalı ve
`openclaw/plugin-sdk/directory-runtime` içindeki paylaşılan yardımcıları yeniden kullanmalıdır.

Bunu, bir kanalın şu tür yapılandırma destekli eşlere/gruplara ihtiyaç duyduğu durumlarda kullanın:

- allowlist güdümlü DM eşleri
- yapılandırılmış kanal/grup haritaları
- hesap kapsamlı statik dizin fallback'leri

`directory-runtime` içindeki paylaşılan yardımcılar yalnızca genel işlemleri ele alır:

- sorgu filtreleme
- limit uygulama
- tekrar kaldırma/normalizasyon yardımcıları
- `ChannelDirectoryEntry[]` oluşturma

Kanala özgü hesap inceleme ve kimlik normalizasyonu plugin uygulamasında kalmalıdır.

## Sağlayıcı katalogları

Sağlayıcı plugin'leri, çıkarım için
`registerProvider({ catalog: { run(...) { ... } } })` ile model katalogları tanımlayabilir.

`catalog.run(...)`, OpenClaw'ın
`models.providers` içine yazdığı aynı şekli döndürür:

- tek sağlayıcı girdisi için `{ provider }`
- birden fazla sağlayıcı girdisi için `{ providers }`

Sağlayıcıya özgü model kimliklerinin, temel URL varsayılanlarının veya auth kapılı model meta verisinin
sahibi plugin ise `catalog` kullanın.

`catalog.order`, bir plugin kataloğunun OpenClaw'ın yerleşik örtük sağlayıcılarına göre
ne zaman birleştirileceğini denetler:

- `simple`: düz API anahtarı veya env güdümlü sağlayıcılar
- `profile`: auth profilleri var olduğunda görünen sağlayıcılar
- `paired`: birden çok ilişkili sağlayıcı girdisi sentezleyen sağlayıcılar
- `late`: diğer örtük sağlayıcılardan sonra son geçiş

Daha sonraki sağlayıcılar anahtar çakışmasında kazanır; böylece plugin'ler aynı sağlayıcı kimliğine sahip
yerleşik bir sağlayıcı girdisini kasıtlı olarak geçersiz kılabilir.

Uyumluluk:

- `discovery` hâlâ eski bir takma ad olarak çalışır
- hem `catalog` hem `discovery` kayıtlıysa OpenClaw `catalog` kullanır

## Salt okunur kanal incelemesi

Plugin'iniz bir kanal kaydediyorsa,
`resolveAccount(...)` ile birlikte `plugin.config.inspectAccount(cfg, accountId)` uygulamayı tercih edin.

Neden:

- `resolveAccount(...)` çalışma zamanı yoludur. Kimlik bilgilerinin
  tamamen somutlaştırıldığını varsayabilir ve gerekli sırlar eksikse hızlıca başarısız olabilir.
- `openclaw status`, `openclaw status --all`,
  `openclaw channels status`, `openclaw channels resolve` ve doctor/config
  onarım akışları gibi salt okunur komut yolları; yapılandırmayı açıklamak için çalışma zamanı kimlik bilgilerini
  somutlaştırmaya ihtiyaç duymamalıdır.

Önerilen `inspectAccount(...)` davranışı:

- Yalnızca açıklayıcı hesap durumu döndürün.
- `enabled` ve `configured` değerlerini koruyun.
- Gerekliyse kimlik bilgisi kaynağı/durum alanlarını ekleyin, örneğin:
  - `tokenSource`, `tokenStatus`
  - `botTokenSource`, `botTokenStatus`
  - `appTokenSource`, `appTokenStatus`
  - `signingSecretSource`, `signingSecretStatus`
- Salt okunur kullanılabilirliği raporlamak için ham token değerlerini döndürmeniz gerekmez.
  `tokenStatus: "available"` (ve eşleşen kaynak alanı) döndürmek durum tarzı komutlar için yeterlidir.
- Bir kimlik bilgisi SecretRef yoluyla yapılandırılmış ama mevcut komut yolunda erişilemiyorsa
  `configured_unavailable` kullanın.

Bu, salt okunur komutların çökmeden veya hesabı yanlış şekilde yapılandırılmamış diye bildirmeden,
"yapılandırılmış ama bu komut yolunda kullanılamıyor" diyebilmesini sağlar.

## Paket paketleri

Bir plugin dizini, `openclaw.extensions` içeren bir `package.json` barındırabilir:

```json
{
  "name": "my-pack",
  "openclaw": {
    "extensions": ["./src/safety.ts", "./src/tools.ts"],
    "setupEntry": "./src/setup-entry.ts"
  }
}
```

Her girdi bir plugin olur. Paket birden fazla uzantı listeliyorsa, plugin kimliği
`name/<fileBase>` olur.

Plugin'iniz npm bağımlılıkları içe aktarıyorsa,
`node_modules` kullanılabilir olsun diye bunları o dizinde kurun (`npm install` / `pnpm install`).

Güvenlik koruması: her `openclaw.extensions` girdisi,
symlink çözümlemesinden sonra plugin dizini içinde kalmalıdır. Paket dizininden kaçan girdiler
reddedilir.

Güvenlik notu: `openclaw plugins install`, plugin bağımlılıklarını
`npm install --omit=dev --ignore-scripts` ile kurar (yaşam döngüsü script'i yok, çalışma zamanında dev dependency yoktur). Plugin bağımlılık
ağaçlarını "saf JS/TS" tutun ve `postinstall` derlemeleri gerektiren paketlerden kaçının.

İsteğe bağlı: `openclaw.setupEntry`, hafif bir yalnızca kurulum modülüne işaret edebilir.
OpenClaw devre dışı bir kanal plugin'i için kurulum yüzeylerine ihtiyaç duyduğunda veya
bir kanal plugin'i etkin ama hâlâ yapılandırılmamış olduğunda, tam plugin girdisi yerine `setupEntry`
yüklenir. Bu, ana plugin girdiniz araçlar, hook'lar veya diğer yalnızca çalışma zamanı
kodları da bağlıyorsa başlangıcı ve kurulumu daha hafif tutar.

İsteğe bağlı: `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`,
bir kanal plugin'ini, kanal zaten yapılandırılmış olsa bile, gateway'nin
dinleme öncesi başlangıç aşamasında aynı `setupEntry` yoluna dahil edebilir.

Bunu yalnızca `setupEntry`, gateway dinlemeye başlamadan önce var olması gereken
başlangıç yüzeyini tamamen kapsıyorsa kullanın. Pratikte bu, setup entry'nin başlangıcın bağlı olduğu
kanala ait her yeteneği kaydetmesi gerektiği anlamına gelir, örneğin:

- kanal kaydı
- gateway dinlemeye başlamadan önce kullanılabilir olması gereken tüm HTTP rotaları
- aynı pencerede var olması gereken tüm gateway yöntemleri, araçlar veya hizmetler

Tam girdiniz hâlâ gerekli bir başlangıç yeteneğinin sahibiyse, bu bayrağı etkinleştirmeyin.
Plugin'i varsayılan davranışta bırakın ve OpenClaw'ın başlangıçta tam girdiyi yüklemesine izin verin.

Paketlenmiş kanallar ayrıca, tam kanal çalışma zamanı yüklenmeden önce çekirdeğin danışabileceği
yalnızca kurulum sözleşme yüzeyi yardımcıları yayımlayabilir. Geçerli setup promotion yüzeyi şudur:

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

Çekirdek bu yüzeyi, tam plugin girdisini yüklemeden eski tek hesaplı kanal
yapılandırmasını `channels.<id>.accounts.*` içine yükseltmesi gerektiğinde kullanır.
Matrix mevcut paketlenmiş örnektir: adlandırılmış hesaplar zaten varsa yalnızca auth/bootstrap anahtarlarını
adlandırılmış bir yükseltilmiş hesaba taşır ve her zaman
`accounts.default` oluşturmak yerine yapılandırılmış kanonik olmayan bir varsayılan hesap anahtarını koruyabilir.

Bu kurulum yama bağdaştırıcıları, paketlenmiş sözleşme yüzeyi keşfini tembel tutar.
İçe aktarma zamanı hafif kalır; promotion yüzeyi, modül içe aktarması sırasında
paketlenmiş kanal başlangıcına yeniden girmek yerine yalnızca ilk kullanımda yüklenir.

Bu başlangıç yüzeyleri gateway RPC yöntemleri içerdiğinde, bunları
plugin'e özgü bir önek altında tutun. Çekirdek yönetici ad alanları (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) ayrılmıştır ve bir plugin daha dar bir kapsam istese bile
her zaman `operator.admin` olarak çözülür.

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

### Kanal katalog meta verisi

Kanal plugin'leri, `openclaw.channel` üzerinden kurulum/keşif meta verisi ve
`openclaw.install` üzerinden kurulum ipuçları sunabilir. Bu, çekirdek kataloğu verisiz tutar.

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

En küçük örneğin ötesinde yararlı `openclaw.channel` alanları:

- `detailLabel`: daha zengin katalog/durum yüzeyleri için ikincil etiket
- `docsLabel`: belgeler bağlantısı için bağlantı metnini geçersiz kılar
- `preferOver`: bu katalog girdisinin geride bırakması gereken daha düşük öncelikli plugin/kanal kimlikleri
- `selectionDocsPrefix`, `selectionDocsOmitLabel`, `selectionExtras`: seçim yüzeyi metin denetimleri
- `markdownCapable`: giden biçimlendirme kararları için kanalı markdown destekli olarak işaretler
- `exposure.configured`: `false` olarak ayarlandığında kanalı yapılandırılmış kanal listeleme yüzeylerinden gizler
- `exposure.setup`: `false` olarak ayarlandığında kanalı etkileşimli kurulum/yapılandırma seçicilerinden gizler
- `exposure.docs`: kanalı belgeler gezinme yüzeyleri için iç/özel olarak işaretler
- `showConfigured` / `showInSetup`: eski takma adlar uyumluluk için hâlâ kabul edilir; `exposure` tercih edin
- `quickstartAllowFrom`: kanalı standart hızlı başlangıç `allowFrom` akışına dahil eder
- `forceAccountBinding`: yalnızca tek hesap olsa bile açık hesap bağlamasını zorunlu kılar
- `preferSessionLookupForAnnounceTarget`: duyuru hedefi çözümlemesinde oturum aramasını tercih eder

OpenClaw ayrıca **harici kanal kataloglarını** (örneğin bir MPM
kayıt çıktısı) da birleştirebilir. Bir JSON dosyasını şu konumlardan birine bırakın:

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

Veya `OPENCLAW_PLUGIN_CATALOG_PATHS` (ya da `OPENCLAW_MPM_CATALOG_PATHS`) değişkenini
bir veya daha fazla JSON dosyasına yönlendirin (virgül/noktalı virgül/`PATH` ayırımlı). Her dosya
`{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }` içermelidir. Ayrıştırıcı ayrıca `"entries"` anahtarı için eski takma adlar olarak `"packages"` veya `"plugins"` değerlerini de kabul eder.

## Bağlam motoru plugin'leri

Bağlam motoru plugin'leri, alım, birleştirme
ve sıkıştırma için oturum bağlamı orkestrasyonunun sahibidir. Bunları plugin'inizden
`api.registerContextEngine(id, factory)` ile kaydedin, ardından etkin motoru
`plugins.slots.contextEngine` ile seçin.

Bunu, plugin'iniz yalnızca bellek arama veya hook eklemekten öte varsayılan bağlam
hattını değiştirmek ya da genişletmek istediğinde kullanın.

```ts
export default function (api) {
  api.registerContextEngine("lossless-claw", () => ({
    info: { id: "lossless-claw", name: "Lossless Claw", ownsCompaction: true },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages }) {
      return { messages, estimatedTokens: 0 };
    },
    async compact() {
      return { ok: true, compacted: false };
    },
  }));
}
```

Motorunuz sıkıştırma algoritmasının sahibi **değilse**, `compact()`
uygulamasını koruyun ve bunu açıkça devredin:

```ts
import { delegateCompactionToRuntime } from "openclaw/plugin-sdk/core";

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
    async assemble({ messages }) {
      return { messages, estimatedTokens: 0 };
    },
    async compact(params) {
      return await delegateCompactionToRuntime(params);
    },
  }));
}
```

## Yeni bir yetenek ekleme

Bir plugin, mevcut API'ye uymayan bir davranışa ihtiyaç duyduğunda,
plugin sistemini özel bir içeri uzanma ile baypas etmeyin. Eksik yeteneği ekleyin.

Önerilen sıra:

1. çekirdek sözleşmeyi tanımlayın
   Çekirdeğin hangi paylaşılan davranışın sahibi olması gerektiğine karar verin: ilke, fallback, yapılandırma birleştirme,
   yaşam döngüsü, kanala dönük anlambilim ve çalışma zamanı yardımcı şekli.
2. türlenmiş plugin kayıt/çalışma zamanı yüzeyleri ekleyin
   `OpenClawPluginApi` ve/veya `api.runtime` alanını en küçük yararlı
   türlenmiş yetenek yüzeyiyle genişletin.
3. çekirdeği + kanal/özellik tüketicilerini bağlayın
   Kanallar ve özellik plugin'leri, yeni yeteneği doğrudan bir satıcı uygulamasını içe aktararak değil,
   çekirdek üzerinden tüketmelidir.
4. satıcı uygulamalarını kaydedin
   Satıcı plugin'leri daha sonra kendi arka uçlarını bu yeteneğe karşı kaydeder.
5. sözleşme kapsamı ekleyin
   Sahiplik ve kayıt şeklinin zaman içinde açık kalması için testler ekleyin.

OpenClaw bu şekilde tek bir sağlayıcının dünya görüşüne sabit kodlanmadan
güçlü görüşlü kalır. Somut bir dosya kontrol listesi ve çalışan örnek için
[Capability Cookbook](/tr/plugins/architecture) bölümüne bakın.

### Yetenek kontrol listesi

Yeni bir yetenek eklediğinizde uygulama genellikle şu
yüzeylere birlikte dokunmalıdır:

- `src/<capability>/types.ts` içindeki çekirdek sözleşme türleri
- `src/<capability>/runtime.ts` içindeki çekirdek runner/çalışma zamanı yardımcısı
- `src/plugins/types.ts` içindeki plugin API kayıt yüzeyi
- `src/plugins/registry.ts` içindeki plugin kayıt defteri bağlantısı
- özellik/kanal plugin'lerinin tüketmesi gerektiğinde `src/plugins/runtime/*` içindeki plugin çalışma zamanı açığa çıkarması
- `src/test-utils/plugin-registration.ts` içindeki yakalama/test yardımcıları
- `src/plugins/contracts/registry.ts` içindeki sahiplik/sözleşme doğrulamaları
- `docs/` içindeki operatör/plugin belgeleri

Bu yüzeylerden biri eksikse, bu genellikle yeteneğin
henüz tam entegre edilmediğinin işaretidir.

### Yetenek şablonu

En küçük desen:

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

- çekirdek yetenek sözleşmesinin + orkestrasyonun sahibidir
- satıcı plugin'leri satıcı uygulamalarının sahibidir
- özellik/kanal plugin'leri çalışma zamanı yardımcılarını tüketir
- sözleşme testleri sahipliği açık tutar
