---
read_when:
    - Aracı üzerinden görsel oluşturma
    - Görsel oluşturma sağlayıcılarını ve modellerini yapılandırma
    - '`image_generate` aracının parametrelerini anlama'
summary: Yapılandırılmış sağlayıcıları (OpenAI, Google Gemini, fal, MiniMax, ComfyUI, Vydra) kullanarak görseller oluşturun ve düzenleyin
title: Görsel Oluşturma
x-i18n:
    generated_at: "2026-04-06T08:49:06Z"
    model: gpt-5.4
    provider: openai
    source_hash: 903cc522c283a8da2cbd449ae3e25f349a74d00ecfdaf0f323fd8aa3f2107aea
    source_path: tools/image-generation.md
    workflow: 15
---

# Görsel Oluşturma

`image_generate` aracı, aracının yapılandırdığınız sağlayıcıları kullanarak görseller oluşturmasına ve düzenlemesine olanak tanır. Oluşturulan görseller, aracının yanıtında medya eki olarak otomatik şekilde teslim edilir.

<Note>
Araç yalnızca en az bir görsel oluşturma sağlayıcısı kullanılabilir olduğunda görünür. Aracınızın araçlarında `image_generate` seçeneğini görmüyorsanız, `agents.defaults.imageGenerationModel` yapılandırın veya bir sağlayıcı API anahtarı ayarlayın.
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

3. Aracıya şunu söyleyin: _"Dost canlısı bir ıstakoz maskotunun görselini oluştur."_

Aracı `image_generate` aracını otomatik olarak çağırır. Araç izin listesine ekleme gerekmez — bir sağlayıcı kullanılabilir olduğunda varsayılan olarak etkindir.

## Desteklenen sağlayıcılar

| Sağlayıcı | Varsayılan model                | Düzenleme desteği                   | API anahtarı                                          |
| --------- | ------------------------------- | ----------------------------------- | ----------------------------------------------------- |
| OpenAI    | `gpt-image-1`                   | Evet (en fazla 5 görsel)            | `OPENAI_API_KEY`                                      |
| Google    | `gemini-3.1-flash-image-preview` | Evet                               | `GEMINI_API_KEY` veya `GOOGLE_API_KEY`                |
| fal       | `fal-ai/flux/dev`               | Evet                                | `FAL_KEY`                                             |
| MiniMax   | `image-01`                      | Evet (özne referansı)               | `MINIMAX_API_KEY` veya MiniMax OAuth (`minimax-portal`) |
| ComfyUI   | `workflow`                      | Evet (1 görsel, iş akışı yapılandırmalı) | bulut için `COMFY_API_KEY` veya `COMFY_CLOUD_API_KEY` |
| Vydra     | `grok-imagine`                  | Hayır                               | `VYDRA_API_KEY`                                       |

Çalışma zamanında kullanılabilir sağlayıcıları ve modelleri incelemek için `action: "list"` kullanın:

```
/tool image_generate action=list
```

## Araç parametreleri

| Parametre    | Tür      | Açıklama                                                                             |
| ------------ | -------- | ------------------------------------------------------------------------------------ |
| `prompt`     | string   | Görsel oluşturma istemi (`action: "generate"` için zorunlu)                          |
| `action`     | string   | Sağlayıcıları incelemek için `"generate"` (varsayılan) veya `"list"`                |
| `model`      | string   | Sağlayıcı/model geçersiz kılması, ör. `openai/gpt-image-1`                          |
| `image`      | string   | Düzenleme modu için tek referans görsel yolu veya URL’si                             |
| `images`     | string[] | Düzenleme modu için birden fazla referans görsel (en fazla 5)                        |
| `size`       | string   | Boyut ipucu: `1024x1024`, `1536x1024`, `1024x1536`, `1024x1792`, `1792x1024`         |
| `aspectRatio`| string   | En-boy oranı: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` |
| `resolution` | string   | Çözünürlük ipucu: `1K`, `2K` veya `4K`                                               |
| `count`      | number   | Oluşturulacak görsel sayısı (1–4)                                                    |
| `filename`   | string   | Çıktı dosya adı ipucu                                                                |

Tüm sağlayıcılar tüm parametreleri desteklemez. Araç, her sağlayıcının desteklediği parametreleri iletir, kalanları yok sayar ve bırakılan geçersiz kılmaları araç sonucunda bildirir.

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

Bir görsel oluşturulurken OpenClaw sağlayıcıları şu sırayla dener:

1. Araç çağrısındaki **`model` parametresi** (aracı bir model belirtirse)
2. Yapılandırmadaki **`imageGenerationModel.primary`**
3. Sırayla **`imageGenerationModel.fallbacks`**
4. **Otomatik algılama** — yalnızca kimlik doğrulama destekli sağlayıcı varsayılanlarını kullanır:
   - önce mevcut varsayılan sağlayıcı
   - ardından sağlayıcı kimliği sırasına göre kalan kayıtlı görsel oluşturma sağlayıcıları

Bir sağlayıcı başarısız olursa (kimlik doğrulama hatası, hız sınırı vb.), bir sonraki aday otomatik olarak denenir. Hepsi başarısız olursa, hata her denemeden ayrıntılar içerir.

Notlar:

- Otomatik algılama kimlik doğrulama farkındadır. Bir sağlayıcı varsayılanı yalnızca OpenClaw o sağlayıcıda gerçekten kimlik doğrulaması yapabildiğinde aday listesine girer.
- Geçerli olarak kayıtlı sağlayıcıları, varsayılan modellerini ve kimlik doğrulama ortam değişkeni ipuçlarını incelemek için `action: "list"` kullanın.

### Görsel düzenleme

OpenAI, Google, fal, MiniMax ve ComfyUI referans görselleri düzenlemeyi destekler. Bir referans görsel yolu veya URL’si geçin:

```
"Bu fotoğrafın sulu boya sürümünü oluştur" + image: "/path/to/photo.jpg"
```

OpenAI ve Google, `images` parametresiyle en fazla 5 referans görseli destekler. fal, MiniMax ve ComfyUI 1 görsel destekler.

MiniMax görsel oluşturma, paketlenmiş iki MiniMax kimlik doğrulama yolu üzerinden de kullanılabilir:

- API anahtarı kurulumları için `minimax/image-01`
- OAuth kurulumları için `minimax-portal/image-01`

## Sağlayıcı yetenekleri

| Yetenek               | OpenAI               | Google               | fal                 | MiniMax                    | ComfyUI                            | Vydra    |
| --------------------- | -------------------- | -------------------- | ------------------- | -------------------------- | ---------------------------------- | -------- |
| Oluşturma             | Evet (en fazla 4)    | Evet (en fazla 4)    | Evet (en fazla 4)   | Evet (en fazla 9)          | Evet (iş akışı tanımlı çıktılar)   | Evet (1) |
| Düzenleme/referans    | Evet (en fazla 5 görsel) | Evet (en fazla 5 görsel) | Evet (1 görsel) | Evet (1 görsel, özne referansı) | Evet (1 görsel, iş akışı yapılandırmalı) | Hayır    |
| Boyut denetimi        | Evet                 | Evet                 | Evet                | Hayır                      | Hayır                              | Hayır    |
| En-boy oranı          | Hayır                | Evet                 | Evet (yalnızca oluşturma) | Evet                   | Hayır                              | Hayır    |
| Çözünürlük (1K/2K/4K) | Hayır                | Evet                 | Evet                | Hayır                      | Hayır                              | Hayır    |

## İlgili

- [Araçlara Genel Bakış](/tr/tools) — kullanılabilir tüm aracı araçları
- [fal](/tr/providers/fal) — fal görsel ve video sağlayıcısı kurulumu
- [ComfyUI](/tr/providers/comfy) — yerel ComfyUI ve Comfy Cloud iş akışı kurulumu
- [Google (Gemini)](/tr/providers/google) — Gemini görsel sağlayıcısı kurulumu
- [MiniMax](/tr/providers/minimax) — MiniMax görsel sağlayıcısı kurulumu
- [OpenAI](/tr/providers/openai) — OpenAI Images sağlayıcısı kurulumu
- [Vydra](/tr/providers/vydra) — Vydra görsel, video ve konuşma kurulumu
- [Yapılandırma Başvurusu](/tr/gateway/configuration-reference#agent-defaults) — `imageGenerationModel` yapılandırması
- [Modeller](/tr/concepts/models) — model yapılandırması ve yük devretme
