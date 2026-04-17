---
read_when:
    - Bellek yükseltmenin otomatik olarak çalışmasını istiyorsunuz
    - Her Dreaming evresinin ne yaptığını anlamak istiyorsunuz
    - Pekiştirmeyi, `MEMORY.md` dosyasını kirletmeden ayarlamak istiyorsunuz
summary: Hafif, derin ve REM evreleri ile bir Rüya Günlüğü eşliğinde arka plan bellek pekiştirme
title: Dreaming
x-i18n:
    generated_at: "2026-04-15T14:40:31Z"
    model: gpt-5.4
    provider: openai
    source_hash: a5bcaec80f62e7611ed533094ef1917bd72c885f57252824db910e1f0496adc6
    source_path: concepts/dreaming.md
    workflow: 15
---

# Dreaming

Dreaming, `memory-core` içindeki arka plan bellek pekiştirme sistemidir.
OpenClaw’un güçlü kısa süreli sinyalleri kalıcı belleğe taşımasına yardımcı olurken
süreci açıklanabilir ve gözden geçirilebilir tutar.

Dreaming **isteğe bağlıdır** ve varsayılan olarak devre dışıdır.

## Dreaming ne yazar

Dreaming iki tür çıktı tutar:

- `memory/.dreams/` içinde **makine durumu** (geri çağırma deposu, evre sinyalleri, içe aktarma denetim noktaları, kilitler).
- `DREAMS.md` (veya mevcut `dreams.md`) içinde **insan tarafından okunabilir çıktı** ve `memory/dreaming/<phase>/YYYY-MM-DD.md` altında isteğe bağlı evre raporu dosyaları.

Uzun vadeli yükseltme yine yalnızca `MEMORY.md` dosyasına yazar.

## Evre modeli

Dreaming üç işbirlikçi evre kullanır:

| Evre | Amaç                                     | Kalıcı yazım      |
| ----- | ---------------------------------------- | ----------------- |
| Hafif | Son kısa süreli materyali sıralamak ve hazırlamak | Hayır             |
| Derin | Kalıcı adayları puanlamak ve yükseltmek  | Evet (`MEMORY.md`) |
| REM   | Temalar ve tekrar eden fikirler üzerine düşünmek | Hayır             |

Bu evreler, kullanıcı tarafından ayrı ayrı yapılandırılan
"modlar" değil, dahili uygulama ayrıntılarıdır.

### Hafif evre

Hafif evre, son günlük bellek sinyallerini ve geri çağırma izlerini içe aktarır,
bunları tekilleştirir ve aday satırları hazırlar.

- Kısa süreli geri çağırma durumundan, son günlük bellek dosyalarından ve mevcut olduğunda sansürlenmiş oturum dökümlerinden okur.
- Depolama satır içi çıktı içerdiğinde yönetilen bir `## Light Sleep` bloğu yazar.
- Daha sonra derin sıralama için pekiştirme sinyallerini kaydeder.
- Asla `MEMORY.md` dosyasına yazmaz.

### Derin evre

Derin evre, neyin uzun vadeli belleğe dönüşeceğine karar verir.

- Adayları ağırlıklı puanlama ve eşik geçitleri kullanarak sıralar.
- `minScore`, `minRecallCount` ve `minUniqueQueries` değerlerinin geçilmesini gerektirir.
- Yazmadan önce parçaları canlı günlük dosyalardan yeniden yükler; böylece eski/silinmiş parçalar atlanır.
- Yükseltilen girdileri `MEMORY.md` dosyasına ekler.
- `DREAMS.md` içine bir `## Deep Sleep` özeti yazar ve isteğe bağlı olarak `memory/dreaming/deep/YYYY-MM-DD.md` dosyasını yazar.

### REM evresi

REM evresi, örüntüleri ve yansıtıcı sinyalleri çıkarır.

- Son kısa süreli izlerden tema ve yansıma özetleri oluşturur.
- Depolama satır içi çıktı içerdiğinde yönetilen bir `## REM Sleep` bloğu yazar.
- Derin sıralamada kullanılan REM pekiştirme sinyallerini kaydeder.
- Asla `MEMORY.md` dosyasına yazmaz.

## Oturum dökümü içe aktarma

Dreaming, sansürlenmiş oturum dökümlerini dreaming külliyatına içe aktarabilir. Dökümler
mevcut olduğunda, günlük bellek sinyalleri ve geri çağırma izlerinin yanında hafif evreye
beslenir. Kişisel ve hassas içerikler içe aktarmadan önce sansürlenir.

## Rüya Günlüğü

Dreaming ayrıca `DREAMS.md` içinde anlatı niteliğinde bir **Rüya Günlüğü** tutar.
Her evre yeterli malzemeye sahip olduktan sonra `memory-core`, en iyi çaba esaslı bir arka plan
alt aracı dönüşü çalıştırır (varsayılan çalışma zamanı modelini kullanarak) ve kısa bir günlük girdisi ekler.

Bu günlük, yükseltme kaynağı değil, Dreams UI içinde insan tarafından okunmak içindir.
Dreaming tarafından üretilen günlük/rapor yapıtları kısa süreli
yükseltmeden hariç tutulur. `MEMORY.md` içine yükseltme için yalnızca temellendirilmiş
bellek parçaları uygundur.

İnceleme ve kurtarma çalışmaları için ayrıca temellendirilmiş bir geçmişi doldurma hattı vardır:

- `memory rem-harness --path ... --grounded`, geçmiş `YYYY-MM-DD.md` notlarından temellendirilmiş günlük çıktısını önizler.
- `memory rem-backfill --path ...`, geri alınabilir temellendirilmiş günlük girdilerini `DREAMS.md` içine yazar.
- `memory rem-backfill --path ... --stage-short-term`, temellendirilmiş kalıcı adayları normal derin evrenin zaten kullandığı aynı kısa süreli kanıt deposuna hazırlar.
- `memory rem-backfill --rollback` ve `--rollback-short-term`, sıradan günlük girdilerine veya canlı kısa süreli geri çağırmaya dokunmadan bu hazırlanmış geçmiş doldurma yapıtlarını kaldırır.

Control UI aynı günlük geçmiş doldurma/sıfırlama akışını sunar; böylece temellendirilmiş adayların
yükseltmeyi hak edip etmediğine karar vermeden önce sonuçları Dreams sahnesinde inceleyebilirsiniz.
Sahne ayrıca ayrı bir temellendirilmiş hat gösterir; böylece hangi hazırlanmış kısa süreli girdilerin
geçmiş tekrar oynatımından geldiğini, hangi yükseltilmiş öğelerin temellendirilmiş odaklı olduğunu
görebilir ve sıradan canlı kısa süreli duruma dokunmadan yalnızca temellendirilmiş hazırlanmış girdileri temizleyebilirsiniz.

## Derin sıralama sinyalleri

Derin sıralama, evre pekiştirmesine ek olarak altı ağırlıklı temel sinyal kullanır:

| Sinyal             | Ağırlık | Açıklama                                          |
| ------------------ | ------- | ------------------------------------------------- |
| Sıklık             | 0.24    | Girdinin biriktirdiği kısa süreli sinyal sayısı   |
| İlgililik          | 0.30    | Girdi için ortalama geri getirme kalitesi         |
| Sorgu çeşitliliği  | 0.15    | Onu ortaya çıkaran farklı sorgu/gün bağlamları    |
| Güncellik          | 0.15    | Zamana bağlı azalan tazelik puanı                 |
| Pekiştirme         | 0.10    | Çok günlü tekrar gücü                             |
| Kavramsal zenginlik| 0.06    | Parça/yoldan kavram etiketi yoğunluğu             |

Hafif ve REM evresi isabetleri,
`memory/.dreams/phase-signals.json` dosyasından güncelliğe bağlı küçük bir azalan artış ekler.

## Zamanlama

Etkinleştirildiğinde `memory-core`, tam bir dreaming
taraması için tek bir Cron işi otomatik olarak yönetir. Her tarama evreleri sırayla çalıştırır: hafif -> REM -> derin.

Varsayılan sıklık davranışı:

| Ayar                 | Varsayılan |
| -------------------- | ---------- |
| `dreaming.frequency` | `0 3 * * *` |

## Hızlı başlangıç

Dreaming’i etkinleştirin:

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

Özel bir tarama sıklığı ile Dreaming’i etkinleştirin:

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

Önizleme veya elle uygulama için CLI yükseltmesini kullanın:

```bash
openclaw memory promote
openclaw memory promote --apply
openclaw memory promote --limit 5
openclaw memory status --deep
```

Elle `memory promote`, CLI bayraklarıyla geçersiz kılınmadığı sürece varsayılan olarak
derin evre eşiklerini kullanır.

Belirli bir adayın neden yükseltileceğini veya yükseltilmeyeceğini açıklayın:

```bash
openclaw memory promote-explain "router vlan"
openclaw memory promote-explain "router vlan" --json
```

Hiçbir şey yazmadan REM yansımalarını, aday gerçekleri ve derin yükseltme çıktısını önizleyin:

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

Evre politikası, eşikler ve depolama davranışı dahili uygulama
ayrıntılarıdır (kullanıcıya dönük yapılandırma değildir).

Tam anahtar listesi için
[Bellek yapılandırma başvurusu](/tr/reference/memory-config#dreaming)
sayfasına bakın.

## Dreams UI

Etkinleştirildiğinde Gateway **Dreams** sekmesi şunları gösterir:

- dreaming’in mevcut etkinlik durumu
- evre düzeyinde durum ve yönetilen tarama varlığı
- kısa süreli, temellendirilmiş, sinyal ve bugün yükseltilen sayıları
- bir sonraki zamanlanmış çalıştırmanın zamanı
- hazırlanmış geçmiş tekrar oynatım girdileri için ayrı bir temellendirilmiş Sahne hattı
- `doctor.memory.dreamDiary` tarafından desteklenen genişletilebilir bir Rüya Günlüğü okuyucusu

## İlgili

- [Bellek](/tr/concepts/memory)
- [Bellek Arama](/tr/concepts/memory-search)
- [memory CLI](/cli/memory)
- [Bellek yapılandırma başvurusu](/tr/reference/memory-config)
