---
read_when:
    - API sağlayıcıları başarısız olduğunda güvenilir bir geri dönüş istiyorsunuz
    - Codex CLI veya diğer yerel AI CLI'lerini çalıştırıyor ve bunları yeniden kullanmak istiyorsunuz
    - CLI arka uç araç erişimi için MCP loopback köprüsünü anlamak istiyorsunuz
summary: 'CLI arka uçları: isteğe bağlı MCP araç köprüsüyle yerel AI CLI geri dönüşü'
title: CLI Arka Uçları
x-i18n:
    generated_at: "2026-04-08T02:14:25Z"
    model: gpt-5.4
    provider: openai
    source_hash: b0e8c41f5f5a8e34466f6b765e5c08585ef1788fa9e9d953257324bcc6cbc414
    source_path: gateway/cli-backends.md
    workflow: 15
---

# CLI arka uçları (geri dönüş çalışma zamanı)

OpenClaw, API sağlayıcıları devre dışı kaldığında, hız sınırına takıldığında
veya geçici olarak hatalı davrandığında **yalnızca metin kullanan bir geri dönüş**
olarak **yerel AI CLI'lerini** çalıştırabilir. Bu, bilinçli olarak temkinli tasarlanmıştır:

- **OpenClaw araçları doğrudan enjekte edilmez**, ancak `bundleMcp: true`
  olan arka uçlar gateway araçlarını bir loopback MCP köprüsü üzerinden alabilir.
- Bunu destekleyen CLI'ler için **JSONL akışı**.
- **Oturumlar desteklenir** (böylece sonraki turlar tutarlı kalır).
- CLI görüntü yollarını kabul ediyorsa **görüntüler aktarılabilir**.

Bu, birincil yol olmaktan çok bir **güvenlik ağı** olarak tasarlanmıştır. Bunu,
harici API'lere bağlı kalmadan “her zaman çalışır” metin yanıtları istediğinizde kullanın.

ACP oturum denetimleri, arka plan görevleri,
başlık/konuşma bağlama ve kalıcı harici kodlama oturumları içeren tam bir harness çalışma zamanı istiyorsanız,
bunun yerine [ACP Agents](/tr/tools/acp-agents) kullanın. CLI arka uçları ACP değildir.

## Yeni başlayanlar için hızlı başlangıç

Codex CLI'yi **hiçbir yapılandırma olmadan** kullanabilirsiniz (paketle gelen OpenAI eklentisi
varsayılan bir arka uç kaydeder):

```bash
openclaw agent --message "hi" --model codex-cli/gpt-5.4
```

Gateway'iniz launchd/systemd altında çalışıyorsa ve PATH minimum düzeydeyse, yalnızca
komut yolunu ekleyin:

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "codex-cli": {
          command: "/opt/homebrew/bin/codex",
        },
      },
    },
  },
}
```

Hepsi bu. CLI'nin kendisi dışında anahtar, ek kimlik doğrulama yapılandırması gerekmez.

Bir paketlenmiş CLI arka ucunu bir
gateway ana makinesinde **birincil mesaj sağlayıcısı** olarak kullanırsanız, OpenClaw artık yapılandırmanız
bir model ref içinde veya
`agents.defaults.cliBackends` altında bu arka uca açıkça başvurduğunda sahibi olan paketlenmiş eklentiyi otomatik olarak yükler.

## Geri dönüş olarak kullanma

Bir CLI arka ucunu geri dönüş listenize ekleyin; böylece yalnızca birincil modeller başarısız olduğunda çalışır:

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["codex-cli/gpt-5.4"],
      },
      models: {
        "anthropic/claude-opus-4-6": { alias: "Opus" },
        "codex-cli/gpt-5.4": {},
      },
    },
  },
}
```

Notlar:

- `agents.defaults.models` (izin listesi) kullanıyorsanız, CLI arka uç modellerinizi de oraya eklemeniz gerekir.
- Birincil sağlayıcı başarısız olursa (kimlik doğrulama, hız sınırları, zaman aşımları), OpenClaw
  sıradaki CLI arka ucunu dener.

## Yapılandırmaya genel bakış

Tüm CLI arka uçları şunun altında bulunur:

```
agents.defaults.cliBackends
```

Her giriş bir **sağlayıcı kimliği** ile anahtarlanır (`codex-cli`, `my-cli` gibi).
Sağlayıcı kimliği model ref'inizin sol tarafı olur:

```
<provider>/<model>
```

### Örnek yapılandırma

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "codex-cli": {
          command: "/opt/homebrew/bin/codex",
        },
        "my-cli": {
          command: "my-cli",
          args: ["--json"],
          output: "json",
          input: "arg",
          modelArg: "--model",
          modelAliases: {
            "claude-opus-4-6": "opus",
            "claude-sonnet-4-6": "sonnet",
          },
          sessionArg: "--session",
          sessionMode: "existing",
          sessionIdFields: ["session_id", "conversation_id"],
          systemPromptArg: "--system",
          systemPromptWhen: "first",
          imageArg: "--image",
          imageMode: "repeat",
          serialize: true,
        },
      },
    },
  },
}
```

## Nasıl çalışır

1. Sağlayıcı önekine (`codex-cli/...`) göre bir **arka uç seçer**.
2. Aynı OpenClaw istemi + çalışma alanı bağlamını kullanarak bir **sistem istemi oluşturur**.
3. Geçmiş tutarlı kalsın diye CLI'yi bir oturum kimliğiyle (destekleniyorsa) **çalıştırır**.
4. **Çıktıyı ayrıştırır** (JSON veya düz metin) ve son metni döndürür.
5. **Arka uç başına oturum kimliklerini kalıcı hale getirir**, böylece sonraki adımlar aynı CLI oturumunu yeniden kullanır.

<Note>
Paketle gelen Anthropic `claude-cli` arka ucu yeniden desteklenmektedir. Anthropic çalışanları
bize OpenClaw tarzı Claude CLI kullanımına yeniden izin verildiğini söyledi; bu nedenle OpenClaw,
Anthropic yeni bir politika yayımlamadıkça bu entegrasyon için
`claude -p` kullanımını onaylanmış kabul eder.
</Note>

## Oturumlar

- CLI oturumları destekliyorsa, `sessionArg` (`--session-id` gibi) veya
  kimliğin birden fazla işarete eklenmesi gerektiğinde `sessionArgs`
  (yer tutucu `{sessionId}`) ayarlayın.
- CLI farklı işaretlerle bir **resume alt komutu** kullanıyorsa,
  `resumeArgs` (`args` yerine geçer) ve isteğe bağlı olarak `resumeOutput`
  (JSON olmayan resume işlemleri için) ayarlayın.
- `sessionMode`:
  - `always`: her zaman bir oturum kimliği gönderir (saklı değilse yeni bir UUID).
  - `existing`: yalnızca daha önce saklanmışsa bir oturum kimliği gönderir.
  - `none`: asla bir oturum kimliği göndermez.

Serileştirme notları:

- `serialize: true` aynı şerit üzerindeki çalıştırmaları sıralı tutar.
- Çoğu CLI tek bir sağlayıcı şeridinde serileştirme yapar.
- OpenClaw, arka uç kimlik doğrulama durumu değiştiğinde, buna yeniden giriş,
  token rotasyonu veya değişen bir kimlik doğrulama profili kimlik bilgisi dahil olmak üzere,
  saklanan CLI oturumu yeniden kullanımını bırakır.

## Görüntüler (aktararak geçirme)

CLI'niz görüntü yollarını kabul ediyorsa `imageArg` ayarlayın:

```json5
imageArg: "--image",
imageMode: "repeat"
```

OpenClaw base64 görüntüleri geçici dosyalara yazar. `imageArg` ayarlanmışsa bu
yollar CLI argümanları olarak geçirilir. `imageArg` eksikse OpenClaw
dosya yollarını isteme ekler (yol ekleme); bu, düz yollardan yerel dosyaları otomatik
yükleyen CLI'ler için yeterlidir.

## Girişler / çıkışlar

- `output: "json"` (varsayılan) JSON ayrıştırmayı dener ve metin + oturum kimliğini çıkarır.
- Gemini CLI JSON çıktısı için OpenClaw, `usage` eksik veya boş olduğunda yanıt metnini `response` alanından,
  kullanım bilgisini ise `stats` içinden okur.
- `output: "jsonl"` JSONL akışlarını ayrıştırır (örneğin Codex CLI `--json`) ve varsa son agent mesajını artı oturum
  tanımlayıcılarını çıkarır.
- `output: "text"` stdout'u son yanıt olarak ele alır.

Giriş modları:

- `input: "arg"` (varsayılan) istemi son CLI argümanı olarak geçirir.
- `input: "stdin"` istemi stdin üzerinden gönderir.
- İstem çok uzunsa ve `maxPromptArgChars` ayarlanmışsa stdin kullanılır.

## Varsayılanlar (eklentiye ait)

Paketle gelen OpenAI eklentisi `codex-cli` için de bir varsayılan kaydeder:

- `command: "codex"`
- `args: ["exec","--json","--color","never","--sandbox","workspace-write","--skip-git-repo-check"]`
- `resumeArgs: ["exec","resume","{sessionId}","--color","never","--sandbox","workspace-write","--skip-git-repo-check"]`
- `output: "jsonl"`
- `resumeOutput: "text"`
- `modelArg: "--model"`
- `imageArg: "--image"`
- `sessionMode: "existing"`

Paketle gelen Google eklentisi `google-gemini-cli` için de bir varsayılan kaydeder:

- `command: "gemini"`
- `args: ["--output-format", "json", "--prompt", "{prompt}"]`
- `resumeArgs: ["--resume", "{sessionId}", "--output-format", "json", "--prompt", "{prompt}"]`
- `imageArg: "@"`
- `imagePathScope: "workspace"`
- `modelArg: "--model"`
- `sessionMode: "existing"`
- `sessionIdFields: ["session_id", "sessionId"]`

Ön koşul: yerel Gemini CLI kurulu olmalı ve
`PATH` üzerinde `gemini` olarak erişilebilir olmalıdır (`brew install gemini-cli` veya
`npm install -g @google/gemini-cli`).

Gemini CLI JSON notları:

- Yanıt metni JSON `response` alanından okunur.
- `usage` yoksa veya boşsa kullanım bilgisi `stats` değerine geri düşer.
- `stats.cached`, OpenClaw `cacheRead` içine normalize edilir.
- `stats.input` eksikse OpenClaw giriş token'larını
  `stats.input_tokens - stats.cached` üzerinden türetir.

Yalnızca gerekirse geçersiz kılın (yaygın olan: mutlak `command` yolu).

## Eklentiye ait varsayılanlar

CLI arka uç varsayılanları artık eklenti yüzeyinin bir parçasıdır:

- Eklentiler bunları `api.registerCliBackend(...)` ile kaydeder.
- Arka uç `id`, model ref'lerinde sağlayıcı öneki olur.
- `agents.defaults.cliBackends.<id>` içindeki kullanıcı yapılandırması hâlâ eklenti varsayılanını geçersiz kılar.
- Arka uca özgü yapılandırma temizliği, isteğe bağlı
  `normalizeConfig` kancası aracılığıyla eklentiye ait olmaya devam eder.

## Bundle MCP katmanları

CLI arka uçları OpenClaw araç çağrılarını **doğrudan** almaz, ancak bir arka uç
`bundleMcp: true` ile oluşturulmuş bir MCP yapılandırma katmanını kullanmayı seçebilir.

Mevcut paketli davranış:

- `claude-cli`: oluşturulmuş sıkı MCP yapılandırma dosyası
- `codex-cli`: `mcp_servers` için satır içi yapılandırma geçersiz kılmaları
- `google-gemini-cli`: oluşturulmuş Gemini sistem ayarları dosyası

Bundle MCP etkin olduğunda OpenClaw şunları yapar:

- CLI sürecine gateway araçlarını sunan bir loopback HTTP MCP sunucusu başlatır
- köprüyü oturum başına bir token ile (`OPENCLAW_MCP_TOKEN`) kimlik doğrular
- araç erişimini mevcut oturum, hesap ve kanal bağlamıyla sınırlar
- mevcut çalışma alanı için etkin bundle-MCP sunucularını yükler
- bunları mevcut arka uç MCP yapılandırması/ayarları şekliyle birleştirir
- başlatma yapılandırmasını sahibi olan uzantının arka uca ait entegrasyon modunu kullanarak yeniden yazar

Hiçbir MCP sunucusu etkin değilse bile OpenClaw, bir arka uç
bundle MCP kullanmayı seçtiğinde arka plan çalıştırmaları izole kalsın diye yine de sıkı bir yapılandırma enjekte eder.

## Sınırlamalar

- **Doğrudan OpenClaw araç çağrısı yoktur.** OpenClaw, araç çağrılarını
  CLI arka uç protokolüne enjekte etmez. Arka uçlar gateway araçlarını yalnızca
  `bundleMcp: true` kullanmayı seçtiklerinde görür.
- **Akış arka uca özeldir.** Bazı arka uçlar JSONL akışı yapar; diğerleri
  çıkışa kadar arabellekte tutar.
- **Yapılandırılmış çıktılar** CLI'nin JSON biçimine bağlıdır.
- **Codex CLI oturumları** düz metin çıktısı üzerinden resume edilir (JSONL yoktur), bu da
  ilk `--json` çalıştırmasına göre daha az yapılandırılmıştır. OpenClaw oturumları yine de
  normal şekilde çalışır.

## Sorun giderme

- **CLI bulunamadı**: `command` değerini tam yol olarak ayarlayın.
- **Yanlış model adı**: `provider/model` → CLI modeli eşlemesi yapmak için `modelAliases` kullanın.
- **Oturum sürekliliği yok**: `sessionArg` ayarlı olduğundan ve `sessionMode` değerinin
  `none` olmadığından emin olun (Codex CLI şu anda JSON çıktısıyla resume edemez).
- **Görüntüler yok sayılıyor**: `imageArg` ayarlayın (ve CLI'nin dosya yollarını desteklediğini doğrulayın).
