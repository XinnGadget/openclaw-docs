---
read_when:
    - Aracı üzerinden görsel üretme
    - Görsel üretimi sağlayıcılarını ve modellerini yapılandırma
    - '`image_generate` aracı parametrelerini anlama'
summary: Yapılandırılmış sağlayıcıları kullanarak görseller oluşturun ve düzenleyin (OpenAI, Google Gemini, fal, MiniMax, ComfyUI, Vydra)
title: Görsel Üretimi
x-i18n:
    generated_at: "2026-04-06T03:13:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: dde416dd1441a06605db85b5813cf61ccfc525813d6db430b7b7dfa53d6a3134
    source_path: tools/image-generation.md
    workflow: 15
---

# Görsel Üretimi

`image_generate` aracı, aracının yapılandırılmış sağlayıcılarınızı kullanarak görseller oluşturmasına ve düzenlemesine olanak tanır. Oluşturulan görseller, aracının yanıtında otomatik olarak medya ekleri olarak teslim edilir.

<Note>
Araç yalnızca en az bir görsel üretimi sağlayıcısı mevcut olduğunda görünür. Aracınızın araçlarında `image_generate` görmüyorsanız `agents.defaults.imageGenerationModel` yapılandırın veya bir sağlayıcı API anahtarı ayarlayın.
</Note>

## Hızlı başlangıç

1. En az bir sağlayıcı için bir API anahtarı ayarlayın (örneğin `OPENAI_API_KEY` veya `GEMINI_API_KEY`).
2. İsteğe bağlı olarak tercih ettiğiniz modeli ayarlayın:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "openai/gpt-image-1",
      },
    },
  },
}
```

3. Aracıya şunu sorun: _"Dost canlısı bir ıstakoz maskotunun görselini oluştur."_

Aracı `image_generate` aracını otomatik olarak çağırır. Araç izin listesine eklemeye gerek yoktur — bir sağlayıcı mevcut olduğunda varsayılan olarak etkindir.

## Desteklenen sağlayıcılar

| Sağlayıcı | Varsayılan model               | Düzenleme desteği                  | API anahtarı                                          |
| --------- | ------------------------------ | ---------------------------------- | ----------------------------------------------------- |
| OpenAI    | `gpt-image-1`                  | Evet (en fazla 5 görsel)           | `OPENAI_API_KEY`                                      |
| Google    | `gemini-3.1-flash-image-preview` | Evet                             | `GEMINI_API_KEY` veya `GOOGLE_API_KEY`                |
| fal       | `fal-ai/flux/dev`              | Evet                               | `FAL_KEY`                                             |
| MiniMax   | `image-01`                     | Evet (özne referansı)              | `MINIMAX_API_KEY` veya MiniMax OAuth (`minimax-portal`) |
| ComfyUI   | `workflow`                     | Evet (1 görsel, iş akışı yapılandırmalı) | Bulut için `COMFY_API_KEY` veya `COMFY_CLOUD_API_KEY` |
| Vydra     | `grok-imagine`                 | Hayır                              | `VYDRA_API_KEY`                                       |

Çalışma zamanında mevcut sağlayıcıları ve modelleri incelemek için `action: "list"` kullanın:

```
/tool image_generate action=list
```

## Araç parametreleri

| Parametre    | Tür      | Açıklama                                                                            |
| ------------ | -------- | ----------------------------------------------------------------------------------- |
| `prompt`     | string   | Görsel üretimi promptu (`action: "generate"` için gereklidir)                       |
| `action`     | string   | Sağlayıcıları incelemek için `"generate"` (varsayılan) veya `"list"`                |
| `model`      | string   | Sağlayıcı/model geçersiz kılması, örn. `openai/gpt-image-1`                         |
| `image`      | string   | Düzenleme kipi için tek referans görsel yolu veya URL'si                            |
| `images`     | string[] | Düzenleme kipi için birden çok referans görsel (en fazla 5)                         |
| `size`       | string   | Boyut ipucu: `1024x1024`, `1536x1024`, `1024x1536`, `1024x1792`, `1792x1024`        |
| `aspectRatio` | string  | En-boy oranı: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` |
| `resolution` | string   | Çözünürlük ipucu: `1K`, `2K` veya `4K`                                              |
| `count`      | number   | Oluşturulacak görsel sayısı (1–4)                                                   |
| `filename`   | string   | Çıktı dosya adı ipucu                                                               |

Tüm sağlayıcılar tüm parametreleri desteklemez. Araç, her sağlayıcının desteklediğini geçirir, geri kalanını yok sayar ve düşürülen geçersiz kılmaları araç sonucunda bildirir.

## Yapılandırma

### Model seçimi

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "openai/gpt-image-1",
        fallbacks: ["google/gemini-3.1-flash-image-preview", "fal/fal-ai/flux/dev"],
      },
    },
  },
}
```

### Sağlayıcı seçim sırası

Bir görsel oluşturulurken OpenClaw, sağlayıcıları şu sırayla dener:

1. Araç çağrısından gelen **`model` parametresi** (aracı bir model belirtirse)
2. Yapılandırmadan gelen **`imageGenerationModel.primary`**
3. Sırayla **`imageGenerationModel.fallbacks`**
4. **Otomatik algılama** — yalnızca kimlik doğrulama destekli sağlayıcı varsayılanlarını kullanır:
   - önce geçerli varsayılan sağlayıcı
   - ardından sağlayıcı kimliği sırasına göre kalan kayıtlı görsel üretimi sağlayıcıları

Bir sağlayıcı başarısız olursa (kimlik doğrulama hatası, hız sınırı vb.), bir sonraki aday otomatik olarak denenir. Hepsi başarısız olursa hata her denemedeki ayrıntıları içerir.

Notlar:

- Otomatik algılama kimlik doğrulama farkındadır. Bir sağlayıcı varsayılanı, yalnızca
  OpenClaw bu sağlayıcı için gerçekten kimlik doğrulaması yapabiliyorsa aday listesine girer.
- Şu anda kayıtlı sağlayıcıları, bunların
  varsayılan modellerini ve kimlik doğrulama ortam değişkeni ipuçlarını incelemek için `action: "list"` kullanın.

### Görsel düzenleme

OpenAI, Google, fal, MiniMax ve ComfyUI referans görsellerin düzenlenmesini destekler. Bir referans görsel yolu veya URL'si geçin:

```
"Bu fotoğrafın suluboya sürümünü oluştur" + image: "/path/to/photo.jpg"
```

OpenAI ve Google, `images` parametresi aracılığıyla en fazla 5 referans görseli destekler. fal, MiniMax ve ComfyUI 1 görsel destekler.

MiniMax görsel üretimi, her iki paketlenmiş MiniMax kimlik doğrulama yolu üzerinden kullanılabilir:

- API anahtarlı kurulumlar için `minimax/image-01`
- OAuth kurulumları için `minimax-portal/image-01`

## Sağlayıcı yetenekleri

| Yetenek               | OpenAI              | Google               | fal                  | MiniMax                    | ComfyUI                            | Vydra |
| --------------------- | ------------------- | -------------------- | -------------------- | -------------------------- | ---------------------------------- | ----- |
| Üretme                | Evet (en fazla 4)   | Evet (en fazla 4)    | Evet (en fazla 4)    | Evet (en fazla 9)          | Evet (iş akışı tanımlı çıktılar)   | Evet (1) |
| Düzenleme/referans    | Evet (en fazla 5 görsel) | Evet (en fazla 5 görsel) | Evet (1 görsel) | Evet (1 görsel, özne ref) | Evet (1 görsel, iş akışı yapılandırmalı) | Hayır |
| Boyut denetimi        | Evet                | Evet                 | Evet                 | Hayır                      | Hayır                              | Hayır |
| En-boy oranı          | Hayır               | Evet                 | Evet (yalnızca üretme) | Evet                     | Hayır                              | Hayır |
| Çözünürlük (1K/2K/4K) | Hayır               | Evet                 | Evet                 | Hayır                      | Hayır                              | Hayır |

## İlgili

- [Araçlara Genel Bakış](/tr/tools) — mevcut tüm aracı araçları
- [fal](/providers/fal) — fal görsel ve video sağlayıcısı kurulumu
- [ComfyUI](/providers/comfy) — yerel ComfyUI ve Comfy Cloud iş akışı kurulumu
- [Google (Gemini)](/tr/providers/google) — Gemini görsel sağlayıcısı kurulumu
- [MiniMax](/tr/providers/minimax) — MiniMax görsel sağlayıcısı kurulumu
- [OpenAI](/tr/providers/openai) — OpenAI Images sağlayıcısı kurulumu
- [Vydra](/providers/vydra) — Vydra görsel, video ve konuşma kurulumu
- [Yapılandırma Başvurusu](/tr/gateway/configuration-reference#agent-defaults) — `imageGenerationModel` yapılandırması
- [Models](/tr/concepts/models) — model yapılandırması ve geri dönüş
