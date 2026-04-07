---
read_when:
    - Medya yeteneklerine genel bir bakış arıyorsunuz
    - Hangi medya sağlayıcısını yapılandıracağınıza karar veriyorsunuz
    - Asenkron medya üretiminin nasıl çalıştığını anlamaya çalışıyorsunuz
summary: Medya üretimi, anlama ve konuşma yetenekleri için birleşik giriş sayfası
title: Medyaya Genel Bakış
x-i18n:
    generated_at: "2026-04-07T08:50:06Z"
    model: gpt-5.4
    provider: openai
    source_hash: cfee08eb91ec3e827724c8fa99bff7465356f6f1ac1b146562f35651798e3fd6
    source_path: tools/media-overview.md
    workflow: 15
---

# Medya Üretimi ve Anlama

OpenClaw görüntüler, videolar ve müzik üretir; gelen medyayı (görüntü, ses, video) anlar ve yanıtları metinden konuşmaya ile sesli olarak okur. Tüm medya yetenekleri araç odaklıdır: agent bunları konuşmaya göre ne zaman kullanacağına karar verir ve her araç yalnızca en az bir destekleyici sağlayıcı yapılandırıldığında görünür.

## Yeteneklere hızlı bakış

| Yetenek              | Araç             | Sağlayıcılar                                                                               | Ne yapar                                               |
| -------------------- | ---------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------ |
| Görüntü üretimi      | `image_generate` | ComfyUI, fal, Google, MiniMax, OpenAI, Vydra                                               | Metin prompt'larından veya referanslardan görüntü oluşturur ya da düzenler |
| Video üretimi        | `video_generate` | Alibaba, BytePlus, ComfyUI, fal, Google, MiniMax, OpenAI, Qwen, Runway, Together, Vydra, xAI | Metinden, görüntülerden veya mevcut videolardan video oluşturur |
| Müzik üretimi        | `music_generate` | ComfyUI, Google, MiniMax                                                                   | Metin prompt'larından müzik veya ses parçaları oluşturur |
| Metinden konuşmaya (TTS) | `tts`        | ElevenLabs, Microsoft, MiniMax, OpenAI                                                     | Giden yanıtları konuşulan sese dönüştürür              |
| Medya anlama         | (otomatik)       | Herhangi bir vision/audio yetenekli model sağlayıcısı, ayrıca CLI fallback'leri            | Gelen görüntüleri, sesleri ve videoları özetler        |

## Sağlayıcı yetenek matrisi

Bu tablo, sağlayıcıların platform genelinde hangi medya yeteneklerini desteklediğini gösterir.

| Sağlayıcı | Görüntü | Video | Müzik | TTS | STT / Transkripsiyon | Medya Anlama |
| --------- | ------- | ----- | ----- | --- | -------------------- | ------------ |
| Alibaba   |         | Yes   |       |     |                      |              |
| BytePlus  |         | Yes   |       |     |                      |              |
| ComfyUI   | Yes     | Yes   | Yes   |     |                      |              |
| Deepgram  |         |       |       |     | Yes                  |              |
| ElevenLabs|         |       |       | Yes |                      |              |
| fal       | Yes     | Yes   |       |     |                      |              |
| Google    | Yes     | Yes   | Yes   |     |                      | Yes          |
| Microsoft |         |       |       | Yes |                      |              |
| MiniMax   | Yes     | Yes   | Yes   | Yes |                      |              |
| OpenAI    | Yes     | Yes   |       | Yes | Yes                  | Yes          |
| Qwen      |         | Yes   |       |     |                      |              |
| Runway    |         | Yes   |       |     |                      |              |
| Together  |         | Yes   |       |     |                      |              |
| Vydra     | Yes     | Yes   |       |     |                      |              |
| xAI       |         | Yes   |       |     |                      |              |

<Note>
Medya anlama, sağlayıcı config'inizde kayıtlı olan herhangi bir vision-capable veya audio-capable modeli kullanır. Yukarıdaki tablo, özel medya-anlama desteğine sahip sağlayıcıları öne çıkarır; multimodal modellere sahip çoğu LLM sağlayıcısı (Anthropic, Google, OpenAI vb.) etkin yanıt modeli olarak yapılandırıldığında gelen medyayı da anlayabilir.
</Note>

## Asenkron üretim nasıl çalışır

Video ve müzik üretimi arka plan görevleri olarak çalışır; çünkü sağlayıcı işlemesi tipik olarak 30 saniye ile birkaç dakika sürer. Agent `video_generate` veya `music_generate` çağırdığında, OpenClaw isteği sağlayıcıya gönderir, hemen bir görev kimliği döndürür ve işi görev ledger'ında izler. İş çalışırken agent diğer mesajlara yanıt vermeye devam eder. Sağlayıcı tamamladığında OpenClaw agent'ı uyandırır; böylece tamamlanmış medyayı özgün kanala geri gönderebilir. Görüntü üretimi ve TTS eşzamanlıdır ve yanıtla birlikte satır içinde tamamlanır.

## Hızlı bağlantılar

- [Image Generation](/tr/tools/image-generation) -- görüntü oluşturma ve düzenleme
- [Video Generation](/tr/tools/video-generation) -- metinden videoya, görüntüden videoya ve videodan videoya
- [Music Generation](/tr/tools/music-generation) -- müzik ve ses parçaları oluşturma
- [Text-to-Speech](/tr/tools/tts) -- yanıtları konuşulan sese dönüştürme
- [Media Understanding](/tr/nodes/media-understanding) -- gelen görüntüleri, sesleri ve videoları anlama
