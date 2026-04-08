---
x-i18n:
    generated_at: "2026-04-08T02:18:25Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0e156cc8e2fe946a0423862f937754a7caa1fe7e6863b50a80bff49a1c86e1e8
    source_path: refactor/qa.md
    workflow: 15
---

# QA Yeniden Düzenleme

Durum: temel geçiş tamamlandı.

## Amaç

OpenClaw QA'yı bölünmüş tanım modelinden tek bir doğruluk kaynağına taşımak:

- senaryo meta verileri
- modele gönderilen istemler
- kurulum ve temizleme
- harness mantığı
- doğrulamalar ve başarı ölçütleri
- artifact'ler ve rapor ipuçları

İstenen son durum, davranışın çoğunu TypeScript içinde sabit kodlamak yerine güçlü senaryo tanım dosyaları yükleyen genel bir QA harness'idir.

## Mevcut Durum

Birincil doğruluk kaynağı artık `qa/scenarios.md` içinde bulunuyor.

Uygulananlar:

- `qa/scenarios.md`
  - kanonik QA paketi
  - operatör kimliği
  - başlangıç görevi
  - senaryo meta verileri
  - işleyici bağlamaları
- `extensions/qa-lab/src/scenario-catalog.ts`
  - markdown paket ayrıştırıcısı + zod doğrulaması
- `extensions/qa-lab/src/qa-agent-bootstrap.ts`
  - markdown paketinden plan oluşturma
- `extensions/qa-lab/src/qa-agent-workspace.ts`
  - oluşturulmuş uyumluluk dosyalarını ve `QA_SCENARIOS.md` dosyasını tohumlar
- `extensions/qa-lab/src/suite.ts`
  - çalıştırılabilir senaryoları markdown tanımlı işleyici bağlamaları üzerinden seçer
- QA veri yolu protokolü + UI
  - resim/video/ses/dosya işleme için genel satır içi ekler

Kalan bölünmüş yüzeyler:

- `extensions/qa-lab/src/suite.ts`
  - yürütülebilir özel işleyici mantığının çoğuna hâlâ sahip
- `extensions/qa-lab/src/report.ts`
  - rapor yapısını hâlâ çalışma zamanı çıktılarından türetiyor

Dolayısıyla doğruluk kaynağı bölünmesi düzeltildi, ancak yürütme hâlâ tam bildirime dayalı olmaktan çok çoğunlukla işleyici destekli.

## Gerçek Senaryo Yüzeyi Nasıl Görünüyor

Mevcut suite okunduğunda birkaç farklı senaryo sınıfı görülüyor.

### Basit etkileşim

- kanal taban çizgisi
- DM taban çizgisi
- iş parçacıklı takip
- model değiştirme
- onay tamamlama
- tepki/düzenleme/silme

### Yapılandırma ve çalışma zamanı mutasyonu

- config patch skill devre dışı bırakma
- config apply yeniden başlatma uyandırması
- config yeniden başlatma yetenek çevirme
- çalışma zamanı envanter kayması denetimi

### Dosya sistemi ve repo doğrulamaları

- kaynak/docs keşif raporu
- Lobster Invaders oluşturma
- oluşturulmuş görsel artifact arama

### Bellek orkestrasyonu

- bellek geri çağırma
- kanal bağlamında bellek araçları
- bellek başarısızlığı fallback'i
- oturum belleği sıralaması
- iş parçacığı bellek yalıtımı
- bellek rüya görme taraması

### Araç ve eklenti entegrasyonu

- MCP plugin-tools çağrısı
- skill görünürlüğü
- skill anında yükleme
- yerel görsel oluşturma
- görsel gidiş-dönüş
- ekten görsel anlama

### Çok turlu ve çok aktörlü

- alt ajan devri
- alt ajan fanout sentezi
- yeniden başlatma kurtarma tarzı akışlar

Bu kategoriler önemlidir çünkü DSL gereksinimlerini yönlendirir. Düz bir istem + beklenen metin listesi yeterli değildir.

## Yön

### Tek doğruluk kaynağı

Yazılan doğruluk kaynağı olarak `qa/scenarios.md` kullanın.

Paket şu özellikleri korumalıdır:

- incelemede insan tarafından okunabilir
- makine tarafından ayrıştırılabilir
- şunları yönetecek kadar zengin:
  - suite yürütmesi
  - QA çalışma alanı bootstrap'i
  - QA Lab UI meta verileri
  - docs/keşif istemleri
  - rapor oluşturma

### Tercih edilen yazım biçimi

Üst düzey biçim olarak markdown kullanın; içinde yapılandırılmış YAML olsun.

Önerilen biçim:

- YAML frontmatter
  - id
  - title
  - surface
  - tags
  - docs refs
  - code refs
  - model/provider override'ları
  - ön koşullar
- düz yazı bölümleri
  - amaç
  - notlar
  - hata ayıklama ipuçları
- fenced YAML blokları
  - setup
  - steps
  - assertions
  - cleanup

Bu şu avantajları sağlar:

- dev JSON'a göre daha iyi PR okunabilirliği
- saf YAML'a göre daha zengin bağlam
- katı ayrıştırma ve zod doğrulaması

Ham JSON yalnızca ara oluşturulmuş biçim olarak kabul edilebilir.

## Önerilen Senaryo Dosyası Biçimi

Örnek:

````md
---
id: image-generation-roundtrip
title: Image generation roundtrip
surface: image
tags: [media, image, roundtrip]
models:
  primary: openai/gpt-5.4
requires:
  tools: [image_generate]
  plugins: [openai, qa-channel]
docsRefs:
  - docs/help/testing.md
  - docs/concepts/model-providers.md
codeRefs:
  - extensions/qa-lab/src/suite.ts
  - src/gateway/chat-attachments.ts
---

# Objective

Verify generated media is reattached on the follow-up turn.

# Setup

```yaml scenario.setup
- action: config.patch
  patch:
    agents:
      defaults:
        imageGenerationModel:
          primary: openai/gpt-image-1
- action: session.create
  key: agent:qa:image-roundtrip
```

# Steps

```yaml scenario.steps
- action: agent.send
  session: agent:qa:image-roundtrip
  message: |
    Image generation check: generate a QA lighthouse image and summarize it in one short sentence.
- action: artifact.capture
  kind: generated-image
  promptSnippet: Image generation check
  saveAs: lighthouseImage
- action: agent.send
  session: agent:qa:image-roundtrip
  message: |
    Roundtrip image inspection check: describe the generated lighthouse attachment in one short sentence.
  attachments:
    - fromArtifact: lighthouseImage
```

# Expect

```yaml scenario.expect
- assert: outbound.textIncludes
  value: lighthouse
- assert: requestLog.matches
  where:
    promptIncludes: Roundtrip image inspection check
  imageInputCountGte: 1
- assert: artifact.exists
  ref: lighthouseImage
```
````

## DSL'nin Kapsaması Gereken Çalıştırıcı Yetenekleri

Mevcut suite'e göre, genel çalıştırıcı istem yürütmeden daha fazlasına ihtiyaç duyar.

### Ortam ve kurulum eylemleri

- `bus.reset`
- `gateway.waitHealthy`
- `channel.waitReady`
- `session.create`
- `thread.create`
- `workspace.writeSkill`

### Ajan turu eylemleri

- `agent.send`
- `agent.wait`
- `bus.injectInbound`
- `bus.injectOutbound`

### Yapılandırma ve çalışma zamanı eylemleri

- `config.get`
- `config.patch`
- `config.apply`
- `gateway.restart`
- `tools.effective`
- `skills.status`

### Dosya ve artifact eylemleri

- `file.write`
- `file.read`
- `file.delete`
- `file.touchTime`
- `artifact.captureGeneratedImage`
- `artifact.capturePath`

### Bellek ve cron eylemleri

- `memory.indexForce`
- `memory.searchCli`
- `doctor.memory.status`
- `cron.list`
- `cron.run`
- `cron.waitCompletion`
- `sessionTranscript.write`

### MCP eylemleri

- `mcp.callTool`

### Doğrulamalar

- `outbound.textIncludes`
- `outbound.inThread`
- `outbound.notInRoot`
- `tool.called`
- `tool.notPresent`
- `skill.visible`
- `skill.disabled`
- `file.contains`
- `memory.contains`
- `requestLog.matches`
- `sessionStore.matches`
- `cron.managedPresent`
- `artifact.exists`

## Değişkenler ve Artifact Referansları

DSL kaydedilmiş çıktıları ve daha sonra yapılan referansları desteklemelidir.

Mevcut suite'ten örnekler:

- bir iş parçacığı oluştur, sonra `threadId` değerini yeniden kullan
- bir oturum oluştur, sonra `sessionKey` değerini yeniden kullan
- bir görsel oluştur, sonra dosyayı sonraki turda ek olarak iliştir
- bir uyandırma işaretçisi dizesi oluştur, sonra bunun daha sonra göründüğünü doğrula

Gerekli yetenekler:

- `saveAs`
- `${vars.name}`
- `${artifacts.name}`
- yollar, oturum anahtarları, iş parçacığı kimlikleri, işaretçiler, araç çıktıları için türlendirilmiş referanslar

Değişken desteği olmadan harness, senaryo mantığını TypeScript'e geri sızdırmaya devam eder.

## Kaçış Kapısı Olarak Nelerin Kalması Gerekir

Tamamen saf bildirimsel bir çalıştırıcı 1. aşamada gerçekçi değildir.

Bazı senaryolar doğası gereği yoğun orkestrasyon gerektirir:

- bellek rüya görme taraması
- config apply yeniden başlatma uyandırması
- config yeniden başlatma yetenek çevirme
- zaman damgası/yola göre oluşturulmuş görsel artifact çözümleme
- discovery-report değerlendirmesi

Bunlar şimdilik açık özel işleyiciler kullanmalıdır.

Önerilen kural:

- %85-%90 bildirime dayalı
- geri kalan zor kısım için açık `customHandler` adımları
- yalnızca adlandırılmış ve belgelenmiş özel işleyiciler
- senaryo dosyasında anonim satır içi kod yok

Bu, ilerlemeye izin verirken genel motoru temiz tutar.

## Mimari Değişiklik

### Mevcut

Senaryo markdown'u zaten şu alanlar için doğruluk kaynağıdır:

- suite yürütmesi
- çalışma alanı bootstrap dosyaları
- QA Lab UI senaryo kataloğu
- rapor meta verileri
- keşif istemleri

Oluşturulan uyumluluk:

- tohumlanmış çalışma alanı hâlâ `QA_KICKOFF_TASK.md` içeriyor
- tohumlanmış çalışma alanı hâlâ `QA_SCENARIO_PLAN.md` içeriyor
- tohumlanmış çalışma alanı artık ayrıca `QA_SCENARIOS.md` içeriyor

## Yeniden Düzenleme Planı

### Aşama 1: yükleyici ve şema

Tamamlandı.

- `qa/scenarios.md` eklendi
- adlandırılmış markdown YAML paket içeriği için ayrıştırıcı eklendi
- zod ile doğrulandı
- tüketiciler ayrıştırılmış pakete geçirildi
- repo düzeyi `qa/seed-scenarios.json` ve `qa/QA_KICKOFF_TASK.md` kaldırıldı

### Aşama 2: genel motor

- `extensions/qa-lab/src/suite.ts` dosyasını şunlara ayır:
  - yükleyici
  - motor
  - eylem kayıt defteri
  - doğrulama kayıt defteri
  - özel işleyiciler
- mevcut yardımcı işlevleri motor işlemleri olarak tut

Teslim edilecek çıktı:

- motor, basit bildirimsel senaryoları yürütür

Çoğunlukla istem + bekleme + doğrulamadan oluşan senaryolarla başlayın:

- iş parçacıklı takip
- ekten görsel anlama
- skill görünürlüğü ve çağrılması
- kanal taban çizgisi

Teslim edilecek çıktı:

- ilk gerçek markdown tanımlı senaryolar genel motor üzerinden yayımlanıyor

### Aşama 4: orta düzey senaryoları taşı

- görsel oluşturma gidiş-dönüş
- kanal bağlamında bellek araçları
- oturum belleği sıralaması
- alt ajan devri
- alt ajan fanout sentezi

Teslim edilecek çıktı:

- değişkenler, artifact'ler, araç doğrulamaları, request-log doğrulamaları kanıtlanmış olur

### Aşama 5: zor senaryoları özel işleyicilerde tut

- bellek rüya görme taraması
- config apply yeniden başlatma uyandırması
- config yeniden başlatma yetenek çevirme
- çalışma zamanı envanter kayması

Teslim edilecek çıktı:

- aynı yazım biçimi, ancak gerektiğinde açık özel adım bloklarıyla

### Aşama 6: sabit kodlanmış senaryo haritasını sil

Paket kapsamı yeterince iyi olduğunda:

- `extensions/qa-lab/src/suite.ts` içindeki senaryoya özgü TypeScript dallanmasının çoğunu kaldır

## Sahte Slack / Zengin Medya Desteği

Mevcut QA veri yolu önce metne odaklıdır.

İlgili dosyalar:

- `extensions/qa-channel/src/protocol.ts`
- `extensions/qa-lab/src/bus-state.ts`
- `extensions/qa-lab/src/bus-queries.ts`
- `extensions/qa-lab/src/bus-server.ts`
- `extensions/qa-lab/web/src/ui-render.ts`

Bugün QA veri yolu şunları destekler:

- metin
- tepkiler
- iş parçacıkları

Henüz satır içi medya eklerini modellemiyor.

### Gerekli taşıma sözleşmesi

Genel bir QA veri yolu ek modeli ekleyin:

```ts
type QaBusAttachment = {
  id: string;
  kind: "image" | "video" | "audio" | "file";
  mimeType: string;
  fileName?: string;
  inline?: boolean;
  url?: string;
  contentBase64?: string;
  width?: number;
  height?: number;
  durationMs?: number;
  altText?: string;
  transcript?: string;
};
```

Sonra `attachments?: QaBusAttachment[]` alanını şunlara ekleyin:

- `QaBusMessage`
- `QaBusInboundMessageInput`
- `QaBusOutboundMessageInput`

### Neden önce genel

Yalnızca Slack'e özgü bir medya modeli oluşturmayın.

Bunun yerine:

- tek bir genel QA taşıma modeli
- bunun üzerinde birden çok işleyici
  - mevcut QA Lab sohbeti
  - gelecekteki sahte Slack web
  - diğer olası sahte taşıma görünümleri

Bu yaklaşım yinelenen mantığı önler ve medya senaryolarının taşıma bağımsız kalmasını sağlar.

### Gereken UI çalışması

QA UI'ı şunları işleyebilecek şekilde güncelleyin:

- satır içi görsel önizlemesi
- satır içi ses oynatıcı
- satır içi video oynatıcı
- dosya eki çipi

Mevcut UI zaten iş parçacıklarını ve tepkileri işleyebiliyor, bu nedenle ek işleme aynı mesaj kartı modeli üzerine katman olarak eklenmelidir.

### Medya taşımasıyla etkinleşen senaryo çalışması

Ekler QA veri yolundan akmaya başladığında daha zengin sahte sohbet senaryoları ekleyebiliriz:

- sahte Slack'te satır içi görsel yanıtı
- ses eki anlama
- video eki anlama
- karışık ek sıralaması
- medyayı koruyan iş parçacığı yanıtı

## Öneri

Sonraki uygulama parçası şu olmalıdır:

1. markdown senaryo yükleyicisi + zod şeması ekle
2. mevcut kataloğu markdown'dan oluştur
3. önce birkaç basit senaryoyu taşı
4. genel QA veri yolu ek desteği ekle
5. QA UI'da satır içi görseli işle
6. sonra ses ve videoya genişlet

Bu, her iki hedefi de kanıtlayan en küçük yoldur:

- genel markdown tanımlı QA
- daha zengin sahte mesajlaşma yüzeyleri

## Açık Sorular

- senaryo dosyalarının değişken enterpolasyonu ile gömülü markdown istem şablonlarına izin verip vermemesi gerektiği
- setup/cleanup bölümlerinin adlandırılmış bölümler mi yoksa yalnızca sıralı eylem listeleri mi olması gerektiği
- artifact referanslarının şemada güçlü biçimde türlendirilmiş mi yoksa dize tabanlı mı olması gerektiği
- özel işleyicilerin tek bir kayıt defterinde mi yoksa yüzey başına kayıt defterlerinde mi yaşaması gerektiği
- oluşturulan JSON uyumluluk dosyasının geçiş sırasında sürüm kontrolünde tutulmaya devam edip etmemesi gerektiği
