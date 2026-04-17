---
read_when:
    - Bellek arama sağlayıcılarını veya gömme modellerini yapılandırmak istiyorsunuz
    - QMD arka ucunu kurmak istiyorsunuz
    - Hibrit aramayı, MMR'yi veya zamansal azalmayı ayarlamak istiyorsunuz
    - Çok modlu bellek dizinlemeyi etkinleştirmek istiyorsunuz
summary: Bellek araması, gömme sağlayıcıları, QMD, hibrit arama ve çok modlu dizinleme için tüm yapılandırma seçenekleri
title: Bellek yapılandırma başvurusu
x-i18n:
    generated_at: "2026-04-15T14:41:01Z"
    model: gpt-5.4
    provider: openai
    source_hash: 334c3c4dac08e864487047d3822c75f96e9e7a97c38be4b4e0cd9e63c4489a53
    source_path: reference/memory-config.md
    workflow: 15
---

# Bellek yapılandırma başvurusu

Bu sayfa, OpenClaw bellek araması için her yapılandırma seçeneğini listeler. Kavramsal genel bakışlar için şunlara bakın:

- [Belleğe Genel Bakış](/tr/concepts/memory) -- belleğin nasıl çalıştığı
- [Yerleşik Motor](/tr/concepts/memory-builtin) -- varsayılan SQLite arka ucu
- [QMD Motoru](/tr/concepts/memory-qmd) -- önce yerel çalışan sidecar
- [Bellek Araması](/tr/concepts/memory-search) -- arama hattı ve ayarlama
- [Active Memory](/tr/concepts/active-memory) -- etkileşimli oturumlar için bellek alt ajanını etkinleştirme

Aksi belirtilmedikçe tüm bellek araması ayarları `openclaw.json` içindeki
`agents.defaults.memorySearch` altında bulunur.

**Active Memory** özellik anahtarını ve alt ajan yapılandırmasını arıyorsanız,
bu ayar `memorySearch` yerine `plugins.entries.active-memory` altında bulunur.

Active Memory iki kapılı bir model kullanır:

1. Plugin etkin olmalı ve geçerli ajan kimliğini hedeflemelidir
2. İstek, uygun bir etkileşimli kalıcı sohbet oturumu olmalıdır

Etkinleştirme modeli, Plugin'e ait yapılandırma, döküm kalıcılığı ve güvenli
yaygınlaştırma deseni için [Active Memory](/tr/concepts/active-memory) bölümüne bakın.

---

## Sağlayıcı seçimi

| Anahtar   | Tür       | Varsayılan      | Açıklama                                                                                                      |
| --------- | --------- | --------------- | ------------------------------------------------------------------------------------------------------------- |
| `provider` | `string` | otomatik algılanır | Gömme bağdaştırıcısı kimliği: `bedrock`, `gemini`, `github-copilot`, `local`, `mistral`, `ollama`, `openai`, `voyage` |
| `model`   | `string`  | sağlayıcı varsayılanı | Gömme modeli adı                                                                                         |
| `fallback` | `string` | `"none"`        | Birincil başarısız olduğunda geri dönüş bağdaştırıcısı kimliği                                              |
| `enabled` | `boolean` | `true`          | Bellek aramasını etkinleştirir veya devre dışı bırakır                                                       |

### Otomatik algılama sırası

`provider` ayarlanmadığında, OpenClaw kullanılabilir ilk seçeneği seçer:

1. `local` -- `memorySearch.local.modelPath` yapılandırılmışsa ve dosya mevcutsa.
2. `github-copilot` -- bir GitHub Copilot belirteci çözümlenebiliyorsa (ortam değişkeni veya kimlik doğrulama profili).
3. `openai` -- bir OpenAI anahtarı çözümlenebiliyorsa.
4. `gemini` -- bir Gemini anahtarı çözümlenebiliyorsa.
5. `voyage` -- bir Voyage anahtarı çözümlenebiliyorsa.
6. `mistral` -- bir Mistral anahtarı çözümlenebiliyorsa.
7. `bedrock` -- AWS SDK kimlik bilgisi zinciri çözümlenebiliyorsa (örnek rolü, erişim anahtarları, profil, SSO, web kimliği veya paylaşılan yapılandırma).

`ollama` desteklenir ancak otomatik algılanmaz (açıkça ayarlayın).

### API anahtarı çözümleme

Uzak gömmeler bir API anahtarı gerektirir. Bunun yerine Bedrock, AWS SDK’nin
varsayılan kimlik bilgisi zincirini kullanır (örnek rolleri, SSO, erişim anahtarları).

| Sağlayıcı      | Ortam değişkeni                                  | Yapılandırma anahtarı            |
| -------------- | ------------------------------------------------ | -------------------------------- |
| Bedrock        | AWS kimlik bilgisi zinciri                       | API anahtarı gerekmez            |
| Gemini         | `GEMINI_API_KEY`                                 | `models.providers.google.apiKey` |
| GitHub Copilot | `COPILOT_GITHUB_TOKEN`, `GH_TOKEN`, `GITHUB_TOKEN` | Cihaz oturumu açma yoluyla kimlik doğrulama profili |
| Mistral        | `MISTRAL_API_KEY`                                | `models.providers.mistral.apiKey` |
| Ollama         | `OLLAMA_API_KEY` (yer tutucu)                    | --                               |
| OpenAI         | `OPENAI_API_KEY`                                 | `models.providers.openai.apiKey` |
| Voyage         | `VOYAGE_API_KEY`                                 | `models.providers.voyage.apiKey` |

Codex OAuth yalnızca sohbet/completions isteklerini kapsar ve gömme
isteklerini karşılamaz.

---

## Uzak uç nokta yapılandırması

Özel OpenAI uyumlu uç noktalar veya sağlayıcı varsayılanlarını geçersiz kılmak için:

| Anahtar           | Tür      | Açıklama                                |
| ----------------- | -------- | --------------------------------------- |
| `remote.baseUrl`  | `string` | Özel API temel URL’si                   |
| `remote.apiKey`   | `string` | API anahtarını geçersiz kılar           |
| `remote.headers`  | `object` | Ek HTTP üstbilgileri (sağlayıcı varsayılanlarıyla birleştirilir) |

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "openai",
        model: "text-embedding-3-small",
        remote: {
          baseUrl: "https://api.example.com/v1/",
          apiKey: "YOUR_KEY",
        },
      },
    },
  },
}
```

---

## Gemini'ye özgü yapılandırma

| Anahtar                | Tür      | Varsayılan             | Açıklama                                   |
| ---------------------- | -------- | ---------------------- | ------------------------------------------ |
| `model`                | `string` | `gemini-embedding-001` | Ayrıca `gemini-embedding-2-preview` desteklenir |
| `outputDimensionality` | `number` | `3072`                 | Embedding 2 için: 768, 1536 veya 3072      |

<Warning>
`model` veya `outputDimensionality` değerini değiştirmek otomatik olarak tam bir yeniden dizinlemeyi tetikler.
</Warning>

---

## Bedrock gömme yapılandırması

Bedrock, AWS SDK’nin varsayılan kimlik bilgisi zincirini kullanır -- API anahtarı gerekmez.
OpenClaw, Bedrock etkin örnek rolüne sahip bir EC2 üzerinde çalışıyorsa, yalnızca
sağlayıcıyı ve modeli ayarlamanız yeterlidir:

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "bedrock",
        model: "amazon.titan-embed-text-v2:0",
      },
    },
  },
}
```

| Anahtar                | Tür      | Varsayılan                   | Açıklama                         |
| ---------------------- | -------- | ---------------------------- | -------------------------------- |
| `model`                | `string` | `amazon.titan-embed-text-v2:0` | Herhangi bir Bedrock gömme model kimliği |
| `outputDimensionality` | `number` | model varsayılanı            | Titan V2 için: 256, 512 veya 1024 |

### Desteklenen modeller

Aşağıdaki modeller desteklenir (aile algılama ve boyut varsayılanlarıyla birlikte):

| Model Kimliği                               | Sağlayıcı  | Varsayılan Boyut | Yapılandırılabilir Boyut |
| ------------------------------------------- | ---------- | ---------------- | ------------------------ |
| `amazon.titan-embed-text-v2:0`              | Amazon     | 1024             | 256, 512, 1024           |
| `amazon.titan-embed-text-v1`                | Amazon     | 1536             | --                       |
| `amazon.titan-embed-g1-text-02`             | Amazon     | 1536             | --                       |
| `amazon.titan-embed-image-v1`               | Amazon     | 1024             | --                       |
| `amazon.nova-2-multimodal-embeddings-v1:0`  | Amazon     | 1024             | 256, 384, 1024, 3072     |
| `cohere.embed-english-v3`                   | Cohere     | 1024             | --                       |
| `cohere.embed-multilingual-v3`              | Cohere     | 1024             | --                       |
| `cohere.embed-v4:0`                         | Cohere     | 1536             | 256-1536                 |
| `twelvelabs.marengo-embed-3-0-v1:0`         | TwelveLabs | 512              | --                       |
| `twelvelabs.marengo-embed-2-7-v1:0`         | TwelveLabs | 1024             | --                       |

Verim eki alan varyantlar (ör. `amazon.titan-embed-text-v1:2:8k`) temel modelin
yapılandırmasını devralır.

### Kimlik doğrulama

Bedrock kimlik doğrulaması, standart AWS SDK kimlik bilgisi çözümleme sırasını kullanır:

1. Ortam değişkenleri (`AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`)
2. SSO belirteç önbelleği
3. Web kimliği belirteci kimlik bilgileri
4. Paylaşılan kimlik bilgileri ve yapılandırma dosyaları
5. ECS veya EC2 meta veri kimlik bilgileri

Bölge, `AWS_REGION`, `AWS_DEFAULT_REGION`, `amazon-bedrock`
sağlayıcısının `baseUrl` değeri üzerinden çözümlenir veya varsayılan olarak `us-east-1` kullanılır.

### IAM izinleri

IAM rolü veya kullanıcısı şuna ihtiyaç duyar:

```json
{
  "Effect": "Allow",
  "Action": "bedrock:InvokeModel",
  "Resource": "*"
}
```

En az ayrıcalık için `InvokeModel` yetkisini belirli modele daraltın:

```
arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v2:0
```

---

## Yerel gömme yapılandırması

| Anahtar               | Tür      | Varsayılan              | Açıklama                         |
| --------------------- | -------- | ----------------------- | -------------------------------- |
| `local.modelPath`     | `string` | otomatik indirilir      | GGUF model dosyasının yolu       |
| `local.modelCacheDir` | `string` | node-llama-cpp varsayılanı | İndirilen modeller için önbellek dizini |

Varsayılan model: `embeddinggemma-300m-qat-Q8_0.gguf` (~0.6 GB, otomatik indirilir).
Yerel derleme gerektirir: `pnpm approve-builds` ardından `pnpm rebuild node-llama-cpp`.

---

## Hibrit arama yapılandırması

Tümü `memorySearch.query.hybrid` altında bulunur:

| Anahtar              | Tür       | Varsayılan | Açıklama                           |
| -------------------- | --------- | ---------- | ---------------------------------- |
| `enabled`            | `boolean` | `true`     | Hibrit BM25 + vektör aramasını etkinleştirir |
| `vectorWeight`       | `number`  | `0.7`      | Vektör puanları için ağırlık (0-1) |
| `textWeight`         | `number`  | `0.3`      | BM25 puanları için ağırlık (0-1)   |
| `candidateMultiplier` | `number` | `4`        | Aday havuzu boyutu çarpanı         |

### MMR (çeşitlilik)

| Anahtar       | Tür       | Varsayılan | Açıklama                                  |
| ------------- | --------- | ---------- | ----------------------------------------- |
| `mmr.enabled` | `boolean` | `false`    | MMR yeniden sıralamasını etkinleştirir    |
| `mmr.lambda`  | `number`  | `0.7`      | 0 = en yüksek çeşitlilik, 1 = en yüksek alaka |

### Zamansal azalma (güncellik)

| Anahtar                     | Tür       | Varsayılan | Açıklama                     |
| --------------------------- | --------- | ---------- | ---------------------------- |
| `temporalDecay.enabled`     | `boolean` | `false`    | Güncellik artışını etkinleştirir |
| `temporalDecay.halfLifeDays` | `number` | `30`       | Puan her N günde yarıya iner |

Kalıcı dosyalara (`MEMORY.md`, `memory/` içindeki tarihsiz dosyalar) hiçbir zaman azalma uygulanmaz.

### Tam örnek

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        query: {
          hybrid: {
            vectorWeight: 0.7,
            textWeight: 0.3,
            mmr: { enabled: true, lambda: 0.7 },
            temporalDecay: { enabled: true, halfLifeDays: 30 },
          },
        },
      },
    },
  },
}
```

---

## Ek bellek yolları

| Anahtar      | Tür        | Açıklama                                 |
| ------------ | ---------- | ---------------------------------------- |
| `extraPaths` | `string[]` | Dizinlenecek ek dizinler veya dosyalar   |

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        extraPaths: ["../team-docs", "/srv/shared-notes"],
      },
    },
  },
}
```

Yollar mutlak veya çalışma alanına göreli olabilir. Dizinler, `.md` dosyaları için
özyinelemeli olarak taranır. Sembolik bağlantı işleme etkin arka uca bağlıdır:
yerleşik motor sembolik bağlantıları yok sayar, QMD ise alttaki QMD
tarayıcısının davranışını izler.

Ajan kapsamlı, ajanlar arası döküm araması için
`memory.qmd.paths` yerine `agents.list[].memorySearch.qmd.extraCollections`
kullanın. Bu ek koleksiyonlar aynı `{ path, name, pattern? }` biçimini izler,
ancak ajan başına birleştirilir ve yol geçerli çalışma alanının dışını gösterdiğinde
açık paylaşılan adları koruyabilir.
Aynı çözümlenmiş yol hem `memory.qmd.paths` hem de
`memorySearch.qmd.extraCollections` içinde görünürse, QMD ilk girdiyi korur ve
yineleneni atlar.

---

## Çok modlu bellek (Gemini)

Gemini Embedding 2 kullanarak Markdown ile birlikte görüntüleri ve sesi dizinleyin:

| Anahtar                   | Tür        | Varsayılan | Açıklama                               |
| ------------------------- | ---------- | ---------- | -------------------------------------- |
| `multimodal.enabled`      | `boolean`  | `false`    | Çok modlu dizinlemeyi etkinleştirir    |
| `multimodal.modalities`   | `string[]` | --         | `["image"]`, `["audio"]` veya `["all"]` |
| `multimodal.maxFileBytes` | `number`   | `10000000` | Dizinleme için en büyük dosya boyutu   |

Yalnızca `extraPaths` içindeki dosyalara uygulanır. Varsayılan bellek kökleri yalnızca Markdown olarak kalır.
`gemini-embedding-2-preview` gerektirir. `fallback` değeri `"none"` olmalıdır.

Desteklenen biçimler: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.heic`, `.heif`
(görüntüler); `.mp3`, `.wav`, `.ogg`, `.opus`, `.m4a`, `.aac`, `.flac` (ses).

---

## Gömme önbelleği

| Anahtar           | Tür       | Varsayılan | Açıklama                               |
| ----------------- | --------- | ---------- | -------------------------------------- |
| `cache.enabled`   | `boolean` | `false`    | Parça gömmelerini SQLite içinde önbelleğe alır |
| `cache.maxEntries` | `number` | `50000`    | En fazla önbelleğe alınan gömme sayısı |

Yeniden dizinleme veya döküm güncellemeleri sırasında değişmemiş metnin yeniden gömülmesini önler.

---

## Toplu dizinleme

| Anahtar                      | Tür       | Varsayılan | Açıklama                    |
| ---------------------------- | --------- | ---------- | --------------------------- |
| `remote.batch.enabled`       | `boolean` | `false`    | Toplu gömme API'sini etkinleştirir |
| `remote.batch.concurrency`   | `number`  | `2`        | Paralel toplu işler         |
| `remote.batch.wait`          | `boolean` | `true`     | Toplu işlemin tamamlanmasını bekler |
| `remote.batch.pollIntervalMs` | `number` | --         | Yoklama aralığı             |
| `remote.batch.timeoutMinutes` | `number` | --         | Toplu işlem zaman aşımı     |

`openai`, `gemini` ve `voyage` için kullanılabilir. OpenAI toplu işlem, büyük geriye dönük doldurmalarda genellikle
en hızlı ve en ucuz seçenektir.

---

## Oturum belleği araması (deneysel)

Oturum dökümlerini dizinleyin ve bunları `memory_search` üzerinden gösterin:

| Anahtar                     | Tür        | Varsayılan   | Açıklama                                 |
| --------------------------- | ---------- | ------------ | ---------------------------------------- |
| `experimental.sessionMemory` | `boolean` | `false`      | Oturum dizinlemeyi etkinleştirir         |
| `sources`                   | `string[]` | `["memory"]` | Dökümleri dahil etmek için `"sessions"` ekleyin |
| `sync.sessions.deltaBytes`  | `number`   | `100000`     | Yeniden dizinleme için bayt eşiği        |
| `sync.sessions.deltaMessages` | `number` | `50`         | Yeniden dizinleme için ileti eşiği       |

Oturum dizinleme isteğe bağlıdır ve eşzamansız çalışır. Sonuçlar bir miktar eski olabilir.
Oturum günlükleri diskte bulunduğundan, dosya sistemi erişimini güven
sınırı olarak değerlendirin.

---

## SQLite vektör hızlandırma (`sqlite-vec`)

| Anahtar                    | Tür       | Varsayılan | Açıklama                              |
| -------------------------- | --------- | ---------- | ------------------------------------- |
| `store.vector.enabled`     | `boolean` | `true`     | Vektör sorguları için `sqlite-vec` kullanır |
| `store.vector.extensionPath` | `string` | bundled    | `sqlite-vec` yolunu geçersiz kılar    |

`sqlite-vec` kullanılamadığında OpenClaw otomatik olarak süreç içi kosinüs
benzerliğine geri döner.

---

## Dizin depolama

| Anahtar              | Tür      | Varsayılan                            | Açıklama                                      |
| -------------------- | -------- | ------------------------------------- | --------------------------------------------- |
| `store.path`         | `string` | `~/.openclaw/memory/{agentId}.sqlite` | Dizin konumu (`{agentId}` belirtecini destekler) |
| `store.fts.tokenizer` | `string` | `unicode61`                          | FTS5 tokenizer'ı (`unicode61` veya `trigram`) |

---

## QMD arka uç yapılandırması

Etkinleştirmek için `memory.backend = "qmd"` ayarlayın. Tüm QMD ayarları
`memory.qmd` altında bulunur:

| Anahtar                 | Tür       | Varsayılan | Açıklama                                      |
| ----------------------- | --------- | ---------- | --------------------------------------------- |
| `command`               | `string`  | `qmd`      | QMD çalıştırılabilir dosya yolu               |
| `searchMode`            | `string`  | `search`   | Arama komutu: `search`, `vsearch`, `query`    |
| `includeDefaultMemory`  | `boolean` | `true`     | `MEMORY.md` + `memory/**/*.md` otomatik dizinler |
| `paths[]`               | `array`   | --         | Ek yollar: `{ name, path, pattern? }`         |
| `sessions.enabled`      | `boolean` | `false`    | Oturum dökümlerini dizinler                   |
| `sessions.retentionDays` | `number` | --         | Döküm saklama süresi                          |
| `sessions.exportDir`    | `string`  | --         | Dışa aktarma dizini                           |

OpenClaw, geçerli QMD koleksiyonu ve MCP sorgu biçimlerini tercih eder, ancak
gerektiğinde eski `--mask` koleksiyon bayraklarına ve daha eski MCP araç adlarına geri dönerek
eski QMD sürümlerini de çalışır durumda tutar.

QMD model geçersiz kılmaları OpenClaw yapılandırmasında değil, QMD tarafında kalır. QMD'nin modellerini
genel olarak geçersiz kılmanız gerekiyorsa, ağ geçidi çalışma zamanı ortamında
`QMD_EMBED_MODEL`, `QMD_RERANK_MODEL` ve `QMD_GENERATE_MODEL` gibi ortam değişkenlerini ayarlayın.

### Güncelleme zamanlaması

| Anahtar                  | Tür       | Varsayılan | Açıklama                             |
| ------------------------ | --------- | ---------- | ------------------------------------ |
| `update.interval`        | `string`  | `5m`       | Yenileme aralığı                     |
| `update.debounceMs`      | `number`  | `15000`    | Dosya değişikliklerini debounce eder |
| `update.onBoot`          | `boolean` | `true`     | Başlangıçta yeniler                  |
| `update.waitForBootSync` | `boolean` | `false`    | Yenileme tamamlanana kadar başlangıcı engeller |
| `update.embedInterval`   | `string`  | --         | Ayrı gömme sıklığı                   |
| `update.commandTimeoutMs` | `number` | --         | QMD komutları için zaman aşımı       |
| `update.updateTimeoutMs` | `number`  | --         | QMD güncelleme işlemleri için zaman aşımı |
| `update.embedTimeoutMs`  | `number`  | --         | QMD gömme işlemleri için zaman aşımı |

### Sınırlar

| Anahtar                  | Tür      | Varsayılan | Açıklama                         |
| ------------------------ | -------- | ---------- | -------------------------------- |
| `limits.maxResults`      | `number` | `6`        | En fazla arama sonucu            |
| `limits.maxSnippetChars` | `number` | --         | Parça uzunluğunu sınırlar        |
| `limits.maxInjectedChars` | `number` | --        | Enjekte edilen toplam karakteri sınırlar |
| `limits.timeoutMs`       | `number` | `4000`     | Arama zaman aşımı                |

### Kapsam

Hangi oturumların QMD arama sonuçları alabileceğini denetler. Şununla aynı şemayı kullanır:
[`session.sendPolicy`](/tr/gateway/configuration-reference#session):

```json5
{
  memory: {
    qmd: {
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }],
      },
    },
  },
}
```

Yayınlanan varsayılan, grupları yine reddederken doğrudan ve kanal oturumlarına izin verir.

Varsayılan DM-only'dir. `match.keyPrefix` normalize edilmiş oturum anahtarıyla eşleşir;
`match.rawKeyPrefix` ise `agent:<id>:` dahil ham anahtarla eşleşir.

### Alıntılar

`memory.citations` tüm arka uçlara uygulanır:

| Değer            | Davranış                                        |
| ---------------- | ----------------------------------------------- |
| `auto` (varsayılan) | Parçalara `Source: <path#line>` altbilgisini ekler |
| `on`             | Altbilgiyi her zaman ekler                      |
| `off`            | Altbilgiyi çıkarır (yol yine de içten içe ajana iletilir) |

### Tam QMD örneği

```json5
{
  memory: {
    backend: "qmd",
    citations: "auto",
    qmd: {
      includeDefaultMemory: true,
      update: { interval: "5m", debounceMs: 15000 },
      limits: { maxResults: 6, timeoutMs: 4000 },
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }],
      },
      paths: [{ name: "docs", path: "~/notes", pattern: "**/*.md" }],
    },
  },
}
```

---

## Dreaming

Dreaming, `agents.defaults.memorySearch` altında değil,
`plugins.entries.memory-core.config.dreaming` altında yapılandırılır.

Dreaming, zamanlanmış tek bir tarama olarak çalışır ve dahili light/deep/REM aşamalarını
uygulama ayrıntısı olarak kullanır.

Kavramsal davranış ve eğik çizgi komutları için [Dreaming](/tr/concepts/dreaming) bölümüne bakın.

### Kullanıcı ayarları

| Anahtar    | Tür       | Varsayılan  | Açıklama                                      |
| ---------- | --------- | ----------- | --------------------------------------------- |
| `enabled`  | `boolean` | `false`     | Dreaming'i tamamen etkinleştirir veya devre dışı bırakır |
| `frequency` | `string` | `0 3 * * *` | Tam Dreaming taraması için isteğe bağlı Cron sıklığı |

### Örnek

```json5
{
  plugins: {
    entries: {
      "memory-core": {
        config: {
          dreaming: {
            enabled: true,
            frequency: "0 3 * * *",
          },
        },
      },
    },
  },
}
```

Notlar:

- Dreaming makine durumunu `memory/.dreams/` içine yazar.
- Dreaming insan tarafından okunabilir anlatı çıktısını `DREAMS.md` (veya mevcut `dreams.md`) dosyasına yazar.
- light/deep/REM aşama politikası ve eşikler, kullanıcıya dönük yapılandırma değil, dahili davranıştır.
