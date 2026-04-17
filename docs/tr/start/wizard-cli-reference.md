---
read_when:
    - '`openclaw onboard` için ayrıntılı davranışa ihtiyacınız var'
    - Onboarding sonuçlarında hata ayıklıyorsunuz veya onboarding istemcilerini entegre ediyorsunuz
sidebarTitle: CLI reference
summary: CLI kurulum akışı, kimlik doğrulama/model kurulumu, çıktılar ve iç yapılar için eksiksiz başvuru
title: CLI Kurulum Başvurusu
x-i18n:
    generated_at: "2026-04-15T14:41:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: 61ca679caca3b43fa02388294007f89db22d343e49e10b61d8d118cd8fbb7369
    source_path: start/wizard-cli-reference.md
    workflow: 15
---

# CLI Kurulum Başvurusu

Bu sayfa, `openclaw onboard` için eksiksiz başvurudur.
Kısa kılavuz için bkz. [Onboarding (CLI)](/tr/start/wizard).

## Sihirbaz ne yapar

Yerel mod (varsayılan) size şu adımlarda rehberlik eder:

- Model ve kimlik doğrulama kurulumu (OpenAI Code aboneliği OAuth’u, Anthropic Claude CLI veya API anahtarı, ayrıca MiniMax, GLM, Ollama, Moonshot, StepFun ve AI Gateway seçenekleri)
- Çalışma alanı konumu ve önyükleme dosyaları
- Gateway ayarları (port, bind, auth, tailscale)
- Kanallar ve sağlayıcılar (Telegram, WhatsApp, Discord, Google Chat, Mattermost, Signal, BlueBubbles ve diğer paketlenmiş kanal Plugin’leri)
- Artalan süreci kurulumu (LaunchAgent, systemd kullanıcı birimi veya Başlangıç klasörü geri dönüş seçeneği olan yerel Windows Scheduled Task)
- Durum denetimi
- Skills kurulumu

Uzak mod, bu makineyi başka bir yerdeki bir Gateway’e bağlanacak şekilde yapılandırır.
Uzak ana makinede hiçbir şey kurmaz veya değiştirmez.

## Yerel akış ayrıntıları

<Steps>
  <Step title="Mevcut yapılandırma algılama">
    - `~/.openclaw/openclaw.json` mevcutsa Keep, Modify veya Reset seçeneklerinden birini belirleyin.
    - Sihirbazı yeniden çalıştırmak, siz açıkça Reset seçmediğiniz sürece (veya `--reset` geçmediğiniz sürece) hiçbir şeyi silmez.
    - CLI `--reset` varsayılan olarak `config+creds+sessions` kullanır; çalışma alanını da kaldırmak için `--reset-scope full` kullanın.
    - Yapılandırma geçersizse veya eski anahtarlar içeriyorsa, sihirbaz durur ve devam etmeden önce `openclaw doctor` çalıştırmanızı ister.
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
    - İlk çalıştırma önyükleme ritüeli için gereken çalışma alanı dosyalarını oluşturur.
    - Çalışma alanı düzeni: [Ajan çalışma alanı](/tr/concepts/agent-workspace).
  </Step>
  <Step title="Gateway">
    - Port, bind, auth modu ve tailscale erişimi için istemde bulunur.
    - Önerilen: yerel WS istemcilerinin kimlik doğrulaması yapmasını zorunlu kılmak için loopback üzerinde bile token auth etkin kalsın.
    - Token modunda, etkileşimli kurulum şunları sunar:
      - **Düz metin token oluştur/sakla** (varsayılan)
      - **SecretRef kullan** (isteğe bağlı)
    - Parola modunda, etkileşimli kurulum düz metin veya SecretRef depolamayı da destekler.
    - Etkileşimsiz token SecretRef yolu: `--gateway-token-ref-env <ENV_VAR>`.
      - Onboarding işlem ortamında boş olmayan bir ortam değişkeni gerektirir.
      - `--gateway-token` ile birlikte kullanılamaz.
    - Auth’u yalnızca her yerel sürece tamamen güveniyorsanız devre dışı bırakın.
    - Loopback dışı bind’lerde de auth gereklidir.
  </Step>
  <Step title="Kanallar">
    - [WhatsApp](/tr/channels/whatsapp): isteğe bağlı QR girişi
    - [Telegram](/tr/channels/telegram): bot token’ı
    - [Discord](/tr/channels/discord): bot token’ı
    - [Google Chat](/tr/channels/googlechat): hizmet hesabı JSON’u + Webhook audience
    - [Mattermost](/tr/channels/mattermost): bot token’ı + temel URL
    - [Signal](/tr/channels/signal): isteğe bağlı `signal-cli` kurulumu + hesap yapılandırması
    - [BlueBubbles](/tr/channels/bluebubbles): iMessage için önerilir; sunucu URL’si + parola + Webhook
    - [iMessage](/tr/channels/imessage): eski `imsg` CLI yolu + DB erişimi
    - DM güvenliği: varsayılan pairing’dir. İlk DM bir kod gönderir; `openclaw pairing approve <channel> <code>` ile onaylayın veya allowlist kullanın.
  </Step>
  <Step title="Artalan süreci kurulumu">
    - macOS: LaunchAgent
      - Oturum açmış kullanıcı oturumu gerektirir; başsız kullanım için özel bir LaunchDaemon kullanın (paketlenmez).
    - Linux ve Windows üzerinden WSL2: systemd kullanıcı birimi
      - Sihirbaz, çıkıştan sonra da Gateway’in çalışır kalması için `loginctl enable-linger <user>` komutunu denemeye çalışır.
      - sudo isteyebilir (`/var/lib/systemd/linger` yazar); önce sudo olmadan dener.
    - Yerel Windows: önce Scheduled Task
      - Görev oluşturma reddedilirse OpenClaw, kullanıcı başına Başlangıç klasörü giriş öğesine geri döner ve Gateway’i hemen başlatır.
      - Scheduled Task tercih edilmeye devam edilir çünkü daha iyi supervisor durumu sağlarlar.
    - Çalışma zamanı seçimi: Node (önerilir; WhatsApp ve Telegram için gereklidir). Bun önerilmez.
  </Step>
  <Step title="Durum denetimi">
    - Gateway’i başlatır (gerekiyorsa) ve `openclaw health` çalıştırır.
    - `openclaw status --deep`, desteklendiğinde kanal probları dahil olmak üzere canlı Gateway durum probunu durum çıktısına ekler.
  </Step>
  <Step title="Skills">
    - Kullanılabilir Skills’i okur ve gereksinimleri denetler.
    - Node yöneticisini seçmenize izin verir: npm, pnpm veya bun.
    - İsteğe bağlı bağımlılıkları kurar (bazıları macOS üzerinde Homebrew kullanır).
  </Step>
  <Step title="Bitir">
    - iOS, Android ve macOS uygulama seçenekleri dahil özet ve sonraki adımlar.
  </Step>
</Steps>

<Note>
GUI algılanmazsa sihirbaz, bir tarayıcı açmak yerine Control UI için SSH port yönlendirme yönergelerini yazdırır.
Control UI varlıkları eksikse sihirbaz bunları oluşturmaya çalışır; geri dönüş olarak `pnpm ui:build` kullanılır (UI bağımlılıklarını otomatik kurar).
</Note>

## Uzak mod ayrıntıları

Uzak mod, bu makineyi başka bir yerdeki bir Gateway’e bağlanacak şekilde yapılandırır.

<Info>
Uzak mod, uzak ana makinede hiçbir şey kurmaz veya değiştirmez.
</Info>

Ayarladıklarınız:

- Uzak Gateway URL’si (`ws://...`)
- Uzak Gateway auth gerektiriyorsa token (önerilir)

<Note>
- Gateway yalnızca loopback ise SSH tünelleme veya bir tailnet kullanın.
- Keşif ipuçları:
  - macOS: Bonjour (`dns-sd`)
  - Linux: Avahi (`avahi-browse`)
</Note>

## Kimlik doğrulama ve model seçenekleri

<AccordionGroup>
  <Accordion title="Anthropic API anahtarı">
    Varsa `ANTHROPIC_API_KEY` kullanır veya bir anahtar ister, ardından artalan süreci kullanımı için bunu kaydeder.
  </Accordion>
  <Accordion title="OpenAI Code aboneliği (Codex CLI yeniden kullanımı)">
    `~/.codex/auth.json` mevcutsa sihirbaz bunu yeniden kullanabilir.
    Yeniden kullanılan Codex CLI kimlik bilgileri, Codex CLI tarafından yönetilmeye devam eder; süre dolduğunda OpenClaw
    önce bu kaynağı yeniden okur ve sağlayıcı bunu yenileyebildiğinde
    kimlik bilgisini sahipliğini üstlenmek yerine yeniden Codex deposuna yazar.
  </Accordion>
  <Accordion title="OpenAI Code aboneliği (OAuth)">
    Tarayıcı akışı; `code#state` yapıştırın.

    Model ayarlanmamışsa veya `openai/*` ise `agents.defaults.model` değerini `openai-codex/gpt-5.4` olarak ayarlar.

  </Accordion>
  <Accordion title="OpenAI API anahtarı">
    Varsa `OPENAI_API_KEY` kullanır veya bir anahtar ister, ardından kimlik bilgisini auth profillerinde saklar.

    Model ayarlanmamışsa, `openai/*` ise veya `openai-codex/*` ise `agents.defaults.model` değerini `openai/gpt-5.4` olarak ayarlar.

  </Accordion>
  <Accordion title="xAI (Grok) API anahtarı">
    `XAI_API_KEY` ister ve xAI’yi model sağlayıcısı olarak yapılandırır.
  </Accordion>
  <Accordion title="OpenCode">
    `OPENCODE_API_KEY` (veya `OPENCODE_ZEN_API_KEY`) ister ve Zen ya da Go kataloğunu seçmenize izin verir.
    Kurulum URL’si: [opencode.ai/auth](https://opencode.ai/auth).
  </Accordion>
  <Accordion title="API anahtarı (genel)">
    Anahtarı sizin için saklar.
  </Accordion>
  <Accordion title="Vercel AI Gateway">
    `AI_GATEWAY_API_KEY` ister.
    Daha fazla ayrıntı: [Vercel AI Gateway](/tr/providers/vercel-ai-gateway).
  </Accordion>
  <Accordion title="Cloudflare AI Gateway">
    Hesap kimliği, Gateway kimliği ve `CLOUDFLARE_AI_GATEWAY_API_KEY` ister.
    Daha fazla ayrıntı: [Cloudflare AI Gateway](/tr/providers/cloudflare-ai-gateway).
  </Accordion>
  <Accordion title="MiniMax">
    Yapılandırma otomatik yazılır. Barındırılan varsayılan `MiniMax-M2.7`’dir; API anahtarı kurulumu
    `minimax/...`, OAuth kurulumu ise `minimax-portal/...` kullanır.
    Daha fazla ayrıntı: [MiniMax](/tr/providers/minimax).
  </Accordion>
  <Accordion title="StepFun">
    Yapılandırma, Çin veya global uç noktalardaki StepFun standardı ya da Step Plan için otomatik yazılır.
    Standard şu anda `step-3.5-flash` içerir ve Step Plan ayrıca `step-3.5-flash-2603` içerir.
    Daha fazla ayrıntı: [StepFun](/tr/providers/stepfun).
  </Accordion>
  <Accordion title="Synthetic (Anthropic uyumlu)">
    `SYNTHETIC_API_KEY` ister.
    Daha fazla ayrıntı: [Synthetic](/tr/providers/synthetic).
  </Accordion>
  <Accordion title="Ollama (Bulut ve yerel açık modeller)">
    Önce `Bulut + Yerel`, `Yalnızca Bulut` veya `Yalnızca Yerel` seçeneklerini ister.
    `Yalnızca Bulut`, `https://ollama.com` ile `OLLAMA_API_KEY` kullanır.
    Ana makine destekli modlar temel URL’yi ister (varsayılan `http://127.0.0.1:11434`), kullanılabilir modelleri keşfeder ve varsayılanlar önerir.
    `Bulut + Yerel`, ayrıca o Ollama ana makinesinin bulut erişimi için oturum açıp açmadığını da denetler.
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
    - **Gizli başvurusu kullan** (ortam başvurusu veya yapılandırılmış sağlayıcı başvurusu, ön denetim doğrulaması ile)

    Etkileşimsiz bayraklar:
    - `--auth-choice custom-api-key`
    - `--custom-base-url`
    - `--custom-model-id`
    - `--custom-api-key` (isteğe bağlı; varsayılan olarak `CUSTOM_API_KEY` kullanılır)
    - `--custom-provider-id` (isteğe bağlı)
    - `--custom-compatibility <openai|anthropic>` (isteğe bağlı; varsayılan `openai`)

  </Accordion>
  <Accordion title="Atla">
    Auth yapılandırılmadan bırakır.
  </Accordion>
</AccordionGroup>

Model davranışı:

- Algılanan seçeneklerden varsayılan modeli seçin veya sağlayıcı ve modeli elle girin.
- Onboarding bir sağlayıcı auth seçeneğinden başladığında model seçici,
  o sağlayıcıyı otomatik olarak tercih eder. Volcengine ve BytePlus için bu tercih
  onların coding-plan varyantlarıyla da eşleşir (`volcengine-plan/*`,
  `byteplus-plan/*`).
- Tercih edilen sağlayıcı filtresi boş kalırsa seçici,
  hiç model göstermemek yerine tam kataloğa geri döner.
- Sihirbaz bir model denetimi çalıştırır ve yapılandırılan model bilinmiyorsa veya auth eksikse uyarı verir.

Kimlik bilgisi ve profil yolları:

- Auth profilleri (API anahtarları + OAuth): `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- Eski OAuth içe aktarma: `~/.openclaw/credentials/oauth.json`

Kimlik bilgisi depolama modu:

- Varsayılan onboarding davranışı, API anahtarlarını auth profillerinde düz metin değerler olarak kalıcılaştırır.
- `--secret-input-mode ref`, düz metin anahtar depolaması yerine başvuru modunu etkinleştirir.
  Etkileşimli kurulumda şunlardan birini seçebilirsiniz:
  - ortam değişkeni başvurusu (örneğin `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`)
  - sağlayıcı takma adı + kimlik ile yapılandırılmış sağlayıcı başvurusu (`file` veya `exec`)
- Etkileşimli başvuru modu, kaydetmeden önce hızlı bir ön denetim doğrulaması çalıştırır.
  - Ortam başvuruları: değişken adını ve mevcut onboarding ortamındaki boş olmayan değeri doğrular.
  - Sağlayıcı başvuruları: sağlayıcı yapılandırmasını doğrular ve istenen kimliği çözümler.
  - Ön denetim başarısız olursa onboarding hatayı gösterir ve yeniden denemenize izin verir.
- Etkileşimsiz modda `--secret-input-mode ref` yalnızca ortam desteklidir.
  - Sağlayıcı ortam değişkenini onboarding işlem ortamında ayarlayın.
  - Satır içi anahtar bayrakları (örneğin `--openai-api-key`) bu ortam değişkeninin ayarlanmış olmasını gerektirir; aksi halde onboarding hızlıca başarısız olur.
  - Özel sağlayıcılar için etkileşimsiz `ref` modu, `models.providers.<id>.apiKey` değerini `{ source: "env", provider: "default", id: "CUSTOM_API_KEY" }` olarak saklar.
  - Bu özel sağlayıcı durumunda `--custom-api-key`, `CUSTOM_API_KEY` ayarlanmış olmasını gerektirir; aksi halde onboarding hızlıca başarısız olur.
- Gateway auth kimlik bilgileri, etkileşimli kurulumda düz metin ve SecretRef seçeneklerini destekler:
  - Token modu: **Düz metin token oluştur/sakla** (varsayılan) veya **SecretRef kullan**.
  - Parola modu: düz metin veya SecretRef.
- Etkileşimsiz token SecretRef yolu: `--gateway-token-ref-env <ENV_VAR>`.
- Mevcut düz metin kurulumlar değişmeden çalışmaya devam eder.

<Note>
Başsız ve sunucu ipucu: OAuth’u tarayıcısı olan bir makinede tamamlayın, ardından
o ajanın `auth-profiles.json` dosyasını (örneğin
`~/.openclaw/agents/<agentId>/agent/auth-profiles.json` veya eşleşen
`$OPENCLAW_STATE_DIR/...` yolu) Gateway ana makinesine kopyalayın. `credentials/oauth.json`
yalnızca eski bir içe aktarma kaynağıdır.
</Note>

## Çıktılar ve iç yapılar

`~/.openclaw/openclaw.json` içindeki tipik alanlar:

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers` (MiniMax seçildiyse)
- `tools.profile` (yerel onboarding, ayarlanmamışsa varsayılan olarak `"coding"` kullanır; mevcut açık değerler korunur)
- `gateway.*` (mode, bind, auth, tailscale)
- `session.dmScope` (yerel onboarding, ayarlanmamışsa varsayılan olarak `per-channel-peer` yapar; mevcut açık değerler korunur)
- `channels.telegram.botToken`, `channels.discord.token`, `channels.matrix.*`, `channels.signal.*`, `channels.imessage.*`
- İstemlerde katıldığınızda kanal allowlist’leri (Slack, Discord, Matrix, Microsoft Teams) (adlar mümkün olduğunda kimliklere çözümlenir)
- `skills.install.nodeManager`
  - `setup --node-manager` bayrağı `npm`, `pnpm` veya `bun` kabul eder.
  - Elle yapılandırma daha sonra yine de `skills.install.nodeManager: "yarn"` ayarlayabilir.
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add`, `agents.list[]` ve isteğe bağlı `bindings` yazar.

WhatsApp kimlik bilgileri `~/.openclaw/credentials/whatsapp/<accountId>/` altında tutulur.
Oturumlar `~/.openclaw/agents/<agentId>/sessions/` altında saklanır.

<Note>
Bazı kanallar Plugin olarak sunulur. Kurulum sırasında seçildiklerinde sihirbaz,
kanal yapılandırmasından önce Plugin’i yüklemenizi ister (npm veya yerel yol).
</Note>

Gateway sihirbazı RPC:

- `wizard.start`
- `wizard.next`
- `wizard.cancel`
- `wizard.status`

İstemciler (macOS uygulaması ve Control UI), onboarding mantığını yeniden uygulamadan adımları işleyebilir.

Signal kurulum davranışı:

- Uygun sürüm varlığını indirir
- Bunu `~/.openclaw/tools/signal-cli/<version>/` altında saklar
- Yapılandırmaya `channels.signal.cliPath` yazar
- JVM derlemeleri Java 21 gerektirir
- Kullanılabildiğinde yerel derlemeler kullanılır
- Windows, WSL2 kullanır ve WSL içinde Linux signal-cli akışını izler

## İlgili belgeler

- Onboarding merkezi: [Onboarding (CLI)](/tr/start/wizard)
- Otomasyon ve betikler: [CLI Otomasyonu](/tr/start/wizard-cli-automation)
- Komut başvurusu: [`openclaw onboard`](/cli/onboard)
