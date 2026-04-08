---
read_when:
    - Exec onaylarını veya izin listelerini yapılandırırken
    - macOS uygulamasında exec onay UX'ini uygularken
    - Sandbox'tan çıkış istemlerini ve etkilerini incelerken
summary: Exec onayları, izin listeleri ve sandbox'tan çıkış istemleri
title: Exec Onayları
x-i18n:
    generated_at: "2026-04-08T02:19:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6041929185bab051ad873cc4822288cb7d6f0470e19e7ae7a16b70f76dfc2cd9
    source_path: tools/exec-approvals.md
    workflow: 15
---

# Exec onayları

Exec onayları, sandbox içine alınmış bir aracının gerçek bir ana makinede (`gateway` veya `node`) komut çalıştırmasına izin vermek için kullanılan **yardımcı uygulama / node ana makinesi korumasıdır**. Bunu bir güvenlik kilidi gibi düşünün:
komutlara yalnızca ilke + izin listesi + (isteğe bağlı) kullanıcı onayı birlikte kabul ettiğinde izin verilir.
Exec onayları, araç ilkesine ve elevated geçidine **ek olarak** uygulanır (elevated `full` olarak ayarlanmışsa ve onayları atlıyorsa bu durum hariçtir).
Etkili ilke, `tools.exec.*` ile onay varsayılanlarının **daha katı** olanıdır; bir onay alanı atlanmışsa `tools.exec` değeri kullanılır.
Ana makinede exec ayrıca o makinedeki yerel onay durumunu da kullanır. Ana makinede yerel
`~/.openclaw/exec-approvals.json` içindeki `ask: "always"` değeri,
oturum veya yapılandırma varsayılanları `ask: "on-miss"` istese bile istem göstermeye devam eder.
İstenen ilkeyi,
ana makine ilke kaynaklarını ve etkili sonucu incelemek için `openclaw approvals get`, `openclaw approvals get --gateway` veya
`openclaw approvals get --node <id|name|ip>` kullanın.

Eğer yardımcı uygulama UI'ı **mevcut değilse**, istem gerektiren her istek
**ask fallback** ile çözülür (varsayılan: deny).

Yerel sohbet onay istemcileri, bekleyen onay mesajında kanala özgü kolaylıklar da sunabilir.
Örneğin Matrix, onay istemi üzerinde tepki kısayollarını önceden yerleştirebilir
(`✅` bir kez izin ver, `❌` reddet ve varsa `♾️` her zaman izin ver),
ve bunu yedek yol olarak mesajdaki `/approve ...` komutlarını bırakırken yapabilir.

## Nerede uygulanır

Exec onayları, yürütmenin yapıldığı ana makinede yerel olarak uygulanır:

- **gateway ana makinesi** → gateway makinesindeki `openclaw` süreci
- **node ana makinesi** → node çalıştırıcısı (macOS yardımcı uygulaması veya başsız node ana makinesi)

Güven modeli notu:

- Gateway ile kimliği doğrulanmış çağıranlar, o Gateway için güvenilir operatörlerdir.
- Eşlenmiş node'lar, bu güvenilir operatör yeteneğini node ana makinesine taşır.
- Exec onayları kazara yürütme riskini azaltır, ancak kullanıcı başına bir auth sınırı değildir.
- Onaylanmış node-ana-makine çalıştırmaları standart yürütme bağlamını bağlar: standart cwd, tam argv, varsa env
  bağlaması ve uygunsa sabit yürütülebilir yol.
- Shell betikleri ve doğrudan yorumlayıcı/runtime dosya çağrıları için OpenClaw ayrıca
  tek bir somut yerel dosya operandını bağlamaya çalışır. Bu bağlı dosya onaydan sonra ama çalıştırmadan önce değişirse,
  çalışma, kaymış içerik yürütülmek yerine reddedilir.
- Bu dosya bağlama bilinçli olarak en iyi çaba yaklaşımıdır; her
  yorumlayıcı/runtime yükleyici yolunun tam anlamsal modeli değildir. Onay modu tam olarak bağlanacak tek bir somut yerel
  dosya belirleyemezse, tam kapsama varmış gibi davranmak yerine onay destekli bir çalışma üretmeyi reddeder.

macOS ayrımı:

- **node ana makinesi hizmeti**, `system.run` isteğini yerel IPC üzerinden **macOS uygulamasına** iletir.
- **macOS uygulaması**, onayları uygular + komutu UI bağlamında çalıştırır.

## Ayarlar ve depolama

Onaylar, yürütmenin yapıldığı ana makinedeki yerel bir JSON dosyasında tutulur:

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

Ana makinede exec'in onay istemleri olmadan çalışmasını istiyorsanız, **her iki** ilke katmanını da açmanız gerekir:

- OpenClaw yapılandırmasındaki istenen exec ilkesi (`tools.exec.*`)
- `~/.openclaw/exec-approvals.json` içindeki ana makinede yerel onay ilkesi

Bu artık, siz açıkça sıkılaştırmadığınız sürece varsayılan ana makine davranışıdır:

- `tools.exec.security`: `gateway`/`node` üzerinde `full`
- `tools.exec.ask`: `off`
- ana makine `askFallback`: `full`

Önemli ayrım:

- `tools.exec.host=auto`, exec'in nerede çalışacağını seçer: varsa sandbox, yoksa gateway.
- YOLO, ana makinede exec'in nasıl onaylandığını seçer: `security=full` artı `ask=off`.
- YOLO modunda OpenClaw, yapılandırılmış ana makine exec ilkesinin üzerine ayrı bir sezgisel komut karartma onay geçidi eklemez.
- `auto`, gateway yönlendirmesini sandbox'lanmış bir oturumdan ücretsiz bir geçersiz kılma haline getirmez. Çağrı başına `host=node` isteğine `auto` içinden izin verilir ve `host=gateway` yalnızca etkin bir sandbox runtime yoksa `auto` içinden izinlidir. Kararlı bir auto olmayan varsayılan istiyorsanız `tools.exec.host` ayarlayın veya açıkça `/exec host=...` kullanın.

Daha muhafazakâr bir kurulum istiyorsanız katmanlardan birini `allowlist` / `on-miss`
veya `deny` olarak geri sıkılaştırın.

Kalıcı gateway-ana-makinesi "asla istem gösterme" kurulumu:

```bash
openclaw config set tools.exec.host gateway
openclaw config set tools.exec.security full
openclaw config set tools.exec.ask off
openclaw gateway restart
```

Ardından ana makine onay dosyasını buna uyacak şekilde ayarlayın:

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

Bir node ana makinesi için bunun yerine aynı onay dosyasını o node üzerinde uygulayın:

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

Yalnızca oturuma özel kısayol:

- `/exec security=full ask=off` yalnızca geçerli oturumu değiştirir.
- `/elevated full`, o oturum için exec onaylarını da atlayan bir acil durum kısayoludur.

Ana makine onay dosyası yapılandırmadan daha katı kalırsa, daha katı olan ana makine ilkesi yine kazanır.

## İlke düğmeleri

### Security (`exec.security`)

- **deny**: tüm ana makine exec isteklerini engelle.
- **allowlist**: yalnızca izin listesine alınmış komutlara izin ver.
- **full**: her şeye izin ver (elevated ile eşdeğer).

### Ask (`exec.ask`)

- **off**: asla istem gösterme.
- **on-miss**: yalnızca izin listesi eşleşmediğinde istem göster.
- **always**: her komutta istem göster.
- Etkili ask modu `always` olduğunda `allow-always` kalıcı güven kararı istemleri bastırmaz

### Ask fallback (`askFallback`)

İstem gerekliyse ama hiçbir UI erişilebilir değilse, fallback şuna karar verir:

- **deny**: engelle.
- **allowlist**: yalnızca izin listesi eşleşirse izin ver.
- **full**: izin ver.

### Satır içi yorumlayıcı eval sertleştirmesi (`tools.exec.strictInlineEval`)

`tools.exec.strictInlineEval=true` olduğunda OpenClaw, yorumlayıcı ikilisinin kendisi izin listesinde olsa bile satır içi kod değerlendirme biçimlerini yalnızca onayla çalıştırılabilir olarak ele alır.

Örnekler:

- `python -c`
- `node -e`, `node --eval`, `node -p`
- `ruby -e`
- `perl -e`, `perl -E`
- `php -r`
- `lua -e`
- `osascript -e`

Bu, tek bir kararlı dosya operandına temiz biçimde eşlenmeyen yorumlayıcı yükleyicileri için derinlikli savunmadır. Sıkı modda:

- bu komutlar yine de açık onay gerektirir;
- `allow-always`, bunlar için yeni izin listesi girdilerini otomatik olarak kalıcı hale getirmez.

## Allowlist (aracı başına)

İzin listeleri **aracı başınadır**. Birden fazla aracı varsa, düzenlediğiniz
aracıyı macOS uygulamasında değiştirin. Desenler **büyük/küçük harfe duyarsız glob eşleşmeleridir**.
Desenler **ikili yollara** çözülmelidir (yalnızca basename içeren girdiler yok sayılır).
Eski `agents.default` girdileri yükleme sırasında `agents.main` içine taşınır.
`echo ok && pwd` gibi shell zincirleri için yine de her üst düzey segmentin izin listesi kurallarını karşılaması gerekir.

Örnekler:

- `~/Projects/**/bin/peekaboo`
- `~/.local/bin/*`
- `/opt/homebrew/bin/rg`

Her izin listesi girdisi şunları izler:

- UI kimliği için sabit UUID olarak **id** (isteğe bağlı)
- **son kullanım** zaman damgası
- **son kullanılan komut**
- **son çözümlenen yol**

## Skill CLI'larını otomatik izinli yapma

**Skill CLI'larını otomatik izinli yap** etkinleştirildiğinde, bilinen Skills tarafından başvurulan yürütülebilir dosyalar
node'larda (macOS node veya başsız node ana makinesi) izin listesinde kabul edilir. Bu,
skill ikili listesini almak için Gateway RPC üzerinden `skills.bins` kullanır. Katı el ile izin listeleri istiyorsanız bunu kapatın.

Önemli güven notları:

- Bu, el ile yol izin listesi girdilerinden ayrı olan **örtük bir kolaylık izin listesidir**.
- Gateway ile node'un aynı güven sınırında olduğu güvenilir operatör ortamları için tasarlanmıştır.
- Katı açık güven gerekiyorsa `autoAllowSkills: false` değerini koruyun ve yalnızca el ile yol izin listesi girdileri kullanın.

## Safe bins (yalnızca stdin)

`tools.exec.safeBins`, allowlist modunda **açık izin listesi girdileri olmadan**
çalışabilen küçük bir **yalnızca stdin** ikili listesi (örneğin `cut`) tanımlar. Safe bins,
konumsal dosya argümanlarını ve yol benzeri token'ları reddeder; bu nedenle yalnızca gelen akış üzerinde çalışabilirler.
Bunu genel bir güven listesi olarak değil, akış filtreleri için dar bir hızlı yol olarak değerlendirin.
Yorumlayıcı veya runtime ikililerini (örneğin `python3`, `node`, `ruby`, `bash`, `sh`, `zsh`)
`safeBins` içine **eklemeyin**.
Bir komut tasarım gereği kod değerlendirebiliyorsa, alt komut çalıştırabiliyorsa veya dosya okuyabiliyorsa,
açık izin listesi girdilerini tercih edin ve onay istemlerini açık tutun.
Özel safe bin'ler `tools.exec.safeBinProfiles.<bin>` içinde açık bir profil tanımlamalıdır.
Doğrulama yalnızca argv biçiminden deterministik olarak yapılır (ana makinede dosya sistemi varlık kontrolleri yoktur); bu,
izin/verme farklarından dosya varlığı oracle davranışını önler.
Dosya odaklı seçenekler varsayılan safe bin'ler için reddedilir (örneğin `sort -o`, `sort --output`,
`sort --files0-from`, `sort --compress-program`, `sort --random-source`,
`sort --temporary-directory`/`-T`, `wc --files0-from`, `jq -f/--from-file`,
`grep -f/--file`).
Safe bin'ler ayrıca yalnızca stdin davranışını bozan seçenekler için ikili başına açık bayrak ilkesi de uygular
(örneğin `sort -o/--output/--compress-program` ve grep özyinelemeli bayrakları).
Uzun seçenekler safe-bin modunda fail-closed doğrulanır: bilinmeyen bayraklar ve belirsiz
kısaltmalar reddedilir.
Safe-bin profiline göre reddedilen bayraklar:

[//]: # "SAFE_BIN_DENIED_FLAGS:START"

- `grep`: `--dereference-recursive`, `--directories`, `--exclude-from`, `--file`, `--recursive`, `-R`, `-d`, `-f`, `-r`
- `jq`: `--argfile`, `--from-file`, `--library-path`, `--rawfile`, `--slurpfile`, `-L`, `-f`
- `sort`: `--compress-program`, `--files0-from`, `--output`, `--random-source`, `--temporary-directory`, `-T`, `-o`
- `wc`: `--files0-from`

[//]: # "SAFE_BIN_DENIED_FLAGS:END"

Safe bin'ler ayrıca argv token'larının çalışma zamanında **literal metin** olarak ele alınmasını zorlar (globbing
ve `$VARS` genişletmesi yoktur) böylece `*` veya `$HOME/...` gibi desenler
dosya okuma kaçırmak için kullanılamaz.
Safe bin'ler ayrıca güvenilir ikili dizinlerinden çözülmelidir (sistem varsayılanları artı isteğe bağlı
`tools.exec.safeBinTrustedDirs`). `PATH` girdilerine asla otomatik güvenilmez.
Varsayılan güvenilir safe-bin dizinleri bilinçli olarak minimaldir: `/bin`, `/usr/bin`.
Safe-bin yürütülebilir dosyanız paket yöneticisi/kullanıcı yollarında bulunuyorsa (örneğin
`/opt/homebrew/bin`, `/usr/local/bin`, `/opt/local/bin`, `/snap/bin`), bunları açıkça
`tools.exec.safeBinTrustedDirs` içine ekleyin.
Shell zincirleme ve yönlendirmelere allowlist modunda otomatik izin verilmez.

Her üst düzey segment izin listesi kurallarını karşıladığında shell zincirlemeye (`&&`, `||`, `;`) izin verilir
(safe bin'ler veya skill auto-allow dahil). Yönlendirmeler allowlist modunda desteklenmez.
Komut ikamesi (`$()` / backtick'ler), çift tırnak içinde dahil olmak üzere allowlist ayrıştırması sırasında reddedilir;
literal `$()` metnine ihtiyacınız varsa tek tırnak kullanın.
macOS yardımcı uygulama onaylarında, shell denetim veya genişletme sözdizimi içeren ham shell metni
(`&&`, `||`, `;`, `|`, `` ` ``, `$`, `<`, `>`, `(`, `)`) shell ikilisinin kendisi
izin listesine alınmadıkça allowlist eşleşmezliği olarak değerlendirilir.
Shell sarmalayıcıları için (`bash|sh|zsh ... -c/-lc`), istek kapsamlı env geçersiz kılmaları
küçük bir açık izin listesine indirilir (`TERM`, `LANG`, `LC_*`, `COLORTERM`, `NO_COLOR`, `FORCE_COLOR`).
Allowlist modunda allow-always kararları için, bilinen dağıtım sarmalayıcıları
(`env`, `nice`, `nohup`, `stdbuf`, `timeout`) sarmalayıcı yolları yerine iç yürütülebilir yolları kalıcılaştırır.
Shell çoklayıcıları (`busybox`, `toybox`) da shell applet'leri (`sh`, `ash`,
vb.) için açılır; böylece çoklayıcı ikilileri yerine iç yürütülebilir dosyalar kalıcılaştırılır. Bir sarmalayıcı veya
çoklayıcı güvenli biçimde açılamıyorsa, otomatik olarak hiçbir izin listesi girdisi kalıcılaştırılmaz.
`python3` veya `node` gibi yorumlayıcıları izin listesine alıyorsanız satır içi eval'in yine de açık onay gerektirmesi için `tools.exec.strictInlineEval=true` tercih edin. Sıkı modda `allow-always`, zararsız yorumlayıcı/betik çağrılarını yine de kalıcılaştırabilir, ancak satır içi eval taşıyıcıları otomatik olarak kalıcılaştırılmaz.

Varsayılan safe bins:

[//]: # "SAFE_BIN_DEFAULTS:START"

`cut`, `uniq`, `head`, `tail`, `tr`, `wc`

[//]: # "SAFE_BIN_DEFAULTS:END"

`grep` ve `sort` varsayılan listede değildir. Bunları özellikle dahil ederseniz
stdin dışı iş akışları için açık izin listesi girdilerini koruyun.
`grep` için safe-bin modunda, deseni `-e`/`--regexp` ile sağlayın; konumsal desen biçimi
reddedilir, böylece dosya operandları belirsiz konumsal argümanlar olarak kaçıralamaz.

### Safe bins ve allowlist karşılaştırması

| Konu | `tools.exec.safeBins` | Allowlist (`exec-approvals.json`) |
| ---------------- | ------------------------------------------------------ | ------------------------------------------------------------ |
| Amaç | Dar stdin filtrelerine otomatik izin ver | Belirli yürütülebilir dosyalara açıkça güven |
| Eşleşme türü | Yürütülebilir ad + safe-bin argv ilkesi | Çözümlenmiş yürütülebilir yol glob deseni |
| Argüman kapsamı | Safe-bin profili ve literal-token kurallarıyla kısıtlı | Yalnızca yol eşleşmesi; argümanlar aksi halde sizin sorumluluğunuzdur |
| Tipik örnekler | `head`, `tail`, `tr`, `wc` | `jq`, `python3`, `node`, `ffmpeg`, özel CLI'lar |
| En iyi kullanım | Pipeline'larda düşük riskli metin dönüşümleri | Daha geniş davranış veya yan etkilere sahip tüm araçlar |

Yapılandırma konumu:

- `safeBins` yapılandırmadan gelir (`tools.exec.safeBins` veya aracı başına `agents.list[].tools.exec.safeBins`).
- `safeBinTrustedDirs` yapılandırmadan gelir (`tools.exec.safeBinTrustedDirs` veya aracı başına `agents.list[].tools.exec.safeBinTrustedDirs`).
- `safeBinProfiles` yapılandırmadan gelir (`tools.exec.safeBinProfiles` veya aracı başına `agents.list[].tools.exec.safeBinProfiles`). Aracı başına profil anahtarları genel anahtarları geçersiz kılar.
- allowlist girdileri ana makinede yerel `~/.openclaw/exec-approvals.json` dosyasında `agents.<id>.allowlist` altında bulunur (veya Control UI / `openclaw approvals allowlist ...` üzerinden).
- `openclaw security audit`, yorumlayıcı/runtime ikilileri açık profiller olmadan `safeBins` içinde göründüğünde `tools.exec.safe_bins_interpreter_unprofiled` uyarısı verir.
- `openclaw doctor --fix`, eksik özel `safeBinProfiles.<bin>` girdilerini `{}` olarak iskeletleyebilir (sonrasında gözden geçirip sıkılaştırın). Yorumlayıcı/runtime ikilileri otomatik iskeletlenmez.

Özel profil örneği:
__OC_I18N_900004__
`jq` öğesini özellikle `safeBins` içine alırsanız OpenClaw yine de safe-bin
modunda `env` built-in'ini reddeder; böylece `jq -n env` açık bir izin listesi yolu
veya onay istemi olmadan ana makine süreç ortamını dökemez.

## Control UI düzenleme

Varsayılanları, aracı başına
geçersiz kılmaları ve izin listelerini düzenlemek için **Control UI → Nodes → Exec approvals** kartını kullanın. Bir kapsam seçin (Varsayılanlar veya bir aracı), ilkeyi ayarlayın,
izin listesi desenleri ekleyin/kaldırın, sonra **Kaydet** seçeneğini kullanın. UI, listeyi düzenli tutabilmeniz için
desen başına **son kullanım** meta verisini gösterir.

Hedef seçici **Gateway** (yerel onaylar) veya bir **Node** seçer. Node'ların
`system.execApprovals.get/set` ilan etmesi gerekir (macOS uygulaması veya başsız node ana makinesi).
Bir node henüz exec onaylarını ilan etmiyorsa yerel
`~/.openclaw/exec-approvals.json` dosyasını doğrudan düzenleyin.

CLI: `openclaw approvals`, gateway veya node düzenlemeyi destekler (bkz. [Approvals CLI](/cli/approvals)).

## Onay akışı

İstem gerektiğinde gateway, operatör istemcilerine `exec.approval.requested` yayını yapar.
Control UI ve macOS uygulaması bunu `exec.approval.resolve` ile çözer; ardından gateway
onaylanan isteği node ana makinesine iletir.

`host=node` için onay istekleri standart bir `systemRunPlan` yükü içerir. Gateway,
onaylanan `system.run`
isteklerini iletirken bu planı yetkili komut/cwd/oturum bağlamı olarak kullanır.

Bu, eşzamansız onay gecikmesi için önemlidir:

- node exec yolu baştan tek bir standart plan hazırlar
- onay kaydı bu planı ve bağlama meta verisini saklar
- onaylandıktan sonra son iletilen `system.run` çağrısı daha sonraki çağıran düzenlemelerine güvenmek yerine
  saklanan planı yeniden kullanır
- çağıran, onay isteği oluşturulduktan sonra `command`, `rawCommand`, `cwd`, `agentId` veya
  `sessionKey` değerlerini değiştirirse, gateway iletilen
  çalıştırmayı onay uyumsuzluğu olarak reddeder

## Yorumlayıcı/runtime komutları

Onay destekli yorumlayıcı/runtime çalıştırmaları bilinçli olarak muhafazakârdır:

- Tam argv/cwd/env bağlamı her zaman bağlanır.
- Doğrudan shell betiği ve doğrudan runtime dosyası biçimleri, en iyi çabayla tek bir somut yerel
  dosya anlık görüntüsüne bağlanır.
- Yine tek bir doğrudan yerel dosyaya çözümlenen yaygın paket yöneticisi sarmalayıcı biçimleri (örneğin
  `pnpm exec`, `pnpm node`, `npm exec`, `npx`) bağlamadan önce açılır.
- OpenClaw bir yorumlayıcı/runtime komutu için tam olarak tek bir somut yerel dosya belirleyemezse
  (örneğin paket betikleri, eval biçimleri, runtime'a özgü yükleyici zincirleri veya belirsiz çok dosyalı
  biçimler), anlamsal kapsama varmış gibi davranmak yerine onay destekli yürütmeyi reddeder.
- Bu iş akışları için sandboxing, ayrı bir ana makine sınırı veya operatörün daha geniş runtime anlambilimini kabul ettiği
  açık güvenilir allowlist/full iş akışını tercih edin.

Onay gerektiğinde exec aracı, bir onay kimliği döndürerek hemen geri gelir. Daha sonraki sistem olaylarıyla (`Exec finished` / `Exec denied`)
ilişkilendirmek için bu kimliği kullanın. Zaman aşımından önce karar gelmezse istek
onay zaman aşımı olarak ele alınır ve red nedeni olarak gösterilir.

### Devam teslim davranışı

Onaylanmış eşzamansız bir exec tamamlandıktan sonra OpenClaw, aynı oturuma bir devam `agent` dönüşü gönderir.

- Geçerli bir harici teslim hedefi varsa (teslim edilebilir kanal artı hedef `to`), devam teslimi bu kanalı kullanır.
- Harici hedefi olmayan yalnızca webchat veya dahili oturum akışlarında devam teslimi yalnızca oturum içinde kalır (`deliver: false`).
- Bir çağıran, çözümlenebilir bir harici kanal olmadan açıkça katı harici teslim isterse istek `INVALID_REQUEST` ile başarısız olur.
- `bestEffortDeliver` etkinse ve hiçbir harici kanal çözümlenemiyorsa teslim, başarısız olmak yerine yalnızca oturuma düşürülür.

Onay iletişim kutusu şunları içerir:

- komut + argümanlar
- cwd
- aracı kimliği
- çözümlenmiş yürütülebilir yol
- ana makine + ilke meta verisi

Eylemler:

- **Bir kez izin ver** → şimdi çalıştır
- **Her zaman izin ver** → izin listesine ekle + çalıştır
- **Reddet** → engelle

## Sohbet kanallarına onay iletme

Exec onay istemlerini herhangi bir sohbet kanalına (plugin kanalları dahil) iletebilir ve
bunları `/approve` ile onaylayabilirsiniz. Bu, normal giden teslim hattını kullanır.

Yapılandırma:
__OC_I18N_900005__
Sohbette şu şekilde yanıt verin:
__OC_I18N_900006__
`/approve` komutu hem exec onaylarını hem de plugin onaylarını işler. Kimlik bekleyen bir exec onayıyla eşleşmezse otomatik olarak bunun yerine plugin onaylarını denetler.

### Plugin onay iletimi

Plugin onay iletimi, exec onaylarıyla aynı teslim hattını kullanır ama
`approvals.plugin` altında kendine ait bağımsız yapılandırmaya sahiptir. Birini etkinleştirmek veya devre dışı bırakmak diğerini etkilemez.
__OC_I18N_900007__
Yapılandırma biçimi `approvals.exec` ile aynıdır: `enabled`, `mode`, `agentFilter`,
`sessionFilter` ve `targets` aynı şekilde çalışır.

Paylaşılan etkileşimli yanıtları destekleyen kanallar hem exec hem de
plugin onayları için aynı onay düğmelerini gösterir. Paylaşılan etkileşimli UI'ı olmayan kanallar,
`/approve` yönergeleri içeren düz metne geri döner.

### Herhangi bir kanalda aynı sohbetten onay

Bir exec veya plugin onay isteği teslim edilebilir bir sohbet yüzeyinden geliyorsa, artık varsayılan olarak
aynı sohbet bunu `/approve` ile onaylayabilir. Bu, mevcut Web UI ve terminal UI akışlarına ek olarak Slack, Matrix ve
Microsoft Teams gibi kanallara da uygulanır.

Bu paylaşılan metin komutu yolu, o konuşma için normal kanal auth modelini kullanır. Kaynak sohbet
zaten komut gönderebiliyor ve yanıt alabiliyorsa, onay isteklerinin beklemede kalması için artık ayrı bir yerel teslim bağdaştırıcısına gerek yoktur.

Discord ve Telegram da aynı sohbetten `/approve` desteğine sahiptir, ancak bu kanallar
yerel onay teslimi devre dışı olsa bile yetkilendirme için yine çözümlenmiş onaylayıcı listelerini kullanır.

Gateway'i doğrudan çağıran Telegram ve diğer yerel onay istemcileri için,
bu fallback bilinçli olarak "onay bulunamadı" hatalarıyla sınırlıdır. Gerçek bir
exec onayı reddi/hatası sessizce plugin onayı olarak yeniden denenmez.

### Yerel onay teslimi

Bazı kanallar ayrıca yerel onay istemcisi olarak da davranabilir. Yerel istemciler, paylaşılan aynı sohbetten `/approve`
akışının üzerine onaylayıcı DM'leri, kaynak sohbet fanout'u ve kanala özgü etkileşimli onay UX'i ekler.

Yerel onay kartları/düğmeleri mevcut olduğunda, bu yerel UI aracıya dönük birincil
yoldur. Araç sonucu sohbet onaylarının kullanılamadığını veya
tek kalan yolun el ile onay olduğunu söylemiyorsa, aracı ayrıca
yinelenen düz bir sohbet `/approve` komutu da yinelememelidir.

Genel model:

- ana makine exec ilkesi, exec onayının gerekip gerekmediğine yine karar verir
- `approvals.exec`, onay istemlerinin diğer sohbet hedeflerine iletilmesini denetler
- `channels.<channel>.execApprovals`, o kanalın yerel onay istemcisi olarak davranıp davranmadığını denetler

Yerel onay istemcileri, şu koşulların tümü doğruysa DM-first teslimi otomatik etkinleştirir:

- kanal yerel onay teslimini destekliyordur
- onaylayıcılar açık `execApprovals.approvers` veya o
  kanalın belgelenmiş fallback kaynaklarından çözümlenebiliyordur
- `channels.<channel>.execApprovals.enabled` ayarsızdır veya `"auto"` değerindedir

Bir yerel onay istemcisini açıkça devre dışı bırakmak için `enabled: false` ayarlayın. Onaylayıcılar çözümlendiğinde zorla
etkinleştirmek için `enabled: true` ayarlayın. Genel kaynak-sohbet teslimi ise
`channels.<channel>.execApprovals.target` üzerinden açık kalır.

SSS: [Sohbet onayları için neden iki exec onay yapılandırması var?](/help/faq#why-are-there-two-exec-approval-configs-for-chat-approvals)

- Discord: `channels.discord.execApprovals.*`
- Slack: `channels.slack.execApprovals.*`
- Telegram: `channels.telegram.execApprovals.*`

Bu yerel onay istemcileri, paylaşılan aynı sohbetten `/approve` akışı ve paylaşılan onay düğmelerinin üzerine
DM yönlendirmesi ve isteğe bağlı kanal fanout'u ekler.

Paylaşılan davranış:

- Slack, Matrix, Microsoft Teams ve benzeri teslim edilebilir sohbetler
  aynı sohbetten `/approve` için normal kanal auth modelini kullanır
- yerel bir onay istemcisi otomatik etkinleştiğinde, varsayılan yerel teslim hedefi onaylayıcı DM'leridir
- Discord ve Telegram için yalnızca çözümlenmiş onaylayıcılar onaylayabilir veya reddedebilir
- Discord onaylayıcıları açık olabilir (`execApprovals.approvers`) veya `commands.ownerAllowFrom` değerinden çıkarılabilir
- Telegram onaylayıcıları açık olabilir (`execApprovals.approvers`) veya mevcut owner yapılandırmasından çıkarılabilir (`allowFrom`, ayrıca desteklendiğinde doğrudan mesaj `defaultTo`)
- Slack onaylayıcıları açık olabilir (`execApprovals.approvers`) veya `commands.ownerAllowFrom` değerinden çıkarılabilir
- Slack yerel düğmeleri onay kimliği türünü korur; böylece `plugin:` kimlikleri ikinci bir Slack-yerel fallback katmanı olmadan
  plugin onaylarını çözebilir
- Matrix yerel DM/kanal yönlendirmesi ve tepki kısayolları hem exec hem de plugin onaylarını işler;
  plugin yetkilendirmesi yine `channels.matrix.dm.allowFrom` değerinden gelir
- isteği yapanın onaylayıcı olması gerekmez
- kaynak sohbet zaten komutları ve yanıtları destekliyorsa kaynak sohbet doğrudan `/approve` ile onaylayabilir
- yerel Discord onay düğmeleri onay kimliği türüne göre yönlendirir: `plugin:` kimlikleri
  doğrudan plugin onaylarına gider, diğer her şey exec onaylarına gider
- yerel Telegram onay düğmeleri `/approve` ile aynı sınırlı exec'den plugin'e fallback davranışını izler
- yerel `target`, kaynak-sohbet teslimini etkinleştirdiğinde onay istemleri komut metnini içerir
- bekleyen exec onayları varsayılan olarak 30 dakika sonra sona erer
- hiçbir operatör UI'ı veya yapılandırılmış onay istemcisi isteği kabul edemiyorsa istem `askFallback` değerine geri döner

Telegram varsayılan olarak onaylayıcı DM'lerini kullanır (`target: "dm"`). Onay istemlerinin kaynak Telegram sohbetinde/konusunda da görünmesini istediğinizde bunu
`channel` veya `both` olarak değiştirebilirsiniz. Telegram forum konularında OpenClaw,
onay istemi ve onay sonrası devam için konuyu korur.

Bkz.:

- [Discord](/channels/discord)
- [Telegram](/channels/telegram)

### macOS IPC akışı
__OC_I18N_900008__
Güvenlik notları:

- Unix socket modu `0600`, token `exec-approvals.json` içinde saklanır.
- Aynı UID eş kontrolü.
- Challenge/response (nonce + HMAC token + istek hash'i) + kısa TTL.

## Sistem olayları

Exec yaşam döngüsü sistem mesajları olarak yüzeye çıkarılır:

- `Exec running` (yalnızca komut çalışma bildirimi eşiğini aşarsa)
- `Exec finished`
- `Exec denied`

Bunlar, node olayı bildirdikten sonra aracının oturumuna gönderilir.
Gateway-ana-makine exec onayları da komut bittiğinde (ve isteğe bağlı olarak çalışma eşiğinden daha uzun sürdüğünde) aynı yaşam döngüsü olaylarını yayar.
Onay geçitli exec'ler, kolay ilişkilendirme için bu mesajlarda `runId` olarak onay kimliğini yeniden kullanır.

## Reddedilen onay davranışı

Eşzamansız bir exec onayı reddedildiğinde OpenClaw, aracının
oturumda aynı komutun daha önceki bir çalıştırmasından gelen çıktıyı yeniden kullanmasını önler. Red nedeni,
komut çıktısının mevcut olmadığına dair açık rehberlikle iletilir; bu da
aracının yeni çıktı varmış gibi davranmasını veya daha önceki başarılı bir çalıştırmadan kalan sonuçlarla
reddedilmiş komutu yinelemesini durdurur.

## Etkiler

- **full** güçlüdür; mümkün olduğunda allowlist tercih edin.
- **ask**, hızlı onaylara izin verirken sizi döngünün içinde tutar.
- Aracı başına allowlist'ler, bir aracının onaylarının diğerlerine sızmasını önler.
- Onaylar yalnızca **yetkili göndericilerden** gelen ana makine exec isteklerine uygulanır. Yetkisiz göndericiler `/exec` veremez.
- `/exec security=full`, yetkili operatörler için oturum düzeyinde bir kolaylıktır ve tasarım gereği onayları atlar.
  Ana makinede exec'i kesin olarak engellemek için onay güvenliğini `deny` olarak ayarlayın veya araç ilkesi üzerinden `exec` aracını reddedin.

İlgili:

- [Exec aracı](/tr/tools/exec)
- [Elevated mode](/tr/tools/elevated)
- [Skills](/tr/tools/skills)

## İlgili

- [Exec](/tr/tools/exec) — shell komutu yürütme aracı
- [Sandboxing](/tr/gateway/sandboxing) — sandbox modları ve çalışma alanı erişimi
- [Security](/tr/gateway/security) — güvenlik modeli ve sertleştirme
- [Sandbox vs Tool Policy vs Elevated](/tr/gateway/sandbox-vs-tool-policy-vs-elevated) — her biri ne zaman kullanılmalı
