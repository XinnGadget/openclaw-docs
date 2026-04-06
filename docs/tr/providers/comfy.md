---
read_when:
    - OpenClaw ile yerel ComfyUI iş akışlarını kullanmak istiyorsunuz
    - Görsel, video veya müzik iş akışlarıyla Comfy Cloud kullanmak istiyorsunuz
    - Paketlenmiş comfy plugin yapılandırma anahtarlarına ihtiyacınız var
summary: OpenClaw içinde ComfyUI iş akışı görsel, video ve müzik oluşturma kurulumu
title: ComfyUI
x-i18n:
    generated_at: "2026-04-06T03:11:28Z"
    model: gpt-5.4
    provider: openai
    source_hash: e645f32efdffdf4cd498684f1924bb953a014d3656b48f4b503d64e38c61ba9c
    source_path: providers/comfy.md
    workflow: 15
---

# ComfyUI

OpenClaw, iş akışı odaklı ComfyUI çalıştırmaları için paketlenmiş bir `comfy` plugin'i ile gelir.

- Sağlayıcı: `comfy`
- Modeller: `comfy/workflow`
- Paylaşılan yüzeyler: `image_generate`, `video_generate`, `music_generate`
- Kimlik doğrulama: yerel ComfyUI için yok; Comfy Cloud için `COMFY_API_KEY` veya `COMFY_CLOUD_API_KEY`
- API: ComfyUI `/prompt` / `/history` / `/view` ve Comfy Cloud `/api/*`

## Neleri destekler

- Bir iş akışı JSON dosyasından görsel oluşturma
- Yüklenmiş 1 referans görselle görsel düzenleme
- Bir iş akışı JSON dosyasından video oluşturma
- Yüklenmiş 1 referans görselle video oluşturma
- Paylaşılan `music_generate` aracı üzerinden müzik veya ses oluşturma
- Yapılandırılmış bir düğümden veya eşleşen tüm çıktı düğümlerinden çıktı indirme

Paketlenmiş plugin iş akışı odaklıdır, bu nedenle OpenClaw genel
`size`, `aspectRatio`, `resolution`, `durationSeconds` veya TTS tarzı denetimleri
grafiğinize eşlemeye çalışmaz.

## Yapılandırma düzeni

Comfy, paylaşılan üst düzey bağlantı ayarlarını ve yetenek başına iş akışı
bölümlerini destekler:

```json5
{
  models: {
    providers: {
      comfy: {
        mode: "local",
        baseUrl: "http://127.0.0.1:8188",
        image: {
          workflowPath: "./workflows/flux-api.json",
          promptNodeId: "6",
          outputNodeId: "9",
        },
        video: {
          workflowPath: "./workflows/video-api.json",
          promptNodeId: "12",
          outputNodeId: "21",
        },
        music: {
          workflowPath: "./workflows/music-api.json",
          promptNodeId: "3",
          outputNodeId: "18",
        },
      },
    },
  },
}
```

Paylaşılan anahtarlar:

- `mode`: `local` veya `cloud`
- `baseUrl`: yerel için varsayılan `http://127.0.0.1:8188`, cloud için `https://cloud.comfy.org`
- `apiKey`: ortam değişkenlerine isteğe bağlı satır içi anahtar alternatifi
- `allowPrivateNetwork`: cloud kipinde özel/LAN `baseUrl` değerine izin verir

`image`, `video` veya `music` altındaki yetenek başına anahtarlar:

- `workflow` veya `workflowPath`: zorunlu
- `promptNodeId`: zorunlu
- `promptInputName`: varsayılan `text`
- `outputNodeId`: isteğe bağlı
- `pollIntervalMs`: isteğe bağlı
- `timeoutMs`: isteğe bağlı

Görsel ve video bölümleri ayrıca şunları da destekler:

- `inputImageNodeId`: referans görsel geçirdiğinizde zorunlu
- `inputImageInputName`: varsayılan `image`

## Geriye dönük uyumluluk

Mevcut üst düzey görsel yapılandırması hâlâ çalışır:

```json5
{
  models: {
    providers: {
      comfy: {
        workflowPath: "./workflows/flux-api.json",
        promptNodeId: "6",
        outputNodeId: "9",
      },
    },
  },
}
```

OpenClaw bu eski biçimi görsel iş akışı yapılandırması olarak ele alır.

## Görsel iş akışları

Varsayılan görsel modelini ayarlayın:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "comfy/workflow",
      },
    },
  },
}
```

Referans görselli düzenleme örneği:

```json5
{
  models: {
    providers: {
      comfy: {
        image: {
          workflowPath: "./workflows/edit-api.json",
          promptNodeId: "6",
          inputImageNodeId: "7",
          inputImageInputName: "image",
          outputNodeId: "9",
        },
      },
    },
  },
}
```

## Video iş akışları

Varsayılan video modelini ayarlayın:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "comfy/workflow",
      },
    },
  },
}
```

Comfy video iş akışları şu anda yapılandırılmış grafik üzerinden metinden videoya ve görselden videoya desteği sunar. OpenClaw, giriş videolarını Comfy iş akışlarına geçirmez.

## Müzik iş akışları

Paketlenmiş plugin, iş akışıyla tanımlanmış
ses veya müzik çıktıları için, paylaşılan `music_generate` aracı üzerinden sunulan bir müzik oluşturma sağlayıcısı kaydeder:

```text
/tool music_generate prompt="Warm ambient synth loop with soft tape texture"
```

Ses iş akışı JSON dosyanıza ve çıktı
düğümüne işaret etmek için `music` yapılandırma bölümünü kullanın.

## Comfy Cloud

`mode: "cloud"` ile birlikte aşağıdakilerden birini kullanın:

- `COMFY_API_KEY`
- `COMFY_CLOUD_API_KEY`
- `models.providers.comfy.apiKey`

Cloud kipi hâlâ aynı `image`, `video` ve `music` iş akışı bölümlerini kullanır.

## Canlı testler

Paketlenmiş plugin için isteğe bağlı canlı kapsama mevcuttur:

```bash
OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts
```

Canlı test, eşleşen
Comfy iş akışı bölümü yapılandırılmadıkça tek tek görsel, video veya müzik durumlarını atlar.

## İlgili

- [Görsel Oluşturma](/tr/tools/image-generation)
- [Video Oluşturma](/tools/video-generation)
- [Müzik Oluşturma](/tools/music-generation)
- [Sağlayıcı Dizini](/tr/providers/index)
- [Yapılandırma Başvurusu](/tr/gateway/configuration-reference#agent-defaults)
