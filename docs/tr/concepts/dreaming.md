---
read_when:
    - Bellek yükseltmenin otomatik olarak çalışmasını istiyorsunuz
    - Her rüya görme evresinin ne yaptığını anlamak istiyorsunuz
    - Pekiştirmeyi `MEMORY.md` dosyasını kirletmeden ayarlamak istiyorsunuz
summary: Hafif, derin ve REM evreleri ile Arka plan bellek pekiştirmesi ve bir Rüya Günlüğü
title: Rüya Görme (deneysel)
x-i18n:
    generated_at: "2026-04-06T03:06:18Z"
    model: gpt-5.4
    provider: openai
    source_hash: f27da718176bebf59fe8a80fddd4fb5b6d814ac5647f6c1e8344bcfb328db9de
    source_path: concepts/dreaming.md
    workflow: 15
---

# Rüya Görme (deneysel)

Rüya görme, `memory-core` içindeki arka plan bellek pekiştirme sistemidir.
OpenClaw'ın güçlü kısa süreli sinyalleri kalıcı belleğe taşımasına yardımcı olurken
sürecin açıklanabilir ve gözden geçirilebilir kalmasını sağlar.

Rüya görme **isteğe bağlıdır** ve varsayılan olarak devre dışıdır.

## Rüya görme ne yazar

Rüya görme iki tür çıktı tutar:

- `memory/.dreams/` içinde **makine durumu** (geri çağırma deposu, evre sinyalleri, alım denetim noktaları, kilitler).
- `DREAMS.md` (veya mevcut `dreams.md`) içinde **insan tarafından okunabilir çıktı** ve `memory/dreaming/<phase>/YYYY-MM-DD.md` altında isteğe bağlı evre raporu dosyaları.

Uzun vadeli yükseltme hâlâ yalnızca `MEMORY.md` dosyasına yazar.

## Evre modeli

Rüya görme üç iş birliği yapan evre kullanır:

| Evre | Amaç                                      | Kalıcı yazım      |
| ----- | ----------------------------------------- | ----------------- |
| Hafif | Son kısa süreli materyali sıralamak ve hazırlamak | Hayır             |
| Derin | Kalıcı adayları puanlamak ve yükseltmek   | Evet (`MEMORY.md`) |
| REM   | Temalar ve tekrarlayan fikirler üzerine düşünmek | Hayır             |

Bu evreler, ayrı kullanıcı yapılandırmalı
"kipler" değil, dahili uygulama ayrıntılarıdır.

### Hafif evre

Hafif evre son günlük bellek sinyallerini ve geri çağırma izlerini alır, bunları tekilleştirir
ve aday satırları hazırlar.

- Kısa süreli geri çağırma durumundan ve son günlük bellek dosyalarından okur.
- Depolama satır içi çıktı içerdiğinde yönetilen bir `## Hafif Uyku` bloğu yazar.
- Daha sonraki derin sıralama için pekiştirme sinyalleri kaydeder.
- Asla `MEMORY.md` dosyasına yazmaz.

### Derin evre

Derin evre, neyin uzun vadeli belleğe dönüşeceğine karar verir.

- Adayları ağırlıklı puanlama ve eşik geçitleri kullanarak sıralar.
- `minScore`, `minRecallCount` ve `minUniqueQueries` değerlerinin geçilmesini gerektirir.
- Yazmadan önce parçaları canlı günlük dosyalardan yeniden yükler; böylece eski/silinmiş parçalar atlanır.
- Yükseltilen girdileri `MEMORY.md` dosyasına ekler.
- `DREAMS.md` içine bir `## Derin Uyku` özeti yazar ve isteğe bağlı olarak `memory/dreaming/deep/YYYY-MM-DD.md` dosyasını yazar.

### REM evresi

REM evresi örüntüleri ve düşünsel sinyalleri çıkarır.

- Son kısa süreli izlerden tema ve düşünce özetleri oluşturur.
- Depolama satır içi çıktı içerdiğinde yönetilen bir `## REM Uykusu` bloğu yazar.
- Derin sıralamada kullanılan REM pekiştirme sinyallerini kaydeder.
- Asla `MEMORY.md` dosyasına yazmaz.

## Rüya Günlüğü

Rüya görme ayrıca `DREAMS.md` içinde anlatısal bir **Rüya Günlüğü** tutar.
Her evre yeterli materyale sahip olduktan sonra `memory-core`, en iyi çaba esasına dayalı bir arka plan
alt aracısı turu çalıştırır (varsayılan çalışma zamanı modelini kullanarak) ve kısa bir günlük girdisi ekler.

Bu günlük, yükseltme kaynağı değil, Dreams UI içinde insanlar tarafından okunmak içindir.

## Derin sıralama sinyalleri

Derin sıralama, evre pekiştirmesine ek olarak ağırlıklı altı temel sinyal kullanır:

| Sinyal              | Ağırlık | Açıklama                                        |
| ------------------- | ------ | ------------------------------------------------ |
| Sıklık              | 0.24   | Girdinin biriktirdiği kısa süreli sinyal sayısı |
| İlgililik           | 0.30   | Girdi için ortalama geri getirme kalitesi       |
| Sorgu çeşitliliği   | 0.15   | Onu ortaya çıkaran farklı sorgu/gün bağlamları  |
| Yakınlık            | 0.15   | Zamana göre azalan tazelik puanı                |
| Pekiştirme          | 0.10   | Çok günlük tekrar gücü                          |
| Kavramsal zenginlik | 0.06   | Parça/yoldan gelen kavram etiketi yoğunluğu     |

Hafif ve REM evresi isabetleri,
`memory/.dreams/phase-signals.json` içinden zamana göre azalan küçük bir artış ekler.

## Zamanlama

Etkinleştirildiğinde `memory-core`, tam bir rüya görme
taraması için tek bir cron işi otomatik olarak yönetir. Her tarama evreleri sırayla çalıştırır: hafif -> REM -> derin.

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

## Eğik çizgi komutu

```
/dreaming status
/dreaming on
/dreaming off
/dreaming help
```

## CLI iş akışı

Önizleme veya el ile uygulama için CLI yükseltmesini kullanın:

```bash
openclaw memory promote
openclaw memory promote --apply
openclaw memory promote --limit 5
openclaw memory status --deep
```

El ile `memory promote`, CLI bayraklarıyla geçersiz kılınmadıkça varsayılan olarak
derin evre eşiklerini kullanır.

## Temel varsayılanlar

Tüm ayarlar `plugins.entries.memory-core.config.dreaming` altında bulunur.

| Anahtar    | Varsayılan |
| ----------- | ----------- |
| `enabled`   | `false`     |
| `frequency` | `0 3 * * *` |

Evre ilkesi, eşikler ve depolama davranışı dahili uygulama
ayrıntılarıdır (kullanıcıya yönelik yapılandırma değildir).

Tam anahtar listesi için bkz. [Bellek yapılandırma başvurusu](/tr/reference/memory-config#dreaming-experimental).

## Dreams UI

Etkinleştirildiğinde Gateway içindeki **Dreams** sekmesi şunları gösterir:

- rüya görmenin mevcut etkin durumu
- evre düzeyinde durum ve yönetilen tarama varlığı
- kısa süreli, uzun vadeli ve bugün yükseltilen sayıları
- bir sonraki zamanlanan çalıştırmanın zamanı
- `doctor.memory.dreamDiary` tarafından desteklenen genişletilebilir bir Rüya Günlüğü okuyucusu

## İlgili

- [Bellek](/tr/concepts/memory)
- [Bellek Araması](/tr/concepts/memory-search)
- [memory CLI](/cli/memory)
- [Bellek yapılandırma başvurusu](/tr/reference/memory-config)
