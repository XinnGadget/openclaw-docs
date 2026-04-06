---
read_when:
    - QMD'yi bellek arka ucunuz olarak kurmak istiyorsunuz
    - Yeniden sıralama veya ek dizinlenen yollar gibi gelişmiş bellek özellikleri istiyorsunuz
summary: BM25, vektörler, yeniden sıralama ve sorgu genişletme içeren, yerel öncelikli arama yardımcı hizmeti
title: QMD Bellek Motoru
x-i18n:
    generated_at: "2026-04-06T03:06:23Z"
    model: gpt-5.4
    provider: openai
    source_hash: 36642c7df94b88f562745dd2270334379f2aeeef4b363a8c13ef6be42dadbe5c
    source_path: concepts/memory-qmd.md
    workflow: 15
---

# QMD Bellek Motoru

[QMD](https://github.com/tobi/qmd), OpenClaw ile birlikte çalışan yerel öncelikli bir arama yardımcı hizmetidir. BM25, vektör araması ve yeniden sıralamayı tek bir
ikili dosyada birleştirir ve çalışma alanı bellek dosyalarınızın ötesindeki içeriği de dizinleyebilir.

## Yerleşik olana göre ne ekler

- Daha iyi geri çağırma için **yeniden sıralama ve sorgu genişletme**.
- **Ek dizinleri dizinleme** -- proje belgeleri, ekip notları, diskteki her şey.
- **Oturum transkriptlerini dizinleme** -- önceki konuşmaları geri çağırın.
- **Tamamen yerel** -- Bun + node-llama-cpp ile çalışır, GGUF modellerini otomatik indirir.
- **Otomatik geri dönüş** -- QMD kullanılamıyorsa OpenClaw sorunsuz şekilde
  yerleşik motora geri döner.

## Başlarken

### Önkoşullar

- QMD'yi yükleyin: `npm install -g @tobilu/qmd` veya `bun install -g @tobilu/qmd`
- Uzantılara izin veren SQLite derlemesi (`brew install sqlite` macOS'ta).
- QMD, ağ geçidinin `PATH` değişkeninde olmalıdır.
- macOS ve Linux kutudan çıktığı gibi çalışır. Windows en iyi WSL2 üzerinden desteklenir.

### Etkinleştirme

```json5
{
  memory: {
    backend: "qmd",
  },
}
```

OpenClaw, `~/.openclaw/agents/<agentId>/qmd/` altında bağımsız bir QMD ana dizini oluşturur ve yardımcı hizmetin yaşam döngüsünü
otomatik olarak yönetir -- koleksiyonlar, güncellemeler ve gömme çalıştırmaları sizin için işlenir.
Güncel QMD koleksiyonu ve MCP sorgu biçimlerini tercih eder, ancak gerektiğinde
eski `--mask` koleksiyon işaretlerine ve daha eski MCP araç adlarına yine de geri döner.

## Yardımcı hizmet nasıl çalışır

- OpenClaw, çalışma alanı bellek dosyalarınızdan ve yapılandırılmış
  `memory.qmd.paths` girdilerinden koleksiyonlar oluşturur, ardından açılışta
  ve düzenli aralıklarla (varsayılan olarak her 5 dakikada bir) `qmd update` + `qmd embed` çalıştırır.
- Açılış yenilemesi arka planda çalışır, bu nedenle sohbet başlangıcı engellenmez.
- Aramalar yapılandırılmış `searchMode` kullanır (varsayılan: `search`; ayrıca
  `vsearch` ve `query` de desteklenir). Bir mod başarısız olursa OpenClaw `qmd query` ile yeniden dener.
- QMD tamamen başarısız olursa OpenClaw yerleşik SQLite motoruna geri döner.

<Info>
İlk arama yavaş olabilir -- QMD, ilk `qmd query` çalıştırmasında
yeniden sıralama ve sorgu genişletme için GGUF modellerini (~2 GB) otomatik olarak indirir.
</Info>

## Model geçersiz kılmaları

QMD model ortam değişkenleri ağ geçidi
işleminden değiştirilmeden geçirilir, böylece yeni OpenClaw yapılandırması eklemeden QMD'yi genel olarak ayarlayabilirsiniz:

```bash
export QMD_EMBED_MODEL="hf:Qwen/Qwen3-Embedding-0.6B-GGUF/Qwen3-Embedding-0.6B-Q8_0.gguf"
export QMD_RERANK_MODEL="/absolute/path/to/reranker.gguf"
export QMD_GENERATE_MODEL="/absolute/path/to/generator.gguf"
```

Gömme modelini değiştirdikten sonra, dizinin yeni
vektör uzayıyla eşleşmesi için gömmeleri yeniden çalıştırın.

## Ek yolları dizinleme

Ek dizinleri aranabilir yapmak için QMD'yi onlara yönlendirin:

```json5
{
  memory: {
    backend: "qmd",
    qmd: {
      paths: [{ name: "docs", path: "~/notes", pattern: "**/*.md" }],
    },
  },
}
```

Ek yollardan alınan parçacıklar arama sonuçlarında `qmd/<collection>/<relative-path>` olarak görünür. `memory_get` bu öneki anlar ve doğru
koleksiyon kökünden okur.

## Oturum transkriptlerini dizinleme

Önceki konuşmaları geri çağırmak için oturum dizinlemeyi etkinleştirin:

```json5
{
  memory: {
    backend: "qmd",
    qmd: {
      sessions: { enabled: true },
    },
  },
}
```

Transkriptler, temizlenmiş User/Assistant dönüşleri olarak
`~/.openclaw/agents/<id>/qmd/sessions/` altındaki özel bir QMD koleksiyonuna dışa aktarılır.

## Arama kapsamı

Varsayılan olarak, QMD arama sonuçları yalnızca DM oturumlarında gösterilir (gruplarda veya
kanallarda değil). Bunu değiştirmek için `memory.qmd.scope` yapılandırın:

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

Kapsam bir aramayı reddettiğinde OpenClaw, türetilen kanalı ve
sohbet türünü içeren bir uyarı günlüğe kaydeder; böylece boş sonuçlarda hata ayıklamak kolaylaşır.

## Alıntılar

`memory.citations` değeri `auto` veya `on` olduğunda, arama parçacıkları
`Source: <path#line>` alt bilgisi içerir. Alt bilgiyi çıkarmak ama
yolu dahili olarak aracıya iletmeye devam etmek için `memory.citations = "off"` ayarlayın.

## Ne zaman kullanılmalı

Şunlara ihtiyacınız olduğunda QMD'yi seçin:

- Daha yüksek kaliteli sonuçlar için yeniden sıralama.
- Çalışma alanı dışındaki proje belgelerinde veya notlarda arama yapma.
- Geçmiş oturum konuşmalarını geri çağırma.
- API anahtarı gerektirmeyen tamamen yerel arama.

Daha basit kurulumlar için [yerleşik motor](/tr/concepts/memory-builtin),
ek bağımlılık olmadan iyi çalışır.

## Sorun giderme

**QMD bulunamadı mı?** İkili dosyanın ağ geçidinin `PATH` değişkeninde olduğundan emin olun. OpenClaw
bir hizmet olarak çalışıyorsa bir sembolik bağ oluşturun:
`sudo ln -s ~/.bun/bin/qmd /usr/local/bin/qmd`.

**İlk arama çok mu yavaş?** QMD ilk kullanımda GGUF modellerini indirir. Aynı XDG dizinlerini kullanarak
`qmd query "test"` ile önceden ısıtın; OpenClaw da bunları kullanır.

**Arama zaman aşımına mı uğruyor?** `memory.qmd.limits.timeoutMs` değerini artırın (varsayılan: 4000ms).
Daha yavaş donanımlar için `120000` olarak ayarlayın.

**Grup sohbetlerinde sonuçlar boş mu?** `memory.qmd.scope` değerini kontrol edin -- varsayılan yalnızca
DM oturumlarına izin verir.

**Çalışma alanında görünen geçici depolar `ENAMETOOLONG` veya bozuk dizinlemeye mi neden oluyor?**
QMD geçişi şu anda OpenClaw'ın yerleşik sembolik bağ kurallarından ziyade
temeldeki QMD tarayıcı davranışını izler. QMD, döngü güvenli geçişi veya açık dışlama denetimlerini sunana kadar
geçici monorepo checkout'larını `.tmp/` gibi gizli dizinlerde veya dizinlenen QMD köklerinin dışında tutun.

## Yapılandırma

Tam yapılandırma yüzeyi (`memory.qmd.*`), arama modları, güncelleme aralıkları,
kapsam kuralları ve diğer tüm ayarlar için
[Bellek yapılandırma başvurusu](/tr/reference/memory-config) bölümüne bakın.
