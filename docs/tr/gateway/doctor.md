---
read_when:
    - Doctor geçişleri eklerken veya değiştirirken
    - Geriye dönük uyumsuz yapılandırma değişiklikleri eklerken
summary: 'Doctor komutu: sağlık kontrolleri, yapılandırma geçişleri ve onarım adımları'
title: Doctor
x-i18n:
    generated_at: "2026-04-08T02:15:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3761a222d9db7088f78215575fa84e5896794ad701aa716e8bf9039a4424dca6
    source_path: gateway/doctor.md
    workflow: 15
---

# Doctor

`openclaw doctor`, OpenClaw için onarım + geçiş aracıdır. Eski yapılandırma/durumu düzeltir, sağlığı kontrol eder ve uygulanabilir onarım adımları sağlar.

## Hızlı başlangıç

```bash
openclaw doctor
```

### Başsız / otomasyon

```bash
openclaw doctor --yes
```

İstem göstermeden varsayılanları kabul eder (uygulanabildiğinde yeniden başlatma/hizmet/sandbox onarım adımları dahil).

```bash
openclaw doctor --repair
```

Önerilen onarımları istem göstermeden uygular (güvenli olduğunda onarımlar + yeniden başlatmalar).

```bash
openclaw doctor --repair --force
```

Agresif onarımları da uygular (özel supervisor yapılandırmalarının üzerine yazar).

```bash
openclaw doctor --non-interactive
```

İstem göstermeden çalışır ve yalnızca güvenli geçişleri uygular (yapılandırma normalleştirme + disk üzerindeki durum taşımaları). İnsan onayı gerektiren yeniden başlatma/hizmet/sandbox eylemlerini atlar.
Eski durum geçişleri algılandığında otomatik olarak çalıştırılır.

```bash
openclaw doctor --deep
```

Ek gateway kurulumları için sistem hizmetlerini tarar (launchd/systemd/schtasks).

Yazmadan önce değişiklikleri incelemek istiyorsanız, önce yapılandırma dosyasını açın:

```bash
cat ~/.openclaw/openclaw.json
```

## Ne yapar (özet)

- Git kurulumları için isteğe bağlı uçuş öncesi güncelleme (yalnızca etkileşimli).
- UI protokol güncellik denetimi (protokol şeması daha yeniyse Control UI yeniden oluşturulur).
- Sağlık denetimi + yeniden başlatma istemi.
- Skills durum özeti (uygun/eksik/engellenmiş) ve plugin durumu.
- Eski değerler için yapılandırma normalleştirme.
- Eski düz `talk.*` alanlarından `talk.provider` + `talk.providers.<provider>` yapısına Talk yapılandırması geçişi.
- Eski Chrome uzantısı yapılandırmaları ve Chrome MCP hazırlığı için tarayıcı geçiş kontrolleri.
- OpenCode sağlayıcı geçersiz kılma uyarıları (`models.providers.opencode` / `models.providers.opencode-go`).
- Codex OAuth gölgeleme uyarıları (`models.providers.openai-codex`).
- OpenAI Codex OAuth profilleri için OAuth TLS önkoşul kontrolü.
- Eski disk üstü durum geçişi (oturumlar/agent dizini/WhatsApp kimlik doğrulaması).
- Eski plugin manifest sözleşme anahtarı geçişi (`speechProviders`, `realtimeTranscriptionProviders`, `realtimeVoiceProviders`, `mediaUnderstandingProviders`, `imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`, `webSearchProviders` → `contracts`).
- Eski cron deposu geçişi (`jobId`, `schedule.cron`, üst düzey delivery/payload alanları, payload `provider`, basit `notify: true` webhook yedek işleri).
- Oturum kilit dosyası incelemesi ve eski kilit temizliği.
- Durum bütünlüğü ve izin kontrolleri (oturumlar, transcript'ler, durum dizini).
- Yerel çalışırken yapılandırma dosyası izin kontrolleri (chmod 600).
- Model kimlik doğrulama sağlığı: OAuth süresinin dolmasını kontrol eder, süresi dolmak üzere olan belirteçleri yenileyebilir ve auth-profile cooldown/devre dışı durumlarını bildirir.
- Ek çalışma alanı dizini algılama (`~/openclaw`).
- Sandbox etkinleştirildiğinde sandbox image onarımı.
- Eski hizmet geçişi ve ek gateway algılama.
- Matrix kanalında eski durum geçişi (`--fix` / `--repair` kipinde).
- Gateway çalışma zamanı kontrolleri (hizmet kurulu ama çalışmıyor; önbelleğe alınmış launchd etiketi).
- Kanal durumu uyarıları (çalışan gateway üzerinden yoklanır).
- Supervisor yapılandırma denetimi (launchd/systemd/schtasks) ve isteğe bağlı onarım.
- Gateway çalışma zamanı en iyi uygulama kontrolleri (Node ve Bun, sürüm yöneticisi yolları).
- Gateway port çakışması tanılaması (varsayılan `18789`).
- Açık DM ilkeleri için güvenlik uyarıları.
- Yerel token kipi için gateway auth kontrolleri (token kaynağı yoksa token oluşturmayı önerir; token SecretRef yapılandırmalarının üzerine yazmaz).
- Linux'ta systemd linger kontrolü.
- Çalışma alanı bootstrap dosya boyutu kontrolü (kesilme/sınıra yakın uyarıları bağlam dosyaları için).
- Shell completion durumu kontrolü ve otomatik kurulum/yükseltme.
- Bellek araması embedding sağlayıcı hazırlık kontrolü (yerel model, uzak API anahtarı veya QMD ikilisi).
- Kaynak kurulum kontrolleri (pnpm çalışma alanı uyuşmazlığı, eksik UI varlıkları, eksik tsx ikilisi).
- Güncellenmiş yapılandırma + wizard metadata yazar.

## Ayrıntılı davranış ve gerekçe

### 0) İsteğe bağlı güncelleme (git kurulumları)

Bu bir git checkout ise ve doctor etkileşimli olarak çalışıyorsa, doctor çalıştırmadan önce güncelleme (fetch/rebase/build) önerir.

### 1) Yapılandırma normalleştirme

Yapılandırma eski değer biçimleri içeriyorsa (örneğin kanal bazlı bir geçersiz kılma olmadan `messages.ackReaction`), doctor bunları mevcut şemaya normalleştirir.

Buna eski Talk düz alanları da dahildir. Mevcut genel Talk yapılandırması
`talk.provider` + `talk.providers.<provider>` biçimindedir. Doctor, eski
`talk.voiceId` / `talk.voiceAliases` / `talk.modelId` / `talk.outputFormat` /
`talk.apiKey` biçimlerini sağlayıcı eşlemesine yeniden yazar.

### 2) Eski yapılandırma anahtarı geçişleri

Yapılandırma kullanımdan kaldırılmış anahtarlar içerdiğinde, diğer komutlar çalışmayı reddeder ve sizden `openclaw doctor` çalıştırmanızı ister.

Doctor şunları yapar:

- Hangi eski anahtarların bulunduğunu açıklar.
- Uyguladığı geçişi gösterir.
- `~/.openclaw/openclaw.json` dosyasını güncellenmiş şemayla yeniden yazar.

Gateway de eski bir yapılandırma biçimi algıladığında başlangıçta doctor geçişlerini otomatik çalıştırır, böylece eski yapılandırmalar el ile müdahale olmadan onarılır.
Cron iş deposu geçişleri `openclaw doctor --fix` tarafından ele alınır.

Geçerli geçişler:

- `routing.allowFrom` → `channels.whatsapp.allowFrom`
- `routing.groupChat.requireMention` → `channels.whatsapp/telegram/imessage.groups."*".requireMention`
- `routing.groupChat.historyLimit` → `messages.groupChat.historyLimit`
- `routing.groupChat.mentionPatterns` → `messages.groupChat.mentionPatterns`
- `routing.queue` → `messages.queue`
- `routing.bindings` → üst düzey `bindings`
- `routing.agents`/`routing.defaultAgentId` → `agents.list` + `agents.list[].default`
- eski `talk.voiceId`/`talk.voiceAliases`/`talk.modelId`/`talk.outputFormat`/`talk.apiKey` → `talk.provider` + `talk.providers.<provider>`
- `routing.agentToAgent` → `tools.agentToAgent`
- `routing.transcribeAudio` → `tools.media.audio.models`
- `messages.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `messages.tts.providers.<provider>`
- `channels.discord.voice.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `channels.discord.voice.tts.providers.<provider>`
- `channels.discord.accounts.<id>.voice.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `channels.discord.accounts.<id>.voice.tts.providers.<provider>`
- `plugins.entries.voice-call.config.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `plugins.entries.voice-call.config.tts.providers.<provider>`
- `plugins.entries.voice-call.config.provider: "log"` → `"mock"`
- `plugins.entries.voice-call.config.twilio.from` → `plugins.entries.voice-call.config.fromNumber`
- `plugins.entries.voice-call.config.streaming.sttProvider` → `plugins.entries.voice-call.config.streaming.provider`
- `plugins.entries.voice-call.config.streaming.openaiApiKey|sttModel|silenceDurationMs|vadThreshold`
  → `plugins.entries.voice-call.config.streaming.providers.openai.*`
- `bindings[].match.accountID` → `bindings[].match.accountId`
- Adlandırılmış `accounts` içeren ancak tek hesaplı üst düzey kanal değerleri kalmaya devam eden kanallarda, bu hesap kapsamlı değerleri o kanal için seçilen yükseltilmiş hesaba taşı (`accounts.default` çoğu kanal için; Matrix mevcut eşleşen adlandırılmış/varsayılan hedefi koruyabilir)
- `identity` → `agents.list[].identity`
- `agent.*` → `agents.defaults` + `tools.*` (tools/elevated/exec/sandbox/subagents)
- `agent.model`/`allowedModels`/`modelAliases`/`modelFallbacks`/`imageModelFallbacks`
  → `agents.defaults.models` + `agents.defaults.model.primary/fallbacks` + `agents.defaults.imageModel.primary/fallbacks`
- `browser.ssrfPolicy.allowPrivateNetwork` → `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork`
- `browser.profiles.*.driver: "extension"` → `"existing-session"`
- `browser.relayBindHost` kaldırılır (eski uzantı relay ayarı)

Doctor uyarıları ayrıca çok hesaplı kanallar için varsayılan hesap yönlendirmesini de içerir:

- `channels.<channel>.accounts` içinde iki veya daha fazla kayıt yapılandırılmışsa, ancak `channels.<channel>.defaultAccount` veya `accounts.default` yoksa, doctor yedek yönlendirmenin beklenmeyen bir hesap seçebileceği konusunda uyarır.
- `channels.<channel>.defaultAccount` bilinmeyen bir hesap kimliğine ayarlanmışsa, doctor uyarır ve yapılandırılmış hesap kimliklerini listeler.

### 2b) OpenCode sağlayıcı geçersiz kılmaları

`models.providers.opencode`, `opencode-zen` veya `opencode-go` öğelerini elle eklediyseniz, bu işlem `@mariozechner/pi-ai` içindeki yerleşik OpenCode kataloğunu geçersiz kılar.
Bu durum modelleri yanlış API'ye zorlayabilir veya maliyetleri sıfırlayabilir. Doctor, geçersiz kılmayı kaldırıp model başına API yönlendirmesi + maliyetleri geri yükleyebilmeniz için uyarı verir.

### 2c) Tarayıcı geçişi ve Chrome MCP hazırlığı

Tarayıcı yapılandırmanız hâlâ kaldırılmış Chrome uzantısı yolunu gösteriyorsa, doctor bunu mevcut host-local Chrome MCP bağlanma modeline normalleştirir:

- `browser.profiles.*.driver: "extension"` değeri `"existing-session"` olur
- `browser.relayBindHost` kaldırılır

Doctor ayrıca `defaultProfile:
"user"` veya yapılandırılmış bir `existing-session` profili kullandığınızda host-local Chrome MCP yolunu denetler:

- varsayılan otomatik bağlanma profilleri için Google Chrome'un aynı host üzerinde kurulu olup olmadığını kontrol eder
- algılanan Chrome sürümünü kontrol eder ve Chrome 144'ün altında ise uyarır
- tarayıcı inspect sayfasında remote debugging'i etkinleştirmenizi hatırlatır (örneğin `chrome://inspect/#remote-debugging`, `brave://inspect/#remote-debugging`,
  veya `edge://inspect/#remote-debugging`)

Doctor, Chrome tarafındaki ayarı sizin için etkinleştiremez. Host-local Chrome MCP için yine de şunlar gerekir:

- gateway/node host üzerinde 144+ sürümünde Chromium tabanlı bir tarayıcı
- tarayıcının yerel olarak çalışıyor olması
- o tarayıcıda remote debugging'in etkin olması
- tarayıcıdaki ilk attach izin isteminin onaylanması

Buradaki hazırlık yalnızca yerel attach önkoşullarıyla ilgilidir. Existing-session, mevcut Chrome MCP rota sınırlarını korur; `responsebody`, PDF dışa aktarma, indirme yakalama ve toplu eylemler gibi gelişmiş rotalar için yine de yönetilen bir tarayıcı veya ham CDP profili gerekir.

Bu kontrol Docker, sandbox, remote-browser veya diğer başsız akışlar için **geçerli değildir**. Bunlar ham CDP kullanmaya devam eder.

### 2d) OAuth TLS önkoşulları

Bir OpenAI Codex OAuth profili yapılandırıldığında doctor, yerel Node/OpenSSL TLS yığınının sertifika zincirini doğrulayabildiğini onaylamak için OpenAI yetkilendirme uç noktasını yoklar. Yoklama bir sertifika hatasıyla başarısız olursa (örneğin `UNABLE_TO_GET_ISSUER_CERT_LOCALLY`, süresi dolmuş sertifika veya self-signed sertifika), doctor platforma özgü düzeltme yönergeleri yazdırır. Homebrew Node kullanan macOS'ta düzeltme genellikle `brew postinstall ca-certificates` komutudur. `--deep` ile yoklama, gateway sağlıklı olsa bile çalıştırılır.

### 2c) Codex OAuth sağlayıcı geçersiz kılmaları

Daha önce eski OpenAI taşıma ayarlarını
`models.providers.openai-codex` altında eklediyseniz, bunlar yeni sürümlerin otomatik olarak kullandığı yerleşik Codex OAuth sağlayıcı yolunu gölgeleyebilir. Doctor, bu eski taşıma ayarlarını Codex OAuth ile birlikte gördüğünde uyarı verir; böylece eski taşıma geçersiz kılmasını kaldırabilir veya yeniden yazabilir ve yerleşik yönlendirme/yedek davranışını geri alabilirsiniz. Özel proxy'ler ve yalnızca başlık temelli geçersiz kılmalar hâlâ desteklenir ve bu uyarıyı tetiklemez.

### 3) Eski durum geçişleri (disk düzeni)

Doctor eski disk üstü düzenleri mevcut yapıya taşıyabilir:

- Oturum deposu + transcript'ler:
  - `~/.openclaw/sessions/` konumundan `~/.openclaw/agents/<agentId>/sessions/` konumuna
- Agent dizini:
  - `~/.openclaw/agent/` konumundan `~/.openclaw/agents/<agentId>/agent/` konumuna
- WhatsApp auth durumu (Baileys):
  - eski `~/.openclaw/credentials/*.json` konumundan (`oauth.json` hariç)
  - `~/.openclaw/credentials/whatsapp/<accountId>/...` konumuna (varsayılan hesap kimliği: `default`)

Bu geçişler en iyi çaba esaslıdır ve idempotent'tir; doctor, yedek olarak geride bıraktığı eski klasörler olduğunda uyarılar yayınlar. Gateway/CLI ayrıca başlangıçta eski oturumlar + agent dizinini otomatik taşır, böylece geçmiş/auth/models el ile doctor çalıştırmadan agent başına olan yola yerleşir. WhatsApp auth bilerek yalnızca `openclaw doctor` yoluyla taşınır. Talk provider/provider-map normalleştirmesi artık yapısal eşitliğe göre karşılaştırma yapar; bu nedenle yalnızca anahtar sırasına bağlı farklar artık tekrar eden etkisiz `doctor --fix` değişikliklerini tetiklemez.

### 3a) Eski plugin manifest geçişleri

Doctor, kullanımdan kaldırılmış üst düzey yetenek anahtarları (`speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`,
`webSearchProviders`) için kurulu tüm plugin manifest'lerini tarar. Bulunduğunda, bunları `contracts` nesnesine taşımayı ve manifest dosyasını yerinde yeniden yazmayı önerir. Bu geçiş idempotent'tir;
`contracts` anahtarı zaten aynı değerlere sahipse, eski anahtar veri yinelenmeden kaldırılır.

### 3b) Eski cron deposu geçişleri

Doctor ayrıca, zamanlayıcının geriye dönük uyumluluk için hâlâ kabul ettiği eski iş biçimleri açısından cron iş deposunu (`varsayılan olarak ~/.openclaw/cron/jobs.json` veya geçersiz kılınmışsa `cron.store`) kontrol eder.

Geçerli cron temizlemeleri şunları içerir:

- `jobId` → `id`
- `schedule.cron` → `schedule.expr`
- üst düzey payload alanları (`message`, `model`, `thinking`, ...) → `payload`
- üst düzey delivery alanları (`deliver`, `channel`, `to`, `provider`, ...) → `delivery`
- payload `provider` delivery takma adları → açık `delivery.channel`
- basit eski `notify: true` webhook yedek işleri → açık `delivery.mode="webhook"` ile `delivery.to=cron.webhook`

Doctor, `notify: true` işlerini yalnızca davranışı değiştirmeden yapabildiğinde otomatik taşır. Bir iş eski notify yedeğini mevcut bir web dışı delivery kipiyle birleştiriyorsa, doctor uyarır ve o işi elle inceleme için olduğu gibi bırakır.

### 3c) Oturum kilidi temizliği

Doctor, eski yazma kilit dosyaları için her agent oturum dizinini tarar — bir oturum anormal şekilde sonlandığında geride kalan dosyalar. Bulunan her kilit dosyası için şunları rapor eder:
yol, PID, PID'nin hâlâ çalışıp çalışmadığı, kilit yaşı ve eski kabul edilip edilmediği (ölü PID veya 30 dakikadan eski). `--fix` / `--repair`
kipinde eski kilit dosyalarını otomatik kaldırır; aksi takdirde bir not yazdırır ve `--fix` ile yeniden çalıştırmanızı söyler.

### 4) Durum bütünlüğü kontrolleri (oturum kalıcılığı, yönlendirme ve güvenlik)

Durum dizini işletimsel beyin sapıdır. Kaybolursa, başka yerde yedeğiniz yoksa oturumları, kimlik bilgilerini, günlükleri ve yapılandırmayı kaybedersiniz.

Doctor şunları kontrol eder:

- **Durum dizini eksik**: yıkıcı durum kaybı konusunda uyarır, dizini yeniden oluşturmayı önerir ve eksik verileri geri getiremeyeceğini hatırlatır.
- **Durum dizini izinleri**: yazılabilirliği doğrular; izinleri onarmayı önerir
  (sahip/grup uyumsuzluğu algılandığında `chown` ipucu da verir).
- **macOS bulut eşzamanlı durum dizini**: durum yolu iCloud Drive
  (`~/Library/Mobile Documents/com~apple~CloudDocs/...`) veya
  `~/Library/CloudStorage/...` altında çözümlendiğinde uyarır; çünkü eşzamanlama destekli yollar daha yavaş G/Ç ve kilit/eşzamanlama yarışlarına neden olabilir.
- **Linux SD veya eMMC durum dizini**: durum yolu bir `mmcblk*`
  bağlama kaynağına çözümlendiğinde uyarır; çünkü SD veya eMMC tabanlı rastgele G/Ç, oturum ve kimlik bilgisi yazımları altında daha yavaş olabilir ve daha hızlı yıpranabilir.
- **Oturum dizinleri eksik**: `sessions/` ve oturum deposu dizini,
  geçmişi kalıcı kılmak ve `ENOENT` çöküşlerini önlemek için gereklidir.
- **Transcript uyuşmazlığı**: son oturum kayıtlarında eksik transcript dosyaları olduğunda uyarır.
- **Ana oturum “1 satırlı JSONL”**: ana transcript yalnızca bir satıra sahipse işaretler (geçmiş birikmiyor demektir).
- **Birden fazla durum dizini**: farklı ev dizinlerinde birden fazla `~/.openclaw` klasörü bulunduğunda veya `OPENCLAW_STATE_DIR` başka bir yeri işaret ettiğinde uyarır (geçmiş kurulumlar arasında bölünebilir).
- **Uzak kip hatırlatması**: `gateway.mode=remote` ise, doctor bunu uzak host üzerinde çalıştırmanız gerektiğini hatırlatır (durum orada yaşar).
- **Yapılandırma dosyası izinleri**: `~/.openclaw/openclaw.json` dosyası grup/dünya tarafından okunabiliyorsa uyarır ve izni `600` olacak şekilde sıkılaştırmayı önerir.

### 5) Model auth sağlığı (OAuth süresi dolması)

Doctor, auth deposundaki OAuth profillerini inceler, belirteçlerin süresi dolmak üzereyse/dolmuşsa uyarır ve güvenliyse bunları yenileyebilir. Anthropic
OAuth/token profili eskiyse, bir Anthropic API anahtarı veya
Anthropic setup-token yolunu önerir.
Yenileme istemleri yalnızca etkileşimli (TTY) çalışırken görünür; `--non-interactive`
yenileme denemelerini atlar.

Doctor ayrıca geçici olarak kullanılamayan auth profillerini de rapor eder:

- kısa cooldown'lar (oran sınırları/zaman aşımları/auth hataları)
- daha uzun devre dışı bırakmalar (faturalama/kredi hataları)

### 6) Hooks model doğrulaması

`hooks.gmail.model` ayarlanmışsa doctor, model başvurusunu katalog ve allowlist'e karşı doğrular; çözümlenmeyecekse veya izin verilmiyorsa uyarır.

### 7) Sandbox image onarımı

Sandbox etkinleştirildiğinde doctor, Docker image'larını kontrol eder ve mevcut image eksikse oluşturmayı veya eski adlara geçmeyi önerir.

### 7b) Paketlenmiş plugin çalışma zamanı bağımlılıkları

Doctor, paketlenmiş plugin çalışma zamanı bağımlılıklarının (örneğin
Discord plugin çalışma zamanı paketleri) OpenClaw kurulum kökünde mevcut olduğunu doğrular.
Herhangi biri eksikse doctor paketleri rapor eder ve bunları
`openclaw doctor --fix` / `openclaw doctor --repair` kipinde yükler.

### 8) Gateway hizmet geçişleri ve temizleme ipuçları

Doctor, eski gateway hizmetlerini (launchd/systemd/schtasks) algılar ve bunları kaldırıp mevcut gateway portunu kullanarak OpenClaw hizmetini kurmayı önerir. Ayrıca ek gateway benzeri hizmetleri tarayabilir ve temizleme ipuçları yazdırabilir.
Profil adlandırılmış OpenClaw gateway hizmetleri birinci sınıf kabul edilir ve "ekstra" olarak işaretlenmez.

### 8b) Başlangıç Matrix geçişi

Bir Matrix kanal hesabında bekleyen veya uygulanabilir bir eski durum geçişi olduğunda,
doctor (`--fix` / `--repair` kipinde) geçiş öncesi bir anlık görüntü oluşturur ve ardından en iyi çaba esaslı geçiş adımlarını çalıştırır: eski Matrix durum geçişi ve eski şifreli durum hazırlığı. Her iki adım da ölümcül değildir; hatalar günlüğe yazılır ve başlangıç devam eder. Salt okunur kipte (`--fix` olmadan `openclaw doctor`) bu kontrol tamamen atlanır.

### 9) Güvenlik uyarıları

Doctor, bir sağlayıcı allowlist olmadan DM'lere açıksa veya bir ilke tehlikeli biçimde yapılandırılmışsa uyarılar yayınlar.

### 10) systemd linger (Linux)

Bir systemd kullanıcı hizmeti olarak çalışıyorsa doctor, çıkış yaptıktan sonra gateway'in canlı kalması için lingering'in etkin olduğunu doğrular.

### 11) Çalışma alanı durumu (skills, plugins ve eski dizinler)

Doctor, varsayılan agent için çalışma alanı durumunun bir özetini yazdırır:

- **Skills durumu**: uygun, gereksinimleri eksik ve allowlist tarafından engellenmiş skill sayılarını sayar.
- **Eski çalışma alanı dizinleri**: `~/openclaw` veya diğer eski çalışma alanı dizinleri mevcut çalışma alanıyla birlikte varsa uyarır.
- **Plugin durumu**: yüklenen/devre dışı/hata veren plugin sayılarını sayar; hatalar için plugin kimliklerini listeler; paket plugin yeteneklerini bildirir.
- **Plugin uyumluluk uyarıları**: mevcut çalışma zamanı ile uyumluluk sorunları olan plugin'leri işaretler.
- **Plugin tanılamaları**: plugin kayıt defteri tarafından yayınlanan yükleme zamanı uyarılarını veya hatalarını gösterir.

### 11b) Bootstrap dosya boyutu

Doctor, çalışma alanı bootstrap dosyalarının (`AGENTS.md`,
`CLAUDE.md` veya diğer enjekte edilen bağlam dosyaları gibi) yapılandırılmış
karakter bütçesine yakın veya üzerinde olup olmadığını kontrol eder. Dosya başına ham ve enjekte edilmiş karakter sayılarını, kesilme yüzdesini, kesilme nedenini (`max/file` veya `max/total`) ve toplam enjekte edilen karakterleri toplam bütçenin bir kesri olarak rapor eder. Dosyalar kesilmişse veya sınıra yakınsa, doctor `agents.defaults.bootstrapMaxChars`
ve `agents.defaults.bootstrapTotalMaxChars` ayarlarını ayarlamak için ipuçları yazdırır.

### 11c) Shell completion

Doctor, geçerli shell için
(zsh, bash, fish veya PowerShell) tab completion kurulu olup olmadığını kontrol eder:

- Shell profili yavaş dinamik completion deseni kullanıyorsa
  (`source <(openclaw completion ...)`), doctor bunu daha hızlı olan
  önbellekli dosya varyantına yükseltir.
- Completion profilde yapılandırılmışsa ancak önbellek dosyası eksikse,
  doctor önbelleği otomatik olarak yeniden oluşturur.
- Hiç completion yapılandırılmamışsa doctor bunu kurmayı önerir
  (yalnızca etkileşimli kipte; `--non-interactive` ile atlanır).

Önbelleği elle yeniden oluşturmak için `openclaw completion --write-state` çalıştırın.

### 12) Gateway auth kontrolleri (yerel token)

Doctor, yerel gateway token auth hazırlığını kontrol eder.

- Token kipi bir token gerektiriyorsa ve token kaynağı yoksa, doctor bir tane oluşturmayı önerir.
- `gateway.auth.token` SecretRef tarafından yönetiliyorsa ancak kullanılamıyorsa, doctor uyarır ve bunu düz metinle üzerine yazmaz.
- `openclaw doctor --generate-gateway-token`, yalnızca token SecretRef yapılandırılmadığında oluşturmayı zorlar.

### 12b) Salt okunur SecretRef farkındalıklı onarımlar

Bazı onarım akışlarının, çalışma zamanındaki hızlı başarısız olma davranışını zayıflatmadan yapılandırılmış kimlik bilgilerini incelemesi gerekir.

- `openclaw doctor --fix` artık hedefli yapılandırma onarımları için status ailesi komutlarıyla aynı salt okunur SecretRef özet modelini kullanır.
- Örnek: Telegram `allowFrom` / `groupAllowFrom` `@username` onarımı, kullanılabilir olduğunda yapılandırılmış bot kimlik bilgilerini kullanmayı dener.
- Telegram bot token'ı SecretRef üzerinden yapılandırılmışsa ancak mevcut komut yolunda kullanılamıyorsa, doctor kimlik bilgisinin yapılandırılmış-ama-kullanılamaz olduğunu bildirir ve token'ı eksikmiş gibi göstermeden veya çökmeden otomatik çözümlemeyi atlar.

### 13) Gateway sağlık denetimi + yeniden başlatma

Doctor bir sağlık denetimi çalıştırır ve sağlıksız görünüyorsa gateway'i yeniden başlatmayı önerir.

### 13b) Bellek araması hazırlığı

Doctor, varsayılan agent için yapılandırılmış bellek araması embedding sağlayıcısının hazır olup olmadığını kontrol eder. Davranış, yapılandırılmış backend ve sağlayıcıya bağlıdır:

- **QMD backend**: `qmd` ikilisinin mevcut ve başlatılabilir olup olmadığını yoklar.
  Değilse, npm paketi ve elle ikili yol seçeneği dahil olmak üzere düzeltme yönergeleri yazdırır.
- **Açık yerel sağlayıcı**: yerel model dosyası veya tanınan bir
  uzak/indirilebilir model URL'si olup olmadığını kontrol eder. Eksikse, uzak sağlayıcıya geçmeyi önerir.
- **Açık uzak sağlayıcı** (`openai`, `voyage` vb.): ortamda veya auth deposunda bir API anahtarının mevcut olduğunu doğrular. Eksikse uygulanabilir düzeltme ipuçları yazdırır.
- **Otomatik sağlayıcı**: önce yerel model kullanılabilirliğini kontrol eder, ardından otomatik seçim sırasına göre her uzak sağlayıcıyı dener.

Bir gateway yoklama sonucu mevcut olduğunda (kontrol sırasında gateway sağlıklıydıysa),
doctor sonucunu CLI tarafından görülebilen yapılandırmayla çapraz denetler ve
varsa herhangi bir uyumsuzluğu not eder.

Embedding hazırlığını çalışma zamanında doğrulamak için `openclaw memory status --deep` kullanın.

### 14) Kanal durumu uyarıları

Gateway sağlıklıysa doctor, kanal durumu yoklaması çalıştırır ve
önerilen düzeltmelerle birlikte uyarıları rapor eder.

### 15) Supervisor yapılandırma denetimi + onarım

Doctor, kurulu supervisor yapılandırmasını (launchd/systemd/schtasks)
eksik veya eski varsayılanlar açısından kontrol eder (ör. systemd network-online bağımlılıkları ve yeniden başlatma gecikmesi). Bir uyuşmazlık bulduğunda güncelleme önerir ve hizmet dosyasını/görevi mevcut varsayılanlara göre yeniden yazabilir.

Notlar:

- `openclaw doctor`, supervisor yapılandırmasını yeniden yazmadan önce istem gösterir.
- `openclaw doctor --yes`, varsayılan onarım istemlerini kabul eder.
- `openclaw doctor --repair`, önerilen düzeltmeleri istem göstermeden uygular.
- `openclaw doctor --repair --force`, özel supervisor yapılandırmalarının üzerine yazar.
- Token auth bir token gerektiriyorsa ve `gateway.auth.token` SecretRef tarafından yönetiliyorsa, doctor hizmet kurulum/onarı mı SecretRef'i doğrular ancak çözümlenmiş düz metin token değerlerini supervisor hizmet ortam metadata'sına kalıcı olarak yazmaz.
- Token auth bir token gerektiriyorsa ve yapılandırılmış token SecretRef çözümlenmemişse, doctor kurulum/onarma yolunu uygulanabilir yönergelerle engeller.
- Hem `gateway.auth.token` hem de `gateway.auth.password` yapılandırılmışsa ve `gateway.auth.mode` ayarlanmamışsa, doctor kip açıkça ayarlanana kadar kurulum/onarmayı engeller.
- Linux kullanıcı-systemd birimleri için doctor token sapma kontrolleri artık hizmet auth metadata'sını karşılaştırırken hem `Environment=` hem de `EnvironmentFile=` kaynaklarını içerir.
- Her zaman `openclaw gateway install --force` ile tam yeniden yazmayı zorlayabilirsiniz.

### 16) Gateway çalışma zamanı + port tanılamaları

Doctor, hizmet çalışma zamanını (PID, son çıkış durumu) inceler ve hizmet kurulu olduğu hâlde gerçekte çalışmıyorsa uyarır. Ayrıca gateway portunda (varsayılan `18789`) port çakışmalarını kontrol eder ve olası nedenleri bildirir (gateway zaten çalışıyor, SSH tüneli).

### 17) Gateway çalışma zamanı en iyi uygulamaları

Doctor, gateway hizmeti Bun üzerinde veya sürüm yöneticisiyle yönetilen bir Node yolunda
(`nvm`, `fnm`, `volta`, `asdf` vb.) çalışıyorsa uyarır. WhatsApp + Telegram kanalları Node gerektirir ve sürüm yöneticisi yolları yükseltmelerden sonra bozulabilir çünkü hizmet shell init'inizi yüklemez. Doctor, kullanılabiliyorsa bir sistem Node kurulumuna geçiş önerebilir (Homebrew/apt/choco).

### 18) Yapılandırma yazımı + wizard metadata

Doctor, tüm yapılandırma değişikliklerini kalıcı hale getirir ve doctor çalıştırmasını kaydetmek için wizard metadata damgası vurur.

### 19) Çalışma alanı ipuçları (yedekleme + bellek sistemi)

Doctor, eksikse bir çalışma alanı bellek sistemi önerir ve çalışma alanı zaten git altında değilse bir yedekleme ipucu yazdırır.

Çalışma alanı yapısı ve git yedekleme (önerilen özel GitHub veya GitLab) için tam kılavuza [/concepts/agent-workspace](/tr/concepts/agent-workspace) üzerinden bakın.
