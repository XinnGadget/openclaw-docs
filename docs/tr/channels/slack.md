---
read_when:
    - Slack kurulurken veya Slack socket/HTTP modunda hata ayıklarken
summary: Slack kurulumu ve çalışma zamanı davranışı (Socket Mode + HTTP Events API)
title: Slack
x-i18n:
    generated_at: "2026-04-06T03:07:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7e4ff2ce7d92276d62f4f3d3693ddb56ca163d5fdc2f1082ff7ba3421fada69c
    source_path: channels/slack.md
    workflow: 15
---

# Slack

Durum: Slack uygulama entegrasyonları üzerinden DM'ler ve kanallar için üretime hazır. Varsayılan mod Socket Mode'dur; HTTP Events API modu da desteklenir.

<CardGroup cols={3}>
  <Card title="Eşleme" icon="link" href="/tr/channels/pairing">
    Slack DM'leri varsayılan olarak eşleme modunu kullanır.
  </Card>
  <Card title="Slash komutları" icon="terminal" href="/tr/tools/slash-commands">
    Yerel komut davranışı ve komut kataloğu.
  </Card>
  <Card title="Kanal sorun giderme" icon="wrench" href="/tr/channels/troubleshooting">
    Kanallar arası tanılama ve onarım çalışma kitapları.
  </Card>
</CardGroup>

## Hızlı kurulum

<Tabs>
  <Tab title="Socket Mode (varsayılan)">
    <Steps>
      <Step title="Slack uygulaması ve token'ları oluşturun">
        Slack uygulaması ayarlarında:

        - **Socket Mode**'u etkinleştirin
        - `connections:write` ile **App Token** (`xapp-...`) oluşturun
        - uygulamayı yükleyin ve **Bot Token**'ı (`xoxb-...`) kopyalayın
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

      <Step title="Uygulama etkinliklerine abone olun">
        Şunlar için bot etkinliklerine abone olun:

        - `app_mention`
        - `message.channels`, `message.groups`, `message.im`, `message.mpim`
        - `reaction_added`, `reaction_removed`
        - `member_joined_channel`, `member_left_channel`
        - `channel_rename`
        - `pin_added`, `pin_removed`

        DM'ler için ayrıca App Home **Messages Tab**'ı etkinleştirin.
      </Step>

      <Step title="Gateway'i başlatın">

```bash
openclaw gateway
```

      </Step>
    </Steps>

  </Tab>

  <Tab title="HTTP Events API modu">
    <Steps>
      <Step title="Slack uygulamasını HTTP için yapılandırın">

        - modu HTTP olarak ayarlayın (`channels.slack.mode="http"`)
        - Slack **Signing Secret**'ını kopyalayın
        - Event Subscriptions + Interactivity + Slash command Request URL'yi aynı webhook yoluna ayarlayın (varsayılan `/slack/events`)

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

      <Step title="Çok hesaplı HTTP için benzersiz webhook yolları kullanın">
        Hesap başına HTTP modu desteklenir.

        Kayıtların çakışmaması için her hesaba ayrı bir `webhookPath` verin.
      </Step>
    </Steps>

  </Tab>
</Tabs>

## Manifest ve kapsam denetim listesi

<AccordionGroup>
  <Accordion title="Slack uygulama manifest örneği" defaultOpen>

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

  </Accordion>

  <Accordion title="İsteğe bağlı kullanıcı token kapsamları (okuma işlemleri)">
    `channels.slack.userToken` yapılandırırsanız, tipik okuma kapsamları şunlardır:

    - `channels:history`, `groups:history`, `im:history`, `mpim:history`
    - `channels:read`, `groups:read`, `im:read`, `mpim:read`
    - `users:read`
    - `reactions:read`
    - `pins:read`
    - `emoji:read`
    - `search:read` (Slack arama okumalarına bağlıysanız)

  </Accordion>
</AccordionGroup>

## Token modeli

- Socket Mode için `botToken` + `appToken` gereklidir.
- HTTP modu için `botToken` + `signingSecret` gerekir.
- `botToken`, `appToken`, `signingSecret` ve `userToken`, düz metin
  dizelerini veya SecretRef nesnelerini kabul eder.
- Yapılandırma token'ları, ortam değişkeni yedeğinin önüne geçer.
- `SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN` ortam değişkeni yedeği yalnızca varsayılan hesap için geçerlidir.
- `userToken` (`xoxp-...`) yalnızca yapılandırmadadır (ortam değişkeni yedeği yoktur) ve varsayılan olarak salt okunur davranışı kullanır (`userTokenReadOnly: true`).
- İsteğe bağlı: giden mesajların etkin ajan kimliğini kullanmasını istiyorsanız `chat:write.customize` ekleyin (özel `username` ve simge). `icon_emoji`, `:emoji_name:` sözdizimini kullanır.

Durum anlık görüntüsü davranışı:

- Slack hesap incelemesi, kimlik bilgisi başına `*Source` ve `*Status`
  alanlarını izler (`botToken`, `appToken`, `signingSecret`, `userToken`).
- Durum `available`, `configured_unavailable` veya `missing` olur.
- `configured_unavailable`, hesabın SecretRef
  veya başka bir satır içi olmayan gizli kaynak üzerinden yapılandırıldığı,
  ancak mevcut komut/çalışma zamanı yolunun gerçek değeri çözemediği anlamına gelir.
- HTTP modunda `signingSecretStatus` dahil edilir; Socket Mode'da
  gerekli ikili `botTokenStatus` + `appTokenStatus` olur.

<Tip>
Eylemler/dizin okumaları için, yapılandırılmışsa kullanıcı token'ı tercih edilebilir. Yazma işlemleri için bot token'ı tercih edilmeye devam eder; kullanıcı token'ı ile yazmaya yalnızca `userTokenReadOnly: false` olduğunda ve bot token'ı kullanılamadığında izin verilir.
</Tip>

## Eylemler ve geçitler

Slack eylemleri `channels.slack.actions.*` tarafından kontrol edilir.

Mevcut Slack araçlarında kullanılabilen eylem grupları:

| Grup      | Varsayılan |
| ---------- | ------- |
| messages   | etkin |
| reactions  | etkin |
| pins       | etkin |
| memberInfo | etkin |
| emojiList  | etkin |

Mevcut Slack mesaj eylemleri arasında `send`, `upload-file`, `download-file`, `read`, `edit`, `delete`, `pin`, `unpin`, `list-pins`, `member-info` ve `emoji-list` bulunur.

## Erişim denetimi ve yönlendirme

<Tabs>
  <Tab title="DM ilkesi">
    `channels.slack.dmPolicy`, DM erişimini kontrol eder (eski: `channels.slack.dm.policy`):

    - `pairing` (varsayılan)
    - `allowlist`
    - `open` (`channels.slack.allowFrom` içine `"*"` eklenmesini gerektirir; eski: `channels.slack.dm.allowFrom`)
    - `disabled`

    DM bayrakları:

    - `dm.enabled` (varsayılan true)
    - `channels.slack.allowFrom` (tercih edilen)
    - `dm.allowFrom` (eski)
    - `dm.groupEnabled` (grup DM'leri varsayılan olarak false)
    - `dm.groupChannels` (isteğe bağlı MPIM izin listesi)

    Çok hesaplı öncelik:

    - `channels.slack.accounts.default.allowFrom` yalnızca `default` hesabına uygulanır.
    - Adlandırılmış hesaplar, kendi `allowFrom` alanları ayarlı değilse `channels.slack.allowFrom` değerini devralır.
    - Adlandırılmış hesaplar `channels.slack.accounts.default.allowFrom` değerini devralmaz.

    DM'lerde eşleme için `openclaw pairing approve slack <code>` kullanılır.

  </Tab>

  <Tab title="Kanal ilkesi">
    `channels.slack.groupPolicy`, kanal işlemeyi kontrol eder:

    - `open`
    - `allowlist`
    - `disabled`

    Kanal izin listesi `channels.slack.channels` altında bulunur ve kararlı kanal kimliklerini kullanmalıdır.

    Çalışma zamanı notu: `channels.slack` tamamen eksikse (yalnızca ortam değişkeni kurulumu), çalışma zamanı `groupPolicy="allowlist"` değerine geri döner ve bir uyarı kaydeder (`channels.defaults.groupPolicy` ayarlanmış olsa bile).

    Ad/kimlik çözümleme:

    - kanal izin listesi girdileri ve DM izin listesi girdileri, token erişimi izin verdiğinde başlangıçta çözülür
    - çözümlenmemiş kanal adı girdileri yapılandırıldığı gibi tutulur ancak varsayılan olarak yönlendirme için yok sayılır
    - gelen yetkilendirme ve kanal yönlendirme varsayılan olarak önce kimlik temellidir; doğrudan kullanıcı adı/slug eşleştirmesi için `channels.slack.dangerouslyAllowNameMatching: true` gerekir

  </Tab>

  <Tab title="Bahsetmeler ve kanal kullanıcıları">
    Kanal mesajları varsayılan olarak bahsetme ile kapılanır.

    Bahsetme kaynakları:

    - açık uygulama bahsetmesi (`<@botId>`)
    - bahsetme regex kalıpları (`agents.list[].groupChat.mentionPatterns`, yedek olarak `messages.groupChat.mentionPatterns`)
    - bota yanıt verilen iş parçacığındaki örtük davranış

    Kanal başına denetimler (`channels.slack.channels.<id>`; adlar yalnızca başlangıç çözümlemesi veya `dangerouslyAllowNameMatching` yoluyla):

    - `requireMention`
    - `users` (izin listesi)
    - `allowBots`
    - `skills`
    - `systemPrompt`
    - `tools`, `toolsBySender`
    - `toolsBySender` anahtar biçimi: `id:`, `e164:`, `username:`, `name:` veya `"*"` jokeri
      (eski öneksiz anahtarlar yine yalnızca `id:` ile eşleşir)

  </Tab>
</Tabs>

## İş parçacıkları, oturumlar ve yanıt etiketleri

- DM'ler `direct` olarak, kanallar `channel` olarak, MPIM'ler `group` olarak yönlendirilir.
- Varsayılan `session.dmScope=main` ile Slack DM'leri ajan ana oturumunda birleştirilir.
- Kanal oturumları: `agent:<agentId>:slack:channel:<channelId>`.
- Uygun olduğunda iş parçacığı yanıtları iş parçacığı oturum son ekleri (`:thread:<threadTs>`) oluşturabilir.
- `channels.slack.thread.historyScope` varsayılan olarak `thread`; `thread.inheritParent` varsayılan olarak `false` değerindedir.
- `channels.slack.thread.initialHistoryLimit`, yeni bir iş parçacığı oturumu başladığında kaç mevcut iş parçacığı mesajının getirileceğini kontrol eder (varsayılan `20`; devre dışı bırakmak için `0` ayarlayın).

Yanıt iş parçacığı denetimleri:

- `channels.slack.replyToMode`: `off|first|all|batched` (varsayılan `off`)
- `channels.slack.replyToModeByChatType`: `direct|group|channel` başına
- doğrudan sohbetler için eski yedek: `channels.slack.dm.replyToMode`

El ile yanıt etiketleri desteklenir:

- `[[reply_to_current]]`
- `[[reply_to:<id>]]`

Not: `replyToMode="off"`, açık `[[reply_to_*]]` etiketleri dahil Slack'teki **tüm** yanıt iş parçacıklarını devre dışı bırakır. Bu, açık etiketlerin `"off"` modunda yine de uygulandığı Telegram'dan farklıdır. Fark, platform iş parçacığı modellerini yansıtır: Slack iş parçacıkları mesajları kanaldan gizlerken, Telegram yanıtları ana sohbet akışında görünür kalır.

## Onay reaksiyonları

`ackReaction`, OpenClaw gelen bir mesajı işlerken bir onay emojisi gönderir.

Çözümleme sırası:

- `channels.slack.accounts.<accountId>.ackReaction`
- `channels.slack.ackReaction`
- `messages.ackReaction`
- ajan kimliği emoji yedeği (`agents.list[].identity.emoji`, aksi halde "👀")

Notlar:

- Slack kısa kodlar bekler (örneğin `"eyes"`).
- Slack hesabı için veya genel olarak reaksiyonu devre dışı bırakmak amacıyla `""` kullanın.

## Metin akışı

`channels.slack.streaming`, canlı önizleme davranışını kontrol eder:

- `off`: canlı önizleme akışını devre dışı bırakır.
- `partial` (varsayılan): önizleme metnini en son kısmi çıktı ile değiştirir.
- `block`: parçalı önizleme güncellemelerini ekler.
- `progress`: oluşturma sırasında ilerleme durum metni gösterir, ardından son metni gönderir.

`channels.slack.nativeStreaming`, `streaming` `partial` olduğunda Slack yerel metin akışını kontrol eder (varsayılan: `true`).

- Yerel metin akışının görünmesi için bir yanıt iş parçacığı mevcut olmalıdır. İş parçacığı seçimi yine `replyToMode` değerini izler. Bu olmadan normal taslak önizleme kullanılır.
- Medya ve metin dışı yükler normal teslimata geri döner.
- Akış yanıt ortasında başarısız olursa OpenClaw kalan yükler için normal teslimata geri döner.

Slack yerel metin akışı yerine taslak önizlemeyi kullanın:

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

- `channels.slack.streamMode` (`replace | status_final | append`) otomatik olarak `channels.slack.streaming` alanına geçirilir.
- boolean `channels.slack.streaming`, otomatik olarak `channels.slack.nativeStreaming` alanına geçirilir.

## Yazıyor reaksiyonu yedeği

`typingReaction`, OpenClaw bir yanıtı işlerken gelen Slack mesajına geçici bir reaksiyon ekler, ardından çalışma bittiğinde bunu kaldırır. Bu özellikle, varsayılan bir "is typing..." durum göstergesi kullanan iş parçacığı yanıtlarının dışında faydalıdır.

Çözümleme sırası:

- `channels.slack.accounts.<accountId>.typingReaction`
- `channels.slack.typingReaction`

Notlar:

- Slack kısa kodlar bekler (örneğin `"hourglass_flowing_sand"`).
- Reaksiyon en iyi çaba esasına göredir ve yanıt veya hata yolu tamamlandıktan sonra temizleme işlemi otomatik olarak denenir.

## Medya, parçalama ve teslimat

<AccordionGroup>
  <Accordion title="Gelen ekler">
    Slack dosya ekleri, Slack tarafından barındırılan özel URL'lerden indirilir (token ile kimliği doğrulanmış istek akışı) ve getirme başarılı olduğunda ve boyut sınırları izin verdiğinde medya deposuna yazılır.

    Gelen çalışma zamanı boyut üst sınırı, `channels.slack.mediaMaxMb` ile geçersiz kılınmadıkça varsayılan olarak `20MB`'dır.

  </Accordion>

  <Accordion title="Giden metin ve dosyalar">
    - metin parçaları `channels.slack.textChunkLimit` kullanır (varsayılan 4000)
    - `channels.slack.chunkMode="newline"`, paragraf öncelikli bölmeyi etkinleştirir
    - dosya gönderimleri Slack yükleme API'lerini kullanır ve iş parçacığı yanıtlarını içerebilir (`thread_ts`)
    - giden medya sınırı, yapılandırılmışsa `channels.slack.mediaMaxMb` değerini izler; aksi halde kanal gönderimleri medya işlem hattındaki MIME türü varsayılanlarını kullanır
  </Accordion>

  <Accordion title="Teslimat hedefleri">
    Tercih edilen açık hedefler:

    - DM'ler için `user:<id>`
    - kanallar için `channel:<id>`

    Slack DM'leri, kullanıcı hedeflerine gönderim yapılırken Slack konuşma API'leri aracılığıyla açılır.

  </Accordion>
</AccordionGroup>

## Komutlar ve slash davranışı

- Slack için yerel komut otomatik modu **kapalıdır** (`commands.native: "auto"` Slack yerel komutlarını etkinleştirmez).
- Yerel Slack komut işleyicilerini `channels.slack.commands.native: true` ile etkinleştirin (veya genel `commands.native: true`).
- Yerel komutlar etkinleştirildiğinde, Slack'te eşleşen slash komutlarını (`/<command>` adları) kaydedin; tek istisna şudur:
  - durum komutu için `/agentstatus` kaydedin (Slack `/status` komutunu ayırmıştır)
- Yerel komutlar etkin değilse, `channels.slack.slashCommand` üzerinden tek bir yapılandırılmış slash komutu çalıştırabilirsiniz.
- Yerel arg menüleri artık işleme stratejilerini uyarlıyor:
  - 5 seçeneğe kadar: düğme blokları
  - 6-100 seçenek: statik seçim menüsü
  - 100'den fazla seçenek: etkileşim seçenek işleyicileri mevcut olduğunda eşzamansız seçenek filtrelemeli harici seçim
  - kodlanmış seçenek değerleri Slack sınırlarını aşarsa akış düğmelere geri döner
- Uzun seçenek yükleri için Slash komut argüman menüleri, seçilen bir değeri göndermeden önce bir onay iletişim kutusu kullanır.

Varsayılan slash komut ayarları:

- `enabled: false`
- `name: "openclaw"`
- `sessionPrefix: "slack:slash"`
- `ephemeral: true`

Slash oturumları yalıtılmış anahtarlar kullanır:

- `agent:<agentId>:slack:slash:<userId>`

ve yine de komut yürütmesini hedef konuşma oturumuna karşı yönlendirir (`CommandTargetSessionKey`).

## Etkileşimli yanıtlar

Slack, ajan tarafından oluşturulan etkileşimli yanıt denetimlerini işleyebilir, ancak bu özellik varsayılan olarak devre dışıdır.

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

Etkinleştirildiğinde ajanlar yalnızca Slack'e özel yanıt yönergeleri üretebilir:

- `[[slack_buttons: Approve:approve, Reject:reject]]`
- `[[slack_select: Choose a target | Canary:canary, Production:production]]`

Bu yönergeler Slack Block Kit'e derlenir ve tıklamaları veya seçimleri mevcut Slack etkileşim etkinliği yolu üzerinden geri yönlendirir.

Notlar:

- Bu, Slack'e özgü bir kullanıcı arayüzüdür. Diğer kanallar Slack Block Kit yönergelerini kendi düğme sistemlerine çevirmez.
- Etkileşimli geri çağırma değerleri, ajanın doğrudan yazdığı ham değerler değil, OpenClaw tarafından üretilen opak token'lardır.
- Oluşturulan etkileşimli bloklar Slack Block Kit sınırlarını aşarsa, OpenClaw geçersiz bir blocks yükü göndermek yerine özgün metin yanıtına geri döner.

## Slack'te exec onayları

Slack, Web UI veya terminale geri dönmek yerine, etkileşimli düğmeler ve etkileşimlerle yerel bir onay istemcisi olarak davranabilir.

- Exec onayları, yerel DM/kanal yönlendirmesi için `channels.slack.execApprovals.*` kullanır.
- Eklenti onayları, istek zaten Slack'e ulaşıyorsa ve onay kimliği türü `plugin:` ise aynı Slack yerel düğme yüzeyi üzerinden çözülebilir.
- Onaylayan yetkilendirmesi yine uygulanır: yalnızca onaylayıcı olarak tanımlanan kullanıcılar istekleri Slack üzerinden onaylayabilir veya reddedebilir.

Bu, diğer kanallarla aynı paylaşılan onay düğmesi yüzeyini kullanır. Slack uygulama ayarlarınızda `interactivity` etkin olduğunda, onay istemleri doğrudan konuşma içinde Block Kit düğmeleri olarak işlenir.
Bu düğmeler mevcut olduğunda birincil onay kullanıcı deneyimi bunlardır; OpenClaw
yalnızca araç sonucu sohbet
onaylarının kullanılamadığını söylediğinde veya tek yol el ile onay olduğunda manuel bir `/approve` komutu eklemelidir.

Yapılandırma yolu:

- `channels.slack.execApprovals.enabled`
- `channels.slack.execApprovals.approvers` (isteğe bağlı; mümkün olduğunda `commands.ownerAllowFrom` değerine geri döner)
- `channels.slack.execApprovals.target` (`dm` | `channel` | `both`, varsayılan: `dm`)
- `agentFilter`, `sessionFilter`

Slack, `enabled` ayarlanmadığında veya `"auto"` olduğunda ve en az bir
onaylayıcı çözümlendiğinde yerel exec onaylarını otomatik olarak etkinleştirir. Slack'i yerel bir onay istemcisi olarak açıkça devre dışı bırakmak için `enabled: false` ayarlayın.
Onaylayıcılar çözümlendiğinde yerel onayları zorla açmak için `enabled: true` ayarlayın.

Açık Slack exec onayı yapılandırması olmayan varsayılan davranış:

```json5
{
  commands: {
    ownerAllowFrom: ["slack:U12345678"],
  },
}
```

Açık Slack yerel yapılandırması yalnızca onaylayıcıları geçersiz kılmak, filtreler eklemek veya
kaynak sohbet teslimatını kullanmak istediğinizde gerekir:

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

Paylaşılan `approvals.exec` yönlendirmesi ayrıdır. Bunu yalnızca exec onay istemlerinin diğer sohbetlere veya açık bant dışı hedeflere de yönlendirilmesi gerektiğinde kullanın. Paylaşılan `approvals.plugin` yönlendirmesi de
ayrıdır; Slack yerel düğmeleri, bu istekler zaten
Slack'e ulaştığında eklenti onaylarını yine çözebilir.

Aynı sohbette `/approve`, komutları zaten destekleyen Slack kanallarında ve DM'lerde de çalışır. Tam onay yönlendirme modeli için [Exec approvals](/tr/tools/exec-approvals) bölümüne bakın.

## Etkinlikler ve operasyonel davranış

- Mesaj düzenlemeleri/silmeleri/iş parçacığı yayınları sistem etkinliklerine eşlenir.
- Reaksiyon ekleme/kaldırma etkinlikleri sistem etkinliklerine eşlenir.
- Üye katılma/ayrılma, kanal oluşturma/yeniden adlandırma ve sabitleme ekleme/kaldırma etkinlikleri sistem etkinliklerine eşlenir.
- `channel_id_changed`, `configWrites` etkin olduğunda kanal yapılandırma anahtarlarını taşıyabilir.
- Kanal konu/amaç meta verileri güvenilmeyen bağlam olarak değerlendirilir ve yönlendirme bağlamına enjekte edilebilir.
- İş parçacığı başlatıcısı ve ilk iş parçacığı geçmişi bağlam tohumu, uygun olduğunda yapılandırılmış gönderici izin listelerine göre filtrelenir.
- Blok eylemleri ve modal etkileşimler, zengin yük alanlarıyla yapılandırılmış `Slack interaction: ...` sistem etkinlikleri üretir:
  - blok eylemleri: seçilen değerler, etiketler, seçici değerleri ve `workflow_*` meta verileri
  - yönlendirilmiş kanal meta verileri ve form girdileriyle modal `view_submission` ve `view_closed` etkinlikleri

## Yapılandırma başvuru işaretçileri

Birincil başvuru:

- [Yapılandırma başvurusu - Slack](/tr/gateway/configuration-reference#slack)

  Yüksek sinyalli Slack alanları:
  - mod/kimlik doğrulama: `mode`, `botToken`, `appToken`, `signingSecret`, `webhookPath`, `accounts.*`
  - DM erişimi: `dm.enabled`, `dmPolicy`, `allowFrom` (eski: `dm.policy`, `dm.allowFrom`), `dm.groupEnabled`, `dm.groupChannels`
  - uyumluluk anahtarı: `dangerouslyAllowNameMatching` (acil durum; gerekmedikçe kapalı tutun)
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
    - eşleme onayları / izin listesi girdileri

```bash
openclaw pairing list slack
```

  </Accordion>

  <Accordion title="Socket modu bağlanmıyor">
    Slack uygulama ayarlarında bot + uygulama token'larını ve Socket Mode etkinliğini doğrulayın.

    `openclaw channels status --probe --json`, `botTokenStatus` veya
    `appTokenStatus: "configured_unavailable"` gösteriyorsa, Slack hesabı
    yapılandırılmıştır ancak mevcut çalışma zamanı SecretRef destekli
    değeri çözememiştir.

  </Accordion>

  <Accordion title="HTTP modu etkinlik almıyor">
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

    - Slack'te eşleşen slash komutları kaydedilmiş yerel komut modu (`channels.slack.commands.native: true`)
    - veya tek slash komut modu (`channels.slack.slashCommand.enabled: true`)

    Ayrıca `commands.useAccessGroups` ve kanal/kullanıcı izin listelerini kontrol edin.

  </Accordion>
</AccordionGroup>

## İlgili

- [Eşleme](/tr/channels/pairing)
- [Gruplar](/tr/channels/groups)
- [Güvenlik](/tr/gateway/security)
- [Kanal yönlendirme](/tr/channels/channel-routing)
- [Sorun giderme](/tr/channels/troubleshooting)
- [Yapılandırma](/tr/gateway/configuration)
- [Slash komutları](/tr/tools/slash-commands)
