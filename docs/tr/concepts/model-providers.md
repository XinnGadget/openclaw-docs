---
read_when:
    - Sağlayıcı bazında model kurulum başvurusu gerektiğinde
    - Model sağlayıcıları için örnek yapılandırmalar veya CLI onboarding komutları istediğinizde
summary: Örnek yapılandırmalar ve CLI akışlarıyla model sağlayıcısı genel bakışı
title: Model Sağlayıcıları
x-i18n:
    generated_at: "2026-04-08T02:15:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: 26b36a2bc19a28a7ef39aa8e81a0050fea1d452ac4969122e5cdf8755e690258
    source_path: concepts/model-providers.md
    workflow: 15
---

# Model sağlayıcıları

Bu sayfa **LLM/model sağlayıcılarını** kapsar (WhatsApp/Telegram gibi sohbet kanalları değil).
Model seçim kuralları için bkz. [/concepts/models](/tr/concepts/models).

## Hızlı kurallar

- Model başvuruları `provider/model` kullanır (örnek: `opencode/claude-opus-4-6`).
- `agents.defaults.models` ayarlarsanız bu allowlist olur.
- CLI yardımcıları: `openclaw onboard`, `openclaw models list`, `openclaw models set <provider/model>`.
- Yedek çalışma zamanı kuralları, cooldown propları ve oturum geçersiz kılma kalıcılığı
  [/concepts/model-failover](/tr/concepts/model-failover) içinde belgelenmiştir.
- `models.providers.*.models[].contextWindow` yerel model meta verisidir;
  `models.providers.*.models[].contextTokens` etkin çalışma zamanı sınırıdır.
- Sağlayıcı plugin’leri `registerProvider({ catalog })` aracılığıyla model katalogları ekleyebilir;
  OpenClaw bu çıktıyı `models.providers` içine birleştirir ve ardından
  `models.json` yazar.
- Sağlayıcı manifest’leri `providerAuthEnvVars` bildirebilir; böylece genel env tabanlı
  kimlik doğrulama yoklamalarının plugin çalışma zamanını yüklemesi gerekmez. Kalan çekirdek env-var
  eşlemesi artık yalnızca plugin olmayan/çekirdek sağlayıcılar ve Anthropic için API-key-first onboarding gibi
  birkaç genel öncelik durumu içindir.
- Sağlayıcı plugin’leri ayrıca
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
  `onModelSelected` aracılığıyla sağlayıcı çalışma zamanı davranışını sahiplenebilir.
- Not: sağlayıcı çalışma zamanı `capabilities`, paylaşılan çalıştırıcı meta verisidir (sağlayıcı
  ailesi, transkript/araç farklılıkları, taşıma/önbellek ipuçları). Bu,
  bir plugin’in ne kaydettiğini açıklayan
  [genel capability modeli](/tr/plugins/architecture#public-capability-model)
  ile aynı şey değildir (metin çıkarımı, konuşma vb.).

## Plugin’e ait sağlayıcı davranışı

Sağlayıcı plugin’leri artık sağlayıcıya özgü mantığın çoğunu sahiplenebilirken OpenClaw
genel çıkarım döngüsünü korur.

Tipik ayrım:

- `auth[].run` / `auth[].runNonInteractive`: sağlayıcı,
  `openclaw onboard`, `openclaw models auth` ve başsız kurulum için onboarding/login
  akışlarını sahiplenir
- `wizard.setup` / `wizard.modelPicker`: sağlayıcı, auth-choice etiketlerini,
  eski takma adları, onboarding allowlist ipuçlarını ve onboarding/model seçimlerinde
  kurulum girişlerini sahiplenir
- `catalog`: sağlayıcı `models.providers` içinde görünür
- `normalizeModelId`: sağlayıcı, arama veya kanonikleştirme öncesinde eski/önizleme model kimliklerini
  normalize eder
- `normalizeTransport`: sağlayıcı, genel model derlemesi öncesinde taşıma ailesi `api` / `baseUrl` değerlerini
  normalize eder; OpenClaw önce eşleşen sağlayıcıyı,
  sonra gerçekten taşıma üzerinde değişiklik yapana kadar diğer hook destekli sağlayıcı plugin’lerini
  denetler
- `normalizeConfig`: sağlayıcı, çalışma zamanı kullanmadan önce `models.providers.<id>` yapılandırmasını
  normalize eder; OpenClaw önce eşleşen sağlayıcıyı,
  sonra gerçekten yapılandırmayı değiştirene kadar diğer hook destekli sağlayıcı plugin’lerini
  denetler. Hiçbir sağlayıcı hook’u yapılandırmayı yeniden yazmazsa, paketlenmiş Google ailesi yardımcıları
  desteklenen Google sağlayıcı girdilerini yine de normalize eder.
- `applyNativeStreamingUsageCompat`: sağlayıcı, yapılandırma sağlayıcıları için uç nokta odaklı yerel akış-kullanım uyumluluk yeniden yazımlarını uygular
- `resolveConfigApiKey`: sağlayıcı, yapılandırma sağlayıcıları için tam çalışma zamanı auth yüklemesini zorlamadan
  env-marker auth çözümler. Bedrock çalışma zamanı auth’u
  AWS SDK varsayılan zincirini kullansa da `amazon-bedrock` burada ayrıca
  yerleşik bir AWS env-marker çözücüsüne sahiptir.
- `resolveSyntheticAuth`: sağlayıcı, düz metin gizli anahtarları kalıcılaştırmadan
  local/self-hosted veya diğer yapılandırma destekli auth kullanılabilirliğini ortaya çıkarabilir
- `shouldDeferSyntheticProfileAuth`: sağlayıcı, depolanmış sentetik profil
  yer tutucularını env/config destekli auth’tan daha düşük öncelikli olarak işaretleyebilir
- `resolveDynamicModel`: sağlayıcı, henüz yerel statik katalogda bulunmayan model kimliklerini kabul eder
- `prepareDynamicModel`: sağlayıcı, dinamik çözümlemeyi yeniden denemeden önce meta veri yenilemesine ihtiyaç duyar
- `normalizeResolvedModel`: sağlayıcı, taşıma veya base URL yeniden yazımlarına ihtiyaç duyar
- `contributeResolvedModelCompat`: sağlayıcı, başka bir uyumlu taşıma üzerinden gelseler bile
  kendi satıcı modelleri için uyumluluk bayrakları sağlar
- `capabilities`: sağlayıcı, transkript/araçlama/sağlayıcı ailesi farklılıklarını yayımlar
- `normalizeToolSchemas`: sağlayıcı, gömülü çalıştırıcı onları görmeden önce araç şemalarını temizler
- `inspectToolSchemas`: sağlayıcı, normalleştirme sonrasında taşıma türüne özgü şema uyarılarını yüzeye çıkarır
- `resolveReasoningOutputMode`: sağlayıcı, yerel ve etiketli
  reasoning-output sözleşmeleri arasında seçim yapar
- `prepareExtraParams`: sağlayıcı, model başına istek parametreleri için varsayılanları uygular veya normalize eder
- `createStreamFn`: sağlayıcı, normal akış yolunu tamamen
  özel bir taşıma ile değiştirir
- `wrapStreamFn`: sağlayıcı, istek üstbilgisi/gövdesi/model uyumluluk sarmalayıcıları uygular
- `resolveTransportTurnState`: sağlayıcı, tur başına yerel taşıma
  üstbilgileri veya meta verileri sağlar
- `resolveWebSocketSessionPolicy`: sağlayıcı, yerel WebSocket oturumu
  üstbilgileri veya oturum cool-down politikasını sağlar
- `createEmbeddingProvider`: provider plugin’i yerine çekirdek embedding switchboard’a değil,
  sağlayıcı plugin’ine ait olduğunda bellek embedding davranışını sağlayıcı sahiplenir
- `formatApiKey`: sağlayıcı, depolanmış auth profillerini taşımanın beklediği
  çalışma zamanı `apiKey` dizesine biçimlendirir
- `refreshOAuth`: sağlayıcı, paylaşılan `pi-ai`
  yenileyiciler yeterli olmadığında OAuth yenilemeyi sahiplenir
- `buildAuthDoctorHint`: sağlayıcı, OAuth yenileme
  başarısız olduğunda onarım rehberliği ekler
- `matchesContextOverflowError`: sağlayıcı, genel sezgilerin kaçıracağı
  sağlayıcıya özgü context-window taşma hatalarını tanır
- `classifyFailoverReason`: sağlayıcı, sağlayıcıya özgü ham taşıma/API
  hatalarını hız sınırı veya aşırı yük gibi failover nedenlerine eşler
- `isCacheTtlEligible`: sağlayıcı, hangi yukarı akış model kimliklerinin prompt-cache TTL desteklediğine karar verir
- `buildMissingAuthMessage`: sağlayıcı, genel auth-store hatasını
  sağlayıcıya özgü bir kurtarma ipucuyla değiştirir
- `suppressBuiltInModel`: sağlayıcı, eski yukarı akış satırlarını gizler ve doğrudan çözümleme başarısızlıkları için
  satıcıya ait bir hata döndürebilir
- `augmentModelCatalog`: sağlayıcı, keşif ve yapılandırma birleştirmesinden sonra
  sentetik/nihai katalog satırları ekler
- `isBinaryThinking`: sağlayıcı, ikili açık/kapalı düşünme UX’ini sahiplenir
- `supportsXHighThinking`: sağlayıcı, seçili modelleri `xhigh` içine alır
- `resolveDefaultThinkingLevel`: sağlayıcı, bir model ailesi için varsayılan `/think` politikasını sahiplenir
- `applyConfigDefaults`: sağlayıcı, auth modu, env veya model ailesine göre
  yapılandırma materyalizasyonu sırasında sağlayıcıya özgü genel varsayılanlar uygular
- `isModernModelRef`: sağlayıcı, live/smoke tercih edilen model eşleştirmesini sahiplenir
- `prepareRuntimeAuth`: sağlayıcı, yapılandırılmış bir kimlik bilgisini kısa ömürlü bir
  çalışma zamanı belirtecine dönüştürür
- `resolveUsageAuth`: sağlayıcı, `/usage`
  ve ilgili durum/raporlama yüzeyleri için kullanım/kota kimlik bilgilerini çözer
- `fetchUsageSnapshot`: sağlayıcı, kullanım uç noktası alma/ayrıştırma işini sahiplenirken
  çekirdek yine özet kabuğunu ve biçimlendirmeyi sahiplenir
- `onModelSelected`: sağlayıcı, telemetri veya sağlayıcıya ait oturum kayıt tutma gibi
  seçim sonrası yan etkileri çalıştırır

Mevcut paketlenmiş örnekler:

- `anthropic`: Claude 4.6 ileri uyumluluk geri dönüşü, auth onarım ipuçları, kullanım
  uç noktası alma, cache-TTL/sağlayıcı ailesi meta verisi ve auth farkındalıklı genel
  yapılandırma varsayılanları
- `amazon-bedrock`: Bedrock’a özgü throttle/not-ready hataları için sağlayıcıya ait context-overflow eşleştirme ve failover
  neden sınıflandırması; ayrıca Anthropic trafiğindeki yalnızca-Claude replay-policy
  korumaları için paylaşılan `anthropic-by-model` replay ailesi
- `anthropic-vertex`: Anthropic-message
  trafiği için yalnızca-Claude replay-policy korumaları
- `openrouter`: doğrudan model kimlikleri, istek sarmalayıcıları, sağlayıcı capability
  ipuçları, proxy Gemini trafiğinde Gemini thought-signature temizleme,
  `openrouter-thinking` akış ailesi üzerinden proxy reasoning ekleme, yönlendirme
  meta verisi iletimi ve cache-TTL politikası
- `github-copilot`: onboarding/device login, ileri uyumluluk model geri dönüşü,
  Claude-thinking transkript ipuçları, çalışma zamanı token değişimi ve kullanım uç noktası
  alma
- `openai`: GPT-5.4 ileri uyumluluk geri dönüşü, doğrudan OpenAI taşıma
  normalizasyonu, Codex farkındalıklı eksik auth ipuçları, Spark gizleme, sentetik
  OpenAI/Codex katalog satırları, thinking/live-model politikası, kullanım token takma ad
  normalizasyonu (`input` / `output` ve `prompt` / `completion` aileleri), yerel OpenAI/Codex
  sarmalayıcıları için paylaşılan `openai-responses-defaults` akış ailesi, sağlayıcı ailesi
  meta verisi, `gpt-image-1` için paketlenmiş görüntü oluşturma sağlayıcısı
  kaydı ve `sora-2` için paketlenmiş video oluşturma sağlayıcısı
  kaydı
- `google` ve `google-gemini-cli`: Gemini 3.1 ileri uyumluluk geri dönüşü,
  yerel Gemini replay doğrulaması, bootstrap replay temizliği, etiketli
  reasoning-output modu, modern model eşleştirmesi, Gemini image-preview modelleri için paketlenmiş görüntü oluşturma
  sağlayıcısı kaydı ve Veo modelleri için paketlenmiş
  video oluşturma sağlayıcısı kaydı; Gemini CLI OAuth ayrıca
  auth-profile token biçimlendirmesi, usage-token ayrıştırması ve kullanım yüzeyleri için kota uç noktası
  alımını da sahiplenir
- `moonshot`: paylaşılan taşıma, plugin’e ait thinking payload normalizasyonu
- `kilocode`: paylaşılan taşıma, plugin’e ait istek üstbilgileri, reasoning payload
  normalizasyonu, proxy-Gemini thought-signature temizliği ve cache-TTL
  politikası
- `zai`: GLM-5 ileri uyumluluk geri dönüşü, `tool_stream` varsayılanları, cache-TTL
  politikası, binary-thinking/live-model politikası ve kullanım auth + kota alımı;
  bilinmeyen `glm-5*` kimlikleri, paketlenmiş `glm-4.7` şablonundan sentezlenir
- `xai`: yerel Responses taşıma normalizasyonu, Grok hızlı varyantları için
  `/fast` takma ad yeniden yazımları, varsayılan `tool_stream`, xAI’ye özgü tool-schema /
  reasoning-payload temizliği ve `grok-imagine-video` için paketlenmiş video oluşturma sağlayıcısı
  kaydı
- `mistral`: plugin’e ait capability meta verisi
- `opencode` ve `opencode-go`: plugin’e ait capability meta verisi ile birlikte
  proxy-Gemini thought-signature temizliği
- `alibaba`: `alibaba/wan2.6-t2v` gibi doğrudan Wan model başvuruları için
  plugin’e ait video oluşturma kataloğu
- `byteplus`: plugin’e ait kataloglar ve Seedance text-to-video/image-to-video modelleri için
  paketlenmiş video oluşturma sağlayıcısı kaydı
- `fal`: FLUX görüntü modelleri için barındırılan üçüncü taraf görüntü oluşturma sağlayıcısı kaydı ve
  barındırılan üçüncü taraf video modelleri için paketlenmiş
  video oluşturma sağlayıcısı kaydı
- `cloudflare-ai-gateway`, `huggingface`, `kimi`, `nvidia`, `qianfan`,
  `stepfun`, `synthetic`, `venice`, `vercel-ai-gateway` ve `volcengine`:
  yalnızca plugin’e ait kataloglar
- `qwen`: metin modelleri için plugin’e ait kataloglar ile birlikte,
  çok modlu yüzeyleri için paylaşılan media-understanding ve video-generation sağlayıcısı kayıtları;
  Qwen video oluşturma, `wan2.6-t2v` ve `wan2.7-r2v` gibi paketlenmiş Wan modelleriyle
  Standard DashScope video uç noktalarını kullanır
- `runway`: `gen4.5` gibi yerel
  Runway görev tabanlı modeller için plugin’e ait video oluşturma sağlayıcısı kaydı
- `minimax`: plugin’e ait kataloglar, Hailuo video modelleri için paketlenmiş video oluşturma sağlayıcısı
  kaydı, `image-01` için paketlenmiş görüntü oluşturma sağlayıcısı
  kaydı, hibrit Anthropic/OpenAI replay-policy
  seçimi ve kullanım auth/snapshot mantığı
- `together`: plugin’e ait kataloglar ve Wan video modelleri için paketlenmiş video oluşturma sağlayıcısı
  kaydı
- `xiaomi`: plugin’e ait kataloglar ile kullanım auth/snapshot mantığı

Paketlenmiş `openai` plugin’i artık her iki sağlayıcı kimliğini de sahipleniyor: `openai` ve
`openai-codex`.

Bu, OpenClaw’ın normal taşımalarına hâlâ uyan sağlayıcıları kapsar. Tamamen
özel bir istek yürütücüsüne ihtiyaç duyan sağlayıcılar ayrı, daha derin bir genişletme yüzeyidir.

## API anahtarı rotasyonu

- Seçili sağlayıcılar için genel sağlayıcı rotasyonunu destekler.
- Birden çok anahtarı şu yollarla yapılandırın:
  - `OPENCLAW_LIVE_<PROVIDER>_KEY` (tek canlı geçersiz kılma, en yüksek öncelik)
  - `<PROVIDER>_API_KEYS` (virgül veya noktalı virgül ayrımlı liste)
  - `<PROVIDER>_API_KEY` (birincil anahtar)
  - `<PROVIDER>_API_KEY_*` (numaralandırılmış liste, örn. `<PROVIDER>_API_KEY_1`)
- Google sağlayıcıları için `GOOGLE_API_KEY` de yedek olarak dahil edilir.
- Anahtar seçim sırası önceliği korur ve değerleri tekilleştirir.
- İstekler yalnızca hız sınırı yanıtlarında bir sonraki anahtarla yeniden denenir
  (örneğin `429`, `rate_limit`, `quota`, `resource exhausted`, `Too many
concurrent requests`, `ThrottlingException`, `concurrency limit reached`,
  `workers_ai ... quota limit exceeded` veya dönemsel kullanım sınırı iletileri).
- Hız sınırı dışındaki hatalar hemen başarısız olur; anahtar rotasyonu denenmez.
- Tüm aday anahtarlar başarısız olduğunda son hata, son denemeden döndürülür.

## Yerleşik sağlayıcılar (pi-ai kataloğu)

OpenClaw, pi‑ai kataloğuyla gelir. Bu sağlayıcılar için
`models.providers` yapılandırması **gerekmez**; yalnızca auth ayarlayın ve bir model seçin.

### OpenAI

- Sağlayıcı: `openai`
- Auth: `OPENAI_API_KEY`
- İsteğe bağlı rotasyon: `OPENAI_API_KEYS`, `OPENAI_API_KEY_1`, `OPENAI_API_KEY_2`, ayrıca `OPENCLAW_LIVE_OPENAI_KEY` (tek geçersiz kılma)
- Örnek modeller: `openai/gpt-5.4`, `openai/gpt-5.4-pro`
- CLI: `openclaw onboard --auth-choice openai-api-key`
- Varsayılan taşıma `auto`’dur (önce WebSocket, sonra SSE)
- Model başına geçersiz kılmak için `agents.defaults.models["openai/<model>"].params.transport` kullanın (`"sse"`, `"websocket"` veya `"auto"`)
- OpenAI Responses WebSocket ısınması varsayılan olarak `params.openaiWsWarmup` aracılığıyla etkindir (`true`/`false`)
- OpenAI öncelikli işleme, `agents.defaults.models["openai/<model>"].params.serviceTier` aracılığıyla etkinleştirilebilir
- `/fast` ve `params.fastMode`, doğrudan `openai/*` Responses isteklerini `api.openai.com` üzerinde `service_tier=priority` olarak eşler
- Paylaşılan `/fast` anahtarı yerine açık bir katman istiyorsanız `params.serviceTier` kullanın
- Gizli OpenClaw atıf üstbilgileri (`originator`, `version`,
  `User-Agent`) yalnızca `api.openai.com` üzerindeki yerel OpenAI trafiğinde uygulanır,
  genel OpenAI uyumlu proxy’lerde uygulanmaz
- Yerel OpenAI rotaları ayrıca Responses `store`, prompt-cache ipuçları ve
  OpenAI reasoning-compat payload şekillendirmesini korur; proxy rotaları korumaz
- `openai/gpt-5.3-codex-spark`, canlı OpenAI API bunu reddettiği için OpenClaw’da kasıtlı olarak gizlenir; Spark yalnızca Codex’e ait kabul edilir

```json5
{
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

### Anthropic

- Sağlayıcı: `anthropic`
- Auth: `ANTHROPIC_API_KEY`
- İsteğe bağlı rotasyon: `ANTHROPIC_API_KEYS`, `ANTHROPIC_API_KEY_1`, `ANTHROPIC_API_KEY_2`, ayrıca `OPENCLAW_LIVE_ANTHROPIC_KEY` (tek geçersiz kılma)
- Örnek model: `anthropic/claude-opus-4-6`
- CLI: `openclaw onboard --auth-choice apiKey`
- Doğrudan genel Anthropic istekleri, `api.anthropic.com` adresine gönderilen API anahtarı ve OAuth kimlik doğrulamalı trafik dahil,
  paylaşılan `/fast` anahtarını ve `params.fastMode` değerini destekler; OpenClaw bunu Anthropic `service_tier` değerine (`auto` ve `standard_only`) eşler
- Anthropic notu: Anthropic çalışanları, OpenClaw tarzı Claude CLI kullanımına yeniden izin verildiğini söyledi; bu yüzden Anthropic yeni bir politika yayımlamadığı sürece OpenClaw, Claude CLI yeniden kullanımını ve `claude -p` kullanımını bu entegrasyon için onaylı kabul eder.
- Anthropic setup-token, desteklenen bir OpenClaw token yolu olarak kullanılmaya devam eder, ancak OpenClaw artık mevcut olduğunda Claude CLI yeniden kullanımını ve `claude -p`’yi tercih eder.

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

### OpenAI Code (Codex)

- Sağlayıcı: `openai-codex`
- Auth: OAuth (ChatGPT)
- Örnek model: `openai-codex/gpt-5.4`
- CLI: `openclaw onboard --auth-choice openai-codex` veya `openclaw models auth login --provider openai-codex`
- Varsayılan taşıma `auto`’dur (önce WebSocket, sonra SSE)
- Model başına geçersiz kılmak için `agents.defaults.models["openai-codex/<model>"].params.transport` kullanın (`"sse"`, `"websocket"` veya `"auto"`)
- `params.serviceTier`, yerel Codex Responses isteklerinde (`chatgpt.com/backend-api`) de iletilir
- Gizli OpenClaw atıf üstbilgileri (`originator`, `version`,
  `User-Agent`) yalnızca
  `chatgpt.com/backend-api` üzerindeki yerel Codex trafiğine eklenir, genel OpenAI uyumlu proxy’lere eklenmez
- Doğrudan `openai/*` ile aynı `/fast` anahtarını ve `params.fastMode` yapılandırmasını paylaşır; OpenClaw bunu `service_tier=priority` olarak eşler
- `openai-codex/gpt-5.3-codex-spark`, Codex OAuth kataloğu bunu açığa çıkardığında kullanılabilir kalır; yetki durumuna bağlıdır
- `openai-codex/gpt-5.4`, yerel `contextWindow = 1050000` ve varsayılan çalışma zamanı `contextTokens = 272000` değerlerini korur; çalışma zamanı sınırını `models.providers.openai-codex.models[].contextTokens` ile geçersiz kılın
- Politika notu: OpenAI Codex OAuth, OpenClaw gibi harici araçlar/iş akışları için açıkça desteklenmektedir.

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

- [Qwen Cloud](/tr/providers/qwen): Qwen Cloud sağlayıcı yüzeyi ile Alibaba DashScope ve Coding Plan uç nokta eşlemesi
- [MiniMax](/tr/providers/minimax): MiniMax Coding Plan OAuth veya API anahtarı erişimi
- [GLM Models](/tr/providers/glm): Z.AI Coding Plan veya genel API uç noktaları

### OpenCode

- Auth: `OPENCODE_API_KEY` (veya `OPENCODE_ZEN_API_KEY`)
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
- Auth: `GEMINI_API_KEY`
- İsteğe bağlı rotasyon: `GEMINI_API_KEYS`, `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`, `GOOGLE_API_KEY` yedeği ve `OPENCLAW_LIVE_GEMINI_KEY` (tek geçersiz kılma)
- Örnek modeller: `google/gemini-3.1-pro-preview`, `google/gemini-3-flash-preview`
- Uyumluluk: `google/gemini-3.1-flash-preview` kullanan eski OpenClaw yapılandırması `google/gemini-3-flash-preview` olarak normalize edilir
- CLI: `openclaw onboard --auth-choice gemini-api-key`
- Doğrudan Gemini çalıştırmaları ayrıca `agents.defaults.models["google/<model>"].params.cachedContent`
  (veya eski `cached_content`) kabul eder; böylece sağlayıcıya özgü bir
  `cachedContents/...` işleyicisini iletir; Gemini önbellek isabetleri OpenClaw `cacheRead` olarak görünür

### Google Vertex ve Gemini CLI

- Sağlayıcılar: `google-vertex`, `google-gemini-cli`
- Auth: Vertex gcloud ADC kullanır; Gemini CLI kendi OAuth akışını kullanır
- Dikkat: Gemini CLI OAuth’un OpenClaw içindeki entegrasyonu resmi değildir. Bazı kullanıcılar üçüncü taraf istemcileri kullandıktan sonra Google hesaplarında kısıtlamalar bildiriyor. Devam etmeyi seçerseniz Google şartlarını inceleyin ve kritik olmayan bir hesap kullanın.
- Gemini CLI OAuth, paketlenmiş `google` plugin’inin bir parçası olarak gönderilir.
  - Önce Gemini CLI’yi kurun:
    - `brew install gemini-cli`
    - veya `npm install -g @google/gemini-cli`
  - Etkinleştirin: `openclaw plugins enable google`
  - Giriş yapın: `openclaw models auth login --provider google-gemini-cli --set-default`
  - Varsayılan model: `google-gemini-cli/gemini-3-flash-preview`
  - Not: istemci kimliğini veya gizli anahtarı `openclaw.json` içine **yapıştırmazsınız**. CLI giriş akışı,
    token’ları gateway host üzerindeki auth profillerinde depolar.
  - Girişten sonra istekler başarısız olursa gateway host üzerinde `GOOGLE_CLOUD_PROJECT` veya `GOOGLE_CLOUD_PROJECT_ID` ayarlayın.
  - Gemini CLI JSON yanıtları `response` alanından ayrıştırılır; kullanım bilgisi
    `stats` alanına geri döner ve `stats.cached`, OpenClaw `cacheRead` olarak normalize edilir.

### Z.AI (GLM)

- Sağlayıcı: `zai`
- Auth: `ZAI_API_KEY`
- Örnek model: `zai/glm-5`
- CLI: `openclaw onboard --auth-choice zai-api-key`
  - Takma adlar: `z.ai/*` ve `z-ai/*`, `zai/*` olarak normalize edilir
  - `zai-api-key`, eşleşen Z.AI uç noktasını otomatik algılar; `zai-coding-global`, `zai-coding-cn`, `zai-global` ve `zai-cn` belirli bir yüzeyi zorlar

### Vercel AI Gateway

- Sağlayıcı: `vercel-ai-gateway`
- Auth: `AI_GATEWAY_API_KEY`
- Örnek model: `vercel-ai-gateway/anthropic/claude-opus-4.6`
- CLI: `openclaw onboard --auth-choice ai-gateway-api-key`

### Kilo Gateway

- Sağlayıcı: `kilocode`
- Auth: `KILOCODE_API_KEY`
- Örnek model: `kilocode/kilo/auto`
- CLI: `openclaw onboard --auth-choice kilocode-api-key`
- Base URL: `https://api.kilo.ai/api/gateway/`
- Statik yedek katalog `kilocode/kilo/auto` ile gelir; canlı
  `https://api.kilo.ai/api/gateway/models` keşfi çalışma zamanı
  kataloğunu daha da genişletebilir.
- `kilocode/kilo/auto` arkasındaki tam yukarı akış yönlendirmesi Kilo Gateway’e aittir,
  OpenClaw içinde sabit kodlanmamıştır.

Kurulum ayrıntıları için bkz. [/providers/kilocode](/tr/providers/kilocode).

### Diğer paketlenmiş sağlayıcı plugin’leri

- OpenRouter: `openrouter` (`OPENROUTER_API_KEY`)
- Örnek model: `openrouter/auto`
- OpenClaw, OpenRouter’ın belgelenmiş uygulama atıf üstbilgilerini yalnızca
  istek gerçekten `openrouter.ai` hedefine gidiyorsa uygular
- OpenRouter’a özgü Anthropic `cache_control` işaretçileri de
  rastgele proxy URL’lerine değil, yalnızca doğrulanmış OpenRouter rotalarına uygulanır
- OpenRouter, proxy tarzı OpenAI uyumlu yol üzerinde kalır; dolayısıyla yerel
  yalnızca OpenAI’ye özgü istek şekillendirme (`serviceTier`, Responses `store`,
  prompt-cache ipuçları, OpenAI reasoning-compat payload’ları) iletilmez
- Gemini destekli OpenRouter başvuruları yalnızca proxy-Gemini thought-signature temizliğini korur;
  yerel Gemini replay doğrulaması ve bootstrap yeniden yazımları kapalı kalır
- Kilo Gateway: `kilocode` (`KILOCODE_API_KEY`)
- Örnek model: `kilocode/kilo/auto`
- Gemini destekli Kilo başvuruları aynı proxy-Gemini thought-signature
  temizleme yolunu korur; `kilocode/kilo/auto` ve proxy-reasoning’i desteklemeyen diğer
  ipuçları proxy reasoning eklemeyi atlar
- MiniMax: `minimax` (API anahtarı) ve `minimax-portal` (OAuth)
- Auth: `minimax` için `MINIMAX_API_KEY`; `minimax-portal` için `MINIMAX_OAUTH_TOKEN` veya `MINIMAX_API_KEY`
- Örnek model: `minimax/MiniMax-M2.7` veya `minimax-portal/MiniMax-M2.7`
- MiniMax onboarding/API anahtarı kurulumu, açık M2.7 model tanımları yazar ve
  `input: ["text", "image"]` içerir; paketlenmiş sağlayıcı kataloğu bu sohbet başvurularını
  sağlayıcı yapılandırması materyalize edilene kadar yalnızca metin olarak tutar
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
    `grok-4` ve `grok-4-0709` modellerini `*-fast` varyantlarına yeniden yazar
  - `tool_stream` varsayılan olarak açıktır; devre dışı bırakmak için
    `agents.defaults.models["xai/<model>"].params.tool_stream` değerini `false`
    yapın
- Mistral: `mistral` (`MISTRAL_API_KEY`)
- Örnek model: `mistral/mistral-large-latest`
- CLI: `openclaw onboard --auth-choice mistral-api-key`
- Groq: `groq` (`GROQ_API_KEY`)
- Cerebras: `cerebras` (`CEREBRAS_API_KEY`)
  - Cerebras üzerindeki GLM modelleri `zai-glm-4.7` ve `zai-glm-4.6` kimliklerini kullanır.
  - OpenAI uyumlu base URL: `https://api.cerebras.ai/v1`.
- GitHub Copilot: `github-copilot` (`COPILOT_GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_TOKEN`)
- Hugging Face Inference örnek modeli: `huggingface/deepseek-ai/DeepSeek-R1`; CLI: `openclaw onboard --auth-choice huggingface-api-key`. Bkz. [Hugging Face (Inference)](/tr/providers/huggingface).

## `models.providers` üzerinden sağlayıcılar (özel/base URL)

**Özel** sağlayıcılar veya
OpenAI/Anthropic uyumlu proxy’ler eklemek için `models.providers` (veya `models.json`) kullanın.

Aşağıdaki paketlenmiş sağlayıcı plugin’lerinin çoğu zaten varsayılan bir katalog yayımlar.
Varsayılan base URL, üstbilgiler veya model listesini geçersiz kılmak
istemediğiniz sürece açık `models.providers.<id>` girdileri kullanmayın.

### Moonshot AI (Kimi)

Moonshot, paketlenmiş bir sağlayıcı plugin’i olarak gelir. Varsayılan olarak yerleşik sağlayıcıyı
kullanın; yalnızca base URL veya model meta verisini geçersiz kılmanız gerektiğinde
açık bir `models.providers.moonshot` girdisi ekleyin:

- Sağlayıcı: `moonshot`
- Auth: `MOONSHOT_API_KEY`
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

Kimi Coding, Moonshot AI’nin Anthropic uyumlu uç noktasını kullanır:

- Sağlayıcı: `kimi`
- Auth: `KIMI_API_KEY`
- Örnek model: `kimi/kimi-code`

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: { model: { primary: "kimi/kimi-code" } },
  },
}
```

Eski `kimi/k2p5`, uyumluluk modeli kimliği olarak kabul edilmeye devam eder.

### Volcano Engine (Doubao)

Volcano Engine (火山引擎), Çin’de Doubao ve diğer modellere erişim sağlar.

- Sağlayıcı: `volcengine` (coding: `volcengine-plan`)
- Auth: `VOLCANO_ENGINE_API_KEY`
- Örnek model: `volcengine-plan/ark-code-latest`
- CLI: `openclaw onboard --auth-choice volcengine-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "volcengine-plan/ark-code-latest" } },
  },
}
```

Onboarding varsayılan olarak coding yüzeyini kullanır, ancak genel `volcengine/*`
kataloğu da aynı anda kaydedilir.

Onboarding/model yapılandırma seçimlerinde Volcengine auth choice,
hem `volcengine/*` hem de `volcengine-plan/*` satırlarını tercih eder. Bu modeller henüz yüklenmemişse
OpenClaw, boş bir sağlayıcı kapsamlı seçim göstermek yerine
filtrelenmemiş kataloğa geri döner.

Kullanılabilir modeller:

- `volcengine/doubao-seed-1-8-251228` (Doubao Seed 1.8)
- `volcengine/doubao-seed-code-preview-251028`
- `volcengine/kimi-k2-5-260127` (Kimi K2.5)
- `volcengine/glm-4-7-251222` (GLM 4.7)
- `volcengine/deepseek-v3-2-251201` (DeepSeek V3.2 128K)

Coding modelleri (`volcengine-plan`):

- `volcengine-plan/ark-code-latest`
- `volcengine-plan/doubao-seed-code`
- `volcengine-plan/kimi-k2.5`
- `volcengine-plan/kimi-k2-thinking`
- `volcengine-plan/glm-4.7`

### BytePlus (Uluslararası)

BytePlus ARK, uluslararası kullanıcılar için Volcano Engine ile aynı modellere erişim sağlar.

- Sağlayıcı: `byteplus` (coding: `byteplus-plan`)
- Auth: `BYTEPLUS_API_KEY`
- Örnek model: `byteplus-plan/ark-code-latest`
- CLI: `openclaw onboard --auth-choice byteplus-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "byteplus-plan/ark-code-latest" } },
  },
}
```

Onboarding varsayılan olarak coding yüzeyini kullanır, ancak genel `byteplus/*`
kataloğu da aynı anda kaydedilir.

Onboarding/model yapılandırma seçimlerinde BytePlus auth choice,
hem `byteplus/*` hem de `byteplus-plan/*` satırlarını tercih eder. Bu modeller henüz yüklenmemişse
OpenClaw, boş bir sağlayıcı kapsamlı seçim göstermek yerine
filtrelenmemiş kataloğa geri döner.

Kullanılabilir modeller:

- `byteplus/seed-1-8-251228` (Seed 1.8)
- `byteplus/kimi-k2-5-260127` (Kimi K2.5)
- `byteplus/glm-4-7-251222` (GLM 4.7)

Coding modelleri (`byteplus-plan`):

- `byteplus-plan/ark-code-latest`
- `byteplus-plan/doubao-seed-code`
- `byteplus-plan/kimi-k2.5`
- `byteplus-plan/kimi-k2-thinking`
- `byteplus-plan/glm-4.7`

### Synthetic

Synthetic, `synthetic` sağlayıcısı arkasında Anthropic uyumlu modeller sunar:

- Sağlayıcı: `synthetic`
- Auth: `SYNTHETIC_API_KEY`
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

- MiniMax OAuth (Genel): `--auth-choice minimax-global-oauth`
- MiniMax OAuth (CN): `--auth-choice minimax-cn-oauth`
- MiniMax API anahtarı (Genel): `--auth-choice minimax-global-api`
- MiniMax API anahtarı (CN): `--auth-choice minimax-cn-api`
- Auth: `minimax` için `MINIMAX_API_KEY`; `minimax-portal` için `MINIMAX_OAUTH_TOKEN` veya
  `MINIMAX_API_KEY`

Kurulum ayrıntıları, model seçenekleri ve yapılandırma parçacıkları için bkz. [/providers/minimax](/tr/providers/minimax).

MiniMax’in Anthropic uyumlu akış yolunda OpenClaw,
siz açıkça ayarlamadığınız sürece düşünmeyi varsayılan olarak devre dışı bırakır ve `/fast on`
`MiniMax-M2.7` modelini `MiniMax-M2.7-highspeed` olarak yeniden yazar.

Plugin’e ait capability ayrımı:

- Metin/sohbet varsayılanları `minimax/MiniMax-M2.7` üzerinde kalır
- Görüntü oluşturma `minimax/image-01` veya `minimax-portal/image-01` kullanır
- Görüntü anlama, her iki MiniMax auth yolunda da plugin’e ait `MiniMax-VL-01` kullanır
- Web araması `minimax` sağlayıcı kimliğinde kalır

### Ollama

Ollama, paketlenmiş bir sağlayıcı plugin’i olarak gelir ve Ollama’nın yerel API’sini kullanır:

- Sağlayıcı: `ollama`
- Auth: Gerekmez (yerel sunucu)
- Örnek model: `ollama/llama3.3`
- Kurulum: [https://ollama.com/download](https://ollama.com/download)

```bash
# Ollama'yı kurun, ardından bir model çekin:
ollama pull llama3.3
```

```json5
{
  agents: {
    defaults: { model: { primary: "ollama/llama3.3" } },
  },
}
```

`OLLAMA_API_KEY` ile katılım gösterdiğinizde Ollama yerel olarak `http://127.0.0.1:11434`
adresinde algılanır ve paketlenmiş sağlayıcı plugin’i Ollama’yı doğrudan
`openclaw onboard` ve model seçicisine ekler. Onboarding, cloud/local modu ve özel yapılandırma için
bkz. [/providers/ollama](/tr/providers/ollama).

### vLLM

vLLM, local/self-hosted OpenAI uyumlu
sunucular için paketlenmiş bir sağlayıcı plugin’i olarak gelir:

- Sağlayıcı: `vllm`
- Auth: İsteğe bağlıdır (sunucunuza bağlıdır)
- Varsayılan base URL: `http://127.0.0.1:8000/v1`

Yerelde otomatik keşfe katılmak için (sunucunuz auth zorlamıyorsa herhangi bir değer çalışır):

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

Ayrıntılar için bkz. [/providers/vllm](/tr/providers/vllm).

### SGLang

SGLang, hızlı self-hosted
OpenAI uyumlu sunucular için paketlenmiş bir sağlayıcı plugin’i olarak gelir:

- Sağlayıcı: `sglang`
- Auth: İsteğe bağlıdır (sunucunuza bağlıdır)
- Varsayılan base URL: `http://127.0.0.1:30000/v1`

Yerelde otomatik keşfe katılmak için (sunucunuz auth zorlamıyorsa herhangi bir değer çalışır):

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

Ayrıntılar için bkz. [/providers/sglang](/tr/providers/sglang).

### Yerel proxy’ler (LM Studio, vLLM, LiteLLM vb.)

Örnek (OpenAI uyumlu):

```json5
{
  agents: {
    defaults: {
      model: { primary: "lmstudio/my-local-model" },
      models: { "lmstudio/my-local-model": { alias: "Local" } },
    },
  },
  models: {
    providers: {
      lmstudio: {
        baseUrl: "http://localhost:1234/v1",
        apiKey: "LMSTUDIO_KEY",
        api: "openai-completions",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
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
  Atlandıklarında OpenClaw şu varsayılanları kullanır:
  - `reasoning: false`
  - `input: ["text"]`
  - `cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 }`
  - `contextWindow: 200000`
  - `maxTokens: 8192`
- Önerilir: proxy/model sınırlarınızla eşleşen açık değerler ayarlayın.
- Yerel olmayan uç noktalarda `api: "openai-completions"` için (ana makinesi `api.openai.com` olmayan boş olmayan herhangi bir `baseUrl`), OpenClaw sağlayıcının desteklemediği `developer` rolleri nedeniyle 400 hatalarından kaçınmak için `compat.supportsDeveloperRole: false` değerini zorunlu kılar.
- Proxy tarzı OpenAI uyumlu rotalar ayrıca yerel yalnızca OpenAI’ye özgü istek
  şekillendirmesini de atlar: `service_tier` yok, Responses `store` yok, prompt-cache ipuçları yok,
  OpenAI reasoning-compat payload şekillendirmesi yok ve gizli OpenClaw atıf
  üstbilgileri yok.
- `baseUrl` boşsa/atlanmışsa OpenClaw varsayılan OpenAI davranışını korur (`api.openai.com` adresine çözülür).
- Güvenlik için, açık bir `compat.supportsDeveloperRole: true` değeri bile yerel olmayan `openai-completions` uç noktalarında yine geçersiz kılınır.

## CLI örnekleri

```bash
openclaw onboard --auth-choice opencode-zen
openclaw models set opencode/claude-opus-4-6
openclaw models list
```

Ayrıca bkz.: tam yapılandırma örnekleri için [/gateway/configuration](/tr/gateway/configuration).

## İlgili

- [Models](/tr/concepts/models) — model yapılandırması ve takma adlar
- [Model Failover](/tr/concepts/model-failover) — fallback zincirleri ve yeniden deneme davranışı
- [Configuration Reference](/tr/gateway/configuration-reference#agent-defaults) — model yapılandırma anahtarları
- [Providers](/tr/providers) — sağlayıcı bazında kurulum kılavuzları
