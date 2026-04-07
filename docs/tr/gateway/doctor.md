---
read_when:
    - Doctor geçişleri ekliyorsunuz veya değiştiriyorsunuz
    - Uyumsuz yapılandırma değişiklikleri ekliyorsunuz
summary: 'Doctor komutu: sağlık kontrolleri, yapılandırma geçişleri ve onarım adımları'
title: Doctor
x-i18n:
    generated_at: "2026-04-07T08:45:56Z"
    model: gpt-5.4
    provider: openai
    source_hash: a834dc7aec79c20d17bc23d37fb5f5e99e628d964d55bd8cf24525a7ee57130c
    source_path: gateway/doctor.md
    workflow: 15
---

# Doctor

`openclaw doctor`, OpenClaw için onarım + geçiş aracıdır. Eski yapılandırma/durumu düzeltir, sağlık kontrolleri yapar ve uygulanabilir onarım adımları sağlar.

## Hızlı başlangıç

```bash
openclaw doctor
```

### Headless / otomasyon

```bash
openclaw doctor --yes
```

Sormadan varsayılanları kabul eder (uygulanabildiğinde yeniden başlatma/hizmet/sandbox onarım adımları dahil).

```bash
openclaw doctor --repair
```

Önerilen onarımları sormadan uygular (güvenli olduğunda onarımlar + yeniden başlatmalar).

```bash
openclaw doctor --repair --force
```

Agresif onarımları da uygular (özel supervisor yapılandırmalarının üzerine yazar).

```bash
openclaw doctor --non-interactive
```

İstemler olmadan çalışır ve yalnızca güvenli geçişleri uygular (yapılandırma normalizasyonu + disk üzerindeki durum taşıma işlemleri). İnsan onayı gerektiren yeniden başlatma/hizmet/sandbox işlemlerini atlar.
Legacy durum geçişleri algılandığında otomatik olarak çalışır.

```bash
openclaw doctor --deep
```

Ek gateway kurulumları için sistem hizmetlerini tarar (launchd/systemd/schtasks).

Yazmadan önce değişiklikleri incelemek istiyorsanız, önce yapılandırma dosyasını açın:

```bash
cat ~/.openclaw/openclaw.json
```

## Ne yapar (özet)

- Git kurulumları için isteğe bağlı ön uçuş güncellemesi (yalnızca etkileşimli).
- UI protokol güncelliği kontrolü (protokol şeması daha yeniyse Control UI'ı yeniden oluşturur).
- Sağlık kontrolü + yeniden başlatma istemi.
- Skills durum özeti (uygun/eksik/engelli) ve plugin durumu.
- Legacy değerler için yapılandırma normalizasyonu.
- Legacy düz `talk.*` alanlarından `talk.provider` + `talk.providers.<provider>` yapısına Talk yapılandırması geçişi.
- Legacy Chrome uzantısı yapılandırmaları ve Chrome MCP hazırlığı için tarayıcı geçiş kontrolleri.
- OpenCode sağlayıcı geçersiz kılma uyarıları (`models.providers.opencode` / `models.providers.opencode-go`).
- OpenAI Codex OAuth profilleri için OAuth TLS önkoşulları kontrolü.
- Legacy disk üstü durum geçişi (oturumlar/agent dizini/WhatsApp auth).
- Legacy plugin manifest sözleşme anahtarı geçişi (`speechProviders`, `realtimeTranscriptionProviders`, `realtimeVoiceProviders`, `mediaUnderstandingProviders`, `imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`, `webSearchProviders` → `contracts`).
- Legacy cron deposu geçişi (`jobId`, `schedule.cron`, üst düzey delivery/payload alanları, payload `provider`, basit `notify: true` webhook fallback işleri).
- Oturum kilit dosyası incelemesi ve eski kilit temizliği.
- Durum bütünlüğü ve izin kontrolleri (oturumlar, transkriptler, durum dizini).
- Yerel çalışırken yapılandırma dosyası izin kontrolleri (`chmod 600`).
- Model auth sağlığı: OAuth süre sonunu denetler, süresi dolmak üzere olan token'ları yenileyebilir ve auth-profile cooldown/devre dışı durumlarını raporlar.
- Ek çalışma alanı dizini tespiti (`~/openclaw`).
- Sandbox etkin olduğunda sandbox imajı onarımı.
- Legacy hizmet geçişi ve ek gateway tespiti.
- Matrix kanal legacy durum geçişi (`--fix` / `--repair` modunda).
- Gateway çalışma zamanı kontrolleri (hizmet yüklü ama çalışmıyor; önbelleğe alınmış launchd etiketi).
- Kanal durum uyarıları (çalışan gateway'den yoklanır).
- İsteğe bağlı onarımla supervisor yapılandırma denetimi (launchd/systemd/schtasks).
- Gateway çalışma zamanı en iyi uygulama kontrolleri (Node ve Bun, sürüm yöneticisi yolları).
- Gateway port çakışması tanılaması (varsayılan `18789`).
- Açık DM ilkeleri için güvenlik uyarıları.
- Yerel token modu için gateway auth kontrolleri (token kaynağı yoksa token üretmeyi teklif eder; token SecretRef yapılandırmalarının üzerine yazmaz).
- Linux'ta systemd linger kontrolü.
- Çalışma alanı bootstrap dosya boyutu kontrolü (bağlam dosyaları için kısaltma/sınıra yakın uyarıları).
- Kabuk tamamlama durumu kontrolü ve otomatik kurulum/yükseltme.
- Bellek arama embedding sağlayıcısı hazırlık kontrolü (yerel model, uzak API key veya QMD ikilisi).
- Kaynak kurulum kontrolleri (pnpm çalışma alanı uyumsuzluğu, eksik UI varlıkları, eksik tsx ikilisi).
- Güncellenmiş yapılandırma + sihirbaz meta verilerini yazar.

## Ayrıntılı davranış ve gerekçe

### 0) İsteğe bağlı güncelleme (git kurulumları)

Bu bir git checkout ise ve doctor etkileşimli çalışıyorsa, doctor çalıştırılmadan önce güncelleme yapmayı (fetch/rebase/build) teklif eder.

### 1) Yapılandırma normalizasyonu

Yapılandırma legacy değer şekilleri içeriyorsa (örneğin kanal bazlı geçersiz kılma olmadan `messages.ackReaction`), doctor bunları geçerli şemaya normalleştirir.

Buna legacy Talk düz alanları da dahildir. Geçerli genel Talk yapılandırması
`talk.provider` + `talk.providers.<provider>` şeklindedir. Doctor eski
`talk.voiceId` / `talk.voiceAliases` / `talk.modelId` / `talk.outputFormat` /
`talk.apiKey` biçimlerini sağlayıcı haritasına yeniden yazar.

### 2) Legacy yapılandırma anahtarı geçişleri

Yapılandırma kullanımdan kaldırılmış anahtarlar içeriyorsa, diğer komutlar çalışmayı reddeder ve sizden `openclaw doctor` çalıştırmanızı ister.

Doctor şunları yapar:

- Hangi legacy anahtarların bulunduğunu açıklar.
- Uyguladığı geçişi gösterir.
- `~/.openclaw/openclaw.json` dosyasını güncellenmiş şemayla yeniden yazar.

Gateway de başlangıçta legacy bir yapılandırma biçimi algıladığında doctor geçişlerini otomatik çalıştırır; böylece eski yapılandırmalar elle müdahale olmadan onarılır.
Cron iş deposu geçişleri `openclaw doctor --fix` tarafından işlenir.

Geçerli geçişler:

- `routing.allowFrom` → `channels.whatsapp.allowFrom`
- `routing.groupChat.requireMention` → `channels.whatsapp/telegram/imessage.groups."*".requireMention`
- `routing.groupChat.historyLimit` → `messages.groupChat.historyLimit`
- `routing.groupChat.mentionPatterns` → `messages.groupChat.mentionPatterns`
- `routing.queue` → `messages.queue`
- `routing.bindings` → üst düzey `bindings`
- `routing.agents`/`routing.defaultAgentId` → `agents.list` + `agents.list[].default`
- legacy `talk.voiceId`/`talk.voiceAliases`/`talk.modelId`/`talk.outputFormat`/`talk.apiKey` → `talk.provider` + `talk.providers.<provider>`
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
- Adlandırılmış `accounts` içeren kanallarda, tek hesaplı üst düzey kanal değerleri kalmışsa, bu hesap kapsamlı değerleri o kanal için seçilen yükseltilmiş hesaba taşıyın (`accounts.default` çoğu kanal için; Matrix mevcut eşleşen adlı/varsayılan hedefi koruyabilir)
- `identity` → `agents.list[].identity`
- `agent.*` → `agents.defaults` + `tools.*` (tools/elevated/exec/sandbox/subagents)
- `agent.model`/`allowedModels`/`modelAliases`/`modelFallbacks`/`imageModelFallbacks`
  → `agents.defaults.models` + `agents.defaults.model.primary/fallbacks` + `agents.defaults.imageModel.primary/fallbacks`
- `browser.ssrfPolicy.allowPrivateNetwork` → `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork`
- `browser.profiles.*.driver: "extension"` → `"existing-session"`
- `browser.relayBindHost` öğesini kaldırır (legacy uzantı relay ayarı)

Doctor uyarıları ayrıca çok hesaplı kanallar için varsayılan hesap yönlendirmesi de içerir:

- `channels.<channel>.accounts` içinde iki veya daha fazla girdi yapılandırılmışsa ancak `channels.<channel>.defaultAccount` veya `accounts.default` yoksa, doctor fallback yönlendirmenin beklenmeyen bir hesap seçebileceği konusunda uyarır.
- `channels.<channel>.defaultAccount` bilinmeyen bir hesap kimliğine ayarlanmışsa, doctor uyarır ve yapılandırılmış hesap kimliklerini listeler.

### 2b) OpenCode sağlayıcı geçersiz kılmaları

`models.providers.opencode`, `opencode-zen` veya `opencode-go` değerlerini elle eklediyseniz,
bu, `@mariozechner/pi-ai` içindeki yerleşik OpenCode kataloğunu geçersiz kılar.
Bu durum modelleri yanlış API'ye zorlayabilir veya maliyetleri sıfırlayabilir. Doctor, geçersiz kılmayı kaldırıp model başına API yönlendirmesini + maliyetleri geri yükleyebilmeniz için uyarır.

### 2c) Tarayıcı geçişi ve Chrome MCP hazırlığı

Tarayıcı yapılandırmanız hâlâ kaldırılmış Chrome uzantısı yolunu işaret ediyorsa, doctor
bunu geçerli ana makine-yerel Chrome MCP bağlanma modeline normalleştirir:

- `browser.profiles.*.driver: "extension"` değeri `"existing-session"` olur
- `browser.relayBindHost` kaldırılır

Doctor ayrıca `defaultProfile:
"user"` veya yapılandırılmış bir `existing-session` profili kullandığınızda ana makine-yerel Chrome MCP yolunu da denetler:

- varsayılan otomatik bağlanma profilleri için Google Chrome'un aynı ana makinede kurulu olup olmadığını denetler
- algılanan Chrome sürümünü denetler ve Chrome 144'ün altındaysa uyarır
- tarayıcı inspect sayfasında uzak hata ayıklamayı etkinleştirmenizi hatırlatır (örneğin `chrome://inspect/#remote-debugging`, `brave://inspect/#remote-debugging`,
  veya `edge://inspect/#remote-debugging`)

Doctor, Chrome tarafındaki ayarı sizin yerinize etkinleştiremez. Ana makine-yerel Chrome MCP için hâlâ şunlar gerekir:

- gateway/node ana makinesinde Chromium tabanlı 144+ bir tarayıcı
- tarayıcının yerel olarak çalışıyor olması
- o tarayıcıda uzak hata ayıklamanın etkin olması
- tarayıcıdaki ilk bağlanma onay isteminin kabul edilmesi

Buradaki hazırlık yalnızca yerel bağlanma önkoşullarıyla ilgilidir. Existing-session, geçerli Chrome MCP yol sınırlarını korur; `responsebody`, PDF dışa aktarma, indirme yakalama ve toplu işlemler gibi gelişmiş yollar için hâlâ yönetilen bir tarayıcı veya ham CDP profili gerekir.

Bu kontrol Docker, sandbox, remote-browser veya diğer headless akışlar için **geçerli değildir**. Bunlar ham CDP kullanmaya devam eder.

### 2d) OAuth TLS önkoşulları

Bir OpenAI Codex OAuth profili yapılandırıldığında, doctor yerel Node/OpenSSL TLS yığınının sertifika zincirini doğrulayabildiğini doğrulamak için OpenAI yetkilendirme uç noktasını yoklar. Yoklama bir sertifika hatasıyla başarısız olursa (örneğin `UNABLE_TO_GET_ISSUER_CERT_LOCALLY`, süresi dolmuş sertifika veya self-signed sertifika), doctor platforma özgü düzeltme yönergeleri yazdırır. Homebrew Node kullanan macOS'ta düzeltme genellikle `brew postinstall ca-certificates` komutudur. `--deep` ile, gateway sağlıklı olsa bile yoklama çalışır.

### 3) Legacy durum geçişleri (disk düzeni)

Doctor eski disk düzenlerini geçerli yapıya taşıyabilir:

- Oturum deposu + transkriptler:
  - `~/.openclaw/sessions/` konumundan `~/.openclaw/agents/<agentId>/sessions/` konumuna
- Agent dizini:
  - `~/.openclaw/agent/` konumundan `~/.openclaw/agents/<agentId>/agent/` konumuna
- WhatsApp auth durumu (Baileys):
  - legacy `~/.openclaw/credentials/*.json` ( `oauth.json` hariç ) konumundan
  - `~/.openclaw/credentials/whatsapp/<accountId>/...` konumuna (varsayılan hesap kimliği: `default`)

Bu geçişler best-effort ve idempotent'tır; doctor herhangi bir legacy klasörü yedek olarak bıraktığında uyarı verir. Gateway/CLI de başlangıçta legacy oturumlar + agent dizinini otomatik geçirir; böylece geçmiş/auth/model'ler elle doctor çalıştırmadan agent başına yola taşınır. WhatsApp auth özellikle yalnızca `openclaw doctor` ile geçirilir. Talk provider/provider-map normalizasyonu artık yapısal eşitliğe göre karşılaştırılır; böylece yalnızca anahtar sırası farkları artık yinelenen no-op `doctor --fix` değişikliklerini tetiklemez.

### 3a) Legacy plugin manifest geçişleri

Doctor, kurulu tüm plugin manifest dosyalarını kullanımdan kaldırılmış üst düzey yetenek anahtarları için tarar
(`speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`,
`webSearchProviders`). Bulunduğunda, bunları `contracts`
nesnesine taşımayı teklif eder ve manifest dosyasını yerinde yeniden yazar. Bu geçiş idempotent'tır;
`contracts` anahtarı zaten aynı değerlere sahipse, veriyi çoğaltmadan
legacy anahtar kaldırılır.

### 3b) Legacy cron deposu geçişleri

Doctor ayrıca cron iş deposunu da denetler (varsayılan olarak `~/.openclaw/cron/jobs.json`,
veya geçersiz kılınmışsa `cron.store`) zamanlayıcının uyumluluk için hâlâ kabul ettiği
eski iş şekilleri için.

Geçerli cron temizlikleri şunları içerir:

- `jobId` → `id`
- `schedule.cron` → `schedule.expr`
- üst düzey payload alanları (`message`, `model`, `thinking`, ...) → `payload`
- üst düzey delivery alanları (`deliver`, `channel`, `to`, `provider`, ...) → `delivery`
- payload `provider` delivery takma adları → açık `delivery.channel`
- basit legacy `notify: true` webhook fallback işleri → açık `delivery.mode="webhook"` ile `delivery.to=cron.webhook`

Doctor, `notify: true` işlerini yalnızca davranışı değiştirmeden yapabildiğinde otomatik geçirir. Bir iş legacy notify fallback ile mevcut bir webhook olmayan delivery modunu birleştiriyorsa, doctor uyarır ve bu işi elle inceleme için olduğu gibi bırakır.

### 3c) Oturum kilidi temizliği

Doctor, anormal şekilde sonlanan oturumların geride bıraktığı yazma kilidi dosyaları için her agent oturum dizinini tarar. Bulunan her kilit dosyası için şunları raporlar:
yol, PID, PID'nin hâlâ canlı olup olmadığı, kilit yaşı ve eski kabul edilip edilmediği
(ölü PID veya 30 dakikadan eski). `--fix` / `--repair`
modunda doctor eski kilit dosyalarını otomatik kaldırır; aksi halde not yazar ve
`--fix` ile yeniden çalıştırmanızı söyler.

### 4) Durum bütünlüğü kontrolleri (oturum kalıcılığı, yönlendirme ve güvenlik)

Durum dizini operasyonel omurgadır. Kaybolursa
oturumları, kimlik bilgilerini, günlükleri ve yapılandırmayı kaybedersiniz (başka yerde yedekleriniz yoksa).

Doctor şunları kontrol eder:

- **Durum dizini yok**: yıkıcı durum kaybı hakkında uyarır, dizini yeniden oluşturmayı ister
  ve eksik verileri kurtaramayacağını hatırlatır.
- **Durum dizini izinleri**: yazılabilirliği doğrular; izinleri onarmayı teklif eder
  (sahip/grup uyumsuzluğu algılanırsa `chown` ipucu da verir).
- **macOS bulut eşitlemeli durum dizini**: durum iCloud Drive altında çözümleniyorsa uyarır
  (`~/Library/Mobile Documents/com~apple~CloudDocs/...`) veya
  `~/Library/CloudStorage/...`, çünkü eşitleme destekli yollar daha yavaş I/O'ya
  ve kilit/eşitleme yarışlarına neden olabilir.
- **Linux SD veya eMMC durum dizini**: durum bir `mmcblk*`
  bağlama kaynağına çözülüyorsa uyarır; çünkü SD veya eMMC destekli rastgele I/O, oturum ve kimlik bilgisi yazımları altında daha yavaş olabilir ve daha hızlı yıpranabilir.
- **Oturum dizinleri yok**: `sessions/` ve oturum deposu dizini
  geçmişi kalıcı kılmak ve `ENOENT` çöküşlerini önlemek için gereklidir.
- **Transkript uyuşmazlığı**: son oturum girdilerinde eksik
  transkript dosyaları varsa uyarır.
- **Ana oturum “1 satırlık JSONL”**: ana transkriptin yalnızca bir
  satırı olduğunda işaretler (geçmiş birikmiyor).
- **Birden çok durum dizini**: birden çok `~/.openclaw` klasörü varsa uyarır
  veya `OPENCLAW_STATE_DIR` başka bir yeri işaret ediyorsa (geçmiş kurulumlar arasında bölünebilir).
- **Uzak mod hatırlatması**: `gateway.mode=remote` ise doctor, bunu
  uzak ana makinede çalıştırmanızı hatırlatır (durum orada yaşar).
- **Yapılandırma dosyası izinleri**: `~/.openclaw/openclaw.json`
  grup/herkes tarafından okunabilir durumdaysa uyarır ve `600` yapmayı teklif eder.

### 5) Model auth sağlığı (OAuth süre sonu)

Doctor, auth deposundaki OAuth profillerini inceler, token'ların
süresi dolmak üzereyken veya dolmuşken uyarır ve güvenliyse yenileyebilir. Anthropic
OAuth/token profili eskiyse Anthropic API key veya
Anthropic setup-token yolunu önerir.
Yenileme istemleri yalnızca etkileşimli (TTY) çalışırken görünür; `--non-interactive`
yenileme denemelerini atlar.

Doctor ayrıca aşağıdaki nedenlerle geçici olarak kullanılamayan auth profillerini de raporlar:

- kısa cooldown'lar (oran sınırları/zaman aşımları/auth hataları)
- daha uzun devre dışı bırakmalar (faturalandırma/kredi hataları)

### 6) Hooks model doğrulaması

`hooks.gmail.model` ayarlanmışsa, doctor model başvurusunu katalog ve izin listesine göre doğrular; çözümlenmeyecekse veya izin verilmiyorsa uyarır.

### 7) Sandbox imajı onarımı

Sandbox etkin olduğunda doctor Docker imajlarını denetler ve geçerli imaj yoksa oluşturmayı veya legacy adlara geçmeyi teklif eder.

### 7b) Paketlenmiş plugin çalışma zamanı bağımlılıkları

Doctor, paketlenmiş plugin çalışma zamanı bağımlılıklarının (örneğin
Discord plugin çalışma zamanı paketleri) OpenClaw kurulum kökünde mevcut olduğunu doğrular.
Eksik olan varsa doctor paketleri raporlar ve bunları
`openclaw doctor --fix` / `openclaw doctor --repair` modunda kurar.

### 8) Gateway hizmet geçişleri ve temizlik ipuçları

Doctor legacy gateway hizmetlerini (launchd/systemd/schtasks) algılar ve
bunları kaldırmayı ve OpenClaw hizmetini geçerli gateway
portunu kullanarak kurmayı teklif eder. Ayrıca ek gateway benzeri hizmetleri tarayıp temizlik ipuçları yazdırabilir.
Profil adlandırılmış OpenClaw gateway hizmetleri birinci sınıf kabul edilir ve
"ek" olarak işaretlenmez.

### 8b) Başlangıç Matrix geçişi

Bir Matrix kanal hesabında bekleyen veya işlem yapılabilir bir legacy durum geçişi olduğunda,
doctor (`--fix` / `--repair` modunda) geçiş öncesi bir anlık görüntü oluşturur ve ardından
best-effort geçiş adımlarını çalıştırır: legacy Matrix durum geçişi ve legacy
şifreli durum hazırlığı. Her iki adım da ölümcül değildir; hatalar günlüğe yazılır ve
başlangıç devam eder. Salt okunur modda (`--fix` olmadan `openclaw doctor`) bu kontrol
tamamen atlanır.

### 9) Güvenlik uyarıları

Doctor, bir sağlayıcı izin listesi olmadan DM'lere açıksa veya
bir ilke tehlikeli şekilde yapılandırılmışsa uyarılar verir.

### 10) systemd linger (Linux)

Systemd kullanıcı hizmeti olarak çalışıyorsa doctor, çıkış yaptıktan sonra gateway'in
canlı kalması için lingering'in etkin olduğundan emin olur.

### 11) Çalışma alanı durumu (skills, plugin'ler ve legacy dizinler)

Doctor, varsayılan agent için çalışma alanı durumunun bir özetini yazdırır:

- **Skills durumu**: uygun, gereksinimi eksik ve izin listesi tarafından engellenmiş skills sayısını verir.
- **Legacy çalışma alanı dizinleri**: `~/openclaw` veya diğer legacy çalışma alanı dizinleri
  geçerli çalışma alanıyla birlikte varsa uyarır.
- **Plugin durumu**: yüklenen/devre dışı/hatalı plugin sayısını verir; herhangi bir
  hata için plugin kimliklerini listeler; bundle plugin yeteneklerini raporlar.
- **Plugin uyumluluk uyarıları**: geçerli çalışma zamanı ile
  uyumluluk sorunları olan plugin'leri işaretler.
- **Plugin tanılama**: plugin kayıt defteri tarafından yayımlanan yükleme zamanı uyarılarını veya hatalarını
  gösterir.

### 11b) Bootstrap dosya boyutu

Doctor, çalışma alanı bootstrap dosyalarının (`AGENTS.md`,
`CLAUDE.md` veya diğer enjekte edilen bağlam dosyaları gibi) yapılandırılmış
karakter bütçesine yakın veya onun üzerinde olup olmadığını denetler. Dosya başına ham ve enjekte edilmiş karakter sayılarını, kısaltma
yüzdesini, kısaltma nedenini (`max/file` veya `max/total`) ve toplam enjekte edilmiş
karakterleri toplam bütçenin bir kesri olarak raporlar. Dosyalar kısaltıldığında veya sınıra yakın olduğunda, doctor `agents.defaults.bootstrapMaxChars`
ve `agents.defaults.bootstrapTotalMaxChars` ayarlarını düzenlemek için ipuçları yazdırır.

### 11c) Kabuk tamamlama

Doctor, geçerli kabuk için sekme tamamlamasının kurulu olup olmadığını denetler
(zsh, bash, fish veya PowerShell):

- Kabuk profili yavaş bir dinamik tamamlama deseni kullanıyorsa
  (`source <(openclaw completion ...)`), doctor bunu daha hızlı
  önbelleğe alınmış dosya varyantına yükseltir.
- Tamamlama profilde yapılandırılmışsa ama önbellek dosyası eksikse,
  doctor önbelleği otomatik yeniden üretir.
- Hiç tamamlama yapılandırılmamışsa, doctor bunu kurmayı ister
  (yalnızca etkileşimli modda; `--non-interactive` ile atlanır).

Önbelleği elle yeniden üretmek için `openclaw completion --write-state` çalıştırın.

### 12) Gateway auth kontrolleri (yerel token)

Doctor, yerel gateway token auth hazırlığını denetler.

- Token modu bir token gerektiriyorsa ve hiçbir token kaynağı yoksa, doctor bir tane üretmeyi teklif eder.
- `gateway.auth.token` SecretRef ile yönetiliyorsa ancak kullanılamıyorsa, doctor uyarır ve bunun üzerine düz metin yazmaz.
- `openclaw doctor --generate-gateway-token`, yalnızca token SecretRef yapılandırılmadığında üretimi zorlar.

### 12b) Salt okunur SecretRef farkında onarımlar

Bazı onarım akışlarının, çalışma zamanındaki hızlı başarısız olma davranışını zayıflatmadan yapılandırılmış kimlik bilgilerini incelemesi gerekir.

- `openclaw doctor --fix`, hedefli yapılandırma onarımları için artık status ailesi komutlarıyla aynı salt okunur SecretRef özet modelini kullanır.
- Örnek: Telegram `allowFrom` / `groupAllowFrom` `@username` onarımı, uygun olduğunda yapılandırılmış bot kimlik bilgilerini kullanmayı dener.
- Telegram bot token'ı SecretRef üzerinden yapılandırılmışsa ancak geçerli komut yolunda kullanılamıyorsa, doctor kimlik bilgisinin yapılandırılmış ama kullanılamaz olduğunu bildirir ve eksik olarak yanlış raporlamak veya çökermek yerine otomatik çözümlemeyi atlar.

### 13) Gateway sağlık kontrolü + yeniden başlatma

Doctor bir sağlık kontrolü çalıştırır ve gateway sağlıksız görünüyorsa
yeniden başlatmayı teklif eder.

### 13b) Bellek arama hazırlığı

Doctor, yapılandırılmış bellek arama embedding sağlayıcısının varsayılan
agent için hazır olup olmadığını denetler. Davranış, yapılandırılmış backend ve sağlayıcıya bağlıdır:

- **QMD backend**: `qmd` ikilisinin kullanılabilir ve başlatılabilir olup olmadığını yoklar.
  Değilse npm paketi ve elle ikili yol seçeneği dahil düzeltme yönergeleri yazdırır.
- **Açık yerel sağlayıcı**: yerel model dosyasını veya tanınan bir
  uzak/indirilebilir model URL'sini denetler. Eksikse uzak sağlayıcıya geçmeyi önerir.
- **Açık uzak sağlayıcı** (`openai`, `voyage` vb.): ortamda veya auth deposunda bir API key
  bulunup bulunmadığını doğrular. Eksikse uygulanabilir düzeltme ipuçları yazdırır.
- **Otomatik sağlayıcı**: önce yerel model kullanılabilirliğini denetler, ardından
  otomatik seçim sırasındaki her uzak sağlayıcıyı dener.

Bir gateway yoklama sonucu mevcut olduğunda (kontrol sırasında gateway sağlıklıydı),
doctor sonucunu CLI tarafından görülebilen yapılandırmayla çapraz karşılaştırır ve
herhangi bir tutarsızlığı not eder.

Çalışma zamanında embedding hazırlığını doğrulamak için `openclaw memory status --deep` kullanın.

### 14) Kanal durum uyarıları

Gateway sağlıklıysa doctor kanal durumu yoklaması çalıştırır ve
önerilen düzeltmelerle birlikte uyarıları raporlar.

### 15) Supervisor yapılandırma denetimi + onarım

Doctor, kurulu supervisor yapılandırmasını (launchd/systemd/schtasks)
eksik veya eski varsayılanlar için denetler (örn. systemd network-online bağımlılıkları ve
yeniden başlatma gecikmesi). Uyumsuzluk bulduğunda güncelleme önerir ve
hizmet dosyasını/görevi geçerli varsayılanlara göre yeniden yazabilir.

Notlar:

- `openclaw doctor`, supervisor yapılandırmasını yeniden yazmadan önce sorar.
- `openclaw doctor --yes`, varsayılan onarım istemlerini kabul eder.
- `openclaw doctor --repair`, önerilen düzeltmeleri istem olmadan uygular.
- `openclaw doctor --repair --force`, özel supervisor yapılandırmalarının üzerine yazar.
- Token auth bir token gerektiriyorsa ve `gateway.auth.token` SecretRef ile yönetiliyorsa, doctor hizmet kurma/onarımı SecretRef'i doğrular ancak çözümlenmiş düz metin token değerlerini supervisor hizmet ortam meta verisine kalıcı olarak yazmaz.
- Token auth bir token gerektiriyorsa ve yapılandırılmış token SecretRef çözümlenmemişse, doctor kurulum/onarım yolunu uygulanabilir yönergelerle engeller.
- Hem `gateway.auth.token` hem de `gateway.auth.password` yapılandırılmışsa ve `gateway.auth.mode` ayarlanmamışsa, doctor mod açıkça ayarlanana kadar kurulum/onarımı engeller.
- Linux user-systemd birimleri için doctor token sapması kontrolleri artık hizmet auth meta verisini karşılaştırırken hem `Environment=` hem de `EnvironmentFile=` kaynaklarını içerir.
- Her zaman `openclaw gateway install --force` ile tam yeniden yazımı zorlayabilirsiniz.

### 16) Gateway çalışma zamanı + port tanılaması

Doctor, hizmet çalışma zamanını (PID, son çıkış durumu) inceler ve
hizmet kurulu ama gerçekte çalışmıyorsa uyarır. Ayrıca gateway portunda
(varsayılan `18789`) port çakışması olup olmadığını kontrol eder ve olası nedenleri raporlar (gateway zaten çalışıyor, SSH tüneli).

### 17) Gateway çalışma zamanı en iyi uygulamaları

Doctor, gateway hizmeti Bun üzerinde veya sürüm yöneticili bir Node yolunda
(`nvm`, `fnm`, `volta`, `asdf` vb.) çalışıyorsa uyarır. WhatsApp + Telegram kanalları Node gerektirir,
ve sürüm yöneticisi yolları yükseltmelerden sonra bozulabilir çünkü hizmet kabuk init dosyanızı
yüklemez. Doctor, sistem Node kurulumu mevcutsa buna geçmeyi teklif eder
(Homebrew/apt/choco).

### 18) Yapılandırma yazımı + sihirbaz meta verileri

Doctor, yapılandırma değişikliklerini kalıcı hale getirir ve
doctor çalıştırmasını kaydetmek için sihirbaz meta verilerini damgalar.

### 19) Çalışma alanı ipuçları (yedekleme + bellek sistemi)

Doctor, eksikse bir çalışma alanı bellek sistemi önerir ve çalışma alanı henüz git altında değilse
bir yedekleme ipucu yazdırır.

Çalışma alanı yapısı ve git yedekleme için tam kılavuzda
(recommended private GitHub or GitLab) bkz. [/concepts/agent-workspace](/tr/concepts/agent-workspace).
