---
read_when:
    - Belleğin nasıl çalıştığını anlamak istiyorsunuz
    - Hangi bellek dosyalarını yazmanız gerektiğini bilmek istiyorsunuz
summary: OpenClaw'ın oturumlar arasında şeyleri nasıl hatırladığı
title: Belleğe Genel Bakış
x-i18n:
    generated_at: "2026-04-15T14:40:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: ad1adafe1d81f1703d24f48a9c9da2b25a0ebbd4aad4f65d8bde5df78195d55b
    source_path: concepts/memory.md
    workflow: 15
---

# Belleğe Genel Bakış

OpenClaw, ajanınızın çalışma alanına **düz Markdown dosyaları** yazarak şeyleri hatırlar. Model yalnızca diske kaydedilenleri "hatırlar" -- gizli bir durum yoktur.

## Nasıl çalışır

Ajanınızın bellekle ilgili üç dosyası vardır:

- **`MEMORY.md`** -- uzun vadeli bellek. Kalıcı gerçekler, tercihler ve kararlar. Her DM oturumunun başında yüklenir.
- **`memory/YYYY-MM-DD.md`** -- günlük notlar. Devam eden bağlam ve gözlemler. Bugünün ve dünün notları otomatik olarak yüklenir.
- **`DREAMS.md`** (isteğe bağlı) -- insan incelemesi için Rüya Günlüğü ve Dreaming taraması özetleri; buna temellendirilmiş geçmişe dönük doldurma girdileri de dahildir.

Bu dosyalar ajan çalışma alanında bulunur (varsayılan `~/.openclaw/workspace`).

<Tip>
Ajanınızın bir şeyi hatırlamasını istiyorsanız, ona söylemeniz yeterlidir: "Remember that I
prefer TypeScript." Uygun dosyaya yazacaktır.
</Tip>

## Bellek araçları

Ajanın bellekle çalışmak için iki aracı vardır:

- **`memory_search`** -- ifade biçimi özgün metinden farklı olsa bile anlamsal aramayı kullanarak ilgili notları bulur.
- **`memory_get`** -- belirli bir bellek dosyasını veya satır aralığını okur.

Her iki araç da etkin bellek Plugin'i tarafından sağlanır (varsayılan: `memory-core`).

## Memory Wiki yardımcı Plugin'i

Kalıcı belleğin yalnızca ham notlar yerine bakımı yapılan bir bilgi tabanı gibi davranmasını istiyorsanız, paketle gelen `memory-wiki` Plugin'ini kullanın.

`memory-wiki`, kalıcı bilgileri şu özelliklere sahip bir wiki kasasına derler:

- deterministik sayfa yapısı
- yapılandırılmış iddialar ve kanıtlar
- çelişki ve güncellik takibi
- oluşturulmuş panolar
- ajan/çalışma zamanı tüketicileri için derlenmiş özetler
- `wiki_search`, `wiki_get`, `wiki_apply` ve `wiki_lint` gibi wiki-yerel araçlar

Etkin bellek Plugin'inin yerini almaz. Geri çağırma, yükseltme ve Dreaming süreçlerinin sahibi olmaya etkin bellek Plugin'i devam eder. `memory-wiki`, bunun yanına kaynak geçmişi açısından zengin bir bilgi katmanı ekler.

Bkz. [Memory Wiki](/tr/plugins/memory-wiki).

## Bellek araması

Bir embedding sağlayıcısı yapılandırıldığında, `memory_search` **hibrit arama** kullanır -- vektör benzerliğini (anlamsal anlam) anahtar sözcük eşleştirmesiyle (kimlikler ve kod sembolleri gibi tam terimler) birleştirir. Desteklenen herhangi bir sağlayıcı için bir API anahtarınız olduğunda bu özellik kutudan çıktığı gibi çalışır.

<Info>
OpenClaw, kullanılabilir API anahtarlarından embedding sağlayıcınızı otomatik olarak algılar. OpenAI, Gemini, Voyage veya Mistral anahtarınız yapılandırılmışsa bellek araması otomatik olarak etkinleştirilir.
</Info>

Aramanın nasıl çalıştığı, ayar seçenekleri ve sağlayıcı kurulumu hakkında ayrıntılar için bkz.
[Memory Search](/tr/concepts/memory-search).

## Bellek arka uçları

<CardGroup cols={3}>
<Card title="Yerleşik (varsayılan)" icon="database" href="/tr/concepts/memory-builtin">
SQLite tabanlıdır. Anahtar sözcük araması, vektör benzerliği ve hibrit arama ile kutudan çıktığı gibi çalışır. Ek bağımlılık gerekmez.
</Card>
<Card title="QMD" icon="search" href="/tr/concepts/memory-qmd">
Yeniden sıralama, sorgu genişletme ve çalışma alanı dışındaki dizinleri dizine ekleme yeteneğine sahip local loopback öncelikli yardımcı süreç.
</Card>
<Card title="Honcho" icon="brain" href="/tr/concepts/memory-honcho">
Kullanıcı modelleme, anlamsal arama ve çoklu ajan farkındalığına sahip yapay zeka yerel oturumlar arası bellek. Plugin kurulumu.
</Card>
</CardGroup>

## Bilgi wiki katmanı

<CardGroup cols={1}>
<Card title="Memory Wiki" icon="book" href="/tr/plugins/memory-wiki">
Kalıcı belleği; iddialar, panolar, köprü modu ve Obsidian dostu iş akışları içeren, kaynak geçmişi açısından zengin bir wiki kasasına derler.
</Card>
</CardGroup>

## Otomatik bellek boşaltma

[Compaction](/tr/concepts/compaction), konuşmanızı özetlemeden önce OpenClaw, ajana önemli bağlamı bellek dosyalarına kaydetmesini hatırlatan sessiz bir tur çalıştırır. Bu varsayılan olarak açıktır -- herhangi bir şey yapılandırmanız gerekmez.

<Tip>
Bellek boşaltma, Compaction sırasında bağlam kaybını önler. Ajanınızın konuşmada bulunan ancak henüz bir dosyaya yazılmamış önemli gerçekleri varsa, özetleme gerçekleşmeden önce bunlar otomatik olarak kaydedilir.
</Tip>

## Dreaming

Dreaming, bellek için isteğe bağlı bir arka plan pekiştirme geçişidir. Kısa vadeli sinyalleri toplar, adayları puanlar ve yalnızca uygun öğeleri uzun vadeli belleğe (`MEMORY.md`) yükseltir.

Uzun vadeli belleği yüksek sinyal düzeyinde tutmak için tasarlanmıştır:

- **İsteğe bağlı katılım**: varsayılan olarak devre dışıdır.
- **Zamanlanmış**: etkinleştirildiğinde `memory-core`, tam bir Dreaming taraması için yinelenen tek bir Cron işini otomatik olarak yönetir.
- **Eşikli**: yükseltmelerin puan, geri çağırma sıklığı ve sorgu çeşitliliği kapılarından geçmesi gerekir.
- **İncelenebilir**: aşama özetleri ve günlük girdileri, insan incelemesi için `DREAMS.md` dosyasına yazılır.

Aşama davranışı, puanlama sinyalleri ve Rüya Günlüğü ayrıntıları için bkz.
[Dreaming](/tr/concepts/dreaming).

## Temellendirilmiş geçmişe dönük doldurma ve canlı yükseltme

Dreaming sistemi artık birbiriyle yakından ilişkili iki inceleme hattına sahiptir:

- **Canlı Dreaming**, `memory/.dreams/` altındaki kısa vadeli Dreaming deposundan çalışır ve bir şeyin `MEMORY.md` içine yükselip yükselemeyeceğine karar verirken normal derin aşamanın kullandığı şeydir.
- **Temellendirilmiş geçmişe dönük doldurma**, geçmiş `memory/YYYY-MM-DD.md` notlarını bağımsız gün dosyaları olarak okur ve yapılandırılmış inceleme çıktısını `DREAMS.md` dosyasına yazar.

Temellendirilmiş geçmişe dönük doldurma, eski notları yeniden oynatmak ve sistemin dayanıklı olarak gördüğü şeyleri `MEMORY.md` dosyasını elle düzenlemeden incelemek istediğinizde yararlıdır.

Şunu kullandığınızda:

```bash
openclaw memory rem-backfill --path ./memory --stage-short-term
```

temellendirilmiş kalıcı adaylar doğrudan yükseltilmez. Bunun yerine, normal derin aşamanın zaten kullandığı aynı kısa vadeli Dreaming deposuna aşamalı olarak alınırlar. Bu şu anlama gelir:

- `DREAMS.md` insan inceleme yüzeyi olarak kalır.
- kısa vadeli depo makineye yönelik sıralama yüzeyi olarak kalır.
- `MEMORY.md` hâlâ yalnızca derin yükseltme tarafından yazılır.

Yeniden oynatmanın yararlı olmadığına karar verirseniz, sıradan günlük girdilerine veya normal geri çağırma durumuna dokunmadan aşamalı olarak alınmış yapıtları kaldırabilirsiniz:

```bash
openclaw memory rem-backfill --rollback
openclaw memory rem-backfill --rollback-short-term
```

## CLI

```bash
openclaw memory status          # Dizin durumunu ve sağlayıcıyı kontrol et
openclaw memory search "query"  # Komut satırından ara
openclaw memory index --force   # Dizini yeniden oluştur
```

## Daha fazla bilgi

- [Builtin Memory Engine](/tr/concepts/memory-builtin) -- varsayılan SQLite arka ucu
- [QMD Memory Engine](/tr/concepts/memory-qmd) -- gelişmiş local loopback öncelikli yardımcı süreç
- [Honcho Memory](/tr/concepts/memory-honcho) -- yapay zeka yerel oturumlar arası bellek
- [Memory Wiki](/tr/plugins/memory-wiki) -- derlenmiş bilgi kasası ve wiki-yerel araçlar
- [Memory Search](/tr/concepts/memory-search) -- arama ardışık düzeni, sağlayıcılar ve ayarlama
- [Dreaming](/tr/concepts/dreaming) -- kısa vadeli geri çağırmadan uzun vadeli belleğe arka plan yükseltmesi
- [Memory configuration reference](/tr/reference/memory-config) -- tüm yapılandırma seçenekleri
- [Compaction](/tr/concepts/compaction) -- Compaction'ın bellekle nasıl etkileşime girdiği
