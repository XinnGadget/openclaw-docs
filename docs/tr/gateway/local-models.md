---
read_when:
    - Modelleri kendi GPU makinenizden sunmak istiyorsunuz
    - LM Studio’yu veya OpenAI uyumlu bir proxy’yi yapılandırıyorsunuz
    - En güvenli yerel model rehberine ihtiyacınız var
summary: OpenClaw’ı yerel LLM’lerde çalıştırın (LM Studio, vLLM, LiteLLM, özel OpenAI uç noktaları)
title: Yerel Modeller
x-i18n:
    generated_at: "2026-04-14T08:52:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1544c522357ba4b18dfa6d05ea8d60c7c6262281b53863d9aee7002464703ca7
    source_path: gateway/local-models.md
    workflow: 15
---

# Yerel modeller

Yerel kullanım mümkündür, ancak OpenClaw büyük bağlam ve prompt injection’a karşı güçlü savunmalar bekler. Küçük kartlar bağlamı kırpar ve güvenliği zayıflatır. Hedefinizi yüksek tutun: **≥2 tam donanımlı Mac Studio veya eşdeğer GPU sistemi (~30 bin $+)**. Tek bir **24 GB** GPU yalnızca daha hafif prompt’larda ve daha yüksek gecikmeyle çalışır. Çalıştırabildiğiniz **en büyük / tam boyutlu model varyantını kullanın**; yoğun biçimde quantize edilmiş veya “small” checkpoint’ler prompt injection riskini artırır (bkz. [Güvenlik](/tr/gateway/security)).

En az sürtünmeli yerel model kurulumu istiyorsanız, [LM Studio](/tr/providers/lmstudio) veya [Ollama](/tr/providers/ollama) ile başlayıp `openclaw onboard` çalıştırın. Bu sayfa, daha üst seviye yerel yığınlar ve özel OpenAI uyumlu yerel sunucular için görüş odaklı rehberdir.

## Önerilen: LM Studio + büyük yerel model (Responses API)

Şu anda en iyi yerel yığın. LM Studio’da büyük bir model yükleyin (örneğin, tam boyutlu bir Qwen, DeepSeek veya Llama derlemesi), yerel sunucuyu etkinleştirin (varsayılan `http://127.0.0.1:1234`) ve akıl yürütmeyi nihai metinden ayrı tutmak için Responses API kullanın.

```json5
{
  agents: {
    defaults: {
      model: { primary: “lmstudio/my-local-model” },
      models: {
        “anthropic/claude-opus-4-6”: { alias: “Opus” },
        “lmstudio/my-local-model”: { alias: “Local” },
      },
    },
  },
  models: {
    mode: “merge”,
    providers: {
      lmstudio: {
        baseUrl: “http://127.0.0.1:1234/v1”,
        apiKey: “lmstudio”,
        api: “openai-responses”,
        models: [
          {
            id: “my-local-model”,
            name: “Yerel Model”,
            reasoning: false,
            input: [“text”],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 196608,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

**Kurulum kontrol listesi**

- LM Studio’yu yükleyin: [https://lmstudio.ai](https://lmstudio.ai)
- LM Studio’da, **mevcut en büyük model derlemesini** indirin (“small”/ağır quantize edilmiş varyantlardan kaçının), sunucuyu başlatın ve `http://127.0.0.1:1234/v1/models` çıktısında modelin listelendiğini doğrulayın.
- `my-local-model` değerini LM Studio’da görünen gerçek model kimliğiyle değiştirin.
- Modeli yüklü tutun; soğuk yükleme başlangıç gecikmesi ekler.
- LM Studio derlemeniz farklıysa `contextWindow`/`maxTokens` değerlerini ayarlayın.
- WhatsApp için yalnızca son metnin gönderilmesi amacıyla Responses API kullanın.

Yerelde çalıştırıyor olsanız bile barındırılan modelleri yapılandırılmış tutun; yedeklerin kullanılabilir kalması için `models.mode: "merge"` kullanın.

### Hibrit yapılandırma: barındırılan birincil, yerel yedek

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-6",
        fallbacks: ["lmstudio/my-local-model", "anthropic/claude-opus-4-6"],
      },
      models: {
        "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
        "lmstudio/my-local-model": { alias: "Local" },
        "anthropic/claude-opus-4-6": { alias: "Opus" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      lmstudio: {
        baseUrl: "http://127.0.0.1:1234/v1",
        apiKey: "lmstudio",
        api: "openai-responses",
        models: [
          {
            id: "my-local-model",
            name: "Yerel Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 196608,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

### Önce yerel, güvenlik ağı olarak barındırılan

Birincil ve yedek sırasını değiştirin; yerel makine devre dışı kaldığında Sonnet veya Opus’a geri dönebilmek için aynı providers bloğunu ve `models.mode: "merge"` ayarını koruyun.

### Bölgesel barındırma / veri yönlendirme

- Barındırılan MiniMax/Kimi/GLM varyantları OpenRouter üzerinde de bölgeye sabitlenmiş uç noktalarla mevcuttur (ör. ABD’de barındırılan). Trafiği seçtiğiniz yargı alanında tutarken Anthropic/OpenAI yedeklerini korumak için orada bölgesel varyantı seçin ve yine `models.mode: "merge"` kullanın.
- Yalnızca yerel kullanım en güçlü gizlilik yoludur; barındırılan bölgesel yönlendirme ise sağlayıcı özelliklerine ihtiyaç duyduğunuz ama veri akışı üzerinde kontrol de istediğiniz durumlar için orta yoldur.

## Diğer OpenAI uyumlu yerel proxy’ler

vLLM, LiteLLM, OAI-proxy veya özel Gateway’ler OpenAI tarzı bir `/v1` uç noktası sunuyorsa çalışır. Yukarıdaki provider bloğunu kendi uç noktanız ve model kimliğinizle değiştirin:

```json5
{
  models: {
    mode: "merge",
    providers: {
      local: {
        baseUrl: "http://127.0.0.1:8000/v1",
        apiKey: "sk-local",
        api: "openai-responses",
        models: [
          {
            id: "my-local-model",
            name: "Yerel Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 120000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

Barındırılan modellerin yedek olarak kullanılabilir kalması için `models.mode: "merge"` ayarını koruyun.

Yerel/proxy’lenmiş `/v1` arka uçları için davranış notu:

- OpenClaw bunları yerel OpenAI uç noktaları olarak değil, proxy tarzı OpenAI uyumlu yollar olarak ele alır
- yalnızca yerel OpenAI’ye özgü istek şekillendirmesi burada uygulanmaz: `service_tier` yoktur, Responses `store` yoktur, OpenAI reasoning-compat payload şekillendirmesi yoktur ve prompt-cache ipuçları yoktur
- gizli OpenClaw atıf başlıkları (`originator`, `version`, `User-Agent`) bu özel proxy URL’lerine eklenmez

Daha katı OpenAI uyumlu arka uçlar için uyumluluk notları:

- Bazı sunucular Chat Completions içinde yapılandırılmış content-part dizileri yerine yalnızca string `messages[].content` kabul eder. Bu uç noktalar için `models.providers.<provider>.models[].compat.requiresStringContent: true` ayarlayın.
- Bazı daha küçük veya daha katı yerel arka uçlar, özellikle tool şemaları dahil edildiğinde, OpenClaw’ın tam agent-runtime prompt yapısıyla kararsız çalışır. Arka uç küçük doğrudan `/v1/chat/completions` çağrılarında çalışıyor ama normal OpenClaw agent dönüşlerinde başarısız oluyorsa önce `models.providers.<provider>.models[].compat.supportsTools: false` deneyin.
- Arka uç yalnızca daha büyük OpenClaw çalıştırmalarında hâlâ başarısız oluyorsa, kalan sorun genellikle OpenClaw’ın taşıma katmanı değil, yukarı akış model/sunucu kapasitesi veya bir arka uç hatasıdır.

## Sorun giderme

- Gateway proxy’ye ulaşabiliyor mu? `curl http://127.0.0.1:1234/v1/models`.
- LM Studio modeli boşaltılmış mı? Yeniden yükleyin; “takılı kalıyor” durumunun yaygın nedenlerinden biri soğuk başlangıçtır.
- OpenClaw, algılanan bağlam penceresi **32k**’nin altındaysa uyarır ve **16k**’nin altında engeller. Bu ön kontrolde takılırsanız, sunucu/model bağlam sınırını artırın veya daha büyük bir model seçin.
- Bağlam hataları mı var? `contextWindow` değerini düşürün veya sunucu sınırınızı yükseltin.
- OpenAI uyumlu sunucu `messages[].content ... expected a string` döndürüyor mu? Bu model girdisine `compat.requiresStringContent: true` ekleyin.
- Doğrudan küçük `/v1/chat/completions` çağrıları çalışıyor ama `openclaw infer model run` Gemma veya başka bir yerel modelde başarısız mı oluyor? Önce tool şemalarını `compat.supportsTools: false` ile devre dışı bırakın, sonra yeniden test edin. Sunucu yalnızca daha büyük OpenClaw prompt’larında hâlâ çöküyorsa, bunu yukarı akış sunucu/model sınırlaması olarak değerlendirin.
- Güvenlik: yerel modeller sağlayıcı tarafı filtreleri atlar; prompt injection etki alanını sınırlamak için agent’ları dar tutun ve Compaction’ı açık bırakın.
