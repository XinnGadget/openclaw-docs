---
read_when:
    - Bellek araması provider’larını veya embedding modellerini yapılandırmak istiyorsunuz
    - QMD backend’ini kurmak istiyorsunuz
    - Hibrit arama, MMR veya zamansal çürümeyi ayarlamak istiyorsunuz
    - Multimodal bellek indekslemeyi etkinleştirmek istiyorsunuz
summary: Bellek araması, embedding provider’ları, QMD, hibrit arama ve multimodal indeksleme için tüm yapılandırma ayarları
title: Bellek yapılandırma başvurusu
x-i18n:
    generated_at: "2026-04-06T03:13:01Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0de0b85125443584f4e575cf673ca8d9bd12ecd849d73c537f4a17545afa93fd
    source_path: reference/memory-config.md
    workflow: 15
---

# Bellek yapılandırma başvurusu

Bu sayfa, OpenClaw bellek araması için tüm yapılandırma ayarlarını listeler. Kavramsal genel bakışlar için bkz.:

- [Belleğe Genel Bakış](/tr/concepts/memory) -- belleğin nasıl çalıştığı
- [Yerleşik Motor](/tr/concepts/memory-builtin) -- varsayılan SQLite backend’i
- [QMD Motoru](/tr/concepts/memory-qmd) -- local-first yan hizmet
- [Bellek Araması](/tr/concepts/memory-search) -- arama işlem hattı ve ince ayar

Aksi belirtilmedikçe tüm bellek araması ayarları `openclaw.json` içinde
`agents.defaults.memorySearch` altında bulunur.

---

## Provider seçimi

| Anahtar   | Tür       | Varsayılan     | Açıklama                                                                                     |
| --------- | --------- | -------------- | -------------------------------------------------------------------------------------------- |
| `provider` | `string`  | otomatik algılanır | Embedding bağdaştırıcı kimliği: `openai`, `gemini`, `voyage`, `mistral`, `bedrock`, `ollama`, `local` |
| `model`    | `string`  | provider varsayılanı | Embedding model adı                                                                     |
| `fallback` | `string`  | `"none"`       | Birincil başarısız olduğunda geri dönüş bağdaştırıcı kimliği                                |
| `enabled`  | `boolean` | `true`         | Bellek aramasını etkinleştir veya devre dışı bırak                                           |

### Otomatik algılama sırası

`provider` ayarlanmadığında, OpenClaw kullanılabilir ilk seçeneği seçer:

1. `local` -- `memorySearch.local.modelPath` yapılandırılmışsa ve dosya varsa.
2. `openai` -- bir OpenAI anahtarı çözümlenebiliyorsa.
3. `gemini` -- bir Gemini anahtarı çözümlenebiliyorsa.
4. `voyage` -- bir Voyage anahtarı çözümlenebiliyorsa.
5. `mistral` -- bir Mistral anahtarı çözümlenebiliyorsa.
6. `bedrock` -- AWS SDK kimlik bilgisi zinciri çözümleniyorsa (instance role, access key’ler, profile, SSO, web identity veya paylaşılan config).

`ollama` desteklenir ancak otomatik algılanmaz (açıkça ayarlayın).

### API anahtarı çözümleme

Uzak embedding’ler bir API anahtarı gerektirir. Bedrock bunun yerine AWS SDK varsayılan
kimlik bilgisi zincirini kullanır (instance role’ler, SSO, access key’ler).

| Provider | Env değişkeni                  | Yapılandırma anahtarı             |
| -------- | ------------------------------ | --------------------------------- |
| OpenAI   | `OPENAI_API_KEY`               | `models.providers.openai.apiKey`  |
| Gemini   | `GEMINI_API_KEY`               | `models.providers.google.apiKey`  |
| Voyage   | `VOYAGE_API_KEY`               | `models.providers.voyage.apiKey`  |
| Mistral  | `MISTRAL_API_KEY`              | `models.providers.mistral.apiKey` |
| Bedrock  | AWS kimlik bilgisi zinciri     | API anahtarı gerekmez             |
| Ollama   | `OLLAMA_API_KEY` (yer tutucu)  | --                                |

Codex OAuth yalnızca chat/completions kapsamını kapsar ve embedding
isteklerini karşılamaz.

---

## Uzak endpoint yapılandırması

Özel OpenAI uyumlu endpoint’ler veya provider varsayılanlarını geçersiz kılmak için:

| Anahtar           | Tür      | Açıklama                                     |
| ----------------- | -------- | -------------------------------------------- |
| `remote.baseUrl`  | `string` | Özel API base URL                            |
| `remote.apiKey`   | `string` | API anahtarını geçersiz kıl                  |
| `remote.headers`  | `object` | Ek HTTP üstbilgileri (provider varsayılanlarıyla birleştirilir) |

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

## Gemini’ye özgü yapılandırma

| Anahtar                | Tür      | Varsayılan             | Açıklama                                  |
| ---------------------- | -------- | ---------------------- | ----------------------------------------- |
| `model`                | `string` | `gemini-embedding-001` | Ayrıca `gemini-embedding-2-preview` desteklenir |
| `outputDimensionality` | `number` | `3072`                 | Embedding 2 için: 768, 1536 veya 3072     |

<Warning>
Model veya `outputDimensionality` değiştirildiğinde otomatik tam yeniden indeksleme tetiklenir.
</Warning>

---

## Bedrock embedding yapılandırması

Bedrock, AWS SDK varsayılan kimlik bilgisi zincirini kullanır -- API anahtarı gerekmez.
OpenClaw, Bedrock etkin bir instance role ile EC2 üzerinde çalışıyorsa yalnızca
provider ve modeli ayarlamanız yeterlidir:

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

| Anahtar                | Tür      | Varsayılan                   | Açıklama                        |
| ---------------------- | -------- | ---------------------------- | ------------------------------- |
| `model`                | `string` | `amazon.titan-embed-text-v2:0` | Herhangi bir Bedrock embedding model kimliği |
| `outputDimensionality` | `number` | model varsayılanı            | Titan V2 için: 256, 512 veya 1024 |

### Desteklenen modeller

Aşağıdaki modeller desteklenir (family algılama ve boyut varsayılanlarıyla):

| Model ID                                   | Provider   | Varsayılan Boyut | Yapılandırılabilir Boyutlar |
| ------------------------------------------ | ---------- | ---------------- | --------------------------- |
| `amazon.titan-embed-text-v2:0`             | Amazon     | 1024             | 256, 512, 1024              |
| `amazon.titan-embed-text-v1`               | Amazon     | 1536             | --                          |
| `amazon.titan-embed-g1-text-02`            | Amazon     | 1536             | --                          |
| `amazon.titan-embed-image-v1`              | Amazon     | 1024             | --                          |
| `amazon.nova-2-multimodal-embeddings-v1:0` | Amazon     | 1024             | 256, 384, 1024, 3072        |
| `cohere.embed-english-v3`                  | Cohere     | 1024             | --                          |
| `cohere.embed-multilingual-v3`             | Cohere     | 1024             | --                          |
| `cohere.embed-v4:0`                        | Cohere     | 1536             | 256-1536                    |
| `twelvelabs.marengo-embed-3-0-v1:0`        | TwelveLabs | 512              | --                          |
| `twelvelabs.marengo-embed-2-7-v1:0`        | TwelveLabs | 1024             | --                          |

Verim eki bulunan varyantlar (ör. `amazon.titan-embed-text-v1:2:8k`), temel
modelin yapılandırmasını devralır.

### Kimlik doğrulama

Bedrock auth, standart AWS SDK kimlik bilgisi çözümleme sırasını kullanır:

1. Ortam değişkenleri (`AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`)
2. SSO token önbelleği
3. Web identity token kimlik bilgileri
4. Paylaşılan kimlik bilgileri ve config dosyaları
5. ECS veya EC2 meta veri kimlik bilgileri

Bölge, `AWS_REGION`, `AWS_DEFAULT_REGION`, `amazon-bedrock`
provider `baseUrl` değerinden çözülür veya varsayılan olarak `us-east-1` kullanılır.

### IAM izinleri

IAM role veya kullanıcısının şuna ihtiyacı vardır:

```json
{
  "Effect": "Allow",
  "Action": "bedrock:InvokeModel",
  "Resource": "*"
}
```

En az ayrıcalık için `InvokeModel` iznini belirli modele sınırlandırın:

```
arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v2:0
```

---

## Yerel embedding yapılandırması

| Anahtar                | Tür      | Varsayılan               | Açıklama                       |
| ---------------------- | -------- | ------------------------ | ------------------------------ |
| `local.modelPath`      | `string` | otomatik indirilir       | GGUF model dosyasının yolu     |
| `local.modelCacheDir`  | `string` | node-llama-cpp varsayılanı | İndirilen modeller için önbellek dizini |

Varsayılan model: `embeddinggemma-300m-qat-Q8_0.gguf` (~0.6 GB, otomatik indirilir).
Yerel derleme gerektirir: `pnpm approve-builds` ardından `pnpm rebuild node-llama-cpp`.

---

## Hibrit arama yapılandırması

Hepsi `memorySearch.query.hybrid` altındadır:

| Anahtar               | Tür       | Varsayılan | Açıklama                          |
| --------------------- | --------- | ---------- | --------------------------------- |
| `enabled`             | `boolean` | `true`     | Hibrit BM25 + vektör aramayı etkinleştir |
| `vectorWeight`        | `number`  | `0.7`      | Vektör puanları için ağırlık (0-1) |
| `textWeight`          | `number`  | `0.3`      | BM25 puanları için ağırlık (0-1)  |
| `candidateMultiplier` | `number`  | `4`        | Aday havuzu boyutu çarpanı        |

### MMR (çeşitlilik)

| Anahtar       | Tür       | Varsayılan | Açıklama                               |
| ------------- | --------- | ---------- | -------------------------------------- |
| `mmr.enabled` | `boolean` | `false`    | MMR yeniden sıralamayı etkinleştir     |
| `mmr.lambda`  | `number`  | `0.7`      | 0 = en yüksek çeşitlilik, 1 = en yüksek alaka |

### Zamansal çürüme (güncellik)

| Anahtar                     | Tür       | Varsayılan | Açıklama                    |
| --------------------------- | --------- | ---------- | --------------------------- |
| `temporalDecay.enabled`     | `boolean` | `false`    | Güncellik artışını etkinleştir |
| `temporalDecay.halfLifeDays`| `number`  | `30`       | Puan her N günde yarıya iner |

Evergreen dosyalar (`MEMORY.md`, `memory/` içindeki tarih içermeyen dosyalar) asla çürütülmez.

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

| Anahtar      | Tür        | Açıklama                                    |
| ------------ | ---------- | ------------------------------------------- |
| `extraPaths` | `string[]` | İndekslenecek ek dizinler veya dosyalar     |

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

Yollar mutlak veya çalışma alanına göreli olabilir. Dizinler `.md` dosyaları için
özyinelemeli taranır. Symlink işleme etkin backend’e bağlıdır:
yerleşik motor symlink’leri yok sayar, QMD ise alttaki QMD tarayıcı
davranışını izler.

Agent kapsamlı agent’lar arası transcript araması için
`memory.qmd.paths` yerine `agents.list[].memorySearch.qmd.extraCollections`
kullanın. Bu ek koleksiyonlar aynı `{ path, name, pattern? }` biçimini izler,
ancak agent başına birleştirilir ve yol mevcut çalışma alanının dışına
işaret ettiğinde açık paylaşılan adları koruyabilir.
Aynı çözümlenmiş yol hem `memory.qmd.paths` hem de
`memorySearch.qmd.extraCollections` içinde görünürse, QMD ilk girdiyi tutar ve
yineleneni atlar.

---

## Multimodal bellek (Gemini)

Markdown ile birlikte görsel ve sesi Gemini Embedding 2 kullanarak indeksleyin:

| Anahtar                   | Tür        | Varsayılan | Açıklama                                 |
| ------------------------- | ---------- | ---------- | ---------------------------------------- |
| `multimodal.enabled`      | `boolean`  | `false`    | Multimodal indekslemeyi etkinleştir      |
| `multimodal.modalities`   | `string[]` | --         | `["image"]`, `["audio"]` veya `["all"]`  |
| `multimodal.maxFileBytes` | `number`   | `10000000` | İndeksleme için en büyük dosya boyutu    |

Yalnızca `extraPaths` içindeki dosyalara uygulanır. Varsayılan bellek kökleri yalnızca Markdown olarak kalır.
`gemini-embedding-2-preview` gerektirir. `fallback` değeri `"none"` olmalıdır.

Desteklenen biçimler: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.heic`, `.heif`
(görseller); `.mp3`, `.wav`, `.ogg`, `.opus`, `.m4a`, `.aac`, `.flac` (ses).

---

## Embedding önbelleği

| Anahtar           | Tür       | Varsayılan | Açıklama                              |
| ----------------- | --------- | ---------- | ------------------------------------- |
| `cache.enabled`   | `boolean` | `false`    | Parça embedding’lerini SQLite içinde önbelleğe al |
| `cache.maxEntries`| `number`  | `50000`    | En fazla önbelleğe alınan embedding   |

Yeniden indeksleme veya transcript güncellemeleri sırasında değişmemiş metnin yeniden embedding yapılmasını önler.

---

## Toplu indeksleme

| Anahtar                      | Tür       | Varsayılan | Açıklama                    |
| ---------------------------- | --------- | ---------- | --------------------------- |
| `remote.batch.enabled`       | `boolean` | `false`    | Toplu embedding API’yi etkinleştir |
| `remote.batch.concurrency`   | `number`  | `2`        | Paralel toplu işler         |
| `remote.batch.wait`          | `boolean` | `true`     | Toplu işin tamamlanmasını bekle |
| `remote.batch.pollIntervalMs`| `number`  | --         | Yoklama aralığı             |
| `remote.batch.timeoutMinutes`| `number`  | --         | Toplu iş zaman aşımı        |

`openai`, `gemini` ve `voyage` için kullanılabilir. OpenAI batch genellikle
büyük geri doldurmalar için en hızlı ve en ucuz olanıdır.

---

## Oturum bellek araması (deneysel)

Oturum transcript’lerini indeksleyin ve bunları `memory_search` üzerinden gösterin:

| Anahtar                      | Tür        | Varsayılan    | Açıklama                                    |
| ---------------------------- | ---------- | ------------- | ------------------------------------------- |
| `experimental.sessionMemory` | `boolean`  | `false`       | Oturum indekslemeyi etkinleştir             |
| `sources`                    | `string[]` | `["memory"]`  | Transcript’leri dahil etmek için `"sessions"` ekleyin |
| `sync.sessions.deltaBytes`   | `number`   | `100000`      | Yeniden indeksleme için bayt eşiği          |
| `sync.sessions.deltaMessages`| `number`   | `50`          | Yeniden indeksleme için mesaj eşiği         |

Oturum indeksleme isteğe bağlıdır ve eşzamansız çalışır. Sonuçlar biraz eski olabilir.
Oturum günlükleri diskte yaşar, bu yüzden dosya sistemi erişimini güven sınırı olarak değerlendirin.

---

## SQLite vektör hızlandırma (sqlite-vec)

| Anahtar                     | Tür       | Varsayılan | Açıklama                          |
| --------------------------- | --------- | ---------- | --------------------------------- |
| `store.vector.enabled`      | `boolean` | `true`     | Vektör sorguları için sqlite-vec kullan |
| `store.vector.extensionPath`| `string`  | bundled    | sqlite-vec yolunu geçersiz kıl    |

sqlite-vec kullanılamadığında OpenClaw otomatik olarak süreç içi kosinüs
benzerliğine geri döner.

---

## İndeks depolama

| Anahtar              | Tür      | Varsayılan                            | Açıklama                                   |
| -------------------- | -------- | ------------------------------------- | ------------------------------------------ |
| `store.path`         | `string` | `~/.openclaw/memory/{agentId}.sqlite` | İndeks konumu (`{agentId}` token’ını destekler) |
| `store.fts.tokenizer`| `string` | `unicode61`                           | FTS5 tokenizer (`unicode61` veya `trigram`) |

---

## QMD backend yapılandırması

Etkinleştirmek için `memory.backend = "qmd"` ayarlayın. Tüm QMD ayarları
`memory.qmd` altında bulunur:

| Anahtar                 | Tür       | Varsayılan | Açıklama                                     |
| ----------------------- | --------- | ---------- | -------------------------------------------- |
| `command`               | `string`  | `qmd`      | QMD çalıştırılabilir dosya yolu              |
| `searchMode`            | `string`  | `search`   | Arama komutu: `search`, `vsearch`, `query`   |
| `includeDefaultMemory`  | `boolean` | `true`     | `MEMORY.md` + `memory/**/*.md` otomatik indeksle |
| `paths[]`               | `array`   | --         | Ek yollar: `{ name, path, pattern? }`        |
| `sessions.enabled`      | `boolean` | `false`    | Oturum transcript’lerini indeksle            |
| `sessions.retentionDays`| `number`  | --         | Transcript saklama süresi                    |
| `sessions.exportDir`    | `string`  | --         | Dışa aktarma dizini                          |

OpenClaw, mevcut QMD koleksiyonu ve MCP sorgu şekillerini tercih eder, ancak
gerektiğinde eski `--mask` koleksiyon bayraklarına ve eski MCP araç adlarına
geri dönerek eski QMD sürümlerini de çalışır halde tutar.

QMD model geçersiz kılmaları OpenClaw config tarafında değil, QMD tarafında kalır.
QMD’nin modellerini global olarak geçersiz kılmanız gerekiyorsa,
gateway çalışma zamanı ortamında `QMD_EMBED_MODEL`, `QMD_RERANK_MODEL` ve `QMD_GENERATE_MODEL`
gibi ortam değişkenlerini ayarlayın.

### Güncelleme takvimi

| Anahtar                   | Tür       | Varsayılan | Açıklama                               |
| ------------------------- | --------- | ---------- | -------------------------------------- |
| `update.interval`         | `string`  | `5m`       | Yenileme aralığı                       |
| `update.debounceMs`       | `number`  | `15000`    | Dosya değişikliklerini debounce et     |
| `update.onBoot`           | `boolean` | `true`     | Başlangıçta yenile                     |
| `update.waitForBootSync`  | `boolean` | `false`    | Yenileme tamamlanana kadar başlangıcı engelle |
| `update.embedInterval`    | `string`  | --         | Ayrı embedding kadansı                 |
| `update.commandTimeoutMs` | `number`  | --         | QMD komutları için zaman aşımı         |
| `update.updateTimeoutMs`  | `number`  | --         | QMD update işlemleri için zaman aşımı  |
| `update.embedTimeoutMs`   | `number`  | --         | QMD embedding işlemleri için zaman aşımı |

### Sınırlar

| Anahtar                  | Tür      | Varsayılan | Açıklama                     |
| ------------------------ | -------- | ---------- | ---------------------------- |
| `limits.maxResults`      | `number` | `6`        | En fazla arama sonucu        |
| `limits.maxSnippetChars` | `number` | --         | Snippet uzunluğunu sınırla   |
| `limits.maxInjectedChars`| `number` | --         | Toplam enjekte edilen karakteri sınırla |
| `limits.timeoutMs`       | `number` | `4000`     | Arama zaman aşımı            |

### Kapsam

Hangi oturumların QMD arama sonuçlarını alabileceğini denetler. Şeması,
[`session.sendPolicy`](/tr/gateway/configuration-reference#session) ile aynıdır:

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

Varsayılan yalnızca DM’dir. `match.keyPrefix`, normalize edilmiş oturum anahtarıyla eşleşir;
`match.rawKeyPrefix`, `agent:<id>:` dahil ham anahtarla eşleşir.

### Atıflar

`memory.citations`, tüm backend’lere uygulanır:

| Değer             | Davranış                                           |
| ----------------- | -------------------------------------------------- |
| `auto` (varsayılan) | Snippet’lere `Source: <path#line>` altbilgisi ekle |
| `on`              | Altbilgiyi her zaman ekle                          |
| `off`             | Altbilgiyi çıkar (yol yine de agent’a dahili olarak iletilir) |

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

## Dreaming (deneysel)

Dreaming, `agents.defaults.memorySearch` altında değil,
`plugins.entries.memory-core.config.dreaming` altında yapılandırılır.

Dreaming tek bir zamanlanmış tarama olarak çalışır ve dahili light/deep/REM aşamalarını
uygulama ayrıntısı olarak kullanır.

Kavramsal davranış ve slash komutları için bkz. [Dreaming](/concepts/dreaming).

### Kullanıcı ayarları

| Anahtar    | Tür       | Varsayılan  | Açıklama                                   |
| ---------- | --------- | ----------- | ------------------------------------------ |
| `enabled`  | `boolean` | `false`     | Dreaming’i tamamen etkinleştir veya devre dışı bırak |
| `frequency`| `string`  | `0 3 * * *` | Tam dreaming taraması için isteğe bağlı cron aralığı |

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
- Dreaming insan tarafından okunabilir anlatı çıktısını `DREAMS.md` (veya mevcut `dreams.md`) içine yazar.
- Light/deep/REM aşama ilkesi ve eşikleri, kullanıcıya dönük config değil dahili davranıştır.
