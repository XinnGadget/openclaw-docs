---
read_when:
    - Ajan aracılığıyla görsel üretme
    - Görsel üretim sağlayıcılarını ve modellerini yapılandırma
    - image_generate araç parametrelerini anlama
summary: Yapılandırılmış sağlayıcıları kullanarak görseller oluşturun ve düzenleyin (OpenAI, Google Gemini, fal, MiniMax, ComfyUI, Vydra)
title: Görsel Üretimi
x-i18n:
    generated_at: "2026-04-07T08:50:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8f7303c199d46e63e88f5f9567478a1025631afb03cb35f44344c12370365e57
    source_path: tools/image-generation.md
    workflow: 15
---

# Görsel Üretimi

`image_generate` aracı, ajanın yapılandırılmış sağlayıcılarınızı kullanarak görseller oluşturmasına ve düzenlemesine olanak tanır. Üretilen görseller, ajanın yanıtında medya eki olarak otomatik şekilde gönderilir.

<Note>
Araç yalnızca en az bir görsel üretim sağlayıcısı kullanılabilir olduğunda görünür. Ajanınızın araçlarında `image_generate` görmüyorsanız, `agents.defaults.imageGenerationModel` yapılandırın veya bir sağlayıcı API anahtarı ayarlayın.
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

3. Ajana şunu sorun: _"Dost canlısı bir ıstakoz maskotu görseli oluştur."_

Ajan `image_generate` aracını otomatik olarak çağırır. Araç allow-list eklemesi gerekmez — bir sağlayıcı kullanılabilir olduğunda varsayılan olarak etkindir.

## Desteklenen sağlayıcılar

| Sağlayıcı | Varsayılan model                | Düzenleme desteği                  | API anahtarı                                          |
| --------- | ------------------------------- | ---------------------------------- | ----------------------------------------------------- |
| OpenAI    | `gpt-image-1`                   | Evet (en fazla 5 görsel)           | `OPENAI_API_KEY`                                      |
| Google    | `gemini-3.1-flash-image-preview`| Evet                               | `GEMINI_API_KEY` veya `GOOGLE_API_KEY`                |
| fal       | `fal-ai/flux/dev`               | Evet                               | `FAL_KEY`                                             |
| MiniMax   | `image-01`                      | Evet (özne referansı)              | `MINIMAX_API_KEY` veya MiniMax OAuth (`minimax-portal`) |
| ComfyUI   | `workflow`                      | Evet (1 görsel, iş akışı yapılandırmalı) | bulut için `COMFY_API_KEY` veya `COMFY_CLOUD_API_KEY` |
| Vydra     | `grok-imagine`                  | Hayır                              | `VYDRA_API_KEY`                                       |

Çalışma zamanında kullanılabilir sağlayıcıları ve modelleri incelemek için `action: "list"` kullanın:

```
/tool image_generate action=list
```

## Araç parametreleri

| Parametre    | Tür      | Açıklama                                                                          |
| ------------ | -------- | --------------------------------------------------------------------------------- |
| `prompt`     | string   | Görsel üretim istemi (`action: "generate"` için gereklidir)                       |
| `action`     | string   | Sağlayıcıları incelemek için `"generate"` (varsayılan) veya `"list"`              |
| `model`      | string   | Sağlayıcı/model geçersiz kılması, ör. `openai/gpt-image-1`                        |
| `image`      | string   | Düzenleme modu için tek referans görsel yolu veya URL                             |
| `images`     | string[] | Düzenleme modu için birden çok referans görsel (en fazla 5)                       |
| `size`       | string   | Boyut ipucu: `1024x1024`, `1536x1024`, `1024x1536`, `1024x1792`, `1792x1024`      |
| `aspectRatio`| string   | En-boy oranı: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` |
| `resolution` | string   | Çözünürlük ipucu: `1K`, `2K` veya `4K`                                            |
| `count`      | number   | Oluşturulacak görsel sayısı (1–4)                                                 |
| `filename`   | string   | Çıktı dosya adı ipucu                                                             |

Tüm sağlayıcılar tüm parametreleri desteklemez. Bir fallback sağlayıcı, tam istenen seçenek yerine yakın bir geometri seçeneğini desteklediğinde, OpenClaw gönderimden önce bunu desteklenen en yakın boyuta, en-boy oranına veya çözünürlüğe yeniden eşler. Gerçekten desteklenmeyen geçersiz kılmalar yine araç sonucunda bildirilir.

Araç sonuçları uygulanan ayarları bildirir. OpenClaw, sağlayıcı fallback'i sırasında geometriyi yeniden eşlediğinde, döndürülen `size`, `aspectRatio` ve `resolution` değerleri gerçekten gönderilen değeri yansıtır ve `details.normalization`, istenenden uygulanana yapılan çeviriyi yakalar.

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

Bir görsel üretilirken OpenClaw sağlayıcıları şu sırayla dener:

1. Araç çağrısından gelen **`model` parametresi** (ajan bir tane belirtirse)
2. Yapılandırmadaki **`imageGenerationModel.primary`**
3. Sırasıyla **`imageGenerationModel.fallbacks`**
4. **Otomatik algılama** — yalnızca auth destekli sağlayıcı varsayılanlarını kullanır:
   - önce geçerli varsayılan sağlayıcı
   - ardından sağlayıcı kimliği sırasına göre kalan kayıtlı görsel üretim sağlayıcıları

Bir sağlayıcı başarısız olursa (auth hatası, hız sınırı vb.), sıradaki aday otomatik olarak denenir. Hepsi başarısız olursa, hata her denemeden ayrıntılar içerir.

Notlar:

- Otomatik algılama auth farkındalıklıdır. Bir sağlayıcı varsayılanı yalnızca
  OpenClaw o sağlayıcı için gerçekten kimlik doğrulaması yapabildiğinde aday listesine girer.
- Otomatik algılama varsayılan olarak etkindir. Görsel
  üretiminin yalnızca açık `model`, `primary` ve `fallbacks`
  girdilerini kullanmasını istiyorsanız
  `agents.defaults.mediaGenerationAutoProviderFallback: false` ayarlayın.
- Geçerli kayıtlı sağlayıcıları, bunların
  varsayılan modellerini ve auth env-var ipuçlarını incelemek için `action: "list"` kullanın.

### Görsel düzenleme

OpenAI, Google, fal, MiniMax ve ComfyUI referans görselleri düzenlemeyi destekler. Bir referans görsel yolu veya URL'si geçin:

```
"Bu fotoğrafın sulu boya sürümünü oluştur" + image: "/path/to/photo.jpg"
```

OpenAI ve Google, `images` parametresi aracılığıyla en fazla 5 referans görseli destekler. fal, MiniMax ve ComfyUI 1 adet destekler.

MiniMax görsel üretimi, birlikte gelen her iki MiniMax auth yolu üzerinden de kullanılabilir:

- API anahtarı kurulumları için `minimax/image-01`
- OAuth kurulumları için `minimax-portal/image-01`

## Sağlayıcı yetenekleri

| Yetenek              | OpenAI               | Google               | fal                  | MiniMax                   | ComfyUI                             | Vydra   |
| -------------------- | -------------------- | -------------------- | -------------------- | ------------------------- | ----------------------------------- | ------- |
| Üretme               | Evet (en fazla 4)    | Evet (en fazla 4)    | Evet (en fazla 4)    | Evet (en fazla 9)         | Evet (iş akışı tanımlı çıktılar)    | Evet (1) |
| Düzenleme/referans   | Evet (en fazla 5 görsel) | Evet (en fazla 5 görsel) | Evet (1 görsel)      | Evet (1 görsel, özne ref.) | Evet (1 görsel, iş akışı yapılandırmalı) | Hayır   |
| Boyut kontrolü       | Evet                 | Evet                 | Evet                 | Hayır                     | Hayır                               | Hayır   |
| En-boy oranı         | Hayır                | Evet                 | Evet (yalnızca üretme) | Evet                    | Hayır                               | Hayır   |
| Çözünürlük (1K/2K/4K)| Hayır                | Evet                 | Evet                 | Hayır                     | Hayır                               | Hayır   |

## İlgili

- [Araçlara Genel Bakış](/tr/tools) — kullanılabilir tüm ajan araçları
- [fal](/tr/providers/fal) — fal görsel ve video sağlayıcısı kurulumu
- [ComfyUI](/tr/providers/comfy) — yerel ComfyUI ve Comfy Cloud iş akışı kurulumu
- [Google (Gemini)](/tr/providers/google) — Gemini görsel sağlayıcısı kurulumu
- [MiniMax](/tr/providers/minimax) — MiniMax görsel sağlayıcısı kurulumu
- [OpenAI](/tr/providers/openai) — OpenAI Images sağlayıcısı kurulumu
- [Vydra](/tr/providers/vydra) — Vydra görsel, video ve konuşma kurulumu
- [Yapılandırma Başvurusu](/tr/gateway/configuration-reference#agent-defaults) — `imageGenerationModel` yapılandırması
- [Modeller](/tr/concepts/models) — model yapılandırması ve failover
