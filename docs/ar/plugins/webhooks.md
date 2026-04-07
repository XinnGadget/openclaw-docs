---
read_when:
    - تريد تشغيل TaskFlows أو التحكم فيها من نظام خارجي
    - أنت تهيّئ إضافة webhooks المضمّنة
summary: 'إضافة Webhooks: إدخال TaskFlow موثّق للمصادقة من أجل الأتمتة الخارجية الموثوقة'
title: إضافة Webhooks
x-i18n:
    generated_at: "2026-04-07T07:20:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: a5da12a887752ec6ee853cfdb912db0ae28512a0ffed06fe3828ef2eee15bc9d
    source_path: plugins/webhooks.md
    workflow: 15
---

# Webhooks (إضافة)

تضيف إضافة Webhooks مسارات HTTP موثّقة بالمصادقة تربط الأتمتة الخارجية
بـ OpenClaw TaskFlows.

استخدمها عندما تريد أن يتمكن نظام موثوق مثل Zapier أو n8n أو مهمة CI أو
خدمة داخلية من إنشاء TaskFlows مُدارة والتحكم فيها من دون كتابة إضافة مخصصة
أولًا.

## مكان التشغيل

تعمل إضافة Webhooks داخل عملية Gateway.

إذا كان Gateway يعمل على جهاز آخر، فقم بتثبيت الإضافة وتهيئتها على مضيف
Gateway هذا، ثم أعد تشغيل Gateway.

## تهيئة المسارات

اضبط الإعدادات تحت `plugins.entries.webhooks.config`:

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

حقول المسار:

- `enabled`: اختياري، والقيمة الافتراضية `true`
- `path`: اختياري، والقيمة الافتراضية `/plugins/webhooks/<routeId>`
- `sessionKey`: الجلسة المطلوبة التي تملك TaskFlows المرتبطة
- `secret`: سر مشترك مطلوب أو SecretRef
- `controllerId`: معرّف متحكم اختياري للتدفقات المُدارة التي يتم إنشاؤها
- `description`: ملاحظة اختيارية للمشغّل

مدخلات `secret` المدعومة:

- سلسلة نصية عادية
- SecretRef مع `source: "env" | "file" | "exec"`

إذا تعذر على مسار مدعوم بسر حلّ سره عند بدء التشغيل، فإن الإضافة تتخطى هذا
المسار وتسجّل تحذيرًا بدلًا من كشف نقطة نهاية معطلة.

## نموذج الأمان

يُوثَق بكل مسار ليتصرف بصلاحية TaskFlow الخاصة بـ `sessionKey`
المكوَّنة له.

وهذا يعني أن المسار يمكنه فحص وتعديل TaskFlows المملوكة لتلك الجلسة، لذا
ينبغي عليك:

- استخدام سر قوي وفريد لكل مسار
- تفضيل مراجع الأسرار على الأسرار النصية المضمّنة مباشرة
- ربط المسارات بأضيق جلسة تناسب سير العمل
- كشف مسار webhook المحدد الذي تحتاجه فقط

تطبّق الإضافة ما يلي:

- مصادقة بالسر المشترك
- حواجز لحجم جسم الطلب والمهلة الزمنية
- تحديد المعدل بنافذة ثابتة
- تحديد عدد الطلبات الجاري تنفيذها
- وصول TaskFlow مرتبط بالمالك عبر `api.runtime.taskFlow.bindSession(...)`

## تنسيق الطلب

أرسل طلبات `POST` مع:

- `Content-Type: application/json`
- `Authorization: Bearer <secret>` أو `x-openclaw-webhook-secret: <secret>`

مثال:

```bash
curl -X POST https://gateway.example.com/plugins/webhooks/zapier \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_SHARED_SECRET' \
  -d '{"action":"create_flow","goal":"Review inbound queue"}'
```

## الإجراءات المدعومة

تقبل الإضافة حاليًا قيم `action` التالية في JSON:

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

ينشئ TaskFlow مُدارًا للجلسة المرتبطة بالمسار.

مثال:

```json
{
  "action": "create_flow",
  "goal": "Review inbound queue",
  "status": "queued",
  "notifyPolicy": "done_only"
}
```

### `run_task`

ينشئ مهمة فرعية مُدارة داخل TaskFlow مُدار موجود.

بيئات التشغيل المسموح بها هي:

- `subagent`
- `acp`

مثال:

```json
{
  "action": "run_task",
  "flowId": "flow_123",
  "runtime": "acp",
  "childSessionKey": "agent:main:acp:worker",
  "task": "Inspect the next message batch"
}
```

## شكل الاستجابة

تعيد الاستجابات الناجحة:

```json
{
  "ok": true,
  "routeId": "zapier",
  "result": {}
}
```

وتعيد الطلبات المرفوضة:

```json
{
  "ok": false,
  "routeId": "zapier",
  "code": "not_found",
  "error": "TaskFlow not found.",
  "result": {}
}
```

تتعمّد الإضافة إزالة بيانات تعريف المالك/الجلسة من استجابات webhook.

## وثائق ذات صلة

- [Plugin runtime SDK](/ar/plugins/sdk-runtime)
- [نظرة عامة على Hooks وwebhooks](/ar/automation/hooks)
- [CLI webhooks](/cli/webhooks)
