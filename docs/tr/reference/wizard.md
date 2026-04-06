---
read_when:
    - Belirli bir başlangıç adımını veya bayrağını arıyorsunuz
    - Etkileşimsiz kiple başlangıcı otomatikleştiriyorsunuz
    - Başlangıç davranışında hata ayıklıyorsunuz
sidebarTitle: Onboarding Reference
summary: 'CLI başlangıcı için tam başvuru: her adım, bayrak ve yapılandırma alanı'
title: Başlangıç Başvurusu
x-i18n:
    generated_at: "2026-04-06T03:12:56Z"
    model: gpt-5.4
    provider: openai
    source_hash: e02a4da4a39ba335199095723f5d3b423671eb12efc2d9e4f9e48c1e8ee18419
    source_path: reference/wizard.md
    workflow: 15
---

# Başlangıç Başvurusu

Bu, `openclaw onboard` için tam başvurudur.
Üst düzey genel bakış için bkz. [Başlangıç (CLI)](/tr/start/wizard).

## Akış ayrıntıları (yerel kip)

<Steps>
  <Step title="Mevcut yapılandırma algılama">
    - `~/.openclaw/openclaw.json` varsa **Keep / Modify / Reset** seçeneklerinden birini seçin.
    - Başlangıcı yeniden çalıştırmak, siz açıkça **Reset** seçmediğiniz sürece
      (veya `--reset` geçmediğiniz sürece) hiçbir şeyi silmez.
    - CLI `--reset` varsayılan olarak `config+creds+sessions` kullanır; çalışma alanını da kaldırmak için
      `--reset-scope full` kullanın.
    - Yapılandırma geçersizse veya eski anahtarlar içeriyorsa sihirbaz durur ve
      devam etmeden önce `openclaw doctor` çalıştırmanızı ister.
    - Sıfırlama `trash` kullanır (`rm` asla kullanılmaz) ve şu kapsamları sunar:
      - Yalnızca yapılandırma
      - Yapılandırma + kimlik bilgileri + oturumlar
      - Tam sıfırlama (çalışma alanını da kaldırır)
  </Step>
  <Step title="Model/Auth">
    - **Anthropic API key**: Varsa `ANTHROPIC_API_KEY` kullanır veya sizden bir anahtar ister, ardından daemon kullanımı için kaydeder.
    - **Anthropic API key**: başlangıç/yapılandırma içinde tercih edilen Anthropic asistan seçeneğidir.
    - **Anthropic setup-token (legacy/manual)**: başlangıç/yapılandırmada yeniden kullanılabilir, ancak Anthropic OpenClaw kullanıcılarına OpenClaw Claude-giriş yolunun üçüncü taraf harness kullanımı sayıldığını ve Claude hesabında **Extra Usage** gerektirdiğini söyledi.
    - **OpenAI Code (Codex) subscription (Codex CLI)**: `~/.codex/auth.json` varsa başlangıç bunu yeniden kullanabilir. Yeniden kullanılan Codex CLI kimlik bilgileri Codex CLI tarafından yönetilmeye devam eder; süreleri dolduğunda OpenClaw önce bu kaynağı yeniden okur ve sağlayıcı bunu yenileyebiliyorsa, sahipliğini kendisi almaktansa yenilenmiş kimlik bilgisini yeniden Codex depolamasına yazar.
    - **OpenAI Code (Codex) subscription (OAuth)**: tarayıcı akışı; `code#state` değerini yapıştırın.
      - Model ayarlanmamışsa veya `openai/*` ise `agents.defaults.model` değerini `openai-codex/gpt-5.4` olarak ayarlar.
    - **OpenAI API key**: Varsa `OPENAI_API_KEY` kullanır veya sizden bir anahtar ister, ardından bunu auth profillerinde saklar.
      - Model ayarlanmamışsa, `openai/*` ise veya `openai-codex/*` ise `agents.defaults.model` değerini `openai/gpt-5.4` olarak ayarlar.
    - **xAI (Grok) API key**: `XAI_API_KEY` ister ve xAI'yi model sağlayıcısı olarak yapılandırır.
    - **OpenCode**: `OPENCODE_API_KEY` (veya `OPENCODE_ZEN_API_KEY`, https://opencode.ai/auth adresinden alın) ister ve Zen veya Go kataloğunu seçmenize izin verir.
    - **Ollama**: Ollama temel URL'sini ister, **Cloud + Local** veya **Local** kipini sunar, mevcut modelleri keşfeder ve gerektiğinde seçilen yerel modeli otomatik olarak çeker.
    - Daha fazla ayrıntı: [Ollama](/tr/providers/ollama)
    - **API key**: anahtarı sizin için saklar.
    - **Vercel AI Gateway (multi-model proxy)**: `AI_GATEWAY_API_KEY` ister.
    - Daha fazla ayrıntı: [Vercel AI Gateway](/tr/providers/vercel-ai-gateway)
    - **Cloudflare AI Gateway**: Hesap Kimliği, Gateway Kimliği ve `CLOUDFLARE_AI_GATEWAY_API_KEY` ister.
    - Daha fazla ayrıntı: [Cloudflare AI Gateway](/tr/providers/cloudflare-ai-gateway)
    - **MiniMax**: yapılandırma otomatik yazılır; barındırılan varsayılan `MiniMax-M2.7` olur.
      API anahtarı kurulumu `minimax/...`, OAuth kurulumu ise
      `minimax-portal/...` kullanır.
    - Daha fazla ayrıntı: [MiniMax](/tr/providers/minimax)
    - **StepFun**: yapılandırma, Çin veya global uç noktalarda StepFun standard veya Step Plan için otomatik yazılır.
    - Standard şu anda `step-3.5-flash` içerir, Step Plan ise ayrıca `step-3.5-flash-2603` içerir.
    - Daha fazla ayrıntı: [StepFun](/tr/providers/stepfun)
    - **Synthetic (Anthropic-compatible)**: `SYNTHETIC_API_KEY` ister.
    - Daha fazla ayrıntı: [Synthetic](/tr/providers/synthetic)
    - **Moonshot (Kimi K2)**: yapılandırma otomatik yazılır.
    - **Kimi Coding**: yapılandırma otomatik yazılır.
    - Daha fazla ayrıntı: [Moonshot AI (Kimi + Kimi Coding)](/tr/providers/moonshot)
    - **Skip**: henüz kimlik doğrulama yapılandırılmaz.
    - Algılanan seçeneklerden varsayılan bir model seçin (veya `provider/model` değerini el ile girin). En iyi kalite ve daha düşük prompt-injection riski için, sağlayıcı yığınınızda mevcut en güçlü en yeni nesil modeli seçin.
    - Başlangıç bir model denetimi çalıştırır ve yapılandırılan model bilinmiyorsa veya kimlik doğrulaması eksikse uyarır.
    - API anahtarı depolama kipi varsayılan olarak düz metin auth-profile değerlerini kullanır. Bunun yerine ortam destekli başvuruları saklamak için `--secret-input-mode ref` kullanın (örneğin `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`).
    - Auth profilleri `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` içinde bulunur (API anahtarları + OAuth). `~/.openclaw/credentials/oauth.json` yalnızca eski içe aktarma içindir.
    - Daha fazla ayrıntı: [/concepts/oauth](/tr/concepts/oauth)
    <Note>
    Başsız/sunucu ipucu: OAuth işlemini tarayıcısı olan bir makinede tamamlayın, ardından
    bu aracının `auth-profiles.json` dosyasını (örneğin
    `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` veya eşleşen
    `$OPENCLAW_STATE_DIR/...` yolu) gateway ana makinesine kopyalayın. `credentials/oauth.json`
    yalnızca eski bir içe aktarma kaynağıdır.
    </Note>
  </Step>
  <Step title="Çalışma Alanı">
    - Varsayılan `~/.openclaw/workspace` (yapılandırılabilir).
    - Aracı bootstrap ritüeli için gereken çalışma alanı dosyalarını başlatır.
    - Tam çalışma alanı düzeni + yedekleme rehberi: [Aracı çalışma alanı](/tr/concepts/agent-workspace)
  </Step>
  <Step title="Gateway">
    - Port, bind, auth mode, Tailscale exposure.
    - Kimlik doğrulama önerisi: yerel WS istemcilerinin de kimlik doğrulaması yapması için loopback kullanılsa bile **Token** koruyun.
    - Token kipinde, etkileşimli kurulum şunları sunar:
      - **Generate/store plaintext token** (varsayılan)
      - **Use SecretRef** (isteğe bağlı katılım)
      - Quickstart, başlangıç yoklaması/pano bootstrap'i için `env`, `file` ve `exec` sağlayıcıları genelindeki mevcut `gateway.auth.token` SecretRef değerlerini yeniden kullanır.
      - Bu SecretRef yapılandırılmış ama çözümlenemiyorsa başlangıç, çalışma zamanı kimlik doğrulamasını sessizce zayıflatmak yerine açık bir düzeltme iletisiyle erken başarısız olur.
    - Parola kipinde, etkileşimli kurulum ayrıca düz metin veya SecretRef depolamayı da destekler.
    - Etkileşimsiz token SecretRef yolu: `--gateway-token-ref-env <ENV_VAR>`.
      - Başlangıç süreci ortamında boş olmayan bir ortam değişkeni gerektirir.
      - `--gateway-token` ile birlikte kullanılamaz.
    - Yalnızca her yerel sürece tamamen güveniyorsanız kimlik doğrulamayı devre dışı bırakın.
    - Loopback dışı bind değerleri yine de kimlik doğrulama gerektirir.
  </Step>
  <Step title="Kanallar">
    - [WhatsApp](/tr/channels/whatsapp): isteğe bağlı QR girişi.
    - [Telegram](/tr/channels/telegram): bot token.
    - [Discord](/tr/channels/discord): bot token.
    - [Google Chat](/tr/channels/googlechat): hizmet hesabı JSON'u + webhook audience.
    - [Mattermost](/tr/channels/mattermost) (eklenti): bot token + temel URL.
    - [Signal](/tr/channels/signal): isteğe bağlı `signal-cli` kurulumu + hesap yapılandırması.
    - [BlueBubbles](/tr/channels/bluebubbles): **iMessage için önerilir**; sunucu URL'si + parola + webhook.
    - [iMessage](/tr/channels/imessage): eski `imsg` CLI yolu + DB erişimi.
    - DM güvenliği: varsayılan eşleştirmedir. İlk DM bir kod gönderir; `openclaw pairing approve <channel> <code>` ile onaylayın veya izin listelerini kullanın.
  </Step>
  <Step title="Web araması">
    - Brave, DuckDuckGo, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search, Ollama Web Search, Perplexity, SearXNG veya Tavily gibi desteklenen bir sağlayıcı seçin (veya atlayın).
    - API destekli sağlayıcılar hızlı kurulum için ortam değişkenlerini veya mevcut yapılandırmayı kullanabilir; anahtarsız sağlayıcılar ise kendi sağlayıcılarına özgü önkoşulları kullanır.
    - `--skip-search` ile atlayın.
    - Daha sonra yapılandırın: `openclaw configure --section web`.
  </Step>
  <Step title="Daemon kurulumu">
    - macOS: LaunchAgent
      - Giriş yapılmış bir kullanıcı oturumu gerektirir; başsız kullanım için özel bir LaunchDaemon kullanın (paketle gelmez).
    - Linux (ve WSL2 üzerinden Windows): systemd user unit
      - Başlangıç, çıkış yaptıktan sonra da Gateway açık kalsın diye `loginctl enable-linger <user>` etkinleştirmeye çalışır.
      - sudo isteyebilir (`/var/lib/systemd/linger` yazar); önce sudo olmadan dener.
    - **Çalışma zamanı seçimi:** Node (önerilir; WhatsApp/Telegram için gereklidir). Bun **önerilmez**.
    - Token kimlik doğrulaması bir token gerektiriyorsa ve `gateway.auth.token` SecretRef tarafından yönetiliyorsa daemon kurulumu bunu doğrular ancak çözümlenmiş düz metin token değerlerini supervisor hizmet ortamı meta verisine kalıcı olarak yazmaz.
    - Token kimlik doğrulaması bir token gerektiriyorsa ve yapılandırılmış token SecretRef çözümlenemiyorsa daemon kurulumu uygulanabilir yönlendirmeyle engellenir.
    - Hem `gateway.auth.token` hem de `gateway.auth.password` yapılandırılmışsa ve `gateway.auth.mode` ayarlanmamışsa, kip açıkça ayarlanana kadar daemon kurulumu engellenir.
  </Step>
  <Step title="Sağlık denetimi">
    - Gateway'i başlatır (gerekirse) ve `openclaw health` çalıştırır.
    - İpucu: `openclaw status --deep`, durum çıktısına canlı gateway sağlık yoklamasını ekler; desteklendiğinde kanal yoklamalarını da içerir (erişilebilir bir gateway gerekir).
  </Step>
  <Step title="Skills (önerilir)">
    - Mevcut Skills değerlerini okur ve gereksinimleri denetler.
    - Bir düğüm yöneticisi seçmenizi sağlar: **npm / pnpm** (bun önerilmez).
    - İsteğe bağlı bağımlılıkları kurar (bazıları macOS'ta Homebrew kullanır).
  </Step>
  <Step title="Bitir">
    - Ek özellikler için iOS/Android/macOS uygulamaları dahil olmak üzere özet + sonraki adımlar.
  </Step>
</Steps>

<Note>
GUI algılanmazsa başlangıç, bir tarayıcı açmak yerine Control UI için SSH port yönlendirme yönergeleri yazdırır.
Control UI varlıkları eksikse başlangıç bunları oluşturmaya çalışır; geri dönüş olarak `pnpm ui:build` kullanılır (UI bağımlılıklarını otomatik kurar).
</Note>

## Etkileşimsiz kip

Başlangıcı otomatikleştirmek veya betiklemek için `--non-interactive` kullanın:

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice apiKey \
  --anthropic-api-key "$ANTHROPIC_API_KEY" \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --install-daemon \
  --daemon-runtime node \
  --skip-skills
```

Makine tarafından okunabilir özet için `--json` ekleyin.

Etkileşimsiz kipte Gateway token SecretRef:

```bash
export OPENCLAW_GATEWAY_TOKEN="your-token"
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice skip \
  --gateway-auth token \
  --gateway-token-ref-env OPENCLAW_GATEWAY_TOKEN
```

`--gateway-token` ve `--gateway-token-ref-env` birbirini dışlar.

<Note>
`--json`, etkileşimsiz kip anlamına gelmez. Betikler için `--non-interactive` (ve `--workspace`) kullanın.
</Note>

Sağlayıcıya özgü komut örnekleri [CLI Automation](/tr/start/wizard-cli-automation#provider-specific-examples) içinde bulunur.
Bayrak anlambilimi ve adım sıralaması için bu başvuru sayfasını kullanın.

### Aracı ekleme (etkileşimsiz)

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.4 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

## Gateway wizard RPC

Gateway, başlangıç akışını RPC üzerinden açığa çıkarır (`wizard.start`, `wizard.next`, `wizard.cancel`, `wizard.status`).
İstemciler (macOS uygulaması, Control UI), başlangıç mantığını yeniden uygulamadan adımları işleyebilir.

## Signal kurulumu (`signal-cli`)

Başlangıç, `signal-cli` aracını GitHub sürümlerinden kurabilir:

- Uygun sürüm varlığını indirir.
- Bunu `~/.openclaw/tools/signal-cli/<version>/` altında saklar.
- Yapılandırmanıza `channels.signal.cliPath` yazar.

Notlar:

- JVM derlemeleri **Java 21** gerektirir.
- Yerel derlemeler mevcut olduğunda kullanılır.
- Windows, WSL2 kullanır; signal-cli kurulumu WSL içindeki Linux akışını izler.

## Sihirbazın yazdıkları

`~/.openclaw/openclaw.json` içindeki tipik alanlar:

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers` (Minimax seçildiyse)
- `tools.profile` (yerel başlangıç, ayarlanmamışsa varsayılan olarak `"coding"` kullanır; mevcut açık değerler korunur)
- `gateway.*` (mode, bind, auth, tailscale)
- `session.dmScope` (davranış ayrıntıları: [CLI Kurulum Başvurusu](/tr/start/wizard-cli-reference#outputs-and-internals))
- `channels.telegram.botToken`, `channels.discord.token`, `channels.matrix.*`, `channels.signal.*`, `channels.imessage.*`
- İstemler sırasında katılım sağladığınızda kanal izin listeleri (Slack/Discord/Matrix/Microsoft Teams) mümkünse adlar kimliklere çözülür.
- `skills.install.nodeManager`
  - `setup --node-manager`, `npm`, `pnpm` veya `bun` kabul eder.
  - El ile yapılandırma, `skills.install.nodeManager` doğrudan ayarlanarak yine de `yarn` kullanabilir.
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add`, `agents.list[]` ve isteğe bağlı `bindings` yazar.

WhatsApp kimlik bilgileri `~/.openclaw/credentials/whatsapp/<accountId>/` altında bulunur.
Oturumlar `~/.openclaw/agents/<agentId>/sessions/` altında saklanır.

Bazı kanallar eklenti olarak sunulur. Kurulum sırasında bunlardan birini seçtiğinizde başlangıç,
yapılandırılabilmeden önce sizden onu kurmanızı ister (npm veya yerel bir yol).

## İlgili belgeler

- Başlangıç genel bakışı: [Başlangıç (CLI)](/tr/start/wizard)
- macOS uygulaması başlangıcı: [Başlangıç](/tr/start/onboarding)
- Yapılandırma başvurusu: [Gateway configuration](/tr/gateway/configuration)
- Sağlayıcılar: [WhatsApp](/tr/channels/whatsapp), [Telegram](/tr/channels/telegram), [Discord](/tr/channels/discord), [Google Chat](/tr/channels/googlechat), [Signal](/tr/channels/signal), [BlueBubbles](/tr/channels/bluebubbles) (iMessage), [iMessage](/tr/channels/imessage) (eski)
- Skills: [Skills](/tr/tools/skills), [Skills config](/tr/tools/skills-config)
