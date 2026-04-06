---
read_when:
    - Sağlayıcı bazında bir model kurulum başvurusuna ihtiyacınız var
    - Model sağlayıcıları için örnek yapılandırmalar veya CLI başlangıç komutları istiyorsunuz
summary: Örnek yapılandırmalar + CLI akışlarıyla model sağlayıcısı genel bakışı
title: Model Sağlayıcıları
x-i18n:
    generated_at: "2026-04-06T03:08:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: 15e4b82e07221018a723279d309e245bb4023bc06e64b3c910ef2cae3dfa2599
    source_path: concepts/model-providers.md
    workflow: 15
---

# Model sağlayıcıları

Bu sayfa **LLM/model sağlayıcılarını** kapsar (WhatsApp/Telegram gibi sohbet kanallarını değil).
Model seçim kuralları için bkz. [/concepts/models](/tr/concepts/models).

## Hızlı kurallar

- Model başvuruları `provider/model` kullanır (örnek: `opencode/claude-opus-4-6`).
- `agents.defaults.models` ayarlarsanız bu, izin listesi olur.
- CLI yardımcıları: `openclaw onboard`, `openclaw models list`, `openclaw models set <provider/model>`.
- Geri dönüş çalışma zamanı kuralları, bekleme süresi sondaları ve oturum geçersiz kılma kalıcılığı
  [/concepts/model-failover](/tr/concepts/model-failover) içinde belgelenmiştir.
- `models.providers.*.models[].contextWindow` yerel model meta verisidir;
  `models.providers.*.models[].contextTokens` ise etkin çalışma zamanı sınırıdır.
- Sağlayıcı eklentileri `registerProvider({ catalog })` aracılığıyla model katalogları ekleyebilir;
  OpenClaw bu çıktıyı `models.providers` içine birleştirip ardından
  `models.json` dosyasını yazar.
- Sağlayıcı manifestleri `providerAuthEnvVars` bildirebilir; böylece genel ortam tabanlı
  kimlik doğrulama yoklamalarının eklenti çalışma zamanını yüklemesi gerekmez. Kalan çekirdek ortam değişkeni
  eşlemesi artık yalnızca eklenti olmayan/çekirdek sağlayıcılar ve Anthropic API-anahtarı öncelikli başlangıç gibi
  birkaç genel öncelik durumu içindir.
- Sağlayıcı eklentileri ayrıca sağlayıcı çalışma zamanı davranışını da şu yollarla sahiplenebilir:
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
- Not: sağlayıcı çalışma zamanı `capabilities`, paylaşılan çalıştırıcı meta verisidir (sağlayıcı
  ailesi, transkript/araç farklılıkları, taşıma/önbellek ipuçları). Bu,
  bir eklentinin ne kaydettiğini açıklayan [genel yetenek modeli](/tr/plugins/architecture#public-capability-model)
  ile aynı şey değildir (metin çıkarımı, konuşma vb.).

## Eklentiye ait sağlayıcı davranışı

Sağlayıcı eklentileri artık sağlayıcıya özgü mantığın çoğuna sahip olabilirken OpenClaw
genel çıkarım döngüsünü korur.

Tipik ayrım:

- `auth[].run` / `auth[].runNonInteractive`: sağlayıcı, `openclaw onboard`, `openclaw models auth` ve etkileşimsiz kurulum için başlangıç/giriş
  akışlarına sahiptir
- `wizard.setup` / `wizard.modelPicker`: sağlayıcı, kimlik doğrulama seçeneği etiketlerine,
  eski takma adlara, başlangıç izin listesi ipuçlarına ve başlangıç/model seçicilerindeki kurulum girdilerine sahiptir
- `catalog`: sağlayıcı `models.providers` içinde görünür
- `normalizeModelId`: sağlayıcı, eski/önizleme model kimliklerini arama veya
  standartlaştırmadan önce normalize eder
- `normalizeTransport`: sağlayıcı, genel model birleştirmeden önce taşıma ailesi `api` / `baseUrl`
  değerlerini normalize eder; OpenClaw önce eşleşen sağlayıcıyı,
  sonra gerçekten taşıma değiştirene kadar diğer kanca özellikli sağlayıcı eklentilerini denetler
- `normalizeConfig`: sağlayıcı, çalışma zamanı kullanmadan önce `models.providers.<id>` yapılandırmasını normalize eder;
  OpenClaw önce eşleşen sağlayıcıyı, sonra gerçekten yapılandırmayı değiştiren diğer
  kanca özellikli sağlayıcı eklentilerini denetler. Hiçbir
  sağlayıcı kancası yapılandırmayı yeniden yazmazsa paketlenmiş Google ailesi yardımcıları yine de
  desteklenen Google sağlayıcı girdilerini normalize eder.
- `applyNativeStreamingUsageCompat`: sağlayıcı, yapılandırma sağlayıcıları için uç nokta odaklı yerel akış kullanım uyumluluğu yeniden yazımlarını uygular
- `resolveConfigApiKey`: sağlayıcı, tam çalışma zamanı kimlik doğrulamasını yüklemeye zorlamadan
  yapılandırma sağlayıcıları için ortam işaretleyici kimlik doğrulamayı çözer.
  `amazon-bedrock` da burada yerleşik bir AWS ortam işaretleyici çözücüsüne sahiptir; Bedrock çalışma zamanı kimlik doğrulaması
  AWS SDK varsayılan zincirini kullanıyor olsa bile
- `resolveSyntheticAuth`: sağlayıcı, düz metin gizli bilgileri kalıcı hale getirmeden
  yerel/kendi barındırılan veya diğer yapılandırma destekli kimlik doğrulama kullanılabilirliğini açığa çıkarabilir
- `shouldDeferSyntheticProfileAuth`: sağlayıcı, depolanmış sentetik profil
  yer tutucularını ortam/yapılandırma destekli kimlik doğrulamadan daha düşük öncelikli olarak işaretleyebilir
- `resolveDynamicModel`: sağlayıcı, henüz yerel
  statik katalogda bulunmayan model kimliklerini kabul eder
- `prepareDynamicModel`: sağlayıcının, dinamik çözümü yeniden denemeden önce bir meta veri yenilemesine ihtiyacı vardır
- `normalizeResolvedModel`: sağlayıcının taşıma veya temel URL yeniden yazımlarına ihtiyacı vardır
- `contributeResolvedModelCompat`: sağlayıcı, kendi satıcı modelleri
  başka bir uyumlu taşıma üzerinden geldiğinde bile uyumluluk bayrakları ekler
- `capabilities`: sağlayıcı, transkript/araçlar/sağlayıcı ailesi farklılıklarını yayımlar
- `normalizeToolSchemas`: sağlayıcı, gömülü
  çalıştırıcının görmesinden önce araç şemalarını temizler
- `inspectToolSchemas`: sağlayıcı, normalizasyondan sonra taşıma özelindeki şema uyarılarını gösterir
- `resolveReasoningOutputMode`: sağlayıcı, yerel ile etiketli
  muhakeme çıktısı sözleşmeleri arasında seçim yapar
- `prepareExtraParams`: sağlayıcı, model başına istek parametrelerini varsayılan hale getirir veya normalize eder
- `createStreamFn`: sağlayıcı, normal akış yolunu tamamen
  özel bir taşıma ile değiştirir
- `wrapStreamFn`: sağlayıcı, istek üst bilgileri/gövdesi/model uyumluluk sarmalayıcıları uygular
- `resolveTransportTurnState`: sağlayıcı, dönüş başına yerel taşıma
  üst bilgileri veya meta veriler sağlar
- `resolveWebSocketSessionPolicy`: sağlayıcı, yerel WebSocket oturumu
  üst bilgileri veya oturum bekleme politikası sağlar
- `createEmbeddingProvider`: sağlayıcı, bellek gömme davranışı
  çekirdek gömme dağıtım mekanizması yerine sağlayıcı eklentisiyle birlikte olduğunda buna sahiptir
- `formatApiKey`: sağlayıcı, depolanmış kimlik doğrulama profillerini
  taşımanın beklediği çalışma zamanı `apiKey` dizesine dönüştürür
- `refreshOAuth`: paylaşılan `pi-ai`
  yenileyicileri yeterli olmadığında OAuth yenilemeye sağlayıcı sahiptir
- `buildAuthDoctorHint`: OAuth yenileme
  başarısız olduğunda sağlayıcı onarım rehberliği ekler
- `matchesContextOverflowError`: sağlayıcı, genel sezgilerin kaçıracağı
  sağlayıcıya özgü bağlam penceresi taşma hatalarını tanır
- `classifyFailoverReason`: sağlayıcı, sağlayıcıya özgü ham taşıma/API
  hatalarını hız sınırı veya aşırı yük gibi geri dönüş nedenlerine eşler
- `isCacheTtlEligible`: sağlayıcı, hangi yukarı akış model kimliklerinin prompt-cache TTL desteklediğine karar verir
- `buildMissingAuthMessage`: sağlayıcı, genel kimlik doğrulama deposu hatasını
  sağlayıcıya özgü bir kurtarma ipucuyla değiştirir
- `suppressBuiltInModel`: sağlayıcı, eski yukarı akış satırlarını gizler ve
  doğrudan çözümleme başarısızlıkları için satıcıya ait bir hata döndürebilir
- `augmentModelCatalog`: sağlayıcı, keşif ve yapılandırma birleştirmesinden sonra
  sentetik/nihai katalog satırları ekler
- `isBinaryThinking`: sağlayıcı, ikili açık/kapalı düşünme UX'ine sahiptir
- `supportsXHighThinking`: sağlayıcı, seçili modelleri `xhigh` için etkinleştirir
- `resolveDefaultThinkingLevel`: sağlayıcı, bir
  model ailesi için varsayılan `/think` ilkesine sahiptir
- `applyConfigDefaults`: sağlayıcı, kimlik doğrulama kipine, ortama veya model ailesine göre
  yapılandırma somutlaştırması sırasında sağlayıcıya özgü genel varsayılanları uygular
- `isModernModelRef`: sağlayıcı, canlı/duman testi tercih edilen model eşleştirmesine sahiptir
- `prepareRuntimeAuth`: sağlayıcı, yapılandırılmış bir kimlik bilgisini kısa ömürlü
  bir çalışma zamanı belirtecine dönüştürür
- `resolveUsageAuth`: sağlayıcı, `/usage`
  ve ilgili durum/raporlama yüzeyleri için kullanım/kota kimlik bilgilerini çözer
- `fetchUsageSnapshot`: sağlayıcı, kullanım uç noktası getirme/ayrıştırma işlemlerine sahipken
  çekirdek yine özet kabuğuna ve biçimlendirmeye sahiptir
- `onModelSelected`: sağlayıcı, telemetri veya sağlayıcıya ait oturum kayıtları gibi
  seçim sonrası yan etkileri çalıştırır

Mevcut paketlenmiş örnekler:

- `anthropic`: Claude 4.6 ileri uyumluluk geri dönüşü, kimlik doğrulama onarım ipuçları, kullanım
  uç noktası getirme, önbellek TTL/sağlayıcı ailesi meta verisi ve kimlik doğrulama farkında genel
  yapılandırma varsayılanları
- `amazon-bedrock`: Bedrock'a özgü boğma/hazır değil hataları için sağlayıcıya ait bağlam taşması eşleştirmesi ve geri dönüş
  nedeni sınıflandırması; ayrıca Anthropic trafiğinde yalnızca Claude yeniden oynatma ilkesi
  korumaları için paylaşılan `anthropic-by-model` yeniden oynatma ailesi
- `anthropic-vertex`: Anthropic-message
  trafiğinde yalnızca Claude yeniden oynatma ilkesi korumaları
- `openrouter`: doğrudan model kimlikleri, istek sarmalayıcıları, sağlayıcı yetenek
  ipuçları, proxy Gemini trafiğinde Gemini thought-signature temizliği,
  `openrouter-thinking` akış ailesi üzerinden proxy muhakeme ekleme,
  yönlendirme meta verisi iletimi ve önbellek TTL ilkesi
- `github-copilot`: başlangıç/cihaz girişi, ileri uyumluluk model geri dönüşü,
  Claude-thinking transkript ipuçları, çalışma zamanı belirteci değişimi ve kullanım uç noktası
  getirme
- `openai`: GPT-5.4 ileri uyumluluk geri dönüşü, doğrudan OpenAI taşıma
  normalizasyonu, Codex farkında eksik kimlik doğrulama ipuçları, Spark bastırma, sentetik
  OpenAI/Codex katalog satırları, düşünme/canlı model ilkesi, kullanım belirteci takma ad
  normalizasyonu (`input` / `output` ve `prompt` / `completion` aileleri), yerel OpenAI/Codex
  sarmalayıcıları için paylaşılan `openai-responses-defaults` akış ailesi,
  sağlayıcı ailesi meta verisi, `gpt-image-1` için paketlenmiş görsel üretimi sağlayıcısı
  kaydı ve `sora-2` için paketlenmiş video üretimi sağlayıcısı
  kaydı
- `google`: Gemini 3.1 ileri uyumluluk geri dönüşü, yerel Gemini yeniden oynatma
  doğrulaması, bootstrap yeniden oynatma temizliği, etiketli muhakeme çıktısı modu,
  modern model eşleştirme, Gemini image-preview modelleri için paketlenmiş görsel üretimi sağlayıcısı kaydı ve Veo modelleri için paketlenmiş video üretimi sağlayıcısı
  kaydı
- `moonshot`: paylaşılan taşıma, eklentiye ait düşünme yükü normalizasyonu
- `kilocode`: paylaşılan taşıma, eklentiye ait istek üst bilgileri, muhakeme yükü
  normalizasyonu, proxy-Gemini thought-signature temizliği ve önbellek TTL
  ilkesi
- `zai`: GLM-5 ileri uyumluluk geri dönüşü, `tool_stream` varsayılanları, önbellek TTL
  ilkesi, ikili düşünme/canlı model ilkesi ve kullanım kimlik doğrulaması + kota getirme;
  bilinmeyen `glm-5*` kimlikleri paketlenmiş `glm-4.7` şablonundan üretilir
- `xai`: yerel Responses taşıma normalizasyonu, Grok hızlı varyantları için
  `/fast` takma ad yeniden yazımları, varsayılan `tool_stream`, xAI'ya özgü araç şeması /
  muhakeme yükü temizliği ve `grok-imagine-video` için paketlenmiş video üretimi sağlayıcısı
  kaydı
- `mistral`: eklentiye ait yetenek meta verisi
- `opencode` ve `opencode-go`: eklentiye ait yetenek meta verisi artı
  proxy-Gemini thought-signature temizliği
- `alibaba`: `alibaba/wan2.6-t2v` gibi doğrudan Wan model başvuruları için eklentiye ait video üretimi kataloğu
- `byteplus`: eklentiye ait kataloglar artı Seedance metinden videoya/görselden videoya modelleri için paketlenmiş video üretimi sağlayıcısı
  kaydı
- `fal`: barındırılan üçüncü taraf FLUX görsel modelleri için
  paketlenmiş görsel üretimi sağlayıcısı kaydı artı barındırılan üçüncü taraf video modelleri için
  paketlenmiş video üretimi sağlayıcısı kaydı
- `cloudflare-ai-gateway`, `huggingface`, `kimi`, `nvidia`, `qianfan`,
  `stepfun`, `synthetic`, `venice`, `vercel-ai-gateway` ve `volcengine`:
  yalnızca eklentiye ait kataloglar
- `qwen`: metin modelleri için eklentiye ait kataloglar artı
  çok modlu yüzeyleri için paylaşılan media-understanding ve video üretimi sağlayıcısı kayıtları;
  Qwen video üretimi, `wan2.6-t2v` ve `wan2.7-r2v` gibi paketlenmiş Wan modelleriyle birlikte
  Standard DashScope video uç noktalarını kullanır
- `runway`: `gen4.5` gibi yerel
  Runway görev tabanlı modeller için eklentiye ait video üretimi sağlayıcısı kaydı
- `minimax`: eklentiye ait kataloglar, Hailuo video modelleri için paketlenmiş video üretimi sağlayıcısı
  kaydı, `image-01` için paketlenmiş görsel üretimi sağlayıcısı
  kaydı, hibrit Anthropic/OpenAI yeniden oynatma ilkesi
  seçimi ve kullanım kimlik doğrulaması/anlık görüntü mantığı
- `together`: eklentiye ait kataloglar artı Wan video modelleri için paketlenmiş video üretimi sağlayıcısı
  kaydı
- `xiaomi`: eklentiye ait kataloglar artı kullanım kimlik doğrulaması/anlık görüntü mantığı

Paketlenmiş `openai` eklentisi artık her iki sağlayıcı kimliğine de sahiptir: `openai` ve
`openai-codex`.

Bu, hâlâ OpenClaw'ın normal taşımalarına uyan sağlayıcıları kapsar. Tamamen
özel bir istek yürütücüsüne ihtiyaç duyan bir sağlayıcı, ayrı ve daha derin bir eklenti
yüzeyidir.

## API anahtarı döndürme

- Seçili sağlayıcılar için genel sağlayıcı döndürmeyi destekler.
- Birden çok anahtarı şununla yapılandırın:
  - `OPENCLAW_LIVE_<PROVIDER>_KEY` (tek canlı geçersiz kılma, en yüksek öncelik)
  - `<PROVIDER>_API_KEYS` (virgül veya noktalı virgülle ayrılmış liste)
  - `<PROVIDER>_API_KEY` (birincil anahtar)
  - `<PROVIDER>_API_KEY_*` (numaralandırılmış liste, örn. `<PROVIDER>_API_KEY_1`)
- Google sağlayıcıları için `GOOGLE_API_KEY` de geri dönüş olarak eklenir.
- Anahtar seçme sırası önceliği korur ve değerleri tekilleştirir.
- İstekler, yalnızca hız sınırı yanıtlarında bir sonraki anahtarla yeniden denenir (örneğin
  `429`, `rate_limit`, `quota`, `resource exhausted`, `Too many
concurrent requests`, `ThrottlingException`, `concurrency limit reached`,
  `workers_ai ... quota limit exceeded` veya dönemsel kullanım sınırı iletileri).
- Hız sınırı dışındaki başarısızlıklar anında başarısız olur; anahtar döndürme denenmez.
- Tüm aday anahtarlar başarısız olduğunda son hata, son denemeden döndürülür.

## Yerleşik sağlayıcılar (pi-ai kataloğu)

OpenClaw, pi‑ai kataloğuyla birlikte gelir. Bu sağlayıcılar **hiç**
`models.providers` yapılandırması gerektirmez; sadece kimlik doğrulamayı ayarlayın ve bir model seçin.

### OpenAI

- Sağlayıcı: `openai`
- Kimlik doğrulama: `OPENAI_API_KEY`
- İsteğe bağlı döndürme: `OPENAI_API_KEYS`, `OPENAI_API_KEY_1`, `OPENAI_API_KEY_2`, ayrıca `OPENCLAW_LIVE_OPENAI_KEY` (tek geçersiz kılma)
- Örnek modeller: `openai/gpt-5.4`, `openai/gpt-5.4-pro`
- CLI: `openclaw onboard --auth-choice openai-api-key`
- Varsayılan taşıma `auto`dur (önce WebSocket, geri dönüşte SSE)
- Model başına şu yolla geçersiz kılınır: `agents.defaults.models["openai/<model>"].params.transport` (`"sse"`, `"websocket"` veya `"auto"`)
- OpenAI Responses WebSocket ön ısıtma varsayılan olarak `params.openaiWsWarmup` (`true`/`false`) ile etkindir
- OpenAI öncelikli işleme, `agents.defaults.models["openai/<model>"].params.serviceTier` aracılığıyla etkinleştirilebilir
- `/fast` ve `params.fastMode`, doğrudan `openai/*` Responses isteklerini `api.openai.com` üzerinde `service_tier=priority` olarak eşler
- Paylaşılan `/fast` geçişi yerine açık bir katman istiyorsanız `params.serviceTier` kullanın
- Gizli OpenClaw atıf üst bilgileri (`originator`, `version`,
  `User-Agent`) yalnızca `api.openai.com` adresine giden yerel OpenAI trafiğinde uygulanır,
  genel OpenAI uyumlu proxy'lerde uygulanmaz
- Yerel OpenAI yolları ayrıca Responses `store`, prompt-cache ipuçları ve
  OpenAI muhakeme uyumluluğu yük biçimlendirmesini korur; proxy yolları korumaz
- `openai/gpt-5.3-codex-spark`, canlı OpenAI API'si bunu reddettiği için OpenClaw'da kasıtlı olarak bastırılır; Spark yalnızca Codex olarak değerlendirilir

```json5
{
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

### Anthropic

- Sağlayıcı: `anthropic`
- Kimlik doğrulama: `ANTHROPIC_API_KEY`
- İsteğe bağlı döndürme: `ANTHROPIC_API_KEYS`, `ANTHROPIC_API_KEY_1`, `ANTHROPIC_API_KEY_2`, ayrıca `OPENCLAW_LIVE_ANTHROPIC_KEY` (tek geçersiz kılma)
- Örnek model: `anthropic/claude-opus-4-6`
- CLI: `openclaw onboard --auth-choice apiKey`
- Doğrudan genel Anthropic istekleri, `api.anthropic.com` adresine gönderilen API anahtarı ve OAuth ile kimliği doğrulanmış trafik dahil olmak üzere paylaşılan `/fast` geçişini ve `params.fastMode` değerini de destekler; OpenClaw bunu Anthropic `service_tier` değerine eşler (`auto` ve `standard_only`)
- Faturalandırma notu: Anthropic için OpenClaw'daki pratik ayrım **API anahtarı** veya **Extra Usage ile Claude aboneliği** şeklindedir. Anthropic, **4 Nisan 2026 saat 12:00 PT / 20:00 BST** tarihinde OpenClaw kullanıcılarına, **OpenClaw** Claude-giriş yolunun üçüncü taraf harness kullanımı sayıldığını ve abonelikten ayrı faturalanan **Extra Usage** gerektirdiğini bildirdi. Yerel yeniden üretimlerimiz de OpenClaw'ı tanımlayan prompt dizesinin Anthropic SDK + API anahtarı yolunda yeniden üretilemediğini gösteriyor.
- Anthropic kurulum belirteci, eski/el ile kullanılan bir OpenClaw yolu olarak yeniden kullanılabilir. Bunu, Anthropic'in OpenClaw kullanıcılarına bu yolun **Extra Usage** gerektirdiğini söylediği beklentisiyle kullanın.

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
- Varsayılan taşıma `auto`dur (önce WebSocket, geri dönüşte SSE)
- Model başına şu yolla geçersiz kılınır: `agents.defaults.models["openai-codex/<model>"].params.transport` (`"sse"`, `"websocket"` veya `"auto"`)
- `params.serviceTier`, yerel Codex Responses isteklerinde (`chatgpt.com/backend-api`) de iletilir
- Gizli OpenClaw atıf üst bilgileri (`originator`, `version`,
  `User-Agent`) yalnızca `chatgpt.com/backend-api` adresine giden yerel Codex trafiğine
  eklenir, genel OpenAI uyumlu proxy'lere eklenmez
- Doğrudan `openai/*` ile aynı `/fast` geçişini ve `params.fastMode` yapılandırmasını paylaşır; OpenClaw bunu `service_tier=priority` olarak eşler
- `openai-codex/gpt-5.3-codex-spark`, Codex OAuth kataloğu bunu açığa çıkardığında kullanılabilir kalır; yetkilendirmeye bağlıdır
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

- [Qwen Cloud](/tr/providers/qwen): Qwen Cloud sağlayıcı yüzeyi artı Alibaba DashScope ve Coding Plan uç nokta eşlemesi
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
- İsteğe bağlı döndürme: `GEMINI_API_KEYS`, `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`, `GOOGLE_API_KEY` geri dönüşü ve `OPENCLAW_LIVE_GEMINI_KEY` (tek geçersiz kılma)
- Örnek modeller: `google/gemini-3.1-pro-preview`, `google/gemini-3-flash-preview`
- Uyumluluk: `google/gemini-3.1-flash-preview` kullanan eski OpenClaw yapılandırması `google/gemini-3-flash-preview` olarak normalize edilir
- CLI: `openclaw onboard --auth-choice gemini-api-key`
- Doğrudan Gemini çalıştırmaları ayrıca `agents.defaults.models["google/<model>"].params.cachedContent`
  (veya eski `cached_content`) değerini kabul eder; bu, sağlayıcıya özgü
  bir `cachedContents/...` tutamacını iletmek içindir; Gemini önbellek isabetleri OpenClaw `cacheRead` olarak görünür

### Google Vertex

- Sağlayıcı: `google-vertex`
- Kimlik doğrulama: gcloud ADC
  - Gemini CLI JSON yanıtları `response` içinden ayrıştırılır; kullanım geri dönüşte
    `stats` içinden alınır, `stats.cached` ise OpenClaw `cacheRead` biçimine normalize edilir.

### Z.AI (GLM)

- Sağlayıcı: `zai`
- Kimlik doğrulama: `ZAI_API_KEY`
- Örnek model: `zai/glm-5`
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
- Statik geri dönüş kataloğu `kilocode/kilo/auto` ile gelir; canlı
  `https://api.kilo.ai/api/gateway/models` keşfi çalışma zamanı
  kataloğunu daha da genişletebilir.
- `kilocode/kilo/auto` arkasındaki tam yukarı akış yönlendirmesi,
  OpenClaw'da sabit kodlanmış değildir; Kilo Gateway'e aittir.

Kurulum ayrıntıları için bkz. [/providers/kilocode](/tr/providers/kilocode).

### Diğer paketlenmiş sağlayıcı eklentileri

- OpenRouter: `openrouter` (`OPENROUTER_API_KEY`)
- Örnek model: `openrouter/auto`
- OpenClaw, OpenRouter'ın belgelenmiş uygulama atıf üst bilgilerini yalnızca
  istek gerçekten `openrouter.ai` hedefliyorsa uygular
- OpenRouter'a özgü Anthropic `cache_control` işaretçileri de
  doğrulanmış OpenRouter yollarıyla sınırlıdır, rastgele proxy URL'leriyle değil
- OpenRouter, proxy tarzı OpenAI uyumlu yolda kalır; bu nedenle yerel
  yalnızca OpenAI istek biçimlendirmesi (`serviceTier`, Responses `store`,
  prompt-cache ipuçları, OpenAI muhakeme uyumluluğu yükleri) iletilmez
- Gemini destekli OpenRouter başvuruları yalnızca proxy-Gemini thought-signature temizliğini korur;
  yerel Gemini yeniden oynatma doğrulaması ve bootstrap yeniden yazımları kapalı kalır
- Kilo Gateway: `kilocode` (`KILOCODE_API_KEY`)
- Örnek model: `kilocode/kilo/auto`
- Gemini destekli Kilo başvuruları aynı proxy-Gemini thought-signature
  temizleme yolunu korur; `kilocode/kilo/auto` ve proxy muhakeme desteklemeyen diğer
  ipuçları proxy muhakeme eklemeyi atlar
- MiniMax: `minimax` (API anahtarı) ve `minimax-portal` (OAuth)
- Kimlik doğrulama: `minimax` için `MINIMAX_API_KEY`; `minimax-portal` için `MINIMAX_OAUTH_TOKEN` veya `MINIMAX_API_KEY`
- Örnek model: `minimax/MiniMax-M2.7` veya `minimax-portal/MiniMax-M2.7`
- MiniMax başlangıç/API anahtarı kurulumu, `input: ["text", "image"]` ile açık M2.7 model tanımları yazar; paketlenmiş sağlayıcı kataloğu ise
  o sağlayıcı yapılandırması somutlaştırılana kadar sohbet başvurularını
  yalnızca metin olarak tutar
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
    `grok-4` ve `grok-4-0709` modellerini ilgili `*-fast` varyantlarına yeniden yazar
  - `tool_stream` varsayılan olarak açıktır;
    devre dışı bırakmak için `agents.defaults.models["xai/<model>"].params.tool_stream` değerini `false`
    olarak ayarlayın
- Mistral: `mistral` (`MISTRAL_API_KEY`)
- Örnek model: `mistral/mistral-large-latest`
- CLI: `openclaw onboard --auth-choice mistral-api-key`
- Groq: `groq` (`GROQ_API_KEY`)
- Cerebras: `cerebras` (`CEREBRAS_API_KEY`)
  - Cerebras üzerindeki GLM modelleri `zai-glm-4.7` ve `zai-glm-4.6` kimliklerini kullanır.
  - OpenAI uyumlu temel URL: `https://api.cerebras.ai/v1`.
- GitHub Copilot: `github-copilot` (`COPILOT_GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_TOKEN`)
- Hugging Face Inference örnek modeli: `huggingface/deepseek-ai/DeepSeek-R1`; CLI: `openclaw onboard --auth-choice huggingface-api-key`. Bkz. [Hugging Face (Inference)](/tr/providers/huggingface).

## `models.providers` üzerinden sağlayıcılar (özel/temel URL)

**Özel** sağlayıcılar veya
OpenAI/Anthropic uyumlu proxy'ler eklemek için `models.providers` (veya `models.json`) kullanın.

Aşağıdaki paketlenmiş sağlayıcı eklentilerinin birçoğu zaten varsayılan bir katalog yayımlar.
Varsayılan temel URL'yi, üst bilgileri veya model listesini geçersiz kılmak istediğinizde
yalnızca açık `models.providers.<id>` girdileri kullanın.

### Moonshot AI (Kimi)

Moonshot, paketlenmiş bir sağlayıcı eklentisi olarak gelir. Varsayılan olarak
yerleşik sağlayıcıyı kullanın; yalnızca temel URL'yi veya model meta verisini geçersiz kılmanız gerektiğinde açık bir `models.providers.moonshot` girdisi ekleyin:

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

Kimi Coding, Moonshot AI'ın Anthropic uyumlu uç noktasını kullanır:

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

Eski `kimi/k2p5`, uyumluluk model kimliği olarak kabul edilmeye devam eder.

### Volcano Engine (Doubao)

Volcano Engine (火山引擎), Çin'de Doubao ve diğer modellere erişim sağlar.

- Sağlayıcı: `volcengine` (coding: `volcengine-plan`)
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

Başlangıç varsayılan olarak coding yüzeyini kullanır, ancak genel `volcengine/*`
kataloğu aynı anda kaydedilir.

Başlangıç/model yapılandırma seçicilerinde, Volcengine kimlik doğrulama seçeneği hem
`volcengine/*` hem de `volcengine-plan/*` satırlarını tercih eder. Bu modeller henüz yüklenmemişse
OpenClaw boş bir sağlayıcı kapsamlı seçici göstermek yerine filtrelenmemiş kataloğa geri döner.

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

Başlangıç varsayılan olarak coding yüzeyini kullanır, ancak genel `byteplus/*`
kataloğu aynı anda kaydedilir.

Başlangıç/model yapılandırma seçicilerinde, BytePlus kimlik doğrulama seçeneği hem
`byteplus/*` hem de `byteplus-plan/*` satırlarını tercih eder. Bu modeller henüz yüklenmemişse
OpenClaw boş bir sağlayıcı kapsamlı seçici göstermek yerine filtrelenmemiş kataloğa geri döner.

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

Synthetic, `synthetic` sağlayıcısının arkasında Anthropic uyumlu modeller sağlar:

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

Kurulum ayrıntıları, model seçenekleri ve yapılandırma parçacıkları için bkz. [/providers/minimax](/tr/providers/minimax).

MiniMax'in Anthropic uyumlu akış yolunda OpenClaw, siz açıkça ayarlamadığınız sürece
düşünmeyi varsayılan olarak devre dışı bırakır ve `/fast on`,
`MiniMax-M2.7` modelini `MiniMax-M2.7-highspeed` olarak yeniden yazar.

Eklentiye ait yetenek ayrımı:

- Metin/sohbet varsayılanları `minimax/MiniMax-M2.7` üzerinde kalır
- Görsel üretimi `minimax/image-01` veya `minimax-portal/image-01`
- Görsel anlama, her iki MiniMax kimlik doğrulama yolunda da eklentiye ait `MiniMax-VL-01`'dir
- Web araması, `minimax` sağlayıcı kimliğinde kalır

### Ollama

Ollama, paketlenmiş bir sağlayıcı eklentisi olarak gelir ve Ollama'nın yerel API'sini kullanır:

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

Ollama, `OLLAMA_API_KEY` ile katılım sağladığınızda yerelde `http://127.0.0.1:11434` adresinde algılanır
ve paketlenmiş sağlayıcı eklentisi Ollama'yı doğrudan
`openclaw onboard` ve model seçicisine ekler. Başlangıç, bulut/yerel kip ve özel yapılandırma için bkz. [/providers/ollama](/tr/providers/ollama).

### vLLM

vLLM, yerel/kendi barındırdığınız OpenAI uyumlu
sunucular için paketlenmiş bir sağlayıcı eklentisi olarak gelir:

- Sağlayıcı: `vllm`
- Kimlik doğrulama: İsteğe bağlı (sunucunuza bağlıdır)
- Varsayılan temel URL: `http://127.0.0.1:8000/v1`

Yerelde otomatik keşfe katılmak için (sunucunuz kimlik doğrulama zorunlu kılmıyorsa herhangi bir değer çalışır):

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

SGLang, hızlı kendi barındırdığınız
OpenAI uyumlu sunucular için paketlenmiş bir sağlayıcı eklentisi olarak gelir:

- Sağlayıcı: `sglang`
- Kimlik doğrulama: İsteğe bağlı (sunucunuza bağlıdır)
- Varsayılan temel URL: `http://127.0.0.1:30000/v1`

Yerelde otomatik keşfe katılmak için (sunucunuz
kimlik doğrulama zorunlu kılmıyorsa herhangi bir değer çalışır):

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

### Yerel proxy'ler (LM Studio, vLLM, LiteLLM vb.)

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
  Atlandığında OpenClaw şu varsayılanları kullanır:
  - `reasoning: false`
  - `input: ["text"]`
  - `cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 }`
  - `contextWindow: 200000`
  - `maxTokens: 8192`
- Önerilir: proxy/model sınırlarınızla eşleşen açık değerler ayarlayın.
- Yerel olmayan uç noktalarda `api: "openai-completions"` için (`host` değeri `api.openai.com` olmayan boş olmayan herhangi bir `baseUrl`), OpenClaw desteklenmeyen `developer` rolleri için sağlayıcı 400 hatalarını önlemek amacıyla `compat.supportsDeveloperRole: false` değerini zorlar.
- Proxy tarzı OpenAI uyumlu yollar ayrıca yerel yalnızca OpenAI istek
  biçimlendirmesini atlar: `service_tier` yok, Responses `store` yok, prompt-cache ipuçları yok,
  OpenAI muhakeme uyumluluğu yük biçimlendirmesi yok ve gizli OpenClaw atıf
  üst bilgileri yok.
- `baseUrl` boşsa/atlanmışsa OpenClaw varsayılan OpenAI davranışını korur (bu, `api.openai.com` adresine çözülür).
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
- [Model Failover](/tr/concepts/model-failover) — geri dönüş zincirleri ve yeniden deneme davranışı
- [Configuration Reference](/tr/gateway/configuration-reference#agent-defaults) — model yapılandırma anahtarları
- [Providers](/tr/providers) — sağlayıcı başına kurulum kılavuzları
