---
read_when:
    - OpenClaw içinde Matrix kurma
    - Matrix E2EE ve doğrulamayı yapılandırma
summary: Matrix destek durumu, kurulum ve yapılandırma örnekleri
title: Matrix
x-i18n:
    generated_at: "2026-04-06T08:51:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: 06f833bf0ede81bad69f140994c32e8cc5d1635764f95fc5db4fc5dc25f2b85e
    source_path: channels/matrix.md
    workflow: 15
---

# Matrix

Matrix, OpenClaw için paketlenmiş Matrix kanal pluginidir.
Resmi `matrix-js-sdk` kullanır ve DM'leri, odaları, ileti dizilerini, medyayı, tepkileri, anketleri, konumu ve E2EE'yi destekler.

## Paketlenmiş plugin

Matrix, güncel OpenClaw sürümlerinde paketlenmiş bir plugin olarak gelir, bu nedenle normal
paketlenmiş derlemelerde ayrı bir kurulum gerekmez.

Daha eski bir derlemeyi veya Matrix'i hariç tutan özel bir kurulumu kullanıyorsanız, onu
elle kurun:

npm'den kurulum:

```bash
openclaw plugins install @openclaw/matrix
```

Yerel checkout'tan kurulum:

```bash
openclaw plugins install ./path/to/local/matrix-plugin
```

Plugin davranışı ve kurulum kuralları için [Pluginler](/tr/tools/plugin) bölümüne bakın.

## Kurulum

1. Matrix plugininin kullanılabilir olduğundan emin olun.
   - Güncel paketlenmiş OpenClaw sürümleri bunu zaten içerir.
   - Daha eski/özel kurulumlar bunu yukarıdaki komutlarla elle ekleyebilir.
2. Homeserver'ınızda bir Matrix hesabı oluşturun.
3. `channels.matrix` yapılandırmasını şu seçeneklerden biriyle ayarlayın:
   - `homeserver` + `accessToken`, veya
   - `homeserver` + `userId` + `password`.
4. Gateway'i yeniden başlatın.
5. Bot ile bir DM başlatın veya onu bir odaya davet edin.

Etkileşimli kurulum yolları:

```bash
openclaw channels add
openclaw configure --section channels
```

Matrix sihirbazının gerçekte sorduğu bilgiler:

- homeserver URL'si
- kimlik doğrulama yöntemi: erişim belirteci veya parola
- yalnızca parola kimlik doğrulamasını seçtiğinizde kullanıcı kimliği
- isteğe bağlı cihaz adı
- E2EE'nin etkinleştirilip etkinleştirilmeyeceği
- Matrix oda erişiminin şimdi yapılandırılıp yapılandırılmayacağı

Önemli sihirbaz davranışları:

- Seçilen hesap için Matrix kimlik doğrulama ortam değişkenleri zaten varsa ve bu hesap için yapılandırmada zaten kaydedilmiş kimlik doğrulama yoksa, sihirbaz bir ortam kısayolu sunar ve bu hesap için yalnızca `enabled: true` yazar.
- Etkileşimli olarak başka bir Matrix hesabı eklediğinizde, girilen hesap adı yapılandırmada ve ortam değişkenlerinde kullanılan hesap kimliğine normalize edilir. Örneğin, `Ops Bot`, `ops-bot` olur.
- DM izin listesi istemleri tam `@user:server` değerlerini hemen kabul eder. Görünen adlar yalnızca canlı dizin araması tek bir tam eşleşme bulduğunda çalışır; aksi halde sihirbaz tam bir Matrix kimliğiyle yeniden denemenizi ister.
- Oda izin listesi istemleri oda kimliklerini ve takma adları doğrudan kabul eder. Ayrıca katılınmış oda adlarını canlı olarak çözebilirler, ancak çözülemeyen adlar kurulum sırasında yalnızca girildiği şekliyle tutulur ve daha sonra çalışma zamanındaki izin listesi çözümlemesi tarafından yok sayılır. `!room:server` veya `#alias:server` tercih edin.
- Çalışma zamanı oda/oturum kimliği kararlı Matrix oda kimliğini kullanır. Oda içinde tanımlanan takma adlar yalnızca arama girdileri olarak kullanılır, uzun vadeli oturum anahtarı veya kararlı grup kimliği olarak kullanılmaz.
- Oda adlarını kaydetmeden önce çözümlemek için `openclaw channels resolve --channel matrix "Project Room"` kullanın.

Belirteç tabanlı asgari kurulum:

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

Parola tabanlı kurulum (girişten sonra belirteç önbelleğe alınır):

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      userId: "@bot:example.org",
      password: "replace-me", // pragma: izin listesi gizli bilgisi
      deviceName: "OpenClaw Gateway",
    },
  },
}
```

Matrix önbelleğe alınmış kimlik bilgilerini `~/.openclaw/credentials/matrix/` içinde saklar.
Varsayılan hesap `credentials.json` kullanır; adlandırılmış hesaplar `credentials-<account>.json` kullanır.
Önbelleğe alınmış kimlik bilgileri burada mevcut olduğunda, mevcut kimlik doğrulama doğrudan yapılandırmada ayarlanmamış olsa bile, OpenClaw kurulum, doctor ve kanal durumu keşfi için Matrix'i yapılandırılmış olarak kabul eder.

Ortam değişkeni karşılıkları (yapılandırma anahtarı ayarlanmadığında kullanılır):

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

Matrix, hesap kimliklerindeki noktalama işaretlerini, kapsamlı ortam değişkenlerini çakışmasız tutmak için kaçışlar.
Örneğin, `-` karakteri `_X2D_` olur, bu nedenle `ops-prod`, `MATRIX_OPS_X2D_PROD_*` ile eşlenir.

Etkileşimli sihirbaz, bu kimlik doğrulama ortam değişkenleri zaten mevcutsa ve seçilen hesap için yapılandırmada zaten kaydedilmiş Matrix kimlik doğrulaması yoksa, yalnızca bu durumda ortam değişkeni kısayolunu sunar.

## Yapılandırma örneği

Bu, DM eşleştirme, oda izin listesi ve etkin E2EE içeren pratik bir temel yapılandırmadır:

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
Buna yeni DM tarzı davetler de dahildir. Davet anında OpenClaw, davet edilen
odanın sonunda DM mi yoksa grup mu olarak ele alınacağını güvenilir şekilde bilemez, bu nedenle
tüm davetler önce aynı `autoJoin` kararı üzerinden geçer. Bot katıldıktan ve oda
DM olarak sınıflandırıldıktan sonra `dm.policy` yine uygulanır; dolayısıyla `autoJoin` katılma davranışını,
`dm.policy` ise yanıt/erişim davranışını kontrol eder.

## Akış önizlemeleri

Matrix yanıt akışı isteğe bağlıdır.

OpenClaw'ın tek bir canlı önizleme yanıtı göndermesini,
model metin üretirken bu önizlemeyi yerinde düzenlemesini ve ardından yanıt tamamlandığında bunu
sonlandırmasını istiyorsanız `channels.matrix.streaming` değerini `"partial"` olarak ayarlayın:

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
- `streaming: "partial"`, geçerli asistan bloğu için normal Matrix metin mesajları kullanarak düzenlenebilir bir önizleme mesajı oluşturur. Bu, Matrix'in eski önizleme-öncelikli bildirim davranışını korur; bu yüzden standart istemciler bitmiş blok yerine ilk akış önizleme metni için bildirim gönderebilir.
- `streaming: "quiet"`, geçerli asistan bloğu için düzenlenebilir sessiz bir önizleme bildirimi oluşturur. Bunu yalnızca sonlandırılmış önizleme düzenlemeleri için alıcı push kurallarını da yapılandırıyorsanız kullanın.
- `blockStreaming: true`, ayrı Matrix ilerleme mesajlarını etkinleştirir. Önizleme akışı etkinken Matrix, geçerli blok için canlı taslağı korur ve tamamlanmış blokları ayrı mesajlar olarak saklar.
- Önizleme akışı açık ve `blockStreaming` kapalı olduğunda Matrix canlı taslağı yerinde düzenler ve blok veya tur tamamlandığında aynı olayı sonlandırır.
- Önizleme artık tek bir Matrix olayına sığmıyorsa OpenClaw önizleme akışını durdurur ve normal son teslimata geri döner.
- Medya yanıtları ekleri normal şekilde göndermeye devam eder. Eski bir önizleme artık güvenle yeniden kullanılamıyorsa OpenClaw son medya yanıtını göndermeden önce onu redakte eder.
- Önizleme düzenlemeleri ek Matrix API çağrılarına mal olur. En muhafazakar hız sınırı davranışını istiyorsanız akışı kapalı bırakın.

`blockStreaming`, taslak önizlemeleri tek başına etkinleştirmez.
Önizleme düzenlemeleri için `streaming: "partial"` veya `streaming: "quiet"` kullanın; ardından yalnızca tamamlanmış asistan bloklarının ayrı ilerleme mesajları olarak görünür kalmasını da istiyorsanız `blockStreaming: true` ekleyin.

Özel push kuralları olmadan standart Matrix bildirimlerine ihtiyacınız varsa, önizleme-öncelikli davranış için `streaming: "partial"` kullanın veya yalnızca son teslimat için `streaming` değerini kapalı bırakın. `streaming: "off"` ile:

- `blockStreaming: true`, tamamlanan her bloğu normal bildirim veren bir Matrix mesajı olarak gönderir.
- `blockStreaming: false`, yalnızca son tamamlanmış yanıtı normal bildirim veren bir Matrix mesajı olarak gönderir.

### Sessiz sonlandırılmış önizlemeler için self-hosted push kuralları

Kendi Matrix altyapınızı çalıştırıyorsanız ve sessiz önizlemelerin yalnızca bir blok veya
son yanıt tamamlandığında bildirim göndermesini istiyorsanız, `streaming: "quiet"` ayarlayın ve sonlandırılmış önizleme düzenlemeleri için kullanıcı başına bir push kuralı ekleyin.

Bu genellikle homeserver genelinde bir yapılandırma değişikliği değil, alıcı kullanıcı tarafında bir kurulumdur:

Başlamadan önce hızlı özet:

- alıcı kullanıcı = bildirimi alması gereken kişi
- bot kullanıcısı = yanıtı gönderen OpenClaw Matrix hesabı
- aşağıdaki API çağrıları için alıcı kullanıcının erişim belirtecini kullanın
- push kuralındaki `sender` alanını bot kullanıcısının tam MXID'siyle eşleştirin

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
   kuralları yalnızca bu kullanıcının çalışan pusher'ları/cihazları zaten varsa çalışır.

3. Alıcı kullanıcının erişim belirtecini alın.
   - Botun belirtecini değil, alıcı kullanıcının belirtecini kullanın.
   - Mevcut bir istemci oturum belirtecini yeniden kullanmak genellikle en kolay yoldur.
   - Yeni bir belirteç üretmeniz gerekiyorsa standart Matrix Client-Server API üzerinden giriş yapabilirsiniz:

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
OpenClaw kuralını eklemeden önce normal Matrix bildirimlerini düzeltin.

OpenClaw, sonlandırılmış yalnızca metin içeren önizleme düzenlemelerini şu şekilde işaretler:

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
- `$USER_ACCESS_TOKEN`: alıcı kullanıcının erişim belirteci
- `openclaw-finalized-preview-botname`: bu alıcı kullanıcı için bu bota özgü bir kural kimliği
- `@bot:example.org`: alıcı kullanıcının MXID'si değil, OpenClaw Matrix bot MXID'niz

Çoklu bot kurulumları için önemli:

- Push kuralları `ruleId` ile anahtarlanır. Aynı kural kimliğine karşı `PUT` işlemini yeniden çalıştırmak, o tek kuralı günceller.
- Bir alıcı kullanıcının birden fazla OpenClaw Matrix bot hesabı için bildirim alması gerekiyorsa, her gönderici eşleşmesi için benzersiz kural kimliğine sahip bir kural oluşturun.
- Basit bir desen `openclaw-finalized-preview-<botname>` biçimidir; örneğin `openclaw-finalized-preview-ops` veya `openclaw-finalized-preview-support`.

Kural olay göndericisine karşı değerlendirilir:

- alıcı kullanıcının belirteciyle kimlik doğrulayın
- `sender` alanını OpenClaw bot MXID'sine karşı eşleştirin

6. Kuralın var olduğunu doğrulayın:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

7. Akışlı bir yanıtı test edin. Sessiz modda oda sessiz bir taslak önizleme göstermeli ve son
   yerinde düzenleme blok veya tur tamamlandığında bir kez bildirim göndermelidir.

Daha sonra kuralı kaldırmanız gerekirse, aynı kural kimliğini alıcı kullanıcının belirteciyle silin:

```bash
curl -sS -X DELETE \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

Notlar:

- Kuralı botunkiyle değil, alıcı kullanıcının erişim belirteciyle oluşturun.
- Yeni kullanıcı tanımlı `override` kuralları varsayılan bastırma kurallarının önüne eklenir, bu yüzden ek bir sıralama parametresine gerek yoktur.
- Bu yalnızca OpenClaw'ın güvenle yerinde sonlandırabildiği yalnızca metin içeren önizleme düzenlemelerini etkiler. Medya fallback'leri ve eski önizleme fallback'leri yine normal Matrix teslimatını kullanır.
- Eğer `GET /_matrix/client/v3/pushers` hiçbir pusher göstermiyorsa, kullanıcının bu hesap/cihaz için çalışan Matrix push teslimi henüz yoktur.

#### Synapse

Synapse için yukarıdaki kurulum genellikle tek başına yeterlidir:

- Sonlandırılmış OpenClaw önizleme bildirimleri için özel bir `homeserver.yaml` değişikliği gerekmez.
- Synapse dağıtımınız zaten normal Matrix push bildirimleri gönderiyorsa, yukarıdaki kullanıcı belirteci + `pushrules` çağrısı ana kurulum adımıdır.
- Synapse'i reverse proxy veya worker'ların arkasında çalıştırıyorsanız `/_matrix/client/.../pushrules/` yolunun Synapse'e doğru ulaştığından emin olun.
- Synapse worker'ları kullanıyorsanız pusher'ların sağlıklı olduğundan emin olun. Push teslimi ana süreç veya `synapse.app.pusher` / yapılandırılmış pusher worker'ları tarafından gerçekleştirilir.

#### Tuwunel

Tuwunel için yukarıda gösterilen aynı kurulum akışını ve push-rule API çağrısını kullanın:

- Sonlandırılmış önizleme işaretçisi için Tuwunel'e özgü bir yapılandırma gerekmez.
- Normal Matrix bildirimleri bu kullanıcı için zaten çalışıyorsa, yukarıdaki kullanıcı belirteci + `pushrules` çağrısı ana kurulum adımıdır.
- Kullanıcı başka bir cihazda etkin durumdayken bildirimler kayboluyor gibi görünüyorsa `suppress_push_when_active` ayarının etkin olup olmadığını kontrol edin. Tuwunel bu seçeneği 12 Eylül 2025 tarihinde Tuwunel 1.4.2 sürümünde ekledi ve bu seçenek bir cihaz etkinken diğer cihazlara push gönderimini kasıtlı olarak bastırabilir.

## Şifreleme ve doğrulama

Şifreli (E2EE) odalarda, giden görsel olayları `thumbnail_file` kullanır; böylece görsel önizlemeleri tam ekle birlikte şifrelenir. Şifrelenmemiş odalar hâlâ düz `thumbnail_url` kullanır. Yapılandırma gerekmez — plugin E2EE durumunu otomatik olarak algılar.

### Botlar arası odalar

Varsayılan olarak, yapılandırılmış diğer OpenClaw Matrix hesaplarından gelen Matrix mesajları yok sayılır.

Bilerek ajanlar arası Matrix trafiği istiyorsanız `allowBots` kullanın:

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
- `allowBots: "mentions"`, bu mesajları odalarda yalnızca bu bottan açıkça bahsedildiğinde kabul eder. DM'lere yine izin verilir.
- `groups.<room>.allowBots`, hesap düzeyi ayarı tek bir oda için geçersiz kılar.
- OpenClaw, kendine yanıt döngülerini önlemek için yine aynı Matrix kullanıcı kimliğinden gelen mesajları yok sayar.
- Matrix burada yerel bir bot bayrağı sunmaz; OpenClaw "bot tarafından yazılmış" ifadesini "bu OpenClaw gateway'inde yapılandırılmış başka bir Matrix hesabı tarafından gönderilmiş" olarak ele alır.

Paylaşılan odalarda botlar arası trafiği etkinleştirirken sıkı oda izin listeleri ve mention gereksinimleri kullanın.

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

Ayrıntılı durum (tam tanı bilgileri):

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

Çoklu hesap desteği: hesap başına kimlik bilgileri ve isteğe bağlı `name` ile `channels.matrix.accounts` kullanın. Paylaşılan desen için [Yapılandırma başvurusu](/tr/gateway/configuration-reference#multi-account-all-channels) bölümüne bakın.

Ayrıntılı bootstrap tanıları:

```bash
openclaw matrix verify bootstrap --verbose
```

Bootstrap işleminden önce yeni bir çapraz imzalama kimliği sıfırlamasını zorlayın:

```bash
openclaw matrix verify bootstrap --force-reset-cross-signing
```

Bu cihazı bir kurtarma anahtarı ile doğrulayın:

```bash
openclaw matrix verify device "<your-recovery-key>"
```

Ayrıntılı cihaz doğrulama bilgileri:

```bash
openclaw matrix verify device "<your-recovery-key>" --verbose
```

Oda anahtarı yedeği durumunu kontrol edin:

```bash
openclaw matrix verify backup status
```

Ayrıntılı yedek durumu tanıları:

```bash
openclaw matrix verify backup status --verbose
```

Oda anahtarlarını sunucu yedeğinden geri yükleyin:

```bash
openclaw matrix verify backup restore
```

Ayrıntılı geri yükleme tanıları:

```bash
openclaw matrix verify backup restore --verbose
```

Geçerli sunucu yedeğini silin ve yeni bir yedek temel çizgisi oluşturun. Saklanan
yedek anahtarı temiz şekilde yüklenemiyorsa, bu sıfırlama secret storage'ı da yeniden oluşturabilir; böylece
gelecekteki soğuk başlangıçlar yeni yedek anahtarını yükleyebilir:

```bash
openclaw matrix verify backup reset --yes
```

Tüm `verify` komutları varsayılan olarak kısadır (sessiz dahili SDK günlükleri dahil) ve ayrıntılı tanıları yalnızca `--verbose` ile gösterir.
Betik yazarken tam makine tarafından okunabilir çıktı için `--json` kullanın.

Çoklu hesap kurulumlarında Matrix CLI komutları, siz `--account <id>` geçmediğiniz sürece örtük Matrix varsayılan hesabını kullanır.
Birden fazla adlandırılmış hesap yapılandırırsanız önce `channels.matrix.defaultAccount` ayarlayın; aksi halde bu örtük CLI işlemleri durur ve sizden açıkça bir hesap seçmenizi ister.
Doğrulama veya cihaz işlemlerinin belirli bir adlandırılmış hesabı açıkça hedeflemesini istediğinizde `--account` kullanın:

```bash
openclaw matrix verify status --account assistant
openclaw matrix verify backup restore --account assistant
openclaw matrix devices list --account assistant
```

Şifreleme belirli bir adlandırılmış hesap için devre dışıysa veya kullanılamıyorsa, Matrix uyarıları ve doğrulama hataları o hesabın yapılandırma anahtarını işaret eder; örneğin `channels.matrix.accounts.assistant.encryption`.

### "Doğrulanmış" ne anlama gelir

OpenClaw bu Matrix cihazını yalnızca cihaz sizin kendi çapraz imzalama kimliğiniz tarafından doğrulanmışsa doğrulanmış kabul eder.
Pratikte, `openclaw matrix verify status --verbose` üç güven sinyali gösterir:

- `Locally trusted`: bu cihaz yalnızca mevcut istemci tarafından güvenilir kabul edilir
- `Cross-signing verified`: SDK bu cihazın çapraz imzalama yoluyla doğrulandığını bildirir
- `Signed by owner`: cihaz sizin kendi self-signing anahtarınız tarafından imzalanmıştır

`Verified by owner`, yalnızca çapraz imzalama doğrulaması veya owner-signing mevcut olduğunda `yes` olur.
Yalnızca yerel güven, OpenClaw'ın cihazı tam doğrulanmış olarak kabul etmesi için yeterli değildir.

### Bootstrap ne yapar

`openclaw matrix verify bootstrap`, şifreli Matrix hesapları için onarım ve kurulum komutudur.
Aşağıdakilerin tümünü sırayla yapar:

- mümkün olduğunda mevcut kurtarma anahtarını yeniden kullanarak secret storage'ı bootstrap eder
- çapraz imzalamayı bootstrap eder ve eksik genel çapraz imzalama anahtarlarını yükler
- mevcut cihazı işaretlemeye ve çapraz imzalamaya çalışır
- henüz yoksa yeni bir sunucu tarafı oda anahtarı yedeği oluşturur

Homeserver, çapraz imzalama anahtarlarını yüklemek için etkileşimli kimlik doğrulama gerektiriyorsa, OpenClaw yüklemeyi önce kimlik doğrulama olmadan, sonra `m.login.dummy` ile, ardından `channels.matrix.password` yapılandırılmışsa `m.login.password` ile dener.

Geçerli çapraz imzalama kimliğini bilerek atıp yenisini oluşturmak istiyorsanız yalnızca `--force-reset-cross-signing` kullanın.

Geçerli oda anahtarı yedeğini bilerek atıp gelecekteki iletiler için yeni bir
yedek temel çizgisi başlatmak istiyorsanız `openclaw matrix verify backup reset --yes` kullanın.
Bunu yalnızca kurtarılamayan eski şifreli geçmişin erişilemez
kalacağını ve OpenClaw'ın mevcut yedek
gizli bilgisi güvenle yüklenemiyorsa secret storage'ı yeniden oluşturabileceğini kabul ettiğinizde yapın.

### Yeni yedek temel çizgisi

Gelecekteki şifreli iletilerin çalışmaya devam etmesini istiyor ve kurtarılamayan eski geçmişi kaybetmeyi kabul ediyorsanız, bu komutları sırayla çalıştırın:

```bash
openclaw matrix verify backup reset --yes
openclaw matrix verify backup status --verbose
openclaw matrix verify status
```

Belirli bir adlandırılmış Matrix hesabını açıkça hedeflemek istediğinizde her komuta `--account <id>` ekleyin.

### Başlangıç davranışı

`encryption: true` olduğunda Matrix varsayılan olarak `startupVerification` değerini `"if-unverified"` yapar.
Başlangıçta, bu cihaz hâlâ doğrulanmamışsa Matrix başka bir Matrix istemcisinde self-verification isteyecek,
biri zaten beklemedeyken yinelenen istekleri atlayacak ve yeniden başlatmalardan sonra yeniden denemeden önce yerel bir bekleme süresi uygulayacaktır.
Başarısız istek denemeleri varsayılan olarak başarılı istek oluşturmadan daha erken yeniden denenir.
Otomatik başlangıç isteklerini devre dışı bırakmak için `startupVerification: "off"` ayarlayın veya daha kısa ya da daha uzun bir yeniden deneme penceresi istiyorsanız `startupVerificationCooldownHours` değerini ayarlayın.

Başlangıç ayrıca otomatik olarak muhafazakar bir kripto bootstrap geçişi yapar.
Bu geçiş önce mevcut secret storage ve çapraz imzalama kimliğini yeniden kullanmaya çalışır ve siz açık bir bootstrap onarım akışı çalıştırmadıkça çapraz imzalamayı sıfırlamaktan kaçınır.

Başlangıç bozuk bootstrap durumu bulursa ve `channels.matrix.password` yapılandırılmışsa, OpenClaw daha sıkı bir onarım yolunu deneyebilir.
Mevcut cihaz zaten owner-signed ise OpenClaw bu kimliği otomatik olarak sıfırlamak yerine korur.

Önceki genel Matrix plugininden yükseltme:

- OpenClaw mümkün olduğunda aynı Matrix hesabını, erişim belirtecini ve cihaz kimliğini otomatik olarak yeniden kullanır.
- Herhangi bir eyleme dönüştürülebilir Matrix geçiş değişikliği çalıştırılmadan önce OpenClaw `~/Backups/openclaw-migrations/` altında bir kurtarma anlık görüntüsü oluşturur veya mevcut olanı yeniden kullanır.
- Birden fazla Matrix hesabı kullanıyorsanız, eski düz depo düzeninden yükseltmeden önce `channels.matrix.defaultAccount` ayarlayın; böylece OpenClaw bu paylaşılan eski durumun hangi hesap tarafından alınacağını bilir.
- Önceki plugin bir Matrix oda anahtarı yedek çözme anahtarını yerelde sakladıysa, başlangıç veya `openclaw doctor --fix` bunu otomatik olarak yeni kurtarma anahtarı akışına aktarır.
- Matrix erişim belirteci geçiş hazırlandıktan sonra değiştiyse, başlangıç artık otomatik yedek geri yüklemeden vazgeçmeden önce bekleyen eski geri yükleme durumunu aramak için komşu belirteç-hash depolama köklerini tarar.
- Matrix erişim belirteci daha sonra aynı hesap, homeserver ve kullanıcı için değişirse, OpenClaw artık boş bir Matrix durum dizininden başlamak yerine en eksiksiz mevcut belirteç-hash depolama kökünü yeniden kullanmayı tercih eder.
- Bir sonraki gateway başlangıcında yedeklenmiş oda anahtarları otomatik olarak yeni kripto deposuna geri yüklenir.
- Eski pluginde yalnızca yerel olup hiç yedeklenmemiş oda anahtarları varsa OpenClaw açık bir uyarı verir. Bu anahtarlar önceki rust kripto deposundan otomatik olarak dışa aktarılamaz, bu nedenle bazı eski şifreli geçmişler elle kurtarılana kadar erişilemez kalabilir.
- Tam yükseltme akışı, sınırlar, kurtarma komutları ve yaygın geçiş iletileri için [Matrix geçişi](/tr/install/migrating-matrix) bölümüne bakın.

Şifreli çalışma zamanı durumu, hesap başına ve kullanıcı başına belirteç-hash kökleri altında
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/` içinde düzenlenir.
Bu dizin sync deposunu (`bot-storage.json`), kripto deposunu (`crypto/`),
kurtarma anahtarı dosyasını (`recovery-key.json`), IndexedDB anlık görüntüsünü (`crypto-idb-snapshot.json`),
ileti dizisi bağlamalarını (`thread-bindings.json`) ve başlangıç doğrulama durumunu (`startup-verification.json`)
bu özellikler kullanımdayken içerir.
Belirteç değiştiğinde ancak hesap kimliği aynı kaldığında OpenClaw, o hesap/homeserver/kullanıcı üçlüsü için mevcut en iyi
kökü yeniden kullanır; böylece önceki sync durumu, kripto durumu, ileti dizisi bağlamaları
ve başlangıç doğrulama durumu görünür kalır.

### Node kripto deposu modeli

Bu plugindeki Matrix E2EE, Node içinde resmi `matrix-js-sdk` Rust kripto yolunu kullanır.
Kripto durumunun yeniden başlatmalar arasında kalıcı olmasını istiyorsanız bu yol IndexedDB tabanlı kalıcılık bekler.

OpenClaw şu anda bunu Node içinde şu şekilde sağlar:

- SDK'nın beklediği IndexedDB API shim'i olarak `fake-indexeddb` kullanarak
- `initRustCrypto` öncesinde Rust kripto IndexedDB içeriğini `crypto-idb-snapshot.json` dosyasından geri yükleyerek
- init sonrasında ve çalışma zamanı sırasında güncellenmiş IndexedDB içeriğini tekrar `crypto-idb-snapshot.json` dosyasına yazarak
- gateway çalışma zamanı kalıcılığı ile CLI bakımının aynı anlık görüntü dosyası üzerinde yarışmaması için, anlık görüntü geri yükleme ve yazma işlemlerini `crypto-idb-snapshot.json` üzerinde danışmalı bir dosya kilidiyle serileştirerek

Bu, özel bir kripto uygulaması değil; uyumluluk/depolama altyapısıdır.
Anlık görüntü dosyası hassas çalışma zamanı durumudur ve kısıtlayıcı dosya izinleriyle saklanır.
OpenClaw'ın güvenlik modelinde, gateway sunucusu ve yerel OpenClaw durum dizini zaten güvenilen operatör sınırının içindedir; bu nedenle bu konu ayrı bir uzak güven sınırından çok operasyonel dayanıklılık konusudur.

Planlanan iyileştirme:

- kalıcı Matrix anahtar materyali için SecretRef desteği eklemek; böylece kurtarma anahtarları ve ilgili store-encryption gizli bilgileri yalnızca yerel dosyalardan değil, OpenClaw gizli bilgi sağlayıcılarından da alınabilir

## Profil yönetimi

Seçilen hesabın Matrix öz-profilini şu komutla güncelleyin:

```bash
openclaw matrix profile set --name "OpenClaw Assistant"
openclaw matrix profile set --avatar-url https://cdn.example.org/avatar.png
```

Belirli bir adlandırılmış Matrix hesabını açıkça hedeflemek istediğinizde `--account <id>` ekleyin.

Matrix, `mxc://` avatar URL'lerini doğrudan kabul eder. `http://` veya `https://` bir avatar URL'si verdiğinizde OpenClaw önce bunu Matrix'e yükler ve çözümlenen `mxc://` URL'sini tekrar `channels.matrix.avatarUrl` içine (veya seçilen hesap geçersiz kılmasına) kaydeder.

## Otomatik doğrulama bildirimleri

Matrix artık doğrulama yaşam döngüsü bildirimlerini doğrudan sıkı DM doğrulama odasına `m.notice` mesajları olarak gönderir.
Buna şunlar dahildir:

- doğrulama isteği bildirimleri
- doğrulama hazır bildirimleri (açık "Emoji ile doğrula" yönlendirmesi ile)
- doğrulama başlangıç ve tamamlanma bildirimleri
- uygun olduğunda SAS ayrıntıları (emoji ve ondalık)

Başka bir Matrix istemcisinden gelen doğrulama istekleri OpenClaw tarafından izlenir ve otomatik olarak kabul edilir.
Self-verification akışları için OpenClaw, emoji doğrulaması kullanılabilir olduğunda SAS akışını otomatik olarak başlatır ve kendi tarafını onaylar.
Başka bir Matrix kullanıcısı/cihazından gelen doğrulama istekleri için OpenClaw isteği otomatik olarak kabul eder ve ardından SAS akışının normal şekilde ilerlemesini bekler.
Doğrulamayı tamamlamak için yine de Matrix istemcinizde emoji veya ondalık SAS'ı karşılaştırmanız ve orada "Eşleşiyorlar" seçeneğini onaylamanız gerekir.

OpenClaw, kendi başlattığı yinelenen akışları körü körüne otomatik kabul etmez. Self-verification isteği zaten beklemedeyken başlangıç yeni bir istek oluşturmayı atlar.

Doğrulama protokolü/sistem bildirimleri ajan sohbet hattına iletilmez, bu nedenle `NO_REPLY` üretmezler.

### Cihaz hijyeni

Hesapta eski OpenClaw tarafından yönetilen Matrix cihazları birikebilir ve şifreli oda güvenini anlamayı zorlaştırabilir.
Şu komutla listeleyin:

```bash
openclaw matrix devices list
```

Eski OpenClaw tarafından yönetilen cihazları şu komutla kaldırın:

```bash
openclaw matrix devices prune-stale
```

### Doğrudan Oda Onarımı

Doğrudan mesaj durumu senkron dışına çıkarsa OpenClaw, canlı DM yerine eski tekli odalara işaret eden bayat `m.direct` eşlemeleriyle karşılaşabilir. Bir eş için mevcut eşlemeyi incelemek için şunu kullanın:

```bash
openclaw matrix direct inspect --user-id @alice:example.org
```

Şu komutla onarın:

```bash
openclaw matrix direct repair --user-id @alice:example.org
```

Onarım, Matrix'e özgü mantığı plugin içinde tutar:

- önce `m.direct` içinde zaten eşlenmiş olan sıkı bir 1:1 DM'yi tercih eder
- aksi halde o kullanıcıyla şu anda katılınmış olan herhangi bir sıkı 1:1 DM'ye geri döner
- sağlıklı bir DM yoksa yeni bir doğrudan oda oluşturur ve `m.direct` alanını onu işaret edecek şekilde yeniden yazar

Onarım akışı eski odaları otomatik olarak silmez. Yalnızca sağlıklı DM'yi seçer ve eşlemeyi günceller; böylece yeni Matrix gönderimleri, doğrulama bildirimleri ve diğer doğrudan mesaj akışları yeniden doğru odayı hedefler.

## İleti dizileri

Matrix hem otomatik yanıtlar hem de message-tool gönderimleri için yerel Matrix ileti dizilerini destekler.

- `dm.sessionScope: "per-user"` (varsayılan), Matrix DM yönlendirmesini gönderici kapsamlı tutar; böylece birden fazla DM odası aynı eşe çözülüyorsa tek bir oturumu paylaşabilir.
- `dm.sessionScope: "per-room"`, her Matrix DM odasını kendi oturum anahtarına ayırırken normal DM kimlik doğrulama ve izin listesi kontrollerini kullanmaya devam eder.
- Açık Matrix konuşma bağlamaları yine de `dm.sessionScope` üzerinde önceliklidir; bu nedenle bağlanmış odalar ve ileti dizileri seçtikleri hedef oturumu korur.
- `threadReplies: "off"`, yanıtları üst düzeyde tutar ve gelen ileti dizili mesajları ana oturumda tutar.
- `threadReplies: "inbound"`, yalnızca gelen mesaj zaten o ileti dizisindeyse ileti dizisi içinde yanıt verir.
- `threadReplies: "always"`, oda yanıtlarını tetikleyici mesaja köklenen bir ileti dizisinde tutar ve bu konuşmayı ilk tetikleyici mesajdan itibaren eşleşen ileti dizisi kapsamlı oturum üzerinden yönlendirir.
- `dm.threadReplies`, yalnızca DM'ler için üst düzey ayarı geçersiz kılar. Örneğin, odalardaki ileti dizilerini yalıtılmış tutarken DM'leri düz tutabilirsiniz.
- Gelen ileti dizili mesajlar, ileti dizisi kök mesajını ek ajan bağlamı olarak içerir.
- Message-tool gönderimleri artık hedef aynı oda veya aynı DM kullanıcı hedefi olduğunda mevcut Matrix ileti dizisini otomatik olarak devralır; açık bir `threadId` verilmişse bu geçerli değildir.
- Aynı oturumdaki DM kullanıcı hedefi yeniden kullanımı yalnızca mevcut oturum meta verileri aynı Matrix hesabındaki aynı DM eşini kanıtladığında devreye girer; aksi halde OpenClaw normal kullanıcı kapsamlı yönlendirmeye geri döner.
- OpenClaw, aynı paylaşılan Matrix DM oturumunda bir Matrix DM odasının başka bir DM odasıyla çakıştığını gördüğünde, ileti dizisi bağlamaları etkinse ve `dm.sessionScope` ipucuyla birlikte o odada bir kerelik `/focus` kaçış yolunu içeren bir `m.notice` yayınlar.
- Çalışma zamanı ileti dizisi bağlamaları Matrix için desteklenir. `/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age` ve ileti dizisine bağlı `/acp spawn` artık Matrix odalarında ve DM'lerde çalışır.
- Üst düzey Matrix oda/DM `/focus`, `threadBindings.spawnSubagentSessions=true` olduğunda yeni bir Matrix ileti dizisi oluşturur ve onu hedef oturuma bağlar.
- Mevcut bir Matrix ileti dizisi içinde `/focus` veya `/acp spawn --thread here` çalıştırmak bunun yerine mevcut ileti dizisini bağlar.

## ACP konuşma bağlamaları

Matrix odaları, DM'ler ve mevcut Matrix ileti dizileri sohbet yüzeyini değiştirmeden kalıcı ACP çalışma alanlarına dönüştürülebilir.

Hızlı operatör akışı:

- Kullanmaya devam etmek istediğiniz Matrix DM, oda veya mevcut ileti dizisi içinde `/acp spawn codex --bind here` çalıştırın.
- Üst düzey bir Matrix DM veya odasında, mevcut DM/oda sohbet yüzeyi olarak kalır ve gelecekteki mesajlar oluşturulan ACP oturumuna yönlendirilir.
- Mevcut bir Matrix ileti dizisi içinde `--bind here`, mevcut ileti dizisini yerinde bağlar.
- `/new` ve `/reset`, aynı bağlı ACP oturumunu yerinde sıfırlar.
- `/acp close`, ACP oturumunu kapatır ve bağlamayı kaldırır.

Notlar:

- `--bind here`, alt Matrix ileti dizisi oluşturmaz.
- `threadBindings.spawnAcpSessions`, yalnızca OpenClaw'ın alt Matrix ileti dizisi oluşturması veya bağlaması gereken `/acp spawn --thread auto|here` için gereklidir.

### İleti Dizisi Bağlama Yapılandırması

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

Matrix giden tepki eylemlerini, gelen tepki bildirimlerini ve gelen ack tepkilerini destekler.

- Giden tepki araçları `channels["matrix"].actions.reactions` ile denetlenir.
- `react`, belirli bir Matrix olayına tepki ekler.
- `reactions`, belirli bir Matrix olayı için mevcut tepki özetini listeler.
- `emoji=""`, bot hesabının o olay üzerindeki kendi tepkilerini kaldırır.
- `remove: true`, bot hesabından yalnızca belirtilen emoji tepkisini kaldırır.

Ack tepkileri standart OpenClaw çözümleme sırasını kullanır:

- `channels["matrix"].accounts.<accountId>.ackReaction`
- `channels["matrix"].ackReaction`
- `messages.ackReaction`
- ajan kimliği emoji fallback'i

Ack tepki kapsamı şu sırayla çözülür:

- `channels["matrix"].accounts.<accountId>.ackReactionScope`
- `channels["matrix"].ackReactionScope`
- `messages.ackReactionScope`

Tepki bildirim modu şu sırayla çözülür:

- `channels["matrix"].accounts.<accountId>.reactionNotifications`
- `channels["matrix"].reactionNotifications`
- varsayılan: `own`

Geçerli davranış:

- `reactionNotifications: "own"`, bottan yazılmış Matrix mesajlarını hedeflediklerinde eklenen `m.reaction` olaylarını iletir.
- `reactionNotifications: "off"`, tepki sistem olaylarını devre dışı bırakır.
- Tepki kaldırmaları hâlâ sistem olaylarına dönüştürülmez çünkü Matrix bunları bağımsız `m.reaction` kaldırmaları olarak değil, redaction olarak gösterir.

## Geçmiş bağlamı

- `channels.matrix.historyLimit`, bir Matrix oda mesajı ajanı tetiklediğinde kaç son oda mesajının `InboundHistory` olarak ekleneceğini kontrol eder.
- Bu ayar `messages.groupChat.historyLimit` değerine geri döner. Her ikisi de ayarlanmamışsa etkin varsayılan `0` olur; bu nedenle mention-gated oda mesajları tamponlanmaz. Devre dışı bırakmak için `0` ayarlayın.
- Matrix oda geçmişi yalnızca oda içindir. DM'ler normal oturum geçmişini kullanmaya devam eder.
- Matrix oda geçmişi yalnızca pending öğeleri içerir: OpenClaw henüz yanıt tetiklememiş oda mesajlarını tamponlar, sonra bir mention veya başka bir tetikleyici geldiğinde bu pencerenin anlık görüntüsünü alır.
- Geçerli tetikleyici mesaj `InboundHistory` içine dahil edilmez; o tur için ana gelen gövdede kalır.
- Aynı Matrix olayının yeniden denemeleri, daha yeni oda mesajlarına doğru kaymak yerine özgün geçmiş anlık görüntüsünü yeniden kullanır.

## Bağlam görünürlüğü

Matrix, alınan yanıt metni, ileti dizisi kökleri ve bekleyen geçmiş gibi ek oda bağlamı için paylaşılan `contextVisibility` denetimini destekler.

- `contextVisibility: "all"` varsayılandır. Ek bağlam alındığı gibi korunur.
- `contextVisibility: "allowlist"`, ek bağlamı etkin oda/kullanıcı izin listesi kontrolleri tarafından izin verilen gönderenlere filtreler.
- `contextVisibility: "allowlist_quote"`, `allowlist` gibi davranır ancak yine de açık bir alıntılanmış yanıtı korur.

Bu ayar ek bağlam görünürlüğünü etkiler; gelen iletinin kendisinin bir yanıtı tetikleyip tetikleyemeyeceğini etkilemez.
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

Mention-gating ve izin listesi davranışı için [Gruplar](/tr/channels/groups) bölümüne bakın.

Matrix DM'leri için eşleştirme örneği:

```bash
openclaw pairing list matrix
openclaw pairing approve matrix <CODE>
```

Onaylanmamış bir Matrix kullanıcısı onaydan önce size mesaj göndermeye devam ederse, OpenClaw aynı bekleyen eşleştirme kodunu yeniden kullanır ve yeni bir kod üretmek yerine kısa bir bekleme süresinden sonra yeniden hatırlatma yanıtı gönderebilir.

Paylaşılan DM eşleştirme akışı ve depolama düzeni için [Eşleştirme](/tr/channels/pairing) bölümüne bakın.

## Exec onayları

Matrix, bir Matrix hesabı için exec onay istemcisi olarak çalışabilir.

- `channels.matrix.execApprovals.enabled`
- `channels.matrix.execApprovals.approvers` (isteğe bağlı; `channels.matrix.dm.allowFrom` değerine geri döner)
- `channels.matrix.execApprovals.target` (`dm` | `channel` | `both`, varsayılan: `dm`)
- `channels.matrix.execApprovals.agentFilter`
- `channels.matrix.execApprovals.sessionFilter`

Onaylayıcılar `@owner:example.org` gibi Matrix kullanıcı kimlikleri olmalıdır. `enabled` ayarlanmamış veya `"auto"` ise ve en az bir onaylayıcı `execApprovals.approvers` ya da `channels.matrix.dm.allowFrom` üzerinden çözümlenebiliyorsa Matrix yerel exec onaylarını otomatik etkinleştirir. Matrix'i yerel onay istemcisi olarak açıkça devre dışı bırakmak için `enabled: false` ayarlayın. Aksi halde onay istekleri başka yapılandırılmış onay yollarına veya exec onay fallback politikasına geri döner.

Yerel Matrix yönlendirmesi bugün yalnızca exec içindir:

- `channels.matrix.execApprovals.*`, yalnızca exec onayları için yerel DM/kanal yönlendirmesini kontrol eder.
- Plugin onayları hâlâ paylaşılan aynı sohbet içi `/approve` ve yapılandırılmış herhangi bir `approvals.plugin` iletmesini kullanır.
- Matrix, onaylayıcıları güvenle çıkarabildiğinde plugin onay yetkilendirmesi için yine `channels.matrix.dm.allowFrom` kullanabilir, ancak ayrı bir yerel plugin onayı DM/kanal fanout yolu sunmaz.

Teslim kuralları:

- `target: "dm"`, onay istemlerini onaylayıcı DM'lerine gönderir
- `target: "channel"`, istemi kaynak Matrix oda veya DM'sine geri gönderir
- `target: "both"`, istemleri onaylayıcı DM'lerine ve kaynak Matrix oda veya DM'sine gönderir

Matrix onay istemleri, birincil onay mesajında tepki kısayolları oluşturur:

- `✅` = bir kez izin ver
- `❌` = reddet
- `♾️` = bu karar etkin exec politikası tarafından izin veriliyorsa her zaman izin ver

Onaylayıcılar bu mesaja tepki verebilir veya fallback slash komutlarını kullanabilir: `/approve <id> allow-once`, `/approve <id> allow-always` veya `/approve <id> deny`.

Yalnızca çözümlenmiş onaylayıcılar onaylayabilir veya reddedebilir. Kanal teslimi komut metnini içerir; bu nedenle `channel` veya `both` seçeneklerini yalnızca güvenilen odalarda etkinleştirin.

Matrix onay istemleri paylaşılan çekirdek onay planlayıcısını yeniden kullanır. Matrix'e özgü yerel yüzey exec onayları için yalnızca taşıma katmanıdır: oda/DM yönlendirmesi ve mesaj gönderme/güncelleme/silme davranışı.

Hesap başına geçersiz kılma:

- `channels.matrix.accounts.<account>.execApprovals`

İlgili belgeler: [Exec onayları](/tr/tools/exec-approvals)

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

Üst düzey `channels.matrix` değerleri, bir hesap tarafından geçersiz kılınmadıkça adlandırılmış hesaplar için varsayılan görevi görür.
Devralınan oda girdilerini tek bir Matrix hesabına `groups.<room>.account` (veya eski `rooms.<room>.account`) ile sınırlayabilirsiniz.
`account` içermeyen girdiler tüm Matrix hesapları arasında paylaşılmış kalır ve `account: "default"` içeren girdiler varsayılan hesap doğrudan üst düzey `channels.matrix.*` üzerinde yapılandırıldığında yine çalışır.
Kısmi paylaşılan kimlik doğrulama varsayılanları tek başlarına ayrı bir örtük varsayılan hesap oluşturmaz. OpenClaw, üst düzey `default` hesabını yalnızca o varsayılan hesap yeni kimlik doğrulamaya sahipse (`homeserver` artı `accessToken` veya `homeserver` artı `userId` ve `password`) sentezler; adlandırılmış hesaplar, önbelleğe alınmış kimlik bilgileri kimlik doğrulamayı daha sonra sağlarsa `homeserver` artı `userId` üzerinden yine keşfedilebilir kalabilir.
Matrix zaten tam olarak bir adlandırılmış hesaba sahipse veya `defaultAccount` mevcut bir adlandırılmış hesap anahtarını işaret ediyorsa, tek hesaplıdan çok hesaplıya onarım/kurulum yükseltmesi yeni bir `accounts.default` girdisi oluşturmak yerine bu hesabı korur. Yalnızca Matrix kimlik doğrulama/bootstrap anahtarları bu yükseltilmiş hesaba taşınır; paylaşılan teslim politikası anahtarları üst düzeyde kalır.
Örtük yönlendirme, probing ve CLI işlemleri için OpenClaw'ın belirli bir adlandırılmış Matrix hesabını tercih etmesini istiyorsanız `defaultAccount` ayarlayın.
Birden fazla adlandırılmış hesap yapılandırıyorsanız, örtük hesap seçimine dayanan CLI komutları için `defaultAccount` ayarlayın veya `--account <id>` geçin.
Bir komut için bu örtük seçimi geçersiz kılmak istediğinizde `openclaw matrix verify ...` ve `openclaw matrix devices ...` komutlarına `--account <id>` geçin.

## Özel/LAN homeserver'ları

Varsayılan olarak OpenClaw, SSRF koruması nedeniyle özel/iç Matrix homeserver'larını engeller; siz
hesap başına açıkça izin verene kadar.

Homeserver'ınız localhost, bir LAN/Tailscale IP'si veya dahili bir ana makine adı üzerinde çalışıyorsa,
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

Bu açık katılım yalnızca güvenilen özel/iç hedeflere izin verir. Şunun gibi
genel açık metin homeserver'lar: `http://matrix.example.org:8008` yine engellenir. Mümkün olduğunda `https://` tercih edin.

## Matrix trafiğini proxy üzerinden yönlendirme

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

OpenClaw sizden bir oda veya kullanıcı hedefi istediğinde Matrix şu hedef biçimlerini kabul eder:

- Kullanıcılar: `@user:server`, `user:@user:server` veya `matrix:user:@user:server`
- Odalar: `!room:server`, `room:!room:server` veya `matrix:room:!room:server`
- Takma adlar: `#alias:server`, `channel:#alias:server` veya `matrix:channel:#alias:server`

Canlı dizin araması giriş yapılmış Matrix hesabını kullanır:

- Kullanıcı aramaları, o homeserver'daki Matrix kullanıcı dizinini sorgular.
- Oda aramaları açık oda kimliklerini ve takma adları doğrudan kabul eder, sonra o hesap için katılınmış oda adlarında aramaya geri döner.
- Katılınmış oda adı araması en iyi çabadır. Bir oda adı bir kimliğe veya takma ada çözümlenemiyorsa, çalışma zamanındaki izin listesi çözümlemesi tarafından yok sayılır.

## Yapılandırma başvurusu

- `enabled`: kanalı etkinleştirir veya devre dışı bırakır.
- `name`: hesap için isteğe bağlı etiket.
- `defaultAccount`: birden fazla Matrix hesabı yapılandırıldığında tercih edilen hesap kimliği.
- `homeserver`: homeserver URL'si, örneğin `https://matrix.example.org`.
- `allowPrivateNetwork`: bu Matrix hesabının özel/iç homeserver'lara bağlanmasına izin verir. Homeserver `localhost`, bir LAN/Tailscale IP'si veya `matrix-synapse` gibi dahili bir ana makine adına çözülüyorsa bunu etkinleştirin.
- `proxy`: Matrix trafiği için isteğe bağlı HTTP(S) proxy URL'si. Adlandırılmış hesaplar üst düzey varsayılanı kendi `proxy` ayarlarıyla geçersiz kılabilir.
- `userId`: tam Matrix kullanıcı kimliği, örneğin `@bot:example.org`.
- `accessToken`: belirteç tabanlı kimlik doğrulama için erişim belirteci. Düz metin değerler ve SecretRef değerleri, env/file/exec sağlayıcıları genelinde `channels.matrix.accessToken` ve `channels.matrix.accounts.<id>.accessToken` için desteklenir. Bkz. [Gizli Bilgi Yönetimi](/tr/gateway/secrets).
- `password`: parola tabanlı giriş için parola. Düz metin değerler ve SecretRef değerleri desteklenir.
- `deviceId`: açık Matrix cihaz kimliği.
- `deviceName`: parola ile giriş için cihaz görünen adı.
- `avatarUrl`: profil senkronizasyonu ve `set-profile` güncellemeleri için saklanan öz-avatar URL'si.
- `initialSyncLimit`: başlangıç sync olay sınırı.
- `encryption`: E2EE'yi etkinleştirir.
- `allowlistOnly`: DM'ler ve odalar için yalnızca izin listesi davranışını zorlar.
- `allowBots`: yapılandırılmış diğer OpenClaw Matrix hesaplarından gelen mesajlara izin verir (`true` veya `"mentions"`).
- `groupPolicy`: `open`, `allowlist` veya `disabled`.
- `contextVisibility`: ek oda bağlamı görünürlük modu (`all`, `allowlist`, `allowlist_quote`).
- `groupAllowFrom`: oda trafiği için kullanıcı kimliği izin listesi.
- `groupAllowFrom` girdileri tam Matrix kullanıcı kimlikleri olmalıdır. Çözümlenmeyen adlar çalışma zamanında yok sayılır.
- `historyLimit`: grup geçmişi bağlamı olarak dahil edilecek azami oda mesajı sayısı. `messages.groupChat.historyLimit` değerine geri döner; her ikisi de ayarlanmamışsa etkin varsayılan `0` olur. Devre dışı bırakmak için `0` ayarlayın.
- `replyToMode`: `off`, `first` veya `all`.
- `markdown`: giden Matrix metni için isteğe bağlı Markdown işleme yapılandırması.
- `streaming`: `off` (varsayılan), `partial`, `quiet`, `true` veya `false`. `partial` ve `true`, normal Matrix metin mesajları ile önizleme-öncelikli taslak güncellemelerini etkinleştirir. `quiet`, self-hosted push-rule kurulumları için bildirim vermeyen önizleme bildirimleri kullanır.
- `blockStreaming`: `true`, taslak önizleme akışı etkinken tamamlanmış asistan blokları için ayrı ilerleme mesajlarını etkinleştirir.
- `threadReplies`: `off`, `inbound` veya `always`.
- `threadBindings`: ileti dizisine bağlı oturum yönlendirmesi ve yaşam döngüsü için kanal başına geçersiz kılmalar.
- `startupVerification`: başlangıçta otomatik self-verification istek modu (`if-unverified`, `off`).
- `startupVerificationCooldownHours`: otomatik başlangıç doğrulama isteklerini yeniden denemeden önce bekleme süresi.
- `textChunkLimit`: giden mesaj parça boyutu.
- `chunkMode`: `length` veya `newline`.
- `responsePrefix`: giden yanıtlar için isteğe bağlı mesaj öneki.
- `ackReaction`: bu kanal/hesap için isteğe bağlı ack tepki geçersiz kılması.
- `ackReactionScope`: isteğe bağlı ack tepki kapsamı geçersiz kılması (`group-mentions`, `group-all`, `direct`, `all`, `none`, `off`).
- `reactionNotifications`: gelen tepki bildirim modu (`own`, `off`).
- `mediaMaxMb`: Matrix medya işleme için MB cinsinden medya boyutu sınırı. Bu ayar giden gönderimlere ve gelen medya işlemeye uygulanır.
- `autoJoin`: davet otomatik katılma politikası (`always`, `allowlist`, `off`). Varsayılan: `off`. Bu ayar yalnızca oda/grup davetleri değil, DM tarzı davetler dahil genel Matrix davetleri için geçerlidir. OpenClaw bu kararı davet anında, katılınan odanın DM mi yoksa grup mu olarak sınıflandırılacağını henüz güvenilir şekilde belirleyemeden önce verir.
- `autoJoinAllowlist`: `autoJoin` değeri `allowlist` olduğunda izin verilen odalar/takma adlar. Takma ad girdileri davet işleme sırasında oda kimliklerine çözülür; OpenClaw davet edilen odanın iddia ettiği takma ad durumuna güvenmez.
- `dm`: DM politika bloğu (`enabled`, `policy`, `allowFrom`, `sessionScope`, `threadReplies`).
- `dm.policy`: OpenClaw odaya katıldıktan ve onu DM olarak sınıflandırdıktan sonraki DM erişimini kontrol eder. Bir davetin otomatik katılıp katılmayacağını değiştirmez.
- `dm.allowFrom` girdileri, siz bunları canlı dizin aramasıyla zaten çözümlemediyseniz tam Matrix kullanıcı kimlikleri olmalıdır.
- `dm.sessionScope`: `per-user` (varsayılan) veya `per-room`. Eş aynı olsa bile her Matrix DM odasının ayrı bağlam tutmasını istiyorsanız `per-room` kullanın.
- `dm.threadReplies`: yalnızca DM'ler için ileti dizisi politikası geçersiz kılması (`off`, `inbound`, `always`). Bu ayar hem yanıt yerleşimi hem de DM'lerdeki oturum yalıtımı için üst düzey `threadReplies` ayarını geçersiz kılar.
- `execApprovals`: Matrix yerel exec onay teslimi (`enabled`, `approvers`, `target`, `agentFilter`, `sessionFilter`).
- `execApprovals.approvers`: exec isteklerini onaylamaya izin verilen Matrix kullanıcı kimlikleri. `dm.allowFrom` zaten onaylayıcıları tanımlıyorsa isteğe bağlıdır.
- `execApprovals.target`: `dm | channel | both` (varsayılan: `dm`).
- `accounts`: adlandırılmış hesap başına geçersiz kılmalar. Üst düzey `channels.matrix` değerleri bu girdiler için varsayılan görevi görür.
- `groups`: oda başına politika eşlemesi. Oda kimliklerini veya takma adları tercih edin; çözümlenmeyen oda adları çalışma zamanında yok sayılır. Çözümleme sonrasında oturum/grup kimliği kararlı oda kimliğini kullanır, insan tarafından okunabilir etiketler ise yine oda adlarından gelir.
- `groups.<room>.account`: çoklu hesap kurulumlarında devralınan tek bir oda girdisini belirli bir Matrix hesabıyla sınırlar.
- `groups.<room>.allowBots`: yapılandırılmış bot gönderenleri için oda düzeyi geçersiz kılma (`true` veya `"mentions"`).
- `groups.<room>.users`: oda başına gönderen izin listesi.
- `groups.<room>.tools`: oda başına araç izin/verme veya reddetme geçersiz kılmaları.
- `groups.<room>.autoReply`: oda düzeyi mention-gating geçersiz kılması. `true`, o oda için mention gereksinimlerini devre dışı bırakır; `false`, onları yeniden zorunlu kılar.
- `groups.<room>.skills`: isteğe bağlı oda düzeyi Skills filtresi.
- `groups.<room>.systemPrompt`: isteğe bağlı oda düzeyi system prompt parçacığı.
- `rooms`: `groups` için eski takma ad.
- `actions`: eylem başına araç denetimi (`messages`, `reactions`, `pins`, `profile`, `memberInfo`, `channelInfo`, `verification`).

## İlgili

- [Kanallara Genel Bakış](/tr/channels) — desteklenen tüm kanallar
- [Eşleştirme](/tr/channels/pairing) — DM kimlik doğrulaması ve eşleştirme akışı
- [Gruplar](/tr/channels/groups) — grup sohbeti davranışı ve mention-gating
- [Kanal Yönlendirme](/tr/channels/channel-routing) — mesajlar için oturum yönlendirmesi
- [Güvenlik](/tr/gateway/security) — erişim modeli ve sağlamlaştırma
