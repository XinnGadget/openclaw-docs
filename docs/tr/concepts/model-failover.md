---
read_when:
    - Auth profili döndürmeyi, cooldown sürelerini veya model yedekleme davranışını teşhis ediyorsunuz
    - Auth profilleri veya modeller için yedekleme kurallarını güncelliyorsunuz
    - Oturum model geçersiz kılmalarının yedekleme yeniden denemeleriyle nasıl etkileşime girdiğini anlamak istiyorsunuz
summary: OpenClaw'ın modeller arasında auth profillerini nasıl döndürdüğü ve yedeklemeye geçtiği
title: Model Yedekleme
x-i18n:
    generated_at: "2026-04-07T08:44:36Z"
    model: gpt-5.4
    provider: openai
    source_hash: d88821e229610f236bdab3f798d5e8c173f61a77c01017cc87431126bf465e32
    source_path: concepts/model-failover.md
    workflow: 15
---

# Model yedekleme

OpenClaw hataları iki aşamada ele alır:

1. Geçerli sağlayıcı içinde **auth profili döndürme**.
2. `agents.defaults.model.fallbacks` içindeki bir sonraki modele **model yedekleme**.

Bu belge çalışma zamanı kurallarını ve bunları destekleyen verileri açıklar.

## Çalışma zamanı akışı

Normal bir metin çalıştırması için OpenClaw adayları şu sırayla değerlendirir:

1. O anda seçili oturum modeli.
2. Sıralı şekilde yapılandırılmış `agents.defaults.model.fallbacks`.
3. Çalıştırma bir geçersiz kılma ile başladıysa sonda yapılandırılmış birincil model.

Her aday içinde OpenClaw, bir sonraki model adayına geçmeden önce auth profili
yedeklemesini dener.

Yüksek seviyeli sıra:

1. Etkin oturum modelini ve auth profili tercihini çözümle.
2. Model aday zincirini oluştur.
3. Auth profili döndürme/cooldown kurallarıyla geçerli sağlayıcıyı dene.
4. Bu sağlayıcı yedeklemeye uygun bir hatayla tükenirse, bir sonraki model
   adayına geç.
5. Yeniden deneme başlamadan önce seçilen yedek geçersiz kılmayı kalıcı hale getir ki diğer
   oturum okuyucuları çalıştırıcının kullanmak üzere olduğu aynı sağlayıcıyı/modeli görsün.
6. Yedek aday başarısız olursa, yalnızca yedek adaya ait oturum
   geçersiz kılma alanlarını, hâlâ o başarısız adayla eşleşiyorlarsa geri al.
7. Her aday başarısız olursa, deneme başına ayrıntı ve biliniyorsa
   en yakın cooldown bitiş zamanı ile bir `FallbackSummaryError` fırlat.

Bu bilerek "tüm oturumu kaydet ve geri yükle" yaklaşımından daha dardır. Yanıt
çalıştırıcısı yedekleme için yalnızca sahip olduğu model seçimi alanlarını kalıcı hale getirir:

- `providerOverride`
- `modelOverride`
- `authProfileOverride`
- `authProfileOverrideSource`
- `authProfileOverrideCompactionCount`

Bu, başarısız bir yedek yeniden denemesinin, deneme çalışırken gerçekleşmiş
manuel `/model` değişiklikleri veya oturum döndürme güncellemeleri gibi daha yeni,
ilgisiz oturum mutasyonlarının üzerine yazmasını engeller.

## Auth depolama (anahtarlar + OAuth)

OpenClaw hem API anahtarları hem de OAuth belirteçleri için **auth profilleri** kullanır.

- Gizli bilgiler `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` içinde bulunur (eski: `~/.openclaw/agent/auth-profiles.json`).
- Çalışma zamanı auth yönlendirme durumu `~/.openclaw/agents/<agentId>/agent/auth-state.json` içinde bulunur.
- `auth.profiles` / `auth.order` yapılandırması yalnızca **üst veri + yönlendirme** içindir (gizli bilgi içermez).
- Eski yalnızca içe aktarma amaçlı OAuth dosyası: `~/.openclaw/credentials/oauth.json` (ilk kullanımda `auth-profiles.json` içine aktarılır).

Daha fazla ayrıntı: [/concepts/oauth](/tr/concepts/oauth)

Kimlik bilgisi türleri:

- `type: "api_key"` → `{ provider, key }`
- `type: "oauth"` → `{ provider, access, refresh, expires, email? }` (bazı sağlayıcılar için `projectId`/`enterpriseUrl` ile birlikte)

## Profil kimlikleri

OAuth oturum açmaları, birden fazla hesabın birlikte var olabilmesi için ayrı profiller oluşturur.

- Varsayılan: e-posta yoksa `provider:default`.
- E-posta ile OAuth: `provider:<email>` (örneğin `google-antigravity:user@gmail.com`).

Profiller, `profiles` altında `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` içinde bulunur.

## Döndürme sırası

Bir sağlayıcının birden fazla profili olduğunda OpenClaw şu şekilde bir sıra seçer:

1. **Açık yapılandırma**: `auth.order[provider]` (ayarlanmışsa).
2. **Yapılandırılmış profiller**: sağlayıcıya göre filtrelenmiş `auth.profiles`.
3. **Depolanmış profiller**: sağlayıcı için `auth-profiles.json` içindeki girdiler.

Açık bir sıra yapılandırılmamışsa OpenClaw round-robin bir sıra kullanır:

- **Birincil anahtar:** profil türü (**API anahtarlarından önce OAuth**).
- **İkincil anahtar:** `usageStats.lastUsed` (her tür içinde en eski önce).
- **Cooldown/devre dışı profiller** en sona taşınır ve en yakın bitiş süresine göre sıralanır.

### Oturum sabitleme (önbellek dostu)

OpenClaw, sağlayıcı önbelleklerini sıcak tutmak için **seçilen auth profilini oturum başına sabitler**.
Her istekte döndürme yapmaz. Sabitlenen profil şu durumlara kadar yeniden kullanılır:

- oturum sıfırlanırsa (`/new` / `/reset`)
- bir sıkıştırma tamamlanırsa (sıkıştırma sayısı artar)
- profil cooldown durumundaysa/devre dışıysa

`/model …@<profileId>` ile manuel seçim, o oturum için bir **kullanıcı geçersiz kılması**
ayarlar ve yeni bir oturum başlayana kadar otomatik olarak döndürülmez.

Otomatik olarak sabitlenen profiller (oturum yönlendiricisi tarafından seçilenler) bir **tercih**
olarak değerlendirilir: önce onlar denenir, ancak OpenClaw hız sınırlarında/zaman aşımlarında başka bir profile dönebilir.
Kullanıcı tarafından sabitlenen profiller o profile kilitli kalır; başarısız olursa ve model yedeklemeleri
yapılandırılmışsa, OpenClaw profil değiştirmek yerine bir sonraki modele geçer.

### OAuth neden "kaybolmuş" gibi görünebilir

Aynı sağlayıcı için hem bir OAuth profiliniz hem de bir API anahtarı profiliniz varsa, round-robin sabitlenmediği sürece mesajlar arasında bunlar arasında geçiş yapabilir. Tek bir profili zorlamak için:

- `auth.order[provider] = ["provider:profileId"]` ile sabitleyin veya
- UI/chat yüzeyiniz destekliyorsa profil geçersiz kılması içeren `/model …` ile oturum başına bir geçersiz kılma kullanın.

## Cooldown süreleri

Bir profil auth/hız sınırı hataları nedeniyle başarısız olduğunda (veya hız sınırlaması gibi
görünen bir zaman aşımında), OpenClaw onu cooldown durumuna işaretler ve bir sonraki profile geçer.
Bu hız sınırı kovası yalnızca `429` ile sınırlı değildir: sağlayıcı
mesajlarını da içerir; örneğin `Too many concurrent requests`, `ThrottlingException`,
`concurrency limit reached`, `workers_ai ... quota limit exceeded`,
`throttled`, `resource exhausted` ve `weekly/monthly limit reached`
gibi dönemsel kullanım penceresi sınırları.
Biçim/geçersiz istek hataları (örneğin Cloud Code Assist tool call ID
doğrulama hataları) yedeklemeye uygun kabul edilir ve aynı cooldown sürelerini kullanır.
`Unhandled stop reason: error`,
`stop reason: error` ve `reason: error` gibi OpenAI uyumlu durdurma nedeni hataları, zaman aşımı/yedekleme
sinyalleri olarak sınıflandırılır.
Sağlayıcı kapsamlı genel sunucu metinleri de, kaynak bilinen geçici bir desenle eşleştiğinde,
bu zaman aşımı kovasına girebilir. Örneğin Anthropic için yalın
`An unknown error occurred` ve `internal server error`, `unknown error, 520`, `upstream error`
veya `backend error` gibi geçici sunucu metinleri içeren JSON `api_error`
yükleri, yedeklemeye uygun zaman aşımı olarak değerlendirilir. OpenRouter'a özgü
yalın `Provider returned error` gibi genel upstream metinleri de yalnızca
sağlayıcı bağlamı gerçekten OpenRouter olduğunda zaman aşımı olarak değerlendirilir. `LLM request failed with an unknown error.` gibi
genel dahili yedek metinler temkinli kalır ve tek başına yedeklemeyi tetiklemez.

Hız sınırı cooldown süreleri model kapsamlı da olabilir:

- OpenClaw, başarısız model kimliği biliniyorsa hız sınırı hataları için `cooldownModel` kaydeder.
- Aynı sağlayıcıdaki kardeş bir model, cooldown farklı bir modele
  kapsamlanmışsa yine de denenebilir.
- Faturalama/devre dışı pencereleri ise modeller arasında tüm profili engellemeye devam eder.

Cooldown süreleri üstel geri çekilme kullanır:

- 1 dakika
- 5 dakika
- 25 dakika
- 1 saat (üst sınır)

Durum, `usageStats` altında `auth-state.json` içinde saklanır:

```json
{
  "usageStats": {
    "provider:profile": {
      "lastUsed": 1736160000000,
      "cooldownUntil": 1736160600000,
      "errorCount": 2
    }
  }
}
```

## Faturalama nedeniyle devre dışı bırakmalar

Faturalama/kredi hataları (örneğin “insufficient credits” / “credit balance too low”) yedeklemeye uygun kabul edilir, ancak genellikle geçici değildir. Kısa bir cooldown yerine OpenClaw, profili **devre dışı** olarak işaretler (daha uzun bir geri çekilme ile) ve bir sonraki profile/sağlayıcıya döner.

Her faturalama benzeri yanıt `402` değildir ve her HTTP `402` de buraya düşmez.
OpenClaw, bir sağlayıcı bunun yerine `401` veya `403` döndürse bile açık
faturalama metnini faturalama yolunda tutar, ancak sağlayıcıya özgü eşleştiriciler
onlara sahip olan sağlayıcıyla sınırlı kalır (örneğin OpenRouter `403 Key limit
exceeded`). Buna karşılık geçici `402` kullanım penceresi ve
kuruluş/çalışma alanı harcama sınırı hataları, ileti yeniden denenebilir göründüğünde `rate_limit` olarak sınıflandırılır
(örneğin `weekly usage limit exhausted`, `daily
limit reached, resets tomorrow` veya `organization spending limit exceeded`).
Bunlar uzun
faturalama-devre dışı bırakma yolu yerine kısa cooldown/yedekleme yolunda kalır.

Durum `auth-state.json` içinde saklanır:

```json
{
  "usageStats": {
    "provider:profile": {
      "disabledUntil": 1736178000000,
      "disabledReason": "billing"
    }
  }
}
```

Varsayılanlar:

- Faturalama geri çekilmesi **5 saatten** başlar, her faturalama hatasında iki katına çıkar ve **24 saatte** sınırlanır.
- Geri çekilme sayaçları, profil **24 saat** boyunca başarısız olmamışsa sıfırlanır (yapılandırılabilir).
- Aşırı yük yeniden denemeleri, model yedeklemeden önce **aynı sağlayıcı içinde 1 auth profili döndürmeye** izin verir.
- Aşırı yük yeniden denemeleri varsayılan olarak **0 ms geri çekilme** kullanır.

## Model yedekleme

Bir sağlayıcıdaki tüm profiller başarısız olursa OpenClaw,
`agents.defaults.model.fallbacks` içindeki bir sonraki modele geçer. Bu durum auth hataları, hız sınırları ve
profil döndürmeyi tüketen zaman aşımları için geçerlidir (diğer hatalar yedeklemeyi ilerletmez).

Aşırı yük ve hız sınırı hataları, faturalama cooldown sürelerinden daha agresif ele alınır.
Varsayılan olarak OpenClaw bir kez aynı sağlayıcı auth profili yeniden denemesine izin verir,
ardından beklemeden yapılandırılmış bir sonraki model yedeğine geçer.
`ModelNotReadyException` gibi sağlayıcı meşgul sinyalleri bu aşırı yük kovasına düşer.
Bunu `auth.cooldowns.overloadedProfileRotations`,
`auth.cooldowns.overloadedBackoffMs` ve
`auth.cooldowns.rateLimitedProfileRotations` ile ayarlayın.

Bir çalıştırma bir model geçersiz kılmasıyla başladığında (hook'lar veya CLI), yedeklemeler yapılandırılmış yedekler denendikten sonra yine de `agents.defaults.model.primary` ile sonlanır.

### Aday zinciri kuralları

OpenClaw aday listesini o anda istenen `provider/model`
ile yapılandırılmış yedeklerden oluşturur.

Kurallar:

- İstenen model her zaman ilk sıradadır.
- Açıkça yapılandırılmış yedekler yinelenenlerden arındırılır ancak model
  izin listesinden filtrelenmez. Açık operatör niyeti olarak değerlendirilirler.
- Geçerli çalıştırma zaten aynı sağlayıcı
  ailesindeki yapılandırılmış bir yedek üzerindeyse, OpenClaw tüm yapılandırılmış zinciri kullanmaya devam eder.
- Geçerli çalıştırma yapılandırmadan farklı bir sağlayıcı üzerindeyse ve bu geçerli
  model zaten yapılandırılmış yedek zincirinin bir parçası değilse, OpenClaw başka bir sağlayıcıdan
  ilgisiz yapılandırılmış yedekleri eklemez.
- Çalıştırma bir geçersiz kılma ile başladıysa, daha önceki
  adaylar tükendiğinde zincirin yeniden normal varsayılana yerleşebilmesi için yapılandırılmış birincil en sona eklenir.

### Hangi hatalar yedeklemeyi ilerletir

Model yedekleme şu durumlarda devam eder:

- auth hataları
- hız sınırları ve cooldown tükenmesi
- aşırı yük/sağlayıcı meşgul hataları
- zaman aşımı biçimli yedekleme hataları
- faturalama nedeniyle devre dışı bırakmalar
- `LiveSessionModelSwitchError`; bu, eski bir kalıcı modelin dış bir yeniden deneme döngüsü oluşturmaması için
  yedekleme yoluna normalize edilir
- başka tanınmayan hatalar, hâlâ kalan adaylar varsa

Model yedekleme şu durumlarda devam etmez:

- zaman aşımı/yedekleme biçiminde olmayan açık iptaller
- sıkıştırma/yeniden deneme mantığı içinde kalması gereken bağlam taşması hataları
  (örneğin `request_too_large`, `INVALID_ARGUMENT: input exceeds the maximum
number of tokens`, `input token count exceeds the maximum number of input
tokens`, `The input is too long for the model` veya `ollama error: context
length exceeded`)
- aday kalmadığında son bir bilinmeyen hata

### Cooldown atlama ve yoklama davranışı

Bir sağlayıcı için her auth profili zaten cooldown durumundaysa OpenClaw
o sağlayıcıyı otomatik olarak sonsuza kadar atlamaz. Aday başına karar verir:

- Kalıcı auth hataları tüm sağlayıcıyı hemen atlar.
- Faturalama nedeniyle devre dışı bırakmalar genellikle atlanır, ancak kurtarma
  yeniden başlatmadan mümkün olsun diye birincil aday yine de bir sınırlama ile yoklanabilir.
- Birincil aday, sağlayıcı başına bir sınırlama ile cooldown bitimine yakın yoklanabilir.
- Aynı sağlayıcıdaki yedek kardeşler, hata geçici görünüyorsa (`rate_limit`, `overloaded` veya bilinmeyen), cooldown'a rağmen denenebilir. Bu,
  özellikle bir hız sınırı model kapsamlı olduğunda ve kardeş bir model hemen toparlanabilecekse önemlidir.
- Geçici cooldown yoklamaları, tek bir sağlayıcının sağlayıcılar arası yedeklemeyi durdurmaması için yedekleme çalıştırması başına sağlayıcı başına bir taneyle sınırlıdır.

## Oturum geçersiz kılmaları ve canlı model geçişi

Oturum modeli değişiklikleri paylaşılan durumdur. Etkin çalıştırıcı, `/model` komutu,
sıkıştırma/oturum güncellemeleri ve canlı oturum uzlaştırması aynı oturum girdisinin
bölümlerini okur veya yazar.

Bu da yedek yeniden denemelerinin canlı model geçişiyle eşgüdüm kurması gerektiği anlamına gelir:

- Yalnızca açık kullanıcı odaklı model değişiklikleri bekleyen bir canlı geçişi işaretler. Buna
  `/model`, `session_status(model=...)` ve `sessions.patch` dahildir.
- Yedek döndürme, heartbeat geçersiz kılmaları
  veya sıkıştırma gibi sistem odaklı model değişiklikleri kendi başına bekleyen bir canlı geçiş işaretlemez.
- Bir yedek yeniden deneme başlamadan önce yanıt çalıştırıcısı seçilen
  yedek geçersiz kılma alanlarını oturum girdisine kalıcı hale getirir.
- Canlı oturum uzlaştırması, eski çalışma zamanı model alanları yerine kalıcı oturum geçersiz kılmalarını tercih eder.
- Yedek denemesi başarısız olursa çalıştırıcı, yalnızca yazdığı geçersiz kılma alanlarını
  ve yalnızca bunlar hâlâ o başarısız adayla eşleşiyorsa geri alır.

Bu, klasik yarış durumunu önler:

1. Birincil model başarısız olur.
2. Yedek aday bellekte seçilir.
3. Oturum deposu hâlâ eski birinciliği gösterir.
4. Canlı oturum uzlaştırması eski oturum durumunu okur.
5. Yeniden deneme, yedek deneme başlamadan önce eski modele geri çekilir.

Kalıcı yedek geçersiz kılması bu boşluğu kapatır ve dar geri alma,
daha yeni manuel veya çalışma zamanı oturum değişikliklerini korur.

## Gözlemlenebilirlik ve hata özetleri

`runWithModelFallback(...)`, günlükleri ve kullanıcıya dönük cooldown mesajlarını besleyen deneme başına ayrıntıları kaydeder:

- denenen sağlayıcı/model
- neden (`rate_limit`, `overloaded`, `billing`, `auth`, `model_not_found` ve
  benzer yedekleme nedenleri)
- isteğe bağlı durum/kod
- insan tarafından okunabilir hata özeti

Her aday başarısız olduğunda OpenClaw `FallbackSummaryError` fırlatır. Dış yanıt
çalıştırıcısı bunu "tüm modeller geçici olarak hız sınırına takıldı" gibi daha
özel bir mesaj oluşturmak ve biliniyorsa en yakın cooldown bitiş süresini eklemek için kullanabilir.

Bu cooldown özeti model farkındalığına sahiptir:

- denenen
  sağlayıcı/model zinciri için ilgisiz model kapsamlı hız sınırları yok sayılır
- kalan engel eşleşen model kapsamlı bir hız sınırıysa, OpenClaw
  hâlâ o modeli engelleyen son eşleşen bitiş zamanını bildirir

## İlgili yapılandırma

Şunlar için [Gateway configuration](/tr/gateway/configuration) belgesine bakın:

- `auth.profiles` / `auth.order`
- `auth.cooldowns.billingBackoffHours` / `auth.cooldowns.billingBackoffHoursByProvider`
- `auth.cooldowns.billingMaxHours` / `auth.cooldowns.failureWindowHours`
- `auth.cooldowns.overloadedProfileRotations` / `auth.cooldowns.overloadedBackoffMs`
- `auth.cooldowns.rateLimitedProfileRotations`
- `agents.defaults.model.primary` / `agents.defaults.model.fallbacks`
- `agents.defaults.imageModel` yönlendirmesi

Daha geniş model seçimi ve yedekleme genel görünümü için [Models](/tr/concepts/models) belgesine bakın.
