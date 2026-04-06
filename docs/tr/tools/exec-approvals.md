---
read_when:
    - Exec onaylarını veya allowlist'leri yapılandırma
    - macOS uygulamasında exec onay UX'i uygulama
    - Sandbox'tan çıkış istemlerini ve etkilerini inceleme
summary: Exec onayları, allowlist'ler ve sandbox'tan çıkış istemleri
title: Exec Onayları
x-i18n:
    generated_at: "2026-04-06T03:14:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: 39e91cd5c7615bdb9a6b201a85bde7514327910f6f12da5a4b0532bceb229c22
    source_path: tools/exec-approvals.md
    workflow: 15
---

# Exec onayları

Exec onayları, sandbox içindeki bir ajanın gerçek bir host (`gateway` veya `node`) üzerinde
komut çalıştırmasına izin vermek için kullanılan **yardımcı uygulama / node host korkuluğudur**. Bunu bir güvenlik ara kilidi gibi düşünün:
komutlara yalnızca politika + allowlist + (isteğe bağlı) kullanıcı onayı birlikte izin verdiğinde izin verilir.
Exec onayları, araç politikasına ve elevated geçidine **ek olarak** uygulanır (elevated `full` olarak ayarlanmışsa ve onayları atlıyorsa hariç).
Etkin politika, `tools.exec.*` ile onay varsayılanlarının **daha katı olanıdır**; bir onay alanı atlanırsa `tools.exec` değeri kullanılır.
Host exec, o makinedeki yerel onay durumunu da kullanır. `~/.openclaw/exec-approvals.json` içindeki host-yerel
`ask: "always"` ayarı, oturum veya yapılandırma varsayılanları `ask: "on-miss"` istese bile
istem göstermeye devam eder.
İstenen politikayı,
host politika kaynaklarını ve etkin sonucu incelemek için `openclaw approvals get`, `openclaw approvals get --gateway` veya
`openclaw approvals get --node <id|name|ip>` kullanın.

Yardımcı uygulama UI'ı **kullanılamıyorsa**, istem gerektiren her istek
**ask fallback** ile çözülür (varsayılan: deny).

Yerel sohbet onay istemcileri, bekleyen onay iletisinde kanala özgü olanaklar da sunabilir.
Örneğin, Matrix onay istemine tepki kısayolları ekleyebilir
(`✅` bir kez izin ver, `❌` reddet ve mümkün olduğunda `♾️` her zaman izin ver),
aynı zamanda fallback olarak iletide `/approve ...` komutlarını bırakır.

## Nerede uygulanır

Exec onayları yürütme host'unda yerel olarak uygulanır:

- **gateway host** → gateway makinesindeki `openclaw` süreci
- **node host** → node runner (macOS yardımcı uygulaması veya başsız node host)

Güven modeli notu:

- Gateway tarafından kimliği doğrulanmış çağıranlar, o Gateway için güvenilir operatörlerdir.
- Eşleştirilmiş node'lar bu güvenilir operatör yetkisini node host'a genişletir.
- Exec onayları kazara yürütme riskini azaltır, ancak kullanıcı başına bir kimlik doğrulama sınırı değildir.
- Onaylı node-host çalıştırmaları kanonik yürütme bağlamını bağlar: kanonik cwd, tam argv, mevcut olduğunda env
  bağlaması ve uygulanabildiğinde sabitlenmiş çalıştırılabilir dosya yolu.
- Shell betikleri ve doğrudan yorumlayıcı/çalışma zamanı dosya çağrıları için OpenClaw ayrıca
  tek bir somut yerel dosya operandını bağlamaya çalışır. Bu bağlı dosya onaydan sonra fakat yürütmeden önce değişirse,
  kaymış içerik yürütülmek yerine çalışma reddedilir.
- Bu dosya bağlama kasıtlı olarak en iyi çaba düzeyindedir; her
  yorumlayıcı/çalışma zamanı yükleyici yolunun tam anlamsal modeli değildir. Onay modu bağlamak için tam olarak bir somut yerel
  dosya belirleyemiyorsa, tam kapsama varmış gibi davranmak yerine onay destekli çalıştırma üretmeyi reddeder.

macOS ayrımı:

- **node host service**, `system.run` isteğini yerel IPC üzerinden **macOS uygulamasına** iletir.
- **macOS uygulaması**, UI bağlamında onayları uygular + komutu yürütür.

## Ayarlar ve depolama

Onaylar yürütme host'undaki yerel bir JSON dosyasında bulunur:

`~/.openclaw/exec-approvals.json`

Örnek şema:

```json
{
  "version": 1,
  "socket": {
    "path": "~/.openclaw/exec-approvals.sock",
    "token": "base64url-token"
  },
  "defaults": {
    "security": "deny",
    "ask": "on-miss",
    "askFallback": "deny",
    "autoAllowSkills": false
  },
  "agents": {
    "main": {
      "security": "allowlist",
      "ask": "on-miss",
      "askFallback": "deny",
      "autoAllowSkills": true,
      "allowlist": [
        {
          "id": "B0C8C0B3-2C2D-4F8A-9A3C-5A4B3C2D1E0F",
          "pattern": "~/Projects/**/bin/rg",
          "lastUsedAt": 1737150000000,
          "lastUsedCommand": "rg -n TODO",
          "lastResolvedPath": "/Users/user/Projects/.../bin/rg"
        }
      ]
    }
  }
}
```

## Onaysız "YOLO" modu

Host exec'in onay istemleri olmadan çalışmasını istiyorsanız, **her iki** politika katmanını da açmanız gerekir:

- OpenClaw yapılandırmasında istenen exec politikası (`tools.exec.*`)
- `~/.openclaw/exec-approvals.json` içindeki host-yerel onay politikası

Bunu açıkça sıkılaştırmadığınız sürece bu artık varsayılan host davranışıdır:

- `tools.exec.security`: `gateway`/`node` üzerinde `full`
- `tools.exec.ask`: `off`
- host `askFallback`: `full`

Önemli ayrım:

- `tools.exec.host=auto`, exec'in nerede çalışacağını seçer: mevcutsa sandbox'ta, değilse gateway üzerinde.
- YOLO, host exec'in nasıl onaylanacağını seçer: `security=full` artı `ask=off`.
- YOLO modunda OpenClaw, yapılandırılmış host exec politikasının üzerine ayrı bir sezgisel komut gizleme onay geçidi eklemez.
- `auto`, sandbox içindeki bir oturumdan gateway yönlendirmesini ücretsiz bir geçersiz kılma haline getirmez. Çağrı başına `host=node` isteğine `auto` içinden izin verilir ve `host=gateway` yalnızca etkin bir sandbox çalışma zamanı yoksa `auto` içinden izin alır. Kararlı bir auto olmayan varsayılan istiyorsanız `tools.exec.host` ayarlayın veya `/exec host=...` komutunu açıkça kullanın.

Daha korumacı bir kurulum istiyorsanız, katmanlardan birini `allowlist` / `on-miss`
veya `deny` olarak yeniden sıkılaştırın.

Kalıcı gateway-host "asla istem gösterme" kurulumu:

```bash
openclaw config set tools.exec.host gateway
openclaw config set tools.exec.security full
openclaw config set tools.exec.ask off
openclaw gateway restart
```

Ardından host onay dosyasını buna uyacak şekilde ayarlayın:

```bash
openclaw approvals set --stdin <<'EOF'
{
  version: 1,
  defaults: {
    security: "full",
    ask: "off",
    askFallback: "full"
  }
}
EOF
```

Bir node host için aynı onay dosyasını bunun yerine o node üzerinde uygulayın:

```bash
openclaw approvals set --node <id|name|ip> --stdin <<'EOF'
{
  version: 1,
  defaults: {
    security: "full",
    ask: "off",
    askFallback: "full"
  }
}
EOF
```

Yalnızca oturum kısayolu:

- `/exec security=full ask=off` yalnızca mevcut oturumu değiştirir.
- `/elevated full`, bu oturum için exec onaylarını da atlayan bir kır-cam kısayoludur.

Host onay dosyası yapılandırmadan daha katı kalırsa, daha katı host politikası yine kazanır.

## Politika düğmeleri

### Security (`exec.security`)

- **deny**: tüm host exec isteklerini engelle.
- **allowlist**: yalnızca allowlist'e alınmış komutlara izin ver.
- **full**: her şeye izin ver (elevated ile eşdeğer).

### Ask (`exec.ask`)

- **off**: asla istem gösterme.
- **on-miss**: yalnızca allowlist eşleşmediğinde istem göster.
- **always**: her komutta istem göster.
- Etkin ask modu `always` olduğunda `allow-always` kalıcı güven kararı istemleri bastırmaz

### Ask fallback (`askFallback`)

İstem gerekliyse ama hiçbir UI erişilebilir değilse, fallback şunu belirler:

- **deny**: engelle.
- **allowlist**: yalnızca allowlist eşleşiyorsa izin ver.
- **full**: izin ver.

### Satır içi yorumlayıcı eval sertleştirmesi (`tools.exec.strictInlineEval`)

`tools.exec.strictInlineEval=true` olduğunda OpenClaw, yorumlayıcı ikilisi allowlist'te olsa bile satır içi code-eval biçimlerini yalnızca onaylı olarak değerlendirir.

Örnekler:

- `python -c`
- `node -e`, `node --eval`, `node -p`
- `ruby -e`
- `perl -e`, `perl -E`
- `php -r`
- `lua -e`
- `osascript -e`

Bu, tek bir kararlı dosya operandına temiz şekilde eşlenmeyen yorumlayıcı yükleyicileri için ek savunmadır. Katı modda:

- bu komutlar yine açık onay gerektirir;
- `allow-always`, bunlar için otomatik olarak yeni allowlist girdileri kalıcı hale getirmez.

## Allowlist (ajan başına)

Allowlist'ler **ajan başınadır**. Birden fazla ajan varsa, macOS uygulamasında
düzenlediğiniz ajanı değiştirin. Desenler **büyük/küçük harf duyarsız glob eşleşmeleridir**.
Desenler **ikili dosya yollarına** çözülmelidir (yalnızca basename içeren girdiler yok sayılır).
Eski `agents.default` girdileri yükleme sırasında `agents.main` içine taşınır.
`echo ok && pwd` gibi shell zincirleri yine her üst düzey segmentin allowlist kurallarını karşılamasını gerektirir.

Örnekler:

- `~/Projects/**/bin/peekaboo`
- `~/.local/bin/*`
- `/opt/homebrew/bin/rg`

Her allowlist girdisi şunları izler:

- UI kimliği için kullanılan kararlı UUID **id** (isteğe bağlı)
- **son kullanım** zaman damgası
- **son kullanılan komut**
- **son çözümlenen yol**

## Skill CLI'lerini otomatik izinli yapma

**Auto-allow skill CLIs** etkin olduğunda, bilinen skill'ler tarafından başvurulan çalıştırılabilir dosyalar
node'larda (macOS node veya başsız node host) allowlist'te kabul edilir. Bu,
skill bin listesini getirmek için Gateway RPC üzerinden `skills.bins` kullanır. Katı el ile allowlist istiyorsanız bunu devre dışı bırakın.

Önemli güven notları:

- Bu, el ile yol allowlist girdilerinden ayrı bir **örtük kolaylık allowlist'i**dir.
- Gateway ile node'un aynı güven sınırı içinde olduğu güvenilir operatör ortamları için tasarlanmıştır.
- Katı açık güvene ihtiyacınız varsa `autoAllowSkills: false` bırakın ve yalnızca el ile yol allowlist girdilerini kullanın.

## Güvenli bin'ler (yalnızca stdin)

`tools.exec.safeBins`, açık allowlist girdileri olmadan
allowlist modunda çalışabilen küçük bir **yalnızca stdin** ikili dosya listesini (örneğin `cut`) tanımlar. Güvenli bin'ler,
konumsal dosya argümanlarını ve yol benzeri token'ları reddeder, bu nedenle yalnızca gelen akış üzerinde çalışabilirler.
Bunu genel bir güven listesi değil, akış filtreleri için dar bir hızlı yol olarak değerlendirin.
`safeBins` içine yorumlayıcı veya çalışma zamanı ikili dosyaları (örneğin `python3`, `node`, `ruby`, `bash`, `sh`, `zsh`) **eklemeyin**.
Bir komut tasarım gereği kod değerlendirebiliyor, alt komut yürütebiliyor veya dosya okuyabiliyorsa, açık allowlist girdilerini tercih edin ve onay istemlerini etkin tutun.
Özel güvenli bin'ler, `tools.exec.safeBinProfiles.<bin>` altında açık bir profil tanımlamalıdır.
Doğrulama yalnızca argv biçiminden deterministik olarak yapılır (host dosya sistemi varlık denetimi yoktur), bu da
izin/verme farklarından dosya varlığı oracle davranışını önler.
Varsayılan güvenli bin'ler için dosya odaklı seçenekler reddedilir (örneğin `sort -o`, `sort --output`,
`sort --files0-from`, `sort --compress-program`, `sort --random-source`,
`sort --temporary-directory`/`-T`, `wc --files0-from`, `jq -f/--from-file`,
`grep -f/--file`).
Güvenli bin'ler, yalnızca stdin davranışını bozan seçenekler için açık ikili-dosya-başına bayrak politikasını da uygular
(örneğin `sort -o/--output/--compress-program` ve grep recursive bayrakları).
Uzun seçenekler güvenli bin modunda fail-closed olarak doğrulanır: bilinmeyen bayraklar ve belirsiz
kısaltmalar reddedilir.
Güvenli bin profiline göre reddedilen bayraklar:

[//]: # "SAFE_BIN_DENIED_FLAGS:START"

- `grep`: `--dereference-recursive`, `--directories`, `--exclude-from`, `--file`, `--recursive`, `-R`, `-d`, `-f`, `-r`
- `jq`: `--argfile`, `--from-file`, `--library-path`, `--rawfile`, `--slurpfile`, `-L`, `-f`
- `sort`: `--compress-program`, `--files0-from`, `--output`, `--random-source`, `--temporary-directory`, `-T`, `-o`
- `wc`: `--files0-from`

[//]: # "SAFE_BIN_DENIED_FLAGS:END"

Güvenli bin'ler ayrıca argv token'larının yürütme zamanında **literal metin** olarak ele alınmasını zorlar (globbing
ve `$VARS` genişletmesi yoktur); böylece `*` veya `$HOME/...` gibi desenler
dosya okumayı kaçırmak için kullanılamaz.
Güvenli bin'ler ayrıca güvenilir ikili dosya dizinlerinden çözülmelidir (sistem varsayılanları artı isteğe bağlı
`tools.exec.safeBinTrustedDirs`). `PATH` girdileri hiçbir zaman otomatik olarak güvenilir kabul edilmez.
Varsayılan güvenilir safe-bin dizinleri kasıtlı olarak minimum düzeydedir: `/bin`, `/usr/bin`.
Safe-bin çalıştırılabilir dosyanız paket yöneticisi/kullanıcı yollarında bulunuyorsa (örneğin
`/opt/homebrew/bin`, `/usr/local/bin`, `/opt/local/bin`, `/snap/bin`), bunları açıkça
`tools.exec.safeBinTrustedDirs` içine ekleyin.
Shell zincirleme ve yönlendirmelere allowlist modunda otomatik izin verilmez.

Her üst düzey segment allowlist'i karşılıyorsa shell zincirlemeye (`&&`, `||`, `;`) izin verilir
(güvenli bin'ler veya skill auto-allow dahil). Yönlendirmeler allowlist modunda hâlâ desteklenmez.
Komut substitution (`$()` / backticks), çift tırnaklar içi dahil olmak üzere allowlist ayrıştırması sırasında reddedilir;
literal `$()` metni gerekiyorsa tek tırnak kullanın.
macOS yardımcı uygulama onaylarında, shell kontrolü veya genişletme söz dizimi
(`&&`, `||`, `;`, `|`, `` ` ``, `$`, `<`, `>`, `(`, `)`) içeren ham shell metni,
shell ikilisi allowlist'te değilse allowlist miss olarak değerlendirilir.
Shell sarmalayıcıları için (`bash|sh|zsh ... -c/-lc`), istek kapsamlı env geçersiz kılmaları küçük bir açık
allowlist'e indirgenir (`TERM`, `LANG`, `LC_*`, `COLORTERM`, `NO_COLOR`, `FORCE_COLOR`).
Allowlist modunda allow-always kararları için bilinen dispatch sarmalayıcıları
(`env`, `nice`, `nohup`, `stdbuf`, `timeout`) sarmalayıcı
yolları yerine iç çalıştırılabilir dosya yollarını kalıcı hale getirir. Shell çoklayıcıları (`busybox`, `toybox`) da shell applet'leri için (`sh`, `ash`,
vb.) açılarak çoklayıcı ikili dosyaları yerine iç çalıştırılabilir dosyalar kalıcı hale getirilir. Bir sarmalayıcı veya
çoklayıcı güvenli şekilde açılamıyorsa, hiçbir allowlist girdisi otomatik olarak kalıcı yapılmaz.
`python3` veya `node` gibi yorumlayıcıları allowlist'e alırsanız, satır içi eval yine açık onay gerektirsin diye `tools.exec.strictInlineEval=true` tercih edin. Katı modda, `allow-always` yine zararsız yorumlayıcı/betik çağrılarını kalıcı hale getirebilir, ancak satır içi eval taşıyıcıları otomatik olarak kalıcı yapılmaz.

Varsayılan güvenli bin'ler:

[//]: # "SAFE_BIN_DEFAULTS:START"

`cut`, `uniq`, `head`, `tail`, `tr`, `wc`

[//]: # "SAFE_BIN_DEFAULTS:END"

`grep` ve `sort` varsayılan listede değildir. Bunları açıkça etkinleştirirseniz,
stdin dışı iş akışları için açık allowlist girdileri tutun.
Güvenli bin modunda `grep` için, deseni `-e`/`--regexp` ile sağlayın; konumsal desen biçimi
reddedilir; böylece dosya operandları belirsiz konumsal argümanlar olarak kaçırılamaz.

### Güvenli bin'ler ile allowlist karşılaştırması

| Konu             | `tools.exec.safeBins`                                  | Allowlist (`exec-approvals.json`)                            |
| ---------------- | ------------------------------------------------------ | ------------------------------------------------------------ |
| Amaç             | Dar stdin filtrelerine otomatik izin verme             | Belirli çalıştırılabilir dosyalara açıkça güvenme            |
| Eşleşme türü     | Çalıştırılabilir adı + güvenli bin argv politikası     | Çözümlenmiş çalıştırılabilir dosya yolu glob deseni          |
| Argüman kapsamı  | Güvenli bin profili ve literal-token kurallarıyla kısıtlı | Yalnızca yol eşleşmesi; argümanlar aksi halde sizin sorumluluğunuzdur |
| Tipik örnekler   | `head`, `tail`, `tr`, `wc`                             | `jq`, `python3`, `node`, `ffmpeg`, özel CLI'ler              |
| En iyi kullanım  | Boru hatlarında düşük riskli metin dönüşümleri         | Daha geniş davranış veya yan etkileri olan her araç          |

Yapılandırma konumu:

- `safeBins`, yapılandırmadan gelir (`tools.exec.safeBins` veya ajan başına `agents.list[].tools.exec.safeBins`).
- `safeBinTrustedDirs`, yapılandırmadan gelir (`tools.exec.safeBinTrustedDirs` veya ajan başına `agents.list[].tools.exec.safeBinTrustedDirs`).
- `safeBinProfiles`, yapılandırmadan gelir (`tools.exec.safeBinProfiles` veya ajan başına `agents.list[].tools.exec.safeBinProfiles`). Ajan başına profil anahtarları genel anahtarları geçersiz kılar.
- allowlist girdileri host-yerel `~/.openclaw/exec-approvals.json` içinde `agents.<id>.allowlist` altında bulunur (veya Control UI / `openclaw approvals allowlist ...` üzerinden).
- `openclaw security audit`, yorumlayıcı/çalışma zamanı bin'leri açık profil olmadan `safeBins` içinde göründüğünde `tools.exec.safe_bins_interpreter_unprofiled` uyarısı verir.
- `openclaw doctor --fix`, eksik özel `safeBinProfiles.<bin>` girdilerini `{}` olarak iskeletleyebilir (sonrasında gözden geçirip sıkılaştırın). Yorumlayıcı/çalışma zamanı bin'leri otomatik iskeletlenmez.

Özel profil örneği:
__OC_I18N_900004__
`jq` için açıkça `safeBins` tercihi yaparsanız, OpenClaw yine safe-bin
modunda `env` builtin'ini reddeder; böylece `jq -n env`, açık allowlist yolu
veya onay istemi olmadan host süreç ortamını dökemez.

## Control UI ile düzenleme

Varsayılanları, ajan başına
geçersiz kılmaları ve allowlist'leri düzenlemek için **Control UI → Nodes → Exec approvals** kartını kullanın. Bir kapsam seçin (Varsayılanlar veya bir ajan), politikayı ayarlayın,
allowlist desenleri ekleyin/kaldırın, sonra **Kaydet** düğmesine basın. UI, listeyi düzenli tutabilmeniz için
desen başına **son kullanım** meta verilerini gösterir.

Hedef seçici **Gateway** (yerel onaylar) veya bir **Node** seçer. Node'lar
`system.execApprovals.get/set` bildirmelidir (macOS uygulaması veya başsız node host).
Bir node henüz exec onaylarını bildirmiyorsa, onun yerel
`~/.openclaw/exec-approvals.json` dosyasını doğrudan düzenleyin.

CLI: `openclaw approvals`, gateway veya node düzenlemeyi destekler (bkz. [Approvals CLI](/cli/approvals)).

## Onay akışı

Bir istem gerektiğinde gateway, operatör istemcilerine `exec.approval.requested` yayınlar.
Control UI ve macOS uygulaması bunu `exec.approval.resolve` ile çözer, ardından gateway
onaylı isteği node host'a iletir.

`host=node` için onay istekleri kanonik bir `systemRunPlan` payload'ı içerir. Gateway,
onaylı `system.run`
isteklerini iletirken bu planı yetkili komut/cwd/oturum bağlamı olarak kullanır.

Bu, eşzamansız onay gecikmesi için önemlidir:

- node exec yolu başta tek bir kanonik plan hazırlar
- onay kaydı bu planı ve bağlama meta verilerini depolar
- onaylandıktan sonra son iletilen `system.run` çağrısı
  daha sonra gelen çağıran düzenlemelerine güvenmek yerine saklanan planı yeniden kullanır
- çağıran onay isteği oluşturulduktan sonra `command`, `rawCommand`, `cwd`, `agentId` veya
  `sessionKey` değerlerini değiştirirse, gateway
  iletilen çalıştırmayı onay uyuşmazlığı olarak reddeder

## Yorumlayıcı/çalışma zamanı komutları

Onay destekli yorumlayıcı/çalışma zamanı çalıştırmaları kasıtlı olarak korumacıdır:

- Tam argv/cwd/env bağlamı her zaman bağlanır.
- Doğrudan shell betiği ve doğrudan çalışma zamanı dosyası biçimleri en iyi çaba ile tek bir somut yerel
  dosya anlık görüntüsüne bağlanır.
- Hâlâ tek bir doğrudan yerel dosyaya çözümlenen yaygın paket yöneticisi sarmalayıcı biçimleri (örneğin
  `pnpm exec`, `pnpm node`, `npm exec`, `npx`) bağlama öncesinde açılır.
- OpenClaw bir yorumlayıcı/çalışma zamanı komutu için tam olarak bir somut yerel dosya belirleyemiyorsa
  (örneğin paket betikleri, eval biçimleri, çalışma zamanına özgü yükleyici zincirleri veya belirsiz çok dosyalı
  biçimler), iddia edemediği anlamsal kapsama sahipmiş gibi yapmak yerine onay destekli yürütme reddedilir.
- Bu iş akışları için sandboxing, ayrı bir host sınırı veya operatörün daha geniş çalışma zamanı semantiğini kabul ettiği
  açık güvenilir allowlist/full iş akışını tercih edin.

Onay gerektiğinde exec aracı bir onay kimliğiyle hemen geri döner. Daha sonraki sistem olaylarını (`Exec finished` / `Exec denied`) ilişkilendirmek için
bu kimliği kullanın. Zaman aşımından önce karar gelmezse, istek onay zaman aşımı olarak değerlendirilir ve
ret nedeni olarak gösterilir.

### Devam teslim davranışı

Onaylı eşzamansız exec tamamlandıktan sonra OpenClaw aynı oturuma bir takip `agent` turu gönderir.

- Geçerli bir harici teslim hedefi varsa (teslim edilebilir kanal artı hedef `to`), takip teslimi bu kanalı kullanır.
- Harici hedefi olmayan yalnızca webchat veya iç oturum akışlarında takip teslimi yalnızca oturum içinde kalır (`deliver: false`).
- Bir çağıran çözümlenebilir harici kanal olmadan açıkça katı harici teslim isterse, istek `INVALID_REQUEST` ile başarısız olur.
- `bestEffortDeliver` etkinse ve harici kanal çözümlenemiyorsa, teslim başarısız olmak yerine yalnızca oturum içi teslimata düşürülür.

Onay iletişim kutusu şunları içerir:

- komut + argümanlar
- cwd
- ajan kimliği
- çözümlenen çalıştırılabilir dosya yolu
- host + politika meta verileri

Eylemler:

- **Allow once** → şimdi çalıştır
- **Always allow** → allowlist'e ekle + çalıştır
- **Deny** → engelle

## Sohbet kanallarına onay yönlendirme

Exec onay istemlerini herhangi bir sohbet kanalına (eklenti kanalları dahil) yönlendirebilir ve
bunları `/approve` ile onaylayabilirsiniz. Bu, normal giden teslim hattını kullanır.

Yapılandırma:
__OC_I18N_900005__
Sohbette yanıtlayın:
__OC_I18N_900006__
`/approve` komutu hem exec onaylarını hem de eklenti onaylarını işler. Kimlik bekleyen bir exec onayıyla eşleşmezse,
otomatik olarak bunun yerine eklenti onaylarını kontrol eder.

### Eklenti onayı yönlendirmesi

Eklenti onayı yönlendirmesi, exec onaylarıyla aynı teslim hattını kullanır ancak
`approvals.plugin` altında kendi bağımsız yapılandırmasına sahiptir. Birini etkinleştirmek veya devre dışı bırakmak diğerini etkilemez.
__OC_I18N_900007__
Yapılandırma biçimi `approvals.exec` ile aynıdır: `enabled`, `mode`, `agentFilter`,
`sessionFilter` ve `targets` aynı şekilde çalışır.

Paylaşılan etkileşimli yanıtları destekleyen kanallar, hem exec hem de
eklenti onayları için aynı onay düğmelerini oluşturur. Paylaşılan etkileşimli UI'ı olmayan kanallar, `/approve`
yönergeleri içeren düz metne geri döner.

### Herhangi bir kanalda aynı sohbet içinde onaylar

Bir exec veya eklenti onayı isteği teslim edilebilir bir sohbet yüzeyinden geliyorsa, aynı sohbet
artık varsayılan olarak `/approve` ile bunu onaylayabilir. Bu, mevcut Web UI ve terminal UI akışlarına ek olarak
Slack, Matrix ve Microsoft Teams gibi kanallara da uygulanır.

Bu paylaşılan metin-komutu yolu, o konuşma için normal kanal kimlik doğrulama modelini kullanır. Kaynak sohbet
zaten komut gönderebiliyor ve yanıt alabiliyorsa, onay isteklerinin artık beklemede kalması için
ayrı bir yerel teslim bağdaştırıcısına ihtiyacı yoktur.

Discord ve Telegram da aynı sohbet içinde `/approve` desteği sunar, ancak bu kanallar
yerel onay teslimi devre dışı olsa bile yetkilendirme için yine de
çözümlenmiş onaylayıcı listelerini kullanır.

Gateway'i doğrudan çağıran Telegram ve diğer yerel onay istemcileri için,
bu fallback kasıtlı olarak "onay bulunamadı" hatalarıyla sınırlandırılmıştır. Gerçek bir
exec onayı reddi/hatası sessizce eklenti onayı olarak yeniden denenmez.

### Yerel onay teslimi

Bazı kanallar yerel onay istemcileri olarak da davranabilir. Yerel istemciler, paylaşılan aynı sohbet `/approve`
akışına ek olarak onaylayıcı DM'leri, kaynak-sohbet fanout'u ve kanala özgü etkileşimli onay UX'i ekler.

Yerel onay kartları/düğmeleri mevcut olduğunda, bu yerel UI birincil
ajan odaklı yoldur. Araç sonucu sohbet onaylarının kullanılamadığını veya
tek kalan yolun manuel onay olduğunu söylemedikçe ajan ayrıca yinelenen düz sohbet
`/approve` komutunu yankılamamalıdır.

Genel model:

- host exec politikası yine exec onayının gerekip gerekmediğine karar verir
- `approvals.exec`, onay istemlerinin diğer sohbet hedeflerine yönlendirilmesini kontrol eder
- `channels.<channel>.execApprovals`, o kanalın yerel onay istemcisi olarak davranıp davranmayacağını kontrol eder

Yerel onay istemcileri, aşağıdakilerin tümü doğru olduğunda DM-öncelikli teslimi otomatik etkinleştirir:

- kanal yerel onay teslimini destekliyor
- onaylayıcılar açık `execApprovals.approvers` veya o
  kanalın belgelenmiş fallback kaynaklarından çözümlenebiliyor
- `channels.<channel>.execApprovals.enabled` ayarlı değil veya `"auto"`

Yerel onay istemcisini açıkça devre dışı bırakmak için `enabled: false` ayarlayın. Onaylayıcılar çözümlendiğinde
zorla etkinleştirmek için `enabled: true` ayarlayın. Genel kaynak-sohbet teslimi
`channels.<channel>.execApprovals.target` üzerinden açık kalır.

SSS: [Sohbet onayları için neden iki exec onayı yapılandırması var?](/help/faq#why-are-there-two-exec-approval-configs-for-chat-approvals)

- Discord: `channels.discord.execApprovals.*`
- Slack: `channels.slack.execApprovals.*`
- Telegram: `channels.telegram.execApprovals.*`

Bu yerel onay istemcileri, paylaşılan
aynı sohbet `/approve` akışı ve paylaşılan onay düğmelerinin üzerine DM yönlendirmesi ve isteğe bağlı kanal fanout'u ekler.

Paylaşılan davranış:

- Slack, Matrix, Microsoft Teams ve benzeri teslim edilebilir sohbetler, aynı sohbet `/approve` için normal kanal kimlik doğrulama modelini kullanır
- yerel onay istemcisi otomatik etkinleştiğinde, varsayılan yerel teslim hedefi onaylayıcı DM'leri olur
- Discord ve Telegram için yalnızca çözümlenmiş onaylayıcılar izin verebilir veya reddedebilir
- Discord onaylayıcıları açık (`execApprovals.approvers`) olabilir veya `commands.ownerAllowFrom` üzerinden çıkarılabilir
- Telegram onaylayıcıları açık (`execApprovals.approvers`) olabilir veya mevcut owner yapılandırmasından çıkarılabilir (`allowFrom` artı desteklendiğinde doğrudan mesaj `defaultTo`)
- Slack onaylayıcıları açık (`execApprovals.approvers`) olabilir veya `commands.ownerAllowFrom` üzerinden çıkarılabilir
- Slack yerel düğmeleri onay kimliği türünü korur; bu sayede `plugin:` kimlikleri ikinci bir Slack-yerel fallback katmanı olmadan eklenti onaylarını çözebilir
- Matrix yerel DM/kanal yönlendirmesi yalnızca exec içindir; Matrix eklenti onayları paylaşılan
  aynı sohbet `/approve` ve isteğe bağlı `approvals.plugin` yönlendirme yollarında kalır
- istekte bulunan kişinin onaylayıcı olması gerekmez
- kaynak sohbet zaten komutları ve yanıtları destekliyorsa, `/approve` ile doğrudan onay verebilir
- yerel Discord onay düğmeleri onay kimliği türüne göre yönlendirir: `plugin:` kimlikleri
  doğrudan eklenti onaylarına gider, diğer her şey exec onaylarına gider
- yerel Telegram onay düğmeleri, `/approve` ile aynı sınırlı exec'ten eklentiye fallback yolunu izler
- yerel `target` kaynak-sohbet teslimini etkinleştirdiğinde, onay istemleri komut metnini içerir
- bekleyen exec onaylarının varsayılan süresi 30 dakika sonra dolar
- hiçbir operatör UI'ı veya yapılandırılmış onay istemcisi isteği kabul edemiyorsa, istem `askFallback` değerine geri döner

Telegram varsayılan olarak onaylayıcı DM'lerini kullanır (`target: "dm"`). Onay istemlerinin kaynak Telegram sohbetinde/konusunda da görünmesini istiyorsanız
bunu `channel` veya `both` olarak değiştirebilirsiniz. Telegram forum konuları için OpenClaw, onay istemi ve onay sonrası takip için konuyu korur.

Bkz.:

- [Discord](/channels/discord)
- [Telegram](/channels/telegram)

### macOS IPC akışı
__OC_I18N_900008__
Güvenlik notları:

- Unix soket modu `0600`, token `exec-approvals.json` içinde saklanır.
- Aynı UID eş denetimi.
- Challenge/response (nonce + HMAC token + istek hash'i) + kısa TTL.

## Sistem olayları

Exec yaşam döngüsü sistem iletileri olarak gösterilir:

- `Exec running` (yalnızca komut running notice eşiğini aşarsa)
- `Exec finished`
- `Exec denied`

Bunlar node olayı bildirdikten sonra ajanın oturumuna gönderilir.
Gateway-host exec onayları da komut tamamlandığında (ve isteğe bağlı olarak eşikten uzun sürdüğünde çalışırken) aynı yaşam döngüsü olaylarını üretir.
Onay geçitli exec'ler, kolay ilişkilendirme için bu iletilerde `runId` olarak onay kimliğini yeniden kullanır.

## Reddedilen onay davranışı

Eşzamansız bir exec onayı reddedildiğinde OpenClaw, ajanın
aynı komutun oturumdaki daha önceki herhangi bir çalıştırmasından çıktı yeniden kullanmasını engeller. Ret nedeni,
komut çıktısının mevcut olmadığına dair açık yönlendirme ile iletilir; bu da
ajanın yeni çıktı varmış gibi iddia etmesini veya
önceki başarılı bir çalıştırmadan alınan bayat sonuçlarla reddedilen komutu tekrarlamasını durdurur.

## Sonuçlar

- **full** güçlüdür; mümkün olduğunda allowlist'leri tercih edin.
- **ask**, hızlı onaylara izin verirken sizi de döngüde tutar.
- Ajan başına allowlist'ler, bir ajanın onaylarının diğerlerine sızmasını önler.
- Onaylar yalnızca **yetkili gönderenlerden** gelen host exec isteklerine uygulanır. Yetkisiz gönderenler `/exec` veremez.
- `/exec security=full`, yetkili operatörler için oturum düzeyinde kolaylıktır ve tasarım gereği onayları atlar.
  Host exec'i kesin olarak engellemek için onay güvenliğini `deny` yapın veya araç politikasıyla `exec` aracını reddedin.

İlgili:

- [Exec tool](/tr/tools/exec)
- [Elevated mode](/tr/tools/elevated)
- [Skills](/tr/tools/skills)

## İlgili

- [Exec](/tr/tools/exec) — shell komutu yürütme aracı
- [Sandboxing](/tr/gateway/sandboxing) — sandbox modları ve çalışma alanı erişimi
- [Security](/tr/gateway/security) — güvenlik modeli ve sağlamlaştırma
- [Sandbox vs Tool Policy vs Elevated](/tr/gateway/sandbox-vs-tool-policy-vs-elevated) — hangisini ne zaman kullanmalı
