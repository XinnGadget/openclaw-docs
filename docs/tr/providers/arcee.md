---
read_when:
    - Arcee AI'ı OpenClaw ile kullanmak istiyorsunuz
    - API anahtarı env değişkenine veya CLI kimlik doğrulama seçimine ihtiyacınız var
summary: Arcee AI kurulumu (kimlik doğrulama + model seçimi)
title: Arcee AI
x-i18n:
    generated_at: "2026-04-07T08:48:20Z"
    model: gpt-5.4
    provider: openai
    source_hash: fb04909a708fec08dd2c8c863501b178f098bc4818eaebad38aea264157969d8
    source_path: providers/arcee.md
    workflow: 15
---

# Arcee AI

[Arcee AI](https://arcee.ai), OpenAI uyumlu bir API üzerinden Trinity karışım-uzman modelleri ailesine erişim sağlar. Tüm Trinity modelleri Apache 2.0 lisanslıdır.

Arcee AI modellerine doğrudan Arcee platformu üzerinden veya [OpenRouter](/tr/providers/openrouter) aracılığıyla erişilebilir.

- Sağlayıcı: `arcee`
- Kimlik doğrulama: `ARCEEAI_API_KEY` (doğrudan) veya `OPENROUTER_API_KEY` (OpenRouter üzerinden)
- API: OpenAI uyumlu
- Temel URL: `https://api.arcee.ai/api/v1` (doğrudan) veya `https://openrouter.ai/api/v1` (OpenRouter)

## Hızlı başlangıç

1. [Arcee AI](https://chat.arcee.ai/) veya [OpenRouter](https://openrouter.ai/keys) üzerinden bir API anahtarı alın.

2. API anahtarını ayarlayın (önerilen: Gateway için saklayın):

```bash
# Doğrudan (Arcee platformu)
openclaw onboard --auth-choice arceeai-api-key

# OpenRouter üzerinden
openclaw onboard --auth-choice arceeai-openrouter
```

3. Varsayılan bir model ayarlayın:

```json5
{
  agents: {
    defaults: {
      model: { primary: "arcee/trinity-large-thinking" },
    },
  },
}
```

## Etkileşimsiz örnek

```bash
# Doğrudan (Arcee platformu)
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice arceeai-api-key \
  --arceeai-api-key "$ARCEEAI_API_KEY"

# OpenRouter üzerinden
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice arceeai-openrouter \
  --openrouter-api-key "$OPENROUTER_API_KEY"
```

## Ortam notu

Gateway bir daemon olarak çalışıyorsa (launchd/systemd), `ARCEEAI_API_KEY`
(veya `OPENROUTER_API_KEY`) değerinin bu süreç için kullanılabilir olduğundan emin olun (örneğin
`~/.openclaw/.env` içinde veya `env.shellEnv` aracılığıyla).

## Yerleşik katalog

OpenClaw şu anda bu paketlenmiş Arcee kataloğunu gönderir:

| Model ref                      | Adı                    | Girdi | Bağlam | Maliyet (1M başına giriş/çıkış) | Notlar                                    |
| ------------------------------ | ---------------------- | ----- | ------ | -------------------------------- | ----------------------------------------- |
| `arcee/trinity-large-thinking` | Trinity Large Thinking | text  | 256K   | $0.25 / $0.90                    | Varsayılan model; akıl yürütme etkin      |
| `arcee/trinity-large-preview`  | Trinity Large Preview  | text  | 128K   | $0.25 / $1.00                    | Genel amaçlı; 400B parametre, 13B etkin   |
| `arcee/trinity-mini`           | Trinity Mini 26B       | text  | 128K   | $0.045 / $0.15                   | Hızlı ve maliyet verimli; function calling |

Aynı model ref'leri hem doğrudan hem de OpenRouter kurulumlarında çalışır (örneğin `arcee/trinity-large-thinking`).

Onboarding hazır ayarı, varsayılan model olarak `arcee/trinity-large-thinking` ayarlar.

## Desteklenen özellikler

- Akış
- Araç kullanımı / function calling
- Yapılandırılmış çıktı (JSON modu ve JSON şeması)
- Genişletilmiş düşünme (Trinity Large Thinking)
