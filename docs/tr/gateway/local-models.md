---
read_when:
    - Modelleri kendi GPU makinenizden sunmak istiyorsunuz
    - LM Studio'yu veya OpenAI uyumlu bir proxy'yi yapılandırıyorsunuz
    - En güvenli yerel model yönlendirmesine ihtiyacınız var
summary: OpenClaw'ı yerel LLM'lerde çalıştırın (LM Studio, vLLM, LiteLLM, özel OpenAI uç noktaları)
title: Yerel Modeller
x-i18n:
    generated_at: "2026-04-15T14:40:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7a506ff83e4c2870d3878339f646c906584454a156ecd618c360f592cf3b0011
    source_path: gateway/local-models.md
    workflow: 15
---

# Yerel modeller

Yerel kullanım mümkün, ancak OpenClaw büyük bağlam + istem enjeksiyonuna karşı güçlü savunmalar bekler. Küçük kartlar bağlamı kısaltır ve güvenliği zayıflatır. Hedefi yüksek tutun: **en az 2 tam donanımlı Mac Studio veya eşdeğer GPU sistemi (~30 bin $+)**. Tek bir **24 GB** GPU yalnızca daha hafif istemlerde ve daha yüksek gecikmeyle çalışır. Çalıştırabildiğiniz **en büyük / tam boyutlu model varyantını kullanın**; agresif şekilde kuantize edilmiş veya “küçük” checkpoint'ler istem enjeksiyonu riskini artırır (bkz. [Güvenlik](/tr/gateway/security)).

En az sürtünmeli yerel kurulum istiyorsanız, [LM Studio](/tr/providers/lmstudio) veya [Ollama](/tr/providers/ollama) ile başlayın ve `openclaw onboard` çalıştırın. Bu sayfa, daha üst düzey yerel yığınlar ve özel OpenAI uyumlu yerel sunucular için görüş odaklı kılavuzdur.

## Önerilen: LM Studio + büyük yerel model (Responses API)

Şu anda en iyi yerel yığın. LM Studio'da büyük bir model yükleyin (örneğin tam boyutlu bir Qwen, DeepSeek veya Llama derlemesi), yerel sunucuyu etkinleştirin (varsayılan `http://127.0.0.1:1234`) ve akıl yürütmeyi nihai metinden ayrı tutmak için Responses API kullanın.

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
- LM Studio'da, **mevcut en büyük model derlemesini** indirin (“small”/yoğun şekilde kuantize edilmiş varyantlardan kaçının), sunucuyu başlatın, `http://127.0.0.1:1234/v1/models` çıktısında listelendiğini doğrulayın.
- `my-local-model` değerini, LM Studio'da görünen gerçek model kimliğiyle değiştirin.
- Modeli yüklü tutun; soğuk yükleme başlangıç gecikmesi ekler.
- LM Studio derlemeniz farklıysa `contextWindow`/`maxTokens` değerlerini ayarlayın.
- WhatsApp için yalnızca nihai metnin gönderilmesi amacıyla Responses API kullanın.

Yerelde çalışırken bile barındırılan modelleri yapılandırılmış halde tutun; yedekler kullanılabilir kalsın diye `models.mode: "merge"` kullanın.

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

Birincil ve yedek sırasını değiştirin; yerel makine kapalıyken Sonnet veya Opus'a geri dönebilmek için aynı provider bloğunu ve `models.mode: "merge"` ayarını koruyun.

### Bölgesel barındırma / veri yönlendirme

- Barındırılan MiniMax/Kimi/GLM varyantları OpenRouter üzerinde de bölgeye sabitlenmiş uç noktalarla bulunur (ör. ABD'de barındırılan). Trafiği seçtiğiniz yargı alanında tutarken Anthropic/OpenAI yedeklerini kullanmaya devam etmek için oradaki bölgesel varyantı seçin ve yine `models.mode: "merge"` kullanın.
- Yalnızca yerel kullanım en güçlü gizlilik yoludur; provider özelliklerine ihtiyaç duyup veri akışı üzerinde kontrol istediğinizde barındırılan bölgesel yönlendirme orta yoldur.

## Diğer OpenAI uyumlu yerel proxy'ler

vLLM, LiteLLM, OAI-proxy veya özel Gateway'ler, OpenAI tarzı bir `/v1` uç noktası sundukları sürece çalışır. Yukarıdaki provider bloğunu kendi uç noktanız ve model kimliğinizle değiştirin:

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

Barındırılan modeller yedek olarak kullanılabilir kalsın diye `models.mode: "merge"` kullanın.

Yerel/proxy'lenmiş `/v1` arka uçları için davranış notu:

- OpenClaw bunları yerel OpenAI uç noktaları değil, proxy tarzı OpenAI uyumlu rotalar olarak ele alır
- buraya yerel OpenAI'ye özgü istek şekillendirmesi uygulanmaz: `service_tier` yok, Responses `store` yok, OpenAI akıl yürütme uyumluluğu yük şekillendirmesi yok ve istem önbelleği ipuçları yok
- gizli OpenClaw ilişkilendirme üstbilgileri (`originator`, `version`, `User-Agent`) bu özel proxy URL'lerine eklenmez

Daha katı OpenAI uyumlu arka uçlar için uyumluluk notları:

- Bazı sunucular Chat Completions içinde yapılandırılmış içerik bölümü dizileri yerine yalnızca dize `messages[].content` kabul eder. Bu uç noktalar için `models.providers.<provider>.models[].compat.requiresStringContent: true` ayarlayın.
- Daha küçük veya daha katı bazı yerel arka uçlar, özellikle araç şemaları dahil edildiğinde, OpenClaw'ın tam agent-runtime istem biçimiyle kararsız çalışır. Arka uç küçük doğrudan `/v1/chat/completions` çağrılarında çalışıyor ama normal OpenClaw agent dönüşlerinde başarısız oluyorsa, önce `browser`, `cron` ve `message` gibi ağır varsayılan araçları kaldırmak için `agents.defaults.experimental.localModelLean: true` deneyin; bu deneysel bir işarettir, kararlı varsayılan mod ayarı değildir. Bkz. [Deneysel Özellikler](/tr/concepts/experimental-features). Bu da işe yaramazsa `models.providers.<provider>.models[].compat.supportsTools: false` deneyin.
- Arka uç yine yalnızca daha büyük OpenClaw çalıştırmalarında başarısız oluyorsa, kalan sorun genellikle OpenClaw'ın taşıma katmanı değil, yukarı akış model/sunucu kapasitesi veya bir arka uç hatasıdır.

## Sorun giderme

- Gateway proxy'ye ulaşabiliyor mu? `curl http://127.0.0.1:1234/v1/models`.
- LM Studio modeli yükten çıkarılmış mı? Yeniden yükleyin; soğuk başlangıç yaygın bir “takılma” nedenidir.
- OpenClaw, algılanan bağlam penceresi **32k**'nin altındaysa uyarır ve **16k**'nin altında engeller. Bu ön kontrolde takılırsanız, sunucu/model bağlam sınırını yükseltin veya daha büyük bir model seçin.
- Bağlam hataları mı alıyorsunuz? `contextWindow` değerini düşürün veya sunucu sınırınızı yükseltin.
- OpenAI uyumlu sunucu `messages[].content ... expected a string` döndürüyor mu? O model girdisine `compat.requiresStringContent: true` ekleyin.
- Doğrudan küçük `/v1/chat/completions` çağrıları çalışıyor ama `openclaw infer model run` Gemma'da veya başka bir yerel modelde başarısız mı oluyor? Önce `compat.supportsTools: false` ile araç şemalarını devre dışı bırakın, sonra yeniden test edin. Sunucu yine yalnızca daha büyük OpenClaw istemlerinde çöküyorsa, bunu yukarı akış sunucu/model sınırlaması olarak değerlendirin.
- Güvenlik: yerel modeller provider tarafı filtreleri atlar; istem enjeksiyonu etki alanını sınırlamak için agent'ları dar tutun ve Compaction açık olsun.
