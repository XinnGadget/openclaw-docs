---
read_when:
    - Belirli bir ilk kurulum adımını veya bayrağını arıyorsunuz
    - Etkileşimsiz mod ile ilk kurulumu otomatikleştirme
    - İlk kurulum davranışında hata ayıklama
sidebarTitle: Onboarding Reference
summary: 'CLI ile ilk kurulum için tam başvuru: her adım, bayrak ve yapılandırma alanı'
title: İlk Kurulum Başvurusu
x-i18n:
    generated_at: "2026-04-15T14:41:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1db3ff789422617634e6624f9d12c18b6a6c573721226b9c0fa6f6b7956ef33d
    source_path: reference/wizard.md
    workflow: 15
---

# İlk Kurulum Başvurusu

Bu, `openclaw onboard` için tam başvuru kılavuzudur.
Yüksek seviyeli bir genel bakış için bkz. [Onboarding (CLI)](/tr/start/wizard).

## Akış ayrıntıları (yerel mod)

<Steps>
  <Step title="Mevcut yapılandırma algılama">
    - `~/.openclaw/openclaw.json` varsa **Koru / Değiştir / Sıfırla** seçeneklerinden birini seçin.
    - İlk kurulumu yeniden çalıştırmak, açıkça **Sıfırla** seçmediğiniz sürece hiçbir şeyi silmez
      (veya `--reset` geçmediğiniz sürece).
    - CLI `--reset` varsayılan olarak `config+creds+sessions` kullanır; çalışma alanını da kaldırmak için `--reset-scope full`
      kullanın.
    - Yapılandırma geçersizse veya eski anahtarlar içeriyorsa, sihirbaz durur ve
      devam etmeden önce `openclaw doctor` çalıştırmanızı ister.
    - Sıfırlama, `trash` kullanır (`rm` asla kullanılmaz) ve şu kapsamları sunar:
      - Yalnızca yapılandırma
      - Yapılandırma + kimlik bilgileri + oturumlar
      - Tam sıfırlama (çalışma alanını da kaldırır)
  </Step>
  <Step title="Model/Kimlik Doğrulama">
    - **Anthropic API anahtarı**: varsa `ANTHROPIC_API_KEY` kullanır veya bir anahtar ister, ardından daemon kullanımı için kaydeder.
    - **Anthropic API anahtarı**: ilk kurulum/yapılandırmada tercih edilen Anthropic asistan seçimidir.
    - **Anthropic setup-token**: ilk kurulum/yapılandırmada hâlâ kullanılabilir, ancak OpenClaw artık mevcut olduğunda Claude CLI yeniden kullanımını tercih eder.
    - **OpenAI Code (Codex) aboneliği (Codex CLI)**: `~/.codex/auth.json` varsa ilk kurulum bunu yeniden kullanabilir. Yeniden kullanılan Codex CLI kimlik bilgileri Codex CLI tarafından yönetilmeye devam eder; süresi dolduğunda OpenClaw önce bu kaynağı yeniden okur ve sağlayıcı bunu yenileyebiliyorsa, yenilenen kimlik bilgisini kendisi sahiplenmek yerine tekrar Codex depolamasına yazar.
    - **OpenAI Code (Codex) aboneliği (OAuth)**: tarayıcı akışı; `code#state` değerini yapıştırın.
      - Model ayarlanmamışsa veya `openai/*` ise `agents.defaults.model` alanını `openai-codex/gpt-5.4` olarak ayarlar.
    - **OpenAI API anahtarı**: varsa `OPENAI_API_KEY` kullanır veya bir anahtar ister, ardından bunu auth profillerinde saklar.
      - Model ayarlanmamışsa, `openai/*` ise veya `openai-codex/*` ise `agents.defaults.model` alanını `openai/gpt-5.4` olarak ayarlar.
    - **xAI (Grok) API anahtarı**: `XAI_API_KEY` ister ve xAI'ı model sağlayıcısı olarak yapılandırır.
    - **OpenCode**: `OPENCODE_API_KEY` (veya `OPENCODE_ZEN_API_KEY`, almak için https://opencode.ai/auth adresine gidin) ister ve Zen veya Go kataloğunu seçmenize olanak tanır.
    - **Ollama**: önce **Cloud + Local**, **Yalnızca Cloud** veya **Yalnızca Local** seçeneklerini sunar. `Yalnızca Cloud`, `OLLAMA_API_KEY` ister ve `https://ollama.com` kullanır; host destekli modlar Ollama temel URL'sini ister, kullanılabilir modelleri keşfeder ve gerektiğinde seçilen yerel modeli otomatik olarak çeker; `Cloud + Local` ayrıca bu Ollama hostunun Cloud erişimi için oturum açıp açmadığını da kontrol eder.
    - Daha fazla ayrıntı: [Ollama](/tr/providers/ollama)
    - **API anahtarı**: anahtarı sizin için saklar.
    - **Vercel AI Gateway (çok modelli proxy)**: `AI_GATEWAY_API_KEY` ister.
    - Daha fazla ayrıntı: [Vercel AI Gateway](/tr/providers/vercel-ai-gateway)
    - **Cloudflare AI Gateway**: Account ID, Gateway ID ve `CLOUDFLARE_AI_GATEWAY_API_KEY` ister.
    - Daha fazla ayrıntı: [Cloudflare AI Gateway](/tr/providers/cloudflare-ai-gateway)
    - **MiniMax**: yapılandırma otomatik yazılır; barındırılan varsayılan `MiniMax-M2.7`'dir.
      API anahtarı kurulumu `minimax/...`, OAuth kurulumu ise
      `minimax-portal/...` kullanır.
    - Daha fazla ayrıntı: [MiniMax](/tr/providers/minimax)
    - **StepFun**: yapılandırma, Çin veya küresel uç noktalardaki standart StepFun veya Step Plan için otomatik yazılır.
    - Standart şu anda `step-3.5-flash` içerir ve Step Plan ayrıca `step-3.5-flash-2603` içerir.
    - Daha fazla ayrıntı: [StepFun](/tr/providers/stepfun)
    - **Synthetic (Anthropic uyumlu)**: `SYNTHETIC_API_KEY` ister.
    - Daha fazla ayrıntı: [Synthetic](/tr/providers/synthetic)
    - **Moonshot (Kimi K2)**: yapılandırma otomatik yazılır.
    - **Kimi Coding**: yapılandırma otomatik yazılır.
    - Daha fazla ayrıntı: [Moonshot AI (Kimi + Kimi Coding)](/tr/providers/moonshot)
    - **Atla**: henüz kimlik doğrulama yapılandırılmaz.
    - Algılanan seçeneklerden varsayılan bir model seçin (veya sağlayıcı/model bilgisini elle girin). En iyi kalite ve daha düşük istem enjeksiyonu riski için, sağlayıcı yığınınızda bulunan en güçlü yeni nesil modeli seçin.
    - İlk kurulum bir model denetimi çalıştırır ve yapılandırılan model bilinmiyorsa veya kimlik doğrulama eksikse uyarı verir.
    - API anahtarı depolama modu varsayılan olarak düz metin auth-profile değerlerini kullanır. Bunun yerine env destekli referanslar depolamak için `--secret-input-mode ref` kullanın (örneğin `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`).
    - Auth profilleri `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` içinde bulunur (API anahtarları + OAuth). `~/.openclaw/credentials/oauth.json` yalnızca eski içe aktarma için kullanılır.
    - Daha fazla ayrıntı: [/concepts/oauth](/tr/concepts/oauth)
    <Note>
    Başsız/sunucu ipucu: OAuth'u tarayıcısı olan bir makinede tamamlayın, sonra
    bu ajanın `auth-profiles.json` dosyasını (örneğin
    `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` veya eşleşen
    `$OPENCLAW_STATE_DIR/...` yolu) Gateway hostuna kopyalayın. `credentials/oauth.json`
    yalnızca eski bir içe aktarma kaynağıdır.
    </Note>
  </Step>
  <Step title="Çalışma alanı">
    - Varsayılan `~/.openclaw/workspace` (yapılandırılabilir).
    - Ajan önyükleme ritüeli için gereken çalışma alanı dosyalarını tohumlar.
    - Tam çalışma alanı düzeni + yedekleme kılavuzu: [Agent workspace](/tr/concepts/agent-workspace)
  </Step>
  <Step title="Gateway">
    - Port, bind, auth modu, Tailscale görünürlüğü.
    - Kimlik doğrulama önerisi: yerel WS istemcilerinin kimlik doğrulaması yapması gereksin diye loopback için bile **Token** kullanın.
    - Token modunda etkileşimli kurulum şunları sunar:
      - **Düz metin token oluştur/sakla** (varsayılan)
      - **SecretRef kullan** (isteğe bağlı)
      - Hızlı başlangıç, ilk kurulum yoklaması/pano önyüklemesi için `env`, `file` ve `exec` sağlayıcıları genelinde mevcut `gateway.auth.token` SecretRef'lerini yeniden kullanır.
      - Bu SecretRef yapılandırılmışsa ancak çözümlenemiyorsa, ilk kurulum çalışma zamanı kimlik doğrulamasını sessizce zayıflatmak yerine açık bir düzeltme mesajıyla erkenden başarısız olur.
    - Parola modunda etkileşimli kurulum da düz metin veya SecretRef depolamayı destekler.
    - Etkileşimsiz token SecretRef yolu: `--gateway-token-ref-env <ENV_VAR>`.
      - İlk kurulum işlem ortamında boş olmayan bir ortam değişkeni gerektirir.
      - `--gateway-token` ile birlikte kullanılamaz.
    - Yalnızca her yerel sürece tamamen güveniyorsanız kimlik doğrulamayı devre dışı bırakın.
    - Loopback dışı bind'ler yine de kimlik doğrulama gerektirir.
  </Step>
  <Step title="Kanallar">
    - [WhatsApp](/tr/channels/whatsapp): isteğe bağlı QR girişi.
    - [Telegram](/tr/channels/telegram): bot token'ı.
    - [Discord](/tr/channels/discord): bot token'ı.
    - [Google Chat](/tr/channels/googlechat): hizmet hesabı JSON'u + webhook audience.
    - [Mattermost](/tr/channels/mattermost) (Plugin): bot token'ı + temel URL.
    - [Signal](/tr/channels/signal): isteğe bağlı `signal-cli` kurulumu + hesap yapılandırması.
    - [BlueBubbles](/tr/channels/bluebubbles): **iMessage için önerilir**; sunucu URL'si + parola + webhook.
    - [iMessage](/tr/channels/imessage): eski `imsg` CLI yolu + VT erişimi.
    - DM güvenliği: varsayılan eşleştirmedir. İlk DM bir kod gönderir; `openclaw pairing approve <channel> <code>` ile onaylayın veya izin listeleri kullanın.
  </Step>
  <Step title="Web araması">
    - Brave, DuckDuckGo, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search, Ollama Web Search, Perplexity, SearXNG veya Tavily gibi desteklenen bir sağlayıcı seçin (veya atlayın).
    - API destekli sağlayıcılar hızlı kurulum için ortam değişkenlerini veya mevcut yapılandırmayı kullanabilir; anahtarsız sağlayıcılar bunun yerine sağlayıcıya özgü önkoşullarını kullanır.
    - `--skip-search` ile atlayın.
    - Daha sonra yapılandırın: `openclaw configure --section web`.
  </Step>
  <Step title="Daemon kurulumu">
    - macOS: LaunchAgent
      - Oturum açılmış bir kullanıcı oturumu gerektirir; başsız kullanım için özel bir LaunchDaemon gerekir (paketlenmez).
    - Linux (ve Windows üzerinden WSL2): systemd kullanıcı birimi
      - İlk kurulum, çıkış yaptıktan sonra da Gateway çalışmaya devam etsin diye `loginctl enable-linger <user>` komutunu etkinleştirmeyi dener.
      - Sudo isteyebilir (`/var/lib/systemd/linger` yazar); önce sudo olmadan dener.
    - **Çalışma zamanı seçimi:** Node (önerilir; WhatsApp/Telegram için gereklidir). Bun **önerilmez**.
    - Token kimlik doğrulaması bir token gerektiriyorsa ve `gateway.auth.token` SecretRef ile yönetiliyorsa, daemon kurulumu bunu doğrular ancak çözümlenen düz metin token değerlerini supervisor hizmet ortamı meta verisine kalıcı olarak yazmaz.
    - Token kimlik doğrulaması bir token gerektiriyorsa ve yapılandırılmış token SecretRef çözümlenmemişse, daemon kurulumu eyleme geçirilebilir yönlendirme ile engellenir.
    - Hem `gateway.auth.token` hem de `gateway.auth.password` yapılandırılmışsa ve `gateway.auth.mode` ayarlanmamışsa, mod açıkça ayarlanana kadar daemon kurulumu engellenir.
  </Step>
  <Step title="Sağlık denetimi">
    - Gateway'i başlatır (gerekirse) ve `openclaw health` çalıştırır.
    - İpucu: `openclaw status --deep`, desteklendiğinde kanal yoklamaları da dahil olmak üzere canlı Gateway sağlık yoklamasını durum çıktısına ekler (erişilebilir bir Gateway gerektirir).
  </Step>
  <Step title="Skills (önerilir)">
    - Kullanılabilir Skills öğelerini okur ve gereksinimleri denetler.
    - Bir Node yöneticisi seçmenize olanak tanır: **npm / pnpm** (bun önerilmez).
    - İsteğe bağlı bağımlılıkları kurar (bazıları macOS'ta Homebrew kullanır).
  </Step>
  <Step title="Bitir">
    - Ek özellikler için iOS/Android/macOS uygulamaları da dahil olmak üzere özet + sonraki adımlar.
  </Step>
</Steps>

<Note>
GUI algılanmazsa, ilk kurulum tarayıcı açmak yerine Control UI için SSH port yönlendirme talimatlarını yazdırır.
Control UI varlıkları eksikse, ilk kurulum bunları oluşturmayı dener; geri dönüş komutu `pnpm ui:build` olur (UI bağımlılıklarını otomatik kurar).
</Note>

## Etkileşimsiz mod

İlk kurulumu otomatikleştirmek veya betik haline getirmek için `--non-interactive` kullanın:

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

Etkileşimsiz modda Gateway token SecretRef:

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

Sağlayıcıya özgü komut örnekleri [CLI Automation](/tr/start/wizard-cli-automation#provider-specific-examples) içinde bulunur.
Bayrak anlamları ve adım sıralaması için bu başvuru sayfasını kullanın.

### Ajan ekle (etkileşimsiz)

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.4 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

## Gateway sihirbazı RPC

Gateway, ilk kurulum akışını RPC üzerinden sunar (`wizard.start`, `wizard.next`, `wizard.cancel`, `wizard.status`).
İstemciler (macOS uygulaması, Control UI), ilk kurulum mantığını yeniden uygulamadan adımları işleyebilir.

## Signal kurulumu (signal-cli)

İlk kurulum, `signal-cli` aracını GitHub sürümlerinden kurabilir:

- Uygun sürüm varlığını indirir.
- Bunu `~/.openclaw/tools/signal-cli/<version>/` altına kaydeder.
- `channels.signal.cliPath` alanını yapılandırmanıza yazar.

Notlar:

- JVM yapıları **Java 21** gerektirir.
- Mümkün olduğunda yerel yapılar kullanılır.
- Windows WSL2 kullanır; signal-cli kurulumu WSL içindeki Linux akışını izler.

## Sihirbazın yazdığı şeyler

`~/.openclaw/openclaw.json` içindeki tipik alanlar:

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers` (MiniMax seçildiyse)
- `tools.profile` (yerel ilk kurulum, ayarlanmamışsa varsayılan olarak `"coding"` kullanır; mevcut açık değerler korunur)
- `gateway.*` (mod, bind, auth, tailscale)
- `session.dmScope` (davranış ayrıntıları: [CLI Setup Reference](/tr/start/wizard-cli-reference#outputs-and-internals))
- `channels.telegram.botToken`, `channels.discord.token`, `channels.matrix.*`, `channels.signal.*`, `channels.imessage.*`
- İstemler sırasında seçerek etkinleştirdiğinizde kanal izin listeleri (Slack/Discord/Matrix/Microsoft Teams) (adlar mümkün olduğunda kimliklere çözülür).
- `skills.install.nodeManager`
  - `setup --node-manager`, `npm`, `pnpm` veya `bun` kabul eder.
  - Elle yapılandırma, `skills.install.nodeManager` alanını doğrudan ayarlayarak hâlâ `yarn` kullanabilir.
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add`, `agents.list[]` ve isteğe bağlı `bindings` yazar.

WhatsApp kimlik bilgileri `~/.openclaw/credentials/whatsapp/<accountId>/` altında bulunur.
Oturumlar `~/.openclaw/agents/<agentId>/sessions/` altında saklanır.

Bazı kanallar Plugin olarak sunulur. Kurulum sırasında bunlardan birini seçtiğinizde, yapılandırılabilmeden önce ilk kurulum onu yüklemenizi ister (npm veya yerel bir yol ile).

## İlgili belgeler

- İlk kurulum genel bakışı: [Onboarding (CLI)](/tr/start/wizard)
- macOS uygulamasıyla ilk kurulum: [Onboarding](/tr/start/onboarding)
- Yapılandırma başvurusu: [Gateway configuration](/tr/gateway/configuration)
- Sağlayıcılar: [WhatsApp](/tr/channels/whatsapp), [Telegram](/tr/channels/telegram), [Discord](/tr/channels/discord), [Google Chat](/tr/channels/googlechat), [Signal](/tr/channels/signal), [BlueBubbles](/tr/channels/bluebubbles) (iMessage), [iMessage](/tr/channels/imessage) (eski)
- Skills: [Skills](/tr/tools/skills), [Skills config](/tr/tools/skills-config)
