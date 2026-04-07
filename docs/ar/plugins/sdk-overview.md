---
read_when:
    - تحتاج إلى معرفة أي مسار فرعي من SDK يجب الاستيراد منه
    - تريد مرجعًا لجميع أساليب التسجيل على OpenClawPluginApi
    - تبحث عن export محدد في SDK
sidebarTitle: SDK Overview
summary: خريطة الاستيراد، ومرجع API التسجيل، وبنية SDK
title: نظرة عامة على Plugin SDK
x-i18n:
    generated_at: "2026-04-07T07:21:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: 533bc3027ed8ad50b706518a4f58e75f6ef717fc8b36f242e928cae54d20985f
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# نظرة عامة على Plugin SDK

يُعد plugin SDK العقد typed بين plugins وcore. هذه الصفحة هي
المرجع الخاص بـ **ما يجب استيراده** و**ما الذي يمكنك تسجيله**.

<Tip>
  **هل تبحث عن دليل عملي؟**
  - أول plugin؟ ابدأ من [البدء](/ar/plugins/building-plugins)
  - Channel plugin؟ راجع [Channel Plugins](/ar/plugins/sdk-channel-plugins)
  - Provider plugin؟ راجع [Provider Plugins](/ar/plugins/sdk-provider-plugins)
</Tip>

## اصطلاحات الاستيراد

استورد دائمًا من مسار فرعي محدد:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

كل مسار فرعي عبارة عن وحدة صغيرة مستقلة بذاتها. وهذا يُبقي بدء التشغيل سريعًا
ويمنع مشكلات التبعيات الدائرية. بالنسبة إلى مساعدات الإدخال/البناء الخاصة بالقنوات،
فضّل `openclaw/plugin-sdk/channel-core`; وأبقِ `openclaw/plugin-sdk/core` للسطح
الأوسع الشامل والمساعدات المشتركة مثل
`buildChannelConfigSchema`.

لا تضف ولا تعتمد على نقاط ربط تسهيلية مسماة باسم المزود مثل
`openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp` أو
نقاط ربط مساعدة تحمل العلامة الخاصة بالقناة. يجب أن تؤلف plugins المضمنة
المسارات الفرعية العامة من SDK داخل ملفات `api.ts` أو `runtime-api.ts` الخاصة بها، ويجب على core
إما استخدام هذه الملفات المحلية الخاصة بالـ plugin أو إضافة عقد SDK عام ضيق
عندما تكون الحاجة فعلًا عابرة للقنوات.

لا تزال خريطة export المولدة تحتوي على مجموعة صغيرة من
نقاط الربط المساعدة للـ plugins المضمنة مثل `plugin-sdk/feishu`, `plugin-sdk/feishu-setup`,
`plugin-sdk/zalo`, `plugin-sdk/zalo-setup`, و`plugin-sdk/matrix*`. وهذه
المسارات الفرعية موجودة فقط لصيانة plugins المضمنة ولأغراض التوافق؛ وهي
مستبعدة عمدًا من الجدول الشائع أدناه وليست مسار الاستيراد الموصى به
للـ plugins الخارجية الجديدة.

## مرجع المسارات الفرعية

أكثر المسارات الفرعية استخدامًا، مجمعة حسب الغرض. والقائمة الكاملة المولدة التي تضم
أكثر من 200 مسار فرعي موجودة في `scripts/lib/plugin-sdk-entrypoints.json`.

لا تزال مسارات المساعدة المحجوزة الخاصة بالـ plugins المضمنة تظهر في تلك القائمة المولدة.
تعامل معها على أنها أسطح تنفيذية/توافقية ما لم تروّج صفحة توثيق
لأحدها صراحةً على أنه عام.

### إدخال plugin

| المسار الفرعي | أهم exports |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/plugin-entry`   | `definePluginEntry`                                                                                                                    |
| `plugin-sdk/core`           | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema`  | `OpenClawSchema`                                                                                                                       |
| `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry`                                                                                                      |

<AccordionGroup>
  <Accordion title="المسارات الفرعية للقنوات">
    | المسار الفرعي | أهم exports |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | export مخطط Zod الجذر لـ `openclaw.json` ‏(`OpenClawSchema`) |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`، بالإضافة إلى `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | مساعدات wizard المشتركة للإعداد، ومطالبات allowlist، وبناة حالة الإعداد |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | مساعدات إعدادات/بوابة إجراءات متعددة الحسابات، ومساعدات fallback الخاصة بالحساب الافتراضي |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`، ومساعدات تطبيع معرّف الحساب |
    | `plugin-sdk/account-resolution` | مساعدات البحث عن الحساب + fallback الافتراضي |
    | `plugin-sdk/account-helpers` | مساعدات ضيقة لقوائم الحسابات/إجراءات الحساب |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | أنواع مخطط إعدادات القناة |
    | `plugin-sdk/telegram-command-config` | مساعدات تطبيع/تحقق أوامر Telegram المخصصة مع fallback لعقد مجمّع |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | مساعدات مشتركة لبناء route + envelope للوارد |
    | `plugin-sdk/inbound-reply-dispatch` | مساعدات مشتركة لتسجيل وإرسال الردود الواردة |
    | `plugin-sdk/messaging-targets` | مساعدات تحليل/مطابقة الأهداف |
    | `plugin-sdk/outbound-media` | مساعدات مشتركة لتحميل الوسائط الصادرة |
    | `plugin-sdk/outbound-runtime` | مساعدات هوية الصادر/تفويض الإرسال |
    | `plugin-sdk/thread-bindings-runtime` | مساعدات دورة حياة thread-binding وadapter |
    | `plugin-sdk/agent-media-payload` | باني قديم لحمولة وسائط الوكيل |
    | `plugin-sdk/conversation-runtime` | مساعدات الربط بالمحادثة/الخيط، والاقتران، والربط المُعد |
    | `plugin-sdk/runtime-config-snapshot` | مساعد لقطة إعدادات وقت التشغيل |
    | `plugin-sdk/runtime-group-policy` | مساعدات تحليل group-policy في وقت التشغيل |
    | `plugin-sdk/channel-status` | مساعدات مشتركة للقطات/ملخصات حالة القناة |
    | `plugin-sdk/channel-config-primitives` | بدائيات ضيقة لمخطط إعدادات القناة |
    | `plugin-sdk/channel-config-writes` | مساعدات تفويض كتابة إعدادات القناة |
    | `plugin-sdk/channel-plugin-common` | exports تمهيدية مشتركة لـ Channel plugin |
    | `plugin-sdk/allowlist-config-edit` | مساعدات قراءة/تحرير إعدادات allowlist |
    | `plugin-sdk/group-access` | مساعدات مشتركة لقرارات الوصول إلى المجموعات |
    | `plugin-sdk/direct-dm` | مساعدات مشتركة لمصادقة/حراسة الرسائل الخاصة المباشرة |
    | `plugin-sdk/interactive-runtime` | مساعدات تطبيع/تقليص حمولة الرد التفاعلي |
    | `plugin-sdk/channel-inbound` | مساعدات إزالة ارتداد الوارد، ومطابقة الإشارات، وسياسة الإشارة، وenvelope |
    | `plugin-sdk/channel-send-result` | أنواع نتائج الرد |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | مساعدات تحليل/مطابقة الأهداف |
    | `plugin-sdk/channel-contract` | أنواع عقد القناة |
    | `plugin-sdk/channel-feedback` | توصيل feedback/reaction |
    | `plugin-sdk/channel-secret-runtime` | مساعدات ضيقة لعقود الأسرار مثل `collectSimpleChannelFieldAssignments`, `getChannelSurface`, `pushAssignment` وأنواع أهداف الأسرار |
  </Accordion>

  <Accordion title="المسارات الفرعية للمزودات">
    | المسار الفرعي | أهم exports |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | مساعدات إعداد منتقاة للمزودات المحلية/المستضافة ذاتيًا |
    | `plugin-sdk/self-hosted-provider-setup` | مساعدات إعداد مركزة لمزودات OpenAI-compatible المستضافة ذاتيًا |
    | `plugin-sdk/cli-backend` | قيم افتراضية لـ CLI backend + ثوابت watchdog |
    | `plugin-sdk/provider-auth-runtime` | مساعدات وقت التشغيل لتحليل API key الخاصة بـ Provider plugins |
    | `plugin-sdk/provider-auth-api-key` | مساعدات onboarding/كتابة profile لمفتاح API مثل `upsertApiKeyProfile` |
    | `plugin-sdk/provider-auth-result` | باني auth-result قياسي لـ OAuth |
    | `plugin-sdk/provider-auth-login` | مساعدات تسجيل دخول تفاعلية مشتركة لـ Provider plugins |
    | `plugin-sdk/provider-env-vars` | مساعدات البحث عن متغيرات البيئة لمصادقة المزود |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile`, `upsertApiKeyProfile`, `writeOAuthCredentials` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`، وبناة replay-policy المشتركون، ومساعدات endpoint للمزود، ومساعدات تطبيع model-id مثل `normalizeNativeXaiModelId` |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | مساعدات عامة لقدرات HTTP/endpoint الخاصة بالمزود |
    | `plugin-sdk/provider-web-fetch` | مساعدات التسجيل/cache لمزود web-fetch |
    | `plugin-sdk/provider-web-search-contract` | مساعدات ضيقة لعقود إعدادات/بيانات اعتماد web-search مثل `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig`، ومعينات set/get لبيانات اعتماد محددة النطاق |
    | `plugin-sdk/provider-web-search` | مساعدات التسجيل/cache/وقت التشغيل لمزود web-search |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`، وتنظيف/تشخيص مخطط Gemini، ومساعدات توافق xAI مثل `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` وما شابه |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`، وأنواع stream wrapper، ومساعدات wrappers المشتركة لـ Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
    | `plugin-sdk/provider-onboard` | مساعدات تعديل إعدادات onboarding |
    | `plugin-sdk/global-singleton` | مساعدات singleton/map/cache محلية للعملية |
  </Accordion>

  <Accordion title="المسارات الفرعية للمصادقة والأمان">
    | المسار الفرعي | أهم exports |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`، ومساعدات سجل الأوامر، ومساعدات تفويض المرسل |
    | `plugin-sdk/approval-auth-runtime` | مساعدات تحليل approver ومصادقة الإجراء في نفس الدردشة |
    | `plugin-sdk/approval-client-runtime` | مساعدات ملفات التعريف/المرشحات الأصلية لـ exec approval |
    | `plugin-sdk/approval-delivery-runtime` | محولات القدرات/التسليم الأصلية لـ approval |
    | `plugin-sdk/approval-native-runtime` | مساعدات الهدف الأصلي لـ approval + ربط الحساب |
    | `plugin-sdk/approval-reply-runtime` | مساعدات حمولة الرد لـ exec/plugin approval |
    | `plugin-sdk/command-auth-native` | مصادقة الأوامر الأصلية + مساعدات الهدف الأصلي للجلسة |
    | `plugin-sdk/command-detection` | مساعدات مشتركة لاكتشاف الأوامر |
    | `plugin-sdk/command-surface` | تطبيع نص الأمر ومساعدات سطح الأمر |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/channel-secret-runtime` | مساعدات ضيقة لتجميع عقود الأسرار لأسطح أسرار القناة/الـ plugin |
    | `plugin-sdk/secret-ref-runtime` | مساعدات ضيقة لـ `coerceSecretRef` وأنواع SecretRef لتحليل عقود الأسرار/الإعدادات |
    | `plugin-sdk/security-runtime` | مساعدات مشتركة للثقة، وتقييد DM، والمحتوى الخارجي، وتجميع الأسرار |
    | `plugin-sdk/ssrf-policy` | مساعدات allowlist للمضيف وسياسة SSRF للشبكات الخاصة |
    | `plugin-sdk/ssrf-runtime` | مساعدات pinned-dispatcher وfetch المحروس بـ SSRF وسياسة SSRF |
    | `plugin-sdk/secret-input` | مساعدات تحليل مدخلات الأسرار |
    | `plugin-sdk/webhook-ingress` | مساعدات طلب/هدف webhook |
    | `plugin-sdk/webhook-request-guards` | مساعدات حجم جسم الطلب/المهلة |
  </Accordion>

  <Accordion title="المسارات الفرعية لوقت التشغيل والتخزين">
    | المسار الفرعي | أهم exports |
    | --- | --- |
    | `plugin-sdk/runtime` | مساعدات واسعة لوقت التشغيل/التسجيل/النسخ الاحتياطي/تثبيت plugin |
    | `plugin-sdk/runtime-env` | مساعدات ضيقة لبيئة وقت التشغيل، وlogger، والمهلة، وإعادة المحاولة، وbackoff |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | مساعدات مشتركة لأوامر/خطافات/HTTP/التفاعلية الخاصة بالـ plugin |
    | `plugin-sdk/hook-runtime` | مساعدات مشتركة لخطوط webhook/internal hook |
    | `plugin-sdk/lazy-runtime` | مساعدات الاستيراد/الربط الكسول لوقت التشغيل مثل `createLazyRuntimeModule`, `createLazyRuntimeMethod`, و`createLazyRuntimeSurface` |
    | `plugin-sdk/process-runtime` | مساعدات تنفيذ العمليات |
    | `plugin-sdk/cli-runtime` | مساعدات تنسيق CLI، والانتظار، والإصدار |
    | `plugin-sdk/gateway-runtime` | مساعدات عميل Gateway وتعديل حالة القناة |
    | `plugin-sdk/config-runtime` | مساعدات تحميل/كتابة الإعدادات |
    | `plugin-sdk/telegram-command-config` | مساعدات تطبيع أسماء/أوصاف أوامر Telegram والتحقق من التكرار/التعارض، حتى عند عدم توفر سطح عقد Telegram المضمّن |
    | `plugin-sdk/approval-runtime` | مساعدات exec/plugin approval، وبناة approval-capability، ومساعدات المصادقة/profile، ومساعدات التوجيه/وقت التشغيل الأصلية |
    | `plugin-sdk/reply-runtime` | مساعدات مشتركة لوقت تشغيل الوارد/الرد، والتجزئة، والإرسال، وheartbeat، ومخطط الرد |
    | `plugin-sdk/reply-dispatch-runtime` | مساعدات ضيقة لإرسال/إنهاء الرد |
    | `plugin-sdk/reply-history` | مساعدات مشتركة لسجل الرد قصير النافذة مثل `buildHistoryContext`, `recordPendingHistoryEntry`, و`clearHistoryEntriesIfEnabled` |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | مساعدات ضيقة لتجزئة النص/Markdown |
    | `plugin-sdk/session-store-runtime` | مساعدات مسار مخزن الجلسة + updated-at |
    | `plugin-sdk/state-paths` | مساعدات مسارات الحالة/OAuth |
    | `plugin-sdk/routing` | مساعدات route/session-key وربط الحساب مثل `resolveAgentRoute`, `buildAgentSessionKey`, و`resolveDefaultAgentBoundAccountId` |
    | `plugin-sdk/status-helpers` | مساعدات مشتركة لملخصات حالة القناة/الحساب، والقيم الافتراضية لحالة وقت التشغيل، ومساعدات بيانات issue الوصفية |
    | `plugin-sdk/target-resolver-runtime` | مساعدات مشتركة لتحليل الأهداف |
    | `plugin-sdk/string-normalization-runtime` | مساعدات تطبيع slug/string |
    | `plugin-sdk/request-url` | استخراج عناوين URL النصية من مدخلات شبيهة بـ fetch/request |
    | `plugin-sdk/run-command` | مُشغّل أوامر موقّت بنتائج stdout/stderr مطبّعة |
    | `plugin-sdk/param-readers` | قارئات معلمات شائعة للأدوات/CLI |
    | `plugin-sdk/tool-send` | استخراج حقول هدف الإرسال القياسية من وسيطات الأداة |
    | `plugin-sdk/temp-path` | مساعدات مشتركة لمسارات التنزيل المؤقت |
    | `plugin-sdk/logging-core` | مساعدات logger الخاصة بالأنظمة الفرعية وإخفاء البيانات |
    | `plugin-sdk/markdown-table-runtime` | مساعدات وضع جداول Markdown |
    | `plugin-sdk/json-store` | مساعدات صغيرة لقراءة/كتابة حالة JSON |
    | `plugin-sdk/file-lock` | مساعدات file-lock قابلة لإعادة الدخول |
    | `plugin-sdk/persistent-dedupe` | مساعدات cache لإزالة التكرار مدعومة بالقرص |
    | `plugin-sdk/acp-runtime` | مساعدات وقت تشغيل ACP/session وإرسال الرد |
    | `plugin-sdk/agent-config-primitives` | بدائيات ضيقة لمخطط إعدادات وقت تشغيل الوكيل |
    | `plugin-sdk/boolean-param` | قارئ مرن لمعامل boolean |
    | `plugin-sdk/dangerous-name-runtime` | مساعدات تحليل مطابقة الأسماء الخطرة |
    | `plugin-sdk/device-bootstrap` | مساعدات bootstrap للجهاز ورمز الاقتران |
    | `plugin-sdk/extension-shared` | بدائيات مساعدة مشتركة للقنوات السلبية، والحالة، والـ ambient proxy |
    | `plugin-sdk/models-provider-runtime` | مساعدات الرد لأمر `/models`/المزود |
    | `plugin-sdk/skill-commands-runtime` | مساعدات سرد أوامر Skills |
    | `plugin-sdk/native-command-registry` | مساعدات السجل الأصلي للأوامر/البناء/التسلسل |
    | `plugin-sdk/provider-zai-endpoint` | مساعدات اكتشاف endpoint لـ Z.A.I |
    | `plugin-sdk/infra-runtime` | مساعدات أحداث النظام/heartbeat |
    | `plugin-sdk/collection-runtime` | مساعدات صغيرة لـ cache محدود |
    | `plugin-sdk/diagnostic-runtime` | مساعدات الأعلام التشخيصية والأحداث |
    | `plugin-sdk/error-runtime` | رسم الأخطاء، والتنسيق، ومساعدات تصنيف الأخطاء المشتركة، و`isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | مساعدات fetch مغلف، وproxy، والبحث المثبت |
    | `plugin-sdk/host-runtime` | مساعدات تطبيع اسم المضيف ومضيف SCP |
    | `plugin-sdk/retry-runtime` | إعدادات إعادة المحاولة ومساعدات مشغّل الإعادة |
    | `plugin-sdk/agent-runtime` | مساعدات دليل الوكيل/الهوية/workspace |
    | `plugin-sdk/directory-runtime` | query/dedup للأدلة المدعومة بالإعدادات |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="المسارات الفرعية للقدرات والاختبار">
    | المسار الفرعي | أهم exports |
    | --- | --- |
    | `plugin-sdk/media-runtime` | مساعدات مشتركة لجلب/تحويل/تخزين الوسائط بالإضافة إلى بناة حمولة الوسائط |
    | `plugin-sdk/media-generation-runtime` | مساعدات مشتركة لفشل-over في توليد الوسائط، واختيار candidates، ورسائل النماذج المفقودة |
    | `plugin-sdk/media-understanding` | أنواع مزود فهم الوسائط بالإضافة إلى exports مساعدة موجهة للمزود للصورة/الصوت |
    | `plugin-sdk/text-runtime` | مساعدات مشتركة للنص/Markdown/التسجيل مثل إزالة النص المرئي للمساعد، ومساعدات render/chunking/table الخاصة بـ Markdown، ومساعدات إخفاء البيانات، وdirective-tag، وأدوات النص الآمن |
    | `plugin-sdk/text-chunking` | مساعد تجزئة النص الصادر |
    | `plugin-sdk/speech` | أنواع مزود الكلام بالإضافة إلى exports موجهة للمزود خاصة بالتوجيه، والسجل، والتحقق |
    | `plugin-sdk/speech-core` | أنواع مشتركة لمزود الكلام، والسجل، والتوجيه، ومساعدات التطبيع |
    | `plugin-sdk/realtime-transcription` | أنواع مزود النسخ الفوري ومساعدات السجل |
    | `plugin-sdk/realtime-voice` | أنواع مزود الصوت الفوري ومساعدات السجل |
    | `plugin-sdk/image-generation` | أنواع مزود توليد الصور |
    | `plugin-sdk/image-generation-core` | أنواع مشتركة لتوليد الصور، والفشل-over، والمصادقة، ومساعدات السجل |
    | `plugin-sdk/music-generation` | أنواع الطلب/النتيجة/المزود لتوليد الموسيقى |
    | `plugin-sdk/music-generation-core` | أنواع مشتركة لتوليد الموسيقى، ومساعدات failover، والبحث عن المزود، وتحليل model-ref |
    | `plugin-sdk/video-generation` | أنواع الطلب/النتيجة/المزود لتوليد الفيديو |
    | `plugin-sdk/video-generation-core` | أنواع مشتركة لتوليد الفيديو، ومساعدات failover، والبحث عن المزود، وتحليل model-ref |
    | `plugin-sdk/webhook-targets` | سجل أهداف webhook ومساعدات تثبيت المسارات |
    | `plugin-sdk/webhook-path` | مساعدات تطبيع مسار webhook |
    | `plugin-sdk/web-media` | مساعدات مشتركة لتحميل الوسائط البعيدة/المحلية |
    | `plugin-sdk/zod` | إعادة export لـ `zod` لمستهلكي Plugin SDK |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="المسارات الفرعية للذاكرة">
    | المسار الفرعي | أهم exports |
    | --- | --- |
    | `plugin-sdk/memory-core` | سطح مساعد memory-core المضمّن لمساعدات manager/config/file/CLI |
    | `plugin-sdk/memory-core-engine-runtime` | واجهة وقت تشغيل لفهرسة/بحث الذاكرة |
    | `plugin-sdk/memory-core-host-engine-foundation` | exports محرك الأساس لمضيف الذاكرة |
    | `plugin-sdk/memory-core-host-engine-embeddings` | exports محرك embeddings لمضيف الذاكرة |
    | `plugin-sdk/memory-core-host-engine-qmd` | exports محرك QMD لمضيف الذاكرة |
    | `plugin-sdk/memory-core-host-engine-storage` | exports محرك التخزين لمضيف الذاكرة |
    | `plugin-sdk/memory-core-host-multimodal` | مساعدات متعددة الوسائط لمضيف الذاكرة |
    | `plugin-sdk/memory-core-host-query` | مساعدات الاستعلام لمضيف الذاكرة |
    | `plugin-sdk/memory-core-host-secret` | مساعدات الأسرار لمضيف الذاكرة |
    | `plugin-sdk/memory-core-host-events` | مساعدات سجل أحداث مضيف الذاكرة |
    | `plugin-sdk/memory-core-host-status` | مساعدات حالة مضيف الذاكرة |
    | `plugin-sdk/memory-core-host-runtime-cli` | مساعدات CLI الخاصة بوقت تشغيل مضيف الذاكرة |
    | `plugin-sdk/memory-core-host-runtime-core` | مساعدات core لوقت تشغيل مضيف الذاكرة |
    | `plugin-sdk/memory-core-host-runtime-files` | مساعدات الملفات/وقت التشغيل لمضيف الذاكرة |
    | `plugin-sdk/memory-host-core` | اسم مستعار محايد للمورّد لمساعدات core لوقت تشغيل مضيف الذاكرة |
    | `plugin-sdk/memory-host-events` | اسم مستعار محايد للمورّد لمساعدات سجل أحداث مضيف الذاكرة |
    | `plugin-sdk/memory-host-files` | اسم مستعار محايد للمورّد لمساعدات الملفات/وقت التشغيل لمضيف الذاكرة |
    | `plugin-sdk/memory-host-markdown` | مساعدات managed-Markdown مشتركة للـ plugins القريبة من الذاكرة |
    | `plugin-sdk/memory-host-search` | واجهة وقت تشغيل الذاكرة النشطة للوصول إلى search-manager |
    | `plugin-sdk/memory-host-status` | اسم مستعار محايد للمورّد لمساعدات حالة مضيف الذاكرة |
    | `plugin-sdk/memory-lancedb` | سطح مساعد memory-lancedb المضمّن |
  </Accordion>

  <Accordion title="المسارات الفرعية المساعدة المحجوزة للمضمن">
    | العائلة | المسارات الفرعية الحالية | الاستخدام المقصود |
    | --- | --- | --- |
    | Browser | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | مساعدات دعم Browser plugin المضمّن (`browser-support` يبقى barrel التوافقية) |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | سطح مساعد/وقت تشغيل Matrix المضمّن |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | سطح مساعد/وقت تشغيل LINE المضمّن |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | سطح مساعد IRC المضمّن |
    | مساعدات خاصة بالقنوات | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | نقاط ربط التوافق/المساعدة للقنوات المضمنة |
    | مساعدات خاصة بالمصادقة/الـ plugin | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | نقاط ربط مساعدة للميزات/الـ plugins المضمنة؛ ويقوم `plugin-sdk/github-copilot-token` حاليًا بتصدير `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken`, و`resolveCopilotApiToken` |
  </Accordion>
</AccordionGroup>

## API التسجيل

يتلقى callback الخاص بـ `register(api)` كائن `OpenClawPluginApi` يحوي
هذه الأساليب:

### تسجيل القدرات

| الأسلوب | ما الذي يسجله |
| ------------------------------------------------ | -------------------------------- |
| `api.registerProvider(...)`                      | الاستدلال النصي (LLM) |
| `api.registerCliBackend(...)`                    | CLI inference backend محلي |
| `api.registerChannel(...)`                       | قناة مراسلة |
| `api.registerSpeechProvider(...)`                | تحويل النص إلى كلام / توليف STT |
| `api.registerRealtimeTranscriptionProvider(...)` | نسخ فوري متدفق |
| `api.registerRealtimeVoiceProvider(...)`         | جلسات صوت فوري ثنائية الاتجاه |
| `api.registerMediaUnderstandingProvider(...)`    | تحليل الصور/الصوت/الفيديو |
| `api.registerImageGenerationProvider(...)`       | توليد الصور |
| `api.registerMusicGenerationProvider(...)`       | توليد الموسيقى |
| `api.registerVideoGenerationProvider(...)`       | توليد الفيديو |
| `api.registerWebFetchProvider(...)`              | مزود جلب / scrape للويب |
| `api.registerWebSearchProvider(...)`             | البحث على الويب |

### الأدوات والأوامر

| الأسلوب | ما الذي يسجله |
| ------------------------------- | --------------------------------------------- |
| `api.registerTool(tool, opts?)` | أداة وكيل (مطلوبة أو `{ optional: true }`) |
| `api.registerCommand(def)`      | أمر مخصص (يتجاوز LLM) |

### البنية التحتية

| الأسلوب | ما الذي يسجله |
| ---------------------------------------------- | --------------------------------------- |
| `api.registerHook(events, handler, opts?)`     | event hook |
| `api.registerHttpRoute(params)`                | endpoint ‏HTTP في Gateway |
| `api.registerGatewayMethod(name, handler)`     | أسلوب Gateway RPC |
| `api.registerCli(registrar, opts?)`            | أمر CLI فرعي |
| `api.registerService(service)`                 | خدمة في الخلفية |
| `api.registerInteractiveHandler(registration)` | معالج تفاعلي |
| `api.registerMemoryPromptSupplement(builder)`  | قسم إضافي من prompt مجاور للذاكرة |
| `api.registerMemoryCorpusSupplement(adapter)`  | corpus إضافي لبحث/قراءة الذاكرة |

تظل مساحات أسماء الإدارة الأساسية المحجوزة (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`) دائمًا عند `operator.admin`، حتى إذا حاول plugin تعيين
نطاق أضيق لأسلوب gateway. ويفضل استخدام بادئات خاصة بالـ plugin
للأساليب المملوكة له.

### بيانات تعريف تسجيل CLI

يقبل `api.registerCli(registrar, opts?)` نوعين من بيانات التعريف العليا:

- `commands`: جذور أوامر صريحة يملكها registrar
- `descriptors`: واصفات أوامر وقت التحليل المستخدمة لمساعدة CLI الجذرية،
  والتوجيه، والتسجيل الكسول لـ CLI الخاص بالـ plugin

إذا كنت تريد أن يبقى أمر plugin محمّلًا بكسل في مسار CLI الجذري العادي،
فقدّم `descriptors` تغطي كل جذر أمر من المستوى الأعلى يكشفه
ذلك registrar.

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

استخدم `commands` وحدها فقط عندما لا تحتاج إلى تسجيل CLI جذري كسول.
يظل مسار التوافق eager هذا مدعومًا، لكنه لا يثبت
عناصر نائبة مدعومة بـ descriptor للتحميل الكسول وقت التحليل.

### تسجيل CLI backend

يتيح `api.registerCliBackend(...)` للـ plugin امتلاك الإعداد الافتراضي لـ
AI CLI backend محلي مثل `codex-cli`.

- يصبح `id` الخاص بالـ backend بادئة المزوّد في مراجع النماذج مثل `codex-cli/gpt-5`.
- تستخدم `config` الخاصة بالـ backend الشكل نفسه الموجود في `agents.defaults.cliBackends.<id>`.
- تظل إعدادات المستخدم هي الغالبة. يدمج OpenClaw ‏`agents.defaults.cliBackends.<id>` فوق
  القيمة الافتراضية للـ plugin قبل تشغيل CLI.
- استخدم `normalizeConfig` عندما يحتاج backend إلى إعادة كتابة توافقية بعد الدمج
  (مثل تطبيع أشكال flags القديمة).

### الخانات الحصرية

| الأسلوب | ما الذي يسجله |
| ------------------------------------------ | ------------------------------------- |
| `api.registerContextEngine(id, factory)`   | محرك سياق (واحد فقط نشط في كل مرة) |
| `api.registerMemoryPromptSection(builder)` | باني قسم prompt للذاكرة |
| `api.registerMemoryFlushPlan(resolver)`    | محلل خطة flush للذاكرة |
| `api.registerMemoryRuntime(runtime)`       | محول وقت تشغيل الذاكرة |

### محولات embedding الخاصة بالذاكرة

| الأسلوب | ما الذي يسجله |
| ---------------------------------------------- | ---------------------------------------------- |
| `api.registerMemoryEmbeddingProvider(adapter)` | محول embedding للذاكرة للـ plugin النشط |

- `registerMemoryPromptSection`, `registerMemoryFlushPlan`, و
  `registerMemoryRuntime` حصرية لـ Memory plugins.
- يتيح `registerMemoryEmbeddingProvider` للـ memory plugin النشط تسجيل
  معرّف محول embedding واحد أو أكثر (مثل `openai`, `gemini`، أو معرّف
  مخصص يعرّفه plugin).
- تُحل إعدادات المستخدم مثل `agents.defaults.memorySearch.provider` و
  `agents.defaults.memorySearch.fallback` مقابل معرّفات المحولات المسجلة تلك.

### الأحداث ودورة الحياة

| الأسلوب | ما الذي يفعله |
| -------------------------------------------- | ----------------------------- |
| `api.on(hookName, handler, opts?)`           | hook دورة حياة typed |
| `api.onConversationBindingResolved(handler)` | callback عند تحليل ربط المحادثة |

### دلالات قرارات الـ hook

- `before_tool_call`: إرجاع `{ block: true }` نهائي. وبمجرد أن يضبطه أي معالج، يتم تخطي المعالجات الأقل أولوية.
- `before_tool_call`: إرجاع `{ block: false }` يُعامل على أنه بدون قرار (مثل حذف `block`) وليس كتجاوز.
- `before_install`: إرجاع `{ block: true }` نهائي. وبمجرد أن يضبطه أي معالج، يتم تخطي المعالجات الأقل أولوية.
- `before_install`: إرجاع `{ block: false }` يُعامل على أنه بدون قرار (مثل حذف `block`) وليس كتجاوز.
- `reply_dispatch`: إرجاع `{ handled: true, ... }` نهائي. وبمجرد أن يدّعي أي معالج الإرسال، يتم تخطي المعالجات الأقل أولوية ومسار إرسال النموذج الافتراضي.
- `message_sending`: إرجاع `{ cancel: true }` نهائي. وبمجرد أن يضبطه أي معالج، يتم تخطي المعالجات الأقل أولوية.
- `message_sending`: إرجاع `{ cancel: false }` يُعامل على أنه بدون قرار (مثل حذف `cancel`) وليس كتجاوز.

### حقول كائن API

| الحقل | النوع | الوصف |
| ------------------------ | ------------------------- | ------------------------------------------------------------------------------------------- |
| `api.id`                 | `string`                  | معرّف plugin |
| `api.name`               | `string`                  | اسم العرض |
| `api.version`            | `string?`                 | إصدار plugin ‏(اختياري) |
| `api.description`        | `string?`                 | وصف plugin ‏(اختياري) |
| `api.source`             | `string`                  | مسار مصدر plugin |
| `api.rootDir`            | `string?`                 | الدليل الجذري لـ plugin ‏(اختياري) |
| `api.config`             | `OpenClawConfig`          | لقطة الإعدادات الحالية (لقطة وقت تشغيل داخل الذاكرة النشطة عندما تكون متاحة) |
| `api.pluginConfig`       | `Record<string, unknown>` | إعدادات خاصة بالـ plugin من `plugins.entries.<id>.config` |
| `api.runtime`            | `PluginRuntime`           | [مساعدات وقت التشغيل](/ar/plugins/sdk-runtime) |
| `api.logger`             | `PluginLogger`            | logger محدود النطاق (`debug`, `info`, `warn`, `error`) |
| `api.registrationMode`   | `PluginRegistrationMode`  | وضع التحميل الحالي؛ و`"setup-runtime"` هي نافذة بدء التشغيل/الإعداد الخفيفة قبل الإدخال الكامل |
| `api.resolvePath(input)` | `(string) => string`      | تحليل المسار نسبةً إلى جذر plugin |

## اصطلاحات الوحدات الداخلية

داخل plugin الخاص بك، استخدم ملفات barrel محلية للاستيراد الداخلي:

```
my-plugin/
  api.ts            # Exports عامة للمستهلكين الخارجيين
  runtime-api.ts    # Exports داخلية فقط لوقت التشغيل
  index.ts          # نقطة إدخال plugin
  setup-entry.ts    # إدخال خفيف خاص بالإعداد فقط (اختياري)
```

<Warning>
  لا تستورد plugin الخاص بك أبدًا عبر `openclaw/plugin-sdk/<your-plugin>`
  من كود الإنتاج. وجّه عمليات الاستيراد الداخلية عبر `./api.ts` أو
  `./runtime-api.ts`. مسار SDK هو العقد الخارجي فقط.
</Warning>

تفضّل الآن الأسطح العامة للـ plugins المضمنة المحمّلة عبر facade (`api.ts`, `runtime-api.ts`,
`index.ts`, `setup-entry.ts`، وملفات الإدخال العامة المشابهة) استخدام
لقطة إعدادات وقت التشغيل النشطة عندما يكون OpenClaw يعمل بالفعل. وإذا لم تكن
هناك لقطة وقت تشغيل متاحة بعد، فسترجع إلى ملف الإعدادات المحلول على القرص.

يمكن لـ Provider plugins أيضًا كشف barrel عقد محلي ضيق خاص بالـ plugin عندما يكون
المساعد مقصودًا أن يكون خاصًا بالمزود ولا ينتمي بعد إلى مسار فرعي عام في SDK.
المثال المضمّن الحالي: يحتفظ مزود Anthropic بمساعدات تدفق Claude
داخل نقطة الربط العامة الخاصة به `api.ts` / `contract-api.ts` بدلًا من
ترقية منطق ترويسات Anthropic beta و`service_tier` إلى عقد عام
`plugin-sdk/*`.

أمثلة مضمنة حالية أخرى:

- `@openclaw/openai-provider`: يصدّر `api.ts` بناة المزودات،
  ومساعدات النماذج الافتراضية، وبناة مزودات الوقت الفعلي
- `@openclaw/openrouter-provider`: يصدّر `api.ts` باني المزود بالإضافة إلى
  مساعدات onboarding/config

<Warning>
  يجب أيضًا على كود الإنتاج الخاص بالامتدادات تجنب استيرادات
  `openclaw/plugin-sdk/<other-plugin>`. وإذا كان أحد المساعدات مشتركًا فعلًا، فقم بترقيته إلى مسار فرعي
  محايد في SDK مثل `openclaw/plugin-sdk/speech`, `.../provider-model-shared` أو أي
  سطح موجّه للقدرات بدلًا من ربط pluginين معًا.
</Warning>

## ذو صلة

- [Entry Points](/ar/plugins/sdk-entrypoints) — خيارات `definePluginEntry` و`defineChannelPluginEntry`
- [Runtime Helpers](/ar/plugins/sdk-runtime) — المرجع الكامل لمساحة الأسماء `api.runtime`
- [Setup and Config](/ar/plugins/sdk-setup) — التغليف، وmanifest، ومخططات الإعدادات
- [Testing](/ar/plugins/sdk-testing) — أدوات الاختبار وقواعد lint
- [SDK Migration](/ar/plugins/sdk-migration) — الترحيل من الأسطح المهجورة
- [Plugin Internals](/ar/plugins/architecture) — البنية العميقة ونموذج القدرات
