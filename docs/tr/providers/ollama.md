---
read_when:
    - OpenClaw'ı Ollama üzerinden bulut veya yerel modellerle çalıştırmak istiyorsunuz
    - Ollama kurulumu ve yapılandırma rehberine ihtiyacınız var
summary: OpenClaw'ı Ollama ile çalıştırın (bulut ve yerel modeller)
title: Ollama
x-i18n:
    generated_at: "2026-04-08T02:18:18Z"
    model: gpt-5.4
    provider: openai
    source_hash: 222ec68f7d4bb29cc7796559ddef1d5059f5159e7a51e2baa3a271ddb3abb716
    source_path: providers/ollama.md
    workflow: 15
---

# Ollama

Ollama, makinenizde açık kaynaklı modeller çalıştırmayı kolaylaştıran yerel bir LLM çalışma zamanıdır. OpenClaw, Ollama'nın yerel API'siyle (`/api/chat`) entegre olur, akış ve araç çağırmayı destekler ve `OLLAMA_API_KEY` (veya bir auth profili) ile etkinleştirdiğinizde ve açık bir `models.providers.ollama` girdisi tanımlamadığınızda yerel Ollama modellerini otomatik olarak keşfedebilir.

<Warning>
**Uzak Ollama kullanıcıları**: OpenClaw ile `/v1` OpenAI uyumlu URL'yi (`http://host:11434/v1`) kullanmayın. Bu, araç çağırmayı bozar ve modeller ham araç JSON'unu düz metin olarak çıkarabilir. Bunun yerine yerel Ollama API URL'sini kullanın: `baseUrl: "http://host:11434"` (`/v1` olmadan).
</Warning>

## Hızlı başlangıç

### Onboarding (önerilir)

Ollama kurmanın en hızlı yolu onboarding üzerinden geçer:

```bash
openclaw onboard
```

Sağlayıcı listesinden **Ollama** seçin. Onboarding şunları yapar:

1. Ollama örneğinize ulaşılabilen Ollama temel URL'sini sorar (varsayılan `http://127.0.0.1:11434`).
2. **Cloud + Local** (bulut modelleri ve yerel modeller) veya **Local** (yalnızca yerel modeller) seçmenizi sağlar.
3. **Cloud + Local** seçerseniz ve ollama.com üzerinde oturumunuz açık değilse tarayıcı tabanlı bir oturum açma akışı başlatır.
4. Mevcut modelleri keşfeder ve varsayılanlar önerir.
5. Seçilen model yerelde mevcut değilse onu otomatik olarak çeker.

Etkileşimsiz mod da desteklenir:

```bash
openclaw onboard --non-interactive \
  --auth-choice ollama \
  --accept-risk
```

İsteğe bağlı olarak özel bir temel URL veya model belirtebilirsiniz:

```bash
openclaw onboard --non-interactive \
  --auth-choice ollama \
  --custom-base-url "http://ollama-host:11434" \
  --custom-model-id "qwen3.5:27b" \
  --accept-risk
```

### Manuel kurulum

1. Ollama'yı kurun: [https://ollama.com/download](https://ollama.com/download)

2. Yerel çıkarım istiyorsanız yerel bir model çekin:

```bash
ollama pull gemma4
# veya
ollama pull gpt-oss:20b
# veya
ollama pull llama3.3
```

3. Bulut modellerini de istiyorsanız oturum açın:

```bash
ollama signin
```

4. Onboarding çalıştırın ve `Ollama` seçin:

```bash
openclaw onboard
```

- `Local`: yalnızca yerel modeller
- `Cloud + Local`: yerel modeller artı bulut modelleri
- `kimi-k2.5:cloud`, `minimax-m2.7:cloud` ve `glm-5.1:cloud` gibi bulut modelleri yerel `ollama pull` **gerektirmez**

OpenClaw şu anda şunları önerir:

- yerel varsayılan: `gemma4`
- bulut varsayılanları: `kimi-k2.5:cloud`, `minimax-m2.7:cloud`, `glm-5.1:cloud`

5. Manuel kurulumu tercih ediyorsanız Ollama'yı doğrudan OpenClaw için etkinleştirin (herhangi bir değer çalışır; Ollama gerçek bir anahtar gerektirmez):

```bash
# Ortam değişkeni ayarla
export OLLAMA_API_KEY="ollama-local"

# Veya yapılandırma dosyanızda ayarlayın
openclaw config set models.providers.ollama.apiKey "ollama-local"
```

6. Modelleri inceleyin veya değiştirin:

```bash
openclaw models list
openclaw models set ollama/gemma4
```

7. Veya varsayılanı yapılandırmada ayarlayın:

```json5
{
  agents: {
    defaults: {
      model: { primary: "ollama/gemma4" },
    },
  },
}
```

## Model keşfi (örtük sağlayıcı)

`OLLAMA_API_KEY` (veya bir auth profili) ayarladığınızda ve **`models.providers.ollama` tanımlamadığınızda**, OpenClaw modelleri `http://127.0.0.1:11434` adresindeki yerel Ollama örneğinden keşfeder:

- `/api/tags` sorgulanır
- Mümkün olduğunda `contextWindow` okumak için en iyi çabayla `/api/show` aramaları kullanılır
- `reasoning`, model adı sezgisiyle işaretlenir (`r1`, `reasoning`, `think`)
- `maxTokens`, OpenClaw tarafından kullanılan varsayılan Ollama azami token sınırına ayarlanır
- Tüm maliyetler `0` olarak ayarlanır

Bu, kataloğu yerel Ollama örneğiyle uyumlu tutarken manuel model girdilerinden kaçınmanızı sağlar.

Hangi modellerin mevcut olduğunu görmek için:

```bash
ollama list
openclaw models list
```

Yeni bir model eklemek için onu Ollama ile çekmeniz yeterlidir:

```bash
ollama pull mistral
```

Yeni model otomatik olarak keşfedilir ve kullanıma sunulur.

`models.providers.ollama` değerini açıkça ayarlarsanız otomatik keşif atlanır ve modelleri manuel olarak tanımlamanız gerekir (aşağıya bakın).

## Yapılandırma

### Temel kurulum (örtük keşif)

Ollama'yı etkinleştirmenin en basit yolu ortam değişkeni kullanmaktır:

```bash
export OLLAMA_API_KEY="ollama-local"
```

### Açık kurulum (manuel modeller)

Şu durumlarda açık yapılandırma kullanın:

- Ollama başka bir host/port üzerinde çalışıyorsa.
- Belirli bağlam pencerelerini veya model listelerini zorlamak istiyorsanız.
- Tamamen manuel model tanımları istiyorsanız.

```json5
{
  models: {
    providers: {
      ollama: {
        baseUrl: "http://ollama-host:11434",
        apiKey: "ollama-local",
        api: "ollama",
        models: [
          {
            id: "gpt-oss:20b",
            name: "GPT-OSS 20B",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 8192,
            maxTokens: 8192 * 10
          }
        ]
      }
    }
  }
}
```

`OLLAMA_API_KEY` ayarlıysa sağlayıcı girdisinde `apiKey` değerini atlayabilirsiniz; OpenClaw bunu kullanılabilirlik kontrolleri için doldurur.

### Özel temel URL (açık yapılandırma)

Ollama farklı bir host veya port üzerinde çalışıyorsa (açık yapılandırma otomatik keşfi devre dışı bırakır, bu yüzden modelleri manuel tanımlayın):

```json5
{
  models: {
    providers: {
      ollama: {
        apiKey: "ollama-local",
        baseUrl: "http://ollama-host:11434", // /v1 yok - yerel Ollama API URL'sini kullanın
        api: "ollama", // yerel araç çağırma davranışını garanti etmek için açıkça ayarlayın
      },
    },
  },
}
```

<Warning>
URL'ye `/v1` eklemeyin. `/v1` yolu, araç çağırmanın güvenilir olmadığı OpenAI uyumlu modu kullanır. Yol son eki olmadan temel Ollama URL'sini kullanın.
</Warning>

### Model seçimi

Bir kez yapılandırıldığında tüm Ollama modelleriniz kullanılabilir olur:

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "ollama/gpt-oss:20b",
        fallbacks: ["ollama/llama3.3", "ollama/qwen2.5-coder:32b"],
      },
    },
  },
}
```

## Bulut modelleri

Bulut modelleri, yerel modellerinizle birlikte bulutta barındırılan modelleri (`kimi-k2.5:cloud`, `minimax-m2.7:cloud`, `glm-5.1:cloud` gibi) çalıştırmanızı sağlar.

Bulut modellerini kullanmak için kurulum sırasında **Cloud + Local** modunu seçin. Sihirbaz oturumunuzun açık olup olmadığını kontrol eder ve gerektiğinde tarayıcı tabanlı oturum açma akışı başlatır. Kimlik doğrulama doğrulanamazsa sihirbaz yerel model varsayılanlarına geri döner.

Doğrudan [ollama.com/signin](https://ollama.com/signin) adresinden de oturum açabilirsiniz.

## Ollama Web Search

OpenClaw ayrıca paketlenmiş bir `web_search`
sağlayıcısı olarak **Ollama Web Search** desteği sunar.

- Yapılandırılmış Ollama host'unuzu kullanır (`models.providers.ollama.baseUrl` ayarlıysa onu,
  aksi halde `http://127.0.0.1:11434`).
- Anahtar gerektirmez.
- Ollama'nın çalışıyor olmasını ve `ollama signin` ile oturum açılmış olmasını gerektirir.

`openclaw onboard` veya
`openclaw configure --section web` sırasında **Ollama Web Search** seçin ya da şunu ayarlayın:

```json5
{
  tools: {
    web: {
      search: {
        provider: "ollama",
      },
    },
  },
}
```

Tam kurulum ve davranış ayrıntıları için [Ollama Web Search](/tr/tools/ollama-search) bölümüne bakın.

## Gelişmiş

### Reasoning modelleri

OpenClaw, varsayılan olarak `deepseek-r1`, `reasoning` veya `think` gibi adlara sahip modelleri reasoning destekli kabul eder:

```bash
ollama pull deepseek-r1:32b
```

### Model maliyetleri

Ollama ücretsizdir ve yerelde çalışır, bu nedenle tüm model maliyetleri $0 olarak ayarlanır.

### Akış yapılandırması

OpenClaw'ın Ollama entegrasyonu varsayılan olarak **yerel Ollama API'sini** (`/api/chat`) kullanır; bu, akış ve araç çağırmayı aynı anda tam olarak destekler. Özel bir yapılandırma gerekmez.

#### Eski OpenAI uyumlu mod

<Warning>
**Araç çağırma OpenAI uyumlu modda güvenilir değildir.** Bu modu yalnızca bir proxy için OpenAI biçimine ihtiyacınız varsa ve yerel araç çağırma davranışına bağımlı değilseniz kullanın.
</Warning>

Bunun yerine OpenAI uyumlu uç noktayı kullanmanız gerekiyorsa (ör. yalnızca OpenAI biçimini destekleyen bir proxy arkasında), `api: "openai-completions"` değerini açıkça ayarlayın:

```json5
{
  models: {
    providers: {
      ollama: {
        baseUrl: "http://ollama-host:11434/v1",
        api: "openai-completions",
        injectNumCtxForOpenAICompat: true, // varsayılan: true
        apiKey: "ollama-local",
        models: [...]
      }
    }
  }
}
```

Bu mod aynı anda akış + araç çağırmayı desteklemeyebilir. Model yapılandırmasında `params: { streaming: false }` ile akışı devre dışı bırakmanız gerekebilir.

Ollama ile `api: "openai-completions"` kullanıldığında OpenClaw, Ollama'nın sessizce 4096 bağlam penceresine geri dönmemesi için varsayılan olarak `options.num_ctx` enjekte eder. Proxy'niz/yukarı akışınız bilinmeyen `options` alanlarını reddediyorsa bu davranışı devre dışı bırakın:

```json5
{
  models: {
    providers: {
      ollama: {
        baseUrl: "http://ollama-host:11434/v1",
        api: "openai-completions",
        injectNumCtxForOpenAICompat: false,
        apiKey: "ollama-local",
        models: [...]
      }
    }
  }
}
```

### Bağlam pencereleri

Otomatik keşfedilen modeller için OpenClaw, mümkün olduğunda Ollama tarafından bildirilen bağlam penceresini kullanır; aksi halde OpenClaw tarafından kullanılan varsayılan Ollama bağlam penceresine geri döner. Açık sağlayıcı yapılandırmasında `contextWindow` ve `maxTokens` değerlerini geçersiz kılabilirsiniz.

## Sorun giderme

### Ollama algılanmadı

Ollama'nın çalıştığından, `OLLAMA_API_KEY` (veya bir auth profili) ayarladığınızdan ve açık bir `models.providers.ollama` girdisi tanımlamadığınızdan emin olun:

```bash
ollama serve
```

Ayrıca API'nin erişilebilir olduğunu doğrulayın:

```bash
curl http://localhost:11434/api/tags
```

### Kullanılabilir model yok

Modeliniz listelenmiyorsa şunlardan birini yapın:

- Modeli yerelde çekin veya
- Modeli `models.providers.ollama` içinde açıkça tanımlayın.

Model eklemek için:

```bash
ollama list  # Kurulu olanları görün
ollama pull gemma4
ollama pull gpt-oss:20b
ollama pull llama3.3     # Veya başka bir model
```

### Bağlantı reddedildi

Ollama'nın doğru port üzerinde çalıştığını kontrol edin:

```bash
# Ollama çalışıyor mu kontrol edin
ps aux | grep ollama

# Veya Ollama'yı yeniden başlatın
ollama serve
```

## Ayrıca bakın

- [Model Sağlayıcıları](/tr/concepts/model-providers) - Tüm sağlayıcılara genel bakış
- [Model Seçimi](/tr/concepts/models) - Modeller nasıl seçilir
- [Yapılandırma](/tr/gateway/configuration) - Tam yapılandırma referansı
