---
read_when:
    - Slack kurarken veya Slack socket/HTTP modunda hata ayıklarken
summary: Slack kurulumu ve çalışma zamanı davranışı (Socket Mode + HTTP Request URL'leri)
title: Slack
x-i18n:
    generated_at: "2026-04-06T08:50:09Z"
    model: gpt-5.4
    provider: openai
    source_hash: 897001c13d400cc8387a27000b82dd4c0512b2b88e2fe47785634aed8b7ab7af
    source_path: channels/slack.md
    workflow: 15
---

# Slack

Durum: Slack uygulama entegrasyonları üzerinden DM'ler ve kanallar için üretime hazır. Varsayılan mod Socket Mode'dur; HTTP Request URL'leri de desteklenir.

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
      <Step title="Slack uygulaması ve token'lar oluşturun">
        Slack uygulama ayarlarında:

        - **Socket Mode** etkinleştirin
        - `connections:write` ile **App Token** (`xapp-...`) oluşturun
        - uygulamayı yükleyin ve **Bot Token** (`xoxb-...`) kopyalayın
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

      <Step title="Uygulama olaylarına abone olun">
        Şunlar için bot olaylarına abone olun:

        - `app_mention`
        - `message.channels`, `message.groups`, `message.im`, `message.mpim`
        - `reaction_added`, `reaction_removed`
        - `member_joined_channel`, `member_left_channel`
        - `channel_rename`
        - `pin_added`, `pin_removed`

        Ayrıca DM'ler için App Home **Messages Tab** özelliğini etkinleştirin.
      </Step>

      <Step title="Gateway'i başlatın">

```bash
openclaw gateway
```

      </Step>
    </Steps>

  </Tab>

  <Tab title="HTTP Request URL'leri">
    <Steps>
      <Step title="Slack uygulamasını HTTP için yapılandırın">

        - modu HTTP olarak ayarlayın (`channels.slack.mode="http"`)
        - Slack **Signing Secret** değerini kopyalayın
        - Event Subscriptions + Interactivity + Slash command Request URL değerini aynı webhook yoluna ayarlayın (varsayılan `/slack/events`)

      </Step>

      <Step title="OpenClaw HTTP modunu yapılandırın">

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

      </Step>

      <Step title="Çoklu hesap HTTP için benzersiz webhook yolları kullanın">
        Hesap başına HTTP modu desteklenir.

        Kayıtların çakışmaması için her hesaba farklı bir `webhookPath` verin.
      </Step>
    </Steps>

  </Tab>
</Tabs>

## Manifest ve kapsam denetim listesi

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

  <Tab title="HTTP Request URL'leri">

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
    Giden mesajların varsayılan Slack uygulaması kimliği yerine etkin ajan kimliğini (özel kullanıcı adı ve simge) kullanmasını istiyorsanız `chat:write.customize` bot kapsamını ekleyin.

    Bir emoji simgesi kullanıyorsanız Slack `:emoji_name:` söz dizimini bekler.

  </Accordion>
  <Accordion title="İsteğe bağlı kullanıcı token kapsamları (okuma işlemleri)">
    `channels.slack.userToken` yapılandırırsanız, tipik okuma kapsamları şunlardır:

    - `channels:history`, `groups:history`, `im:history`, `mpim:history`
    - `channels:read`, `groups:read`, `im:read`, `mpim:read`
    - `users:read`
    - `reactions:read`
    - `pins:read`
    - `emoji:read`
    - `search:read` (Slack arama okumalarına bağımlıysanız)

  </Accordion>
</AccordionGroup>

## Token modeli

- Socket Mode için `botToken` + `appToken` gereklidir.
- HTTP modu `botToken` + `signingSecret` gerektirir.
- `botToken`, `appToken`, `signingSecret` ve `userToken`, düz metin
  dizelerini veya SecretRef nesnelerini kabul eder.
- Yapılandırma token'ları ortam değişkeni yedeğinin önüne geçer.
- `SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN` ortam değişkeni yedeği yalnızca varsayılan hesap için geçerlidir.
- `userToken` (`xoxp-...`) yalnızca yapılandırmadadır (ortam değişkeni yedeği yoktur) ve varsayılan olarak salt okunur davranış kullanır (`userTokenReadOnly: true`).

Durum anlık görüntüsü davranışı:

- Slack hesap incelemesi, kimlik bilgisi başına `*Source` ve `*Status`
  alanlarını (`botToken`, `appToken`, `signingSecret`, `userToken`) izler.
- Durum `available`, `configured_unavailable` veya `missing` olur.
- `configured_unavailable`, hesabın SecretRef
  veya satır içi olmayan başka bir gizli kaynak üzerinden yapılandırıldığı,
  ancak mevcut komut/çalışma zamanı yolunun gerçek değeri çözemediği anlamına gelir.
- HTTP modunda `signingSecretStatus` eklenir; Socket Mode'da gerekli
  ikili `botTokenStatus` + `appTokenStatus` olur.

<Tip>
Eylemler/dizin okumaları için, yapılandırılmışsa kullanıcı token'ı tercih edilebilir. Yazma işlemleri için bot token'ı tercih edilmeye devam eder; kullanıcı token'ı ile yazmaya yalnızca `userTokenReadOnly: false` olduğunda ve bot token'ı kullanılamadığında izin verilir.
</Tip>

## Eylemler ve geçitler

Slack eylemleri `channels.slack.actions.*` tarafından denetlenir.

Mevcut Slack araçlarında kullanılabilen eylem grupları:

| Grup      | Varsayılan |
| ---------- | ------- |
| messages   | etkin |
| reactions  | etkin |
| pins       | etkin |
| memberInfo | etkin |
| emojiList  | etkin |

Mevcut Slack mesaj eylemleri `send`, `upload-file`, `download-file`, `read`, `edit`, `delete`, `pin`, `unpin`, `list-pins`, `member-info` ve `emoji-list` öğelerini içerir.

## Erişim denetimi ve yönlendirme

<Tabs>
  <Tab title="DM ilkesi">
    `channels.slack.dmPolicy`, DM erişimini denetler (eski: `channels.slack.dm.policy`):

    - `pairing` (varsayılan)
    - `allowlist`
    - `open` (`channels.slack.allowFrom` içinde `"*"` bulunmasını gerektirir; eski: `channels.slack.dm.allowFrom`)
    - `disabled`

    DM bayrakları:

    - `dm.enabled` (varsayılan true)
    - `channels.slack.allowFrom` (tercih edilen)
    - `dm.allowFrom` (eski)
    - `dm.groupEnabled` (grup DM'leri varsayılan olarak false)
    - `dm.groupChannels` (isteğe bağlı MPIM izin listesi)

    Çoklu hesap önceliği:

    - `channels.slack.accounts.default.allowFrom` yalnızca `default` hesabına uygulanır.
    - Adlandırılmış hesaplar, kendi `allowFrom` değerleri ayarlı değilse `channels.slack.allowFrom` değerini devralır.
    - Adlandırılmış hesaplar `channels.slack.accounts.default.allowFrom` değerini devralmaz.

    DM'lerde eşleştirme `openclaw pairing approve slack <code>` kullanır.

  </Tab>

  <Tab title="Kanal ilkesi">
    `channels.slack.groupPolicy`, kanal işlemesini denetler:

    - `open`
    - `allowlist`
    - `disabled`

    Kanal izin listesi `channels.slack.channels` altında bulunur ve kararlı kanal kimliklerini kullanmalıdır.

    Çalışma zamanı notu: `channels.slack` tamamen eksikse (yalnızca ortam değişkeni kurulumu), çalışma zamanı `groupPolicy="allowlist"` değerine geri döner ve bir uyarı günlüğe kaydeder (`channels.defaults.groupPolicy` ayarlanmış olsa bile).

    Ad/kimlik çözümleme:

    - kanal izin listesi girdileri ve DM izin listesi girdileri, token erişimi izin verdiğinde başlangıçta çözümlenir
    - çözümlenmemiş kanal adı girdileri yapılandırıldığı gibi tutulur ancak varsayılan olarak yönlendirme için yok sayılır
    - gelen yetkilendirme ve kanal yönlendirme varsayılan olarak önce kimlik ile yapılır; doğrudan kullanıcı adı/slug eşleştirmesi için `channels.slack.dangerouslyAllowNameMatching: true` gerekir

  </Tab>

  <Tab title="Bahsetmeler ve kanal kullanıcıları">
    Kanal mesajları varsayılan olarak bahsetme ile geçitlenir.

    Bahsetme kaynakları:

    - açık uygulama bahsetmesi (`<@botId>`)
    - bahsetme regex desenleri (`agents.list[].groupChat.mentionPatterns`, geri dönüş olarak `messages.groupChat.mentionPatterns`)
    - örtük bottan-yanıta iş parçacığı davranışı

    Kanal başına denetimler (`channels.slack.channels.<id>`; adlar yalnızca başlangıç çözümlemesi veya `dangerouslyAllowNameMatching` ile):

    - `requireMention`
    - `users` (izin listesi)
    - `allowBots`
    - `skills`
    - `systemPrompt`
    - `tools`, `toolsBySender`
    - `toolsBySender` anahtar biçimi: `id:`, `e164:`, `username:`, `name:` veya `"*"` joker karakteri
      (eski ön ek kullanılmayan anahtarlar hâlâ yalnızca `id:` olarak eşlenir)

  </Tab>
</Tabs>

## İş parçacıkları, oturumlar ve yanıt etiketleri

- DM'ler `direct`, kanallar `channel`, MPIM'ler `group` olarak yönlendirilir.
- Varsayılan `session.dmScope=main` ile Slack DM'leri ajan ana oturumuna daraltılır.
- Kanal oturumları: `agent:<agentId>:slack:channel:<channelId>`.
- İş parçacığı yanıtları, gerektiğinde iş parçacığı oturum son ekleri (`:thread:<threadTs>`) oluşturabilir.
- `channels.slack.thread.historyScope` varsayılan olarak `thread`; `thread.inheritParent` varsayılan olarak `false` olur.
- `channels.slack.thread.initialHistoryLimit`, yeni bir iş parçacığı oturumu başladığında kaç mevcut iş parçacığı mesajının getirileceğini denetler (varsayılan `20`; devre dışı bırakmak için `0` ayarlayın).

Yanıt iş parçacığı denetimleri:

- `channels.slack.replyToMode`: `off|first|all|batched` (varsayılan `off`)
- `channels.slack.replyToModeByChatType`: her `direct|group|channel` için
- doğrudan sohbetler için eski geri dönüş: `channels.slack.dm.replyToMode`

Elle yanıt etiketleri desteklenir:

- `[[reply_to_current]]`
- `[[reply_to:<id>]]`

Not: `replyToMode="off"`, açık `[[reply_to_*]]` etiketleri dahil Slack'teki **tüm** yanıt iş parçacıklarını devre dışı bırakır. Bu durum, açık etiketlerin `"off"` modunda hâlâ dikkate alındığı Telegram'dan farklıdır. Fark, platform iş parçacığı modellerini yansıtır: Slack iş parçacıkları mesajları kanaldan gizlerken Telegram yanıtları ana sohbet akışında görünür kalır.

## Ack reaksiyonları

`ackReaction`, OpenClaw gelen bir mesajı işlerken bir onay emojisi gönderir.

Çözümleme sırası:

- `channels.slack.accounts.<accountId>.ackReaction`
- `channels.slack.ackReaction`
- `messages.ackReaction`
- ajan kimliği emoji geri dönüşü (`agents.list[].identity.emoji`, aksi halde "👀")

Notlar:

- Slack kısa kod bekler (örneğin `"eyes"`).
- Slack hesabı için veya genel olarak reaksiyonu devre dışı bırakmak üzere `""` kullanın.

## Metin akışı

`channels.slack.streaming`, canlı önizleme davranışını denetler:

- `off`: canlı önizleme akışını devre dışı bırakır.
- `partial` (varsayılan): önizleme metnini en son kısmi çıktı ile değiştirir.
- `block`: parça parça önizleme güncellemeleri ekler.
- `progress`: oluşturma sırasında ilerleme durum metni gösterir, ardından son metni gönderir.

`channels.slack.nativeStreaming`, `streaming` değeri `partial` olduğunda Slack yerel metin akışını denetler (varsayılan: `true`).

- Yerel metin akışının görünmesi için bir yanıt iş parçacığının kullanılabilir olması gerekir. İş parçacığı seçimi yine `replyToMode` kurallarını izler. Bu olmadan normal taslak önizleme kullanılır.
- Medya ve metin dışı yükler normal teslimata geri döner.
- Akış yanıtın ortasında başarısız olursa OpenClaw, kalan yükler için normal teslimata geri döner.

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
- boolean `channels.slack.streaming` otomatik olarak `channels.slack.nativeStreaming` değerine taşınır.

## Yazma reaksiyonu geri dönüşü

`typingReaction`, OpenClaw bir yanıtı işlerken gelen Slack mesajına geçici bir reaksiyon ekler, ardından çalışma bittiğinde bunu kaldırır. Bu özellikle varsayılan "is typing..." durum göstergesini kullanan iş parçacığı yanıtları dışında yararlıdır.

Çözümleme sırası:

- `channels.slack.accounts.<accountId>.typingReaction`
- `channels.slack.typingReaction`

Notlar:

- Slack kısa kod bekler (örneğin `"hourglass_flowing_sand"`).
- Reaksiyon en iyi çaba esaslıdır ve yanıt veya hata yolu tamamlandıktan sonra temizleme otomatik olarak denenir.

## Medya, parçalara ayırma ve teslimat

<AccordionGroup>
  <Accordion title="Gelen ekler">
    Slack dosya ekleri, Slack tarafından barındırılan özel URL'lerden (token kimlik doğrulamalı istek akışı) indirilir ve getirme başarılı olduğunda ve boyut sınırları izin verdiğinde medya deposuna yazılır.

    Çalışma zamanı gelen boyut üst sınırı, `channels.slack.mediaMaxMb` ile geçersiz kılınmadıkça varsayılan olarak `20MB` olur.

  </Accordion>

  <Accordion title="Giden metin ve dosyalar">
    - metin parçaları `channels.slack.textChunkLimit` kullanır (varsayılan 4000)
    - `channels.slack.chunkMode="newline"` paragraf öncelikli bölmeyi etkinleştirir
    - dosya gönderimleri Slack yükleme API'lerini kullanır ve iş parçacığı yanıtlarını (`thread_ts`) içerebilir
    - giden medya üst sınırı, yapılandırılmışsa `channels.slack.mediaMaxMb` değerini izler; aksi halde kanal gönderimleri medya işlem hattındaki MIME türü varsayılanlarını kullanır
  </Accordion>

  <Accordion title="Teslimat hedefleri">
    Tercih edilen açık hedefler:

    - DM'ler için `user:<id>`
    - kanallar için `channel:<id>`

    Slack DM'leri, kullanıcı hedeflerine gönderim yapılırken Slack konuşma API'leri üzerinden açılır.

  </Accordion>
</AccordionGroup>

## Komutlar ve slash davranışı

- Yerel komut otomatik modu Slack için **kapalıdır** (`commands.native: "auto"`, Slack yerel komutlarını etkinleştirmez).
- Yerel Slack komut işleyicilerini `channels.slack.commands.native: true` (veya genel `commands.native: true`) ile etkinleştirin.
- Yerel komutlar etkinleştirildiğinde, bir istisna dışında Slack'te eşleşen slash komutlarını (`/<command>` adları) kaydedin:
  - durum komutu için `/agentstatus` kaydedin (Slack `/status` komutunu ayırır)
- Yerel komutlar etkin değilse, `channels.slack.slashCommand` üzerinden tek bir yapılandırılmış slash komutu çalıştırabilirsiniz.
- Yerel argüman menüleri artık işleme stratejilerini uyarlıyor:
  - en fazla 5 seçenek: düğme blokları
  - 6-100 seçenek: statik seçim menüsü
  - 100'den fazla seçenek: etkileşim seçenek işleyicileri kullanılabiliyorsa eşzamansız seçenek filtreleme ile harici seçim
  - kodlanmış seçenek değerleri Slack sınırlarını aşarsa akış düğmelere geri döner
- Uzun seçenek yüklerinde, Slash komutu argüman menüleri seçilen bir değeri göndermeden önce onay iletişim kutusu kullanır.

Varsayılan slash komutu ayarları:

- `enabled: false`
- `name: "openclaw"`
- `sessionPrefix: "slack:slash"`
- `ephemeral: true`

Slash oturumları yalıtılmış anahtarlar kullanır:

- `agent:<agentId>:slack:slash:<userId>`

ve yine de komut yürütmesini hedef konuşma oturumuna (`CommandTargetSessionKey`) karşı yönlendirir.

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

Veya bunu yalnızca bir Slack hesabı için etkinleştirin:

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

Etkinleştirildiğinde ajanlar yalnızca Slack'e özel yanıt yönergeleri verebilir:

- `[[slack_buttons: Approve:approve, Reject:reject]]`
- `[[slack_select: Choose a target | Canary:canary, Production:production]]`

Bu yönergeler Slack Block Kit içine derlenir ve tıklamaları veya seçimleri mevcut Slack etkileşim olayı yolu üzerinden geri yönlendirir.

Notlar:

- Bu Slack'e özgü bir kullanıcı arayüzüdür. Diğer kanallar Slack Block Kit yönergelerini kendi düğme sistemlerine çevirmez.
- Etkileşimli geri çağırım değerleri, ajan tarafından yazılmış ham değerler değil, OpenClaw tarafından oluşturulan opak token'lardır.
- Oluşturulan etkileşimli bloklar Slack Block Kit sınırlarını aşarsa OpenClaw geçersiz bir blocks yükü göndermek yerine özgün metin yanıtına geri döner.

## Slack'te exec onayları

Slack, Web UI veya terminale geri dönmek yerine etkileşimli düğmeler ve etkileşimlerle yerel bir onay istemcisi olarak davranabilir.

- Exec onayları, yerel DM/kanal yönlendirmesi için `channels.slack.execApprovals.*` kullanır.
- İstek zaten Slack'e ulaşıyorsa ve onay kimliği türü `plugin:` ise eklenti onayları yine aynı Slack yerel düğme yüzeyi üzerinden çözülebilir.
- Onaylayıcı yetkilendirmesi yine uygulanır: yalnızca onaylayıcı olarak tanımlanan kullanıcılar istekleri Slack üzerinden onaylayabilir veya reddedebilir.

Bu, diğer kanallarla aynı paylaşılan onay düğmesi yüzeyini kullanır. Slack uygulaması ayarlarınızda `interactivity` etkin olduğunda onay istemleri doğrudan konuşmada Block Kit düğmeleri olarak işlenir.
Bu düğmeler mevcut olduğunda birincil onay kullanıcı deneyimi bunlardır; OpenClaw,
araç sonucu sohbet onaylarının kullanılamadığını veya tek yolun manuel onay olduğunu söylemedikçe yalnızca manuel bir `/approve` komutu içermelidir.

Yapılandırma yolu:

- `channels.slack.execApprovals.enabled`
- `channels.slack.execApprovals.approvers` (isteğe bağlı; mümkün olduğunda `commands.ownerAllowFrom` değerine geri döner)
- `channels.slack.execApprovals.target` (`dm` | `channel` | `both`, varsayılan: `dm`)
- `agentFilter`, `sessionFilter`

`enabled` ayarsız veya `"auto"` olduğunda ve en az bir
onaylayıcı çözümlendiğinde Slack yerel exec onaylarını otomatik olarak etkinleştirir. Slack'i yerel onay istemcisi olarak açıkça devre dışı bırakmak için `enabled: false` ayarlayın.
Onaylayıcılar çözümlendiğinde yerel onayları zorla açmak için `enabled: true` ayarlayın.

Açık Slack exec onay yapılandırması olmadan varsayılan davranış:

```json5
{
  commands: {
    ownerAllowFrom: ["slack:U12345678"],
  },
}
```

Açık Slack yerel yapılandırması yalnızca onaylayıcıları geçersiz kılmak, filtreler eklemek veya
köken sohbetine teslimatı seçmek istediğinizde gereklidir:

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

Paylaşılan `approvals.exec` yönlendirmesi ayrıdır. Bunu yalnızca exec onay istemlerinin ayrıca
başka sohbetlere veya açık bant dışı hedeflere yönlendirilmesi gerektiğinde kullanın. Paylaşılan `approvals.plugin` yönlendirmesi de
ayrıdır; Slack yerel düğmeleri, bu istekler zaten Slack'e ulaştığında eklenti onaylarını yine çözebilir.

Aynı sohbet içinde `/approve`, komutları zaten destekleyen Slack kanallarında ve DM'lerinde de çalışır. Tam onay yönlendirme modeli için bkz. [Exec approvals](/tr/tools/exec-approvals).

## Olaylar ve operasyonel davranış

- Mesaj düzenlemeleri/silmeleri/iş parçacığı yayınları sistem olaylarına eşlenir.
- Reaksiyon ekleme/kaldırma olayları sistem olaylarına eşlenir.
- Üye katılma/ayrılma, kanal oluşturma/yeniden adlandırma ve sabitleme ekleme/kaldırma olayları sistem olaylarına eşlenir.
- `channel_id_changed`, `configWrites` etkin olduğunda kanal yapılandırma anahtarlarını taşıyabilir.
- Kanal konu/amaç meta verileri güvenilmeyen bağlam olarak değerlendirilir ve yönlendirme bağlamına eklenebilir.
- İş parçacığı başlatıcısı ve ilk iş parçacığı geçmişi bağlam tohumlaması, uygulanabildiğinde yapılandırılmış gönderici izin listelerine göre filtrelenir.
- Blok eylemleri ve modal etkileşimler, zengin yük alanlarıyla yapılandırılmış `Slack interaction: ...` sistem olayları yayar:
  - blok eylemleri: seçilen değerler, etiketler, seçici değerleri ve `workflow_*` meta verileri
  - yönlendirilmiş kanal meta verileri ve form girdileri ile modal `view_submission` ve `view_closed` olayları

## Yapılandırma başvuru işaretçileri

Birincil başvuru:

- [Yapılandırma başvurusu - Slack](/tr/gateway/configuration-reference#slack)

  Yüksek sinyalli Slack alanları:
  - mod/kimlik doğrulama: `mode`, `botToken`, `appToken`, `signingSecret`, `webhookPath`, `accounts.*`
  - DM erişimi: `dm.enabled`, `dmPolicy`, `allowFrom` (eski: `dm.policy`, `dm.allowFrom`), `dm.groupEnabled`, `dm.groupChannels`
  - uyumluluk anahtarı: `dangerouslyAllowNameMatching` (son çare; gerekmedikçe kapalı tutun)
  - kanal erişimi: `groupPolicy`, `channels.*`, `channels.*.users`, `channels.*.requireMention`
  - iş parçacığı/geçmiş: `replyToMode`, `replyToModeByChatType`, `thread.*`, `historyLimit`, `dmHistoryLimit`, `dms.*.historyLimit`
  - teslimat: `textChunkLimit`, `chunkMode`, `mediaMaxMb`, `streaming`, `nativeStreaming`
  - operasyonlar/özellikler: `configWrites`, `commands.native`, `slashCommand.*`, `actions.*`, `userToken`, `userTokenReadOnly`

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
    Şunları kontrol edin:

    - `channels.slack.dm.enabled`
    - `channels.slack.dmPolicy` (veya eski `channels.slack.dm.policy`)
    - eşleştirme onayları / izin listesi girdileri

```bash
openclaw pairing list slack
```

  </Accordion>

  <Accordion title="Socket modu bağlanmıyor">
    Bot + uygulama token'larını ve Slack uygulama ayarlarında Socket Mode'un etkinleştirilmesini doğrulayın.

    `openclaw channels status --probe --json`, `botTokenStatus` veya
    `appTokenStatus: "configured_unavailable"` gösteriyorsa, Slack hesabı
    yapılandırılmıştır ancak mevcut çalışma zamanı SecretRef destekli
    değeri çözememiştir.

  </Accordion>

  <Accordion title="HTTP modu olay almıyor">
    Şunları doğrulayın:

    - signing secret
    - webhook yolu
    - Slack Request URL'leri (Events + Interactivity + Slash Commands)
    - HTTP hesap başına benzersiz `webhookPath`

    Hesap anlık görüntülerinde `signingSecretStatus: "configured_unavailable"`
    görünüyorsa, HTTP hesabı yapılandırılmıştır ancak mevcut çalışma zamanı
    SecretRef destekli signing secret değerini çözememiştir.

  </Accordion>

  <Accordion title="Yerel/slash komutları tetiklenmiyor">
    Şunlardan hangisini amaçladığınızı doğrulayın:

    - Slack'te eşleşen slash komutları kayıtlı olacak şekilde yerel komut modu (`channels.slack.commands.native: true`)
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
