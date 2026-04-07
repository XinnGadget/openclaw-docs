---
read_when:
    - OpenClaw içinde Mistral modellerini kullanmak istiyorsanız
    - Mistral API anahtarı onboarding'i ve model başvurularına ihtiyacınız varsa
summary: OpenClaw ile Mistral modellerini ve Voxtral transkripsiyonunu kullanın
title: Mistral
x-i18n:
    generated_at: "2026-04-07T08:48:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4e32a0eb2a37dba6383ba338b06a8d0be600e7443aa916225794ccb0fdf46aee
    source_path: providers/mistral.md
    workflow: 15
---

# Mistral

OpenClaw, hem metin/görüntü model yönlendirmesi (`mistral/...`) hem de
media understanding içinde Voxtral üzerinden ses transkripsiyonu için Mistral'ı destekler.
Mistral, bellek gömmeleri için de kullanılabilir (`memorySearch.provider = "mistral"`).

## CLI kurulumu

```bash
openclaw onboard --auth-choice mistral-api-key
# veya etkileşimsiz
openclaw onboard --mistral-api-key "$MISTRAL_API_KEY"
```

## Yapılandırma örneği (LLM provider)

```json5
{
  env: { MISTRAL_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "mistral/mistral-large-latest" } } },
}
```

## Yerleşik LLM kataloğu

OpenClaw şu anda şu paketlenmiş Mistral kataloğunu sunar:

| Model başvurusu                  | Girdi       | Bağlam  | Maks. çıktı | Notlar                                                           |
| -------------------------------- | ----------- | ------- | ----------- | ---------------------------------------------------------------- |
| `mistral/mistral-large-latest`   | metin, görüntü | 262,144 | 16,384      | Varsayılan model                                                 |
| `mistral/mistral-medium-2508`    | metin, görüntü | 262,144 | 8,192       | Mistral Medium 3.1                                               |
| `mistral/mistral-small-latest`   | metin, görüntü | 128,000 | 16,384      | Mistral Small 4; API `reasoning_effort` ile ayarlanabilir akıl yürütme |
| `mistral/pixtral-large-latest`   | metin, görüntü | 128,000 | 32,768      | Pixtral                                                          |
| `mistral/codestral-latest`       | metin       | 256,000 | 4,096       | Kodlama                                                          |
| `mistral/devstral-medium-latest` | metin       | 262,144 | 32,768      | Devstral 2                                                       |
| `mistral/magistral-small`        | metin       | 128,000 | 40,000      | Akıl yürütme etkin                                               |

## Yapılandırma örneği (Voxtral ile ses transkripsiyonu)

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        models: [{ provider: "mistral", model: "voxtral-mini-latest" }],
      },
    },
  },
}
```

## Ayarlanabilir akıl yürütme (`mistral-small-latest`)

`mistral/mistral-small-latest`, Mistral Small 4'e eşlenir ve Chat Completions API üzerinde `reasoning_effort` aracılığıyla [ayarlanabilir akıl yürütmeyi](https://docs.mistral.ai/capabilities/reasoning/adjustable) destekler (`none`, çıktıda ek düşünmeyi en aza indirir; `high`, son yanıttan önce tam düşünme izlerini gösterir).

OpenClaw, oturum **thinking** düzeyini Mistral API'sine şöyle eşler:

- **off** / **minimal** → `none`
- **low** / **medium** / **high** / **xhigh** / **adaptive** → `high`

Diğer paketlenmiş Mistral katalog modelleri bu parametreyi kullanmaz; Mistral'ın yerel olarak akıl yürütme öncelikli davranışını istediğinizde `magistral-*` modellerini kullanmaya devam edin.

## Notlar

- Mistral kimlik doğrulaması `MISTRAL_API_KEY` kullanır.
- Provider temel URL'si varsayılan olarak `https://api.mistral.ai/v1` değeridir.
- Onboarding varsayılan modeli `mistral/mistral-large-latest` değeridir.
- Mistral için media-understanding varsayılan ses modeli `voxtral-mini-latest` değeridir.
- Medya transkripsiyon yolu `/v1/audio/transcriptions` kullanır.
- Bellek gömmeleri yolu `/v1/embeddings` kullanır (varsayılan model: `mistral-embed`).
