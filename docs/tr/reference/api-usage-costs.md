---
read_when:
    - Hangi özelliklerin ücretli API'leri çağırabileceğini anlamak istiyorsunuz
    - Anahtarları, maliyetleri ve kullanım görünürlüğünü denetlemeniz gerekiyor
    - '`/status` veya `/usage` maliyet raporlamasını açıklıyorsunuz'
summary: Nelerin para harcayabileceğini, hangi anahtarların kullanıldığını ve kullanımın nasıl görüntüleneceğini denetleyin
title: API Kullanımı ve Maliyetler
x-i18n:
    generated_at: "2026-04-13T08:50:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: f5077e74d38ef781ac7a72603e9f9e3829a628b95c5a9967915ab0f321565429
    source_path: reference/api-usage-costs.md
    workflow: 15
---

# API kullanımı ve maliyetler

Bu belge, **API anahtarlarını çağırabilen özellikleri** ve bunların maliyetlerinin nerede göründüğünü listeler. Özellikle provider kullanımı veya ücretli API çağrıları oluşturabilen OpenClaw özelliklerine odaklanır.

## Maliyetlerin göründüğü yerler (sohbet + CLI)

**Oturum başına maliyet özeti**

- `/status`, mevcut oturum modelini, bağlam kullanımını ve son yanıt token'larını gösterir.
- Model **API anahtarı kimlik doğrulaması** kullanıyorsa, `/status` ayrıca son yanıt için **tahmini maliyeti** de gösterir.
- Canlı oturum meta verileri yetersizse, `/status` en son transkript kullanım girişinden token/cache sayaçlarını ve etkin çalışma zamanı model etiketini geri kazanabilir. Mevcut sıfır olmayan canlı değerler yine önceliklidir ve depolanan toplamlar eksikse veya daha küçükse, istem boyutundaki transkript toplamları üstün gelebilir.

**Mesaj başına maliyet altbilgisi**

- `/usage full`, her yanıta **tahmini maliyet** de dahil olmak üzere bir kullanım altbilgisi ekler (yalnızca API anahtarı).
- `/usage tokens` yalnızca token'ları gösterir; abonelik tarzı OAuth/token ve CLI akışları dolar maliyetini gizler.
- Gemini CLI notu: CLI JSON çıktısı döndürdüğünde, OpenClaw kullanımı `stats` içinden okur, `stats.cached` değerini `cacheRead` olarak normalize eder ve gerektiğinde giriş token'larını `stats.input_tokens - stats.cached` üzerinden türetir.

Anthropic notu: Anthropic çalışanları bize OpenClaw tarzı Claude CLI kullanımına yeniden izin verildiğini söyledi, bu nedenle Anthropic yeni bir politika yayımlamadığı sürece OpenClaw, Claude CLI yeniden kullanımını ve `claude -p` kullanımını bu entegrasyon için onaylı kabul eder. Anthropic hâlâ OpenClaw'ın `/usage full` içinde gösterebileceği mesaj başına bir dolar tahmini sunmuyor.

**CLI kullanım pencereleri (provider kotaları)**

- `openclaw status --usage` ve `openclaw channels list`, provider **kullanım pencerelerini** gösterir (mesaj başına maliyet değil, kota anlık görüntüleri).
- İnsan tarafından okunabilir çıktı, provider'lar arasında `X% kaldı` biçimine normalize edilir.
- Mevcut kullanım penceresi provider'ları: Anthropic, GitHub Copilot, Gemini CLI, OpenAI Codex, MiniMax, Xiaomi ve z.ai.
- MiniMax notu: ham `usage_percent` / `usagePercent` alanları kalan kotayı ifade eder, bu yüzden OpenClaw bunları görüntülemeden önce tersine çevirir. Sayı tabanlı alanlar mevcut olduğunda yine önceliklidir. Provider `model_remains` döndürürse, OpenClaw sohbet modeli girdisini tercih eder, gerektiğinde pencere etiketini zaman damgalarından türetir ve plan etiketine model adını ekler.
- Bu kota pencereleri için kullanım kimlik doğrulaması, mevcut olduğunda provider'a özgü hook'lardan gelir; aksi halde OpenClaw auth profilleri, ortam veya yapılandırmadan eşleşen OAuth/API anahtarı kimlik bilgilerine geri döner.

Ayrıntılar ve örnekler için [Token kullanımı ve maliyetler](/tr/reference/token-use) bölümüne bakın.

## Anahtarlar nasıl keşfedilir

OpenClaw kimlik bilgilerini şuralardan alabilir:

- **Auth profilleri** (ajan başına, `auth-profiles.json` içinde saklanır).
- **Ortam değişkenleri** (ör. `OPENAI_API_KEY`, `BRAVE_API_KEY`, `FIRECRAWL_API_KEY`).
- **Yapılandırma** (`models.providers.*.apiKey`, `plugins.entries.*.config.webSearch.apiKey`,
  `plugins.entries.firecrawl.config.webFetch.apiKey`, `memorySearch.*`,
  `talk.providers.*.apiKey`).
- **Skills** (`skills.entries.<name>.apiKey`); bunlar anahtarları skill süreç ortamına aktarabilir.

## Anahtar harcayabilen özellikler

### 1) Çekirdek model yanıtları (sohbet + araçlar)

Her yanıt veya araç çağrısı **mevcut model provider'ını** (OpenAI, Anthropic vb.) kullanır. Bu, kullanım ve maliyetin birincil kaynağıdır.

Buna, maliyeti yine de OpenClaw'ın yerel arayüzü dışında faturalandırılan abonelik tarzı barındırılan provider'lar da dahildir; örneğin **OpenAI Codex**, **Alibaba Cloud Model Studio Coding Plan**, **MiniMax Coding Plan**, **Z.AI / GLM Coding Plan** ve **Extra Usage** etkinleştirilmiş Anthropic'in OpenClaw Claude-login yolu.

Fiyatlandırma yapılandırması için [Models](/tr/providers/models), görüntüleme için [Token kullanımı ve maliyetler](/tr/reference/token-use) bölümüne bakın.

### 2) Medya anlama (ses/görüntü/video)

Gelen medya, yanıt çalışmadan önce özetlenebilir veya yazıya dökülebilir. Bu, model/provider API'lerini kullanır.

- Ses: OpenAI / Groq / Deepgram / Google / Mistral.
- Görüntü: OpenAI / OpenRouter / Anthropic / Google / MiniMax / Moonshot / Qwen / Z.AI.
- Video: Google / Qwen / Moonshot.

Bkz. [Medya anlama](/tr/nodes/media-understanding).

### 3) Görüntü ve video üretimi

Paylaşılan üretim yetenekleri de provider anahtarları harcayabilir:

- Görüntü üretimi: OpenAI / Google / fal / MiniMax
- Video üretimi: Qwen

Görüntü üretimi, `agents.defaults.imageGenerationModel` ayarlanmadığında auth destekli varsayılan bir provider'ı çıkarımsayabilir. Video üretimi şu anda `qwen/wan2.6-t2v` gibi açık bir `agents.defaults.videoGenerationModel` gerektirir.

Bkz. [Image generation](/tr/tools/image-generation), [Qwen Cloud](/tr/providers/qwen) ve [Models](/tr/concepts/models).

### 4) Bellek embedding'leri + anlamsal arama

Anlamsal bellek araması, uzak provider'lar için yapılandırıldığında **embedding API'lerini** kullanır:

- `memorySearch.provider = "openai"` → OpenAI embedding'leri
- `memorySearch.provider = "gemini"` → Gemini embedding'leri
- `memorySearch.provider = "voyage"` → Voyage embedding'leri
- `memorySearch.provider = "mistral"` → Mistral embedding'leri
- `memorySearch.provider = "lmstudio"` → LM Studio embedding'leri (yerel/self-hosted)
- `memorySearch.provider = "ollama"` → Ollama embedding'leri (yerel/self-hosted; genellikle barındırılan API faturalaması yoktur)
- Yerel embedding'ler başarısız olursa uzak bir provider'a isteğe bağlı geri dönüş

`memorySearch.provider = "local"` ile yerel kalabilirsiniz (API kullanımı yok).

Bkz. [Memory](/tr/concepts/memory).

### 5) Web arama aracı

`web_search`, provider'ınıza bağlı olarak kullanım ücreti doğurabilir:

- **Brave Search API**: `BRAVE_API_KEY` veya `plugins.entries.brave.config.webSearch.apiKey`
- **Exa**: `EXA_API_KEY` veya `plugins.entries.exa.config.webSearch.apiKey`
- **Firecrawl**: `FIRECRAWL_API_KEY` veya `plugins.entries.firecrawl.config.webSearch.apiKey`
- **Gemini (Google Search)**: `GEMINI_API_KEY` veya `plugins.entries.google.config.webSearch.apiKey`
- **Grok (xAI)**: `XAI_API_KEY` veya `plugins.entries.xai.config.webSearch.apiKey`
- **Kimi (Moonshot)**: `KIMI_API_KEY`, `MOONSHOT_API_KEY` veya `plugins.entries.moonshot.config.webSearch.apiKey`
- **MiniMax Search**: `MINIMAX_CODE_PLAN_KEY`, `MINIMAX_CODING_API_KEY`, `MINIMAX_API_KEY` veya `plugins.entries.minimax.config.webSearch.apiKey`
- **Ollama Web Search**: varsayılan olarak anahtar gerektirmez, ancak erişilebilir bir Ollama host'u ve `ollama signin` gerektirir; host gerektirdiğinde normal Ollama provider bearer auth'u da yeniden kullanabilir
- **Perplexity Search API**: `PERPLEXITY_API_KEY`, `OPENROUTER_API_KEY` veya `plugins.entries.perplexity.config.webSearch.apiKey`
- **Tavily**: `TAVILY_API_KEY` veya `plugins.entries.tavily.config.webSearch.apiKey`
- **DuckDuckGo**: anahtarsız geri dönüş (API faturası yok, ancak resmî değil ve HTML tabanlı)
- **SearXNG**: `SEARXNG_BASE_URL` veya `plugins.entries.searxng.config.webSearch.baseUrl` (anahtarsız/self-hosted; barındırılan API faturalaması yok)

Eski `tools.web.search.*` provider yolları, geçici uyumluluk katmanı üzerinden hâlâ yüklenir, ancak artık önerilen yapılandırma yüzeyi değildir.

**Brave Search ücretsiz kredisi:** Her Brave planı, her ay yenilenen \$5 ücretsiz kredi içerir. Search planı 1.000 istek başına \$5 tutarındadır, bu nedenle kredi ek ücret olmadan ayda 1.000 isteği kapsar. Beklenmedik ücretlerden kaçınmak için kullanım sınırınızı Brave kontrol panelinde ayarlayın.

Bkz. [Web tools](/tr/tools/web).

### 5) Web getirme aracı (Firecrawl)

Bir API anahtarı mevcut olduğunda `web_fetch`, **Firecrawl** çağırabilir:

- `FIRECRAWL_API_KEY` veya `plugins.entries.firecrawl.config.webFetch.apiKey`

Firecrawl yapılandırılmamışsa araç, doğrudan fetch + readability'ye geri döner (ücretli API yok).

Bkz. [Web tools](/tr/tools/web).

### 6) Provider kullanım anlık görüntüleri (durum/sağlık)

Bazı durum komutları, kota pencerelerini veya auth sağlığını göstermek için **provider kullanım uç noktalarını** çağırır. Bunlar genellikle düşük hacimli çağrılardır ancak yine de provider API'lerine istek atar:

- `openclaw status --usage`
- `openclaw models status --json`

Bkz. [Models CLI](/cli/models).

### 7) Compaction koruma amaçlı özetleme

Compaction koruması, oturum geçmişini **mevcut model** kullanarak özetleyebilir; bu da çalıştığında provider API'lerini çağırır.

Bkz. [Oturum yönetimi + compaction](/tr/reference/session-management-compaction).

### 8) Model tarama / yoklama

`openclaw models scan`, OpenRouter modellerini yoklayabilir ve yoklama etkin olduğunda `OPENROUTER_API_KEY` kullanır.

Bkz. [Models CLI](/cli/models).

### 9) Talk (konuşma)

Talk modu, yapılandırıldığında **ElevenLabs** çağırabilir:

- `ELEVENLABS_API_KEY` veya `talk.providers.elevenlabs.apiKey`

Bkz. [Talk mode](/tr/nodes/talk).

### 10) Skills (üçüncü taraf API'ler)

Skills, `skills.entries.<name>.apiKey` içinde `apiKey` saklayabilir. Bir skill bu anahtarı harici API'ler için kullanıyorsa, skill'in provider'ına göre maliyet oluşturabilir.

Bkz. [Skills](/tr/tools/skills).
