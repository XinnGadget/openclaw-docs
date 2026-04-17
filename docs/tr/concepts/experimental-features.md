---
read_when:
    - Bir ``.experimental`` yapılandırma anahtarı görüyorsunuz ve bunun kararlı olup olmadığını öğrenmek istiyorsunuz
    - Önizleme çalışma zamanı özelliklerini, bunları normal varsayılanlarla karıştırmadan denemek istiyorsunuz
    - Şu anda belgelenmiş deneysel bayrakları bulmak için tek bir yer istiyorsunuz
summary: OpenClaw'da deneysel bayraklar ne anlama gelir ve hangileri şu anda belgelenmiştir
title: Deneysel Özellikler
x-i18n:
    generated_at: "2026-04-15T14:40:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2d1c7b3d4cd56ef8a0bdab1deb9918e9b2c9a33f956d63193246087f8633dcf3
    source_path: concepts/experimental-features.md
    workflow: 15
---

# Deneysel özellikler

OpenClaw'daki deneysel özellikler **isteğe bağlı önizleme yüzeyleridir**. Bunlar
açık bayrakların arkasındadır çünkü kararlı bir varsayılanı ya da uzun ömürlü bir
genel sözleşmeyi hak etmeden önce hâlâ gerçek dünyada yeterince denenmeleri gerekir.

Bunlara normal yapılandırmadan farklı yaklaşın:

- İlgili belgede birini denemeniz söylenmedikçe bunları varsayılan olarak **kapalı tutun**.
- Kararlı yapılandırmaya göre **biçim ve davranışın** daha hızlı değişmesini bekleyin.
- Zaten mevcutsa önce kararlı yolu tercih edin.
- OpenClaw'ı geniş ölçekte devreye alıyorsanız, deneysel bayrakları paylaşılan bir
  temele yerleştirmeden önce daha küçük bir ortamda test edin.

## Şu anda belgelenmiş bayraklar

| Yüzey                    | Anahtar                                                   | Bunu şu durumda kullanın                                                                                       | Daha fazla                                                                                   |
| ------------------------ | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Yerel model çalışma zamanı | `agents.defaults.experimental.localModelLean`             | Daha küçük veya daha katı bir yerel arka uç, OpenClaw'ın tam varsayılan araç yüzeyini kaldıramıyorsa          | [Yerel Modeller](/tr/gateway/local-models)                                                       |
| Bellek araması           | `agents.defaults.memorySearch.experimental.sessionMemory` | `memory_search`'ün önceki oturum dökümlerini dizine eklemesini istiyorsanız ve ek depolama/dizinleme maliyetini kabul ediyorsanız | [Bellek yapılandırma başvurusu](/tr/reference/memory-config#session-memory-search-experimental) |
| Yapılandırılmış planlama aracı | `tools.experimental.planTool`                             | Uyumlu çalışma zamanlarında ve kullanıcı arayüzlerinde, çok adımlı iş takibi için yapılandırılmış `update_plan` aracının sunulmasını istiyorsanız | [Gateway yapılandırma başvurusu](/tr/gateway/configuration-reference#toolsexperimental)         |

## Yerel model yalın modu

`agents.defaults.experimental.localModelLean: true`, daha zayıf yerel model kurulumları için
bir rahatlatma supabıdır. `browser`, `cron` ve `message` gibi ağır varsayılan araçları
budar; böylece istem biçimi daha küçük olur ve küçük bağlamlı veya daha katı
OpenAI uyumlu arka uçlar için daha az kırılgan hale gelir.

Bu kasıtlı olarak normal yol **değildir**. Arka ucunuz tam çalışma zamanını sorunsuz
şekilde yönetiyorsa bunu kapalı bırakın.

## Deneysel, gizli demek değildir

Bir özellik deneysel ise, OpenClaw bunu belgelerde ve yapılandırma yolunun kendisinde
açıkça belirtmelidir. Yapmaması gereken şey ise önizleme davranışını kararlı gibi
görünen bir varsayılan düğmenin içine gizlice sokup bunun normalmiş gibi davranmaktır.
Yapılandırma yüzeyleri böyle karmaşık hale gelir.
