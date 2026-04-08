---
read_when:
    - Modelleri kendi GPU kutunuzdan sunmak istiyorsunuz
    - LM Studio veya OpenAI uyumlu bir proxy'yi yapılandırıyorsunuz
    - En güvenli yerel model rehberliğine ihtiyacınız var
summary: OpenClaw'u yerel LLM'lerde çalıştırın (LM Studio, vLLM, LiteLLM, özel OpenAI uç noktaları)
title: Yerel Modeller
x-i18n:
    generated_at: "2026-04-08T02:14:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: d619d72b0e06914ebacb7e9f38b746caf1b9ce8908c9c6638c3acdddbaa025e8
    source_path: gateway/local-models.md
    workflow: 15
---

# Yerel modeller

Yerel kullanım mümkündür, ancak OpenClaw geniş bağlam ve istem enjeksiyonuna karşı güçlü savunmalar bekler. Küçük kartlar bağlamı kısaltır ve güvenliği sızdırır. Yüksek hedefleyin: **≥2 tam donanımlı Mac Studio veya eşdeğer GPU sistemi (~$30k+)**. Tek bir **24 GB** GPU yalnızca daha hafif istemlerde ve daha yüksek gecikmeyle işe yarar. Çalıştırabildiğiniz **en büyük / tam boyutlu model varyantını** kullanın; aşırı nicemlenmiş veya “küçük” checkpoint'ler istem enjeksiyonu riskini artırır (bkz. [Security](/tr/gateway/security)).

En düşük sürtünmeli yerel kurulum istiyorsanız, [Ollama](/tr/providers/ollama) ve `openclaw onboard` ile başlayın. Bu sayfa, daha üst düzey yerel yığınlar ve özel OpenAI uyumlu yerel sunucular için görüşlü rehberdir.

## Önerilen: LM Studio + büyük yerel model (Responses API)

Şu anki en iyi yerel yığın. LM Studio içinde büyük bir model yükleyin (örneğin tam boyutlu bir Qwen, DeepSeek veya Llama derlemesi), yerel sunucuyu etkinleştirin (varsayılan `http://127.0.0.1:1234`) ve akıl yürütmeyi son metinden ayrı tutmak için Responses API kullanın.

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
            name: “Local Model”,
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

- LM Studio'yu yükleyin: [https://lmstudio.ai](https://lmstudio.ai)
- LM Studio içinde **mevcut en büyük model derlemesini** indirin (“small”/yoğun biçimde nicemlenmiş varyantlardan kaçının), sunucuyu başlatın ve `http://127.0.0.1:1234/v1/models` içinde listelendiğini doğrulayın.
- `my-local-model` değerini LM Studio'da gösterilen gerçek model kimliğiyle değiştirin.
- Modeli yüklü tutun; soğuk yükleme başlangıç gecikmesi ekler.
- LM Studio derlemeniz farklıysa `contextWindow`/`maxTokens` değerlerini ayarlayın.
- WhatsApp için yalnızca son metnin gönderilmesi amacıyla Responses API'ye bağlı kalın.

Yerelde çalışırken bile barındırılan modelleri yapılandırılmış tutun; yedeklerin kullanılabilir kalması için `models.mode: "merge"` kullanın.

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
            name: "Local Model",
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

### Önce yerel, barındırılan güvenlik ağıyla

Birincil ve yedek sırasını değiştirin; yerel kutu devre dışı kaldığında Sonnet veya Opus'a geri dönebilmek için aynı sağlayıcı bloğunu ve `models.mode: "merge"` ayarını koruyun.

### Bölgesel barındırma / veri yönlendirme

- Barındırılan MiniMax/Kimi/GLM varyantları OpenRouter üzerinde bölgeye sabitlenmiş uç noktalarla da vardır (ör. ABD'de barındırılan). Trafiği seçtiğiniz yargı alanında tutarken Anthropic/OpenAI yedeklerini de kullanabilmek için orada bölgesel varyantı seçin ve `models.mode: "merge"` kullanmaya devam edin.
- Yalnızca yerel kullanım, gizlilik açısından en güçlü yoldur; barındırılan bölgesel yönlendirme, sağlayıcı özelliklerine ihtiyaç duyduğunuz ama veri akışı üzerinde kontrol istediğiniz durumlarda orta yoldur.

## Diğer OpenAI uyumlu yerel proxy'ler

vLLM, LiteLLM, OAI-proxy veya özel gateway'ler, OpenAI tarzı bir `/v1` uç noktası sunuyorlarsa çalışır. Yukarıdaki sağlayıcı bloğunu kendi uç noktanız ve model kimliğinizle değiştirin:

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
            name: "Local Model",
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

Barındırılan modellerin yedek olarak kullanılabilir kalması için `models.mode: "merge"` kullanmaya devam edin.

Yerel/proxy'lenmiş `/v1` arka uçları için davranış notu:

- OpenClaw bunları yerel OpenAI uç noktaları olarak değil, proxy tarzı OpenAI uyumlu rotalar olarak ele alır
- yerel OpenAI'ye özgü istek şekillendirme burada uygulanmaz: `service_tier` yoktur, Responses `store` yoktur, OpenAI akıl yürütme uyumluluğu yük şekillendirmesi yoktur ve istem önbelleği ipuçları yoktur
- gizli OpenClaw atıf başlıkları (`originator`, `version`, `User-Agent`) bu özel proxy URL'lerine eklenmez

Daha katı OpenAI uyumlu arka uçlar için uyumluluk notları:

- Bazı sunucular Chat Completions üzerinde yapılandırılmış içerik bölümü dizileri değil, yalnızca string `messages[].content` kabul eder. Bu uç noktalar için `models.providers.<provider>.models[].compat.requiresStringContent: true` ayarlayın.
- Daha küçük veya daha katı bazı yerel arka uçlar, özellikle araç şemaları dahil edildiğinde, OpenClaw'un tam ajan çalışma zamanı istem şekliyle kararsız olabilir. Arka uç küçük doğrudan `/v1/chat/completions` çağrılarında çalışıyor ancak normal OpenClaw ajan turlarında başarısız oluyorsa, önce `models.providers.<provider>.models[].compat.supportsTools: false` deneyin.
- Arka uç hâlâ yalnızca daha büyük OpenClaw çalıştırmalarında başarısız oluyorsa, kalan sorun genellikle OpenClaw'un taşıma katmanı değil, üst akış model/sunucu kapasitesi veya bir arka uç hatasıdır.

## Sorun giderme

- Gateway proxy'ye ulaşabiliyor mu? `curl http://127.0.0.1:1234/v1/models`.
- LM Studio modeli kaldırılmış mı? Yeniden yükleyin; soğuk başlangıç yaygın bir “takılı kalma” nedenidir.
- Bağlam hataları mı var? `contextWindow` değerini düşürün veya sunucu sınırınızı artırın.
- OpenAI uyumlu sunucu `messages[].content ... expected a string` döndürüyor mu? Bu model girdisine `compat.requiresStringContent: true` ekleyin.
- Doğrudan küçük `/v1/chat/completions` çağrıları çalışıyor ama `openclaw infer model run` Gemma veya başka bir yerel modelde başarısız mı oluyor? Önce `compat.supportsTools: false` ile araç şemalarını devre dışı bırakın, sonra yeniden test edin. Sunucu hâlâ yalnızca daha büyük OpenClaw istemlerinde çöküyorsa, bunu üst akış sunucu/model sınırlaması olarak değerlendirin.
- Güvenlik: yerel modeller sağlayıcı tarafı filtreleri atlar; istem enjeksiyonunun etki alanını sınırlamak için ajanları dar tutun ve sıkıştırmayı açık bırakın.
