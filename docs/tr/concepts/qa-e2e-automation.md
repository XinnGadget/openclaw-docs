---
read_when:
    - qa-lab veya qa-channel'ı genişletme
    - Depo destekli QA senaryoları ekleme
    - Gateway panosu etrafında daha yüksek gerçekçiliğe sahip QA otomasyonu oluşturma
summary: qa-lab, qa-channel, tohumlanmış senaryolar ve protokol raporları için özel QA otomasyon yapısı
title: QA E2E Otomasyonu
x-i18n:
    generated_at: "2026-04-13T08:50:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: a4a4f5c765163565c95c2a071f201775fd9d8d60cad4ff25d71e4710559c1570
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# QA E2E Otomasyonu

Özel QA yığını, OpenClaw'ı tek birim testinin yapabileceğinden daha gerçekçi,
kanal biçimli bir şekilde çalıştırmayı amaçlar.

Mevcut parçalar:

- `extensions/qa-channel`: DM, kanal, ileti dizisi,
  tepki, düzenleme ve silme yüzeylerine sahip sentetik mesaj kanalı.
- `extensions/qa-lab`: transkripti gözlemlemek,
  gelen mesajları enjekte etmek ve bir Markdown raporu dışa aktarmak için hata ayıklayıcı UI ve QA veri yolu.
- `qa/`: başlangıç görevi ve temel QA
  senaryoları için depo destekli tohum varlıkları.

Mevcut QA operatör akışı iki bölmeli bir QA sitesidir:

- Sol: ajanla birlikte Gateway panosu (Control UI).
- Sağ: Slack benzeri transkripti ve senaryo planını gösteren QA Lab.

Bunu şu komutla çalıştırın:

```bash
pnpm qa:lab:up
```

Bu, QA sitesini oluşturur, Docker destekli gateway hattını başlatır ve
bir operatörün veya otomasyon döngüsünün ajana bir QA
görevi verebildiği, gerçek kanal davranışını gözlemleyebildiği ve neyin çalıştığını, başarısız olduğunu veya
engelli kaldığını kaydedebildiği QA Lab sayfasını açığa çıkarır.

Docker image'ını her seferinde yeniden oluşturmadan daha hızlı QA Lab UI yinelemesi için,
yığını bind-mounted bir QA Lab paketiyle başlatın:

```bash
pnpm openclaw qa docker-build-image
pnpm qa:lab:build
pnpm qa:lab:up:fast
pnpm qa:lab:watch
```

`qa:lab:up:fast`, Docker servislerini önceden oluşturulmuş bir image üzerinde tutar ve
`extensions/qa-lab/web/dist` dizinini `qa-lab` container'ına bind-mount eder. `qa:lab:watch`
değişiklikte bu paketi yeniden oluşturur ve QA Lab
varlık hash'i değiştiğinde tarayıcı otomatik olarak yeniden yüklenir.

Taşıma açısından gerçek bir Matrix smoke hattı için şunu çalıştırın:

```bash
pnpm openclaw qa matrix
```

Bu hat, Docker içinde tek kullanımlık bir Tuwunel homeserver sağlar, geçici
sürücü, SUT ve gözlemci kullanıcıları kaydeder, bir özel oda oluşturur, ardından
gerçek Matrix Plugin'ini bir QA gateway child içinde çalıştırır. Canlı taşıma hattı child config'i
test edilen taşımaya kapsamlı tutar; bu nedenle Matrix, child config içinde
`qa-channel` olmadan çalışır.

Taşıma açısından gerçek bir Telegram smoke hattı için şunu çalıştırın:

```bash
pnpm openclaw qa telegram
```

Bu hat, tek kullanımlık bir sunucu sağlamak yerine gerçek bir özel Telegram grubunu hedefler.
`OPENCLAW_QA_TELEGRAM_GROUP_ID`,
`OPENCLAW_QA_TELEGRAM_DRIVER_BOT_TOKEN` ve
`OPENCLAW_QA_TELEGRAM_SUT_BOT_TOKEN` gerektirir; ayrıca aynı
özel grupta iki ayrı bot gerekir. SUT botunun bir Telegram kullanıcı adı olmalıdır ve
botlar arası gözlem, her iki botta da
`@BotFather` içinde Bot-to-Bot Communication Mode etkinleştirildiğinde en iyi şekilde çalışır.

Canlı taşıma hatları artık her birinin kendi senaryo listesi şeklini
icat etmesi yerine ortak, daha küçük bir sözleşmeyi paylaşıyor:

`qa-channel`, geniş sentetik ürün davranışı paketi olmaya devam eder ve
canlı taşıma kapsam matriksinin bir parçası değildir.

| Hat      | Canary | Mention gating | Allowlist block | Üst düzey yanıt | Yeniden başlatma sonrası sürdürme | İleti dizisi takibi | İleti dizisi yalıtımı | Tepki gözlemi | Yardım komutu |
| -------- | ------ | -------------- | --------------- | --------------- | --------------------------------- | ------------------- | -------------------- | ------------- | ------------- |
| Matrix   | x      | x              | x               | x               | x                                 | x                   | x                    | x             |               |
| Telegram | x      |                |                 |                 |                                   |                     |                      |               | x             |

Bu, `qa-channel`'ı geniş ürün davranışı paketi olarak korurken Matrix,
Telegram ve gelecekteki canlı taşımaların tek bir açık
taşıma sözleşmesi kontrol listesini paylaşmasını sağlar.

QA yoluna Docker katmadan tek kullanımlık bir Linux VM hattı için şunu çalıştırın:

```bash
pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline
```

Bu, yeni bir Multipass guest'i başlatır, bağımlılıkları kurar, guest içinde OpenClaw'ı oluşturur,
`qa suite` çalıştırır, ardından normal QA raporunu ve
özetini host üzerindeki `.artifacts/qa-e2e/...` dizinine geri kopyalar.
Host üzerindeki `qa suite` ile aynı senaryo seçimi davranışını yeniden kullanır.
Host ve Multipass suite çalıştırmaları, varsayılan olarak
yalıtılmış gateway worker'larıyla birden çok seçilmiş senaryoyu paralel çalıştırır; en fazla 64 worker veya seçilen
senaryo sayısı kullanılır. Worker sayısını ayarlamak için `--concurrency <count>`,
seri yürütme için ise `--concurrency 1` kullanın.
Canlı çalıştırmalar, guest için pratik olan desteklenen QA kimlik doğrulama girdilerini iletir:
env tabanlı sağlayıcı anahtarları, QA canlı sağlayıcı config yolu ve
varsa `CODEX_HOME`. Guest'in
bağlı çalışma alanı üzerinden geri yazabilmesi için `--output-dir` değerini depo kökü altında tutun.

## Depo destekli tohumlar

Tohum varlıkları `qa/` içinde bulunur:

- `qa/scenarios/index.md`
- `qa/scenarios/*.md`

Bunlar kasıtlı olarak git içindedir; böylece QA planı hem insanlar hem de
ajan için görünür olur.

`qa-lab` genel amaçlı bir markdown çalıştırıcısı olarak kalmalıdır. Her senaryo markdown dosyası
tek bir test çalıştırmasının doğruluk kaynağıdır ve şunları tanımlamalıdır:

- senaryo meta verileri
- doküman ve kod referansları
- isteğe bağlı Plugin gereksinimleri
- isteğe bağlı gateway config yaması
- yürütülebilir `qa-flow`

`qa-flow`'u destekleyen yeniden kullanılabilir çalışma zamanı yüzeyinin genel amaçlı
ve kesitler arası kalmasına izin verilir. Örneğin markdown senaryoları,
özel durumlu bir çalıştırıcı eklemeden gömülü Control UI'ı
Gateway `browser.request` yüzeyi üzerinden süren tarayıcı tarafı yardımcılarıyla taşıma tarafı yardımcılarını birleştirebilir.

Temel liste, şunları kapsayacak kadar geniş kalmalıdır:

- DM ve kanal sohbeti
- ileti dizisi davranışı
- mesaj eylemi yaşam döngüsü
- Cron geri çağrıları
- bellekten geri çağırma
- model değiştirme
- alt ajan devri
- depo okuma ve doküman okuma
- Lobster Invaders gibi küçük bir derleme görevi

## Taşıma bağdaştırıcıları

`qa-lab`, markdown QA senaryoları için genel bir taşıma yüzeyine sahiptir.
`qa-channel`, bu yüzeydeki ilk bağdaştırıcıdır; ancak tasarım hedefi daha geniştir:
gelecekteki gerçek veya sentetik kanallar, taşımaya özgü bir QA çalıştırıcısı eklemek yerine
aynı suite çalıştırıcısına takılmalıdır.

Mimari düzeyde ayrım şöyledir:

- `qa-lab`, genel senaryo yürütmeyi, worker eşzamanlılığını, artifact yazmayı ve raporlamayı yönetir.
- taşıma bağdaştırıcısı gateway config'ini, hazır olma durumunu, gelen ve giden gözlemi, taşıma eylemlerini ve normalize edilmiş taşıma durumunu yönetir.
- `qa/scenarios/` altındaki markdown senaryo dosyaları test çalıştırmasını tanımlar; bunları yürüten yeniden kullanılabilir çalışma zamanı yüzeyini `qa-lab` sağlar.

Yeni kanal bağdaştırıcıları için bakımcıya yönelik benimseme yönergeleri
[Testing](/tr/help/testing#adding-a-channel-to-qa) içinde bulunur.

## Raporlama

`qa-lab`, gözlemlenen veri yolu zaman çizelgesinden bir Markdown protokol raporu dışa aktarır.
Rapor şu sorulara yanıt vermelidir:

- Ne işe yaradı
- Ne başarısız oldu
- Ne engelli kaldı
- Hangi takip senaryolarını eklemeye değer

Karakter ve stil kontrolleri için aynı senaryoyu birden çok canlı model
ref'i üzerinde çalıştırın ve değerlendirilmiş bir Markdown raporu yazın:

```bash
pnpm openclaw qa character-eval \
  --model openai/gpt-5.4,thinking=xhigh \
  --model openai/gpt-5.2,thinking=xhigh \
  --model openai/gpt-5,thinking=xhigh \
  --model anthropic/claude-opus-4-6,thinking=high \
  --model anthropic/claude-sonnet-4-6,thinking=high \
  --model zai/glm-5.1,thinking=high \
  --model moonshot/kimi-k2.5,thinking=high \
  --model google/gemini-3.1-pro-preview,thinking=high \
  --judge-model openai/gpt-5.4,thinking=xhigh,fast \
  --judge-model anthropic/claude-opus-4-6,thinking=high \
  --blind-judge-models \
  --concurrency 16 \
  --judge-concurrency 16
```

Komut, Docker değil, yerel QA gateway child süreçlerini çalıştırır. Character eval
senaryoları persona'yı `SOUL.md` üzerinden ayarlamalı, ardından sohbet,
çalışma alanı yardımı ve küçük dosya görevleri gibi sıradan kullanıcı turlarını çalıştırmalıdır. Aday modele
değerlendirildiği söylenmemelidir. Komut her tam
transkripti korur, temel çalışma istatistiklerini kaydeder, ardından değerlendirme modellerinden fast mode ile
`xhigh` akıl yürütme kullanarak çalıştırmaları doğallık, hava ve mizaha göre sıralamalarını ister.
Sağlayıcıları karşılaştırırken `--blind-judge-models` kullanın: değerlendirme istemi yine de
her transkripti ve çalışma durumunu alır, ancak aday ref'leri
`candidate-01` gibi nötr etiketlerle değiştirilir; rapor ayrıştırmadan sonra sıralamaları gerçek ref'lere geri eşler.
Aday çalıştırmalar varsayılan olarak `high` thinking kullanır; bunu destekleyen OpenAI modelleri için
`xhigh` kullanılır. Belirli bir adayı satır içinde
`--model provider/model,thinking=<level>` ile geçersiz kılın. `--thinking <level>` hâlâ
genel bir yedek değer ayarlar ve eski `--model-thinking <provider/model=level>` biçimi
uyumluluk için korunur.
OpenAI aday ref'leri varsayılan olarak fast mode kullanır; böylece sağlayıcının bunu desteklediği yerlerde
öncelikli işleme kullanılır. Tek bir aday veya değerlendirici için geçersiz kılma gerektiğinde satır içinde
`,fast`, `,no-fast` veya `,fast=false` ekleyin. Fast mode'u her aday model için
zorla açmak istediğinizde yalnızca `--fast` geçin. Aday ve değerlendirici süreleri
kıyaslama analizi için rapora kaydedilir, ancak değerlendirici istemleri açıkça
hıza göre sıralama yapılmamasını söyler.
Aday ve değerlendirici model çalıştırmalarının her ikisi de varsayılan olarak 16 eşzamanlılıkla çalışır.
Sağlayıcı sınırları veya yerel gateway
yükü bir çalıştırmayı fazla gürültülü hale getiriyorsa `--concurrency` veya `--judge-concurrency` değerini düşürün.
Aday `--model` geçilmediğinde character eval varsayılan olarak
`openai/gpt-5.4`, `openai/gpt-5.2`, `openai/gpt-5`, `anthropic/claude-opus-4-6`,
`anthropic/claude-sonnet-4-6`, `zai/glm-5.1`,
`moonshot/kimi-k2.5` ve
`google/gemini-3.1-pro-preview` kullanır.
Değerlendirici `--judge-model` geçilmediğinde değerlendiriciler varsayılan olarak
`openai/gpt-5.4,thinking=xhigh,fast` ve
`anthropic/claude-opus-4-6,thinking=high` olur.

## İlgili dokümanlar

- [Testing](/tr/help/testing)
- [QA Channel](/tr/channels/qa-channel)
- [Dashboard](/web/dashboard)
