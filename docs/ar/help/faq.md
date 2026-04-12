---
read_when:
    - الإجابة عن الأسئلة الشائعة المتعلقة بالإعداد أو التثبيت أو التهيئة الأولية أو دعم وقت التشغيل
    - فرز المشكلات التي يبلغ عنها المستخدمون قبل بدء تصحيح أعمق للأخطاء
summary: الأسئلة الشائعة حول إعداد OpenClaw وتهيئته واستخدامه
title: الأسئلة الشائعة
x-i18n:
    generated_at: "2026-04-12T23:28:24Z"
    model: gpt-5.4
    provider: openai
    source_hash: d2a78d0fea9596625cc2753e6dc8cc42c2379a3a0c91729265eee0261fe53eaa
    source_path: help/faq.md
    workflow: 15
---

# الأسئلة الشائعة

إجابات سريعة بالإضافة إلى استكشاف أخطاء أعمق لبيئات الاستخدام الواقعية (التطوير المحلي، VPS، إعدادات الوكلاء المتعددين، OAuth/مفاتيح API، والتبديل الاحتياطي للنماذج). لتشخيصات وقت التشغيل، راجع [استكشاف الأخطاء وإصلاحها](/ar/gateway/troubleshooting). وللمرجع الكامل للإعدادات، راجع [الإعدادات](/ar/gateway/configuration).

## أول 60 ثانية إذا كان هناك شيء معطّل

1. **الحالة السريعة (أول فحص)**

   ```bash
   openclaw status
   ```

   ملخص محلي سريع: نظام التشغيل + التحديث، إمكانية الوصول إلى Gateway/الخدمة، الوكلاء/الجلسات، إعدادات المزوّد + مشكلات وقت التشغيل (عندما يكون Gateway قابلاً للوصول).

2. **تقرير قابل للمشاركة بأمان**

   ```bash
   openclaw status --all
   ```

   تشخيص للقراءة فقط مع ذيل السجل (مع إخفاء الرموز المميّزة).

3. **حالة العملية الخلفية + المنفذ**

   ```bash
   openclaw gateway status
   ```

   يعرض حالة المشرف أثناء التشغيل مقابل إمكانية الوصول عبر RPC، وعنوان URL الهدف للفحص، وأي إعدادات يُرجّح أن الخدمة استخدمتها.

4. **فحوصات عميقة**

   ```bash
   openclaw status --deep
   ```

   يشغّل فحصًا مباشرًا لصحة Gateway، بما في ذلك فحوصات القنوات عند توفر الدعم
   (يتطلب Gateway قابلاً للوصول). راجع [الصحة](/ar/gateway/health).

5. **متابعة أحدث سجل**

   ```bash
   openclaw logs --follow
   ```

   إذا كان RPC متوقفًا، فاستخدم البديل التالي:

   ```bash
   tail -f "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)"
   ```

   سجلات الملفات منفصلة عن سجلات الخدمة؛ راجع [التسجيل](/ar/logging) و[استكشاف الأخطاء وإصلاحها](/ar/gateway/troubleshooting).

6. **تشغيل Doctor (الإصلاحات)**

   ```bash
   openclaw doctor
   ```

   يُصلح/يُرحّل الإعدادات والحالة + يشغّل فحوصات الصحة. راجع [Doctor](/ar/gateway/doctor).

7. **لقطة Gateway**

   ```bash
   openclaw health --json
   openclaw health --verbose   # يعرض عنوان URL الهدف + مسار الإعدادات عند حدوث أخطاء
   ```

   يطلب من Gateway العامل لقطة كاملة (عبر WS فقط). راجع [الصحة](/ar/gateway/health).

## البدء السريع وإعداد التشغيل الأول

<AccordionGroup>
  <Accordion title="أنا عالق، ما أسرع طريقة للخروج من المشكلة؟">
    استخدم وكيل AI محلي يمكنه **رؤية جهازك**. هذا أكثر فعالية بكثير من السؤال
    في Discord، لأن معظم حالات "أنا عالق" تكون **مشكلات محلية في الإعدادات أو البيئة**
    لا يمكن للمساعدين عن بُعد فحصها.

    - **Claude Code**: [https://www.anthropic.com/claude-code/](https://www.anthropic.com/claude-code/)
    - **OpenAI Codex**: [https://openai.com/codex/](https://openai.com/codex/)

    يمكن لهذه الأدوات قراءة المستودع وتشغيل الأوامر وفحص السجلات والمساعدة في إصلاح
    الإعداد على مستوى جهازك (PATH، الخدمات، الأذونات، ملفات المصادقة). امنحها
    **نسخة المصدر الكاملة** عبر التثبيت القابل للتعديل (git):

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    يثبّت هذا OpenClaw **من نسخة git محلية**، حتى يتمكن الوكيل من قراءة الشيفرة + المستندات
    والتعامل مع الإصدار الدقيق الذي تشغّله. ويمكنك دائمًا العودة إلى الإصدار المستقر لاحقًا
    عبر إعادة تشغيل أداة التثبيت بدون `--install-method git`.

    نصيحة: اطلب من الوكيل **تخطيط الإصلاح والإشراف عليه** (خطوة بخطوة)، ثم تنفيذ
    الأوامر الضرورية فقط. هذا يُبقي التغييرات صغيرة وأسهل للمراجعة.

    إذا اكتشفت خطأً فعليًا أو إصلاحًا، فيُرجى فتح GitHub issue أو إرسال PR:
    [https://github.com/openclaw/openclaw/issues](https://github.com/openclaw/openclaw/issues)
    [https://github.com/openclaw/openclaw/pulls](https://github.com/openclaw/openclaw/pulls)

    ابدأ بهذه الأوامر (وشارك المخرجات عند طلب المساعدة):

    ```bash
    openclaw status
    openclaw models status
    openclaw doctor
    ```

    ما الذي تفعله:

    - `openclaw status`: لقطة سريعة لصحة Gateway/الوكيل + الإعدادات الأساسية.
    - `openclaw models status`: يفحص مصادقة المزوّد + توفر النماذج.
    - `openclaw doctor`: يتحقق من مشكلات الإعدادات/الحالة الشائعة ويصلحها.

    فحوصات CLI المفيدة الأخرى: `openclaw status --all`، `openclaw logs --follow`،
    `openclaw gateway status`، `openclaw health --verbose`.

    حلقة التصحيح السريعة: [أول 60 ثانية إذا كان هناك شيء معطّل](#first-60-seconds-if-something-is-broken).
    مستندات التثبيت: [التثبيت](/ar/install)، [علامات أداة التثبيت](/ar/install/installer)، [التحديث](/ar/install/updating).

  </Accordion>

  <Accordion title="Heartbeat يستمر في التخطي. ماذا تعني أسباب التخطي؟">
    أسباب تخطي Heartbeat الشائعة:

    - `quiet-hours`: خارج نافذة الساعات النشطة المضبوطة
    - `empty-heartbeat-file`: ملف `HEARTBEAT.md` موجود لكنه يحتوي فقط على هيكل فارغ/عناوين فقط
    - `no-tasks-due`: وضع مهام `HEARTBEAT.md` نشط ولكن لم يحن موعد أي من فترات المهام بعد
    - `alerts-disabled`: تم تعطيل كل إظهار Heartbeat (`showOk` و`showAlerts` و`useIndicator` كلها معطلة)

    في وضع المهام، لا يتم تقديم الطوابع الزمنية المستحقة إلا بعد اكتمال
    تشغيل Heartbeat فعلي. ولا تُعلّم عمليات التشغيل المتخطاة المهام على أنها مكتملة.

    المستندات: [Heartbeat](/ar/gateway/heartbeat)، [الأتمتة والمهام](/ar/automation).

  </Accordion>

  <Accordion title="ما هي الطريقة الموصى بها لتثبيت OpenClaw وإعداده؟">
    يوصي المستودع بالتشغيل من المصدر واستخدام التهيئة الأولية:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash
    openclaw onboard --install-daemon
    ```

    يمكن للمعالج أيضًا بناء أصول واجهة المستخدم تلقائيًا. بعد التهيئة الأولية، عادةً ما تشغّل Gateway على المنفذ **18789**.

    من المصدر (للمساهمين/المطورين):

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    pnpm ui:build # يثبت تبعيات واجهة المستخدم تلقائيًا عند أول تشغيل
    openclaw onboard
    ```

    إذا لم يكن لديك تثبيت عام بعد، فشغّله عبر `pnpm openclaw onboard`.

  </Accordion>

  <Accordion title="كيف أفتح لوحة المعلومات بعد التهيئة الأولية؟">
    يفتح المعالج المتصفح لديك بعنوان URL نظيف للوحة المعلومات (من دون رموز مميّزة في العنوان) مباشرة بعد التهيئة الأولية، كما يطبع الرابط أيضًا في الملخص. أبقِ علامة التبويب تلك مفتوحة؛ وإذا لم تُفتح، فانسخ/ألصق عنوان URL المطبوع على الجهاز نفسه.
  </Accordion>

  <Accordion title="كيف أصادق على لوحة المعلومات على localhost مقابل الاتصال البعيد؟">
    **localhost (الجهاز نفسه):**

    - افتح `http://127.0.0.1:18789/`.
    - إذا طلبت مصادقة سر مشترك، فألصق الرمز المميّز أو كلمة المرور المضبوطة في إعدادات Control UI.
    - مصدر الرمز المميّز: `gateway.auth.token` (أو `OPENCLAW_GATEWAY_TOKEN`).
    - مصدر كلمة المرور: `gateway.auth.password` (أو `OPENCLAW_GATEWAY_PASSWORD`).
    - إذا لم يتم إعداد سر مشترك بعد، فأنشئ رمزًا مميّزًا باستخدام `openclaw doctor --generate-gateway-token`.

    **ليس على localhost:**

    - **Tailscale Serve** (مُوصى به): أبقِ الربط على loopback، وشغّل `openclaw gateway --tailscale serve`، ثم افتح `https://<magicdns>/`. إذا كانت `gateway.auth.allowTailscale` مضبوطة على `true`، فإن ترويسات الهوية تلبّي مصادقة Control UI/WebSocket (من دون لصق سر مشترك، مع افتراض موثوقية مضيف Gateway)؛ تظل HTTP APIs تتطلب مصادقة السر المشترك إلا إذا استخدمت عمدًا `none` للدخول الخاص أو مصادقة HTTP عبر trusted-proxy.
      تتم جدولة محاولات مصادقة Serve السيئة المتزامنة من العميل نفسه تسلسليًا قبل أن يسجل محدد المصادقة الفاشلة هذه المحاولات، لذا قد يظهر بالفعل في إعادة المحاولة السيئة الثانية `retry later`.
    - **ربط Tailnet**: شغّل `openclaw gateway --bind tailnet --token "<token>"` (أو اضبط مصادقة كلمة المرور)، وافتح `http://<tailscale-ip>:18789/`، ثم ألصق السر المشترك المطابق في إعدادات لوحة المعلومات.
    - **وكيل عكسي مدرك للهوية**: أبقِ Gateway خلف trusted-proxy غير مربوط بـ loopback، واضبط `gateway.auth.mode: "trusted-proxy"`، ثم افتح عنوان URL الخاص بالوكيل.
    - **نفق SSH**: `ssh -N -L 18789:127.0.0.1:18789 user@host` ثم افتح `http://127.0.0.1:18789/`. تظل مصادقة السر المشترك مطبقة عبر النفق؛ ألصق الرمز المميّز أو كلمة المرور المضبوطة إذا طُلب منك ذلك.

    راجع [لوحة المعلومات](/web/dashboard) و[أسطح الويب](/web) لمعرفة أوضاع الربط وتفاصيل المصادقة.

  </Accordion>

  <Accordion title="لماذا توجد إعداداتان للموافقة على exec في موافقات الدردشة؟">
    هما تتحكمان في طبقتين مختلفتين:

    - `approvals.exec`: يمرّر مطالبات الموافقة إلى وجهات الدردشة
    - `channels.<channel>.execApprovals`: يجعل تلك القناة تعمل كعميل موافقة أصلي لموافقات exec

    تظل سياسة exec على المضيف هي بوابة الموافقة الفعلية. تتحكم إعدادات الدردشة فقط في المكان
    الذي تظهر فيه مطالبات الموافقة وكيف يمكن للناس الرد عليها.

    في معظم البيئات **لا** تحتاج إلى كليهما:

    - إذا كانت الدردشة تدعم الأوامر والردود بالفعل، فإن `/approve` في الدردشة نفسها يعمل عبر المسار المشترك.
    - إذا كانت قناة أصلية مدعومة قادرة على استنتاج الموافقين بأمان، فإن OpenClaw يفعّل الآن تلقائيًا الموافقات الأصلية المعتمدة على الرسائل الخاصة أولًا عندما تكون `channels.<channel>.execApprovals.enabled` غير مضبوطة أو مضبوطة على `"auto"`.
    - عند توفر بطاقات/أزرار الموافقة الأصلية، تكون واجهة المستخدم الأصلية تلك هي المسار الأساسي؛ ويجب على الوكيل تضمين أمر `/approve` يدوي فقط إذا كانت نتيجة الأداة تشير إلى أن موافقات الدردشة غير متاحة أو أن الموافقة اليدوية هي المسار الوحيد.
    - استخدم `approvals.exec` فقط عندما يجب أيضًا تمرير المطالبات إلى دردشات أخرى أو غرف عمليات صريحة.
    - استخدم `channels.<channel>.execApprovals.target: "channel"` أو `"both"` فقط عندما تريد صراحةً نشر مطالبات الموافقة مرة أخرى في الغرفة/الموضوع الأصلي.
    - موافقات Plugin منفصلة أيضًا: فهي تستخدم `/approve` في الدردشة نفسها افتراضيًا، مع تمرير اختياري عبر `approvals.plugin`، ولا تحتفظ إلا بعض القنوات الأصلية بمعالجة أصلية إضافية لموافقات Plugin.

    باختصار: التمرير مخصص للتوجيه، أما إعدادات العميل الأصلي فهي مخصصة لتجربة مستخدم أغنى خاصة بالقناة.
    راجع [موافقات Exec](/ar/tools/exec-approvals).

  </Accordion>

  <Accordion title="ما هو وقت التشغيل الذي أحتاج إليه؟">
    Node **>= 22** مطلوب. يُوصى باستخدام `pnpm`. لا يُوصى باستخدام Bun مع Gateway.
  </Accordion>

  <Accordion title="هل يعمل على Raspberry Pi؟">
    نعم. Gateway خفيف - وتذكر المستندات أن **512MB-1GB RAM** و**نواة واحدة** ونحو **500MB**
    من مساحة القرص كافية للاستخدام الشخصي، كما تشير إلى أن **Raspberry Pi 4 يمكنه تشغيله**.

    إذا كنت تريد هامشًا إضافيًا (للسجلات، والوسائط، والخدمات الأخرى)، فإن **2GB موصى بها**، لكنها
    ليست حدًا أدنى صارمًا.

    نصيحة: يمكن لجهاز Pi/VPS صغير استضافة Gateway، ويمكنك إقران **Nodes** على الحاسوب المحمول/الهاتف من أجل
    الشاشة/الكاميرا/Canvas المحلية أو تنفيذ الأوامر. راجع [Nodes](/ar/nodes).

  </Accordion>

  <Accordion title="هل توجد نصائح لتثبيتات Raspberry Pi؟">
    باختصار: يعمل، لكن توقّع بعض الجوانب غير المصقولة.

    - استخدم نظام تشغيل **64-bit** وأبقِ Node >= 22.
    - فضّل **التثبيت القابل للتعديل (git)** حتى تتمكن من رؤية السجلات والتحديث بسرعة.
    - ابدأ من دون قنوات/Skills، ثم أضفها واحدة تلو الأخرى.
    - إذا واجهت مشكلات غريبة متعلقة بالملفات الثنائية، فعادةً ما تكون مشكلة **توافق ARM**.

    المستندات: [Linux](/ar/platforms/linux)، [التثبيت](/ar/install).

  </Accordion>

  <Accordion title="إنه عالق عند wake up my friend / والتهيئة الأولية لا تكتمل. ماذا الآن؟">
    تعتمد هذه الشاشة على أن يكون Gateway قابلاً للوصول ومصادَقًا عليه. كما يرسل TUI أيضًا
    "Wake up, my friend!" تلقائيًا عند أول اكتمال. إذا رأيت هذا السطر **من دون رد**
    وبقيت الرموز عند 0، فهذا يعني أن الوكيل لم يعمل مطلقًا.

    1. أعد تشغيل Gateway:

    ```bash
    openclaw gateway restart
    ```

    2. تحقق من الحالة + المصادقة:

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    3. إذا ظل عالقًا، فشغّل:

    ```bash
    openclaw doctor
    ```

    إذا كان Gateway بعيدًا، فتأكد من أن اتصال النفق/Tailscale يعمل وأن واجهة المستخدم
    موجّهة إلى Gateway الصحيح. راجع [الوصول البعيد](/ar/gateway/remote).

  </Accordion>

  <Accordion title="هل يمكنني نقل إعدادي إلى جهاز جديد (Mac mini) من دون إعادة التهيئة الأولية؟">
    نعم. انسخ **دليل الحالة** و**مساحة العمل**، ثم شغّل Doctor مرة واحدة. هذا
    يُبقي البوت "كما هو تمامًا" (الذاكرة، وسجل الجلسات، والمصادقة، وحالة القناة)
    ما دمت تنسخ **الموقعين** معًا:

    1. ثبّت OpenClaw على الجهاز الجديد.
    2. انسخ `$OPENCLAW_STATE_DIR` (الافتراضي: `~/.openclaw`) من الجهاز القديم.
    3. انسخ مساحة العمل الخاصة بك (الافتراضي: `~/.openclaw/workspace`).
    4. شغّل `openclaw doctor` وأعد تشغيل خدمة Gateway.

    هذا يحافظ على الإعدادات، وملفات تعريف المصادقة، وبيانات اعتماد WhatsApp، والجلسات، والذاكرة. إذا كنت تعمل في
    الوضع البعيد، فتذكر أن مضيف Gateway هو الذي يملك مخزن الجلسات ومساحة العمل.

    **مهم:** إذا كنت تكتفي فقط بعمل commit/push لمساحة العمل الخاصة بك إلى GitHub، فأنت تنشئ
    نسخة احتياطية من **الذاكرة + ملفات التمهيد**، لكن **ليس** من سجل الجلسات أو المصادقة. فهذه موجودة
    ضمن `~/.openclaw/` (على سبيل المثال `~/.openclaw/agents/<agentId>/sessions/`).

    ذو صلة: [الترحيل](/ar/install/migrating)، [أين توجد الأشياء على القرص](#where-things-live-on-disk)،
    [مساحة عمل الوكيل](/ar/concepts/agent-workspace)، [Doctor](/ar/gateway/doctor)،
    [الوضع البعيد](/ar/gateway/remote).

  </Accordion>

  <Accordion title="أين أرى ما الجديد في أحدث إصدار؟">
    راجع سجل التغييرات على GitHub:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    أحدث الإدخالات تكون في الأعلى. إذا كان القسم العلوي موسومًا بـ **Unreleased**، فالقسم التالي المؤرخ
    هو أحدث إصدار تم شحنه. تُجمع الإدخالات تحت **Highlights** و**Changes** و
    **Fixes** (بالإضافة إلى أقسام المستندات/الأقسام الأخرى عند الحاجة).

  </Accordion>

  <Accordion title="لا يمكن الوصول إلى docs.openclaw.ai (خطأ SSL)">
    تقوم بعض اتصالات Comcast/Xfinity بحظر `docs.openclaw.ai` بشكل غير صحيح عبر Xfinity
    Advanced Security. عطّلها أو أضف `docs.openclaw.ai` إلى قائمة السماح، ثم أعد المحاولة.
    نرجو مساعدتنا في رفع الحظر عنه بالإبلاغ هنا: [https://spa.xfinity.com/check_url_status](https://spa.xfinity.com/check_url_status).

    إذا كنت لا تزال غير قادر على الوصول إلى الموقع، فالمستندات لها نسخة مرآة على GitHub:
    [https://github.com/openclaw/openclaw/tree/main/docs](https://github.com/openclaw/openclaw/tree/main/docs)

  </Accordion>

  <Accordion title="الفرق بين stable وbeta">
    إن **Stable** و**beta** هما **npm dist-tags**، وليسا سطرَي شيفرة منفصلين:

    - `latest` = stable
    - `beta` = إصدار مبكر للاختبار

    عادةً، يصل الإصدار المستقر إلى **beta** أولًا، ثم تنقل خطوة
    ترقية صريحة الإصدار نفسه إلى `latest`. ويمكن للمشرفين أيضًا
    النشر مباشرة إلى `latest` عند الحاجة. ولهذا يمكن أن يشير beta وstable
    إلى **الإصدار نفسه** بعد الترقية.

    لمعرفة ما الذي تغيّر:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    لمعرفة أوامر التثبيت المختصرة والفرق بين beta وdev، راجع الأكورديون أدناه.

  </Accordion>

  <Accordion title="كيف أُثبّت إصدار beta وما الفرق بين beta وdev؟">
    **Beta** هو npm dist-tag `beta` (وقد يطابق `latest` بعد الترقية).
    أما **Dev** فهو الرأس المتحرك للفرع `main` (git)؛ وعند نشره، يستخدم npm dist-tag `dev`.

    أوامر مختصرة (macOS/Linux):

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --beta
    ```

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    أداة تثبيت Windows (PowerShell):
    [https://openclaw.ai/install.ps1](https://openclaw.ai/install.ps1)

    مزيد من التفاصيل: [قنوات التطوير](/ar/install/development-channels) و[علامات أداة التثبيت](/ar/install/installer).

  </Accordion>

  <Accordion title="كيف أجرّب أحدث الإصدارات؟">
    هناك خياران:

    1. **قناة Dev (نسخة git محلية):**

    ```bash
    openclaw update --channel dev
    ```

    يؤدي هذا إلى التبديل إلى الفرع `main` والتحديث من المصدر.

    2. **تثبيت قابل للتعديل (من موقع أداة التثبيت):**

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    يمنحك هذا مستودعًا محليًا يمكنك تعديله، ثم تحديثه عبر git.

    إذا كنت تفضّل استنساخًا نظيفًا يدويًا، فاستخدم:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    ```

    المستندات: [التحديث](/cli/update)، [قنوات التطوير](/ar/install/development-channels)،
    [التثبيت](/ar/install).

  </Accordion>

  <Accordion title="كم يستغرق التثبيت والتهيئة الأولية عادةً؟">
    دليل تقريبي:

    - **التثبيت:** من 2 إلى 5 دقائق
    - **التهيئة الأولية:** من 5 إلى 15 دقيقة حسب عدد القنوات/النماذج التي تقوم بإعدادها

    إذا بدا أنه عالق، فاستخدم [تعطلت أداة التثبيت؟](#quick-start-and-first-run-setup)
    وحلقة التصحيح السريعة في [أنا عالق](#quick-start-and-first-run-setup).

  </Accordion>

  <Accordion title="تعطلت أداة التثبيت؟ كيف أحصل على مزيد من المعلومات؟">
    أعد تشغيل أداة التثبيت مع **مخرجات تفصيلية**:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --verbose
    ```

    تثبيت Beta مع الوضع التفصيلي:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --beta --verbose
    ```

    لتثبيت قابل للتعديل (git):

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git --verbose
    ```

    المكافئ في Windows (PowerShell):

    ```powershell
    # لا يحتوي install.ps1 على علامة -Verbose مخصصة حتى الآن.
    Set-PSDebug -Trace 1
    & ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -NoOnboard
    Set-PSDebug -Trace 0
    ```

    مزيد من الخيارات: [علامات أداة التثبيت](/ar/install/installer).

  </Accordion>

  <Accordion title="يقول تثبيت Windows إن git غير موجود أو إن openclaw غير معروف">
    هناك مشكلتان شائعتان في Windows:

    **1) خطأ npm spawn git / git not found**

    - ثبّت **Git for Windows** وتأكد من أن `git` موجود على PATH.
    - أغلق PowerShell وأعد فتحه، ثم أعد تشغيل أداة التثبيت.

    **2) openclaw is not recognized after install**

    - مجلد npm global bin ليس موجودًا على PATH.
    - تحقّق من المسار:

      ```powershell
      npm config get prefix
      ```

    - أضف ذلك الدليل إلى PATH الخاص بالمستخدم (لا حاجة إلى اللاحقة `\bin` في Windows؛ وفي معظم الأنظمة يكون `%AppData%\npm`).
    - أغلق PowerShell وأعد فتحه بعد تحديث PATH.

    إذا كنت تريد إعداد Windows الأكثر سلاسة، فاستخدم **WSL2** بدلًا من Windows الأصلي.
    المستندات: [Windows](/ar/platforms/windows).

  </Accordion>

  <Accordion title="يعرض ناتج exec في Windows نصًا صينيًا مشوّهًا - ماذا ينبغي أن أفعل؟">
    يكون السبب عادةً عدم تطابق صفحة ترميز وحدة التحكم في أصداف Windows الأصلية.

    الأعراض:

    - ناتج `system.run`/`exec` يعرض النص الصيني بشكل مشوّه
    - الأمر نفسه يظهر بشكل صحيح في ملف تعريف طرفية آخر

    حل سريع مؤقت في PowerShell:

    ```powershell
    chcp 65001
    [Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    ```

    ثم أعد تشغيل Gateway وأعد محاولة تنفيذ الأمر:

    ```powershell
    openclaw gateway restart
    ```

    إذا استمرت المشكلة على أحدث إصدار من OpenClaw، فتابعها/أبلغ عنها هنا:

    - [Issue #30640](https://github.com/openclaw/openclaw/issues/30640)

  </Accordion>

  <Accordion title="لم تُجب المستندات عن سؤالي - كيف أحصل على إجابة أفضل؟">
    استخدم **التثبيت القابل للتعديل (git)** حتى تحصل على المصدر الكامل والمستندات محليًا، ثم اسأل
    البوت الخاص بك (أو Claude/Codex) _من داخل ذلك المجلد_ حتى يتمكن من قراءة المستودع والإجابة بدقة.

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    مزيد من التفاصيل: [التثبيت](/ar/install) و[علامات أداة التثبيت](/ar/install/installer).

  </Accordion>

  <Accordion title="كيف أُثبّت OpenClaw على Linux؟">
    الإجابة القصيرة: اتبع دليل Linux، ثم شغّل التهيئة الأولية.

    - المسار السريع لـ Linux + تثبيت الخدمة: [Linux](/ar/platforms/linux).
    - الشرح الكامل: [البدء](/ar/start/getting-started).
    - أداة التثبيت + التحديثات: [التثبيت والتحديثات](/ar/install/updating).

  </Accordion>

  <Accordion title="كيف أُثبّت OpenClaw على VPS؟">
    أي VPS يعمل بنظام Linux مناسب. ثبّت البرنامج على الخادم، ثم استخدم SSH/Tailscale للوصول إلى Gateway.

    الأدلة: [exe.dev](/ar/install/exe-dev)، [Hetzner](/ar/install/hetzner)، [Fly.io](/ar/install/fly).
    الوصول البعيد: [Gateway remote](/ar/gateway/remote).

  </Accordion>

  <Accordion title="أين توجد أدلة التثبيت على السحابة/VPS؟">
    لدينا **مركز استضافة** يضم مزودي الخدمة الشائعين. اختر واحدًا واتبع الدليل:

    - [استضافة VPS](/ar/vps) (كل المزوّدين في مكان واحد)
    - [Fly.io](/ar/install/fly)
    - [Hetzner](/ar/install/hetzner)
    - [exe.dev](/ar/install/exe-dev)

    طريقة العمل على السحابة: يتم تشغيل **Gateway على الخادم**، وتصل إليه
    من حاسوبك المحمول/هاتفك عبر Control UI (أو Tailscale/SSH). وتعيش حالتك + مساحة العمل
    على الخادم، لذا تعامل مع المضيف على أنه مصدر الحقيقة وقم بعمل نسخ احتياطي له.

    يمكنك إقران **Nodes** (Mac/iOS/Android/headless) مع Gateway السحابي هذا للوصول إلى
    الشاشة/الكاميرا/Canvas المحلية أو تشغيل الأوامر على حاسوبك المحمول مع الإبقاء على
    Gateway في السحابة.

    المركز: [المنصات](/ar/platforms). الوصول البعيد: [Gateway remote](/ar/gateway/remote).
    Nodes: [Nodes](/ar/nodes)، [Nodes CLI](/cli/nodes).

  </Accordion>

  <Accordion title="هل يمكنني أن أطلب من OpenClaw أن يحدّث نفسه؟">
    الإجابة القصيرة: **ممكن، لكنه غير مُوصى به**. قد تؤدي عملية التحديث إلى إعادة تشغيل
    Gateway (مما يُسقط الجلسة النشطة)، وقد تحتاج إلى نسخة git نظيفة، كما
    قد تطلب تأكيدًا. والأكثر أمانًا هو تشغيل التحديثات من سطر الأوامر بصفتك المشغّل.

    استخدم CLI:

    ```bash
    openclaw update
    openclaw update status
    openclaw update --channel stable|beta|dev
    openclaw update --tag <dist-tag|version>
    openclaw update --no-restart
    ```

    إذا كان لا بد من أتمتة ذلك من وكيل:

    ```bash
    openclaw update --yes --no-restart
    openclaw gateway restart
    ```

    المستندات: [التحديث](/cli/update)، [التحديث](/ar/install/updating).

  </Accordion>

  <Accordion title="ماذا تفعل التهيئة الأولية فعليًا؟">
    `openclaw onboard` هو مسار الإعداد الموصى به. في **الوضع المحلي** يأخذك عبر:

    - **إعداد النموذج/المصادقة** (OAuth للمزوّد، ومفاتيح API، وsetup-token الخاصة بـ Anthropic، بالإضافة إلى خيارات النماذج المحلية مثل LM Studio)
    - موقع **مساحة العمل** + ملفات التمهيد
    - **إعدادات Gateway** (الربط/المنفذ/المصادقة/Tailscale)
    - **القنوات** (WhatsApp، وTelegram، وDiscord، وMattermost، وSignal، وiMessage، بالإضافة إلى Plugin قنوات مضمّنة مثل QQ Bot)
    - **تثبيت العملية الخلفية** (LaunchAgent على macOS؛ ووحدة مستخدم systemd على Linux/WSL2)
    - **فحوصات الصحة** واختيار **Skills**

    كما أنه يحذّر أيضًا إذا كان النموذج الذي قمت بإعداده غير معروف أو تنقصه المصادقة.

  </Accordion>

  <Accordion title="هل أحتاج إلى اشتراك Claude أو OpenAI لتشغيل هذا؟">
    لا. يمكنك تشغيل OpenClaw باستخدام **مفاتيح API** (Anthropic/OpenAI/وغيرها) أو باستخدام
    **نماذج محلية فقط** حتى تبقى بياناتك على جهازك. الاشتراكات (Claude
    Pro/Max أو OpenAI Codex) هي طرق اختيارية لمصادقة هؤلاء المزوّدين.

    بالنسبة إلى Anthropic في OpenClaw، فالتقسيم العملي هو:

    - **مفتاح Anthropic API**: فوترة عادية لـ Anthropic API
    - **مصادقة Claude CLI / اشتراك Claude داخل OpenClaw**: أخبرنا موظفو Anthropic
      أن هذا الاستخدام مسموح به مرة أخرى، ويتعامل OpenClaw مع استخدام `claude -p`
      على أنه معتمد لهذا التكامل ما لم تنشر Anthropic سياسة جديدة

    بالنسبة إلى مضيفي Gateway طويلة الأمد، تظل مفاتيح Anthropic API هي
    الإعداد الأكثر قابلية للتنبؤ. كما أن OpenAI Codex OAuth مدعوم صراحةً للأدوات
    الخارجية مثل OpenClaw.

    يدعم OpenClaw أيضًا خيارات أخرى مستضافة على نمط الاشتراك، بما في ذلك
    **Qwen Cloud Coding Plan**، و**MiniMax Coding Plan**، و
    **Z.AI / GLM Coding Plan**.

    المستندات: [Anthropic](/ar/providers/anthropic)، [OpenAI](/ar/providers/openai)،
    [Qwen Cloud](/ar/providers/qwen)،
    [MiniMax](/ar/providers/minimax)، [GLM Models](/ar/providers/glm)،
    [النماذج المحلية](/ar/gateway/local-models)، [النماذج](/ar/concepts/models).

  </Accordion>

  <Accordion title="هل يمكنني استخدام اشتراك Claude Max من دون مفتاح API؟">
    نعم.

    أخبرنا موظفو Anthropic أن استخدام Claude CLI بأسلوب OpenClaw مسموح به مرة أخرى، لذلك
    يتعامل OpenClaw مع مصادقة اشتراك Claude واستخدام `claude -p` على أنهما معتمدان
    لهذا التكامل ما لم تنشر Anthropic سياسة جديدة. وإذا كنت تريد
    أكثر إعدادات جانب الخادم قابلية للتنبؤ، فاستخدم مفتاح Anthropic API بدلًا من ذلك.

  </Accordion>

  <Accordion title="هل تدعمون مصادقة اشتراك Claude (Claude Pro أو Max)؟">
    نعم.

    أخبرنا موظفو Anthropic أن هذا الاستخدام مسموح به مرة أخرى، لذلك يتعامل OpenClaw مع
    إعادة استخدام Claude CLI واستخدام `claude -p` على أنهما معتمدان لهذا التكامل
    ما لم تنشر Anthropic سياسة جديدة.

    لا يزال Anthropic setup-token متاحًا كمسار رمز مدعوم في OpenClaw، لكن OpenClaw يفضّل الآن إعادة استخدام Claude CLI و`claude -p` عند توفرهما.
    أما لأعباء العمل الإنتاجية أو متعددة المستخدمين، فما تزال مصادقة مفتاح Anthropic API هي
    الخيار الأكثر أمانًا وقابلية للتنبؤ. وإذا كنت تريد خيارات أخرى مستضافة
    على نمط الاشتراك في OpenClaw، فراجع [OpenAI](/ar/providers/openai)، و[Qwen / Model
    Cloud](/ar/providers/qwen)، و[MiniMax](/ar/providers/minimax)، و[GLM
    Models](/ar/providers/glm).

  </Accordion>

<a id="why-am-i-seeing-http-429-ratelimiterror-from-anthropic"></a>
<Accordion title="لماذا أرى HTTP 429 rate_limit_error من Anthropic؟">
هذا يعني أن **الحصة/حد المعدل الخاص بـ Anthropic** قد استُنفد في النافذة الحالية. إذا كنت
تستخدم **Claude CLI**، فانتظر حتى تُعاد تهيئة النافذة أو قم بترقية خطتك. وإذا كنت
تستخدم **مفتاح Anthropic API**، فتحقق من Anthropic Console
من الاستخدام/الفوترة وارفع الحدود عند الحاجة.

    إذا كانت الرسالة تحديدًا:
    `Extra usage is required for long context requests`، فهذا يعني أن الطلب يحاول استخدام
    الإصدار التجريبي 1M context من Anthropic (`context1m: true`). ولا يعمل ذلك إلا عندما تكون
    بيانات الاعتماد الخاصة بك مؤهلة لفوترة السياق الطويل (فوترة مفتاح API أو
    مسار Claude-login الخاص بـ OpenClaw مع تمكين Extra Usage).

    نصيحة: اضبط **fallback model** حتى يتمكن OpenClaw من الاستمرار في الرد عندما يكون أحد المزوّدين مقيّدًا بالمعدل.
    راجع [Models](/cli/models)، و[OAuth](/ar/concepts/oauth)، و
    [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/ar/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context).

  </Accordion>

  <Accordion title="هل AWS Bedrock مدعوم؟">
    نعم. يحتوي OpenClaw على مزوّد **Amazon Bedrock (Converse)** مضمّن. عند وجود مؤشرات بيئة AWS، يمكن لـ OpenClaw اكتشاف كتالوج Bedrock للبث/النص تلقائيًا ودمجه كمزوّد ضمني `amazon-bedrock`؛ وإلا يمكنك تمكين `plugins.entries.amazon-bedrock.config.discovery.enabled` صراحةً أو إضافة إدخال مزوّد يدوي. راجع [Amazon Bedrock](/ar/providers/bedrock) و[مزوّدو النماذج](/ar/providers/models). وإذا كنت تفضّل تدفق مفاتيح مُدارًا، فإن وكيلًا متوافقًا مع OpenAI أمام Bedrock يظل خيارًا صالحًا.
  </Accordion>

  <Accordion title="كيف تعمل مصادقة Codex؟">
    يدعم OpenClaw **OpenAI Code (Codex)** عبر OAuth (تسجيل دخول ChatGPT). يمكن للتهيئة الأولية تشغيل تدفق OAuth وستضبط النموذج الافتراضي على `openai-codex/gpt-5.4` عند الاقتضاء. راجع [مزوّدو النماذج](/ar/concepts/model-providers) و[التهيئة الأولية (CLI)](/ar/start/wizard).
  </Accordion>

  <Accordion title="لماذا لا يؤدي ChatGPT GPT-5.4 إلى فتح openai/gpt-5.4 في OpenClaw؟">
    يتعامل OpenClaw مع المسارين بشكل منفصل:

    - `openai-codex/gpt-5.4` = OAuth الخاص بـ ChatGPT/Codex
    - `openai/gpt-5.4` = OpenAI Platform API المباشر

    في OpenClaw، يتم توصيل تسجيل دخول ChatGPT/Codex بالمسار `openai-codex/*`،
    وليس بالمسار المباشر `openai/*`. إذا كنت تريد مسار API المباشر في
    OpenClaw، فاضبط `OPENAI_API_KEY` (أو إعداد مزوّد OpenAI المكافئ).
    وإذا كنت تريد تسجيل دخول ChatGPT/Codex في OpenClaw، فاستخدم `openai-codex/*`.

  </Accordion>

  <Accordion title="لماذا قد تختلف حدود Codex OAuth عن ChatGPT web؟">
    يستخدم `openai-codex/*` مسار Codex OAuth، ونوافذ الحصة القابلة للاستخدام فيه
    تُدار من OpenAI وتعتمد على الخطة. وعمليًا، قد تختلف هذه الحدود عن
    تجربة موقع/تطبيق ChatGPT، حتى عندما يكون كلاهما مرتبطًا بالحساب نفسه.

    يمكن لـ OpenClaw عرض نوافذ الاستخدام/الحصة المرئية حاليًا للمزوّد في
    `openclaw models status`، لكنه لا يخترع ولا يوحّد
    استحقاقات ChatGPT web لتصبح وصولًا مباشرًا إلى API. وإذا كنت تريد مسار
    الفوترة/الحدود المباشر في OpenAI Platform، فاستخدم `openai/*` مع مفتاح API.

  </Accordion>

  <Accordion title="هل تدعمون مصادقة اشتراك OpenAI (Codex OAuth)؟">
    نعم. يدعم OpenClaw بالكامل **OpenAI Code (Codex) subscription OAuth**.
    تسمح OpenAI صراحةً باستخدام subscription OAuth في الأدوات/سير العمل الخارجية
    مثل OpenClaw. ويمكن للتهيئة الأولية تشغيل تدفق OAuth نيابةً عنك.

    راجع [OAuth](/ar/concepts/oauth)، و[مزوّدو النماذج](/ar/concepts/model-providers)، و[التهيئة الأولية (CLI)](/ar/start/wizard).

  </Accordion>

  <Accordion title="كيف أُعد Gemini CLI OAuth؟">
    يستخدم Gemini CLI **تدفق مصادقة Plugin**، وليس client id أو secret داخل `openclaw.json`.

    الخطوات:

    1. ثبّت Gemini CLI محليًا حتى يكون `gemini` موجودًا على `PATH`
       - Homebrew: `brew install gemini-cli`
       - npm: `npm install -g @google/gemini-cli`
    2. فعّل Plugin: `openclaw plugins enable google`
    3. سجّل الدخول: `openclaw models auth login --provider google-gemini-cli --set-default`
    4. النموذج الافتراضي بعد تسجيل الدخول: `google-gemini-cli/gemini-3-flash-preview`
    5. إذا فشلت الطلبات، فاضبط `GOOGLE_CLOUD_PROJECT` أو `GOOGLE_CLOUD_PROJECT_ID` على مضيف Gateway

    يخزّن هذا رموز OAuth في ملفات تعريف المصادقة على مضيف Gateway. التفاصيل: [مزوّدو النماذج](/ar/concepts/model-providers).

  </Accordion>

  <Accordion title="هل النموذج المحلي مناسب للمحادثات العادية؟">
    غالبًا لا. يحتاج OpenClaw إلى سياق كبير + أمان قوي؛ فالبطاقات الصغيرة تقوم بالاقتطاع والتسريب. وإذا كان لا بد من ذلك، فشغّل **أكبر** بنية نموذج يمكنك تشغيلها محليًا (LM Studio) وراجع [/gateway/local-models](/ar/gateway/local-models). تزيد النماذج الأصغر/المكمّمة من خطر حقن المطالبات - راجع [الأمان](/ar/gateway/security).
  </Accordion>

  <Accordion title="كيف أحافظ على حركة مرور النماذج المستضافة داخل منطقة محددة؟">
    اختر نقاط نهاية مثبتة على منطقة محددة. يوفّر OpenRouter خيارات مستضافة في الولايات المتحدة لـ MiniMax وKimi وGLM؛ اختر النسخة المستضافة في الولايات المتحدة لإبقاء البيانات داخل المنطقة. ولا يزال بإمكانك إدراج Anthropic/OpenAI إلى جانب هذه الخيارات باستخدام `models.mode: "merge"` حتى تظل fallback متاحة مع احترام المزوّد المحدد حسب المنطقة الذي تختاره.
  </Accordion>

  <Accordion title="هل يجب أن أشتري Mac Mini لتثبيت هذا؟">
    لا. يعمل OpenClaw على macOS أو Linux (وعلى Windows عبر WSL2). ويُعد Mac mini اختياريًا - فبعض الأشخاص
    يشترونه كمضيف يعمل دائمًا، لكن VPS صغير أو خادم منزلي أو جهاز من فئة Raspberry Pi يعمل أيضًا.

    أنت تحتاج إلى Mac **فقط لأدوات macOS-only**. وبالنسبة إلى iMessage، استخدم [BlueBubbles](/ar/channels/bluebubbles) (مُوصى به) - إذ يعمل خادم BlueBubbles على أي Mac، بينما يمكن أن يعمل Gateway على Linux أو في أي مكان آخر. وإذا كنت تريد أدوات أخرى خاصة بـ macOS، فشغّل Gateway على جهاز Mac أو قم بإقران Node يعمل بنظام macOS.

    المستندات: [BlueBubbles](/ar/channels/bluebubbles)، [Nodes](/ar/nodes)، [Mac remote mode](/ar/platforms/mac/remote).

  </Accordion>

  <Accordion title="هل أحتاج إلى Mac mini لدعم iMessage؟">
    تحتاج إلى **جهاز macOS ما** مسجّل الدخول إلى Messages. ولا **يشترط** أن يكون Mac mini -
    فأي Mac يكفي. **استخدم [BlueBubbles](/ar/channels/bluebubbles)** (مُوصى به) مع iMessage - إذ يعمل خادم BlueBubbles على macOS، بينما يمكن أن يعمل Gateway على Linux أو في أي مكان آخر.

    الإعدادات الشائعة:

    - شغّل Gateway على Linux/VPS، وشغّل خادم BlueBubbles على أي Mac مسجّل الدخول إلى Messages.
    - شغّل كل شيء على جهاز Mac إذا كنت تريد أبسط إعداد أحادي الجهاز.

    المستندات: [BlueBubbles](/ar/channels/bluebubbles)، [Nodes](/ar/nodes)،
    [Mac remote mode](/ar/platforms/mac/remote).

  </Accordion>

  <Accordion title="إذا اشتريت Mac mini لتشغيل OpenClaw، فهل يمكنني توصيله بـ MacBook Pro الخاص بي؟">
    نعم. يمكن لـ **Mac mini تشغيل Gateway**، ويمكن لـ MacBook Pro الاتصال كـ
    **Node** (جهاز مرافق). لا تقوم Nodes بتشغيل Gateway - بل توفّر
    إمكانات إضافية مثل الشاشة/الكاميرا/Canvas و`system.run` على ذلك الجهاز.

    النمط الشائع:

    - Gateway على Mac mini (يعمل دائمًا).
    - يشغّل MacBook Pro تطبيق macOS أو مضيف Node ويقترن مع Gateway.
    - استخدم `openclaw nodes status` / `openclaw nodes list` لرؤيته.

    المستندات: [Nodes](/ar/nodes)، [Nodes CLI](/cli/nodes).

  </Accordion>

  <Accordion title="هل يمكنني استخدام Bun؟">
    استخدام Bun **غير مُوصى به**. نرى أخطاء وقت تشغيل، خصوصًا مع WhatsApp وTelegram.
    استخدم **Node** للحصول على Gateways مستقرة.

    وإذا كنت لا تزال تريد التجربة باستخدام Bun، فافعل ذلك على Gateway غير إنتاجية
    من دون WhatsApp/Telegram.

  </Accordion>

  <Accordion title="Telegram: ماذا يوضع في allowFrom؟">
    إن `channels.telegram.allowFrom` هو **Telegram user ID الخاص بالمرسل البشري** (رقمي). وليس اسم مستخدم البوت.

    تقبل التهيئة الأولية إدخال `@username` وتحوّله إلى معرّف رقمي، لكن تفويض OpenClaw يستخدم المعرّفات الرقمية فقط.

    الأكثر أمانًا (من دون بوت تابع لجهة خارجية):

    - أرسل رسالة خاصة إلى البوت، ثم شغّل `openclaw logs --follow` واقرأ `from.id`.

    Bot API الرسمي:

    - أرسل رسالة خاصة إلى البوت، ثم استدعِ `https://api.telegram.org/bot<bot_token>/getUpdates` واقرأ `message.from.id`.

    طرف ثالث (خصوصية أقل):

    - أرسل رسالة خاصة إلى `@userinfobot` أو `@getidsbot`.

    راجع [/channels/telegram](/ar/channels/telegram#access-control-and-activation).

  </Accordion>

  <Accordion title="هل يمكن لعدة أشخاص استخدام رقم WhatsApp واحد مع مثيلات OpenClaw مختلفة؟">
    نعم، عبر **توجيه الوكلاء المتعددين**. اربط **DM** الخاص بـ WhatsApp لكل مرسل (نظير `kind: "direct"`، مع رقم E.164 للمرسل مثل `+15551234567`) بـ `agentId` مختلف، حتى يحصل كل شخص على مساحة العمل ومخزن الجلسات الخاصين به. وستظل الردود صادرة من **حساب WhatsApp نفسه**، كما أن التحكم في الوصول إلى DM (`channels.whatsapp.dmPolicy` / `channels.whatsapp.allowFrom`) عام على مستوى حساب WhatsApp بأكمله. راجع [توجيه الوكلاء المتعددين](/ar/concepts/multi-agent) و[WhatsApp](/ar/channels/whatsapp).
  </Accordion>

  <Accordion title='هل يمكنني تشغيل وكيل "دردشة سريعة" ووكيل "Opus للبرمجة"؟'>
    نعم. استخدم توجيه الوكلاء المتعددين: امنح كل وكيل نموذجه الافتراضي الخاص، ثم اربط المسارات الواردة (حساب المزوّد أو نظراء محددون) بكل وكيل. يوجد مثال للإعدادات في [توجيه الوكلاء المتعددين](/ar/concepts/multi-agent). راجع أيضًا [النماذج](/ar/concepts/models) و[الإعدادات](/ar/gateway/configuration).
  </Accordion>

  <Accordion title="هل يعمل Homebrew على Linux؟">
    نعم. يدعم Homebrew نظام Linux (Linuxbrew). إعداد سريع:

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew install <formula>
    ```

    إذا كنت تشغّل OpenClaw عبر systemd، فتأكد من أن PATH الخاص بالخدمة يتضمن `/home/linuxbrew/.linuxbrew/bin` (أو بادئة brew الخاصة بك) حتى يتم العثور على الأدوات المثبتة بواسطة `brew` في الأصداف غير التفاعلية.
    كما أن البُنى الحديثة تضيف مسبقًا أدلة bin الشائعة للمستخدم على خدمات Linux systemd (على سبيل المثال `~/.local/bin` و`~/.npm-global/bin` و`~/.local/share/pnpm` و`~/.bun/bin`) وتحترم `PNPM_HOME` و`NPM_CONFIG_PREFIX` و`BUN_INSTALL` و`VOLTA_HOME` و`ASDF_DATA_DIR` و`NVM_DIR` و`FNM_DIR` عند ضبطها.

  </Accordion>

  <Accordion title="ما الفرق بين التثبيت القابل للتعديل عبر git وnpm install؟">
    - **التثبيت القابل للتعديل (git):** نسخة مصدر كاملة، قابلة للتعديل، وهي الأفضل للمساهمين.
      تقوم أنت بتشغيل البُنى محليًا ويمكنك تعديل الشيفرة/المستندات.
    - **npm install:** تثبيت CLI عام، من دون مستودع، وهو الأفضل لمن يريد "فقط تشغيله".
      تأتي التحديثات من npm dist-tags.

    المستندات: [البدء](/ar/start/getting-started)، [التحديث](/ar/install/updating).

  </Accordion>

  <Accordion title="هل يمكنني التبديل لاحقًا بين تثبيتات npm وgit؟">
    نعم. ثبّت النسخة الأخرى، ثم شغّل Doctor حتى تشير خدمة Gateway إلى نقطة الدخول الجديدة.
    هذا **لا يحذف بياناتك** - بل يغيّر فقط تثبيت شيفرة OpenClaw. وتبقى حالتك
    (`~/.openclaw`) ومساحة عملك (`~/.openclaw/workspace`) كما هي من دون تغيير.

    من npm إلى git:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    openclaw doctor
    openclaw gateway restart
    ```

    من git إلى npm:

    ```bash
    npm install -g openclaw@latest
    openclaw doctor
    openclaw gateway restart
    ```

    يكتشف Doctor عدم تطابق نقطة دخول خدمة Gateway ويعرض إعادة كتابة إعدادات الخدمة لتتوافق مع التثبيت الحالي (استخدم `--repair` في الأتمتة).

    نصائح النسخ الاحتياطي: راجع [استراتيجية النسخ الاحتياطي](#where-things-live-on-disk).

  </Accordion>

  <Accordion title="هل ينبغي أن أشغّل Gateway على حاسوبي المحمول أم على VPS؟">
    الإجابة المختصرة: **إذا كنت تريد موثوقية على مدار الساعة، فاستخدم VPS**. وإذا كنت تريد
    أقل قدر من الاحتكاك وكنت موافقًا على السكون/إعادة التشغيل، فشغّله محليًا.

    **الحاسوب المحمول (Gateway محلي)**

    - **الإيجابيات:** لا توجد تكلفة خادم، وصول مباشر إلى الملفات المحلية، نافذة متصفح مرئية مباشرة.
    - **السلبيات:** السكون/انقطاع الشبكة = انقطاعات، تحديثات/إعادات تشغيل نظام التشغيل تقاطع العمل، ويجب أن يبقى الجهاز مستيقظًا.

    **VPS / السحابة**

    - **الإيجابيات:** يعمل دائمًا، شبكة مستقرة، لا توجد مشكلات سكون الحاسوب المحمول، وأسهل في الإبقاء عليه قيد التشغيل.
    - **السلبيات:** غالبًا يعمل بدون واجهة مرئية (استخدم لقطات الشاشة)، وصول إلى الملفات عن بُعد فقط، ويجب أن تستخدم SSH لإجراء التحديثات.

    **ملاحظة خاصة بـ OpenClaw:** تعمل WhatsApp/Telegram/Slack/Mattermost/Discord كلها جيدًا من VPS. والمقايضة الحقيقية الوحيدة هي **متصفح بدون واجهة مرئية** مقابل نافذة ظاهرة. راجع [Browser](/ar/tools/browser).

    **الافتراضي الموصى به:** VPS إذا كنت قد واجهت سابقًا انقطاعات في Gateway. والتشغيل المحلي ممتاز عندما تكون تستخدم جهاز Mac بنشاط وتريد الوصول إلى الملفات المحلية أو أتمتة واجهة المستخدم عبر متصفح مرئي.

  </Accordion>

  <Accordion title="ما مدى أهمية تشغيل OpenClaw على جهاز مخصص؟">
    ليس مطلوبًا، لكنه **موصى به من أجل الموثوقية والعزل**.

    - **مضيف مخصص (VPS/Mac mini/Pi):** يعمل دائمًا، مع انقطاعات أقل بسبب السكون/إعادة التشغيل، وأذونات أنظف، وأسهل في الإبقاء عليه قيد التشغيل.
    - **حاسوب محمول/مكتبي مشترك:** مناسب تمامًا للاختبار والاستخدام النشط، لكن توقّع توقفات عندما يدخل الجهاز في السكون أو يتلقى تحديثات.

    إذا كنت تريد أفضل ما في العالمين، فأبقِ Gateway على مضيف مخصص، وأقرن حاسوبك المحمول كـ **Node** لأدوات الشاشة/الكاميرا/exec المحلية. راجع [Nodes](/ar/nodes).
    ولإرشادات الأمان، اقرأ [الأمان](/ar/gateway/security).

  </Accordion>

  <Accordion title="ما الحد الأدنى لمتطلبات VPS ونظام التشغيل الموصى به؟">
    OpenClaw خفيف. بالنسبة إلى Gateway أساسي + قناة دردشة واحدة:

    - **الحد الأدنى المطلق:** 1 vCPU، و1GB RAM، وحوالي 500MB من مساحة القرص.
    - **الموصى به:** 1-2 vCPU، و2GB RAM أو أكثر كهامش إضافي (للسجلات، والوسائط، والقنوات المتعددة). قد تكون أدوات Node وأتمتة المتصفح شرهة للموارد.

    نظام التشغيل: استخدم **Ubuntu LTS** (أو أي Debian/Ubuntu حديث). فهذا هو مسار التثبيت الأفضل اختبارًا على Linux.

    المستندات: [Linux](/ar/platforms/linux)، [استضافة VPS](/ar/vps).

  </Accordion>

  <Accordion title="هل يمكنني تشغيل OpenClaw داخل VM وما المتطلبات؟">
    نعم. تعامل مع VM بالطريقة نفسها التي تتعامل بها مع VPS: يجب أن يكون يعمل دائمًا، وقابلًا للوصول، ولديه
    ذاكرة RAM كافية لـ Gateway وأي قنوات تقوم بتمكينها.

    إرشادات أساسية:

    - **الحد الأدنى المطلق:** 1 vCPU، و1GB RAM.
    - **الموصى به:** 2GB RAM أو أكثر إذا كنت تشغّل عدة قنوات، أو أتمتة متصفح، أو أدوات وسائط.
    - **نظام التشغيل:** Ubuntu LTS أو أي Debian/Ubuntu حديث آخر.

    إذا كنت تستخدم Windows، فإن **WSL2 هو أسهل إعداد على نمط VM** ويتمتع بأفضل
    توافق مع الأدوات. راجع [Windows](/ar/platforms/windows)، [استضافة VPS](/ar/vps).
    وإذا كنت تشغّل macOS داخل VM، فراجع [macOS VM](/ar/install/macos-vm).

  </Accordion>
</AccordionGroup>

## ما هو OpenClaw؟

<AccordionGroup>
  <Accordion title="ما هو OpenClaw، في فقرة واحدة؟">
    OpenClaw هو مساعد AI شخصي تقوم بتشغيله على أجهزتك الخاصة. يرد على أسطح المراسلة التي تستخدمها بالفعل (WhatsApp وTelegram وSlack وMattermost وDiscord وGoogle Chat وSignal وiMessage وWebChat، بالإضافة إلى Plugin قنوات مضمّنة مثل QQ Bot)، ويمكنه أيضًا تنفيذ الصوت + Canvas مباشر على المنصات المدعومة. إن **Gateway** هو مستوى التحكم الذي يعمل دائمًا؛ أما المساعد فهو المنتج.
  </Accordion>

  <Accordion title="القيمة المقترحة">
    OpenClaw ليس "مجرد غلاف لـ Claude". بل هو **مستوى تحكم محلي أولًا** يتيح لك تشغيل مساعد
    قوي على **أجهزتك الخاصة**، ويمكن الوصول إليه من تطبيقات الدردشة التي تستخدمها بالفعل، مع
    جلسات حالية، وذاكرة، وأدوات - من دون تسليم التحكم في سير عملك إلى
    SaaS مستضاف.

    أبرز النقاط:

    - **أجهزتك، بياناتك:** شغّل Gateway أينما تريد (Mac أو Linux أو VPS) واحتفظ
      بمساحة العمل + سجل الجلسات محليًا.
    - **قنوات حقيقية، لا صندوق رمل ويب:** WhatsApp/Telegram/Slack/Discord/Signal/iMessage/etc،
      بالإضافة إلى الصوت على الهاتف المحمول وCanvas على المنصات المدعومة.
    - **غير مرتبط بمزوّد نموذج واحد:** استخدم Anthropic وOpenAI وMiniMax وOpenRouter وغيرها، مع توجيه
      لكل وكيل وآليات failover.
    - **خيار محلي فقط:** شغّل نماذج محلية حتى **تتمكن من إبقاء جميع البيانات على جهازك** إذا أردت.
    - **توجيه الوكلاء المتعددين:** وكلاء منفصلون لكل قناة أو حساب أو مهمة، ولكل منهم
      مساحة عمله وافتراضياته الخاصة.
    - **مفتوح المصدر وقابل للتعديل:** افحصه، ووسّعه، واستضفه بنفسك من دون ارتهان لمزوّد.

    المستندات: [Gateway](/ar/gateway)، [القنوات](/ar/channels)، [الوكلاء المتعددون](/ar/concepts/multi-agent)،
    [الذاكرة](/ar/concepts/memory).

  </Accordion>

  <Accordion title="لقد أعددته للتو - ماذا ينبغي أن أفعل أولًا؟">
    مشاريع أولى جيدة:

    - بناء موقع ويب (WordPress أو Shopify أو موقع ثابت بسيط).
    - إنشاء نموذج أولي لتطبيق جوال (مخطط، شاشات، خطة API).
    - تنظيم الملفات والمجلدات (تنظيف، تسمية، وسم).
    - ربط Gmail وأتمتة الملخصات أو المتابعات.

    يمكنه التعامل مع المهام الكبيرة، لكنه يعمل بأفضل صورة عندما تقسّمها إلى مراحل
    وتستخدم وكلاء فرعيين للعمل المتوازي.

  </Accordion>

  <Accordion title="ما أبرز خمس حالات استخدام يومية لـ OpenClaw؟">
    تبدو المكاسب اليومية عادةً على هذا النحو:

    - **إحاطات شخصية:** ملخصات للبريد الوارد، والتقويم، والأخبار التي تهمك.
    - **البحث والصياغة:** بحث سريع، وملخصات، ومسودات أولى للرسائل الإلكترونية أو المستندات.
    - **التذكيرات والمتابعات:** تنبيهات وقوائم تحقق تقودها Cron أو Heartbeat.
    - **أتمتة المتصفح:** ملء النماذج، وجمع البيانات، وتكرار المهام على الويب.
    - **التنسيق بين الأجهزة:** أرسل مهمة من هاتفك، ودع Gateway يشغّلها على خادم، ثم استلم النتيجة مرة أخرى في الدردشة.

  </Accordion>

  <Accordion title="هل يمكن لـ OpenClaw المساعدة في توليد العملاء المحتملين، والتواصل، والإعلانات، والمدونات لخدمة SaaS؟">
    نعم بالنسبة إلى **البحث، والتأهيل، والصياغة**. يمكنه فحص المواقع، وبناء قوائم مختصرة،
    وتلخيص العملاء المحتملين، وكتابة مسودات للتواصل أو نصوص إعلانية.

    أما بالنسبة إلى **حملات التواصل أو الإعلانات**، فأبقِ إنسانًا داخل الحلقة. تجنب الرسائل المزعجة، واتبع القوانين المحلية
    وسياسات المنصات، وراجع أي شيء قبل إرساله. وأكثر الأنماط أمانًا هو أن
    يقوم OpenClaw بالصياغة ثم توافق أنت عليها.

    المستندات: [الأمان](/ar/gateway/security).

  </Accordion>

  <Accordion title="ما المزايا مقارنةً بـ Claude Code في تطوير الويب؟">
    OpenClaw هو **مساعد شخصي** وطبقة تنسيق، وليس بديلًا عن IDE. استخدم
    Claude Code أو Codex لأسرع حلقة برمجة مباشرة داخل مستودع. واستخدم OpenClaw عندما
    تريد ذاكرة دائمة، ووصولًا عبر الأجهزة، وتنسيقًا للأدوات.

    المزايا:

    - **ذاكرة + مساحة عمل مستمرة** عبر الجلسات
    - **وصول متعدد المنصات** (WhatsApp، Telegram، TUI، WebChat)
    - **تنسيق الأدوات** (المتصفح، والملفات، والجدولة، والخطافات)
    - **Gateway تعمل دائمًا** (شغّلها على VPS، وتفاعل معها من أي مكان)
    - **Nodes** للمتصفح/الشاشة/الكاميرا/exec المحلي

    العرض: [https://openclaw.ai/showcase](https://openclaw.ai/showcase)

  </Accordion>
</AccordionGroup>

## Skills والأتمتة

<AccordionGroup>
  <Accordion title="كيف أخصص Skills من دون إبقاء المستودع متسخًا؟">
    استخدم عمليات التجاوز المُدارة بدلًا من تعديل نسخة المستودع. ضع تغييراتك في `~/.openclaw/skills/<name>/SKILL.md` (أو أضف مجلدًا عبر `skills.load.extraDirs` في `~/.openclaw/openclaw.json`). ترتيب الأولوية هو `<workspace>/skills` ← `<workspace>/.agents/skills` ← `~/.agents/skills` ← `~/.openclaw/skills` ← المضمّنة ← `skills.load.extraDirs`، لذا تظل عمليات التجاوز المُدارة متقدمة على Skills المضمّنة من دون المساس بـ git. وإذا كنت تحتاج إلى تثبيت Skill على مستوى عام لكنك تريد أن تكون مرئية لبعض الوكلاء فقط، فاحتفظ بالنسخة المشتركة في `~/.openclaw/skills` وتحكّم في الرؤية عبر `agents.defaults.skills` و`agents.list[].skills`. أما التعديلات الجديرة بالرفع إلى الأصل فقط فينبغي أن تعيش في المستودع وتُرسل كـ PRs.
  </Accordion>

  <Accordion title="هل يمكنني تحميل Skills من مجلد مخصص؟">
    نعم. أضف أدلة إضافية عبر `skills.load.extraDirs` في `~/.openclaw/openclaw.json` (أدنى أولوية). ترتيب الأولوية الافتراضي هو `<workspace>/skills` ← `<workspace>/.agents/skills` ← `~/.agents/skills` ← `~/.openclaw/skills` ← المضمّنة ← `skills.load.extraDirs`. يقوم `clawhub` بالتثبيت افتراضيًا في `./skills`، ويتعامل OpenClaw معها على أنها `<workspace>/skills` في الجلسة التالية. وإذا كان ينبغي أن تكون Skill مرئية لبعض الوكلاء فقط، فاربط ذلك مع `agents.defaults.skills` أو `agents.list[].skills`.
  </Accordion>

  <Accordion title="كيف يمكنني استخدام نماذج مختلفة لمهام مختلفة؟">
    الأنماط المدعومة اليوم هي:

    - **وظائف Cron**: يمكن للوظائف المعزولة تعيين تجاوز `model` لكل وظيفة.
    - **الوكلاء الفرعيون**: وجّه المهام إلى وكلاء منفصلين لديهم نماذج افتراضية مختلفة.
    - **التبديل عند الطلب**: استخدم `/model` لتبديل نموذج الجلسة الحالية في أي وقت.

    راجع [وظائف Cron](/ar/automation/cron-jobs)، و[توجيه الوكلاء المتعددين](/ar/concepts/multi-agent)، و[أوامر الشرطة المائلة](/ar/tools/slash-commands).

  </Accordion>

  <Accordion title="يتجمّد البوت أثناء تنفيذ أعمال ثقيلة. كيف أنقل ذلك إلى مكان آخر؟">
    استخدم **الوكلاء الفرعيين** للمهام الطويلة أو المتوازية. تعمل الوكلاء الفرعيون في جلستهم الخاصة،
    ويعيدون ملخصًا، ويحافظون على استجابة دردشتك الرئيسية.

    اطلب من البوت "spawn a sub-agent for this task" أو استخدم `/subagents`.
    واستخدم `/status` في الدردشة لمعرفة ما الذي يفعله Gateway الآن (وما إذا كان مشغولًا).

    نصيحة حول الرموز: كل من المهام الطويلة والوكلاء الفرعيين يستهلكان الرموز. وإذا كانت التكلفة مصدر قلق، فاضبط
    نموذجًا أرخص للوكلاء الفرعيين عبر `agents.defaults.subagents.model`.

    المستندات: [الوكلاء الفرعيون](/ar/tools/subagents)، [المهام الخلفية](/ar/automation/tasks).

  </Accordion>

  <Accordion title="كيف تعمل جلسات الوكلاء الفرعيين المرتبطة بالخيوط على Discord؟">
    استخدم روابط الخيوط. يمكنك ربط خيط Discord بوكيل فرعي أو بهدف جلسة بحيث تبقى رسائل المتابعة في ذلك الخيط على الجلسة المرتبطة نفسها.

    التدفق الأساسي:

    - أنشئه باستخدام `sessions_spawn` مع `thread: true` (واختياريًا `mode: "session"` للمتابعة المستمرة).
    - أو اربطه يدويًا باستخدام `/focus <target>`.
    - استخدم `/agents` لفحص حالة الربط.
    - استخدم `/session idle <duration|off>` و`/session max-age <duration|off>` للتحكم في إلغاء التركيز التلقائي.
    - استخدم `/unfocus` لفصل الخيط.

    الإعدادات المطلوبة:

    - الافتراضيات العامة: `session.threadBindings.enabled` و`session.threadBindings.idleHours` و`session.threadBindings.maxAgeHours`.
    - تجاوزات Discord: `channels.discord.threadBindings.enabled` و`channels.discord.threadBindings.idleHours` و`channels.discord.threadBindings.maxAgeHours`.
    - الربط التلقائي عند الإنشاء: اضبط `channels.discord.threadBindings.spawnSubagentSessions: true`.

    المستندات: [الوكلاء الفرعيون](/ar/tools/subagents)، [Discord](/ar/channels/discord)، [مرجع الإعدادات](/ar/gateway/configuration-reference)، [أوامر الشرطة المائلة](/ar/tools/slash-commands).

  </Accordion>

  <Accordion title="انتهى وكيل فرعي، لكن تحديث الإكمال ذهب إلى المكان الخطأ أو لم يُنشر إطلاقًا. ما الذي ينبغي أن أتحقق منه؟">
    تحقّق أولًا من مسار الطالب الذي تم حسمه:

    - يفضّل تسليم الوكيل الفرعي في وضع الإكمال أي خيط أو مسار محادثة مرتبط عندما يكون موجودًا.
    - إذا كان أصل الإكمال يحمل قناة فقط، فسيعود OpenClaw إلى المسار المخزّن لجلسة الطالب (`lastChannel` / `lastTo` / `lastAccountId`) حتى يظل التسليم المباشر ممكنًا.
    - إذا لم يوجد لا مسار مرتبط ولا مسار مخزّن قابل للاستخدام، فقد يفشل التسليم المباشر وتعود النتيجة إلى التسليم عبر الجلسة في قائمة الانتظار بدلًا من النشر الفوري في الدردشة.
    - لا تزال الأهداف غير الصالحة أو القديمة قادرة على فرض الرجوع إلى قائمة الانتظار أو التسبب في فشل التسليم النهائي.
    - إذا كان آخر رد مرئي للمساعد من الوكيل الابن هو رمز الصمت المطابق تمامًا `NO_REPLY` / `no_reply`، أو كان بالضبط `ANNOUNCE_SKIP`، فإن OpenClaw يمنع الإعلان عمدًا بدلًا من نشر تقدم أقدم لم يعد صالحًا.
    - إذا انتهت مهلة الوكيل الابن بعد مكالمات أدوات فقط، فقد يختزل الإعلان ذلك إلى ملخص قصير للتقدم الجزئي بدلًا من إعادة عرض ناتج الأدوات الخام.

    التصحيح:

    ```bash
    openclaw tasks show <runId-or-sessionKey>
    ```

    المستندات: [الوكلاء الفرعيون](/ar/tools/subagents)، [المهام الخلفية](/ar/automation/tasks)، [أدوات الجلسة](/ar/concepts/session-tool).

  </Accordion>

  <Accordion title="لا تعمل Cron أو التذكيرات. ما الذي ينبغي أن أتحقق منه؟">
    تعمل Cron داخل عملية Gateway. إذا لم تكن Gateway تعمل باستمرار،
    فلن تعمل الوظائف المجدولة.

    قائمة التحقق:

    - تأكد من أن Cron مفعّلة (`cron.enabled`) وأن `OPENCLAW_SKIP_CRON` غير مضبوط.
    - تحقق من أن Gateway تعمل على مدار الساعة طوال أيام الأسبوع (من دون سكون/إعادة تشغيل).
    - تحقق من إعدادات المنطقة الزمنية للوظيفة (`--tz` مقابل المنطقة الزمنية للمضيف).

    التصحيح:

    ```bash
    openclaw cron run <jobId>
    openclaw cron runs --id <jobId> --limit 50
    ```

    المستندات: [وظائف Cron](/ar/automation/cron-jobs)، [الأتمتة والمهام](/ar/automation).

  </Accordion>

  <Accordion title="تم تشغيل Cron، لكن لم يتم إرسال أي شيء إلى القناة. لماذا؟">
    تحقّق أولًا من وضع التسليم:

    - يعني `--no-deliver` / `delivery.mode: "none"` أنه لا يُتوقع إرسال أي رسالة خارجية.
    - يعني غياب هدف إعلان (`channel` / `to`) أو عدم صلاحيته أن المشغّل تخطّى التسليم الصادر.
    - تعني حالات فشل مصادقة القناة (`unauthorized`، `Forbidden`) أن المشغّل حاول التسليم ولكن بيانات الاعتماد منعته.
    - تُعامل النتيجة المعزولة الصامتة (`NO_REPLY` / `no_reply` فقط) على أنها غير قابلة للتسليم عمدًا، لذلك يمنع المشغّل أيضًا الرجوع إلى التسليم عبر قائمة الانتظار.

    بالنسبة إلى وظائف Cron المعزولة، يتولى المشغّل التسليم النهائي. ومن المتوقع
    أن يعيد الوكيل ملخصًا نصيًا عاديًا ليرسله المشغّل. ويُبقي `--no-deliver`
    هذه النتيجة داخلية؛ ولا يسمح للوكيل بالإرسال مباشرةً باستخدام
    أداة الرسائل بدلًا من ذلك.

    التصحيح:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    المستندات: [وظائف Cron](/ar/automation/cron-jobs)، [المهام الخلفية](/ar/automation/tasks).

  </Accordion>

  <Accordion title="لماذا غيّر تشغيل Cron المعزول النماذج أو أعاد المحاولة مرة واحدة؟">
    يكون هذا عادةً مسار التبديل المباشر للنموذج، وليس جدولة مكررة.

    يمكن لـ Cron المعزولة أن تحتفظ بتحويل نموذج وقت التشغيل وتعيد المحاولة عندما يرمي التشغيل
    النشط الخطأ `LiveSessionModelSwitchError`. وتحافظ إعادة المحاولة على
    المزوّد/النموذج الذي تم التبديل إليه، وإذا كان التبديل قد حمل تجاوزًا جديدًا
    لملف تعريف المصادقة، فإن Cron تحتفظ به أيضًا قبل إعادة المحاولة.

    قواعد الاختيار ذات الصلة:

    - يتقدّم أولًا تجاوز نموذج Gmail hook عند انطباقه.
    - ثم `model` الخاصة بكل وظيفة.
    - ثم أي تجاوز نموذج مخزّن لجلسة Cron.
    - ثم اختيار النموذج العادي للوكيل/الافتراضي.

    حلقة إعادة المحاولة محدودة. بعد المحاولة الأولية بالإضافة إلى محاولتي
    تبديل، تُجهض Cron بدلًا من الاستمرار إلى ما لا نهاية.

    التصحيح:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    المستندات: [وظائف Cron](/ar/automation/cron-jobs)، [Cron CLI](/cli/cron).

  </Accordion>

  <Accordion title="كيف أُثبت Skills على Linux؟">
    استخدم أوامر `openclaw skills` الأصلية أو ضع Skills داخل مساحة عملك. واجهة Skills في macOS غير متاحة على Linux.
    تصفح Skills على [https://clawhub.ai](https://clawhub.ai).

    ```bash
    openclaw skills search "calendar"
    openclaw skills search --limit 20
    openclaw skills install <skill-slug>
    openclaw skills install <skill-slug> --version <version>
    openclaw skills install <skill-slug> --force
    openclaw skills update --all
    openclaw skills list --eligible
    openclaw skills check
    ```

    يكتب `openclaw skills install` الأصلي داخل دليل `skills/`
    الخاص بمساحة العمل النشطة. ثبّت CLI المنفصل `clawhub` فقط إذا كنت تريد نشر
    Skills الخاصة بك أو مزامنتها. وللتثبيتات المشتركة بين الوكلاء، ضع Skill تحت
    `~/.openclaw/skills` واستخدم `agents.defaults.skills` أو
    `agents.list[].skills` إذا كنت تريد تضييق نطاق الوكلاء الذين يمكنهم رؤيتها.

  </Accordion>

  <Accordion title="هل يمكن لـ OpenClaw تشغيل المهام وفق جدول زمني أو بشكل مستمر في الخلفية؟">
    نعم. استخدم مجدول Gateway:

    - **وظائف Cron** للمهام المجدولة أو المتكررة (وتستمر عبر إعادة التشغيل).
    - **Heartbeat** لعمليات الفحص الدورية الخاصة بـ "الجلسة الرئيسية".
    - **الوظائف المعزولة** للوكلاء المستقلين الذين ينشرون ملخصات أو يسلّمون النتائج إلى الدردشات.

    المستندات: [وظائف Cron](/ar/automation/cron-jobs)، [الأتمتة والمهام](/ar/automation)،
    [Heartbeat](/ar/gateway/heartbeat).

  </Accordion>

  <Accordion title="هل يمكنني تشغيل Skills الخاصة بـ Apple وmacOS فقط من Linux؟">
    ليس بشكل مباشر. يتم تقييد Skills الخاصة بـ macOS بواسطة `metadata.openclaw.os` بالإضافة إلى الملفات التنفيذية المطلوبة، ولا تظهر Skills في مطالبة النظام إلا عندما تكون مؤهلة على **مضيف Gateway**. على Linux، لن يتم تحميل Skills المخصّصة لـ `darwin` فقط (مثل `apple-notes` و`apple-reminders` و`things-mac`) ما لم تتجاوز هذا التقييد.

    لديك ثلاثة أنماط مدعومة:

    **الخيار A - شغّل Gateway على جهاز Mac (الأبسط).**
    شغّل Gateway حيث توجد الملفات التنفيذية الخاصة بـ macOS، ثم اتصل من Linux في [الوضع البعيد](#gateway-ports-already-running-and-remote-mode) أو عبر Tailscale. تُحمَّل Skills بشكل طبيعي لأن مضيف Gateway هو macOS.

    **الخيار B - استخدم Node يعمل بنظام macOS (من دون SSH).**
    شغّل Gateway على Linux، ثم أقرن Node يعمل بنظام macOS (تطبيق شريط القوائم)، واضبط **Node Run Commands** على "Always Ask" أو "Always Allow" على جهاز Mac. يمكن لـ OpenClaw معاملة Skills الخاصة بـ macOS فقط على أنها مؤهلة عندما تكون الملفات التنفيذية المطلوبة موجودة على Node. يشغّل الوكيل تلك Skills عبر أداة `nodes`. وإذا اخترت "Always Ask"، فإن الموافقة على "Always Allow" في المطالبة تضيف ذلك الأمر إلى قائمة السماح.

    **الخيار C - مرّر الملفات التنفيذية الخاصة بـ macOS عبر SSH (متقدم).**
    أبقِ Gateway على Linux، ولكن اجعل ملفات CLI التنفيذية المطلوبة تُحلّ إلى أغلفة SSH تعمل على جهاز Mac. ثم تجاوز Skill للسماح بـ Linux حتى تظل مؤهلة.

    1. أنشئ غلاف SSH للملف التنفيذي (مثال: `memo` من أجل Apple Notes):

       ```bash
       #!/usr/bin/env bash
       set -euo pipefail
       exec ssh -T user@mac-host /opt/homebrew/bin/memo "$@"
       ```

    2. ضع الغلاف على `PATH` على مضيف Linux (على سبيل المثال `~/bin/memo`).
    3. تجاوز بيانات Skill الوصفية (في مساحة العمل أو `~/.openclaw/skills`) للسماح بـ Linux:

       ```markdown
       ---
       name: apple-notes
       description: Manage Apple Notes via the memo CLI on macOS.
       metadata: { "openclaw": { "os": ["darwin", "linux"], "requires": { "bins": ["memo"] } } }
       ---
       ```

    4. ابدأ جلسة جديدة حتى يتم تحديث لقطة Skills.

  </Accordion>

  <Accordion title="هل لديكم تكامل مع Notion أو HeyGen؟">
    ليس مضمّنًا حاليًا.

    الخيارات:

    - **Skill / Plugin مخصص:** الأفضل للوصول الموثوق إلى API (لكل من Notion وHeyGen واجهات API).
    - **أتمتة المتصفح:** تعمل من دون شيفرة لكنها أبطأ وأكثر هشاشة.

    إذا كنت تريد الاحتفاظ بالسياق لكل عميل (سير عمل الوكالات)، فهناك نمط بسيط:

    - صفحة Notion واحدة لكل عميل (السياق + التفضيلات + العمل النشط).
    - اطلب من الوكيل جلب تلك الصفحة في بداية الجلسة.

    إذا كنت تريد تكاملًا أصليًا، فافتح طلب ميزة أو ابنِ Skill
    تستهدف تلك الواجهات.

    تثبيت Skills:

    ```bash
    openclaw skills install <skill-slug>
    openclaw skills update --all
    ```

    تصل التثبيتات الأصلية إلى دليل `skills/` الخاص بمساحة العمل النشطة. وبالنسبة إلى Skills المشتركة بين الوكلاء، ضعها في `~/.openclaw/skills/<name>/SKILL.md`. وإذا كان ينبغي أن ترى بعض الوكلاء فقط تثبيتًا مشتركًا، فاضبط `agents.defaults.skills` أو `agents.list[].skills`. تتوقع بعض Skills وجود ملفات تنفيذية مثبّتة عبر Homebrew؛ وعلى Linux يعني ذلك Linuxbrew (راجع إدخال الأسئلة الشائعة عن Homebrew على Linux أعلاه). راجع [Skills](/ar/tools/skills)، و[إعدادات Skills](/ar/tools/skills-config)، و[ClawHub](/ar/tools/clawhub).

  </Accordion>

  <Accordion title="كيف أستخدم Chrome الحالي المسجّل الدخول به مع OpenClaw؟">
    استخدم ملف تعريف المتصفح المضمّن `user`، الذي يتصل عبر Chrome DevTools MCP:

    ```bash
    openclaw browser --browser-profile user tabs
    openclaw browser --browser-profile user snapshot
    ```

    وإذا كنت تريد اسمًا مخصصًا، فأنشئ ملف تعريف MCP صريحًا:

    ```bash
    openclaw browser create-profile --name chrome-live --driver existing-session
    openclaw browser --browser-profile chrome-live tabs
    ```

    هذا المسار محلي على المضيف. وإذا كانت Gateway تعمل في مكان آخر، فإما أن تشغّل مضيف Node على جهاز المتصفح أو تستخدم CDP بعيدًا بدلًا من ذلك.

    القيود الحالية على `existing-session` / `user`:

    - تعتمد الإجراءات على `ref`، لا على محددات CSS
    - تتطلب عمليات الرفع `ref` / `inputRef` وتدعم حاليًا ملفًا واحدًا في كل مرة
    - ما زالت `responsebody`، وتصدير PDF، واعتراض التنزيلات، والإجراءات الدفعية تحتاج إلى متصفح مُدار أو ملف تعريف CDP خام

  </Accordion>
</AccordionGroup>

## العزل والذاكرة

<AccordionGroup>
  <Accordion title="هل توجد وثيقة مخصصة للعزل؟">
    نعم. راجع [العزل](/ar/gateway/sandboxing). وبالنسبة إلى إعداد Docker تحديدًا (Gateway كامل داخل Docker أو صور العزل)، راجع [Docker](/ar/install/docker).
  </Accordion>

  <Accordion title="يبدو Docker محدودًا - كيف أمكّن الميزات الكاملة؟">
    الصورة الافتراضية تضع الأمان أولًا وتعمل كمستخدم `node`، لذلك فهي لا
    تتضمن حزم النظام، أو Homebrew، أو المتصفحات المضمّنة. ولإعداد أكثر اكتمالًا:

    - اجعل `/home/node` دائمًا باستخدام `OPENCLAW_HOME_VOLUME` حتى تبقى الذاكرات المؤقتة.
    - ضمّن تبعيات النظام داخل الصورة باستخدام `OPENCLAW_DOCKER_APT_PACKAGES`.
    - ثبّت متصفحات Playwright عبر CLI المضمّن:
      `node /app/node_modules/playwright-core/cli.js install chromium`
    - اضبط `PLAYWRIGHT_BROWSERS_PATH` وتأكد من استمرارية هذا المسار.

    المستندات: [Docker](/ar/install/docker)، [Browser](/ar/tools/browser).

  </Accordion>

  <Accordion title="هل يمكنني إبقاء الرسائل الخاصة شخصية وجعل المجموعات عامة/معزولة باستخدام وكيل واحد؟">
    نعم - إذا كانت الحركة الخاصة لديك هي **DMs** وكانت الحركة العامة لديك هي **groups**.

    استخدم `agents.defaults.sandbox.mode: "non-main"` حتى تعمل جلسات المجموعات/القنوات (المفاتيح غير الرئيسية) داخل Docker، بينما تبقى جلسة DM الرئيسية على المضيف. ثم قيّد الأدوات المتاحة في الجلسات المعزولة عبر `tools.sandbox.tools`.

    شرح الإعداد الكامل + مثال للإعدادات: [المجموعات: رسائل خاصة شخصية + مجموعات عامة](/ar/channels/groups#pattern-personal-dms-public-groups-single-agent)

    المرجع الأساسي للإعدادات: [إعدادات Gateway](/ar/gateway/configuration-reference#agentsdefaultssandbox)

  </Accordion>

  <Accordion title="كيف أربط مجلدًا من المضيف داخل العزل؟">
    اضبط `agents.defaults.sandbox.docker.binds` على `["host:path:mode"]` (مثل `"/home/user/src:/src:ro"`). يتم دمج الروابط العامة وروابط كل وكيل؛ ويتم تجاهل الروابط الخاصة بكل وكيل عندما تكون `scope: "shared"`. استخدم `:ro` لأي شيء حساس وتذكّر أن الروابط تتجاوز جدران نظام ملفات العزل.

    يتحقق OpenClaw من صحة مصادر الربط مقارنةً بكل من المسار المُطبّع والمسار القانوني الذي يُحل عبر أعمق سلف موجود. وهذا يعني أن محاولات الهروب عبر والد symlink تظل محظورة افتراضيًا حتى عندما لا يكون مقطع المسار الأخير موجودًا بعد، كما أن فحوصات الجذر المسموح به تظل مطبقة بعد حل symlink.

    راجع [العزل](/ar/gateway/sandboxing#custom-bind-mounts) و[Sandbox vs Tool Policy vs Elevated](/ar/gateway/sandbox-vs-tool-policy-vs-elevated#bind-mounts-security-quick-check) للاطلاع على الأمثلة وملاحظات الأمان.

  </Accordion>

  <Accordion title="كيف تعمل الذاكرة؟">
    ذاكرة OpenClaw هي مجرد ملفات Markdown داخل مساحة عمل الوكيل:

    - ملاحظات يومية في `memory/YYYY-MM-DD.md`
    - ملاحظات منسقة طويلة الأمد في `MEMORY.md` (للجلسات الرئيسية/الخاصة فقط)

    كما يشغّل OpenClaw **تفريغ ذاكرة صامتًا قبل Compaction** لتذكير النموذج
    بكتابة ملاحظات دائمة قبل Compaction التلقائي. ولا يعمل هذا إلا عندما تكون
    مساحة العمل قابلة للكتابة (تتخطاه بيئات العزل للقراءة فقط). راجع [الذاكرة](/ar/concepts/memory).

  </Accordion>

  <Accordion title="الذاكرة تستمر في نسيان الأشياء. كيف أجعلها تثبت؟">
    اطلب من البوت **كتابة المعلومة في الذاكرة**. تنتمي الملاحظات طويلة الأمد إلى `MEMORY.md`،
    بينما يذهب السياق قصير الأمد إلى `memory/YYYY-MM-DD.md`.

    ما زلنا نعمل على تحسين هذا المجال. ومن المفيد تذكير النموذج بتخزين الذكريات؛
    فهو سيعرف ما الذي ينبغي فعله. وإذا استمر في النسيان، فتحقق من أن Gateway تستخدم
    مساحة العمل نفسها في كل تشغيل.

    المستندات: [الذاكرة](/ar/concepts/memory)، [مساحة عمل الوكيل](/ar/concepts/agent-workspace).

  </Accordion>

  <Accordion title="هل تستمر الذاكرة إلى الأبد؟ وما الحدود؟">
    تعيش ملفات الذاكرة على القرص وتستمر حتى تحذفها. والحد هنا هو
    مساحة التخزين لديك، لا النموذج. أما **سياق الجلسة** فلا يزال محدودًا بنافذة سياق
    النموذج، لذا قد تُضغط المحادثات الطويلة أو تُقتطع. ولهذا السبب
    يوجد بحث الذاكرة - فهو يعيد فقط الأجزاء ذات الصلة إلى السياق.

    المستندات: [الذاكرة](/ar/concepts/memory)، [السياق](/ar/concepts/context).

  </Accordion>

  <Accordion title="هل يتطلب البحث الدلالي في الذاكرة مفتاح OpenAI API؟">
    نعم، ولكن فقط إذا كنت تستخدم **OpenAI embeddings**. تغطي Codex OAuth المحادثة/الإكمالات
    ولا **تمنح** وصولًا إلى embeddings، لذلك فإن **تسجيل الدخول باستخدام Codex (OAuth أو
    تسجيل دخول Codex CLI)** لا يفيد في البحث الدلالي في الذاكرة. وما تزال OpenAI embeddings
    تحتاج إلى مفتاح API حقيقي (`OPENAI_API_KEY` أو `models.providers.openai.apiKey`).

    إذا لم تضبط مزودًا صراحةً، فإن OpenClaw يختار مزودًا تلقائيًا عندما
    يتمكن من حل مفتاح API (ملفات تعريف المصادقة، أو `models.providers.*.apiKey`، أو متغيرات البيئة).
    وهو يفضّل OpenAI إذا أمكن حل مفتاح OpenAI، ثم Gemini إذا أمكن حل مفتاح Gemini،
    ثم Voyage، ثم Mistral. وإذا لم يكن هناك مفتاح بعيد متاح، فسيظل
    البحث في الذاكرة معطّلًا حتى تقوم بإعداده. وإذا كان لديك مسار نموذج محلي
    مضبوط وموجود، فإن OpenClaw
    يفضّل `local`. كما أن Ollama مدعوم عندما تضبط صراحةً
    `memorySearch.provider = "ollama"`.

    وإذا كنت تفضّل البقاء محليًا، فاضبط `memorySearch.provider = "local"` (واختياريًا
    `memorySearch.fallback = "none"`). وإذا كنت تريد Gemini embeddings، فاضبط
    `memorySearch.provider = "gemini"` ووفّر `GEMINI_API_KEY` (أو
    `memorySearch.remote.apiKey`). نحن ندعم نماذج embeddings من **OpenAI وGemini وVoyage وMistral وOllama أو local**
    - راجع [الذاكرة](/ar/concepts/memory) للحصول على تفاصيل الإعداد.

  </Accordion>
</AccordionGroup>

## أين توجد الأشياء على القرص

<AccordionGroup>
  <Accordion title="هل يتم حفظ جميع البيانات المستخدمة مع OpenClaw محليًا؟">
    لا - **حالة OpenClaw محلية**، لكن **الخدمات الخارجية لا تزال ترى ما ترسله إليها**.

    - **محلي افتراضيًا:** تعيش الجلسات، وملفات الذاكرة، والإعدادات، ومساحة العمل على مضيف Gateway
      (`~/.openclaw` + دليل مساحة العمل الخاص بك).
    - **بعيد بحكم الضرورة:** تذهب الرسائل التي ترسلها إلى مزودي النماذج (Anthropic/OpenAI/إلخ) إلى
      واجهات API الخاصة بهم، كما تخزن منصات الدردشة (WhatsApp/Telegram/Slack/إلخ) بيانات الرسائل على
      خوادمها.
    - **أنت تتحكم في الأثر:** يؤدي استخدام النماذج المحلية إلى إبقاء المطالبات على جهازك، لكن
      حركة القنوات لا تزال تمر عبر خوادم القناة.

    ذو صلة: [مساحة عمل الوكيل](/ar/concepts/agent-workspace)، [الذاكرة](/ar/concepts/memory).

  </Accordion>

  <Accordion title="أين يخزّن OpenClaw بياناته؟">
    كل شيء يعيش تحت `$OPENCLAW_STATE_DIR` (الافتراضي: `~/.openclaw`):

    | Path                                                            | Purpose                                                            |
    | --------------------------------------------------------------- | ------------------------------------------------------------------ |
    | `$OPENCLAW_STATE_DIR/openclaw.json`                             | الإعدادات الرئيسية (JSON5)                                         |
    | `$OPENCLAW_STATE_DIR/credentials/oauth.json`                    | استيراد OAuth قديم (يُنسخ إلى ملفات تعريف المصادقة عند أول استخدام) |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth-profiles.json` | ملفات تعريف المصادقة (OAuth، ومفاتيح API، و`keyRef`/`tokenRef` الاختيارية) |
    | `$OPENCLAW_STATE_DIR/secrets.json`                              | حمولة سرية اختيارية مدعومة بالملفات لمزودي `file` من SecretRef    |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth.json`          | ملف توافق قديم (تُنظَّف إدخالات `api_key` الثابتة)                |
    | `$OPENCLAW_STATE_DIR/credentials/`                              | حالة المزوّد (مثل `whatsapp/<accountId>/creds.json`)              |
    | `$OPENCLAW_STATE_DIR/agents/`                                   | حالة كل وكيل على حدة (agentDir + sessions)                        |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                | سجل المحادثات والحالة (لكل وكيل)                                  |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/sessions.json`   | البيانات الوصفية للجلسات (لكل وكيل)                               |

    المسار القديم لوكيل واحد: `~/.openclaw/agent/*` (يتم ترحيله بواسطة `openclaw doctor`).

    أما **مساحة العمل** الخاصة بك (`AGENTS.md`، وملفات الذاكرة، وSkills، وما إلى ذلك) فهي منفصلة وتُضبط عبر `agents.defaults.workspace` (الافتراضي: `~/.openclaw/workspace`).

  </Accordion>

  <Accordion title="أين ينبغي أن توجد AGENTS.md / SOUL.md / USER.md / MEMORY.md؟">
    تعيش هذه الملفات في **مساحة عمل الوكيل**، وليس في `~/.openclaw`.

    - **مساحة العمل (لكل وكيل):** `AGENTS.md` و`SOUL.md` و`IDENTITY.md` و`USER.md`،
      و`MEMORY.md` (أو البديل القديم `memory.md` عند غياب `MEMORY.md`)،
      و`memory/YYYY-MM-DD.md`، و`HEARTBEAT.md` اختياريًا.
    - **دليل الحالة (`~/.openclaw`)**: الإعدادات، وحالة القناة/المزوّد، وملفات تعريف المصادقة، والجلسات، والسجلات،
      وSkills المشتركة (`~/.openclaw/skills`).

    مساحة العمل الافتراضية هي `~/.openclaw/workspace`، ويمكن ضبطها عبر:

    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
    }
    ```

    إذا كان البوت "ينسى" بعد إعادة التشغيل، فتأكد من أن Gateway تستخدم
    مساحة العمل نفسها في كل تشغيل (وتذكّر: يستخدم الوضع البعيد **مساحة عمل مضيف Gateway**،
    وليس حاسوبك المحمول المحلي).

    نصيحة: إذا كنت تريد سلوكًا أو تفضيلًا دائمًا، فاطلب من البوت **كتابته في
    AGENTS.md أو MEMORY.md** بدلًا من الاعتماد على سجل الدردشة.

    راجع [مساحة عمل الوكيل](/ar/concepts/agent-workspace) و[الذاكرة](/ar/concepts/memory).

  </Accordion>

  <Accordion title="استراتيجية النسخ الاحتياطي الموصى بها">
    ضع **مساحة عمل الوكيل** الخاصة بك في مستودع git **خاص** وقم بعمل نسخة احتياطية له في مكان
    خاص (مثل GitHub الخاص). يلتقط ذلك الذاكرة + ملفات AGENTS/SOUL/USER
    ويتيح لك استعادة "عقل" المساعد لاحقًا.

    لا تقم **بعمل commit** لأي شيء ضمن `~/.openclaw` (بيانات الاعتماد، أو الجلسات، أو الرموز، أو حمولات الأسرار المشفرة).
    وإذا كنت تحتاج إلى استعادة كاملة، فقم بنسخ كل من مساحة العمل ودليل الحالة احتياطيًا
    بشكل منفصل (راجع سؤال الترحيل أعلاه).

    المستندات: [مساحة عمل الوكيل](/ar/concepts/agent-workspace).

  </Accordion>

  <Accordion title="كيف أزيل OpenClaw بالكامل؟">
    راجع الدليل المخصص: [إلغاء التثبيت](/ar/install/uninstall).
  </Accordion>

  <Accordion title="هل يمكن للوكلاء العمل خارج مساحة العمل؟">
    نعم. مساحة العمل هي **cwd الافتراضي** ومرساة الذاكرة، وليست عزلًا صارمًا.
    تُحل المسارات النسبية داخل مساحة العمل، لكن يمكن للمسارات المطلقة الوصول إلى
    مواقع أخرى على المضيف ما لم يكن العزل مفعّلًا. وإذا كنت تحتاج إلى عزل، فاستخدم
    [`agents.defaults.sandbox`](/ar/gateway/sandboxing) أو إعدادات العزل الخاصة بكل وكيل. وإذا
    كنت تريد أن يكون المستودع هو دليل العمل الافتراضي، فوجّه
    `workspace` الخاصة بذلك الوكيل إلى جذر المستودع. إن مستودع OpenClaw مجرد
    شيفرة مصدر؛ فاحتفظ بمساحة العمل منفصلة ما لم تكن تريد عمدًا أن يعمل الوكيل داخله.

    مثال (المستودع كـ cwd افتراضي):

    ```json5
    {
      agents: {
        defaults: {
          workspace: "~/Projects/my-repo",
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="الوضع البعيد: أين يوجد مخزن الجلسات؟">
    تملك حالة الجلسة **مضيف Gateway**. إذا كنت في الوضع البعيد، فإن مخزن الجلسات الذي يهمك يوجد على الجهاز البعيد، وليس على حاسوبك المحمول المحلي. راجع [إدارة الجلسات](/ar/concepts/session).
  </Accordion>
</AccordionGroup>

## أساسيات الإعدادات

<AccordionGroup>
  <Accordion title="ما صيغة الإعدادات؟ وأين توجد؟">
    يقرأ OpenClaw ملف إعدادات **JSON5** اختياريًا من `$OPENCLAW_CONFIG_PATH` (الافتراضي: `~/.openclaw/openclaw.json`):

    ```
    $OPENCLAW_CONFIG_PATH
    ```

    إذا كان الملف مفقودًا، فإنه يستخدم افتراضيات آمنة نسبيًا (بما في ذلك مساحة عمل افتراضية هي `~/.openclaw/workspace`).

  </Accordion>

  <Accordion title='لقد ضبطت gateway.bind: "lan" (أو "tailnet") والآن لا شيء يستمع / تقول واجهة المستخدم unauthorized'>
    تتطلب عمليات الربط غير loopback **مسار مصادقة صالحًا لـ Gateway**. وعمليًا يعني ذلك:

    - مصادقة السر المشترك: رمز مميز أو كلمة مرور
    - `gateway.auth.mode: "trusted-proxy"` خلف وكيل عكسي مدرك للهوية غير loopback ومضبوط بشكل صحيح

    ```json5
    {
      gateway: {
        bind: "lan",
        auth: {
          mode: "token",
          token: "replace-me",
        },
      },
    }
    ```

    ملاحظات:

    - لا يؤدي `gateway.remote.token` / `.password` إلى تمكين مصادقة Gateway المحلية بمفردهما.
    - يمكن للمسارات المحلية استدعاء `gateway.remote.*` كاحتياط فقط عندما تكون `gateway.auth.*` غير مضبوطة.
    - بالنسبة إلى مصادقة كلمة المرور، اضبط `gateway.auth.mode: "password"` بالإضافة إلى `gateway.auth.password` (أو `OPENCLAW_GATEWAY_PASSWORD`) بدلًا من ذلك.
    - إذا جرى ضبط `gateway.auth.token` / `gateway.auth.password` صراحةً عبر SecretRef وتعذر حلّه، فإن الحل يفشل على نحو مغلق افتراضيًا (ولا يوجد احتياط بعيد يحجب ذلك).
    - تُصادق إعدادات Control UI ذات السر المشترك عبر `connect.params.auth.token` أو `connect.params.auth.password` (المخزنة في إعدادات التطبيق/واجهة المستخدم). أما الأوضاع الحاملة للهوية مثل Tailscale Serve أو `trusted-proxy` فتستخدم ترويسات الطلب بدلًا من ذلك. تجنّب وضع الأسرار المشتركة في عناوين URL.
    - مع `gateway.auth.mode: "trusted-proxy"`، فإن الوكلاء العكسيين على loopback على المضيف نفسه ما زالوا **لا** يستوفون مصادقة trusted-proxy. يجب أن يكون trusted proxy مصدرًا غير loopback ومضبوطًا في الإعدادات.

  </Accordion>

  <Accordion title="لماذا أحتاج إلى رمز مميز على localhost الآن؟">
    يفرض OpenClaw مصادقة Gateway افتراضيًا، بما في ذلك loopback. وفي المسار الافتراضي العادي يعني ذلك مصادقة الرمز المميز: إذا لم يتم ضبط مسار مصادقة صريح، فإن بدء تشغيل Gateway يحسم إلى وضع الرمز المميز ويولّد واحدًا تلقائيًا، ثم يحفظه في `gateway.auth.token`، لذا **يجب على عملاء WS المحليين المصادقة**. وهذا يمنع العمليات المحلية الأخرى من استدعاء Gateway.

    وإذا كنت تفضّل مسار مصادقة مختلفًا، فيمكنك اختيار وضع كلمة المرور صراحةً (أو، بالنسبة إلى الوكلاء العكسيين غير loopback والمدركين للهوية، `trusted-proxy`). وإذا كنت **حقًا** تريد loopback مفتوحًا، فاضبط `gateway.auth.mode: "none"` صراحةً في إعداداتك. ويمكن لـ Doctor إنشاء رمز مميز لك في أي وقت: `openclaw doctor --generate-gateway-token`.

  </Accordion>

  <Accordion title="هل يجب أن أعيد التشغيل بعد تغيير الإعدادات؟">
    تراقب Gateway ملف الإعدادات وتدعم إعادة التحميل السريع:

    - `gateway.reload.mode: "hybrid"` (الافتراضي): يطبّق التغييرات الآمنة بسرعة، ويعيد التشغيل للتغييرات الحرجة
    - كما أن `hot` و`restart` و`off` مدعومة أيضًا

  </Accordion>

  <Accordion title="كيف أعطّل العبارات الطريفة في CLI؟">
    اضبط `cli.banner.taglineMode` في الإعدادات:

    ```json5
    {
      cli: {
        banner: {
          taglineMode: "off", // random | default | off
        },
      },
    }
    ```

    - `off`: يُخفي نص العبارة مع الإبقاء على سطر عنوان الإصدار/الإصدار.
    - `default`: يستخدم `All your chats, one OpenClaw.` في كل مرة.
    - `random`: عبارات طريفة/موسمية متناوبة (السلوك الافتراضي).
    - إذا كنت لا تريد أي بانر إطلاقًا، فاضبط متغير البيئة `OPENCLAW_HIDE_BANNER=1`.

  </Accordion>

  <Accordion title="كيف أمكّن web search (وweb fetch)؟">
    يعمل `web_fetch` من دون مفتاح API. أما `web_search` فيعتمد على
    المزوّد الذي اخترته:

    - تتطلب المزوّدات المعتمدة على API مثل Brave وExa وFirecrawl وGemini وGrok وKimi وMiniMax Search وPerplexity وTavily إعداد مفاتيح API المعتاد.
    - بحث الويب في Ollama لا يحتاج إلى مفتاح، لكنه يستخدم مضيف Ollama الذي ضبطته ويتطلب `ollama signin`.
    - لا يحتاج DuckDuckGo إلى مفتاح، لكنه تكامل غير رسمي قائم على HTML.
    - SearXNG لا يحتاج إلى مفتاح/ويمكن استضافته ذاتيًا؛ اضبط `SEARXNG_BASE_URL` أو `plugins.entries.searxng.config.webSearch.baseUrl`.

    **الموصى به:** شغّل `openclaw configure --section web` واختر مزودًا.
    بدائل متغيرات البيئة:

    - Brave: `BRAVE_API_KEY`
    - Exa: `EXA_API_KEY`
    - Firecrawl: `FIRECRAWL_API_KEY`
    - Gemini: `GEMINI_API_KEY`
    - Grok: `XAI_API_KEY`
    - Kimi: `KIMI_API_KEY` أو `MOONSHOT_API_KEY`
    - MiniMax Search: `MINIMAX_CODE_PLAN_KEY` أو `MINIMAX_CODING_API_KEY` أو `MINIMAX_API_KEY`
    - Perplexity: `PERPLEXITY_API_KEY` أو `OPENROUTER_API_KEY`
    - SearXNG: `SEARXNG_BASE_URL`
    - Tavily: `TAVILY_API_KEY`

    ```json5
    {
      plugins: {
        entries: {
          brave: {
            config: {
              webSearch: {
                apiKey: "BRAVE_API_KEY_HERE",
              },
            },
          },
        },
        },
        tools: {
          web: {
            search: {
              enabled: true,
              provider: "brave",
              maxResults: 5,
            },
            fetch: {
              enabled: true,
              provider: "firecrawl", // اختياري؛ احذفه لاكتشافه تلقائيًا
            },
          },
        },
    }
    ```

    تعيش إعدادات web search الخاصة بكل مزوّد الآن تحت `plugins.entries.<plugin>.config.webSearch.*`.
    وما زالت مسارات المزوّد القديمة `tools.web.search.*` تُحمّل مؤقتًا من أجل التوافق، لكن لا ينبغي استخدامها في الإعدادات الجديدة.
    أما إعدادات fallback الخاصة بـ Firecrawl web-fetch فتوجد تحت `plugins.entries.firecrawl.config.webFetch.*`.

    ملاحظات:

    - إذا كنت تستخدم قوائم السماح، فأضف `web_search`/`web_fetch`/`x_search` أو `group:web`.
    - يكون `web_fetch` مفعّلًا افتراضيًا (ما لم يُعطّل صراحةً).
    - إذا لم يتم ضبط `tools.web.fetch.provider`، يكتشف OpenClaw تلقائيًا أول مزوّد fallback جاهز للجلب من بيانات الاعتماد المتاحة. والمزوّد المضمّن اليوم هو Firecrawl.
    - تقرأ العمليات الخلفية متغيرات البيئة من `~/.openclaw/.env` (أو من بيئة الخدمة).

    المستندات: [أدوات الويب](/ar/tools/web).

  </Accordion>

  <Accordion title="قام config.apply بمسح إعداداتي. كيف أستعيدها وأتجنب ذلك؟">
    يقوم `config.apply` باستبدال **الإعدادات بالكامل**. فإذا أرسلت كائنًا جزئيًا، فسيتم
    حذف كل شيء آخر.

    الاستعادة:

    - استعد من نسخة احتياطية (git أو نسخة من `~/.openclaw/openclaw.json`).
    - إذا لم تكن لديك نسخة احتياطية، فأعد تشغيل `openclaw doctor` وأعد تهيئة القنوات/النماذج.
    - إذا كان هذا غير متوقع، فافتح تقرير خطأ وأرفق آخر إعدادات معروفة لديك أو أي نسخة احتياطية.
    - يمكن لوكيل برمجة محلي في كثير من الأحيان إعادة بناء إعدادات صالحة من السجلات أو السجل.

    تجنّب ذلك:

    - استخدم `openclaw config set` للتغييرات الصغيرة.
    - استخدم `openclaw configure` للتحرير التفاعلي.
    - استخدم `config.schema.lookup` أولًا عندما لا تكون متأكدًا من المسار الدقيق أو شكل الحقل؛ فهو يعيد عقدة مخطط سطحية بالإضافة إلى ملخصات الأبناء المباشرين للتعمق.
    - استخدم `config.patch` لتعديلات RPC الجزئية؛ واحتفظ بـ `config.apply` لاستبدال الإعدادات الكاملة فقط.
    - إذا كنت تستخدم أداة `gateway` الخاصة بالمالك فقط من تشغيل وكيل، فستظل ترفض الكتابة إلى `tools.exec.ask` / `tools.exec.security` (بما في ذلك الأسماء البديلة القديمة `tools.bash.*` التي تُطبَّع إلى مسارات exec المحمية نفسها).

    المستندات: [الإعدادات](/cli/config)، [التهيئة](/cli/configure)، [Doctor](/ar/gateway/doctor).

  </Accordion>

  <Accordion title="كيف أشغّل Gateway مركزية مع عمال متخصصين عبر الأجهزة؟">
    النمط الشائع هو **Gateway واحدة** (مثل Raspberry Pi) بالإضافة إلى **Nodes** و**وكلاء**:

    - **Gateway (مركزية):** تملك القنوات (Signal/WhatsApp)، والتوجيه، والجلسات.
    - **Nodes (الأجهزة):** تتصل أجهزة Mac/iOS/Android كأجهزة طرفية وتعرض أدوات محلية (`system.run` و`canvas` و`camera`).
    - **الوكلاء (العمال):** عقول/مساحات عمل منفصلة لأدوار متخصصة (مثل "عمليات Hetzner" و"البيانات الشخصية").
    - **الوكلاء الفرعيون:** أنشئ عملًا في الخلفية من وكيل رئيسي عندما تريد التوازي.
    - **TUI:** اتصل بـ Gateway وبدّل بين الوكلاء/الجلسات.

    المستندات: [Nodes](/ar/nodes)، [الوصول البعيد](/ar/gateway/remote)، [توجيه الوكلاء المتعددين](/ar/concepts/multi-agent)، [الوكلاء الفرعيون](/ar/tools/subagents)، [TUI](/web/tui).

  </Accordion>

  <Accordion title="هل يمكن لمتصفح OpenClaw العمل دون واجهة مرئية؟">
    نعم. إنه خيار إعدادات:

    ```json5
    {
      browser: { headless: true },
      agents: {
        defaults: {
          sandbox: { browser: { headless: true } },
        },
      },
    }
    ```

    القيمة الافتراضية هي `false` (مع واجهة مرئية). ويكون وضع headless أكثر عرضة لإطلاق فحوصات مكافحة البوت في بعض المواقع. راجع [Browser](/ar/tools/browser).

    يستخدم وضع headless **محرك Chromium نفسه** ويعمل لمعظم عمليات الأتمتة (النماذج، والنقرات، والاستخراج، وتسجيلات الدخول). والفروق الأساسية هي:

    - لا توجد نافذة متصفح مرئية (استخدم لقطات الشاشة إذا كنت تحتاج إلى عناصر مرئية).
    - بعض المواقع أكثر تشددًا تجاه الأتمتة في وضع headless (CAPTCHAs، ومكافحة البوت).
      على سبيل المثال، كثيرًا ما يحظر X/Twitter جلسات headless.

  </Accordion>

  <Accordion title="كيف أستخدم Brave للتحكم في المتصفح؟">
    اضبط `browser.executablePath` على الملف التنفيذي الخاص بـ Brave (أو أي متصفح آخر مبني على Chromium) ثم أعد تشغيل Gateway.
    راجع أمثلة الإعدادات الكاملة في [Browser](/ar/tools/browser#use-brave-or-another-chromium-based-browser).
  </Accordion>
</AccordionGroup>

## Gateways البعيدة وNodes

<AccordionGroup>
  <Accordion title="كيف تنتشر الأوامر بين Telegram وGateway وNodes؟">
    تتعامل **Gateway** مع رسائل Telegram. تقوم Gateway بتشغيل الوكيل
    وبعد ذلك فقط تستدعي Nodes عبر **Gateway WebSocket** عند الحاجة إلى أداة Node:

    Telegram → Gateway → Agent → `node.*` → Node → Gateway → Telegram

    لا ترى Nodes حركة المزوّدات الواردة؛ فهي لا تتلقى إلا استدعاءات RPC الخاصة بـ Node.

  </Accordion>

  <Accordion title="كيف يمكن لوكيلي الوصول إلى حاسوبي إذا كانت Gateway مستضافة عن بُعد؟">
    الإجابة المختصرة: **اقرن حاسوبك كـ Node**. تعمل Gateway في مكان آخر، لكنها تستطيع
    استدعاء أدوات `node.*` (الشاشة، والكاميرا، والنظام) على جهازك المحلي عبر Gateway WebSocket.

    إعداد نموذجي:

    1. شغّل Gateway على المضيف الذي يعمل دائمًا (VPS/خادم منزلي).
    2. ضع مضيف Gateway + حاسوبك على tailnet نفسها.
    3. تأكد من أن WS الخاص بـ Gateway قابل للوصول (ربط tailnet أو نفق SSH).
    4. افتح تطبيق macOS محليًا واتصل في وضع **Remote over SSH** (أو tailnet مباشر)
       حتى يتمكن من التسجيل كـ Node.
    5. وافق على Node في Gateway:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    لا حاجة إلى جسر TCP منفصل؛ تتصل Nodes عبر Gateway WebSocket.

    تذكير أمني: يتيح إقران Node يعمل بنظام macOS تنفيذ `system.run` على ذلك الجهاز. قم فقط
    بإقران الأجهزة التي تثق بها، وراجع [الأمان](/ar/gateway/security).

    المستندات: [Nodes](/ar/nodes)، [بروتوكول Gateway](/ar/gateway/protocol)، [وضع macOS البعيد](/ar/platforms/mac/remote)، [الأمان](/ar/gateway/security).

  </Accordion>

  <Accordion title="Tailscale متصل لكنني لا أحصل على أي ردود. ماذا الآن؟">
    تحقّق من الأساسيات:

    - تعمل Gateway: `openclaw gateway status`
    - صحة Gateway: `openclaw status`
    - صحة القناة: `openclaw channels status`

    ثم تحقّق من المصادقة والتوجيه:

    - إذا كنت تستخدم Tailscale Serve، فتأكد من ضبط `gateway.auth.allowTailscale` بشكل صحيح.
    - إذا كنت تتصل عبر نفق SSH، فتأكد من أن النفق المحلي يعمل ويشير إلى المنفذ الصحيح.
    - تأكد من أن قوائم السماح لديك (DM أو المجموعة) تتضمن حسابك.

    المستندات: [Tailscale](/ar/gateway/tailscale)، [الوصول البعيد](/ar/gateway/remote)، [القنوات](/ar/channels).

  </Accordion>

  <Accordion title="هل يمكن لمثيلين من OpenClaw التحدث مع بعضهما (محلي + VPS)؟">
    نعم. لا يوجد جسر "بوت إلى بوت" مضمّن، لكن يمكنك توصيل ذلك ببضعة
    أساليب موثوقة:

    **الأبسط:** استخدم قناة دردشة عادية يمكن لكلا البوتين الوصول إليها (Telegram/Slack/WhatsApp).
    اجعل البوت A يرسل رسالة إلى البوت B، ثم دع البوت B يرد كالمعتاد.

    **جسر CLI (عام):** شغّل برنامجًا نصيًا يستدعي Gateway الأخرى باستخدام
    `openclaw agent --message ... --deliver`، مع توجيهه إلى دردشة يستمع فيها البوت
    الآخر. وإذا كان أحد البوتين على VPS بعيد، فاجعل CLI يشير إلى تلك Gateway البعيدة
    عبر SSH/Tailscale (راجع [الوصول البعيد](/ar/gateway/remote)).

    نمط مثال (يُشغّل من جهاز يمكنه الوصول إلى Gateway المستهدفة):

    ```bash
    openclaw agent --message "Hello from local bot" --deliver --channel telegram --reply-to <chat-id>
    ```

    نصيحة: أضف وسيلة حماية حتى لا يدخل البوتان في حلقة لا نهائية (إشارة فقط، أو
    قوائم سماح للقنوات، أو قاعدة "لا ترد على رسائل البوت").

    المستندات: [الوصول البعيد](/ar/gateway/remote)، [Agent CLI](/cli/agent)، [إرسال الوكيل](/ar/tools/agent-send).

  </Accordion>

  <Accordion title="هل أحتاج إلى VPS منفصلة لوكلاء متعددين؟">
    لا. يمكن لـ Gateway واحدة استضافة عدة وكلاء، لكل منهم مساحة عمله الخاصة، وافتراضيات النموذج،
    والتوجيه. وهذا هو الإعداد المعتاد، وهو أرخص بكثير وأبسط من تشغيل
    VPS واحدة لكل وكيل.

    استخدم VPS منفصلة فقط عندما تحتاج إلى عزل صارم (حدود أمان) أو إلى
    إعدادات مختلفة جدًا لا تريد مشاركتها. وبخلاف ذلك، احتفظ بـ Gateway واحدة
    واستخدم عدة وكلاء أو وكلاء فرعيين.

  </Accordion>

  <Accordion title="هل هناك فائدة من استخدام Node على حاسوبي المحمول الشخصي بدلًا من SSH من VPS؟">
    نعم - تُعد Nodes الطريقة الأساسية للوصول إلى حاسوبك المحمول من Gateway بعيدة، وهي
    تفتح أكثر من مجرد وصول إلى الصدفة. تعمل Gateway على macOS/Linux (وعلى Windows عبر WSL2) وهي
    خفيفة، لذا فإن إعدادًا شائعًا هو مضيف يعمل دائمًا بالإضافة إلى حاسوبك المحمول كـ Node.

    - **لا حاجة إلى SSH وارد.** تتصل Nodes خارجيًا بـ Gateway WebSocket وتستخدم إقران الأجهزة.
    - **عناصر تحكم أكثر أمانًا في التنفيذ.** يتم تقييد `system.run` بواسطة قوائم السماح/الموافقات الخاصة بـ Node على ذلك الحاسوب المحمول.
    - **مزيد من أدوات الأجهزة.** تعرض Nodes كلًا من `canvas` و`camera` و`screen` بالإضافة إلى `system.run`.
    - **أتمتة متصفح محلية.** أبقِ Gateway على VPS، لكن شغّل Chrome محليًا عبر مضيف Node على الحاسوب المحمول، أو اتصل بـ Chrome المحلي على المضيف عبر Chrome MCP.

    لا بأس باستخدام SSH للوصول العرضي إلى الصدفة، لكن Nodes أبسط لسير عمل الوكلاء المستمر
    وأتمتة الأجهزة.

    المستندات: [Nodes](/ar/nodes)، [Nodes CLI](/cli/nodes)، [Browser](/ar/tools/browser).

  </Accordion>

  <Accordion title="هل تقوم Nodes بتشغيل خدمة Gateway؟">
    لا. ينبغي أن تعمل **Gateway واحدة** فقط لكل مضيف ما لم تكن تشغّل عمدًا ملفات تعريف معزولة (راجع [Gateways متعددة](/ar/gateway/multiple-gateways)). تُعد Nodes أجهزة طرفية تتصل
    بـ Gateway (Nodes الخاصة بـ iOS/Android، أو "وضع Node" في تطبيق شريط القوائم على macOS). وبالنسبة إلى
    مضيفي Node بدون واجهة مرئية والتحكم عبر CLI، راجع [Node host CLI](/cli/node).

    يتطلب الأمر إعادة تشغيل كاملة لتغييرات `gateway` و`discovery` و`canvasHost`.

  </Accordion>

  <Accordion title="هل توجد طريقة API / RPC لتطبيق الإعدادات؟">
    نعم.

    - `config.schema.lookup`: افحص شجرة فرعية واحدة من الإعدادات مع عقدة المخطط السطحية الخاصة بها، وتلميح واجهة المستخدم المطابق، وملخصات الأبناء المباشرين قبل الكتابة
    - `config.get`: اجلب اللقطة الحالية + hash
    - `config.patch`: تحديث جزئي آمن (المفضّل لمعظم تعديلات RPC)؛ يعيد التحميل سريعًا عند الإمكان ويعيد التشغيل عند الحاجة
    - `config.apply`: يتحقق من الإعدادات الكاملة ويستبدلها؛ يعيد التحميل سريعًا عند الإمكان ويعيد التشغيل عند الحاجة
    - لا تزال أداة وقت التشغيل `gateway` الخاصة بالمالك فقط ترفض إعادة كتابة `tools.exec.ask` / `tools.exec.security`؛ وتُطبَّع الأسماء البديلة القديمة `tools.bash.*` إلى مسارات exec المحمية نفسها

  </Accordion>

  <Accordion title="الحد الأدنى المعقول من الإعدادات لأول تثبيت">
    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
      channels: { whatsapp: { allowFrom: ["+15555550123"] } },
    }
    ```

    يضبط هذا مساحة عملك ويقيّد من يمكنه تشغيل البوت.

  </Accordion>

  <Accordion title="كيف أُعد Tailscale على VPS وأتصل من جهاز Mac الخاص بي؟">
    الحد الأدنى من الخطوات:

    1. **ثبّت وسجّل الدخول على VPS**

       ```bash
       curl -fsSL https://tailscale.com/install.sh | sh
       sudo tailscale up
       ```

    2. **ثبّت وسجّل الدخول على جهاز Mac**
       - استخدم تطبيق Tailscale وسجّل الدخول إلى tailnet نفسها.
    3. **فعّل MagicDNS (موصى به)**
       - في وحدة تحكم إدارة Tailscale، فعّل MagicDNS حتى يحصل VPS على اسم ثابت.
    4. **استخدم اسم مضيف tailnet**
       - SSH: `ssh user@your-vps.tailnet-xxxx.ts.net`
       - Gateway WS: `ws://your-vps.tailnet-xxxx.ts.net:18789`

    إذا كنت تريد Control UI بدون SSH، فاستخدم Tailscale Serve على VPS:

    ```bash
    openclaw gateway --tailscale serve
    ```

    يُبقي هذا Gateway مربوطة بـ loopback ويعرّض HTTPS عبر Tailscale. راجع [Tailscale](/ar/gateway/tailscale).

  </Accordion>

  <Accordion title="كيف أوصل Node من جهاز Mac بـ Gateway بعيدة (Tailscale Serve)؟">
    يعرّض Serve **Gateway Control UI + WS**. وتتصل Nodes عبر نقطة نهاية Gateway WS نفسها.

    الإعداد الموصى به:

    1. **تأكد من أن VPS وMac على tailnet نفسها**.
    2. **استخدم تطبيق macOS في الوضع البعيد** (يمكن أن يكون هدف SSH هو اسم مضيف tailnet).
       سيقوم التطبيق بعمل نفق لمنفذ Gateway والاتصال كـ Node.
    3. **وافق على Node** في Gateway:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    المستندات: [بروتوكول Gateway](/ar/gateway/protocol)، [Discovery](/ar/gateway/discovery)، [وضع macOS البعيد](/ar/platforms/mac/remote).

  </Accordion>

  <Accordion title="هل ينبغي أن أثبّت على حاسوب محمول ثانٍ أم أضيف Node فقط؟">
    إذا كنت تحتاج فقط إلى **أدوات محلية** (screen/camera/exec) على الحاسوب المحمول الثاني، فأضفه كـ
    **Node**. وهذا يُبقي على Gateway واحدة ويتجنب تكرار الإعدادات. أدوات Node المحلية
    حاليًا خاصة بـ macOS فقط، لكننا نخطط لتوسيعها إلى أنظمة تشغيل أخرى.

    لا تثبّت Gateway ثانية إلا عندما تحتاج إلى **عزل صارم** أو إلى بوتين منفصلين تمامًا.

    المستندات: [Nodes](/ar/nodes)، [Nodes CLI](/cli/nodes)، [Gateways متعددة](/ar/gateway/multiple-gateways).

  </Accordion>
</AccordionGroup>

## متغيرات البيئة وتحميل ‎.env

<AccordionGroup>
  <Accordion title="كيف يحمّل OpenClaw متغيرات البيئة؟">
    يقرأ OpenClaw متغيرات البيئة من العملية الأم (الصدفة، وlaunchd/systemd، وCI، وما إلى ذلك) ويحمّل أيضًا بشكل إضافي:

    - `.env` من دليل العمل الحالي
    - ملف `.env` احتياطيًا عامًا من `~/.openclaw/.env` (ويُعرف أيضًا باسم `$OPENCLAW_STATE_DIR/.env`)

    لا يقوم أي من ملفَي `.env` بتجاوز متغيرات البيئة الموجودة مسبقًا.

    يمكنك أيضًا تعريف متغيرات بيئة مضمنة داخل الإعدادات (تُطبّق فقط إذا كانت مفقودة من بيئة العملية):

    ```json5
    {
      env: {
        OPENROUTER_API_KEY: "sk-or-...",
        vars: { GROQ_API_KEY: "gsk-..." },
      },
    }
    ```

    راجع [/environment](/ar/help/environment) لمعرفة الأولوية الكاملة والمصادر.

  </Accordion>

  <Accordion title="بدأت Gateway عبر الخدمة واختفت متغيرات البيئة الخاصة بي. ماذا الآن؟">
    هناك حلان شائعان:

    1. ضع المفاتيح المفقودة في `~/.openclaw/.env` حتى يتم التقاطها حتى عندما لا ترث الخدمة متغيرات بيئة الصدفة الخاصة بك.
    2. فعّل استيراد متغيرات الصدفة (وسيلة راحة اختيارية):

    ```json5
    {
      env: {
        shellEnv: {
          enabled: true,
          timeoutMs: 15000,
        },
      },
    }
    ```

    يشغّل هذا صدفة تسجيل الدخول الخاصة بك ويستورد فقط المفاتيح المتوقعة المفقودة (من دون أي تجاوز). المكافئات في متغيرات البيئة:
    `OPENCLAW_LOAD_SHELL_ENV=1`، `OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`.

  </Accordion>

  <Accordion title='لقد ضبطت COPILOT_GITHUB_TOKEN، لكن models status يعرض "Shell env: off." لماذا؟'>
    يعرض `openclaw models status` ما إذا كان **استيراد متغيرات بيئة الصدفة** مفعّلًا. لا تعني عبارة "Shell env: off"
    أن متغيرات البيئة الخاصة بك مفقودة - بل تعني فقط أن OpenClaw لن يحمّل
    صدفة تسجيل الدخول الخاصة بك تلقائيًا.

    إذا كانت Gateway تعمل كخدمة (launchd/systemd)، فلن ترث بيئة
    الصدفة الخاصة بك. أصلح ذلك بإحدى هذه الطرق:

    1. ضع الرمز المميز في `~/.openclaw/.env`:

       ```
       COPILOT_GITHUB_TOKEN=...
       ```

    2. أو فعّل استيراد الصدفة (`env.shellEnv.enabled: true`).
    3. أو أضفه إلى كتلة `env` في إعداداتك (يُطبّق فقط إذا كان مفقودًا).

    ثم أعد تشغيل gateway وتحقق مرة أخرى:

    ```bash
    openclaw models status
    ```

    تتم قراءة رموز Copilot من `COPILOT_GITHUB_TOKEN` (وكذلك `GH_TOKEN` / `GITHUB_TOKEN`).
    راجع [/concepts/model-providers](/ar/concepts/model-providers) و[/environment](/ar/help/environment).

  </Accordion>
</AccordionGroup>

## الجلسات والدردشات المتعددة

<AccordionGroup>
  <Accordion title="كيف أبدأ محادثة جديدة؟">
    أرسل `/new` أو `/reset` كرسالة مستقلة. راجع [إدارة الجلسات](/ar/concepts/session).
  </Accordion>

  <Accordion title="هل تُعاد تعيين الجلسات تلقائيًا إذا لم أرسل /new مطلقًا؟">
    يمكن أن تنتهي صلاحية الجلسات بعد `session.idleMinutes`، لكن هذا **معطّل افتراضيًا** (القيمة الافتراضية **0**).
    اضبطها على قيمة موجبة لتمكين انتهاء الصلاحية عند الخمول. وعند التمكين، تبدأ الرسالة **التالية**
    بعد فترة الخمول بمعرّف جلسة جديد لمفتاح الدردشة ذاك.
    وهذا لا يحذف النصوص - بل يبدأ جلسة جديدة فقط.

    ```json5
    {
      session: {
        idleMinutes: 240,
      },
    }
    ```

  </Accordion>

  <Accordion title="هل توجد طريقة لإنشاء فريق من مثيلات OpenClaw (رئيس تنفيذي واحد والعديد من الوكلاء)؟">
    نعم، عبر **توجيه الوكلاء المتعددين** و**الوكلاء الفرعيين**. يمكنك إنشاء وكيل
    منسق واحد وعدة وكلاء عاملين لهم مساحات عملهم ونماذجهم الخاصة.

    ومع ذلك، فمن الأفضل النظر إلى هذا على أنه **تجربة ممتعة**. فهو كثيف من ناحية الرموز وغالبًا
    أقل كفاءة من استخدام بوت واحد مع جلسات منفصلة. أما النموذج المعتاد الذي
    نتصوره فهو بوت واحد تتحدث إليه، مع جلسات مختلفة للعمل المتوازي. ويمكن لهذا
    البوت أيضًا إنشاء وكلاء فرعيين عند الحاجة.

    المستندات: [توجيه الوكلاء المتعددين](/ar/concepts/multi-agent)، [الوكلاء الفرعيون](/ar/tools/subagents)، [Agents CLI](/cli/agents).

  </Accordion>

  <Accordion title="لماذا تم اقتطاع السياق في منتصف المهمة؟ وكيف أمنع ذلك؟">
    يظل سياق الجلسة محدودًا بنافذة النموذج. يمكن للمحادثات الطويلة، أو نواتج الأدوات الكبيرة، أو عدد كبير من
    الملفات أن تؤدي إلى Compaction أو الاقتطاع.

    ما الذي يساعد:

    - اطلب من البوت تلخيص الحالة الحالية وكتابتها إلى ملف.
    - استخدم `/compact` قبل المهام الطويلة، و`/new` عند تبديل المواضيع.
    - احتفظ بالسياق المهم في مساحة العمل واطلب من البوت قراءته مجددًا.
    - استخدم الوكلاء الفرعيين للأعمال الطويلة أو المتوازية حتى تبقى الدردشة الرئيسية أصغر.
    - اختر نموذجًا بنافذة سياق أكبر إذا كان هذا يحدث كثيرًا.

  </Accordion>

  <Accordion title="كيف أعيد ضبط OpenClaw بالكامل لكن مع الإبقاء عليه مثبتًا؟">
    استخدم أمر إعادة الضبط:

    ```bash
    openclaw reset
    ```

    إعادة ضبط كاملة غير تفاعلية:

    ```bash
    openclaw reset --scope full --yes --non-interactive
    ```

    ثم أعد تشغيل الإعداد:

    ```bash
    openclaw onboard --install-daemon
    ```

    ملاحظات:

    - توفّر التهيئة الأولية أيضًا خيار **إعادة الضبط** إذا رأت إعدادات موجودة. راجع [التهيئة الأولية (CLI)](/ar/start/wizard).
    - إذا كنت تستخدم ملفات تعريف (`--profile` / `OPENCLAW_PROFILE`)، فأعد ضبط كل دليل حالة (الافتراضي هو `~/.openclaw-<profile>`).
    - إعادة ضبط التطوير: `openclaw gateway --dev --reset` (للتطوير فقط؛ تمسح إعدادات التطوير + بيانات الاعتماد + الجلسات + مساحة العمل).

  </Accordion>

  <Accordion title='أتلقى أخطاء "context too large" - كيف أعيد الضبط أو أُجري Compaction؟'>
    استخدم أحد الخيارات التالية:

    - **Compaction** (يُبقي المحادثة لكنه يلخّص الأدوار الأقدم):

      ```
      /compact
      ```

      أو `/compact <instructions>` لتوجيه التلخيص.

    - **إعادة الضبط** (معرّف جلسة جديد لمفتاح الدردشة نفسه):

      ```
      /new
      /reset
      ```

    إذا استمر حدوث ذلك:

    - فعّل أو اضبط **session pruning** (`agents.defaults.contextPruning`) لاقتطاع نواتج الأدوات القديمة.
    - استخدم نموذجًا بنافذة سياق أكبر.

    المستندات: [Compaction](/ar/concepts/compaction)، [Session pruning](/ar/concepts/session-pruning)، [إدارة الجلسات](/ar/concepts/session).

  </Accordion>

  <Accordion title='لماذا أرى "LLM request rejected: messages.content.tool_use.input field required"؟'>
    هذا خطأ تحقق من صحة المزوّد: أصدر النموذج كتلة `tool_use` من دون
    `input` المطلوب. ويعني هذا عادةً أن سجل الجلسة قديم أو تالف (غالبًا بعد خيوط طويلة
    أو تغيير في الأداة/المخطط).

    الحل: ابدأ جلسة جديدة باستخدام `/new` (كرسالة مستقلة).

  </Accordion>

  <Accordion title="لماذا أتلقى رسائل Heartbeat كل 30 دقيقة؟">
    تعمل Heartbeats كل **30m** افتراضيًا (**1h** عند استخدام مصادقة OAuth). اضبطها أو عطّلها:

    ```json5
    {
      agents: {
        defaults: {
          heartbeat: {
            every: "2h", // أو "0m" للتعطيل
          },
        },
      },
    }
    ```

    إذا كان `HEARTBEAT.md` موجودًا لكنه فارغ فعليًا (يحتوي فقط على أسطر فارغة وعناوين markdown
    مثل `# Heading`)، فإن OpenClaw تتخطى تشغيل Heartbeat لتوفير استدعاءات API.
    وإذا كان الملف مفقودًا، فستظل Heartbeat تعمل ويقرر النموذج ما الذي ينبغي فعله.

    تستخدم التجاوزات الخاصة بكل وكيل `agents.list[].heartbeat`. المستندات: [Heartbeat](/ar/gateway/heartbeat).

  </Accordion>

  <Accordion title='هل أحتاج إلى إضافة "حساب بوت" إلى مجموعة WhatsApp؟'>
    لا. يعمل OpenClaw على **حسابك الشخصي**، لذلك إذا كنت موجودًا في المجموعة، يستطيع OpenClaw رؤيتها.
    افتراضيًا، يتم حظر الردود في المجموعات حتى تسمح للمرسلين (`groupPolicy: "allowlist"`).

    إذا كنت تريد أن تكون **أنت فقط** القادر على تشغيل الردود في المجموعة:

    ```json5
    {
      channels: {
        whatsapp: {
          groupPolicy: "allowlist",
          groupAllowFrom: ["+15551234567"],
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="كيف أحصل على JID لمجموعة WhatsApp؟">
    الخيار 1 (الأسرع): تابع السجلات وأرسل رسالة اختبار في المجموعة:

    ```bash
    openclaw logs --follow --json
    ```

    ابحث عن `chatId` (أو `from`) المنتهي بـ `@g.us`، مثل:
    `1234567890-1234567890@g.us`.

    الخيار 2 (إذا كانت مُعدّة/موجودة في قائمة السماح بالفعل): اعرض المجموعات من الإعدادات:

    ```bash
    openclaw directory groups list --channel whatsapp
    ```

    المستندات: [WhatsApp](/ar/channels/whatsapp)، [Directory](/cli/directory)، [Logs](/cli/logs).

  </Accordion>

  <Accordion title="لماذا لا يرد OpenClaw في مجموعة؟">
    هناك سببان شائعان:

    - تفعيل الإشارة مفعّل (افتراضيًا). يجب أن تقوم بعمل @mention للبوت (أو مطابقة `mentionPatterns`).
    - قمت بإعداد `channels.whatsapp.groups` من دون `"*"` ولم تُضف المجموعة إلى قائمة السماح.

    راجع [المجموعات](/ar/channels/groups) و[رسائل المجموعات](/ar/channels/group-messages).

  </Accordion>

  <Accordion title="هل تشترك المجموعات/الخيوط في السياق مع الرسائل الخاصة؟">
    تُدمج الدردشات المباشرة في الجلسة الرئيسية افتراضيًا. أما المجموعات/القنوات فلها مفاتيح جلسات خاصة بها، كما أن موضوعات Telegram / خيوط Discord هي جلسات منفصلة. راجع [المجموعات](/ar/channels/groups) و[رسائل المجموعات](/ar/channels/group-messages).
  </Accordion>

  <Accordion title="كم عدد مساحات العمل والوكلاء التي يمكنني إنشاؤها؟">
    لا توجد حدود صارمة. العشرات (بل حتى المئات) مقبولة، لكن انتبه إلى:

    - **نمو القرص:** تعيش الجلسات + النصوص تحت `~/.openclaw/agents/<agentId>/sessions/`.
    - **تكلفة الرموز:** المزيد من الوكلاء يعني مزيدًا من استخدام النماذج المتزامن.
    - **العبء التشغيلي:** ملفات تعريف المصادقة، ومساحات العمل، وتوجيه القنوات لكل وكيل.

    نصائح:

    - احتفظ بمساحة عمل **نشطة** واحدة لكل وكيل (`agents.defaults.workspace`).
    - قلّم الجلسات القديمة (احذف JSONL أو إدخالات المخزن) إذا زاد استخدام القرص.
    - استخدم `openclaw doctor` لاكتشاف مساحات العمل الشاردة وعدم تطابق ملفات التعريف.

  </Accordion>

  <Accordion title="هل يمكنني تشغيل عدة بوتات أو دردشات في الوقت نفسه (Slack)، وكيف ينبغي أن أعد ذلك؟">
    نعم. استخدم **توجيه الوكلاء المتعددين** لتشغيل عدة وكلاء معزولين وتوجيه الرسائل الواردة حسب
    القناة/الحساب/النظير. وSlack مدعوم كقناة ويمكن ربطه بوكلاء محددين.

    الوصول إلى المتصفح قوي، لكنه ليس "افعل أي شيء يمكن للإنسان فعله" - إذ إن آليات مكافحة البوت، وCAPTCHAs، وMFA يمكن
    أن تظل تحجب الأتمتة. وللحصول على أكثر تحكم موثوق في المتصفح، استخدم Chrome MCP المحلي على المضيف،
    أو استخدم CDP على الجهاز الذي يشغّل المتصفح فعليًا.

    أفضل إعداد عملي:

    - مضيف Gateway يعمل دائمًا (VPS/Mac mini).
    - وكيل واحد لكل دور (روابط).
    - قناة/قنوات Slack مرتبطة بتلك الوكلاء.
    - متصفح محلي عبر Chrome MCP أو عبر Node عند الحاجة.

    المستندات: [توجيه الوكلاء المتعددين](/ar/concepts/multi-agent)، [Slack](/ar/channels/slack)،
    [Browser](/ar/tools/browser)، [Nodes](/ar/nodes).

  </Accordion>
</AccordionGroup>

## النماذج: الافتراضيات، والاختيار، والأسماء المستعارة، والتبديل

<AccordionGroup>
  <Accordion title='ما هو "النموذج الافتراضي"؟'>
    النموذج الافتراضي في OpenClaw هو أي نموذج تضبطه كالتالي:

    ```
    agents.defaults.model.primary
    ```

    يُشار إلى النماذج بصيغة `provider/model` (مثال: `openai/gpt-5.4`). وإذا حذفت اسم المزوّد، فسيحاول OpenClaw أولًا اسمًا مستعارًا، ثم مطابقة فريدة لمزوّد مضبوط لهذا المعرّف الدقيق للنموذج، وبعد ذلك فقط يعود إلى المزوّد الافتراضي المضبوط كمسار توافق قديم. وإذا لم يعد هذا المزوّد يعرّض النموذج الافتراضي المضبوط، فسيعود OpenClaw إلى أول مزوّد/نموذج مضبوط بدلًا من إظهار افتراضي قديم من مزوّد محذوف. ومع ذلك، ينبغي لك **ضبط `provider/model` صراحةً**.

  </Accordion>

  <Accordion title="ما النموذج الذي توصي به؟">
    **الافتراضي الموصى به:** استخدم أقوى نموذج من أحدث جيل متاح في مجموعة مزوّديك.
    **بالنسبة إلى الوكلاء المزوّدين بالأدوات أو الذين يتعاملون مع مدخلات غير موثوقة:** أعطِ قوة النموذج أولوية على التكلفة.
    **وبالنسبة إلى الدردشة الروتينية/منخفضة المخاطر:** استخدم نماذج fallback أرخص ووجّه حسب دور الوكيل.

    لدى MiniMax مستنداته الخاصة: [MiniMax](/ar/providers/minimax) و
    [النماذج المحلية](/ar/gateway/local-models).

    قاعدة عامة: استخدم **أفضل نموذج يمكنك تحمّل تكلفته** للأعمال عالية المخاطر، واستخدم نموذجًا
    أرخص للدردشة الروتينية أو الملخصات. ويمكنك توجيه النماذج لكل وكيل واستخدام الوكلاء الفرعيين من أجل
    التوازي في المهام الطويلة (كل وكيل فرعي يستهلك رموزًا). راجع [النماذج](/ar/concepts/models) و
    [الوكلاء الفرعيون](/ar/tools/subagents).

    تحذير قوي: النماذج الأضعف/المكمّمة بدرجة كبيرة أكثر عرضة لحقن
    المطالبات والسلوك غير الآمن. راجع [الأمان](/ar/gateway/security).

    لمزيد من السياق: [النماذج](/ar/concepts/models).

  </Accordion>

  <Accordion title="كيف أبدّل النماذج من دون مسح إعداداتي؟">
    استخدم **أوامر النموذج** أو عدّل حقول **النموذج** فقط. وتجنّب استبدال الإعدادات بالكامل.

    الخيارات الآمنة:

    - `/model` في الدردشة (سريع، لكل جلسة)
    - `openclaw models set ...` (يحدّث إعدادات النموذج فقط)
    - `openclaw configure --section model` (تفاعلي)
    - عدّل `agents.defaults.model` في `~/.openclaw/openclaw.json`

    تجنّب `config.apply` مع كائن جزئي ما لم تكن تنوي استبدال الإعدادات كلها.
    وبالنسبة إلى تعديلات RPC، افحص أولًا باستخدام `config.schema.lookup` وفضّل `config.patch`. تعطيك حمولة lookup المسار المُطبّع، ووثائق/قيود المخطط السطحية، وملخصات الأبناء المباشرين
    للتحديثات الجزئية.
    وإذا كنت قد كتبت فوق الإعدادات بالفعل، فاستعدها من نسخة احتياطية أو أعد تشغيل `openclaw doctor` للإصلاح.

    المستندات: [النماذج](/ar/concepts/models)، [التهيئة](/cli/configure)، [الإعدادات](/cli/config)، [Doctor](/ar/gateway/doctor).

  </Accordion>

  <Accordion title="هل يمكنني استخدام نماذج مستضافة ذاتيًا (llama.cpp, vLLM, Ollama)؟">
    نعم. يُعد Ollama أسهل مسار للنماذج المحلية.

    أسرع إعداد:

    1. ثبّت Ollama من `https://ollama.com/download`
    2. اسحب نموذجًا محليًا مثل `ollama pull gemma4`
    3. إذا كنت تريد نماذج سحابية أيضًا، فشغّل `ollama signin`
    4. شغّل `openclaw onboard` واختر `Ollama`
    5. اختر `Local` أو `Cloud + Local`

    ملاحظات:

    - يمنحك `Cloud + Local` نماذج سحابية بالإضافة إلى نماذج Ollama المحلية
    - النماذج السحابية مثل `kimi-k2.5:cloud` لا تحتاج إلى سحب محلي
    - للتبديل اليدوي، استخدم `openclaw models list` و`openclaw models set ollama/<model>`

    ملاحظة أمنية: النماذج الأصغر أو المكمّمة بشدة أكثر عرضة لحقن
    المطالبات. نوصي بشدة باستخدام **نماذج كبيرة** لأي بوت يمكنه استخدام الأدوات.
    وإذا كنت لا تزال تريد نماذج صغيرة، ففعّل العزل وقوائم السماح الصارمة للأدوات.

    المستندات: [Ollama](/ar/providers/ollama)، [النماذج المحلية](/ar/gateway/local-models)،
    [مزوّدو النماذج](/ar/concepts/model-providers)، [الأمان](/ar/gateway/security)،
    [العزل](/ar/gateway/sandboxing).

  </Accordion>

  <Accordion title="ما النماذج التي يستخدمها OpenClaw وFlawd وKrill؟">
    - قد تختلف هذه البيئات وقد تتغير مع مرور الوقت؛ ولا توجد توصية ثابتة بمزوّد معين.
    - تحقّق من إعداد وقت التشغيل الحالي على كل gateway باستخدام `openclaw models status`.
    - بالنسبة إلى الوكلاء الحساسين أمنيًا/الممكّنين بالأدوات، استخدم أقوى نموذج من أحدث جيل متاح.
  </Accordion>

  <Accordion title="كيف أبدّل النماذج أثناء التشغيل (من دون إعادة تشغيل)؟">
    استخدم الأمر `/model` كرسالة مستقلة:

    ```
    /model sonnet
    /model opus
    /model gpt
    /model gpt-mini
    /model gemini
    /model gemini-flash
    /model gemini-flash-lite
    ```

    هذه هي الأسماء المستعارة المضمّنة. ويمكن إضافة أسماء مستعارة مخصصة عبر `agents.defaults.models`.

    يمكنك عرض النماذج المتاحة باستخدام `/model` أو `/model list` أو `/model status`.

    يعرض `/model` (وكذلك `/model list`) منتقيًا مضغوطًا ومرقّمًا. اختر بالرقم:

    ```
    /model 3
    ```

    يمكنك أيضًا فرض ملف تعريف مصادقة محدد للمزوّد (لكل جلسة):

    ```
    /model opus@anthropic:default
    /model opus@anthropic:work
    ```

    نصيحة: يعرض `/model status` الوكيل النشط، وملف `auth-profiles.json` المستخدم، وملف تعريف المصادقة الذي ستجري تجربته بعد ذلك.
    كما يعرض نقطة نهاية المزوّد المضبوطة (`baseUrl`) ووضع API (`api`) عند توفرهما.

    **كيف أفك التثبيت عن ملف تعريف قمت بتعيينه باستخدام @profile؟**

    أعد تشغيل `/model` **من دون** اللاحقة `@profile`:

    ```
    /model anthropic/claude-opus-4-6
    ```

    وإذا كنت تريد العودة إلى الافتراضي، فاختره من `/model` (أو أرسل `/model <default provider/model>`).
    استخدم `/model status` للتأكد من ملف تعريف المصادقة النشط.

  </Accordion>

  <Accordion title="هل يمكنني استخدام GPT 5.2 للمهام اليومية وCodex 5.3 للبرمجة؟">
    نعم. اضبط أحدهما كافتراضي وبدّل حسب الحاجة:

    - **تبديل سريع (لكل جلسة):** `/model gpt-5.4` للمهام اليومية، و`/model openai-codex/gpt-5.4` للبرمجة باستخدام Codex OAuth.
    - **افتراضي + تبديل:** اضبط `agents.defaults.model.primary` على `openai/gpt-5.4`، ثم بدّل إلى `openai-codex/gpt-5.4` عند البرمجة (أو العكس).
    - **الوكلاء الفرعيون:** وجّه مهام البرمجة إلى وكلاء فرعيين لديهم نموذج افتراضي مختلف.

    راجع [النماذج](/ar/concepts/models) و[أوامر الشرطة المائلة](/ar/tools/slash-commands).

  </Accordion>

  <Accordion title="كيف أضبط fast mode لـ GPT 5.4؟">
    استخدم إما تبديلًا على مستوى الجلسة أو افتراضيًا في الإعدادات:

    - **لكل جلسة:** أرسل `/fast on` بينما تستخدم الجلسة `openai/gpt-5.4` أو `openai-codex/gpt-5.4`.
    - **افتراضي لكل نموذج:** اضبط `agents.defaults.models["openai/gpt-5.4"].params.fastMode` على `true`.
    - **ينطبق على Codex OAuth أيضًا:** إذا كنت تستخدم أيضًا `openai-codex/gpt-5.4`، فاضبط العلامة نفسها هناك.

    مثال:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "openai/gpt-5.4": {
              params: {
                fastMode: true,
              },
            },
            "openai-codex/gpt-5.4": {
              params: {
                fastMode: true,
              },
            },
          },
        },
      },
    }
    ```

    بالنسبة إلى OpenAI، يرتبط fast mode بالقيمة `service_tier = "priority"` في طلبات Responses الأصلية المدعومة. وتتغلب إعدادات `/fast` الخاصة بالجلسة على افتراضيات الإعدادات.

    راجع [التفكير ووضع fast](/ar/tools/thinking) و[OpenAI fast mode](/ar/providers/openai#openai-fast-mode).

  </Accordion>

  <Accordion title='لماذا أرى "Model ... is not allowed" ثم لا يوجد رد؟'>
    إذا كان `agents.defaults.models` مضبوطًا، فإنه يصبح **قائمة السماح** لأمر `/model` وأي
    تجاوزات على مستوى الجلسة. ويؤدي اختيار نموذج غير موجود في تلك القائمة إلى إرجاع:

    ```
    Model "provider/model" is not allowed. Use /model to list available models.
    ```

    ويُعاد هذا الخطأ **بدلًا من** رد عادي. الحل: أضف النموذج إلى
    `agents.defaults.models`، أو أزل قائمة السماح، أو اختر نموذجًا من `/model list`.

  </Accordion>

  <Accordion title='لماذا أرى "Unknown model: minimax/MiniMax-M2.7"؟'>
    هذا يعني أن **المزوّد غير مضبوط** (لم يتم العثور على إعدادات مزوّد MiniMax أو
    ملف تعريف مصادقة)، لذلك لا يمكن حل النموذج.

    قائمة التحقق للإصلاح:

    1. حدّث إلى إصدار حديث من OpenClaw (أو شغّل من المصدر `main`)، ثم أعد تشغيل gateway.
    2. تأكد من إعداد MiniMax (عبر المعالج أو JSON)، أو من وجود مصادقة MiniMax
       في متغيرات البيئة/ملفات تعريف المصادقة بحيث يمكن حقن المزوّد المطابق
       (`MINIMAX_API_KEY` من أجل `minimax`، و`MINIMAX_OAUTH_TOKEN` أو OAuth الخاص بـ MiniMax المخزن
       من أجل `minimax-portal`).
    3. استخدم معرّف النموذج الدقيق (مع مراعاة حالة الأحرف) لمسار المصادقة لديك:
       `minimax/MiniMax-M2.7` أو `minimax/MiniMax-M2.7-highspeed` لإعداد
       مفتاح API، أو `minimax-portal/MiniMax-M2.7` /
       `minimax-portal/MiniMax-M2.7-highspeed` لإعداد OAuth.
    4. شغّل:

       ```bash
       openclaw models list
       ```

       واختر من القائمة (أو `/model list` في الدردشة).

    راجع [MiniMax](/ar/providers/minimax) و[النماذج](/ar/concepts/models).

  </Accordion>

  <Accordion title="هل يمكنني استخدام MiniMax كافتراضي وOpenAI للمهام المعقدة؟">
    نعم. استخدم **MiniMax كافتراضي** وبدّل النماذج **لكل جلسة** عند الحاجة.
    إن fallback مخصصة **للأخطاء**، لا "للمهام الصعبة"، لذا استخدم `/model` أو وكيلًا منفصلًا.

    **الخيار A: التبديل لكل جلسة**

    ```json5
    {
      env: { MINIMAX_API_KEY: "sk-...", OPENAI_API_KEY: "sk-..." },
      agents: {
        defaults: {
          model: { primary: "minimax/MiniMax-M2.7" },
          models: {
            "minimax/MiniMax-M2.7": { alias: "minimax" },
            "openai/gpt-5.4": { alias: "gpt" },
          },
        },
      },
    }
    ```

    ثم:

    ```
    /model gpt
    ```

    **الخيار B: وكلاء منفصلون**

    - الوكيل A الافتراضي: MiniMax
    - الوكيل B الافتراضي: OpenAI
    - وجّه حسب الوكيل أو استخدم `/agent` للتبديل

    المستندات: [النماذج](/ar/concepts/models)، [توجيه الوكلاء المتعددين](/ar/concepts/multi-agent)، [MiniMax](/ar/providers/minimax)، [OpenAI](/ar/providers/openai).

  </Accordion>

  <Accordion title="هل opus / sonnet / gpt اختصارات مضمّنة؟">
    نعم. يوفّر OpenClaw بعض الاختصارات الافتراضية (تُطبّق فقط عندما يكون النموذج موجودًا في `agents.defaults.models`):

    - `opus` ← `anthropic/claude-opus-4-6`
    - `sonnet` ← `anthropic/claude-sonnet-4-6`
    - `gpt` ← `openai/gpt-5.4`
    - `gpt-mini` ← `openai/gpt-5.4-mini`
    - `gpt-nano` ← `openai/gpt-5.4-nano`
    - `gemini` ← `google/gemini-3.1-pro-preview`
    - `gemini-flash` ← `google/gemini-3-flash-preview`
    - `gemini-flash-lite` ← `google/gemini-3.1-flash-lite-preview`

    إذا ضبطت اسمًا مستعارًا خاصًا بك بالاسم نفسه، فستكون قيمتك هي الغالبة.

  </Accordion>

  <Accordion title="كيف أعرّف/أتجاوز اختصارات النماذج (الأسماء المستعارة)؟">
    تأتي الأسماء المستعارة من `agents.defaults.models.<modelId>.alias`. مثال:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "anthropic/claude-opus-4-6" },
          models: {
            "anthropic/claude-opus-4-6": { alias: "opus" },
            "anthropic/claude-sonnet-4-6": { alias: "sonnet" },
            "anthropic/claude-haiku-4-5": { alias: "haiku" },
          },
        },
      },
    }
    ```

    بعد ذلك سيُحل `/model sonnet` (أو `/<alias>` عندما يكون مدعومًا) إلى معرّف النموذج ذاك.

  </Accordion>

  <Accordion title="كيف أضيف نماذج من مزوّدين آخرين مثل OpenRouter أو Z.AI؟">
    OpenRouter (الدفع لكل رمز؛ نماذج كثيرة):

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "openrouter/anthropic/claude-sonnet-4-6" },
          models: { "openrouter/anthropic/claude-sonnet-4-6": {} },
        },
      },
      env: { OPENROUTER_API_KEY: "sk-or-..." },
    }
    ```

    Z.AI (نماذج GLM):

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "zai/glm-5" },
          models: { "zai/glm-5": {} },
        },
      },
      env: { ZAI_API_KEY: "..." },
    }
    ```

    إذا أشرت إلى مزوّد/نموذج لكن مفتاح المزوّد المطلوب مفقود، فستتلقى خطأ مصادقة وقت التشغيل (مثل `No API key found for provider "zai"`).

    **لم يتم العثور على مفتاح API للمزوّد بعد إضافة وكيل جديد**

    يعني هذا عادةً أن **الوكيل الجديد** لديه مخزن مصادقة فارغ. تكون المصادقة لكل وكيل على حدة
    وتُخزّن في:

    ```
    ~/.openclaw/agents/<agentId>/agent/auth-profiles.json
    ```

    خيارات الإصلاح:

    - شغّل `openclaw agents add <id>` واضبط المصادقة أثناء المعالج.
    - أو انسخ `auth-profiles.json` من `agentDir` الخاص بالوكيل الرئيسي إلى `agentDir` الخاص بالوكيل الجديد.

    لا **تعِد استخدام** `agentDir` بين الوكلاء؛ فهذا يسبب تعارضات في المصادقة/الجلسات.

  </Accordion>
</AccordionGroup>

## fallback للنماذج و"All models failed"

<AccordionGroup>
  <Accordion title="كيف تعمل آلية fallback؟">
    تحدث آلية fallback على مرحلتين:

    1. **تدوير ملفات تعريف المصادقة** داخل المزوّد نفسه.
    2. **fallback للنموذج** إلى النموذج التالي في `agents.defaults.model.fallbacks`.

    تُطبّق فترات انتظار على ملفات التعريف الفاشلة (تراجع أسي)، حتى يتمكن OpenClaw من مواصلة الرد حتى عندما يكون أحد المزوّدين مقيّدًا بالمعدل أو فاشلًا مؤقتًا.

    يتضمن حوض تحديد المعدل أكثر من مجرد استجابات `429` العادية. كما يتعامل OpenClaw
    أيضًا مع رسائل مثل `Too many concurrent requests`،
    و`ThrottlingException`، و`concurrency limit reached`،
    و`workers_ai ... quota limit exceeded`، و`resource exhausted`، وحدود
    نوافذ الاستخدام الدورية (`weekly/monthly limit reached`) على أنها
    حدود معدل تستحق fallback.

    بعض الاستجابات التي تبدو مرتبطة بالفوترة ليست `402`، وبعض استجابات HTTP `402`
    تبقى أيضًا في هذا الحوض المؤقت. وإذا أعاد المزوّد
    نص فوترة صريحًا على `401` أو `403`، فلا يزال OpenClaw قادرًا على إبقائه في
    مسار الفوترة، لكن مطابِقات النصوص الخاصة بكل مزوّد تبقى محصورة في
    المزوّد الذي يملكها (مثل OpenRouter `Key limit exceeded`). أما إذا كانت رسالة `402`
    تبدو بدلًا من ذلك كحد نافذة استخدام قابل لإعادة المحاولة أو
    حد إنفاق للمؤسسة/مساحة العمل (`daily limit reached, resets tomorrow`،
    `organization spending limit exceeded`)، فإن OpenClaw يتعامل معها على أنها
    `rate_limit`، وليس تعطيل فوترة طويلًا.

    تختلف أخطاء تجاوز السياق عن ذلك: فالتواقيع مثل
    `request_too_large`، و`input exceeds the maximum number of tokens`،
    و`input token count exceeds the maximum number of input tokens`،
    و`input is too long for the model`، أو `ollama error: context length
    exceeded` تبقى على مسار Compaction/إعادة المحاولة بدلًا من التقدم إلى fallback
    للنموذج.

    إن نصوص أخطاء الخادم العامة أضيق عمدًا من "أي شيء يحتوي على
    unknown/error". يعامل OpenClaw الأشكال المؤقتة المحصورة بالمزوّد
    مثل Anthropic `An unknown error occurred` المجردة، وOpenRouter
    `Provider returned error` المجردة، وأخطاء سبب التوقف مثل `Unhandled stop reason:
    error`، وحمولات JSON `api_error` ذات نصوص الخادم المؤقتة
    (`internal server error`، `unknown error, 520`، `upstream error`، `backend
    error`)، وأخطاء انشغال المزوّد مثل `ModelNotReadyException` على أنها
    إشارات مهلة/تحميل زائد تستحق fallback عندما يكون سياق المزوّد
    مطابقًا.
    أما نص fallback الداخلي العام مثل `LLM request failed with an unknown
    error.` فيبقى محافظًا ولا يطلق fallback للنموذج بمفرده.

  </Accordion>

  <Accordion title='ماذا يعني "No credentials found for profile anthropic:default"؟'>
    يعني ذلك أن النظام حاول استخدام معرّف ملف تعريف المصادقة `anthropic:default`، لكنه لم يتمكن من العثور على بيانات اعتماد له في مخزن المصادقة المتوقع.

    **قائمة التحقق للإصلاح:**

    - **أكد مكان وجود ملفات تعريف المصادقة** (المسارات الجديدة مقابل القديمة)
      - الحالي: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
      - القديم: `~/.openclaw/agent/*` (يتم ترحيله بواسطة `openclaw doctor`)
    - **أكد أن متغير البيئة الخاص بك محمّل بواسطة Gateway**
      - إذا كنت قد ضبطت `ANTHROPIC_API_KEY` في صدفتك لكنك تشغّل Gateway عبر systemd/launchd، فقد لا يرثه. ضعه في `~/.openclaw/.env` أو فعّل `env.shellEnv`.
    - **تأكد من أنك تعدّل الوكيل الصحيح**
      - تعني إعدادات الوكلاء المتعددين أنه يمكن أن توجد ملفات `auth-profiles.json` متعددة.
    - **تحقق سريعًا من حالة النموذج/المصادقة**
      - استخدم `openclaw models status` لرؤية النماذج المضبوطة وما إذا كانت المزوّدات مصادَقًا عليها.

    **قائمة التحقق للإصلاح لرسالة "No credentials found for profile anthropic"**

    يعني هذا أن التشغيل مثبت على ملف تعريف مصادقة Anthropic، لكن Gateway
    لا تستطيع العثور عليه في مخزن المصادقة الخاص بها.

    - **استخدم Claude CLI**
      - شغّل `openclaw models auth login --provider anthropic --method cli --set-default` على مضيف gateway.
    - **إذا كنت تريد استخدام مفتاح API بدلًا من ذلك**
      - ضع `ANTHROPIC_API_KEY` في `~/.openclaw/.env` على **مضيف gateway**.
      - امسح أي ترتيب مثبّت يفرض ملف تعريف مفقود:

        ```bash
        openclaw models auth order clear --provider anthropic
        ```

    - **تأكد من أنك تشغّل الأوامر على مضيف gateway**
      - في الوضع البعيد، تعيش ملفات تعريف المصادقة على جهاز gateway، وليس على حاسوبك المحمول.

  </Accordion>

  <Accordion title="لماذا حاول أيضًا Google Gemini وفشل؟">
    إذا كانت إعدادات النموذج لديك تتضمن Google Gemini كـ fallback (أو إذا بدّلت إلى اختصار Gemini)، فسيحاول OpenClaw استخدامه أثناء fallback للنموذج. وإذا لم تكن قد أعددت بيانات اعتماد Google، فسترى `No API key found for provider "google"`.

    الحل: إما أن توفّر مصادقة Google، أو أن تزيل/تتجنب نماذج Google في `agents.defaults.model.fallbacks` / الأسماء المستعارة حتى لا يتجه fallback إليها.

    **LLM request rejected: thinking signature required (Google Antigravity)**

    السبب: يحتوي سجل الجلسة على **كتل thinking من دون تواقيع** (غالبًا من
    بث متوقف/جزئي). يتطلب Google Antigravity وجود تواقيع لكتل thinking.

    الحل: يقوم OpenClaw الآن بإزالة كتل thinking غير الموقعة من أجل Google Antigravity Claude. وإذا استمرت المشكلة، فابدأ **جلسة جديدة** أو اضبط `/thinking off` لذلك الوكيل.

  </Accordion>
</AccordionGroup>

## ملفات تعريف المصادقة: ما هي وكيف تديرها

ذو صلة: [/concepts/oauth](/ar/concepts/oauth) (تدفقات OAuth، وتخزين الرموز، وأنماط الحسابات المتعددة)

<AccordionGroup>
  <Accordion title="ما هو ملف تعريف المصادقة؟">
    ملف تعريف المصادقة هو سجل بيانات اعتماد مسمى (OAuth أو مفتاح API) مرتبط بمزوّد. تعيش الملفات في:

    ```
    ~/.openclaw/agents/<agentId>/agent/auth-profiles.json
    ```

  </Accordion>

  <Accordion title="ما معرّفات ملفات التعريف النموذجية؟">
    يستخدم OpenClaw معرّفات مسبوقة باسم المزوّد مثل:

    - `anthropic:default` (شائع عندما لا توجد هوية بريد إلكتروني)
    - `anthropic:<email>` لهويات OAuth
    - معرّفات مخصصة تختارها أنت (مثل `anthropic:work`)

  </Accordion>

  <Accordion title="هل يمكنني التحكم في ملف تعريف المصادقة الذي تتم تجربته أولًا؟">
    نعم. تدعم الإعدادات بيانات وصفية اختيارية لملفات التعريف وترتيبًا لكل مزوّد (`auth.order.<provider>`). وهذا **لا** يخزّن الأسرار؛ بل يربط المعرّفات بالمزوّد/الوضع ويضبط ترتيب التدوير.

    قد يتخطى OpenClaw مؤقتًا ملف تعريف إذا كان في **فترة انتظار** قصيرة (حدود معدل/مهل/فشل مصادقة) أو في حالة **تعطيل** أطول (فوترة/رصيد غير كافٍ). ولتفحص ذلك، شغّل `openclaw models status --json` وتحقق من `auth.unusableProfiles`. الضبط: `auth.cooldowns.billingBackoffHours*`.

    يمكن أن تكون فترات انتظار حدود المعدل محصورة بالنموذج. فقد يظل ملف تعريف في فترة انتظار
    لنموذج واحد لكنه يظل قابلًا للاستخدام لنموذج شقيق على المزوّد نفسه،
    بينما تظل نوافذ الفوترة/التعطيل تحظر ملف التعريف كله.

    يمكنك أيضًا ضبط تجاوز ترتيب **لكل وكيل** (مخزن في `auth-state.json` الخاص بذلك الوكيل) عبر CLI:

    ```bash
    # يُستخدم الوكيل الافتراضي المضبوط افتراضيًا (احذف --agent)
    openclaw models auth order get --provider anthropic

    # ثبّت التدوير على ملف تعريف واحد (جرّب هذا فقط)
    openclaw models auth order set --provider anthropic anthropic:default

    # أو اضبط ترتيبًا صريحًا (fallback داخل المزوّد)
    openclaw models auth order set --provider anthropic anthropic:work anthropic:default

    # امسح التجاوز (ارجع إلى config auth.order / round-robin)
    openclaw models auth order clear --provider anthropic
    ```

    لاستهداف وكيل محدد:

    ```bash
    openclaw models auth order set --provider anthropic --agent main anthropic:default
    ```

    وللتحقق مما سيُجرَّب فعليًا، استخدم:

    ```bash
    openclaw models status --probe
    ```

    إذا تم حذف ملف تعريف مخزّن من الترتيب الصريح، فسيعرض probe
    `excluded_by_auth_order` لذلك الملف بدلًا من تجربته بصمت.

  </Accordion>

  <Accordion title="OAuth مقابل مفتاح API - ما الفرق؟">
    يدعم OpenClaw كلاهما:

    - **OAuth** غالبًا ما يستفيد من وصول الاشتراك (حيثما ينطبق).
    - **مفاتيح API** تستخدم فوترة الدفع لكل رمز.

    يدعم المعالج صراحةً Anthropic Claude CLI، وOpenAI Codex OAuth، ومفاتيح API.

  </Accordion>
</AccordionGroup>

## Gateway: المنافذ، و"already running"، والوضع البعيد

<AccordionGroup>
  <Accordion title="ما المنفذ الذي تستخدمه Gateway؟">
    يتحكم `gateway.port` في المنفذ المتعدد الإرسال الواحد لكل من WebSocket + HTTP (Control UI، والخطافات، وما إلى ذلك).

    ترتيب الأولوية:

    ```
    --port > OPENCLAW_GATEWAY_PORT > gateway.port > default 18789
    ```

  </Accordion>

  <Accordion title='لماذا يقول openclaw gateway status "Runtime: running" لكن "RPC probe: failed"؟'>
    لأن "running" هو منظور **المشرف** (launchd/systemd/schtasks). أما RPC probe فهو أن CLI تتصل فعليًا بـ gateway WebSocket وتستدعي `status`.

    استخدم `openclaw gateway status` وركّز على هذه الأسطر:

    - `Probe target:` (عنوان URL الذي استخدمه probe فعليًا)
    - `Listening:` (ما هو مربوط فعليًا على المنفذ)
    - `Last gateway error:` (سبب جذري شائع عندما تكون العملية حية لكن المنفذ لا يستمع)

  </Accordion>

  <Accordion title='لماذا يعرض openclaw gateway status قيمتين مختلفتين لـ "Config (cli)" و"Config (service)"؟'>
    أنت تعدّل ملف إعدادات واحدًا بينما تشغّل الخدمة ملفًا آخر (غالبًا بسبب عدم تطابق `--profile` / `OPENCLAW_STATE_DIR`).

    الحل:

    ```bash
    openclaw gateway install --force
    ```

    شغّل ذلك من البيئة / `--profile` نفسها التي تريد أن تستخدمها الخدمة.

  </Accordion>

  <Accordion title='ماذا يعني "another gateway instance is already listening"؟'>
    يفرض OpenClaw قفلًا في وقت التشغيل من خلال ربط مستمع WebSocket فورًا عند بدء التشغيل (الافتراضي `ws://127.0.0.1:18789`). وإذا فشل الربط بسبب `EADDRINUSE`، فإنه يرمي `GatewayLockError` مشيرًا إلى أن مثيلًا آخر يستمع بالفعل.

    الحل: أوقف المثيل الآخر، أو حرّر المنفذ، أو شغّل باستخدام `openclaw gateway --port <port>`.

  </Accordion>

  <Accordion title="كيف أشغّل OpenClaw في الوضع البعيد (يتصل العميل بـ Gateway في مكان آخر)؟">
    اضبط `gateway.mode: "remote"` وأشر إلى عنوان URL بعيد لـ WebSocket، اختياريًا مع بيانات اعتماد بعيدة ذات سر مشترك:

    ```json5
    {
      gateway: {
        mode: "remote",
        remote: {
          url: "ws://gateway.tailnet:18789",
          token: "your-token",
          password: "your-password",
        },
      },
    }
    ```

    ملاحظات:

    - لا يبدأ `openclaw gateway` إلا عندما تكون `gateway.mode` مساوية لـ `local` (أو إذا مررت علامة التجاوز).
    - يراقب تطبيق macOS ملف الإعدادات ويبدّل الأوضاع مباشرة عند تغيّر هذه القيم.
    - إن `gateway.remote.token` / `.password` هما بيانات اعتماد بعيدة على جانب العميل فقط؛ ولا يفعّلان مصادقة Gateway المحلية بمفردهما.

  </Accordion>

  <Accordion title='تقول Control UI "unauthorized" (أو تستمر في إعادة الاتصال). ماذا الآن؟'>
    مسار مصادقة gateway وطريقة المصادقة في واجهة المستخدم غير متطابقين.

    حقائق (من الشيفرة):

    - تحتفظ Control UI بالرمز المميز في `sessionStorage` لجلسة علامة تبويب المتصفح الحالية وعنوان URL الخاص بـ gateway المحددة، لذلك يستمر التحديث في علامة التبويب نفسها في العمل من دون استعادة التخزين الدائم الطويل الأمد للرمز في `localStorage`.
    - عند `AUTH_TOKEN_MISMATCH`، يمكن للعملاء الموثوقين محاولة إعادة محاولة واحدة محدودة باستخدام رمز جهاز مخزّن مؤقتًا عندما تعيد gateway تلميحات إعادة المحاولة (`canRetryWithDeviceToken=true`، `recommendedNextStep=retry_with_device_token`).
    - تعيد محاولة الرمز المخزّن مؤقتًا الآن استخدام النطاقات الموافق عليها المخزنة مع رمز الجهاز. أما المستدعون الذين يمررون `deviceToken` صريحًا / أو `scopes` صريحة فيحتفظون بمجموعة النطاقات المطلوبة بدلًا من وراثة النطاقات المخزنة.
    - خارج مسار إعادة المحاولة هذا، تكون أولوية مصادقة الاتصال هي: الرمز/كلمة المرور الصريحان للسر المشترك أولًا، ثم `deviceToken` الصريح، ثم رمز الجهاز المخزن، ثم bootstrap token.
    - تكون فحوصات نطاق bootstrap token ذات بادئات بحسب الدور. ولا تفي قائمة السماح المضمّنة الخاصة بـ bootstrap operator إلا بطلبات operator؛ أما أدوار node أو غير operator فتظل تحتاج إلى نطاقات تحت بادئة دورها الخاص.

    الحل:

    - الأسرع: `openclaw dashboard` (يطبع + ينسخ عنوان URL الخاص بلوحة المعلومات، ويحاول الفتح؛ ويعرض تلميح SSH إذا كان بدون واجهة مرئية).
    - إذا لم يكن لديك رمز مميز بعد: `openclaw doctor --generate-gateway-token`.
    - إذا كان الاتصال بعيدًا، فأنشئ نفقًا أولًا: `ssh -N -L 18789:127.0.0.1:18789 user@host` ثم افتح `http://127.0.0.1:18789/`.
    - وضع السر المشترك: اضبط `gateway.auth.token` / `OPENCLAW_GATEWAY_TOKEN` أو `gateway.auth.password` / `OPENCLAW_GATEWAY_PASSWORD`، ثم ألصق السر المطابق في إعدادات Control UI.
    - وضع Tailscale Serve: تأكد من تمكين `gateway.auth.allowTailscale` وأنك تفتح عنوان URL الخاص بـ Serve، وليس عنوان loopback/tailnet خامًا يتجاوز ترويسات هوية Tailscale.
    - وضع trusted-proxy: تأكد من أنك تمر عبر الوكيل المدرك للهوية غير loopback المضبوط، وليس عبر وكيل loopback على المضيف نفسه أو عنوان URL خام لـ gateway.
    - إذا استمر عدم التطابق بعد إعادة المحاولة الواحدة، فقم بتدوير/إعادة الموافقة على رمز الجهاز المقترن:
      - `openclaw devices list`
      - `openclaw devices rotate --device <id> --role operator`
    - إذا أخبرك استدعاء التدوير ذاك بأنه رُفض، فتحقق من أمرين:
      - لا تستطيع جلسات الأجهزة المقترنة تدوير إلا **أجهزتها الخاصة** ما لم تكن تملك أيضًا `operator.admin`
      - لا يمكن لقيم `--scope` الصريحة أن تتجاوز نطاقات operator الحالية الخاصة بالمستدعي
    - ما زلت عالقًا؟ شغّل `openclaw status --all` واتبع [استكشاف الأخطاء وإصلاحها](/ar/gateway/troubleshooting). راجع [لوحة المعلومات](/web/dashboard) لمعرفة تفاصيل المصادقة.

  </Accordion>

  <Accordion title="لقد ضبطت gateway.bind على tailnet لكنه لا يستطيع الربط ولا شيء يستمع">
    يختار الربط `tailnet` عنوان Tailscale IP من واجهات الشبكة لديك (`100.64.0.0/10`). وإذا لم يكن الجهاز موجودًا على Tailscale (أو إذا كانت الواجهة متوقفة)، فلن يوجد شيء ليرتبط به.

    الحل:

    - شغّل Tailscale على ذلك المضيف (حتى يحصل على عنوان 100.x)، أو
    - بدّل إلى `gateway.bind: "loopback"` / `"lan"`.

    ملاحظة: إن `tailnet` صريح. بينما يفضّل `auto` loopback؛ لذا استخدم `gateway.bind: "tailnet"` عندما تريد ربطًا يقتصر على tailnet فقط.

  </Accordion>

  <Accordion title="هل يمكنني تشغيل عدة Gateways على المضيف نفسه؟">
    عادةً لا - يمكن لـ Gateway واحدة تشغيل عدة قنوات مراسلة وعدة وكلاء. استخدم عدة Gateways فقط عندما تحتاج إلى التكرار (مثل rescue bot) أو إلى عزل صارم.

    نعم، لكن يجب أن تعزل:

    - `OPENCLAW_CONFIG_PATH` (إعدادات لكل مثيل)
    - `OPENCLAW_STATE_DIR` (حالة لكل مثيل)
    - `agents.defaults.workspace` (عزل مساحة العمل)
    - `gateway.port` (منافذ فريدة)

    إعداد سريع (موصى به):

    - استخدم `openclaw --profile <name> ...` لكل مثيل (ينشئ تلقائيًا `~/.openclaw-<name>`).
    - اضبط `gateway.port` فريدًا في إعدادات كل ملف تعريف (أو مرّر `--port` للتشغيلات اليدوية).
    - ثبّت خدمة لكل ملف تعريف: `openclaw --profile <name> gateway install`.

    تضيف ملفات التعريف أيضًا لواحق إلى أسماء الخدمات (`ai.openclaw.<profile>`؛ أو القديمة `com.openclaw.*`، و`openclaw-gateway-<profile>.service`، و`OpenClaw Gateway (<profile>)`).
    الدليل الكامل: [Gateways متعددة](/ar/gateway/multiple-gateways).

  </Accordion>

  <Accordion title='ماذا يعني "invalid handshake" / الرمز 1008؟'>
    إن Gateway هي **خادم WebSocket**، وهي تتوقع أن تكون أول رسالة
    هي إطار `connect`. وإذا استقبلت أي شيء آخر، فإنها تغلق الاتصال
    بالرمز **1008** (مخالفة للسياسة).

    الأسباب الشائعة:

    - فتحت عنوان URL الخاص بـ **HTTP** في متصفح (`http://...`) بدلًا من عميل WS.
    - استخدمت المنفذ أو المسار الخطأ.
    - قام وكيل أو نفق بإزالة ترويسات المصادقة أو أرسل طلبًا ليس خاصًا بـ Gateway.

    حلول سريعة:

    1. استخدم عنوان URL الخاص بـ WS: `ws://<host>:18789` (أو `wss://...` إذا كان HTTPS).
    2. لا تفتح منفذ WS في علامة تبويب متصفح عادية.
    3. إذا كانت المصادقة مفعّلة، فضمّن الرمز المميز/كلمة المرور في إطار `connect`.

    إذا كنت تستخدم CLI أو TUI، فينبغي أن يبدو عنوان URL كما يلي:

    ```
    openclaw tui --url ws://<host>:18789 --token <token>
    ```

    تفاصيل البروتوكول: [بروتوكول Gateway](/ar/gateway/protocol).

  </Accordion>
</AccordionGroup>

## التسجيل وتصحيح الأخطاء

<AccordionGroup>
  <Accordion title="أين توجد السجلات؟">
    سجلات الملفات (منظمة):

    ```
    /tmp/openclaw/openclaw-YYYY-MM-DD.log
    ```

    يمكنك ضبط مسار ثابت عبر `logging.file`. ويتحكم `logging.level` في مستوى سجل الملف. أما تفصيلية وحدة التحكم فيتحكم بها `--verbose` و`logging.consoleLevel`.

    أسرع متابعة للسجل:

    ```bash
    openclaw logs --follow
    ```

    سجلات الخدمة/المشرف (عندما تعمل gateway عبر launchd/systemd):

    - macOS: `$OPENCLAW_STATE_DIR/logs/gateway.log` و`gateway.err.log` (الافتراضي: `~/.openclaw/logs/...`؛ وتستخدم ملفات التعريف `~/.openclaw-<profile>/logs/...`)
    - Linux: `journalctl --user -u openclaw-gateway[-<profile>].service -n 200 --no-pager`
    - Windows: `schtasks /Query /TN "OpenClaw Gateway (<profile>)" /V /FO LIST`

    راجع [استكشاف الأخطاء وإصلاحها](/ar/gateway/troubleshooting) للمزيد.

  </Accordion>

  <Accordion title="كيف أبدأ/أوقف/أعيد تشغيل خدمة Gateway؟">
    استخدم مساعدات gateway:

    ```bash
    openclaw gateway status
    openclaw gateway restart
    ```

    إذا كنت تشغّل gateway يدويًا، فيمكن لـ `openclaw gateway --force` استعادة المنفذ. راجع [Gateway](/ar/gateway).

  </Accordion>

  <Accordion title="أغلقت الطرفية على Windows - كيف أعيد تشغيل OpenClaw؟">
    توجد **طريقتا تثبيت** على Windows:

    **1) WSL2 (موصى به):** تعمل Gateway داخل Linux.

    افتح PowerShell، وادخل إلى WSL، ثم أعد التشغيل:

    ```powershell
    wsl
    openclaw gateway status
    openclaw gateway restart
    ```

    إذا لم تكن قد ثبّت الخدمة مطلقًا، فابدأها في الواجهة الأمامية:

    ```bash
    openclaw gateway run
    ```

    **2) Windows الأصلي (غير موصى به):** تعمل Gateway مباشرة داخل Windows.

    افتح PowerShell وشغّل:

    ```powershell
    openclaw gateway status
    openclaw gateway restart
    ```

    إذا كنت تشغّلها يدويًا (من دون خدمة)، فاستخدم:

    ```powershell
    openclaw gateway run
    ```

    المستندات: [Windows (WSL2)](/ar/platforms/windows)، [دليل تشغيل خدمة Gateway](/ar/gateway).

  </Accordion>

  <Accordion title="تعمل Gateway لكن الردود لا تصل أبدًا. ما الذي ينبغي أن أتحقق منه؟">
    ابدأ بمسح سريع للصحة:

    ```bash
    openclaw status
    openclaw models status
    openclaw channels status
    openclaw logs --follow
    ```

    الأسباب الشائعة:

    - لم يتم تحميل مصادقة النموذج على **مضيف gateway** (تحقق من `models status`).
    - اقتران القناة/قائمة السماح تحظر الردود (تحقق من إعدادات القناة + السجلات).
    - WebChat/Dashboard مفتوحة من دون الرمز الصحيح.

    إذا كنت في وضع بعيد، فتأكد من أن اتصال النفق/Tailscale يعمل وأن
    Gateway WebSocket قابلة للوصول.

    المستندات: [القنوات](/ar/channels)، [استكشاف الأخطاء وإصلاحها](/ar/gateway/troubleshooting)، [الوصول البعيد](/ar/gateway/remote).

  </Accordion>

  <Accordion title='"Disconnected from gateway: no reason" - ماذا الآن؟'>
    يعني هذا عادةً أن واجهة المستخدم فقدت اتصال WebSocket. تحقق مما يلي:

    1. هل تعمل Gateway؟ `openclaw gateway status`
    2. هل Gateway سليمة؟ `openclaw status`
    3. هل تمتلك واجهة المستخدم الرمز الصحيح؟ `openclaw dashboard`
    4. إذا كان الاتصال بعيدًا، فهل يعمل رابط النفق/Tailscale؟

    ثم تابع السجلات:

    ```bash
    openclaw logs --follow
    ```

    المستندات: [لوحة المعلومات](/web/dashboard)، [الوصول البعيد](/ar/gateway/remote)، [استكشاف الأخطاء وإصلاحها](/ar/gateway/troubleshooting).

  </Accordion>

  <Accordion title="فشل Telegram setMyCommands. ما الذي ينبغي أن أتحقق منه؟">
    ابدأ بالسجلات وحالة القناة:

    ```bash
    openclaw channels status
    openclaw channels logs --channel telegram
    ```

    ثم طابق الخطأ:

    - `BOT_COMMANDS_TOO_MUCH`: تحتوي قائمة Telegram على عدد كبير جدًا من الإدخالات. يقوم OpenClaw بالفعل بالاقتطاع إلى حد Telegram ويعيد المحاولة بعدد أوامر أقل، لكن بعض إدخالات القائمة ما تزال تحتاج إلى الحذف. قلّل أوامر Plugin/Skill/الأوامر المخصصة، أو عطّل `channels.telegram.commands.native` إذا لم تكن تحتاج إلى القائمة.
    - `TypeError: fetch failed`، أو `Network request for 'setMyCommands' failed!`، أو أخطاء شبكة مشابهة: إذا كنت على VPS أو خلف وكيل، فتأكد من أن HTTPS الصادرة مسموح بها وأن DNS يعمل من أجل `api.telegram.org`.

    إذا كانت Gateway بعيدة، فتأكد من أنك تنظر إلى السجلات على مضيف Gateway.

    المستندات: [Telegram](/ar/channels/telegram)، [استكشاف أخطاء القنوات](/ar/channels/troubleshooting).

  </Accordion>

  <Accordion title="يعرض TUI أي مخرجات. ما الذي ينبغي أن أتحقق منه؟">
    تأكد أولًا من أن Gateway قابلة للوصول وأن الوكيل قادر على العمل:

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    في TUI، استخدم `/status` لرؤية الحالة الحالية. وإذا كنت تتوقع ردودًا في قناة
    دردشة، فتأكد من أن التسليم مفعّل (`/deliver on`).

    المستندات: [TUI](/web/tui)، [أوامر الشرطة المائلة](/ar/tools/slash-commands).

  </Accordion>

  <Accordion title="كيف أوقف Gateway تمامًا ثم أبدأها؟">
    إذا كنت قد ثبّت الخدمة:

    ```bash
    openclaw gateway stop
    openclaw gateway start
    ```

    يؤدي هذا إلى إيقاف/بدء **الخدمة الخاضعة للإشراف** (launchd على macOS، وsystemd على Linux).
    استخدم هذا عندما تعمل Gateway في الخلفية كعملية daemon.

    إذا كنت تشغّله في الواجهة الأمامية، فأوقفه باستخدام Ctrl-C، ثم:

    ```bash
    openclaw gateway run
    ```

    المستندات: [دليل تشغيل خدمة Gateway](/ar/gateway).

  </Accordion>

  <Accordion title="بصياغة مبسطة جدًا: openclaw gateway restart مقابل openclaw gateway">
    - `openclaw gateway restart`: يعيد تشغيل **الخدمة الخلفية** (launchd/systemd).
    - `openclaw gateway`: يشغّل gateway **في الواجهة الأمامية** لهذه الجلسة الطرفية.

    إذا كنت قد ثبّت الخدمة، فاستخدم أوامر gateway. واستخدم `openclaw gateway` عندما
    تريد تشغيلًا لمرة واحدة في الواجهة الأمامية.

  </Accordion>

  <Accordion title="أسرع طريقة للحصول على مزيد من التفاصيل عند فشل شيء ما">
    ابدأ Gateway باستخدام `--verbose` للحصول على مزيد من التفاصيل في وحدة التحكم. ثم افحص ملف السجل لمعرفة مصادقة القناة، وتوجيه النموذج، وأخطاء RPC.
  </Accordion>
</AccordionGroup>

## الوسائط والمرفقات

<AccordionGroup>
  <Accordion title="أنشأت Skill صورة/PDF، لكن لم يتم إرسال أي شيء">
    يجب أن تتضمن المرفقات الصادرة من الوكيل سطر `MEDIA:<path-or-url>` (في سطر مستقل). راجع [إعداد مساعد OpenClaw](/ar/start/openclaw) و[إرسال الوكيل](/ar/tools/agent-send).

    الإرسال عبر CLI:

    ```bash
    openclaw message send --target +15555550123 --message "Here you go" --media /path/to/file.png
    ```

    تحقّق أيضًا من:

    - أن القناة المستهدفة تدعم الوسائط الصادرة وليست محظورة بواسطة قوائم السماح.
    - أن الملف ضمن حدود الحجم الخاصة بالمزوّد (تُعاد تحجيم الصور إلى حد أقصى 2048px).
    - أن `tools.fs.workspaceOnly=true` يُبقي الإرسال من المسارات المحلية محصورًا في مساحة العمل، وtemp/media-store، والملفات التي اجتازت التحقق في sandbox.
    - أن `tools.fs.workspaceOnly=false` يسمح لإرسال `MEDIA:` بإرسال الملفات المحلية على المضيف التي يستطيع الوكيل قراءتها بالفعل، ولكن فقط للوسائط بالإضافة إلى أنواع المستندات الآمنة (الصور، والصوت، والفيديو، وPDF، ومستندات Office). أما النصوص العادية والملفات التي تبدو كأسرار فتظل محظورة.

    راجع [الصور](/ar/nodes/images).

  </Accordion>
</AccordionGroup>

## الأمان والتحكم في الوصول

<AccordionGroup>
  <Accordion title="هل من الآمن تعريض OpenClaw للرسائل الخاصة الواردة؟">
    تعامل مع الرسائل الخاصة الواردة على أنها مدخلات غير موثوقة. وقد صُممت الإعدادات الافتراضية لتقليل المخاطر:

    - السلوك الافتراضي على القنوات القادرة على الرسائل الخاصة هو **الاقتران**:
      - يتلقى المرسلون غير المعروفين رمز اقتران؛ ولا يعالج البوت رسالتهم.
      - وافق باستخدام: `openclaw pairing approve --channel <channel> [--account <id>] <code>`
      - الحد الأقصى للطلبات المعلقة هو **3 لكل قناة**؛ تحقق من `openclaw pairing list --channel <channel> [--account <id>]` إذا لم يصل الرمز.
    - يتطلب فتح الرسائل الخاصة للعامة موافقة صريحة (`dmPolicy: "open"` وقائمة سماح `"*"`).

    شغّل `openclaw doctor` لإظهار سياسات الرسائل الخاصة الخطِرة.

  </Accordion>

  <Accordion title="هل يُعد حقن المطالبات مصدر قلق فقط للبوتات العامة؟">
    لا. يتعلق حقن المطالبات بـ **المحتوى غير الموثوق**، وليس فقط بمن يمكنه إرسال رسالة خاصة إلى البوت.
    فإذا كان مساعدك يقرأ محتوى خارجيًا (web search/fetch، أو صفحات المتصفح، أو الرسائل الإلكترونية،
    أو المستندات، أو المرفقات، أو السجلات الملصقة)، فقد يتضمن ذلك المحتوى تعليمات تحاول
    اختطاف النموذج. ويمكن أن يحدث ذلك حتى لو كنت **أنت المرسل الوحيد**.

    يكمن أكبر خطر عندما تكون الأدوات مفعّلة: إذ يمكن خداع النموذج
    لاستخراج السياق أو استدعاء الأدوات نيابةً عنك. قلّل نطاق التأثير عبر:

    - استخدام وكيل "قارئ" للقراءة فقط أو معطّل الأدوات لتلخيص المحتوى غير الموثوق
    - إبقاء `web_search` / `web_fetch` / `browser` معطّلة للوكلاء الممكّنين بالأدوات
    - التعامل مع النصوص المفككة من الملفات/المستندات على أنها غير موثوقة أيضًا: يقوم كل من
      `input_file` في OpenResponses واستخراج مرفقات الوسائط بتغليف النص المستخرج داخل
      علامات صريحة لحدود المحتوى الخارجي بدلًا من تمرير نص الملف الخام
    - العزل وقوائم السماح الصارمة للأدوات

    التفاصيل: [الأمان](/ar/gateway/security).

  </Accordion>

  <Accordion title="هل ينبغي أن يكون للبوت بريده الإلكتروني، أو حساب GitHub، أو رقم هاتفه الخاص؟">
    نعم، في معظم الإعدادات. إن عزل البوت بحسابات وأرقام هواتف منفصلة
    يقلل نطاق التأثير إذا حدث خطأ ما. كما يجعل ذلك أسهل في تدوير
    بيانات الاعتماد أو سحب الوصول دون التأثير في حساباتك الشخصية.

    ابدأ على نطاق صغير. امنح الوصول فقط إلى الأدوات والحسابات التي تحتاج إليها فعليًا، ووسّع
    لاحقًا إذا لزم الأمر.

    المستندات: [الأمان](/ar/gateway/security)، [الاقتران](/ar/channels/pairing).

  </Accordion>

  <Accordion title="هل يمكنني منحه استقلالية على رسائلي النصية وهل هذا آمن؟">
    نحن **لا** نوصي بالاستقلالية الكاملة على رسائلك الشخصية. والنمط الأكثر أمانًا هو:

    - أبقِ الرسائل الخاصة في **وضع الاقتران** أو ضمن قائمة سماح ضيقة.
    - استخدم **رقمًا أو حسابًا منفصلًا** إذا كنت تريد أن يرسل الرسائل نيابةً عنك.
    - دعه يصيغ، ثم **وافق قبل الإرسال**.

    إذا كنت تريد التجربة، فافعل ذلك على حساب مخصص وأبقِه معزولًا. راجع
    [الأمان](/ar/gateway/security).

  </Accordion>

  <Accordion title="هل يمكنني استخدام نماذج أرخص لمهام المساعد الشخصي؟">
    نعم، **إذا** كان الوكيل للدردشة فقط وكانت المدخلات موثوقة. فالطبقات الأصغر
    أكثر عرضة لاختطاف التعليمات، لذا تجنّبها للوكلاء الممكّنين بالأدوات
    أو عند قراءة محتوى غير موثوق. وإذا كان لا بد من استخدام نموذج أصغر، فقيّد
    الأدوات وشغّله داخل sandbox. راجع [الأمان](/ar/gateway/security).
  </Accordion>

  <Accordion title="لقد شغّلت /start في Telegram لكنني لم أحصل على رمز اقتران">
    تُرسل رموز الاقتران **فقط** عندما يرسل مرسل غير معروف رسالة إلى البوت ويكون
    `dmPolicy: "pairing"` مفعّلًا. لا يؤدي `/start` وحده إلى إنشاء رمز.

    تحقّق من الطلبات المعلقة:

    ```bash
    openclaw pairing list telegram
    ```

    إذا كنت تريد وصولًا فوريًا، فأضف معرّف المرسل إلى قائمة السماح أو اضبط `dmPolicy: "open"`
    لذلك الحساب.

  </Accordion>

  <Accordion title="WhatsApp: هل سيراسل جهات اتصالي؟ وكيف يعمل الاقتران؟">
    لا. السياسة الافتراضية لرسائل WhatsApp الخاصة هي **الاقتران**. يحصل المرسلون غير المعروفين فقط على رمز اقتران ولا **تُعالج** رسالتهم. ولا يرد OpenClaw إلا على الدردشات التي يتلقاها أو على الرسائل الصريحة التي تقوم أنت بتشغيلها.

    وافق على الاقتران باستخدام:

    ```bash
    openclaw pairing approve whatsapp <code>
    ```

    اعرض الطلبات المعلقة:

    ```bash
    openclaw pairing list whatsapp
    ```

    مطالبة رقم الهاتف في المعالج: تُستخدم لضبط **قائمة السماح/المالك** الخاصة بك حتى تُسمح رسائلك الخاصة. ولا تُستخدم للإرسال التلقائي. وإذا كنت تشغّله على رقم WhatsApp الشخصي لديك، فاستخدم ذلك الرقم وفعّل `channels.whatsapp.selfChatMode`.

  </Accordion>
</AccordionGroup>

## أوامر الدردشة، وإيقاف المهام، و"إنه لا يتوقف"

<AccordionGroup>
  <Accordion title="كيف أوقف ظهور رسائل النظام الداخلية في الدردشة؟">
    تظهر معظم الرسائل الداخلية أو رسائل الأدوات فقط عندما يكون **verbose** أو **trace** أو **reasoning** مفعّلًا
    لتلك الجلسة.

    الحل في الدردشة التي تراها فيها:

    ```
    /verbose off
    /trace off
    /reasoning off
    ```

    إذا ظل الأمر صاخبًا، فتحقق من إعدادات الجلسة في Control UI واضبط verbose
    على **inherit**. وتأكد أيضًا من أنك لا تستخدم ملف تعريف بوت يحتوي على `verboseDefault` مضبوطًا
    على `on` في الإعدادات.

    المستندات: [التفكير وverbose](/ar/tools/thinking)، [الأمان](/ar/gateway/security#reasoning-verbose-output-in-groups).

  </Accordion>

  <Accordion title="كيف أوقف/ألغي مهمة قيد التشغيل؟">
    أرسل أيًّا مما يلي **كرسالة مستقلة** (من دون slash):

    ```
    stop
    stop action
    stop current action
    stop run
    stop current run
    stop agent
    stop the agent
    stop openclaw
    openclaw stop
    stop don't do anything
    stop do not do anything
    stop doing anything
    please stop
    stop please
    abort
    esc
    wait
    exit
    interrupt
    ```

    هذه محفزات إيقاف، وليست أوامر slash.

    بالنسبة إلى العمليات الخلفية (من أداة exec)، يمكنك أن تطلب من الوكيل تشغيل:

    ```
    process action:kill sessionId:XXX
    ```

    نظرة عامة على أوامر slash: راجع [أوامر الشرطة المائلة](/ar/tools/slash-commands).

    يجب إرسال معظم الأوامر **كرسالة مستقلة** تبدأ بـ `/`، لكن بعض الاختصارات (مثل `/status`) تعمل أيضًا داخل السطر للمرسلين الموجودين في قائمة السماح.

  </Accordion>

  <Accordion title='كيف أرسل رسالة Discord من Telegram؟ ("Cross-context messaging denied")'>
    يحظر OpenClaw المراسلة **عبر المزوّدات المختلفة** افتراضيًا. إذا كان استدعاء الأداة مرتبطًا
    بـ Telegram، فلن يرسل إلى Discord ما لم تسمح بذلك صراحةً.

    فعّل المراسلة عبر المزوّدات المختلفة للوكيل:

    ```json5
    {
      tools: {
        message: {
          crossContext: {
            allowAcrossProviders: true,
            marker: { enabled: true, prefix: "[from {channel}] " },
          },
        },
      },
    }
    ```

    أعد تشغيل gateway بعد تعديل الإعدادات.

  </Accordion>

  <Accordion title='لماذا يبدو أن البوت "يتجاهل" الرسائل المتتابعة بسرعة؟'>
    يتحكم وضع قائمة الانتظار في كيفية تفاعل الرسائل الجديدة مع تشغيل جارٍ. استخدم `/queue` لتغيير الأوضاع:

    - `steer` - تعيد الرسائل الجديدة توجيه المهمة الحالية
    - `followup` - يشغّل الرسائل واحدة تلو الأخرى
    - `collect` - يجمع الرسائل في دفعة ويرد مرة واحدة (الافتراضي)
    - `steer-backlog` - يعيد التوجيه الآن، ثم يعالج التراكم
    - `interrupt` - يجهض التشغيل الحالي ويبدأ من جديد

    يمكنك إضافة خيارات مثل `debounce:2s cap:25 drop:summarize` لأوضاع followup.

  </Accordion>
</AccordionGroup>

## متفرقات

<AccordionGroup>
  <Accordion title='ما هو النموذج الافتراضي لـ Anthropic عند استخدام مفتاح API؟'>
    في OpenClaw، تكون بيانات الاعتماد واختيار النموذج منفصلين. إن ضبط `ANTHROPIC_API_KEY` (أو تخزين مفتاح Anthropic API في ملفات تعريف المصادقة) يفعّل المصادقة، لكن النموذج الافتراضي الفعلي هو أي نموذج تضبطه في `agents.defaults.model.primary` (مثل `anthropic/claude-sonnet-4-6` أو `anthropic/claude-opus-4-6`). وإذا رأيت `No credentials found for profile "anthropic:default"`، فهذا يعني أن Gateway لم تتمكن من العثور على بيانات اعتماد Anthropic في `auth-profiles.json` المتوقع للوكيل الذي يعمل.
  </Accordion>
</AccordionGroup>

---

ما زلت عالقًا؟ اسأل في [Discord](https://discord.com/invite/clawd) أو افتح [GitHub discussion](https://github.com/openclaw/openclaw/discussions).
