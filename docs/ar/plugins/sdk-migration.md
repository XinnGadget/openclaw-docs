---
read_when:
    - تظهر لك رسالة التحذير OPENCLAW_PLUGIN_SDK_COMPAT_DEPRECATED
    - تظهر لك رسالة التحذير OPENCLAW_EXTENSION_API_DEPRECATED
    - أنت تحدّث إضافة إلى بنية الإضافات الحديثة
    - أنت مسؤول عن إضافة OpenClaw خارجية
sidebarTitle: Migrate to SDK
summary: الانتقال من طبقة التوافق العكسي القديمة إلى Plugin SDK الحديث
title: ترحيل Plugin SDK
x-i18n:
    generated_at: "2026-04-09T01:29:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: 60cbb6c8be30d17770887d490c14e3a4538563339a5206fb419e51e0558bbc07
    source_path: plugins/sdk-migration.md
    workflow: 15
---

# ترحيل Plugin SDK

انتقل OpenClaw من طبقة توافق عكسي واسعة إلى بنية إضافات حديثة
ذات عمليات استيراد مركزة وموثقة. إذا كانت إضافتك قد بُنيت قبل
البنية الجديدة، فسيساعدك هذا الدليل على ترحيلها.

## ما الذي يتغير

كان نظام الإضافات القديم يوفر سطحين مفتوحين على اتساعهما يتيحان للإضافات استيراد
أي شيء تحتاجه من نقطة دخول واحدة:

- **`openclaw/plugin-sdk/compat`** — استيراد واحد يعيد تصدير عشرات
  الأدوات المساعدة. تم تقديمه للإبقاء على عمل الإضافات القديمة المعتمدة على hooks أثناء
  بناء بنية الإضافات الجديدة.
- **`openclaw/extension-api`** — جسر يمنح الإضافات وصولًا مباشرًا إلى
  أدوات جهة المضيف المساعدة مثل مشغل الوكيل المضمن.

كلا السطحين أصبح الآن **مهجورًا**. لا يزالان يعملان وقت التشغيل، لكن يجب ألا تستخدمهما
الإضافات الجديدة، ويجب على الإضافات الحالية الترحيل قبل أن تزيلهما
الإصدار الرئيسي التالي.

<Warning>
  ستُزال طبقة التوافق العكسي في إصدار رئيسي مستقبلي.
  الإضافات التي لا تزال تستورد من هذه الأسطح ستتعطل عند حدوث ذلك.
</Warning>

## لماذا تغيّر هذا

تسبب النهج القديم في مشكلات:

- **بدء تشغيل بطيء** — كان استيراد أداة مساعدة واحدة يحمّل عشرات الوحدات غير المرتبطة
- **اعتماديات دائرية** — كانت إعادة التصدير الواسعة تجعل من السهل إنشاء دورات استيراد
- **سطح API غير واضح** — لم تكن هناك طريقة لمعرفة أي الصادرات مستقرة وأيها داخلية

يعالج Plugin SDK الحديث ذلك: فكل مسار استيراد (`openclaw/plugin-sdk/\<subpath\>`)
هو وحدة صغيرة مكتفية بذاتها ذات غرض واضح وعقد موثق.

كما أزيلت أيضًا واجهات الراحة القديمة الخاصة بالموفرات للقنوات المضمنة. عمليات استيراد
مثل `openclaw/plugin-sdk/slack` و`openclaw/plugin-sdk/discord` و
`openclaw/plugin-sdk/signal` و`openclaw/plugin-sdk/whatsapp`،
وواجهات المساعدة الموسومة باسم القناة، و
`openclaw/plugin-sdk/telegram-core` كانت اختصارات خاصة داخل mono-repo، وليست
عقود إضافات مستقرة. استخدم بدلًا منها مسارات SDK عامة ضيقة. داخل
مساحة عمل الإضافات المضمنة، احتفظ بالأدوات المساعدة المملوكة للموفر في
`api.ts` أو `runtime-api.ts` الخاصين بتلك الإضافة.

أمثلة الموفرات المضمنة الحالية:

- تحتفظ Anthropic بأدوات بث خاصة بـ Claude في واجهتها الخاصة `api.ts` /
  `contract-api.ts`
- تحتفظ OpenAI بمنشئات الموفرات، وأدوات النموذج الافتراضي، ومنشئات موفرات
  realtime في `api.ts` الخاص بها
- يحتفظ OpenRouter بمنشئ الموفر وأدوات onboarding/config المساعدة في
  `api.ts` الخاص به

## كيفية الترحيل

<Steps>
  <Step title="ترحيل المعالجات الأصلية المعتمدة على الموافقة إلى حقائق القدرات">
    تعرض إضافات القنوات القادرة على الموافقة الآن سلوك الموافقة الأصلي عبر
    `approvalCapability.nativeRuntime` بالإضافة إلى سجل سياق وقت التشغيل المشترك.

    التغييرات الأساسية:

    - استبدل `approvalCapability.handler.loadRuntime(...)` بـ
      `approvalCapability.nativeRuntime`
    - انقل المصادقة/التسليم الخاصين بالموافقة من الربط القديم `plugin.auth` /
      `plugin.approvals` إلى `approvalCapability`
    - تمت إزالة `ChannelPlugin.approvals` من العقد العام
      لإضافات القنوات؛ انقل حقول delivery/native/render إلى `approvalCapability`
    - يبقى `plugin.auth` لتدفقات تسجيل الدخول/الخروج الخاصة بالقناة فقط؛ لم تعد
      hooks مصادقة الموافقة هناك تُقرأ من core
    - سجّل عناصر وقت التشغيل المملوكة للقناة مثل العملاء أو الرموز أو تطبيقات
      Bolt من خلال `openclaw/plugin-sdk/channel-runtime-context`
    - لا ترسل إشعارات إعادة التوجيه المملوكة للإضافة من معالجات الموافقة الأصلية؛
      أصبح core الآن مسؤولًا عن إشعارات التوجيه إلى مكان آخر بناءً على نتائج التسليم الفعلية
    - عند تمرير `channelRuntime` إلى `createChannelManager(...)`، قدّم
      سطح `createPluginRuntime().channel` حقيقيًا. تُرفض البدائل الجزئية.

    راجع `/plugins/sdk-channel-plugins` للاطلاع على
    تخطيط قدرة الموافقة الحالي.

  </Step>

  <Step title="مراجعة سلوك fallback الخاص بغلاف Windows">
    إذا كانت إضافتك تستخدم `openclaw/plugin-sdk/windows-spawn`،
    فإن أغلفة Windows من نوع `.cmd`/`.bat` غير المحلولة ستفشل الآن بشكل مغلق ما لم تمرر
    صراحةً `allowShellFallback: true`.

    ```typescript
    // قبل
    const program = applyWindowsSpawnProgramPolicy({ candidate });

    // بعد
    const program = applyWindowsSpawnProgramPolicy({
      candidate,
      // اضبط هذا فقط للجهات المتوافقة الموثوقة التي
      // تقبل عمدًا fallback بوساطة shell.
      allowShellFallback: true,
    });
    ```

    إذا لم يكن المستدعي لديك يعتمد عمدًا على shell fallback، فلا تضبط
    `allowShellFallback` وتعامل مع الخطأ المرمى بدلًا من ذلك.

  </Step>

  <Step title="العثور على عمليات الاستيراد المهجورة">
    ابحث في إضافتك عن عمليات الاستيراد من أي من السطحين المهجورين:

    ```bash
    grep -r "plugin-sdk/compat" my-plugin/
    grep -r "openclaw/extension-api" my-plugin/
    ```

  </Step>

  <Step title="الاستبدال بعمليات استيراد مركزة">
    كل عنصر مُصدَّر من السطح القديم يقابله مسار استيراد حديث محدد:

    ```typescript
    // قبل (طبقة التوافق العكسي المهجورة)
    import {
      createChannelReplyPipeline,
      createPluginRuntimeStore,
      resolveControlCommandGate,
    } from "openclaw/plugin-sdk/compat";

    // بعد (عمليات استيراد حديثة ومركزة)
    import { createChannelReplyPipeline } from "openclaw/plugin-sdk/channel-reply-pipeline";
    import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
    import { resolveControlCommandGate } from "openclaw/plugin-sdk/command-auth";
    ```

    بالنسبة إلى الأدوات المساعدة على جهة المضيف، استخدم وقت تشغيل الإضافة المحقون بدلًا من الاستيراد
    المباشر:

    ```typescript
    // قبل (جسر extension-api المهجور)
    import { runEmbeddedPiAgent } from "openclaw/extension-api";
    const result = await runEmbeddedPiAgent({ sessionId, prompt });

    // بعد (وقت تشغيل محقون)
    const result = await api.runtime.agent.runEmbeddedPiAgent({ sessionId, prompt });
    ```

    ينطبق النمط نفسه على أدوات الجسر القديمة الأخرى:

    | الاستيراد القديم | المكافئ الحديث |
    | --- | --- |
    | `resolveAgentDir` | `api.runtime.agent.resolveAgentDir` |
    | `resolveAgentWorkspaceDir` | `api.runtime.agent.resolveAgentWorkspaceDir` |
    | `resolveAgentIdentity` | `api.runtime.agent.resolveAgentIdentity` |
    | `resolveThinkingDefault` | `api.runtime.agent.resolveThinkingDefault` |
    | `resolveAgentTimeoutMs` | `api.runtime.agent.resolveAgentTimeoutMs` |
    | `ensureAgentWorkspace` | `api.runtime.agent.ensureAgentWorkspace` |
    | أدوات مخزن الجلسة المساعدة | `api.runtime.agent.session.*` |

  </Step>

  <Step title="البناء والاختبار">
    ```bash
    pnpm build
    pnpm test -- my-plugin/
    ```
  </Step>
</Steps>

## مرجع مسارات الاستيراد

<Accordion title="جدول مسارات الاستيراد الشائعة">
  | مسار الاستيراد | الغرض | الصادرات الأساسية |
  | --- | --- | --- |
  | `plugin-sdk/plugin-entry` | أداة إدخال الإضافة القياسية | `definePluginEntry` |
  | `plugin-sdk/core` | إعادة تصدير مظلية قديمة لتعريفات/منشئات إدخال القنوات | `defineChannelPluginEntry`, `createChatChannelPlugin` |
  | `plugin-sdk/config-schema` | تصدير مخطط الإعداد الجذر | `OpenClawSchema` |
  | `plugin-sdk/provider-entry` | أداة إدخال موفر واحد | `defineSingleProviderPluginEntry` |
  | `plugin-sdk/channel-core` | تعريفات ومنشئات إدخال القنوات المركزة | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
  | `plugin-sdk/setup` | أدوات معالج الإعداد المشتركة | مطالبات قائمة السماح، ومنشئات حالة الإعداد |
  | `plugin-sdk/setup-runtime` | أدوات وقت التشغيل المساعدة أثناء الإعداد | محولات setup patch الآمنة للاستيراد، وأدوات lookup-note المساعدة، و`promptResolvedAllowFrom` و`splitSetupEntries` ووكلاء الإعداد المفوضون |
  | `plugin-sdk/setup-adapter-runtime` | أدوات محول الإعداد المساعدة | `createEnvPatchedAccountSetupAdapter` |
  | `plugin-sdk/setup-tools` | أدوات الإعداد المساعدة | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
  | `plugin-sdk/account-core` | أدوات تعدد الحسابات المساعدة | أدوات قائمة الحساب/الإعداد/بوابة الإجراء |
  | `plugin-sdk/account-id` | أدوات معرّف الحساب المساعدة | `DEFAULT_ACCOUNT_ID`، وتطبيع معرّف الحساب |
  | `plugin-sdk/account-resolution` | أدوات البحث عن الحساب المساعدة | أدوات البحث عن الحساب + fallback الافتراضي |
  | `plugin-sdk/account-helpers` | أدوات حساب ضيقة المدى | أدوات قائمة الحساب/إجراء الحساب |
  | `plugin-sdk/channel-setup` | محولات معالج الإعداد | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`، بالإضافة إلى `DEFAULT_ACCOUNT_ID` و`createTopLevelChannelDmPolicy` و`setSetupChannelEnabled` و`splitSetupEntries` |
  | `plugin-sdk/channel-pairing` | أساسيات إقران DM | `createChannelPairingController` |
  | `plugin-sdk/channel-reply-pipeline` | أسلاك بادئة الرد + مؤشرات الكتابة | `createChannelReplyPipeline` |
  | `plugin-sdk/channel-config-helpers` | مصانع محولات الإعداد | `createHybridChannelConfigAdapter` |
  | `plugin-sdk/channel-config-schema` | منشئات مخطط الإعداد | أنواع مخطط إعداد القناة |
  | `plugin-sdk/telegram-command-config` | أدوات إعداد أوامر Telegram المساعدة | تطبيع أسماء الأوامر، واقتطاع الأوصاف، والتحقق من التكرار/التعارض |
  | `plugin-sdk/channel-policy` | تحليل سياسات المجموعة/DM | `resolveChannelGroupRequireMention` |
  | `plugin-sdk/channel-lifecycle` | تتبع حالة الحساب | `createAccountStatusSink` |
  | `plugin-sdk/inbound-envelope` | أدوات envelope الوارد المساعدة | أدوات route + منشئ envelope المشتركة |
  | `plugin-sdk/inbound-reply-dispatch` | أدوات الرد الوارد المساعدة | أدوات التسجيل والإرسال المشتركة |
  | `plugin-sdk/messaging-targets` | تحليل وجهات المراسلة | أدوات تحليل/مطابقة الوجهات |
  | `plugin-sdk/outbound-media` | أدوات الوسائط الصادرة المساعدة | تحميل الوسائط الصادرة المشتركة |
  | `plugin-sdk/outbound-runtime` | أدوات وقت التشغيل الصادر المساعدة | أدوات هوية الصادر/مفوّض الإرسال |
  | `plugin-sdk/thread-bindings-runtime` | أدوات ربط السلاسل المساعدة | دورة حياة ربط السلاسل وأدوات المحول المساعدة |
  | `plugin-sdk/agent-media-payload` | أدوات حمولة الوسائط القديمة المساعدة | منشئ حمولة وسائط الوكيل لتخطيطات الحقول القديمة |
  | `plugin-sdk/channel-runtime` | طبقة توافقية مهجورة | أدوات وقت تشغيل القناة القديمة فقط |
  | `plugin-sdk/channel-send-result` | أنواع نتائج الإرسال | أنواع نتائج الرد |
  | `plugin-sdk/runtime-store` | تخزين الإضافة الدائم | `createPluginRuntimeStore` |
  | `plugin-sdk/runtime` | أدوات وقت تشغيل واسعة | أدوات وقت التشغيل/التسجيل/النسخ الاحتياطي/تثبيت الإضافات |
  | `plugin-sdk/runtime-env` | أدوات بيئة وقت تشغيل ضيقة | المسجل/بيئة وقت التشغيل، وأدوات المهلة وإعادة المحاولة وbackoff |
  | `plugin-sdk/plugin-runtime` | أدوات وقت تشغيل الإضافات المشتركة | أدوات أوامر/ hooks /HTTP/التفاعلية الخاصة بالإضافات |
  | `plugin-sdk/hook-runtime` | أدوات خط أنابيب hook المساعدة | أدوات خط أنابيب webhook/internal hook المشتركة |
  | `plugin-sdk/lazy-runtime` | أدوات وقت التشغيل الكسول المساعدة | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeMethodBinder`, `createLazyRuntimeNamedExport`, `createLazyRuntimeSurface` |
  | `plugin-sdk/process-runtime` | أدوات العمليات المساعدة | أدوات exec المشتركة |
  | `plugin-sdk/cli-runtime` | أدوات وقت تشغيل CLI المساعدة | تنسيق الأوامر، والانتظار، وأدوات الإصدار المساعدة |
  | `plugin-sdk/gateway-runtime` | أدوات البوابة المساعدة | عميل البوابة وأدوات patch حالة القناة المساعدة |
  | `plugin-sdk/config-runtime` | أدوات الإعداد المساعدة | أدوات تحميل/كتابة الإعداد |
  | `plugin-sdk/telegram-command-config` | أدوات أوامر Telegram المساعدة | أدوات التحقق من أوامر Telegram المستقرة بالحد الأدنى عندما يكون سطح عقد Telegram المضمن غير متاح |
  | `plugin-sdk/approval-runtime` | أدوات مطالبات الموافقة المساعدة | حمولة موافقة exec/plugin، وأدوات قدرة/ملف تعريف الموافقة، وأدوات توجيه/وقت تشغيل الموافقة الأصلية |
  | `plugin-sdk/approval-auth-runtime` | أدوات مصادقة الموافقة المساعدة | تحليل المُوافق، ومصادقة الإجراء ضمن الدردشة نفسها |
  | `plugin-sdk/approval-client-runtime` | أدوات عميل الموافقة المساعدة | أدوات ملف تعريف/تصفية الموافقة الأصلية لـ exec |
  | `plugin-sdk/approval-delivery-runtime` | أدوات تسليم الموافقة المساعدة | محولات قدرة/تسليم الموافقة الأصلية |
  | `plugin-sdk/approval-gateway-runtime` | أدوات بوابة الموافقة المساعدة | أداة تحليل approval gateway المشتركة |
  | `plugin-sdk/approval-handler-adapter-runtime` | أدوات محول الموافقة المساعدة | أدوات تحميل محول الموافقة الأصلية خفيفة الوزن لنقاط إدخال القنوات الساخنة |
  | `plugin-sdk/approval-handler-runtime` | أدوات معالج الموافقة المساعدة | أدوات وقت تشغيل معالج الموافقة الأوسع؛ فضّل واجهات adapter/gateway الأضيق عندما تكون كافية |
  | `plugin-sdk/approval-native-runtime` | أدوات هدف الموافقة المساعدة | أدوات ربط هدف/حساب الموافقة الأصلية |
  | `plugin-sdk/approval-reply-runtime` | أدوات رد الموافقة المساعدة | أدوات حمولة رد موافقة exec/plugin |
  | `plugin-sdk/channel-runtime-context` | أدوات channel runtime-context المساعدة | أدوات register/get/watch عامة لسياق وقت تشغيل القناة |
  | `plugin-sdk/security-runtime` | أدوات الأمان المساعدة | أدوات الثقة المشتركة، وبوابة DM، والمحتوى الخارجي، وجمع الأسرار |
  | `plugin-sdk/ssrf-policy` | أدوات سياسة SSRF المساعدة | قائمة سماح المضيف وأدوات سياسة الشبكة الخاصة |
  | `plugin-sdk/ssrf-runtime` | أدوات وقت تشغيل SSRF المساعدة | Pinned-dispatcher وguarded fetch وأدوات سياسة SSRF |
  | `plugin-sdk/collection-runtime` | أدوات cache المقيّدة المساعدة | `pruneMapToMaxSize` |
  | `plugin-sdk/diagnostic-runtime` | أدوات بوابة التشخيص المساعدة | `isDiagnosticFlagEnabled`, `isDiagnosticsEnabled` |
  | `plugin-sdk/error-runtime` | أدوات تنسيق الأخطاء المساعدة | `formatUncaughtError`, `isApprovalNotFoundError`، وأدوات error graph |
  | `plugin-sdk/fetch-runtime` | أدوات fetch/proxy المغلفة المساعدة | `resolveFetch`، وأدوات proxy المساعدة |
  | `plugin-sdk/host-runtime` | أدوات تطبيع المضيف المساعدة | `normalizeHostname`, `normalizeScpRemoteHost` |
  | `plugin-sdk/retry-runtime` | أدوات إعادة المحاولة المساعدة | `RetryConfig`, `retryAsync`، ومنفذات السياسات |
  | `plugin-sdk/allow-from` | تنسيق قائمة السماح | `formatAllowFromLowercase` |
  | `plugin-sdk/allowlist-resolution` | تعيين مدخلات قائمة السماح | `mapAllowlistResolutionInputs` |
  | `plugin-sdk/command-auth` | أدوات بوابة الأوامر وسطح الأوامر المساعدة | `resolveControlCommandGate`، وأدوات تفويض المرسل المساعدة، وأدوات سجل الأوامر |
  | `plugin-sdk/command-status` | عارضات حالة/مساعدة الأوامر | `buildCommandsMessage`, `buildCommandsMessagePaginated`, `buildHelpMessage` |
  | `plugin-sdk/secret-input` | تحليل المدخلات السرية | أدوات المدخلات السرية المساعدة |
  | `plugin-sdk/webhook-ingress` | أدوات طلبات webhook المساعدة | أدوات هدف webhook |
  | `plugin-sdk/webhook-request-guards` | أدوات حماية جسم webhook المساعدة | أدوات قراءة/تحديد جسم الطلب |
  | `plugin-sdk/reply-runtime` | وقت تشغيل الرد المشترك | الإرسال الوارد، وheartbeat، ومخطط الرد، والتقسيم |
  | `plugin-sdk/reply-dispatch-runtime` | أدوات إرسال الرد الضيقة المساعدة | أدوات finalize + provider dispatch المساعدة |
  | `plugin-sdk/reply-history` | أدوات سجل الرد المساعدة | `buildHistoryContext`, `buildPendingHistoryContextFromMap`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` |
  | `plugin-sdk/reply-reference` | تخطيط مرجع الرد | `createReplyReferencePlanner` |
  | `plugin-sdk/reply-chunking` | أدوات تقسيم الرد المساعدة | أدوات تقسيم النص/Markdown |
  | `plugin-sdk/session-store-runtime` | أدوات مخزن الجلسة المساعدة | أدوات مسار المخزن + وقت آخر تحديث |
  | `plugin-sdk/state-paths` | أدوات مسارات الحالة المساعدة | أدوات مجلد الحالة وOAuth |
  | `plugin-sdk/routing` | أدوات التوجيه/مفتاح الجلسة المساعدة | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId`، وأدوات تطبيع مفتاح الجلسة |
  | `plugin-sdk/status-helpers` | أدوات حالة القناة المساعدة | منشئات ملخص حالة القناة/الحساب، وافتراضيات runtime-state، وأدوات metadata الخاصة بالمشكلات |
  | `plugin-sdk/target-resolver-runtime` | أدوات تحليل الوجهة المساعدة | أدوات تحليل الوجهة المشتركة |
  | `plugin-sdk/string-normalization-runtime` | أدوات تطبيع السلاسل المساعدة | أدوات تطبيع slug/string |
  | `plugin-sdk/request-url` | أدوات URL الطلب المساعدة | استخراج عناوين URL النصية من المدخلات الشبيهة بالطلبات |
  | `plugin-sdk/run-command` | أدوات الأوامر الموقّتة المساعدة | مشغل أوامر موقّت مع stdout/stderr مطبّعين |
  | `plugin-sdk/param-readers` | قارئات المعلمات | قارئات معلمات شائعة للأداة/CLI |
  | `plugin-sdk/tool-payload` | استخراج حمولة الأداة | استخراج حمولات مطبّعة من كائنات نتائج الأدوات |
  | `plugin-sdk/tool-send` | استخراج إرسال الأداة | استخراج حقول وجهة الإرسال القياسية من وسائط الأداة |
  | `plugin-sdk/temp-path` | أدوات المسارات المؤقتة المساعدة | أدوات مشتركة لمسارات تنزيل الملفات المؤقتة |
  | `plugin-sdk/logging-core` | أدوات التسجيل المساعدة | مسجل النظام الفرعي وأدوات إخفاء البيانات الحساسة |
  | `plugin-sdk/markdown-table-runtime` | أدوات جداول Markdown المساعدة | أدوات أوضاع جداول Markdown |
  | `plugin-sdk/reply-payload` | أنواع ردود الرسائل | أنواع حمولة الرد |
  | `plugin-sdk/provider-setup` | أدوات إعداد الموفّر المحلي/المستضاف ذاتيًا المنسقة | أدوات اكتشاف/إعداد الموفّر المستضاف ذاتيًا |
  | `plugin-sdk/self-hosted-provider-setup` | أدوات إعداد مركزة للموفرات المستضافة ذاتيًا المتوافقة مع OpenAI | الأدوات نفسها لاكتشاف/إعداد الموفّر المستضاف ذاتيًا |
  | `plugin-sdk/provider-auth-runtime` | أدوات مصادقة وقت تشغيل الموفّر المساعدة | أدوات تحليل مفتاح API في وقت التشغيل |
  | `plugin-sdk/provider-auth-api-key` | أدوات إعداد مفتاح API للموفر | أدوات onboarding/profile-write الخاصة بمفتاح API |
  | `plugin-sdk/provider-auth-result` | أدوات نتائج مصادقة الموفّر المساعدة | منشئ auth-result قياسي لـ OAuth |
  | `plugin-sdk/provider-auth-login` | أدوات تسجيل الدخول التفاعلي للموفّر | أدوات تسجيل الدخول التفاعلي المشتركة |
  | `plugin-sdk/provider-env-vars` | أدوات متغيرات البيئة للموفّر | أدوات البحث عن متغيرات البيئة الخاصة بمصادقة الموفّر |
  | `plugin-sdk/provider-model-shared` | أدوات مشتركة لنماذج/إعادة تشغيل الموفر | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`، ومنشئات replay-policy المشتركة، وأدوات provider-endpoint، وأدوات تطبيع model-id |
  | `plugin-sdk/provider-catalog-shared` | أدوات مشتركة لفهرس الموفّر | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
  | `plugin-sdk/provider-onboard` | أدوات onboarding للموفّر | أدوات إعداد onboarding المساعدة |
  | `plugin-sdk/provider-http` | أدوات HTTP الخاصة بالموفّر | أدوات HTTP/قدرات endpoint العامة الخاصة بالموفّر |
  | `plugin-sdk/provider-web-fetch` | أدوات web-fetch الخاصة بالموفّر | أدوات تسجيل/تخزين مؤقت لموفّر web-fetch |
  | `plugin-sdk/provider-web-search-config-contract` | أدوات إعداد web-search الخاصة بالموفّر | أدوات إعداد/اعتماد ضيقة للبحث على الويب للموفرات التي لا تحتاج إلى ربط تمكين الإضافة |
  | `plugin-sdk/provider-web-search-contract` | أدوات عقد web-search الخاصة بالموفّر | أدوات عقد إعداد/اعتماد ضيقة للبحث على الويب مثل `createWebSearchProviderContractFields` و`enablePluginInConfig` و`resolveProviderWebSearchPluginConfig` وأدوات تعيين/قراءة بيانات الاعتماد المقيّدة |
  | `plugin-sdk/provider-web-search` | أدوات web-search الخاصة بالموفّر | أدوات تسجيل/تخزين مؤقت/وقت تشغيل لموفّر البحث على الويب |
  | `plugin-sdk/provider-tools` | أدوات توافق أدوات/مخطط الموفّر | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`، وتنظيف مخطط Gemini + أدوات التشخيص، وأدوات توافق xAI مثل `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
  | `plugin-sdk/provider-usage` | أدوات استخدام الموفّر | `fetchClaudeUsage`, `fetchGeminiUsage`, `fetchGithubCopilotUsage`، وأدوات استخدام موفر أخرى |
  | `plugin-sdk/provider-stream` | أدوات تغليف بث الموفّر | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`، وأنواع مغلفات البث، وأدوات مغلفات مشتركة لـ Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
  | `plugin-sdk/keyed-async-queue` | قائمة انتظار async مرتبة | `KeyedAsyncQueue` |
  | `plugin-sdk/media-runtime` | أدوات وسائط مشتركة | أدوات جلب/تحويل/تخزين الوسائط بالإضافة إلى منشئات حمولة الوسائط |
  | `plugin-sdk/media-generation-runtime` | أدوات مشتركة لتوليد الوسائط | أدوات failover المشتركة، واختيار المرشح، ورسائل النماذج المفقودة لتوليد الصور/الفيديو/الموسيقى |
  | `plugin-sdk/media-understanding` | أدوات فهم الوسائط المساعدة | أنواع موفر فهم الوسائط بالإضافة إلى صادرات أدوات الصور/الصوت المواجهة للموفر |
  | `plugin-sdk/text-runtime` | أدوات نصية مشتركة | إزالة النص المرئي للمساعد، وأدوات render/chunking/table الخاصة بـ Markdown، وأدوات إخفاء البيانات، وأدوات directive-tag، وأدوات النص الآمن، وغيرها من أدوات النص/التسجيل ذات الصلة |
  | `plugin-sdk/text-chunking` | أدوات تقسيم النص المساعدة | أداة تقسيم النص الصادر |
  | `plugin-sdk/speech` | أدوات الكلام المساعدة | أنواع موفّر الكلام بالإضافة إلى أدوات directive والسجل والتحقق المواجهة للموفّر |
  | `plugin-sdk/speech-core` | نواة الكلام المشتركة | أنواع موفّر الكلام، والسجل، والتوجيهات، والتطبيع |
  | `plugin-sdk/realtime-transcription` | أدوات النسخ الفوري المساعدة | أنواع الموفّر وأدوات السجل |
  | `plugin-sdk/realtime-voice` | أدوات الصوت الفوري المساعدة | أنواع الموفّر وأدوات السجل |
  | `plugin-sdk/image-generation-core` | نواة توليد الصور المشتركة | أنواع توليد الصور، وfailover، والمصادقة، وأدوات السجل |
  | `plugin-sdk/music-generation` | أدوات توليد الموسيقى المساعدة | أنواع موفر/طلب/نتيجة توليد الموسيقى |
  | `plugin-sdk/music-generation-core` | نواة توليد الموسيقى المشتركة | أنواع توليد الموسيقى، وأدوات failover المساعدة، والبحث عن الموفّر، وتحليل model-ref |
  | `plugin-sdk/video-generation` | أدوات توليد الفيديو المساعدة | أنواع موفر/طلب/نتيجة توليد الفيديو |
  | `plugin-sdk/video-generation-core` | نواة توليد الفيديو المشتركة | أنواع توليد الفيديو، وأدوات failover المساعدة، والبحث عن الموفّر، وتحليل model-ref |
  | `plugin-sdk/interactive-runtime` | أدوات الرد التفاعلي المساعدة | تطبيع/اختزال حمولة الرد التفاعلي |
  | `plugin-sdk/channel-config-primitives` | بدائيات إعداد القناة | بدائيات ضيقة لمخطط إعداد القناة |
  | `plugin-sdk/channel-config-writes` | أدوات كتابة إعداد القناة المساعدة | أدوات تفويض كتابة إعداد القناة |
  | `plugin-sdk/channel-plugin-common` | تمهيد القنوات المشترك | صادرات تمهيد إضافات القنوات المشتركة |
  | `plugin-sdk/channel-status` | أدوات حالة القناة المساعدة | أدوات snapshot/summary المشتركة لحالة القناة |
  | `plugin-sdk/allowlist-config-edit` | أدوات إعداد قائمة السماح | أدوات قراءة/تعديل إعداد قائمة السماح |
  | `plugin-sdk/group-access` | أدوات الوصول للمجموعات المساعدة | أدوات القرار المشتركة للوصول إلى المجموعات |
  | `plugin-sdk/direct-dm` | أدوات DM المباشر المساعدة | أدوات المصادقة/الحماية المشتركة للـ DM المباشر |
  | `plugin-sdk/extension-shared` | أدوات إضافات مشتركة | بدائيات القناة/الحالة السلبية وأدوات ambient proxy المساعدة |
  | `plugin-sdk/webhook-targets` | أدوات أهداف webhook المساعدة | سجل أهداف webhook وأدوات تثبيت route |
  | `plugin-sdk/webhook-path` | أدوات مسار webhook المساعدة | أدوات تطبيع مسار webhook |
  | `plugin-sdk/web-media` | أدوات وسائط الويب المشتركة | أدوات تحميل الوسائط البعيدة/المحلية |
  | `plugin-sdk/zod` | إعادة تصدير Zod | إعادة تصدير `zod` لمستهلكي Plugin SDK |
  | `plugin-sdk/memory-core` | أدوات memory-core المضمنة | سطح أدوات memory manager/config/file/CLI |
  | `plugin-sdk/memory-core-engine-runtime` | واجهة وقت تشغيل محرك الذاكرة | واجهة وقت تشغيل memory index/search |
  | `plugin-sdk/memory-core-host-engine-foundation` | محرك أساس مضيف الذاكرة | صادرات محرك الأساس لمضيف الذاكرة |
  | `plugin-sdk/memory-core-host-engine-embeddings` | محرك embeddings لمضيف الذاكرة | صادرات محرك embeddings لمضيف الذاكرة |
  | `plugin-sdk/memory-core-host-engine-qmd` | محرك QMD لمضيف الذاكرة | صادرات محرك QMD لمضيف الذاكرة |
  | `plugin-sdk/memory-core-host-engine-storage` | محرك التخزين لمضيف الذاكرة | صادرات محرك التخزين لمضيف الذاكرة |
  | `plugin-sdk/memory-core-host-multimodal` | أدوات multimodal لمضيف الذاكرة | أدوات multimodal لمضيف الذاكرة |
  | `plugin-sdk/memory-core-host-query` | أدوات الاستعلام لمضيف الذاكرة | أدوات الاستعلام لمضيف الذاكرة |
  | `plugin-sdk/memory-core-host-secret` | أدوات الأسرار لمضيف الذاكرة | أدوات الأسرار لمضيف الذاكرة |
  | `plugin-sdk/memory-core-host-events` | أدوات سجل أحداث مضيف الذاكرة | أدوات سجل أحداث مضيف الذاكرة |
  | `plugin-sdk/memory-core-host-status` | أدوات حالة مضيف الذاكرة | أدوات حالة مضيف الذاكرة |
  | `plugin-sdk/memory-core-host-runtime-cli` | وقت تشغيل CLI لمضيف الذاكرة | أدوات وقت تشغيل CLI لمضيف الذاكرة |
  | `plugin-sdk/memory-core-host-runtime-core` | وقت تشغيل core لمضيف الذاكرة | أدوات وقت تشغيل core لمضيف الذاكرة |
  | `plugin-sdk/memory-core-host-runtime-files` | أدوات ملف/وقت تشغيل لمضيف الذاكرة | أدوات ملف/وقت تشغيل لمضيف الذاكرة |
  | `plugin-sdk/memory-host-core` | اسم بديل لوقت تشغيل core لمضيف الذاكرة | اسم بديل محايد للبائع لأدوات وقت تشغيل core لمضيف الذاكرة |
  | `plugin-sdk/memory-host-events` | اسم بديل لسجل أحداث مضيف الذاكرة | اسم بديل محايد للبائع لأدوات سجل أحداث مضيف الذاكرة |
  | `plugin-sdk/memory-host-files` | اسم بديل لأدوات ملف/وقت تشغيل مضيف الذاكرة | اسم بديل محايد للبائع لأدوات ملف/وقت تشغيل مضيف الذاكرة |
  | `plugin-sdk/memory-host-markdown` | أدوات markdown مُدارة | أدوات markdown مُدارة مشتركة للإضافات القريبة من الذاكرة |
  | `plugin-sdk/memory-host-search` | واجهة بحث الذاكرة النشطة | واجهة وقت تشغيل lazy active-memory search-manager |
  | `plugin-sdk/memory-host-status` | اسم بديل لحالة مضيف الذاكرة | اسم بديل محايد للبائع لأدوات حالة مضيف الذاكرة |
  | `plugin-sdk/memory-lancedb` | أدوات memory-lancedb المضمنة | سطح أدوات memory-lancedb |
  | `plugin-sdk/testing` | أدوات الاختبار | أدوات الاختبار وmockات |
</Accordion>

هذا الجدول هو عمدًا مجموعة الترحيل الشائعة، وليس سطح SDK الكامل.
القائمة الكاملة التي تضم أكثر من 200 نقطة دخول موجودة في
`scripts/lib/plugin-sdk-entrypoints.json`.

لا تزال تلك القائمة تتضمن بعض واجهات المساعدة الخاصة بالإضافات المضمنة مثل
`plugin-sdk/feishu` و`plugin-sdk/feishu-setup` و`plugin-sdk/zalo` و
`plugin-sdk/zalo-setup` و`plugin-sdk/matrix*`. لا تزال هذه الواجهات مُصدّرة
لصيانة الإضافات المضمنة والتوافق، لكنها حُذفت عمدًا من جدول الترحيل الشائع
وليست الهدف الموصى به لكتابة إضافات جديدة.

وتنطبق القاعدة نفسها على عائلات المساعدات المضمنة الأخرى مثل:

- أدوات دعم المتصفح المساعدة: `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support`
- Matrix: `plugin-sdk/matrix*`
- LINE: `plugin-sdk/line*`
- IRC: `plugin-sdk/irc*`
- الأسطح المضمنة للمساعدات/الإضافات مثل `plugin-sdk/googlechat`,
  و`plugin-sdk/zalouser`, و`plugin-sdk/bluebubbles*`,
  و`plugin-sdk/mattermost*`, و`plugin-sdk/msteams`,
  و`plugin-sdk/nextcloud-talk`, و`plugin-sdk/nostr`, و`plugin-sdk/tlon`,
  و`plugin-sdk/twitch`,
  و`plugin-sdk/github-copilot-login`, و`plugin-sdk/github-copilot-token`,
  و`plugin-sdk/diagnostics-otel`, و`plugin-sdk/diffs`, و`plugin-sdk/llm-task`,
  و`plugin-sdk/thread-ownership`, و`plugin-sdk/voice-call`

يكشف `plugin-sdk/github-copilot-token` حاليًا عن
سطح أدوات الرموز الضيق `DEFAULT_COPILOT_API_BASE_URL`,
و`deriveCopilotApiBaseUrlFromToken`، و`resolveCopilotApiToken`.

استخدم أضيق استيراد يطابق المهمة. إذا لم تتمكن من العثور على عنصر مُصدَّر،
فتحقق من المصدر في `src/plugin-sdk/` أو اسأل في Discord.

## الجدول الزمني للإزالة

| متى | ما الذي يحدث |
| ---------------------- | ----------------------------------------------------------------------- |
| **الآن** | تصدر الأسطح المهجورة تحذيرات وقت التشغيل |
| **الإصدار الرئيسي التالي** | ستُزال الأسطح المهجورة؛ وستفشل الإضافات التي لا تزال تستخدمها |

تم بالفعل ترحيل جميع الإضافات الأساسية. يجب على الإضافات الخارجية الترحيل
قبل الإصدار الرئيسي التالي.

## إخفاء التحذيرات مؤقتًا

اضبط متغيرات البيئة هذه أثناء العمل على الترحيل:

```bash
OPENCLAW_SUPPRESS_PLUGIN_SDK_COMPAT_WARNING=1 openclaw gateway run
OPENCLAW_SUPPRESS_EXTENSION_API_WARNING=1 openclaw gateway run
```

هذا مخرج مؤقت، وليس حلًا دائمًا.

## ذو صلة

- [البدء](/ar/plugins/building-plugins) — أنشئ إضافتك الأولى
- [نظرة عامة على SDK](/ar/plugins/sdk-overview) — مرجع كامل لعمليات الاستيراد حسب المسار الفرعي
- [إضافات القنوات](/ar/plugins/sdk-channel-plugins) — بناء إضافات القنوات
- [إضافات الموفّرات](/ar/plugins/sdk-provider-plugins) — بناء إضافات الموفّرات
- [الهيكل الداخلي للإضافات](/ar/plugins/architecture) — نظرة معمارية متعمقة
- [بيان الإضافة](/ar/plugins/manifest) — مرجع مخطط البيان
