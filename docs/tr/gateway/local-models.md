---
read_when:
    - Modelleri kendi GPU makinenizden sunmak istiyorsunuz
    - LM Studio’yu veya OpenAI uyumlu bir proxy’yi yapılandırıyorsunuz
    - En güvenli yerel model yönlendirmesine ihtiyacınız var
summary: OpenClaw'ı yerel LLM'lerde çalıştırın (LM Studio, vLLM, LiteLLM, özel OpenAI uç noktaları)
title: Yerel Modeller
x-i18n:
    generated_at: "2026-04-13T08:50:44Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3ecb61b3e6e34d3666f9b688cd694d92c5fb211cf8c420fa876f7ccf5789154a
    source_path: gateway/local-models.md
    workflow: 15
---

# Yerel modeller

Yerel kullanım mümkündür, ancak OpenClaw büyük bağlam ve prompt injection’a karşı güçlü savunmalar bekler. Küçük kartlar bağlamı kırpar ve güvenliği zayıflatır. Hedefinizi yüksek tutun: **en az 2 tam donanımlı Mac Studio veya eşdeğer GPU sistemi (~30 bin $+)**. Tek bir **24 GB** GPU, yalnızca daha hafif prompt’larda ve daha yüksek gecikmeyle çalışır. Çalıştırabildiğiniz **en büyük / tam boyutlu model varyantını kullanın**; agresif biçimde kuantize edilmiş veya “small” checkpoint’ler prompt injection riskini artırır (bkz. [Güvenlik](/tr/gateway/security)).

En düşük sürtünmeli yerel kurulum istiyorsanız, [LM Studio](/tr/providers/lmstudio) veya [Ollama](/tr/providers/ollama) ile başlayın ve `openclaw onboard` kullanın. Bu sayfa, daha üst seviye yerel yığınlar ve özel OpenAI uyumlu yerel sunucular için görüş odaklı rehberdir.

## Önerilen: LM Studio + büyük yerel model (Responses API)

Şu anda en iyi yerel yığın. LM Studio’da büyük bir model yükleyin (örneğin tam boyutlu bir Qwen, DeepSeek veya Llama derlemesi), yerel sunucuyu etkinleştirin (varsayılan `http://127.0.0.1:1234`) ve akıl yürütmeyi nihai metinden ayrı tutmak için Responses API kullanın.

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

**Kurulum denetim listesi**

- LM Studio’yu kurun: [https://lmstudio.ai](https://lmstudio.ai)
- LM Studio’da, **mevcut en büyük model derlemesini** indirin (“small”/ağır kuantize edilmiş varyantlardan kaçının), sunucuyu başlatın ve `http://127.0.0.1:1234/v1/models` çıktısında listelendiğini doğrulayın.
- `my-local-model` değerini LM Studio’da gösterilen gerçek model kimliğiyle değiştirin.
- Modeli yüklü tutun; soğuk yükleme başlangıç gecikmesi ekler.
- LM Studio derlemeniz farklıysa `contextWindow`/`maxTokens` değerlerini ayarlayın.
- WhatsApp için yalnızca nihai metnin gönderilmesi amacıyla Responses API kullanın.

Yerelde çalıştırıyor olsanız bile barındırılan modelleri yapılandırılmış tutun; geri dönüşlerin kullanılabilir kalması için `models.mode: "merge"` kullanın.

### Hibrit yapılandırma: barındırılan birincil, yerel geri dönüş

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

### Yerel öncelikli, barındırılan güvenlik ağıyla

Birincil ve geri dönüş sırasını değiştirin; yerel makine devre dışı kaldığında Sonnet veya Opus’a geri dönebilmek için aynı sağlayıcı bloğunu ve `models.mode: "merge"` ayarını koruyun.

### Bölgesel barındırma / veri yönlendirme

- Barındırılan MiniMax/Kimi/GLM varyantları, bölgeye sabitlenmiş uç noktalarla OpenRouter üzerinde de bulunur (ör. ABD’de barındırılan). Trafiği seçtiğiniz yargı alanında tutmak için oradaki bölgesel varyantı seçin; yine de Anthropic/OpenAI geri dönüşleri için `models.mode: "merge"` kullanın.
- Yalnızca yerel kullanım en güçlü gizlilik yoludur; sağlayıcı özelliklerine ihtiyaç duyuyor ama veri akışı üzerinde kontrol istiyorsanız, barındırılan bölgesel yönlendirme orta yoldur.

## Diğer OpenAI uyumlu yerel proxy’ler

vLLM, LiteLLM, OAI-proxy veya özel gateway’ler, OpenAI tarzı bir `/v1` uç noktası sunuyorlarsa çalışır. Yukarıdaki sağlayıcı bloğunu kendi uç noktanız ve model kimliğinizle değiştirin:

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

Barındırılan modellerin geri dönüş olarak kullanılabilir kalması için `models.mode: "merge"` ayarını koruyun.

Yerel/proxy’lenmiş `/v1` arka uçları için davranış notu:

- OpenClaw bunları yerel OpenAI uç noktaları değil, proxy tarzı OpenAI uyumlu yollar olarak ele alır
- yalnızca yerel OpenAI’ye özgü istek şekillendirme burada uygulanmaz: `service_tier` yoktur, Responses `store` yoktur, OpenAI reasoning uyumluluk payload şekillendirmesi yoktur ve prompt önbelleği ipuçları yoktur
- gizli OpenClaw ilişkilendirme başlıkları (`originator`, `version`, `User-Agent`) bu özel proxy URL’lerine eklenmez

Daha katı OpenAI uyumlu arka uçlar için uyumluluk notları:

- Bazı sunucular, Chat Completions içinde yapılandırılmış içerik-parça dizileri yerine yalnızca string `messages[].content` kabul eder. Bu tür uç noktalar için `models.providers.<provider>.models[].compat.requiresStringContent: true` ayarını yapın.
- Bazı daha küçük veya daha katı yerel arka uçlar, özellikle araç şemaları dahil edildiğinde OpenClaw’ın tam agent-runtime prompt biçimiyle kararsız çalışır. Arka uç küçük doğrudan `/v1/chat/completions` çağrılarında çalışıyor ama normal OpenClaw agent dönüşlerinde başarısız oluyorsa, önce `models.providers.<provider>.models[].compat.supportsTools: false` deneyin.
- Arka uç yalnızca daha büyük OpenClaw çalıştırmalarında hâlâ başarısız oluyorsa, kalan sorun genellikle OpenClaw’ın taşıma katmanı değil, yukarı akış model/sunucu kapasitesi veya bir arka uç hatasıdır.

## Sorun giderme

- Gateway proxy’ye ulaşabiliyor mu? `curl http://127.0.0.1:1234/v1/models`.
- LM Studio modeli yükten mi düştü? Yeniden yükleyin; soğuk başlangıç, yaygın bir “takılı kalma” nedenidir.
- Bağlam hataları mı alıyorsunuz? `contextWindow` değerini düşürün veya sunucu sınırınızı yükseltin.
- OpenAI uyumlu sunucu `messages[].content ... expected a string` mı döndürüyor? O model girdisine `compat.requiresStringContent: true` ekleyin.
- Doğrudan küçük `/v1/chat/completions` çağrıları çalışıyor ama `openclaw infer model run` Gemma veya başka bir yerel modelde başarısız mı oluyor? Önce `compat.supportsTools: false` ile araç şemalarını devre dışı bırakın, sonra yeniden test edin. Sunucu yine yalnızca daha büyük OpenClaw prompt’larında çöküyorsa, bunu yukarı akış sunucu/model sınırlaması olarak değerlendirin.
- Güvenlik: yerel modeller sağlayıcı tarafı filtreleri atlar; prompt injection etki alanını sınırlamak için agent’ları dar kapsamlı tutun ve Compaction özelliğini açık bırakın.
