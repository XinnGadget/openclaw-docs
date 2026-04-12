---
read_when:
    - تريد استخدام نماذج OpenAI في OpenClaw
    - تريد مصادقة اشتراك Codex بدلًا من مفاتيح API
    - تحتاج إلى سلوك تنفيذ أكثر صرامة لوكيل GPT-5
summary: استخدم OpenAI عبر مفاتيح API أو اشتراك Codex في OpenClaw
title: OpenAI
x-i18n:
    generated_at: "2026-04-12T23:31:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6aeb756618c5611fed56e4bf89015a2304ff2e21596104b470ec6e7cb459d1c9
    source_path: providers/openai.md
    workflow: 15
---

# OpenAI

توفّر OpenAI واجهات API للمطورين لنماذج GPT. يدعم OpenClaw مسارين للمصادقة:

- **مفتاح API** — وصول مباشر إلى OpenAI Platform مع فوترة بحسب الاستخدام (نماذج `openai/*`)
- **اشتراك Codex** — تسجيل دخول ChatGPT/Codex مع وصول عبر الاشتراك (نماذج `openai-codex/*`)

تدعم OpenAI صراحةً استخدام OAuth للاشتراك في الأدوات وسير العمل الخارجية مثل OpenClaw.

## البدء

اختر طريقة المصادقة المفضلة لديك واتبع خطوات الإعداد.

<Tabs>
  <Tab title="مفتاح API ‏(OpenAI Platform)">
    **الأفضل لـ:** الوصول المباشر إلى API والفوترة بحسب الاستخدام.

    <Steps>
      <Step title="احصل على مفتاح API الخاص بك">
        أنشئ أو انسخ مفتاح API من [لوحة تحكم OpenAI Platform](https://platform.openai.com/api-keys).
      </Step>
      <Step title="شغّل الإعداد">
        ```bash
        openclaw onboard --auth-choice openai-api-key
        ```

        أو مرّر المفتاح مباشرة:

        ```bash
        openclaw onboard --openai-api-key "$OPENAI_API_KEY"
        ```
      </Step>
      <Step title="تحقق من أن النموذج متاح">
        ```bash
        openclaw models list --provider openai
        ```
      </Step>
    </Steps>

    ### ملخص المسار

    | مرجع النموذج | المسار | المصادقة |
    |-----------|-------|------|
    | `openai/gpt-5.4` | OpenAI Platform API المباشر | `OPENAI_API_KEY` |
    | `openai/gpt-5.4-pro` | OpenAI Platform API المباشر | `OPENAI_API_KEY` |

    <Note>
    يتم توجيه تسجيل دخول ChatGPT/Codex عبر `openai-codex/*` وليس `openai/*`.
    </Note>

    ### مثال على الإعداد

    ```json5
    {
      env: { OPENAI_API_KEY: "sk-..." },
      agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
    }
    ```

    <Warning>
    لا يوفّر OpenClaw **`openai/gpt-5.3-codex-spark`** على مسار API المباشر. إذ ترفض طلبات OpenAI API الحية هذا النموذج. إن Spark مخصص لـ Codex فقط.
    </Warning>

  </Tab>

  <Tab title="اشتراك Codex">
    **الأفضل لـ:** استخدام اشتراك ChatGPT/Codex الخاص بك بدلًا من مفتاح API منفصل. يتطلب Codex cloud تسجيل الدخول إلى ChatGPT.

    <Steps>
      <Step title="شغّل OAuth الخاص بـ Codex">
        ```bash
        openclaw onboard --auth-choice openai-codex
        ```

        أو شغّل OAuth مباشرة:

        ```bash
        openclaw models auth login --provider openai-codex
        ```
      </Step>
      <Step title="عيّن النموذج الافتراضي">
        ```bash
        openclaw config set agents.defaults.model.primary openai-codex/gpt-5.4
        ```
      </Step>
      <Step title="تحقق من أن النموذج متاح">
        ```bash
        openclaw models list --provider openai-codex
        ```
      </Step>
    </Steps>

    ### ملخص المسار

    | مرجع النموذج | المسار | المصادقة |
    |-----------|-------|------|
    | `openai-codex/gpt-5.4` | ChatGPT/Codex OAuth | تسجيل دخول Codex |
    | `openai-codex/gpt-5.3-codex-spark` | ChatGPT/Codex OAuth | تسجيل دخول Codex (بحسب الاستحقاق) |

    <Note>
    هذا المسار منفصل عمدًا عن `openai/gpt-5.4`. استخدم `openai/*` مع مفتاح API للوصول المباشر إلى Platform، واستخدم `openai-codex/*` للوصول عبر اشتراك Codex.
    </Note>

    ### مثال على الإعداد

    ```json5
    {
      agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
    }
    ```

    <Tip>
    إذا أعاد الإعداد استخدام تسجيل دخول موجود مسبقًا إلى Codex CLI، فستظل بيانات الاعتماد تلك مُدارة بواسطة Codex CLI. وعند انتهاء الصلاحية، يعيد OpenClaw قراءة مصدر Codex الخارجي أولًا ثم يكتب بيانات الاعتماد المحدّثة مرة أخرى إلى تخزين Codex.
    </Tip>

    ### حد نافذة السياق

    يتعامل OpenClaw مع بيانات تعريف النموذج وحد وقت التشغيل للسياق باعتبارهما قيمتين منفصلتين.

    بالنسبة إلى `openai-codex/gpt-5.4`:

    - القيمة الأصلية لـ `contextWindow`: `1050000`
    - الحد الافتراضي لـ `contextTokens` وقت التشغيل: `272000`

    يوفّر هذا الحد الافتراضي الأصغر خصائص أفضل من حيث الكمون والجودة عمليًا. يمكنك تجاوزه باستخدام `contextTokens`:

    ```json5
    {
      models: {
        providers: {
          "openai-codex": {
            models: [{ id: "gpt-5.4", contextTokens: 160000 }],
          },
        },
      },
    }
    ```

    <Note>
    استخدم `contextWindow` للتصريح ببيانات تعريف النموذج الأصلية. واستخدم `contextTokens` لتقييد ميزانية السياق وقت التشغيل.
    </Note>

  </Tab>
</Tabs>

## توليد الصور

يسجل Plugin ‏`openai` المضمّن توليد الصور عبر الأداة `image_generate`.

| الإمكانية                | القيمة                              |
| ------------------------- | ---------------------------------- |
| النموذج الافتراضي             | `openai/gpt-image-1`               |
| الحد الأقصى للصور لكل طلب    | 4                                  |
| وضع التحرير                 | مفعّل (حتى 5 صور مرجعية) |
| تجاوزات الحجم            | مدعومة                          |
| نسبة العرض إلى الارتفاع / الدقة | لا يتم تمريرها إلى OpenAI Images API |

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: { primary: "openai/gpt-image-1" },
    },
  },
}
```

<Note>
راجع [Image Generation](/ar/tools/image-generation) لمعلمات الأداة المشتركة، واختيار المزوّد، وسلوك التبديل الاحتياطي.
</Note>

## توليد الفيديو

يسجل Plugin ‏`openai` المضمّن توليد الفيديو عبر الأداة `video_generate`.

| الإمكانية       | القيمة                                                                             |
| ---------------- | --------------------------------------------------------------------------------- |
| النموذج الافتراضي    | `openai/sora-2`                                                                   |
| الأوضاع            | نص إلى فيديو، وصورة إلى فيديو، وتحرير فيديو واحد                                  |
| المدخلات المرجعية | صورة واحدة أو فيديو واحد                                                                |
| تجاوزات الحجم   | مدعومة                                                                         |
| تجاوزات أخرى  | يتم تجاهل `aspectRatio` و`resolution` و`audio` و`watermark` مع تحذير من الأداة |

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: { primary: "openai/sora-2" },
    },
  },
}
```

<Note>
راجع [Video Generation](/ar/tools/video-generation) لمعلمات الأداة المشتركة، واختيار المزوّد، وسلوك التبديل الاحتياطي.
</Note>

## طبقة الشخصية

يضيف OpenClaw طبقة موجّه صغيرة خاصة بـ OpenAI لتشغيلات `openai/*` و`openai-codex/*`. وتحافظ هذه الطبقة على أن يكون المساعد ودودًا ومتعاونًا وموجزًا وأكثر تعبيرًا عاطفيًا قليلًا، من دون استبدال موجّه النظام الأساسي.

| القيمة                  | التأثير                             |
| ---------------------- | ---------------------------------- |
| `"friendly"` (الافتراضي) | تمكين الطبقة الخاصة بـ OpenAI |
| `"on"`                 | اسم بديل لـ `"friendly"`             |
| `"off"`                | استخدام موجّه OpenClaw الأساسي فقط      |

<Tabs>
  <Tab title="الإعداد">
    ```json5
    {
      plugins: {
        entries: {
          openai: { config: { personality: "friendly" } },
        },
      },
    }
    ```
  </Tab>
  <Tab title="CLI">
    ```bash
    openclaw config set plugins.entries.openai.config.personality off
    ```
  </Tab>
</Tabs>

<Tip>
القيم غير حساسة لحالة الأحرف وقت التشغيل، لذا فإن `"Off"` و`"off"` كلتاهما تعطلان هذه الطبقة.
</Tip>

## الصوت والكلام

<AccordionGroup>
  <Accordion title="تركيب الكلام (TTS)">
    يسجل Plugin ‏`openai` المضمّن تركيب الكلام لسطح `messages.tts`.

    | الإعداد | مسار الإعداد | الافتراضي |
    |---------|------------|---------|
    | النموذج | `messages.tts.providers.openai.model` | `gpt-4o-mini-tts` |
    | الصوت | `messages.tts.providers.openai.voice` | `coral` |
    | السرعة | `messages.tts.providers.openai.speed` | (غير معيّن) |
    | التعليمات | `messages.tts.providers.openai.instructions` | (غير معيّن، `gpt-4o-mini-tts` فقط) |
    | التنسيق | `messages.tts.providers.openai.responseFormat` | `opus` للملاحظات الصوتية، و`mp3` للملفات |
    | مفتاح API | `messages.tts.providers.openai.apiKey` | يعود إلى `OPENAI_API_KEY` |
    | عنوان URL الأساسي | `messages.tts.providers.openai.baseUrl` | `https://api.openai.com/v1` |

    النماذج المتاحة: `gpt-4o-mini-tts` و`tts-1` و`tts-1-hd`. والأصوات المتاحة: `alloy` و`ash` و`ballad` و`cedar` و`coral` و`echo` و`fable` و`juniper` و`marin` و`onyx` و`nova` و`sage` و`shimmer` و`verse`.

    ```json5
    {
      messages: {
        tts: {
          providers: {
            openai: { model: "gpt-4o-mini-tts", voice: "coral" },
          },
        },
      },
    }
    ```

    <Note>
    عيّن `OPENAI_TTS_BASE_URL` لتجاوز عنوان URL الأساسي لـ TTS من دون التأثير في نقطة نهاية Chat API.
    </Note>

  </Accordion>

  <Accordion title="النسخ الفوري">
    يسجل Plugin ‏`openai` المضمّن النسخ الفوري لصالح Plugin Voice Call.

    | الإعداد | مسار الإعداد | الافتراضي |
    |---------|------------|---------|
    | النموذج | `plugins.entries.voice-call.config.streaming.providers.openai.model` | `gpt-4o-transcribe` |
    | مدة الصمت | `...openai.silenceDurationMs` | `800` |
    | عتبة VAD | `...openai.vadThreshold` | `0.5` |
    | مفتاح API | `...openai.apiKey` | يعود إلى `OPENAI_API_KEY` |

    <Note>
    يستخدم اتصال WebSocket إلى `wss://api.openai.com/v1/realtime` مع صوت G.711 u-law.
    </Note>

  </Accordion>

  <Accordion title="الصوت الفوري">
    يسجل Plugin ‏`openai` المضمّن الصوت الفوري لصالح Plugin Voice Call.

    | الإعداد | مسار الإعداد | الافتراضي |
    |---------|------------|---------|
    | النموذج | `plugins.entries.voice-call.config.realtime.providers.openai.model` | `gpt-realtime` |
    | الصوت | `...openai.voice` | `alloy` |
    | الحرارة | `...openai.temperature` | `0.8` |
    | عتبة VAD | `...openai.vadThreshold` | `0.5` |
    | مدة الصمت | `...openai.silenceDurationMs` | `500` |
    | مفتاح API | `...openai.apiKey` | يعود إلى `OPENAI_API_KEY` |

    <Note>
    يدعم Azure OpenAI عبر مفتاحي الإعداد `azureEndpoint` و`azureDeployment`. ويدعم استدعاء الأدوات ثنائي الاتجاه. ويستخدم تنسيق الصوت G.711 u-law.
    </Note>

  </Accordion>
</AccordionGroup>

## الإعداد المتقدم

<AccordionGroup>
  <Accordion title="النقل (WebSocket مقابل SSE)">
    يستخدم OpenClaw أسلوب WebSocket أولًا مع الرجوع الاحتياطي إلى SSE (`"auto"`) لكل من `openai/*` و`openai-codex/*`.

    في وضع `"auto"`، يقوم OpenClaw بما يلي:
    - يعيد محاولة فشل WebSocket المبكر مرة واحدة قبل الرجوع إلى SSE
    - بعد الفشل، يضع علامة على WebSocket على أنه متدهور لمدة تقارب 60 ثانية ويستخدم SSE أثناء فترة التهدئة
    - يرفق ترويسات هوية مستقرة للجلسة والدور لإعادة المحاولات وإعادة الاتصال
    - يطبّع عدادات الاستخدام (`input_tokens` / `prompt_tokens`) عبر متغيرات النقل المختلفة

    | القيمة | السلوك |
    |-------|----------|
    | `"auto"` (الافتراضي) | WebSocket أولًا، مع رجوع احتياطي إلى SSE |
    | `"sse"` | فرض SSE فقط |
    | `"websocket"` | فرض WebSocket فقط |

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "openai-codex/gpt-5.4": {
              params: { transport: "auto" },
            },
          },
        },
      },
    }
    ```

    مستندات OpenAI ذات الصلة:
    - [Realtime API with WebSocket](https://platform.openai.com/docs/guides/realtime-websocket)
    - [Streaming API responses (SSE)](https://platform.openai.com/docs/guides/streaming-responses)

  </Accordion>

  <Accordion title="الإحماء المسبق لـ WebSocket">
    يفعّل OpenClaw الإحماء المسبق لـ WebSocket افتراضيًا من أجل `openai/*` لتقليل زمن الاستجابة في الدور الأول.

    ```json5
    // تعطيل الإحماء المسبق
    {
      agents: {
        defaults: {
          models: {
            "openai/gpt-5.4": {
              params: { openaiWsWarmup: false },
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="الوضع السريع">
    يوفّر OpenClaw مفتاح تبديل مشتركًا للوضع السريع لكل من `openai/*` و`openai-codex/*`:

    - **الدردشة/الواجهة:** `/fast status|on|off`
    - **الإعداد:** `agents.defaults.models["<provider>/<model>"].params.fastMode`

    عند التمكين، يربط OpenClaw الوضع السريع بمعالجة الأولوية في OpenAI (`service_tier = "priority"`). ويتم الحفاظ على قيم `service_tier` الموجودة، ولا يعيد الوضع السريع كتابة `reasoning` أو `text.verbosity`.

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": { params: { fastMode: true } },
        "openai-codex/gpt-5.4": { params: { fastMode: true } },
      },
    },
  },
}
```

    <Note>
    تتغلب تجاوزات الجلسة على الإعداد. وتؤدي إزالة تجاوز الجلسة في واجهة Sessions إلى إعادة الجلسة إلى الإعداد الافتراضي المضبوط.
    </Note>

  </Accordion>

  <Accordion title="المعالجة ذات الأولوية (service_tier)">
    يوفّر API الخاص بـ OpenAI المعالجة ذات الأولوية عبر `service_tier`. اضبطها لكل نموذج في OpenClaw:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "openai/gpt-5.4": { params: { serviceTier: "priority" } },
            "openai-codex/gpt-5.4": { params: { serviceTier: "priority" } },
          },
        },
      },
    }
    ```

    القيم المدعومة: `auto` و`default` و`flex` و`priority`.

    <Warning>
    لا يتم تمرير `serviceTier` إلا إلى نقاط نهاية OpenAI الأصلية (`api.openai.com`) ونقاط نهاية Codex الأصلية (`chatgpt.com/backend-api`). وإذا قمت بتوجيه أي من المزوّدين عبر Proxy، فسيترك OpenClaw قيمة `service_tier` بدون تغيير.
    </Warning>

  </Accordion>

  <Accordion title="Compaction على جانب الخادم (Responses API)">
    بالنسبة إلى نماذج OpenAI Responses المباشرة (`openai/*` على `api.openai.com`)، يفعّل OpenClaw تلقائيًا Compaction على جانب الخادم:

    - يفرض `store: true` (ما لم يضبط توافق النموذج `supportsStore: false`)
    - يحقن `context_management: [{ type: "compaction", compact_threshold: ... }]`
    - القيمة الافتراضية لـ `compact_threshold`: ‏70% من `contextWindow` (أو `80000` عند عدم توفرها)

    <Tabs>
      <Tab title="تمكين صريح">
        مفيد لنقاط النهاية المتوافقة مثل Azure OpenAI Responses:

        ```json5
        {
          agents: {
            defaults: {
              models: {
                "azure-openai-responses/gpt-5.4": {
                  params: { responsesServerCompaction: true },
                },
              },
            },
          },
        }
        ```
      </Tab>
      <Tab title="حد مخصص">
        ```json5
        {
          agents: {
            defaults: {
              models: {
                "openai/gpt-5.4": {
                  params: {
                    responsesServerCompaction: true,
                    responsesCompactThreshold: 120000,
                  },
                },
              },
            },
          },
        }
        ```
      </Tab>
      <Tab title="تعطيل">
        ```json5
        {
          agents: {
            defaults: {
              models: {
                "openai/gpt-5.4": {
                  params: { responsesServerCompaction: false },
                },
              },
            },
          },
        }
        ```
      </Tab>
    </Tabs>

    <Note>
    يتحكم `responsesServerCompaction` فقط في حقن `context_management`. وتظل نماذج OpenAI Responses المباشرة تفرض `store: true` ما لم يضبط التوافق `supportsStore: false`.
    </Note>

  </Accordion>

  <Accordion title="وضع GPT الصارم الوكيلي">
    بالنسبة إلى تشغيلات عائلة GPT-5 على `openai/*` و`openai-codex/*`، يمكن لـ OpenClaw استخدام عقد تنفيذ مضمّن أكثر صرامة:

    ```json5
    {
      agents: {
        defaults: {
          embeddedPi: { executionContract: "strict-agentic" },
        },
      },
    }
    ```

    مع `strict-agentic`، يقوم OpenClaw بما يلي:
    - لا يعود يعتبر الدور الذي يحتوي على خطة فقط تقدمًا ناجحًا عندما يكون إجراء أداة متاحًا
    - يعيد محاولة الدور مع توجيه لتنفيذ الإجراء فورًا
    - يفعّل `update_plan` تلقائيًا للأعمال الكبيرة
    - يعرض حالة تعطّل صريحة إذا استمر النموذج في التخطيط من دون تنفيذ

    <Note>
    يقتصر ذلك على تشغيلات عائلة GPT-5 الخاصة بـ OpenAI وCodex فقط. أما المزوّدون الآخرون وعائلات النماذج الأقدم فيحتفظون بالسلوك الافتراضي.
    </Note>

  </Accordion>

  <Accordion title="المسارات الأصلية مقابل المسارات المتوافقة مع OpenAI">
    يتعامل OpenClaw مع نقاط النهاية المباشرة الخاصة بـ OpenAI وCodex وAzure OpenAI بطريقة مختلفة عن وكلاء `/v1` العامة المتوافقة مع OpenAI:

    **المسارات الأصلية** (`openai/*` و`openai-codex/*` وAzure OpenAI):
    - تُبقي `reasoning: { effort: "none" }` كما هي عندما يكون الاستدلال معطّلًا صراحةً
    - تضبط مخططات الأدوات على الوضع الصارم افتراضيًا
    - ترفق ترويسات إسناد مخفية فقط على المضيفات الأصلية الموثّقة
    - تُبقي تشكيل الطلبات الخاص بـ OpenAI فقط (`service_tier` و`store` وتوافق الاستدلال وتلميحات التخزين المؤقت للموجّهات)

    **المسارات المتوافقة/عبر Proxy:**
    - تستخدم سلوك توافق أكثر مرونة
    - لا تفرض مخططات أدوات صارمة أو ترويسات أصلية فقط

    يستخدم Azure OpenAI النقل الأصلي وسلوك التوافق الأصلي، لكنه لا يتلقى ترويسات الإسناد المخفية.

  </Accordion>
</AccordionGroup>

## ذو صلة

<CardGroup cols={2}>
  <Card title="اختيار النموذج" href="/ar/concepts/model-providers" icon="layers">
    اختيار المزوّدين، ومراجع النماذج، وسلوك التبديل الاحتياطي.
  </Card>
  <Card title="توليد الصور" href="/ar/tools/image-generation" icon="image">
    معلمات أداة الصور المشتركة واختيار المزوّد.
  </Card>
  <Card title="توليد الفيديو" href="/ar/tools/video-generation" icon="video">
    معلمات أداة الفيديو المشتركة واختيار المزوّد.
  </Card>
  <Card title="OAuth and auth" href="/ar/gateway/authentication" icon="key">
    تفاصيل المصادقة وقواعد إعادة استخدام بيانات الاعتماد.
  </Card>
</CardGroup>
