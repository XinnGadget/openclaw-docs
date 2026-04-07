---
read_when:
    - Slack kuruluyorsa veya Slack socket/HTTP modunda hata ayıklanıyorsa
summary: Slack kurulumu ve çalışma zamanı davranışı (Socket Mode + HTTP Request URLs)
title: Slack
x-i18n:
    generated_at: "2026-04-07T08:44:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2b8fd2cc6c638ee82069f0af2c2b6f6f49c87da709b941433a0343724a9907ea
    source_path: channels/slack.md
    workflow: 15
---

# Slack

Durum: Slack uygulama entegrasyonları üzerinden DM'ler ve kanallar için üretime hazır. Varsayılan mod Socket Mode'dur; HTTP Request URLs de desteklenir.

<CardGroup cols={3}>
  <Card title="Eşleştirme" icon="link" href="/tr/channels/pairing">
    Slack DM'leri varsayılan olarak eşleştirme modunu kullanır.
  </Card>
  <Card title="Slash komutları" icon="terminal" href="/tr/tools/slash-commands">
    Yerel komut davranışı ve komut kataloğu.
  </Card>
  <Card title="Kanal sorun giderme" icon="wrench" href="/tr/channels/troubleshooting">
    Kanallar arası tanılama ve onarım kılavuzları.
  </Card>
</CardGroup>

## Hızlı kurulum

<Tabs>
  <Tab title="Socket Mode (varsayılan)">
    <Steps>
      <Step title="Yeni bir Slack uygulaması oluşturun">
        Slack uygulama ayarlarında **[Create New App](https://api.slack.com/apps/new)** düğmesine basın:

        - **from a manifest** seçeneğini seçin ve uygulamanız için bir çalışma alanı seçin
        - aşağıdaki [örnek manifest](#manifest-and-scope-checklist) içeriğini yapıştırın ve oluşturmaya devam edin
        - `connections:write` ile bir **App-Level Token** (`xapp-...`) oluşturun
        - uygulamayı yükleyin ve gösterilen **Bot Token** (`xoxb-...`) değerini kopyalayın
      </Step>

      <Step title="OpenClaw'ı yapılandırın">

```json5
{
  channels: {
    slack: {
      enabled: true,
      mode: "socket",
      appToken: "xapp-...",
      botToken: "xoxb-...",
    },
  },
}
```

        Ortam değişkeni yedeği (yalnızca varsayılan hesap):

```bash
SLACK_APP_TOKEN=xapp-...
SLACK_BOT_TOKEN=xoxb-...
```

      </Step>

      <Step title="Gateway'i başlatın">

```bash
openclaw gateway
```

      </Step>
    </Steps>

  </Tab>

  <Tab title="HTTP Request URLs">
    <Steps>
      <Step title="Yeni bir Slack uygulaması oluşturun">
        Slack uygulama ayarlarında **[Create New App](https://api.slack.com/apps/new)** düğmesine basın:

        - **from a manifest** seçeneğini seçin ve uygulamanız için bir çalışma alanı seçin
        - [örnek manifest](#manifest-and-scope-checklist) içeriğini yapıştırın ve oluşturmadan önce URL'leri güncelleyin
        - istek doğrulaması için **Signing Secret** değerini kaydedin
        - uygulamayı yükleyin ve gösterilen **Bot Token** (`xoxb-...`) değerini kopyalayın

      </Step>

      <Step title="OpenClaw'ı yapılandırın">

```json5
{
  channels: {
    slack: {
      enabled: true,
      mode: "http",
      botToken: "xoxb-...",
      signingSecret: "your-signing-secret",
      webhookPath: "/slack/events",
    },
  },
}
```

        <Note>
        Çok hesaplı HTTP için benzersiz webhook yolları kullanın

        Kayıtların çakışmaması için her hesaba farklı bir `webhookPath` verin (varsayılan `/slack/events`).
        </Note>

      </Step>

      <Step title="Gateway'i başlatın">

```bash
openclaw gateway
```

      </Step>
    </Steps>

  </Tab>
</Tabs>

## Manifest ve kapsam kontrol listesi

<Tabs>
  <Tab title="Socket Mode (varsayılan)">

```json
{
  "display_information": {
    "name": "OpenClaw",
    "description": "Slack connector for OpenClaw"
  },
  "features": {
    "bot_user": {
      "display_name": "OpenClaw",
      "always_online": true
    },
    "app_home": {
      "messages_tab_enabled": true,
      "messages_tab_read_only_enabled": false
    },
    "slash_commands": [
      {
        "command": "/openclaw",
        "description": "Send a message to OpenClaw",
        "should_escape": false
      }
    ]
  },
  "oauth_config": {
    "scopes": {
      "bot": [
        "app_mentions:read",
        "assistant:write",
        "channels:history",
        "channels:read",
        "chat:write",
        "commands",
        "emoji:read",
        "files:read",
        "files:write",
        "groups:history",
        "groups:read",
        "im:history",
        "im:read",
        "im:write",
        "mpim:history",
        "mpim:read",
        "mpim:write",
        "pins:read",
        "pins:write",
        "reactions:read",
        "reactions:write",
        "users:read"
      ]
    }
  },
  "settings": {
    "socket_mode_enabled": true,
    "event_subscriptions": {
      "bot_events": [
        "app_mention",
        "channel_rename",
        "member_joined_channel",
        "member_left_channel",
        "message.channels",
        "message.groups",
        "message.im",
        "message.mpim",
        "pin_added",
        "pin_removed",
        "reaction_added",
        "reaction_removed"
      ]
    }
  }
}
```

  </Tab>

  <Tab title="HTTP Request URLs">

```json
{
  "display_information": {
    "name": "OpenClaw",
    "description": "Slack connector for OpenClaw"
  },
  "features": {
    "bot_user": {
      "display_name": "OpenClaw",
      "always_online": true
    },
    "app_home": {
      "messages_tab_enabled": true,
      "messages_tab_read_only_enabled": false
    },
    "slash_commands": [
      {
        "command": "/openclaw",
        "description": "Send a message to OpenClaw",
        "should_escape": false,
        "url": "https://gateway-host.example.com/slack/events"
      }
    ]
  },
  "oauth_config": {
    "scopes": {
      "bot": [
        "app_mentions:read",
        "assistant:write",
        "channels:history",
        "channels:read",
        "chat:write",
        "commands",
        "emoji:read",
        "files:read",
        "files:write",
        "groups:history",
        "groups:read",
        "im:history",
        "im:read",
        "im:write",
        "mpim:history",
        "mpim:read",
        "mpim:write",
        "pins:read",
        "pins:write",
        "reactions:read",
        "reactions:write",
        "users:read"
      ]
    }
  },
  "settings": {
    "event_subscriptions": {
      "request_url": "https://gateway-host.example.com/slack/events",
      "bot_events": [
        "app_mention",
        "channel_rename",
        "member_joined_channel",
        "member_left_channel",
        "message.channels",
        "message.groups",
        "message.im",
        "message.mpim",
        "pin_added",
        "pin_removed",
        "reaction_added",
        "reaction_removed"
      ]
    },
    "interactivity": {
      "is_enabled": true,
      "request_url": "https://gateway-host.example.com/slack/events",
      "message_menu_options_url": "https://gateway-host.example.com/slack/events"
    }
  }
}
```

  </Tab>
</Tabs>

<AccordionGroup>
  <Accordion title="İsteğe bağlı yazarlık kapsamları (yazma işlemleri)">
    Giden mesajların varsayılan Slack uygulama kimliği yerine etkin ajan kimliğini (özel kullanıcı adı ve simge) kullanmasını istiyorsanız `chat:write.customize` bot kapsamını ekleyin.

    Bir emoji simgesi kullanıyorsanız Slack `:emoji_name:` sözdizimini bekler.

  </Accordion>
  <Accordion title="İsteğe bağlı kullanıcı belirteci kapsamları (okuma işlemleri)">
    `channels.slack.userToken` yapılandırırsanız tipik okuma kapsamları şunlardır:

    - `channels:history`, `groups:history`, `im:history`, `mpim:history`
    - `channels:read`, `groups:read`, `im:read`, `mpim:read`
    - `users:read`
    - `reactions:read`
    - `pins:read`
    - `emoji:read`
    - `search:read` (Slack arama okumalarına bağımlıysanız)

  </Accordion>
</AccordionGroup>

## Belirteç modeli

- Socket Mode için `botToken` + `appToken` gereklidir.
- HTTP modu `botToken` + `signingSecret` gerektirir.
- `botToken`, `appToken`, `signingSecret` ve `userToken`, düz metin
  dizeleri veya SecretRef nesneleri kabul eder.
- Yapılandırma belirteçleri ortam değişkeni yedeğini geçersiz kılar.
- `SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN` ortam değişkeni yedeği yalnızca varsayılan hesaba uygulanır.
- `userToken` (`xoxp-...`) yalnızca yapılandırmadadır (ortam değişkeni yedeği yoktur) ve varsayılan olarak salt okunur davranış kullanır (`userTokenReadOnly: true`).

Durum anlık görüntüsü davranışı:

- Slack hesap incelemesi, her kimlik bilgisi için `*Source` ve `*Status`
  alanlarını izler (`botToken`, `appToken`, `signingSecret`, `userToken`).
- Durum `available`, `configured_unavailable` veya `missing` olabilir.
- `configured_unavailable`, hesabın SecretRef
  veya başka bir satır içi olmayan gizli kaynak üzerinden yapılandırıldığı,
  ancak mevcut komut/çalışma zamanı yolunun gerçek değeri çözemediği anlamına gelir.
- HTTP modunda `signingSecretStatus` dahil edilir; Socket Mode'da
  gereken ikili `botTokenStatus` + `appTokenStatus` olur.

<Tip>
Eylemler/dizin okumaları için, yapılandırılmışsa kullanıcı belirteci tercih edilebilir. Yazmalar için bot belirteci tercih edilmeye devam eder; kullanıcı belirteciyle yazmaya yalnızca `userTokenReadOnly: false` olduğunda ve bot belirteci kullanılamadığında izin verilir.
</Tip>

## Eylemler ve geçitler

Slack eylemleri `channels.slack.actions.*` ile kontrol edilir.

Geçerli Slack araçlarında kullanılabilir eylem grupları:

| Grup      | Varsayılan |
| ---------- | ------- |
| messages   | etkin |
| reactions  | etkin |
| pins       | etkin |
| memberInfo | etkin |
| emojiList  | etkin |

Geçerli Slack mesaj eylemleri arasında `send`, `upload-file`, `download-file`, `read`, `edit`, `delete`, `pin`, `unpin`, `list-pins`, `member-info` ve `emoji-list` bulunur.

## Erişim kontrolü ve yönlendirme

<Tabs>
  <Tab title="DM ilkesi">
    `channels.slack.dmPolicy`, DM erişimini kontrol eder (eski: `channels.slack.dm.policy`):

    - `pairing` (varsayılan)
    - `allowlist`
    - `open` (`channels.slack.allowFrom` içinde `"*"` bulunmasını gerektirir; eski: `channels.slack.dm.allowFrom`)
    - `disabled`

    DM işaretleri:

    - `dm.enabled` (varsayılan true)
    - `channels.slack.allowFrom` (tercih edilen)
    - `dm.allowFrom` (eski)
    - `dm.groupEnabled` (grup DM'leri varsayılan olarak false)
    - `dm.groupChannels` (isteğe bağlı MPIM izin listesi)

    Çok hesaplı öncelik:

    - `channels.slack.accounts.default.allowFrom` yalnızca `default` hesabına uygulanır.
    - Adlandırılmış hesaplar, kendi `allowFrom` değerleri ayarlanmamışsa `channels.slack.allowFrom` değerini devralır.
    - Adlandırılmış hesaplar `channels.slack.accounts.default.allowFrom` değerini devralmaz.

    DM'lerde eşleştirme `openclaw pairing approve slack <code>` kullanır.

  </Tab>

  <Tab title="Kanal ilkesi">
    `channels.slack.groupPolicy`, kanal işlemeyi kontrol eder:

    - `open`
    - `allowlist`
    - `disabled`

    Kanal izin listesi `channels.slack.channels` altında bulunur ve kararlı kanal kimlikleri kullanmalıdır.

    Çalışma zamanı notu: `channels.slack` tamamen eksikse (yalnızca ortam değişkenli kurulum), çalışma zamanı `groupPolicy="allowlist"` değerine geri döner ve bir uyarı kaydeder (`channels.defaults.groupPolicy` ayarlanmış olsa bile).

    Ad/kimlik çözümleme:

    - kanal izin listesi girişleri ve DM izin listesi girişleri, belirteç erişimi izin verdiğinde başlangıçta çözümlenir
    - çözümlenmemiş kanal adı girişleri yapılandırıldığı gibi tutulur ancak varsayılan olarak yönlendirme için yok sayılır
    - gelen yetkilendirme ve kanal yönlendirme varsayılan olarak önce kimlik kullanır; doğrudan kullanıcı adı/slug eşleştirmesi için `channels.slack.dangerouslyAllowNameMatching: true` gerekir

  </Tab>

  <Tab title="Bahsetmeler ve kanal kullanıcıları">
    Kanal mesajları varsayılan olarak bahsetme geçidiyle korunur.

    Bahsetme kaynakları:

    - açık uygulama bahsetmesi (`<@botId>`)
    - bahsetme regex desenleri (`agents.list[].groupChat.mentionPatterns`, yedek olarak `messages.groupChat.mentionPatterns`)
    - örtük botta yanıt dizisi davranışı (`thread.requireExplicitMention` `true` olduğunda devre dışıdır)

    Kanal başına kontroller (`channels.slack.channels.<id>`; adlar yalnızca başlangıç çözümlemesi veya `dangerouslyAllowNameMatching` ile):

    - `requireMention`
    - `users` (izin listesi)
    - `allowBots`
    - `skills`
    - `systemPrompt`
    - `tools`, `toolsBySender`
    - `toolsBySender` anahtar biçimi: `id:`, `e164:`, `username:`, `name:` veya `"*"` joker karakteri
      (eski ön eksiz anahtarlar yine de yalnızca `id:` ile eşlenir)

  </Tab>
</Tabs>

## Diziler, oturumlar ve yanıt etiketleri

- DM'ler `direct` olarak; kanallar `channel` olarak; MPIM'ler `group` olarak yönlendirilir.
- Varsayılan `session.dmScope=main` ile Slack DM'leri ajan ana oturumunda birleştirilir.
- Kanal oturumları: `agent:<agentId>:slack:channel:<channelId>`.
- Dizi yanıtları, uygun olduğunda dizi oturumu sonekleri (`:thread:<threadTs>`) oluşturabilir.
- `channels.slack.thread.historyScope` varsayılanı `thread`; `thread.inheritParent` varsayılanı `false` değeridir.
- `channels.slack.thread.initialHistoryLimit`, yeni bir dizi oturumu başladığında kaç mevcut dizi mesajının alınacağını kontrol eder (varsayılan `20`; devre dışı bırakmak için `0` ayarlayın).
- `channels.slack.thread.requireExplicitMention` (varsayılan `false`): `true` olduğunda örtük dizi bahsetmelerini bastırır; böylece bot, diziler içinde yalnızca açık `@bot` bahsetmelerine yanıt verir, bot dizide zaten yer almış olsa bile. Bu olmadan, botun katıldığı bir dizideki yanıtlar `requireMention` geçidini atlar.

Yanıt dizileme denetimleri:

- `channels.slack.replyToMode`: `off|first|all|batched` (varsayılan `off`)
- `channels.slack.replyToModeByChatType`: `direct|group|channel` başına
- doğrudan sohbetler için eski yedek: `channels.slack.dm.replyToMode`

Elle yanıt etiketleri desteklenir:

- `[[reply_to_current]]`
- `[[reply_to:<id>]]`

Not: `replyToMode="off"`, açık `[[reply_to_*]]` etiketleri dahil Slack'teki **tüm** yanıt dizilemesini devre dışı bırakır. Bu, açık etiketlerin `"off"` modunda yine de dikkate alındığı Telegram'dan farklıdır. Fark, platformların dizi modellerini yansıtır: Slack dizileri mesajları kanaldan gizlerken Telegram yanıtları ana sohbet akışında görünür kalır.

## Onay reaksiyonları

`ackReaction`, OpenClaw gelen bir mesajı işlerken bir onay emojisi gönderir.

Çözümleme sırası:

- `channels.slack.accounts.<accountId>.ackReaction`
- `channels.slack.ackReaction`
- `messages.ackReaction`
- ajan kimliği emoji yedeği (`agents.list[].identity.emoji`, yoksa "👀")

Notlar:

- Slack kısa kodlar bekler (örneğin `"eyes"`).
- Slack hesabı veya genel olarak reaksiyonu devre dışı bırakmak için `""` kullanın.

## Metin akışı

`channels.slack.streaming`, canlı önizleme davranışını kontrol eder:

- `off`: canlı önizleme akışını devre dışı bırakır.
- `partial` (varsayılan): önizleme metnini en son kısmi çıktıyla değiştirir.
- `block`: parçalı önizleme güncellemeleri ekler.
- `progress`: üretim sırasında ilerleme durumu metni gösterir, ardından son metni gönderir.

`channels.slack.nativeStreaming`, `streaming` değeri `partial` olduğunda Slack yerel metin akışını kontrol eder (varsayılan: `true`).

- Yerel metin akışının görünmesi için bir yanıt dizisi kullanılabilir olmalıdır. Dizi seçimi yine de `replyToMode` değerini izler. Böyle bir dizi yoksa normal taslak önizleme kullanılır.
- Medya ve metin dışı yükler normal teslimata geri döner.
- Akış yanıt ortasında başarısız olursa OpenClaw kalan yükler için normal teslimata geri döner.

Slack yerel metin akışı yerine taslak önizleme kullanın:

```json5
{
  channels: {
    slack: {
      streaming: "partial",
      nativeStreaming: false,
    },
  },
}
```

Eski anahtarlar:

- `channels.slack.streamMode` (`replace | status_final | append`) otomatik olarak `channels.slack.streaming` değerine taşınır.
- boolean `channels.slack.streaming`, otomatik olarak `channels.slack.nativeStreaming` değerine taşınır.

## Yazıyor reaksiyonu yedeği

`typingReaction`, OpenClaw bir yanıtı işlerken gelen Slack mesajına geçici bir reaksiyon ekler, ardından çalıştırma bittiğinde bunu kaldırır. Bu en çok, varsayılan "is typing..." durum göstergesini kullanan dizi yanıtları dışında faydalıdır.

Çözümleme sırası:

- `channels.slack.accounts.<accountId>.typingReaction`
- `channels.slack.typingReaction`

Notlar:

- Slack kısa kodlar bekler (örneğin `"hourglass_flowing_sand"`).
- Reaksiyon en iyi çabayla uygulanır ve yanıt veya hata yolu tamamlandıktan sonra temizleme otomatik olarak denenir.

## Medya, parçalara ayırma ve teslimat

<AccordionGroup>
  <Accordion title="Gelen ekler">
    Slack dosya ekleri, Slack tarafından barındırılan özel URL'lerden (belirteç kimlik doğrulamalı istek akışı) indirilir ve alma başarılı olduğunda ve boyut sınırları izin verdiğinde medya deposuna yazılır.

    Çalışma zamanındaki gelen boyut sınırı, `channels.slack.mediaMaxMb` ile geçersiz kılınmadıkça varsayılan olarak `20MB` değeridir.

  </Accordion>

  <Accordion title="Giden metin ve dosyalar">
    - metin parçaları `channels.slack.textChunkLimit` kullanır (varsayılan 4000)
    - `channels.slack.chunkMode="newline"` paragraf öncelikli bölmeyi etkinleştirir
    - dosya gönderimleri Slack yükleme API'lerini kullanır ve dizi yanıtlarını (`thread_ts`) içerebilir
    - giden medya sınırı, yapılandırılmışsa `channels.slack.mediaMaxMb` değerini izler; aksi halde kanal gönderimleri medya işlem hattından MIME türü varsayılanlarını kullanır
  </Accordion>

  <Accordion title="Teslimat hedefleri">
    Tercih edilen açık hedefler:

    - DM'ler için `user:<id>`
    - kanallar için `channel:<id>`

    Slack DM'leri, kullanıcı hedeflerine gönderim yapılırken Slack konuşma API'leri aracılığıyla açılır.

  </Accordion>
</AccordionGroup>

## Komutlar ve slash davranışı

- Yerel komut otomatik modu Slack için **kapalıdır** (`commands.native: "auto"` Slack yerel komutlarını etkinleştirmez).
- Yerel Slack komut işleyicilerini `channels.slack.commands.native: true` (veya genel `commands.native: true`) ile etkinleştirin.
- Yerel komutlar etkinleştirildiğinde, eşleşen slash komutlarını Slack'te (`/<command>` adlarıyla) kaydedin; tek istisna:
  - durum komutu için `/agentstatus` kaydedin (Slack `/status` komutunu ayırır)
- Yerel komutlar etkin değilse, `channels.slack.slashCommand` aracılığıyla tek bir yapılandırılmış slash komutu çalıştırabilirsiniz.
- Yerel argüman menüleri artık işleme stratejilerini uyarlıyor:
  - 5 seçeneğe kadar: düğme blokları
  - 6-100 seçenek: statik seçim menüsü
  - 100'den fazla seçenek: etkileşim seçenek işleyicileri mevcut olduğunda eşzamansız seçenek filtrelemeli harici seçim
  - kodlanmış seçenek değerleri Slack sınırlarını aşarsa akış düğmelere geri döner
- Uzun seçenek yükleri için Slash komutu argüman menüleri, seçilen değeri göndermeden önce bir onay iletişim kutusu kullanır.

Varsayılan slash komutu ayarları:

- `enabled: false`
- `name: "openclaw"`
- `sessionPrefix: "slack:slash"`
- `ephemeral: true`

Slash oturumları yalıtılmış anahtarlar kullanır:

- `agent:<agentId>:slack:slash:<userId>`

ve yine de komut yürütmesini hedef konuşma oturumuna göre yönlendirir (`CommandTargetSessionKey`).

## Etkileşimli yanıtlar

Slack, ajan tarafından yazılmış etkileşimli yanıt denetimlerini işleyebilir, ancak bu özellik varsayılan olarak devre dışıdır.

Bunu genel olarak etkinleştirin:

```json5
{
  channels: {
    slack: {
      capabilities: {
        interactiveReplies: true,
      },
    },
  },
}
```

Veya yalnızca bir Slack hesabı için etkinleştirin:

```json5
{
  channels: {
    slack: {
      accounts: {
        ops: {
          capabilities: {
            interactiveReplies: true,
          },
        },
      },
    },
  },
}
```

Etkinleştirildiğinde, ajanlar yalnızca Slack'e özel yanıt yönergeleri üretebilir:

- `[[slack_buttons: Approve:approve, Reject:reject]]`
- `[[slack_select: Choose a target | Canary:canary, Production:production]]`

Bu yönergeler Slack Block Kit içine derlenir ve tıklamaları veya seçimleri mevcut Slack etkileşim olay yolu üzerinden geri yönlendirir.

Notlar:

- Bu, Slack'e özgü bir kullanıcı arayüzüdür. Diğer kanallar, Slack Block Kit yönergelerini kendi düğme sistemlerine çevirmez.
- Etkileşimli geri çağrı değerleri, ham ajan tarafından yazılmış değerler değil, OpenClaw tarafından oluşturulmuş opak belirteçlerdir.
- Üretilen etkileşimli bloklar Slack Block Kit sınırlarını aşarsa OpenClaw geçersiz bir blocks yükü göndermek yerine özgün metin yanıtına geri döner.

## Slack'te exec onayları

Slack, Web UI veya terminale geri dönmek yerine, etkileşimli düğmeler ve etkileşimlerle yerel bir onay istemcisi olarak çalışabilir.

- Exec onayları, yerel DM/kanal yönlendirmesi için `channels.slack.execApprovals.*` kullanır.
- Eklenti onayları, istek zaten Slack'e ulaşıyorsa ve onay kimliği türü `plugin:` ise aynı Slack yerel düğme yüzeyi üzerinden yine çözülebilir.
- Onaylayıcı yetkilendirmesi yine de uygulanır: yalnızca onaylayıcı olarak tanımlanan kullanıcılar Slack üzerinden istekleri onaylayabilir veya reddedebilir.

Bu, diğer kanallarla aynı paylaşılan onay düğmesi yüzeyini kullanır. Slack uygulama ayarlarınızda `interactivity` etkinleştirildiğinde, onay istemleri doğrudan konuşma içinde Block Kit düğmeleri olarak işlenir.
Bu düğmeler mevcut olduğunda birincil onay kullanıcı deneyimi bunlar olur; OpenClaw,
araç sonucu sohbet onaylarının kullanılamadığını söylemediği veya tek yol manuel onay olmadığı sürece
yalnızca manuel bir `/approve` komutu eklemelidir.

Yapılandırma yolu:

- `channels.slack.execApprovals.enabled`
- `channels.slack.execApprovals.approvers` (isteğe bağlı; mümkün olduğunda `commands.ownerAllowFrom` değerine geri döner)
- `channels.slack.execApprovals.target` (`dm` | `channel` | `both`, varsayılan: `dm`)
- `agentFilter`, `sessionFilter`

Slack, `enabled` ayarlanmamış veya `"auto"` olduğunda ve en az bir
onaylayıcı çözümlendiğinde yerel exec onaylarını otomatik etkinleştirir. Slack'i yerel onay istemcisi olarak açıkça devre dışı bırakmak için `enabled: false` ayarlayın.
Onaylayıcılar çözümlendiğinde yerel onayları zorla açmak için `enabled: true` ayarlayın.

Açık Slack exec onay yapılandırması olmayan varsayılan davranış:

```json5
{
  commands: {
    ownerAllowFrom: ["slack:U12345678"],
  },
}
```

Açık Slack yerel yapılandırması yalnızca onaylayıcıları geçersiz kılmak, filtre eklemek veya
kaynak sohbet teslimatına katılmak istediğinizde gerekir:

```json5
{
  channels: {
    slack: {
      execApprovals: {
        enabled: true,
        approvers: ["U12345678"],
        target: "both",
      },
    },
  },
}
```

Paylaşılan `approvals.exec` yönlendirmesi ayrıdır. Bunu yalnızca exec onay istemleri ayrıca
başka sohbetlere veya açık bant dışı hedeflere yönlendirilmeliyse kullanın. Paylaşılan `approvals.plugin` yönlendirmesi de
ayrıdır; Slack yerel düğmeleri bu istekler zaten
Slack'e ulaşmışsa eklenti onaylarını yine çözebilir.

Aynı sohbet içi `/approve`, komutları zaten destekleyen Slack kanalları ve DM'lerinde de çalışır. Tüm onay yönlendirme modeli için [Exec approvals](/tr/tools/exec-approvals) bölümüne bakın.

## Olaylar ve operasyonel davranış

- Mesaj düzenlemeleri/silmeleri/dizi yayınları sistem olaylarına eşlenir.
- Reaksiyon ekleme/kaldırma olayları sistem olaylarına eşlenir.
- Üye katılma/ayrılma, kanal oluşturma/yeniden adlandırma ve sabitleme ekleme/kaldırma olayları sistem olaylarına eşlenir.
- `channel_id_changed`, `configWrites` etkin olduğunda kanal yapılandırma anahtarlarını taşıyabilir.
- Kanal topic/purpose meta verisi güvenilmeyen bağlam olarak değerlendirilir ve yönlendirme bağlamına enjekte edilebilir.
- Dizi başlatıcısı ve ilk dizi geçmişi bağlam tohumlaması, uygun olduğunda yapılandırılmış gönderici izin listelerine göre filtrelenir.
- Blok eylemleri ve modal etkileşimler, zengin yük alanlarıyla yapılandırılmış `Slack interaction: ...` sistem olayları üretir:
  - blok eylemleri: seçilen değerler, etiketler, seçici değerleri ve `workflow_*` meta verisi
  - yönlendirilmiş kanal meta verisi ve form girdileriyle modal `view_submission` ve `view_closed` olayları

## Yapılandırma başvurusu işaretçileri

Birincil başvuru:

- [Configuration reference - Slack](/tr/gateway/configuration-reference#slack)

  Yüksek sinyalli Slack alanları:
  - mod/kimlik doğrulama: `mode`, `botToken`, `appToken`, `signingSecret`, `webhookPath`, `accounts.*`
  - DM erişimi: `dm.enabled`, `dmPolicy`, `allowFrom` (eski: `dm.policy`, `dm.allowFrom`), `dm.groupEnabled`, `dm.groupChannels`
  - uyumluluk anahtarı: `dangerouslyAllowNameMatching` (son çare; gerekmedikçe kapalı tutun)
  - kanal erişimi: `groupPolicy`, `channels.*`, `channels.*.users`, `channels.*.requireMention`
  - dizi/geçmiş: `replyToMode`, `replyToModeByChatType`, `thread.*`, `historyLimit`, `dmHistoryLimit`, `dms.*.historyLimit`
  - teslimat: `textChunkLimit`, `chunkMode`, `mediaMaxMb`, `streaming`, `nativeStreaming`
  - işlemler/özellikler: `configWrites`, `commands.native`, `slashCommand.*`, `actions.*`, `userToken`, `userTokenReadOnly`

## Sorun giderme

<AccordionGroup>
  <Accordion title="Kanallarda yanıt yok">
    Sırayla şunları kontrol edin:

    - `groupPolicy`
    - kanal izin listesi (`channels.slack.channels`)
    - `requireMention`
    - kanal başına `users` izin listesi

    Yararlı komutlar:

```bash
openclaw channels status --probe
openclaw logs --follow
openclaw doctor
```

  </Accordion>

  <Accordion title="DM mesajları yok sayılıyor">
    Kontrol edin:

    - `channels.slack.dm.enabled`
    - `channels.slack.dmPolicy` (veya eski `channels.slack.dm.policy`)
    - eşleştirme onayları / izin listesi girdileri

```bash
openclaw pairing list slack
```

  </Accordion>

  <Accordion title="Socket mode bağlanmıyor">
    Slack uygulama ayarlarında bot + uygulama belirteçlerini ve Socket Mode etkinliğini doğrulayın.

    `openclaw channels status --probe --json`, `botTokenStatus` veya
    `appTokenStatus: "configured_unavailable"` gösteriyorsa, Slack hesabı
    yapılandırılmıştır ancak mevcut çalışma zamanı SecretRef destekli
    değeri çözememiştir.

  </Accordion>

  <Accordion title="HTTP mode olay almıyor">
    Şunları doğrulayın:

    - signing secret
    - webhook yolu
    - Slack Request URLs (Events + Interactivity + Slash Commands)
    - HTTP hesap başına benzersiz `webhookPath`

    Hesap anlık görüntülerinde `signingSecretStatus: "configured_unavailable"`
    görünüyorsa, HTTP hesabı yapılandırılmıştır ancak mevcut çalışma zamanı
    SecretRef destekli signing secret değerini çözememiştir.

  </Accordion>

  <Accordion title="Yerel/slash komutları çalışmıyor">
    Neyi amaçladığınızı doğrulayın:

    - Slack'te eşleşen slash komutları kaydedilmiş yerel komut modu (`channels.slack.commands.native: true`)
    - veya tek slash komutu modu (`channels.slack.slashCommand.enabled: true`)

    Ayrıca `commands.useAccessGroups` ile kanal/kullanıcı izin listelerini de kontrol edin.

  </Accordion>
</AccordionGroup>

## İlgili

- [Eşleştirme](/tr/channels/pairing)
- [Gruplar](/tr/channels/groups)
- [Güvenlik](/tr/gateway/security)
- [Kanal yönlendirme](/tr/channels/channel-routing)
- [Sorun giderme](/tr/channels/troubleshooting)
- [Yapılandırma](/tr/gateway/configuration)
- [Slash komutları](/tr/tools/slash-commands)
