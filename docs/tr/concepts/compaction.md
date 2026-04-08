---
read_when:
    - Otomatik sıkıştırmayı ve /compact komutunu anlamak istiyorsunuz
    - Bağlam sınırlarına takılan uzun oturumlarda hata ayıklıyorsunuz
summary: OpenClaw'un model sınırları içinde kalmak için uzun konuşmaları nasıl özetlediği
title: Sıkıştırma
x-i18n:
    generated_at: "2026-04-08T02:14:09Z"
    model: gpt-5.4
    provider: openai
    source_hash: e6590b82a8c3a9c310998d653459ca4d8612495703ca0a8d8d306d7643142fd1
    source_path: concepts/compaction.md
    workflow: 15
---

# Sıkıştırma

Her modelin bir bağlam penceresi vardır -- işleyebileceği en yüksek token sayısı.
Bir konuşma bu sınıra yaklaştığında, OpenClaw eski mesajları bir özette
**sıkıştırır**; böylece sohbet devam edebilir.

## Nasıl çalışır

1. Konuşmanın eski bölümleri sıkıştırılmış bir girdide özetlenir.
2. Özet, oturum dökümüne kaydedilir.
3. Son mesajlar olduğu gibi korunur.

OpenClaw geçmişi sıkıştırma parçalarına böldüğünde, asistan araç
çağrılarını eşleşen `toolResult` girdileriyle eşleştirilmiş halde tutar. Bir bölme noktası
bir araç bloğunun içine denk gelirse, OpenClaw sınırı kaydırır; böylece çift bir arada kalır ve
özetlenmemiş mevcut son bölüm korunur.

Konuşma geçmişinin tamamı diskte kalır. Sıkıştırma yalnızca
modelin bir sonraki turda gördüğü şeyi değiştirir.

## Otomatik sıkıştırma

Otomatik sıkıştırma varsayılan olarak açıktır. Oturum bağlam
sınırına yaklaştığında veya model bir bağlam taşması hatası döndürdüğünde çalışır (bu durumda
OpenClaw sıkıştırır ve yeniden dener). Yaygın taşma imzaları arasında
`request_too_large`, `context length exceeded`, `input exceeds the maximum
number of tokens`, `input token count exceeds the maximum number of input
tokens`, `input is too long for the model` ve `ollama error: context length
exceeded` bulunur.

<Info>
Sıkıştırmadan önce OpenClaw, önemli
notları [memory](/tr/concepts/memory) dosyalarına kaydetmesi için aracıya otomatik olarak hatırlatma yapar. Bu, bağlam kaybını önler.
</Info>

Sıkıştırma davranışını yapılandırmak için `openclaw.json` dosyanızdaki `agents.defaults.compaction` ayarını kullanın (mod, hedef token sayısı vb.).
Sıkıştırma özetleme, varsayılan olarak opak tanımlayıcıları korur (`identifierPolicy: "strict"`). Bunu `identifierPolicy: "off"` ile geçersiz kılabilir veya `identifierPolicy: "custom"` ve `identifierInstructions` ile özel metin sağlayabilirsiniz.

İsteğe bağlı olarak, sıkıştırma özetleme için `agents.defaults.compaction.model` üzerinden farklı bir model belirtebilirsiniz. Bu, birincil modeliniz yerel veya küçük bir model olduğunda ve sıkıştırma özetlerinin daha yetenekli bir model tarafından üretilmesini istediğinizde kullanışlıdır. Geçersiz kılma, herhangi bir `provider/model-id` dizesini kabul eder:

```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "model": "openrouter/anthropic/claude-sonnet-4-6"
      }
    }
  }
}
```

Bu, yerel modellerle de çalışır; örneğin özetlemeye ayrılmış ikinci bir Ollama modeli veya ince ayarlanmış bir sıkıştırma uzmanı:

```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "model": "ollama/llama3.1:8b"
      }
    }
  }
}
```

Ayarlanmadığında, sıkıştırma aracının birincil modelini kullanır.

## Takılabilir sıkıştırma sağlayıcıları

Plugins, eklenti API'sindeki `registerCompactionProvider()` aracılığıyla özel bir sıkıştırma sağlayıcısı kaydedebilir. Bir sağlayıcı kaydedilip yapılandırıldığında, OpenClaw özetlemeyi yerleşik LLM işlem hattı yerine ona devreder.

Kayıtlı bir sağlayıcıyı kullanmak için yapılandırmanızda sağlayıcı kimliğini ayarlayın:

```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "provider": "my-provider"
      }
    }
  }
}
```

Bir `provider` ayarlamak, otomatik olarak `mode: "safeguard"` kullanımını zorunlu kılar. Sağlayıcılar, yerleşik yolla aynı sıkıştırma yönergelerini ve tanımlayıcı koruma ilkesini alır; ayrıca OpenClaw, sağlayıcı çıktısından sonra da son tur ve bölünmüş tur son ek bağlamını korur. Sağlayıcı başarısız olursa veya boş bir sonuç döndürürse, OpenClaw yerleşik LLM özetlemeye geri döner.

## Otomatik sıkıştırma (varsayılan olarak açık)

Bir oturum modelin bağlam penceresine yaklaştığında veya bunu aştığında, OpenClaw otomatik sıkıştırmayı tetikler ve orijinal isteği sıkıştırılmış bağlamı kullanarak yeniden deneyebilir.

Şunları görürsünüz:

- ayrıntılı modda `🧹 Otomatik sıkıştırma tamamlandı`
- `/status` içinde `🧹 Sıkıştırmalar: <count>`

Sıkıştırmadan önce OpenClaw, kalıcı notları diske kaydetmek için **sessiz bellek boşaltma** turu çalıştırabilir.
Ayrıntılar ve yapılandırma için bkz. [Memory](/tr/concepts/memory).

## El ile sıkıştırma

Sıkıştırmayı zorlamak için herhangi bir sohbette `/compact` yazın. Özeti
yönlendirmek için yönergeler ekleyin:

```
/compact API tasarım kararlarına odaklan
```

## Farklı bir model kullanma

Varsayılan olarak, sıkıştırma aracınızın birincil modelini kullanır. Daha iyi
özetler için daha yetenekli bir model kullanabilirsiniz:

```json5
{
  agents: {
    defaults: {
      compaction: {
        model: "openrouter/anthropic/claude-sonnet-4-6",
      },
    },
  },
}
```

## Sıkıştırma başlangıç bildirimi

Varsayılan olarak, sıkıştırma sessizce çalışır. Sıkıştırma
başladığında kısa bir bildirim göstermek için `notifyUser` seçeneğini etkinleştirin:

```json5
{
  agents: {
    defaults: {
      compaction: {
        notifyUser: true,
      },
    },
  },
}
```

Etkinleştirildiğinde, kullanıcı her sıkıştırma çalışmasının başında kısa bir mesaj görür (örneğin, "Bağlam sıkıştırılıyor...").

## Sıkıştırma ve budama karşılaştırması

|                  | Sıkıştırma                    | Budama                           |
| ---------------- | ----------------------------- | -------------------------------- |
| **Ne yapar**     | Eski konuşmayı özetler        | Eski araç sonuçlarını kırpar     |
| **Kaydedilir mi?** | Evet (oturum dökümünde)     | Hayır (yalnızca bellekte, istek başına) |
| **Kapsam**       | Tüm konuşma                   | Yalnızca araç sonuçları          |

[Oturum budama](/tr/concepts/session-pruning), özetleme yapmadan
araç çıktısını kırpan daha hafif bir tamamlayıcıdır.

## Sorun giderme

**Çok sık mı sıkıştırılıyor?** Modelin bağlam penceresi küçük olabilir veya araç
çıktıları büyük olabilir. Şunu etkinleştirmeyi deneyin:
[oturum budama](/tr/concepts/session-pruning).

**Sıkıştırmadan sonra bağlam eski mi geliyor?** Özeti yönlendirmek için `/compact Focus on <topic>` kullanın veya notların kalıcı olmasını sağlamak için [memory flush](/tr/concepts/memory) seçeneğini etkinleştirin.

**Temiz bir başlangıca mı ihtiyacınız var?** `/new`, sıkıştırma yapmadan yeni bir oturum başlatır.

Gelişmiş yapılandırma için (ayrılmış token'lar, tanımlayıcı koruma, özel
bağlam motorları, OpenAI sunucu tarafı sıkıştırma), bkz.
[Oturum Yönetimi Derinlemesine İnceleme](/tr/reference/session-management-compaction).

## İlgili

- [Oturum](/tr/concepts/session) — oturum yönetimi ve yaşam döngüsü
- [Oturum Budama](/tr/concepts/session-pruning) — araç sonuçlarını kırpma
- [Bağlam](/tr/concepts/context) — aracı turları için bağlamın nasıl oluşturulduğu
- [Kancalar](/tr/automation/hooks) — sıkıştırma yaşam döngüsü kancaları (`before_compaction`, `after_compaction`)
