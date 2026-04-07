---
read_when:
    - Belirli bir onboarding adımını veya işaretini arıyorsanız
    - Onboarding'i etkileşimsiz modla otomatikleştiriyorsanız
    - Onboarding davranışında hata ayıklıyorsanız
sidebarTitle: Onboarding Reference
summary: 'CLI onboarding için tam başvuru: her adım, işaret ve yapılandırma alanı'
title: Onboarding Başvurusu
x-i18n:
    generated_at: "2026-04-07T08:50:13Z"
    model: gpt-5.4
    provider: openai
    source_hash: a142b9ec4323fabb9982d05b64375d2b4a4007dffc910acbee3a38ff871a7236
    source_path: reference/wizard.md
    workflow: 15
---

# Onboarding Başvurusu

Bu, `openclaw onboard` için tam başvurudur.
Üst düzey bir genel bakış için bkz. [Onboarding (CLI)](/tr/start/wizard).

## Akış ayrıntıları (yerel mod)

<Steps>
  <Step title="Mevcut yapılandırma algılama">
    - `~/.openclaw/openclaw.json` varsa **Keep / Modify / Reset** seçeneklerinden birini seçin.
    - Onboarding'i yeniden çalıştırmak, açıkça **Reset** seçmediğiniz sürece
      (veya `--reset` geçmediğiniz sürece) hiçbir şeyi silmez.
    - CLI `--reset` varsayılan olarak `config+creds+sessions` kullanır; çalışma alanını da kaldırmak için `--reset-scope full`
      kullanın.
    - Yapılandırma geçersizse veya eski anahtarlar içeriyorsa wizard durur ve
      devam etmeden önce `openclaw doctor` çalıştırmanızı ister.
    - Reset, `trash` kullanır (`rm` asla kullanılmaz) ve şu kapsamları sunar:
      - Yalnızca yapılandırma
      - Yapılandırma + kimlik bilgileri + oturumlar
      - Tam sıfırlama (çalışma alanını da kaldırır)
  </Step>
  <Step title="Model/Auth">
    - **Anthropic API key**: varsa `ANTHROPIC_API_KEY` kullanır veya bir anahtar ister, ardından daemon kullanımı için kaydeder.
    - **Anthropic API key**: onboarding/configure içinde tercih edilen Anthropic asistan seçimi.
    - **Anthropic setup-token**: onboarding/configure içinde hâlâ kullanılabilir, ancak OpenClaw artık mümkün olduğunda Claude CLI yeniden kullanımını tercih eder.
    - **OpenAI Code (Codex) subscription (Codex CLI)**: `~/.codex/auth.json` varsa onboarding bunu yeniden kullanabilir. Yeniden kullanılan Codex CLI kimlik bilgileri Codex CLI tarafından yönetilmeye devam eder; süreleri dolduğunda OpenClaw önce bu kaynağı yeniden okur ve provider bunu yenileyebiliyorsa, sahipliğini almak yerine yenilenmiş kimlik bilgisini tekrar Codex depolamasına yazar.
    - **OpenAI Code (Codex) subscription (OAuth)**: tarayıcı akışı; `code#state` değerini yapıştırın.
      - Model ayarlanmamışsa veya `openai/*` ise `agents.defaults.model` değerini `openai-codex/gpt-5.4` olarak ayarlar.
    - **OpenAI API key**: varsa `OPENAI_API_KEY` kullanır veya bir anahtar ister, ardından bunu auth profillerinde saklar.
      - Model ayarlanmamışsa, `openai/*` veya `openai-codex/*` ise `agents.defaults.model` değerini `openai/gpt-5.4` olarak ayarlar.
    - **xAI (Grok) API key**: `XAI_API_KEY` ister ve xAI'ı model provider olarak yapılandırır.
    - **OpenCode**: `OPENCODE_API_KEY` (veya `OPENCODE_ZEN_API_KEY`, bunu https://opencode.ai/auth adresinden alın) ister ve Zen veya Go kataloğunu seçmenize izin verir.
    - **Ollama**: Ollama temel URL'sini ister, **Cloud + Local** veya **Local** modu sunar, kullanılabilir modelleri keşfeder ve gerektiğinde seçilen yerel modeli otomatik olarak çeker.
    - Daha fazla ayrıntı: [Ollama](/tr/providers/ollama)
    - **API key**: anahtarı sizin için saklar.
    - **Vercel AI Gateway (çok modelli proxy)**: `AI_GATEWAY_API_KEY` ister.
    - Daha fazla ayrıntı: [Vercel AI Gateway](/tr/providers/vercel-ai-gateway)
    - **Cloudflare AI Gateway**: Account ID, Gateway ID ve `CLOUDFLARE_AI_GATEWAY_API_KEY` ister.
    - Daha fazla ayrıntı: [Cloudflare AI Gateway](/tr/providers/cloudflare-ai-gateway)
    - **MiniMax**: yapılandırma otomatik olarak yazılır; barındırılan varsayılan `MiniMax-M2.7` olur.
      API anahtarı kurulumu `minimax/...` kullanır, OAuth kurulumu ise
      `minimax-portal/...` kullanır.
    - Daha fazla ayrıntı: [MiniMax](/tr/providers/minimax)
    - **StepFun**: yapılandırma, Çin veya küresel uç noktalarda StepFun standard veya Step Plan için otomatik yazılır.
    - Standard şu anda `step-3.5-flash` içerir ve Step Plan ayrıca `step-3.5-flash-2603` içerir.
    - Daha fazla ayrıntı: [StepFun](/tr/providers/stepfun)
    - **Synthetic (Anthropic-compatible)**: `SYNTHETIC_API_KEY` ister.
    - Daha fazla ayrıntı: [Synthetic](/tr/providers/synthetic)
    - **Moonshot (Kimi K2)**: yapılandırma otomatik olarak yazılır.
    - **Kimi Coding**: yapılandırma otomatik olarak yazılır.
    - Daha fazla ayrıntı: [Moonshot AI (Kimi + Kimi Coding)](/tr/providers/moonshot)
    - **Skip**: henüz auth yapılandırılmaz.
    - Algılanan seçeneklerden varsayılan bir model seçin (veya provider/model'i elle girin). En iyi kalite ve daha düşük prompt injection riski için provider yığınınızda bulunan en güçlü yeni nesil modeli seçin.
    - Onboarding bir model denetimi çalıştırır ve yapılandırılan model bilinmiyorsa veya auth eksikse uyarı verir.
    - API anahtarı depolama modu varsayılan olarak düz metin auth-profile değerleri kullanır. Bunun yerine env destekli başvurular saklamak için `--secret-input-mode ref` kullanın (örneğin `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`).
    - Auth profilleri `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` içinde bulunur (API anahtarları + OAuth). `~/.openclaw/credentials/oauth.json` eski ve yalnızca içe aktarma içindir.
    - Daha fazla ayrıntı: [/concepts/oauth](/tr/concepts/oauth)
    <Note>
    Headless/sunucu ipucu: OAuth'u tarayıcısı olan bir makinede tamamlayın, sonra
    o ajanın `auth-profiles.json` dosyasını (örneğin
    `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` veya eşleşen
    `$OPENCLAW_STATE_DIR/...` yolu) gateway ana makinesine kopyalayın. `credentials/oauth.json`
    yalnızca eski bir içe aktarma kaynağıdır.
    </Note>
  </Step>
  <Step title="Çalışma alanı">
    - Varsayılan `~/.openclaw/workspace` (yapılandırılabilir).
    - Ajan bootstrap ritüeli için gereken çalışma alanı dosyalarını yerleştirir.
    - Tam çalışma alanı düzeni + yedekleme kılavuzu: [Agent workspace](/tr/concepts/agent-workspace)
  </Step>
  <Step title="Gateway">
    - Port, bind, auth modu, Tailscale yayını.
    - Auth önerisi: yerel WS istemcilerinin kimlik doğrulaması yapması için loopback üzerinde bile **Token** kullanın.
    - Token modunda etkileşimli kurulum şunları sunar:
      - **Generate/store plaintext token** (varsayılan)
      - **Use SecretRef** (isteğe bağlı)
      - Hızlı başlangıç, onboarding probe/dashboard bootstrap için `env`, `file` ve `exec` provider'ları genelinde mevcut `gateway.auth.token` SecretRef'lerini yeniden kullanır.
      - Bu SecretRef yapılandırılmışsa ancak çözümlenemiyorsa onboarding, çalışma zamanı auth'unu sessizce zayıflatmak yerine net bir düzeltme iletisiyle erken başarısız olur.
    - Parola modunda etkileşimli kurulum, düz metin veya SecretRef depolamayı da destekler.
    - Etkileşimsiz token SecretRef yolu: `--gateway-token-ref-env <ENV_VAR>`.
      - Onboarding süreç ortamında boş olmayan bir env değişkeni gerektirir.
      - `--gateway-token` ile birlikte kullanılamaz.
    - Auth'u yalnızca tüm yerel süreçlere tamamen güveniyorsanız devre dışı bırakın.
    - Loopback olmayan bind'ler yine de auth gerektirir.
  </Step>
  <Step title="Kanallar">
    - [WhatsApp](/tr/channels/whatsapp): isteğe bağlı QR oturumu açma.
    - [Telegram](/tr/channels/telegram): bot token.
    - [Discord](/tr/channels/discord): bot token.
    - [Google Chat](/tr/channels/googlechat): service account JSON + webhook audience.
    - [Mattermost](/tr/channels/mattermost) (plugin): bot token + temel URL.
    - [Signal](/tr/channels/signal): isteğe bağlı `signal-cli` kurulumu + hesap yapılandırması.
    - [BlueBubbles](/tr/channels/bluebubbles): **iMessage için önerilir**; sunucu URL'si + parola + webhook.
    - [iMessage](/tr/channels/imessage): eski `imsg` CLI yolu + DB erişimi.
    - DM güvenliği: varsayılan eşleştirmedir. İlk DM bir kod gönderir; bunu `openclaw pairing approve <channel> <code>` ile onaylayın veya izin listeleri kullanın.
  </Step>
  <Step title="Web arama">
    - Brave, DuckDuckGo, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search, Ollama Web Search, Perplexity, SearXNG veya Tavily gibi desteklenen bir provider seçin (veya atlayın).
    - API destekli provider'lar hızlı kurulum için env değişkenleri veya mevcut yapılandırmayı kullanabilir; anahtarsız provider'lar bunun yerine provider'a özgü ön koşullarını kullanır.
    - `--skip-search` ile atlayın.
    - Daha sonra yapılandırın: `openclaw configure --section web`.
  </Step>
  <Step title="Daemon kurulumu">
    - macOS: LaunchAgent
      - Oturum açılmış bir kullanıcı oturumu gerektirir; headless için özel bir LaunchDaemon kullanın (gönderilmez).
    - Linux (ve Windows üzerinden WSL2): systemd user unit
      - Onboarding, Gateway'in oturum kapatıldıktan sonra da çalışmaya devam etmesi için `loginctl enable-linger <user>` komutuyla lingering'i etkinleştirmeye çalışır.
      - sudo isteyebilir (`/var/lib/systemd/linger` yazar); önce sudo olmadan dener.
    - **Çalışma zamanı seçimi:** Node (önerilir; WhatsApp/Telegram için gereklidir). Bun **önerilmez**.
    - Token auth bir token gerektiriyorsa ve `gateway.auth.token` SecretRef ile yönetiliyorsa daemon kurulumu bunu doğrular ancak çözümlenmiş düz metin token değerlerini supervisor hizmet ortam meta verisine kalıcı olarak yazmaz.
    - Token auth bir token gerektiriyorsa ve yapılandırılmış token SecretRef çözümlenmemişse daemon kurulumu eyleme geçirilebilir yönlendirmeyle engellenir.
    - Hem `gateway.auth.token` hem `gateway.auth.password` yapılandırılmışsa ve `gateway.auth.mode` ayarlanmamışsa, mod açıkça ayarlanana kadar daemon kurulumu engellenir.
  </Step>
  <Step title="Sağlık denetimi">
    - Gateway'i başlatır (gerekiyorsa) ve `openclaw health` çalıştırır.
    - İpucu: `openclaw status --deep`, desteklendiğinde kanal probları dahil olmak üzere canlı gateway sağlık probunu durum çıktısına ekler (erişilebilir bir gateway gerektirir).
  </Step>
  <Step title="Skills (önerilir)">
    - Kullanılabilir skill'leri okur ve gereksinimleri denetler.
    - Bir node manager seçmenize izin verir: **npm / pnpm** (bun önerilmez).
    - İsteğe bağlı bağımlılıkları yükler (bazıları macOS'ta Homebrew kullanır).
  </Step>
  <Step title="Bitir">
    - Ek özellikler için iOS/Android/macOS uygulamaları dahil özet + sonraki adımlar.
  </Step>
</Steps>

<Note>
GUI algılanmazsa onboarding, tarayıcı açmak yerine Control UI için SSH port-forward yönergeleri yazdırır.
Control UI varlıkları eksikse onboarding bunları derlemeye çalışır; geri dönüş komutu `pnpm ui:build` olur (UI bağımlılıklarını otomatik kurar).
</Note>

## Etkileşimsiz mod

Onboarding'i otomatikleştirmek veya betiklemek için `--non-interactive` kullanın:

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

Makine tarafından okunabilir bir özet için `--json` ekleyin.

Etkileşimsiz modda gateway token SecretRef:

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
`--json`, etkileşimsiz modu **ima etmez**. Betikler için `--non-interactive` (ve `--workspace`) kullanın.
</Note>

Provider'a özgü komut örnekleri [CLI Automation](/tr/start/wizard-cli-automation#provider-specific-examples) içinde bulunur.
İşaret semantiği ve adım sıralaması için bu başvuru sayfasını kullanın.

### Ajan ekle (etkileşimsiz)

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.4 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

## Gateway wizard RPC

Gateway, onboarding akışını RPC üzerinden sunar (`wizard.start`, `wizard.next`, `wizard.cancel`, `wizard.status`).
İstemciler (macOS uygulaması, Control UI), onboarding mantığını yeniden uygulamadan adımları işleyebilir.

## Signal kurulumu (`signal-cli`)

Onboarding, `signal-cli` uygulamasını GitHub sürümlerinden kurabilir:

- Uygun sürüm varlığını indirir.
- Bunu `~/.openclaw/tools/signal-cli/<version>/` altında saklar.
- Yapılandırmanıza `channels.signal.cliPath` yazar.

Notlar:

- JVM derlemeleri **Java 21** gerektirir.
- Mümkün olduğunda yerel derlemeler kullanılır.
- Windows, WSL2 kullanır; `signal-cli` kurulumu WSL içindeki Linux akışını izler.

## Wizard'ın yazdığı şeyler

`~/.openclaw/openclaw.json` içindeki tipik alanlar:

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers` (MiniMax seçildiyse)
- `tools.profile` (yerel onboarding, ayarlanmamışsa varsayılan olarak `"coding"` kullanır; mevcut açık değerler korunur)
- `gateway.*` (mod, bind, auth, tailscale)
- `session.dmScope` (davranış ayrıntıları: [CLI Setup Reference](/tr/start/wizard-cli-reference#outputs-and-internals))
- `channels.telegram.botToken`, `channels.discord.token`, `channels.matrix.*`, `channels.signal.*`, `channels.imessage.*`
- İstemlerde katıldığınızda kanal izin listeleri (Slack/Discord/Matrix/Microsoft Teams) mümkün olduğunda adlardan kimliklere çözülür.
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

Bazı kanallar plugin olarak sunulur. Kurulum sırasında birini seçtiğinizde onboarding,
yapılandırılmadan önce onu kurmanızı ister (npm veya yerel bir yol).

## İlgili belgeler

- Onboarding genel bakışı: [Onboarding (CLI)](/tr/start/wizard)
- macOS uygulaması onboarding'i: [Onboarding](/tr/start/onboarding)
- Yapılandırma başvurusu: [Gateway configuration](/tr/gateway/configuration)
- Provider'lar: [WhatsApp](/tr/channels/whatsapp), [Telegram](/tr/channels/telegram), [Discord](/tr/channels/discord), [Google Chat](/tr/channels/googlechat), [Signal](/tr/channels/signal), [BlueBubbles](/tr/channels/bluebubbles) (iMessage), [iMessage](/tr/channels/imessage) (eski)
- Skills: [Skills](/tr/tools/skills), [Skills config](/tr/tools/skills-config)
