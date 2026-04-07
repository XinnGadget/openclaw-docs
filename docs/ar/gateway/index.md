---
read_when:
    - تشغيل عملية Gateway أو تصحيح أخطائها
summary: دليل التشغيل لخدمة Gateway ودورة حياتها وعملياتها
title: دليل تشغيل Gateway
x-i18n:
    generated_at: "2026-04-07T07:17:46Z"
    model: gpt-5.4
    provider: openai
    source_hash: fd2c21036e88612861ef2195b8ff7205aca31386bb11558614ade8d1a54fdebd
    source_path: gateway/index.md
    workflow: 15
---

# دليل تشغيل Gateway

استخدم هذه الصفحة لبدء التشغيل في اليوم الأول وعمليات التشغيل في اليوم الثاني لخدمة Gateway.

<CardGroup cols={2}>
  <Card title="استكشاف الأخطاء المتعمق" icon="siren" href="/ar/gateway/troubleshooting">
    تشخيص يبدأ من الأعراض مع سلاسل أوامر دقيقة وتواقيع السجلات.
  </Card>
  <Card title="الإعدادات" icon="sliders" href="/ar/gateway/configuration">
    دليل إعداد موجّه للمهام + مرجع إعدادات كامل.
  </Card>
  <Card title="إدارة الأسرار" icon="key-round" href="/ar/gateway/secrets">
    عقد SecretRef وسلوك اللقطة في وقت التشغيل وعمليات الترحيل/إعادة التحميل.
  </Card>
  <Card title="عقد خطة الأسرار" icon="shield-check" href="/ar/gateway/secrets-plan-contract">
    قواعد `secrets apply` الدقيقة للهدف/المسار وسلوك ملفات تعريف المصادقة المعتمدة على المراجع فقط.
  </Card>
</CardGroup>

## بدء تشغيل محلي خلال 5 دقائق

<Steps>
  <Step title="ابدأ Gateway">

```bash
openclaw gateway --port 18789
# debug/trace mirrored to stdio
openclaw gateway --port 18789 --verbose
# force-kill listener on selected port, then start
openclaw gateway --force
```

  </Step>

  <Step title="تحقق من سلامة الخدمة">

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
```

الأساس السليم: `Runtime: running` و`RPC probe: ok`.

  </Step>

  <Step title="تحقق من جاهزية القنوات">

```bash
openclaw channels status --probe
```

مع Gateway يمكن الوصول إليه، يشغّل هذا فحوصات مباشرة لكل حساب للقنوات وتدقيقات اختيارية.
إذا تعذر الوصول إلى Gateway، يعود CLI إلى ملخصات القنوات المعتمدة على الإعدادات فقط بدلًا
من مخرجات الفحص المباشر.

  </Step>
</Steps>

<Note>
تراقب إعادة تحميل إعدادات Gateway مسار ملف الإعدادات النشط (المُحدَّد من افتراضيات الملف الشخصي/الحالة، أو `OPENCLAW_CONFIG_PATH` عند ضبطه).
الوضع الافتراضي هو `gateway.reload.mode="hybrid"`.
بعد أول تحميل ناجح، تقدّم العملية الجارية اللقطة النشطة من الإعدادات الموجودة في الذاكرة؛ وتؤدي إعادة التحميل الناجحة إلى تبديل تلك اللقطة بشكل ذري.
</Note>

## نموذج وقت التشغيل

- عملية واحدة تعمل دائمًا للتوجيه ومستوى التحكم واتصالات القنوات.
- منفذ واحد متعدد الإرسال من أجل:
  - WebSocket للتحكم/RPC
  - واجهات HTTP API متوافقة مع OpenAI (`/v1/models` و`/v1/embeddings` و`/v1/chat/completions` و`/v1/responses` و`/tools/invoke`)
  - Control UI وhooks
- وضع الربط الافتراضي: `loopback`.
- المصادقة مطلوبة افتراضيًا. تستخدم إعدادات السر المشترك
  `gateway.auth.token` / `gateway.auth.password` (أو
  `OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`)، ويمكن لإعدادات
  الوكيل العكسي غير المعتمدة على loopback استخدام `gateway.auth.mode: "trusted-proxy"`.

## نقاط النهاية المتوافقة مع OpenAI

أصبحت واجهة التوافق الأعلى أثرًا في OpenClaw الآن هي:

- `GET /v1/models`
- `GET /v1/models/{id}`
- `POST /v1/embeddings`
- `POST /v1/chat/completions`
- `POST /v1/responses`

لماذا تهم هذه المجموعة:

- تتحقق معظم تكاملات Open WebUI وLobeChat وLibreChat من `/v1/models` أولًا.
- تتوقع العديد من مسارات RAG والذاكرة وجود `/v1/embeddings`.
- تفضّل العملاء الأصليون للوكلاء بشكل متزايد `/v1/responses`.

ملاحظة تخطيطية:

- `/v1/models` موجّه للوكلاء أولًا: فهو يعيد `openclaw` و`openclaw/default` و`openclaw/<agentId>`.
- `openclaw/default` هو الاسم المستعار الثابت الذي يطابق دائمًا الوكيل الافتراضي المكوّن.
- استخدم `x-openclaw-model` عندما تريد تجاوز مزوّد/نموذج الخلفية؛ وإلا يظل إعداد النموذج والتضمين العادي للوكيل المحدد هو المتحكم.

كل هذه النقاط تعمل على منفذ Gateway الرئيسي وتستخدم نفس حد مصادقة المشغّل الموثوق مثل بقية واجهة HTTP API الخاصة بـ Gateway.

### أسبقية المنفذ والربط

| الإعداد      | ترتيب التحديد                                                |
| ------------ | ------------------------------------------------------------ |
| منفذ Gateway | `--port` → `OPENCLAW_GATEWAY_PORT` → `gateway.port` → `18789` |
| وضع الربط    | CLI/override → `gateway.bind` → `loopback`                   |

### أوضاع إعادة التحميل السريع

| `gateway.reload.mode` | السلوك                                   |
| --------------------- | ---------------------------------------- |
| `off`                 | لا توجد إعادة تحميل للإعدادات            |
| `hot`                 | تطبيق التغييرات الآمنة للتحديث السريع فقط |
| `restart`             | إعادة التشغيل عند التغييرات التي تتطلب إعادة تحميل |
| `hybrid` (الافتراضي) | تطبيق سريع عندما يكون آمنًا، وإعادة تشغيل عند الحاجة |

## مجموعة أوامر المشغّل

```bash
openclaw gateway status
openclaw gateway status --deep   # adds a system-level service scan
openclaw gateway status --json
openclaw gateway install
openclaw gateway restart
openclaw gateway stop
openclaw secrets reload
openclaw logs --follow
openclaw doctor
```

إن `gateway status --deep` مخصص لاكتشاف الخدمات الإضافية (وحدات LaunchDaemons/systemd system
وschtasks)، وليس لفحص سلامة RPC أعمق.

## عدة Gateways (على المضيف نفسه)

يجب أن تشغّل معظم عمليات التثبيت Gateway واحدًا لكل جهاز. يمكن لـ Gateway واحد استضافة عدة
وكلاء وقنوات.

تحتاج إلى عدة Gateways فقط عندما تريد العزل عمدًا أو روبوت إنقاذ.

فحوصات مفيدة:

```bash
openclaw gateway status --deep
openclaw gateway probe
```

ما الذي يجب توقعه:

- يمكن أن يبلّغ `gateway status --deep` عن `Other gateway-like services detected (best effort)`
  ويعرض تلميحات تنظيف عندما تظل تثبيتات launchd/systemd/schtasks القديمة موجودة.
- يمكن أن يحذّر `gateway probe` من `multiple reachable gateways` عندما يستجيب أكثر من هدف
  واحد.
- إذا كان ذلك مقصودًا، فاعزل المنافذ والإعدادات/الحالة وجذور مساحة العمل لكل Gateway.

إعداد مفصل: [/gateway/multiple-gateways](/ar/gateway/multiple-gateways).

## الوصول عن بُعد

المفضل: Tailscale/VPN.
البديل: نفق SSH.

```bash
ssh -N -L 18789:127.0.0.1:18789 user@host
```

ثم صِل العملاء محليًا بـ `ws://127.0.0.1:18789`.

<Warning>
لا تتجاوز أنفاق SSH مصادقة Gateway. في إعدادات السر المشترك، لا يزال يتعين على العملاء
إرسال `token`/`password` حتى عبر النفق. أما في الأوضاع التي تحمل هوية،
فلا يزال يتعين على الطلب استيفاء مسار المصادقة هذا.
</Warning>

راجع: [Gateway البعيد](/ar/gateway/remote) و[المصادقة](/ar/gateway/authentication) و[Tailscale](/ar/gateway/tailscale).

## الإشراف ودورة حياة الخدمة

استخدم عمليات التشغيل الخاضعة للإشراف من أجل موثوقية شبيهة بالإنتاج.

<Tabs>
  <Tab title="macOS (launchd)">

```bash
openclaw gateway install
openclaw gateway status
openclaw gateway restart
openclaw gateway stop
```

تسميات LaunchAgent هي `ai.openclaw.gateway` (الافتراضي) أو `ai.openclaw.<profile>` (ملف شخصي مسمّى). يقوم `openclaw doctor` بتدقيق انجراف إعدادات الخدمة وإصلاحه.

  </Tab>

  <Tab title="Linux (systemd user)">

```bash
openclaw gateway install
systemctl --user enable --now openclaw-gateway[-<profile>].service
openclaw gateway status
```

للاستمرارية بعد تسجيل الخروج، فعّل lingering:

```bash
sudo loginctl enable-linger <user>
```

مثال لوحدة مستخدم يدوية عندما تحتاج إلى مسار تثبيت مخصص:

```ini
[Unit]
Description=OpenClaw Gateway
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/local/bin/openclaw gateway --port 18789
Restart=always
RestartSec=5
TimeoutStopSec=30
TimeoutStartSec=30
SuccessExitStatus=0 143
KillMode=control-group

[Install]
WantedBy=default.target
```

  </Tab>

  <Tab title="Windows (native)">

```powershell
openclaw gateway install
openclaw gateway status --json
openclaw gateway restart
openclaw gateway stop
```

يستخدم بدء التشغيل المُدار الأصلي في Windows Scheduled Task باسم `OpenClaw Gateway`
(أو `OpenClaw Gateway (<profile>)` للملفات الشخصية المسمّاة). إذا تم رفض إنشاء
Scheduled Task، يعود OpenClaw إلى مشغّل داخل مجلد Startup لكل مستخدم
يشير إلى `gateway.cmd` داخل دليل الحالة.

  </Tab>

  <Tab title="Linux (system service)">

استخدم وحدة نظام للمضيفات متعددة المستخدمين/الدائمة التشغيل.

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now openclaw-gateway[-<profile>].service
```

استخدم نص الخدمة نفسه كما في وحدة المستخدم، ولكن ثبّته ضمن
`/etc/systemd/system/openclaw-gateway[-<profile>].service` واضبط
`ExecStart=` إذا كان ملف `openclaw` التنفيذي لديك موجودًا في مكان آخر.

  </Tab>
</Tabs>

## عدة Gateways على مضيف واحد

يجب أن تشغّل معظم الإعدادات **Gateway** واحدًا.
استخدم عدة Gateways فقط للعزل/الاستمرارية الصارمة (على سبيل المثال ملف إنقاذ).

قائمة التحقق لكل نسخة:

- `gateway.port` فريد
- `OPENCLAW_CONFIG_PATH` فريد
- `OPENCLAW_STATE_DIR` فريد
- `agents.defaults.workspace` فريد

مثال:

```bash
OPENCLAW_CONFIG_PATH=~/.openclaw/a.json OPENCLAW_STATE_DIR=~/.openclaw-a openclaw gateway --port 19001
OPENCLAW_CONFIG_PATH=~/.openclaw/b.json OPENCLAW_STATE_DIR=~/.openclaw-b openclaw gateway --port 19002
```

راجع: [عدة Gateways](/ar/gateway/multiple-gateways).

### المسار السريع لملف التطوير

```bash
openclaw --dev setup
openclaw --dev gateway --allow-unconfigured
openclaw --dev status
```

تتضمن القيم الافتراضية حالة/إعدادات معزولة ومنفذ Gateway أساسي `19001`.

## مرجع سريع للبروتوكول (منظور المشغّل)

- يجب أن يكون أول إطار من العميل هو `connect`.
- يعيد Gateway لقطة `hello-ok` (`presence` و`health` و`stateVersion` و`uptimeMs` والحدود/السياسة).
- `hello-ok.features.methods` / `events` هما قائمة اكتشاف متحفظة، وليسا
  تفريغًا مولدًا لكل مسار مساعد قابل للاستدعاء.
- الطلبات: `req(method, params)` → `res(ok/payload|error)`.
- تشمل الأحداث الشائعة `connect.challenge` و`agent` و`chat` و
  `session.message` و`session.tool` و`sessions.changed` و`presence` و`tick` و
  `health` و`heartbeat` وأحداث دورة حياة الاقتران/الموافقة و`shutdown`.

تشغيلات الوكيل تمر بمرحلتين:

1. إقرار قبول فوري (`status:"accepted"`)
2. استجابة إكمال نهائية (`status:"ok"|"error"`)، مع أحداث `agent` متدفقة بينهما.

راجع وثائق البروتوكول الكاملة: [بروتوكول Gateway](/ar/gateway/protocol).

## الفحوصات التشغيلية

### الحيوية

- افتح WS وأرسل `connect`.
- توقّع استجابة `hello-ok` مع لقطة.

### الجاهزية

```bash
openclaw gateway status
openclaw channels status --probe
openclaw health
```

### استعادة الفجوات

لا تُعاد الأحداث. عند وجود فجوات في التسلسل، حدّث الحالة (`health` و`system-presence`) قبل المتابعة.

## تواقيع الأعطال الشائعة

| التوقيع                                                       | المشكلة المحتملة                                                                   |
| ------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `refusing to bind gateway ... without auth`                   | ربط غير loopback من دون مسار مصادقة صالح لـ Gateway                               |
| `another gateway instance is already listening` / `EADDRINUSE` | تعارض منفذ                                                                          |
| `Gateway start blocked: set gateway.mode=local`               | الإعداد مضبوط على الوضع البعيد، أو ختم الوضع المحلي مفقود من إعداد تالف          |
| `unauthorized` during connect                                 | عدم تطابق المصادقة بين العميل وGateway                                             |

للاطلاع على سلاسل تشخيص كاملة، استخدم [استكشاف أخطاء Gateway](/ar/gateway/troubleshooting).

## ضمانات السلامة

- تفشل عملاء بروتوكول Gateway بسرعة عندما لا يكون Gateway متاحًا (من دون رجوع احتياطي ضمني إلى القناة المباشرة).
- تُرفض الإطارات الأولى غير الصالحة/غير `connect` ويُغلق الاتصال.
- يرسل الإغلاق السلس الحدث `shutdown` قبل إغلاق المقبس.

---

ذو صلة:

- [استكشاف الأخطاء وإصلاحها](/ar/gateway/troubleshooting)
- [العملية الخلفية](/ar/gateway/background-process)
- [الإعدادات](/ar/gateway/configuration)
- [السلامة](/ar/gateway/health)
- [Doctor](/ar/gateway/doctor)
- [المصادقة](/ar/gateway/authentication)
