---
read_when:
    - إعداد Zalo الشخصي لـ OpenClaw
    - استكشاف أخطاء تسجيل الدخول أو تدفق الرسائل في Zalo الشخصي وإصلاحها
summary: دعم حساب Zalo الشخصي عبر `zca-js` الأصلي (تسجيل الدخول عبر QR)، والإمكانات، والإعداد
title: Zalo الشخصي
x-i18n:
    generated_at: "2026-04-07T07:16:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: 08f50edb2f4c6fe24972efe5e321f5fd0572c7d29af5c1db808151c7c943dc66
    source_path: channels/zalouser.md
    workflow: 15
---

# Zalo الشخصي (غير رسمي)

الحالة: تجريبي. يقوم هذا التكامل بأتمتة **حساب Zalo شخصي** عبر `zca-js` الأصلي داخل OpenClaw.

> **تحذير:** هذا تكامل غير رسمي وقد يؤدي إلى تعليق الحساب/حظره. استخدمه على مسؤوليتك الخاصة.

## Plugin المضمّن

يأتي Zalo الشخصي كـ plugin مضمّن في إصدارات OpenClaw الحالية، لذلك لا تحتاج
البنيات المعبأة العادية إلى تثبيت منفصل.

إذا كنت تستخدم إصدارًا أقدم أو تثبيتًا مخصصًا لا يتضمن Zalo الشخصي،
فقم بتثبيته يدويًا:

- التثبيت عبر CLI: `openclaw plugins install @openclaw/zalouser`
- أو من نسخة مصدر محلية: `openclaw plugins install ./path/to/local/zalouser-plugin`
- التفاصيل: [Plugins](/ar/tools/plugin)

لا يلزم أي ملف CLI ثنائي خارجي لـ `zca`/`openzca`.

## الإعداد السريع (للمبتدئين)

1. تأكد من أن plugin الخاص بـ Zalo الشخصي متاح.
   - إصدارات OpenClaw المعبأة الحالية تتضمنه بالفعل.
   - يمكن للتثبيتات الأقدم/المخصصة إضافته يدويًا باستخدام الأوامر أعلاه.
2. سجّل الدخول (QR، على جهاز Gateway):
   - `openclaw channels login --channel zalouser`
   - امسح رمز QR باستخدام تطبيق Zalo على الهاتف المحمول.
3. فعّل القناة:

```json5
{
  channels: {
    zalouser: {
      enabled: true,
      dmPolicy: "pairing",
    },
  },
}
```

4. أعد تشغيل Gateway (أو أكمل الإعداد).
5. يكون وصول الرسائل المباشرة مضبوطًا افتراضيًا على الاقتران؛ وافق على رمز الاقتران عند أول تواصل.

## ما هو

- يعمل بالكامل داخل العملية عبر `zca-js`.
- يستخدم مستمعي الأحداث الأصليين لتلقي الرسائل الواردة.
- يرسل الردود مباشرة عبر واجهة JS البرمجية (نص/وسائط/رابط).
- مصمم لحالات استخدام "الحساب الشخصي" حيث لا تكون Zalo Bot API متاحة.

## التسمية

معرّف القناة هو `zalouser` لتوضيح أن هذا يؤتمت **حساب مستخدم Zalo شخصي** (غير رسمي). نحتفظ بالاسم `zalo` محجوزًا لتكامل رسمي محتمل مع Zalo API في المستقبل.

## العثور على المعرّفات (الدليل)

استخدم CLI الخاص بالدليل لاكتشاف الأقران/المجموعات ومعرّفاتها:

```bash
openclaw directory self --channel zalouser
openclaw directory peers list --channel zalouser --query "name"
openclaw directory groups list --channel zalouser --query "work"
```

## الحدود

- يتم تقسيم النصوص الصادرة إلى أجزاء بحوالي 2000 حرف (حدود عميل Zalo).
- يتم حظر البث افتراضيًا.

## التحكم في الوصول (الرسائل المباشرة)

يدعم `channels.zalouser.dmPolicy`: `pairing | allowlist | open | disabled` (الافتراضي: `pairing`).

يقبل `channels.zalouser.allowFrom` معرّفات المستخدمين أو الأسماء. أثناء الإعداد، يتم تحويل الأسماء إلى معرّفات باستخدام بحث جهات الاتصال داخل العملية الخاص بـ plugin.

وافِق عبر:

- `openclaw pairing list zalouser`
- `openclaw pairing approve zalouser <code>`

## الوصول إلى المجموعات (اختياري)

- الافتراضي: `channels.zalouser.groupPolicy = "open"` (المجموعات مسموح بها). استخدم `channels.defaults.groupPolicy` لتجاوز القيمة الافتراضية عند عدم تعيينها.
- للقيْد إلى قائمة سماح:
  - `channels.zalouser.groupPolicy = "allowlist"`
  - `channels.zalouser.groups` (يجب أن تكون المفاتيح معرّفات مجموعات مستقرة؛ وتُحوَّل الأسماء إلى معرّفات عند بدء التشغيل عندما يكون ذلك ممكنًا)
  - `channels.zalouser.groupAllowFrom` (يتحكم في المرسلين داخل المجموعات المسموح بها الذين يمكنهم تشغيل البوت)
- لحظر جميع المجموعات: `channels.zalouser.groupPolicy = "disabled"`.
- يمكن لمعالج الإعداد المطالبة بقوائم سماح للمجموعات.
- عند بدء التشغيل، يقوم OpenClaw بتحويل أسماء المجموعات/المستخدمين في قوائم السماح إلى معرّفات ويسجل عملية الربط.
- تتم مطابقة قائمة سماح المجموعات حسب المعرّف فقط افتراضيًا. تُتجاهل الأسماء غير المحلولة لأغراض التفويض ما لم يتم تفعيل `channels.zalouser.dangerouslyAllowNameMatching: true`.
- `channels.zalouser.dangerouslyAllowNameMatching: true` هو وضع توافق طارئ يعيد تمكين المطابقة باستخدام أسماء المجموعات القابلة للتغيير.
- إذا لم يتم تعيين `groupAllowFrom`، فسيعود وقت التشغيل إلى `allowFrom` للتحقق من مرسلي المجموعات.
- تنطبق عمليات التحقق من المرسلين على كل من رسائل المجموعات العادية وأوامر التحكم (على سبيل المثال `/new` و`/reset`).

مثال:

```json5
{
  channels: {
    zalouser: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["1471383327500481391"],
      groups: {
        "123456789": { allow: true },
        "Work Chat": { allow: true },
      },
    },
  },
}
```

### تقييد الإشارة في المجموعات

- يتحكم `channels.zalouser.groups.<group>.requireMention` في ما إذا كانت الردود داخل المجموعات تتطلب إشارة.
- ترتيب التحويل: معرّف/اسم المجموعة المطابق تمامًا -> الاسم المختصر الموحّد للمجموعة -> `*` -> الافتراضي (`true`).
- ينطبق هذا على كل من المجموعات المدرجة في قائمة السماح ووضع المجموعات المفتوح.
- يُحتسب اقتباس رسالة من البوت كإشارة ضمنية لتفعيل المجموعة.
- يمكن لأوامر التحكم المصرّح بها (على سبيل المثال `/new`) تجاوز شرط الإشارة.
- عندما يتم تخطي رسالة مجموعة لأن الإشارة مطلوبة، يخزن OpenClaw الرسالة كتاريخ مجموعة معلّق ويضمّنها في رسالة المجموعة التالية التي تتم معالجتها.
- حد سجل المجموعات يكون افتراضيًا `messages.groupChat.historyLimit` (والاحتياطي `50`). يمكنك تجاوزه لكل حساب عبر `channels.zalouser.historyLimit`.

مثال:

```json5
{
  channels: {
    zalouser: {
      groupPolicy: "allowlist",
      groups: {
        "*": { allow: true, requireMention: true },
        "Work Chat": { allow: true, requireMention: false },
      },
    },
  },
}
```

## تعدد الحسابات

تُربط الحسابات بملفات تعريف `zalouser` في حالة OpenClaw. مثال:

```json5
{
  channels: {
    zalouser: {
      enabled: true,
      defaultAccount: "default",
      accounts: {
        work: { enabled: true, profile: "work" },
      },
    },
  },
}
```

## الكتابة، والتفاعلات، وإشعارات التسليم

- يرسل OpenClaw حدث كتابة قبل إرسال الرد (على أساس أفضل جهد).
- إجراء تفاعل الرسالة `react` مدعوم لـ `zalouser` في إجراءات القناة.
  - استخدم `remove: true` لإزالة رمز تفاعل emoji محدد من رسالة.
  - دلالات التفاعلات: [Reactions](/ar/tools/reactions)
- بالنسبة إلى الرسائل الواردة التي تتضمن بيانات وصفية للحدث، يرسل OpenClaw إشعارات تم التسليم + تمت المشاهدة (على أساس أفضل جهد).

## استكشاف الأخطاء وإصلاحها

**تسجيل الدخول لا يستمر:**

- `openclaw channels status --probe`
- أعد تسجيل الدخول: `openclaw channels logout --channel zalouser && openclaw channels login --channel zalouser`

**لم يتم تحويل اسم في قائمة السماح/المجموعة:**

- استخدم معرّفات رقمية في `allowFrom`/`groupAllowFrom`/`groups`، أو أسماء الأصدقاء/المجموعات المطابقة تمامًا.

**تمت الترقية من إعداد قديم يعتمد على CLI:**

- أزل أي افتراضات قديمة حول عملية `zca` خارجية.
- تعمل القناة الآن بالكامل داخل OpenClaw بدون ملفات CLI ثنائية خارجية.

## ذو صلة

- [نظرة عامة على القنوات](/ar/channels) — جميع القنوات المدعومة
- [الاقتران](/ar/channels/pairing) — مصادقة الرسائل المباشرة وتدفق الاقتران
- [المجموعات](/ar/channels/groups) — سلوك الدردشة الجماعية وتقييد الإشارة
- [توجيه القنوات](/ar/channels/channel-routing) — توجيه الجلسات للرسائل
- [الأمان](/ar/gateway/security) — نموذج الوصول والتقوية
