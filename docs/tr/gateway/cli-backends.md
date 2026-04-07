---
read_when:
    - API sağlayıcıları başarısız olduğunda güvenilir bir yedek istiyorsunuz
    - Codex CLI veya diğer yerel AI CLI'larını çalıştırıyor ve bunları yeniden kullanmak istiyorsunuz
    - CLI arka uç araç erişimi için MCP local loopback köprüsünü anlamak istiyorsunuz
summary: 'CLI arka uçları: isteğe bağlı MCP araç köprüsüyle yerel AI CLI yedeği'
title: CLI Arka Uçları
x-i18n:
    generated_at: "2026-04-07T08:44:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: f061357f420455ad6ffaabe7fe28f1fb1b1769d73a4eb2e6f45c6eb3c2e36667
    source_path: gateway/cli-backends.md
    workflow: 15
---

# CLI arka uçları (yedek çalışma zamanı)

OpenClaw, API sağlayıcıları kapalı olduğunda, hız sınırına takıldığında
veya geçici olarak hatalı davrandığında **yalnızca metin tabanlı bir yedek**
olarak **yerel AI CLI'ları** çalıştırabilir. Bu kasıtlı olarak temkinlidir:

- **OpenClaw araçları doğrudan enjekte edilmez**, ancak `bundleMcp: true`
  kullanan arka uçlar, gateway araçlarını bir local loopback MCP köprüsü üzerinden alabilir.
- Bunu destekleyen CLI'lar için **JSONL akışı**.
- **Oturumlar desteklenir** (böylece takip eden dönüşler tutarlı kalır).
- CLI görüntü yollarını kabul ediyorsa **görüntüler aktarılabilir**.

Bu, birincil yol olmaktan ziyade bir **güvenlik ağı** olarak tasarlanmıştır.
Dış API'lere güvenmeden “her zaman çalışır” metin yanıtları istediğinizde bunu kullanın.

ACP oturum denetimleri, arka plan görevleri,
iz/parçacık-konuşma bağlama ve kalıcı harici kodlama oturumları ile tam bir harness çalışma zamanı istiyorsanız
bunun yerine [ACP Agents](/tr/tools/acp-agents) kullanın. CLI arka uçları ACP değildir.

## Yeni başlayanlar için hızlı başlangıç

Codex CLI'ı **hiç yapılandırma olmadan** kullanabilirsiniz (paketle gelen OpenAI eklentisi
varsayılan bir arka uç kaydeder):

```bash
openclaw agent --message "hi" --model codex-cli/gpt-5.4
```

Gateway'iniz launchd/systemd altında çalışıyorsa ve PATH minimal ise, yalnızca
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

Hepsi bu. Anahtar yok, CLI'ın kendisi dışında ek kimlik doğrulama yapılandırması gerekmez.

Bir gateway ana makinesinde paketle gelen bir CLI arka ucunu **birincil mesaj sağlayıcısı** olarak kullanırsanız,
OpenClaw artık yapılandırmanız bu arka uca model başvurusunda veya
`agents.defaults.cliBackends` altında açıkça atıfta bulunduğunda
sahip olan paketle gelen eklentiyi otomatik olarak yükler.

## Yedek olarak kullanma

Bir CLI arka ucunu yedek listenize ekleyin; böylece yalnızca birincil modeller başarısız olduğunda çalışır:

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

- `agents.defaults.models` (izin listesi) kullanıyorsanız, CLI arka uç modelerinizi de oraya eklemeniz gerekir.
- Birincil sağlayıcı başarısız olursa (kimlik doğrulama, hız sınırları, zaman aşımları), OpenClaw
  sıradaki CLI arka ucunu dener.

## Yapılandırmaya genel bakış

Tüm CLI arka uçları şu konumda bulunur:

```
agents.defaults.cliBackends
```

Her giriş bir **sağlayıcı kimliği** ile anahtarlanır (`codex-cli`, `my-cli` gibi).
Sağlayıcı kimliği model başvurunuzun sol tarafı olur:

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

1. Sağlayıcı ön ekine göre (`codex-cli/...`) bir arka uç **seçer**.
2. Aynı OpenClaw istemi + çalışma alanı bağlamını kullanarak bir sistem istemi **oluşturur**.
3. Geçmiş tutarlı kalsın diye CLI'ı destekleniyorsa bir oturum kimliği ile **çalıştırır**.
4. Çıktıyı (JSON veya düz metin) **ayrıştırır** ve son metni döndürür.
5. Takip edenler aynı CLI oturumunu yeniden kullansın diye arka uç başına oturum kimliklerini **kalıcılaştırır**.

<Note>
Paketle gelen Anthropic `claude-cli` arka ucu yeniden destekleniyor. Anthropic çalışanları,
OpenClaw tarzı Claude CLI kullanımına yeniden izin verildiğini söylediler, bu yüzden OpenClaw
Anthropic yeni bir ilke yayımlamadığı sürece bu entegrasyon için
`claude -p` kullanımını onaylı kabul eder.
</Note>

## Oturumlar

- CLI oturumları destekliyorsa, `sessionArg` (`--session-id` gibi) veya
  kimliğin birden çok bayrağa eklenmesi gerektiğinde `sessionArgs` (`{sessionId}` yer tutucusu) ayarlayın.
- CLI farklı bayraklarla bir **resume alt komutu** kullanıyorsa,
  `resumeArgs` ayarlayın (yeniden devam etmede `args` yerine geçer) ve isteğe bağlı olarak
  `resumeOutput` ayarlayın (JSON olmayan devamlar için).
- `sessionMode`:
  - `always`: her zaman bir oturum kimliği gönderir (saklanmış yoksa yeni UUID).
  - `existing`: yalnızca daha önce saklanmış bir kimlik varsa oturum kimliği gönderir.
  - `none`: asla oturum kimliği göndermez.

Serileştirme notları:

- `serialize: true`, aynı hat çalıştırmalarını sıralı tutar.
- Çoğu CLI tek bir sağlayıcı hattında serileştirme yapar.
- OpenClaw, arka uç kimlik doğrulama durumu değiştiğinde, buna yeniden giriş,
  token döndürme veya değişmiş kimlik doğrulama profili kimlik bilgisi dahil olmak üzere,
  saklanan CLI oturumu yeniden kullanımını bırakır.

## Görüntüler (aktarım)

CLI'ınız görüntü yollarını kabul ediyorsa `imageArg` ayarlayın:

```json5
imageArg: "--image",
imageMode: "repeat"
```

OpenClaw base64 görüntüleri geçici dosyalara yazar. `imageArg` ayarlıysa bu
yollar CLI argümanları olarak geçirilir. `imageArg` eksikse OpenClaw dosya
yollarını isteme ekler (yol enjeksiyonu); bu da yerel dosyaları düz yollardan otomatik yükleyen
CLI'lar için yeterlidir.

## Girdiler / çıktılar

- `output: "json"` (varsayılan) JSON ayrıştırmayı ve metin + oturum kimliği çıkarmayı dener.
- Gemini CLI JSON çıktısı için OpenClaw, `usage` eksik veya boş olduğunda
  yanıt metnini `response` alanından ve kullanımı `stats` alanından okur.
- `output: "jsonl"` JSONL akışlarını ayrıştırır (örneğin Codex CLI `--json`) ve mevcut olduğunda son ajan mesajını ve oturum
  tanımlayıcılarını çıkarır.
- `output: "text"` stdout'u son yanıt olarak ele alır.

Girdi modları:

- `input: "arg"` (varsayılan) istemi son CLI argümanı olarak geçirir.
- `input: "stdin"` istemi stdin üzerinden gönderir.
- İstem çok uzunsa ve `maxPromptArgChars` ayarlıysa stdin kullanılır.

## Varsayılanlar (eklenti sahibi)

Paketle gelen OpenAI eklentisi `codex-cli` için bir varsayılan da kaydeder:

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
- `args: ["--prompt", "--output-format", "json"]`
- `resumeArgs: ["--resume", "{sessionId}", "--prompt", "--output-format", "json"]`
- `modelArg: "--model"`
- `sessionMode: "existing"`
- `sessionIdFields: ["session_id", "sessionId"]`

Ön koşul: yerel Gemini CLI kurulu olmalı ve
PATH üzerinde `gemini` olarak erişilebilir olmalıdır (`brew install gemini-cli` veya
`npm install -g @google/gemini-cli`).

Gemini CLI JSON notları:

- Yanıt metni JSON `response` alanından okunur.
- Kullanım, `usage` yoksa veya boşsa `stats` alanına geri döner.
- `stats.cached`, OpenClaw `cacheRead` içine normalize edilir.
- `stats.input` eksikse OpenClaw giriş tokenlarını
  `stats.input_tokens - stats.cached` üzerinden türetir.

Yalnızca gerektiğinde geçersiz kılın (yaygın durum: mutlak `command` yolu).

## Eklenti sahibi varsayılanlar

CLI arka uç varsayılanları artık eklenti yüzeyinin bir parçasıdır:

- Eklentiler bunları `api.registerCliBackend(...)` ile kaydeder.
- Arka uç `id`, model başvurularında sağlayıcı ön eki olur.
- `agents.defaults.cliBackends.<id>` içindeki kullanıcı yapılandırması yine de eklenti varsayılanını geçersiz kılar.
- Arka uca özgü yapılandırma temizliği, isteğe bağlı
  `normalizeConfig` kancası üzerinden eklenti sahibi olarak kalır.

## Bundle MCP katmanları

CLI arka uçları OpenClaw araç çağrılarını **doğrudan** almaz, ancak bir arka uç
`bundleMcp: true` ile oluşturulmuş bir MCP yapılandırma katmanını etkinleştirebilir.

Geçerli paketle gelen davranış:

- `codex-cli`: bundle MCP katmanı yok
- `google-gemini-cli`: bundle MCP katmanı yok

Bundle MCP etkinleştirildiğinde OpenClaw:

- gateway araçlarını CLI işlemine açan bir local loopback HTTP MCP sunucusu başlatır
- köprünün kimliğini oturum başına bir token ile doğrular (`OPENCLAW_MCP_TOKEN`)
- araç erişimini geçerli oturum, hesap ve kanal bağlamıyla sınırlar
- geçerli çalışma alanı için etkin bundle-MCP sunucularını yükler
- bunları mevcut tüm arka uç `--mcp-config` değerleriyle birleştirir
- CLI argümanlarını `--strict-mcp-config --mcp-config <generated-file>` geçecek şekilde yeniden yazar

Hiçbir MCP sunucusu etkin değilse, bir arka uç bundle MCP'yi etkinleştirdiğinde
arka plan çalıştırmaları yalıtılmış kalsın diye OpenClaw yine de katı bir yapılandırma enjekte eder.

## Sınırlamalar

- **Doğrudan OpenClaw araç çağrıları yok.** OpenClaw araç çağrılarını
  CLI arka uç protokolüne enjekte etmez. Arka uçlar yalnızca
  `bundleMcp: true` seçtiklerinde gateway araçlarını görür.
- **Akış arka uca özeldir.** Bazı arka uçlar JSONL akışı yapar; diğerleri
  çıkışa kadar arabelleğe alır.
- **Yapılandırılmış çıktılar** CLI'ın JSON biçimine bağlıdır.
- **Codex CLI oturumları** metin çıktısı üzerinden devam eder (JSONL yoktur), bu da
  ilk `--json` çalıştırmasına göre daha az yapılandırılmıştır. OpenClaw oturumları yine de
  normal çalışır.

## Sorun giderme

- **CLI bulunamadı**: `command` için tam yol ayarlayın.
- **Yanlış model adı**: `provider/model` → CLI modeli eşlemesi için `modelAliases` kullanın.
- **Oturum sürekliliği yok**: `sessionArg` ayarlı olduğundan ve `sessionMode` değerinin
  `none` olmadığından emin olun (Codex CLI şu anda JSON çıktısıyla devam edemez).
- **Görüntüler yok sayılıyor**: `imageArg` ayarlayın (ve CLI'ın dosya yollarını desteklediğini doğrulayın).
