---
read_when:
    - تريد استخدام نماذج Anthropic في OpenClaw
summary: استخدم Anthropic Claude عبر مفاتيح API أو Claude CLI في OpenClaw
title: Anthropic
x-i18n:
    generated_at: "2026-04-12T23:29:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: 5e3dda5f98ade9d4c3841888103bfb43d59e075d358a701ed0ae3ffb8d5694a7
    source_path: providers/anthropic.md
    workflow: 15
---

# Anthropic (Claude)

تطوّر Anthropic عائلة نماذج **Claude**. يدعم OpenClaw مسارين للمصادقة:

- **مفتاح API** — وصول مباشر إلى Anthropic API مع فوترة بحسب الاستخدام (نماذج `anthropic/*`)
- **Claude CLI** — إعادة استخدام تسجيل دخول Claude CLI موجود على نفس المضيف

<Warning>
أبلغنا فريق Anthropic أن استخدام Claude CLI على نمط OpenClaw أصبح مسموحًا مجددًا، لذلك يتعامل
OpenClaw مع إعادة استخدام Claude CLI واستخدام `claude -p` على أنهما معتمدان ما لم
تنشر Anthropic سياسة جديدة.

بالنسبة لمضيفات Gateway طويلة العمر، تبقى مفاتيح Anthropic API هي المسار الإنتاجي
الأوضح والأكثر قابلية للتنبؤ.

مستندات Anthropic العامة الحالية:

- [مرجع Claude Code CLI](https://code.claude.com/docs/en/cli-reference)
- [نظرة عامة على Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview)
- [استخدام Claude Code مع خطة Pro أو Max](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- [استخدام Claude Code مع خطة Team أو Enterprise](https://support.anthropic.com/en/articles/11845131-using-claude-code-with-your-team-or-enterprise-plan/)
  </Warning>

## البدء

<Tabs>
  <Tab title="مفتاح API">
    **الأفضل لـ:** الوصول القياسي إلى API والفوترة بحسب الاستخدام.

    <Steps>
      <Step title="احصل على مفتاح API الخاص بك">
        أنشئ مفتاح API في [Anthropic Console](https://console.anthropic.com/).
      </Step>
      <Step title="شغّل الإعداد">
        ```bash
        openclaw onboard
        # choose: Anthropic API key
        ```

        أو مرّر المفتاح مباشرة:

        ```bash
        openclaw onboard --anthropic-api-key "$ANTHROPIC_API_KEY"
        ```
      </Step>
      <Step title="تحقق من أن النموذج متاح">
        ```bash
        openclaw models list --provider anthropic
        ```
      </Step>
    </Steps>

    ### مثال على الإعداد

    ```json5
    {
      env: { ANTHROPIC_API_KEY: "sk-ant-..." },
      agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
    }
    ```

  </Tab>

  <Tab title="Claude CLI">
    **الأفضل لـ:** إعادة استخدام تسجيل دخول Claude CLI موجود دون مفتاح API منفصل.

    <Steps>
      <Step title="تأكد من أن Claude CLI مثبّت ومسجّل الدخول">
        تحقّق باستخدام:

        ```bash
        claude --version
        ```
      </Step>
      <Step title="شغّل الإعداد">
        ```bash
        openclaw onboard
        # choose: Claude CLI
        ```

        يكتشف OpenClaw بيانات اعتماد Claude CLI الحالية ويعيد استخدامها.
      </Step>
      <Step title="تحقق من أن النموذج متاح">
        ```bash
        openclaw models list --provider anthropic
        ```
      </Step>
    </Steps>

    <Note>
    توجد تفاصيل الإعداد ووقت التشغيل لواجهة Claude CLI الخلفية في [CLI Backends](/ar/gateway/cli-backends).
    </Note>

    <Tip>
    إذا كنت تريد أوضح مسار للفوترة، فاستخدم مفتاح Anthropic API بدلًا من ذلك. يدعم OpenClaw أيضًا خيارات بنمط الاشتراك من [OpenAI Codex](/ar/providers/openai) و[Qwen Cloud](/ar/providers/qwen) و[MiniMax](/ar/providers/minimax) و[Z.AI / GLM](/ar/providers/glm).
    </Tip>

  </Tab>
</Tabs>

## إعدادات التفكير الافتراضية (Claude 4.6)

تستخدم نماذج Claude 4.6 افتراضيًا التفكير `adaptive` في OpenClaw عندما لا يتم تعيين مستوى تفكير صريح.

يمكنك التجاوز لكل رسالة باستخدام `/think:<level>` أو ضمن معلمات النموذج:

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { thinking: "adaptive" },
        },
      },
    },
  },
}
```

<Note>
مستندات Anthropic ذات الصلة:
- [Adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking)
- [Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)
</Note>

## التخزين المؤقت للموجّهات

يدعم OpenClaw ميزة التخزين المؤقت للموجّهات الخاصة بـ Anthropic لمصادقة مفتاح API.

| القيمة | مدة التخزين المؤقت | الوصف |
| ------------------- | -------------- | -------------------------------------- |
| `"short"` (الافتراضي) | 5 دقائق      | يُطبّق تلقائيًا لمصادقة مفتاح API |
| `"long"`            | ساعة واحدة         | تخزين مؤقت ممتد |
| `"none"`            | بلا تخزين مؤقت     | تعطيل التخزين المؤقت للموجّهات |

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" },
        },
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="تجاوزات التخزين المؤقت لكل وكيل">
    استخدم معلمات مستوى النموذج كأساس، ثم تجاوز وكلاء محددين عبر `agents.list[].params`:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "anthropic/claude-opus-4-6" },
          models: {
            "anthropic/claude-opus-4-6": {
              params: { cacheRetention: "long" },
            },
          },
        },
        list: [
          { id: "research", default: true },
          { id: "alerts", params: { cacheRetention: "none" } },
        ],
      },
    }
    ```

    ترتيب دمج الإعداد:

    1. `agents.defaults.models["provider/model"].params`
    2. `agents.list[].params` (مطابقة `id`، مع التجاوز حسب المفتاح)

    يتيح هذا لوكيل واحد الاحتفاظ بتخزين مؤقت طويل الأمد بينما يعطّل وكيل آخر على النموذج نفسه التخزين المؤقت للحركة المتدفقة أو منخفضة إعادة الاستخدام.

  </Accordion>

  <Accordion title="ملاحظات Claude على Bedrock">
    - تقبل نماذج Anthropic Claude على Bedrock (`amazon-bedrock/*anthropic.claude*`) تمرير `cacheRetention` عند ضبطه.
    - تُفرض قيمة `cacheRetention: "none"` وقت التشغيل على نماذج Bedrock غير التابعة لـ Anthropic.
    - تقوم الإعدادات الذكية الافتراضية لمفتاح API أيضًا بتهيئة `cacheRetention: "short"` لمراجع Claude-on-Bedrock عندما لا يتم تعيين قيمة صريحة.
  </Accordion>
</AccordionGroup>

## الإعداد المتقدم

<AccordionGroup>
  <Accordion title="الوضع السريع">
    يدعم مفتاح التبديل المشترك `/fast` في OpenClaw حركة Anthropic المباشرة (مفتاح API وOAuth إلى `api.anthropic.com`).

    | الأمر | يُطابق |
    |---------|---------|
    | `/fast on` | `service_tier: "auto"` |
    | `/fast off` | `service_tier: "standard_only"` |

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "anthropic/claude-sonnet-4-6": {
              params: { fastMode: true },
            },
          },
        },
      },
    }
    ```

    <Note>
    - لا يتم حقنه إلا لطلبات `api.anthropic.com` المباشرة. تترك مسارات الوكيل قيمة `service_tier` بدون تغيير.
    - تتجاوز معلمات `serviceTier` أو `service_tier` الصريحة `/fast` عند تعيينهما معًا.
    - في الحسابات التي لا تحتوي على سعة Priority Tier، قد تُحل القيمة `service_tier: "auto"` إلى `standard`.
    </Note>

  </Accordion>

  <Accordion title="فهم الوسائط (الصور وPDF)">
    يسجل Plugin Anthropic المضمّن فهم الصور وملفات PDF. يقوم OpenClaw
    بحل قدرات الوسائط تلقائيًا من مصادقة Anthropic المضبوطة — لا حاجة إلى
    إعداد إضافي.

    | الخاصية | القيمة |
    | -------------- | -------------------- |
    | النموذج الافتراضي  | `claude-opus-4-6`    |
    | الإدخال المدعوم | الصور، مستندات PDF |

    عند إرفاق صورة أو ملف PDF بمحادثة، يقوم OpenClaw تلقائيًا
    بتوجيهه عبر مزوّد فهم الوسائط الخاص بـ Anthropic.

  </Accordion>

  <Accordion title="نافذة سياق 1M (بيتا)">
    تخضع نافذة السياق 1M من Anthropic لبوابة بيتا. قم بتمكينها لكل نموذج:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "anthropic/claude-opus-4-6": {
              params: { context1m: true },
            },
          },
        },
      },
    }
    ```

    يطابق OpenClaw ذلك إلى `anthropic-beta: context-1m-2025-08-07` في الطلبات.

    <Warning>
    يتطلب هذا وصول السياق الطويل على بيانات اعتماد Anthropic الخاصة بك. تُرفض مصادقة الرموز القديمة (`sk-ant-oat-*`) لطلبات سياق 1M — ويسجل OpenClaw تحذيرًا ثم يعود إلى نافذة السياق القياسية.
    </Warning>

  </Accordion>
</AccordionGroup>

## استكشاف الأخطاء وإصلاحها

<AccordionGroup>
  <Accordion title="أخطاء 401 / أصبح الرمز غير صالح فجأة">
    قد تنتهي صلاحية مصادقة رموز Anthropic أو يتم سحبها. بالنسبة للإعدادات الجديدة، انتقل إلى مفتاح Anthropic API.
  </Accordion>

  <Accordion title='لم يتم العثور على مفتاح API للمزوّد "anthropic"'>
    المصادقة **لكل وكيل**. لا ترث الوكلاء الجدد مفاتيح الوكيل الرئيسي. أعد تشغيل الإعداد لهذا الوكيل، أو اضبط مفتاح API على مضيف Gateway، ثم تحقّق باستخدام `openclaw models status`.
  </Accordion>

  <Accordion title='لم يتم العثور على بيانات اعتماد للملف الشخصي "anthropic:default"'>
    شغّل `openclaw models status` لمعرفة ملف المصادقة الشخصي النشط. أعد تشغيل الإعداد، أو اضبط مفتاح API لمسار هذا الملف الشخصي.
  </Accordion>

  <Accordion title="لا يوجد ملف مصادقة شخصي متاح (الكل في فترة تهدئة)">
    تحقّق من `openclaw models status --json` لمعرفة `auth.unusableProfiles`. قد تكون فترات تهدئة حدود المعدل لدى Anthropic محصورة على مستوى النموذج، لذا قد يظل نموذج Anthropic شقيق قابلًا للاستخدام. أضف ملف Anthropic شخصيًا آخر أو انتظر انتهاء فترة التهدئة.
  </Accordion>
</AccordionGroup>

<Note>
مزيد من المساعدة: [استكشاف الأخطاء وإصلاحها](/ar/help/troubleshooting) و[الأسئلة الشائعة](/ar/help/faq).
</Note>

## ذو صلة

<CardGroup cols={2}>
  <Card title="اختيار النموذج" href="/ar/concepts/model-providers" icon="layers">
    اختيار المزوّدين ومراجع النماذج وسلوك التبديل الاحتياطي.
  </Card>
  <Card title="CLI backends" href="/ar/gateway/cli-backends" icon="terminal">
    إعداد الواجهة الخلفية لـ Claude CLI وتفاصيل وقت التشغيل.
  </Card>
  <Card title="Prompt caching" href="/ar/reference/prompt-caching" icon="database">
    كيفية عمل التخزين المؤقت للموجّهات عبر المزوّدين.
  </Card>
  <Card title="OAuth and auth" href="/ar/gateway/authentication" icon="key">
    تفاصيل المصادقة وقواعد إعادة استخدام بيانات الاعتماد.
  </Card>
</CardGroup>
