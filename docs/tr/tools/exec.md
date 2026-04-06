---
read_when:
    - Exec aracını kullanıyor veya değiştiriyorsunuz
    - stdin veya TTY davranışında hata ayıklıyorsunuz
summary: Exec aracı kullanımı, stdin modları ve TTY desteği
title: Exec Aracı
x-i18n:
    generated_at: "2026-04-06T03:13:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: 28388971c627292dba9bf65ae38d7af8cde49a33bb3b5fc8b20da4f0e350bedd
    source_path: tools/exec.md
    workflow: 15
---

# Exec aracı

Çalışma alanında shell komutları çalıştırın. `process` aracılığıyla ön plan + arka plan yürütmeyi destekler.
`process` izinli değilse `exec` eşzamanlı çalışır ve `yieldMs`/`background` değerlerini yok sayar.
Arka plan oturumları ajan başına kapsamlidir; `process` yalnızca aynı ajandan gelen oturumları görür.

## Parametreler

- `command` (zorunlu)
- `workdir` (varsayılan olarak cwd)
- `env` (anahtar/değer geçersiz kılmaları)
- `yieldMs` (varsayılan 10000): gecikmeden sonra otomatik arka plan
- `background` (bool): hemen arka plana al
- `timeout` (saniye, varsayılan 1800): süre dolunca sonlandır
- `pty` (bool): kullanılabiliyorsa bir pseudo-terminal içinde çalıştır (yalnızca TTY CLI'ları, coding agent'lar, terminal UI'ları)
- `host` (`auto | sandbox | gateway | node`): nerede yürütüleceği
- `security` (`deny | allowlist | full`): `gateway`/`node` için uygulama modu
- `ask` (`off | on-miss | always`): `gateway`/`node` için onay istemleri
- `node` (string): `host=node` için node kimliği/adı
- `elevated` (bool): elevated mod iste (sandbox'tan yapılandırılmış host yoluna çık); `security=full` yalnızca elevated çözümü `full` olduğunda zorlanır

Notlar:

- `host` varsayılan olarak `auto`'dur: oturum için sandbox çalışma zamanı etkinse sandbox, aksi halde gateway.
- `auto` varsayılan yönlendirme stratejisidir, joker değildir. Çağrı başına `host=node`, `auto` içinden izinlidir; çağrı başına `host=gateway` ise yalnızca etkin bir sandbox çalışma zamanı yoksa izinlidir.
- Ek yapılandırma olmadan `host=auto` yine de “çalışır”: sandbox yoksa `gateway`'e çözülür; canlı bir sandbox varsa sandbox içinde kalır.
- `elevated`, sandbox'tan yapılandırılmış host yoluna çıkar: varsayılan olarak `gateway`, veya `tools.exec.host=node` olduğunda (ya da oturum varsayılanı `host=node` olduğunda) `node`. Yalnızca geçerli oturum/sağlayıcı için elevated erişim etkinse kullanılabilir.
- `gateway`/`node` onayları `~/.openclaw/exec-approvals.json` tarafından denetlenir.
- `node`, eşlenmiş bir node gerektirir (companion app veya headless node host).
- Birden fazla node varsa birini seçmek için `exec.node` veya `tools.exec.node` ayarlayın.
- `exec host=node`, node'lar için tek shell yürütme yoludur; eski `nodes.run` sarmalayıcısı kaldırılmıştır.
- Windows dışı host'larda exec, ayarlıysa `SHELL` kullanır; `SHELL` değeri `fish` ise fish ile uyumsuz betikleri önlemek için `PATH` içinden `bash` (veya `sh`) tercih eder, ardından ikisi de yoksa `SHELL` değerine geri döner.
- Windows host'larda exec önce PowerShell 7 (`pwsh`) keşfini dener (Program Files, ProgramW6432, ardından PATH), sonra Windows PowerShell 5.1'e geri döner.
- Host yürütmesi (`gateway`/`node`), ikili ele geçirme veya enjekte edilmiş kodu önlemek için `env.PATH` ve yükleyici geçersiz kılmalarını (`LD_*`/`DYLD_*`) reddeder.
- OpenClaw, shell/profile kurallarının exec-tool bağlamını algılayabilmesi için oluşturulan komut ortamında `OPENCLAW_SHELL=exec` ayarlar (PTY ve sandbox yürütmesi dahil).
- Önemli: sandboxing varsayılan olarak **kapalıdır**. Sandboxing kapalıysa örtük `host=auto`
  değeri `gateway`'e çözülür. Açık `host=sandbox` ise sessizce
  gateway host'unda çalışmak yerine yine kapalı güvenli şekilde başarısız olur. Sandboxing'i etkinleştirin veya onaylarla `host=gateway` kullanın.
- Betik ön kontrol denetimleri (yaygın Python/Node shell-sözdizimi hataları için) yalnızca
  etkili `workdir` sınırı içindeki dosyaları inceler. Bir betik yolu `workdir` dışına çözülürse,
  bu dosya için ön kontrol atlanır.
- Şimdi başlayan uzun süreli işler için bir kez başlatın ve komut çıktı ürettiğinde veya başarısız olduğunda etkinse otomatik
  tamamlanma uyanmasına güvenin.
  Günlükler, durum, girdi veya müdahale için `process` kullanın; sleep döngüleri,
  timeout döngüleri veya tekrarlı yoklama ile zamanlama öykünmesi yapmayın.
- Daha sonra veya bir zamanlamaya göre gerçekleşmesi gereken işler için
  `exec` sleep/delay desenleri yerine cron kullanın.

## Yapılandırma

- `tools.exec.notifyOnExit` (varsayılan: true): true olduğunda arka plana alınmış exec oturumları çıkışta bir sistem etkinliği kuyruğa alır ve heartbeat ister.
- `tools.exec.approvalRunningNoticeMs` (varsayılan: 10000): onay geçitli bir exec bu süreden uzun çalışırsa tek bir “running” bildirimi yayar (`0` devre dışı bırakır).
- `tools.exec.host` (varsayılan: `auto`; sandbox çalışma zamanı etkinse `sandbox`, aksi halde `gateway` olarak çözülür)
- `tools.exec.security` (varsayılan: sandbox için `deny`, gateway + node için ayarlı değilse `full`)
- `tools.exec.ask` (varsayılan: `off`)
- Onaysız host exec, gateway + node için varsayılandır. Onay/allowlist davranışı istiyorsanız hem `tools.exec.*` hem de host `~/.openclaw/exec-approvals.json` dosyasını sıkılaştırın; bkz. [Exec approvals](/tr/tools/exec-approvals#no-approval-yolo-mode).
- YOLO, `host=auto` değerinden değil host-ilkesi varsayılanlarından (`security=full`, `ask=off`) gelir. Gateway veya node yönlendirmesini zorlamak istiyorsanız `tools.exec.host` ayarlayın veya `/exec host=...` kullanın.
- `security=full` artı `ask=off` modunda host exec doğrudan yapılandırılmış ilkeyi izler; ek sezgisel komut-karartma ön filtresi yoktur.
- `tools.exec.node` (varsayılan: ayarsız)
- `tools.exec.strictInlineEval` (varsayılan: false): true olduğunda `python -c`, `node -e`, `ruby -e`, `perl -e`, `php -r`, `lua -e` ve `osascript -e` gibi satır içi yorumlayıcı eval biçimleri her zaman açık onay gerektirir. `allow-always` yine de zararsız yorumlayıcı/betik çağrılarını kalıcılaştırabilir, ancak satır içi eval biçimleri her seferinde yine istem gösterir.
- `tools.exec.pathPrepend`: exec çalıştırmaları için `PATH` başına eklenecek dizin listesi (yalnızca gateway + sandbox).
- `tools.exec.safeBins`: açık allowlist girdileri olmadan çalışabilen yalnızca-stdin güvenli ikililer. Davranış ayrıntıları için bkz. [Safe bins](/tr/tools/exec-approvals#safe-bins-stdin-only).
- `tools.exec.safeBinTrustedDirs`: `safeBins` yol denetimleri için açıkça güvenilen ek dizinler. `PATH` girdilerine otomatik güvenilmez. Yerleşik varsayılanlar `/bin` ve `/usr/bin`'dir.
- `tools.exec.safeBinProfiles`: güvenli ikili başına isteğe bağlı özel argv ilkesi (`minPositional`, `maxPositional`, `allowedValueFlags`, `deniedFlags`).

Örnek:

```json5
{
  tools: {
    exec: {
      pathPrepend: ["~/bin", "/opt/oss/bin"],
    },
  },
}
```

### PATH işleme

- `host=gateway`: giriş-shell'inizin `PATH` değerini exec ortamına birleştirir. `env.PATH` geçersiz kılmaları
  host yürütmesi için reddedilir. Daemon'un kendisi yine de asgari bir `PATH` ile çalışır:
  - macOS: `/opt/homebrew/bin`, `/usr/local/bin`, `/usr/bin`, `/bin`
  - Linux: `/usr/local/bin`, `/usr/bin`, `/bin`
- `host=sandbox`: container içinde `sh -lc` (login shell) çalıştırır, bu nedenle `/etc/profile`, `PATH` değerini sıfırlayabilir.
  OpenClaw, profil kaynaklamasından sonra `env.PATH` değerini dahili bir env var aracılığıyla başa ekler (shell enterpolasyonu yok);
  `tools.exec.pathPrepend` burada da uygulanır.
- `host=node`: ilettiğiniz engellenmemiş env geçersiz kılmalarının yalnızca bunları node'a gönderilir. `env.PATH` geçersiz kılmaları
  host yürütmesi için reddedilir ve node host'ları tarafından yok sayılır. Bir node üzerinde ek PATH girdilerine ihtiyacınız varsa,
  node host servis ortamını (systemd/launchd) yapılandırın veya araçları standart konumlara kurun.

Ajan başına node bağlama (yapılandırmada ajan listesi dizinini kullanın):

```bash
openclaw config get agents.list
openclaw config set agents.list[0].tools.exec.node "node-id-or-name"
```

Control UI: Nodes sekmesinde aynı ayarlar için küçük bir “Exec node binding” paneli bulunur.

## Oturum geçersiz kılmaları (`/exec`)

`host`, `security`, `ask` ve `node` için **oturum başına** varsayılanları ayarlamak üzere `/exec` kullanın.
Geçerli değerleri göstermek için `/exec` komutunu bağımsız olarak gönderin.

Örnek:

```
/exec host=auto security=allowlist ask=on-miss node=mac-1
```

## Yetkilendirme modeli

`/exec`, yalnızca **yetkili göndericiler** için geçerlidir (kanal izin listeleri/eşleme artı `commands.useAccessGroups`).
Yalnızca **oturum durumunu** günceller ve yapılandırma yazmaz. Exec'i kesin olarak devre dışı bırakmak için
araç ilkesi üzerinden reddedin (`tools.deny: ["exec"]` veya ajan başına).
Açıkça `security=full` ve `ask=off` ayarlamadığınız sürece host onayları yine uygulanır.

## Exec onayları (companion app / node host)

Sandbox içindeki ajanlar, exec'in gateway veya node host üzerinde çalışmasından önce istek başına onay gerektirebilir.
İlke, allowlist ve UI akışı için bkz. [Exec approvals](/tr/tools/exec-approvals).

Onay gerektiğinde exec aracı
`status: "approval-pending"` ve bir onay kimliği ile hemen döner. Onaylandıktan (veya reddedildikten / süresi dolduktan) sonra,
Gateway sistem etkinlikleri yayar (`Exec finished` / `Exec denied`). Komut
`tools.exec.approvalRunningNoticeMs` sonrasında hâlâ çalışıyorsa tek bir `Exec running` bildirimi yayılır.
Yerel onay kartları/düğmeleri bulunan kanallarda ajan öncelikle bu
yerel UI'a güvenmeli ve yalnızca araç
sonucu sohbet onaylarının kullanılamadığını açıkça söylediğinde veya tek yol
el ile onay olduğunda manuel `/approve` komutu eklemelidir.

## Allowlist + safe bins

El ile allowlist uygulaması **yalnızca çözümlenmiş ikili yolları** ile eşleşir (basename eşleşmesi yoktur). `security=allowlist`
olduğunda shell komutları yalnızca her boru hattı segmenti
allowlist'te veya bir safe bin ise otomatik izin alır. Zincirleme (`;`, `&&`, `||`) ve yönlendirmeler,
her üst düzey segment allowlist'i karşılamadıkça
allowlist modunda reddedilir (safe bins dahil).
Yönlendirmeler desteklenmemeye devam eder.
Kalıcı `allow-always` güveni bu kuralı aşmaz: zincirli bir komut yine her
üst düzey segmentin eşleşmesini gerektirir.

`autoAllowSkills`, exec onaylarında ayrı bir kolaylık yoludur. El ile yol allowlist girdileriyle aynı şey değildir.
Katı açık güven için `autoAllowSkills` kapalı tutun.

İki denetimi farklı işler için kullanın:

- `tools.exec.safeBins`: küçük, yalnızca-stdin akış filtreleri.
- `tools.exec.safeBinTrustedDirs`: safe-bin yürütülebilir yolları için açık ek güvenilir dizinler.
- `tools.exec.safeBinProfiles`: özel safe bin'ler için açık argv ilkesi.
- allowlist: yürütülebilir yollar için açık güven.

`safeBins`'i genel bir allowlist olarak görmeyin ve yorumlayıcı/çalışma zamanı ikilileri (örneğin `python3`, `node`, `ruby`, `bash`) eklemeyin. Bunlara ihtiyacınız varsa açık allowlist girdileri kullanın ve onay istemlerini açık tutun.
`openclaw security audit`, yorumlayıcı/çalışma zamanı `safeBins` girdilerinde açık profiller eksik olduğunda uyarır ve `openclaw doctor --fix`, eksik özel `safeBinProfiles` girdilerini iskelet olarak oluşturabilir.
`openclaw security audit` ve `openclaw doctor`, `jq` gibi geniş davranışlı ikilileri yeniden açıkça `safeBins` içine eklediğinizde de uyarır.
Yorumlayıcıları açıkça allowlist'e alırsanız satır içi kod-eval biçimlerinin yine yeni onay gerektirmesi için `tools.exec.strictInlineEval` etkinleştirin.

Tam ilke ayrıntıları ve örnekleri için bkz. [Exec approvals](/tr/tools/exec-approvals#safe-bins-stdin-only) ve [Safe bins versus allowlist](/tr/tools/exec-approvals#safe-bins-versus-allowlist).

## Örnekler

Ön plan:

```json
{ "tool": "exec", "command": "ls -la" }
```

Arka plan + yoklama:

```json
{"tool":"exec","command":"npm run build","yieldMs":1000}
{"tool":"process","action":"poll","sessionId":"<id>"}
```

Yoklama, bekleme döngüleri için değil isteğe bağlı durum içindir. Otomatik tamamlanma uyanması
etkinse komut çıktı ürettiğinde veya başarısız olduğunda oturumu uyandırabilir.

Tuş gönder (tmux tarzı):

```json
{"tool":"process","action":"send-keys","sessionId":"<id>","keys":["Enter"]}
{"tool":"process","action":"send-keys","sessionId":"<id>","keys":["C-c"]}
{"tool":"process","action":"send-keys","sessionId":"<id>","keys":["Up","Up","Enter"]}
```

Gönder (yalnızca CR gönder):

```json
{ "tool": "process", "action": "submit", "sessionId": "<id>" }
```

Yapıştır (varsayılan olarak bracketed):

```json
{ "tool": "process", "action": "paste", "sessionId": "<id>", "text": "line1\nline2\n" }
```

## apply_patch

`apply_patch`, `exec`'in yapılandırılmış çok dosyalı düzenlemeler için bir alt aracıdır.
OpenAI ve OpenAI Codex modelleri için varsayılan olarak etkindir. Yapılandırmayı yalnızca
onu devre dışı bırakmak veya belirli modellerle sınırlamak istediğinizde kullanın:

```json5
{
  tools: {
    exec: {
      applyPatch: { workspaceOnly: true, allowModels: ["gpt-5.4"] },
    },
  },
}
```

Notlar:

- Yalnızca OpenAI/OpenAI Codex modelleri için kullanılabilir.
- Araç ilkesi yine geçerlidir; `allow: ["write"]`, örtük olarak `apply_patch` izni verir.
- Yapılandırma `tools.exec.applyPatch` altında bulunur.
- `tools.exec.applyPatch.enabled` varsayılan olarak `true`'dur; OpenAI modelleri için aracı devre dışı bırakmak üzere `false` ayarlayın.
- `tools.exec.applyPatch.workspaceOnly` varsayılan olarak `true`'dur (çalışma alanı içinde). `apply_patch` aracının çalışma alanı dizini dışında yazma/silme yapmasını bilerek istiyorsanız yalnızca `false` ayarlayın.

## İlgili

- [Exec Approvals](/tr/tools/exec-approvals) — shell komutları için onay geçitleri
- [Sandboxing](/tr/gateway/sandboxing) — komutları sandbox'lı ortamlarda çalıştırma
- [Background Process](/tr/gateway/background-process) — uzun süreli exec ve process aracı
- [Security](/tr/gateway/security) — araç ilkesi ve elevated erişim
