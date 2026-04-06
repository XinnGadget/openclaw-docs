---
read_when:
    - Belleğin nasıl çalıştığını anlamak istiyorsunuz
    - Hangi bellek dosyalarına yazılması gerektiğini öğrenmek istiyorsunuz
summary: OpenClaw’un oturumlar arasında bir şeyleri nasıl hatırladığı
title: Belleğe Genel Bakış
x-i18n:
    generated_at: "2026-04-06T03:06:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: d19d4fa9c4b3232b7a97f7a382311d2a375b562040de15e9fe4a0b1990b825e7
    source_path: concepts/memory.md
    workflow: 15
---

# Belleğe Genel Bakış

OpenClaw, aracınızın çalışma alanında **düz Markdown dosyaları** yazarak bir şeyleri hatırlar. Model yalnızca diske kaydedilenleri "hatırlar" -- gizli durum yoktur.

## Nasıl çalışır

Aracınızın bellekle ilgili üç dosyası vardır:

- **`MEMORY.md`** -- uzun vadeli bellek. Kalıcı gerçekler, tercihler ve kararlar. Her DM oturumunun başında yüklenir.
- **`memory/YYYY-MM-DD.md`** -- günlük notlar. Akan bağlam ve gözlemler. Bugünün ve dünkü notlar otomatik olarak yüklenir.
- **`DREAMS.md`** (deneysel, isteğe bağlı) -- insan incelemesi için Dream Diary ve dreaming sweep özetleri.

Bu dosyalar araç çalışma alanında bulunur (varsayılan `~/.openclaw/workspace`).

<Tip>
Aracınızın bir şeyi hatırlamasını istiyorsanız, ona söylemeniz yeterlidir: "TypeScript tercih ettiğimi hatırla." Uygun dosyaya yazacaktır.
</Tip>

## Bellek araçları

Aracının bellekle çalışmak için iki aracı vardır:

- **`memory_search`** -- ifade biçimi asılinden farklı olsa bile, anlamsal arama kullanarak ilgili notları bulur.
- **`memory_get`** -- belirli bir bellek dosyasını veya satır aralığını okur.

Her iki araç da etkin bellek plugin’i tarafından sağlanır (varsayılan: `memory-core`).

## Bellek araması

Bir embedding sağlayıcısı yapılandırıldığında, `memory_search` **hibrit arama** kullanır -- vektör benzerliğini (anlamsal anlam) anahtar kelime eşleştirmesiyle (kimlikler ve kod sembolleri gibi tam terimler) birleştirir. Desteklenen herhangi bir sağlayıcı için bir API anahtarınız olduğunda bu özellik kutudan çıktığı gibi çalışır.

<Info>
OpenClaw, kullanılabilir API anahtarlarından embedding sağlayıcınızı otomatik algılar. Yapılandırılmış bir OpenAI, Gemini, Voyage veya Mistral anahtarınız varsa, bellek araması otomatik olarak etkinleştirilir.
</Info>

Aramanın nasıl çalıştığı, ince ayar seçenekleri ve sağlayıcı kurulumu hakkında ayrıntılar için bkz. [Bellek Araması](/tr/concepts/memory-search).

## Bellek arka uçları

<CardGroup cols={3}>
<Card title="Yerleşik (varsayılan)" icon="database" href="/tr/concepts/memory-builtin">
SQLite tabanlıdır. Anahtar kelime araması, vektör benzerliği ve hibrit arama ile kutudan çıktığı gibi çalışır. Ek bağımlılık yoktur.
</Card>
<Card title="QMD" icon="search" href="/tr/concepts/memory-qmd">
Yeniden sıralama, sorgu genişletme ve çalışma alanı dışındaki dizinleri indeksleme yeteneğine sahip local-first yan hizmet.
</Card>
<Card title="Honcho" icon="brain" href="/tr/concepts/memory-honcho">
Kullanıcı modelleme, anlamsal arama ve çok aracılı farkındalık ile AI-native oturumlar arası bellek. Plugin kurulumu gerekir.
</Card>
</CardGroup>

## Otomatik bellek flush

[Compaction](/tr/concepts/compaction) konuşmanızı özetlemeden önce, OpenClaw araca önemli bağlamı bellek dosyalarına kaydetmesini hatırlatan sessiz bir tur çalıştırır. Bu varsayılan olarak açıktır -- herhangi bir şey yapılandırmanız gerekmez.

<Tip>
Bellek flush, sıkıştırma sırasında bağlam kaybını önler. Konuşmada henüz bir dosyaya yazılmamış önemli gerçekler varsa, özetleme gerçekleşmeden önce otomatik olarak kaydedilirler.
</Tip>

## Dreaming (deneysel)

Dreaming, bellek için isteğe bağlı bir arka plan pekiştirme geçişidir. Kısa vadeli sinyalleri toplar, adayları puanlar ve yalnızca uygun öğeleri uzun vadeli belleğe (`MEMORY.md`) yükseltir.

Uzun vadeli belleği yüksek sinyalli tutmak için tasarlanmıştır:

- **İsteğe bağlı**: varsayılan olarak devre dışıdır.
- **Zamanlanmış**: etkinleştirildiğinde `memory-core`, tam bir dreaming sweep için yinelenen bir cron işini otomatik olarak yönetir.
- **Eşikli**: yükseltmelerin puan, hatırlama sıklığı ve sorgu çeşitliliği kapılarını geçmesi gerekir.
- **İncelenebilir**: aşama özetleri ve günlük girdileri insan incelemesi için `DREAMS.md` dosyasına yazılır.

Aşama davranışı, puanlama sinyalleri ve Dream Diary ayrıntıları için bkz. [Dreaming (deneysel)](/concepts/dreaming).

## CLI

```bash
openclaw memory status          # İndeks durumunu ve sağlayıcıyı kontrol et
openclaw memory search "query"  # Komut satırından ara
openclaw memory index --force   # İndeksi yeniden oluştur
```

## Daha fazla okuma

- [Builtin Memory Engine](/tr/concepts/memory-builtin) -- varsayılan SQLite arka ucu
- [QMD Memory Engine](/tr/concepts/memory-qmd) -- gelişmiş local-first yan hizmet
- [Honcho Memory](/tr/concepts/memory-honcho) -- AI-native oturumlar arası bellek
- [Memory Search](/tr/concepts/memory-search) -- arama işlem hattı, sağlayıcılar ve ince ayar
- [Dreaming (experimental)](/concepts/dreaming) -- kısa vadeli hatırlamadan uzun vadeli belleğe arka plan yükseltme
- [Memory configuration reference](/tr/reference/memory-config) -- tüm yapılandırma ayarları
- [Compaction](/tr/concepts/compaction) -- sıkıştırmanın bellekle nasıl etkileşime girdiği
