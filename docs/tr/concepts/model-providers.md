---
read_when:
    - Sağlayıcı bazında model kurulumu başvuru kaynağına ihtiyacınız var
    - Model sağlayıcıları için örnek yapılandırmalar veya CLI onboarding komutları istiyorsunuz
summary: Örnek yapılandırmalar + CLI akışları ile model sağlayıcısı genel bakışı
title: Model Sağlayıcıları
x-i18n:
    generated_at: "2026-04-13T08:50:44Z"
    model: gpt-5.4
    provider: openai
    source_hash: 66ba688c4b4366eec07667571e835d4cfeee684896e2ffae11d601b5fa0a4b98
    source_path: concepts/model-providers.md
    workflow: 15
---

# Model sağlayıcıları

Bu sayfa **LLM/model sağlayıcılarını** kapsar (WhatsApp/Telegram gibi sohbet kanallarını değil).
Model seçim kuralları için bkz. [/concepts/models](/tr/concepts/models).

## Hızlı kurallar

- Model başvuruları `provider/model` kullanır (örnek: `opencode/claude-opus-4-6`).
- `agents.defaults.models` ayarlarsanız, bu allowlist olur.
- CLI yardımcıları: `openclaw onboard`, `openclaw models list`, `openclaw models set <provider/model>`.
- Yedek çalışma zamanı kuralları, cooldown probları ve oturum geçersiz kılma kalıcılığı
  [/concepts/model-failover](/tr/concepts/model-failover) içinde belgelenmiştir.
- `models.providers.*.models[].contextWindow` yerel model meta verisidir;
  `models.providers.*.models[].contextTokens` ise etkili çalışma zamanı sınırıdır.
- Provider Plugin'leri model kataloglarını `registerProvider({ catalog })` aracılığıyla ekleyebilir;
  OpenClaw bu çıktıyı `models.providers` içine birleştirir ve ardından
  `models.json` dosyasını yazar.
- Provider manifest'leri `providerAuthEnvVars` ve
  `providerAuthAliases` bildirebilir; böylece genel ortam tabanlı kimlik doğrulama probları ve sağlayıcı varyantları
  Plugin çalışma zamanını yüklemek zorunda kalmaz. Geriye kalan çekirdek env-var eşlemesi artık
  yalnızca Plugin olmayan/çekirdek sağlayıcılar ve Anthropic API anahtarı öncelikli onboarding gibi
  birkaç genel öncelik durumu içindir.
- Provider Plugin'leri ayrıca sağlayıcı çalışma zamanı davranışını da sahiplenebilir:
  `normalizeModelId`, `normalizeTransport`, `normalizeConfig`,
  `applyNativeStreamingUsageCompat`, `resolveConfigApiKey`,
  `resolveSyntheticAuth`, `shouldDeferSyntheticProfileAuth`,
  `resolveDynamicModel`, `prepareDynamicModel`,
  `normalizeResolvedModel`, `contributeResolvedModelCompat`,
  `capabilities`, `normalizeToolSchemas`,
  `inspectToolSchemas`, `resolveReasoningOutputMode`,
  `prepareExtraParams`, `createStreamFn`, `wrapStreamFn`,
  `resolveTransportTurnState`, `resolveWebSocketSessionPolicy`,
  `createEmbeddingProvider`, `formatApiKey`, `refreshOAuth`,
  `buildAuthDoctorHint`,
  `matchesContextOverflowError`, `classifyFailoverReason`,
  `isCacheTtlEligible`, `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `isBinaryThinking`, `supportsXHighThinking`,
  `resolveDefaultThinkingLevel`, `applyConfigDefaults`, `isModernModelRef`,
  `prepareRuntimeAuth`, `resolveUsageAuth`, `fetchUsageSnapshot` ve
  `onModelSelected`.
- Not: provider çalışma zamanı `capabilities`, paylaşılan çalıştırıcı meta verisidir (sağlayıcı
  ailesi, transkript/araçlama özellikleri, taşıma/önbellek ipuçları). Bu,
  bir Plugin'in ne kaydettiğini açıklayan [genel yetenek modeli](/tr/plugins/architecture#public-capability-model)
  ile aynı şey değildir (metin çıkarımı, konuşma vb.).
- Paketlenmiş `codex` sağlayıcısı, paketlenmiş Codex ajan koşum takımı ile eşleştirilmiştir.
  Codex'e ait oturum açma, model keşfi, yerel iş parçacığı sürdürme ve
  uygulama sunucusu yürütmesi istediğinizde `codex/gpt-*` kullanın. Düz `openai/gpt-*` başvuruları
  OpenAI sağlayıcısını ve normal OpenClaw sağlayıcı taşımasını kullanmaya devam eder.
  Yalnızca Codex dağıtımları, otomatik PI geri dönüşünü
  `agents.defaults.embeddedHarness.fallback: "none"` ile devre dışı bırakabilir; bkz.
  [Codex Harness](/tr/plugins/codex-harness).

## Plugin'e ait sağlayıcı davranışı

Provider Plugin'leri artık sağlayıcıya özgü mantığın büyük kısmını sahiplenebilirken OpenClaw
genel çıkarım döngüsünü korur.

Tipik ayrım:

- `auth[].run` / `auth[].runNonInteractive`: sağlayıcı, `openclaw onboard`, `openclaw models auth` ve başsız kurulum için onboarding/oturum açma
  akışlarını sahiplenir
- `wizard.setup` / `wizard.modelPicker`: sağlayıcı, kimlik doğrulama seçeneği etiketlerini,
  eski takma adları, onboarding allowlist ipuçlarını ve onboarding/model seçicilerdeki kurulum girişlerini sahiplenir
- `catalog`: sağlayıcı `models.providers` içinde görünür
- `normalizeModelId`: sağlayıcı, arama veya kanonikleştirmeden önce eski/önizleme model kimliklerini
  normalize eder
- `normalizeTransport`: sağlayıcı, genel model birleştirmesinden önce taşıma ailesi `api` / `baseUrl` değerlerini
  normalize eder; OpenClaw önce eşleşen sağlayıcıyı,
  ardından taşıma üzerinde gerçekten değişiklik yapan birini bulana kadar diğer hook yetenekli provider Plugin'lerini kontrol eder
- `normalizeConfig`: sağlayıcı, çalışma zamanı kullanmadan önce `models.providers.<id>` yapılandırmasını
  normalize eder; OpenClaw önce eşleşen sağlayıcıyı,
  ardından yapılandırmayı gerçekten değiştiren birini bulana kadar diğer
  hook yetenekli provider Plugin'lerini kontrol eder. Hiçbir sağlayıcı hook'u yapılandırmayı yeniden yazmazsa,
  paketlenmiş Google ailesi yardımcıları desteklenen Google sağlayıcı girişlerini yine de
  normalize eder.
- `applyNativeStreamingUsageCompat`: sağlayıcı, yapılandırma sağlayıcıları için uç nokta güdümlü yerel akış kullanım uyumluluğu yeniden yazımlarını uygular
- `resolveConfigApiKey`: sağlayıcı, tam çalışma zamanı kimlik doğrulamasının yüklenmesini zorlamadan
  yapılandırma sağlayıcıları için env-marker kimlik doğrulamasını çözer. `amazon-bedrock` burada
  yerleşik bir AWS env-marker çözücüsüne de sahiptir; Bedrock çalışma zamanı kimlik doğrulaması
  AWS SDK varsayılan zincirini kullansa da.
- `resolveSyntheticAuth`: sağlayıcı, düz metin sırları kalıcılaştırmadan yerel/self-hosted veya diğer
  yapılandırma destekli kimlik doğrulama kullanılabilirliğini açığa çıkarabilir
- `shouldDeferSyntheticProfileAuth`: sağlayıcı, depolanan sentetik profil yer tutucularını
  env/yapılandırma destekli kimlik doğrulamadan daha düşük öncelikli olarak işaretleyebilir
- `resolveDynamicModel`: sağlayıcı, yerel statik katalogda henüz bulunmayan model kimliklerini kabul eder
- `prepareDynamicModel`: sağlayıcının, dinamik çözümlemeyi yeniden denemeden önce
  meta veri yenilemesi gerekir
- `normalizeResolvedModel`: sağlayıcının taşıma veya temel URL yeniden yazımlarına ihtiyacı vardır
- `contributeResolvedModelCompat`: sağlayıcı, modeller başka bir uyumlu taşıma üzerinden gelse bile
  kendi satıcı modelleri için uyumluluk bayrakları sağlar
- `capabilities`: sağlayıcı, transkript/araçlama/sağlayıcı ailesi özelliklerini yayımlar
- `normalizeToolSchemas`: sağlayıcı, gömülü çalıştırıcı bunları görmeden önce
  araç şemalarını temizler
- `inspectToolSchemas`: sağlayıcı, normalleştirmeden sonra
  taşımaya özgü şema uyarılarını ortaya çıkarır
- `resolveReasoningOutputMode`: sağlayıcı, yerel ve etiketli
  muhakeme çıktısı sözleşmeleri arasında seçim yapar
- `prepareExtraParams`: sağlayıcı, model başına istek parametrelerini varsayılan hale getirir veya normalize eder
- `createStreamFn`: sağlayıcı, normal akış yolunu tamamen özel bir
  taşıma ile değiştirir
- `wrapStreamFn`: sağlayıcı, istek üstbilgisi/gövdesi/model uyumluluk sarmalayıcıları uygular
- `resolveTransportTurnState`: sağlayıcı, tur başına yerel taşıma
  üstbilgileri veya meta verileri sağlar
- `resolveWebSocketSessionPolicy`: sağlayıcı, yerel WebSocket oturumu
  üstbilgileri veya oturum cooldown ilkesini sağlar
- `createEmbeddingProvider`: sağlayıcı, bellek embedding davranışını sahiplenir; bu davranış
  çekirdek embedding anahtarlama mantığı yerine provider Plugin'i ile birlikte olmalıdır
- `formatApiKey`: sağlayıcı, depolanan kimlik doğrulama profillerini çalışma zamanının
  beklediği `apiKey` dizgesine biçimlendirir
- `refreshOAuth`: sağlayıcı, paylaşılan `pi-ai`
  yenileyicileri yeterli olmadığında OAuth yenilemeyi sahiplenir
- `buildAuthDoctorHint`: sağlayıcı, OAuth yenileme
  başarısız olduğunda onarım rehberliği ekler
- `matchesContextOverflowError`: sağlayıcı, genel sezgilerin kaçıracağı
  sağlayıcıya özgü bağlam penceresi taşma hatalarını tanır
- `classifyFailoverReason`: sağlayıcı, sağlayıcıya özgü ham taşıma/API
  hatalarını hız sınırı veya aşırı yük gibi failover nedenlerine eşler
- `isCacheTtlEligible`: sağlayıcı, hangi upstream model kimliklerinin prompt-cache TTL'yi desteklediğine karar verir
- `buildMissingAuthMessage`: sağlayıcı, genel auth-store hatasını
  sağlayıcıya özgü bir kurtarma ipucuyla değiştirir
- `suppressBuiltInModel`: sağlayıcı, eski upstream satırlarını gizler ve
  doğrudan çözümleme başarısızlıkları için satıcıya ait bir hata döndürebilir
- `augmentModelCatalog`: sağlayıcı, keşif ve yapılandırma birleştirmesinden sonra
  sentetik/nihai katalog satırları ekler
- `isBinaryThinking`: sağlayıcı, ikili aç/kapat düşünme UX'ini sahiplenir
- `supportsXHighThinking`: sağlayıcı, seçilen modelleri `xhigh` için etkinleştirir
- `resolveDefaultThinkingLevel`: sağlayıcı, bir model ailesi için varsayılan `/think` ilkesini sahiplenir
- `applyConfigDefaults`: sağlayıcı, kimlik doğrulama modu, env veya model ailesine göre
  yapılandırma somutlaştırması sırasında sağlayıcıya özgü genel varsayılanları uygular
- `isModernModelRef`: sağlayıcı, canlı/smoke tercih edilen model eşlemesini sahiplenir
- `prepareRuntimeAuth`: sağlayıcı, yapılandırılmış bir kimlik bilgisini kısa ömürlü
  bir çalışma zamanı belirtecine dönüştürür
- `resolveUsageAuth`: sağlayıcı, `/usage` ve ilgili durum/raporlama yüzeyleri için
  kullanım/kota kimlik bilgilerini çözer
- `fetchUsageSnapshot`: sağlayıcı, kullanım uç noktası getirme/ayrıştırmasını sahiplenirken
  çekirdek yine özet kabuğu ve biçimlendirmeyi sahiplenir
- `onModelSelected`: sağlayıcı, telemetri veya sağlayıcıya ait oturum kayıtları gibi
  model seçimi sonrası yan etkileri çalıştırır

Mevcut paketlenmiş örnekler:

- `anthropic`: Claude 4.6 ileri uyumluluk geri dönüşü, kimlik doğrulama onarım ipuçları, kullanım
  uç noktası getirme, cache-TTL/sağlayıcı ailesi meta verisi ve kimlik doğrulama farkındalıklı genel
  yapılandırma varsayılanları
- `amazon-bedrock`: Bedrock'a özgü throttle/hazır değil hataları için sağlayıcıya ait bağlam taşması eşleştirmesi ve failover
  nedeni sınıflandırması; ayrıca Anthropic trafiğinde yalnızca Claude için replay-policy
  korumaları sağlayan paylaşılan `anthropic-by-model` replay ailesi
- `anthropic-vertex`: Anthropic-message
  trafiğinde yalnızca Claude için replay-policy korumaları
- `openrouter`: doğrudan aktarılan model kimlikleri, istek sarmalayıcıları, sağlayıcı yetenek
  ipuçları, proxy Gemini trafiğinde Gemini thought-signature temizleme, `openrouter-thinking` akış ailesi üzerinden
  proxy muhakeme ekleme, yönlendirme meta verisi iletimi ve cache-TTL ilkesi
- `github-copilot`: onboarding/cihaz girişi, ileri uyumluluk model geri dönüşü,
  Claude-thinking transkript ipuçları, çalışma zamanı belirteç değişimi ve kullanım uç noktası
  getirme
- `openai`: GPT-5.4 ileri uyumluluk geri dönüşü, doğrudan OpenAI taşıma
  normalleştirmesi, Codex farkındalıklı eksik kimlik doğrulama ipuçları, Spark bastırma, sentetik
  OpenAI/Codex katalog satırları, thinking/canlı model ilkesi, kullanım belirteci takma ad
  normalleştirmesi (`input` / `output` ve `prompt` / `completion` aileleri), yerel OpenAI/Codex
  sarmalayıcıları için paylaşılan `openai-responses-defaults` akış ailesi, sağlayıcı ailesi meta verisi, paketlenmiş görsel oluşturma sağlayıcısı
  kaydı (`gpt-image-1` için) ve paketlenmiş video oluşturma sağlayıcısı
  kaydı (`sora-2` için)
- `google` ve `google-gemini-cli`: Gemini 3.1 ileri uyumluluk geri dönüşü,
  yerel Gemini replay doğrulaması, bootstrap replay temizleme, etiketli
  muhakeme çıktısı modu, modern model eşleştirmesi, Gemini image-preview modelleri için paketlenmiş görsel oluşturma
  sağlayıcısı kaydı ve Veo modelleri için paketlenmiş
  video oluşturma sağlayıcısı kaydı; Gemini CLI OAuth ayrıca
  kullanım yüzeyleri için kimlik doğrulama profili belirteç biçimlendirmesi, kullanım belirteci ayrıştırması ve kota uç noktası
  getirmesini de sahiplenir
- `moonshot`: paylaşılan taşıma, Plugin'e ait thinking payload normalleştirmesi
- `kilocode`: paylaşılan taşıma, Plugin'e ait istek üstbilgileri, muhakeme payload
  normalleştirmesi, proxy-Gemini thought-signature temizleme ve cache-TTL
  ilkesi
- `zai`: GLM-5 ileri uyumluluk geri dönüşü, `tool_stream` varsayılanları, cache-TTL
  ilkesi, ikili thinking/canlı model ilkesi ve kullanım kimlik doğrulaması + kota getirme;
  bilinmeyen `glm-5*` kimlikleri paketlenmiş `glm-4.7` şablonundan sentezlenir
- `xai`: yerel Responses taşıma normalleştirmesi, Grok hızlı varyantları için
  `/fast` takma ad yeniden yazımları, varsayılan `tool_stream`, xAI'ye özgü araç şeması /
  muhakeme payload temizleme ve `grok-imagine-video` için paketlenmiş video oluşturma sağlayıcısı
  kaydı
- `mistral`: Plugin'e ait yetenek meta verisi
- `opencode` ve `opencode-go`: Plugin'e ait yetenek meta verisi ve ayrıca
  proxy-Gemini thought-signature temizleme
- `alibaba`: `alibaba/wan2.6-t2v` gibi doğrudan Wan model başvuruları için
  Plugin'e ait video oluşturma kataloğu
- `byteplus`: Plugin'e ait kataloglar ve ayrıca Seedance metinden videoya/görselden videoya modelleri için paketlenmiş video oluşturma sağlayıcısı
  kaydı
- `fal`: barındırılan üçüncü taraf video modelleri için paketlenmiş video oluşturma sağlayıcısı
  kaydı ve ayrıca FLUX görsel modelleri için görsel oluşturma sağlayıcısı kaydı ile birlikte
  barındırılan üçüncü taraf video modelleri için paketlenmiş video oluşturma sağlayıcısı kaydı
- `cloudflare-ai-gateway`, `huggingface`, `kimi`, `nvidia`, `qianfan`,
  `stepfun`, `synthetic`, `venice`, `vercel-ai-gateway` ve `volcengine`:
  yalnızca Plugin'e ait kataloglar
- `qwen`: metin modelleri için Plugin'e ait kataloglar ve ayrıca
  çok modlu yüzeyleri için paylaşılan media-understanding ve video oluşturma sağlayıcısı kayıtları;
  Qwen video oluşturma, `wan2.6-t2v` ve `wan2.7-r2v` gibi paketlenmiş Wan modelleriyle
  standart DashScope video uç noktalarını kullanır
- `runway`: `gen4.5` gibi yerel
  Runway görev tabanlı modelleri için Plugin'e ait video oluşturma sağlayıcısı kaydı
- `minimax`: Plugin'e ait kataloglar, Hailuo video modelleri için paketlenmiş video oluşturma sağlayıcısı
  kaydı, `image-01` için paketlenmiş görsel oluşturma sağlayıcısı
  kaydı, hibrit Anthropic/OpenAI replay-policy
  seçimi ve kullanım kimlik doğrulaması/anlık görüntü mantığı
- `together`: Plugin'e ait kataloglar ve ayrıca Wan video modelleri için paketlenmiş video oluşturma sağlayıcısı
  kaydı
- `xiaomi`: Plugin'e ait kataloglar ve ayrıca kullanım kimlik doğrulaması/anlık görüntü mantığı

Paketlenmiş `openai` Plugin'i artık her iki sağlayıcı kimliğini de sahipleniyor: `openai` ve
`openai-codex`.

Bu, hâlâ OpenClaw'ın normal taşımalarına uyan sağlayıcıları kapsar. Tamamen özel bir istek yürütücüsüne ihtiyaç duyan bir sağlayıcı
ayrı ve daha derin bir genişletme yüzeyidir.

## API anahtarı rotasyonu

- Seçili sağlayıcılar için genel sağlayıcı rotasyonunu destekler.
- Birden çok anahtarı şu yollarla yapılandırın:
  - `OPENCLAW_LIVE_<PROVIDER>_KEY` (tek canlı geçersiz kılma, en yüksek öncelik)
  - `<PROVIDER>_API_KEYS` (virgül veya noktalı virgülle ayrılmış liste)
  - `<PROVIDER>_API_KEY` (birincil anahtar)
  - `<PROVIDER>_API_KEY_*` (numaralandırılmış liste, ör. `<PROVIDER>_API_KEY_1`)
- Google sağlayıcıları için `GOOGLE_API_KEY` de geri dönüş olarak dahil edilir.
- Anahtar seçim sırası önceliği korur ve değerleri tekilleştirir.
- İstekler yalnızca hız sınırı yanıtlarında bir sonraki anahtarla yeniden denenir (
  örneğin `429`, `rate_limit`, `quota`, `resource exhausted`, `Too many
concurrent requests`, `ThrottlingException`, `concurrency limit reached`,
  `workers_ai ... quota limit exceeded` veya dönemsel kullanım sınırı iletileri).
- Hız sınırı dışındaki hatalar hemen başarısız olur; anahtar rotasyonu denenmez.
- Tüm aday anahtarlar başarısız olduğunda, son hata son denemeden döndürülür.

## Yerleşik sağlayıcılar (pi-ai kataloğu)

OpenClaw, pi‑ai kataloğuyla birlikte gelir. Bu sağlayıcılar için **hiç**
`models.providers` yapılandırması gerekmez; yalnızca kimlik doğrulamayı ayarlayın ve bir model seçin.

### OpenAI

- Sağlayıcı: `openai`
- Kimlik doğrulama: `OPENAI_API_KEY`
- İsteğe bağlı rotasyon: `OPENAI_API_KEYS`, `OPENAI_API_KEY_1`, `OPENAI_API_KEY_2`, ayrıca `OPENCLAW_LIVE_OPENAI_KEY` (tek geçersiz kılma)
- Örnek modeller: `openai/gpt-5.4`, `openai/gpt-5.4-pro`
- CLI: `openclaw onboard --auth-choice openai-api-key`
- Varsayılan taşıma `auto`'dur (önce WebSocket, sonra SSE geri dönüşü)
- Model başına geçersiz kılmak için `agents.defaults.models["openai/<model>"].params.transport` kullanın (`"sse"`, `"websocket"` veya `"auto"`)
- OpenAI Responses WebSocket ön ısıtma varsayılan olarak `params.openaiWsWarmup` üzerinden etkindir (`true`/`false`)
- OpenAI öncelikli işleme `agents.defaults.models["openai/<model>"].params.serviceTier` ile etkinleştirilebilir
- `/fast` ve `params.fastMode`, doğrudan `openai/*` Responses isteklerini `api.openai.com` üzerinde `service_tier=priority` değerine eşler
- Paylaşılan `/fast` geçişi yerine açık bir katman istediğinizde `params.serviceTier` kullanın
- Gizli OpenClaw atıf üstbilgileri (`originator`, `version`,
  `User-Agent`) yalnızca `api.openai.com` adresine giden yerel OpenAI trafiğinde uygulanır,
  genel OpenAI uyumlu proxy'lerde uygulanmaz
- Yerel OpenAI yolları ayrıca Responses `store`, prompt-cache ipuçları ve
  OpenAI reasoning-compat payload şekillendirmesini korur; proxy yolları korumaz
- `openai/gpt-5.3-codex-spark`, canlı OpenAI API'si bunu reddettiği için OpenClaw'da bilerek bastırılır; Spark yalnızca Codex'e özgü kabul edilir

```json5
{
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

### Anthropic

- Sağlayıcı: `anthropic`
- Kimlik doğrulama: `ANTHROPIC_API_KEY`
- İsteğe bağlı rotasyon: `ANTHROPIC_API_KEYS`, `ANTHROPIC_API_KEY_1`, `ANTHROPIC_API_KEY_2`, ayrıca `OPENCLAW_LIVE_ANTHROPIC_KEY` (tek geçersiz kılma)
- Örnek model: `anthropic/claude-opus-4-6`
- CLI: `openclaw onboard --auth-choice apiKey`
- Doğrudan genel Anthropic istekleri, `api.anthropic.com` adresine gönderilen API anahtarıyla ve OAuth ile kimliği doğrulanmış trafikte dahil olmak üzere, paylaşılan `/fast` geçişini ve `params.fastMode` değerini de destekler; OpenClaw bunu Anthropic `service_tier` değerine eşler (`auto` ve `standard_only`)
- Anthropic notu: Anthropic çalışanları bize OpenClaw tarzı Claude CLI kullanımına tekrar izin verildiğini söyledi, bu nedenle Anthropic yeni bir ilke yayımlamadıkça OpenClaw, Claude CLI yeniden kullanımını ve `claude -p` kullanımını bu entegrasyon için onaylı kabul eder.
- Anthropic setup-token desteklenen bir OpenClaw belirteç yolu olarak kullanılmaya devam eder, ancak OpenClaw artık mümkün olduğunda Claude CLI yeniden kullanımını ve `claude -p` yolunu tercih eder.

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

### OpenAI Code (Codex)

- Sağlayıcı: `openai-codex`
- Kimlik doğrulama: OAuth (ChatGPT)
- Örnek model: `openai-codex/gpt-5.4`
- CLI: `openclaw onboard --auth-choice openai-codex` veya `openclaw models auth login --provider openai-codex`
- Varsayılan taşıma `auto`'dur (önce WebSocket, sonra SSE geri dönüşü)
- Model başına geçersiz kılmak için `agents.defaults.models["openai-codex/<model>"].params.transport` kullanın (`"sse"`, `"websocket"` veya `"auto"`)
- `params.serviceTier` yerel Codex Responses isteklerinde de iletilir (`chatgpt.com/backend-api`)
- Gizli OpenClaw atıf üstbilgileri (`originator`, `version`,
  `User-Agent`) yalnızca `chatgpt.com/backend-api` adresine giden yerel Codex trafiğinde
  eklenir, genel OpenAI uyumlu proxy'lerde eklenmez
- Doğrudan `openai/*` ile aynı `/fast` geçişini ve `params.fastMode` yapılandırmasını paylaşır; OpenClaw bunu `service_tier=priority` değerine eşler
- `openai-codex/gpt-5.3-codex-spark`, Codex OAuth kataloğu bunu gösterdiğinde kullanılabilir olmaya devam eder; yetkiye bağlıdır
- `openai-codex/gpt-5.4`, yerel `contextWindow = 1050000` ve varsayılan çalışma zamanı `contextTokens = 272000` değerlerini korur; çalışma zamanı sınırını `models.providers.openai-codex.models[].contextTokens` ile geçersiz kılın
- İlke notu: OpenAI Codex OAuth, OpenClaw gibi harici araçlar/iş akışları için açıkça desteklenir.

```json5
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
}
```

```json5
{
  models: {
    providers: {
      "openai-codex": {
        models: [{ id: "gpt-5.4", contextTokens: 160000 }],
      },
    },
  },
}
```

### Diğer abonelik tarzı barındırılan seçenekler

- [Qwen Cloud](/tr/providers/qwen): Qwen Cloud sağlayıcı yüzeyi ve ayrıca Alibaba DashScope ile Coding Plan uç nokta eşlemesi
- [MiniMax](/tr/providers/minimax): MiniMax Coding Plan OAuth veya API anahtarı erişimi
- [GLM Models](/tr/providers/glm): Z.AI Coding Plan veya genel API uç noktaları

### OpenCode

- Kimlik doğrulama: `OPENCODE_API_KEY` (veya `OPENCODE_ZEN_API_KEY`)
- Zen çalışma zamanı sağlayıcısı: `opencode`
- Go çalışma zamanı sağlayıcısı: `opencode-go`
- Örnek modeller: `opencode/claude-opus-4-6`, `opencode-go/kimi-k2.5`
- CLI: `openclaw onboard --auth-choice opencode-zen` veya `openclaw onboard --auth-choice opencode-go`

```json5
{
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-6" } } },
}
```

### Google Gemini (API anahtarı)

- Sağlayıcı: `google`
- Kimlik doğrulama: `GEMINI_API_KEY`
- İsteğe bağlı rotasyon: `GEMINI_API_KEYS`, `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`, `GOOGLE_API_KEY` geri dönüşü ve `OPENCLAW_LIVE_GEMINI_KEY` (tek geçersiz kılma)
- Örnek modeller: `google/gemini-3.1-pro-preview`, `google/gemini-3-flash-preview`
- Uyumluluk: `google/gemini-3.1-flash-preview` kullanan eski OpenClaw yapılandırması `google/gemini-3-flash-preview` olarak normalize edilir
- CLI: `openclaw onboard --auth-choice gemini-api-key`
- Doğrudan Gemini çalıştırmaları ayrıca sağlayıcıya özgü yerel bir
  `cachedContents/...` tanıtıcısını iletmek için `agents.defaults.models["google/<model>"].params.cachedContent`
  (veya eski `cached_content`) kabul eder; Gemini önbellek isabetleri OpenClaw `cacheRead` olarak görünür

### Google Vertex ve Gemini CLI

- Sağlayıcılar: `google-vertex`, `google-gemini-cli`
- Kimlik doğrulama: Vertex, gcloud ADC kullanır; Gemini CLI ise kendi OAuth akışını kullanır
- Dikkat: OpenClaw içindeki Gemini CLI OAuth resmi olmayan bir entegrasyondur. Bazı kullanıcılar, üçüncü taraf istemcileri kullandıktan sonra Google hesaplarında kısıtlamalar bildirildiğini belirtti. İlerlemeyi seçerseniz Google şartlarını gözden geçirin ve kritik olmayan bir hesap kullanın.
- Gemini CLI OAuth, paketlenmiş `google` Plugin'inin bir parçası olarak sunulur.
  - Önce Gemini CLI'yi yükleyin:
    - `brew install gemini-cli`
    - veya `npm install -g @google/gemini-cli`
  - Etkinleştirin: `openclaw plugins enable google`
  - Giriş yapın: `openclaw models auth login --provider google-gemini-cli --set-default`
  - Varsayılan model: `google-gemini-cli/gemini-3-flash-preview`
  - Not: `openclaw.json` içine bir istemci kimliği veya gizli anahtar yapıştırmazsınız. CLI giriş akışı,
    belirteçleri Gateway ana makinesindeki auth profillerinde depolar.
  - Girişten sonra istekler başarısız olursa, Gateway ana makinesinde `GOOGLE_CLOUD_PROJECT` veya `GOOGLE_CLOUD_PROJECT_ID` ayarlayın.
  - Gemini CLI JSON yanıtları `response` alanından ayrıştırılır; kullanım bilgisi
    `stats` alanına geri döner ve `stats.cached`, OpenClaw `cacheRead` olarak normalize edilir.

### Z.AI (GLM)

- Sağlayıcı: `zai`
- Kimlik doğrulama: `ZAI_API_KEY`
- Örnek model: `zai/glm-5.1`
- CLI: `openclaw onboard --auth-choice zai-api-key`
  - Takma adlar: `z.ai/*` ve `z-ai/*`, `zai/*` olarak normalize edilir
  - `zai-api-key`, eşleşen Z.AI uç noktasını otomatik algılar; `zai-coding-global`, `zai-coding-cn`, `zai-global` ve `zai-cn` belirli bir yüzeyi zorlar

### Vercel AI Gateway

- Sağlayıcı: `vercel-ai-gateway`
- Kimlik doğrulama: `AI_GATEWAY_API_KEY`
- Örnek model: `vercel-ai-gateway/anthropic/claude-opus-4.6`
- CLI: `openclaw onboard --auth-choice ai-gateway-api-key`

### Kilo Gateway

- Sağlayıcı: `kilocode`
- Kimlik doğrulama: `KILOCODE_API_KEY`
- Örnek model: `kilocode/kilo/auto`
- CLI: `openclaw onboard --auth-choice kilocode-api-key`
- Temel URL: `https://api.kilo.ai/api/gateway/`
- Statik geri dönüş kataloğu `kilocode/kilo/auto` ile birlikte gelir; canlı
  `https://api.kilo.ai/api/gateway/models` keşfi çalışma zamanı
  kataloğunu daha da genişletebilir.
- `kilocode/kilo/auto` arkasındaki tam upstream yönlendirme Kilo Gateway'e aittir,
  OpenClaw içinde sabit kodlanmış değildir.

Kurulum ayrıntıları için [/providers/kilocode](/tr/providers/kilocode) sayfasına bakın.

### Diğer paketlenmiş provider Plugin'leri

- OpenRouter: `openrouter` (`OPENROUTER_API_KEY`)
- Örnek model: `openrouter/auto`
- OpenClaw, OpenRouter'ın belgelenmiş uygulama atıf üstbilgilerini yalnızca
  istek gerçekten `openrouter.ai` hedefine gidiyorsa uygular
- OpenRouter'a özgü Anthropic `cache_control` işaretçileri de aynı şekilde
  doğrulanmış OpenRouter yollarıyla sınırlıdır, rastgele proxy URL'leriyle değil
- OpenRouter, proxy tarzı OpenAI uyumlu yol üzerinde kalır; bu nedenle
  yalnızca yerel OpenAI'ye özgü istek şekillendirmesi (`serviceTier`, Responses `store`,
  prompt-cache ipuçları, OpenAI reasoning-compat payload'ları) iletilmez
- Gemini destekli OpenRouter başvuruları yalnızca proxy-Gemini thought-signature temizliğini korur;
  yerel Gemini replay doğrulaması ve bootstrap yeniden yazımları kapalı kalır
- Kilo Gateway: `kilocode` (`KILOCODE_API_KEY`)
- Örnek model: `kilocode/kilo/auto`
- Gemini destekli Kilo başvuruları aynı proxy-Gemini thought-signature
  temizleme yolunu korur; `kilocode/kilo/auto` ve proxy muhakeme eklemeyi desteklemeyen
  diğer ipuçları proxy muhakeme eklemeyi atlar
- MiniMax: `minimax` (API anahtarı) ve `minimax-portal` (OAuth)
- Kimlik doğrulama: `minimax` için `MINIMAX_API_KEY`; `minimax-portal` için `MINIMAX_OAUTH_TOKEN` veya `MINIMAX_API_KEY`
- Örnek model: `minimax/MiniMax-M2.7` veya `minimax-portal/MiniMax-M2.7`
- MiniMax onboarding/API anahtarı kurulumu, açık M2.7 model tanımlarını
  `input: ["text", "image"]` ile yazar; paketlenmiş sağlayıcı kataloğu bu sağlayıcı yapılandırması somutlaştırılana kadar
  sohbet başvurularını yalnızca metin olarak tutar
- Moonshot: `moonshot` (`MOONSHOT_API_KEY`)
- Örnek model: `moonshot/kimi-k2.5`
- Kimi Coding: `kimi` (`KIMI_API_KEY` veya `KIMICODE_API_KEY`)
- Örnek model: `kimi/kimi-code`
- Qianfan: `qianfan` (`QIANFAN_API_KEY`)
- Örnek model: `qianfan/deepseek-v3.2`
- Qwen Cloud: `qwen` (`QWEN_API_KEY`, `MODELSTUDIO_API_KEY` veya `DASHSCOPE_API_KEY`)
- Örnek model: `qwen/qwen3.5-plus`
- NVIDIA: `nvidia` (`NVIDIA_API_KEY`)
- Örnek model: `nvidia/nvidia/llama-3.1-nemotron-70b-instruct`
- StepFun: `stepfun` / `stepfun-plan` (`STEPFUN_API_KEY`)
- Örnek modeller: `stepfun/step-3.5-flash`, `stepfun-plan/step-3.5-flash-2603`
- Together: `together` (`TOGETHER_API_KEY`)
- Örnek model: `together/moonshotai/Kimi-K2.5`
- Venice: `venice` (`VENICE_API_KEY`)
- Xiaomi: `xiaomi` (`XIAOMI_API_KEY`)
- Örnek model: `xiaomi/mimo-v2-flash`
- Vercel AI Gateway: `vercel-ai-gateway` (`AI_GATEWAY_API_KEY`)
- Hugging Face Inference: `huggingface` (`HUGGINGFACE_HUB_TOKEN` veya `HF_TOKEN`)
- Cloudflare AI Gateway: `cloudflare-ai-gateway` (`CLOUDFLARE_AI_GATEWAY_API_KEY`)
- Volcengine: `volcengine` (`VOLCANO_ENGINE_API_KEY`)
- Örnek model: `volcengine-plan/ark-code-latest`
- BytePlus: `byteplus` (`BYTEPLUS_API_KEY`)
- Örnek model: `byteplus-plan/ark-code-latest`
- xAI: `xai` (`XAI_API_KEY`)
  - Yerel paketlenmiş xAI istekleri xAI Responses yolunu kullanır
  - `/fast` veya `params.fastMode: true`, `grok-3`, `grok-3-mini`,
    `grok-4` ve `grok-4-0709` değerlerini kendi `*-fast` varyantlarına yeniden yazar
  - `tool_stream` varsayılan olarak açıktır; devre dışı bırakmak için
    `agents.defaults.models["xai/<model>"].params.tool_stream` değerini `false`
    yapın
- Mistral: `mistral` (`MISTRAL_API_KEY`)
- Örnek model: `mistral/mistral-large-latest`
- CLI: `openclaw onboard --auth-choice mistral-api-key`
- Groq: `groq` (`GROQ_API_KEY`)
- Cerebras: `cerebras` (`CEREBRAS_API_KEY`)
  - Cerebras üzerindeki GLM modelleri `zai-glm-4.7` ve `zai-glm-4.6` kimliklerini kullanır.
  - OpenAI uyumlu temel URL: `https://api.cerebras.ai/v1`.
- GitHub Copilot: `github-copilot` (`COPILOT_GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_TOKEN`)
- Hugging Face Inference örnek modeli: `huggingface/deepseek-ai/DeepSeek-R1`; CLI: `openclaw onboard --auth-choice huggingface-api-key`. Bkz. [Hugging Face (Inference)](/tr/providers/huggingface).

## `models.providers` aracılığıyla sağlayıcılar (özel/base URL)

**Özel** sağlayıcılar veya
OpenAI/Anthropic uyumlu proxy'ler eklemek için `models.providers` (veya `models.json`) kullanın.

Aşağıdaki paketlenmiş provider Plugin'lerinin birçoğu zaten varsayılan bir katalog yayımlar.
Varsayılan base URL, üstbilgiler veya model listesini geçersiz kılmak istediğinizde yalnızca açık
`models.providers.<id>` girişlerini kullanın.

### Moonshot AI (Kimi)

Moonshot, paketlenmiş bir provider Plugin'i olarak sunulur. Varsayılan olarak yerleşik sağlayıcıyı kullanın;
yalnızca base URL veya model meta verisini geçersiz kılmanız gerektiğinde açık bir `models.providers.moonshot` girdisi ekleyin:

- Sağlayıcı: `moonshot`
- Kimlik doğrulama: `MOONSHOT_API_KEY`
- Örnek model: `moonshot/kimi-k2.5`
- CLI: `openclaw onboard --auth-choice moonshot-api-key` veya `openclaw onboard --auth-choice moonshot-api-key-cn`

Kimi K2 model kimlikleri:

[//]: # "moonshot-kimi-k2-model-refs:start"

- `moonshot/kimi-k2.5`
- `moonshot/kimi-k2-thinking`
- `moonshot/kimi-k2-thinking-turbo`
- `moonshot/kimi-k2-turbo`

[//]: # "moonshot-kimi-k2-model-refs:end"

```json5
{
  agents: {
    defaults: { model: { primary: "moonshot/kimi-k2.5" } },
  },
  models: {
    mode: "merge",
    providers: {
      moonshot: {
        baseUrl: "https://api.moonshot.ai/v1",
        apiKey: "${MOONSHOT_API_KEY}",
        api: "openai-completions",
        models: [{ id: "kimi-k2.5", name: "Kimi K2.5" }],
      },
    },
  },
}
```

### Kimi Coding

Kimi Coding, Moonshot AI'nin Anthropic uyumlu uç noktasını kullanır:

- Sağlayıcı: `kimi`
- Kimlik doğrulama: `KIMI_API_KEY`
- Örnek model: `kimi/kimi-code`

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: { model: { primary: "kimi/kimi-code" } },
  },
}
```

Eski `kimi/k2p5` kimliği uyumluluk model kimliği olarak kabul edilmeye devam eder.

### Volcano Engine (Doubao)

Volcano Engine (火山引擎), Çin'de Doubao ve diğer modellere erişim sağlar.

- Sağlayıcı: `volcengine` (kodlama: `volcengine-plan`)
- Kimlik doğrulama: `VOLCANO_ENGINE_API_KEY`
- Örnek model: `volcengine-plan/ark-code-latest`
- CLI: `openclaw onboard --auth-choice volcengine-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "volcengine-plan/ark-code-latest" } },
  },
}
```

Onboarding varsayılan olarak kodlama yüzeyini kullanır, ancak genel `volcengine/*`
kataloğu da aynı anda kaydedilir.

Onboarding/model yapılandırma seçicilerinde Volcengine kimlik doğrulama seçeneği hem
`volcengine/*` hem de `volcengine-plan/*` satırlarını tercih eder. Bu modeller henüz yüklenmemişse,
OpenClaw boş bir sağlayıcı kapsamlı seçici göstermek yerine
filtresiz kataloğa geri döner.

Kullanılabilir modeller:

- `volcengine/doubao-seed-1-8-251228` (Doubao Seed 1.8)
- `volcengine/doubao-seed-code-preview-251028`
- `volcengine/kimi-k2-5-260127` (Kimi K2.5)
- `volcengine/glm-4-7-251222` (GLM 4.7)
- `volcengine/deepseek-v3-2-251201` (DeepSeek V3.2 128K)

Kodlama modelleri (`volcengine-plan`):

- `volcengine-plan/ark-code-latest`
- `volcengine-plan/doubao-seed-code`
- `volcengine-plan/kimi-k2.5`
- `volcengine-plan/kimi-k2-thinking`
- `volcengine-plan/glm-4.7`

### BytePlus (Uluslararası)

BytePlus ARK, uluslararası kullanıcılar için Volcano Engine ile aynı modellere erişim sağlar.

- Sağlayıcı: `byteplus` (kodlama: `byteplus-plan`)
- Kimlik doğrulama: `BYTEPLUS_API_KEY`
- Örnek model: `byteplus-plan/ark-code-latest`
- CLI: `openclaw onboard --auth-choice byteplus-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "byteplus-plan/ark-code-latest" } },
  },
}
```

Onboarding varsayılan olarak kodlama yüzeyini kullanır, ancak genel `byteplus/*`
kataloğu da aynı anda kaydedilir.

Onboarding/model yapılandırma seçicilerinde BytePlus kimlik doğrulama seçeneği hem
`byteplus/*` hem de `byteplus-plan/*` satırlarını tercih eder. Bu modeller henüz yüklenmemişse,
OpenClaw boş bir sağlayıcı kapsamlı seçici göstermek yerine
filtresiz kataloğa geri döner.

Kullanılabilir modeller:

- `byteplus/seed-1-8-251228` (Seed 1.8)
- `byteplus/kimi-k2-5-260127` (Kimi K2.5)
- `byteplus/glm-4-7-251222` (GLM 4.7)

Kodlama modelleri (`byteplus-plan`):

- `byteplus-plan/ark-code-latest`
- `byteplus-plan/doubao-seed-code`
- `byteplus-plan/kimi-k2.5`
- `byteplus-plan/kimi-k2-thinking`
- `byteplus-plan/glm-4.7`

### Synthetic

Synthetic, `synthetic` sağlayıcısının arkasında Anthropic uyumlu modeller sunar:

- Sağlayıcı: `synthetic`
- Kimlik doğrulama: `SYNTHETIC_API_KEY`
- Örnek model: `synthetic/hf:MiniMaxAI/MiniMax-M2.5`
- CLI: `openclaw onboard --auth-choice synthetic-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "synthetic/hf:MiniMaxAI/MiniMax-M2.5" } },
  },
  models: {
    mode: "merge",
    providers: {
      synthetic: {
        baseUrl: "https://api.synthetic.new/anthropic",
        apiKey: "${SYNTHETIC_API_KEY}",
        api: "anthropic-messages",
        models: [{ id: "hf:MiniMaxAI/MiniMax-M2.5", name: "MiniMax M2.5" }],
      },
    },
  },
}
```

### MiniMax

MiniMax, özel uç noktalar kullandığı için `models.providers` üzerinden yapılandırılır:

- MiniMax OAuth (Global): `--auth-choice minimax-global-oauth`
- MiniMax OAuth (CN): `--auth-choice minimax-cn-oauth`
- MiniMax API anahtarı (Global): `--auth-choice minimax-global-api`
- MiniMax API anahtarı (CN): `--auth-choice minimax-cn-api`
- Kimlik doğrulama: `minimax` için `MINIMAX_API_KEY`; `minimax-portal` için `MINIMAX_OAUTH_TOKEN` veya
  `MINIMAX_API_KEY`

Kurulum ayrıntıları, model seçenekleri ve yapılandırma parçacıkları için [/providers/minimax](/tr/providers/minimax) sayfasına bakın.

MiniMax'in Anthropic uyumlu akış yolunda OpenClaw,
açıkça ayarlamadığınız sürece varsayılan olarak thinking'i devre dışı bırakır ve `/fast on`
`MiniMax-M2.7` değerini `MiniMax-M2.7-highspeed` olarak yeniden yazar.

Plugin'e ait yetenek ayrımı:

- Metin/sohbet varsayılanları `minimax/MiniMax-M2.7` üzerinde kalır
- Görsel oluşturma `minimax/image-01` veya `minimax-portal/image-01` olur
- Görsel anlama, her iki MiniMax kimlik doğrulama yolunda da Plugin'e ait `MiniMax-VL-01`'dir
- Web araması `minimax` sağlayıcı kimliğinde kalır

### LM Studio

LM Studio, yerel API'yi kullanan paketlenmiş bir provider Plugin'i olarak sunulur:

- Sağlayıcı: `lmstudio`
- Kimlik doğrulama: `LM_API_TOKEN`
- Varsayılan çıkarım base URL'si: `http://localhost:1234/v1`

Ardından bir model ayarlayın (`http://localhost:1234/api/v1/models` tarafından döndürülen kimliklerden biriyle değiştirin):

```json5
{
  agents: {
    defaults: { model: { primary: "lmstudio/openai/gpt-oss-20b" } },
  },
}
```

OpenClaw, keşif + otomatik yükleme için LM Studio'nun yerel `/api/v1/models` ve `/api/v1/models/load`
uç noktalarını, varsayılan olarak çıkarım için ise `/v1/chat/completions` uç noktasını kullanır.
Kurulum ve sorun giderme için [/providers/lmstudio](/tr/providers/lmstudio) sayfasına bakın.

### Ollama

Ollama, paketlenmiş bir provider Plugin'i olarak sunulur ve Ollama'nın yerel API'sini kullanır:

- Sağlayıcı: `ollama`
- Kimlik doğrulama: Gerekmez (yerel sunucu)
- Örnek model: `ollama/llama3.3`
- Kurulum: [https://ollama.com/download](https://ollama.com/download)

```bash
# Ollama'yı yükleyin, ardından bir model çekin:
ollama pull llama3.3
```

```json5
{
  agents: {
    defaults: { model: { primary: "ollama/llama3.3" } },
  },
}
```

`OLLAMA_API_KEY` ile katılım sağladığınızda Ollama yerel olarak `http://127.0.0.1:11434` adresinde algılanır ve paketlenmiş provider Plugin'i Ollama'yı doğrudan
`openclaw onboard` ve model seçiciye ekler. Onboarding, bulut/yerel mod ve özel yapılandırma için [/providers/ollama](/tr/providers/ollama)
sayfasına bakın.

### vLLM

vLLM, yerel/self-hosted OpenAI uyumlu
sunucular için paketlenmiş bir provider Plugin'i olarak sunulur:

- Sağlayıcı: `vllm`
- Kimlik doğrulama: İsteğe bağlıdır (sunucunuza bağlıdır)
- Varsayılan base URL: `http://127.0.0.1:8000/v1`

Yerelde otomatik keşfe katılmak için (sunucunuz kimlik doğrulamayı zorlamıyorsa herhangi bir değer çalışır):

```bash
export VLLM_API_KEY="vllm-local"
```

Ardından bir model ayarlayın (`/v1/models` tarafından döndürülen kimliklerden biriyle değiştirin):

```json5
{
  agents: {
    defaults: { model: { primary: "vllm/your-model-id" } },
  },
}
```

Ayrıntılar için [/providers/vllm](/tr/providers/vllm) sayfasına bakın.

### SGLang

SGLang, hızlı self-hosted
OpenAI uyumlu sunucular için paketlenmiş bir provider Plugin'i olarak sunulur:

- Sağlayıcı: `sglang`
- Kimlik doğrulama: İsteğe bağlıdır (sunucunuza bağlıdır)
- Varsayılan base URL: `http://127.0.0.1:30000/v1`

Yerelde otomatik keşfe katılmak için (sunucunuz kimlik doğrulamayı
zorlamıyorsa herhangi bir değer çalışır):

```bash
export SGLANG_API_KEY="sglang-local"
```

Ardından bir model ayarlayın (`/v1/models` tarafından döndürülen kimliklerden biriyle değiştirin):

```json5
{
  agents: {
    defaults: { model: { primary: "sglang/your-model-id" } },
  },
}
```

Ayrıntılar için [/providers/sglang](/tr/providers/sglang) sayfasına bakın.

### Yerel proxy'ler (LM Studio, vLLM, LiteLLM vb.)

Örnek (OpenAI uyumlu):

```json5
{
  agents: {
    defaults: {
      model: { primary: "lmstudio/my-local-model" },
      models: { "lmstudio/my-local-model": { alias: "Yerel" } },
    },
  },
  models: {
    providers: {
      lmstudio: {
        baseUrl: "http://localhost:1234/v1",
        apiKey: "${LM_API_TOKEN}",
        api: "openai-completions",
        models: [
          {
            id: "my-local-model",
            name: "Yerel Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 200000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

Notlar:

- Özel sağlayıcılar için `reasoning`, `input`, `cost`, `contextWindow` ve `maxTokens` isteğe bağlıdır.
  Belirtilmediğinde OpenClaw varsayılan olarak şunları kullanır:
  - `reasoning: false`
  - `input: ["text"]`
  - `cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 }`
  - `contextWindow: 200000`
  - `maxTokens: 8192`
- Önerilir: proxy/model sınırlarınızla eşleşen açık değerler ayarlayın.
- Yerel olmayan uç noktalardaki `api: "openai-completions"` için (`baseUrl` boş olmayan ve ana makinesi `api.openai.com` olmayan her URL), OpenClaw desteklenmeyen `developer` rolleri için sağlayıcı 400 hatalarını önlemek amacıyla `compat.supportsDeveloperRole: false` değerini zorunlu kılar.
- Proxy tarzı OpenAI uyumlu yollar, yerel OpenAI'ye özgü istek
  şekillendirmesini de atlar: `service_tier` yok, Responses `store` yok, prompt-cache ipuçları yok,
  OpenAI reasoning-compat payload şekillendirmesi yok ve gizli OpenClaw atıf
  üstbilgileri yok.
- `baseUrl` boşsa/belirtilmemişse OpenClaw varsayılan OpenAI davranışını korur (bu da `api.openai.com` adresine çözülür).
- Güvenlik için, yerel olmayan `openai-completions` uç noktalarında açık bir `compat.supportsDeveloperRole: true` değeri yine de geçersiz kılınır.

## CLI örnekleri

```bash
openclaw onboard --auth-choice opencode-zen
openclaw models set opencode/claude-opus-4-6
openclaw models list
```

Ayrıca bkz.: tam yapılandırma örnekleri için [/gateway/configuration](/tr/gateway/configuration).

## İlgili

- [Models](/tr/concepts/models) — model yapılandırması ve takma adlar
- [Model Failover](/tr/concepts/model-failover) — geri dönüş zincirleri ve yeniden deneme davranışı
- [Configuration Reference](/tr/gateway/configuration-reference#agent-defaults) — model yapılandırma anahtarları
- [Providers](/tr/providers) — sağlayıcı bazında kurulum kılavuzları
