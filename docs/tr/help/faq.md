---
read_when:
    - Yaygın kurulum, yükleme, onboarding veya çalışma zamanı destek sorularını yanıtlama
    - Daha derin hata ayıklamadan önce kullanıcı tarafından bildirilen sorunları ön değerlendirmeden geçirme
summary: OpenClaw kurulumu, yapılandırması ve kullanımı hakkında sık sorulan sorular
title: SSS
x-i18n:
    generated_at: "2026-04-08T02:20:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: 001b4605966b45b08108606f76ae937ec348c2179b04cf6fb34fef94833705e6
    source_path: help/faq.md
    workflow: 15
---

# SSS

Gerçek dünya kurulumları için hızlı yanıtlar ve daha derin sorun giderme (yerel geliştirme, VPS, çoklu ajan, OAuth/API anahtarları, model devretme). Çalışma zamanı tanılamaları için bkz. [Sorun Giderme](/tr/gateway/troubleshooting). Tam yapılandırma başvurusu için bkz. [Yapılandırma](/tr/gateway/configuration).

## Bir şey bozuksa ilk 60 saniye

1. **Hızlı durum (ilk kontrol)**

   ```bash
   openclaw status
   ```

   Hızlı yerel özet: işletim sistemi + güncelleme, gateway/hizmet erişilebilirliği, ajanlar/oturumlar, sağlayıcı yapılandırması + çalışma zamanı sorunları (gateway erişilebilirse).

2. **Paylaşılabilir rapor (paylaşması güvenli)**

   ```bash
   openclaw status --all
   ```

   Günlük sonuyla birlikte salt okunur tanılama (token'lar gizlenir).

3. **Daemon + port durumu**

   ```bash
   openclaw gateway status
   ```

   Denetleyici çalışma zamanı ile RPC erişilebilirliğini, probe hedef URL'sini ve hizmetin büyük olasılıkla hangi yapılandırmayı kullandığını gösterir.

4. **Derin probe'lar**

   ```bash
   openclaw status --deep
   ```

   Destekleniyorsa kanal probe'ları dahil canlı gateway sağlık probe'u çalıştırır
   (erişilebilir bir gateway gerekir). Bkz. [Sağlık](/tr/gateway/health).

5. **En son günlüğü takip et**

   ```bash
   openclaw logs --follow
   ```

   RPC kapalıysa şuna dönün:

   ```bash
   tail -f "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)"
   ```

   Dosya günlükleri hizmet günlüklerinden ayrıdır; bkz. [Günlükleme](/tr/logging) ve [Sorun Giderme](/tr/gateway/troubleshooting).

6. **Doctor'ı çalıştır (onarım)**

   ```bash
   openclaw doctor
   ```

   Yapılandırma/durumu onarır veya taşır + sağlık kontrolleri çalıştırır. Bkz. [Doctor](/tr/gateway/doctor).

7. **Gateway anlık görüntüsü**

   ```bash
   openclaw health --json
   openclaw health --verbose   # hatalarda hedef URL + yapılandırma yolunu gösterir
   ```

   Çalışan gateway'den tam bir anlık görüntü ister (yalnızca WS). Bkz. [Sağlık](/tr/gateway/health).

## Hızlı başlangıç ve ilk çalıştırma kurulumu

<AccordionGroup>
  <Accordion title="Takıldım, takılmayı aşmanın en hızlı yolu">
    Makinenizi **görebilen** yerel bir AI ajanı kullanın. Bu, Discord'da sormaktan çok daha etkilidir,
    çünkü “takıldım” vakalarının çoğu uzaktaki yardımcıların inceleyemediği **yerel yapılandırma veya ortam sorunlarıdır**.

    - **Claude Code**: [https://www.anthropic.com/claude-code/](https://www.anthropic.com/claude-code/)
    - **OpenAI Codex**: [https://openai.com/codex/](https://openai.com/codex/)

    Bu araçlar depoyu okuyabilir, komut çalıştırabilir, günlükleri inceleyebilir ve makine düzeyindeki
    kurulumunuzu (PATH, hizmetler, izinler, kimlik doğrulama dosyaları) düzeltmenize yardımcı olabilir.
    Onlara hacklenebilir (git) kurulum üzerinden **tam kaynak checkout'unu** verin:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Bu, OpenClaw'u **bir git checkout'undan** kurar; böylece ajan kodu + belgeleri okuyabilir ve
    çalıştırdığınız tam sürüm üzerinde akıl yürütebilir. Daha sonra yükleyiciyi `--install-method git`
    olmadan yeniden çalıştırarak istediğiniz zaman yeniden stable sürüme dönebilirsiniz.

    İpucu: ajandan düzeltmeyi **planlamasını ve denetlemesini** isteyin (adım adım), ardından yalnızca
    gerekli komutları çalıştırın. Bu, değişiklikleri küçük ve denetlenmesini kolay tutar.

    Gerçek bir hata veya düzeltme keşfederseniz lütfen bir GitHub issue açın veya bir PR gönderin:
    [https://github.com/openclaw/openclaw/issues](https://github.com/openclaw/openclaw/issues)
    [https://github.com/openclaw/openclaw/pulls](https://github.com/openclaw/openclaw/pulls)

    Şu komutlarla başlayın (yardım isterken çıktıları paylaşın):

    ```bash
    openclaw status
    openclaw models status
    openclaw doctor
    ```

    Yaptıkları:

    - `openclaw status`: gateway/ajan sağlığı + temel yapılandırmanın hızlı anlık görüntüsü.
    - `openclaw models status`: sağlayıcı kimlik doğrulamasını + model kullanılabilirliğini kontrol eder.
    - `openclaw doctor`: yaygın yapılandırma/durum sorunlarını doğrular ve onarır.

    Diğer yararlı CLI kontrolleri: `openclaw status --all`, `openclaw logs --follow`,
    `openclaw gateway status`, `openclaw health --verbose`.

    Hızlı hata ayıklama döngüsü: [Bir şey bozuksa ilk 60 saniye](#bir-şey-bozuksa-ilk-60-saniye).
    Kurulum belgeleri: [Yükleme](/tr/install), [Yükleyici bayrakları](/tr/install/installer), [Güncelleme](/tr/install/updating).

  </Accordion>

  <Accordion title="Heartbeat atlamaya devam ediyor. Atlama nedenleri ne anlama geliyor?">
    Yaygın heartbeat atlama nedenleri:

    - `quiet-hours`: yapılandırılmış aktif saatler penceresinin dışında
    - `empty-heartbeat-file`: `HEARTBEAT.md` var ama yalnızca boş/başlık içeren iskelet içeriyor
    - `no-tasks-due`: `HEARTBEAT.md` görev modu etkin ama görev aralıklarının hiçbiri henüz zamanı gelmemiş
    - `alerts-disabled`: tüm heartbeat görünürlüğü kapalı (`showOk`, `showAlerts` ve `useIndicator` hepsi kapalı)

    Görev modunda, zamanı gelen zaman damgaları yalnızca gerçek bir heartbeat çalıştırması
    tamamlandıktan sonra ilerletilir. Atlanan çalıştırmalar görevleri tamamlandı olarak işaretlemez.

    Belgeler: [Heartbeat](/tr/gateway/heartbeat), [Otomasyon ve Görevler](/tr/automation).

  </Accordion>

  <Accordion title="OpenClaw'u yükleyip kurmanın önerilen yolu">
    Depo kaynak koddan çalıştırmayı ve onboarding kullanmayı önerir:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash
    openclaw onboard --install-daemon
    ```

    Sihirbaz ayrıca UI varlıklarını otomatik olarak derleyebilir. Onboarding'den sonra genellikle Gateway'i **18789** portunda çalıştırırsınız.

    Kaynak koddan (katkıda bulunanlar/geliştiriciler):

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    pnpm ui:build # ilk çalıştırmada UI bağımlılıklarını otomatik yükler
    openclaw onboard
    ```

    Henüz global kurulumunuz yoksa bunu `pnpm openclaw onboard` ile çalıştırın.

  </Accordion>

  <Accordion title="Onboarding'den sonra panoyu nasıl açarım?">
    Sihirbaz onboarding'den hemen sonra tarayıcınızı temiz (token içermeyen) bir pano URL'siyle açar ve bağlantıyı özet içinde de yazdırır. O sekmeyi açık tutun; açılmadıysa aynı makinede yazdırılan URL'yi kopyalayıp yapıştırın.
  </Accordion>

  <Accordion title="Panoyu localhost'ta ve uzakta nasıl kimlik doğrularım?">
    **Localhost (aynı makine):**

    - `http://127.0.0.1:18789/` adresini açın.
    - Paylaşılan gizli anahtar kimlik doğrulaması isterse, yapılandırılmış token veya parolayı Control UI ayarlarına yapıştırın.
    - Token kaynağı: `gateway.auth.token` (veya `OPENCLAW_GATEWAY_TOKEN`).
    - Parola kaynağı: `gateway.auth.password` (veya `OPENCLAW_GATEWAY_PASSWORD`).
    - Henüz paylaşılan gizli anahtar yapılandırılmadıysa `openclaw doctor --generate-gateway-token` ile bir token oluşturun.

    **Localhost değilse:**

    - **Tailscale Serve** (önerilir): bağlamayı loopback olarak tutun, `openclaw gateway --tailscale serve` çalıştırın, `https://<magicdns>/` açın. `gateway.auth.allowTailscale` değeri `true` ise, kimlik başlıkları Control UI/WebSocket kimlik doğrulamasını karşılar (yapıştırılan paylaşılan gizli anahtar gerekmez, güvenilir gateway host varsayılır); HTTP API'leri ise özel olarak private-ingress `none` veya trusted-proxy HTTP auth kullanmadığınız sürece yine paylaşılan gizli anahtar kimlik doğrulaması gerektirir.
      Aynı istemciden gelen hatalı eşzamanlı Serve auth denemeleri, başarısız auth sınırlayıcısı bunları kaydetmeden önce seri hale getirilir; bu yüzden ikinci hatalı deneme zaten `retry later` gösterebilir.
    - **Tailnet bind**: `openclaw gateway --bind tailnet --token "<token>"` çalıştırın (veya parola kimlik doğrulamasını yapılandırın), `http://<tailscale-ip>:18789/` açın, ardından panoda eşleşen paylaşılan gizli anahtarı yapıştırın.
    - **Kimlik farkındalıklı reverse proxy**: Gateway'i loopback olmayan güvenilir bir proxy arkasında tutun, `gateway.auth.mode: "trusted-proxy"` yapılandırın, ardından proxy URL'sini açın.
    - **SSH tunnel**: `ssh -N -L 18789:127.0.0.1:18789 user@host` sonra `http://127.0.0.1:18789/` açın. Tunnel üzerinden de paylaşılan gizli anahtar kimlik doğrulaması geçerlidir; istenirse yapılandırılmış token veya parolayı yapıştırın.

    Bağlama kipleri ve auth ayrıntıları için bkz. [Pano](/web/dashboard) ve [Web yüzeyleri](/web).

  </Accordion>

  <Accordion title="Sohbet onayları için neden iki exec approval yapılandırması var?">
    Bunlar farklı katmanları kontrol eder:

    - `approvals.exec`: onay istemlerini sohbet hedeflerine iletir
    - `channels.<channel>.execApprovals`: o kanalın exec onayları için yerel bir onay istemcisi gibi davranmasını sağlar

    Host exec ilkesi hâlâ gerçek onay kapısıdır. Sohbet yapılandırması yalnızca onay
    istemlerinin nerede görüneceğini ve insanların nasıl yanıt verebileceğini kontrol eder.

    Çoğu kurulumda **ikisinin de** gerekli olması gerekmez:

    - Sohbet zaten komutları ve yanıtları destekliyorsa, aynı sohbet içindeki `/approve` paylaşılan yol üzerinden çalışır.
    - Desteklenen yerel bir kanal onay verenleri güvenli biçimde çıkarım yapabiliyorsa, OpenClaw artık `channels.<channel>.execApprovals.enabled` ayarlanmamışsa veya `"auto"` ise DM-öncelikli yerel onayları otomatik etkinleştirir.
    - Yerel onay kartları/düğmeleri mevcut olduğunda, birincil yol bu yerel UI'dır; araç sonucu sohbet onaylarının kullanılamadığını veya tek yolun elle onay olduğunu söylemiyorsa ajan yalnızca manuel `/approve` komutunu eklemelidir.
    - İstemlerin ayrıca başka sohbetlere veya belirli operasyon odalarına da iletilmesi gerekiyorsa yalnızca `approvals.exec` kullanın.
    - Yalnızca onay istemlerinin kaynak oda/konuya da geri gönderilmesini açıkça istiyorsanız `channels.<channel>.execApprovals.target: "channel"` veya `"both"` kullanın.
    - Plugin onayları ise yine ayrıdır: varsayılan olarak aynı sohbet içindeki `/approve`, isteğe bağlı `approvals.plugin` iletimi kullanırlar ve yalnızca bazı yerel kanallar bunun üzerinde plugin-approval-native işlemesini tutar.

    Kısaca: iletme yönlendirme içindir, yerel istemci yapılandırması daha zengin kanala özgü UX içindir.
    Bkz. [Exec Onayları](/tr/tools/exec-approvals).

  </Accordion>

  <Accordion title="Hangi çalışma zamanına ihtiyacım var?">
    Node **>= 22** gereklidir. `pnpm` önerilir. Gateway için Bun **önerilmez**.
  </Accordion>

  <Accordion title="Raspberry Pi üzerinde çalışır mı?">
    Evet. Gateway hafiftir - belgeler kişisel kullanım için **512MB-1GB RAM**, **1 çekirdek** ve yaklaşık **500MB**
    diskin yeterli olduğunu ve bir **Raspberry Pi 4** üzerinde çalışabildiğini belirtir.

    Ek boşluk istiyorsanız (günlükler, medya, diğer hizmetler), **2GB önerilir**, ancak
    bu katı bir alt sınır değildir.

    İpucu: küçük bir Pi/VPS Gateway'i barındırabilir ve yerel ekran/kamera/canvas ya da
    komut yürütme için dizüstü bilgisayarınızda/telefonunuzda **node** eşleştirebilirsiniz. Bkz. [Nodes](/tr/nodes).

  </Accordion>

  <Accordion title="Raspberry Pi kurulumları için ipuçları var mı?">
    Kısaca: çalışır, ancak pürüzler bekleyin.

    - **64 bit** bir işletim sistemi kullanın ve Node sürümünü >= 22 tutun.
    - Günlükleri görebilmek ve hızlı güncelleyebilmek için **hacklenebilir (git) kurulumu** tercih edin.
    - Kanal/Skills olmadan başlayın, sonra bunları teker teker ekleyin.
    - Garip binary sorunlarıyla karşılaşırsanız, bu genelde bir **ARM uyumluluk** sorunudur.

    Belgeler: [Linux](/tr/platforms/linux), [Yükleme](/tr/install).

  </Accordion>

  <Accordion title="Wake up my friend ekranında takılıyor / onboarding hatch olmuyor. Ne yapmalıyım?">
    Bu ekran Gateway'in erişilebilir ve kimliği doğrulanmış olmasına bağlıdır. TUI ayrıca
    ilk hatch sırasında otomatik olarak "Wake up, my friend!" gönderir. Bu satırı **yanıt olmadan**
    görüyorsanız ve token'lar 0'da kalıyorsa, ajan hiç çalışmamıştır.

    1. Gateway'i yeniden başlatın:

    ```bash
    openclaw gateway restart
    ```

    2. Durumu + auth'u kontrol edin:

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    3. Hâlâ takılıyorsa şunu çalıştırın:

    ```bash
    openclaw doctor
    ```

    Gateway uzaktaysa, tunnel/Tailscale bağlantısının açık olduğundan ve UI'ın
    doğru Gateway'e yönlendirildiğinden emin olun. Bkz. [Uzaktan erişim](/tr/gateway/remote).

  </Accordion>

  <Accordion title="Kurulumumu yeni bir makineye (Mac mini) onboarding'i yeniden yapmadan taşıyabilir miyim?">
    Evet. **Durum dizinini** ve **çalışma alanını** kopyalayın, ardından Doctor'ı bir kez çalıştırın. Bu,
    **her iki** konumu da kopyaladığınız sürece botunuzu “tam olarak aynı” (hafıza, oturum geçmişi, auth ve kanal
    durumu) halde tutar:

    1. Yeni makineye OpenClaw kurun.
    2. Eski makineden `$OPENCLAW_STATE_DIR` (varsayılan: `~/.openclaw`) dizinini kopyalayın.
    3. Çalışma alanınızı kopyalayın (varsayılan: `~/.openclaw/workspace`).
    4. `openclaw doctor` çalıştırın ve Gateway hizmetini yeniden başlatın.

    Bu, yapılandırmayı, auth profillerini, WhatsApp kimlik bilgilerini, oturumları ve hafızayı korur. Eğer
    uzak moddaysanız, oturum deposu ve çalışma alanının sahibi gateway host'tur.

    **Önemli:** Yalnızca çalışma alanınızı GitHub'a commit/push ederseniz,
    **hafıza + bootstrap dosyalarını** yedeklemiş olursunuz; ancak **oturum geçmişini veya auth'u** değil.
    Bunlar `~/.openclaw/` altında yaşar (örneğin `~/.openclaw/agents/<agentId>/sessions/`).

    İlgili: [Taşıma](/tr/install/migrating), [Diskte neler nerededir](#diskte-neler-nerededir),
    [Ajan çalışma alanı](/tr/concepts/agent-workspace), [Doctor](/tr/gateway/doctor),
    [Uzak mod](/tr/gateway/remote).

  </Accordion>

  <Accordion title="En son sürümde nelerin yeni olduğunu nerede görürüm?">
    GitHub changelog'una bakın:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    En yeni girdiler en üsttedir. En üst bölüm **Unreleased** olarak işaretliyse, bir sonraki tarihli
    bölüm yayımlanmış en son sürümdür. Girdiler **Highlights**, **Changes** ve
    **Fixes** olarak gruplanır (gerektiğinde docs/other bölümleriyle birlikte).

  </Accordion>

  <Accordion title="docs.openclaw.ai sitesine erişemiyorum (SSL hatası)">
    Bazı Comcast/Xfinity bağlantıları `docs.openclaw.ai` alanını Xfinity
    Advanced Security üzerinden hatalı şekilde engelliyor. Bunu devre dışı bırakın veya `docs.openclaw.ai` alanını allowlist'e ekleyin, sonra tekrar deneyin.
    Engeli kaldırmamıza yardımcı olmak için lütfen burada bildirin: [https://spa.xfinity.com/check_url_status](https://spa.xfinity.com/check_url_status).

    Siteye hâlâ erişemiyorsanız, belgeler GitHub üzerinde yansılanmıştır:
    [https://github.com/openclaw/openclaw/tree/main/docs](https://github.com/openclaw/openclaw/tree/main/docs)

  </Accordion>

  <Accordion title="stable ile beta arasındaki fark">
    **Stable** ve **beta**, ayrı kod hatları değil, **npm dist-tag**'leridir:

    - `latest` = stable
    - `beta` = test için erken derleme

    Genellikle bir stable sürüm önce **beta**'ya gelir, sonra açık bir
    promotion adımı aynı sürümü `latest`'e taşır. Maintainer'lar gerektiğinde doğrudan
    `latest`'e de yayımlayabilir. Bu yüzden promotion sonrasında beta ve stable
    **aynı sürümü** gösterebilir.

    Nelerin değiştiğine bakın:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    Tek satırlık kurulumlar ve beta ile dev arasındaki fark için aşağıdaki accordion'a bakın.

  </Accordion>

  <Accordion title="Beta sürümü nasıl yüklerim ve beta ile dev arasındaki fark nedir?">
    **Beta**, npm dist-tag `beta`'dır (`latest` ile promotion sonrasında eşleşebilir).
    **Dev**, `main` dalının hareketli tepesidir (git); yayımlandığında npm dist-tag `dev` kullanır.

    Tek satırlık kurulumlar (macOS/Linux):

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --beta
    ```

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Windows yükleyici (PowerShell):
    [https://openclaw.ai/install.ps1](https://openclaw.ai/install.ps1)

    Daha fazla ayrıntı: [Geliştirme kanalları](/tr/install/development-channels) ve [Yükleyici bayrakları](/tr/install/installer).

  </Accordion>

  <Accordion title="En yeni parçaları nasıl denerim?">
    İki seçenek:

    1. **Dev kanalı (git checkout):**

    ```bash
    openclaw update --channel dev
    ```

    Bu sizi `main` dalına geçirir ve kaynaktan günceller.

    2. **Hacklenebilir kurulum (yükleyici sitesinden):**

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Bu size düzenleyebileceğiniz bir yerel depo verir, sonra git üzerinden güncelleyebilirsiniz.

    Manuel temiz bir clone tercih ederseniz şunu kullanın:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    ```

    Belgeler: [Güncelleme](/cli/update), [Geliştirme kanalları](/tr/install/development-channels),
    [Yükleme](/tr/install).

  </Accordion>

  <Accordion title="Kurulum ve onboarding genelde ne kadar sürer?">
    Kabaca:

    - **Kurulum:** 2-5 dakika
    - **Onboarding:** yapılandırdığınız kanal/model sayısına bağlı olarak 5-15 dakika

    Takılırsa [Yükleyici takıldı](#hızlı-başlangıç-ve-ilk-çalıştırma-kurulumu)
    ve [Takıldım](#hızlı-başlangıç-ve-ilk-çalıştırma-kurulumu) içindeki hızlı hata ayıklama döngüsünü kullanın.

  </Accordion>

  <Accordion title="Yükleyici takıldı mı? Daha fazla geri bildirimi nasıl alırım?">
    Yükleyiciyi **ayrıntılı çıktı** ile yeniden çalıştırın:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --verbose
    ```

    Ayrıntılı beta kurulumu:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --beta --verbose
    ```

    Hacklenebilir (git) kurulum için:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git --verbose
    ```

    Windows (PowerShell) eşdeğeri:

    ```powershell
    # install.ps1 dosyasında henüz özel bir -Verbose bayrağı yok.
    Set-PSDebug -Trace 1
    & ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -NoOnboard
    Set-PSDebug -Trace 0
    ```

    Daha fazla seçenek: [Yükleyici bayrakları](/tr/install/installer).

  </Accordion>

  <Accordion title="Windows kurulumu git not found veya openclaw not recognized diyor">
    İki yaygın Windows sorunu:

    **1) npm error spawn git / git not found**

    - **Git for Windows** yükleyin ve `git` komutunun PATH üzerinde olduğundan emin olun.
    - PowerShell'i kapatıp yeniden açın, sonra yükleyiciyi tekrar çalıştırın.

    **2) Kurulumdan sonra openclaw is not recognized**

    - npm global bin klasörünüz PATH üzerinde değil.
    - Yolu kontrol edin:

      ```powershell
      npm config get prefix
      ```

    - Bu dizini kullanıcı PATH'inize ekleyin (Windows'ta `\bin` soneki gerekmez; çoğu sistemde `%AppData%\npm` olur).
    - PATH'i güncelledikten sonra PowerShell'i kapatıp yeniden açın.

    En sorunsuz Windows kurulumu için native Windows yerine **WSL2** kullanın.
    Belgeler: [Windows](/tr/platforms/windows).

  </Accordion>

  <Accordion title="Windows exec çıktısı bozuk Çince metin gösteriyor - ne yapmalıyım?">
    Bu genellikle native Windows shell'lerinde konsol kod sayfası uyumsuzluğudur.

    Belirtiler:

    - `system.run`/`exec` çıktısı Çince'yi bozuk karakterlerle gösterir
    - Aynı komut başka bir terminal profilinde düzgün görünür

    PowerShell'de hızlı geçici çözüm:

    ```powershell
    chcp 65001
    [Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    ```

    Sonra Gateway'i yeniden başlatın ve komutunuzu tekrar deneyin:

    ```powershell
    openclaw gateway restart
    ```

    Bunu en yeni OpenClaw sürümünde de yeniden üretebiliyorsanız şurada izleyin/bildirin:

    - [Issue #30640](https://github.com/openclaw/openclaw/issues/30640)

  </Accordion>

  <Accordion title="Belgeler sorumu yanıtlamadı - daha iyi bir yanıtı nasıl alırım?">
    Tam kaynak ve belgelere yerelde sahip olmak için **hacklenebilir (git) kurulum** kullanın, ardından
    botunuza (veya Claude/Codex'e) _o klasörden_ sorun; böylece depoyu okuyup net yanıt verebilir.

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Daha fazla ayrıntı: [Yükleme](/tr/install) ve [Yükleyici bayrakları](/tr/install/installer).

  </Accordion>

  <Accordion title="OpenClaw'u Linux'a nasıl yüklerim?">
    Kısa yanıt: Linux rehberini izleyin, sonra onboarding çalıştırın.

    - Linux hızlı yol + hizmet kurulumu: [Linux](/tr/platforms/linux).
    - Tam kılavuz: [Başlarken](/tr/start/getting-started).
    - Yükleyici + güncellemeler: [Yükleme ve güncellemeler](/tr/install/updating).

  </Accordion>

  <Accordion title="OpenClaw'u bir VPS'e nasıl yüklerim?">
    Herhangi bir Linux VPS çalışır. Sunucuya kurun, sonra Gateway'e erişmek için SSH/Tailscale kullanın.

    Rehberler: [exe.dev](/tr/install/exe-dev), [Hetzner](/tr/install/hetzner), [Fly.io](/tr/install/fly).
    Uzak erişim: [Gateway remote](/tr/gateway/remote).

  </Accordion>

  <Accordion title="Bulut/VPS kurulum rehberleri nerede?">
    Yaygın sağlayıcıları içeren bir **barındırma merkezi** tutuyoruz. Birini seçin ve rehberi izleyin:

    - [VPS hosting](/tr/vps) (tüm sağlayıcılar tek yerde)
    - [Fly.io](/tr/install/fly)
    - [Hetzner](/tr/install/hetzner)
    - [exe.dev](/tr/install/exe-dev)

    Bulutta nasıl çalışır: **Gateway sunucuda çalışır**, siz de ona
    dizüstü bilgisayarınızdan/telefonunuzdan Control UI (veya Tailscale/SSH) ile erişirsiniz. Durumunuz + çalışma alanınız
    sunucuda yaşar; bu yüzden host'u doğruluk kaynağı olarak değerlendirin ve yedekleyin.

    Yerel ekran/kamera/canvas erişimi için veya
    Gateway bulutta kalırken dizüstünüzde komut çalıştırmak için o bulut Gateway'ine **nodes**
    (Mac/iOS/Android/headless) eşleştirebilirsiniz.

    Merkez: [Platformlar](/tr/platforms). Uzak erişim: [Gateway remote](/tr/gateway/remote).
    Nodes: [Nodes](/tr/nodes), [Nodes CLI](/cli/nodes).

  </Accordion>

  <Accordion title="OpenClaw'dan kendini güncellemesini isteyebilir miyim?">
    Kısa yanıt: **mümkün, önerilmez**. Güncelleme akışı Gateway'i yeniden başlatabilir
    (bu da etkin oturumu düşürür), temiz bir git checkout gerekebilir ve
    onay isteyebilir. Daha güvenli yol: güncellemeleri operatör olarak shell'den çalıştırmak.

    CLI kullanın:

    ```bash
    openclaw update
    openclaw update status
    openclaw update --channel stable|beta|dev
    openclaw update --tag <dist-tag|version>
    openclaw update --no-restart
    ```

    Bir ajandan otomasyon yapmanız gerekiyorsa:

    ```bash
    openclaw update --yes --no-restart
    openclaw gateway restart
    ```

    Belgeler: [Güncelleme](/cli/update), [Güncelleme](/tr/install/updating).

  </Accordion>

  <Accordion title="Onboarding aslında ne yapıyor?">
    `openclaw onboard` önerilen kurulum yoludur. **Yerel modda** size şunlarda rehberlik eder:

    - **Model/auth kurulumu** (sağlayıcı OAuth, API anahtarları, Anthropic setup-token ve LM Studio gibi yerel model seçenekleri)
    - **Çalışma alanı** konumu + bootstrap dosyaları
    - **Gateway ayarları** (bind/port/auth/tailscale)
    - **Kanallar** (WhatsApp, Telegram, Discord, Mattermost, Signal, iMessage ve QQ Bot gibi paketli kanal plugin'leri)
    - **Daemon kurulumu** (macOS'ta LaunchAgent; Linux/WSL2'de systemd user unit)
    - **Sağlık kontrolleri** ve **Skills** seçimi

    Ayrıca yapılandırılmış modeliniz bilinmiyorsa veya auth eksikse uyarır.

  </Accordion>

  <Accordion title="Bunu çalıştırmak için Claude veya OpenAI aboneliğine ihtiyacım var mı?">
    Hayır. OpenClaw'u **API anahtarlarıyla** (Anthropic/OpenAI/diğerleri) veya
    verileriniz cihazınızda kalsın diye **yalnızca yerel modellerle** çalıştırabilirsiniz.
    Abonelikler (Claude Pro/Max veya OpenAI Codex), bu sağlayıcılarla kimlik doğrulamanın isteğe bağlı yollarıdır.

    Anthropic için OpenClaw'daki pratik ayrım şudur:

    - **Anthropic API key**: normal Anthropic API faturalaması
    - **OpenClaw içinde Claude CLI / Claude abonelik auth'u**: Anthropic çalışanları
      bize bunun tekrar izinli olduğunu söyledi ve Anthropic yeni bir
      politika yayımlamadıkça OpenClaw, `claude -p` kullanımını bu entegrasyon için onaylı kabul ediyor

    Uzun ömürlü gateway host'ları için Anthropic API anahtarları yine de daha
    öngörülebilir kurulumdur. OpenAI Codex OAuth, OpenClaw gibi harici
    araçlar için açıkça desteklenir.

    OpenClaw ayrıca şu diğer barındırılan abonelik benzeri seçenekleri de destekler:
    **Qwen Cloud Coding Plan**, **MiniMax Coding Plan** ve
    **Z.AI / GLM Coding Plan**.

    Belgeler: [Anthropic](/tr/providers/anthropic), [OpenAI](/tr/providers/openai),
    [Qwen Cloud](/tr/providers/qwen),
    [MiniMax](/tr/providers/minimax), [GLM Models](/tr/providers/glm),
    [Yerel modeller](/tr/gateway/local-models), [Modeller](/tr/concepts/models).

  </Accordion>

  <Accordion title="API anahtarı olmadan Claude Max aboneliğini kullanabilir miyim?">
    Evet.

    Anthropic çalışanları bize OpenClaw tarzı Claude CLI kullanımına yeniden izin verildiğini söyledi; bu nedenle
    Anthropic yeni bir politika yayımlamadıkça OpenClaw Claude abonelik auth'unu ve `claude -p`
    kullanımını bu entegrasyon için onaylı kabul eder. En öngörülebilir sunucu tarafı
    kurulumunu istiyorsanız bunun yerine bir Anthropic API anahtarı kullanın.

  </Accordion>

  <Accordion title="Claude abonelik auth'unu (Claude Pro veya Max) destekliyor musunuz?">
    Evet.

    Anthropic çalışanları bize bu kullanıma tekrar izin verildiğini söyledi; bu nedenle OpenClaw
    Anthropic yeni bir politika yayımlamadıkça Claude CLI yeniden kullanımını ve `claude -p`
    kullanımını bu entegrasyon için onaylı kabul eder.

    Anthropic setup-token hâlâ desteklenen bir OpenClaw token yolu olarak mevcuttur, ancak OpenClaw artık mümkün olduğunda Claude CLI yeniden kullanımını ve `claude -p` kullanımını tercih eder.
    Üretim veya çok kullanıcılı iş yükleri için Anthropic API key auth'u hâlâ
    daha güvenli ve öngörülebilir seçimdir. OpenClaw içinde başka abonelik benzeri
    barındırılan seçenekler istiyorsanız bkz. [OpenAI](/tr/providers/openai), [Qwen / Model
    Cloud](/tr/providers/qwen), [MiniMax](/tr/providers/minimax) ve [GLM
    Models](/tr/providers/glm).

  </Accordion>

<a id="why-am-i-seeing-http-429-ratelimiterror-from-anthropic"></a>
<Accordion title="Anthropic'ten neden HTTP 429 rate_limit_error görüyorum?">
Bu, **Anthropic kotanızın/hız sınırınızın** mevcut pencere için tükendiği anlamına gelir. Eğer
**Claude CLI** kullanıyorsanız pencerenin sıfırlanmasını bekleyin veya planınızı yükseltin. Eğer
bir **Anthropic API key** kullanıyorsanız, kullanım/faturalama için Anthropic Console'u
kontrol edin ve gerekirse limitleri artırın.

    Mesaj özellikle şuysa:
    `Extra usage is required for long context requests`, istek
    Anthropic'in 1M bağlam beta özelliğini (`context1m: true`) kullanmaya çalışıyor demektir. Bu yalnızca
    kimlik bilgileriniz uzun bağlam faturalandırmasına uygun olduğunda çalışır (API key faturalaması veya
    Extra Usage etkinleştirilmiş OpenClaw Claude-login yolu).

    İpucu: bir sağlayıcı hız sınırına takıldığında OpenClaw'un yanıt vermeye devam edebilmesi için bir **fallback model** ayarlayın.
    Bkz. [Modeller](/cli/models), [OAuth](/tr/concepts/oauth) ve
    [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/tr/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context).

  </Accordion>

  <Accordion title="AWS Bedrock destekleniyor mu?">
    Evet. OpenClaw'da paketli bir **Amazon Bedrock (Converse)** sağlayıcısı vardır. AWS env işaretleyicileri mevcutsa OpenClaw, akış/metin Bedrock kataloğunu otomatik keşfedip örtük bir `amazon-bedrock` sağlayıcısı olarak birleştirebilir; aksi halde `plugins.entries.amazon-bedrock.config.discovery.enabled` değerini açıkça etkinleştirebilir veya manuel bir sağlayıcı girdisi ekleyebilirsiniz. Bkz. [Amazon Bedrock](/tr/providers/bedrock) ve [Model sağlayıcıları](/tr/providers/models). Yönetilen bir anahtar akışı tercih ediyorsanız, Bedrock önünde bir OpenAI uyumlu proxy de geçerli bir seçenektir.
  </Accordion>

  <Accordion title="Codex auth nasıl çalışıyor?">
    OpenClaw, **OpenAI Code (Codex)** desteğini OAuth (ChatGPT oturum açma) ile sunar. Onboarding OAuth akışını çalıştırabilir ve uygun olduğunda varsayılan modeli `openai-codex/gpt-5.4` olarak ayarlar. Bkz. [Model sağlayıcıları](/tr/concepts/model-providers) ve [Onboarding (CLI)](/tr/start/wizard).
  </Accordion>

  <Accordion title="Neden ChatGPT GPT-5.4, OpenClaw içinde openai/gpt-5.4 kilidini açmıyor?">
    OpenClaw iki yolu ayrı değerlendirir:

    - `openai-codex/gpt-5.4` = ChatGPT/Codex OAuth
    - `openai/gpt-5.4` = doğrudan OpenAI Platform API

    OpenClaw içinde ChatGPT/Codex oturum açması `openai-codex/*` yoluna bağlanır,
    doğrudan `openai/*` yoluna değil. OpenClaw içinde doğrudan API yolunu
    istiyorsanız `OPENAI_API_KEY` (veya eşdeğer OpenAI sağlayıcı yapılandırması) ayarlayın.
    OpenClaw içinde ChatGPT/Codex oturum açması istiyorsanız `openai-codex/*` kullanın.

  </Accordion>

  <Accordion title="Neden Codex OAuth limitleri ChatGPT web'den farklı olabilir?">
    `openai-codex/*`, Codex OAuth yolunu kullanır ve kullanılabilir kota pencereleri
    OpenAI tarafından yönetilir ve plana bağlıdır. Pratikte bu limitler,
    ikisi de aynı hesaba bağlı olsa bile ChatGPT web sitesi/uygulama deneyiminden farklı olabilir.

    OpenClaw, şu anda görünen sağlayıcı kullanım/kota pencerelerini
    `openclaw models status` içinde gösterebilir, ancak ChatGPT-web
    haklarını doğrudan API erişimine dönüştürmez veya normalleştirmez. Doğrudan OpenAI Platform
    faturalama/limit yolunu istiyorsanız API anahtarıyla `openai/*` kullanın.

  </Accordion>

  <Accordion title="OpenAI abonelik auth'unu (Codex OAuth) destekliyor musunuz?">
    Evet. OpenClaw, **OpenAI Code (Codex) abonelik OAuth** desteğini tam olarak sunar.
    OpenAI, OpenClaw gibi harici araçlar/iş akışlarında abonelik OAuth kullanımına
    açıkça izin verir. Onboarding sizin için OAuth akışını çalıştırabilir.

    Bkz. [OAuth](/tr/concepts/oauth), [Model sağlayıcıları](/tr/concepts/model-providers) ve [Onboarding (CLI)](/tr/start/wizard).

  </Accordion>

  <Accordion title="Gemini CLI OAuth'u nasıl kurarım?">
    Gemini CLI, `openclaw.json` içinde client id veya secret değil, bir **plugin auth akışı** kullanır.

    Adımlar:

    1. `gemini` komutunun `PATH` üzerinde olması için Gemini CLI'ı yerel olarak yükleyin
       - Homebrew: `brew install gemini-cli`
       - npm: `npm install -g @google/gemini-cli`
    2. Plugin'i etkinleştirin: `openclaw plugins enable google`
    3. Oturum açın: `openclaw models auth login --provider google-gemini-cli --set-default`
    4. Oturum açtıktan sonraki varsayılan model: `google-gemini-cli/gemini-3-flash-preview`
    5. İstekler başarısız olursa gateway host'ta `GOOGLE_CLOUD_PROJECT` veya `GOOGLE_CLOUD_PROJECT_ID` ayarlayın

    Bu, OAuth token'larını gateway host üzerindeki auth profillerinde depolar. Ayrıntılar: [Model sağlayıcıları](/tr/concepts/model-providers).

  </Accordion>

  <Accordion title="Sıradan sohbetler için yerel model uygun mu?">
    Genellikle hayır. OpenClaw büyük bağlam + güçlü güvenlik gerektirir; küçük kartlar keser ve sızdırır. Mecbursanız, yerelde çalıştırabildiğiniz **en büyük** model derlemesini (LM Studio) kullanın ve bkz. [/gateway/local-models](/tr/gateway/local-models). Daha küçük/nicemlenmiş modeller istem enjeksiyonu riskini artırır - bkz. [Güvenlik](/tr/gateway/security).
  </Accordion>

  <Accordion title="Barındırılan model trafiğini belirli bir bölgede nasıl tutarım?">
    Bölgeye sabitlenmiş uç noktaları seçin. OpenRouter, MiniMax, Kimi ve GLM için ABD'de barındırılan seçenekler sunar; veriyi bölgede tutmak için ABD'de barındırılan varyantı seçin. Seçtiğiniz bölgesel sağlayıcıya saygı gösterirken yedeklerin kullanılabilir kalması için yine de `models.mode: "merge"` kullanarak Anthropic/OpenAI'yi bunların yanında listeleyebilirsiniz.
  </Accordion>

  <Accordion title="Bunu kurmak için bir Mac Mini almam gerekiyor mu?">
    Hayır. OpenClaw macOS veya Linux üzerinde çalışır (Windows, WSL2 üzerinden). Mac mini isteğe bağlıdır -
    bazı kişiler onu sürekli açık bir host olarak alır, ancak küçük bir VPS, ev sunucusu veya Raspberry Pi sınıfı bir kutu da çalışır.

    Yalnızca **macOS'e özel araçlar** için bir Mac gerekir. iMessage için [BlueBubbles](/tr/channels/bluebubbles) kullanın (önerilir) -
    BlueBubbles sunucusu herhangi bir Mac'te çalışır ve Gateway Linux'ta veya başka bir yerde çalışabilir. Başka macOS'e özel araçlar istiyorsanız Gateway'i bir Mac'te çalıştırın veya bir macOS node eşleştirin.

    Belgeler: [BlueBubbles](/tr/channels/bluebubbles), [Nodes](/tr/nodes), [Mac remote mode](/tr/platforms/mac/remote).

  </Accordion>

  <Accordion title="iMessage desteği için Mac mini gerekiyor mu?">
    Messages'da oturum açmış **bir macOS cihazına** ihtiyacınız var. Bunun **Mac mini** olması gerekmez -
    herhangi bir Mac olur. iMessage için **[BlueBubbles](/tr/channels/bluebubbles)** kullanın (önerilir) - BlueBubbles sunucusu macOS'ta çalışırken Gateway Linux'ta veya başka bir yerde olabilir.

    Yaygın kurulumlar:

    - Gateway'i Linux/VPS üzerinde çalıştırın, BlueBubbles sunucusunu ise Messages'da oturum açmış herhangi bir Mac'te çalıştırın.
    - En basit tek makine kurulumu için her şeyi Mac üzerinde çalıştırın.

    Belgeler: [BlueBubbles](/tr/channels/bluebubbles), [Nodes](/tr/nodes),
    [Mac remote mode](/tr/platforms/mac/remote).

  </Accordion>

  <Accordion title="OpenClaw çalıştırmak için bir Mac mini alırsam MacBook Pro'ma bağlayabilir miyim?">
    Evet. **Mac mini Gateway'i çalıştırabilir**, MacBook Pro'nuz ise bir
    **node** (eşlik eden cihaz) olarak bağlanabilir. Nodes Gateway çalıştırmaz -
    bu cihazda ekran/kamera/canvas ve `system.run` gibi ek yetenekler sağlar.

    Yaygın desen:

    - Her zaman açık Mac mini üzerinde Gateway.
    - MacBook Pro macOS uygulamasını veya bir node host çalıştırır ve Gateway ile eşleşir.
    - Görmek için `openclaw nodes status` / `openclaw nodes list` kullanın.

    Belgeler: [Nodes](/tr/nodes), [Nodes CLI](/cli/nodes).

  </Accordion>

  <Accordion title="Bun kullanabilir miyim?">
    Bun **önerilmez**. Özellikle WhatsApp ve Telegram ile çalışma zamanı hataları görüyoruz.
    Kararlı gateway'ler için **Node** kullanın.

    Yine de Bun ile deneme yapmak istiyorsanız bunu
    WhatsApp/Telegram olmadan üretim dışı bir gateway'de yapın.

  </Accordion>

  <Accordion title="Telegram: allowFrom içine ne girer?">
    `channels.telegram.allowFrom`, **insan gönderenin Telegram kullanıcı kimliğidir** (sayısal). Bot kullanıcı adı değildir.

    Onboarding `@username` girdisini kabul eder ve bunu sayısal kimliğe çözer, ancak OpenClaw yetkilendirmesi yalnızca sayısal kimlikleri kullanır.

    Daha güvenli (üçüncü taraf bot olmadan):

    - Botunuza DM atın, sonra `openclaw logs --follow` çalıştırın ve `from.id` değerini okuyun.

    Resmi Bot API:

    - Botunuza DM atın, sonra `https://api.telegram.org/bot<bot_token>/getUpdates` çağrısını yapın ve `message.from.id` değerini okuyun.

    Üçüncü taraf (daha az gizli):

    - `@userinfobot` veya `@getidsbot` botlarına DM atın.

    Bkz. [/channels/telegram](/tr/channels/telegram#access-control-and-activation).

  </Accordion>

  <Accordion title="Birden fazla kişi farklı OpenClaw örnekleriyle tek bir WhatsApp numarasını kullanabilir mi?">
    Evet, **çoklu ajan yönlendirme** ile. Her gönderenin WhatsApp **DM**'ini (peer `kind: "direct"`, gönderici E.164 örn. `+15551234567`) farklı bir `agentId`'ye bağlayın; böylece her kişinin kendi çalışma alanı ve oturum deposu olur. Yanıtlar yine **aynı WhatsApp hesabından** gelir ve DM erişim kontrolü (`channels.whatsapp.dmPolicy` / `channels.whatsapp.allowFrom`) her WhatsApp hesabı için küreseldir. Bkz. [Çoklu Ajan Yönlendirme](/tr/concepts/multi-agent) ve [WhatsApp](/tr/channels/whatsapp).
  </Accordion>

  <Accordion title='Bir "hızlı sohbet" ajanı ve bir "kodlama için Opus" ajanı çalıştırabilir miyim?'>
    Evet. Çoklu ajan yönlendirmeyi kullanın: her ajana kendi varsayılan modelini verin, ardından gelen rotaları (sağlayıcı hesabı veya belirli peers) her ajana bağlayın. Örnek yapılandırma [Çoklu Ajan Yönlendirme](/tr/concepts/multi-agent) içinde bulunur. Ayrıca bkz. [Modeller](/tr/concepts/models) ve [Yapılandırma](/tr/gateway/configuration).
  </Accordion>

  <Accordion title="Homebrew Linux'ta çalışır mı?">
    Evet. Homebrew Linux'u destekler (Linuxbrew). Hızlı kurulum:

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew install <formula>
    ```

    OpenClaw'u systemd üzerinden çalıştırıyorsanız, hizmet PATH'inin `/home/linuxbrew/.linuxbrew/bin` (veya brew önekiniz) dizinini içerdiğinden emin olun; böylece `brew` ile yüklenen araçlar oturum açılmamış shell'lerde çözülebilir.
    Son derlemeler ayrıca Linux systemd hizmetlerinde yaygın kullanıcı bin dizinlerini de başa ekler (örneğin `~/.local/bin`, `~/.npm-global/bin`, `~/.local/share/pnpm`, `~/.bun/bin`) ve ayarlıysa `PNPM_HOME`, `NPM_CONFIG_PREFIX`, `BUN_INSTALL`, `VOLTA_HOME`, `ASDF_DATA_DIR`, `NVM_DIR` ve `FNM_DIR` değerlerine saygı duyar.

  </Accordion>

  <Accordion title="Hacklenebilir git kurulumu ile npm install arasındaki fark">
    - **Hacklenebilir (git) kurulum:** tam kaynak checkout'u, düzenlenebilir, katkıda bulunanlar için en iyisi.
      Derlemeleri yerelde çalıştırırsınız ve kod/belgeleri yamalayabilirsiniz.
    - **npm install:** global CLI kurulumu, repo yok, “yalnızca çalıştırmak” için en iyisi.
      Güncellemeler npm dist-tag'lerinden gelir.

    Belgeler: [Başlarken](/tr/start/getting-started), [Güncelleme](/tr/install/updating).

  </Accordion>

  <Accordion title="Daha sonra npm ve git kurulumları arasında geçiş yapabilir miyim?">
    Evet. Diğer türü yükleyin, ardından gateway hizmetinin yeni entrypoint'i göstermesi için Doctor çalıştırın.
    Bu **verilerinizi silmez** - yalnızca OpenClaw kod kurulumunu değiştirir. Durumunuz
    (`~/.openclaw`) ve çalışma alanınız (`~/.openclaw/workspace`) dokunulmadan kalır.

    npm'den git'e:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    openclaw doctor
    openclaw gateway restart
    ```

    git'ten npm'e:

    ```bash
    npm install -g openclaw@latest
    openclaw doctor
    openclaw gateway restart
    ```

    Doctor, gateway hizmeti entrypoint uyumsuzluğunu algılar ve hizmet yapılandırmasını mevcut kuruluma uyacak şekilde yeniden yazmayı önerir (otomasyonda `--repair` kullanın).

    Yedekleme ipuçları: bkz. [Yedekleme stratejisi](#diskte-neler-nerededir).

  </Accordion>

  <Accordion title="Gateway'i dizüstü bilgisayarımda mı yoksa bir VPS'te mi çalıştırmalıyım?">
    Kısa yanıt: **24/7 güvenilirlik istiyorsanız bir VPS kullanın**. En düşük sürtünmeyi istiyorsanız ve uyku/yeniden başlatmalar sizin için sorun değilse yerelde çalıştırın.

    **Dizüstü bilgisayar (yerel Gateway)**

    - **Artılar:** sunucu maliyeti yok, yerel dosyalara doğrudan erişim, canlı tarayıcı penceresi.
    - **Eksiler:** uyku/ağ kopmaları = bağlantı kopmaları, işletim sistemi güncellemeleri/yeniden başlatmaları kesinti yaratır, uyanık kalması gerekir.

    **VPS / bulut**

    - **Artılar:** sürekli açık, kararlı ağ, dizüstü uyku sorunları yok, çalışır durumda tutması daha kolay.
    - **Eksiler:** genellikle headless çalışır (ekran görüntüsü kullanın), yalnızca uzak dosya erişimi vardır, güncellemeler için SSH gerekir.

    **OpenClaw'a özgü not:** WhatsApp/Telegram/Slack/Mattermost/Discord bir VPS'te gayet iyi çalışır. Asıl ödünleşim yalnızca **headless tarayıcı** ile görünür pencere arasındadır. Bkz. [Tarayıcı](/tr/tools/browser).

    **Önerilen varsayılan:** Daha önce gateway bağlantı kopmaları yaşadıysanız VPS. Mac'i aktif kullanırken ve yerel dosya erişimi veya görünür tarayıcıyla UI otomasyonu istediğinizde yerel kurulum harikadır.

  </Accordion>

  <Accordion title="OpenClaw'u özel bir makinede çalıştırmak ne kadar önemli?">
    Zorunlu değil, ancak **güvenilirlik ve yalıtım** için önerilir.

    - **Özel host (VPS/Mac mini/Pi):** sürekli açık, daha az uyku/yeniden başlatma kesintisi, daha temiz izinler, çalışır durumda tutması daha kolay.
    - **Paylaşılan dizüstü/masaüstü:** test ve aktif kullanım için tamamen uygundur, ancak makine uyuduğunda veya güncellendiğinde duraklamalar bekleyin.

    Her iki dünyanın en iyisini istiyorsanız Gateway'i özel bir host üzerinde tutun ve yerel ekran/kamera/exec araçları için dizüstünüzü bir **node** olarak eşleştirin. Bkz. [Nodes](/tr/nodes).
    Güvenlik rehberi için [Güvenlik](/tr/gateway/security) bölümünü okuyun.

  </Accordion>

  <Accordion title="Asgari VPS gereksinimleri ve önerilen işletim sistemi nedir?">
    OpenClaw hafiftir. Temel bir Gateway + tek bir sohbet kanalı için:

    - **Mutlak minimum:** 1 vCPU, 1GB RAM, ~500MB disk.
    - **Önerilen:** boşluk için 1-2 vCPU, 2GB RAM veya daha fazlası (günlükler, medya, birden fazla kanal). Node araçları ve tarayıcı otomasyonu kaynak tüketebilir.

    İşletim sistemi: **Ubuntu LTS** (veya herhangi bir modern Debian/Ubuntu) kullanın. Linux kurulum yolu en çok orada test edilir.

    Belgeler: [Linux](/tr/platforms/linux), [VPS hosting](/tr/vps).

  </Accordion>

  <Accordion title="OpenClaw'u bir VM içinde çalıştırabilir miyim ve gereksinimler nelerdir?">
    Evet. Bir VM'yi VPS gibi değerlendirin: sürekli açık olmalı, erişilebilir olmalı ve
    Gateway ile etkinleştirdiğiniz kanallar için yeterli RAM'e sahip olmalıdır.

    Temel rehber:

    - **Mutlak minimum:** 1 vCPU, 1GB RAM.
    - **Önerilen:** birden fazla kanal, tarayıcı otomasyonu veya medya araçları çalıştırıyorsanız 2GB RAM veya daha fazlası.
    - **İşletim sistemi:** Ubuntu LTS veya başka bir modern Debian/Ubuntu.

    Windows kullanıyorsanız, **WSL2 en kolay VM tarzı kurulumdur** ve araç uyumluluğu en iyidir.
    Bkz. [Windows](/tr/platforms/windows), [VPS hosting](/tr/vps).
    macOS'u bir VM içinde çalıştırıyorsanız bkz. [macOS VM](/tr/install/macos-vm).

  </Accordion>
</AccordionGroup>

## OpenClaw nedir?

<AccordionGroup>
  <Accordion title="Tek paragrafta OpenClaw nedir?">
    OpenClaw, kendi cihazlarınızda çalıştırdığınız kişisel bir AI asistandır. Zaten kullandığınız mesajlaşma yüzeylerinde (WhatsApp, Telegram, Slack, Mattermost, Discord, Google Chat, Signal, iMessage, WebChat ve QQ Bot gibi paketli kanal plugin'leri) yanıt verir ve desteklenen platformlarda ses + canlı Canvas da yapabilir. **Gateway** her zaman açık kontrol düzlemidir; ürün asistanın kendisidir.
  </Accordion>

  <Accordion title="Değer önerisi">
    OpenClaw “sadece bir Claude sarmalayıcı” değildir. Bu, size
    **kendi donanımınızda** yetenekli bir asistan çalıştırma olanağı veren, zaten kullandığınız sohbet uygulamaları üzerinden erişilebilen,
    durum bilgili oturumlar, hafıza ve araçlarla çalışan, iş akışlarınızın kontrolünü
    barındırılan bir SaaS'a teslim etmeyen **yerel öncelikli bir kontrol düzlemidir**.

    Öne çıkanlar:

    - **Cihazlarınız, verileriniz:** Gateway'i istediğiniz yerde (Mac, Linux, VPS) çalıştırın ve
      çalışma alanını + oturum geçmişini yerelde tutun.
    - **Gerçek kanallar, web sandbox'ı değil:** WhatsApp/Telegram/Slack/Discord/Signal/iMessage/vb,
      ayrıca desteklenen platformlarda mobil ses ve Canvas.
    - **Model bağımsız:** Anthropic, OpenAI, MiniMax, OpenRouter vb. kullanın; ajan başına yönlendirme
      ve devretme ile.
    - **Yalnızca yerel seçenek:** isterseniz **tüm veriler cihazınızda kalabilsin** diye yerel modeller çalıştırın.
    - **Çoklu ajan yönlendirme:** kanal, hesap veya görev başına ayrı ajanlar; her birinin kendi
      çalışma alanı ve varsayılanları vardır.
    - **Açık kaynak ve hacklenebilir:** satıcıya kilitlenmeden inceleyin, genişletin ve self-host edin.

    Belgeler: [Gateway](/tr/gateway), [Kanallar](/tr/channels), [Çoklu ajan](/tr/concepts/multi-agent),
    [Hafıza](/tr/concepts/memory).

  </Accordion>

  <Accordion title="Az önce kurdum - önce ne yapmalıyım?">
    Başlangıç için iyi projeler:

    - Bir web sitesi oluşturun (WordPress, Shopify veya basit bir statik site).
    - Bir mobil uygulama prototipi hazırlayın (taslak, ekranlar, API planı).
    - Dosya ve klasörleri düzenleyin (temizlik, adlandırma, etiketleme).
    - Gmail bağlayın ve özetleri veya takipleri otomatikleştirin.

    Büyük görevleri ele alabilir, ancak bunları aşamalara böldüğünüzde ve
    paralel çalışma için alt ajanlar kullandığınızda en iyi sonucu verir.

  </Accordion>

  <Accordion title="OpenClaw için günlük hayattaki en iyi beş kullanım senaryosu nedir?">
    Günlük kazanımlar genelde şuna benzer:

    - **Kişisel özetler:** gelen kutusu, takvim ve ilgilendiğiniz haberlerin özetleri.
    - **Araştırma ve taslak hazırlama:** e-postalar veya belgeler için hızlı araştırma, özetler ve ilk taslaklar.
    - **Hatırlatmalar ve takipler:** cron veya heartbeat ile çalışan dürtmeler ve kontrol listeleri.
    - **Tarayıcı otomasyonu:** form doldurma, veri toplama ve tekrarlayan web görevleri.
    - **Cihazlar arası koordinasyon:** telefonunuzdan bir görev gönderin, Gateway bunu bir sunucuda çalıştırsın ve sonucu size sohbette geri versin.

  </Accordion>

  <Accordion title="OpenClaw bir SaaS için lead gen, outreach, reklam ve bloglar konusunda yardımcı olabilir mi?">
    **Araştırma, nitelendirme ve taslak hazırlama** için evet. Siteleri tarayabilir, kısa listeler oluşturabilir,
    adayları özetleyebilir ve outreach veya reklam metni taslakları yazabilir.

    **Outreach veya reklam çalıştırmaları** için bir insanı süreç içinde tutun. Spam'den kaçının, yerel yasalara ve
    platform politikalarına uyun ve gönderilmeden önce her şeyi gözden geçirin. En güvenli desen,
    OpenClaw'un taslak hazırlaması ve sizin onay vermenizdir.

    Belgeler: [Güvenlik](/tr/gateway/security).

  </Accordion>

  <Accordion title="Web geliştirme için Claude Code'a göre avantajları nelerdir?">
    OpenClaw bir **kişisel asistan** ve koordinasyon katmanıdır, IDE yerine geçmez. Depo içinde en hızlı doğrudan kodlama döngüsü için
    Claude Code veya Codex kullanın. Kalıcı hafıza, cihazlar arası erişim ve araç orkestrasyonu istediğinizde
    OpenClaw kullanın.

    Avantajlar:

    - Oturumlar arasında **kalıcı hafıza + çalışma alanı**
    - **Çok platformlu erişim** (WhatsApp, Telegram, TUI, WebChat)
    - **Araç orkestrasyonu** (tarayıcı, dosyalar, zamanlama, hooks)
    - **Her zaman açık Gateway** (bir VPS'te çalıştırın, her yerden etkileşin)
    - Yerel tarayıcı/ekran/kamera/exec için **Nodes**

    Vitrin: [https://openclaw.ai/showcase](https://openclaw.ai/showcase)

  </Accordion>
</AccordionGroup>

## Skills ve otomasyon

<AccordionGroup>
  <Accordion title="Depoyu kirletmeden Skills'i nasıl özelleştiririm?">
    Depodaki kopyayı düzenlemek yerine yönetilen override'lar kullanın. Değişikliklerinizi `~/.openclaw/skills/<name>/SKILL.md` içine koyun (veya `~/.openclaw/openclaw.json` içinde `skills.load.extraDirs` üzerinden bir klasör ekleyin). Öncelik sırası `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → paketli → `skills.load.extraDirs` şeklindedir; yani yönetilen override'lar git'e dokunmadan yine paketli Skills'in önüne geçer. Skill'in küresel olarak yüklü olmasını ama yalnızca bazı ajanlara görünmesini istiyorsanız, paylaşılan kopyayı `~/.openclaw/skills` içinde tutun ve görünürlüğü `agents.defaults.skills` ve `agents.list[].skills` ile kontrol edin. Yalnızca upstream'e değer değişiklikler depoda yaşamalı ve PR olarak gitmelidir.
  </Accordion>

  <Accordion title="Skills'i özel bir klasörden yükleyebilir miyim?">
    Evet. `~/.openclaw/openclaw.json` içinde `skills.load.extraDirs` üzerinden ek dizinler ekleyin (en düşük öncelik). Varsayılan öncelik sırası `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → paketli → `skills.load.extraDirs` şeklindedir. `clawhub` varsayılan olarak `./skills` içine kurar; OpenClaw bunu bir sonraki oturumda `<workspace>/skills` olarak değerlendirir. Skill yalnızca belirli ajanlara görünmeliysa, bunu `agents.defaults.skills` veya `agents.list[].skills` ile eşleştirin.
  </Accordion>

  <Accordion title="Farklı görevler için farklı modelleri nasıl kullanabilirim?">
    Bugün desteklenen desenler şunlardır:

    - **Cron işleri**: yalıtılmış işler iş başına `model` override ayarlayabilir.
    - **Alt ajanlar**: görevleri farklı varsayılan modellere sahip ayrı ajanlara yönlendirin.
    - **İsteğe bağlı geçiş**: mevcut oturum modelini istediğiniz zaman değiştirmek için `/model` kullanın.

    Bkz. [Cron işleri](/tr/automation/cron-jobs), [Çoklu Ajan Yönlendirme](/tr/concepts/multi-agent) ve [Slash komutları](/tr/tools/slash-commands).

  </Accordion>

  <Accordion title="Bot ağır iş yaparken donuyor. Bunu nasıl başka yere taşıyabilirim?">
    Uzun veya paralel görevler için **alt ajanlar** kullanın. Alt ajanlar kendi oturumlarında çalışır,
    bir özet döndürür ve ana sohbetinizin yanıt verebilir kalmasını sağlar.

    Botunuza “bu görev için bir alt ajan başlat” deyin veya `/subagents` kullanın.
    Gateway'in şu anda ne yaptığını (ve meşgul olup olmadığını) görmek için sohbette `/status` kullanın.

    Token ipucu: uzun görevler ve alt ajanlar da token tüketir. Maliyet endişe veriyorsa,
    `agents.defaults.subagents.model` üzerinden alt ajanlar için daha ucuz bir model ayarlayın.

    Belgeler: [Alt ajanlar](/tr/tools/subagents), [Arka Plan Görevleri](/tr/automation/tasks).

  </Accordion>

  <Accordion title="Discord'da iş parçacığına bağlı alt ajan oturumları nasıl çalışır?">
    İş parçacığı bağlamalarını kullanın. Bir Discord iş parçacığını bir alt ajana veya oturum hedefine bağlayabilirsiniz; böylece o iş parçacığındaki takip mesajları bağlı oturumda kalır.

    Temel akış:

    - `sessions_spawn` ile `thread: true` kullanarak başlatın (ve kalıcı takip için isteğe bağlı olarak `mode: "session"`).
    - Veya `/focus <target>` ile elle bağlayın.
    - Bağlama durumunu incelemek için `/agents` kullanın.
    - Otomatik odak kaldırmayı kontrol etmek için `/session idle <duration|off>` ve `/session max-age <duration|off>` kullanın.
    - İş parçacığını ayırmak için `/unfocus` kullanın.

    Gerekli yapılandırma:

    - Küresel varsayılanlar: `session.threadBindings.enabled`, `session.threadBindings.idleHours`, `session.threadBindings.maxAgeHours`.
    - Discord override'ları: `channels.discord.threadBindings.enabled`, `channels.discord.threadBindings.idleHours`, `channels.discord.threadBindings.maxAgeHours`.
    - Başlatmada otomatik bağlama: `channels.discord.threadBindings.spawnSubagentSessions: true` ayarlayın.

    Belgeler: [Alt ajanlar](/tr/tools/subagents), [Discord](/tr/channels/discord), [Yapılandırma Başvurusu](/tr/gateway/configuration-reference), [Slash komutları](/tr/tools/slash-commands).

  </Accordion>

  <Accordion title="Bir alt ajan bitti, ama tamamlama güncellemesi yanlış yere gitti veya hiç gönderilmedi. Neyi kontrol etmeliyim?">
    Önce çözümlenen istekçi rotasını kontrol edin:

    - Tamamlama kipindeki alt ajan teslimi, mevcutsa bağlı herhangi bir iş parçacığını veya konuşma rotasını tercih eder.
    - Tamamlama kökeni yalnızca bir kanal taşıyorsa, OpenClaw doğrudan teslimin yine de başarılı olabilmesi için istekçi oturumunun depolanan rotasına (`lastChannel` / `lastTo` / `lastAccountId`) geri döner.
    - Ne bağlı bir rota ne de kullanılabilir bir depolanan rota yoksa, doğrudan teslim başarısız olabilir ve sonuç sohbete hemen gönderilmek yerine sıraya alınmış oturum teslimine geri düşer.
    - Geçersiz veya bayat hedefler yine kuyruk geri dönüşünü veya nihai teslim başarısızlığını zorlayabilir.
    - Çocuğun son görünür asistan yanıtı tam olarak sessiz token `NO_REPLY` / `no_reply` veya tam olarak `ANNOUNCE_SKIP` ise, OpenClaw bayat eski ilerlemeyi göndermek yerine duyuruyu bilinçli olarak bastırır.
    - Çocuk yalnızca araç çağrılarından sonra zaman aşımına uğradıysa, duyuru ham araç çıktısını tekrar oynatmak yerine bunu kısa bir kısmi ilerleme özeti olarak çökertilebilir.

    Hata ayıklama:

    ```bash
    openclaw tasks show <runId-or-sessionKey>
    ```

    Belgeler: [Alt ajanlar](/tr/tools/subagents), [Arka Plan Görevleri](/tr/automation/tasks), [Oturum Araçları](/tr/concepts/session-tool).

  </Accordion>

  <Accordion title="Cron veya hatırlatmalar çalışmıyor. Neyi kontrol etmeliyim?">
    Cron, Gateway işlemi içinde çalışır. Gateway sürekli çalışmıyorsa,
    zamanlanmış işler çalışmaz.

    Kontrol listesi:

    - cron etkin mi (`cron.enabled`) ve `OPENCLAW_SKIP_CRON` ayarlanmamış mı kontrol edin.
    - Gateway'in 24/7 çalıştığını kontrol edin (uyku/yeniden başlatma yok).
    - İş için saat dilimi ayarlarını doğrulayın (`--tz` ve host saat dilimi).

    Hata ayıklama:

    ```bash
    openclaw cron run <jobId>
    openclaw cron runs --id <jobId> --limit 50
    ```

    Belgeler: [Cron işleri](/tr/automation/cron-jobs), [Otomasyon ve Görevler](/tr/automation).

  </Accordion>

  <Accordion title="Cron tetiklendi, ama kanala hiçbir şey gönderilmedi. Neden?">
    Önce teslim kipini kontrol edin:

    - `--no-deliver` / `delivery.mode: "none"` hiçbir dış mesaj beklenmediği anlamına gelir.
    - Eksik veya geçersiz duyuru hedefi (`channel` / `to`) çalıştırıcının giden teslimi atladığı anlamına gelir.
    - Kanal auth başarısızlıkları (`unauthorized`, `Forbidden`), çalıştırıcının teslim etmeye çalıştığı ama kimlik bilgilerinin bunu engellediği anlamına gelir.
    - Sessiz bir yalıtılmış sonuç (`NO_REPLY` / `no_reply` yalnızca) kasıtlı olarak teslim edilemez kabul edilir, bu yüzden çalıştırıcı sıraya alınmış geri dönüş teslimini de bastırır.

    Yalıtılmış cron işleri için nihai teslimden çalıştırıcı sorumludur. Ajanın,
    çalıştırıcının gönderebilmesi için düz metin bir özet döndürmesi beklenir. `--no-deliver`
    bu sonucu içeride tutar; bunun yerine ajanın message aracıyla doğrudan
    göndermesine izin vermez.

    Hata ayıklama:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    Belgeler: [Cron işleri](/tr/automation/cron-jobs), [Arka Plan Görevleri](/tr/automation/tasks).

  </Accordion>

  <Accordion title="Neden yalıtılmış bir cron çalıştırması modeli değiştirdi veya bir kez yeniden denedi?">
    Bu genelde çift zamanlama değil, canlı model-geçiş yoludur.

    Yalıtılmış cron, etkin çalıştırma `LiveSessionModelSwitchError` fırlattığında
    çalışma zamanı model devrini kalıcı hâle getirip yeniden deneyebilir. Yeniden deneme,
    değiştirilen sağlayıcı/modeli korur ve geçiş yeni bir auth profili override'ı taşıyorsa,
    cron yeniden denemeden önce bunu da kalıcı hâle getirir.

    İlgili seçim kuralları:

    - Uygunsa Gmail hook model override'ı önce kazanır.
    - Sonra iş başına `model`.
    - Sonra depolanan herhangi bir cron-oturum model override'ı.
    - Sonra normal ajan/varsayılan model seçimi.

    Yeniden deneme döngüsü sınırlıdır. İlk deneme artı 2 geçiş yeniden denemesinden sonra
    cron sonsuza dek döngüye girmek yerine iptal eder.

    Hata ayıklama:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    Belgeler: [Cron işleri](/tr/automation/cron-jobs), [cron CLI](/cli/cron).

  </Accordion>

  <Accordion title="Skills'i Linux'ta nasıl kurarım?">
    Yerel `openclaw skills` komutlarını kullanın veya Skills'i çalışma alanınıza bırakın. macOS Skills UI Linux'ta mevcut değildir.
    Skills'e [https://clawhub.ai](https://clawhub.ai) adresinden göz atın.

    ```bash
    openclaw skills search "calendar"
    openclaw skills search --limit 20
    openclaw skills install <skill-slug>
    openclaw skills install <skill-slug> --version <version>
    openclaw skills install <skill-slug> --force
    openclaw skills update --all
    openclaw skills list --eligible
    openclaw skills check
    ```

    Yerel `openclaw skills install` etkin çalışma alanının `skills/`
    dizinine yazar. Kendi Skills'inizi yayımlamak veya
    eşzamanlamak istemiyorsanız ayrı `clawhub` CLI'ını yalnızca o durumda kurun. Ajanlar arasında paylaşılan kurulumlar için
    skill'i `~/.openclaw/skills` altına koyun ve hangi ajanların görebileceğini daraltmak için
    `agents.defaults.skills` veya `agents.list[].skills` kullanın.

  </Accordion>

  <Accordion title="OpenClaw görevleri takvime bağlı veya sürekli arka planda çalıştırabilir mi?">
    Evet. Gateway zamanlayıcısını kullanın:

    - Zamanlanmış veya yinelenen görevler için **Cron işleri** (yeniden başlatmalardan sonra da kalır).
    - “Ana oturum” periyodik kontrolleri için **Heartbeat**.
    - Özetler yayımlayan veya sohbetlere teslim eden otonom ajanlar için **Yalıtılmış işler**.

    Belgeler: [Cron işleri](/tr/automation/cron-jobs), [Otomasyon ve Görevler](/tr/automation),
    [Heartbeat](/tr/gateway/heartbeat).

  </Accordion>

  <Accordion title="Apple macOS-only Skills'i Linux'tan çalıştırabilir miyim?">
    Doğrudan hayır. macOS Skills, `metadata.openclaw.os` ile gerekli binary'ler tarafından kapatılır ve Skills yalnızca **Gateway host** üzerinde uygun olduklarında sistem isteminde görünür. Linux'ta `darwin`-yalnızca Skills (`apple-notes`, `apple-reminders`, `things-mac` gibi), bu kapatmayı override etmediğiniz sürece yüklenmez.

    Desteklenen üç deseniniz vardır:

    **Seçenek A - Gateway'i bir Mac üzerinde çalıştırın (en basit).**
    Gateway'i macOS binary'lerinin bulunduğu yerde çalıştırın, sonra Linux'tan [uzak modda](#gateway-portlari-zaten-calisiyor-ve-uzak-mod) veya Tailscale üzerinden bağlanın. Gateway host macOS olduğu için Skills normal yüklenir.

    **Seçenek B - bir macOS node kullanın (SSH yok).**
    Gateway'i Linux'ta çalıştırın, bir macOS node'u (menü çubuğu uygulaması) eşleştirin ve Mac'te **Node Run Commands** ayarını "Always Ask" veya "Always Allow" yapın. Gerekli binary'ler node üzerinde mevcut olduğunda OpenClaw macOS-only Skills'i uygun kabul edebilir. Ajan bu Skills'i `nodes` aracı üzerinden çalıştırır. "Always Ask" seçerseniz istemde "Always Allow" onayı o komutu allowlist'e ekler.

    **Seçenek C - macOS binary'lerini SSH üzerinden proxy'leyin (ileri seviye).**
    Gateway'i Linux'ta tutun, ancak gerekli CLI binary'lerinin bir Mac üzerinde çalışan SSH wrapper'lara çözülmesini sağlayın. Sonra skill'i Linux'a izin verecek şekilde override edin ki uygun kalabilsin.

    1. Binary için bir SSH wrapper oluşturun (örnek: Apple Notes için `memo`):

       ```bash
       #!/usr/bin/env bash
       set -euo pipefail
       exec ssh -T user@mac-host /opt/homebrew/bin/memo "$@"
       ```

    2. Wrapper'ı Linux host'ta `PATH` içine koyun (örneğin `~/bin/memo`).
    3. Skill metadata'sını (çalışma alanı veya `~/.openclaw/skills`) Linux'a izin verecek şekilde override edin:

       ```markdown
       ---
       name: apple-notes
       description: Manage Apple Notes via the memo CLI on macOS.
       metadata: { "openclaw": { "os": ["darwin", "linux"], "requires": { "bins": ["memo"] } } }
       ---
       ```

    4. Skills anlık görüntüsünün yenilenmesi için yeni bir oturum başlatın.

  </Accordion>

  <Accordion title="Notion veya HeyGen entegrasyonunuz var mı?">
    Bugün yerleşik değil.

    Seçenekler:

    - **Özel skill / plugin:** güvenilir API erişimi için en iyisi (Notion/HeyGen'in ikisinin de API'si vardır).
    - **Tarayıcı otomasyonu:** kod olmadan çalışır ama daha yavaş ve daha kırılgandır.

    Bağlamı müşteri başına tutmak istiyorsanız (ajans iş akışları), basit bir desen:

    - Müşteri başına bir Notion sayfası (bağlam + tercihler + etkin iş).
    - Ajandan oturumun başında bu sayfayı getirmesini isteyin.

    Yerel bir entegrasyon istiyorsanız bir özellik isteği açın veya bu API'leri
    hedefleyen bir skill oluşturun.

    Skills yükleme:

    ```bash
    openclaw skills install <skill-slug>
    openclaw skills update --all
    ```

    Yerel kurulumlar etkin çalışma alanının `skills/` dizinine gider. Ajanlar arası paylaşılan Skills için bunları `~/.openclaw/skills/<name>/SKILL.md` içine koyun. Yalnızca bazı ajanlar paylaşılan kurulumu görmeliysa `agents.defaults.skills` veya `agents.list[].skills` yapılandırın. Bazı Skills, Homebrew ile kurulu binary'ler bekler; Linux'ta bu Linuxbrew demektir (yukarıdaki Homebrew Linux SSS girdisine bakın). Bkz. [Skills](/tr/tools/skills), [Skills config](/tr/tools/skills-config) ve [ClawHub](/tr/tools/clawhub).

  </Accordion>

  <Accordion title="Mevcut oturum açılmış Chrome'umu OpenClaw ile nasıl kullanırım?">
    Chrome DevTools MCP üzerinden bağlanan yerleşik `user` tarayıcı profilini kullanın:

    ```bash
    openclaw browser --browser-profile user tabs
    openclaw browser --browser-profile user snapshot
    ```

    Özel bir ad istiyorsanız açık bir MCP profili oluşturun:

    ```bash
    openclaw browser create-profile --name chrome-live --driver existing-session
    openclaw browser --browser-profile chrome-live tabs
    ```

    Bu yol host-yereldir. Gateway başka yerde çalışıyorsa, ya tarayıcı makinesinde bir node host çalıştırın ya da bunun yerine uzak CDP kullanın.

    `existing-session` / `user` üzerindeki mevcut sınırlar:

    - eylemler CSS-selector güdümlü değil, ref güdümlüdür
    - yüklemeler `ref` / `inputRef` gerektirir ve şu anda aynı anda tek dosyayı destekler
    - `responsebody`, PDF dışa aktarma, indirme yakalama ve toplu eylemler için hâlâ yönetilen tarayıcı veya ham CDP profili gerekir

  </Accordion>
</AccordionGroup>

## Sandbox ve hafıza

<AccordionGroup>
  <Accordion title="Özel bir sandbox belgesi var mı?">
    Evet. Bkz. [Sandboxing](/tr/gateway/sandboxing). Docker'a özgü kurulum (tam gateway'i Docker içinde çalıştırma veya sandbox imajları) için bkz. [Docker](/tr/install/docker).
  </Accordion>

  <Accordion title="Docker sınırlı hissettiriyor - tam özellikleri nasıl etkinleştiririm?">
    Varsayılan imaj güvenlik önceliklidir ve `node` kullanıcısı olarak çalışır; bu yüzden
    sistem paketleri, Homebrew veya paketli tarayıcılar içermez. Daha tam bir kurulum için:

    - Önbelleklerin kalıcı olması için `/home/node` dizinini `OPENCLAW_HOME_VOLUME` ile kalıcı yapın.
    - Sistem bağımlılıklarını `OPENCLAW_DOCKER_APT_PACKAGES` ile imaj içine derleyin.
    - Paketli CLI ile Playwright tarayıcılarını kurun:
      `node /app/node_modules/playwright-core/cli.js install chromium`
    - `PLAYWRIGHT_BROWSERS_PATH` ayarlayın ve yolun kalıcı olduğundan emin olun.

    Belgeler: [Docker](/tr/install/docker), [Tarayıcı](/tr/tools/browser).

  </Accordion>

  <Accordion title="DM'leri kişisel tutup grupları herkese açık/sandbox'lı tek bir ajanla yönetebilir miyim?">
    Evet - özel trafiğiniz **DM**, herkese açık trafiğiniz **gruplar** ise.

    `agents.defaults.sandbox.mode: "non-main"` kullanın; böylece grup/kanal oturumları (anahtar olmayan anahtarlar) Docker içinde çalışırken, ana DM oturumu host üzerinde kalır. Sonra `tools.sandbox.tools` aracılığıyla sandbox'lı oturumlarda hangi araçların kullanılabileceğini sınırlayın.

    Kurulum kılavuzu + örnek yapılandırma: [Gruplar: kişisel DM'ler + herkese açık gruplar](/tr/channels/groups#pattern-personal-dms-public-groups-single-agent)

    Temel yapılandırma başvurusu: [Gateway yapılandırması](/tr/gateway/configuration-reference#agentsdefaultssandbox)

  </Accordion>

  <Accordion title="Host klasörünü sandbox içine nasıl bağlarım?">
    `agents.defaults.sandbox.docker.binds` değerini `["host:path:mode"]` biçiminde ayarlayın (ör. `"/home/user/src:/src:ro"`). Küresel + ajan başına bind'ler birleşir; `scope: "shared"` olduğunda ajan başına bind'ler yok sayılır. Hassas şeyler için `:ro` kullanın ve bind'lerin sandbox dosya sistemi duvarlarını aştığını unutmayın.

    OpenClaw bind kaynaklarını hem normalize edilmiş yol hem de en derin mevcut ata üzerinden çözümlenen kanonik yol karşısında doğrular. Bu, son yol segmenti henüz yokken bile symlink-parent kaçışlarının yine kapalı başarısız olacağı ve symlink çözümlemesinden sonra da allow-root kontrollerinin geçerli olduğu anlamına gelir.

    Örnekler ve güvenlik notları için bkz. [Sandboxing](/tr/gateway/sandboxing#custom-bind-mounts) ve [Sandbox vs Tool Policy vs Elevated](/tr/gateway/sandbox-vs-tool-policy-vs-elevated#bind-mounts-security-quick-check).

  </Accordion>

  <Accordion title="Hafıza nasıl çalışır?">
    OpenClaw hafızası, ajan çalışma alanındaki Markdown dosyalarından ibarettir:

    - `memory/YYYY-MM-DD.md` içindeki günlük notlar
    - `MEMORY.md` içindeki düzenlenmiş uzun vadeli notlar (yalnızca ana/özel oturumlar)

    OpenClaw ayrıca modelin
    otomatik sıkıştırmadan önce kalıcı notlar yazmasını hatırlatmak için **sessiz bir sıkıştırma öncesi hafıza boşaltma** da çalıştırır. Bu yalnızca çalışma alanı
    yazılabilirse çalışır (salt okunur sandbox'lar bunu atlar). Bkz. [Hafıza](/tr/concepts/memory).

  </Accordion>

  <Accordion title="Hafıza bir şeyleri unutmaya devam ediyor. Bunu nasıl kalıcı yaparım?">
    Botunuzdan **gerçeği hafızaya yazmasını** isteyin. Uzun vadeli notlar `MEMORY.md` içinde,
    kısa vadeli bağlam ise `memory/YYYY-MM-DD.md` içine gitmelidir.

    Bu hâlâ geliştirdiğimiz bir alandır. Modele anıları saklamasını hatırlatmak yardımcı olur;
    ne yapacağını bilir. Hâlâ unutuyorsa, Gateway'in her çalıştırmada aynı
    çalışma alanını kullandığını doğrulayın.

    Belgeler: [Hafıza](/tr/concepts/memory), [Ajan çalışma alanı](/tr/concepts/agent-workspace).

  </Accordion>

  <Accordion title="Hafıza sonsuza kadar kalıcı mı? Sınırlar nelerdir?">
    Hafıza dosyaları diskte yaşar ve siz silene kadar kalır. Sınır model değil,
    depolamanızdır. **Oturum bağlamı** yine de modelin bağlam penceresiyle
    sınırlıdır; bu yüzden uzun konuşmalar sıkıştırılabilir veya kesilebilir. Bu nedenle
    hafıza araması vardır - yalnızca ilgili parçaları yeniden bağlama çeker.

    Belgeler: [Hafıza](/tr/concepts/memory), [Bağlam](/tr/concepts/context).

  </Accordion>

  <Accordion title="Anlamsal hafıza araması için OpenAI API anahtarı gerekir mi?">
    Yalnızca **OpenAI embeddings** kullanıyorsanız. Codex OAuth sohbet/completions'ı kapsar ve
    embeddings erişimi vermez, bu yüzden **Codex ile oturum açmak (OAuth veya
    Codex CLI oturumu)** anlamsal hafıza aramasında yardımcı olmaz. OpenAI embeddings
    için yine de gerçek bir API anahtarı gerekir (`OPENAI_API_KEY` veya `models.providers.openai.apiKey`).

    Bir sağlayıcıyı açıkça ayarlamazsanız, OpenClaw bir API anahtarını çözebildiğinde
    otomatik olarak bir sağlayıcı seçer (auth profilleri, `models.providers.*.apiKey` veya env var'lar).
    Bir OpenAI anahtarı çözülürse OpenAI'yi, aksi halde Gemini anahtarı
    çözülürse Gemini'yi, sonra Voyage'ı, sonra Mistral'ı tercih eder. Uzak bir anahtar yoksa hafıza
    araması siz yapılandırana kadar devre dışı kalır. Yapılandırılmış ve mevcut bir yerel model yolunuz varsa, OpenClaw
    `local` tercih eder. `memorySearch.provider = "ollama"` açıkça
    ayarlandığında Ollama desteklenir.

    Yerelde kalmak isterseniz `memorySearch.provider = "local"` (ve isteğe bağlı olarak
    `memorySearch.fallback = "none"`) ayarlayın. Gemini embeddings istiyorsanız
    `memorySearch.provider = "gemini"` ayarlayın ve `GEMINI_API_KEY` (veya
    `memorySearch.remote.apiKey`) sağlayın. **OpenAI, Gemini, Voyage, Mistral, Ollama veya local** embedding
    modellerini destekliyoruz - kurulum ayrıntıları için bkz. [Hafıza](/tr/concepts/memory).

  </Accordion>
</AccordionGroup>

## Diskte neler nerededir

<AccordionGroup>
  <Accordion title="OpenClaw ile kullanılan tüm veriler yerel olarak mı kaydediliyor?">
    Hayır - **OpenClaw'un durumu yereldir**, ama **harici hizmetler yine de onlara gönderdiğiniz şeyi görür**.

    - **Varsayılan olarak yerel:** oturumlar, hafıza dosyaları, yapılandırma ve çalışma alanı Gateway host'ta
      (`~/.openclaw` + çalışma alanı dizininiz) yaşar.
    - **Gereken yerde uzak:** model sağlayıcılarına (Anthropic/OpenAI/vb.) gönderdiğiniz mesajlar
      onların API'lerine gider ve sohbet platformları (WhatsApp/Telegram/Slack/vb.) mesaj verilerini
      kendi sunucularında depolar.
    - **İzi siz kontrol edersiniz:** yerel modeller kullanmak istemleri makinenizde tutar, ama kanal
      trafiği yine de kanalın sunucularından geçer.

    İlgili: [Ajan çalışma alanı](/tr/concepts/agent-workspace), [Hafıza](/tr/concepts/memory).

  </Accordion>

  <Accordion title="OpenClaw verilerini nerede depolar?">
    Her şey `$OPENCLAW_STATE_DIR` altında yaşar (varsayılan: `~/.openclaw`):

    | Yol                                                             | Amaç                                                               |
    | --------------------------------------------------------------- | ------------------------------------------------------------------ |
    | `$OPENCLAW_STATE_DIR/openclaw.json`                             | Ana yapılandırma (JSON5)                                           |
    | `$OPENCLAW_STATE_DIR/credentials/oauth.json`                    | Eski OAuth içe aktarımı (ilk kullanımda auth profillerine kopyalanır) |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth-profiles.json` | Auth profilleri (OAuth, API anahtarları ve isteğe bağlı `keyRef`/`tokenRef`) |
    | `$OPENCLAW_STATE_DIR/secrets.json`                              | `file` SecretRef sağlayıcıları için isteğe bağlı dosya destekli secret yükü |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth.json`          | Eski uyumluluk dosyası (statik `api_key` girdileri temizlenmiş)    |
    | `$OPENCLAW_STATE_DIR/credentials/`                              | Sağlayıcı durumu (örn. `whatsapp/<accountId>/creds.json`)          |
    | `$OPENCLAW_STATE_DIR/agents/`                                   | Ajan başına durum (agentDir + oturumlar)                           |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                | Konuşma geçmişi ve durumu (ajan başına)                            |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/sessions.json`   | Oturum metadata'sı (ajan başına)                                   |

    Eski tek ajan yolu: `~/.openclaw/agent/*` (`openclaw doctor` tarafından taşınır).

    **Çalışma alanınız** (AGENTS.md, hafıza dosyaları, Skills vb.) ayrıdır ve `agents.defaults.workspace` ile yapılandırılır (varsayılan: `~/.openclaw/workspace`).

  </Accordion>

  <Accordion title="AGENTS.md / SOUL.md / USER.md / MEMORY.md nerede yaşamalı?">
    Bu dosyalar `~/.openclaw` içinde değil, **ajan çalışma alanında** yaşar.

    - **Çalışma alanı (ajan başına)**: `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`,
      `MEMORY.md` (veya `MEMORY.md` yoksa eski geri dönüş `memory.md`),
      `memory/YYYY-MM-DD.md`, isteğe bağlı `HEARTBEAT.md`.
    - **Durum dizini (`~/.openclaw`)**: yapılandırma, kanal/sağlayıcı durumu, auth profilleri, oturumlar, günlükler
      ve paylaşılan Skills (`~/.openclaw/skills`).

    Varsayılan çalışma alanı `~/.openclaw/workspace`'tir, şu yolla yapılandırılabilir:

    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
    }
    ```

    Bot yeniden başlatmadan sonra “unutuyorsa”, Gateway'in her açılışta aynı
    çalışma alanını kullandığını doğrulayın (ve unutmayın: uzak mod **gateway host'un**
    çalışma alanını kullanır, yerel dizüstünüzünkünü değil).

    İpucu: kalıcı bir davranış veya tercih istiyorsanız, sohbet geçmişine güvenmek yerine
    bottan bunu **AGENTS.md veya MEMORY.md içine yazmasını** isteyin.

    Bkz. [Ajan çalışma alanı](/tr/concepts/agent-workspace) ve [Hafıza](/tr/concepts/memory).

  </Accordion>

  <Accordion title="Önerilen yedekleme stratejisi">
    **Ajan çalışma alanınızı** **özel** bir git deposuna koyun ve onu özel bir yerde
    yedekleyin (örneğin GitHub private). Bu, hafızayı + AGENTS/SOUL/USER
    dosyalarını yakalar ve daha sonra asistanın “zihnini” geri yüklemenize izin verir.

    `~/.openclaw` altındaki hiçbir şeyi commit etmeyin (kimlik bilgileri, oturumlar, token'lar veya şifrelenmiş secret yükleri).
    Tam geri yükleme gerekiyorsa, çalışma alanını ve durum dizinini
    ayrı ayrı yedekleyin (yukarıdaki taşıma sorusuna bakın).

    Belgeler: [Ajan çalışma alanı](/tr/concepts/agent-workspace).

  </Accordion>

  <Accordion title="OpenClaw'u tamamen nasıl kaldırırım?">
    Özel rehbere bakın: [Kaldırma](/tr/install/uninstall).
  </Accordion>

  <Accordion title="Ajanlar çalışma alanı dışında çalışabilir mi?">
    Evet. Çalışma alanı **varsayılan cwd** ve hafıza dayanağıdır, katı bir sandbox değildir.
    Göreli yollar çalışma alanı içinde çözülür, ancak mutlak yollar
    sandbox etkin değilse host'taki diğer konumlara erişebilir. Yalıtım gerekiyorsa
    [`agents.defaults.sandbox`](/tr/gateway/sandboxing) veya ajan başına sandbox ayarlarını kullanın. Bir
    depoyu varsayılan çalışma dizini yapmak istiyorsanız, o ajanın
    `workspace` değerini depo köküne yönlendirin. OpenClaw deposu yalnızca kaynak koddur; ajanı bilinçli olarak içinde çalıştırmak istemiyorsanız
    çalışma alanını ondan ayrı tutun.

    Örnek (varsayılan cwd olarak repo):

    ```json5
    {
      agents: {
        defaults: {
          workspace: "~/Projects/my-repo",
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Uzak mod: oturum deposu nerede?">
    Oturum durumu **gateway host** tarafından sahiplenilir. Uzak moddaysanız, önem verdiğiniz oturum deposu yerel dizüstünüzde değil, uzak makinededir. Bkz. [Oturum yönetimi](/tr/concepts/session).
  </Accordion>
</AccordionGroup>

## Yapılandırma temelleri

<AccordionGroup>
  <Accordion title="Yapılandırma hangi biçimde? Nerede?">
    OpenClaw isteğe bağlı bir **JSON5** yapılandırmasını `$OPENCLAW_CONFIG_PATH` yolundan okur (varsayılan: `~/.openclaw/openclaw.json`):

    ```
    $OPENCLAW_CONFIG_PATH
    ```

    Dosya yoksa güvenli sayılabilecek varsayılanları kullanır (varsayılan çalışma alanı olarak `~/.openclaw/workspace` dahil).

  </Accordion>

  <Accordion title='gateway.bind: "lan" (veya "tailnet") ayarladım ve şimdi hiçbir şey dinlemiyor / UI unauthorized diyor'>
    Loopback dışı bind'ler **geçerli bir gateway auth yolu** gerektirir. Pratikte bu şunlardan biridir:

    - paylaşılan gizli anahtar auth'u: token veya parola
    - doğru yapılandırılmış loopback dışı, kimlik farkındalıklı bir reverse proxy arkasında `gateway.auth.mode: "trusted-proxy"`

    ```json5
    {
      gateway: {
        bind: "lan",
        auth: {
          mode: "token",
          token: "replace-me",
        },
      },
    }
    ```

    Notlar:

    - `gateway.remote.token` / `.password` tek başlarına yerel gateway auth'u etkinleştirmez.
    - Yerel çağrı yolları, yalnızca `gateway.auth.*` ayarlanmamışsa geri dönüş olarak `gateway.remote.*` kullanabilir.
    - Parola auth'u için bunun yerine `gateway.auth.mode: "password"` ve `gateway.auth.password` (veya `OPENCLAW_GATEWAY_PASSWORD`) ayarlayın.
    - `gateway.auth.token` / `gateway.auth.password` SecretRef üzerinden açıkça yapılandırılmış ama çözülememişse çözümleme kapalı şekilde başarısız olur (uzak geri dönüş bunu gizlemez).
    - Paylaşılan gizli anahtar kullanan Control UI kurulumları `connect.params.auth.token` veya `connect.params.auth.password` ile kimlik doğrular (uygulama/UI ayarlarında saklanır). Tailscale Serve veya `trusted-proxy` gibi kimlik taşıyan kipler bunun yerine istek başlıklarını kullanır. Paylaşılan gizli anahtarları URL'lere koymaktan kaçının.
    - `gateway.auth.mode: "trusted-proxy"` ile aynı host üzerindeki loopback reverse proxy'ler yine de trusted-proxy auth'unu karşılamaz. Güvenilir proxy yapılandırılmış loopback dışı bir kaynak olmalıdır.

  </Accordion>

  <Accordion title="Neden artık localhost'ta bir token'a ihtiyacım var?">
    OpenClaw, loopback dahil varsayılan olarak gateway auth'unu zorunlu kılar. Normal varsayılan yolda bu token auth'u anlamına gelir: açık bir auth yolu yapılandırılmadıysa, gateway başlatma token moduna çözülür ve otomatik olarak bir token üretip bunu `gateway.auth.token` içine kaydeder; bu nedenle **yerel WS istemcileri kimlik doğrulamalıdır**. Bu, diğer yerel süreçlerin Gateway'i çağırmasını engeller.

    Farklı bir auth yolu tercih ediyorsanız, açıkça parola modunu (veya loopback dışı kimlik farkındalıklı reverse proxy'ler için `trusted-proxy`) seçebilirsiniz. **Gerçekten** açık loopback istiyorsanız, yapılandırmanızda `gateway.auth.mode: "none"` değerini açıkça ayarlayın. Doctor sizin için istediğiniz zaman token üretebilir: `openclaw doctor --generate-gateway-token`.

  </Accordion>

  <Accordion title="Yapılandırmayı değiştirdikten sonra yeniden başlatmam gerekiyor mu?">
    Gateway yapılandırmayı izler ve hot-reload destekler:

    - `gateway.reload.mode: "hybrid"` (varsayılan): güvenli değişiklikleri hot-apply eder, kritik olanlar için yeniden başlatır
    - `hot`, `restart`, `off` da desteklenir

  </Accordion>

  <Accordion title="Eğlenceli CLI sloganlarını nasıl kapatırım?">
    Yapılandırmada `cli.banner.taglineMode` ayarlayın:

    ```json5
    {
      cli: {
        banner: {
          taglineMode: "off", // random | default | off
        },
      },
    }
    ```

    - `off`: slogan metnini gizler ama afiş başlığı/sürüm satırını tutar.
    - `default`: her seferinde `All your chats, one OpenClaw.` kullanır.
    - `random`: dönen komik/mevsimsel sloganlar (varsayılan davranış).
    - Hiç afiş istemiyorsanız env `OPENCLAW_HIDE_BANNER=1` ayarlayın.

  </Accordion>

  <Accordion title="Web aramayı (ve web fetch'i) nasıl etkinleştiririm?">
    `web_fetch` API anahtarı olmadan çalışır. `web_search` seçtiğiniz
    sağlayıcıya bağlıdır:

    - Brave, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search, Perplexity ve Tavily gibi API destekli sağlayıcılar normal API key kurulumlarını gerektirir.
    - Ollama Web Search anahtarsızdır, ama yapılandırılmış Ollama host'unuzu kullanır ve `ollama signin` gerektirir.
    - DuckDuckGo anahtarsızdır, ama resmi olmayan HTML tabanlı bir entegrasyondur.
    - SearXNG anahtarsız/self-hosted'dir; `SEARXNG_BASE_URL` veya `plugins.entries.searxng.config.webSearch.baseUrl` yapılandırın.

    **Önerilen:** `openclaw configure --section web` çalıştırın ve bir sağlayıcı seçin.
    Ortam değişkeni alternatifleri:

    - Brave: `BRAVE_API_KEY`
    - Exa: `EXA_API_KEY`
    - Firecrawl: `FIRECRAWL_API_KEY`
    - Gemini: `GEMINI_API_KEY`
    - Grok: `XAI_API_KEY`
    - Kimi: `KIMI_API_KEY` veya `MOONSHOT_API_KEY`
    - MiniMax Search: `MINIMAX_CODE_PLAN_KEY`, `MINIMAX_CODING_API_KEY` veya `MINIMAX_API_KEY`
    - Perplexity: `PERPLEXITY_API_KEY` veya `OPENROUTER_API_KEY`
    - SearXNG: `SEARXNG_BASE_URL`
    - Tavily: `TAVILY_API_KEY`

    ```json5
    {
      plugins: {
        entries: {
          brave: {
            config: {
              webSearch: {
                apiKey: "BRAVE_API_KEY_HERE",
              },
            },
          },
        },
        },
        tools: {
          web: {
            search: {
              enabled: true,
              provider: "brave",
              maxResults: 5,
            },
            fetch: {
              enabled: true,
              provider: "firecrawl", // isteğe bağlı; otomatik algılama için çıkarın
            },
          },
        },
    }
    ```

    Sağlayıcıya özgü web-search yapılandırması artık `plugins.entries.<plugin>.config.webSearch.*` altında yaşar.
    Eski `tools.web.search.*` sağlayıcı yolları uyumluluk için geçici olarak hâlâ yüklenir, ancak yeni yapılandırmalarda kullanılmamalıdır.
    Firecrawl web-fetch geri dönüş yapılandırması `plugins.entries.firecrawl.config.webFetch.*` altında yaşar.

    Notlar:

    - allowlist kullanıyorsanız `web_search`/`web_fetch`/`x_search` veya `group:web` ekleyin.
    - `web_fetch` varsayılan olarak etkindir (açıkça kapatılmadıkça).
    - `tools.web.fetch.provider` atlanırsa, OpenClaw mevcut kimlik bilgilerinden hazır ilk fetch fallback sağlayıcısını otomatik algılar. Bugün paketli sağlayıcı Firecrawl'dır.
    - Daemon'lar env var'ları `~/.openclaw/.env` içinden (veya hizmet ortamından) okur.

    Belgeler: [Web araçları](/tr/tools/web).

  </Accordion>

  <Accordion title="config.apply yapılandırmamı sildi. Bunu nasıl kurtarır ve önlerim?">
    `config.apply` **tüm yapılandırmayı** değiştirir. Kısmi bir nesne gönderirseniz diğer
    her şey kaldırılır.

    Kurtarma:

    - Yedekten geri yükleyin (git veya kopyalanmış `~/.openclaw/openclaw.json`).
    - Yedeğiniz yoksa `openclaw doctor` yeniden çalıştırın ve kanalları/modelleri yeniden yapılandırın.
    - Bu beklenmedikse bir hata bildirin ve bilinen son yapılandırmanızı veya herhangi bir yedeği ekleyin.
    - Yerel bir kodlama ajanı çoğu zaman günlüklerden veya geçmişten çalışan bir yapılandırmayı yeniden kurabilir.

    Önleme:

    - Küçük değişiklikler için `openclaw config set` kullanın.
    - Etkileşimli düzenleme için `openclaw configure` kullanın.
    - Tam yol veya alan şekli konusunda emin değilseniz önce `config.schema.lookup` kullanın; sığ bir şema düğümü ve aşağı inmek için anlık alt özetler döndürür.
    - Kısmi RPC düzenlemeleri için `config.patch` kullanın; `config.apply` yalnızca tam yapılandırma değiştirme için kalsın.
    - Bir ajan çalıştırmasından sahip-özel `gateway` aracını kullanıyorsanız, bu araç yine de `tools.exec.ask` / `tools.exec.security` yollarına yazmayı reddeder (aynı korumalı exec yollarına normalize olan eski `tools.bash.*` takma adları dahil).

    Belgeler: [Yapılandırma](/cli/config), [Yapılandır](/cli/configure), [Doctor](/tr/gateway/doctor).

  </Accordion>

  <Accordion title="Merkezi bir Gateway'i cihazlara dağılmış uzman işçilerle nasıl çalıştırırım?">
    Yaygın desen **tek bir Gateway** (ör. Raspberry Pi) artı **nodes** ve **agents**'tır:

    - **Gateway (merkezi):** kanalların (Signal/WhatsApp), yönlendirme ve oturumların sahibidir.
    - **Nodes (cihazlar):** Mac/iOS/Android çevrebirim olarak bağlanır ve yerel araçları (`system.run`, `canvas`, `camera`) açar.
    - **Agents (işçiler):** özel roller için ayrı beyinler/çalışma alanlarıdır (ör. “Hetzner ops”, “Kişisel veriler”).
    - **Alt ajanlar:** paralellik istediğinizde ana ajandan arka plan işi başlatır.
    - **TUI:** Gateway'e bağlanır ve ajan/oturum değiştirir.

    Belgeler: [Nodes](/tr/nodes), [Uzak erişim](/tr/gateway/remote), [Çoklu Ajan Yönlendirme](/tr/concepts/multi-agent), [Alt ajanlar](/tr/tools/subagents), [TUI](/web/tui).

  </Accordion>

  <Accordion title="OpenClaw tarayıcısı headless çalışabilir mi?">
    Evet. Bu bir yapılandırma seçeneğidir:

    ```json5
    {
      browser: { headless: true },
      agents: {
        defaults: {
          sandbox: { browser: { headless: true } },
        },
      },
    }
    ```

    Varsayılan `false`'tur (başlıklı). Headless kip bazı sitelerde anti-bot kontrollerini tetiklemeye daha yatkındır. Bkz. [Tarayıcı](/tr/tools/browser).

    Headless aynı **Chromium motorunu** kullanır ve çoğu otomasyon için çalışır (formlar, tıklamalar, scraping, girişler). Temel farklar:

    - Görünür tarayıcı penceresi yoktur (görsel gerekirse ekran görüntüsü kullanın).
    - Bazı siteler headless kipte otomasyona karşı daha katıdır (CAPTCHA, anti-bot).
      Örneğin X/Twitter çoğu zaman headless oturumları engeller.

  </Accordion>

  <Accordion title="Tarayıcı kontrolü için Brave'i nasıl kullanırım?">
    `browser.executablePath` değerini Brave binary'nize (veya Chromium tabanlı başka bir tarayıcıya) ayarlayın ve Gateway'i yeniden başlatın.
    Tam yapılandırma örnekleri için bkz. [Tarayıcı](/tr/tools/browser#use-brave-or-another-chromium-based-browser).
  </Accordion>
</AccordionGroup>

## Uzak gateway'ler ve nodes

<AccordionGroup>
  <Accordion title="Komutlar Telegram, gateway ve nodes arasında nasıl yayılır?">
    Telegram mesajları **gateway** tarafından işlenir. Gateway ajanı çalıştırır ve
    yalnızca bir node aracı gerektiğinde **Gateway WebSocket** üzerinden node'ları çağırır:

    Telegram → Gateway → Agent → `node.*` → Node → Gateway → Telegram

    Nodes gelen sağlayıcı trafiğini görmez; yalnızca node RPC çağrıları alır.

  </Accordion>

  <Accordion title="Gateway uzakta barındırılıyorsa ajanım bilgisayarıma nasıl erişebilir?">
    Kısa yanıt: **bilgisayarınızı bir node olarak eşleştirin**. Gateway başka yerde çalışır ama
    Gateway WebSocket üzerinden yerel makinenizdeki `node.*` araçlarını (ekran, kamera, sistem) çağırabilir.

    Tipik kurulum:

    1. Gateway'i her zaman açık host üzerinde çalıştırın (VPS/ev sunucusu).
    2. Gateway host'u + bilgisayarınızı aynı tailnet'e koyun.
    3. Gateway WS'nin erişilebilir olduğundan emin olun (tailnet bind veya SSH tunnel).
    4. macOS uygulamasını yerelde açın ve **Remote over SSH** modunda (veya doğrudan tailnet)
       bağlanın ki bir node olarak kaydolabilsin.
    5. Gateway üzerinde node'u onaylayın:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    Ayrı bir TCP köprüsü gerekmez; nodes Gateway WebSocket üzerinden bağlanır.

    Güvenlik hatırlatması: bir macOS node eşleştirmek o makinede `system.run` izni verir. Yalnızca güvendiğiniz cihazları
    eşleştirin ve [Güvenlik](/tr/gateway/security) bölümünü gözden geçirin.

    Belgeler: [Nodes](/tr/nodes), [Gateway protokolü](/tr/gateway/protocol), [macOS remote mode](/tr/platforms/mac/remote), [Güvenlik](/tr/gateway/security).

  </Accordion>

  <Accordion title="Tailscale bağlı ama hiç yanıt gelmiyor. Ne yapmalıyım?">
    Temelleri kontrol edin:

    - Gateway çalışıyor mu: `openclaw gateway status`
    - Gateway sağlığı: `openclaw status`
    - Kanal sağlığı: `openclaw channels status`

    Sonra auth ve yönlendirmeyi doğrulayın:

    - Tailscale Serve kullanıyorsanız, `gateway.auth.allowTailscale` doğru ayarlandığından emin olun.
    - SSH tunnel üzerinden bağlanıyorsanız, yerel tunnel'in açık olduğunu ve doğru porta işaret ettiğini doğrulayın.
    - allowlist'lerinizin (DM veya grup) hesabınızı içerdiğini doğrulayın.

    Belgeler: [Tailscale](/tr/gateway/tailscale), [Uzak erişim](/tr/gateway/remote), [Kanallar](/tr/channels).

  </Accordion>

  <Accordion title="İki OpenClaw örneği birbiriyle konuşabilir mi (yerel + VPS)?">
    Evet. Yerleşik bir “bot-to-bot” köprü yoktur, ama bunu birkaç
    güvenilir yolla kurabilirsiniz:

    **En basiti:** iki botun da erişebildiği normal bir sohbet kanalı kullanın (Telegram/Slack/WhatsApp).
    Bot A'nın Bot B'ye mesaj göndermesini sağlayın, sonra Bot B normal şekilde yanıtlasın.

    **CLI köprüsü (genel):** diğer Gateway'i
    `openclaw agent --message ... --deliver` ile çağıran bir betik çalıştırın; hedef, diğer botun
    dinlediği bir sohbet olmalıdır. Botlardan biri uzak bir VPS üzerindeyse, CLI'ınızı o uzak Gateway'e
    SSH/Tailscale üzerinden yönlendirin (bkz. [Uzak erişim](/tr/gateway/remote)).

    Örnek desen (hedef Gateway'e erişebilen bir makineden çalıştırın):

    ```bash
    openclaw agent --message "Hello from local bot" --deliver --channel telegram --reply-to <chat-id>
    ```

    İpucu: iki botun sonsuz döngüye girmemesi için bir koruma ekleyin (yalnızca mention,
    kanal allowlist'leri veya “bot mesajlarına yanıt verme” kuralı).

    Belgeler: [Uzak erişim](/tr/gateway/remote), [Agent CLI](/cli/agent), [Agent send](/tr/tools/agent-send).

  </Accordion>

  <Accordion title="Birden fazla ajan için ayrı VPS'lere ihtiyacım var mı?">
    Hayır. Tek bir Gateway, her birinin kendi çalışma alanı, model varsayılanları
    ve yönlendirmesi olan birden fazla ajanı barındırabilir. Bu normal kurulumdur ve
    ajan başına bir VPS çalıştırmaktan çok daha ucuz ve basittir.

    Ayrı VPS'leri yalnızca sert yalıtım (güvenlik sınırları) gerektiğinde veya
    paylaşmak istemediğiniz çok farklı yapılandırmalar olduğunda kullanın. Aksi halde tek Gateway tutun ve
    birden fazla ajan veya alt ajan kullanın.

  </Accordion>

  <Accordion title="Uzak bir VPS'ten SSH yapmak yerine kişisel dizüstü bilgisayarımda node kullanmanın faydası var mı?">
    Evet - nodes, uzak bir Gateway'den dizüstünüze erişmenin birinci sınıf yoludur ve
    kabuk erişiminden fazlasını açar. Gateway macOS/Linux üzerinde çalışır (Windows, WSL2 üzerinden) ve
    hafiftir (küçük bir VPS veya Raspberry Pi sınıfı bir kutu yeterlidir; 4 GB RAM fazlasıyla yeterlidir), bu yüzden yaygın
    kurulum, her zaman açık bir host artı dizüstünüzün node olmasıdır.

    - **Gelen SSH gerekmez.** Nodes dışarı doğru Gateway WebSocket'e bağlanır ve cihaz eşleştirmesi kullanır.
    - **Daha güvenli yürütme kontrolleri.** `system.run`, o dizüstündeki node allowlist/onaylarıyla kapatılır.
    - **Daha fazla cihaz aracı.** Nodes, `system.run` yanında `canvas`, `camera` ve `screen` açar.
    - **Yerel tarayıcı otomasyonu.** Gateway'i bir VPS'te tutun, ama dizüstündeki node host üzerinden Chrome'u yerelde çalıştırın veya host üzerindeki yerel Chrome'a Chrome MCP üzerinden bağlanın.

    Ad hoc shell erişimi için SSH uygundur, ama devam eden ajan iş akışları ve
    cihaz otomasyonu için nodes daha basittir.

    Belgeler: [Nodes](/tr/nodes), [Nodes CLI](/cli/nodes), [Tarayıcı](/tr/tools/browser).

  </Accordion>

  <Accordion title="Nodes bir gateway hizmeti çalıştırır mı?">
    Hayır. Aynı host üzerinde yalnızca **bir gateway** çalışmalıdır; bilerek yalıtılmış profiller çalıştırmıyorsanız (bkz. [Birden fazla gateway](/tr/gateway/multiple-gateways)). Nodes, gateway'e bağlanan çevrebirimlerdir
    (iOS/Android nodes veya menü çubuğu uygulamasında macOS “node mode”). Headless node
    host'lar ve CLI denetimi için bkz. [Node host CLI](/cli/node).

    `gateway`, `discovery` ve `canvasHost` değişiklikleri için tam yeniden başlatma gerekir.

  </Accordion>

  <Accordion title="Yapılandırma uygulamak için API / RPC yolu var mı?">
    Evet.

    - `config.schema.lookup`: yazmadan önce sığ şema düğümü, eşleşen UI ipucu ve anlık alt özetleriyle bir yapılandırma alt ağacını inceleyin
    - `config.get`: mevcut anlık görüntüyü + hash'i getirin
    - `config.patch`: güvenli kısmi güncelleme (çoğu RPC düzenlemesi için tercih edilir); mümkünse hot-reload eder, gerekirse yeniden başlatır
    - `config.apply`: tam yapılandırmayı doğrular + değiştirir; mümkünse hot-reload eder, gerekirse yeniden başlatır
    - Sahip-özel `gateway` çalışma zamanı aracı yine `tools.exec.ask` / `tools.exec.security` yollarını yeniden yazmayı reddeder; eski `tools.bash.*` takma adları aynı korumalı exec yollarına normalize olur

  </Accordion>

  <Accordion title="İlk kurulum için asgari makul yapılandırma">
    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
      channels: { whatsapp: { allowFrom: ["+15555550123"] } },
    }
    ```

    Bu, çalışma alanınızı ayarlar ve botu kimin tetikleyebileceğini sınırlar.

  </Accordion>

  <Accordion title="Bir VPS'te Tailscale'i nasıl kurar ve Mac'imden nasıl bağlanırım?">
    Asgari adımlar:

    1. **VPS'te yükleyin + oturum açın**

       ```bash
       curl -fsSL https://tailscale.com/install.sh | sh
       sudo tailscale up
       ```

    2. **Mac'inizde yükleyin + oturum açın**
       - Tailscale uygulamasını kullanın ve aynı tailnet'e giriş yapın.
    3. **MagicDNS'i etkinleştirin (önerilir)**
       - Tailscale yönetici konsolunda MagicDNS'i açın; böylece VPS'in kararlı bir adı olur.
    4. **Tailnet host adını kullanın**
       - SSH: `ssh user@your-vps.tailnet-xxxx.ts.net`
       - Gateway WS: `ws://your-vps.tailnet-xxxx.ts.net:18789`

    SSH olmadan Control UI istiyorsanız VPS'te Tailscale Serve kullanın:

    ```bash
    openclaw gateway --tailscale serve
    ```

    Bu, gateway'i loopback'e bağlı tutar ve Tailscale üzerinden HTTPS açığa çıkarır. Bkz. [Tailscale](/tr/gateway/tailscale).

  </Accordion>

  <Accordion title="Uzak bir Gateway'e (Tailscale Serve) bir Mac node'u nasıl bağlarım?">
    Serve, **Gateway Control UI + WS** açığa çıkarır. Nodes aynı Gateway WS uç noktası üzerinden bağlanır.

    Önerilen kurulum:

    1. **VPS + Mac'in aynı tailnet'te olduğundan emin olun**.
    2. **macOS uygulamasını Remote modunda kullanın** (SSH hedefi tailnet host adı olabilir).
       Uygulama gateway portunu tüneller ve node olarak bağlanır.
    3. **Gateway üzerinde node'u onaylayın**:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    Belgeler: [Gateway protokolü](/tr/gateway/protocol), [Keşif](/tr/gateway/discovery), [macOS remote mode](/tr/platforms/mac/remote).

  </Accordion>

  <Accordion title="İkinci dizüstüne kurulum mu yapmalıyım yoksa sadece bir node mu eklemeliyim?">
    İkinci dizüstünde yalnızca **yerel araçlara** (ekran/kamera/exec) ihtiyacınız varsa, onu
    **node** olarak ekleyin. Bu tek bir Gateway tutar ve çift yapılandırmadan kaçınır. Yerel node araçları
    şu anda yalnızca macOS'tur, ancak bunları diğer işletim sistemlerine de genişletmeyi planlıyoruz.

    Yalnızca **sert yalıtım** veya tamamen ayrı iki bot gerektiğinde ikinci bir Gateway kurun.

    Belgeler: [Nodes](/tr/nodes), [Nodes CLI](/cli/nodes), [Birden fazla gateway](/tr/gateway/multiple-gateways).

  </Accordion>
</AccordionGroup>

## Ortam değişkenleri ve .env yükleme

<AccordionGroup>
  <Accordion title="OpenClaw ortam değişkenlerini nasıl yükler?">
    OpenClaw ortam değişkenlerini ebeveyn süreçten (shell, launchd/systemd, CI vb.) okur ve ayrıca şunları yükler:

    - mevcut çalışma dizinindeki `.env`
    - `~/.openclaw/.env` içindeki küresel geri dönüş `.env` dosyası (diğer adıyla `$OPENCLAW_STATE_DIR/.env`)

    Hiçbir `.env` dosyası mevcut env var'ları override etmez.

    Yapılandırma içinde satır içi env var'lar da tanımlayabilirsiniz (yalnızca süreç env'inde eksiklerse uygulanır):

    ```json5
    {
      env: {
        OPENROUTER_API_KEY: "sk-or-...",
        vars: { GROQ_API_KEY: "gsk-..." },
      },
    }
    ```

    Tam öncelik ve kaynaklar için bkz. [/environment](/tr/help/environment).

  </Accordion>

  <Accordion title="Gateway'i hizmet üzerinden başlattım ve env var'larım kayboldu. Ne yapmalıyım?">
    İki yaygın çözüm:

    1. Eksik anahtarları `~/.openclaw/.env` içine koyun; böylece hizmet shell env'inizi devralmasa bile alınırlar.
    2. Shell içe aktarmayı etkinleştirin (isteğe bağlı kolaylık):

    ```json5
    {
      env: {
        shellEnv: {
          enabled: true,
          timeoutMs: 15000,
        },
      },
    }
    ```

    Bu, giriş shell'inizi çalıştırır ve yalnızca beklenen eksik anahtarları içe aktarır (asla override etmez).
    Env var eşdeğerleri:
    `OPENCLAW_LOAD_SHELL_ENV=1`, `OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`.

  </Accordion>

  <Accordion title='COPILOT_GITHUB_TOKEN ayarladım ama models status "Shell env: off." gösteriyor. Neden?'>
    `openclaw models status`, **shell env içe aktarma** özelliğinin etkin olup olmadığını raporlar. "Shell env: off"
    env var'larınızın eksik olduğu anlamına gelmez - yalnızca OpenClaw'un
    oturum açma shell'inizi otomatik yüklemeyeceği anlamına gelir.

    Gateway bir hizmet (launchd/systemd) olarak çalışıyorsa shell
    ortamınızı devralmaz. Bunu şu yollardan biriyle düzeltin:

    1. Token'ı `~/.openclaw/.env` içine koyun:

       ```
       COPILOT_GITHUB_TOKEN=...
       ```

    2. Veya shell içe aktarmayı etkinleştirin (`env.shellEnv.enabled: true`).
    3. Veya bunu config `env` bloğunuza ekleyin (yalnızca eksikse uygulanır).

    Sonra gateway'i yeniden başlatın ve tekrar kontrol edin:

    ```bash
    openclaw models status
    ```

    Copilot token'ları `COPILOT_GITHUB_TOKEN` üzerinden okunur (ayrıca `GH_TOKEN` / `GITHUB_TOKEN`).
    Bkz. [/concepts/model-providers](/tr/concepts/model-providers) ve [/environment](/tr/help/environment).

  </Accordion>
</AccordionGroup>

## Oturumlar ve birden fazla sohbet

<AccordionGroup>
  <Accordion title="Yeni bir konuşmayı nasıl başlatırım?">
    Tek başına mesaj olarak `/new` veya `/reset` gönderin. Bkz. [Oturum yönetimi](/tr/concepts/session).
  </Accordion>

  <Accordion title="Hiç /new göndermezsem oturumlar otomatik sıfırlanır mı?">
    Oturumlar `session.idleMinutes` süresi sonunda sona erebilir, ancak bu varsayılan olarak **kapalıdır** (varsayılan **0**).
    Boşta sona ermeyi etkinleştirmek için bunu pozitif bir değere ayarlayın. Etkinleştirildiğinde,
    boşta kalma süresinden sonraki **bir sonraki** mesaj o sohbet anahtarı için taze bir oturum kimliği başlatır.
    Bu, dökümleri silmez - yalnızca yeni bir oturum başlatır.

    ```json5
    {
      session: {
        idleMinutes: 240,
      },
    }
    ```

  </Accordion>

  <Accordion title="OpenClaw örneklerinden oluşan bir ekip kurmanın bir yolu var mı (bir CEO ve birçok ajan)?">
    Evet, **çoklu ajan yönlendirme** ve **alt ajanlar** ile. Bir koordinatör
    ajan ve kendi çalışma alanları ve modelleri olan birkaç işçi ajan oluşturabilirsiniz.

    Ancak bunu daha çok **eğlenceli bir deney** olarak görmek gerekir. Token açısından ağırdır ve çoğu zaman
    ayrı oturumlar kullanan tek bottan daha az verimlidir. Tipik olarak öngördüğümüz model,
    konuştuğunuz tek bot ve paralel işler için farklı oturumlardır. Bu
    bot gerektiğinde alt ajanlar da başlatabilir.

    Belgeler: [Çoklu ajan yönlendirme](/tr/concepts/multi-agent), [Alt ajanlar](/tr/tools/subagents), [Agents CLI](/cli/agents).

  </Accordion>

  <Accordion title="Neden bağlam görev ortasında kesildi? Bunu nasıl önlerim?">
    Oturum bağlamı model penceresiyle sınırlıdır. Uzun sohbetler, büyük araç çıktıları veya çok sayıda
    dosya sıkıştırma veya kesilmeyi tetikleyebilir.

    Yardımcı olanlar:

    - Bottan mevcut durumu özetleyip bir dosyaya yazmasını isteyin.
    - Uzun görevlerden önce `/compact`, konu değiştirirken `/new` kullanın.
    - Önemli bağlamı çalışma alanında tutun ve bottan tekrar okumasını isteyin.
    - Ana sohbet küçük kalsın diye uzun veya paralel işler için alt ajanlar kullanın.
    - Bu sık oluyorsa daha büyük bağlam penceresine sahip bir model seçin.

  </Accordion>

  <Accordion title="OpenClaw'u tamamen nasıl sıfırlar ama kurulu tutarım?">
    Sıfırlama komutunu kullanın:

    ```bash
    openclaw reset
    ```

    Etkileşimsiz tam sıfırlama:

    ```bash
    openclaw reset --scope full --yes --non-interactive
    ```

    Sonra kurulumu yeniden çalıştırın:

    ```bash
    openclaw onboard --install-daemon
    ```

    Notlar:

    - Onboarding mevcut bir yapılandırma görürse **Reset** seçeneğini de sunar. Bkz. [Onboarding (CLI)](/tr/start/wizard).
    - Profil kullandıysanız (`--profile` / `OPENCLAW_PROFILE`), her durum dizinini sıfırlayın (varsayılanlar `~/.openclaw-<profile>` şeklindedir).
    - Geliştirme sıfırlaması: `openclaw gateway --dev --reset` (yalnızca geliştirme; geliştirme yapılandırmasını + kimlik bilgilerini + oturumları + çalışma alanını siler).

  </Accordion>

  <Accordion title='“context too large” hataları alıyorum - nasıl sıfırlar veya sıkıştırırım?'>
    Şunlardan birini kullanın:

    - **Sıkıştırma** (konuşmayı korur ama eski turları özetler):

      ```
      /compact
      ```

      veya özeti yönlendirmek için `/compact <instructions>`.

    - **Sıfırlama** (aynı sohbet anahtarı için taze oturum kimliği):

      ```
      /new
      /reset
      ```

    Bu devam ediyorsa:

    - Eski araç çıktısını kırpmak için **session pruning** (`agents.defaults.contextPruning`) özelliğini etkinleştirin veya ayarlayın.
    - Daha büyük bağlam penceresine sahip bir model kullanın.

    Belgeler: [Sıkıştırma](/tr/concepts/compaction), [Oturum budama](/tr/concepts/session-pruning), [Oturum yönetimi](/tr/concepts/session).

  </Accordion>

  <Accordion title='Neden "LLM request rejected: messages.content.tool_use.input field required" görüyorum?'>
    Bu bir sağlayıcı doğrulama hatasıdır: model gerekli `input`
    olmadan bir `tool_use` bloğu üretti. Genelde oturum geçmişinin bayat veya bozuk olduğu anlamına gelir (çoğu zaman uzun iş parçacıklarından
    veya araç/şema değişikliğinden sonra).

    Çözüm: tek başına mesaj olarak `/new` ile yeni bir oturum başlatın.

  </Accordion>

  <Accordion title="Neden her 30 dakikada bir heartbeat mesajı alıyorum?">
    Heartbeat'ler varsayılan olarak **30m**'de bir (**OAuth auth kullanıldığında 1h**) çalışır. Ayarlayın veya kapatın:

    ```json5
    {
      agents: {
        defaults: {
          heartbeat: {
            every: "2h", // veya kapatmak için "0m"
          },
        },
      },
    }
    ```

    `HEARTBEAT.md` mevcut ama fiilen boşsa (yalnızca boş satırlar ve
    `# Heading` gibi markdown başlıkları), OpenClaw API çağrılarını azaltmak için heartbeat çalıştırmasını atlar.
    Dosya yoksa heartbeat yine çalışır ve model ne yapacağına karar verir.

    Ajan başına override'lar `agents.list[].heartbeat` kullanır. Belgeler: [Heartbeat](/tr/gateway/heartbeat).

  </Accordion>

  <Accordion title='Bir WhatsApp grubuna "bot hesabı" eklemem gerekir mi?'>
    Hayır. OpenClaw **kendi hesabınızda** çalışır; siz gruptaysanız OpenClaw da onu görebilir.
    Varsayılan olarak, gönderenlere izin verene kadar grup yanıtları engellenir (`groupPolicy: "allowlist"`).

    Yalnızca **sizin** grup yanıtlarını tetikleyebilmenizi istiyorsanız:

    ```json5
    {
      channels: {
        whatsapp: {
          groupPolicy: "allowlist",
          groupAllowFrom: ["+15551234567"],
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Bir WhatsApp grubunun JID'sini nasıl alırım?">
    Seçenek 1 (en hızlı): günlükleri izleyin ve gruba bir test mesajı gönderin:

    ```bash
    openclaw logs --follow --json
    ```

    `@g.us` ile biten `chatId` (veya `from`) değerini arayın, örneğin:
    `1234567890-1234567890@g.us`.

    Seçenek 2 (zaten yapılandırılmış/allowlist'te ise): yapılandırmadan grupları listeleyin:

    ```bash
    openclaw directory groups list --channel whatsapp
    ```

    Belgeler: [WhatsApp](/tr/channels/whatsapp), [Directory](/cli/directory), [Günlükler](/cli/logs).

  </Accordion>

  <Accordion title="OpenClaw neden bir grupta yanıt vermiyor?">
    İki yaygın neden:

    - Mention gating açık (varsayılan). Botu @mention etmeniz gerekir (veya `mentionPatterns` eşleşmeli).
    - `channels.whatsapp.groups` yapılandırdınız ama `"*"` yok ve grup allowlist'te değil.

    Bkz. [Gruplar](/tr/channels/groups) ve [Grup mesajları](/tr/channels/group-messages).

  </Accordion>

  <Accordion title="Gruplar/iş parçacıkları DM'lerle bağlam paylaşır mı?">
    Doğrudan sohbetler varsayılan olarak ana oturuma çöker. Gruplar/kanalların kendi oturum anahtarları vardır ve Telegram konuları / Discord iş parçacıkları ayrı oturumlardır. Bkz. [Gruplar](/tr/channels/groups) ve [Grup mesajları](/tr/channels/group-messages).
  </Accordion>

  <Accordion title="Kaç çalışma alanı ve ajan oluşturabilirim?">
    Sert sınırlar yok. Onlarca (hatta yüzlerce) sorun olmaz, ancak şunlara dikkat edin:

    - **Disk büyümesi:** oturumlar + dökümler `~/.openclaw/agents/<agentId>/sessions/` altında yaşar.
    - **Token maliyeti:** daha fazla ajan, daha fazla eşzamanlı model kullanımı demektir.
    - **Operasyon yükü:** ajan başına auth profilleri, çalışma alanları ve kanal yönlendirmesi.

    İpuçları:

    - Ajan başına **etkin** tek çalışma alanı tutun (`agents.defaults.workspace`).
    - Disk büyürse eski oturumları budayın (JSONL veya store girdilerini silin).
    - Başıboş çalışma alanlarını ve profil uyumsuzluklarını fark etmek için `openclaw doctor` kullanın.

  </Accordion>

  <Accordion title="Aynı anda birden fazla bot veya sohbet (Slack) çalıştırabilir miyim ve bunu nasıl kurmalıyım?">
    Evet. Birden fazla yalıtılmış ajan çalıştırmak ve gelen mesajları
    kanal/hesap/peer bazında yönlendirmek için **Çoklu Ajan Yönlendirme** kullanın. Slack bir kanal olarak desteklenir ve belirli ajanlara bağlanabilir.

    Tarayıcı erişimi güçlüdür ama “insanın yapabildiği her şeyi yapar” değildir - anti-bot, CAPTCHA ve MFA
    otomasyonu yine engelleyebilir. En güvenilir tarayıcı denetimi için host üzerindeki yerel Chrome MCP'yi kullanın,
    veya tarayıcıyı gerçekten çalıştıran makinede CDP kullanın.

    En iyi uygulama kurulumu:

    - Her zaman açık Gateway host'u (VPS/Mac mini).
    - Rol başına bir ajan (bindings).
    - Bu ajanlara bağlı Slack kanal(lar)ı.
    - Gerektiğinde Chrome MCP veya node üzerinden yerel tarayıcı.

    Belgeler: [Çoklu Ajan Yönlendirme](/tr/concepts/multi-agent), [Slack](/tr/channels/slack),
    [Tarayıcı](/tr/tools/browser), [Nodes](/tr/nodes).

  </Accordion>
</AccordionGroup>

## Modeller: varsayılanlar, seçim, takma adlar, geçiş

<AccordionGroup>
  <Accordion title='“Varsayılan model” nedir?'>
    OpenClaw'un varsayılan modeli şu şekilde ayarladığınız modeldir:

    ```
    agents.defaults.model.primary
    ```

    Modeller `provider/model` olarak başvurulur (örnek: `openai/gpt-5.4`). Sağlayıcıyı atlarsanız, OpenClaw önce bir takma adı dener, sonra o tam model kimliği için benzersiz bir yapılandırılmış sağlayıcı eşleşmesini dener ve ancak ondan sonra eski bir uyumluluk yolu olarak yapılandırılmış varsayılan sağlayıcıya geri düşer. O sağlayıcı artık yapılandırılmış varsayılan modeli sunmuyorsa, bayat kaldırılmış-sağlayıcı varsayılanını göstermeden ilk yapılandırılmış sağlayıcı/modele geri düşer. Yine de `provider/model` değerini **açıkça** ayarlamalısınız.

  </Accordion>

  <Accordion title="Hangi modeli öneriyorsunuz?">
    **Önerilen varsayılan:** sağlayıcı yığınınızda mevcut en güçlü son nesil modeli kullanın.
    **Araç etkin veya güvenilmeyen girdili ajanlar için:** maliyetten çok model gücüne öncelik verin.
    **Rutin/düşük riskli sohbetler için:** daha ucuz fallback modeller kullanın ve ajan rolüne göre yönlendirin.

    MiniMax'ın kendi belgeleri vardır: [MiniMax](/tr/providers/minimax) ve
    [Yerel modeller](/tr/gateway/local-models).

    Genel kural: yüksek riskli işler için karşılayabildiğiniz **en iyi modeli** kullanın, rutin
    sohbet veya özetler için daha ucuz bir model kullanın. Modelleri ajan başına yönlendirebilir ve uzun görevleri
    paralelleştirmek için alt ajanlar kullanabilirsiniz (her alt ajan token tüketir). Bkz. [Modeller](/tr/concepts/models) ve
    [Alt ajanlar](/tr/tools/subagents).

    Güçlü uyarı: daha zayıf/aşırı nicemlenmiş modeller istem
    enjeksiyonu ve güvensiz davranışlara daha açıktır. Bkz. [Güvenlik](/tr/gateway/security).

    Daha fazla bağlam: [Modeller](/tr/concepts/models).

  </Accordion>

  <Accordion title="Yapılandırmamı silmeden modelleri nasıl değiştiririm?">
    **Model komutlarını** kullanın veya yalnızca **model** alanlarını düzenleyin. Tam yapılandırma değişimlerinden kaçının.

    Güvenli seçenekler:

    - sohbette `/model` (hızlı, oturum başına)
    - `openclaw models set ...` (yalnızca model yapılandırmasını günceller)
    - `openclaw configure --section model` (etkileşimli)
    - `~/.openclaw/openclaw.json` içinde `agents.defaults.model` düzenleme

    Tüm yapılandırmayı değiştirmek istemiyorsanız kısmi nesne ile `config.apply` kullanmaktan kaçının.
    RPC düzenlemeleri için önce `config.schema.lookup` ile inceleyin ve `config.patch` tercih edin. Lookup yükü, normalize edilmiş yolu, sığ şema belgelerini/kısıtlarını ve anlık alt özetleri verir.
    kısmi güncellemeler için.
    Yapılandırmayı üzerine yazdıysanız yedekten geri yükleyin veya onarım için `openclaw doctor` yeniden çalıştırın.

    Belgeler: [Modeller](/tr/concepts/models), [Yapılandır](/cli/configure), [Yapılandırma](/cli/config), [Doctor](/tr/gateway/doctor).

  </Accordion>

  <Accordion title="Kendi barındırdığım modelleri kullanabilir miyim (llama.cpp, vLLM, Ollama)?">
    Evet. Yerel modeller için en kolay yol Ollama'dır.

    En hızlı kurulum:

    1. `https://ollama.com/download` adresinden Ollama'yı kurun
    2. `ollama pull gemma4` gibi yerel bir model çekin
    3. Bulut modellerini de istiyorsanız `ollama signin` çalıştırın
    4. `openclaw onboard` çalıştırın ve `Ollama` seçin
    5. `Local` veya `Cloud + Local` seçin

    Notlar:

    - `Cloud + Local`, bulut modelleri ile yerel Ollama modellerinizi birlikte verir
    - `kimi-k2.5:cloud` gibi bulut modelleri yerel pull gerektirmez
    - elle geçiş için `openclaw models list` ve `openclaw models set ollama/<model>` kullanın

    Güvenlik notu: daha küçük veya yoğun nicemlenmiş modeller istem
    enjeksiyonuna daha açıktır. Araç kullanabilen herhangi bir bot için güçlü şekilde **büyük modeller**
    öneriyoruz. Yine de küçük modeller istiyorsanız sandboxing ve sıkı araç allowlist'leri etkinleştirin.

    Belgeler: [Ollama](/tr/providers/ollama), [Yerel modeller](/tr/gateway/local-models),
    [Model sağlayıcıları](/tr/concepts/model-providers), [Güvenlik](/tr/gateway/security),
    [Sandboxing](/tr/gateway/sandboxing).

  </Accordion>

  <Accordion title="OpenClaw, Flawd ve Krill modeller için ne kullanıyor?">
    - Bu dağıtımlar farklı olabilir ve zamanla değişebilir; sabit bir sağlayıcı önerisi yoktur.
    - Her gateway'deki mevcut çalışma zamanı ayarını `openclaw models status` ile kontrol edin.
    - Güvenlik açısından hassas/araç etkin ajanlar için mevcut en güçlü son nesil modeli kullanın.
  </Accordion>

  <Accordion title="Modelleri anında nasıl değiştiririm (yeniden başlatmadan)?">
    Tek başına mesaj olarak `/model` komutunu kullanın:

    ```
    /model sonnet
    /model opus
    /model gpt
    /model gpt-mini
    /model gemini
    /model gemini-flash
    /model gemini-flash-lite
    ```

    Bunlar yerleşik takma adlardır. Özel takma adlar `agents.defaults.models` üzerinden eklenebilir.

    Kullanılabilir modelleri `/model`, `/model list` veya `/model status` ile listeleyebilirsiniz.

    `/model` (ve `/model list`) kompakt, numaralı bir seçici gösterir. Numarayla seçin:

    ```
    /model 3
    ```

    Sağlayıcı için belirli bir auth profilini de zorlayabilirsiniz (oturum başına):

    ```
    /model opus@anthropic:default
    /model opus@anthropic:work
    ```

    İpucu: `/model status`, hangi ajanın etkin olduğunu, hangi `auth-profiles.json` dosyasının kullanıldığını ve hangi auth profilinin sırada deneneceğini gösterir.
    Ayrıca mevcutsa yapılandırılmış sağlayıcı uç noktasını (`baseUrl`) ve API kipini (`api`) de gösterir.

    **@profile ile ayarladığım profile pin'ini nasıl kaldırırım?**

    `@profile` soneki **olmadan** `/model` komutunu yeniden çalıştırın:

    ```
    /model anthropic/claude-opus-4-6
    ```

    Varsayılana dönmek istiyorsanız, onu `/model` içinden seçin (veya `/model <default provider/model>` gönderin).
    Hangi auth profilinin etkin olduğunu doğrulamak için `/model status` kullanın.

  </Accordion>

  <Accordion title="Günlük görevler için GPT 5.2 ve kodlama için Codex 5.3 kullanabilir miyim?">
    Evet. Birini varsayılan yapın, gerekince değiştirin:

    - **Hızlı geçiş (oturum başına):** günlük görevler için `/model gpt-5.4`, Codex OAuth ile kodlama için `/model openai-codex/gpt-5.4`.
    - **Varsayılan + geçiş:** `agents.defaults.model.primary` değerini `openai/gpt-5.4` yapın, sonra kodlama sırasında `openai-codex/gpt-5.4`'e geçin (veya tam tersi).
    - **Alt ajanlar:** kodlama görevlerini farklı varsayılan model kullanan alt ajanlara yönlendirin.

    Bkz. [Modeller](/tr/concepts/models) ve [Slash komutları](/tr/tools/slash-commands).

  </Accordion>

  <Accordion title="GPT 5.4 için fast mode nasıl yapılandırılır?">
    Oturum anahtarı veya yapılandırma varsayılanı kullanın:

    - **Oturum başına:** oturum `openai/gpt-5.4` veya `openai-codex/gpt-5.4` kullanırken `/fast on` gönderin.
    - **Model başına varsayılan:** `agents.defaults.models["openai/gpt-5.4"].params.fastMode` değerini `true` yapın