---
read_when:
    - iOS node'u eşleştiriyor veya yeniden bağlıyorsunuz
    - iOS uygulamasını kaynak koddan çalıştırıyorsunuz
    - Gateway keşfini veya canvas komutlarını hata ayıklıyorsunuz
summary: 'iOS node uygulaması: Gateway''e bağlanma, eşleştirme, canvas ve sorun giderme'
title: iOS Uygulaması
x-i18n:
    generated_at: "2026-04-07T08:46:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: f3e0a6e33e72d4c9f1f17ef70a1b67bae9ebe4a2dca16677ea6b28d0ddac1b4e
    source_path: platforms/ios.md
    workflow: 15
---

# iOS Uygulaması (Node)

Kullanılabilirlik: dahili önizleme. iOS uygulaması henüz herkese açık olarak dağıtılmıyor.

## Ne yapar

- Bir Gateway'e WebSocket üzerinden bağlanır (LAN veya tailnet).
- Node yeteneklerini sunar: Canvas, Ekran anlık görüntüsü, Kamera yakalama, Konum, Talk mode, Voice wake.
- `node.invoke` komutlarını alır ve node durum olaylarını bildirir.

## Gereksinimler

- Başka bir cihazda çalışan Gateway (macOS, Linux veya WSL2 üzerinden Windows).
- Ağ yolu:
  - Aynı LAN üzerinde Bonjour ile, **veya**
  - Unicast DNS-SD ile tailnet üzerinden (örnek alan adı: `openclaw.internal.`), **veya**
  - Manuel host/port (yedek).

## Hızlı başlangıç (eşleştir + bağlan)

1. Gateway'i başlatın:

```bash
openclaw gateway --port 18789
```

2. iOS uygulamasında Ayarlar'ı açın ve keşfedilmiş bir gateway seçin (veya Manuel Host'u etkinleştirip host/port girin).

3. Gateway host'unda eşleştirme isteğini onaylayın:

```bash
openclaw devices list
openclaw devices approve <requestId>
```

Uygulama değişmiş auth ayrıntılarıyla (rol/kapsamlar/genel anahtar)
eşleştirmeyi yeniden denerse, önceki bekleyen istek geçersiz kılınır ve yeni bir `requestId` oluşturulur.
Onaylamadan önce `openclaw devices list` komutunu tekrar çalıştırın.

4. Bağlantıyı doğrulayın:

```bash
openclaw nodes status
openclaw gateway call node.list --params "{}"
```

## Resmi derlemeler için relay destekli push

Resmi olarak dağıtılan iOS derlemeleri, ham APNs
token'ını gateway'e yayınlamak yerine harici push relay kullanır.

Gateway tarafı gereksinimi:

```json5
{
  gateway: {
    push: {
      apns: {
        relay: {
          baseUrl: "https://relay.example.com",
        },
      },
    },
  },
}
```

Akışın çalışma şekli:

- iOS uygulaması, App Attest ve uygulama makbuzunu kullanarak relay'e kaydolur.
- Relay, opak bir relay tanıtıcısı ve kayıt kapsamlı bir gönderim yetkisi döndürür.
- iOS uygulaması eşleştirilmiş gateway kimliğini alır ve bunu relay kaydına dahil eder; böylece relay destekli kayıt o belirli gateway'e devredilir.
- Uygulama bu relay destekli kaydı `push.apns.register` ile eşleştirilmiş gateway'e iletir.
- Gateway, `push.test`, arka plan uyandırmaları ve uyandırma dürtmeleri için depolanan bu relay tanıtıcısını kullanır.
- Gateway relay temel URL'si, resmi/TestFlight iOS derlemesine gömülmüş relay URL'si ile eşleşmelidir.
- Uygulama daha sonra farklı bir gateway'e veya farklı relay temel URL'sine sahip bir derlemeye bağlanırsa, eski bağı yeniden kullanmak yerine relay kaydını yeniler.

Gateway'in bu yol için **gerektirmediği** şeyler:

- Dağıtım genelinde bir relay token'ı yok.
- Resmi/TestFlight relay destekli gönderimler için doğrudan APNs anahtarı yok.

Beklenen operatör akışı:

1. Resmi/TestFlight iOS derlemesini yükleyin.
2. Gateway üzerinde `gateway.push.apns.relay.baseUrl` ayarlayın.
3. Uygulamayı gateway ile eşleştirin ve bağlantıyı tamamlamasına izin verin.
4. Uygulama, APNs token'ına sahip olduktan, operatör oturumu bağlandıktan ve relay kaydı başarıyla tamamlandıktan sonra `push.apns.register` çağrısını otomatik olarak yayınlar.
5. Bundan sonra `push.test`, yeniden bağlanma uyandırmaları ve uyandırma dürtmeleri depolanan relay destekli kaydı kullanabilir.

Uyumluluk notu:

- `OPENCLAW_APNS_RELAY_BASE_URL`, gateway için geçici bir env geçersiz kılması olarak hâlâ çalışır.

## Kimlik doğrulama ve güven akışı

Relay, resmi iOS derlemeleri için doğrudan gateway üzerinde APNs kullanımının sağlayamadığı iki kısıtı
uygulamak için vardır:

- Yalnızca Apple üzerinden dağıtılan gerçek OpenClaw iOS derlemeleri barındırılan relay'i kullanabilir.
- Bir gateway, yalnızca o belirli
  gateway ile eşleşmiş iOS cihazları için relay destekli push gönderebilir.

Adım adım:

1. `iOS app -> gateway`
   - Uygulama önce normal Gateway auth akışı üzerinden gateway ile eşleşir.
   - Bu, uygulamaya kimliği doğrulanmış bir node oturumu ile kimliği doğrulanmış bir operatör oturumu verir.
   - Operatör oturumu, `gateway.identity.get` çağrısı için kullanılır.

2. `iOS app -> relay`
   - Uygulama relay kayıt uç noktalarını HTTPS üzerinden çağırır.
   - Kayıt, App Attest kanıtını ve uygulama makbuzunu içerir.
   - Relay, bundle ID, App Attest kanıtı ve Apple makbuzunu doğrular ve
     resmi/üretim dağıtım yolunu zorunlu kılar.
   - Barındırılan relay'in yerel Xcode/geliştirme derlemeleri tarafından kullanılmasını engelleyen şey budur. Yerel bir derleme
     imzalanmış olabilir, ancak relay'in beklediği resmi Apple dağıtım kanıtını sağlamaz.

3. `gateway identity delegation`
   - Relay kaydından önce uygulama, eşleştirilmiş gateway kimliğini
     `gateway.identity.get` üzerinden alır.
   - Uygulama bu gateway kimliğini relay kayıt yüküne dahil eder.
   - Relay, bu gateway kimliğine devredilmiş bir relay tanıtıcısı ve kayıt kapsamlı gönderim yetkisi döndürür.

4. `gateway -> relay`
   - Gateway, `push.apns.register` çağrısından gelen relay tanıtıcısını ve gönderim yetkisini depolar.
   - `push.test`, yeniden bağlanma uyandırmaları ve uyandırma dürtmelerinde gateway, gönderim isteğini kendi cihaz kimliği ile imzalar.
   - Relay, hem depolanan gönderim yetkisini hem de gateway imzasını,
     kayıt sırasındaki devredilmiş gateway kimliğine karşı doğrular.
   - Başka bir gateway, bir şekilde tanıtıcıyı ele geçirse bile, bu depolanan kaydı yeniden kullanamaz.

5. `relay -> APNs`
   - Relay, resmi derleme için üretim APNs kimlik bilgilerine ve ham APNs token'ına sahiptir.
   - Gateway, relay destekli resmi derlemeler için ham APNs token'ını hiçbir zaman depolamaz.
   - Relay, son push'u eşleştirilmiş gateway adına APNs'e gönderir.

Bu tasarımın oluşturulma nedenleri:

- Üretim APNs kimlik bilgilerini kullanıcı gateway'lerinden uzak tutmak.
- Resmi derleme APNs ham token'larını gateway üzerinde depolamaktan kaçınmak.
- Barındırılan relay kullanımına yalnızca resmi/TestFlight OpenClaw derlemeleri için izin vermek.
- Bir gateway'in başka bir gateway'e ait iOS cihazlarına uyandırma push'u göndermesini engellemek.

Yerel/manüel derlemeler doğrudan APNs üzerinde kalır. Bu derlemeleri relay olmadan test ediyorsanız,
gateway'in yine de doğrudan APNs kimlik bilgilerine ihtiyacı vardır:

```bash
export OPENCLAW_APNS_TEAM_ID="TEAMID"
export OPENCLAW_APNS_KEY_ID="KEYID"
export OPENCLAW_APNS_PRIVATE_KEY_P8="$(cat /path/to/AuthKey_KEYID.p8)"
```

Bunlar Fastlane ayarları değil, gateway host çalışma zamanı env değişkenleridir. `apps/ios/fastlane/.env` yalnızca
`ASC_KEY_ID` ve `ASC_ISSUER_ID` gibi App Store Connect / TestFlight auth bilgilerini depolar; yerel iOS derlemeleri için
doğrudan APNs teslimini yapılandırmaz.

Önerilen gateway host depolaması:

```bash
mkdir -p ~/.openclaw/credentials/apns
chmod 700 ~/.openclaw/credentials/apns
mv /path/to/AuthKey_KEYID.p8 ~/.openclaw/credentials/apns/AuthKey_KEYID.p8
chmod 600 ~/.openclaw/credentials/apns/AuthKey_KEYID.p8
export OPENCLAW_APNS_PRIVATE_KEY_PATH="$HOME/.openclaw/credentials/apns/AuthKey_KEYID.p8"
```

`.p8` dosyasını commit etmeyin veya repo checkout'u altına koymayın.

## Keşif yolları

### Bonjour (LAN)

iOS uygulaması, `local.` üzerinde `_openclaw-gw._tcp` kaydını ve yapılandırılmışsa aynı
geniş alan DNS-SD keşif alanını tarar. Aynı LAN üzerindeki gateway'ler `local.` üzerinden otomatik görünür;
ağlar arası keşif, beacon türünü değiştirmeden yapılandırılmış geniş alan alanını kullanabilir.

### Tailnet (ağlar arası)

mDNS engellenmişse, bir unicast DNS-SD bölgesi kullanın (bir alan seçin; örnek:
`openclaw.internal.`) ve Tailscale split DNS kullanın.
CoreDNS örneği için [Bonjour](/tr/gateway/bonjour) belgesine bakın.

### Manuel host/port

Ayarlar'da **Manual Host** seçeneğini etkinleştirin ve gateway host + port değerini girin (varsayılan `18789`).

## Canvas + A2UI

iOS node, bir WKWebView canvas işler. Sürmek için `node.invoke` kullanın:

```bash
openclaw nodes invoke --node "iOS Node" --command canvas.navigate --params '{"url":"http://<gateway-host>:18789/__openclaw__/canvas/"}'
```

Notlar:

- Gateway canvas host, `/__openclaw__/canvas/` ve `/__openclaw__/a2ui/` sunar.
- Gateway HTTP sunucusundan sunulur (`gateway.port` ile aynı port, varsayılan `18789`).
- iOS node, bir canvas host URL'si ilan edildiğinde bağlanırken otomatik olarak A2UI'ye gider.
- `canvas.navigate` ve `{"url":""}` ile yerleşik iskelete dönün.

### Canvas eval / snapshot

```bash
openclaw nodes invoke --node "iOS Node" --command canvas.eval --params '{"javaScript":"(() => { const {ctx} = window.__openclaw; ctx.clearRect(0,0,innerWidth,innerHeight); ctx.lineWidth=6; ctx.strokeStyle=\"#ff2d55\"; ctx.beginPath(); ctx.moveTo(40,40); ctx.lineTo(innerWidth-40, innerHeight-40); ctx.stroke(); return \"ok\"; })()"}'
```

```bash
openclaw nodes invoke --node "iOS Node" --command canvas.snapshot --params '{"maxWidth":900,"format":"jpeg"}'
```

## Voice wake + Talk mode

- Voice wake ve Talk mode, Ayarlar'da kullanılabilir.
- iOS arka plan sesini askıya alabilir; uygulama etkin değilken ses özelliklerini en iyi çaba olarak değerlendirin.

## Yaygın hatalar

- `NODE_BACKGROUND_UNAVAILABLE`: iOS uygulamasını ön plana getirin (canvas/kamera/ekran komutları bunu gerektirir).
- `A2UI_HOST_NOT_CONFIGURED`: Gateway bir canvas host URL'si ilan etmedi; [Gateway configuration](/tr/gateway/configuration) içindeki `canvasHost` değerini kontrol edin.
- Eşleştirme istemi hiç görünmüyor: `openclaw devices list` çalıştırın ve manuel olarak onaylayın.
- Yeniden yüklemeden sonra yeniden bağlanma başarısız oluyor: Keychain eşleştirme token'ı temizlenmiş; node'u yeniden eşleştirin.

## İlgili belgeler

- [Eşleştirme](/tr/channels/pairing)
- [Keşif](/tr/gateway/discovery)
- [Bonjour](/tr/gateway/bonjour)
