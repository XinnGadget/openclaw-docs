---
read_when:
    - Sorun giderme merkezi sizi daha derin tanılama için buraya yönlendirdiğinde
    - Belirti temelli kararlı çalışma kitabı bölümlerine ve tam komutlara ihtiyaç duyduğunuzda
summary: Gateway, kanallar, otomasyon, düğümler ve tarayıcı için ayrıntılı sorun giderme çalışma kitabı
title: Sorun Giderme
x-i18n:
    generated_at: "2026-04-08T02:15:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: 02c9537845248db0c9d315bf581338a93215fe6fe3688ed96c7105cbb19fe6ba
    source_path: gateway/troubleshooting.md
    workflow: 15
---

# Gateway sorun giderme

Bu sayfa ayrıntılı çalışma kitabıdır.
Önce hızlı triyaj akışını istiyorsanız [/help/troubleshooting](/tr/help/troubleshooting) sayfasından başlayın.

## Komut sıralaması

Bunları önce, şu sırayla çalıştırın:

```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
openclaw channels status --probe
```

Beklenen sağlıklı sinyaller:

- `openclaw gateway status`, `Runtime: running` ve `RPC probe: ok` gösterir.
- `openclaw doctor`, engelleyici yapılandırma/hizmet sorunu olmadığını bildirir.
- `openclaw channels status --probe`, hesap başına canlı taşıma durumu ve,
  desteklenen yerlerde `works` veya `audit ok` gibi probe/denetim sonuçlarını gösterir.

## Uzun bağlam için Anthropic 429 ek kullanım gerekli

Günlükler/hatalar şunu içerdiğinde bunu kullanın:
`HTTP 429: rate_limit_error: Extra usage is required for long context requests`.

```bash
openclaw logs --follow
openclaw models status
openclaw config get agents.defaults.models
```

Şunlara bakın:

- Seçilen Anthropic Opus/Sonnet modelinde `params.context1m: true` var.
- Mevcut Anthropic kimlik bilgileri, uzun bağlam kullanımı için uygun değil.
- İstekler yalnızca 1M beta yoluna ihtiyaç duyan uzun oturumlarda/model çalıştırmalarında başarısız oluyor.

Düzeltme seçenekleri:

1. Normal bağlam penceresine dönmek için o modelde `context1m` ayarını devre dışı bırakın.
2. Uzun bağlam istekleri için uygun bir Anthropic kimlik bilgisi kullanın veya Anthropic API anahtarına geçin.
3. Anthropic uzun bağlam istekleri reddedildiğinde çalıştırmaların devam etmesi için fallback modeller yapılandırın.

İlgili:

- [/providers/anthropic](/tr/providers/anthropic)
- [/reference/token-use](/tr/reference/token-use)
- [/help/faq#why-am-i-seeing-http-429-ratelimiterror-from-anthropic](/tr/help/faq#why-am-i-seeing-http-429-ratelimiterror-from-anthropic)

## Yerel OpenAI uyumlu arka uç doğrudan probe'ları geçiyor ama ajan çalıştırmaları başarısız oluyor

Şu durumlarda bunu kullanın:

- `curl ... /v1/models` çalışıyor
- küçük doğrudan `/v1/chat/completions` çağrıları çalışıyor
- OpenClaw model çalıştırmaları yalnızca normal ajan dönüşlerinde başarısız oluyor

```bash
curl http://127.0.0.1:1234/v1/models
curl http://127.0.0.1:1234/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"model":"<id>","messages":[{"role":"user","content":"hi"}],"stream":false}'
openclaw infer model run --model <provider/model> --prompt "hi" --json
openclaw logs --follow
```

Şunlara bakın:

- doğrudan küçük çağrılar başarılı oluyor, ancak OpenClaw çalıştırmaları yalnızca daha büyük istemlerde başarısız oluyor
- arka uçta `messages[].content` alanının bir dize beklediğine dair hatalar
- yalnızca daha büyük istem token sayılarında veya tam ajan çalışma zamanı istemlerinde görülen arka uç çökmeleri

Yaygın imzalar:

- `messages[...].content: invalid type: sequence, expected a string` → arka uç
  yapılandırılmış Chat Completions içerik parçalarını reddediyor. Düzeltme: şunu ayarlayın
  `models.providers.<provider>.models[].compat.requiresStringContent: true`.
- doğrudan küçük istekler başarılı oluyor, ancak OpenClaw ajan çalıştırmaları arka uç/model
  çökmeleriyle başarısız oluyor (örneğin bazı `inferrs` derlemelerinde Gemma) → OpenClaw taşıması
  büyük olasılıkla zaten doğru; arka uç daha büyük ajan çalışma zamanı
  istem şekliyle başarısız oluyor.
- araçlar devre dışı bırakıldıktan sonra hatalar azalıyor ama kaybolmuyor → araç şemaları
  baskının bir parçasıydı, ancak kalan sorun hâlâ yukarı akış model/sunucu
  kapasitesi veya bir arka uç hatası.

Düzeltme seçenekleri:

1. Yalnızca dize kabul eden Chat Completions arka uçları için `compat.requiresStringContent: true` ayarlayın.
2. OpenClaw'ın araç şeması yüzeyini güvenilir şekilde işleyemeyen model/arka uçlar için `compat.supportsTools: false` ayarlayın.
3. Mümkün olan yerlerde istem baskısını azaltın: daha küçük workspace bootstrap, daha kısa
   oturum geçmişi, daha hafif yerel model veya daha güçlü uzun bağlam
   desteğine sahip bir arka uç.
4. Doğrudan küçük istekler geçmeye devam ederken OpenClaw ajan dönüşleri arka uç içinde
   çökmeye devam ediyorsa, bunu yukarı akış sunucu/model sınırlaması olarak değerlendirin ve
   kabul edilen payload şekliyle oraya yeniden üretim raporu gönderin.

İlgili:

- [/gateway/local-models](/tr/gateway/local-models)
- [/gateway/configuration#models](/tr/gateway/configuration#models)
- [/gateway/configuration-reference#openai-compatible-endpoints](/tr/gateway/configuration-reference#openai-compatible-endpoints)

## Yanıt yok

Kanallar çalışır durumdaysa ama hiçbir şey yanıt vermiyorsa, bir şeyi yeniden bağlamadan önce yönlendirme ve politikayı kontrol edin.

```bash
openclaw status
openclaw channels status --probe
openclaw pairing list --channel <channel> [--account <id>]
openclaw config get channels
openclaw logs --follow
```

Şunlara bakın:

- DM gönderenleri için eşleştirme beklemede.
- Grup bahsetme kapısı (`requireMention`, `mentionPatterns`).
- Kanal/grup izin listesi uyumsuzlukları.

Yaygın imzalar:

- `drop guild message (mention required` → grup mesajı, bahsetme olana kadar yok sayılır.
- `pairing request` → gönderenin onaya ihtiyacı var.
- `blocked` / `allowlist` → gönderen/kanal politika tarafından filtrelendi.

İlgili:

- [/channels/troubleshooting](/tr/channels/troubleshooting)
- [/channels/pairing](/tr/channels/pairing)
- [/channels/groups](/tr/channels/groups)

## Dashboard control ui bağlantısı

Dashboard/control UI bağlanmıyorsa, URL'yi, kimlik doğrulama modunu ve güvenli bağlam varsayımlarını doğrulayın.

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --json
```

Şunlara bakın:

- Doğru probe URL'si ve dashboard URL'si.
- İstemci ile gateway arasında kimlik doğrulama modu/token uyumsuzluğu.
- Aygıt kimliği gerektiği halde HTTP kullanımı.

Yaygın imzalar:

- `device identity required` → güvenli olmayan bağlam veya eksik aygıt kimlik doğrulaması.
- `origin not allowed` → tarayıcı `Origin` değeri `gateway.controlUi.allowedOrigins`
  içinde değil (veya açık bir
  allowlist olmadan loopback olmayan bir tarayıcı origin'inden bağlanıyorsunuz).
- `device nonce required` / `device nonce mismatch` → istemci meydan okumaya dayalı
  aygıt kimlik doğrulama akışını tamamlamıyor (`connect.challenge` + `device.nonce`).
- `device signature invalid` / `device signature expired` → istemci mevcut el sıkışma için
  yanlış payload'u (veya eski bir zaman damgasını) imzaladı.
- `AUTH_TOKEN_MISMATCH` ve `canRetryWithDeviceToken=true` → istemci önbelleğe alınmış aygıt token'ı ile bir kez güvenilir yeniden deneme yapabilir.
- Bu önbelleğe alınmış token yeniden denemesi, eşleştirilmiş
  aygıt token'ı ile saklanan önbelleğe alınmış kapsam kümesini yeniden kullanır. Açık `deviceToken` / açık `scopes` çağıranları bunun yerine
  istenen kapsam kümesini korur.
- Bu yeniden deneme yolunun dışında, bağlantı kimlik doğrulaması önceliği önce açık paylaşılan
  token/parola, sonra açık `deviceToken`, ardından saklanan aygıt token'ı,
  sonra bootstrap token'dır.
- Eşzamansız Tailscale Serve Control UI yolunda, aynı
  `{scope, ip}` için başarısız denemeler sınırlayıcı başarısızlığı kaydetmeden önce serileştirilir. Aynı istemciden iki kötü eşzamanlı yeniden deneme bu nedenle
  ikinci denemede iki düz uyumsuzluk yerine `retry later`
  gösterebilir.
- Bir tarayıcı origin'li loopback istemcisinden gelen `too many failed authentication attempts (retry later)` → aynı normalize edilmiş `Origin` kaynağından gelen tekrarlanan başarısızlıklar geçici olarak
  kilitlenir; başka bir localhost origin'i ayrı bir kova kullanır.
- Bu yeniden denemeden sonra tekrarlanan `unauthorized` → paylaşılan token/aygıt token'ı kayması; gerekirse token yapılandırmasını yenileyin ve aygıt token'ını yeniden onaylayın/döndürün.
- `gateway connect failed:` → yanlış ana makine/port/url hedefi.

### Kimlik doğrulama ayrıntı kodları hızlı eşleştirme

Sonraki adımı seçmek için başarısız `connect` yanıtındaki `error.details.code` değerini kullanın:

| Detail code                  | Anlamı                                                   | Önerilen işlem                                                                                                                                                                                                                                                                              |
| ---------------------------- | -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `AUTH_TOKEN_MISSING`         | İstemci gerekli paylaşılan token'ı göndermedi.           | İstemciye token'ı yapıştırın/ayarlayın ve yeniden deneyin. Dashboard yolları için: `openclaw config get gateway.auth.token` ardından bunu Control UI ayarlarına yapıştırın.                                                                                                                  |
| `AUTH_TOKEN_MISMATCH`        | Paylaşılan token, gateway auth token ile eşleşmedi.      | Eğer `canRetryWithDeviceToken=true` ise, tek bir güvenilir yeniden denemeye izin verin. Önbelleğe alınmış token yeniden denemeleri saklanan onaylı kapsamları yeniden kullanır. Açık `deviceToken` / `scopes` çağıranları istenen kapsamları korur. Hâlâ başarısızsa [token drift recovery checklist](/cli/devices#token-drift-recovery-checklist) çalıştırın. |
| `AUTH_DEVICE_TOKEN_MISMATCH` | Önbelleğe alınmış aygıt başına token eski veya iptal edilmiş. | [devices CLI](/cli/devices) kullanarak aygıt token'ını döndürün/yeniden onaylayın, ardından yeniden bağlanın.                                                                                                                                                                              |
| `PAIRING_REQUIRED`           | Aygıt kimliği biliniyor ama bu rol için onaylı değil.    | Bekleyen isteği onaylayın: `openclaw devices list` ardından `openclaw devices approve <requestId>`.                                                                                                                                                                                        |

Aygıt auth v2 geçiş denetimi:

```bash
openclaw --version
openclaw doctor
openclaw gateway status
```

Günlüklerde nonce/imza hataları görünüyorsa, bağlanan istemciyi güncelleyin ve şunları doğrulayın:

1. `connect.challenge` bekliyor
2. meydan okumaya bağlı payload'u imzalıyor
3. aynı challenge nonce ile `connect.params.device.nonce` gönderiyor

`openclaw devices rotate` / `revoke` / `remove` beklenmedik şekilde reddediliyorsa:

- eşleştirilmiş aygıt token oturumları yalnızca **kendi** aygıtlarını yönetebilir, çağıran ayrıca
  `operator.admin` iznine sahip değilse
- `openclaw devices rotate --scope ...` yalnızca çağıran oturumun zaten sahip olduğu operatör kapsamlarını
  isteyebilir

İlgili:

- [/web/control-ui](/web/control-ui)
- [/gateway/configuration](/tr/gateway/configuration) (gateway kimlik doğrulama modları)
- [/gateway/trusted-proxy-auth](/tr/gateway/trusted-proxy-auth)
- [/gateway/remote](/tr/gateway/remote)
- [/cli/devices](/cli/devices)

## Gateway hizmeti çalışmıyor

Hizmet kurulu olduğu halde süreç ayakta kalmıyorsa bunu kullanın.

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --deep   # sistem düzeyi hizmetleri de tarar
```

Şunlara bakın:

- Çıkış ipuçlarıyla birlikte `Runtime: stopped`.
- Hizmet yapılandırması uyuşmazlığı (`Config (cli)` ve `Config (service)`).
- Port/dinleyici çakışmaları.
- `--deep` kullanıldığında ek launchd/systemd/schtasks kurulumları.
- `Other gateway-like services detected (best effort)` temizleme ipuçları.

Yaygın imzalar:

- `Gateway start blocked: set gateway.mode=local` veya `existing config is missing gateway.mode` → yerel gateway modu etkin değil ya da yapılandırma dosyası bozuldu ve `gateway.mode` kayboldu. Düzeltme: yapılandırmanızda `gateway.mode="local"` ayarlayın veya beklenen yerel mod yapılandırmasını yeniden damgalamak için `openclaw onboard --mode local` / `openclaw setup` komutunu tekrar çalıştırın. OpenClaw'ı Podman ile çalıştırıyorsanız varsayılan yapılandırma yolu `~/.openclaw/openclaw.json` olur.
- `refusing to bind gateway ... without auth` → geçerli bir gateway auth yolu (token/parola veya yapılandırılmışsa trusted-proxy) olmadan loopback olmayan bind.
- `another gateway instance is already listening` / `EADDRINUSE` → port çakışması.
- `Other gateway-like services detected (best effort)` → eski veya paralel launchd/systemd/schtasks birimleri mevcut. Çoğu kurulum makine başına bir gateway kullanmalıdır; gerçekten birden fazla gerekiyorsa port + config/state/workspace ayırın. Bkz. [/gateway#multiple-gateways-same-host](/tr/gateway#multiple-gateways-same-host).

İlgili:

- [/gateway/background-process](/tr/gateway/background-process)
- [/gateway/configuration](/tr/gateway/configuration)
- [/gateway/doctor](/tr/gateway/doctor)

## Gateway probe uyarıları

`openclaw gateway probe` bir şeye ulaştığında ancak yine de bir uyarı bloğu yazdırdığında bunu kullanın.

```bash
openclaw gateway probe
openclaw gateway probe --json
openclaw gateway probe --ssh user@gateway-host
```

Şunlara bakın:

- JSON çıktısında `warnings[].code` ve `primaryTargetId`.
- Uyarının SSH fallback, birden fazla gateway, eksik kapsamlar veya çözümlenmemiş auth ref'leri hakkında olup olmadığı.

Yaygın imzalar:

- `SSH tunnel failed to start; falling back to direct probes.` → SSH kurulumu başarısız oldu, ancak komut yine de doğrudan yapılandırılmış/loopback hedeflerini denedi.
- `multiple reachable gateways detected` → birden fazla hedef yanıt verdi. Bu genellikle kasıtlı çoklu gateway kurulumu veya eski/çift dinleyiciler anlamına gelir.
- `Probe diagnostics are limited by gateway scopes (missing operator.read)` → bağlantı çalıştı, ancak ayrıntı RPC'si kapsamla sınırlı; aygıt kimliğini eşleştirin veya `operator.read` içeren kimlik bilgileri kullanın.
- çözümlenmemiş `gateway.auth.*` / `gateway.remote.*` SecretRef uyarı metni → başarısız hedef için bu komut yolunda auth materyali mevcut değildi.

İlgili:

- [/cli/gateway](/cli/gateway)
- [/gateway#multiple-gateways-same-host](/tr/gateway#multiple-gateways-same-host)
- [/gateway/remote](/tr/gateway/remote)

## Kanal bağlı ama mesajlar akmıyor

Kanal durumu bağlı olduğu halde mesaj akışı durmuşsa, politika, izinler ve kanala özgü teslim kurallarına odaklanın.

```bash
openclaw channels status --probe
openclaw pairing list --channel <channel> [--account <id>]
openclaw status --deep
openclaw logs --follow
openclaw config get channels
```

Şunlara bakın:

- DM politikası (`pairing`, `allowlist`, `open`, `disabled`).
- Grup izin listesi ve bahsetme gereksinimleri.
- Eksik kanal API izinleri/kapsamları.

Yaygın imzalar:

- `mention required` → mesaj grup bahsetme politikası nedeniyle yok sayıldı.
- `pairing` / bekleyen onay izleri → gönderen onaylanmış değil.
- `missing_scope`, `not_in_channel`, `Forbidden`, `401/403` → kanal auth/izin sorunu.

İlgili:

- [/channels/troubleshooting](/tr/channels/troubleshooting)
- [/channels/whatsapp](/tr/channels/whatsapp)
- [/channels/telegram](/tr/channels/telegram)
- [/channels/discord](/tr/channels/discord)

## Cron ve heartbeat teslimi

Cron veya heartbeat çalışmadıysa ya da teslim edilmediyse, önce zamanlayıcı durumunu, sonra teslim hedefini doğrulayın.

```bash
openclaw cron status
openclaw cron list
openclaw cron runs --id <jobId> --limit 20
openclaw system heartbeat last
openclaw logs --follow
```

Şunlara bakın:

- Cron etkin ve sonraki uyandırma mevcut.
- İş çalıştırma geçmişi durumu (`ok`, `skipped`, `error`).
- Heartbeat atlama nedenleri (`quiet-hours`, `requests-in-flight`, `alerts-disabled`, `empty-heartbeat-file`, `no-tasks-due`).

Yaygın imzalar:

- `cron: scheduler disabled; jobs will not run automatically` → cron devre dışı.
- `cron: timer tick failed` → zamanlayıcı tıkı başarısız oldu; dosya/günlük/çalışma zamanı hatalarını kontrol edin.
- `heartbeat skipped` ve `reason=quiet-hours` → etkin saatler penceresinin dışında.
- `heartbeat skipped` ve `reason=empty-heartbeat-file` → `HEARTBEAT.md` var ama yalnızca boş satırlar / markdown başlıkları içeriyor, bu yüzden OpenClaw model çağrısını atlıyor.
- `heartbeat skipped` ve `reason=no-tasks-due` → `HEARTBEAT.md` bir `tasks:` bloğu içeriyor, ancak bu tıkta görevlerin hiçbiri zamanı gelmiş değil.
- `heartbeat: unknown accountId` → heartbeat teslim hedefi için geçersiz hesap kimliği.
- `heartbeat skipped` ve `reason=dm-blocked` → heartbeat hedefi DM tarzı bir hedefe çözümlendi, ancak `agents.defaults.heartbeat.directPolicy` (veya ajan başına geçersiz kılma) `block` olarak ayarlı.

İlgili:

- [/automation/cron-jobs#troubleshooting](/tr/automation/cron-jobs#troubleshooting)
- [/automation/cron-jobs](/tr/automation/cron-jobs)
- [/gateway/heartbeat](/tr/gateway/heartbeat)

## Eşleştirilmiş düğüm aracı başarısız oluyor

Bir düğüm eşleştirilmiş olduğu halde araçlar başarısız oluyorsa, ön plan, izin ve onay durumunu ayrı ayrı inceleyin.

```bash
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
openclaw approvals get --node <idOrNameOrIp>
openclaw logs --follow
openclaw status
```

Şunlara bakın:

- Beklenen yeteneklerle düğüm çevrimiçi.
- Kamera/mikrofon/konum/ekran için işletim sistemi izinleri verilmiş.
- Exec onayları ve allowlist durumu.

Yaygın imzalar:

- `NODE_BACKGROUND_UNAVAILABLE` → düğüm uygulaması ön planda olmalı.
- `*_PERMISSION_REQUIRED` / `LOCATION_PERMISSION_REQUIRED` → eksik işletim sistemi izni.
- `SYSTEM_RUN_DENIED: approval required` → exec onayı bekliyor.
- `SYSTEM_RUN_DENIED: allowlist miss` → komut allowlist tarafından engellendi.

İlgili:

- [/nodes/troubleshooting](/tr/nodes/troubleshooting)
- [/nodes/index](/tr/nodes/index)
- [/tools/exec-approvals](/tr/tools/exec-approvals)

## Tarayıcı aracı başarısız oluyor

Gateway'in kendisi sağlıklı olsa bile tarayıcı aracı işlemleri başarısız olduğunda bunu kullanın.

```bash
openclaw browser status
openclaw browser start --browser-profile openclaw
openclaw browser profiles
openclaw logs --follow
openclaw doctor
```

Şunlara bakın:

- `plugins.allow` ayarlı mı ve `browser` içeriyor mu.
- Geçerli tarayıcı yürütülebilir yolu.
- CDP profil erişilebilirliği.
- `existing-session` / `user` profilleri için yerel Chrome kullanılabilirliği.

Yaygın imzalar:

- `unknown command "browser"` veya `unknown command 'browser'` → paketlenmiş browser eklentisi `plugins.allow` tarafından hariç tutulmuş.
- `browser.enabled=true` olduğu halde browser aracı eksik / kullanılamıyor → `plugins.allow`, `browser` eklentisini hariç tutuyor, bu yüzden eklenti hiç yüklenmedi.
- `Failed to start Chrome CDP on port` → tarayıcı süreci başlatılamadı.
- `browser.executablePath not found` → yapılandırılmış yol geçersiz.
- `browser.cdpUrl must be http(s) or ws(s)` → yapılandırılmış CDP URL'si `file:` veya `ftp:` gibi desteklenmeyen bir şema kullanıyor.
- `browser.cdpUrl has invalid port` → yapılandırılmış CDP URL'sinde hatalı veya aralık dışı bir port var.
- `No Chrome tabs found for profile="user"` → Chrome MCP attach profilinde açık yerel Chrome sekmesi yok.
- `Remote CDP for profile "<name>" is not reachable` → yapılandırılmış uzak CDP uç noktasına gateway ana makinesinden ulaşılamıyor.
- `Browser attachOnly is enabled ... not reachable` veya `Browser attachOnly is enabled and CDP websocket ... is not reachable` → attach-only profilinde erişilebilir hedef yok veya HTTP uç noktası yanıt verdi ama CDP WebSocket yine de açılamadı.
- `Playwright is not available in this gateway build; '<feature>' is unsupported.` → mevcut gateway kurulumunda tam Playwright paketi yok; ARIA anlık görüntüleri ve temel sayfa ekran görüntüleri yine de çalışabilir, ancak gezinme, AI anlık görüntüleri, CSS seçici öğe ekran görüntüleri ve PDF dışa aktarma kullanılamaz.
- `fullPage is not supported for element screenshots` → ekran görüntüsü isteği `--full-page` ile `--ref` veya `--element` seçeneklerini karıştırdı.
- `element screenshots are not supported for existing-session profiles; use ref from snapshot.` → Chrome MCP / `existing-session` ekran görüntüsü çağrılarında CSS `--element` değil, sayfa yakalama veya snapshot `--ref` kullanılmalıdır.
- `existing-session file uploads do not support element selectors; use ref/inputRef.` → Chrome MCP yükleme hook'ları CSS seçicileri değil, snapshot ref'lerini gerektirir.
- `existing-session file uploads currently support one file at a time.` → Chrome MCP profillerinde çağrı başına bir yükleme gönderin.
- `existing-session dialog handling does not support timeoutMs.` → Chrome MCP profillerindeki diyalog hook'ları zaman aşımı geçersiz kılmalarını desteklemez.
- `response body is not supported for existing-session profiles yet.` → `responsebody` hâlâ yönetilen bir tarayıcı veya ham CDP profili gerektirir.
- attach-only veya uzak CDP profillerinde eski viewport / dark-mode / locale / offline geçersiz kılmaları → tüm gateway'i yeniden başlatmadan etkin kontrol oturumunu kapatmak ve Playwright/CDP öykünme durumunu serbest bırakmak için `openclaw browser stop --browser-profile <name>` çalıştırın.

İlgili:

- [/tools/browser-linux-troubleshooting](/tr/tools/browser-linux-troubleshooting)
- [/tools/browser](/tr/tools/browser)

## Yükselttikten sonra bir şey aniden bozulduysa

Yükseltme sonrası bozulmaların çoğu yapılandırma kayması veya artık zorlanan daha katı varsayılanlardan kaynaklanır.

### 1) Auth ve URL override davranışı değişti

```bash
openclaw gateway status
openclaw config get gateway.mode
openclaw config get gateway.remote.url
openclaw config get gateway.auth.mode
```

Kontrol edilecekler:

- `gateway.mode=remote` ise CLI çağrıları uzak hedefi kullanıyor olabilir; yerel hizmetiniz ise düzgün olabilir.
- Açık `--url` çağrıları saklanan kimlik bilgilerine fallback yapmaz.

Yaygın imzalar:

- `gateway connect failed:` → yanlış URL hedefi.
- `unauthorized` → uç noktaya ulaşılıyor ama auth yanlış.

### 2) Bind ve auth korkulukları daha katı

```bash
openclaw config get gateway.bind
openclaw config get gateway.auth.mode
openclaw config get gateway.auth.token
openclaw gateway status
openclaw logs --follow
```

Kontrol edilecekler:

- Loopback olmayan bind'ler (`lan`, `tailnet`, `custom`) geçerli bir gateway auth yolu gerektirir: paylaşılan token/parola auth veya doğru yapılandırılmış loopback olmayan bir `trusted-proxy` dağıtımı.
- `gateway.token` gibi eski anahtarlar `gateway.auth.token` yerine geçmez.

Yaygın imzalar:

- `refusing to bind gateway ... without auth` → geçerli bir gateway auth yolu olmadan loopback olmayan bind.
- Çalışma zamanı çalışırken `RPC probe: failed` → gateway canlı ama mevcut auth/url ile erişilemiyor.

### 3) Eşleştirme ve aygıt kimliği durumu değişti

```bash
openclaw devices list
openclaw pairing list --channel <channel> [--account <id>]
openclaw logs --follow
openclaw doctor
```

Kontrol edilecekler:

- Dashboard/düğümler için bekleyen aygıt onayları.
- Politika veya kimlik değişikliklerinden sonra bekleyen DM eşleştirme onayları.

Yaygın imzalar:

- `device identity required` → aygıt auth karşılanmadı.
- `pairing required` → gönderen/aygıt onaylanmalıdır.

Denetimlerden sonra hizmet yapılandırması ve çalışma zamanı hâlâ uyuşmuyorsa, hizmet meta verilerini aynı profil/durum dizininden yeniden kurun:

```bash
openclaw gateway install --force
openclaw gateway restart
```

İlgili:

- [/gateway/pairing](/tr/gateway/pairing)
- [/gateway/authentication](/tr/gateway/authentication)
- [/gateway/background-process](/tr/gateway/background-process)
