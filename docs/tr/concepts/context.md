---
read_when:
    - OpenClaw içinde “bağlam”ın ne anlama geldiğini anlamak istiyorsunuz
    - Modelin neden bir şeyi “bildiğini” (veya unuttuğunu) hata ayıklıyorsunuz
    - Bağlam ek yükünü azaltmak istiyorsunuz (/context, /status, /compact)
summary: 'Bağlam: modelin ne gördüğü, nasıl oluşturulduğu ve nasıl inceleneceği'
title: Bağlam
x-i18n:
    generated_at: "2026-04-06T03:06:20Z"
    model: gpt-5.4
    provider: openai
    source_hash: fe7dfe52cb1a64df229c8622feed1804df6c483a6243e0d2f309f6ff5c9fe521
    source_path: concepts/context.md
    workflow: 15
---

# Bağlam

“Bağlam”, **OpenClaw’un bir çalıştırma için modele gönderdiği her şeydir**. Modelin **bağlam penceresi** (token sınırı) ile sınırlıdır.

Yeni başlayanlar için zihinsel model:

- **Sistem komutu** (OpenClaw tarafından oluşturulur): kurallar, araçlar, skills listesi, zaman/çalışma zamanı ve enjekte edilen çalışma alanı dosyaları.
- **Konuşma geçmişi**: bu oturum için sizin mesajlarınız + asistanın mesajları.
- **Araç çağrıları/sonuçları + ekler**: komut çıktısı, dosya okumaları, görseller/ses vb.

Bağlam, “bellek” ile _aynı şey değildir_: bellek diskte saklanıp daha sonra yeniden yüklenebilir; bağlam ise modelin mevcut penceresinin içindedir.

## Hızlı başlangıç (bağlamı inceleme)

- `/status` → “pencerem ne kadar dolu?” için hızlı görünüm + oturum ayarları.
- `/context list` → neyin enjekte edildiği + yaklaşık boyutlar (dosya başına + toplamlar).
- `/context detail` → daha ayrıntılı döküm: dosya başına, araç şeması başına, skill girdisi başına boyutlar ve sistem komutu boyutu.
- `/usage tokens` → normal yanıtlara yanıt başına kullanım altbilgisi ekler.
- `/compact` → pencere alanı boşaltmak için eski geçmişi kompakt bir girdide özetler.

Ayrıca bkz.: [Slash komutları](/tr/tools/slash-commands), [Token kullanımı ve maliyetler](/tr/reference/token-use), [Sıkıştırma](/tr/concepts/compaction).

## Çıktı örneği

Değerler modele, sağlayıcıya, araç ilkesine ve çalışma alanınızda ne olduğuna göre değişir.

### `/context list`

```
🧠 Bağlam dökümü
Çalışma alanı: <workspaceDir>
Önyükleme maks/dosya: 20,000 karakter
Sandbox: mode=non-main sandboxed=false
Sistem komutu (çalıştırma): 38,412 karakter (~9,603 tok) (Proje Bağlamı 23,901 karakter (~5,976 tok))

Enjekte edilen çalışma alanı dosyaları:
- AGENTS.md: TAMAM | ham 1,742 karakter (~436 tok) | enjekte edilen 1,742 karakter (~436 tok)
- SOUL.md: TAMAM | ham 912 karakter (~228 tok) | enjekte edilen 912 karakter (~228 tok)
- TOOLS.md: KESİLDİ | ham 54,210 karakter (~13,553 tok) | enjekte edilen 20,962 karakter (~5,241 tok)
- IDENTITY.md: TAMAM | ham 211 karakter (~53 tok) | enjekte edilen 211 karakter (~53 tok)
- USER.md: TAMAM | ham 388 karakter (~97 tok) | enjekte edilen 388 karakter (~97 tok)
- HEARTBEAT.md: EKSİK | ham 0 | enjekte edilen 0
- BOOTSTRAP.md: TAMAM | ham 0 karakter (~0 tok) | enjekte edilen 0 karakter (~0 tok)

Skills listesi (sistem komutu metni): 2,184 karakter (~546 tok) (12 skill)
Araçlar: read, edit, write, exec, process, browser, message, sessions_send, …
Araç listesi (sistem komutu metni): 1,032 karakter (~258 tok)
Araç şemaları (JSON): 31,988 karakter (~7,997 tok) (bağlama dahil edilir; metin olarak gösterilmez)
Araçlar: (yukarıdakiyle aynı)

Oturum tokenları (önbelleğe alınmış): toplam 14,250 / ctx=32,000
```

### `/context detail`

```
🧠 Bağlam dökümü (ayrıntılı)
…
En büyük skills (komut girdisi boyutu):
- frontend-design: 412 karakter (~103 tok)
- oracle: 401 karakter (~101 tok)
… (+10 tane daha skill)

En büyük araçlar (şema boyutu):
- browser: 9,812 karakter (~2,453 tok)
- exec: 6,240 karakter (~1,560 tok)
… (+N tane daha araç)
```

## Bağlam penceresine neler dahil edilir

Modele gelen her şey buna dahildir, örneğin:

- Sistem komutu (tüm bölümler).
- Konuşma geçmişi.
- Araç çağrıları + araç sonuçları.
- Ekler/dökümler (görseller/ses/dosyalar).
- Sıkıştırma özetleri ve budama yapıtları.
- Sağlayıcı “sarmalayıcıları” veya gizli üstbilgiler (görünmezler, yine de sayılırlar).

## OpenClaw sistem komutunu nasıl oluşturur

Sistem komutu **OpenClaw’a aittir** ve her çalıştırmada yeniden oluşturulur. Şunları içerir:

- Araç listesi + kısa açıklamalar.
- Skills listesi (yalnızca meta veriler; aşağıya bakın).
- Çalışma alanı konumu.
- Zaman (UTC + yapılandırılmışsa dönüştürülmüş kullanıcı saati).
- Çalışma zamanı meta verileri (host/OS/model/thinking).
- **Project Context** altındaki enjekte edilen çalışma alanı önyükleme dosyaları.

Tam döküm: [System Prompt](/tr/concepts/system-prompt).

## Enjekte edilen çalışma alanı dosyaları (Project Context)

Varsayılan olarak OpenClaw, sabit bir çalışma alanı dosyaları kümesini enjekte eder (varsa):

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md` (yalnızca ilk çalıştırmada)

Büyük dosyalar, `agents.defaults.bootstrapMaxChars` kullanılarak dosya başına kesilir (varsayılan `20000` karakter). OpenClaw ayrıca dosyalar genelinde toplam önyükleme enjeksiyonu için `agents.defaults.bootstrapTotalMaxChars` ile toplam bir üst sınır uygular (varsayılan `150000` karakter). `/context`, **ham ve enjekte edilen** boyutları ve kesme olup olmadığını gösterir.

Kesme olduğunda, çalışma zamanı Project Context altında komut içi bir uyarı bloğu enjekte edebilir. Bunu `agents.defaults.bootstrapPromptTruncationWarning` ile yapılandırın (`off`, `once`, `always`; varsayılan `once`).

## Skills: enjekte edilenler ve isteğe bağlı yüklenenler

Sistem komutu kompakt bir **skills listesi** içerir (ad + açıklama + konum). Bu listenin gerçek bir ek yükü vardır.

Skill yönergeleri varsayılan olarak _dahil edilmez_. Modelin, skill’in `SKILL.md` dosyasını **yalnızca gerektiğinde** `read` ile okuması beklenir.

## Araçlar: iki tür maliyet vardır

Araçlar bağlamı iki şekilde etkiler:

1. Sistem komutundaki **araç listesi metni** (gördüğünüz “Tooling”).
2. **Araç şemaları** (JSON). Modelin araç çağırabilmesi için bunlar modele gönderilir. Düz metin olarak görmeseniz bile bağlama dahil edilirler.

`/context detail`, en büyük araç şemalarını döker; böylece baskın olanları görebilirsiniz.

## Komutlar, yönergeler ve "satır içi kısayollar"

Slash komutları Gateway tarafından işlenir. Birkaç farklı davranış vardır:

- **Bağımsız komutlar**: yalnızca `/...` olan bir mesaj komut olarak çalıştırılır.
- **Yönergeler**: `/think`, `/verbose`, `/reasoning`, `/elevated`, `/model`, `/queue`, model mesajı görmeden önce ayıklanır.
  - Yalnızca yönerge içeren mesajlar oturum ayarlarını kalıcı hale getirir.
  - Normal bir mesaj içindeki satır içi yönergeler, mesaj başına ipucu işlevi görür.
- **Satır içi kısayollar** (yalnızca izin verilen göndericiler): normal bir mesaj içindeki bazı `/...` belirteçleri hemen çalışabilir (örnek: “hey /status”) ve model kalan metni görmeden önce ayıklanır.

Ayrıntılar: [Slash komutları](/tr/tools/slash-commands).

## Oturumlar, sıkıştırma ve budama (kalıcı olanlar)

Mesajlar arasında neyin kalıcı olduğu kullanılan mekanizmaya bağlıdır:

- **Normal geçmiş**, ilke gereği sıkıştırılana/budanana kadar oturum dökümünde kalıcı olur.
- **Sıkıştırma**, özeti döküme kalıcı olarak yazar ve son mesajları bozulmadan tutar.
- **Budama**, bir çalıştırma için _bellek içi_ komuttan eski araç sonuçlarını kaldırır, ancak dökümü yeniden yazmaz.

Belgeler: [Session](/tr/concepts/session), [Compaction](/tr/concepts/compaction), [Session pruning](/tr/concepts/session-pruning).

Varsayılan olarak OpenClaw, birleştirme ve sıkıştırma için yerleşik `legacy` bağlam motorunu kullanır. `kind: "context-engine"` sağlayan bir plugin yüklerseniz ve bunu `plugins.slots.contextEngine` ile seçerseniz, OpenClaw bağlam birleştirmeyi, `/compact` işlemini ve ilgili alt aracı bağlam yaşam döngüsü kancalarını bunun yerine o motora devreder. `ownsCompaction: false`, `legacy` motora otomatik geri dönüş sağlamaz; etkin motorun yine de `compact()` işlevini doğru şekilde uygulaması gerekir. Tam takılabilir arayüz, yaşam döngüsü kancaları ve yapılandırma için [Context Engine](/tr/concepts/context-engine) sayfasına bakın.

## `/context` gerçekte ne raporlar

`/context`, mümkün olduğunda en son **çalıştırma sırasında oluşturulmuş** sistem komutu raporunu tercih eder:

- `System prompt (run)` = son gömülü (araç çağırabilen) çalıştırmadan alınır ve oturum deposunda kalıcı olarak saklanır.
- `System prompt (estimate)` = henüz bir çalıştırma raporu yoksa anlık olarak hesaplanır.

Her iki durumda da boyutları ve en büyük katkıda bulunanları raporlar; tam sistem komutunu veya araç şemalarını dökmez.

## İlgili

- [Context Engine](/tr/concepts/context-engine) — plugin’ler aracılığıyla özel bağlam enjeksiyonu
- [Compaction](/tr/concepts/compaction) — uzun konuşmaları özetleme
- [System Prompt](/tr/concepts/system-prompt) — sistem komutunun nasıl oluşturulduğu
- [Agent Loop](/tr/concepts/agent-loop) — tam ajan yürütme döngüsü
