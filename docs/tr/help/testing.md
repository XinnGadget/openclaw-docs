---
read_when:
    - Testleri yerelde veya CI içinde çalıştırırken
    - Model/provider hataları için regresyon eklerken
    - Gateway + ajan davranışında hata ayıklarken
summary: 'Test kiti: unit/e2e/live paketleri, Docker çalıştırıcıları ve her testin neleri kapsadığı'
title: Test etme
x-i18n:
    generated_at: "2026-04-07T08:47:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: 248868fe5726ca2086ffd3dffee1459bcd810ac9275414eba3a75576cdeec116
    source_path: help/testing.md
    workflow: 15
---

# Test etme

OpenClaw'ın üç Vitest paketi vardır (unit/integration, e2e, live) ve küçük bir Docker çalıştırıcı kümesi bulunur.

Bu belge bir “nasıl test ediyoruz” kılavuzudur:

- Her paketin neleri kapsadığı (ve özellikle neleri kapsamadığı)
- Yaygın iş akışları için hangi komutların çalıştırılacağı (yerel, push öncesi, hata ayıklama)
- Live testlerin kimlik bilgilerini nasıl bulduğu ve modelleri/provider'ları nasıl seçtiği
- Gerçek dünyadaki model/provider sorunları için regresyonların nasıl ekleneceği

## Hızlı başlangıç

Çoğu gün:

- Tam geçit (push öncesinde beklenir): `pnpm build && pnpm check && pnpm test`
- Geniş kaynaklı bir makinede daha hızlı yerel tam paket çalıştırması: `pnpm test:max`
- Doğrudan Vitest izleme döngüsü: `pnpm test:watch`
- Doğrudan dosya hedefleme artık extension/channel yollarını da yönlendirir: `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`
- Docker destekli QA sitesi: `pnpm qa:lab:up`

Testlere dokunduğunuzda veya daha fazla güven istediğinizde:

- Kapsam geçidi: `pnpm test:coverage`
- E2E paketi: `pnpm test:e2e`

Gerçek provider/model hatalarında hata ayıklarken (gerçek kimlik bilgileri gerekir):

- Live paketi (modeller + gateway araç/görüntü probları): `pnpm test:live`
- Tek bir live dosyasını sessizce hedefleyin: `pnpm test:live -- src/agents/models.profiles.live.test.ts`

İpucu: yalnızca tek bir başarısız duruma ihtiyacınız olduğunda, aşağıda açıklanan izin listesi ortam değişkenleriyle live testleri daraltmayı tercih edin.

## Test paketleri (nerede ne çalışır)

Paketleri “artan gerçekçilik” (ve artan kararsızlık/maliyet) olarak düşünün:

### Unit / integration (varsayılan)

- Komut: `pnpm test`
- Yapılandırma: mevcut kapsamlı Vitest projeleri üzerinde ardışık on shard çalıştırması (`vitest.full-*.config.ts`)
- Dosyalar: `src/**/*.test.ts`, `packages/**/*.test.ts`, `test/**/*.test.ts` altındaki core/unit envanterleri ve `vitest.unit.config.ts` tarafından kapsanan izinli `ui` node testleri
- Kapsam:
  - Saf unit testleri
  - Süreç içi integration testleri (gateway auth, routing, tooling, parsing, config)
  - Bilinen hatalar için deterministik regresyonlar
- Beklentiler:
  - CI içinde çalışır
  - Gerçek anahtar gerekmez
  - Hızlı ve kararlı olmalıdır
- Projeler notu:
  - Hedef verilmemiş `pnpm test`, artık tek büyük bir yerel kök proje süreci yerine on bir küçük shard yapılandırması çalıştırır (`core-unit-src`, `core-unit-security`, `core-unit-ui`, `core-unit-support`, `core-support-boundary`, `core-contracts`, `core-bundled`, `core-runtime`, `agentic`, `auto-reply`, `extensions`). Bu, yüklü makinelerde tepe RSS değerini azaltır ve auto-reply/extension işlerinin ilgisiz paketleri aç bırakmasını önler.
  - `pnpm test --watch` hâlâ yerel kök `vitest.config.ts` proje grafiğini kullanır, çünkü çok shard'lı bir izleme döngüsü pratik değildir.
  - `pnpm test`, `pnpm test:watch` ve `pnpm test:perf:imports`, açık dosya/dizin hedeflerini önce kapsamlı koridorlar üzerinden yönlendirir; böylece `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts` tam kök proje başlangıç maliyetini ödemez.
  - `pnpm test:changed`, fark yalnızca yönlendirilebilir kaynak/test dosyalarına dokunuyorsa değişen git yollarını aynı kapsamlı koridorlara genişletir; config/setup düzenlemeleri yine geniş kök proje yeniden çalıştırmasına geri döner.
  - Seçili `plugin-sdk` ve `commands` testleri de `test/setup-openclaw-runtime.ts` dosyasını atlayan ayrılmış hafif koridorlar üzerinden yönlendirilir; durumsal/çalışma zamanı ağırlıklı dosyalar mevcut koridorlarda kalır.
  - Seçili `plugin-sdk` ve `commands` yardımcı kaynak dosyaları da değişen-mod çalıştırmalarını bu hafif koridorlardaki açık kardeş testlere eşler; böylece yardımcı düzenlemeleri o dizin için tam ağır paketi yeniden çalıştırmaktan kaçınır.
  - `auto-reply` artık üç ayrılmış bölüme sahiptir: üst düzey core yardımcıları, üst düzey `reply.*` integration testleri ve `src/auto-reply/reply/**` alt ağacı. Bu, en ağır yanıt harness işini ucuz status/chunk/token testlerinden uzak tutar.
- Gömülü çalıştırıcı notu:
  - Mesaj-aracı keşif girdilerini veya compaction çalışma zamanı bağlamını değiştirdiğinizde,
    her iki kapsama düzeyini de koruyun.
  - Saf routing/normalization sınırları için odaklı yardımcı regresyonları ekleyin.
  - Ayrıca gömülü çalıştırıcı integration paketlerini de sağlıklı tutun:
    `src/agents/pi-embedded-runner/compact.hooks.test.ts`,
    `src/agents/pi-embedded-runner/run.overflow-compaction.test.ts` ve
    `src/agents/pi-embedded-runner/run.overflow-compaction.loop.test.ts`.
  - Bu paketler, kapsamlı kimliklerin ve compaction davranışının hâlâ
    gerçek `run.ts` / `compact.ts` yollarından aktığını doğrular; yalnızca
    yardımcı testler bu integration yolları için yeterli bir ikame değildir.
- Havuz notu:
  - Temel Vitest config artık varsayılan olarak `threads` kullanır.
  - Paylaşılan Vitest config ayrıca `isolate: false` değerini sabitler ve kök projeler, e2e ve live config'lerinde izole edilmemiş çalıştırıcıyı kullanır.
  - Kök UI koridoru `jsdom` setup ve optimizer ayarını korur, ancak artık paylaşılan izole edilmemiş çalıştırıcı üzerinde çalışır.
  - Her `pnpm test` shard'ı, paylaşılan Vitest config'den aynı `threads` + `isolate: false` varsayılanlarını devralır.
  - Paylaşılan `scripts/run-vitest.mjs` başlatıcısı artık büyük yerel çalıştırmalarda V8 derleme dalgalanmasını azaltmak için Vitest alt Node süreçlerine varsayılan olarak `--no-maglev` de ekler. Varsayılan V8 davranışıyla karşılaştırmanız gerekiyorsa `OPENCLAW_VITEST_ENABLE_MAGLEV=1` ayarlayın.
- Hızlı yerel iterasyon notu:
  - `pnpm test:changed`, değişen yollar daha küçük bir pakete temiz biçimde eşleniyorsa kapsamlı koridorlar üzerinden yönlendirir.
  - `pnpm test:max` ve `pnpm test:changed:max`, yalnızca daha yüksek worker sınırıyla aynı yönlendirme davranışını korur.
  - Yerel worker otomatik ölçekleme artık kasıtlı olarak daha muhafazakârdır ve ana makine yük ortalaması zaten yüksek olduğunda da geri çekilir; böylece birden fazla eşzamanlı Vitest çalıştırması varsayılan olarak daha az zarar verir.
  - Temel Vitest config, test kablolaması değiştiğinde changed-mode yeniden çalıştırmalar doğru kalsın diye projeleri/config dosyalarını `forceRerunTriggers` olarak işaretler.
  - Config, desteklenen ana makinelerde `OPENCLAW_VITEST_FS_MODULE_CACHE` ayarını etkin tutar; doğrudan profil oluşturma için açık bir önbellek konumu istiyorsanız `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/abs/path` ayarlayın.
- Performans hata ayıklama notu:
  - `pnpm test:perf:imports`, Vitest import-duration raporlamasını ve import-breakdown çıktısını etkinleştirir.
  - `pnpm test:perf:imports:changed`, aynı profilleme görünümünü `origin/main` sonrasındaki değişen dosyalarla sınırlar.
- `pnpm test:perf:changed:bench -- --ref <git-ref>`, yönlendirilmiş `test:changed` ile yerel kök proje yolunu o commit edilmiş fark için karşılaştırır ve duvar saati ile macOS max RSS değerini yazdırır.
- `pnpm test:perf:changed:bench -- --worktree`, değişen dosya listesini `scripts/test-projects.mjs` ve kök Vitest config üzerinden yönlendirerek mevcut kirli ağacı kıyaslar.
  - `pnpm test:perf:profile:main`, Vitest/Vite başlangıcı ve transform yükü için ana iş parçacığı CPU profili yazar.
  - `pnpm test:perf:profile:runner`, dosya paralelliği devre dışı bırakılmış unit paketi için çalıştırıcı CPU+heap profilleri yazar.

### E2E (gateway smoke)

- Komut: `pnpm test:e2e`
- Config: `vitest.e2e.config.ts`
- Dosyalar: `src/**/*.e2e.test.ts`, `test/**/*.e2e.test.ts`
- Çalışma zamanı varsayılanları:
  - Depodaki geri kalanla eşleşecek şekilde Vitest `threads` ve `isolate: false` kullanır.
  - Uyarlanabilir worker'lar kullanır (CI: en fazla 2, yerel: varsayılan 1).
  - Konsol G/Ç yükünü azaltmak için varsayılan olarak sessiz modda çalışır.
- Yararlı geçersiz kılmalar:
  - Worker sayısını zorlamak için `OPENCLAW_E2E_WORKERS=<n>` (üst sınır 16).
  - Ayrıntılı konsol çıktısını yeniden etkinleştirmek için `OPENCLAW_E2E_VERBOSE=1`.
- Kapsam:
  - Çok örnekli gateway uçtan uca davranışı
  - WebSocket/HTTP yüzeyleri, node eşleştirme ve daha ağır ağ işlemleri
- Beklentiler:
  - CI içinde çalışır (pipeline'da etkinleştirildiğinde)
  - Gerçek anahtar gerekmez
  - Unit testlerden daha fazla hareketli parça vardır (daha yavaş olabilir)

### E2E: OpenShell backend smoke

- Komut: `pnpm test:e2e:openshell`
- Dosya: `test/openshell-sandbox.e2e.test.ts`
- Kapsam:
  - Ana makinede Docker üzerinden yalıtılmış bir OpenShell gateway başlatır
  - Geçici bir yerel Dockerfile'dan bir sandbox oluşturur
  - OpenClaw'ın OpenShell backend'ini gerçek `sandbox ssh-config` + SSH exec üzerinden çalıştırır
  - Sandbox fs bridge üzerinden remote-canonical dosya sistemi davranışını doğrular
- Beklentiler:
  - Yalnızca isteğe bağlıdır; varsayılan `pnpm test:e2e` çalıştırmasının parçası değildir
  - Yerel bir `openshell` CLI ve çalışan bir Docker daemon gerektirir
  - Yalıtılmış `HOME` / `XDG_CONFIG_HOME` kullanır, ardından test gateway ve sandbox'ı yok eder
- Yararlı geçersiz kılmalar:
  - Daha geniş e2e paketini elle çalıştırırken testi etkinleştirmek için `OPENCLAW_E2E_OPENSHELL=1`
  - Varsayılan olmayan bir CLI binary'si veya sarmalayıcı betiğine işaret etmek için `OPENCLAW_E2E_OPENSHELL_COMMAND=/path/to/openshell`

### Live (gerçek provider'lar + gerçek modeller)

- Komut: `pnpm test:live`
- Config: `vitest.live.config.ts`
- Dosyalar: `src/**/*.live.test.ts`
- Varsayılan: `pnpm test:live` tarafından **etkinleştirilir** (`OPENCLAW_LIVE_TEST=1` ayarlar)
- Kapsam:
  - “Bu provider/model bugün gerçek kimlik bilgileriyle gerçekten çalışıyor mu?”
  - Provider biçim değişikliklerini, tool-calling tuhaflıklarını, auth sorunlarını ve rate limit davranışını yakalar
- Beklentiler:
  - Tasarım gereği CI içinde kararlı değildir (gerçek ağlar, gerçek provider politikaları, kotalar, kesintiler)
  - Para harcar / rate limit kullanır
  - “Her şeyi” çalıştırmak yerine daraltılmış alt kümeleri tercih edin
- Live çalıştırmalar, eksik API anahtarlarını almak için `~/.profile` dosyasını source eder.
- Varsayılan olarak live çalıştırmalar yine de `HOME` dizinini yalıtır ve config/auth materyalini geçici bir test ana dizinine kopyalar; böylece unit fixture'ları gerçek `~/.openclaw` dizininizi değiştiremez.
- Live testlerin gerçek home dizininizi kullanmasını özellikle istediğinizde yalnızca `OPENCLAW_LIVE_USE_REAL_HOME=1` ayarlayın.
- `pnpm test:live` artık daha sessiz bir modu varsayılan yapar: `[live] ...` ilerleme çıktısını korur, ancak ek `~/.profile` bildirimini bastırır ve gateway bootstrap günlükleri/Bonjour gürültüsünü susturur. Tam başlangıç günlüklerini geri istiyorsanız `OPENCLAW_LIVE_TEST_QUIET=0` ayarlayın.
- API anahtarı döndürme (provider'a özel): virgül/noktalı virgül biçimiyle `*_API_KEYS` veya `*_API_KEY_1`, `*_API_KEY_2` ayarlayın (örneğin `OPENAI_API_KEYS`, `ANTHROPIC_API_KEYS`, `GEMINI_API_KEYS`) ya da live başına geçersiz kılma için `OPENCLAW_LIVE_*_KEY` kullanın; testler rate limit yanıtlarında yeniden dener.
- İlerleme/heartbeat çıktısı:
  - Live paketleri artık uzun provider çağrılarında etkinliğin görünür kalması için ilerleme satırlarını stderr'e yazar; böylece Vitest konsol yakalaması sessiz olduğunda bile görünür olur.
  - `vitest.live.config.ts`, provider/gateway ilerleme satırlarının live çalıştırmalar sırasında anında akması için Vitest konsol müdahalesini devre dışı bırakır.
  - Doğrudan model heartbeat'lerini `OPENCLAW_LIVE_HEARTBEAT_MS` ile ayarlayın.
  - Gateway/probe heartbeat'lerini `OPENCLAW_LIVE_GATEWAY_HEARTBEAT_MS` ile ayarlayın.

## Hangi paketi çalıştırmalıyım?

Bu karar tablosunu kullanın:

- Mantık/test düzenliyorsanız: `pnpm test` çalıştırın (çok şey değiştirdiyseniz ayrıca `pnpm test:coverage`)
- Gateway ağı / WS protokolü / eşleştirmeye dokunuyorsanız: `pnpm test:e2e` ekleyin
- “Botum çalışmıyor” / provider'a özgü hatalar / tool calling hata ayıklıyorsanız: daraltılmış bir `pnpm test:live` çalıştırın

## Live: Android node capability sweep

- Test: `src/gateway/android-node.capabilities.live.test.ts`
- Betik: `pnpm android:test:integration`
- Amaç: bağlı bir Android node tarafından şu anda ilan edilen **her komutu** çağırmak ve komut sözleşmesi davranışını doğrulamak.
- Kapsam:
  - Ön koşullu/elle kurulum (paket uygulamayı kurmaz/çalıştırmaz/eşleştirmez).
  - Seçilen Android node için komut bazında gateway `node.invoke` doğrulaması.
- Gerekli ön kurulum:
  - Android uygulaması zaten gateway'e bağlı ve eşleştirilmiş olmalı.
  - Uygulama ön planda tutulmalı.
  - Geçmesini beklediğiniz yetenekler için izinler/yakalama onayı verilmiş olmalı.
- İsteğe bağlı hedef geçersiz kılmaları:
  - `OPENCLAW_ANDROID_NODE_ID` veya `OPENCLAW_ANDROID_NODE_NAME`.
  - `OPENCLAW_ANDROID_GATEWAY_URL` / `OPENCLAW_ANDROID_GATEWAY_TOKEN` / `OPENCLAW_ANDROID_GATEWAY_PASSWORD`.
- Tam Android kurulum ayrıntıları: [Android App](/tr/platforms/android)

## Live: model smoke (profil anahtarları)

Live testler hataları yalıtabilmek için iki katmana ayrılmıştır:

- “Doğrudan model”, provider/model'in verilen anahtarla en azından yanıt verebildiğini söyler.
- “Gateway smoke”, tam gateway+ajan işlem hattısının o model için çalıştığını söyler (oturumlar, geçmiş, araçlar, sandbox ilkesi vb.).

### Katman 1: Doğrudan model tamamlama (gateway yok)

- Test: `src/agents/models.profiles.live.test.ts`
- Amaç:
  - Keşfedilen modelleri numaralandırmak
  - Kimlik bilgilerine sahip olduğunuz modelleri seçmek için `getApiKeyForModel` kullanmak
  - Model başına küçük bir tamamlama çalıştırmak (ve gerektiğinde hedefli regresyonlar)
- Etkinleştirme:
  - `pnpm test:live` (veya Vitest'i doğrudan çağırıyorsanız `OPENCLAW_LIVE_TEST=1`)
- Bu paketi gerçekten çalıştırmak için `OPENCLAW_LIVE_MODELS=modern` (veya modern için takma ad olan `all`) ayarlayın; aksi halde `pnpm test:live` odaklı kalsın diye atlanır
- Model seçimi:
  - Modern izin listesini çalıştırmak için `OPENCLAW_LIVE_MODELS=modern` (Opus/Sonnet 4.6+, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.7, Grok 4)
  - `OPENCLAW_LIVE_MODELS=all`, modern izin listesi için bir takma addır
  - veya `OPENCLAW_LIVE_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,..."` (virgüllü izin listesi)
- Provider seçimi:
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity,google-gemini-cli"` (virgüllü izin listesi)
- Anahtarlar nereden gelir:
  - Varsayılan olarak: profil deposu ve ortam değişkeni yedekleri
  - Yalnızca **profil deposunu** zorunlu kılmak için `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` ayarlayın
- Bunun nedeni:
  - “Provider API bozuk / anahtar geçersiz” ile “gateway ajan işlem hattı bozuk” durumlarını ayırır
  - Küçük, yalıtılmış regresyonlar içerir (örnek: OpenAI Responses/Codex Responses akıl yürütme tekrar oynatma + tool-call akışları)

### Katman 2: Gateway + dev ajan smoke ( "@openclaw" gerçekte ne yapar)

- Test: `src/gateway/gateway-models.profiles.live.test.ts`
- Amaç:
  - Süreç içi bir gateway döndürmek
  - Bir `agent:dev:*` oturumu oluşturmak/yamalamak (çalıştırma başına model geçersiz kılmalı)
  - Anahtarlı modeller üzerinde dönerek şunları doğrulamak:
    - “anlamlı” yanıt (araç yok)
    - gerçek bir araç çağrısının çalışması (`read` probe)
    - isteğe bağlı ek araç probları (`exec+read` probe)
    - OpenAI regresyon yollarının (yalnızca tool-call → takip) çalışmaya devam etmesi
- Probe ayrıntıları (hataları hızlı açıklayabilmeniz için):
  - `read` probe: test çalışma alanına nonce içeren bir dosya yazar ve ajandan bunu `read` etmesini ve nonce değerini geri yankılamasını ister.
  - `exec+read` probe: test ajandan geçici bir dosyaya nonce yazmak için `exec` kullanmasını, ardından bunu geri `read` etmesini ister.
  - görüntü probe'u: test oluşturulmuş bir PNG ekler (cat + rastgele kod) ve modelin `cat <CODE>` döndürmesini bekler.
  - Uygulama başvurusu: `src/gateway/gateway-models.profiles.live.test.ts` ve `src/gateway/live-image-probe.ts`.
- Etkinleştirme:
  - `pnpm test:live` (veya Vitest'i doğrudan çağırıyorsanız `OPENCLAW_LIVE_TEST=1`)
- Model seçimi:
  - Varsayılan: modern izin listesi (Opus/Sonnet 4.6+, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.7, Grok 4)
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all`, modern izin listesi için bir takma addır
  - Ya da daraltmak için `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"` (veya virgüllü liste) ayarlayın
- Provider seçimi (“OpenRouter her şey”den kaçının):
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,google-gemini-cli,openai,anthropic,zai,minimax"` (virgüllü izin listesi)
- Araç + görüntü probları bu live testte her zaman açıktır:
  - `read` probe + `exec+read` probe (araç stresi)
  - model görüntü girişi desteği ilan ettiğinde görüntü probe'u çalışır
  - Akış (üst düzey):
    - Test “CAT” + rastgele kod içeren küçük bir PNG üretir (`src/gateway/live-image-probe.ts`)
    - Bunu `agent` üzerinden `attachments: [{ mimeType: "image/png", content: "<base64>" }]` ile gönderir
    - Gateway ekleri `images[]` içine ayrıştırır (`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`)
    - Gömülü ajan modele çok kipli bir kullanıcı mesajı iletir
    - Doğrulama: yanıt `cat` + kodu içerir (OCR toleransı: küçük hatalara izin verilir)

İpucu: makinenizde neyi test edebileceğinizi (ve tam `provider/model` kimliklerini) görmek için şunu çalıştırın:

```bash
openclaw models list
openclaw models list --json
```

## Live: CLI backend smoke (Claude, Codex, Gemini veya diğer yerel CLI'lar)

- Test: `src/gateway/gateway-cli-backend.live.test.ts`
- Amaç: varsayılan config'inize dokunmadan, Gateway + ajan işlem hattısını yerel bir CLI backend ile doğrulamak.
- Backend'e özgü varsayılan smoke ayarları, sahip extension'ın `cli-backend.ts` tanımıyla birlikte yaşar.
- Etkinleştirme:
  - `pnpm test:live` (veya Vitest'i doğrudan çağırıyorsanız `OPENCLAW_LIVE_TEST=1`)
  - `OPENCLAW_LIVE_CLI_BACKEND=1`
- Varsayılanlar:
  - Varsayılan provider/model: `claude-cli/claude-sonnet-4-6`
  - Komut/argüman/görüntü davranışı sahip CLI backend plugin meta verisinden gelir.
- Geçersiz kılmalar (isteğe bağlı):
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4"`
  - `OPENCLAW_LIVE_CLI_BACKEND_COMMAND="/full/path/to/codex"`
  - `OPENCLAW_LIVE_CLI_BACKEND_ARGS='["exec","--json","--color","never","--sandbox","read-only","--skip-git-repo-check"]'`
  - Gerçek bir görüntü eki göndermek için `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_PROBE=1` (yollar prompt içine enjekte edilir).
  - Görüntü dosyası yollarını prompt enjeksiyonu yerine CLI argümanları olarak geçirmek için `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_ARG="--image"`.
  - `IMAGE_ARG` ayarlı olduğunda görüntü argümanlarının nasıl geçirileceğini kontrol etmek için `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_MODE="repeat"` (veya `"list"`).
  - İkinci tur göndermek ve resume akışını doğrulamak için `OPENCLAW_LIVE_CLI_BACKEND_RESUME_PROBE=1`.

Örnek:

```bash
OPENCLAW_LIVE_CLI_BACKEND=1 \
  OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4" \
  pnpm test:live src/gateway/gateway-cli-backend.live.test.ts
```

Docker tarifi:

```bash
pnpm test:docker:live-cli-backend
```

Tek provider Docker tarifleri:

```bash
pnpm test:docker:live-cli-backend:claude
pnpm test:docker:live-cli-backend:codex
pnpm test:docker:live-cli-backend:gemini
```

Notlar:

- Docker çalıştırıcısı `scripts/test-live-cli-backend-docker.sh` konumundadır.
- Live CLI-backend smoke testini depo Docker görüntüsü içinde root olmayan `node` kullanıcısı olarak çalıştırır.
- CLI smoke meta verisini sahip extension'dan çözümler, ardından eşleşen Linux CLI paketini (`@anthropic-ai/claude-code`, `@openai/codex` veya `@google/gemini-cli`) `OPENCLAW_DOCKER_CLI_TOOLS_DIR` içindeki önbelleklenmiş yazılabilir öneke kurar (varsayılan: `~/.cache/openclaw/docker-cli-tools`).

## Live: ACP bind smoke (`/acp spawn ... --bind here`)

- Test: `src/gateway/gateway-acp-bind.live.test.ts`
- Amaç: gerçek bir ACP ajanıyla gerçek ACP conversation-bind akışını doğrulamak:
  - `/acp spawn <agent> --bind here` gönder
  - sentetik bir message-channel konuşmasını yerinde bağla
  - aynı konuşmada normal bir takip mesajı gönder
  - takibin bağlı ACP oturum dökümüne düştüğünü doğrula
- Etkinleştirme:
  - `pnpm test:live src/gateway/gateway-acp-bind.live.test.ts`
  - `OPENCLAW_LIVE_ACP_BIND=1`
- Varsayılanlar:
  - Docker içindeki ACP ajanları: `claude,codex,gemini`
  - Doğrudan `pnpm test:live ...` için ACP ajanı: `claude`
  - Sentetik kanal: Slack DM tarzı konuşma bağlamı
  - ACP backend: `acpx`
- Geçersiz kılmalar:
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=claude`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=codex`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude,codex,gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND='npx -y @agentclientprotocol/claude-agent-acp@<version>'`
- Notlar:
  - Bu koridor, testlerin dışarıya teslim edilmiş gibi yapmadan message-channel bağlamı ekleyebilmesi için admin-only sentetik originating-route alanlarıyla gateway `chat.send` yüzeyini kullanır.
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND` ayarlanmadığında test, seçili ACP harness ajanı için gömülü `acpx` plugin'inin yerleşik ajan kaydını kullanır.

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

Tek ajan Docker tarifleri:

```bash
pnpm test:docker:live-acp-bind:claude
pnpm test:docker:live-acp-bind:codex
pnpm test:docker:live-acp-bind:gemini
```

Docker notları:

- Docker çalıştırıcısı `scripts/test-live-acp-bind-docker.sh` konumundadır.
- Varsayılan olarak ACP bind smoke testini desteklenen tüm live CLI ajanlarına sırayla karşı çalıştırır: `claude`, `codex`, sonra `gemini`.
- Matrisi daraltmak için `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude`, `OPENCLAW_LIVE_ACP_BIND_AGENTS=codex` veya `OPENCLAW_LIVE_ACP_BIND_AGENTS=gemini` kullanın.
- `~/.profile` dosyasını source eder, eşleşen CLI auth materyalini konteynıra taşır, `acpx`'i yazılabilir bir npm önekine kurar, sonra eksikse istenen live CLI'ı (`@anthropic-ai/claude-code`, `@openai/codex` veya `@google/gemini-cli`) kurar.
- Docker içinde çalıştırıcı `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=$HOME/.npm-global/bin/acpx` ayarlar; böylece acpx, sourced profile'dan gelen provider ortam değişkenlerini alt harness CLI için kullanılabilir tutar.

### Önerilen live tarifleri

Dar, açık izin listeleri en hızlı ve en az kararsız olanlardır:

- Tek model, doğrudan (gateway yok):
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.4" pnpm test:live src/agents/models.profiles.live.test.ts`

- Tek model, gateway smoke:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Birkaç provider boyunca tool calling:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Google odağı (Gemini API anahtarı + Antigravity):
  - Gemini (API anahtarı): `OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  - Antigravity (OAuth): `OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

Notlar:

- `google/...`, Gemini API kullanır (API anahtarı).
- `google-antigravity/...`, Antigravity OAuth bridge kullanır (Cloud Code Assist tarzı ajan uç noktası).
- `google-gemini-cli/...`, makinenizdeki yerel Gemini CLI'ı kullanır (ayrı auth + araç tuhaflıkları).
- Gemini API ile Gemini CLI:
  - API: OpenClaw, Google'ın barındırılan Gemini API'sini HTTP üzerinden çağırır (API anahtarı / profil auth); çoğu kullanıcının “Gemini” derken kastettiği budur.
  - CLI: OpenClaw, yerel bir `gemini` binary'sini kabuktan çağırır; kendine ait auth'u vardır ve farklı davranabilir (streaming/tool desteği/sürüm kayması).

## Live: model matrisi (neleri kapsıyoruz)

Sabit bir “CI model listesi” yoktur (live isteğe bağlıdır), ancak anahtarlara sahip bir geliştirme makinesinde düzenli olarak kapsanması **önerilen** modeller bunlardır.

### Modern smoke kümesi (tool calling + görüntü)

Çalışır durumda tutmayı beklediğimiz “yaygın modeller” çalıştırması budur:

- OpenAI (Codex dışı): `openai/gpt-5.4` (isteğe bağlı: `openai/gpt-5.4-mini`)
- OpenAI Codex: `openai-codex/gpt-5.4`
- Anthropic: `anthropic/claude-opus-4-6` (veya `anthropic/claude-sonnet-4-6`)
- Google (Gemini API): `google/gemini-3.1-pro-preview` ve `google/gemini-3-flash-preview` (eski Gemini 2.x modellerinden kaçının)
- Google (Antigravity): `google-antigravity/claude-opus-4-6-thinking` ve `google-antigravity/gemini-3-flash`
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

Araçlar + görüntü ile gateway smoke çalıştırması:
`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,openai-codex/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3.1-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

### Temel: tool calling (Read + isteğe bağlı Exec)

Her provider ailesinden en az birini seçin:

- OpenAI: `openai/gpt-5.4` (veya `openai/gpt-5.4-mini`)
- Anthropic: `anthropic/claude-opus-4-6` (veya `anthropic/claude-sonnet-4-6`)
- Google: `google/gemini-3-flash-preview` (veya `google/gemini-3.1-pro-preview`)
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

İsteğe bağlı ek kapsama (olursa iyi olur):

- xAI: `xai/grok-4` (veya mevcut en yeni)
- Mistral: `mistral/`… (etkinleştirdiğiniz “tools” destekli bir model seçin)
- Cerebras: `cerebras/`… (erişiminiz varsa)
- LM Studio: `lmstudio/`… (yerel; tool calling API moduna bağlıdır)

### Vision: görüntü gönderme (ek → çok kipli mesaj)

Görüntü probe'unu çalıştırmak için `OPENCLAW_LIVE_GATEWAY_MODELS` içinde en az bir görüntü destekli modeli (Claude/Gemini/OpenAI görüntü destekli varyantları vb.) ekleyin.

### Toplayıcılar / alternatif gateway'ler

Anahtarlarınız etkinse, şu yollar üzerinden test etmeyi de destekliyoruz:

- OpenRouter: `openrouter/...` (yüzlerce model; tool+image destekli adayları bulmak için `openclaw models scan` kullanın)
- OpenCode: Zen için `opencode/...` ve Go için `opencode-go/...` (`OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY` ile auth)

Live matrisine dahil edebileceğiniz daha fazla provider (kimlik bilgileriniz/config'iniz varsa):

- Yerleşik: `openai`, `openai-codex`, `anthropic`, `google`, `google-vertex`, `google-antigravity`, `google-gemini-cli`, `zai`, `openrouter`, `opencode`, `opencode-go`, `xai`, `groq`, `cerebras`, `mistral`, `github-copilot`
- `models.providers` üzerinden (özel uç noktalar): `minimax` (bulut/API) ve ayrıca OpenAI/Anthropic uyumlu her türlü proxy (LM Studio, vLLM, LiteLLM vb.)

İpucu: belgelere “tüm modelleri” sabit kodlamaya çalışmayın. Yetkili liste, makinenizde `discoverModels(...)` ne döndürüyorsa ve hangi anahtarlar mevcutsa odur.

## Kimlik bilgileri (asla commit etmeyin)

Live testler kimlik bilgilerini CLI ile aynı şekilde bulur. Bunun pratik sonuçları:

- CLI çalışıyorsa live testler de aynı anahtarları bulmalıdır.
- Bir live test “kimlik bilgisi yok” diyorsa, bunu `openclaw models list` / model seçimi hatasını ayıklar gibi ayıklayın.

- Ajan başına auth profilleri: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` (live testlerde “profil anahtarları” denince kastedilen budur)
- Config: `~/.openclaw/openclaw.json` (veya `OPENCLAW_CONFIG_PATH`)
- Eski durum dizini: `~/.openclaw/credentials/` (varsa aşamalı live home içine kopyalanır, ancak ana profil-anahtarı deposu değildir)
- Live yerel çalıştırmalar varsayılan olarak etkin config'i, ajan başına `auth-profiles.json` dosyalarını, eski `credentials/` dizinini ve desteklenen harici CLI auth dizinlerini geçici bir test home'una kopyalar; bu aşamalı config içinde `agents.*.workspace` / `agentDir` yol geçersiz kılmaları kaldırılır, böylece problar gerçek ana makine çalışma alanınızdan uzak kalır.

Ortam değişkeni anahtarlarına güvenmek istiyorsanız (ör. `~/.profile` içinde export edildiyse), yerel testleri `source ~/.profile` sonrasında çalıştırın veya aşağıdaki Docker çalıştırıcılarını kullanın (`~/.profile` dosyasını konteynıra bağlayabilirler).

## Deepgram live (ses transkripsiyonu)

- Test: `src/media-understanding/providers/deepgram/audio.live.test.ts`
- Etkinleştirme: `DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`

## BytePlus coding plan live

- Test: `src/agents/byteplus.live.test.ts`
- Etkinleştirme: `BYTEPLUS_API_KEY=... BYTEPLUS_LIVE_TEST=1 pnpm test:live src/agents/byteplus.live.test.ts`
- İsteğe bağlı model geçersiz kılması: `BYTEPLUS_CODING_MODEL=ark-code-latest`

## ComfyUI workflow media live

- Test: `extensions/comfy/comfy.live.test.ts`
- Etkinleştirme: `OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts`
- Kapsam:
  - Paketlenmiş comfy görüntü, video ve `music_generate` yollarını çalıştırır
  - `models.providers.comfy.<capability>` yapılandırılmamışsa her yeteneği atlar
  - Comfy workflow gönderimi, polling, indirmeler veya plugin kaydı değiştirildikten sonra yararlıdır

## Görüntü üretimi live

- Test: `src/image-generation/runtime.live.test.ts`
- Komut: `pnpm test:live src/image-generation/runtime.live.test.ts`
- Harness: `pnpm test:live:media image`
- Kapsam:
  - Kayıtlı her görüntü üretimi provider plugin'ini numaralandırır
  - Probe'dan önce eksik provider ortam değişkenlerini login kabuğunuzdan (`~/.profile`) yükler
  - Varsayılan olarak saklanan auth profillerinden önce live/env API anahtarlarını kullanır; böylece `auth-profiles.json` içindeki eski test anahtarları gerçek kabuk kimlik bilgilerini maskelemez
  - Kullanılabilir auth/profil/model olmayan provider'ları atlar
  - Stok görüntü üretimi varyantlarını paylaşılan çalışma zamanı yeteneği üzerinden çalıştırır:
    - `google:flash-generate`
    - `google:pro-generate`
    - `google:pro-edit`
    - `openai:default-generate`
- Şu anda kapsanan paketlenmiş provider'lar:
  - `openai`
  - `google`
- İsteğe bağlı daraltma:
  - `OPENCLAW_LIVE_IMAGE_GENERATION_PROVIDERS="openai,google"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_MODELS="openai/gpt-image-1,google/gemini-3.1-flash-image-preview"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_CASES="google:flash-generate,google:pro-edit"`
- İsteğe bağlı auth davranışı:
  - Yalnızca profil deposu auth'unu zorlamak ve env-only geçersiz kılmaları yok saymak için `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`

## Müzik üretimi live

- Test: `extensions/music-generation-providers.live.test.ts`
- Etkinleştirme: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts`
- Harness: `pnpm test:live:media music`
- Kapsam:
  - Paylaşılan paketlenmiş müzik üretimi provider yolunu çalıştırır
  - Şu anda Google ve MiniMax'ı kapsar
  - Probe'dan önce provider ortam değişkenlerini login kabuğunuzdan (`~/.profile`) yükler
  - Varsayılan olarak saklanan auth profillerinden önce live/env API anahtarlarını kullanır; böylece `auth-profiles.json` içindeki eski test anahtarları gerçek kabuk kimlik bilgilerini maskelemez
  - Kullanılabilir auth/profil/model olmayan provider'ları atlar
  - Mevcut olduğunda ilan edilmiş iki çalışma zamanı modunu da çalıştırır:
    - Yalnızca prompt girdisiyle `generate`
    - Provider `capabilities.edit.enabled` ilan ediyorsa `edit`
  - Mevcut paylaşılan-koridor kapsaması:
    - `google`: `generate`, `edit`
    - `minimax`: `generate`
    - `comfy`: ayrı Comfy live dosyası, bu paylaşılan sweep değil
- İsteğe bağlı daraltma:
  - `OPENCLAW_LIVE_MUSIC_GENERATION_PROVIDERS="google,minimax"`
  - `OPENCLAW_LIVE_MUSIC_GENERATION_MODELS="google/lyria-3-clip-preview,minimax/music-2.5+"`
- İsteğe bağlı auth davranışı:
  - Yalnızca profil deposu auth'unu zorlamak ve env-only geçersiz kılmaları yok saymak için `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`

## Video üretimi live

- Test: `extensions/video-generation-providers.live.test.ts`
- Etkinleştirme: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts`
- Harness: `pnpm test:live:media video`
- Kapsam:
  - Paylaşılan paketlenmiş video üretimi provider yolunu çalıştırır
  - Probe'dan önce provider ortam değişkenlerini login kabuğunuzdan (`~/.profile`) yükler
  - Varsayılan olarak saklanan auth profillerinden önce live/env API anahtarlarını kullanır; böylece `auth-profiles.json` içindeki eski test anahtarları gerçek kabuk kimlik bilgilerini maskelemez
  - Kullanılabilir auth/profil/model olmayan provider'ları atlar
  - Mevcut olduğunda ilan edilmiş çalışma zamanı modlarını çalıştırır:
    - Yalnızca prompt girdisiyle `generate`
    - Provider `capabilities.imageToVideo.enabled` ilan ettiğinde ve seçilen provider/model paylaşılan sweep içinde buffer destekli yerel görüntü girdisini kabul ettiğinde `imageToVideo`
    - Provider `capabilities.videoToVideo.enabled` ilan ettiğinde ve seçilen provider/model paylaşılan sweep içinde buffer destekli yerel video girdisini kabul ettiğinde `videoToVideo`
  - Paylaşılan sweep içinde şu anda ilan edilmiş ancak atlanan `imageToVideo` provider'ları:
    - `vydra`, çünkü paketlenmiş `veo3` yalnızca metindir ve paketlenmiş `kling` uzak görüntü URL'si gerektirir
  - Provider'a özgü Vydra kapsamı:
    - `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_VYDRA_VIDEO=1 pnpm test:live -- extensions/vydra/vydra.live.test.ts`
    - bu dosya varsayılan olarak uzak görüntü URL fixture'ı kullanan bir `kling` koridoruyla birlikte `veo3` text-to-video çalıştırır
  - Şu anki `videoToVideo` live kapsamı:
    - yalnızca seçilen model `runway/gen4_aleph` olduğunda `runway`
  - Paylaşılan sweep içinde şu anda ilan edilmiş ancak atlanan `videoToVideo` provider'ları:
    - `alibaba`, `qwen`, `xai`, çünkü bu yollar şu anda uzak `http(s)` / MP4 referans URL'leri gerektiriyor
    - `google`, çünkü mevcut paylaşılan Gemini/Veo koridoru yerel buffer destekli girdi kullanıyor ve bu yol paylaşılan sweep'te kabul edilmiyor
    - `openai`, çünkü mevcut paylaşılan koridorda kuruma özgü video inpaint/remix erişimi garantileri yok
- İsteğe bağlı daraltma:
  - `OPENCLAW_LIVE_VIDEO_GENERATION_PROVIDERS="google,openai,runway"`
  - `OPENCLAW_LIVE_VIDEO_GENERATION_MODELS="google/veo-3.1-fast-generate-preview,openai/sora-2,runway/gen4_aleph"`
- İsteğe bağlı auth davranışı:
  - Yalnızca profil deposu auth'unu zorlamak ve env-only geçersiz kılmaları yok saymak için `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`

## Medya live harness

- Komut: `pnpm test:live:media`
- Amaç:
  - Paylaşılan görüntü, müzik ve video live paketlerini depo-yerel tek bir giriş noktası üzerinden çalıştırır
  - Eksik provider ortam değişkenlerini `~/.profile` içinden otomatik yükler
  - Varsayılan olarak her paketi şu anda kullanılabilir auth'a sahip provider'lara otomatik daraltır
  - `scripts/test-live.mjs` dosyasını yeniden kullanır; böylece heartbeat ve sessiz mod davranışı tutarlı kalır
- Örnekler:
  - `pnpm test:live:media`
  - `pnpm test:live:media image video --providers openai,google,minimax`
  - `pnpm test:live:media video --video-providers openai,runway --all-providers`
  - `pnpm test:live:media music --quiet`

## Docker çalıştırıcıları (isteğe bağlı “Linux'ta çalışıyor” kontrolleri)

Bu Docker çalıştırıcıları iki gruba ayrılır:

- Live-model çalıştırıcıları: `test:docker:live-models` ve `test:docker:live-gateway`, yalnızca eşleşen profil-anahtarı live dosyalarını depo Docker görüntüsü içinde çalıştırır (`src/agents/models.profiles.live.test.ts` ve `src/gateway/gateway-models.profiles.live.test.ts`), yerel config dizininizi ve çalışma alanınızı bağlar (ve bağlıysa `~/.profile` dosyasını source eder). Eşleşen yerel giriş noktaları `test:live:models-profiles` ve `test:live:gateway-profiles` olur.
- Docker live çalıştırıcıları, tam bir Docker sweep'in uygulanabilir kalması için varsayılan olarak daha küçük bir smoke sınırı kullanır:
  `test:docker:live-models`, varsayılan olarak `OPENCLAW_LIVE_MAX_MODELS=12` kullanır ve
  `test:docker:live-gateway`, varsayılan olarak `OPENCLAW_LIVE_GATEWAY_SMOKE=1`,
  `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=8`,
  `OPENCLAW_LIVE_GATEWAY_STEP_TIMEOUT_MS=45000` ve
  `OPENCLAW_LIVE_GATEWAY_MODEL_TIMEOUT_MS=90000` kullanır. Daha büyük kapsamlı taramayı özellikle istediğinizde bu ortam değişkenlerini geçersiz kılın.
- `test:docker:all`, live Docker görüntüsünü bir kez `test:docker:live-build` ile oluşturur, sonra iki live Docker koridoru için yeniden kullanır.
- Konteynır smoke çalıştırıcıları: `test:docker:openwebui`, `test:docker:onboard`, `test:docker:gateway-network`, `test:docker:mcp-channels` ve `test:docker:plugins`, bir veya daha fazla gerçek konteynır önyükler ve daha yüksek düzeyli integration yollarını doğrular.

Live-model Docker çalıştırıcıları ayrıca yalnızca gerekli CLI auth home dizinlerini bağlar (veya çalıştırma daraltılmamışsa desteklenenlerin hepsini), sonra harici-CLI OAuth'un ana makine auth deposunu değiştirmeden belirteçleri yenileyebilmesi için çalıştırma öncesinde bunları konteynır home dizinine kopyalar:

- Doğrudan modeller: `pnpm test:docker:live-models` (betik: `scripts/test-live-models-docker.sh`)
- ACP bind smoke: `pnpm test:docker:live-acp-bind` (betik: `scripts/test-live-acp-bind-docker.sh`)
- CLI backend smoke: `pnpm test:docker:live-cli-backend` (betik: `scripts/test-live-cli-backend-docker.sh`)
- Gateway + dev ajan: `pnpm test:docker:live-gateway` (betik: `scripts/test-live-gateway-models-docker.sh`)
- Open WebUI live smoke: `pnpm test:docker:openwebui` (betik: `scripts/e2e/openwebui-docker.sh`)
- Onboarding wizard (TTY, tam iskelet oluşturma): `pnpm test:docker:onboard` (betik: `scripts/e2e/onboard-docker.sh`)
- Gateway ağı (iki konteynır, WS auth + health): `pnpm test:docker:gateway-network` (betik: `scripts/e2e/gateway-network-docker.sh`)
- MCP channel bridge (tohumlanmış Gateway + stdio bridge + ham Claude notification-frame smoke): `pnpm test:docker:mcp-channels` (betik: `scripts/e2e/mcp-channels-docker.sh`)
- Plugins (yükleme smoke + `/plugin` takma adı + Claude-bundle restart semantiği): `pnpm test:docker:plugins` (betik: `scripts/e2e/plugins-docker.sh`)

Live-model Docker çalıştırıcıları ayrıca mevcut checkout'u salt okunur olarak bağlar ve
konteynır içinde geçici bir workdir'e aşamalar. Bu, çalışma zamanı
görüntüsünü ince tutarken yine de Vitest'i tam olarak yerel kaynak/config'inize karşı çalıştırır.
Aşama adımı, büyük yerel-only önbellekleri ve uygulama derleme çıktıları gibi
`.pnpm-store`, `.worktrees`, `__openclaw_vitest__` ve uygulamaya özgü `.build` veya
Gradle çıktı dizinlerini atlar; böylece Docker live çalıştırmaları
makineye özgü yapıtları kopyalamak için dakikalar harcamaz.
Ayrıca gateway live problarının konteynır içinde gerçek
Telegram/Discord/vb. channel worker'larını başlatmaması için `OPENCLAW_SKIP_CHANNELS=1` ayarlarlar.
`test:docker:live-models` yine de `pnpm test:live` çalıştırır; dolayısıyla
o Docker koridorundan gateway
live kapsamını daraltmanız veya hariç tutmanız gerektiğinde `OPENCLAW_LIVE_GATEWAY_*` değerlerini de geçirin.
`test:docker:openwebui`, daha yüksek seviyeli bir uyumluluk smoke testidir: OpenAI uyumlu HTTP uç noktaları etkinleştirilmiş bir
OpenClaw gateway konteynırı başlatır,
bu gateway'e karşı sabitlenmiş bir Open WebUI konteynırı başlatır, Open WebUI üzerinden oturum açar,
`/api/models` uç noktasının `openclaw/default` gösterdiğini doğrular, ardından
Open WebUI'nin `/api/chat/completions` proxy'si üzerinden gerçek bir sohbet isteği gönderir.
İlk çalıştırma belirgin şekilde daha yavaş olabilir; çünkü Docker'ın
Open WebUI görüntüsünü çekmesi gerekebilir ve Open WebUI kendi cold-start kurulumunu tamamlamak zorunda kalabilir.
Bu koridor kullanılabilir bir live model anahtarı bekler ve
Docker içinde çalıştırılan senaryolarda bunu sağlamak için birincil yol `OPENCLAW_PROFILE_FILE`
(varsayılan olarak `~/.profile`) olur.
Başarılı çalıştırmalar `{ "ok": true, "model":
"openclaw/default", ... }` gibi küçük bir JSON yükü yazdırır.
`test:docker:mcp-channels` kasıtlı olarak deterministiktir ve gerçek bir
Telegram, Discord veya iMessage hesabına ihtiyaç duymaz. Tohumlanmış bir Gateway
konteynırı önyükler, ardından `openclaw mcp serve` başlatan ikinci bir konteynır çalıştırır, sonra
gerçek stdio MCP bridge üzerinden yönlendirilmiş konuşma keşfini, döküm okumalarını, ek meta verisini,
live event queue davranışını, giden gönderim yönlendirmesini ve Claude tarzı channel +
izin bildirimlerini doğrular. Bildirim kontrolü,
bridge'in gerçekte ne yaydığını doğrulamak için ham stdio MCP frame'lerini doğrudan inceler; yalnızca belirli bir istemci SDK'sının neyi yüzeye çıkardığını değil.

Elle ACP düz dil thread smoke testi (CI değil):

- `bun scripts/dev/discord-acp-plain-language-smoke.ts --channel <discord-channel-id> ...`
- Bu betiği regresyon/hata ayıklama iş akışları için koruyun. ACP thread yönlendirme doğrulaması için tekrar gerekli olabilir, bu yüzden silmeyin.

Yararlı ortam değişkenleri:

- `OPENCLAW_CONFIG_DIR=...` (varsayılan: `~/.openclaw`) `/home/node/.openclaw` dizinine bağlanır
- `OPENCLAW_WORKSPACE_DIR=...` (varsayılan: `~/.openclaw/workspace`) `/home/node/.openclaw/workspace` dizinine bağlanır
- `OPENCLAW_PROFILE_FILE=...` (varsayılan: `~/.profile`) `/home/node/.profile` dizinine bağlanır ve testler çalıştırılmadan önce source edilir
- `OPENCLAW_DOCKER_CLI_TOOLS_DIR=...` (varsayılan: `~/.cache/openclaw/docker-cli-tools`) Docker içindeki önbelleklenmiş CLI kurulumları için `/home/node/.npm-global` dizinine bağlanır
- `$HOME` altındaki harici CLI auth dizinleri/dosyaları, `/host-auth...` altında salt okunur bağlanır, sonra testler başlamadan önce `/home/node/...` içine kopyalanır
  - Varsayılan dizinler: `.minimax`
  - Varsayılan dosyalar: `~/.codex/auth.json`, `~/.codex/config.toml`, `.claude.json`, `~/.claude/.credentials.json`, `~/.claude/settings.json`, `~/.claude/settings.local.json`
  - Daraltılmış provider çalıştırmaları yalnızca `OPENCLAW_LIVE_PROVIDERS` / `OPENCLAW_LIVE_GATEWAY_PROVIDERS` üzerinden çıkarılan gerekli dizinleri/dosyaları bağlar
  - Elle geçersiz kılmak için `OPENCLAW_DOCKER_AUTH_DIRS=all`, `OPENCLAW_DOCKER_AUTH_DIRS=none` veya `OPENCLAW_DOCKER_AUTH_DIRS=.claude,.codex` gibi virgüllü bir liste kullanın
- Çalıştırmayı daraltmak için `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...`
- Konteynır içindeki provider'ları filtrelemek için `OPENCLAW_LIVE_GATEWAY_PROVIDERS=...` / `OPENCLAW_LIVE_PROVIDERS=...`
- Kimlik bilgilerinin profil deposundan gelmesini sağlamak için `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` (env değil)
- Open WebUI smoke testi için gateway tarafından sunulan modeli seçmek üzere `OPENCLAW_OPENWEBUI_MODEL=...`
- Open WebUI smoke tarafından kullanılan nonce-check prompt'unu geçersiz kılmak için `OPENCLAW_OPENWEBUI_PROMPT=...`
- Sabitlenmiş Open WebUI görüntü etiketini geçersiz kılmak için `OPENWEBUI_IMAGE=...`

## Belge sağlama kontrolü

Belge düzenlemelerinden sonra docs kontrollerini çalıştırın: `pnpm check:docs`.
Sayfa içi başlık kontrollerine de ihtiyaç duyduğunuzda tam Mintlify anchor doğrulamasını çalıştırın: `pnpm docs:check-links:anchors`.

## Çevrimdışı regresyon (CI-güvenli)

Bunlar gerçek provider'lar olmadan “gerçek işlem hattısı” regresyonlarıdır:

- Gateway tool calling (sahte OpenAI, gerçek gateway + ajan döngüsü): `src/gateway/gateway.test.ts` (durum: "runs a mock OpenAI tool call end-to-end via gateway agent loop")
- Gateway wizard (WS `wizard.start`/`wizard.next`, config + auth enforced yazar): `src/gateway/gateway.test.ts` (durum: "runs wizard over ws and writes auth token config")

## Ajan güvenilirlik değerlendirmeleri (Skills)

Zaten “ajan güvenilirlik değerlendirmeleri” gibi davranan birkaç CI-güvenli testimiz var:

- Gerçek gateway + ajan döngüsü üzerinden sahte tool-calling (`src/gateway/gateway.test.ts`).
- Oturum kablolamasını ve config etkilerini doğrulayan uçtan uca wizard akışları (`src/gateway/gateway.test.ts`).

Skills için hâlâ eksik olanlar (bkz. [Skills](/tr/tools/skills)):

- **Karar verme:** prompt içinde Skills listelendiğinde, ajan doğru Skill'i seçiyor mu (veya ilgisiz olanlardan kaçınıyor mu)?
- **Uyumluluk:** ajan kullanımdan önce `SKILL.md` dosyasını okuyor ve gerekli adımları/argümanları izliyor mu?
- **İş akışı sözleşmeleri:** araç sırasını, oturum geçmişi devrini ve sandbox sınırlarını doğrulayan çok turlu senaryolar.

Gelecekteki değerlendirmeler önce deterministik kalmalıdır:

- Araç çağrılarını + sırasını, Skill dosyası okumalarını ve oturum kablolamasını doğrulamak için sahte provider'lar kullanan bir senaryo çalıştırıcısı.
- Skill odaklı küçük bir senaryo paketi (kullan vs kaçın, geçitleme, prompt injection).
- İsteğe bağlı live değerlendirmeler (isteğe bağlı, env-geçitli), ancak CI-güvenli paket yerleştikten sonra.

## Sözleşme testleri (plugin ve channel şekli)

Sözleşme testleri, kayıtlı her plugin ve channel'ın
arayüz sözleşmesine uyduğunu doğrular. Keşfedilen tüm plugin'ler üzerinde dolaşır ve
bir şekil ve davranış doğrulama paketi çalıştırırlar. Varsayılan `pnpm test` unit koridoru
bu paylaşılan seam ve smoke dosyalarını bilerek
atlar; paylaşılan channel veya provider yüzeylerine dokunduğunuzda sözleşme komutlarını
açıkça çalıştırın.

### Komutlar

- Tüm sözleşmeler: `pnpm test:contracts`
- Yalnızca channel sözleşmeleri: `pnpm test:contracts:channels`
- Yalnızca provider sözleşmeleri: `pnpm test:contracts:plugins`

### Channel sözleşmeleri

`src/channels/plugins/contracts/*.contract.test.ts` içinde bulunur:

- **plugin** - Temel plugin şekli (id, name, capabilities)
- **setup** - Kurulum wizard sözleşmesi
- **session-binding** - Oturum bağlama davranışı
- **outbound-payload** - Mesaj yükü yapısı
- **inbound** - Gelen mesaj işleme
- **actions** - Channel eylem işleyicileri
- **threading** - Thread ID işleme
- **directory** - Dizin/roster API
- **group-policy** - Grup ilkesi uygulaması

### Provider durum sözleşmeleri

`src/plugins/contracts/*.contract.test.ts` içinde bulunur.

- **status** - Channel durum probları
- **registry** - Plugin kayıt şekli

### Provider sözleşmeleri

`src/plugins/contracts/*.contract.test.ts` içinde bulunur:

- **auth** - Auth akışı sözleşmesi
- **auth-choice** - Auth seçimi/tercihi
- **catalog** - Model katalog API'si
- **discovery** - Plugin keşfi
- **loader** - Plugin yükleme
- **runtime** - Provider çalışma zamanı
- **shape** - Plugin şekli/arayüzü
- **wizard** - Kurulum wizard'ı

### Ne zaman çalıştırılmalı

- plugin-sdk export'larını veya alt yollarını değiştirdikten sonra
- Bir channel veya provider plugin'i ekledikten ya da değiştirdikten sonra
- Plugin kaydı veya keşfini yeniden düzenledikten sonra

Sözleşme testleri CI içinde çalışır ve gerçek API anahtarları gerektirmez.

## Regresyon ekleme (rehber)

Live içinde keşfedilen bir provider/model sorununu düzelttiğinizde:

- Mümkünse CI-güvenli bir regresyon ekleyin (provider'ı mock/stub yapın veya tam istek-şekli dönüşümünü yakalayın)
- Doğası gereği yalnızca live ise (rate limit, auth politikaları), live testi dar ve env değişkenleriyle isteğe bağlı tutun
- Hatayı yakalayan en küçük katmanı hedeflemeyi tercih edin:
  - provider istek dönüştürme/tekrar oynatma hatası → doğrudan modeller testi
  - gateway oturum/geçmiş/araç işlem hattısı hatası → gateway live smoke veya CI-güvenli gateway mock testi
- SecretRef traversal korkuluğu:
  - `src/secrets/exec-secret-ref-id-parity.test.ts`, kayıt meta verisinden SecretRef sınıfı başına örneklenmiş bir hedef türetir (`listSecretTargetRegistryEntries()`), sonra traversal-segment exec kimliklerinin reddedildiğini doğrular.
  - `src/secrets/target-registry-data.ts` içine yeni bir `includeInPlan` SecretRef hedef ailesi eklerseniz, o testte `classifyTargetClass` değerini güncelleyin. Test, yeni sınıfların sessizce atlanamaması için sınıflandırılmamış hedef kimliklerinde bilerek başarısız olur.
