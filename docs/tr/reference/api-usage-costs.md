---
read_when:
    - Hangi özelliklerin ücretli API'leri çağırabileceğini anlamak istiyorsanız
    - Anahtarları, maliyetleri ve kullanım görünürlüğünü denetlemeniz gerekiyorsa
    - '`/status` veya `/usage` maliyet raporlamasını açıklıyorsanız'
summary: Nelerin para harcayabileceğini, hangi anahtarların kullanıldığını ve kullanımın nasıl görüntüleneceğini denetleyin
title: API Kullanımı ve Maliyetler
x-i18n:
    generated_at: "2026-04-07T08:49:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: ab6eefcde9ac014df6cdda7aaa77ef48f16936ab12eaa883d9fe69425a31a2dd
    source_path: reference/api-usage-costs.md
    workflow: 15
---

# API kullanımı ve maliyetler

Bu belge, **API anahtarlarını çağırabilen özellikleri** ve maliyetlerinin nerede göründüğünü listeler. Odak noktası,
provider kullanımı veya ücretli API çağrıları üretebilen OpenClaw özellikleridir.

## Maliyetlerin göründüğü yerler (sohbet + CLI)

**Oturum başına maliyet anlık görüntüsü**

- `/status`, mevcut oturum modelini, bağlam kullanımını ve son yanıt belirteçlerini gösterir.
- Model **API anahtarı kimlik doğrulaması** kullanıyorsa `/status`, son yanıt için **tahmini maliyeti** de gösterir.
- Canlı oturum meta verileri seyrekse `/status`, en son transcript kullanım
  girişinden belirteç/önbellek sayaçlarını ve etkin çalışma zamanı model etiketini
  geri alabilir. Mevcut sıfır olmayan canlı değerler yine önceliklidir ve
  saklanan toplamlar eksikse veya daha küçükse prompt boyutlu transcript
  toplamları kazanabilir.

**Mesaj başına maliyet alt bilgisi**

- `/usage full`, her yanıta **tahmini maliyet** dahil bir kullanım alt bilgisi ekler (yalnızca API anahtarı).
- `/usage tokens`, yalnızca belirteçleri gösterir; abonelik tarzı OAuth/token ve CLI akışları dolar maliyetini gizler.
- Gemini CLI notu: CLI JSON çıktısı döndürdüğünde OpenClaw kullanımı
  `stats` içinden okur, `stats.cached` değerini `cacheRead` olarak normalize eder ve
  gerektiğinde giriş belirteçlerini `stats.input_tokens - stats.cached` üzerinden türetir.

Anthropic notu: Anthropic personeli bize OpenClaw tarzı Claude CLI kullanımına
yeniden izin verildiğini söyledi; bu nedenle OpenClaw, Anthropic yeni bir politika yayımlamadığı sürece
Claude CLI yeniden kullanımını ve `claude -p` kullanımını bu entegrasyon için
onaylanmış kabul eder. Anthropic hâlâ OpenClaw'ın
`/usage full` içinde gösterebileceği mesaj başına dolar tahmini sunmaz.

**CLI kullanım pencereleri (provider kotaları)**

- `openclaw status --usage` ve `openclaw channels list`, provider **kullanım pencerelerini**
  gösterir (mesaj başına maliyet değil, kota anlık görüntüleri).
- İnsan tarafından okunabilir çıktı, provider'lar arasında `X% left` olarak normalize edilir.
- Mevcut kullanım-penceresi provider'ları: Anthropic, GitHub Copilot, Gemini CLI,
  OpenAI Codex, MiniMax, Xiaomi ve z.ai.
- MiniMax notu: ham `usage_percent` / `usagePercent` alanları kalan
  kotayı ifade eder, bu nedenle OpenClaw bunları göstermeden önce tersine çevirir. Sayı tabanlı alanlar varsa yine
  öncelik kazanır. Provider `model_remains` döndürürse OpenClaw sohbet-modeli girdisini tercih eder,
  gerekirse pencere etiketini zaman damgalarından türetir ve
  plan etiketine model adını dahil eder.
- Bu kota pencereleri için kullanım kimlik doğrulaması, mümkün olduğunda provider'a özgü hook'lardan gelir;
  aksi halde OpenClaw auth profilleri, env veya config içindeki eşleşen OAuth/API anahtarı
  kimlik bilgilerine geri döner.

Ayrıntılar ve örnekler için bkz. [Token use & costs](/tr/reference/token-use).

## Anahtarlar nasıl keşfedilir

OpenClaw kimlik bilgilerini şuralardan alabilir:

- **Auth profilleri** (ajan başına, `auth-profiles.json` içinde saklanır).
- **Ortam değişkenleri** (ör. `OPENAI_API_KEY`, `BRAVE_API_KEY`, `FIRECRAWL_API_KEY`).
- **Config** (`models.providers.*.apiKey`, `plugins.entries.*.config.webSearch.apiKey`,
  `plugins.entries.firecrawl.config.webFetch.apiKey`, `memorySearch.*`,
  `talk.providers.*.apiKey`).
- **Skills** (`skills.entries.<name>.apiKey`), anahtarları skill süreci ortamına aktarabilir.

## Anahtar harcayabilen özellikler

### 1) Çekirdek model yanıtları (sohbet + araçlar)

Her yanıt veya araç çağrısı, **mevcut model provider**'ını kullanır (OpenAI, Anthropic vb.). Bu,
kullanım ve maliyetin birincil kaynağıdır.

Buna, OpenClaw'ın yerel kullanıcı arayüzü dışında yine de faturalandırılan abonelik tarzı barındırılan provider'lar da dahildir;
örneğin **OpenAI Codex**, **Alibaba Cloud Model Studio
Coding Plan**, **MiniMax Coding Plan**, **Z.AI / GLM Coding Plan** ve
**Extra Usage** etkinleştirilmiş Anthropic OpenClaw Claude-login yolu.

Fiyatlandırma yapılandırması için bkz. [Models](/tr/providers/models), gösterim için [Token use & costs](/tr/reference/token-use).

### 2) Media understanding (ses/görüntü/video)

Gelen medya, yanıt çalıştırılmadan önce özetlenebilir/transkribe edilebilir. Bu, model/provider API'lerini kullanır.

- Ses: OpenAI / Groq / Deepgram / Google / Mistral.
- Görüntü: OpenAI / OpenRouter / Anthropic / Google / MiniMax / Moonshot / Qwen / Z.AI.
- Video: Google / Qwen / Moonshot.

Bkz. [Media understanding](/tr/nodes/media-understanding).

### 3) Görüntü ve video üretimi

Paylaşılan üretim yetenekleri de provider anahtarlarını harcayabilir:

- Görüntü üretimi: OpenAI / Google / fal / MiniMax
- Video üretimi: Qwen

Görüntü üretimi,
`agents.defaults.imageGenerationModel` ayarlanmamışsa auth destekli varsayılan provider'ı çıkarım yoluyla belirleyebilir. Video üretimi ise şu anda
`qwen/wan2.6-t2v` gibi açık bir `agents.defaults.videoGenerationModel` gerektirir.

Bkz. [Image generation](/tr/tools/image-generation), [Qwen Cloud](/tr/providers/qwen)
ve [Models](/tr/concepts/models).

### 4) Bellek gömmeleri + anlamsal arama

Anlamsal bellek araması, uzak provider'lar için yapılandırıldığında **embedding API'lerini** kullanır:

- `memorySearch.provider = "openai"` → OpenAI embeddings
- `memorySearch.provider = "gemini"` → Gemini embeddings
- `memorySearch.provider = "voyage"` → Voyage embeddings
- `memorySearch.provider = "mistral"` → Mistral embeddings
- `memorySearch.provider = "ollama"` → Ollama embeddings (yerel/self-hosted; genellikle barındırılan API faturalandırması yoktur)
- Yerel gömmeler başarısız olursa uzak provider'a isteğe bağlı geri dönüş

`memorySearch.provider = "local"` ile yerelde tutabilirsiniz (API kullanımı yok).

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
- **Ollama Web Search**: varsayılan olarak anahtarsızdır, ancak erişilebilir bir Ollama ana makinesi ile `ollama signin` gerektirir; ana makine gerektiriyorsa normal Ollama provider bearer auth'unu da yeniden kullanabilir
- **Perplexity Search API**: `PERPLEXITY_API_KEY`, `OPENROUTER_API_KEY` veya `plugins.entries.perplexity.config.webSearch.apiKey`
- **Tavily**: `TAVILY_API_KEY` veya `plugins.entries.tavily.config.webSearch.apiKey`
- **DuckDuckGo**: anahtarsız geri dönüş (API faturalandırması yoktur, ancak resmî değildir ve HTML tabanlıdır)
- **SearXNG**: `SEARXNG_BASE_URL` veya `plugins.entries.searxng.config.webSearch.baseUrl` (anahtarsız/self-hosted; barındırılan API faturalandırması yoktur)

Eski `tools.web.search.*` provider yolları geçici uyumluluk katmanı üzerinden hâlâ yüklenir, ancak artık önerilen config yüzeyi değildir.

**Brave Search ücretsiz kredisi:** Her Brave planı, her ay yenilenen
\$5 ücretsiz kredi içerir. Search planı 1.000 istek başına \$5 olduğundan, bu kredi
ayda 1.000 isteği ücretsiz karşılar. Beklenmeyen ücretlerden kaçınmak için kullanım sınırınızı Brave panosunda ayarlayın.

Bkz. [Web tools](/tr/tools/web).

### 5) Web fetch aracı (Firecrawl)

`web_fetch`, API anahtarı mevcut olduğunda **Firecrawl** çağırabilir:

- `FIRECRAWL_API_KEY` veya `plugins.entries.firecrawl.config.webFetch.apiKey`

Firecrawl yapılandırılmamışsa araç doğrudan fetch + readability kullanımına geri döner (ücretli API yok).

Bkz. [Web tools](/tr/tools/web).

### 6) Provider kullanım anlık görüntüleri (status/health)

Bazı status komutları, kota pencerelerini veya auth sağlığını göstermek için **provider kullanım uç noktalarını** çağırır.
Bunlar genellikle düşük hacimli çağrılardır, ancak yine de provider API'lerine istek yapar:

- `openclaw status --usage`
- `openclaw models status --json`

Bkz. [Models CLI](/cli/models).

### 7) Compaction koruma özetlemesi

Compaction koruması, oturum geçmişini **mevcut model** kullanarak özetleyebilir; bu da
çalıştığında provider API'lerini çağırır.

Bkz. [Session management + compaction](/tr/reference/session-management-compaction).

### 8) Model tarama / probe

`openclaw models scan`, OpenRouter modellerini probe edebilir ve
probe etkin olduğunda `OPENROUTER_API_KEY` kullanır.

Bkz. [Models CLI](/cli/models).

### 9) Talk (konuşma)

Talk modu, yapılandırıldığında **ElevenLabs** çağırabilir:

- `ELEVENLABS_API_KEY` veya `talk.providers.elevenlabs.apiKey`

Bkz. [Talk mode](/tr/nodes/talk).

### 10) Skills (üçüncü taraf API'ler)

Skills, `skills.entries.<name>.apiKey` içinde `apiKey` saklayabilir. Bir skill bu anahtarı harici
API'ler için kullanıyorsa, skill'in provider'ına göre maliyet oluşturabilir.

Bkz. [Skills](/tr/tools/skills).
