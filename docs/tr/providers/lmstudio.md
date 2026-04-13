---
read_when:
    - OpenClaw'ı LM Studio aracılığıyla açık kaynak modellerle çalıştırmak istiyorsunuz
    - LM Studio'yu kurmak ve yapılandırmak istiyorsunuz
summary: OpenClaw'ı LM Studio ile çalıştırın
title: LM Studio
x-i18n:
    generated_at: "2026-04-13T08:50:44Z"
    model: gpt-5.4
    provider: openai
    source_hash: 11264584e8277260d4215feb7c751329ce04f59e9228da1c58e147c21cd9ac2c
    source_path: providers/lmstudio.md
    workflow: 15
---

# LM Studio

LM Studio, açık ağırlıklı modelleri kendi donanımınızda çalıştırmak için kullanıcı dostu ama güçlü bir uygulamadır. `llama.cpp` (GGUF) veya MLX modellerini (Apple Silicon) çalıştırmanıza olanak tanır. GUI paketi ya da başsız daemon (`llmster`) olarak sunulur. Ürün ve kurulum belgeleri için [lmstudio.ai](https://lmstudio.ai/) adresine bakın.

## Hızlı başlangıç

1. LM Studio'yu (masaüstü) veya `llmster`'ı (başsız) kurun, ardından yerel sunucuyu başlatın:

```bash
curl -fsSL https://lmstudio.ai/install.sh | bash
```

2. Sunucuyu başlatın

Masaüstü uygulamasını başlattığınızdan ya da daemon'u aşağıdaki komutu kullanarak çalıştırdığınızdan emin olun:

```bash
lms daemon up
```

```bash
lms server start --port 1234
```

Uygulamayı kullanıyorsanız, sorunsuz bir deneyim için JIT'in etkin olduğundan emin olun. Daha fazla bilgi için [LM Studio JIT and TTL guide](https://lmstudio.ai/docs/developer/core/ttl-and-auto-evict) belgesine bakın.

3. OpenClaw, bir LM Studio token değeri gerektirir. `LM_API_TOKEN` değişkenini ayarlayın:

```bash
export LM_API_TOKEN="your-lm-studio-api-token"
```

LM Studio kimlik doğrulaması devre dışıysa, boş olmayan herhangi bir token değeri kullanın:

```bash
export LM_API_TOKEN="placeholder-key"
```

LM Studio kimlik doğrulaması kurulum ayrıntıları için [LM Studio Authentication](https://lmstudio.ai/docs/developer/core/authentication) belgesine bakın.

4. Onboarding'i çalıştırın ve `LM Studio` seçeneğini seçin:

```bash
openclaw onboard
```

5. Onboarding sırasında, LM Studio modelinizi seçmek için `Default model` istemini kullanın.

Bunu daha sonra da ayarlayabilir veya değiştirebilirsiniz:

```bash
openclaw models set lmstudio/qwen/qwen3.5-9b
```

LM Studio model anahtarları `author/model-name` biçimini izler (ör. `qwen/qwen3.5-9b`). OpenClaw
model başvuruları sağlayıcı adını başa ekler: `lmstudio/qwen/qwen3.5-9b`. Bir modelin tam anahtarını
`curl http://localhost:1234/api/v1/models` komutunu çalıştırıp `key` alanına bakarak bulabilirsiniz.

## Etkileşimsiz onboarding

Kurulumu betiklerle yapmak istediğinizde etkileşimsiz onboarding kullanın (CI, sağlama, uzak önyükleme):

```bash
openclaw onboard \
  --non-interactive \
  --accept-risk \
  --auth-choice lmstudio
```

Ya da API anahtarıyla birlikte temel URL'yi veya modeli belirtin:

```bash
openclaw onboard \
  --non-interactive \
  --accept-risk \
  --auth-choice lmstudio \
  --custom-base-url http://localhost:1234/v1 \
  --lmstudio-api-key "$LM_API_TOKEN" \
  --custom-model-id qwen/qwen3.5-9b
```

`--custom-model-id`, LM Studio tarafından döndürülen model anahtarını alır (ör. `qwen/qwen3.5-9b`);
`lmstudio/` sağlayıcı öneki olmadan.

Etkileşimsiz onboarding, `--lmstudio-api-key` gerektirir (veya ortam değişkenlerinde `LM_API_TOKEN`).
Kimlik doğrulaması olmayan LM Studio sunucularında, boş olmayan herhangi bir token değeri işe yarar.

`--custom-api-key` uyumluluk için desteklenmeye devam eder, ancak LM Studio için tercih edilen seçenek `--lmstudio-api-key`'dir.

Bu işlem `models.providers.lmstudio` yazar, varsayılan modeli
`lmstudio/<custom-model-id>` olarak ayarlar ve `lmstudio:default` kimlik doğrulama profilini yazar.

Etkileşimli kurulum, isteğe bağlı tercih edilen yükleme bağlamı uzunluğu isteyebilir ve bunu yapılandırmaya kaydettiği keşfedilen LM Studio modelleri genelinde uygular.

## Yapılandırma

### Açık yapılandırma

```json5
{
  models: {
    providers: {
      lmstudio: {
        baseUrl: "http://localhost:1234/v1",
        apiKey: "${LM_API_TOKEN}",
        api: "openai-completions",
        models: [
          {
            id: "qwen/qwen3-coder-next",
            name: "Qwen 3 Coder Next",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 128000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

## Sorun giderme

### LM Studio algılanmıyor

LM Studio'nun çalıştığından ve `LM_API_TOKEN` değişkenini ayarladığınızdan emin olun (kimlik doğrulaması olmayan sunucular için boş olmayan herhangi bir token değeri işe yarar):

```bash
# Masaüstü uygulamasıyla başlatın veya başsız olarak:
lms server start --port 1234
```

API'ye erişilebildiğini doğrulayın:

```bash
curl http://localhost:1234/api/v1/models
```

### Kimlik doğrulama hataları (HTTP 401)

Kurulum HTTP 401 bildiriyorsa, API anahtarınızı doğrulayın:

- `LM_API_TOKEN` değerinin LM Studio'da yapılandırılan anahtarla eşleştiğini kontrol edin.
- LM Studio kimlik doğrulaması kurulum ayrıntıları için [LM Studio Authentication](https://lmstudio.ai/docs/developer/core/authentication) belgesine bakın.
- Sunucunuz kimlik doğrulaması gerektirmiyorsa, `LM_API_TOKEN` için boş olmayan herhangi bir token değeri kullanın.

### Tam zamanında model yükleme

LM Studio, modellerin ilk istekte yüklendiği tam zamanında (JIT) model yüklemeyi destekler. `Model not loaded` hatalarından kaçınmak için bunun etkin olduğundan emin olun.
