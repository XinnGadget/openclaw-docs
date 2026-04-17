---
read_when:
    - تريد استخدام Groq مع OpenClaw
    - تحتاج إلى متغير البيئة الخاص بمفتاح API أو خيار المصادقة عبر CLI
summary: إعداد Groq (المصادقة + اختيار النموذج)
title: Groq
x-i18n:
    generated_at: "2026-04-12T23:30:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 613289efc36fedd002e1ebf9366e0e7119ea1f9e14a1dae773b90ea57100baee
    source_path: providers/groq.md
    workflow: 15
---

# Groq

توفّر [Groq](https://groq.com) استدلالًا فائق السرعة على النماذج مفتوحة المصدر
(Llama وGemma وMistral وغيرها) باستخدام عتاد LPU مخصص. ويتصل OpenClaw
بـ Groq عبر API المتوافق مع OpenAI.

| الخاصية | القيمة          |
| -------- | --------------- |
| الموفّر | `groq`          |
| المصادقة | `GROQ_API_KEY` |
| API      | متوافق مع OpenAI |

## البدء

<Steps>
  <Step title="Get an API key">
    أنشئ مفتاح API من [console.groq.com/keys](https://console.groq.com/keys).
  </Step>
  <Step title="Set the API key">
    ```bash
    export GROQ_API_KEY="gsk_..."
    ```
  </Step>
  <Step title="Set a default model">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "groq/llama-3.3-70b-versatile" },
        },
      },
    }
    ```
  </Step>
</Steps>

### مثال على ملف الإعداد

```json5
{
  env: { GROQ_API_KEY: "gsk_..." },
  agents: {
    defaults: {
      model: { primary: "groq/llama-3.3-70b-versatile" },
    },
  },
}
```

## النماذج المتاحة

يتغير فهرس نماذج Groq كثيرًا. شغّل `openclaw models list | grep groq`
لرؤية النماذج المتاحة حاليًا، أو راجع
[console.groq.com/docs/models](https://console.groq.com/docs/models).

| النموذج                       | ملاحظات                              |
| ---------------------------- | ------------------------------------ |
| **Llama 3.3 70B Versatile**  | للأغراض العامة، وسياق كبير            |
| **Llama 3.1 8B Instant**     | سريع وخفيف                           |
| **Gemma 2 9B**               | مدمج وفعّال                          |
| **Mixtral 8x7B**             | بنية MoE، واستدلال قوي               |

<Tip>
استخدم `openclaw models list --provider groq` للحصول على أحدث قائمة بالنماذج
المتاحة في حسابك.
</Tip>

## نسخ الصوت إلى نص

توفّر Groq أيضًا نسخًا سريعًا للصوت إلى نص بالاعتماد على Whisper. عند تهيئتها
كموفّر media-understanding، يستخدم OpenClaw نموذج Groq
`whisper-large-v3-turbo` لنسخ الرسائل الصوتية عبر واجهة
`tools.media.audio` المشتركة.

```json5
{
  tools: {
    media: {
      audio: {
        models: [{ provider: "groq" }],
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="Audio transcription details">
    | الخاصية | القيمة |
    |----------|-------|
    | مسار الإعداد المشترك | `tools.media.audio` |
    | Base URL الافتراضي   | `https://api.groq.com/openai/v1` |
    | النموذج الافتراضي    | `whisper-large-v3-turbo` |
    | نقطة نهاية API       | ‏`/audio/transcriptions` متوافقة مع OpenAI |
  </Accordion>

  <Accordion title="Environment note">
    إذا كان Gateway يعمل كخدمة daemon (`launchd/systemd`)، فتأكد من أن `GROQ_API_KEY`
    متاح لتلك العملية (على سبيل المثال، في `~/.openclaw/.env` أو عبر
    `env.shellEnv`).

    <Warning>
    المفاتيح المعيّنة فقط في بيئة shell التفاعلية ليست مرئية لعمليات Gateway
    المُدارة بواسطة daemon. استخدم `~/.openclaw/.env` أو إعداد `env.shellEnv`
    لضمان التوفر المستمر.
    </Warning>

  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="Model selection" href="/ar/concepts/model-providers" icon="layers">
    اختيار الموفّرات، ومراجع النماذج، وسلوك التبديل الاحتياطي.
  </Card>
  <Card title="Configuration reference" href="/ar/gateway/configuration-reference" icon="gear">
    مخطط الإعداد الكامل بما في ذلك إعدادات الموفّر والصوت.
  </Card>
  <Card title="Groq Console" href="https://console.groq.com" icon="arrow-up-right-from-square">
    لوحة تحكم Groq، ووثائق API، والأسعار.
  </Card>
  <Card title="Groq model list" href="https://console.groq.com/docs/models" icon="list">
    فهرس نماذج Groq الرسمي.
  </Card>
</CardGroup>
