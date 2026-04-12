---
read_when:
    - تريد استخدام GitHub Copilot كمزوّد نماذج
    - تحتاج إلى تدفق `openclaw models auth login-github-copilot`
summary: سجّل الدخول إلى GitHub Copilot من OpenClaw باستخدام تدفق الجهاز
title: GitHub Copilot
x-i18n:
    generated_at: "2026-04-12T23:30:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: 51fee006e7d4e78e37b0c29356b0090b132de727d99b603441767d3fb642140b
    source_path: providers/github-copilot.md
    workflow: 15
---

# GitHub Copilot

GitHub Copilot هو مساعد GitHub للبرمجة بالذكاء الاصطناعي. ويوفر الوصول إلى نماذج
Copilot لحساب GitHub الخاص بك وخطتك. ويمكن لـ OpenClaw استخدام Copilot كمزوّد نماذج
بطريقتين مختلفتين.

## طريقتان لاستخدام Copilot في OpenClaw

<Tabs>
  <Tab title="المزوّد المدمج (github-copilot)">
    استخدم تدفق تسجيل الدخول الأصلي عبر الجهاز للحصول على رمز GitHub، ثم استبدله
    برموز Copilot API عند تشغيل OpenClaw. هذا هو المسار **الافتراضي** والأبسط
    لأنه لا يتطلب VS Code.

    <Steps>
      <Step title="تشغيل أمر تسجيل الدخول">
        ```bash
        openclaw models auth login-github-copilot
        ```

        سيُطلب منك زيارة عنوان URL وإدخال رمز لمرة واحدة. أبقِ
        الطرفية مفتوحة حتى تكتمل العملية.
      </Step>
      <Step title="تعيين نموذج افتراضي">
        ```bash
        openclaw models set github-copilot/gpt-4o
        ```

        أو في الإعدادات:

        ```json5
        {
          agents: { defaults: { model: { primary: "github-copilot/gpt-4o" } } },
        }
        ```
      </Step>
    </Steps>

  </Tab>

  <Tab title="Plugin Copilot Proxy ‏(copilot-proxy)">
    استخدم إضافة VS Code **Copilot Proxy** كجسر محلي. يتواصل OpenClaw مع
    نقطة النهاية `/v1` الخاصة بالوكيل ويستخدم قائمة النماذج التي تضبطها هناك.

    <Note>
    اختر هذا عندما تكون تشغّل Copilot Proxy بالفعل في VS Code أو تحتاج إلى التوجيه
    من خلاله. يجب عليك تفعيل Plugin والإبقاء على إضافة VS Code قيد التشغيل.
    </Note>

  </Tab>
</Tabs>

## الأعلام الاختيارية

| العلم           | الوصف                                              |
| --------------- | -------------------------------------------------- |
| `--yes`         | تخطي مطالبة التأكيد                                |
| `--set-default` | تطبيق النموذج الافتراضي الموصى به من المزوّد أيضًا |

```bash
# تخطي التأكيد
openclaw models auth login-github-copilot --yes

# تسجيل الدخول وتعيين النموذج الافتراضي في خطوة واحدة
openclaw models auth login --provider github-copilot --method device --set-default
```

<AccordionGroup>
  <Accordion title="مطلوب TTY تفاعلي">
    يتطلب تدفق تسجيل الدخول عبر الجهاز TTY تفاعليًا. شغّله مباشرةً في
    طرفية، وليس في سكربت غير تفاعلي أو ضمن مسار CI.
  </Accordion>

  <Accordion title="يعتمد توفر النماذج على خطتك">
    يعتمد توفر نماذج Copilot على خطة GitHub الخاصة بك. إذا تم
    رفض نموذج، فجرّب معرّفًا آخر (على سبيل المثال `github-copilot/gpt-4.1`).
  </Accordion>

  <Accordion title="اختيار النقل">
    تستخدم معرّفات نماذج Claude نقل Anthropic Messages تلقائيًا. أما نماذج GPT
    وسلسلة o وGemini فتبقي على نقل OpenAI Responses. ويختار OpenClaw
    النقل الصحيح استنادًا إلى مرجع النموذج.
  </Accordion>

  <Accordion title="ترتيب أولوية حل متغيرات البيئة">
    يحل OpenClaw مصادقة Copilot من متغيرات البيئة وفق
    ترتيب الأولوية التالي:

    | الأولوية | المتغير               | ملاحظات                                |
    | -------- | --------------------- | -------------------------------------- |
    | 1        | `COPILOT_GITHUB_TOKEN` | أعلى أولوية، ومخصص لـ Copilot           |
    | 2        | `GH_TOKEN`            | رمز GitHub CLI ‏(احتياطي)              |
    | 3        | `GITHUB_TOKEN`        | رمز GitHub القياسي (أدنى أولوية)       |

    عند ضبط عدة متغيرات، يستخدم OpenClaw المتغير الأعلى أولوية.
    يخزّن تدفق تسجيل الدخول عبر الجهاز (`openclaw models auth login-github-copilot`)
    رمزه في مخزن ملفات تعريف المصادقة، وتكون له أولوية على جميع
    متغيرات البيئة.

  </Accordion>

  <Accordion title="تخزين الرمز">
    يخزّن تسجيل الدخول رمز GitHub في مخزن ملفات تعريف المصادقة ويستبدله
    برمز Copilot API عند تشغيل OpenClaw. ولا تحتاج إلى إدارة
    الرمز يدويًا.
  </Accordion>
</AccordionGroup>

<Warning>
يتطلب TTY تفاعليًا. شغّل أمر تسجيل الدخول مباشرةً في طرفية، وليس
داخل سكربت دون واجهة أو ضمن مهمة CI.
</Warning>

## ذو صلة

<CardGroup cols={2}>
  <Card title="اختيار النموذج" href="/ar/concepts/model-providers" icon="layers">
    اختيار المزوّدات ومراجع النماذج وسلوك التحويل الاحتياطي.
  </Card>
  <Card title="OAuth والمصادقة" href="/ar/gateway/authentication" icon="key">
    تفاصيل المصادقة وقواعد إعادة استخدام بيانات الاعتماد.
  </Card>
</CardGroup>
