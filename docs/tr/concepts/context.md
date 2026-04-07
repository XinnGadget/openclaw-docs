---
read_when:
    - OpenClaw'da “bağlam”ın ne anlama geldiğini anlamak istiyorsunuz
    - Modelin neden bir şeyi “bildiğini” (veya unuttuğunu) hata ayıklıyorsunuz
    - Bağlam ek yükünü azaltmak istiyorsunuz (/context, /status, /compact)
summary: 'Bağlam: modelin ne gördüğü, nasıl oluşturulduğu ve nasıl inceleneceği'
title: Bağlam
x-i18n:
    generated_at: "2026-04-07T08:43:49Z"
    model: gpt-5.4
    provider: openai
    source_hash: a75b4cd65bf6385d46265b9ce1643310bc99d220e35ec4b4924096bed3ca4aa0
    source_path: concepts/context.md
    workflow: 15
---

# Bağlam

“Bağlam”, **OpenClaw'ın bir çalıştırma için modele gönderdiği her şeydir**. Modelin **bağlam penceresi** (token sınırı) ile sınırlıdır.

Başlangıç düzeyi zihinsel model:

- **System prompt** (OpenClaw tarafından oluşturulur): kurallar, araçlar, Skills listesi, zaman/çalışma zamanı ve enjekte edilen çalışma alanı dosyaları.
- **Konuşma geçmişi**: bu oturum için sizin mesajlarınız + asistanın mesajları.
- **Araç çağrıları/sonuçları + ekler**: komut çıktısı, dosya okumaları, görüntüler/ses, vb.

Bağlam, “hafıza” ile _aynı şey değildir_: hafıza diskte saklanıp daha sonra yeniden yüklenebilir; bağlam ise modelin mevcut penceresinin içinde olan şeydir.

## Hızlı başlangıç (bağlamı inceleme)

- `/status` → “pencerem ne kadar dolu?” için hızlı görünüm + oturum ayarları.
- `/context list` → neyin enjekte edildiği + yaklaşık boyutlar (dosya başına + toplamlar).
- `/context detail` → daha ayrıntılı döküm: dosya başına, araç şeması başına, skill girdisi başına boyutlar ve system prompt boyutu.
- `/usage tokens` → normal yanıtlara yanıt başına kullanım altbilgisi ekler.
- `/compact` → pencere alanı açmak için eski geçmişi kompakt bir girdide özetler.

Ayrıca bkz.: [Slash commands](/tr/tools/slash-commands), [Token use & costs](/tr/reference/token-use), [Compaction](/tr/concepts/compaction).

## Örnek çıktı

Değerler modele, sağlayıcıya, araç ilkesine ve çalışma alanınızda ne olduğuna göre değişir.

### `/context list`

```
🧠 Context breakdown
Workspace: <workspaceDir>
Bootstrap max/file: 20,000 chars
Sandbox: mode=non-main sandboxed=false
System prompt (run): 38,412 chars (~9,603 tok) (Project Context 23,901 chars (~5,976 tok))

Injected workspace files:
- AGENTS.md: OK | raw 1,742 chars (~436 tok) | injected 1,742 chars (~436 tok)
- SOUL.md: OK | raw 912 chars (~228 tok) | injected 912 chars (~228 tok)
- TOOLS.md: TRUNCATED | raw 54,210 chars (~13,553 tok) | injected 20,962 chars (~5,241 tok)
- IDENTITY.md: OK | raw 211 chars (~53 tok) | injected 211 chars (~53 tok)
- USER.md: OK | raw 388 chars (~97 tok) | injected 388 chars (~97 tok)
- HEARTBEAT.md: MISSING | raw 0 | injected 0
- BOOTSTRAP.md: OK | raw 0 chars (~0 tok) | injected 0 chars (~0 tok)

Skills list (system prompt text): 2,184 chars (~546 tok) (12 skills)
Tools: read, edit, write, exec, process, browser, message, sessions_send, …
Tool list (system prompt text): 1,032 chars (~258 tok)
Tool schemas (JSON): 31,988 chars (~7,997 tok) (counts toward context; not shown as text)
Tools: (same as above)

Session tokens (cached): 14,250 total / ctx=32,000
```

### `/context detail`

```
🧠 Context breakdown (detailed)
…
Top skills (prompt entry size):
- frontend-design: 412 chars (~103 tok)
- oracle: 401 chars (~101 tok)
… (+10 more skills)

Top tools (schema size):
- browser: 9,812 chars (~2,453 tok)
- exec: 6,240 chars (~1,560 tok)
… (+N more tools)
```

## Bağlam penceresine neler dahil edilir

Modelin aldığı her şey dahildir; buna şunlar da dahil:

- System prompt (tüm bölümler).
- Konuşma geçmişi.
- Araç çağrıları + araç sonuçları.
- Ekler/transkriptler (görüntüler/ses/dosyalar).
- Compaction özetleri ve budama artıkları.
- Sağlayıcı “sarmalayıcıları” veya gizli üst bilgiler (görünmezler, yine de sayılırlar).

## OpenClaw system prompt'u nasıl oluşturur

System prompt, **OpenClaw'a aittir** ve her çalıştırmada yeniden oluşturulur. Şunları içerir:

- Araç listesi + kısa açıklamalar.
- Skills listesi (yalnızca meta veriler; aşağıya bakın).
- Çalışma alanı konumu.
- Zaman (UTC + yapılandırılmışsa dönüştürülmüş kullanıcı saati).
- Çalışma zamanı meta verileri (ana bilgisayar/OS/model/düşünme).
- **Project Context** altındaki enjekte edilmiş çalışma alanı bootstrap dosyaları.

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

Büyük dosyalar, `agents.defaults.bootstrapMaxChars` (varsayılan `20000` karakter) kullanılarak dosya başına kısaltılır. OpenClaw ayrıca dosyalar genelinde toplam bootstrap enjeksiyonu için `agents.defaults.bootstrapTotalMaxChars` (varsayılan `150000` karakter) ile bir üst sınır uygular. `/context`, **ham ve enjekte edilmiş** boyutları ve kısaltma olup olmadığını gösterir.

Kısaltma olduğunda, çalışma zamanı Project Context altında prompt içinde bir uyarı bloğu enjekte edebilir. Bunu `agents.defaults.bootstrapPromptTruncationWarning` ile yapılandırın (`off`, `once`, `always`; varsayılan `once`).

## Skills: enjekte edilenler ve isteğe bağlı yüklenenler

System prompt, kompakt bir **skills listesi** içerir (ad + açıklama + konum). Bu listenin gerçek bir ek yükü vardır.

Skill talimatları varsayılan olarak dahil edilmez. Modelin, skill'in `SKILL.md` dosyasını **yalnızca gerektiğinde** `read` ile okuması beklenir.

## Araçlar: iki maliyet vardır

Araçlar bağlamı iki şekilde etkiler:

1. System prompt içindeki **araç listesi metni** ("Tooling" olarak gördüğünüz şey).
2. **Araç şemaları** (JSON). Bunlar, araç çağırabilmesi için modele gönderilir. Düz metin olarak görmeseniz de bağlama dahil edilirler.

`/context detail`, neyin baskın olduğunu görebilmeniz için en büyük araç şemalarını dökümler.

## Komutlar, yönergeler ve "satır içi kısayollar"

Slash komutları Gateway tarafından işlenir. Birkaç farklı davranış vardır:

- **Bağımsız komutlar**: yalnızca `/...` olan bir mesaj komut olarak çalıştırılır.
- **Yönergeler**: `/think`, `/verbose`, `/reasoning`, `/elevated`, `/model`, `/queue`, model mesajı görmeden önce ayıklanır.
  - Yalnızca yönergeden oluşan mesajlar oturum ayarlarını kalıcı hale getirir.
  - Normal bir mesajdaki satır içi yönergeler, mesaj başına ipucu olarak davranır.
- **Satır içi kısayollar** (yalnızca izin verilen gönderenler): normal bir mesajın içindeki belirli `/...` belirteçleri hemen çalışabilir (örnek: “hey /status”) ve kalan metni model görmeden önce ayıklanır.

Ayrıntılar: [Slash commands](/tr/tools/slash-commands).

## Oturumlar, compaction ve budama (neler kalıcıdır)

Mekanizmaya bağlı olarak mesajlar arasında kalıcı olanlar değişir:

- **Normal geçmiş**, ilkeye göre compacted/pruned yapılana kadar oturum transkriptinde kalır.
- **Compaction**, transkripte bir özet ekler ve son mesajları olduğu gibi tutar.
- **Budama**, bir çalıştırma için _bellek içi_ prompt'tan eski araç sonuçlarını kaldırır, ancak transkripti yeniden yazmaz.

Belgeler: [Session](/tr/concepts/session), [Compaction](/tr/concepts/compaction), [Session pruning](/tr/concepts/session-pruning).

Varsayılan olarak OpenClaw, derleme ve compaction için yerleşik `legacy` bağlam motorunu kullanır. `kind: "context-engine"` sağlayan bir plugin yüklerseniz ve bunu `plugins.slots.contextEngine` ile seçerseniz, OpenClaw bağlam derlemeyi, `/compact` işlemini ve ilgili alt temsilci bağlam yaşam döngüsü kancalarını bunun yerine o motora devreder. `ownsCompaction: false`, otomatik olarak legacy motora geri dönüş yapmaz; etkin motorun yine de `compact()` işlevini doğru uygulaması gerekir. Tam takılabilir arayüz, yaşam döngüsü kancaları ve yapılandırma için [Context Engine](/tr/concepts/context-engine) sayfasına bakın.

## `/context` gerçekte ne raporlar

`/context`, mümkün olduğunda en son **çalıştırmada oluşturulmuş** system prompt raporunu tercih eder:

- `System prompt (run)` = son gömülü (araç kullanabilen) çalıştırmadan alınmış ve oturum deposunda kalıcı olarak saklanmış rapor.
- `System prompt (estimate)` = çalıştırma raporu olmadığında (veya raporu üretmeyen bir CLI arka ucu üzerinden çalışırken) anlık olarak hesaplanır.

Her iki durumda da boyutları ve en büyük katkı sağlayanları raporlar; tam system prompt'u veya araç şemalarını **dökmez**.

## İlgili

- [Context Engine](/tr/concepts/context-engine) — plugin'ler aracılığıyla özel bağlam enjeksiyonu
- [Compaction](/tr/concepts/compaction) — uzun konuşmaların özetlenmesi
- [System Prompt](/tr/concepts/system-prompt) — system prompt'un nasıl oluşturulduğu
- [Agent Loop](/tr/concepts/agent-loop) — tam temsilci yürütme döngüsü
