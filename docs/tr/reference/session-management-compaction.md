---
read_when:
    - Oturum kimliklerinde, transcript JSONL'de veya sessions.json alanlarında hata ayıklamanız gerekiyor
    - Otomatik sıkıştırma davranışını değiştiriyor veya “sıkıştırma öncesi” bakım ekliyorsunuz
    - Bellek boşaltmaları veya sessiz sistem turları uygulamak istiyorsunuz
summary: 'Derinlemesine inceleme: oturum deposu + transkriptler, yaşam döngüsü ve (otomatik) sıkıştırma iç yapıları'
title: Oturum Yönetimi Derinlemesine İnceleme
x-i18n:
    generated_at: "2026-04-08T02:18:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: cb1a4048646486693db8943a9e9c6c5bcb205f0ed532b34842de3d0346077454
    source_path: reference/session-management-compaction.md
    workflow: 15
---

# Oturum Yönetimi ve Sıkıştırma (Derinlemesine İnceleme)

Bu belge, OpenClaw'ın oturumları uçtan uca nasıl yönettiğini açıklar:

- **Oturum yönlendirme** (gelen mesajların bir `sessionKey` değerine nasıl eşlendiği)
- **Oturum deposu** (`sessions.json`) ve neyi izlediği
- **Transkript kalıcılığı** (`*.jsonl`) ve yapısı
- **Transkript hijyeni** (çalıştırmalardan önce sağlayıcıya özgü düzeltmeler)
- **Bağlam sınırları** (bağlam penceresi ile izlenen token'lar)
- **Sıkıştırma** (elle + otomatik sıkıştırma) ve sıkıştırma öncesi işlerin nereye bağlanacağı
- **Sessiz bakım** (ör. kullanıcıya görünür çıktı üretmemesi gereken bellek yazımları)

Önce daha üst düzey bir genel bakış istiyorsanız, şuradan başlayın:

- [/concepts/session](/tr/concepts/session)
- [/concepts/compaction](/tr/concepts/compaction)
- [/concepts/memory](/tr/concepts/memory)
- [/concepts/memory-search](/tr/concepts/memory-search)
- [/concepts/session-pruning](/tr/concepts/session-pruning)
- [/reference/transcript-hygiene](/tr/reference/transcript-hygiene)

---

## Doğruluğun kaynağı: Gateway

OpenClaw, oturum durumuna sahip tek bir **Gateway süreci** etrafında tasarlanmıştır.

- UI'ler (macOS uygulaması, web Control UI, TUI), oturum listeleri ve token sayıları için Gateway'i sorgulamalıdır.
- Uzak modda oturum dosyaları uzak ana makinededir; “yerel Mac dosyalarınızı kontrol etmek”, Gateway'in kullandığını yansıtmaz.

---

## İki kalıcılık katmanı

OpenClaw, oturumları iki katmanda kalıcı hale getirir:

1. **Oturum deposu (`sessions.json`)**
   - Anahtar/değer eşlemesi: `sessionKey -> SessionEntry`
   - Küçük, değiştirilebilir, düzenlenmesi güvenli (veya girdiler silinebilir)
   - Oturum meta verilerini izler (geçerli oturum kimliği, son etkinlik, anahtarlar, token sayaçları vb.)

2. **Transkript (`<sessionId>.jsonl`)**
   - Ağaç yapılı eklemeli transkript (girdilerde `id` + `parentId` vardır)
   - Gerçek konuşmayı + araç çağrılarını + sıkıştırma özetlerini saklar
   - Gelecek turlar için model bağlamını yeniden oluşturmakta kullanılır

---

## Disk üzerindeki konumlar

Gateway ana makinesinde, agent başına:

- Depo: `~/.openclaw/agents/<agentId>/sessions/sessions.json`
- Transkriptler: `~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl`
  - Telegram konu oturumları: `.../<sessionId>-topic-<threadId>.jsonl`

OpenClaw bunları `src/config/sessions.ts` aracılığıyla çözümler.

---

## Depo bakımı ve disk denetimleri

Oturum kalıcılığı, `sessions.json` ve transkript yapılarını korumak için otomatik bakım denetimlerine (`session.maintenance`) sahiptir:

- `mode`: `warn` (varsayılan) veya `enforce`
- `pruneAfter`: eski giriş yaş sınırı (varsayılan `30d`)
- `maxEntries`: `sessions.json` içindeki giriş sınırı (varsayılan `500`)
- `rotateBytes`: `sessions.json` aşırı büyüdüğünde döndürme eşiği (varsayılan `10mb`)
- `resetArchiveRetention`: `*.reset.<timestamp>` transkript arşivleri için saklama süresi (varsayılan: `pruneAfter` ile aynı; `false` temizlemeyi devre dışı bırakır)
- `maxDiskBytes`: isteğe bağlı oturumlar dizini bütçesi
- `highWaterBytes`: temizlikten sonraki isteğe bağlı hedef (varsayılan `maxDiskBytes` değerinin `%80`'i)

Disk bütçesi temizliği için uygulama sırası (`mode: "enforce"`):

1. Önce en eski arşivlenmiş veya sahipsiz transkript yapılarını kaldırın.
2. Hâlâ hedefin üzerindeyse en eski oturum girdilerini ve transkript dosyalarını çıkarın.
3. Kullanım `highWaterBytes` değerine veya altına inene kadar devam edin.

`mode: "warn"` modunda OpenClaw olası çıkarmaları bildirir, ancak depoyu/dosyaları değiştirmez.

Bakımı isteğe bağlı olarak çalıştırın:

```bash
openclaw sessions cleanup --dry-run
openclaw sessions cleanup --enforce
```

---

## Cron oturumları ve çalıştırma günlükleri

Yalıtılmış cron çalıştırmaları da oturum girdileri/transkriptler oluşturur ve bunların özel saklama denetimleri vardır:

- `cron.sessionRetention` (varsayılan `24h`), oturum deposundaki eski yalıtılmış cron çalıştırma oturumlarını budar (`false` bunu devre dışı bırakır).
- `cron.runLog.maxBytes` + `cron.runLog.keepLines`, `~/.openclaw/cron/runs/<jobId>.jsonl` dosyalarını budar (varsayılanlar: `2_000_000` bayt ve `2000` satır).

---

## Oturum anahtarları (`sessionKey`)

Bir `sessionKey`, _hangi konuşma kovasında_ olduğunuzu tanımlar (yönlendirme + yalıtım).

Yaygın desenler:

- Ana/doğrudan sohbet (agent başına): `agent:<agentId>:<mainKey>` (varsayılan `main`)
- Grup: `agent:<agentId>:<channel>:group:<id>`
- Oda/kanal (Discord/Slack): `agent:<agentId>:<channel>:channel:<id>` veya `...:room:<id>`
- Cron: `cron:<job.id>`
- Webhook: `hook:<uuid>` (geçersiz kılınmadıkça)

Kanonik kurallar [/concepts/session](/tr/concepts/session) altında belgelenmiştir.

---

## Oturum kimlikleri (`sessionId`)

Her `sessionKey`, geçerli bir `sessionId` değerine işaret eder (konuşmayı sürdüren transkript dosyası).

Temel kurallar:

- **Sıfırlama** (`/new`, `/reset`), bu `sessionKey` için yeni bir `sessionId` oluşturur.
- **Günlük sıfırlama** (varsayılan olarak gateway ana makinesinin yerel saatine göre sabah 4:00), sıfırlama sınırından sonraki ilk mesajda yeni bir `sessionId` oluşturur.
- **Boşta kalma süresi dolumu** (`session.reset.idleMinutes` veya eski `session.idleMinutes`), boşta kalma penceresinden sonra mesaj geldiğinde yeni bir `sessionId` oluşturur. Günlük + boşta kalma birlikte yapılandırıldığında hangisinin süresi önce dolarsa o kazanır.
- **Thread üst çatallama koruması** (`session.parentForkMaxTokens`, varsayılan `100000`), üst oturum zaten çok büyükse üst transkript çatallamasını atlar; yeni thread temiz başlar. Devre dışı bırakmak için `0` ayarlayın.

Uygulama ayrıntısı: karar, `src/auto-reply/reply/session.ts` içindeki `initSessionState()` içinde verilir.

---

## Oturum deposu şeması (`sessions.json`)

Deponun değer türü, `src/config/sessions.ts` içindeki `SessionEntry` türüdür.

Temel alanlar (tam liste değildir):

- `sessionId`: geçerli transkript kimliği (eğer `sessionFile` ayarlanmışsa dosya adı bundan türetilmez)
- `updatedAt`: son etkinlik zaman damgası
- `sessionFile`: isteğe bağlı açık transkript yolu geçersiz kılması
- `chatType`: `direct | group | room` (UI'lere ve gönderim ilkesine yardımcı olur)
- `provider`, `subject`, `room`, `space`, `displayName`: grup/kanal etiketlemesi için meta veriler
- Anahtarlar:
  - `thinkingLevel`, `verboseLevel`, `reasoningLevel`, `elevatedLevel`
  - `sendPolicy` (oturum başına geçersiz kılma)
- Model seçimi:
  - `providerOverride`, `modelOverride`, `authProfileOverride`
- Token sayaçları (en iyi çaba / sağlayıcıya bağlı):
  - `inputTokens`, `outputTokens`, `totalTokens`, `contextTokens`
- `compactionCount`: bu oturum anahtarı için otomatik sıkıştırmanın kaç kez tamamlandığı
- `memoryFlushAt`: son sıkıştırma öncesi bellek boşaltmanın zaman damgası
- `memoryFlushCompactionCount`: son boşaltmanın çalıştığı sıradaki sıkıştırma sayısı

Deponun düzenlenmesi güvenlidir, ancak yetkili olan Gateway'dir: oturumlar çalıştıkça girdileri yeniden yazabilir veya yeniden oluşturabilir.

---

## Transkript yapısı (`*.jsonl`)

Transkriptler, `@mariozechner/pi-coding-agent` içindeki `SessionManager` tarafından yönetilir.

Dosya JSONL biçimindedir:

- İlk satır: oturum başlığı (`type: "session"`, `id`, `cwd`, `timestamp`, isteğe bağlı `parentSession` içerir)
- Sonra: `id` + `parentId` içeren oturum girdileri (ağaç)

Dikkat çeken girdi türleri:

- `message`: kullanıcı/asistan/toolResult mesajları
- `custom_message`: model bağlamına _giren_ uzantı enjeksiyonlu mesajlar (UI'de gizlenebilir)
- `custom`: model bağlamına girmeyen uzantı durumu
- `compaction`: `firstKeptEntryId` ve `tokensBefore` içeren kalıcı sıkıştırma özeti
- `branch_summary`: bir ağaç dalında gezinirken kalıcı özet

OpenClaw bilinçli olarak transkriptleri **düzeltmez**; Gateway bunları okumak/yazmak için `SessionManager` kullanır.

---

## Bağlam pencereleri ve izlenen token'lar

İki farklı kavram önemlidir:

1. **Model bağlam penceresi**: model başına sabit üst sınır (modele görünen token'lar)
2. **Oturum deposu sayaçları**: `sessions.json` içine yazılan dönen istatistikler (`/status` ve panolar için kullanılır)

Sınırları ayarlıyorsanız:

- Bağlam penceresi model kataloğundan gelir (ve yapılandırma ile geçersiz kılınabilir).
- Depodaki `contextTokens`, çalışma zamanı tahmini/raporlama değeridir; bunu katı bir garanti olarak görmeyin.

Daha fazla bilgi için [/token-use](/tr/reference/token-use) sayfasına bakın.

---

## Sıkıştırma: nedir

Sıkıştırma, daha eski konuşmayı transkriptte kalıcı bir `compaction` girdisi halinde özetler ve son mesajları bozulmadan tutar.

Sıkıştırmadan sonra gelecekteki turlar şunları görür:

- Sıkıştırma özeti
- `firstKeptEntryId` sonrasındaki mesajlar

Sıkıştırma **kalıcıdır** (oturum budamadan farklı olarak). Bkz. [/concepts/session-pruning](/tr/concepts/session-pruning).

## Sıkıştırma parça sınırları ve araç eşleştirme

OpenClaw uzun bir transkripti sıkıştırma parçalarına böldüğünde,
asistan araç çağrılarını eşleşen `toolResult` girdileriyle eşli tutar.

- Token paylaşımı bölümü bir araç çağrısı ile sonucu arasına denk gelirse OpenClaw
  çifti ayırmak yerine sınırı asistan araç çağrısı mesajına kaydırır.
- Sondaki bir araç sonucu bloğu parçayı aksi halde hedefin üstüne iteceksa
  OpenClaw bekleyen bu araç bloğunu korur ve özetlenmemiş kuyruğu bozulmadan tutar.
- İptal edilen/hatalı araç çağrısı blokları bekleyen bir bölünmeyi açık tutmaz.

---

## Otomatik sıkıştırma ne zaman olur (Pi çalışma zamanı)

Gömülü Pi agent'ında otomatik sıkıştırma iki durumda tetiklenir:

1. **Taşma kurtarma**: model bir bağlam taşması hatası döndürür
   (`request_too_large`, `context length exceeded`, `input exceeds the maximum
number of tokens`, `input token count exceeds the maximum number of input
tokens`, `input is too long for the model`, `ollama error: context length
exceeded` ve benzeri sağlayıcı biçimli varyantlar) → sıkıştır → yeniden dene.
2. **Eşik bakımı**: başarılı bir turdan sonra, şu durumda:

`contextTokens > contextWindow - reserveTokens`

Burada:

- `contextWindow`, modelin bağlam penceresidir
- `reserveTokens`, istemler + bir sonraki model çıktısı için ayrılan boşluk payıdır

Bunlar Pi çalışma zamanı semantikidir (OpenClaw olayları tüketir, ancak ne zaman sıkıştırılacağına Pi karar verir).

---

## Sıkıştırma ayarları (`reserveTokens`, `keepRecentTokens`)

Pi'nin sıkıştırma ayarları Pi settings içinde bulunur:

```json5
{
  compaction: {
    enabled: true,
    reserveTokens: 16384,
    keepRecentTokens: 20000,
  },
}
```

OpenClaw ayrıca gömülü çalıştırmalar için bir güvenlik taban sınırı uygular:

- Eğer `compaction.reserveTokens < reserveTokensFloor` ise OpenClaw bunu yükseltir.
- Varsayılan taban sınır `20000` token'dır.
- Taban sınırı devre dışı bırakmak için `agents.defaults.compaction.reserveTokensFloor: 0` ayarlayın.
- Değer zaten daha yüksekse OpenClaw dokunmaz.

Neden: sıkıştırma kaçınılmaz hale gelmeden önce çok turlu “bakım” işlemleri (bellek yazımları gibi) için yeterli boşluk bırakmak.

Uygulama: `src/agents/pi-settings.ts` içindeki `ensurePiCompactionReserveTokens()`
(`src/agents/pi-embedded-runner.ts` içinden çağrılır).

---

## Takılabilir sıkıştırma sağlayıcıları

Plugin'ler, plugin API üzerinde `registerCompactionProvider()` aracılığıyla bir sıkıştırma sağlayıcısı kaydedebilir. `agents.defaults.compaction.provider`, kaydedilmiş bir sağlayıcı kimliğine ayarlandığında güvenlik uzantısı, özetlemeyi yerleşik `summarizeInStages` hattı yerine bu sağlayıcıya devreder.

- `provider`: kayıtlı bir sıkıştırma sağlayıcı plugin'inin kimliği. Varsayılan LLM özetlemesi için boş bırakın.
- `provider` ayarlamak `mode: "safeguard"` değerini zorlar.
- Sağlayıcılar, yerleşik yol ile aynı sıkıştırma yönergelerini ve tanımlayıcı koruma ilkesini alır.
- Güvenlik koruması, sağlayıcı çıktısından sonra da son turların ve bölünmüş turun sonek bağlamını korur.
- Sağlayıcı başarısız olursa veya boş sonuç döndürürse OpenClaw otomatik olarak yerleşik LLM özetlemesine geri döner.
- Abort/timeout sinyalleri çağıran iptaline saygı göstermek için yeniden fırlatılır (yutulmaz).

Kaynak: `src/plugins/compaction-provider.ts`, `src/agents/pi-hooks/compaction-safeguard.ts`.

---

## Kullanıcıya görünür yüzeyler

Sıkıştırmayı ve oturum durumunu şuralardan gözlemleyebilirsiniz:

- `/status` (herhangi bir sohbet oturumunda)
- `openclaw status` (CLI)
- `openclaw sessions` / `sessions --json`
- Ayrıntılı mod: `🧹 Auto-compaction complete` + sıkıştırma sayısı

---

## Sessiz bakım (`NO_REPLY`)

OpenClaw, kullanıcının ara çıktıları görmemesi gereken arka plan görevleri için “sessiz” turları destekler.

Kural:

- Asistan, “kullanıcıya yanıt teslim etme” anlamına gelecek şekilde çıktısına tam sessiz token `NO_REPLY` /
  `no_reply` ile başlar.
- OpenClaw bunu teslim katmanında temizler/bastırır.
- Tam sessiz token bastırması büyük/küçük harfe duyarsızdır; yani tüm yük yalnızca sessiz token ise
  `NO_REPLY` ve `no_reply` ikisi de sayılır.
- Bu yalnızca gerçek arka plan/teslim yok turları içindir; sıradan eyleme dönük kullanıcı istekleri için bir kısayol değildir.

`2026.1.10` itibarıyla OpenClaw, kısmi bir parça `NO_REPLY` ile başladığında
**taslak/yazıyor akışını** da bastırır; böylece sessiz işlemler tur ortasında
kısmi çıktı sızdırmaz.

---

## Sıkıştırma öncesi "bellek boşaltma" (uygulandı)

Amaç: otomatik sıkıştırma olmadan önce diske kalıcı durum yazan sessiz bir agentic tur çalıştırmak
(ör. agent çalışma alanındaki `memory/YYYY-MM-DD.md`), böylece sıkıştırma kritik bağlamı
silemez.

OpenClaw **eşik öncesi boşaltma** yaklaşımını kullanır:

1. Oturum bağlam kullanımını izleyin.
2. Bu kullanım bir “yumuşak eşiği” geçtiğinde (Pi'nin sıkıştırma eşiğinin altında), agente sessiz bir
   “şimdi belleğe yaz” yönergesi çalıştırın.
3. Kullanıcı hiçbir şey görmesin diye tam sessiz token `NO_REPLY` / `no_reply` kullanın.

Yapılandırma (`agents.defaults.compaction.memoryFlush`):

- `enabled` (varsayılan: `true`)
- `softThresholdTokens` (varsayılan: `4000`)
- `prompt` (boşaltma turu için kullanıcı mesajı)
- `systemPrompt` (boşaltma turu için eklenen ek sistem istemi)

Notlar:

- Varsayılan prompt/system prompt, teslimi bastırmak için `NO_REPLY` ipucu içerir.
- Boşaltma, sıkıştırma döngüsü başına bir kez çalışır (`sessions.json` içinde izlenir).
- Boşaltma yalnızca gömülü Pi oturumlarında çalışır (CLI arka uçları bunu atlar).
- Oturum çalışma alanı salt okunursa boşaltma atlanır (`workspaceAccess: "ro"` veya `"none"`).
- Çalışma alanı dosya düzeni ve yazma desenleri için [Memory](/tr/concepts/memory) sayfasına bakın.

Pi ayrıca uzantı API'sinde bir `session_before_compact` hook'u da sunar, ancak OpenClaw'ın
boşaltma mantığı bugün Gateway tarafında bulunur.

---

## Sorun giderme kontrol listesi

- Oturum anahtarı yanlış mı? [/concepts/session](/tr/concepts/session) ile başlayın ve `/status` içindeki `sessionKey` değerini doğrulayın.
- Depo ile transkript uyuşmuyor mu? Gateway ana makinesini ve `openclaw status` çıktısındaki depo yolunu doğrulayın.
- Sıkıştırma spam'i mi var? Şunları kontrol edin:
  - model bağlam penceresi (çok küçük olabilir)
  - sıkıştırma ayarları (model penceresi için `reserveTokens` çok yüksekse daha erken sıkıştırmaya neden olabilir)
  - tool-result şişmesi: oturum budamayı etkinleştirin/ayarlayın
- Sessiz turlar sızıyor mu? Yanıtın `NO_REPLY` ile başladığını (büyük/küçük harfe duyarsız tam token) ve akış bastırma düzeltmesini içeren bir sürüm kullandığınızı doğrulayın.
