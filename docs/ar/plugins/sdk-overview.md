---
read_when:
    - تحتاج إلى معرفة أي مسار فرعي من SDK يجب الاستيراد منه
    - تريد مرجعًا لجميع أساليب التسجيل في OpenClawPluginApi
    - أنت تبحث عن تصدير محدد من SDK
sidebarTitle: SDK Overview
summary: مرجع خريطة الاستيراد وواجهة برمجة التسجيل وبنية SDK
title: نظرة عامة على Plugin SDK
x-i18n:
    generated_at: "2026-04-09T01:31:17Z"
    model: gpt-5.4
    provider: openai
    source_hash: bf205af060971931df97dca4af5110ce173d2b7c12f56ad7c62d664a402f2381
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# نظرة عامة على Plugin SDK

يمثل Plugin SDK العقد المطبوع بين الإضافات والنواة. وهذه الصفحة هي
المرجع الخاص بـ **ما يجب استيراده** و**ما يمكنك تسجيله**.

<Tip>
  **هل تبحث عن دليل إرشادي؟**
  - أول إضافة؟ ابدأ من [البدء](/ar/plugins/building-plugins)
  - إضافة قناة؟ راجع [إضافات القنوات](/ar/plugins/sdk-channel-plugins)
  - إضافة مزود؟ راجع [إضافات المزوّدين](/ar/plugins/sdk-provider-plugins)
</Tip>

## اصطلاح الاستيراد

استورد دائمًا من مسار فرعي محدد:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

كل مسار فرعي هو وحدة صغيرة ومكتفية ذاتيًا. وهذا يحافظ على سرعة بدء التشغيل
ويمنع مشكلات التبعيات الدائرية. وبالنسبة إلى وسائل إدخال/بناء القنوات الخاصة،
ففضّل `openclaw/plugin-sdk/channel-core`؛ واحتفظ بـ `openclaw/plugin-sdk/core`
للسطح الأشمل والمساعدات المشتركة مثل
`buildChannelConfigSchema`.

لا تضف أو تعتمد على أسطح مريحة مسماة باسم مزود مثل
`openclaw/plugin-sdk/slack` أو `openclaw/plugin-sdk/discord` أو
`openclaw/plugin-sdk/signal` أو `openclaw/plugin-sdk/whatsapp` أو
أسطح المساعدة المعنونة باسم القناة. يجب أن تركّب الإضافات المضمّنة
المسارات الفرعية العامة لـ SDK داخل ملفات `api.ts` أو `runtime-api.ts`
الخاصة بها، ويجب على النواة إما استخدام هذه الملفات المحلية للإضافة أو إضافة عقد
عام ضيق من SDK عندما تكون الحاجة فعلًا عابرة للقنوات.

لا تزال خريطة التصدير المولدة تحتوي على مجموعة صغيرة من
أسطح مساعدة الإضافات المضمّنة مثل `plugin-sdk/feishu` و`plugin-sdk/feishu-setup`
و`plugin-sdk/zalo` و`plugin-sdk/zalo-setup` و`plugin-sdk/matrix*`. هذه
المسارات الفرعية موجودة فقط لصيانة الإضافات المضمّنة والتوافق؛ وقد تم حذفها عمدًا من
الجدول الشائع أدناه وليست مسار الاستيراد الموصى به للإضافات الجديدة من جهات خارجية.

## مرجع المسارات الفرعية

أكثر المسارات الفرعية استخدامًا، مجمعة حسب الغرض. القائمة الكاملة المولدة والتي تضم
أكثر من 200 مسار فرعي موجودة في `scripts/lib/plugin-sdk-entrypoints.json`.

لا تزال المسارات الفرعية المساعدة المحجوزة للإضافات المضمّنة تظهر في تلك القائمة المولدة.
تعامل معها كتفاصيل تنفيذ/أسطح توافق ما لم تروج صفحة توثيق
صراحة لأحدها كسطح عام.

### إدخال الإضافة

| المسار الفرعي                | أهم التصديرات                                                                                                                        |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/plugin-entry`    | `definePluginEntry`                                                                                                                   |
| `plugin-sdk/core`            | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema`   | `OpenClawSchema`                                                                                                                      |
| `plugin-sdk/provider-entry`  | `defineSingleProviderPluginEntry`                                                                                                     |

<AccordionGroup>
  <Accordion title="المسارات الفرعية للقنوات">
    | المسار الفرعي | أهم التصديرات |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | تصدير مخطط Zod الجذري لـ `openclaw.json` (`OpenClawSchema`) |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`، بالإضافة إلى `DEFAULT_ACCOUNT_ID` و`createTopLevelChannelDmPolicy` و`setSetupChannelEnabled` و`splitSetupEntries` |
    | `plugin-sdk/setup` | مساعدات مشتركة لمعالج الإعداد، ورسائل allowlist، وبناة حالة الإعداد |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | مساعدات إعدادات/بوابة إجراء متعددة الحسابات، ومساعدات الرجوع إلى الحساب الافتراضي |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`، ومساعدات تطبيع معرّف الحساب |
    | `plugin-sdk/account-resolution` | مساعدات البحث عن الحساب + الرجوع الافتراضي |
    | `plugin-sdk/account-helpers` | مساعدات ضيقة لقائمة الحسابات/إجراءات الحساب |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | أنواع مخطط إعدادات القناة |
    | `plugin-sdk/telegram-command-config` | مساعدات تطبيع/تحقق الأوامر المخصصة في Telegram مع الرجوع إلى العقد المضمّن |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | مساعدات مشتركة لبناء route + envelope الوارد |
    | `plugin-sdk/inbound-reply-dispatch` | مساعدات مشتركة لتسجيل الرسائل الواردة وتوزيعها |
    | `plugin-sdk/messaging-targets` | مساعدات تحليل/مطابقة الأهداف |
    | `plugin-sdk/outbound-media` | مساعدات مشتركة لتحميل الوسائط الصادرة |
    | `plugin-sdk/outbound-runtime` | مساعدات هوية الإرسال الصادر/مفوّض الإرسال |
    | `plugin-sdk/thread-bindings-runtime` | مساعدات دورة حياة ربط الخيوط والمهايئات |
    | `plugin-sdk/agent-media-payload` | باني حمولة وسائط الوكيل القديم |
    | `plugin-sdk/conversation-runtime` | مساعدات ربط المحادثة/الخيط، والاقتران، والربط المُعد |
    | `plugin-sdk/runtime-config-snapshot` | مساعد لقطة إعدادات وقت التشغيل |
    | `plugin-sdk/runtime-group-policy` | مساعدات حل سياسة المجموعات في وقت التشغيل |
    | `plugin-sdk/channel-status` | مساعدات مشتركة للقطات/ملخصات حالة القناة |
    | `plugin-sdk/channel-config-primitives` | بدائيات ضيقة لمخطط إعدادات القناة |
    | `plugin-sdk/channel-config-writes` | مساعدات تفويض كتابة إعدادات القناة |
    | `plugin-sdk/channel-plugin-common` | تصديرات تمهيدية مشتركة لإضافات القنوات |
    | `plugin-sdk/allowlist-config-edit` | مساعدات قراءة/تعديل إعدادات allowlist |
    | `plugin-sdk/group-access` | مساعدات مشتركة لاتخاذ قرارات وصول المجموعة |
    | `plugin-sdk/direct-dm` | مساعدات مشتركة للمصادقة/الحماية في direct-DM |
    | `plugin-sdk/interactive-runtime` | مساعدات تطبيع/اختزال حمولة الردود التفاعلية |
    | `plugin-sdk/channel-inbound` | مساعدات إزالة اهتزاز الوارد، ومطابقة الإشارات، وسياسة الإشارة، وenvelope |
    | `plugin-sdk/channel-send-result` | أنواع نتائج الرد |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | مساعدات تحليل/مطابقة الأهداف |
    | `plugin-sdk/channel-contract` | أنواع عقد القناة |
    | `plugin-sdk/channel-feedback` | توصيل الملاحظات/التفاعلات |
    | `plugin-sdk/channel-secret-runtime` | مساعدات ضيقة لعقد الأسرار مثل `collectSimpleChannelFieldAssignments` و`getChannelSurface` و`pushAssignment` وأنواع هدف السر |
  </Accordion>

  <Accordion title="المسارات الفرعية للمزوّدين">
    | المسار الفرعي | أهم التصديرات |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | مساعدات إعداد منسقة للمزوّدات المحلية/المستضافة ذاتيًا |
    | `plugin-sdk/self-hosted-provider-setup` | مساعدات إعداد مركزة للمزوّدات المستضافة ذاتيًا المتوافقة مع OpenAI |
    | `plugin-sdk/cli-backend` | القيم الافتراضية للواجهة الخلفية CLI + ثوابت المراقبة |
    | `plugin-sdk/provider-auth-runtime` | مساعدات وقت التشغيل لحل مفاتيح API لإضافات المزوّدين |
    | `plugin-sdk/provider-auth-api-key` | مساعدات إعداد أولي/كتابة ملف التعريف لمفتاح API مثل `upsertApiKeyProfile` |
    | `plugin-sdk/provider-auth-result` | باني نتيجة OAuth القياسي |
    | `plugin-sdk/provider-auth-login` | مساعدات تسجيل دخول تفاعلية مشتركة لإضافات المزوّدين |
    | `plugin-sdk/provider-env-vars` | مساعدات البحث عن متغيرات البيئة لمصادقة المزوّد |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile`, `upsertApiKeyProfile`, `writeOAuthCredentials` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`، وبناة سياسة الإعادة المشتركون، ومساعدات نقاط نهاية المزوّد، ومساعدات تطبيع معرّف النموذج مثل `normalizeNativeXaiModelId` |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | مساعدات عامة لقدرات HTTP/نقاط النهاية للمزوّد |
    | `plugin-sdk/provider-web-fetch-contract` | مساعدات ضيقة لعقد إعداد/اختيار web-fetch مثل `enablePluginInConfig` و`WebFetchProviderPlugin` |
    | `plugin-sdk/provider-web-fetch` | مساعدات تسجيل/تخزين مؤقت لمزوّد web-fetch |
    | `plugin-sdk/provider-web-search-config-contract` | مساعدات ضيقة لإعداد/اعتماديات web-search للمزوّدات التي لا تحتاج إلى توصيل تمكين الإضافة |
    | `plugin-sdk/provider-web-search-contract` | مساعدات ضيقة لعقد إعداد/اعتماديات web-search مثل `createWebSearchProviderContractFields` و`enablePluginInConfig` و`resolveProviderWebSearchPluginConfig` وواضعات/جالبات الاعتماديات ذات النطاق |
    | `plugin-sdk/provider-web-search` | مساعدات تسجيل/تخزين مؤقت/وقت تشغيل لمزوّد web-search |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`، وتنظيف مخطط Gemini + التشخيصات، ومساعدات توافق xAI مثل `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` وما شابه |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`، وأنواع مغلفات التدفق، ومساعدات مغلفات مشتركة لـ Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
    | `plugin-sdk/provider-onboard` | مساعدات ترقيع إعدادات الإعداد الأولي |
    | `plugin-sdk/global-singleton` | مساعدات singleton/map/cache محلية على مستوى العملية |
  </Accordion>

  <Accordion title="المسارات الفرعية للمصادقة والأمان">
    | المسار الفرعي | أهم التصديرات |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`، ومساعدات سجل الأوامر، ومساعدات تفويض المُرسل |
    | `plugin-sdk/command-status` | بناة رسائل الأوامر/المساعدة مثل `buildCommandsMessagePaginated` و`buildHelpMessage` |
    | `plugin-sdk/approval-auth-runtime` | مساعدات حل الموافقين ومصادقة الإجراءات داخل المحادثة نفسها |
    | `plugin-sdk/approval-client-runtime` | مساعدات ملفات التعريف/المرشحات الخاصة بالموافقات الأصلية لـ exec |
    | `plugin-sdk/approval-delivery-runtime` | مهايئات قدرات/تسليم الموافقات الأصلية |
    | `plugin-sdk/approval-gateway-runtime` | مساعد حل Gateway المشترك للموافقات |
    | `plugin-sdk/approval-handler-adapter-runtime` | مساعدات خفيفة لتحميل مهايئات الموافقة الأصلية لنقاط دخول القنوات الساخنة |
    | `plugin-sdk/approval-handler-runtime` | مساعدات أوسع لوقت تشغيل معالج الموافقات؛ فضّل الأسطح الأضيق للمهايئ/البوابة عندما تكون كافية |
    | `plugin-sdk/approval-native-runtime` | مساعدات أهداف الموافقة الأصلية + ربط الحساب |
    | `plugin-sdk/approval-reply-runtime` | مساعدات حمولة الرد لموافقات exec/plugin |
    | `plugin-sdk/command-auth-native` | مصادقة الأوامر الأصلية + مساعدات هدف الجلسة الأصلية |
    | `plugin-sdk/command-detection` | مساعدات مشتركة لاكتشاف الأوامر |
    | `plugin-sdk/command-surface` | مساعدات تطبيع جسم الأمر وسطح الأمر |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/channel-secret-runtime` | مساعدات ضيقة لتجميع العقود السرية لأسطح أسرار القنوات/الإضافات |
    | `plugin-sdk/secret-ref-runtime` | مساعدات ضيقة لـ `coerceSecretRef` وأنواع SecretRef لتحليل عقد السر/الإعدادات |
    | `plugin-sdk/security-runtime` | مساعدات مشتركة للثقة، وحظر الرسائل المباشرة، والمحتوى الخارجي، وتجميع الأسرار |
    | `plugin-sdk/ssrf-policy` | مساعدات سياسة SSRF لقائمة سماح المضيف والشبكة الخاصة |
    | `plugin-sdk/ssrf-runtime` | مساعدات pinned-dispatcher، وfetch المحمي بـ SSRF، وسياسة SSRF |
    | `plugin-sdk/secret-input` | مساعدات تحليل إدخال السر |
    | `plugin-sdk/webhook-ingress` | مساعدات طلب/هدف webhook |
    | `plugin-sdk/webhook-request-guards` | مساعدات حجم/مهلة جسم الطلب |
  </Accordion>

  <Accordion title="المسارات الفرعية لوقت التشغيل والتخزين">
    | المسار الفرعي | أهم التصديرات |
    | --- | --- |
    | `plugin-sdk/runtime` | مساعدات واسعة لوقت التشغيل/التسجيل/النسخ الاحتياطي/تثبيت الإضافات |
    | `plugin-sdk/runtime-env` | مساعدات ضيقة لبيئة وقت التشغيل، والمسجّل، والمهلة، وإعادة المحاولة، والتراجع |
    | `plugin-sdk/channel-runtime-context` | مساعدات عامة لتسجيل سياق وقت تشغيل القناة والبحث عنه |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | مساعدات مشتركة للأوامر/الخطافات/HTTP/التفاعل الخاصة بالإضافةات |
    | `plugin-sdk/hook-runtime` | مساعدات مشتركة لخط أنابيب webhook/الخطافات الداخلية |
    | `plugin-sdk/lazy-runtime` | مساعدات استيراد/ربط وقت التشغيل الكسول مثل `createLazyRuntimeModule` و`createLazyRuntimeMethod` و`createLazyRuntimeSurface` |
    | `plugin-sdk/process-runtime` | مساعدات تنفيذ العملية |
    | `plugin-sdk/cli-runtime` | مساعدات تنسيق CLI والانتظار والإصدار |
    | `plugin-sdk/gateway-runtime` | عميل Gateway ومساعدات ترقيع حالة القناة |
    | `plugin-sdk/config-runtime` | مساعدات تحميل/كتابة الإعدادات |
    | `plugin-sdk/telegram-command-config` | مساعدات تطبيع اسم/وصف أوامر Telegram وفحوصات التكرار/التعارض، حتى عندما لا يكون سطح عقد Telegram المضمّن متاحًا |
    | `plugin-sdk/approval-runtime` | مساعدات موافقات exec/plugin، وبناة قدرات الموافقة، ومساعدات المصادقة/ملف التعريف، ومساعدات التوجيه/وقت التشغيل الأصلية |
    | `plugin-sdk/reply-runtime` | مساعدات مشتركة لوقت تشغيل الوارد/الرد، والتقطيع، والتوزيع، والنبضات، ومخطط الرد |
    | `plugin-sdk/reply-dispatch-runtime` | مساعدات ضيقة لتوزيع/إنهاء الرد |
    | `plugin-sdk/reply-history` | مساعدات مشتركة لسجل الردود ذي النافذة القصيرة مثل `buildHistoryContext` و`recordPendingHistoryEntry` و`clearHistoryEntriesIfEnabled` |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | مساعدات ضيقة لتقطيع النص/Markdown |
    | `plugin-sdk/session-store-runtime` | مساعدات مسار مخزن الجلسة + updated-at |
    | `plugin-sdk/state-paths` | مساعدات مسارات حالة/OAuth dir |
    | `plugin-sdk/routing` | مساعدات route/session-key/account binding مثل `resolveAgentRoute` و`buildAgentSessionKey` و`resolveDefaultAgentBoundAccountId` |
    | `plugin-sdk/status-helpers` | مساعدات مشتركة لملخصات حالة القناة/الحساب، وافتراضيات حالة وقت التشغيل، ومساعدات بيانات المشكلات الوصفية |
    | `plugin-sdk/target-resolver-runtime` | مساعدات مشتركة لحل الأهداف |
    | `plugin-sdk/string-normalization-runtime` | مساعدات تطبيع slug/string |
    | `plugin-sdk/request-url` | استخراج عناوين URL النصية من مدخلات شبيهة fetch/request |
    | `plugin-sdk/run-command` | مشغل أوامر مؤقت مع نتائج stdout/stderr مطبّعة |
    | `plugin-sdk/param-readers` | قارئات معلمات مشتركة للأدوات/CLI |
    | `plugin-sdk/tool-payload` | استخراج حمولات مطبعة من كائنات نتائج الأدوات |
    | `plugin-sdk/tool-send` | استخراج حقول هدف الإرسال الأساسية من وسائط الأدوات |
    | `plugin-sdk/temp-path` | مساعدات مشتركة لمسارات التنزيل المؤقت |
    | `plugin-sdk/logging-core` | مسجّل النظام الفرعي ومساعدات تنقيح البيانات |
    | `plugin-sdk/markdown-table-runtime` | مساعدات أوضاع جداول Markdown |
    | `plugin-sdk/json-store` | مساعدات صغيرة لقراءة/كتابة حالة JSON |
    | `plugin-sdk/file-lock` | مساعدات قفل الملفات القابلة لإعادة الدخول |
    | `plugin-sdk/persistent-dedupe` | مساعدات cache لإزالة التكرار مدعومة بالقرص |
    | `plugin-sdk/acp-runtime` | مساعدات ACP لوقت التشغيل/الجلسة وتوزيع الرد |
    | `plugin-sdk/agent-config-primitives` | بدائيات ضيقة لمخطط إعدادات وقت تشغيل الوكيل |
    | `plugin-sdk/boolean-param` | قارئ مرن لمعلمة منطقية |
    | `plugin-sdk/dangerous-name-runtime` | مساعدات حل مطابقة الأسماء الخطرة |
    | `plugin-sdk/device-bootstrap` | مساعدات bootstrap للجهاز ورمز الاقتران |
    | `plugin-sdk/extension-shared` | بدائيات مساعدة مشتركة للقنوات السلبية، والحالة، والوكيل المحيطي |
    | `plugin-sdk/models-provider-runtime` | مساعدات رد أمر `/models`/المزوّد |
    | `plugin-sdk/skill-commands-runtime` | مساعدات سرد أوامر Skills |
    | `plugin-sdk/native-command-registry` | مساعدات السجل/البناء/التسلسل للأوامر الأصلية |
    | `plugin-sdk/provider-zai-endpoint` | مساعدات اكتشاف نقاط نهاية Z.AI |
    | `plugin-sdk/infra-runtime` | مساعدات أحداث النظام/النبضات |
    | `plugin-sdk/collection-runtime` | مساعدات صغيرة لـ cache محدود |
    | `plugin-sdk/diagnostic-runtime` | مساعدات الأعلام التشخيصية والأحداث |
    | `plugin-sdk/error-runtime` | الرسم البياني للأخطاء، والتنسيق، ومساعدات تصنيف الأخطاء المشتركة، و`isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | مساعدات fetch المغلف، والوكيل، والبحث المثبت |
    | `plugin-sdk/host-runtime` | مساعدات تطبيع اسم المضيف وSCP host |
    | `plugin-sdk/retry-runtime` | مساعدات إعداد وإجراء إعادة المحاولة |
    | `plugin-sdk/agent-runtime` | مساعدات دليل/هوية/مساحة عمل الوكيل |
    | `plugin-sdk/directory-runtime` | استعلام/إزالة تكرار الأدلة المدعومة بالإعدادات |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="المسارات الفرعية للإمكانات والاختبار">
    | المسار الفرعي | أهم التصديرات |
    | --- | --- |
    | `plugin-sdk/media-runtime` | مساعدات مشتركة لجلب/تحويل/تخزين الوسائط بالإضافة إلى بناة حمولات الوسائط |
    | `plugin-sdk/media-generation-runtime` | مساعدات مشتركة للفشل البديل في توليد الوسائط، واختيار المرشحين، ورسائل النموذج المفقود |
    | `plugin-sdk/media-understanding` | أنواع مزوّد media understanding بالإضافة إلى تصديرات مساعدة للمزوّد موجهة للصور/الصوت |
    | `plugin-sdk/text-runtime` | مساعدات مشتركة للنص/Markdown/التسجيل مثل إزالة النص المرئي للمساعد، ومساعدات العرض/التقطيع/الجداول لـ Markdown، ومساعدات التنقيح، ومساعدات directive-tag، وأدوات النص الآمن |
    | `plugin-sdk/text-chunking` | مساعد تقطيع النص الصادر |
    | `plugin-sdk/speech` | أنواع مزوّد speech بالإضافة إلى مساعدات موجهات/سجل/تحقق موجّهة للمزوّد |
    | `plugin-sdk/speech-core` | أنواع مشتركة لمزوّد speech، والسجل، والموجهات، ومساعدات التطبيع |
    | `plugin-sdk/realtime-transcription` | أنواع مزوّد realtime transcription ومساعدات السجل |
    | `plugin-sdk/realtime-voice` | أنواع مزوّد realtime voice ومساعدات السجل |
    | `plugin-sdk/image-generation` | أنواع مزوّد image generation |
    | `plugin-sdk/image-generation-core` | أنواع image-generation المشتركة، والفشل البديل، والمصادقة، ومساعدات السجل |
    | `plugin-sdk/music-generation` | أنواع مزوّد/طلب/نتيجة music generation |
    | `plugin-sdk/music-generation-core` | أنواع music-generation المشتركة، ومساعدات الفشل البديل، والبحث عن المزوّد، وتحليل مراجع النماذج |
    | `plugin-sdk/video-generation` | أنواع مزوّد/طلب/نتيجة video generation |
    | `plugin-sdk/video-generation-core` | أنواع video-generation المشتركة، ومساعدات الفشل البديل، والبحث عن المزوّد، وتحليل مراجع النماذج |
    | `plugin-sdk/webhook-targets` | سجل أهداف webhook ومساعدات تثبيت route |
    | `plugin-sdk/webhook-path` | مساعدات تطبيع مسار webhook |
    | `plugin-sdk/web-media` | مساعدات مشتركة لتحميل الوسائط البعيدة/المحلية |
    | `plugin-sdk/zod` | إعادة تصدير `zod` لمستهلكي Plugin SDK |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="المسارات الفرعية للذاكرة">
    | المسار الفرعي | أهم التصديرات |
    | --- | --- |
    | `plugin-sdk/memory-core` | سطح مساعد memory-core المضمّن لمساعدات المدير/الإعدادات/الملفات/CLI |
    | `plugin-sdk/memory-core-engine-runtime` | واجهة وقت تشغيل فهرسة/بحث الذاكرة |
    | `plugin-sdk/memory-core-host-engine-foundation` | تصديرات محرك الأساس لمضيف الذاكرة |
    | `plugin-sdk/memory-core-host-engine-embeddings` | تصديرات محرك embeddings لمضيف الذاكرة |
    | `plugin-sdk/memory-core-host-engine-qmd` | تصديرات محرك QMD لمضيف الذاكرة |
    | `plugin-sdk/memory-core-host-engine-storage` | تصديرات محرك التخزين لمضيف الذاكرة |
    | `plugin-sdk/memory-core-host-multimodal` | مساعدات متعددة الوسائط لمضيف الذاكرة |
    | `plugin-sdk/memory-core-host-query` | مساعدات الاستعلام لمضيف الذاكرة |
    | `plugin-sdk/memory-core-host-secret` | مساعدات الأسرار لمضيف الذاكرة |
    | `plugin-sdk/memory-core-host-events` | مساعدات سجل أحداث مضيف الذاكرة |
    | `plugin-sdk/memory-core-host-status` | مساعدات حالة مضيف الذاكرة |
    | `plugin-sdk/memory-core-host-runtime-cli` | مساعدات CLI لوقت تشغيل مضيف الذاكرة |
    | `plugin-sdk/memory-core-host-runtime-core` | مساعدات وقت التشغيل الأساسية لمضيف الذاكرة |
    | `plugin-sdk/memory-core-host-runtime-files` | مساعدات الملفات/وقت التشغيل لمضيف الذاكرة |
    | `plugin-sdk/memory-host-core` | اسم مستعار محايد للمورّد لمساعدات وقت التشغيل الأساسية لمضيف الذاكرة |
    | `plugin-sdk/memory-host-events` | اسم مستعار محايد للمورّد لمساعدات سجل أحداث مضيف الذاكرة |
    | `plugin-sdk/memory-host-files` | اسم مستعار محايد للمورّد لمساعدات الملفات/وقت التشغيل لمضيف الذاكرة |
    | `plugin-sdk/memory-host-markdown` | مساعدات shared managed-markdown للإضافات المرتبطة بالذاكرة |
    | `plugin-sdk/memory-host-search` | واجهة وقت تشغيل الذاكرة النشطة للوصول إلى search-manager |
    | `plugin-sdk/memory-host-status` | اسم مستعار محايد للمورّد لمساعدات حالة مضيف الذاكرة |
    | `plugin-sdk/memory-lancedb` | سطح مساعد memory-lancedb المضمّن |
  </Accordion>

  <Accordion title="المسارات الفرعية المحجوزة للمساعدات المضمّنة">
    | الفئة | المسارات الفرعية الحالية | الاستخدام المقصود |
    | --- | --- | --- |
    | المتصفح | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | مساعدات دعم إضافة المتصفح المضمّنة (`browser-support` يبقى شريط التوافق) |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | سطح مساعد/وقت تشغيل Matrix المضمّن |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | سطح مساعد/وقت تشغيل LINE المضمّن |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | سطح مساعد IRC المضمّن |
    | مساعدات خاصة بالقنوات | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | أسطح توافق/مساعدة القنوات المضمّنة |
    | مساعدات خاصة بالمصادقة/الإضافات | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | أسطح مساعدة الميزات/الإضافات المضمّنة؛ يصدر `plugin-sdk/github-copilot-token` حاليًا `DEFAULT_COPILOT_API_BASE_URL` و`deriveCopilotApiBaseUrlFromToken` و`resolveCopilotApiToken` |
  </Accordion>
</AccordionGroup>

## واجهة برمجة التسجيل

يتلقى رد النداء `register(api)` كائن `OpenClawPluginApi` بهذه
الأساليب:

### تسجيل الإمكانات

| الأسلوب                                         | ما الذي يسجله                     |
| ----------------------------------------------- | --------------------------------- |
| `api.registerProvider(...)`                     | استدلال النص (LLM)                |
| `api.registerCliBackend(...)`                   | واجهة خلفية محلية للاستدلال عبر CLI |
| `api.registerChannel(...)`                      | قناة مراسلة                       |
| `api.registerSpeechProvider(...)`               | تركيب text-to-speech / STT        |
| `api.registerRealtimeTranscriptionProvider(...)`| نسخ فوري متدفق في الزمن الحقيقي   |
| `api.registerRealtimeVoiceProvider(...)`        | جلسات صوتية ثنائية الاتجاه بالزمن الحقيقي |
| `api.registerMediaUnderstandingProvider(...)`   | تحليل الصور/الصوت/الفيديو         |
| `api.registerImageGenerationProvider(...)`      | توليد الصور                       |
| `api.registerMusicGenerationProvider(...)`      | توليد الموسيقى                    |
| `api.registerVideoGenerationProvider(...)`      | توليد الفيديو                     |
| `api.registerWebFetchProvider(...)`             | مزود web fetch / scrape           |
| `api.registerWebSearchProvider(...)`            | بحث الويب                         |

### الأدوات والأوامر

| الأسلوب                        | ما الذي يسجله                                  |
| ------------------------------ | ---------------------------------------------- |
| `api.registerTool(tool, opts?)`| أداة وكيل (إلزامية أو `{ optional: true }`)    |
| `api.registerCommand(def)`     | أمر مخصص (يتجاوز LLM)                          |

### البنية التحتية

| الأسلوب                                        | ما الذي يسجله                     |
| ---------------------------------------------- | --------------------------------- |
| `api.registerHook(events, handler, opts?)`     | خطاف أحداث                        |
| `api.registerHttpRoute(params)`                | نقطة نهاية HTTP في Gateway        |
| `api.registerGatewayMethod(name, handler)`     | أسلوب Gateway RPC                 |
| `api.registerCli(registrar, opts?)`            | أمر فرعي في CLI                   |
| `api.registerService(service)`                 | خدمة في الخلفية                   |
| `api.registerInteractiveHandler(registration)` | معالج تفاعلي                      |
| `api.registerMemoryPromptSupplement(builder)`  | قسم إضافي للموجّه مرتبط بالذاكرة  |
| `api.registerMemoryCorpusSupplement(adapter)`  | متن إضافي لبحث/قراءة الذاكرة      |

تبقى مساحات أسماء الإدارة الأساسية المحجوزة (`config.*` و`exec.approvals.*` و`wizard.*` و
`update.*`) دائمًا `operator.admin`، حتى إذا حاولت إضافة تعيين
نطاق أضيق لأسلوب Gateway. وفضّل استخدام بادئات خاصة بالإضافة
للأساليب التي تملكها الإضافة.

### بيانات التسجيل الوصفية لـ CLI

يقبل `api.registerCli(registrar, opts?)` نوعين من البيانات الوصفية ذات المستوى الأعلى:

- `commands`: جذور أوامر صريحة يملكها المسجّل
- `descriptors`: واصفات أوامر في وقت التحليل تُستخدم لمساعدة CLI الجذرية،
  والتوجيه، والتسجيل الكسول لـ CLI الخاص بالإضافة

إذا أردت أن يبقى أمر الإضافة محمّلًا بكسل في المسار الجذري العادي لـ CLI،
فقدّم `descriptors` تغطي كل جذر أمر من المستوى الأعلى يكشفه ذلك
المسجّل.

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
        description: "Manage Matrix accounts, verification, devices, and profile state",
        hasSubcommands: true,
      },
    ],
  },
);
```

استخدم `commands` وحده فقط عندما لا تحتاج إلى تسجيل كسول في المسار الجذري لـ CLI.
ولا يزال مسار التوافق eager هذا مدعومًا، لكنه لا يثبت
عناصر نائبة مدعومة بـ descriptor للتحميل الكسول وقت التحليل.

### تسجيل الواجهة الخلفية CLI

يسمح `api.registerCliBackend(...)` لإضافة بامتلاك الإعداد الافتراضي لواجهة
خلفية محلية لـ CLI الخاص بالذكاء الاصطناعي مثل `codex-cli`.

- يصبح `id` الخاص بالواجهة الخلفية بادئة المزوّد في مراجع النماذج مثل `codex-cli/gpt-5`.
- يستخدم `config` الخاص بالواجهة الخلفية الشكل نفسه المستخدم في `agents.defaults.cliBackends.<id>`.
- تظل إعدادات المستخدم هي الغالبة. يدمج OpenClaw `agents.defaults.cliBackends.<id>` فوق
  القيمة الافتراضية للإضافة قبل تشغيل CLI.
- استخدم `normalizeConfig` عندما تحتاج واجهة خلفية إلى إعادة كتابة توافق بعد الدمج
  (على سبيل المثال تطبيع أشكال الأعلام القديمة).

### الفتحات الحصرية

| الأسلوب                                    | ما الذي يسجله                                                                                                                                         |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `api.registerContextEngine(id, factory)`   | محرك سياق (واحد نشط في كل مرة). يتلقى رد النداء `assemble()` كلًا من `availableTools` و`citationsMode` حتى يتمكن المحرك من تخصيص إضافات الموجّه. |
| `api.registerMemoryCapability(capability)` | قدرة ذاكرة موحدة                                                                                                                                       |
| `api.registerMemoryPromptSection(builder)` | باني قسم موجّه الذاكرة                                                                                                                                |
| `api.registerMemoryFlushPlan(resolver)`    | محلل خطة تفريغ الذاكرة                                                                                                                                 |
| `api.registerMemoryRuntime(runtime)`       | مهايئ وقت تشغيل الذاكرة                                                                                                                                |

### مهايئات تضمين الذاكرة

| الأسلوب                                        | ما الذي يسجله                                 |
| ---------------------------------------------- | --------------------------------------------- |
| `api.registerMemoryEmbeddingProvider(adapter)` | مهايئ تضمين الذاكرة للإضافة النشطة            |

- `registerMemoryCapability` هي واجهة API المفضلة والحصرية لإضافات الذاكرة.
- قد تكشف `registerMemoryCapability` أيضًا `publicArtifacts.listArtifacts(...)`
  حتى تتمكن الإضافات المصاحبة من استهلاك عناصر الذاكرة المصدّرة عبر
  `openclaw/plugin-sdk/memory-host-core` بدلًا من الوصول إلى التخطيط الخاص
  بإضافة ذاكرة محددة.
- `registerMemoryPromptSection` و`registerMemoryFlushPlan` و
  `registerMemoryRuntime` هي واجهات API متوافقة مع الإضافات القديمة
  والحصرية لإضافات الذاكرة.
- يتيح `registerMemoryEmbeddingProvider` لإضافة الذاكرة النشطة تسجيل
  معرّف مهايئ تضمين واحد أو أكثر (مثل `openai` أو `gemini` أو معرّف
  مخصص تعرفه الإضافة).
- تُحل إعدادات المستخدم مثل `agents.defaults.memorySearch.provider` و
  `agents.defaults.memorySearch.fallback` مقابل معرّفات المهايئات المسجلة تلك.

### الأحداث ودورة الحياة

| الأسلوب                                     | ما الذي يفعله                |
| ------------------------------------------- | ---------------------------- |
| `api.on(hookName, handler, opts?)`          | خطاف دورة حياة مطبوع         |
| `api.onConversationBindingResolved(handler)`| رد نداء عند حل ربط المحادثة  |

### دلالات قرار الخطافات

- `before_tool_call`: إرجاع `{ block: true }` نهائي. فبمجرد أن يعينه أي معالج، يتم تخطي المعالجات ذات الأولوية الأدنى.
- `before_tool_call`: إرجاع `{ block: false }` يُعامل على أنه بلا قرار (مثل حذف `block`) وليس كتجاوز.
- `before_install`: إرجاع `{ block: true }` نهائي. فبمجرد أن يعينه أي معالج، يتم تخطي المعالجات ذات الأولوية الأدنى.
- `before_install`: إرجاع `{ block: false }` يُعامل على أنه بلا قرار (مثل حذف `block`) وليس كتجاوز.
- `reply_dispatch`: إرجاع `{ handled: true, ... }` نهائي. فبمجرد أن يطالب أي معالج بالتوزيع، يتم تخطي المعالجات ذات الأولوية الأدنى ومسار توزيع النموذج الافتراضي.
- `message_sending`: إرجاع `{ cancel: true }` نهائي. فبمجرد أن يعينه أي معالج، يتم تخطي المعالجات ذات الأولوية الأدنى.
- `message_sending`: إرجاع `{ cancel: false }` يُعامل على أنه بلا قرار (مثل حذف `cancel`) وليس كتجاوز.

### حقول كائن API

| الحقل                   | النوع                     | الوصف                                                                                         |
| ----------------------- | ------------------------- | ---------------------------------------------------------------------------------------------- |
| `api.id`                | `string`                  | معرّف الإضافة                                                                                  |
| `api.name`              | `string`                  | اسم العرض                                                                                      |
| `api.version`           | `string?`                 | إصدار الإضافة (اختياري)                                                                        |
| `api.description`       | `string?`                 | وصف الإضافة (اختياري)                                                                          |
| `api.source`            | `string`                  | مسار مصدر الإضافة                                                                              |
| `api.rootDir`           | `string?`                 | دليل جذر الإضافة (اختياري)                                                                     |
| `api.config`            | `OpenClawConfig`          | لقطة الإعدادات الحالية (لقطة وقت التشغيل النشطة داخل الذاكرة عند توفرها)                      |
| `api.pluginConfig`      | `Record<string, unknown>` | إعدادات خاصة بالإضافة من `plugins.entries.<id>.config`                                         |
| `api.runtime`           | `PluginRuntime`           | [مساعدات وقت التشغيل](/ar/plugins/sdk-runtime)                                                    |
| `api.logger`            | `PluginLogger`            | مسجّل ذو نطاق محدد (`debug`, `info`, `warn`, `error`)                                          |
| `api.registrationMode`  | `PluginRegistrationMode`  | وضع التحميل الحالي؛ `"setup-runtime"` هي نافذة بدء التشغيل/الإعداد الخفيفة قبل الإدخال الكامل |
| `api.resolvePath(input)`| `(string) => string`      | حل المسار نسبة إلى جذر الإضافة                                                                 |

## اصطلاح الوحدة الداخلية

داخل إضافتك، استخدم ملفات barrel محلية للاستيرادات الداخلية:

```
my-plugin/
  api.ts            # تصديرات عامة للمستهلكين الخارجيين
  runtime-api.ts    # تصديرات وقت تشغيل داخلية فقط
  index.ts          # نقطة إدخال الإضافة
  setup-entry.ts    # إدخال خفيف للإعداد فقط (اختياري)
```

<Warning>
  لا تستورد إضافتك الخاصة أبدًا من خلال `openclaw/plugin-sdk/<your-plugin>`
  من كود الإنتاج. وجّه الاستيرادات الداخلية عبر `./api.ts` أو
  `./runtime-api.ts`. فمسار SDK هو العقد الخارجي فقط.
</Warning>

تفضّل الآن الأسطح العامة للإضافات المضمّنة المحمّلة عبر الواجهات (`api.ts` و`runtime-api.ts`،
و`index.ts`، و`setup-entry.ts`، وملفات الإدخال العامة المشابهة)
لقطة إعدادات وقت التشغيل النشطة عندما يكون OpenClaw قيد التشغيل بالفعل. وإذا لم تكن
هناك لقطة وقت تشغيل موجودة بعد، فإنها ترجع إلى ملف الإعدادات المحلول على القرص.

يمكن لإضافات المزوّدين أيضًا كشف شريط عقد محلي ضيق خاص بالإضافة عندما
يكون المساعد خاصًا بالمزوّد عمدًا ولا ينتمي بعد إلى مسار فرعي عام من SDK.
المثال المضمّن الحالي: يحتفظ مزوّد Anthropic بمساعدات تدفق Claude الخاصة به
ضمن السطح العام `api.ts` / `contract-api.ts` بدلًا من
ترقية منطق ترويسات Anthropic التجريبية و`service_tier` إلى عقد عام
ضمن `plugin-sdk/*`.

أمثلة مضمّنة حالية أخرى:

- `@openclaw/openai-provider`: يصدّر `api.ts` بناة المزوّد،
  ومساعدات النماذج الافتراضية، وبناة مزوّدات الوقت الحقيقي
- `@openclaw/openrouter-provider`: يصدّر `api.ts` باني المزوّد بالإضافة إلى
  مساعدات الإعداد الأولي/الإعدادات

<Warning>
  يجب أن يتجنب كود الإنتاج الخاص بالامتدادات أيضًا استيراد
  `openclaw/plugin-sdk/<other-plugin>`. وإذا كان مساعد ما مشتركًا فعلًا،
  فقم بترقيته إلى مسار فرعي محايد من SDK
  مثل `openclaw/plugin-sdk/speech` أو `.../provider-model-shared` أو سطح آخر
  موجّه للإمكانات بدلًا من ربط إضافتين ببعضهما مباشرة.
</Warning>

## ذو صلة

- [نقاط الإدخال](/ar/plugins/sdk-entrypoints) — خيارات `definePluginEntry` و`defineChannelPluginEntry`
- [مساعدات وقت التشغيل](/ar/plugins/sdk-runtime) — المرجع الكامل لنطاق `api.runtime`
- [الإعداد والإعدادات](/ar/plugins/sdk-setup) — التغليف، والبيانات، ومخططات الإعدادات
- [الاختبار](/ar/plugins/sdk-testing) — أدوات الاختبار وقواعد lint
- [ترحيل SDK](/ar/plugins/sdk-migration) — الترحيل من الأسطح المهملة
- [الداخليات الخاصة بالإضافةات](/ar/plugins/architecture) — البنية العميقة ونموذج الإمكانات
