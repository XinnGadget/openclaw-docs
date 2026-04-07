---
read_when:
    - OpenClaw'ın model bağlamını nasıl oluşturduğunu anlamak istiyorsunuz
    - Eski motor ile bir eklenti motoru arasında geçiş yapıyorsunuz
    - Bir bağlam motoru eklentisi geliştiriyorsunuz
summary: 'Bağlam motoru: takılabilir bağlam oluşturma, sıkıştırma ve alt aracı yaşam döngüsü'
title: Bağlam Motoru
x-i18n:
    generated_at: "2026-04-07T08:43:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: e8290ac73272eee275bce8e481ac7959b65386752caa68044d0c6f3e450acfb1
    source_path: concepts/context-engine.md
    workflow: 15
---

# Bağlam Motoru

Bir **bağlam motoru**, OpenClaw'ın her çalıştırma için model bağlamını nasıl oluşturduğunu denetler.
Hangi mesajların dahil edileceğine, eski geçmişin nasıl özetleneceğine ve
alt aracı sınırları arasında bağlamın nasıl yönetileceğine karar verir.

OpenClaw, yerleşik bir `legacy` motoruyla gelir. Eklentiler,
etkin bağlam motoru yaşam döngüsünün yerine geçen alternatif motorlar
kaydedebilir.

## Hızlı başlangıç

Hangi motorun etkin olduğunu kontrol edin:

```bash
openclaw doctor
# veya yapılandırmayı doğrudan inceleyin:
cat ~/.openclaw/openclaw.json | jq '.plugins.slots.contextEngine'
```

### Bir bağlam motoru eklentisi yükleme

Bağlam motoru eklentileri, diğer tüm OpenClaw eklentileri gibi yüklenir. Önce
yükleyin, ardından yuvadaki motoru seçin:

```bash
# npm üzerinden yükleyin
openclaw plugins install @martian-engineering/lossless-claw

# Veya yerel bir yoldan yükleyin (geliştirme için)
openclaw plugins install -l ./my-context-engine
```

Ardından eklentiyi etkinleştirin ve yapılandırmanızda etkin motor olarak seçin:

```json5
// openclaw.json
{
  plugins: {
    slots: {
      contextEngine: "lossless-claw", // eklentinin kaydettiği motor kimliğiyle eşleşmelidir
    },
    entries: {
      "lossless-claw": {
        enabled: true,
        // Eklentiye özgü yapılandırma buraya gelir (eklenti belgelerine bakın)
      },
    },
  },
}
```

Yükleme ve yapılandırmadan sonra ağ geçidini yeniden başlatın.

Yerleşik motora geri dönmek için `contextEngine` değerini `"legacy"` olarak ayarlayın (veya
anahtarı tamamen kaldırın — varsayılan `"legacy"` değeridir).

## Nasıl çalışır

OpenClaw her model istemini çalıştırdığında, bağlam motoru
dört yaşam döngüsü noktasında devreye girer:

1. **İçe alım** — oturuma yeni bir mesaj eklendiğinde çağrılır. Motor,
   mesajı kendi veri deposunda saklayabilir veya dizinleyebilir.
2. **Birleştirme** — her model çalıştırmasından önce çağrılır. Motor,
   belirteç bütçesine sığan sıralı bir mesaj kümesi
   (ve isteğe bağlı bir `systemPromptAddition`) döndürür.
3. **Sıkıştırma** — bağlam penceresi dolduğunda veya kullanıcı
   `/compact` komutunu çalıştırdığında çağrılır. Motor, alan açmak için eski geçmişi özetler.
4. **Tur sonrası** — bir çalıştırma tamamlandıktan sonra çağrılır. Motor durumu kalıcı hale getirebilir,
   arka planda sıkıştırma tetikleyebilir veya dizinleri güncelleyebilir.

### Alt aracı yaşam döngüsü (isteğe bağlı)

OpenClaw şu anda bir alt aracı yaşam döngüsü kancasını çağırır:

- **onSubagentEnded** — bir alt aracı oturumu tamamlandığında veya temizlendiğinde temizlik yapar.

`prepareSubagentSpawn` kancası gelecekte kullanılmak üzere arayüzün bir parçasıdır, ancak
çalışma zamanı onu henüz çağırmaz.

### Sistem istemi eki

`assemble` yöntemi bir `systemPromptAddition` dizesi döndürebilir. OpenClaw
bunu çalıştırma için sistem isteminin başına ekler. Bu, motorların
statik çalışma alanı dosyaları gerektirmeden dinamik geri çağırma rehberliği,
getirme talimatları veya bağlama duyarlı ipuçları eklemesine olanak tanır.

## legacy motoru

Yerleşik `legacy` motoru, OpenClaw'ın özgün davranışını korur:

- **İçe alım**: no-op (mesaj kalıcılığını doğrudan oturum yöneticisi işler).
- **Birleştirme**: geçişli (çalışma zamanındaki mevcut sanitize → validate → limit işlem hattı
  bağlam oluşturmayı yönetir).
- **Sıkıştırma**: eski mesajların tek bir özetini oluşturan ve son mesajları bozulmadan tutan
  yerleşik özetleme sıkıştırmasına devreder.
- **Tur sonrası**: no-op.

legacy motoru araç kaydetmez ve bir `systemPromptAddition` sağlamaz.

Hiçbir `plugins.slots.contextEngine` ayarlanmadığında (veya `"legacy"` olarak ayarlandığında), bu
motor otomatik olarak kullanılır.

## Eklenti motorları

Bir eklenti, eklenti API'sini kullanarak bir bağlam motoru kaydedebilir:

```ts
import { buildMemorySystemPromptAddition } from "openclaw/plugin-sdk/core";

export default function register(api) {
  api.registerContextEngine("my-engine", () => ({
    info: {
      id: "my-engine",
      name: "My Context Engine",
      ownsCompaction: true,
    },

    async ingest({ sessionId, message, isHeartbeat }) {
      // Store the message in your data store
      return { ingested: true };
    },

    async assemble({ sessionId, messages, tokenBudget, availableTools, citationsMode }) {
      // Return messages that fit the budget
      return {
        messages: buildContext(messages, tokenBudget),
        estimatedTokens: countTokens(messages),
        systemPromptAddition: buildMemorySystemPromptAddition({
          availableTools: availableTools ?? new Set(),
          citationsMode,
        }),
      };
    },

    async compact({ sessionId, force }) {
      // Summarize older context
      return { ok: true, compacted: true };
    },
  }));
}
```

Ardından bunu yapılandırmada etkinleştirin:

```json5
{
  plugins: {
    slots: {
      contextEngine: "my-engine",
    },
    entries: {
      "my-engine": {
        enabled: true,
      },
    },
  },
}
```

### ContextEngine arayüzü

Gerekli üyeler:

| Üye                | Tür      | Amaç                                                     |
| ------------------ | -------- | -------------------------------------------------------- |
| `info`             | Özellik  | Motor kimliği, adı, sürümü ve sıkıştırmanın kendisine ait olup olmadığı |
| `ingest(params)`   | Yöntem   | Tek bir mesajı depolama                                  |
| `assemble(params)` | Yöntem   | Bir model çalıştırması için bağlam oluşturma (`AssembleResult` döndürür) |
| `compact(params)`  | Yöntem   | Bağlamı özetleme/azaltma                                 |

`assemble`, şu öğeleri içeren bir `AssembleResult` döndürür:

- `messages` — modele gönderilecek sıralı mesajlar.
- `estimatedTokens` (zorunlu, `number`) — motorun oluşturulan bağlamdaki toplam
  belirteç sayısına ilişkin tahmini. OpenClaw bunu sıkıştırma eşiği
  kararları ve tanılama raporlaması için kullanır.
- `systemPromptAddition` (isteğe bağlı, `string`) — sistem isteminin başına eklenir.

İsteğe bağlı üyeler:

| Üye                            | Tür    | Amaç                                                                                                            |
| ------------------------------ | ------ | --------------------------------------------------------------------------------------------------------------- |
| `bootstrap(params)`            | Yöntem | Bir oturum için motor durumunu başlatma. Motor bir oturumu ilk kez gördüğünde bir kez çağrılır (ör. geçmişi içe aktarma). |
| `ingestBatch(params)`          | Yöntem | Tamamlanmış bir turu toplu olarak içe alma. Bir çalıştırma tamamlandıktan sonra, o turdaki tüm mesajlarla birlikte tek seferde çağrılır. |
| `afterTurn(params)`            | Yöntem | Çalıştırma sonrası yaşam döngüsü işi (durumu kalıcı hale getirme, arka planda sıkıştırma tetikleme).          |
| `prepareSubagentSpawn(params)` | Yöntem | Bir alt oturum için paylaşılan durumu hazırlama.                                                                |
| `onSubagentEnded(params)`      | Yöntem | Bir alt aracı sona erdikten sonra temizlik yapma.                                                               |
| `dispose()`                    | Yöntem | Kaynakları serbest bırakma. Ağ geçidi kapanışı veya eklenti yeniden yüklenmesi sırasında çağrılır — oturum başına değil. |

### ownsCompaction

`ownsCompaction`, Pi'nin yerleşik deneme içi otomatik sıkıştırmasının
çalıştırma için etkin kalıp kalmayacağını denetler:

- `true` — motor sıkıştırma davranışının sahibidir. OpenClaw, o çalıştırma için Pi'nin yerleşik
  otomatik sıkıştırmasını devre dışı bırakır ve motorun `compact()` uygulaması
  `/compact`, taşma kurtarma sıkıştırması ve `afterTurn()` içinde yapmak istediği
  tüm proaktif sıkıştırmalardan sorumlu olur.
- `false` veya ayarlanmamış — Pi'nin yerleşik otomatik sıkıştırması istem
  yürütme sırasında yine de çalışabilir, ancak etkin motorun `compact()` yöntemi
  `/compact` ve taşma kurtarma için yine de çağrılır.

`ownsCompaction: false`, OpenClaw'ın otomatik olarak
legacy motorunun sıkıştırma yoluna geri döndüğü anlamına **gelmez**.

Bu da iki geçerli eklenti deseni olduğu anlamına gelir:

- **Sahiplenen mod** — kendi sıkıştırma algoritmanızı uygulayın ve
  `ownsCompaction: true` olarak ayarlayın.
- **Devreden mod** — `ownsCompaction: false` olarak ayarlayın ve
  OpenClaw'ın yerleşik sıkıştırma davranışını kullanmak için `compact()` içinde
  `openclaw/plugin-sdk/core` içinden `delegateCompactionToRuntime(...)` çağırın.

Etkin, sahiplenmeyen bir motor için no-op bir `compact()` güvenli değildir çünkü
o motor yuvası için normal `/compact` ve taşma kurtarma sıkıştırma yolunu
devre dışı bırakır.

## Yapılandırma başvurusu

```json5
{
  plugins: {
    slots: {
      // Etkin bağlam motorunu seçin. Varsayılan: "legacy".
      // Bir eklenti motoru kullanmak için bunu bir eklenti kimliğine ayarlayın.
      contextEngine: "legacy",
    },
  },
}
```

Yuva çalışma zamanında özeldir — belirli bir çalıştırma veya sıkıştırma işlemi için
yalnızca bir kayıtlı bağlam motoru çözülür. Etkin durumdaki diğer
`kind: "context-engine"` eklentileri yine de yüklenebilir ve kayıt
kodlarını çalıştırabilir; `plugins.slots.contextEngine` yalnızca OpenClaw'ın
bir bağlam motoruna ihtiyaç duyduğunda hangi kayıtlı motor kimliğini
çözeceğini seçer.

## Sıkıştırma ve bellek ile ilişkisi

- **Sıkıştırma**, bağlam motorunun sorumluluklarından biridir. legacy motoru,
  OpenClaw'ın yerleşik özetlemesine devreder. Eklenti motorları herhangi bir
  sıkıştırma stratejisi uygulayabilir (DAG özetleri, vektör getirme vb.).
- **Bellek eklentileri** (`plugins.slots.memory`), bağlam motorlarından ayrıdır.
  Bellek eklentileri arama/getirme sağlar; bağlam motorları modelin
  ne gördüğünü denetler. Birlikte çalışabilirler — bir bağlam motoru
  birleştirme sırasında bellek eklentisi verilerini kullanabilir. Etkin bellek
  istem yolunu isteyen eklenti motorları, etkin bellek istem bölümlerini
  başa eklenmeye hazır bir `systemPromptAddition` öğesine dönüştüren
  `openclaw/plugin-sdk/core` içindeki `buildMemorySystemPromptAddition(...)`
  yöntemini tercih etmelidir. Bir motor daha düşük seviyeli
  denetim gerektiriyorsa, ham satırları yine de
  `openclaw/plugin-sdk/memory-host-core` üzerinden
  `buildActiveMemoryPromptSection(...)` ile çekebilir.
- **Oturum budama** (eski araç sonuçlarını bellekte kırpma), hangi bağlam motorunun etkin olduğuna
  bakılmaksızın yine de çalışır.

## İpuçları

- Motorunuzun doğru yüklendiğini doğrulamak için `openclaw doctor` kullanın.
- Motor değiştiriyorsanız, mevcut oturumlar mevcut geçmişleriyle devam eder.
  Yeni motor gelecekteki çalıştırmaları devralır.
- Motor hataları günlüklenir ve tanılamalarda gösterilir. Bir eklenti motoru
  kaydolamazsa veya seçili motor kimliği çözülemezse, OpenClaw
  otomatik olarak geri dönmez; eklentiyi düzeltene veya
  `plugins.slots.contextEngine` değerini `"legacy"` olarak geri değiştirene kadar çalıştırmalar başarısız olur.
- Geliştirme için, yerel bir eklenti dizinini kopyalamadan bağlamak üzere
  `openclaw plugins install -l ./my-engine` kullanın.

Ayrıca bakın: [Sıkıştırma](/tr/concepts/compaction), [Bağlam](/tr/concepts/context),
[Eklentiler](/tr/tools/plugin), [Eklenti manifesti](/tr/plugins/manifest).

## İlgili

- [Bağlam](/tr/concepts/context) — aracı turları için bağlamın nasıl oluşturulduğu
- [Eklenti Mimarisi](/tr/plugins/architecture) — bağlam motoru eklentilerini kaydetme
- [Sıkıştırma](/tr/concepts/compaction) — uzun konuşmaları özetleme
