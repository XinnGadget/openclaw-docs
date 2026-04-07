---
read_when:
    - CLI onboarding'ı çalıştırma veya yapılandırma
    - Yeni bir makine kurma
sidebarTitle: 'Onboarding: CLI'
summary: 'CLI onboarding: gateway, çalışma alanı, kanallar ve Skills için rehberli kurulum'
title: Onboarding (CLI)
x-i18n:
    generated_at: "2026-04-07T08:50:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6773b07afa8babf1b5ac94d857063d08094a962ee21ec96ca966e99ad57d107d
    source_path: start/wizard.md
    workflow: 15
---

# Onboarding (CLI)

CLI onboarding, OpenClaw'ı macOS,
Linux veya Windows'ta (WSL2 üzerinden; güçlü şekilde önerilir) kurmanın **önerilen** yoludur.
Tek bir rehberli akışta yerel bir Gateway veya uzak bir Gateway bağlantısını, ayrıca kanalları, Skills'i
ve çalışma alanı varsayılanlarını yapılandırır.

```bash
openclaw onboard
```

<Info>
En hızlı ilk sohbet: Control UI'ı açın (kanal kurulumu gerekmez). Şunu çalıştırın:
`openclaw dashboard` ve tarayıcıda sohbet edin. Belgeler: [Dashboard](/web/dashboard).
</Info>

Daha sonra yeniden yapılandırmak için:

```bash
openclaw configure
openclaw agents add <name>
```

<Note>
`--json`, etkileşimsiz mod anlamına gelmez. Betikler için `--non-interactive` kullanın.
</Note>

<Tip>
CLI onboarding, Brave, DuckDuckGo, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search,
Ollama Web Search, Perplexity, SearXNG veya Tavily gibi bir provider
seçebileceğiniz bir web search adımı içerir. Bazı provider'lar bir
API anahtarı gerektirirken bazıları anahtarsızdır. Bunu daha sonra
`openclaw configure --section web` ile de yapılandırabilirsiniz. Belgeler: [Web tools](/tr/tools/web).
</Tip>

## QuickStart ve Advanced

Onboarding, **QuickStart** (varsayılanlar) ile **Advanced** (tam denetim) arasında seçimle başlar.

<Tabs>
  <Tab title="QuickStart (varsayılanlar)">
    - Yerel gateway (loopback)
    - Çalışma alanı varsayılanı (veya mevcut çalışma alanı)
    - Gateway portu **18789**
    - Gateway kimlik doğrulaması **Token** (loopback üzerinde bile otomatik oluşturulur)
    - Yeni yerel kurulumlar için varsayılan tool policy: `tools.profile: "coding"` (mevcut açık profil korunur)
    - Varsayılan DM izolasyonu: yerel onboarding, ayarlanmamışsa `session.dmScope: "per-channel-peer"` yazar. Ayrıntılar: [CLI Setup Reference](/tr/start/wizard-cli-reference#outputs-and-internals)
    - Tailscale erişimi **Kapalı**
    - Telegram + WhatsApp DM'leri varsayılan olarak **allowlist** kullanır (telefon numaranız istenir)
  </Tab>
  <Tab title="Advanced (tam denetim)">
    - Her adımı açığa çıkarır (mod, çalışma alanı, gateway, kanallar, daemon, Skills).
  </Tab>
</Tabs>

## Onboarding neyi yapılandırır

**Yerel mod (varsayılan)** sizi şu adımlardan geçirir:

1. **Model/Kimlik Doğrulama** — desteklenen herhangi bir provider/kimlik doğrulama akışını seçin (API anahtarı, OAuth veya provider'a özgü manuel kimlik doğrulama), buna Custom Provider
   (OpenAI-compatible, Anthropic-compatible veya Unknown auto-detect) dahildir. Varsayılan bir model seçin.
   Güvenlik notu: bu ajan tool çalıştıracaksa veya webhook/hooks içeriğini işleyecekse, mevcut en güçlü yeni nesil modeli tercih edin ve tool politikasını katı tutun. Daha zayıf/eski katmanlara prompt injection daha kolay uygulanır.
   Etkileşimsiz çalıştırmalarda `--secret-input-mode ref`, düz metin API anahtarı değerleri yerine env destekli ref'leri auth profillerinde saklar.
   Etkileşimsiz `ref` modunda provider env değişkeni ayarlanmış olmalıdır; bu env değişkeni olmadan satır içi anahtar bayrakları vermek hızlı şekilde başarısız olur.
   Etkileşimli çalıştırmalarda secret reference modunu seçmek, kaydetmeden önce hızlı bir ön kontrol doğrulamasıyla ya bir ortam değişkenine ya da yapılandırılmış bir provider ref'ine (`file` veya `exec`) işaret etmenizi sağlar.
   Anthropic için, etkileşimli onboarding/configure **Anthropic Claude CLI** seçeneğini tercih edilen yerel yol ve **Anthropic API key** seçeneğini önerilen üretim yolu olarak sunar. Anthropic setup-token seçeneği de desteklenen token-auth yolu olarak kullanılabilir olmaya devam eder.
2. **Çalışma Alanı** — Ajan dosyalarının konumu (varsayılan `~/.openclaw/workspace`). Bootstrap dosyalarını tohumlar.
3. **Gateway** — Port, bind adresi, kimlik doğrulama modu, Tailscale erişimi.
   Etkileşimli token modunda varsayılan düz metin token depolamayı seçin veya SecretRef kullanımını tercih edin.
   Etkileşimsiz token SecretRef yolu: `--gateway-token-ref-env <ENV_VAR>`.
4. **Kanallar** — BlueBubbles, Discord, Feishu, Google Chat, Mattermost, Microsoft Teams, QQ Bot, Signal, Slack, Telegram, WhatsApp ve daha fazlası gibi yerleşik ve paketlenmiş sohbet kanalları.
5. **Daemon** — LaunchAgent (macOS), systemd user unit (Linux/WSL2) veya yerel Windows Scheduled Task kurar; kullanıcı başına Startup-folder geri dönüşü içerir.
   Token kimlik doğrulaması token gerektiriyorsa ve `gateway.auth.token` SecretRef tarafından yönetiliyorsa, daemon kurulumu bunu doğrular ancak çözümlenen token'ı supervisor servis ortam meta verilerine kalıcı olarak yazmaz.
   Token kimlik doğrulaması token gerektiriyorsa ve yapılandırılmış token SecretRef çözümlenmemişse, daemon kurulumu eyleme geçirilebilir yönlendirmeyle engellenir.
   Hem `gateway.auth.token` hem de `gateway.auth.password` yapılandırılmış ve `gateway.auth.mode` ayarlanmamışsa, mod açıkça ayarlanana kadar daemon kurulumu engellenir.
6. **Sağlık denetimi** — Gateway'i başlatır ve çalıştığını doğrular.
7. **Skills** — Önerilen Skills'i ve isteğe bağlı bağımlılıkları kurar.

<Note>
Onboarding'i yeniden çalıştırmak, açıkça **Reset** seçmediğiniz sürece (veya `--reset` vermediğiniz sürece) hiçbir şeyi silmez.
CLI `--reset` varsayılan olarak config, credentials ve sessions alanlarını kapsar; çalışma alanını da eklemek için `--reset-scope full` kullanın.
Config geçersizse veya eski anahtarlar içeriyorsa, onboarding önce `openclaw doctor` çalıştırmanızı ister.
</Note>

**Uzak mod**, yalnızca yerel istemciyi başka bir yerdeki bir Gateway'e bağlanacak şekilde yapılandırır.
Uzak host üzerinde hiçbir şeyi kurmaz veya değiştirmez.

## Başka bir ajan ekleme

Kendi çalışma alanı,
oturumları ve auth profilleri olan ayrı bir ajan oluşturmak için `openclaw agents add <name>` kullanın. `--workspace` olmadan çalıştırmak onboarding'i başlatır.

Ayarladıkları:

- `agents.list[].name`
- `agents.list[].workspace`
- `agents.list[].agentDir`

Notlar:

- Varsayılan çalışma alanları `~/.openclaw/workspace-<agentId>` düzenini izler.
- Gelen mesajları yönlendirmek için `bindings` ekleyin (onboarding bunu yapabilir).
- Etkileşimsiz bayraklar: `--model`, `--agent-dir`, `--bind`, `--non-interactive`.

## Tam başvuru

Ayrıntılı adım adım dökümler ve config çıktıları için
[CLI Setup Reference](/tr/start/wizard-cli-reference) bölümüne bakın.
Etkileşimsiz örnekler için [CLI Automation](/tr/start/wizard-cli-automation) bölümüne bakın.
RPC ayrıntıları da dahil daha derin teknik başvuru için
[Onboarding Reference](/tr/reference/wizard) bölümüne bakın.

## İlgili belgeler

- CLI komut başvurusu: [`openclaw onboard`](/cli/onboard)
- Onboarding genel bakışı: [Onboarding Overview](/tr/start/onboarding-overview)
- macOS uygulaması onboarding'i: [Onboarding](/tr/start/onboarding)
- Ajan ilk çalıştırma ritüeli: [Agent Bootstrapping](/tr/start/bootstrapping)
