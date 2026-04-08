---
read_when:
    - OpenClaw çalışmıyor ve çözüme en hızlı yolu bulmanız gerekiyor
    - Ayrıntılı runbook'lara geçmeden önce bir triyaj akışı istiyorsunuz
summary: OpenClaw için belirti odaklı ilk sorun giderme merkezi
title: Genel Sorun Giderme
x-i18n:
    generated_at: "2026-04-08T02:16:16Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8abda90ef80234c2f91a51c5e1f2c004d4a4da12a5d5631b5927762550c6d5e3
    source_path: help/troubleshooting.md
    workflow: 15
---

# Sorun Giderme

Yalnızca 2 dakikanız varsa, bu sayfayı bir triyaj giriş noktası olarak kullanın.

## İlk 60 saniye

Bu tam adım sırasını belirtilen sırayla çalıştırın:

```bash
openclaw status
openclaw status --all
openclaw gateway probe
openclaw gateway status
openclaw doctor
openclaw channels status --probe
openclaw logs --follow
```

İyi çıktının tek satırlık özeti:

- `openclaw status` → yapılandırılmış kanalları ve belirgin auth hatası olmadığını gösterir.
- `openclaw status --all` → tam rapor mevcuttur ve paylaşılabilir.
- `openclaw gateway probe` → beklenen gateway hedefine erişilebilir (`Reachable: yes`). `RPC: limited - missing scope: operator.read`, bozulmuş tanılama anlamına gelir; bağlantı hatası değildir.
- `openclaw gateway status` → `Runtime: running` ve `RPC probe: ok`.
- `openclaw doctor` → engelleyici yapılandırma/hizmet hatası yok.
- `openclaw channels status --probe` → erişilebilir gateway, hesap başına canlı taşıma durumu ile `works` veya `audit ok` gibi probe/audit sonuçlarını döndürür; gateway'e erişilemiyorsa komut yalnızca yapılandırma özetlerine geri döner.
- `openclaw logs --follow` → düzenli etkinlik vardır, tekrarlayan ölümcül hata yoktur.

## Anthropic uzun bağlam 429

Şunu görüyorsanız:
`HTTP 429: rate_limit_error: Extra usage is required for long context requests`,
şuraya gidin: [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/tr/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context).

## Yerel OpenAI uyumlu backend doğrudan çalışıyor ama OpenClaw'da başarısız oluyor

Yerel veya self-hosted `/v1` backend'iniz küçük doğrudan
`/v1/chat/completions` yoklamalarına yanıt veriyor ancak `openclaw infer model run` veya normal
agent dönüşlerinde başarısız oluyorsa:

1. Hata, `messages[].content` için string beklendiğini söylüyorsa,
   `models.providers.<provider>.models[].compat.requiresStringContent: true` ayarlayın.
2. Backend hâlâ yalnızca OpenClaw agent dönüşlerinde başarısız oluyorsa,
   `models.providers.<provider>.models[].compat.supportsTools: false` ayarlayın ve yeniden deneyin.
3. Çok küçük doğrudan çağrılar hâlâ çalışıyor ama daha büyük OpenClaw istemleri backend'i çökertiyorsa,
   kalan sorunu upstream model/sunucu sınırlaması olarak değerlendirin ve ayrıntılı runbook'a devam edin:
   [/gateway/troubleshooting#local-openai-compatible-backend-passes-direct-probes-but-agent-runs-fail](/tr/gateway/troubleshooting#local-openai-compatible-backend-passes-direct-probes-but-agent-runs-fail)

## Eksik openclaw extensions nedeniyle plugin kurulumu başarısız oluyor

Kurulum `package.json missing openclaw.extensions` hatasıyla başarısız oluyorsa, plugin paketi
OpenClaw'ın artık kabul etmediği eski bir şekli kullanıyordur.

Plugin paketindeki düzeltme:

1. `package.json` içine `openclaw.extensions` ekleyin.
2. Girdileri derlenmiş çalışma zamanı dosyalarına yönlendirin (genellikle `./dist/index.js`).
3. Plugin'i yeniden yayımlayın ve `openclaw plugins install <package>` komutunu tekrar çalıştırın.

Örnek:

```json
{
  "name": "@openclaw/my-plugin",
  "version": "1.2.3",
  "openclaw": {
    "extensions": ["./dist/index.js"]
  }
}
```

Başvuru: [Plugin mimarisi](/tr/plugins/architecture)

## Karar ağacı

```mermaid
flowchart TD
  A[OpenClaw çalışmıyor] --> B{İlk önce ne bozuluyor}
  B --> C[Yanıt yok]
  B --> D[Dashboard veya Control UI bağlanmıyor]
  B --> E[Gateway başlamıyor veya hizmet çalışmıyor]
  B --> F[Kanal bağlanıyor ama mesajlar akmıyor]
  B --> G[Cron veya heartbeat tetiklenmedi ya da teslim edilmedi]
  B --> H[Node eşlenmiş ama camera canvas screen exec aracı başarısız oluyor]
  B --> I[Browser aracı başarısız oluyor]

  C --> C1[/Yanıt yok bölümü/]
  D --> D1[/Control UI bölümü/]
  E --> E1[/Gateway bölümü/]
  F --> F1[/Kanal akışı bölümü/]
  G --> G1[/Otomasyon bölümü/]
  H --> H1[/Node araçları bölümü/]
  I --> I1[/Browser bölümü/]
```

<AccordionGroup>
  <Accordion title="Yanıt yok">
    ```bash
    openclaw status
    openclaw gateway status
    openclaw channels status --probe
    openclaw pairing list --channel <channel> [--account <id>]
    openclaw logs --follow
    ```

    İyi çıktı şöyle görünür:

    - `Runtime: running`
    - `RPC probe: ok`
    - Kanalınızda taşıma bağlı görünür ve desteklendiği yerlerde `channels status --probe` içinde `works` veya `audit ok` görünür
    - Gönderici onaylanmış görünür (veya DM ilkesi açık/allowlist durumundadır)

    Yaygın günlük imzaları:

    - `drop guild message (mention required` → mention geçidi Discord'da mesajı engelledi.
    - `pairing request` → gönderici onaylanmamış ve DM pairing onayı bekliyor.
    - kanal günlüklerinde `blocked` / `allowlist` → gönderici, oda veya grup filtrelenmiş.

    Ayrıntılı sayfalar:

    - [/gateway/troubleshooting#no-replies](/tr/gateway/troubleshooting#no-replies)
    - [/channels/troubleshooting](/tr/channels/troubleshooting)
    - [/channels/pairing](/tr/channels/pairing)

  </Accordion>

  <Accordion title="Dashboard veya Control UI bağlanmıyor">
    ```bash
    openclaw status
    openclaw gateway status
    openclaw logs --follow
    openclaw doctor
    openclaw channels status --probe
    ```

    İyi çıktı şöyle görünür:

    - `openclaw gateway status` içinde `Dashboard: http://...` gösterilir
    - `RPC probe: ok`
    - Günlüklerde auth döngüsü yok

    Yaygın günlük imzaları:

    - `device identity required` → HTTP/güvenli olmayan bağlam, cihaz auth işlemini tamamlayamaz.
    - `origin not allowed` → tarayıcı `Origin` değeri, Control UI gateway hedefi için izinli değil.
    - yeniden deneme ipuçlarıyla birlikte `AUTH_TOKEN_MISMATCH` (`canRetryWithDeviceToken=true`) → güvenilir bir device-token yeniden denemesi otomatik olarak gerçekleşebilir.
    - Bu önbelleğe alınmış token yeniden denemesi, eşlenmiş cihaz token'ı ile saklanan önbellekteki kapsam kümesini yeniden kullanır. Açık `deviceToken` / açık `scopes` çağıranları ise istenen kapsam kümesini korur.
    - Eşzamansız Tailscale Serve Control UI yolunda, aynı `{scope, ip}` için başarısız denemeler sınırlayıcı başarısızlığı kaydetmeden önce serileştirilir; bu nedenle ikinci bir eşzamanlı kötü yeniden deneme zaten `retry later` gösterebilir.
    - localhost tarayıcı origin'inden gelen `too many failed authentication attempts (retry later)` → aynı `Origin` üzerinden tekrarlanan başarısızlıklar geçici olarak kilitlenir; başka bir localhost origin'i ayrı bir havuz kullanır.
    - bu yeniden denemeden sonra tekrarlanan `unauthorized` → yanlış token/parola, auth kipi uyuşmazlığı veya eski paired device token.
    - `gateway connect failed:` → UI yanlış URL/portu hedefliyor veya gateway'e erişilemiyor.

    Ayrıntılı sayfalar:

    - [/gateway/troubleshooting#dashboard-control-ui-connectivity](/tr/gateway/troubleshooting#dashboard-control-ui-connectivity)
    - [/web/control-ui](/web/control-ui)
    - [/gateway/authentication](/tr/gateway/authentication)

  </Accordion>

  <Accordion title="Gateway başlamıyor veya hizmet kurulu ama çalışmıyor">
    ```bash
    openclaw status
    openclaw gateway status
    openclaw logs --follow
    openclaw doctor
    openclaw channels status --probe
    ```

    İyi çıktı şöyle görünür:

    - `Service: ... (loaded)`
    - `Runtime: running`
    - `RPC probe: ok`

    Yaygın günlük imzaları:

    - `Gateway start blocked: set gateway.mode=local` veya `existing config is missing gateway.mode` → gateway kipi remote durumda ya da yapılandırma dosyasında local-mode damgası eksik ve onarılması gerekiyor.
    - `refusing to bind gateway ... without auth` → geçerli bir gateway auth yolu olmadan loopback dışı bind denemesi (token/parola veya yapılandırılmışsa trusted-proxy).
    - `another gateway instance is already listening` veya `EADDRINUSE` → port zaten kullanımda.

    Ayrıntılı sayfalar:

    - [/gateway/troubleshooting#gateway-service-not-running](/tr/gateway/troubleshooting#gateway-service-not-running)
    - [/gateway/background-process](/tr/gateway/background-process)
    - [/gateway/configuration](/tr/gateway/configuration)

  </Accordion>

  <Accordion title="Kanal bağlanıyor ama mesajlar akmıyor">
    ```bash
    openclaw status
    openclaw gateway status
    openclaw logs --follow
    openclaw doctor
    openclaw channels status --probe
    ```

    İyi çıktı şöyle görünür:

    - Kanal taşıması bağlıdır.
    - Pairing/allowlist kontrolleri geçer.
    - Gerektiği yerde mention'lar algılanır.

    Yaygın günlük imzaları:

    - `mention required` → grup mention geçidi işlemeyi engelledi.
    - `pairing` / `pending` → DM göndericisi henüz onaylanmamış.
    - `not_in_channel`, `missing_scope`, `Forbidden`, `401/403` → kanal izin token sorunu.

    Ayrıntılı sayfalar:

    - [/gateway/troubleshooting#channel-connected-messages-not-flowing](/tr/gateway/troubleshooting#channel-connected-messages-not-flowing)
    - [/channels/troubleshooting](/tr/channels/troubleshooting)

  </Accordion>

  <Accordion title="Cron veya heartbeat tetiklenmedi ya da teslim edilmedi">
    ```bash
    openclaw status
    openclaw gateway status
    openclaw cron status
    openclaw cron list
    openclaw cron runs --id <jobId> --limit 20
    openclaw logs --follow
    ```

    İyi çıktı şöyle görünür:

    - `cron.status`, etkin olduğunu ve bir sonraki uyanmayı gösterir.
    - `cron runs`, son `ok` girdilerini gösterir.
    - Heartbeat etkindir ve etkin saatlerin dışında değildir.

    Yaygın günlük imzaları:

- `cron: scheduler disabled; jobs will not run automatically` → cron devre dışıdır.
- `heartbeat skipped` ve `reason=quiet-hours` → yapılandırılmış etkin saatlerin dışındadır.
- `heartbeat skipped` ve `reason=empty-heartbeat-file` → `HEARTBEAT.md` var ama yalnızca boş/yalnızca başlık iskeleti içeriyor.
- `heartbeat skipped` ve `reason=no-tasks-due` → `HEARTBEAT.md` görev kipi etkin ama görev aralıklarının hiçbiri henüz zamanı gelmemiş.
- `heartbeat skipped` ve `reason=alerts-disabled` → tüm heartbeat görünürlüğü devre dışı (`showOk`, `showAlerts` ve `useIndicator` hepsi kapalı).
- `requests-in-flight` → ana hat meşgul; heartbeat uyanması ertelendi. - `unknown accountId` → heartbeat teslim hedefi hesabı mevcut değil.

      Ayrıntılı sayfalar:

      - [/gateway/troubleshooting#cron-and-heartbeat-delivery](/tr/gateway/troubleshooting#cron-and-heartbeat-delivery)
      - [/automation/cron-jobs#troubleshooting](/tr/automation/cron-jobs#troubleshooting)
      - [/gateway/heartbeat](/tr/gateway/heartbeat)

    </Accordion>

    <Accordion title="Node eşlenmiş ama araç camera canvas screen exec işlemlerinde başarısız oluyor">
      ```bash
      openclaw status
      openclaw gateway status
      openclaw nodes status
      openclaw nodes describe --node <idOrNameOrIp>
      openclaw logs --follow
      ```

      İyi çıktı şöyle görünür:

      - Node, `node` rolü için bağlı ve eşlenmiş olarak listelenir.
      - Çağırdığınız komut için yetenek mevcuttur.
      - Araç için izin durumu verilmiştir.

      Yaygın günlük imzaları:

      - `NODE_BACKGROUND_UNAVAILABLE` → node uygulamasını ön plana getirin.
      - `*_PERMISSION_REQUIRED` → OS izni reddedildi/eksik.
      - `SYSTEM_RUN_DENIED: approval required` → exec onayı bekliyor.
      - `SYSTEM_RUN_DENIED: allowlist miss` → komut exec allowlist içinde değil.

      Ayrıntılı sayfalar:

      - [/gateway/troubleshooting#node-paired-tool-fails](/tr/gateway/troubleshooting#node-paired-tool-fails)
      - [/nodes/troubleshooting](/tr/nodes/troubleshooting)
      - [/tools/exec-approvals](/tr/tools/exec-approvals)

    </Accordion>

    <Accordion title="Exec aniden onay istemeye başladı">
      ```bash
      openclaw config get tools.exec.host
      openclaw config get tools.exec.security
      openclaw config get tools.exec.ask
      openclaw gateway restart
      ```

      Ne değişti:

      - `tools.exec.host` ayarlanmamışsa varsayılan `auto` olur.
      - `host=auto`, bir sandbox çalışma zamanı etkinken `sandbox`, aksi halde `gateway` olarak çözülür.
      - `host=auto` yalnızca yönlendirmedir; istemsiz "YOLO" davranışı `gateway/node` üzerinde `security=full` ve `ask=off` ayarlarından gelir.
      - `gateway` ve `node` üzerinde, ayarlanmamış `tools.exec.security` varsayılan olarak `full` olur.
      - Ayarlanmamış `tools.exec.ask` varsayılan olarak `off` olur.
      - Sonuç: onaylar görüyorsanız, host-local veya oturum başına bir ilke exec davranışını mevcut varsayılanlardan daha sıkı hale getirmiştir.

      Güncel varsayılan onaysız davranışı geri yükleyin:

      ```bash
      openclaw config set tools.exec.host gateway
      openclaw config set tools.exec.security full
      openclaw config set tools.exec.ask off
      openclaw gateway restart
      ```

      Daha güvenli alternatifler:

      - Yalnızca kararlı host yönlendirmesi istiyorsanız sadece `tools.exec.host=gateway` ayarlayın.
      - Host exec istiyor ama allowlist kaçırmalarında yine de gözden geçirme istiyorsanız `security=allowlist` ile `ask=on-miss` kullanın.
      - `host=auto` değerinin yeniden `sandbox` olarak çözülmesini istiyorsanız sandbox kipini etkinleştirin.

      Yaygın günlük imzaları:

      - `Approval required.` → komut `/approve ...` için bekliyor.
      - `SYSTEM_RUN_DENIED: approval required` → node-host exec onayı bekliyor.
      - `exec host=sandbox requires a sandbox runtime for this session` → örtük/açık sandbox seçimi var ama sandbox kipi kapalı.

      Ayrıntılı sayfalar:

      - [/tools/exec](/tr/tools/exec)
      - [/tools/exec-approvals](/tr/tools/exec-approvals)
      - [/gateway/security#runtime-expectation-drift](/tr/gateway/security#runtime-expectation-drift)

    </Accordion>

    <Accordion title="Browser aracı başarısız oluyor">
      ```bash
      openclaw status
      openclaw gateway status
      openclaw browser status
      openclaw logs --follow
      openclaw doctor
      ```

      İyi çıktı şöyle görünür:

      - Browser durumu `running: true` ve seçilmiş bir browser/profile gösterir.
      - `openclaw` başlar veya `user` yerel Chrome sekmelerini görebilir.

      Yaygın günlük imzaları:

      - `unknown command "browser"` veya `unknown command 'browser'` → `plugins.allow` ayarlıdır ve `browser` içermez.
      - `Failed to start Chrome CDP on port` → yerel browser başlatma başarısız oldu.
      - `browser.executablePath not found` → yapılandırılmış ikili yolu yanlış.
      - `browser.cdpUrl must be http(s) or ws(s)` → yapılandırılmış CDP URL'si desteklenmeyen bir şema kullanıyor.
      - `browser.cdpUrl has invalid port` → yapılandırılmış CDP URL'sinde kötü veya aralık dışı bir port var.
      - `No Chrome tabs found for profile="user"` → Chrome MCP attach profilinde açık yerel Chrome sekmesi yok.
      - `Remote CDP for profile "<name>" is not reachable` → yapılandırılmış uzak CDP uç noktasına bu hosttan erişilemiyor.
      - `Browser attachOnly is enabled ... not reachable` veya `Browser attachOnly is enabled and CDP websocket ... is not reachable` → yalnızca attach profili için canlı CDP hedefi yok.
      - attach-only veya remote CDP profillerinde eski viewport / dark-mode / locale / offline geçersiz kılmaları → gateway'i yeniden başlatmadan etkin kontrol oturumunu kapatmak ve öykünme durumunu serbest bırakmak için `openclaw browser stop --browser-profile <name>` çalıştırın.

      Ayrıntılı sayfalar:

      - [/gateway/troubleshooting#browser-tool-fails](/tr/gateway/troubleshooting#browser-tool-fails)
      - [/tools/browser#missing-browser-command-or-tool](/tr/tools/browser#missing-browser-command-or-tool)
      - [/tools/browser-linux-troubleshooting](/tr/tools/browser-linux-troubleshooting)
      - [/tools/browser-wsl2-windows-remote-cdp-troubleshooting](/tr/tools/browser-wsl2-windows-remote-cdp-troubleshooting)

    </Accordion>
  </AccordionGroup>

## İlgili

- [SSS](/tr/help/faq) — sık sorulan sorular
- [Gateway Sorun Giderme](/tr/gateway/troubleshooting) — gateway'e özgü sorunlar
- [Doctor](/tr/gateway/doctor) — otomatik sağlık kontrolleri ve onarımlar
- [Kanal Sorun Giderme](/tr/channels/troubleshooting) — kanal bağlantı sorunları
- [Otomasyon Sorun Giderme](/tr/automation/cron-jobs#troubleshooting) — cron ve heartbeat sorunları
