---
read_when:
    - Yaygın kurulum, yükleme, ilk kurulum veya çalışma zamanı destek sorularını yanıtlarken
    - Daha derin hata ayıklamadan önce kullanıcı tarafından bildirilen sorunları ön incelemeden geçirirken
summary: OpenClaw kurulumu, yapılandırması ve kullanımı hakkında sık sorulan sorular
title: SSS
x-i18n:
    generated_at: "2026-04-06T03:14:18Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4d6d09621c6033d580cbcf1ff46f81587d69404d6f64c8d8fd8c3f09185bb920
    source_path: help/faq.md
    workflow: 15
---

# SSS

Gerçek dünya kurulumları için hızlı yanıtlar ve daha derin sorun giderme (yerel geliştirme, VPS, çoklu temsilci, OAuth/API anahtarları, model devretme). Çalışma zamanı tanılaması için [Troubleshooting](/tr/gateway/troubleshooting) bölümüne bakın. Tam yapılandırma başvurusu için [Configuration](/tr/gateway/configuration) bölümüne bakın.

## Bir şey bozulduysa ilk 60 saniye

1. **Hızlı durum (ilk kontrol)**

   ```bash
   openclaw status
   ```

   Hızlı yerel özet: OS + güncelleme, gateway/service erişilebilirliği, temsilciler/oturumlar, sağlayıcı yapılandırması + çalışma zamanı sorunları (gateway erişilebilirse).

2. **Paylaşılabilir rapor (paylaşması güvenli)**

   ```bash
   openclaw status --all
   ```

   Günlük sonu ile salt okunur tanılama (token'lar sansürlenmiş).

3. **Daemon + port durumu**

   ```bash
   openclaw gateway status
   ```

   Denetleyici çalışma zamanı ile RPC erişilebilirliğini, yoklama hedef URL'sini ve hizmetin büyük olasılıkla hangi yapılandırmayı kullandığını gösterir.

4. **Derin yoklamalar**

   ```bash
   openclaw status --deep
   ```

   Desteklendiğinde kanal yoklamaları dahil canlı gateway sağlık yoklaması çalıştırır
   (erişilebilir bir gateway gerekir). Bkz. [Health](/tr/gateway/health).

5. **En son günlüğü izle**

   ```bash
   openclaw logs --follow
   ```

   RPC kapalıysa şuna dönün:

   ```bash
   tail -f "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)"
   ```

   Dosya günlükleri hizmet günlüklerinden ayrıdır; bkz. [Logging](/tr/logging) ve [Troubleshooting](/tr/gateway/troubleshooting).

6. **Doctor'u çalıştırın (onarımlar)**

   ```bash
   openclaw doctor
   ```

   Yapılandırmayı/durumu onarır veya taşır + sağlık denetimleri çalıştırır. Bkz. [Doctor](/tr/gateway/doctor).

7. **Gateway anlık görüntüsü**

   ```bash
   openclaw health --json
   openclaw health --verbose   # hatalarda hedef URL + yapılandırma yolunu gösterir
   ```

   Çalışan gateway'den tam anlık görüntü ister (yalnızca WS). Bkz. [Health](/tr/gateway/health).

## Hızlı başlangıç ve ilk çalıştırma kurulumu

<AccordionGroup>
  <Accordion title="Takıldım, takılmayı çözmenin en hızlı yolu nedir?">
    **Makinenizi görebilen** yerel bir AI temsilcisi kullanın. Bu, Discord'da sormaktan çok daha etkilidir;
    çünkü "takıldım" durumlarının çoğu, uzaktaki yardımcıların inceleyemeyeceği **yerel yapılandırma veya ortam sorunlarıdır**.

    - **Claude Code**: [https://www.anthropic.com/claude-code/](https://www.anthropic.com/claude-code/)
    - **OpenAI Codex**: [https://openai.com/codex/](https://openai.com/codex/)

    Bu araçlar depoyu okuyabilir, komut çalıştırabilir, günlükleri inceleyebilir ve makine düzeyindeki
    kurulumunuzu (PATH, hizmetler, izinler, kimlik doğrulama dosyaları) düzeltmenize yardımcı olabilir.
    Onlara hacklenebilir (git) yükleme üzerinden **tam kaynak ödeme** verin:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Bu, OpenClaw'ı **bir git checkout içinden** yükler; böylece temsilci kodu + belgeleri okuyabilir
    ve çalıştırdığınız tam sürüm üzerinde düşünebilir. Daha sonra yükleyiciyi `--install-method git`
    olmadan yeniden çalıştırarak her zaman kararlı sürüme dönebilirsiniz.

    İpucu: temsilciden düzeltmeyi **planlamasını ve denetlemesini** isteyin (adım adım), ardından yalnızca
    gerekli komutları yürütün. Bu, değişiklikleri küçük ve denetlenmesini kolay tutar.

    Gerçek bir hata veya düzeltme keşfederseniz lütfen bir GitHub sorunu açın veya PR gönderin:
    [https://github.com/openclaw/openclaw/issues](https://github.com/openclaw/openclaw/issues)
    [https://github.com/openclaw/openclaw/pulls](https://github.com/openclaw/openclaw/pulls)

    Şu komutlarla başlayın (yardım isterken çıktıları paylaşın):

    ```bash
    openclaw status
    openclaw models status
    openclaw doctor
    ```

    Ne yaptıkları:

    - `openclaw status`: gateway/temsilci sağlığı + temel yapılandırmanın hızlı anlık görüntüsü.
    - `openclaw models status`: sağlayıcı kimlik doğrulamasını + model kullanılabilirliğini kontrol eder.
    - `openclaw doctor`: yaygın yapılandırma/durum sorunlarını doğrular ve onarır.

    Diğer yararlı CLI denetimleri: `openclaw status --all`, `openclaw logs --follow`,
    `openclaw gateway status`, `openclaw health --verbose`.

    Hızlı hata ayıklama döngüsü: [Bir şey bozulduysa ilk 60 saniye](#bir-şey-bozulduysa-ilk-60-saniye).
    Kurulum belgeleri: [Install](/tr/install), [Installer flags](/tr/install/installer), [Updating](/tr/install/updating).

  </Accordion>

  <Accordion title="Heartbeat atlamaya devam ediyor. Atlama nedenleri ne anlama geliyor?">
    Yaygın heartbeat atlama nedenleri:

    - `quiet-hours`: yapılandırılmış etkin saatler penceresinin dışında
    - `empty-heartbeat-file`: `HEARTBEAT.md` var ama yalnızca boş/yalnızca başlık iskeleti içeriyor
    - `no-tasks-due`: `HEARTBEAT.md` görev modu etkin ama görev aralıklarının hiçbiri henüz zamanı gelmedi
    - `alerts-disabled`: tüm heartbeat görünürlüğü devre dışı (`showOk`, `showAlerts` ve `useIndicator` kapalı)

    Görev modunda, zamanı gelen zaman damgaları yalnızca gerçek bir heartbeat çalıştırması
    tamamlandıktan sonra ilerletilir. Atlanan çalıştırmalar görevleri tamamlandı olarak işaretlemez.

    Belgeler: [Heartbeat](/tr/gateway/heartbeat), [Automation & Tasks](/tr/automation).

  </Accordion>

  <Accordion title="OpenClaw yüklemek ve kurmak için önerilen yol">
    Depo, kaynaktan çalıştırmayı ve ilk kurulumu kullanmayı önerir:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash
    openclaw onboard --install-daemon
    ```

    Sihirbaz ayrıca UI varlıklarını otomatik olarak oluşturabilir. İlk kurulumdan sonra genellikle Gateway'i **18789** portunda çalıştırırsınız.

    Kaynaktan (katkıda bulunanlar/geliştiriciler):

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    pnpm ui:build # ilk çalıştırmada UI bağımlılıklarını otomatik yükler
    openclaw onboard
    ```

    Henüz genel kurulumunuz yoksa bunu `pnpm openclaw onboard` ile çalıştırın.

  </Accordion>

  <Accordion title="İlk kurulumdan sonra kontrol panelini nasıl açarım?">
    Sihirbaz, ilk kurulumdan hemen sonra tarayıcınızı temiz (token içermeyen) bir kontrol paneli URL'siyle açar ve bağlantıyı özette de yazdırır. Bu sekmeyi açık tutun; açılmadıysa yazdırılan URL'yi aynı makinede kopyalayıp yapıştırın.
  </Accordion>

  <Accordion title="Kontrol panelinde localhost ile uzak erişimde kimlik doğrulamayı nasıl yaparım?">
    **Localhost (aynı makine):**

    - `http://127.0.0.1:18789/` adresini açın.
    - Paylaşılan gizli kimlik doğrulaması isterse yapılandırılmış token'ı veya parolayı Control UI ayarlarına yapıştırın.
    - Token kaynağı: `gateway.auth.token` (veya `OPENCLAW_GATEWAY_TOKEN`).
    - Parola kaynağı: `gateway.auth.password` (veya `OPENCLAW_GATEWAY_PASSWORD`).
    - Henüz paylaşılan gizli yapılandırılmadıysa `openclaw doctor --generate-gateway-token` ile token oluşturun.

    **Localhost üzerinde değilse:**

    - **Tailscale Serve** (önerilen): bind'i loopback olarak tutun, `openclaw gateway --tailscale serve` çalıştırın, `https://<magicdns>/` adresini açın. `gateway.auth.allowTailscale` `true` ise kimlik başlıkları Control UI/WebSocket kimlik doğrulamasını karşılar (paylaşılan gizli yapıştırılmaz, güvenilir gateway ana bilgisayarını varsayar); HTTP API'leri ise özellikle private-ingress `none` veya trusted-proxy HTTP kimlik doğrulaması kullanmadığınız sürece yine de paylaşılan gizli kimlik doğrulaması ister.
      Aynı istemciden gelen hatalı eşzamanlı Serve kimlik doğrulama denemeleri, başarısız kimlik doğrulama sınırlayıcısı bunları kaydetmeden önce sıraya alınır; bu yüzden ikinci hatalı yeniden deneme zaten `retry later` gösterebilir.
    - **Tailnet bind**: `openclaw gateway --bind tailnet --token "<token>"` çalıştırın (veya parola kimlik doğrulaması yapılandırın), `http://<tailscale-ip>:18789/` adresini açın, ardından kontrol paneli ayarlarına eşleşen paylaşılan gizliyi yapıştırın.
    - **Kimlik farkındalıklı ters proxy**: Gateway'i loopback olmayan güvenilir bir ters proxy arkasında tutun, `gateway.auth.mode: "trusted-proxy"` yapılandırın, ardından proxy URL'sini açın.
    - **SSH tüneli**: `ssh -N -L 18789:127.0.0.1:18789 user@host`, sonra `http://127.0.0.1:18789/` adresini açın. Paylaşılan gizli kimlik doğrulaması tünel üzerinden de geçerlidir; istenirse yapılandırılmış token'ı veya parolayı yapıştırın.

    Bind kipleri ve kimlik doğrulama ayrıntıları için [Dashboard](/web/dashboard) ve [Web surfaces](/web) bölümlerine bakın.

  </Accordion>

  <Accordion title="Sohbet onayları için neden iki farklı exec onay yapılandırması var?">
    Bunlar farklı katmanları denetler:

    - `approvals.exec`: onay istemlerini sohbet hedeflerine iletir
    - `channels.<channel>.execApprovals`: o kanalın exec onayları için yerel bir onay istemcisi gibi davranmasını sağlar

    Ana bilgisayar exec ilkesi hâlâ gerçek onay geçididir. Sohbet yapılandırması yalnızca onay
    istemlerinin nerede görüneceğini ve insanların bunlara nasıl yanıt verebileceğini denetler.

    Çoğu kurulumda **ikisinin birden** gerekmez:

    - Sohbet zaten komutları ve yanıtları destekliyorsa, aynı sohbette `/approve` paylaşılan yol üzerinden çalışır.
    - Desteklenen bir yerel kanal onaylayıcıları güvenli biçimde çıkarabiliyorsa, OpenClaw artık `channels.<channel>.execApprovals.enabled` ayarlanmadığında veya `"auto"` olduğunda DM-first yerel onayları otomatik etkinleştirir.
    - Yerel onay kartları/düğmeleri mevcut olduğunda birincil yol bu yerel UI'dir; araç sonucu sohbet onaylarının kullanılamadığını veya tek yolun elle onay olduğunu söylemedikçe temsilci yalnızca elle `/approve` komutunu eklemelidir.
    - İstemlerin ayrıca başka sohbetlere veya açık operasyon odalarına iletilmesi gerekiyorsa yalnızca `approvals.exec` kullanın.
    - Onay istemlerinin özellikle kaynak oda/konuya geri gönderilmesini istiyorsanız yalnızca `channels.<channel>.execApprovals.target: "channel"` veya `"both"` kullanın.
    - Plugin onayları yine ayrıdır: varsayılan olarak aynı sohbette `/approve`, isteğe bağlı `approvals.plugin` iletimi kullanırlar ve yalnızca bazı yerel kanallar ek olarak yerel plugin onayı işleyişini korur.

    Kısa sürüm: iletme yönlendirme içindir, yerel istemci yapılandırması ise daha zengin kanala özgü UX içindir.
    Bkz. [Exec Approvals](/tr/tools/exec-approvals).

  </Accordion>

  <Accordion title="Hangi çalışma zamanına ihtiyacım var?">
    Node **>= 22** gerekir. `pnpm` önerilir. Bun, Gateway için **önerilmez**.
  </Accordion>

  <Accordion title="Raspberry Pi üzerinde çalışır mı?">
    Evet. Gateway hafiftir - belgelerde kişisel kullanım için **512MB-1GB RAM**, **1 çekirdek** ve yaklaşık **500MB**
    diskin yeterli olduğu yazılıdır ve **Raspberry Pi 4 üzerinde çalışabileceği** belirtilir.

    Biraz daha boş alan istiyorsanız (günlükler, medya, diğer hizmetler) **2GB önerilir**, ancak
    bu katı bir alt sınır değildir.

    İpucu: küçük bir Pi/VPS Gateway'i barındırabilir ve yerel ekran/kamera/canvas veya komut yürütme için
    dizüstü bilgisayarınızda/telefonunuzda **node** eşleyebilirsiniz. Bkz. [Nodes](/tr/nodes).

  </Accordion>

  <Accordion title="Raspberry Pi kurulumları için ipuçları var mı?">
    Kısa sürüm: çalışır, ancak pürüzler bekleyin.

    - **64-bit** bir OS kullanın ve Node >= 22 tutun.
    - Günlükleri görebilmek ve hızlı güncellemek için **hacklenebilir (git) kurulumu** tercih edin.
    - Kanal/Skills olmadan başlayın, sonra bunları tek tek ekleyin.
    - Garip ikili sorunlarla karşılaşırsanız bu genellikle bir **ARM uyumluluk** sorunudur.

    Belgeler: [Linux](/tr/platforms/linux), [Install](/tr/install).

  </Accordion>

  <Accordion title="Wake up my friend ekranında takılı kaldı / ilk kurulum ilerlemiyor. Şimdi ne yapmalıyım?">
    Bu ekran, Gateway'in erişilebilir ve kimliği doğrulanmış olmasına bağlıdır. TUI ayrıca
    ilk açılışta otomatik olarak "Wake up, my friend!" gönderir. Bu satırı **yanıt olmadan**
    görüyorsanız ve token'lar 0'da kalıyorsa, temsilci hiç çalışmamış demektir.

    1. Gateway'i yeniden başlatın:

    ```bash
    openclaw gateway restart
    ```

    2. Durum + kimlik doğrulamasını kontrol edin:

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    3. Hâlâ takılıyorsa şunu çalıştırın:

    ```bash
    openclaw doctor
    ```

    Gateway uzaktaysa tünelin/Tailscale bağlantısının açık olduğundan ve UI'ın
    doğru Gateway'e işaret ettiğinden emin olun. Bkz. [Remote access](/tr/gateway/remote).

  </Accordion>

  <Accordion title="Kurulumumu yeni bir makineye (Mac mini) yeniden ilk kurulum yapmadan taşıyabilir miyim?">
    Evet. **Durum dizinini** ve **çalışma alanını** kopyalayın, ardından Doctor'u bir kez çalıştırın. Bu,
    **her iki** konumu da kopyaladığınız sürece botunuzu "aynı şekilde" (bellek, oturum geçmişi, kimlik doğrulama ve kanal
    durumu) korur:

    1. Yeni makineye OpenClaw yükleyin.
    2. Eski makineden `$OPENCLAW_STATE_DIR` dizinini (varsayılan: `~/.openclaw`) kopyalayın.
    3. Çalışma alanınızı kopyalayın (varsayılan: `~/.openclaw/workspace`).
    4. `openclaw doctor` çalıştırın ve Gateway hizmetini yeniden başlatın.

    Bu, yapılandırmayı, kimlik doğrulama profillerini, WhatsApp kimlik bilgilerini, oturumları ve belleği korur. Eğer
    uzak kipteyseniz, gateway ana bilgisayarının oturum deposu ve çalışma alanına sahip olduğunu unutmayın.

    **Önemli:** yalnızca çalışma alanınızı GitHub'a commit/push ederseniz,
    **bellek + önyükleme dosyalarını** yedeklemiş olursunuz, ancak **oturum geçmişini veya kimlik doğrulamayı**
    yedeklemiş olmazsınız. Bunlar `~/.openclaw/` altında yaşar (örneğin `~/.openclaw/agents/<agentId>/sessions/`).

    İlgili: [Migrating](/tr/install/migrating), [Where things live on disk](#where-things-live-on-disk),
    [Agent workspace](/tr/concepts/agent-workspace), [Doctor](/tr/gateway/doctor),
    [Remote mode](/tr/gateway/remote).

  </Accordion>

  <Accordion title="En son sürümde nelerin yeni olduğunu nerede görürüm?">
    GitHub değişiklik günlüğünü kontrol edin:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    En yeni girdiler üsttedir. Üst bölüm **Unreleased** olarak işaretliyse, bir sonraki tarihli
    bölüm en son yayımlanmış sürümdür. Girdiler **Highlights**, **Changes** ve
    **Fixes** olarak gruplanır (gerektiğinde belgeler/diğer bölümler ile birlikte).

  </Accordion>

  <Accordion title="docs.openclaw.ai erişilemiyor (SSL hatası)">
    Bazı Comcast/Xfinity bağlantıları `docs.openclaw.ai` alanını Xfinity
    Advanced Security ile yanlış şekilde engeller. Bunu devre dışı bırakın veya `docs.openclaw.ai` alanını izin listesine alın, sonra yeniden deneyin.
    Lütfen engelin kaldırılmasına yardımcı olmak için şurada bildirin: [https://spa.xfinity.com/check_url_status](https://spa.xfinity.com/check_url_status).

    Siteye hâlâ ulaşamıyorsanız, belgeler GitHub üzerinde de aynalanır:
    [https://github.com/openclaw/openclaw/tree/main/docs](https://github.com/openclaw/openclaw/tree/main/docs)

  </Accordion>

  <Accordion title="Kararlı ile beta arasındaki fark">
    **Kararlı** ve **beta**, ayrı kod hatları değil, **npm dist-tag**'leridir:

    - `latest` = kararlı
    - `beta` = test için erken derleme

    Genellikle bir kararlı sürüm önce **beta** üzerine gelir, sonra açık bir
    yükseltme adımı aynı sürümü `latest`'e taşır. Bakımcılar gerektiğinde
    doğrudan `latest`'e de yayımlayabilir. Bu nedenle yükseltmeden sonra beta ve kararlı
    **aynı sürüme** işaret edebilir.

    Neyin değiştiğini görün:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    Tek satırlık kurulum komutları ve beta ile dev arasındaki fark için aşağıdaki akordeona bakın.

  </Accordion>

  <Accordion title="Beta sürümünü nasıl yüklerim ve beta ile dev arasındaki fark nedir?">
    **Beta**, npm dist-tag `beta`'dır (`latest` ile yükseltmeden sonra eşleşebilir).
    **Dev**, `main`'in hareketli başıdır (git); yayımlandığında npm dist-tag `dev` kullanılır.

    Tek satırlık komutlar (macOS/Linux):

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --beta
    ```

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Windows yükleyicisi (PowerShell):
    [https://openclaw.ai/install.ps1](https://openclaw.ai/install.ps1)

    Daha fazla ayrıntı: [Development channels](/tr/install/development-channels) ve [Installer flags](/tr/install/installer).

  </Accordion>

  <Accordion title="En son parçaları nasıl denerim?">
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

    Bu size düzenleyebileceğiniz yerel bir repo verir, ardından git ile güncelleyebilirsiniz.

    Temiz bir clone'u elle tercih ediyorsanız şunu kullanın:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    ```

    Belgeler: [Update](/cli/update), [Development channels](/tr/install/development-channels),
    [Install](/tr/install).

  </Accordion>

  <Accordion title="Kurulum ve ilk kurulum genelde ne kadar sürer?">
    Kabaca kılavuz:

    - **Kurulum:** 2-5 dakika
    - **İlk kurulum:** yapılandırdığınız kanal/model sayısına bağlı olarak 5-15 dakika

    Takılırsa [Installer stuck](#quick-start-and-first-run-setup)
    ve [I am stuck](#quick-start-and-first-run-setup) içindeki hızlı hata ayıklama döngüsünü kullanın.

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
    # install.ps1 için henüz özel bir -Verbose bayrağı yok.
    Set-PSDebug -Trace 1
    & ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -NoOnboard
    Set-PSDebug -Trace 0
    ```

    Daha fazla seçenek: [Installer flags](/tr/install/installer).

  </Accordion>

  <Accordion title="Windows kurulumu git bulunamadı veya openclaw tanınmıyor diyor">
    İki yaygın Windows sorunu:

    **1) npm error spawn git / git not found**

    - **Git for Windows** yükleyin ve `git` komutunun PATH üzerinde olduğundan emin olun.
    - PowerShell'i kapatıp yeniden açın, sonra yükleyiciyi yeniden çalıştırın.

    **2) Kurulumdan sonra openclaw tanınmıyor**

    - npm global bin klasörünüz PATH üzerinde değil.
    - Yolu kontrol edin:

      ```powershell
      npm config get prefix
      ```

    - Bu dizini kullanıcı PATH'inize ekleyin (Windows'ta `\bin` son eki gerekmez; çoğu sistemde `%AppData%\npm` olur).
    - PATH güncellendikten sonra PowerShell'i kapatıp yeniden açın.

    En sorunsuz Windows kurulumu için yerel Windows yerine **WSL2** kullanın.
    Belgeler: [Windows](/tr/platforms/windows).

  </Accordion>

  <Accordion title="Windows exec çıktısı bozuk Çince metin gösteriyor - ne yapmalıyım?">
    Bu genellikle yerel Windows kabuklarında konsol kod sayfası uyuşmazlığıdır.

    Belirtiler:

    - `system.run`/`exec` çıktısı Çinceyi bozuk gösterir
    - Aynı komut başka bir terminal profilinde düzgün görünür

    PowerShell'de hızlı geçici çözüm:

    ```powershell
    chcp 65001
    [Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    ```

    Sonra Gateway'i yeniden başlatın ve komutunuzu yeniden deneyin:

    ```powershell
    openclaw gateway restart
    ```

    Bunu en son OpenClaw sürümünde hâlâ yeniden üretebiliyorsanız burada izleyin/bildirin:

    - [Issue #30640](https://github.com/openclaw/openclaw/issues/30640)

  </Accordion>

  <Accordion title="Belgeler soruma yanıt vermedi - daha iyi bir yanıtı nasıl alırım?">
    Tam kaynak ve belgelerin yerelde olması için **hacklenebilir (git) kurulumu** kullanın, ardından
    botunuza (veya Claude/Codex'e) _o klasörden_ sorun ki depoyu okuyup tam yanıt verebilsin.

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Daha fazla ayrıntı: [Install](/tr/install) ve [Installer flags](/tr/install/installer).

  </Accordion>

  <Accordion title="OpenClaw'ı Linux'a nasıl kurarım?">
    Kısa yanıt: Linux rehberini izleyin, sonra ilk kurulumu çalıştırın.

    - Linux hızlı yol + hizmet kurulumu: [Linux](/tr/platforms/linux).
    - Tam adım adım rehber: [Getting Started](/tr/start/getting-started).
    - Kurulum + güncellemeler: [Install & updates](/tr/install/updating).

  </Accordion>

  <Accordion title="OpenClaw'ı bir VPS'e nasıl kurarım?">
    Herhangi bir Linux VPS çalışır. Sunucuya yükleyin, sonra Gateway'e erişmek için SSH/Tailscale kullanın.

    Rehberler: [exe.dev](/tr/install/exe-dev), [Hetzner](/tr/install/hetzner), [Fly.io](/tr/install/fly).
    Uzak erişim: [Gateway remote](/tr/gateway/remote).

  </Accordion>

  <Accordion title="Bulut/VPS kurulum rehberleri nerede?">
    Yaygın sağlayıcılar için bir **barındırma merkezi** tutuyoruz. Birini seçin ve rehberi izleyin:

    - [VPS hosting](/tr/vps) (tüm sağlayıcılar tek yerde)
    - [Fly.io](/tr/install/fly)
    - [Hetzner](/tr/install/hetzner)
    - [exe.dev](/tr/install/exe-dev)

    Bulutta nasıl çalışır: **Gateway sunucuda çalışır**, siz de ona
    dizüstü bilgisayarınız/telefonunuzdan Control UI (veya Tailscale/SSH) ile erişirsiniz. Durumunuz + çalışma alanınız
    sunucuda yaşar; bu yüzden ana bilgisayarı doğruluk kaynağı olarak kabul edin ve yedekleyin.

    Yerel ekran/kamera/canvas erişimi için veya dizüstü bilgisayarınızda komut çalıştırmak için
    bulut Gateway'e **node** (Mac/iOS/Android/headless) eşleyebilirsiniz; böylece
    Gateway bulutta kalır.

    Merkez: [Platforms](/tr/platforms). Uzak erişim: [Gateway remote](/tr/gateway/remote).
    Nodes: [Nodes](/tr/nodes), [Nodes CLI](/cli/nodes).

  </Accordion>

  <Accordion title="OpenClaw'dan kendini güncellemesini isteyebilir miyim?">
    Kısa yanıt: **mümkün, önerilmez**. Güncelleme akışı
    Gateway'i yeniden başlatabilir (etkin oturumu düşürür), temiz bir git checkout gerektirebilir ve
    onay isteyebilir. Daha güvenlisi: güncellemeleri operatör olarak bir kabuktan çalıştırın.

    CLI kullanın:

    ```bash
    openclaw update
    openclaw update status
    openclaw update --channel stable|beta|dev
    openclaw update --tag <dist-tag|version>
    openclaw update --no-restart
    ```

    Bir temsilciden otomatikleştirmeniz gerekiyorsa:

    ```bash
    openclaw update --yes --no-restart
    openclaw gateway restart
    ```

    Belgeler: [Update](/cli/update), [Updating](/tr/install/updating).

  </Accordion>

  <Accordion title="İlk kurulum gerçekte ne yapar?">
    `openclaw onboard` önerilen kurulum yoludur. **Yerel kipte** size şunlarda rehberlik eder:

    - **Model/kimlik doğrulama kurulumu** (sağlayıcı OAuth, API anahtarları, Anthropic eski setup-token, ayrıca LM Studio gibi yerel model seçenekleri)
    - **Çalışma alanı** konumu + önyükleme dosyaları
    - **Gateway ayarları** (bind/port/auth/tailscale)
    - **Kanallar** (WhatsApp, Telegram, Discord, Mattermost, Signal, iMessage, ayrıca QQ Bot gibi paketlenmiş kanal plugin'leri)
    - **Daemon kurulumu** (macOS'ta LaunchAgent; Linux/WSL2'de systemd user unit)
    - **Sağlık denetimleri** ve **Skills** seçimi

    Ayrıca yapılandırılmış modeliniz bilinmiyorsa veya kimlik doğrulaması eksikse uyarır.

  </Accordion>

  <Accordion title="Bunu çalıştırmak için Claude veya OpenAI aboneliğine ihtiyacım var mı?">
    Hayır. OpenClaw'ı **API anahtarları** (Anthropic/OpenAI/diğerleri) veya
    verilerinizin cihazınızda kalmasını sağlayan **yalnızca yerel modeller** ile çalıştırabilirsiniz. Abonelikler (Claude
    Pro/Max veya OpenAI Codex), bu sağlayıcılarda kimlik doğrulamanın isteğe bağlı yollarıdır.

    Anthropic için OpenClaw içindeki pratik ayrım şudur:

    - **Anthropic API anahtarı**: normal Anthropic API faturalandırması
    - **OpenClaw içinde Claude abonelik kimlik doğrulaması**: Anthropic, OpenClaw kullanıcılarına
      **4 Nisan 2026 saat 12:00 PT / 20:00 BST** tarihinde bunun
      abonelikten ayrı faturalandırılan **Ek Kullanım** gerektirdiğini bildirdi

    Yerel yeniden üretimlerimiz ayrıca `claude -p --append-system-prompt ...` komutunun,
    eklenen istem OpenClaw'ı tanımladığında aynı Ek Kullanım korumasına
    takılabildiğini; aynı istem dizgesinin ise
    Anthropic SDK + API-anahtarı yolunda bu engeli **yeniden üretmediğini** gösteriyor. OpenAI Codex OAuth,
    OpenClaw gibi harici araçlar için açıkça
    desteklenmektedir.

    OpenClaw ayrıca şu diğer barındırılan abonelik tarzı seçenekleri de destekler:
    **Qwen Cloud Coding Plan**, **MiniMax Coding Plan** ve
    **Z.AI / GLM Coding Plan**.

    Belgeler: [Anthropic](/tr/providers/anthropic), [OpenAI](/tr/providers/openai),
    [Qwen Cloud](/tr/providers/qwen),
    [MiniMax](/tr/providers/minimax), [GLM Models](/tr/providers/glm),
    [Local models](/tr/gateway/local-models), [Models](/tr/concepts/models).

  </Accordion>

  <Accordion title="API anahtarı olmadan Claude Max aboneliğini kullanabilir miyim?">
    Evet, ancak buna **Ek Kullanımlı Claude abonelik kimlik doğrulaması** olarak yaklaşın.

    Claude Pro/Max abonelikleri API anahtarı içermez. OpenClaw içinde bu,
    Anthropic'in OpenClaw'a özel faturalandırma bildirisinin geçerli olduğu anlamına gelir: abonelik
    trafiği **Ek Kullanım** gerektirir. Anthropic trafiğini bu Ek Kullanım
    yolu olmadan istiyorsanız bunun yerine bir Anthropic API anahtarı kullanın.

  </Accordion>

  <Accordion title="Claude abonelik kimlik doğrulamasını destekliyor musunuz (Claude Pro veya Max)?">
    Evet, ancak desteklenen yorum artık şöyledir:

    - Abonelik ile OpenClaw içinde Anthropic = **Ek Kullanım**
    - Bu yol olmadan OpenClaw içinde Anthropic = **API anahtarı**

    Anthropic setup-token hâlâ eski/elle kullanılan bir OpenClaw yolu olarak mevcuttur
    ve Anthropic'in OpenClaw'a özel faturalandırma bildirimi orada da geçerlidir. Ayrıca
    eklenen istem OpenClaw'ı tanımladığında doğrudan
    `claude -p --append-system-prompt ...` kullanımında aynı faturalandırma korumasını yerelde yeniden ürettik;
    aynı istem dizgesi
    Anthropic SDK + API-anahtarı yolunda ise **yeniden üretilmedi**.

    Üretim veya çok kullanıcılı iş yükleri için Anthropic API anahtarı kimlik doğrulaması
    daha güvenli, önerilen seçimdir. OpenClaw içinde diğer abonelik tarzı barındırılan
    seçenekleri istiyorsanız [OpenAI](/tr/providers/openai), [Qwen / Model
    Cloud](/tr/providers/qwen), [MiniMax](/tr/providers/minimax) ve
    [GLM Models](/tr/providers/glm) bölümlerine bakın.

  </Accordion>

<a id="why-am-i-seeing-http-429-ratelimiterror-from-anthropic"></a>
<Accordion title="Anthropic'ten neden HTTP 429 rate_limit_error görüyorum?">
Bu, mevcut pencere için **Anthropic kotanızın/hız sınırınızın** tükendiği anlamına gelir. **Claude CLI**
kullanıyorsanız pencerenin sıfırlanmasını bekleyin veya planınızı yükseltin. Bir
**Anthropic API anahtarı** kullanıyorsanız Anthropic Console
üzerinden kullanım/faturalandırmayı kontrol edin ve gerektiğinde limitleri artırın.

    Mesaj özellikle şu ise:
    `Extra usage is required for long context requests`, istek
    Anthropic'in 1M bağlam betasını (`context1m: true`) kullanmaya çalışıyordur. Bu yalnızca
    kimlik bilginiz uzun bağlam faturalandırmasına uygunsa çalışır (API anahtarı faturalandırması veya
    Ek Kullanım etkin OpenClaw Claude-login yolu).

    İpucu: bir sağlayıcı hız sınırına takıldığında OpenClaw'ın yanıt vermeye devam edebilmesi için
    bir **yedek model** ayarlayın.
    Bkz. [Models](/cli/models), [OAuth](/tr/concepts/oauth) ve
    [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/tr/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context).

  </Accordion>

  <Accordion title="AWS Bedrock destekleniyor mu?">
    Evet. OpenClaw paketlenmiş bir **Amazon Bedrock (Converse)** sağlayıcısına sahiptir. AWS ortam işaretçileri varsa OpenClaw, akış/metin Bedrock kataloğunu otomatik keşfedip bunu örtük bir `amazon-bedrock` sağlayıcısı olarak birleştirebilir; aksi halde `plugins.entries.amazon-bedrock.config.discovery.enabled` ayarını açıkça etkinleştirebilir veya elle bir sağlayıcı girdisi ekleyebilirsiniz. Bkz. [Amazon Bedrock](/tr/providers/bedrock) ve [Model providers](/tr/providers/models). Yönetilen anahtar akışını tercih ediyorsanız Bedrock önünde OpenAI uyumlu bir proxy kullanmak da geçerli bir seçenektir.
  </Accordion>

  <Accordion title="Codex kimlik doğrulaması nasıl çalışır?">
    OpenClaw, OAuth (ChatGPT oturum açma) üzerinden **OpenAI Code (Codex)** destekler. İlk kurulum OAuth akışını çalıştırabilir ve uygun olduğunda varsayılan modeli `openai-codex/gpt-5.4` olarak ayarlar. Bkz. [Model providers](/tr/concepts/model-providers) ve [Onboarding (CLI)](/tr/start/wizard).
  </Accordion>

  <Accordion title="OpenAI abonelik kimlik doğrulamasını destekliyor musunuz (Codex OAuth)?">
    Evet. OpenClaw, **OpenAI Code (Codex) abonelik OAuth**'u tam olarak destekler.
    OpenAI, OpenClaw gibi harici araçlar/iş akışlarında
    abonelik OAuth kullanımına açıkça izin verir. İlk kurulum sizin için OAuth akışını çalıştırabilir.

    Bkz. [OAuth](/tr/concepts/oauth), [Model providers](/tr/concepts/model-providers) ve [Onboarding (CLI)](/tr/start/wizard).

  </Accordion>

  <Accordion title="Gemini CLI OAuth'u nasıl kurarım?">
    Gemini CLI, `openclaw.json` içinde istemci kimliği veya gizli yerine
    bir **plugin kimlik doğrulama akışı** kullanır.

    Bunun yerine Gemini API sağlayıcısını kullanın:

    1. Plugin'i etkinleştirin: `openclaw plugins enable google`
    2. `openclaw onboard --auth-choice gemini-api-key` çalıştırın
    3. `google/gemini-3.1-pro-preview` gibi bir Google modeli ayarlayın

  </Accordion>

  <Accordion title="Gündelik sohbetler için yerel model uygun mu?">
    Genellikle hayır. OpenClaw büyük bağlam + güçlü güvenlik gerektirir; küçük kartlar keser ve sızdırır. Mecbur kalırsanız yerelde çalıştırabildiğiniz **en büyük** model derlemesini (LM Studio) çalıştırın ve [/gateway/local-models](/tr/gateway/local-models) bölümüne bakın. Daha küçük/kuantize modeller istem enjeksiyonu riskini artırır - bkz. [Security](/tr/gateway/security).
  </Accordion>

  <Accordion title="Barındırılan model trafiğini belirli bir bölgede nasıl tutarım?">
    Bölgeye sabitlenmiş uç noktalar seçin. OpenRouter, MiniMax, Kimi ve GLM için ABD barındırmalı seçenekler sunar; veriyi bölgede tutmak için ABD barındırmalı varyantı seçin. Bunların yanında yine de Anthropic/OpenAI listeleyebilirsiniz; bunun için `models.mode: "merge"` kullanın, böylece seçtiğiniz bölgelendirilmiş sağlayıcıya saygı gösterirken yedekler kullanılabilir kalır.
  </Accordion>

  <Accordion title="Bunu yüklemek için bir Mac Mini satın almam gerekiyor mu?">
    Hayır. OpenClaw macOS veya Linux üzerinde çalışır (Windows, WSL2 üzerinden). Mac mini isteğe bağlıdır - bazı kişiler
    her zaman açık bir ana bilgisayar olarak bir tane alır, ancak küçük bir VPS, ev sunucusu veya Raspberry Pi sınıfı bir kutu da çalışır.

    Mac'e yalnızca **yalnızca macOS araçları** için ihtiyacınız vardır. iMessage için [BlueBubbles](/tr/channels/bluebubbles) kullanın (önerilen) - BlueBubbles sunucusu herhangi bir Mac'te çalışır ve Gateway Linux veya başka bir yerde çalışabilir. Başka yalnızca macOS araçları istiyorsanız Gateway'i Mac üzerinde çalıştırın veya bir macOS node eşleyin.

    Belgeler: [BlueBubbles](/tr/channels/bluebubbles), [Nodes](/tr/nodes), [Mac remote mode](/tr/platforms/mac/remote).

  </Accordion>

  <Accordion title="iMessage desteği için Mac mini gerekir mi?">
    Messages'a giriş yapmış **bir macOS cihazına** ihtiyacınız var. Bunun Mac mini olması **gerekmez** -
    herhangi bir Mac olur. iMessage için **[BlueBubbles](/tr/channels/bluebubbles)** kullanın (önerilen) - BlueBubbles sunucusu macOS üzerinde çalışır, Gateway ise Linux veya başka bir yerde çalışabilir.

    Yaygın kurulumlar:

    - Gateway'i Linux/VPS üzerinde çalıştırın ve BlueBubbles sunucusunu Messages'a giriş yapmış herhangi bir Mac üzerinde çalıştırın.
    - En basit tek makine kurulumu istiyorsanız her şeyi Mac üzerinde çalıştırın.

    Belgeler: [BlueBubbles](/tr/channels/bluebubbles), [Nodes](/tr/nodes),
    [Mac remote mode](/tr/platforms/mac/remote).

  </Accordion>

  <Accordion title="OpenClaw çalıştırmak için bir Mac mini alırsam onu MacBook Pro'ma bağlayabilir miyim?">
    Evet. **Mac mini Gateway'i çalıştırabilir**, MacBook Pro'nuz ise bir
    **node** (yardımcı cihaz) olarak bağlanabilir. Node'lar Gateway'i çalıştırmaz -
    o cihazda ekran/kamera/canvas ve `system.run` gibi ek
    yetenekler sağlarlar.

    Yaygın desen:

    - Gateway Mac mini üzerinde (her zaman açık).
    - MacBook Pro macOS uygulamasını veya node ana bilgisayarını çalıştırır ve Gateway ile eşleşir.
    - Görmek için `openclaw nodes status` / `openclaw nodes list` kullanın.

    Belgeler: [Nodes](/tr/nodes), [Nodes CLI](/cli/nodes).

  </Accordion>

  <Accordion title="Bun kullanabilir miyim?">
    Bun **önerilmez**. Özellikle WhatsApp ve Telegram ile çalışma zamanı hataları görüyoruz.
    Kararlı gateway'ler için **Node** kullanın.

    Bun ile yine de denemek isterseniz bunu WhatsApp/Telegram olmayan
    üretim dışı bir gateway üzerinde yapın.

  </Accordion>

  <Accordion title="Telegram: allowFrom içine ne girer?">
    `channels.telegram.allowFrom`, **insan gönderenin Telegram kullanıcı kimliğidir** (sayısal). Bot kullanıcı adı değildir.

    İlk kurulum `@username` girdisini kabul eder ve bunu sayısal kimliğe çözer, ancak OpenClaw yetkilendirmesi yalnızca sayısal kimlikleri kullanır.

    Daha güvenli (üçüncü taraf bot olmadan):

    - Botunuza DM gönderin, sonra `openclaw logs --follow` çalıştırıp `from.id` değerini okuyun.

    Resmî Bot API:

    - Botunuza DM gönderin, sonra `https://api.telegram.org/bot<bot_token>/getUpdates` çağırıp `message.from.id` değerini okuyun.

    Üçüncü taraf (daha az özel):

    - `@userinfobot` veya `@getidsbot`'a DM gönderin.

    Bkz. [/channels/telegram](/tr/channels/telegram#access-control-and-activation).

  </Accordion>

  <Accordion title="Birden fazla kişi farklı OpenClaw örnekleriyle tek bir WhatsApp numarasını kullanabilir mi?">
    Evet, **çoklu temsilci yönlendirme** ile. Her gönderenin WhatsApp **DM**'ini (eş `kind: "direct"`, gönderen E.164 ör. `+15551234567`) farklı bir `agentId`'ye bağlayın; böylece herkes kendi çalışma alanını ve oturum deposunu alır. Yanıtlar yine **aynı WhatsApp hesabından** gelir ve DM erişim denetimi (`channels.whatsapp.dmPolicy` / `channels.whatsapp.allowFrom`) WhatsApp hesabı başına geneldir. Bkz. [Multi-Agent Routing](/tr/concepts/multi-agent) ve [WhatsApp](/tr/channels/whatsapp).
  </Accordion>

  <Accordion title='Bir "hızlı sohbet" temsilcisi ve bir "kodlama için Opus" temsilcisi çalıştırabilir miyim?'>
    Evet. Çoklu temsilci yönlendirmesi kullanın: her temsilciye kendi varsayılan modelini verin, sonra gelen rotaları (sağlayıcı hesabı veya belirli eşler) her temsilciye bağlayın. Örnek yapılandırma [Multi-Agent Routing](/tr/concepts/multi-agent) içinde bulunur. Ayrıca [Models](/tr/concepts/models) ve [Configuration](/tr/gateway/configuration) bölümlerine de bakın.
  </Accordion>

  <Accordion title="Homebrew Linux'ta çalışır mı?">
    Evet. Homebrew Linux'u (Linuxbrew) destekler. Hızlı kurulum:

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew install <formula>
    ```

    OpenClaw'ı systemd ile çalıştırıyorsanız, hizmet PATH'inin `/home/linuxbrew/.linuxbrew/bin` (veya brew önekinizi) içerdiğinden emin olun ki `brew` ile yüklenen araçlar girişsiz kabuklarda çözülebilsin.
    Son derlemeler ayrıca Linux systemd hizmetlerinde yaygın kullanıcı bin dizinlerini öne ekler (örneğin `~/.local/bin`, `~/.npm-global/bin`, `~/.local/share/pnpm`, `~/.bun/bin`) ve ayarlı olduğunda `PNPM_HOME`, `NPM_CONFIG_PREFIX`, `BUN_INSTALL`, `VOLTA_HOME`, `ASDF_DATA_DIR`, `NVM_DIR` ve `FNM_DIR` değerlerine saygı gösterir.

  </Accordion>

  <Accordion title="Hacklenebilir git kurulumu ile npm install arasındaki fark">
    - **Hacklenebilir (git) kurulum:** tam kaynak checkout, düzenlenebilir, katkıda bulunanlar için en iyisi.
      Derlemeleri yerelde çalıştırır ve kodu/belgeleri yamalayabilirsiniz.
    - **npm install:** genel CLI kurulumu, repo yok, "sadece çalıştır" için en iyisi.
      Güncellemeler npm dist-tag'lerden gelir.

    Belgeler: [Getting started](/tr/start/getting-started), [Updating](/tr/install/updating).

  </Accordion>

  <Accordion title="Daha sonra npm ve git kurulumları arasında geçiş yapabilir miyim?">
    Evet. Diğer çeşidi yükleyin, sonra gateway hizmeti yeni giriş noktasını kullansın diye Doctor'u çalıştırın.
    Bu **verilerinizi silmez** - yalnızca OpenClaw kod kurulumunu değiştirir. Durumunuz
    (`~/.openclaw`) ve çalışma alanınız (`~/.openclaw/workspace`) olduğu gibi kalır.

    npm'den git'e:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    openclaw doctor
    openclaw gateway restart
    ```

    git'ten npm'ye:

    ```bash
    npm install -g openclaw@latest
    openclaw doctor
    openclaw gateway restart
    ```

    Doctor, gateway hizmeti giriş noktası uyuşmazlığını algılar ve hizmet yapılandırmasını mevcut kurulumla eşleşecek şekilde yeniden yazmayı önerir (otomasyonda `--repair` kullanın).

    Yedekleme ipuçları: bkz. [Backup strategy](#where-things-live-on-disk).

  </Accordion>

  <Accordion title="Gateway'i dizüstü bilgisayarımda mı yoksa bir VPS'te mi çalıştırmalıyım?">
    Kısa yanıt: **7/24 güvenilirlik istiyorsanız bir VPS kullanın**. En düşük
    sürtünmeyi istiyorsanız ve uyku/yeniden başlatmalar sorun değilse yerelde çalıştırın.

    **Dizüstü bilgisayar (yerel Gateway)**

    - **Artıları:** sunucu maliyeti yok, yerel dosyalara doğrudan erişim, görünür tarayıcı penceresi.
    - **Eksileri:** uyku/ağ düşüşleri = kopmalar, OS güncellemeleri/yeniden başlatmalar kesintiye uğratır, uyanık kalmalıdır.

    **VPS / bulut**

    - **Artıları:** her zaman açık, kararlı ağ, dizüstü uyku sorunları yok, çalışır durumda tutmak daha kolay.
    - **Eksileri:** genellikle headless çalışır (ekran görüntüsü kullanın), yalnızca uzak dosya erişimi, güncellemeler için SSH gerekir.

    **OpenClaw'a özgü not:** WhatsApp/Telegram/Slack/Mattermost/Discord bir VPS üzerinden gayet iyi çalışır. Tek gerçek ödünleşim **headless tarayıcı** ile görünür pencere arasındadır. Bkz. [Browser](/tr/tools/browser).

    **Önerilen varsayılan:** daha önce gateway bağlantı kopmaları yaşadıysanız VPS. Mac'i aktif kullanırken ve yerel dosya erişimi veya görünür tarayıcıyla UI otomasyonu istediğinizde yerel kullanım harikadır.

  </Accordion>

  <Accordion title="OpenClaw'ı özel bir makinede çalıştırmak ne kadar önemli?">
    Gerekli değil, ancak **güvenilirlik ve yalıtım için önerilir**.

    - **Özel ana bilgisayar (VPS/Mac mini/Pi):** her zaman açık, daha az uyku/yeniden başlatma kesintisi, daha temiz izinler, çalışır durumda tutması daha kolay.
    - **Paylaşılan dizüstü/masaüstü:** test ve aktif kullanım için tamamen uygundur, ancak makine uyuduğunda veya güncellendiğinde duraklamalar bekleyin.

    İkisinin en iyisini istiyorsanız Gateway'i özel bir ana bilgisayarda tutun ve yerel ekran/kamera/exec araçları için dizüstü bilgisayarınızı **node** olarak eşleyin. Bkz. [Nodes](/tr/nodes).
    Güvenlik rehberi için [Security](/tr/gateway/security) okuyun.

  </Accordion>

  <Accordion title="Minimum VPS gereksinimleri ve önerilen OS nedir?">
    OpenClaw hafiftir. Temel bir Gateway + bir sohbet kanalı için:

    - **Mutlak minimum:** 1 vCPU, 1GB RAM, ~500MB disk.
    - **Önerilen:** boş alan için 1-2 vCPU, 2GB RAM veya daha fazlası (günlükler, medya, çoklu kanallar). Node araçları ve tarayıcı otomasyonu kaynak tüketebilir.

    OS: **Ubuntu LTS** kullanın (veya herhangi bir modern Debian/Ubuntu). Linux kurulum yolu orada en iyi test edilmiştir.

    Belgeler: [Linux](/tr/platforms/linux), [VPS hosting](/tr/vps).

  </Accordion>

  <Accordion title="OpenClaw'ı bir VM içinde çalıştırabilir miyim ve gereksinimler nelerdir?">
    Evet. Bir VM'i VPS ile aynı şekilde değerlendirin: her zaman açık, erişilebilir olmalı ve
    Gateway ile etkinleştirdiğiniz kanallar için yeterli RAM'e sahip olmalıdır.

    Temel kılavuz:

    - **Mutlak minimum:** 1 vCPU, 1GB RAM.
    - **Önerilen:** çoklu kanal, tarayıcı otomasyonu veya medya araçları çalıştırıyorsanız 2GB RAM veya üzeri.
    - **OS:** Ubuntu LTS veya başka bir modern Debian/Ubuntu.

    Windows kullanıyorsanız **WSL2 en kolay VM tarzı kurulumdur** ve araç uyumluluğu en iyisidir.
    Bkz. [Windows](/tr/platforms/windows), [VPS hosting](/tr/vps).
    macOS'i bir VM içinde çalıştırıyorsanız bkz. [macOS VM](/tr/install/macos-vm).

  </Accordion>
</AccordionGroup>

## OpenClaw nedir?

<AccordionGroup>
  <Accordion title="OpenClaw tek paragrafta nedir?">
    OpenClaw, kendi cihazlarınızda çalıştırdığınız kişisel bir AI asistandır. Zaten kullandığınız mesajlaşma yüzeylerinde (WhatsApp, Telegram, Slack, Mattermost, Discord, Google Chat, Signal, iMessage, WebChat ve QQ Bot gibi paketlenmiş kanal plugin'leri) yanıt verir ve desteklenen platformlarda ses + canlı Canvas da sunabilir. **Gateway** her zaman açık denetim düzlemidir; ürünün kendisi asistandır.
  </Accordion>

  <Accordion title="Değer önerisi">
    OpenClaw "sadece bir Claude sarmalayıcısı" değildir. Zaten kullandığınız sohbet uygulamalarından
    erişilebilen, durum bilgili oturumlar, bellek ve araçlarla
    **kendi donanımınız üzerinde**
    yetenekli bir asistan çalıştırmanızı sağlayan, iş akışlarınızın denetimini barındırılan bir
    SaaS'e bırakmadan çalışan **yerel öncelikli bir denetim düzlemidir**.

    Öne çıkanlar:

    - **Cihazlarınız, verileriniz:** Gateway'i istediğiniz yerde çalıştırın (Mac, Linux, VPS) ve
      çalışma alanını + oturum geçmişini yerelde tutun.
    - **Web sandbox değil, gerçek kanallar:** WhatsApp/Telegram/Slack/Discord/Signal/iMessage/vb,
      ayrıca desteklenen platformlarda mobil ses ve Canvas.
    - **Modele bağlı değil:** Anthropic, OpenAI, MiniMax, OpenRouter vb. kullanın; temsilci başına yönlendirme
      ve devretme ile.
    - **Yalnızca yerel seçenek:** isterseniz **tüm veriler cihazınızda kalabilsin** diye yerel modeller çalıştırın.
    - **Çoklu temsilci yönlendirme:** kanal, hesap veya görev başına ayrı temsilciler; her birinin kendi
      çalışma alanı ve varsayılanları vardır.
    - **Açık kaynak ve hacklenebilir:** satıcı bağımlılığı olmadan inceleyin, genişletin ve kendi sunucunuzda barındırın.

    Belgeler: [Gateway](/tr/gateway), [Channels](/tr/channels), [Multi-agent](/tr/concepts/multi-agent),
    [Memory](/tr/concepts/memory).

  </Accordion>

  <Accordion title="Yeni kurdum - ilk olarak ne yapmalıyım?">
    İlk projeler için iyi örnekler:

    - Web sitesi oluşturun (WordPress, Shopify veya basit bir statik site).
    - Mobil uygulama prototipi yapın (taslak, ekranlar, API planı).
    - Dosya ve klasörleri düzenleyin (temizlik, adlandırma, etiketleme).
    - Gmail bağlayın ve özetleri veya takipleri otomatikleştirin.

    Büyük görevleri ele alabilir, ancak bunları aşamalara böldüğünüzde ve paralel iş için
    alt temsilciler kullandığınızda en iyi sonucu verir.

  </Accordion>

  <Accordion title="OpenClaw için günlük hayattaki en iyi beş kullanım alanı nedir?">
    Günlük kazanımlar genelde şöyle görünür:

    - **Kişisel brifingler:** gelen kutusu, takvim ve önemsediğiniz haberlerin özetleri.
    - **Araştırma ve taslak oluşturma:** e-postalar veya belgeler için hızlı araştırma, özetler ve ilk taslaklar.
    - **Hatırlatıcılar ve takipler:** cron veya heartbeat ile çalışan dürtmeler ve kontrol listeleri.
    - **Tarayıcı otomasyonu:** form doldurma, veri toplama ve web görevlerini yineleme.
    - **Cihazlar arası koordinasyon:** telefonunuzdan görev gönderin, Gateway bunu sunucuda çalıştırsın ve sonucu sohbette geri alın.

  </Accordion>

  <Accordion title="OpenClaw, bir SaaS için lead generation, outreach, reklamlar ve bloglar konusunda yardımcı olabilir mi?">
    **Araştırma, nitelendirme ve taslak oluşturma** için evet. Siteleri tarayabilir, kısa listeler oluşturabilir,
    potansiyel müşterileri özetleyebilir ve outreach veya reklam metni taslakları yazabilir.

    **Outreach veya reklam çalıştırmaları** için bir insanı döngüde tutun. Spam'den kaçının, yerel yasalara ve
    platform ilkelerine uyun ve gönderilmeden önce her şeyi gözden geçirin. En güvenli desen,
    OpenClaw'ın taslak hazırlaması ve sizin onaylamanızdır.

    Belgeler: [Security](/tr/gateway/security).

  </Accordion>

  <Accordion title="Web geliştirme için Claude Code'a göre avantajları nelerdir?">
    OpenClaw bir **kişisel asistan** ve koordinasyon katmanıdır; IDE yerine geçmez. Bir depoda en hızlı doğrudan kodlama döngüsü için
    Claude Code veya Codex kullanın. Dayanıklı bellek, cihazlar arası erişim ve araç orkestrasyonu
    istediğinizde OpenClaw kullanın.

    Avantajlar:

    - Oturumlar arasında **kalıcı bellek + çalışma alanı**
    - **Çok platformlu erişim** (WhatsApp, Telegram, TUI, WebChat)
    - **Araç orkestrasyonu** (tarayıcı, dosyalar, planlama, kancalar)
    - **Her zaman açık Gateway** (bir VPS'te çalıştırın, her yerden etkileşim kurun)
    - Yerel tarayıcı/ekran/kamera/exec için **Nodes**

    Vitrin: [https://openclaw.ai/showcase](https://openclaw.ai/showcase)

  </Accordion>
</AccordionGroup>

## Skills ve otomasyon

<AccordionGroup>
  <Accordion title="Depoyu kirli tutmadan Skills'i nasıl özelleştiririm?">
    Depo kopyasını düzenlemek yerine yönetilen geçersiz kılmalar kullanın. Değişikliklerinizi `~/.openclaw/skills/<name>/SKILL.md` içine koyun (veya `~/.openclaw/openclaw.json` içinde `skills.load.extraDirs` ile bir klasör ekleyin). Öncelik sırası `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → paketlenmiş → `skills.load.extraDirs` şeklindedir; yani yönetilen geçersiz kılmalar git'e dokunmadan paketlenmiş Skills üzerinde yine kazanır. Skill'in küresel olarak kurulu olmasını ama yalnızca bazı temsilcilere görünmesini istiyorsanız paylaşılan kopyayı `~/.openclaw/skills` içinde tutun ve görünürlüğü `agents.defaults.skills` ve `agents.list[].skills` ile denetleyin. Yalnızca upstream'e uygun düzenlemeler depoda yaşamalı ve PR olarak gönderilmelidir.
  </Accordion>

  <Accordion title="Skills'i özel bir klasörden yükleyebilir miyim?">
    Evet. `~/.openclaw/openclaw.json` içinde `skills.load.extraDirs` ile ek dizinler ekleyin (en düşük öncelik). Varsayılan öncelik sırası `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → paketlenmiş → `skills.load.extraDirs` şeklindedir. `clawhub` varsayılan olarak `./skills` içine kurar; OpenClaw bunu bir sonraki oturumda `<workspace>/skills` olarak değerlendirir. Skill yalnızca belirli temsilcilere görünmeliysa bunu `agents.defaults.skills` veya `agents.list[].skills` ile eşleştirin.
  </Accordion>

  <Accordion title="Farklı görevler için farklı modelleri nasıl kullanabilirim?">
    Bugün desteklenen desenler şunlardır:

    - **Cron işleri**: yalıtılmış işler iş başına `model` geçersiz kılması ayarlayabilir.
    - **Alt temsilciler**: görevleri farklı varsayılan modellere sahip ayrı temsilcilere yönlendirin.
    - **İsteğe bağlı geçiş**: geçerli oturum modelini istediğiniz zaman değiştirmek için `/model` kullanın.

    Bkz. [Cron jobs](/tr/automation/cron-jobs), [Multi-Agent Routing](/tr/concepts/multi-agent) ve [Slash commands](/tr/tools/slash-commands).

  </Accordion>

  <Accordion title="Bot ağır iş yaparken donuyor. Bunu nasıl başka yere aktarırım?">
    Uzun veya paralel görevler için **alt temsilciler** kullanın. Alt temsilciler kendi oturumlarında çalışır,
    özet döndürür ve ana sohbetinizin yanıt vermeye devam etmesini sağlar.

    Botunuzdan "bu görev için bir alt temsilci başlatmasını" isteyin veya `/subagents` kullanın.
    Gateway'in şu anda ne yaptığını (ve meşgul olup olmadığını) görmek için sohbette `/status` kullanın.

    Token ipucu: uzun görevler ve alt temsilciler her ikisi de token tüketir. Maliyet endişeniz varsa
    `agents.defaults.subagents.model` ile alt temsilciler için daha ucuz bir model ayarlayın.

    Belgeler: [Sub-agents](/tr/tools/subagents), [Background Tasks](/tr/automation/tasks).

  </Accordion>

  <Accordion title="Discord'da iş parçacığına bağlı alt temsilci oturumları nasıl çalışır?">
    İş parçacığı bağlarını kullanın. Bir Discord iş parçacığını alt temsilciye veya oturum hedefine bağlayabilirsiniz; böylece o iş parçacığındaki takip mesajları bağlı oturumda kalır.

    Temel akış:

    - `sessions_spawn` ile `thread: true` kullanarak başlatın (ve kalıcı takip için isteğe bağlı `mode: "session"`).
    - Veya `/focus <target>` ile elle bağlayın.
    - Bağ durumunu incelemek için `/agents` kullanın.
    - Otomatik odak kaldırmayı denetlemek için `/session idle <duration|off>` ve `/session max-age <duration|off>` kullanın.
    - İş parçacığını ayırmak için `/unfocus` kullanın.

    Gerekli yapılandırma:

    - Genel varsayılanlar: `session.threadBindings.enabled`, `session.threadBindings.idleHours`, `session.threadBindings.maxAgeHours`.
    - Discord geçersiz kılmaları: `channels.discord.threadBindings.enabled`, `channels.discord.threadBindings.idleHours`, `channels.discord.threadBindings.maxAgeHours`.
    - Başlatmada otomatik bağlama: `channels.discord.threadBindings.spawnSubagentSessions: true` ayarlayın.

    Belgeler: [Sub-agents](/tr/tools/subagents), [Discord](/tr/channels/discord), [Configuration Reference](/tr/gateway/configuration-reference), [Slash commands](/tr/tools/slash-commands).

  </Accordion>

  <Accordion title="Bir alt temsilci bitti ama tamamlanma güncellemesi yanlış yere gitti veya hiç gönderilmedi. Neyi kontrol etmeliyim?">
    Önce çözümlenmiş istekte bulunan rota bilgisini kontrol edin:

    - Tamamlama kipindeki alt temsilci teslimatı, varsa bağlı iş parçacığını veya konuşma rotasını tercih eder.
    - Tamamlama kaynağı yalnızca kanal taşıyorsa, OpenClaw doğrudan teslimatın yine de başarılı olabilmesi için istekte bulunan oturumun depolanan rotasına (`lastChannel` / `lastTo` / `lastAccountId`) geri döner.
    - Ne bağlı bir rota ne de kullanılabilir bir depolanan rota varsa doğrudan teslimat başarısız olabilir ve sonuç sohbete hemen gönderilmek yerine kuyruğa alınmış oturum teslimatına geri düşer.
    - Geçersiz veya eski hedefler yine de kuyruk geri düşüşünü veya son teslimat hatasını zorlayabilir.
    - Çocuğun son görünür asistan yanıtı tam olarak sessiz token `NO_REPLY` / `no_reply` ise veya tam olarak `ANNOUNCE_SKIP` ise OpenClaw, eski erken ilerlemeyi göndermek yerine duyuruyu bilerek bastırır.
    - Çocuk yalnızca araç çağrılarından sonra zaman aşımına uğradıysa duyuru, ham araç çıktısını yeniden oynatmak yerine bunu kısa bir kısmi ilerleme özetine indirger.

    Hata ayıklama:

    ```bash
    openclaw tasks show <runId-or-sessionKey>
    ```

    Belgeler: [Sub-agents](/tr/tools/subagents), [Background Tasks](/tr/automation/tasks), [Session Tools](/tr/concepts/session-tool).

  </Accordion>

  <Accordion title="Cron veya hatırlatıcılar tetiklenmiyor. Neyi kontrol etmeliyim?">
    Cron, Gateway süreci içinde çalışır. Gateway sürekli çalışmıyorsa
    zamanlanmış işler çalışmaz.

    Denetim listesi:

    - Cron'un etkin olduğunu (`cron.enabled`) ve `OPENCLAW_SKIP_CRON`'un ayarlı olmadığını doğrulayın.
    - Gateway'in 7/24 çalıştığını kontrol edin (uyku/yeniden başlatma olmamalı).
    - İş için saat dilimi ayarlarını doğrulayın (`--tz` ile ana bilgisayar saat dilimi).

    Hata ayıklama:

    ```bash
    openclaw cron run <jobId>
    openclaw cron runs --id <jobId> --limit 50
    ```

    Belgeler: [Cron jobs](/tr/automation/cron-jobs), [Automation & Tasks](/tr/automation).

  </Accordion>

  <Accordion title="Cron tetiklendi ama kanala hiçbir şey gönderilmedi. Neden?">
    Önce teslim kipini kontrol edin:

    - `--no-deliver` / `delivery.mode: "none"` dış mesaj beklenmediği anlamına gelir.
    - Eksik veya geçersiz duyuru hedefi (`channel` / `to`) çalıştırıcının giden teslimatı atlaması demektir.
    - Kanal kimlik doğrulama hataları (`unauthorized`, `Forbidden`) çalıştırıcının teslim etmeye çalıştığını ancak kimlik bilgilerinin bunu engellediğini gösterir.
    - Sessiz bir yalıtılmış sonuç (`NO_REPLY` / `no_reply` yalnızca) kasıtlı olarak teslim edilemez kabul edilir; bu durumda çalıştırıcı kuyruk geri dönüş teslimatını da bastırır.

    Yalıtılmış cron işleri için son teslimata çalıştırıcı sahiptir. Temsilcinin,
    çalıştırıcının göndermesi için düz metin özet döndürmesi beklenir. `--no-deliver`
    bu sonucu dahili tutar; temsilcinin bunun yerine mesaj aracıyla doğrudan
    göndermesine izin vermez.

    Hata ayıklama:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    Belgeler: [Cron jobs](/tr/automation/cron-jobs), [Background Tasks](/tr/automation/tasks).

  </Accordion>

  <Accordion title="Yalıtılmış bir cron çalıştırması neden model değiştirdi veya bir kez yeniden denedi?">
    Bu genellikle yinelenen zamanlama değil, canlı model değiştirme yoludur.

    Yalıtılmış cron, etkin çalıştırma
    `LiveSessionModelSwitchError` attığında çalışma zamanı model aktarımını kalıcı hâle getirip yeniden deneyebilir. Yeniden deneme,
    değiştirilen sağlayıcıyı/modeli korur; değişim yeni bir kimlik doğrulama profili geçersiz kılması taşıdıysa cron
    bunu da yeniden denemeden önce kalıcılaştırır.

    İlgili seçim kuralları:

    - Uygunsa önce Gmail kancası model geçersiz kılması kazanır.
    - Sonra iş başına `model`.
    - Sonra depolanmış cron-oturum modeli geçersiz kılması.
    - Sonra normal temsilci/varsayılan model seçimi.

    Yeniden deneme döngüsü sınırlıdır. İlk deneme + 2 geçiş yeniden denemesinden sonra
    cron sonsuza kadar döngüye girmek yerine iptal eder.

    Hata ayıklama:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    Belgeler: [Cron jobs](/tr/automation/cron-jobs), [cron CLI](/cli/cron).

  </Accordion>

  <Accordion title="Linux'ta Skills nasıl yüklenir?">
    Yerel `openclaw skills` komutlarını kullanın veya Skills'i çalışma alanınıza bırakın. macOS Skills UI Linux'ta yoktur.
    Skills'e [https://clawhub.ai](https://clawhub.ai) üzerinden göz atın.

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

    Yerel `openclaw skills install`, etkin çalışma alanı `skills/`
    dizinine yazar. Kendi Skills'inizi yayımlamak veya
    eşzamanlamak istiyorsanız ayrı `clawhub` CLI'ını kurun. Temsilciler arasında paylaşılan kurulumlar için Skill'i
    `~/.openclaw/skills` altına koyun ve hangi temsilcilerin görebileceğini daraltmak istiyorsanız
    `agents.defaults.skills` veya
    `agents.list[].skills` kullanın.

  </Accordion>

  <Accordion title="OpenClaw görevleri zamanlı veya arka planda sürekli çalıştırabilir mi?">
    Evet. Gateway zamanlayıcısını kullanın:

    - Zamanlanmış veya yinelenen görevler için **cron işleri** (yeniden başlatmalardan sonra kalıcıdır).
    - "Ana oturum" periyodik denetimleri için **Heartbeat**.
    - Özetler gönderen veya sohbetlere teslim eden otonom temsilciler için **yalıtılmış işler**.

    Belgeler: [Cron jobs](/tr/automation/cron-jobs), [Automation & Tasks](/tr/automation),
    [Heartbeat](/tr/gateway/heartbeat).

  </Accordion>

  <Accordion title="Linux'tan Apple macOS-only Skills çalıştırabilir miyim?">
    Doğrudan hayır. macOS Skills, `metadata.openclaw.os` artı gerekli ikili dosyalar tarafından denetlenir ve Skills yalnızca **Gateway ana bilgisayarında** uygun olduğunda sistem isteminde görünür. Linux'ta `darwin`-yalnız Skills (`apple-notes`, `apple-reminders`, `things-mac` gibi) kapılamayı geçersiz kılmadıkça yüklenmez.

    Desteklenen üç deseniniz vardır:

    **Seçenek A - Gateway'i bir Mac üzerinde çalıştırın (en basit).**
    Gateway'i macOS ikililerinin bulunduğu yerde çalıştırın, sonra Linux'tan [remote mode](#gateway-ports-already-running-and-remote-mode) veya Tailscale üzerinden bağlanın. Gateway ana bilgisayarı macOS olduğu için Skills normal şekilde yüklenir.

    **Seçenek B - bir macOS node kullanın (SSH yok).**
    Gateway'i Linux'ta çalıştırın, bir macOS node (menubar app) eşleyin ve Mac'te **Node Run Commands** ayarını "Always Ask" veya "Always Allow" yapın. Gerekli ikili dosyalar node üzerinde varsa OpenClaw, yalnızca macOS Skills'i uygun olarak değerlendirebilir. Temsilci bu Skills'i `nodes` aracıyla çalıştırır. "Always Ask" seçerseniz istemde "Always Allow" onayı o komutu izin listesine ekler.

    **Seçenek C - macOS ikili dosyalarını SSH üzerinden vekil olarak kullanın (ileri seviye).**
    Gateway'i Linux'ta tutun, ancak gerekli CLI ikili dosyalarını bir Mac'te çalışan SSH sarmalayıcılarına çözdürün. Sonra Skill'i Linux'a izin verecek şekilde geçersiz kılın ki uygun kalsın.

    1. İkili için bir SSH sarmalayıcısı oluşturun (örnek: Apple Notes için `memo`):

       ```bash
       #!/usr/bin/env bash
       set -euo pipefail
       exec ssh -T user@mac-host /opt/homebrew/bin/memo "$@"
       ```

    2. Sarmalayıcıyı Linux ana bilgisayarda `PATH` üstüne koyun (örneğin `~/bin/memo`).
    3. Skill meta verisini (çalışma alanı veya `~/.openclaw/skills`) Linux'a izin verecek şekilde geçersiz kılın:

       ```markdown
       ---
       name: apple-notes
       description: Apple Notes'u macOS üzerindeki memo CLI ile yönetin.
       metadata: { "openclaw": { "os": ["darwin", "linux"], "requires": { "bins": ["memo"] } } }
       ---
       ```

    4. Skills anlık görüntüsünün yenilenmesi için yeni bir oturum başlatın.

  </Accordion>

  <Accordion title="Notion veya HeyGen entegrasyonunuz var mı?">
    Bugün yerleşik değil.

    Seçenekler:

    - **Özel Skill / plugin:** güvenilir API erişimi için en iyisi (Notion/HeyGen'in ikisinin de API'si var).
    - **Tarayıcı otomasyonu:** kod olmadan çalışır ama daha yavaş ve kırılgandır.

    İstemci başına bağlam tutmak istiyorsanız (ajans iş akışları), basit bir desen şudur:

    - Müşteri başına bir Notion sayfası (bağlam + tercihler + etkin işler).
    - Temsilciden bir oturumun başında bu sayfayı getirmesini isteyin.

    Yerel entegrasyon istiyorsanız bir özellik isteği açın veya bu API'leri hedefleyen bir Skill
    oluşturun.

    Skills yükleme:

    ```bash
    openclaw skills install <skill-slug>
    openclaw skills update --all
    ```

    Yerel kurulumlar etkin çalışma alanı `skills/` dizinine iner. Temsilciler arasında paylaşılan Skills için bunları `~/.openclaw/skills/<name>/SKILL.md` içine yerleştirin. Paylaşılan kurulumu yalnızca bazı temsilciler görmeliysa `agents.defaults.skills` veya `agents.list[].skills` yapılandırın. Bazı Skills, Homebrew üzerinden kurulan ikili dosyalar bekler; Linux'ta bu Linuxbrew anlamına gelir (yukarıdaki Homebrew Linux SSS girdisine bakın). Bkz. [Skills](/tr/tools/skills), [Skills config](/tr/tools/skills-config) ve [ClawHub](/tr/tools/clawhub).

  </Accordion>

  <Accordion title="Mevcut oturum açılmış Chrome'umu OpenClaw ile nasıl kullanırım?">
    Chrome DevTools MCP üzerinden bağlanan yerleşik `user` tarayıcı profilini kullanın:

    ```bash
    openclaw browser --browser-profile user tabs
    openclaw browser --browser-profile user snapshot
    ```

    Özel ad istiyorsanız açık bir MCP profili oluşturun:

    ```bash
    openclaw browser create-profile --name chrome-live --driver existing-session
    openclaw browser --browser-profile chrome-live tabs
    ```

    Bu yol ana bilgisayara özeldir. Gateway başka yerde çalışıyorsa ya tarayıcı makinesinde bir node host çalıştırın ya da bunun yerine uzak CDP kullanın.

    `existing-session` / `user` üzerindeki mevcut sınırlamalar:

    - işlemler CSS seçici odaklı değil, ref odaklıdır
    - yüklemeler `ref` / `inputRef` gerektirir ve şu anda aynı anda bir dosyayı destekler
    - `responsebody`, PDF dışa aktarma, indirme yakalama ve toplu işlemler hâlâ yönetilen bir tarayıcıya veya ham CDP profiline ihtiyaç duyar

  </Accordion>
</AccordionGroup>

## Sandbox ve bellek

<AccordionGroup>
  <Accordion title="Özel bir sandboxing belgesi var mı?">
    Evet. Bkz. [Sandboxing](/tr/gateway/sandboxing). Docker'a özgü kurulum için (tam gateway Docker içinde veya sandbox imajları), bkz. [Docker](/tr/install/docker).
  </Accordion>

  <Accordion title="Docker kısıtlı hissettiriyor - tam özellikleri nasıl etkinleştiririm?">
    Varsayılan imaj güvenlik önceliklidir ve `node` kullanıcısı olarak çalışır; bu nedenle
    sistem paketleri, Homebrew veya paketlenmiş tarayıcılar içermez. Daha dolu bir kurulum için:

    - Önbellekler kalıcı olsun diye `/home/node` yolunu `OPENCLAW_HOME_VOLUME` ile kalıcılaştırın.
    - Sistem bağımlılıklarını `OPENCLAW_DOCKER_APT_PACKAGES` ile imaja gömün.
    - Paketlenmiş CLI ile Playwright tarayıcılarını yükleyin:
      `node /app/node_modules/playwright-core/cli.js install chromium`
    - `PLAYWRIGHT_BROWSERS_PATH` ayarlayın ve yolun kalıcı olduğundan emin olun.

    Belgeler: [Docker](/tr/install/docker), [Browser](/tr/tools/browser).

  </Accordion>

  <Accordion title="DM'leri kişisel tutup grupları herkese açık/sandbox içinde tek temsilciyle yapabilir miyim?">
    Evet - özel trafiğiniz **DM**, herkese açık trafiğiniz **gruplar** ise.

    `agents.defaults.sandbox.mode: "non-main"` kullanın; böylece grup/kanal oturumları (ana olmayan anahtarlar) Docker içinde çalışır, ana DM oturumu ise ana bilgisayarda kalır. Sonra sandbox içindeki oturumlarda hangi araçların kullanılabileceğini `tools.sandbox.tools` ile kısıtlayın.

    Kurulum rehberi + örnek yapılandırma: [Groups: personal DMs + public groups](/tr/channels/groups#pattern-personal-dms-public-groups-single-agent)

    Ana yapılandırma başvurusu: [Gateway configuration](/tr/gateway/configuration-reference#agentsdefaultssandbox)

  </Accordion>

  <Accordion title="Bir ana bilgisayar klasörünü sandbox içine nasıl bağlarım?">
    `agents.defaults.sandbox.docker.binds` alanını `["host:path:mode"]` olarak ayarlayın (ör. `"/home/user/src:/src:ro"`). Genel + temsilci başına bağlar birleştirilir; `scope: "shared"` olduğunda temsilci başına bağlar yok sayılır. Hassas olan her şey için `:ro` kullanın ve bağların sandbox dosya sistemi duvarlarını aştığını unutmayın.

    OpenClaw bağ kaynaklarını hem normalize edilmiş yola hem de en derin mevcut üst atadan çözümlenen kanonik yola göre doğrular. Bu, son yol bölümü henüz mevcut olmadığında bile sembolik bağlantılı üst kaçışların kapalı başarısız olduğu ve izinli kök denetimlerinin sembolik bağlantı çözümlemesinden sonra da geçerli olduğu anlamına gelir.

    Örnekler ve güvenlik notları için [Sandboxing](/tr/gateway/sandboxing#custom-bind-mounts) ve [Sandbox vs Tool Policy vs Elevated](/tr/gateway/sandbox-vs-tool-policy-vs-elevated#bind-mounts-security-quick-check) bölümlerine bakın.

  </Accordion>

  <Accordion title="Bellek nasıl çalışır?">
    OpenClaw belleği, temsilci çalışma alanındaki Markdown dosyalarından ibarettir:

    - `memory/YYYY-MM-DD.md` içinde günlük notlar
    - `MEMORY.md` içinde küratörlü uzun vadeli notlar (yalnızca ana/özel oturumlar)

    OpenClaw ayrıca modele,
    otomatik sıkıştırmadan önce dayanıklı notlar yazmasını hatırlatmak için **sessiz bir ön-sıkıştırma bellek boşaltması** çalıştırır. Bu yalnızca çalışma alanı
    yazılabilir olduğunda çalışır (salt okunur sandbox'lar bunu atlar). Bkz. [Memory](/tr/concepts/memory).

  </Accordion>

  <Accordion title="Bellek bir şeyleri unutmaya devam ediyor. Nasıl kalıcı hâle getiririm?">
    Bottan **gerçeği belleğe yazmasını** isteyin. Uzun vadeli notlar `MEMORY.md` içine,
    kısa vadeli bağlam ise `memory/YYYY-MM-DD.md` içine gitmelidir.

    Bu hâlâ geliştirdiğimiz bir alandır. Modele bellekleri depolamasını hatırlatmak yardımcı olur;
    ne yapacağını bilir. Hâlâ unutuyorsa Gateway'in her çalıştırmada aynı
    çalışma alanını kullandığını doğrulayın.

    Belgeler: [Memory](/tr/concepts/memory), [Agent workspace](/tr/concepts/agent-workspace).

  </Accordion>

  <Accordion title="Bellek sonsuza dek kalır mı? Sınırlar nelerdir?">
    Bellek dosyaları diskte yaşar ve siz silene kadar kalıcıdır. Sınır
    model değil, depolamanızdır. **Oturum bağlamı** yine de modelin
    bağlam penceresi ile sınırlıdır; bu nedenle uzun konuşmalar sıkıştırılabilir veya kesilebilir. Bu yüzden
    bellek araması vardır - yalnızca ilgili parçaları bağlama geri çeker.

    Belgeler: [Memory](/tr/concepts/memory), [Context](/tr/concepts/context).

  </Accordion>

  <Accordion title="Anlamsal bellek araması için OpenAI API anahtarı gerekir mi?">
    Yalnızca **OpenAI embeddings** kullanırsanız. Codex OAuth sohbet/tamamlamaları kapsar ve
    embeddings erişimi vermez; dolayısıyla **Codex ile oturum açmak (OAuth veya
    Codex CLI girişi)** anlamsal bellek aramasına yardımcı olmaz. OpenAI embeddings
    hâlâ gerçek bir API anahtarı gerektirir (`OPENAI_API_KEY` veya `models.providers.openai.apiKey`).

    Açıkça bir sağlayıcı ayarlamazsanız, OpenClaw API anahtarını
    çözebildiğinde otomatik olarak sağlayıcı seçer (kimlik doğrulama profilleri, `models.providers.*.apiKey` veya ortam değişkenleri).
    OpenAI anahtarı çözümlenirse OpenAI'ı, aksi halde Gemini anahtarı
    çözümlenirse Gemini'yi, sonra Voyage'ı, sonra Mistral'ı tercih eder. Uzak anahtar yoksa bellek
    araması siz yapılandırana kadar devre dışı kalır. Yapılandırılmış ve mevcut yerel model yolunuz varsa OpenClaw
    `local` seçeneğini tercih eder. `memorySearch.provider = "ollama"` açıkça ayarlandığında
    Ollama desteklenir.

    Yerel kalmak istiyorsanız `memorySearch.provider = "local"` ayarlayın (ve isteğe bağlı
    `memorySearch.fallback = "none"`). Gemini embeddings istiyorsanız
    `memorySearch.provider = "gemini"` ayarlayın ve `GEMINI_API_KEY` (veya
    `memorySearch.remote.apiKey`) sağlayın. **OpenAI, Gemini, Voyage, Mistral, Ollama veya local** embedding
    modellerini destekliyoruz - kurulum ayrıntıları için [Memory](/tr/concepts/memory) bölümüne bakın.

  </Accordion>
</AccordionGroup>

## Diskte neler nerede yaşar

<AccordionGroup>
  <Accordion title="OpenClaw ile kullanılan tüm veriler yerelde mi kaydedilir?">
    Hayır - **OpenClaw'ın durumu yereldir**, ancak **harici hizmetler onlara gönderdiğinizi yine de görür**.

    - **Varsayılan olarak yerel:** oturumlar, bellek dosyaları, yapılandırma ve çalışma alanı gateway ana bilgisayarında yaşar
      (`~/.openclaw` + çalışma alanı dizininiz).
    - **Gereği olarak uzak:** model sağlayıcılarına (Anthropic/OpenAI/vb.) gönderdiğiniz mesajlar
      onların API'lerine gider ve sohbet platformları (WhatsApp/Telegram/Slack/vb.) mesaj verilerini kendi
      sunucularında depolar.
    - **İzi siz denetlersiniz:** yerel modeller kullanmak istemleri makinenizde tutar, ancak kanal
      trafiği yine de kanalın sunucularından geçer.

    İlgili: [Agent workspace](/tr/concepts/agent-workspace), [Memory](/tr/concepts/memory).

  </Accordion>

  <Accordion title="OpenClaw verilerini nerede saklar?">
    Her şey `$OPENCLAW_STATE_DIR` altında yaşar (varsayılan: `~/.openclaw`):

    | Yol                                                            | Amaç                                                            |
    | --------------------------------------------------------------- | ------------------------------------------------------------------ |
    | `$OPENCLAW_STATE_DIR/openclaw.json`                             | Ana yapılandırma (JSON5)                                                |
    | `$OPENCLAW_STATE_DIR/credentials/oauth.json`                    | Eski OAuth içe aktarma (ilk kullanımda auth profillerine kopyalanır)       |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth-profiles.json` | Kimlik doğrulama profilleri (OAuth, API anahtarları ve isteğe bağlı `keyRef`/`tokenRef`)  |
    | `$OPENCLAW_STATE_DIR/secrets.json`                              | `file` SecretRef sağlayıcıları için isteğe bağlı dosya destekli gizli yük |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth.json`          | Eski uyumluluk dosyası (statik `api_key` girdileri temizlenmiş)      |
    | `$OPENCLAW_STATE_DIR/credentials/`                              | Sağlayıcı durumu (ör. `whatsapp/<accountId>/creds.json`)            |
    | `$OPENCLAW_STATE_DIR/agents/`                                   | Temsilci başına durum (agentDir + oturumlar)                              |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                | Konuşma geçmişi ve durumu (temsilci başına)                           |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/sessions.json`   | Oturum meta verisi (temsilci başına)                                       |

    Eski tek temsilci yolu: `~/.openclaw/agent/*` (`openclaw doctor` tarafından taşınır).

    **Çalışma alanınız** (AGENTS.md, bellek dosyaları, Skills vb.) ayrıdır ve `agents.defaults.workspace` ile yapılandırılır (varsayılan: `~/.openclaw/workspace`).

  </Accordion>

  <Accordion title="AGENTS.md / SOUL.md / USER.md / MEMORY.md nerede yaşamalı?">
    Bu dosyalar `~/.openclaw` içinde değil, **temsilci çalışma alanında** yaşar.

    - **Çalışma alanı (temsilci başına)**: `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`,
      `MEMORY.md` (veya `MEMORY.md` yoksa eski geri dönüş `memory.md`),
      `memory/YYYY-MM-DD.md`, isteğe bağlı `HEARTBEAT.md`.
    - **Durum dizini (`~/.openclaw`)**: yapılandırma, kanal/sağlayıcı durumu, auth profilleri, oturumlar, günlükler,
      ve paylaşılan Skills (`~/.openclaw/skills`).

    Varsayılan çalışma alanı `~/.openclaw/workspace` olup şu şekilde yapılandırılabilir:

    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
    }
    ```

    Bot yeniden başlatmadan sonra "unutuyorsa", Gateway'in her başlatmada aynı
    çalışma alanını kullandığını doğrulayın (ve unutmayın: uzak kipte kullanılan çalışma alanı sizin yerel dizüstü bilgisayarınız değil,
    **gateway ana bilgisayarının** çalışma alanıdır).

    İpucu: dayanıklı bir davranış veya tercih istiyorsanız, sohbete güvenmek yerine bottan
    **bunu AGENTS.md veya MEMORY.md içine yazmasını** isteyin.

    Bkz. [Agent workspace](/tr/concepts/agent-workspace) ve [Memory](/tr/concepts/memory).

  </Accordion>

  <Accordion title="Önerilen yedekleme stratejisi">
    **Temsilci çalışma alanınızı** **özel** bir git reposuna koyun ve bunu yine
    özel bir yere yedekleyin (örneğin GitHub private). Bu, bellek + AGENTS/SOUL/USER
    dosyalarını yakalar ve daha sonra asistanın "zihnini" geri yüklemenizi sağlar.

    `~/.openclaw` altındaki hiçbir şeyi commit etmeyin (kimlik bilgileri, oturumlar, token'lar veya şifrelenmiş gizli yükler).
    Tam geri yükleme gerekiyorsa çalışma alanını ve durum dizinini
    ayrı ayrı yedekleyin (yukarıdaki taşıma sorusuna bakın).

    Belgeler: [Agent workspace](/tr/concepts/agent-workspace).

  </Accordion>

  <Accordion title="OpenClaw'ı tamamen nasıl kaldırırım?">
    Özel rehbere bakın: [Uninstall](/tr/install/uninstall).
  </Accordion>

  <Accordion title="Temsilciler çalışma alanı dışında çalışabilir mi?">
    Evet. Çalışma alanı **varsayılan cwd** ve bellek çapasıdır, katı bir sandbox değildir.
    Göreli yollar çalışma alanı içinde çözülür, ancak mutlak yollar
    sandboxing etkin değilse ana bilgisayardaki başka konumlara erişebilir. Yalıtım gerekiyorsa
    [`agents.defaults.sandbox`](/tr/gateway/sandboxing) veya temsilci başına sandbox ayarlarını kullanın. Bir
    reponun varsayılan çalışma dizini olmasını istiyorsanız o temsilcinin
    `workspace` değerini repo köküne yöneltin. OpenClaw deposu yalnızca kaynak koddur; temsilcinin özellikle onun içinde çalışmasını istemiyorsanız
    çalışma alanını ondan ayrı tutun.

    Örnek (repo varsayılan cwd olarak):

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

  <Accordion title="Uzak kip: oturum deposu nerede?">
    Oturum durumuna **gateway ana bilgisayarı** sahiptir. Uzak kipteyseniz ilgilendiğiniz oturum deposu yerel dizüstü bilgisayarınızda değil, uzak makinededir. Bkz. [Session management](/tr/concepts/session).
  </Accordion>
</AccordionGroup>

## Yapılandırma temelleri

<AccordionGroup>
  <Accordion title="Yapılandırma biçimi nedir? Nerede?">
    OpenClaw isteğe bağlı **JSON5** yapılandırmasını `$OPENCLAW_CONFIG_PATH` üzerinden okur (varsayılan: `~/.openclaw/openclaw.json`):

    ```
    $OPENCLAW_CONFIG_PATH
    ```

    Dosya eksikse güvenli sayılabilecek varsayılanları kullanır (varsayılan çalışma alanı `~/.openclaw/workspace` dahil).

  </Accordion>

  <Accordion title='gateway.bind: "lan" (veya "tailnet") ayarladım ve şimdi hiçbir şey dinlemiyor / UI yetkisiz diyor'>
    Loopback olmayan bind'ler **geçerli bir gateway auth yolu** gerektirir. Pratikte bu şu anlama gelir:

    - paylaşılan gizli kimlik doğrulaması: token veya parola
    - doğru yapılandırılmış loopback olmayan kimlik farkındalıklı ters proxy arkasında `gateway.auth.mode: "trusted-proxy"`

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

    - `gateway.remote.token` / `.password` kendi başına yerel gateway kimlik doğrulamasını etkinleştirmez.
    - Yerel çağrı yolları, yalnızca `gateway.auth.*` ayarsızsa geri dönüş olarak `gateway.remote.*` kullanabilir.
    - Parola kimlik doğrulaması için bunun yerine `gateway.auth.mode: "password"` artı `gateway.auth.password` (veya `OPENCLAW_GATEWAY_PASSWORD`) ayarlayın.
    - `gateway.auth.token` / `gateway.auth.password` SecretRef ile açıkça yapılandırılmış ve çözümlenmemişse çözümleme kapalı başarısız olur (maskelenmiş uzak geri dönüş olmaz).
    - Paylaşılan gizli Control UI kurulumları `connect.params.auth.token` veya `connect.params.auth.password` üzerinden kimlik doğrular (uygulama/UI ayarlarında depolanır). Tailscale Serve veya `trusted-proxy` gibi kimlik taşıyan kipler ise bunun yerine istek başlıkları kullanır. Paylaşılan gizlileri URL'lere koymaktan kaçının.
    - `gateway.auth.mode: "trusted-proxy"` ile aynı ana bilgisayar üzerindeki loopback ters proxy'ler yine de trusted-proxy kimlik doğrulamasını karşılamaz. Güvenilir proxy, yapılandırılmış loopback olmayan bir kaynak olmalıdır.

  </Accordion>

  <Accordion title="Neden artık localhost üzerinde token'a ihtiyacım var?">
    OpenClaw varsayılan olarak loopback dahil gateway kimlik doğrulamasını zorunlu kılar. Normal varsayılan yolda bu token kimlik doğrulaması demektir: açık bir auth yolu yapılandırılmamışsa gateway başlangıcı token kipine çözülür ve bir tane otomatik üretir, bunu `gateway.auth.token` içine kaydeder; dolayısıyla **yerel WS istemcileri kimlik doğrulamalıdır**. Bu, diğer yerel süreçlerin Gateway'i çağırmasını engeller.

    Farklı bir auth yolu tercih ediyorsanız parola kipini açıkça seçebilirsiniz (veya loopback olmayan kimlik farkındalıklı ters proxy'ler için `trusted-proxy`). **Gerçekten** açık loopback istiyorsanız yapılandırmanızda açıkça `gateway.auth.mode: "none"` ayarlayın. Doctor sizin için her zaman token üretebilir: `openclaw doctor --generate-gateway-token`.

  </Accordion>

  <Accordion title="Yapılandırmayı değiştirdikten sonra yeniden başlatmam gerekir mi?">
    Gateway yapılandırmayı izler ve sıcak yeniden yüklemeyi destekler:

    - `gateway.reload.mode: "hybrid"` (varsayılan): güvenli değişiklikleri sıcak uygular, kritik olanlar için yeniden başlatır
    - `hot`, `restart`, `off` da desteklenir

  </Accordion>

  <Accordion title="Komik CLI sloganlarını nasıl kapatırım?">
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

    - `off`: slogan metnini gizler ama banner başlık/sürüm satırını korur.
    - `default`: her zaman `All your chats, one OpenClaw.` kullanır.
    - `random`: dönüşümlü komik/mevsimsel sloganlar (varsayılan davranış).
    - Hiç banner istemiyorsanız `OPENCLAW_HIDE_BANNER=1` ortam değişkenini ayarlayın.

  </Accordion>

  <Accordion title="Web aramayı (ve web fetch'i) nasıl etkinleştiririm?">
    `web_fetch` API anahtarı olmadan çalışır. `web_search` seçtiğiniz
    sağlayıcıya bağlıdır:

    - Brave, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search, Perplexity ve Tavily gibi API destekli sağlayıcılar normal API anahtarı kurulumlarını gerektirir.
    - Ollama Web Search anahtarsızdır, ancak yapılandırdığınız Ollama ana bilgisayarını kullanır ve `ollama signin` gerektirir.
    - DuckDuckGo anahtarsızdır, ancak bu resmî olmayan HTML tabanlı bir entegrasyondur.
    - SearXNG anahtarsız/kendi barındırdığınız bir çözümdür; `SEARXNG_BASE_URL` veya `plugins.entries.searxng.config.webSearch.baseUrl` yapılandırın.

    **Önerilen:** `openclaw configure --section web` çalıştırın ve bir sağlayıcı seçin.
    Ortam alternatifleri:

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
    Eski `tools.web.search.*` sağlayıcı yolları uyumluluk için geçici olarak hâlâ yüklenir, ancak yeni yapılandırmalar için kullanılmamalıdır.
    Firecrawl web-fetch geri dönüş yapılandırması `plugins.entries.firecrawl.config.webFetch.*` altında yaşar.

    Notlar:

    - İzin listeleri kullanıyorsanız `web_search`/`web_fetch`/`x_search` veya `group:web` ekleyin.
    - `web_fetch` varsayılan olarak etkindir (açıkça devre dışı bırakılmadıkça).
    - `tools.web.fetch.provider` çıkarılırsa OpenClaw, kullanılabilir kimlik bilgilerinden ilk hazır fetch geri dönüş sağlayıcısını otomatik algılar. Bugün paketlenmiş sağlayıcı Firecrawl'dır.
    - Daemon'lar ortam değişkenlerini `~/.openclaw/.env` (veya hizmet ortamı) üzerinden okur.

    Belgeler: [Web tools](/tr/tools/web).

  </Accordion>

  <Accordion title="config.apply yapılandırmamı sildi. Nasıl geri yüklerim ve bundan nasıl kaçınırım?">
    `config.apply` **tüm yapılandırmayı** değiştirir. Kısmi nesne gönderirseniz diğer her şey
    kaldırılır.

    Kurtarma:

    - Yedekten geri yükleyin (git veya kopyalanmış `~/.openclaw/openclaw.json`).
    - Yedeğiniz yoksa `openclaw doctor` yeniden çalıştırın ve kanalları/modelleri yeniden yapılandırın.
    - Bu beklenmedikse bir hata bildirin ve son bilinen yapılandırmanızı veya herhangi bir yedeği ekleyin.
    - Yerel bir kodlama temsilcisi çoğu zaman günlüklerden veya geçmişten çalışan bir yapılandırmayı yeniden oluşturabilir.

    Kaçınma:

    - Küçük değişiklikler için `openclaw config set` kullanın.
    - Etkileşimli düzenlemeler için `openclaw configure` kullanın.
    - Tam yol veya alan şekli konusunda emin değilseniz önce `config.schema.lookup` kullanın; size aşağı inmek için sığ şema düğümü ve anlık alt özetleri döndürür.
    - Kısmi RPC düzenlemeleri için `config.patch` kullanın; `config.apply`'ı yalnızca tam yapılandırma değiştirme için tutun.
    - Bir temsilci çalıştırmasından sahip-yalnız `gateway` aracını kullanıyorsanız, bu araç yine de `tools.exec.ask` / `tools.exec.security` yazımlarını reddeder (bunlarla aynı korumalı exec yollarına normalize olan eski `tools.bash.*` takma adları dahil).

    Belgeler: [Config](/cli/config), [Configure](/cli/configure), [Doctor](/tr/gateway/doctor).

  </Accordion>

  <Accordion title="Merkezi bir Gateway'i cihazlar arasında uzmanlaşmış çalışanlarla nasıl çalıştırırım?">
    Yaygın desen **bir Gateway** (ör. Raspberry Pi) + **nodes** + **agents** kullanmaktır:

    - **Gateway (merkezi):** kanallara (Signal/WhatsApp), yönlendirmeye ve oturumlara sahiptir.
    - **Nodes (cihazlar):** Mac/iOS/Android çevresel birim olarak bağlanır ve yerel araçları (`system.run`, `canvas`, `camera`) açığa çıkarır.
    - **Agents (çalışanlar):** özel roller için ayrı zihinler/çalışma alanları (ör. "Hetzner ops", "Personal data").
    - **Sub-agents:** paralellik istediğinizde ana temsilciden arka plan işi başlatır.
    - **TUI:** Gateway'e bağlanır ve temsilci/oturum değiştirir.

    Belgeler: [Nodes](/tr/nodes), [Remote access](/tr/gateway/remote), [Multi-Agent Routing](/tr/concepts/multi-agent), [Sub-agents](/tr/tools/subagents), [TUI](/web/tui).

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

    Varsayılan `false`'tur (görünür tarayıcı). Headless, bazı sitelerde bot karşıtı denetimleri tetiklemeye daha yatkındır. Bkz. [Browser](/tr/tools/browser).

    Headless **aynı Chromium motorunu** kullanır ve çoğu otomasyon için çalışır (formlar, tıklamalar, scraping, girişler). Ana farklar:

    - Görünür tarayıcı penceresi yoktur (görsel gerekiyorsa ekran görüntüsü kullanın).
    - Bazı siteler headless kipte otomasyona karşı daha katıdır (CAPTCHA'lar, bot karşıtı önlemler).
      Örneğin X/Twitter sık sık headless oturumları engeller.

  </Accordion>

  <Accordion title="Tarayıcı denetimi için Brave'i nasıl kullanırım?">
    `browser.executablePath` değerini Brave ikiliniz (veya herhangi bir Chromium tabanlı tarayıcı) olarak ayarlayın ve Gateway'i yeniden başlatın.
    Tam yapılandırma örnekleri için [Browser](/tr/tools/browser#use-brave-or-another-chromium-based-browser) bölümüne bakın.
  </Accordion>
</AccordionGroup>

## Uzak gateway'ler ve nodes

<AccordionGroup>
  <Accordion title="Komutlar Telegram, gateway ve nodes arasında nasıl yayılır?">
    Telegram mesajları **gateway** tarafından işlenir. Gateway temsilciyi çalıştırır ve
    ancak bir node aracına ihtiyaç duyulduğunda **Gateway WebSocket** üzerinden node'ları çağırır:

    Telegram → Gateway → Agent → `node.*` → Node → Gateway → Telegram

    Node'lar gelen sağlayıcı trafiğini görmez; yalnızca node RPC çağrılarını alırlar.

  </Accordion>

  <Accordion title="Gateway uzakta barındırılıyorsa temsilcim bilgisayarıma nasıl erişebilir?">
    Kısa yanıt: **bilgisayarınızı bir node olarak eşleyin**. Gateway başka yerde çalışır, ama
    yerel makinenizdeki `node.*` araçlarını (ekran, kamera, sistem) Gateway WebSocket üzerinden çağırabilir.

    Tipik kurulum:

    1. Gateway'i her zaman açık ana bilgisayarda çalıştırın (VPS/ev sunucusu).
    2. Gateway ana bilgisayarını + bilgisayarınızı aynı tailnet'e koyun.
    3. Gateway WS'nin erişilebilir olduğundan emin olun (tailnet bind veya SSH tüneli).
    4. macOS uygulamasını yerelde açın ve **Remote over SSH** kipinde (veya doğrudan tailnet üzerinden)
       bağlanın ki node olarak kaydolabilsin.
    5. Gateway üzerinde node'u onaylayın:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    Ayrı TCP köprüsü gerekmez; node'lar Gateway WebSocket üzerinden bağlanır.

    Güvenlik hatırlatması: bir macOS node eşlemek o makinede `system.run` yetkisi verir. Yalnızca
    güvendiğiniz cihazları eşleyin ve [Security](/tr/gateway/security) bölümünü inceleyin.

    Belgeler: [Nodes](/tr/nodes), [Gateway protocol](/tr/gateway/protocol), [macOS remote mode](/tr/platforms/mac/remote), [Security](/tr/gateway/security).

  </Accordion>

  <Accordion title="Tailscale bağlı ama yanıt alamıyorum. Şimdi ne yapmalıyım?">
    Temelleri kontrol edin:

    - Gateway çalışıyor mu: `openclaw gateway status`
    - Gateway sağlığı: `openclaw status`
    - Kanal sağlığı: `openclaw channels status`

    Sonra kimlik doğrulama ve yönlendirmeyi doğrulayın:

    - Tailscale Serve kullanıyorsanız `gateway.auth.allowTailscale` doğru ayarlanmış mı kontrol edin.
    - SSH tüneli üzerinden bağlanıyorsanız yerel tünelin açık olduğunu ve doğru porta işaret ettiğini doğrulayın.
    - İzin listelerinizin (DM veya grup) hesabınızı içerdiğini doğrulayın.

    Belgeler: [Tailscale](/tr/gateway/tailscale), [Remote access](/tr/gateway/remote), [Channels](/tr/channels).

  </Accordion>

  <Accordion title="İki OpenClaw örneği birbirleriyle konuşabilir mi (yerel + VPS)?">
    Evet. Yerleşik bir "bot-to-bot" köprüsü yok, ancak bunu birkaç
    güvenilir şekilde bağlayabilirsiniz:

    **En basit:** iki botun da erişebildiği normal bir sohbet kanalı kullanın (Telegram/Slack/WhatsApp).
    Bot A'nın Bot B'ye mesaj göndermesini sağlayın, ardından Bot B normal şekilde yanıt versin.

    **CLI köprüsü (genel):** diğer Gateway'i
    `openclaw agent --message ... --deliver` ile çağıran bir betik çalıştırın ve diğer botun
    dinlediği bir sohbeti hedefleyin. Botlardan biri uzak VPS üzerindeyse CLI'nizi
    SSH/Tailscale üzerinden o uzak Gateway'e yöneltin (bkz. [Remote access](/tr/gateway/remote)).

    Örnek desen (hedef Gateway'e erişebilen bir makineden çalıştırın):

    ```bash
    openclaw agent --message "Yerel bottan merhaba" --deliver --channel telegram --reply-to <chat-id>
    ```

    İpucu: iki botun sonsuz döngüye girmemesi için bir koruma ekleyin (yalnızca mention,
    kanal izin listeleri veya "bot mesajlarına yanıt verme" kuralı).

    Belgeler: [Remote access](/tr/gateway/remote), [Agent CLI](/cli/agent), [Agent send](/tr/tools/agent-send).

  </Accordion>

  <Accordion title="Birden çok temsilci için ayrı VPS'lere ihtiyacım var mı?">
    Hayır. Bir Gateway birden fazla temsilciyi barındırabilir; her birinin kendi çalışma alanı, model varsayılanları
    ve yönlendirmesi olur. Bu normal kurulumdur ve
    temsilci başına bir VPS çalıştırmaktan çok daha ucuz ve basittir.

    Ayrı VPS'leri yalnızca katı yalıtım (güvenlik sınırları) veya paylaşmak
    istemediğiniz çok farklı yapılandırmalar gerektiğinde kullanın. Aksi halde bir Gateway tutun ve
    birden fazla temsilci veya alt temsilci kullanın.

  </Accordion>

  <Accordion title="Kişisel dizüstü bilgisayarımda bir node kullanmanın, VPS'ten SSH kullanmaya göre faydası var mı?">
    Evet - uzak Gateway'den dizüstü bilgisayarınıza erişmenin birinci sınıf yolu node'lardır ve
    kabuk erişiminden fazlasını açarlar. Gateway macOS/Linux üzerinde çalışır (Windows, WSL2 üzerinden) ve
    hafiftir (küçük bir VPS veya Raspberry Pi sınıfı kutu yeterlidir; 4 GB RAM bolca yeterlidir), bu yüzden yaygın
    kurulum, her zaman açık bir ana bilgisayar + node olarak dizüstü bilgisayarınızdır.

    - **Gelen SSH gerekmez.** Node'lar dışarıya Gateway WebSocket'e bağlanır ve cihaz eşleştirmesi kullanır.
    - **Daha güvenli yürütme denetimleri.** `system.run`, o dizüstü bilgisayardaki node izin listeleri/onayları ile kapılanır.
    - **Daha fazla cihaz aracı.** Node'lar `system.run` yanında `canvas`, `camera` ve `screen` de açığa çıkarır.
    - **Yerel tarayıcı otomasyonu.** Gateway'i bir VPS'te tutun ama tarayıcıyı dizüstü bilgisayardaki bir node host üzerinden yerelde çalıştırın ya da Chrome MCP ile ana bilgisayar üzerindeki yerel Chrome'a bağlanın.

    SSH, geçici kabuk erişimi için uygundur, ancak temsilci iş akışları ve
    cihaz otomasyonu için node'lar daha basittir.

    Belgeler: [Nodes](/tr/nodes), [Nodes CLI](/cli/nodes), [Browser](/tr/tools/browser).

  </Accordion>

  <Accordion title="Nodes bir gateway service çalıştırır mı?">
    Hayır. Bilerek yalıtılmış profiller çalıştırmıyorsanız (bkz. [Multiple gateways](/tr/gateway/multiple-gateways)) her ana bilgisayarda yalnızca **bir gateway** çalışmalıdır. Node'lar gateway'e bağlanan çevresel birimlerdir
    (iOS/Android nodes veya menubar app içinde macOS "node mode"). Headless node
    ana bilgisayarları ve CLI denetimi için [Node host CLI](/cli/node) bölümüne bakın.

    `gateway`, `discovery` ve `canvasHost` değişiklikleri için tam yeniden başlatma gerekir.

  </Accordion>

  <Accordion title="Yapılandırmayı uygulamak için API / RPC yolu var mı?">
    Evet.

    - `config.schema.lookup`: yazmadan önce bir yapılandırma alt ağacını sığ şema düğümü, eşleşen UI ipucu ve anlık alt özetlerle inceleyin
    - `config.get`: geçerli anlık görüntüyü + hash'i alın
    - `config.patch`: güvenli kısmi güncelleme (çoğu RPC düzenlemesi için tercih edilir)
    - `config.apply`: yapılandırmayı doğrular + tümünü değiştirir, sonra yeniden başlatır
    - Sahip-yalnız `gateway` çalışma zamanı aracı hâlâ `tools.exec.ask` / `tools.exec.security` yeniden yazımlarını reddeder; eski `tools.bash.*` takma adları aynı korumalı exec yollarına normalize olur

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

  <Accordion title="Bir VPS üzerinde Tailscale'i nasıl kurar ve Mac'imden nasıl bağlanırım?">
    Asgari adımlar:

    1. **VPS üzerinde yükleyin + giriş yapın**

       ```bash
       curl -fsSL https://tailscale.com/install.sh | sh
       sudo tailscale up
       ```

    2. **Mac'inizde yükleyin + giriş yapın**
       - Tailscale uygulamasını kullanın ve aynı tailnet'e giriş yapın.
    3. **MagicDNS'i etkinleştirin (önerilen)**
       - Tailscale yönetici konsolunda MagicDNS'i açın ki VPS kararlı bir ada sahip olsun.
    4. **Tailnet ana bilgisayar adını kullanın**
       - SSH: `ssh user@your-vps.tailnet-xxxx.ts.net`
       - Gateway WS: `ws://your-vps.tailnet-xxxx.ts.net:18789`

    SSH olmadan Control UI istiyorsanız VPS üzerinde Tailscale Serve kullanın:

    ```bash
    openclaw gateway --tailscale serve
    ```

    Bu, gateway'i loopback'e bağlı tutar ve HTTPS'i Tailscale üzerinden açığa çıkarır. Bkz. [Tailscale](/tr/gateway/tailscale).

  </Accordion>

  <Accordion title="Bir Mac node'u uzak Gateway'e nasıl bağlarım (Tailscale Serve)?">
    Serve, **Gateway Control UI + WS**'yi açığa çıkarır. Node'lar aynı Gateway WS uç noktası üzerinden bağlanır.

    Önerilen kurulum:

    1. **VPS + Mac'in aynı tailnet üzerinde olduğundan emin olun**.
    2. **macOS uygulamasını Remote kipte kullanın** (SSH hedefi tailnet ana bilgisayar adı olabilir).
       Uygulama gateway portunu tüneller ve node olarak bağlanır.
    3. **Gateway üzerinde node'u onaylayın**:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    Belgeler: [Gateway protocol](/tr/gateway/protocol), [Discovery](/tr/gateway/discovery), [macOS remote mode](/tr/platforms/mac/remote).

  </Accordion>

  <Accordion title="İkinci bir dizüstüye kurmalı mıyım yoksa sadece bir node mu eklemeliyim?">
    İkinci dizüstü bilgisayarda yalnızca **yerel araçlara** (ekran/kamera/exec) ihtiyacınız varsa bunu
    bir **node** olarak ekleyin. Bu, tek Gateway'i korur ve yinelenen yapılandırmadan kaçınır. Yerel node araçları
    şu anda yalnızca macOS'tadır, ancak bunları diğer OS'lere genişletmeyi planlıyoruz.

    Yalnızca **katı yalıtım** veya tamamen ayrı iki bot gerektiğinde ikinci bir Gateway kurun.

    Belgeler: [Nodes](/tr/nodes), [Nodes CLI](/cli/nodes), [Multiple gateways](/tr/gateway/multiple-gateways).

  </Accordion>
</AccordionGroup>

## Ortam değişkenleri ve .env yükleme

<AccordionGroup>
  <Accordion title="OpenClaw ortam değişkenlerini nasıl yükler?">
    OpenClaw, üst süreçten (shell, launchd/systemd, CI, vb.) ortam değişkenlerini okur ve ek olarak şunları yükler:

    - geçerli çalışma dizinindeki `.env`
    - `~/.openclaw/.env` içinden genel geri dönüş `.env` (yani `$OPENCLAW_STATE_DIR/.env`)

    Hiçbir `.env` dosyası mevcut ortam değişkenlerini geçersiz kılmaz.

    Ayrıca yapılandırma içinde satır içi ortam değişkenleri tanımlayabilirsiniz (yalnızca süreç ortamında eksikse uygulanır):

    ```json5
    {
      env: {
        OPENROUTER_API_KEY: "sk-or-...",
        vars: { GROQ_API_KEY: "gsk-..." },
      },
    }
    ```

    Tam öncelik ve kaynaklar için [/environment](/tr/help/environment) bölümüne bakın.

  </Accordion>

  <Accordion title="Gateway'i service üzerinden başlattım ve ortam değişkenlerim kayboldu. Şimdi ne olacak?">
    İki yaygın çözüm:

    1. Eksik anahtarları `~/.openclaw/.env` içine koyun ki hizmet shell ortamınızı devralmasa bile bunlar alınsın.
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

    Bu, oturum açma kabuğunuzu çalıştırır ve yalnızca eksik beklenen anahtarları içe aktarır (asla geçersiz kılmaz). Ortam değişkeni eşdeğerleri:
    `OPENCLAW_LOAD_SHELL_ENV=1`, `OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`.

  </Accordion>

  <Accordion title='COPILOT_GITHUB_TOKEN ayarladım ama models status "Shell env: off." gösteriyor. Neden?'>
    `openclaw models status`, **shell env içe aktarmasının** etkin olup olmadığını raporlar. "Shell env: off"
    ortam değişkenlerinizin eksik olduğu anlamına **gelmez** - sadece OpenClaw'ın
    oturum açma kabuğunuzu otomatik yüklemeyeceği anlamına gelir.

    Gateway hizmet olarak çalışıyorsa (launchd/systemd) shell
    ortamınızı devralmaz. Şunlardan birini yaparak düzeltin:

    1. Token'ı `~/.openclaw/.env` içine koyun:

       ```
       COPILOT_GITHUB_TOKEN=...
       ```

    2. Veya shell içe aktarmayı etkinleştirin (`env.shellEnv.enabled: true`).
    3. Veya yapılandırma `env` bloğunuza ekleyin (yalnızca eksikse uygulanır).

    Sonra gateway'i yeniden başlatın ve tekrar kontrol edin:

    ```bash
    openclaw models status
    ```

    Copilot token'ları `COPILOT_GITHUB_TOKEN` üzerinden okunur (ayrıca `GH_TOKEN` / `GITHUB_TOKEN`).
    Bkz. [/concepts/model-providers](/tr/concepts/model-providers) ve [/environment](/tr/help/environment).

  </Accordion>
</AccordionGroup>

## Oturumlar ve çoklu sohbetler

<AccordionGroup>
  <Accordion title="Taze bir konuşmayı nasıl başlatırım?">
    `/new` veya `/reset` komutunu tek başına mesaj olarak gönderin. Bkz. [Session management](/tr/concepts/session).
  </Accordion>

  <Accordion title="/new göndermezsem oturumlar otomatik sıfırlanır mı?">
    Oturumların süresi `session.idleMinutes` sonrasında dolabilir, ancak bu varsayılan olarak **kapalıdır** (varsayılan **0**).
    Boşta kalma süresi dolumunu etkinleştirmek için bunu pozitif bir değere ayarlayın. Etkinleştirildiğinde, boşta süre sonrasındaki **sonraki**
    mesaj o sohbet anahtarı için yeni bir oturum kimliği başlatır.
    Bu, dökümleri silmez - yalnızca yeni bir oturum başlatır.

    ```json5
    {
      session: {
        idleMinutes: 240,
      },
    }
    ```

  </Accordion>

  <Accordion title="OpenClaw örneklerinden oluşan bir takım (bir CEO ve birçok temsilci) kurmanın yolu var mı?">
    Evet, **çoklu temsilci yönlendirme** ve **alt temsilciler** ile. Bir koordinatör
    temsilci ve kendi çalışma alanları ile modellerine sahip birkaç çalışan temsilci oluşturabilirsiniz.

    Bununla birlikte, bunu daha çok **eğlenceli bir deney** olarak görmek en iyisidir. Token açısından ağırdır ve çoğu zaman
    ayrı oturumlarla tek bir bot kullanmaktan daha az verimlidir. Bizim tipik olarak
    öngördüğümüz model, paralel iş için farklı oturumlara sahip, konuştuğunuz tek bir bottur. Bu
    bot gerektiğinde alt temsilciler de başlatabilir.

    Belgeler: [Multi-agent routing](/tr/concepts/multi-agent), [Sub-agents](/tr/tools/subagents), [Agents CLI](/cli/agents).

  </Accordion>

  <Accordion title="Bağlam neden görevin ortasında kesildi? Bunu nasıl önlerim?">
    Oturum bağlamı model penceresiyle sınırlıdır. Uzun sohbetler, büyük araç çıktıları veya çok sayıda
    dosya sıkıştırma veya kesmeye yol açabilir.

    Yardımcı olanlar:

    - Bota mevcut durumu özetlemesini ve bir dosyaya yazmasını söyleyin.
    - Uzun görevlerden önce `/compact`, konu değiştirirken `/new` kullanın.
    - Önemli bağlamı çalışma alanında tutun ve bottan tekrar okumasını isteyin.
    - Ana sohbet daha küçük kalsın diye uzun veya paralel işler için alt temsilciler kullanın.
    - Bu sık oluyorsa daha büyük bağlam penceresine sahip bir model seçin.

  </Accordion>

  <Accordion title="OpenClaw'ı tamamen sıfırlayıp kurulu bırakmak istiyorum. Nasıl yaparım?">
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

    - İlk kurulum mevcut yapılandırma görürse **Reset** de sunar. Bkz. [Onboarding (CLI)](/tr/start/wizard).
    - Profiller kullandıysanız (`--profile` / `OPENCLAW_PROFILE`), her durum dizinini sıfırlayın (varsayılanlar `~/.openclaw-<profile>`).
    - Geliştirici sıfırlaması: `openclaw gateway --dev --reset` (yalnızca geliştirme; geliştirme yapılandırması + kimlik bilgileri + oturumlar + çalışma alanını siler).

  </Accordion>

  <Accordion title='Şu hatayı alıyorum: "context too large" - nasıl sıfırlar veya sıkıştırırım?'>
    Şunlardan birini kullanın:

    - **Sıkıştır** (konuşmayı korur ama eski dönüşleri özetler):

      ```
      /compact
      ```

      veya özeti yönlendirmek için `/compact <instructions>`.

    - **Sıfırla** (aynı sohbet anahtarı için taze oturum kimliği):

      ```
      /new
      /reset
      ```

    Bu olmaya devam ederse:

    - Eski araç çıktısını kırpmak için **oturum budamayı** (`agents.defaults.contextPruning`) etkinleştirin veya ayarlayın.
    - Daha büyük bağlam penceresine sahip bir model kullanın.

    Belgeler: [Compaction](/tr/concepts/compaction), [Session pruning](/tr/concepts/session-pruning), [Session management](/tr/concepts/session).

  </Accordion>

  <Accordion title='Neden şu hatayı görüyorum: "LLM request rejected: messages.content.tool_use.input field required"?'>
    Bu bir sağlayıcı doğrulama hatasıdır: model gerekli
    `input` olmadan `tool_use` bloğu üretti. Genellikle oturum geçmişinin eski veya bozuk olduğu anlamına gelir (çoğu zaman uzun iş parçacıklarından
    veya araç/şema değişikliğinden sonra).

    Çözüm: `/new` ile taze bir oturum başlatın (tek başına mesaj).

  </Accordion>

  <Accordion title="Neden her 30 dakikada bir heartbeat mesajı alıyorum?">
    Heartbeat'ler varsayılan olarak her **30 dakikada** (**OAuth auth kullanırken 1 saat**) çalışır. Ayarlayın veya devre dışı bırakın:

    ```json5
    {
      agents: {
        defaults: {
          heartbeat: {
            every: "2h", // devre dışı bırakmak için "0m"
          },
        },
      },
    }
    ```

    `HEARTBEAT.md` varsa ama fiilen boşsa (yalnızca boş satırlar ve
    `# Heading` gibi markdown başlıkları), OpenClaw API çağrılarını azaltmak için heartbeat çalıştırmasını atlar.
    Dosya eksikse heartbeat yine çalışır ve model ne yapacağına karar verir.

    Temsilci başına geçersiz kılmalar `agents.list[].heartbeat` kullanır. Belgeler: [Heartbeat](/tr/gateway/heartbeat).

  </Accordion>

  <Accordion title='WhatsApp grubuna bir "bot hesabı" eklemem gerekir mi?'>
    Hayır. OpenClaw **kendi hesabınızda** çalışır; dolayısıyla siz gruptaysanız OpenClaw da görebilir.
    Varsayılan olarak grup yanıtları, gönderenlere izin verene kadar engellenir (`groupPolicy: "allowlist"`).

    Grup yanıtlarını yalnızca **siz** tetikleyebilin istiyorsanız:

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
    Seçenek 1 (en hızlı): günlükleri izleyin ve grupta test mesajı gönderin:

    ```bash
    openclaw logs --follow --json
    ```

    `@g.us` ile biten `chatId` (veya `from`) değerini arayın, örneğin:
    `1234567890-1234567890@g.us`.

    Seçenek 2 (zaten yapılandırılmış/izin listesinde ise): yapılandırmadan grupları listeleyin:

    ```bash
    openclaw directory groups list --channel whatsapp
    ```

    Belgeler: [WhatsApp](/tr/channels/whatsapp), [Directory](/cli/directory), [Logs](/cli/logs).

  </Accordion>

  <Accordion title="OpenClaw neden grupta yanıt vermiyor?">
    İki yaygın neden:

    - Mention kapısı açık (varsayılan). Botu @mention etmelisiniz (veya `mentionPatterns` eşleşmeli).
    - `channels.whatsapp.groups` yapılandırdınız ama `"*"` yok ve grup izin listesinde değil.

    Bkz. [Groups](/tr/channels/groups) ve [Group messages](/tr/channels/group-messages).

  </Accordion>

  <Accordion title="Gruplar/iş parçacıkları DM'lerle bağlam paylaşır mı?">
    Doğrudan sohbetler varsayılan olarak ana oturuma çöker. Gruplar/kanalların kendi oturum anahtarları vardır ve Telegram konuları / Discord iş parçacıkları ayrı oturumlardır. Bkz. [Groups](/tr/channels/groups) ve [Group messages](/tr/channels/group-messages).
  </Accordion>

  <Accordion title="Kaç çalışma alanı ve temsilci oluşturabilirim?">
    Katı sınır yok. Onlarcası (hatta yüzlercesi) uygundur, ama şunlara dikkat edin:

    - **Disk büyümesi:** oturumlar + dökümler `~/.openclaw/agents/<agentId>/sessions/` altında yaşar.
    - **Token maliyeti:** daha fazla temsilci daha fazla eşzamanlı model kullanımı demektir.
    - **İşletim yükü:** temsilci başına auth profilleri, çalışma alanları ve kanal yönlendirmesi.

    İpuçları:

    - Temsilci başına bir **etkin** çalışma alanı tutun (`agents.defaults.workspace`).
    - Disk büyürse eski oturumları budayın (JSONL veya depo girdilerini silin).
    - Dağınık çalışma alanlarını ve profil uyuşmazlıklarını tespit etmek için `openclaw doctor` kullanın.

  </Accordion>

  <Accordion title="Birden fazla botu veya sohbeti aynı anda (Slack) çalıştırabilir miyim ve bunu nasıl kurmalıyım?">
    Evet. Birden fazla yalıtılmış temsilci çalıştırmak ve gelen mesajları
    kanal/hesap/eşe göre yönlendirmek için **Multi-Agent Routing** kullanın. Slack bir kanal olarak desteklenir ve belirli temsilcilere bağlanabilir.

    Tarayıcı erişimi güçlüdür ama "bir insanın yapabildiği her şeyi yapar" değildir - bot karşıtı önlemler, CAPTCHA'lar ve MFA
    otomasyonu yine de engelleyebilir. En güvenilir tarayıcı denetimi için ana bilgisayarda yerel Chrome MCP kullanın
    veya tarayıcıyı gerçekten çalıştıran makinede CDP kullanın.

    En iyi uygulama kurulumu:

    - Her zaman açık Gateway ana bilgisayarı (VPS/Mac mini).
    - Rol başına bir temsilci (bağlar).
    - Bu temsilcilere bağlı Slack kanal(lar)ı.
    - Gerektiğinde Chrome MCP veya bir node üzerinden yerel tarayıcı.

    Belgeler: [Multi-Agent Routing](/tr/concepts/multi-agent), [Slack](/tr/channels/slack),
    [Browser](/tr/tools/browser), [Nodes](/tr/nodes).

  </Accordion>
</AccordionGroup>

## Modeller: varsayılanlar, seçim, takma adlar, geçiş

<AccordionGroup>
  <Accordion title='"Varsayılan model" nedir?'>
    OpenClaw'ın varsayılan modeli, şurada ayarladığınız modeldir:

    ```
    agents.defaults.model.primary
    ```

    Modeller `provider/model` olarak başvurulur (örnek: `openai/gpt-5.4`). Sağlayıcıyı çıkarırsanız OpenClaw önce takma adı, sonra tam bu model kimliği için benzersiz yapılandırılmış sağlayıcı eşleşmesini dener ve ancak bundan sonra eski uyumluluk yolu olarak yapılandırılmış varsayılan sağlayıcıya geri döner. O sağlayıcı artık yapılandırılmış varsayılan modeli sunmuyorsa, eski kaldırılmış sağlayıcı varsayılanını yüzeye çıkarmak yerine ilk yapılandırılmış sağlayıcı/modele geri döner. Yine de **açıkça** `provider/model` ayarlamalısınız.

  </Accordion>

  <Accordion title="Hangi modeli öneriyorsunuz?">
    **Önerilen varsayılan:** sağlayıcı yığınınızda bulunan en güçlü son nesil modeli kullanın.
    **Araç etkin veya güvenilmeyen girdi alan temsilciler için:** maliyetten çok model gücüne öncelik verin.
    **Rutin/düşük riskli sohbetler için:** daha ucuz yedek modeller kullanın ve temsilci rolüne göre yönlendirin.

    MiniMax'in kendi belgeleri vardır: [MiniMax](/tr/providers/minimax) ve
    [Local models](/tr/gateway/local-models).

    Genel kural: yüksek riskli işler için karşılayabildiğiniz **en iyi modeli** kullanın ve rutin
    sohbetler veya özetler için daha ucuz bir model kullanın. Temsilci başına model yönlendirebilir ve uzun görevleri
    paralelleştirmek için alt temsilciler kullanabilirsiniz (her alt temsilci token tüketir). Bkz. [Models](/tr/concepts/models) ve
    [Sub-agents](/tr/tools/subagents).

    Güçlü uyarı: daha zayıf/aşırı kuantize modeller istem
    enjeksiyonuna ve güvensiz davranışa daha açıktır. Bkz. [Security](/tr/gateway/security).

    Daha fazla bağlam: [Models](/tr/concepts/models).

  </Accordion>

  <Accordion title="Yapılandırmamı silmeden modelleri nasıl değiştiririm?">
    **Model komutlarını** kullanın veya yalnızca **model** alanlarını düzenleyin. Tam yapılandırma değiştirmelerden kaçının.

    Güvenli seçenekler:

    - sohbette `/model` (hızlı, oturum başına)
    - `openclaw models set ...` (yalnızca model yapılandırmasını günceller)
    - `openclaw configure --section model` (etkileşimli)
    - `~/.openclaw/openclaw.json` içinde `agents.defaults.model` düzenleyin

    Tüm yapılandırmayı değiştirmeyi amaçlamıyorsanız kısmi nesne ile `config.apply` kullanmaktan kaçının.
    RPC düzenlemeleri için önce `config.schema.lookup` ile inceleyin ve `config.patch` tercih edin. Lookup yükü size normalize edilmiş yolu, sığ şema belgeleri/kısıtları ve anlık alt özetleri verir.
    kısmi güncellemeler için.
    Yapılandırmanın üzerine yazdıysanız yedekten geri yükleyin veya onarmak için `openclaw doctor` yeniden çalıştırın.

    Belgeler: [Models](/tr/concepts/models), [Configure](/cli/configure), [Config](/cli/config), [Doctor](/tr/gateway/doctor).

  </Accordion>

  <Accordion title="Kendi barındırdığım modelleri kullanabilir miyim (llama.cpp, vLLM, Ollama)?">
    Evet. Yerel modeller için en kolay yol Ollama'dır.

    En hızlı kurulum:

    1. Ollama'yı `https://ollama.com/download` adresinden kurun
    2. `ollama pull glm-4.7-flash` gibi bir yerel model çekin
    3. Bulut modellerini de istiyorsanız `ollama signin` çalıştırın
    4. `openclaw onboard` çalıştırın ve `Ollama` seçin
    5. `Local` veya `Cloud + Local` seçin

    Notlar:

    - `Cloud + Local` size bulut modellerini artı yerel Ollama modellerinizi verir
    - `kimi-k2.5:cloud` gibi bulut modelleri için yerel çekme gerekmez
    - elle geçiş için `openclaw models list` ve `openclaw models set ollama/<model>` kullanın

    Güvenlik notu: daha küçük veya yoğun kuantize edilmiş modeller istem
    enjeksiyonuna daha açıktır. Araç kullanabilen herhangi bir bot için
    **büyük modelleri** güçlü biçimde öneriyoruz.
    Yine de küçük modeller istiyorsanız sandboxing ve katı araç izin listelerini etkinleştirin.

    Belgeler: [Ollama](/tr/providers/ollama), [Local models](/tr/gateway/local-models),
    [Model providers](/tr/concepts/model-providers), [Security](/tr/gateway/security),
    [Sandboxing](/tr/gateway/sandboxing).

  </Accordion>

  <Accordion title="OpenClaw, Flawd ve Krill modeller için ne kullanıyor?">
    - Bu dağıtımlar farklı olabilir ve zamanla değişebilir; sabit bir sağlayıcı önerisi yoktur.
    - Her gateway'deki mevcut çalışma zamanı ayarını `openclaw models status` ile kontrol edin.
    - Güvenlik açısından hassas/araç etkin temsilciler için mevcut en güçlü son nesil modeli kullanın.
  </Accordion>

  <Accordion title="Modelleri yeniden başlatmadan anında nasıl değiştiririm?">
    `/model` komutunu tek başına mesaj olarak kullanın:

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

    İpucu: `/model status`, hangi temsilcinin etkin olduğunu, hangi `auth-profiles.json` dosyasının kullanıldığını ve sırada hangi auth profilinin deneneceğini gösterir.
    Ayrıca mevcut olduğunda yapılandırılmış sağlayıcı uç noktasını (`baseUrl`) ve API kipini (`api`) gösterir.

    **@profile ile ayarladığım sabitlemeyi nasıl kaldırırım?**

    `/model` komutunu `@profile` son eki **olmadan** yeniden çalıştırın:

    ```
    /model anthropic/claude-opus-4-6
    ```

    Varsayılana dönmek istiyorsanız `/model` içinden seçin (veya `/model <default provider/model>` gönderin).
    Hangi auth profilinin etkin olduğunu doğrulamak için `/model status` kullanın.

  </Accordion>

  <Accordion title="Günlük görevler için GPT 5.2 ve kodlama için Codex 5.3 kullanabilir miyim?">
    Evet. Birini varsayılan yapın, gerektiğinde geçin:

    - **Hızlı geçiş (oturum başına):** günlük görevler için `/model gpt-5.4`, Codex OAuth ile kodlama için `/model openai-codex/gpt-5.4`.
    - **Varsayılan + geçiş:** `agents.defaults.model.primary` değerini `openai/gpt-5.4` yapın, sonra kodlama yaparken `openai-codex/gpt-5.4`'e geçin (veya tersi).
    - **Alt temsilciler:** kodlama görevlerini farklı varsayılan modele sahip alt temsilcilere yönlendirin.

    Bkz. [Models](/tr/concepts/models) ve [Slash commands](/tr/tools/slash-commands).

  </Accordion>

  <Accordion title="GPT 5.4 için fast mode'u nasıl yapılandırırım?">
    Bir oturum anahtarı veya yapılandırma varsayılanı kullanın:

    - **Oturum başına:** oturum `openai/gpt-5.4` veya `openai-codex/gpt-5.4` kullanırken `/fast on` gönderin.
    - **Model başına varsayılan:** `agents.defaults.models["openai/gpt-5.4"].params.fastMode` değerini `true` ayarlayın.
    - **Codex OAuth için de:** `openai-codex/gpt-5.4` kullanıyorsanız aynı bayrağı orada da ayarlayın.

    Örnek:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "openai/gpt-5.4": {
              params: {
                fastMode: true,
              },
            },
            "openai-codex/gpt-5.4": {
              params: {
                fastMode: true,
              },
            },
          },
        },
      },
    }
    ```

    OpenAI için fast mode, desteklenen yerel Responses isteklerinde `service_tier = "priority"` ile eşleşir. Oturum `/fast` geçersiz kılmaları yapılandırma varsayılanlarını yener.

    Bkz. [Thinking and fast mode](/tr/tools/thinking) ve [OpenAI fast mode](/tr/providers/openai#openai-fast-mode).

  </Accordion>

  <Accordion title='Neden "Model ... is not allowed" görüyorum ve sonra yanıt gelmiyor?'>
    `agents.defaults.models` ayarlıysa bu, `/model` ve tüm
    oturum geçersiz kılmaları için **izin listesi** olur. Bu listede olmayan bir modeli seçmek şunu döndürür:

    ```
    Model "provider/model" is not allowed. Kullanılabilir modelleri listelemek için /model kullanın.
    ```

    Bu hata normal yanıtın **yerine** döndürülür. Çözüm: modeli
    `agents.defaults.models` içine ekleyin, izin listesini kaldırın veya `/model list` içinden bir model seçin.

  </Accordion>

  <Accordion title='Neden "Unknown model: minimax/MiniMax-M2.7"