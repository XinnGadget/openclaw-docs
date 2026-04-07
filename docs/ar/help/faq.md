---
read_when:
    - الإجابة عن الأسئلة الشائعة المتعلقة بالإعداد أو التثبيت أو التهيئة الأولية أو دعم وقت التشغيل
    - فرز المشكلات التي يبلغ عنها المستخدمون قبل البدء في تصحيح أعمق للأخطاء
summary: الأسئلة الشائعة حول إعداد OpenClaw وتهيئته واستخدامه
title: الأسئلة الشائعة
x-i18n:
    generated_at: "2026-04-07T07:23:49Z"
    model: gpt-5.4
    provider: openai
    source_hash: bddcde55cf4bcec4913aadab4c665b235538104010e445e4c99915a1672b1148
    source_path: help/faq.md
    workflow: 15
---

# الأسئلة الشائعة

إجابات سريعة مع استكشاف أعمق للأخطاء في البيئات الواقعية (التطوير المحلي، VPS، تعدد الوكلاء، OAuth/API keys، وفشل النموذج الاحتياطي). لتشخيصات وقت التشغيل، راجع [استكشاف الأخطاء وإصلاحها](/ar/gateway/troubleshooting). وللاطلاع على مرجع الإعداد الكامل، راجع [الإعداد](/ar/gateway/configuration).

## أول 60 ثانية إذا كان هناك شيء معطل

1. **الحالة السريعة (أول فحص)**

   ```bash
   openclaw status
   ```

   ملخص محلي سريع: نظام التشغيل + التحديث، إمكانية الوصول إلى البوابة/الخدمة، الوكلاء/الجلسات، إعداد الموفر + مشكلات وقت التشغيل (عندما تكون البوابة قابلة للوصول).

2. **تقرير قابل للمشاركة (آمن للمشاركة)**

   ```bash
   openclaw status --all
   ```

   تشخيص للقراءة فقط مع ذيل السجل (الرموز المميزة محجوبة).

3. **حالة الخدمة والمنفذ**

   ```bash
   openclaw gateway status
   ```

   يعرض حالة المشرف أثناء التشغيل مقابل إمكانية الوصول عبر RPC، وعنوان URL المستهدف للفحص، وأي إعداد يُحتمل أن الخدمة استخدمته.

4. **فحوصات عميقة**

   ```bash
   openclaw status --deep
   ```

   يشغّل فحصًا مباشرًا لصحة البوابة، بما في ذلك فحوصات القنوات عند دعمها
   (يتطلب بوابة قابلة للوصول). راجع [الصحة](/ar/gateway/health).

5. **تابع أحدث سجل**

   ```bash
   openclaw logs --follow
   ```

   إذا كان RPC متوقفًا، فارجع إلى:

   ```bash
   tail -f "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)"
   ```

   سجلات الملفات منفصلة عن سجلات الخدمة؛ راجع [التسجيل](/ar/logging) و[استكشاف الأخطاء وإصلاحها](/ar/gateway/troubleshooting).

6. **شغّل الطبيب (الإصلاحات)**

   ```bash
   openclaw doctor
   ```

   يصلح/يرحّل الإعداد والحالة + يشغّل فحوصات صحية. راجع [الطبيب](/ar/gateway/doctor).

7. **لقطة البوابة**

   ```bash
   openclaw health --json
   openclaw health --verbose   # يعرض عنوان URL المستهدف + مسار الإعداد عند حدوث أخطاء
   ```

   يطلب من البوابة العاملة لقطة كاملة (WS فقط). راجع [الصحة](/ar/gateway/health).

## البدء السريع وإعداد التشغيل الأول

<AccordionGroup>
  <Accordion title="أنا عالق، ما أسرع طريقة للخروج من هذا المأزق؟">
    استخدم وكيل AI محليًا يمكنه **رؤية جهازك**. هذا أكثر فاعلية بكثير من السؤال
    في Discord، لأن معظم حالات "أنا عالق" تكون **مشكلات إعداد أو بيئة محلية**
    لا يستطيع المساعدون عن بُعد فحصها.

    - **Claude Code**: [https://www.anthropic.com/claude-code/](https://www.anthropic.com/claude-code/)
    - **OpenAI Codex**: [https://openai.com/codex/](https://openai.com/codex/)

    يمكن لهذه الأدوات قراءة المستودع، وتشغيل الأوامر، وفحص السجلات، والمساعدة في إصلاح
    الإعداد على مستوى جهازك (PATH، الخدمات، الأذونات، ملفات المصادقة). امنحها **نسخة
    المصدر الكاملة** عبر التثبيت القابل للاختراق (git):

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    هذا يثبّت OpenClaw **من نسخة git**، بحيث يتمكن الوكيل من قراءة الشيفرة + الوثائق
    والاستدلال على الإصدار الدقيق الذي تشغّله. ويمكنك دائمًا العودة إلى الإصدار المستقر لاحقًا
    بإعادة تشغيل المثبّت من دون `--install-method git`.

    نصيحة: اطلب من الوكيل أن **يخطط ويشرف** على الإصلاح (خطوة بخطوة)، ثم ينفّذ فقط
    الأوامر الضرورية. هذا يبقي التغييرات صغيرة وأسهل في المراجعة.

    إذا اكتشفت خطأ حقيقيًا أو إصلاحًا، فالرجاء فتح GitHub issue أو إرسال PR:
    [https://github.com/openclaw/openclaw/issues](https://github.com/openclaw/openclaw/issues)
    [https://github.com/openclaw/openclaw/pulls](https://github.com/openclaw/openclaw/pulls)

    ابدأ بهذه الأوامر (وشارك المخرجات عند طلب المساعدة):

    ```bash
    openclaw status
    openclaw models status
    openclaw doctor
    ```

    ما الذي تفعله:

    - `openclaw status`: لقطة سريعة لصحة البوابة/الوكيل + الإعداد الأساسي.
    - `openclaw models status`: يفحص مصادقة الموفر + توفر النماذج.
    - `openclaw doctor`: يتحقق من مشكلات الإعداد/الحالة الشائعة ويصلحها.

    فحوصات CLI أخرى مفيدة: `openclaw status --all`, `openclaw logs --follow`,
    `openclaw gateway status`, `openclaw health --verbose`.

    حلقة تصحيح سريعة: [أول 60 ثانية إذا كان هناك شيء معطل](#first-60-seconds-if-something-is-broken).
    وثائق التثبيت: [التثبيت](/ar/install)، [أعلام المثبّت](/ar/install/installer)، [التحديث](/ar/install/updating).

  </Accordion>

  <Accordion title="Heartbeat يستمر في التخطي. ماذا تعني أسباب التخطي؟">
    أسباب تخطي Heartbeat الشائعة:

    - `quiet-hours`: خارج نافذة الساعات النشطة المهيأة
    - `empty-heartbeat-file`: الملف `HEARTBEAT.md` موجود لكنه يحتوي فقط على هيكل فارغ/عناوين فقط
    - `no-tasks-due`: وضع مهام `HEARTBEAT.md` نشط لكن لم يحن موعد أي من فواصل المهام بعد
    - `alerts-disabled`: كل إظهار Heartbeat معطّل (`showOk` و`showAlerts` و`useIndicator` كلها متوقفة)

    في وضع المهام، لا يتم تقديم الطوابع الزمنية المستحقة إلا بعد اكتمال تشغيل Heartbeat
    حقيقي. ولا تضع عمليات التشغيل المتخطاة علامة اكتمال على المهام.

    الوثائق: [Heartbeat](/ar/gateway/heartbeat)، [الأتمتة والمهام](/ar/automation).

  </Accordion>

  <Accordion title="الطريقة الموصى بها لتثبيت OpenClaw وإعداده">
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
    pnpm ui:build # يثبّت تبعيات واجهة المستخدم تلقائيًا في أول تشغيل
    openclaw onboard
    ```

    إذا لم يكن لديك تثبيت عام بعد، فشغّله عبر `pnpm openclaw onboard`.

  </Accordion>

  <Accordion title="كيف أفتح لوحة التحكم بعد التهيئة الأولية؟">
    يفتح المعالج متصفحك بعنوان URL نظيف للوحة التحكم (من دون رمز مميز في الرابط) مباشرة بعد التهيئة الأولية، كما يطبع الرابط في الملخص. أبقِ تلك الصفحة مفتوحة؛ وإذا لم تُفتح تلقائيًا، فانسخ/الصق عنوان URL المطبوع على الجهاز نفسه.
  </Accordion>

  <Accordion title="كيف أوثّق لوحة التحكم على localhost مقابل الوصول البعيد؟">
    **على localhost (نفس الجهاز):**

    - افتح `http://127.0.0.1:18789/`.
    - إذا طلبت مصادقة shared-secret، فأدخل الرمز المميز أو كلمة المرور المهيأة في إعدادات Control UI.
    - مصدر الرمز المميز: `gateway.auth.token` (أو `OPENCLAW_GATEWAY_TOKEN`).
    - مصدر كلمة المرور: `gateway.auth.password` (أو `OPENCLAW_GATEWAY_PASSWORD`).
    - إذا لم يكن هناك shared secret مهيأ بعد، فأنشئ رمزًا مميزًا باستخدام `openclaw doctor --generate-gateway-token`.

    **ليس على localhost:**

    - **Tailscale Serve** (موصى به): أبقِ الربط على loopback، وشغّل `openclaw gateway --tailscale serve`، ثم افتح `https://<magicdns>/`. إذا كانت `gateway.auth.allowTailscale` تساوي `true`، فإن رؤوس الهوية تفي بمصادقة Control UI/WebSocket (من دون لصق shared secret، مع افتراض أن مضيف البوابة موثوق)؛ ولا تزال واجهات HTTP APIs تتطلب مصادقة shared-secret ما لم تستخدم عمدًا `none` في private-ingress أو مصادقة HTTP لموجه موثوق.
      تتم تسوية محاولات مصادقة Serve المتزامنة السيئة من العميل نفسه قبل أن يسجّل محدد المصادقة الفاشلة المحاولة، لذلك قد تُظهر المحاولة السيئة الثانية بالفعل `retry later`.
    - **ربط Tailnet**: شغّل `openclaw gateway --bind tailnet --token "<token>"` (أو اضبط مصادقة بكلمة مرور)، ثم افتح `http://<tailscale-ip>:18789/`، ثم الصق shared secret المطابق في إعدادات لوحة التحكم.
    - **موجه عكسي مدرك للهوية**: أبقِ Gateway خلف موجه موثوق غير loopback، واضبط `gateway.auth.mode: "trusted-proxy"`، ثم افتح عنوان URL الخاص بالموجه.
    - **نفق SSH**: `ssh -N -L 18789:127.0.0.1:18789 user@host` ثم افتح `http://127.0.0.1:18789/`. تظل مصادقة shared-secret مطبقة عبر النفق؛ الصق الرمز المميز أو كلمة المرور المهيأة إذا طُلب منك ذلك.

    راجع [لوحة التحكم](/web/dashboard) و[أسطح الويب](/web) للاطلاع على أوضاع الربط وتفاصيل المصادقة.

  </Accordion>

  <Accordion title="لماذا يوجد إعدادان لموافقات exec لموافقات الدردشة؟">
    يتحكمان في طبقتين مختلفتين:

    - `approvals.exec`: يوجّه طلبات الموافقة إلى وجهات الدردشة
    - `channels.<channel>.execApprovals`: يجعل تلك القناة تعمل كعميل موافقة أصلي لموافقات exec

    تظل سياسة exec على المضيف هي بوابة الموافقة الحقيقية. إعداد الدردشة يتحكم فقط في مكان ظهور
    طلبات الموافقة وكيفية رد الأشخاص عليها.

    في معظم الإعدادات **لا** تحتاج إلى كليهما:

    - إذا كانت الدردشة تدعم الأوامر والردود بالفعل، فإن `/approve` في نفس الدردشة يعمل عبر المسار المشترك.
    - إذا استطاعت قناة أصلية مدعومة استنتاج الموافقين بأمان، فإن OpenClaw يفعّل الآن الموافقات الأصلية DM-first تلقائيًا عندما تكون `channels.<channel>.execApprovals.enabled` غير مضبوطة أو مساوية لـ `"auto"`.
    - عندما تكون بطاقات/أزرار الموافقة الأصلية متاحة، تكون واجهة المستخدم الأصلية هي المسار الأساسي؛ ولا ينبغي للوكيل أن يتضمن أمر `/approve` يدويًا إلا إذا كانت نتيجة الأداة تشير إلى أن موافقات الدردشة غير متاحة أو أن الموافقة اليدوية هي المسار الوحيد.
    - استخدم `approvals.exec` فقط عندما يجب أيضًا إعادة توجيه الطلبات إلى دردشات أخرى أو غرف عمليات صريحة.
    - استخدم `channels.<channel>.execApprovals.target: "channel"` أو `"both"` فقط عندما تريد صراحة نشر طلبات الموافقة مرة أخرى في الغرفة/الموضوع الأصلي.
    - موافقات plugin منفصلة مرة أخرى: فهي تستخدم `/approve` في نفس الدردشة افتراضيًا، مع توجيه `approvals.plugin` الاختياري، ولا تحتفظ إلا بعض القنوات الأصلية بمعالجة موافقة plugin الأصلية فوق ذلك.

    النسخة المختصرة: التوجيه مخصص للمسار، أما إعداد العميل الأصلي فمخصص لتجربة مستخدم أغنى خاصة بالقناة.
    راجع [موافقات Exec](/ar/tools/exec-approvals).

  </Accordion>

  <Accordion title="ما بيئة التشغيل التي أحتاجها؟">
    يتطلب Node **>= 22**. ويُنصح باستخدام `pnpm`. ولا يُنصح باستخدام Bun مع Gateway.
  </Accordion>

  <Accordion title="هل يعمل على Raspberry Pi؟">
    نعم. Gateway خفيف الوزن - توضح الوثائق أن **512MB-1GB RAM**، و**نواة واحدة**، وحوالي **500MB**
    من القرص كافية للاستخدام الشخصي، كما تشير إلى أن **Raspberry Pi 4 يمكنه تشغيله**.

    إذا أردت هامشًا إضافيًا (للسجلات، والوسائط، والخدمات الأخرى)، فإن **2GB موصى بها**، لكنها
    ليست حدًا أدنى صارمًا.

    نصيحة: يمكن لجهاز Pi/VPS صغير استضافة Gateway، ويمكنك إقران **nodes** على حاسوبك المحمول/هاتفك
    للوصول إلى الشاشة/الكاميرا/Canvas محليًا أو تنفيذ الأوامر. راجع [Nodes](/ar/nodes).

  </Accordion>

  <Accordion title="هل هناك نصائح لتثبيت Raspberry Pi؟">
    النسخة المختصرة: نعم، يعمل، لكن توقّع بعض الحواف الخشنة.

    - استخدم نظام تشغيل **64-bit** وأبقِ Node >= 22.
    - فضّل **التثبيت القابل للاختراق (git)** حتى تتمكن من رؤية السجلات والتحديث بسرعة.
    - ابدأ من دون channels/Skills، ثم أضفها واحدًا واحدًا.
    - إذا واجهت مشكلات غريبة في الثنائيات، فعادةً ما تكون مشكلة **توافق ARM**.

    الوثائق: [Linux](/ar/platforms/linux)، [التثبيت](/ar/install).

  </Accordion>

  <Accordion title="إنه عالق على wake up my friend / التهيئة الأولية لا تكتمل. ماذا أفعل الآن؟">
    تعتمد تلك الشاشة على أن تكون Gateway قابلة للوصول وموثقة. كما أن TUI يرسل
    "Wake up, my friend!" تلقائيًا عند أول فتح. إذا رأيت هذا السطر **من دون رد**
    وبقيت الرموز عند 0، فهذا يعني أن الوكيل لم يعمل.

    1. أعد تشغيل Gateway:

    ```bash
    openclaw gateway restart
    ```

    2. تحقّق من الحالة + المصادقة:

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    3. إذا ظل معلقًا، فشغّل:

    ```bash
    openclaw doctor
    ```

    إذا كانت Gateway بعيدة، فتأكد من أن اتصال النفق/Tailscale يعمل وأن واجهة المستخدم
    تشير إلى Gateway الصحيحة. راجع [الوصول البعيد](/ar/gateway/remote).

  </Accordion>

  <Accordion title="هل يمكنني ترحيل الإعداد إلى جهاز جديد (Mac mini) من دون إعادة التهيئة الأولية؟">
    نعم. انسخ **دليل الحالة** و**مساحة العمل**، ثم شغّل Doctor مرة واحدة. هذا
    يبقي البوت "كما هو تمامًا" (الذاكرة، سجل الجلسات، المصادقة، وحالة القنوات)
    طالما أنك تنسخ **الموقعين** معًا:

    1. ثبّت OpenClaw على الجهاز الجديد.
    2. انسخ `$OPENCLAW_STATE_DIR` (الافتراضي: `~/.openclaw`) من الجهاز القديم.
    3. انسخ مساحة العمل الخاصة بك (الافتراضي: `~/.openclaw/workspace`).
    4. شغّل `openclaw doctor` وأعد تشغيل خدمة Gateway.

    يحافظ ذلك على الإعداد، وملفات تعريف المصادقة، وبيانات اعتماد WhatsApp، والجلسات، والذاكرة. وإذا كنت في
    الوضع البعيد، فتذكّر أن مضيف البوابة هو من يملك مخزن الجلسات ومساحة العمل.

    **مهم:** إذا كنت فقط تقوم بعمل commit/push لمساحة العمل إلى GitHub، فأنت تنسخ
    **الذاكرة + ملفات bootstrap**، لكن **ليس** سجل الجلسات أو المصادقة. فهذه توجد
    ضمن `~/.openclaw/` (مثلًا `~/.openclaw/agents/<agentId>/sessions/`).

    ذو صلة: [الترحيل](/ar/install/migrating)، [أماكن تخزين الأشياء على القرص](#where-things-live-on-disk)،
    [مساحة عمل الوكيل](/ar/concepts/agent-workspace)، [Doctor](/ar/gateway/doctor)،
    [الوضع البعيد](/ar/gateway/remote).

  </Accordion>

  <Accordion title="أين أرى الجديد في أحدث إصدار؟">
    راجع سجل التغييرات على GitHub:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    أحدث الإدخالات تكون في الأعلى. وإذا كان القسم العلوي يحمل علامة **Unreleased**، فالقسم المؤرخ
    التالي هو أحدث إصدار تم شحنه. يتم تجميع الإدخالات تحت **Highlights** و**Changes** و
    **Fixes** (مع أقسام للوثائق/أخرى عند الحاجة).

  </Accordion>

  <Accordion title="لا يمكن الوصول إلى docs.openclaw.ai (خطأ SSL)">
    بعض اتصالات Comcast/Xfinity تحظر `docs.openclaw.ai` بشكل غير صحيح عبر Xfinity
    Advanced Security. عطّله أو أضف `docs.openclaw.ai` إلى قائمة السماح ثم أعد المحاولة.
    الرجاء مساعدتنا في رفع الحظر بالإبلاغ هنا: [https://spa.xfinity.com/check_url_status](https://spa.xfinity.com/check_url_status).

    إذا كنت لا تزال غير قادر على الوصول إلى الموقع، فالوثائق لها مرآة على GitHub:
    [https://github.com/openclaw/openclaw/tree/main/docs](https://github.com/openclaw/openclaw/tree/main/docs)

  </Accordion>

  <Accordion title="الفرق بين الإصدار المستقر وbeta">
    **Stable** و**beta** هما **npm dist-tags**، وليسا خطي شيفرة منفصلين:

    - `latest` = مستقر
    - `beta` = بناء مبكر للاختبار

    عادةً، يصل الإصدار المستقر إلى **beta** أولًا، ثم تقوم خطوة
    ترقية صريحة بنقل الإصدار نفسه إلى `latest`. ويمكن للمشرفين أيضًا
    النشر مباشرة إلى `latest` عند الحاجة. ولهذا يمكن أن يشير beta وstable إلى **الإصدار نفسه** بعد الترقية.

    راجع ما الذي تغيّر:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    وللاطلاع على أوامر التثبيت السريعة والفارق بين beta وdev، راجع القسم القابل للطي أدناه.

  </Accordion>

  <Accordion title="كيف أثبّت إصدار beta وما الفرق بين beta وdev؟">
    **Beta** هو npm dist-tag باسم `beta` (وقد يطابق `latest` بعد الترقية).
    **Dev** هو رأس فرع `main` المتحرك (git)؛ وعند نشره يستخدم npm dist-tag باسم `dev`.

    أوامر سريعة (macOS/Linux):

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --beta
    ```

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    مثبّت Windows (PowerShell):
    [https://openclaw.ai/install.ps1](https://openclaw.ai/install.ps1)

    مزيد من التفاصيل: [قنوات التطوير](/ar/install/development-channels) و[أعلام المثبّت](/ar/install/installer).

  </Accordion>

  <Accordion title="كيف أجرّب أحدث الإصدارات؟">
    لديك خياران:

    1. **قناة Dev (نسخة git):**

    ```bash
    openclaw update --channel dev
    ```

    هذا يبدّل إلى فرع `main` ويحدّث من المصدر.

    2. **تثبيت قابل للاختراق (من موقع المثبّت):**

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    يمنحك ذلك مستودعًا محليًا يمكنك تعديله، ثم تحديثه عبر git.

    إذا كنت تفضّل نسخة نظيفة يدويًا، فاستخدم:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    ```

    الوثائق: [التحديث](/cli/update)، [قنوات التطوير](/ar/install/development-channels)،
    [التثبيت](/ar/install).

  </Accordion>

  <Accordion title="كم يستغرق التثبيت والتهيئة الأولية عادةً؟">
    دليل تقريبي:

    - **التثبيت:** 2-5 دقائق
    - **التهيئة الأولية:** 5-15 دقيقة بحسب عدد channels/models التي تهيئها

    إذا علِق، فاستخدم [تعطل المثبّت](#quick-start-and-first-run-setup)
    وحلقة التصحيح السريعة في [أنا عالق](#quick-start-and-first-run-setup).

  </Accordion>

  <Accordion title="المثبّت عالق؟ كيف أحصل على مزيد من المعلومات؟">
    أعد تشغيل المثبّت مع **مخرجات تفصيلية**:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --verbose
    ```

    تثبيت Beta مع الوضع التفصيلي:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --beta --verbose
    ```

    لتثبيت قابل للاختراق (git):

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git --verbose
    ```

    ما يعادل ذلك على Windows (PowerShell):

    ```powershell
    # install.ps1 لا يحتوي بعد على علم -Verbose مخصص.
    Set-PSDebug -Trace 1
    & ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -NoOnboard
    Set-PSDebug -Trace 0
    ```

    خيارات أكثر: [أعلام المثبّت](/ar/install/installer).

  </Accordion>

  <Accordion title="يقول التثبيت على Windows إن git غير موجود أو إن openclaw غير معروف">
    مشكلتان شائعتان على Windows:

    **1) خطأ npm spawn git / git غير موجود**

    - ثبّت **Git for Windows** وتأكد من أن `git` موجود على PATH.
    - أغلق PowerShell وأعد فتحه، ثم أعد تشغيل المثبّت.

    **2) openclaw غير معروف بعد التثبيت**

    - مجلد npm global bin غير موجود على PATH.
    - تحقق من المسار:

      ```powershell
      npm config get prefix
      ```

    - أضف ذلك الدليل إلى PATH الخاص بالمستخدم (لا حاجة إلى اللاحقة `\bin` على Windows؛ وفي معظم الأنظمة يكون `%AppData%\npm`).
    - أغلق PowerShell وأعد فتحه بعد تحديث PATH.

    إذا أردت أسهل إعداد على Windows، فاستخدم **WSL2** بدل Windows الأصلي.
    الوثائق: [Windows](/ar/platforms/windows).

  </Accordion>

  <Accordion title="يعرض خرج exec على Windows نصًا صينيًا مشوهًا - ماذا أفعل؟">
    يحدث هذا عادةً بسبب عدم تطابق صفحة ترميز وحدة التحكم في صدَفات Windows الأصلية.

    الأعراض:

    - يظهر خرج `system.run`/`exec` للنص الصيني بشكل مشوه
    - يبدو الأمر نفسه صحيحًا في ملف تعريف طرفية آخر

    حل سريع في PowerShell:

    ```powershell
    chcp 65001
    [Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    ```

    ثم أعد تشغيل Gateway وأعد محاولة الأمر:

    ```powershell
    openclaw gateway restart
    ```

    إذا كنت لا تزال ترى هذا على أحدث إصدار من OpenClaw، فتابعه/أبلِغ عنه هنا:

    - [Issue #30640](https://github.com/openclaw/openclaw/issues/30640)

  </Accordion>

  <Accordion title="الوثائق لم تجب عن سؤالي - كيف أحصل على إجابة أفضل؟">
    استخدم **التثبيت القابل للاختراق (git)** بحيث تملك المصدر الكامل والوثائق محليًا، ثم اسأل
    البوت الخاص بك (أو Claude/Codex) _من داخل ذلك المجلد_ حتى يتمكن من قراءة المستودع والإجابة بدقة.

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    مزيد من التفاصيل: [التثبيت](/ar/install) و[أعلام المثبّت](/ar/install/installer).

  </Accordion>

  <Accordion title="كيف أثبّت OpenClaw على Linux؟">
    الإجابة المختصرة: اتبع دليل Linux، ثم شغّل التهيئة الأولية.

    - المسار السريع لـ Linux + تثبيت الخدمة: [Linux](/ar/platforms/linux).
    - الشرح الكامل: [البدء](/ar/start/getting-started).
    - المثبّت + التحديثات: [التثبيت والتحديثات](/ar/install/updating).

  </Accordion>

  <Accordion title="كيف أثبّت OpenClaw على VPS؟">
    أي Linux VPS سيعمل. ثبّته على الخادم، ثم استخدم SSH/Tailscale للوصول إلى Gateway.

    الأدلة: [exe.dev](/ar/install/exe-dev)، [Hetzner](/ar/install/hetzner)، [Fly.io](/ar/install/fly).
    الوصول البعيد: [Gateway remote](/ar/gateway/remote).

  </Accordion>

  <Accordion title="أين توجد أدلة التثبيت السحابي/VPS؟">
    نحتفظ **بمحور استضافة** يضم الموفرين الشائعين. اختر واحدًا واتبع الدليل:

    - [استضافة VPS](/ar/vps) (كل الموفرين في مكان واحد)
    - [Fly.io](/ar/install/fly)
    - [Hetzner](/ar/install/hetzner)
    - [exe.dev](/ar/install/exe-dev)

    كيف يعمل ذلك في السحابة: **Gateway تعمل على الخادم**، وأنت تصل إليها
    من حاسوبك المحمول/هاتفك عبر Control UI (أو Tailscale/SSH). وتوجد حالتك + مساحة العمل
    على الخادم، لذا عامل المضيف بوصفه المصدر الأساسي للحقيقة وخذ له نسخًا احتياطية.

    يمكنك إقران **nodes** ‏(Mac/iOS/Android/headless) مع تلك Gateway السحابية للوصول إلى
    الشاشة/الكاميرا/Canvas محليًا أو تشغيل أوامر على حاسوبك المحمول مع إبقاء
    Gateway في السحابة.

    المحور: [المنصات](/ar/platforms). الوصول البعيد: [Gateway remote](/ar/gateway/remote).
    Nodes: [Nodes](/ar/nodes)، [CLI الخاص بـ Nodes](/cli/nodes).

  </Accordion>

  <Accordion title="هل يمكنني أن أطلب من OpenClaw أن يحدّث نفسه؟">
    الإجابة المختصرة: **ممكن، لكنه غير موصى به**. قد تعيد عملية التحديث تشغيل
    Gateway (ما يؤدي إلى إسقاط الجلسة النشطة)، وقد تحتاج إلى نسخة git نظيفة،
    وقد تطلب تأكيدًا. والأكثر أمانًا: تشغيل التحديثات من طرفية بصفتك المشغّل.

    استخدم CLI:

    ```bash
    openclaw update
    openclaw update status
    openclaw update --channel stable|beta|dev
    openclaw update --tag <dist-tag|version>
    openclaw update --no-restart
    ```

    إذا كان لا بد من أتمتته من وكيل:

    ```bash
    openclaw update --yes --no-restart
    openclaw gateway restart
    ```

    الوثائق: [التحديث](/cli/update)، [التحديث](/ar/install/updating).

  </Accordion>

  <Accordion title="ماذا تفعل التهيئة الأولية فعليًا؟">
    يعد `openclaw onboard` مسار الإعداد الموصى به. في **الوضع المحلي** يرشدك خلال:

    - **إعداد النموذج/المصادقة** (OAuth للموفر، وAPI keys، وAnthropic setup-token، بالإضافة إلى خيارات النماذج المحلية مثل LM Studio)
    - موقع **مساحة العمل** + ملفات bootstrap
    - **إعدادات Gateway** ‏(bind/port/auth/tailscale)
    - **Channels** ‏(WhatsApp، Telegram، Discord، Mattermost، Signal، iMessage، بالإضافة إلى channel plugins المجمعة مثل QQ Bot)
    - **تثبيت daemon** ‏(LaunchAgent على macOS؛ ووحدة مستخدم systemd على Linux/WSL2)
    - **فحوصات الصحة** واختيار **Skills**

    كما يحذرك إذا كان النموذج المهيأ غير معروف أو تنقصه المصادقة.

  </Accordion>

  <Accordion title="هل أحتاج إلى اشتراك Claude أو OpenAI لتشغيل هذا؟">
    لا. يمكنك تشغيل OpenClaw باستخدام **API keys** ‏(Anthropic/OpenAI/غيرهما) أو باستخدام
    **نماذج محلية فقط** بحيث تبقى بياناتك على جهازك. والاشتراكات (Claude
    Pro/Max أو OpenAI Codex) هي طرق اختيارية لمصادقة هؤلاء الموفّرين.

    بالنسبة إلى Anthropic في OpenClaw، فالتقسيم العملي هو:

    - **Anthropic API key**: فوترة Anthropic API العادية
    - **Claude CLI / مصادقة اشتراك Claude في OpenClaw**: أخبرنا موظفو Anthropic
      بأن هذا الاستخدام مسموح به مجددًا، ويتعامل OpenClaw مع استخدام `claude -p`
      على أنه معتمد لهذا التكامل ما لم تنشر Anthropic سياسة جديدة

    بالنسبة إلى مضيفي gateway طويلة العمر، تظل Anthropic API keys هي
    الإعداد الأكثر قابلية للتنبؤ. كما أن OpenAI Codex OAuth مدعوم صراحةً للأدوات
    الخارجية مثل OpenClaw.

    كما يدعم OpenClaw خيارات أخرى مستضافة على نمط الاشتراك، بما في ذلك
    **Qwen Cloud Coding Plan**، و**MiniMax Coding Plan**، و
    **Z.AI / GLM Coding Plan**.

    الوثائق: [Anthropic](/ar/providers/anthropic)، [OpenAI](/ar/providers/openai)،
    [Qwen Cloud](/ar/providers/qwen)،
    [MiniMax](/ar/providers/minimax)، [GLM Models](/ar/providers/glm)،
    [النماذج المحلية](/ar/gateway/local-models)، [النماذج](/ar/concepts/models).

  </Accordion>

  <Accordion title="هل يمكنني استخدام اشتراك Claude Max من دون API key؟">
    نعم.

    أخبرنا موظفو Anthropic أن استخدام Claude CLI بأسلوب OpenClaw مسموح به مجددًا، لذا
    يتعامل OpenClaw مع مصادقة اشتراك Claude واستخدام `claude -p` على أنهما معتمدان
    لهذا التكامل ما لم تنشر Anthropic سياسة جديدة. وإذا أردت
    إعدادًا أكثر قابلية للتنبؤ على جانب الخادم، فاستخدم Anthropic API key بدلًا من ذلك.

  </Accordion>

  <Accordion title="هل تدعمون مصادقة اشتراك Claude (Claude Pro أو Max)؟">
    نعم.

    أخبرنا موظفو Anthropic أن هذا الاستخدام مسموح به مجددًا، لذلك يتعامل OpenClaw مع
    إعادة استخدام Claude CLI واستخدام `claude -p` على أنهما معتمدان لهذا التكامل
    ما لم تنشر Anthropic سياسة جديدة.

    لا يزال Anthropic setup-token متاحًا كمسار رمز مميز مدعوم في OpenClaw، لكن OpenClaw يفضّل الآن إعادة استخدام Claude CLI واستخدام `claude -p` عند توفرهما.
    وبالنسبة إلى أحمال العمل الإنتاجية أو متعددة المستخدمين، تظل مصادقة Anthropic API key
    الخيار الأكثر أمانًا وقابلية للتنبؤ. وإذا أردت خيارات مستضافة أخرى
    على نمط الاشتراك داخل OpenClaw، فراجع [OpenAI](/ar/providers/openai)، و[Qwen / Model
    Cloud](/ar/providers/qwen)، و[MiniMax](/ar/providers/minimax)، و[GLM
    Models](/ar/providers/glm).

  </Accordion>

<a id="why-am-i-seeing-http-429-ratelimiterror-from-anthropic"></a>
<Accordion title="لماذا أرى HTTP 429 rate_limit_error من Anthropic؟">
هذا يعني أن **حصة/حد المعدل لدى Anthropic** قد استُنفدت في النافذة الحالية. إذا كنت
تستخدم **Claude CLI**، فانتظر حتى تُعاد تهيئة النافذة أو قم بترقية خطتك. وإذا كنت
تستخدم **Anthropic API key**، فتحقق من Anthropic Console
من الاستخدام/الفوترة وارفع الحدود عند الحاجة.

    إذا كانت الرسالة تحديدًا:
    `Extra usage is required for long context requests`، فهذا يعني أن الطلب يحاول استخدام
    إصدار Anthropic التجريبي لسياق 1M (`context1m: true`). وهذا لا يعمل إلا عندما تكون
    بيانات اعتمادك مؤهلة لفوترة السياق الطويل (فوترة API key أو
    مسار تسجيل دخول Claude في OpenClaw مع تفعيل Extra Usage).

    نصيحة: اضبط **نموذجًا احتياطيًا** حتى يتمكن OpenClaw من الاستمرار في الرد بينما يكون أحد الموفّرين مقيدًا بالمعدل.
    راجع [النماذج](/cli/models)، و[OAuth](/ar/concepts/oauth)، و
    [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/ar/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context).

  </Accordion>

  <Accordion title="هل AWS Bedrock مدعوم؟">
    نعم. يحتوي OpenClaw على موفر مجمّع **Amazon Bedrock (Converse)**. وعند وجود علامات بيئة AWS، يستطيع OpenClaw اكتشاف فهرس Bedrock للبث/النص تلقائيًا ودمجه كموفر ضمني باسم `amazon-bedrock`؛ وإلا يمكنك تفعيل `plugins.entries.amazon-bedrock.config.discovery.enabled` صراحةً أو إضافة إدخال موفر يدويًا. راجع [Amazon Bedrock](/ar/providers/bedrock) و[موفرو النماذج](/ar/providers/models). وإذا كنت تفضّل مسار مفاتيح مُدارًا، فسيظل وجود موجه متوافق مع OpenAI أمام Bedrock خيارًا صالحًا.
  </Accordion>

  <Accordion title="كيف تعمل مصادقة Codex؟">
    يدعم OpenClaw **OpenAI Code (Codex)** عبر OAuth (تسجيل دخول ChatGPT). ويمكن للتهيئة الأولية تشغيل تدفق OAuth وستضبط النموذج الافتراضي إلى `openai-codex/gpt-5.4` عند الاقتضاء. راجع [موفرو النماذج](/ar/concepts/model-providers) و[التهيئة الأولية (CLI)](/ar/start/wizard).
  </Accordion>

  <Accordion title="لماذا لا يفتح ChatGPT GPT-5.4 المسار openai/gpt-5.4 في OpenClaw؟">
    يتعامل OpenClaw مع المسارين بشكل منفصل:

    - `openai-codex/gpt-5.4` = OAuth الخاص بـ ChatGPT/Codex
    - `openai/gpt-5.4` = OpenAI Platform API مباشر

    في OpenClaw، يتم توصيل تسجيل دخول ChatGPT/Codex بمسار `openai-codex/*`،
    وليس بمسار `openai/*` المباشر. وإذا أردت مسار API المباشر في
    OpenClaw، فاضبط `OPENAI_API_KEY` (أو إعداد موفر OpenAI المكافئ).
    وإذا أردت تسجيل دخول ChatGPT/Codex داخل OpenClaw، فاستخدم `openai-codex/*`.

  </Accordion>

  <Accordion title="لماذا قد تختلف حدود Codex OAuth عن ChatGPT web؟">
    يستخدم `openai-codex/*` مسار Codex OAuth، وتدير OpenAI نوافذ الحصة القابلة للاستخدام فيه
    وتعتمد على الخطة. وعمليًا، قد تختلف هذه الحدود عن
    تجربة موقع/تطبيق ChatGPT، حتى عندما يكون كلاهما مرتبطًا بالحساب نفسه.

    يمكن لـ OpenClaw عرض نوافذ الاستخدام/الحصة المرئية حاليًا لدى الموفر في
    `openclaw models status`، لكنه لا يخترع أو يطبّع استحقاقات ChatGPT-web
    إلى وصول مباشر إلى API. وإذا أردت مسار الفوترة/الحدود المباشر في OpenAI Platform،
    فاستخدم `openai/*` مع API key.

  </Accordion>

  <Accordion title="هل تدعمون مصادقة اشتراك OpenAI (Codex OAuth)؟">
    نعم. يدعم OpenClaw بالكامل **OAuth اشتراك OpenAI Code (Codex)**.
    وتسمح OpenAI صراحةً باستخدام OAuth للاشتراك في الأدوات/سير العمل
    الخارجية مثل OpenClaw. ويمكن للتهيئة الأولية تشغيل تدفق OAuth بالنيابة عنك.

    راجع [OAuth](/ar/concepts/oauth)، و[موفرو النماذج](/ar/concepts/model-providers)، و[التهيئة الأولية (CLI)](/ar/start/wizard).

  </Accordion>

  <Accordion title="كيف أعد Gemini CLI OAuth؟">
    يستخدم Gemini CLI **تدفق مصادقة plugin**، وليس client id أو secret في `openclaw.json`.

    الخطوات:

    1. ثبّت Gemini CLI محليًا بحيث يكون `gemini` على `PATH`
       - Homebrew: `brew install gemini-cli`
       - npm: `npm install -g @google/gemini-cli`
    2. فعّل plugin: `openclaw plugins enable google`
    3. سجّل الدخول: `openclaw models auth login --provider google-gemini-cli --set-default`
    4. النموذج الافتراضي بعد تسجيل الدخول: `google-gemini-cli/gemini-3.1-pro-preview`
    5. إذا فشلت الطلبات، فاضبط `GOOGLE_CLOUD_PROJECT` أو `GOOGLE_CLOUD_PROJECT_ID` على مضيف gateway

    يؤدي هذا إلى تخزين OAuth tokens في ملفات تعريف المصادقة على مضيف gateway. التفاصيل: [موفرو النماذج](/ar/concepts/model-providers).

  </Accordion>

  <Accordion title="هل النموذج المحلي مناسب للدردشات العادية؟">
    عادةً لا. يحتاج OpenClaw إلى سياق كبير + أمان قوي؛ والبطاقات الصغيرة تقطع السياق وتسرّبه. وإذا كان لا بد، فشغّل **أكبر** بناء نموذج تستطيع تشغيله محليًا (LM Studio) وراجع [/gateway/local-models](/ar/gateway/local-models). فالنماذج الأصغر/المكمّاة تزيد خطر prompt-injection - راجع [الأمان](/ar/gateway/security).
  </Accordion>

  <Accordion title="كيف أحافظ على حركة المرور إلى النماذج المستضافة ضمن منطقة محددة؟">
    اختر نقاط نهاية مثبتة على منطقة معينة. يوفّر OpenRouter خيارات مستضافة في الولايات المتحدة لكل من MiniMax وKimi وGLM؛ اختر النسخة المستضافة في الولايات المتحدة للإبقاء على البيانات ضمن المنطقة. ولا يزال بإمكانك إدراج Anthropic/OpenAI إلى جانب هذه الخيارات باستخدام `models.mode: "merge"` حتى تبقى النماذج الاحتياطية متاحة مع احترام الموفر الإقليمي الذي تختاره.
  </Accordion>

  <Accordion title="هل يجب أن أشتري Mac Mini لتثبيت هذا؟">
    لا. يعمل OpenClaw على macOS أو Linux (وعلى Windows عبر WSL2). وMac mini اختياري -
    فبعض الأشخاص يشترونه كمضيف دائم التشغيل، لكن VPS صغيرًا أو خادمًا منزليًا أو جهازًا من فئة Raspberry Pi يصلح أيضًا.

    أنت تحتاج إلى Mac **فقط للأدوات الخاصة بـ macOS فقط**. وبالنسبة إلى iMessage، استخدم [BlueBubbles](/ar/channels/bluebubbles) (موصى به) - يعمل خادم BlueBubbles على أي Mac، ويمكن أن تعمل Gateway على Linux أو في مكان آخر. وإذا أردت أدوات أخرى خاصة بـ macOS فقط، فشغّل Gateway على جهاز Mac أو أقرِن macOS node.

    الوثائق: [BlueBubbles](/ar/channels/bluebubbles)، [Nodes](/ar/nodes)، [الوضع البعيد على Mac](/ar/platforms/mac/remote).

  </Accordion>

  <Accordion title="هل أحتاج إلى Mac mini لدعم iMessage؟">
    أنت بحاجة إلى **أي جهاز macOS** مسجّل الدخول إلى Messages. ولا **يجب** أن يكون Mac mini -
    أي جهاز Mac يكفي. **استخدم [BlueBubbles](/ar/channels/bluebubbles)** (موصى به) لـ iMessage - يعمل خادم BlueBubbles على macOS، بينما يمكن أن تعمل Gateway على Linux أو في مكان آخر.

    إعدادات شائعة:

    - شغّل Gateway على Linux/VPS، وشغّل خادم BlueBubbles على أي Mac مسجل الدخول إلى Messages.
    - شغّل كل شيء على جهاز Mac إذا كنت تريد أبسط إعداد على جهاز واحد.

    الوثائق: [BlueBubbles](/ar/channels/bluebubbles)، [Nodes](/ar/nodes)،
    [الوضع البعيد على Mac](/ar/platforms/mac/remote).

  </Accordion>

  <Accordion title="إذا اشتريت Mac mini لتشغيل OpenClaw، فهل يمكنني وصله بـ MacBook Pro؟">
    نعم. يمكن لـ **Mac mini تشغيل Gateway**، ويمكن لـ MacBook Pro الاتصال به
    بوصفه **node** ‏(جهازًا مرافقًا). لا تشغّل Nodes الـ Gateway - بل توفر
    قدرات إضافية مثل الشاشة/الكاميرا/Canvas و`system.run` على ذلك الجهاز.

    نمط شائع:

    - Gateway على Mac mini (دائم التشغيل).
    - يشغّل MacBook Pro تطبيق macOS أو مضيف node ويُقترن مع Gateway.
    - استخدم `openclaw nodes status` / `openclaw nodes list` لرؤيته.

    الوثائق: [Nodes](/ar/nodes)، [CLI الخاص بـ Nodes](/cli/nodes).

  </Accordion>

  <Accordion title="هل يمكنني استخدام Bun؟">
    **لا يُنصح** بـ Bun. فنحن نرى أخطاء وقت تشغيل، خاصة مع WhatsApp وTelegram.
    استخدم **Node** للحصول على بوابات مستقرة.

    وإذا كنت لا تزال تريد التجربة باستخدام Bun، فافعل ذلك على Gateway غير إنتاجية
    من دون WhatsApp/Telegram.

  </Accordion>

  <Accordion title="Telegram: ما الذي يوضع في allowFrom؟">
    القيمة `channels.telegram.allowFrom` هي **معرّف مستخدم Telegram البشري المرسِل** (رقمي). وليست اسم مستخدم البوت.

    تقبل التهيئة الأولية إدخال `@username` وتحله إلى معرّف رقمي، لكن تفويض OpenClaw يستخدم المعرفات الرقمية فقط.

    الطريقة الأكثر أمانًا (من دون بوت خارجي):

    - أرسل رسالة خاصة إلى البوت، ثم شغّل `openclaw logs --follow` واقرأ `from.id`.

    Bot API الرسمي:

    - أرسل رسالة خاصة إلى البوت، ثم اطلب `https://api.telegram.org/bot<bot_token>/getUpdates` واقرأ `message.from.id`.

    طرف ثالث (أقل خصوصية):

    - أرسل رسالة خاصة إلى `@userinfobot` أو `@getidsbot`.

    راجع [/channels/telegram](/ar/channels/telegram#access-control-and-activation).

  </Accordion>

  <Accordion title="هل يمكن لعدة أشخاص استخدام رقم WhatsApp واحد مع نُسخ OpenClaw مختلفة؟">
    نعم، عبر **التوجيه متعدد الوكلاء**. اربط WhatsApp **DM** لكل مرسل (peer من النوع `kind: "direct"`، مع sender E.164 مثل `+15551234567`) بمعرّف `agentId` مختلف، حتى يحصل كل شخص على مساحة العمل الخاصة به ومخزن الجلسات الخاص به. وستظل الردود تصدر من **حساب WhatsApp نفسه**، ويظل التحكم في الوصول إلى DM (`channels.whatsapp.dmPolicy` / `channels.whatsapp.allowFrom`) عامًا لكل حساب WhatsApp. راجع [التوجيه متعدد الوكلاء](/ar/concepts/multi-agent) و[WhatsApp](/ar/channels/whatsapp).
  </Accordion>

  <Accordion title='هل يمكنني تشغيل وكيل "دردشة سريعة" ووكيل "Opus للبرمجة"؟'>
    نعم. استخدم التوجيه متعدد الوكلاء: أعطِ كل وكيل نموذجه الافتراضي الخاص، ثم اربط المسارات الواردة (حساب الموفر أو peers محددين) بكل وكيل. يوجد مثال للإعداد في [التوجيه متعدد الوكلاء](/ar/concepts/multi-agent). راجع أيضًا [النماذج](/ar/concepts/models) و[الإعداد](/ar/gateway/configuration).
  </Accordion>

  <Accordion title="هل يعمل Homebrew على Linux؟">
    نعم. يدعم Homebrew نظام Linux ‏(Linuxbrew). إعداد سريع:

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew install <formula>
    ```

    إذا كنت تشغّل OpenClaw عبر systemd، فتأكد من أن PATH في الخدمة يتضمن `/home/linuxbrew/.linuxbrew/bin` (أو البادئة الخاصة بك في brew) حتى تُحل الأدوات المثبتة عبر `brew` داخل non-login shells.
    كما أن الإصدارات الحديثة تضيف مسبقًا أدلة user bin الشائعة إلى خدمات Linux systemd (مثل `~/.local/bin`، و`~/.npm-global/bin`، و`~/.local/share/pnpm`، و`~/.bun/bin`) وتحترم `PNPM_HOME` و`NPM_CONFIG_PREFIX` و`BUN_INSTALL` و`VOLTA_HOME` و`ASDF_DATA_DIR` و`NVM_DIR` و`FNM_DIR` عند ضبطها.

  </Accordion>

  <Accordion title="الفرق بين التثبيت القابل للاختراق عبر git وnpm install">
    - **التثبيت القابل للاختراق (git):** نسخة مصدر كاملة، قابلة للتعديل، والأفضل للمساهمين.
      تقوم بتشغيل عمليات البناء محليًا ويمكنك ترقيع الشيفرة/الوثائق.
    - **npm install:** تثبيت CLI عام، من دون مستودع، والأفضل لمن يريد "تشغيله فقط".
      تأتي التحديثات من npm dist-tags.

    الوثائق: [البدء](/ar/start/getting-started)، [التحديث](/ar/install/updating).

  </Accordion>

  <Accordion title="هل يمكنني التبديل بين تثبيت npm وgit لاحقًا؟">
    نعم. ثبّت النوع الآخر، ثم شغّل Doctor حتى تشير خدمة gateway إلى نقطة الدخول الجديدة.
    هذا **لا يحذف بياناتك** - بل يغير فقط تثبيت شيفرة OpenClaw. وستظل الحالة
    (`~/.openclaw`) ومساحة العمل (`~/.openclaw/workspace`) من دون مساس.

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

    يكتشف Doctor عدم تطابق نقطة دخول خدمة gateway ويعرض إعادة كتابة إعداد الخدمة ليتوافق مع التثبيت الحالي (استخدم `--repair` في الأتمتة).

    نصائح النسخ الاحتياطي: راجع [استراتيجية النسخ الاحتياطي](#where-things-live-on-disk).

  </Accordion>

  <Accordion title="هل يجب أن أشغّل Gateway على حاسوبي المحمول أم على VPS؟">
    الإجابة المختصرة: **إذا أردت موثوقية 24/7 فاستخدم VPS**. وإذا أردت
    أقل قدر من الاحتكاك وكنت متقبلًا للنوم/إعادة التشغيل، فشغّلها محليًا.

    **الحاسوب المحمول (Gateway محلية)**

    - **الإيجابيات:** لا تكلفة خادم، وصول مباشر إلى الملفات المحلية، نافذة متصفح مرئية.
    - **السلبيات:** النوم/انقطاع الشبكة = انقطاعات، تحديثات/إعادات تشغيل النظام تقطع العمل، ويجب أن يبقى الجهاز مستيقظًا.

    **VPS / السحابة**

    - **الإيجابيات:** دائم التشغيل، شبكة مستقرة، لا توجد مشكلات نوم الحاسوب المحمول، أسهل في إبقائه قيد التشغيل.
    - **السلبيات:** غالبًا يعمل من دون واجهة (استخدم لقطات الشاشة)، وصول بعيد إلى الملفات فقط، ويجب عليك استخدام SSH للتحديثات.

    **ملاحظة خاصة بـ OpenClaw:** تعمل WhatsApp/Telegram/Slack/Mattermost/Discord جيدًا من VPS. والمفاضلة الحقيقية الوحيدة هي **متصفح headless** مقابل نافذة مرئية. راجع [المتصفح](/ar/tools/browser).

    **الافتراضي الموصى به:** VPS إذا سبق أن واجهت انقطاعات في gateway. أما الوضع المحلي فهو ممتاز عندما تستخدم جهاز Mac بنشاط وتريد وصولًا محليًا إلى الملفات أو أتمتة واجهة مستخدم مع متصفح مرئي.

  </Accordion>

  <Accordion title="ما مدى أهمية تشغيل OpenClaw على جهاز مخصص؟">
    ليس مطلوبًا، لكنه **موصى به للموثوقية والعزل**.

    - **مضيف مخصص (VPS/Mac mini/Pi):** دائم التشغيل، انقطاعات أقل بسبب النوم/إعادة التشغيل، أذونات أنظف، أسهل في الإبقاء عليه قيد التشغيل.
    - **حاسوب محمول/مكتبي مشترك:** جيد تمامًا للاختبار والاستخدام النشط، لكن توقّع توقفات عندما ينام الجهاز أو يُحدَّث.

    إذا أردت أفضل ما في العالمين، فأبقِ Gateway على مضيف مخصص وأقرِن حاسوبك المحمول بوصفه **node** لأدوات الشاشة/الكاميرا/exec المحلية. راجع [Nodes](/ar/nodes).
    ولإرشادات الأمان، اقرأ [الأمان](/ar/gateway/security).

  </Accordion>

  <Accordion title="ما الحد الأدنى لمتطلبات VPS ونظام التشغيل الموصى به؟">
    OpenClaw خفيف الوزن. بالنسبة إلى Gateway أساسية + قناة دردشة واحدة:

    - **الحد الأدنى المطلق:** ‏1 vCPU، و1GB RAM، ونحو 500MB من القرص.
    - **الموصى به:** ‏1-2 vCPU، و2GB RAM أو أكثر لهامش إضافي (للسجلات، والوسائط، وتعدد القنوات). وقد تكون أدوات Node وأتمتة المتصفح شرهة للموارد.

    نظام التشغيل: استخدم **Ubuntu LTS** ‏(أو أي Debian/Ubuntu حديث). فهذا هو المسار الأكثر اختبارًا للتثبيت على Linux.

    الوثائق: [Linux](/ar/platforms/linux)، [استضافة VPS](/ar/vps).

  </Accordion>

  <Accordion title="هل يمكنني تشغيل OpenClaw في VM وما المتطلبات؟">
    نعم. تعامل مع VM بالطريقة نفسها التي تتعامل بها مع VPS: يجب أن تكون دائمًا قيد التشغيل، قابلة للوصول، وتملك
    ذاكرة RAM كافية لـ Gateway وأي channels تقوم بتفعيلها.

    إرشادات أساسية:

    - **الحد الأدنى المطلق:** ‏1 vCPU و1GB RAM.
    - **الموصى به:** ‏2GB RAM أو أكثر إذا كنت تشغّل عدة channels، أو أتمتة متصفح، أو أدوات وسائط.
    - **نظام التشغيل:** Ubuntu LTS أو Debian/Ubuntu حديث آخر.

    إذا كنت على Windows، فإن **WSL2 هو أسهل إعداد بنمط VM** ويتمتع بأفضل توافق
    مع الأدوات. راجع [Windows](/ar/platforms/windows)، [استضافة VPS](/ar/vps).
    وإذا كنت تشغّل macOS داخل VM، فراجع [macOS VM](/ar/install/macos-vm).

  </Accordion>
</AccordionGroup>

## ما هو OpenClaw؟

<AccordionGroup>
  <Accordion title="ما هو OpenClaw في فقرة واحدة؟">
    OpenClaw هو مساعد AI شخصي تشغّله على أجهزتك الخاصة. فهو يرد على أسطح المراسلة التي تستخدمها بالفعل (WhatsApp، Telegram، Slack، Mattermost، Discord، Google Chat، Signal، iMessage، WebChat، وchannel plugins المجمعة مثل QQ Bot)، ويمكنه أيضًا تنفيذ الصوت + Canvas حي على المنصات المدعومة. وتمثل **Gateway** طبقة التحكم الدائمة التشغيل؛ أما المساعد فهو المنتج نفسه.
  </Accordion>

  <Accordion title="القيمة المقترحة">
    OpenClaw ليس "مجرد غلاف لـ Claude". بل هو **طبقة تحكم local-first** تتيح لك تشغيل
    مساعد قادر على **عتادك أنت**، يمكن الوصول إليه من تطبيقات الدردشة التي تستخدمها بالفعل، مع
    جلسات ذات حالة، وذاكرة، وأدوات - من دون تسليم التحكم في سير عملك إلى
    SaaS مستضاف.

    أبرز المزايا:

    - **أجهزتك، بياناتك:** شغّل Gateway حيثما تريد (Mac أو Linux أو VPS) واحتفظ
      بمساحة العمل + سجل الجلسات محليًا.
    - **قنوات حقيقية، لا sandbox ويب:** WhatsApp/Telegram/Slack/Discord/Signal/iMessage/etc،
      بالإضافة إلى الصوت عبر الهاتف المحمول وCanvas على المنصات المدعومة.
    - **غير مرتبط بموفر واحد للنماذج:** استخدم Anthropic وOpenAI وMiniMax وOpenRouter وغيرها، مع توجيه
      وتبديل احتياطي لكل وكيل.
    - **خيار محلي بالكامل:** شغّل نماذج محلية بحيث **يمكن أن تبقى كل البيانات على جهازك** إذا أردت.
    - **توجيه متعدد الوكلاء:** وكلاء منفصلون لكل قناة أو حساب أو مهمة، ولكلٍ منها
      مساحة عمل وافتراضيات خاصة.
    - **مفتوح المصدر وقابل للاختراق:** افحصه، ووسّعه، واستضفه ذاتيًا من دون ارتهان لمورّد.

    الوثائق: [Gateway](/ar/gateway)، [القنوات](/ar/channels)، [تعدد الوكلاء](/ar/concepts/multi-agent)،
    [الذاكرة](/ar/concepts/memory).

  </Accordion>

  <Accordion title="لقد أعددته للتو - ماذا يجب أن أفعل أولًا؟">
    مشاريع أولى جيدة:

    - أنشئ موقعًا إلكترونيًا (WordPress أو Shopify أو موقعًا ثابتًا بسيطًا).
    - اصنع نموذجًا أوليًا لتطبيق هاتف محمول (المخطط، الشاشات، خطة API).
    - نظّم الملفات والمجلدات (تنظيف، تسمية، ووسوم).
    - اربط Gmail وأتمتة الملخصات أو المتابعات.

    يمكنه التعامل مع مهام كبيرة، لكنه يعمل أفضل عندما تقسّمها إلى مراحل
    وتستخدم وكلاء فرعيين للعمل المتوازي.

  </Accordion>

  <Accordion title="ما أهم خمس حالات استخدام يومية لـ OpenClaw؟">
    المكاسب اليومية غالبًا ما تبدو هكذا:

    - **إحاطات شخصية:** ملخصات للبريد الوارد والتقويم والأخبار التي تهمك.
    - **البحث وصياغة المسودات:** بحث سريع، وملخصات، ومسودات أولى للرسائل أو الوثائق.
    - **التذكيرات والمتابعات:** تنبيهات وقوائم مراجعة مدفوعة بـ cron أو heartbeat.
    - **أتمتة المتصفح:** تعبئة النماذج، وجمع البيانات، وتكرار مهام الويب.
    - **التنسيق بين الأجهزة:** أرسل مهمة من هاتفك، ودع Gateway تنفذها على خادم، ثم أعد النتيجة إلى الدردشة.

  </Accordion>

  <Accordion title="هل يمكن أن يساعد OpenClaw في توليد العملاء المحتملين، والتواصل، والإعلانات، والمدونات لـ SaaS؟">
    نعم بالنسبة إلى **البحث، والتأهيل، وصياغة المسودات**. إذ يمكنه فحص المواقع، وبناء قوائم مختصرة،
    وتلخيص العملاء المحتملين، وكتابة مسودات للتواصل أو نصوص إعلانية.

    أما **عمليات التواصل أو تشغيل الإعلانات**، فأبقِ إنسانًا ضمن الحلقة. تجنب الرسائل غير المرغوب فيها، واتبع القوانين المحلية
    وسياسات المنصات، وراجع أي شيء قبل إرساله. وأكثر الأنماط أمانًا هو أن يدع
    OpenClaw يصوغ المسودة ثم توافق أنت عليها.

    الوثائق: [الأمان](/ar/gateway/security).

  </Accordion>

  <Accordion title="ما المزايا مقارنة بـ Claude Code لتطوير الويب؟">
    OpenClaw هو **مساعد شخصي** وطبقة تنسيق، وليس بديلًا عن IDE. استخدم
    Claude Code أو Codex لأسرع حلقة برمجة مباشرة داخل المستودع. واستخدم OpenClaw عندما
    تريد ذاكرة دائمة، ووصولًا عبر الأجهزة، وتنسيقًا للأدوات.

    المزايا:

    - **ذاكرة + مساحة عمل دائمة** عبر الجلسات
    - **وصول متعدد المنصات** ‏(WhatsApp، Telegram، TUI، WebChat)
    - **تنسيق الأدوات** ‏(المتصفح، والملفات، والجدولة، والخطافات)
    - **Gateway دائمة التشغيل** ‏(شغّلها على VPS، وتفاعل معها من أي مكان)
    - **Nodes** للمتصفح/الشاشة/الكاميرا/exec المحلي

    العرض: [https://openclaw.ai/showcase](https://openclaw.ai/showcase)

  </Accordion>
</AccordionGroup>

## Skills والأتمتة

<AccordionGroup>
  <Accordion title="كيف أخصص Skills من دون إبقاء المستودع متسخًا؟">
    استخدم overrides مُدارة بدل تعديل نسخة المستودع. ضع تغييراتك في `~/.openclaw/skills/<name>/SKILL.md` (أو أضف مجلدًا عبر `skills.load.extraDirs` في `~/.openclaw/openclaw.json`). ترتيب الأولوية هو `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → المجمّعة → `skills.load.extraDirs`، لذا فإن overrides المُدارة لا تزال تتقدم على Skills المجمعة من دون لمس git. وإذا كنت تحتاج إلى تثبيت المهارة عالميًا لكن تريد أن تكون مرئية فقط لبعض الوكلاء، فأبقِ النسخة المشتركة في `~/.openclaw/skills` وتحكم في الظهور عبر `agents.defaults.skills` و`agents.list[].skills`. ولا ينبغي أن تعيش في المستودع وتُرسل على هيئة PRs إلا التعديلات الجديرة بالرفع للمشروع.
  </Accordion>

  <Accordion title="هل يمكنني تحميل Skills من مجلد مخصص؟">
    نعم. أضف أدلة إضافية عبر `skills.load.extraDirs` في `~/.openclaw/openclaw.json` (أدنى أولوية). ترتيب الأولوية الافتراضي هو `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → المجمّعة → `skills.load.extraDirs`. ويثبّت `clawhub` افتراضيًا في `./skills`، ويتعامل OpenClaw مع ذلك بوصفه `<workspace>/skills` في الجلسة التالية. وإذا كان يجب أن تكون المهارة مرئية فقط لوكلاء معينين، فاقرن ذلك مع `agents.defaults.skills` أو `agents.list[].skills`.
  </Accordion>

  <Accordion title="كيف يمكنني استخدام نماذج مختلفة لمهام مختلفة؟">
    الأنماط المدعومة اليوم هي:

    - **وظائف Cron**: يمكن للوظائف المعزولة ضبط override للنموذج لكل وظيفة.
    - **الوكلاء الفرعيون**: وجّه المهام إلى وكلاء منفصلين لديهم نماذج افتراضية مختلفة.
    - **التبديل عند الطلب**: استخدم `/model` لتبديل نموذج الجلسة الحالية في أي وقت.

    راجع [وظائف Cron](/ar/automation/cron-jobs)، [التوجيه متعدد الوكلاء](/ar/concepts/multi-agent)، و[أوامر الشرطة المائلة](/ar/tools/slash-commands).

  </Accordion>

  <Accordion title="يتجمد البوت أثناء أداء عمل ثقيل. كيف أنقل ذلك بعيدًا؟">
    استخدم **الوكلاء الفرعيين** للمهام الطويلة أو المتوازية. يعمل الوكلاء الفرعيون في جلستهم الخاصة،
    ويعيدون ملخصًا، ويحافظون على استجابة الدردشة الرئيسية.

    اطلب من البوت "spawn a sub-agent for this task" أو استخدم `/subagents`.
    واستخدم `/status` في الدردشة لمعرفة ما الذي تقوم به Gateway الآن (وما إذا كانت مشغولة).

    نصيحة بشأن الرموز: تستهلك كل من المهام الطويلة والوكلاء الفرعيين رموزًا. وإذا كانت التكلفة مصدر قلق، فاضبط
    نموذجًا أرخص للوكلاء الفرعيين عبر `agents.defaults.subagents.model`.

    الوثائق: [الوكلاء الفرعيون](/ar/tools/subagents)، [المهام الخلفية](/ar/automation/tasks).

  </Accordion>

  <Accordion title="كيف تعمل جلسات الوكلاء الفرعيين المرتبطة بالخيوط على Discord؟">
    استخدم ربط الخيوط. يمكنك ربط خيط Discord بوكيل فرعي أو بهدف جلسة بحيث تبقى الرسائل اللاحقة في ذلك الخيط على الجلسة المرتبطة.

    التدفق الأساسي:

    - نفّذ spawn باستخدام `sessions_spawn` مع `thread: true` (واختياريًا `mode: "session"` للمتابعة الدائمة).
    - أو اربط يدويًا باستخدام `/focus <target>`.
    - استخدم `/agents` لفحص حالة الربط.
    - استخدم `/session idle <duration|off>` و`/session max-age <duration|off>` للتحكم في إلغاء التركيز التلقائي.
    - استخدم `/unfocus` لفصل الخيط.

    الإعداد المطلوب:

    - الافتراضيات العامة: `session.threadBindings.enabled`, `session.threadBindings.idleHours`, `session.threadBindings.maxAgeHours`.
    - تجاوزات Discord: ‏`channels.discord.threadBindings.enabled`, `channels.discord.threadBindings.idleHours`, `channels.discord.threadBindings.maxAgeHours`.
    - ربط تلقائي عند الـ spawn: اضبط `channels.discord.threadBindings.spawnSubagentSessions: true`.

    الوثائق: [الوكلاء الفرعيون](/ar/tools/subagents)، [Discord](/ar/channels/discord)، [مرجع الإعداد](/ar/gateway/configuration-reference)، [أوامر الشرطة المائلة](/ar/tools/slash-commands).

  </Accordion>

  <Accordion title="انتهى وكيل فرعي، لكن تحديث الاكتمال ذهب إلى المكان الخطأ أو لم يُنشر أبدًا. ما الذي ينبغي أن أتحقق منه؟">
    تحقق أولًا من مسار مقدم الطلب الذي تم حله:

    - يفضّل تسليم الوكيل الفرعي في وضع الاكتمال أي خيط أو مسار محادثة مرتبط عندما يكون موجودًا.
    - إذا كان أصل الاكتمال يحمل قناة فقط، فإن OpenClaw يعود إلى المسار المخزن لجلسة مقدم الطلب (`lastChannel` / `lastTo` / `lastAccountId`) حتى ينجح التسليم المباشر.
    - إذا لم يوجد مسار مرتبط ولا مسار مخزن صالح، فقد يفشل التسليم المباشر وتعود النتيجة إلى التسليم المؤجل ضمن الجلسة بدلًا من النشر الفوري في الدردشة.
    - لا تزال الأهداف غير الصالحة أو القديمة قادرة على فرض الرجوع إلى الطابور أو فشل التسليم النهائي.
    - إذا كان آخر رد مرئي للمساعد من الوكيل الابن هو الرمز الصامت الدقيق `NO_REPLY` / `no_reply`، أو بالضبط `ANNOUNCE_SKIP`، فإن OpenClaw يتعمد حجب الإعلان بدلًا من نشر تقدم قديم.
    - إذا انتهت مهلة الوكيل الابن بعد استدعاءات أدوات فقط، فقد يختصر الإعلان ذلك إلى ملخص موجز للتقدم الجزئي بدلًا من إعادة عرض خرج الأدوات الخام.

    التصحيح:

    ```bash
    openclaw tasks show <runId-or-sessionKey>
    ```

    الوثائق: [الوكلاء الفرعيون](/ar/tools/subagents)، [المهام الخلفية](/ar/automation/tasks)، [أدوات الجلسات](/ar/concepts/session-tool).

  </Accordion>

  <Accordion title="لا تعمل Cron أو التذكيرات. ما الذي يجب أن أتحقق منه؟">
    يعمل Cron داخل عملية Gateway. فإذا لم تكن Gateway تعمل باستمرار،
    فلن تعمل الوظائف المجدولة.

    قائمة تحقق:

    - تأكد من أن cron مفعّل (`cron.enabled`) وأن `OPENCLAW_SKIP_CRON` غير مضبوط.
    - تحقق من أن Gateway تعمل 24/7 (من دون نوم/إعادة تشغيل).
    - تحقق من إعدادات المنطقة الزمنية للوظيفة (`--tz` مقابل المنطقة الزمنية للمضيف).

    التصحيح:

    ```bash
    openclaw cron run <jobId>
    openclaw cron runs --id <jobId> --limit 50
    ```

    الوثائق: [وظائف Cron](/ar/automation/cron-jobs)، [الأتمتة والمهام](/ar/automation).

  </Accordion>

  <Accordion title="اشتغلت Cron، لكن لم يُرسل أي شيء إلى القناة. لماذا؟">
    تحقق أولًا من وضع التسليم:

    - `--no-deliver` / `delivery.mode: "none"` يعني أنه لا يُتوقع أي رسالة خارجية.
    - غياب هدف إعلان (`channel` / `to`) أو عدم صلاحيته يعني أن المشغّل تخطى التسليم الخارجي.
    - تعني أخطاء مصادقة القناة (`unauthorized`, `Forbidden`) أن المشغّل حاول التسليم لكن بيانات الاعتماد منعته.
    - تُعامل النتيجة المعزولة الصامتة (`NO_REPLY` / `no_reply` فقط) على أنها غير قابلة للتسليم عمدًا، لذلك يحجب المشغّل أيضًا التسليم الاحتياطي المؤجل.

    بالنسبة إلى وظائف cron المعزولة، يملك المشغّل مسؤولية التسليم النهائي. ومن المتوقع
    أن يعيد الوكيل ملخصًا نصيًا عاديًا ليرسله المشغّل. و`--no-deliver` يبقي
    تلك النتيجة داخلية؛ ولا يسمح للوكيل بالإرسال مباشرة باستخدام
    أداة الرسائل بدلًا من ذلك.

    التصحيح:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    الوثائق: [وظائف Cron](/ar/automation/cron-jobs)، [المهام الخلفية](/ar/automation/tasks).

  </Accordion>

  <Accordion title="لماذا بدّلت عملية cron معزولة النماذج أو أعادت المحاولة مرة واحدة؟">
    عادةً ما يكون هذا مسار تبديل النموذج المباشر، وليس جدولة مكررة.

    يمكن لـ cron المعزول حفظ تسليم نموذج وقت التشغيل وإعادة المحاولة عندما
    يطلق التشغيل النشط `LiveSessionModelSwitchError`. وتحافظ
    إعادة المحاولة على الموفر/النموذج المُبدّل، وإذا كان التبديل يحمل override جديدًا لملف تعريف المصادقة، فإن cron
    تحفظه أيضًا قبل إعادة المحاولة.

    قواعد الاختيار ذات الصلة:

    - يفوز override نموذج خطاف Gmail أولًا عند الاقتضاء.
    - ثم `model` لكل وظيفة.
    - ثم أي override مخزن لنموذج جلسة cron.
    - ثم الاختيار العادي لنموذج الوكيل/الافتراضي.

    تكون حلقة إعادة المحاولة محدودة. فبعد المحاولة الأولية وإعادتَي تبديل،
    يجهض cron بدلًا من الدوران بلا نهاية.

    التصحيح:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    الوثائق: [وظائف Cron](/ar/automation/cron-jobs)، [CLI الخاص بـ cron](/cli/cron).

  </Accordion>

  <Accordion title="كيف أثبّت Skills على Linux؟">
    استخدم أوامر `openclaw skills` الأصلية أو أسقِط Skills في مساحة العمل الخاصة بك. واجهة Skills في macOS غير متاحة على Linux.
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

    تؤدي عمليات التثبيت الأصلية باستخدام `openclaw skills install` إلى الكتابة داخل الدليل `skills/`
    في مساحة العمل النشطة. ولا تثبّت CLI المنفصل `clawhub` إلا إذا كنت تريد نشر
    Skills الخاصة بك أو مزامنتها. وبالنسبة إلى التثبيتات المشتركة بين الوكلاء، ضع المهارة ضمن
    `~/.openclaw/skills` واستخدم `agents.defaults.skills` أو
    `agents.list[].skills` إذا أردت تضييق أي الوكلاء يستطيعون رؤيتها.

  </Accordion>

  <Accordion title="هل يمكن لـ OpenClaw تشغيل مهام وفق جدول أو باستمرار في الخلفية؟">
    نعم. استخدم مجدول Gateway:

    - **وظائف Cron** للمهام المجدولة أو المتكررة (تستمر عبر إعادة التشغيل).
    - **Heartbeat** للفحوصات الدورية الخاصة بـ "الجلسة الرئيسية".
    - **وظائف معزولة** لوكلاء مستقلين ينشرون ملخصات أو يسلّمون إلى الدردشات.

    الوثائق: [وظائف Cron](/ar/automation/cron-jobs)، [الأتمتة والمهام](/ar/automation)،
    [Heartbeat](/ar/gateway/heartbeat).

  </Accordion>

  <Accordion title="هل يمكنني تشغيل Skills خاصة بـ Apple/macOS فقط من Linux؟">
    ليس مباشرة. تُضبط Skills الخاصة بـ macOS بواسطة `metadata.openclaw.os` مع الثنائيات المطلوبة، ولا تظهر Skills في system prompt إلا عندما تكون مؤهلة على **مضيف Gateway**. وعلى Linux، لن تُحمّل Skills التي تعمل فقط على `darwin` (مثل `apple-notes` و`apple-reminders` و`things-mac`) ما لم تتجاوز هذا التقييد.

    لديك ثلاثة أنماط مدعومة:

    **الخيار A - شغّل Gateway على جهاز Mac (الأبسط).**
    شغّل Gateway حيث توجد ثنائيات macOS، ثم اتصل من Linux في [الوضع البعيد](#gateway-ports-already-running-and-remote-mode) أو عبر Tailscale. وستحمّل Skills بشكل طبيعي لأن مضيف Gateway هو macOS.

    **الخيار B - استخدم macOS node (من دون SSH).**
    شغّل Gateway على Linux، وأقرن macOS node (تطبيق شريط القوائم)، واضبط **Node Run Commands** على "Always Ask" أو "Always Allow" على جهاز Mac. ويمكن لـ OpenClaw أن يعامل Skills الخاصة بـ macOS على أنها مؤهلة عندما تكون الثنائيات المطلوبة موجودة على الـ node. ويشغّل الوكيل تلك Skills عبر أداة `nodes`. وإذا اخترت "Always Ask"، فإن الموافقة على "Always Allow" في المطالبة تضيف ذلك الأمر إلى قائمة السماح.

    **الخيار C - توكيل ثنائيات macOS عبر SSH (متقدم).**
    أبقِ Gateway على Linux، لكن اجعل ثنائيات CLI المطلوبة تُحل إلى أغلفة SSH تعمل على جهاز Mac. ثم تجاوز إعداد المهارة للسماح بـ Linux حتى تظل مؤهلة.

    1. أنشئ غلاف SSH للثنائي (مثال: `memo` لـ Apple Notes):

       ```bash
       #!/usr/bin/env bash
       set -euo pipefail
       exec ssh -T user@mac-host /opt/homebrew/bin/memo "$@"
       ```

    2. ضع الغلاف على `PATH` على مضيف Linux (مثل `~/bin/memo`).
    3. تجاوز metadata الخاصة بالمهارة (في مساحة العمل أو `~/.openclaw/skills`) للسماح بـ Linux:

       ```markdown
       ---
       name: apple-notes
       description: Manage Apple Notes via the memo CLI on macOS.
       metadata: { "openclaw": { "os": ["darwin", "linux"], "requires": { "bins": ["memo"] } } }
       ---
       ```

    4. ابدأ جلسة جديدة حتى تتجدد لقطة Skills.

  </Accordion>

  <Accordion title="هل لديكم تكامل مع Notion أو HeyGen؟">
    ليس مدمجًا حاليًا.

    الخيارات:

    - **Skill / plugin مخصص:** الأفضل للوصول الموثوق إلى API ‏(كل من Notion وHeyGen لهما API).
    - **أتمتة المتصفح:** تعمل من دون شيفرة لكنها أبطأ وأكثر هشاشة.

    إذا أردت الاحتفاظ بالسياق لكل عميل (سير عمل الوكالات)، فهناك نمط بسيط:

    - صفحة Notion واحدة لكل عميل (السياق + التفضيلات + العمل النشط).
    - اطلب من الوكيل جلب تلك الصفحة في بداية الجلسة.

    وإذا كنت تريد تكاملًا أصليًا، فافتح طلب ميزة أو ابنِ Skill
    تستهدف تلك الـ APIs.

    تثبيت Skills:

    ```bash
    openclaw skills install <skill-slug>
    openclaw skills update --all
    ```

    يتم وضع عمليات التثبيت الأصلية في دليل `skills/` ضمن مساحة العمل النشطة. وبالنسبة إلى Skills المشتركة بين الوكلاء، ضعها في `~/.openclaw/skills/<name>/SKILL.md`. وإذا كان يجب أن تراها بعض الوكلاء فقط، فاضبط `agents.defaults.skills` أو `agents.list[].skills`. وتتوقع بعض Skills وجود ثنائيات مثبّتة عبر Homebrew؛ وعلى Linux يعني ذلك Linuxbrew (راجع إدخال الأسئلة الشائعة الخاص بـ Homebrew على Linux أعلاه). راجع [Skills](/ar/tools/skills)، و[إعداد Skills](/ar/tools/skills-config)، و[ClawHub](/ar/tools/clawhub).

  </Accordion>

  <Accordion title="كيف أستخدم Chrome الحالي الذي سجلت الدخول فيه مع OpenClaw؟">
    استخدم ملف المتصفح المدمج `user`، الذي يتصل عبر Chrome DevTools MCP:

    ```bash
    openclaw browser --browser-profile user tabs
    openclaw browser --browser-profile user snapshot
    ```

    وإذا كنت تريد اسمًا مخصصًا، فأنشئ ملف MCP صريحًا:

    ```bash
    openclaw browser create-profile --name chrome-live --driver existing-session
    openclaw browser --browser-profile chrome-live tabs
    ```

    هذا المسار محلي على المضيف. وإذا كانت Gateway تعمل في مكان آخر، فإما أن تشغّل مضيف node على جهاز المتصفح أو تستخدم CDP عن بُعد بدلًا من ذلك.

    الحدود الحالية على `existing-session` / `user`:

    - الإجراءات تعتمد على ref، وليس على CSS-selector
    - تتطلب عمليات الرفع `ref` / `inputRef` وتدعم حاليًا ملفًا واحدًا في كل مرة
    - لا تزال `responsebody`، وتصدير PDF، واعتراض التنزيلات، والإجراءات الدفعية تحتاج إلى متصفح مُدار أو ملف CDP خام

  </Accordion>
</AccordionGroup>

## الحاويات الآمنة والذاكرة

<AccordionGroup>
  <Accordion title="هل توجد وثيقة مخصصة للحاويات الآمنة؟">
    نعم. راجع [الحاويات الآمنة](/ar/gateway/sandboxing). وبالنسبة إلى إعداد Docker تحديدًا (Gateway كاملة داخل Docker أو صور sandbox)، راجع [Docker](/ar/install/docker).
  </Accordion>

  <Accordion title="يبدو Docker محدودًا - كيف أفعّل الميزات الكاملة؟">
    الصورة الافتراضية تضع الأمان أولًا وتعمل باسم المستخدم `node`، ولذلك فهي لا
    تتضمن حزم النظام أو Homebrew أو المتصفحات المجمعة. ولإعداد أكمل:

    - اجعل `/home/node` دائمًا باستخدام `OPENCLAW_HOME_VOLUME` حتى تبقى الذاكرات المؤقتة.
    - ضمّن تبعيات النظام في الصورة باستخدام `OPENCLAW_DOCKER_APT_PACKAGES`.
    - ثبّت متصفحات Playwright عبر CLI المجمعة:
      `node /app/node_modules/playwright-core/cli.js install chromium`
    - اضبط `PLAYWRIGHT_BROWSERS_PATH` وتأكد من حفظ هذا المسار.

    الوثائق: [Docker](/ar/install/docker)، [المتصفح](/ar/tools/browser).

  </Accordion>

  <Accordion title="هل يمكنني إبقاء الرسائل الخاصة شخصية لكن جعل المجموعات عامة/ضمن sandbox باستخدام وكيل واحد؟">
    نعم - إذا كانت الحركة الخاصة لديك **رسائل خاصة** وكانت الحركة العامة لديك **مجموعات**.

    استخدم `agents.defaults.sandbox.mode: "non-main"` حتى تعمل جلسات المجموعة/القناة (المفاتيح غير الرئيسية) داخل Docker، بينما تبقى جلسة DM الرئيسية على المضيف. ثم قيّد الأدوات المتاحة في الجلسات ضمن sandbox عبر `tools.sandbox.tools`.

    شرح الإعداد + مثال إعداد: [المجموعات: رسائل خاصة شخصية + مجموعات عامة](/ar/channels/groups#pattern-personal-dms-public-groups-single-agent)

    مرجع الإعداد الأساسي: [إعداد Gateway](/ar/gateway/configuration-reference#agentsdefaultssandbox)

  </Accordion>

  <Accordion title="كيف أربط مجلدًا من المضيف داخل sandbox؟">
    اضبط `agents.defaults.sandbox.docker.binds` على `["host:path:mode"]` (مثل `"/home/user/src:/src:ro"`). تُدمج الروابط العامة + روابط كل وكيل؛ وتُتجاهل روابط كل وكيل عندما تكون `scope: "shared"`. استخدم `:ro` لأي شيء حساس وتذكّر أن الروابط تتجاوز جدران نظام الملفات الخاصة بـ sandbox.

    يتحقق OpenClaw من مصادر الربط مقارنةً بكل من المسار المُطبع والمسار القانوني الذي يتم حله عبر أعمق سلف موجود. وهذا يعني أن الهروب عبر symlink-parent ما زال يفشل بشكل مغلق حتى عندما لا يكون الجزء الأخير من المسار موجودًا بعد، ولا تزال فحوصات allowed-root تنطبق بعد حل الروابط الرمزية.

    راجع [الحاويات الآمنة](/ar/gateway/sandboxing#custom-bind-mounts) و[Sandbox مقابل سياسة الأداة مقابل الامتيازات المرتفعة](/ar/gateway/sandbox-vs-tool-policy-vs-elevated#bind-mounts-security-quick-check) للاطلاع على أمثلة وملاحظات السلامة.

  </Accordion>

  <Accordion title="كيف تعمل الذاكرة؟">
    ذاكرة OpenClaw هي مجرد ملفات Markdown في مساحة عمل الوكيل:

    - ملاحظات يومية في `memory/YYYY-MM-DD.md`
    - ملاحظات طويلة الأمد منتقاة في `MEMORY.md` (للجلسات الرئيسية/الخاصة فقط)

    كما يشغّل OpenClaw **تفريغًا صامتًا للذاكرة قبل الضغط** لتذكير النموذج
    بكتابة ملاحظات دائمة قبل الضغط التلقائي. ولا يعمل هذا إلا عندما تكون مساحة العمل
    قابلة للكتابة (تتخطى sandboxes للقراءة فقط ذلك). راجع [الذاكرة](/ar/concepts/memory).

  </Accordion>

  <Accordion title="تستمر الذاكرة في نسيان الأشياء. كيف أجعلها ثابتة؟">
    اطلب من البوت أن **يكتب الحقيقة في الذاكرة**. فالملاحظات طويلة الأمد مكانها `MEMORY.md`،
    والسياق قصير الأمد يذهب إلى `memory/YYYY-MM-DD.md`.

    ما زلنا نحسّن هذا المجال. ومن المفيد تذكير النموذج بتخزين الذكريات؛
    فهو يعرف ما الذي يجب فعله. وإذا استمر في النسيان، فتحقق من أن Gateway تستخدم
    مساحة العمل نفسها في كل تشغيل.

    الوثائق: [الذاكرة](/ar/concepts/memory)، [مساحة عمل الوكيل](/ar/concepts/agent-workspace).

  </Accordion>

  <Accordion title="هل تستمر الذاكرة إلى الأبد؟ ما الحدود؟">
    تعيش ملفات الذاكرة على القرص وتستمر حتى تحذفها. والحد هو
    مساحة التخزين لديك، وليس النموذج. أما **سياق الجلسة** فلا يزال محدودًا بنافذة سياق
    النموذج، لذلك قد تُضغط المحادثات الطويلة أو تُقتطع. ولهذا السبب
    يوجد بحث الذاكرة - فهو يعيد الأجزاء ذات الصلة فقط إلى السياق.

    الوثائق: [الذاكرة](/ar/concepts/memory)، [السياق](/ar/concepts/context).

  </Accordion>

  <Accordion title="هل يتطلب البحث الدلالي في الذاكرة OpenAI API key؟">
    نعم فقط إذا كنت تستخدم **OpenAI embeddings**. تغطي Codex OAuth الدردشة/الإكمالات
    ولا **تمنح** وصولًا إلى embeddings، لذا فإن **تسجيل الدخول باستخدام Codex (OAuth أو
    تسجيل دخول Codex CLI)** لا يفيد في البحث الدلالي في الذاكرة. ولا تزال OpenAI embeddings
    تحتاج إلى API key حقيقي (`OPENAI_API_KEY` أو `models.providers.openai.apiKey`).

    إذا لم تضبط موفرًا صراحةً، فإن OpenClaw يختار موفرًا تلقائيًا عندما
    يستطيع حل API key (ملفات تعريف المصادقة، أو `models.providers.*.apiKey`، أو متغيرات البيئة).
    وهو يفضّل OpenAI إذا أمكن حل مفتاح OpenAI، وإلا Gemini إذا أمكن حل مفتاح Gemini،
    ثم Voyage، ثم Mistral. وإذا لم يتوفر مفتاح بعيد، فسيظل
    بحث الذاكرة معطلًا حتى تقوم بتهيئته. وإذا كان لديك مسار نموذج محلي
    مهيأ وموجود، فإن OpenClaw
    يفضّل `local`. كما أن Ollama مدعومة عندما تضبط صراحةً
    `memorySearch.provider = "ollama"`.

    وإذا كنت تفضّل البقاء محليًا، فاضبط `memorySearch.provider = "local"` (واختياريًا
    `memorySearch.fallback = "none"`). وإذا كنت تريد Gemini embeddings، فاضبط
    `memorySearch.provider = "gemini"` ووفّر `GEMINI_API_KEY` (أو
    `memorySearch.remote.apiKey`). نحن ندعم نماذج embedding من **OpenAI وGemini وVoyage وMistral وOllama أو local**
    - راجع [الذاكرة](/ar/concepts/memory) للحصول على تفاصيل الإعداد.

  </Accordion>
</AccordionGroup>

## أماكن تخزين الأشياء على القرص

<AccordionGroup>
  <Accordion title="هل تُحفَظ كل البيانات المستخدمة مع OpenClaw محليًا؟">
    لا - **حالة OpenClaw محلية**، لكن **الخدمات الخارجية ما زالت ترى ما ترسله إليها**.

    - **محلية افتراضيًا:** الجلسات، وملفات الذاكرة، والإعداد، ومساحة العمل تعيش على مضيف Gateway
      (`~/.openclaw` + دليل مساحة العمل الخاص بك).
    - **بعيدة بحكم الضرورة:** الرسائل التي ترسلها إلى موفري النماذج (Anthropic/OpenAI/etc.) تذهب إلى
      APIs الخاصة بهم، كما تخزن منصات الدردشة (WhatsApp/Telegram/Slack/etc.) بيانات الرسائل على
      خوادمها.
    - **أنت تتحكم في الأثر:** استخدام النماذج المحلية يبقي المطالبات على جهازك، لكن
      حركة القنوات لا تزال تمر عبر خوادم القناة.

    ذو صلة: [مساحة عمل الوكيل](/ar/concepts/agent-workspace)، [الذاكرة](/ar/concepts/memory).

  </Accordion>

  <Accordion title="أين يخزن OpenClaw بياناته؟">
    كل شيء يعيش تحت `$OPENCLAW_STATE_DIR` (الافتراضي: `~/.openclaw`):

    | المسار                                                            | الغرض                                                            |
    | --------------------------------------------------------------- | ------------------------------------------------------------------ |
    | `$OPENCLAW_STATE_DIR/openclaw.json`                             | الإعداد الرئيسي (JSON5)                                                |
    | `$OPENCLAW_STATE_DIR/credentials/oauth.json`                    | استيراد OAuth قديم (يُنسخ إلى ملفات تعريف المصادقة عند أول استخدام)       |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth-profiles.json` | ملفات تعريف المصادقة (OAuth، وAPI keys، و`keyRef`/`tokenRef` الاختياريان)  |
    | `$OPENCLAW_STATE_DIR/secrets.json`                              | حمولة سرية اختيارية مدعومة بملف لموفري `file` SecretRef |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth.json`          | ملف توافق قديم (تُزال منه إدخالات `api_key` الثابتة)      |
    | `$OPENCLAW_STATE_DIR/credentials/`                              | حالة الموفر (مثل `whatsapp/<accountId>/creds.json`)            |
    | `$OPENCLAW_STATE_DIR/agents/`                                   | حالة كل وكيل (agentDir + الجلسات)                              |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                | سجل المحادثة والحالة (لكل وكيل)                           |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/sessions.json`   | بيانات تعريف الجلسات (لكل وكيل)                                       |

    المسار القديم لوكيل واحد: `~/.openclaw/agent/*` (يرحّله `openclaw doctor`).

    أما **مساحة العمل** الخاصة بك (`AGENTS.md`، وملفات الذاكرة، وSkills، إلخ) فهي منفصلة وتُضبط عبر `agents.defaults.workspace` (الافتراضي: `~/.openclaw/workspace`).

  </Accordion>

  <Accordion title="أين يجب أن توجد AGENTS.md / SOUL.md / USER.md / MEMORY.md؟">
    تعيش هذه الملفات في **مساحة عمل الوكيل**، وليس في `~/.openclaw`.

    - **مساحة العمل (لكل وكيل):** `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`,
      `MEMORY.md` (أو البديل القديم `memory.md` عند غياب `MEMORY.md`)،
      `memory/YYYY-MM-DD.md`، و`HEARTBEAT.md` اختياريًا.
    - **دليل الحالة (`~/.openclaw`)**: الإعداد، وحالة القنوات/الموفّرين، وملفات تعريف المصادقة، والجلسات، والسجلات،
      وSkills المشتركة (`~/.openclaw/skills`).

    مساحة العمل الافتراضية هي `~/.openclaw/workspace`، ويمكن ضبطها عبر:

    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
    }
    ```

    إذا كان البوت "ينسى" بعد إعادة التشغيل، فتأكد من أن Gateway تستخدم
    مساحة العمل نفسها في كل تشغيل (وتذكر: الوضع البعيد يستخدم **مساحة عمل مضيف gateway**،
    لا مساحة عمل حاسوبك المحمول المحلي).

    نصيحة: إذا أردت سلوكًا أو تفضيلًا دائمًا، فاطلب من البوت أن **يكتبه في
    AGENTS.md أو MEMORY.md** بدلًا من الاعتماد على سجل الدردشة.

    راجع [مساحة عمل الوكيل](/ar/concepts/agent-workspace) و[الذاكرة](/ar/concepts/memory).

  </Accordion>

  <Accordion title="استراتيجية النسخ الاحتياطي الموصى بها">
    ضع **مساحة عمل الوكيل** في مستودع git **خاص** وانسخها احتياطيًا إلى مكان
    خاص (مثل GitHub الخاص). فهذا يلتقط الذاكرة + ملفات AGENTS/SOUL/USER،
    ويسمح لك باستعادة "عقل" المساعد لاحقًا.

    **لا** تقم بعمل commit لأي شيء ضمن `~/.openclaw` (بيانات الاعتماد، أو الجلسات، أو الرموز المميزة، أو حمولة الأسرار المشفرة).
    وإذا كنت تحتاج إلى استعادة كاملة، فانسخ كلًا من مساحة العمل ودليل الحالة
    كلًا على حدة (راجع سؤال الترحيل أعلاه).

    الوثائق: [مساحة عمل الوكيل](/ar/concepts/agent-workspace).

  </Accordion>

  <Accordion title="كيف أزيل OpenClaw بالكامل؟">
    راجع الدليل المخصص: [إلغاء التثبيت](/ar/install/uninstall).
  </Accordion>

  <Accordion title="هل يمكن للوكلاء العمل خارج مساحة العمل؟">
    نعم. فمساحة العمل هي **cwd افتراضي** ومرساة للذاكرة، وليست sandbox صارمة.
    تُحل المسارات النسبية داخل مساحة العمل، لكن المسارات المطلقة يمكنها الوصول إلى
    مواقع أخرى على المضيف ما لم يكن sandboxing مفعّلًا. وإذا كنت تحتاج إلى عزل، فاستخدم
    [`agents.defaults.sandbox`](/ar/gateway/sandboxing) أو إعدادات sandbox لكل وكيل. وإذا كنت
    تريد أن يكون مستودع ما هو دليل العمل الافتراضي، فاجعل
    `workspace` لذلك الوكيل تشير إلى جذر المستودع. ومستودع OpenClaw هو مجرد
    شيفرة مصدر؛ فافصل مساحة العمل عنه ما لم تكن تريد عمدًا أن يعمل الوكيل داخله.

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
    حالة الجلسة يملكها **مضيف gateway**. فإذا كنت في الوضع البعيد، فإن مخزن الجلسات الذي يهمك موجود على الجهاز البعيد، لا على حاسوبك المحمول المحلي. راجع [إدارة الجلسات](/ar/concepts/session).
  </Accordion>
</AccordionGroup>

## أساسيات الإعداد

<AccordionGroup>
  <Accordion title="ما صيغة الإعداد؟ وأين يوجد؟">
    يقرأ OpenClaw إعداد **JSON5** اختياريًا من `$OPENCLAW_CONFIG_PATH` (الافتراضي: `~/.openclaw/openclaw.json`):

    ```
    $OPENCLAW_CONFIG_PATH
    ```

    وإذا كان الملف مفقودًا، فإنه يستخدم افتراضيات آمنة إلى حد ما (بما في ذلك مساحة عمل افتراضية هي `~/.openclaw/workspace`).

  </Accordion>

  <Accordion title='لقد ضبطت gateway.bind: "lan" (أو "tailnet") والآن لا شيء يستمع / وتقول الواجهة unauthorized'>
    يتطلب الربط على غير loopback **مسار مصادقة صالحًا للبوابة**. وهذا يعني عمليًا:

    - مصادقة shared-secret: رمز مميز أو كلمة مرور
    - `gateway.auth.mode: "trusted-proxy"` خلف موجه عكسي مدرك للهوية مضبوط بشكل صحيح وغير loopback

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

    - لا يفعّل `gateway.remote.token` / `.password` مصادقة البوابة المحلية بمفردهما.
    - يمكن أن تستخدم مسارات النداء المحلية `gateway.remote.*` كبديل احتياطي فقط عندما لا تكون `gateway.auth.*` مضبوطة.
    - بالنسبة إلى مصادقة كلمة المرور، اضبط `gateway.auth.mode: "password"` مع `gateway.auth.password` (أو `OPENCLAW_GATEWAY_PASSWORD`) بدلًا من ذلك.
    - إذا كانت `gateway.auth.token` / `gateway.auth.password` مهيأة صراحةً عبر SecretRef ولم يمكن حلها، فإن الحل يفشل بشكل مغلق (من دون بديل بعيد يُخفي ذلك).
    - تتم مصادقة إعدادات Control UI باستخدام `connect.params.auth.token` أو `connect.params.auth.password` (مخزنة في إعدادات التطبيق/الواجهة). أما أوضاع حمل الهوية مثل Tailscale Serve أو `trusted-proxy` فتستخدم رؤوس الطلبات بدلًا من ذلك. وتجنب وضع shared secrets في عناوين URL.
    - مع `gateway.auth.mode: "trusted-proxy"`، فإن الموجهات العكسية loopback على المضيف نفسه لا تفي أيضًا بمصادقة trusted-proxy. بل يجب أن يكون الموجه الموثوق مصدرًا غير loopback ومهيأً.

  </Accordion>

  <Accordion title="لماذا أحتاج إلى رمز مميز على localhost الآن؟">
    يفرض OpenClaw مصادقة البوابة افتراضيًا، بما في ذلك loopback. وفي المسار الافتراضي المعتاد يعني هذا مصادقة عبر الرمز المميز: فإذا لم يكن هناك مسار مصادقة صريح مهيأ، فإن بدء تشغيل البوابة يحل إلى وضع token ويولّد واحدًا تلقائيًا ويخزنه في `gateway.auth.token`، لذا **يجب على عملاء WS المحليين المصادقة**. وهذا يمنع العمليات المحلية الأخرى من استدعاء Gateway.

    وإذا كنت تفضّل مسار مصادقة مختلفًا، فيمكنك اختيار وضع كلمة المرور صراحةً (أو، بالنسبة إلى الموجهات العكسية غير loopback والمدركة للهوية، `trusted-proxy`). وإذا **كنت حقًا** تريد loopback مفتوحة، فاضبط `gateway.auth.mode: "none"` صراحةً في إعدادك. ويمكن لـ Doctor أن يولد لك رمزًا مميزًا في أي وقت: `openclaw doctor --generate-gateway-token`.

  </Accordion>

  <Accordion title="هل يجب أن أعيد التشغيل بعد تغيير الإعداد؟">
    تراقب Gateway الإعداد وتدعم إعادة التحميل الساخنة:

    - `gateway.reload.mode: "hybrid"` (الافتراضي): يطبق التغييرات الآمنة مباشرة، ويعيد التشغيل للتغييرات الحرجة
    - كما أن `hot` و`restart` و`off` مدعومة أيضًا

  </Accordion>

  <Accordion title="كيف أعطّل العبارات الطريفة في CLI؟">
    اضبط `cli.banner.taglineMode` في الإعداد:

    ```json5
    {
      cli: {
        banner: {
          taglineMode: "off", // random | default | off
        },
      },
    }
    ```

    - `off`: يُخفي نص الشعار مع إبقاء سطر عنوان الشعار/الإصدار.
    - `default`: يستخدم `All your chats, one OpenClaw.` في كل مرة.
    - `random`: شعارات طريفة/موسمية متعاقبة (السلوك الافتراضي).
    - وإذا كنت لا تريد أي شعار إطلاقًا، فاضبط متغير البيئة `OPENCLAW_HIDE_BANNER=1`.

  </Accordion>

  <Accordion title="كيف أفعّل web search (وweb fetch)؟">
    تعمل `web_fetch` من دون API key. أما `web_search` فتعتمد على
    الموفر الذي اخترته:

    - يتطلب الموفّرون المدعومون عبر API مثل Brave وExa وFirecrawl وGemini وGrok وKimi وMiniMax Search وPerplexity وTavily إعداد API key المعتاد لديهم.
    - Ollama Web Search لا يحتاج إلى مفتاح، لكنه يستخدم مضيف Ollama المهيأ لديك ويتطلب `ollama signin`.
    - DuckDuckGo لا يحتاج إلى مفتاح، لكنه تكامل غير رسمي قائم على HTML.
    - SearXNG لا يحتاج إلى مفتاح/ويصلح للاستضافة الذاتية؛ اضبط `SEARXNG_BASE_URL` أو `plugins.entries.searxng.config.webSearch.baseUrl`.

    **الموصى به:** شغّل `openclaw configure --section web` واختر موفرًا.
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
              provider: "firecrawl", // اختياري؛ احذفه للكشف التلقائي
            },
          },
        },
    }
    ```

    يعيش الآن إعداد web-search الخاص بكل موفر تحت `plugins.entries.<plugin>.config.webSearch.*`.
    وما زالت مسارات الموفر القديمة `tools.web.search.*` تُحمّل مؤقتًا للتوافق، لكن لا ينبغي استخدامها في الإعدادات الجديدة.
    يعيش إعداد fallback الخاص بـ Firecrawl web-fetch تحت `plugins.entries.firecrawl.config.webFetch.*`.

    ملاحظات:

    - إذا كنت تستخدم قوائم السماح، فأضف `web_search`/`web_fetch`/`x_search` أو `group:web`.
    - تكون `web_fetch` مفعلة افتراضيًا (ما لم تُعطل صراحةً).
    - إذا تم حذف `tools.web.fetch.provider`، فإن OpenClaw يكتشف تلقائيًا أول موفر fetch احتياطي جاهز من بيانات الاعتماد المتاحة. والموفر المجمّع اليوم هو Firecrawl.
    - تقرأ الخدمات متغيرات البيئة من `~/.openclaw/.env` (أو من بيئة الخدمة).

    الوثائق: [أدوات الويب](/ar/tools/web).

  </Accordion>

  <Accordion title="قام config.apply بمسح إعدادي. كيف أستعيده وأتجنب هذا؟">
    يقوم `config.apply` باستبدال **الإعداد بالكامل**. فإذا أرسلت كائنًا جزئيًا، فسيُزال
    كل شيء آخر.

    الاستعادة:

    - استعد من نسخة احتياطية (git أو نسخة من `~/.openclaw/openclaw.json`).
    - إذا لم تكن لديك نسخة احتياطية، فأعد تشغيل `openclaw doctor` وأعد تهيئة channels/models.
    - إذا كان هذا غير متوقع، فافتح تقرير خطأ وأرفق آخر إعداد معروف أو أي نسخة احتياطية.
    - يمكن لوكيل برمجة محلي غالبًا إعادة بناء إعداد صالح من السجلات أو السجل التاريخي.

    لتجنب ذلك:

    - استخدم `openclaw config set` للتغييرات الصغيرة.
    - استخدم `openclaw configure` للتحرير التفاعلي.
    - استخدم `config.schema.lookup` أولًا عندما لا تكون متأكدًا من المسار الدقيق أو شكل الحقل؛ فهو يعيد عقدة schema سطحية مع ملخصات الأبناء المباشرين للتدرج.
    - استخدم `config.patch` للتحرير الجزئي عبر RPC؛ واحتفظ بـ `config.apply` لاستبدال الإعداد الكامل فقط.
    - إذا كنت تستخدم أداة `gateway` المخصصة للمالك فقط من داخل تشغيل الوكيل، فستظل ترفض الكتابة إلى `tools.exec.ask` / `tools.exec.security` (بما في ذلك الأسماء القديمة `tools.bash.*` التي تُطبّع إلى مسارات exec المحمية نفسها).

    الوثائق: [الإعداد](/cli/config)، [التكوين](/cli/configure)، [Doctor](/ar/gateway/doctor).

  </Accordion>

  <Accordion title="كيف أشغّل Gateway مركزية مع عمال متخصصين عبر الأجهزة؟">
    النمط الشائع هو **Gateway واحدة** (مثل Raspberry Pi) مع **nodes** و**agents**:

    - **Gateway (مركزية):** تملك القنوات (Signal/WhatsApp)، والتوجيه، والجلسات.
    - **Nodes (الأجهزة):** تتصل أجهزة Mac/iOS/Android كأجهزة طرفية وتعرض أدوات محلية (`system.run`, `canvas`, `camera`).
    - **Agents (العمال):** عقول/مساحات عمل منفصلة لأدوار متخصصة (مثل "عمليات Hetzner" أو "بيانات شخصية").
    - **الوكلاء الفرعيون:** ينشئون عملًا في الخلفية من وكيل رئيسي عندما تريد التوازي.
    - **TUI:** يتصل بـ Gateway ويبدّل بين الوكلاء/الجلسات.

    الوثائق: [Nodes](/ar/nodes)، [الوصول البعيد](/ar/gateway/remote)، [التوجيه متعدد الوكلاء](/ar/concepts/multi-agent)، [الوكلاء الفرعيون](/ar/tools/subagents)، [TUI](/web/tui).

  </Accordion>

  <Accordion title="هل يمكن لمتصفح OpenClaw أن يعمل في وضع headless؟">
    نعم. إنه خيار إعداد:

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

    القيمة الافتراضية هي `false` ‏(headful). ويزيد headless احتمال تفعيل فحوصات مكافحة الروبوتات في بعض المواقع. راجع [المتصفح](/ar/tools/browser).

    يستخدم headless **محرك Chromium نفسه** ويعمل مع معظم الأتمتة (النماذج، والنقرات، والاستخراج، وتسجيلات الدخول). والفروقات الأساسية:

    - لا توجد نافذة متصفح مرئية (استخدم لقطات الشاشة إذا كنت بحاجة إلى عناصر بصرية).
    - بعض المواقع أكثر تشددًا مع الأتمتة في وضع headless (CAPTCHAs، مكافحة الروبوتات).
      فمثلًا، يقوم X/Twitter كثيرًا بحظر الجلسات headless.

  </Accordion>

  <Accordion title="كيف أستخدم Brave للتحكم في المتصفح؟">
    اضبط `browser.executablePath` على ثنائي Brave لديك (أو أي متصفح آخر مبني على Chromium) ثم أعد تشغيل Gateway.
    راجع أمثلة الإعداد الكاملة في [المتصفح](/ar/tools/browser#use-brave-or-another-chromium-based-browser).
  </Accordion>
</AccordionGroup>

## البوابات البعيدة وnodes

<AccordionGroup>
  <Accordion title="كيف تنتشر الأوامر بين Telegram وgateway وnodes؟">
    تتم معالجة رسائل Telegram بواسطة **gateway**. وتشغّل gateway الوكيل
    وبعد ذلك فقط تستدعي nodes عبر **Gateway WebSocket** عندما تكون هناك حاجة إلى أداة node:

    Telegram → Gateway → Agent → `node.*` → Node → Gateway → Telegram

    لا ترى nodes حركة المرور الواردة من الموفّر؛ فهي تستقبل فقط نداءات node RPC.

  </Accordion>

  <Accordion title="كيف يمكن لوكيلي الوصول إلى حاسوبي إذا كانت Gateway مستضافة عن بُعد؟">
    الإجابة المختصرة: **أقرِن حاسوبك بوصفه node**. تعمل Gateway في مكان آخر، لكنها تستطيع
    استدعاء أدوات `node.*` ‏(الشاشة، والكاميرا، والنظام) على جهازك المحلي عبر Gateway WebSocket.

    إعداد نموذجي:

    1. شغّل Gateway على المضيف دائم التشغيل (VPS/خادم منزلي).
    2. ضع مضيف Gateway + حاسوبك على tailnet نفسها.
    3. تأكد من أن WS الخاص بـ Gateway قابل للوصول (ربط tailnet أو نفق SSH).
    4. افتح تطبيق macOS محليًا واتصل في وضع **Remote over SSH** (أو tailnet مباشر)
       حتى يستطيع التسجيل بوصفه node.
    5. وافق على node على Gateway:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    لا يلزم أي جسر TCP منفصل؛ إذ تتصل nodes عبر Gateway WebSocket.

    تذكير أمني: إقران macOS node يتيح `system.run` على ذلك الجهاز. ولا
    تقرن إلا الأجهزة التي تثق بها، وراجع [الأمان](/ar/gateway/security).

    الوثائق: [Nodes](/ar/nodes)، [بروتوكول Gateway](/ar/gateway/protocol)، [الوضع البعيد على macOS](/ar/platforms/mac/remote)، [الأمان](/ar/gateway/security).

  </Accordion>

  <Accordion title="Tailscale متصل لكنني لا أتلقى أي ردود. ماذا الآن؟">
    تحقق من الأساسيات:

    - تعمل Gateway: ‏`openclaw gateway status`
    - صحة Gateway: ‏`openclaw status`
    - صحة القناة: ‏`openclaw channels status`

    ثم تحقق من المصادقة والتوجيه:

    - إذا كنت تستخدم Tailscale Serve، فتأكد من أن `gateway.auth.allowTailscale` مضبوطة بشكل صحيح.
    - إذا كنت تتصل عبر نفق SSH، فتأكد من أن النفق المحلي يعمل ويشير إلى المنفذ الصحيح.
    - تأكد من أن قوائم السماح لديك (DM أو group) تتضمن حسابك.

    الوثائق: [Tailscale](/ar/gateway/tailscale)، [الوصول البعيد](/ar/gateway/remote)، [القنوات](/ar/channels).

  </Accordion>

  <Accordion title="هل يمكن لنسختين من OpenClaw التحدث مع بعضهما بعضًا (محلي + VPS)؟">
    نعم. لا يوجد جسر "bot-to-bot" مدمج، لكن يمكنك توصيل ذلك بعدة
    طرق موثوقة:

    **الأبسط:** استخدم قناة دردشة عادية يمكن لكلا البوتين الوصول إليها (Telegram/Slack/WhatsApp).
    اجعل Bot A يرسل رسالة إلى Bot B، ثم دع Bot B يرد كالمعتاد.

    **جسر CLI (عام):** شغّل نصًا برمجيًا يستدعي Gateway الأخرى باستخدام
    `openclaw agent --message ... --deliver`، مستهدفًا دردشة يستمع فيها البوت الآخر.
    وإذا كان أحد البوتين على VPS بعيد، فاجعل CLI الخاص بك يشير إلى تلك Gateway البعيدة
    عبر SSH/Tailscale (راجع [الوصول البعيد](/ar/gateway/remote)).

    نمط مثال (شغّله من جهاز يستطيع الوصول إلى Gateway المستهدفة):

    ```bash
    openclaw agent --message "Hello from local bot" --deliver --channel telegram --reply-to <chat-id>
    ```

    نصيحة: أضف حاجزًا حتى لا يدور البوتان في حلقة بلا نهاية (الرد عند الإشارة فقط، أو
    قوائم سماح القنوات، أو قاعدة "لا ترد على رسائل البوتات").

    الوثائق: [الوصول البعيد](/ar/gateway/remote)، [CLI الخاص بالوكيل](/cli/agent)، [إرسال الوكيل](/ar/tools/agent-send).

  </Accordion>

  <Accordion title="هل أحتاج إلى VPS منفصل لكل وكيل؟">
    لا. يمكن لـ Gateway واحدة استضافة عدة وكلاء، لكل منهم مساحة عمله وافتراضيات نموذجه
    وتوجيهه الخاص. وهذا هو الإعداد المعتاد، وهو أرخص وأبسط بكثير من تشغيل
    VPS واحد لكل وكيل.

    استخدم VPSes منفصلة فقط عندما تحتاج إلى عزل صارم (حدود أمان) أو إلى
    إعدادات مختلفة جدًا لا تريد مشاركتها. وإلا فاحتفظ بـ Gateway واحدة
    واستخدم عدة وكلاء أو وكلاء فرعيين.

  </Accordion>

  <Accordion title="هل هناك فائدة من استخدام node على حاسوبي المحمول الشخصي بدل SSH من VPS؟">
    نعم - تُعد nodes الطريقة الأساسية للوصول إلى حاسوبك المحمول من Gateway بعيدة، وهي
    تفتح أكثر من مجرد وصول إلى shell. تعمل Gateway على macOS/Linux ‏(وعلى Windows عبر WSL2) وهي
    خفيفة الوزن (يكفي VPS صغير أو جهاز من فئة Raspberry Pi؛ و4 GB RAM أكثر من كافية)، لذا فإن
    الإعداد الشائع هو مضيف دائم التشغيل + حاسوبك المحمول بوصفه node.

    - **لا حاجة إلى SSH inbound.** تتصل nodes خارجيًا إلى Gateway WebSocket وتستخدم إقران الأجهزة.
    - **عناصر تحكم تنفيذ أكثر أمانًا.** يخضع `system.run` لقوائم السماح/الموافقات الخاصة بـ node على ذلك الحاسوب المحمول.
    - **أدوات أجهزة أكثر.** تعرض nodes كلًا من `canvas` و`camera` و`screen` بالإضافة إلى `system.run`.
    - **أتمتة متصفح محلية.** أبقِ Gateway على VPS، لكن شغّل Chrome محليًا عبر مضيف node على الحاسوب المحمول، أو اتصل بـ Chrome المحلي على المضيف عبر Chrome MCP.

    SSH جيد للوصول المؤقت إلى shell، لكن nodes أبسط لسير العمل المستمر للوكلاء
    وأتمتة الأجهزة.

    الوثائق: [Nodes](/ar/nodes)، [CLI الخاص بـ Nodes](/cli/nodes)، [المتصفح](/ar/tools/browser).

  </Accordion>

  <Accordion title="هل تشغّل nodes خدمة gateway؟">
    لا. يجب أن تعمل **بوابة واحدة** فقط لكل مضيف ما لم تكن تشغّل عمدًا ملفات تعريف معزولة (راجع [بوابات متعددة](/ar/gateway/multiple-gateways)). وnodes أجهزة طرفية تتصل
    بالبوابة (nodes على iOS/Android، أو "وضع node" في تطبيق شريط القوائم على macOS). أما بالنسبة إلى
    مضيفي node عديمي الواجهة والتحكم عبر CLI، فراجع [CLI الخاص بمضيف node](/cli/node).

    يلزم إعادة تشغيل كاملة لتغييرات `gateway` و`discovery` و`canvasHost`.

  </Accordion>

  <Accordion title="هل توجد طريقة API / RPC لتطبيق الإعداد؟">
    نعم.

    - `config.schema.lookup`: فحص شجرة إعداد فرعية واحدة مع عقدة schema سطحية، وتلميح UI المطابق، وملخصات الأبناء المباشرين قبل الكتابة
    - `config.get`: جلب اللقطة الحالية + hash
    - `config.patch`: تحديث جزئي آمن (مفضل لمعظم عمليات تحرير RPC)
    - `config.apply`: تحقق + استبدال الإعداد الكامل، ثم إعادة تشغيل
    - لا تزال أداة runtime `gateway` المخصصة للمالك فقط ترفض إعادة كتابة `tools.exec.ask` / `tools.exec.security`؛ وتُطبَّع الأسماء القديمة `tools.bash.*` إلى مسارات exec المحمية نفسها

  </Accordion>

  <Accordion title="الحد الأدنى المعقول من الإعداد لأول تثبيت">
    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
      channels: { whatsapp: { allowFrom: ["+15555550123"] } },
    }
    ```

    يضبط هذا مساحة العمل لديك ويقيّد من يمكنه تشغيل البوت.

  </Accordion>

  <Accordion title="كيف أعد Tailscale على VPS وأتصل من جهازي Mac؟">
    خطوات دنيا:

    1. **ثبّت وسجل الدخول على VPS**

       ```bash
       curl -fsSL https://tailscale.com/install.sh | sh
       sudo tailscale up
       ```

    2. **ثبّت وسجل الدخول على جهاز Mac**
       - استخدم تطبيق Tailscale وسجل الدخول إلى tailnet نفسها.
    3. **فعّل MagicDNS (موصى به)**
       - في وحدة تحكم إدارة Tailscale، فعّل MagicDNS حتى يحصل VPS على اسم ثابت.
    4. **استخدم اسم مضيف tailnet**
       - SSH: ‏`ssh user@your-vps.tailnet-xxxx.ts.net`
       - Gateway WS: ‏`ws://your-vps.tailnet-xxxx.ts.net:18789`

    إذا كنت تريد Control UI من دون SSH، فاستخدم Tailscale Serve على VPS:

    ```bash
    openclaw gateway --tailscale serve
    ```

    هذا يبقي gateway مربوطة على loopback ويكشف HTTPS عبر Tailscale. راجع [Tailscale](/ar/gateway/tailscale).

  </Accordion>

  <Accordion title="كيف أوصل Mac node بـ Gateway بعيدة (Tailscale Serve)؟">
    يكشف Serve كلًا من **Control UI + WS الخاصين بـ Gateway**. وتتصل nodes عبر نقطة نهاية Gateway WS نفسها.

    الإعداد الموصى به:

    1. **تأكد من أن VPS + Mac على tailnet نفسها**.
    2. **استخدم تطبيق macOS في وضع Remote** (يمكن أن يكون هدف SSH هو اسم مضيف tailnet).
       سيقوم التطبيق بعمل نفق لمنفذ Gateway ويتصل بوصفه node.
    3. **وافق على node** على gateway:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    الوثائق: [بروتوكول Gateway](/ar/gateway/protocol)، [Discovery](/ar/gateway/discovery)، [الوضع البعيد على macOS](/ar/platforms/mac/remote).

  </Accordion>

  <Accordion title="هل ينبغي أن أثبّت على حاسوب محمول ثانٍ أم أضيف node فقط؟">
    إذا كنت تحتاج فقط إلى **أدوات محلية** ‏(الشاشة/الكاميرا/exec) على الحاسوب المحمول الثاني، فأضفه بوصفه
    **node**. فهذا يبقي Gateway واحدة ويتجنب تكرار الإعداد. وأدوات node المحلية
    حاليًا خاصة بـ macOS فقط، لكننا نخطط لتوسيعها إلى أنظمة تشغيل أخرى.

    لا تثبّت Gateway ثانية إلا عندما تحتاج إلى **عزل صارم** أو إلى بوتين منفصلين بالكامل.

    الوثائق: [Nodes](/ar/nodes)، [CLI الخاص بـ Nodes](/cli/nodes)، [بوابات متعددة](/ar/gateway/multiple-gateways).

  </Accordion>
</AccordionGroup>

## متغيرات البيئة وتحميل .env

<AccordionGroup>
  <Accordion title="كيف يحمّل OpenClaw متغيرات البيئة؟">
    يقرأ OpenClaw متغيرات البيئة من العملية الأب (shell، أو launchd/systemd، أو CI، إلخ)، ويحمّل أيضًا:

    - `.env` من دليل العمل الحالي
    - `.env` عالمية احتياطية من `~/.openclaw/.env` ‏(أي `$OPENCLAW_STATE_DIR/.env`)

    لا يقوم أي من ملفي `.env` بتجاوز متغيرات البيئة الموجودة أصلًا.

    يمكنك أيضًا تعريف متغيرات بيئة داخلية في الإعداد (تُطبق فقط إذا كانت مفقودة من بيئة العملية):

    ```json5
    {
      env: {
        OPENROUTER_API_KEY: "sk-or-...",
        vars: { GROQ_API_KEY: "gsk-..." },
      },
    }
    ```

    راجع [/environment](/ar/help/environment) للاطلاع على الأولوية الكاملة والمصادر.

  </Accordion>

  <Accordion title="بدأت Gateway عبر الخدمة واختفت متغيرات البيئة الخاصة بي. ماذا الآن؟">
    إصلاحان شائعان:

    1. ضع المفاتيح المفقودة في `~/.openclaw/.env` حتى يتم التقاطها حتى عندما لا ترث الخدمة بيئة shell الخاصة بك.
    2. فعّل استيراد shell ‏(تسهيل اختياري):

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

    يشغّل هذا shell تسجيل الدخول لديك ويستورد فقط المفاتيح المتوقعة المفقودة (من دون أي تجاوز). مقابلات متغيرات البيئة:
    `OPENCLAW_LOAD_SHELL_ENV=1`, `OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`.

  </Accordion>

  <Accordion title='لقد ضبطت COPILOT_GITHUB_TOKEN، لكن models status تعرض "Shell env: off." لماذا؟'>
    يعرض `openclaw models status` ما إذا كان **استيراد shell env** مفعّلًا. ولا تعني عبارة "Shell env: off"
    أن متغيرات البيئة لديك مفقودة - بل تعني فقط أن OpenClaw لن يحمّل
    shell تسجيل الدخول لديك تلقائيًا.

    إذا كانت Gateway تعمل بوصفها خدمة (launchd/systemd)، فلن ترث
    بيئة shell الخاصة بك. أصلح ذلك عبر أحد هذه الخيارات:

    1. ضع الرمز المميز في `~/.openclaw/.env`:

       ```
       COPILOT_GITHUB_TOKEN=...
       ```

    2. أو فعّل استيراد shell (`env.shellEnv.enabled: true`).
    3. أو أضفه إلى كتلة `env` في الإعداد (يُطبق فقط إذا كان مفقودًا).

    ثم أعد تشغيل gateway وأعد الفحص:

    ```bash
    openclaw models status
    ```

    تتم قراءة Copilot tokens من `COPILOT_GITHUB_TOKEN` (وأيضًا `GH_TOKEN` / `GITHUB_TOKEN`).
    راجع [/concepts/model-providers](/ar/concepts/model-providers) و[/environment](/ar/help/environment).

  </Accordion>
</AccordionGroup>

## الجلسات والدردشات المتعددة

<AccordionGroup>
  <Accordion title="كيف أبدأ محادثة جديدة؟">
    أرسل `/new` أو `/reset` كرسالة مستقلة. راجع [إدارة الجلسات](/ar/concepts/session).
  </Accordion>

  <Accordion title="هل تُعاد تعيين الجلسات تلقائيًا إذا لم أرسل /new أبدًا؟">
    يمكن أن تنتهي صلاحية الجلسات بعد `session.idleMinutes`، لكن هذا **معطل افتراضيًا** (الافتراضي **0**).
    اضبطها على قيمة موجبة لتفعيل انتهاء الصلاحية بسبب الخمول. وعند التفعيل، فإن الرسالة **التالية**
    بعد فترة الخمول تبدأ معرّف جلسة جديدًا لذلك المفتاح الخاص بالدردشة.
    وهذا لا يحذف النصوص - بل يبدأ جلسة جديدة فقط.

    ```json5
    {
      session: {
        idleMinutes: 240,
      },
    }
    ```

  </Accordion>

  <Accordion title="هل توجد طريقة لتكوين فريق من نسخ OpenClaw (رئيس تنفيذي واحد والعديد من الوكلاء)؟">
    نعم، عبر **التوجيه متعدد الوكلاء** و**الوكلاء الفرعيين**. يمكنك إنشاء وكيل
    منسق واحد وعدة وكلاء عاملين مع مساحات العمل والنماذج الخاصة بهم.

    ومع ذلك، يُفضّل النظر إلى هذا على أنه **تجربة ممتعة**. فهو كثيف من ناحية الرموز وغالبًا
    أقل كفاءة من استخدام بوت واحد مع جلسات منفصلة. والنموذج المعتاد الذي
    نتصوره هو بوت واحد تتحدث إليه، مع جلسات مختلفة للعمل المتوازي. كما يمكن لذلك
    البوت أن ينشئ وكلاء فرعيين عند الحاجة.

    الوثائق: [التوجيه متعدد الوكلاء](/ar/concepts/multi-agent)، [الوكلاء الفرعيون](/ar/tools/subagents)، [CLI الخاص بالوكلاء](/cli/agents).

  </Accordion>

  <Accordion title="لماذا قُطع السياق في منتصف المهمة؟ كيف أتجنب ذلك؟">
    يقتصر سياق الجلسة على نافذة النموذج. ويمكن للدردشات الطويلة، أو مخارج الأدوات الكبيرة، أو
    كثرة الملفات أن تؤدي إلى الضغط أو القطع.

    ما الذي يساعد:

    - اطلب من البوت أن يلخص الحالة الحالية ويكتبها في ملف.
    - استخدم `/compact` قبل المهام الطويلة، و`/new` عند تبديل الموضوعات.
    - احتفظ بالسياق المهم في مساحة العمل واطلب من البوت قراءته مجددًا.
    - استخدم وكلاء فرعيين للعمل الطويل أو المتوازي حتى تبقى الدردشة الرئيسية أصغر.
    - اختر نموذجًا بنافذة سياق أكبر إذا كان هذا يحدث كثيرًا.

  </Accordion>

  <Accordion title="كيف أعيد تعيين OpenClaw بالكامل مع إبقائه مثبتًا؟">
    استخدم أمر إعادة التعيين:

    ```bash
    openclaw reset
    ```

    إعادة تعيين كاملة غير تفاعلية:

    ```bash
    openclaw reset --scope full --yes --non-interactive
    ```

    ثم أعد تشغيل الإعداد:

    ```bash
    openclaw onboard --install-daemon
    ```

    ملاحظات:

    - تعرض التهيئة الأولية أيضًا **إعادة تعيين** إذا رأت إعدادًا موجودًا. راجع [التهيئة الأولية (CLI)](/ar/start/wizard).
    - إذا كنت تستخدم ملفات تعريف (`--profile` / `OPENCLAW_PROFILE`)، فأعد تعيين كل دليل حالة (الافتراضيات هي `~/.openclaw-<profile>`).
    - إعادة تعيين Dev: ‏`openclaw gateway --dev --reset` ‏(للتطوير فقط؛ تمسح إعداد dev + بيانات الاعتماد + الجلسات + مساحة العمل).

  </Accordion>

  <Accordion title='أتلقى أخطاء "context too large" - كيف أعيد التعيين أو أضغط؟'>
    استخدم أحد هذه الخيارات:

    - **ضغط** (يحافظ على المحادثة لكنه يلخص الأدوار الأقدم):

      ```
      /compact
      ```

      أو `/compact <instructions>` لتوجيه الملخص.

    - **إعادة تعيين** (معرّف جلسة جديد لمفتاح الدردشة نفسه):

      ```
      /new
      /reset
      ```

    إذا استمر هذا في الحدوث:

    - فعّل أو اضبط **session pruning** ‏(`agents.defaults.contextPruning`) لقص خرج الأدوات القديم.
    - استخدم نموذجًا بنافذة سياق أكبر.

    الوثائق: [الضغط](/ar/concepts/compaction)، [تشذيب الجلسات](/ar/concepts/session-pruning)، [إدارة الجلسات](/ar/concepts/session).

  </Accordion>

  <Accordion title='لماذا أرى "LLM request rejected: messages.content.tool_use.input field required"؟'>
    هذا خطأ تحقق من الموفر: أصدر النموذج كتلة `tool_use` من دون
    `input` المطلوب. وعادةً ما يعني ذلك أن سجل الجلسة قديم أو تالف (غالبًا بعد خيوط طويلة
    أو تغيير في الأداة/schema).

    الحل: ابدأ جلسة جديدة باستخدام `/new` (كردة فعل مستقلة).

  </Accordion>

  <Accordion title="لماذا أتلقى رسائل heartbeat كل 30 دقيقة؟">
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

    إذا كان `HEARTBEAT.md` موجودًا لكنه فارغ فعليًا (يحتوي فقط على أسطر فارغة وعناوين
    Markdown مثل `# Heading`)، فإن OpenClaw يتخطى تشغيل heartbeat لتوفير استدعاءات API.
    وإذا كان الملف مفقودًا، فإن heartbeat تستمر في العمل ويقرر النموذج ما الذي يجب فعله.

    تستخدم overrides لكل وكيل `agents.list[].heartbeat`. الوثائق: [Heartbeat](/ar/gateway/heartbeat).

  </Accordion>

  <Accordion title='هل أحتاج إلى إضافة "حساب بوت" إلى مجموعة WhatsApp؟'>
    لا. يعمل OpenClaw على **حسابك الشخصي**، لذا إذا كنت داخل المجموعة، يستطيع OpenClaw رؤيتها.
    وبشكل افتراضي، يتم حظر الردود في المجموعات حتى تسمح للمرسلين (`groupPolicy: "allowlist"`).

    إذا كنت تريد أن يكون **أنت فقط** قادرًا على تحفيز الردود في المجموعة:

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

    الخيار 2 (إذا كانت مهيأة/موجودة بالفعل في قائمة السماح): اعرض المجموعات من الإعداد:

    ```bash
    openclaw directory groups list --channel whatsapp
    ```

    الوثائق: [WhatsApp](/ar/channels/whatsapp)، [الدليل](/cli/directory)، [السجلات](/cli/logs).

  </Accordion>

  <Accordion title="لماذا لا يرد OpenClaw في مجموعة؟">
    هناك سببان شائعان:

    - بوابة الإشارة مفعلة (افتراضيًا). يجب أن تقوم @mention للبوت (أو تطابق `mentionPatterns`).
    - لقد هيّأت `channels.whatsapp.groups` من دون `"*"` والمجموعة غير موجودة في قائمة السماح.

    راجع [المجموعات](/ar/channels/groups) و[رسائل المجموعات](/ar/channels/group-messages).

  </Accordion>

  <Accordion title="هل تشارك المجموعات/الخيوط السياق مع الرسائل الخاصة؟">
    تنهار الدردشات المباشرة إلى الجلسة الرئيسية افتراضيًا. أما المجموعات/القنوات فلها مفاتيح جلسات خاصة بها، وموضوعات Telegram / خيوط Discord هي جلسات منفصلة. راجع [المجموعات](/ar/channels/groups) و[رسائل المجموعات](/ar/channels/group-messages).
  </Accordion>

  <Accordion title="كم عدد مساحات العمل والوكلاء التي يمكنني إنشاؤها؟">
    لا توجد حدود صارمة. فالعشرات (بل المئات) لا بأس بها، لكن راقب:

    - **نمو القرص:** تعيش الجلسات + النصوص تحت `~/.openclaw/agents/<agentId>/sessions/`.
    - **تكلفة الرموز:** مزيد من الوكلاء يعني مزيدًا من استخدام النماذج بالتوازي.
    - **العبء التشغيلي:** ملفات تعريف مصادقة ومساحات عمل وتوجيه قنوات لكل وكيل.

    نصائح:

    - احتفظ بمساحة عمل **نشطة** واحدة لكل وكيل (`agents.defaults.workspace`).
    - قلّم الجلسات القديمة (احذف JSONL أو إدخالات المتجر) إذا ازداد حجم القرص.
    - استخدم `openclaw doctor` لاكتشاف مساحات العمل الشاردة وعدم تطابق الملفات الشخصية.

  </Accordion>

  <Accordion title="هل يمكنني تشغيل عدة بوتات أو دردشات في الوقت نفسه (Slack)، وكيف ينبغي أن أعد ذلك؟">
    نعم. استخدم **التوجيه متعدد الوكلاء** لتشغيل عدة وكلاء معزولين وتوجيه الرسائل الواردة بحسب
    القناة/الحساب/الندّ. Slack مدعوم كقناة ويمكن ربطه بوكلاء محددين.

    الوصول إلى المتصفح قوي لكنه ليس "افعل أي شيء يمكن للإنسان فعله" - إذ لا تزال أنظمة مكافحة الروبوتات وCAPTCHAs وMFA
    قادرة على حظر الأتمتة. وللحصول على أكثر تحكم موثوق بالمتصفح، استخدم Chrome MCP المحلي على المضيف،
    أو استخدم CDP على الجهاز الذي يشغّل المتصفح فعليًا.

    أفضل إعداد عملي:

    - مضيف Gateway دائم التشغيل (VPS/Mac mini).
    - وكيل واحد لكل دور (bindings).
    - قناة/قنوات Slack مربوطة بتلك الوكلاء.
    - متصفح محلي عبر Chrome MCP أو node عند الحاجة.

    الوثائق: [التوجيه متعدد الوكلاء](/ar/concepts/multi-agent)، [Slack](/ar/channels/slack)،
    [المتصفح](/ar/tools/browser)، [Nodes](/ar/nodes).

  </Accordion>
</AccordionGroup>

## النماذج: الافتراضيات، والاختيار، والأسماء المستعارة، والتبديل

<AccordionGroup>
  <Accordion title='ما هو "النموذج الافتراضي"؟'>
    النموذج الافتراضي في OpenClaw هو ما تضبطه على أنه:

    ```
    agents.defaults.model.primary
    ```

    يُشار إلى النماذج بصيغة `provider/model` (مثال: `openai/gpt-5.4`). وإذا حذفت الموفر، فإن OpenClaw تحاول أولًا اسمًا مستعارًا، ثم تطابقًا فريدًا لموفر مهيأ لذلك المعرّف الدقيق للنموذج، وبعد ذلك فقط تعود إلى الموفر الافتراضي المهيأ كمسار توافق قديم. وإذا كان ذلك الموفر لم يعد يعرّض النموذج الافتراضي المهيأ، فإن OpenClaw تعود إلى أول موفر/نموذج مهيأ بدل إظهار افتراضي قديم يعود إلى موفر مُزال. ومع ذلك، ينبغي لك **تعيين** `provider/model` بشكل صريح.

  </Accordion>

  <Accordion title="ما النموذج الذي توصي به؟">
    **الافتراضي الموصى به:** استخدم أقوى نموذج من أحدث جيل متاح ضمن مجموعة الموفّرين لديك.
    **للوكلاء المزوّدين بالأدوات أو ذوي المدخلات غير الموثوقة:** أعطِ الأولوية لقوة النموذج على التكلفة.
    **للدردشة الروتينية/منخفضة المخاطر:** استخدم نماذج احتياطية أرخص ووجّه حسب دور الوكيل.

    لدى MiniMax وثائقها الخاصة: [MiniMax](/ar/providers/minimax) و
    [النماذج المحلية](/ar/gateway/local-models).

    القاعدة العامة: استخدم **أفضل نموذج يمكنك تحمّل تكلفته** للأعمال عالية المخاطر، ونموذجًا أرخص
    للدردشة الروتينية أو الملخصات. ويمكنك توجيه النماذج لكل وكيل واستخدام وكلاء فرعيين
    لتوازي المهام الطويلة (كل وكيل فرعي يستهلك رموزًا). راجع [النماذج](/ar/concepts/models) و
    [الوكلاء الفرعيون](/ar/tools/subagents).

    تحذير قوي: النماذج الأضعف/المكمّاة بإفراط أكثر عرضة لـ prompt
    injection والسلوك غير الآمن. راجع [الأمان](/ar/gateway/security).

    مزيد من السياق: [النماذج](/ar/concepts/models).

  </Accordion>

  <Accordion title="كيف أبدّل النماذج من دون مسح الإعداد؟">
    استخدم **أوامر النماذج** أو حرر فقط حقول **النموذج**. وتجنب استبدال الإعداد كاملًا.

    خيارات آمنة:

    - `/model` في الدردشة (سريع، لكل جلسة)
    - `openclaw models set ...` (يحدّث إعداد النموذج فقط)
    - `openclaw configure --section model` (تفاعلي)
    - عدّل `agents.defaults.model` في `~/.openclaw/openclaw.json`

    تجنب `config.apply` مع كائن جزئي ما لم تكن تنوي استبدال الإعداد كله.
    وبالنسبة إلى تعديلات RPC، افحص أولًا باستخدام `config.schema.lookup` وفضّل `config.patch`.
    تمنحك حمولة lookup المسار المُطبع، ووثائق/قيود schema السطحية، وملخصات الأبناء المباشرين
    للتحديثات الجزئية.
    وإذا كنت قد استبدلت الإعداد بالفعل، فاستعد من نسخة احتياطية أو أعد تشغيل `openclaw doctor` للإصلاح.

    الوثائق: [النماذج](/ar/concepts/models)، [التكوين](/cli/configure)، [الإعداد](/cli/config)، [Doctor](/ar/gateway/doctor).

  </Accordion>

  <Accordion title="هل يمكنني استخدام نماذج مستضافة ذاتيًا (llama.cpp، vLLM، Ollama)؟">
    نعم. وOllama هي أسهل طريق إلى النماذج المحلية.

    أسرع إعداد:

    1. ثبّت Ollama من `https://ollama.com/download`
    2. اسحب نموذجًا محليًا مثل `ollama pull glm-4.7-flash`
    3. إذا كنت تريد نماذج سحابية أيضًا، فشغّل `ollama signin`
    4. شغّل `openclaw onboard` واختر `Ollama`
    5. اختر `Local` أو `Cloud + Local`

    ملاحظات:

    - يمنحك `Cloud + Local` نماذج سحابية بالإضافة إلى نماذج Ollama المحلية
    - النماذج السحابية مثل `kimi-k2.5:cloud` لا تحتاج إلى سحب محلي
    - للتبديل اليدوي، استخدم `openclaw models list` و`openclaw models set ollama/<model>`

    ملاحظة أمنية: النماذج الأصغر أو المكمّاة بشدة أكثر عرضة لـ prompt
    injection. ونوصي بشدة باستخدام **نماذج كبيرة** لأي بوت يستطيع استخدام الأدوات.
    وإذا كنت لا تزال تريد نماذج صغيرة، ففعّل sandboxing وقوائم سماح صارمة للأدوات.

    الوثائق: [Ollama](/ar/providers/ollama)، [النماذج المحلية](/ar/gateway/local-models)،
    [موفرو النماذج](/ar/concepts/model-providers)، [الأمان](/ar/gateway/security)،
    [الحاويات الآمنة](/ar/gateway/sandboxing).

  </Accordion>

  <Accordion title="ما النماذج التي يستخدمها OpenClaw وFlawd وKrill؟">
    - قد تختلف هذه البيئات وقد تتغير بمرور الوقت؛ ولا توجد توصية ثابتة بموفر معين.
    - تحقق من إعداد وقت التشغيل الحالي على كل بوابة باستخدام `openclaw models status`.
    - بالنسبة إلى الوكلاء الحساسين أمنيًا/المزوّدين بالأدوات، استخدم أقوى نموذج من أحدث جيل متاح.
  </Accordion>

  <Accordion title="كيف أبدّل النماذج أثناء التشغيل (من دون إعادة تشغيل)؟">
    استخدم أمر `/model` كرسالة مستقلة:

    ```
    /model sonnet
    /model opus
    /model gpt
    /model gpt-mini
    /model gemini
    /model gemini-flash
    /model gemini-flash-lite
    ```

    هذه هي الأسماء المستعارة المدمجة. ويمكن إضافة أسماء مستعارة مخصصة عبر `agents.defaults.models`.

    يمكنك عرض النماذج المتاحة باستخدام `/model` أو `/model list` أو `/model status`.

    يعرض `/model` ‏(وكذلك `/model list`) منتقيًا مدمجًا ومُرقّمًا. اختر حسب الرقم:

    ```
    /model 3
    ```

    ويمكنك أيضًا فرض ملف تعريف مصادقة معين للموفر (لكل جلسة):

    ```
    /model opus@anthropic:default
    /model opus@anthropic:work
    ```

    نصيحة: يعرض `/model status` الوكيل النشط، وملف `auth-profiles.json` المستخدم، وملف تعريف المصادقة الذي ستتم تجربته بعد ذلك.
    كما يعرض نقطة نهاية الموفر المهيأة (`baseUrl`) ووضع API ‏(`api`) عند توفرهما.

    **كيف ألغي تثبيت ملف تعريف قمت بتعيينه باستخدام @profile؟**

    أعد تشغيل `/model` **من دون** اللاحقة `@profile`:

    ```
    /model anthropic/claude-opus-4-6
    ```

    وإذا أردت العودة إلى الافتراضي، فاختره من `/model` (أو أرسل `/model <default provider/model>`).
    واستخدم `/model status` للتأكد من ملف تعريف المصادقة النشط.

  </Accordion>

  <Accordion title="هل يمكنني استخدام GPT 5.2 للمهام اليومية وCodex 5.3 للبرمجة؟">
    نعم. اضبط أحدهما كافتراضي وبدّل عند الحاجة:

    - **تبديل سريع (لكل جلسة):** استخدم `/model gpt-5.4` للمهام اليومية، و`/model openai-codex/gpt-5.4` للبرمجة باستخدام Codex OAuth.
    - **افتراضي + تبديل:** اضبط `agents.defaults.model.primary` على `openai/gpt-5.4`، ثم بدّل إلى `openai-codex/gpt-5.4` عند البرمجة (أو بالعكس).
    - **الوكلاء الفرعيون:** وجّه مهام البرمجة إلى وكلاء فرعيين لديهم نموذج افتراضي مختلف.

    راجع [النماذج](/ar/concepts/models) و[أوامر الشرطة المائلة](/ar/tools/slash-commands).

  </Accordion>

  <Accordion title="كيف أهيئ fast mode لـ GPT 5.4؟">
    استخدم إما تبديلًا لكل جلسة أو افتراضيًا في الإعداد:

    - **لكل جلسة:** أرسل `/fast on` بينما تستخدم الجلسة `openai/gpt-5.4` أو `openai-codex/gpt-5.4`.
    - **افتراضي لكل نموذج:** اضبط `agents.defaults.models["openai/gpt-5.4"].params.fastMode` على `true`.
    - **ينطبق على Codex OAuth أيضًا:** إذا كنت تستخدم أيضًا `openai-codex/gpt-5.4`، فاضبط العلم نفسه هناك.

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

    بالنسبة إلى OpenAI، يُطابق fast mode القيمة `service_tier = "priority"` في طلبات Responses الأصلية المدعومة. وتتغلب قيمة `/fast` الخاصة بالجلسة على افتراضيات الإعداد.

    راجع [التفكير وfast mode](/ar/tools/thinking) و[OpenAI fast mode](/ar/providers/openai#openai-fast-mode).

  </Accordion>

  <Accordion title='لماذا أرى "Model ... is not allowed" ثم لا يأتيني رد؟'>
    إذا كانت `agents.defaults.models` مضبوطة، فإنها تصبح **قائمة السماح** لـ `/model` وأي
    overrides للجلسة. ويؤدي اختيار نموذج غير موجود في تلك القائمة إلى إرجاع:

    ```
    Model "provider/model" is not allowed. Use /model to list available models.
    ```

    يُعاد هذا الخطأ **بدلًا من** رد عادي. والحل: أضف النموذج إلى
    `agents.defaults.models`، أو أزل قائمة السماح، أو اختر نموذجًا من `/model list`.

  </Accordion>

  <Accordion title='لماذا أرى "Unknown model: minimax/MiniMax-M2.7"؟'>
    هذا يعني أن **الموفر غير مهيأ** (لم يُعثر على إعداد موفر MiniMax أو ملف
    تعريف مصادقة)، لذلك لا يمكن حل النموذج.

    قائمة تحقق للحل:

    1. حدّث إلى إصدار حديث من OpenClaw (أو شغّل من المصدر `main`) ثم أعد تشغيل gateway.
    2. تأكد من أن MiniMax مهيأ (عبر المعالج أو JSON)، أو أن مصادقة MiniMax
       موجودة