---
read_when:
    - Discord kanal özellikleri üzerinde çalışırken
summary: Discord bot desteği durumu, yetenekleri ve yapılandırması
title: Discord
x-i18n:
    generated_at: "2026-04-06T03:08:11Z"
    model: gpt-5.4
    provider: openai
    source_hash: 54af2176a1b4fa1681e3f07494def0c652a2730165058848000e71a59e2a9d08
    source_path: channels/discord.md
    workflow: 15
---

# Discord (Bot API)

Durum: resmi Discord gateway üzerinden DM'ler ve sunucu kanalları için hazır.

<CardGroup cols={3}>
  <Card title="Eşleme" icon="link" href="/tr/channels/pairing">
    Discord DM'leri varsayılan olarak eşleme modundadır.
  </Card>
  <Card title="Slash komutları" icon="terminal" href="/tr/tools/slash-commands">
    Yerel komut davranışı ve komut kataloğu.
  </Card>
  <Card title="Kanal sorun giderme" icon="wrench" href="/tr/channels/troubleshooting">
    Kanallar arası tanılama ve onarım akışı.
  </Card>
</CardGroup>

## Hızlı kurulum

Bot içeren yeni bir uygulama oluşturmanız, botu sunucunuza eklemeniz ve OpenClaw ile eşlemeniz gerekir. Botunuzu kendi özel sunucunuza eklemenizi öneririz. Henüz bir sunucunuz yoksa önce [bir tane oluşturun](https://support.discord.com/hc/en-us/articles/204849977-How-do-I-create-a-server) (**Create My Own > For me and my friends** seçin).

<Steps>
  <Step title="Bir Discord uygulaması ve bot oluşturun">
    [Discord Developer Portal](https://discord.com/developers/applications) adresine gidin ve **New Application** seçeneğine tıklayın. Adını "OpenClaw" gibi bir şey yapın.

    Kenar çubuğunda **Bot** seçeneğine tıklayın. **Username** alanını, OpenClaw ajanınıza verdiğiniz ad olarak ayarlayın.

  </Step>

  <Step title="Ayrıcalıklı intent'leri etkinleştirin">
    Hâlâ **Bot** sayfasındayken aşağı kaydırıp **Privileged Gateway Intents** bölümünde şunları etkinleştirin:

    - **Message Content Intent** (gerekli)
    - **Server Members Intent** (önerilir; rol izin listeleri ve adtan-kimlik eşlemesi için gereklidir)
    - **Presence Intent** (isteğe bağlı; yalnızca presence güncellemeleri için gerekir)

  </Step>

  <Step title="Bot token'ınızı kopyalayın">
    **Bot** sayfasında tekrar yukarı kaydırın ve **Reset Token** seçeneğine tıklayın.

    <Note>
    Adına rağmen bu işlem ilk token'ınızı oluşturur — hiçbir şey "sıfırlanmıyor".
    </Note>

    Token'ı kopyalayın ve bir yere kaydedin. Bu sizin **Bot Token**'ınızdır ve kısa süre içinde buna ihtiyacınız olacak.

  </Step>

  <Step title="Bir davet URL'si oluşturun ve botu sunucunuza ekleyin">
    Kenar çubuğunda **OAuth2** seçeneğine tıklayın. Botu sunucunuza eklemek için doğru izinlere sahip bir davet URL'si oluşturacaksınız.

    Aşağı kaydırıp **OAuth2 URL Generator** bölümünde şunları etkinleştirin:

    - `bot`
    - `applications.commands`

    Altında bir **Bot Permissions** bölümü görünecektir. Şunları etkinleştirin:

    - View Channels
    - Send Messages
    - Read Message History
    - Embed Links
    - Attach Files
    - Add Reactions (isteğe bağlı)

    Alttaki oluşturulmuş URL'yi kopyalayın, tarayıcınıza yapıştırın, sunucunuzu seçin ve bağlamak için **Continue** seçeneğine tıklayın. Artık Discord sunucusunda botunuzu görmelisiniz.

  </Step>

  <Step title="Developer Mode'u etkinleştirin ve kimliklerinizi toplayın">
    Discord uygulamasına geri dönün; dahili kimlikleri kopyalayabilmek için Developer Mode'u etkinleştirmeniz gerekir.

    1. **User Settings**'e (avatarınızın yanındaki dişli simgesi) tıklayın → **Advanced** → **Developer Mode** seçeneğini açın
    2. Kenar çubuğunda **sunucu simgenize** sağ tıklayın → **Copy Server ID**
    3. **Kendi avatarınıza** sağ tıklayın → **Copy User ID**

    **Server ID** ve **User ID** değerlerinizi Bot Token'ınızla birlikte kaydedin — sonraki adımda üçünü de OpenClaw'a göndereceksiniz.

  </Step>

  <Step title="Sunucu üyelerinden DM alımına izin verin">
    Eşlemenin çalışması için Discord'un botunuzun size DM göndermesine izin vermesi gerekir. **Sunucu simgenize** sağ tıklayın → **Privacy Settings** → **Direct Messages** seçeneğini açın.

    Bu, sunucu üyelerinin (botlar dahil) size DM göndermesine izin verir. OpenClaw ile Discord DM'lerini kullanmak istiyorsanız bunu etkin bırakın. Yalnızca sunucu kanallarını kullanmayı planlıyorsanız eşlemeden sonra DM'leri devre dışı bırakabilirsiniz.

  </Step>

  <Step title="Bot token'ınızı güvenli şekilde ayarlayın (sohbette göndermeyin)">
    Discord bot token'ınız bir sırdır (parola gibi). Ajanınıza mesaj atmadan önce OpenClaw'ı çalıştıran makinede ayarlayın.

```bash
export DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN"
openclaw config set channels.discord.token --ref-provider default --ref-source env --ref-id DISCORD_BOT_TOKEN --dry-run
openclaw config set channels.discord.token --ref-provider default --ref-source env --ref-id DISCORD_BOT_TOKEN
openclaw config set channels.discord.enabled true --strict-json
openclaw gateway
```

    OpenClaw zaten arka plan hizmeti olarak çalışıyorsa, OpenClaw Mac uygulaması üzerinden veya `openclaw gateway run` sürecini durdurup yeniden başlatarak yeniden başlatın.

  </Step>

  <Step title="OpenClaw'ı yapılandırın ve eşleyin">

    <Tabs>
      <Tab title="Ajanınıza sorun">
        OpenClaw ajanınızla mevcut herhangi bir kanalda (ör. Telegram) sohbet edin ve bunu söyleyin. Discord ilk kanalınızsa bunun yerine CLI / yapılandırma sekmesini kullanın.

        > "Discord bot token'ımı yapılandırmada zaten ayarladım. Lütfen User ID `<user_id>` ve Server ID `<server_id>` ile Discord kurulumunu tamamla."
      </Tab>
      <Tab title="CLI / yapılandırma">
        Dosya tabanlı yapılandırmayı tercih ediyorsanız şunu ayarlayın:

```json5
{
  channels: {
    discord: {
      enabled: true,
      token: {
        source: "env",
        provider: "default",
        id: "DISCORD_BOT_TOKEN",
      },
    },
  },
}
```

        Varsayılan hesap için env fallback:

```bash
DISCORD_BOT_TOKEN=...
```

        Düz metin `token` değerleri desteklenir. SecretRef değerleri de `channels.discord.token` için env/file/exec sağlayıcıları genelinde desteklenir. Bkz. [Secrets Management](/tr/gateway/secrets).

      </Tab>
    </Tabs>

  </Step>

  <Step title="İlk DM eşlemesini onaylayın">
    Gateway çalışana kadar bekleyin, ardından Discord'da botunuza DM gönderin. Bot bir eşleme koduyla yanıt verecektir.

    <Tabs>
      <Tab title="Ajanınıza sorun">
        Eşleme kodunu mevcut kanalınızda ajanınıza gönderin:

        > "Bu Discord eşleme kodunu onayla: `<CODE>`"
      </Tab>
      <Tab title="CLI">

```bash
openclaw pairing list discord
openclaw pairing approve discord <CODE>
```

      </Tab>
    </Tabs>

    Eşleme kodlarının süresi 1 saat sonra dolar.

    Artık Discord'da ajanınızla DM üzerinden sohbet edebilmelisiniz.

  </Step>
</Steps>

<Note>
Token çözümlemesi hesap farkındalığına sahiptir. Yapılandırmadaki token değerleri env fallback'e üstün gelir. `DISCORD_BOT_TOKEN` yalnızca varsayılan hesap için kullanılır.
Gelişmiş giden çağrılarda (mesaj aracı/kanal işlemleri), açık bir çağrı başına `token` değeri o çağrı için kullanılır. Bu, gönderme ve okuma/probe tarzı işlemler için geçerlidir (örneğin read/search/fetch/thread/pins/permissions). Hesap ilkesi/yeniden deneme ayarları ise etkin çalışma zamanı anlık görüntüsünde seçili hesaptan gelmeye devam eder.
</Note>

## Önerilen: Bir sunucu çalışma alanı kurun

DM'ler çalıştıktan sonra, Discord sunucunuzu tam bir çalışma alanı olarak kurabilirsiniz; burada her kanal kendi bağlamına sahip kendi ajan oturumunu alır. Bu, yalnızca siz ve botunuzun bulunduğu özel sunucular için önerilir.

<Steps>
  <Step title="Sunucunuzu sunucu izin listesine ekleyin">
    Bu, ajanınızın yalnızca DM'lerde değil, sunucunuzdaki herhangi bir kanalda yanıt verebilmesini sağlar.

    <Tabs>
      <Tab title="Ajanınıza sorun">
        > "Discord Server ID `<server_id>` değerimi sunucu izin listesine ekle"
      </Tab>
      <Tab title="Yapılandırma">

```json5
{
  channels: {
    discord: {
      groupPolicy: "allowlist",
      guilds: {
        YOUR_SERVER_ID: {
          requireMention: true,
          users: ["YOUR_USER_ID"],
        },
      },
    },
  },
}
```

      </Tab>
    </Tabs>

  </Step>

  <Step title="@mention olmadan yanıta izin verin">
    Varsayılan olarak ajanınız sunucu kanallarında yalnızca @mention aldığında yanıt verir. Özel bir sunucu için, muhtemelen her mesaja yanıt vermesini istersiniz.

    <Tabs>
      <Tab title="Ajanınıza sorun">
        > "Ajanımın bu sunucuda @mention edilmeden yanıt verebilmesine izin ver"
      </Tab>
      <Tab title="Yapılandırma">
        Sunucu yapılandırmanızda `requireMention: false` ayarlayın:

```json5
{
  channels: {
    discord: {
      guilds: {
        YOUR_SERVER_ID: {
          requireMention: false,
        },
      },
    },
  },
}
```

      </Tab>
    </Tabs>

  </Step>

  <Step title="Sunucu kanallarında bellek için plan yapın">
    Varsayılan olarak, uzun süreli bellek (MEMORY.md) yalnızca DM oturumlarında yüklenir. Sunucu kanalları MEMORY.md'yi otomatik yüklemez.

    <Tabs>
      <Tab title="Ajanınıza sorun">
        > "Discord kanallarında soru sorduğumda, MEMORY.md'den uzun süreli bağlam gerekirse memory_search veya memory_get kullan."
      </Tab>
      <Tab title="Manuel">
        Her kanalda ortak bağlama ihtiyacınız varsa, sabit yönergeleri `AGENTS.md` veya `USER.md` içine koyun (bunlar her oturuma enjekte edilir). Uzun süreli notları `MEMORY.md` içinde tutun ve gerektiğinde bellek araçlarıyla erişin.
      </Tab>
    </Tabs>

  </Step>
</Steps>

Şimdi Discord sunucunuzda bazı kanallar oluşturun ve sohbet etmeye başlayın. Ajanınız kanal adını görebilir ve her kanal kendi yalıtılmış oturumunu alır — böylece `#coding`, `#home`, `#research` veya iş akışınıza uyan başka kanallar kurabilirsiniz.

## Çalışma zamanı modeli

- Gateway, Discord bağlantısını sahiplenir.
- Yanıt yönlendirmesi belirleyicidir: Discord'dan gelen yanıtlar tekrar Discord'a gider.
- Varsayılan olarak (`session.dmScope=main`), doğrudan sohbetler ajanın ana oturumunu paylaşır (`agent:main:main`).
- Sunucu kanalları yalıtılmış oturum anahtarlarıdır (`agent:<agentId>:discord:channel:<channelId>`).
- Grup DM'leri varsayılan olarak yok sayılır (`channels.discord.dm.groupEnabled=false`).
- Yerel slash komutları, yönlendirilen sohbet oturumuna `CommandTargetSessionKey` taşımaya devam ederken yalıtılmış komut oturumlarında çalışır (`agent:<agentId>:discord:slash:<userId>`).

## Forum kanalları

Discord forum ve medya kanalları yalnızca ileti dizisi gönderilerini kabul eder. OpenClaw bunları oluşturmak için iki yolu destekler:

- İleti dizisini otomatik oluşturmak için forum üst öğesine (`channel:<forumId>`) mesaj gönderin. İleti dizisi başlığı, mesajınızın boş olmayan ilk satırını kullanır.
- Bir ileti dizisini doğrudan oluşturmak için `openclaw message thread create` kullanın. Forum kanalları için `--message-id` geçmeyin.

Örnek: ileti dizisi oluşturmak için forum üst öğesine gönderim

```bash
openclaw message send --channel discord --target channel:<forumId> \
  --message "Topic title\nBody of the post"
```

Örnek: açıkça bir forum ileti dizisi oluşturma

```bash
openclaw message thread create --channel discord --target channel:<forumId> \
  --thread-name "Topic title" --message "Body of the post"
```

Forum üst öğeleri Discord bileşenlerini kabul etmez. Bileşenlere ihtiyacınız varsa, ileti dizisinin kendisine (`channel:<threadId>`) gönderin.

## Etkileşimli bileşenler

OpenClaw, ajan mesajları için Discord components v2 container desteği sunar. `components` yükü ile mesaj aracını kullanın. Etkileşim sonuçları normal gelen mesajlar olarak tekrar ajana yönlendirilir ve mevcut Discord `replyToMode` ayarlarını izler.

Desteklenen bloklar:

- `text`, `section`, `separator`, `actions`, `media-gallery`, `file`
- Action row'lar en fazla 5 düğmeye veya tek bir seçim menüsüne izin verir
- Seçim türleri: `string`, `user`, `role`, `mentionable`, `channel`

Varsayılan olarak bileşenler tek kullanımlıktır. Düğmelerin, seçimlerin ve formların süreleri dolana kadar birden çok kez kullanılmasına izin vermek için `components.reusable=true` ayarlayın.

Bir düğmeye kimlerin tıklayabileceğini kısıtlamak için o düğmede `allowedUsers` ayarlayın (Discord kullanıcı kimlikleri, etiketler veya `*`). Yapılandırıldığında, eşleşmeyen kullanıcılar geçici bir red yanıtı alır.

`/model` ve `/models` slash komutları, sağlayıcı ve model açılır menülerinin yanı sıra bir Submit adımı içeren etkileşimli bir model seçici açar. Seçici yanıtı geçicidir ve yalnızca komutu çağıran kullanıcı bunu kullanabilir.

Dosya ekleri:

- `file` blokları bir ek referansını göstermelidir (`attachment://<filename>`)
- Eki `media`/`path`/`filePath` ile sağlayın (tek dosya); birden fazla dosya için `media-gallery` kullanın
- Yükleme adının ek referansıyla eşleşmesi gerektiğinde bunu geçersiz kılmak için `filename` kullanın

Modal formlar:

- En fazla 5 alanla `components.modal` ekleyin
- Alan türleri: `text`, `checkbox`, `radio`, `select`, `role-select`, `user-select`
- OpenClaw otomatik olarak bir tetikleyici düğme ekler

Örnek:

```json5
{
  channel: "discord",
  action: "send",
  to: "channel:123456789012345678",
  message: "Optional fallback text",
  components: {
    reusable: true,
    text: "Choose a path",
    blocks: [
      {
        type: "actions",
        buttons: [
          {
            label: "Approve",
            style: "success",
            allowedUsers: ["123456789012345678"],
          },
          { label: "Decline", style: "danger" },
        ],
      },
      {
        type: "actions",
        select: {
          type: "string",
          placeholder: "Pick an option",
          options: [
            { label: "Option A", value: "a" },
            { label: "Option B", value: "b" },
          ],
        },
      },
    ],
    modal: {
      title: "Details",
      triggerLabel: "Open form",
      fields: [
        { type: "text", label: "Requester" },
        {
          type: "select",
          label: "Priority",
          options: [
            { label: "Low", value: "low" },
            { label: "High", value: "high" },
          ],
        },
      ],
    },
  },
}
```

## Erişim denetimi ve yönlendirme

<Tabs>
  <Tab title="DM ilkesi">
    `channels.discord.dmPolicy`, DM erişimini denetler (eski: `channels.discord.dm.policy`):

    - `pairing` (varsayılan)
    - `allowlist`
    - `open` (`channels.discord.allowFrom` içine `"*"` eklenmesini gerektirir; eski: `channels.discord.dm.allowFrom`)
    - `disabled`

    DM ilkesi açık değilse, bilinmeyen kullanıcılar engellenir (veya `pairing` modunda eşleme istenir).

    Çoklu hesap önceliği:

    - `channels.discord.accounts.default.allowFrom` yalnızca `default` hesabına uygulanır.
    - Adlandırılmış hesaplar, kendi `allowFrom` değeri ayarlanmamışsa `channels.discord.allowFrom` değerini devralır.
    - Adlandırılmış hesaplar `channels.discord.accounts.default.allowFrom` değerini devralmaz.

    Teslimat için DM hedef biçimi:

    - `user:<id>`
    - `<@id>` mention

    Yalın sayısal kimlikler belirsizdir ve açık bir kullanıcı/kanal hedef türü verilmedikçe reddedilir.

  </Tab>

  <Tab title="Sunucu ilkesi">
    Sunucu işleme, `channels.discord.groupPolicy` ile denetlenir:

    - `open`
    - `allowlist`
    - `disabled`

    `channels.discord` mevcut olduğunda güvenli taban çizgisi `allowlist`tir.

    `allowlist` davranışı:

    - sunucu `channels.discord.guilds` ile eşleşmelidir (`id` tercih edilir, slug kabul edilir)
    - isteğe bağlı gönderen izin listeleri: `users` (kararlı kimlikler önerilir) ve `roles` (yalnızca rol kimlikleri); bunlardan biri yapılandırılmışsa, gönderenler `users` VEYA `roles` ile eşleştiğinde izinli sayılır
    - doğrudan ad/etiket eşleştirmesi varsayılan olarak devre dışıdır; bunu yalnızca acil durum uyumluluk modu olarak etkinleştirmek için `channels.discord.dangerouslyAllowNameMatching: true` kullanın
    - `users` için adlar/etiketler desteklenir, ancak kimlikler daha güvenlidir; `openclaw security audit`, ad/etiket girdileri kullanıldığında uyarı verir
    - bir sunucuda `channels` yapılandırılmışsa, listelenmeyen kanallar reddedilir
    - bir sunucuda `channels` bloğu yoksa, izin listesine alınmış o sunucudaki tüm kanallara izin verilir

    Örnek:

```json5
{
  channels: {
    discord: {
      groupPolicy: "allowlist",
      guilds: {
        "123456789012345678": {
          requireMention: true,
          ignoreOtherMentions: true,
          users: ["987654321098765432"],
          roles: ["123456789012345678"],
          channels: {
            general: { allow: true },
            help: { allow: true, requireMention: true },
          },
        },
      },
    },
  },
}
```

    Yalnızca `DISCORD_BOT_TOKEN` ayarlayıp bir `channels.discord` bloğu oluşturmazsanız, çalışma zamanı fallback değeri `groupPolicy="allowlist"` olur (günlüklerde bir uyarıyla), `channels.defaults.groupPolicy` değeri `open` olsa bile.

  </Tab>

  <Tab title="Mention'lar ve grup DM'leri">
    Sunucu mesajları varsayılan olarak mention ile kapılanır.

    Mention algılama şunları içerir:

    - açık bot mention
    - yapılandırılmış mention desenleri (`agents.list[].groupChat.mentionPatterns`, fallback `messages.groupChat.mentionPatterns`)
    - desteklenen durumlarda bota dolaylı yanıt davranışı

    `requireMention`, sunucu/kanal başına yapılandırılır (`channels.discord.guilds...`).
    `ignoreOtherMentions`, bot dışında başka bir kullanıcıdan/rolden bahseden mesajları isteğe bağlı olarak düşürür (@everyone/@here hariç).

    Grup DM'leri:

    - varsayılan: yok sayılır (`dm.groupEnabled=false`)
    - isteğe bağlı izin listesi: `dm.groupChannels` (kanal kimlikleri veya slug'lar)

  </Tab>
</Tabs>

### Role dayalı ajan yönlendirme

Discord sunucu üyelerini rol kimliğine göre farklı ajanlara yönlendirmek için `bindings[].match.roles` kullanın. Role dayalı bağlamalar yalnızca rol kimliklerini kabul eder ve peer veya parent-peer bağlamalarından sonra, yalnızca sunucu bağlamalarından önce değerlendirilir. Bir bağlama başka eşleşme alanları da ayarlıyorsa (örneğin `peer` + `guildId` + `roles`), yapılandırılan tüm alanlar eşleşmelidir.

```json5
{
  bindings: [
    {
      agentId: "opus",
      match: {
        channel: "discord",
        guildId: "123456789012345678",
        roles: ["111111111111111111"],
      },
    },
    {
      agentId: "sonnet",
      match: {
        channel: "discord",
        guildId: "123456789012345678",
      },
    },
  ],
}
```

## Developer Portal kurulumu

<AccordionGroup>
  <Accordion title="Uygulama ve bot oluşturun">

    1. Discord Developer Portal -> **Applications** -> **New Application**
    2. **Bot** -> **Add Bot**
    3. Bot token'ını kopyalayın

  </Accordion>

  <Accordion title="Ayrıcalıklı intent'ler">
    **Bot -> Privileged Gateway Intents** içinde şunları etkinleştirin:

    - Message Content Intent
    - Server Members Intent (önerilir)

    Presence intent isteğe bağlıdır ve yalnızca presence güncellemeleri almak istiyorsanız gerekir. Bot presence ayarlamak (`setPresence`) üyeler için presence güncellemelerini etkinleştirmeyi gerektirmez.

  </Accordion>

  <Accordion title="OAuth kapsamları ve temel izinler">
    OAuth URL oluşturucu:

    - kapsamlar: `bot`, `applications.commands`

    Tipik temel izinler:

    - View Channels
    - Send Messages
    - Read Message History
    - Embed Links
    - Attach Files
    - Add Reactions (isteğe bağlı)

    Açıkça gerekli değilse `Administrator` kullanmayın.

  </Accordion>

  <Accordion title="Kimlikleri kopyalayın">
    Discord Developer Mode'u etkinleştirin, ardından şunları kopyalayın:

    - sunucu kimliği
    - kanal kimliği
    - kullanıcı kimliği

    Güvenilir denetimler ve probelar için OpenClaw yapılandırmasında sayısal kimlikleri tercih edin.

  </Accordion>
</AccordionGroup>

## Yerel komutlar ve komut kimlik doğrulaması

- `commands.native` varsayılan olarak `"auto"` değerini alır ve Discord için etkindir.
- Kanal başına geçersiz kılma: `channels.discord.commands.native`.
- `commands.native=false`, daha önce kaydedilmiş Discord yerel komutlarını açıkça temizler.
- Yerel komut kimlik doğrulaması, normal mesaj işlemenin kullandığı aynı Discord izin listelerini/ilkelerini kullanır.
- Komutlar yetkisiz kullanıcılar için Discord arayüzünde hâlâ görünebilir; ancak yürütme OpenClaw yetkilendirmesini yine de uygular ve "not authorized" döndürür.

Komut kataloğu ve davranış için [Slash commands](/tr/tools/slash-commands) bölümüne bakın.

Varsayılan slash komut ayarları:

- `ephemeral: true`

## Özellik ayrıntıları

<AccordionGroup>
  <Accordion title="Yanıt etiketleri ve yerel yanıtlar">
    Discord, ajan çıktısında yanıt etiketlerini destekler:

    - `[[reply_to_current]]`
    - `[[reply_to:<id>]]`

    `channels.discord.replyToMode` ile denetlenir:

    - `off` (varsayılan)
    - `first`
    - `all`
    - `batched`

    Not: `off`, dolaylı yanıt zincirlemeyi devre dışı bırakır. Açık `[[reply_to_*]]` etiketleri yine de dikkate alınır.
    `first`, turdaki ilk giden Discord mesajına dolaylı yerel yanıt referansını her zaman ekler.
    `batched`, Discord'un dolaylı yerel yanıt referansını yalnızca
    gelen turun birden çok mesajdan oluşan debounce edilmiş bir toplu işlem olduğu durumda ekler. Bu,
    yerel yanıtları çoğunlukla belirsiz, patlamalı sohbetler için isteyip her
    tek mesajlı tur için istemediğiniz durumlarda faydalıdır.

    Mesaj kimlikleri bağlamda/geçmişte görünür, böylece ajanlar belirli mesajları hedefleyebilir.

  </Accordion>

  <Accordion title="Canlı akış önizlemesi">
    OpenClaw, geçici bir mesaj gönderip metin geldikçe bunu düzenleyerek taslak yanıtları akıtabilir.

    - `channels.discord.streaming`, önizleme akışını denetler (`off` | `partial` | `block` | `progress`, varsayılan: `off`).
    - Varsayılan değer `off` olarak kalır; çünkü Discord önizleme düzenlemeleri, özellikle aynı hesabı veya sunucu trafiğini birden fazla bot ya da gateway paylaşıyorsa hızla oran sınırlarına takılabilir.
    - `progress`, kanallar arası tutarlılık için kabul edilir ve Discord'da `partial` ile eşlenir.
    - `channels.discord.streamMode` eski bir takma addır ve otomatik olarak geçirilir.
    - `partial`, token'lar geldikçe tek bir önizleme mesajını düzenler.
    - `block`, taslak boyutunda parçalar yayımlar (boyutu ve kesme noktalarını ayarlamak için `draftChunk` kullanın).

    Örnek:

```json5
{
  channels: {
    discord: {
      streaming: "partial",
    },
  },
}
```

    `block` modu parça varsayılanları (`channels.discord.textChunkLimit` ile sınırlandırılır):

```json5
{
  channels: {
    discord: {
      streaming: "block",
      draftChunk: {
        minChars: 200,
        maxChars: 800,
        breakPreference: "paragraph",
      },
    },
  },
}
```

    Önizleme akışı yalnızca metin içindir; medya yanıtları normal teslimata geri döner.

    Not: önizleme akışı, blok akışından ayrıdır. Discord için blok akışı açıkça
    etkinleştirildiğinde OpenClaw, çift akışı önlemek için önizleme akışını atlar.

  </Accordion>

  <Accordion title="Geçmiş, bağlam ve ileti dizisi davranışı">
    Sunucu geçmişi bağlamı:

    - `channels.discord.historyLimit` varsayılan `20`
    - fallback: `messages.groupChat.historyLimit`
    - `0` devre dışı bırakır

    DM geçmişi denetimleri:

    - `channels.discord.dmHistoryLimit`
    - `channels.discord.dms["<user_id>"].historyLimit`

    İleti dizisi davranışı:

    - Discord ileti dizileri kanal oturumları olarak yönlendirilir
    - üst ileti dizisi meta verileri üst oturum bağlantısı için kullanılabilir
    - ileti dizisi yapılandırması, ileti dizisine özel bir girdi yoksa üst kanal yapılandırmasını devralır

    Kanal konuları **güvenilmeyen** bağlam olarak enjekte edilir (sistem istemi olarak değil).
    Yanıt ve alıntılanmış mesaj bağlamı şu anda alındığı gibi kalır.
    Discord izin listeleri öncelikle ajanın kim tarafından tetiklenebileceğini kapılar; bu tam bir ek bağlam redaksiyon sınırı değildir.

  </Accordion>

  <Accordion title="Alt ajanlar için ileti dizisine bağlı oturumlar">
    Discord, bir ileti dizisini bir oturum hedefine bağlayabilir; böylece o ileti dizisindeki sonraki mesajlar aynı oturuma yönlendirilmeye devam eder (alt ajan oturumları dahil).

    Komutlar:

    - `/focus <target>` geçerli/yeni ileti dizisini bir alt ajan/oturum hedefine bağla
    - `/unfocus` geçerli ileti dizisi bağlamasını kaldır
    - `/agents` etkin çalıştırmaları ve bağlama durumunu göster
    - `/session idle <duration|off>` odaklı bağlamalar için etkin olmama durumunda otomatik odak kaldırmayı incele/güncelle
    - `/session max-age <duration|off>` odaklı bağlamalar için kesin azami yaşı incele/güncelle

    Yapılandırma:

```json5
{
  session: {
    threadBindings: {
      enabled: true,
      idleHours: 24,
      maxAgeHours: 0,
    },
  },
  channels: {
    discord: {
      threadBindings: {
        enabled: true,
        idleHours: 24,
        maxAgeHours: 0,
        spawnSubagentSessions: false, // isteğe bağlı etkinleştirme
      },
    },
  },
}
```

    Notlar:

    - `session.threadBindings.*` genel varsayılanları ayarlar.
    - `channels.discord.threadBindings.*`, Discord davranışını geçersiz kılar.
    - `spawnSubagentSessions`, `sessions_spawn({ thread: true })` için ileti dizilerini otomatik oluşturup bağlamak üzere true olmalıdır.
    - `spawnAcpSessions`, ACP için ileti dizilerini otomatik oluşturup bağlamak üzere true olmalıdır (`/acp spawn ... --thread ...` veya `sessions_spawn({ runtime: "acp", thread: true })`).
    - Bir hesap için ileti dizisi bağlamaları devre dışıysa `/focus` ve ilgili ileti dizisi bağlama işlemleri kullanılamaz.

    Bkz. [Sub-agents](/tr/tools/subagents), [ACP Agents](/tr/tools/acp-agents) ve [Configuration Reference](/tr/gateway/configuration-reference).

  </Accordion>

  <Accordion title="Kalıcı ACP kanal bağlamaları">
    Kararlı "her zaman açık" ACP çalışma alanları için, Discord sohbetlerini hedefleyen üst düzey türlenmiş ACP bağlamaları yapılandırın.

    Yapılandırma yolu:

    - `type: "acp"` ve `match.channel: "discord"` ile `bindings[]`

    Örnek:

```json5
{
  agents: {
    list: [
      {
        id: "codex",
        runtime: {
          type: "acp",
          acp: {
            agent: "codex",
            backend: "acpx",
            mode: "persistent",
            cwd: "/workspace/openclaw",
          },
        },
      },
    ],
  },
  bindings: [
    {
      type: "acp",
      agentId: "codex",
      match: {
        channel: "discord",
        accountId: "default",
        peer: { kind: "channel", id: "222222222222222222" },
      },
      acp: { label: "codex-main" },
    },
  ],
  channels: {
    discord: {
      guilds: {
        "111111111111111111": {
          channels: {
            "222222222222222222": {
              requireMention: false,
            },
          },
        },
      },
    },
  },
}
```

    Notlar:

    - `/acp spawn codex --bind here`, geçerli Discord kanalını veya ileti dizisini yerinde bağlar ve gelecekteki mesajların aynı ACP oturumuna yönlendirilmesini sağlar.
    - Bu yine de "yeni bir Codex ACP oturumu başlat" anlamına gelebilir, ancak kendi başına yeni bir Discord ileti dizisi oluşturmaz. Mevcut kanal sohbet yüzeyi olarak kalır.
    - Codex yine de disk üzerindeki kendi `cwd` veya backend çalışma alanında çalışabilir. Bu çalışma alanı Discord ileti dizisi değil, çalışma zamanı durumudur.
    - İleti dizisi mesajları üst kanal ACP bağlamasını devralabilir.
    - Bağlı bir kanal veya ileti dizisinde `/new` ve `/reset`, aynı ACP oturumunu yerinde sıfırlar.
    - Geçici ileti dizisi bağlamaları hâlâ çalışır ve etkin olduklarında hedef çözümlemeyi geçersiz kılabilir.
    - `spawnAcpSessions`, yalnızca OpenClaw'ın `--thread auto|here` üzerinden bir alt ileti dizisi oluşturup bağlaması gerektiğinde zorunludur. Geçerli kanaldaki `/acp spawn ... --bind here` için gerekli değildir.

    Bağlama davranışı ayrıntıları için [ACP Agents](/tr/tools/acp-agents) bölümüne bakın.

  </Accordion>

  <Accordion title="Tepki bildirimleri">
    Sunucu başına tepki bildirim modu:

    - `off`
    - `own` (varsayılan)
    - `all`
    - `allowlist` (`guilds.<id>.users` kullanır)

    Tepki olayları sistem olaylarına dönüştürülür ve yönlendirilen Discord oturumuna eklenir.

  </Accordion>

  <Accordion title="Ack tepkileri">
    `ackReaction`, OpenClaw gelen bir mesajı işlerken bir onay emojisi gönderir.

    Çözümleme sırası:

    - `channels.discord.accounts.<accountId>.ackReaction`
    - `channels.discord.ackReaction`
    - `messages.ackReaction`
    - ajan kimliği emoji fallback'i (`agents.list[].identity.emoji`, aksi hâlde "👀")

    Notlar:

    - Discord unicode emoji veya özel emoji adlarını kabul eder.
    - Bir kanal veya hesap için tepkiyi devre dışı bırakmak üzere `""` kullanın.

  </Accordion>

  <Accordion title="Yapılandırma yazımları">
    Kanal tarafından başlatılan yapılandırma yazımları varsayılan olarak etkindir.

    Bu, `/config set|unset` akışlarını etkiler (komut özellikleri etkin olduğunda).

    Devre dışı bırakma:

```json5
{
  channels: {
    discord: {
      configWrites: false,
    },
  },
}
```

  </Accordion>

  <Accordion title="Gateway proxy">
    `channels.discord.proxy` ile Discord gateway WebSocket trafiğini ve başlangıç REST aramalarını (uygulama kimliği + izin listesi çözümleme) bir HTTP(S) proxy üzerinden yönlendirin.

```json5
{
  channels: {
    discord: {
      proxy: "http://proxy.example:8080",
    },
  },
}
```

    Hesap başına geçersiz kılma:

```json5
{
  channels: {
    discord: {
      accounts: {
        primary: {
          proxy: "http://proxy.example:8080",
        },
      },
    },
  },
}
```

  </Accordion>

  <Accordion title="PluralKit desteği">
    Proxy edilen mesajları sistem üyesi kimliğine eşlemek için PluralKit çözümlemesini etkinleştirin:

```json5
{
  channels: {
    discord: {
      pluralkit: {
        enabled: true,
        token: "pk_live_...", // isteğe bağlı; özel sistemler için gereklidir
      },
    },
  },
}
```

    Notlar:

    - izin listeleri `pk:<memberId>` kullanabilir
    - üye görünen adları yalnızca `channels.discord.dangerouslyAllowNameMatching: true` olduğunda ad/slug ile eşleştirilir
    - aramalar özgün mesaj kimliğini kullanır ve zaman penceresiyle sınırlıdır
    - arama başarısız olursa, proxy edilen mesajlar bot mesajı olarak değerlendirilir ve `allowBots=true` olmadıkça düşürülür

  </Accordion>

  <Accordion title="Presence yapılandırması">
    Presence güncellemeleri, bir durum veya etkinlik alanı ayarladığınızda ya da otomatik presence'i etkinleştirdiğinizde uygulanır.

    Yalnızca durum örneği:

```json5
{
  channels: {
    discord: {
      status: "idle",
    },
  },
}
```

    Etkinlik örneği (özel durum varsayılan etkinlik türüdür):

```json5
{
  channels: {
    discord: {
      activity: "Focus time",
      activityType: 4,
    },
  },
}
```

    Streaming örneği:

```json5
{
  channels: {
    discord: {
      activity: "Live coding",
      activityType: 1,
      activityUrl: "https://twitch.tv/openclaw",
    },
  },
}
```

    Etkinlik türü eşlemesi:

    - 0: Playing
    - 1: Streaming (`activityUrl` gerektirir)
    - 2: Listening
    - 3: Watching
    - 4: Custom (etkinlik metnini durum durumu olarak kullanır; emoji isteğe bağlıdır)
    - 5: Competing

    Otomatik presence örneği (çalışma zamanı sağlık sinyali):

```json5
{
  channels: {
    discord: {
      autoPresence: {
        enabled: true,
        intervalMs: 30000,
        minUpdateIntervalMs: 15000,
        exhaustedText: "token exhausted",
      },
    },
  },
}
```

    Otomatik presence, çalışma zamanı kullanılabilirliğini Discord durumuna eşler: sağlıklı => online, bozulmuş veya bilinmeyen => idle, tükenmiş veya kullanılamaz => dnd. İsteğe bağlı metin geçersiz kılmaları:

    - `autoPresence.healthyText`
    - `autoPresence.degradedText`
    - `autoPresence.exhaustedText` (`{reason}` yer tutucusunu destekler)

  </Accordion>

  <Accordion title="Discord'da onaylar">
    Discord, DM'lerde düğme tabanlı onay işlemeyi destekler ve isteğe bağlı olarak onay istemlerini kaynak kanalda paylaşabilir.

    Yapılandırma yolu:

    - `channels.discord.execApprovals.enabled`
    - `channels.discord.execApprovals.approvers` (isteğe bağlı; mümkün olduğunda `commands.ownerAllowFrom` değerine fallback yapar)
    - `channels.discord.execApprovals.target` (`dm` | `channel` | `both`, varsayılan: `dm`)
    - `agentFilter`, `sessionFilter`, `cleanupAfterResolve`

    Discord, `enabled` ayarlanmamışsa veya `"auto"` ise ve en az bir onaylayıcı çözümlenebiliyorsa yerel exec onaylarını otomatik etkinleştirir; bu çözümleme ya `execApprovals.approvers` üzerinden ya da `commands.ownerAllowFrom` üzerinden olabilir. Discord, kanal `allowFrom`, eski `dm.allowFrom` veya doğrudan mesaj `defaultTo` değerlerinden exec onaylayıcıları türetmez. Discord'u yerel onay istemcisi olarak açıkça devre dışı bırakmak için `enabled: false` ayarlayın.

    `target` değeri `channel` veya `both` olduğunda, onay istemi kanalda görünür. Yalnızca çözümlenmiş onaylayıcılar düğmeleri kullanabilir; diğer kullanıcılar geçici bir red yanıtı alır. Onay istemleri komut metnini içerir; bu nedenle kanal teslimatını yalnızca güvenilen kanallarda etkinleştirin. Kanal kimliği oturum anahtarından türetilemezse OpenClaw DM teslimatına fallback yapar.

    Discord ayrıca diğer sohbet kanallarının kullandığı paylaşılan onay düğmelerini de işler. Yerel Discord adaptörü esas olarak onaylayıcı DM yönlendirmesi ve kanal fanout ekler.
    Bu düğmeler mevcut olduğunda, bunlar birincil onay UX'idir; OpenClaw
    yalnızca araç sonucu sohbet onaylarının kullanılamadığını veya manuel
    onayın tek yol olduğunu söylüyorsa manuel bir `/approve` komutu içermelidir.

    Bu işleyici için Gateway kimlik doğrulaması, diğer Gateway istemcileriyle aynı paylaşılan kimlik bilgisi çözümleme sözleşmesini kullanır:

    - env öncelikli yerel kimlik doğrulama (`OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`, ardından `gateway.auth.*`)
    - yerel modda, `gateway.auth.*` ayarlanmamışsa `gateway.remote.*` yalnızca fallback olarak kullanılabilir; yapılandırılmış ancak çözümlenmemiş yerel SecretRef değerleri kapalı başarısız olur
    - uygun olduğunda `gateway.remote.*` üzerinden uzak mod desteği
    - URL geçersiz kılmaları güvenli geçersiz kılma mantığına sahiptir: CLI geçersiz kılmaları dolaylı kimlik bilgilerini yeniden kullanmaz ve env geçersiz kılmaları yalnızca env kimlik bilgilerini kullanır

    Onay çözümleme davranışı:

    - `plugin:` önekli kimlikler `plugin.approval.resolve` üzerinden çözülür.
    - Diğer kimlikler `exec.approval.resolve` üzerinden çözülür.
    - Discord burada ek bir exec-to-plugin fallback sıçraması yapmaz; hangi
      Gateway yönteminin çağrılacağını kimlik öneki belirler.

    Exec onaylarının süresi varsayılan olarak 30 dakika sonra dolar. Onaylar
    bilinmeyen onay kimlikleriyle başarısız olursa onaylayıcı çözümlemesini,
    özellik etkinliğini ve teslim edilen onay kimliği türünün bekleyen istekle
    eşleştiğini doğrulayın.

    İlgili belgeler: [Exec approvals](/tr/tools/exec-approvals)

  </Accordion>
</AccordionGroup>

## Araçlar ve işlem kapıları

Discord mesaj işlemleri mesajlaşma, kanal yönetimi, moderasyon, presence ve meta veri işlemlerini içerir.

Temel örnekler:

- mesajlaşma: `sendMessage`, `readMessages`, `editMessage`, `deleteMessage`, `threadReply`
- tepkiler: `react`, `reactions`, `emojiList`
- moderasyon: `timeout`, `kick`, `ban`
- presence: `setPresence`

İşlem kapıları `channels.discord.actions.*` altında bulunur.

Varsayılan kapı davranışı:

| İşlem grubu                                                                                                                                                              | Varsayılan |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------- |
| reactions, messages, threads, pins, polls, search, memberInfo, roleInfo, channelInfo, channels, voiceStatus, events, stickers, emojiUploads, stickerUploads, permissions | etkin      |
| roles                                                                                                                                                                    | devre dışı |
| moderation                                                                                                                                                               | devre dışı |
| presence                                                                                                                                                                 | devre dışı |

## Components v2 UI

OpenClaw, exec onayları ve bağlamlar arası işaretleyiciler için Discord components v2 kullanır. Discord mesaj işlemleri, özel UI için `components` de kabul edebilir (gelişmiş; discord aracı üzerinden bir bileşen yükü oluşturmayı gerektirir), ancak eski `embeds` hâlâ kullanılabilir olsa da önerilmez.

- `channels.discord.ui.components.accentColor`, Discord bileşen container'ları tarafından kullanılan vurgu rengini ayarlar (hex).
- Hesap başına ayarlamak için `channels.discord.accounts.<id>.ui.components.accentColor` kullanın.
- components v2 mevcut olduğunda `embeds` yok sayılır.

Örnek:

```json5
{
  channels: {
    discord: {
      ui: {
        components: {
          accentColor: "#5865F2",
        },
      },
    },
  },
}
```

## Ses kanalları

OpenClaw, gerçek zamanlı ve sürekli sohbetler için Discord ses kanallarına katılabilir. Bu, sesli mesaj eklerinden ayrıdır.

Gereksinimler:

- Yerel komutları etkinleştirin (`commands.native` veya `channels.discord.commands.native`).
- `channels.discord.voice` yapılandırın.
- Botun hedef ses kanalında Connect + Speak izinlerine ihtiyacı vardır.

Oturumları denetlemek için yalnızca Discord'a özgü `/vc join|leave|status` yerel komutunu kullanın. Komut, hesabın varsayılan ajanını kullanır ve diğer Discord komutlarıyla aynı izin listesi ve grup ilkesi kurallarını izler.

Otomatik katılma örneği:

```json5
{
  channels: {
    discord: {
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
    },
  },
}
```

Notlar:

- `voice.tts`, yalnızca ses oynatma için `messages.tts` değerini geçersiz kılar.
- Ses transkript turları, sahip durumunu Discord `allowFrom` (veya `dm.allowFrom`) üzerinden türetir; sahip olmayan konuşmacılar yalnızca sahip araçlarına erişemez (örneğin `gateway` ve `cron`).
- Ses varsayılan olarak etkindir; devre dışı bırakmak için `channels.discord.voice.enabled=false` ayarlayın.
- `voice.daveEncryption` ve `voice.decryptionFailureTolerance`, `@discordjs/voice` katılma seçeneklerine olduğu gibi geçirilir.
- Ayarlanmamışsa `@discordjs/voice` varsayılanları `daveEncryption=true` ve `decryptionFailureTolerance=24` olur.
- OpenClaw ayrıca alma şifre çözme başarısızlıklarını izler ve kısa bir pencerede tekrarlanan başarısızlıklardan sonra ses kanalından ayrılıp yeniden katılarak otomatik toparlanır.
- Alma günlüklerinde tekrar tekrar `DecryptionFailed(UnencryptedWhenPassthroughDisabled)` görünüyorsa, bu [discord.js #11419](https://github.com/discordjs/discord.js/issues/11419) içinde izlenen yukarı akış `@discordjs/voice` alma hatası olabilir.

## Sesli mesajlar

Discord sesli mesajları bir dalga formu önizlemesi gösterir ve OGG/Opus ses ile meta veri gerektirir. OpenClaw dalga formunu otomatik oluşturur, ancak ses dosyalarını incelemek ve dönüştürmek için gateway ana makinesinde `ffmpeg` ve `ffprobe` erişilebilir olmalıdır.

Gereksinimler ve kısıtlamalar:

- Bir **yerel dosya yolu** sağlayın (URL'ler reddedilir).
- Metin içeriğini atlayın (Discord, aynı yükte metin + sesli mesaja izin vermez).
- Herhangi bir ses biçimi kabul edilir; OpenClaw gerektiğinde bunu OGG/Opus'a dönüştürür.

Örnek:

```bash
message(action="send", channel="discord", target="channel:123", path="/path/to/audio.mp3", asVoice=true)
```

## Sorun giderme

<AccordionGroup>
  <Accordion title="İzin verilmeyen intent'ler kullanıldı veya bot sunucu mesajlarını görmüyor">

    - Message Content Intent'i etkinleştirin
    - kullanıcı/üye çözümlemesine dayanıyorsanız Server Members Intent'i etkinleştirin
    - intent'leri değiştirdikten sonra gateway'i yeniden başlatın

  </Accordion>

  <Accordion title="Sunucu mesajları beklenmedik şekilde engelleniyor">

    - `groupPolicy` değerini doğrulayın
    - `channels.discord.guilds` altındaki sunucu izin listesini doğrulayın
    - sunucu `channels` haritası varsa, yalnızca listelenen kanallara izin verilir
    - `requireMention` davranışını ve mention desenlerini doğrulayın

    Yararlı kontroller:

```bash
openclaw doctor
openclaw channels status --probe
openclaw logs --follow
```

  </Accordion>

  <Accordion title="Require mention false ama hâlâ engelleniyor">
    Yaygın nedenler:

    - eşleşen sunucu/kanal izin listesi olmadan `groupPolicy="allowlist"`
    - `requireMention` yanlış yerde yapılandırılmış (mutlaka `channels.discord.guilds` veya kanal girdisi altında olmalıdır)
    - gönderen sunucu/kanal `users` izin listesi tarafından engelleniyor

  </Accordion>

  <Accordion title="Uzun süren işleyiciler zaman aşımına uğruyor veya yinelenen yanıtlar üretiyor">

    Tipik günlükler:

    - `Listener DiscordMessageListener timed out after 30000ms for event MESSAGE_CREATE`
    - `Slow listener detected ...`
    - `discord inbound worker timed out after ...`

    Listener bütçe ayarı:

    - tek hesap: `channels.discord.eventQueue.listenerTimeout`
    - çoklu hesap: `channels.discord.accounts.<accountId>.eventQueue.listenerTimeout`

    Worker çalıştırma zaman aşımı ayarı:

    - tek hesap: `channels.discord.inboundWorker.runTimeoutMs`
    - çoklu hesap: `channels.discord.accounts.<accountId>.inboundWorker.runTimeoutMs`
    - varsayılan: `1800000` (30 dakika); devre dışı bırakmak için `0` ayarlayın

    Önerilen temel yapılandırma:

```json5
{
  channels: {
    discord: {
      accounts: {
        default: {
          eventQueue: {
            listenerTimeout: 120000,
          },
          inboundWorker: {
            runTimeoutMs: 1800000,
          },
        },
      },
    },
  },
}
```

    Yavaş listener kurulumu için `eventQueue.listenerTimeout`, kuyruklanan ajan turları için
    ayrı bir güvenlik vanası istiyorsanız ise yalnızca `inboundWorker.runTimeoutMs`
    kullanın.

  </Accordion>

  <Accordion title="İzin denetimi uyuşmazlıkları">
    `channels status --probe` izin kontrolleri yalnızca sayısal kanal kimlikleriyle çalışır.

    Slug anahtarları kullanırsanız çalışma zamanı eşleştirmesi yine de çalışabilir, ancak probe izinleri tam olarak doğrulayamaz.

  </Accordion>

  <Accordion title="DM ve eşleme sorunları">

    - DM devre dışı: `channels.discord.dm.enabled=false`
    - DM ilkesi devre dışı: `channels.discord.dmPolicy="disabled"` (eski: `channels.discord.dm.policy`)
    - `pairing` modunda eşleme onayı bekleniyor

  </Accordion>

  <Accordion title="Bottan bota döngüler">
    Varsayılan olarak bot tarafından yazılan mesajlar yok sayılır.

    `channels.discord.allowBots=true` ayarlarsanız döngü davranışını önlemek için katı mention ve izin listesi kuralları kullanın.
    Yalnızca bottan mention alan bot mesajlarını kabul etmek için `channels.discord.allowBots="mentions"` tercih edin.

  </Accordion>

  <Accordion title="Voice STT, DecryptionFailed(...) ile düşüyor">

    - Discord ses alma toparlama mantığının mevcut olduğundan emin olmak için OpenClaw'ı güncel tutun (`openclaw update`)
    - `channels.discord.voice.daveEncryption=true` (varsayılan) olduğunu doğrulayın
    - `channels.discord.voice.decryptionFailureTolerance=24` (upstream varsayılanı) ile başlayın ve yalnızca gerekirse ayarlayın
    - günlüklerde şunları izleyin:
      - `discord voice: DAVE decrypt failures detected`
      - `discord voice: repeated decrypt failures; attempting rejoin`
    - otomatik yeniden katılmadan sonra başarısızlıklar sürerse günlükleri toplayın ve [discord.js #11419](https://github.com/discordjs/discord.js/issues/11419) ile karşılaştırın

  </Accordion>
</AccordionGroup>

## Yapılandırma referansı işaretçileri

Birincil başvuru:

- [Configuration reference - Discord](/tr/gateway/configuration-reference#discord)

Yüksek sinyalli Discord alanları:

- başlangıç/kimlik doğrulama: `enabled`, `token`, `accounts.*`, `allowBots`
- ilke: `groupPolicy`, `dm.*`, `guilds.*`, `guilds.*.channels.*`
- komut: `commands.native`, `commands.useAccessGroups`, `configWrites`, `slashCommand.*`
- olay kuyruğu: `eventQueue.listenerTimeout` (listener bütçesi), `eventQueue.maxQueueSize`, `eventQueue.maxConcurrency`
- gelen worker: `inboundWorker.runTimeoutMs`
- yanıt/geçmiş: `replyToMode`, `historyLimit`, `dmHistoryLimit`, `dms.*.historyLimit`
- teslimat: `textChunkLimit`, `chunkMode`, `maxLinesPerMessage`
- akış: `streaming` (eski takma ad: `streamMode`), `draftChunk`, `blockStreaming`, `blockStreamingCoalesce`
- medya/yeniden deneme: `mediaMaxMb`, `retry`
  - `mediaMaxMb`, giden Discord yüklemelerini sınırlar (varsayılan: `100MB`)
- işlemler: `actions.*`
- presence: `activity`, `status`, `activityType`, `activityUrl`
- UI: `ui.components.accentColor`
- özellikler: `threadBindings`, üst düzey `bindings[]` (`type: "acp"`), `pluralkit`, `execApprovals`, `intents`, `agentComponents`, `heartbeat`, `responsePrefix`

## Güvenlik ve işlemler

- Bot token'larını sır olarak ele alın (denetlenen ortamlarda `DISCORD_BOT_TOKEN` tercih edilir).
- En az ayrıcalık veren Discord izinlerini verin.
- Komut dağıtımı/durumu bayatsa, gateway'i yeniden başlatın ve `openclaw channels status --probe` ile yeniden kontrol edin.

## İlgili

- [Eşleme](/tr/channels/pairing)
- [Gruplar](/tr/channels/groups)
- [Kanal yönlendirme](/tr/channels/channel-routing)
- [Güvenlik](/tr/gateway/security)
- [Çoklu ajan yönlendirme](/tr/concepts/multi-agent)
- [Sorun giderme](/tr/channels/troubleshooting)
- [Slash komutları](/tr/tools/slash-commands)
