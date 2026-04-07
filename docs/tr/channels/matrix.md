---
read_when:
    - OpenClaw içinde Matrix kurulumu
    - Matrix E2EE ve doğrulamayı yapılandırma
summary: Matrix destek durumu, kurulum ve yapılandırma örnekleri
title: Matrix
x-i18n:
    generated_at: "2026-04-07T08:46:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: d53baa2ea5916cd00a99cae0ded3be41ffa13c9a69e8ea8461eb7baa6a99e13c
    source_path: channels/matrix.md
    workflow: 15
---

# Matrix

Matrix, OpenClaw için paketlenmiş Matrix kanal eklentisidir.
Resmi `matrix-js-sdk` kullanır ve DM'leri, odaları, iş parçacıklarını, medyayı, tepkileri, anketleri, konumu ve E2EE'yi destekler.

## Paketlenmiş eklenti

Matrix, güncel OpenClaw sürümlerinde paketlenmiş bir eklenti olarak gelir, bu nedenle normal
paketlenmiş derlemelerde ayrı bir kurulum gerekmez.

Eski bir derlemdesiniz ya da Matrix'i hariç tutan özel bir kurulum kullanıyorsanız,
elle kurun:

npm'den kurun:

```bash
openclaw plugins install @openclaw/matrix
```

Yerel bir checkout'tan kurun:

```bash
openclaw plugins install ./path/to/local/matrix-plugin
```

Eklenti davranışı ve kurulum kuralları için [Plugins](/tr/tools/plugin) bölümüne bakın.

## Kurulum

1. Matrix eklentisinin kullanılabilir olduğundan emin olun.
   - Güncel paketlenmiş OpenClaw sürümleri bunu zaten paketlenmiş olarak içerir.
   - Eski/özel kurulumlar bunu yukarıdaki komutlarla elle ekleyebilir.
2. Homeserver'ınızda bir Matrix hesabı oluşturun.
3. `channels.matrix` yapılandırmasını şu seçeneklerden biriyle yapın:
   - `homeserver` + `accessToken`, veya
   - `homeserver` + `userId` + `password`.
4. Gateway'i yeniden başlatın.
5. Botla bir DM başlatın veya onu bir odaya davet edin.
   - Yeni Matrix davetleri yalnızca `channels.matrix.autoJoin` buna izin verdiğinde çalışır.

Etkileşimli kurulum yolları:

```bash
openclaw channels add
openclaw configure --section channels
```

Matrix sihirbazının gerçekte sorduğu şeyler:

- homeserver URL'si
- kimlik doğrulama yöntemi: access token veya parola
- yalnızca parola ile kimlik doğrulama seçtiğinizde kullanıcı kimliği
- isteğe bağlı cihaz adı
- E2EE etkinleştirilip etkinleştirilmeyeceği
- Matrix oda erişiminin şimdi yapılandırılıp yapılandırılmayacağı
- Matrix davet otomatik katılımının şimdi yapılandırılıp yapılandırılmayacağı
- davet otomatik katılımı etkinleştirildiğinde bunun `allowlist`, `always` veya `off` olup olmayacağı

Önemli sihirbaz davranışları:

- Seçilen hesap için Matrix kimlik doğrulama env değişkenleri zaten varsa ve bu hesabın kimlik doğrulaması yapılandırmada zaten kaydedilmemişse, sihirbaz bir env kısayolu sunar; böylece kurulum, sırları yapılandırmaya kopyalamak yerine kimlik doğrulamayı env değişkenlerinde tutabilir.
- Etkileşimli olarak başka bir Matrix hesabı eklediğinizde, girilen hesap adı yapılandırma ve env değişkenlerinde kullanılan hesap kimliğine normalize edilir. Örneğin, `Ops Bot`, `ops-bot` olur.
- DM allowlist istemleri tam `@user:server` değerlerini hemen kabul eder. Görünen adlar yalnızca canlı dizin araması tam olarak tek bir eşleşme bulduğunda çalışır; aksi halde sihirbaz sizden tam bir Matrix kimliğiyle yeniden denemenizi ister.
- Oda allowlist istemleri oda kimliklerini ve takma adları doğrudan kabul eder. Ayrıca katılınmış oda adlarını canlı olarak çözümleyebilir, ancak çözümlenmeyen adlar yalnızca kurulum sırasında yazıldığı gibi tutulur ve daha sonra çalışma zamanı allowlist çözümlemesi tarafından yok sayılır. `!room:server` veya `#alias:server` tercih edin.
- Sihirbaz artık davet otomatik katılımı adımından önce açık bir uyarı gösterir çünkü `channels.matrix.autoJoin` varsayılan olarak `off` değerindedir; siz ayarlamazsanız ajanlar davet edilen odalara veya yeni DM tarzı davetlere katılmaz.
- Davet otomatik katılımı allowlist modunda yalnızca kararlı davet hedeflerini kullanın: `!roomId:server`, `#alias:server` veya `*`. Düz oda adları reddedilir.
- Çalışma zamanı oda/oturum kimliği kararlı Matrix oda kimliğini kullanır. Oda tarafından bildirilen takma adlar yalnızca arama girdileri olarak kullanılır; uzun vadeli oturum anahtarı veya kararlı grup kimliği olarak kullanılmaz.
- Oda adlarını kaydetmeden önce çözümlemek için `openclaw channels resolve --channel matrix "Project Room"` komutunu kullanın.

<Warning>
`channels.matrix.autoJoin` varsayılan olarak `off` değerindedir.

Bunu ayarlamazsanız bot davet edilen odalara veya yeni DM tarzı davetlere katılmaz; bu nedenle siz önce elle katılmazsanız yeni gruplarda veya davet edilen DM'lerde görünmez.

Hangi davetleri kabul edeceğini kısıtlamak için `autoJoin: "allowlist"` ile birlikte `autoJoinAllowlist` ayarlayın ya da her davete katılmasını istiyorsanız `autoJoin: "always"` ayarlayın.

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

En az token tabanlı kurulum:

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
Önbelleğe alınmış kimlik bilgileri burada varsa, geçerli kimlik doğrulama doğrudan yapılandırmada ayarlanmamış olsa bile OpenClaw, kurulum, doctor ve kanal durum keşfi için Matrix'i yapılandırılmış olarak kabul eder.

Ortam değişkeni karşılıkları (yapılandırma anahtarı ayarlanmadığında kullanılır):

- `MATRIX_HOMESERVER`
- `MATRIX_ACCESS_TOKEN`
- `MATRIX_USER_ID`
- `MATRIX_PASSWORD`
- `MATRIX_DEVICE_ID`
- `MATRIX_DEVICE_NAME`

Varsayılan olmayan hesaplar için hesap kapsamlı env değişkenlerini kullanın:

- `MATRIX_<ACCOUNT_ID>_HOMESERVER`
- `MATRIX_<ACCOUNT_ID>_ACCESS_TOKEN`
- `MATRIX_<ACCOUNT_ID>_USER_ID`
- `MATRIX_<ACCOUNT_ID>_PASSWORD`
- `MATRIX_<ACCOUNT_ID>_DEVICE_ID`
- `MATRIX_<ACCOUNT_ID>_DEVICE_NAME`

`ops` hesabı için örnek:

- `MATRIX_OPS_HOMESERVER`
- `MATRIX_OPS_ACCESS_TOKEN`

Normalize edilmiş hesap kimliği `ops-bot` için şunları kullanın:

- `MATRIX_OPS_X2D_BOT_HOMESERVER`
- `MATRIX_OPS_X2D_BOT_ACCESS_TOKEN`

Matrix, hesap kimliklerindeki noktalama işaretlerini kaçışlayarak hesap kapsamlı env değişkenlerinde çakışmaları önler.
Örneğin, `-`, `_X2D_` olur; böylece `ops-prod`, `MATRIX_OPS_X2D_PROD_*` ile eşleşir.

Etkileşimli sihirbaz env değişkeni kısayolunu yalnızca bu kimlik doğrulama env değişkenleri zaten mevcutsa ve seçilen hesapta Matrix kimlik doğrulaması zaten yapılandırmada kayıtlı değilse sunar.

## Yapılandırma örneği

Bu, DM eşleştirme, oda allowlist ve E2EE etkinleştirilmiş pratik bir temel yapılandırmadır:

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
Buna yeni DM tarzı davetler de dahildir. Davet anında OpenClaw, davet edilen odanın sonunda
DM mi yoksa grup mu olarak ele alınacağını güvenilir biçimde bilemez; bu nedenle tüm davetler önce aynı
`autoJoin` kararından geçer. `dm.policy`, bot odaya katıldıktan ve oda
DM olarak sınıflandırıldıktan sonra yine uygulanır; yani `autoJoin` katılma davranışını kontrol ederken `dm.policy` yanıt/erişim
davranışını kontrol eder.

## Akış önizlemeleri

Matrix yanıt akışı isteğe bağlıdır.

OpenClaw'ın tek bir canlı önizleme yanıtı göndermesini, model metin üretirken
bu önizlemeyi yerinde düzenlemesini ve sonra yanıt tamamlandığında sonlandırmasını istiyorsanız
`channels.matrix.streaming` değerini `"partial"` olarak ayarlayın:

```json5
{
  channels: {
    matrix: {
      streaming: "partial",
    },
  },
}
```

- `streaming: "off"` varsayılandır. OpenClaw son yanıtı bekler ve bir kez gönderir.
- `streaming: "partial"` geçerli yardımcı blok için normal Matrix metin mesajlarını kullanarak düzenlenebilir bir önizleme mesajı oluşturur. Bu, Matrix'in eski önizleme-önce bildirim davranışını korur; bu nedenle standart istemciler tamamlanan blok yerine ilk akış önizleme metni için bildirim gönderebilir.
- `streaming: "quiet"` geçerli yardımcı blok için düzenlenebilir sessiz bir önizleme bildirimi oluşturur. Bunu yalnızca tamamlanan önizleme düzenlemeleri için alıcı push kuralları da yapılandırdığınızda kullanın.
- `blockStreaming: true` ayrı Matrix ilerleme mesajlarını etkinleştirir. Önizleme akışı etkinken Matrix geçerli blok için canlı taslağı korur ve tamamlanan blokları ayrı mesajlar olarak saklar.
- Önizleme akışı açıksa ve `blockStreaming` kapalıysa Matrix canlı taslağı yerinde düzenler ve blok veya dönüş bittiğinde aynı olayı sonlandırır.
- Önizleme artık tek bir Matrix olayına sığmazsa OpenClaw önizleme akışını durdurur ve normal son teslimata geri döner.
- Medya yanıtları ekleri normal şekilde göndermeye devam eder. Eski bir önizleme artık güvenle yeniden kullanılamıyorsa OpenClaw son medya yanıtını göndermeden önce onu redakte eder.
- Önizleme düzenlemeleri ek Matrix API çağrıları gerektirir. En muhafazakâr oran sınırlama davranışını istiyorsanız akışı kapalı bırakın.

`blockStreaming` tek başına taslak önizlemeleri etkinleştirmez.
Önizleme düzenlemeleri için `streaming: "partial"` veya `streaming: "quiet"` kullanın; ardından tamamlanan yardımcı blokların ayrı ilerleme mesajları olarak görünmesini de istiyorsanız `blockStreaming: true` ekleyin.

Özel push kuralları olmadan standart Matrix bildirimlerine ihtiyacınız varsa, önizleme-önce davranışı için `streaming: "partial"` kullanın veya yalnızca son teslimat için `streaming` değerini kapalı bırakın. `streaming: "off"` olduğunda:

- `blockStreaming: true` her tamamlanan bloğu normal bildirim veren bir Matrix mesajı olarak gönderir.
- `blockStreaming: false` yalnızca son tamamlanmış yanıtı normal bildirim veren bir Matrix mesajı olarak gönderir.

### Sessiz tamamlanmış önizlemeler için self-hosted push kuralları

Kendi Matrix altyapınızı çalıştırıyorsanız ve sessiz önizlemelerin yalnızca bir blok veya
son yanıt tamamlandığında bildirim vermesini istiyorsanız, `streaming: "quiet"` ayarlayın ve tamamlanmış önizleme düzenlemeleri için kullanıcı başına bir push kuralı ekleyin.

Bu genellikle homeserver genelinde bir yapılandırma değişikliği değil, alıcı kullanıcı kurulumu olur:

Başlamadan önce hızlı harita:

- alıcı kullanıcı = bildirimi alması gereken kişi
- bot kullanıcı = yanıtı gönderen OpenClaw Matrix hesabı
- aşağıdaki API çağrıları için alıcı kullanıcının access token'ını kullanın
- push kuralındaki `sender` alanını bot kullanıcının tam MXID'siyle eşleştirin

1. OpenClaw'ı sessiz önizlemeler kullanacak şekilde yapılandırın:

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
   kuralları yalnızca bu kullanıcı zaten çalışan pusher'lara/cihazlara sahipse çalışır.

3. Alıcı kullanıcının access token'ını alın.
   - Botun token'ını değil, mesajı alan kullanıcının token'ını kullanın.
   - Mevcut bir istemci oturum token'ını yeniden kullanmak genellikle en kolay yoldur.
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

Bu çağrı etkin pusher/cihaz döndürmüyorsa, aşağıdaki
OpenClaw kuralını eklemeden önce önce normal Matrix bildirimlerini düzeltin.

OpenClaw, yalnızca metin içeren tamamlanmış önizleme düzenlemelerini şu şekilde işaretler:

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
- `$USER_ACCESS_TOKEN`: mesajı alan kullanıcının access token'ı
- `openclaw-finalized-preview-botname`: bu bot için bu kullanıcıya özgü benzersiz bir kural kimliği
- `@bot:example.org`: mesajı alan kullanıcının MXID'si değil, OpenClaw Matrix bot MXID'niz

Çok botlu kurulumlar için önemli:

- Push kuralları `ruleId` ile anahtarlanır. Aynı kural kimliğine karşı `PUT` komutunu yeniden çalıştırmak o tek kuralı günceller.
- Bir kullanıcı birden çok OpenClaw Matrix bot hesabı için bildirim alacaksa, her gönderici eşleşmesi için benzersiz kural kimlikli birer kural oluşturun.
- Basit bir desen `openclaw-finalized-preview-<botname>` biçimidir; örneğin `openclaw-finalized-preview-ops` veya `openclaw-finalized-preview-support`.

Kural olay göndericisine göre değerlendirilir:

- mesajı alan kullanıcının token'ı ile kimlik doğrulayın
- `sender` alanını OpenClaw bot MXID'siyle eşleştirin

6. Kuralın var olduğunu doğrulayın:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

7. Akışlı bir yanıtı test edin. Sessiz modda odada sessiz bir taslak önizleme görünmeli ve son
   yerinde düzenleme blok veya dönüş tamamlandığında bir kez bildirim vermelidir.

Kuralı daha sonra kaldırmanız gerekirse, mesajı alan kullanıcının token'ı ile aynı kural kimliğini silin:

```bash
curl -sS -X DELETE \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

Notlar:

- Kuralı botun access token'ı ile değil, mesajı alan kullanıcının access token'ı ile oluşturun.
- Yeni kullanıcı tanımlı `override` kuralları varsayılan bastırma kurallarının önüne eklenir; bu nedenle ek bir sıralama parametresi gerekmez.
- Bu yalnızca OpenClaw'ın yerinde güvenle sonlandırabildiği yalnızca metin içeren önizleme düzenlemelerini etkiler. Medya geri dönüşleri ve eski önizleme geri dönüşleri yine normal Matrix teslimatını kullanır.
- `GET /_matrix/client/v3/pushers` hiç pusher göstermiyorsa, kullanıcının bu hesap/cihaz için çalışan Matrix push teslimatı henüz yoktur.

#### Synapse

Synapse için yukarıdaki kurulum genellikle tek başına yeterlidir:

- Tamamlanmış OpenClaw önizleme bildirimleri için özel bir `homeserver.yaml` değişikliği gerekmez.
- Synapse dağıtımınız zaten normal Matrix push bildirimleri gönderiyorsa, yukarıdaki kullanıcı token'ı + `pushrules` çağrısı temel kurulum adımıdır.
- Synapse'i ters proxy veya worker'lar arkasında çalıştırıyorsanız `/_matrix/client/.../pushrules/` isteğinin doğru şekilde Synapse'e ulaştığından emin olun.
- Synapse worker'ları kullanıyorsanız pusher'ların sağlıklı olduğundan emin olun. Push teslimatı ana süreç veya `synapse.app.pusher` / yapılandırılmış pusher worker'ları tarafından ele alınır.

#### Tuwunel

Tuwunel için yukarıda gösterilen aynı kurulum akışını ve push-rule API çağrısını kullanın:

- Tamamlanmış önizleme işaretleyicisinin kendisi için Tuwunel'e özgü bir yapılandırma gerekmez.
- Normal Matrix bildirimleri bu kullanıcı için zaten çalışıyorsa, yukarıdaki kullanıcı token'ı + `pushrules` çağrısı temel kurulum adımıdır.
- Bildirimler kullanıcı başka bir cihazda etkin olduğunda kayboluyor gibi görünüyorsa `suppress_push_when_active` ayarının etkin olup olmadığını kontrol edin. Tuwunel bu seçeneği 12 Eylül 2025 tarihinde Tuwunel 1.4.2 sürümünde ekledi ve bu seçenek bir cihaz etkin olduğunda diğer cihazlara giden push'ları kasıtlı olarak bastırabilir.

## Şifreleme ve doğrulama

Şifreli (E2EE) odalarda giden görüntü olayları `thumbnail_file` kullanır; böylece görüntü önizlemeleri tam ek ile birlikte şifrelenir. Şifrelenmemiş odalar yine düz `thumbnail_url` kullanır. Yapılandırma gerekmez — eklenti E2EE durumunu otomatik olarak algılar.

### Botlar arası odalar

Varsayılan olarak, yapılandırılmış diğer OpenClaw Matrix hesaplarından gelen Matrix mesajları yok sayılır.

Ajanlar arası Matrix trafiğini bilerek istiyorsanız `allowBots` kullanın:

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

- `allowBots: true`, izin verilen odalarda ve DM'lerde yapılandırılmış diğer Matrix bot hesaplarından gelen mesajları kabul eder.
- `allowBots: "mentions"`, bu mesajları odalarda yalnızca görünür şekilde bu bottan bahsettiklerinde kabul eder. DM'lere yine izin verilir.
- `groups.<room>.allowBots`, hesap düzeyindeki ayarı tek bir oda için geçersiz kılar.
- OpenClaw, kendi kendine yanıt döngülerini önlemek için yine aynı Matrix kullanıcı kimliğinden gelen mesajları yok sayar.
- Matrix burada yerleşik bir bot işareti sunmaz; OpenClaw "bot tarafından yazılmış" ifadesini "bu OpenClaw gateway üzerinde yapılandırılmış başka bir Matrix hesabı tarafından gönderilmiş" olarak kabul eder.

Paylaşılan odalarda botlar arası trafiği etkinleştirirken katı oda allowlist'leri ve mention gereksinimleri kullanın.

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

Makine tarafından okunabilir çıktıya saklanan kurtarma anahtarını da ekleyin:

```bash
openclaw matrix verify status --include-recovery-key --json
```

Cross-signing ve doğrulama durumunu bootstrap edin:

```bash
openclaw matrix verify bootstrap
```

Çoklu hesap desteği: hesap başına kimlik bilgileri ve isteğe bağlı `name` için `channels.matrix.accounts` kullanın. Ortak desen için [Configuration reference](/tr/gateway/configuration-reference#multi-account-all-channels) bölümüne bakın.

Ayrıntılı bootstrap tanılaması:

```bash
openclaw matrix verify bootstrap --verbose
```

Bootstrap işleminden önce yeni bir cross-signing kimliğini zorla sıfırlayın:

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

Oda anahtarı yedeği sağlığını kontrol edin:

```bash
openclaw matrix verify backup status
```

Ayrıntılı yedek sağlık tanılaması:

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

Geçerli sunucu yedeğini silin ve yeni bir yedek temel durumu oluşturun. Saklanan
yedek anahtarı temiz biçimde yüklenemiyorsa, bu sıfırlama gizli depolamayı da yeniden oluşturarak
gelecekteki soğuk başlangıçların yeni yedek anahtarını yükleyebilmesini sağlayabilir:

```bash
openclaw matrix verify backup reset --yes
```

Tüm `verify` komutları varsayılan olarak kısa tutulur (sessiz iç SDK günlüklemesi dahil) ve ayrıntılı tanılamayı yalnızca `--verbose` ile gösterir.
Betik yazarken tam makine tarafından okunabilir çıktı için `--json` kullanın.

Çoklu hesap kurulumlarında Matrix CLI komutları, siz `--account <id>` verene kadar örtük Matrix varsayılan hesabını kullanır.
Birden çok adlandırılmış hesap yapılandırırsanız, örtük CLI işlemleri durup sizden açıkça bir hesap seçmenizi istemeden önce `channels.matrix.defaultAccount` ayarlayın.
Doğrulama veya cihaz işlemlerinin açıkça adlandırılmış bir hesabı hedeflemesini istediğinizde `--account` kullanın:

```bash
openclaw matrix verify status --account assistant
openclaw matrix verify backup restore --account assistant
openclaw matrix devices list --account assistant
```

Şifreleme devre dışıysa veya adlandırılmış bir hesap için kullanılamıyorsa Matrix uyarıları ve doğrulama hataları o hesabın yapılandırma anahtarını işaret eder; örneğin `channels.matrix.accounts.assistant.encryption`.

### "Doğrulanmış" ne demek

OpenClaw bu Matrix cihazını yalnızca kendi cross-signing kimliğiniz tarafından doğrulandığında doğrulanmış kabul eder.
Pratikte, `openclaw matrix verify status --verbose` üç güven sinyalini açığa çıkarır:

- `Locally trusted`: bu cihaz yalnızca geçerli istemci tarafından güvenilir kabul edilir
- `Cross-signing verified`: SDK bu cihazın cross-signing ile doğrulandığını bildirir
- `Signed by owner`: cihaz sizin kendi self-signing anahtarınız tarafından imzalanmıştır

`Verified by owner`, yalnızca cross-signing doğrulaması veya owner-signing mevcut olduğunda `yes` olur.
Yalnızca yerel güven, OpenClaw'ın cihazı tam doğrulanmış kabul etmesi için yeterli değildir.

### Bootstrap ne yapar

`openclaw matrix verify bootstrap`, şifreli Matrix hesapları için onarım ve kurulum komutudur.
Sırayla şunların hepsini yapar:

- mümkün olduğunda mevcut kurtarma anahtarını yeniden kullanarak gizli depolamayı bootstrap eder
- cross-signing'i bootstrap eder ve eksik genel cross-signing anahtarlarını yükler
- geçerli cihazı işaretlemeye ve cross-sign etmeye çalışır
- henüz yoksa yeni bir sunucu tarafı oda-anahtarı yedeği oluşturur

Homeserver, cross-signing anahtarlarını yüklemek için etkileşimli kimlik doğrulama gerektiriyorsa OpenClaw yüklemeyi önce kimlik doğrulamasız, ardından `m.login.dummy` ile ve `channels.matrix.password` yapılandırılmışsa sonra `m.login.password` ile dener.

`--force-reset-cross-signing` seçeneğini yalnızca mevcut cross-signing kimliğini atmak ve yeni bir tane oluşturmak istediğinizde kullanın.

Mevcut oda-anahtarı yedeğini bilerek atmak ve gelecekteki mesajlar için yeni
bir yedek temel durumu başlatmak istiyorsanız `openclaw matrix verify backup reset --yes` kullanın.
Bunu yalnızca kurtarılamayan eski şifreli geçmişin erişilemez kalacağını ve
OpenClaw'ın mevcut yedek sırrı güvenle yüklenemiyorsa gizli depolamayı yeniden oluşturabileceğini kabul ettiğinizde yapın.

### Yeni yedek temel durumu

Gelecekteki şifreli mesajların çalışmasını sürdürmek ve kurtarılamayan eski geçmişi kaybetmeyi kabul etmek istiyorsanız şu komutları sırayla çalıştırın:

```bash
openclaw matrix verify backup reset --yes
openclaw matrix verify backup status --verbose
openclaw matrix verify status
```

Adlandırılmış bir Matrix hesabını açıkça hedeflemek istediğinizde her komuta `--account <id>` ekleyin.

### Başlangıç davranışı

`encryption: true` olduğunda Matrix varsayılan olarak `startupVerification` değerini `"if-unverified"` yapar.
Başlangıçta bu cihaz hâlâ doğrulanmamışsa Matrix başka bir Matrix istemcisinde self-verification isteyecek,
biri zaten beklemedeyken yinelenen istekleri atlayacak ve yeniden başlatmalardan sonra tekrar denemeden önce yerel bir bekleme süresi uygulayacaktır.
Başarısız istek denemeleri varsayılan olarak başarılı istek oluşturmalardan daha kısa sürede yeniden denenir.
Otomatik başlangıç isteklerini devre dışı bırakmak için `startupVerification: "off"` ayarlayın veya daha kısa ya da daha uzun yeniden deneme penceresi istiyorsanız `startupVerificationCooldownHours` değerini ayarlayın.

Başlangıç ayrıca otomatik olarak muhafazakâr bir kripto bootstrap geçişi gerçekleştirir.
Bu geçiş önce mevcut gizli depolamayı ve cross-signing kimliğini yeniden kullanmaya çalışır ve siz açık bir bootstrap onarım akışı çalıştırmadıkça cross-signing'i sıfırlamaktan kaçınır.

Başlangıç bozuk bootstrap durumu bulursa ve `channels.matrix.password` yapılandırılmışsa, OpenClaw daha katı bir onarım yolu deneyebilir.
Geçerli cihaz zaten owner-signed ise OpenClaw bu kimliği otomatik olarak sıfırlamak yerine korur.

Önceki herkese açık Matrix eklentisinden yükseltme:

- OpenClaw mümkün olduğunda aynı Matrix hesabını, access token'ı ve cihaz kimliğini otomatik olarak yeniden kullanır.
- Eyleme geçirilebilir herhangi bir Matrix geçiş değişikliği çalıştırılmadan önce OpenClaw, `~/Backups/openclaw-migrations/` altında bir kurtarma anlık görüntüsü oluşturur veya yeniden kullanır.
- Birden çok Matrix hesabı kullanıyorsanız, eski düz-depo düzeninden yükseltmeden önce `channels.matrix.defaultAccount` ayarlayın; böylece OpenClaw bu paylaşılan eski durumun hangi hesaba verilmesi gerektiğini bilir.
- Önceki eklenti bir Matrix oda-anahtarı yedeği çözme anahtarını yerel olarak sakladıysa, başlangıç veya `openclaw doctor --fix` bunu otomatik olarak yeni kurtarma anahtarı akışına içe aktarır.
- Matrix access token'ı geçiş hazırlandıktan sonra değiştiyse, başlangıç artık otomatik yedek geri yüklemesinden vazgeçmeden önce bekleyen eski geri yükleme durumu için kardeş token-hash depolama köklerini tarar.
- Matrix access token'ı daha sonra aynı hesap, homeserver ve kullanıcı için değişirse OpenClaw artık boş bir Matrix durum dizininden başlamak yerine en eksiksiz mevcut token-hash depolama kökünü yeniden kullanmayı tercih eder.
- Sonraki gateway başlangıcında, yedeklenen oda anahtarları otomatik olarak yeni kripto deposuna geri yüklenir.
- Eski eklentide hiç yedeklenmemiş yalnızca yerel oda anahtarları varsa OpenClaw bunu açık biçimde uyarır. Bu anahtarlar önceki rust kripto deposundan otomatik olarak dışa aktarılamaz; bu nedenle bazı eski şifreli geçmişler elle kurtarılana kadar erişilemez kalabilir.
- Tam yükseltme akışı, sınırlar, kurtarma komutları ve yaygın geçiş mesajları için [Matrix migration](/tr/install/migrating-matrix) bölümüne bakın.

Şifreli çalışma zamanı durumu, hesap başına, kullanıcı başına token-hash kökleri altında
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/` dizininde düzenlenir.
Bu dizin eşitleme deposunu (`bot-storage.json`), kripto deposunu (`crypto/`),
kurtarma anahtarı dosyasını (`recovery-key.json`), IndexedDB anlık görüntüsünü (`crypto-idb-snapshot.json`),
iş parçacığı bağlarını (`thread-bindings.json`) ve başlangıç doğrulama durumunu (`startup-verification.json`)
bu özellikler kullanımdayken içerir.
Token değiştiğinde ancak hesap kimliği aynı kaldığında OpenClaw o hesap/homeserver/kullanıcı üçlüsü için
en iyi mevcut kökü yeniden kullanır; böylece önceki eşitleme durumu, kripto durumu, iş parçacığı bağları
ve başlangıç doğrulama durumu görünür kalır.

### Node crypto store modeli

Bu eklentideki Matrix E2EE, Node içinde resmi `matrix-js-sdk` Rust crypto yolunu kullanır.
Bu yol, kripto durumunun yeniden başlatmalar arasında korunmasını istiyorsanız IndexedDB tabanlı kalıcılık bekler.

OpenClaw şu anda Node içinde bunu şu şekilde sağlar:

- SDK'nın beklediği IndexedDB API shim'i olarak `fake-indexeddb` kullanarak
- `initRustCrypto` öncesinde Rust crypto IndexedDB içeriğini `crypto-idb-snapshot.json` dosyasından geri yükleyerek
- init sonrası ve çalışma zamanı sırasında güncellenmiş IndexedDB içeriğini tekrar `crypto-idb-snapshot.json` dosyasına kalıcı yazarak
- gateway çalışma zamanı kalıcılığı ile CLI bakımının aynı anlık görüntü dosyasında yarışmaması için anlık görüntü geri yükleme ve kalıcı yazma işlemlerini `crypto-idb-snapshot.json` üzerinde danışmalı bir dosya kilidiyle serileştirerek

Bu, özel bir kripto uygulaması değil; uyumluluk/depolama altyapısıdır.
Anlık görüntü dosyası hassas çalışma zamanı durumudur ve kısıtlayıcı dosya izinleriyle saklanır.
OpenClaw'ın güvenlik modelinde gateway host ve yerel OpenClaw durum dizini zaten güvenilen operatör sınırı içindedir; bu nedenle bu öncelikle ayrı bir uzak güven sınırı olmaktan çok operasyonel dayanıklılık konusudur.

Planlanan iyileştirme:

- kalıcı Matrix anahtar malzemesi için SecretRef desteği eklemek; böylece kurtarma anahtarları ve ilgili depo-şifreleme sırları yalnızca yerel dosyalardan değil, OpenClaw secrets provider'larından da alınabilsin

## Profil yönetimi

Seçilen hesabın Matrix öz profilini şu komutlarla güncelleyin:

```bash
openclaw matrix profile set --name "OpenClaw Assistant"
openclaw matrix profile set --avatar-url https://cdn.example.org/avatar.png
```

Adlandırılmış bir Matrix hesabını açıkça hedeflemek istediğinizde `--account <id>` ekleyin.

Matrix `mxc://` avatar URL'lerini doğrudan kabul eder. `http://` veya `https://` avatar URL'si verdiğinizde OpenClaw önce bunu Matrix'e yükler ve çözümlenen `mxc://` URL'sini tekrar `channels.matrix.avatarUrl` içine (veya seçilen hesap geçersiz kılmasına) yazar.

## Otomatik doğrulama bildirimleri

Matrix artık doğrulama yaşam döngüsü bildirimlerini doğrudan katı DM doğrulama odasına `m.notice` mesajları olarak gönderir.
Buna şunlar dahildir:

- doğrulama isteği bildirimleri
- doğrulama hazır bildirimleri (açık "Verify by emoji" yönlendirmesiyle)
- doğrulama başlangıç ve tamamlanma bildirimleri
- mevcut olduğunda SAS ayrıntıları (emoji ve ondalık)

Başka bir Matrix istemcisinden gelen doğrulama istekleri OpenClaw tarafından izlenir ve otomatik kabul edilir.
Self-verification akışlarında OpenClaw, emoji doğrulaması kullanılabilir olduğunda SAS akışını da otomatik olarak başlatır ve kendi tarafını onaylar.
Başka bir Matrix kullanıcısı/cihazından gelen doğrulama isteklerinde OpenClaw isteği otomatik kabul eder ve ardından SAS akışının normal şekilde ilerlemesini bekler.
Doğrulamayı tamamlamak için yine de Matrix istemcinizde emoji veya ondalık SAS'ı karşılaştırmanız ve orada "They match" onayı vermeniz gerekir.

OpenClaw, kendi başlattığı yinelenen akışları körü körüne otomatik kabul etmez. Başlangıç, self-verification isteği zaten beklemedeyse yeni bir istek oluşturmayı atlar.

Doğrulama protokolü/sistem bildirimleri ajan sohbet hattına iletilmez; bu nedenle `NO_REPLY` üretmezler.

### Cihaz hijyeni

OpenClaw tarafından yönetilen eski Matrix cihazları hesapta birikebilir ve şifreli oda güvenini anlamayı zorlaştırabilir.
Bunları listelemek için:

```bash
openclaw matrix devices list
```

Eski OpenClaw tarafından yönetilen cihazları kaldırmak için:

```bash
openclaw matrix devices prune-stale
```

### Direct Room Repair

Doğrudan mesaj durumu senkron dışına çıkarsa OpenClaw, canlı DM yerine eski tekil odaları işaret eden bayat `m.direct` eşlemeleriyle karşılaşabilir. Bir eş için geçerli eşlemeyi şu komutla inceleyin:

```bash
openclaw matrix direct inspect --user-id @alice:example.org
```

Şu komutla onarın:

```bash
openclaw matrix direct repair --user-id @alice:example.org
```

Onarım, Matrix'e özgü mantığı eklenti içinde tutar:

- `m.direct` içinde zaten eşlenmiş katı 1:1 DM'yi tercih eder
- aksi halde o kullanıcıyla şu anda katılınmış herhangi bir katı 1:1 DM'ye geri düşer
- sağlıklı bir DM yoksa yeni bir doğrudan oda oluşturur ve `m.direct` eşlemesini buna işaret edecek şekilde yeniden yazar

Onarım akışı eski odaları otomatik olarak silmez. Yalnızca sağlıklı DM'yi seçer ve eşlemeyi günceller; böylece yeni Matrix göndermeleri, doğrulama bildirimleri ve diğer doğrudan mesaj akışları yeniden doğru odayı hedefler.

## İş parçacıkları

Matrix, hem otomatik yanıtlar hem de message-tool gönderimleri için yerel Matrix iş parçacıklarını destekler.

- `dm.sessionScope: "per-user"` (varsayılan), Matrix DM yönlendirmesini gönderen kapsamlı tutar; böylece birden çok DM odası aynı eşe çözülüyorsa tek bir oturumu paylaşabilir.
- `dm.sessionScope: "per-room"`, normal DM kimlik doğrulama ve allowlist denetimlerini kullanmaya devam ederken her Matrix DM odasını kendi oturum anahtarına yalıtır.
- Açık Matrix konuşma bağları yine `dm.sessionScope` üzerinde önceliklidir; bu nedenle bağlanmış odalar ve iş parçacıkları seçilmiş hedef oturumlarını korur.
- `threadReplies: "off"` yanıtları üst düzeyde tutar ve gelen iş parçacıklı mesajları ana oturumda tutar.
- `threadReplies: "inbound"` yalnızca gelen mesaj zaten o iş parçacığındaysa iş parçacığı içinde yanıt verir.
- `threadReplies: "always"` oda yanıtlarını tetikleyici mesajdan köklenen bir iş parçacığında tutar ve bu konuşmayı ilk tetikleyici mesajdan itibaren eşleşen iş parçacığı kapsamlı oturum üzerinden yönlendirir.
- `dm.threadReplies`, yalnızca DM'ler için üst düzey ayarı geçersiz kılar. Örneğin, odalardaki iş parçacıklarını yalıtılmış tutarken DM'leri düz tutabilirsiniz.
- Gelen iş parçacıklı mesajlar, ek ajan bağlamı olarak iş parçacığı kök mesajını içerir.
- Message-tool gönderimleri artık hedef aynı oda veya aynı DM kullanıcı hedefi olduğunda, açık bir `threadId` verilmemişse geçerli Matrix iş parçacığını otomatik devralır.
- Aynı oturumlu DM kullanıcı-hedef yeniden kullanımı yalnızca geçerli oturum meta verileri aynı Matrix hesabındaki aynı DM eşini kanıtladığında devreye girer; aksi halde OpenClaw normal kullanıcı kapsamlı yönlendirmeye geri döner.
- OpenClaw bir Matrix DM odasının aynı paylaşılan Matrix DM oturumunda başka bir DM odasıyla çakıştığını görürse, iş parçacığı bağları etkin olduğunda ve `dm.sessionScope` ipucuyla birlikte o odada tek seferlik bir `m.notice` ile `/focus` kaçış yolunu gönderir.
- Çalışma zamanı iş parçacığı bağları Matrix için desteklenir. `/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age` ve iş parçacığına bağlı `/acp spawn` artık Matrix odalarında ve DM'lerde çalışır.
- Üst düzey Matrix oda/DM `/focus`, `threadBindings.spawnSubagentSessions=true` olduğunda yeni bir Matrix iş parçacığı oluşturur ve bunu hedef oturuma bağlar.
- Var olan bir Matrix iş parçacığı içinde `/focus` veya `/acp spawn --thread here` çalıştırmak bunun yerine mevcut iş parçacığını bağlar.

## ACP konuşma bağları

Matrix odaları, DM'ler ve mevcut Matrix iş parçacıkları sohbet yüzeyini değiştirmeden kalıcı ACP çalışma alanlarına dönüştürülebilir.

Hızlı operatör akışı:

- Kullanmaya devam etmek istediğiniz Matrix DM, oda veya mevcut iş parçacığı içinde `/acp spawn codex --bind here` komutunu çalıştırın.
- Üst düzey bir Matrix DM veya odada geçerli DM/oda sohbet yüzeyi olarak kalır ve gelecekteki mesajlar oluşturulan ACP oturumuna yönlendirilir.
- Var olan bir Matrix iş parçacığı içinde `--bind here`, mevcut iş parçacığını yerinde bağlar.
- `/new` ve `/reset`, aynı bağlı ACP oturumunu yerinde sıfırlar.
- `/acp close`, ACP oturumunu kapatır ve bağı kaldırır.

Notlar:

- `--bind here` alt bir Matrix iş parçacığı oluşturmaz.
- `threadBindings.spawnAcpSessions` yalnızca OpenClaw'ın alt Matrix iş parçacığı oluşturması veya bağlaması gereken `/acp spawn --thread auto|here` için gereklidir.

### İş Parçacığı Bağlama Yapılandırması

Matrix, genel varsayılanları `session.threadBindings` üzerinden devralır ve ayrıca kanal başına geçersiz kılmalar da destekler:

- `threadBindings.enabled`
- `threadBindings.idleHours`
- `threadBindings.maxAgeHours`
- `threadBindings.spawnSubagentSessions`
- `threadBindings.spawnAcpSessions`

Matrix iş parçacığına bağlı spawn bayrakları isteğe bağlıdır:

- Üst düzey `/focus` komutunun yeni Matrix iş parçacıkları oluşturup bağlamasına izin vermek için `threadBindings.spawnSubagentSessions: true` ayarlayın.
- `/acp spawn --thread auto|here` komutunun ACP oturumlarını Matrix iş parçacıklarına bağlamasına izin vermek için `threadBindings.spawnAcpSessions: true` ayarlayın.

## Tepkiler

Matrix giden tepki eylemlerini, gelen tepki bildirimlerini ve gelen ack tepkilerini destekler.

- Giden tepki araçları `channels["matrix"].actions.reactions` ile kapılanır.
- `react`, belirli bir Matrix olayına tepki ekler.
- `reactions`, belirli bir Matrix olayı için geçerli tepki özetini listeler.
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
- Tepki kaldırmaları hâlâ sistem olaylarına sentezlenmez çünkü Matrix bunları bağımsız `m.reaction` kaldırmaları olarak değil, redaksiyonlar olarak yüzeye çıkarır.

## Geçmiş bağlamı

- `channels.matrix.historyLimit`, bir Matrix oda mesajı ajanı tetiklediğinde `InboundHistory` olarak dahil edilen son oda mesajlarının sayısını kontrol eder.
- `messages.groupChat.historyLimit` değerine geri düşer. Her ikisi de ayarlanmamışsa etkin varsayılan `0` olur; bu nedenle mention kapılı oda mesajları arabelleğe alınmaz. Devre dışı bırakmak için `0` ayarlayın.
- Matrix oda geçmişi yalnızca oda içindir. DM'ler normal oturum geçmişini kullanmaya devam eder.
- Matrix oda geçmişi yalnızca pending içindir: OpenClaw henüz yanıtı tetiklememiş oda mesajlarını arabelleğe alır, sonra bir mention veya başka bir tetikleyici geldiğinde bu pencerenin anlık görüntüsünü alır.
- Geçerli tetikleyici mesaj `InboundHistory` içine dahil edilmez; o dönüş için ana gelen gövdede kalır.
- Aynı Matrix olayının yeniden denemeleri, daha yeni oda mesajlarına doğru kaymak yerine özgün geçmiş anlık görüntüsünü yeniden kullanır.

## Bağlam görünürlüğü

Matrix, getirilen yanıt metni, iş parçacığı kökleri ve bekleyen geçmiş gibi ek oda bağlamı için paylaşılan `contextVisibility` denetimini destekler.

- `contextVisibility: "all"` varsayılandır. Ek bağlam alındığı gibi korunur.
- `contextVisibility: "allowlist"`, ek bağlamı etkin oda/kullanıcı allowlist denetimleri tarafından izin verilen göndericilerle sınırlar.
- `contextVisibility: "allowlist_quote"`, `allowlist` gibi davranır ama yine de açık bir alıntılanmış yanıtı korur.

Bu ayar, gelen mesajın kendisinin bir yanıtı tetikleyip tetikleyemeyeceğini değil, ek bağlam görünürlüğünü etkiler.
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

Mention kapılama ve allowlist davranışı için [Groups](/tr/channels/groups) bölümüne bakın.

Matrix DM'leri için eşleştirme örneği:

```bash
openclaw pairing list matrix
openclaw pairing approve matrix <CODE>
```

Onaylanmamış bir Matrix kullanıcısı onaydan önce size mesaj göndermeye devam ederse OpenClaw aynı bekleyen eşleştirme kodunu yeniden kullanır ve yeni bir kod üretmek yerine kısa bir bekleme süresinden sonra yeniden bir hatırlatma yanıtı gönderebilir.

Paylaşılan DM eşleştirme akışı ve depolama düzeni için [Pairing](/tr/channels/pairing) bölümüne bakın.

## Exec onayları

Matrix, bir Matrix hesabı için exec onay istemcisi olarak davranabilir.

- `channels.matrix.execApprovals.enabled`
- `channels.matrix.execApprovals.approvers` (isteğe bağlı; `channels.matrix.dm.allowFrom` değerine geri düşer)
- `channels.matrix.execApprovals.target` (`dm` | `channel` | `both`, varsayılan: `dm`)
- `channels.matrix.execApprovals.agentFilter`
- `channels.matrix.execApprovals.sessionFilter`

Onaylayıcılar `@owner:example.org` gibi Matrix kullanıcı kimlikleri olmalıdır. `enabled` ayarlanmamışsa veya `"auto"` ise ve `execApprovals.approvers` ya da `channels.matrix.dm.allowFrom` içinden en az bir onaylayıcı çözümlenebiliyorsa Matrix yerel exec onaylarını otomatik etkinleştirir. Matrix'i yerel onay istemcisi olarak açıkça devre dışı bırakmak için `enabled: false` ayarlayın. Aksi halde onay istekleri diğer yapılandırılmış onay yollarına veya exec onay geri dönüş politikasına geri düşer.

Yerel Matrix yönlendirmesi bugün yalnızca exec içindir:

- `channels.matrix.execApprovals.*`, yalnızca exec onayları için yerel DM/kanal yönlendirmesini kontrol eder.
- Eklenti onayları hâlâ paylaşılan aynı sohbet `/approve` ve yapılandırılmış herhangi bir `approvals.plugin` iletmesini kullanır.
- Matrix, onaylayıcıları güvenle çıkarabildiğinde eklenti onayı yetkilendirmesi için yine `channels.matrix.dm.allowFrom` değerini kullanabilir, ancak ayrı bir yerel eklenti onayı DM/kanal fanout yolu sunmaz.

Teslim kuralları:

- `target: "dm"` onay istemlerini onaylayıcı DM'lerine gönderir
- `target: "channel"` istemi kaynak Matrix odasına veya DM'ye geri gönderir
- `target: "both"` onaylayıcı DM'lerine ve kaynak Matrix oda veya DM'sine gönderir

Matrix onay istemleri birincil onay mesajına tepki kısayolları ekler:

- `✅` = bir kez izin ver
- `❌` = reddet
- `♾️` = kararın etkin exec politikası tarafından izin verildiği durumlarda her zaman izin ver

Onaylayıcılar o mesajda tepki verebilir veya geri dönüş slash komutlarını kullanabilir: `/approve <id> allow-once`, `/approve <id> allow-always` veya `/approve <id> deny`.

Yalnızca çözümlenmiş onaylayıcılar onaylayabilir veya reddedebilir. Kanal teslimatı komut metnini içerir; bu nedenle `channel` veya `both` seçeneklerini yalnızca güvenilen odalarda etkinleştirin.

Matrix onay istemleri paylaşılan çekirdek onay planlayıcısını yeniden kullanır. Matrix'e özgü yerel yüzey exec onayları için yalnızca taşıma katmanıdır: oda/DM yönlendirmesi ve mesaj gönderme/güncelleme/silme davranışı.

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

Üst düzey `channels.matrix` değerleri, bir hesap bunları geçersiz kılmadıkça adlandırılmış hesaplar için varsayılan olarak davranır.
Devralınan oda girişlerini çoklu hesap kurulumlarında `groups.<room>.account` (veya eski `rooms.<room>.account`) ile tek bir Matrix hesabına kapsamlayabilirsiniz.
`account` içermeyen girişler tüm Matrix hesapları arasında paylaşılmaya devam eder ve `account: "default"` içeren girişler varsayılan hesap doğrudan üst düzey `channels.matrix.*` üzerinde yapılandırıldığında yine çalışır.
Kısmi paylaşılan kimlik doğrulama varsayılanları tek başlarına ayrı örtük bir varsayılan hesap oluşturmaz. OpenClaw, yalnızca bu varsayılan yeni kimlik doğrulamaya sahipse (`homeserver` + `accessToken` veya `homeserver` + `userId` ve `password`) üst düzey `default` hesabını sentezler; adlandırılmış hesaplar kimlik doğrulama daha sonra önbelleğe alınmış kimlik bilgileriyle sağlandığında yine `homeserver` + `userId` üzerinden keşfedilebilir kalabilir.
Matrix zaten tam olarak bir adlandırılmış hesaba sahipse veya `defaultAccount` mevcut bir adlandırılmış hesap anahtarını gösteriyorsa tek hesaplıdan çok hesaplı onarım/kurulum terfisi yeni bir `accounts.default` girişi oluşturmak yerine o hesabı korur. Yalnızca Matrix kimlik doğrulama/bootstrap anahtarları bu terfi ettirilen hesaba taşınır; paylaşılan teslim politikası anahtarları üst düzeyde kalır.
OpenClaw'ın örtük yönlendirme, probe ve CLI işlemleri için bir adlandırılmış Matrix hesabını tercih etmesini istiyorsanız `defaultAccount` ayarlayın.
Birden çok adlandırılmış hesap yapılandırırsanız, örtük hesap seçimine dayanan CLI komutları için `defaultAccount` ayarlayın veya `--account <id>` verin.
Bu örtük seçimi tek bir komut için geçersiz kılmak istediğinizde `openclaw matrix verify ...` ve `openclaw matrix devices ...` komutlarına `--account <id>` geçin.

## Özel/LAN homeserver'lar

Varsayılan olarak OpenClaw, SSRF koruması için özel/iç Matrix homeserver'larını siz
hesap başına açıkça izin vermedikçe engeller.

Homeserver'ınız localhost, bir LAN/Tailscale IP'si veya iç ana makine adı üzerinde çalışıyorsa,
o Matrix hesabı için `network.dangerouslyAllowPrivateNetwork` etkinleştirin:

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
genel açık metin homeserver'lar engellenmeye devam eder. Mümkün olduğunda `https://` tercih edin.

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
OpenClaw aynı proxy ayarını hem çalışma zamanı Matrix trafiği hem de hesap durum probe'ları için kullanır.

## Hedef çözümleme

Matrix, OpenClaw'ın sizden oda veya kullanıcı hedefi istediği her yerde şu hedef biçimlerini kabul eder:

- Kullanıcılar: `@user:server`, `user:@user:server` veya `matrix:user:@user:server`
- Odalar: `!room:server`, `room:!room:server` veya `matrix:room:!room:server`
- Takma adlar: `#alias:server`, `channel:#alias:server` veya `matrix:channel:#alias:server`

Canlı dizin araması oturum açmış Matrix hesabını kullanır:

- Kullanıcı aramaları o homeserver üzerindeki Matrix kullanıcı dizinini sorgular.
- Oda aramaları açık oda kimliklerini ve takma adları doğrudan kabul eder, ardından o hesap için katılınmış oda adlarını aramaya geri düşer.
- Katılınmış oda adı araması best-effort çalışır. Bir oda adı bir kimliğe veya takma ada çözümlenemezse çalışma zamanı allowlist çözümlemesi tarafından yok sayılır.

## Yapılandırma başvurusu

- `enabled`: kanalı etkinleştirir veya devre dışı bırakır.
- `name`: hesap için isteğe bağlı etiket.
- `defaultAccount`: birden çok Matrix hesabı yapılandırıldığında tercih edilen hesap kimliği.
- `homeserver`: homeserver URL'si, örneğin `https://matrix.example.org`.
- `network.dangerouslyAllowPrivateNetwork`: bu Matrix hesabının özel/iç homeserver'lara bağlanmasına izin verir. Homeserver `localhost`, bir LAN/Tailscale IP'si veya `matrix-synapse` gibi iç bir ana makineye çözülüyorsa bunu etkinleştirin.
- `proxy`: Matrix trafiği için isteğe bağlı HTTP(S) proxy URL'si. Adlandırılmış hesaplar üst düzey varsayılanı kendi `proxy` değerleriyle geçersiz kılabilir.
- `userId`: tam Matrix kullanıcı kimliği, örneğin `@bot:example.org`.
- `accessToken`: token tabanlı kimlik doğrulama için access token. `channels.matrix.accessToken` ve `channels.matrix.accounts.<id>.accessToken` için env/file/exec provider'ları genelinde düz metin değerler ve SecretRef değerleri desteklenir. Bkz. [Secrets Management](/tr/gateway/secrets).
- `password`: parola tabanlı giriş için parola. Düz metin değerler ve SecretRef değerleri desteklenir.
- `deviceId`: açık Matrix cihaz kimliği.
- `deviceName`: parola ile giriş için cihaz görünen adı.
- `avatarUrl`: profil eşitlemesi ve `set-profile` güncellemeleri için saklanan öz avatar URL'si.
- `initialSyncLimit`: başlangıç eşitleme olay sınırı.
- `encryption`: E2EE'yi etkinleştirir.
- `allowlistOnly`: DM'ler ve odalar için yalnızca allowlist davranışını zorlar.
- `allowBots`: yapılandırılmış diğer OpenClaw Matrix hesaplarından gelen mesajlara izin verir (`true` veya `"mentions"`).
- `groupPolicy`: `open`, `allowlist` veya `disabled`.
- `contextVisibility`: ek oda bağlamı görünürlük modu (`all`, `allowlist`, `allowlist_quote`).
- `groupAllowFrom`: oda trafiği için kullanıcı kimliği allowlist'i.
- `groupAllowFrom` girişleri tam Matrix kullanıcı kimlikleri olmalıdır. Çözümlenmemiş adlar çalışma zamanında yok sayılır.
- `historyLimit`: grup geçmiş bağlamı olarak dahil edilecek en fazla oda mesajı sayısı. `messages.groupChat.historyLimit` değerine geri düşer; her ikisi de ayarlanmamışsa etkin varsayılan `0` olur. Devre dışı bırakmak için `0` ayarlayın.
- `replyToMode`: `off`, `first`, `all` veya `batched`.
- `markdown`: giden Matrix metni için isteğe bağlı Markdown işleme yapılandırması.
- `streaming`: `off` (varsayılan), `partial`, `quiet`, `true` veya `false`. `partial` ve `true`, normal Matrix metin mesajlarıyla önizleme-önce taslak güncellemelerini etkinleştirir. `quiet`, self-hosted push-rule kurulumları için bildirim vermeyen önizleme bildirimleri kullanır.
- `blockStreaming`: `true`, taslak önizleme akışı etkinken tamamlanan yardımcı bloklar için ayrı ilerleme mesajlarını etkinleştirir.
- `threadReplies`: `off`, `inbound` veya `always`.
- `threadBindings`: iş parçacığına bağlı oturum yönlendirmesi ve yaşam döngüsü için kanal başına geçersiz kılmalar.
- `startupVerification`: başlangıçta otomatik self-verification istek modu (`if-unverified`, `off`).
- `startupVerificationCooldownHours`: otomatik başlangıç doğrulama isteklerini yeniden denemeden önce beklenecek süre.
- `textChunkLimit`: giden mesaj parça boyutu.
- `chunkMode`: `length` veya `newline`.
- `responsePrefix`: giden yanıtlar için isteğe bağlı mesaj öneki.
- `ackReaction`: bu kanal/hesap için isteğe bağlı ack tepki geçersiz kılması.
- `ackReactionScope`: isteğe bağlı ack tepki kapsamı geçersiz kılması (`group-mentions`, `group-all`, `direct`, `all`, `none`, `off`).
- `reactionNotifications`: gelen tepki bildirim modu (`own`, `off`).
- `mediaMaxMb`: Matrix medya işleme için MB cinsinden medya boyutu üst sınırı. Giden gönderimler ve gelen medya işleme için geçerlidir.
- `autoJoin`: davet otomatik katılım politikası (`always`, `allowlist`, `off`). Varsayılan: `off`. Bu, yalnızca oda/grup davetleri için değil, DM tarzı davetler dahil genel Matrix davetleri için geçerlidir. OpenClaw bu kararı, katılınan odayı bir DM mi yoksa grup mu olarak güvenilir şekilde sınıflandırabilmeden önce, davet anında verir.
- `autoJoinAllowlist`: `autoJoin` değeri `allowlist` olduğunda izin verilen odalar/takma adlar. Takma ad girişleri davet işleme sırasında oda kimliklerine çözülür; OpenClaw davet edilen odanın iddia ettiği takma ad durumuna güvenmez.
- `dm`: DM politika bloğu (`enabled`, `policy`, `allowFrom`, `sessionScope`, `threadReplies`).
- `dm.policy`: OpenClaw odaya katılıp onu DM olarak sınıflandırdıktan sonra DM erişimini kontrol eder. Bir davetin otomatik katılıp katılmayacağını değiştirmez.
- `dm.allowFrom` girişleri, canlı dizin aramasıyla zaten çözümlemediyseniz tam Matrix kullanıcı kimlikleri olmalıdır.
- `dm.sessionScope`: `per-user` (varsayılan) veya `per-room`. Aynı eş olsa bile her Matrix DM odasının ayrı bağlam tutmasını istiyorsanız `per-room` kullanın.
- `dm.threadReplies`: yalnızca DM'ler için iş parçacığı politikası geçersiz kılması (`off`, `inbound`, `always`). Hem yanıt yerleşimi hem de DM'lerde oturum yalıtımı için üst düzey `threadReplies` ayarını geçersiz kılar.
- `execApprovals`: Matrix yerel exec onay teslimatı (`enabled`, `approvers`, `target`, `agentFilter`, `sessionFilter`).
- `execApprovals.approvers`: exec isteklerini onaylamasına izin verilen Matrix kullanıcı kimlikleri. `dm.allowFrom` zaten onaylayıcıları belirliyorsa isteğe bağlıdır.
- `execApprovals.target`: `dm | channel | both` (varsayılan: `dm`).
- `accounts`: adlandırılmış hesap başına geçersiz kılmalar. Üst düzey `channels.matrix` değerleri bu girişler için varsayılan görevi görür.
- `groups`: oda başına politika haritası. Oda kimlikleri veya takma adları tercih edin; çözümlenmemiş oda adları çalışma zamanında yok sayılır. Oturum/grup kimliği çözümlemeden sonra kararlı oda kimliğini kullanır, insan tarafından okunabilir etiketler ise yine oda adlarından gelir.
- `groups.<room>.account`: çoklu hesap kurulumlarında devralınan tek bir oda girişini belirli bir Matrix hesabıyla sınırlar.
- `groups.<room>.allowBots`: yapılandırılmış bot göndericileri için oda düzeyinde geçersiz kılma (`true` veya `"mentions"`).
- `groups.<room>.users`: oda başına gönderici allowlist'i.
- `groups.<room>.tools`: oda başına araç izin/verme geçersiz kılmaları.
- `groups.<room>.autoReply`: oda düzeyinde mention kapılama geçersiz kılması. `true`, o oda için mention gereksinimlerini devre dışı bırakır; `false` bunları yeniden zorunlu kılar.
- `groups.<room>.skills`: isteğe bağlı oda düzeyinde skill filtresi.
- `groups.<room>.systemPrompt`: isteğe bağlı oda düzeyinde system prompt parçası.
- `rooms`: `groups` için eski takma ad.
- `actions`: eylem başına araç kapılama (`messages`, `reactions`, `pins`, `profile`, `memberInfo`, `channelInfo`, `verification`).

## İlgili

- [Channels Overview](/tr/channels) — tüm desteklenen kanallar
- [Pairing](/tr/channels/pairing) — DM kimlik doğrulaması ve eşleştirme akışı
- [Groups](/tr/channels/groups) — grup sohbeti davranışı ve mention kapılama
- [Channel Routing](/tr/channels/channel-routing) — mesajlar için oturum yönlendirmesi
- [Security](/tr/gateway/security) — erişim modeli ve sertleştirme
