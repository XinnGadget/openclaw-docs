---
read_when:
    - Oturum kimliklerini, transcript JSONL'yi veya sessions.json alanlarını hata ayıklamanız gerekiyor
    - Otomatik sıkıştırma davranışını değiştiriyorsunuz veya “sıkıştırma öncesi” bakım işleri ekliyorsunuz
    - Bellek temizlemeleri veya sessiz sistem dönüşleri uygulamak istiyorsunuz
summary: 'Derin inceleme: oturum deposu + transcript''ler, yaşam döngüsü ve (otomatik) sıkıştırma iç yapıları'
title: Oturum Yönetimi Derin İncelemesi
x-i18n:
    generated_at: "2026-04-06T03:12:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: e0d8c2d30be773eac0424f7a4419ab055fdd50daac8bc654e7d250c891f2c3b8
    source_path: reference/session-management-compaction.md
    workflow: 15
---

# Oturum Yönetimi ve Sıkıştırma (Derin İnceleme)

Bu belge, OpenClaw'ın oturumları uçtan uca nasıl yönettiğini açıklar:

- **Oturum yönlendirme** (gelen mesajların bir `sessionKey` değerine nasıl eşlendiği)
- **Oturum deposu** (`sessions.json`) ve neyi izlediği
- **Transcript kalıcılığı** (`*.jsonl`) ve yapısı
- **Transcript hijyeni** (çalıştırmalar öncesi sağlayıcıya özgü düzeltmeler)
- **Bağlam sınırları** (bağlam penceresi ile izlenen token'lar)
- **Sıkıştırma** (el ile + otomatik sıkıştırma) ve sıkıştırma öncesi işlerin nereye bağlanacağı
- **Sessiz bakım işleri** (ör. kullanıcıya görünür çıktı üretmemesi gereken bellek yazımları)

Önce daha yüksek seviyeli bir genel bakış istiyorsanız şuradan başlayın:

- [/concepts/session](/tr/concepts/session)
- [/concepts/compaction](/tr/concepts/compaction)
- [/concepts/memory](/tr/concepts/memory)
- [/concepts/memory-search](/tr/concepts/memory-search)
- [/concepts/session-pruning](/tr/concepts/session-pruning)
- [/reference/transcript-hygiene](/tr/reference/transcript-hygiene)

---

## Doğruluk kaynağı: Gateway

OpenClaw, oturum durumuna sahip olan tek bir **Gateway süreci** etrafında tasarlanmıştır.

- UI'lar (macOS uygulaması, web Control UI, TUI), oturum listeleri ve token sayıları için Gateway'e sorgu yapmalıdır.
- Uzak modda oturum dosyaları uzak ana bilgisayarda bulunur; “yerel Mac dosyalarınızı kontrol etmek” Gateway'in ne kullandığını yansıtmaz.

---

## İki kalıcılık katmanı

OpenClaw oturumları iki katmanda kalıcı hale getirir:

1. **Oturum deposu (`sessions.json`)**
   - Anahtar/değer eşlemesi: `sessionKey -> SessionEntry`
   - Küçük, değiştirilebilir, düzenlemesi güvenli (veya girdiler silinebilir)
   - Oturum meta verilerini izler (geçerli oturum kimliği, son etkinlik, anahtarlar, token sayaçları vb.)

2. **Transcript (`<sessionId>.jsonl`)**
   - Ağaç yapılı salt ekleme transcript (girdiler `id` + `parentId` içerir)
   - Gerçek konuşmayı + araç çağrılarını + sıkıştırma özetlerini saklar
   - Gelecekteki dönüşler için model bağlamını yeniden oluşturmakta kullanılır

---

## Disk üzerindeki konumlar

Her ajan için, Gateway ana bilgisayarında:

- Depo: `~/.openclaw/agents/<agentId>/sessions/sessions.json`
- Transcript'ler: `~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl`
  - Telegram konu oturumları: `.../<sessionId>-topic-<threadId>.jsonl`

OpenClaw bunları `src/config/sessions.ts` üzerinden çözer.

---

## Depo bakımı ve disk denetimleri

Oturum kalıcılığında, `sessions.json` ve transcript artifaktları için otomatik bakım denetimleri (`session.maintenance`) bulunur:

- `mode`: `warn` (varsayılan) veya `enforce`
- `pruneAfter`: eski girdi yaş eşiği (varsayılan `30d`)
- `maxEntries`: `sessions.json` içindeki girdi üst sınırı (varsayılan `500`)
- `rotateBytes`: `sessions.json` aşırı büyüdüğünde döndür (varsayılan `10mb`)
- `resetArchiveRetention`: `*.reset.<timestamp>` transcript arşivleri için saklama süresi (varsayılan: `pruneAfter` ile aynı; `false` temizlemeyi devre dışı bırakır)
- `maxDiskBytes`: isteğe bağlı oturumlar dizini bütçesi
- `highWaterBytes`: temizlik sonrası isteğe bağlı hedef (varsayılan `maxDiskBytes` değerinin `%80`'i)

Disk bütçesi temizliği için uygulama sırası (`mode: "enforce"`):

1. Önce en eski arşivlenmiş veya sahipsiz transcript artifaktlarını kaldır.
2. Hâlâ hedefin üzerindeyse, en eski oturum girdilerini ve transcript dosyalarını çıkar.
3. Kullanım `highWaterBytes` değerine eşit ya da daha düşük olana kadar devam et.

`mode: "warn"` durumunda OpenClaw olası çıkarımları bildirir ama depoyu/dosyaları değiştirmez.

Bakımı isteğe bağlı çalıştırın:

```bash
openclaw sessions cleanup --dry-run
openclaw sessions cleanup --enforce
```

---

## Cron oturumları ve çalıştırma günlükleri

Yalıtılmış cron çalıştırmaları da oturum girdileri/transcript'ler oluşturur ve bunların özel saklama denetimleri vardır:

- `cron.sessionRetention` (varsayılan `24h`), eski yalıtılmış cron çalıştırma oturumlarını oturum deposundan temizler (`false` devre dışı bırakır).
- `cron.runLog.maxBytes` + `cron.runLog.keepLines`, `~/.openclaw/cron/runs/<jobId>.jsonl` dosyalarını budar (varsayılanlar: `2_000_000` bayt ve `2000` satır).

---

## Oturum anahtarları (`sessionKey`)

Bir `sessionKey`, hangi konuşma kovasında bulunduğunuzu tanımlar (yönlendirme + yalıtım).

Yaygın desenler:

- Ana/doğrudan sohbet (ajan başına): `agent:<agentId>:<mainKey>` (varsayılan `main`)
- Grup: `agent:<agentId>:<channel>:group:<id>`
- Oda/kanal (Discord/Slack): `agent:<agentId>:<channel>:channel:<id>` veya `...:room:<id>`
- Cron: `cron:<job.id>`
- Webhook: `hook:<uuid>` (geçersiz kılınmadıkça)

Kanonik kurallar [/concepts/session](/tr/concepts/session) içinde belgelenmiştir.

---

## Oturum kimlikleri (`sessionId`)

Her `sessionKey`, geçerli bir `sessionId` değerine işaret eder (konuşmayı sürdüren transcript dosyası).

Başparmak kuralları:

- **Sıfırlama** (`/new`, `/reset`), o `sessionKey` için yeni bir `sessionId` oluşturur.
- **Günlük sıfırlama** (varsayılan olarak Gateway ana bilgisayarının yerel saatinde sabah 4:00), sıfırlama sınırından sonraki ilk mesajda yeni bir `sessionId` oluşturur.
- **Boşta kalma süresi dolması** (`session.reset.idleMinutes` veya eski `session.idleMinutes`), boşta kalma penceresinden sonra bir mesaj geldiğinde yeni bir `sessionId` oluşturur. Günlük + boşta kalma birlikte yapılandırılmışsa, hangisinin süresi önce dolarsa o kazanır.
- **İş parçacığı üst çatal koruması** (`session.parentForkMaxTokens`, varsayılan `100000`), üst oturum zaten çok büyükse üst transcript çatallanmasını atlar; yeni iş parçacığı temiz başlar. Devre dışı bırakmak için `0` ayarlayın.

Uygulama ayrıntısı: karar, `src/auto-reply/reply/session.ts` içindeki `initSessionState()` içinde verilir.

---

## Oturum deposu şeması (`sessions.json`)

Deponun değer türü `src/config/sessions.ts` içindeki `SessionEntry`'dir.

Temel alanlar (kapsamlı değildir):

- `sessionId`: geçerli transcript kimliği (eğer `sessionFile` ayarlı değilse dosya adı bundan türetilir)
- `updatedAt`: son etkinlik zaman damgası
- `sessionFile`: isteğe bağlı açık transcript yolu geçersiz kılması
- `chatType`: `direct | group | room` (UI'lara ve gönderim ilkesine yardımcı olur)
- `provider`, `subject`, `room`, `space`, `displayName`: grup/kanal etiketleme meta verileri
- Anahtarlar:
  - `thinkingLevel`, `verboseLevel`, `reasoningLevel`, `elevatedLevel`
  - `sendPolicy` (oturum başına geçersiz kılma)
- Model seçimi:
  - `providerOverride`, `modelOverride`, `authProfileOverride`
- Token sayaçları (en iyi çaba / sağlayıcıya bağlı):
  - `inputTokens`, `outputTokens`, `totalTokens`, `contextTokens`
- `compactionCount`: bu oturum anahtarı için otomatik sıkıştırmanın kaç kez tamamlandığı
- `memoryFlushAt`: son sıkıştırma öncesi bellek temizlemesinin zaman damgası
- `memoryFlushCompactionCount`: son temizlemenin çalıştığı andaki sıkıştırma sayısı

Depo düzenlemek için güvenlidir, ancak yetkili kaynak Gateway'dir: oturumlar çalışırken girdileri yeniden yazabilir veya yeniden oluşturabilir.

---

## Transcript yapısı (`*.jsonl`)

Transcript'ler `@mariozechner/pi-coding-agent` paketinin `SessionManager` bileşeni tarafından yönetilir.

Dosya JSONL biçimindedir:

- İlk satır: oturum başlığı (`type: "session"`, `id`, `cwd`, `timestamp`, isteğe bağlı `parentSession` içerir)
- Sonra: `id` + `parentId` içeren oturum girdileri (ağaç)

Dikkate değer girdi türleri:

- `message`: kullanıcı/yardımcı/`toolResult` mesajları
- `custom_message`: model bağlamına _giren_ uzantı enjekte edilmiş mesajlar (UI'da gizlenebilir)
- `custom`: model bağlamına girmeyen uzantı durumu
- `compaction`: `firstKeptEntryId` ve `tokensBefore` içeren kalıcı sıkıştırma özeti
- `branch_summary`: ağaç dalında gezinirken kalıcı özet

OpenClaw transcript'leri kasıtlı olarak **düzeltmez**; Gateway bunları okumak/yazmak için `SessionManager` kullanır.

---

## Bağlam pencereleri ve izlenen token'lar

İki farklı kavram önemlidir:

1. **Model bağlam penceresi**: model başına sert üst sınır (modelin görebildiği token'lar)
2. **Oturum deposu sayaçları**: `sessions.json` içine yazılan kayan istatistikler (/status ve dashboard'larda kullanılır)

Sınırları ayarlıyorsanız:

- Bağlam penceresi model kataloğundan gelir (ve yapılandırma ile geçersiz kılınabilir).
- Depodaki `contextTokens`, çalışma zamanı tahmini/raporlama değeridir; bunu katı bir garanti olarak görmeyin.

Daha fazla bilgi için bkz. [/token-use](/tr/reference/token-use).

---

## Sıkıştırma: nedir

Sıkıştırma, eski konuşmayı transcript içinde kalıcı bir `compaction` girdisi olarak özetler ve son mesajları bozulmadan tutar.

Sıkıştırmadan sonra gelecek dönüşler şunları görür:

- Sıkıştırma özeti
- `firstKeptEntryId` sonrasındaki mesajlar

Sıkıştırma **kalıcıdır** (oturum budamadan farklı olarak). Bkz. [/concepts/session-pruning](/tr/concepts/session-pruning).

## Sıkıştırma parça sınırları ve araç eşleştirme

OpenClaw uzun bir transcript'i sıkıştırma parçalarına böldüğünde,
yardımcı araç çağrılarını eşleşen `toolResult` girdileriyle eşli tutar.

- Token-paylaşımı bölmesi bir araç çağrısı ile sonucunun arasına denk gelirse, OpenClaw
  ikiliyi ayırmak yerine sınırı yardımcı araç-çağrısı mesajına kaydırır.
- Sondaki bir araç-sonuç bloğu aksi halde parçayı hedefin üstüne taşıyacaksa,
  OpenClaw bekleyen o araç bloğunu korur ve özetlenmemiş kuyruğu bozulmadan tutar.
- İptal edilmiş/hata veren araç-çağrısı blokları bekleyen bölmeyi açık tutmaz.

---

## Otomatik sıkıştırma ne zaman olur (Pi çalışma zamanı)

Gömülü Pi ajanında otomatik sıkıştırma iki durumda tetiklenir:

1. **Taşma kurtarma**: model bağlam taşma hatası döndürür
   (`request_too_large`, `context length exceeded`, `input exceeds the maximum
number of tokens`, `input token count exceeds the maximum number of input
tokens`, `input is too long for the model`, `ollama error: context length
exceeded` ve benzeri sağlayıcı biçimli varyantlar) → sıkıştır → yeniden dene.
2. **Eşik bakımı**: başarılı bir dönüşten sonra, şu durumda:

`contextTokens > contextWindow - reserveTokens`

Burada:

- `contextWindow`, modelin bağlam penceresidir
- `reserveTokens`, prompt'lar + sonraki model çıktısı için ayrılan boşluktur

Bunlar Pi çalışma zamanı anlambilimleridir (OpenClaw olayları tüketir, ancak ne zaman sıkıştırılacağına Pi karar verir).

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

OpenClaw gömülü çalıştırmalar için ayrıca bir güvenlik tabanı uygular:

- Eğer `compaction.reserveTokens < reserveTokensFloor` ise OpenClaw bunu yükseltir.
- Varsayılan taban `20000` token'dır.
- Tabanı devre dışı bırakmak için `agents.defaults.compaction.reserveTokensFloor: 0` ayarlayın.
- Zaten daha yüksekse OpenClaw buna dokunmaz.

Neden: sıkıştırma kaçınılmaz hâle gelmeden önce çok dönüşlü “bakım işleri” (bellek yazımları gibi) için yeterli boşluk bırakmak.

Uygulama: `src/agents/pi-settings.ts` içindeki `ensurePiCompactionReserveTokens()`
(`src/agents/pi-embedded-runner.ts` tarafından çağrılır).

---

## Kullanıcıya görünür yüzeyler

Sıkıştırmayı ve oturum durumunu şu yollarla gözlemleyebilirsiniz:

- `/status` (herhangi bir sohbet oturumunda)
- `openclaw status` (CLI)
- `openclaw sessions` / `sessions --json`
- Ayrıntılı mod: `🧹 Auto-compaction complete` + sıkıştırma sayısı

---

## Sessiz bakım işleri (`NO_REPLY`)

OpenClaw, kullanıcıların ara çıktıyı görmemesi gereken arka plan görevleri için “sessiz” dönüşleri destekler.

Kural:

- Yardımcı, kullanıcıya yanıt teslim etmeme anlamına geldiğini belirtmek için çıktısına tam sessiz token `NO_REPLY` /
  `no_reply` ile başlar.
- OpenClaw bunu teslimat katmanında ayıklar/bastırır.
- Tam yük yalnızca sessiz token olduğunda, tam sessiz-token bastırması büyük/küçük harf duyarsızdır; yani `NO_REPLY` ve
  `no_reply` her ikisi de geçerlidir.
- Bu yalnızca gerçek arka plan/teslimatsız dönüşler içindir; sıradan eyleme geçirilebilir kullanıcı istekleri için kestirme yol değildir.

`2026.1.10` itibarıyla OpenClaw, kısmi bir parça `NO_REPLY` ile başladığında **taslak/yazıyor akışını** da bastırır; böylece sessiz işlemler dönüş ortasında kısmi çıktı sızdırmaz.

---

## Sıkıştırma öncesi "bellek temizleme" (uygulandı)

Amaç: otomatik sıkıştırma gerçekleşmeden önce, sıkıştırmanın kritik bağlamı silememesi için diske kalıcı
durum yazan (ör. ajan çalışma alanında `memory/YYYY-MM-DD.md`) sessiz bir ajan dönüşü çalıştırmak.

OpenClaw **eşik öncesi temizleme** yaklaşımını kullanır:

1. Oturum bağlam kullanımını izle.
2. “Yumuşak eşik” aşıldığında (Pi'nin sıkıştırma eşiğinin altında), ajana sessiz
   bir “şimdi bellek yaz” yönergesi çalıştır.
3. Kullanıcının hiçbir şey görmemesi için tam sessiz token `NO_REPLY` / `no_reply` kullan.

Yapılandırma (`agents.defaults.compaction.memoryFlush`):

- `enabled` (varsayılan: `true`)
- `softThresholdTokens` (varsayılan: `4000`)
- `prompt` (temizleme dönüşü için kullanıcı mesajı)
- `systemPrompt` (temizleme dönüşü için eklenen ek sistem prompt'u)

Notlar:

- Varsayılan prompt/system prompt, teslimatı bastırmak için `NO_REPLY` ipucu içerir.
- Temizleme, sıkıştırma döngüsü başına bir kez çalışır (`sessions.json` içinde izlenir).
- Temizleme yalnızca gömülü Pi oturumları için çalışır.
- Oturum çalışma alanı salt okunursa (`workspaceAccess: "ro"` veya `"none"`) temizleme atlanır.
- Çalışma alanı dosya düzeni ve yazma desenleri için bkz. [Bellek](/tr/concepts/memory).

Pi ayrıca uzantı API'sinde `session_before_compact` hook'unu sunar, ancak OpenClaw'ın
temizleme mantığı bugün Gateway tarafında bulunuyor.

---

## Sorun giderme denetim listesi

- Oturum anahtarı yanlış mı? [/concepts/session](/tr/concepts/session) ile başlayın ve `/status` içindeki `sessionKey` değerini doğrulayın.
- Depo ile transcript uyuşmuyor mu? Gateway ana bilgisayarını ve `openclaw status` içindeki depo yolunu doğrulayın.
- Sıkıştırma spam'i mi var? Şunları kontrol edin:
  - model bağlam penceresi (çok küçük)
  - sıkıştırma ayarları (model penceresi için `reserveTokens` çok yüksekse daha erken sıkıştırmaya neden olabilir)
  - araç-sonuç şişmesi: oturum budamayı etkinleştirin/ayarlayın
- Sessiz dönüşler sızıyor mu? Yanıtın `NO_REPLY` ile başladığını (büyük/küçük harf duyarsız tam token) ve akış bastırma düzeltmesini içeren bir derlemede olduğunuzu doğrulayın.
