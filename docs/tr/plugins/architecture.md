---
read_when:
    - Yerel OpenClaw plugin’leri geliştirirken veya hata ayıklarken
    - Plugin capability modelini veya sahiplik sınırlarını anlamak istediğinizde
    - Plugin yükleme hattı veya kayıt sistemi üzerinde çalışırken
    - Sağlayıcı çalışma zamanı hook’larını veya kanal plugin’lerini uygularken
sidebarTitle: Internals
summary: 'Plugin iç yapıları: capability modeli, sahiplik, sözleşmeler, yükleme hattı ve çalışma zamanı yardımcıları'
title: Plugin İç Yapıları
x-i18n:
    generated_at: "2026-04-08T02:19:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: c40ecf14e2a0b2b8d332027aed939cd61fb4289a489f4cd4c076c96d707d1138
    source_path: plugins/architecture.md
    workflow: 15
---

# Plugin İç Yapıları

<Info>
  Bu, **derin mimari başvurusudur**. Pratik kılavuzlar için bkz.:
  - [Plugin’leri kurma ve kullanma](/tr/tools/plugin) — kullanıcı kılavuzu
  - [Başlarken](/tr/plugins/building-plugins) — ilk plugin öğreticisi
  - [Kanal Plugin’leri](/tr/plugins/sdk-channel-plugins) — bir mesajlaşma kanalı oluşturun
  - [Sağlayıcı Plugin’leri](/tr/plugins/sdk-provider-plugins) — bir model sağlayıcısı oluşturun
  - [SDK Genel Bakış](/tr/plugins/sdk-overview) — import eşlemesi ve kayıt API’si
</Info>

Bu sayfa, OpenClaw plugin sisteminin iç mimarisini kapsar.

## Genel capability modeli

Capability’ler, OpenClaw içindeki genel **yerel plugin** modelidir. Her
yerel OpenClaw plugin’i bir veya daha fazla capability türüne kaydolur:

| Capability             | Kayıt yöntemi                                   | Örnek plugin’ler                     |
| ---------------------- | ----------------------------------------------- | ------------------------------------ |
| Metin çıkarımı         | `api.registerProvider(...)`                     | `openai`, `anthropic`                |
| CLI çıkarım arka ucu   | `api.registerCliBackend(...)`                   | `openai`, `anthropic`                |
| Konuşma                | `api.registerSpeechProvider(...)`               | `elevenlabs`, `microsoft`            |
| Gerçek zamanlı yazıya dökme | `api.registerRealtimeTranscriptionProvider(...)` | `openai`                        |
| Gerçek zamanlı ses     | `api.registerRealtimeVoiceProvider(...)`        | `openai`                             |
| Medya anlama           | `api.registerMediaUnderstandingProvider(...)`   | `openai`, `google`                   |
| Görüntü oluşturma      | `api.registerImageGenerationProvider(...)`      | `openai`, `google`, `fal`, `minimax` |
| Müzik oluşturma        | `api.registerMusicGenerationProvider(...)`      | `google`, `minimax`                  |
| Video oluşturma        | `api.registerVideoGenerationProvider(...)`      | `qwen`                               |
| Web alma               | `api.registerWebFetchProvider(...)`             | `firecrawl`                          |
| Web arama              | `api.registerWebSearchProvider(...)`            | `google`                             |
| Kanal / mesajlaşma     | `api.registerChannel(...)`                      | `msteams`, `matrix`                  |

Sıfır capability kaydedip hook’lar, araçlar veya
servisler sağlayan bir plugin, **eski hook-only** plugin’dir. Bu desen hâlâ tam olarak desteklenir.

### Harici uyumluluk duruşu

Capability modeli çekirdeğe indi ve bugün paketlenmiş/yerel plugin’ler
tarafından kullanılıyor, ancak harici plugin uyumluluğu için "dışa aktarılmış,
öyleyse dondurulmuş" yaklaşımından daha sıkı bir eşik gerekir.

Mevcut yönlendirme:

- **mevcut harici plugin’ler:** hook tabanlı entegrasyonları çalışır durumda tutun; bunu
  uyumluluk tabanı olarak değerlendirin
- **yeni paketlenmiş/yerel plugin’ler:** satıcıya özgü içeri uzanımlar veya yeni
  hook-only tasarımlar yerine açık capability kaydını tercih edin
- **capability kaydını benimseyen harici plugin’ler:** izin verilir, ancak
  belgeler bir sözleşmeyi açıkça kararlı olarak işaretlemedikçe capability’ye özgü yardımcı yüzeyleri
  gelişen yüzeyler olarak değerlendirin

Pratik kural:

- capability kayıt API’leri hedeflenen yöndür
- eski hook’lar, geçiş sürecinde harici plugin’ler için en güvenli
  bozulmama yoludur
- dışa aktarılan yardımcı alt yolları eşit değildir; tesadüfi yardımcı dışa aktarımları değil,
  dar ve belgelenmiş sözleşmeyi tercih edin

### Plugin şekilleri

OpenClaw, yüklenen her plugin’i gerçek
kayıt davranışına göre bir şekle ayırır (yalnızca statik meta veriye göre değil):

- **plain-capability** -- tam olarak bir capability türü kaydeder (örneğin
  `mistral` gibi yalnızca sağlayıcı plugin’i)
- **hybrid-capability** -- birden çok capability türü kaydeder (örneğin
  `openai`, metin çıkarımı, konuşma, medya anlama ve görüntü
  oluşturmayı sahiplenir)
- **hook-only** -- yalnızca hook kaydeder (tiplenmiş veya özel), capability,
  araç, komut veya servis yoktur
- **non-capability** -- araçlar, komutlar, servisler veya rotalar kaydeder ama
  capability kaydetmez

Bir plugin’in şeklini ve capability
dökümünü görmek için `openclaw plugins inspect <id>` kullanın. Ayrıntılar için [CLI reference](/cli/plugins#inspect) sayfasına bakın.

### Eski hook’lar

`before_agent_start` hook’u, hook-only plugin’ler için bir uyumluluk yolu olarak desteklenmeye devam eder.
Eski gerçek dünya plugin’leri hâlâ buna bağımlıdır.

Yön:

- çalışır durumda tutun
- eski olarak belgelendirin
- model/sağlayıcı geçersiz kılma işleri için `before_model_resolve` tercih edin
- prompt mutasyonu işleri için `before_prompt_build` tercih edin
- yalnızca gerçek kullanım azaldığında ve fixture kapsamı geçiş güvenliğini kanıtladığında kaldırın

### Uyumluluk sinyalleri

`openclaw doctor` veya `openclaw plugins inspect <id>` çalıştırdığınızda
şu etiketlerden birini görebilirsiniz:

| Sinyal                     | Anlamı                                                      |
| -------------------------- | ----------------------------------------------------------- |
| **config valid**           | Yapılandırma düzgün ayrıştırılıyor ve plugin’ler çözümleniyor |
| **compatibility advisory** | Plugin desteklenen ama eski bir desen kullanıyor (örn. `hook-only`) |
| **legacy warning**         | Plugin artık önerilmeyen `before_agent_start` kullanıyor     |
| **hard error**             | Yapılandırma geçersiz veya plugin yüklenemedi               |

Ne `hook-only` ne de `before_agent_start` bugün plugin’inizi bozmaz --
`hook-only` bir bilgilendirmedir ve `before_agent_start` yalnızca uyarı üretir. Bu
sinyaller ayrıca `openclaw status --all` ve `openclaw plugins doctor` içinde de görünür.

## Mimari genel bakış

OpenClaw’ın plugin sistemi dört katmandan oluşur:

1. **Manifest + keşif**
   OpenClaw, yapılandırılmış yollar, workspace kökleri,
   genel uzantı kökleri ve paketlenmiş uzantılardan aday plugin’leri bulur. Keşif,
   önce yerel `openclaw.plugin.json` manifest’lerini ve desteklenen bundle manifest’lerini okur.
2. **Etkinleştirme + doğrulama**
   Çekirdek, keşfedilmiş bir plugin’in etkin, devre dışı, engellenmiş veya
   bellek gibi özel bir slot için seçilmiş olup olmadığına karar verir.
3. **Çalışma zamanı yükleme**
   Yerel OpenClaw plugin’leri jiti aracılığıyla süreç içinde yüklenir ve
   capability’leri merkezi bir kayıt sistemine kaydeder. Uyumlu bundle’lar ise
   çalışma zamanı kodu içe aktarılmadan kayıt sistemine normalize edilir.
4. **Yüzey tüketimi**
   OpenClaw’ın geri kalanı, araçları, kanalları, sağlayıcı
   kurulumunu, hook’ları, HTTP rotalarını, CLI komutlarını ve servisleri açığa çıkarmak için kayıt sistemini okur.

Özellikle plugin CLI için, kök komut keşfi iki aşamaya ayrılır:

- ayrıştırma zamanı meta verisi `registerCli(..., { descriptors: [...] })` içinden gelir
- gerçek plugin CLI modülü tembel kalabilir ve ilk çağrıda kaydolabilir

Bu, plugin’e ait CLI kodunu plugin içinde tutarken OpenClaw’ın
ayrıştırmadan önce kök komut adlarını ayırmasına da izin verir.

Önemli tasarım sınırı:

- keşif + yapılandırma doğrulaması, plugin kodunu çalıştırmadan
  **manifest/schema meta verisinden** çalışmalıdır
- yerel çalışma zamanı davranışı, plugin modülünün `register(api)` yolundan gelir

Bu ayrım, OpenClaw’ın yapılandırmayı doğrulamasına, eksik/devre dışı plugin’leri açıklamasına ve
tam çalışma zamanı etkin olmadan önce UI/schema ipuçları oluşturmasına olanak tanır.

### Kanal plugin’leri ve paylaşılan message aracı

Kanal plugin’lerinin, normal sohbet eylemleri için ayrı bir gönder/düzenle/tepki aracı kaydetmesi gerekmez.
OpenClaw, çekirdekte tek bir paylaşılan `message` aracı tutar ve
kanal plugin’leri bunun arkasındaki kanala özgü keşif ve yürütmeyi sahiplenir.

Mevcut sınır şudur:

- çekirdek, paylaşılan `message` araç ana makinesini, prompt kablolamasını, oturum/iş parçacığı
  kayıt tutmayı ve yürütme dispatch’ini sahiplenir
- kanal plugin’leri kapsamlı eylem keşfini, capability keşfini ve
  kanala özgü tüm şema parçalarını sahiplenir
- kanal plugin’leri sağlayıcıya özgü oturum konuşma dilbilgisini sahiplenir; örneğin
  konuşma kimliklerinin iş parçacığı kimliklerini nasıl kodladığı veya üst konuşmalardan nasıl miras aldığı gibi
- kanal plugin’leri nihai eylemi kendi eylem adaptörleri üzerinden yürütür

Kanal plugin’leri için SDK yüzeyi
`ChannelMessageActionAdapter.describeMessageTool(...)`’dur. Bu birleşik keşif
çağrısı, bir plugin’in görünür eylemlerini, capability’lerini ve şema
katkılarını birlikte döndürmesine izin verir; böylece bu parçalar birbirinden sapmaz.

Çekirdek, çalışma zamanı kapsamını bu keşif adımına geçirir. Önemli alanlar şunlardır:

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- güvenilir gelen `requesterSenderId`

Bu, bağlama duyarlı plugin’ler için önemlidir. Bir kanal, çekirdek `message` aracına
kanala özgü dallar sabit kodlamadan, etkin hesaba, geçerli odaya/iş parçacığına/mesaja veya
güvenilir istemci kimliğine göre mesaj eylemlerini gizleyebilir veya gösterebilir.

Bu nedenle gömülü çalıştırıcı yönlendirme değişiklikleri hâlâ plugin işidir: çalıştırıcı,
paylaşılan `message` aracının geçerli tur için doğru kanal sahipli yüzeyi göstermesi amacıyla
mevcut sohbet/oturum kimliğini plugin keşif sınırına iletmekten sorumludur.

Kanala ait yürütme yardımcıları için, paketlenmiş plugin’ler yürütme
çalışma zamanını kendi uzantı modüllerinin içinde tutmalıdır. Çekirdek artık
`src/agents/tools` altında Discord,
Slack, Telegram veya WhatsApp mesaj eylemi çalışma zamanlarını sahiplenmez.
Ayrı `plugin-sdk/*-action-runtime` alt yolları yayımlamıyoruz ve paketlenmiş
plugin’ler kendi yerel çalışma zamanı kodlarını doğrudan
uzantı sahipli modüllerinden içe aktarmalıdır.

Aynı sınır genel olarak sağlayıcı adlı SDK yüzeyleri için de geçerlidir:
çekirdek, Slack, Discord, Signal,
WhatsApp veya benzeri uzantılar için kanala özgü kolaylık barrel’larını içe aktarmamalıdır.
Çekirdek bir davranışa ihtiyaç duyuyorsa, ya paketlenmiş plugin’in kendi `api.ts` / `runtime-api.ts`
barrel’ını tüketmeli ya da ihtiyacı paylaşılan SDK içinde dar bir genel capability’ye
yükseltmelidir.

Özellikle anketler için iki yürütme yolu vardır:

- `outbound.sendPoll`, ortak
  anket modeline uyan kanallar için paylaşılan tabandır
- `actions.handleAction("poll")`, kanala özgü
  anket semantiği veya ek anket parametreleri için tercih edilen yoldur

Çekirdek artık paylaşılan anket ayrıştırmasını, plugin anket dispatch’i eylemi
reddettikten sonraya erteler; böylece plugin’e ait anket işleyicileri, önce genel anket ayrıştırıcısı tarafından
engellenmeden kanala özgü anket alanlarını kabul edebilir.

Tam başlangıç sırası için bkz. [Yükleme hattı](#load-pipeline).

## Capability sahiplik modeli

OpenClaw, yerel bir plugin’i ilgisiz entegrasyonların bir torbası olarak değil,
bir **şirket** veya **özellik** için sahiplik sınırı olarak ele alır.

Bu şu anlama gelir:

- bir şirket plugin’i, genellikle o şirketin OpenClaw’a dönük
  tüm yüzeylerini sahiplenmelidir
- bir özellik plugin’i, sunduğu tam özellik yüzeyini
  genellikle sahiplenmelidir
- kanallar, sağlayıcı davranışını geçici olarak yeniden uygulamak yerine
  paylaşılan çekirdek capability’leri tüketmelidir

Örnekler:

- paketlenmiş `openai` plugin’i OpenAI model-sağlayıcı davranışını ve OpenAI
  konuşma + gerçek zamanlı ses + medya anlama + görüntü oluşturma davranışını sahiplenir
- paketlenmiş `elevenlabs` plugin’i ElevenLabs konuşma davranışını sahiplenir
- paketlenmiş `microsoft` plugin’i Microsoft konuşma davranışını sahiplenir
- paketlenmiş `google` plugin’i Google model-sağlayıcı davranışını ve ayrıca Google
  medya anlama + görüntü oluşturma + web arama davranışını sahiplenir
- paketlenmiş `firecrawl` plugin’i Firecrawl web alma davranışını sahiplenir
- paketlenmiş `minimax`, `mistral`, `moonshot` ve `zai` plugin’leri kendi
  medya anlama arka uçlarını sahiplenir
- paketlenmiş `qwen` plugin’i Qwen metin sağlayıcı davranışını ve ayrıca
  medya anlama ile video oluşturma davranışını sahiplenir
- `voice-call` plugin’i bir özellik plugin’idir: çağrı taşımayı, araçları,
  CLI’yi, rotaları ve Twilio medya-akışı köprülemesini sahiplenir, ancak satıcı plugin’lerini doğrudan
  içe aktarmak yerine paylaşılan konuşma ile
  gerçek zamanlı yazıya dökme ve gerçek zamanlı ses capability’lerini tüketir

Hedeflenen son durum şudur:

- OpenAI, metin modelleri, konuşma, görüntüler ve
  gelecekteki video kapsansa bile tek bir plugin içinde yaşar
- başka bir satıcı da kendi yüzey alanı için aynısını yapabilir
- kanallar, sağlayıcının hangi satıcı plugin’ine ait olduğunu umursamaz; çekirdek tarafından açığa çıkarılan
  paylaşılan capability sözleşmesini tüketir

Bu temel ayrımdır:

- **plugin** = sahiplik sınırı
- **capability** = birden fazla plugin’in uygulayabildiği veya tüketebildiği çekirdek sözleşme

Dolayısıyla OpenClaw video gibi yeni bir alan eklerse, ilk soru
"hangi sağlayıcı videoyu sabit kodlayarak ele almalı?" değildir. İlk soru "çekirdek
video capability sözleşmesi nedir?" olmalıdır. Bu sözleşme bir kez var olduğunda, satıcı plugin’leri
ona kaydolabilir ve kanal/özellik plugin’leri onu tüketebilir.

Capability henüz yoksa, doğru hareket genellikle şudur:

1. eksik capability’yi çekirdekte tanımlamak
2. bunu plugin API’si/çalışma zamanı üzerinden tipli şekilde açığa çıkarmak
3. kanal/özellikleri bu capability’ye bağlamak
4. satıcı plugin’lerinin uygulamaları kaydetmesine izin vermek

Bu, tek bir satıcıya veya tek seferlik bir plugin’e özgü kod yoluna bağlı
çekirdek davranışlardan kaçınırken sahipliği açık tutar.

### Capability katmanlaması

Kodun nereye ait olduğuna karar verirken şu zihinsel modeli kullanın:

- **çekirdek capability katmanı**: paylaşılan orkestrasyon, politika, fallback, yapılandırma
  birleştirme kuralları, teslim semantiği ve tipli sözleşmeler
- **satıcı plugin katmanı**: satıcıya özgü API’ler, auth, model katalogları, konuşma
  sentezi, görüntü oluşturma, gelecekteki video arka uçları, kullanım uç noktaları
- **kanal/özellik plugin katmanı**: paylaşılan capability’leri tüketen ve bunları
  Slack/Discord/voice-call vb. üzerinde sunan entegrasyon

Örneğin TTS şu şekli izler:

- çekirdek yanıt zamanı TTS politikasını, fallback sırasını, tercihleri ve kanal teslimini sahiplenir
- `openai`, `elevenlabs` ve `microsoft` sentez uygulamalarını sahiplenir
- `voice-call` telefon TTS çalışma zamanı yardımcısını tüketir

Aynı desen gelecekteki capability’ler için de tercih edilmelidir.

### Çok capability’li şirket plugin’i örneği

Bir şirket plugin’i dışarıdan bakıldığında bütünlüklü hissettirmelidir. OpenClaw;
modeller, konuşma, gerçek zamanlı yazıya dökme, gerçek zamanlı ses, medya
anlama, görüntü oluşturma, video oluşturma, web alma ve web arama için paylaşılan sözleşmelere sahipse,
bir satıcı tüm yüzeylerini tek yerde sahiplenebilir:

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
      // satıcı konuşma yapılandırması — SpeechProviderPlugin arayüzünü doğrudan uygulayın
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
        // kimlik bilgisi + alma mantığı
      }),
    );
  },
};

export default plugin;
```

Önemli olan tam yardımcı adları değildir. Şekil önemlidir:

- tek bir plugin satıcı yüzeyini sahiplenir
- çekirdek capability sözleşmelerini yine sahiplenir
- kanallar ve özellik plugin’leri satıcı kodunu değil `api.runtime.*` yardımcılarını tüketir
- sözleşme testleri, plugin’in sahip olduğunu iddia ettiği capability’leri gerçekten kaydettiğini
  doğrulayabilir

### Capability örneği: video anlama

OpenClaw, görüntü/ses/video anlamayı zaten tek bir paylaşılan
capability olarak ele alır. Aynı sahiplik modeli burada da geçerlidir:

1. çekirdek medya-anlama sözleşmesini tanımlar
2. satıcı plugin’leri, uygun oldukça `describeImage`, `transcribeAudio` ve
   `describeVideo` kaydeder
3. kanallar ve özellik plugin’leri doğrudan satıcı koduna bağlanmak yerine
   paylaşılan çekirdek davranışı tüketir

Bu, tek bir sağlayıcının video varsayımlarının çekirdeğe gömülmesini önler. Plugin, satıcı yüzeyini sahiplenir;
çekirdek ise capability sözleşmesini ve fallback davranışını sahiplenir.

Video oluşturma zaten aynı diziyi kullanır: çekirdek tipli
capability sözleşmesini ve çalışma zamanı yardımcısını sahiplenir, satıcı plugin’leri ise
`api.registerVideoGenerationProvider(...)` uygulamaları kaydeder.

Somut bir yaygınlaştırma kontrol listesine mi ihtiyacınız var? Bkz.
[Capability Cookbook](/tr/plugins/architecture).

## Sözleşmeler ve zorunlu kılma

Plugin API yüzeyi, kasten tiplenmiş ve
`OpenClawPluginApi` içinde merkezileştirilmiştir. Bu sözleşme, desteklenen kayıt noktalarını ve
bir plugin’in güvenebileceği çalışma zamanı yardımcılarını tanımlar.

Bunun önemi:

- plugin yazarları tek bir kararlı iç standarda sahip olur
- çekirdek, aynı sağlayıcı kimliğini iki plugin’in kaydetmesi gibi yinelenen sahiplikleri reddedebilir
- başlangıç, hatalı kayıtlar için eyleme geçirilebilir tanılar gösterebilir
- sözleşme testleri, paketlenmiş plugin sahipliğini zorunlu kılıp sessiz sapmaları önleyebilir

İki zorunlu kılma katmanı vardır:

1. **çalışma zamanı kayıt zorunluluğu**
   Plugin kayıt sistemi, plugin’ler yüklenirken kayıtları doğrular. Örnekler:
   yinelenen sağlayıcı kimlikleri, yinelenen konuşma sağlayıcısı kimlikleri ve hatalı
   kayıtlar, tanımsız davranış yerine plugin tanıları üretir.
2. **sözleşme testleri**
   Paketlenmiş plugin’ler, test çalışmaları sırasında sözleşme kayıt sistemlerinde yakalanır; böylece
   OpenClaw sahipliği açıkça doğrulayabilir. Bugün bu, model
   sağlayıcıları, konuşma sağlayıcıları, web arama sağlayıcıları ve paketlenmiş kayıt
   sahipliği için kullanılır.

Pratik etkisi şudur: OpenClaw, hangi yüzeyin hangi plugin’e ait olduğunu
baştan bilir. Bu, çekirdeğin ve kanalların sorunsuz bir şekilde birleşmesine izin verir çünkü
sahiplik örtük değil, bildirilmiş, tiplenmiş ve test edilebilirdir.

### Bir sözleşmede ne yer almalı

İyi plugin sözleşmeleri şunlardır:

- tipli
- küçük
- capability’ye özgü
- çekirdeğe ait
- birden fazla plugin tarafından yeniden kullanılabilir
- satıcı bilgisi olmadan kanallar/özellikler tarafından tüketilebilir

Kötü plugin sözleşmeleri şunlardır:

- çekirdek içine gizlenmiş satıcıya özgü politika
- kayıt sistemini baypas eden tek seferlik plugin kaçış kapıları
- kanal kodunun doğrudan bir satıcı uygulamasına uzanması
- `OpenClawPluginApi` veya
  `api.runtime` parçası olmayan geçici çalışma zamanı nesneleri

Şüphede kalırsanız soyutlama düzeyini yükseltin: önce capability’yi tanımlayın, ardından
plugin’lerin buna bağlanmasına izin verin.

## Yürütme modeli

Yerel OpenClaw plugin’leri Gateway ile **aynı süreç içinde** çalışır. Kum havuzuna alınmazlar.
Yüklenmiş yerel bir plugin, çekirdek kodla aynı süreç düzeyinde güven sınırına sahiptir.

Sonuçları:

- yerel bir plugin araçlar, ağ işleyicileri, hook’lar ve servisler kaydedebilir
- yerel bir plugin hatası gateway’i çökertip kararsızlaştırabilir
- kötü amaçlı bir yerel plugin, OpenClaw süreci içinde rastgele kod yürütmeye eşdeğerdir

Uyumlu bundle’lar varsayılan olarak daha güvenlidir çünkü OpenClaw şu anda onları
meta veri/içerik paketleri olarak ele alır. Güncel sürümlerde bu çoğunlukla paketlenmiş
Skills anlamına gelir.

Paketlenmemiş plugin’ler için allowlist’ler ve açık kurulum/yükleme yolları kullanın.
Workspace plugin’lerini üretim varsayılanı değil, geliştirme zamanı kodu olarak değerlendirin.

Paketlenmiş workspace paket adları için, plugin kimliğini npm
adına sabitleyin: varsayılan olarak `@openclaw/<id>` veya
paket kasıtlı olarak daha dar bir plugin rolü sunuyorsa
`-provider`, `-plugin`, `-speech`, `-sandbox` veya `-media-understanding` gibi onaylı tipli soneklerden biri.

Önemli güven notu:

- `plugins.allow`, **plugin kimliklerine** güvenir, kaynak kökene değil.
- Paketlenmiş bir plugin ile aynı kimliğe sahip bir workspace plugin’i,
  o workspace plugin’i etkinse/allowlist’e alınmışsa kasıtlı olarak paketlenmiş kopyayı gölgeler.
- Bu normaldir ve yerel geliştirme, yama testi ve hotfix’ler için kullanışlıdır.

## Dışa aktarım sınırı

OpenClaw, uygulama kolaylıklarını değil capability’leri dışa aktarır.

Capability kaydını genel tutun. Sözleşme dışı yardımcı dışa aktarımlarını daraltın:

- paketlenmiş plugin’e özgü yardımcı alt yollar
- genel API olması amaçlanmayan çalışma zamanı tesisat alt yolları
- satıcıya özgü kolaylık yardımcıları
- uygulama ayrıntısı olan kurulum/onboarding yardımcıları

Bazı paketlenmiş plugin yardımcı alt yolları, uyumluluk ve paketlenmiş plugin bakımı için
oluşturulmuş SDK dışa aktarım eşlemesinde hâlâ kalır. Güncel örnekler:
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` ve birkaç `plugin-sdk/matrix*` yüzeyidir. Bunları,
yeni üçüncü taraf plugin’ler için önerilen SDK deseni değil, ayrılmış uygulama ayrıntısı dışa aktarımları olarak değerlendirin.

## Yükleme hattı

Başlangıçta OpenClaw kabaca şunları yapar:

1. aday plugin köklerini keşfeder
2. yerel veya uyumlu bundle manifest’lerini ve paket meta verilerini okur
3. güvensiz adayları reddeder
4. plugin yapılandırmasını (`plugins.enabled`, `allow`, `deny`, `entries`,
   `slots`, `load.paths`) normalize eder
5. her aday için etkinleştirmeye karar verir
6. etkin yerel modülleri jiti ile yükler
7. yerel `register(api)` (veya eski takma ad olan `activate(api)`) hook’larını çağırır ve kayıtları plugin kayıt sistemine toplar
8. kayıt sistemini komutlara/çalışma zamanı yüzeylerine açar

<Note>
`activate`, `register` için eski bir takma addır — yükleyici hangisi varsa onu çözümler (`def.register ?? def.activate`) ve aynı noktada çağırır. Tüm paketlenmiş plugin’ler `register` kullanır; yeni plugin’ler için `register` tercih edin.
</Note>

Güvenlik kapıları, çalışma zamanı yürütmesinden **önce** gerçekleşir. Adaylar,
giriş plugin kökünden taşarsa, yol world-writable ise veya
paketlenmemiş plugin’ler için yol sahipliği şüpheli görünüyorsa engellenir.

### Manifest-first davranışı

Manifest, kontrol düzleminin doğruluk kaynağıdır. OpenClaw bunu şu amaçlarla kullanır:

- plugin’i tanımlamak
- bildirilen kanalları/Skills/yapılandırma şemasını veya bundle capability’lerini keşfetmek
- `plugins.entries.<id>.config` doğrulamak
- Control UI etiketlerini/yer tutucularını zenginleştirmek
- kurulum/katalog meta verisini göstermek

Yerel plugin’ler için çalışma zamanı modülü, veri düzlemi kısmıdır. Bu modül,
hook’lar, araçlar, komutlar veya sağlayıcı akışları gibi gerçek davranışları kaydeder.

### Yükleyicinin önbelleğe aldığı şeyler

OpenClaw süreç içinde kısa ömürlü önbellekler tutar:

- keşif sonuçları
- manifest kayıt sistemi verisi
- yüklenmiş plugin kayıt sistemleri

Bu önbellekler, yoğun başlangıç anını ve tekrar eden komut yükünü azaltır. Bunları
kalıcılık değil, kısa ömürlü performans önbellekleri olarak düşünmek güvenlidir.

Performans notu:

- Bu önbellekleri devre dışı bırakmak için `OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` veya
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1` ayarlayın.
- Önbellek pencerelerini `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` ve
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS` ile ayarlayın.

## Kayıt sistemi modeli

Yüklenmiş plugin’ler rastgele çekirdek globalleri doğrudan değiştirmez. Merkezi bir
plugin kayıt sistemine kaydolurlar.

Kayıt sistemi şunları izler:

- plugin kayıtları (kimlik, kaynak, köken, durum, tanılar)
- araçlar
- eski hook’lar ve tipli hook’lar
- kanallar
- sağlayıcılar
- gateway RPC işleyicileri
- HTTP rotaları
- CLI registrar’ları
- arka plan servisleri
- plugin’e ait komutlar

Ardından çekirdek özellikler, doğrudan plugin modülleriyle konuşmak yerine bu kayıt sisteminden okur.
Bu, yüklemeyi tek yönlü tutar:

- plugin modülü -> kayıt sistemi kaydı
- çekirdek çalışma zamanı -> kayıt sistemi tüketimi

Bu ayrım bakım kolaylığı açısından önemlidir. Çoğu çekirdek yüzeyin
"her plugin modülü için özel durum yazmak" yerine yalnızca tek bir entegrasyon noktasına,
yani "kayıt sistemini okumaya" ihtiyaç duyması anlamına gelir.

## Konuşma bağlama callback’leri

Bir konuşmayı bağlayan plugin’ler, bir onay çözümlendiğinde tepki verebilir.

Bir bağlama isteği onaylandıktan veya reddedildikten sonra callback almak için
`api.onConversationBindingResolved(...)` kullanın:

```ts
export default {
  id: "my-plugin",
  register(api) {
    api.onConversationBindingResolved(async (event) => {
      if (event.status === "approved") {
        // Bu plugin + konuşma için artık bir bağlama mevcut.
        console.log(event.binding?.conversationId);
        return;
      }

      // İstek reddedildi; yerel bekleyen durumu temizleyin.
      console.log(event.request.conversation.conversationId);
    });
  },
};
```

Callback payload alanları:

- `status`: `"approved"` veya `"denied"`
- `decision`: `"allow-once"`, `"allow-always"` veya `"deny"`
- `binding`: onaylanmış istekler için çözümlenen bağlama
- `request`: özgün istek özeti, ayırma ipucu, gönderici kimliği ve
  konuşma meta verisi

Bu callback yalnızca bildirim amaçlıdır. Bir konuşmayı kimin bağlayabileceğini değiştirmez
ve çekirdeğin onay işleme süreci tamamlandıktan sonra çalışır.

## Sağlayıcı çalışma zamanı hook’ları

Sağlayıcı plugin’lerinin artık iki katmanı vardır:

- manifest meta verisi: çalışma zamanı yüklenmeden önce ucuz sağlayıcı env-auth araması için `providerAuthEnvVars`,
  çalışma zamanı yüklenmeden önce ucuz kanal env/kurulum araması için `channelEnvVars`,
  ayrıca çalışma zamanı yüklenmeden önce ucuz onboarding/auth-choice
  etiketleri ve CLI bayrak meta verisi için `providerAuthChoices`
- yapılandırma zamanı hook’ları: `catalog` / eski `discovery` ile `applyConfigDefaults`
- çalışma zamanı hook’ları: `normalizeModelId`, `normalizeTransport`,
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

OpenClaw hâlâ genel ajan döngüsünü, failover’ı, transkript işlemeyi ve
araç politikasını sahiplenir. Bu hook’lar, tümüyle özel bir çıkarım taşımasına ihtiyaç duymadan
sağlayıcıya özgü davranışlar için genişletme yüzeyidir.

Sağlayıcının, genel auth/durum/model seçici yollarının plugin
çalışma zamanını yüklemeden görmesi gereken env tabanlı kimlik bilgileri varsa manifest `providerAuthEnvVars` kullanın.
Onboarding/auth-choice CLI
yüzeylerinin sağlayıcının seçim kimliğini, grup etiketlerini ve basit
tek bayraklı auth kablolamasını çalışma zamanı yüklemeden bilmesi gerekiyorsa manifest `providerAuthChoices` kullanın.
Operatör odaklı onboarding etiketleri veya OAuth
client-id/client-secret kurulum değişkenleri gibi ipuçları için sağlayıcı çalışma zamanı
`envVars` alanını koruyun.

Bir kanalın, genel kabuk env fallback, yapılandırma/durum kontrolleri veya
kurulum istemlerinin çalışma zamanını yüklemeden görmesi gereken env güdümlü auth veya kurulumu varsa
manifest `channelEnvVars` kullanın.

### Hook sırası ve kullanım

Model/sağlayıcı plugin’leri için OpenClaw hook’ları kabaca şu sırayla çağırır.
"Ne zaman kullanılmalı" sütunu hızlı karar rehberidir.

| #   | Hook                              | Ne yapar                                                                                                       | Ne zaman kullanılmalı                                                                                                                        |
| --- | --------------------------------- | -------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `catalog`                         | `models.json` üretimi sırasında sağlayıcı yapılandırmasını `models.providers` içine yayımlar                   | Sağlayıcı bir katalog veya varsayılan base URL’leri sahipleniyorsa                                                                            |
| 2   | `applyConfigDefaults`             | Yapılandırma materyalizasyonu sırasında sağlayıcıya ait genel yapılandırma varsayılanlarını uygular            | Varsayılanlar auth moduna, env’ye veya sağlayıcı model ailesi semantiğine bağlıysa                                                           |
| --  | _(yerleşik model araması)_        | OpenClaw önce normal kayıt sistemi/katalog yolunu dener                                                        | _(plugin hook’u değildir)_                                                                                                                   |
| 3   | `normalizeModelId`                | Aramadan önce eski veya önizleme model-id takma adlarını normalize eder                                        | Sağlayıcı, kanonik model çözümlemesinden önce takma ad temizliğini sahipleniyorsa                                                            |
| 4   | `normalizeTransport`              | Genel model derlemesinden önce sağlayıcı ailesi `api` / `baseUrl` değerlerini normalize eder                  | Sağlayıcı, aynı taşıma ailesindeki özel sağlayıcı kimlikleri için taşıma temizliğini sahipleniyorsa                                          |
| 5   | `normalizeConfig`                 | Çalışma zamanı/sağlayıcı çözümlemesinden önce `models.providers.<id>` değerini normalize eder                 | Sağlayıcı, plugin ile birlikte yaşaması gereken yapılandırma temizliğine ihtiyaç duyuyorsa; paketlenmiş Google ailesi yardımcıları da desteklenen Google yapılandırma girdilerini geriden destekler |
| 6   | `applyNativeStreamingUsageCompat` | Yapılandırma sağlayıcılarına yerel akış-kullanım uyumluluk yeniden yazımları uygular                           | Sağlayıcı, uç nokta odaklı yerel akış kullanım meta verisi düzeltmelerine ihtiyaç duyuyorsa                                                 |
| 7   | `resolveConfigApiKey`             | Çalışma zamanı auth yüklenmeden önce yapılandırma sağlayıcıları için env-marker auth’u çözümler               | Sağlayıcı, sağlayıcıya ait env-marker API anahtarı çözümlemesine sahipse; `amazon-bedrock` burada ayrıca yerleşik AWS env-marker çözücüye de sahiptir |
| 8   | `resolveSyntheticAuth`            | Düz metin kalıcılaştırmadan local/self-hosted veya yapılandırma destekli auth’u yüzeye çıkarır                | Sağlayıcı, sentetik/yerel bir kimlik bilgisi işaretçisi ile çalışabiliyorsa                                                                   |
| 9   | `resolveExternalAuthProfiles`     | Sağlayıcıya ait harici auth profillerini bindirir; varsayılan `persistence`, CLI/uygulama sahipli kimlik bilgileri için `runtime-only`’dir | Sağlayıcı, kopyalanmış refresh token’ları kalıcılaştırmadan harici auth kimlik bilgilerini yeniden kullanıyorsa                              |
| 10  | `shouldDeferSyntheticProfileAuth` | Depolanmış sentetik profil yer tutucularını env/config destekli auth’un gerisine iter                          | Sağlayıcı, öncelik kazanmaması gereken sentetik yer tutucu profiller depoluyorsa                                                             |
| 11  | `resolveDynamicModel`             | Henüz yerel kayıt sisteminde olmayan sağlayıcı sahipli model kimlikleri için eşzamanlı fallback                | Sağlayıcı, rastgele yukarı akış model kimliklerini kabul ediyorsa                                                                             |
| 12  | `prepareDynamicModel`             | Eşzamansız ısınma yapar, ardından `resolveDynamicModel` tekrar çalışır                                          | Sağlayıcı, bilinmeyen kimlikleri çözümlemeden önce ağ meta verisine ihtiyaç duyuyorsa                                                        |
| 13  | `normalizeResolvedModel`          | Gömülü çalıştırıcı çözümlenen modeli kullanmadan önce son yeniden yazımı yapar                                 | Sağlayıcı, taşıma yeniden yazımlarına ihtiyaç duyuyor ama hâlâ çekirdek taşıma kullanıyorsa                                                  |
| 14  | `contributeResolvedModelCompat`   | Başka bir uyumlu taşıma arkasındaki satıcı modelleri için uyumluluk bayrakları ekler                           | Sağlayıcı, sağlayıcıyı devralmadan proxy taşımalarında kendi modellerini tanıyorsa                                                           |
| 15  | `capabilities`                    | Paylaşılan çekirdek mantığı tarafından kullanılan sağlayıcıya ait transkript/araç meta verisi                 | Sağlayıcı, transkript/sağlayıcı ailesi farklılıklarına ihtiyaç duyuyorsa                                                                     |
| 16  | `normalizeToolSchemas`            | Gömülü çalıştırıcı görmeden önce araç şemalarını normalize eder                                                 | Sağlayıcı, taşıma ailesine özgü şema temizliğine ihtiyaç duyuyorsa                                                                            |
| 17  | `inspectToolSchemas`              | Normalleştirme sonrasında sağlayıcıya ait şema tanılarını yüzeye çıkarır                                        | Sağlayıcı, çekirdeğe sağlayıcıya özgü kurallar öğretmeden anahtar sözcük uyarıları istiyorsa                                                 |
| 18  | `resolveReasoningOutputMode`      | Yerel veya etiketli reasoning-output sözleşmesini seçer                                                         | Sağlayıcı, yerel alanlar yerine etiketli reasoning/final output istiyorsa                                                                     |
| 19  | `prepareExtraParams`              | Genel akış seçenek sarmalayıcılarından önce istek parametresi normalizasyonu yapar                              | Sağlayıcı, varsayılan istek parametrelerine veya sağlayıcı başına parametre temizliğine ihtiyaç duyuyorsa                                    |
| 20  | `createStreamFn`                  | Normal akış yolunu tamamen özel bir taşıma ile değiştirir                                                       | Sağlayıcı, yalnızca sarmalayıcı değil özel bir kablo protokolüne ihtiyaç duyuyorsa                                                            |
| 21  | `wrapStreamFn`                    | Genel sarmalayıcılar uygulandıktan sonra akış sarmalayıcısı uygular                                              | Sağlayıcı, özel taşıma olmadan istek üstbilgisi/gövdesi/model uyumluluk sarmalayıcılarına ihtiyaç duyuyorsa                                  |
| 22  | `resolveTransportTurnState`       | Yerel tur başına taşıma üstbilgileri veya meta veri ekler                                                       | Sağlayıcı, genel taşımaların sağlayıcıya ait yerel tur kimliği göndermesini istiyorsa                                                        |
| 23  | `resolveWebSocketSessionPolicy`   | Yerel WebSocket üstbilgileri veya oturum cool-down politikası ekler                                             | Sağlayıcı, genel WS taşımalarının oturum üstbilgilerini veya fallback politikasını ayarlamasını istiyorsa                                    |
| 24  | `formatApiKey`                    | Auth-profile biçimleyici: depolanan profil çalışma zamanı `apiKey` dizesine dönüşür                             | Sağlayıcı, ek auth meta verisi depoluyor ve özel bir çalışma zamanı token şekline ihtiyaç duyuyorsa                                          |
| 25  | `refreshOAuth`                    | Özel refresh uç noktaları veya refresh başarısızlığı politikası için OAuth refresh geçersiz kılması            | Sağlayıcı, paylaşılan `pi-ai` yenileyicilerine uymuyorsa                                                                                     |
| 26  | `buildAuthDoctorHint`             | OAuth refresh başarısız olduğunda eklenecek onarım ipucu                                                        | Sağlayıcı, refresh başarısızlığından sonra sağlayıcıya ait auth onarım yönlendirmesine ihtiyaç duyuyorsa                                     |
| 27  | `matchesContextOverflowError`     | Sağlayıcıya ait context-window taşma eşleştiricisi                                                              | Sağlayıcı, genel sezgilerin kaçıracağı ham taşma hatalarına sahipse                                                                           |
| 28  | `classifyFailoverReason`          | Sağlayıcıya ait failover neden sınıflandırması                                                                  | Sağlayıcı, ham API/taşıma hatalarını rate-limit/overload vb. durumlara eşleyebiliyorsa                                                       |
| 29  | `isCacheTtlEligible`              | Proxy/backhaul sağlayıcıları için prompt-cache politikası                                                       | Sağlayıcı, proxy’ye özgü cache TTL geçitlemesine ihtiyaç duyuyorsa                                                                            |
| 30  | `buildMissingAuthMessage`         | Genel eksik-auth kurtarma iletisini değiştiren mesaj                                                            | Sağlayıcı, sağlayıcıya özgü eksik-auth kurtarma ipucuna ihtiyaç duyuyorsa                                                                     |
| 31  | `suppressBuiltInModel`            | Eski yukarı akış model gizleme ve isteğe bağlı kullanıcıya dönük hata ipucu                                     | Sağlayıcı, eski yukarı akış satırlarını gizlemek veya onları bir satıcı ipucuyla değiştirmek istiyorsa                                       |
| 32  | `augmentModelCatalog`             | Keşiften sonra sentetik/nihai katalog satırları ekler                                                           | Sağlayıcı, `models list` ve seçicilerde sentetik ileri uyumluluk satırlarına ihtiyaç duyuyorsa                                               |
| 33  | `isBinaryThinking`                | İkili düşünme sağlayıcıları için açık/kapalı reasoning geçişi                                                   | Sağlayıcı yalnızca ikili açık/kapalı thinking sunuyorsa                                                                                       |
| 34  | `supportsXHighThinking`           | Seçili modeller için `xhigh` reasoning desteği                                                                  | Sağlayıcı, `xhigh` özelliğini yalnızca modellerin bir alt kümesinde istiyorsa                                                                 |
| 35  | `resolveDefaultThinkingLevel`     | Belirli bir model ailesi için varsayılan `/think` düzeyi                                                        | Sağlayıcı, bir model ailesi için varsayılan `/think` politikasını sahipleniyorsa                                                             |
| 36  | `isModernModelRef`                | Canlı profil filtreleri ve smoke seçimi için modern-model eşleştiricisi                                         | Sağlayıcı, live/smoke tercih edilen model eşleştirmesini sahipleniyorsa                                                                       |
| 37  | `prepareRuntimeAuth`              | Çıkarımdan hemen önce yapılandırılmış bir kimlik bilgisini gerçek çalışma zamanı token’ına/anahtarına çevirir  | Sağlayıcı, token değişimine veya kısa ömürlü istek kimlik bilgisine ihtiyaç duyuyorsa                                                        |
| 38  | `resolveUsageAuth`                | `/usage` ve ilgili durum yüzeyleri için kullanım/faturalama kimlik bilgilerini çözümler                         | Sağlayıcı, özel kullanım/kota token ayrıştırmasına veya farklı bir kullanım kimlik bilgisine ihtiyaç duyuyorsa                               |
| 39  | `fetchUsageSnapshot`              | Auth çözümlendikten sonra sağlayıcıya özgü kullanım/kota snapshot’larını alır ve normalize eder                | Sağlayıcı, sağlayıcıya özgü kullanım uç noktası veya payload ayrıştırıcısına ihtiyaç duyuyorsa                                               |
| 40  | `createEmbeddingProvider`         | Bellek/arama için sağlayıcıya ait embedding adaptörü oluşturur                                                  | Bellek embedding davranışı sağlayıcı plugin’i ile birlikte aitse                                                                              |
| 41  | `buildReplayPolicy`               | Sağlayıcı için transkript işlemeyi denetleyen bir replay policy döndürür                                        | Sağlayıcı, özel transkript politikasına ihtiyaç duyuyorsa (örneğin thinking-block kaldırma)                                                  |
| 42  | `sanitizeReplayHistory`           | Genel transkript temizliğinden sonra replay geçmişini yeniden yazar                                             | Sağlayıcı, paylaşılan sıkıştırma yardımcılarının ötesinde sağlayıcıya özgü replay yeniden yazımlarına ihtiyaç duyuyorsa                      |
| 43  | `validateReplayTurns`             | Gömülü çalıştırıcıdan önce son replay-turn doğrulaması veya yeniden şekillendirme                               | Sağlayıcı taşıması, genel temizlemeden sonra daha sıkı tur doğrulaması gerektiriyorsa                                                        |
| 44  | `onModelSelected`                 | Sağlayıcıya ait seçim sonrası yan etkileri çalıştırır                                                           | Sağlayıcı, model etkin olduğunda telemetri veya sağlayıcıya ait durum yönetimine ihtiyaç duyuyorsa                                           |

`normalizeModelId`, `normalizeTransport` ve `normalizeConfig` önce eşleşen
sağlayıcı plugin’ini denetler, sonra model kimliğini veya taşıma/yapılandırmayı gerçekten değiştirene kadar
diğer hook-capable sağlayıcı plugin’lerine düşer. Bu,
çağıranın hangi paketlenmiş plugin’in yeniden yazımı sahiplediğini bilmesini gerektirmeden
takma ad/uyumluluk sağlayıcı shim’lerinin çalışmasını sağlar. Hiçbir sağlayıcı hook’u
desteklenen Google ailesi yapılandırma girdisini yeniden yazmazsa,
paketlenmiş Google yapılandırma normalleştiricisi yine de bu uyumluluk temizliğini uygular.

Sağlayıcı tamamen özel bir kablo protokolüne veya özel istek yürütücüsüne ihtiyaç duyuyorsa,
bu farklı bir uzantı sınıfıdır. Bu hook’lar,
OpenClaw’ın normal çıkarım döngüsü üzerinde çalışmaya devam eden sağlayıcı davranışları içindir.

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

- Anthropic, Claude 4.6 ileri uyumluluğunu,
  sağlayıcı ailesi ipuçlarını, auth onarım rehberliğini, kullanım uç noktası entegrasyonunu,
  prompt-cache uygunluğunu, auth farkındalıklı yapılandırma varsayılanlarını, Claude
  varsayılan/uyarlamalı thinking politikasını ve beta başlıkları,
  `/fast` / `serviceTier` ve `context1m` için Anthropic’e özgü akış şekillendirmesini sahiplendiği için
  `resolveDynamicModel`, `capabilities`, `buildAuthDoctorHint`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `isCacheTtlEligible`,
  `resolveDefaultThinkingLevel`, `applyConfigDefaults`, `isModernModelRef`
  ve `wrapStreamFn` kullanır.
- Anthropic’in Claude’a özgü akış yardımcıları şimdilik paketlenmiş plugin’in kendi
  genel `api.ts` / `contract-api.ts` yüzeyinde kalır. Bu paket yüzeyi,
  genel SDK’yı tek bir sağlayıcının beta-header kuralları etrafında genişletmek yerine
  `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
  `resolveAnthropicFastMode`, `resolveAnthropicServiceTier` ve daha alt düzey
  Anthropic sarmalayıcı oluşturucularını dışa aktarır.
- OpenAI, GPT-5.4 ileri uyumluluğunu,
  doğrudan OpenAI `openai-completions` -> `openai-responses` normalizasyonunu,
  Codex farkındalıklı auth ipuçlarını, Spark gizlemeyi, sentetik OpenAI liste satırlarını ve GPT-5 thinking /
  live-model politikasını sahiplendiği için `resolveDynamicModel`, `normalizeResolvedModel` ve
  `capabilities` ile birlikte `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `supportsXHighThinking` ve `isModernModelRef`
  kullanır; `openai-responses-defaults` akış ailesi ise
  atıf üstbilgileri, `/fast`/`serviceTier`, metin ayrıntı düzeyi, yerel Codex web araması,
  reasoning-compat payload şekillendirmesi ve Responses bağlam yönetimi için
  paylaşılan yerel OpenAI Responses sarmalayıcılarını sahiplenir.
- OpenRouter, sağlayıcı geçişli olduğu ve OpenClaw’ın statik kataloğu güncellenmeden önce yeni
  model kimlikleri açığa çıkarabileceği için `catalog` ile birlikte `resolveDynamicModel` ve
  `prepareDynamicModel` kullanır; ayrıca
  sağlayıcıya özgü istek üstbilgilerini, yönlendirme meta verisini, reasoning yamalarını ve
  prompt-cache politikasını çekirdek dışında tutmak için
  `capabilities`, `wrapStreamFn` ve `isCacheTtlEligible` kullanır. Replay politikası
  `passthrough-gemini` ailesinden gelirken, `openrouter-thinking` akış ailesi
  proxy reasoning eklemeyi ve desteklenmeyen model / `auto` atlamalarını sahiplenir.
- GitHub Copilot; sağlayıcıya ait cihaz girişi, model fallback davranışı, Claude transkript
  farklılıkları, GitHub token -> Copilot token değişimi ve sağlayıcıya ait kullanım uç noktası
  ihtiyacı nedeniyle `catalog`, `auth`, `resolveDynamicModel` ve
  `capabilities` ile birlikte `prepareRuntimeAuth` ve `fetchUsageSnapshot` kullanır.
- OpenAI Codex, hâlâ çekirdek OpenAI taşımalarında çalışmasına rağmen kendi taşıma/base URL
  normalizasyonunu, OAuth refresh fallback politikasını, varsayılan taşıma seçimini,
  sentetik Codex katalog satırlarını ve ChatGPT kullanım uç noktası entegrasyonunu sahiplendiği için
  `catalog`, `resolveDynamicModel`,
  `normalizeResolvedModel`, `refreshOAuth` ve `augmentModelCatalog` ile birlikte
  `prepareExtraParams`, `resolveUsageAuth` ve `fetchUsageSnapshot` kullanır; doğrudan OpenAI ile
  aynı `openai-responses-defaults` akış ailesini paylaşır.
- Google AI Studio ve Gemini CLI OAuth,
  `google-gemini` replay ailesi Gemini 3.1 ileri uyumluluk fallback’ini,
  yerel Gemini replay doğrulamasını, bootstrap replay temizliğini, etiketli
  reasoning-output modunu ve modern-model eşleştirmesini sahiplenirken,
  `google-thinking` akış ailesi Gemini thinking payload normalizasyonunu sahiplendiği için
  `resolveDynamicModel`,
  `buildReplayPolicy`, `sanitizeReplayHistory`,
  `resolveReasoningOutputMode`, `wrapStreamFn` ve `isModernModelRef` kullanır;
  Gemini CLI OAuth ayrıca token biçimlendirme, token ayrıştırma ve kota uç noktası
  kablolaması için `formatApiKey`, `resolveUsageAuth` ve
  `fetchUsageSnapshot` kullanır.
- Anthropic Vertex, `anthropic-by-model` replay ailesi üzerinden `buildReplayPolicy` kullanır;
  böylece Claude’a özgü replay temizliği her `anthropic-messages` taşımaya değil,
  Claude kimliklerine özgü kalır.
- Amazon Bedrock, Anthropic-on-Bedrock trafiği için
  Bedrock’a özgü throttle/not-ready/context-overflow hata sınıflandırmasını sahiplendiği için
  `buildReplayPolicy`, `matchesContextOverflowError`,
  `classifyFailoverReason` ve `resolveDefaultThinkingLevel` kullanır;
  replay politikası yine aynı yalnızca-Claude `anthropic-by-model` korumasını paylaşır.
- OpenRouter, Kilocode, Opencode ve Opencode Go, Gemini
  modellerini OpenAI uyumlu taşımalar üzerinden proxy’ledikleri ve yerel Gemini replay doğrulaması veya
  bootstrap yeniden yazımları olmadan Gemini thought-signature temizliğine ihtiyaç duydukları için
  `passthrough-gemini` replay ailesi üzerinden `buildReplayPolicy`
  kullanır.
- MiniMax, tek bir sağlayıcı hem
  Anthropic-message hem de OpenAI uyumlu semantiği sahiplendiği için
  `hybrid-anthropic-openai` replay ailesi üzerinden `buildReplayPolicy` kullanır;
  Anthropic tarafında Claude’a özgü thinking-block kaldırmayı korurken reasoning
  output modunu yeniden yerel duruma çevirir ve `minimax-fast-mode` akış ailesi
  paylaşılan akış yolunda hızlı mod model yeniden yazımlarını sahiplenir.
- Moonshot, paylaşılan
  OpenAI taşımasını kullanmaya devam eder ama sağlayıcıya ait thinking payload normalizasyonuna ihtiyaç duyduğu için
  `catalog` ile birlikte `wrapStreamFn` kullanır; `moonshot-thinking` akış ailesi
  yapılandırma ile `/think` durumunu kendi yerel ikili thinking payload’una eşler.
- Kilocode, sağlayıcıya ait istek üstbilgileri,
  reasoning payload normalizasyonu, Gemini transkript ipuçları ve Anthropic
  cache-TTL geçitlemesine ihtiyaç duyduğu için `catalog`, `capabilities`, `wrapStreamFn` ve
  `isCacheTtlEligible` kullanır; `kilocode-thinking` akış ailesi Kilo thinking
  eklemesini, açık reasoning payload’ları desteklemeyen `kilo/auto` ve diğer
  proxy model kimliklerini atlayarak, paylaşılan proxy akış yolunda tutar.
- Z.AI; GLM-5 fallback’i,
  `tool_stream` varsayılanlarını, ikili thinking UX’ini, modern-model eşleştirmesini ve hem
  kullanım auth’u hem de kota alımını sahiplendiği için `resolveDynamicModel`, `prepareExtraParams`, `wrapStreamFn`,
  `isCacheTtlEligible`, `isBinaryThinking`, `isModernModelRef`,
  `resolveUsageAuth` ve `fetchUsageSnapshot` kullanır; `tool-stream-default-on` akış ailesi,
  varsayılan açık `tool_stream` sarmalayıcısını sağlayıcı başına el yazısı yapıştırıcıdan uzak tutar.
- xAI; yerel xAI Responses taşıma normalizasyonunu, Grok hızlı mod
  takma ad yeniden yazımlarını, varsayılan `tool_stream`’ü, strict-tool / reasoning-payload
  temizliğini, plugin’e ait araçlar için fallback auth yeniden kullanımını, ileri uyumluluklu Grok
  model çözümlemesini ve xAI tool-schema
  profili, desteklenmeyen şema anahtar sözcükleri, yerel `web_search` ve HTML-entity
  tool-call argüman çözümlemesi gibi sağlayıcıya ait uyumluluk yamalarını sahiplendiği için
  `normalizeResolvedModel`, `normalizeTransport`,
  `contributeResolvedModelCompat`, `prepareExtraParams`, `wrapStreamFn`,
  `resolveSyntheticAuth`, `resolveDynamicModel` ve `isModernModelRef`
  kullanır.
- Mistral, OpenCode Zen ve OpenCode Go; transkript/araç
  farklılıklarını çekirdek dışında tutmak için yalnızca `capabilities` kullanır.
- `byteplus`, `cloudflare-ai-gateway`,
  `huggingface`, `kimi-coding`, `nvidia`, `qianfan`,
  `synthetic`, `together`, `venice`, `vercel-ai-gateway` ve `volcengine` gibi
  yalnızca kataloglu paketlenmiş sağlayıcılar yalnızca `catalog` kullanır.
- Qwen, metin sağlayıcısı için `catalog`, ayrıca çok modlu yüzeyleri için
  paylaşılan media-understanding ve video-generation kayıtlarını kullanır.
- MiniMax ve Xiaomi, çıkarım hâlâ paylaşılan
  taşımalar üzerinden çalışsa da `/usage`
  davranışları plugin’e ait olduğu için `catalog` ile birlikte kullanım hook’larını kullanır.

## Çalışma zamanı yardımcıları

Plugin’ler, `api.runtime` aracılığıyla seçili çekirdek yardımcılarına erişebilir. TTS için:

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

- `textToSpeech`, dosya/sesli not yüzeyleri için normal çekirdek TTS çıktı payload’unu döndürür.
- Çekirdek `messages.tts` yapılandırmasını ve sağlayıcı seçimini kullanır.
- PCM ses arabelleği + örnekleme hızı döndürür. Plugin’ler sağlayıcılar için yeniden örnekleme/kodlama yapmalıdır.
- `listVoices`, sağlayıcı başına isteğe bağlıdır. Bunu satıcıya ait ses seçicileri veya kurulum akışları için kullanın.
- Ses listeleri; sağlayıcı farkındalıklı seçiciler için yerel ayar, cinsiyet ve kişilik etiketleri gibi daha zengin meta veriler içerebilir.
- OpenAI ve ElevenLabs bugün telefon desteği sunar. Microsoft sunmaz.

Plugin’ler ayrıca `api.registerSpeechProvider(...)` aracılığıyla konuşma sağlayıcıları kaydedebilir.

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

- TTS politikasını, fallback’i ve yanıt teslimini çekirdekte tutun.
- Satıcıya ait sentez davranışı için konuşma sağlayıcılarını kullanın.
- Eski Microsoft `edge` girdisi `microsoft` sağlayıcı kimliğine normalize edilir.
- Tercih edilen sahiplik modeli şirket odaklıdır: tek bir satıcı plugin’i,
  OpenClaw bu capability sözleşmelerini ekledikçe metin, konuşma, görüntü ve gelecekteki medya sağlayıcılarını sahiplenebilir.

Görüntü/ses/video anlama için plugin’ler, genel bir anahtar/değer torbası yerine
tek bir tipli medya-anlama sağlayıcısı kaydeder:

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

- Orkestrasyonu, fallback’i, yapılandırmayı ve kanal kablolamasını çekirdekte tutun.
- Satıcı davranışını sağlayıcı plugin’inde tutun.
- Artımlı genişleme tipli kalmalıdır: yeni isteğe bağlı yöntemler, yeni isteğe bağlı
  sonuç alanları, yeni isteğe bağlı capability’ler.
- Video oluşturma zaten aynı deseni izler:
  - çekirdek capability sözleşmesini ve çalışma zamanı yardımcısını sahiplenir
  - satıcı plugin’leri `api.registerVideoGenerationProvider(...)` kaydeder
  - özellik/kanal plugin’leri `api.runtime.videoGeneration.*` tüketir

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
  // MIME güvenilir biçimde çıkarılamadığında isteğe bağlı:
  mime: "audio/ogg",
});
```

Notlar:

- `api.runtime.mediaUnderstanding.*`, görüntü/ses/video anlama için tercih edilen
  paylaşılan yüzeydir.
- Çekirdek medya-anlama ses yapılandırmasını (`tools.media.audio`) ve sağlayıcı fallback sırasını kullanır.
- Hiç yazıya dökme çıktısı üretilmediğinde `{ text: undefined }` döndürür
  (örneğin atlanan/desteklenmeyen giriş).
- `api.runtime.stt.transcribeAudioFile(...)` uyumluluk takma adı olarak kalır.

Plugin’ler ayrıca `api.runtime.subagent` aracılığıyla arka plan alt ajan çalıştırmaları başlatabilir:

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
- OpenClaw bu geçersiz kılma alanlarını yalnızca güvenilir çağıranlar için uygular.
- Plugin’e ait fallback çalıştırmaları için operatörler `plugins.entries.<id>.subagent.allowModelOverride: true` ile açıkça katılım göstermelidir.
- Güvenilir plugin’leri belirli kanonik `provider/model` hedefleriyle sınırlamak veya açıkça herhangi bir hedefe izin vermek için `"*"` kullanmak üzere `plugins.entries.<id>.subagent.allowedModels` ayarlayın.
- Güvenilmeyen plugin alt ajan çalıştırmaları yine de çalışır, ancak geçersiz kılma istekleri sessizce fallback yapılmak yerine reddedilir.

Web arama için plugin’ler ajan araç kablolamasına uzanmak yerine
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

Plugin’ler ayrıca
`api.registerWebSearchProvider(...)` aracılığıyla web arama sağlayıcıları kaydedebilir.

Notlar:

- Sağlayıcı seçimini, kimlik bilgisi çözümlemesini ve paylaşılan istek semantiğini çekirdekte tutun.
- Satıcıya özgü arama taşımaları için web arama sağlayıcılarını kullanın.
- `api.runtime.webSearch.*`, ajan araç sarmalayıcısına bağlı olmadan arama davranışına ihtiyaç duyan özellik/kanal plugin’leri için tercih edilen paylaşılan yüzeydir.

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

- `generate(...)`: yapılandırılmış görüntü oluşturma sağlayıcı zincirini kullanarak bir görüntü üretir.
- `listProviders(...)`: kullanılabilir görüntü oluşturma sağlayıcılarını ve capability’lerini listeler.

## Gateway HTTP rotaları

Plugin’ler `api.registerHttpRoute(...)` ile HTTP uç noktaları açabilir.

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
- `auth`: zorunlu. Normal gateway auth istemek için `"gateway"` veya plugin tarafından yönetilen auth/webhook doğrulaması için `"plugin"` kullanın.
- `match`: isteğe bağlı. `"exact"` (varsayılan) veya `"prefix"`.
- `replaceExisting`: isteğe bağlı. Aynı plugin’in kendi mevcut rota kaydını değiştirmesine izin verir.
- `handler`: rota isteği işlediyse `true` döndürmelidir.

Notlar:

- `api.registerHttpHandler(...)` kaldırıldı ve plugin yükleme hatasına neden olur. Bunun yerine `api.registerHttpRoute(...)` kullanın.
- Plugin rotaları `auth` değerini açıkça bildirmelidir.
- Açık `path + match` çakışmaları, `replaceExisting: true` olmadıkça reddedilir ve bir plugin başka bir plugin’in rotasını değiştiremez.
- Farklı `auth` düzeylerine sahip örtüşen rotalar reddedilir. `exact`/`prefix` geçiş zincirlerini yalnızca aynı auth düzeyinde tutun.
- `auth: "plugin"` rotaları otomatik olarak operatör çalışma zamanı kapsamları almaz. Bunlar ayrıcalıklı Gateway yardımcı çağrıları için değil, plugin tarafından yönetilen webhook/imza doğrulaması içindir.
- `auth: "gateway"` rotaları bir Gateway istek çalışma zamanı kapsamında çalışır, ancak bu kapsam bilinçli olarak tutucudur:
  - paylaşılan gizli bearer auth (`gateway.auth.mode = "token"` / `"password"`), çağıran `x-openclaw-scopes` gönderse bile plugin-rotası çalışma zamanı kapsamlarını `operator.write` üzerinde sabit tutar
  - güvenilir kimlik taşıyan HTTP modları (örneğin `trusted-proxy` veya özel bir girişte `gateway.auth.mode = "none"`), `x-openclaw-scopes` başlığını yalnızca bu başlık açıkça mevcutsa dikkate alır
  - bu kimlik taşıyan plugin-rotası isteklerinde `x-openclaw-scopes` yoksa çalışma zamanı kapsamı `operator.write` değerine geri düşer
- Pratik kural: gateway auth’lu bir plugin rotasının örtük bir yönetici yüzeyi olduğunu varsaymayın. Rotanız yöneticiye özel davranış gerektiriyorsa kimlik taşıyan bir auth modu gerektirin ve açık `x-openclaw-scopes` başlık sözleşmesini belgelendirin.

## Plugin SDK import yolları

Plugin geliştirirken tek parça `openclaw/plugin-sdk` import’u yerine
SDK alt yollarını kullanın:

- plugin kayıt ilkel öğeleri için `openclaw/plugin-sdk/plugin-entry`.
- genel paylaşılan plugin odaklı sözleşme için `openclaw/plugin-sdk/core`.
- kök `openclaw.json` Zod şema dışa aktarımı
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
  `openclaw/plugin-sdk/webhook-ingress` gibi kararlı kanal ilkel öğeleri; paylaşılan kurulum/auth/yanıt/webhook
  kablolaması içindir. `channel-inbound`; debounce, mention eşleştirme,
  gelen mention-policy yardımcıları, zarf biçimlendirme ve gelen zarf
  bağlam yardımcıları için paylaşılan yuvadır.
  `channel-setup`, dar isteğe bağlı kurulum yüzeyidir.
  `setup-runtime`, `setupEntry` /
  ertelenmiş başlangıç tarafından kullanılan ve import güvenli kurulum patch adaptörlerini içeren çalışma zamanı güvenli kurulum yüzeyidir.
  `setup-adapter-runtime`, env farkındalıklı hesap kurulum adaptörü yüzeyidir.
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
  `openclaw/plugin-sdk/directory-runtime` gibi alan alt yolları; paylaşılan çalışma zamanı/yapılandırma yardımcıları içindir.
  `telegram-command-config`, Telegram özel
  komut normalizasyonu/doğrulaması için dar genel yüzeydir ve paketlenmiş
  Telegram sözleşme yüzeyi geçici olarak kullanılamasa bile kullanılabilir kalır.
  `text-runtime`; asistan tarafından görülebilir metin temizleme,
  markdown işleme/parçalama yardımcıları, sansürleme
  yardımcıları, directive-tag yardımcıları ve güvenli metin yardımcılarını içeren paylaşılan metin/markdown/loglama yüzeyidir.
- Onaya özgü kanal yüzeyleri, plugin üzerindeki tek bir `approvalCapability`
  sözleşmesini tercih etmelidir. Çekirdek daha sonra onay auth’unu, teslimi, işlemeyi,
  yerel yönlendirmeyi ve tembel yerel işleyici davranışını
  ilgisiz plugin alanlarına karıştırmak yerine bu tek capability üzerinden okur.
- `openclaw/plugin-sdk/channel-runtime` artık önerilmez ve yalnızca eski plugin’ler için
  uyumluluk shim’i olarak kalır. Yeni kod daha dar
  genel ilkel öğeleri içe aktarmalı ve depo kodu shim’e yeni import’lar eklememelidir.
- Paketlenmiş uzantı iç yapıları özel kalır. Harici plugin’ler yalnızca
  `openclaw/plugin-sdk/*` alt yollarını kullanmalıdır. OpenClaw çekirdek/test kodu,
  `index.js`, `api.js`,
  `runtime-api.js`, `setup-entry.js` ve
  `login-qr-api.js` gibi dar kapsamlı dosyalar gibi bir plugin paket kökü altındaki
  depo genel giriş noktalarını kullanabilir. Çekirdekten veya başka bir uzantıdan
  asla bir plugin paketinin `src/*` yolunu içe aktarmayın.
- Depo giriş noktası ayrımı:
  `<plugin-package-root>/api.js` yardımcı/tip barrel’ıdır,
  `<plugin-package-root>/runtime-api.js` yalnızca çalışma zamanı barrel’ıdır,
  `<plugin-package-root>/index.js` paketlenmiş plugin girişidir,
  ve `<plugin-package-root>/setup-entry.js` kurulum plugin girişidir.
- Güncel paketlenmiş sağlayıcı örnekleri:
  - Anthropic, `wrapAnthropicProviderStream`, beta-header yardımcıları ve `service_tier`
    ayrıştırması gibi Claude akış yardımcıları için `api.js` / `contract-api.js` kullanır.
  - OpenAI, sağlayıcı oluşturucular, varsayılan model yardımcıları ve
    gerçek zamanlı sağlayıcı oluşturucular için `api.js` kullanır.
  - OpenRouter, sağlayıcı oluşturucusu ile onboarding/yapılandırma
    yardımcıları için `api.js` kullanır; `register.runtime.js` ise depo içi kullanım için genel
    `plugin-sdk/provider-stream` yardımcılarını yeniden dışa aktarabilir.
- Cephe ile yüklenen genel giriş noktaları, varsa etkin çalışma zamanı yapılandırma snapshot’ını tercih eder,
  sonra OpenClaw henüz bir çalışma zamanı snapshot’ı sunmuyorsa diskteki çözümlenmiş yapılandırma dosyasına döner.
- Genel paylaşılan ilkel öğeler, tercih edilen genel SDK sözleşmesi olmaya devam eder. Paketlenmiş kanal markalı yardımcı yüzeylerin küçük bir ayrılmış uyumluluk kümesi hâlâ vardır. Bunları yeni
  üçüncü taraf import hedefleri olarak değil, paketlenmiş bakım/uyumluluk yüzeyleri olarak değerlendirin; yeni kanallar arası sözleşmeler yine
  genel `plugin-sdk/*` alt yollarına veya plugin’e ait yerel `api.js` /
  `runtime-api.js` barrel’larına inmelidir.

Uyumluluk notu:

- Yeni kod için kök `openclaw/plugin-sdk` barrel’ından kaçının.
- Önce dar kararlı ilkel öğeleri tercih edin. Daha yeni kurulum/eşleştirme/yanıt/
  geri bildirim/sözleşme/gelen/iş parçacığı/komut/secret-input/webhook/infra/
  allowlist/durum/message-tool alt yolları, yeni
  paketlenmiş ve harici plugin işleri için hedeflenen sözleşmedir.
  Hedef ayrıştırma/eşleştirme `openclaw/plugin-sdk/channel-targets` üzerinde olmalıdır.
  Mesaj eylemi kapıları ve tepki mesaj-kimliği yardımcıları
  `openclaw/plugin-sdk/channel-actions` üzerinde olmalıdır.
- Paketlenmiş uzantıya özgü yardımcı barrel’lar varsayılan olarak kararlı değildir. Eğer bir
  yardımcıya yalnızca paketlenmiş bir uzantı ihtiyaç duyuyorsa, bunu
  `openclaw/plugin-sdk/<extension>` içine yükseltmek yerine uzantının yerel `api.js` veya `runtime-api.js` yüzeyi arkasında tutun.
- Yeni paylaşılan yardımcı yüzeyleri kanal markalı değil, genel olmalıdır. Paylaşılan hedef
  ayrıştırma `openclaw/plugin-sdk/channel-targets` üzerinde olmalı; kanala özgü
  iç yapılar ise sahip plugin’in yerel `api.js` veya `runtime-api.js`
  yüzeyi arkasında kalmalıdır.
- `image-generation`,
  `media-understanding` ve `speech` gibi capability’ye özgü alt yollar vardır; çünkü paketlenmiş/yerel plugin’ler bugün bunları kullanır. Ancak
  bunların varlığı tek başına her dışa aktarılan yardımcının uzun vadeli donmuş bir harici sözleşme olduğu anlamına gelmez.

## Message araç şemaları

Plugin’ler, kanala özgü `describeMessageTool(...)` şema
katkılarını sahiplenmelidir. Sağlayıcıya özgü alanları paylaşılan çekirdekte değil plugin’de tutun.

Paylaşılan taşınabilir şema parçaları için
`openclaw/plugin-sdk/channel-actions` üzerinden dışa aktarılan genel yardımcıları yeniden kullanın:

- düğme ızgarası tarzı payload’lar için `createMessageToolButtonsSchema()`
- yapılandırılmış kart payload’ları için `createMessageToolCardSchema()`

Bir şema şekli yalnızca tek bir sağlayıcı için anlamlıysa, onu paylaşılan SDK’ya yükseltmek yerine
o plugin’in kendi kaynak kodunda tanımlayın.

## Kanal hedef çözümleme

Kanal plugin’leri, kanala özgü hedef semantiğini sahiplenmelidir. Paylaşılan
giden ana makineyi genel tutun ve sağlayıcı kuralları için mesajlaşma adaptör yüzeyini kullanın:

- `messaging.inferTargetChatType({ to })`, normalize edilmiş bir hedefin dizin aramasından önce
  `direct`, `group` veya `channel` olarak ele alınıp alınmayacağına karar verir.
- `messaging.targetResolver.looksLikeId(raw, normalized)`, bir
  girdinin dizin araması yerine doğrudan kimlik benzeri çözümlemeye atlaması gerekip gerekmediğini çekirdeğe söyler.
- `messaging.targetResolver.resolveTarget(...)`, çekirdeğin normalizasyon sonrası veya
  dizin kaçırma sonrası son bir sağlayıcı sahipli çözümlemeye ihtiyaç duyduğunda kullandığı plugin fallback’idir.
- `messaging.resolveOutboundSessionRoute(...)`, bir hedef çözümlendikten sonra
  sağlayıcıya özgü oturum rota oluşturmayı sahiplenir.

Önerilen ayrım:

- Eşler/gruplar aranmeden önce gerçekleşmesi gereken kategori kararları için `inferTargetChatType` kullanın.
- "Bunu açık/yerel hedef kimliği olarak ele al" kontrolleri için `looksLikeId` kullanın.
- Geniş dizin araması için değil, sağlayıcıya özgü normalizasyon fallback’i için `resolveTarget` kullanın.
- Sohbet kimlikleri, iş parçacığı kimlikleri, JID’ler, handle’lar ve oda kimlikleri gibi sağlayıcıya özgü yerel kimlikleri,
  genel SDK alanlarında değil `target` değerleri veya sağlayıcıya özgü parametreler içinde tutun.

## Yapılandırma destekli dizinler

Yapılandırmadan dizin girdileri türeten plugin’ler bu mantığı
plugin içinde tutmalı ve
`openclaw/plugin-sdk/directory-runtime` içindeki paylaşılan yardımcıları yeniden kullanmalıdır.

Bir kanalın aşağıdakiler gibi yapılandırma destekli eşlere/gruplara ihtiyacı olduğunda bunu kullanın:

- allowlist güdümlü DM eşleri
- yapılandırılmış kanal/grup eşlemeleri
- hesap kapsamlı statik dizin fallback’leri

`directory-runtime` içindeki paylaşılan yardımcılar yalnızca genel işlemleri yürütür:

- sorgu filtreleme
- sınır uygulama
- tekilleştirme/normalizasyon yardımcıları
- `ChannelDirectoryEntry[]` oluşturma

Kanala özgü hesap inceleme ve kimlik normalizasyonu, plugin uygulamasında kalmalıdır.

## Sağlayıcı katalogları

Sağlayıcı plugin’leri,
`registerProvider({ catalog: { run(...) { ... } } })` ile çıkarım için model katalogları tanımlayabilir.

`catalog.run(...)`, OpenClaw’ın
`models.providers` içine yazdığıyla aynı şekli döndürür:

- tek sağlayıcı girdisi için `{ provider }`
- çok sağlayıcı girdisi için `{ providers }`

Sağlayıcıya ait model kimlikleri, varsayılan base URL’ler veya auth kapılı model meta verileri plugin’e aitse
`catalog` kullanın.

`catalog.order`, bir plugin’in kataloğunun OpenClaw’ın
yerleşik örtük sağlayıcılarına göre ne zaman birleşeceğini belirler:

- `simple`: düz API anahtarı veya env güdümlü sağlayıcılar
- `profile`: auth profilleri olduğunda görünen sağlayıcılar
- `paired`: birden çok ilişkili sağlayıcı girdisi sentezleyen sağlayıcılar
- `late`: diğer örtük sağlayıcılardan sonra son geçiş

Daha geç gelen sağlayıcılar anahtar çakışmasında kazanır; böylece plugin’ler aynı
sağlayıcı kimliğine sahip yerleşik bir sağlayıcı girdisini kasıtlı olarak geçersiz kılabilir.

Uyumluluk:

- `discovery`, eski bir takma ad olarak hâlâ çalışır
- hem `catalog` hem `discovery` kaydedilmişse OpenClaw `catalog` kullanır

## Salt okunur kanal incelemesi

Plugin’iniz bir kanal kaydediyorsa,
`resolveAccount(...)` yanında `plugin.config.inspectAccount(cfg, accountId)` uygulamayı tercih edin.

Neden:

- `resolveAccount(...)` çalışma zamanı yoludur. Kimlik bilgilerinin
  tamamen materyalize olduğunu varsayabilir ve gereken gizli değerler eksikse hızlıca başarısız olabilir.
- `openclaw status`, `openclaw status --all`,
  `openclaw channels status`, `openclaw channels resolve` ve doctor/config
  onarım akışları gibi salt okunur komut yolları, yalnızca yapılandırmayı
  tanımlamak için çalışma zamanı kimlik bilgilerini materyalize etmeye ihtiyaç duymamalıdır.

Önerilen `inspectAccount(...)` davranışı:

- Yalnızca açıklayıcı hesap durumunu döndürün.
- `enabled` ve `configured` değerlerini koruyun.
- İlgili olduğunda kimlik bilgisi kaynağı/durumu alanlarını ekleyin; örneğin:
  - `tokenSource`, `tokenStatus`
  - `botTokenSource`, `botTokenStatus`
  - `appTokenSource`, `appTokenStatus`
  - `signingSecretSource`, `signingSecretStatus`
- Salt okunur kullanılabilirliği raporlamak için ham token değerleri döndürmeniz gerekmez.
  `tokenStatus: "available"` döndürmek (ve eşleşen kaynak alanı) durum tarzı komutlar için yeterlidir.
- Bir kimlik bilgisi SecretRef yoluyla yapılandırılmış ama
  mevcut komut yolunda kullanılamıyorsa `configured_unavailable` kullanın.

Bu, salt okunur komutların "bu komut yolunda yapılandırılmış ama kullanılamıyor"
durumunu raporlamasına olanak tanır; çökmeden veya hesabı
yapılandırılmamış diye yanlış raporlamadan.

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

Her giriş bir plugin olur. Paket birden çok uzantı listeliyorsa plugin kimliği
`name/<fileBase>` olur.

Plugin’iniz npm bağımlılıkları içe aktarıyorsa, `node_modules`
kullanılabilir olsun diye bunları o dizinde kurun (`npm install` / `pnpm install`).

Güvenlik kuralı: her `openclaw.extensions` girdisi, sembolik bağlantı çözümlemesinden sonra
plugin dizini içinde kalmalıdır. Paket dizininden taşan girdiler
reddedilir.

Güvenlik notu: `openclaw plugins install`, plugin bağımlılıklarını
`npm install --omit=dev --ignore-scripts` ile kurar (yaşam döngüsü betikleri yok, çalışma zamanında geliştirme bağımlılıkları yok). Plugin bağımlılık
ağaçlarını "saf JS/TS" tutun ve `postinstall` derlemeleri gerektiren paketlerden kaçının.

İsteğe bağlı: `openclaw.setupEntry`, hafif bir yalnızca kurulum modülüne işaret edebilir.
OpenClaw, devre dışı bir kanal plugin’i için kurulum yüzeylerine ihtiyaç duyduğunda veya
bir kanal plugin’i etkin ama henüz yapılandırılmamış olduğunda, tam plugin girdisi yerine
`setupEntry` yükler. Bu, ana plugin girişiniz ayrıca araçlar, hook’lar veya diğer yalnızca çalışma zamanı
kodlarını da bağlıyorsa başlangıcı ve kurulumu daha hafif tutar.

İsteğe bağlı: `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`,
bir kanal plugin’inin, kanal zaten yapılandırılmış olsa bile gateway’in
dinleme öncesi başlangıç aşamasında aynı `setupEntry` yoluna katılmasına izin verebilir.

Bunu yalnızca `setupEntry`, gateway dinlemeye başlamadan
önce var olması gereken başlangıç yüzeyini tam olarak kapsıyorsa kullanın. Pratikte bu,
kurulum girdisinin başlangıcın bağımlı olduğu her kanal sahipli capability’yi kaydetmesi gerektiği anlamına gelir; örneğin:

- kanal kaydının kendisi
- gateway dinlemeye başlamadan önce kullanılabilir olması gereken tüm HTTP rotaları
- aynı pencere içinde var olması gereken tüm gateway yöntemleri, araçlar veya servisler

Tam girişiniz hâlâ gerekli herhangi bir başlangıç capability’sini sahipleniyorsa bu
bayrağı etkinleştirmeyin. Plugin’i varsayılan davranışta bırakın ve OpenClaw’ın
başlangıç sırasında tam girişi yüklemesine izin verin.

Paketlenmiş kanallar ayrıca, tam kanal çalışma zamanı yüklenmeden önce çekirdeğin
danışabileceği yalnızca kurulum sözleşme-yüzeyi yardımcılarını da yayımlayabilir. Mevcut kurulum
yükseltme yüzeyi şudur:

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

Çekirdek bu yüzeyi, tam plugin girişini yüklemeden eski tek hesaplı kanal
yapılandırmasını `channels.<id>.accounts.*` içine yükseltmesi gerektiğinde kullanır.
Matrix mevcut paketlenmiş örnektir: adlandırılmış hesaplar zaten varsa yalnızca auth/bootstrap
anahtarlarını adlandırılmış yükseltilmiş hesaba taşır ve her zaman
`accounts.default` oluşturmaktansa yapılandırılmış kanonik olmayan varsayılan hesap anahtarını koruyabilir.

Bu kurulum patch adaptörleri, paketlenmiş sözleşme-yüzeyi keşfini tembel tutar.
İçe aktarma zamanı hafif kalır; yükseltme yüzeyi ilk kullanımda yüklenir, modül içe aktarımında
paketlenmiş kanal başlangıcına yeniden girmez.

Bu başlangıç yüzeyleri gateway RPC yöntemleri içeriyorsa, onları
plugin’e özgü bir önek üzerinde tutun. Çekirdek yönetici ad alanları (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) ayrılmış kalır ve bir plugin
daha dar bir kapsam istese bile her zaman `operator.admin` değerine çözümlenir.

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

Kanal plugin’leri, `openclaw.channel` aracılığıyla kurulum/keşif meta verisi ve
`openclaw.install` aracılığıyla kurulum ipuçları bildirebilir. Bu, çekirdeği katalog verisinden bağımsız tutar.

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
      "blurb": "Self-hosted sohbet, Nextcloud Talk webhook botları üzerinden.",
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

Asgari örneğin ötesinde yararlı `openclaw.channel` alanları:

- daha zengin katalog/durum yüzeyleri için `detailLabel`: ikincil etiket
- belge bağlantısı metnini geçersiz kılmak için `docsLabel`
- bu katalog girdisinin geride bırakması gereken daha düşük öncelikli plugin/kanal kimlikleri için `preferOver`
- seçim yüzeyi metin denetimleri için `selectionDocsPrefix`, `selectionDocsOmitLabel`, `selectionExtras`
- giden biçimlendirme kararları için kanalın markdown desteklediğini işaretleyen `markdownCapable`
- `false` olduğunda kanalı yapılandırılmış kanal listeleme yüzeylerinden gizleyen `exposure.configured`
- `false` olduğunda kanalı etkileşimli kurulum/yapılandırma seçicilerinden gizleyen `exposure.setup`
- belge gezinme yüzeyleri için kanalı iç/özel olarak işaretleyen `exposure.docs`
- eski takma adlar olarak `showConfigured` / `showInSetup` hâlâ uyumluluk için kabul edilir; `exposure` tercih edilir
- kanalı standart quickstart `allowFrom` akışına dahil eden `quickstartAllowFrom`
- yalnızca tek hesap olsa bile açık hesap bağlamasını zorunlu kılan `forceAccountBinding`
- duyuru hedefleri çözülürken oturum aramasını tercih eden `preferSessionLookupForAnnounceTarget`

OpenClaw ayrıca **harici kanal kataloglarını** da birleştirebilir (örneğin bir MPM
kayıt sistemi dışa aktarımı). Şu konumlardan birine bir JSON dosyası bırakın:

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

Veya `OPENCLAW_PLUGIN_CATALOG_PATHS` (ya da `OPENCLAW_MPM_CATALOG_PATHS`) ile
bir veya daha fazla JSON dosyasına işaret edin (virgül/noktalı virgül/`PATH` ile ayrılmış). Her dosya
şunu içermelidir: `{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }`. Ayrıştırıcı ayrıca `"entries"` anahtarı için eski takma adlar olarak `"packages"` veya `"plugins"` anahtarlarını da kabul eder.

## Bağlam motoru plugin’leri

Bağlam motoru plugin’leri, alma, derleme
ve sıkıştırma için oturum bağlamı orkestrasyonunu sahiplenir. Bunları plugin’inizden
`api.registerContextEngine(id, factory)` ile kaydedin, ardından etkin motoru
`plugins.slots.contextEngine` ile seçin.

Varsayılan bağlam
hattını yalnızca bellek araması veya hook’lar eklemek yerine değiştirmek ya da genişletmek isteyen plugin’lerde bunu kullanın.

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

## Yeni bir capability ekleme

Bir plugin mevcut API’ye uymayan davranışa ihtiyaç duyduğunda,
özel bir içeri uzanımla plugin sistemini baypas etmeyin. Eksik capability’yi ekleyin.

Önerilen sıra:

1. çekirdek sözleşmesini tanımlayın
   Çekirdeğin hangi paylaşılan davranışı sahiplenmesi gerektiğine karar verin: politika, fallback, yapılandırma birleştirme,
   yaşam döngüsü, kanal odaklı semantik ve çalışma zamanı yardımcı şekli.
2. tipli plugin kayıt/çalışma zamanı yüzeylerini ekleyin
   `OpenClawPluginApi` ve/veya `api.runtime` içinde mümkün olan en küçük kullanışlı
   tipli capability yüzeyini genişletin.
3. çekirdek + kanal/özellik tüketicilerini bağlayın
   Kanallar ve özellik plugin’leri yeni capability’yi doğrudan satıcı uygulaması içe aktarmakla değil,
   çekirdek üzerinden tüketmelidir.
4. satıcı uygulamalarını kaydedin
   Satıcı plugin’leri daha sonra arka uçlarını bu capability’ye karşı kaydeder.
5. sözleşme kapsamı ekleyin
   Sahipliğin ve kayıt şeklinin zaman içinde açık kalması için testler ekleyin.

OpenClaw bu şekilde fikir sahibi kalırken tek bir
sağlayıcının dünya görüşüne sabitlenmez. Somut bir dosya kontrol listesi ve işlenmiş örnek için
[Capability Cookbook](/tr/plugins/architecture) sayfasına bakın.

### Capability kontrol listesi

Yeni bir capability eklediğinizde, uygulama genellikle şu
yüzeylere birlikte dokunmalıdır:

- `src/<capability>/types.ts` içindeki çekirdek sözleşme tipleri
- `src/<capability>/runtime.ts` içindeki çekirdek çalıştırıcı/çalışma zamanı yardımcısı
- `src/plugins/types.ts` içindeki plugin API kayıt yüzeyi
- `src/plugins/registry.ts` içindeki plugin kayıt sistemi kablolaması
- özellik/kanal plugin’lerinin tüketmesi gerekiyorsa `src/plugins/runtime/*` içindeki plugin çalışma zamanı dışa aktarımı
- `src/test-utils/plugin-registration.ts` içindeki yakalama/test yardımcıları
- `src/plugins/contracts/registry.ts` içindeki sahiplik/sözleşme doğrulamaları
- `docs/` içindeki operatör/plugin belgeleri

Bu yüzeylerden biri eksikse, bu genellikle capability’nin henüz tam
entegre olmadığının işaretidir.

### Capability şablonu

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

Bu, kuralı basit tutar:

- çekirdek capability sözleşmesini + orkestrasyonu sahiplenir
- satıcı plugin’leri satıcı uygulamalarını sahiplenir
- özellik/kanal plugin’leri çalışma zamanı yardımcılarını tüketir
- sözleşme testleri sahipliği açık tutar
