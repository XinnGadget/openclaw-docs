---
read_when:
    - Oturum kimliklerini, transkript JSONL'yi veya sessions.json alanlarını hata ayıklamanız gerekiyor
    - Otomatik sıkıştırma davranışını değiştiriyorsunuz veya “pre-compaction” bakım işlemleri ekliyorsunuz
    - Bellek flush işlemlerini veya sessiz sistem dönüşlerini uygulamak istiyorsunuz
summary: 'Derin inceleme: oturum deposu + transkriptler, yaşam döngüsü ve (otomatik) sıkıştırma iç yapısı'
title: Oturum Yönetimi Derin İncelemesi
x-i18n:
    generated_at: "2026-04-07T08:49:49Z"
    model: gpt-5.4
    provider: openai
    source_hash: e379d624dd7808d3af25ed011079268ce6a9da64bb3f301598884ad4c46ab091
    source_path: reference/session-management-compaction.md
    workflow: 15
---

# Oturum Yönetimi ve Sıkıştırma (Derin İnceleme)

Bu belge, OpenClaw'ın oturumları uçtan uca nasıl yönettiğini açıklar:

- **Oturum yönlendirme** (gelen mesajların bir `sessionKey` değerine nasıl eşlendiği)
- **Oturum deposu** (`sessions.json`) ve neyi izlediği
- **Transkript kalıcılığı** (`*.jsonl`) ve yapısı
- **Transkript hijyeni** (çalıştırmalardan önce sağlayıcıya özgü düzeltmeler)
- **Bağlam sınırları** (bağlam penceresi ile izlenen token'lar)
- **Sıkıştırma** (manuel + otomatik sıkıştırma) ve sıkıştırma öncesi işleri nereye bağlayacağınız
- **Sessiz bakım işlemleri** (örneğin kullanıcıya görünür çıktı üretmemesi gereken bellek yazmaları)

Önce daha üst düzey bir genel bakış istiyorsanız, şunlarla başlayın:

- [/concepts/session](/tr/concepts/session)
- [/concepts/compaction](/tr/concepts/compaction)
- [/concepts/memory](/tr/concepts/memory)
- [/concepts/memory-search](/tr/concepts/memory-search)
- [/concepts/session-pruning](/tr/concepts/session-pruning)
- [/reference/transcript-hygiene](/tr/reference/transcript-hygiene)

---

## Doğruluğun kaynağı: Gateway

OpenClaw, oturum durumuna sahip olan tek bir **Gateway süreci** etrafında tasarlanmıştır.

- UI'lar (macOS uygulaması, web Control UI, TUI) oturum listeleri ve token sayıları için Gateway'e sorgu göndermelidir.
- Uzak modda, oturum dosyaları uzak host üzerindedir; “yerel Mac dosyalarınızı kontrol etmek”, Gateway'in ne kullandığını yansıtmaz.

---

## İki kalıcılık katmanı

OpenClaw, oturumları iki katmanda kalıcı hale getirir:

1. **Oturum deposu (`sessions.json`)**
   - Anahtar/değer eşlemesi: `sessionKey -> SessionEntry`
   - Küçük, değiştirilebilir, düzenlenmesi (veya girdilerin silinmesi) güvenlidir
   - Oturum meta verilerini izler (geçerli oturum kimliği, son etkinlik, anahtarlar, token sayaçları vb.)

2. **Transkript (`<sessionId>.jsonl`)**
   - Ağaç yapısına sahip append-only transkript (girdilerde `id` + `parentId` bulunur)
   - Gerçek konuşmayı + araç çağrılarını + sıkıştırma özetlerini depolar
   - Gelecek dönüşler için model bağlamını yeniden oluşturmak için kullanılır

---

## Disk üzerindeki konumlar

Gateway host üzerinde, ajan başına:

- Depo: `~/.openclaw/agents/<agentId>/sessions/sessions.json`
- Transkriptler: `~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl`
  - Telegram konu oturumları: `.../<sessionId>-topic-<threadId>.jsonl`

OpenClaw bunları `src/config/sessions.ts` üzerinden çözümler.

---

## Depo bakımı ve disk denetimleri

Oturum kalıcılığı, `sessions.json` ve transkript artifact'leri için otomatik bakım denetimlerine (`session.maintenance`) sahiptir:

- `mode`: `warn` (varsayılan) veya `enforce`
- `pruneAfter`: eski girdiler için yaş sınırı (varsayılan `30d`)
- `maxEntries`: `sessions.json` içindeki girdi sınırı (varsayılan `500`)
- `rotateBytes`: `sessions.json` çok büyüdüğünde döndür (varsayılan `10mb`)
- `resetArchiveRetention`: `*.reset.<timestamp>` transkript arşivleri için saklama süresi (varsayılan: `pruneAfter` ile aynı; `false` temizlemeyi devre dışı bırakır)
- `maxDiskBytes`: isteğe bağlı oturum dizini bütçesi
- `highWaterBytes`: temizleme sonrası isteğe bağlı hedef (varsayılan `maxDiskBytes` değerinin `%80`'i)

Disk bütçesi temizliği için uygulama sırası (`mode: "enforce"`):

1. Önce en eski arşivlenmiş veya yetim transkript artifact'lerini kaldır.
2. Hâlâ hedefin üzerindeyse, en eski oturum girdilerini ve transkript dosyalarını çıkar.
3. Kullanım `highWaterBytes` değerine eşit veya altına inene kadar devam et.

`mode: "warn"` durumunda OpenClaw olası çıkarmaları bildirir, ancak depo/dosyaları değiştirmez.

Bakımı isteğe bağlı olarak çalıştırın:

```bash
openclaw sessions cleanup --dry-run
openclaw sessions cleanup --enforce
```

---

## Cron oturumları ve çalıştırma günlükleri

Yalıtılmış cron çalıştırmaları da oturum girdileri/transkriptler oluşturur ve bunlar için özel saklama denetimleri vardır:

- `cron.sessionRetention` (varsayılan `24h`) eski yalıtılmış cron çalıştırma oturumlarını oturum deposundan temizler (`false` devre dışı bırakır).
- `cron.runLog.maxBytes` + `cron.runLog.keepLines`, `~/.openclaw/cron/runs/<jobId>.jsonl` dosyalarını temizler (varsayılanlar: `2_000_000` bayt ve `2000` satır).

---

## Oturum anahtarları (`sessionKey`)

Bir `sessionKey`, _hangi konuşma kovasında_ olduğunuzu tanımlar (yönlendirme + yalıtım).

Yaygın desenler:

- Ana/doğrudan sohbet (ajan başına): `agent:<agentId>:<mainKey>` (varsayılan `main`)
- Grup: `agent:<agentId>:<channel>:group:<id>`
- Oda/kanal (Discord/Slack): `agent:<agentId>:<channel>:channel:<id>` veya `...:room:<id>`
- Cron: `cron:<job.id>`
- Webhook: `hook:<uuid>` (geçersiz kılınmadıkça)

Kanonik kurallar [/concepts/session](/tr/concepts/session) içinde belgelenmiştir.

---

## Oturum kimlikleri (`sessionId`)

Her `sessionKey`, geçerli bir `sessionId` değerini işaret eder (konuşmayı sürdüren transkript dosyası).

Temel kurallar:

- **Sıfırlama** (`/new`, `/reset`), o `sessionKey` için yeni bir `sessionId` oluşturur.
- **Günlük sıfırlama** (varsayılan olarak gateway host üzerindeki yerel saatte sabah 4:00), sıfırlama sınırından sonraki ilk mesajda yeni bir `sessionId` oluşturur.
- **Boşta kalma süresi dolması** (`session.reset.idleMinutes` veya eski `session.idleMinutes`), bir mesaj boşta kalma penceresinden sonra geldiğinde yeni bir `sessionId` oluşturur. Günlük ve boşta kalma birlikte yapılandırıldığında, hangisinin süresi önce dolarsa o kazanır.
- **İş parçacığı üst ebeveyn çatallanma koruması** (`session.parentForkMaxTokens`, varsayılan `100000`), üst oturum zaten çok büyükse üst transkript çatallamasını atlar; yeni iş parçacığı temiz başlar. Devre dışı bırakmak için `0` ayarlayın.

Uygulama ayrıntısı: karar, `src/auto-reply/reply/session.ts` içindeki `initSessionState()` içinde verilir.

---

## Oturum deposu şeması (`sessions.json`)

Deponun değer türü, `src/config/sessions.ts` içindeki `SessionEntry`'dir.

Temel alanlar (tam liste değildir):

- `sessionId`: geçerli transkript kimliği (`sessionFile` ayarlanmadıysa dosya adı bundan türetilir)
- `updatedAt`: son etkinlik zaman damgası
- `sessionFile`: isteğe bağlı açık transkript yolu geçersiz kılması
- `chatType`: `direct | group | room` (UI'lara ve gönderim ilkesine yardımcı olur)
- `provider`, `subject`, `room`, `space`, `displayName`: grup/kanal etiketlemesi için meta veriler
- Anahtarlar:
  - `thinkingLevel`, `verboseLevel`, `reasoningLevel`, `elevatedLevel`
  - `sendPolicy` (oturum başına geçersiz kılma)
- Model seçimi:
  - `providerOverride`, `modelOverride`, `authProfileOverride`
- Token sayaçları (best-effort / sağlayıcıya bağlı):
  - `inputTokens`, `outputTokens`, `totalTokens`, `contextTokens`
- `compactionCount`: bu oturum anahtarı için otomatik sıkıştırmanın kaç kez tamamlandığı
- `memoryFlushAt`: son sıkıştırma öncesi bellek flush işleminin zaman damgası
- `memoryFlushCompactionCount`: son flush çalıştığında sıkıştırma sayısı

Deponun düzenlenmesi güvenlidir, ancak otoriteli olan Gateway'dir: oturumlar çalışırken girdileri yeniden yazabilir veya yeniden doldurabilir.

---

## Transkript yapısı (`*.jsonl`)

Transkriptler, `@mariozechner/pi-coding-agent` içindeki `SessionManager` tarafından yönetilir.

Dosya JSONL biçimindedir:

- İlk satır: oturum başlığı (`type: "session"`, `id`, `cwd`, `timestamp`, isteğe bağlı `parentSession` içerir)
- Sonra: `id` + `parentId` içeren oturum girdileri (ağaç)

Dikkat çeken girdi türleri:

- `message`: kullanıcı/asistan/toolResult mesajları
- `custom_message`: model bağlamına _giren_ uzantı eklemeli mesajlar (UI'dan gizlenebilir)
- `custom`: model bağlamına _girmeyen_ uzantı durumu
- `compaction`: `firstKeptEntryId` ve `tokensBefore` içeren kalıcı sıkıştırma özeti
- `branch_summary`: bir ağaç dalında gezinirken kalıcı özet

OpenClaw kasıtlı olarak transkriptleri **düzeltmez**; Gateway bunları okumak/yazmak için `SessionManager` kullanır.

---

## Bağlam pencereleri ve izlenen token'lar

İki farklı kavram önemlidir:

1. **Model bağlam penceresi**: model başına kesin sınır (modelin gördüğü token'lar)
2. **Oturum deposu sayaçları**: `sessions.json` içine yazılan döner istatistikler (`/status` ve paneller için kullanılır)

Sınırları ayarlıyorsanız:

- Bağlam penceresi model kataloğundan gelir (ve yapılandırma ile geçersiz kılınabilir).
- Depodaki `contextTokens`, çalışma zamanı tahmini/raporlama değeridir; bunu kesin bir garanti olarak ele almayın.

Daha fazla bilgi için bkz. [/token-use](/tr/reference/token-use).

---

## Sıkıştırma: nedir?

Sıkıştırma, eski konuşmayı transkriptte kalıcı bir `compaction` girdisi halinde özetler ve son mesajları bozulmadan korur.

Sıkıştırmadan sonra gelecek dönüşler şunları görür:

- Sıkıştırma özeti
- `firstKeptEntryId` sonrasındaki mesajlar

Sıkıştırma **kalıcıdır** (oturum budamasından farklı olarak). Bkz. [/concepts/session-pruning](/tr/concepts/session-pruning).

## Sıkıştırma parça sınırları ve araç eşleştirme

OpenClaw uzun bir transkripti sıkıştırma parçalarına böldüğünde,
asistan araç çağrılarını eşleşen `toolResult` girdileriyle eşlenmiş halde tutar.

- Token payı bölünmesi bir araç çağrısı ile sonucu arasına denk gelirse, OpenClaw
  çifti ayırmak yerine sınırı asistan araç çağrısı mesajına kaydırır.
- Sondaki bir tool-result bloğu parçayı hedefin üstüne taşıyacaksa,
  OpenClaw bekleyen bu araç bloğunu korur ve özetlenmemiş kuyruğu
  bozulmadan tutar.
- İptal edilen/hata veren araç çağrısı blokları bekleyen bir bölünmeyi açık tutmaz.

---

## Otomatik sıkıştırma ne zaman olur (Pi çalışma zamanı)

Gömülü Pi ajanında, otomatik sıkıştırma iki durumda tetiklenir:

1. **Taşma kurtarma**: model bir bağlam taşması hatası döndürür
   (`request_too_large`, `context length exceeded`, `input exceeds the maximum
number of tokens`, `input token count exceeds the maximum number of input
tokens`, `input is too long for the model`, `ollama error: context length
exceeded` ve benzeri sağlayıcı biçimli varyantlar) → sıkıştır → yeniden dene.
2. **Eşik bakımı**: başarılı bir dönüşten sonra, şu durumda:

`contextTokens > contextWindow - reserveTokens`

Burada:

- `contextWindow`, modelin bağlam penceresidir
- `reserveTokens`, istemler + sonraki model çıktısı için ayrılmış boşluktur

Bunlar Pi çalışma zamanı semantiğidir (OpenClaw olayları tüketir, ancak ne zaman sıkıştırılacağına Pi karar verir).

---

## Sıkıştırma ayarları (`reserveTokens`, `keepRecentTokens`)

Pi'nin sıkıştırma ayarları Pi ayarlarında bulunur:

```json5
{
  compaction: {
    enabled: true,
    reserveTokens: 16384,
    keepRecentTokens: 20000,
  },
}
```

OpenClaw ayrıca gömülü çalıştırmalar için bir güvenlik tabanı uygular:

- `compaction.reserveTokens < reserveTokensFloor` ise OpenClaw bunu yükseltir.
- Varsayılan taban `20000` token'dır.
- Tabanı devre dışı bırakmak için `agents.defaults.compaction.reserveTokensFloor: 0` ayarlayın.
- Zaten daha yüksekse, OpenClaw buna dokunmaz.

Neden: sıkıştırma kaçınılmaz hale gelmeden önce çok dönüşlü “bakım işlemleri” (bellek yazmaları gibi) için yeterli boşluk bırakmak.

Uygulama: `src/agents/pi-settings.ts` içindeki `ensurePiCompactionReserveTokens()`
(`src/agents/pi-embedded-runner.ts` içinden çağrılır).

---

## Kullanıcıya görünür yüzeyler

Sıkıştırmayı ve oturum durumunu şu yollarla gözlemleyebilirsiniz:

- `/status` (herhangi bir sohbet oturumunda)
- `openclaw status` (CLI)
- `openclaw sessions` / `sessions --json`
- Ayrıntılı mod: `🧹 Auto-compaction complete` + sıkıştırma sayısı

---

## Sessiz bakım işlemleri (`NO_REPLY`)

OpenClaw, kullanıcıya ara çıktıların görünmemesi gereken arka plan görevleri için “sessiz” dönüşleri destekler.

Kural:

- Asistan, “kullanıcıya yanıt iletme” anlamına gelen tam sessiz belirteç `NO_REPLY` /
  `no_reply` ile çıktısına başlar.
- OpenClaw bunu iletim katmanında ayıklar/bastırır.
- Tam sessiz belirteç bastırması büyük/küçük harfe duyarsızdır; yani tüm payload yalnızca sessiz belirteçten oluştuğunda `NO_REPLY` ve
  `no_reply` her ikisi de geçerlidir.
- Bu yalnızca gerçek arka plan/iletimsiz dönüşler içindir; sıradan eyleme geçirilebilir kullanıcı istekleri için bir kısayol değildir.

`2026.1.10` itibarıyla OpenClaw, kısmi bir parça `NO_REPLY` ile başladığında **taslak/yazıyor streaming** davranışını da bastırır; böylece sessiz işlemler dönüş ortasında kısmi çıktı sızdırmaz.

---

## Sıkıştırma öncesi "memory flush" (uygulandı)

Amaç: otomatik sıkıştırma gerçekleşmeden önce, kritik bağlamı
sıkıştırma silemesin diye diske kalıcı durum yazan (örneğin ajan çalışma alanındaki `memory/YYYY-MM-DD.md`) sessiz bir agentsel dönüş çalıştırmak.

OpenClaw **eşik öncesi flush** yaklaşımını kullanır:

1. Oturum bağlam kullanımını izle.
2. Bir “yumuşak eşiği” aştığında (Pi'nin sıkıştırma eşiğinin altında), ajana sessiz bir
   “şimdi belleği yaz” yönergesi çalıştır.
3. Kullanıcının hiçbir şey görmemesi için tam sessiz belirteç `NO_REPLY` / `no_reply` kullan.

Yapılandırma (`agents.defaults.compaction.memoryFlush`):

- `enabled` (varsayılan: `true`)
- `softThresholdTokens` (varsayılan: `4000`)
- `prompt` (flush dönüşü için kullanıcı mesajı)
- `systemPrompt` (flush dönüşüne eklenen ek sistem istemi)

Notlar:

- Varsayılan prompt/system prompt, iletimi bastırmak için bir `NO_REPLY` ipucu içerir.
- Flush, sıkıştırma döngüsü başına bir kez çalışır (`sessions.json` içinde izlenir).
- Flush yalnızca gömülü Pi oturumlarında çalışır (CLI backend'leri bunu atlar).
- Oturum çalışma alanı salt okunursa flush atlanır (`workspaceAccess: "ro"` veya `"none"`).
- Çalışma alanı dosya düzeni ve yazma kalıpları için bkz. [Memory](/tr/concepts/memory).

Pi, uzantı API'sinde ayrıca bir `session_before_compact` hook'u da sunar, ancak OpenClaw'ın
flush mantığı bugün Gateway tarafında yaşar.

---

## Sorun giderme kontrol listesi

- Oturum anahtarı yanlış mı? [/concepts/session](/tr/concepts/session) ile başlayın ve `/status` içindeki `sessionKey` değerini doğrulayın.
- Depo ile transkript uyuşmuyor mu? `openclaw status` çıktısından Gateway host'u ve depo yolunu doğrulayın.
- Sıkıştırma spam'i mi var? Şunları kontrol edin:
  - model bağlam penceresi (çok küçük olabilir)
  - sıkıştırma ayarları (model penceresi için `reserveTokens` çok yüksekse daha erken sıkıştırmaya neden olabilir)
  - tool-result şişmesi: oturum budamayı etkinleştirin/ayarlayın
- Sessiz dönüşler sızıyor mu? Yanıtın `NO_REPLY` ile başladığını (büyük/küçük harfe duyarsız tam belirteç) ve streaming bastırma düzeltmesini içeren bir derleme kullandığınızı doğrulayın.
