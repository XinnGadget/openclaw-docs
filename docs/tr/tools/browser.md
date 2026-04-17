---
read_when:
    - Aracı tarafından kontrol edilen tarayıcı otomasyonunun eklenmesi
    - openclaw’ın kendi Chrome’unuza neden müdahale ettiğini ayıklama
    - macOS uygulamasında tarayıcı ayarları + yaşam döngüsünün uygulanması
summary: Entegre tarayıcı kontrol hizmeti + eylem komutları
title: Tarayıcı (OpenClaw tarafından yönetilen)
x-i18n:
    generated_at: "2026-04-14T08:52:09Z"
    model: gpt-5.4
    provider: openai
    source_hash: ae9ef725f544d4236d229f498c7187871c69bd18d31069b30a7e67fac53166a2
    source_path: tools/browser.md
    workflow: 15
---

# Tarayıcı (openclaw tarafından yönetilen)

OpenClaw, aracının kontrol ettiği **özel bir Chrome/Brave/Edge/Chromium profili** çalıştırabilir.
Bu profil kişisel tarayıcınızdan yalıtılmıştır ve Gateway içindeki küçük bir yerel
kontrol hizmeti üzerinden yönetilir (yalnızca loopback).

Yeni başlayanlar için görünüm:

- Bunu **ayrı, yalnızca aracıya özel bir tarayıcı** olarak düşünün.
- `openclaw` profili **kişisel tarayıcı profilinize** dokunmaz.
- Aracı güvenli bir alanda **sekmeleri açabilir, sayfaları okuyabilir, tıklayabilir ve yazabilir**.
- Yerleşik `user` profili, Chrome MCP aracılığıyla gerçek oturum açılmış Chrome oturumunuza bağlanır.

## Elde edecekleriniz

- **openclaw** adlı ayrı bir tarayıcı profili (varsayılan olarak turuncu vurgu).
- Deterministik sekme kontrolü (listele/aç/odaklan/kapat).
- Aracı eylemleri (tıkla/yaz/sürükle/seç), anlık görüntüler, ekran görüntüleri, PDF’ler.
- İsteğe bağlı çoklu profil desteği (`openclaw`, `work`, `remote`, ...).

Bu tarayıcı **günlük kullandığınız tarayıcı değildir**. Aracı otomasyonu ve doğrulaması için güvenli, yalıtılmış bir yüzeydir.

## Hızlı başlangıç

```bash
openclaw browser --browser-profile openclaw status
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw open https://example.com
openclaw browser --browser-profile openclaw snapshot
```

“Browser disabled” hatası alırsanız, bunu yapılandırmada etkinleştirin (aşağıya bakın) ve
Gateway’i yeniden başlatın.

`openclaw browser` tamamen yoksa veya aracı tarayıcı aracının
kullanılamadığını söylüyorsa, [Eksik tarayıcı komutu veya aracı](/tr/tools/browser#missing-browser-command-or-tool) bölümüne gidin.

## Plugin kontrolü

Varsayılan `browser` aracı artık varsayılan olarak etkin gelen yerleşik bir Plugin’dir.
Bu, OpenClaw’ın Plugin sisteminin geri kalanını kaldırmadan onu devre dışı
bırakabileceğiniz veya değiştirebileceğiniz anlamına gelir:

```json5
{
  plugins: {
    entries: {
      browser: {
        enabled: false,
      },
    },
  },
}
```

Aynı `browser` araç adını sağlayan başka bir Plugin yüklemeden önce yerleşik Plugin’i devre dışı bırakın.
Varsayılan tarayıcı deneyimi için her ikisi de gerekir:

- `plugins.entries.browser.enabled` devre dışı bırakılmamış olmalı
- `browser.enabled=true`

Yalnızca Plugin’i kapatırsanız, yerleşik tarayıcı CLI’si (`openclaw browser`),
gateway yöntemi (`browser.request`), aracı aracı ve varsayılan tarayıcı kontrol
hizmeti birlikte ortadan kalkar. `browser.*` yapılandırmanız, yerine geçecek bir
Plugin’in yeniden kullanabilmesi için olduğu gibi kalır.

Yerleşik tarayıcı Plugin’i artık tarayıcı çalışma zamanı uygulamasının da sahibidir.
Çekirdek yalnızca paylaşılan Plugin SDK yardımcılarını ve eski dahili içe aktarma
yolları için uyumluluk yeniden dışa aktarmalarını tutar. Pratikte bu, tarayıcı
Plugin paketini kaldırmanın veya değiştirmenin, geride çekirdeğe ait ikinci bir
çalışma zamanı bırakmak yerine tarayıcı özellik kümesini kaldırdığı anlamına gelir.

Tarayıcı yapılandırma değişiklikleri hâlâ bir Gateway yeniden başlatması gerektirir;
böylece yerleşik Plugin tarayıcı hizmetini yeni ayarlarla yeniden kaydedebilir.

## Eksik tarayıcı komutu veya aracı

Bir yükseltmeden sonra `openclaw browser` birden bilinmeyen komut hâline geldiyse
veya aracı tarayıcı aracının eksik olduğunu bildiriyorsa, en yaygın neden
`browser` öğesini içermeyen kısıtlayıcı bir `plugins.allow` listesidir.

Bozuk yapılandırma örneği:

```json5
{
  plugins: {
    allow: ["telegram"],
  },
}
```

`browser` öğesini Plugin izin listesine ekleyerek bunu düzeltin:

```json5
{
  plugins: {
    allow: ["telegram", "browser"],
  },
}
```

Önemli notlar:

- `plugins.allow` ayarlıysa tek başına `browser.enabled=true` yeterli değildir.
- `plugins.allow` ayarlıysa tek başına `plugins.entries.browser.enabled=true` de yeterli değildir.
- `tools.alsoAllow: ["browser"]` yerleşik tarayıcı Plugin’ini yüklemez. Yalnızca Plugin zaten yüklendikten sonra araç ilkesini ayarlar.
- Kısıtlayıcı bir Plugin izin listesine ihtiyacınız yoksa, `plugins.allow` değerini kaldırmak da varsayılan yerleşik tarayıcı davranışını geri yükler.

Tipik belirtiler:

- `openclaw browser` bilinmeyen bir komuttur.
- `browser.request` eksiktir.
- Aracı, tarayıcı aracının kullanılamadığını veya eksik olduğunu bildirir.

## Profiller: `openclaw` ve `user`

- `openclaw`: yönetilen, yalıtılmış tarayıcı (uzantı gerekmez).
- `user`: gerçek **oturum açılmış Chrome** oturumunuz için yerleşik Chrome MCP bağlanma profili.

Aracı tarayıcı aracı çağrıları için:

- Varsayılan: yalıtılmış `openclaw` tarayıcısını kullanın.
- Mevcut oturum açılmış oturumlar önemliyse ve kullanıcı bağlanma istemini
  tıklayıp onaylayabilecek durumdaysa `profile="user"` tercih edin.
- Belirli bir tarayıcı modu istediğinizde `profile` açık geçersiz kılmadır.

Varsayılan olarak yönetilen modu istiyorsanız `browser.defaultProfile: "openclaw"` ayarlayın.

## Yapılandırma

Tarayıcı ayarları `~/.openclaw/openclaw.json` içinde bulunur.

```json5
{
  browser: {
    enabled: true, // varsayılan: true
    ssrfPolicy: {
      // dangerouslyAllowPrivateNetwork: true, // yalnızca güvenilen özel ağ erişimi için etkinleştirin
      // allowPrivateNetwork: true, // eski takma ad
      // hostnameAllowlist: ["*.example.com", "example.com"],
      // allowedHostnames: ["localhost"],
    },
    // cdpUrl: "http://127.0.0.1:18792", // eski tek profil geçersiz kılması
    remoteCdpTimeoutMs: 1500, // uzak CDP HTTP zaman aşımı (ms)
    remoteCdpHandshakeTimeoutMs: 3000, // uzak CDP WebSocket el sıkışma zaman aşımı (ms)
    defaultProfile: "openclaw",
    color: "#FF4500",
    headless: false,
    noSandbox: false,
    attachOnly: false,
    executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    profiles: {
      openclaw: { cdpPort: 18800, color: "#FF4500" },
      work: { cdpPort: 18801, color: "#0066CC" },
      user: {
        driver: "existing-session",
        attachOnly: true,
        color: "#00AA00",
      },
      brave: {
        driver: "existing-session",
        attachOnly: true,
        userDataDir: "~/Library/Application Support/BraveSoftware/Brave-Browser",
        color: "#FB542B",
      },
      remote: { cdpUrl: "http://10.0.0.42:9222", color: "#00AA00" },
    },
  },
}
```

Notlar:

- Tarayıcı kontrol hizmeti, `gateway.port` değerinden türetilen bir bağlantı noktası üzerinde loopback’e bağlanır
  (varsayılan: `18791`; yani gateway + 2).
- Gateway bağlantı noktasını geçersiz kılarsanız (`gateway.port` veya `OPENCLAW_GATEWAY_PORT`),
  türetilen tarayıcı bağlantı noktaları aynı “ailede” kalmak için birlikte kayar.
- `cdpUrl`, ayarlanmadığında yönetilen yerel CDP bağlantı noktasını varsayılan olarak kullanır.
- `remoteCdpTimeoutMs`, uzak (loopback olmayan) CDP erişilebilirlik denetimleri için geçerlidir.
- `remoteCdpHandshakeTimeoutMs`, uzak CDP WebSocket erişilebilirlik denetimleri için geçerlidir.
- Tarayıcı gezinmesi/sekme açma, gezinmeden önce SSRF korumasından geçer ve gezinmeden sonraki son `http(s)` URL’sinde en iyi çabayla yeniden denetlenir.
- Katı SSRF modunda, uzak CDP uç noktası keşfi/sondaları (`cdpUrl`, `/json/version` aramaları dahil) da denetlenir.
- `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork` varsayılan olarak devre dışıdır. Yalnızca özel ağ tarayıcı erişimine bilerek güveniyorsanız `true` olarak ayarlayın.
- `browser.ssrfPolicy.allowPrivateNetwork`, uyumluluk için eski bir takma ad olarak desteklenmeye devam eder.
- `attachOnly: true`, “asla yerel tarayıcı başlatma; yalnızca zaten çalışıyorsa bağlan” anlamına gelir.
- `color` + profile özel `color`, hangi profilin etkin olduğunu görebilmeniz için tarayıcı arayüzünü renklendirir.
- Varsayılan profil `openclaw`’dır (OpenClaw tarafından yönetilen bağımsız tarayıcı). Oturum açılmış kullanıcı tarayıcısına geçmek için `defaultProfile: "user"` kullanın.
- Otomatik algılama sırası: Chromium tabanlıysa sistem varsayılan tarayıcısı; değilse Chrome → Brave → Edge → Chromium → Chrome Canary.
- Yerel `openclaw` profilleri `cdpPort`/`cdpUrl` değerlerini otomatik atar — bunları yalnızca uzak CDP için ayarlayın.
- `driver: "existing-session"`, ham CDP yerine Chrome DevTools MCP kullanır. Bu
  sürücü için `cdpUrl` ayarlamayın.
- Var olan oturum profili Brave veya Edge gibi varsayılan olmayan bir Chromium kullanıcı profiline bağlanacaksa
  `browser.profiles.<name>.userDataDir` ayarlayın.

## Brave kullanın (veya başka bir Chromium tabanlı tarayıcı)

**Sistem varsayılan** tarayıcınız Chromium tabanlıysa (Chrome/Brave/Edge/vb.),
OpenClaw bunu otomatik olarak kullanır. Otomatik algılamayı geçersiz kılmak için
`browser.executablePath` ayarlayın:

CLI örneği:

```bash
openclaw config set browser.executablePath "/usr/bin/google-chrome"
```

```json5
// macOS
{
  browser: {
    executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
  }
}

// Windows
{
  browser: {
    executablePath: "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
  }
}

// Linux
{
  browser: {
    executablePath: "/usr/bin/brave-browser"
  }
}
```

## Yerel ve uzak kontrol

- **Yerel kontrol (varsayılan):** Gateway, loopback kontrol hizmetini başlatır ve yerel bir tarayıcı açabilir.
- **Uzak kontrol (Node ana makinesi):** Tarayıcının bulunduğu makinede bir Node ana makinesi çalıştırın; Gateway tarayıcı eylemlerini ona vekâlet eder.
- **Uzak CDP:** uzak bir Chromium tabanlı tarayıcıya bağlanmak için `browser.profiles.<name>.cdpUrl` (veya `browser.cdpUrl`) ayarlayın. Bu durumda OpenClaw yerel bir tarayıcı başlatmaz.

Durdurma davranışı profil moduna göre farklılık gösterir:

- yerel yönetilen profiller: `openclaw browser stop`, OpenClaw’ın başlattığı tarayıcı sürecini durdurur
- yalnızca bağlanma ve uzak CDP profilleri: `openclaw browser stop`, etkin
  kontrol oturumunu kapatır ve Playwright/CDP öykünme geçersiz kılmalarını (görüntü alanı,
  renk düzeni, yerel ayar, saat dilimi, çevrimdışı mod ve benzer durumlar)
  serbest bırakır; OpenClaw tarafından herhangi bir tarayıcı süreci başlatılmamış olsa bile

Uzak CDP URL’leri kimlik doğrulama içerebilir:

- Sorgu belirteçleri (ör. `https://provider.example?token=<token>`)
- HTTP Basic kimlik doğrulaması (ör. `https://user:pass@provider.example`)

OpenClaw, `/json/*` uç noktalarını çağırırken ve
CDP WebSocket’e bağlanırken kimlik doğrulamayı korur. Belirteçleri yapılandırma
dosyalarına işlememek için ortam değişkenlerini veya gizli anahtar yöneticilerini tercih edin.

## Node tarayıcı vekili (varsayılan olarak sıfır yapılandırma)

Tarayıcınızın bulunduğu makinede bir **Node ana makinesi** çalıştırırsanız, OpenClaw
hiçbir ek tarayıcı yapılandırması olmadan tarayıcı aracı çağrılarını otomatik olarak
o Node’a yönlendirebilir. Bu, uzak gateway’ler için varsayılan yoldur.

Notlar:

- Node ana makinesi, kendi yerel tarayıcı kontrol sunucusunu bir **vekil komut** aracılığıyla kullanıma sunar.
- Profiller, Node’un kendi `browser.profiles` yapılandırmasından gelir (yerel ile aynı).
- `nodeHost.browserProxy.allowProfiles` isteğe bağlıdır. Eski/varsayılan davranış için bunu boş bırakın: yapılandırılmış tüm profiller, profil oluşturma/silme rotaları dahil olmak üzere vekil üzerinden erişilebilir kalır.
- `nodeHost.browserProxy.allowProfiles` ayarlarsanız, OpenClaw bunu en az ayrıcalık sınırı olarak değerlendirir: yalnızca izin verilen profiller hedeflenebilir ve kalıcı profil oluşturma/silme rotaları vekil yüzeyinde engellenir.
- İstemiyorsanız devre dışı bırakın:
  - Node üzerinde: `nodeHost.browserProxy.enabled=false`
  - Gateway üzerinde: `gateway.nodes.browser.mode="off"`

## Browserless (barındırılan uzak CDP)

[Browserless](https://browserless.io), HTTPS ve WebSocket üzerinden
CDP bağlantı URL’leri sunan barındırılan bir Chromium hizmetidir. OpenClaw her iki biçimi de kullanabilir, ancak
uzak tarayıcı profili için en basit seçenek Browserless’ın bağlantı belgelerindeki
doğrudan WebSocket URL’sidir.

Örnek:

```json5
{
  browser: {
    enabled: true,
    defaultProfile: "browserless",
    remoteCdpTimeoutMs: 2000,
    remoteCdpHandshakeTimeoutMs: 4000,
    profiles: {
      browserless: {
        cdpUrl: "wss://production-sfo.browserless.io?token=<BROWSERLESS_API_KEY>",
        color: "#00AA00",
      },
    },
  },
}
```

Notlar:

- `<BROWSERLESS_API_KEY>` yerine gerçek Browserless belirtecinizi yazın.
- Browserless hesabınıza uygun bölge uç noktasını seçin (belgelerine bakın).
- Browserless size bir HTTPS temel URL’si veriyorsa, bunu doğrudan CDP bağlantısı için
  `wss://` biçimine dönüştürebilir veya HTTPS URL’sini koruyup OpenClaw’ın
  `/json/version` keşfini yapmasına izin verebilirsiniz.

## Doğrudan WebSocket CDP sağlayıcıları

Bazı barındırılan tarayıcı hizmetleri, standart HTTP tabanlı CDP keşfi (`/json/version`)
yerine **doğrudan WebSocket** uç noktası sunar. OpenClaw her ikisini de destekler:

- **HTTP(S) uç noktaları** — OpenClaw, WebSocket hata ayıklayıcı URL’sini keşfetmek için `/json/version` çağrısı yapar, ardından bağlanır.
- **WebSocket uç noktaları** (`ws://` / `wss://`) — OpenClaw doğrudan bağlanır,
  `/json/version` adımını atlar. Bunu
  [Browserless](https://browserless.io),
  [Browserbase](https://www.browserbase.com) gibi hizmetler veya size bir
  WebSocket URL’si veren herhangi bir sağlayıcı için kullanın.

### Browserbase

[Browserbase](https://www.browserbase.com), yerleşik CAPTCHA çözme, gizlilik modu ve konut tipi
vekiller ile headless tarayıcılar çalıştırmak için bir bulut platformudur.

```json5
{
  browser: {
    enabled: true,
    defaultProfile: "browserbase",
    remoteCdpTimeoutMs: 3000,
    remoteCdpHandshakeTimeoutMs: 5000,
    profiles: {
      browserbase: {
        cdpUrl: "wss://connect.browserbase.com?apiKey=<BROWSERBASE_API_KEY>",
        color: "#F97316",
      },
    },
  },
}
```

Notlar:

- [Kaydolun](https://www.browserbase.com/sign-up) ve [Overview panosundan](https://www.browserbase.com/overview) **API Key** değerinizi kopyalayın.
- `<BROWSERBASE_API_KEY>` yerine gerçek Browserbase API anahtarınızı yazın.
- Browserbase, WebSocket bağlantısında tarayıcı oturumunu otomatik olarak oluşturur; bu nedenle
  elle oturum oluşturma adımı gerekmez.
- Ücretsiz katman, aynı anda bir oturuma ve ayda bir tarayıcı saatine izin verir.
  Ücretli plan sınırları için [fiyatlandırmaya](https://www.browserbase.com/pricing) bakın.
- Tam API başvurusu,
  SDK kılavuzları ve entegrasyon örnekleri için [Browserbase belgelerine](https://docs.browserbase.com) bakın.

## Güvenlik

Temel fikirler:

- Tarayıcı kontrolü yalnızca loopback’tir; erişim Gateway kimlik doğrulaması veya Node eşleştirmesi üzerinden akar.
- Bağımsız loopback tarayıcı HTTP API’si **yalnızca paylaşılan gizli anahtar kimlik doğrulaması** kullanır:
  gateway bearer belirteci kimlik doğrulaması, `x-openclaw-password` veya
  yapılandırılmış gateway parolasıyla HTTP Basic auth.
- Tailscale Serve kimlik başlıkları ve `gateway.auth.mode: "trusted-proxy"`
  bu bağımsız loopback tarayıcı API’sinde **kimlik doğrulaması yapmaz**.
- Tarayıcı kontrolü etkinse ve yapılandırılmış bir paylaşılan gizli anahtar kimlik doğrulaması yoksa, OpenClaw
  başlangıçta `gateway.auth.token` değerini otomatik oluşturur ve bunu yapılandırmaya kalıcı olarak yazar.
- `gateway.auth.mode` zaten
  `password`, `none` veya `trusted-proxy` ise OpenClaw bu belirteci **otomatik oluşturmaz**.
- Gateway ve tüm Node ana makinelerini özel bir ağda (Tailscale) tutun; herkese açık erişimden kaçının.
- Uzak CDP URL’lerini/belirteçlerini gizli bilgi olarak değerlendirin; ortam değişkenlerini veya bir gizli anahtar yöneticisini tercih edin.

Uzak CDP ipuçları:

- Mümkün olduğunda şifreli uç noktaları (HTTPS veya WSS) ve kısa ömürlü belirteçleri tercih edin.
- Uzun ömürlü belirteçleri doğrudan yapılandırma dosyalarına gömmekten kaçının.

## Profiller (çoklu tarayıcı)

OpenClaw birden fazla adlandırılmış profili (yönlendirme yapılandırmaları) destekler. Profiller şunlar olabilir:

- **openclaw tarafından yönetilen**: kendi kullanıcı veri dizini + CDP bağlantı noktası olan özel bir Chromium tabanlı tarayıcı örneği
- **uzak**: açık bir CDP URL’si (başka yerde çalışan Chromium tabanlı tarayıcı)
- **mevcut oturum**: Chrome DevTools MCP otomatik bağlantısı üzerinden mevcut Chrome profiliniz

Varsayılanlar:

- Eksikse `openclaw` profili otomatik oluşturulur.
- `user` profili, Chrome MCP mevcut oturum bağlanması için yerleşiktir.
- `user` dışındaki mevcut oturum profilleri isteğe bağlıdır; bunları `--driver existing-session` ile oluşturun.
- Yerel CDP bağlantı noktaları varsayılan olarak **18800–18899** aralığından ayrılır.
- Bir profili silmek, yerel veri dizinini Çöp Kutusu’na taşır.

Tüm kontrol uç noktaları `?profile=<name>` kabul eder; CLI ise `--browser-profile` kullanır.

## Chrome DevTools MCP üzerinden mevcut oturum

OpenClaw ayrıca çalışan bir Chromium tabanlı tarayıcı profiline
resmi Chrome DevTools MCP sunucusu üzerinden bağlanabilir. Bu, o tarayıcı profilinde
zaten açık olan sekmeleri ve oturum açma durumunu yeniden kullanır.

Resmî arka plan ve kurulum başvuruları:

- [Chrome for Developers: Tarayıcı oturumunuzla Chrome DevTools MCP kullanın](https://developer.chrome.com/blog/chrome-devtools-mcp-debug-your-browser-session)
- [Chrome DevTools MCP README](https://github.com/ChromeDevTools/chrome-devtools-mcp)

Yerleşik profil:

- `user`

İsteğe bağlı: farklı bir ad, renk veya tarayıcı veri dizini istiyorsanız kendi özel mevcut oturum profilinizi oluşturun.

Varsayılan davranış:

- Yerleşik `user` profili, varsayılan yerel Google Chrome profilini hedefleyen Chrome MCP otomatik bağlantısını kullanır.

Brave, Edge, Chromium veya varsayılan olmayan bir Chrome profili için `userDataDir` kullanın:

```json5
{
  browser: {
    profiles: {
      brave: {
        driver: "existing-session",
        attachOnly: true,
        userDataDir: "~/Library/Application Support/BraveSoftware/Brave-Browser",
        color: "#FB542B",
      },
    },
  },
}
```

Ardından eşleşen tarayıcıda:

1. O tarayıcının uzak hata ayıklama için denetleme sayfasını açın.
2. Uzak hata ayıklamayı etkinleştirin.
3. Tarayıcıyı açık tutun ve OpenClaw bağlandığında bağlantı istemini onaylayın.

Yaygın denetleme sayfaları:

- Chrome: `chrome://inspect/#remote-debugging`
- Brave: `brave://inspect/#remote-debugging`
- Edge: `edge://inspect/#remote-debugging`

Canlı bağlanma smoke testi:

```bash
openclaw browser --browser-profile user start
openclaw browser --browser-profile user status
openclaw browser --browser-profile user tabs
openclaw browser --browser-profile user snapshot --format ai
```

Başarılı durumda görünmesi gerekenler:

- `status`, `driver: existing-session` gösterir
- `status`, `transport: chrome-mcp` gösterir
- `status`, `running: true` gösterir
- `tabs`, zaten açık olan tarayıcı sekmelerinizi listeler
- `snapshot`, seçilen canlı sekmeden ref değerleri döndürür

Bağlanma çalışmıyorsa kontrol edilmesi gerekenler:

- hedef Chromium tabanlı tarayıcı sürümü `144+` olmalı
- o tarayıcının denetleme sayfasında uzak hata ayıklama etkin olmalı
- tarayıcı bağlanma onay istemini göstermiş olmalı ve siz kabul etmiş olmalısınız
- `openclaw doctor`, eski uzantı tabanlı tarayıcı yapılandırmasını geçirir ve
  varsayılan otomatik bağlanma profilleri için Chrome’un yerel olarak kurulu olup olmadığını denetler, ancak
  tarayıcı tarafında uzak hata ayıklamayı sizin için etkinleştiremez

Aracı kullanımı:

- Kullanıcının oturum açılmış tarayıcı durumuna ihtiyaç duyduğunuzda `profile="user"` kullanın.
- Özel bir mevcut oturum profili kullanıyorsanız, o açık profil adını geçin.
- Bu modu yalnızca kullanıcı bağlanma
  istemini onaylamak için bilgisayar başındaysa seçin.
- Gateway veya Node ana makinesi `npx chrome-devtools-mcp@latest --autoConnect` çalıştırabilir

Notlar:

- Bu yol, oturum açılmış tarayıcı oturumunuz içinde işlem yapabildiği için
  yalıtılmış `openclaw` profiline kıyasla daha yüksek risklidir.
- OpenClaw bu sürücü için tarayıcı başlatmaz; yalnızca mevcut bir
  oturuma bağlanır.
- OpenClaw burada resmî Chrome DevTools MCP `--autoConnect` akışını kullanır. Eğer
  `userDataDir` ayarlıysa, OpenClaw bu açık Chromium kullanıcı veri dizinini
  hedeflemek için bunu iletir.
- Mevcut oturum ekran görüntüleri; sayfa yakalamalarını ve anlık görüntülerden
  `--ref` öğe yakalamalarını destekler, ancak CSS `--element` seçicilerini desteklemez.
- Mevcut oturum sayfa ekran görüntüleri, Playwright olmadan Chrome MCP üzerinden çalışır.
  Ref tabanlı öğe ekran görüntüleri (`--ref`) de burada çalışır, ancak `--full-page`
  `--ref` veya `--element` ile birlikte kullanılamaz.
- Mevcut oturum eylemleri, yönetilen tarayıcı
  yoluna kıyasla hâlâ daha sınırlıdır:
  - `click`, `type`, `hover`, `scrollIntoView`, `drag` ve `select`,
    CSS seçicileri yerine anlık görüntü ref’leri gerektirir
  - `click` yalnızca sol düğmeyi destekler (düğme geçersiz kılmaları veya değiştirici tuşlar yok)
  - `type`, `slowly=true` desteği sunmaz; `fill` veya `press` kullanın
  - `press`, `delayMs` desteği sunmaz
  - `hover`, `scrollIntoView`, `drag`, `select`, `fill` ve `evaluate`,
    çağrı başına zaman aşımı geçersiz kılmalarını desteklemez
  - `select` şu anda yalnızca tek bir değeri destekler
- Mevcut oturum `wait --url`, diğer tarayıcı sürücüleri gibi tam eşleşme, alt dize ve glob kalıplarını destekler. `wait --load networkidle` henüz desteklenmiyor.
- Mevcut oturum yükleme kancaları `ref` veya `inputRef` gerektirir, bir seferde bir dosyayı destekler ve CSS `element` hedeflemeyi desteklemez.
- Mevcut oturum iletişim kutusu kancaları zaman aşımı geçersiz kılmalarını desteklemez.
- Toplu eylemler, PDF dışa aktarma, indirme yakalama ve `responsebody` dahil olmak üzere bazı özellikler hâlâ yönetilen tarayıcı yolunu gerektirir.
- Mevcut oturum ana makineye özeldir. Chrome farklı bir makinede veya
  farklı bir ağ ad alanında bulunuyorsa, bunun yerine uzak CDP veya bir Node ana makinesi kullanın.

## Yalıtım garantileri

- **Özel kullanıcı veri dizini**: kişisel tarayıcı profilinize asla dokunmaz.
- **Özel bağlantı noktaları**: geliştirme iş akışlarıyla çakışmaları önlemek için `9222` kullanılmaz.
- **Deterministik sekme kontrolü**: sekmeleri “son sekme” yerine `targetId` ile hedefler.

## Tarayıcı seçimi

Yerel olarak başlatılırken OpenClaw, mevcut olan ilk tarayıcıyı seçer:

1. Chrome
2. Brave
3. Edge
4. Chromium
5. Chrome Canary

`browser.executablePath` ile bunu geçersiz kılabilirsiniz.

Platformlar:

- macOS: `/Applications` ve `~/Applications` denetlenir.
- Linux: `google-chrome`, `brave`, `microsoft-edge`, `chromium` vb. aranır.
- Windows: yaygın kurulum konumları denetlenir.

## Kontrol API’si (isteğe bağlı)

Yalnızca yerel entegrasyonlar için Gateway küçük bir loopback HTTP API’si sunar:

- Durum/başlat/durdur: `GET /`, `POST /start`, `POST /stop`
- Sekmeler: `GET /tabs`, `POST /tabs/open`, `POST /tabs/focus`, `DELETE /tabs/:targetId`
- Anlık görüntü/ekran görüntüsü: `GET /snapshot`, `POST /screenshot`
- Eylemler: `POST /navigate`, `POST /act`
- Kancalar: `POST /hooks/file-chooser`, `POST /hooks/dialog`
- İndirmeler: `POST /download`, `POST /wait/download`
- Hata ayıklama: `GET /console`, `POST /pdf`
- Hata ayıklama: `GET /errors`, `GET /requests`, `POST /trace/start`, `POST /trace/stop`, `POST /highlight`
- Ağ: `POST /response/body`
- Durum: `GET /cookies`, `POST /cookies/set`, `POST /cookies/clear`
- Durum: `GET /storage/:kind`, `POST /storage/:kind/set`, `POST /storage/:kind/clear`
- Ayarlar: `POST /set/offline`, `POST /set/headers`, `POST /set/credentials`, `POST /set/geolocation`, `POST /set/media`, `POST /set/timezone`, `POST /set/locale`, `POST /set/device`

Tüm uç noktalar `?profile=<name>` kabul eder.

Paylaşılan gizli anahtar gateway kimlik doğrulaması yapılandırılmışsa, tarayıcı HTTP rotaları da kimlik doğrulaması gerektirir:

- `Authorization: Bearer <gateway token>`
- `x-openclaw-password: <gateway password>` veya bu parola ile HTTP Basic auth

Notlar:

- Bu bağımsız loopback tarayıcı API’si, trusted-proxy veya
  Tailscale Serve kimlik başlıklarını **kullanmaz**.
- `gateway.auth.mode` değeri `none` veya `trusted-proxy` ise, bu loopback tarayıcı
  rotaları bu kimlik taşıyan kipleri devralmaz; bunları yalnızca loopback olarak tutun.

### `/act` hata sözleşmesi

`POST /act`, rota düzeyindeki doğrulama ve
ilke hataları için yapılandırılmış bir hata yanıtı kullanır:

```json
{ "error": "<message>", "code": "ACT_*" }
```

Geçerli `code` değerleri:

- `ACT_KIND_REQUIRED` (HTTP 400): `kind` eksik veya tanınmıyor.
- `ACT_INVALID_REQUEST` (HTTP 400): eylem yükü normalleştirme veya doğrulamadan geçemedi.
- `ACT_SELECTOR_UNSUPPORTED` (HTTP 400): `selector`, desteklenmeyen bir eylem türüyle kullanıldı.
- `ACT_EVALUATE_DISABLED` (HTTP 403): `evaluate` (veya `wait --fn`) yapılandırma tarafından devre dışı bırakıldı.
- `ACT_TARGET_ID_MISMATCH` (HTTP 403): üst düzey veya toplu `targetId`, istek hedefiyle çakışıyor.
- `ACT_EXISTING_SESSION_UNSUPPORTED` (HTTP 501): eylem, mevcut oturum profilleri için desteklenmiyor.

Diğer çalışma zamanı hataları, `code` alanı olmadan hâlâ
`{ "error": "<message>" }` döndürebilir.

### Playwright gereksinimi

Bazı özellikler (navigate/act/AI snapshot/role snapshot, öğe ekran görüntüleri,
PDF) Playwright gerektirir. Playwright yüklü değilse, bu uç noktalar
açık bir 501 hatası döndürür.

Playwright olmadan hâlâ çalışanlar:

- ARIA anlık görüntüleri
- Sekme başına CDP
  WebSocket mevcut olduğunda yönetilen `openclaw` tarayıcısı için sayfa ekran görüntüleri
- `existing-session` / Chrome MCP profilleri için sayfa ekran görüntüleri
- Anlık görüntü çıktısından `existing-session` ref tabanlı ekran görüntüleri (`--ref`)

Hâlâ Playwright gerektirenler:

- `navigate`
- `act`
- AI anlık görüntüleri / rol anlık görüntüleri
- CSS seçicili öğe ekran görüntüleri (`--element`)
- tam tarayıcı PDF dışa aktarma

Öğe ekran görüntüleri ayrıca `--full-page` seçeneğini de reddeder; rota
`fullPage is not supported for element screenshots` döndürür.

`Playwright is not available in this gateway build` görürseniz, tam
Playwright paketini (`playwright-core` değil) yükleyin ve gateway’i yeniden başlatın ya da
OpenClaw’ı tarayıcı desteğiyle yeniden kurun.

#### Docker Playwright kurulumu

Gateway’iniz Docker içinde çalışıyorsa `npx playwright` kullanmayın (npm override çakışmaları).
Bunun yerine yerleşik CLI’yi kullanın:

```bash
docker compose run --rm openclaw-cli \
  node /app/node_modules/playwright-core/cli.js install chromium
```

Tarayıcı indirmelerini kalıcı yapmak için `PLAYWRIGHT_BROWSERS_PATH` ayarlayın (örneğin,
`/home/node/.cache/ms-playwright`) ve `/home/node` dizininin
`OPENCLAW_HOME_VOLUME` veya bir bind mount ile kalıcı olduğundan emin olun. Bkz. [Docker](/tr/install/docker).

## Nasıl çalışır (dahili)

Üst düzey akış:

- Küçük bir **kontrol sunucusu** HTTP isteklerini kabul eder.
- **CDP** üzerinden Chromium tabanlı tarayıcılara (Chrome/Brave/Edge/Chromium) bağlanır.
- Gelişmiş eylemler için (tıklama/yazma/anlık görüntü/PDF), CDP üzerinde
  **Playwright** kullanır.
- Playwright eksik olduğunda yalnızca Playwright gerektirmeyen işlemler kullanılabilir.

Bu tasarım, yerel/uzak tarayıcılar ile profilleri değiştirmenize izin verirken
aracıyı kararlı, deterministik bir arayüz üzerinde tutar.

## CLI hızlı başvuru

Tüm komutlar belirli bir profili hedeflemek için `--browser-profile <name>` kabul eder.
Tüm komutlar ayrıca makine tarafından okunabilir çıktı için `--json` da kabul eder (kararlı yükler).

Temeller:

- `openclaw browser status`
- `openclaw browser start`
- `openclaw browser stop`
- `openclaw browser tabs`
- `openclaw browser tab`
- `openclaw browser tab new`
- `openclaw browser tab select 2`
- `openclaw browser tab close 2`
- `openclaw browser open https://example.com`
- `openclaw browser focus abcd1234`
- `openclaw browser close abcd1234`

İnceleme:

- `openclaw browser screenshot`
- `openclaw browser screenshot --full-page`
- `openclaw browser screenshot --ref 12`
- `openclaw browser screenshot --ref e12`
- `openclaw browser snapshot`
- `openclaw browser snapshot --format aria --limit 200`
- `openclaw browser snapshot --interactive --compact --depth 6`
- `openclaw browser snapshot --efficient`
- `openclaw browser snapshot --labels`
- `openclaw browser snapshot --selector "#main" --interactive`
- `openclaw browser snapshot --frame "iframe#main" --interactive`
- `openclaw browser console --level error`

Yaşam döngüsü notu:

- Yalnızca bağlanma ve uzak CDP profilleri için `openclaw browser stop` testlerden sonra yine de
  doğru temizleme komutudur. Alttaki
  tarayıcıyı sonlandırmak yerine etkin kontrol oturumunu kapatır ve
  geçici öykünme geçersiz kılmalarını temizler.
- `openclaw browser errors --clear`
- `openclaw browser requests --filter api --clear`
- `openclaw browser pdf`
- `openclaw browser responsebody "**/api" --max-chars 5000`

Eylemler:

- `openclaw browser navigate https://example.com`
- `openclaw browser resize 1280 720`
- `openclaw browser click 12 --double`
- `openclaw browser click e12 --double`
- `openclaw browser type 23 "hello" --submit`
- `openclaw browser press Enter`
- `openclaw browser hover 44`
- `openclaw browser scrollintoview e12`
- `openclaw browser drag 10 11`
- `openclaw browser select 9 OptionA OptionB`
- `openclaw browser download e12 report.pdf`
- `openclaw browser waitfordownload report.pdf`
- `openclaw browser upload /tmp/openclaw/uploads/file.pdf`
- `openclaw browser fill --fields '[{"ref":"1","type":"text","value":"Ada"}]'`
- `openclaw browser dialog --accept`
- `openclaw browser wait --text "Done"`
- `openclaw browser wait "#main" --url "**/dash" --load networkidle --fn "window.ready===true"`
- `openclaw browser evaluate --fn '(el) => el.textContent' --ref 7`
- `openclaw browser highlight e12`
- `openclaw browser trace start`
- `openclaw browser trace stop`

Durum:

- `openclaw browser cookies`
- `openclaw browser cookies set session abc123 --url "https://example.com"`
- `openclaw browser cookies clear`
- `openclaw browser storage local get`
- `openclaw browser storage local set theme dark`
- `openclaw browser storage session clear`
- `openclaw browser set offline on`
- `openclaw browser set headers --headers-json '{"X-Debug":"1"}'`
- `openclaw browser set credentials user pass`
- `openclaw browser set credentials --clear`
- `openclaw browser set geo 37.7749 -122.4194 --origin "https://example.com"`
- `openclaw browser set geo --clear`
- `openclaw browser set media dark`
- `openclaw browser set timezone America/New_York`
- `openclaw browser set locale en-US`
- `openclaw browser set device "iPhone 14"`

Notlar:

- `upload` ve `dialog` **hazırlama** çağrılarıdır; dosya seçiciyi/iletişim kutusunu
  tetikleyen tıklama/basma işleminden önce çalıştırın.
- İndirme ve izleme çıktı yolları OpenClaw geçici kökleriyle sınırlıdır:
  - izler: `/tmp/openclaw` (yedek: `${os.tmpdir()}/openclaw`)
  - indirmeler: `/tmp/openclaw/downloads` (yedek: `${os.tmpdir()}/openclaw/downloads`)
- Yükleme yolları bir OpenClaw geçici yükleme köküyle sınırlıdır:
  - yüklemeler: `/tmp/openclaw/uploads` (yedek: `${os.tmpdir()}/openclaw/uploads`)
- `upload`, dosya girişlerini doğrudan `--input-ref` veya `--element` ile de ayarlayabilir.
- `snapshot`:
  - `--format ai` (Playwright yüklüyken varsayılan): sayısal ref’ler içeren bir AI anlık görüntüsü döndürür (`aria-ref="<n>"`).
  - `--format aria`: erişilebilirlik ağacını döndürür (ref yok; yalnızca inceleme için).
  - `--efficient` (veya `--mode efficient`): sıkıştırılmış rol anlık görüntüsü ön ayarıdır (interactive + compact + depth + daha düşük maxChars).
  - Yapılandırma varsayılanı (yalnızca araç/CLI): çağıran mod geçmezse verimli anlık görüntüler kullanmak için `browser.snapshotDefaults.mode: "efficient"` ayarlayın (bkz. [Gateway configuration](/tr/gateway/configuration-reference#browser)).
  - Rol anlık görüntüsü seçenekleri (`--interactive`, `--compact`, `--depth`, `--selector`) `ref=e12` gibi ref’lerle rol tabanlı bir anlık görüntüyü zorlar.
  - `--frame "<iframe selector>"`, rol anlık görüntülerini bir iframe ile sınırlar (`e12` gibi rol ref’leriyle eşleşir).
  - `--interactive`, etkileşimli öğelerin düz, kolay seçilebilir bir listesini verir (eylem yürütmek için en iyisi).
  - `--labels`, üstüne ref etiketleri bindirilmiş yalnızca görüntü alanı ekran görüntüsü ekler (`MEDIA:<path>` yazdırır).
- `click`/`type`/vb. `snapshot` çıktısından bir `ref` gerektirir (sayısal `12` veya rol ref’i `e12`).
  Eylemler için CSS seçicileri bilerek desteklenmez.

## Anlık görüntüler ve ref’ler

OpenClaw iki “anlık görüntü” stilini destekler:

- **AI anlık görüntüsü (sayısal ref’ler)**: `openclaw browser snapshot` (varsayılan; `--format ai`)
  - Çıktı: sayısal ref’ler içeren bir metin anlık görüntüsü.
  - Eylemler: `openclaw browser click 12`, `openclaw browser type 23 "hello"`.
  - Dahili olarak ref, Playwright’ın `aria-ref` özelliği üzerinden çözülür.

- **Rol anlık görüntüsü (`e12` gibi rol ref’leri)**: `openclaw browser snapshot --interactive` (veya `--compact`, `--depth`, `--selector`, `--frame`)
  - Çıktı: `[ref=e12]` (ve isteğe bağlı `[nth=1]`) içeren rol tabanlı bir liste/ağaç.
  - Eylemler: `openclaw browser click e12`, `openclaw browser highlight e12`.
  - Dahili olarak ref, `getByRole(...)` ile (`yinelenenler için `nth()` ile birlikte) çözülür.
  - Üstüne bindirilmiş `e12` etiketleri olan bir görüntü alanı ekran görüntüsü eklemek için `--labels` ekleyin.

Ref davranışı:

- Ref’ler **gezinmeler arasında kararlı değildir**; bir şey başarısız olursa `snapshot` komutunu yeniden çalıştırın ve yeni bir ref kullanın.
- Rol anlık görüntüsü `--frame` ile alındıysa, rol ref’leri bir sonraki rol anlık görüntüsüne kadar o iframe ile sınırlıdır.

## Bekleme güçlendirmeleri

Yalnızca zaman/metin üzerinde beklemek zorunda değilsiniz:

- URL bekleme (Playwright tarafından desteklenen glob’lar):
  - `openclaw browser wait --url "**/dash"`
- Yükleme durumunu bekleme:
  - `openclaw browser wait --load networkidle`
- JS koşulunu bekleme:
  - `openclaw browser wait --fn "window.ready===true"`
- Bir seçicinin görünür olmasını bekleme:
  - `openclaw browser wait "#main"`

Bunlar birleştirilebilir:
__OC_I18N_900013__
## Hata ayıklama iş akışları

Bir eylem başarısız olduğunda (ör. “not visible”, “strict mode violation”, “covered”):

1. `openclaw browser snapshot --interactive`
2. `click <ref>` / `type <ref>` kullanın (interactive modda rol ref’lerini tercih edin)
3. Hâlâ başarısız olursa: Playwright’ın neyi hedeflediğini görmek için `openclaw browser highlight <ref>`
4. Sayfa garip davranıyorsa:
   - `openclaw browser errors --clear`
   - `openclaw browser requests --filter api --clear`
5. Derin hata ayıklama için bir iz kaydedin:
   - `openclaw browser trace start`
   - sorunu yeniden üretin
   - `openclaw browser trace stop` (`TRACE:<path>` yazdırır)

## JSON çıktısı

`--json`, betikler ve yapılandırılmış araçlar içindir.

Örnekler:
__OC_I18N_900014__
JSON içindeki rol anlık görüntüleri `refs` ile birlikte küçük bir `stats` bloğu da içerir (lines/chars/refs/interactive); böylece araçlar yük boyutunu ve yoğunluğu değerlendirebilir.

## Durum ve ortam ayarları

Bunlar “siteyi X gibi davranacak hâle getir” iş akışları için faydalıdır:

- Çerezler: `cookies`, `cookies set`, `cookies clear`
- Depolama: `storage local|session get|set|clear`
- Çevrimdışı: `set offline on|off`
- Başlıklar: `set headers --headers-json '{"X-Debug":"1"}'` (eski `set headers --json '{"X-Debug":"1"}'` desteği sürer)
- HTTP Basic auth: `set credentials user pass` (veya `--clear`)
- Coğrafi konum: `set geo <lat> <lon> --origin "https://example.com"` (veya `--clear`)
- Medya: `set media dark|light|no-preference|none`
- Saat dilimi / yerel ayar: `set timezone ...`, `set locale ...`
- Cihaz / görüntü alanı:
  - `set device "iPhone 14"` (Playwright cihaz ön ayarları)
  - `set viewport 1280 720`

## Güvenlik ve gizlilik

- openclaw tarayıcı profili, oturum açılmış oturumlar içerebilir; bunu hassas kabul edin.
- `browser act kind=evaluate` / `openclaw browser evaluate` ve `wait --fn`
  sayfa bağlamında rastgele JavaScript çalıştırır. Prompt injection bunu yönlendirebilir.
  Buna ihtiyacınız yoksa `browser.evaluateEnabled=false` ile devre dışı bırakın.
- Girişler ve anti-bot notları (X/Twitter vb.) için bkz. [Tarayıcı girişi + X/Twitter paylaşımı](/tools/browser-login).
- Gateway/Node ana makinesini gizli tutun (yalnızca loopback veya tailnet).
- Uzak CDP uç noktaları güçlüdür; tünelleyin ve koruyun.

Katı kip örneği (varsayılan olarak özel/dahili hedefleri engelle):
__OC_I18N_900015__
## Sorun giderme

Linux’a özgü sorunlar için (özellikle snap Chromium), bkz.
[Tarayıcı sorun giderme](/tools/browser-linux-troubleshooting).

WSL2 Gateway + Windows Chrome bölünmüş ana makine kurulumları için bkz.
[WSL2 + Windows + uzak Chrome CDP sorun giderme](/tools/browser-wsl2-windows-remote-cdp-troubleshooting).

### CDP başlatma hatası ve gezinme SSRF engeli

Bunlar farklı hata sınıflarıdır ve farklı kod yollarına işaret ederler.

- **CDP başlatma veya hazır olma hatası**, OpenClaw’ın tarayıcı kontrol düzleminin sağlıklı olduğunu doğrulayamadığı anlamına gelir.
- **Gezinme SSRF engeli**, tarayıcı kontrol düzleminin sağlıklı olduğu ancak bir sayfa gezinme hedefinin ilke tarafından reddedildiği anlamına gelir.

Yaygın örnekler:

- CDP başlatma veya hazır olma hatası:
  - `Chrome CDP websocket for profile "openclaw" is not reachable after start`
  - `Remote CDP for profile "<name>" is not reachable at <cdpUrl>`
- Gezinme SSRF engeli:
  - `open`, `navigate`, anlık görüntü veya sekme açma akışları tarayıcı/ağ ilkesi hatasıyla başarısız olurken `start` ve `tabs` yine de çalışır

İkisini ayırmak için şu en kısa diziyi kullanın:
__OC_I18N_900016__
Sonuçları okuma biçimi:

- `start`, `not reachable after start` ile başarısız olursa önce CDP hazır olma durumunu sorun giderin.
- `start` başarılı olur ama `tabs` başarısız olursa, kontrol düzlemi hâlâ sağlıklı değildir. Bunu sayfa gezinme sorunu değil, bir CDP erişilebilirlik sorunu olarak değerlendirin.
- `start` ve `tabs` başarılı olur ama `open` veya `navigate` başarısız olursa, tarayıcı kontrol düzlemi çalışıyordur ve hata gezinme ilkesi veya hedef sayfadadır.
- `start`, `tabs` ve `open` üçü de başarılı olursa, temel yönetilen tarayıcı kontrol yolu sağlıklıdır.

Önemli davranış ayrıntıları:

- `browser.ssrfPolicy` yapılandırmasanız bile tarayıcı yapılandırması varsayılan olarak fail-closed bir SSRF ilke nesnesi kullanır.
- Yerel loopback `openclaw` yönetilen profili için, CDP sağlık kontrolleri OpenClaw’ın kendi yerel kontrol düzlemi için tarayıcı SSRF erişilebilirlik zorlamasını bilerek atlar.
- Gezinme koruması ayrıdır. `start` veya `tabs` sonucunun başarılı olması, daha sonraki bir `open` veya `navigate` hedefinin izinli olduğu anlamına gelmez.

Güvenlik rehberi:

- Varsayılan olarak tarayıcı SSRF ilkesini **gevşetmeyin**.
- Geniş özel ağ erişimi yerine `hostnameAllowlist` veya `allowedHostnames` gibi dar ana makine istisnalarını tercih edin.
- `dangerouslyAllowPrivateNetwork: true` seçeneğini yalnızca özel ağ tarayıcı erişiminin gerekli olduğu ve gözden geçirildiği, bilerek güvenilen ortamlarda kullanın.

Örnek: gezinme engellendi, kontrol düzlemi sağlıklı

- `start` başarılı olur
- `tabs` başarılı olur
- `open http://internal.example` başarısız olur

Bu genellikle tarayıcı başlangıcının düzgün olduğu ve gezinme hedefinin ilke incelemesi gerektirdiği anlamına gelir.

Örnek: gezinme önemli olmadan önce başlangıç engellendi

- `start`, `not reachable after start` ile başarısız olur
- `tabs` de başarısız olur veya çalıştırılamaz

Bu, sayfa URL izin listesi sorununa değil, tarayıcı başlatma veya CDP erişilebilirliğine işaret eder.

## Aracı araçları + kontrolün nasıl çalıştığı

Aracı, tarayıcı otomasyonu için **tek bir araç** alır:

- `browser` — status/start/stop/tabs/open/focus/close/snapshot/screenshot/navigate/act

Eşleme şekli:

- `browser snapshot`, kararlı bir kullanıcı arayüzü ağacı döndürür (AI veya ARIA).
- `browser act`, tıklama/yazma/sürükleme/seçme işlemleri için anlık görüntü `ref` kimliklerini kullanır.
- `browser screenshot`, pikselleri yakalar (tam sayfa veya öğe).
- `browser` şunları kabul eder:
  - adlandırılmış bir tarayıcı profilini seçmek için `profile` (openclaw, chrome veya uzak CDP).
  - tarayıcının nerede bulunduğunu seçmek için `target` (`sandbox` | `host` | `node`).
  - Sandbox oturumlarında `target: "host"` için `agents.defaults.sandbox.browser.allowHostControl=true` gerekir.
  - `target` belirtilmezse: sandbox oturumları varsayılan olarak `sandbox`, sandbox olmayan oturumlar varsayılan olarak `host` kullanır.
  - Tarayıcı özellikli bir Node bağlıysa, `target="host"` veya `target="node"` ile sabitlemediğiniz sürece araç otomatik olarak ona yönlenebilir.

Bu, aracıyı deterministik tutar ve kırılgan seçicilerden kaçınır.

## İlgili

- [Araçlara Genel Bakış](/tr/tools) — mevcut tüm aracı araçları
- [Sandboxing](/tr/gateway/sandboxing) — sandbox ortamlarında tarayıcı kontrolü
- [Güvenlik](/tr/gateway/security) — tarayıcı kontrolü riskleri ve güçlendirme
