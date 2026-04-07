---
read_when:
    - تريد استخدام Arcee AI مع OpenClaw
    - تحتاج إلى متغير البيئة لمفتاح API أو خيار مصادقة CLI
summary: إعداد Arcee AI ‏(المصادقة + اختيار النموذج)
title: Arcee AI
x-i18n:
    generated_at: "2026-04-07T07:21:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: fb04909a708fec08dd2c8c863501b178f098bc4818eaebad38aea264157969d8
    source_path: providers/arcee.md
    workflow: 15
---

# Arcee AI

يوفر [Arcee AI](https://arcee.ai) وصولًا إلى عائلة Trinity من نماذج mixture-of-experts عبر API متوافق مع OpenAI. جميع نماذج Trinity مرخّصة بموجب Apache 2.0.

يمكن الوصول إلى نماذج Arcee AI مباشرة عبر منصة Arcee أو من خلال [OpenRouter](/ar/providers/openrouter).

- المزوّد: `arcee`
- المصادقة: `ARCEEAI_API_KEY` (مباشر) أو `OPENROUTER_API_KEY` (عبر OpenRouter)
- API: متوافق مع OpenAI
- Base URL: `https://api.arcee.ai/api/v1` (مباشر) أو `https://openrouter.ai/api/v1` (OpenRouter)

## البدء السريع

1. احصل على مفتاح API من [Arcee AI](https://chat.arcee.ai/) أو [OpenRouter](https://openrouter.ai/keys).

2. اضبط مفتاح API (مستحسن: خزّنه من أجل Gateway):

```bash
# Direct (Arcee platform)
openclaw onboard --auth-choice arceeai-api-key

# Via OpenRouter
openclaw onboard --auth-choice arceeai-openrouter
```

3. اضبط نموذجًا افتراضيًا:

```json5
{
  agents: {
    defaults: {
      model: { primary: "arcee/trinity-large-thinking" },
    },
  },
}
```

## مثال غير تفاعلي

```bash
# Direct (Arcee platform)
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice arceeai-api-key \
  --arceeai-api-key "$ARCEEAI_API_KEY"

# Via OpenRouter
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice arceeai-openrouter \
  --openrouter-api-key "$OPENROUTER_API_KEY"
```

## ملاحظة حول البيئة

إذا كان Gateway يعمل كخدمة daemon ‏(launchd/systemd)، فتأكد من أن `ARCEEAI_API_KEY`
(أو `OPENROUTER_API_KEY`) متاح لتلك العملية (على سبيل المثال في
`~/.openclaw/.env` أو عبر `env.shellEnv`).

## الكتالوج المضمّن

يشحن OpenClaw حاليًا كتالوج Arcee المضمّن التالي:

| Model ref                      | الاسم                  | الإدخال | السياق | التكلفة (إدخال/إخراج لكل 1M) | الملاحظات                                 |
| ------------------------------ | ---------------------- | ------- | ------ | ----------------------------- | ------------------------------------------ |
| `arcee/trinity-large-thinking` | Trinity Large Thinking | text    | 256K   | $0.25 / $0.90                 | النموذج الافتراضي؛ reasoning مفعّل        |
| `arcee/trinity-large-preview`  | Trinity Large Preview  | text    | 128K   | $0.25 / $1.00                 | عام الغرض؛ 400B params, 13B active         |
| `arcee/trinity-mini`           | Trinity Mini 26B       | text    | 128K   | $0.045 / $0.15                | سريع وفعّال من حيث التكلفة؛ function calling |

تعمل مراجع النماذج نفسها لكل من الإعداد المباشر وإعداد OpenRouter (على سبيل المثال `arcee/trinity-large-thinking`).

يضبط preset الخاص بـ onboarding القيمة `arcee/trinity-large-thinking` بوصفها النموذج الافتراضي.

## الميزات المدعومة

- Streaming
- استخدام الأدوات / function calling
- مخرجات مهيكلة (وضع JSON وJSON schema)
- التفكير الموسّع (Trinity Large Thinking)
