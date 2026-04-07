---
read_when:
    - ترى التحذير OPENCLAW_PLUGIN_SDK_COMPAT_DEPRECATED
    - ترى التحذير OPENCLAW_EXTENSION_API_DEPRECATED
    - أنت تحدّث إضافة إلى بنية الإضافات الحديثة
    - أنت تصون إضافة OpenClaw خارجية
sidebarTitle: Migrate to SDK
summary: الانتقال من طبقة التوافق العكسي القديمة إلى plugin SDK الحديث
title: ترحيل Plugin SDK
x-i18n:
    generated_at: "2026-04-07T07:20:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3691060e9dc00ca8bee49240a047f0479398691bd14fb96e9204cc9243fdb32c
    source_path: plugins/sdk-migration.md
    workflow: 15
---

# ترحيل Plugin SDK

انتقل OpenClaw من طبقة توافق عكسي واسعة إلى بنية إضافات حديثة ذات عمليات
استيراد مركزة وموثقة. إذا كانت إضافتك قد بُنيت قبل البنية الجديدة، فسيساعدك
هذا الدليل على ترحيلها.

## ما الذي يتغير

كان نظام الإضافات القديم يوفر سطحين مفتوحين على مصراعيهما يتيحان للإضافات
استيراد أي شيء تحتاجه من نقطة دخول واحدة:

- **`openclaw/plugin-sdk/compat`** — استيراد واحد يعيد تصدير عشرات من
  المساعدات. وقد تم تقديمه لإبقاء الإضافات القديمة المعتمدة على hooks عاملة
  أثناء بناء بنية الإضافات الجديدة.
- **`openclaw/extension-api`** — جسر منح الإضافات وصولًا مباشرًا إلى
  المساعدات على جانب المضيف مثل مشغّل الوكيل المضمّن.

كلا السطحين الآن **مهملان**. لا يزالان يعملان في وقت التشغيل، لكن يجب ألا
تستخدمهما الإضافات الجديدة، ويجب أن ترحّل الإضافات الحالية قبل أن تزيلهما
النسخة الرئيسية التالية.

<Warning>
  ستتم إزالة طبقة التوافق العكسي في إصدار رئيسي مستقبلي.
  الإضافات التي لا تزال تستورد من هذه الأسطح ستتعطل عند حدوث ذلك.
</Warning>

## لماذا تغير هذا

تسبب النهج القديم في مشكلات:

- **بدء تشغيل بطيء** — كان استيراد مساعد واحد يحمّل عشرات الوحدات غير
  المرتبطة
- **اعتماديات دائرية** — جعلت إعادة التصدير الواسعة من السهل إنشاء دورات
  استيراد
- **سطح API غير واضح** — لم تكن هناك طريقة لمعرفة أي التصديرات مستقرة
  وأيها داخلية

يصلح plugin SDK الحديث هذا: كل مسار استيراد (`openclaw/plugin-sdk/\<subpath\>`)
هو وحدة صغيرة مكتفية ذاتيًا ذات غرض واضح وعقد موثق.

كما أزيلت أيضًا فواصل الراحة القديمة الخاصة بالمزوّدين للقنوات المضمّنة.
فالاستيرادات مثل `openclaw/plugin-sdk/slack` و`openclaw/plugin-sdk/discord` و
`openclaw/plugin-sdk/signal` و`openclaw/plugin-sdk/whatsapp`،
وفواصل المساعدات ذات العلامات الخاصة بالقنوات، و
`openclaw/plugin-sdk/telegram-core` كانت اختصارات خاصة بالمستودع الأحادي،
وليست عقود إضافات مستقرة. استخدم بدلًا من ذلك مسارات SDK عامة ضيقة. داخل
workspace الإضافات المضمّنة، أبقِ المساعدات المملوكة للمزوّد في `api.ts`
أو `runtime-api.ts` الخاصين بتلك الإضافة.

أمثلة المزوّدات المضمّنة الحالية:

- تحتفظ Anthropic بمساعدات البث الخاصة بـ Claude في الفاصل الخاص بها
  `api.ts` / `contract-api.ts`
- تحتفظ OpenAI بمنشئات المزوّد، ومساعدات النموذج الافتراضي، ومنشئات المزوّد
  الفوري في `api.ts` الخاص بها
- تحتفظ OpenRouter بمنشئ المزوّد ومساعدات onboarding/config في
  `api.ts` الخاص بها

## كيفية الترحيل

<Steps>
  <Step title="راجع سلوك الرجوع الاحتياطي لغلاف Windows">
    إذا كانت إضافتك تستخدم `openclaw/plugin-sdk/windows-spawn`، فإن أغلفة
    Windows من نوع `.cmd`/`.bat` غير المحلولة تفشل الآن بشكل مغلق ما لم تمرّر
    صراحةً `allowShellFallback: true`.

    ```typescript
    // Before
    const program = applyWindowsSpawnProgramPolicy({ candidate });

    // After
    const program = applyWindowsSpawnProgramPolicy({
      candidate,
      // Only set this for trusted compatibility callers that intentionally
      // accept shell-mediated fallback.
      allowShellFallback: true,
    });
    ```

    إذا لم يكن المستدعي لديك يعتمد عمدًا على الرجوع الاحتياطي عبر shell، فلا
    تضبط `allowShellFallback` وتعامل مع الخطأ المطروح بدلًا من ذلك.

  </Step>

  <Step title="ابحث عن عمليات الاستيراد المهملة">
    ابحث في إضافتك عن عمليات استيراد من أي من السطحين المهملين:

    ```bash
    grep -r "plugin-sdk/compat" my-plugin/
    grep -r "openclaw/extension-api" my-plugin/
    ```

  </Step>

  <Step title="استبدلها بعمليات استيراد مركزة">
    يطابق كل تصدير من السطح القديم مسار استيراد حديثًا محددًا:

    ```typescript
    // Before (deprecated backwards-compatibility layer)
    import {
      createChannelReplyPipeline,
      createPluginRuntimeStore,
      resolveControlCommandGate,
    } from "openclaw/plugin-sdk/compat";

    // After (modern focused imports)
    import { createChannelReplyPipeline } from "openclaw/plugin-sdk/channel-reply-pipeline";
    import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
    import { resolveControlCommandGate } from "openclaw/plugin-sdk/command-auth";
    ```

    بالنسبة إلى المساعدات على جانب المضيف، استخدم وقت تشغيل الإضافة المحقون
    بدلًا من الاستيراد المباشر:

    ```typescript
    // Before (deprecated extension-api bridge)
    import { runEmbeddedPiAgent } from "openclaw/extension-api";
    const result = await runEmbeddedPiAgent({ sessionId, prompt });

    // After (injected runtime)
    const result = await api.runtime.agent.runEmbeddedPiAgent({ sessionId, prompt });
    ```

    ينطبق النمط نفسه على مساعدات الجسر القديمة الأخرى:

    | الاستيراد القديم | المكافئ الحديث |
    | --- | --- |
    | `resolveAgentDir` | `api.runtime.agent.resolveAgentDir` |
    | `resolveAgentWorkspaceDir` | `api.runtime.agent.resolveAgentWorkspaceDir` |
    | `resolveAgentIdentity` | `api.runtime.agent.resolveAgentIdentity` |
    | `resolveThinkingDefault` | `api.runtime.agent.resolveThinkingDefault` |
    | `resolveAgentTimeoutMs` | `api.runtime.agent.resolveAgentTimeoutMs` |
    | `ensureAgentWorkspace` | `api.runtime.agent.ensureAgentWorkspace` |
    | مساعدات مخزن الجلسات | `api.runtime.agent.session.*` |

  </Step>

  <Step title="ابنِ واختبر">
    ```bash
    pnpm build
    pnpm test -- my-plugin/
    ```
  </Step>
</Steps>

## مرجع مسار الاستيراد

<Accordion title="جدول مسارات الاستيراد الشائعة">
  | مسار الاستيراد | الغرض | التصديرات الأساسية |
  | --- | --- | --- |
  | `plugin-sdk/plugin-entry` | مساعد نقطة دخول الإضافة القانوني | `definePluginEntry` |
  | `plugin-sdk/core` | إعادة تصدير قديمة جامعة لتعريفات/منشئات إدخال القنوات | `defineChannelPluginEntry`, `createChatChannelPlugin` |
  | `plugin-sdk/config-schema` | تصدير مخطط الإعدادات الجذري | `OpenClawSchema` |
  | `plugin-sdk/provider-entry` | مساعد إدخال مزوّد واحد | `defineSingleProviderPluginEntry` |
  | `plugin-sdk/channel-core` | تعريفات ومنشئات إدخال قنوات مركزة | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
  | `plugin-sdk/setup` | مساعدات معالج الإعداد المشتركة | مطالبات قائمة السماح، ومنشئات حالة الإعداد |
  | `plugin-sdk/setup-runtime` | مساعدات وقت تشغيل الإعداد | محولات تصحيح الإعداد الآمنة للاستيراد، ومساعدات ملاحظات البحث، و`promptResolvedAllowFrom`، و`splitSetupEntries`، ووكلاء الإعداد المفوضون |
  | `plugin-sdk/setup-adapter-runtime` | مساعدات محول الإعداد | `createEnvPatchedAccountSetupAdapter` |
  | `plugin-sdk/setup-tools` | مساعدات أدوات الإعداد | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
  | `plugin-sdk/account-core` | مساعدات الحسابات المتعددة | مساعدات قائمة الحسابات/الإعدادات/بوابة الإجراءات |
  | `plugin-sdk/account-id` | مساعدات معرّف الحساب | `DEFAULT_ACCOUNT_ID`، وتطبيع معرّف الحساب |
  | `plugin-sdk/account-resolution` | مساعدات البحث عن الحساب | مساعدات البحث عن الحساب + الرجوع الاحتياطي الافتراضي |
  | `plugin-sdk/account-helpers` | مساعدات حساب ضيقة | مساعدات قائمة الحسابات/إجراءات الحساب |
  | `plugin-sdk/channel-setup` | محولات معالج الإعداد | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`، بالإضافة إلى `DEFAULT_ACCOUNT_ID` و`createTopLevelChannelDmPolicy` و`setSetupChannelEnabled` و`splitSetupEntries` |
  | `plugin-sdk/channel-pairing` | أساسيات الاقتران عبر DM | `createChannelPairingController` |
  | `plugin-sdk/channel-reply-pipeline` | توصيل بادئة الرد + الكتابة | `createChannelReplyPipeline` |
  | `plugin-sdk/channel-config-helpers` | مصانع محولات الإعدادات | `createHybridChannelConfigAdapter` |
  | `plugin-sdk/channel-config-schema` | منشئات مخطط الإعدادات | أنواع مخطط إعدادات القناة |
  | `plugin-sdk/telegram-command-config` | مساعدات إعداد أوامر Telegram | تطبيع أسماء الأوامر، وتشذيب الوصف، والتحقق من التكرار/التعارض |
  | `plugin-sdk/channel-policy` | حل سياسات المجموعات/DM | `resolveChannelGroupRequireMention` |
  | `plugin-sdk/channel-lifecycle` | تتبع حالة الحساب | `createAccountStatusSink` |
  | `plugin-sdk/inbound-envelope` | مساعدات الظرف الوارد | مساعدات المسار المشترك + منشئ الظرف |
  | `plugin-sdk/inbound-reply-dispatch` | مساعدات الرد الوارد | مساعدات التسجيل والإرسال المشتركة |
  | `plugin-sdk/messaging-targets` | تحليل أهداف المراسلة | مساعدات تحليل/مطابقة الأهداف |
  | `plugin-sdk/outbound-media` | مساعدات الوسائط الصادرة | تحميل الوسائط الصادرة المشتركة |
  | `plugin-sdk/outbound-runtime` | مساعدات وقت التشغيل الصادر | مساعدات الهوية الصادرة/التفويض بالإرسال |
  | `plugin-sdk/thread-bindings-runtime` | مساعدات ربط السلاسل | دورة حياة ربط السلاسل ومساعدات المحول |
  | `plugin-sdk/agent-media-payload` | مساعدات حمولة الوسائط القديمة | منشئ حمولة وسائط الوكيل لتخطيطات الحقول القديمة |
  | `plugin-sdk/channel-runtime` | حشوة توافق مهملة | أدوات وقت تشغيل القنوات القديمة فقط |
  | `plugin-sdk/channel-send-result` | أنواع نتائج الإرسال | أنواع نتائج الرد |
  | `plugin-sdk/runtime-store` | تخزين الإضافات الدائم | `createPluginRuntimeStore` |
  | `plugin-sdk/runtime` | مساعدات وقت تشغيل واسعة | مساعدات وقت التشغيل/التسجيل/النسخ الاحتياطي/تثبيت الإضافات |
  | `plugin-sdk/runtime-env` | مساعدات بيئة وقت تشغيل ضيقة | مساعدات المسجل/بيئة وقت التشغيل، والمهلة، وإعادة المحاولة، والتراجع |
  | `plugin-sdk/plugin-runtime` | مساعدات وقت تشغيل الإضافات المشتركة | مساعدات أوامر/‏hooks/‏http/‏التفاعل للإضافات |
  | `plugin-sdk/hook-runtime` | مساعدات مسار hooks | مساعدات مسار webhook/internal hook المشتركة |
  | `plugin-sdk/lazy-runtime` | مساعدات وقت التشغيل الكسول | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeMethodBinder`, `createLazyRuntimeNamedExport`, `createLazyRuntimeSurface` |
  | `plugin-sdk/process-runtime` | مساعدات العمليات | مساعدات التنفيذ المشتركة |
  | `plugin-sdk/cli-runtime` | مساعدات وقت تشغيل CLI | تنسيق الأوامر، والانتظار، ومساعدات الإصدار |
  | `plugin-sdk/gateway-runtime` | مساعدات Gateway | عميل Gateway ومساعدات تصحيح حالة القناة |
  | `plugin-sdk/config-runtime` | مساعدات الإعدادات | مساعدات تحميل/كتابة الإعدادات |
  | `plugin-sdk/telegram-command-config` | مساعدات أوامر Telegram | مساعدات تحقق مستقرة للرجوع الاحتياطي لأوامر Telegram عندما يكون سطح عقد Telegram المضمّن غير متاح |
  | `plugin-sdk/approval-runtime` | مساعدات مطالبة الموافقة | حمولة موافقة التنفيذ/الإضافة، ومساعدات قدرة/ملف تعريف الموافقة، ومساعدات التوجيه/وقت التشغيل الأصلي للموافقة |
  | `plugin-sdk/approval-auth-runtime` | مساعدات مصادقة الموافقة | حلّ المُوافق، ومصادقة الإجراء داخل المحادثة نفسها |
  | `plugin-sdk/approval-client-runtime` | مساعدات عميل الموافقة | مساعدات ملف تعريف/تصفية الموافقة الأصلية للتنفيذ |
  | `plugin-sdk/approval-delivery-runtime` | مساعدات تسليم الموافقة | محولات قدرة/تسليم الموافقة الأصلية |
  | `plugin-sdk/approval-native-runtime` | مساعدات هدف الموافقة | مساعدات ربط هدف/حساب الموافقة الأصلية |
  | `plugin-sdk/approval-reply-runtime` | مساعدات رد الموافقة | مساعدات حمولة رد الموافقة للتنفيذ/الإضافة |
  | `plugin-sdk/security-runtime` | مساعدات الأمان | مساعدات الثقة المشتركة، وبوابات DM، والمحتوى الخارجي، وجمع الأسرار |
  | `plugin-sdk/ssrf-policy` | مساعدات سياسة SSRF | مساعدات قائمة سماح المضيف وسياسة الشبكة الخاصة |
  | `plugin-sdk/ssrf-runtime` | مساعدات وقت تشغيل SSRF | مساعدات pinned-dispatcher وguarded fetch وسياسة SSRF |
  | `plugin-sdk/collection-runtime` | مساعدات ذاكرة التخزين المؤقت المحدودة | `pruneMapToMaxSize` |
  | `plugin-sdk/diagnostic-runtime` | مساعدات بوابات التشخيص | `isDiagnosticFlagEnabled`, `isDiagnosticsEnabled` |
  | `plugin-sdk/error-runtime` | مساعدات تنسيق الأخطاء | `formatUncaughtError`, `isApprovalNotFoundError`، ومساعدات رسم الأخطاء |
  | `plugin-sdk/fetch-runtime` | مساعدات fetch/proxy المغلفة | `resolveFetch`، ومساعدات الوكيل |
  | `plugin-sdk/host-runtime` | مساعدات تطبيع المضيف | `normalizeHostname`, `normalizeScpRemoteHost` |
  | `plugin-sdk/retry-runtime` | مساعدات إعادة المحاولة | `RetryConfig`, `retryAsync`، ومشغلات السياسات |
  | `plugin-sdk/allow-from` | تنسيق قائمة السماح | `formatAllowFromLowercase` |
  | `plugin-sdk/allowlist-resolution` | تعيين مدخلات قائمة السماح | `mapAllowlistResolutionInputs` |
  | `plugin-sdk/command-auth` | بوابات الأوامر ومساعدات سطح الأوامر | `resolveControlCommandGate`، ومساعدات تفويض المرسل، ومساعدات سجل الأوامر |
  | `plugin-sdk/secret-input` | تحليل مدخلات الأسرار | مساعدات مدخلات الأسرار |
  | `plugin-sdk/webhook-ingress` | مساعدات طلبات webhook | أدوات هدف webhook |
  | `plugin-sdk/webhook-request-guards` | مساعدات حراسة جسم webhook | مساعدات قراءة/تحديد جسم الطلب |
  | `plugin-sdk/reply-runtime` | وقت تشغيل الرد المشترك | الإرسال الوارد، ونبضات القلب، ومخطط الرد، والتقطيع |
  | `plugin-sdk/reply-dispatch-runtime` | مساعدات ضيقة لإرسال الرد | مساعدات الإنهاء + إرسال المزوّد |
  | `plugin-sdk/reply-history` | مساعدات سجل الرد | `buildHistoryContext`, `buildPendingHistoryContextFromMap`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` |
  | `plugin-sdk/reply-reference` | تخطيط مراجع الرد | `createReplyReferencePlanner` |
  | `plugin-sdk/reply-chunking` | مساعدات تقطيع الرد | مساعدات تقطيع النص/markdown |
  | `plugin-sdk/session-store-runtime` | مساعدات مخزن الجلسات | مساعدات مسار المخزن + updated-at |
  | `plugin-sdk/state-paths` | مساعدات مسارات الحالة | مساعدات الحالة ودليل OAuth |
  | `plugin-sdk/routing` | مساعدات التوجيه/مفتاح الجلسة | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId`، ومساعدات تطبيع مفتاح الجلسة |
  | `plugin-sdk/status-helpers` | مساعدات حالة القناة | منشئات ملخص حالة القناة/الحساب، وافتراضيات حالة وقت التشغيل، ومساعدات بيانات تعريف المشكلات |
  | `plugin-sdk/target-resolver-runtime` | مساعدات محلل الهدف | مساعدات محلل الهدف المشتركة |
  | `plugin-sdk/string-normalization-runtime` | مساعدات تطبيع السلاسل | مساعدات تطبيع slug/string |
  | `plugin-sdk/request-url` | مساعدات URL الطلب | استخراج URLات نصية من مدخلات شبيهة بالطلبات |
  | `plugin-sdk/run-command` | مساعدات الأوامر الموقّتة | مشغّل أوامر موقّت مع stdout/stderr مطبّعين |
  | `plugin-sdk/param-readers` | قارئات المعاملات | قارئات معاملات الأدوات/CLI الشائعة |
  | `plugin-sdk/tool-send` | استخراج إرسال الأداة | استخراج حقول هدف الإرسال القانونية من وسائط الأداة |
  | `plugin-sdk/temp-path` | مساعدات المسارات المؤقتة | مساعدات مسارات التنزيل المؤقتة المشتركة |
  | `plugin-sdk/logging-core` | مساعدات التسجيل | مسجل النظام الفرعي ومساعدات التنقيح |
  | `plugin-sdk/markdown-table-runtime` | مساعدات جداول Markdown | مساعدات وضع جدول Markdown |
  | `plugin-sdk/reply-payload` | أنواع رد الرسائل | أنواع حمولة الرد |
  | `plugin-sdk/provider-setup` | مساعدات إعداد مزوّد محلي/مستضاف ذاتيًا منسّقة | مساعدات اكتشاف/إعداد المزوّد المستضاف ذاتيًا |
  | `plugin-sdk/self-hosted-provider-setup` | مساعدات مركزة لإعداد مزوّدات مستضافة ذاتيًا متوافقة مع OpenAI | مساعدات اكتشاف/إعداد المزوّد المستضاف ذاتيًا نفسها |
  | `plugin-sdk/provider-auth-runtime` | مساعدات المصادقة في وقت تشغيل المزوّد | مساعدات حل مفتاح API في وقت التشغيل |
  | `plugin-sdk/provider-auth-api-key` | مساعدات إعداد مفتاح API للمزوّد | مساعدات onboarding/كتابة ملف التعريف لمفتاح API |
  | `plugin-sdk/provider-auth-result` | مساعدات نتيجة مصادقة المزوّد | منشئ auth-result قياسي لـ OAuth |
  | `plugin-sdk/provider-auth-login` | مساعدات تسجيل الدخول التفاعلي للمزوّد | مساعدات تسجيل الدخول التفاعلي المشتركة |
  | `plugin-sdk/provider-env-vars` | مساعدات متغيرات البيئة للمزوّد | مساعدات البحث عن متغيرات بيئة مصادقة المزوّد |
  | `plugin-sdk/provider-model-shared` | مساعدات مشتركة للنموذج/إعادة التشغيل للمزوّد | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`، ومنشئات سياسة إعادة التشغيل المشتركة، ومساعدات نقاط نهاية المزوّد، ومساعدات تطبيع معرّف النموذج |
  | `plugin-sdk/provider-catalog-shared` | مساعدات كتالوج المزوّد المشتركة | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
  | `plugin-sdk/provider-onboard` | تصحيحات onboarding للمزوّد | مساعدات إعدادات onboarding |
  | `plugin-sdk/provider-http` | مساعدات HTTP للمزوّد | مساعدات HTTP/قدرات نقاط النهاية العامة للمزوّد |
  | `plugin-sdk/provider-web-fetch` | مساعدات web-fetch للمزوّد | مساعدات تسجيل/ذاكرة التخزين المؤقت لمزوّد web-fetch |
  | `plugin-sdk/provider-web-search-contract` | مساعدات عقد web-search للمزوّد | مساعدات ضيقة لعقد إعدادات/بيانات اعتماد web-search مثل `enablePluginInConfig` و`resolveProviderWebSearchPluginConfig` وضبط/جلب بيانات الاعتماد المحدودة |
  | `plugin-sdk/provider-web-search` | مساعدات web-search للمزوّد | مساعدات تسجيل/ذاكرة التخزين المؤقت/وقت التشغيل لمزوّد web-search |
  | `plugin-sdk/provider-tools` | مساعدات توافق أدوات/مخططات المزوّد | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`، وتنظيف مخطط Gemini + التشخيصات، ومساعدات توافق xAI مثل `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
  | `plugin-sdk/provider-usage` | مساعدات استخدام المزوّد | `fetchClaudeUsage`, `fetchGeminiUsage`, `fetchGithubCopilotUsage`، ومساعدات استخدام مزوّد أخرى |
  | `plugin-sdk/provider-stream` | مساعدات أغلفة تدفق المزوّد | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`، وأنواع أغلفة التدفق، ومساعدات الأغلفة المشتركة لـ Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
  | `plugin-sdk/keyed-async-queue` | طابور async مرتب | `KeyedAsyncQueue` |
  | `plugin-sdk/media-runtime` | مساعدات الوسائط المشتركة | مساعدات جلب/تحويل/تخزين الوسائط بالإضافة إلى منشئات حمولة الوسائط |
  | `plugin-sdk/media-generation-runtime` | مساعدات مشتركة لتوليد الوسائط | مساعدات الرجوع الاحتياطي المشتركة، واختيار المرشحين، ورسائل غياب النموذج لتوليد الصور/الفيديو/الموسيقى |
  | `plugin-sdk/media-understanding` | مساعدات فهم الوسائط | أنواع مزوّدات فهم الوسائط بالإضافة إلى تصديرات مساعدات الصور/الصوت المواجهة للمزوّد |
  | `plugin-sdk/text-runtime` | مساعدات النص المشتركة | إزالة النص المرئي للمساعد، ومساعدات عرض/تقطيع/جداول markdown، ومساعدات التنقيح، ومساعدات علامات التوجيه، وأدوات النص الآمن، ومساعدات النص/التسجيل ذات الصلة |
  | `plugin-sdk/text-chunking` | مساعدات تقطيع النص | مساعد تقطيع النص الصادر |
  | `plugin-sdk/speech` | مساعدات Speech | أنواع مزوّدات Speech بالإضافة إلى مساعدات التوجيه، والسجل، والتحقق المواجهة للمزوّد |
  | `plugin-sdk/speech-core` | النواة المشتركة لـ Speech | أنواع مزوّدات Speech، والسجل، والتوجيهات، والتطبيع |
  | `plugin-sdk/realtime-transcription` | مساعدات النسخ الفوري | أنواع المزوّدات ومساعدات السجل |
  | `plugin-sdk/realtime-voice` | مساعدات الصوت الفوري | أنواع المزوّدات ومساعدات السجل |
  | `plugin-sdk/image-generation-core` | النواة المشتركة لتوليد الصور | أنواع توليد الصور، والرجوع الاحتياطي، والمصادقة، ومساعدات السجل |
  | `plugin-sdk/music-generation` | مساعدات توليد الموسيقى | أنواع المزوّد/الطلب/النتيجة لتوليد الموسيقى |
  | `plugin-sdk/music-generation-core` | النواة المشتركة لتوليد الموسيقى | أنواع توليد الموسيقى، ومساعدات الرجوع الاحتياطي، والبحث عن المزوّد، وتحليل model-ref |
  | `plugin-sdk/video-generation` | مساعدات توليد الفيديو | أنواع المزوّد/الطلب/النتيجة لتوليد الفيديو |
  | `plugin-sdk/video-generation-core` | النواة المشتركة لتوليد الفيديو | أنواع توليد الفيديو، ومساعدات الرجوع الاحتياطي، والبحث عن المزوّد، وتحليل model-ref |
  | `plugin-sdk/interactive-runtime` | مساعدات الرد التفاعلي | تطبيع/تقليل حمولة الرد التفاعلي |
  | `plugin-sdk/channel-config-primitives` | أساسيات إعدادات القناة | أساسيات ضيقة لمخطط إعدادات القناة |
  | `plugin-sdk/channel-config-writes` | مساعدات كتابة إعدادات القناة | مساعدات تفويض كتابة إعدادات القناة |
  | `plugin-sdk/channel-plugin-common` | تمهيد القناة المشترك | تصديرات تمهيد الإضافة المشتركة للقنوات |
  | `plugin-sdk/channel-status` | مساعدات حالة القناة | مساعدات اللقطة/الملخص المشتركة لحالة القناة |
  | `plugin-sdk/allowlist-config-edit` | مساعدات إعدادات قائمة السماح | مساعدات تحرير/قراءة إعدادات قائمة السماح |
  | `plugin-sdk/group-access` | مساعدات وصول المجموعات | مساعدات قرارات وصول المجموعات المشتركة |
  | `plugin-sdk/direct-dm` | مساعدات Direct-DM | مساعدات المصادقة/الحراسة المشتركة لـ Direct-DM |
  | `plugin-sdk/extension-shared` | مساعدات الإضافات المشتركة | أساسيات مساعدات القناة/الحالة السلبية والوكيل المحيطي |
  | `plugin-sdk/webhook-targets` | مساعدات أهداف webhook | سجل أهداف webhook ومساعدات تثبيت المسارات |
  | `plugin-sdk/webhook-path` | مساعدات مسار webhook | مساعدات تطبيع مسار webhook |
  | `plugin-sdk/web-media` | مساعدات وسائط الويب المشتركة | مساعدات تحميل الوسائط البعيدة/المحلية |
  | `plugin-sdk/zod` | إعادة تصدير Zod | إعادة تصدير `zod` لمستهلكي plugin SDK |
  | `plugin-sdk/memory-core` | مساعدات memory-core المضمّنة | سطح مساعدات مدير الذاكرة/الإعداد/الملفات/CLI |
  | `plugin-sdk/memory-core-engine-runtime` | واجهة وقت تشغيل محرك الذاكرة | واجهة وقت تشغيل فهرسة/بحث الذاكرة |
  | `plugin-sdk/memory-core-host-engine-foundation` | محرك الأساس لمضيف الذاكرة | تصديرات محرك الأساس لمضيف الذاكرة |
  | `plugin-sdk/memory-core-host-engine-embeddings` | محرك embeddings لمضيف الذاكرة | تصديرات محرك embeddings لمضيف الذاكرة |
  | `plugin-sdk/memory-core-host-engine-qmd` | محرك QMD لمضيف الذاكرة | تصديرات محرك QMD لمضيف الذاكرة |
  | `plugin-sdk/memory-core-host-engine-storage` | محرك التخزين لمضيف الذاكرة | تصديرات محرك التخزين لمضيف الذاكرة |
  | `plugin-sdk/memory-core-host-multimodal` | مساعدات متعددة الوسائط لمضيف الذاكرة | مساعدات متعددة الوسائط لمضيف الذاكرة |
  | `plugin-sdk/memory-core-host-query` | مساعدات استعلام مضيف الذاكرة | مساعدات استعلام مضيف الذاكرة |
  | `plugin-sdk/memory-core-host-secret` | مساعدات أسرار مضيف الذاكرة | مساعدات أسرار مضيف الذاكرة |
  | `plugin-sdk/memory-core-host-events` | مساعدات سجل أحداث مضيف الذاكرة | مساعدات سجل أحداث مضيف الذاكرة |
  | `plugin-sdk/memory-core-host-status` | مساعدات حالة مضيف الذاكرة | مساعدات حالة مضيف الذاكرة |
  | `plugin-sdk/memory-core-host-runtime-cli` | وقت تشغيل CLI لمضيف الذاكرة | مساعدات وقت تشغيل CLI لمضيف الذاكرة |
  | `plugin-sdk/memory-core-host-runtime-core` | وقت تشغيل النواة لمضيف الذاكرة | مساعدات وقت تشغيل النواة لمضيف الذاكرة |
  | `plugin-sdk/memory-core-host-runtime-files` | مساعدات ملفات/وقت تشغيل مضيف الذاكرة | مساعدات ملفات/وقت تشغيل مضيف الذاكرة |
  | `plugin-sdk/memory-host-core` | اسم مستعار لوقت تشغيل نواة مضيف الذاكرة | اسم مستعار محايد للمورّد لمساعدات وقت تشغيل نواة مضيف الذاكرة |
  | `plugin-sdk/memory-host-events` | اسم مستعار لسجل أحداث مضيف الذاكرة | اسم مستعار محايد للمورّد لمساعدات سجل أحداث مضيف الذاكرة |
  | `plugin-sdk/memory-host-files` | اسم مستعار لملفات/وقت تشغيل مضيف الذاكرة | اسم مستعار محايد للمورّد لمساعدات ملفات/وقت تشغيل مضيف الذاكرة |
  | `plugin-sdk/memory-host-markdown` | مساعدات markdown المُدارة | مساعدات managed-markdown المشتركة للإضافات المجاورة للذاكرة |
  | `plugin-sdk/memory-host-search` | واجهة بحث الذاكرة النشطة | واجهة وقت تشغيل كسولة لمدير بحث الذاكرة النشطة |
  | `plugin-sdk/memory-host-status` | اسم مستعار لحالة مضيف الذاكرة | اسم مستعار محايد للمورّد لمساعدات حالة مضيف الذاكرة |
  | `plugin-sdk/memory-lancedb` | مساعدات memory-lancedb المضمّنة | سطح مساعدات memory-lancedb |
  | `plugin-sdk/testing` | أدوات الاختبار | مساعدات ومحاكيات الاختبار |
</Accordion>

هذا الجدول هو عمدًا المجموعة الفرعية الشائعة للترحيل، وليس سطح SDK الكامل.
القائمة الكاملة التي تضم أكثر من 200 نقطة دخول موجودة في
`scripts/lib/plugin-sdk-entrypoints.json`.

ولا تزال تلك القائمة تتضمن بعض فواصل مساعدات الإضافات المضمّنة مثل
`plugin-sdk/feishu` و`plugin-sdk/feishu-setup` و`plugin-sdk/zalo` و
`plugin-sdk/zalo-setup` و`plugin-sdk/matrix*`. وتظل هذه مُصدّرة من أجل
صيانة الإضافات المضمّنة والتوافق، لكنها حُذفت عمدًا من جدول الترحيل الشائع
وليست الهدف الموصى به لشيفرة الإضافات الجديدة.

تنطبق القاعدة نفسها على عائلات المساعدات المضمّنة الأخرى مثل:

- مساعدات دعم المتصفح: `plugin-sdk/browser-cdp` و`plugin-sdk/browser-config-runtime` و`plugin-sdk/browser-config-support` و`plugin-sdk/browser-control-auth` و`plugin-sdk/browser-node-runtime` و`plugin-sdk/browser-profiles` و`plugin-sdk/browser-security-runtime` و`plugin-sdk/browser-setup-tools` و`plugin-sdk/browser-support`
- Matrix: `plugin-sdk/matrix*`
- LINE: `plugin-sdk/line*`
- IRC: `plugin-sdk/irc*`
- أسطح المساعدات/الإضافات المضمّنة مثل `plugin-sdk/googlechat`،
  و`plugin-sdk/zalouser`، و`plugin-sdk/bluebubbles*`،
  و`plugin-sdk/mattermost*`، و`plugin-sdk/msteams`،
  و`plugin-sdk/nextcloud-talk`، و`plugin-sdk/nostr`، و`plugin-sdk/tlon`،
  و`plugin-sdk/twitch`،
  و`plugin-sdk/github-copilot-login`، و`plugin-sdk/github-copilot-token`،
  و`plugin-sdk/diagnostics-otel`، و`plugin-sdk/diffs`، و`plugin-sdk/llm-task`،
  و`plugin-sdk/thread-ownership`، و`plugin-sdk/voice-call`

يكشف `plugin-sdk/github-copilot-token` حاليًا عن سطح مساعدات الرموز الضيق
`DEFAULT_COPILOT_API_BASE_URL`،
و`deriveCopilotApiBaseUrlFromToken`، و`resolveCopilotApiToken`.

استخدم أضيق استيراد يطابق المهمة. إذا لم تتمكن من العثور على تصدير،
فتحقق من المصدر في `src/plugin-sdk/` أو اسأل في Discord.

## الجدول الزمني للإزالة

| متى                    | ما الذي يحدث                                                      |
| ---------------------- | ----------------------------------------------------------------- |
| **الآن**               | تصدر الأسطح المهملة تحذيرات في وقت التشغيل                        |
| **الإصدار الرئيسي التالي** | ستُزال الأسطح المهملة؛ وستفشل الإضافات التي لا تزال تستخدمها |

تم ترحيل كل الإضافات الأساسية بالفعل. يجب أن ترحّل الإضافات الخارجية قبل
الإصدار الرئيسي التالي.

## كتم التحذيرات مؤقتًا

اضبط متغيرات البيئة هذه أثناء عملك على الترحيل:

```bash
OPENCLAW_SUPPRESS_PLUGIN_SDK_COMPAT_WARNING=1 openclaw gateway run
OPENCLAW_SUPPRESS_EXTENSION_API_WARNING=1 openclaw gateway run
```

هذا منفذ هروب مؤقت، وليس حلًا دائمًا.

## ذو صلة

- [البدء](/ar/plugins/building-plugins) — أنشئ أول إضافة لك
- [نظرة عامة على SDK](/ar/plugins/sdk-overview) — مرجع كامل لعمليات الاستيراد عبر المسارات الفرعية
- [إضافات القنوات](/ar/plugins/sdk-channel-plugins) — بناء إضافات القنوات
- [إضافات المزوّدات](/ar/plugins/sdk-provider-plugins) — بناء إضافات المزوّدات
- [الآليات الداخلية للإضافات](/ar/plugins/architecture) — نظرة معمقة على البنية
- [بيان الإضافة](/ar/plugins/manifest) — مرجع مخطط البيان
