---
read_when:
    - Sorun giderme merkezi sizi daha derin teşhis için buraya yönlendirdi
    - Tam komutlarla belirti tabanlı, kararlı çalışma kılavuzu bölümlerine ihtiyacınız var
summary: Gateway, kanallar, otomasyon, node'lar ve tarayıcı için derin sorun giderme çalışma kılavuzu
title: Sorun Giderme
x-i18n:
    generated_at: "2026-04-07T08:45:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: e0202e8858310a0bfc1c994cd37b01c3b2d6c73c8a74740094e92dc3c4c36729
    source_path: gateway/troubleshooting.md
    workflow: 15
---

# Gateway sorun giderme

Bu sayfa ayrıntılı çalışma kılavuzudur.
Önce hızlı triyaj akışını istiyorsanız [/help/troubleshooting](/tr/help/troubleshooting) ile başlayın.

## Komut merdiveni

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
- `openclaw channels status --probe`, canlı hesap başına taşıma durumunu ve
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

- Seçili Anthropic Opus/Sonnet modelinde `params.context1m: true` var.
- Geçerli Anthropic kimlik bilgisi uzun bağlam kullanımı için uygun değil.
- İstekler yalnızca 1M beta yoluna ihtiyaç duyan uzun oturumlarda/model çalıştırmalarında başarısız oluyor.

Düzeltme seçenekleri:

1. Normal bağlam penceresine geri dönmek için bu modelde `context1m` özelliğini devre dışı bırakın.
2. Uzun bağlam istekleri için uygun bir Anthropic kimlik bilgisi kullanın veya bir Anthropic API anahtarına geçin.
3. Anthropic uzun bağlam istekleri reddedildiğinde çalıştırmaların devam etmesi için yedek modeller yapılandırın.

İlgili:

- [/providers/anthropic](/tr/providers/anthropic)
- [/reference/token-use](/tr/reference/token-use)
- [/help/faq#why-am-i-seeing-http-429-ratelimiterror-from-anthropic](/tr/help/faq#why-am-i-seeing-http-429-ratelimiterror-from-anthropic)

## Yanıt yok

Kanallar açık ama hiçbir şey yanıt vermiyorsa, herhangi bir şeyi yeniden bağlamadan önce yönlendirmeyi ve ilkeyi kontrol edin.

```bash
openclaw status
openclaw channels status --probe
openclaw pairing list --channel <channel> [--account <id>]
openclaw config get channels
openclaw logs --follow
```

Şunlara bakın:

- DM gönderenleri için eşleştirme bekliyor olabilir.
- Grup bahsetme geçidi (`requireMention`, `mentionPatterns`).
- Kanal/grup izin listesi uyumsuzlukları.

Yaygın işaretler:

- `drop guild message (mention required` → grup mesajı, bahsedilene kadar yok sayılır.
- `pairing request` → gönderenin onaylanması gerekir.
- `blocked` / `allowlist` → gönderen/kanal ilke tarafından filtrelenmiştir.

İlgili:

- [/channels/troubleshooting](/tr/channels/troubleshooting)
- [/channels/pairing](/tr/channels/pairing)
- [/channels/groups](/tr/channels/groups)

## Dashboard Control UI bağlantısı

Dashboard/Control UI bağlanmıyorsa, URL'yi, auth modunu ve güvenli bağlam varsayımlarını doğrulayın.

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --json
```

Şunlara bakın:

- Doğru probe URL'si ve dashboard URL'si.
- İstemci ile gateway arasında auth modu/token uyumsuzluğu.
- Cihaz kimliğinin gerekli olduğu yerde HTTP kullanımı.

Yaygın işaretler:

- `device identity required` → güvenli olmayan bağlam veya eksik cihaz auth.
- `origin not allowed` → tarayıcı `Origin` değeri `gateway.controlUi.allowedOrigins` içinde değil
  (veya açık bir izin listesi olmadan loopback olmayan bir tarayıcı origin'inden bağlanıyorsunuz).
- `device nonce required` / `device nonce mismatch` → istemci, zorluk tabanlı cihaz auth akışını tamamlamıyor
  (`connect.challenge` + `device.nonce`).
- `device signature invalid` / `device signature expired` → istemci, geçerli el sıkışması için yanlış
  yükü imzaladı (veya zaman damgası bayattı).
- `AUTH_TOKEN_MISMATCH` ve `canRetryWithDeviceToken=true` → istemci, önbelleğe alınmış cihaz token'ı ile güvenilir bir yeniden deneme yapabilir.
- Bu önbelleğe alınmış token yeniden denemesi, eşleştirilmiş
  cihaz token'ı ile depolanan önbelleğe alınmış kapsam kümesini yeniden kullanır. Açık `deviceToken` / açık `scopes` çağıranları ise
  istenen kapsam kümesini korur.
- Bu yeniden deneme yolunun dışında, bağlantı auth önceliği önce açık paylaşılan
  token/parola, ardından açık `deviceToken`, sonra depolanmış cihaz token'ı,
  ardından bootstrap token şeklindedir.
- Eşzamansız Tailscale Serve Control UI yolunda, aynı `{scope, ip}` için başarısız denemeler,
  sınırlayıcı hatayı kaydetmeden önce serileştirilir. Bu nedenle aynı istemciden gelen iki kötü eşzamanlı yeniden deneme,
  ikincisinde iki düz uyumsuzluk yerine `retry later`
  gösterebilir.
- Tarayıcı origin'li loopback istemciden gelen `too many failed authentication attempts (retry later)`
  → aynı normalize edilmiş `Origin` için tekrarlanan başarısızlıklar geçici olarak
  kilitlenir; başka bir localhost origin'i ayrı bir kova kullanır.
- Bu yeniden denemeden sonra tekrarlanan `unauthorized` → paylaşılan token/cihaz token'ı kayması; gerekirse token yapılandırmasını yenileyin ve cihaz token'ını yeniden onaylayın/döndürün.
- `gateway connect failed:` → yanlış host/port/url hedefine bağlanılıyor.

### Auth ayrıntı kodları hızlı eşleme

Bir sonraki eylemi seçmek için başarısız `connect` yanıtındaki `error.details.code` değerini kullanın:

| Detail code                  | Anlamı                                                   | Önerilen eylem                                                                                                                                                                                                                                                                             |
| ---------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `AUTH_TOKEN_MISSING`         | İstemci gerekli paylaşılan token'ı göndermedi.           | İstemciye token'ı yapıştırın/ayarlayın ve yeniden deneyin. Dashboard yolları için: `openclaw config get gateway.auth.token`, ardından bunu Control UI ayarlarına yapıştırın.                                                                                                             |
| `AUTH_TOKEN_MISMATCH`        | Paylaşılan token gateway auth token'ı ile eşleşmedi.     | `canRetryWithDeviceToken=true` ise, bir güvenilir yeniden denemeye izin verin. Önbelleğe alınmış token yeniden denemeleri depolanan onaylı kapsamları yeniden kullanır; açık `deviceToken` / `scopes` çağıranları istenen kapsamları korur. Hâlâ başarısız oluyorsa [token drift recovery checklist](/cli/devices#token-drift-recovery-checklist) adımlarını uygulayın. |
| `AUTH_DEVICE_TOKEN_MISMATCH` | Cihaz başına önbelleğe alınmış token bayat veya iptal edilmiş. | [devices CLI](/cli/devices) kullanarak cihaz token'ını döndürün/yeniden onaylayın, sonra yeniden bağlanın.                                                                                                                                                                                  |
| `PAIRING_REQUIRED`           | Cihaz kimliği biliniyor ama bu rol için onaylanmamış.    | Bekleyen isteği onaylayın: `openclaw devices list`, ardından `openclaw devices approve <requestId>`.                                                                                                                                                                                        |

Device auth v2 geçiş kontrolü:

```bash
openclaw --version
openclaw doctor
openclaw gateway status
```

Günlüklerde nonce/imza hataları görünüyorsa, bağlanan istemciyi güncelleyin ve şunu doğrulayın:

1. `connect.challenge` beklediğini
2. zorluğa bağlı yükü imzaladığını
3. aynı zorluk nonce değeriyle `connect.params.device.nonce` gönderdiğini

`openclaw devices rotate` / `revoke` / `remove` beklenmedik şekilde reddediliyorsa:

- eşleştirilmiş cihaz token oturumları yalnızca **kendi** cihazlarını yönetebilir;
  çağıran ayrıca `operator.admin` sahibiyse istisna vardır
- `openclaw devices rotate --scope ...`, yalnızca
  çağıran oturumun zaten sahip olduğu operator kapsamlarını isteyebilir

İlgili:

- [/web/control-ui](/web/control-ui)
- [/gateway/configuration](/tr/gateway/configuration) (gateway auth modları)
- [/gateway/trusted-proxy-auth](/tr/gateway/trusted-proxy-auth)
- [/gateway/remote](/tr/gateway/remote)
- [/cli/devices](/cli/devices)

## Gateway hizmeti çalışmıyor

Hizmet kurulu ama süreç ayakta kalmıyorsa bunu kullanın.

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --deep   # sistem düzeyi hizmetleri de tara
```

Şunlara bakın:

- Çıkış ipuçlarıyla birlikte `Runtime: stopped`.
- Hizmet yapılandırması uyumsuzluğu (`Config (cli)` ile `Config (service)`).
- Port/dinleyici çakışmaları.
- `--deep` kullanıldığında ek launchd/systemd/schtasks kurulumları.
- `Other gateway-like services detected (best effort)` temizleme ipuçları.

Yaygın işaretler:

- `Gateway start blocked: set gateway.mode=local` veya `existing config is missing gateway.mode` → yerel gateway modu etkin değil ya da yapılandırma dosyası bozuldu ve `gateway.mode` kayboldu. Düzeltme: yapılandırmanızda `gateway.mode="local"` ayarlayın veya beklenen yerel mod yapılandırmasını yeniden damgalamak için `openclaw onboard --mode local` / `openclaw setup` komutunu tekrar çalıştırın. OpenClaw'ı Podman üzerinden çalıştırıyorsanız varsayılan yapılandırma yolu `~/.openclaw/openclaw.json` olur.
- `refusing to bind gateway ... without auth` → geçerli bir gateway auth yolu olmadan loopback olmayan bağlama (token/parola veya yapılandırılmışsa trusted-proxy).
- `another gateway instance is already listening` / `EADDRINUSE` → port çakışması.
- `Other gateway-like services detected (best effort)` → eski veya paralel launchd/systemd/schtasks birimleri var. Çoğu kurulumda makine başına tek gateway tutulmalıdır; gerçekten birden fazla gerekiyorsa portları + yapılandırma/durum/çalışma alanını yalıtın. Bkz. [/gateway#multiple-gateways-same-host](/tr/gateway#multiple-gateways-same-host).

İlgili:

- [/gateway/background-process](/tr/gateway/background-process)
- [/gateway/configuration](/tr/gateway/configuration)
- [/gateway/doctor](/tr/gateway/doctor)

## Gateway probe uyarıları

`openclaw gateway probe` bir şeye ulaşıyor ama yine de bir uyarı bloğu yazdırıyorsa bunu kullanın.

```bash
openclaw gateway probe
openclaw gateway probe --json
openclaw gateway probe --ssh user@gateway-host
```

Şunlara bakın:

- JSON çıktısındaki `warnings[].code` ve `primaryTargetId`.
- Uyarının SSH yedeği, birden fazla gateway, eksik kapsamlar veya çözümlenmemiş auth referansları ile ilgili olup olmadığı.

Yaygın işaretler:

- `SSH tunnel failed to start; falling back to direct probes.` → SSH kurulumu başarısız oldu, ancak komut yine de doğrudan yapılandırılmış/loopback hedefleri denedi.
- `multiple reachable gateways detected` → birden fazla hedef yanıt verdi. Bu genellikle kasıtlı bir çoklu gateway kurulumu ya da eski/çift dinleyiciler anlamına gelir.
- `Probe diagnostics are limited by gateway scopes (missing operator.read)` → bağlantı kuruldu, ancak ayrıntı RPC'si kapsam nedeniyle sınırlı; cihaz kimliğini eşleştirin veya `operator.read` içeren kimlik bilgileri kullanın.
- çözümlenmemiş `gateway.auth.*` / `gateway.remote.*` SecretRef uyarı metni → bu komut yolunda başarısız hedef için auth materyali mevcut değildi.

İlgili:

- [/cli/gateway](/cli/gateway)
- [/gateway#multiple-gateways-same-host](/tr/gateway#multiple-gateways-same-host)
- [/gateway/remote](/tr/gateway/remote)

## Kanal bağlı ama mesajlar akmıyor

Kanal durumu bağlı ama mesaj akışı durmuşsa, ilkeye, izinlere ve kanala özgü teslim kurallarına odaklanın.

```bash
openclaw channels status --probe
openclaw pairing list --channel <channel> [--account <id>]
openclaw status --deep
openclaw logs --follow
openclaw config get channels
```

Şunlara bakın:

- DM ilkesi (`pairing`, `allowlist`, `open`, `disabled`).
- Grup izin listesi ve bahsetme gereksinimleri.
- Eksik kanal API izinleri/kapsamları.

Yaygın işaretler:

- `mention required` → mesaj grup bahsetme ilkesi nedeniyle yok sayıldı.
- `pairing` / bekleyen onay izleri → gönderen onaylanmamış.
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

- Cron etkin mi ve bir sonraki uyanma zamanı var mı.
- İş çalıştırma geçmişi durumu (`ok`, `skipped`, `error`).
- Heartbeat atlama nedenleri (`quiet-hours`, `requests-in-flight`, `alerts-disabled`, `empty-heartbeat-file`, `no-tasks-due`).

Yaygın işaretler:

- `cron: scheduler disabled; jobs will not run automatically` → cron devre dışı.
- `cron: timer tick failed` → zamanlayıcı tik'i başarısız oldu; dosya/günlük/çalışma zamanı hatalarını kontrol edin.
- `heartbeat skipped` ve `reason=quiet-hours` → etkin saatler penceresinin dışında.
- `heartbeat skipped` ve `reason=empty-heartbeat-file` → `HEARTBEAT.md` var ama yalnızca boş satırlar / markdown başlıkları içeriyor, bu yüzden OpenClaw model çağrısını atlıyor.
- `heartbeat skipped` ve `reason=no-tasks-due` → `HEARTBEAT.md` bir `tasks:` bloğu içeriyor, ancak bu tik sırasında görevlerin hiçbiri zamanı gelmiş değil.
- `heartbeat: unknown accountId` → heartbeat teslim hedefi için geçersiz hesap kimliği.
- `heartbeat skipped` ve `reason=dm-blocked` → heartbeat hedefi DM tarzı bir hedefe çözümlendi, ancak `agents.defaults.heartbeat.directPolicy` (veya ajan başına geçersiz kılma) `block` olarak ayarlı.

İlgili:

- [/automation/cron-jobs#troubleshooting](/tr/automation/cron-jobs#troubleshooting)
- [/automation/cron-jobs](/tr/automation/cron-jobs)
- [/gateway/heartbeat](/tr/gateway/heartbeat)

## Node eşleştirilmiş ama araç başarısız oluyor

Bir node eşleştirilmiş ama araçlar başarısız oluyorsa, ön plan, izin ve onay durumunu yalıtın.

```bash
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
openclaw approvals get --node <idOrNameOrIp>
openclaw logs --follow
openclaw status
```

Şunlara bakın:

- Node çevrimiçi mi ve beklenen yeteneklere sahip mi.
- Kamera/mikrofon/konum/ekran için işletim sistemi izinleri.
- Çalıştırma onayları ve izin listesi durumu.

Yaygın işaretler:

- `NODE_BACKGROUND_UNAVAILABLE` → node uygulaması ön planda olmalıdır.
- `*_PERMISSION_REQUIRED` / `LOCATION_PERMISSION_REQUIRED` → eksik işletim sistemi izni.
- `SYSTEM_RUN_DENIED: approval required` → çalıştırma onayı bekliyor.
- `SYSTEM_RUN_DENIED: allowlist miss` → komut izin listesi tarafından engellendi.

İlgili:

- [/nodes/troubleshooting](/tr/nodes/troubleshooting)
- [/nodes/index](/tr/nodes/index)
- [/tools/exec-approvals](/tr/tools/exec-approvals)

## Browser aracı başarısız oluyor

Gateway'in kendisi sağlıklı olsa bile Browser aracı eylemleri başarısız olduğunda bunu kullanın.

```bash
openclaw browser status
openclaw browser start --browser-profile openclaw
openclaw browser profiles
openclaw logs --follow
openclaw doctor
```

Şunlara bakın:

- `plugins.allow` ayarlı mı ve `browser` içeriyor mu.
- Geçerli tarayıcı çalıştırılabilir dosya yolu.
- CDP profil erişilebilirliği.
- `existing-session` / `user` profilleri için yerel Chrome kullanılabilirliği.

Yaygın işaretler:

- `unknown command "browser"` veya `unknown command 'browser'` → paketle gelen browser eklentisi `plugins.allow` tarafından hariç tutulmuş.
- `browser.enabled=true` iken browser aracı eksik / kullanılamıyor → `plugins.allow`, `browser` değerini hariç tuttuğu için eklenti hiç yüklenmedi.
- `Failed to start Chrome CDP on port` → tarayıcı süreci başlatılamadı.
- `browser.executablePath not found` → yapılandırılmış yol geçersiz.
- `browser.cdpUrl must be http(s) or ws(s)` → yapılandırılmış CDP URL'si `file:` veya `ftp:` gibi desteklenmeyen bir şema kullanıyor.
- `browser.cdpUrl has invalid port` → yapılandırılmış CDP URL'si geçersiz veya aralık dışı bir port içeriyor.
- `No Chrome tabs found for profile="user"` → Chrome MCP bağlanma profilinde açık yerel Chrome sekmesi yok.
- `Remote CDP for profile "<name>" is not reachable` → yapılandırılmış uzak CDP uç noktasına gateway host'tan ulaşılamıyor.
- `Browser attachOnly is enabled ... not reachable` veya `Browser attachOnly is enabled and CDP websocket ... is not reachable` → yalnızca bağlanmalı profilde erişilebilir hedef yok ya da HTTP uç noktası yanıt verdi ancak CDP WebSocket yine de açılamadı.
- `Playwright is not available in this gateway build; '<feature>' is unsupported.` → geçerli gateway kurulumunda tam Playwright paketi yok; ARIA anlık görüntüleri ve temel sayfa ekran görüntüleri yine de çalışabilir, ancak gezinme, AI anlık görüntüleri, CSS seçici öğe ekran görüntüleri ve PDF dışa aktarma kullanılamaz.
- `fullPage is not supported for element screenshots` → ekran görüntüsü isteği `--full-page` ile `--ref` veya `--element` karıştırdı.
- `element screenshots are not supported for existing-session profiles; use ref from snapshot.` → Chrome MCP / `existing-session` ekran görüntüsü çağrıları CSS `--element` değil, sayfa yakalama veya anlık görüntü `--ref` kullanmalıdır.
- `existing-session file uploads do not support element selectors; use ref/inputRef.` → Chrome MCP yükleme hook'ları CSS seçiciler değil, anlık görüntü referansları gerektirir.
- `existing-session file uploads currently support one file at a time.` → Chrome MCP profillerinde çağrı başına tek yükleme gönderin.
- `existing-session dialog handling does not support timeoutMs.` → Chrome MCP profillerinde diyalog hook'ları zaman aşımı geçersiz kılmalarını desteklemez.
- `response body is not supported for existing-session profiles yet.` → `responsebody` hâlâ yönetilen bir tarayıcı veya ham CDP profili gerektirir.
- yalnızca bağlanmalı veya uzak CDP profillerinde bayat viewport / karanlık mod / yerel ayar / çevrimdışı geçersiz kılmaları → tüm gateway'i yeniden başlatmadan etkin denetim oturumunu kapatmak ve Playwright/CDP öykünme durumunu serbest bırakmak için `openclaw browser stop --browser-profile <name>` çalıştırın.

İlgili:

- [/tools/browser-linux-troubleshooting](/tr/tools/browser-linux-troubleshooting)
- [/tools/browser](/tr/tools/browser)

## Yükseltme yaptıysanız ve bir şey aniden bozulduysa

Yükseltme sonrası bozulmaların çoğu yapılandırma kayması veya artık uygulanan daha katı varsayılanlardan kaynaklanır.

### 1) Auth ve URL geçersiz kılma davranışı değişti

```bash
openclaw gateway status
openclaw config get gateway.mode
openclaw config get gateway.remote.url
openclaw config get gateway.auth.mode
```

Kontrol edilmesi gerekenler:

- `gateway.mode=remote` ise CLI çağrıları uzak hedefe gidiyor olabilir, yerel hizmetiniz ise düzgün çalışıyor olabilir.
- Açık `--url` çağrıları depolanan kimlik bilgilerine geri dönmez.

Yaygın işaretler:

- `gateway connect failed:` → yanlış URL hedefi.
- `unauthorized` → uç noktaya ulaşılıyor ama auth yanlış.

### 2) Bind ve auth korumaları daha katı

```bash
openclaw config get gateway.bind
openclaw config get gateway.auth.mode
openclaw config get gateway.auth.token
openclaw gateway status
openclaw logs --follow
```

Kontrol edilmesi gerekenler:

- Loopback olmayan bind'ler (`lan`, `tailnet`, `custom`) geçerli bir gateway auth yolu gerektirir: paylaşılan token/parola auth veya doğru yapılandırılmış loopback olmayan bir `trusted-proxy` dağıtımı.
- `gateway.token` gibi eski anahtarlar `gateway.auth.token` yerine geçmez.

Yaygın işaretler:

- `refusing to bind gateway ... without auth` → geçerli bir gateway auth yolu olmadan loopback olmayan bind.
- Çalışma zamanı aktifken `RPC probe: failed` → gateway canlı ancak geçerli auth/url ile erişilemiyor.

### 3) Eşleştirme ve cihaz kimliği durumu değişti

```bash
openclaw devices list
openclaw pairing list --channel <channel> [--account <id>]
openclaw logs --follow
openclaw doctor
```

Kontrol edilmesi gerekenler:

- Dashboard/node'lar için bekleyen cihaz onayları.
- İlke veya kimlik değişikliklerinden sonra bekleyen DM eşleştirme onayları.

Yaygın işaretler:

- `device identity required` → cihaz auth gereksinimi karşılanmadı.
- `pairing required` → gönderen/cihaz onaylanmalıdır.

Kontrollerden sonra da hizmet yapılandırması ile çalışma zamanı hâlâ uyuşmuyorsa, aynı profil/durum dizininden hizmet meta verisini yeniden kurun:

```bash
openclaw gateway install --force
openclaw gateway restart
```

İlgili:

- [/gateway/pairing](/tr/gateway/pairing)
- [/gateway/authentication](/tr/gateway/authentication)
- [/gateway/background-process](/tr/gateway/background-process)
