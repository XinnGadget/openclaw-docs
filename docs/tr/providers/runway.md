---
read_when:
    - OpenClaw içinde Runway video oluşturmayı kullanmak istiyorsunuz
    - Runway API anahtarı/env kurulumuna ihtiyacınız var
    - Runway’i varsayılan video provider’ı yapmak istiyorsunuz
summary: OpenClaw içinde Runway video oluşturma kurulumu
title: Runway
x-i18n:
    generated_at: "2026-04-06T03:11:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: bc615d1a26f7a4b890d29461e756690c858ecb05024cf3c4d508218022da6e76
    source_path: providers/runway.md
    workflow: 15
---

# Runway

OpenClaw, barındırılan video oluşturma için paketlenmiş bir `runway` provider ile gelir.

- Provider kimliği: `runway`
- Auth: `RUNWAYML_API_SECRET` (kanonik) veya `RUNWAY_API_KEY`
- API: Runway görev tabanlı video oluşturma (`GET /v1/tasks/{id}` polling)

## Hızlı başlangıç

1. API anahtarını ayarlayın:

```bash
openclaw onboard --auth-choice runway-api-key
```

2. Runway’i varsayılan video provider’ı olarak ayarlayın:

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "runway/gen4.5"
```

3. Agent’tan video oluşturmasını isteyin. Runway otomatik olarak kullanılacaktır.

## Desteklenen kipler

| Kip            | Model              | Referans girdi          |
| -------------- | ------------------ | ----------------------- |
| Metinden videoya  | `gen4.5` (varsayılan) | Yok                  |
| Görselden videoya | `gen4.5`           | 1 yerel veya uzak görsel |
| Videodan videoya  | `gen4_aleph`       | 1 yerel veya uzak video  |

- Veri URI’leri aracılığıyla yerel görsel ve video referansları desteklenir.
- Videodan videoya şu anda özellikle `runway/gen4_aleph` gerektirir.
- Yalnızca metin içeren çalıştırmalar şu anda `16:9` ve `9:16` en-boy oranlarını sunar.

## Yapılandırma

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "runway/gen4.5",
      },
    },
  },
}
```

## İlgili

- [Video Generation](/tools/video-generation) -- paylaşılan araç parametreleri, provider seçimi ve eşzamansız davranış
- [Configuration Reference](/tr/gateway/configuration-reference#agent-defaults)
