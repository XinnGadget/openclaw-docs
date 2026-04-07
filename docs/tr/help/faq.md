---
read_when:
    - Yaygın kurulum, yükleme, onboarding veya çalışma zamanı destek sorularını yanıtlarken
    - Kullanıcı tarafından bildirilen sorunları daha derin hata ayıklamadan önce triyaj ederken
summary: OpenClaw kurulumu, yapılandırması ve kullanımı hakkında sık sorulan sorular
title: SSS
x-i18n:
    generated_at: "2026-04-07T08:50:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: bddcde55cf4bcec4913aadab4c665b235538104010e445e4c99915a1672b1148
    source_path: help/faq.md
    workflow: 15
---

# SSS

Gerçek dünya kurulumları için hızlı yanıtlar ve daha derin sorun giderme (yerel geliştirme, VPS, çok ajanlı kurulum, OAuth/API anahtarları, model devretme). Çalışma zamanı tanılaması için bkz. [Sorun giderme](/tr/gateway/troubleshooting). Tam yapılandırma başvurusu için bkz. [Yapılandırma](/tr/gateway/configuration).

## Bir şey bozuksa ilk 60 saniye

1. **Hızlı durum (ilk kontrol)**

   ```bash
   openclaw status
   ```

   Hızlı yerel özet: OS + güncelleme, gateway/hizmet erişilebilirliği, ajanlar/oturumlar, sağlayıcı yapılandırması + çalışma zamanı sorunları (gateway erişilebilirse).

2. **Paylaşması güvenli rapor**

   ```bash
   openclaw status --all
   ```

   Günlük sonuyla birlikte salt okunur tanılama (token'lar sansürlenmiş).

3. **Daemon + port durumu**

   ```bash
   openclaw gateway status
   ```

   Supervisor çalışma zamanı ile RPC erişilebilirliğini, probe hedef URL'sini ve hizmetin büyük olasılıkla hangi yapılandırmayı kullandığını gösterir.

4. **Derin problar**

   ```bash
   openclaw status --deep
   ```

   Desteklendiğinde kanal probları da dahil olmak üzere canlı bir gateway sağlık probu çalıştırır
   (erişilebilir bir gateway gerektirir). Bkz. [Sağlık](/tr/gateway/health).

5. **En son günlüğü izle**

   ```bash
   openclaw logs --follow
   ```

   RPC kapalıysa şuna geri dönün:

   ```bash
   tail -f "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)"
   ```

   Dosya günlükleri hizmet günlüklerinden ayrıdır; bkz. [Günlükleme](/tr/logging) ve [Sorun giderme](/tr/gateway/troubleshooting).

6. **Doctor'ı çalıştır (onarım)**

   ```bash
   openclaw doctor
   ```

   Yapılandırmayı/durumu onarır veya taşır + sağlık kontrolleri çalıştırır. Bkz. [Doctor](/tr/gateway/doctor).

7. **Gateway anlık görüntüsü**

   ```bash
   openclaw health --json
   openclaw health --verbose   # hatalarda hedef URL'yi + yapılandırma yolunu gösterir
   ```

   Çalışan gateway'den tam bir anlık görüntü ister (yalnızca WS). Bkz. [Sağlık](/tr/gateway/health).

## Hızlı başlangıç ve ilk çalıştırma kurulumu

<AccordionGroup>
  <Accordion title="Takıldım, takılmadan çıkmanın en hızlı yolu">
    Makinenizi **görebilen** yerel bir AI ajanı kullanın. Bu, Discord'da sormaktan çok daha etkilidir,
    çünkü "takıldım" durumlarının çoğu, uzak yardımcıların inceleyemeyeceği **yerel yapılandırma veya ortam sorunlarıdır**.

    - **Claude Code**: [https://www.anthropic.com/claude-code/](https://www.anthropic.com/claude-code/)
    - **OpenAI Codex**: [https://openai.com/codex/](https://openai.com/codex/)

    Bu araçlar depoyu okuyabilir, komut çalıştırabilir, günlükleri inceleyebilir ve makine düzeyindeki
    kurulumunuzu (PATH, hizmetler, izinler, kimlik doğrulama dosyaları) düzeltmenize yardımcı olabilir.
    Onlara hacklenebilir (git) kurulum üzerinden **tam kaynak checkout** verin:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Bu, OpenClaw'ı **bir git checkout'undan** yükler; böylece ajan kodu + belgeleri okuyabilir ve
    çalıştırdığınız tam sürümü değerlendirebilir. Daha sonra yükleyiciyi `--install-method git`
    olmadan yeniden çalıştırarak her zaman stable sürüme dönebilirsiniz.

    İpucu: ajandan düzeltmeyi **planlamasını ve denetlemesini** isteyin (adım adım), ardından
    yalnızca gerekli komutları yürütün. Bu, değişiklikleri küçük ve denetlenmesini kolay tutar.

    Gerçek bir hata veya düzeltme keşfederseniz lütfen bir GitHub issue açın veya bir PR gönderin:
    [https://github.com/openclaw/openclaw/issues](https://github.com/openclaw/openclaw/issues)
    [https://github.com/openclaw/openclaw/pulls](https://github.com/openclaw/openclaw/pulls)

    Şu komutlarla başlayın (yardım isterken çıktıları paylaşın):

    ```bash
    openclaw status
    openclaw models status
    openclaw doctor
    ```

    Bunların yaptıkları:

    - `openclaw status`: gateway/ajan sağlığı + temel yapılandırmanın hızlı anlık görüntüsü.
    - `openclaw models status`: sağlayıcı kimlik doğrulamasını + model kullanılabilirliğini denetler.
    - `openclaw doctor`: yaygın yapılandırma/durum sorunlarını doğrular ve onarır.

    Diğer yararlı CLI kontrolleri: `openclaw status --all`, `openclaw logs --follow`,
    `openclaw gateway status`, `openclaw health --verbose`.

    Hızlı hata ayıklama döngüsü: [Bir şey bozuksa ilk 60 saniye](#bir-şey-bozuksa-ilk-60-saniye).
    Kurulum belgeleri: [Yükleme](/tr/install), [Yükleyici bayrakları](/tr/install/installer), [Güncelleme](/tr/install/updating).

  </Accordion>

  <Accordion title="Heartbeat sürekli atlanıyor. Atlama nedenleri ne anlama geliyor?">
    Yaygın heartbeat atlama nedenleri:

    - `quiet-hours`: yapılandırılmış aktif saat aralığının dışında
    - `empty-heartbeat-file`: `HEARTBEAT.md` var ama yalnızca boş/yalnızca başlık iskeleti içeriyor
    - `no-tasks-due`: `HEARTBEAT.md` görev modu etkin ama görev aralıklarının hiçbiri henüz zamanı gelmemiş
    - `alerts-disabled`: tüm heartbeat görünürlüğü devre dışı (`showOk`, `showAlerts` ve `useIndicator` kapalı)

    Görev modunda, zamanı gelen zaman damgaları yalnızca gerçek bir heartbeat çalıştırması
    tamamlandıktan sonra ilerletilir. Atlanan çalıştırmalar görevleri tamamlanmış olarak işaretlemez.

    Belgeler: [Heartbeat](/tr/gateway/heartbeat), [Otomasyon ve Görevler](/tr/automation).

  </Accordion>

  <Accordion title="OpenClaw'ı yüklemek ve kurmak için önerilen yol">
    Depo, kaynaktan çalıştırmayı ve onboarding kullanmayı önerir:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash
    openclaw onboard --install-daemon
    ```

    Sihirbaz UI varlıklarını da otomatik olarak oluşturabilir. Onboarding sonrasında genellikle Gateway'i **18789** portunda çalıştırırsınız.

    Kaynaktan (katkıcılar/geliştiriciler):

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    pnpm ui:build # ilk çalıştırmada UI bağımlılıklarını otomatik yükler
    openclaw onboard
    ```

    Henüz genel bir kurulumunuz yoksa, bunu `pnpm openclaw onboard` ile çalıştırın.

  </Accordion>

  <Accordion title="Onboarding sonrasında panoyu nasıl açarım?">
    Sihirbaz, onboarding tamamlandıktan hemen sonra tarayıcınızı temiz (tokensız) bir pano URL'siyle açar ve bağlantıyı özette de yazdırır. O sekmeyi açık tutun; açılmadıysa aynı makinede yazdırılan URL'yi kopyalayıp yapıştırın.
  </Accordion>

  <Accordion title="Panoyu localhost'ta ve uzakta nasıl kimlik doğrularım?">
    **Localhost (aynı makine):**

    - `http://127.0.0.1:18789/` adresini açın.
    - Paylaşılan gizli anahtar kimlik doğrulaması isterse, yapılandırılmış token veya parolayı Control UI ayarlarına yapıştırın.
    - Token kaynağı: `gateway.auth.token` (veya `OPENCLAW_GATEWAY_TOKEN`).
    - Parola kaynağı: `gateway.auth.password` (veya `OPENCLAW_GATEWAY_PASSWORD`).
    - Henüz paylaşılan gizli anahtar yapılandırılmadıysa, `openclaw doctor --generate-gateway-token` ile bir token oluşturun.

    **Localhost dışında:**

    - **Tailscale Serve** (önerilen): bağlamayı loopback olarak bırakın, `openclaw gateway --tailscale serve` çalıştırın, `https://<magicdns>/` açın. `gateway.auth.allowTailscale` `true` ise kimlik üstbilgileri Control UI/WebSocket kimlik doğrulamasını karşılar (paylaşılan gizli anahtar yapıştırılmaz, güvenilen gateway ana makinesi varsayılır); HTTP API'leri ise bilinçli olarak private-ingress `none` veya trusted-proxy HTTP auth kullanmadığınız sürece yine paylaşılan gizli anahtar kimlik doğrulaması gerektirir.
      Aynı istemciden gelen hatalı eşzamanlı Serve kimlik doğrulama denemeleri, başarısız kimlik doğrulama sınırlayıcısı kaydı yazmadan önce seri hale getirilir; bu nedenle ikinci hatalı denemede bile `retry later` görünebilir.
    - **Tailnet bağlama**: `openclaw gateway --bind tailnet --token "<token>"` çalıştırın (veya parola kimlik doğrulamasını yapılandırın), `http://<tailscale-ip>:18789/` açın, ardından eşleşen paylaşılan gizli anahtarı pano ayarlarına yapıştırın.
    - **Kimlik farkındalıklı reverse proxy**: Gateway'i loopback olmayan güvenilen bir proxy arkasında tutun, `gateway.auth.mode: "trusted-proxy"` yapılandırın, ardından proxy URL'sini açın.
    - **SSH tüneli**: `ssh -N -L 18789:127.0.0.1:18789 user@host` sonra `http://127.0.0.1:18789/` açın. Tünel üzerinden de paylaşılan gizli anahtar kimlik doğrulaması geçerlidir; istenirse yapılandırılmış token veya parolayı yapıştırın.

    Bağlama modları ve kimlik doğrulama ayrıntıları için bkz. [Pano](/web/dashboard) ve [Web yüzeyleri](/web).

  </Accordion>

  <Accordion title="Sohbet onayları için neden iki exec onay yapılandırması var?">
    Bunlar farklı katmanları kontrol eder:

    - `approvals.exec`: onay istemlerini sohbet hedeflerine iletir
    - `channels.<channel>.execApprovals`: o kanalın exec onayları için yerel bir onay istemcisi gibi davranmasını sağlar

    Ana makine exec ilkesi hâlâ gerçek onay geçididir. Sohbet yapılandırması yalnızca onay
    istemlerinin nerede görüneceğini ve insanların nasıl yanıt verebileceğini kontrol eder.

    Çoğu kurulumda **ikisinin de** gerekli olması beklenmez:

    - Sohbet zaten komutları ve yanıtları destekliyorsa, aynı sohbette `/approve` paylaşılan yol üzerinden çalışır.
    - Desteklenen bir yerel kanal onay verenleri güvenli biçimde çıkarabiliyorsa, OpenClaw artık `channels.<channel>.execApprovals.enabled` ayarlanmamışsa veya `"auto"` ise DM-first yerel onayları otomatik etkinleştirir.
    - Yerel onay kartları/düğmeleri mevcut olduğunda, birincil yol bu yerel UI'dır; ajan yalnızca araç sonucu sohbet onaylarının kullanılamadığını veya tek yolun manuel onay olduğunu söylüyorsa manuel `/approve` komutunu eklemelidir.
    - `approvals.exec` yalnızca istemlerin başka sohbetlere veya açıkça belirtilmiş operasyon odalarına da iletilmesi gerekiyorsa kullanın.
    - `channels.<channel>.execApprovals.target: "channel"` veya `"both"` yalnızca onay istemlerinin kaynak oda/başlığa geri gönderilmesini açıkça istiyorsanız kullanın.
    - Eklenti onayları ayrı bir konudur: varsayılan olarak aynı sohbette `/approve` kullanırlar, isteğe bağlı `approvals.plugin` iletimi vardır ve yalnızca bazı yerel kanallar eklenti-onay-yerel işlemeyi bunun üstünde tutar.

    Kısa sürüm: iletme yönlendirme içindir, yerel istemci yapılandırması ise daha zengin kanala özgü UX içindir.
    Bkz. [Exec Onayları](/tr/tools/exec-approvals).

  </Accordion>

  <Accordion title="Hangi çalışma zamanına ihtiyacım var?">
    Node **>= 22** gereklidir. `pnpm` önerilir. Bun, Gateway için **önerilmez**.
  </Accordion>

  <Accordion title="Raspberry Pi'da çalışıyor mu?">
    Evet. Gateway hafiftir - belgelerde kişisel kullanım için **512MB-1GB RAM**, **1 çekirdek** ve yaklaşık **500MB**
    diskin yeterli olduğu, ayrıca **Raspberry Pi 4'ün bunu çalıştırabildiği** belirtilir.

    Ek boşluk istiyorsanız (günlükler, medya, diğer hizmetler), **2GB önerilir**, ancak bu
    katı bir alt sınır değildir.

    İpucu: küçük bir Pi/VPS Gateway'i barındırabilir ve yerel ekran/kamera/canvas veya komut yürütme için
    dizüstü telefonunuzda **node** eşleştirebilirsiniz. Bkz. [Nodes](/tr/nodes).

  </Accordion>

  <Accordion title="Raspberry Pi kurulumları için ipuçları var mı?">
    Kısa sürüm: çalışır, ancak pürüzler bekleyin.

    - **64 bit** bir OS kullanın ve Node'u >= 22 tutun.
    - Günlükleri görebilmek ve hızlı güncelleyebilmek için **hacklenebilir (git) kurulumunu** tercih edin.
    - Kanallar/Skills olmadan başlayın, sonra tek tek ekleyin.
    - Garip ikili sorunlarla karşılaşırsanız bu genellikle bir **ARM uyumluluğu** problemidir.

    Belgeler: [Linux](/tr/platforms/linux), [Yükleme](/tr/install).

  </Accordion>

  <Accordion title="wake up my friend ekranında kaldı / onboarding hatch olmuyor. Şimdi ne yapayım?">
    Bu ekran, Gateway'in erişilebilir ve kimliği doğrulanmış olmasına bağlıdır. TUI ayrıca
    ilk hatch sırasında otomatik olarak "Wake up, my friend!" gönderir. Bu satırı **yanıt olmadan**
    görüyorsanız ve token'lar 0'da kalıyorsa, ajan hiç çalışmamış demektir.

    1. Gateway'i yeniden başlatın:

    ```bash
    openclaw gateway restart
    ```

    2. Durumu + kimlik doğrulamayı kontrol edin:

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    3. Hâlâ takılı kalıyorsa şunu çalıştırın:

    ```bash
    openclaw doctor
    ```

    Gateway uzaktaysa, tünel/Tailscale bağlantısının çalıştığından ve UI'ın
    doğru Gateway'e yönlendirildiğinden emin olun. Bkz. [Uzak erişim](/tr/gateway/remote).

  </Accordion>

  <Accordion title="Kurulumu yeniden onboarding yapmadan yeni bir makineye (Mac mini) taşıyabilir miyim?">
    Evet. **Durum dizinini** ve **çalışma alanını** kopyalayın, sonra Doctor'ı bir kez çalıştırın. Bu,
    **her iki** konumu da kopyaladığınız sürece botunuzu "tam olarak aynı" (bellek, oturum geçmişi, kimlik doğrulama ve kanal
    durumu) tutar:

    1. Yeni makineye OpenClaw yükleyin.
    2. `$OPENCLAW_STATE_DIR` dizinini (varsayılan: `~/.openclaw`) eski makineden kopyalayın.
    3. Çalışma alanınızı kopyalayın (varsayılan: `~/.openclaw/workspace`).
    4. `openclaw doctor` çalıştırın ve Gateway hizmetini yeniden başlatın.

    Bu, yapılandırmayı, kimlik doğrulama profillerini, WhatsApp kimlik bilgilerini, oturumları ve belleği korur. Eğer
    uzak moddaysanız, gateway ana makinesinin oturum deposuna ve çalışma alanına sahip olduğunu unutmayın.

    **Önemli:** çalışma alanınızı yalnızca GitHub'a commit/push ederseniz,
    **bellek + bootstrap dosyalarınızı** yedekliyorsunuz demektir, ama **oturum geçmişini veya kimlik doğrulamayı değil**.
    Bunlar `~/.openclaw/` altında bulunur (örneğin `~/.openclaw/agents/<agentId>/sessions/`).

    İlgili: [Taşıma](/tr/install/migrating), [Diskte öğelerin bulunduğu yerler](#diskte-ögelerin-bulunduğu-yerler),
    [Ajan çalışma alanı](/tr/concepts/agent-workspace), [Doctor](/tr/gateway/doctor),
    [Uzak mod](/tr/gateway/remote).

  </Accordion>

  <Accordion title="En son sürümde neler yeni, bunu nerede görürüm?">
    GitHub changelog'una bakın:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    En yeni girişler üsttedir. Üst bölüm **Unreleased** olarak işaretliyse, sonraki tarihli
    bölüm son yayımlanan sürümdür. Girişler **Highlights**, **Changes** ve
    **Fixes** olarak gruplanır (gerektiğinde docs/other bölümleri ile birlikte).

  </Accordion>

  <Accordion title="docs.openclaw.ai erişilemiyor (SSL hatası)">
    Bazı Comcast/Xfinity bağlantıları `docs.openclaw.ai` adresini Xfinity
    Advanced Security üzerinden yanlış şekilde engelliyor. Bunu devre dışı bırakın veya `docs.openclaw.ai` için izin listesi oluşturun, ardından yeniden deneyin.
    Engelin kaldırılmasına yardımcı olmak için lütfen şurada bildirin: [https://spa.xfinity.com/check_url_status](https://spa.xfinity.com/check_url_status).

    Siteye hâlâ erişemiyorsanız, belgeler GitHub üzerinde yansılanmıştır:
    [https://github.com/openclaw/openclaw/tree/main/docs](https://github.com/openclaw/openclaw/tree/main/docs)

  </Accordion>

  <Accordion title="Stable ile beta arasındaki fark">
    **Stable** ve **beta**, ayrı kod hatları değil, **npm dist-tag**'leridir:

    - `latest` = stable
    - `beta` = test için erken derleme

    Genellikle stable bir sürüm önce **beta**'ya gelir, sonra açık bir
    yükseltme adımı aynı sürümü `latest`'e taşır. Bakımcılar gerektiğinde
    doğrudan `latest`'e de yayımlayabilir. Bu yüzden yükseltmeden sonra beta ve stable
    **aynı sürümü** işaret edebilir.

    Neyin değiştiğini görün:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    Tek satırlık kurulumlar ve beta ile dev arasındaki fark için aşağıdaki akordeona bakın.

  </Accordion>

  <Accordion title="Beta sürümü nasıl yüklerim ve beta ile dev arasındaki fark nedir?">
    **Beta**, npm dist-tag `beta`'dır (yükseltmeden sonra `latest` ile aynı olabilir).
    **Dev**, `main` dalının hareketli başıdır (git); yayımlandığında npm dist-tag `dev` kullanılır.

    Tek satırlık komutlar (macOS/Linux):

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --beta
    ```

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Windows yükleyicisi (PowerShell):
    [https://openclaw.ai/install.ps1](https://openclaw.ai/install.ps1)

    Daha fazla ayrıntı: [Geliştirme kanalları](/tr/install/development-channels) ve [Yükleyici bayrakları](/tr/install/installer).

  </Accordion>

  <Accordion title="En yeni bit'leri nasıl denerim?">
    İki seçenek var:

    1. **Dev kanalı (git checkout):**

    ```bash
    openclaw update --channel dev
    ```

    Bu, `main` dalına geçer ve kaynaktan günceller.

    2. **Hacklenebilir kurulum (yükleyici sitesinden):**

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Bu size düzenleyebileceğiniz yerel bir repo verir, sonra git ile güncelleyebilirsiniz.

    Temiz bir clone'u el ile tercih ederseniz, şunu kullanın:

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
    Yaklaşık kılavuz:

    - **Kurulum:** 2-5 dakika
    - **Onboarding:** yapılandırdığınız kanal/model sayısına bağlı olarak 5-15 dakika

    Takılı kalırsa [Yükleyici takıldı](#hızlı-başlangıç-ve-ilk-çalıştırma-kurulumu)
    ve [Takıldım](#hızlı-başlangıç-ve-ilk-çalıştırma-kurulumu) bölümündeki hızlı hata ayıklama döngüsünü kullanın.

  </Accordion>

  <Accordion title="Yükleyici takıldı mı? Nasıl daha fazla geri bildirim alırım?">
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

    Daha fazla seçenek: [Yükleyici bayrakları](/tr/install/installer).

  </Accordion>

  <Accordion title="Windows yüklemesinde git bulunamadı veya openclaw tanınmıyor diyor">
    İki yaygın Windows sorunu:

    **1) npm error spawn git / git not found**

    - **Git for Windows** yükleyin ve `git` komutunun PATH'inizde olduğundan emin olun.
    - PowerShell'i kapatıp yeniden açın, sonra yükleyiciyi yeniden çalıştırın.

    **2) Yükleme sonrası openclaw tanınmıyor**

    - npm global bin klasörünüz PATH'te değil.
    - Yolu kontrol edin:

      ```powershell
      npm config get prefix
      ```

    - O dizini kullanıcı PATH'inize ekleyin (Windows'ta `\bin` son eki gerekmez; çoğu sistemde `%AppData%\npm` olur).
    - PATH güncelledikten sonra PowerShell'i kapatıp yeniden açın.

    En sorunsuz Windows kurulumu için, yerel Windows yerine **WSL2** kullanın.
    Belgeler: [Windows](/tr/platforms/windows).

  </Accordion>

  <Accordion title="Windows exec çıktısında bozuk Çince metin görünüyor - ne yapmalıyım?">
    Bu genellikle yerel Windows shell'lerinde konsol kod sayfası uyuşmazlığıdır.

    Belirtiler:

    - `system.run`/`exec` çıktısı Çince'yi bozuk karakterlerle gösteriyor
    - Aynı komut başka bir terminal profilinde düzgün görünüyor

    PowerShell'de hızlı geçici çözüm:

    ```powershell
    chcp 65001
    [Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    ```

    Sonra Gateway'i yeniden başlatın ve komutu yeniden deneyin:

    ```powershell
    openclaw gateway restart
    ```

    Bunun en yeni OpenClaw sürümünde hâlâ tekrarlandığını görüyorsanız, şurada izleyin/bildirin:

    - [Issue #30640](https://github.com/openclaw/openclaw/issues/30640)

  </Accordion>

  <Accordion title="Belgeler sorumu yanıtlamadı - daha iyi bir yanıtı nasıl alırım?">
    Tam kaynak ve belgelere yerel olarak sahip olmak için **hacklenebilir (git) kurulum** kullanın, sonra
    botunuza (veya Claude/Codex'e) _o klasörden_ sorun ki depoyu okuyup tam yanıt verebilsin.

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Daha fazla ayrıntı: [Yükleme](/tr/install) ve [Yükleyici bayrakları](/tr/install/installer).

  </Accordion>

  <Accordion title="OpenClaw'ı Linux'a nasıl yüklerim?">
    Kısa yanıt: Linux kılavuzunu izleyin, sonra onboarding çalıştırın.

    - Linux hızlı yol + hizmet kurulumu: [Linux](/tr/platforms/linux).
    - Tam adım adım anlatım: [Başlarken](/tr/start/getting-started).
    - Yükleyici + güncellemeler: [Yükleme ve güncellemeler](/tr/install/updating).

  </Accordion>

  <Accordion title="OpenClaw'ı VPS'e nasıl yüklerim?">
    Herhangi bir Linux VPS çalışır. Sunucuya yükleyin, sonra Gateway'e erişmek için SSH/Tailscale kullanın.

    Kılavuzlar: [exe.dev](/tr/install/exe-dev), [Hetzner](/tr/install/hetzner), [Fly.io](/tr/install/fly).
    Uzak erişim: [Gateway remote](/tr/gateway/remote).

  </Accordion>

  <Accordion title="Bulut/VPS kurulum kılavuzları nerede?">
    Yaygın sağlayıcılar için bir **barındırma merkezi** tutuyoruz. Birini seçin ve kılavuzu izleyin:

    - [VPS barındırma](/tr/vps) (tüm sağlayıcılar tek yerde)
    - [Fly.io](/tr/install/fly)
    - [Hetzner](/tr/install/hetzner)
    - [exe.dev](/tr/install/exe-dev)

    Bulutta nasıl çalışır: **Gateway sunucuda çalışır**, siz de buna
    dizüstü/telefonunuzdan Control UI (veya Tailscale/SSH) ile erişirsiniz. Durumunuz + çalışma alanınız
    sunucuda yaşar, bu yüzden ana makineyi doğruluk kaynağı olarak görün ve yedekleyin.

    Buluttaki Gateway'i korurken yerel ekran/kamera/canvas erişmek veya
    dizüstünüzde komut çalıştırmak için o bulut Gateway'e **node** (Mac/iOS/Android/headless) eşleştirebilirsiniz.

    Merkez: [Platformlar](/tr/platforms). Uzak erişim: [Gateway remote](/tr/gateway/remote).
    Nodes: [Nodes](/tr/nodes), [Nodes CLI](/cli/nodes).

  </Accordion>

  <Accordion title="OpenClaw'dan kendini güncellemesini isteyebilir miyim?">
    Kısa yanıt: **mümkün, önerilmez**. Güncelleme akışı Gateway'i yeniden başlatabilir
    (bu da etkin oturumu düşürür), temiz bir git checkout gerekebilir ve
    onay isteyebilir. Daha güvenlisi: güncellemeleri operatör olarak shell'den çalıştırmak.

    CLI'ı kullanın:

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

    Belgeler: [Güncelleme](/cli/update), [Güncelleniyor](/tr/install/updating).

  </Accordion>

  <Accordion title="Onboarding aslında ne yapıyor?">
    `openclaw onboard` önerilen kurulum yoludur. **Yerel modda** size şunlarda rehberlik eder:

    - **Model/kimlik doğrulama kurulumu** (sağlayıcı OAuth, API anahtarları, Anthropic setup-token ve LM Studio gibi yerel model seçenekleri)
    - **Çalışma alanı** konumu + bootstrap dosyaları
    - **Gateway ayarları** (bind/port/auth/tailscale)
    - **Kanallar** (WhatsApp, Telegram, Discord, Mattermost, Signal, iMessage ve QQ Bot gibi paketle gelen kanal eklentileri)
    - **Daemon kurulumu** (macOS'te LaunchAgent; Linux/WSL2'de systemd user unit)
    - **Sağlık kontrolleri** ve **Skills** seçimi

    Ayrıca yapılandırdığınız model bilinmiyorsa veya kimlik doğrulaması eksikse uyarı verir.

  </Accordion>

  <Accordion title="Bunu çalıştırmak için Claude veya OpenAI aboneliğine ihtiyacım var mı?">
    Hayır. OpenClaw'ı **API anahtarlarıyla** (Anthropic/OpenAI/diğerleri) veya
    verileriniz cihazınızda kalsın diye **yalnızca yerel modellerle** çalıştırabilirsiniz. Abonelikler (Claude
    Pro/Max veya OpenAI Codex), bu sağlayıcılarda kimlik doğrulamak için isteğe bağlı yollardır.

    Anthropic için OpenClaw'da pratik ayrım şöyledir:

    - **Anthropic API anahtarı**: normal Anthropic API faturalaması
    - **OpenClaw'da Claude CLI / Claude abonelik kimlik doğrulaması**: Anthropic çalışanları
      bunun tekrar izinli olduğunu söylediler ve OpenClaw bu entegrasyon için
      Anthropic yeni bir ilke yayımlamadığı sürece `claude -p`
      kullanımını onaylı kabul ediyor

    Uzun ömürlü gateway ana makineleri için Anthropic API anahtarları hâlâ daha
    öngörülebilir kurulumdur. OpenAI Codex OAuth, OpenClaw gibi harici
    araçlar için açıkça desteklenir.

    OpenClaw ayrıca diğer barındırılan abonelik tarzı seçenekleri de destekler;
    buna **Qwen Cloud Coding Plan**, **MiniMax Coding Plan** ve
    **Z.AI / GLM Coding Plan** dahildir.

    Belgeler: [Anthropic](/tr/providers/anthropic), [OpenAI](/tr/providers/openai),
    [Qwen Cloud](/tr/providers/qwen),
    [MiniMax](/tr/providers/minimax), [GLM Models](/tr/providers/glm),
    [Yerel modeller](/tr/gateway/local-models), [Modeller](/tr/concepts/models).

  </Accordion>

  <Accordion title="Claude Max aboneliğini API anahtarı olmadan kullanabilir miyim?">
    Evet.

    Anthropic çalışanları OpenClaw tarzı Claude CLI kullanımının yeniden izinli olduğunu söyledi, bu yüzden
    OpenClaw Claude abonelik kimlik doğrulamasını ve `claude -p` kullanımını
    Anthropic yeni bir ilke yayımlamadığı sürece bu entegrasyon için onaylı kabul ediyor.
    En öngörülebilir sunucu tarafı kurulumu istiyorsanız bunun yerine bir Anthropic API anahtarı kullanın.

  </Accordion>

  <Accordion title="Claude abonelik kimlik doğrulamasını (Claude Pro veya Max) destekliyor musunuz?">
    Evet.

    Anthropic çalışanları bu kullanımın yeniden izinli olduğunu söylediler, bu yüzden OpenClaw
    Claude CLI yeniden kullanımını ve `claude -p` kullanımını
    Anthropic yeni bir ilke yayımlamadığı sürece bu entegrasyon için onaylı kabul ediyor.

    Anthropic setup-token, desteklenen bir OpenClaw token yolu olarak hâlâ kullanılabilir, ancak OpenClaw artık mümkün olduğunda Claude CLI yeniden kullanımını ve `claude -p` kullanımını tercih eder.
    Üretim veya çok kullanıcılı iş yükleri için Anthropic API anahtarı kimlik doğrulaması hâlâ
    daha güvenli ve öngörülebilir seçimdir. OpenClaw içinde başka barındırılan abonelik tarzı
    seçenekler isterseniz [OpenAI](/tr/providers/openai), [Qwen / Model
    Cloud](/tr/providers/qwen), [MiniMax](/tr/providers/minimax) ve [GLM
    Models](/tr/providers/glm) sayfalarına bakın.

  </Accordion>

<a id="why-am-i-seeing-http-429-ratelimiterror-from-anthropic"></a>
<Accordion title="Anthropic'ten neden HTTP 429 rate_limit_error görüyorum?">
Bu, geçerli pencere için **Anthropic kotanızın/hız sınırınızın** tükendiği anlamına gelir. **Claude CLI**
kullanıyorsanız pencerenin sıfırlanmasını bekleyin veya planınızı yükseltin. Bir
**Anthropic API anahtarı** kullanıyorsanız, kullanım/faturalandırma için Anthropic Console'u
kontrol edin ve gerekirse limitleri yükseltin.

    İleti özellikle şuysa:
    `Extra usage is required for long context requests`, istek
    Anthropic'in 1M bağlam betasını (`context1m: true`) kullanmaya çalışıyordur. Bu yalnızca
    kimlik bilginiz uzun bağlam faturalandırmasına uygunsa çalışır (API anahtarı faturalandırması veya
    Extra Usage etkin OpenClaw Claude-login yolu).

    İpucu: bir sağlayıcı hız sınırına takıldığında OpenClaw yanıt vermeye devam edebilsin diye bir **yedek model** ayarlayın.
    Bkz. [Modeller](/cli/models), [OAuth](/tr/concepts/oauth) ve
    [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/tr/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context).

  </Accordion>

  <Accordion title="AWS Bedrock destekleniyor mu?">
    Evet. OpenClaw'ın paketle gelen bir **Amazon Bedrock (Converse)** sağlayıcısı vardır. AWS ortam işaretçileri mevcut olduğunda OpenClaw akış/metin Bedrock kataloğunu otomatik keşfedebilir ve bunu örtük bir `amazon-bedrock` sağlayıcısı olarak birleştirebilir; aksi durumda `plugins.entries.amazon-bedrock.config.discovery.enabled` değerini açıkça etkinleştirebilir veya elle bir sağlayıcı girdisi ekleyebilirsiniz. Bkz. [Amazon Bedrock](/tr/providers/bedrock) ve [Model sağlayıcıları](/tr/providers/models). Yönetilen anahtar akışı tercih ederseniz, Bedrock önünde OpenAI uyumlu bir proxy kullanmak da geçerli bir seçenektir.
  </Accordion>

  <Accordion title="Codex kimlik doğrulaması nasıl çalışır?">
    OpenClaw, **OpenAI Code (Codex)** desteğini OAuth (ChatGPT oturum açma) üzerinden verir. Onboarding OAuth akışını çalıştırabilir ve uygun olduğunda varsayılan modeli `openai-codex/gpt-5.4` olarak ayarlar. Bkz. [Model sağlayıcıları](/tr/concepts/model-providers) ve [Onboarding (CLI)](/tr/start/wizard).
  </Accordion>

  <Accordion title="ChatGPT GPT-5.4 neden OpenClaw'da openai/gpt-5.4 yolunu açmıyor?">
    OpenClaw iki rotayı ayrı ele alır:

    - `openai-codex/gpt-5.4` = ChatGPT/Codex OAuth
    - `openai/gpt-5.4` = doğrudan OpenAI Platform API

    OpenClaw'da ChatGPT/Codex oturum açma, doğrudan `openai/*` rotasına değil
    `openai-codex/*` rotasına bağlanmıştır. OpenClaw'da doğrudan API yolunu
    istiyorsanız `OPENAI_API_KEY` ayarlayın (veya eşdeğer OpenAI sağlayıcı yapılandırması).
    OpenClaw'da ChatGPT/Codex oturum açma istiyorsanız `openai-codex/*` kullanın.

  </Accordion>

  <Accordion title="Codex OAuth limitleri neden ChatGPT web'den farklı olabilir?">
    `openai-codex/*`, Codex OAuth yolunu kullanır ve kullanılabilir kota pencereleri
    OpenAI tarafından yönetilir ve plana bağlıdır. Pratikte bu limitler,
    her ikisi de aynı hesaba bağlı olsa bile ChatGPT web sitesi/uygulama deneyiminden farklı olabilir.

    OpenClaw, şu anda görülebilen sağlayıcı kullanım/kota pencerelerini
    `openclaw models status` içinde gösterebilir, ancak ChatGPT-web
    haklarını doğrudan API erişimine uydurmaz veya normalleştirmez. Doğrudan OpenAI Platform
    faturalama/limit yolunu istiyorsanız, API anahtarıyla `openai/*` kullanın.

  </Accordion>

  <Accordion title="OpenAI abonelik kimlik doğrulamasını (Codex OAuth) destekliyor musunuz?">
    Evet. OpenClaw, **OpenAI Code (Codex) abonelik OAuth**'unu tamamen destekler.
    OpenAI, OpenClaw gibi harici araçlar/iş akışlarında
    abonelik OAuth kullanımına açıkça izin verir. Onboarding OAuth akışını sizin için çalıştırabilir.

    Bkz. [OAuth](/tr/concepts/oauth), [Model sağlayıcıları](/tr/concepts/model-providers) ve [Onboarding (CLI)](/tr/start/wizard).

  </Accordion>

  <Accordion title="Gemini CLI OAuth'u nasıl kurarım?">
    Gemini CLI, `openclaw.json` içinde client id veya secret değil,
    **eklenti kimlik doğrulama akışı** kullanır.

    Adımlar:

    1. `gemini` PATH üzerinde olacak şekilde Gemini CLI'ı yerel olarak yükleyin
       - Homebrew: `brew install gemini-cli`
       - npm: `npm install -g @google/gemini-cli`
    2. Eklentiyi etkinleştirin: `openclaw plugins enable google`
    3. Giriş yapın: `openclaw models auth login --provider google-gemini-cli --set-default`
    4. Giriş sonrası varsayılan model: `google-gemini-cli/gemini-3.1-pro-preview`
    5. İstekler başarısız olursa, gateway ana makinesinde `GOOGLE_CLOUD_PROJECT` veya `GOOGLE_CLOUD_PROJECT_ID` ayarlayın

    Bu, OAuth token'larını gateway ana makinesindeki kimlik doğrulama profillerinde saklar. Ayrıntılar: [Model sağlayıcıları](/tr/concepts/model-providers).

  </Accordion>

  <Accordion title="Günlük sohbetler için yerel model uygun mu?">
    Genellikle hayır. OpenClaw büyük bağlam + güçlü güvenlik gerektirir; küçük kartlar keser ve sızdırır. Mecbursanız,
    yerelde çalıştırabileceğiniz **en büyük** model derlemesini çalıştırın (LM Studio) ve [/gateway/local-models](/tr/gateway/local-models) sayfasına bakın. Daha küçük/kuantize modeller prompt injection riskini artırır - bkz. [Güvenlik](/tr/gateway/security).
  </Accordion>

  <Accordion title="Barındırılan model trafiğini belirli bir bölgede nasıl tutarım?">
    Bölgeye sabitlenmiş uç noktalar seçin. OpenRouter, MiniMax, Kimi ve GLM için ABD'de barındırılan seçenekler sunar; verileri bölgede tutmak için ABD'de barındırılan varyantı seçin. Seçtiğiniz bölgesel sağlayıcıya saygı gösterirken yedeklerin kullanılabilir kalması için `models.mode: "merge"` kullanarak Anthropic/OpenAI'yi bunların yanında listelemeye devam edebilirsiniz.
  </Accordion>

  <Accordion title="Bunu kurmak için Mac Mini satın almak zorunda mıyım?">
    Hayır. OpenClaw macOS veya Linux'ta çalışır (Windows'ta WSL2 üzerinden). Mac mini isteğe bağlıdır - bazı insanlar
    bunu her zaman açık bir ana makine olarak satın alır, ancak küçük bir VPS, ev sunucusu veya Raspberry Pi sınıfı bir cihaz da çalışır.

    **Yalnızca macOS araçları** için bir Mac gerekir. iMessage için [BlueBubbles](/tr/channels/bluebubbles) kullanın (önerilen) - BlueBubbles sunucusu herhangi bir Mac'te çalışır ve Gateway Linux'ta veya başka bir yerde olabilir. Diğer yalnızca macOS araçlarını istiyorsanız Gateway'i bir Mac'te çalıştırın veya bir macOS node eşleştirin.

    Belgeler: [BlueBubbles](/tr/channels/bluebubbles), [Nodes](/tr/nodes), [Mac remote mode](/tr/platforms/mac/remote).

  </Accordion>

  <Accordion title="iMessage desteği için Mac mini gerekli mi?">
    Messages hesabı açık bir **macOS cihazı** gerekir. Bunun Mac mini olması **gerekmez** -
    herhangi bir Mac olur. iMessage için **[BlueBubbles](/tr/channels/bluebubbles)** kullanın (önerilen) - BlueBubbles sunucusu macOS'te çalışırken Gateway Linux'ta veya başka bir yerde olabilir.

    Yaygın kurulumlar:

    - Gateway'i Linux/VPS'te çalıştırın ve BlueBubbles sunucusunu Messages oturumu açık herhangi bir Mac'te çalıştırın.
    - En basit tek makineli kurulum istiyorsanız her şeyi Mac üzerinde çalıştırın.

    Belgeler: [BlueBubbles](/tr/channels/bluebubbles), [Nodes](/tr/nodes),
    [Mac remote mode](/tr/platforms/mac/remote).

  </Accordion>

  <Accordion title="OpenClaw çalıştırmak için bir Mac mini alırsam, bunu MacBook Pro'ma bağlayabilir miyim?">
    Evet. **Mac mini Gateway'i çalıştırabilir**, MacBook Pro'nuz ise
    **node** (yardımcı cihaz) olarak bağlanabilir. Nodes Gateway çalıştırmaz -
    o cihazda ekran/kamera/canvas ve `system.run` gibi ek yetenekler sağlar.

    Yaygın desen:

    - Her zaman açık olan Mac mini üzerinde Gateway.
    - MacBook Pro, macOS uygulamasını veya bir node host çalıştırır ve Gateway ile eşleştirilir.
    - Görmek için `openclaw nodes status` / `openclaw nodes list` kullanın.

    Belgeler: [Nodes](/tr/nodes), [Nodes CLI](/cli/nodes).

  </Accordion>

  <Accordion title="Bun kullanabilir miyim?">
    Bun **önerilmez**. Özellikle WhatsApp ve Telegram ile çalışma zamanı hataları görüyoruz.
    Kararlı gateway'ler için **Node** kullanın.

    Yine de Bun ile deneme yapmak istiyorsanız bunu WhatsApp/Telegram olmayan,
    üretim dışı bir gateway üzerinde yapın.

  </Accordion>

  <Accordion title="Telegram: allowFrom içine ne girer?">
    `channels.telegram.allowFrom`, **insan gönderenin Telegram kullanıcı kimliğidir** (sayısal). Bot kullanıcı adı değildir.

    Onboarding `@username` girdisini kabul eder ve bunu sayısal kimliğe çözer, ancak OpenClaw yetkilendirmesi yalnızca sayısal kimlikleri kullanır.

    Daha güvenli (üçüncü taraf bot olmadan):

    - Botunuza DM atın, sonra `openclaw logs --follow` çalıştırın ve `from.id` değerini okuyun.

    Resmi Bot API:

    - Botunuza DM atın, sonra `https://api.telegram.org/bot<bot_token>/getUpdates` çağırın ve `message.from.id` okuyun.

    Üçüncü taraf (daha az gizli):

    - `@userinfobot` veya `@getidsbot`'a DM atın.

    Bkz. [/channels/telegram](/tr/channels/telegram#access-control-and-activation).

  </Accordion>

  <Accordion title="Birden fazla kişi tek WhatsApp numarasını farklı OpenClaw örnekleriyle kullanabilir mi?">
    Evet, **çok ajanlı yönlendirme** ile. Her gönderenin WhatsApp **DM**'sini (eş `kind: "direct"`, gönderen E.164 örneğin `+15551234567`) farklı bir `agentId`'ye bağlayın; böylece her kişi kendi çalışma alanına ve oturum deposuna sahip olur. Yanıtlar yine **aynı WhatsApp hesabından** gelir ve DM erişim denetimi (`channels.whatsapp.dmPolicy` / `channels.whatsapp.allowFrom`) her WhatsApp hesabı için geneldir. Bkz. [Çok Ajanlı Yönlendirme](/tr/concepts/multi-agent) ve [WhatsApp](/tr/channels/whatsapp).
  </Accordion>

  <Accordion title='Bir "hızlı sohbet" ajanı ve bir "kodlama için Opus" ajanı çalıştırabilir miyim?'>
    Evet. Çok ajanlı yönlendirme kullanın: her ajana kendi varsayılan modelini verin, sonra gelen rotaları (sağlayıcı hesabı veya belirli eşler) her ajana bağlayın. Örnek yapılandırma [Çok Ajanlı Yönlendirme](/tr/concepts/multi-agent) içinde yer alır. Ayrıca bkz. [Modeller](/tr/concepts/models) ve [Yapılandırma](/tr/gateway/configuration).
  </Accordion>

  <Accordion title="Homebrew Linux'ta çalışır mı?">
    Evet. Homebrew Linux'u destekler (Linuxbrew). Hızlı kurulum:

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew install <formula>
    ```

    OpenClaw'ı systemd üzerinden çalıştırıyorsanız, login olmayan shell'lerde `brew` ile yüklenen araçlar çözümlensin diye hizmet PATH'inin `/home/linuxbrew/.linuxbrew/bin` (veya brew ön ekiniz) içerdiğinden emin olun.
    Son derlemeler ayrıca Linux systemd hizmetlerinde yaygın kullanıcı bin dizinlerini (`~/.local/bin`, `~/.npm-global/bin`, `~/.local/share/pnpm`, `~/.bun/bin` gibi) başa ekler ve ayarlıysa `PNPM_HOME`, `NPM_CONFIG_PREFIX`, `BUN_INSTALL`, `VOLTA_HOME`, `ASDF_DATA_DIR`, `NVM_DIR` ve `FNM_DIR` değerlerine uyar.

  </Accordion>

  <Accordion title="Hacklenebilir git kurulumu ile npm install arasındaki fark">
    - **Hacklenebilir (git) kurulum:** tam kaynak checkout, düzenlenebilir, katkıcılar için en iyisi.
      Derlemeleri yerelde çalıştırırsınız ve kod/belge yaması yapabilirsiniz.
    - **npm install:** genel CLI kurulumu, repo yok, "sadece çalıştırmak" için en iyisi.
      Güncellemeler npm dist-tag'lerinden gelir.

    Belgeler: [Başlarken](/tr/start/getting-started), [Güncelleniyor](/tr/install/updating).

  </Accordion>

  <Accordion title="Daha sonra npm ve git kurulumları arasında geçiş yapabilir miyim?">
    Evet. Diğer kurulumu yapın, sonra gateway hizmeti yeni giriş noktasını işaret etsin diye Doctor'ı çalıştırın.
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

    git'ten npm'e:

    ```bash
    npm install -g openclaw@latest
    openclaw doctor
    openclaw gateway restart
    ```

    Doctor, gateway hizmet giriş noktası uyuşmazlığını algılar ve hizmet yapılandırmasını geçerli kuruluma uyacak şekilde yeniden yazmayı teklif eder (otomasyonda `--repair` kullanın).

    Yedekleme ipuçları: bkz. [Yedekleme stratejisi](#diskte-ögelerin-bulunduğu-yerler).

  </Accordion>

  <Accordion title="Gateway'i dizüstümde mi yoksa VPS'te mi çalıştırmalıyım?">
    Kısa yanıt: **7/24 güvenilirlik istiyorsanız VPS kullanın**. En düşük sürtünmeyi istiyorsanız
    ve uyku/yeniden başlatmalar sizin için sorun değilse yerelde çalıştırın.

    **Dizüstü (yerel Gateway)**

    - **Artıları:** sunucu maliyeti yok, yerel dosyalara doğrudan erişim, canlı tarayıcı penceresi.
    - **Eksileri:** uyku/ağ kesintileri = bağlantı kopmaları, OS güncellemeleri/yeniden başlatmalar kesinti yaratır, uyanık kalması gerekir.

    **VPS / bulut**

    - **Artıları:** her zaman açık, kararlı ağ, dizüstü uyku sorunları yok, çalışır halde tutmak daha kolay.
    - **Eksileri:** genelde headless çalışır (ekran görüntüleri kullanın), yalnızca uzak dosya erişimi vardır, güncellemeler için SSH gerekir.

    **OpenClaw'a özgü not:** WhatsApp/Telegram/Slack/Mattermost/Discord'un hepsi VPS üzerinde gayet iyi çalışır. Tek gerçek ödünleşim **headless tarayıcı** ile görünür pencere arasındadır. Bkz. [Tarayıcı](/tr/tools/browser).

    **Önerilen varsayılan:** daha önce gateway bağlantı kopmaları yaşadıysanız VPS. Mac'i aktif kullanırken ve yerel dosya erişimi veya görünür tarayıcıyla UI otomasyonu istediğinizde yerel kullanım harikadır.

  </Accordion>

  <Accordion title="OpenClaw'ı özel bir makinede çalıştırmak ne kadar önemli?">
    Zorunlu değil, ama **güvenilirlik ve yalıtım için önerilir**.

    - **Özel ana makine (VPS/Mac mini/Pi):** her zaman açık, daha az uyku/yeniden başlatma kesintisi, daha temiz izinler, çalışır halde tutmak daha kolay.
    - **Paylaşılan dizüstü/masaüstü:** test ve aktif kullanım için tamamen uygundur, ancak makine uyuduğunda veya güncellendiğinde duraklamalar bekleyin.

    Her iki dünyanın en iyisini istiyorsanız Gateway'i özel ana makinede tutun ve yerel ekran/kamera/exec araçları için dizüstünüzü **node** olarak eşleştirin. Bkz. [Nodes](/tr/nodes).
    Güvenlik kılavuzu için [Güvenlik](/tr/gateway/security) sayfasını okuyun.

  </Accordion>

  <Accordion title="Minimum VPS gereksinimleri ve önerilen OS nedir?">
    OpenClaw hafiftir. Temel bir Gateway + bir sohbet kanalı için:

    - **Mutlak minimum:** 1 vCPU, 1GB RAM, ~500MB disk.
    - **Önerilen:** boşluk için 1-2 vCPU, 2GB RAM veya daha fazlası (günlükler, medya, birden çok kanal). Node araçları ve tarayıcı otomasyonu kaynak tüketebilir.

    OS: **Ubuntu LTS** kullanın (veya herhangi bir modern Debian/Ubuntu). Linux kurulum yolu en iyi orada test edilmiştir.

    Belgeler: [Linux](/tr/platforms/linux), [VPS barındırma](/tr/vps).

  </Accordion>

  <Accordion title="OpenClaw'ı bir VM içinde çalıştırabilir miyim ve gereksinimler nelerdir?">
    Evet. Bir VM'yi VPS ile aynı şekilde değerlendirin: her zaman açık olmalı, erişilebilir olmalı ve
    Gateway ile etkinleştirdiğiniz kanallar için yeterli RAM'e sahip olmalıdır.

    Temel kılavuz:

    - **Mutlak minimum:** 1 vCPU, 1GB RAM.
    - **Önerilen:** birden çok kanal, tarayıcı otomasyonu veya medya araçları çalıştırıyorsanız 2GB RAM veya daha fazlası.
    - **OS:** Ubuntu LTS veya başka bir modern Debian/Ubuntu.

    Windows kullanıyorsanız **WSL2 en kolay VM tarzı kurulumdur** ve en iyi araç
    uyumluluğuna sahiptir. Bkz. [Windows](/tr/platforms/windows), [VPS barındırma](/tr/vps).
    macOS'i bir VM içinde çalıştırıyorsanız bkz. [macOS VM](/tr/install/macos-vm).

  </Accordion>
</AccordionGroup>

## OpenClaw nedir?

<AccordionGroup>
  <Accordion title="OpenClaw tek paragrafta nedir?">
    OpenClaw, kendi cihazlarınızda çalıştırdığınız kişisel bir AI asistandır. Zaten kullandığınız mesajlaşma yüzeylerinde (WhatsApp, Telegram, Slack, Mattermost, Discord, Google Chat, Signal, iMessage, WebChat ve QQ Bot gibi paketle gelen kanal eklentileri) yanıt verir ve desteklenen platformlarda ses + canlı Canvas da sunabilir. **Gateway** her zaman açık kontrol düzlemidir; ürün ise asistandır.
  </Accordion>

  <Accordion title="Değer önerisi">
    OpenClaw "sadece bir Claude sarmalayıcısı" değildir. Kendi donanımınızda
    çalıştırabildiğiniz, zaten kullandığınız sohbet uygulamalarından erişilebilen, durum tutan
    oturumlara, belleğe ve araçlara sahip güçlü bir asistan sunan **local-first kontrol düzlemidir** -
    iş akışlarınızın kontrolünü barındırılan bir SaaS'e teslim etmeden.

    Öne çıkanlar:

    - **Sizin cihazlarınız, sizin verileriniz:** Gateway'i istediğiniz yerde çalıştırın (Mac, Linux, VPS) ve
      çalışma alanını + oturum geçmişini yerelde tutun.
    - **Web sandbox'u değil, gerçek kanallar:** WhatsApp/Telegram/Slack/Discord/Signal/iMessage/vb.,
      ayrıca desteklenen platformlarda mobil ses ve Canvas.
    - **Modelden bağımsız:** Anthropic, OpenAI, MiniMax, OpenRouter vb. kullanın; ajan başına yönlendirme
      ve devretme ile.
    - **Yalnızca yerel seçenek:** isterseniz **tüm veriler cihazınızda kalsın** diye yerel modeller çalıştırın.
    - **Çok ajanlı yönlendirme:** kanal, hesap veya görev başına ayrı ajanlar; her birinin kendi
      çalışma alanı ve varsayılanları vardır.
    - **Açık kaynak ve hacklenebilir:** sağlayıcıya kilitlenmeden inceleyin, genişletin ve kendi kendinize barındırın.

    Belgeler: [Gateway](/tr/gateway), [Kanallar](/tr/channels), [Çok ajanlı](/tr/concepts/multi-agent),
    [Bellek](/tr/concepts/memory).

  </Accordion>

  <Accordion title="Kurulumu yeni yaptım - önce ne yapmalıyım?">
    İyi ilk projeler:

    - Bir web sitesi oluşturun (WordPress, Shopify veya basit bir statik site).
    - Bir mobil uygulama prototipi hazırlayın (taslak, ekranlar, API planı).
    - Dosya ve klasörleri düzenleyin (temizlik, adlandırma, etiketleme).
    - Gmail'i bağlayın ve özetleri veya takipleri otomatikleştirin.

    Büyük görevleri de ele alabilir, ancak bunları aşamalara böldüğünüzde ve
    paralel iş için alt ajanlar kullandığınızda en iyi çalışır.

  </Accordion>

  <Accordion title="OpenClaw için günlük hayattaki en iyi beş kullanım alanı nedir?">
    Günlük kazanımlar genelde şuna benzer:

    - **Kişisel bilgilendirmeler:** gelen kutusu, takvim ve önemsediğiniz haberlerin özetleri.
    - **Araştırma ve taslak yazımı:** hızlı araştırma, özetler ve e-posta veya belgeler için ilk taslaklar.
    - **Hatırlatmalar ve takipler:** cron veya heartbeat ile çalışan dürtmeler ve kontrol listeleri.
    - **Tarayıcı otomasyonu:** form doldurma, veri toplama ve web görevlerini tekrarlama.
    - **Cihazlar arası koordinasyon:** telefonunuzdan görev gönderin, Gateway bunu bir sunucuda çalıştırsın ve sonucu sohbete geri getirsin.

  </Accordion>

  <Accordion title="OpenClaw, bir SaaS için lead gen, outreach, reklamlar ve bloglar konusunda yardımcı olabilir mi?">
    **Araştırma, nitelendirme ve taslak hazırlama** için evet. Siteleri tarayabilir, kısa listeler oluşturabilir,
    potansiyel müşterileri özetleyebilir ve outreach veya reklam metni taslakları yazabilir.

    **Outreach veya reklam çalıştırmaları** için insanı döngüde tutun. Spam'den kaçının, yerel yasalara ve
    platform politikalarına uyun ve gönderilmeden önce her şeyi gözden geçirin. En güvenli desen,
    OpenClaw'ın taslak hazırlaması ve sizin onaylamanızdır.

    Belgeler: [Güvenlik](/tr/gateway/security).

  </Accordion>

  <Accordion title="Web geliştirme için Claude Code'a kıyasla avantajları nelerdir?">
    OpenClaw bir **kişisel asistan** ve koordinasyon katmanıdır, IDE'nin yerine geçmez.
    Bir repo içinde en hızlı doğrudan kodlama döngüsü için Claude Code veya Codex kullanın. Kalıcı
    bellek, cihazlar arası erişim ve araç orkestrasyonu istediğinizde OpenClaw kullanın.

    Avantajlar:

    - Oturumlar arasında **kalıcı bellek + çalışma alanı**
    - **Çok platformlu erişim** (WhatsApp, Telegram, TUI, WebChat)
    - **Araç orkestrasyonu** (tarayıcı, dosyalar, planlama, hooks)
    - **Her zaman açık Gateway** (bir VPS'te çalıştırın, her yerden etkileşim kurun)
    - Yerel tarayıcı/ekran/kamera/exec için **nodes**

    Vitrin: [https://openclaw.ai/showcase](https://openclaw.ai/showcase)

  </Accordion>
</AccordionGroup>

## Skills ve otomasyon

<AccordionGroup>
  <Accordion title="Depoyu kirli tutmadan Skills'i nasıl özelleştiririm?">
    Repo kopyasını düzenlemek yerine yönetilen geçersiz kılmaları kullanın. Değişikliklerinizi `~/.openclaw/skills/<name>/SKILL.md` içine koyun (veya `~/.openclaw/openclaw.json` içinde `skills.load.extraDirs` ile bir klasör ekleyin). Öncelik sırası `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → paketle gelen → `skills.load.extraDirs` olduğundan, yönetilen geçersiz kılmalar git'e dokunmadan paketle gelen skills'i yine de ezer. Skill'in genel olarak kurulu olmasını ama yalnızca bazı ajanlar tarafından görünmesini istiyorsanız paylaşılan kopyayı `~/.openclaw/skills` altında tutun ve görünürlüğü `agents.defaults.skills` ve `agents.list[].skills` ile kontrol edin. Yalnızca upstream'e uygun düzenlemeler depoda yaşamalı ve PR olarak gönderilmelidir.
  </Accordion>

  <Accordion title="Skills'i özel bir klasörden yükleyebilir miyim?">
    Evet. `~/.openclaw/openclaw.json` içinde `skills.load.extraDirs` ile ek dizinler ekleyin (en düşük öncelik). Varsayılan öncelik sırası `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → paketle gelen → `skills.load.extraDirs`. `clawhub` varsayılan olarak `./skills` içine kurar; OpenClaw bunu bir sonraki oturumda `<workspace>/skills` olarak ele alır. Skill'in yalnızca belirli ajanlara görünmesi gerekiyorsa bunu `agents.defaults.skills` veya `agents.list[].skills` ile eşleştirin.
  </Accordion>

  <Accordion title="Farklı görevler için farklı modelleri nasıl kullanabilirim?">
    Bugün desteklenen desenler şunlardır:

    - **Cron işleri**: yalıtılmış işler iş başına bir `model` geçersiz kılması ayarlayabilir.
    - **Alt ajanlar**: görevleri farklı varsayılan modellere sahip ayrı ajanlara yönlendirin.
    - **İsteğe bağlı geçiş**: geçerli oturum modelini istediğiniz zaman değiştirmek için `/model` kullanın.

    Bkz. [Cron işleri](/tr/automation/cron-jobs), [Çok Ajanlı Yönlendirme](/tr/concepts/multi-agent) ve [Slash komutları](/tr/tools/slash-commands).

  </Accordion>

  <Accordion title="Bot ağır iş yaparken donuyor. Bunu nasıl devrederim?">
    Uzun veya paralel görevler için **alt ajanlar** kullanın. Alt ajanlar kendi oturumlarında çalışır,
    bir özet döndürür ve ana sohbetinizi yanıt verebilir halde tutar.

    Botunuza "bu görev için bir alt ajan oluştur" deyin veya `/subagents` kullanın.
    Gateway'in şu anda ne yaptığını (ve meşgul olup olmadığını) görmek için sohbette `/status` kullanın.

    Token ipucu: uzun görevler ve alt ajanlar da token tüketir. Maliyet önemliyse,
    alt ajanlar için `agents.defaults.subagents.model` üzerinden daha ucuz bir model ayarlayın.

    Belgeler: [Alt ajanlar](/tr/tools/subagents), [Arka Plan Görevleri](/tr/automation/tasks).

  </Accordion>

  <Accordion title="Discord'da thread'e bağlı subagent oturumları nasıl çalışır?">
    Thread bağlamalarını kullanın. Bir Discord thread'ini bir subagent'e veya oturum hedefine bağlayabilirsiniz; böylece o thread içindeki takip mesajları bağlı oturumda kalır.

    Temel akış:

    - `sessions_spawn` ile `thread: true` kullanarak oluşturun (ve isteğe bağlı olarak kalıcı takip için `mode: "session"`).
    - Veya `/focus <target>` ile el ile bağlayın.
    - Bağlama durumunu incelemek için `/agents` kullanın.
    - Otomatik odağı kaldırmayı kontrol etmek için `/session idle <duration|off>` ve `/session max-age <duration|off>` kullanın.
    - Thread'i ayırmak için `/unfocus` kullanın.

    Gerekli yapılandırma:

    - Genel varsayılanlar: `session.threadBindings.enabled`, `session.threadBindings.idleHours`, `session.threadBindings.maxAgeHours`.
    - Discord geçersiz kılmaları: `channels.discord.threadBindings.enabled`, `channels.discord.threadBindings.idleHours`, `channels.discord.threadBindings.maxAgeHours`.
    - Spawn sırasında otomatik bağlama: `channels.discord.threadBindings.spawnSubagentSessions: true` ayarlayın.

    Belgeler: [Alt ajanlar](/tr/tools/subagents), [Discord](/tr/channels/discord), [Yapılandırma Başvurusu](/tr/gateway/configuration-reference), [Slash komutları](/tr/tools/slash-commands).

  </Accordion>

  <Accordion title="Bir subagent bitti, ama tamamlanma güncellemesi yanlış yere gitti veya hiç gönderilmedi. Neyi kontrol etmeliyim?">
    Önce çözümlenen istek sahibinin rotasını kontrol edin:

    - Tamamlama modundaki subagent teslimatı, varsa herhangi bir bağlı thread veya konuşma rotasını tercih eder.
    - Tamamlanma kaynağı yalnızca bir kanal taşıyorsa, doğrudan teslimat yine başarılı olabilsin diye OpenClaw istek sahibi oturumunun kayıtlı rotasına (`lastChannel` / `lastTo` / `lastAccountId`) geri döner.
    - Ne bağlı rota ne de kullanılabilir kayıtlı rota varsa, doğrudan teslimat başarısız olabilir ve sonuç sohbete hemen gönderilmek yerine sıraya alınmış oturum teslimatına geri düşer.
    - Geçersiz veya bayat hedefler yine sıraya geri düşmeye veya son teslimat hatasına neden olabilir.
    - Çocuğun son görünür asistan yanıtı tam olarak sessiz token `NO_REPLY` / `no_reply` veya tam olarak `ANNOUNCE_SKIP` ise, OpenClaw bayat önceki ilerlemeyi göndermek yerine duyuruyu bilinçli olarak bastırır.
    - Çocuk yalnızca araç çağrılarından sonra zaman aşımına uğradıysa, duyuru ham araç çıktısını yeniden oynatmak yerine bunu kısa bir kısmi ilerleme özeti haline getirebilir.

    Hata ayıklama:

    ```bash
    openclaw tasks show <runId-or-sessionKey>
    ```

    Belgeler: [Alt ajanlar](/tr/tools/subagents), [Arka Plan Görevleri](/tr/automation/tasks), [Oturum Araçları](/tr/concepts/session-tool).

  </Accordion>

  <Accordion title="Cron veya hatırlatmalar çalışmıyor. Neyi kontrol etmeliyim?">
    Cron, Gateway süreci içinde çalışır. Gateway sürekli çalışmıyorsa
    zamanlanmış işler de çalışmaz.

    Kontrol listesi:

    - Cron'un etkin olduğunu (`cron.enabled`) ve `OPENCLAW_SKIP_CRON` ayarlı olmadığını doğrulayın.
    - Gateway'in 7/24 çalıştığını kontrol edin (uyku/yeniden başlatma yok).
    - İşin zaman dilimi ayarlarını doğrulayın (`--tz` ile ana makine zaman dilimi).

    Hata ayıklama:

    ```bash
    openclaw cron run <jobId>
    openclaw cron runs --id <jobId> --limit 50
    ```

    Belgeler: [Cron işleri](/tr/automation/cron-jobs), [Otomasyon ve Görevler](/tr/automation).

  </Accordion>

  <Accordion title="Cron tetiklendi ama kanala hiçbir şey gönderilmedi. Neden?">
    Önce teslimat modunu kontrol edin:

    - `--no-deliver` / `delivery.mode: "none"` dış mesaj beklenmediği anlamına gelir.
    - Eksik veya geçersiz duyuru hedefi (`channel` / `to`) çalıştırıcının giden teslimatı atladığı anlamına gelir.
    - Kanal kimlik doğrulama hataları (`unauthorized`, `Forbidden`) çalıştırıcının teslim etmeyi denediğini ama kimlik bilgilerinin engellediğini gösterir.
    - Sessiz yalıtılmış sonuç (`NO_REPLY` / `no_reply` yalnızca) bilinçli olarak teslim edilemez sayılır; bu yüzden çalıştırıcı sıraya alınmış yedek teslimatı da bastırır.

    Yalıtılmış cron işleri için son teslimatın sahibi çalıştırıcıdır. Ajanın
    çalıştırıcının göndermesi için düz metin bir özet döndürmesi beklenir. `--no-deliver`
    bu sonucu içsel tutar; ajanın onun yerine message aracıyla
    doğrudan göndermesine izin vermez.

    Hata ayıklama:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    Belgeler: [Cron işleri](/tr/automation/cron-jobs), [Arka Plan Görevleri](/tr/automation/tasks).

  </Accordion>

  <Accordion title="Yalıtılmış bir cron çalıştırması neden model değiştirdi veya bir kez yeniden denedi?">
    Bu genellikle yinelenen zamanlama değil, canlı model değiştirme yoludur.

    Yalıtılmış cron, etkin çalıştırma `LiveSessionModelSwitchError` attığında
    çalışma zamanı model devrini kalıcılaştırabilir ve yeniden deneyebilir. Yeniden deneme,
    değiştirilen sağlayıcıyı/modeli korur ve geçiş yeni bir kimlik doğrulama profili geçersiz kılması taşıyorsa
    cron bunu da yeniden denemeden önce kalıcılaştırır.

    İlgili seçim kuralları:

    - Uygunsa Gmail hook model geçersiz kılması önce kazanır.
    - Sonra iş başına `model`.
    - Sonra kayıtlı herhangi bir cron-oturum modeli geçersiz kılması.
    - Sonra normal ajan/varsayılan model seçimi.

    Yeniden deneme döngüsü sınırlıdır. İlk deneme artı 2 geçiş yeniden denemesinden sonra
    cron sonsuza kadar döngüye girmek yerine durur.

    Hata ayıklama:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    Belgeler: [Cron işleri](/tr/automation/cron-jobs), [cron CLI](/cli/cron).

  </Accordion>

  <Accordion title="Skills'i Linux'ta nasıl yüklerim?">
    Yerel `openclaw skills` komutlarını kullanın veya skills'i çalışma alanınıza bırakın. macOS Skills UI Linux'ta yoktur.
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
    dizinine yazar. Ayrı `clawhub` CLI'ı yalnızca kendi skills'inizi yayımlamak veya
    eşitlemek istiyorsanız yükleyin. Ajanlar arasında paylaşılan kurulumlar için skill'i
    `~/.openclaw/skills` altına koyun ve hangi ajanların görebileceğini sınırlamak için
    `agents.defaults.skills` veya
    `agents.list[].skills` kullanın.

  </Accordion>

  <Accordion title="OpenClaw görevleri takvimle veya arka planda sürekli çalıştırabilir mi?">
    Evet. Gateway zamanlayıcısını kullanın:

    - Zamanlanmış veya yinelenen görevler için **Cron işleri** (yeniden başlatmalar arasında kalır).
    - "Ana oturum" periyodik kontrolleri için **Heartbeat**.
    - Özet gönderen veya sohbetlere teslim eden otonom ajanlar için **Yalıtılmış işler**.

    Belgeler: [Cron işleri](/tr/automation/cron-jobs), [Otomasyon ve Görevler](/tr/automation),
    [Heartbeat](/tr/gateway/heartbeat).

  </Accordion>

  <Accordion title="Linux'tan Apple macOS-only skills çalıştırabilir miyim?">
    Doğrudan hayır. macOS skills, `metadata.openclaw.os` artı gerekli ikililer tarafından geçitlenir ve skills sistem isteminde yalnızca **Gateway ana makinesinde** uygun olduklarında görünür. Linux'ta `darwin`-yalnızca skills (`apple-notes`, `apple-reminders`, `things-mac` gibi), geçitlemeyi geçersiz kılmadığınız sürece yüklenmez.

    Üç desteklenen deseniniz var:

    **Seçenek A - Gateway'i bir Mac üzerinde çalıştırın (en basit).**
    Gateway'i macOS ikililerinin bulunduğu yerde çalıştırın, sonra Linux'tan [uzak modda](#gateway-portları-zaten-çalışıyor-ve-uzak-mod) veya Tailscale üzerinden bağlanın. Skills normal yüklenir çünkü Gateway ana makinesi macOS'tur.

    **Seçenek B - macOS node kullanın (SSH yok).**
    Gateway'i Linux'ta çalıştırın, bir macOS node'u (menubar uygulaması) eşleştirin ve Mac'te **Node Run Commands** ayarını "Always Ask" veya "Always Allow" yapın. OpenClaw, gerekli ikililer node üzerinde varsa macOS-only skills'i uygun sayabilir. Ajan bu skills'i `nodes` aracı üzerinden çalıştırır. "Always Ask" seçerseniz istemde "Always Allow" onayı o komutu izin listesine ekler.

    **Seçenek C - macOS ikililerini SSH üzerinden vekilleyin (ileri seviye).**
    Gateway'i Linux'ta tutun, ama gerekli CLI ikililerinin bir Mac üzerinde çalışan SSH sarmalayıcılarına çözülmesini sağlayın. Sonra skill'i Linux'a izin verecek şekilde geçersiz kılın ki uygun kalsın.

    1. İkili için bir SSH sarmalayıcı oluşturun (örnek: Apple Notes için `memo`):

       ```bash
       #!/usr/bin/env bash
       set -euo pipefail
       exec ssh -T user@mac-host /opt/homebrew/bin/memo "$@"
       ```

    2. Sarmalayıcıyı Linux ana makinesinde PATH üzerine koyun (örneğin `~/bin/memo`).
    3. Skill metadata'sını (çalışma alanı veya `~/.openclaw/skills`) Linux'a izin verecek şekilde geçersiz kılın:

       ```markdown
       ---
       name: apple-notes
       description: Apple Notes'u macOS üzerindeki memo CLI üzerinden yönetin.
       metadata: { "openclaw": { "os": ["darwin", "linux"], "requires": { "bins": ["memo"] } } }
       ---
       ```

    4. Skills anlık görüntüsü yenilensin diye yeni bir oturum başlatın.

  </Accordion>

  <Accordion title="Notion veya HeyGen entegrasyonunuz var mı?">
    Bugün yerleşik değil.

    Seçenekler:

    - **Özel skill / eklenti:** güvenilir API erişimi için en iyisi (Notion/HeyGen'in ikisinin de API'si var).
    - **Tarayıcı otomasyonu:** kodsuz çalışır ama daha yavaş ve daha kırılgandır.

    İstemci başına bağlam tutmak istiyorsanız (ajans iş akışları), basit bir desen:

    - İstemci başına bir Notion sayfası (bağlam + tercihler + etkin iş).
    - Oturum başında ajandan o sayfayı getirmesini isteyin.

    Yerel bir entegrasyon istiyorsanız özellik isteği açın veya bu API'leri
    hedefleyen bir skill oluşturun.

    Skills yüklemek:

    ```bash
    openclaw skills install <skill-slug>
    openclaw skills update --all
    ```

    Yerel kurulumlar etkin çalışma alanı `skills/` dizinine gider. Ajanlar arasında paylaşılan skills için bunları `~/.openclaw/skills/<name>/SKILL.md` içine yerleştirin. Yalnızca bazı ajanlar paylaşılan kurulumu görmeliyse `agents.defaults.skills` veya `agents.list[].skills` yapılandırın. Bazı skills, Homebrew ile kurulmuş ikililer bekler; Linux'ta bu Linuxbrew anlamına gelir (yukarıdaki Homebrew Linux SSS girişine bakın). Bkz. [Skills](/tr/tools/skills), [Skills yapılandırması](/tr/tools/skills-config) ve [ClawHub](/tr/tools/clawhub).

  </Accordion>

  <Accordion title="Mevcut oturum açılmış Chrome'umu OpenClaw ile nasıl kullanırım?">
    Chrome DevTools MCP üzerinden bağlanan yerleşik `user` tarayıcı profilini kullanın:

    ```bash
    openclaw browser --browser-profile user tabs
    openclaw browser --browser-profile user snapshot
    ```

    Özel bir ad istiyorsanız, açık bir MCP profili oluşturun:

    ```bash
    openclaw browser create-profile --name chrome-live --driver existing-session
    openclaw browser --browser-profile chrome-live tabs
    ```

    Bu yol ana makineye özeldir. Gateway başka yerde çalışıyorsa, ya tarayıcı makinesinde bir node host çalıştırın ya da onun yerine uzak CDP kullanın.

    `existing-session` / `user` için mevcut sınırlar:

    - işlemler CSS seçiciye değil, ref tabanlıdır
    - yüklemeler `ref` / `inputRef` gerektirir ve şu anda aynı anda tek dosyayı destekler
    - `responsebody`, PDF dışa aktarma, indirme yakalama ve toplu işlemler hâlâ yönetilen bir tarayıcı veya ham CDP profili gerektirir

  </Accordion>
</AccordionGroup>

## Sandbox ve bellek

<AccordionGroup>
  <Accordion title="Özel bir sandbox belgesi var mı?">
    Evet. Bkz. [Sandboxing](/tr/gateway/sandboxing). Docker'a özgü kurulum için (tam gateway'in Docker içinde çalışması veya sandbox image'ları), bkz. [Docker](/tr/install/docker).
  </Accordion>

  <Accordion title="Docker kısıtlı hissettiriyor - tam özellikleri nasıl etkinleştiririm?">
    Varsayılan image güvenlik önceliklidir ve `node` kullanıcısı olarak çalışır, bu yüzden
    sistem paketleri, Homebrew veya paketle gelen tarayıcıları içermez. Daha kapsamlı bir kurulum için:

    - Önbellekler kalıcı olsun diye `/home/node` konumunu `OPENCLAW_HOME_VOLUME` ile kalıcılaştırın.
    - Sistem bağımlılıklarını `OPENCLAW_DOCKER_APT_PACKAGES` ile image içine gömün.
    - Paketle gelen CLI ile Playwright tarayıcılarını yükleyin:
      `node /app/node_modules/playwright-core/cli.js install chromium`
    - `PLAYWRIGHT_BROWSERS_PATH` ayarlayın ve yolun kalıcı olduğundan emin olun.

    Belgeler: [Docker](/tr/install/docker), [Tarayıcı](/tr/tools/browser).

  </Accordion>

  <Accordion title="DM'leri kişisel tutup grupları tek ajanla herkese açık/sandbox'lı yapabilir miyim?">
    Evet - özel trafiğiniz **DM**, herkese açık trafiğiniz **gruplar** ise.

    `agents.defaults.sandbox.mode: "non-main"` kullanın; böylece grup/kanal oturumları (ana olmayan anahtarlar) Docker içinde çalışırken ana DM oturumu ana makinede kalır. Sonra sandbox'lı oturumlarda hangi araçların kullanılabileceğini `tools.sandbox.tools` ile kısıtlayın.

    Kurulum anlatımı + örnek yapılandırma: [Gruplar: kişisel DM'ler + herkese açık gruplar](/tr/channels/groups#pattern-personal-dms-public-groups-single-agent)

    Temel yapılandırma başvurusu: [Gateway yapılandırması](/tr/gateway/configuration-reference#agentsdefaultssandbox)

  </Accordion>

  <Accordion title="Bir ana makine klasörünü sandbox'a nasıl bağlarım?">
    `agents.defaults.sandbox.docker.binds` değerini `["host:path:mode"]` olarak ayarlayın (ör. `"/home/user/src:/src:ro"`). Genel + ajan başına bağlar birleşir; `scope: "shared"` olduğunda ajan başına bağlar yok sayılır. Hassas şeyler için `:ro` kullanın ve bağların sandbox dosya sistemi duvarlarını aştığını unutmayın.

    OpenClaw bağ kaynaklarını hem normalize edilmiş yola hem de en derin mevcut üst öğe üzerinden çözülen kanonik yola karşı doğrular. Bu, son yol segmenti henüz yokken bile symlink ebeveyni kaçışlarının kapalı hataya düşeceği ve izin verilen kök denetimlerinin symlink çözümünden sonra da uygulanacağı anlamına gelir.

    Örnekler ve güvenlik notları için bkz. [Sandboxing](/tr/gateway/sandboxing#custom-bind-mounts) ve [Sandbox vs Tool Policy vs Elevated](/tr/gateway/sandbox-vs-tool-policy-vs-elevated#bind-mounts-security-quick-check).

  </Accordion>

  <Accordion title="Bellek nasıl çalışır?">
    OpenClaw belleği, ajan çalışma alanındaki yalnızca Markdown dosyalarıdır:

    - `memory/YYYY-MM-DD.md` içinde günlük notlar
    - `MEMORY.md` içinde derlenmiş uzun vadeli notlar (yalnızca ana/özel oturumlar)

    OpenClaw ayrıca, otomatik sıkıştırmadan önce kalıcı notlar yazmayı
    modele hatırlatmak için **sessiz bir ön-sıkıştırma bellek flush** çalıştırır. Bu yalnızca çalışma alanı
    yazılabilir olduğunda çalışır (salt okunur sandbox'lar bunu atlar). Bkz. [Bellek](/tr/concepts/memory).

  </Accordion>

  <Accordion title="Bellek bir şeyleri unutmaya devam ediyor. Bunu nasıl kalıcı hale getiririm?">
    Bottan **gerçeği belleğe yazmasını** isteyin. Uzun vadeli notlar `MEMORY.md`'ye,
    kısa vadeli bağlam `memory/YYYY-MM-DD.md` dosyasına gider.

    Bu hâlâ geliştirdiğimiz bir alan. Modeli anıları kaydetmesi için hatırlatmak yardımcı olur;
    ne yapacağını bilir. Hâlâ unutuyorsa Gateway'in her çalıştırmada aynı
    çalışma alanını kullandığını doğrulayın.

    Belgeler: [Bellek](/tr/concepts/memory), [Ajan çalışma alanı](/tr/concepts/agent-workspace).

  </Accordion>

  <Accordion title="Bellek sonsuza kadar kalıcı mı? Sınırlar neler?">
    Bellek dosyaları diskte yaşar ve siz silene kadar kalır. Sınır model değil,
    depolamanızdır. **Oturum bağlamı** yine de modelin bağlam penceresiyle
    sınırlıdır, bu yüzden uzun konuşmalar sıkıştırılabilir veya kesilebilir. Bu yüzden
    bellek araması vardır - yalnızca ilgili bölümleri tekrar bağlama çeker.

    Belgeler: [Bellek](/tr/concepts/memory), [Bağlam](/tr/concepts/context).

  </Accordion>

  <Accordion title="Anlamsal bellek araması OpenAI API anahtarı gerektirir mi?">
    Yalnızca **OpenAI embeddings** kullanırsanız. Codex OAuth sohbet/completions'ı kapsar ve
    embeddings erişimi vermez; bu yüzden **Codex ile oturum açmak (OAuth veya
    Codex CLI girişi)** anlamsal bellek aramasına yardımcı olmaz. OpenAI embeddings
    için yine gerçek bir API anahtarı gerekir (`OPENAI_API_KEY` veya `models.providers.openai.apiKey`).

    Açıkça bir sağlayıcı ayarlamazsanız OpenClaw, bir API anahtarı çözebildiğinde
    otomatik olarak bir sağlayıcı seçer (kimlik doğrulama profilleri, `models.providers.*.apiKey` veya ortam değişkenleri).
    Bir OpenAI anahtarı çözülürse OpenAI'yi, aksi halde bir Gemini anahtarı
    çözülürse Gemini'yi, sonra Voyage, sonra Mistral'ı tercih eder. Uzak anahtar yoksa,
    siz yapılandırana kadar bellek araması devre dışı kalır. Yerel model yolu
    yapılandırılmış ve mevcutsa OpenClaw
    `local`'ı tercih eder. Ollama, `memorySearch.provider = "ollama"` değerini açıkça ayarladığınızda desteklenir.

    Yerelde kalmak istiyorsanız `memorySearch.provider = "local"` (ve isteğe bağlı
    `memorySearch.fallback = "none"`) ayarlayın. Gemini embeddings istiyorsanız
    `memorySearch.provider = "gemini"` ayarlayın ve `GEMINI_API_KEY` (veya
    `memorySearch.remote.apiKey`) sağlayın. **OpenAI, Gemini, Voyage, Mistral, Ollama veya local** embedding
    modellerini destekliyoruz - kurulum ayrıntıları için bkz. [Bellek](/tr/concepts/memory).

  </Accordion>
</AccordionGroup>

## Diskte öğelerin bulunduğu yerler

<AccordionGroup>
  <Accordion title="OpenClaw ile kullanılan tüm veriler yerel olarak mı kaydedilir?">
    Hayır - **OpenClaw'ın durumu yereldir**, ama **harici hizmetler onlara gönderdiğinizi yine de görür**.

    - **Varsayılan olarak yerel:** oturumlar, bellek dosyaları, yapılandırma ve çalışma alanı Gateway ana makinesinde yaşar
      (`~/.openclaw` + çalışma alanı dizininiz).
    - **Zorunlu olarak uzak:** model sağlayıcılarına gönderdiğiniz mesajlar (Anthropic/OpenAI/vb.)
      onların API'lerine gider ve sohbet platformları (WhatsApp/Telegram/Slack/vb.) mesaj verilerini kendi
      sunucularında saklar.
    - **Ayak izini siz kontrol edersiniz:** yerel modeller kullanmak istemleri makinenizde tutar, ama kanal
      trafiği yine de kanalın sunucularından geçer.

    İlgili: [Ajan çalışma alanı](/tr/concepts/agent-workspace), [Bellek](/tr/concepts/memory).

  </Accordion>

  <Accordion title="OpenClaw verilerini nerede saklar?">
    Her şey `$OPENCLAW_STATE_DIR` altında yaşar (varsayılan: `~/.openclaw`):

    | Yol                                                             | Amaç                                                               |
    | --------------------------------------------------------------- | ------------------------------------------------------------------ |
    | `$OPENCLAW_STATE_DIR/openclaw.json`                             | Ana yapılandırma (JSON5)                                           |
    | `$OPENCLAW_STATE_DIR/credentials/oauth.json`                    | Eski OAuth içe aktarımı (ilk kullanımda kimlik doğrulama profillerine kopyalanır) |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth-profiles.json` | Kimlik doğrulama profilleri (OAuth, API anahtarları ve isteğe bağlı `keyRef`/`tokenRef`) |
    | `$OPENCLAW_STATE_DIR/secrets.json`                              | `file` SecretRef sağlayıcıları için isteğe bağlı dosya destekli gizli yük |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth.json`          | Eski uyumluluk dosyası (statik `api_key` girdileri temizlenmiş)    |
    | `$OPENCLAW_STATE_DIR/credentials/`                              | Sağlayıcı durumu (örn. `whatsapp/<accountId>/creds.json`)          |
    | `$OPENCLAW_STATE_DIR/agents/`                                   | Ajan başına durum (agentDir + sessions)                            |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                | Konuşma geçmişi ve durum (ajan başına)                             |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/sessions.json`   | Oturum meta verileri (ajan başına)                                 |

    Eski tek ajan yolu: `~/.openclaw/agent/*` (`openclaw doctor` tarafından taşınır).

    **Çalışma alanınız** (AGENTS.md, bellek dosyaları, skills vb.) ayrıdır ve `agents.defaults.workspace` ile yapılandırılır (varsayılan: `~/.openclaw/workspace`).

  </Accordion>

  <Accordion title="AGENTS.md / SOUL.md / USER.md / MEMORY.md nerede yaşamalı?">
    Bu dosyalar `~/.openclaw` içinde değil, **ajan çalışma alanında** yaşar.

    - **Çalışma alanı (ajan başına)**: `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`,
      `MEMORY.md` (veya `MEMORY.md` yoksa eski yedek `memory.md`),
      `memory/YYYY-MM-DD.md`, isteğe bağlı `HEARTBEAT.md`.
    - **Durum dizini (`~/.openclaw`)**: yapılandırma, kanal/sağlayıcı durumu, kimlik doğrulama profilleri, oturumlar, günlükler,
      ve paylaşılan skills (`~/.openclaw/skills`).

    Varsayılan çalışma alanı `~/.openclaw/workspace` olup şu yolla yapılandırılabilir:

    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
    }
    ```

    Bot yeniden başlatmadan sonra "unutuyorsa", Gateway'in her açılışta aynı
    çalışma alanını kullandığını doğrulayın (ve unutmayın: uzak mod **gateway ana makinesinin**
    çalışma alanını kullanır, yerel dizüstünüzünkini değil).

    İpucu: kalıcı bir davranış veya tercih istiyorsanız, sohbet geçmişine güvenmek yerine bottan bunu
    **AGENTS.md veya MEMORY.md içine yazmasını** isteyin.

    Bkz. [Ajan çalışma alanı](/tr/concepts/agent-workspace) ve [Bellek](/tr/concepts/memory).

  </Accordion>

  <Accordion title="Önerilen yedekleme stratejisi">
    **Ajan çalışma alanınızı** **özel** bir git deposuna koyun ve bunu özel bir yere
    yedekleyin (örneğin GitHub private). Bu, bellek + AGENTS/SOUL/USER
    dosyalarını yakalar ve daha sonra asistanın "zihnini" geri yüklemenizi sağlar.

    `~/.openclaw` altındaki hiçbir şeyi commit etmeyin (kimlik bilgileri, oturumlar, token'lar veya şifrelenmiş gizli yükler).
    Tam geri yükleme gerekiyorsa hem çalışma alanını hem de durum dizinini
    ayrı ayrı yedekleyin (yukarıdaki taşıma sorusuna bakın).

    Belgeler: [Ajan çalışma alanı](/tr/concepts/agent-workspace).

  </Accordion>

  <Accordion title="OpenClaw'ı tamamen nasıl kaldırırım?">
    Özel kılavuza bakın: [Kaldırma](/tr/install/uninstall).
  </Accordion>

  <Accordion title="Ajanlar çalışma alanının dışında çalışabilir mi?">
    Evet. Çalışma alanı katı bir sandbox değil, **varsayılan cwd** ve bellek çapasıdır.
    Göreli yollar çalışma alanı içinde çözülür, ancak mutlak yollar
    sandboxing etkin değilse başka ana makine konumlarına erişebilir. Yalıtım gerekiyorsa
    [`agents.defaults.sandbox`](/tr/gateway/sandboxing) veya ajan başına sandbox ayarlarını kullanın. Bir
    reponun varsayılan çalışma dizini olmasını istiyorsanız, o ajanın
    `workspace` değerini repo köküne yönlendirin. OpenClaw deposu yalnızca kaynak koddur; ajanı
    bilerek orada çalıştırmak istemiyorsanız çalışma alanını ondan ayrı tutun.

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
    Oturum durumunun sahibi **gateway ana makinesidir**. Uzak moddaysanız, önem verdiğiniz oturum deposu yerel dizüstünüzde değil uzak makinededir. Bkz. [Oturum yönetimi](/tr/concepts/session).
  </Accordion>
</AccordionGroup>

## Yapılandırma temelleri

<AccordionGroup>
  <Accordion title="Yapılandırma hangi biçimde? Nerede?">
    OpenClaw isteğe bağlı **JSON5** yapılandırmasını `$OPENCLAW_CONFIG_PATH` üzerinden okur (varsayılan: `~/.openclaw/openclaw.json`):

    ```
    $OPENCLAW_CONFIG_PATH
    ```

    Dosya yoksa güvenli sayılabilecek varsayılanları kullanır (varsayılan çalışma alanı olarak `~/.openclaw/workspace` dahil).

  </Accordion>

  <Accordion title='gateway.bind: "lan" (veya "tailnet") ayarladım ve artık hiçbir şey dinlemiyor / UI unauthorized diyor'>
    Loopback olmayan bağlamalar **geçerli bir gateway auth yolu gerektirir**. Pratikte bu şu anlama gelir:

    - paylaşılan gizli anahtar kimlik doğrulaması: token veya parola
    - düzgün yapılandırılmış loopback olmayan kimlik farkındalıklı reverse proxy arkasında `gateway.auth.mode: "trusted-proxy"`

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

    - `gateway.remote.token` / `.password` kendi başlarına yerel gateway auth'u etkinleştirmez.
    - Yerel çağrı yolları yalnızca `gateway.auth.*` ayarlanmamışsa yedek olarak `gateway.remote.*` kullanabilir.
    - Parola kimlik doğrulaması için bunun yerine `gateway.auth.mode: "password"` artı `gateway.auth.password` (veya `OPENCLAW_GATEWAY_PASSWORD`) ayarlayın.
    - `gateway.auth.token` / `gateway.auth.password` SecretRef ile açıkça yapılandırılmış ve çözümlenmemişse çözümleme kapalı hata verir (maskeleyen uzak yedek yoktur).
    - Paylaşılan gizli Control UI kurulumları `connect.params.auth.token` veya `connect.params.auth.password` ile kimlik doğrular (uygulama/UI ayarlarında saklanır). Tailscale Serve veya `trusted-proxy` gibi kimlik taşıyan modlar bunun yerine istek başlıklarını kullanır. Paylaşılan gizli anahtarları URL'lere koymaktan kaçının.
    - `gateway.auth.mode: "trusted-proxy"` ile, aynı ana makinedeki loopback reverse proxy'ler yine de trusted-proxy auth'u karşılamaz. Güvenilen proxy yapılandırılmış loopback olmayan bir kaynak olmalıdır.

  </Accordion>

  <Accordion title="Neden artık localhost'ta token gerekiyor?">
    OpenClaw gateway auth'u varsayılan olarak, loopback dahil, zorunlu kılar. Normal varsayılan yolda bu token auth anlamına gelir: açık bir auth yolu yapılandırılmamışsa gateway başlangıcı token moduna çözülür ve otomatik olarak bir tane üretip `gateway.auth.token` içine kaydeder; bu nedenle **yerel WS istemcileri kimlik doğrulamalıdır**. Bu, diğer yerel süreçlerin Gateway'i çağırmasını engeller.

    Farklı bir auth yolu tercih ediyorsanız açıkça parola modunu seçebilirsiniz (veya loopback olmayan kimlik farkındalıklı reverse proxy'ler için `trusted-proxy`). Loopback'i **gerçekten** açık istiyorsanız yapılandırmanızda açıkça `gateway.auth.mode: "none"` ayarlayın. Doctor size istediğiniz zaman token üretebilir: `openclaw doctor --generate-gateway-token`.

  </Accordion>

  <Accordion title="Yapılandırmayı değiştirdikten sonra yeniden başlatmam gerekir mi?">
    Gateway yapılandırmayı izler ve hot-reload destekler:

    - `gateway.reload.mode: "hybrid"` (varsayılan): güvenli değişiklikleri hot-apply eder, kritik olanlar için yeniden başlatır
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

    - `off`: slogan metnini gizler ama afiş başlık/sürüm satırını korur.
    - `default`: her seferinde `All your chats, one OpenClaw.` kullanır.
    - `random`: dönen komik/mevsimlik sloganlar (varsayılan davranış).
    - Hiç afiş istemiyorsanız ortam değişkenini `OPENCLAW_HIDE_BANNER=1` yapın.

  </Accordion>

  <Accordion title="Web aramayı (ve web fetch'i) nasıl etkinleştiririm?">
    `web_fetch` API anahtarı olmadan çalışır. `web_search`, seçtiğiniz
    sağlayıcıya bağlıdır:

    - Brave, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search, Perplexity ve Tavily gibi API destekli sağlayıcılar normal API anahtarı kurulumlarını gerektirir.
    - Ollama Web Search anahtarsızdır, ancak yapılandırdığınız Ollama ana makinesini kullanır ve `ollama signin` gerektirir.
    - DuckDuckGo anahtarsızdır, ancak resmi olmayan HTML tabanlı bir entegrasyondur.
    - SearXNG anahtarsız/kendi kendine barındırılır; `SEARXNG_BASE_URL` veya `plugins.entries.searxng.config.webSearch.baseUrl` yapılandırın.

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
              provider: "firecrawl", // isteğe bağlı; otomatik algılama için atlayın
            },
          },
        },
    }
    ```

    Sağlayıcıya özgü web-search yapılandırması artık `plugins.entries.<plugin>.config.webSearch.*` altında yer alır.
    Eski `tools.web.search.*` sağlayıcı yolları uyumluluk için geçici olarak yüklenmeye devam eder, ancak yeni yapılandırmalar için kullanılmamalıdır.
    Firecrawl web-fetch yedek yapılandırması `plugins.entries.firecrawl.config.webFetch.*` altında yaşar.

    Notlar:

    - İzin listeleri kullanıyorsanız `web_search`/`web_fetch`/`x_search` veya `group:web` ekleyin.
    - `web_fetch` varsayılan olarak etkindir (açıkça devre dışı bırakılmadıkça).
    - `tools.web.fetch.provider` atlanırsa OpenClaw mevcut kimlik bilgilerinden ilk hazır fetch yedek sağlayıcısını otomatik algılar. Bugün paketle gelen sağlayıcı Firecrawl'dır.
    - Daemon'lar ortam değişkenlerini `~/.openclaw/.env` (veya hizmet ortamı) üzerinden okur.

    Belgeler: [Web araçları](/tr/tools/web).

  </Accordion>

  <Accordion title="config.apply yapılandırmamı sildi. Nasıl kurtarırım ve bundan nasıl kaçınırım?">
    `config.apply` **tüm yapılandırmayı** değiştirir. Kısmi bir nesne gönderirseniz, diğer her şey
    kaldırılır.

    Kurtarma:

    - Yedekten geri yükleyin (git veya kopyalanmış `~/.openclaw/openclaw.json`).
    - Yedeğiniz yoksa `openclaw doctor` çalıştırın ve kanalları/modelleri yeniden yapılandırın.
    - Bu beklenmedikse bir hata bildirin ve son bilinen yapılandırmanızı veya herhangi bir yedeği ekleyin.
    - Yerel bir kodlama ajanı günlüklerden veya geçmişten çalışan bir yapılandırmayı sıklıkla yeniden kurabilir.

    Bundan kaçının:

    - Küçük değişiklikler için `openclaw config set` kullanın.
    - Etkileşimli düzenlemeler için `openclaw configure` kullanın.
    - Tam yol veya alan şekli konusunda emin değilseniz önce `config.schema.lookup` kullanın; bu, derinlemesine inceleme için sığ bir şema düğümü ile hemen alt çocuk özetlerini döndürür.
    - Kısmi RPC düzenlemeleri için `config.patch` kullanın; `config.apply`'ı yalnızca tam yapılandırma değiştirme için saklayın.
    - Bir ajan çalıştırmasından owner-only `gateway` aracını kullanıyorsanız, bu araç yine de `tools.exec.ask` / `tools.exec.security` yollarına yazmayı reddeder (`tools.bash.*` eski takma adları aynı korumalı exec yollarına normalize olur).

    Belgeler: [Config](/cli/config), [Configure](/cli/configure), [Doctor](/tr/gateway/doctor).

  </Accordion>

  <Accordion title="Cihazlar arasında uzmanlaşmış çalışanlarla merkezi bir Gateway'i nasıl çalıştırırım?">
    Yaygın desen **tek bir Gateway** (ör. Raspberry Pi) artı **nodes** ve **agents**:

    - **Gateway (merkezi):** kanalların (Signal/WhatsApp), yönlendirmenin ve oturumların sahibidir.
    - **Nodes (cihazlar):** Mac'ler/iOS/Android çevre birimi gibi bağlanır ve yerel araçları açar (`system.run`, `canvas`, `camera`).
    - **Agents (çalışanlar):** özel roller için ayrı beyinler/çalışma alanları (örn. "Hetzner ops", "Kişisel veri").
    - **Alt ajanlar:** paralellik istediğinizde ana ajandan arka plan işi başlatın.
    - **TUI:** Gateway'e bağlanır ve ajanlar/oturumlar arasında geçiş yapar.

    Belgeler: [Nodes](/tr/nodes), [Uzak erişim](/tr/gateway/remote), [Çok Ajanlı Yönlendirme](/tr/concepts/multi-agent), [Alt ajanlar](/tr/tools/subagents), [TUI](/web/tui).

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

    Varsayılan `false`'dur (headful). Headless modun bazı sitelerde anti-bot kontrollerini tetikleme olasılığı daha yüksektir. Bkz. [Tarayıcı](/tr/tools/browser).

    Headless, **aynı Chromium motorunu** kullanır ve çoğu otomasyon için çalışır (formlar, tıklamalar, scraping, girişler). Başlıca farklar:

    - Görünür tarayıcı penceresi yoktur (görsel gerekiyorsa ekran görüntüsü kullanın).
    - Bazı siteler headless modda otomasyona karşı daha katıdır (CAPTCHA'lar, anti-bot).
      Örneğin X/Twitter, headless oturumları sıklıkla engeller.

  </Accordion>

  <Accordion title="Tarayıcı denetimi için Brave'i nasıl kullanırım?">
    `browser.executablePath` değerini Brave ikilinize (veya Chromium tabanlı başka bir tarayıcıya) ayarlayın ve Gateway'i yeniden başlatın.
    Tam yapılandırma örnekleri için [Tarayıcı](/tr/tools/browser#use-brave-or-another-chromium-based-browser) sayfasına bakın.
  </Accordion>
</AccordionGroup>

## Uzak gateway'ler ve nodes

<AccordionGroup>
  <Accordion title="Komutlar Telegram, gateway ve nodes arasında nasıl yayılır?">
    Telegram mesajları **gateway** tarafından işlenir. Gateway ajanı çalıştırır ve
    ancak bir node aracı gerektiğinde nodes'u **Gateway WebSocket** üzerinden çağırır:

    Telegram → Gateway → Ajan → `node.*` → Node → Gateway → Telegram

    Nodes gelen sağlayıcı trafiğini görmez; yalnızca node RPC çağrıları alır.

  </Accordion>

  <Accordion title="Gateway uzakta barındırılıyorsa ajanım bilgisayarıma nasıl erişebilir?">
    Kısa yanıt: **bilgisayarınızı node olarak eşleştirin**. Gateway başka yerde çalışır, ama
    yerel makinenizde `node.*` araçlarını (ekran, kamera, sistem) Gateway WebSocket üzerinden çağırabilir.

    Tipik kurulum:

    1. Gateway'i her zaman açık ana makinede (VPS/ev sunucusu) çalıştırın.
    2. Gateway ana makinesini + bilgisayarınızı aynı tailnet'e koyun.
    3. Gateway WS'nin erişilebilir olduğundan emin olun (tailnet bind veya SSH tüneli).
    4. macOS uygulamasını yerelde açın ve **Remote over SSH** modunda (veya doğrudan tailnet)
       bağlanın ki node olarak kaydolabilsin.
    5. Gateway üzerinde node'u onaylayın:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    Ayrı bir TCP köprüsü gerekmez; nodes Gateway WebSocket üzerinden bağlanır.

    Güvenlik hatırlatması: bir macOS node eşleştirmek o makinede `system.run` olanağı verir. Yalnızca güvendiğiniz
    cihazları eşleştirin ve [Güvenlik](/tr/gateway/security) sayfasını inceleyin.

    Belgeler: [Nodes](/tr/nodes), [Gateway protokolü](/tr/gateway/protocol), [macOS remote mode](/tr/platforms/mac/remote), [Güvenlik](/tr/gateway/security).

  </Accordion>

  <Accordion title="Tailscale bağlı ama yanıt alamıyorum. Şimdi ne yapayım?">
    Temelleri kontrol edin:

    - Gateway çalışıyor: `openclaw gateway status`
    - Gateway sağlığı: `openclaw status`
    - Kanal sağlığı: `openclaw channels status`

    Sonra kimlik doğrulama ve yönlendirmeyi doğrulayın:

    - Tailscale Serve kullanıyorsanız `gateway.auth.allowTailscale` doğru ayarlanmış mı kontrol edin.
    - SSH tüneli üzerinden bağlanıyorsanız, yerel tünelin çalıştığını ve doğru porta gittiğini doğrulayın.
    - İzin listelerinizin (DM veya grup) hesabınızı içerdiğini doğrulayın.

    Belgeler: [Tailscale](/tr/gateway/tailscale), [Uzak erişim](/tr/gateway/remote), [Kanallar](/tr/channels).

  </Accordion>

  <Accordion title="İki OpenClaw örneği birbiriyle konuşabilir mi (yerel + VPS)?">
    Evet. Yerleşik bir "bot-to-bot" köprüsü yok, ama bunu birkaç
    güvenilir yolla bağlayabilirsiniz:

    **En basiti:** iki botun da erişebildiği normal bir sohbet kanalı kullanın (Telegram/Slack/WhatsApp).
    Bot A, Bot B'ye mesaj göndersin; sonra Bot B normal şekilde yanıtlasın.

    **CLI köprüsü (genel):** diğer Gateway'i
    `openclaw agent --message ... --deliver` ile çağıran bir betik çalıştırın ve bunu diğer botun
    dinlediği sohbete yönlendirin. Bir bot uzak VPS'teyse, CLI'ınızı SSH/Tailscale ile
    o uzak Gateway'e yönlendirin (bkz. [Uzak erişim](/tr/gateway/remote)).

    Örnek desen (hedef Gateway'e erişebilen bir makinede çalıştırın):

    ```bash
    openclaw agent --message "Yerel bottan merhaba" --deliver --channel telegram --reply-to <chat-id>
    ```

    İpucu: iki botun sonsuz döngüye girmemesi için bir guardrail ekleyin (yalnızca mention,
    kanal izin listeleri veya "bot mesajlarına yanıt verme" kuralı).

    Belgeler: [Uzak erişim](/tr/gateway/remote), [Agent CLI](/cli/agent), [Agent send](/tr/tools/agent-send).

  </Accordion>

  <Accordion title="Birden fazla ajan için ayrı VPS'lere ihtiyacım var mı?">
    Hayır. Tek bir Gateway birden çok ajan barındırabilir; her birinin kendi çalışma alanı, model varsayılanları
    ve yönlendirmesi vardır. Bu normal kurulumdur ve ajan başına
    bir VPS çalıştırmaktan çok daha ucuz ve basittir.

    Ayrı VPS'leri yalnızca sert yalıtıma (güvenlik sınırları) veya
    paylaşmak istemediğiniz çok farklı yapılandırmalara ihtiyacınız olduğunda kullanın. Aksi halde tek bir Gateway tutun ve
    birden çok ajan veya alt ajan kullanın.

  </Accordion>

  <Accordion title="Uzak bir VPS'ten SSH kullanmak yerine kişisel dizüstümde node kullanmanın faydası var mı?">
    Evet - uzak bir Gateway'den dizüstünüze ulaşmanın birinci sınıf yolu nodes'tur ve
    shell erişiminden fazlasını açar. Gateway macOS/Linux'ta çalışır (Windows'ta WSL2) ve
    hafiftir (küçük bir VPS veya Raspberry Pi sınıfı kutu yeterlidir; 4 GB RAM bol bol yeterlidir), bu yüzden yaygın
    kurulum her zaman açık ana makine artı node olarak dizüstünüzdür.

    - **Gelen SSH gerekmez.** Nodes Gateway WebSocket'e dışarı bağlanır ve cihaz eşleştirmesi kullanır.
    - **Daha güvenli yürütme denetimleri.** `system.run`, o dizüstündeki node izin listeleri/onaylarıyla geçitlenir.
    - **Daha fazla cihaz aracı.** Nodes, `system.run` yanında `canvas`, `camera` ve `screen` açar.
    - **Yerel tarayıcı otomasyonu.** Gateway'i VPS'te tutun, ama Chrome'u dizüstündeki node host üzerinden yerelde çalıştırın veya ana makinede Chrome MCP üzerinden yerel Chrome'a bağlanın.

    SSH ara sıra shell erişimi için iyidir, ama sürekli ajan iş akışları ve
    cihaz otomasyonu için nodes daha basittir.

    Belgeler: [Nodes](/tr/nodes), [Nodes CLI](/cli/nodes), [Tarayıcı](/tr/tools/browser).

  </Accordion>

  <Accordion title="Nodes bir gateway hizmeti çalıştırır mı?">
    Hayır. Kasıtlı olarak yalıtılmış profiller çalıştırmıyorsanız **her ana makinede yalnızca bir gateway** çalışmalıdır (bkz. [Çoklu gateway'ler](/tr/gateway/multiple-gateways)). Nodes, gateway'e bağlanan çevre birimleridir
    (iOS/Android nodes veya menubar uygulamasında macOS "node mode"). Headless node
    host'ları ve CLI denetimi için bkz. [Node host CLI](/cli/node).

    `gateway`, `discovery` ve `canvasHost` değişiklikleri için tam yeniden başlatma gerekir.

  </Accordion>

  <Accordion title="Yapılandırmayı uygulamak için API / RPC yolu var mı?">
    Evet.

    - `config.schema.lookup`: yazmadan önce bir yapılandırma alt ağacını sığ şema düğümü, eşleşen UI ipucu ve hemen alt çocuk özetleriyle inceleyin
    - `config.get`: geçerli anlık görüntüyü + hash'i alın
    - `config.patch`: güvenli kısmi güncelleme (çoğu RPC düzenlemesi için tercih edilir)
    - `config.apply`: yapılandırmayı doğrular + tümünü değiştirir, sonra yeniden başlatır
    - Owner-only `gateway` çalışma zamanı aracı yine de `tools.exec.ask` / `tools.exec.security` yazmayı reddeder; eski `tools.bash.*` takma adları aynı korumalı exec yollarına normalize olur

  </Accordion>

  <Accordion title="İlk kurulum için mantıklı en küçük yapılandırma">
    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
      channels: { whatsapp: { allowFrom: ["+15555550123"] } },
    }
    ```

    Bu, çalışma alanınızı ayarlar ve botu kimin tetikleyebileceğini sınırlar.

  </Accordion>

  <Accordion title="Bir VPS üzerinde Tailscale'i nasıl kurarım ve Mac'imden nasıl bağlanırım?">
    Minimum adımlar:

    1. **VPS'te kurun + giriş yapın**

       ```bash
       curl -fsSL https://tailscale.com/install.sh | sh
       sudo tailscale up
       ```

    2. **Mac'inize kurun + giriş yapın**
       - Tailscale uygulamasını kullanın ve aynı tailnet'e giriş yapın.
    3. **MagicDNS'i etkinleştirin (önerilen)**
       - Tailscale yönetici konsolunda MagicDNS'i etkinleştirin ki VPS'in sabit bir adı olsun.
    4. **Tailnet ana makine adını kullanın**
       - SSH: `ssh user@your-vps.tailnet-xxxx.ts.net`
       - Gateway WS: `ws://your-vps.tailnet-xxxx.ts.net:18789`

    Control UI'ı SSH olmadan istiyorsanız VPS üzerinde Tailscale Serve kullanın:

    ```bash
    openclaw gateway --tailscale serve
    ```

    Bu, gateway'i loopback'e bağlı tutar ve HTTPS'i Tailscale üzerinden açar. Bkz. [Tailscale](/tr/gateway/tailscale).

  </Accordion>

  <Accordion title="Bir Mac node'u uzak bir Gateway'e (Tailscale Serve) nasıl bağlarım?">
    Serve, **Gateway Control UI + WS**'yi açar. Nodes aynı Gateway WS uç noktası üzerinden bağlanır.

    Önerilen kurulum:

    1. **VPS + Mac'in aynı tailnet'te olduğundan emin olun**.
    2. **macOS uygulamasını Remote modda kullanın** (SSH hedefi tailnet ana makine adı olabilir).
       Uygulama gateway portunu tünelleyecek ve node olarak bağlanacaktır.
    3. **Gateway üzerinde node'u onaylayın**:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    Belgeler: [Gateway protokolü](/tr/gateway/protocol), [Discovery](/tr/gateway/discovery), [macOS remote mode](/tr/platforms/mac/remote).

  </Accordion>

  <Accordion title="İkinci bir dizüstüne mi kurmalıyım yoksa sadece node mu eklemeliyim?">
    İkinci dizüstüde yalnızca **yerel araçlara** (ekran/kamera/exec) ihtiyacınız varsa onu
    **node** olarak ekleyin. Bu, tek bir Gateway tutar ve yinelenen yapılandırmadan kaçınır. Yerel node araçları
    şu anda yalnızca macOS'tur, ancak bunu diğer OS'lere genişletmeyi planlıyoruz.

    İkinci bir Gateway'i yalnızca **sert yalıtım** veya tamamen ayrı iki bot gerektiğinde kurun.

    Belgeler: [Nodes](/tr/nodes), [Nodes CLI](/cli/nodes), [Çoklu gateway'ler](/tr/gateway/multiple-gateways).

  </Accordion>
</AccordionGroup>

## Ortam değişkenleri ve .env yükleme

<AccordionGroup>
  <Accordion title="OpenClaw ortam değişkenlerini nasıl yükler?">
    OpenClaw ortam değişkenlerini üst süreçten (shell, launchd/systemd, CI, vb.) okur ve ek olarak şunları yükler:

    - geçerli çalışma dizininden `.env`
    - `~/.openclaw/.env` üzerinden genel yedek `.env` (diğer adıyla `$OPENCLAW_STATE_DIR/.env`)

    `.env` dosyalarının hiçbiri mevcut ortam değişkenlerini geçersiz kılmaz.

    Yapılandırmada satır içi ortam değişkenleri de tanımlayabilirsiniz (yalnızca süreç ortamında eksikse uygulanır):

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

  <Accordion title="Gateway'i hizmet üzerinden başlattım ve ortam değişkenlerim kayboldu. Şimdi ne yapayım?">
    İki yaygın düzeltme:

    1. Eksik anahtarları `~/.openclaw/.env` içine koyun ki hizmet shell ortamınızı devralmasa bile alınsınlar.
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

    Bu, login shell'inizi çalıştırır ve yalnızca eksik beklenen anahtarları içe aktarır (asla geçersiz kılmaz). Ortam değişkeni eşdeğerleri:
    `OPENCLAW_LOAD_SHELL_ENV=1`, `OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`.

  </Accordion>

  <Accordion title='COPILOT_GITHUB_TOKEN ayarladım ama models status "Shell env: off." gösteriyor. Neden?'>
    `openclaw models status`, **shell env import** etkin olup olmadığını bildirir. "Shell env: off"
    ortam değişkenleriniz eksik anlamına gelmez - sadece OpenClaw'ın
    login shell'inizi otomatik yüklemeyeceği anlamına gelir.

    Gateway bir hizmet olarak çalışıyorsa (launchd/systemd), shell
    ortamınızı devralmaz. Şunlardan birini yaparak düzeltin:

    1. Token'ı `~/.openclaw/.env` içine koyun:

       ```
       COPILOT_GITHUB_TOKEN=...
       ```

    2. Veya shell import'u etkinleştirin (`env.shellEnv.enabled: true`).
    3. Veya bunu yapılandırma `env` bloğunuza ekleyin (yalnızca eksikse uygulanır).

    Sonra gateway'i yeniden başlatın ve tekrar kontrol edin:

    ```bash
    openclaw models status
    ```

    Copilot token'ları `COPILOT_GITHUB_TOKEN` üzerinden okunur (ayrıca `GH_TOKEN` / `GITHUB_TOKEN`).
    Bkz. [/concepts/model-providers](/tr/concepts/model-providers) ve [/environment](/tr/help/environment).

  </Accordion>
</AccordionGroup>

## Oturumlar ve birden çok sohbet

<AccordionGroup>
  <Accordion title="Taze bir konuşmayı nasıl başlatırım?">
    Tek başına mesaj olarak `/new` veya `/reset` gönderin. Bkz. [Oturum yönetimi](/tr/concepts/session).
  </Accordion>

  <Accordion title="Hiç /new göndermezsem oturumlar otomatik sıfırlanır mı?">
    Oturumlar `session.idleMinutes` sonrasında sona erebilir, ama bu varsayılan olarak **devre dışıdır** (varsayılan **0**).
    Boşta kalma sonlandırmasını etkinleştirmek için bunu pozitif bir değere ayarlayın. Etkin olduğunda,
    boşta kalma süresinden sonraki **sonraki** mesaj bu sohbet anahtarı için taze bir oturum kimliği başlatır.
    Bu, transcript'leri silmez - yalnızca yeni bir oturum başlatır.

    ```json5
    {
      session: {
        idleMinutes: 240,
      },
    }
    ```

  </Accordion>

  <Accordion title="Bir OpenClaw örnekleri takımı oluşturmanın yolu var mı (bir CEO ve birçok ajan)?">
    Evet, **çok ajanlı yönlendirme** ve **alt ajanlar** ile. Bir koordinatör
    ajan ve kendi çalışma alanları ve modelleri olan birkaç çalışan ajan oluşturabilirsiniz.

    Bununla birlikte, bunu daha çok **eğlenceli bir deney** olarak görmek gerekir. Token tüketimi yüksektir ve
    çoğu zaman ayrı oturumlarla tek bot kullanmaktan daha verimsizdir. Bizim
    öngördüğümüz tipik model, paralel işler için farklı oturumlara sahip, konuştuğunuz tek bottur. Bu
    bot gerektiğinde alt ajanlar da oluşturabilir.

    Belgeler: [Çok ajanlı yönlendirme](/tr/concepts/multi-agent), [Alt ajanlar](/tr/tools/subagents), [Agents CLI](/cli/agents).

  </Accordion>

  <Accordion title="Bağlam neden görev ortasında kesildi? Bunu nasıl önlerim?">
    Oturum bağlamı model penceresiyle sınırlıdır. Uzun sohbetler, büyük araç çıktıları veya çok sayıda
    dosya sıkıştırma veya kesilmeyi tetikleyebilir.

    Yardımcı olanlar:

    - Bottan mevcut durumu özetlemesini ve bunu dosyaya yazmasını isteyin.
    - Uzun görevlerden önce `/compact`, konu değiştirirken `/new` kullanın.
    - Önemli bağlamı çalışma alanında tutun ve bottan bunu tekrar okumasını isteyin.
    - Ana sohbet küçük kalsın diye uzun veya paralel işler için alt ajanlar kullanın.
    - Bu sık oluyorsa daha büyük bağlam penceresine sahip bir model seçin.

  </Accordion>

  <Accordion title="OpenClaw'ı tamamen sıfırlayıp yüklü bırakmak istiyorum. Nasıl yaparım?">
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

    - Onboarding mevcut bir yapılandırma görürse **Sıfırla** seçeneği de sunar. Bkz. [Onboarding (CLI)](/tr/start/wizard).
    - Profil kullandıysanız (`--profile` / `OPENCLAW_PROFILE`), her durum dizinini sıfırlayın (varsayılanlar `~/.openclaw-<profile>` şeklindedir).
    - Geliştirme sıfırlaması: `openclaw gateway --dev --reset` (yalnızca geliştirme; geliştirme yapılandırmasını + kimlik bilgilerini + oturumları + çalışma alanını siler).

  </Accordion>

  <Accordion title='"context too large" hataları alıyorum - nasıl sıfırlar veya sıkıştırırım?'>
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

    Bu tekrar oluyorsa:

    - Eski araç çıktısını budamak için **oturum budamayı** (`agents.defaults.contextPruning`) etkinleştirin veya ayarlayın.
    - Daha büyük bağlam penceresine sahip bir model kullanın.

    Belgeler: [Sıkıştırma](/tr/concepts/compaction), [Oturum budama](/tr/concepts/session-pruning), [Oturum yönetimi](/tr/concepts/session).

  </Accordion>

  <Accordion title='Neden "LLM request rejected: messages.content.tool_use.input field required" görüyorum?'>
    Bu bir sağlayıcı doğrulama hatasıdır: model, gerekli
    `input` olmadan bir `tool_use` bloğu üretti. Bu genellikle oturum geçmişinin bayat veya bozuk olduğunu gösterir (çoğunlukla uzun thread'lerden
    veya bir araç/şema değişikliğinden sonra).

    Düzeltme: tek başına mesaj olarak `/new` ile taze oturum başlatın.

  </Accordion>

  <Accordion title="Neden her 30 dakikada bir heartbeat mesajı alıyorum?">
    Heartbeat'ler varsayılan olarak her **30dk** çalışır (**OAuth auth kullanırken 1s**). Ayarlayın veya devre dışı bırakın:

    ```json5
    {
      agents: {
        defaults: {
          heartbeat: {
            every: "2h", // veya devre dışı bırakmak için "0m"
          },
        },
      },
    }
    ```

    `HEARTBEAT.md` varsa ama fiilen boşsa (yalnızca boş satırlar ve `# Heading` gibi markdown
    başlıkları), OpenClaw API çağrılarından tasarruf etmek için heartbeat çalıştırmasını atlar.
    Dosya yoksa heartbeat yine çalışır ve ne yapılacağına model karar verir.

    Ajan başına geçersiz kılmalar `agents.list[].heartbeat` kullanır. Belgeler: [Heartbeat](/tr/gateway/heartbeat).

  </Accordion>

  <Accordion title='Bir WhatsApp grubuna "bot hesabı" eklemem gerekir mi?'>
    Hayır. OpenClaw **kendi hesabınız** üzerinde çalışır, yani siz gruptaysanız OpenClaw bunu görebilir.
    Varsayılan olarak gönderenlere izin verene kadar grup yanıtları engellenir (`groupPolicy: "allowlist"`).

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
    Seçenek 1 (en hızlı): günlükleri izleyin ve grupta bir test mesajı gönderin:

    ```bash
    openclaw logs --follow --json
    ```

    `@g.us` ile biten `chatId` (veya `from`) arayın, örneğin:
    `1234567890-1234567890@g.us`.

    Seçenek 2 (zaten yapılandırılmış/izin listesinde ise): yapılandırmadan grupları listeleyin:

    ```bash
    openclaw directory groups list --channel whatsapp
    ```

    Belgeler: [WhatsApp](/tr/channels/whatsapp), [Directory](/cli/directory), [Logs](/cli/logs).

  </Accordion>

  <Accordion title="OpenClaw neden bir grupta yanıt vermiyor?">
    İki yaygın neden:

    - Mention geçidi açık (varsayılan). Botu @mention etmeniz (veya `mentionPatterns` ile eşleşmeniz) gerekir.
    - `channels.whatsapp.groups` yapılandırdınız ama `"*"` eklemediniz ve grup izin listesinde değil.

    Bkz. [Gruplar](/tr/channels/groups) ve [Grup mesajları](/tr/channels/group-messages).

  </Accordion>

  <Accordion title="Gruplar/thread'ler DM'lerle bağlam paylaşır mı?">
    Doğrudan sohbetler varsayılan olarak ana oturuma çöker. Gruplar/kanalların kendi oturum anahtarları vardır ve Telegram başlıkları / Discord thread'leri ayrı oturumlardır. Bkz. [Gruplar](/tr/channels/groups) ve [Grup mesajları](/tr/channels/group-messages).
  </Accordion>

  <Accordion title="Kaç çalışma alanı ve ajan oluşturabilirim?">
    Sert sınırlar yok. Onlarca (hatta yüzlercesi) sorun olmaz, ama şunlara dikkat edin:

    - **Disk büyümesi:** oturumlar + transcript'ler `~/.openclaw/agents/<agentId>/sessions/` altında yaşar.
    - **Token maliyeti:** daha fazla ajan daha fazla eşzamanlı model kullanımı demektir.
    - **İşletim yükü:** ajan başına kimlik doğrulama profilleri, çalışma alanları ve kanal yönlendirmesi.

    İpuçları:

    - Ajan başına bir **etkin** çalışma alanı tutun (`agents.defaults.workspace`).
    - Disk büyürse eski oturumları budayın (JSONL veya store girdilerini silin).
    - Başıboş çalışma alanları ve profil uyuşmazlıklarını görmek için `openclaw doctor` kullanın.

  </Accordion>

  <Accordion title="Aynı anda birden fazla bot veya sohbet (Slack) çalıştırabilir miyim ve bunu nasıl kurmalıyım?">
    Evet. Birden çok yalıtılmış ajan çalıştırmak ve gelen mesajları
    kanal/hesap/eşe göre yönlendirmek için **Çok Ajanlı Yönlendirme** kullanın. Slack kanal olarak desteklenir ve belirli ajanlara bağlanabilir.

    Tarayıcı erişimi güçlüdür ama "bir insanın yapabildiği her şeyi yapar" anlamına gelmez - anti-bot, CAPTCHA'lar ve MFA
    otomasyonu hâlâ engelleyebilir. En güvenilir tarayıcı denetimi için ana makinede yerel Chrome MCP kullanın
    veya tarayıcının gerçekten çalıştığı makinede CDP kullanın.

    En iyi uygulama kurulumu:

    - Her zaman açık Gateway ana makinesi (VPS/Mac mini).
    - Rol başına bir ajan (bağlamalar).
    - O ajanlara bağlı Slack kanal(lar)ı.
    - Gerektiğinde Chrome MCP veya node üzerinden yerel tarayıcı.

    Belgeler: [Çok Ajanlı Yönlendirme](/tr/concepts/multi-agent), [Slack](/tr/channels/slack),
    [Tarayıcı](/tr/tools/browser), [Nodes](/tr/nodes).

  </Accordion>
</AccordionGroup>

## Modeller: varsayılanlar, seçim, takma adlar, geçiş

<AccordionGroup>
  <Accordion title='Varsayılan model nedir?'>
    OpenClaw'ın varsayılan modeli şurada ayarladığınız şeydir:

    ```
    agents.defaults.model.primary
    ```

    Modeller `provider/model` olarak başvurulur (örnek: `openai/gpt-5.4`). Sağlayıcıyı atlarsanız OpenClaw önce bir takma ad dener, sonra o tam model kimliği için benzersiz yapılandırılmış sağlayıcı eşleşmesini dener ve yalnızca ondan sonra kullanımdan kaldırılmış bir uyumluluk yolu olarak yapılandırılmış varsayılan sağlayıcıya geri döner. O sağlayıcı artık yapılandırılmış varsayılan modeli sunmuyorsa, kaldırılmış eski bir sağlayıcı varsayılanını yüzeye çıkarmak yerine ilk yapılandırılmış sağlayıcı/modele geri düşer. Yine de **provider/model değerini açıkça** ayarlamanız gerekir.

  </Accordion>

  <Accordion title="Hangi modeli öneriyorsunuz?">
    **Önerilen varsayılan:** sağlayıcı yığınınızda bulunan en güçlü yeni nesil modeli kullanın.
    **Araç etkin veya güvenilmeyen girdi alan ajanlar için:** maliyetten çok model gücünü önceliklendirin.
    **Rutin/düşük riskli sohbetler için:** daha ucuz yedek modeller kullanın ve ajan rolüne göre yönlendirin.

    MiniMax'in kendi belgeleri vardır: [MiniMax](/tr/providers/minimax) ve
    [Yerel modeller](/tr/gateway/local-models).

    Kural olarak, yüksek riskli işler için **karşılayabildiğiniz en iyi modeli** kullanın ve rutin
    sohbet veya özetler için daha ucuz bir model seçin. Ajan başına model yönlendirebilir ve uzun görevleri
    paralelleştirmek için alt ajanlar kullanabilirsiniz (her alt ajan token tüketir). Bkz. [Modeller](/tr/concepts/models) ve
    [Alt ajanlar](/tr/tools/subagents).

    Güçlü uyarı: daha zayıf/aşırı kuantize modeller prompt
    injection ve güvensiz davranışlara daha açıktır. Bkz. [Güvenlik](/tr/gateway/security).

    Daha fazla bağlam: [Modeller](/tr/concepts/models).

  </Accordion>

  <Accordion title="Yapılandırmamı silmeden modelleri nasıl değiştiririm?">
    **Model komutlarını** kullanın veya yalnızca **model** alanlarını düzenleyin. Tüm yapılandırmayı değiştirmekten kaçının.

    Güvenli seçenekler:

    - sohbette `/model` (hızlı, oturum başına)
    - `openclaw models set ...` (yalnızca model yapılandırmasını günceller)
    - `openclaw configure --section model` (etkileşimli)
    - `~/.openclaw/openclaw.json` içinde `agents.defaults.model` düzenleme

    Tüm yapılandırmayı değiştirmek niyetinde değilseniz kısmi nesneyle `config.apply` kullanmayın.
    RPC düzenlemeleri için önce `config.schema.lookup` ile inceleyin ve `config.patch` tercih edin. Lookup yükü size normalize edilmiş yolu, sığ şema belgelerini/kısıtlarını ve hemen alt çocuk özetlerini verir.
    kısmi güncellemeler için.
    Yapılandırmayı üzerine yazdıysanız yedekten geri yükleyin veya onarmak için `openclaw doctor` çalıştırın.

    Belgeler: [Modeller](/tr/concepts/models), [Configure](/cli/configure), [Config](/cli/config), [Doctor](/tr/gateway/doctor).

  </Accordion>

  <Accordion title="Self-hosted modeller (llama.cpp, vLLM, Ollama) kullanabilir miyim?">
    Evet. Yerel modeller için en kolay yol Ollama'dır.

    En hızlı kurulum:

    1. Ollama'yı `https://ollama.com/download` adresinden yükleyin
    2. `ollama pull glm-4.7-flash` gibi yerel bir model çekin
    3. Bulut modelleri de istiyorsanız `ollama signin` çalıştırın
    4. `openclaw onboard` çalıştırın ve `Ollama` seçin
    5. `Local` veya `Cloud + Local` seçin

    Notlar:

    - `Cloud + Local`, bulut modelleri ile yerel Ollama modellerinizi birlikte verir
    - `kimi-k2.5:cloud` gibi bulut modelleri için yerel pull gerekmez
    - Elle geçiş için `openclaw models list` ve `openclaw models set ollama/<model>` kullanın

    Güvenlik notu: daha küçük veya yoğun kuantize modeller prompt
    injection'a daha açıktır. Araç kullanabilen her bot için güçlü biçimde **büyük modeller**
    öneriyoruz. Yine de küçük modeller kullanmak istiyorsanız sandboxing ve katı araç izin listeleri etkinleştirin.

    Belgeler: [Ollama](/tr/providers/ollama), [Yerel modeller](/tr/gateway/local-models),
    [Model sağlayıcıları](/tr/concepts/model-providers), [Güvenlik](/tr/gateway/security),
    [Sandboxing](/tr/gateway/sandboxing).

  </Accordion>

  <Accordion title="OpenClaw, Flawd ve Krill modeller için ne kullanıyor?">
    - Bu dağıtımlar farklı olabilir ve zamanla değişebilir; sabit bir sağlayıcı önerisi yoktur.
    - Her gateway üzerindeki geçerli çalışma zamanı ayarını `openclaw models status` ile kontrol edin.
    - Güvenliğe duyarlı/araç etkin ajanlar için kullanılabilir en güçlü yeni nesil modeli kullanın.
  </Accordion>

  <Accordion title="Modelleri anında (yeniden başlatmadan) nasıl değiştiririm?">
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

    Bunlar yerleşik takma adlardır. Özel takma adlar `agents.defaults.models` ile eklenebilir.

    Kullanılabilir modelleri `/model`, `/model list` veya `/model status` ile listeleyebilirsiniz.

    `/model` (ve `/model list`) kompakt, numaralı bir seçici gösterir. Numarayla seçin:

    ```
    /model 3
    ```

    Sağlayıcı için belirli bir kimlik doğrulama profilini de zorlayabilirsiniz (oturum başına):

    ```
    /model opus@anthropic:default
    /model opus@anthropic:work
    ```

    İpucu: `/model status`, hangi ajanın etkin olduğunu, hangi `auth-profiles.json` dosyasının kullanıldığını ve hangi kimlik doğrulama profilinin sonraki deneneceğini gösterir.
    Ayrıca mevcutsa yapılandırılmış sağlayıcı uç noktasını (`baseUrl`) ve API modunu (`api`) da gösterir.

    **@profile ile ayarladığım sabitlemeyi nasıl kaldırırım?**

    `/model` komutunu `@profile` son eki **olmadan** yeniden çalıştırın:

    ```
    /model anthropic/claude-opus-4-6
    ```

    Varsayılana dönmek istiyorsanız `/model` içinden seçin (veya `/model <default provider/model>` gönderin).
    Hangi kimlik doğrulama profilinin etkin olduğunu doğrulamak için `/model status` kullanın.

  </Accordion>

  <Accordion title="Günlük işler için GPT 5.2, kodlama için Codex 5.3 kullanabilir miyim?">
    Evet. Birini varsayılan yapın, gerektiğinde değiştirin:

    - **Hızlı geçiş (oturum başına):** günlük işler için `/model gpt-5.4`, Codex OAuth ile kodlama için `/model openai-codex/gpt-5.4`.
    - **Varsayılan + geçiş:** `agents.defaults.model.primary` değerini `openai/gpt-5.4` yapın, sonra kodlama yaparken `openai-codex/gpt-5.4` değerine geçin (veya tersi).
    - **Alt ajanlar:** kodlama görevlerini farklı varsayılan modele sahip alt ajanlara yönlendirin.

    Bkz. [Modeller](/tr/concepts/models) ve [Slash komutları](/tr/tools/slash-commands).

  </Accordion>

  <Accordion title="GPT 5.4 için fast mode'u nasıl yapılandırırım?">
    Oturum geçişi veya yapılandırma varsayılanı