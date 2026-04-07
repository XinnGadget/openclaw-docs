---
read_when:
    - تريد إنشاء plugin جديد لـ OpenClaw
    - تحتاج إلى دليل بدء سريع لتطوير plugin
    - تضيف قناة أو مزودًا أو أداة أو قدرة أخرى جديدة إلى OpenClaw
sidebarTitle: Getting Started
summary: أنشئ أول plugin لـ OpenClaw خلال دقائق
title: بناء Plugins
x-i18n:
    generated_at: "2026-04-07T07:19:17Z"
    model: gpt-5.4
    provider: openai
    source_hash: 509c1f5abe1a0a74966054ed79b71a1a7ee637a43b1214c424acfe62ddf48eef
    source_path: plugins/building-plugins.md
    workflow: 15
---

# بناء Plugins

توسّع Plugins قدرات OpenClaw بإمكانات جديدة: القنوات، وموفرو النماذج،
والكلام، والنسخ الفوري، والصوت الفوري، وفهم الوسائط، وتوليد
الصور، وتوليد الفيديو، وجلب الويب، والبحث على الويب، وأدوات الوكيل، أو أي
مزيج منها.

لا تحتاج إلى إضافة plugin الخاص بك إلى مستودع OpenClaw. انشره على
[ClawHub](/ar/tools/clawhub) أو npm وسيقوم المستخدمون بتثبيته باستخدام
`openclaw plugins install <package-name>`. يحاول OpenClaw استخدام ClawHub أولًا ثم
يرجع تلقائيًا إلى npm.

## المتطلبات الأساسية

- Node >= 22 ومدير حزم (npm أو pnpm)
- الإلمام بـ TypeScript ‏(ESM)
- بالنسبة إلى plugins داخل المستودع: يجب أن يكون المستودع مستنسخًا وقد تم تشغيل `pnpm install`

## ما نوع plugin الذي تريده؟

<CardGroup cols={3}>
  <Card title="Channel plugin" icon="messages-square" href="/ar/plugins/sdk-channel-plugins">
    وصّل OpenClaw بمنصة مراسلة (Discord وIRC وغيرهما)
  </Card>
  <Card title="Provider plugin" icon="cpu" href="/ar/plugins/sdk-provider-plugins">
    أضف مزود نماذج (LLM أو proxy أو endpoint مخصص)
  </Card>
  <Card title="Tool / hook plugin" icon="wrench">
    سجّل أدوات الوكيل أو event hooks أو الخدمات — تابع أدناه
  </Card>
</CardGroup>

إذا كان Channel plugin اختياريًا وقد لا يكون مثبتًا عند تشغيل
onboarding/setup، فاستخدم `createOptionalChannelSetupSurface(...)` من
`openclaw/plugin-sdk/channel-setup`. فهو ينتج setup adapter + wizard
يعلن عن متطلب التثبيت ويفشل بشكل مغلق عند محاولات كتابة الإعدادات الفعلية
إلى أن يتم تثبيت plugin.

## بدء سريع: Tool plugin

ينشئ هذا الدليل plugin بسيطًا يسجل أداة وكيل. أما Channel plugins
وProvider plugins فلها أدلة مخصصة مرتبطة أعلاه.

<Steps>
  <Step title="أنشئ الحزمة وmanifest">
    <CodeGroup>
    ```json package.json
    {
      "name": "@myorg/openclaw-my-plugin",
      "version": "1.0.0",
      "type": "module",
      "openclaw": {
        "extensions": ["./index.ts"],
        "compat": {
          "pluginApi": ">=2026.3.24-beta.2",
          "minGatewayVersion": "2026.3.24-beta.2"
        },
        "build": {
          "openclawVersion": "2026.3.24-beta.2",
          "pluginSdkVersion": "2026.3.24-beta.2"
        }
      }
    }
    ```

    ```json openclaw.plugin.json
    {
      "id": "my-plugin",
      "name": "My Plugin",
      "description": "Adds a custom tool to OpenClaw",
      "configSchema": {
        "type": "object",
        "additionalProperties": false
      }
    }
    ```
    </CodeGroup>

    يحتاج كل plugin إلى manifest، حتى من دون إعدادات. راجع
    [Manifest](/ar/plugins/manifest) للاطلاع على المخطط الكامل. وتوجد مقتطفات النشر
    القياسية الخاصة بـ ClawHub في `docs/snippets/plugin-publish/`.

  </Step>

  <Step title="اكتب نقطة الإدخال">

    ```typescript
    // index.ts
    import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
    import { Type } from "@sinclair/typebox";

    export default definePluginEntry({
      id: "my-plugin",
      name: "My Plugin",
      description: "Adds a custom tool to OpenClaw",
      register(api) {
        api.registerTool({
          name: "my_tool",
          description: "Do a thing",
          parameters: Type.Object({ input: Type.String() }),
          async execute(_id, params) {
            return { content: [{ type: "text", text: `Got: ${params.input}` }] };
          },
        });
      },
    });
    ```

    يُستخدم `definePluginEntry` للـ plugins غير الخاصة بالقنوات. أما القنوات فاستخدم
    `defineChannelPluginEntry` — راجع [Channel Plugins](/ar/plugins/sdk-channel-plugins).
    وللاطلاع على الخيارات الكاملة لنقطة الإدخال، راجع [Entry Points](/ar/plugins/sdk-entrypoints).

  </Step>

  <Step title="اختبر وانشر">

    **Plugins الخارجية:** تحقّق وانشر باستخدام ClawHub، ثم ثبّت:

    ```bash
    clawhub package publish your-org/your-plugin --dry-run
    clawhub package publish your-org/your-plugin
    openclaw plugins install clawhub:@myorg/openclaw-my-plugin
    ```

    يفحص OpenClaw أيضًا ClawHub قبل npm عند استخدام مواصفات حزم مجردة مثل
    `@myorg/openclaw-my-plugin`.

    **Plugins داخل المستودع:** ضَعها ضمن شجرة workspace الخاصة بالـ plugin المضمّن — سيتم اكتشافها تلقائيًا.

    ```bash
    pnpm test -- <bundled-plugin-root>/my-plugin/
    ```

  </Step>
</Steps>

## قدرات plugin

يمكن لـ plugin واحد تسجيل أي عدد من القدرات عبر الكائن `api`:

| القدرة | طريقة التسجيل | الدليل المفصل |
| ---------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------- |
| الاستدلال النصي (LLM) | `api.registerProvider(...)` | [Provider Plugins](/ar/plugins/sdk-provider-plugins) |
| CLI inference backend | `api.registerCliBackend(...)` | [CLI Backends](/ar/gateway/cli-backends) |
| القناة / المراسلة | `api.registerChannel(...)` | [Channel Plugins](/ar/plugins/sdk-channel-plugins) |
| الكلام (TTS/STT) | `api.registerSpeechProvider(...)` | [Provider Plugins](/ar/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| النسخ الفوري | `api.registerRealtimeTranscriptionProvider(...)` | [Provider Plugins](/ar/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| الصوت الفوري | `api.registerRealtimeVoiceProvider(...)` | [Provider Plugins](/ar/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| فهم الوسائط | `api.registerMediaUnderstandingProvider(...)` | [Provider Plugins](/ar/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| توليد الصور | `api.registerImageGenerationProvider(...)` | [Provider Plugins](/ar/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| توليد الموسيقى | `api.registerMusicGenerationProvider(...)` | [Provider Plugins](/ar/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| توليد الفيديو | `api.registerVideoGenerationProvider(...)` | [Provider Plugins](/ar/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| جلب الويب | `api.registerWebFetchProvider(...)` | [Provider Plugins](/ar/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| البحث على الويب | `api.registerWebSearchProvider(...)` | [Provider Plugins](/ar/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| أدوات الوكيل | `api.registerTool(...)` | أدناه |
| أوامر مخصصة | `api.registerCommand(...)` | [Entry Points](/ar/plugins/sdk-entrypoints) |
| Event hooks | `api.registerHook(...)` | [Entry Points](/ar/plugins/sdk-entrypoints) |
| مسارات HTTP | `api.registerHttpRoute(...)` | [Internals](/ar/plugins/architecture#gateway-http-routes) |
| أوامر CLI فرعية | `api.registerCli(...)` | [Entry Points](/ar/plugins/sdk-entrypoints) |

للاطلاع على API التسجيل الكامل، راجع [نظرة عامة على SDK](/ar/plugins/sdk-overview#registration-api).

إذا كان plugin الخاص بك يسجل أساليب Gateway RPC مخصصة، فاحتفظ بها ضمن
بادئة خاصة بـ plugin. تظل مساحات أسماء الإدارة الأساسية (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) محجوزة وتُحل دائمًا إلى
`operator.admin`، حتى إذا طلب plugin نطاقًا أضيق.

دلالات حرس الـ hook التي يجب وضعها في الاعتبار:

- `before_tool_call`: ‏`{ block: true }` نهائية وتوقف المعالجات ذات الأولوية الأقل.
- `before_tool_call`: ‏`{ block: false }` تُعامل على أنها بدون قرار.
- `before_tool_call`: ‏`{ requireApproval: true }` توقف تنفيذ الوكيل مؤقتًا وتطلب موافقة المستخدم عبر طبقة exec approval، أو أزرار Telegram، أو تفاعلات Discord، أو الأمر `/approve` على أي قناة.
- `before_install`: ‏`{ block: true }` نهائية وتوقف المعالجات ذات الأولوية الأقل.
- `before_install`: ‏`{ block: false }` تُعامل على أنها بدون قرار.
- `message_sending`: ‏`{ cancel: true }` نهائية وتوقف المعالجات ذات الأولوية الأقل.
- `message_sending`: ‏`{ cancel: false }` تُعامل على أنها بدون قرار.

يعالج الأمر `/approve` كلًا من exec approvals وplugin approvals مع fallback
مقيّد: فعندما لا يتم العثور على معرّف exec approval، يعيد OpenClaw محاولة
المعرّف نفسه عبر plugin approvals. ويمكن ضبط تمرير plugin approval
بشكل مستقل عبر `approvals.plugin` في الإعدادات.

إذا كان من الضروري أن يكتشف منطق approval المخصص حالة fallback المقيّدة نفسها،
ففضّل استخدام `isApprovalNotFoundError` من `openclaw/plugin-sdk/error-runtime`
بدلًا من مطابقة سلاسل انتهاء صلاحية approval يدويًا.

راجع [دلالات قرارات hook في نظرة عامة على SDK](/ar/plugins/sdk-overview#hook-decision-semantics) للتفاصيل.

## تسجيل أدوات الوكيل

الأدوات هي دوال typed يمكن لـ LLM استدعاؤها. ويمكن أن تكون مطلوبة (متاحة
دائمًا) أو اختيارية (اشتراك من المستخدم):

```typescript
register(api) {
  // Required tool — always available
  api.registerTool({
    name: "my_tool",
    description: "Do a thing",
    parameters: Type.Object({ input: Type.String() }),
    async execute(_id, params) {
      return { content: [{ type: "text", text: params.input }] };
    },
  });

  // Optional tool — user must add to allowlist
  api.registerTool(
    {
      name: "workflow_tool",
      description: "Run a workflow",
      parameters: Type.Object({ pipeline: Type.String() }),
      async execute(_id, params) {
        return { content: [{ type: "text", text: params.pipeline }] };
      },
    },
    { optional: true },
  );
}
```

يفعّل المستخدمون الأدوات الاختيارية في الإعدادات:

```json5
{
  tools: { allow: ["workflow_tool"] },
}
```

- يجب ألا تتعارض أسماء الأدوات مع الأدوات الأساسية (يتم تخطي التعارضات)
- استخدم `optional: true` للأدوات ذات التأثيرات الجانبية أو متطلبات الملفات التنفيذية الإضافية
- يمكن للمستخدمين تفعيل جميع أدوات plugin عبر إضافة معرّف plugin إلى `tools.allow`

## اصطلاحات الاستيراد

استورد دائمًا من مسارات فرعية مركّزة `openclaw/plugin-sdk/<subpath>`:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";

// Wrong: monolithic root (deprecated, will be removed)
import { ... } from "openclaw/plugin-sdk";
```

للاطلاع على المرجع الكامل للمسارات الفرعية، راجع [نظرة عامة على SDK](/ar/plugins/sdk-overview).

داخل plugin الخاص بك، استخدم ملفات barrel محلية (`api.ts`, `runtime-api.ts`)
لعمليات الاستيراد الداخلية — ولا تستورد plugin الخاص بك أبدًا عبر مسار SDK الخاص به.

بالنسبة إلى Provider plugins، احتفظ بالمساعدات الخاصة بالمزود داخل ملفات
barrel الموجودة في جذر الحزمة ما لم تكن نقطة الربط عامة فعلًا. ومن الأمثلة
المضمنة الحالية:

- Anthropic: مغلفات تدفق Claude ومساعدات `service_tier` / beta
- OpenAI: بُناة المزودات، ومساعدات النماذج الافتراضية، ومزودات الوقت الفعلي
- OpenRouter: باني المزود بالإضافة إلى مساعدات onboarding/config

إذا كان المساعد مفيدًا فقط داخل حزمة مزود مضمّنة واحدة، فأبقِه ضمن
نقطة الربط الموجودة في جذر تلك الحزمة بدلًا من ترقيته إلى `openclaw/plugin-sdk/*`.

لا تزال بعض نقاط الربط المساعدة المولدة `openclaw/plugin-sdk/<bundled-id>` موجودة
لصيانة plugins المضمّنة والتوافق، مثل
`plugin-sdk/feishu-setup` أو `plugin-sdk/zalo-setup`. تعامل معها على أنها
أسطح محجوزة، وليست النمط الافتراضي لـ plugins الخارجية الجديدة.

## قائمة التحقق قبل الإرسال

<Check>يحتوي **package.json** على بيانات `openclaw` الوصفية الصحيحة</Check>
<Check>يوجد manifest **openclaw.plugin.json** وهو صالح</Check>
<Check>تستخدم نقطة الإدخال `defineChannelPluginEntry` أو `definePluginEntry`</Check>
<Check>تستخدم جميع عمليات الاستيراد مسارات مركّزة `plugin-sdk/<subpath>`</Check>
<Check>تستخدم عمليات الاستيراد الداخلية وحدات محلية، لا عمليات استيراد ذاتية عبر SDK</Check>
<Check>تجتاز الاختبارات (`pnpm test -- <bundled-plugin-root>/my-plugin/`)</Check>
<Check>يجتاز `pnpm check` (للـ plugins داخل المستودع)</Check>

## اختبار الإصدار التجريبي

1. راقب وسوم إصدارات GitHub على [openclaw/openclaw](https://github.com/openclaw/openclaw/releases) واشترك عبر `Watch` > `Releases`. تبدو الوسوم التجريبية مثل `v2026.3.N-beta.1`. ويمكنك أيضًا تفعيل الإشعارات للحساب الرسمي لـ OpenClaw على X ‏[@openclaw](https://x.com/openclaw) للإعلانات الخاصة بالإصدارات.
2. اختبر plugin الخاص بك مقابل الوسم التجريبي بمجرد ظهوره. وعادةً ما تكون النافذة قبل الإصدار المستقر بضع ساعات فقط.
3. انشر في سلسلة plugin الخاصة بك في قناة Discord ‏`plugin-forum` بعد الاختبار بإحدى العبارتين `all good` أو ما الذي تعطل. وإذا لم تكن لديك سلسلة بعد، فأنشئ واحدة.
4. إذا تعطل شيء ما، فافتح أو حدّث issue بعنوان `Beta blocker: <plugin-name> - <summary>` وطبّق الوسم `beta-blocker`. ضَع رابط issue في سلسلتك.
5. افتح PR إلى `main` بعنوان `fix(<plugin-id>): beta blocker - <summary>` واربط issue في كل من PR وسلسلة Discord الخاصة بك. لا يستطيع المساهمون إضافة وسوم إلى PRs، لذا فالعنوان هو الإشارة الخاصة بـ PR للمشرفين وللأتمتة. يتم دمج المشكلات الحرجة التي لها PR؛ أما التي لا تملك واحدًا فقد تُشحن على أي حال. يراقب المشرفون هذه السلاسل أثناء الاختبار التجريبي.
6. الصمت يعني أن كل شيء على ما يرام. وإذا فاتتك النافذة، فمن المرجح أن يصل إصلاحك في الدورة التالية.

## الخطوات التالية

<CardGroup cols={2}>
  <Card title="Channel Plugins" icon="messages-square" href="/ar/plugins/sdk-channel-plugins">
    ابنِ Channel plugin للمراسلة
  </Card>
  <Card title="Provider Plugins" icon="cpu" href="/ar/plugins/sdk-provider-plugins">
    ابنِ Provider plugin للنماذج
  </Card>
  <Card title="SDK Overview" icon="book-open" href="/ar/plugins/sdk-overview">
    مرجع خريطة الاستيراد وAPI التسجيل
  </Card>
  <Card title="Runtime Helpers" icon="settings" href="/ar/plugins/sdk-runtime">
    TTS والبحث وsubagent عبر api.runtime
  </Card>
  <Card title="Testing" icon="test-tubes" href="/ar/plugins/sdk-testing">
    أدوات وأنماط الاختبار
  </Card>
  <Card title="Plugin Manifest" icon="file-json" href="/ar/plugins/manifest">
    المرجع الكامل لمخطط manifest
  </Card>
</CardGroup>

## ذو صلة

- [بنية plugin](/ar/plugins/architecture) — نظرة عميقة على البنية الداخلية
- [نظرة عامة على SDK](/ar/plugins/sdk-overview) — مرجع Plugin SDK
- [Manifest](/ar/plugins/manifest) — تنسيق manifest الخاص بالـ plugin
- [Channel Plugins](/ar/plugins/sdk-channel-plugins) — بناء Channel plugins
- [Provider Plugins](/ar/plugins/sdk-provider-plugins) — بناء Provider plugins
