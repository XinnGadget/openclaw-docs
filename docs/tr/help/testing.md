---
read_when:
    - Testleri yerel olarak veya CI içinde çalıştırma
    - Model/sağlayıcı hataları için regresyonlar ekleme
    - Gateway + ajan davranışını hata ayıklama
summary: 'Test kiti: birim/e2e/canlı paketleri, Docker çalıştırıcıları ve her testin neleri kapsadığı'
title: Test etme
x-i18n:
    generated_at: "2026-04-13T08:50:46Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3db91b4bc36f626cd014958ec66b08b9cecd9faaa20a5746cd3a49ad4b0b1c38
    source_path: help/testing.md
    workflow: 15
---

# Test etme

OpenClaw üç Vitest paketine (birim/entegrasyon, e2e, canlı) ve küçük bir Docker çalıştırıcıları kümesine sahiptir.

Bu belge, “nasıl test ediyoruz” kılavuzudur:

- Her paketin neyi kapsadığı (ve özellikle neyi _kapsamadığı)
- Yaygın iş akışları için hangi komutların çalıştırılacağı (yerel, push öncesi, hata ayıklama)
- Canlı testlerin kimlik bilgilerini nasıl bulduğu ve modelleri/sağlayıcıları nasıl seçtiği
- Gerçek dünyadaki model/sağlayıcı sorunları için regresyonların nasıl ekleneceği

## Hızlı başlangıç

Çoğu gün:

- Tam kapı (push öncesinde beklenir): `pnpm build && pnpm check && pnpm test`
- Güçlü bir makinede daha hızlı yerel tam paket çalıştırması: `pnpm test:max`
- Doğrudan Vitest izleme döngüsü: `pnpm test:watch`
- Doğrudan dosya hedefleme artık extension/channel yollarını da yönlendiriyor: `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`
- Tek bir hata üzerinde yineleme yapıyorsanız önce hedefli çalıştırmaları tercih edin.
- Docker destekli QA sitesi: `pnpm qa:lab:up`
- Linux VM destekli QA hattı: `pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline`

Testlere dokunduğunuzda veya daha fazla güven istediğinizde:

- Kapsama kapısı: `pnpm test:coverage`
- E2E paketi: `pnpm test:e2e`

Gerçek sağlayıcıları/modelleri hata ayıklarken (gerçek kimlik bilgileri gerekir):

- Canlı paket (modeller + Gateway araç/görsel probları): `pnpm test:live`
- Tek bir canlı dosyayı sessizce hedefleyin: `pnpm test:live -- src/agents/models.profiles.live.test.ts`

İpucu: yalnızca tek bir başarısız duruma ihtiyacınız olduğunda, aşağıda açıklanan allowlist ortam değişkenleriyle canlı testleri daraltmayı tercih edin.

## QA'ya özgü çalıştırıcılar

Bu komutlar, QA-lab gerçekçiliğine ihtiyaç duyduğunuzda ana test paketlerinin yanında yer alır:

- `pnpm openclaw qa suite`
  - Depo destekli QA senaryolarını doğrudan host üzerinde çalıştırır.
  - Varsayılan olarak seçili birden fazla senaryoyu yalıtılmış Gateway worker'larıyla paralel çalıştırır; en fazla 64 worker veya seçili senaryo sayısı kadar kullanır. Worker sayısını ayarlamak için `--concurrency <count>`, eski seri hat için ise `--concurrency 1` kullanın.
- `pnpm openclaw qa suite --runner multipass`
  - Aynı QA paketini tek kullanımlık bir Multipass Linux VM içinde çalıştırır.
  - Host üzerindeki `qa suite` ile aynı senaryo seçimi davranışını korur.
  - `qa suite` ile aynı sağlayıcı/model seçim bayraklarını yeniden kullanır.
  - Canlı çalıştırmalar, misafir için pratik olan desteklenen QA kimlik doğrulama girdilerini iletir:
    ortam tabanlı sağlayıcı anahtarları, QA canlı sağlayıcı yapılandırma yolu ve varsa `CODEX_HOME`.
  - Çıktı dizinleri depo kökü altında kalmalıdır; böylece misafir, bağlanan çalışma alanı üzerinden geri yazabilir.
  - Normal QA raporunu + özeti ve Multipass günlüklerini `.artifacts/qa-e2e/...` altına yazar.
- `pnpm qa:lab:up`
  - Operatör tarzı QA çalışmaları için Docker destekli QA sitesini başlatır.
- `pnpm openclaw qa matrix`
  - Matrix canlı QA hattını, tek kullanımlık Docker destekli bir Tuwunel homeserver karşısında çalıştırır.
  - `driver`, `sut`, `observer` olmak üzere üç geçici Matrix kullanıcısı ve bir özel oda sağlar; ardından gerçek Matrix Plugin ile SUT taşıması olarak bir QA Gateway alt süreci başlatır.
  - Varsayılan olarak sabitlenmiş kararlı Tuwunel imajı `ghcr.io/matrix-construct/tuwunel:v1.5.1` kullanılır. Farklı bir imajı test etmeniz gerektiğinde `OPENCLAW_QA_MATRIX_TUWUNEL_IMAGE` ile geçersiz kılın.
  - Matrix şu anda yalnızca `--credential-source env` destekler; çünkü hat geçici kullanıcıları yerel olarak oluşturur.
  - Bir Matrix QA raporu, özeti ve gözlemlenen olaylar artifact'ını `.artifacts/qa-e2e/...` altına yazar.
- `pnpm openclaw qa telegram`
  - Telegram canlı QA hattını, ortamdaki driver ve SUT bot token'larıyla gerçek bir özel grup karşısında çalıştırır.
  - `OPENCLAW_QA_TELEGRAM_GROUP_ID`, `OPENCLAW_QA_TELEGRAM_DRIVER_BOT_TOKEN` ve `OPENCLAW_QA_TELEGRAM_SUT_BOT_TOKEN` gerekir. Grup kimliği sayısal Telegram sohbet kimliği olmalıdır.
  - Paylaşılan havuz kimlik bilgileri için `--credential-source convex` destekler. Varsayılan olarak env modunu kullanın veya havuzlanmış kiralamalara geçmek için `OPENCLAW_QA_CREDENTIAL_SOURCE=convex` ayarlayın.
  - Aynı özel grupta iki farklı bot gerekir ve SUT botunun bir Telegram kullanıcı adı sunması gerekir.
  - Kararlı botlar arası gözlem için `@BotFather` içinde her iki bot için de Bot-to-Bot Communication Mode'u etkinleştirin ve driver botun grup bot trafiğini gözlemleyebildiğinden emin olun.
  - Bir Telegram QA raporu, özeti ve gözlemlenen mesajlar artifact'ını `.artifacts/qa-e2e/...` altına yazar.

Canlı taşıma hatları tek bir standart sözleşmeyi paylaşır; böylece yeni taşımalar sapma göstermez:

`qa-channel` geniş sentetik QA paketi olarak kalır ve canlı taşıma kapsam matriksinin bir parçası değildir.

| Hat      | Canary | Mention gating | Allowlist block | Üst düzey yanıt | Yeniden başlatma sonrası sürdürme | İleti dizisi takibi | İleti dizisi yalıtımı | Tepki gözlemi | Yardım komutu |
| -------- | ------ | -------------- | --------------- | --------------- | --------------------------------- | ------------------- | --------------------- | ------------- | ------------- |
| Matrix   | x      | x              | x               | x               | x                                 | x                   | x                     | x             |               |
| Telegram | x      |                |                 |                 |                                   |                     |                       |               | x             |

### Convex üzerinden paylaşılan Telegram kimlik bilgileri (v1)

`openclaw qa telegram` için `--credential-source convex` (veya `OPENCLAW_QA_CREDENTIAL_SOURCE=convex`) etkinleştirildiğinde, QA lab Convex destekli bir havuzdan özel bir kiralama alır, hat çalışırken bu kiralamaya Heartbeat gönderir ve kapanışta kiralamayı serbest bırakır.

Başvuru Convex proje iskeleti:

- `qa/convex-credential-broker/`

Gerekli ortam değişkenleri:

- `OPENCLAW_QA_CONVEX_SITE_URL` (örneğin `https://your-deployment.convex.site`)
- Seçilen rol için bir gizli anahtar:
  - `maintainer` için `OPENCLAW_QA_CONVEX_SECRET_MAINTAINER`
  - `ci` için `OPENCLAW_QA_CONVEX_SECRET_CI`
- Kimlik bilgisi rolü seçimi:
  - CLI: `--credential-role maintainer|ci`
  - Ortam varsayılanı: `OPENCLAW_QA_CREDENTIAL_ROLE` (varsayılan `maintainer`)

İsteğe bağlı ortam değişkenleri:

- `OPENCLAW_QA_CREDENTIAL_LEASE_TTL_MS` (varsayılan `1200000`)
- `OPENCLAW_QA_CREDENTIAL_HEARTBEAT_INTERVAL_MS` (varsayılan `30000`)
- `OPENCLAW_QA_CREDENTIAL_ACQUIRE_TIMEOUT_MS` (varsayılan `90000`)
- `OPENCLAW_QA_CREDENTIAL_HTTP_TIMEOUT_MS` (varsayılan `15000`)
- `OPENCLAW_QA_CONVEX_ENDPOINT_PREFIX` (varsayılan `/qa-credentials/v1`)
- `OPENCLAW_QA_CREDENTIAL_OWNER_ID` (isteğe bağlı izleme kimliği)
- `OPENCLAW_QA_ALLOW_INSECURE_HTTP=1`, yalnızca yerel geliştirme için loopback `http://` Convex URL'lerine izin verir.

`OPENCLAW_QA_CONVEX_SITE_URL` normal çalışmada `https://` kullanmalıdır.

Maintainer yönetici komutları (havuz ekleme/kaldırma/listeleme) özellikle `OPENCLAW_QA_CONVEX_SECRET_MAINTAINER` gerektirir.

Maintainer'lar için CLI yardımcıları:

```bash
pnpm openclaw qa credentials add --kind telegram --payload-file qa/telegram-credential.json
pnpm openclaw qa credentials list --kind telegram
pnpm openclaw qa credentials remove --credential-id <credential-id>
```

Betiklerde ve CI yardımcı araçlarında makine tarafından okunabilir çıktı için `--json` kullanın.

Varsayılan uç nokta sözleşmesi (`OPENCLAW_QA_CONVEX_SITE_URL` + `/qa-credentials/v1`):

- `POST /acquire`
  - İstek: `{ kind, ownerId, actorRole, leaseTtlMs, heartbeatIntervalMs }`
  - Başarı: `{ status: "ok", credentialId, leaseToken, payload, leaseTtlMs?, heartbeatIntervalMs? }`
  - Tükenmiş/yeniden denenebilir: `{ status: "error", code: "POOL_EXHAUSTED" | "NO_CREDENTIAL_AVAILABLE", ... }`
- `POST /heartbeat`
  - İstek: `{ kind, ownerId, actorRole, credentialId, leaseToken, leaseTtlMs }`
  - Başarı: `{ status: "ok" }` (veya boş `2xx`)
- `POST /release`
  - İstek: `{ kind, ownerId, actorRole, credentialId, leaseToken }`
  - Başarı: `{ status: "ok" }` (veya boş `2xx`)
- `POST /admin/add` (yalnızca maintainer gizli anahtarı)
  - İstek: `{ kind, actorId, payload, note?, status? }`
  - Başarı: `{ status: "ok", credential }`
- `POST /admin/remove` (yalnızca maintainer gizli anahtarı)
  - İstek: `{ credentialId, actorId }`
  - Başarı: `{ status: "ok", changed, credential }`
  - Etkin kiralama koruması: `{ status: "error", code: "LEASE_ACTIVE", ... }`
- `POST /admin/list` (yalnızca maintainer gizli anahtarı)
  - İstek: `{ kind?, status?, includePayload?, limit? }`
  - Başarı: `{ status: "ok", credentials, count }`

Telegram türü için yük biçimi:

- `{ groupId: string, driverToken: string, sutToken: string }`
- `groupId` sayısal bir Telegram sohbet kimliği dizesi olmalıdır.
- `admin/add`, `kind: "telegram"` için bu biçimi doğrular ve hatalı biçimlendirilmiş yükleri reddeder.

### QA'ya bir kanal ekleme

Bir kanalı markdown QA sistemine eklemek tam olarak iki şey gerektirir:

1. Kanal için bir taşıma bağdaştırıcısı.
2. Kanal sözleşmesini çalıştıran bir senaryo paketi.

Paylaşılan `qa-lab` çalıştırıcısı akışı sahiplenebiliyorsa, kanala özgü bir QA çalıştırıcısı eklemeyin.

`qa-lab` paylaşılan mekanikleri sahiplenir:

- paket başlatma ve kapatma
- worker eşzamanlılığı
- artifact yazımı
- rapor üretimi
- senaryo yürütme
- eski `qa-channel` senaryoları için uyumluluk takma adları

Kanal bağdaştırıcısı taşıma sözleşmesini sahiplenir:

- Gateway'nin bu taşıma için nasıl yapılandırıldığı
- hazır oluşun nasıl kontrol edildiği
- gelen olayların nasıl enjekte edildiği
- giden mesajların nasıl gözlemlendiği
- transkriptlerin ve normalize edilmiş taşıma durumunun nasıl sunulduğu
- taşıma destekli eylemlerin nasıl yürütüldüğü
- taşımaya özgü sıfırlama veya temizliğin nasıl ele alındığı

Yeni bir kanal için minimum benimseme çıtası şudur:

1. Taşıma bağdaştırıcısını paylaşılan `qa-lab` seam üzerinde uygulayın.
2. Bağdaştırıcıyı taşıma kayıt defterine kaydedin.
3. Taşımaya özgü mekanikleri bağdaştırıcı veya kanal harness'i içinde tutun.
4. `qa/scenarios/` altında markdown senaryoları yazın veya uyarlayın.
5. Yeni senaryolar için genel senaryo yardımcılarını kullanın.
6. Depo kasıtlı bir geçiş yapmıyorsa mevcut uyumluluk takma adlarını çalışır durumda tutun.

Karar kuralı katıdır:

- Davranış bir kez `qa-lab` içinde ifade edilebiliyorsa, `qa-lab` içine koyun.
- Davranış bir kanal taşımasına bağlıysa, onu o bağdaştırıcıda veya Plugin harness'inde tutun.
- Bir senaryo birden fazla kanalın kullanabileceği yeni bir yetenek gerektiriyorsa, `suite.ts` içinde kanala özgü bir dal yerine genel bir yardımcı ekleyin.
- Bir davranış yalnızca bir taşıma için anlamlıysa, senaryoyu taşımaya özgü tutun ve bunu senaryo sözleşmesinde açık hale getirin.

Yeni senaryolar için tercih edilen genel yardımcı adları şunlardır:

- `waitForTransportReady`
- `waitForChannelReady`
- `injectInboundMessage`
- `injectOutboundMessage`
- `waitForTransportOutboundMessage`
- `waitForChannelOutboundMessage`
- `waitForNoTransportOutbound`
- `getTransportSnapshot`
- `readTransportMessage`
- `readTransportTranscript`
- `formatTransportTranscript`
- `resetTransport`

Mevcut senaryolar için uyumluluk takma adları kullanılabilir olmaya devam eder; bunlar arasında şunlar vardır:

- `waitForQaChannelReady`
- `waitForOutboundMessage`
- `waitForNoOutbound`
- `formatConversationTranscript`
- `resetBus`

Yeni kanal çalışmaları genel yardımcı adlarını kullanmalıdır.
Uyumluluk takma adları bir “flag day” geçişini önlemek içindir; yeni senaryo yazımında model olarak kullanılmaları için değil.

## Test paketleri (ne nerede çalışır)

Paketleri “artan gerçekçilik” (ve artan oynaklık/maliyet) olarak düşünün:

### Birim / entegrasyon (varsayılan)

- Komut: `pnpm test`
- Yapılandırma: mevcut kapsamlı Vitest projeleri üzerinde on adet sıralı shard çalıştırması (`vitest.full-*.config.ts`)
- Dosyalar: `src/**/*.test.ts`, `packages/**/*.test.ts`, `test/**/*.test.ts` altındaki core/birim envanterleri ve `vitest.unit.config.ts` tarafından kapsanan allowlist içindeki `ui` Node testleri
- Kapsam:
  - Saf birim testleri
  - Süreç içi entegrasyon testleri (Gateway auth, yönlendirme, araçlar, ayrıştırma, yapılandırma)
  - Bilinen hatalar için deterministik regresyonlar
- Beklentiler:
  - CI içinde çalışır
  - Gerçek anahtarlar gerekmez
  - Hızlı ve kararlı olmalıdır
- Projeler notu:
  - Hedeflenmemiş `pnpm test` artık tek bir devasa yerel root-project süreci yerine on bir küçük shard yapılandırması (`core-unit-src`, `core-unit-security`, `core-unit-ui`, `core-unit-support`, `core-support-boundary`, `core-contracts`, `core-bundled`, `core-runtime`, `agentic`, `auto-reply`, `extensions`) çalıştırır. Bu, yüklü makinelerde tepe RSS'yi azaltır ve auto-reply/extension işlerinin ilgisiz paketleri aç bırakmasını önler.
  - `pnpm test --watch` hâlâ yerel root `vitest.config.ts` proje grafiğini kullanır; çünkü çoklu shard izleme döngüsü pratik değildir.
  - `pnpm test`, `pnpm test:watch` ve `pnpm test:perf:imports`, açık dosya/dizin hedeflerini önce kapsamlı hatlar üzerinden yönlendirir; böylece `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts` tam root proje başlatma maliyetini ödemez.
  - `pnpm test:changed`, fark yalnızca yönlendirilebilir kaynak/test dosyalarına dokunduğunda değişen git yollarını aynı kapsamlı hatlara genişletir; yapılandırma/kurulum düzenlemeleri ise yine geniş root-project yeniden çalıştırmasına düşer.
  - Ajanlar, komutlar, plugin'ler, auto-reply yardımcıları, `plugin-sdk` ve benzeri saf yardımcı alanlardaki import açısından hafif birim testleri, `test/setup-openclaw-runtime.ts` dosyasını atlayan `unit-fast` hattı üzerinden yönlendirilir; durum bilgili/çalışma zamanı açısından ağır dosyalar mevcut hatlarda kalır.
  - Seçilmiş `plugin-sdk` ve `commands` yardımcı kaynak dosyaları da changed-mode çalıştırmalarını bu hafif hatlardaki açık kardeş testlere eşler; böylece yardımcı düzenlemeleri o dizin için tam ağır paketi yeniden çalıştırmaz.
  - `auto-reply` artık üç özel bölüme sahiptir: üst düzey core yardımcıları, üst düzey `reply.*` entegrasyon testleri ve `src/auto-reply/reply/**` alt ağacı. Bu, en ağır yanıt harness işini ucuz status/chunk/token testlerinden uzak tutar.
- Gömülü çalıştırıcı notu:
  - Mesaj aracı keşif girdilerini veya Compaction çalışma zamanı bağlamını değiştirdiğinizde, her iki kapsama düzeyini de koruyun.
  - Saf yönlendirme/normalleştirme sınırları için odaklı yardımcı regresyonları ekleyin.
  - Ayrıca gömülü çalıştırıcı entegrasyon paketlerini de sağlıklı tutun:
    `src/agents/pi-embedded-runner/compact.hooks.test.ts`,
    `src/agents/pi-embedded-runner/run.overflow-compaction.test.ts` ve
    `src/agents/pi-embedded-runner/run.overflow-compaction.loop.test.ts`.
  - Bu paketler, kapsamlı kimliklerin ve Compaction davranışının gerçek `run.ts` / `compact.ts` yolları üzerinden akmaya devam ettiğini doğrular; yalnızca yardımcı testler bu entegrasyon yolları için yeterli bir ikame değildir.
- Havuz notu:
  - Temel Vitest yapılandırması artık varsayılan olarak `threads` kullanır.
  - Paylaşılan Vitest yapılandırması ayrıca `isolate: false` ayarlar ve root projeleri, e2e ve canlı yapılandırmalar boyunca yalıtılmamış çalıştırıcıyı kullanır.
  - Root UI hattı `jsdom` kurulumunu ve optimizer'ını korur, ancak artık o da paylaşılan yalıtılmamış çalıştırıcı üzerinde çalışır.
  - Her `pnpm test` shard'ı, paylaşılan Vitest yapılandırmasından aynı `threads` + `isolate: false` varsayılanlarını devralır.
  - Paylaşılan `scripts/run-vitest.mjs` başlatıcısı artık büyük yerel çalıştırmalar sırasında V8 derleme churn'ünü azaltmak için varsayılan olarak Vitest alt Node süreçlerine `--no-maglev` de ekler. Stok V8 davranışıyla karşılaştırma yapmanız gerekiyorsa `OPENCLAW_VITEST_ENABLE_MAGLEV=1` ayarlayın.
- Hızlı yerel yineleme notu:
  - `pnpm test:changed`, değişen yollar daha küçük bir pakete temiz biçimde eşlendiğinde kapsamlı hatlar üzerinden yönlendirir.
  - `pnpm test:max` ve `pnpm test:changed:max` aynı yönlendirme davranışını korur; yalnızca daha yüksek bir worker sınırıyla.
  - Yerel worker otomatik ölçekleme artık kasıtlı olarak daha muhafazakârdır ve host yük ortalaması zaten yüksek olduğunda da geri çekilir; böylece aynı anda birden çok Vitest çalıştırması varsayılan olarak daha az zarar verir.
  - Temel Vitest yapılandırması, test bağlantıları değiştiğinde changed-mode yeniden çalıştırmaların doğru kalması için projeleri/yapılandırma dosyalarını `forceRerunTriggers` olarak işaretler.
  - Yapılandırma, desteklenen host'larda `OPENCLAW_VITEST_FS_MODULE_CACHE` özelliğini etkin tutar; doğrudan profil oluşturma için açık bir önbellek konumu istiyorsanız `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/abs/path` ayarlayın.
- Performans hata ayıklama notu:
  - `pnpm test:perf:imports`, Vitest import süresi raporlamasını ve import dökümü çıktısını etkinleştirir.
  - `pnpm test:perf:imports:changed`, aynı profil görünümünü `origin/main` sonrasındaki değişen dosyalarla sınırlar.
- `pnpm test:perf:changed:bench -- --ref <git-ref>`, ilgili commit farkı için yönlendirilmiş `test:changed` ile yerel root-project yolunu karşılaştırır ve duvar saati ile macOS maksimum RSS'yi yazdırır.
- `pnpm test:perf:changed:bench -- --worktree`, mevcut kirli ağacı değişen dosya listesini `scripts/test-projects.mjs` ve root Vitest yapılandırması üzerinden yönlendirerek kıyaslar.
  - `pnpm test:perf:profile:main`, Vitest/Vite başlatma ve dönüştürme yükü için bir main-thread CPU profili yazar.
  - `pnpm test:perf:profile:runner`, dosya paralelliği devre dışıyken birim paketi için runner CPU+heap profilleri yazar.

### E2E (Gateway smoke)

- Komut: `pnpm test:e2e`
- Yapılandırma: `vitest.e2e.config.ts`
- Dosyalar: `src/**/*.e2e.test.ts`, `test/**/*.e2e.test.ts`
- Çalışma zamanı varsayılanları:
  - Depodaki geri kalanla uyumlu olarak Vitest `threads` ve `isolate: false` kullanır.
  - Uyarlanabilir worker'lar kullanır (CI: en fazla 2, yerel: varsayılan 1).
  - Konsol G/Ç yükünü azaltmak için varsayılan olarak sessiz modda çalışır.
- Yararlı geçersiz kılmalar:
  - Worker sayısını zorlamak için `OPENCLAW_E2E_WORKERS=<n>` (üst sınır 16).
  - Ayrıntılı konsol çıktısını yeniden etkinleştirmek için `OPENCLAW_E2E_VERBOSE=1`.
- Kapsam:
  - Çok örnekli Gateway uçtan uca davranışı
  - WebSocket/HTTP yüzeyleri, Node eşleştirme ve daha ağır ağ çalışmaları
- Beklentiler:
  - CI içinde çalışır (boru hattında etkinleştirildiğinde)
  - Gerçek anahtarlar gerekmez
  - Birim testlerinden daha fazla hareketli parçaya sahiptir (daha yavaş olabilir)

### E2E: OpenShell backend smoke

- Komut: `pnpm test:e2e:openshell`
- Dosya: `test/openshell-sandbox.e2e.test.ts`
- Kapsam:
  - Docker aracılığıyla host üzerinde yalıtılmış bir OpenShell Gateway başlatır
  - Geçici bir yerel Dockerfile'dan bir sandbox oluşturur
  - OpenClaw'ın OpenShell backend'ini gerçek `sandbox ssh-config` + SSH exec üzerinden çalıştırır
  - Uzak-kanonik dosya sistemi davranışını sandbox fs bridge üzerinden doğrular
- Beklentiler:
  - Yalnızca isteğe bağlıdır; varsayılan `pnpm test:e2e` çalıştırmasının parçası değildir
  - Yerel bir `openshell` CLI ve çalışan bir Docker daemon gerektirir
  - Yalıtılmış `HOME` / `XDG_CONFIG_HOME` kullanır, ardından test Gateway'ini ve sandbox'ı yok eder
- Yararlı geçersiz kılmalar:
  - Geniş e2e paketini elle çalıştırırken testi etkinleştirmek için `OPENCLAW_E2E_OPENSHELL=1`
  - Varsayılan olmayan bir CLI ikilisine veya sarmalayıcı betiğe işaret etmek için `OPENCLAW_E2E_OPENSHELL_COMMAND=/path/to/openshell`

### Canlı (gerçek sağlayıcılar + gerçek modeller)

- Komut: `pnpm test:live`
- Yapılandırma: `vitest.live.config.ts`
- Dosyalar: `src/**/*.live.test.ts`
- Varsayılan: `pnpm test:live` tarafından **etkinleştirilir** (`OPENCLAW_LIVE_TEST=1` ayarlar)
- Kapsam:
  - “Bu sağlayıcı/model bugün gerçek kimlik bilgileriyle gerçekten çalışıyor mu?”
  - Sağlayıcı biçim değişikliklerini, araç çağırma tuhaflıklarını, auth sorunlarını ve oran sınırı davranışını yakalar
- Beklentiler:
  - Tasarım gereği CI için kararlı değildir (gerçek ağlar, gerçek sağlayıcı politikaları, kotalar, kesintiler)
  - Paraya mal olur / oran sınırlarını kullanır
  - “Her şeyi” çalıştırmak yerine daraltılmış alt kümeleri çalıştırmak tercih edilir
- Canlı çalıştırmalar eksik API anahtarlarını almak için `~/.profile` dosyasını kaynak olarak yükler.
- Varsayılan olarak canlı çalıştırmalar yine de `HOME` dizinini yalıtır ve yapılandırma/auth materyalini geçici bir test home'una kopyalar; böylece birim fixture'ları gerçek `~/.openclaw` dizininizi değiştiremez.
- Canlı testlerin gerçek home dizininizi kullanmasını özellikle istediğinizde yalnızca `OPENCLAW_LIVE_USE_REAL_HOME=1` ayarlayın.
- `pnpm test:live` artık daha sessiz bir modu varsayılan yapar: `[live] ...` ilerleme çıktısını korur, ancak ek `~/.profile` bildirimini bastırır ve Gateway bootstrap günlükleri/Bonjour gürültüsünü susturur. Tam başlangıç günlüklerini geri istiyorsanız `OPENCLAW_LIVE_TEST_QUIET=0` ayarlayın.
- API anahtarı rotasyonu (sağlayıcıya özgü): virgül/noktalı virgül biçiminde `*_API_KEYS` veya `*_API_KEY_1`, `*_API_KEY_2` ayarlayın (örneğin `OPENAI_API_KEYS`, `ANTHROPIC_API_KEYS`, `GEMINI_API_KEYS`) ya da canlıya özgü geçersiz kılma için `OPENCLAW_LIVE_*_KEY`; testler oran sınırı yanıtlarında yeniden dener.
- İlerleme/Heartbeat çıktısı:
  - Canlı paketler artık stderr'e ilerleme satırları yazar; böylece uzun sağlayıcı çağrıları, Vitest konsol yakalaması sessiz olsa bile görünür biçimde aktif kalır.
  - `vitest.live.config.ts`, Vitest konsol müdahalesini devre dışı bırakır; böylece sağlayıcı/Gateway ilerleme satırları canlı çalıştırmalar sırasında anında akar.
  - Doğrudan model Heartbeat'lerini `OPENCLAW_LIVE_HEARTBEAT_MS` ile ayarlayın.
  - Gateway/probe Heartbeat'lerini `OPENCLAW_LIVE_GATEWAY_HEARTBEAT_MS` ile ayarlayın.

## Hangi paketi çalıştırmalıyım?

Bu karar tablosunu kullanın:

- Mantık/testler düzenleniyorsa: `pnpm test` çalıştırın (ve çok şey değiştirdiyseniz `pnpm test:coverage`)
- Gateway ağ iletişimine / WS protokolüne / eşleştirmeye dokunuyorsanız: `pnpm test:e2e` ekleyin
- “Botum çalışmıyor” / sağlayıcıya özgü arızalar / araç çağırma sorunlarını hata ayıklıyorsanız: daraltılmış bir `pnpm test:live` çalıştırın

## Canlı: Android Node yetenek taraması

- Test: `src/gateway/android-node.capabilities.live.test.ts`
- Betik: `pnpm android:test:integration`
- Amaç: bağlı bir Android Node tarafından şu anda **duyurulan her komutu** çağırmak ve komut sözleşmesi davranışını doğrulamak.
- Kapsam:
  - Ön koşullu/manuel kurulum (paket uygulamayı kurmaz/çalıştırmaz/eşleştirmez).
  - Seçilen Android Node için komut bazında Gateway `node.invoke` doğrulaması.
- Gerekli ön kurulum:
  - Android uygulaması zaten Gateway'ye bağlanmış ve eşleştirilmiş olmalıdır.
  - Uygulama ön planda tutulmalıdır.
  - Başarılı olmasını beklediğiniz yetenekler için izinler/yakalama onayı verilmiş olmalıdır.
- İsteğe bağlı hedef geçersiz kılmaları:
  - `OPENCLAW_ANDROID_NODE_ID` veya `OPENCLAW_ANDROID_NODE_NAME`.
  - `OPENCLAW_ANDROID_GATEWAY_URL` / `OPENCLAW_ANDROID_GATEWAY_TOKEN` / `OPENCLAW_ANDROID_GATEWAY_PASSWORD`.
- Tam Android kurulum ayrıntıları: [Android Uygulaması](/tr/platforms/android)

## Canlı: model smoke (profil anahtarları)

Canlı testler, arızaları izole edebilmek için iki katmana ayrılmıştır:

- “Doğrudan model”, sağlayıcının/modelin verilen anahtarla en azından yanıt verebildiğini söyler.
- “Gateway smoke”, bu model için tam Gateway+ajan hattının çalıştığını söyler (oturumlar, geçmiş, araçlar, sandbox ilkesi vb.).

### Katman 1: Doğrudan model tamamlama (Gateway yok)

- Test: `src/agents/models.profiles.live.test.ts`
- Amaç:
  - Keşfedilen modelleri listelemek
  - Kimlik bilgileriniz olan modelleri seçmek için `getApiKeyForModel` kullanmak
  - Model başına küçük bir tamamlama çalıştırmak (ve gerektiğinde hedefli regresyonlar)
- Nasıl etkinleştirilir:
  - `pnpm test:live` (veya Vitest doğrudan çağrılıyorsa `OPENCLAW_LIVE_TEST=1`)
- Bu paketi gerçekten çalıştırmak için `OPENCLAW_LIVE_MODELS=modern` (veya `all`, modern için takma ad) ayarlayın; aksi halde `pnpm test:live` odağını Gateway smoke üzerinde tutmak için bu paket atlanır
- Modeller nasıl seçilir:
  - Modern allowlist'i çalıştırmak için `OPENCLAW_LIVE_MODELS=modern` (Opus/Sonnet 4.6+, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.7, Grok 4)
  - `OPENCLAW_LIVE_MODELS=all`, modern allowlist için bir takma addır
  - veya `OPENCLAW_LIVE_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,..."` (virgülle ayrılmış allowlist)
  - Modern/all taramaları varsayılan olarak özenle seçilmiş yüksek sinyalli bir üst sınır kullanır; kapsamlı bir modern tarama için `OPENCLAW_LIVE_MAX_MODELS=0` veya daha küçük bir üst sınır için pozitif bir sayı ayarlayın.
- Sağlayıcılar nasıl seçilir:
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity,google-gemini-cli"` (virgülle ayrılmış allowlist)
- Anahtarlar nereden gelir:
  - Varsayılan olarak: profil deposu ve env geri dönüşleri
  - Yalnızca **profil deposunu** zorunlu kılmak için `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` ayarlayın
- Bunun var olma nedeni:
  - “Sağlayıcı API'si bozuk / anahtar geçersiz” ile “Gateway ajan hattı bozuk” durumlarını ayırır
  - Küçük, yalıtılmış regresyonlar içerir (örnek: OpenAI Responses/Codex Responses reasoning replay + araç çağrısı akışları)

### Katman 2: Gateway + geliştirme ajanı smoke (`@openclaw` gerçekte ne yapıyor)

- Test: `src/gateway/gateway-models.profiles.live.test.ts`
- Amaç:
  - Süreç içi bir Gateway başlatmak
  - Bir `agent:dev:*` oturumu oluşturmak/düzeltmek (çalıştırma başına model geçersiz kılma)
  - Anahtarlı modeller üzerinde dolaşmak ve şunları doğrulamak:
    - “anlamlı” yanıt (araç yok)
    - gerçek bir araç çağrısının çalışması (`read` probe)
    - isteğe bağlı ek araç probları (`exec+read` probe)
    - OpenAI regresyon yollarının (yalnızca araç çağrısı → takip) çalışmaya devam etmesi
- Probe ayrıntıları (böylece hataları hızlıca açıklayabilirsiniz):
  - `read` probe: test, çalışma alanına nonce içeren bir dosya yazar ve ajandan bu dosyayı `read` etmesini ve nonce'u geri yankılamasını ister.
  - `exec+read` probe: test, ajandan geçici bir dosyaya nonce yazmak için `exec` kullanmasını, ardından bunu tekrar `read` etmesini ister.
  - image probe: test, oluşturulmuş bir PNG (kedi + rastgele kod) ekler ve modelin `cat <CODE>` döndürmesini bekler.
  - Uygulama başvurusu: `src/gateway/gateway-models.profiles.live.test.ts` ve `src/gateway/live-image-probe.ts`.
- Nasıl etkinleştirilir:
  - `pnpm test:live` (veya Vitest doğrudan çağrılıyorsa `OPENCLAW_LIVE_TEST=1`)
- Modeller nasıl seçilir:
  - Varsayılan: modern allowlist (Opus/Sonnet 4.6+, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.7, Grok 4)
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all`, modern allowlist için bir takma addır
  - Ya da daraltmak için `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"` (veya virgülle ayrılmış liste) ayarlayın
  - Modern/all Gateway taramaları varsayılan olarak özenle seçilmiş yüksek sinyalli bir üst sınır kullanır; kapsamlı bir modern tarama için `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=0` veya daha küçük bir üst sınır için pozitif bir sayı ayarlayın.
- Sağlayıcılar nasıl seçilir (“her şeyi OpenRouter” yapmaktan kaçının):
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,google-gemini-cli,openai,anthropic,zai,minimax"` (virgülle ayrılmış allowlist)
- Araç + görsel probları bu canlı testte her zaman açıktır:
  - `read` probe + `exec+read` probe (araç stresi)
  - model görsel girdi desteği sunduğunda image probe çalışır
  - Akış (üst düzey):
    - Test, “CAT” + rastgele kod içeren küçük bir PNG üretir (`src/gateway/live-image-probe.ts`)
    - Bunu `agent` üzerinden `attachments: [{ mimeType: "image/png", content: "<base64>" }]` ile gönderir
    - Gateway ekleri `images[]` içine ayrıştırır (`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`)
    - Gömülü ajan çok kipli bir kullanıcı mesajını modele iletir
    - Doğrulama: yanıt `cat` + kodu içerir (OCR toleransı: küçük hatalara izin verilir)

İpucu: makinenizde neyi test edebileceğinizi görmek için (ve tam `provider/model` kimlikleri için) şunu çalıştırın:

```bash
openclaw models list
openclaw models list --json
```

## Canlı: CLI backend smoke (Claude, Codex, Gemini veya diğer yerel CLI'lar)

- Test: `src/gateway/gateway-cli-backend.live.test.ts`
- Amaç: Gateway + ajan hattını, varsayılan yapılandırmanıza dokunmadan yerel bir CLI backend kullanarak doğrulamak.
- Backend'e özgü smoke varsayılanları, sahibi olan extension'ın `cli-backend.ts` tanımıyla birlikte bulunur.
- Etkinleştirme:
  - `pnpm test:live` (veya Vitest doğrudan çağrılıyorsa `OPENCLAW_LIVE_TEST=1`)
  - `OPENCLAW_LIVE_CLI_BACKEND=1`
- Varsayılanlar:
  - Varsayılan sağlayıcı/model: `claude-cli/claude-sonnet-4-6`
  - Komut/argüman/görsel davranışı, sahibi olan CLI backend Plugin metadatasından gelir.
- Geçersiz kılmalar (isteğe bağlı):
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4"`
  - `OPENCLAW_LIVE_CLI_BACKEND_COMMAND="/full/path/to/codex"`
  - `OPENCLAW_LIVE_CLI_BACKEND_ARGS='["exec","--json","--color","never","--sandbox","read-only","--skip-git-repo-check"]'`
  - Gerçek bir görsel eki göndermek için `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_PROBE=1` (yollar prompt içine enjekte edilir).
  - Görsel dosya yollarını prompt enjeksiyonu yerine CLI argümanları olarak geçirmek için `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_ARG="--image"`.
  - `IMAGE_ARG` ayarlandığında görsel argümanlarının nasıl geçirileceğini kontrol etmek için `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_MODE="repeat"` (veya `"list"`).
  - İkinci bir tur göndermek ve resume akışını doğrulamak için `OPENCLAW_LIVE_CLI_BACKEND_RESUME_PROBE=1`.
  - Varsayılan Claude Sonnet -> Opus aynı oturum sürekliliği probe'unu devre dışı bırakmak için `OPENCLAW_LIVE_CLI_BACKEND_MODEL_SWITCH_PROBE=0` (seçilen model bir geçiş hedefini desteklediğinde bunu zorla açmak için `1` ayarlayın).

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

Tek sağlayıcılı Docker tarifleri:

```bash
pnpm test:docker:live-cli-backend:claude
pnpm test:docker:live-cli-backend:claude-subscription
pnpm test:docker:live-cli-backend:codex
pnpm test:docker:live-cli-backend:gemini
```

Notlar:

- Docker çalıştırıcısı `scripts/test-live-cli-backend-docker.sh` konumundadır.
- Canlı CLI-backend smoke'u depo Docker imajı içinde root olmayan `node` kullanıcısı olarak çalıştırır.
- Sahibi olan extension'dan CLI smoke metadata'sını çözümler, ardından eşleşen Linux CLI paketini (`@anthropic-ai/claude-code`, `@openai/codex` veya `@google/gemini-cli`) önbelleğe alınmış yazılabilir `OPENCLAW_DOCKER_CLI_TOOLS_DIR` önekine kurar (varsayılan: `~/.cache/openclaw/docker-cli-tools`).
- `pnpm test:docker:live-cli-backend:claude-subscription`, ya `~/.claude/.credentials.json` içindeki `claudeAiOauth.subscriptionType` üzerinden ya da `claude setup-token` içinden `CLAUDE_CODE_OAUTH_TOKEN` aracılığıyla taşınabilir Claude Code abonelik OAuth'u gerektirir. Önce Docker içinde doğrudan `claude -p` komutunu doğrular, ardından Anthropic API anahtarı env değişkenlerini korumadan iki Gateway CLI-backend turu çalıştırır. Bu abonelik hattı, Claude şu anda üçüncü taraf uygulama kullanımını normal abonelik planı sınırları yerine ek kullanım faturalandırması üzerinden yönlendirdiği için Claude MCP/araç ve görsel problarını varsayılan olarak devre dışı bırakır.
- Canlı CLI-backend smoke artık Claude, Codex ve Gemini için aynı uçtan uca akışı çalıştırır: metin turu, görsel sınıflandırma turu, ardından Gateway CLI üzerinden doğrulanan MCP `cron` araç çağrısı.
- Claude'un varsayılan smoke'u ayrıca oturumu Sonnet'ten Opus'a geçirir ve devam eden oturumun önceki bir notu hâlâ hatırladığını doğrular.

## Canlı: ACP bind smoke (`/acp spawn ... --bind here`)

- Test: `src/gateway/gateway-acp-bind.live.test.ts`
- Amaç: gerçek bir ACP ajanıyla gerçek ACP konuşma-bind akışını doğrulamak:
  - `/acp spawn <agent> --bind here` gönder
  - sentetik bir message-channel konuşmasını yerinde bağla
  - aynı konuşmada normal bir takip mesajı gönder
  - takibin bağlı ACP oturum transkriptine ulaştığını doğrula
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
  - Bu hat, testlerin haricen teslim ediyormuş gibi yapmadan message-channel bağlamı ekleyebilmesi için admin-only sentetik originating-route alanlarıyla Gateway `chat.send` yüzeyini kullanır.
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND` ayarlanmamışsa, test seçilen ACP harness ajanı için gömülü `acpx` Plugin'inin yerleşik ajan kayıt defterini kullanır.

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

Tek ajanlı Docker tarifleri:

```bash
pnpm test:docker:live-acp-bind:claude
pnpm test:docker:live-acp-bind:codex
pnpm test:docker:live-acp-bind:gemini
```

Docker notları:

- Docker çalıştırıcısı `scripts/test-live-acp-bind-docker.sh` konumundadır.
- Varsayılan olarak ACP bind smoke'u tüm desteklenen canlı CLI ajanlarına sırayla karşı çalıştırır: `claude`, `codex`, ardından `gemini`.
- Matrisi daraltmak için `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude`, `OPENCLAW_LIVE_ACP_BIND_AGENTS=codex` veya `OPENCLAW_LIVE_ACP_BIND_AGENTS=gemini` kullanın.
- `~/.profile` dosyasını kaynak olarak yükler, eşleşen CLI auth materyalini container içine hazırlar, `acpx`'i yazılabilir bir npm önekine kurar, sonra istenen canlı CLI'yı (`@anthropic-ai/claude-code`, `@openai/codex` veya `@google/gemini-cli`) eksikse kurar.
- Docker içinde çalıştırıcı `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=$HOME/.npm-global/bin/acpx` ayarlar; böylece acpx, kaynak olarak yüklenen profildeki sağlayıcı env değişkenlerini alt harness CLI için kullanılabilir tutar.

## Canlı: Codex app-server harness smoke

- Amaç: Plugin sahibi olunan Codex harness'i normal Gateway
  `agent` yöntemi üzerinden doğrulamak:
  - paketlenmiş `codex` Plugin'ini yüklemek
  - `OPENCLAW_AGENT_RUNTIME=codex` seçmek
  - `codex/gpt-5.4` için ilk Gateway ajan turunu göndermek
  - aynı OpenClaw oturumuna ikinci bir tur göndermek ve app-server
    thread'inin devam edebildiğini doğrulamak
  - `/codex status` ve `/codex models` komutlarını aynı Gateway komutu
    yolu üzerinden çalıştırmak
- Test: `src/gateway/gateway-codex-harness.live.test.ts`
- Etkinleştirme: `OPENCLAW_LIVE_CODEX_HARNESS=1`
- Varsayılan model: `codex/gpt-5.4`
- İsteğe bağlı görsel probe: `OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=1`
- İsteğe bağlı MCP/araç probe: `OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=1`
- Smoke, bozuk bir Codex
  harness'inin sessizce PI'ya geri düşerek başarılı olamaması için `OPENCLAW_AGENT_HARNESS_FALLBACK=none` ayarlar.
- Auth: shell/profile üzerinden `OPENAI_API_KEY`, artı isteğe bağlı olarak kopyalanmış
  `~/.codex/auth.json` ve `~/.codex/config.toml`

Yerel tarif:

```bash
source ~/.profile
OPENCLAW_LIVE_CODEX_HARNESS=1 \
  OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=1 \
  OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=1 \
  OPENCLAW_LIVE_CODEX_HARNESS_MODEL=codex/gpt-5.4 \
  pnpm test:live -- src/gateway/gateway-codex-harness.live.test.ts
```

Docker tarifi:

```bash
source ~/.profile
pnpm test:docker:live-codex-harness
```

Docker notları:

- Docker çalıştırıcısı `scripts/test-live-codex-harness-docker.sh` konumundadır.
- Bağlanan `~/.profile` dosyasını kaynak olarak yükler, `OPENAI_API_KEY` geçirir, varsa Codex CLI
  auth dosyalarını kopyalar, `@openai/codex` paketini yazılabilir bağlanmış bir npm
  önekine kurar, kaynak ağacı hazırlar ve ardından yalnızca Codex-harness canlı testini çalıştırır.
- Docker varsayılan olarak görsel ve MCP/araç problarını etkinleştirir. Daha dar bir hata ayıklama çalıştırması gerektiğinde
  `OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=0` veya
  `OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=0` ayarlayın.
- Docker ayrıca `OPENCLAW_AGENT_HARNESS_FALLBACK=none` dışa aktarır; bu canlı
  test yapılandırmasıyla eşleşir, böylece `openai-codex/*` veya PI geri dönüşü bir Codex harness
  regresyonunu gizleyemez.

### Önerilen canlı tarifler

Dar, açık allowlist'ler en hızlı ve en az oynak olanlardır:

- Tek model, doğrudan (Gateway yok):
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.4" pnpm test:live src/agents/models.profiles.live.test.ts`

- Tek model, Gateway smoke:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Birkaç sağlayıcı arasında araç çağırma:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Google odağı (Gemini API anahtarı + Antigravity):
  - Gemini (API anahtarı): `OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  - Antigravity (OAuth): `OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

Notlar:

- `google/...` Gemini API'yi kullanır (API anahtarı).
- `google-antigravity/...` Antigravity OAuth köprüsünü kullanır (Cloud Code Assist tarzı ajan uç noktası).
- `google-gemini-cli/...` makinenizdeki yerel Gemini CLI'ı kullanır (ayrı auth + araç davranışı farklılıkları).
- Gemini API ile Gemini CLI arasındaki fark:
  - API: OpenClaw, Google'ın barındırılan Gemini API'sini HTTP üzerinden çağırır (API anahtarı / profil auth); çoğu kullanıcının “Gemini” derken kastettiği budur.
  - CLI: OpenClaw yerel bir `gemini` ikilisini shell üzerinden çağırır; bunun kendi auth mekanizması vardır ve davranışı farklı olabilir (streaming/araç desteği/sürüm kayması).

## Canlı: model matriksi (neleri kapsıyoruz)

Sabit bir “CI model listesi” yoktur (canlı isteğe bağlıdır), ancak anahtarlara sahip bir geliştirme makinesinde düzenli olarak kapsanması **önerilen** modeller bunlardır.

### Modern smoke kümesi (araç çağırma + görsel)

Çalışır durumda tutmayı beklediğimiz “yaygın modeller” çalıştırması budur:

- OpenAI (Codex dışı): `openai/gpt-5.4` (isteğe bağlı: `openai/gpt-5.4-mini`)
- OpenAI Codex: `openai-codex/gpt-5.4`
- Anthropic: `anthropic/claude-opus-4-6` (veya `anthropic/claude-sonnet-4-6`)
- Google (Gemini API): `google/gemini-3.1-pro-preview` ve `google/gemini-3-flash-preview` (eski Gemini 2.x modellerinden kaçının)
- Google (Antigravity): `google-antigravity/claude-opus-4-6-thinking` ve `google-antigravity/gemini-3-flash`
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

Araçlar + görselle Gateway smoke çalıştırması:
`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,openai-codex/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3.1-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

### Temel seviye: araç çağırma (Read + isteğe bağlı Exec)

Sağlayıcı ailesi başına en az bir tane seçin:

- OpenAI: `openai/gpt-5.4` (veya `openai/gpt-5.4-mini`)
- Anthropic: `anthropic/claude-opus-4-6` (veya `anthropic/claude-sonnet-4-6`)
- Google: `google/gemini-3-flash-preview` (veya `google/gemini-3.1-pro-preview`)
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

İsteğe bağlı ek kapsama (olsa iyi olur):

- xAI: `xai/grok-4` (veya mevcut en son sürüm)
- Mistral: `mistral/`… (etkinleştirdiğiniz araç yetenekli bir model seçin)
- Cerebras: `cerebras/`… (erişiminiz varsa)
- LM Studio: `lmstudio/`… (yerel; araç çağırma API moduna bağlıdır)

### Vision: görsel gönderimi (ek → çok kipli mesaj)

Görsel probe'u çalıştırmak için `OPENCLAW_LIVE_GATEWAY_MODELS` içine en az bir görsel destekli model ekleyin (Claude/Gemini/OpenAI'nin görsel yetenekli varyantları vb.).

### Toplayıcılar / alternatif Gateway'ler

Anahtarlarınız etkinse şunlar üzerinden de test desteğimiz vardır:

- OpenRouter: `openrouter/...` (yüzlerce model; araç+görsel destekli adayları bulmak için `openclaw models scan` kullanın)
- OpenCode: Zen için `opencode/...` ve Go için `opencode-go/...` (`OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY` ile auth)

Canlı matrikse ekleyebileceğiniz daha fazla sağlayıcı (kimlik bilgileri/yapılandırmanız varsa):

- Yerleşik: `openai`, `openai-codex`, `anthropic`, `google`, `google-vertex`, `google-antigravity`, `google-gemini-cli`, `zai`, `openrouter`, `opencode`, `opencode-go`, `xai`, `groq`, `cerebras`, `mistral`, `github-copilot`
- `models.providers` üzerinden (özel uç noktalar): `minimax` (bulut/API), ayrıca OpenAI/Anthropic uyumlu tüm vekiller (LM Studio, vLLM, LiteLLM vb.)

İpucu: belgelerde “tüm modelleri” sabit kodlamaya çalışmayın. Yetkili liste, makinenizde `discoverModels(...)` ne döndürüyorsa ve hangi anahtarlar mevcutsa odur.

## Kimlik bilgileri (asla commit etmeyin)

Canlı testler kimlik bilgilerini CLI ile aynı şekilde keşfeder. Pratik sonuçlar:

- CLI çalışıyorsa, canlı testler de aynı anahtarları bulmalıdır.
- Bir canlı test “kimlik bilgisi yok” diyorsa, bunu `openclaw models list` / model seçimini hata ayıklarken yaptığınız gibi hata ayıklayın.

- Ajan başına auth profilleri: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` (canlı testlerde “profil anahtarları” denince kastedilen budur)
- Yapılandırma: `~/.openclaw/openclaw.json` (veya `OPENCLAW_CONFIG_PATH`)
- Eski durum dizini: `~/.openclaw/credentials/` (varsa hazırlanan canlı home'a kopyalanır, ancak ana profil-anahtarı deposu bu değildir)
- Canlı yerel çalıştırmalar varsayılan olarak etkin yapılandırmayı, ajan başına `auth-profiles.json` dosyalarını, eski `credentials/` dizinini ve desteklenen harici CLI auth dizinlerini geçici bir test home'una kopyalar; hazırlanan canlı home'lar `workspace/` ve `sandboxes/` öğelerini atlar ve probların gerçek host çalışma alanınızdan uzak durması için `agents.*.workspace` / `agentDir` yol geçersiz kılmaları temizlenir.

Ortam anahtarlarına güvenmek istiyorsanız (ör. `~/.profile` içinde dışa aktarılmışsa), yerel testleri `source ~/.profile` sonrasında çalıştırın veya aşağıdaki Docker çalıştırıcılarını kullanın (`~/.profile` dosyasını container içine bağlayabilirler).

## Deepgram canlı (ses transkripsiyonu)

- Test: `src/media-understanding/providers/deepgram/audio.live.test.ts`
- Etkinleştirme: `DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`

## BytePlus coding plan canlı

- Test: `src/agents/byteplus.live.test.ts`
- Etkinleştirme: `BYTEPLUS_API_KEY=... BYTEPLUS_LIVE_TEST=1 pnpm test:live src/agents/byteplus.live.test.ts`
- İsteğe bağlı model geçersiz kılma: `BYTEPLUS_CODING_MODEL=ark-code-latest`

## ComfyUI workflow media canlı

- Test: `extensions/comfy/comfy.live.test.ts`
- Etkinleştirme: `OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts`
- Kapsam:
  - Paketlenmiş comfy görsel, video ve `music_generate` yollarını çalıştırır
  - `models.providers.comfy.<capability>` yapılandırılmamışsa her yeteneği atlar
  - Comfy workflow gönderimi, polling, indirmeler veya Plugin kaydı değiştirildikten sonra faydalıdır

## Görsel üretimi canlı

- Test: `src/image-generation/runtime.live.test.ts`
- Komut: `pnpm test:live src/image-generation/runtime.live.test.ts`
- Harness: `pnpm test:live:media image`
- Kapsam:
  - Kayıtlı her görsel üretim sağlayıcısı Plugin'ini listeler
  - Probe'dan önce eksik sağlayıcı env değişkenlerini giriş shell'inizden (`~/.profile`) yükler
  - Varsayılan olarak saklanan auth profillerinden önce canlı/env API anahtarlarını kullanır; böylece `auth-profiles.json` içindeki bayat test anahtarları gerçek shell kimlik bilgilerini maskelemez
  - Kullanılabilir auth/profil/model olmayan sağlayıcıları atlar
  - Stok görsel üretim varyantlarını paylaşılan çalışma zamanı yeteneği üzerinden çalıştırır:
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
  - Profil deposu auth'unu zorlamak ve yalnızca env geçersiz kılmalarını yok saymak için `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`

## Müzik üretimi canlı

- Test: `extensions/music-generation-providers.live.test.ts`
- Etkinleştirme: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts`
- Harness: `pnpm test:live:media music`
- Kapsam:
  - Paylaşılan paketlenmiş müzik üretimi sağlayıcısı yolunu çalıştırır
  - Şu anda Google ve MiniMax'ı kapsar
  - Probe'dan önce sağlayıcı env değişkenlerini giriş shell'inizden (`~/.profile`) yükler
  - Varsayılan olarak saklanan auth profillerinden önce canlı/env API anahtarlarını kullanır; böylece `auth-profiles.json` içindeki bayat test anahtarları gerçek shell kimlik bilgilerini maskelemez
  - Kullanılabilir auth/profil/model olmayan sağlayıcıları atlar
  - Mevcut olduğunda bildirilen her iki çalışma zamanı modunu da çalıştırır:
    - yalnızca prompt girdisiyle `generate`
    - sağlayıcı `capabilities.edit.enabled` bildirdiğinde `edit`
  - Mevcut paylaşılan hat kapsaması:
    - `google`: `generate`, `edit`
    - `minimax`: `generate`
    - `comfy`: ayrı Comfy canlı dosyası, bu paylaşılan tarama değil
- İsteğe bağlı daraltma:
  - `OPENCLAW_LIVE_MUSIC_GENERATION_PROVIDERS="google,minimax"`
  - `OPENCLAW_LIVE_MUSIC_GENERATION_MODELS="google/lyria-3-clip-preview,minimax/music-2.5+"`
- İsteğe bağlı auth davranışı:
  - Profil deposu auth'unu zorlamak ve yalnızca env geçersiz kılmalarını yok saymak için `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`

## Video üretimi canlı

- Test: `extensions/video-generation-providers.live.test.ts`
- Etkinleştirme: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts`
- Harness: `pnpm test:live:media video`
- Kapsam:
  - Paylaşılan paketlenmiş video üretimi sağlayıcısı yolunu çalıştırır
  - Probe'dan önce sağlayıcı env değişkenlerini giriş shell'inizden (`~/.profile`) yükler
  - Varsayılan olarak saklanan auth profillerinden önce canlı/env API anahtarlarını kullanır; böylece `auth-profiles.json` içindeki bayat test anahtarları gerçek shell kimlik bilgilerini maskelemez
  - Kullanılabilir auth/profil/model olmayan sağlayıcıları atlar
  - Mevcut olduğunda bildirilen her iki çalışma zamanı modunu da çalıştırır:
    - yalnızca prompt girdisiyle `generate`
    - sağlayıcı `capabilities.imageToVideo.enabled` bildirdiğinde ve seçilen sağlayıcı/model paylaşılan taramada tampon destekli yerel görsel girdisini kabul ettiğinde `imageToVideo`
    - sağlayıcı `capabilities.videoToVideo.enabled` bildirdiğinde ve seçilen sağlayıcı/model paylaşılan taramada tampon destekli yerel video girdisini kabul ettiğinde `videoToVideo`
  - Paylaşılan taramada şu anda bildirilen ama atlanan `imageToVideo` sağlayıcıları:
    - `vydra`, çünkü paketlenmiş `veo3` yalnızca metin desteklidir ve paketlenmiş `kling` uzak bir görsel URL'si gerektirir
  - Sağlayıcıya özgü Vydra kapsaması:
    - `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_VYDRA_VIDEO=1 pnpm test:live -- extensions/vydra/vydra.live.test.ts`
    - bu dosya varsayılan olarak uzak bir görsel URL fixture'ı kullanan bir `kling` hattıyla birlikte `veo3` text-to-video çalıştırır
  - Şu anki `videoToVideo` canlı kapsaması:
    - seçilen model `runway/gen4_aleph` olduğunda yalnızca `runway`
  - Paylaşılan taramada şu anda bildirilen ama atlanan `videoToVideo` sağlayıcıları:
    - `alibaba`, `qwen`, `xai`, çünkü bu yollar şu anda uzak `http(s)` / MP4 referans URL'leri gerektiriyor
    - `google`, çünkü mevcut paylaşılan Gemini/Veo hattı yerel tampon destekli girdi kullanıyor ve bu yol paylaşılan taramada kabul edilmiyor
    - `openai`, çünkü mevcut paylaşılan hatta kuruma özgü video inpaint/remix erişimi garantileri yok
- İsteğe bağlı daraltma:
  - `OPENCLAW_LIVE_VIDEO_GENERATION_PROVIDERS="google,openai,runway"`
  - `OPENCLAW_LIVE_VIDEO_GENERATION_MODELS="google/veo-3.1-fast-generate-preview,openai/sora-2,runway/gen4_aleph"`
- İsteğe bağlı auth davranışı:
  - Profil deposu auth'unu zorlamak ve yalnızca env geçersiz kılmalarını yok saymak için `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`

## Medya canlı harness'i

- Komut: `pnpm test:live:media`
- Amaç:
  - Paylaşılan görsel, müzik ve video canlı paketlerini tek bir depoya özgü giriş noktası üzerinden çalıştırır
  - Eksik sağlayıcı env değişkenlerini `~/.profile` dosyasından otomatik yükler
  - Varsayılan olarak her paketi o anda kullanılabilir auth'u olan sağlayıcılara otomatik daraltır
  - `scripts/test-live.mjs` dosyasını yeniden kullanır; böylece Heartbeat ve sessiz mod davranışı tutarlı kalır
- Örnekler:
  - `pnpm test:live:media`
  - `pnpm test:live:media image video --providers openai,google,minimax`
  - `pnpm test:live:media video --video-providers openai,runway --all-providers`
  - `pnpm test:live:media music --quiet`

## Docker çalıştırıcıları (isteğe bağlı “Linux'ta çalışıyor” kontrolleri)

Bu Docker çalıştırıcıları iki gruba ayrılır:

- Canlı model çalıştırıcıları: `test:docker:live-models` ve `test:docker:live-gateway`, yalnızca eşleşen profil-anahtarı canlı dosyalarını depo Docker imajı içinde çalıştırır (`src/agents/models.profiles.live.test.ts` ve `src/gateway/gateway-models.profiles.live.test.ts`), yerel yapılandırma dizininizi ve çalışma alanınızı bağlar (ve bağlandıysa `~/.profile` dosyasını kaynak olarak yükler). Eşleşen yerel giriş noktaları `test:live:models-profiles` ve `test:live:gateway-profiles`'tır.
- Docker canlı çalıştırıcıları, tam bir Docker taramasının pratik kalması için varsayılan olarak daha küçük bir smoke sınırı kullanır:
  `test:docker:live-models` varsayılan olarak `OPENCLAW_LIVE_MAX_MODELS=12`, ve
  `test:docker:live-gateway` varsayılan olarak `OPENCLAW_LIVE_GATEWAY_SMOKE=1`,
  `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=8`,
  `OPENCLAW_LIVE_GATEWAY_STEP_TIMEOUT_MS=45000` ve
  `OPENCLAW_LIVE_GATEWAY_MODEL_TIMEOUT_MS=90000` ayarlar. Daha büyük kapsamlı taramayı
  özellikle istediğinizde bu env değişkenlerini geçersiz kılın.
- `test:docker:all`, canlı Docker imajını önce `test:docker:live-build` aracılığıyla bir kez oluşturur, sonra bunu iki canlı Docker hattı için yeniden kullanır.
- Container smoke çalıştırıcıları: `test:docker:openwebui`, `test:docker:onboard`, `test:docker:gateway-network`, `test:docker:mcp-channels` ve `test:docker:plugins`, bir veya daha fazla gerçek container başlatır ve daha üst düzey entegrasyon yollarını doğrular.

Canlı model Docker çalıştırıcıları ayrıca yalnızca gerekli CLI auth home'larını (veya çalıştırma daraltılmadıysa desteklenenlerin tümünü) bind-mount eder, sonra dış CLI OAuth'unun host auth deposunu değiştirmeden token'ları yenileyebilmesi için bunları çalıştırma öncesinde container home'una kopyalar:

- Doğrudan modeller: `pnpm test:docker:live-models` (betik: `scripts/test-live-models-docker.sh`)
- ACP bind smoke: `pnpm test:docker:live-acp-bind` (betik: `scripts/test-live-acp-bind-docker.sh`)
- CLI backend smoke: `pnpm test:docker:live-cli-backend` (betik: `scripts/test-live-cli-backend-docker.sh`)
- Codex app-server harness smoke: `pnpm test:docker:live-codex-harness` (betik: `scripts/test-live-codex-harness-docker.sh`)
- Gateway + geliştirme ajanı: `pnpm test:docker:live-gateway` (betik: `scripts/test-live-gateway-models-docker.sh`)
- Open WebUI canlı smoke: `pnpm test:docker:openwebui` (betik: `scripts/e2e/openwebui-docker.sh`)
- Onboarding wizard'ı (TTY, tam scaffolding): `pnpm test:docker:onboard` (betik: `scripts/e2e/onboard-docker.sh`)
- Gateway ağ iletişimi (iki container, WS auth + health): `pnpm test:docker:gateway-network` (betik: `scripts/e2e/gateway-network-docker.sh`)
- MCP kanal köprüsü (tohumlanmış Gateway + stdio bridge + ham Claude notification-frame smoke): `pnpm test:docker:mcp-channels` (betik: `scripts/e2e/mcp-channels-docker.sh`)
- Plugin'ler (kurulum smoke + `/plugin` takma adı + Claude paketi yeniden başlatma semantiği): `pnpm test:docker:plugins` (betik: `scripts/e2e/plugins-docker.sh`)

Canlı model Docker çalıştırıcıları ayrıca mevcut checkout'u salt okunur olarak bind-mount eder ve
container içinde geçici bir workdir'e hazırlar. Bu, çalışma zamanı
imajını ince tutarken yine de tam yerel kaynak/yapılandırmanız üzerinde Vitest çalıştırılmasını sağlar.
Hazırlama adımı `.pnpm-store`, `.worktrees`, `__openclaw_vitest__` ve
uygulamaya özgü `.build` veya Gradle çıktı dizinleri gibi büyük yerel önbellekleri ve uygulama derleme çıktılarını atlar; böylece Docker canlı çalıştırmaları
makineye özgü artifact'ları kopyalamak için dakikalar harcamaz.
Ayrıca `OPENCLAW_SKIP_CHANNELS=1` ayarlarlar; böylece Gateway canlı probları
container içinde gerçek Telegram/Discord vb. kanal worker'larını başlatmaz.
`test:docker:live-models` yine de `pnpm test:live` çalıştırır; bu nedenle bu Docker hattında
Gateway canlı kapsamını daraltmanız veya hariç tutmanız gerektiğinde `OPENCLAW_LIVE_GATEWAY_*`
değerlerini de iletin.
`test:docker:openwebui` daha üst düzey bir uyumluluk smoke'udur: OpenAI uyumlu HTTP uç noktaları etkin bir
OpenClaw Gateway container'ı başlatır,
bu Gateway'ye karşı sabitlenmiş bir Open WebUI container'ı başlatır, Open WebUI üzerinden oturum açar,
`/api/models` içinde `openclaw/default` gösterildiğini doğrular, ardından
Open WebUI'nin `/api/chat/completions` vekili üzerinden gerçek bir sohbet isteği gönderir.
İlk çalıştırma gözle görülür biçimde daha yavaş olabilir; çünkü Docker'ın
Open WebUI imajını çekmesi gerekebilir ve Open WebUI'nin kendi soğuk başlangıç kurulumunu tamamlaması gerekebilir.
Bu hat kullanılabilir bir canlı model anahtarı bekler ve `OPENCLAW_PROFILE_FILE`
(Docker'lı çalıştırmalarda varsayılan olarak `~/.profile`) bunu sağlamak için birincil yoldur.
Başarılı çalıştırmalar `{ "ok": true, "model":
"openclaw/default", ... }` gibi küçük bir JSON yükü yazdırır.
`test:docker:mcp-channels` kasıtlı olarak deterministiktir ve gerçek bir
Telegram, Discord veya iMessage hesabı gerektirmez. Tohumlanmış bir Gateway
container'ı başlatır, `openclaw mcp serve` üreten ikinci bir container başlatır, sonra
yönlendirilmiş konuşma keşfini, transkript okumalarını, ek metadata'sını,
canlı olay kuyruğu davranışını, giden gönderim yönlendirmesini ve Claude tarzı kanal +
izin bildirimlerini gerçek stdio MCP köprüsü üzerinden doğrular. Bildirim kontrolü
ham stdio MCP frame'lerini doğrudan inceler; böylece smoke, yalnızca belirli bir istemci SDK'sının
tesadüfen yüzeye çıkardığını değil, köprünün gerçekten ne yayımladığını doğrular.

Manuel ACP doğal dil thread smoke'u (CI değil):

- `bun scripts/dev/discord-acp-plain-language-smoke.ts --channel <discord-channel-id> ...`
- Bu betiği regresyon/hata ayıklama iş akışları için tutun. ACP thread yönlendirme doğrulaması için yeniden gerekebilir, bu yüzden silmeyin.

Yararlı env değişkenleri:

- `OPENCLAW_CONFIG_DIR=...` (varsayılan: `~/.openclaw`) `/home/node/.openclaw` dizinine bağlanır
- `OPENCLAW_WORKSPACE_DIR=...` (varsayılan: `~/.openclaw/workspace`) `/home/node/.openclaw/workspace` dizinine bağlanır
- `OPENCLAW_PROFILE_FILE=...` (varsayılan: `~/.profile`) `/home/node/.profile` dizinine bağlanır ve testleri çalıştırmadan önce kaynak olarak yüklenir
- `OPENCLAW_DOCKER_CLI_TOOLS_DIR=...` (varsayılan: `~/.cache/openclaw/docker-cli-tools`) Docker içindeki önbelleğe alınmış CLI kurulumları için `/home/node/.npm-global` dizinine bağlanır
- `$HOME` altındaki harici CLI auth dizinleri/dosyaları `/host-auth...` altında salt okunur olarak bağlanır, sonra testler başlamadan önce `/home/node/...` içine kopyalanır
  - Varsayılan dizinler: `.minimax`
  - Varsayılan dosyalar: `~/.codex/auth.json`, `~/.codex/config.toml`, `.claude.json`, `~/.claude/.credentials.json`, `~/.claude/settings.json`, `~/.claude/settings.local.json`
  - Daraltılmış sağlayıcı çalıştırmaları yalnızca `OPENCLAW_LIVE_PROVIDERS` / `OPENCLAW_LIVE_GATEWAY_PROVIDERS` değerlerinden çıkarılan gerekli dizinleri/dosyaları bağlar
  - El ile geçersiz kılmak için `OPENCLAW_DOCKER_AUTH_DIRS=all`, `OPENCLAW_DOCKER_AUTH_DIRS=none` veya `OPENCLAW_DOCKER_AUTH_DIRS=.claude,.codex` gibi virgülle ayrılmış bir liste kullanın
- Çalıştırmayı daraltmak için `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...`
- Container içindeki sağlayıcıları filtrelemek için `OPENCLAW_LIVE_GATEWAY_PROVIDERS=...` / `OPENCLAW_LIVE_PROVIDERS=...`
- Yeniden derleme gerektirmeyen tekrar çalıştırmalar için mevcut `openclaw:local-live` imajını yeniden kullanmak üzere `OPENCLAW_SKIP_DOCKER_BUILD=1`
- Kimlik bilgilerinin env'den değil profil deposundan geldiğinden emin olmak için `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`
- Open WebUI smoke için Gateway'nin sunduğu modeli seçmek üzere `OPENCLAW_OPENWEBUI_MODEL=...`
- Open WebUI smoke'unun kullandığı nonce kontrol prompt'unu geçersiz kılmak için `OPENCLAW_OPENWEBUI_PROMPT=...`
- Sabitlenmiş Open WebUI imaj etiketini geçersiz kılmak için `OPENWEBUI_IMAGE=...`

## Belgeler sağlama kontrolü

Belge düzenlemelerinden sonra belge kontrollerini çalıştırın: `pnpm check:docs`.
Sayfa içi başlık kontrollerine de ihtiyacınız olduğunda tam Mintlify anchor doğrulamasını çalıştırın: `pnpm docs:check-links:anchors`.

## Çevrimdışı regresyon (CI-güvenli)

Bunlar, gerçek sağlayıcılar olmadan “gerçek boru hattı” regresyonlarıdır:

- Gateway araç çağırma (sahte OpenAI, gerçek Gateway + ajan döngüsü): `src/gateway/gateway.test.ts` (durum: "runs a mock OpenAI tool call end-to-end via gateway agent loop")
- Gateway wizard'ı (WS `wizard.start`/`wizard.next`, config + auth yazımı zorunlu): `src/gateway/gateway.test.ts` (durum: "runs wizard over ws and writes auth token config")

## Ajan güvenilirliği değerlendirmeleri (Skills)

Zaten “ajan güvenilirliği değerlendirmeleri” gibi davranan birkaç CI-güvenli testimiz var:

- Gerçek Gateway + ajan döngüsü üzerinden sahte araç çağırma (`src/gateway/gateway.test.ts`).
- Oturum bağlantısını ve config etkilerini doğrulayan uçtan uca wizard akışları (`src/gateway/gateway.test.ts`).

Skills için hâlâ eksik olanlar ([Skills](/tr/tools/skills) bölümüne bakın):

- **Karar verme:** Skills prompt içinde listelendiğinde, ajan doğru Skill'i seçiyor mu (veya ilgisiz olanlardan kaçınıyor mu)?
- **Uyumluluk:** ajan kullanmadan önce `SKILL.md` dosyasını okuyor ve gerekli adımları/argümanları izliyor mu?
- **İş akışı sözleşmeleri:** araç sırasını, oturum geçmişi taşınmasını ve sandbox sınırlarını doğrulayan çok turlu senaryolar.

Gelecekteki değerlendirmeler önce deterministik kalmalıdır:

- Araç çağrılarını + sırasını, Skill dosyası okumalarını ve oturum bağlantısını doğrulamak için sahte sağlayıcılar kullanan bir senaryo çalıştırıcısı.
- Skill odaklı küçük bir senaryo paketi (kullan vs kaçın, kapılama, prompt injection).
- İsteğe bağlı canlı değerlendirmeler (isteğe bağlı, env kapılı) yalnızca CI-güvenli paket yerleştirildikten sonra.

## Sözleşme testleri (Plugin ve kanal şekli)

Sözleşme testleri, kayıtlı her Plugin ve kanalın kendi
arayüz sözleşmesine uyduğunu doğrular. Keşfedilen tüm Plugin'ler üzerinde dolaşır ve
bir dizi şekil ve davranış doğrulaması çalıştırırlar. Varsayılan `pnpm test` birim hattı
bu paylaşılan seam ve smoke dosyalarını kasıtlı olarak atlar; paylaşılan kanal veya sağlayıcı yüzeylerine dokunduğunuzda sözleşme komutlarını açıkça çalıştırın.

### Komutlar

- Tüm sözleşmeler: `pnpm test:contracts`
- Yalnızca kanal sözleşmeleri: `pnpm test:contracts:channels`
- Yalnızca sağlayıcı sözleşmeleri: `pnpm test:contracts:plugins`

### Kanal sözleşmeleri

`src/channels/plugins/contracts/*.contract.test.ts` konumunda bulunur:

- **plugin** - Temel Plugin şekli (id, name, capabilities)
- **setup** - Kurulum sihirbazı sözleşmesi
- **session-binding** - Oturum bağlama davranışı
- **outbound-payload** - Mesaj yükü yapısı
- **inbound** - Gelen mesaj işleme
- **actions** - Kanal eylem işleyicileri
- **threading** - Thread kimliği işleme
- **directory** - Dizin/roster API
- **group-policy** - Grup ilkesi zorlaması

### Sağlayıcı durum sözleşmeleri

`src/plugins/contracts/*.contract.test.ts` konumunda bulunur.

- **status** - Kanal durum probe'ları
- **registry** - Plugin kayıt defteri şekli

### Sağlayıcı sözleşmeleri

`src/plugins/contracts/*.contract.test.ts` konumunda bulunur:

- **auth** - Auth akışı sözleşmesi
- **auth-choice** - Auth seçimi/seçenek belirleme
- **catalog** - Model katalog API'si
- **discovery** - Plugin keşfi
- **loader** - Plugin yükleme
- **runtime** - Sağlayıcı çalışma zamanı
- **shape** - Plugin şekli/arayüzü
- **wizard** - Kurulum sihirbazı

### Ne zaman çalıştırılmalı

- Plugin SDK dışa aktarımlarını veya alt yollarını değiştirdikten sonra
- Bir kanal veya sağlayıcı Plugin'i ekledikten ya da değiştirdikten sonra
- Plugin kaydı veya keşfini yeniden düzenledikten sonra

Sözleşme testleri CI içinde çalışır ve gerçek API anahtarları gerektirmez.

## Regresyon ekleme (rehber)

Canlıda keşfedilen bir sağlayıcı/model sorununu düzelttiğinizde:

- Mümkünse CI-güvenli bir regresyon ekleyin (sahte/stub sağlayıcı veya tam istek-şekli dönüşümünü yakalayın)
- Sorun doğası gereği yalnızca canlıysa (oran sınırları, auth politikaları), canlı testi dar ve env değişkenleriyle isteğe bağlı tutun
- Hatayı yakalayan en küçük katmanı hedeflemeyi tercih edin:
  - sağlayıcı istek dönüştürme/replay hatası → doğrudan modeller testi
  - Gateway oturum/geçmiş/araç hattı hatası → Gateway canlı smoke veya CI-güvenli Gateway mock testi
- SecretRef gezinme koruma kuralı:
  - `src/secrets/exec-secret-ref-id-parity.test.ts`, kayıt defteri metadata'sından (`listSecretTargetRegistryEntries()`) SecretRef sınıfı başına örneklenmiş bir hedef türetir, ardından traversal segment `exec` kimliklerinin reddedildiğini doğrular.
  - `src/secrets/target-registry-data.ts` içinde yeni bir `includeInPlan` SecretRef hedef ailesi eklerseniz, o testte `classifyTargetClass` öğesini güncelleyin. Test, yeni sınıfların sessizce atlanamaması için sınıflandırılmamış hedef kimliklerinde kasıtlı olarak başarısız olur.
