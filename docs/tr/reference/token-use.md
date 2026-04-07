---
read_when:
    - Token kullanımı, maliyetler veya bağlam pencerelerini açıklama
    - Bağlam büyümesi veya sıkıştırma davranışında hata ayıklama
summary: OpenClaw'ın prompt bağlamını nasıl oluşturduğu ve token kullanımı ile maliyetleri nasıl raporladığı
title: Token Kullanımı ve Maliyetler
x-i18n:
    generated_at: "2026-04-07T08:49:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0683693d6c6fcde7d5fba236064ba97dd4b317ae6bea3069db969fcd178119d9
    source_path: reference/token-use.md
    workflow: 15
---

# Token kullanımı ve maliyetler

OpenClaw **karakterleri değil**, **token'ları** izler. Token'lar modele özeldir, ancak çoğu
OpenAI tarzı model İngilizce metin için ortalama token başına yaklaşık 4 karakter kullanır.

## Sistem prompt'u nasıl oluşturulur

OpenClaw her çalıştırmada kendi system prompt'unu oluşturur. Şunları içerir:

- Tool listesi + kısa açıklamalar
- Skills listesi (yalnızca meta veriler; yönergeler isteğe bağlı olarak `read` ile yüklenir)
- Kendi kendini güncelleme yönergeleri
- Çalışma alanı + bootstrap dosyaları (`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, yeni olduğunda `BOOTSTRAP.md`, ayrıca varsa `MEMORY.md` veya küçük harfli geri dönüş olarak `memory.md`). Büyük dosyalar `agents.defaults.bootstrapMaxChars` (varsayılan: 20000) ile kısaltılır ve toplam bootstrap ekleme işlemi `agents.defaults.bootstrapTotalMaxChars` (varsayılan: 150000) ile sınırlandırılır. `memory/*.md` dosyaları memory tools aracılığıyla isteğe bağlıdır ve otomatik eklenmez.
- Zaman (UTC + kullanıcı saat dilimi)
- Yanıt etiketleri + heartbeat davranışı
- Çalışma zamanı meta verileri (host/OS/model/thinking)

Tam döküm için bkz. [System Prompt](/tr/concepts/system-prompt).

## Bağlam penceresinde ne sayılır

Modelin aldığı her şey bağlam sınırına dahil edilir:

- System prompt (yukarıda listelenen tüm bölümler)
- Konuşma geçmişi (kullanıcı + yardımcı mesajları)
- Tool çağrıları ve tool sonuçları
- Ekler/transkriptler (görüntüler, ses, dosyalar)
- Sıkıştırma özetleri ve budama yapıtları
- Provider wrapper'ları veya güvenlik header'ları (görünmezler, ama yine de sayılırlar)

Görüntüler için OpenClaw, provider çağrılarından önce transcript/tool görüntü payload'larını küçültür.
Bunu ayarlamak için `agents.defaults.imageMaxDimensionPx` (varsayılan: `1200`) kullanın:

- Daha düşük değerler genellikle vision-token kullanımını ve payload boyutunu azaltır.
- Daha yüksek değerler OCR/UI ağırlıklı ekran görüntüleri için daha fazla görsel ayrıntıyı korur.

Pratik bir döküm için (eklenen dosya başına, tool'lar, Skills ve system prompt boyutu), `/context list` veya `/context detail` kullanın. Bkz. [Context](/tr/concepts/context).

## Geçerli token kullanımı nasıl görülür

Sohbette şunları kullanın:

- `/status` → oturum modeli, bağlam kullanımı,
  son yanıt giriş/çıkış token'ları ve **tahmini maliyet** (yalnızca API anahtarı) içeren **emoji açısından zengin durum kartı**.
- `/usage off|tokens|full` → her yanıta **yanıt başına kullanım alt bilgisi** ekler.
  - Oturum başına kalıcıdır (`responseUsage` olarak saklanır).
  - OAuth kimlik doğrulaması **maliyeti gizler** (yalnızca token'lar).
- `/usage cost` → OpenClaw oturum günlüklerinden yerel maliyet özetini gösterir.

Diğer yüzeyler:

- **TUI/Web TUI:** `/status` + `/usage` desteklenir.
- **CLI:** `openclaw status --usage` ve `openclaw channels list`,
  normalize edilmiş provider kota pencerelerini gösterir (`yanıt başına maliyetler` değil, `X% kaldı`).
  Geçerli kullanım penceresi provider'ları: Anthropic, GitHub Copilot, Gemini CLI,
  OpenAI Codex, MiniMax, Xiaomi ve z.ai.

Kullanım yüzeyleri, görüntülemeden önce yaygın provider yerel alan takma adlarını normalize eder.
OpenAI ailesi Responses trafiği için buna hem `input_tokens` /
`output_tokens` hem de `prompt_tokens` / `completion_tokens` dahildir; böylece taşımaya özgü
alan adları `/status`, `/usage` veya oturum özetlerini değiştirmez.
Gemini CLI JSON kullanımı da normalize edilir: yanıt metni `response` içinden gelir ve
CLI açık bir `stats.input` alanı vermediğinde
`stats.cached`, `cacheRead` olarak eşlenir; `stats.input_tokens - stats.cached` kullanılır.
Yerel OpenAI ailesi Responses trafiği için WebSocket/SSE kullanım takma adları da
aynı şekilde normalize edilir ve `total_tokens` eksikse veya `0` ise toplamlar normalize edilmiş giriş + çıkıştan geri düşer.
Geçerli oturum anlık görüntüsü seyrekse `/status` ve `session_status`
ayrıca token/cache sayaçlarını ve etkin çalışma zamanı model etiketini
en son transcript kullanım günlüğünden de geri kazanabilir.
Mevcut sıfır olmayan canlı değerler yine de transcript geri dönüş değerlerine göre önceliklidir ve saklanan toplamlar eksik veya daha küçük olduğunda daha büyük prompt odaklı
transcript toplamları kazanabilir.
Provider kota pencereleri için kullanım kimlik doğrulaması, mevcut olduğunda provider'a özgü hook'lardan gelir; aksi halde OpenClaw auth profillerinden, env'den veya yapılandırmadan eşleşen OAuth/API key kimlik bilgilerine geri düşer.

## Maliyet tahmini (gösterildiğinde)

Maliyetler model fiyatlandırma yapılandırmanızdan tahmin edilir:

```
models.providers.<provider>.models[].cost
```

Bunlar `input`, `output`, `cacheRead` ve
`cacheWrite` için **1M token başına USD** değerleridir. Fiyatlandırma eksikse OpenClaw yalnızca token'ları gösterir. OAuth token'ları
asla dolar cinsinden maliyet göstermez.

## Cache TTL ve budama etkisi

Provider prompt caching yalnızca cache TTL penceresi içinde geçerlidir. OpenClaw
isteğe bağlı olarak **cache-ttl pruning** çalıştırabilir: cache TTL
süresi dolduğunda oturumu budar, sonra cache penceresini sıfırlar; böylece sonraki istekler tam geçmişi yeniden cache'lemek yerine
yeni cache'lenen bağlamı yeniden kullanabilir. Bu, bir oturum TTL süresini aşacak kadar boşta kaldığında cache
yazma maliyetlerini daha düşük tutar.

Bunu [Gateway configuration](/tr/gateway/configuration) bölümünde yapılandırın ve
davranış ayrıntıları için [Session pruning](/tr/concepts/session-pruning) bölümüne bakın.

Heartbeat, cache'i boşta geçen aralıklarda **sıcak** tutabilir. Model cache TTL'niz
`1h` ise heartbeat aralığını bunun biraz altına ayarlamak (örneğin `55m`) tam
prompt'un yeniden cache'lenmesini önleyebilir ve cache yazma maliyetlerini düşürebilir.

Çoklu ajan kurulumlarında tek bir paylaşılan model yapılandırmasını koruyabilir ve cache davranışını
ajan başına `agents.list[].params.cacheRetention` ile ayarlayabilirsiniz.

Her ayar düğmesini tek tek açıklayan tam bir kılavuz için bkz. [Prompt Caching](/tr/reference/prompt-caching).

Anthropic API fiyatlandırmasında cache okumaları input
token'lara göre belirgin şekilde daha ucuzdur; cache yazmaları ise daha yüksek bir çarpanla ücretlendirilir. En güncel oranlar ve TTL çarpanları için Anthropic’in
prompt caching fiyatlandırmasına bakın:
[https://docs.anthropic.com/docs/build-with-claude/prompt-caching](https://docs.anthropic.com/docs/build-with-claude/prompt-caching)

### Örnek: 1h cache'i heartbeat ile sıcak tutma

```yaml
agents:
  defaults:
    model:
      primary: "anthropic/claude-opus-4-6"
    models:
      "anthropic/claude-opus-4-6":
        params:
          cacheRetention: "long"
    heartbeat:
      every: "55m"
```

### Örnek: ajan başına cache stratejisi ile karma trafik

```yaml
agents:
  defaults:
    model:
      primary: "anthropic/claude-opus-4-6"
    models:
      "anthropic/claude-opus-4-6":
        params:
          cacheRetention: "long" # çoğu ajan için varsayılan temel yapı
  list:
    - id: "research"
      default: true
      heartbeat:
        every: "55m" # derin oturumlar için uzun cache'i sıcak tut
    - id: "alerts"
      params:
        cacheRetention: "none" # patlamalı bildirimler için cache yazımlarını önle
```

`agents.list[].params`, seçilen modelin `params` alanının üzerine birleştirilir; böylece yalnızca
`cacheRetention` değerini geçersiz kılabilir ve diğer model varsayılanlarını değiştirmeden devralabilirsiniz.

### Örnek: Anthropic 1M bağlam beta header'ını etkinleştirme

Anthropic'in 1M bağlam penceresi şu anda beta kapılıdır. OpenClaw,
desteklenen Opus veya Sonnet modellerinde `context1m` etkinleştirdiğinizde gerekli
`anthropic-beta` değerini ekleyebilir.

```yaml
agents:
  defaults:
    models:
      "anthropic/claude-opus-4-6":
        params:
          context1m: true
```

Bu, Anthropic'in `context-1m-2025-08-07` beta header'ına eşlenir.

Bu yalnızca o model girdisinde `context1m: true` ayarlandığında uygulanır.

Gereksinim: kimlik bilgisinin uzun bağlam kullanımı için uygun olması gerekir. Değilse,
Anthropic bu istek için provider taraflı bir rate limit hatası döndürür.

Anthropic'i OAuth/abonelik token'larıyla (`sk-ant-oat-*`) kimlik doğruluyorsanız,
OpenClaw `context-1m-*` beta header'ını atlar çünkü Anthropic şu anda
bu kombinasyonu HTTP 401 ile reddeder.

## Token baskısını azaltma ipuçları

- Uzun oturumları özetlemek için `/compact` kullanın.
- İş akışlarınızda büyük tool çıktılarını kısaltın.
- Ekran görüntüsü ağırlıklı oturumlar için `agents.defaults.imageMaxDimensionPx` değerini düşürün.
- Skill açıklamalarını kısa tutun (skill listesi prompt'a eklenir).
- Ayrıntılı, keşif amaçlı işler için daha küçük modelleri tercih edin.

Tam skill listesi ek yükü formülü için bkz. [Skills](/tr/tools/skills).
