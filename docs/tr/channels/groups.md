---
read_when:
    - Grup sohbeti davranışını veya mention gating ayarını değiştirirken
summary: Yüzeyler arasında grup sohbeti davranışı (Discord/iMessage/Matrix/Microsoft Teams/Signal/Slack/Telegram/WhatsApp/Zalo)
title: Gruplar
x-i18n:
    generated_at: "2026-04-07T08:44:04Z"
    model: gpt-5.4
    provider: openai
    source_hash: f5045badbba30587c8f1bf27f6b940c7c471a95c57093c9adb142374413ac81e
    source_path: channels/groups.md
    workflow: 15
---

# Gruplar

OpenClaw, grup sohbetlerini yüzeyler arasında tutarlı şekilde ele alır: Discord, iMessage, Matrix, Microsoft Teams, Signal, Slack, Telegram, WhatsApp, Zalo.

## Başlangıç düzeyi giriş (2 dakika)

OpenClaw kendi mesajlaşma hesaplarınızda “yaşar”. Ayrı bir WhatsApp bot kullanıcısı yoktur.
Bir grupta **siz** varsa, OpenClaw o grubu görebilir ve orada yanıt verebilir.

Varsayılan davranış:

- Gruplar kısıtlıdır (`groupPolicy: "allowlist"`).
- Siz açıkça mention gating özelliğini devre dışı bırakmadığınız sürece yanıtlar bir mention gerektirir.

Çevirisi: allowlist içindeki gönderenler OpenClaw'u mention ederek onu tetikleyebilir.

> Özet
>
> - **DM erişimi** `*.allowFrom` ile kontrol edilir.
> - **Grup erişimi** `*.groupPolicy` + allowlist'ler (`*.groups`, `*.groupAllowFrom`) ile kontrol edilir.
> - **Yanıt tetikleme** mention gating (`requireMention`, `/activation`) ile kontrol edilir.

Hızlı akış (bir grup mesajına ne olur):

```
groupPolicy? disabled -> drop
groupPolicy? allowlist -> group allowed? no -> drop
requireMention? yes -> mentioned? no -> store for context only
otherwise -> reply
```

## Bağlam görünürlüğü ve allowlist'ler

Grup güvenliğinde iki farklı kontrol yer alır:

- **Tetikleme yetkilendirmesi**: aracıyı kimin tetikleyebileceği (`groupPolicy`, `groups`, `groupAllowFrom`, kanala özgü allowlist'ler).
- **Bağlam görünürlüğü**: modele hangi ek bağlamın eklendiği (yanıt metni, alıntılar, ileti dizisi geçmişi, iletilen meta veriler).

Varsayılan olarak OpenClaw, normal sohbet davranışına öncelik verir ve bağlamı büyük ölçüde alındığı gibi tutar. Bu, allowlist'lerin öncelikle kimin eylemleri tetikleyebileceğini belirlediği, ancak alıntılanan veya geçmişten gelen her parçacık için evrensel bir redaksiyon sınırı olmadığı anlamına gelir.

Geçerli davranış kanala özeldir:

- Bazı kanallar belirli yollarda ek bağlam için gönderen tabanlı filtreleme uygular (örneğin Slack ileti dizisi başlatma, Matrix yanıt/ileti dizisi aramaları).
- Diğer kanallar ise alıntı/yanıt/iletme bağlamını alındığı gibi geçirmeye devam eder.

Sıkılaştırma yönü (planlanan):

- `contextVisibility: "all"` (varsayılan) mevcut alındığı-gibi davranışını korur.
- `contextVisibility: "allowlist"` ek bağlamı allowlist içindeki gönderenlerle sınırlar.
- `contextVisibility: "allowlist_quote"` `allowlist` artı tek bir açık alıntı/yanıt istisnasıdır.

Bu sıkılaştırma modeli kanallar arasında tutarlı şekilde uygulanana kadar, yüzeye göre farklılıklar bekleyin.

![Grup mesajı akışı](/images/groups-flow.svg)

İstediğiniz şey...

| Hedef                                        | Ayarlanacak değer                                        |
| -------------------------------------------- | -------------------------------------------------------- |
| Tüm gruplara izin ver ama yalnızca @mention olduğunda yanıtla | `groups: { "*": { requireMention: true } }`              |
| Tüm grup yanıtlarını devre dışı bırak        | `groupPolicy: "disabled"`                                |
| Yalnızca belirli gruplar                     | `groups: { "<group-id>": { ... } }` (`"*"` anahtarı yok) |
| Gruplarda yalnızca siz tetikleyebilin        | `groupPolicy: "allowlist"`, `groupAllowFrom: ["+1555..."]` |

## Oturum anahtarları

- Grup oturumları `agent:<agentId>:<channel>:group:<id>` oturum anahtarlarını kullanır (odalar/kanallar `agent:<agentId>:<channel>:channel:<id>` kullanır).
- Telegram forum konuları grup kimliğine `:topic:<threadId>` ekler; böylece her konunun kendi oturumu olur.
- Doğrudan sohbetler ana oturumu kullanır (veya yapılandırıldıysa gönderen başına oturumu).
- Grup oturumlarında heartbeat atlanır.

<a id="pattern-personal-dms-public-groups-single-agent"></a>

## Örüntü: kişisel DM'ler + herkese açık gruplar (tek aracı)

Evet — “kişisel” trafiğiniz **DM'ler**, “herkese açık” trafiğiniz ise **gruplar** ise bu iyi çalışır.

Neden: tek aracı modunda DM'ler genellikle **ana** oturum anahtarına (`agent:main:main`) düşer, gruplar ise her zaman **ana olmayan** oturum anahtarlarını kullanır (`agent:main:<channel>:group:<id>`). `mode: "non-main"` ile sandbox'ı etkinleştirirseniz, bu grup oturumları Docker içinde çalışırken ana DM oturumunuz host üzerinde kalır.

Bu size tek bir aracı “beyni” (paylaşılan çalışma alanı + bellek) verir, ama iki farklı yürütme duruşuyla:

- **DM'ler**: tam araçlar (host)
- **Gruplar**: sandbox + kısıtlı araçlar (Docker)

> Gerçekten ayrı çalışma alanları/kişilikler gerekiyorsa (“kişisel” ve “herkese açık” asla karışmamalıysa), ikinci bir aracı + bağlamalar kullanın. Bkz. [Çoklu Aracı Yönlendirme](/tr/concepts/multi-agent).

Örnek (DM'ler host üzerinde, gruplar sandbox içinde + yalnızca mesajlaşma araçları):

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main", // groups/channels are non-main -> sandboxed
        scope: "session", // strongest isolation (one container per group/channel)
        workspaceAccess: "none",
      },
    },
  },
  tools: {
    sandbox: {
      tools: {
        // If allow is non-empty, everything else is blocked (deny still wins).
        allow: ["group:messaging", "group:sessions"],
        deny: ["group:runtime", "group:fs", "group:ui", "nodes", "cron", "gateway"],
      },
    },
  },
}
```

“Gruplar yalnızca X klasörünü görebilsin” istiyorsanız, “host erişimi olmasın” yerine `workspaceAccess: "none"` değerini koruyun ve sandbox içine yalnızca allowlist içindeki yolları bağlayın:

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
- Bir aracın neden engellendiğini hata ayıklama: [Sandbox vs Araç İlkesi vs Yükseltilmiş](/tr/gateway/sandbox-vs-tool-policy-vs-elevated)
- Bind mount ayrıntıları: [Sandboxing](/tr/gateway/sandboxing#custom-bind-mounts)

## Görünen etiketler

- UI etiketleri mevcutsa `displayName` kullanır ve `<channel>:<token>` biçiminde gösterilir.
- `#room` odalar/kanallar için ayrılmıştır; grup sohbetleri `g-<slug>` kullanır (küçük harf, boşluklar -> `-`, `#@+._-` korunur).

## Grup ilkesi

Kanal başına grup/oda mesajlarının nasıl işleneceğini kontrol edin:

```json5
{
  channels: {
    whatsapp: {
      groupPolicy: "disabled", // "open" | "disabled" | "allowlist"
      groupAllowFrom: ["+15551234567"],
    },
    telegram: {
      groupPolicy: "disabled",
      groupAllowFrom: ["123456789"], // sayısal Telegram kullanıcı kimliği (wizard @username çözümleyebilir)
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
        "!roomId:example.org": { enabled: true },
        "#alias:example.org": { enabled: true },
      },
    },
  },
}
```

| İlke          | Davranış                                                     |
| ------------- | ------------------------------------------------------------ |
| `"open"`      | Gruplar allowlist'leri atlar; mention-gating yine de uygulanır. |
| `"disabled"`  | Tüm grup mesajlarını tamamen engeller.                       |
| `"allowlist"` | Yalnızca yapılandırılmış allowlist ile eşleşen grup/odalara izin verir. |

Notlar:

- `groupPolicy`, mention-gating'den ayrıdır (bu, @mention gerektirir).
- WhatsApp/Telegram/Signal/iMessage/Microsoft Teams/Zalo: `groupAllowFrom` kullanın (yedek olarak: açık `allowFrom`).
- DM eşleştirme onayları (`*-allowFrom` store girdileri) yalnızca DM erişimi için geçerlidir; grup gönderen yetkilendirmesi grup allowlist'lerinde açık kalır.
- Discord: allowlist `channels.discord.guilds.<id>.channels` kullanır.
- Slack: allowlist `channels.slack.channels` kullanır.
- Matrix: allowlist `channels.matrix.groups` kullanır. Oda kimliklerini veya takma adları tercih edin; katılınmış oda adı araması best-effort çalışır ve çözümlenemeyen adlar çalışma zamanında yok sayılır. Gönderenleri kısıtlamak için `channels.matrix.groupAllowFrom` kullanın; oda başına `users` allowlist'leri de desteklenir.
- Grup DM'leri ayrı olarak kontrol edilir (`channels.discord.dm.*`, `channels.slack.dm.*`).
- Telegram allowlist; kullanıcı kimlikleriyle (`"123456789"`, `"telegram:123456789"`, `"tg:123456789"`) veya kullanıcı adlarıyla (`"@alice"` ya da `"alice"`) eşleşebilir; önekler büyük/küçük harf duyarsızdır.
- Varsayılan `groupPolicy: "allowlist"` değeridir; grup allowlist'iniz boşsa grup mesajları engellenir.
- Çalışma zamanı güvenliği: bir sağlayıcı bloğu tamamen eksikse (`channels.<provider>` yoksa), grup ilkesi `channels.defaults.groupPolicy` değerini devralmak yerine fail-closed bir moda (genellikle `allowlist`) geri döner.

Hızlı zihinsel model (grup mesajları için değerlendirme sırası):

1. `groupPolicy` (open/disabled/allowlist)
2. grup allowlist'leri (`*.groups`, `*.groupAllowFrom`, kanala özgü allowlist)
3. mention gating (`requireMention`, `/activation`)

## Mention gating (varsayılan)

Grup mesajları, grup başına geçersiz kılınmadıkça bir mention gerektirir. Varsayılanlar alt sistem başına `*.groups."*"` altında bulunur.

Bir bot mesajına yanıt vermek, kanal yanıt meta verilerini desteklediğinde örtük bir mention sayılır. Bir bot mesajını alıntılamak da alıntı meta verilerini sunan kanallarda örtük bir mention sayılabilir. Mevcut yerleşik örnekler arasında Telegram, WhatsApp, Slack, Discord, Microsoft Teams ve ZaloUser bulunur.

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

- `mentionPatterns` büyük/küçük harf duyarsız güvenli regex kalıplarıdır; geçersiz kalıplar ve güvenli olmayan iç içe tekrar biçimleri yok sayılır.
- Açık mention sağlayan yüzeyler yine de geçer; kalıplar yedek çözümdür.
- Aracı başına geçersiz kılma: `agents.list[].groupChat.mentionPatterns` (birden çok aracı aynı grubu paylaştığında kullanışlıdır).
- Mention gating yalnızca mention algılaması mümkün olduğunda uygulanır (yerel mention'lar varsa veya `mentionPatterns` yapılandırılmışsa).
- Discord varsayılanları `channels.discord.guilds."*"` altında bulunur (guild/kanal başına geçersiz kılınabilir).
- Grup geçmişi bağlamı kanallar arasında tutarlı şekilde sarmalanır ve yalnızca **pending-only** durumundadır (mention gating nedeniyle atlanan mesajlar); genel varsayılan için `messages.groupChat.historyLimit`, geçersiz kılmalar için `channels.<channel>.historyLimit` (veya `channels.<channel>.accounts.*.historyLimit`) kullanın. Devre dışı bırakmak için `0` ayarlayın.

## Grup/kanal araç kısıtlamaları (isteğe bağlı)

Bazı kanal yapılandırmaları, belirli bir grup/oda/kanal **içinde** hangi araçların kullanılabileceğini kısıtlamayı destekler.

- `tools`: tüm grup için araçlara izin verin/engelleyin.
- `toolsBySender`: grup içindeki gönderen bazlı geçersiz kılmalar.
  Açık anahtar önekleri kullanın:
  `id:<senderId>`, `e164:<phone>`, `username:<handle>`, `name:<displayName>` ve `"*"` jokeri.
  Eski öneksiz anahtarlar hâlâ kabul edilir ve yalnızca `id:` olarak eşleştirilir.

Çözümleme sırası (en özeli kazanır):

1. grup/kanal `toolsBySender` eşleşmesi
2. grup/kanal `tools`
3. varsayılan (`"*"`) `toolsBySender` eşleşmesi
4. varsayılan (`"*"`) `tools`

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

- Grup/kanal araç kısıtlamaları, genel/aracı araç ilkelerine ek olarak uygulanır (deny yine kazanır).
- Bazı kanallar odalar/kanallar için farklı iç içe yerleşimler kullanır (örn. Discord `guilds.*.channels.*`, Slack `channels.*`, Microsoft Teams `teams.*.channels.*`).

## Grup allowlist'leri

`channels.whatsapp.groups`, `channels.telegram.groups` veya `channels.imessage.groups` yapılandırıldığında, anahtarlar grup allowlist'i görevi görür. Varsayılan mention davranışını yine de ayarlarken tüm gruplara izin vermek için `"*"` kullanın.

Yaygın karışıklık: DM eşleştirme onayı, grup yetkilendirmesiyle aynı şey değildir.
DM eşleştirmeyi destekleyen kanallarda, eşleştirme deposu yalnızca DM'lerin kilidini açar. Grup komutları hâlâ `groupAllowFrom` veya o kanal için belgelenmiş yapılandırma yedeği gibi yapılandırma allowlist'lerinden açık grup gönderen yetkilendirmesi gerektirir.

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

3. Tüm gruplara izin ver ama mention gerektir (açık)

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

## Activation (yalnızca sahip)

Grup sahipleri grup başına activation durumunu değiştirebilir:

- `/activation mention`
- `/activation always`

Sahip, `channels.whatsapp.allowFrom` ile belirlenir (ayarlanmamışsa botun kendi E.164 değeri kullanılır). Komutu bağımsız bir mesaj olarak gönderin. Diğer yüzeyler şu anda `/activation` komutunu yok sayar.

## Bağlam alanları

Grup gelen payload'ları şunları ayarlar:

- `ChatType=group`
- `GroupSubject` (biliniyorsa)
- `GroupMembers` (biliniyorsa)
- `WasMentioned` (mention gating sonucu)
- Telegram forum konuları ayrıca `MessageThreadId` ve `IsForum` içerir.

Kanala özgü notlar:

- BlueBubbles, adsız macOS grup katılımcılarını `GroupMembers` alanını doldurmadan önce yerel Kişiler veritabanından isteğe bağlı olarak zenginleştirebilir. Bu varsayılan olarak kapalıdır ve yalnızca normal grup geçit denetimi başarıyla geçildikten sonra çalışır.

Aracı sistem prompt'u, yeni bir grup oturumunun ilk turunda grup tanıtımını içerir. Modelle insana benzer şekilde yanıt vermesini, Markdown tablolarından kaçınmasını, boş satırları en aza indirmesini ve normal sohbet aralığını izlemesini, ayrıca gerçek `\n` dizileri yazmamasını hatırlatır.

## iMessage ayrıntıları

- Yönlendirme veya allowlist oluştururken `chat_id:<id>` tercih edin.
- Sohbetleri listele: `imsg chats --limit 20`.
- Grup yanıtları her zaman aynı `chat_id` değerine geri gider.

## WhatsApp ayrıntıları

WhatsApp'a özgü davranışlar (geçmiş ekleme, mention işleme ayrıntıları) için [Grup mesajları](/tr/channels/group-messages) bölümüne bakın.
