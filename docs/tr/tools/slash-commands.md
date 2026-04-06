---
read_when:
    - Sohbet komutlarını kullanıyor veya yapılandırıyorsunuz
    - Komut yönlendirmesini veya izinleri hata ayıklıyorsunuz
summary: 'Slash komutları: metin ve yerel, yapılandırma ve desteklenen komutlar'
title: Slash Komutları
x-i18n:
    generated_at: "2026-04-06T03:14:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: 417e35b9ddd87f25f6c019111b55b741046ea11039dde89210948185ced5696d
    source_path: tools/slash-commands.md
    workflow: 15
---

# Slash komutları

Komutlar Gateway tarafından işlenir. Çoğu komut, `/` ile başlayan **bağımsız** bir mesaj olarak gönderilmelidir.
Yalnızca host üzerinde çalışan bash sohbet komutu `! <cmd>` kullanır (`/bash <cmd>` bir takma addır).

Birbiriyle ilişkili iki sistem vardır:

- **Komutlar**: bağımsız `/...` mesajları.
- **Yönergeler**: `/think`, `/fast`, `/verbose`, `/reasoning`, `/elevated`, `/exec`, `/model`, `/queue`.
  - Yönergeler, model mesajı görmeden önce ondan ayıklanır.
  - Normal sohbet mesajlarında (yalnızca yönergelerden oluşmayan), “satır içi ipuçları” olarak değerlendirilir ve oturum ayarlarını **kalıcı hale getirmez**.
  - Yalnızca yönerge içeren mesajlarda (mesaj yalnızca yönergeler içeriyorsa), oturuma kalıcı olarak kaydedilir ve bir onay yanıtı döndürür.
  - Yönergeler yalnızca **yetkili göndericilere** uygulanır. `commands.allowFrom` ayarlanmışsa, kullanılan tek
    izin listesi odur; aksi halde yetkilendirme channel izin listeleri/eşleştirme ile `commands.useAccessGroups` üzerinden gelir.
    Yetkisiz göndericiler, yönergelerin düz metin olarak ele alındığını görür.

Ayrıca birkaç **satır içi kısayol** da vardır (yalnızca izin listesinde/yetkili göndericiler için): `/help`, `/commands`, `/status`, `/whoami` (`/id`).
Bunlar hemen çalışır, model kalan metni görmeden önce ayıklanır ve kalan metin normal akıştan devam eder.

## Yapılandırma

```json5
{
  commands: {
    native: "auto",
    nativeSkills: "auto",
    text: true,
    bash: false,
    bashForegroundMs: 2000,
    config: false,
    mcp: false,
    plugins: false,
    debug: false,
    restart: false,
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    useAccessGroups: true,
  },
}
```

- `commands.text` (varsayılan `true`), sohbet mesajlarında `/...` ayrıştırmasını etkinleştirir.
  - Yerel komutları olmayan yüzeylerde (WhatsApp/WebChat/Signal/iMessage/Google Chat/Microsoft Teams), bunu `false` yapsanız bile metin komutları çalışmaya devam eder.
- `commands.native` (varsayılan `"auto"`), yerel komutları kaydeder.
  - Otomatik: Discord/Telegram için açık; Slack için kapalıdır (slash komutlarını ekleyene kadar); yerel desteği olmayan sağlayıcılarda yok sayılır.
  - Sağlayıcı bazında geçersiz kılmak için `channels.discord.commands.native`, `channels.telegram.commands.native` veya `channels.slack.commands.native` ayarlayın (bool veya `"auto"`).
  - `false`, başlangıçta Discord/Telegram üzerinde daha önce kaydedilmiş komutları temizler. Slack komutları Slack uygulamasında yönetilir ve otomatik olarak kaldırılmaz.
- `commands.nativeSkills` (varsayılan `"auto"`), desteklendiğinde **skill** komutlarını yerel olarak kaydeder.
  - Otomatik: Discord/Telegram için açık; Slack için kapalıdır (Slack, skill başına bir slash komutu oluşturmayı gerektirir).
  - Sağlayıcı bazında geçersiz kılmak için `channels.discord.commands.nativeSkills`, `channels.telegram.commands.nativeSkills` veya `channels.slack.commands.nativeSkills` ayarlayın (bool veya `"auto"`).
- `commands.bash` (varsayılan `false`), `! <cmd>` ile host shell komutlarının çalıştırılmasını etkinleştirir (`/bash <cmd>` bir takma addır; `tools.elevated` izin listeleri gerekir).
- `commands.bashForegroundMs` (varsayılan `2000`), bash’in arka plan kipine geçmeden önce ne kadar bekleyeceğini denetler (`0`, hemen arka plana atar).
- `commands.config` (varsayılan `false`), `/config` komutunu etkinleştirir (`openclaw.json` okur/yazar).
- `commands.mcp` (varsayılan `false`), `/mcp` komutunu etkinleştirir (`mcp.servers` altındaki OpenClaw tarafından yönetilen MCP config’ini okur/yazar).
- `commands.plugins` (varsayılan `false`), `/plugins` komutunu etkinleştirir (plugin keşfi/durumu artı kurulum + etkinleştirme/devre dışı bırakma denetimleri).
- `commands.debug` (varsayılan `false`), `/debug` komutunu etkinleştirir (yalnızca çalışma zamanı geçersiz kılmaları).
- `commands.allowFrom` (isteğe bağlı), komut yetkilendirmesi için sağlayıcı başına bir izin listesi ayarlar. Yapılandırıldığında, komutlar ve yönergeler için
  tek yetkilendirme kaynağı bu olur (channel izin listeleri/eşleştirme ve `commands.useAccessGroups`
  yok sayılır). Global varsayılan için `"*"` kullanın; sağlayıcıya özgü anahtarlar bunu geçersiz kılar.
- `commands.useAccessGroups` (varsayılan `true`), `commands.allowFrom` ayarlanmamışsa komutlar için izin listelerini/ilkeleri uygular.

## Komut listesi

Metin + yerel (etkinleştirildiğinde):

- `/help`
- `/commands`
- `/tools [compact|verbose]` (geçerli agent’ın şu anda ne kullanabildiğini gösterir; `verbose` açıklamaları ekler)
- `/skill <name> [input]` (bir skill’i adına göre çalıştır)
- `/status` (geçerli durumu gösterir; mevcut model provider için kullanılabiliyorsa provider kullanım/kota bilgilerini içerir)
- `/tasks` (geçerli oturum için arka plan görevlerini listeler; agent-local geri dönüş sayılarıyla etkin ve son görev ayrıntılarını gösterir)
- `/allowlist` (izin listesi girdilerini listele/ekle/kaldır)
- `/approve <id> <decision>` (exec onay istemlerini çözümler; kullanılabilir kararlar için bekleyen onay mesajını kullanın)
- `/context [list|detail|json]` (“bağlam”ı açıklar; `detail`, dosya başına + araç başına + skill başına + sistem komutu boyutunu gösterir)
- `/btw <question>` (gelecekteki oturum bağlamını değiştirmeden geçerli oturum hakkında geçici bir yan soru sorar; bkz. [/tools/btw](/tr/tools/btw))
- `/export-session [path]` (takma ad: `/export`) (geçerli oturumu tam sistem komutuyla birlikte HTML olarak dışa aktarır)
- `/whoami` (gönderici kimliğinizi gösterir; takma adı: `/id`)
- `/session idle <duration|off>` (odaklanmış thread bağları için etkinliksizlik kaynaklı otomatik odak kaldırmayı yönetir)
- `/session max-age <duration|off>` (odaklanmış thread bağları için kesin max-age kaynaklı otomatik odak kaldırmayı yönetir)
- `/subagents list|kill|log|info|send|steer|spawn` (geçerli oturum için alt agent çalıştırmalarını incele, denetle veya başlat)
- `/acp spawn|cancel|steer|close|status|set-mode|set|cwd|permissions|timeout|model|reset-options|doctor|install|sessions` (ACP çalışma zamanı oturumlarını incele ve denetle)
- `/agents` (bu oturum için thread’e bağlı agent’ları listeler)
- `/focus <target>` (Discord: bu thread’i veya yeni bir thread’i bir oturum/alt agent hedefine bağla)
- `/unfocus` (Discord: geçerli thread bağını kaldır)
- `/kill <id|#|all>` (bu oturum için çalışan bir veya tüm alt agent’ları hemen durdurur; onay mesajı yoktur)
- `/steer <id|#> <message>` (çalışan bir alt agent’ı hemen yönlendirir: mümkünse çalışma içinde, aksi halde mevcut işi durdurup yönlendirme mesajıyla yeniden başlatır)
- `/tell <id|#> <message>` (`/steer` için takma ad)
- `/config show|get|set|unset` (config’i diske kalıcı yazar, yalnızca sahip; `commands.config: true` gerektirir)
- `/mcp show|get|set|unset` (OpenClaw MCP sunucu config’ini yönetir, yalnızca sahip; `commands.mcp: true` gerektirir)
- `/plugins list|show|get|install|enable|disable` (keşfedilen plugin’leri incele, yenilerini kur ve etkinliği değiştir; yazma işlemleri yalnızca sahip içindir; `commands.plugins: true` gerektirir)
  - `/plugin`, `/plugins` için bir takma addır.
  - `/plugin install <spec>`, `openclaw plugins install` ile aynı plugin spec’lerini kabul eder: yerel yol/arşiv, npm paketi veya `clawhub:<pkg>`.
  - Etkinleştirme/devre dışı bırakma yazmaları yine de bir yeniden başlatma ipucuyla yanıt verir. Ön planda izlenen bir gateway’de OpenClaw bu yeniden başlatmayı yazımdan hemen sonra otomatik gerçekleştirebilir.
- `/debug show|set|unset|reset` (yalnızca çalışma zamanı geçersiz kılmaları, yalnızca sahip; `commands.debug: true` gerektirir)
- `/usage off|tokens|full|cost` (yanıt başına kullanım altbilgisi veya yerel maliyet özeti)
- `/tts off|always|inbound|tagged|status|provider|limit|summary|audio` (TTS denetimi; bkz. [/tts](/tr/tools/tts))
  - Discord: yerel komut `/voice`’dur (Discord `/tts` komutunu ayırır); metin `/tts` yine de çalışır.
- `/stop`
- `/restart`
- `/dock-telegram` (takma ad: `/dock_telegram`) (yanıtları Telegram’a geçir)
- `/dock-discord` (takma ad: `/dock_discord`) (yanıtları Discord’a geçir)
- `/dock-slack` (takma ad: `/dock_slack`) (yanıtları Slack’e geçir)
- `/activation mention|always` (yalnızca gruplar)
- `/send on|off|inherit` (yalnızca sahip)
- `/reset` veya `/new [model]` (isteğe bağlı model ipucu; kalan metin aynen iletilir)
- `/think <off|minimal|low|medium|high|xhigh>` (modele/sağlayıcıya göre dinamik seçenekler; takma adlar: `/thinking`, `/t`)
- `/fast status|on|off` (argümanı atlamak, geçerli etkin fast-mode durumunu gösterir)
- `/verbose on|full|off` (takma adı: `/v`)
- `/reasoning on|off|stream` (takma adı: `/reason`; açıkken `Reasoning:` önekli ayrı bir mesaj gönderir; `stream` = yalnızca Telegram taslağı)
- `/elevated on|off|ask|full` (takma adı: `/elev`; `full`, exec onaylarını atlar)
- `/exec host=<auto|sandbox|gateway|node> security=<deny|allowlist|full> ask=<off|on-miss|always> node=<id>` (geçerli durumu görmek için `/exec` gönderin)
- `/model <name>` (takma adı: `/models`; veya `agents.defaults.models.*.alias` içindeki `/<alias>`)
- `/queue <mode>` (artı `debounce:2s cap:25 drop:summarize` gibi seçenekler; mevcut ayarları görmek için `/queue` gönderin)
- `/bash <command>` (yalnızca host; `! <command>` için takma ad; `commands.bash: true` + `tools.elevated` izin listeleri gerekir)
- `/dreaming [on|off|status|help]` (global dreaming’i aç/kapat veya durumu göster; bkz. [Dreaming](/concepts/dreaming))

Yalnızca metin:

- `/compact [instructions]` (bkz. [/concepts/compaction](/tr/concepts/compaction))
- `! <command>` (yalnızca host; aynı anda bir tane; uzun işler için `!poll` + `!stop` kullanın)
- `!poll` (çıktıyı / durumu kontrol eder; isteğe bağlı `sessionId` kabul eder; `/bash poll` da çalışır)
- `!stop` (çalışan bash işini durdurur; isteğe bağlı `sessionId` kabul eder; `/bash stop` da çalışır)

Notlar:

- Komutlar, komut ile argümanlar arasında isteğe bağlı `:` kabul eder (ör. `/think: high`, `/send: on`, `/help:`).
- `/new <model>`, bir model takma adı, `provider/model` veya sağlayıcı adı (bulanık eşleşme) kabul eder; eşleşme yoksa metin mesaj gövdesi olarak ele alınır.
- Tam provider kullanım dökümü için `openclaw status --usage` kullanın.
- `/allowlist add|remove`, `commands.config=true` gerektirir ve channel `configWrites` ayarını dikkate alır.
- Çok hesaplı channels içinde, hedef hesap için kullanılan `/allowlist --account <id>` ve `/config set channels.<provider>.accounts.<id>...` da hedef hesabın `configWrites` ayarını dikkate alır.
- `/usage`, yanıt başına kullanım altbilgisini denetler; `/usage cost`, OpenClaw oturum günlüklerinden yerel bir maliyet özeti yazdırır.
- `/restart` varsayılan olarak etkindir; devre dışı bırakmak için `commands.restart: false` ayarlayın.
- Yalnızca Discord yerel komutu: `/vc join|leave|status`, ses kanallarını denetler (`channels.discord.voice` ve yerel komutlar gerekir; metin olarak yoktur).
- Discord thread-binding komutları (`/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age`), etkin thread bağlarının etkin olmasını gerektirir (`session.threadBindings.enabled` ve/veya `channels.discord.threadBindings.enabled`).
- ACP komut başvurusu ve çalışma zamanı davranışı: [ACP Agents](/tr/tools/acp-agents).
- `/verbose`, hata ayıklama ve ek görünürlük içindir; normal kullanımda **kapalı** tutun.
- `/fast on|off`, oturum geçersiz kılmasını kalıcı hale getirir. Bunu temizleyip config varsayılanlarına dönmek için Sessions UI içindeki `inherit` seçeneğini kullanın.
- `/fast`, sağlayıcıya özgüdür: OpenAI/OpenAI Codex bunu yerel Responses endpoint’lerinde `service_tier=priority` olarak eşlerken, `api.anthropic.com` adresine gönderilen OAuth ile kimlik doğrulanmış trafik dahil doğrudan herkese açık Anthropic istekleri bunu `service_tier=auto` veya `standard_only` olarak eşler. Bkz. [OpenAI](/tr/providers/openai) ve [Anthropic](/tr/providers/anthropic).
- Araç hata özetleri ilgili olduğunda yine gösterilir, ancak ayrıntılı hata metni yalnızca `/verbose` `on` veya `full` iken eklenir.
- `/reasoning` (ve `/verbose`) grup ortamlarında risklidir: açığa çıkarmayı düşünmediğiniz iç reasoning’i veya araç çıktısını ifşa edebilir. Özellikle grup sohbetlerinde bunları kapalı bırakmayı tercih edin.
- `/model`, yeni oturum modelini hemen kalıcı hale getirir.
- Agent boşta ise bir sonraki çalıştırma bunu hemen kullanır.
- Bir çalıştırma zaten etkinse OpenClaw canlı geçişi beklemede olarak işaretler ve yalnızca temiz bir yeniden deneme noktasında yeni modele yeniden başlar.
- Araç etkinliği veya yanıt çıktısı zaten başladıysa, bekleyen geçiş daha sonraki bir yeniden deneme fırsatına ya da sonraki kullanıcı turuna kadar kuyrukta kalabilir.
- **Hızlı yol:** izin listesindeki göndericilerden gelen yalnızca komut içeren mesajlar hemen işlenir (kuyruk + model atlanır).
- **Grup mention kapılaması:** izin listesindeki göndericilerden gelen yalnızca komut içeren mesajlar mention gereksinimlerini atlar.
- **Satır içi kısayollar (yalnızca izin listesindeki göndericiler):** bazı komutlar normal bir mesajın içine gömülü olduğunda da çalışır ve model kalan metni görmeden önce ayıklanır.
  - Örnek: `hey /status`, bir durum yanıtı tetikler ve kalan metin normal akıştan devam eder.
- Şu anda: `/help`, `/commands`, `/status`, `/whoami` (`/id`).
- Yetkisiz yalnızca komut mesajları sessizce yok sayılır ve satır içi `/...` belirteçleri düz metin olarak değerlendirilir.
- **Skill komutları:** `user-invocable` skill’ler slash komutları olarak sunulur. Adlar `a-z0-9_` olacak şekilde temizlenir (en fazla 32 karakter); çakışmalar sayısal son ekler alır (ör. `_2`).
  - `/skill <name> [input]`, bir skill’i adına göre çalıştırır (yerel komut sınırları skill başına komutları engellediğinde yararlıdır).
  - Varsayılan olarak skill komutları modele normal istek olarak iletilir.
  - Skill’ler isteğe bağlı olarak komutu doğrudan bir araca yönlendirmek için `command-dispatch: tool` bildirebilir (deterministik, modelsiz).
  - Örnek: `/prose` (OpenProse plugin’i) — bkz. [OpenProse](/tr/prose).
- **Yerel komut argümanları:** Discord, dinamik seçenekler için autocomplete kullanır (ve gerekli argümanları atlarsanız düğme menüleri gösterir). Telegram ve Slack, komut seçenekleri destekliyorsa ve argümanı atlarsanız bir düğme menüsü gösterir.

## `/tools`

`/tools`, bir config sorusunu değil, çalışma zamanı sorusunu yanıtlar: **bu agent’ın şu anda
bu konuşmada ne kullanabildiğini**.

- Varsayılan `/tools` kompakttır ve hızlı tarama için optimize edilmiştir.
- `/tools verbose`, kısa açıklamalar ekler.
- Argümanları destekleyen yerel komut yüzeyleri, aynı `compact|verbose` kip değiştiricisini sunar.
- Sonuçlar oturum kapsamındadır; bu nedenle agent, channel, thread, gönderici yetkilendirmesi veya model değişirse çıktı da değişebilir.
- `/tools`, çalışma zamanında gerçekten erişilebilir araçları içerir; buna core araçları, bağlı plugin araçları ve channel’a ait araçlar dahildir.

Profil ve geçersiz kılma düzenlemeleri için, `/tools`’u statik katalog gibi görmek yerine Control UI Tools panelini veya config/katalog yüzeylerini kullanın.

## Kullanım yüzeyleri (nerede ne gösterilir)

- **Provider kullanım/kota** (örnek: “Claude %80 kaldı”), kullanım izleme etkin olduğunda `/status` içinde mevcut model provider için görünür. OpenClaw provider pencerelerini `% kaldı` olarak normalize eder; MiniMax için yalnızca kalan yüzde alanları gösterimden önce tersine çevrilir ve `model_remains` yanıtları model etiketi taşıyan plan etiketine ek olarak chat-model girdisini tercih eder.
- `/status` içindeki **Token/cache satırları**, canlı oturum snapshot’ı seyrek olduğunda en son transcript kullanım girdisine geri dönebilir. Mevcut sıfır olmayan canlı değerler yine de kazanır ve transcript geri dönüşü ayrıca etkin çalışma zamanı model etiketini ve depolanmış toplamlar eksik veya daha küçük olduğunda prompt odaklı daha büyük bir toplamı da geri getirebilir.
- **Yanıt başına token/maliyet**, `/usage off|tokens|full` ile denetlenir (normal yanıtlara eklenir).
- `/model status`, kullanımla değil, **modeller/auth/endpoint’lerle** ilgilidir.

## Model seçimi (`/model`)

`/model`, bir yönerge olarak uygulanır.

Örnekler:

```
/model
/model list
/model 3
/model openai/gpt-5.4
/model opus@anthropic:default
/model status
```

Notlar:

- `/model` ve `/model list`, kompakt, numaralandırılmış bir seçici gösterir (model ailesi + kullanılabilir sağlayıcılar).
- Discord üzerinde `/model` ve `/models`, sağlayıcı ve model açılır listeleri artı bir Submit adımı içeren etkileşimli bir seçici açar.
- `/model <#>`, bu seçiciden seçim yapar (ve mümkün olduğunda geçerli sağlayıcıyı tercih eder).
- `/model status`, kullanılabildiğinde yapılandırılmış sağlayıcı endpoint’i (`baseUrl`) ve API kipini (`api`) de içeren ayrıntılı görünümü gösterir.

## Debug geçersiz kılmaları

`/debug`, **yalnızca çalışma zamanı** config geçersiz kılmaları ayarlamanıza olanak tanır (disk değil, bellek). Yalnızca sahip içindir. Varsayılan olarak devre dışıdır; etkinleştirmek için `commands.debug: true` kullanın.

Örnekler:

```
/debug show
/debug set messages.responsePrefix="[openclaw]"
/debug set channels.whatsapp.allowFrom=["+1555","+4477"]
/debug unset messages.responsePrefix
/debug reset
```

Notlar:

- Geçersiz kılmalar yeni config okumalarına hemen uygulanır, ancak `openclaw.json` dosyasına yazılmaz.
- Tüm geçersiz kılmaları temizlemek ve disk üzerindeki config’e dönmek için `/debug reset` kullanın.

## Config güncellemeleri

`/config`, disk üzerindeki config’inize (`openclaw.json`) yazar. Yalnızca sahip içindir. Varsayılan olarak devre dışıdır; etkinleştirmek için `commands.config: true` kullanın.

Örnekler:

```
/config show
/config show messages.responsePrefix
/config get messages.responsePrefix
/config set messages.responsePrefix="[openclaw]"
/config unset messages.responsePrefix
```

Notlar:

- Yazmadan önce config doğrulanır; geçersiz değişiklikler reddedilir.
- `/config` güncellemeleri yeniden başlatmalar arasında kalıcıdır.

## MCP güncellemeleri

`/mcp`, `mcp.servers` altındaki OpenClaw tarafından yönetilen MCP sunucu tanımlarını yazar. Yalnızca sahip içindir. Varsayılan olarak devre dışıdır; etkinleştirmek için `commands.mcp: true` kullanın.

Örnekler:

```text
/mcp show
/mcp show context7
/mcp set context7={"command":"uvx","args":["context7-mcp"]}
/mcp unset context7
```

Notlar:

- `/mcp`, config’i Pi’ye ait proje ayarlarında değil OpenClaw config’inde saklar.
- Hangi transport’ların gerçekten yürütülebilir olduğuna çalışma zamanı bağdaştırıcıları karar verir.

## Plugin güncellemeleri

`/plugins`, operatörlerin keşfedilen plugin’leri incelemesine ve config içindeki etkinliği değiştirmesine olanak tanır. Salt okunur akışlar takma ad olarak `/plugin` kullanabilir. Varsayılan olarak devre dışıdır; etkinleştirmek için `commands.plugins: true` kullanın.

Örnekler:

```text
/plugins
/plugins list
/plugin show context7
/plugins enable context7
/plugins disable context7
```

Notlar:

- `/plugins list` ve `/plugins show`, mevcut çalışma alanı ve disk üzerindeki config’e karşı gerçek plugin keşfini kullanır.
- `/plugins enable|disable`, yalnızca plugin config’ini günceller; plugin kurmaz veya kaldırmaz.
- Etkinleştirme/devre dışı bırakma değişikliklerinden sonra bunları uygulamak için gateway’i yeniden başlatın.

## Yüzey notları

- **Metin komutları**, normal sohbet oturumunda çalışır (DM’ler `main`’i paylaşır, grupların kendi oturumu vardır).
- **Yerel komutlar**, izole oturumlar kullanır:
  - Discord: `agent:<agentId>:discord:slash:<userId>`
  - Slack: `agent:<agentId>:slack:slash:<userId>` (önek `channels.slack.slashCommand.sessionPrefix` ile yapılandırılabilir)
  - Telegram: `telegram:slash:<userId>` (oturum hedefi `CommandTargetSessionKey` üzerinden sohbet oturumunu hedefler)
- **`/stop`**, geçerli çalıştırmayı durdurabilmesi için etkin sohbet oturumunu hedefler.
- **Slack:** `channels.slack.slashCommand`, tek bir `/openclaw` tarzı komut için hâlâ desteklenir. `commands.native` etkinleştirirseniz, her yerleşik komut için bir Slack slash komutu oluşturmanız gerekir (`/help` ile aynı adlar). Slack için komut argüman menüleri geçici Block Kit düğmeleri olarak iletilir.
  - Slack yerel istisnası: Slack `/status` komutunu ayırdığı için `/status` değil `/agentstatus` kaydedin. Metin `/status`, Slack mesajlarında yine de çalışır.

## BTW yan soruları

`/btw`, mevcut oturum hakkında hızlı bir **yan soru**dur.

Normal sohbetten farklı olarak:

- mevcut oturumu arka plan bağlamı olarak kullanır,
- ayrı, **araçsız** tek seferlik bir çağrı olarak çalışır,
- gelecekteki oturum bağlamını değiştirmez,
- transcript geçmişine yazılmaz,
- normal bir asistan mesajı yerine canlı bir yan sonuç olarak iletilir.

Bu, ana görev devam ederken geçici bir netleştirme istediğinizde `/btw` komutunu yararlı kılar.

Örnek:

```text
/btw şu anda ne yapıyoruz?
```

Tam davranış ve istemci UX ayrıntıları için bkz. [BTW Side Questions](/tr/tools/btw).
