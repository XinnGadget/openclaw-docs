---
read_when:
    - Doctor geçişleri ekliyorsunuz veya değiştiriyorsunuz
    - Uyumsuz yapılandırma değişiklikleri getiriyorsunuz
summary: 'Doctor komutu: sağlık kontrolleri, yapılandırma geçişleri ve onarım adımları'
title: Doctor
x-i18n:
    generated_at: "2026-04-06T03:08:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6c0a15c522994552a1eef39206bed71fc5bf45746776372f24f31c101bfbd411
    source_path: gateway/doctor.md
    workflow: 15
---

# Doctor

`openclaw doctor`, OpenClaw için onarım + geçiş aracıdır. Eskiyen
yapılandırmayı/durumu düzeltir, sağlık kontrolleri yapar ve uygulanabilir onarım adımları sağlar.

## Hızlı başlangıç

```bash
openclaw doctor
```

### Headless / otomasyon

```bash
openclaw doctor --yes
```

İstemde bulunmadan varsayılanları kabul eder (uygunsa yeniden başlatma/hizmet/sandbox onarım adımları dahil).

```bash
openclaw doctor --repair
```

Önerilen onarımları istemde bulunmadan uygular (güvenli olduğunda onarımlar + yeniden başlatmalar).

```bash
openclaw doctor --repair --force
```

Agresif onarımları da uygular (özel supervisor yapılandırmalarının üzerine yazar).

```bash
openclaw doctor --non-interactive
```

İstemler olmadan çalışır ve yalnızca güvenli geçişleri uygular (yapılandırma normalleştirme + disk üzerindeki durum taşımaları). İnsan onayı gerektiren yeniden başlatma/hizmet/sandbox eylemlerini atlar.
Eski durum geçişleri algılandığında otomatik olarak çalışır.

```bash
openclaw doctor --deep
```

Ek gateway kurulumları için sistem hizmetlerini tarar (launchd/systemd/schtasks).

Yazmadan önce değişiklikleri gözden geçirmek istiyorsanız, önce yapılandırma dosyasını açın:

```bash
cat ~/.openclaw/openclaw.json
```

## Ne yapar (özet)

- Git kurulumları için isteğe bağlı ön uçuş güncellemesi (yalnızca etkileşimli).
- UI protokol güncelliği denetimi (protokol şeması daha yeniyse Control UI'yi yeniden oluşturur).
- Sağlık denetimi + yeniden başlatma istemi.
- Skills durum özeti (uygun/eksik/engelli) ve plugin durumu.
- Eski değerler için yapılandırma normalleştirme.
- Eski düz `talk.*` alanlarından `talk.provider` + `talk.providers.<provider>` yapısına Talk yapılandırma geçişi.
- Eski Chrome extension yapılandırmaları ve Chrome MCP hazırlığı için browser geçiş denetimleri.
- OpenCode sağlayıcı geçersiz kılma uyarıları (`models.providers.opencode` / `models.providers.opencode-go`).
- OpenAI Codex OAuth profilleri için OAuth TLS önkoşulları denetimi.
- Disk üzerindeki eski durum geçişi (oturumlar/agent dizini/WhatsApp kimlik doğrulaması).
- Eski plugin manifest sözleşme anahtarı geçişi (`speechProviders`, `realtimeTranscriptionProviders`, `realtimeVoiceProviders`, `mediaUnderstandingProviders`, `imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`, `webSearchProviders` → `contracts`).
- Eski cron deposu geçişi (`jobId`, `schedule.cron`, üst düzey delivery/payload alanları, payload `provider`, basit `notify: true` webhook geri dönüş işleri).
- Oturum kilit dosyası incelemesi ve eski kilit temizliği.
- Durum bütünlüğü ve izin denetimleri (oturumlar, dökümler, durum dizini).
- Yerel çalışırken yapılandırma dosyası izin denetimleri (`chmod 600`).
- Model kimlik doğrulama sağlığı: OAuth süre sonunu denetler, süresi dolmak üzere olan belirteçleri yenileyebilir ve auth-profile cooldown/devre dışı durumlarını bildirir.
- Ek çalışma alanı dizini algılama (`~/openclaw`).
- Sandbox etkin olduğunda sandbox image onarımı.
- Eski hizmet geçişi ve ek gateway algılama.
- Matrix kanalı eski durum geçişi (`--fix` / `--repair` kipinde).
- Gateway çalışma zamanı denetimleri (hizmet kurulu ama çalışmıyor; önbelleğe alınmış launchd etiketi).
- Kanal durum uyarıları (çalışan gateway'den yoklanır).
- Supervisor yapılandırma denetimi (launchd/systemd/schtasks) ve isteğe bağlı onarım.
- Gateway çalışma zamanı en iyi uygulama denetimleri (Node ve Bun, sürüm yöneticisi yolları).
- Gateway port çakışması tanılaması (varsayılan `18789`).
- Açık DM ilkeleri için güvenlik uyarıları.
- Yerel belirteç kipi için gateway kimlik doğrulama denetimleri (belirteç kaynağı yoksa belirteç üretmeyi önerir; belirteç SecretRef yapılandırmalarının üzerine yazmaz).
- Linux'ta systemd linger denetimi.
- Çalışma alanı bootstrap dosyası boyut denetimi (bağlam dosyaları için kesme/sınıra yakın uyarılar).
- Shell completion durum denetimi ve otomatik kurulum/yükseltme.
- Bellek araması embedding sağlayıcısı hazırlık denetimi (yerel model, uzak API anahtarı veya QMD ikilisi).
- Kaynak kurulum denetimleri (pnpm çalışma alanı uyumsuzluğu, eksik UI varlıkları, eksik tsx ikilisi).
- Güncellenmiş yapılandırma + sihirbaz meta verisi yazar.

## Ayrıntılı davranış ve gerekçe

### 0) İsteğe bağlı güncelleme (git kurulumları)

Bu bir git checkout ise ve doctor etkileşimli olarak çalışıyorsa, doctor'ı çalıştırmadan önce
güncelleme (fetch/rebase/build) yapmayı önerir.

### 1) Yapılandırma normalleştirme

Yapılandırma eski değer biçimleri içeriyorsa (örneğin `messages.ackReaction`
kanala özgü geçersiz kılma olmadan), doctor bunları mevcut
şemaya normalleştirir.

Buna eski Talk düz alanları da dahildir. Geçerli genel Talk yapılandırması
`talk.provider` + `talk.providers.<provider>` şeklindedir. Doctor eski
`talk.voiceId` / `talk.voiceAliases` / `talk.modelId` / `talk.outputFormat` /
`talk.apiKey` biçimlerini sağlayıcı eşlemine yeniden yazar.

### 2) Eski yapılandırma anahtarı geçişleri

Yapılandırma kullanım dışı anahtarlar içerdiğinde, diğer komutlar çalışmayı reddeder ve
sizden `openclaw doctor` çalıştırmanızı ister.

Doctor şunları yapar:

- Hangi eski anahtarların bulunduğunu açıklar.
- Uyguladığı geçişi gösterir.
- `~/.openclaw/openclaw.json` dosyasını güncellenmiş şemayla yeniden yazar.

Gateway de eski bir
yapılandırma biçimi algıladığında başlangıçta doctor geçişlerini otomatik çalıştırır; böylece eski yapılandırmalar el ile müdahale olmadan onarılır.
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
- Adlandırılmış `accounts` içeren kanallarda tek hesaplı üst düzey kanal değerleri kaldıysa, bu hesap kapsamlı değerleri o kanal için seçilen yükseltilmiş hesaba taşı (`accounts.default` çoğu kanal için; Matrix mevcut eşleşen adlı/varsayılan hedefi koruyabilir)
- `identity` → `agents.list[].identity`
- `agent.*` → `agents.defaults` + `tools.*` (tools/elevated/exec/sandbox/subagents)
- `agent.model`/`allowedModels`/`modelAliases`/`modelFallbacks`/`imageModelFallbacks`
  → `agents.defaults.models` + `agents.defaults.model.primary/fallbacks` + `agents.defaults.imageModel.primary/fallbacks`
- `browser.ssrfPolicy.allowPrivateNetwork` → `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork`
- `browser.profiles.*.driver: "extension"` → `"existing-session"`
- `browser.relayBindHost` kaldırılır (eski extension relay ayarı)

Doctor uyarıları ayrıca çok hesaplı kanallar için hesap varsayılanı rehberliği de içerir:

- `channels.<channel>.accounts` içinde iki veya daha fazla girdi yapılandırılmışsa ancak `channels.<channel>.defaultAccount` veya `accounts.default` yoksa, doctor geri dönüş yönlendirmesinin beklenmeyen bir hesap seçebileceği konusunda uyarır.
- `channels.<channel>.defaultAccount` bilinmeyen bir hesap kimliğine ayarlanmışsa, doctor uyarır ve yapılandırılmış hesap kimliklerini listeler.

### 2b) OpenCode sağlayıcı geçersiz kılmaları

`models.providers.opencode`, `opencode-zen` veya `opencode-go`
öğelerini el ile eklediyseniz, bu `@mariozechner/pi-ai` içindeki yerleşik OpenCode kataloğunu geçersiz kılar.
Bu, modelleri yanlış API'ye zorlayabilir veya maliyetleri sıfırlayabilir. Doctor, geçersiz kılmayı kaldırıp model başına API yönlendirmesini + maliyetleri geri yükleyebilmeniz için uyarır.

### 2c) Browser geçişi ve Chrome MCP hazırlığı

Browser yapılandırmanız hâlâ kaldırılmış Chrome extension yolunu gösteriyorsa, doctor
onu mevcut host-local Chrome MCP bağlanma modeline normalleştirir:

- `browser.profiles.*.driver: "extension"` → `"existing-session"`
- `browser.relayBindHost` kaldırılır

Doctor ayrıca `defaultProfile:
"user"` veya yapılandırılmış bir `existing-session` profili kullandığınızda host-local Chrome MCP yolunu denetler:

- varsayılan
  otomatik bağlanma profilleri için Google Chrome'un aynı host üzerinde kurulu olup olmadığını denetler
- algılanan Chrome sürümünü denetler ve Chrome 144'ün altındaysa uyarır
- tarayıcı inceleme sayfasında uzak hata ayıklamayı etkinleştirmenizi hatırlatır (örneğin `chrome://inspect/#remote-debugging`, `brave://inspect/#remote-debugging`,
  veya `edge://inspect/#remote-debugging`)

Doctor Chrome tarafındaki ayarı sizin yerinize etkinleştiremez. Host-local Chrome MCP
hâlâ şunları gerektirir:

- gateway/node host üzerinde Chromium tabanlı 144+ bir tarayıcı
- tarayıcının yerel olarak çalışıyor olması
- bu tarayıcıda uzak hata ayıklamanın etkin olması
- tarayıcıdaki ilk bağlanma onay isteminin kabul edilmesi

Buradaki hazırlık yalnızca yerel bağlanma önkoşullarıyla ilgilidir. Existing-session, mevcut Chrome MCP rota sınırlarını korur; `responsebody`, PDF dışa aktarma, indirme yakalama ve toplu eylemler gibi gelişmiş rotalar hâlâ yönetilen
browser veya ham CDP profili gerektirir.

Bu denetim Docker, sandbox, remote-browser veya diğer
headless akışlara **uygulanmaz**. Bunlar ham CDP kullanmaya devam eder.

### 2d) OAuth TLS önkoşulları

Bir OpenAI Codex OAuth profili yapılandırıldığında doctor, yerel Node/OpenSSL TLS yığınının
sertifika zincirini doğrulayabildiğini doğrulamak için OpenAI
yetkilendirme uç noktasını yoklar. Yoklama bir sertifika hatasıyla başarısız olursa (örneğin
`UNABLE_TO_GET_ISSUER_CERT_LOCALLY`, süresi dolmuş sertifika veya kendi imzaladığı sertifika),
doctor platforma özgü çözüm rehberini yazdırır. Homebrew Node kullanan macOS'ta çözüm
genellikle `brew postinstall ca-certificates` olur. `--deep` ile, gateway sağlıklı olsa bile yoklama çalışır.

### 3) Eski durum geçişleri (disk düzeni)

Doctor, eski disk düzenlerini mevcut yapıya taşıyabilir:

- Oturum deposu + dökümler:
  - `~/.openclaw/sessions/` konumundan `~/.openclaw/agents/<agentId>/sessions/` konumuna
- Agent dizini:
  - `~/.openclaw/agent/` konumundan `~/.openclaw/agents/<agentId>/agent/` konumuna
- WhatsApp kimlik doğrulama durumu (Baileys):
  - eski `~/.openclaw/credentials/*.json` konumundan (`oauth.json` hariç)
  - `~/.openclaw/credentials/whatsapp/<accountId>/...` konumuna (varsayılan hesap kimliği: `default`)

Bu geçişler en iyi çaba esasına dayanır ve idempotent'tir; doctor,
yedek olarak bıraktığı eski klasörler olduğunda uyarı verir. Gateway/CLI de
başlangıçta eski oturumlar + agent dizinini otomatik geçirir; böylece geçmiş/kimlik doğrulama/modeller el ile doctor çalıştırmadan agent başına yola taşınır. WhatsApp kimlik doğrulaması özellikle yalnızca `openclaw doctor` aracılığıyla taşınır. Talk sağlayıcısı/sağlayıcı haritası normalleştirmesi artık
yapısal eşitliğe göre karşılaştırır; bu nedenle yalnızca anahtar sırası farklarından kaynaklanan farklar artık tekrarlanan etkisiz `doctor --fix` değişikliklerini tetiklemez.

### 3a) Eski plugin manifest geçişleri

Doctor, kurulu tüm plugin manifest dosyalarını kullanım dışı üst düzey yetenek
anahtarları için tarar (`speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`,
`webSearchProviders`). Bulduğunda, bunları `contracts`
nesnesine taşımayı ve manifest dosyasını yerinde yeniden yazmayı önerir. Bu geçiş idempotent'tir;
`contracts` anahtarı zaten aynı değerlere sahipse, eski anahtar veriyi çoğaltmadan
kaldırılır.

### 3b) Eski cron deposu geçişleri

Doctor ayrıca cron iş deposunu (`~/.openclaw/cron/jobs.json` varsayılan olarak,
veya geçersiz kılındığında `cron.store`) planlayıcının uyumluluk için hâlâ
kabul ettiği eski iş biçimleri açısından denetler.

Geçerli cron temizlemeleri şunları içerir:

- `jobId` → `id`
- `schedule.cron` → `schedule.expr`
- üst düzey payload alanları (`message`, `model`, `thinking`, ...) → `payload`
- üst düzey delivery alanları (`deliver`, `channel`, `to`, `provider`, ...) → `delivery`
- payload `provider` delivery takma adları → açık `delivery.channel`
- basit eski `notify: true` webhook geri dönüş işleri → açık `delivery.mode="webhook"` ve `delivery.to=cron.webhook`

Doctor `notify: true` işlerini yalnızca bunu davranışı
değiştirmeden yapabildiğinde otomatik geçirir. Bir iş, eski notify geri dönüşünü mevcut
webhook olmayan bir delivery kipiyle birleştiriyorsa, doctor uyarır ve o işi el ile inceleme için bırakır.

### 3c) Oturum kilidi temizliği

Doctor, anormal çıkan bir oturum tarafından geride bırakılan
yazma kilit dosyaları için her agent oturum dizinini tarar. Bulunan her kilit dosyası için şunları bildirir:
yol, PID, PID'nin hâlâ canlı olup olmadığı, kilit yaşı ve
eski kabul edilip edilmediği (ölü PID veya 30 dakikadan eski). `--fix` / `--repair`
kipinde eski kilit dosyalarını otomatik kaldırır; aksi takdirde bir not yazdırır ve
`--fix` ile yeniden çalıştırmanızı söyler.

### 4) Durum bütünlüğü denetimleri (oturum kalıcılığı, yönlendirme ve güvenlik)

Durum dizini operasyonel omurilik gibidir. Kaybolursa
oturumları, kimlik bilgilerini, günlükleri ve yapılandırmayı kaybedersiniz (başka yerde yedekleriniz yoksa).

Doctor şunları denetler:

- **Durum dizini eksik**: yıkıcı durum kaybı konusunda uyarır, dizini yeniden oluşturmayı önerir
  ve eksik verileri kurtaramayacağını hatırlatır.
- **Durum dizini izinleri**: yazılabilirliği doğrular; izinleri onarmayı önerir
  (sahip/grup uyumsuzluğu algılanırsa `chown` ipucu da verir).
- **macOS bulut eşzamanlı durum dizini**: durum iCloud Drive
  (`~/Library/Mobile Documents/com~apple~CloudDocs/...`) veya
  `~/Library/CloudStorage/...` altında çözülürse uyarır; çünkü eşzamanlama destekli yollar daha yavaş G/Ç'ye
  ve kilit/eşzamanlama yarışlarına neden olabilir.
- **Linux SD veya eMMC durum dizini**: durum bir `mmcblk*`
  bağlama kaynağına çözülürse uyarır; çünkü SD veya eMMC destekli rastgele G/Ç
  oturum ve kimlik bilgisi yazımları altında daha yavaş olabilir ve daha hızlı yıpranabilir.
- **Oturum dizinleri eksik**: `sessions/` ve oturum deposu dizini,
  geçmişi kalıcı kılmak ve `ENOENT` çöküşlerini önlemek için gereklidir.
- **Döküm uyumsuzluğu**: son oturum girdilerinde eksik
  döküm dosyaları varsa uyarır.
- **Ana oturum “tek satırlı JSONL”**: ana döküm yalnızca tek satır içeriyorsa
  işaretler (geçmiş birikmiyor demektir).
- **Birden fazla durum dizini**: birden fazla `~/.openclaw` klasörü farklı
  ana dizinlerde bulunduğunda veya `OPENCLAW_STATE_DIR` başka bir yere işaret ettiğinde uyarır (geçmiş kurulumlar arasında bölünebilir).
- **Uzak kip hatırlatması**: `gateway.mode=remote` ise doctor bunu
  uzak host üzerinde çalıştırmanızı hatırlatır (durum orada yaşar).
- **Yapılandırma dosyası izinleri**: `~/.openclaw/openclaw.json` dosyası
  grup/herkes tarafından okunabiliyorsa uyarır ve `600` olarak sıkılaştırmayı önerir.

### 5) Model kimlik doğrulama sağlığı (OAuth süre sonu)

Doctor, kimlik doğrulama deposundaki OAuth profillerini inceler, belirteçlerin
süresi dolmak üzereyse/dolmuşsa uyarır ve güvenliyse bunları yenileyebilir. Anthropic
OAuth/belirteç profili eskiyse, Anthropic API anahtarı veya eski
Anthropic setup-token yolunu önerir.
Yenileme istemleri yalnızca etkileşimli (TTY) çalışırken görünür; `--non-interactive`
yenileme denemelerini atlar.

Doctor ayrıca eski kaldırılmış Anthropic Claude CLI durumunu da algılar. Eski
`anthropic:claude-cli` kimlik bilgisi baytları hâlâ `auth-profiles.json` içinde varsa,
doctor bunları yeniden Anthropic belirteç/OAuth profillerine dönüştürür ve eski
`claude-cli/...` model başvurularını yeniden yazar.
Baytlar yoksa, doctor eski yapılandırmayı kaldırır ve bunun yerine kurtarma
komutlarını yazdırır.

Doctor ayrıca şu nedenlerle geçici olarak kullanılamayan auth profillerini de bildirir:

- kısa cooldown'lar (oran sınırları/zaman aşımları/kimlik doğrulama hataları)
- daha uzun devre dışı bırakmalar (faturalandırma/kredi hataları)

### 6) Hooks model doğrulaması

`hooks.gmail.model` ayarlanmışsa doctor model başvurusunu katalog ve izin listesine göre doğrular ve çözümlenmeyecekse veya izin verilmiyorsa uyarır.

### 7) Sandbox image onarımı

Sandbox etkin olduğunda doctor Docker image'larını denetler ve
geçerli image eksikse oluşturmayı veya eski adlara geçmeyi önerir.

### 7b) Paketlenmiş plugin çalışma zamanı bağımlılıkları

Doctor, paketlenmiş plugin çalışma zamanı bağımlılıklarının (örneğin
Discord plugin çalışma zamanı paketleri) OpenClaw kurulum kökünde bulunduğunu doğrular.
Herhangi biri eksikse, doctor paketleri bildirir ve
`openclaw doctor --fix` / `openclaw doctor --repair` kipinde bunları kurar.

### 8) Gateway hizmet geçişleri ve temizlik ipuçları

Doctor eski gateway hizmetlerini (launchd/systemd/schtasks) algılar ve
bunları kaldırıp OpenClaw hizmetini mevcut gateway
portunu kullanarak kurmayı önerir. Ayrıca ek gateway benzeri hizmetleri tarayabilir ve temizlik ipuçları yazdırabilir.
Profil adlandırılmış OpenClaw gateway hizmetleri birinci sınıf kabul edilir ve "ek" olarak işaretlenmez.

### 8b) Başlangıç Matrix geçişi

Bir Matrix kanal hesabında bekleyen veya uygulanabilir eski durum geçişi olduğunda,
doctor (`--fix` / `--repair` kipinde) geçiş öncesi bir anlık görüntü oluşturur ve ardından
en iyi çaba geçiş adımlarını çalıştırır: eski Matrix durum geçişi ve eski
şifreli durum hazırlığı. Her iki adım da ölümcül değildir; hatalar günlüğe kaydedilir ve
başlangıç devam eder. Salt okunur kipte (`--fix` olmadan `openclaw doctor`) bu denetim
tamamen atlanır.

### 9) Güvenlik uyarıları

Doctor, bir sağlayıcı izin listesi olmadan DM'lere açıksa veya
bir ilke tehlikeli biçimde yapılandırılmışsa uyarılar verir.

### 10) systemd linger (Linux)

Bir systemd kullanıcı hizmeti olarak çalışıyorsa doctor,
oturum kapatıldıktan sonra gateway'in canlı kalması için lingering'in etkin olduğunu doğrular.

### 11) Çalışma alanı durumu (Skills, plugin'ler ve eski dizinler)

Doctor, varsayılan agent için çalışma alanı durumunun bir özetini yazdırır:

- **Skills durumu**: uygun, gereksinimi eksik ve izin listesi tarafından engellenmiş skill sayılarını verir.
- **Eski çalışma alanı dizinleri**: `~/openclaw` veya diğer eski çalışma alanı dizinleri
  mevcut çalışma alanının yanında bulunuyorsa uyarır.
- **Plugin durumu**: yüklenen/devre dışı/hata veren plugin sayılarını verir; herhangi bir
  hata için plugin kimliklerini listeler; bundle plugin yeteneklerini bildirir.
- **Plugin uyumluluk uyarıları**: mevcut çalışma zamanı ile uyumluluk sorunu olan
  plugin'leri işaretler.
- **Plugin tanılamaları**: plugin registry tarafından
  yükleme zamanında üretilen uyarıları veya hataları gösterir.

### 11b) Bootstrap dosya boyutu

Doctor, çalışma alanı bootstrap dosyalarının (`AGENTS.md`,
`CLAUDE.md` veya diğer enjekte edilen bağlam dosyaları gibi) yapılandırılmış
karakter bütçesine yakın veya onun üzerinde olup olmadığını denetler. Dosya başına ham ve enjekte edilen karakter sayılarını, kesme
yüzdesini, kesme nedenini (`max/file` veya `max/total`) ve toplam enjekte edilen
karakterleri toplam bütçenin bir kesri olarak bildirir. Dosyalar kesildiğinde veya sınıra yaklaştığında, doctor `agents.defaults.bootstrapMaxChars`
ve `agents.defaults.bootstrapTotalMaxChars` ayarları için iyileştirme ipuçları yazdırır.

### 11c) Shell completion

Doctor, mevcut shell için
(zsh, bash, fish veya PowerShell) sekme tamamlamasının kurulu olup olmadığını denetler:

- Shell profili yavaş bir dinamik tamamlama kalıbı kullanıyorsa
  (`source <(openclaw completion ...)`), doctor bunu daha hızlı
  önbellek dosyası varyantına yükseltir.
- Completion profil içinde yapılandırılmış ancak önbellek dosyası eksikse,
  doctor önbelleği otomatik olarak yeniden üretir.
- Hiç completion yapılandırılmamışsa, doctor
  kurmayı önerir (yalnızca etkileşimli kipte; `--non-interactive` ile atlanır).

Önbelleği el ile yeniden üretmek için `openclaw completion --write-state` çalıştırın.

### 12) Gateway kimlik doğrulama denetimleri (yerel belirteç)

Doctor, yerel gateway belirteç kimlik doğrulaması hazırlığını denetler.

- Belirteç kipi bir belirteç gerektiriyor ve belirteç kaynağı yoksa, doctor bir tane üretmeyi önerir.
- `gateway.auth.token` SecretRef tarafından yönetiliyor ancak kullanılamıyorsa, doctor uyarır ve üzerine düz metin yazmaz.
- `openclaw doctor --generate-gateway-token`, yalnızca belirteç SecretRef yapılandırılmamışsa üretimi zorlar.

### 12b) Salt okunur SecretRef farkındalığına sahip onarımlar

Bazı onarım akışlarının, çalışma zamanındaki hızlı başarısız olma davranışını zayıflatmadan yapılandırılmış kimlik bilgilerini incelemesi gerekir.

- `openclaw doctor --fix`, hedefli yapılandırma onarımları için artık durum ailesi komutlarıyla aynı salt okunur SecretRef özet modelini kullanır.
- Örnek: Telegram `allowFrom` / `groupAllowFrom` `@username` onarımı, varsa yapılandırılmış bot kimlik bilgilerini kullanmayı dener.
- Telegram bot belirteci SecretRef üzerinden yapılandırılmış ancak mevcut komut yolunda kullanılamıyorsa, doctor kimlik bilgisinin yapılandırılmış-ama-kullanılamaz olduğunu bildirir ve çökme veya belirteci eksikmiş gibi yanlış bildirme yerine otomatik çözümlemeyi atlar.

### 13) Gateway sağlık denetimi + yeniden başlatma

Doctor, bir sağlık denetimi çalıştırır ve gateway sağlıksız görünüyorsa
yeniden başlatmayı önerir.

### 13b) Bellek araması hazırlığı

Doctor, yapılandırılmış bellek araması embedding sağlayıcısının varsayılan
agent için hazır olup olmadığını denetler. Davranış, yapılandırılmış backend ve sağlayıcıya bağlıdır:

- **QMD backend**: `qmd` ikilisinin kullanılabilir ve başlatılabilir olup olmadığını yoklar.
  Değilse, npm paketi ve el ile ikili yol seçeneği dahil olmak üzere düzeltme rehberi yazdırır.
- **Açık yerel sağlayıcı**: yerel model dosyasını veya tanınan bir
  uzak/indirilebilir model URL'sini denetler. Eksikse, uzak sağlayıcıya geçmeyi önerir.
- **Açık uzak sağlayıcı** (`openai`, `voyage` vb.): ortamda veya kimlik doğrulama deposunda bir API anahtarının
  mevcut olduğunu doğrular. Eksikse uygulanabilir düzeltme ipuçları yazdırır.
- **Otomatik sağlayıcı**: önce yerel model kullanılabilirliğini denetler, sonra her uzak
  sağlayıcıyı otomatik seçim sırasına göre dener.

Bir gateway yoklama sonucu mevcut olduğunda (denetim sırasında gateway sağlıklıysa),
doctor sonucunu CLI tarafından görülebilen yapılandırmayla çapraz doğrular ve
herhangi bir uyuşmazlığı not eder.

Çalışma zamanında embedding hazırlığını doğrulamak için `openclaw memory status --deep` kullanın.

### 14) Kanal durum uyarıları

Gateway sağlıklıysa doctor bir kanal durumu yoklaması çalıştırır ve
önerilen düzeltmelerle birlikte uyarıları bildirir.

### 15) Supervisor yapılandırma denetimi + onarım

Doctor, kurulu supervisor yapılandırmasını (launchd/systemd/schtasks)
eksik veya güncel olmayan varsayılanlar açısından denetler (örn. systemd network-online bağımlılıkları ve
yeniden başlatma gecikmesi). Bir uyumsuzluk bulduğunda, güncelleme önerir ve
hizmet dosyasını/görevi mevcut varsayılanlara göre yeniden yazabilir.

Notlar:

- `openclaw doctor`, supervisor yapılandırmasını yeniden yazmadan önce sorar.
- `openclaw doctor --yes`, varsayılan onarım istemlerini kabul eder.
- `openclaw doctor --repair`, önerilen düzeltmeleri istem olmadan uygular.
- `openclaw doctor --repair --force`, özel supervisor yapılandırmalarının üzerine yazar.
- Belirteç kimlik doğrulaması bir belirteç gerektiriyorsa ve `gateway.auth.token` SecretRef tarafından yönetiliyorsa, doctor hizmet kurulum/onarı mı SecretRef'i doğrular ancak çözümlenmiş düz metin belirteç değerlerini supervisor hizmet ortam meta verisine kalıcı yazmaz.
- Belirteç kimlik doğrulaması bir belirteç gerektiriyorsa ve yapılandırılmış belirteç SecretRef'i çözümlenmemişse, doctor kurulum/onarı m yolunu uygulanabilir rehberlikle engeller.
- Hem `gateway.auth.token` hem de `gateway.auth.password` yapılandırılmışsa ve `gateway.auth.mode` ayarlanmamışsa, doctor kip açıkça ayarlanana kadar kurulum/onarı mı engeller.
- Linux kullanıcı-systemd birimleri için doctor belirteç sapma denetimleri artık hizmet kimlik doğrulama meta verisini karşılaştırırken hem `Environment=` hem de `EnvironmentFile=` kaynaklarını içerir.
- Her zaman `openclaw gateway install --force` ile tam yeniden yazımı zorlayabilirsiniz.

### 16) Gateway çalışma zamanı + port tanılamaları

Doctor, hizmet çalışma zamanını (PID, son çıkış durumu) inceler ve
hizmet kurulu olduğu halde gerçekten çalışmıyorsa uyarır. Ayrıca gateway portunda
(varsayılan `18789`) port çakışmalarını denetler ve olası nedenleri bildirir (gateway zaten
çalışıyor, SSH tüneli).

### 17) Gateway çalışma zamanı en iyi uygulamaları

Doctor, gateway hizmeti Bun üzerinde veya sürüm yöneticili bir Node yolu
(`nvm`, `fnm`, `volta`, `asdf` vb.) üzerinde çalışıyorsa uyarır. WhatsApp + Telegram kanalları Node gerektirir,
ve sürüm yöneticisi yolları yükseltmelerden sonra bozulabilir; çünkü hizmet shell başlangıcınızı
yüklemez. Doctor, mevcut olduğunda sistem Node kurulumuna geçmeyi önerir
(Homebrew/apt/choco).

### 18) Yapılandırma yazımı + sihirbaz meta verisi

Doctor, tüm yapılandırma değişikliklerini kalıcı yazar ve
doctor çalıştırmasını kaydetmek için sihirbaz meta verisini damgalar.

### 19) Çalışma alanı ipuçları (yedekleme + bellek sistemi)

Doctor, eksikse bir çalışma alanı bellek sistemi önerir ve çalışma alanı henüz git altında değilse
bir yedekleme ipucu yazdırır.

Çalışma alanı yapısı ve git yedeklemesi (önerilen özel GitHub veya GitLab) için tam rehber adına bkz.
[/concepts/agent-workspace](/tr/concepts/agent-workspace).
