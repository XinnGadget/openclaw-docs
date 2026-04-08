---
read_when:
    - OpenClaw içinde Matrix kurulumu
    - Matrix E2EE ve doğrulamayı yapılandırma
summary: Matrix destek durumu, kurulum ve yapılandırma örnekleri
title: Matrix
x-i18n:
    generated_at: "2026-04-08T02:16:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: ec926df79a41fa296d63f0ec7219d0f32e075628d76df9ea490e93e4c5030f83
    source_path: channels/matrix.md
    workflow: 15
---

# Matrix

Matrix, OpenClaw için Matrix paketlenmiş kanal eklentisidir.
Resmi `matrix-js-sdk` kullanır ve DM'leri, odaları, ileti dizilerini, medyayı, tepkileri, anketleri, konumu ve E2EE'yi destekler.

## Paketlenmiş eklenti

Matrix, mevcut OpenClaw sürümlerinde paketlenmiş bir eklenti olarak gelir; bu nedenle normal
paketlenmiş derlemeler ayrı bir kurulum gerektirmez.

Daha eski bir derlemeyi veya Matrix'i içermeyen özel bir kurulumu kullanıyorsanız,
onu manuel olarak yükleyin:

npm'den yükleyin:

```bash
openclaw plugins install @openclaw/matrix
```

Yerel bir checkout'tan yükleyin:

```bash
openclaw plugins install ./path/to/local/matrix-plugin
```

Eklenti davranışı ve kurulum kuralları için [Eklentiler](/tr/tools/plugin) bölümüne bakın.

## Kurulum

1. Matrix eklentisinin kullanılabilir olduğundan emin olun.
   - Güncel paketlenmiş OpenClaw sürümleri zaten bunu paketlenmiş olarak içerir.
   - Eski/özel kurulumlar yukarıdaki komutlarla bunu manuel olarak ekleyebilir.
2. Homeserver'ınızda bir Matrix hesabı oluşturun.
3. `channels.matrix` yapılandırmasını şu seçeneklerden biriyle yapın:
   - `homeserver` + `accessToken`, veya
   - `homeserver` + `userId` + `password`.
4. Gateway'i yeniden başlatın.
5. Bot ile bir DM başlatın veya onu bir odaya davet edin.
   - Yeni Matrix davetleri yalnızca `channels.matrix.autoJoin` buna izin verdiğinde çalışır.

Etkileşimli kurulum yolları:

```bash
openclaw channels add
openclaw configure --section channels
```

Matrix sihirbazının gerçekte sorduğu şeyler:

- homeserver URL'si
- kimlik doğrulama yöntemi: access token veya parola
- yalnızca parola kimlik doğrulamasını seçtiğinizde kullanıcı kimliği
- isteğe bağlı cihaz adı
- E2EE'nin etkinleştirilip etkinleştirilmeyeceği
- Matrix oda erişiminin şimdi yapılandırılıp yapılandırılmayacağı
- Matrix davet otomatik katılımının şimdi yapılandırılıp yapılandırılmayacağı
- davet otomatik katılımı etkinleştirildiğinde bunun `allowlist`, `always` veya `off` olup olmayacağı

Önemli sihirbaz davranışları:

- Seçilen hesap için Matrix kimlik doğrulama ortam değişkenleri zaten mevcutsa ve bu hesap için yapılandırmada zaten kaydedilmiş kimlik doğrulama yoksa, sihirbaz bir ortam değişkeni kısayolu sunar; böylece kurulum, sırları yapılandırmaya kopyalamak yerine kimlik doğrulamayı ortam değişkenlerinde tutabilir.
- Etkileşimli olarak başka bir Matrix hesabı eklediğinizde, girilen hesap adı yapılandırma ve ortam değişkenlerinde kullanılan hesap kimliğine normalize edilir. Örneğin, `Ops Bot`, `ops-bot` olur.
- DM allowlist istemleri tam `@user:server` değerlerini hemen kabul eder. Görünen adlar yalnızca canlı dizin araması tek bir tam eşleşme bulduğunda çalışır; aksi halde sihirbaz sizden tam bir Matrix kimliği ile yeniden denemenizi ister.
- Oda allowlist istemleri oda kimliklerini ve takma adları doğrudan kabul eder. Ayrıca katılınmış oda adlarını canlı olarak çözebilirler, ancak çözümlenmeyen adlar yalnızca kurulum sırasında yazıldığı şekilde tutulur ve daha sonra çalışma zamanındaki allowlist çözümlemesi tarafından yok sayılır. `!room:server` veya `#alias:server` tercih edin.
- Sihirbaz artık davet otomatik katılımı adımından önce açık bir uyarı gösterir çünkü `channels.matrix.autoJoin` varsayılan olarak `off` durumundadır; siz ayarlamadığınız sürece ajanlar davet edilen odalara veya yeni DM tarzı davetlere katılmaz.
- Davet otomatik katılımı allowlist modunda yalnızca kararlı davet hedeflerini kullanın: `!roomId:server`, `#alias:server` veya `*`. Düz oda adları reddedilir.
- Çalışma zamanındaki oda/oturum kimliği kararlı Matrix oda kimliğini kullanır. Oda tarafından bildirilen takma adlar yalnızca arama girdileri olarak kullanılır; uzun vadeli oturum anahtarı veya kararlı grup kimliği olarak kullanılmaz.
- Oda adlarını kaydetmeden önce çözümlemek için `openclaw channels resolve --channel matrix "Project Room"` kullanın.

<Warning>
`channels.matrix.autoJoin` varsayılan olarak `off` durumundadır.

Bunu ayarlamazsanız bot davet edilen odalara veya yeni DM tarzı davetlere katılmaz; dolayısıyla siz önce manuel olarak katılmadığınız sürece yeni gruplarda veya davet edilen DM'lerde görünmez.

Hangi davetleri kabul edeceğini sınırlamak için `autoJoin: "allowlist"` ile birlikte `autoJoinAllowlist` ayarlayın ya da her davete katılmasını istiyorsanız `autoJoin: "always"` ayarlayın.

`allowlist` modunda `autoJoinAllowlist` yalnızca `!roomId:server`, `#alias:server` veya `*` kabul eder.
</Warning>

Allowlist örneği:

```json5
{
  channels: {
    matrix: {
      autoJoin: "allowlist",
      autoJoinAllowlist: ["!ops:example.org", "#support:example.org"],
      groups: {
        "!ops:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

Her davete katıl:

```json5
{
  channels: {
    matrix: {
      autoJoin: "always",
    },
  },
}
```

En küçük token tabanlı kurulum:

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      dm: { policy: "pairing" },
    },
  },
}
```

Parola tabanlı kurulum (girişten sonra token önbelleğe alınır):

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      userId: "@bot:example.org",
      password: "replace-me", // pragma: allowlist secret
      deviceName: "OpenClaw Gateway",
    },
  },
}
```

Matrix önbelleğe alınmış kimlik bilgilerini `~/.openclaw/credentials/matrix/` içinde saklar.
Varsayılan hesap `credentials.json` kullanır; adlandırılmış hesaplar `credentials-<account>.json` kullanır.
Önbelleğe alınmış kimlik bilgileri burada mevcut olduğunda, mevcut kimlik doğrulama doğrudan yapılandırmada ayarlı olmasa bile OpenClaw, kurulum, doctor ve kanal durumu keşfi için Matrix'i yapılandırılmış kabul eder.

Ortam değişkeni eşdeğerleri (yapılandırma anahtarı ayarlı olmadığında kullanılır):

- `MATRIX_HOMESERVER`
- `MATRIX_ACCESS_TOKEN`
- `MATRIX_USER_ID`
- `MATRIX_PASSWORD`
- `MATRIX_DEVICE_ID`
- `MATRIX_DEVICE_NAME`

Varsayılan olmayan hesaplar için hesap kapsamlı ortam değişkenlerini kullanın:

- `MATRIX_<ACCOUNT_ID>_HOMESERVER`
- `MATRIX_<ACCOUNT_ID>_ACCESS_TOKEN`
- `MATRIX_<ACCOUNT_ID>_USER_ID`
- `MATRIX_<ACCOUNT_ID>_PASSWORD`
- `MATRIX_<ACCOUNT_ID>_DEVICE_ID`
- `MATRIX_<ACCOUNT_ID>_DEVICE_NAME`

`ops` hesabı için örnek:

- `MATRIX_OPS_HOMESERVER`
- `MATRIX_OPS_ACCESS_TOKEN`

Normalize edilmiş `ops-bot` hesap kimliği için şunları kullanın:

- `MATRIX_OPS_X2D_BOT_HOMESERVER`
- `MATRIX_OPS_X2D_BOT_ACCESS_TOKEN`

Matrix, hesap kimliklerindeki noktalama işaretlerini kaçıralayarak kapsamlı ortam değişkenlerinde çakışmaları önler.
Örneğin, `-` karakteri `_X2D_` olur; dolayısıyla `ops-prod`, `MATRIX_OPS_X2D_PROD_*` eşlemesine dönüşür.

Etkileşimli sihirbaz, bu kimlik doğrulama ortam değişkenleri zaten mevcutsa ve seçilen hesap için yapılandırmada zaten kaydedilmiş Matrix kimlik doğrulaması yoksa, ortam değişkeni kısayolunu sunar.

## Yapılandırma örneği

Bu, DM eşleştirme, oda allowlist'i ve etkin E2EE içeren pratik bir temel yapılandırmadır:

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      encryption: true,

      dm: {
        policy: "pairing",
        sessionScope: "per-room",
        threadReplies: "off",
      },

      groupPolicy: "allowlist",
      groupAllowFrom: ["@admin:example.org"],
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },

      autoJoin: "allowlist",
      autoJoinAllowlist: ["!roomid:example.org"],
      threadReplies: "inbound",
      replyToMode: "off",
      streaming: "partial",
    },
  },
}
```

`autoJoin`, yalnızca oda/grup davetleri için değil, genel olarak Matrix davetleri için geçerlidir.
Buna yeni DM tarzı davetler de dahildir. Davet anında OpenClaw, davet edilen odanın sonunda bir DM mi yoksa bir grup mu olarak ele alınacağını
güvenilir biçimde bilemez; bu nedenle tüm davetler önce aynı `autoJoin` kararından geçer. Bot odaya katıldıktan ve oda bir DM olarak
sınıflandırıldıktan sonra `dm.policy` yine uygulanır; dolayısıyla `autoJoin` katılma davranışını, `dm.policy` ise yanıt/erişim
davranışını kontrol eder.

## Akış önizlemeleri

Matrix yanıt akışı isteğe bağlıdır.

OpenClaw'ın tek bir canlı önizleme yanıtı göndermesini, model metin üretirken bu önizlemeyi yerinde düzenlemesini
ve yanıt tamamlandığında bunu sonlandırmasını istediğinizde `channels.matrix.streaming` değerini `"partial"` olarak ayarlayın:

```json5
{
  channels: {
    matrix: {
      streaming: "partial",
    },
  },
}
```

- `streaming: "off"` varsayılandır. OpenClaw son yanıtı bekler ve onu bir kez gönderir.
- `streaming: "partial"`, mevcut asistan bloğu için normal Matrix metin mesajlarını kullanarak düzenlenebilir bir önizleme mesajı oluşturur. Bu, Matrix'in eski önizleme-önce bildirim davranışını korur; dolayısıyla standart istemciler bitmiş blok yerine ilk akış önizleme metni için bildirim gönderebilir.
- `streaming: "quiet"`, mevcut asistan bloğu için düzenlenebilir sessiz bir önizleme bildirimi oluşturur. Bunu yalnızca sonlandırılmış önizleme düzenlemeleri için alıcı push kuralları da yapılandırdığınızda kullanın.
- `blockStreaming: true` ayrı Matrix ilerleme mesajlarını etkinleştirir. Önizleme akışı etkin olduğunda Matrix, mevcut blok için canlı taslağı korur ve tamamlanan blokları ayrı mesajlar olarak saklar.
- Önizleme akışı açık ve `blockStreaming` kapalı olduğunda Matrix canlı taslağı yerinde düzenler ve blok veya dönüş tamamlandığında aynı olayı sonlandırır.
- Önizleme artık tek bir Matrix olayına sığmıyorsa OpenClaw önizleme akışını durdurur ve normal son teslimata geri döner.
- Medya yanıtları ekleri normal şekilde gönderir. Eski bir önizleme artık güvenli şekilde yeniden kullanılamıyorsa OpenClaw son medya yanıtını göndermeden önce onu redakte eder.
- Önizleme düzenlemeleri ek Matrix API çağrılarına mal olur. En muhafazakar rate-limit davranışını istiyorsanız akışı kapalı bırakın.

`blockStreaming` tek başına taslak önizlemeleri etkinleştirmez.
Önizleme düzenlemeleri için `streaming: "partial"` veya `streaming: "quiet"` kullanın; ardından yalnızca tamamlanmış asistan bloklarının ayrı ilerleme mesajları olarak görünür kalmasını da istiyorsanız `blockStreaming: true` ekleyin.

Özel push kuralları olmadan standart Matrix bildirimlerine ihtiyacınız varsa, önizleme-önce davranışı için `streaming: "partial"` kullanın veya yalnızca son teslimat için `streaming` değerini kapalı bırakın. `streaming: "off"` ile:

- `blockStreaming: true` her tamamlanmış bloğu normal bildirim veren bir Matrix mesajı olarak gönderir.
- `blockStreaming: false` yalnızca son tamamlanmış yanıtı normal bildirim veren bir Matrix mesajı olarak gönderir.

### Sessiz sonlandırılmış önizlemeler için self-hosted push kuralları

Kendi Matrix altyapınızı çalıştırıyorsanız ve sessiz önizlemelerin yalnızca bir blok veya
son yanıt tamamlandığında bildirim göndermesini istiyorsanız `streaming: "quiet"` ayarlayın ve sonlandırılmış önizleme düzenlemeleri için kullanıcı başına bir push kuralı ekleyin.

Bu genellikle homeserver genelinde bir yapılandırma değişikliği değil, alıcı kullanıcı kurulumu olur:

Başlamadan önce hızlı eşleme:

- alıcı kullanıcı = bildirimi alması gereken kişi
- bot kullanıcısı = yanıtı gönderen OpenClaw Matrix hesabı
- aşağıdaki API çağrıları için alıcı kullanıcının access token'ını kullanın
- push kuralındaki `sender` alanını bot kullanıcısının tam MXID değeriyle eşleştirin

1. OpenClaw'ı sessiz önizlemeleri kullanacak şekilde yapılandırın:

```json5
{
  channels: {
    matrix: {
      streaming: "quiet",
    },
  },
}
```

2. Alıcı hesabın zaten normal Matrix push bildirimleri aldığından emin olun. Sessiz önizleme
   kuralları yalnızca o kullanıcı için pushers/devices zaten çalışıyorsa işe yarar.

3. Alıcı kullanıcının access token'ını alın.
   - Botun token'ını değil, alan kullanıcının token'ını kullanın.
   - Mevcut bir istemci oturum token'ını yeniden kullanmak genellikle en kolay yoldur.
   - Yeni bir token üretmeniz gerekiyorsa, standart Matrix İstemci-Sunucu API'si üzerinden giriş yapabilirsiniz:

```bash
curl -sS -X POST \
  "https://matrix.example.org/_matrix/client/v3/login" \
  -H "Content-Type: application/json" \
  --data '{
    "type": "m.login.password",
    "identifier": {
      "type": "m.id.user",
      "user": "@alice:example.org"
    },
    "password": "REDACTED"
  }'
```

4. Alıcı hesabın zaten pushers içerdiğini doğrulayın:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushers"
```

Bu, etkin pushers/devices döndürmüyorsa aşağıdaki
OpenClaw kuralını eklemeden önce önce normal Matrix bildirimlerini düzeltin.

OpenClaw sonlandırılmış yalnızca metin içeren önizleme düzenlemelerini şu şekilde işaretler:

```json
{
  "com.openclaw.finalized_preview": true
}
```

5. Bu bildirimleri alması gereken her alıcı hesap için bir override push kuralı oluşturun:

```bash
curl -sS -X PUT \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname" \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "conditions": [
      { "kind": "event_match", "key": "type", "pattern": "m.room.message" },
      {
        "kind": "event_property_is",
        "key": "content.m\\.relates_to.rel_type",
        "value": "m.replace"
      },
      {
        "kind": "event_property_is",
        "key": "content.com\\.openclaw\\.finalized_preview",
        "value": true
      },
      { "kind": "event_match", "key": "sender", "pattern": "@bot:example.org" }
    ],
    "actions": [
      "notify",
      { "set_tweak": "sound", "value": "default" },
      { "set_tweak": "highlight", "value": false }
    ]
  }'
```

Komutu çalıştırmadan önce şu değerleri değiştirin:

- `https://matrix.example.org`: homeserver temel URL'niz
- `$USER_ACCESS_TOKEN`: alan kullanıcının access token'ı
- `openclaw-finalized-preview-botname`: bu alan kullanıcı için bu bota özel bir kural kimliği
- `@bot:example.org`: alan kullanıcının MXID'si değil, OpenClaw Matrix bot MXID'niz

Çok botlu kurulumlar için önemli:

- Push kuralları `ruleId` ile anahtarlanır. Aynı kural kimliğine karşı `PUT` komutunu yeniden çalıştırmak o tek kuralı günceller.
- Bir alan kullanıcının birden fazla OpenClaw Matrix bot hesabı için bildirim alması gerekiyorsa, her sender eşleşmesi için benzersiz bir kural kimliğiyle bot başına bir kural oluşturun.
- Basit bir desen `openclaw-finalized-preview-<botname>` şeklindedir; örneğin `openclaw-finalized-preview-ops` veya `openclaw-finalized-preview-support`.

Kural olay gönderenine göre değerlendirilir:

- alan kullanıcının token'ı ile kimlik doğrulaması yapın
- `sender` alanını OpenClaw bot MXID'siyle eşleştirin

6. Kuralın mevcut olduğunu doğrulayın:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

7. Akışlı bir yanıtı test edin. Sessiz modda odada sessiz bir taslak önizleme görünmeli ve son
   yerinde düzenleme blok veya dönüş tamamlandığında bir kez bildirim göndermelidir.

Kuralı daha sonra kaldırmanız gerekirse, alan kullanıcının token'ı ile aynı kural kimliğini silin:

```bash
curl -sS -X DELETE \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

Notlar:

- Kuralı botun token'ı ile değil, alan kullanıcının access token'ı ile oluşturun.
- Yeni kullanıcı tanımlı `override` kuralları varsayılan bastırma kurallarının önüne eklenir; bu nedenle ek bir sıralama parametresi gerekmez.
- Bu yalnızca OpenClaw'ın güvenli şekilde yerinde sonlandırabildiği yalnızca metin içeren önizleme düzenlemelerini etkiler. Medya geri dönüşleri ve eski önizleme geri dönüşleri hâlâ normal Matrix teslimatını kullanır.
- `GET /_matrix/client/v3/pushers` hiçbir pusher göstermiyorsa kullanıcı henüz bu hesap/cihaz için çalışan Matrix push teslimatına sahip değildir.

#### Synapse

Synapse için yukarıdaki kurulum genellikle tek başına yeterlidir:

- Sonlandırılmış OpenClaw önizleme bildirimleri için özel bir `homeserver.yaml` değişikliği gerekmez.
- Synapse dağıtımınız zaten normal Matrix push bildirimleri gönderiyorsa, yukarıdaki kullanıcı token'ı + `pushrules` çağrısı ana kurulum adımıdır.
- Synapse'i reverse proxy veya workers arkasında çalıştırıyorsanız `/_matrix/client/.../pushrules/` yolunun Synapse'e doğru şekilde ulaştığından emin olun.
- Synapse workers kullanıyorsanız pushers durumunun sağlıklı olduğundan emin olun. Push teslimatı ana süreç veya `synapse.app.pusher` / yapılandırılmış pusher worker'ları tarafından gerçekleştirilir.

#### Tuwunel

Tuwunel için yukarıda gösterilen aynı kurulum akışını ve push-rule API çağrısını kullanın:

- Sonlandırılmış önizleme işaretleyicisinin kendisi için Tuwunel'e özgü bir yapılandırma gerekmez.
- O kullanıcı için normal Matrix bildirimleri zaten çalışıyorsa, yukarıdaki kullanıcı token'ı + `pushrules` çağrısı ana kurulum adımıdır.
- Kullanıcı başka bir cihazda etkinken bildirimler kayboluyor gibi görünüyorsa `suppress_push_when_active` etkin mi kontrol edin. Tuwunel bu seçeneği 12 Eylül 2025'te Tuwunel 1.4.2 sürümünde ekledi ve bir cihaz etkinken diğer cihazlara gönderilen push'ları bilerek bastırabilir.

## Şifreleme ve doğrulama

Şifrelenmiş (E2EE) odalarda giden görüntü olayları `thumbnail_file` kullanır; böylece görüntü önizlemeleri tam ek ile birlikte şifrelenir. Şifrelenmemiş odalar yine düz `thumbnail_url` kullanır. Yapılandırma gerekmez — eklenti E2EE durumunu otomatik olarak algılar.

### Bottan bota odalar

Varsayılan olarak diğer yapılandırılmış OpenClaw Matrix hesaplarından gelen Matrix mesajları yok sayılır.

Ajanlar arası Matrix trafiğini bilinçli olarak istediğinizde `allowBots` kullanın:

```json5
{
  channels: {
    matrix: {
      allowBots: "mentions", // true | "mentions"
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

- `allowBots: true`, izin verilen odalarda ve DM'lerde diğer yapılandırılmış Matrix bot hesaplarından gelen mesajları kabul eder.
- `allowBots: "mentions"`, bu mesajları odalarda yalnızca bu bottan görünür şekilde bahsettiklerinde kabul eder. DM'lere yine izin verilir.
- `groups.<room>.allowBots`, bir oda için hesap düzeyi ayarı geçersiz kılar.
- OpenClaw, kendi kendine yanıt döngülerini önlemek için aynı Matrix kullanıcı kimliğinden gelen mesajları yine yok sayar.
- Matrix burada yerel bir bot bayrağı sunmaz; OpenClaw "bot tarafından yazılmış" ifadesini "bu OpenClaw gateway üzerinde yapılandırılmış başka bir Matrix hesabı tarafından gönderilmiş" olarak değerlendirir.

Paylaşılan odalarda bottan bota trafiği etkinleştirirken katı oda allowlist'leri ve mention gereksinimleri kullanın.

Şifrelemeyi etkinleştirin:

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      encryption: true,
      dm: { policy: "pairing" },
    },
  },
}
```

Doğrulama durumunu kontrol edin:

```bash
openclaw matrix verify status
```

Ayrıntılı durum (tam tanılama):

```bash
openclaw matrix verify status --verbose
```

Makine tarafından okunabilir çıktıda saklanan kurtarma anahtarını ekleyin:

```bash
openclaw matrix verify status --include-recovery-key --json
```

Çapraz imzalama ve doğrulama durumunu bootstrap edin:

```bash
openclaw matrix verify bootstrap
```

Çok hesap desteği: hesap başına kimlik bilgileri ve isteğe bağlı `name` ile `channels.matrix.accounts` kullanın. Paylaşılan desen için [Yapılandırma referansı](/tr/gateway/configuration-reference#multi-account-all-channels) bölümüne bakın.

Ayrıntılı bootstrap tanılaması:

```bash
openclaw matrix verify bootstrap --verbose
```

Bootstrap işleminden önce yeni bir çapraz imzalama kimliği sıfırlamasını zorlayın:

```bash
openclaw matrix verify bootstrap --force-reset-cross-signing
```

Bu cihazı bir kurtarma anahtarıyla doğrulayın:

```bash
openclaw matrix verify device "<your-recovery-key>"
```

Ayrıntılı cihaz doğrulama ayrıntıları:

```bash
openclaw matrix verify device "<your-recovery-key>" --verbose
```

Oda anahtarı yedekleme sağlığını kontrol edin:

```bash
openclaw matrix verify backup status
```

Ayrıntılı yedekleme sağlığı tanılaması:

```bash
openclaw matrix verify backup status --verbose
```

Oda anahtarlarını sunucu yedeğinden geri yükleyin:

```bash
openclaw matrix verify backup restore
```

Ayrıntılı geri yükleme tanılaması:

```bash
openclaw matrix verify backup restore --verbose
```

Geçerli sunucu yedeğini silin ve yeni bir yedekleme temeli oluşturun. Saklanan
yedekleme anahtarı düzgün biçimde yüklenemiyorsa bu sıfırlama, gelecekteki soğuk
başlatmaların yeni yedekleme anahtarını yükleyebilmesi için secret storage'ı da yeniden oluşturabilir:

```bash
openclaw matrix verify backup reset --yes
```

Tüm `verify` komutları varsayılan olarak kısa çıktı verir (sessiz dahili SDK günlükleri dahil) ve ayrıntılı tanılamayı yalnızca `--verbose` ile gösterir.
Betik kullanımında tam makine tarafından okunabilir çıktı için `--json` kullanın.

Çok hesaplı kurulumlarda Matrix CLI komutları, siz `--account <id>` vermediğiniz sürece örtük Matrix varsayılan hesabını kullanır.
Birden fazla adlandırılmış hesap yapılandırdıysanız önce `channels.matrix.defaultAccount` ayarlayın; aksi halde bu örtük CLI işlemleri durur ve sizden bir hesabı açıkça seçmenizi ister.
Doğrulama veya cihaz işlemlerinin açıkça adlandırılmış bir hesabı hedeflemesini istediğinizde `--account` kullanın:

```bash
openclaw matrix verify status --account assistant
openclaw matrix verify backup restore --account assistant
openclaw matrix devices list --account assistant
```

Şifreleme devre dışıysa veya adlandırılmış bir hesap için kullanılamıyorsa Matrix uyarıları ve doğrulama hataları o hesabın yapılandırma anahtarını işaret eder; örneğin `channels.matrix.accounts.assistant.encryption`.

### "Doğrulanmış" ne anlama gelir

OpenClaw bu Matrix cihazını yalnızca sizin kendi çapraz imzalama kimliğiniz tarafından doğrulandığında doğrulanmış kabul eder.
Pratikte `openclaw matrix verify status --verbose` üç güven sinyali gösterir:

- `Locally trusted`: bu cihaz yalnızca mevcut istemci tarafından güvenilir kabul edilir
- `Cross-signing verified`: SDK bu cihazın çapraz imzalama üzerinden doğrulandığını bildirir
- `Signed by owner`: cihaz sizin kendi self-signing anahtarınızla imzalanmıştır

`Verified by owner`, yalnızca çapraz imzalama doğrulaması veya sahip imzası mevcut olduğunda `yes` olur.
Yalnızca yerel güven, OpenClaw'ın bu cihazı tamamen doğrulanmış kabul etmesi için yeterli değildir.

### Bootstrap ne yapar

`openclaw matrix verify bootstrap`, şifreli Matrix hesapları için onarım ve kurulum komutudur.
Sırayla aşağıdakilerin tümünü yapar:

- mümkün olduğunda mevcut kurtarma anahtarını yeniden kullanarak secret storage'ı bootstrap eder
- çapraz imzalamayı bootstrap eder ve eksik genel çapraz imzalama anahtarlarını yükler
- mevcut cihazı işaretlemeyi ve çapraz imzalamayı dener
- zaten mevcut değilse yeni bir sunucu tarafı oda anahtarı yedeği oluşturur

Homeserver, çapraz imzalama anahtarlarını yüklemek için etkileşimli kimlik doğrulama gerektiriyorsa OpenClaw önce yüklemeyi kimlik doğrulamasız, sonra `m.login.dummy` ile, ardından `channels.matrix.password` yapılandırılmışsa `m.login.password` ile dener.

Geçerli çapraz imzalama kimliğini bilinçli olarak atmak ve yeni bir tane oluşturmak istiyorsanız yalnızca `--force-reset-cross-signing` kullanın.

Geçerli oda anahtarı yedeğini bilinçli olarak atmak ve gelecekteki mesajlar için yeni
bir yedekleme temeli başlatmak istiyorsanız `openclaw matrix verify backup reset --yes` kullanın.
Bunu yalnızca kurtarılamayan eski şifreli geçmişin erişilemez kalacağını ve OpenClaw'ın mevcut
yedekleme sırrı güvenli şekilde yüklenemiyorsa secret storage'ı yeniden oluşturabileceğini kabul ediyorsanız yapın.

### Yeni yedekleme temeli

Gelecekteki şifreli mesajların çalışmasını sürdürmek ve kurtarılamayan eski geçmişi kaybetmeyi kabul etmek istiyorsanız bu komutları sırayla çalıştırın:

```bash
openclaw matrix verify backup reset --yes
openclaw matrix verify backup status --verbose
openclaw matrix verify status
```

Adlandırılmış bir Matrix hesabını açıkça hedeflemek istediğinizde her komuta `--account <id>` ekleyin.

### Başlangıç davranışı

`encryption: true` olduğunda Matrix varsayılan olarak `startupVerification` değerini `"if-unverified"` yapar.
Başlangıçta bu cihaz hâlâ doğrulanmamışsa Matrix başka bir Matrix istemcisinde kendi kendini doğrulama isteğinde bulunur,
biri zaten beklemedeyken yinelenen istekleri atlar ve yeniden başlatmalardan sonra tekrar denemeden önce yerel bir cooldown uygular.
Başarısız istek denemeleri varsayılan olarak başarılı istek oluşturmalardan daha erken yeniden denenir.
Otomatik başlangıç isteklerini devre dışı bırakmak için `startupVerification: "off"` ayarlayın veya daha kısa ya da daha uzun bir yeniden deneme penceresi istiyorsanız `startupVerificationCooldownHours` değerini ayarlayın.

Başlangıç ayrıca otomatik olarak temkinli bir kripto bootstrap geçişi yapar.
Bu geçiş önce mevcut secret storage ve çapraz imzalama kimliğini yeniden kullanmayı dener ve siz açık bir bootstrap onarım akışı çalıştırmadığınız sürece çapraz imzalamayı sıfırlamaktan kaçınır.

Başlangıç bozuk bootstrap durumu bulursa ve `channels.matrix.password` yapılandırılmışsa OpenClaw daha katı bir onarım yolu deneyebilir.
Geçerli cihaz zaten sahip tarafından imzalanmışsa OpenClaw bu kimliği otomatik olarak sıfırlamak yerine korur.

Önceki herkese açık Matrix eklentisinden yükseltme:

- OpenClaw mümkün olduğunda aynı Matrix hesabını, access token'ı ve cihaz kimliğini otomatik olarak yeniden kullanır.
- Eyleme dönüştürülebilir Matrix geçiş değişiklikleri çalıştırılmadan önce OpenClaw `~/Backups/openclaw-migrations/` altında bir kurtarma anlık görüntüsü oluşturur veya yeniden kullanır.
- Birden fazla Matrix hesabı kullanıyorsanız, eski düz mağaza düzeninden yükseltmeden önce `channels.matrix.defaultAccount` ayarlayın; böylece OpenClaw bu paylaşılan eski durumun hangi hesaba aktarılacağını bilir.
- Önceki eklenti yerel olarak bir Matrix oda anahtarı yedeği çözme anahtarı depoladıysa başlangıç veya `openclaw doctor --fix` bunu yeni kurtarma anahtarı akışına otomatik olarak içe aktarır.
- Geçiş hazırlandıktan sonra Matrix access token değiştiyse başlangıç artık otomatik yedek geri yüklemeden vazgeçmeden önce bekleyen eski geri yükleme durumu için komşu token-hash depolama köklerini tarar.
- Matrix access token daha sonra aynı hesap, homeserver ve kullanıcı için değişirse OpenClaw artık boş bir Matrix durum dizininden başlamak yerine mevcut en tam token-hash depolama kökünü yeniden kullanmayı tercih eder.
- Sonraki gateway başlangıcında yedeklenen oda anahtarları otomatik olarak yeni kripto deposuna geri yüklenir.
- Eski eklentide hiç yedeklenmemiş yalnızca yerel oda anahtarları varsa OpenClaw açık bir uyarı verir. Bu anahtarlar önceki rust kripto deposundan otomatik olarak dışa aktarılamaz; bu nedenle bazı eski şifreli geçmişler manuel olarak kurtarılana kadar erişilemez kalabilir.
- Tam yükseltme akışı, sınırlamalar, kurtarma komutları ve yaygın geçiş mesajları için [Matrix geçişi](/tr/install/migrating-matrix) bölümüne bakın.

Şifreli çalışma zamanı durumu, şu dizin altında hesap başına, kullanıcı başına token-hash kökleri halinde düzenlenir:
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/`.
Bu dizin sync store (`bot-storage.json`), crypto store (`crypto/`),
recovery key dosyası (`recovery-key.json`), IndexedDB anlık görüntüsü (`crypto-idb-snapshot.json`),
thread bindings (`thread-bindings.json`) ve başlangıç doğrulama durumu (`startup-verification.json`)
özellikler kullanıldığında bunları içerir.
Token değişse ancak hesap kimliği aynı kalsa bile OpenClaw, bu hesap/homeserver/kullanıcı üçlüsü için mevcut en iyi
kökü yeniden kullanır; böylece önceki sync durumu, kripto durumu, ileti dizisi bağları
ve başlangıç doğrulama durumu görünür kalır.

### Node crypto store modeli

Bu eklentide Matrix E2EE, Node üzerinde resmi `matrix-js-sdk` Rust kripto yolunu kullanır.
Bu yol, kripto durumunun yeniden başlatmalardan sonra korunmasını istiyorsanız IndexedDB destekli kalıcılık bekler.

OpenClaw bunu şu anda Node üzerinde şu şekilde sağlar:

- SDK'nın beklediği IndexedDB API shim'i olarak `fake-indexeddb` kullanarak
- `initRustCrypto` öncesinde Rust crypto IndexedDB içeriğini `crypto-idb-snapshot.json` dosyasından geri yükleyerek
- init işleminden sonra ve çalışma zamanı sırasında güncellenmiş IndexedDB içeriğini tekrar `crypto-idb-snapshot.json` dosyasına yazarak
- gateway çalışma zamanı kalıcılığı ile CLI bakımının aynı anlık görüntü dosyası üzerinde yarışmaması için anlık görüntü geri yükleme ve kalıcılık işlemlerini `crypto-idb-snapshot.json` üzerinde tavsiye niteliğinde bir dosya kilidiyle seri hale getirerek

Bu, özel bir kripto uygulaması değil, uyumluluk/depolama tesisatıdır.
Anlık görüntü dosyası hassas çalışma zamanı durumudur ve kısıtlayıcı dosya izinleriyle saklanır.
OpenClaw'ın güvenlik modelinde gateway host ve yerel OpenClaw durum dizini zaten güvenilen operatör sınırı içinde olduğundan, bu esas olarak ayrı bir uzak güven sınırından ziyade operasyonel dayanıklılık meselesidir.

Planlanan iyileştirme:

- kalıcı Matrix anahtar malzemesi için SecretRef desteği eklemek; böylece kurtarma anahtarları ve ilgili store şifreleme sırları yalnızca yerel dosyalardan değil, OpenClaw sır sağlayıcılarından da alınabilir

## Profil yönetimi

Seçilen hesap için Matrix öz profilini güncellemek için şunu kullanın:

```bash
openclaw matrix profile set --name "OpenClaw Assistant"
openclaw matrix profile set --avatar-url https://cdn.example.org/avatar.png
```

Açıkça adlandırılmış bir Matrix hesabını hedeflemek istediğinizde `--account <id>` ekleyin.

Matrix, `mxc://` avatar URL'lerini doğrudan kabul eder. `http://` veya `https://` avatar URL'si verdiğinizde OpenClaw önce bunu Matrix'e yükler ve çözümlenen `mxc://` URL'sini tekrar `channels.matrix.avatarUrl` içine (veya seçili hesap geçersiz kılmasına) kaydeder.

## Otomatik doğrulama bildirimleri

Matrix artık doğrulama yaşam döngüsü bildirimlerini sıkı DM doğrulama odasına doğrudan `m.notice` mesajları olarak gönderir.
Buna şunlar dahildir:

- doğrulama isteği bildirimleri
- doğrulama hazır bildirimleri (açık "emoji ile doğrulayın" yönlendirmesiyle)
- doğrulama başlangıç ve tamamlanma bildirimleri
- mevcut olduğunda SAS ayrıntıları (emoji ve ondalık)

Başka bir Matrix istemcisinden gelen doğrulama istekleri OpenClaw tarafından izlenir ve otomatik kabul edilir.
Kendi kendini doğrulama akışlarında OpenClaw ayrıca emoji doğrulaması kullanılabilir olduğunda SAS akışını otomatik başlatır ve kendi tarafını onaylar.
Başka bir Matrix kullanıcı/cihazından gelen doğrulama istekleri için OpenClaw isteği otomatik kabul eder ve ardından SAS akışının normal şekilde ilerlemesini bekler.
Doğrulamayı tamamlamak için Matrix istemcinizde yine de emoji veya ondalık SAS değerini karşılaştırmanız ve orada "They match" seçeneğini onaylamanız gerekir.

OpenClaw kendi başlattığı yinelenen akışları körü körüne otomatik kabul etmez. Kendi kendini doğrulama isteği zaten beklemedeyse başlangıç yeni bir istek oluşturmaz.

Doğrulama protokolü/sistem bildirimleri ajan sohbet hattına iletilmez; bu nedenle `NO_REPLY` üretmezler.

### Cihaz hijyeni

Eski OpenClaw tarafından yönetilen Matrix cihazları hesapta birikebilir ve şifreli oda güvenini anlamayı zorlaştırabilir.
Bunları şu komutla listeleyin:

```bash
openclaw matrix devices list
```

Eski OpenClaw tarafından yönetilen cihazları şu komutla kaldırın:

```bash
openclaw matrix devices prune-stale
```

### Doğrudan Oda Onarımı

Doğrudan mesaj durumu senkron dışına çıkarsa OpenClaw, eski tekli odalara işaret eden bayat `m.direct` eşlemeleriyle kalabilir. Bir eş için mevcut eşlemeyi incelemek için şunu kullanın:

```bash
openclaw matrix direct inspect --user-id @alice:example.org
```

Onarmak için:

```bash
openclaw matrix direct repair --user-id @alice:example.org
```

Onarım, Matrix'e özgü mantığı eklenti içinde tutar:

- zaten `m.direct` içinde eşlenmiş olan katı 1:1 DM'yi tercih eder
- aksi halde bu kullanıcıyla şu anda katılınmış herhangi bir katı 1:1 DM'ye geri döner
- sağlıklı bir DM yoksa yeni bir doğrudan oda oluşturur ve `m.direct` değerini ona işaret edecek şekilde yeniden yazar

Onarım akışı eski odaları otomatik olarak silmez. Yalnızca sağlıklı DM'yi seçer ve eşlemeyi günceller; böylece yeni Matrix gönderimleri, doğrulama bildirimleri ve diğer doğrudan mesaj akışları yeniden doğru odayı hedefler.

## İleti dizileri

Matrix, hem otomatik yanıtlar hem de message-tool gönderimleri için yerel Matrix ileti dizilerini destekler.

- `dm.sessionScope: "per-user"` (varsayılan) Matrix DM yönlendirmesini gönderen kapsamlı tutar; böylece birden fazla DM odası aynı eşe çözülüyorsa tek bir oturumu paylaşabilir.
- `dm.sessionScope: "per-room"`, her Matrix DM odasını kendi oturum anahtarına ayırırken yine normal DM kimlik doğrulama ve allowlist kontrollerini kullanır.
- Açık Matrix konuşma bağları yine de `dm.sessionScope` ayarını geçersiz kılar; dolayısıyla bağlanmış odalar ve ileti dizileri seçtikleri hedef oturumu korur.
- `threadReplies: "off"`, yanıtları üst düzeyde tutar ve gelen ileti dizili mesajları ana oturumda tutar.
- `threadReplies: "inbound"`, yalnızca gelen mesaj zaten o ileti dizisindeyse ileti dizisi içinde yanıt verir.
- `threadReplies: "always"`, oda yanıtlarını tetikleyici mesaja köklenen bir ileti dizisinde tutar ve bu konuşmayı ilk tetikleyici mesajdan itibaren eşleşen ileti dizisi kapsamlı oturum üzerinden yönlendirir.
- `dm.threadReplies`, yalnızca DM'ler için üst düzey ayarı geçersiz kılar. Örneğin, odalardaki ileti dizilerini izole tutarken DM'leri düz tutabilirsiniz.
- Gelen ileti dizili mesajlar, ek ajan bağlamı olarak ileti dizisi kök mesajını içerir.
- Message-tool gönderimleri artık hedef aynı oda veya aynı DM kullanıcı hedefi olduğunda, açık bir `threadId` verilmedikçe mevcut Matrix ileti dizisini otomatik devralır.
- Aynı oturumlu DM kullanıcı hedefi yeniden kullanımı yalnızca mevcut oturum meta verisi aynı Matrix hesabındaki aynı DM eşini kanıtladığında devreye girer; aksi halde OpenClaw normal kullanıcı kapsamlı yönlendirmeye geri döner.
- OpenClaw, bir Matrix DM odasının aynı paylaşılan Matrix DM oturumunda başka bir DM odası ile çakıştığını gördüğünde, thread bindings etkinse ve `dm.sessionScope` ipucu varsa, bu odada `/focus` kaçış yolunu içeren tek seferlik bir `m.notice` gönderir.
- Matrix için çalışma zamanı thread bindings desteklenir. `/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age` ve ileti dizisine bağlı `/acp spawn` artık Matrix odalarında ve DM'lerde çalışır.
- Üst düzey Matrix oda/DM `/focus`, `threadBindings.spawnSubagentSessions=true` olduğunda yeni bir Matrix ileti dizisi oluşturur ve onu hedef oturuma bağlar.
- Mevcut bir Matrix ileti dizisi içinde `/focus` veya `/acp spawn --thread here` çalıştırmak bunun yerine mevcut ileti dizisini bağlar.

## ACP konuşma bağları

Matrix odaları, DM'ler ve mevcut Matrix ileti dizileri, sohbet yüzeyini değiştirmeden kalıcı ACP çalışma alanlarına dönüştürülebilir.

Hızlı operatör akışı:

- Kullanmayı sürdürmek istediğiniz Matrix DM, oda veya mevcut ileti dizisi içinde `/acp spawn codex --bind here` çalıştırın.
- Üst düzey bir Matrix DM veya odasında mevcut DM/oda sohbet yüzeyi olarak kalır ve gelecekteki mesajlar oluşturulan ACP oturumuna yönlendirilir.
- Mevcut bir Matrix ileti dizisi içinde `--bind here`, mevcut ileti dizisini yerinde bağlar.
- `/new` ve `/reset`, aynı bağlı ACP oturumunu yerinde sıfırlar.
- `/acp close`, ACP oturumunu kapatır ve bağı kaldırır.

Notlar:

- `--bind here`, alt Matrix ileti dizisi oluşturmaz.
- `threadBindings.spawnAcpSessions`, yalnızca OpenClaw'ın alt Matrix ileti dizisi oluşturması veya bağlaması gereken `/acp spawn --thread auto|here` için gereklidir.

### Thread Binding Yapılandırması

Matrix, genel varsayılanları `session.threadBindings` üzerinden devralır ve ayrıca kanal başına geçersiz kılmaları destekler:

- `threadBindings.enabled`
- `threadBindings.idleHours`
- `threadBindings.maxAgeHours`
- `threadBindings.spawnSubagentSessions`
- `threadBindings.spawnAcpSessions`

Matrix ileti dizisine bağlı spawn bayrakları isteğe bağlıdır:

- Üst düzey `/focus` komutunun yeni Matrix ileti dizileri oluşturup bağlamasına izin vermek için `threadBindings.spawnSubagentSessions: true` ayarlayın.
- `/acp spawn --thread auto|here` komutunun ACP oturumlarını Matrix ileti dizilerine bağlamasına izin vermek için `threadBindings.spawnAcpSessions: true` ayarlayın.

## Tepkiler

Matrix, giden tepki eylemlerini, gelen tepki bildirimlerini ve gelen ack tepkilerini destekler.

- Giden tepki araçları `channels["matrix"].actions.reactions` tarafından denetlenir.
- `react`, belirli bir Matrix olayına tepki ekler.
- `reactions`, belirli bir Matrix olayı için mevcut tepki özetini listeler.
- `emoji=""`, bot hesabının o olay üzerindeki kendi tepkilerini kaldırır.
- `remove: true`, bot hesabından yalnızca belirtilen emoji tepkisini kaldırır.

Ack tepkileri standart OpenClaw çözümleme sırasını kullanır:

- `channels["matrix"].accounts.<accountId>.ackReaction`
- `channels["matrix"].ackReaction`
- `messages.ackReaction`
- ajan kimliği emoji geri dönüşü

Ack tepki kapsamı şu sırayla çözülür:

- `channels["matrix"].accounts.<accountId>.ackReactionScope`
- `channels["matrix"].ackReactionScope`
- `messages.ackReactionScope`

Tepki bildirim modu şu sırayla çözülür:

- `channels["matrix"].accounts.<accountId>.reactionNotifications`
- `channels["matrix"].reactionNotifications`
- varsayılan: `own`

Mevcut davranış:

- `reactionNotifications: "own"`, bot tarafından yazılmış Matrix mesajlarını hedeflediklerinde eklenen `m.reaction` olaylarını iletir.
- `reactionNotifications: "off"`, tepki sistem olaylarını devre dışı bırakır.
- Tepki kaldırmaları hâlâ sistem olaylarına dönüştürülmez çünkü Matrix bunları bağımsız `m.reaction` kaldırmaları olarak değil, redaksiyonlar olarak gösterir.

## Geçmiş bağlamı

- `channels.matrix.historyLimit`, bir Matrix oda mesajı ajanı tetiklediğinde kaç son oda mesajının `InboundHistory` olarak dahil edileceğini kontrol eder.
- Bu değer `messages.groupChat.historyLimit` değerine geri döner. İkisi de ayarlı değilse etkin varsayılan `0` olur; dolayısıyla mention ile denetlenen oda mesajları arabelleğe alınmaz. Devre dışı bırakmak için `0` ayarlayın.
- Matrix oda geçmişi yalnızca odaya özeldir. DM'ler normal oturum geçmişini kullanmaya devam eder.
- Matrix oda geçmişi yalnızca beklemedeki mesajlar içindir: OpenClaw henüz yanıt tetiklememiş oda mesajlarını arabelleğe alır, ardından bir mention veya başka bir tetikleyici geldiğinde bu pencerenin anlık görüntüsünü alır.
- Geçerli tetikleyici mesaj `InboundHistory` içine dahil edilmez; o dönüş için ana gelen gövde içinde kalır.
- Aynı Matrix olayının yeniden denemeleri, daha yeni oda mesajlarına kaymak yerine özgün geçmiş anlık görüntüsünü yeniden kullanır.

## Bağlam görünürlüğü

Matrix, alınan yanıt metni, ileti dizisi kökleri ve bekleyen geçmiş gibi ek oda bağlamı için paylaşılan `contextVisibility` denetimini destekler.

- `contextVisibility: "all"` varsayılandır. Ek bağlam alındığı gibi tutulur.
- `contextVisibility: "allowlist"`, ek bağlamı etkin oda/kullanıcı allowlist kontrolleri tarafından izin verilen gönderenlere filtreler.
- `contextVisibility: "allowlist_quote"`, `allowlist` gibi davranır, ancak yine de açık bir alıntılanmış yanıtı tutar.

Bu ayar, ek bağlam görünürlüğünü etkiler; gelen mesajın kendisinin yanıt tetikleyip tetikleyemeyeceğini etkilemez.
Tetikleme yetkilendirmesi yine `groupPolicy`, `groups`, `groupAllowFrom` ve DM politika ayarlarından gelir.

## DM ve oda politikası örneği

```json5
{
  channels: {
    matrix: {
      dm: {
        policy: "allowlist",
        allowFrom: ["@admin:example.org"],
        threadReplies: "off",
      },
      groupPolicy: "allowlist",
      groupAllowFrom: ["@admin:example.org"],
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

Mention denetimi ve allowlist davranışı için [Gruplar](/tr/channels/groups) bölümüne bakın.

Matrix DM'leri için eşleştirme örneği:

```bash
openclaw pairing list matrix
openclaw pairing approve matrix <CODE>
```

Onaylanmamış bir Matrix kullanıcısı onaydan önce size mesaj göndermeye devam ederse OpenClaw aynı bekleyen eşleştirme kodunu yeniden kullanır ve yeni bir kod üretmek yerine kısa bir cooldown sonrasında yeniden bir hatırlatma yanıtı gönderebilir.

Paylaşılan DM eşleştirme akışı ve depolama düzeni için [Eşleştirme](/tr/channels/pairing) bölümüne bakın.

## Yürütme onayları

Matrix, bir Matrix hesabı için yerel bir onay istemcisi olarak çalışabilir. Yerel
DM/kanal yönlendirme düğmeleri yine yürütme onay yapılandırması altında bulunur:

- `channels.matrix.execApprovals.enabled`
- `channels.matrix.execApprovals.approvers` (isteğe bağlı; `channels.matrix.dm.allowFrom` değerine geri döner)
- `channels.matrix.execApprovals.target` (`dm` | `channel` | `both`, varsayılan: `dm`)
- `channels.matrix.execApprovals.agentFilter`
- `channels.matrix.execApprovals.sessionFilter`

Onaylayıcılar `@owner:example.org` gibi Matrix kullanıcı kimlikleri olmalıdır. `enabled` ayarsız veya `"auto"` olduğunda ve en az bir onaylayıcı çözümlenebildiğinde Matrix yerel onayları otomatik etkinleştirir. Yürütme onayları önce `execApprovals.approvers` kullanır ve `channels.matrix.dm.allowFrom` değerine geri dönebilir. Eklenti onayları `channels.matrix.dm.allowFrom` üzerinden yetkilendirilir. Matrix'i açıkça yerel bir onay istemcisi olarak devre dışı bırakmak için `enabled: false` ayarlayın. Aksi halde onay istekleri diğer yapılandırılmış onay yollarına veya onay geri dönüş politikasına geri döner.

Matrix yerel yönlendirme artık her iki onay türünü de destekler:

- `channels.matrix.execApprovals.*`, Matrix onay istemleri için yerel DM/kanal fanout modunu kontrol eder.
- Yürütme onayları `execApprovals.approvers` veya `channels.matrix.dm.allowFrom` içinden yürütme onaylayıcı kümesini kullanır.
- Eklenti onayları Matrix DM allowlist'ini `channels.matrix.dm.allowFrom` içinden kullanır.
- Matrix tepki kısayolları ve mesaj güncellemeleri hem yürütme hem de eklenti onaylarına uygulanır.

Teslimat kuralları:

- `target: "dm"` onay istemlerini onaylayıcı DM'lerine gönderir
- `target: "channel"` istemi kaynağın geldiği Matrix oda veya DM'ye geri gönderir
- `target: "both"` istemleri onaylayıcı DM'lerine ve kaynağın geldiği Matrix oda veya DM'ye gönderir

Matrix onay istemleri birincil onay mesajında tepki kısayollarını başlatır:

- `✅` = bir kez izin ver
- `❌` = reddet
- `♾️` = bu karar etkin yürütme politikası tarafından izin verildiğinde her zaman izin ver

Onaylayıcılar bu mesaja tepki verebilir veya geri dönüş slash komutlarını kullanabilir: `/approve <id> allow-once`, `/approve <id> allow-always` veya `/approve <id> deny`.

Yalnızca çözümlenmiş onaylayıcılar onaylayabilir veya reddedebilir. Yürütme onaylarında kanal teslimatı komut metnini içerdiğinden, `channel` veya `both` seçeneklerini yalnızca güvenilen odalarda etkinleştirin.

Matrix onay istemleri paylaşılan çekirdek onay planlayıcısını yeniden kullanır. Matrix'e özgü yerel yüzey, hem yürütme hem de eklenti onayları için oda/DM yönlendirmesini, tepkileri ve mesaj gönderme/güncelleme/silme davranışını işler.

Hesap başına geçersiz kılma:

- `channels.matrix.accounts.<account>.execApprovals`

İlgili belgeler: [Yürütme onayları](/tr/tools/exec-approvals)

## Çok hesap örneği

```json5
{
  channels: {
    matrix: {
      enabled: true,
      defaultAccount: "assistant",
      dm: { policy: "pairing" },
      accounts: {
        assistant: {
          homeserver: "https://matrix.example.org",
          accessToken: "syt_assistant_xxx",
          encryption: true,
        },
        alerts: {
          homeserver: "https://matrix.example.org",
          accessToken: "syt_alerts_xxx",
          dm: {
            policy: "allowlist",
            allowFrom: ["@ops:example.org"],
            threadReplies: "off",
          },
        },
      },
    },
  },
}
```

Üst düzey `channels.matrix` değerleri, bir hesap bunları geçersiz kılmadıkça adlandırılmış hesaplar için varsayılan görevi görür.
Devralınan oda girdilerini çok hesaplı kurulumlarda `groups.<room>.account` (veya eski `rooms.<room>.account`) ile tek bir Matrix hesabına kapsamlayabilirsiniz.
`account` içermeyen girdiler tüm Matrix hesapları arasında paylaşılmış kalır ve `account: "default"` içeren girdiler de varsayılan hesap doğrudan üst düzey `channels.matrix.*` üzerinde yapılandırıldığında çalışmaya devam eder.
Kısmi paylaşılan kimlik doğrulama varsayılanları kendi başına ayrı örtük bir varsayılan hesap oluşturmaz. OpenClaw, yalnızca bu varsayılanın yeni kimlik doğrulaması olduğunda (`homeserver` artı `accessToken` veya `homeserver` artı `userId` ve `password`) üst düzey `default` hesabını sentezler; adlandırılmış hesaplar daha sonra önbelleğe alınmış kimlik bilgilerinin kimlik doğrulamayı karşılaması durumunda `homeserver` artı `userId` ile yine keşfedilebilir kalabilir.
Matrix'te zaten tam olarak bir adlandırılmış hesap varsa veya `defaultAccount` mevcut bir adlandırılmış hesap anahtarını işaret ediyorsa, tek hesaplıdan çok hesaplıya onarım/kurulum yükseltmesi yeni bir `accounts.default` girdisi oluşturmak yerine bu hesabı korur. Yalnızca Matrix kimlik doğrulama/bootstrap anahtarları bu yükseltilmiş hesaba taşınır; paylaşılan teslimat politikası anahtarları üst düzeyde kalır.
Örtük yönlendirme, probe ve CLI işlemleri için OpenClaw'ın bir adlandırılmış Matrix hesabını tercih etmesini istiyorsanız `defaultAccount` ayarlayın.
Birden fazla adlandırılmış hesap yapılandırdıysanız `defaultAccount` ayarlayın veya örtük hesap seçimine dayanan CLI komutları için `--account <id>` geçin.
Bir komutta bu örtük seçimi geçersiz kılmak istediğinizde `openclaw matrix verify ...` ve `openclaw matrix devices ...` komutlarına `--account <id>` geçin.

## Özel/LAN homeserver'lar

Varsayılan olarak OpenClaw, SSRF koruması için özel/iç Matrix homeserver'larını
siz hesap başına açıkça izin vermedikçe engeller.

Homeserver'ınız localhost üzerinde, bir LAN/Tailscale IP'sinde veya iç bir hostname üzerinde çalışıyorsa,
bu Matrix hesabı için `network.dangerouslyAllowPrivateNetwork` değerini etkinleştirin:

```json5
{
  channels: {
    matrix: {
      homeserver: "http://matrix-synapse:8008",
      network: {
        dangerouslyAllowPrivateNetwork: true,
      },
      accessToken: "syt_internal_xxx",
    },
  },
}
```

CLI kurulum örneği:

```bash
openclaw matrix account add \
  --account ops \
  --homeserver http://matrix-synapse:8008 \
  --allow-private-network \
  --access-token syt_ops_xxx
```

Bu katılım yalnızca güvenilen özel/iç hedeflere izin verir. `http://matrix.example.org:8008` gibi
herkese açık düz metin homeserver'lar yine engellenir. Mümkün olduğunda `https://` tercih edin.

## Matrix trafiğini proxy üzerinden geçirmek

Matrix dağıtımınız açık bir giden HTTP(S) proxy gerektiriyorsa `channels.matrix.proxy` ayarlayın:

```json5
{
  channels: {
    matrix: {
      homeserver: "https://matrix.example.org",
      accessToken: "syt_bot_xxx",
      proxy: "http://127.0.0.1:7890",
    },
  },
}
```

Adlandırılmış hesaplar üst düzey varsayılanı `channels.matrix.accounts.<id>.proxy` ile geçersiz kılabilir.
OpenClaw aynı proxy ayarını çalışma zamanı Matrix trafiği ve hesap durumu probe'ları için kullanır.

## Hedef çözümleme

Matrix, OpenClaw'ın sizden oda veya kullanıcı hedefi istediği her yerde şu hedef biçimlerini kabul eder:

- Kullanıcılar: `@user:server`, `user:@user:server` veya `matrix:user:@user:server`
- Odalar: `!room:server`, `room:!room:server` veya `matrix:room:!room:server`
- Takma adlar: `#alias:server`, `channel:#alias:server` veya `matrix:channel:#alias:server`

Canlı dizin araması, oturum açmış Matrix hesabını kullanır:

- Kullanıcı aramaları, o homeserver üzerindeki Matrix kullanıcı dizinini sorgular.
- Oda aramaları açık oda kimliklerini ve takma adları doğrudan kabul eder, ardından o hesap için katılınmış oda adlarını aramaya geri döner.
- Katılınmış oda adı araması en iyi çaba esasına göre çalışır. Bir oda adı bir kimliğe veya takma ada çözümlenemiyorsa çalışma zamanındaki allowlist çözümlemesi tarafından yok sayılır.

## Yapılandırma referansı

- `enabled`: kanalı etkinleştir veya devre dışı bırak.
- `name`: hesap için isteğe bağlı etiket.
- `defaultAccount`: birden fazla Matrix hesabı yapılandırıldığında tercih edilen hesap kimliği.
- `homeserver`: homeserver URL'si, örneğin `https://matrix.example.org`.
- `network.dangerouslyAllowPrivateNetwork`: bu Matrix hesabının özel/iç homeserver'lara bağlanmasına izin ver. Homeserver `localhost`, bir LAN/Tailscale IP'si veya `matrix-synapse` gibi bir iç host adına çözülüyorsa bunu etkinleştirin.
- `proxy`: Matrix trafiği için isteğe bağlı HTTP(S) proxy URL'si. Adlandırılmış hesaplar üst düzey varsayılanı kendi `proxy` değerleriyle geçersiz kılabilir.
- `userId`: tam Matrix kullanıcı kimliği, örneğin `@bot:example.org`.
- `accessToken`: token tabanlı kimlik doğrulama için access token. Düz metin değerler ve SecretRef değerleri, env/file/exec sağlayıcıları genelinde `channels.matrix.accessToken` ve `channels.matrix.accounts.<id>.accessToken` için desteklenir. Bkz. [Sır Yönetimi](/tr/gateway/secrets).
- `password`: parola tabanlı giriş için parola. Düz metin değerler ve SecretRef değerleri desteklenir.
- `deviceId`: açık Matrix cihaz kimliği.
- `deviceName`: parola girişi için cihaz görünen adı.
- `avatarUrl`: profil senkronizasyonu ve `set-profile` güncellemeleri için saklanan öz avatar URL'si.
- `initialSyncLimit`: başlangıç sync olay sınırı.
- `encryption`: E2EE'yi etkinleştir.
- `allowlistOnly`: DM'ler ve odalar için yalnızca allowlist davranışını zorla.
- `allowBots`: diğer yapılandırılmış OpenClaw Matrix hesaplarından gelen mesajlara izin ver (`true` veya `"mentions"`).
- `groupPolicy`: `open`, `allowlist` veya `disabled`.
- `contextVisibility`: ek oda bağlamı görünürlük modu (`all`, `allowlist`, `allowlist_quote`).
- `groupAllowFrom`: oda trafiği için kullanıcı kimlikleri allowlist'i.
- `groupAllowFrom` girdileri tam Matrix kullanıcı kimlikleri olmalıdır. Çözümlenmeyen adlar çalışma zamanında yok sayılır.
- `historyLimit`: grup geçmiş bağlamı olarak dahil edilecek en fazla oda mesajı sayısı. `messages.groupChat.historyLimit` değerine geri döner; ikisi de ayarlı değilse etkin varsayılan `0` olur. Devre dışı bırakmak için `0` ayarlayın.
- `replyToMode`: `off`, `first`, `all` veya `batched`.
- `markdown`: giden Matrix metni için isteğe bağlı Markdown işleme yapılandırması.
- `streaming`: `off` (varsayılan), `partial`, `quiet`, `true` veya `false`. `partial` ve `true`, normal Matrix metin mesajlarıyla önizleme-önce taslak güncellemelerini etkinleştirir. `quiet`, self-hosted push-rule kurulumları için bildirim üretmeyen önizleme bildirimlerini kullanır.
- `blockStreaming`: `true`, taslak önizleme akışı etkinken tamamlanan asistan blokları için ayrı ilerleme mesajlarını etkinleştirir.
- `threadReplies`: `off`, `inbound` veya `always`.
- `threadBindings`: ileti dizisine bağlı oturum yönlendirmesi ve yaşam döngüsü için kanal başına geçersiz kılmalar.
- `startupVerification`: başlangıçta otomatik kendi kendini doğrulama isteği modu (`if-unverified`, `off`).
- `startupVerificationCooldownHours`: otomatik başlangıç doğrulama isteklerini yeniden denemeden önce cooldown süresi.
- `textChunkLimit`: giden mesaj parça boyutu.
- `chunkMode`: `length` veya `newline`.
- `responsePrefix`: giden yanıtlar için isteğe bağlı mesaj öneki.
- `ackReaction`: bu kanal/hesap için isteğe bağlı ack tepki geçersiz kılması.
- `ackReactionScope`: isteğe bağlı ack tepki kapsamı geçersiz kılması (`group-mentions`, `group-all`, `direct`, `all`, `none`, `off`).
- `reactionNotifications`: gelen tepki bildirim modu (`own`, `off`).
- `mediaMaxMb`: Matrix medya işleme için MB cinsinden medya boyut üst sınırı. Giden gönderimlere ve gelen medya işlemeye uygulanır.
- `autoJoin`: davet otomatik katılım politikası (`always`, `allowlist`, `off`). Varsayılan: `off`. Bu yalnızca oda/grup davetleri için değil, DM tarzı davetler dahil genel Matrix davetleri için geçerlidir. OpenClaw bu kararı davet anında, katıldığı odanın DM mi grup mu olduğunu güvenilir şekilde sınıflandıramadan önce verir.
- `autoJoinAllowlist`: `autoJoin` değeri `allowlist` olduğunda izin verilen odalar/takma adlar. Takma ad girdileri davet işleme sırasında oda kimliklerine çözülür; OpenClaw davet edilen odanın iddia ettiği takma ad durumuna güvenmez.
- `dm`: DM politika bloğu (`enabled`, `policy`, `allowFrom`, `sessionScope`, `threadReplies`).
- `dm.policy`: OpenClaw odaya katılıp onu DM olarak sınıflandırdıktan sonra DM erişimini kontrol eder. Davetin otomatik katılıp katılmayacağını değiştirmez.
- `dm.allowFrom` girdileri, siz bunları zaten canlı dizin aramasıyla çözümlemediyseniz tam Matrix kullanıcı kimlikleri olmalıdır.
- `dm.sessionScope`: `per-user` (varsayılan) veya `per-room`. Eş aynı olsa bile her Matrix DM odasının ayrı bağlam tutmasını istiyorsanız `per-room` kullanın.
- `dm.threadReplies`: yalnızca DM için ileti dizisi politikası geçersiz kılması (`off`, `inbound`, `always`). DM'lerde hem yanıt yerleştirmesi hem de oturum izolasyonu için üst düzey `threadReplies` ayarını geçersiz kılar.
- `execApprovals`: Matrix-yerel yürütme onayı teslimatı (`enabled`, `approvers`, `target`, `agentFilter`, `sessionFilter`).
- `execApprovals.approvers`: yürütme isteklerini onaylamasına izin verilen Matrix kullanıcı kimlikleri. `dm.allowFrom` zaten onaylayıcıları tanımlıyorsa isteğe bağlıdır.
- `execApprovals.target`: `dm | channel | both` (varsayılan: `dm`).
- `accounts`: hesap başına adlandırılmış geçersiz kılmalar. Üst düzey `channels.matrix` değerleri bu girdiler için varsayılan görevi görür.
- `groups`: oda başına politika eşlemesi. Oda kimliklerini veya takma adları tercih edin; çözümlenmeyen oda adları çalışma zamanında yok sayılır. Oturum/grup kimliği çözümlemeden sonra kararlı oda kimliğini kullanırken insanlar tarafından okunabilir etiketler yine oda adlarından gelir.
- `groups.<room>.account`: çok hesaplı kurulumlarda devralınmış tek bir oda girdisini belirli bir Matrix hesabıyla sınırla.
- `groups.<room>.allowBots`: yapılandırılmış bot gönderenleri için oda düzeyinde geçersiz kılma (`true` veya `"mentions"`).
- `groups.<room>.users`: oda başına gönderen allowlist'i.
- `groups.<room>.tools`: oda başına araç izin/verme veya engelleme geçersiz kılmaları.
- `groups.<room>.autoReply`: oda düzeyinde mention denetimi geçersiz kılması. `true`, bu oda için mention gereksinimlerini devre dışı bırakır; `false` bunları yeniden zorla etkinleştirir.
- `groups.<room>.skills`: isteğe bağlı oda düzeyinde Skills filtresi.
- `groups.<room>.systemPrompt`: isteğe bağlı oda düzeyinde system prompt parçacığı.
- `rooms`: `groups` için eski takma ad.
- `actions`: eylem başına araç denetimi (`messages`, `reactions`, `pins`, `profile`, `memberInfo`, `channelInfo`, `verification`).

## İlgili

- [Kanallara Genel Bakış](/tr/channels) — desteklenen tüm kanallar
- [Eşleştirme](/tr/channels/pairing) — DM kimlik doğrulaması ve eşleştirme akışı
- [Gruplar](/tr/channels/groups) — grup sohbeti davranışı ve mention denetimi
- [Kanal Yönlendirme](/tr/channels/channel-routing) — mesajlar için oturum yönlendirmesi
- [Güvenlik](/tr/gateway/security) — erişim modeli ve sağlamlaştırma
