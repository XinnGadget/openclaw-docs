---
read_when:
    - Harici bir sistemden TaskFlow'ları tetiklemek veya yönlendirmek istiyorsanız
    - Paketlenmiş webhooks plugin'ini yapılandırıyorsanız
summary: 'Webhooks plugin''i: güvenilir harici otomasyon için kimlik doğrulamalı TaskFlow girişi'
title: Webhooks Plugin
x-i18n:
    generated_at: "2026-04-07T08:47:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: a5da12a887752ec6ee853cfdb912db0ae28512a0ffed06fe3828ef2eee15bc9d
    source_path: plugins/webhooks.md
    workflow: 15
---

# Webhooks (plugin)

Webhooks plugin'i, harici
otomasyonu OpenClaw TaskFlows'a bağlayan kimlik doğrulamalı HTTP yolları ekler.

Zapier, n8n, bir CI işi veya
dahili bir servis gibi güvenilir bir sistemin, önce özel bir
plugin yazmadan yönetilen TaskFlow'lar oluşturmasını ve yönlendirmesini istediğinizde bunu kullanın.

## Nerede çalışır

Webhooks plugin'i Gateway süreci içinde çalışır.

Gateway'iniz başka bir makinede çalışıyorsa, plugin'i o
Gateway ana makinesine kurup yapılandırın, ardından Gateway'i yeniden başlatın.

## Yolları yapılandırın

Yapılandırmayı `plugins.entries.webhooks.config` altında ayarlayın:

```json5
{
  plugins: {
    entries: {
      webhooks: {
        enabled: true,
        config: {
          routes: {
            zapier: {
              path: "/plugins/webhooks/zapier",
              sessionKey: "agent:main:main",
              secret: {
                source: "env",
                provider: "default",
                id: "OPENCLAW_WEBHOOK_SECRET",
              },
              controllerId: "webhooks/zapier",
              description: "Zapier TaskFlow bridge",
            },
          },
        },
      },
    },
  },
}
```

Yol alanları:

- `enabled`: isteğe bağlıdır, varsayılan olarak `true`
- `path`: isteğe bağlıdır, varsayılan olarak `/plugins/webhooks/<routeId>`
- `sessionKey`: bağlı TaskFlow'ların sahibi olan gerekli oturum
- `secret`: gerekli paylaşılan gizli anahtar veya SecretRef
- `controllerId`: oluşturulan yönetilen akışlar için isteğe bağlı denetleyici kimliği
- `description`: isteğe bağlı operatör notu

Desteklenen `secret` girdileri:

- Düz dize
- `source: "env" | "file" | "exec"` içeren SecretRef

Gizli anahtar destekli bir yol başlangıçta gizli anahtarını çözemiyorsa, plugin
bozuk bir uç noktayı açığa çıkarmak yerine o yolu atlar ve bir uyarı kaydeder.

## Güvenlik modeli

Her yol, yapılandırılmış
`sessionKey` değerinin TaskFlow yetkisiyle hareket edecek şekilde güvenilir kabul edilir.

Bu, yolun o oturuma ait TaskFlow'ları inceleyebileceği ve değiştirebileceği anlamına gelir; bu nedenle şunları yapmalısınız:

- Yol başına güçlü ve benzersiz bir gizli anahtar kullanın
- Satır içi düz metin gizli anahtarlar yerine gizli anahtar başvurularını tercih edin
- Yolları iş akışına uyan en dar oturuma bağlayın
- Yalnızca ihtiyaç duyduğunuz belirli webhook yolunu açığa çıkarın

Plugin şunları uygular:

- Paylaşılan gizli anahtar kimlik doğrulaması
- İstek gövdesi boyutu ve zaman aşımı korumaları
- Sabit pencereli rate limiting
- Uçuş halindeki istek sınırlaması
- `api.runtime.taskFlow.bindSession(...)` üzerinden sahipliğe bağlı TaskFlow erişimi

## İstek biçimi

Şunlarla `POST` istekleri gönderin:

- `Content-Type: application/json`
- `Authorization: Bearer <secret>` veya `x-openclaw-webhook-secret: <secret>`

Örnek:

```bash
curl -X POST https://gateway.example.com/plugins/webhooks/zapier \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_SHARED_SECRET' \
  -d '{"action":"create_flow","goal":"Review inbound queue"}'
```

## Desteklenen eylemler

Plugin şu anda şu JSON `action` değerlerini kabul eder:

- `create_flow`
- `get_flow`
- `list_flows`
- `find_latest_flow`
- `resolve_flow`
- `get_task_summary`
- `set_waiting`
- `resume_flow`
- `finish_flow`
- `fail_flow`
- `request_cancel`
- `cancel_flow`
- `run_task`

### `create_flow`

Yolun bağlı oturumu için yönetilen bir TaskFlow oluşturur.

Örnek:

```json
{
  "action": "create_flow",
  "goal": "Review inbound queue",
  "status": "queued",
  "notifyPolicy": "done_only"
}
```

### `run_task`

Mevcut bir yönetilen TaskFlow içinde yönetilen bir alt görev oluşturur.

İzin verilen çalışma zamanları şunlardır:

- `subagent`
- `acp`

Örnek:

```json
{
  "action": "run_task",
  "flowId": "flow_123",
  "runtime": "acp",
  "childSessionKey": "agent:main:acp:worker",
  "task": "Inspect the next message batch"
}
```

## Yanıt şekli

Başarılı yanıtlar şunu döndürür:

```json
{
  "ok": true,
  "routeId": "zapier",
  "result": {}
}
```

Reddedilen istekler şunu döndürür:

```json
{
  "ok": false,
  "routeId": "zapier",
  "code": "not_found",
  "error": "TaskFlow not found.",
  "result": {}
}
```

Plugin, webhook yanıtlarından sahip/oturum meta verilerini kasıtlı olarak temizler.

## İlgili belgeler

- [Plugin runtime SDK](/tr/plugins/sdk-runtime)
- [Hooks and webhooks overview](/tr/automation/hooks)
- [CLI webhooks](/cli/webhooks)
