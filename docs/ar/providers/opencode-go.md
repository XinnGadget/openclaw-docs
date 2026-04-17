---
read_when:
    - تريد فهرس OpenCode Go
    - تحتاج إلى مراجع النماذج وقت التشغيل للنماذج المستضافة على Go
summary: استخدم فهرس OpenCode Go مع إعداد OpenCode المشترك
title: OpenCode Go
x-i18n:
    generated_at: "2026-04-12T23:32:09Z"
    model: gpt-5.4
    provider: openai
    source_hash: d1f0f182de81729616ccc19125d93ba0445de2349daf7067b52e8c15b9d3539c
    source_path: providers/opencode-go.md
    workflow: 15
---

# OpenCode Go

OpenCode Go هو فهرس Go ضمن [OpenCode](/ar/providers/opencode).
ويستخدم مفتاح `OPENCODE_API_KEY` نفسه الخاص بفهرس Zen، لكنه يحتفظ بمعرّف مزوّد
وقت التشغيل `opencode-go` حتى يبقى التوجيه لكل نموذج في المنبع صحيحًا.

| الخاصية         | القيمة                          |
| --------------- | ------------------------------- |
| مزوّد وقت التشغيل | `opencode-go`                   |
| المصادقة        | `OPENCODE_API_KEY`              |
| الإعداد الأب    | [OpenCode](/ar/providers/opencode) |

## النماذج المدعومة

| مرجع النموذج               | الاسم         |
| ------------------------- | ------------- |
| `opencode-go/kimi-k2.5`   | Kimi K2.5     |
| `opencode-go/glm-5`       | GLM 5         |
| `opencode-go/minimax-m2.5` | MiniMax M2.5 |

## البدء

<Tabs>
  <Tab title="تفاعلي">
    <Steps>
      <Step title="شغّل الإعداد الأولي">
        ```bash
        openclaw onboard --auth-choice opencode-go
        ```
      </Step>
      <Step title="اضبط نموذج Go كنموذج افتراضي">
        ```bash
        openclaw config set agents.defaults.model.primary "opencode-go/kimi-k2.5"
        ```
      </Step>
      <Step title="تحقق من توفر النماذج">
        ```bash
        openclaw models list --provider opencode-go
        ```
      </Step>
    </Steps>
  </Tab>

  <Tab title="غير تفاعلي">
    <Steps>
      <Step title="مرّر المفتاح مباشرة">
        ```bash
        openclaw onboard --opencode-go-api-key "$OPENCODE_API_KEY"
        ```
      </Step>
      <Step title="تحقق من توفر النماذج">
        ```bash
        openclaw models list --provider opencode-go
        ```
      </Step>
    </Steps>
  </Tab>
</Tabs>

## مثال على الإعداد

```json5
{
  env: { OPENCODE_API_KEY: "YOUR_API_KEY_HERE" }, // pragma: allowlist secret
  agents: { defaults: { model: { primary: "opencode-go/kimi-k2.5" } } },
}
```

## ملاحظات متقدمة

<AccordionGroup>
  <Accordion title="سلوك التوجيه">
    يتولى OpenClaw التوجيه لكل نموذج تلقائيًا عندما يستخدم مرجع النموذج
    `opencode-go/...`. ولا يلزم أي إعداد إضافي للمزوّد.
  </Accordion>

  <Accordion title="اصطلاح مرجع وقت التشغيل">
    تظل مراجع وقت التشغيل صريحة: `opencode/...` لـ Zen، و`opencode-go/...` لـ Go.
    وهذا يحافظ على صحة التوجيه لكل نموذج في المنبع عبر كلا الفهرسين.
  </Accordion>

  <Accordion title="بيانات الاعتماد المشتركة">
    يُستخدم مفتاح `OPENCODE_API_KEY` نفسه لكل من فهرسي Zen وGo. ويؤدي إدخال
    المفتاح أثناء الإعداد إلى تخزين بيانات الاعتماد لكلا مزوّدي وقت التشغيل.
  </Accordion>
</AccordionGroup>

<Tip>
راجع [OpenCode](/ar/providers/opencode) للحصول على نظرة عامة على الإعداد المشترك والمرجع الكامل
لفهرسي Zen وGo.
</Tip>

## ذو صلة

<CardGroup cols={2}>
  <Card title="OpenCode (الأصل)" href="/ar/providers/opencode" icon="server">
    الإعداد المشترك، ونظرة عامة على الفهرس، والملاحظات المتقدمة.
  </Card>
  <Card title="اختيار النموذج" href="/ar/concepts/model-providers" icon="layers">
    اختيار المزوّدين، ومراجع النماذج، وسلوك التبديل الاحتياطي.
  </Card>
</CardGroup>
