---
read_when:
    - Bellek yükseltmenin otomatik olarak çalışmasını istiyorsunuz
    - Her rüya görme aşamasının ne yaptığını anlamak istiyorsunuz
    - Pekiştirmeyi `MEMORY.md` dosyasını kirletmeden ayarlamak istiyorsunuz
summary: Hafif, derin ve REM aşamaları ile bir Rüya Günlüğünü içeren arka plan bellek pekiştirmesi
title: Rüya Görme (deneysel)
x-i18n:
    generated_at: "2026-04-06T08:49:09Z"
    model: gpt-5.4
    provider: openai
    source_hash: 36c4b1e70801d662090dc8ce20608c2f141c23cd7ce53c54e3dcf332c801fd4e
    source_path: concepts/dreaming.md
    workflow: 15
---

# Rüya Görme (deneysel)

Rüya görme, `memory-core` içindeki arka plan bellek pekiştirme sistemidir.
OpenClaw'ın güçlü kısa süreli sinyalleri kalıcı belleğe taşımasına yardımcı olurken
sürecin açıklanabilir ve incelenebilir kalmasını sağlar.

Rüya görme **isteğe bağlıdır** ve varsayılan olarak devre dışıdır.

## Rüya görme nereye yazar

Rüya görme iki tür çıktı tutar:

- `memory/.dreams/` içinde **makine durumu** (hatırlama deposu, aşama sinyalleri, içe aktarma denetim noktaları, kilitler).
- `DREAMS.md` içinde (veya mevcut `dreams.md` içinde) **insan tarafından okunabilir çıktı** ve `memory/dreaming/<phase>/YYYY-MM-DD.md` altındaki isteğe bağlı aşama raporu dosyaları.

Uzun vadeli yükseltme yine yalnızca `MEMORY.md` dosyasına yazar.

## Aşama modeli

Rüya görme üç işbirlikçi aşama kullanır:

| Aşama | Amaç                                      | Kalıcı yazma      |
| ----- | ----------------------------------------- | ----------------- |
| Hafif | Son kısa süreli materyali sıralamak ve hazırlamak | Hayır             |
| Derin | Kalıcı adayları puanlamak ve yükseltmek   | Evet (`MEMORY.md`) |
| REM   | Temalar ve tekrarlayan fikirler üzerine düşünmek | Hayır             |

Bu aşamalar, ayrı kullanıcı tarafından yapılandırılan
"modlar" değil, dahili uygulama ayrıntılarıdır.

### Hafif aşama

Hafif aşama, son günlük bellek sinyallerini ve hatırlama izlerini içe alır, bunları yinelenenlerden arındırır
ve aday satırları hazırlar.

- Kısa süreli hatırlama durumundan ve son günlük bellek dosyalarından okur.
- Depolama satır içi çıktı içerdiğinde yönetilen bir `## Light Sleep` bloğu yazar.
- Daha sonraki derin sıralama için pekiştirme sinyallerini kaydeder.
- Asla `MEMORY.md` dosyasına yazmaz.

### Derin aşama

Derin aşama, neyin uzun vadeli belleğe dönüşeceğine karar verir.

- Adayları ağırlıklı puanlama ve eşik kapıları kullanarak sıralar.
- Geçmek için `minScore`, `minRecallCount` ve `minUniqueQueries` gerektirir.
- Yazmadan önce parçacıkları canlı günlük dosyalardan yeniden yükler; bu nedenle eski/silinmiş parçacıklar atlanır.
- Yükseltilen girdileri `MEMORY.md` dosyasına ekler.
- `DREAMS.md` içine bir `## Deep Sleep` özeti yazar ve isteğe bağlı olarak `memory/dreaming/deep/YYYY-MM-DD.md` dosyasını yazar.

### REM aşaması

REM aşaması kalıpları ve yansıtıcı sinyalleri çıkarır.

- Son kısa süreli izlerden tema ve düşünsel özetler oluşturur.
- Depolama satır içi çıktı içerdiğinde yönetilen bir `## REM Sleep` bloğu yazar.
- Derin sıralamada kullanılan REM pekiştirme sinyallerini kaydeder.
- Asla `MEMORY.md` dosyasına yazmaz.

## Rüya Günlüğü

Rüya görme ayrıca `DREAMS.md` içinde anlatı biçiminde bir **Rüya Günlüğü** tutar.
Her aşama yeterli materyale sahip olduktan sonra `memory-core`, en iyi çaba ilkesine dayalı bir arka plan
alt aracı turu çalıştırır (varsayılan çalışma zamanı modeli kullanılarak) ve kısa bir günlük girdisi ekler.

Bu günlük, yükseltme kaynağı değil, Dreams kullanıcı arayüzünde insan tarafından okunmak içindir.

## Derin sıralama sinyalleri

Derin sıralama, aşama pekiştirmesine ek olarak altı ağırlıklı temel sinyal kullanır:

| Sinyal              | Ağırlık | Açıklama                                        |
| ------------------- | ------ | ------------------------------------------------ |
| Sıklık              | 0.24   | Girdinin biriktirdiği kısa süreli sinyal sayısı |
| İlgililik           | 0.30   | Girdi için ortalama alma kalitesi               |
| Sorgu çeşitliliği   | 0.15   | Onu ortaya çıkaran farklı sorgu/gün bağlamları  |
| Yakınlık            | 0.15   | Zamana göre azalan tazelik puanı                |
| Pekiştirme          | 0.10   | Çok günlük tekrar gücü                          |
| Kavramsal zenginlik | 0.06   | Parçacık/yoldan kavram etiketi yoğunluğu        |

Hafif ve REM aşaması isabetleri,
`memory/.dreams/phase-signals.json` içinden yakınlığa göre azalan küçük bir artış ekler.

## Zamanlama

Etkinleştirildiğinde `memory-core`, tam bir rüya görme
taraması için tek bir cron job'ı otomatik olarak yönetir. Her tarama aşamaları sırayla çalıştırır: hafif -> REM -> derin.

Varsayılan sıklık davranışı:

| Ayar                 | Varsayılan |
| -------------------- | ---------- |
| `dreaming.frequency` | `0 3 * * *` |

## Hızlı başlangıç

Rüya görmeyi etkinleştirin:

```json
{
  "plugins": {
    "entries": {
      "memory-core": {
        "config": {
          "dreaming": {
            "enabled": true
          }
        }
      }
    }
  }
}
```

Özel bir tarama sıklığı ile rüya görmeyi etkinleştirin:

```json
{
  "plugins": {
    "entries": {
      "memory-core": {
        "config": {
          "dreaming": {
            "enabled": true,
            "timezone": "America/Los_Angeles",
            "frequency": "0 */6 * * *"
          }
        }
      }
    }
  }
}
```

## Slash komutu

```
/dreaming status
/dreaming on
/dreaming off
/dreaming help
```

## CLI iş akışı

Önizleme veya manuel uygulama için CLI yükseltmesini kullanın:

```bash
openclaw memory promote
openclaw memory promote --apply
openclaw memory promote --limit 5
openclaw memory status --deep
```

Manuel `memory promote`, CLI bayraklarıyla geçersiz kılınmadığı sürece varsayılan olarak
derin aşama eşiklerini kullanır.

Belirli bir adayın neden yükseltileceğini veya yükseltilmeyeceğini açıklayın:

```bash
openclaw memory promote-explain "router vlan"
openclaw memory promote-explain "router vlan" --json
```

REM yansımalarını, aday gerçekleri ve derin yükseltme çıktısını
hiçbir şey yazmadan önizleyin:

```bash
openclaw memory rem-harness
openclaw memory rem-harness --json
```

## Temel varsayılanlar

Tüm ayarlar `plugins.entries.memory-core.config.dreaming` altında bulunur.

| Anahtar     | Varsayılan |
| ----------- | ---------- |
| `enabled`   | `false`    |
| `frequency` | `0 3 * * *` |

Aşama politikası, eşikler ve depolama davranışı dahili uygulama
ayrıntılarıdır (kullanıcıya dönük yapılandırma değildir).

Tam anahtar listesi için [Bellek yapılandırma başvurusu](/tr/reference/memory-config#dreaming-experimental) bölümüne bakın.

## Dreams kullanıcı arayüzü

Etkinleştirildiğinde Gateway **Dreams** sekmesi şunları gösterir:

- geçerli rüya görme etkin durumunu
- aşama düzeyi durumu ve yönetilen tarama varlığını
- kısa vadeli, uzun vadeli ve bugün yükseltilen sayıları
- bir sonraki zamanlanmış çalıştırmanın zamanlamasını
- `doctor.memory.dreamDiary` tarafından desteklenen genişletilebilir bir Rüya Günlüğü okuyucusunu

## İlgili

- [Bellek](/tr/concepts/memory)
- [Bellek Arama](/tr/concepts/memory-search)
- [memory CLI](/cli/memory)
- [Bellek yapılandırma başvurusu](/tr/reference/memory-config)
