---
read_when:
    - '`openclaw onboard` için ayrıntılı davranışa ihtiyacınız var'
    - Onboarding sonuçlarında hata ayıklıyorsunuz veya onboarding istemcilerini entegre ediyorsunuz
sidebarTitle: CLI reference
summary: CLI kurulum akışı, kimlik doğrulama/model kurulumu, çıktılar ve iç yapılar için eksiksiz başvuru
title: CLI Kurulum Başvurusu
x-i18n:
    generated_at: "2026-04-06T03:13:27Z"
    model: gpt-5.4
    provider: openai
    source_hash: 92f379b34a2b48c68335dae4f759117c770f018ec51b275f4f40421c6b3abb23
    source_path: start/wizard-cli-reference.md
    workflow: 15
---

# CLI Kurulum Başvurusu

Bu sayfa, `openclaw onboard` için tam başvurudur.
Kısa kılavuz için bkz. [Onboarding (CLI)](/tr/start/wizard).

## Sihirbaz ne yapar

Yerel kip (varsayılan) sizi şu adımlardan geçirir:

- Model ve kimlik doğrulama kurulumu (OpenAI Code abonelik OAuth, Anthropic Claude CLI veya API anahtarı, ayrıca MiniMax, GLM, Ollama, Moonshot, StepFun ve AI Gateway seçenekleri)
- Çalışma alanı konumu ve bootstrap dosyaları
- Gateway ayarları (port, bind, auth, tailscale)
- Kanallar ve sağlayıcılar (Telegram, WhatsApp, Discord, Google Chat, Mattermost, Signal, BlueBubbles ve diğer paketlenmiş kanal plugin'leri)
- Daemon kurulumu (LaunchAgent, systemd kullanıcı birimi veya Startup-folder geri dönüşü olan yerel Windows Scheduled Task)
- Sağlık denetimi
- Skills kurulumu

Uzak kip, bu makineyi başka bir yerdeki gateway'e bağlanacak şekilde yapılandırır.
Uzak host üzerinde hiçbir şeyi kurmaz veya değiştirmez.

## Yerel akış ayrıntıları

<Steps>
  <Step title="Mevcut yapılandırma algılama">
    - `~/.openclaw/openclaw.json` mevcutsa Keep, Modify veya Reset seçeneklerinden birini seçin.
    - Sihirbazı yeniden çalıştırmak, siz açıkça Reset seçmedikçe (veya `--reset` geçmedikçe) hiçbir şeyi silmez.
    - CLI `--reset` varsayılan olarak `config+creds+sessions` kullanır; çalışma alanını da kaldırmak için `--reset-scope full` kullanın.
    - Yapılandırma geçersizse veya eski anahtarlar içeriyorsa, sihirbaz devam etmeden önce `openclaw doctor` çalıştırmanızı isteyerek durur.
    - Reset, `trash` kullanır ve şu kapsamları sunar:
      - Yalnızca yapılandırma
      - Yapılandırma + kimlik bilgileri + oturumlar
      - Tam sıfırlama (çalışma alanını da kaldırır)
  </Step>
  <Step title="Model ve kimlik doğrulama">
    - Tam seçenek matrisi [Kimlik doğrulama ve model seçenekleri](#auth-and-model-options) bölümündedir.
  </Step>
  <Step title="Çalışma alanı">
    - Varsayılan `~/.openclaw/workspace` (yapılandırılabilir).
    - İlk çalıştırma bootstrap ritüeli için gereken çalışma alanı dosyalarını tohumlar.
    - Çalışma alanı düzeni: [Agent çalışma alanı](/tr/concepts/agent-workspace).
  </Step>
  <Step title="Gateway">
    - Port, bind, auth kipi ve tailscale erişimi için istemde bulunur.
    - Önerilen: loopback için bile belirteç kimlik doğrulamasını etkin tutun; böylece yerel WS istemcileri kimlik doğrulaması yapmak zorunda kalır.
    - Belirteç kipinde, etkileşimli kurulum şunları sunar:
      - **Düz metin belirteç oluştur/depola** (varsayılan)
      - **SecretRef kullan** (isteğe bağlı)
    - Parola kipinde, etkileşimli kurulum ayrıca düz metin veya SecretRef depolamayı destekler.
    - Etkileşimsiz belirteç SecretRef yolu: `--gateway-token-ref-env <ENV_VAR>`.
      - Onboarding süreci ortamında boş olmayan bir ortam değişkeni gerektirir.
      - `--gateway-token` ile birlikte kullanılamaz.
    - Yalnızca tüm yerel süreçlere tamamen güveniyorsanız kimlik doğrulamayı devre dışı bırakın.
    - Loopback dışı bind işlemleri hâlâ kimlik doğrulama gerektirir.
  </Step>
  <Step title="Kanallar">
    - [WhatsApp](/tr/channels/whatsapp): isteğe bağlı QR oturum açma
    - [Telegram](/tr/channels/telegram): bot belirteci
    - [Discord](/tr/channels/discord): bot belirteci
    - [Google Chat](/tr/channels/googlechat): hizmet hesabı JSON'u + webhook audience
    - [Mattermost](/tr/channels/mattermost): bot belirteci + temel URL
    - [Signal](/tr/channels/signal): isteğe bağlı `signal-cli` kurulumu + hesap yapılandırması
    - [BlueBubbles](/tr/channels/bluebubbles): iMessage için önerilir; sunucu URL'si + parola + webhook
    - [iMessage](/tr/channels/imessage): eski `imsg` CLI yolu + DB erişimi
    - DM güvenliği: varsayılan eşleştirmedir. İlk DM bir kod gönderir; bunu
      `openclaw pairing approve <channel> <code>` ile onaylayın veya allowlist kullanın.
  </Step>
  <Step title="Daemon kurulumu">
    - macOS: LaunchAgent
      - Oturum açmış kullanıcı oturumu gerektirir; headless için özel bir LaunchDaemon kullanın (gönderilmez).
    - Linux ve WSL2 üzerinden Windows: systemd kullanıcı birimi
      - Gateway'in oturum kapatıldıktan sonra da çalışmaya devam etmesi için sihirbaz `loginctl enable-linger <user>` çalıştırmayı dener.
      - sudo isteyebilir (`/var/lib/systemd/linger` yazar); önce sudo olmadan dener.
    - Yerel Windows: önce Scheduled Task
      - Görev oluşturma reddedilirse, OpenClaw kullanıcı başına Startup-folder oturum açma öğesine geri döner ve gateway'i hemen başlatır.
      - Scheduled Task'lar daha iyi supervisor durumu sağladıkları için tercih edilmeye devam eder.
    - Çalışma zamanı seçimi: Node (önerilir; WhatsApp ve Telegram için gereklidir). Bun önerilmez.
  </Step>
  <Step title="Sağlık denetimi">
    - Gateway'i başlatır (gerekirse) ve `openclaw health` çalıştırır.
    - `openclaw status --deep`, desteklendiğinde kanal yoklamaları da dahil olmak üzere canlı gateway sağlık yoklamasını durum çıktısına ekler.
  </Step>
  <Step title="Skills">
    - Kullanılabilir skills'leri okur ve gereksinimleri denetler.
    - Düğüm yöneticisini seçmenize izin verir: npm, pnpm veya bun.
    - İsteğe bağlı bağımlılıkları kurar (bazıları macOS'ta Homebrew kullanır).
  </Step>
  <Step title="Bitir">
    - iOS, Android ve macOS uygulama seçenekleri dahil özet ve sonraki adımlar.
  </Step>
</Steps>

<Note>
GUI algılanmazsa sihirbaz tarayıcı açmak yerine Control UI için SSH port-forward yönergelerini yazdırır.
Control UI varlıkları eksikse sihirbaz bunları oluşturmayı dener; geri dönüş olarak `pnpm ui:build` kullanılır (UI bağımlılıklarını otomatik kurar).
</Note>

## Uzak kip ayrıntıları

Uzak kip, bu makineyi başka bir yerdeki gateway'e bağlanacak şekilde yapılandırır.

<Info>
Uzak kip, uzak host üzerinde hiçbir şeyi kurmaz veya değiştirmez.
</Info>

Ayarladığınız şeyler:

- Uzak gateway URL'si (`ws://...`)
- Uzak gateway auth gerekiyorsa belirteç (önerilir)

<Note>
- Gateway yalnızca loopback ise SSH tünelleme veya bir tailnet kullanın.
- Keşif ipuçları:
  - macOS: Bonjour (`dns-sd`)
  - Linux: Avahi (`avahi-browse`)
</Note>

## Kimlik doğrulama ve model seçenekleri

<AccordionGroup>
  <Accordion title="Anthropic API anahtarı">
    Varsa `ANTHROPIC_API_KEY` kullanır veya bir anahtar ister, ardından daemon kullanımı için kaydeder.
  </Accordion>
  <Accordion title="OpenAI Code aboneliği (Codex CLI yeniden kullanımı)">
    `~/.codex/auth.json` mevcutsa sihirbaz bunu yeniden kullanabilir.
    Yeniden kullanılan Codex CLI kimlik bilgileri Codex CLI tarafından yönetilmeye devam eder; süre dolduğunda OpenClaw
    önce bu kaynağı yeniden okur ve sağlayıcı bunu yenileyebiliyorsa
    yenilenmiş kimlik bilgisini sahiplenmek yerine tekrar Codex depolamasına yazar.
  </Accordion>
  <Accordion title="OpenAI Code aboneliği (OAuth)">
    Tarayıcı akışı; `code#state` yapıştırın.

    Model ayarlanmamışsa veya `openai/*` ise `agents.defaults.model` değerini `openai-codex/gpt-5.4` olarak ayarlar.

  </Accordion>
  <Accordion title="OpenAI API anahtarı">
    Varsa `OPENAI_API_KEY` kullanır veya bir anahtar ister, ardından kimlik bilgisini auth profillerinde depolar.

    Model ayarlanmamışsa, `openai/*` ise veya `openai-codex/*` ise `agents.defaults.model` değerini `openai/gpt-5.4` olarak ayarlar.

  </Accordion>
  <Accordion title="xAI (Grok) API anahtarı">
    `XAI_API_KEY` ister ve xAI'ı model sağlayıcısı olarak yapılandırır.
  </Accordion>
  <Accordion title="OpenCode">
    `OPENCODE_API_KEY` (veya `OPENCODE_ZEN_API_KEY`) ister ve Zen veya Go kataloğunu seçmenize izin verir.
    Kurulum URL'si: [opencode.ai/auth](https://opencode.ai/auth).
  </Accordion>
  <Accordion title="API anahtarı (genel)">
    Anahtarı sizin için depolar.
  </Accordion>
  <Accordion title="Vercel AI Gateway">
    `AI_GATEWAY_API_KEY` ister.
    Daha fazla ayrıntı: [Vercel AI Gateway](/tr/providers/vercel-ai-gateway).
  </Accordion>
  <Accordion title="Cloudflare AI Gateway">
    Hesap kimliği, gateway kimliği ve `CLOUDFLARE_AI_GATEWAY_API_KEY` ister.
    Daha fazla ayrıntı: [Cloudflare AI Gateway](/tr/providers/cloudflare-ai-gateway).
  </Accordion>
  <Accordion title="MiniMax">
    Yapılandırma otomatik olarak yazılır. Barındırılan varsayılan `MiniMax-M2.7`'dir; API anahtarı kurulumu
    `minimax/...`, OAuth kurulumu ise `minimax-portal/...` kullanır.
    Daha fazla ayrıntı: [MiniMax](/tr/providers/minimax).
  </Accordion>
  <Accordion title="StepFun">
    Yapılandırma, Çin veya global uç noktalarda StepFun standard veya Step Plan için otomatik yazılır.
    Standard şu anda `step-3.5-flash` içerir ve Step Plan ayrıca `step-3.5-flash-2603` içerir.
    Daha fazla ayrıntı: [StepFun](/tr/providers/stepfun).
  </Accordion>
  <Accordion title="Synthetic (Anthropic uyumlu)">
    `SYNTHETIC_API_KEY` ister.
    Daha fazla ayrıntı: [Synthetic](/tr/providers/synthetic).
  </Accordion>
  <Accordion title="Ollama (Cloud ve yerel açık modeller)">
    Temel URL'yi ister (varsayılan `http://127.0.0.1:11434`), sonra Cloud + Local veya Local kipini sunar.
    Kullanılabilir modelleri keşfeder ve varsayılanlar önerir.
    Daha fazla ayrıntı: [Ollama](/tr/providers/ollama).
  </Accordion>
  <Accordion title="Moonshot ve Kimi Coding">
    Moonshot (Kimi K2) ve Kimi Coding yapılandırmaları otomatik yazılır.
    Daha fazla ayrıntı: [Moonshot AI (Kimi + Kimi Coding)](/tr/providers/moonshot).
  </Accordion>
  <Accordion title="Özel sağlayıcı">
    OpenAI uyumlu ve Anthropic uyumlu uç noktalarla çalışır.

    Etkileşimli onboarding, diğer sağlayıcı API anahtarı akışlarıyla aynı API anahtarı depolama seçeneklerini destekler:
    - **API anahtarını şimdi yapıştır** (düz metin)
    - **Gizli başvuru kullan** (ortam başvurusu veya yapılandırılmış sağlayıcı başvurusu, ön denetim doğrulaması ile)

    Etkileşimsiz bayraklar:
    - `--auth-choice custom-api-key`
    - `--custom-base-url`
    - `--custom-model-id`
    - `--custom-api-key` (isteğe bağlı; `CUSTOM_API_KEY` değerine geri döner)
    - `--custom-provider-id` (isteğe bağlı)
    - `--custom-compatibility <openai|anthropic>` (isteğe bağlı; varsayılan `openai`)

  </Accordion>
  <Accordion title="Atla">
    Kimlik doğrulamayı yapılandırılmamış bırakır.
  </Accordion>
</AccordionGroup>

Model davranışı:

- Algılanan seçeneklerden varsayılan modeli seçin veya sağlayıcı ve modeli elle girin.
- Onboarding bir sağlayıcı kimlik doğrulama seçeneğinden başladığında model seçici
  o sağlayıcıyı otomatik olarak tercih eder. Volcengine ve BytePlus için aynı tercih
  kodlama planı varyantlarıyla da eşleşir (`volcengine-plan/*`,
  `byteplus-plan/*`).
- Tercih edilen sağlayıcı filtresi boş kalacaksa, seçici hiç model göstermemek yerine tam kataloğa geri döner.
- Sihirbaz bir model denetimi çalıştırır ve yapılandırılmış model bilinmiyorsa veya kimlik doğrulaması eksikse uyarır.

Kimlik bilgisi ve profil yolları:

- Kimlik doğrulama profilleri (API anahtarları + OAuth): `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- Eski OAuth içe aktarma kaynağı: `~/.openclaw/credentials/oauth.json`

Kimlik bilgisi depolama kipi:

- Varsayılan onboarding davranışı, API anahtarlarını auth profillerinde düz metin değerler olarak kalıcı yazar.
- `--secret-input-mode ref`, düz metin anahtar depolama yerine başvuru kipini etkinleştirir.
  Etkileşimli kurulumda şunlardan birini seçebilirsiniz:
  - ortam değişkeni başvurusu (örneğin `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`)
  - sağlayıcı takma adı + kimlik ile yapılandırılmış sağlayıcı başvurusu (`file` veya `exec`)
- Etkileşimli başvuru kipi kaydetmeden önce hızlı bir ön denetim doğrulaması çalıştırır.
  - Ortam başvuruları: mevcut onboarding ortamında değişken adını + boş olmayan değeri doğrular.
  - Sağlayıcı başvuruları: sağlayıcı yapılandırmasını doğrular ve istenen kimliği çözümler.
  - Ön denetim başarısız olursa onboarding hatayı gösterir ve yeniden denemenize izin verir.
- Etkileşimsiz kipte `--secret-input-mode ref` yalnızca ortam desteklidir.
  - Sağlayıcı ortam değişkenini onboarding süreci ortamında ayarlayın.
  - Satır içi anahtar bayrakları (örneğin `--openai-api-key`) bu ortam değişkeninin ayarlanmış olmasını gerektirir; aksi halde onboarding hızlıca başarısız olur.
  - Özel sağlayıcılar için etkileşimsiz `ref` kipi, `models.providers.<id>.apiKey` değerini `{ source: "env", provider: "default", id: "CUSTOM_API_KEY" }` olarak depolar.
  - Bu özel sağlayıcı durumunda `--custom-api-key`, `CUSTOM_API_KEY` ayarlanmış olmasını gerektirir; aksi halde onboarding hızlıca başarısız olur.
- Gateway kimlik doğrulama kimlik bilgileri, etkileşimli kurulumda düz metin ve SecretRef seçeneklerini destekler:
  - Belirteç kipi: **Düz metin belirteç oluştur/depola** (varsayılan) veya **SecretRef kullan**.
  - Parola kipi: düz metin veya SecretRef.
- Etkileşimsiz belirteç SecretRef yolu: `--gateway-token-ref-env <ENV_VAR>`.
- Mevcut düz metin kurulumları değişmeden çalışmaya devam eder.

<Note>
Headless ve sunucu ipucu: OAuth'u tarayıcısı olan bir makinede tamamlayın, sonra
o agent'in `auth-profiles.json` dosyasını (örneğin
`~/.openclaw/agents/<agentId>/agent/auth-profiles.json` veya eşleşen
`$OPENCLAW_STATE_DIR/...` yolu) gateway host'una kopyalayın. `credentials/oauth.json`
yalnızca eski bir içe aktarma kaynağıdır.
</Note>

## Çıktılar ve iç yapılar

`~/.openclaw/openclaw.json` içindeki tipik alanlar:

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers` (MiniMax seçildiyse)
- `tools.profile` (yerel onboarding, ayarlanmamışsa bunu varsayılan olarak `"coding"` yapar; mevcut açık değerler korunur)
- `gateway.*` (mode, bind, auth, tailscale)
- `session.dmScope` (yerel onboarding, ayarlanmamışsa bunu varsayılan olarak `per-channel-peer` yapar; mevcut açık değerler korunur)
- `channels.telegram.botToken`, `channels.discord.token`, `channels.matrix.*`, `channels.signal.*`, `channels.imessage.*`
- İstemler sırasında buna katıldığınızda kanal allowlist'leri (Slack, Discord, Matrix, Microsoft Teams) mümkün olduğunda adlar kimliklere çözümlenir
- `skills.install.nodeManager`
  - `setup --node-manager` bayrağı `npm`, `pnpm` veya `bun` kabul eder.
  - El ile yapılandırma daha sonra yine de `skills.install.nodeManager: "yarn"` ayarlayabilir.
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add`, `agents.list[]` ve isteğe bağlı `bindings` yazar.

WhatsApp kimlik bilgileri `~/.openclaw/credentials/whatsapp/<accountId>/` altında bulunur.
Oturumlar `~/.openclaw/agents/<agentId>/sessions/` altında depolanır.

<Note>
Bazı kanallar plugin olarak sunulur. Kurulum sırasında seçildiklerinde sihirbaz,
kanal yapılandırmasından önce plugin'i kurmanızı ister (npm veya yerel yol).
</Note>

Gateway sihirbazı RPC:

- `wizard.start`
- `wizard.next`
- `wizard.cancel`
- `wizard.status`

İstemciler (macOS uygulaması ve Control UI), onboarding mantığını yeniden uygulamadan adımları işleyebilir.

Signal kurulum davranışı:

- Uygun sürüm varlığını indirir
- Bunu `~/.openclaw/tools/signal-cli/<version>/` altına depolar
- Yapılandırmaya `channels.signal.cliPath` yazar
- JVM derlemeleri Java 21 gerektirir
- Mevcut olduğunda yerel derlemeler kullanılır
- Windows, WSL2 kullanır ve Linux signal-cli akışını WSL içinde izler

## İlgili belgeler

- Onboarding merkezi: [Onboarding (CLI)](/tr/start/wizard)
- Otomasyon ve betikler: [CLI Automation](/tr/start/wizard-cli-automation)
- Komut başvurusu: [`openclaw onboard`](/cli/onboard)
