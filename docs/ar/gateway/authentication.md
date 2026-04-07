---
read_when:
    - استكشاف أخطاء مصادقة النماذج أو انتهاء صلاحية OAuth وإصلاحها
    - توثيق المصادقة أو تخزين بيانات الاعتماد
summary: 'مصادقة النماذج: OAuth، ومفاتيح API، وإعادة استخدام Claude CLI، وAnthropic setup-token'
title: المصادقة
x-i18n:
    generated_at: "2026-04-07T07:17:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9db0ad9eccd7e3e3ca328adaad260bc4288a8ccdbe2dc0c24d9fd049b7ab9231
    source_path: gateway/authentication.md
    workflow: 15
---

# المصادقة (موفرو النماذج)

<Note>
تغطي هذه الصفحة مصادقة **موفر النموذج** (مفاتيح API، وOAuth، وإعادة استخدام Claude CLI، وAnthropic setup-token). أما **مصادقة اتصال gateway** (الرمز المميز، وكلمة المرور، وtrusted-proxy)، فراجع [Configuration](/ar/gateway/configuration) و[Trusted Proxy Auth](/ar/gateway/trusted-proxy-auth).
</Note>

يدعم OpenClaw OAuth ومفاتيح API لموفري النماذج. بالنسبة إلى مضيفي gateway
الدائمين، تكون مفاتيح API عادةً الخيار الأكثر قابلية للتنبؤ. كما أن تدفقات
الاشتراك/OAuth مدعومة أيضًا عندما تتوافق مع نموذج حساب موفر الخدمة لديك.

راجع [/concepts/oauth](/ar/concepts/oauth) للاطلاع على تدفق OAuth الكامل وتخطيط
التخزين.
وبالنسبة إلى المصادقة المستندة إلى SecretRef (موفرو `env`/`file`/`exec`)، راجع [Secrets Management](/ar/gateway/secrets).
وبالنسبة إلى قواعد أهلية بيانات الاعتماد/رموز الأسباب المستخدمة بواسطة `models status --probe`، راجع
[Auth Credential Semantics](/ar/auth-credential-semantics).

## الإعداد الموصى به (API key، أي موفر)

إذا كنت تشغّل gateway طويل الأمد، فابدأ باستخدام API key لموفر الخدمة
الذي اخترته.
وبالنسبة إلى Anthropic تحديدًا، تظل مصادقة API key هي إعداد الخادم الأكثر
قابلية للتنبؤ، لكن OpenClaw يدعم أيضًا إعادة استخدام تسجيل دخول Claude CLI محلي.

1. أنشئ API key في لوحة موفر الخدمة لديك.
2. ضعه على **مضيف gateway** (الجهاز الذي يشغّل `openclaw gateway`).

```bash
export <PROVIDER>_API_KEY="..."
openclaw models status
```

3. إذا كان Gateway يعمل تحت systemd/launchd، فمن الأفضل وضع المفتاح في
   `~/.openclaw/.env` حتى يتمكن الـ daemon من قراءته:

```bash
cat >> ~/.openclaw/.env <<'EOF'
<PROVIDER>_API_KEY=...
EOF
```

ثم أعد تشغيل الـ daemon (أو أعد تشغيل عملية Gateway) وتحقق مرة أخرى:

```bash
openclaw models status
openclaw doctor
```

إذا كنت تفضل عدم إدارة متغيرات env بنفسك، فيمكن لعملية onboarding تخزين
مفاتيح API لاستخدام الـ daemon: `openclaw onboard`.

راجع [Help](/ar/help) للحصول على تفاصيل حول توريث env (`env.shellEnv`,
`~/.openclaw/.env`، وsystemd/launchd).

## Anthropic: Claude CLI وتوافق الرموز المميزة

لا تزال مصادقة Anthropic setup-token متاحة في OpenClaw باعتبارها مسارًا
مدعومًا للرموز المميزة. وقد أخبرنا موظفو Anthropic منذ ذلك الحين أن استخدام Claude CLI
على نمط OpenClaw مسموح به مرة أخرى، لذلك يتعامل OpenClaw مع إعادة استخدام Claude CLI واستخدام
`claude -p` على أنهما مسموح بهما لهذا التكامل ما لم تنشر Anthropic
سياسة جديدة. وعندما تكون إعادة استخدام Claude CLI متاحة على المضيف،
فهي الآن المسار المفضل.

بالنسبة إلى مضيفي gateway طويلَي الأمد، يظل Anthropic API key هو الإعداد الأكثر
قابلية للتنبؤ. وإذا كنت تريد إعادة استخدام تسجيل دخول Claude موجود على
المضيف نفسه، فاستخدم مسار Anthropic Claude CLI في onboarding/configure.

إدخال الرمز المميز يدويًا (أي موفر؛ يكتب إلى `auth-profiles.json` + يحدّث الإعداد):

```bash
openclaw models auth paste-token --provider openrouter
```

كما أن مراجع ملف تعريف المصادقة مدعومة أيضًا لبيانات الاعتماد الثابتة:

- يمكن لبيانات اعتماد `api_key` استخدام `keyRef: { source, provider, id }`
- يمكن لبيانات اعتماد `token` استخدام `tokenRef: { source, provider, id }`
- لا تدعم الملفات الشخصية ذات وضع OAuth بيانات الاعتماد من نوع SecretRef؛ إذا تم تعيين `auth.profiles.<id>.mode` إلى `"oauth"`، فسيتم رفض إدخال `keyRef`/`tokenRef` المدعوم بـ SecretRef لهذا الملف الشخصي.

فحص ملائم للأتمتة (يخرج بالقيمة `1` عند الانتهاء/الغياب، و`2` عند قرب الانتهاء):

```bash
openclaw models status --check
```

فحوصات مصادقة مباشرة:

```bash
openclaw models status --probe
```

ملاحظات:

- يمكن أن تأتي صفوف الفحص من ملفات تعريف المصادقة، أو بيانات اعتماد env، أو `models.json`.
- إذا كان `auth.order.<provider>` الصريح يحذف ملفًا شخصيًا مخزنًا، فسيبلغ الفحص
  عن `excluded_by_auth_order` لذلك الملف الشخصي بدلًا من محاولة استخدامه.
- إذا كانت المصادقة موجودة لكن OpenClaw لا يستطيع تحديد نموذج مرشح قابل للفحص لذلك
  الموفر، فسيبلغ الفحص عن `status: no_model`.
- يمكن أن تكون فترات التهدئة الناتجة عن حدود المعدل مرتبطة بنموذج معين. قد يظل
  الملف الشخصي في حالة تهدئة لنموذج واحد قابلًا للاستخدام لنموذج شقيق على الموفر نفسه.

تم توثيق نصوص التشغيل الاختيارية (systemd/Termux) هنا:
[Auth monitoring scripts](/ar/help/scripts#auth-monitoring-scripts)

## ملاحظة Anthropic

إن الواجهة الخلفية `claude-cli` الخاصة بـ Anthropic مدعومة مرة أخرى.

- أخبرنا موظفو Anthropic أن مسار تكامل OpenClaw هذا مسموح به مرة أخرى.
- لذلك يتعامل OpenClaw مع إعادة استخدام Claude CLI واستخدام `claude -p` باعتبارهما مسموحًا بهما
  للتشغيلات المعتمدة على Anthropic ما لم تنشر Anthropic سياسة جديدة.
- تظل مفاتيح Anthropic API الخيار الأكثر قابلية للتنبؤ لمضيفي gateway
  طويلَي الأمد وللتحكم الصريح في الفوترة على جانب الخادم.

## التحقق من حالة مصادقة النموذج

```bash
openclaw models status
openclaw doctor
```

## سلوك تدوير API key ‏(gateway)

تدعم بعض موفري الخدمة إعادة محاولة الطلب باستخدام مفاتيح بديلة عندما تصادف
استدعاءات API حدًا لمعدل موفر الخدمة.

- ترتيب الأولوية:
  - `OPENCLAW_LIVE_<PROVIDER>_KEY` (تجاوز واحد)
  - `<PROVIDER>_API_KEYS`
  - `<PROVIDER>_API_KEY`
  - `<PROVIDER>_API_KEY_*`
- تتضمن موفرو Google أيضًا `GOOGLE_API_KEY` كخيار احتياطي إضافي.
- تتم إزالة التكرارات من قائمة المفاتيح نفسها قبل الاستخدام.
- يعيد OpenClaw المحاولة بالمفتاح التالي فقط لأخطاء حدود المعدل (على سبيل المثال
  `429`، أو `rate_limit`، أو `quota`، أو `resource exhausted`، أو `Too many concurrent
requests`، أو `ThrottlingException`، أو `concurrency limit reached`، أو
  `workers_ai ... quota limit exceeded`).
- لا تتم إعادة محاولة الأخطاء غير المرتبطة بحدود المعدل باستخدام مفاتيح بديلة.
- إذا فشلت جميع المفاتيح، فسيتم إرجاع الخطأ النهائي من آخر محاولة.

## التحكم في بيانات الاعتماد المستخدمة

### لكل جلسة (أمر الدردشة)

استخدم `/model <alias-or-id>@<profileId>` لتثبيت بيانات اعتماد موفر خدمة محددة للجلسة الحالية (أمثلة على معرّفات الملفات الشخصية: `anthropic:default` و`anthropic:work`).

استخدم `/model` (أو `/model list`) للحصول على محدد مضغوط؛ واستخدم `/model status` للعرض الكامل (المرشحون + ملف تعريف المصادقة التالي، بالإضافة إلى تفاصيل نقطة نهاية الموفر عند ضبطها).

### لكل وكيل (تجاوز CLI)

عيّن تجاوزًا صريحًا لترتيب ملفات تعريف المصادقة لوكيل ما (يتم تخزينه في `auth-state.json` الخاص بذلك الوكيل):

```bash
openclaw models auth order get --provider anthropic
openclaw models auth order set --provider anthropic anthropic:default
openclaw models auth order clear --provider anthropic
```

استخدم `--agent <id>` لاستهداف وكيل معين؛ واحذفه لاستخدام الوكيل الافتراضي المضبوط.
عندما تستكشف أخطاء الترتيب، يعرض `openclaw models status --probe` الملفات الشخصية
المخزنة المحذوفة على أنها `excluded_by_auth_order` بدلًا من تخطيها بصمت.
وعندما تستكشف أخطاء التهدئة، تذكر أن فترات التهدئة الناتجة عن حدود المعدل قد تكون مرتبطة
بمعرّف نموذج واحد بدلًا من ملف تعريف الموفر بالكامل.

## استكشاف الأخطاء وإصلاحها

### "لم يتم العثور على بيانات اعتماد"

إذا كان ملف تعريف Anthropic مفقودًا، فاضبط Anthropic API key على
**مضيف gateway** أو أعد إعداد مسار Anthropic setup-token، ثم تحقق مرة أخرى:

```bash
openclaw models status
```

### الرمز المميز على وشك الانتهاء/منتهي الصلاحية

شغّل `openclaw models status` للتأكد من الملف الشخصي الذي أوشكت صلاحيته على الانتهاء. إذا كان
ملف تعريف الرمز المميز لـ Anthropic مفقودًا أو منتهي الصلاحية، فقم بتحديث هذا الإعداد عبر
setup-token أو انتقل إلى Anthropic API key.
