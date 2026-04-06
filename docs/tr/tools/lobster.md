---
read_when:
    - Açık onaylarla belirleyici çok adımlı iş akışları istediğinizde
    - Önceki adımları yeniden çalıştırmadan bir iş akışına devam etmeniz gerektiğinde
summary: Açık onay kapılarına sahip, devam ettirilebilir OpenClaw için türlenmiş iş akışı çalışma zamanı.
title: Lobster
x-i18n:
    generated_at: "2026-04-06T03:14:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: c1014945d104ef8fdca0d30be89e35136def1b274c6403b06de29e8502b8124b
    source_path: tools/lobster.md
    workflow: 15
---

# Lobster

Lobster, OpenClaw'ın çok adımlı araç dizilerini açık onay kontrol noktalarıyla tek, belirleyici bir işlem olarak çalıştırmasını sağlayan bir iş akışı kabuğudur.

Lobster, ayrılmış arka plan işinin bir yazarlık katmanı üzerindedir. Bireysel görevlerin üzerindeki akış orkestrasyonu için [Task Flow](/tr/automation/taskflow) (`openclaw tasks flow`) bölümüne bakın. Görev etkinlik defteri için [`openclaw tasks`](/tr/automation/tasks) bölümüne bakın.

## Hook

Asistanınız, kendisini yöneten araçları oluşturabilir. Bir iş akışı isteyin; 30 dakika sonra tek çağrı olarak çalışan bir CLI ve boru hatlarına sahip olun. Lobster eksik parçadır: belirleyici boru hatları, açık onaylar ve devam ettirilebilir durum.

## Neden

Bugün karmaşık iş akışları çok sayıda ileri geri araç çağrısı gerektirir. Her çağrı token maliyeti oluşturur ve LLM her adımı orkestre etmek zorunda kalır. Lobster bu orkestrasyonu türlenmiş bir çalışma zamanına taşır:

- **Birçok çağrı yerine tek çağrı**: OpenClaw tek bir Lobster araç çağrısı çalıştırır ve yapılandırılmış bir sonuç alır.
- **Onaylar yerleşik**: Yan etkiler (e-posta gönderme, yorum gönderme) açıkça onaylanana kadar iş akışını durdurur.
- **Devam ettirilebilir**: Durdurulmuş iş akışları bir token döndürür; her şeyi yeniden çalıştırmadan onaylayıp devam edebilirsiniz.

## Düz programlar yerine neden bir DSL?

Lobster kasıtlı olarak küçüktür. Amaç "yeni bir dil" değil; birinci sınıf onaylara ve devam token'larına sahip, öngörülebilir, AI dostu bir boru hattı tanımıdır.

- **Onaylama/devam ettirme yerleşiktir**: Normal bir program bir insana sorabilir, ancak bu çalışma zamanını kendiniz icat etmeden kalıcı bir token ile _duraklayıp devam edemez_.
- **Belirleyicilik + denetlenebilirlik**: Boru hatları veridir, bu yüzden günlüklemek, farklarını almak, yeniden oynatmak ve gözden geçirmek kolaydır.
- **AI için sınırlı yüzey**: Küçük bir dil bilgisi + JSON borulama, “yaratıcı” kod yollarını azaltır ve doğrulamayı gerçekçi kılar.
- **Güvenlik ilkesi yerleşiktir**: Zaman aşımları, çıktı sınırları, sandbox kontrolleri ve allowlist'ler çalışma zamanı tarafından uygulanır; her script tarafından değil.
- **Yine de programlanabilir**: Her adım herhangi bir CLI veya script çağırabilir. JS/TS istiyorsanız `.lobster` dosyalarını koddan üretin.

## Nasıl çalışır

OpenClaw, Lobster iş akışlarını gömülü bir runner kullanarak **süreç içinde** çalıştırır. Harici bir CLI alt süreci oluşturulmaz; iş akışı motoru gateway süreci içinde yürütülür ve doğrudan bir JSON zarfı döndürür.
Boru hattı onay için duraklarsa, araç daha sonra devam edebilmeniz için bir `resumeToken` döndürür.

## Desen: küçük CLI + JSON boruları + onaylar

JSON konuşan küçük komutlar oluşturun, sonra bunları tek bir Lobster çağrısında zincirleyin. (Aşağıdaki komut adları örnektir — kendinizinkilerle değiştirin.)

```bash
inbox list --json
inbox categorize --json
inbox apply --json
```

```json
{
  "action": "run",
  "pipeline": "exec --json --shell 'inbox list --json' | exec --stdin json --shell 'inbox categorize --json' | exec --stdin json --shell 'inbox apply --json' | approve --preview-from-stdin --limit 5 --prompt 'Apply changes?'",
  "timeoutMs": 30000
}
```

Boru hattısı onay isterse, token ile devam edin:

```json
{
  "action": "resume",
  "token": "<resumeToken>",
  "approve": true
}
```

AI iş akışını tetikler; Lobster adımları yürütür. Onay kapıları yan etkileri açık ve denetlenebilir tutar.

Örnek: girdi öğelerini araç çağrılarına eşleme:

```bash
gog.gmail.search --query 'newer_than:1d' \
  | openclaw.invoke --tool message --action send --each --item-key message --args-json '{"provider":"telegram","to":"..."}'
```

## Yalnızca JSON LLM adımları (llm-task)

**Yapılandırılmış bir LLM adımı** gerektiren iş akışları için isteğe bağlı
`llm-task` plugin aracını etkinleştirin ve bunu Lobster içinden çağırın. Bu, iş akışını
belirleyici tutarken yine de bir modelle sınıflandırma/özetleme/taslak oluşturma yapmanızı sağlar.

Aracı etkinleştirin:

```json
{
  "plugins": {
    "entries": {
      "llm-task": { "enabled": true }
    }
  },
  "agents": {
    "list": [
      {
        "id": "main",
        "tools": { "allow": ["llm-task"] }
      }
    ]
  }
}
```

Bunu bir boru hattında kullanın:

```lobster
openclaw.invoke --tool llm-task --action json --args-json '{
  "prompt": "Given the input email, return intent and draft.",
  "thinking": "low",
  "input": { "subject": "Hello", "body": "Can you help?" },
  "schema": {
    "type": "object",
    "properties": {
      "intent": { "type": "string" },
      "draft": { "type": "string" }
    },
    "required": ["intent", "draft"],
    "additionalProperties": false
  }
}'
```

Ayrıntılar ve yapılandırma seçenekleri için [LLM Task](/tr/tools/llm-task) bölümüne bakın.

## İş akışı dosyaları (.lobster)

Lobster, `name`, `args`, `steps`, `env`, `condition` ve `approval` alanlarına sahip YAML/JSON iş akışı dosyalarını çalıştırabilir. OpenClaw araç çağrılarında `pipeline` değerini dosya yolu olarak ayarlayın.

```yaml
name: inbox-triage
args:
  tag:
    default: "family"
steps:
  - id: collect
    command: inbox list --json
  - id: categorize
    command: inbox categorize --json
    stdin: $collect.stdout
  - id: approve
    command: inbox apply --approve
    stdin: $categorize.stdout
    approval: required
  - id: execute
    command: inbox apply --execute
    stdin: $categorize.stdout
    condition: $approve.approved
```

Notlar:

- `stdin: $step.stdout` ve `stdin: $step.json`, önceki bir adımın çıktısını geçirir.
- `condition` (veya `when`), adımları `$step.approved` üzerinde kapılayabilir.

## Lobster'ı yükleyin

Paketlenmiş Lobster iş akışları süreç içinde çalışır; ayrı bir `lobster` ikili dosyası gerekmez. Gömülü runner, Lobster plugin'i ile birlikte gelir.

Geliştirme veya harici boru hatları için bağımsız Lobster CLI'a ihtiyacınız varsa, bunu [Lobster repo](https://github.com/openclaw/lobster) üzerinden yükleyin ve `lobster` komutunun `PATH` üzerinde olduğundan emin olun.

## Aracı etkinleştirin

Lobster, **isteğe bağlı** bir plugin aracıdır (varsayılan olarak etkin değildir).

Önerilen (toplamalı, güvenli):

```json
{
  "tools": {
    "alsoAllow": ["lobster"]
  }
}
```

Veya ajan başına:

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "tools": {
          "alsoAllow": ["lobster"]
        }
      }
    ]
  }
}
```

Kısıtlayıcı allowlist modunda çalışmayı amaçlamıyorsanız `tools.allow: ["lobster"]` kullanmaktan kaçının.

Not: allowlist'ler isteğe bağlı plugin'ler için isteğe bağlı katılımla çalışır. Allowlist'iniz yalnızca
`lobster` gibi plugin araçlarını adlandırıyorsa, OpenClaw çekirdek araçları etkin tutar. Çekirdek
araçları kısıtlamak için allowlist'e istediğiniz çekirdek araçları veya grupları da ekleyin.

## Örnek: E-posta sınıflandırma

Lobster olmadan:

```
User: "Check my email and draft replies"
→ openclaw calls gmail.list
→ LLM summarizes
→ User: "draft replies to #2 and #5"
→ LLM drafts
→ User: "send #2"
→ openclaw calls gmail.send
(repeat daily, no memory of what was triaged)
```

Lobster ile:

```json
{
  "action": "run",
  "pipeline": "email.triage --limit 20",
  "timeoutMs": 30000
}
```

Bir JSON zarfı döndürür (kısaltılmış):

```json
{
  "ok": true,
  "status": "needs_approval",
  "output": [{ "summary": "5 need replies, 2 need action" }],
  "requiresApproval": {
    "type": "approval_request",
    "prompt": "Send 2 draft replies?",
    "items": [],
    "resumeToken": "..."
  }
}
```

Kullanıcı onaylar → devam et:

```json
{
  "action": "resume",
  "token": "<resumeToken>",
  "approve": true
}
```

Tek iş akışı. Belirleyici. Güvenli.

## Araç parametreleri

### `run`

Bir boru hattını araç modunda çalıştırın.

```json
{
  "action": "run",
  "pipeline": "gog.gmail.search --query 'newer_than:1d' | email.triage",
  "cwd": "workspace",
  "timeoutMs": 30000,
  "maxStdoutBytes": 512000
}
```

Argümanlarla bir iş akışı dosyası çalıştırın:

```json
{
  "action": "run",
  "pipeline": "/path/to/inbox-triage.lobster",
  "argsJson": "{\"tag\":\"family\"}"
}
```

### `resume`

Onaydan sonra durdurulmuş bir iş akışına devam edin.

```json
{
  "action": "resume",
  "token": "<resumeToken>",
  "approve": true
}
```

### İsteğe bağlı girdiler

- `cwd`: Boru hattısı için göreli çalışma dizini (gateway çalışma dizini içinde kalmalıdır).
- `timeoutMs`: İş akışı bu süreyi aşarsa iptal edin (varsayılan: 20000).
- `maxStdoutBytes`: Çıktı bu boyutu aşarsa iş akışını iptal edin (varsayılan: 512000).
- `argsJson`: `lobster run --args-json` komutuna geçirilen JSON dizgesi (yalnızca iş akışı dosyaları).

## Çıktı zarfı

Lobster, üç durumdan biriyle bir JSON zarfı döndürür:

- `ok` → başarıyla tamamlandı
- `needs_approval` → duraklatıldı; devam etmek için `requiresApproval.resumeToken` gerekir
- `cancelled` → açıkça reddedildi veya iptal edildi

Araç, zarfı hem `content` içinde (güzel biçimlendirilmiş JSON) hem de `details` içinde (ham nesne) gösterir.

## Onaylar

`requiresApproval` mevcutsa istemi inceleyin ve karar verin:

- `approve: true` → devam edin ve yan etkileri sürdürün
- `approve: false` → iş akışını iptal edin ve sonlandırın

Özel jq/heredoc yapıştırıcısı olmadan onay isteklerine bir JSON önizlemesi eklemek için `approve --preview-from-stdin --limit N` kullanın. Devam token'ları artık küçüktür: Lobster iş akışı devam durumunu kendi durum dizini altında saklar ve küçük bir token anahtarı geri verir.

## OpenProse

OpenProse, Lobster ile iyi eşleşir: çok ajanlı hazırlığı orkestre etmek için `/prose` kullanın, ardından belirleyici onaylar için bir Lobster boru hattı çalıştırın. Bir Prose programının Lobster'a ihtiyacı varsa, alt ajanlar için `tools.subagents.tools` üzerinden `lobster` aracına izin verin. Bkz. [OpenProse](/tr/prose).

## Güvenlik

- **Yalnızca yerel süreç içi** — iş akışları gateway süreci içinde yürütülür; plugin'in kendisinden ağ çağrısı yapılmaz.
- **Sır yok** — Lobster OAuth yönetmez; bunu yapan OpenClaw araçlarını çağırır.
- **Sandbox farkındalıklı** — araç bağlamı sandbox içindeyken devre dışıdır.
- **Sertleştirilmiş** — zaman aşımları ve çıktı sınırları gömülü runner tarafından uygulanır.

## Sorun giderme

- **`lobster timed out`** → `timeoutMs` değerini artırın veya uzun bir boru hattını bölün.
- **`lobster output exceeded maxStdoutBytes`** → `maxStdoutBytes` değerini artırın veya çıktı boyutunu azaltın.
- **`lobster returned invalid JSON`** → boru hattının araç modunda çalıştığından ve yalnızca JSON yazdırdığından emin olun.
- **`lobster failed`** → gömülü runner hata ayrıntıları için gateway günlüklerini kontrol edin.

## Daha fazla bilgi

- [Plugin'ler](/tr/tools/plugin)
- [Plugin aracı yazımı](/tr/plugins/building-plugins#registering-agent-tools)

## Vaka çalışması: topluluk iş akışları

Genel bir örnek: üç Markdown kasasını (kişisel, partner, paylaşılan) yöneten “second brain” CLI + Lobster boru hatları. CLI; istatistikler, gelen kutusu listeleri ve bayat taramalar için JSON üretir; Lobster ise bu komutları `weekly-review`, `inbox-triage`, `memory-consolidation` ve `shared-task-sync` gibi iş akışlarına zincirler; her biri onay kapılarına sahiptir. AI, mümkün olduğunda yargı işini (kategorizasyon) üstlenir; mümkün olmadığında belirleyici kurallara geri döner.

- İleti dizisi: [https://x.com/plattenschieber/status/2014508656335770033](https://x.com/plattenschieber/status/2014508656335770033)
- Repo: [https://github.com/bloomedai/brain-cli](https://github.com/bloomedai/brain-cli)

## İlgili

- [Otomasyon ve Görevler](/tr/automation) — Lobster iş akışlarını zamanlama
- [Otomasyon Genel Bakışı](/tr/automation) — tüm otomasyon mekanizmaları
- [Araçlar Genel Bakışı](/tr/tools) — kullanılabilir tüm ajan araçları
