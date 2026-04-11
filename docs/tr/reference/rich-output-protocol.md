---
x-i18n:
    generated_at: "2026-04-11T15:15:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2a8884fc2c304bf96d4675f0c1d1ff781d6dc1ae8c49d92ce08040c9c7709035
    source_path: reference/rich-output-protocol.md
    workflow: 15
---

# Zengin Çıktı Protokolü

Asistan çıktısı küçük bir teslim/render yönergesi kümesi taşıyabilir:

- Ek teslimi için `MEDIA:`
- Sesli sunum ipuçları için `[[audio_as_voice]]`
- Yanıt meta verisi için `[[reply_to_current]]` / `[[reply_to:<id>]]`
- Control UI zengin render için `[embed ...]`

Bu yönergeler ayrıdır. `MEDIA:` ve reply/voice etiketleri teslim meta verisi olarak kalır; `[embed ...]` ise yalnızca web için zengin render yoludur.

## `[embed ...]`

`[embed ...]`, Control UI için etkene yönelik tek zengin render söz dizimidir.

Kendiliğinden kapanan örnek:

```text
[embed ref="cv_123" title="Durum" /]
```

Kurallar:

- `[view ...]` artık yeni çıktı için geçerli değildir.
- Embed kısa kodları yalnızca asistan mesaj yüzeyinde render edilir.
- Yalnızca URL destekli embed'ler render edilir. `ref="..."` veya `url="..."` kullanın.
- Blok biçimli satır içi HTML embed kısa kodları render edilmez.
- Web UI kısa kodu görünür metinden ayıklar ve embed'i satır içinde render eder.
- `MEDIA:` bir embed takma adı değildir ve zengin embed render için kullanılmamalıdır.

## Saklanan Render Biçimi

Normalleştirilmiş/saklanan asistan içerik bloğu, yapılandırılmış bir `canvas` öğesidir:

```json
{
  "type": "canvas",
  "preview": {
    "kind": "canvas",
    "surface": "assistant_message",
    "render": "url",
    "viewId": "cv_123",
    "url": "/__openclaw__/canvas/documents/cv_123/index.html",
    "title": "Status",
    "preferredHeight": 320
  }
}
```

Saklanan/render edilen zengin bloklar bu `canvas` biçimini doğrudan kullanır. `present_view` tanınmaz.
