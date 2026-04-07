---
read_when:
    - WhatsApp/web kanal davranışı veya gelen kutusu yönlendirmesi üzerinde çalışırken
summary: WhatsApp kanal desteği, erişim kontrolleri, teslimat davranışı ve operasyonlar
title: WhatsApp
x-i18n:
    generated_at: "2026-04-07T08:44:06Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9e2ce84d869ace6c0bebd9ec17bdbbef997a5c31e5da410b02a19a0f103f7359
    source_path: channels/whatsapp.md
    workflow: 15
---

# WhatsApp (Web kanalı)

Durum: WhatsApp Web (Baileys) üzerinden üretime hazır. Gateway bağlı oturum(lar)ın sahibidir.

## Kurulum (gerektiğinde)

- Onboarding (`openclaw onboard`) ve `openclaw channels add --channel whatsapp`,
  ilk kez seçtiğinizde WhatsApp eklentisini yüklemeyi önerir.
- `openclaw channels login --channel whatsapp` de,
  eklenti henüz mevcut değilse kurulum akışını sunar.
- Geliştirme kanalı + git checkout: varsayılan olarak yerel eklenti yolunu kullanır.
- Stable/Beta: varsayılan olarak npm paketi `@openclaw/whatsapp` kullanılır.

Elle kurulum seçeneği kullanılabilir olmaya devam eder:

```bash
openclaw plugins install @openclaw/whatsapp
```

<CardGroup cols={3}>
  <Card title="Eşleştirme" icon="link" href="/tr/channels/pairing">
    Bilinmeyen gönderenler için varsayılan DM ilkesi eşleştirmedir.
  </Card>
  <Card title="Kanal sorun giderme" icon="wrench" href="/tr/channels/troubleshooting">
    Kanallar arası tanılama ve onarım kılavuzları.
  </Card>
  <Card title="Gateway yapılandırması" icon="settings" href="/tr/gateway/configuration">
    Tam kanal yapılandırma kalıpları ve örnekleri.
  </Card>
</CardGroup>

## Hızlı kurulum

<Steps>
  <Step title="WhatsApp erişim ilkesini yapılandırın">

```json5
{
  channels: {
    whatsapp: {
      dmPolicy: "pairing",
      allowFrom: ["+15551234567"],
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15551234567"],
    },
  },
}
```

  </Step>

  <Step title="WhatsApp'ı bağlayın (QR)">

```bash
openclaw channels login --channel whatsapp
```

    Belirli bir hesap için:

```bash
openclaw channels login --channel whatsapp --account work
```

  </Step>

  <Step title="Gateway'i başlatın">

```bash
openclaw gateway
```

  </Step>

  <Step title="İlk eşleştirme isteğini onaylayın (eşleştirme modu kullanılıyorsa)">

```bash
openclaw pairing list whatsapp
openclaw pairing approve whatsapp <CODE>
```

    Eşleştirme isteklerinin süresi 1 saat sonra dolar. Bekleyen istekler kanal başına en fazla 3 ile sınırlandırılır.

  </Step>
</Steps>

<Note>
OpenClaw mümkün olduğunda WhatsApp'ı ayrı bir numarada çalıştırmanızı önerir. (Kanal meta verileri ve kurulum akışı bu kurulum için optimize edilmiştir, ancak kişisel numara kurulumları da desteklenir.)
</Note>

## Dağıtım kalıpları

<AccordionGroup>
  <Accordion title="Ayrı numara (önerilen)">
    Bu en temiz operasyonel moddur:

    - OpenClaw için ayrı bir WhatsApp kimliği
    - daha net DM izin listeleri ve yönlendirme sınırları
    - kendi kendine sohbet karışıklığı olasılığının daha düşük olması

    En az ilke kalıbı:

    ```json5
    {
      channels: {
        whatsapp: {
          dmPolicy: "allowlist",
          allowFrom: ["+15551234567"],
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Kişisel numara yedeği">
    Onboarding kişisel numara modunu destekler ve kendi kendine sohbet dostu bir temel yazar:

    - `dmPolicy: "allowlist"`
    - `allowFrom` kişisel numaranızı içerir
    - `selfChatMode: true`

    Çalışma zamanında, kendi kendine sohbet korumaları bağlı kendi numaraya ve `allowFrom` değerine göre çalışır.

  </Accordion>

  <Accordion title="Yalnızca WhatsApp Web kanal kapsamı">
    Mesajlaşma platformu kanalı, mevcut OpenClaw kanal mimarisinde WhatsApp Web tabanlıdır (`Baileys`).

    Yerleşik sohbet kanalı kayıt defterinde ayrı bir Twilio WhatsApp mesajlaşma kanalı yoktur.

  </Accordion>
</AccordionGroup>

## Çalışma zamanı modeli

- Gateway, WhatsApp soketinin ve yeniden bağlanma döngüsünün sahibidir.
- Giden gönderimler, hedef hesap için etkin bir WhatsApp dinleyicisi gerektirir.
- Durum ve yayın sohbetleri yok sayılır (`@status`, `@broadcast`).
- Doğrudan sohbetler DM oturum kurallarını kullanır (`session.dmScope`; varsayılan `main`, DM'leri ajanın ana oturumunda birleştirir).
- Grup oturumları yalıtılmıştır (`agent:<agentId>:whatsapp:group:<jid>`).
- WhatsApp Web taşıması, gateway ana makinesinde standart proxy ortam değişkenlerine uyar (`HTTPS_PROXY`, `HTTP_PROXY`, `NO_PROXY` / küçük harfli varyantlar). Kanala özel WhatsApp proxy ayarları yerine ana makine düzeyinde proxy yapılandırmasını tercih edin.

## Erişim denetimi ve etkinleştirme

<Tabs>
  <Tab title="DM ilkesi">
    `channels.whatsapp.dmPolicy`, doğrudan sohbet erişimini kontrol eder:

    - `pairing` (varsayılan)
    - `allowlist`
    - `open` (`allowFrom` içinde `"*"` bulunmasını gerektirir)
    - `disabled`

    `allowFrom`, E.164 tarzı numaraları kabul eder (dahili olarak normalize edilir).

    Çoklu hesap geçersiz kılması: `channels.whatsapp.accounts.<id>.dmPolicy` (ve `allowFrom`) o hesap için kanal düzeyindeki varsayılanlardan önceliklidir.

    Çalışma zamanı davranışı ayrıntıları:

    - eşleştirmeler kanal izin deposunda kalıcı olarak saklanır ve yapılandırılmış `allowFrom` ile birleştirilir
    - hiçbir izin listesi yapılandırılmadıysa, bağlı kendi numaraya varsayılan olarak izin verilir
    - giden `fromMe` DM'leri asla otomatik eşleştirilmez

  </Tab>

  <Tab title="Grup ilkesi + izin listeleri">
    Grup erişiminin iki katmanı vardır:

    1. **Grup üyeliği izin listesi** (`channels.whatsapp.groups`)
       - `groups` atlanırsa, tüm gruplar uygun kabul edilir
       - `groups` mevcutsa, grup izin listesi olarak çalışır (`"*"` kullanılabilir)

    2. **Grup gönderen ilkesi** (`channels.whatsapp.groupPolicy` + `groupAllowFrom`)
       - `open`: gönderen izin listesi atlanır
       - `allowlist`: gönderen `groupAllowFrom` ile eşleşmelidir (veya `*`)
       - `disabled`: tüm grup gelenlerini engeller

    Gönderen izin listesi yedeği:

    - `groupAllowFrom` ayarlanmamışsa, çalışma zamanı mevcut olduğunda `allowFrom` değerine geri döner
    - gönderen izin listeleri, bahsetme/yanıtlama etkinleştirmesinden önce değerlendirilir

    Not: hiç `channels.whatsapp` bloğu yoksa, çalışma zamanı grup ilkesi yedeği `allowlist` olur (bir uyarı günlüğüyle), `channels.defaults.groupPolicy` ayarlı olsa bile.

  </Tab>

  <Tab title="Bahsetmeler + /activation">
    Grup yanıtları varsayılan olarak bahsetme gerektirir.

    Bahsetme algılaması şunları içerir:

    - bot kimliğinin açık WhatsApp bahsetmeleri
    - yapılandırılmış bahsetme regex kalıpları (`agents.list[].groupChat.mentionPatterns`, yedek `messages.groupChat.mentionPatterns`)
    - örtük bota-yanıtlama algılaması (yanıt göndereni bot kimliğiyle eşleşir)

    Güvenlik notu:

    - alıntı/yanıt yalnızca bahsetme geçidini karşılar; gönderen yetkisi vermez
    - `groupPolicy: "allowlist"` ile, izin listesinde olmayan gönderenler, izin listesindeki bir kullanıcının mesajını yanıtlasalar bile yine engellenir

    Oturum düzeyinde etkinleştirme komutu:

    - `/activation mention`
    - `/activation always`

    `activation`, oturum durumunu günceller (genel yapılandırmayı değil). Sahip geçidine tabidir.

  </Tab>
</Tabs>

## Kişisel numara ve kendi kendine sohbet davranışı

Bağlı kendi numara `allowFrom` içinde de mevcut olduğunda, WhatsApp kendi kendine sohbet korumaları etkinleşir:

- kendi kendine sohbet dönüşlerinde okundu bilgilerini atla
- aksi halde kendinize ping atacak olan mention-JID otomatik tetikleme davranışını yok say
- `messages.responsePrefix` ayarlanmamışsa, kendi kendine sohbet yanıtları varsayılan olarak `[{identity.name}]` veya `[openclaw]` olur

## Mesaj normalizasyonu ve bağlam

<AccordionGroup>
  <Accordion title="Gelen zarf + yanıt bağlamı">
    Gelen WhatsApp mesajları paylaşılan gelen zarfına sarılır.

    Alıntılanmış bir yanıt varsa, bağlam şu biçimde eklenir:

    ```text
    [<sender> kullanıcısına yanıt veriliyor id:<stanzaId>]
    <alıntılanan gövde veya medya yer tutucusu>
    [/Yanıt veriliyor]
    ```

    Yanıt meta veri alanları da mevcut olduğunda doldurulur (`ReplyToId`, `ReplyToBody`, `ReplyToSender`, gönderen JID/E.164).

  </Accordion>

  <Accordion title="Medya yer tutucuları ve konum/kişi çıkarımı">
    Yalnızca medya içeren gelen mesajlar şu gibi yer tutucularla normalize edilir:

    - `<media:image>`
    - `<media:video>`
    - `<media:audio>`
    - `<media:document>`
    - `<media:sticker>`

    Konum ve kişi yükleri, yönlendirmeden önce metinsel bağlama normalize edilir.

  </Accordion>

  <Accordion title="Bekleyen grup geçmişi ekleme">
    Gruplar için, işlenmemiş mesajlar arabelleğe alınabilir ve bot sonunda tetiklendiğinde bağlam olarak eklenebilir.

    - varsayılan sınır: `50`
    - yapılandırma: `channels.whatsapp.historyLimit`
    - yedek: `messages.groupChat.historyLimit`
    - `0` devre dışı bırakır

    Ekleme işaretçileri:

    - `[Son yanıtınızdan bu yana sohbet mesajları - bağlam için]`
    - `[Geçerli mesaj - buna yanıt verin]`

  </Accordion>

  <Accordion title="Okundu bilgileri">
    Okundu bilgileri, kabul edilen gelen WhatsApp mesajları için varsayılan olarak etkindir.

    Genel olarak devre dışı bırakmak için:

    ```json5
    {
      channels: {
        whatsapp: {
          sendReadReceipts: false,
        },
      },
    }
    ```

    Hesap başına geçersiz kılma:

    ```json5
    {
      channels: {
        whatsapp: {
          accounts: {
            work: {
              sendReadReceipts: false,
            },
          },
        },
      },
    }
    ```

    Kendi kendine sohbet dönüşleri, genel olarak etkin olsa bile okundu bilgilerini atlar.

  </Accordion>
</AccordionGroup>

## Teslimat, parçalara ayırma ve medya

<AccordionGroup>
  <Accordion title="Metni parçalara ayırma">
    - varsayılan parça sınırı: `channels.whatsapp.textChunkLimit = 4000`
    - `channels.whatsapp.chunkMode = "length" | "newline"`
    - `newline` modu paragraf sınırlarını (boş satırlar) tercih eder, ardından uzunluk açısından güvenli parçalamaya geri döner
  </Accordion>

  <Accordion title="Giden medya davranışı">
    - resim, video, ses (PTT sesli not) ve belge yüklerini destekler
    - `audio/ogg`, sesli not uyumluluğu için `audio/ogg; codecs=opus` olarak yeniden yazılır
    - animasyonlu GIF oynatımı, video gönderimlerinde `gifPlayback: true` ile desteklenir
    - çoklu medya yanıt yükleri gönderilirken başlıklar ilk medya öğesine uygulanır
    - medya kaynağı HTTP(S), `file://` veya yerel yollar olabilir
  </Accordion>

  <Accordion title="Medya boyutu sınırları ve yedek davranış">
    - gelen medya kaydetme sınırı: `channels.whatsapp.mediaMaxMb` (varsayılan `50`)
    - giden medya gönderme sınırı: `channels.whatsapp.mediaMaxMb` (varsayılan `50`)
    - hesap başına geçersiz kılmalar `channels.whatsapp.accounts.<accountId>.mediaMaxMb` kullanır
    - resimler, sınırlara sığması için otomatik olarak optimize edilir (yeniden boyutlandırma/kalite taraması)
    - medya gönderme hatasında, ilk öğe yedeği yanıtı sessizce düşürmek yerine metin uyarısı gönderir
  </Accordion>
</AccordionGroup>

## Tepki düzeyi

`channels.whatsapp.reactionLevel`, ajanın WhatsApp'ta emoji tepkilerini ne kadar geniş kullandığını kontrol eder:

| Düzey         | Alındı tepkileri | Ajan tarafından başlatılan tepkiler | Açıklama                                        |
| ------------- | ---------------- | ----------------------------------- | ----------------------------------------------- |
| `"off"`       | Hayır            | Hayır                               | Hiç tepki yok                                   |
| `"ack"`       | Evet             | Hayır                               | Yalnızca alındı tepkileri (yanıt öncesi alındı) |
| `"minimal"`   | Evet             | Evet (temkinli)                     | Alındı + temkinli yönlendirmeli ajan tepkileri  |
| `"extensive"` | Evet             | Evet (teşvik edilir)                | Alındı + teşvik edilen yönlendirmeli ajan tepkileri |

Varsayılan: `"minimal"`.

Hesap başına geçersiz kılmalar `channels.whatsapp.accounts.<id>.reactionLevel` kullanır.

```json5
{
  channels: {
    whatsapp: {
      reactionLevel: "ack",
    },
  },
}
```

## Alındı tepkileri

WhatsApp, `channels.whatsapp.ackReaction` üzerinden gelen alımında anında alındı tepkilerini destekler.
Alındı tepkileri `reactionLevel` tarafından geçitlenir — `reactionLevel` `"off"` olduğunda bastırılır.

```json5
{
  channels: {
    whatsapp: {
      ackReaction: {
        emoji: "👀",
        direct: true,
        group: "mentions", // always | mentions | never
      },
    },
  },
}
```

Davranış notları:

- gelen kabul edildikten hemen sonra gönderilir (yanıt öncesi)
- hatalar günlüğe kaydedilir ancak normal yanıt teslimatını engellemez
- grup modu `mentions`, bahsetmeyle tetiklenen dönüşlerde tepki verir; grup etkinleştirme `always` bu denetim için baypas görevi görür
- WhatsApp `channels.whatsapp.ackReaction` kullanır (eski `messages.ackReaction` burada kullanılmaz)

## Çoklu hesap ve kimlik bilgileri

<AccordionGroup>
  <Accordion title="Hesap seçimi ve varsayılanlar">
    - hesap kimlikleri `channels.whatsapp.accounts` içinden gelir
    - varsayılan hesap seçimi: varsa `default`, aksi halde ilk yapılandırılmış hesap kimliği (sıralanmış)
    - hesap kimlikleri arama için dahili olarak normalize edilir
  </Accordion>

  <Accordion title="Kimlik bilgisi yolları ve eski sürüm uyumluluğu">
    - geçerli kimlik doğrulama yolu: `~/.openclaw/credentials/whatsapp/<accountId>/creds.json`
    - yedek dosya: `creds.json.bak`
    - `~/.openclaw/credentials/` içindeki eski varsayılan kimlik doğrulama hâlâ tanınır/varsayılan hesap akışları için taşınır
  </Accordion>

  <Accordion title="Oturumu kapatma davranışı">
    `openclaw channels logout --channel whatsapp [--account <id>]`, o hesap için WhatsApp kimlik doğrulama durumunu temizler.

    Eski kimlik doğrulama dizinlerinde, `oauth.json` korunurken Baileys kimlik doğrulama dosyaları kaldırılır.

  </Accordion>
</AccordionGroup>

## Araçlar, eylemler ve yapılandırma yazımları

- Ajan araç desteği WhatsApp tepki eylemini (`react`) içerir.
- Eylem geçitleri:
  - `channels.whatsapp.actions.reactions`
  - `channels.whatsapp.actions.polls`
- Kanal tarafından başlatılan yapılandırma yazımları varsayılan olarak etkindir (`channels.whatsapp.configWrites=false` ile devre dışı bırakın).

## Sorun giderme

<AccordionGroup>
  <Accordion title="Bağlı değil (QR gerekli)">
    Belirti: kanal durumu bağlı olmadığını bildirir.

    Düzeltme:

    ```bash
    openclaw channels login --channel whatsapp
    openclaw channels status
    ```

  </Accordion>

  <Accordion title="Bağlı ama bağlantısı kesilmiş / yeniden bağlanma döngüsü">
    Belirti: tekrar eden bağlantı kesilmeleri veya yeniden bağlanma denemeleri olan bağlı hesap.

    Düzeltme:

    ```bash
    openclaw doctor
    openclaw logs --follow
    ```

    Gerekirse `channels login` ile yeniden bağlayın.

  </Accordion>

  <Accordion title="Gönderimde etkin dinleyici yok">
    Giden gönderimler, hedef hesap için etkin bir gateway dinleyicisi yoksa hızlıca başarısız olur.

    Gateway'in çalıştığından ve hesabın bağlı olduğundan emin olun.

  </Accordion>

  <Accordion title="Grup mesajları beklenmedik şekilde yok sayılıyor">
    Şu sırayla kontrol edin:

    - `groupPolicy`
    - `groupAllowFrom` / `allowFrom`
    - `groups` izin listesi girdileri
    - bahsetme geçidi (`requireMention` + bahsetme kalıpları)
    - `openclaw.json` içindeki yinelenen anahtarlar (JSON5): sonraki girdiler öncekileri geçersiz kılar, bu nedenle kapsam başına tek bir `groupPolicy` tutun

  </Accordion>

  <Accordion title="Bun çalışma zamanı uyarısı">
    WhatsApp gateway çalışma zamanı Node kullanmalıdır. Bun, kararlı WhatsApp/Telegram gateway işlemi için uyumsuz olarak işaretlenmiştir.
  </Accordion>
</AccordionGroup>

## Yapılandırma başvuru işaretçileri

Birincil başvuru:

- [Yapılandırma başvurusu - WhatsApp](/tr/gateway/configuration-reference#whatsapp)

Yüksek sinyalli WhatsApp alanları:

- erişim: `dmPolicy`, `allowFrom`, `groupPolicy`, `groupAllowFrom`, `groups`
- teslimat: `textChunkLimit`, `chunkMode`, `mediaMaxMb`, `sendReadReceipts`, `ackReaction`, `reactionLevel`
- çoklu hesap: `accounts.<id>.enabled`, `accounts.<id>.authDir`, hesap düzeyi geçersiz kılmalar
- operasyonlar: `configWrites`, `debounceMs`, `web.enabled`, `web.heartbeatSeconds`, `web.reconnect.*`
- oturum davranışı: `session.dmScope`, `historyLimit`, `dmHistoryLimit`, `dms.<id>.historyLimit`

## İlgili

- [Eşleştirme](/tr/channels/pairing)
- [Gruplar](/tr/channels/groups)
- [Güvenlik](/tr/gateway/security)
- [Kanal yönlendirme](/tr/channels/channel-routing)
- [Çok ajanlı yönlendirme](/tr/concepts/multi-agent)
- [Sorun giderme](/tr/channels/troubleshooting)
