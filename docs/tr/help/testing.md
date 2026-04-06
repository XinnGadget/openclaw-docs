---
read_when:
    - Testleri yerelde veya CI içinde çalıştırıyorsunuz
    - Model/sağlayıcı hataları için regresyonlar ekliyorsunuz
    - Gateway + agent davranışında hata ayıklıyorsunuz
summary: 'Test kiti: unit/e2e/live paketleri, Docker çalıştırıcıları ve her testin neyi kapsadığı'
title: Testler
x-i18n:
    generated_at: "2026-04-06T03:09:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: cfa174e565df5fdf957234b7909beaf1304aa026e731cc2c433ca7d931681b56
    source_path: help/testing.md
    workflow: 15
---

# Testler

OpenClaw’un üç Vitest paketi vardır (unit/integration, e2e, live) ve küçük bir Docker çalıştırıcı kümesi bulunur.

Bu belge bir “nasıl test ediyoruz” kılavuzudur:

- Her paketin neyi kapsadığı (ve bilerek neyi kapsamadığı)
- Yaygın iş akışları için hangi komutların çalıştırılacağı (yerel, push öncesi, hata ayıklama)
- Live testlerin kimlik bilgilerini nasıl bulduğu ve modelleri/sağlayıcıları nasıl seçtiği
- Gerçek dünyadaki model/sağlayıcı sorunları için nasıl regresyon ekleneceği

## Hızlı başlangıç

Çoğu gün:

- Tam kapı (push öncesinde beklenen): `pnpm build && pnpm check && pnpm test`
- Geniş kaynaklı bir makinede daha hızlı yerel tam paket çalıştırması: `pnpm test:max`
- Doğrudan Vitest watch döngüsü (modern projects config): `pnpm test:watch`
- Doğrudan dosya hedefleme artık extension/channel yollarını da yönlendirir: `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`

Testlere dokunduğunuzda veya daha fazla güven istediğinizde:

- Kapsam kapısı: `pnpm test:coverage`
- E2E paketi: `pnpm test:e2e`

Gerçek sağlayıcılar/modeller üzerinde hata ayıklarken (gerçek kimlik bilgileri gerekir):

- Live paketi (modeller + gateway araç/görsel yoklamaları): `pnpm test:live`
- Tek bir live dosyasını sessizce hedefleyin: `pnpm test:live -- src/agents/models.profiles.live.test.ts`

İpucu: yalnızca tek bir başarısız duruma ihtiyacınız olduğunda, live testleri aşağıda açıklanan allowlist ortam değişkenleriyle daraltmayı tercih edin.

## Test paketleri (nerede ne çalışır)

Paketleri “artan gerçekçilik” (ve artan kararsızlık/maliyet) olarak düşünün:

### Unit / integration (varsayılan)

- Komut: `pnpm test`
- Yapılandırma: `vitest.config.ts` üzerinden yerel Vitest `projects`
- Dosyalar: `src/**/*.test.ts`, `packages/**/*.test.ts`, `test/**/*.test.ts` altındaki çekirdek/unit envanterleri ve `vitest.unit.config.ts` kapsamındaki izin verilmiş `ui` node testleri
- Kapsam:
  - Saf unit testleri
  - Süreç içi integration testleri (gateway auth, routing, tooling, parsing, config)
  - Bilinen hatalar için deterministik regresyonlar
- Beklentiler:
  - CI içinde çalışır
  - Gerçek anahtar gerekmez
  - Hızlı ve kararlı olmalıdır
- Projects notu:
  - `pnpm test`, `pnpm test:watch` ve `pnpm test:changed` artık aynı yerel Vitest kök `projects` config’ini kullanır.
  - Doğrudan dosya filtreleri kök proje grafiği üzerinden yerel olarak yönlendirilir; bu yüzden `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts` özel bir wrapper olmadan çalışır.
- Embedded runner notu:
  - Mesaj-araç keşfi girdilerini veya compaction çalışma zamanı bağlamını değiştirdiğinizde, her iki kapsama düzeyini de koruyun.
  - Saf routing/normalization sınırları için odaklı helper regresyonları ekleyin.
  - Ayrıca embedded runner integration paketlerini de sağlıklı tutun:
    `src/agents/pi-embedded-runner/compact.hooks.test.ts`,
    `src/agents/pi-embedded-runner/run.overflow-compaction.test.ts` ve
    `src/agents/pi-embedded-runner/run.overflow-compaction.loop.test.ts`.
  - Bu paketler, kapsamlı kimliklerin ve compaction davranışının gerçek `run.ts` / `compact.ts` yolları üzerinden akmaya devam ettiğini doğrular; yalnızca helper testleri bu integration yollarının yeterli bir yerine geçmez.
- Pool notu:
  - Temel Vitest config artık varsayılan olarak `threads` kullanır.
  - Paylaşılan Vitest config ayrıca `isolate: false` sabitler ve kök projects, e2e ve live config’lerde izole edilmemiş runner’ı kullanır.
  - Kök UI şeridi `jsdom` kurulumunu ve optimizer’ını korur, ancak artık paylaşılan izole edilmemiş runner üzerinde çalışır.
  - `pnpm test`, kök `vitest.config.ts` projects config’inden aynı `threads` + `isolate: false` varsayılanlarını devralır.
  - Paylaşılan `scripts/run-vitest.mjs` başlatıcısı, büyük yerel çalıştırmalarda V8 derleme churn’ünü azaltmak için artık Vitest alt Node süreçlerine varsayılan olarak `--no-maglev` de ekler. Stok V8 davranışıyla karşılaştırmanız gerekiyorsa `OPENCLAW_VITEST_ENABLE_MAGLEV=1` ayarlayın.
- Hızlı yerel yineleme notu:
  - `pnpm test:changed`, yerel projects config’ini `--changed origin/main` ile çalıştırır.
  - `pnpm test:max` ve `pnpm test:changed:max`, aynı yerel projects config’ini korur; yalnızca daha yüksek worker sınırıyla.
  - Yerel worker otomatik ölçekleme artık bilinçli olarak daha muhafazakârdır ve host load average zaten yüksekse geri çekilir; böylece eşzamanlı birden fazla Vitest çalıştırması varsayılan olarak daha az zarar verir.
  - Temel Vitest config, test wiring değiştiğinde changed-mode yeniden çalıştırmaların doğru kalması için projects/config dosyalarını `forceRerunTriggers` olarak işaretler.
  - Config, desteklenen host’larda `OPENCLAW_VITEST_FS_MODULE_CACHE` değerini etkin tutar; doğrudan profiling için tek bir açık önbellek konumu istiyorsanız `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/abs/path` ayarlayın.
- Perf-debug notu:
  - `pnpm test:perf:imports`, Vitest import-duration raporlamasını ve import-breakdown çıktısını etkinleştirir.
  - `pnpm test:perf:imports:changed`, aynı profiling görünümünü `origin/main` sonrası değişen dosyalarla sınırlar.
  - `pnpm test:perf:profile:main`, Vitest/Vite başlangıcı ve transform ek yükü için bir main-thread CPU profili yazar.
  - `pnpm test:perf:profile:runner`, dosya paralelliği devre dışıyken unit paketi için runner CPU+heap profilleri yazar.

### E2E (gateway smoke)

- Komut: `pnpm test:e2e`
- Yapılandırma: `vitest.e2e.config.ts`
- Dosyalar: `src/**/*.e2e.test.ts`, `test/**/*.e2e.test.ts`
- Çalışma zamanı varsayılanları:
  - Deponun geri kalanıyla eşleşecek şekilde Vitest `threads` ve `isolate: false` kullanır.
  - Uyarlanabilir worker’lar kullanır (CI: en fazla 2, yerel: varsayılan olarak 1).
  - Konsol G/Ç ek yükünü azaltmak için varsayılan olarak sessiz kipte çalışır.
- Yararlı geçersiz kılmalar:
  - Worker sayısını zorlamak için `OPENCLAW_E2E_WORKERS=<n>` (üst sınır 16).
  - Ayrıntılı konsol çıktısını yeniden etkinleştirmek için `OPENCLAW_E2E_VERBOSE=1`.
- Kapsam:
  - Çok örnekli gateway uçtan uca davranışı
  - WebSocket/HTTP yüzeyleri, node eşleştirme ve daha ağır ağ oluşturma
- Beklentiler:
  - CI içinde çalışır (boru hattında etkinleştirildiğinde)
  - Gerçek anahtar gerekmez
  - Unit testlerinden daha fazla hareketli parça vardır (daha yavaş olabilir)

### E2E: OpenShell backend smoke

- Komut: `pnpm test:e2e:openshell`
- Dosya: `test/openshell-sandbox.e2e.test.ts`
- Kapsam:
  - Docker üzerinden host üzerinde izole bir OpenShell gateway başlatır
  - Geçici bir yerel Dockerfile’dan sandbox oluşturur
  - OpenClaw’un OpenShell backend’ini gerçek `sandbox ssh-config` + SSH exec üzerinden dener
  - Uzak canonical dosya sistemi davranışını sandbox fs köprüsü üzerinden doğrular
- Beklentiler:
  - Yalnızca isteğe bağlıdır; varsayılan `pnpm test:e2e` çalıştırmasının parçası değildir
  - Yerel bir `openshell` CLI ve çalışan bir Docker daemon gerektirir
  - İzole `HOME` / `XDG_CONFIG_HOME` kullanır, ardından test gateway ve sandbox’ı yok eder
- Yararlı geçersiz kılmalar:
  - Daha geniş e2e paketini elle çalıştırırken testi etkinleştirmek için `OPENCLAW_E2E_OPENSHELL=1`
  - Varsayılan olmayan bir CLI ikilisine veya wrapper script’e işaret etmek için `OPENCLAW_E2E_OPENSHELL_COMMAND=/path/to/openshell`

### Live (gerçek sağlayıcılar + gerçek modeller)

- Komut: `pnpm test:live`
- Yapılandırma: `vitest.live.config.ts`
- Dosyalar: `src/**/*.live.test.ts`
- Varsayılan: `pnpm test:live` tarafından **etkinleştirilir** (`OPENCLAW_LIVE_TEST=1` ayarlar)
- Kapsam:
  - “Bu sağlayıcı/model bugün gerçek kimlik bilgileriyle gerçekten çalışıyor mu?”
  - Sağlayıcı biçim değişikliklerini, araç çağırma tuhaflıklarını, auth sorunlarını ve rate limit davranışını yakalar
- Beklentiler:
  - Tasarım gereği CI içinde kararlı değildir (gerçek ağlar, gerçek sağlayıcı ilkeleri, kotalar, kesintiler)
  - Para harcar / rate limit kullanır
  - “Her şeyi” değil, daraltılmış alt kümeleri çalıştırmak tercih edilir
- Live çalıştırmalar, eksik API anahtarlarını almak için `~/.profile` kaynağını kullanır.
- Varsayılan olarak live çalıştırmalar yine de `HOME` değerini izole eder ve config/auth materyalini geçici bir test ana dizinine kopyalar; böylece unit fixture’ları gerçek `~/.openclaw` dizininizi değiştiremez.
- Live testlerin gerçek home dizininizi kullanmasını yalnızca bilinçli olarak istediğinizde `OPENCLAW_LIVE_USE_REAL_HOME=1` ayarlayın.
- `pnpm test:live` artık varsayılan olarak daha sessiz bir kip kullanır: `[live] ...` ilerleme çıktısını korur, ancak ek `~/.profile` bildirimini bastırır ve gateway bootstrap log’larını/Bonjour trafiğini susturur. Tam başlangıç log’larını geri istiyorsanız `OPENCLAW_LIVE_TEST_QUIET=0` ayarlayın.
- API anahtarı rotasyonu (sağlayıcıya özgü): virgül/noktalı virgül biçiminde `*_API_KEYS` veya `*_API_KEY_1`, `*_API_KEY_2` ayarlayın (örneğin `OPENAI_API_KEYS`, `ANTHROPIC_API_KEYS`, `GEMINI_API_KEYS`) ya da live başına geçersiz kılma için `OPENCLAW_LIVE_*_KEY`; testler rate limit yanıtlarında yeniden dener.
- İlerleme/heartbeat çıktısı:
  - Live paketleri artık ilerleme satırlarını stderr’e yazar; böylece uzun sağlayıcı çağrıları, Vitest konsol yakalama sessiz olsa bile görünür şekilde etkin olur.
  - `vitest.live.config.ts`, sağlayıcı/gateway ilerleme satırlarının live çalıştırmalar sırasında hemen akması için Vitest konsol yakalamasını devre dışı bırakır.
  - Doğrudan model heartbeat’lerini `OPENCLAW_LIVE_HEARTBEAT_MS` ile ayarlayın.
  - Gateway/yoklama heartbeat’lerini `OPENCLAW_LIVE_GATEWAY_HEARTBEAT_MS` ile ayarlayın.

## Hangi paketi çalıştırmalıyım?

Şu karar tablosunu kullanın:

- Mantık/test düzenliyorsanız: `pnpm test` çalıştırın (ve çok şey değiştirdiyseniz `pnpm test:coverage`)
- Gateway ağ iletişimi / WS protokolü / eşleştirmeye dokunuyorsanız: `pnpm test:e2e` ekleyin
- “Botum çalışmıyor” / sağlayıcıya özgü hatalar / araç çağırma sorunlarında hata ayıklıyorsanız: daraltılmış bir `pnpm test:live` çalıştırın

## Live: Android node yetenek taraması

- Test: `src/gateway/android-node.capabilities.live.test.ts`
- Script: `pnpm android:test:integration`
- Amaç: bağlı bir Android node tarafından şu anda duyurulan **her komutu** çağırmak ve komut sözleşmesi davranışını doğrulamak.
- Kapsam:
  - Ön koşullu/elle kurulum (paket uygulamayı kurmaz/çalıştırmaz/eşleştirmez).
  - Seçilen Android node için komut bazında gateway `node.invoke` doğrulaması.
- Gerekli ön kurulum:
  - Android uygulaması zaten gateway’e bağlı ve eşleştirilmiş olmalı.
  - Uygulama ön planda tutulmalı.
  - Başarılı olmasını beklediğiniz yetenekler için izinler/yakalama onayı verilmiş olmalı.
- İsteğe bağlı hedef geçersiz kılmaları:
  - `OPENCLAW_ANDROID_NODE_ID` veya `OPENCLAW_ANDROID_NODE_NAME`.
  - `OPENCLAW_ANDROID_GATEWAY_URL` / `OPENCLAW_ANDROID_GATEWAY_TOKEN` / `OPENCLAW_ANDROID_GATEWAY_PASSWORD`.
- Tam Android kurulum ayrıntıları: [Android App](/tr/platforms/android)

## Live: model smoke (profil anahtarları)

Live testler, hataları izole edebilmek için iki katmana ayrılmıştır:

- “Doğrudan model”, sağlayıcı/modelin verilen anahtarla en azından yanıt verebildiğini söyler.
- “Gateway smoke”, tam gateway+agent boru hattının o model için çalıştığını söyler (oturumlar, geçmiş, araçlar, sandbox ilkesi vb.).

### Katman 1: Doğrudan model tamamlama (gateway yok)

- Test: `src/agents/models.profiles.live.test.ts`
- Amaç:
  - Keşfedilen modelleri listelemek
  - Kimlik bilgileriniz olan modelleri seçmek için `getApiKeyForModel` kullanmak
  - Model başına küçük bir tamamlama çalıştırmak (ve gerektiğinde hedefli regresyonlar)
- Nasıl etkinleştirilir:
  - `pnpm test:live` (veya Vitest doğrudan çağrılıyorsa `OPENCLAW_LIVE_TEST=1`)
- Bu paketin gerçekten çalışması için `OPENCLAW_LIVE_MODELS=modern` (veya `all`, modern için takma ad) ayarlayın; aksi halde `pnpm test:live` odağını gateway smoke üzerinde tutmak için atlanır
- Modeller nasıl seçilir:
  - Modern allowlist’i çalıştırmak için `OPENCLAW_LIVE_MODELS=modern` (Opus/Sonnet 4.6+, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.7, Grok 4)
  - `OPENCLAW_LIVE_MODELS=all`, modern allowlist için bir takma addır
  - veya `OPENCLAW_LIVE_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,..."` (virgülle allowlist)
- Sağlayıcılar nasıl seçilir:
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity"` (virgülle allowlist)
- Anahtarlar nereden gelir:
  - Varsayılan olarak: profil deposu ve ortam değişkeni geri dönüşleri
  - Yalnızca **profil deposunu** zorlamak için `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` ayarlayın
- Bunun var olma nedeni:
  - “Sağlayıcı API bozuk / anahtar geçersiz” ile “gateway agent boru hattı bozuk” durumlarını ayırır
  - Küçük, izole regresyonlar içerir (örnek: OpenAI Responses/Codex Responses reasoning replay + tool-call akışları)

### Katman 2: Gateway + dev agent smoke (`@openclaw` gerçekte ne yapıyor)

- Test: `src/gateway/gateway-models.profiles.live.test.ts`
- Amaç:
  - Süreç içi bir gateway başlatmak
  - `agent:dev:*` oturumu oluşturmak/düzeltmek (çalıştırma başına model geçersiz kılma)
  - Anahtarlı modeller arasında dönmek ve şunları doğrulamak:
    - “anlamlı” yanıt (araç yok)
    - gerçek bir araç çağrısının çalışması (read probe)
    - isteğe bağlı ek araç yoklamaları (exec+read probe)
    - OpenAI regresyon yollarının (yalnızca tool-call → takip) çalışmaya devam etmesi
- Yoklama ayrıntıları (hataları hızlı açıklayabilmeniz için):
  - `read` probe: test, çalışma alanına nonce içeren bir dosya yazar ve agent’tan bunu `read` ile okuyup nonce’ı geri yankılamasını ister.
  - `exec+read` probe: test, agent’tan nonce’ı geçici bir dosyaya `exec` ile yazmasını, sonra `read` ile geri okumasını ister.
  - image probe: test, oluşturulmuş bir PNG (kedi + rastgele kod) ekler ve modelin `cat <CODE>` döndürmesini bekler.
  - Uygulama referansı: `src/gateway/gateway-models.profiles.live.test.ts` ve `src/gateway/live-image-probe.ts`.
- Nasıl etkinleştirilir:
  - `pnpm test:live` (veya Vitest doğrudan çağrılıyorsa `OPENCLAW_LIVE_TEST=1`)
- Modeller nasıl seçilir:
  - Varsayılan: modern allowlist (Opus/Sonnet 4.6+, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.7, Grok 4)
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all`, modern allowlist için bir takma addır
  - Veya daraltmak için `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"` (veya virgüllü liste) ayarlayın
- Sağlayıcılar nasıl seçilir (“OpenRouter her şeyi”nden kaçınmak için):
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,openai,anthropic,zai,minimax"` (virgülle allowlist)
- Araç + görsel yoklamaları bu live testte her zaman açıktır:
  - `read` probe + `exec+read` probe (araç stres testi)
  - model görsel girdi desteği duyuruyorsa image probe çalışır
  - Akış (yüksek seviye):
    - Test, “CAT” + rastgele kod içeren küçük bir PNG üretir (`src/gateway/live-image-probe.ts`)
    - Bunu `agent` üzerinden `attachments: [{ mimeType: "image/png", content: "<base64>" }]` ile gönderir
    - Gateway ekleri `images[]` içine ayrıştırır (`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`)
    - Embedded agent, modele multimodal bir kullanıcı mesajı iletir
    - Doğrulama: yanıt `cat` + kodu içerir (OCR toleransı: küçük hatalara izin verilir)

İpucu: makinenizde neyi test edebileceğinizi (ve tam `provider/model` kimliklerini) görmek için şunu çalıştırın:

```bash
openclaw models list
openclaw models list --json
```

## Live: ACP bind smoke (`/acp spawn ... --bind here`)

- Test: `src/gateway/gateway-acp-bind.live.test.ts`
- Amaç: canlı bir ACP agent ile gerçek ACP konuşma-bind akışını doğrulamak:
  - `/acp spawn <agent> --bind here` gönder
  - sentetik bir message-channel konuşmasını yerinde bağla
  - aynı konuşmada normal bir takip mesajı gönder
  - takibin bağlı ACP oturum dökümüne ulaştığını doğrula
- Etkinleştirme:
  - `pnpm test:live src/gateway/gateway-acp-bind.live.test.ts`
  - `OPENCLAW_LIVE_ACP_BIND=1`
- Varsayılanlar:
  - ACP agent: `claude`
  - Sentetik kanal: Slack DM tarzı konuşma bağlamı
  - ACP backend: `acpx`
- Geçersiz kılmalar:
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=claude`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=codex`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND='npx -y @agentclientprotocol/claude-agent-acp@<version>'`
- Notlar:
  - Bu şerit, testlerin harici teslimat yapıyormuş gibi davranmadan message-channel bağlamı ekleyebilmesi için admin-only sentetik kaynak rota alanlarıyla gateway `chat.send` yüzeyini kullanır.
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND` ayarlanmamışsa test, seçilen ACP harness agent için embedded `acpx` plugin’inin yerleşik agent kayıt defterini kullanır.

Örnek:

```bash
OPENCLAW_LIVE_ACP_BIND=1 \
  OPENCLAW_LIVE_ACP_BIND_AGENT=claude \
  pnpm test:live src/gateway/gateway-acp-bind.live.test.ts
```

Docker tarifi:

```bash
pnpm test:docker:live-acp-bind
```

Docker notları:

- Docker çalıştırıcısı `scripts/test-live-acp-bind-docker.sh` içinde bulunur.
- `~/.profile` kaynağını alır, eşleşen CLI auth materyalini kapsayıcıya hazırlar, yazılabilir bir npm prefix içine `acpx` kurar, ardından eksikse istenen live CLI’yi (`@anthropic-ai/claude-code` veya `@openai/codex`) kurar.
- Docker içinde çalıştırıcı `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=$HOME/.npm-global/bin/acpx` ayarlar; böylece acpx, kaynak profilden gelen sağlayıcı ortam değişkenlerini alt harness CLI için kullanılabilir tutar.

### Önerilen live tarifleri

Dar, açık allowlist’ler en hızlı ve en az kararsız olanlardır:

- Tek model, doğrudan (gateway yok):
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.4" pnpm test:live src/agents/models.profiles.live.test.ts`

- Tek model, gateway smoke:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Birkaç sağlayıcıda araç çağırma:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Google odağı (Gemini API anahtarı + Antigravity):
  - Gemini (API anahtarı): `OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  - Antigravity (OAuth): `OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

Notlar:

- `google/...`, Gemini API’sini kullanır (API anahtarı).
- `google-antigravity/...`, Antigravity OAuth bridge’i kullanır (Cloud Code Assist tarzı agent endpoint’i).

## Live: model matrisi (neyi kapsıyoruz)

Sabit bir “CI model listesi” yoktur (live isteğe bağlıdır), ancak anahtarları olan bir geliştirme makinesinde düzenli olarak kapsanması **önerilen** modeller şunlardır.

### Modern smoke kümesi (araç çağırma + görsel)

Bu, çalışır durumda tutmayı beklediğimiz “yaygın modeller” çalıştırmasıdır:

- OpenAI (Codex dışı): `openai/gpt-5.4` (isteğe bağlı: `openai/gpt-5.4-mini`)
- OpenAI Codex: `openai-codex/gpt-5.4`
- Anthropic: `anthropic/claude-opus-4-6` (veya `anthropic/claude-sonnet-4-6`)
- Google (Gemini API): `google/gemini-3.1-pro-preview` ve `google/gemini-3-flash-preview` (eski Gemini 2.x modellerinden kaçının)
- Google (Antigravity): `google-antigravity/claude-opus-4-6-thinking` ve `google-antigravity/gemini-3-flash`
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

Araçlar + görsel ile gateway smoke çalıştırın:
`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,openai-codex/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3.1-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

### Temel seviye: araç çağırma (Read + isteğe bağlı Exec)

Her sağlayıcı ailesi için en az bir tane seçin:

- OpenAI: `openai/gpt-5.4` (veya `openai/gpt-5.4-mini`)
- Anthropic: `anthropic/claude-opus-4-6` (veya `anthropic/claude-sonnet-4-6`)
- Google: `google/gemini-3-flash-preview` (veya `google/gemini-3.1-pro-preview`)
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

İsteğe bağlı ek kapsam (olsa iyi olur):

- xAI: `xai/grok-4` (veya mevcut en son sürüm)
- Mistral: `mistral/`… (etkinleştirdiğiniz “tools” destekli bir model seçin)
- Cerebras: `cerebras/`… (erişiminiz varsa)
- LM Studio: `lmstudio/`… (yerel; araç çağırma API moduna bağlıdır)

### Vision: görsel gönderimi (ek → multimodal mesaj)

Image probe’u çalıştırmak için `OPENCLAW_LIVE_GATEWAY_MODELS` içine en az bir görsel destekli model ekleyin (Claude/Gemini/OpenAI vision-capable varyantları vb.).

### Toplayıcılar / alternatif gateway’ler

Anahtarlarınız etkinse şunlar üzerinden test de desteklenir:

- OpenRouter: `openrouter/...` (yüzlerce model; araç+görsel destekli adayları bulmak için `openclaw models scan` kullanın)
- OpenCode: Zen için `opencode/...`, Go için `opencode-go/...` (auth: `OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY`)

Live matrisine ekleyebileceğiniz daha fazla sağlayıcı (kimlik bilgileri/config varsa):

- Yerleşik: `openai`, `openai-codex`, `anthropic`, `google`, `google-vertex`, `google-antigravity`, `zai`, `openrouter`, `opencode`, `opencode-go`, `xai`, `groq`, `cerebras`, `mistral`, `github-copilot`
- `models.providers` üzerinden (özel endpoint’ler): `minimax` (cloud/API), ayrıca herhangi bir OpenAI/Anthropic uyumlu proxy (LM Studio, vLLM, LiteLLM vb.)

İpucu: belgelerde “tüm modelleri” sabit kodlamaya çalışmayın. Yetkili liste, makinenizde `discoverModels(...)` ne döndürüyorsa ve hangi anahtarlar mevcutsa odur.

## Kimlik bilgileri (asla commit etmeyin)

Live testler, kimlik bilgilerini CLI ile aynı şekilde bulur. Pratik sonuçlar:

- CLI çalışıyorsa, live testler de aynı anahtarları bulmalıdır.
- Bir live test “kimlik bilgisi yok” diyorsa, bunu `openclaw models list` / model seçimi hata ayıklamasında yaptığınız gibi hata ayıklayın.

- Agent başına auth profilleri: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` (live testlerde “profil anahtarları” denilen şey budur)
- Config: `~/.openclaw/openclaw.json` (veya `OPENCLAW_CONFIG_PATH`)
- Eski state dizini: `~/.openclaw/credentials/` (varsa hazırlanan live home içine kopyalanır, ancak ana profil-anahtar deposu değildir)
- Yerel live çalıştırmalar, varsayılan olarak etkin config’i, agent başına `auth-profiles.json` dosyalarını, eski `credentials/` dizinini ve desteklenen harici CLI auth dizinlerini geçici bir test home içine kopyalar; bu hazırlanan config içinde `agents.*.workspace` / `agentDir` yol geçersiz kılmaları kaldırılır, böylece yoklamalar gerçek host çalışma alanınıza gitmez.

Ortam değişkeni anahtarlarına güvenmek istiyorsanız (ör. `~/.profile` içinde dışa aktarılmışsa), yerel testleri `source ~/.profile` sonrasında çalıştırın veya aşağıdaki Docker çalıştırıcılarını kullanın (`~/.profile` dosyasını kapsayıcı içine mount edebilirler).

## Deepgram live (ses yazıya dökme)

- Test: `src/media-understanding/providers/deepgram/audio.live.test.ts`
- Etkinleştirme: `DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`

## BytePlus coding plan live

- Test: `src/agents/byteplus.live.test.ts`
- Etkinleştirme: `BYTEPLUS_API_KEY=... BYTEPLUS_LIVE_TEST=1 pnpm test:live src/agents/byteplus.live.test.ts`
- İsteğe bağlı model geçersiz kılma: `BYTEPLUS_CODING_MODEL=ark-code-latest`

## ComfyUI workflow media live

- Test: `extensions/comfy/comfy.live.test.ts`
- Etkinleştirme: `OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts`
- Kapsam:
  - Paketlenmiş comfy görsel, video ve `music_generate` yollarını dener
  - `models.providers.comfy.<capability>` yapılandırılmamışsa her yeteneği atlar
  - Comfy workflow gönderimi, polling, indirmeler veya plugin kaydı değiştirildikten sonra yararlıdır

## Görsel oluşturma live

- Test: `src/image-generation/runtime.live.test.ts`
- Komut: `pnpm test:live src/image-generation/runtime.live.test.ts`
- Kapsam:
  - Kayıtlı her görsel oluşturma sağlayıcı plugin’ini listeler
  - Yoklamadan önce eksik sağlayıcı ortam değişkenlerini login shell’inizden (`~/.profile`) yükler
  - Varsayılan olarak depolanmış auth profillerinden önce live/env API anahtarlarını kullanır; böylece `auth-profiles.json` içindeki eski test anahtarları gerçek shell kimlik bilgilerini maskelemez
  - Kullanılabilir auth/profil/model olmayan sağlayıcıları atlar
  - Stok görsel oluşturma varyantlarını paylaşılan çalışma zamanı yeteneği üzerinden çalıştırır:
    - `google:flash-generate`
    - `google:pro-generate`
    - `google:pro-edit`
    - `openai:default-generate`
- Şu anda kapsanan paketlenmiş sağlayıcılar:
  - `openai`
  - `google`
- İsteğe bağlı daraltma:
  - `OPENCLAW_LIVE_IMAGE_GENERATION_PROVIDERS="openai,google"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_MODELS="openai/gpt-image-1,google/gemini-3.1-flash-image-preview"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_CASES="google:flash-generate,google:pro-edit"`
- İsteğe bağlı auth davranışı:
  - Profil deposu auth’unu zorlamak ve yalnızca env geçersiz kılmalarını yok saymak için `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`

## Müzik oluşturma live

- Test: `extensions/music-generation-providers.live.test.ts`
- Etkinleştirme: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts`
- Kapsam:
  - Paylaşılan paketlenmiş müzik oluşturma sağlayıcı yolunu dener
  - Şu anda Google ve MiniMax’i kapsar
  - Yoklamadan önce sağlayıcı ortam değişkenlerini login shell’inizden (`~/.profile`) yükler
  - Kullanılabilir auth/profil/model olmayan sağlayıcıları atlar
- İsteğe bağlı daraltma:
  - `OPENCLAW_LIVE_MUSIC_GENERATION_PROVIDERS="google,minimax"`
  - `OPENCLAW_LIVE_MUSIC_GENERATION_MODELS="google/lyria-3-clip-preview,minimax/music-2.5+"`

## Docker çalıştırıcıları (isteğe bağlı “Linux’ta çalışıyor” denetimleri)

Bu Docker çalıştırıcıları iki gruba ayrılır:

- Live-model çalıştırıcıları: `test:docker:live-models` ve `test:docker:live-gateway`, yalnızca eşleşen profil-anahtarlı live dosyalarını depo Docker imajı içinde çalıştırır (`src/agents/models.profiles.live.test.ts` ve `src/gateway/gateway-models.profiles.live.test.ts`), yerel config dizininizi ve çalışma alanınızı mount eder (ve mount edilmişse `~/.profile` kaynağını alır). Eşleşen yerel giriş noktaları `test:live:models-profiles` ve `test:live:gateway-profiles`’tır.
- Docker live çalıştırıcıları varsayılan olarak daha küçük bir smoke sınırı kullanır; böylece tam bir Docker taraması pratik kalır:
  `test:docker:live-models`, varsayılan olarak `OPENCLAW_LIVE_MAX_MODELS=12` kullanır ve
  `test:docker:live-gateway`, varsayılan olarak `OPENCLAW_LIVE_GATEWAY_SMOKE=1`,
  `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=8`,
  `OPENCLAW_LIVE_GATEWAY_STEP_TIMEOUT_MS=45000` ve
  `OPENCLAW_LIVE_GATEWAY_MODEL_TIMEOUT_MS=90000` kullanır. Daha büyük kapsamlı taramayı özellikle istediğinizde bu ortam değişkenlerini geçersiz kılın.
- `test:docker:all`, live Docker imajını bir kez `test:docker:live-build` ile oluşturur, ardından bunu iki live Docker şeridi için yeniden kullanır.
- Kapsayıcı smoke çalıştırıcıları: `test:docker:openwebui`, `test:docker:onboard`, `test:docker:gateway-network`, `test:docker:mcp-channels` ve `test:docker:plugins`, bir veya daha fazla gerçek kapsayıcı başlatır ve daha üst seviye integration yollarını doğrular.

Live-model Docker çalıştırıcıları ayrıca yalnızca gerekli CLI auth home’larını bağlar (veya çalıştırma daraltılmamışsa desteklenenlerin tümünü), ardından harici-CLI OAuth belirteç yenileme işlemlerinin host auth deposunu değiştirmeden çalışabilmesi için bunları çalıştırma öncesinde kapsayıcı home’una kopyalar:

- Doğrudan modeller: `pnpm test:docker:live-models` (script: `scripts/test-live-models-docker.sh`)
- ACP bind smoke: `pnpm test:docker:live-acp-bind` (script: `scripts/test-live-acp-bind-docker.sh`)
- Gateway + dev agent: `pnpm test:docker:live-gateway` (script: `scripts/test-live-gateway-models-docker.sh`)
- Open WebUI live smoke: `pnpm test:docker:openwebui` (script: `scripts/e2e/openwebui-docker.sh`)
- Onboarding wizard (TTY, tam scaffolding): `pnpm test:docker:onboard` (script: `scripts/e2e/onboard-docker.sh`)
- Gateway networking (iki kapsayıcı, WS auth + sağlık): `pnpm test:docker:gateway-network` (script: `scripts/e2e/gateway-network-docker.sh`)
- MCP channel bridge (seeded Gateway + stdio bridge + ham Claude notification-frame smoke): `pnpm test:docker:mcp-channels` (script: `scripts/e2e/mcp-channels-docker.sh`)
- Plugins (kurulum smoke + `/plugin` takma adı + Claude-bundle yeniden başlatma semantiği): `pnpm test:docker:plugins` (script: `scripts/e2e/plugins-docker.sh`)

Live-model Docker çalıştırıcıları ayrıca mevcut checkout’u salt okunur olarak bind-mount eder ve bunu kapsayıcı içinde geçici bir workdir’e hazırlar. Bu, çalışma zamanı imajını ince tutarken Vitest’i tam sizin yerel kaynak/config’iniz üzerinde çalıştırmayı sağlar.
Hazırlama adımı `.pnpm-store`, `.worktrees`, `__openclaw_vitest__` ve uygulamaya özgü `.build` veya Gradle çıktı dizinleri gibi büyük yerel önbellekleri ve uygulama derleme çıktılarını atlar; böylece Docker live çalıştırmaları makineye özgü yapıtları kopyalamakla dakikalar harcamaz.
Ayrıca `OPENCLAW_SKIP_CHANNELS=1` ayarlarlar; böylece gateway live yoklamaları kapsayıcı içinde gerçek Telegram/Discord vb. kanal worker’larını başlatmaz.
`test:docker:live-models` yine de `pnpm test:live` çalıştırır; bu yüzden bu Docker şeridinde gateway live kapsamını daraltmanız veya hariç tutmanız gerektiğinde `OPENCLAW_LIVE_GATEWAY_*` değişkenlerini de iletin.
`test:docker:openwebui`, daha üst seviye bir uyumluluk smoke testidir: OpenAI uyumlu HTTP uç noktaları etkin bir OpenClaw gateway kapsayıcısı başlatır, bu gateway’e karşı sabitlenmiş bir Open WebUI kapsayıcısı başlatır, Open WebUI üzerinden oturum açar, `/api/models` içinde `openclaw/default` değerinin sunulduğunu doğrular, ardından Open WebUI’nin `/api/chat/completions` proxy’si üzerinden gerçek bir sohbet isteği gönderir.
İlk çalıştırma belirgin şekilde daha yavaş olabilir; çünkü Docker’ın Open WebUI imajını çekmesi gerekebilir ve Open WebUI’nin kendi soğuk başlangıç kurulumunu tamamlaması gerekebilir.
Bu şerit kullanılabilir bir live model anahtarı bekler ve Docker’laştırılmış çalıştırmalarda bunu sağlamanın birincil yolu `OPENCLAW_PROFILE_FILE`’dır (varsayılan `~/.profile`).
Başarılı çalıştırmalar `{ "ok": true, "model": "openclaw/default", ... }` gibi küçük bir JSON yükü yazdırır.
`test:docker:mcp-channels`, bilinçli olarak deterministiktir ve gerçek bir Telegram, Discord veya iMessage hesabına ihtiyaç duymaz. Seeded bir Gateway kapsayıcısı başlatır, ardından `openclaw mcp serve` başlatan ikinci bir kapsayıcı açar ve gerçek stdio MCP bridge üzerinden yönlendirilmiş konuşma keşfi, transcript okumaları, ek meta verileri, live event queue davranışı, outbound gönderim yönlendirmesi ve Claude tarzı kanal + izin bildirimlerini doğrular. Bildirim denetimi, smoke testinin yalnızca belirli bir istemci SDK’sının yüzeye çıkardığını değil, bridge’in gerçekte ne yaydığını doğrulaması için ham stdio MCP frame’lerini doğrudan inceler.

Elle ACP plain-language thread smoke (CI değil):

- `bun scripts/dev/discord-acp-plain-language-smoke.ts --channel <discord-channel-id> ...`
- Bu script’i regresyon/hata ayıklama iş akışları için koruyun. ACP thread yönlendirme doğrulaması için tekrar gerekebilir, bu yüzden silmeyin.

Yararlı ortam değişkenleri:

- `OPENCLAW_CONFIG_DIR=...` (varsayılan: `~/.openclaw`) `/home/node/.openclaw` olarak mount edilir
- `OPENCLAW_WORKSPACE_DIR=...` (varsayılan: `~/.openclaw/workspace`) `/home/node/.openclaw/workspace` olarak mount edilir
- `OPENCLAW_PROFILE_FILE=...` (varsayılan: `~/.profile`) `/home/node/.profile` olarak mount edilir ve testler çalıştırılmadan önce source edilir
- `OPENCLAW_DOCKER_CLI_TOOLS_DIR=...` (varsayılan: `~/.cache/openclaw/docker-cli-tools`) Docker içindeki önbelleğe alınmış CLI kurulumları için `/home/node/.npm-global` olarak mount edilir
- `$HOME` altındaki harici CLI auth dizinleri/dosyaları `/host-auth...` altında salt okunur mount edilir, ardından testler başlamadan önce `/home/node/...` içine kopyalanır
  - Varsayılan dizinler: `.minimax`
  - Varsayılan dosyalar: `~/.codex/auth.json`, `~/.codex/config.toml`, `.claude.json`, `~/.claude/.credentials.json`, `~/.claude/settings.json`, `~/.claude/settings.local.json`
  - Daraltılmış sağlayıcı çalıştırmaları, yalnızca `OPENCLAW_LIVE_PROVIDERS` / `OPENCLAW_LIVE_GATEWAY_PROVIDERS` üzerinden çıkarılan gerekli dizinleri/dosyaları mount eder
  - `OPENCLAW_DOCKER_AUTH_DIRS=all`, `OPENCLAW_DOCKER_AUTH_DIRS=none` veya `OPENCLAW_DOCKER_AUTH_DIRS=.claude,.codex` gibi virgüllü bir liste ile elle geçersiz kılın
- Çalıştırmayı daraltmak için `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...`
- Kapsayıcı içinde sağlayıcıları filtrelemek için `OPENCLAW_LIVE_GATEWAY_PROVIDERS=...` / `OPENCLAW_LIVE_PROVIDERS=...`
- Kimlik bilgilerinin profil deposundan gelmesini sağlamak için `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` (env değil)
- Open WebUI smoke testi için gateway tarafından sunulan modeli seçmek için `OPENCLAW_OPENWEBUI_MODEL=...`
- Open WebUI smoke testinde kullanılan nonce-check komutunu geçersiz kılmak için `OPENCLAW_OPENWEBUI_PROMPT=...`
- Sabitlenmiş Open WebUI imaj etiketini geçersiz kılmak için `OPENWEBUI_IMAGE=...`

## Belgeler sağlama denetimi

Belge düzenlemelerinden sonra belge denetimlerini çalıştırın: `pnpm check:docs`.
Sayfa içi başlık denetimlerine de ihtiyacınız olduğunda tam Mintlify anchor doğrulamasını çalıştırın: `pnpm docs:check-links:anchors`.

## Çevrimdışı regresyon (CI-safe)

Bunlar, gerçek sağlayıcılar olmadan “gerçek boru hattı” regresyonlarıdır:

- Gateway araç çağırma (sahte OpenAI, gerçek gateway + agent loop): `src/gateway/gateway.test.ts` (durum: "runs a mock OpenAI tool call end-to-end via gateway agent loop")
- Gateway wizard (WS `wizard.start`/`wizard.next`, config + auth yazımı zorunlu): `src/gateway/gateway.test.ts` (durum: "runs wizard over ws and writes auth token config")

## Agent güvenilirlik değerlendirmeleri (skills)

Şimdiden “agent güvenilirlik değerlendirmeleri” gibi davranan birkaç CI-safe testimiz var:

- Gerçek gateway + agent loop üzerinden sahte araç çağırma (`src/gateway/gateway.test.ts`).
- Oturum wiring ve config etkilerini doğrulayan uçtan uca wizard akışları (`src/gateway/gateway.test.ts`).

Skills için hâlâ eksik olanlar (bkz. [Skills](/tr/tools/skills)):

- **Karar verme:** skills komutta listelendiğinde agent doğru skill’i seçiyor mu (veya alakasız olanlardan kaçınıyor mu)?
- **Uyumluluk:** agent kullanımdan önce `SKILL.md` dosyasını okuyor ve gerekli adımları/argümanları izliyor mu?
- **İş akışı sözleşmeleri:** araç sırasını, oturum geçmişi devrini ve sandbox sınırlarını doğrulayan çok turlu senaryolar.

Gelecekteki değerlendirmeler önce deterministik kalmalıdır:

- Araç çağrılarını + sırasını, skill dosyası okumalarını ve oturum wiring’ini doğrulamak için sahte sağlayıcılar kullanan bir senaryo çalıştırıcısı.
- Skill odaklı küçük bir senaryo paketi (kullan ve kaçın, kapılama, prompt injection).
- Yalnızca CI-safe paket yerleştirildikten sonra isteğe bağlı live değerlendirmeler (opt-in, env-gated).

## Sözleşme testleri (plugin ve channel şekli)

Sözleşme testleri, kayıtlı her plugin ve channel’ın arayüz sözleşmesine uyduğunu doğrular. Keşfedilen tüm plugin’ler üzerinde dolaşır ve şekil ile davranış doğrulamaları paketini çalıştırır. Varsayılan `pnpm test` unit şeridi, bu paylaşılan seam ve smoke dosyalarını bilerek atlar; paylaşılan channel veya provider yüzeylerine dokunduğunuzda sözleşme komutlarını açıkça çalıştırın.

### Komutlar

- Tüm sözleşmeler: `pnpm test:contracts`
- Yalnızca channel sözleşmeleri: `pnpm test:contracts:channels`
- Yalnızca provider sözleşmeleri: `pnpm test:contracts:plugins`

### Channel sözleşmeleri

`src/channels/plugins/contracts/*.contract.test.ts` içinde bulunur:

- **plugin** - Temel plugin şekli (id, name, capabilities)
- **setup** - Setup wizard sözleşmesi
- **session-binding** - Oturum bağlama davranışı
- **outbound-payload** - Mesaj payload yapısı
- **inbound** - Gelen mesaj işleme
- **actions** - Channel eylem işleyicileri
- **threading** - Thread ID işleme
- **directory** - Directory/roster API
- **group-policy** - Grup ilkesi uygulaması

### Provider durum sözleşmeleri

`src/plugins/contracts/*.contract.test.ts` içinde bulunur.

- **status** - Channel durum yoklamaları
- **registry** - Plugin kayıt defteri şekli

### Provider sözleşmeleri

`src/plugins/contracts/*.contract.test.ts` içinde bulunur:

- **auth** - Auth akışı sözleşmesi
- **auth-choice** - Auth seçimi/seçim mantığı
- **catalog** - Model katalog API’si
- **discovery** - Plugin keşfi
- **loader** - Plugin yükleme
- **runtime** - Provider çalışma zamanı
- **shape** - Plugin şekli/arayüzü
- **wizard** - Setup wizard

### Ne zaman çalıştırılmalı

- plugin-sdk dışa aktarımlarını veya alt yollarını değiştirdikten sonra
- Bir channel veya provider plugin ekledikten ya da değiştirdikten sonra
- Plugin kaydı veya keşfini yeniden düzenledikten sonra

Sözleşme testleri CI içinde çalışır ve gerçek API anahtarı gerektirmez.

## Regresyon ekleme (rehber)

Live içinde keşfedilen bir provider/model sorununu düzelttiğinizde:

- Mümkünse CI-safe bir regresyon ekleyin (sahte/stub provider veya tam istek-şekli dönüşümünü yakalayın)
- Doğası gereği yalnızca live ise (rate limit, auth ilkeleri), live testi dar ve ortam değişkenleriyle opt-in tutun
- Hatayı yakalayan en küçük katmanı hedeflemeyi tercih edin:
  - provider istek dönüştürme/replay hatası → doğrudan models testi
  - gateway session/history/tool pipeline hatası → gateway live smoke veya CI-safe gateway mock testi
- SecretRef traversal guardrail:
  - `src/secrets/exec-secret-ref-id-parity.test.ts`, kayıt defteri meta verisinden (`listSecretTargetRegistryEntries()`) SecretRef sınıfı başına örneklenmiş bir hedef türetir, ardından traversal-segment exec kimliklerinin reddedildiğini doğrular.
  - `src/secrets/target-registry-data.ts` içinde yeni bir `includeInPlan` SecretRef hedef ailesi eklerseniz, bu testte `classifyTargetClass` değerini güncelleyin. Test, yeni sınıfların sessizce atlanamaması için bilerek sınıflandırılmamış hedef kimliklerinde başarısız olur.
