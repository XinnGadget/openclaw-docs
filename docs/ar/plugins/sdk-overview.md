---
read_when:
    - تحتاج إلى معرفة أي مسار فرعي من SDK يجب الاستيراد منه
    - تريد مرجعًا لجميع أساليب التسجيل على OpenClawPluginApi
    - تبحث عن تصدير محدد في SDK
sidebarTitle: SDK Overview
summary: خريطة الاستيراد، ومرجع واجهة برمجة تطبيقات التسجيل، وبنية SDK
title: نظرة عامة على Plugin SDK
x-i18n:
    generated_at: "2026-04-08T07:18:00Z"
    model: gpt-5.4
    provider: openai
    source_hash: a9141dc0303c91974fe693ce48ad9f7dc4179418ae262a96011ad565aae87d21
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# نظرة عامة على Plugin SDK

يُعد plugin SDK العقد المطبّع بين plugins والنواة. هذه الصفحة هي
المرجع الخاص بـ **ما يجب استيراده** و**ما الذي يمكنك تسجيله**.

<Tip>
  **هل تبحث عن دليل إرشادي؟**
  - أول plugin؟ ابدأ من [البدء](/ar/plugins/building-plugins)
  - Channel plugin؟ راجع [إضافات القنوات](/ar/plugins/sdk-channel-plugins)
  - Provider plugin؟ راجع [إضافات المزوّدين](/ar/plugins/sdk-provider-plugins)
</Tip>

## اصطلاح الاستيراد

استورد دائمًا من مسار فرعي محدد:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

كل مسار فرعي هو وحدة صغيرة مستقلة بذاتها. يساعد هذا في إبقاء بدء التشغيل سريعًا
ويمنع مشكلات الاعتماد الدائري. بالنسبة إلى أدوات إدخال/بناء القنوات الخاصة،
ففضّل `openclaw/plugin-sdk/channel-core`؛ واحتفظ بـ `openclaw/plugin-sdk/core`
للسطح الشامل الأوسع والمساعدات المشتركة مثل
`buildChannelConfigSchema`.

لا تضف أو تعتمد على واجهات ملاءمة مسماة بأسماء المزوّدين مثل
`openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp`، أو
واجهات المساعدة المميّزة بعلامات القنوات. يجب على bundled plugins تركيب
المسارات الفرعية العامة لـ SDK داخل ملفات `api.ts` أو `runtime-api.ts` الخاصة بها، ويجب
على النواة إما استخدام هذه الملفات المحلية الخاصة بالplugin أو إضافة عقد SDK عام ضيق
عندما تكون الحاجة فعلًا مشتركة بين عدة قنوات.

لا تزال خريطة التصدير المولّدة تحتوي على مجموعة صغيرة من
واجهات المساعدة الخاصة بـ bundled plugins مثل `plugin-sdk/feishu`,
`plugin-sdk/feishu-setup`, `plugin-sdk/zalo`, `plugin-sdk/zalo-setup`, و `plugin-sdk/matrix*`. توجد
هذه المسارات الفرعية فقط من أجل صيانة bundled plugins والتوافق؛ وقد أُزيلت عمدًا من الجدول الشائع أدناه
وليست هي مسار الاستيراد الموصى به لـ plugins الخارجية الجديدة.

## مرجع المسارات الفرعية

أكثر المسارات الفرعية استخدامًا، مجمّعة حسب الغرض. وتوجد القائمة الكاملة المولّدة
التي تتضمن أكثر من 200 مسار فرعي في `scripts/lib/plugin-sdk-entrypoints.json`.

لا تزال المسارات الفرعية المحجوزة لمساعدات bundled plugins تظهر في تلك القائمة المولدة.
تعامل معها على أنها تفاصيل تنفيذ/أسطح توافق ما لم تكن صفحة توثيق
تروّج صراحةً لواحد منها على أنه عام.

### إدخال plugin

| المسار الفرعي                     | أهم التصديرات                                                                                                                            |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/plugin-entry`   | `definePluginEntry`                                                                                                                    |
| `plugin-sdk/core`           | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema`  | `OpenClawSchema`                                                                                                                       |
| `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry`                                                                                                      |

<AccordionGroup>
  <Accordion title="المسارات الفرعية للقنوات">
    | المسار الفرعي | أهم التصديرات |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | تصدير مخطط Zod الجذري لـ `openclaw.json` (`OpenClawSchema`) |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`، بالإضافة إلى `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | مساعدات معالج الإعداد المشتركة، ومطالبات allowlist، وبناة حالة الإعداد |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | مساعدات تهيئة/بوابة إجراءات متعددة الحسابات، ومساعدات الرجوع إلى الحساب الافتراضي |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`، ومساعدات تطبيع معرّف الحساب |
    | `plugin-sdk/account-resolution` | مساعدات البحث عن الحساب + الرجوع الافتراضي |
    | `plugin-sdk/account-helpers` | مساعدات ضيقة لقائمة الحسابات/إجراءات الحساب |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | أنواع مخطط تهيئة القناة |
    | `plugin-sdk/telegram-command-config` | مساعدات تطبيع/تحقق الأوامر المخصصة في Telegram مع الرجوع إلى bundled contract |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | مساعدات مشتركة لمسار الإدخال + بناء المغلف |
    | `plugin-sdk/inbound-reply-dispatch` | مساعدات مشتركة لتسجيل الإدخال وتوزيعه |
    | `plugin-sdk/messaging-targets` | مساعدات تحليل/مطابقة الأهداف |
    | `plugin-sdk/outbound-media` | مساعدات مشتركة لتحميل الوسائط الصادرة |
    | `plugin-sdk/outbound-runtime` | مساعدات هوية الإرسال/التفويض للإرسال |
    | `plugin-sdk/thread-bindings-runtime` | دورة حياة ربط السلاسل ومساعدات المحوّل |
    | `plugin-sdk/agent-media-payload` | باني حمولة وسائط الوكيل القديم |
    | `plugin-sdk/conversation-runtime` | مساعدات ربط المحادثة/السلسلة والاقتران والربط المهيأ |
    | `plugin-sdk/runtime-config-snapshot` | مساعد لقطة تهيئة وقت التشغيل |
    | `plugin-sdk/runtime-group-policy` | مساعدات حل سياسة المجموعة في وقت التشغيل |
    | `plugin-sdk/channel-status` | مساعدات مشتركة للّقطة/الملخص لحالة القناة |
    | `plugin-sdk/channel-config-primitives` | أوليات ضيقة لمخطط تهيئة القناة |
    | `plugin-sdk/channel-config-writes` | مساعدات تفويض كتابة تهيئة القناة |
    | `plugin-sdk/channel-plugin-common` | تصديرات تمهيدية مشتركة لـ channel plugin |
    | `plugin-sdk/allowlist-config-edit` | مساعدات قراءة/تعديل تهيئة allowlist |
    | `plugin-sdk/group-access` | مساعدات مشتركة لاتخاذ قرار الوصول إلى المجموعة |
    | `plugin-sdk/direct-dm` | مساعدات مشتركة للمصادقة/الحماية في الرسائل المباشرة |
    | `plugin-sdk/interactive-runtime` | مساعدات تطبيع/اختزال حمولة الرد التفاعلي |
    | `plugin-sdk/channel-inbound` | إزالة الارتداد للإدخال، ومطابقة الذكر، ومساعدات سياسة الذكر، ومساعدات المغلف |
    | `plugin-sdk/channel-send-result` | أنواع نتيجة الرد |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | مساعدات تحليل/مطابقة الأهداف |
    | `plugin-sdk/channel-contract` | أنواع عقد القناة |
    | `plugin-sdk/channel-feedback` | توصيل التعليقات/التفاعلات |
    | `plugin-sdk/channel-secret-runtime` | مساعدات ضيقة لعقد الأسرار مثل `collectSimpleChannelFieldAssignments`, `getChannelSurface`, `pushAssignment`، وأنواع أهداف الأسرار |
  </Accordion>

  <Accordion title="المسارات الفرعية للمزوّدين">
    | المسار الفرعي | أهم التصديرات |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | مساعدات منسّقة لإعداد المزوّدين المحليين/المستضافين ذاتيًا |
    | `plugin-sdk/self-hosted-provider-setup` | مساعدات مركّزة لإعداد مزوّدات متوافقة مع OpenAI ومُستضافة ذاتيًا |
    | `plugin-sdk/cli-backend` | إعدادات CLI الخلفية الافتراضية + ثوابت watchdog |
    | `plugin-sdk/provider-auth-runtime` | مساعدات حل مفاتيح API في وقت التشغيل لـ provider plugins |
    | `plugin-sdk/provider-auth-api-key` | مساعدات ضمّ API key/الكتابة إلى الملف الشخصي مثل `upsertApiKeyProfile` |
    | `plugin-sdk/provider-auth-result` | باني نتيجة مصادقة OAuth القياسي |
    | `plugin-sdk/provider-auth-login` | مساعدات تسجيل الدخول التفاعلي المشتركة لـ provider plugins |
    | `plugin-sdk/provider-env-vars` | مساعدات البحث عن متغيرات البيئة لمصادقة المزوّد |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile`, `upsertApiKeyProfile`, `writeOAuthCredentials` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`، وبناة سياسة الإعادة المشتركة، ومساعدات نقاط نهاية المزوّد، ومساعدات تطبيع معرّف النموذج مثل `normalizeNativeXaiModelId` |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | مساعدات عامة لقدرات HTTP/نقطة النهاية للمزوّد |
    | `plugin-sdk/provider-web-fetch-contract` | مساعدات ضيقة لعقد تهيئة/اختيار web-fetch مثل `enablePluginInConfig` و `WebFetchProviderPlugin` |
    | `plugin-sdk/provider-web-fetch` | مساعدات تسجيل/تخزين مؤقت لمزوّد web-fetch |
    | `plugin-sdk/provider-web-search-contract` | مساعدات ضيقة لعقد تهيئة/بيانات اعتماد web-search مثل `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig`، وواضعات/جالبات بيانات اعتماد ضمن النطاق |
    | `plugin-sdk/provider-web-search` | مساعدات تسجيل/تخزين مؤقت/وقت تشغيل لمزوّد web-search |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`، وتنظيف مخطط Gemini + التشخيصات، ومساعدات توافق xAI مثل `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` وما شابه |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`، وأنواع أغلفة التدفق، ومساعدات الأغلفة المشتركة لـ Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
    | `plugin-sdk/provider-onboard` | مساعدات تصحيح التهيئة الخاصة بالإعداد الأولي |
    | `plugin-sdk/global-singleton` | مساعدات singleton/map/cache محلية على مستوى العملية |
  </Accordion>

  <Accordion title="المسارات الفرعية للمصادقة والأمان">
    | المسار الفرعي | أهم التصديرات |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`، ومساعدات سجل الأوامر، ومساعدات تفويض المرسِل |
    | `plugin-sdk/approval-auth-runtime` | مساعدات حل المعتمِد ومصادقة الإجراءات ضمن نفس المحادثة |
    | `plugin-sdk/approval-client-runtime` | مساعدات الملف الشخصي/المرشّح لاعتماد التنفيذ الأصلي |
    | `plugin-sdk/approval-delivery-runtime` | محولات قدرة/تسليم الاعتماد الأصلية |
    | `plugin-sdk/approval-gateway-runtime` | مساعد مشترك لحل approval gateway |
    | `plugin-sdk/approval-handler-adapter-runtime` | مساعدات خفيفة لتحميل محوّل الاعتماد الأصلي لنقاط دخول القنوات السريعة |
    | `plugin-sdk/approval-handler-runtime` | مساعدات أوسع لمعالِج الاعتماد في وقت التشغيل؛ فضّل الواجهات الأضيق للمحوّل/البوابة عندما تكون كافية |
    | `plugin-sdk/approval-native-runtime` | مساعدات الهدف الأصلي للاعتماد + ربط الحساب |
    | `plugin-sdk/approval-reply-runtime` | مساعدات حمولة رد اعتماد التنفيذ/الplugin |
    | `plugin-sdk/command-auth-native` | مصادقة الأوامر الأصلية + مساعدات هدف الجلسة الأصلية |
    | `plugin-sdk/command-detection` | مساعدات مشتركة لاكتشاف الأوامر |
    | `plugin-sdk/command-surface` | تطبيع جسم الأمر ومساعدات سطح الأوامر |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/channel-secret-runtime` | مساعدات ضيقة لجمع عقود الأسرار لأسطح أسرار القناة/الplugin |
    | `plugin-sdk/secret-ref-runtime` | مساعدات ضيقة لـ `coerceSecretRef` وكتابة SecretRef لتحليل عقود الأسرار/التهيئة |
    | `plugin-sdk/security-runtime` | مساعدات مشتركة للثقة، وبوابات الرسائل المباشرة، والمحتوى الخارجي، وجمع الأسرار |
    | `plugin-sdk/ssrf-policy` | مساعدات سياسة SSRF لقائمة السماح بالمضيفين والشبكات الخاصة |
    | `plugin-sdk/ssrf-runtime` | مساعدات pinned-dispatcher وfetch المحمي من SSRF وسياسة SSRF |
    | `plugin-sdk/secret-input` | مساعدات تحليل إدخال الأسرار |
    | `plugin-sdk/webhook-ingress` | مساعدات طلب/هدف webhook |
    | `plugin-sdk/webhook-request-guards` | مساعدات حجم/مهلة جسم الطلب |
  </Accordion>

  <Accordion title="المسارات الفرعية لوقت التشغيل والتخزين">
    | المسار الفرعي | أهم التصديرات |
    | --- | --- |
    | `plugin-sdk/runtime` | مساعدات واسعة لوقت التشغيل/التسجيل/النسخ الاحتياطي/تثبيت plugin |
    | `plugin-sdk/runtime-env` | مساعدات ضيقة لبيئة وقت التشغيل، والمسجّل، والمهلة، وإعادة المحاولة، والتراجع التدريجي |
    | `plugin-sdk/channel-runtime-context` | مساعدات عامة لتسجيل سياق وقت تشغيل القناة والبحث عنه |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | مساعدات مشتركة لأوامر/خطافات/HTTP/تفاعلية plugin |
    | `plugin-sdk/hook-runtime` | مساعدات مشتركة لخط أنابيب webhook/الخطاف الداخلي |
    | `plugin-sdk/lazy-runtime` | مساعدات الربط/الاستيراد الكسول لوقت التشغيل مثل `createLazyRuntimeModule`, `createLazyRuntimeMethod`, و `createLazyRuntimeSurface` |
    | `plugin-sdk/process-runtime` | مساعدات تنفيذ العمليات |
    | `plugin-sdk/cli-runtime` | مساعدات تنسيق CLI والانتظار والإصدار |
    | `plugin-sdk/gateway-runtime` | مساعدات عميل البوابة وتصحيح حالة القناة |
    | `plugin-sdk/config-runtime` | مساعدات تحميل/كتابة التهيئة |
    | `plugin-sdk/telegram-command-config` | تطبيع اسم/وصف أوامر Telegram وفحوصات التكرار/التعارض، حتى عند عدم توفر سطح عقد Telegram المضمّن |
    | `plugin-sdk/approval-runtime` | مساعدات اعتماد التنفيذ/الplugin، وبناة قدرات الاعتماد، ومساعدات المصادقة/الملف الشخصي، ومساعدات التوجيه الأصلي/وقت التشغيل |
    | `plugin-sdk/reply-runtime` | مساعدات مشتركة لوقت تشغيل الإدخال/الرد، والتقسيم، والتوزيع، والنبض، ومخطط الرد |
    | `plugin-sdk/reply-dispatch-runtime` | مساعدات ضيقة لتوزيع/إنهاء الرد |
    | `plugin-sdk/reply-history` | مساعدات مشتركة لسجل الردود ضمن نافذة قصيرة مثل `buildHistoryContext`, `recordPendingHistoryEntry`, و `clearHistoryEntriesIfEnabled` |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | مساعدات ضيقة لتقسيم النص/Markdown |
    | `plugin-sdk/session-store-runtime` | مساعدات مسار مخزن الجلسة + updated-at |
    | `plugin-sdk/state-paths` | مساعدات مسارات دليل الحالة/OAuth |
    | `plugin-sdk/routing` | مساعدات ربط المسار/مفتاح الجلسة/الحساب مثل `resolveAgentRoute`, `buildAgentSessionKey`, و `resolveDefaultAgentBoundAccountId` |
    | `plugin-sdk/status-helpers` | مساعدات مشتركة لملخص حالة القناة/الحساب، وافتراضيات حالة وقت التشغيل، ومساعدات بيانات وصفية للمشكلات |
    | `plugin-sdk/target-resolver-runtime` | مساعدات مشتركة لحل الأهداف |
    | `plugin-sdk/string-normalization-runtime` | مساعدات تطبيع slug/string |
    | `plugin-sdk/request-url` | استخراج عناوين URL النصية من مدخلات شبيهة بـ fetch/request |
    | `plugin-sdk/run-command` | مشغّل أوامر موقّت بنتائج stdout/stderr مطبّعة |
    | `plugin-sdk/param-readers` | قارئات شائعة لمعاملات الأداة/CLI |
    | `plugin-sdk/tool-send` | استخراج حقول هدف الإرسال القياسية من وسيطات الأداة |
    | `plugin-sdk/temp-path` | مساعدات مشتركة لمسارات التنزيل المؤقت |
    | `plugin-sdk/logging-core` | مسجّل النظام الفرعي ومساعدات إخفاء البيانات الحساسة |
    | `plugin-sdk/markdown-table-runtime` | مساعدات أوضاع جداول Markdown |
    | `plugin-sdk/json-store` | مساعدات صغيرة لقراءة/كتابة حالة JSON |
    | `plugin-sdk/file-lock` | مساعدات إعادة الدخول لقفل الملفات |
    | `plugin-sdk/persistent-dedupe` | مساعدات ذاكرة التخزين المؤقت لإزالة التكرار المعتمدة على القرص |
    | `plugin-sdk/acp-runtime` | مساعدات ACP لوقت التشغيل/الجلسة وتوزيع الرد |
    | `plugin-sdk/agent-config-primitives` | أوليات ضيقة لمخطط تهيئة وقت تشغيل الوكيل |
    | `plugin-sdk/boolean-param` | قارئ مرن لمعاملات boolean |
    | `plugin-sdk/dangerous-name-runtime` | مساعدات حل مطابقة الأسماء الخطرة |
    | `plugin-sdk/device-bootstrap` | مساعدات الإقلاع الأولي للجهاز ورمز الاقتران |
    | `plugin-sdk/extension-shared` | أوليات مشتركة لمساعدات القنوات السلبية، والحالة، والوكيل المحيط |
    | `plugin-sdk/models-provider-runtime` | مساعدات أمر `/models` وردود المزوّد |
    | `plugin-sdk/skill-commands-runtime` | مساعدات سرد أوامر Skills |
    | `plugin-sdk/native-command-registry` | مساعدات سجل الأوامر الأصلية/بنائه/تسلسله |
    | `plugin-sdk/provider-zai-endpoint` | مساعدات اكتشاف نقاط نهاية Z.AI |
    | `plugin-sdk/infra-runtime` | مساعدات أحداث النظام/النبض |
    | `plugin-sdk/collection-runtime` | مساعدات صغيرة لذاكرة تخزين مؤقتة محدودة |
    | `plugin-sdk/diagnostic-runtime` | مساعدات الأعلام والأحداث التشخيصية |
    | `plugin-sdk/error-runtime` | مساعدات رسم الأخطاء البياني، والتنسيق، وتصنيف الأخطاء المشتركة، و `isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | مساعدات fetch المغلّف والوكيل والبحث المثبّت |
    | `plugin-sdk/host-runtime` | مساعدات تطبيع اسم المضيف ومضيف SCP |
    | `plugin-sdk/retry-runtime` | مساعدات تهيئة إعادة المحاولة ومشغّل إعادة المحاولة |
    | `plugin-sdk/agent-runtime` | مساعدات دليل/هوية/مساحة عمل الوكيل |
    | `plugin-sdk/directory-runtime` | الاستعلام عن الدليل وإزالة التكرار استنادًا إلى التهيئة |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="المسارات الفرعية للقدرات والاختبار">
    | المسار الفرعي | أهم التصديرات |
    | --- | --- |
    | `plugin-sdk/media-runtime` | مساعدات مشتركة لجلب/تحويل/تخزين الوسائط بالإضافة إلى بُناة حمولات الوسائط |
    | `plugin-sdk/media-generation-runtime` | مساعدات مشتركة للفشل المتتابع في توليد الوسائط، واختيار المرشحين، ورسائل النموذج المفقود |
    | `plugin-sdk/media-understanding` | أنواع مزوّد فهم الوسائط بالإضافة إلى تصديرات مساعدات الصور/الصوت للمزوّد |
    | `plugin-sdk/text-runtime` | مساعدات مشتركة للنص/Markdown/التسجيل مثل إزالة النص المرئي للمساعد، ومساعدات العرض/التقسيم/الجداول في Markdown، ومساعدات الإخفاء، ومساعدات وسم التوجيه، وأدوات النص الآمن |
    | `plugin-sdk/text-chunking` | مساعد تقسيم النص الصادر |
    | `plugin-sdk/speech` | أنواع مزوّدات الكلام بالإضافة إلى مساعدات التوجيه والسجل والتحقق الموجّهة للمزوّد |
    | `plugin-sdk/speech-core` | أنواع مزوّدات الكلام المشتركة، والسجل، والتوجيه، ومساعدات التطبيع |
    | `plugin-sdk/realtime-transcription` | أنواع مزوّدات النسخ الفوري ومساعدات السجل |
    | `plugin-sdk/realtime-voice` | أنواع مزوّدات الصوت الفوري ومساعدات السجل |
    | `plugin-sdk/image-generation` | أنواع مزوّدات توليد الصور |
    | `plugin-sdk/image-generation-core` | أنواع توليد الصور المشتركة، ومساعدات الفشل المتتابع، والمصادقة، والسجل |
    | `plugin-sdk/music-generation` | أنواع مزوّد/طلب/نتيجة توليد الموسيقى |
    | `plugin-sdk/music-generation-core` | أنواع توليد الموسيقى المشتركة، ومساعدات الفشل المتتابع، والبحث عن المزوّد، وتحليل model-ref |
    | `plugin-sdk/video-generation` | أنواع مزوّد/طلب/نتيجة توليد الفيديو |
    | `plugin-sdk/video-generation-core` | أنواع توليد الفيديو المشتركة، ومساعدات الفشل المتتابع، والبحث عن المزوّد، وتحليل model-ref |
    | `plugin-sdk/webhook-targets` | سجل أهداف webhook ومساعدات تثبيت المسارات |
    | `plugin-sdk/webhook-path` | مساعدات تطبيع مسار webhook |
    | `plugin-sdk/web-media` | مساعدات مشتركة لتحميل الوسائط البعيدة/المحلية |
    | `plugin-sdk/zod` | إعادة تصدير `zod` لمستهلكي plugin SDK |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="المسارات الفرعية للذاكرة">
    | المسار الفرعي | أهم التصديرات |
    | --- | --- |
    | `plugin-sdk/memory-core` | سطح مساعد memory-core المضمّن لمدير/تهيئة/ملف/مساعدات CLI |
    | `plugin-sdk/memory-core-engine-runtime` | واجهة وقت تشغيل لفهرسة/بحث الذاكرة |
    | `plugin-sdk/memory-core-host-engine-foundation` | تصديرات محرك الأساس لمضيف الذاكرة |
    | `plugin-sdk/memory-core-host-engine-embeddings` | تصديرات محرك embeddings لمضيف الذاكرة |
    | `plugin-sdk/memory-core-host-engine-qmd` | تصديرات محرك QMD لمضيف الذاكرة |
    | `plugin-sdk/memory-core-host-engine-storage` | تصديرات محرك التخزين لمضيف الذاكرة |
    | `plugin-sdk/memory-core-host-multimodal` | مساعدات متعددة الوسائط لمضيف الذاكرة |
    | `plugin-sdk/memory-core-host-query` | مساعدات الاستعلام لمضيف الذاكرة |
    | `plugin-sdk/memory-core-host-secret` | مساعدات الأسرار لمضيف الذاكرة |
    | `plugin-sdk/memory-core-host-events` | مساعدات سجل أحداث مضيف الذاكرة |
    | `plugin-sdk/memory-core-host-status` | مساعدات حالة مضيف الذاكرة |
    | `plugin-sdk/memory-core-host-runtime-cli` | مساعدات وقت تشغيل CLI لمضيف الذاكرة |
    | `plugin-sdk/memory-core-host-runtime-core` | مساعدات وقت التشغيل الأساسية لمضيف الذاكرة |
    | `plugin-sdk/memory-core-host-runtime-files` | مساعدات الملفات/وقت التشغيل لمضيف الذاكرة |
    | `plugin-sdk/memory-host-core` | اسم بديل محايد تجاه المورّد لمساعدات وقت تشغيل نواة مضيف الذاكرة |
    | `plugin-sdk/memory-host-events` | اسم بديل محايد تجاه المورّد لمساعدات سجل أحداث مضيف الذاكرة |
    | `plugin-sdk/memory-host-files` | اسم بديل محايد تجاه المورّد لمساعدات ملفات/وقت تشغيل مضيف الذاكرة |
    | `plugin-sdk/memory-host-markdown` | مساعدات مشتركة لـ managed-markdown لـ plugins المجاورة للذاكرة |
    | `plugin-sdk/memory-host-search` | واجهة وقت تشغيل الذاكرة النشطة للوصول إلى search-manager |
    | `plugin-sdk/memory-host-status` | اسم بديل محايد تجاه المورّد لمساعدات حالة مضيف الذاكرة |
    | `plugin-sdk/memory-lancedb` | سطح مساعد memory-lancedb المضمّن |
  </Accordion>

  <Accordion title="المسارات الفرعية المحجوزة للمساعدات المضمّنة">
    | العائلة | المسارات الفرعية الحالية | الاستخدام المقصود |
    | --- | --- | --- |
    | Browser | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | مساعدات دعم bundled browser plugin (`browser-support` يبقى واجهة التوافق) |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | سطح المساعدة/وقت التشغيل الخاص بـ bundled Matrix |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | سطح المساعدة/وقت التشغيل الخاص بـ bundled LINE |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | سطح المساعدة الخاص بـ bundled IRC |
    | مساعدات خاصة بالقنوات | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | واجهات المساعدة/التوافق الخاصة بالقنوات المضمّنة |
    | مساعدات خاصة بالمصادقة/الplugin | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | واجهات مساعدة خاصة بالميزات/الplugins المضمّنة؛ يصدّر `plugin-sdk/github-copilot-token` حاليًا `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken`, و `resolveCopilotApiToken` |
  </Accordion>
</AccordionGroup>

## واجهة برمجة تطبيقات التسجيل

يتلقى رد النداء `register(api)` كائن `OpenClawPluginApi` بهذه
الأساليب:

### تسجيل القدرات

| الأسلوب                                           | ما الذي يسجله                |
| ------------------------------------------------ | -------------------------------- |
| `api.registerProvider(...)`                      | الاستدلال النصي (LLM)             |
| `api.registerCliBackend(...)`                    | خلفية استدلال CLI محلية      |
| `api.registerChannel(...)`                       | قناة مراسلة                |
| `api.registerSpeechProvider(...)`                | تحويل النص إلى كلام / توليف STT   |
| `api.registerRealtimeTranscriptionProvider(...)` | نسخ فوري متدفق |
| `api.registerRealtimeVoiceProvider(...)`         | جلسات صوت فوري ثنائية الاتجاه   |
| `api.registerMediaUnderstandingProvider(...)`    | تحليل الصور/الصوت/الفيديو       |
| `api.registerImageGenerationProvider(...)`       | توليد الصور                 |
| `api.registerMusicGenerationProvider(...)`       | توليد الموسيقى                 |
| `api.registerVideoGenerationProvider(...)`       | توليد الفيديو                 |
| `api.registerWebFetchProvider(...)`              | مزوّد جلب / scraping للويب      |
| `api.registerWebSearchProvider(...)`             | بحث الويب                       |

### الأدوات والأوامر

| الأسلوب                          | ما الذي يسجله                             |
| ------------------------------- | --------------------------------------------- |
| `api.registerTool(tool, opts?)` | أداة وكيل (إلزامية أو `{ optional: true }`) |
| `api.registerCommand(def)`      | أمر مخصص (يتجاوز LLM)             |

### البنية التحتية

| الأسلوب                                         | ما الذي يسجله                       |
| ---------------------------------------------- | --------------------------------------- |
| `api.registerHook(events, handler, opts?)`     | خطاف حدث                              |
| `api.registerHttpRoute(params)`                | نقطة نهاية HTTP للبوابة                   |
| `api.registerGatewayMethod(name, handler)`     | أسلوب RPC للبوابة                      |
| `api.registerCli(registrar, opts?)`            | أمر فرعي في CLI                          |
| `api.registerService(service)`                 | خدمة في الخلفية                      |
| `api.registerInteractiveHandler(registration)` | معالِج تفاعلي                     |
| `api.registerMemoryPromptSupplement(builder)`  | قسم إضافي للمطالبة مجاور للذاكرة |
| `api.registerMemoryCorpusSupplement(adapter)`  | corpus إضافي لبحث/قراءة الذاكرة      |

تظل مساحات أسماء إدارة النواة المحجوزة (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`) دائمًا `operator.admin`، حتى إذا حاول plugin تعيين
نطاق أضيق لأسلوب البوابة. فضّل البوادئ الخاصة بالplugin
للأساليب المملوكة للplugin.

### بيانات تعريف تسجيل CLI

يقبل `api.registerCli(registrar, opts?)` نوعين من البيانات التعريفية على المستوى الأعلى:

- `commands`: جذور أوامر صريحة يملكها المُسجِّل
- `descriptors`: واصفات أوامر في وقت التحليل تُستخدم لمساعدة CLI الجذري،
  والتوجيه، وتسجيل CLI الكسول للplugins

إذا أردت أن يبقى أمر plugin محمّلًا كسولًا في مسار CLI الجذري العادي،
فقدّم `descriptors` تغطي كل جذر أمر على المستوى الأعلى يكشفه ذلك
المُسجِّل.

```typescript
api.registerCli(
  async ({ program }) => {
    const { registerMatrixCli } = await import("./src/cli.js");
    registerMatrixCli({ program });
  },
  {
    descriptors: [
      {
        name: "matrix",
        description: "إدارة حسابات Matrix والتحقق والأجهزة وحالة الملف الشخصي",
        hasSubcommands: true,
      },
    ],
  },
);
```

استخدم `commands` وحده فقط عندما لا تحتاج إلى تسجيل CLI جذري كسول.
لا يزال مسار التوافق المتحمّس هذا مدعومًا، لكنه لا يثبت
عناصر نائبة مدعومة بـ descriptor للتحميل الكسول في وقت التحليل.

### تسجيل CLI backend

يتيح `api.registerCliBackend(...)` لـ plugin امتلاك التهيئة الافتراضية لـ
خلفية CLI محلية للذكاء الاصطناعي مثل `codex-cli`.

- يصبح `id` الخاص بالخلفية هو بادئة المزوّد في مراجع النماذج مثل `codex-cli/gpt-5`.
- يستخدم `config` الخاص بالخلفية نفس البنية مثل `agents.defaults.cliBackends.<id>`.
- تهيئة المستخدم تبقى هي الغالبة. يدمج OpenClaw `agents.defaults.cliBackends.<id>` فوق
  افتراضي plugin قبل تشغيل CLI.
- استخدم `normalizeConfig` عندما تحتاج الخلفية إلى إعادة كتابة توافقية بعد الدمج
  (على سبيل المثال، تطبيع أشكال العلامات القديمة).

### الفتحات الحصرية

| الأسلوب                                     | ما الذي يسجله                                                                                                                                         |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `api.registerContextEngine(id, factory)`   | محرك السياق (واحد فقط نشط في كل مرة). يتلقى رد النداء `assemble()` كلًا من `availableTools` و `citationsMode` حتى يتمكن المحرك من تخصيص إضافات المطالبة. |
| `api.registerMemoryCapability(capability)` | قدرة ذاكرة موحدة                                                                                                                                 |
| `api.registerMemoryPromptSection(builder)` | باني قسم مطالبة الذاكرة                                                                                                                             |
| `api.registerMemoryFlushPlan(resolver)`    | محلّل خطة تفريغ الذاكرة                                                                                                                                |
| `api.registerMemoryRuntime(runtime)`       | محوّل وقت تشغيل الذاكرة                                                                                                                                    |

### محوّلات تضمين الذاكرة

| الأسلوب                                         | ما الذي يسجله                              |
| ---------------------------------------------- | ---------------------------------------------- |
| `api.registerMemoryEmbeddingProvider(adapter)` | محوّل تضمين الذاكرة للplugin النشط |

- يُعد `registerMemoryCapability` واجهة API الحصرية المفضلة لـ memory-plugin.
- قد يكشف `registerMemoryCapability` أيضًا `publicArtifacts.listArtifacts(...)`
  حتى تتمكن plugins المصاحبة من استهلاك العناصر المصدّرة الخاصة بالذاكرة عبر
  `openclaw/plugin-sdk/memory-host-core` بدلًا من الوصول إلى التخطيط الخاص
  لplugin ذاكرة محدد.
- تمثّل `registerMemoryPromptSection`, `registerMemoryFlushPlan`, و
  `registerMemoryRuntime` واجهات API حصرية متوافقة مع الإصدارات القديمة لـ memory-plugin.
- يتيح `registerMemoryEmbeddingProvider` لـ plugin الذاكرة النشط تسجيل
  معرّف محوّل تضمين واحد أو أكثر (على سبيل المثال `openai`, `gemini`، أو معرّف مخصص يعرّفه plugin).
- تُحل تهيئة المستخدم مثل `agents.defaults.memorySearch.provider` و
  `agents.defaults.memorySearch.fallback` بالرجوع إلى معرّفات
  المحوّلات المسجّلة هذه.

### الأحداث ودورة الحياة

| الأسلوب                                       | ما الذي يفعله                  |
| -------------------------------------------- | ----------------------------- |
| `api.on(hookName, handler, opts?)`           | خطاف دورة حياة مطبّع          |
| `api.onConversationBindingResolved(handler)` | رد نداء ربط المحادثة |

### دلالات قرار الخطاف

- `before_tool_call`: تكون إعادة `{ block: true }` نهائية. وبمجرد أن يضبطها أي معالِج، يتم تخطي المعالجات ذات الأولوية الأدنى.
- `before_tool_call`: تُعامل إعادة `{ block: false }` على أنها بلا قرار (مثل حذف `block`) وليست تجاوزًا.
- `before_install`: تكون إعادة `{ block: true }` نهائية. وبمجرد أن يضبطها أي معالِج، يتم تخطي المعالجات ذات الأولوية الأدنى.
- `before_install`: تُعامل إعادة `{ block: false }` على أنها بلا قرار (مثل حذف `block`) وليست تجاوزًا.
- `reply_dispatch`: تكون إعادة `{ handled: true, ... }` نهائية. وبمجرد أن يطالب أي معالِج بالتوزيع، يتم تخطي المعالجات ذات الأولوية الأدنى ومسار توزيع النموذج الافتراضي.
- `message_sending`: تكون إعادة `{ cancel: true }` نهائية. وبمجرد أن يضبطها أي معالِج، يتم تخطي المعالجات ذات الأولوية الأدنى.
- `message_sending`: تُعامل إعادة `{ cancel: false }` على أنها بلا قرار (مثل حذف `cancel`) وليست تجاوزًا.

### حقول كائن API

| الحقل                    | النوع                      | الوصف                                                                                 |
| ------------------------ | ------------------------- | ------------------------------------------------------------------------------------------- |
| `api.id`                 | `string`                  | معرّف plugin                                                                                   |
| `api.name`               | `string`                  | اسم العرض                                                                                |
| `api.version`            | `string?`                 | إصدار plugin (اختياري)                                                                   |
| `api.description`        | `string?`                 | وصف plugin (اختياري)                                                               |
| `api.source`             | `string`                  | مسار مصدر plugin                                                                          |
| `api.rootDir`            | `string?`                 | الدليل الجذري لـ plugin (اختياري)                                                            |
| `api.config`             | `OpenClawConfig`          | لقطة التهيئة الحالية (لقطة وقت التشغيل النشطة داخل الذاكرة عند توفرها)                  |
| `api.pluginConfig`       | `Record<string, unknown>` | تهيئة plugin الخاصة من `plugins.entries.<id>.config`                                   |
| `api.runtime`            | `PluginRuntime`           | [مساعدات وقت التشغيل](/ar/plugins/sdk-runtime)                                                     |
| `api.logger`             | `PluginLogger`            | مسجّل ضمن النطاق (`debug`, `info`, `warn`, `error`)                                            |
| `api.registrationMode`   | `PluginRegistrationMode`  | وضع التحميل الحالي؛ `"setup-runtime"` هي نافذة بدء التشغيل/الإعداد الخفيفة قبل الإدخال الكامل |
| `api.resolvePath(input)` | `(string) => string`      | حل المسار نسبةً إلى جذر plugin                                                        |

## اصطلاح الوحدات الداخلية

داخل plugin الخاص بك، استخدم ملفات barrel محلية للاستيرادات الداخلية:

```
my-plugin/
  api.ts            # التصديرات العامة للمستهلكين الخارجيين
  runtime-api.ts    # تصديرات وقت تشغيل داخلية فقط
  index.ts          # نقطة إدخال plugin
  setup-entry.ts    # إدخال إعداد خفيف فقط (اختياري)
```

<Warning>
  لا تستورد plugin الخاص بك أبدًا عبر `openclaw/plugin-sdk/<your-plugin>`
  من كود الإنتاج. وجّه الاستيرادات الداخلية عبر `./api.ts` أو
  `./runtime-api.ts`. مسار SDK هو العقد الخارجي فقط.
</Warning>

تفضّل الآن الأسطح العامة لـ bundled plugin المحمّلة عبر الواجهة (`api.ts`, `runtime-api.ts`,
`index.ts`, `setup-entry.ts`، وملفات الإدخال العامة المشابهة)
لقطة تهيئة وقت التشغيل النشطة عندما يكون OpenClaw قيد التشغيل بالفعل. وإذا لم تكن لقطة
وقت التشغيل موجودة بعد، فإنها تعود إلى ملف التهيئة المحلول على القرص.

يمكن لـ provider plugins أيضًا كشف barrel محلي ضيق لعقد plugin عندما تكون
المساعدة مخصصة عمدًا لمزوّد بعينه ولا تنتمي بعد إلى مسار فرعي عام في SDK.
المثال المضمّن الحالي: يحتفظ مزوّد Anthropic بمساعدات تدفق Claude
في واجهته العامة `api.ts` / `contract-api.ts` الخاصة به بدلًا من
ترقية منطق رؤوس Anthropic التجريبية و `service_tier` إلى عقد
عام في `plugin-sdk/*`.

أمثلة مضمّنة حالية أخرى:

- `@openclaw/openai-provider`: يصدّر `api.ts` بُناة المزوّد،
  ومساعدات النموذج الافتراضي، وبُناة المزوّد الفوري
- `@openclaw/openrouter-provider`: يصدّر `api.ts` باني المزوّد بالإضافة إلى
  مساعدات الإعداد الأولي/التهيئة

<Warning>
  يجب على كود الإنتاج الخاص بالامتدادات أيضًا تجنب الاستيراد من `openclaw/plugin-sdk/<other-plugin>`.
  إذا كانت إحدى المساعدات مشتركة فعلًا، فقم بترقيتها إلى مسار فرعي محايد في SDK
  مثل `openclaw/plugin-sdk/speech`, `.../provider-model-shared`، أو سطح آخر
  موجّه للقدرات بدلًا من ربط pluginين معًا.
</Warning>

## ذو صلة

- [نقاط الإدخال](/ar/plugins/sdk-entrypoints) — خيارات `definePluginEntry` و `defineChannelPluginEntry`
- [مساعدات وقت التشغيل](/ar/plugins/sdk-runtime) — المرجع الكامل لمساحة الاسم `api.runtime`
- [الإعداد والتهيئة](/ar/plugins/sdk-setup) — الحزم، وملفات manifest، ومخططات التهيئة
- [الاختبار](/ar/plugins/sdk-testing) — أدوات الاختبار وقواعد lint
- [ترحيل SDK](/ar/plugins/sdk-migration) — الترحيل من الأسطح المهجورة
- [بنية plugin الداخلية](/ar/plugins/architecture) — البنية العميقة ونموذج القدرات
