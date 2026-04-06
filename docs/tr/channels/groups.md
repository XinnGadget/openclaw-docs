---
read_when:
    - Grup sohbeti davranışını veya bahsetme geçitlemesini değiştirirken
summary: Yüzeyler genelinde grup sohbeti davranışı (Discord/iMessage/Matrix/Microsoft Teams/Signal/Slack/Telegram/WhatsApp/Zalo)
title: Gruplar
x-i18n:
    generated_at: "2026-04-06T03:06:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8620de6f7f0b866bf43a307fdbec3399790f09f22a87703704b0522caba80b18
    source_path: channels/groups.md
    workflow: 15
---

# Gruplar

OpenClaw, grup sohbetlerini yüzeyler genelinde tutarlı şekilde ele alır: Discord, iMessage, Matrix, Microsoft Teams, Signal, Slack, Telegram, WhatsApp, Zalo.

## Başlangıç tanıtımı (2 dakika)

OpenClaw kendi mesajlaşma hesaplarınızda “yaşar”. Ayrı bir WhatsApp bot kullanıcısı yoktur.
**Siz** bir gruptaysanız OpenClaw o grubu görebilir ve orada yanıt verebilir.

Varsayılan davranış:

- Gruplar kısıtlıdır (`groupPolicy: "allowlist"`).
- Siz açıkça bahsetme geçitlemesini devre dışı bırakmadıkça yanıtlar için bir bahsetme gerekir.

Çevirisi: izin listesine alınmış göndericiler, OpenClaw'dan bahsederek onu tetikleyebilir.

> Kısaca
>
> - **DM erişimi** `*.allowFrom` ile kontrol edilir.
> - **Grup erişimi** `*.groupPolicy` + izin listeleri (`*.groups`, `*.groupAllowFrom`) ile kontrol edilir.
> - **Yanıt tetikleme** bahsetme geçitlemesi (`requireMention`, `/activation`) ile kontrol edilir.

Hızlı akış (bir grup mesajına ne olur):

```
groupPolicy? disabled -> bırak
groupPolicy? allowlist -> grup izinli mi? hayır -> bırak
requireMention? evet -> bahsedildi mi? hayır -> yalnızca bağlam için sakla
aksi halde -> yanıt ver
```

## Bağlam görünürlüğü ve izin listeleri

Grup güvenliğinde iki farklı denetim yer alır:

- **Tetikleme yetkilendirmesi**: aracıyı kimin tetikleyebileceği (`groupPolicy`, `groups`, `groupAllowFrom`, kanala özgü izin listeleri).
- **Bağlam görünürlüğü**: modele hangi ek bağlamın enjekte edildiği (yanıt metni, alıntılar, konu geçmişi, iletilen meta veriler).

OpenClaw varsayılan olarak normal sohbet davranışına öncelik verir ve bağlamı çoğunlukla alındığı gibi tutar. Bu, izin listelerinin öncelikle kimin eylemleri tetikleyebileceğine karar verdiği, her alıntılanmış veya geçmiş parçacık için evrensel bir sansür sınırı olmadığı anlamına gelir.

Geçerli davranış kanala özgüdür:

- Bazı kanallar belirli yollarda ek bağlam için zaten gönderici tabanlı filtreleme uygular (örneğin Slack konu tohumlaması, Matrix yanıt/konu aramaları).
- Diğer kanallar hâlâ alıntı/yanıt/iletme bağlamını alındığı gibi geçirir.

Sıkılaştırma yönü (planlanan):

- `contextVisibility: "all"` (varsayılan), mevcut alındığı gibi davranışı korur.
- `contextVisibility: "allowlist"`, ek bağlamı izin listesine alınmış göndericilere filtreler.
- `contextVisibility: "allowlist_quote"`, `allowlist` artı tek bir açık alıntı/yanıt istisnasıdır.

Bu sıkılaştırma modeli kanallar genelinde tutarlı şekilde uygulanana kadar yüzeye göre farklılıklar bekleyin.

![Grup mesaj akışı](/images/groups-flow.svg)

İstiyorsanız...

| Hedef                                        | Ayarlanacak değer                                          |
| -------------------------------------------- | ---------------------------------------------------------- |
| Tüm gruplara izin ver ama yalnızca @bahsetmelerde yanıtla | `groups: { "*": { requireMention: true } }`                |
| Tüm grup yanıtlarını devre dışı bırak        | `groupPolicy: "disabled"`                                  |
| Yalnızca belirli gruplar                     | `groups: { "<group-id>": { ... } }` (`"*"` anahtarı olmadan) |
| Gruplarda yalnızca siz tetikleyebilirsiniz   | `groupPolicy: "allowlist"`, `groupAllowFrom: ["+1555..."]` |

## Oturum anahtarları

- Grup oturumları `agent:<agentId>:<channel>:group:<id>` oturum anahtarlarını kullanır (odalar/kanallar `agent:<agentId>:<channel>:channel:<id>` kullanır).
- Telegram forum konuları, her konunun kendi oturumu olması için grup kimliğine `:topic:<threadId>` ekler.
- Doğrudan sohbetler ana oturumu kullanır (veya yapılandırılmışsa gönderici başına ayrı oturum kullanır).
- Heartbeat'ler grup oturumları için atlanır.

<a id="pattern-personal-dms-public-groups-single-agent"></a>

## Desen: kişisel DM'ler + herkese açık gruplar (tek aracı)

Evet — “kişisel” trafiğiniz **DM'ler** ve “herkese açık” trafiğiniz **gruplar** ise bu iyi çalışır.

Neden: tek aracı modunda, DM'ler genellikle **ana** oturum anahtarına (`agent:main:main`) giderken gruplar her zaman **ana olmayan** oturum anahtarlarını (`agent:main:<channel>:group:<id>`) kullanır. `mode: "non-main"` ile sandbox'ı etkinleştirirseniz, bu grup oturumları Docker içinde çalışırken ana DM oturumunuz host üzerinde kalır.

Bu size tek bir aracı “beyni” (paylaşılan çalışma alanı + bellek) verir, ancak iki farklı yürütme duruşu sağlar:

- **DM'ler**: tam araçlar (host)
- **Gruplar**: sandbox + kısıtlı araçlar (Docker)

> Gerçekten ayrı çalışma alanlarına/kişiliklere ihtiyacınız varsa (“kişisel” ve “herkese açık” asla karışmamalıysa), ikinci bir aracı + bağlamalar kullanın. Bkz. [Çoklu Aracı Yönlendirme](/tr/concepts/multi-agent).

Örnek (DM'ler host üzerinde, gruplar sandbox içinde + yalnızca mesajlaşma araçları):

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main", // gruplar/kanallar ana olmayan -> sandbox içinde
        scope: "session", // en güçlü yalıtım (grup/kanal başına bir kapsayıcı)
        workspaceAccess: "none",
      },
    },
  },
  tools: {
    sandbox: {
      tools: {
        // allow boş değilse, diğer her şey engellenir (deny yine önceliklidir).
        allow: ["group:messaging", "group:sessions"],
        deny: ["group:runtime", "group:fs", "group:ui", "nodes", "cron", "gateway"],
      },
    },
  },
}
```

“Gruplar yalnızca X klasörünü görebilsin” istiyorsanız, “host erişimi olmasın” yerine `workspaceAccess: "none"` değerini koruyun ve yalnızca izin listesine alınmış yolları sandbox içine bağlayın:

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none",
        docker: {
          binds: [
            // hostPath:containerPath:mode
            "/home/user/FriendsShared:/data:ro",
          ],
        },
      },
    },
  },
}
```

İlgili:

- Yapılandırma anahtarları ve varsayılanlar: [Gateway yapılandırması](/tr/gateway/configuration-reference#agentsdefaultssandbox)
- Bir aracın neden engellendiğini hata ayıklama: [Sandbox vs Araç İlkesi vs Elevated](/tr/gateway/sandbox-vs-tool-policy-vs-elevated)
- Bind mount ayrıntıları: [Sandboxing](/tr/gateway/sandboxing#custom-bind-mounts)

## Görünen etiketler

- UI etiketleri, varsa `displayName` kullanır ve `<channel>:<token>` olarak biçimlendirilir.
- `#room`, odalar/kanallar için ayrılmıştır; grup sohbetleri `g-<slug>` kullanır (küçük harf, boşluklar -> `-`, `#@+._-` korunur).

## Grup ilkesi

Grup/oda mesajlarının kanal başına nasıl işleneceğini kontrol edin:

```json5
{
  channels: {
    whatsapp: {
      groupPolicy: "disabled", // "open" | "disabled" | "allowlist"
      groupAllowFrom: ["+15551234567"],
    },
    telegram: {
      groupPolicy: "disabled",
      groupAllowFrom: ["123456789"], // sayısal Telegram kullanıcı kimliği (sihirbaz @username çözebilir)
    },
    signal: {
      groupPolicy: "disabled",
      groupAllowFrom: ["+15551234567"],
    },
    imessage: {
      groupPolicy: "disabled",
      groupAllowFrom: ["chat_id:123"],
    },
    msteams: {
      groupPolicy: "disabled",
      groupAllowFrom: ["user@org.com"],
    },
    discord: {
      groupPolicy: "allowlist",
      guilds: {
        GUILD_ID: { channels: { help: { allow: true } } },
      },
    },
    slack: {
      groupPolicy: "allowlist",
      channels: { "#general": { allow: true } },
    },
    matrix: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["@owner:example.org"],
      groups: {
        "!roomId:example.org": { allow: true },
        "#alias:example.org": { allow: true },
      },
    },
  },
}
```

| İlke          | Davranış                                                     |
| ------------- | ------------------------------------------------------------ |
| `"open"`      | Gruplar izin listelerini atlar; bahsetme geçitlemesi yine uygulanır. |
| `"disabled"`  | Tüm grup mesajlarını tamamen engeller.                       |
| `"allowlist"` | Yalnızca yapılandırılmış izin listesiyle eşleşen gruplara/odalara izin verir. |

Notlar:

- `groupPolicy`, bahsetme geçitlemesinden ayrıdır (bu, @bahsetmeleri gerektirir).
- WhatsApp/Telegram/Signal/iMessage/Microsoft Teams/Zalo: `groupAllowFrom` kullanın (yedek: açık `allowFrom`).
- DM eşleştirme onayları (`*-allowFrom` store girdileri) yalnızca DM erişimi için geçerlidir; grup gönderici yetkilendirmesi grup izin listelerinde açık kalır.
- Discord: izin listesi `channels.discord.guilds.<id>.channels` kullanır.
- Slack: izin listesi `channels.slack.channels` kullanır.
- Matrix: izin listesi `channels.matrix.groups` kullanır. Oda kimliklerini veya takma adları tercih edin; katılınmış oda adı araması best-effort şeklindedir ve çözümlenemeyen adlar çalışma zamanında yok sayılır. Göndericileri kısıtlamak için `channels.matrix.groupAllowFrom` kullanın; oda başına `users` izin listeleri de desteklenir.
- Grup DM'leri ayrı olarak kontrol edilir (`channels.discord.dm.*`, `channels.slack.dm.*`).
- Telegram izin listesi kullanıcı kimlikleriyle (`"123456789"`, `"telegram:123456789"`, `"tg:123456789"`) veya kullanıcı adlarıyla (`"@alice"` ya da `"alice"`) eşleşebilir; önekler büyük/küçük harfe duyarsızdır.
- Varsayılan `groupPolicy: "allowlist"` değeridir; grup izin listeniz boşsa grup mesajları engellenir.
- Çalışma zamanı güvenliği: bir sağlayıcı bloğu tamamen eksik olduğunda (`channels.<provider>` yoksa), grup ilkesi `channels.defaults.groupPolicy` değerini devralmak yerine fail-closed bir moda (genellikle `allowlist`) geri döner.

Hızlı zihinsel model (grup mesajları için değerlendirme sırası):

1. `groupPolicy` (open/disabled/allowlist)
2. grup izin listeleri (`*.groups`, `*.groupAllowFrom`, kanala özgü izin listesi)
3. bahsetme geçitlemesi (`requireMention`, `/activation`)

## Bahsetme geçitlemesi (varsayılan)

Grup mesajları, grup başına geçersiz kılınmadıkça bir bahsetme gerektirir. Varsayılanlar her alt sistem için `*.groups."*"` altında bulunur.

Bot mesajına yanıt vermek, örtük bir bahsetme sayılır (kanal yanıt meta verisini destekliyorsa). Bu Telegram, WhatsApp, Slack, Discord ve Microsoft Teams için geçerlidir.

```json5
{
  channels: {
    whatsapp: {
      groups: {
        "*": { requireMention: true },
        "123@g.us": { requireMention: false },
      },
    },
    telegram: {
      groups: {
        "*": { requireMention: true },
        "123456789": { requireMention: false },
      },
    },
    imessage: {
      groups: {
        "*": { requireMention: true },
        "123": { requireMention: false },
      },
    },
  },
  agents: {
    list: [
      {
        id: "main",
        groupChat: {
          mentionPatterns: ["@openclaw", "openclaw", "\\+15555550123"],
          historyLimit: 50,
        },
      },
    ],
  },
}
```

Notlar:

- `mentionPatterns`, büyük/küçük harfe duyarsız güvenli regex desenleridir; geçersiz desenler ve güvenli olmayan iç içe yineleme biçimleri yok sayılır.
- Açık bahsetme sağlayan yüzeyler yine geçer; desenler yedektir.
- Aracı başına geçersiz kılma: `agents.list[].groupChat.mentionPatterns` (birden çok aracı aynı grubu paylaştığında kullanışlıdır).
- Bahsetme geçitlemesi yalnızca bahsetme algılaması mümkün olduğunda zorunlu kılınır (yerel bahsetmeler varsa veya `mentionPatterns` yapılandırılmışsa).
- Discord varsayılanları `channels.discord.guilds."*"` altında bulunur (sunucu/kanal başına geçersiz kılınabilir).
- Grup geçmişi bağlamı kanallar arasında tutarlı şekilde sarılır ve yalnızca **pending-only** durumundadır (bahsetme geçitlemesi nedeniyle atlanan mesajlar); genel varsayılan için `messages.groupChat.historyLimit`, geçersiz kılmalar için `channels.<channel>.historyLimit` (veya `channels.<channel>.accounts.*.historyLimit`) kullanın. Devre dışı bırakmak için `0` ayarlayın.

## Grup/kanal araç kısıtlamaları (isteğe bağlı)

Bazı kanal yapılandırmaları, **belirli bir grup/oda/kanal içinde** hangi araçların kullanılabildiğini kısıtlamayı destekler.

- `tools`: tüm grup için araçlara izin verin/engelleyin.
- `toolsBySender`: grup içinde gönderici başına geçersiz kılmalar.
  Açık anahtar önekleri kullanın:
  `id:<senderId>`, `e164:<phone>`, `username:<handle>`, `name:<displayName>` ve `"*"` joker karakteri.
  Eski öneksiz anahtarlar hâlâ kabul edilir ve yalnızca `id:` olarak eşleştirilir.

Çözümleme sırası (en belirgin olan kazanır):

1. grup/kanal `toolsBySender` eşleşmesi
2. grup/kanal `tools`
3. varsayılan (`"*"` ) `toolsBySender` eşleşmesi
4. varsayılan (`"*"` ) `tools`

Örnek (Telegram):

```json5
{
  channels: {
    telegram: {
      groups: {
        "*": { tools: { deny: ["exec"] } },
        "-1001234567890": {
          tools: { deny: ["exec", "read", "write"] },
          toolsBySender: {
            "id:123456789": { alsoAllow: ["exec"] },
          },
        },
      },
    },
  },
}
```

Notlar:

- Grup/kanal araç kısıtlamaları, global/aracı araç ilkesine ek olarak uygulanır (deny yine önceliklidir).
- Bazı kanallar odalar/kanallar için farklı iç içe yerleşim kullanır (ör. Discord `guilds.*.channels.*`, Slack `channels.*`, Microsoft Teams `teams.*.channels.*`).

## Grup izin listeleri

`channels.whatsapp.groups`, `channels.telegram.groups` veya `channels.imessage.groups` yapılandırıldığında, anahtarlar grup izin listesi işlevi görür. Varsayılan bahsetme davranışını ayarlamaya devam ederken tüm gruplara izin vermek için `"*"` kullanın.

Yaygın karışıklık: DM eşleştirme onayı, grup yetkilendirmesiyle aynı şey değildir.
DM eşleştirmeyi destekleyen kanallarda eşleştirme deposu yalnızca DM'lerin kilidini açar. Grup komutları yine de `groupAllowFrom` gibi yapılandırma izin listelerinden veya o kanal için belgelenmiş yapılandırma yedeğinden açık grup gönderici yetkilendirmesi gerektirir.

Yaygın amaçlar (kopyala/yapıştır):

1. Tüm grup yanıtlarını devre dışı bırak

```json5
{
  channels: { whatsapp: { groupPolicy: "disabled" } },
}
```

2. Yalnızca belirli gruplara izin ver (WhatsApp)

```json5
{
  channels: {
    whatsapp: {
      groups: {
        "123@g.us": { requireMention: true },
        "456@g.us": { requireMention: false },
      },
    },
  },
}
```

3. Tüm gruplara izin ver ama bahsetme zorunlu olsun (açık)

```json5
{
  channels: {
    whatsapp: {
      groups: { "*": { requireMention: true } },
    },
  },
}
```

4. Gruplarda yalnızca sahip tetikleyebilsin (WhatsApp)

```json5
{
  channels: {
    whatsapp: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15551234567"],
      groups: { "*": { requireMention: true } },
    },
  },
}
```

## Aktivasyon (yalnızca sahip)

Grup sahipleri grup başına aktivasyonu değiştirebilir:

- `/activation mention`
- `/activation always`

Sahip, `channels.whatsapp.allowFrom` ile belirlenir (ayarlanmamışsa botun kendi E.164 değeri kullanılır). Komutu bağımsız bir mesaj olarak gönderin. Diğer yüzeyler şu anda `/activation` komutunu yok sayar.

## Bağlam alanları

Grup gelen payload'ları şunları ayarlar:

- `ChatType=group`
- `GroupSubject` (biliniyorsa)
- `GroupMembers` (biliniyorsa)
- `WasMentioned` (bahsetme geçitlemesi sonucu)
- Telegram forum konuları ayrıca `MessageThreadId` ve `IsForum` içerir.

Kanala özgü notlar:

- BlueBubbles, adsız macOS grup katılımcılarını `GroupMembers` doldurulmadan önce yerel Contacts veritabanından isteğe bağlı olarak zenginleştirebilir. Bu varsayılan olarak kapalıdır ve yalnızca normal grup geçitlemesi geçildikten sonra çalışır.

Aracı sistem istemi, yeni bir grup oturumunun ilk turunda bir grup tanıtımı içerir. Modele insan gibi yanıt vermesini, Markdown tablolarından kaçınmasını, boş satırları en aza indirmesini, normal sohbet aralığını takip etmesini ve doğrudan `\n` dizileri yazmamasını hatırlatır.

## iMessage ayrıntıları

- Yönlendirme veya izin listesi için `chat_id:<id>` tercih edin.
- Sohbetleri listeleyin: `imsg chats --limit 20`.
- Grup yanıtları her zaman aynı `chat_id` değerine geri gider.

## WhatsApp ayrıntıları

Yalnızca WhatsApp davranışı için [Grup mesajları](/tr/channels/group-messages) bölümüne bakın (geçmiş enjeksiyonu, bahsetme işleme ayrıntıları).
