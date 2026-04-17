---
read_when:
    - تريد إعداد Perplexity كمزوّد للبحث على الويب
    - تحتاج إلى إعداد مفتاح API الخاص بـ Perplexity أو وكيل OpenRouter proxy
summary: إعداد مزوّد البحث على الويب Perplexity ‏(مفتاح API، أوضاع البحث، والتصفية)
title: Perplexity
x-i18n:
    generated_at: "2026-04-12T23:32:24Z"
    model: gpt-5.4
    provider: openai
    source_hash: 55c089e96601ebe05480d305364272c7f0ac721caa79746297c73002a9f20f55
    source_path: providers/perplexity-provider.md
    workflow: 15
---

# Perplexity (مزوّد البحث على الويب)

يوفّر Plugin الخاص بـ Perplexity قدرات البحث على الويب من خلال
Perplexity Search API أو Perplexity Sonar عبر OpenRouter.

<Note>
تغطي هذه الصفحة إعداد **المزوّد** الخاص بـ Perplexity. أما **الأداة**
الخاصة بـ Perplexity (كيفية استخدام الوكيل لها)، فراجع [أداة Perplexity](/ar/tools/perplexity-search).
</Note>

| الخاصية      | القيمة                                                                 |
| ------------ | ---------------------------------------------------------------------- |
| النوع        | مزوّد بحث على الويب (وليس مزوّد نماذج)                                 |
| المصادقة     | `PERPLEXITY_API_KEY` ‏(مباشر) أو `OPENROUTER_API_KEY` ‏(عبر OpenRouter) |
| مسار الإعداد | `plugins.entries.perplexity.config.webSearch.apiKey`                   |

## البدء

<Steps>
  <Step title="تعيين مفتاح API">
    شغّل مسار الإعداد التفاعلي للبحث على الويب:

    ```bash
    openclaw configure --section web
    ```

    أو اضبط المفتاح مباشرةً:

    ```bash
    openclaw config set plugins.entries.perplexity.config.webSearch.apiKey "pplx-xxxxxxxxxxxx"
    ```

  </Step>
  <Step title="بدء البحث">
    سيستخدم الوكيل Perplexity تلقائيًا لعمليات البحث على الويب بمجرد
    إعداد المفتاح. ولا يلزم اتخاذ أي خطوات إضافية.
  </Step>
</Steps>

## أوضاع البحث

يختار Plugin النقل تلقائيًا استنادًا إلى بادئة مفتاح API:

<Tabs>
  <Tab title="واجهة Perplexity API الأصلية (pplx-)">
    عندما يبدأ المفتاح لديك بـ `pplx-`، يستخدم OpenClaw واجهة
    Perplexity Search API الأصلية. يعيد هذا النقل نتائج منظمة ويدعم
    عوامل تصفية النطاق واللغة والتاريخ (راجع خيارات التصفية أدناه).
  </Tab>
  <Tab title="OpenRouter / Sonar ‏(sk-or-)">
    عندما يبدأ المفتاح لديك بـ `sk-or-`، يوجّه OpenClaw الطلبات عبر OpenRouter باستخدام
    نموذج Perplexity Sonar. يعيد هذا النقل إجابات مُركّبة بالذكاء الاصطناعي مع
    استشهادات.
  </Tab>
</Tabs>

| بادئة المفتاح | النقل                         | الميزات                                            |
| ------------- | ----------------------------- | -------------------------------------------------- |
| `pplx-`       | Perplexity Search API الأصلية | نتائج منظمة، وعوامل تصفية للنطاق/اللغة/التاريخ     |
| `sk-or-`      | OpenRouter ‏(Sonar)           | إجابات مُركّبة بالذكاء الاصطناعي مع استشهادات       |

## التصفية في API الأصلية

<Note>
تتوفر خيارات التصفية فقط عند استخدام واجهة Perplexity API الأصلية
(مفتاح `pplx-`). ولا تدعم عمليات بحث OpenRouter/Sonar هذه المعلمات.
</Note>

عند استخدام واجهة Perplexity API الأصلية، تدعم عمليات البحث عوامل التصفية التالية:

| عامل التصفية   | الوصف                                  | المثال                            |
| -------------- | -------------------------------------- | --------------------------------- |
| البلد          | رمز بلد مكوّن من حرفين                 | `us` و`de` و`jp`                  |
| اللغة          | رمز لغة ISO 639-1                      | `en` و`fr` و`zh`                  |
| النطاق الزمني  | نافذة الحداثة الزمنية                  | `day` و`week` و`month` و`year`    |
| عوامل تصفية النطاق | قائمة سماح أو قائمة رفض (بحد أقصى 20 نطاقًا) | `example.com`                     |
| ميزانية المحتوى | حدود الرموز لكل استجابة / لكل صفحة     | `max_tokens` و`max_tokens_per_page` |

## ملاحظات متقدمة

<AccordionGroup>
  <Accordion title="متغير البيئة لعمليات daemon">
    إذا كان OpenClaw Gateway يعمل كخدمة daemon ‏(launchd/systemd)، فتأكد من أن
    `PERPLEXITY_API_KEY` متاح لتلك العملية.

    <Warning>
    المفتاح الذي يتم ضبطه فقط في `~/.profile` لن يكون مرئيًا لخدمة daemon تعمل عبر launchd/systemd
    ما لم يتم استيراد تلك البيئة صراحةً. اضبط المفتاح في
    `~/.openclaw/.env` أو عبر `env.shellEnv` لضمان أن تتمكن عملية gateway من
    قراءته.
    </Warning>

  </Accordion>

  <Accordion title="إعداد وكيل OpenRouter proxy">
    إذا كنت تفضل توجيه عمليات بحث Perplexity عبر OpenRouter، فاضبط
    `OPENROUTER_API_KEY` ‏(بالبادئة `sk-or-`) بدلًا من مفتاح Perplexity أصلي.
    سيكتشف OpenClaw البادئة وينتقل إلى نقل Sonar
    تلقائيًا.

    <Tip>
    يكون نقل OpenRouter مفيدًا إذا كان لديك بالفعل حساب OpenRouter
    وتريد فوترة موحدة عبر عدة مزوّدين.
    </Tip>

  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="أداة البحث Perplexity" href="/ar/tools/perplexity-search" icon="magnifying-glass">
    كيفية استدعاء الوكيل لعمليات بحث Perplexity وتفسير النتائج.
  </Card>
  <Card title="مرجع الإعدادات" href="/ar/gateway/configuration-reference" icon="gear">
    مرجع الإعدادات الكامل بما في ذلك إدخالات Plugin.
  </Card>
</CardGroup>
