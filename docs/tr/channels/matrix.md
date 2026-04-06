---
read_when:
    - OpenClaw içinde Matrix kurulumu
    - Matrix E2EE ve doğrulamayı yapılandırma
summary: Matrix destek durumu, kurulum ve yapılandırma örnekleri
title: Matrix
x-i18n:
    generated_at: "2026-04-06T03:08:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3e2d84c08d7d5b96db14b914e54f08d25334401cdd92eb890bc8dfb37b0ca2dc
    source_path: channels/matrix.md
    workflow: 15
---

# Matrix

Matrix, OpenClaw için paketlenmiş Matrix kanal eklentisidir.
Resmi `matrix-js-sdk` kullanır ve DM'leri, odaları, ileti dizilerini, medyayı, tepkileri, anketleri, konumu ve E2EE'yi destekler.

## Paketlenmiş eklenti

Matrix, mevcut OpenClaw sürümlerinde paketlenmiş bir eklenti olarak gelir; bu nedenle normal
paketlenmiş derlemelerde ayrı bir kurulum gerekmez.

Eski bir derlemeyi veya Matrix'i hariç tutan özel bir kurulumu kullanıyorsanız, onu
elle yükleyin:

npm'den yükleyin:

```bash
openclaw plugins install @openclaw/matrix
```

Yerel bir checkout'tan yükleyin:

```bash
openclaw plugins install ./path/to/local/matrix-plugin
```

Eklenti davranışı ve kurulum kuralları için [Plugins](/tr/tools/plugin) bölümüne bakın.

## Kurulum

1. Matrix eklentisinin kullanılabilir olduğundan emin olun.
   - Güncel paketlenmiş OpenClaw sürümleri bunu zaten içerir.
   - Eski/özel kurulumlar bunu yukarıdaki komutlarla elle ekleyebilir.
2. Homeserver'ınızda bir Matrix hesabı oluşturun.
3. `channels.matrix` yapılandırmasını aşağıdakilerden biriyle yapın:
   - `homeserver` + `accessToken`, veya
   - `homeserver` + `userId` + `password`.
4. Gateway'i yeniden başlatın.
5. Bot ile bir DM başlatın veya onu bir odaya davet edin.

Etkileşimli kurulum yolları:

```bash
openclaw channels add
openclaw configure --section channels
```

Matrix sihirbazının gerçekte sordukları:

- homeserver URL'si
- kimlik doğrulama yöntemi: access token veya parola
- yalnızca parola ile kimlik doğrulamayı seçtiğinizde kullanıcı kimliği
- isteğe bağlı cihaz adı
- E2EE'nin etkinleştirilip etkinleştirilmeyeceği
- Matrix oda erişiminin şimdi yapılandırılıp yapılandırılmayacağı

Önemli sihirbaz davranışları:

- Seçilen hesap için Matrix kimlik doğrulama ortam değişkenleri zaten varsa ve bu hesabın kimlik doğrulaması yapılandırmada henüz kayıtlı değilse, sihirbaz bir ortam kısayolu sunar ve bu hesap için yalnızca `enabled: true` yazar.
- Etkileşimli olarak başka bir Matrix hesabı eklediğinizde, girilen hesap adı yapılandırma ve ortam değişkenlerinde kullanılan hesap kimliğine normalize edilir. Örneğin, `Ops Bot`, `ops-bot` olur.
- DM allowlist istemleri tam `@user:server` değerlerini doğrudan kabul eder. Görünen adlar yalnızca canlı dizin araması tek bir kesin eşleşme bulduğunda çalışır; aksi takdirde sihirbaz sizden tam Matrix kimliğiyle yeniden denemenizi ister.
- Oda allowlist istemleri oda kimliklerini ve takma adlarını doğrudan kabul eder. Ayrıca katılınmış oda adlarını canlı olarak çözebilirler, ancak çözümlenmeyen adlar yalnızca kurulum sırasında yazıldığı haliyle tutulur ve daha sonra çalışma zamanı allowlist çözümlemesi tarafından yok sayılır. `!room:server` veya `#alias:server` tercih edin.
- Çalışma zamanında oda/oturum kimliği kararlı Matrix oda kimliğini kullanır. Oda içinde tanımlanan takma adlar yalnızca arama girdisi olarak kullanılır; uzun vadeli oturum anahtarı veya kararlı grup kimliği olarak kullanılmaz.
- Oda adlarını kaydetmeden önce çözmek için `openclaw channels resolve --channel matrix "Project Room"` komutunu kullanın.

En az düzeyde token tabanlı kurulum:

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

Matrix, önbelleğe alınmış kimlik bilgilerini `~/.openclaw/credentials/matrix/` içinde saklar.
Varsayılan hesap `credentials.json` kullanır; adlandırılmış hesaplar `credentials-<account>.json` kullanır.
Orada önbelleğe alınmış kimlik bilgileri varsa, OpenClaw mevcut kimlik doğrulama doğrudan yapılandırmada ayarlı olmasa bile kurulum, doctor ve kanal durumu keşfi için Matrix'i yapılandırılmış olarak kabul eder.

Ortam değişkeni eşdeğerleri (yapılandırma anahtarı ayarlı değilse kullanılır):

- `MATRIX_HOMESERVER`
- `MATRIX_ACCESS_TOKEN`
- `MATRIX_USER_ID`
- `MATRIX_PASSWORD`
- `MATRIX_DEVICE_ID`
- `MATRIX_DEVICE_NAME`

Varsayılan olmayan hesaplar için hesap kapsamlı ortam değişkenleri kullanın:

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

Matrix, hesap kimliklerindeki noktalama işaretlerini kapsamlı ortam değişkenlerinde çakışmaları önlemek için kaçar.
Örneğin, `-`, `_X2D_` olur; bu nedenle `ops-prod`, `MATRIX_OPS_X2D_PROD_*` eşlemesine dönüşür.

Etkileşimli sihirbaz yalnızca bu kimlik doğrulama ortam değişkenleri zaten mevcutsa ve seçilen hesap için Matrix kimlik doğrulaması yapılandırmaya henüz kaydedilmemişse ortam değişkeni kısayolunu sunar.

## Yapılandırma örneği

Bu, DM eşleştirmesi, oda allowlist'i ve etkin E2EE içeren pratik bir temel yapılandırmadır:

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

## Akış önizlemeleri

Matrix yanıt akışı isteğe bağlıdır.

OpenClaw'ın tek bir canlı önizleme
yanıtı göndermesini, model metin üretirken bu önizlemeyi yerinde düzenlemesini ve ardından
yanıt tamamlandığında bunu sonlandırmasını istiyorsanız `channels.matrix.streaming` değerini `"partial"` olarak ayarlayın:

```json5
{
  channels: {
    matrix: {
      streaming: "partial",
    },
  },
}
```

- `streaming: "off"` varsayılandır. OpenClaw son yanıtı bekler ve onu tek seferde gönderir.
- `streaming: "partial"`, normal Matrix metin iletilerini kullanarak mevcut asistan bloğu için düzenlenebilir tek bir önizleme iletisi oluşturur. Bu, Matrix'in eski önizleme-öncelikli bildirim davranışını korur; bu nedenle standart istemciler tamamlanmış blok yerine ilk akış önizleme metni için bildirim gönderebilir.
- `streaming: "quiet"`, mevcut asistan bloğu için düzenlenebilir sessiz bir önizleme bildirimi oluşturur. Bunu yalnızca alıcı push kurallarını tamamlanmış önizleme düzenlemeleri için de yapılandırdığınızda kullanın.
- `blockStreaming: true` ayrı Matrix ilerleme iletilerini etkinleştirir. Önizleme akışı etkinleştirildiğinde, Matrix mevcut blok için canlı taslağı tutar ve tamamlanmış blokları ayrı iletiler olarak korur.
- Önizleme akışı açıkken `blockStreaming` kapalıysa, Matrix canlı taslağı yerinde düzenler ve blok veya tur bittiğinde aynı olayı sonlandırır.
- Önizleme artık tek bir Matrix olayına sığmıyorsa, OpenClaw önizleme akışını durdurur ve normal son teslimata geri döner.
- Medya yanıtları yine ekleri normal şekilde gönderir. Eski bir önizleme artık güvenli şekilde yeniden kullanılamıyorsa, OpenClaw son medya yanıtını göndermeden önce onu sansürler.
- Önizleme düzenlemeleri ek Matrix API çağrıları gerektirir. En korumacı hız sınırı davranışını istiyorsanız akışı kapalı bırakın.

`blockStreaming`, taslak önizlemeleri tek başına etkinleştirmez.
Önizleme düzenlemeleri için `streaming: "partial"` veya `streaming: "quiet"` kullanın; ardından yalnızca tamamlanmış asistan bloklarının ayrı ilerleme iletileri olarak görünür kalmasını da istiyorsanız `blockStreaming: true` ekleyin.

Özel push kuralları olmadan standart Matrix bildirimlerine ihtiyacınız varsa, önizleme-öncelikli davranış için `streaming: "partial"` kullanın veya yalnızca son teslimat için `streaming` özelliğini kapalı bırakın. `streaming: "off"` ile:

- `blockStreaming: true` her tamamlanmış bloğu normal bildirim veren bir Matrix iletisi olarak gönderir.
- `blockStreaming: false` yalnızca son tamamlanmış yanıtı normal bildirim veren bir Matrix iletisi olarak gönderir.

### Sessiz sonlandırılmış önizlemeler için self-hosted push kuralları

Kendi Matrix altyapınızı çalıştırıyorsanız ve sessiz önizlemelerin yalnızca bir blok veya
son yanıt tamamlandığında bildirim göndermesini istiyorsanız, `streaming: "quiet"` ayarlayın ve sonlandırılmış önizleme düzenlemeleri için kullanıcı başına bir push kuralı ekleyin.

Bu genellikle homeserver genelinde bir yapılandırma değişikliği değil, alıcı kullanıcı kurulumu olur:

Başlamadan önce hızlı eşleme:

- alıcı kullanıcı = bildirimi alması gereken kişi
- bot kullanıcısı = yanıtı gönderen OpenClaw Matrix hesabı
- aşağıdaki API çağrıları için alıcı kullanıcının access token'ını kullanın
- push kuralındaki `sender` alanını bot kullanıcısının tam MXID'siyle eşleştirin

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

2. Alıcı hesabın halihazırda normal Matrix push bildirimleri aldığından emin olun. Sessiz önizleme
   kuralları yalnızca o kullanıcının çalışan pusher'ları/cihazları zaten varsa çalışır.

3. Alıcı kullanıcının access token'ını alın.
   - Botun token'ını değil, alan kullanıcının token'ını kullanın.
   - Var olan bir istemci oturum token'ını yeniden kullanmak genellikle en kolay yoldur.
   - Yeni bir token üretmeniz gerekiyorsa, standart Matrix Client-Server API üzerinden giriş yapabilirsiniz:

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

4. Alıcı hesabın zaten pusher'lara sahip olduğunu doğrulayın:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushers"
```

Bu, etkin pusher/cihaz döndürmüyorsa, aşağıdaki
OpenClaw kuralını eklemeden önce önce normal Matrix bildirimlerini düzeltin.

OpenClaw, sonlandırılmış yalnızca metin önizleme düzenlemelerini şu işaretle işaretler:

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
- `openclaw-finalized-preview-botname`: bu alan kullanıcı için bu bota özgü bir kural kimliği
- `@bot:example.org`: alan kullanıcının MXID'si değil, OpenClaw Matrix bot MXID'niz

Çoklu bot kurulumları için önemli:

- Push kuralları `ruleId` ile anahtarlanır. Aynı kural kimliğine karşı `PUT` komutunu yeniden çalıştırmak o tek kuralı günceller.
- Bir alan kullanıcı birden fazla OpenClaw Matrix bot hesabı için bildirim alacaksa, her gönderen eşleşmesi için benzersiz bir kural kimliğiyle bot başına bir kural oluşturun.
- Basit bir desen `openclaw-finalized-preview-<botname>` olur; örneğin `openclaw-finalized-preview-ops` veya `openclaw-finalized-preview-support`.

Kural olay göndericisine göre değerlendirilir:

- alan kullanıcının token'ı ile kimlik doğrulayın
- `sender` alanını OpenClaw bot MXID'siyle eşleştirin

6. Kuralın var olduğunu doğrulayın:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

7. Akışlı bir yanıtı test edin. Sessiz modda oda, sessiz bir taslak önizleme göstermeli ve son
   yerinde düzenleme blok veya tur tamamlandığında bir kez bildirim göndermelidir.

Kuralı daha sonra kaldırmanız gerekirse, aynı kural kimliğini alan kullanıcının token'ı ile silin:

```bash
curl -sS -X DELETE \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

Notlar:

- Kuralı botunkini değil, alan kullanıcının access token'ı ile oluşturun.
- Yeni kullanıcı tanımlı `override` kuralları varsayılan bastırma kurallarının önüne eklenir; bu nedenle ek bir sıralama parametresi gerekmez.
- Bu yalnızca OpenClaw'ın güvenli şekilde yerinde sonlandırabildiği yalnızca metin önizleme düzenlemelerini etkiler. Medya fallback'leri ve eski önizleme fallback'leri yine normal Matrix teslimatını kullanır.
- `GET /_matrix/client/v3/pushers` hiçbir pusher göstermiyorsa, kullanıcı bu hesap/cihaz için henüz çalışan Matrix push teslimine sahip değildir.

#### Synapse

Synapse için yukarıdaki kurulum genellikle tek başına yeterlidir:

- Sonlandırılmış OpenClaw önizleme bildirimleri için özel bir `homeserver.yaml` değişikliği gerekmez.
- Synapse dağıtımınız zaten normal Matrix push bildirimleri gönderiyorsa, kullanıcı token'ı + yukarıdaki `pushrules` çağrısı ana kurulum adımıdır.
- Synapse'i bir reverse proxy veya worker'ların arkasında çalıştırıyorsanız, `/_matrix/client/.../pushrules/` isteğinin Synapse'e doğru ulaştığından emin olun.
- Synapse worker'ları kullanıyorsanız, pusher'ların sağlıklı olduğundan emin olun. Push teslimi ana süreç veya `synapse.app.pusher` / yapılandırılmış pusher worker'ları tarafından işlenir.

#### Tuwunel

Tuwunel için yukarıda gösterilen aynı kurulum akışını ve push kuralı API çağrısını kullanın:

- Sonlandırılmış önizleme işaretleyicisinin kendisi için Tuwunel'e özgü bir yapılandırma gerekmez.
- Normal Matrix bildirimleri o kullanıcı için zaten çalışıyorsa, kullanıcı token'ı + yukarıdaki `pushrules` çağrısı ana kurulum adımıdır.
- Kullanıcı başka bir cihazda etkin olduğunda bildirimler kayboluyor gibi görünüyorsa, `suppress_push_when_active` etkin olup olmadığını kontrol edin. Tuwunel bu seçeneği Tuwunel 1.4.2 sürümünde 12 Eylül 2025 tarihinde ekledi ve bu seçenek bir cihaz etkin durumdayken diğer cihazlara gönderilen push'ları bilerek bastırabilir.

## Şifreleme ve doğrulama

Şifreli (E2EE) odalarda, giden görsel olayları `thumbnail_file` kullanır; böylece görsel önizlemeleri tam ek ile birlikte şifrelenir. Şifrelenmemiş odalar yine düz `thumbnail_url` kullanır. Yapılandırma gerekmez — eklenti E2EE durumunu otomatik olarak algılar.

### Botlar arası odalar

Varsayılan olarak, yapılandırılmış diğer OpenClaw Matrix hesaplarından gelen Matrix iletileri yok sayılır.

Kasıtlı olarak ajanlar arası Matrix trafiği istediğinizde `allowBots` kullanın:

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

- `allowBots: true`, izin verilen odalarda ve DM'lerde yapılandırılmış diğer Matrix bot hesaplarından gelen iletileri kabul eder.
- `allowBots: "mentions"`, bu iletileri odalarda yalnızca bu bottan görünür şekilde bahsediyorsa kabul eder. DM'lere yine izin verilir.
- `groups.<room>.allowBots`, hesap düzeyindeki ayarı bir oda için geçersiz kılar.
- OpenClaw, kendi kendine yanıt döngülerini önlemek için yine aynı Matrix kullanıcı kimliğinden gelen iletileri yok sayar.
- Matrix burada yerel bir bot işareti sağlamaz; OpenClaw "bot tarafından yazılmış" ifadesini "bu OpenClaw gateway üzerinde yapılandırılmış başka bir Matrix hesabı tarafından gönderilmiş" olarak yorumlar.

Paylaşılan odalarda botlar arası trafiği etkinleştirirken sıkı oda allowlist'leri ve mention gereksinimleri kullanın.

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

Makine tarafından okunabilir çıktıya saklanan kurtarma anahtarını dahil edin:

```bash
openclaw matrix verify status --include-recovery-key --json
```

Çapraz imzalama ve doğrulama durumunu bootstrap edin:

```bash
openclaw matrix verify bootstrap
```

Çoklu hesap desteği: hesap başına kimlik bilgileri ve isteğe bağlı `name` ile `channels.matrix.accounts` kullanın. Ortak desen için [Configuration reference](/tr/gateway/configuration-reference#multi-account-all-channels) bölümüne bakın.

Ayrıntılı bootstrap tanılaması:

```bash
openclaw matrix verify bootstrap --verbose
```

Bootstrap öncesi yeni bir çapraz imzalama kimliği sıfırlamasını zorlayın:

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

Sunucu yedeğinden oda anahtarlarını geri yükleyin:

```bash
openclaw matrix verify backup restore
```

Ayrıntılı geri yükleme tanılaması:

```bash
openclaw matrix verify backup restore --verbose
```

Mevcut sunucu yedeğini silin ve yeni bir yedekleme temel düzeyi oluşturun. Saklanan
yedekleme anahtarı temiz şekilde yüklenemiyorsa, bu sıfırlama gizli depolamayı da yeniden oluşturarak
gelecekteki soğuk başlangıçların yeni yedekleme anahtarını yükleyebilmesini sağlayabilir:

```bash
openclaw matrix verify backup reset --yes
```

Tüm `verify` komutları varsayılan olarak özdür (sessiz dahili SDK günlüklemesi dahil) ve yalnızca `--verbose` ile ayrıntılı tanılama gösterir.
Betik yazarken tam makine tarafından okunabilir çıktı için `--json` kullanın.

Çoklu hesap kurulumlarında, Matrix CLI komutları `--account <id>` parametresini vermediğiniz sürece örtük Matrix varsayılan hesabını kullanır.
Birden fazla adlandırılmış hesap yapılandırırsanız, önce `channels.matrix.defaultAccount` ayarlayın; aksi takdirde bu örtük CLI işlemleri durur ve sizden açıkça bir hesap seçmenizi ister.
Doğrulama veya cihaz işlemlerinin açıkça adlandırılmış bir hesabı hedeflemesini istediğinizde `--account` kullanın:

```bash
openclaw matrix verify status --account assistant
openclaw matrix verify backup restore --account assistant
openclaw matrix devices list --account assistant
```

Şifreleme devre dışıysa veya adlandırılmış bir hesap için kullanılamıyorsa, Matrix uyarıları ve doğrulama hataları o hesabın yapılandırma anahtarını işaret eder; örneğin `channels.matrix.accounts.assistant.encryption`.

### "Doğrulanmış" ne anlama gelir

OpenClaw, bu Matrix cihazını yalnızca kendi çapraz imzalama kimliğiniz tarafından doğrulandığında doğrulanmış kabul eder.
Uygulamada, `openclaw matrix verify status --verbose` üç güven sinyali gösterir:

- `Locally trusted`: bu cihaz yalnızca mevcut istemci tarafından güvenilir kabul edilir
- `Cross-signing verified`: SDK, cihazın çapraz imzalama yoluyla doğrulandığını bildirir
- `Signed by owner`: cihaz kendi self-signing anahtarınız tarafından imzalanmıştır

`Verified by owner`, yalnızca çapraz imzalama doğrulaması veya sahip imzası mevcut olduğunda `yes` olur.
Yerel güven tek başına OpenClaw'ın cihazı tamamen doğrulanmış kabul etmesi için yeterli değildir.

### Bootstrap ne yapar

`openclaw matrix verify bootstrap`, şifrelenmiş Matrix hesapları için onarım ve kurulum komutudur.
Aşağıdakilerin tümünü sırayla yapar:

- gizli depolamayı bootstrap eder ve mümkün olduğunda mevcut bir kurtarma anahtarını yeniden kullanır
- çapraz imzalamayı bootstrap eder ve eksik genel çapraz imzalama anahtarlarını yükler
- mevcut cihazı işaretlemeyi ve çapraz imzalamayı dener
- henüz yoksa yeni bir sunucu tarafı oda anahtarı yedeği oluşturur

Homeserver çapraz imzalama anahtarlarını yüklemek için etkileşimli kimlik doğrulaması gerektiriyorsa, OpenClaw önce kimlik doğrulaması olmadan, ardından `m.login.dummy` ile, sonra `channels.matrix.password` yapılandırılmışsa `m.login.password` ile yüklemeyi dener.

`--force-reset-cross-signing` seçeneğini yalnızca mevcut çapraz imzalama kimliğini bilerek silmek ve yenisini oluşturmak istediğinizde kullanın.

Mevcut oda anahtarı yedeğini bilerek silmek ve gelecekteki iletiler için yeni
bir yedekleme temel düzeyi başlatmak istiyorsanız, `openclaw matrix verify backup reset --yes` kullanın.
Bunu yalnızca kurtarılamayan eski şifreli geçmişin erişilemez kalacağını ve
OpenClaw'ın mevcut yedekleme sırrı güvenli şekilde yüklenemiyorsa gizli depolamayı yeniden oluşturabileceğini kabul ediyorsanız yapın.

### Yeni yedekleme temel düzeyi

Gelecekteki şifreli iletilerin çalışmaya devam etmesini istiyorsanız ve kurtarılamayan eski geçmişi kaybetmeyi kabul ediyorsanız, şu komutları sırayla çalıştırın:

```bash
openclaw matrix verify backup reset --yes
openclaw matrix verify backup status --verbose
openclaw matrix verify status
```

Adlandırılmış bir Matrix hesabını açıkça hedeflemek istediğinizde her komuta `--account <id>` ekleyin.

### Başlangıç davranışı

`encryption: true` olduğunda Matrix varsayılan olarak `startupVerification` değerini `"if-unverified"` yapar.
Başlangıçta bu cihaz hâlâ doğrulanmamışsa, Matrix başka bir Matrix istemcisinde öz-doğrulama ister,
biri zaten beklemedeyken yinelenen istekleri atlar ve yeniden başlatmalardan sonra tekrar denemeden önce yerel bir bekleme süresi uygular.
Başarısız istek denemeleri varsayılan olarak başarılı istek oluşturmadan daha erken yeniden denenir.
Otomatik başlangıç isteklerini devre dışı bırakmak için `startupVerification: "off"` ayarlayın veya daha kısa ya da daha uzun bir yeniden deneme aralığı istiyorsanız `startupVerificationCooldownHours` değerini ayarlayın.

Başlangıç ayrıca otomatik olarak korumacı bir kripto bootstrap geçişi de gerçekleştirir.
Bu geçiş, önce mevcut gizli depolamayı ve çapraz imzalama kimliğini yeniden kullanmayı dener ve siz açık bir bootstrap onarım akışı çalıştırmadığınız sürece çapraz imzalamayı sıfırlamaktan kaçınır.

Başlangıç bozuk bootstrap durumu bulursa ve `channels.matrix.password` yapılandırılmışsa, OpenClaw daha katı bir onarım yolunu deneyebilir.
Mevcut cihaz zaten owner-signed ise, OpenClaw bu kimliği otomatik olarak sıfırlamak yerine korur.

Önceki herkese açık Matrix eklentisinden yükseltme:

- OpenClaw mümkün olduğunda aynı Matrix hesabını, access token'ı ve cihaz kimliğini otomatik olarak yeniden kullanır.
- Uygulanabilir herhangi bir Matrix geçiş değişikliği çalışmadan önce, OpenClaw `~/Backups/openclaw-migrations/` altında bir kurtarma anlık görüntüsü oluşturur veya yeniden kullanır.
- Birden fazla Matrix hesabı kullanıyorsanız, OpenClaw'ın bu paylaşılan eski durumu hangi hesabın alacağını bilmesi için eski düz depo düzeninden yükseltmeden önce `channels.matrix.defaultAccount` ayarlayın.
- Önceki eklenti Matrix oda anahtarı yedek çözme anahtarını yerel olarak sakladıysa, başlangıç veya `openclaw doctor --fix` bunu yeni kurtarma anahtarı akışına otomatik olarak aktarır.
- Matrix access token geçiş hazırlandıktan sonra değiştiyse, başlangıç artık otomatik yedek geri yüklemeden vazgeçmeden önce bekleyen eski geri yükleme durumu için kardeş token-hash depolama köklerini tarar.
- Matrix access token daha sonra aynı hesap, homeserver ve kullanıcı için değişirse, OpenClaw artık boş bir Matrix durum dizininden başlamak yerine en eksiksiz mevcut token-hash depolama kökünü yeniden kullanmayı tercih eder.
- Bir sonraki gateway başlangıcında, yedeklenmiş oda anahtarları otomatik olarak yeni kripto deposuna geri yüklenir.
- Eski eklentide hiç yedeklenmemiş yalnızca yerel oda anahtarları varsa, OpenClaw açık şekilde uyarır. Bu anahtarlar önceki rust kripto deposundan otomatik olarak dışa aktarılamaz; bu nedenle bazı eski şifreli geçmişler elle kurtarılana kadar erişilemez kalabilir.
- Tam yükseltme akışı, sınırlar, kurtarma komutları ve yaygın geçiş iletileri için [Matrix migration](/tr/install/migrating-matrix) bölümüne bakın.

Şifreli çalışma zamanı durumu, hesap başına, kullanıcı başına token-hash kökleri altında
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/` içinde düzenlenir.
Bu dizin sync deposunu (`bot-storage.json`), kripto deposunu (`crypto/`),
kurtarma anahtarı dosyasını (`recovery-key.json`), IndexedDB anlık görüntüsünü (`crypto-idb-snapshot.json`),
ileti dizisi bağlarını (`thread-bindings.json`) ve başlangıç doğrulama durumunu (`startup-verification.json`)
bu özellikler kullanıldığında içerir.
Token değişse de hesap kimliği aynı kaldığında, OpenClaw o hesap/homeserver/kullanıcı üçlüsü için en iyi mevcut
kökü yeniden kullanır; böylece önceki sync durumu, kripto durumu, ileti dizisi bağları
ve başlangıç doğrulama durumu görünür kalır.

### Node crypto store modeli

Bu eklentideki Matrix E2EE, Node içinde resmi `matrix-js-sdk` Rust kripto yolunu kullanır.
Kalıcı olmasını istediğinizde bu yol, yeniden başlatmalar arasında kripto durumunu korumak için IndexedDB destekli kalıcılık bekler.

OpenClaw şu anda Node içinde bunu şu şekilde sağlar:

- SDK'nin beklediği IndexedDB API shim'i olarak `fake-indexeddb` kullanma
- `initRustCrypto` öncesinde Rust kripto IndexedDB içeriğini `crypto-idb-snapshot.json` dosyasından geri yükleme
- init sonrasında ve çalışma zamanı sırasında güncellenmiş IndexedDB içeriğini yeniden `crypto-idb-snapshot.json` içine kalıcı hale getirme
- gateway çalışma zamanı kalıcılığı ile CLI bakımının aynı anlık görüntü dosyasında yarışmaması için anlık görüntü geri yükleme ve kalıcılığı `crypto-idb-snapshot.json` üzerinde danışmalı bir dosya kilidiyle serileştirme

Bu, özel bir kripto uygulaması değil, uyumluluk/depolama altyapısıdır.
Anlık görüntü dosyası hassas çalışma zamanı durumudur ve kısıtlayıcı dosya izinleriyle saklanır.
OpenClaw'ın güvenlik modeline göre gateway host ve yerel OpenClaw durum dizini zaten güvenilir operatör sınırı içindedir; bu nedenle bu öncelikle ayrı bir uzak güven sınırından ziyade operasyonel dayanıklılık konusudur.

Planlanan iyileştirme:

- kalıcı Matrix anahtar materyali için SecretRef desteği eklemek; böylece kurtarma anahtarları ve ilgili depo şifreleme sırları yalnızca yerel dosyalardan değil OpenClaw gizli bilgi sağlayıcılarından da alınabilir

## Profil yönetimi

Seçilen hesap için Matrix öz-profilini şu şekilde güncelleyin:

```bash
openclaw matrix profile set --name "OpenClaw Assistant"
openclaw matrix profile set --avatar-url https://cdn.example.org/avatar.png
```

Adlandırılmış bir Matrix hesabını açıkça hedeflemek istediğinizde `--account <id>` ekleyin.

Matrix, `mxc://` avatar URL'lerini doğrudan kabul eder. Bir `http://` veya `https://` avatar URL'si verdiğinizde, OpenClaw önce onu Matrix'e yükler ve çözümlenen `mxc://` URL'sini yeniden `channels.matrix.avatarUrl` içine (veya seçilen hesap geçersiz kılmasına) kaydeder.

## Otomatik doğrulama bildirimleri

Matrix artık doğrulama yaşam döngüsü bildirimlerini doğrudan sıkı DM doğrulama odasına `m.notice` iletileri olarak gönderir.
Buna şunlar dahildir:

- doğrulama isteği bildirimleri
- doğrulama hazır bildirimleri (açık "emoji ile doğrula" yönlendirmesiyle)
- doğrulama başlangıç ve tamamlama bildirimleri
- mevcut olduğunda SAS ayrıntıları (emoji ve ondalık)

Başka bir Matrix istemcisinden gelen doğrulama istekleri izlenir ve OpenClaw tarafından otomatik kabul edilir.
Öz-doğrulama akışlarında, OpenClaw emoji doğrulaması kullanılabilir olduğunda SAS akışını da otomatik olarak başlatır ve kendi tarafını onaylar.
Başka bir Matrix kullanıcı/cihazından gelen doğrulama isteklerinde, OpenClaw isteği otomatik kabul eder ve ardından SAS akışının normal şekilde ilerlemesini bekler.
Doğrulamayı tamamlamak için Matrix istemcinizde emoji veya ondalık SAS değerini karşılaştırmanız ve orada "They match" onayı vermeniz yine gerekir.

OpenClaw, kendi başlattığı yinelenen akışları körü körüne otomatik kabul etmez. Başlangıç, öz-doğrulama isteği zaten beklemedeyse yeni bir istek oluşturmaz.

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

Doğrudan ileti durumu eşzamansız hale gelirse, OpenClaw canlı DM yerine eski tekli odaları gösteren bayat `m.direct` eşlemeleriyle karşılaşabilir. Bir eş için mevcut eşlemeyi şu komutla inceleyin:

```bash
openclaw matrix direct inspect --user-id @alice:example.org
```

Şu komutla onarın:

```bash
openclaw matrix direct repair --user-id @alice:example.org
```

Onarım, Matrix'e özgü mantığı eklentinin içinde tutar:

- önce `m.direct` içinde zaten eşlenmiş olan sıkı 1:1 DM'yi tercih eder
- aksi takdirde bu kullanıcıyla hâlihazırda katılınmış herhangi bir sıkı 1:1 DM'ye geri döner
- sağlıklı bir DM yoksa yeni bir doğrudan oda oluşturur ve `m.direct` eşlemesini ona işaret edecek şekilde yeniden yazar

Onarım akışı eski odaları otomatik olarak silmez. Yalnızca sağlıklı DM'yi seçer ve eşlemeyi günceller; böylece yeni Matrix gönderimleri, doğrulama bildirimleri ve diğer doğrudan ileti akışları yeniden doğru odayı hedefler.

## İleti dizileri

Matrix, hem otomatik yanıtlar hem de ileti aracı gönderimleri için yerel Matrix ileti dizilerini destekler.

- `dm.sessionScope: "per-user"` (varsayılan), Matrix DM yönlendirmesini gönderen kapsamlı tutar; böylece birden fazla DM odası aynı eşe çözümlendiğinde tek bir oturumu paylaşabilir.
- `dm.sessionScope: "per-room"`, normal DM kimlik doğrulaması ve allowlist kontrollerini kullanmaya devam ederken her Matrix DM odasını kendi oturum anahtarına ayırır.
- Açık Matrix konuşma bağları yine `dm.sessionScope` ayarına üstün gelir; bu nedenle bağlanmış odalar ve ileti dizileri seçtikleri hedef oturumu korur.
- `threadReplies: "off"`, yanıtları üst düzeyde tutar ve gelen dizili iletileri ana oturumda tutar.
- `threadReplies: "inbound"`, yalnızca gelen ileti zaten o ileti dizisindeyse o ileti dizisi içinde yanıt verir.
- `threadReplies: "always"`, oda yanıtlarını tetikleyen iletiye köklenen bir ileti dizisinde tutar ve o konuşmayı ilk tetikleyen iletiden itibaren eşleşen ileti dizisi kapsamlı oturum üzerinden yönlendirir.
- `dm.threadReplies`, üst düzey ayarı yalnızca DM'ler için geçersiz kılar. Örneğin, odalardaki ileti dizilerini ayrık tutarken DM'leri düz tutabilirsiniz.
- Gelen dizili iletiler, ileti dizisi kök iletisini ek ajan bağlamı olarak içerir.
- İleti aracı gönderimleri artık hedef aynı odaysa veya aynı DM kullanıcı hedefiyse, açık `threadId` verilmediği sürece mevcut Matrix ileti dizisini otomatik devralır.
- Aynı oturumlu DM kullanıcı hedefi yeniden kullanımı yalnızca mevcut oturum meta verileri aynı Matrix hesabındaki aynı DM eşini kanıtladığında devreye girer; aksi takdirde OpenClaw normal kullanıcı kapsamlı yönlendirmeye geri döner.
- OpenClaw, bir Matrix DM odasının aynı paylaşılan Matrix DM oturumundaki başka bir DM odasıyla çakıştığını gördüğünde, ileti dizisi bağları etkinse ve `dm.sessionScope` ipucu mevcutsa bu odaya `/focus` kaçış yolunu içeren tek seferlik bir `m.notice` gönderir.
- Çalışma zamanı ileti dizisi bağları Matrix için desteklenir. `/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age` ve ileti dizisine bağlı `/acp spawn` artık Matrix odalarında ve DM'lerde çalışır.
- Üst düzey Matrix oda/DM `/focus`, `threadBindings.spawnSubagentSessions=true` olduğunda yeni bir Matrix ileti dizisi oluşturur ve bunu hedef oturuma bağlar.
- Mevcut bir Matrix ileti dizisi içinde `/focus` veya `/acp spawn --thread here` çalıştırmak bunun yerine mevcut ileti dizisini bağlar.

## ACP konuşma bağları

Matrix odaları, DM'ler ve mevcut Matrix ileti dizileri sohbet yüzeyini değiştirmeden kalıcı ACP çalışma alanlarına dönüştürülebilir.

Hızlı operatör akışı:

- Kullanmaya devam etmek istediğiniz Matrix DM, oda veya mevcut ileti dizisi içinde `/acp spawn codex --bind here` çalıştırın.
- Üst düzey bir Matrix DM veya odasında, mevcut DM/oda sohbet yüzeyi olarak kalır ve gelecekteki iletiler oluşturulan ACP oturumuna yönlendirilir.
- Mevcut bir Matrix ileti dizisi içinde, `--bind here` mevcut ileti dizisini yerinde bağlar.
- `/new` ve `/reset`, aynı bağlı ACP oturumunu yerinde sıfırlar.
- `/acp close`, ACP oturumunu kapatır ve bağı kaldırır.

Notlar:

- `--bind here`, alt bir Matrix ileti dizisi oluşturmaz.
- `threadBindings.spawnAcpSessions` yalnızca OpenClaw'ın alt bir Matrix ileti dizisi oluşturması veya bağlaması gereken `/acp spawn --thread auto|here` için gereklidir.

### İleti Dizisi Bağlama Yapılandırması

Matrix, genel varsayılanları `session.threadBindings` üzerinden devralır ve ayrıca kanal başına geçersiz kılmaları destekler:

- `threadBindings.enabled`
- `threadBindings.idleHours`
- `threadBindings.maxAgeHours`
- `threadBindings.spawnSubagentSessions`
- `threadBindings.spawnAcpSessions`

Matrix ileti dizisine bağlı oluşturma işaretleri isteğe bağlıdır:

- Üst düzey `/focus` komutunun yeni Matrix ileti dizileri oluşturup bağlamasına izin vermek için `threadBindings.spawnSubagentSessions: true` ayarlayın.
- `/acp spawn --thread auto|here` komutunun ACP oturumlarını Matrix ileti dizilerine bağlamasına izin vermek için `threadBindings.spawnAcpSessions: true` ayarlayın.

## Tepkiler

Matrix, giden tepki eylemlerini, gelen tepki bildirimlerini ve gelen onay tepkilerini destekler.

- Giden tepki araçları `channels["matrix"].actions.reactions` ile sınırlandırılır.
- `react`, belirli bir Matrix olayına tepki ekler.
- `reactions`, belirli bir Matrix olayı için mevcut tepki özetini listeler.
- `emoji=""`, bot hesabının o olay üzerindeki kendi tepkilerini kaldırır.
- `remove: true`, bot hesabından yalnızca belirtilen emoji tepkisini kaldırır.

Onay tepkisi kapsamı standart OpenClaw çözümleme sırasını kullanır:

- `channels["matrix"].accounts.<accountId>.ackReaction`
- `channels["matrix"].ackReaction`
- `messages.ackReaction`
- ajan kimliği emoji fallback'i

Onay tepkisi kapsamı şu sırayla çözülür:

- `channels["matrix"].accounts.<accountId>.ackReactionScope`
- `channels["matrix"].ackReactionScope`
- `messages.ackReactionScope`

Tepki bildirim modu şu sırayla çözülür:

- `channels["matrix"].accounts.<accountId>.reactionNotifications`
- `channels["matrix"].reactionNotifications`
- varsayılan: `own`

Mevcut davranış:

- `reactionNotifications: "own"`, bot tarafından yazılmış Matrix iletilerini hedeflediğinde eklenen `m.reaction` olaylarını iletir.
- `reactionNotifications: "off"`, tepki sistem olaylarını devre dışı bırakır.
- Tepki kaldırmaları hâlâ sistem olaylarına dönüştürülmez; çünkü Matrix bunları bağımsız `m.reaction` kaldırmaları olarak değil sansürler olarak gösterir.

## Geçmiş bağlamı

- `channels.matrix.historyLimit`, bir Matrix oda iletisi ajanı tetiklediğinde `InboundHistory` olarak dahil edilen son oda iletilerinin sayısını kontrol eder.
- `messages.groupChat.historyLimit` değerine geri döner. Devre dışı bırakmak için `0` ayarlayın.
- Matrix oda geçmişi yalnızca odaya özeldir. DM'ler normal oturum geçmişini kullanmaya devam eder.
- Matrix oda geçmişi yalnızca bekleyen iletiler içindir: OpenClaw henüz yanıt tetiklememiş oda iletilerini tamponlar, sonra bir mention veya başka bir tetikleyici geldiğinde bu pencerenin anlık görüntüsünü alır.
- Mevcut tetikleyici ileti `InboundHistory` içine dahil edilmez; o tur için ana gelen gövdede kalır.
- Aynı Matrix olayının yeniden denemeleri, daha yeni oda iletilerine kaymak yerine orijinal geçmiş anlık görüntüsünü yeniden kullanır.

## Bağlam görünürlüğü

Matrix, getirilen yanıt metni, ileti dizisi kökleri ve bekleyen geçmiş gibi ek oda bağlamı için paylaşılan `contextVisibility` denetimini destekler.

- `contextVisibility: "all"` varsayılandır. Ek bağlam alındığı gibi korunur.
- `contextVisibility: "allowlist"`, ek bağlamı etkin oda/kullanıcı allowlist denetimleri tarafından izin verilen gönderenlerle sınırlar.
- `contextVisibility: "allowlist_quote"`, `allowlist` gibi davranır ancak yine de tek bir açık alıntılanmış yanıtı korur.

Bu ayar ek bağlam görünürlüğünü etkiler; gelen iletinin kendisinin yanıt tetikleyip tetikleyemeyeceğini değil.
Tetikleme yetkilendirmesi hâlâ `groupPolicy`, `groups`, `groupAllowFrom` ve DM politika ayarlarından gelir.

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

Mention kapılama ve allowlist davranışı için [Groups](/tr/channels/groups) bölümüne bakın.

Matrix DM'leri için eşleştirme örneği:

```bash
openclaw pairing list matrix
openclaw pairing approve matrix <CODE>
```

Onaylanmamış bir Matrix kullanıcısı onaydan önce size mesaj göndermeye devam ederse, OpenClaw aynı bekleyen eşleştirme kodunu yeniden kullanır ve yeni bir kod üretmek yerine kısa bir bekleme süresinden sonra yeniden hatırlatma yanıtı gönderebilir.

Paylaşılan DM eşleştirme akışı ve depolama düzeni için [Pairing](/tr/channels/pairing) bölümüne bakın.

## Exec onayları

Matrix, bir Matrix hesabı için exec onay istemcisi olarak davranabilir.

- `channels.matrix.execApprovals.enabled`
- `channels.matrix.execApprovals.approvers` (isteğe bağlı; `channels.matrix.dm.allowFrom` değerine geri döner)
- `channels.matrix.execApprovals.target` (`dm` | `channel` | `both`, varsayılan: `dm`)
- `channels.matrix.execApprovals.agentFilter`
- `channels.matrix.execApprovals.sessionFilter`

Onaylayıcılar `@owner:example.org` gibi Matrix kullanıcı kimlikleri olmalıdır. Matrix, `enabled` ayarsız veya `"auto"` olduğunda ve en az bir onaylayıcı çözümlenebildiğinde yerel exec onaylarını otomatik etkinleştirir; bu, ya `execApprovals.approvers` ya da `channels.matrix.dm.allowFrom` üzerinden olabilir. Matrix'i yerel onay istemcisi olarak açıkça devre dışı bırakmak için `enabled: false` ayarlayın. Aksi halde onay istekleri diğer yapılandırılmış onay yollarına veya exec onay fallback politikasına geri döner.

Yerel Matrix yönlendirmesi bugün yalnızca exec içindir:

- `channels.matrix.execApprovals.*`, yalnızca exec onayları için yerel DM/kanal yönlendirmesini kontrol eder.
- Eklenti onayları hâlâ paylaşılan aynı sohbet `/approve` komutunu ve yapılandırılmış tüm `approvals.plugin` yönlendirmesini kullanır.
- Matrix, onaylayıcıları güvenli şekilde çıkarabildiğinde eklenti onayı yetkilendirmesi için yine `channels.matrix.dm.allowFrom` kullanabilir, ancak ayrı bir yerel eklenti onayı DM/kanal fanout yolu sunmaz.

Teslimat kuralları:

- `target: "dm"`, onay istemlerini onaylayıcı DM'lerine gönderir
- `target: "channel"`, istemi kaynak Matrix odasına veya DM'ye geri gönderir
- `target: "both"`, onaylayıcı DM'lerine ve kaynak Matrix odasına veya DM'ye gönderir

Matrix onay istemleri, birincil onay iletisine tepki kısayolları ekler:

- `✅` = bir kez izin ver
- `❌` = reddet
- `♾️` = karar etkin exec politikası tarafından izin veriliyorsa her zaman izin ver

Onaylayıcılar bu ileti üzerinde tepki verebilir veya fallback slash komutlarını kullanabilir: `/approve <id> allow-once`, `/approve <id> allow-always` veya `/approve <id> deny`.

Yalnızca çözümlenmiş onaylayıcılar izin verebilir veya reddedebilir. Kanal teslimatı komut metnini içerir; bu nedenle `channel` veya `both` seçeneklerini yalnızca güvenilir odalarda etkinleştirin.

Matrix onay istemleri paylaşılan çekirdek onay planlayıcısını yeniden kullanır. Matrix'e özgü yerel yüzey exec onayları için yalnızca taşıma katmanıdır: oda/DM yönlendirmesi ile ileti gönderme/güncelleme/silme davranışı.

Hesap başına geçersiz kılma:

- `channels.matrix.accounts.<account>.execApprovals`

İlgili belgeler: [Exec approvals](/tr/tools/exec-approvals)

## Çoklu hesap örneği

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

Üst düzey `channels.matrix` değerleri, bir hesap tarafından geçersiz kılınmadığı sürece adlandırılmış hesaplar için varsayılan görevi görür.
Devralınan oda girdilerini tek bir Matrix hesabına `groups.<room>.account` (veya eski `rooms.<room>.account`) ile kapsamlandırabilirsiniz.
`account` içermeyen girdiler tüm Matrix hesapları arasında paylaşılır ve `account: "default"` içeren girdiler varsayılan hesap doğrudan üst düzey `channels.matrix.*` üzerinde yapılandırıldığında yine çalışır.
Kısmi paylaşılan kimlik doğrulama varsayılanları kendi başına ayrı bir örtük varsayılan hesap oluşturmaz. OpenClaw yalnızca üst düzey `default` hesabını, o varsayılan hesap yeni kimlik doğrulamaya sahipse (`homeserver` artı `accessToken` veya `homeserver` artı `userId` ve `password`) sentezler; adlandırılmış hesaplar, önbelleğe alınmış kimlik bilgileri daha sonra kimlik doğrulamayı sağlarsa `homeserver` artı `userId` üzerinden keşfedilebilir kalabilir.
Matrix'te zaten tam olarak bir adlandırılmış hesap varsa veya `defaultAccount` mevcut bir adlandırılmış hesap anahtarını işaret ediyorsa, tek hesaptan çoklu hesaba onarım/kurulum yükseltmesi yeni bir `accounts.default` girdisi oluşturmak yerine o hesabı korur. Yalnızca Matrix kimlik doğrulama/bootstrap anahtarları bu yükseltilmiş hesaba taşınır; paylaşılan teslimat politikası anahtarları üst düzeyde kalır.
Örtük yönlendirme, yoklama ve CLI işlemleri için OpenClaw'ın adlandırılmış bir Matrix hesabını tercih etmesini istiyorsanız `defaultAccount` ayarlayın.
Birden fazla adlandırılmış hesap yapılandırırsanız, örtük hesap seçimine dayanan CLI komutları için `defaultAccount` ayarlayın veya `--account <id>` geçin.
Bir komut için bu örtük seçimi geçersiz kılmak istediğinizde `openclaw matrix verify ...` ve `openclaw matrix devices ...` komutlarına `--account <id>` geçin.

## Özel/LAN homeserver'lar

Varsayılan olarak OpenClaw, siz
hesap başına açıkça izin vermediğiniz sürece SSRF koruması için özel/iç Matrix homeserver'larını engeller.

Homeserver'ınız localhost, bir LAN/Tailscale IP'si veya iç bir host adı üzerinde çalışıyorsa,
o Matrix hesabı için `allowPrivateNetwork` etkinleştirin:

```json5
{
  channels: {
    matrix: {
      homeserver: "http://matrix-synapse:8008",
      allowPrivateNetwork: true,
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

Bu isteğe bağlı etkinleştirme yalnızca güvenilir özel/iç hedeflere izin verir. `http://matrix.example.org:8008` gibi
genel düz metin homeserver'lar yine engellenir. Mümkün olduğunda `https://` tercih edin.

## Matrix trafiğini proxy üzerinden yönlendirme

Matrix dağıtımınız açık bir giden HTTP(S) proxy gerektiriyorsa, `channels.matrix.proxy` ayarlayın:

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
OpenClaw aynı proxy ayarını çalışma zamanı Matrix trafiği ve hesap durumu yoklamaları için kullanır.

## Hedef çözümleme

OpenClaw sizden bir oda veya kullanıcı hedefi istediğinde Matrix şu hedef biçimlerini kabul eder:

- Kullanıcılar: `@user:server`, `user:@user:server` veya `matrix:user:@user:server`
- Odalar: `!room:server`, `room:!room:server` veya `matrix:room:!room:server`
- Takma adlar: `#alias:server`, `channel:#alias:server` veya `matrix:channel:#alias:server`

Canlı dizin araması oturum açmış Matrix hesabını kullanır:

- Kullanıcı aramaları o homeserver'daki Matrix kullanıcı dizinini sorgular.
- Oda aramaları açık oda kimliklerini ve takma adlarını doğrudan kabul eder, sonra bu hesap için katılınmış oda adlarını aramaya geri döner.
- Katılınmış oda adı araması en iyi çaba esaslıdır. Bir oda adı bir kimliğe veya takma ada çözümlenemezse, çalışma zamanı allowlist çözümlemesi tarafından yok sayılır.

## Yapılandırma başvurusu

- `enabled`: kanalı etkinleştirir veya devre dışı bırakır.
- `name`: hesap için isteğe bağlı etiket.
- `defaultAccount`: birden fazla Matrix hesabı yapılandırıldığında tercih edilen hesap kimliği.
- `homeserver`: homeserver URL'si; örneğin `https://matrix.example.org`.
- `allowPrivateNetwork`: bu Matrix hesabının özel/iç homeserver'lara bağlanmasına izin verir. Homeserver `localhost`, bir LAN/Tailscale IP'si veya `matrix-synapse` gibi iç bir host'a çözülüyorsa bunu etkinleştirin.
- `proxy`: Matrix trafiği için isteğe bağlı HTTP(S) proxy URL'si. Adlandırılmış hesaplar üst düzey varsayılanı kendi `proxy` değerleriyle geçersiz kılabilir.
- `userId`: tam Matrix kullanıcı kimliği; örneğin `@bot:example.org`.
- `accessToken`: token tabanlı kimlik doğrulama için access token. `channels.matrix.accessToken` ve `channels.matrix.accounts.<id>.accessToken` için env/file/exec sağlayıcılarında düz metin değerleri ve SecretRef değerleri desteklenir. Bkz. [Secrets Management](/tr/gateway/secrets).
- `password`: parola tabanlı giriş için parola. Düz metin değerleri ve SecretRef değerleri desteklenir.
- `deviceId`: açık Matrix cihaz kimliği.
- `deviceName`: parola girişi için cihaz görünen adı.
- `avatarUrl`: profil eşitlemesi ve `set-profile` güncellemeleri için saklanan öz-avatar URL'si.
- `initialSyncLimit`: başlangıç sync olay sınırı.
- `encryption`: E2EE'yi etkinleştirir.
- `allowlistOnly`: DM'ler ve odalar için yalnızca allowlist davranışını zorlar.
- `allowBots`: yapılandırılmış diğer OpenClaw Matrix hesaplarından gelen iletilere izin verir (`true` veya `"mentions"`).
- `groupPolicy`: `open`, `allowlist` veya `disabled`.
- `contextVisibility`: ek oda bağlamı görünürlük modu (`all`, `allowlist`, `allowlist_quote`).
- `groupAllowFrom`: oda trafiği için kullanıcı kimlikleri allowlist'i.
- `groupAllowFrom` girdileri tam Matrix kullanıcı kimlikleri olmalıdır. Çözümlenmemiş adlar çalışma zamanında yok sayılır.
- `historyLimit`: grup geçmiş bağlamı olarak dahil edilecek en fazla oda iletisi sayısı. `messages.groupChat.historyLimit` değerine geri döner. Devre dışı bırakmak için `0` ayarlayın.
- `replyToMode`: `off`, `first` veya `all`.
- `markdown`: giden Matrix metni için isteğe bağlı Markdown işleme yapılandırması.
- `streaming`: `off` (varsayılan), `partial`, `quiet`, `true` veya `false`. `partial` ve `true`, normal Matrix metin iletileriyle önizleme-öncelikli taslak güncellemelerini etkinleştirir. `quiet`, self-hosted push-kuralı kurulumları için bildirim vermeyen önizleme bildirimlerini kullanır.
- `blockStreaming`: `true`, taslak önizleme akışı etkin olduğunda tamamlanmış asistan blokları için ayrı ilerleme iletilerini etkinleştirir.
- `threadReplies`: `off`, `inbound` veya `always`.
- `threadBindings`: ileti dizisine bağlı oturum yönlendirmesi ve yaşam döngüsü için kanal başına geçersiz kılmalar.
- `startupVerification`: başlangıçta otomatik öz-doğrulama istek modu (`if-unverified`, `off`).
- `startupVerificationCooldownHours`: otomatik başlangıç doğrulama istekleri yeniden denenmeden önce bekleme süresi.
- `textChunkLimit`: giden ileti parça boyutu.
- `chunkMode`: `length` veya `newline`.
- `responsePrefix`: giden yanıtlar için isteğe bağlı ileti öneki.
- `ackReaction`: bu kanal/hesap için isteğe bağlı onay tepkisi geçersiz kılması.
- `ackReactionScope`: isteğe bağlı onay tepkisi kapsamı geçersiz kılması (`group-mentions`, `group-all`, `direct`, `all`, `none`, `off`).
- `reactionNotifications`: gelen tepki bildirim modu (`own`, `off`).
- `mediaMaxMb`: Matrix medya işleme için MB cinsinden medya boyut sınırı. Giden gönderimlere ve gelen medya işlemeye uygulanır.
- `autoJoin`: davete otomatik katılma politikası (`always`, `allowlist`, `off`). Varsayılan: `off`.
- `autoJoinAllowlist`: `autoJoin` değeri `allowlist` olduğunda izin verilen odalar/takma adlar. Takma ad girdileri davet işleme sırasında oda kimliklerine çözülür; OpenClaw davet edilen oda tarafından iddia edilen takma ad durumuna güvenmez.
- `dm`: DM politika bloğu (`enabled`, `policy`, `allowFrom`, `sessionScope`, `threadReplies`).
- `dm.allowFrom` girdileri, onları canlı dizin aramasıyla zaten çözümlemediyseniz tam Matrix kullanıcı kimlikleri olmalıdır.
- `dm.sessionScope`: `per-user` (varsayılan) veya `per-room`. Aynı eş olsa bile her Matrix DM odasının ayrı bağlam tutmasını istiyorsanız `per-room` kullanın.
- `dm.threadReplies`: yalnızca DM için ileti dizisi politikası geçersiz kılması (`off`, `inbound`, `always`). Hem yanıt yerleşimi hem de DM'lerde oturum yalıtımı için üst düzey `threadReplies` ayarını geçersiz kılar.
- `execApprovals`: Matrix yerel exec onay teslimi (`enabled`, `approvers`, `target`, `agentFilter`, `sessionFilter`).
- `execApprovals.approvers`: exec isteklerini onaylamasına izin verilen Matrix kullanıcı kimlikleri. `dm.allowFrom` zaten onaylayıcıları belirliyorsa isteğe bağlıdır.
- `execApprovals.target`: `dm | channel | both` (varsayılan: `dm`).
- `accounts`: adlandırılmış hesap başına geçersiz kılmalar. Üst düzey `channels.matrix` değerleri bu girdiler için varsayılan görevi görür.
- `groups`: oda başına politika eşlemesi. Oda kimliklerini veya takma adları tercih edin; çözümlenmemiş oda adları çalışma zamanında yok sayılır. Çözümleme sonrası oturum/grup kimliği kararlı oda kimliğini kullanırken, insan tarafından okunabilir etiketler yine oda adlarından gelir.
- `groups.<room>.account`: çoklu hesap kurulumlarında bir devralınan oda girdisini belirli bir Matrix hesabıyla sınırlar.
- `groups.<room>.allowBots`: yapılandırılmış bot gönderenleri için oda düzeyi geçersiz kılma (`true` veya `"mentions"`).
- `groups.<room>.users`: oda başına gönderen allowlist'i.
- `groups.<room>.tools`: oda başına araç izin/verme veya reddetme geçersiz kılmaları.
- `groups.<room>.autoReply`: oda düzeyi mention kapılama geçersiz kılması. `true`, o oda için mention gereksinimlerini devre dışı bırakır; `false` bunları yeniden zorlar.
- `groups.<room>.skills`: isteğe bağlı oda düzeyi skill filtresi.
- `groups.<room>.systemPrompt`: isteğe bağlı oda düzeyi system prompt parçası.
- `rooms`: `groups` için eski takma ad.
- `actions`: eylem başına araç kapılama (`messages`, `reactions`, `pins`, `profile`, `memberInfo`, `channelInfo`, `verification`).

## İlgili

- [Channels Overview](/tr/channels) — desteklenen tüm kanallar
- [Pairing](/tr/channels/pairing) — DM kimlik doğrulaması ve eşleştirme akışı
- [Groups](/tr/channels/groups) — grup sohbeti davranışı ve mention kapılama
- [Channel Routing](/tr/channels/channel-routing) — iletiler için oturum yönlendirmesi
- [Security](/tr/gateway/security) — erişim modeli ve sağlamlaştırma
