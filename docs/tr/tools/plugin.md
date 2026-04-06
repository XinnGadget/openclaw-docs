---
read_when:
    - Plugin kuruyor veya yapılandırıyorsunuz
    - Plugin keşfi ve yükleme kurallarını anlamak istiyorsunuz
    - Codex/Claude uyumlu plugin paketleriyle çalışıyorsunuz
sidebarTitle: Install and Configure
summary: OpenClaw plugin'lerini kurun, yapılandırın ve yönetin
title: Plugin'ler
x-i18n:
    generated_at: "2026-04-06T03:14:16Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9e2472a3023f3c1c6ee05b0cdc228f6b713cc226a08695b327de8a3ad6973c83
    source_path: tools/plugin.md
    workflow: 15
---

# Plugin'ler

Plugin'ler, OpenClaw'ı yeni yeteneklerle genişletir: kanallar, model sağlayıcıları,
araçlar, Skills, konuşma, gerçek zamanlı transkripsiyon, gerçek zamanlı ses,
medya anlama, görsel oluşturma, video oluşturma, web getirme, web
arama ve daha fazlası. Bazı plugin'ler **çekirdektir** (OpenClaw ile birlikte gelir), diğerleri ise
**haricidir** (topluluk tarafından npm'de yayımlanır).

## Hızlı başlangıç

<Steps>
  <Step title="Nelerin yüklü olduğunu görün">
    ```bash
    openclaw plugins list
    ```
  </Step>

  <Step title="Bir plugin kurun">
    ```bash
    # npm'den
    openclaw plugins install @openclaw/voice-call

    # Yerel dizin veya arşivden
    openclaw plugins install ./my-plugin
    openclaw plugins install ./my-plugin.tgz
    ```

  </Step>

  <Step title="Gateway'i yeniden başlatın">
    ```bash
    openclaw gateway restart
    ```

    Ardından yapılandırma dosyanızda `plugins.entries.\<id\>.config` altında yapılandırın.

  </Step>
</Steps>

Sohbete özgü denetimi tercih ediyorsanız `commands.plugins: true` etkinleştirin ve şunları kullanın:

```text
/plugin install clawhub:@openclaw/voice-call
/plugin show voice-call
/plugin enable voice-call
```

Kurulum yolu, CLI ile aynı çözümleyiciyi kullanır: yerel yol/arşiv, açık
`clawhub:<pkg>` veya çıplak paket tanımı (önce ClawHub, sonra npm geri dönüşü).

Yapılandırma geçersizse, kurulum normalde kapalı şekilde başarısız olur ve sizi
`openclaw doctor --fix` komutuna yönlendirir. Tek kurtarma istisnası, şu özelliğe katılan plugin'ler için
dar bir paketlenmiş-plugin yeniden kurulum yoludur:
`openclaw.install.allowInvalidConfigRecovery`.

## Plugin türleri

OpenClaw iki plugin biçimini tanır:

| Biçim      | Nasıl çalışır                                                    | Örnekler                                               |
| ---------- | ---------------------------------------------------------------- | ------------------------------------------------------ |
| **Native** | `openclaw.plugin.json` + çalışma zamanı modülü; süreç içinde çalışır | Resmî plugin'ler, topluluk npm paketleri               |
| **Bundle** | Codex/Claude/Cursor uyumlu düzen; OpenClaw özelliklerine eşlenir | `.codex-plugin/`, `.claude-plugin/`, `.cursor-plugin/` |

Her ikisi de `openclaw plugins list` altında görünür. Paket ayrıntıları için bkz. [Plugin Paketleri](/tr/plugins/bundles).

Bir native plugin yazıyorsanız [Plugin Geliştirme](/tr/plugins/building-plugins)
ve [Plugin SDK Overview](/tr/plugins/sdk-overview) ile başlayın.

## Resmî plugin'ler

### Kurulabilir (npm)

| Plugin          | Paket                 | Belgeler                             |
| --------------- | --------------------- | ------------------------------------ |
| Matrix          | `@openclaw/matrix`    | [Matrix](/tr/channels/matrix)           |
| Microsoft Teams | `@openclaw/msteams`   | [Microsoft Teams](/tr/channels/msteams) |
| Nostr           | `@openclaw/nostr`     | [Nostr](/tr/channels/nostr)             |
| Voice Call      | `@openclaw/voice-call` | [Voice Call](/tr/plugins/voice-call)   |
| Zalo            | `@openclaw/zalo`      | [Zalo](/tr/channels/zalo)               |
| Zalo Personal   | `@openclaw/zalouser`  | [Zalo Personal](/tr/plugins/zalouser)   |

### Çekirdek (OpenClaw ile birlikte gelir)

<AccordionGroup>
  <Accordion title="Model sağlayıcıları (varsayılan olarak etkin)">
    `anthropic`, `byteplus`, `cloudflare-ai-gateway`, `github-copilot`, `google`,
    `huggingface`, `kilocode`, `kimi-coding`, `minimax`, `mistral`, `qwen`,
    `moonshot`, `nvidia`, `openai`, `opencode`, `opencode-go`, `openrouter`,
    `qianfan`, `synthetic`, `together`, `venice`,
    `vercel-ai-gateway`, `volcengine`, `xiaomi`, `zai`
  </Accordion>

  <Accordion title="Bellek plugin'leri">
    - `memory-core` — paketlenmiş bellek araması (varsayılan olarak `plugins.slots.memory` üzerinden)
    - `memory-lancedb` — otomatik geri çağırma/yakalama ile isteğe bağlı kurulan uzun vadeli bellek (`plugins.slots.memory = "memory-lancedb"` ayarlayın)
  </Accordion>

  <Accordion title="Konuşma sağlayıcıları (varsayılan olarak etkin)">
    `elevenlabs`, `microsoft`
  </Accordion>

  <Accordion title="Diğer">
    - `browser` — browser aracı, `openclaw browser` CLI, `browser.request` gateway yöntemi, browser çalışma zamanı ve varsayılan browser kontrol hizmeti için paketlenmiş browser plugin'i (varsayılan olarak etkin; değiştirmeden önce devre dışı bırakın)
    - `copilot-proxy` — VS Code Copilot Proxy köprüsü (varsayılan olarak devre dışı)
  </Accordion>
</AccordionGroup>

Üçüncü taraf plugin'ler mi arıyorsunuz? Bkz. [Topluluk Plugin'leri](/tr/plugins/community).

## Yapılandırma

```json5
{
  plugins: {
    enabled: true,
    allow: ["voice-call"],
    deny: ["untrusted-plugin"],
    load: { paths: ["~/Projects/oss/voice-call-extension"] },
    entries: {
      "voice-call": { enabled: true, config: { provider: "twilio" } },
    },
  },
}
```

| Alan            | Açıklama                                                  |
| ---------------- | --------------------------------------------------------- |
| `enabled`        | Ana anahtar (varsayılan: `true`)                          |
| `allow`          | Plugin allowlist'i (isteğe bağlı)                         |
| `deny`           | Plugin denylist'i (isteğe bağlı; deny önceliklidir)       |
| `load.paths`     | Ek plugin dosyaları/dizinleri                             |
| `slots`          | Özel slot seçicileri (örn. `memory`, `contextEngine`)     |
| `entries.\<id\>` | Plugin başına açma/kapama + yapılandırma                  |

Yapılandırma değişiklikleri **gateway yeniden başlatması gerektirir**. Gateway yapılandırma
izleme + süreç içi yeniden başlatma etkinken çalışıyorsa (varsayılan `openclaw gateway` yolu), bu
yeniden başlatma genellikle yapılandırma yazımı tamamlandıktan kısa süre sonra otomatik yapılır.

<Accordion title="Plugin durumları: disabled, missing ve invalid">
  - **Disabled**: plugin vardır ancak etkinleştirme kuralları onu kapatmıştır. Yapılandırma korunur.
  - **Missing**: yapılandırma, keşfin bulamadığı bir plugin kimliğine başvurur.
  - **Invalid**: plugin vardır ancak yapılandırması bildirilen şemayla eşleşmez.
</Accordion>

## Keşif ve öncelik

OpenClaw, plugin'leri şu sırayla tarar (ilk eşleşme kazanır):

<Steps>
  <Step title="Yapılandırma yolları">
    `plugins.load.paths` — açık dosya veya dizin yolları.
  </Step>

  <Step title="Çalışma alanı uzantıları">
    `\<workspace\>/.openclaw/<plugin-root>/*.ts` ve `\<workspace\>/.openclaw/<plugin-root>/*/index.ts`.
  </Step>

  <Step title="Global uzantılar">
    `~/.openclaw/<plugin-root>/*.ts` ve `~/.openclaw/<plugin-root>/*/index.ts`.
  </Step>

  <Step title="Paketlenmiş plugin'ler">
    OpenClaw ile birlikte gelir. Birçoğu varsayılan olarak etkindir (model sağlayıcıları, konuşma gibi).
    Diğerleri açık etkinleştirme gerektirir.
  </Step>
</Steps>

### Etkinleştirme kuralları

- `plugins.enabled: false` tüm plugin'leri devre dışı bırakır
- `plugins.deny`, her zaman allow'u kazanır
- `plugins.entries.\<id\>.enabled: false` o plugin'i devre dışı bırakır
- Çalışma alanı kaynaklı plugin'ler **varsayılan olarak devre dışıdır** (açıkça etkinleştirilmelidir)
- Paketlenmiş plugin'ler, üzerine yazılmadıkça yerleşik varsayılan açık kümesini izler
- Özel slot'lar, o slot için seçilen plugin'i zorla etkinleştirebilir

## Plugin slot'ları (özel kategoriler)

Bazı kategoriler özeldir (aynı anda yalnızca biri etkin olabilir):

```json5
{
  plugins: {
    slots: {
      memory: "memory-core", // veya devre dışı bırakmak için "none"
      contextEngine: "legacy", // veya bir plugin kimliği
    },
  },
}
```

| Slot            | Neyi denetler          | Varsayılan          |
| --------------- | ---------------------- | ------------------- |
| `memory`        | Etkin bellek plugin'i  | `memory-core`       |
| `contextEngine` | Etkin bağlam motoru    | `legacy` (yerleşik) |

## CLI başvurusu

```bash
openclaw plugins list                       # kompakt envanter
openclaw plugins list --enabled            # yalnızca yüklü plugin'ler
openclaw plugins list --verbose            # plugin başına ayrıntı satırları
openclaw plugins list --json               # makine tarafından okunabilir envanter
openclaw plugins inspect <id>              # derin ayrıntı
openclaw plugins inspect <id> --json       # makine tarafından okunabilir
openclaw plugins inspect --all             # filo genelinde tablo
openclaw plugins info <id>                 # inspect takma adı
openclaw plugins doctor                    # tanılama

openclaw plugins install <package>         # kurulum (önce ClawHub, sonra npm)
openclaw plugins install clawhub:<pkg>     # yalnızca ClawHub'dan kurulum
openclaw plugins install <spec> --force    # mevcut kurulumu üzerine yaz
openclaw plugins install <path>            # yerel yoldan kurulum
openclaw plugins install -l <path>         # geliştirme için bağla (kopyalama yok)
openclaw plugins install <plugin> --marketplace <source>
openclaw plugins install <plugin> --marketplace https://github.com/<owner>/<repo>
openclaw plugins install <spec> --pin      # tam çözülmüş npm spec'i kaydet
openclaw plugins install <spec> --dangerously-force-unsafe-install
openclaw plugins update <id>             # tek plugin'i güncelle
openclaw plugins update <id> --dangerously-force-unsafe-install
openclaw plugins update --all            # tümünü güncelle
openclaw plugins uninstall <id>          # yapılandırma/kurulum kayıtlarını kaldır
openclaw plugins uninstall <id> --keep-files
openclaw plugins marketplace list <source>
openclaw plugins marketplace list <source> --json

openclaw plugins enable <id>
openclaw plugins disable <id>
```

Paketlenmiş plugin'ler OpenClaw ile birlikte gelir. Birçoğu varsayılan olarak etkindir (örneğin
paketlenmiş model sağlayıcıları, paketlenmiş konuşma sağlayıcıları ve paketlenmiş browser
plugin'i). Diğer paketlenmiş plugin'ler için yine de `openclaw plugins enable <id>` gerekir.

`--force`, mevcut kurulu bir plugin veya hook paketinin üzerine yerinde yazar.
Kaynak yolu yönetilen kurulum hedefine kopyalamak yerine yeniden kullanan
`--link` ile desteklenmez.

`--pin` yalnızca npm içindir. `--marketplace` ile desteklenmez, çünkü
marketplace kurulumları npm spec'i yerine marketplace kaynak meta verisini kalıcı yazar.

`--dangerously-force-unsafe-install`, yerleşik tehlikeli kod tarayıcısının
yanlış pozitifleri için acil durum geçersiz kılma seçeneğidir. Plugin kurulumu
ve plugin güncellemelerinin yerleşik `critical` bulgularını aşarak devam etmesine izin verir, ancak yine de
plugin `before_install` ilke engellemelerini veya tarama başarısızlığı engellemesini aşmaz.

Bu CLI bayrağı yalnızca plugin kurulum/güncelleme akışlarına uygulanır. Gateway destekli skill
bağımlılık kurulumları bunun yerine eşleşen `dangerouslyForceUnsafeInstall` istek geçersiz kılmasını kullanır; `openclaw skills install` ise ayrı ClawHub
skill indirme/kurma akışı olarak kalır.

Uyumlu paketler aynı plugin listeleme/inceleme/etkinleştirme/devre dışı bırakma
akışına katılır. Mevcut çalışma zamanı desteği paket skill'leri, Claude command-skills,
Claude `settings.json` varsayılanları, Claude `.lsp.json` ve manifest bildirilen
`lspServers` varsayılanları, Cursor command-skills ve uyumlu Codex hook
dizinlerini içerir.

`openclaw plugins inspect <id>`, ayrıca paket tarafından desteklenen plugin'ler için
algılanan paket yeteneklerini ve desteklenen veya desteklenmeyen MCP ve LSP sunucusu girdilerini de bildirir.

Marketplace kaynakları,
`~/.claude/plugins/known_marketplaces.json` içinden Claude bilinen-marketplace adı,
yerel marketplace kökü veya `marketplace.json` yolu, `owner/repo` gibi GitHub kısaltması, GitHub depo
URL'si veya git URL'si olabilir. Uzak marketplace'ler için plugin girdileri klonlanan
marketplace deposu içinde kalmalı ve yalnızca göreli yol kaynaklarını kullanmalıdır.

Tam ayrıntılar için bkz. [`openclaw plugins` CLI başvurusu](/cli/plugins).

## Plugin API genel bakışı

Native plugin'ler, `register(api)` sunan bir giriş nesnesi dışa aktarır. Daha eski
plugin'ler kullanım dışı bir takma ad olarak hâlâ `activate(api)` kullanabilir, ancak yeni plugin'ler
`register` kullanmalıdır.

```typescript
export default definePluginEntry({
  id: "my-plugin",
  name: "My Plugin",
  register(api) {
    api.registerProvider({
      /* ... */
    });
    api.registerTool({
      /* ... */
    });
    api.registerChannel({
      /* ... */
    });
  },
});
```

OpenClaw giriş nesnesini yükler ve plugin
etkinleştirme sırasında `register(api)` çağırır. Yükleyici eski plugin'ler için hâlâ `activate(api)` geri dönüşünü kullanır,
ancak paketlenmiş plugin'ler ve yeni harici plugin'ler `register`'ı genel
sözleşme olarak ele almalıdır.

Yaygın kayıt yöntemleri:

| Yöntem                                  | Ne kaydeder                |
| --------------------------------------- | -------------------------- |
| `registerProvider`                      | Model sağlayıcısı (LLM)    |
| `registerChannel`                       | Sohbet kanalı              |
| `registerTool`                          | Agent aracı                |
| `registerHook` / `on(...)`              | Yaşam döngüsü hook'ları    |
| `registerSpeechProvider`                | Metinden konuşmaya / STT   |
| `registerRealtimeTranscriptionProvider` | Akan STT                   |
| `registerRealtimeVoiceProvider`         | Çift yönlü gerçek zamanlı ses |
| `registerMediaUnderstandingProvider`    | Görsel/ses analizi         |
| `registerImageGenerationProvider`       | Görsel oluşturma           |
| `registerMusicGenerationProvider`       | Müzik oluşturma            |
| `registerVideoGenerationProvider`       | Video oluşturma            |
| `registerWebFetchProvider`              | Web getirme / scrape sağlayıcısı |
| `registerWebSearchProvider`             | Web arama                  |
| `registerHttpRoute`                     | HTTP uç noktası            |
| `registerCommand` / `registerCli`       | CLI komutları              |
| `registerContextEngine`                 | Bağlam motoru              |
| `registerService`                       | Arka plan hizmeti          |

Türlendirilmiş yaşam döngüsü hook'ları için hook guard davranışı:

- `before_tool_call`: `{ block: true }` terminaldir; daha düşük öncelikli işleyiciler atlanır.
- `before_tool_call`: `{ block: false }` etkisizdir ve daha önceki bir engeli temizlemez.
- `before_install`: `{ block: true }` terminaldir; daha düşük öncelikli işleyiciler atlanır.
- `before_install`: `{ block: false }` etkisizdir ve daha önceki bir engeli temizlemez.
- `message_sending`: `{ cancel: true }` terminaldir; daha düşük öncelikli işleyiciler atlanır.
- `message_sending`: `{ cancel: false }` etkisizdir ve daha önceki bir iptali temizlemez.

Tam türlendirilmiş hook davranışı için bkz. [SDK Overview](/tr/plugins/sdk-overview#hook-decision-semantics).

## İlgili

- [Plugin Geliştirme](/tr/plugins/building-plugins) — kendi plugin'inizi oluşturun
- [Plugin Paketleri](/tr/plugins/bundles) — Codex/Claude/Cursor paket uyumluluğu
- [Plugin Manifest](/tr/plugins/manifest) — manifest şeması
- [Araç Kaydetme](/tr/plugins/building-plugins#registering-agent-tools) — bir plugin içinde agent araçları ekleyin
- [Plugin İç Yapısı](/tr/plugins/architecture) — yetenek modeli ve yükleme ardışık düzeni
- [Topluluk Plugin'leri](/tr/plugins/community) — üçüncü taraf listeleri
