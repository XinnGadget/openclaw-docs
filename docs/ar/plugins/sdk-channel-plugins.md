---
read_when:
    - أنت تبني plugin قناة مراسلة جديدة
    - تريد ربط OpenClaw بمنصة مراسلة
    - تحتاج إلى فهم سطح محول ChannelPlugin
sidebarTitle: Channel Plugins
summary: دليل خطوة بخطوة لبناء plugin قناة مراسلة لـ OpenClaw
title: بناء plugins القنوات
x-i18n:
    generated_at: "2026-04-07T07:20:16Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0aab6cc835b292c62e33c52ad0c35f989fb1a5b225511e8bdc2972feb3c64f09
    source_path: plugins/sdk-channel-plugins.md
    workflow: 15
---

# بناء plugins القنوات

يرشدك هذا الدليل خلال بناء plugin قناة يربط OpenClaw بمنصة
مراسلة. وبنهاية الدليل سيكون لديك قناة عاملة مع أمان الرسائل الخاصة،
وpairing، وربط الردود في سلاسل، والمراسلة الصادرة.

<Info>
  إذا لم تكن قد بنيت أي plugin لـ OpenClaw من قبل، فاقرأ
  [البدء](/ar/plugins/building-plugins) أولًا لمعرفة بنية الحزمة الأساسية
  وإعداد manifest.
</Info>

## كيف تعمل plugins القنوات

لا تحتاج plugins القنوات إلى أدوات send/edit/react خاصة بها. يحتفظ OpenClaw
بأداة `message` واحدة مشتركة في النواة. وتمتلك plugin الخاصة بك ما يلي:

- **التهيئة** — تحليل الحسابات ومعالج الإعداد
- **الأمان** — سياسة الرسائل الخاصة وallowlists
- **Pairing** — تدفق اعتماد الرسائل الخاصة
- **صياغة الجلسة** — كيفية تعيين معرّفات المحادثة الخاصة بالموفر إلى الدردشات الأساسية ومعرّفات سلاسل الرسائل وبدائل الأصل
- **الصادر** — إرسال النصوص والوسائط واستطلاعات الرأي إلى المنصة
- **الترابط في السلاسل** — كيفية ربط الردود في سلاسل

تمتلك النواة أداة الرسائل المشتركة، وربط prompt، وشكل مفتاح الجلسة الخارجي،
والتتبّع العام `:thread:`، والإرسال.

إذا كانت منصتك تخزّن نطاقًا إضافيًا داخل معرّفات المحادثات، فاحتفظ بهذا التحليل
داخل plugin باستخدام `messaging.resolveSessionConversation(...)`. هذا هو
المدخل القياسي لتعيين `rawId` إلى معرّف المحادثة الأساسي، ومعرّف سلسلة
اختياري، و`baseConversationId` صريح، وأي `parentConversationCandidates`.
عندما تعيد `parentConversationCandidates`، فاحرص على ترتيبها من
الأصل الأضيق إلى المحادثة الأساسية/الأوسع.

يمكن أيضًا لـ plugins المضمّنة التي تحتاج إلى التحليل نفسه قبل إقلاع سجل القنوات
أن تعرض ملف `session-key-api.ts` أعلى المستوى مع
تصدير `resolveSessionConversation(...)` مطابق. تستخدم النواة هذا السطح الآمن
للتمهيد فقط عندما لا يكون سجل plugin وقت التشغيل متاحًا بعد.

يبقى `messaging.resolveParentConversationCandidates(...)` متاحًا كبديل
توافقي قديم عندما تحتاج plugin فقط إلى بدائل الأصل فوق
المعرّف العام/الخام. وإذا وُجد كلا المدخلين، تستخدم النواة
`resolveSessionConversation(...).parentConversationCandidates` أولًا ولا
تعود إلى `resolveParentConversationCandidates(...)` إلا عندما يحذفها
المدخل القياسي.

## الموافقات وإمكانات القناة

معظم plugins القنوات لا تحتاج إلى شيفرة خاصة بالموافقات.

- تمتلك النواة `/approve` في الدردشة نفسها، وحمولات أزرار الموافقة المشتركة، والتسليم الاحتياطي العام.
- فضّل كائن `approvalCapability` واحدًا على plugin القناة عندما تحتاج القناة إلى سلوك خاص بالموافقات.
- يمثّل `approvalCapability.authorizeActorAction` و`approvalCapability.getActionAvailabilityState` مدخل التفويض القياسي للموافقات.
- إذا كانت قناتك تعرض موافقات exec أصلية، فنفّذ `approvalCapability.getActionAvailabilityState` حتى عندما تعيش وسيلة النقل الأصلية بالكامل تحت `approvalCapability.native`. تستخدم النواة هذا المدخل الخاص بالتوافر للتمييز بين `enabled` و`disabled`، وتقرير ما إذا كانت القناة البادئة تدعم الموافقات الأصلية، وتضمين القناة في إرشادات fallback الخاصة بالعميل الأصلي.
- استخدم `outbound.shouldSuppressLocalPayloadPrompt` أو `outbound.beforeDeliverPayload` لسلوك دورة حياة الحمولات الخاص بالقناة مثل إخفاء مطالبات الموافقة المحلية المكررة أو إرسال مؤشرات الكتابة قبل التسليم.
- استخدم `approvalCapability.delivery` فقط للتوجيه الأصلي للموافقات أو كبت fallback.
- استخدم `approvalCapability.render` فقط عندما تحتاج القناة فعلًا إلى حمولات موافقة مخصصة بدلًا من المصيّر المشترك.
- استخدم `approvalCapability.describeExecApprovalSetup` عندما تريد القناة أن يشرح رد المسار المعطّل مفاتيح التهيئة الدقيقة المطلوبة لتمكين موافقات exec الأصلية. يتلقى المدخل `{ channel, channelLabel, accountId }`؛ ويجب على القنوات ذات الحسابات المسماة عرض مسارات بنطاق الحساب مثل `channels.<channel>.accounts.<id>.execApprovals.*` بدلًا من القيم الافتراضية على المستوى الأعلى.
- إذا كانت القناة تستطيع استنتاج هويات رسائل خاصة ثابتة شبيهة بالمالك من التهيئة الحالية، فاستخدم `createResolvedApproverActionAuthAdapter` من `openclaw/plugin-sdk/approval-runtime` لتقييد `/approve` في الدردشة نفسها دون إضافة منطق خاص بالموافقات إلى النواة.
- إذا كانت القناة تحتاج إلى تسليم موافقات أصلية، فأبقِ شيفرة القناة مركزة على تطبيع الهدف ومدخلات وسيلة النقل. استخدم `createChannelExecApprovalProfile` و`createChannelNativeOriginTargetResolver` و`createChannelApproverDmTargetResolver` و`createApproverRestrictedNativeApprovalCapability` و`createChannelNativeApprovalRuntime` من `openclaw/plugin-sdk/approval-runtime` حتى تمتلك النواة تصفية الطلبات والتوجيه وإزالة التكرار والانتهاء والاشتراك في البوابة.
- يجب على قنوات الموافقات الأصلية تمرير كل من `accountId` و`approvalKind` عبر هذه المساعدات. يحافظ `accountId` على تقييد سياسة الموافقات متعددة الحسابات بنطاق حساب الروبوت الصحيح، ويحافظ `approvalKind` على إتاحة سلوك exec مقابل plugin للقناة دون فروع ثابتة في النواة.
- حافظ على نوع معرّف الموافقة المُسلَّم من البداية إلى النهاية. يجب على العملاء الأصليين ألا
  يخمّنوا أو يعيدوا كتابة توجيه موافقات exec مقابل plugin اعتمادًا على حالة محلية في القناة.
- يمكن لأنواع الموافقات المختلفة أن تعرض عمدًا أسطحًا أصلية مختلفة.
  أمثلة مضمّنة حالية:
  - يحتفظ Slack بإتاحة توجيه الموافقات الأصلية لكل من معرّفات exec وplugin.
  - يحتفظ Matrix بتوجيه الرسائل الخاصة/القنوات الأصلي لموافقات exec فقط ويترك
    موافقات plugin على مسار `/approve` المشترك داخل الدردشة نفسها.
- ما يزال `createApproverRestrictedNativeApprovalAdapter` موجودًا كغلاف توافق، لكن الشيفرة الجديدة يجب أن تفضّل باني الإمكانات وتعرض `approvalCapability` على plugin.

بالنسبة إلى نقاط دخول القنوات الساخنة، فضّل المسارات الفرعية الأضيق وقت التشغيل عندما تحتاج
إلى جزء واحد فقط من هذه المجموعة:

- `openclaw/plugin-sdk/approval-auth-runtime`
- `openclaw/plugin-sdk/approval-client-runtime`
- `openclaw/plugin-sdk/approval-delivery-runtime`
- `openclaw/plugin-sdk/approval-native-runtime`
- `openclaw/plugin-sdk/approval-reply-runtime`

وبالمثل، فضّل `openclaw/plugin-sdk/setup-runtime`،
و`openclaw/plugin-sdk/setup-adapter-runtime`،
و`openclaw/plugin-sdk/reply-runtime`،
و`openclaw/plugin-sdk/reply-dispatch-runtime`،
و`openclaw/plugin-sdk/reply-reference`، و
`openclaw/plugin-sdk/reply-chunking` عندما لا تحتاج إلى السطح
الأوسع المظلّي.

وبالنسبة إلى الإعداد تحديدًا:

- يغطي `openclaw/plugin-sdk/setup-runtime` مساعدات الإعداد الآمنة لوقت التشغيل:
  محولات رقع الإعداد الآمنة للاستيراد (`createPatchedAccountSetupAdapter`,
  `createEnvPatchedAccountSetupAdapter`,
  `createSetupInputPresenceValidator`)، ومخرجات ملاحظات البحث،
  و`promptResolvedAllowFrom`، و`splitSetupEntries`، وبناة
  proxy الإعداد المفوّض
- يمثّل `openclaw/plugin-sdk/setup-adapter-runtime`
  مدخل المحول الضيق الواعي بمتغيرات البيئة لـ `createEnvPatchedAccountSetupAdapter`
- يغطي `openclaw/plugin-sdk/channel-setup` بناة الإعداد ذي التثبيت الاختياري
  بالإضافة إلى بعض الأوليات الآمنة للإعداد:
  `createOptionalChannelSetupSurface`، و`createOptionalChannelSetupAdapter`،

إذا كانت قناتك تدعم إعدادًا أو مصادقة مدفوعين بمتغيرات البيئة ويجب أن تعرف
تدفقات بدء التشغيل/التهيئة العامة أسماء متغيرات البيئة تلك قبل تحميل وقت التشغيل،
فصرّح بها في manifest الخاص بـ plugin باستخدام `channelEnvVars`. واحتفظ
بـ `envVars` وقت تشغيل القناة أو الثوابت المحلية لنسخة المشغّل فقط.
`createOptionalChannelSetupWizard`، و`DEFAULT_ACCOUNT_ID`،
و`createTopLevelChannelDmPolicy`، و`setSetupChannelEnabled`، و
`splitSetupEntries`

- استخدم المدخل الأوسع `openclaw/plugin-sdk/setup` فقط عندما تحتاج أيضًا إلى
  مساعدات الإعداد/التهيئة المشتركة الأثقل مثل
  `moveSingleAccountChannelSectionToDefaultAccount(...)`

إذا كانت قناتك تريد فقط الإعلان عن "ثبّت هذه plugin أولًا" في أسطح الإعداد،
ففضّل `createOptionalChannelSetupSurface(...)`. يفشل
المحول/المعالج المولدان إغلاقًا على كتابات التهيئة والإنهاء، ويعيدان استخدام
رسالة "التثبيت مطلوب" نفسها عبر التحقق والإنهاء ونسخة روابط المستندات.

وبالنسبة إلى المسارات الساخنة الأخرى للقناة، فضّل المساعدات الضيقة على الأسطح القديمة الأوسع:

- `openclaw/plugin-sdk/account-core`،
  و`openclaw/plugin-sdk/account-id`،
  و`openclaw/plugin-sdk/account-resolution`، و
  `openclaw/plugin-sdk/account-helpers` للتهيئة متعددة الحسابات
  والرجوع إلى الحساب الافتراضي
- `openclaw/plugin-sdk/inbound-envelope` و
  `openclaw/plugin-sdk/inbound-reply-dispatch` لربط
  المسار/الظرف الوارد والتسجيل ثم الإرسال
- `openclaw/plugin-sdk/messaging-targets` لتحليل/مطابقة الأهداف
- `openclaw/plugin-sdk/outbound-media` و
  `openclaw/plugin-sdk/outbound-runtime` لتحميل الوسائط مع
  مفوّضي الهوية/الإرسال الصادر
- `openclaw/plugin-sdk/thread-bindings-runtime` لدورة حياة
  روابط سلاسل الرسائل وتسجيل المحول
- `openclaw/plugin-sdk/agent-media-payload` فقط عندما يكون
  تخطيط حقول حمولة الوكيل/الوسائط القديم لا يزال مطلوبًا
- `openclaw/plugin-sdk/telegram-command-config` لتطبيع
  الأوامر المخصصة في Telegram والتحقق من التكرار/التعارض وعقد
  تهيئة الأوامر المستقر في fallback

يمكن للقنوات التي تعتمد على المصادقة فقط أن تتوقف غالبًا عند المسار الافتراضي: تتعامل النواة مع الموافقات وتعرض plugin فقط إمكانات الصادر/المصادقة. ويجب على قنوات الموافقات الأصلية مثل Matrix وSlack وTelegram ووسائط الدردشة المخصصة استخدام المساعدات الأصلية المشتركة بدلًا من بناء دورة حياة الموافقات الخاصة بها.

## سياسة الذكر في الوارد

أبقِ التعامل مع الذكر في الرسائل الواردة مقسّمًا إلى طبقتين:

- جمع الأدلة المملوك لـ plugin
- تقييم السياسة المشتركة

استخدم `openclaw/plugin-sdk/channel-inbound` للطبقة المشتركة.

ملائم للمنطق المحلي في plugin:

- اكتشاف الرد على الروبوت
- اكتشاف الاقتباس من الروبوت
- فحوصات المشاركة في سلسلة الرسائل
- استبعاد رسائل الخدمة/النظام
- الذاكرات المخبئية الأصلية للمنصة اللازمة لإثبات مشاركة الروبوت

ملائم للمساعد المشترك:

- `requireMention`
- نتيجة الذكر الصريح
- allowlist الذكر الضمني
- تجاوز الأوامر
- قرار التخطي النهائي

التدفق المفضل:

1. احسب حقائق الذكر المحلية.
2. مرر هذه الحقائق إلى `resolveInboundMentionDecision({ facts, policy })`.
3. استخدم `decision.effectiveWasMentioned` و`decision.shouldBypassMention` و`decision.shouldSkip` في بوابة الوارد.

```typescript
import {
  implicitMentionKindWhen,
  matchesMentionWithExplicit,
  resolveInboundMentionDecision,
} from "openclaw/plugin-sdk/channel-inbound";

const mentionMatch = matchesMentionWithExplicit(text, {
  mentionRegexes,
  mentionPatterns,
});

const facts = {
  canDetectMention: true,
  wasMentioned: mentionMatch.matched,
  hasAnyMention: mentionMatch.hasExplicitMention,
  implicitMentionKinds: [
    ...implicitMentionKindWhen("reply_to_bot", isReplyToBot),
    ...implicitMentionKindWhen("quoted_bot", isQuoteOfBot),
  ],
};

const decision = resolveInboundMentionDecision({
  facts,
  policy: {
    isGroup,
    requireMention,
    allowedImplicitMentionKinds: requireExplicitMention ? [] : ["reply_to_bot", "quoted_bot"],
    allowTextCommands,
    hasControlCommand,
    commandAuthorized,
  },
});

if (decision.shouldSkip) return;
```

يكشف `api.runtime.channel.mentions` عن مساعدات الذكر المشتركة نفسها من أجل
plugins القنوات المضمّنة التي تعتمد بالفعل على حقن وقت التشغيل:

- `buildMentionRegexes`
- `matchesMentionPatterns`
- `matchesMentionWithExplicit`
- `implicitMentionKindWhen`
- `resolveInboundMentionDecision`

تبقى المساعدات الأقدم `resolveMentionGating*` على
`openclaw/plugin-sdk/channel-inbound` كتصديرات توافق فقط. ويجب أن تستخدم الشيفرة الجديدة
`resolveInboundMentionDecision({ facts, policy })`.

## الشرح العملي

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="الحزمة وmanifest">
    أنشئ ملفات plugin القياسية. الحقل `channel` في `package.json` هو
    ما يجعل هذه plugin قناة. وللاطلاع على سطح بيانات تعريف الحزمة الكامل،
    راجع [إعداد plugin والتهيئة](/ar/plugins/sdk-setup#openclawchannel):

    <CodeGroup>
    ```json package.json
    {
      "name": "@myorg/openclaw-acme-chat",
      "version": "1.0.0",
      "type": "module",
      "openclaw": {
        "extensions": ["./index.ts"],
        "setupEntry": "./setup-entry.ts",
        "channel": {
          "id": "acme-chat",
          "label": "Acme Chat",
          "blurb": "Connect OpenClaw to Acme Chat."
        }
      }
    }
    ```

    ```json openclaw.plugin.json
    {
      "id": "acme-chat",
      "kind": "channel",
      "channels": ["acme-chat"],
      "name": "Acme Chat",
      "description": "Acme Chat channel plugin",
      "configSchema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "acme-chat": {
            "type": "object",
            "properties": {
              "token": { "type": "string" },
              "allowFrom": {
                "type": "array",
                "items": { "type": "string" }
              }
            }
          }
        }
      }
    }
    ```
    </CodeGroup>

  </Step>

  <Step title="ابنِ كائن plugin القناة">
    تحتوي الواجهة `ChannelPlugin` على العديد من أسطح المحولات الاختيارية. ابدأ
    بالحد الأدنى — `id` و`setup` — ثم أضف المحولات عند الحاجة.

    أنشئ `src/channel.ts`:

    ```typescript src/channel.ts
    import {
      createChatChannelPlugin,
      createChannelPluginBase,
    } from "openclaw/plugin-sdk/channel-core";
    import type { OpenClawConfig } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatApi } from "./client.js"; // عميل API الخاص بمنصتك

    type ResolvedAccount = {
      accountId: string | null;
      token: string;
      allowFrom: string[];
      dmPolicy: string | undefined;
    };

    function resolveAccount(
      cfg: OpenClawConfig,
      accountId?: string | null,
    ): ResolvedAccount {
      const section = (cfg.channels as Record<string, any>)?.["acme-chat"];
      const token = section?.token;
      if (!token) throw new Error("acme-chat: token is required");
      return {
        accountId: accountId ?? null,
        token,
        allowFrom: section?.allowFrom ?? [],
        dmPolicy: section?.dmSecurity,
      };
    }

    export const acmeChatPlugin = createChatChannelPlugin<ResolvedAccount>({
      base: createChannelPluginBase({
        id: "acme-chat",
        setup: {
          resolveAccount,
          inspectAccount(cfg, accountId) {
            const section =
              (cfg.channels as Record<string, any>)?.["acme-chat"];
            return {
              enabled: Boolean(section?.token),
              configured: Boolean(section?.token),
              tokenStatus: section?.token ? "available" : "missing",
            };
          },
        },
      }),

      // أمان الرسائل الخاصة: من يمكنه مراسلة الروبوت
      security: {
        dm: {
          channelKey: "acme-chat",
          resolvePolicy: (account) => account.dmPolicy,
          resolveAllowFrom: (account) => account.allowFrom,
          defaultPolicy: "allowlist",
        },
      },

      // Pairing: تدفق الاعتماد لجهات الاتصال الجديدة في الرسائل الخاصة
      pairing: {
        text: {
          idLabel: "Acme Chat username",
          message: "Send this code to verify your identity:",
          notify: async ({ target, code }) => {
            await acmeChatApi.sendDm(target, `Pairing code: ${code}`);
          },
        },
      },

      // الترابط في السلاسل: كيفية تسليم الردود
      threading: { topLevelReplyToMode: "reply" },

      // الصادر: إرسال الرسائل إلى المنصة
      outbound: {
        attachedResults: {
          sendText: async (params) => {
            const result = await acmeChatApi.sendMessage(
              params.to,
              params.text,
            );
            return { messageId: result.id };
          },
        },
        base: {
          sendMedia: async (params) => {
            await acmeChatApi.sendFile(params.to, params.filePath);
          },
        },
      },
    });
    ```

    <Accordion title="ما الذي ينجزه createChatChannelPlugin من أجلك">
      بدلًا من تنفيذ واجهات المحولات منخفضة المستوى يدويًا، تمرر
      خيارات تصريحية ويقوم الباني بتركيبها:

      | الخيار | ما الذي يربطه |
      | --- | --- |
      | `security.dm` | محلّل أمان الرسائل الخاصة ضمن النطاق من حقول التهيئة |
      | `pairing.text` | تدفق pairing للرسائل الخاصة المعتمد على النص مع تبادل الرموز |
      | `threading` | محلّل وضع الرد (ثابت، أو ضمن نطاق الحساب، أو مخصص) |
      | `outbound.attachedResults` | دوال الإرسال التي تعيد بيانات تعريف النتيجة (معرّفات الرسائل) |

      يمكنك أيضًا تمرير كائنات محولات خام بدلًا من الخيارات التصريحية
      إذا كنت تحتاج إلى تحكم كامل.
    </Accordion>

  </Step>

  <Step title="اربط نقطة الدخول">
    أنشئ `index.ts`:

    ```typescript index.ts
    import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineChannelPluginEntry({
      id: "acme-chat",
      name: "Acme Chat",
      description: "Acme Chat channel plugin",
      plugin: acmeChatPlugin,
      registerCliMetadata(api) {
        api.registerCli(
          ({ program }) => {
            program
              .command("acme-chat")
              .description("Acme Chat management");
          },
          {
            descriptors: [
              {
                name: "acme-chat",
                description: "Acme Chat management",
                hasSubcommands: false,
              },
            ],
          },
        );
      },
      registerFull(api) {
        api.registerGatewayMethod(/* ... */);
      },
    });
    ```

    ضع واصفات CLI المملوكة للقناة في `registerCliMetadata(...)` حتى يتمكن OpenClaw
    من عرضها في المساعدة الجذرية دون تفعيل وقت تشغيل القناة الكامل،
    بينما تلتقط عمليات التحميل الكاملة العادية الواصفات نفسها لتسجيل الأوامر
    الفعلي. واحتفظ بـ `registerFull(...)` للأعمال الخاصة بوقت التشغيل فقط.
    إذا كان `registerFull(...)` يسجل أساليب RPC للبوابة، فاستخدم
    بادئة خاصة بـ plugin. تبقى نطاقات الإدارة الأساسية (`config.*`،
    و`exec.approvals.*`، و`wizard.*`، و`update.*`) محجوزة وتُحل دائمًا
    إلى `operator.admin`.
    يتعامل `defineChannelPluginEntry` مع تقسيم أوضاع التسجيل تلقائيًا. راجع
    [نقاط الدخول](/ar/plugins/sdk-entrypoints#definechannelpluginentry) لكل
    الخيارات.

  </Step>

  <Step title="أضف نقطة دخول للإعداد">
    أنشئ `setup-entry.ts` للتحميل الخفيف أثناء onboarding:

    ```typescript setup-entry.ts
    import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineSetupPluginEntry(acmeChatPlugin);
    ```

    يحمّل OpenClaw هذا بدلًا من نقطة الدخول الكاملة عندما تكون القناة معطلة
    أو غير مهيأة. وهو يتجنب سحب شيفرة وقت تشغيل ثقيلة أثناء تدفقات الإعداد.
    راجع [الإعداد والتهيئة](/ar/plugins/sdk-setup#setup-entry) للتفاصيل.

  </Step>

  <Step title="تعامل مع الرسائل الواردة">
    تحتاج plugin الخاصة بك إلى تلقي الرسائل من المنصة وإعادة توجيهها إلى
    OpenClaw. النمط المعتاد هو webhook يتحقق من الطلب
    ويرسله عبر معالج الوارد الخاص بقناتك:

    ```typescript
    registerFull(api) {
      api.registerHttpRoute({
        path: "/acme-chat/webhook",
        auth: "plugin", // مصادقة مُدارة بواسطة plugin (تحقق من التواقيع بنفسك)
        handler: async (req, res) => {
          const event = parseWebhookPayload(req);

          // يقوم معالج الوارد لديك بإرسال الرسالة إلى OpenClaw.
          // يعتمد الربط الدقيق على SDK الخاصة بمنصتك —
          // راجع مثالًا حقيقيًا في حزمة plugin Microsoft Teams أو Google Chat المضمّنة.
          await handleAcmeChatInbound(api, event);

          res.statusCode = 200;
          res.end("ok");
          return true;
        },
      });
    }
    ```

    <Note>
      التعامل مع الرسائل الواردة خاص بالقناة. كل plugin قناة تمتلك
      مسار الوارد الخاص بها. انظر إلى plugins القنوات المضمّنة
      (مثل حزمة plugin Microsoft Teams أو Google Chat) للاطلاع على أنماط حقيقية.
    </Note>

  </Step>

<a id="step-6-test"></a>
<Step title="الاختبار">
اكتب اختبارات موضوعة بجانب الشيفرة في `src/channel.test.ts`:

    ```typescript src/channel.test.ts
    import { describe, it, expect } from "vitest";
    import { acmeChatPlugin } from "./channel.js";

    describe("acme-chat plugin", () => {
      it("resolves account from config", () => {
        const cfg = {
          channels: {
            "acme-chat": { token: "test-token", allowFrom: ["user1"] },
          },
        } as any;
        const account = acmeChatPlugin.setup!.resolveAccount(cfg, undefined);
        expect(account.token).toBe("test-token");
      });

      it("inspects account without materializing secrets", () => {
        const cfg = {
          channels: { "acme-chat": { token: "test-token" } },
        } as any;
        const result = acmeChatPlugin.setup!.inspectAccount!(cfg, undefined);
        expect(result.configured).toBe(true);
        expect(result.tokenStatus).toBe("available");
      });

      it("reports missing config", () => {
        const cfg = { channels: {} } as any;
        const result = acmeChatPlugin.setup!.inspectAccount!(cfg, undefined);
        expect(result.configured).toBe(false);
      });
    });
    ```

    ```bash
    pnpm test -- <bundled-plugin-root>/acme-chat/
    ```

    وبالنسبة إلى مساعدات الاختبار المشتركة، راجع [الاختبار](/ar/plugins/sdk-testing).

  </Step>
</Steps>

## بنية الملفات

```
<bundled-plugin-root>/acme-chat/
├── package.json              # بيانات تعريف openclaw.channel
├── openclaw.plugin.json      # Manifest مع مخطط التهيئة
├── index.ts                  # defineChannelPluginEntry
├── setup-entry.ts            # defineSetupPluginEntry
├── api.ts                    # التصديرات العامة (اختياري)
├── runtime-api.ts            # تصديرات وقت التشغيل الداخلية (اختياري)
└── src/
    ├── channel.ts            # ChannelPlugin عبر createChatChannelPlugin
    ├── channel.test.ts       # الاختبارات
    ├── client.ts             # عميل API الخاص بالمنصة
    └── runtime.ts            # مخزن وقت التشغيل (إذا لزم)
```

## موضوعات متقدمة

<CardGroup cols={2}>
  <Card title="خيارات الترابط في السلاسل" icon="git-branch" href="/ar/plugins/sdk-entrypoints#registration-mode">
    أوضاع رد ثابتة، أو ضمن نطاق الحساب، أو مخصصة
  </Card>
  <Card title="تكامل أداة الرسائل" icon="puzzle" href="/ar/plugins/architecture#channel-plugins-and-the-shared-message-tool">
    describeMessageTool واكتشاف الإجراءات
  </Card>
  <Card title="تحليل الهدف" icon="crosshair" href="/ar/plugins/architecture#channel-target-resolution">
    inferTargetChatType وlooksLikeId وresolveTarget
  </Card>
  <Card title="مساعدات وقت التشغيل" icon="settings" href="/ar/plugins/sdk-runtime">
    TTS وSTT والوسائط وsubagent عبر api.runtime
  </Card>
</CardGroup>

<Note>
لا تزال بعض المداخل المساعدة المضمّنة موجودة لصيانة plugins المضمّنة
والتوافق. وهي ليست النمط الموصى به لـ plugins القنوات الجديدة؛
فضّل المسارات الفرعية العامة للقناة/الإعداد/الرد/وقت التشغيل من سطح SDK
المشترك ما لم تكن تصون عائلة plugin المضمّنة تلك مباشرة.
</Note>

## الخطوات التالية

- [Provider Plugins](/ar/plugins/sdk-provider-plugins) — إذا كانت plugin الخاصة بك توفر النماذج أيضًا
- [نظرة عامة على SDK](/ar/plugins/sdk-overview) — المرجع الكامل لاستيرادات المسارات الفرعية
- [اختبار SDK](/ar/plugins/sdk-testing) — أدوات الاختبار واختبارات العقود
- [Manifest الخاص بـ plugin](/ar/plugins/manifest) — مخطط manifest الكامل
