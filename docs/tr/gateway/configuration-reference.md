---
read_when:
    - Tam alan düzeyinde yapılandırma anlamlarını veya varsayılanları öğrenmeniz gerekiyor
    - Kanal, model, ağ geçidi veya araç yapılandırma bloklarını doğruluyorsunuz
summary: Her OpenClaw yapılandırma anahtarı, varsayılanlar ve kanal ayarları için eksiksiz başvuru
title: Yapılandırma Başvurusu
x-i18n:
    generated_at: "2026-04-07T08:51:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7768cb77e1d3fc483c66f655ea891d2c32f21b247e3c1a56a919b28a37f9b128
    source_path: gateway/configuration-reference.md
    workflow: 15
---

# Yapılandırma Başvurusu

`~/.openclaw/openclaw.json` içinde kullanılabilen her alan. Görev odaklı bir genel bakış için bkz. [Configuration](/tr/gateway/configuration).

Yapılandırma biçimi **JSON5**'tir (yorumlar + sondaki virgüllere izin verilir). Tüm alanlar isteğe bağlıdır — atlandığında OpenClaw güvenli varsayılanları kullanır.

---

## Kanallar

Her kanal, yapılandırma bölümü mevcut olduğunda otomatik olarak başlar (`enabled: false` değilse).

### DM ve grup erişimi

Tüm kanallar DM ilkelerini ve grup ilkelerini destekler:

| DM ilkesi           | Davranış                                                      |
| ------------------- | ------------------------------------------------------------- |
| `pairing` (varsayılan) | Bilinmeyen gönderenler tek kullanımlık bir eşleme kodu alır; sahibin onaylaması gerekir |
| `allowlist`         | Yalnızca `allowFrom` içindeki gönderenler (veya eşlenmiş izin deposu) |
| `open`              | Tüm gelen DM'lere izin ver (gerektirir: `allowFrom: ["*"]`)   |
| `disabled`          | Tüm gelen DM'leri yok say                                     |

| Grup ilkesi           | Davranış                                             |
| --------------------- | ---------------------------------------------------- |
| `allowlist` (varsayılan) | Yalnızca yapılandırılmış allowlist ile eşleşen gruplar |
| `open`                | Grup allowlist'lerini atla (mention-gating yine de uygulanır) |
| `disabled`            | Tüm grup/oda mesajlarını engelle                     |

<Note>
`channels.defaults.groupPolicy`, bir sağlayıcının `groupPolicy` alanı ayarlanmamışsa varsayılanı belirler.
Eşleme kodlarının süresi 1 saat sonra dolar. Bekleyen DM eşleme istekleri **kanal başına 3** ile sınırlıdır.
Bir sağlayıcı bloğu tamamen eksikse (`channels.<provider>` yoksa), çalışma zamanındaki grup ilkesi bir başlangıç uyarısıyla birlikte `allowlist` (fail-closed) olarak geri döner.
</Note>

### Kanal model geçersiz kılmaları

Belirli kanal kimliklerini bir modele sabitlemek için `channels.modelByChannel` kullanın. Değerler `provider/model` veya yapılandırılmış model takma adlarını kabul eder. Kanal eşlemesi, oturumda zaten bir model geçersiz kılması yoksa uygulanır (örneğin `/model` ile ayarlanmışsa).

```json5
{
  channels: {
    modelByChannel: {
      discord: {
        "123456789012345678": "anthropic/claude-opus-4-6",
      },
      slack: {
        C1234567890: "openai/gpt-4.1",
      },
      telegram: {
        "-1001234567890": "openai/gpt-4.1-mini",
        "-1001234567890:topic:99": "anthropic/claude-sonnet-4-6",
      },
    },
  },
}
```

### Kanal varsayılanları ve heartbeat

Sağlayıcılar arasında paylaşılan grup ilkesi ve heartbeat davranışı için `channels.defaults` kullanın:

```json5
{
  channels: {
    defaults: {
      groupPolicy: "allowlist", // open | allowlist | disabled
      contextVisibility: "all", // all | allowlist | allowlist_quote
      heartbeat: {
        showOk: false,
        showAlerts: true,
        useIndicator: true,
      },
    },
  },
}
```

- `channels.defaults.groupPolicy`: sağlayıcı düzeyindeki `groupPolicy` ayarlanmamışsa geri dönüş grup ilkesi.
- `channels.defaults.contextVisibility`: tüm kanallar için varsayılan ek bağlam görünürlük modu. Değerler: `all` (varsayılan, alıntılanan/ileti dizisi/geçmiş bağlamının tamamını dahil eder), `allowlist` (yalnızca allowlist'teki gönderenlerden gelen bağlamı dahil eder), `allowlist_quote` (allowlist ile aynıdır ama açık alıntı/yanıt bağlamını korur). Kanal başına geçersiz kılma: `channels.<channel>.contextVisibility`.
- `channels.defaults.heartbeat.showOk`: sağlıklı kanal durumlarını heartbeat çıktısına dahil et.
- `channels.defaults.heartbeat.showAlerts`: bozulmuş/hata durumlarını heartbeat çıktısına dahil et.
- `channels.defaults.heartbeat.useIndicator`: kompakt gösterge tarzı heartbeat çıktısı oluştur.

### WhatsApp

WhatsApp, ağ geçidinin web kanalı (Baileys Web) üzerinden çalışır. Bağlı bir oturum olduğunda otomatik olarak başlar.

```json5
{
  channels: {
    whatsapp: {
      dmPolicy: "pairing", // pairing | allowlist | open | disabled
      allowFrom: ["+15555550123", "+447700900123"],
      textChunkLimit: 4000,
      chunkMode: "length", // length | newline
      mediaMaxMb: 50,
      sendReadReceipts: true, // mavi tikler (self-chat modunda false)
      groups: {
        "*": { requireMention: true },
      },
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15551234567"],
    },
  },
  web: {
    enabled: true,
    heartbeatSeconds: 60,
    reconnect: {
      initialMs: 2000,
      maxMs: 120000,
      factor: 1.4,
      jitter: 0.2,
      maxAttempts: 0,
    },
  },
}
```

<Accordion title="Çok hesaplı WhatsApp">

```json5
{
  channels: {
    whatsapp: {
      accounts: {
        default: {},
        personal: {},
        biz: {
          // authDir: "~/.openclaw/credentials/whatsapp/biz",
        },
      },
    },
  },
}
```

- Giden komutlar, varsa varsayılan olarak `default` hesabını kullanır; aksi halde ilk yapılandırılmış hesap kimliğini (sıralı) kullanır.
- İsteğe bağlı `channels.whatsapp.defaultAccount`, yapılandırılmış bir hesap kimliğiyle eşleştiğinde bu geri dönüş varsayılan hesap seçimini geçersiz kılar.
- Eski tek hesaplı Baileys auth dizini, `openclaw doctor` tarafından `whatsapp/default` içine taşınır.
- Hesap başına geçersiz kılmalar: `channels.whatsapp.accounts.<id>.sendReadReceipts`, `channels.whatsapp.accounts.<id>.dmPolicy`, `channels.whatsapp.accounts.<id>.allowFrom`.

</Accordion>

### Telegram

```json5
{
  channels: {
    telegram: {
      enabled: true,
      botToken: "your-bot-token",
      dmPolicy: "pairing",
      allowFrom: ["tg:123456789"],
      groups: {
        "*": { requireMention: true },
        "-1001234567890": {
          allowFrom: ["@admin"],
          systemPrompt: "Keep answers brief.",
          topics: {
            "99": {
              requireMention: false,
              skills: ["search"],
              systemPrompt: "Stay on topic.",
            },
          },
        },
      },
      customCommands: [
        { command: "backup", description: "Git backup" },
        { command: "generate", description: "Create an image" },
      ],
      historyLimit: 50,
      replyToMode: "first", // off | first | all | batched
      linkPreview: true,
      streaming: "partial", // off | partial | block | progress (varsayılan: off; preview-edit hız sınırlarını önlemek için açıkça etkinleştirin)
      actions: { reactions: true, sendMessage: true },
      reactionNotifications: "own", // off | own | all
      mediaMaxMb: 100,
      retry: {
        attempts: 3,
        minDelayMs: 400,
        maxDelayMs: 30000,
        jitter: 0.1,
      },
      network: {
        autoSelectFamily: true,
        dnsResultOrder: "ipv4first",
      },
      proxy: "socks5://localhost:9050",
      webhookUrl: "https://example.com/telegram-webhook",
      webhookSecret: "secret",
      webhookPath: "/telegram-webhook",
    },
  },
}
```

- Bot tokenı: `channels.telegram.botToken` veya `channels.telegram.tokenFile` (yalnızca normal dosya; symlink'ler reddedilir), varsayılan hesap için geri dönüş olarak `TELEGRAM_BOT_TOKEN`.
- İsteğe bağlı `channels.telegram.defaultAccount`, yapılandırılmış bir hesap kimliğiyle eşleştiğinde varsayılan hesap seçimini geçersiz kılar.
- Çok hesaplı kurulumlarda (2+ hesap kimliği), geri dönüş yönlendirmesini önlemek için açık bir varsayılan ayarlayın (`channels.telegram.defaultAccount` veya `channels.telegram.accounts.default`); bu yoksa veya geçersizse `openclaw doctor` uyarı verir.
- `configWrites: false`, Telegram tarafından başlatılan yapılandırma yazımlarını engeller (supergroup kimlik taşıma işlemleri, `/config set|unset`).
- Üst düzey `bindings[]` girdilerinde `type: "acp"`, forum konuları için kalıcı ACP bağlamaları yapılandırır (`match.peer.id` içinde kanonik `chatId:topic:topicId` kullanın). Alan anlamları [ACP Agents](/tr/tools/acp-agents#channel-specific-settings) içinde ortaktır.
- Telegram akış önizlemeleri `sendMessage` + `editMessageText` kullanır (doğrudan ve grup sohbetlerinde çalışır).
- Yeniden deneme ilkesi: bkz. [Retry policy](/tr/concepts/retry).

### Discord

```json5
{
  channels: {
    discord: {
      enabled: true,
      token: "your-bot-token",
      mediaMaxMb: 100,
      allowBots: false,
      actions: {
        reactions: true,
        stickers: true,
        polls: true,
        permissions: true,
        messages: true,
        threads: true,
        pins: true,
        search: true,
        memberInfo: true,
        roleInfo: true,
        roles: false,
        channelInfo: true,
        voiceStatus: true,
        events: true,
        moderation: false,
      },
      replyToMode: "off", // off | first | all | batched
      dmPolicy: "pairing",
      allowFrom: ["1234567890", "123456789012345678"],
      dm: { enabled: true, groupEnabled: false, groupChannels: ["openclaw-dm"] },
      guilds: {
        "123456789012345678": {
          slug: "friends-of-openclaw",
          requireMention: false,
          ignoreOtherMentions: true,
          reactionNotifications: "own",
          users: ["987654321098765432"],
          channels: {
            general: { allow: true },
            help: {
              allow: true,
              requireMention: true,
              users: ["987654321098765432"],
              skills: ["docs"],
              systemPrompt: "Short answers only.",
            },
          },
        },
      },
      historyLimit: 20,
      textChunkLimit: 2000,
      chunkMode: "length", // length | newline
      streaming: "off", // off | partial | block | progress (progress, Discord'da partial'a eşlenir)
      maxLinesPerMessage: 17,
      ui: {
        components: {
          accentColor: "#5865F2",
        },
      },
      threadBindings: {
        enabled: true,
        idleHours: 24,
        maxAgeHours: 0,
        spawnSubagentSessions: false, // `sessions_spawn({ thread: true })` için katılım gerektirir
      },
      voice: {
        enabled: true,
        autoJoin: [
          {
            guildId: "123456789012345678",
            channelId: "234567890123456789",
          },
        ],
        daveEncryption: true,
        decryptionFailureTolerance: 24,
        tts: {
          provider: "openai",
          openai: { voice: "alloy" },
        },
      },
      execApprovals: {
        enabled: "auto", // true | false | "auto"
        approvers: ["987654321098765432"],
        agentFilter: ["default"],
        sessionFilter: ["discord:"],
        target: "dm", // dm | channel | both
        cleanupAfterResolve: false,
      },
      retry: {
        attempts: 3,
        minDelayMs: 500,
        maxDelayMs: 30000,
        jitter: 0.1,
      },
    },
  },
}
```

- Token: `channels.discord.token`, varsayılan hesap için geri dönüş olarak `DISCORD_BOT_TOKEN`.
- Açık bir Discord `token` sağlayan doğrudan giden çağrılar, çağrı için o tokenı kullanır; hesap yeniden deneme/ilke ayarları yine etkin çalışma zamanı anlık görüntüsünde seçilen hesaptan gelir.
- İsteğe bağlı `channels.discord.defaultAccount`, yapılandırılmış bir hesap kimliğiyle eşleştiğinde varsayılan hesap seçimini geçersiz kılar.
- Teslim hedefleri için `user:<id>` (DM) veya `channel:<id>` (guild kanalı) kullanın; çıplak sayısal kimlikler reddedilir.
- Guild slug'ları küçük harflidir ve boşluklar `-` ile değiştirilir; kanal anahtarları slug'lanmış adı kullanır (`#` yok). Guild kimliklerini tercih edin.
- Bot tarafından yazılmış mesajlar varsayılan olarak yok sayılır. `allowBots: true` bunları etkinleştirir; yalnızca botu mention eden bot mesajlarını kabul etmek için `allowBots: "mentions"` kullanın (kendi mesajları yine filtrelenir).
- `channels.discord.guilds.<id>.ignoreOtherMentions` (ve kanal geçersiz kılmaları), başka bir kullanıcıyı veya rolü mention edip botu mention etmeyen mesajları düşürür (`@everyone/@here` hariç).
- `maxLinesPerMessage` (varsayılan 17), 2000 karakterin altında olsa bile uzun mesajları böler.
- `channels.discord.threadBindings`, Discord ileti dizisine bağlı yönlendirmeyi denetler:
  - `enabled`: ileti dizisine bağlı oturum özellikleri için Discord geçersiz kılması (`/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age` ve bağlı teslim/yönlendirme)
  - `idleHours`: saat cinsinden hareketsizlik nedeniyle otomatik odak kaldırma için Discord geçersiz kılması (`0` devre dışı bırakır)
  - `maxAgeHours`: saat cinsinden katı azami yaş için Discord geçersiz kılması (`0` devre dışı bırakır)
  - `spawnSubagentSessions`: `sessions_spawn({ thread: true })` otomatik ileti dizisi oluşturma/bağlama için katılım anahtarı
- Üst düzey `bindings[]` girdilerinde `type: "acp"`, kanal ve ileti dizileri için kalıcı ACP bağlamaları yapılandırır (`match.peer.id` içinde kanal/ileti dizisi kimliğini kullanın). Alan anlamları [ACP Agents](/tr/tools/acp-agents#channel-specific-settings) içinde ortaktır.
- `channels.discord.ui.components.accentColor`, Discord components v2 kapsayıcıları için vurgu rengini ayarlar.
- `channels.discord.voice`, Discord ses kanalı konuşmalarını ve isteğe bağlı otomatik katılım + TTS geçersiz kılmalarını etkinleştirir.
- `channels.discord.voice.daveEncryption` ve `channels.discord.voice.decryptionFailureTolerance`, `@discordjs/voice` DAVE seçeneklerine doğrudan aktarılır (varsayılan olarak `true` ve `24`).
- OpenClaw ayrıca, tekrar eden çözme hatalarından sonra bir ses oturumundan ayrılıp yeniden katılarak ses alma kurtarmasını dener.
- `channels.discord.streaming`, kanonik akış modu anahtarıdır. Eski `streamMode` ve boolean `streaming` değerleri otomatik taşınır.
- `channels.discord.autoPresence`, çalışma zamanı kullanılabilirliğini bot varlığına eşler (sağlıklı => online, bozulmuş => idle, tükenmiş => dnd) ve isteğe bağlı durum metni geçersiz kılmalarına izin verir.
- `channels.discord.dangerouslyAllowNameMatching`, değişebilir ad/etiket eşleştirmesini yeniden etkinleştirir (yalnızca acil durum uyumluluk modu).
- `channels.discord.execApprovals`: Discord yerel exec onay teslimi ve onaylayıcı yetkilendirmesi.
  - `enabled`: `true`, `false` veya `"auto"` (varsayılan). Otomatik modda exec onayları, onaylayıcılar `approvers` veya `commands.ownerAllowFrom` içinden çözümlenebildiğinde etkinleşir.
  - `approvers`: exec isteklerini onaylamaya yetkili Discord kullanıcı kimlikleri. Atlanırsa `commands.ownerAllowFrom` kullanılır.
  - `agentFilter`: isteğe bağlı aracı kimliği allowlist'i. Tüm aracılar için onay iletmek istiyorsanız atlayın.
  - `sessionFilter`: isteğe bağlı oturum anahtarı desenleri (alt dize veya regex).
  - `target`: onay istemlerinin nereye gönderileceği. `"dm"` (varsayılan) onaylayıcı DM'lerine gönderir, `"channel"` kaynak kanala gönderir, `"both"` her ikisine gönderir. Hedef `"channel"` içerdiğinde düğmeler yalnızca çözümlenen onaylayıcılar tarafından kullanılabilir.
  - `cleanupAfterResolve`: `true` olduğunda onay, ret veya zaman aşımından sonra onay DM'lerini siler.

**Tepki bildirimi modları:** `off` (yok), `own` (bot mesajları, varsayılan), `all` (tüm mesajlar), `allowlist` (`guilds.<id>.users` içinden tüm mesajlar).

### Google Chat

```json5
{
  channels: {
    googlechat: {
      enabled: true,
      serviceAccountFile: "/path/to/service-account.json",
      audienceType: "app-url", // app-url | project-number
      audience: "https://gateway.example.com/googlechat",
      webhookPath: "/googlechat",
      botUser: "users/1234567890",
      dm: {
        enabled: true,
        policy: "pairing",
        allowFrom: ["users/1234567890"],
      },
      groupPolicy: "allowlist",
      groups: {
        "spaces/AAAA": { allow: true, requireMention: true },
      },
      actions: { reactions: true },
      typingIndicator: "message",
      mediaMaxMb: 20,
    },
  },
}
```

- Service account JSON: satır içi (`serviceAccount`) veya dosya tabanlı (`serviceAccountFile`).
- Service account SecretRef de desteklenir (`serviceAccountRef`).
- Ortam geri dönüşleri: `GOOGLE_CHAT_SERVICE_ACCOUNT` veya `GOOGLE_CHAT_SERVICE_ACCOUNT_FILE`.
- Teslim hedefleri için `spaces/<spaceId>` veya `users/<userId>` kullanın.
- `channels.googlechat.dangerouslyAllowNameMatching`, değişebilir e-posta principal eşleştirmesini yeniden etkinleştirir (yalnızca acil durum uyumluluk modu).

### Slack

```json5
{
  channels: {
    slack: {
      enabled: true,
      botToken: "xoxb-...",
      appToken: "xapp-...",
      dmPolicy: "pairing",
      allowFrom: ["U123", "U456", "*"],
      dm: { enabled: true, groupEnabled: false, groupChannels: ["G123"] },
      channels: {
        C123: { allow: true, requireMention: true, allowBots: false },
        "#general": {
          allow: true,
          requireMention: true,
          allowBots: false,
          users: ["U123"],
          skills: ["docs"],
          systemPrompt: "Short answers only.",
        },
      },
      historyLimit: 50,
      allowBots: false,
      reactionNotifications: "own",
      reactionAllowlist: ["U123"],
      replyToMode: "off", // off | first | all | batched
      thread: {
        historyScope: "thread", // thread | channel
        inheritParent: false,
      },
      actions: {
        reactions: true,
        messages: true,
        pins: true,
        memberInfo: true,
        emojiList: true,
      },
      slashCommand: {
        enabled: true,
        name: "openclaw",
        sessionPrefix: "slack:slash",
        ephemeral: true,
      },
      typingReaction: "hourglass_flowing_sand",
      textChunkLimit: 4000,
      chunkMode: "length",
      streaming: "partial", // off | partial | block | progress (önizleme modu)
      nativeStreaming: true, // streaming=partial olduğunda Slack yerel akış API'sini kullan
      mediaMaxMb: 20,
      execApprovals: {
        enabled: "auto", // true | false | "auto"
        approvers: ["U123"],
        agentFilter: ["default"],
        sessionFilter: ["slack:"],
        target: "dm", // dm | channel | both
      },
    },
  },
}
```

- **Socket mode**, hem `botToken` hem `appToken` gerektirir (varsayılan hesap ortam geri dönüşü için `SLACK_BOT_TOKEN` + `SLACK_APP_TOKEN`).
- **HTTP mode**, `botToken` ile birlikte `signingSecret` gerektirir (kökte veya hesap başına).
- `botToken`, `appToken`, `signingSecret` ve `userToken`, düz metin
  dizeleri veya SecretRef nesnelerini kabul eder.
- Slack hesap anlık görüntüleri, `botTokenSource`, `botTokenStatus`, `appTokenStatus` ve HTTP modunda
  `signingSecretStatus` gibi kimlik bilgisi kaynağı/durum alanlarını açığa çıkarır.
  `configured_unavailable`, hesabın SecretRef ile yapılandırıldığını ancak
  mevcut komut/çalışma zamanı yolunun gizli değeri çözemediğini gösterir.
- `configWrites: false`, Slack tarafından başlatılan yapılandırma yazımlarını engeller.
- İsteğe bağlı `channels.slack.defaultAccount`, yapılandırılmış bir hesap kimliğiyle eşleştiğinde varsayılan hesap seçimini geçersiz kılar.
- `channels.slack.streaming`, kanonik akış modu anahtarıdır. Eski `streamMode` ve boolean `streaming` değerleri otomatik taşınır.
- Teslim hedefleri için `user:<id>` (DM) veya `channel:<id>` kullanın.

**Tepki bildirimi modları:** `off`, `own` (varsayılan), `all`, `allowlist` (`reactionAllowlist` içinden).

**İleti dizisi oturum yalıtımı:** `thread.historyScope` ileti dizisi başına (varsayılan) veya kanal genelinde paylaşılır. `thread.inheritParent`, üst kanal transkriptini yeni ileti dizilerine kopyalar.

- `typingReaction`, bir yanıt çalışırken gelen Slack mesajına geçici bir tepki ekler, tamamlandığında kaldırır. `"hourglass_flowing_sand"` gibi bir Slack emoji kısa kodu kullanın.
- `channels.slack.execApprovals`: Slack yerel exec onay teslimi ve onaylayıcı yetkilendirmesi. Discord ile aynı şema: `enabled` (`true`/`false`/`"auto"`), `approvers` (Slack kullanıcı kimlikleri), `agentFilter`, `sessionFilter` ve `target` (`"dm"`, `"channel"` veya `"both"`).

| Eylem grubu | Varsayılan | Notlar                   |
| ----------- | ---------- | ------------------------ |
| reactions   | etkin      | Tepki ver + tepkileri listele |
| messages    | etkin      | Oku/gönder/düzenle/sil   |
| pins        | etkin      | Sabitle/sabitlemeyi kaldır/listele |
| memberInfo  | etkin      | Üye bilgisi              |
| emojiList   | etkin      | Özel emoji listesi       |

### Mattermost

Mattermost bir eklenti olarak gelir: `openclaw plugins install @openclaw/mattermost`.

```json5
{
  channels: {
    mattermost: {
      enabled: true,
      botToken: "mm-token",
      baseUrl: "https://chat.example.com",
      dmPolicy: "pairing",
      chatmode: "oncall", // oncall | onmessage | onchar
      oncharPrefixes: [">", "!"],
      groups: {
        "*": { requireMention: true },
        "team-channel-id": { requireMention: false },
      },
      commands: {
        native: true, // katılım gerektirir
        nativeSkills: true,
        callbackPath: "/api/channels/mattermost/command",
        // Reverse-proxy/public dağıtımlar için isteğe bağlı açık URL
        callbackUrl: "https://gateway.example.com/api/channels/mattermost/command",
      },
      textChunkLimit: 4000,
      chunkMode: "length",
    },
  },
}
```

Sohbet modları: `oncall` (@-mention olduğunda yanıt ver, varsayılan), `onmessage` (her mesaj), `onchar` (tetikleyici önekle başlayan mesajlar).

Mattermost yerel komutları etkin olduğunda:

- `commands.callbackPath` tam URL değil, bir yol olmalıdır (örneğin `/api/channels/mattermost/command`).
- `commands.callbackUrl`, OpenClaw ağ geçidi uç noktasına çözülmeli ve Mattermost sunucusundan erişilebilir olmalıdır.
- Yerel slash callback'leri, slash komut kaydı sırasında Mattermost tarafından döndürülen komut başına tokenlarla doğrulanır. Kayıt başarısız olursa veya hiçbir komut etkinleşmezse, OpenClaw callback'leri şu hata ile reddeder:
  `Unauthorized: invalid command token.`
- Özel/tailnet/iç callback ana makineleri için Mattermost,
  `ServiceSettings.AllowedUntrustedInternalConnections` içinde callback ana makinesini/alan adını istemek zorunda kalabilir.
  Tam URL değil, ana makine/alan adı değerlerini kullanın.
- `channels.mattermost.configWrites`: Mattermost tarafından başlatılan yapılandırma yazımlarına izin ver veya reddet.
- `channels.mattermost.requireMention`: kanallarda yanıtlamadan önce `@mention` gerektir.
- `channels.mattermost.groups.<channelId>.requireMention`: kanal başına mention-gating geçersiz kılması (varsayılan için `"*"`).
- İsteğe bağlı `channels.mattermost.defaultAccount`, yapılandırılmış bir hesap kimliğiyle eşleştiğinde varsayılan hesap seçimini geçersiz kılar.

### Signal

```json5
{
  channels: {
    signal: {
      enabled: true,
      account: "+15555550123", // isteğe bağlı hesap bağlama
      dmPolicy: "pairing",
      allowFrom: ["+15551234567", "uuid:123e4567-e89b-12d3-a456-426614174000"],
      configWrites: true,
      reactionNotifications: "own", // off | own | all | allowlist
      reactionAllowlist: ["+15551234567", "uuid:123e4567-e89b-12d3-a456-426614174000"],
      historyLimit: 50,
    },
  },
}
```

**Tepki bildirimi modları:** `off`, `own` (varsayılan), `all`, `allowlist` (`reactionAllowlist` içinden).

- `channels.signal.account`: kanal başlatmayı belirli bir Signal hesap kimliğine sabitler.
- `channels.signal.configWrites`: Signal tarafından başlatılan yapılandırma yazımlarına izin ver veya reddet.
- İsteğe bağlı `channels.signal.defaultAccount`, yapılandırılmış bir hesap kimliğiyle eşleştiğinde varsayılan hesap seçimini geçersiz kılar.

### BlueBubbles

BlueBubbles önerilen iMessage yoludur (eklenti destekli, `channels.bluebubbles` altında yapılandırılır).

```json5
{
  channels: {
    bluebubbles: {
      enabled: true,
      dmPolicy: "pairing",
      // serverUrl, password, webhookPath, group controls ve gelişmiş eylemler:
      // bkz. /channels/bluebubbles
    },
  },
}
```

- Burada kapsanan çekirdek anahtar yolları: `channels.bluebubbles`, `channels.bluebubbles.dmPolicy`.
- İsteğe bağlı `channels.bluebubbles.defaultAccount`, yapılandırılmış bir hesap kimliğiyle eşleştiğinde varsayılan hesap seçimini geçersiz kılar.
- Üst düzey `bindings[]` girdilerinde `type: "acp"`, BlueBubbles konuşmalarını kalıcı ACP oturumlarına bağlayabilir. `match.peer.id` içinde bir BlueBubbles tanıtıcısı veya hedef dizesi (`chat_id:*`, `chat_guid:*`, `chat_identifier:*`) kullanın. Ortak alan anlamları: [ACP Agents](/tr/tools/acp-agents#channel-specific-settings).
- Tam BlueBubbles kanal yapılandırması [BlueBubbles](/tr/channels/bluebubbles) içinde belgelenmiştir.

### iMessage

OpenClaw `imsg rpc` (stdio üzerinden JSON-RPC) başlatır. Daemon veya port gerekmez.

```json5
{
  channels: {
    imessage: {
      enabled: true,
      cliPath: "imsg",
      dbPath: "~/Library/Messages/chat.db",
      remoteHost: "user@gateway-host",
      dmPolicy: "pairing",
      allowFrom: ["+15555550123", "user@example.com", "chat_id:123"],
      historyLimit: 50,
      includeAttachments: false,
      attachmentRoots: ["/Users/*/Library/Messages/Attachments"],
      remoteAttachmentRoots: ["/Users/*/Library/Messages/Attachments"],
      mediaMaxMb: 16,
      service: "auto",
      region: "US",
    },
  },
}
```

- İsteğe bağlı `channels.imessage.defaultAccount`, yapılandırılmış bir hesap kimliğiyle eşleştiğinde varsayılan hesap seçimini geçersiz kılar.

- Messages DB için Full Disk Access gerekir.
- `chat_id:<id>` hedeflerini tercih edin. Sohbetleri listelemek için `imsg chats --limit 20` kullanın.
- `cliPath` bir SSH wrapper'ına işaret edebilir; SCP ek dosyası getirme için `remoteHost` (`host` veya `user@host`) ayarlayın.
- `attachmentRoots` ve `remoteAttachmentRoots`, gelen ek dosya yollarını sınırlar (varsayılan: `/Users/*/Library/Messages/Attachments`).
- SCP katı host-key denetimi kullanır, bu nedenle relay host anahtarının zaten `~/.ssh/known_hosts` içinde bulunduğundan emin olun.
- `channels.imessage.configWrites`: iMessage tarafından başlatılan yapılandırma yazımlarına izin ver veya reddet.
- Üst düzey `bindings[]` girdilerinde `type: "acp"`, iMessage konuşmalarını kalıcı ACP oturumlarına bağlayabilir. `match.peer.id` içinde normalize edilmiş bir tanıtıcı veya açık sohbet hedefi (`chat_id:*`, `chat_guid:*`, `chat_identifier:*`) kullanın. Ortak alan anlamları: [ACP Agents](/tr/tools/acp-agents#channel-specific-settings).

<Accordion title="iMessage SSH wrapper örneği">

```bash
#!/usr/bin/env bash
exec ssh -T gateway-host imsg "$@"
```

</Accordion>

### Matrix

Matrix eklenti desteklidir ve `channels.matrix` altında yapılandırılır.

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_bot_xxx",
      proxy: "http://127.0.0.1:7890",
      encryption: true,
      initialSyncLimit: 20,
      defaultAccount: "ops",
      accounts: {
        ops: {
          name: "Ops",
          userId: "@ops:example.org",
          accessToken: "syt_ops_xxx",
        },
        alerts: {
          userId: "@alerts:example.org",
          password: "secret",
          proxy: "http://127.0.0.1:7891",
        },
      },
    },
  },
}
```

- Token kimlik doğrulaması `accessToken` kullanır; parola kimlik doğrulaması `userId` + `password` kullanır.
- `channels.matrix.proxy`, Matrix HTTP trafiğini açık bir HTTP(S) proxy üzerinden yönlendirir. Adlandırılmış hesaplar bunu `channels.matrix.accounts.<id>.proxy` ile geçersiz kılabilir.
- `channels.matrix.network.dangerouslyAllowPrivateNetwork`, özel/iç homeserver'lara izin verir. `proxy` ve bu ağ katılımı birbirinden bağımsız denetimlerdir.
- `channels.matrix.defaultAccount`, çok hesaplı kurulumlarda tercih edilen hesabı seçer.
- `channels.matrix.autoJoin` varsayılan olarak `off` olduğundan, `autoJoin: "allowlist"` ile `autoJoinAllowlist` veya `autoJoin: "always"` ayarlanana kadar davet edilen odalar ve yeni DM tarzı davetler yok sayılır.
- `channels.matrix.execApprovals`: Matrix yerel exec onay teslimi ve onaylayıcı yetkilendirmesi.
  - `enabled`: `true`, `false` veya `"auto"` (varsayılan). Otomatik modda exec onayları, onaylayıcılar `approvers` veya `commands.ownerAllowFrom` içinden çözümlenebildiğinde etkinleşir.
  - `approvers`: exec isteklerini onaylamaya yetkili Matrix kullanıcı kimlikleri (ör. `@owner:example.org`).
  - `agentFilter`: isteğe bağlı aracı kimliği allowlist'i. Tüm aracılar için onay iletmek istiyorsanız atlayın.
  - `sessionFilter`: isteğe bağlı oturum anahtarı desenleri (alt dize veya regex).
  - `target`: onay istemlerinin nereye gönderileceği. `"dm"` (varsayılan), `"channel"` (kaynak oda) veya `"both"`.
  - Hesap başına geçersiz kılmalar: `channels.matrix.accounts.<id>.execApprovals`.
- `channels.matrix.dm.sessionScope`, Matrix DM'lerinin oturumlara nasıl gruplanacağını denetler: `per-user` (varsayılan) yönlendirilen eşe göre paylaşır, `per-room` ise her DM odasını yalıtır.
- Matrix durum probları ve canlı dizin aramaları, çalışma zamanı trafiğiyle aynı proxy ilkesini kullanır.
- Tam Matrix yapılandırması, hedefleme kuralları ve kurulum örnekleri [Matrix](/tr/channels/matrix) içinde belgelenmiştir.

### Microsoft Teams

Microsoft Teams eklenti desteklidir ve `channels.msteams` altında yapılandırılır.

```json5
{
  channels: {
    msteams: {
      enabled: true,
      configWrites: true,
      // appId, appPassword, tenantId, webhook, takım/kanal ilkeleri:
      // bkz. /channels/msteams
    },
  },
}
```

- Burada kapsanan çekirdek anahtar yolları: `channels.msteams`, `channels.msteams.configWrites`.
- Tam Teams yapılandırması (kimlik bilgileri, webhook, DM/grup ilkesi, takım/kanal başına geçersiz kılmalar) [Microsoft Teams](/tr/channels/msteams) içinde belgelenmiştir.

### IRC

IRC eklenti desteklidir ve `channels.irc` altında yapılandırılır.

```json5
{
  channels: {
    irc: {
      enabled: true,
      dmPolicy: "pairing",
      configWrites: true,
      nickserv: {
        enabled: true,
        service: "NickServ",
        password: "${IRC_NICKSERV_PASSWORD}",
        register: false,
        registerEmail: "bot@example.com",
      },
    },
  },
}
```

- Burada kapsanan çekirdek anahtar yolları: `channels.irc`, `channels.irc.dmPolicy`, `channels.irc.configWrites`, `channels.irc.nickserv.*`.
- İsteğe bağlı `channels.irc.defaultAccount`, yapılandırılmış bir hesap kimliğiyle eşleştiğinde varsayılan hesap seçimini geçersiz kılar.
- Tam IRC kanal yapılandırması (host/port/TLS/kanallar/allowlist'ler/mention gating) [IRC](/tr/channels/irc) içinde belgelenmiştir.

### Çok hesaplı (tüm kanallar)

Kanal başına birden fazla hesap çalıştırın (her birinin kendi `accountId` değeri vardır):

```json5
{
  channels: {
    telegram: {
      accounts: {
        default: {
          name: "Primary bot",
          botToken: "123456:ABC...",
        },
        alerts: {
          name: "Alerts bot",
          botToken: "987654:XYZ...",
        },
      },
    },
  },
}
```

- `accountId` atlandığında `default` kullanılır (CLI + yönlendirme).
- Ortam tokenları yalnızca **varsayılan** hesap için geçerlidir.
- Temel kanal ayarları, hesap başına geçersiz kılınmadıkça tüm hesaplara uygulanır.
- Her hesabı farklı bir aracıya yönlendirmek için `bindings[].match.accountId` kullanın.
- Tek hesaplı üst düzey kanal yapılandırmasındayken `openclaw channels add` (veya kanal onboarding) ile varsayılan olmayan bir hesap eklerseniz, OpenClaw önce hesap kapsamlı üst düzey tek hesaplı değerleri kanal hesap haritasına taşır; böylece asıl hesap çalışmaya devam eder. Çoğu kanal bunları `channels.<channel>.accounts.default` içine taşır; Matrix ise mevcut eşleşen adlandırılmış/varsayılan hedefi koruyabilir.
- Mevcut yalnızca kanala ait bağlamalar (`accountId` yok) varsayılan hesapla eşleşmeye devam eder; hesap kapsamlı bağlamalar isteğe bağlı kalır.
- `openclaw doctor --fix`, hesap kapsamlı üst düzey tek hesaplı değerleri o kanal için seçilen yükseltilmiş hesaba taşıyarak karışık şekilleri de onarır. Çoğu kanal `accounts.default` kullanır; Matrix ise mevcut eşleşen adlandırılmış/varsayılan hedefi koruyabilir.

### Diğer eklenti kanalları

Birçok eklenti kanalı `channels.<id>` olarak yapılandırılır ve özel kanal sayfalarında belgelenir (örneğin Feishu, Matrix, LINE, Nostr, Zalo, Nextcloud Talk, Synology Chat ve Twitch).
Tam kanal dizinine bakın: [Channels](/tr/channels).

### Grup sohbeti mention-gating

Grup mesajları varsayılan olarak **mention gerektirir** (meta veri mention'ı veya güvenli regex desenleri). WhatsApp, Telegram, Discord, Google Chat ve iMessage grup sohbetleri için geçerlidir.

**Mention türleri:**

- **Meta veri mention'ları**: Platformun yerel @-mention'ları. WhatsApp self-chat modunda yok sayılır.
- **Metin desenleri**: `agents.list[].groupChat.mentionPatterns` içindeki güvenli regex desenleri. Geçersiz desenler ve güvenli olmayan iç içe tekrarlar yok sayılır.
- Mention-gating yalnızca algılama mümkün olduğunda uygulanır (yerel mention'lar veya en az bir desen).

```json5
{
  messages: {
    groupChat: { historyLimit: 50 },
  },
  agents: {
    list: [{ id: "main", groupChat: { mentionPatterns: ["@openclaw", "openclaw"] } }],
  },
}
```

`messages.groupChat.historyLimit` genel varsayılanı belirler. Kanallar bunu `channels.<channel>.historyLimit` ile (veya hesap başına) geçersiz kılabilir. Devre dışı bırakmak için `0` ayarlayın.

#### DM geçmiş sınırları

```json5
{
  channels: {
    telegram: {
      dmHistoryLimit: 30,
      dms: {
        "123456789": { historyLimit: 50 },
      },
    },
  },
}
```

Çözümleme: DM başına geçersiz kılma → sağlayıcı varsayılanı → sınır yok (hepsi tutulur).

Desteklenenler: `telegram`, `whatsapp`, `discord`, `slack`, `signal`, `imessage`, `msteams`.

#### Self-chat modu

Kendi numaranızı `allowFrom` içine ekleyerek self-chat modunu etkinleştirin (yerel @-mention'ları yok sayar, yalnızca metin desenlerine yanıt verir):

```json5
{
  channels: {
    whatsapp: {
      allowFrom: ["+15555550123"],
      groups: { "*": { requireMention: true } },
    },
  },
  agents: {
    list: [
      {
        id: "main",
        groupChat: { mentionPatterns: ["reisponde", "@openclaw"] },
      },
    ],
  },
}
```

### Komutlar (sohbet komutu işleme)

```json5
{
  commands: {
    native: "auto", // desteklendiğinde yerel komutları kaydet
    text: true, // sohbet mesajlarında /commands ayrıştır
    bash: false, // ! izni ver (takma ad: /bash)
    bashForegroundMs: 2000,
    config: false, // /config izni ver
    debug: false, // /debug izni ver
    restart: false, // /restart + gateway restart tool izni ver
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    useAccessGroups: true,
  },
}
```

<Accordion title="Komut ayrıntıları">

- Metin komutları, başında `/` olan **bağımsız** mesajlar olmalıdır.
- `native: "auto"`, Discord/Telegram için yerel komutları açar, Slack'i kapalı bırakır.
- Kanal başına geçersiz kılma: `channels.discord.commands.native` (bool veya `"auto"`). `false`, daha önce kaydedilmiş komutları temizler.
- `channels.telegram.customCommands`, fazladan Telegram bot menü girdileri ekler.
- `bash: true`, host shell için `! <cmd>` etkinleştirir. `tools.elevated.enabled` ve gönderenin `tools.elevated.allowFrom.<channel>` içinde olmasını gerektirir.
- `config: true`, `/config` etkinleştirir (`openclaw.json` okur/yazar). Ağ geçidi `chat.send` istemcileri için kalıcı `/config set|unset` yazımları ayrıca `operator.admin` gerektirir; salt okunur `/config show` normal yazma kapsamlı operatör istemcilerinde kullanılabilir kalır.
- `channels.<provider>.configWrites`, kanal başına yapılandırma değişimlerini denetler (varsayılan: true).
- Çok hesaplı kanallarda `channels.<provider>.accounts.<id>.configWrites` de o hesabı hedefleyen yazımları denetler (örneğin `/allowlist --config --account <id>` veya `/config set channels.<provider>.accounts.<id>...`).
- `allowFrom`, sağlayıcı başınadır. Ayarlandığında **tek** yetkilendirme kaynağı budur (kanal allowlist/eşleme ve `useAccessGroups` yok sayılır).
- `useAccessGroups: false`, `allowFrom` ayarlı değilse komutların erişim grubu ilkelerini atlamasına izin verir.

</Accordion>

---

## Aracı varsayılanları

### `agents.defaults.workspace`

Varsayılan: `~/.openclaw/workspace`.

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
}
```

### `agents.defaults.repoRoot`

Sistem isteminin Runtime satırında gösterilen isteğe bağlı depo kökü. Ayarlanmamışsa OpenClaw, çalışma alanından yukarı doğru yürüyerek otomatik algılar.

```json5
{
  agents: { defaults: { repoRoot: "~/Projects/openclaw" } },
}
```

### `agents.defaults.skills`

`agents.list[].skills` ayarlamayan aracılar için isteğe bağlı varsayılan Skill allowlist'i.

```json5
{
  agents: {
    defaults: { skills: ["github", "weather"] },
    list: [
      { id: "writer" }, // github, weather devralır
      { id: "docs", skills: ["docs-search"] }, // varsayılanların yerine geçer
      { id: "locked-down", skills: [] }, // Skill yok
    ],
  },
}
```

- Varsayılan olarak sınırsız Skills için `agents.defaults.skills` alanını atlayın.
- Varsayılanları devralmak için `agents.list[].skills` alanını atlayın.
- Hiç Skill olmaması için `agents.list[].skills: []` ayarlayın.
- Boş olmayan bir `agents.list[].skills` listesi, o aracı için son kümedir; varsayılanlarla birleşmez.

### `agents.defaults.skipBootstrap`

Çalışma alanı bootstrap dosyalarının (`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md`) otomatik oluşturulmasını devre dışı bırakır.

```json5
{
  agents: { defaults: { skipBootstrap: true } },
}
```

### `agents.defaults.contextInjection`

Çalışma alanı bootstrap dosyalarının sistem istemine ne zaman ekleneceğini denetler. Varsayılan: `"always"`.

- `"continuation-skip"`: güvenli devam turları (tamamlanmış bir asistan yanıtından sonra), çalışma alanı bootstrap yeniden eklemesini atlayarak istem boyutunu azaltır. Heartbeat çalıştırmaları ve sıkıştırma sonrası yeniden denemeler yine bağlamı yeniden oluşturur.

```json5
{
  agents: { defaults: { contextInjection: "continuation-skip" } },
}
```

### `agents.defaults.bootstrapMaxChars`

Kısaltmadan önce çalışma alanı bootstrap dosyası başına azami karakter sayısı. Varsayılan: `20000`.

```json5
{
  agents: { defaults: { bootstrapMaxChars: 20000 } },
}
```

### `agents.defaults.bootstrapTotalMaxChars`

Tüm çalışma alanı bootstrap dosyaları arasında eklenen toplam azami karakter sayısı. Varsayılan: `150000`.

```json5
{
  agents: { defaults: { bootstrapTotalMaxChars: 150000 } },
}
```

### `agents.defaults.bootstrapPromptTruncationWarning`

Bootstrap bağlamı kısaltıldığında aracıya görünen uyarı metnini denetler.
Varsayılan: `"once"`.

- `"off"`: sistem istemine asla uyarı metni ekleme.
- `"once"`: her benzersiz kısaltma imzası için uyarıyı bir kez ekle (önerilir).
- `"always"`: kısaltma mevcut olduğunda her çalıştırmada uyarı ekle.

```json5
{
  agents: { defaults: { bootstrapPromptTruncationWarning: "once" } }, // off | once | always
}
```

### `agents.defaults.imageMaxDimensionPx`

Sağlayıcı çağrılarından önce transkript/araç görüntü bloklarında en uzun görüntü kenarı için azami piksel boyutu.
Varsayılan: `1200`.

Daha düşük değerler genelde ekran görüntüsü ağırlıklı çalıştırmalarda vision token kullanımını ve istek yükü boyutunu azaltır.
Daha yüksek değerler daha fazla görsel ayrıntıyı korur.

```json5
{
  agents: { defaults: { imageMaxDimensionPx: 1200 } },
}
```

### `agents.defaults.userTimezone`

Sistem istemi bağlamı için saat dilimi (mesaj zaman damgaları için değil). Host saat dilimine geri döner.

```json5
{
  agents: { defaults: { userTimezone: "America/Chicago" } },
}
```

### `agents.defaults.timeFormat`

Sistem istemindeki saat biçimi. Varsayılan: `auto` (OS tercihi).

```json5
{
  agents: { defaults: { timeFormat: "auto" } }, // auto | 12 | 24
}
```

### `agents.defaults.model`

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": { alias: "opus" },
        "minimax/MiniMax-M2.7": { alias: "minimax" },
      },
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["minimax/MiniMax-M2.7"],
      },
      imageModel: {
        primary: "openrouter/qwen/qwen-2.5-vl-72b-instruct:free",
        fallbacks: ["openrouter/google/gemini-2.0-flash-vision:free"],
      },
      imageGenerationModel: {
        primary: "openai/gpt-image-1",
        fallbacks: ["google/gemini-3.1-flash-image-preview"],
      },
      videoGenerationModel: {
        primary: "qwen/wan2.6-t2v",
        fallbacks: ["qwen/wan2.6-i2v"],
      },
      pdfModel: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["openai/gpt-5.4-mini"],
      },
      params: { cacheRetention: "long" }, // genel varsayılan sağlayıcı parametreleri
      pdfMaxBytesMb: 10,
      pdfMaxPages: 20,
      thinkingDefault: "low",
      verboseDefault: "off",
      elevatedDefault: "on",
      timeoutSeconds: 600,
      mediaMaxMb: 5,
      contextTokens: 200000,
      maxConcurrent: 3,
    },
  },
}
```

- `model`: bir dize (`"provider/model"`) veya bir nesne (`{ primary, fallbacks }`) kabul eder.
  - Dize biçimi yalnızca birincil modeli ayarlar.
  - Nesne biçimi birincil modeli ve sıralı failover modellerini ayarlar.
- `imageModel`: bir dize (`"provider/model"`) veya bir nesne (`{ primary, fallbacks }`) kabul eder.
  - `image` araç yolu tarafından vision-model yapılandırması olarak kullanılır.
  - Ayrıca seçili/varsayılan model görüntü girdisini kabul edemediğinde geri dönüş yönlendirmesi olarak kullanılır.
- `imageGenerationModel`: bir dize (`"provider/model"`) veya bir nesne (`{ primary, fallbacks }`) kabul eder.
  - Paylaşılan görüntü üretme yeteneği ve gelecekte görüntü üreten tüm araç/eklenti yüzeyleri tarafından kullanılır.
  - Tipik değerler: yerel Gemini görüntü üretimi için `google/gemini-3.1-flash-image-preview`, fal için `fal/fal-ai/flux/dev` veya OpenAI Images için `openai/gpt-image-1`.
  - Bir sağlayıcı/modeli doğrudan seçerseniz, eşleşen sağlayıcı auth/API anahtarını da yapılandırın (örneğin `google/*` için `GEMINI_API_KEY` veya `GOOGLE_API_KEY`, `openai/*` için `OPENAI_API_KEY`, `fal/*` için `FAL_KEY`).
  - Atlanırsa `image_generate`, auth destekli bir sağlayıcı varsayılanını yine de çıkarabilir. Önce geçerli varsayılan sağlayıcıyı, sonra sağlayıcı kimliği sırasındaki kalan kayıtlı görüntü üretim sağlayıcılarını dener.
- `musicGenerationModel`: bir dize (`"provider/model"`) veya bir nesne (`{ primary, fallbacks }`) kabul eder.
  - Paylaşılan müzik üretme yeteneği ve yerleşik `music_generate` aracı tarafından kullanılır.
  - Tipik değerler: `google/lyria-3-clip-preview`, `google/lyria-3-pro-preview` veya `minimax/music-2.5+`.
  - Atlanırsa `music_generate`, auth destekli bir sağlayıcı varsayılanını yine de çıkarabilir. Önce geçerli varsayılan sağlayıcıyı, sonra sağlayıcı kimliği sırasındaki kalan kayıtlı müzik üretim sağlayıcılarını dener.
  - Bir sağlayıcı/modeli doğrudan seçerseniz, eşleşen sağlayıcı auth/API anahtarını da yapılandırın.
- `videoGenerationModel`: bir dize (`"provider/model"`) veya bir nesne (`{ primary, fallbacks }`) kabul eder.
  - Paylaşılan video üretme yeteneği ve yerleşik `video_generate` aracı tarafından kullanılır.
  - Tipik değerler: `qwen/wan2.6-t2v`, `qwen/wan2.6-i2v`, `qwen/wan2.6-r2v`, `qwen/wan2.6-r2v-flash` veya `qwen/wan2.7-r2v`.
  - Atlanırsa `video_generate`, auth destekli bir sağlayıcı varsayılanını yine de çıkarabilir. Önce geçerli varsayılan sağlayıcıyı, sonra sağlayıcı kimliği sırasındaki kalan kayıtlı video üretim sağlayıcılarını dener.
  - Bir sağlayıcı/modeli doğrudan seçerseniz, eşleşen sağlayıcı auth/API anahtarını da yapılandırın.
  - Paketlenmiş Qwen video üretim sağlayıcısı şu anda en fazla 1 çıktı videosu, 1 giriş görüntüsü, 4 giriş videosu, 10 saniye süre ve sağlayıcı düzeyinde `size`, `aspectRatio`, `resolution`, `audio` ve `watermark` seçeneklerini destekler.
- `pdfModel`: bir dize (`"provider/model"`) veya bir nesne (`{ primary, fallbacks }`) kabul eder.
  - `pdf` aracı tarafından model yönlendirmesi için kullanılır.
  - Atlanırsa PDF aracı sırasıyla `imageModel` ve çözümlenen oturum/varsayılan modele geri döner.
- `pdfMaxBytesMb`: çağrı zamanında `maxBytesMb` geçirilmediğinde `pdf` aracı için varsayılan PDF boyut sınırı.
- `pdfMaxPages`: `pdf` aracında extraction fallback modu tarafından dikkate alınan varsayılan azami sayfa sayısı.
- `verboseDefault`: aracılar için varsayılan verbose düzeyi. Değerler: `"off"`, `"on"`, `"full"`. Varsayılan: `"off"`.
- `elevatedDefault`: aracılar için varsayılan elevated-output düzeyi. Değerler: `"off"`, `"on"`, `"ask"`, `"full"`. Varsayılan: `"on"`.
- `model.primary`: `provider/model` biçimi (örn. `openai/gpt-5.4`). Sağlayıcıyı atlayırsanız OpenClaw önce bir takma adı, sonra tam model kimliği için benzersiz bir yapılandırılmış sağlayıcı eşleşmesini dener ve yalnızca bundan sonra yapılandırılmış varsayılan sağlayıcıya geri döner (eski uyumluluk davranışı, bu yüzden açık `provider/model` tercih edin). O sağlayıcı artık yapılandırılmış varsayılan modeli sunmuyorsa, OpenClaw eski ve kaldırılmış bir sağlayıcı varsayılanını göstermek yerine ilk yapılandırılmış sağlayıcı/modele geri döner.
- `models`: `/model` için yapılandırılmış model kataloğu ve allowlist. Her girdi `alias` (kısayol) ve `params` (sağlayıcıya özgü; örneğin `temperature`, `maxTokens`, `cacheRetention`, `context1m`) içerebilir.
- `params`: tüm modellere uygulanan genel varsayılan sağlayıcı parametreleri. `agents.defaults.params` altında ayarlanır (örn. `{ cacheRetention: "long" }`).
- `params` birleştirme önceliği (yapılandırma): `agents.defaults.params` (genel taban), `agents.defaults.models["provider/model"].params` (model başına) tarafından geçersiz kılınır, ardından `agents.list[].params` (eşleşen aracı kimliği) anahtar bazında geçersiz kılar. Ayrıntılar için bkz. [Prompt Caching](/tr/reference/prompt-caching).
- Bu alanları değiştiren yapılandırma yazıcıları (örneğin `/models set`, `/models set-image` ve fallback ekle/kaldır komutları), kanonik nesne biçimini kaydeder ve mümkün olduğunda mevcut fallback listelerini korur.
- `maxConcurrent`: oturumlar arasında paralel aracı çalıştırmalarının azami sayısı (her oturum yine serileştirilir). Varsayılan: 4.

**Yerleşik takma ad kısayolları** (yalnızca model `agents.defaults.models` içindeyse geçerlidir):

| Takma ad            | Model                                  |
| ------------------- | -------------------------------------- |
| `opus`              | `anthropic/claude-opus-4-6`            |
| `sonnet`            | `anthropic/claude-sonnet-4-6`          |
| `gpt`               | `openai/gpt-5.4`                       |
| `gpt-mini`          | `openai/gpt-5.4-mini`                  |
| `gpt-nano`          | `openai/gpt-5.4-nano`                  |
| `gemini`            | `google/gemini-3.1-pro-preview`        |
| `gemini-flash`      | `google/gemini-3-flash-preview`        |
| `gemini-flash-lite` | `google/gemini-3.1-flash-lite-preview` |

Yapılandırdığınız takma adlar her zaman varsayılanların önüne geçer.

Z.AI GLM-4.x modelleri, `--thinking off` ayarlamadığınız veya `agents.defaults.models["zai/<model>"].params.thinking` değerini kendiniz tanımlamadığınız sürece thinking modunu otomatik etkinleştirir.
Z.AI modelleri araç çağrısı akışı için varsayılan olarak `tool_stream` etkinleştirir. Devre dışı bırakmak için `agents.defaults.models["zai/<model>"].params.tool_stream` değerini `false` yapın.
Anthropic Claude 4.6 modelleri, açık bir thinking düzeyi ayarlanmamışsa varsayılan olarak `adaptive` thinking kullanır.

### `agents.defaults.cliBackends`

Yalnızca metin kullanan fallback çalıştırmaları (araç çağrısı yok) için isteğe bağlı CLI backend'leri. API sağlayıcıları başarısız olduğunda yedek olarak kullanışlıdır.

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "codex-cli": {
          command: "/opt/homebrew/bin/codex",
        },
        "my-cli": {
          command: "my-cli",
          args: ["--json"],
          output: "json",
          modelArg: "--model",
          sessionArg: "--session",
          sessionMode: "existing",
          systemPromptArg: "--system",
          systemPromptWhen: "first",
          imageArg: "--image",
          imageMode: "repeat",
        },
      },
    },
  },
}
```

- CLI backend'leri metin önceliklidir; araçlar her zaman devre dışıdır.
- `sessionArg` ayarlanmışsa oturumlar desteklenir.
- `imageArg` dosya yollarını kabul ediyorsa görüntü aktarımı desteklenir.

### `agents.defaults.heartbeat`

Periyodik heartbeat çalıştırmaları.

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // 0m devre dışı bırakır
        model: "openai/gpt-5.4-mini",
        includeReasoning: false,
        lightContext: false, // varsayılan: false; true yalnızca çalışma alanı bootstrap dosyalarından HEARTBEAT.md tutar
        isolatedSession: false, // varsayılan: false; true her heartbeat'i yeni bir oturumda çalıştırır (konuşma geçmişi yok)
        session: "main",
        to: "+15555550123",
        directPolicy: "allow", // allow (varsayılan) | block
        target: "none", // varsayılan: none | seçenekler: last | whatsapp | telegram | discord | ...
        prompt: "Read HEARTBEAT.md if it exists...",
        ackMaxChars: 300,
        suppressToolErrorWarnings: false,
      },
    },
  },
}
```

- `every`: süre dizesi (ms/s/m/h). Varsayılan: `30m` (API-key auth) veya `1h` (OAuth auth). Devre dışı bırakmak için `0m` ayarlayın.
- `suppressToolErrorWarnings`: true olduğunda, heartbeat çalıştırmaları sırasında araç hata uyarı yüklerini bastırır.
- `directPolicy`: doğrudan/DM teslim ilkesi. `allow` (varsayılan) doğrudan hedef teslimine izin verir. `block` doğrudan hedef teslimini bastırır ve `reason=dm-blocked` üretir.
- `lightContext`: true olduğunda heartbeat çalıştırmaları hafif bootstrap bağlamı kullanır ve çalışma alanı bootstrap dosyalarından yalnızca `HEARTBEAT.md` tutar.
- `isolatedSession`: true olduğunda her heartbeat, önceki konuşma geçmişi olmayan yeni bir oturumda çalışır. Cron `sessionTarget: "isolated"` ile aynı yalıtım deseni. Heartbeat başına token maliyetini yaklaşık ~100K'dan ~2-5K tokena düşürür.
- Aracı başına: `agents.list[].heartbeat` ayarlayın. Herhangi bir aracı `heartbeat` tanımladığında heartbeat yalnızca **o aracılar** için çalışır.
- Heartbeat'ler tam aracı turları çalıştırır — daha kısa aralıklar daha fazla token yakar.

### `agents.defaults.compaction`

```json5
{
  agents: {
    defaults: {
      compaction: {
        mode: "safeguard", // default | safeguard
        timeoutSeconds: 900,
        reserveTokensFloor: 24000,
        identifierPolicy: "strict", // strict | off | custom
        identifierInstructions: "Preserve deployment IDs, ticket IDs, and host:port pairs exactly.", // identifierPolicy=custom olduğunda kullanılır
        postCompactionSections: ["Session Startup", "Red Lines"], // [] yeniden eklemeyi devre dışı bırakır
        model: "openrouter/anthropic/claude-sonnet-4-6", // isteğe bağlı yalnızca sıkıştırma için model geçersiz kılması
        notifyUser: true, // sıkıştırma başladığında kullanıcıya kısa bir bildirim gönder (varsayılan: false)
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 6000,
          systemPrompt: "Session nearing compaction. Store durable memories now.",
          prompt: "Write any lasting notes to memory/YYYY-MM-DD.md; reply with the exact silent token NO_REPLY if nothing to store.",
        },
      },
    },
  },
}
```

- `mode`: `default` veya `safeguard` (uzun geçmişler için parçalı özetleme). Bkz. [Compaction](/tr/concepts/compaction).
- `timeoutSeconds`: OpenClaw'ın tek bir sıkıştırma işlemi için iptal etmeden önce izin verdiği azami saniye. Varsayılan: `900`.
- `identifierPolicy`: `strict` (varsayılan), `off` veya `custom`. `strict`, sıkıştırma özetlemesi sırasında yerleşik opak tanımlayıcı koruma rehberliğini başa ekler.
- `identifierInstructions`: `identifierPolicy=custom` olduğunda kullanılan isteğe bağlı özel tanımlayıcı koruma metni.
- `postCompactionSections`: sıkıştırma sonrası yeniden eklenecek isteğe bağlı AGENTS.md H2/H3 bölüm adları. Varsayılan `["Session Startup", "Red Lines"]`; devre dışı bırakmak için `[]` ayarlayın. Ayarlanmamışsa veya açıkça bu varsayılan çift olarak ayarlanmışsa, eski `Every Session`/`Safety` başlıkları da eski uyumluluk geri dönüşü olarak kabul edilir.
- `model`: yalnızca sıkıştırma özetlemesi için isteğe bağlı `provider/model-id` geçersiz kılması. Ana oturum bir modeli korurken sıkıştırma özetleri başka bir modelde çalışsın istiyorsanız bunu kullanın; ayarlanmazsa sıkıştırma oturumun birincil modelini kullanır.
- `notifyUser`: `true` olduğunda sıkıştırma başladığında kullanıcıya kısa bir bildirim gönderir (örneğin "Compacting context..."). Sıkıştırmayı sessiz tutmak için varsayılan olarak devre dışıdır.
- `memoryFlush`: dayanıklı anıları depolamak için otomatik sıkıştırmadan önce sessiz aracı turu. Çalışma alanı salt okunursa atlanır.

### `agents.defaults.contextPruning`

LLM'ye göndermeden önce bellek içi bağlamdan **eski araç sonuçlarını** budar. Diskteki oturum geçmişini **değiştirmez**.

```json5
{
  agents: {
    defaults: {
      contextPruning: {
        mode: "cache-ttl", // off | cache-ttl
        ttl: "1h", // süre (ms/s/m/h), varsayılan birim: dakika
        keepLastAssistants: 3,
        softTrimRatio: 0.3,
        hardClearRatio: 0.5,
        minPrunableToolChars: 50000,
        softTrim: { maxChars: 4000, headChars: 1500, tailChars: 1500 },
        hardClear: { enabled: true, placeholder: "[Old tool result content cleared]" },
        tools: { deny: ["browser", "canvas"] },
      },
    },
  },
}
```

<Accordion title="cache-ttl modu davranışı">

- `mode: "cache-ttl"` budama geçişlerini etkinleştirir.
- `ttl`, budamanın ne kadar sonra yeniden çalışabileceğini denetler (son önbellek temasından sonra).
- Budama önce büyük araç sonuçlarını yumuşak biçimde kısaltır, gerekirse daha eski araç sonuçlarını sert biçimde temizler.

**Soft-trim**, başı ve sonu korur ve ortaya `...` ekler.

**Hard-clear**, tüm araç sonucunu yer tutucu ile değiştirir.

Notlar:

- Görüntü blokları asla kırpılmaz/temizlenmez.
- Oranlar karakter tabanlıdır (yaklaşık), tam token sayıları değildir.
- `keepLastAssistants` sayısından daha az asistan mesajı varsa budama atlanır.

</Accordion>

Davranış ayrıntıları için bkz. [Session Pruning](/tr/concepts/session-pruning).

### Blok akışı

```json5
{
  agents: {
    defaults: {
      blockStreamingDefault: "off", // on | off
      blockStreamingBreak: "text_end", // text_end | message_end
      blockStreamingChunk: { minChars: 800, maxChars: 1200 },
      blockStreamingCoalesce: { idleMs: 1000 },
      humanDelay: { mode: "natural" }, // off | natural | custom (minMs/maxMs kullanın)
    },
  },
}
```

- Telegram dışındaki kanallarda blok yanıtlarını etkinleştirmek için açık `*.blockStreaming: true` gerekir.
- Kanal geçersiz kılmaları: `channels.<channel>.blockStreamingCoalesce` (ve hesap başına varyantları). Signal/Slack/Discord/Google Chat varsayılanı `minChars: 1500`.
- `humanDelay`: blok yanıtları arasında rastgele duraklama. `natural` = 800–2500ms. Aracı başına geçersiz kılma: `agents.list[].humanDelay`.

Davranış ve parçalara ayırma ayrıntıları için bkz. [Streaming](/tr/concepts/streaming).

### Yazıyor göstergeleri

```json5
{
  agents: {
    defaults: {
      typingMode: "instant", // never | instant | thinking | message
      typingIntervalSeconds: 6,
    },
  },
}
```

- Varsayılanlar: doğrudan sohbetler/mention'lar için `instant`, mention içermeyen grup sohbetleri için `message`.
- Oturum başına geçersiz kılmalar: `session.typingMode`, `session.typingIntervalSeconds`.

Bkz. [Typing Indicators](/tr/concepts/typing-indicators).

<a id="agentsdefaultssandbox"></a>

### `agents.defaults.sandbox`

Gömülü aracı için isteğe bağlı sandboxing. Tam kılavuz için bkz. [Sandboxing](/tr/gateway/sandboxing).

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main", // off | non-main | all
        backend: "docker", // docker | ssh | openshell
        scope: "agent", // session | agent | shared
        workspaceAccess: "none", // none | ro | rw
        workspaceRoot: "~/.openclaw/sandboxes",
        docker: {
          image: "openclaw-sandbox:bookworm-slim",
          containerPrefix: "openclaw-sbx-",
          workdir: "/workspace",
          readOnlyRoot: true,
          tmpfs: ["/tmp", "/var/tmp", "/run"],
          network: "none",
          user: "1000:1000",
          capDrop: ["ALL"],
          env: { LANG: "C.UTF-8" },
          setupCommand: "apt-get update && apt-get install -y git curl jq",
          pidsLimit: 256,
          memory: "1g",
          memorySwap: "2g",
          cpus: 1,
          ulimits: {
            nofile: { soft: 1024, hard: 2048 },
            nproc: 256,
          },
          seccompProfile: "/path/to/seccomp.json",
          apparmorProfile: "openclaw-sandbox",
          dns: ["1.1.1.1", "8.8.8.8"],
          extraHosts: ["internal.service:10.0.0.5"],
          binds: ["/home/user/source:/source:rw"],
        },
        ssh: {
          target: "user@gateway-host:22",
          command: "ssh",
          workspaceRoot: "/tmp/openclaw-sandboxes",
          strictHostKeyChecking: true,
          updateHostKeys: true,
          identityFile: "~/.ssh/id_ed25519",
          certificateFile: "~/.ssh/id_ed25519-cert.pub",
          knownHostsFile: "~/.ssh/known_hosts",
          // SecretRef / satır içi içerikler de desteklenir:
          // identityData: { source: "env", provider: "default", id: "SSH_IDENTITY" },
          // certificateData: { source: "env", provider: "default", id: "SSH_CERTIFICATE" },
          // knownHostsData: { source: "env", provider: "default", id: "SSH_KNOWN_HOSTS" },
        },
        browser: {
          enabled: false,
          image: "openclaw-sandbox-browser:bookworm-slim",
          network: "openclaw-sandbox-browser",
          cdpPort: 9222,
          cdpSourceRange: "172.21.0.1/32",
          vncPort: 5900,
          noVncPort: 6080,
          headless: false,
          enableNoVnc: true,
          allowHostControl: false,
          autoStart: true,
          autoStartTimeoutMs: 12000,
        },
        prune: {
          idleHours: 24,
          maxAgeDays: 7,
        },
      },
    },
  },
  tools: {
    sandbox: {
      tools: {
        allow: [
          "exec",
          "process",
          "read",
          "write",
          "edit",
          "apply_patch",
          "sessions_list",
          "sessions_history",
          "sessions_send",
          "sessions_spawn",
          "session_status",
        ],
        deny: ["browser", "canvas", "nodes", "cron", "discord", "gateway"],
      },
    },
  },
}
```

<Accordion title="Sandbox ayrıntıları">

**Backend:**

- `docker`: yerel Docker çalışma zamanı (varsayılan)
- `ssh`: genel SSH destekli uzak çalışma zamanı
- `openshell`: OpenShell çalışma zamanı

`backend: "openshell"` seçildiğinde, çalışma zamanına özgü ayarlar
`plugins.entries.openshell.config` altına taşınır.

**SSH backend yapılandırması:**

- `target`: `user@host[:port]` biçiminde SSH hedefi
- `command`: SSH istemci komutu (varsayılan: `ssh`)
- `workspaceRoot`: kapsam başına çalışma alanları için kullanılan mutlak uzak kök
- `identityFile` / `certificateFile` / `knownHostsFile`: OpenSSH'ye geçirilen mevcut yerel dosyalar
- `identityData` / `certificateData` / `knownHostsData`: OpenClaw'ın çalışma zamanında geçici dosyalara dönüştürdüğü satır içi içerikler veya SecretRef'ler
- `strictHostKeyChecking` / `updateHostKeys`: OpenSSH host-key ilkesi düğmeleri

**SSH auth önceliği:**

- `identityData`, `identityFile` değerinin önüne geçer
- `certificateData`, `certificateFile` değerinin önüne geçer
- `knownHostsData`, `knownHostsFile` değerinin önüne geçer
- SecretRef destekli `*Data` değerleri, sandbox oturumu başlamadan önce etkin secrets çalışma zamanı anlık görüntüsünden çözülür

**SSH backend davranışı:**

- oluşturma veya yeniden oluşturmadan sonra uzak çalışma alanını bir kez tohumlar
- ardından uzak SSH çalışma alanını kanonik tutar
- `exec`, dosya araçları ve medya yollarını SSH üzerinden yönlendirir
- uzak değişiklikleri otomatik olarak hosta geri eşitlemez
- sandbox tarayıcı kapsayıcılarını desteklemez

**Çalışma alanı erişimi:**

- `none`: `~/.openclaw/sandboxes` altında kapsam başına sandbox çalışma alanı
- `ro`: `/workspace` altında sandbox çalışma alanı, `/agent` altında salt okunur bağlanmış aracı çalışma alanı
- `rw`: `/workspace` altında okuma/yazma bağlanmış aracı çalışma alanı

**Kapsam:**

- `session`: oturum başına kapsayıcı + çalışma alanı
- `agent`: aracı başına bir kapsayıcı + çalışma alanı (varsayılan)
- `shared`: paylaşılan kapsayıcı ve çalışma alanı (oturumlar arası yalıtım yok)

**OpenShell eklenti yapılandırması:**

```json5
{
  plugins: {
    entries: {
      openshell: {
        enabled: true,
        config: {
          mode: "mirror", // mirror | remote
          from: "openclaw",
          remoteWorkspaceDir: "/sandbox",
          remoteAgentWorkspaceDir: "/agent",
          gateway: "lab", // isteğe bağlı
          gatewayEndpoint: "https://lab.example", // isteğe bağlı
          policy: "strict", // isteğe bağlı OpenShell ilke kimliği
          providers: ["openai"], // isteğe bağlı
          autoProviders: true,
          timeoutSeconds: 120,
        },
      },
    },
  },
}
```

**OpenShell modu:**

- `mirror`: exec öncesi uzağı yerelden tohumla, exec sonrası geri eşitle; yerel çalışma alanı kanonik kalır
- `remote`: sandbox oluşturulduğunda uzağı bir kez tohumla, ardından uzak çalışma alanını kanonik tut

`remote` modunda, OpenClaw dışında host üzerinde yapılan yerel düzenlemeler tohumlama adımından sonra sandbox'a otomatik eşitlenmez.
Taşıma SSH ile OpenShell sandbox'ına yapılır, ancak sandbox yaşam döngüsüne ve isteğe bağlı mirror sync'e eklenti sahip olur.

**`setupCommand`**, kapsayıcı oluşturulduktan sonra bir kez çalışır (`sh -lc` üzerinden). Ağ çıkışı, yazılabilir kök, root kullanıcı gerekir.

**Kapsayıcılar varsayılan olarak `network: "none"` ile gelir** — aracı dış erişim gerektiriyorsa `"bridge"` (veya özel bir bridge ağı) olarak ayarlayın.
`"host"` engellenir. `"container:<id>"`, varsayılan olarak engellenir; yalnızca
`sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true` açıkça ayarlanırsa izin verilir (yalnızca acil durum).

**Gelen ek dosyalar**, etkin çalışma alanındaki `media/inbound/*` içine aşamalandırılır.

**`docker.binds`**, ek host dizinlerini bağlar; genel ve aracı başına bind'ler birleştirilir.

**Sandboxed browser** (`sandbox.browser.enabled`): kapsayıcı içinde Chromium + CDP. noVNC URL'si sistem istemine eklenir. `openclaw.json` içinde `browser.enabled` gerektirmez.
noVNC gözlemci erişimi varsayılan olarak VNC auth kullanır ve OpenClaw paylaşılan URL'de parolayı açığa çıkarmak yerine kısa ömürlü token URL üretir.

- `allowHostControl: false` (varsayılan), sandbox oturumlarının host tarayıcıyı hedeflemesini engeller.
- `network` varsayılanı `openclaw-sandbox-browser` (ayrılmış bridge ağı). Yalnızca genel bridge bağlantısı istiyorsanız `bridge` olarak ayarlayın.
- `cdpSourceRange`, isteğe bağlı olarak CDP girişini kapsayıcı kenarında bir CIDR aralığıyla sınırlar (örneğin `172.21.0.1/32`).
- `sandbox.browser.binds`, ek host dizinlerini yalnızca sandbox tarayıcı kapsayıcısına bağlar. Ayarlandığında (`[]` dahil), tarayıcı kapsayıcısı için `docker.binds` değerinin yerine geçer.
- Başlatma varsayılanları `scripts/sandbox-browser-entrypoint.sh` içinde tanımlanır ve kapsayıcı hostları için ayarlanır:
  - `--remote-debugging-address=127.0.0.1`
  - `--remote-debugging-port=<derived from OPENCLAW_BROWSER_CDP_PORT>`
  - `--user-data-dir=${HOME}/.chrome`
  - `--no-first-run`
  - `--no-default-browser-check`
  - `--disable-3d-apis`
  - `--disable-gpu`
  - `--disable-software-rasterizer`
  - `--disable-dev-shm-usage`
  - `--disable-background-networking`
  - `--disable-features=TranslateUI`
  - `--disable-breakpad`
  - `--disable-crash-reporter`
  - `--renderer-process-limit=2`
  - `--no-zygote`
  - `--metrics-recording-only`
  - `--disable-extensions` (varsayılan olarak etkin)
  - `--disable-3d-apis`, `--disable-software-rasterizer` ve `--disable-gpu`
    varsayılan olarak etkindir ve WebGL/3D kullanımı gerektiriyorsa
    `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0` ile devre dışı bırakılabilir.
  - `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0`, iş akışınız
    uzantılara bağlıysa uzantıları yeniden etkinleştirir.
  - `--renderer-process-limit=2`,
    `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>` ile değiştirilebilir; Chromium'un
    varsayılan işlem sınırını kullanmak için `0` ayarlayın.
  - ayrıca `noSandbox` etkin olduğunda `--no-sandbox` ve `--disable-setuid-sandbox`.
  - Varsayılanlar kapsayıcı görüntüsünün temel çizgisidir; kapsayıcı varsayılanlarını değiştirmek için
    özel bir giriş noktası olan özel bir tarayıcı görüntüsü kullanın.

</Accordion>

Tarayıcı sandboxing ve `sandbox.docker.binds` şu anda yalnızca Docker'da desteklenir.

Görüntüleri derleyin:

```bash
scripts/sandbox-setup.sh           # ana sandbox görüntüsü
scripts/sandbox-browser-setup.sh   # isteğe bağlı tarayıcı görüntüsü
```

### `agents.list` (aracı başına geçersiz kılmalar)

```json5
{
  agents: {
    list: [
      {
        id: "main",
        default: true,
        name: "Main Agent",
        workspace: "~/.openclaw/workspace",
        agentDir: "~/.openclaw/agents/main/agent",
        model: "anthropic/claude-opus-4-6", // veya { primary, fallbacks }
        thinkingDefault: "high", // aracı başına thinking düzeyi geçersiz kılması
        reasoningDefault: "on", // aracı başına reasoning görünürlüğü geçersiz kılması
        fastModeDefault: false, // aracı başına fast mode geçersiz kılması
        params: { cacheRetention: "none" }, // eşleşen defaults.models params değerlerini anahtar bazında geçersiz kılar
        skills: ["docs-search"], // ayarlanırsa agents.defaults.skills yerine geçer
        identity: {
          name: "Samantha",
          theme: "helpful sloth",
          emoji: "🦥",
          avatar: "avatars/samantha.png",
        },
        groupChat: { mentionPatterns: ["@openclaw"] },
        sandbox: { mode: "off" },
        runtime: {
          type: "acp",
          acp: {
            agent: "codex",
            backend: "acpx",
            mode: "persistent",
            cwd: "/workspace/openclaw",
          },
        },
        subagents: { allowAgents: ["*"] },
        tools: {
          profile: "coding",
          allow: ["browser"],
          deny: ["canvas"],
          elevated: { enabled: true },
        },
      },
    ],
  },
}
```

- `id`: kararlı aracı kimliği (gerekli).
- `default`: birden fazla ayarlıysa ilki kazanır (uyarı günlüğe kaydedilir). Hiçbiri ayarlı değilse listedeki ilk girdi varsayılandır.
- `model`: dize biçimi yalnızca `primary` değerini geçersiz kılar; nesne biçimi `{ primary, fallbacks }` ikisini de geçersiz kılar (`[]` genel fallback'leri devre dışı bırakır). Yalnızca `primary` geçersiz kılan cron işleri, `fallbacks: []` ayarlamadıkça varsayılan fallback'leri devralmaya devam eder.
- `params`: `agents.defaults.models` içindeki seçili model girdisinin üzerine birleştirilen aracı başına akış parametreleri. `cacheRetention`, `temperature` veya `maxTokens` gibi aracıya özgü geçersiz kılmalar için tüm model kataloğunu çoğaltmak yerine bunu kullanın.
- `skills`: isteğe bağlı aracı başına Skill allowlist'i. Atlanırsa aracı, ayarlıysa `agents.defaults.skills` değerini devralır; açık bir liste varsayılanların yerine geçer ve birleşmez, `[]` ise Skill yok demektir.
- `thinkingDefault`: isteğe bağlı aracı başına varsayılan thinking düzeyi (`off | minimal | low | medium | high | xhigh | adaptive`). Mesaj başına veya oturum geçersiz kılması ayarlı değilse bu aracı için `agents.defaults.thinkingDefault` değerini geçersiz kılar.
- `reasoningDefault`: isteğe bağlı aracı başına varsayılan reasoning görünürlüğü (`on | off | stream`). Mesaj başına veya oturum reasoning geçersiz kılması ayarlı değilse uygulanır.
- `fastModeDefault`: isteğe bağlı aracı başına varsayılan fast mode değeri (`true | false`). Mesaj başına veya oturum fast-mode geçersiz kılması ayarlı değilse uygulanır.
- `runtime`: isteğe bağlı aracı başına çalışma zamanı tanımlayıcısı. Aracının varsayılan olarak ACP harness oturumları kullanması gerekiyorsa `type: "acp"` ile `runtime.acp` varsayılanlarını (`agent`, `backend`, `mode`, `cwd`) kullanın.
- `identity.avatar`: çalışma alanına göreli yol, `http(s)` URL'si veya `data:` URI'si.
- `identity`, varsayılanları türetir: `ackReaction` için `emoji`, `mentionPatterns` için `name`/`emoji`.
- `subagents.allowAgents`: `sessions_spawn` için aracı kimlikleri allowlist'i (`["*"]` = herhangi biri; varsayılan: yalnızca aynı aracı).
- Sandbox devralma koruması: istekte bulunan oturum sandbox içindeyse `sessions_spawn`, sandboxsız çalışacak hedefleri reddeder.
- `subagents.requireAgentId`: true olduğunda `agentId` içermeyen `sessions_spawn` çağrılarını engeller (açık profil seçimini zorlar; varsayılan: false).

---

## Çok aracı yönlendirme

Tek bir Gateway içinde birden fazla yalıtılmış aracı çalıştırın. Bkz. [Multi-Agent](/tr/concepts/multi-agent).

```json5
{
  agents: {
    list: [
      { id: "home", default: true, workspace: "~/.openclaw/workspace-home" },
      { id: "work", workspace: "~/.openclaw/workspace-work" },
    ],
  },
  bindings: [
    { agentId: "home", match: { channel: "whatsapp", accountId: "personal" } },
    { agentId: "work", match: { channel: "whatsapp", accountId: "biz" } },
  ],
}
```

### Bağlama eşleşme alanları

- `type` (isteğe bağlı): normal yönlendirme için `route` (type eksikse varsayılan route), kalıcı ACP konuşma bağlamaları için `acp`.
- `match.channel` (gerekli)
- `match.accountId` (isteğe bağlı; `*` = herhangi bir hesap; atlanırsa varsayılan hesap)
- `match.peer` (isteğe bağlı; `{ kind: direct|group|channel, id }`)
- `match.guildId` / `match.teamId` (isteğe bağlı; kanala özgü)
- `acp` (isteğe bağlı; yalnızca `type: "acp"` için): `{ mode, label, cwd, backend }`

**Deterministik eşleşme sırası:**

1. `match.peer`
2. `match.guildId`
3. `match.teamId`
4. `match.accountId` (tam eşleşme, peer/guild/team yok)
5. `match.accountId: "*"` (kanal geneli)
6. Varsayılan aracı

Her kademede ilk eşleşen `bindings` girdisi kazanır.

`type: "acp"` girdileri için OpenClaw, tam konuşma kimliğiyle (`match.channel` + hesap + `match.peer.id`) çözümler ve yukarıdaki route bağlama kademe sırasını kullanmaz.

### Aracı başına erişim profilleri

<Accordion title="Tam erişim (sandbox yok)">

```json5
{
  agents: {
    list: [
      {
        id: "personal",
        workspace: "~/.openclaw/workspace-personal",
        sandbox: { mode: "off" },
      },
    ],
  },
}
```

</Accordion>

<Accordion title="Salt okunur araçlar + çalışma alanı">

```json5
{
  agents: {
    list: [
      {
        id: "family",
        workspace: "~/.openclaw/workspace-family",
        sandbox: { mode: "all", scope: "agent", workspaceAccess: "ro" },
        tools: {
          allow: [
            "read",
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
          ],
          deny: ["write", "edit", "apply_patch", "exec", "process", "browser"],
        },
      },
    ],
  },
}
```

</Accordion>

<Accordion title="Dosya sistemi erişimi yok (yalnızca mesajlaşma)">

```json5
{
  agents: {
    list: [
      {
        id: "public",
        workspace: "~/.openclaw/workspace-public",
        sandbox: { mode: "all", scope: "agent", workspaceAccess: "none" },
        tools: {
          allow: [
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "whatsapp",
            "telegram",
            "slack",
            "discord",
            "gateway",
          ],
          deny: [
            "read",
            "write",
            "edit",
            "apply_patch",
            "exec",
            "process",
            "browser",
            "canvas",
            "nodes",
            "cron",
            "gateway",
            "image",
          ],
        },
      },
    ],
  },
}
```

</Accordion>

Öncelik ayrıntıları için bkz. [Multi-Agent Sandbox & Tools](/tr/tools/multi-agent-sandbox-tools).

---

## Oturum

```json5
{
  session: {
    scope: "per-sender",
    dmScope: "main", // main | per-peer | per-channel-peer | per-account-channel-peer
    identityLinks: {
      alice: ["telegram:123456789", "discord:987654321012345678"],
    },
    reset: {
      mode: "daily", // daily | idle
      atHour: 4,
      idleMinutes: 60,
    },
    resetByType: {
      thread: { mode: "daily", atHour: 4 },
      direct: { mode: "idle", idleMinutes: 240 },
      group: { mode: "idle", idleMinutes: 120 },
    },
    resetTriggers: ["/new", "/reset"],
    store: "~/.openclaw/agents/{agentId}/sessions/sessions.json",
    parentForkMaxTokens: 100000, // bu token sayısının üstünde üst ileti dizisi çatallaması atlanır (0 devre dışı bırakır)
    maintenance: {
      mode: "warn", // warn | enforce
      pruneAfter: "30d",
      maxEntries: 500,
      rotateBytes: "10mb",
      resetArchiveRetention: "30d", // süre veya false
      maxDiskBytes: "500mb", // isteğe bağlı katı bütçe
      highWaterBytes: "400mb", // isteğe bağlı temizleme hedefi
    },
    threadBindings: {
      enabled: true,
      idleHours: 24, // saat cinsinden varsayılan hareketsizlik oto-odak kaldırma (`0` devre dışı bırakır)
      maxAgeHours: 0, // saat cinsinden varsayılan katı azami yaş (`0` devre dışı bırakır)
    },
    mainKey: "main", // eski (çalışma zamanı her zaman "main" kullanır)
    agentToAgent: { maxPingPongTurns: 5 },
    sendPolicy: {
      rules: [{ action: "deny", match: { channel: "discord", chatType: "group" } }],
      default: "allow",
    },
  },
}
```

<Accordion title="Oturum alanı ayrıntıları">

- **`scope`**: grup sohbeti bağlamları için temel oturum gruplama stratejisi.
  - `per-sender` (varsayılan): her gönderen, kanal bağlamında yalıtılmış bir oturum alır.
  - `global`: kanal bağlamındaki tüm katılımcılar tek bir oturumu paylaşır (yalnızca paylaşılan bağlam istendiğinde kullanın).
- **`dmScope`**: DM'lerin nasıl gruplanacağı.
  - `main`: tüm DM'ler ana oturumu paylaşır.
  - `per-peer`: kanallar arasında gönderen kimliğine göre yalıtır.
  - `per-channel-peer`: kanal + gönderen başına yalıtır (çok kullanıcılı gelen kutuları için önerilir).
  - `per-account-channel-peer`: hesap + kanal + gönderen başına yalıtır (çok hesaplı kullanım için önerilir).
- **`identityLinks`**: kanallar arası oturum paylaşımı için kanonik kimlikleri sağlayıcı önekli eşlere eşler.
- **`reset`**: birincil sıfırlama ilkesi. `daily`, yerel saatte `atHour` zamanında sıfırlar; `idle`, `idleMinutes` sonrasında sıfırlar. İkisi de yapılandırılmışsa önce süresi dolan kazanır.
- **`resetByType`**: tür başına geçersiz kılmalar (`direct`, `group`, `thread`). Eski `dm`, `direct` için takma ad olarak kabul edilir.
- **`parentForkMaxTokens`**: çatallanmış ileti dizisi oturumu oluştururken izin verilen azami üst oturum `totalTokens` değeri (varsayılan `100000`).
  - Üst `totalTokens` bu değerin üzerindeyse OpenClaw, üst transkript geçmişini devralmak yerine yeni bir ileti dizisi oturumu başlatır.
  - Bu korumayı devre dışı bırakmak ve üst çatallanmasına her zaman izin vermek için `0` ayarlayın.
- **`mainKey`**: eski alan. Çalışma zamanı artık ana doğrudan sohbet kovası için her zaman `"main"` kullanır.
- **`agentToAgent.maxPingPongTurns`**: aracıdan aracıya değişimlerde aracılar arasındaki azami geri-yanıt turu sayısı (tam sayı, aralık: `0`–`5`). `0`, ping-pong zincirini devre dışı bırakır.
- **`sendPolicy`**: `channel`, `chatType` (`direct|group|channel`, eski `dm` takma adıyla), `keyPrefix` veya `rawKeyPrefix` ile eşleşir. İlk deny kazanır.
- **`maintenance`**: oturum deposu temizleme + saklama denetimleri.
  - `mode`: `warn` yalnızca uyarı üretir; `enforce` temizleme uygular.
  - `pruneAfter`: eski girişler için yaş kesimi (varsayılan `30d`).
  - `maxEntries`: `sessions.json` içindeki azami giriş sayısı (varsayılan `500`).
  - `rotateBytes`: `sessions.json` bu boyutu aşınca döndür (varsayılan `10mb`).
  - `resetArchiveRetention`: `*.reset.<timestamp>` transkript arşivleri için saklama süresi. Varsayılan olarak `pruneAfter`; devre dışı bırakmak için `false` ayarlayın.
  - `maxDiskBytes`: oturumlar dizini için isteğe bağlı disk bütçesi. `warn` modunda uyarı günlüğü yazar; `enforce` modunda en eski artifaktları/oturumları önce kaldırır.
  - `highWaterBytes`: bütçe temizliğinden sonraki isteğe bağlı hedef. Varsayılan olarak `maxDiskBytes` değerinin `%80`idir.
- **`threadBindings`**: ileti dizisine bağlı oturum özellikleri için genel varsayılanlar.
  - `enabled`: ana varsayılan anahtar (sağlayıcılar geçersiz kılabilir; Discord `channels.discord.threadBindings.enabled` kullanır)
  - `idleHours`: saat cinsinden varsayılan hareketsizlik oto-odak kaldırma (`0` devre dışı bırakır; sağlayıcılar geçersiz kılabilir)
  - `maxAgeHours`: saat cinsinden varsayılan katı azami yaş (`0` devre dışı bırakır; sağlayıcılar geçersiz kılabilir)

</Accordion>

---

## Mesajlar

```json5
{
  messages: {
    responsePrefix: "🦞", // veya "auto"
    ackReaction: "👀",
    ackReactionScope: "group-mentions", // group-mentions | group-all | direct | all
    removeAckAfterReply: false,
    queue: {
      mode: "collect", // steer | followup | collect | steer-backlog | steer+backlog | queue | interrupt
      debounceMs: 1000,
      cap: 20,
      drop: "summarize", // old | new | summarize
      byChannel: {
        whatsapp: "collect",
        telegram: "collect",
      },
    },
    inbound: {
      debounceMs: 2000, // 0 devre dışı bırakır
      byChannel: {
        whatsapp: 5000,
        slack: 1500,
      },
    },
  },
}
```

### Yanıt öneki

Kanal/hesap başına geçersiz kılmalar: `channels.<channel>.responsePrefix`, `channels.<channel>.accounts.<id>.responsePrefix`.

Çözümleme (en özeli kazanır): hesap → kanal → genel. `""` devre dışı bırakır ve zinciri durdurur. `"auto"`, `[{identity.name}]` türetir.

**Şablon değişkenleri:**

| Değişken         | Açıklama                | Örnek                       |
| ---------------- | ----------------------- | --------------------------- |
| `{model}`        | Kısa model adı          | `claude-opus-4-6`           |
| `{modelFull}`    | Tam model tanımlayıcısı | `anthropic/claude-opus-4-6` |
| `{provider}`     | Sağlayıcı adı           | `anthropic`                 |
| `{thinkingLevel}` | Geçerli thinking düzeyi | `high`, `low`, `off`        |
| `{identity.name}` | Aracı kimlik adı        | (`"auto"` ile aynı)         |

Değişkenler büyük/küçük harfe duyarsızdır. `{think}`, `{thinkingLevel}` için takma addır.

### Ack tepkisi

- Varsayılan olarak etkin aracının `identity.emoji` değeri, aksi halde `"👀"`. Devre dışı bırakmak için `""` ayarlayın.
- Kanal başına geçersiz kılmalar: `channels.<channel>.ackReaction`, `channels.<channel>.accounts.<id>.ackReaction`.
- Çözümleme sırası: hesap → kanal → `messages.ackReaction` → identity geri dönüşü.
- Kapsam: `group-mentions` (varsayılan), `group-all`, `direct`, `all`.
- `removeAckAfterReply`, Slack, Discord ve Telegram'da yanıt sonrası ack'i kaldırır.
- `messages.statusReactions.enabled`, Slack, Discord ve Telegram'da yaşam döngüsü durum tepkilerini etkinleştirir.
  Slack ve Discord'da ayarlanmamışsa, ack tepkileri etkin olduğunda durum tepkileri etkin kalır.
  Telegram'da yaşam döngüsü durum tepkilerini etkinleştirmek için açıkça `true` ayarlayın.

### Gelen debounce

Aynı gönderenden gelen hızlı, yalnızca metin içeren mesajları tek bir aracı turunda toplar. Medya/ek dosyalar hemen flush edilir. Kontrol komutları debounce'u atlar.

### TTS (text-to-speech)

```json5
{
  messages: {
    tts: {
      auto: "always", // off | always | inbound | tagged
      mode: "final", // final | all
      provider: "elevenlabs",
      summaryModel: "openai/gpt-4.1-mini",
      modelOverrides: { enabled: true },
      maxTextLength: 4000,
      timeoutMs: 30000,
      prefsPath: "~/.openclaw/settings/tts.json",
      elevenlabs: {
        apiKey: "elevenlabs_api_key",
        baseUrl: "https://api.elevenlabs.io",
        voiceId: "voice_id",
        modelId: "eleven_multilingual_v2",
        seed: 42,
        applyTextNormalization: "auto",
        languageCode: "en",
        voiceSettings: {
          stability: 0.5,
          similarityBoost: 0.75,
          style: 0.0,
          useSpeakerBoost: true,
          speed: 1.0,
        },
      },
      openai: {
        apiKey: "openai_api_key",
        baseUrl: "https://api.openai.com/v1",
        model: "gpt-4o-mini-tts",
        voice: "alloy",
      },
    },
  },
}
```

- `auto`, otomatik TTS'yi denetler. `/tts off|always|inbound|tagged` bunu oturum başına geçersiz kılar.
- `summaryModel`, otomatik özet için `agents.defaults.model.primary` değerini geçersiz kılar.
- `modelOverrides` varsayılan olarak etkindir; `modelOverrides.allowProvider` varsayılan olarak `false`'dur (katılım gerekir).
- API anahtarları `ELEVENLABS_API_KEY`/`XI_API_KEY` ve `OPENAI_API_KEY` değerlerine geri döner.
- `openai.baseUrl`, OpenAI TTS uç noktasını geçersiz kılar. Çözümleme sırası yapılandırma, ardından `OPENAI_TTS_BASE_URL`, ardından `https://api.openai.com/v1` şeklindedir.
- `openai.baseUrl` OpenAI dışı bir uç noktaya işaret ettiğinde OpenClaw bunu OpenAI uyumlu bir TTS sunucusu olarak ele alır ve model/ses doğrulamasını gevşetir.

---

## Talk

Talk modu için varsayılanlar (macOS/iOS/Android).

```json5
{
  talk: {
    provider: "elevenlabs",
    providers: {
      elevenlabs: {
        voiceId: "elevenlabs_voice_id",
        voiceAliases: {
          Clawd: "EXAVITQu4vr4xnSDxMaL",
          Roger: "CwhRBWXzGAHq8TQ4Fs17",
        },
        modelId: "eleven_v3",
        outputFormat: "mp3_44100_128",
        apiKey: "elevenlabs_api_key",
      },
    },
    silenceTimeoutMs: 1500,
    interruptOnSpeech: true,
  },
}
```

- `talk.provider`, birden fazla Talk sağlayıcısı yapılandırıldığında `talk.providers` içindeki bir anahtarla eşleşmelidir.
- Eski düz Talk anahtarları (`talk.voiceId`, `talk.voiceAliases`, `talk.modelId`, `talk.outputFormat`, `talk.apiKey`) yalnızca uyumluluk içindir ve otomatik olarak `talk.providers.<provider>` içine taşınır.
- Ses kimlikleri `ELEVENLABS_VOICE_ID` veya `SAG_VOICE_ID` değerlerine geri döner.
- `providers.*.apiKey`, düz metin dizeleri veya SecretRef nesneleri kabul eder.
- `ELEVENLABS_API_KEY` geri dönüşü yalnızca Talk API anahtarı yapılandırılmadığında uygulanır.
- `providers.*.voiceAliases`, Talk yönergelerinin kolay adlar kullanmasına izin verir.
- `silenceTimeoutMs`, Talk modunun kullanıcı sessizliğinden sonra transkripti göndermeden önce ne kadar bekleyeceğini denetler. Ayarlanmamışsa platform varsayılan duraklama penceresi korunur (`macOS ve Android'de 700 ms, iOS'ta 900 ms`).

---

## Araçlar

### Araç profilleri

`tools.profile`, `tools.allow`/`tools.deny` öncesinde temel bir allowlist ayarlar:

Yerel onboarding, ayarlanmamış yeni yerel yapılandırmaları varsayılan olarak `tools.profile: "coding"` ile başlatır (mevcut açık profiller korunur).

| Profil      | İçerir                                                                                                                        |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `minimal`   | yalnızca `session_status`                                                                                                     |
| `coding`    | `group:fs`, `group:runtime`, `group:web`, `group:sessions`, `group:memory`, `cron`, `image`, `image_generate`, `video_generate` |
| `messaging` | `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status`                                    |
| `full`      | Kısıtlama yok (ayarlanmamış ile aynı)                                                                                         |

### Araç grupları

| Grup               | Araçlar                                                                                                                |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| `group:runtime`    | `exec`, `process`, `code_execution` (`bash`, `exec` için takma ad olarak kabul edilir)                               |
| `group:fs`         | `read`, `write`, `edit`, `apply_patch`                                                                                |
| `group:sessions`   | `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `sessions_yield`, `subagents`, `session_status` |
| `group:memory`     | `memory_search`, `memory_get`                                                                                         |
| `group:web`        | `web_search`, `x_search`, `web_fetch`                                                                                 |
| `group:ui`         | `browser`, `canvas`                                                                                                   |
| `group:automation` | `cron`, `gateway`                                                                                                     |
| `group:messaging`  | `message`                                                                                                             |
| `group:nodes`      | `nodes`                                                                                                               |
| `group:agents`     | `agents_list`                                                                                                         |
| `group:media`      | `image`, `image_generate`, `video_generate`, `tts`                                                                    |
| `group:openclaw`   | Tüm yerleşik araçlar (sağlayıcı eklentileri hariç)                                                                    |

### `tools.allow` / `tools.deny`

Genel araç izin/ret ilkesi (deny kazanır). Büyük/küçük harfe duyarsızdır, `*` joker karakterlerini destekler. Docker sandbox kapalı olduğunda da uygulanır.

```json5
{
  tools: { deny: ["browser", "canvas"] },
}
```

### `tools.byProvider`

Belirli sağlayıcılar veya modeller için araçları daha da kısıtlar. Sıra: temel profil → sağlayıcı profili → allow/deny.

```json5
{
  tools: {
    profile: "coding",
    byProvider: {
      "google-antigravity": { profile: "minimal" },
      "openai/gpt-5.4": { allow: ["group:fs", "sessions_list"] },
    },
  },
}
```

### `tools.elevated`

Sandbox dışındaki elevated exec erişimini denetler:

```json5
{
  tools: {
    elevated: {
      enabled: true,
      allowFrom: {
        whatsapp: ["+15555550123"],
        discord: ["1234567890123", "987654321098765432"],
      },
    },
  },
}
```

- Aracı başına geçersiz kılma (`agents.list[].tools.elevated`) yalnızca daha da kısıtlayabilir.
- `/elevated on|off|ask|full` durumu oturum başına saklar; satır içi yönergeler tek mesaja uygulanır.
- Elevated `exec`, sandboxing'i atlar ve yapılandırılmış escape yolunu kullanır (`gateway` varsayılan, `exec` hedefi `node` olduğunda `node`).

### `tools.exec`

```json5
{
  tools: {
    exec: {
      backgroundMs: 10000,
      timeoutSec: 1800,
      cleanupMs: 1800000,
      notifyOnExit: true,
      notifyOnExitEmptySuccess: false,
      applyPatch: {
        enabled: false,
        allowModels: ["gpt-5.4"],
      },
    },
  },
}
```

### `tools.loopDetection`

Araç döngüsü güvenlik denetimleri varsayılan olarak **devre dışıdır**. Algılamayı etkinleştirmek için `enabled: true` ayarlayın.
Ayarlar genel olarak `tools.loopDetection` altında tanımlanabilir ve aracı başına `agents.list[].tools.loopDetection` ile geçersiz kılınabilir.

```json5
{
  tools: {
    loopDetection: {
      enabled: true,
      historySize: 30,
      warningThreshold: 10,
      criticalThreshold: 20,
      globalCircuitBreakerThreshold: 30,
      detectors: {
        genericRepeat: true,
        knownPollNoProgress: true,
        pingPong: true,
      },
    },
  },
}
```

- `historySize`: döngü analizi için tutulan azami araç çağrısı geçmişi.
- `warningThreshold`: uyarılar için tekrar eden ilerleme yok deseni eşiği.
- `criticalThreshold`: kritik döngüleri engellemek için daha yüksek tekrar eşiği.
- `globalCircuitBreakerThreshold`: herhangi bir ilerleme olmayan çalıştırma için katı durdurma eşiği.
- `detectors.genericRepeat`: aynı araç/aynı argüman çağrılarındaki tekrarlarda uyar.
- `detectors.knownPollNoProgress`: bilinen poll araçlarında (`process.poll`, `command_status` vb.) uyar/engelle.
- `detectors.pingPong`: dönüşümlü ilerleme olmayan çift desenlerinde uyar/engelle.
- `warningThreshold >= criticalThreshold` veya `criticalThreshold >= globalCircuitBreakerThreshold` ise doğrulama başarısız olur.

### `tools.web`

```json5
{
  tools: {
    web: {
      search: {
        enabled: true,
        apiKey: "brave_api_key", // veya BRAVE_API_KEY env
        maxResults: 5,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
      },
      fetch: {
        enabled: true,
        provider: "firecrawl", // isteğe bağlı; otomatik algılama için atlayın
        maxChars: 50000,
        maxCharsCap: 50000,
        maxResponseBytes: 2000000,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
        maxRedirects: 3,
        readability: true,
        userAgent: "custom-ua",
      },
    },
  },
}
```

### `tools.media`

Gelen medya anlama işlemini yapılandırır (görüntü/ses/video):

```json5
{
  tools: {
    media: {
      concurrency: 2,
      asyncCompletion: {
        directSend: false, // katılım gerekir: tamamlanmış async müzik/videoyu doğrudan kanala gönder
      },
      audio: {
        enabled: true,
        maxBytes: 20971520,
        scope: {
          default: "deny",
          rules: [{ action: "allow", match: { chatType: "direct" } }],
        },
        models: [
          { provider: "openai", model: "gpt-4o-mini-transcribe" },
          { type: "cli", command: "whisper", args: ["--model", "base", "{{MediaPath}}"] },
        ],
      },
      video: {
        enabled: true,
        maxBytes: 52428800,
        models: [{ provider: "google", model: "gemini-3-flash-preview" }],
      },
    },
  },
}
```

<Accordion title="Medya model girdisi alanları">

**Sağlayıcı girdisi** (`type: "provider"` veya atlanmış):

- `provider`: API sağlayıcı kimliği (`openai`, `anthropic`, `google`/`gemini`, `groq` vb.)
- `model`: model kimliği geçersiz kılması
- `profile` / `preferredProfile`: `auth-profiles.json` profil seçimi

**CLI girdisi** (`type: "cli"`):

- `command`: çalıştırılacak yürütülebilir dosya
- `args`: şablonlu argümanlar (`{{MediaPath}}`, `{{Prompt}}`, `{{MaxChars}}` vb. desteklenir)

**Ortak alanlar:**

- `capabilities`: isteğe bağlı liste (`image`, `audio`, `video`). Varsayılanlar: `openai`/`anthropic`/`minimax` → image, `google` → image+audio+video, `groq` → audio.
- `prompt`, `maxChars`, `maxBytes`, `timeoutSeconds`, `language`: girdi başına geçersiz kılmalar.
- Hatalarda bir sonraki girdiye geri dönülür.

Sağlayıcı auth standart sırayı izler: `auth-profiles.json` → env vars → `models.providers.*.apiKey`.

**Async completion alanları:**

- `asyncCompletion.directSend`: `true` olduğunda tamamlanan async `music_generate`
  ve `video_generate` görevleri önce doğrudan kanal teslimini dener. Varsayılan: `false`
  (eski requester-session wake/model-delivery yolu).

</Accordion>

### `tools.agentToAgent`

```json5
{
  tools: {
    agentToAgent: {
      enabled: false,
      allow: ["home", "work"],
    },
  },
}
```

### `tools.sessions`

Oturum araçlarının (`sessions_list`, `sessions_history`, `sessions_send`) hangi oturumları hedefleyebileceğini denetler.

Varsayılan: `tree` (geçerli oturum + onun başlattığı oturumlar, örneğin alt aracılar).

```json5
{
  tools: {
    sessions: {
      // "self" | "tree" | "agent" | "all"
      visibility: "tree",
    },
  },
}
```

Notlar:

- `self`: yalnızca geçerli oturum anahtarı.
- `tree`: geçerli oturum + geçerli oturumun başlattığı oturumlar (alt aracılar).
- `agent`: geçerli aracı kimliğine ait herhangi bir oturum (aynı aracı kimliği altında gönderen başına oturum çalıştırıyorsanız başka kullanıcıları içerebilir).
- `all`: herhangi bir oturum. Aracılar arası hedefleme yine de `tools.agentToAgent` gerektirir.
- Sandbox kıskacı: geçerli oturum sandbox içindeyse ve `agents.defaults.sandbox.sessionToolsVisibility="spawned"` ise `tools.sessions.visibility="all"` olsa bile görünürlük `tree` olarak zorlanır.

### `tools.sessions_spawn`

`sessions_spawn` için satır içi ek dosya desteğini denetler.

```json5
{
  tools: {
    sessions_spawn: {
      attachments: {
        enabled: false, // katılım gerekir: satır içi dosya eklerine izin ver
        maxTotalBytes: 5242880, // tüm dosyalar toplamı 5 MB
        maxFiles: 50,
        maxFileBytes: 1048576, // dosya başına 1 MB
        retainOnSessionKeep: false, // cleanup="keep" olduğunda ekleri tut
      },
    },
  },
}
```

Notlar:

- Ek dosyalar yalnızca `runtime: "subagent"` için desteklenir. ACP çalışma zamanı bunları reddeder.
- Dosyalar çocuk çalışma alanında `.openclaw/attachments/<uuid>/` içine `.manifest.json` ile dönüştürülür.
- Ek içeriği, transkript kalıcılığından otomatik olarak redakte edilir.
- Base64 girdileri, katı alfabe/dolgu denetimleri ve decode öncesi boyut korumasıyla doğrulanır.
- Dosya izinleri dizinler için `0700`, dosyalar için `0600` olur.
- Temizleme `cleanup` ilkesini izler: `delete` ekleri her zaman kaldırır; `keep`, yalnızca `retainOnSessionKeep: true` olduğunda korur.

### `tools.experimental`

Deneysel yerleşik araç bayrakları. Çalışma zamanına özgü bir otomatik etkinleştirme kuralı uygulanmadığı sürece varsayılan olarak kapalıdır.

```json5
{
  tools: {
    experimental: {
      planTool: true, // deneysel update_plan etkinleştir
    },
  },
}
```

Notlar:

- `planTool`: trivial olmayan çok adımlı iş takibi için yapılandırılmış `update_plan` aracını etkinleştirir.
- Varsayılan: OpenAI dışı sağlayıcılar için `false`. OpenAI ve OpenAI Codex çalıştırmaları bunu otomatik etkinleştirir.
- Etkin olduğunda sistem istemi ayrıca kullanım rehberliği ekler; böylece model bunu yalnızca önemli işlerde kullanır ve en fazla bir adımı `in_progress` tutar.

### `agents.defaults.subagents`

```json5
{
  agents: {
    defaults: {
      subagents: {
        allowAgents: ["research"],
        model: "minimax/MiniMax-M2.7",
        maxConcurrent: 8,
        runTimeoutSeconds: 900,
        archiveAfterMinutes: 60,
      },
    },
  },
}
```

- `model`: başlatılan alt aracılar için varsayılan model. Atlanırsa alt aracılar çağıranın modelini devralır.
- `allowAgents`: istek yapan aracı kendi `subagents.allowAgents` değerini ayarlamadığında `sessions_spawn` için varsayılan hedef aracı kimlikleri allowlist'i (`["*"]` = herhangi biri; varsayılan: yalnızca aynı aracı).
- `runTimeoutSeconds`: araç çağrısı `runTimeoutSeconds` içermediğinde `sessions_spawn` için varsayılan zaman aşımı (saniye). `0` zaman aşımı yok demektir.
- Alt aracı başına araç ilkesi: `tools.subagents.tools.allow` / `tools.subagents.tools.deny`.

---

## Özel sağlayıcılar ve base URL'ler

OpenClaw yerleşik model kataloğunu kullanır. `models.providers` veya `~/.openclaw/agents/<agentId>/agent/models.json` üzerinden özel sağlayıcılar ekleyin.

```json5
{
  models: {
    mode: "merge", // merge (varsayılan) | replace
    providers: {
      "custom-proxy": {
        baseUrl: "http://localhost:4000/v1",
        apiKey: "LITELLM_KEY",
        api: "openai-completions", // openai-completions | openai-responses | anthropic-messages | google-generative-ai
        models: [
          {
            id: "llama-3.1-8b",
            name: "Llama 3.1 8B",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 128000,
            contextTokens: 96000,
            maxTokens: 32000,
          },
        ],
      },
    },
  },
}
```

- Özel auth ihtiyaçları için `authHeader: true` + `headers` kullanın.
- Aracı yapılandırma kökünü `OPENCLAW_AGENT_DIR` ile geçersiz kılın (veya eski ortam değişkeni takma adı `PI_CODING_AGENT_DIR`).
- Eşleşen sağlayıcı kimlikleri için birleştirme önceliği:
  - Boş olmayan aracı `models.json` `baseUrl` değerleri kazanır.
  - Boş olmayan aracı `apiKey` değerleri, yalnızca sağlayıcı mevcut yapılandırma/auth-profile bağlamında SecretRef tarafından yönetilmiyorsa kazanır.
  - SecretRef tarafından yönetilen sağlayıcı `apiKey` değerleri, çözümlenmiş sırları kalıcılaştırmak yerine kaynak işaretlerinden (`ENV_VAR_NAME` env ref'leri için, `secretref-managed` file/exec ref'leri için) yenilenir.
  - SecretRef tarafından yönetilen sağlayıcı başlık değerleri, kaynak işaretlerinden (`secretref-env:ENV_VAR_NAME` env ref'leri için, `secretref-managed` file/exec ref'leri için) yenilenir.
  - Boş veya eksik aracı `apiKey`/`baseUrl`, yapılandırmadaki `models.providers` değerlerine geri döner.
  - Eşleşen model `contextWindow`/`maxTokens` değerleri, açık yapılandırma ve örtük katalog değerleri arasındaki daha yüksek değeri kullanır.
  - Eşleşen model `contextTokens`, açık çalışma zamanı sınırı varsa onu korur; yerel model meta verisini değiştirmeden etkin bağlam bütçesini sınırlamak için kullanın.
  - Yapılandırmanın `models.json` dosyasını tamamen yeniden yazmasını istiyorsanız `models.mode: "replace"` kullanın.
  - İşaretçi kalıcılığı kaynak açısından yetkilidir: işaretçiler, çözümlenen çalışma zamanı gizli değerlerinden değil etkin kaynak yapılandırma anlık görüntüsünden (çözümleme öncesi) yazılır.

### Sağlayıcı alanı ayrıntıları

- `models.mode`: sağlayıcı katalog davranışı (`merge` veya `replace`).
- `models.providers`: sağlayıcı kimliğine göre anahtarlanmış özel sağlayıcı haritası.
- `models.providers.*.api`: istek bağdaştırıcısı (`openai-completions`, `openai-responses`, `anthropic-messages`, `google-generative-ai` vb.).
- `models.providers.*.apiKey`: sağlayıcı kimlik bilgisi (tercihen SecretRef/env substitution).
- `models.providers.*.auth`: auth stratejisi (`api-key`, `token`, `oauth`, `aws-sdk`).
- `models.providers.*.injectNumCtxForOpenAICompat`: Ollama + `openai-completions` için isteklere `options.num_ctx` ekle (varsayılan: `true`).
- `models.providers.*.authHeader`: gerektiğinde kimlik bilgisini `Authorization` üstbilgisinde taşımayı zorla.
- `models.providers.*.baseUrl`: yukarı akış API base URL.
- `models.providers.*.headers`: proxy/tenant yönlendirmesi için ek statik üstbilgiler.
- `models.providers.*.request`: model-sağlayıcı HTTP istekleri için taşıma geçersiz kılmaları.
  - `request.headers`: ek üstbilgiler (sağlayıcı varsayılanlarıyla birleşir). Değerler SecretRef kabul eder.
  - `request.auth`: auth stratejisi geçersiz kılması. Modlar: `"provider-default"` (sağlayıcının yerleşik auth'unu kullan), `"authorization-bearer"` (`token` ile), `"header"` (`headerName`, `value`, isteğe bağlı `prefix` ile).
  - `request.proxy`: HTTP proxy geçersiz kılması. Modlar: `"env-proxy"` (`HTTP_PROXY`/`HTTPS_PROXY` env vars kullan), `"explicit-proxy"` (`url` ile). Her iki mod da isteğe bağlı `tls` alt nesnesini kabul eder.
  - `request.tls`: doğrudan bağlantılar için TLS geçersiz kılması. Alanlar: `ca`, `cert`, `key`, `passphrase` (hepsi SecretRef kabul eder), `serverName`, `insecureSkipVerify`.
- `models.providers.*.models`: açık sağlayıcı model kataloğu girdileri.
- `models.providers.*.models.*.contextWindow`: yerel model bağlam penceresi meta verisi.
- `models.providers.*.models.*.contextTokens`: isteğe bağlı çalışma zamanı bağlam sınırı. Modelin yerel `contextWindow` değerinden daha küçük bir etkin bağlam bütçesi istiyorsanız bunu kullanın.
- `models.providers.*.models.*.compat.supportsDeveloperRole`: isteğe bağlı uyumluluk ipucu. `api: "openai-completions"` için ve boş olmayan yerel olmayan bir `baseUrl` ile (`api.openai.com` dışındaki host), OpenClaw bunu çalışma zamanında `false` olarak zorlar. Boş/atlanmış `baseUrl`, varsayılan OpenAI davranışını korur.
- `plugins.entries.amazon-bedrock.config.discovery`: Bedrock otomatik keşif ayarlarının kökü.
- `plugins.entries.amazon-bedrock.config.discovery.enabled`: örtük keşfi aç/kapat.
- `plugins.entries.amazon-bedrock.config.discovery.region`: keşif için AWS bölgesi.
- `plugins.entries.amazon-bedrock.config.discovery.providerFilter`: hedefli keşif için isteğe bağlı sağlayıcı kimliği filtresi.
- `plugins.entries.amazon-bedrock.config.discovery.refreshInterval`: keşif yenileme anket aralığı.
- `plugins.entries.amazon-bedrock.config.discovery.defaultContextWindow`: keşfedilen modeller için geri dönüş bağlam penceresi.
- `plugins.entries.amazon-bedrock.config.discovery.defaultMaxTokens`: keşfedilen modeller için geri dönüş azami çıktı tokenı.

### Sağlayıcı örnekleri

<Accordion title="Cerebras (GLM 4.6 / 4.7)">

```json5
{
  env: { CEREBRAS_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: {
        primary: "cerebras/zai-glm-4.7",
        fallbacks: ["cerebras/zai-glm-4.6"],
      },
      models: {
        "cerebras/zai-glm-4.7": { alias: "GLM 4.7 (Cerebras)" },
        "cerebras/zai-glm-4.6": { alias: "GLM 4.6 (Cerebras)" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      cerebras: {
        baseUrl: "https://api.cerebras.ai/v1",
        apiKey: "${CEREBRAS_API_KEY}",
        api: "openai-completions",
        models: [
          { id: "zai-glm-4.7", name: "GLM 4.7 (Cerebras)" },
          { id: "zai-glm-4.6", name: "GLM 4.6 (Cerebras)" },
        ],
      },
    },
  },
}
```

Cerebras için `cerebras/zai-glm-4.7`; Z.AI direct için `zai/glm-4.7` kullanın.

</Accordion>

<Accordion title="OpenCode">

```json5
{
  agents: {
    defaults: {
      model: { primary: "opencode/claude-opus-4-6" },
      models: { "opencode/claude-opus-4-6": { alias: "Opus" } },
    },
  },
}
```

`OPENCODE_API_KEY` (veya `OPENCODE_ZEN_API_KEY`) ayarlayın. Zen kataloğu için `opencode/...`, Go kataloğu için `opencode-go/...` referanslarını kullanın. Kısayol: `openclaw onboard --auth-choice opencode-zen` veya `openclaw onboard --auth-choice opencode-go`.

</Accordion>

<Accordion title="Z.AI (GLM-4.7)">

```json5
{
  agents: {
    defaults: {
      model: { primary: "zai/glm-4.7" },
      models: { "zai/glm-4.7": {} },
    },
  },
}
```

`ZAI_API_KEY` ayarlayın. `z.ai/*` ve `z-ai/*` kabul edilen takma adlardır. Kısayol: `openclaw onboard --auth-choice zai-api-key`.

- Genel uç nokta: `https://api.z.ai/api/paas/v4`
- Kodlama uç noktası (varsayılan): `https://api.z.ai/api/coding/paas/v4`
- Genel uç nokta için base URL geçersiz kılmalı özel bir sağlayıcı tanımlayın.

</Accordion>

<Accordion title="Moonshot AI (Kimi)">

```json5
{
  env: { MOONSHOT_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "moonshot/kimi-k2.5" },
      models: { "moonshot/kimi-k2.5": { alias: "Kimi K2.5" } },
    },
  },
  models: {
    mode: "merge",
    providers: {
      moonshot: {
        baseUrl: "https://api.moonshot.ai/v1",
        apiKey: "${MOONSHOT_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "kimi-k2.5",
            name: "Kimi K2.5",
            reasoning: false,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 262144,
          },
        ],
      },
    },
  },
}
```

Çin uç noktası için: `baseUrl: "https://api.moonshot.cn/v1"` veya `openclaw onboard --auth-choice moonshot-api-key-cn`.

Yerel Moonshot uç noktaları, paylaşılan
`openai-completions` taşıması üzerinde akış kullanımı uyumluluğu sunar ve OpenClaw artık bunu yalnızca yerleşik sağlayıcı kimliğine değil
uç nokta yeteneklerine göre anahtarlar.

</Accordion>

<Accordion title="Kimi Coding">

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "kimi/kimi-code" },
      models: { "kimi/kimi-code": { alias: "Kimi Code" } },
    },
  },
}
```

Anthropic uyumlu, yerleşik sağlayıcı. Kısayol: `openclaw onboard --auth-choice kimi-code-api-key`.

</Accordion>

<Accordion title="Synthetic (Anthropic uyumlu)">

```json5
{
  env: { SYNTHETIC_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "synthetic/hf:MiniMaxAI/MiniMax-M2.5" },
      models: { "synthetic/hf:MiniMaxAI/MiniMax-M2.5": { alias: "MiniMax M2.5" } },
    },
  },
  models: {
    mode: "merge",
    providers: {
      synthetic: {
        baseUrl: "https://api.synthetic.new/anthropic",
        apiKey: "${SYNTHETIC_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "hf:MiniMaxAI/MiniMax-M2.5",
            name: "MiniMax M2.5",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 192000,
            maxTokens: 65536,
          },
        ],
      },
    },
  },
}
```

Base URL `/v1` içermemelidir (Anthropic istemcisi bunu ekler). Kısayol: `openclaw onboard --auth-choice synthetic-api-key`.

</Accordion>

<Accordion title="MiniMax M2.7 (direct)">

```json5
{
  agents: {
    defaults: {
      model: { primary: "minimax/MiniMax-M2.7" },
      models: {
        "minimax/MiniMax-M2.7": { alias: "Minimax" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      minimax: {
        baseUrl: "https://api.minimax.io/anthropic",
        apiKey: "${MINIMAX_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "MiniMax-M2.7",
            name: "MiniMax M2.7",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0.3, output: 1.2, cacheRead: 0.06, cacheWrite: 0.375 },
            contextWindow: 204800,
            maxTokens: 131072,
          },
        ],
      },
    },
  },
}
```

`MINIMAX_API_KEY` ayarlayın. Kısayollar:
`openclaw onboard --auth-choice minimax-global-api` veya
`openclaw onboard --auth-choice minimax-cn-api`.
Model kataloğu artık varsayılan olarak yalnızca M2.7 kullanır.
Anthropic uyumlu akış yolunda OpenClaw, siz açıkça `thinking` ayarlamadıkça
MiniMax thinking'i varsayılan olarak devre dışı bırakır. `/fast on` veya
`params.fastMode: true`, `MiniMax-M2.7` modelini
`MiniMax-M2.7-highspeed` olarak yeniden yazar.

</Accordion>

<Accordion title="Yerel modeller (LM Studio)">

Bkz. [Local Models](/tr/gateway/local-models). Kısaca: ciddi donanımda LM Studio Responses API ile büyük bir yerel model çalıştırın; fallback için host edilen modelleri birleştirilmiş halde tutun.

</Accordion>

---

## Skills

```json5
{
  skills: {
    allowBundled: ["gemini", "peekaboo"],
    load: {
      extraDirs: ["~/Projects/agent-scripts/skills"],
    },
    install: {
      preferBrew: true,
      nodeManager: "npm", // npm | pnpm | yarn | bun
    },
    entries: {
      "image-lab": {
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" }, // veya düz metin dize
        env: { GEMINI_API_KEY: "GEMINI_KEY_HERE" },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

- `allowBundled`: yalnızca paketlenmiş Skills için isteğe bağlı allowlist (yönetilen/çalışma alanı Skills bundan etkilenmez).
- `load.extraDirs`: ek paylaşılan Skill kökleri (en düşük öncelik).
- `install.preferBrew`: `brew` mevcut olduğunda diğer yükleyici türlerine geri dönmeden önce Homebrew yükleyicilerini tercih eder.
- `install.nodeManager`: `metadata.openclaw.install`
  özellikleri için node yükleyici tercihi (`npm` | `pnpm` | `yarn` | `bun`).
- `entries.<skillKey>.enabled: false`, bir Skill paketlenmiş/yüklenmiş olsa bile onu devre dışı bırakır.
- `entries.<skillKey>.apiKey`: birincil env değişkeni bildiren Skills için kolaylık alanı (düz metin dize veya SecretRef nesnesi).

---

## Eklentiler

```json5
{
  plugins: {
    enabled: true,
    allow: ["voice-call"],
    deny: [],
    load: {
      paths: ["~/Projects/oss/voice-call-extension"],
    },
    entries: {
      "voice-call": {
        enabled: true,
        hooks: {
          allowPromptInjection: false,
        },
        config: { provider: "twilio" },
      },
    },
  },
}
```

- `~/.openclaw/extensions`, `<workspace>/.openclaw/extensions` ve `plugins.load.paths` içinden yüklenir.
- Keşif, yerel OpenClaw eklentilerinin yanı sıra uyumlu Codex paketlerini ve Claude paketlerini, manifest'i olmayan Claude varsayılan düzen paketleri dahil, kabul eder.
- **Yapılandırma değişiklikleri ağ geçidi yeniden başlatması gerektirir.**
- `allow`: isteğe bağlı allowlist (yalnızca listelenen eklentiler yüklenir). `deny` kazanır.
- `plugins.entries.<id>.apiKey`: eklenti düzeyinde API anahtarı kolaylık alanı (eklenti destekliyorsa).
- `plugins.entries.<id>.env`: eklenti kapsamlı env değişkeni haritası.
- `plugins.entries.<id>.hooks.allowPromptInjection`: `false` olduğunda çekirdek `before_prompt_build` kancasını engeller ve eski `before_agent_start` içindeki istemi değiştiren alanları yok sayar; eski `modelOverride` ve `providerOverride` alanlarını ise korur. Yerel eklenti kancaları ve desteklenen paket tarafından sağlanan kanca dizinleri için geçerlidir.
- `plugins.entries.<id>.subagent.allowModelOverride`: bu eklentiye arka plan alt aracı çalıştırmaları için çalışma başına `provider` ve `model` geçersiz kılmaları isteme konusunda açık güven ver.
- `plugins.entries.<id>.subagent.allowedModels`: güvenilen alt aracı geçersiz kılmaları için isteğe bağlı kanonik `provider/model` hedefleri allowlist'i. Herhangi bir modele bilinçli olarak izin vermek istiyorsanız `"*"` kullanın.
- `plugins.entries.<id>.config`: eklentinin tanımladığı yapılandırma nesnesi (varsa yerel OpenClaw eklenti şemasıyla doğrulanır).
- `plugins.entries.firecrawl.config.webFetch`: Firecrawl web-fetch sağlayıcı ayarları.
  - `apiKey`: Firecrawl API anahtarı (SecretRef kabul eder). `plugins.entries.firecrawl.config.webSearch.apiKey`, eski `tools.web.fetch.firecrawl.apiKey` veya `FIRECRAWL_API_KEY` env değişkenine geri döner.
  - `baseUrl`: Firecrawl API base URL (varsayılan: `https://api.firecrawl.dev`).
  - `onlyMainContent`: sayfalardan yalnızca ana içeriği çıkar (varsayılan: `true`).
  - `maxAgeMs`: milisaniye cinsinden azami önbellek yaşı (varsayılan: `172800000` / 2 gün).
  - `timeoutSeconds`: scrape isteği zaman aşımı saniye cinsinden (varsayılan: `60`).
- `plugins.entries.xai.config.xSearch`: xAI X Search (Grok web search) ayarları.
  - `enabled`: X Search sağlayıcısını etkinleştir.
  - `model`: arama için kullanılacak Grok modeli (ör. `"grok-4-1-fast"`).
- `plugins.entries.memory-core.config.dreaming`: bellek dreaming (deneysel) ayarları. Aşamalar ve eşikler için bkz. [Dreaming](/tr/concepts/dreaming).
  - `enabled`: ana dreaming anahtarı (varsayılan `false`).
  - `frequency`: her tam dreaming süpürmesi için cron sıklığı (varsayılan `"0 3 * * *"`).
  - Aşama ilkesi ve eşikler uygulama ayrıntılarıdır (kullanıcıya açık yapılandırma anahtarları değildir).
- Etkin Claude paket eklentileri, `settings.json` içinden gömülü Pi varsayılanları da sağlayabilir; OpenClaw bunları ham OpenClaw yapılandırma yamaları olarak değil, temizlenmiş aracı ayarları olarak uygular.
- `plugins.slots.memory`: etkin bellek eklenti kimliğini seçin veya bellek eklentilerini devre dışı bırakmak için `"none"` seçin.
- `plugins.slots.contextEngine`: etkin bağlam motoru eklenti kimliğini seçin; başka bir motor yükleyip seçmediğiniz sürece varsayılan `"legacy"` olur.
- `plugins.installs`: `openclaw plugins update` tarafından kullanılan CLI yönetimli kurulum meta verisi.
  - `source`, `spec`, `sourcePath`, `installPath`, `version`, `resolvedName`, `resolvedVersion`, `resolvedSpec`, `integrity`, `shasum`, `resolvedAt`, `installedAt` içerir.
  - `plugins.installs.*` alanlarını yönetilen durum olarak ele alın; el ile düzenlemek yerine CLI komutlarını tercih edin.

Bkz. [Plugins](/tr/tools/plugin).

---

## Tarayıcı

```json5
{
  browser: {
    enabled: true,
    evaluateEnabled: true,
    defaultProfile: "user",
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: true, // varsayılan trusted-network modu
      // allowPrivateNetwork: true, // eski takma ad
      // hostnameAllowlist: ["*.example.com", "example.com"],
      // allowedHostnames: ["localhost"],
    },
    profiles: {
      openclaw: { cdpPort: 18800, color: "#FF4500" },
      work: { cdpPort: 18801, color: "#0066CC" },
      user: { driver: "existing-session", attachOnly: true, color: "#00AA00" },
      brave: {
        driver: "existing-session",
        attachOnly: true,
        userDataDir: "~/Library/Application Support/BraveSoftware/Brave-Browser",
        color: "#FB542B",
      },
      remote: { cdpUrl: "http://10.0.0.42:9222", color: "#00AA00" },
    },
    color: "#FF4500",
    // headless: false,
    // noSandbox: false,
    // extraArgs: [],
    // executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    // attachOnly: false,
  },
}
```

- `evaluateEnabled: false`, `act:evaluate` ve `wait --fn` işlemlerini devre dışı bırakır.
- `ssrfPolicy.dangerouslyAllowPrivateNetwork`, ayarlanmadığında varsayılan olarak `true` olur (trusted-network modeli).
- Yalnızca genel tarayıcı gezintisi için katı moda geçmek istiyorsanız `ssrfPolicy.dangerouslyAllowPrivateNetwork: false` ayarlayın.
- Katı modda uzak CDP profil uç noktaları (`profiles.*.cdpUrl`), erişilebilirlik/keşif kontrolleri sırasında aynı özel ağ engellemesine tabi olur.
- `ssrfPolicy.allowPrivateNetwork`, eski takma ad olarak desteklenmeye devam eder.
- Katı modda açık istisnalar için `ssrfPolicy.hostnameAllowlist` ve `ssrfPolicy.allowedHostnames` kullanın.
- Uzak profiller yalnızca attach-only'dir (başlat/durdur/sıfırla devre dışı).
- `profiles.*.cdpUrl`, `http://`, `https://`, `ws://` ve `wss://` kabul eder.
  OpenClaw'ın `/json/version` keşfi yapmasını istiyorsanız HTTP(S) kullanın;
  sağlayıcınız size doğrudan bir DevTools WebSocket URL'si veriyorsa WS(S)
  kullanın.
- `existing-session` profilleri yalnızca host