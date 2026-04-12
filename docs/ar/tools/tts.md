---
read_when:
    - تمكين تحويل النص إلى كلام للردود
    - إعداد مزودي TTS أو الحدود
    - استخدام أوامر `/tts`
summary: تحويل النص إلى كلام (TTS) للردود الصادرة
title: تحويل النص إلى كلام
x-i18n:
    generated_at: "2026-04-12T23:34:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: ad79a6be34879347dc73fdab1bd219823cd7c6aa8504e3e4c73e1a0554c837c5
    source_path: tools/tts.md
    workflow: 15
---

# تحويل النص إلى كلام (TTS)

يمكن لـ OpenClaw تحويل الردود الصادرة إلى صوت باستخدام ElevenLabs أو Microsoft أو MiniMax أو OpenAI.
ويعمل هذا في أي مكان يستطيع OpenClaw إرسال الصوت إليه.

## الخدمات المدعومة

- **ElevenLabs** (كمزود أساسي أو احتياطي)
- **Microsoft** (كمزود أساسي أو احتياطي؛ يستخدم التنفيذ المدمج الحالي `node-edge-tts`)
- **MiniMax** (كمزود أساسي أو احتياطي؛ يستخدم T2A v2 API)
- **OpenAI** (كمزود أساسي أو احتياطي؛ ويُستخدم أيضًا للملخصات)

### ملاحظات حول Microsoft speech

يستخدم مزود Microsoft speech المدمج حاليًا خدمة TTS العصبية عبر الإنترنت من Microsoft Edge
من خلال مكتبة `node-edge-tts`. وهي خدمة مستضافة (وليست
محلية)، وتستخدم نقاط نهاية Microsoft، ولا تتطلب مفتاح API.
يوفّر `node-edge-tts` خيارات إعدادات للكلام وتنسيقات للإخراج، لكن
ليست كل الخيارات مدعومة من الخدمة. ولا يزال الإدخال الخاص بالإعدادات القديمة وتوجيهات
`edge` يعمل ويتم تطبيعه إلى `microsoft`.

ولأن هذا المسار عبارة عن خدمة ويب عامة من دون SLA أو حصة منشورة،
فتعامل معه على أنه أفضل جهد. وإذا كنت تحتاج إلى حدود مضمونة ودعم، فاستخدم OpenAI
أو ElevenLabs.

## المفاتيح الاختيارية

إذا كنت تريد OpenAI أو ElevenLabs أو MiniMax:

- `ELEVENLABS_API_KEY` (أو `XI_API_KEY`)
- `MINIMAX_API_KEY`
- `OPENAI_API_KEY`

لا يتطلب Microsoft speech **مفتاح API**.

إذا تم إعداد عدة مزودين، فسيُستخدم المزود المحدد أولًا وسيكون الآخرون خيارات احتياطية.
ويستخدم التلخيص التلقائي `summaryModel` المُعد (أو `agents.defaults.model.primary`)،
لذلك يجب أيضًا مصادقة ذلك المزود إذا قمت بتمكين الملخصات.

## روابط الخدمة

- [دليل OpenAI لتحويل النص إلى كلام](https://platform.openai.com/docs/guides/text-to-speech)
- [مرجع OpenAI Audio API](https://platform.openai.com/docs/api-reference/audio)
- [تحويل النص إلى كلام في ElevenLabs](https://elevenlabs.io/docs/api-reference/text-to-speech)
- [المصادقة في ElevenLabs](https://elevenlabs.io/docs/api-reference/authentication)
- [MiniMax T2A v2 API](https://platform.minimaxi.com/document/T2A%20V2)
- [node-edge-tts](https://github.com/SchneeHertz/node-edge-tts)
- [تنسيقات إخراج Microsoft Speech](https://learn.microsoft.com/azure/ai-services/speech-service/rest-text-to-speech#audio-outputs)

## هل هو مفعّل افتراضيًا؟

لا. إن Auto‑TTS **معطّل** افتراضيًا. قم بتمكينه في الإعدادات باستخدام
`messages.tts.auto` أو محليًا باستخدام `/tts on`.

عندما لا يتم تعيين `messages.tts.provider`، يختار OpenClaw أول
مزود speech مُعد وفق ترتيب الاختيار التلقائي في السجل.

## الإعدادات

توجد إعدادات TTS ضمن `messages.tts` في `openclaw.json`.
المخطط الكامل موجود في [إعدادات Gateway](/ar/gateway/configuration).

### الحد الأدنى من الإعدادات (التمكين + المزود)

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "elevenlabs",
    },
  },
}
```

### OpenAI أساسي مع ElevenLabs احتياطي

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "openai",
      summaryModel: "openai/gpt-4.1-mini",
      modelOverrides: {
        enabled: true,
      },
      providers: {
        openai: {
          apiKey: "openai_api_key",
          baseUrl: "https://api.openai.com/v1",
          model: "gpt-4o-mini-tts",
          voice: "alloy",
        },
        elevenlabs: {
          apiKey: "elevenlabs_api_key",
          baseUrl: "https://api.elevenlabs.io",
          voiceId: "voice_id",
          modelId: "eleven_multilingual_v2",
          seed: 42,
          applyTextNormalization: "auto",
          languageCode: "en",
          voiceSettings: {
            stability: 0.5,
            similarityBoost: 0.75,
            style: 0.0,
            useSpeakerBoost: true,
            speed: 1.0,
          },
        },
      },
    },
  },
}
```

### Microsoft أساسي (من دون مفتاح API)

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "microsoft",
      providers: {
        microsoft: {
          enabled: true,
          voice: "en-US-MichelleNeural",
          lang: "en-US",
          outputFormat: "audio-24khz-48kbitrate-mono-mp3",
          rate: "+10%",
          pitch: "-5%",
        },
      },
    },
  },
}
```

### MiniMax أساسي

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "minimax",
      providers: {
        minimax: {
          apiKey: "minimax_api_key",
          baseUrl: "https://api.minimax.io",
          model: "speech-2.8-hd",
          voiceId: "English_expressive_narrator",
          speed: 1.0,
          vol: 1.0,
          pitch: 0,
        },
      },
    },
  },
}
```

### تعطيل Microsoft speech

```json5
{
  messages: {
    tts: {
      providers: {
        microsoft: {
          enabled: false,
        },
      },
    },
  },
}
```

### حدود مخصصة + مسار التفضيلات

```json5
{
  messages: {
    tts: {
      auto: "always",
      maxTextLength: 4000,
      timeoutMs: 30000,
      prefsPath: "~/.openclaw/settings/tts.json",
    },
  },
}
```

### الرد بالصوت فقط بعد رسالة صوتية واردة

```json5
{
  messages: {
    tts: {
      auto: "inbound",
    },
  },
}
```

### تعطيل التلخيص التلقائي للردود الطويلة

```json5
{
  messages: {
    tts: {
      auto: "always",
    },
  },
}
```

ثم شغّل:

```
/tts summary off
```

### ملاحظات حول الحقول

- `auto`: وضع Auto‑TTS (`off`، `always`، `inbound`، `tagged`).
  - يرسل `inbound` الصوت فقط بعد رسالة صوتية واردة.
  - يرسل `tagged` الصوت فقط عندما يتضمن الرد توجيهات `[[tts:key=value]]` أو كتلة `[[tts:text]]...[[/tts:text]]`.
- `enabled`: مفتاح تبديل قديم (يقوم doctor بترحيله إلى `auto`).
- `mode`: ‏`"final"` (الافتراضي) أو `"all"` (يتضمن ردود الأدوات/الكتل).
- `provider`: معرّف مزود speech مثل `"elevenlabs"` أو `"microsoft"` أو `"minimax"` أو `"openai"` (ويكون الاحتياطي تلقائيًا).
- إذا لم يتم تعيين `provider`، يستخدم OpenClaw أول مزود speech مُعد وفق ترتيب الاختيار التلقائي في السجل.
- لا يزال `provider: "edge"` القديم يعمل ويتم تطبيعه إلى `microsoft`.
- `summaryModel`: نموذج منخفض التكلفة اختياري للتلخيص التلقائي؛ والقيمة الافتراضية هي `agents.defaults.model.primary`.
  - يقبل `provider/model` أو اسمًا مستعارًا لنموذج مُعد.
- `modelOverrides`: السماح للنموذج بإصدار توجيهات TTS (مفعّل افتراضيًا).
  - تكون القيمة الافتراضية لـ `allowProvider` هي `false` (تبديل المزود اشتراك اختياري).
- `providers.<id>`: إعدادات مملوكة للمزود ومفهرسة بمعرّف مزود speech.
- يتم ترحيل كتل المزود المباشرة القديمة (`messages.tts.openai`، و`messages.tts.elevenlabs`، و`messages.tts.microsoft`، و`messages.tts.edge`) تلقائيًا إلى `messages.tts.providers.<id>` عند التحميل.
- `maxTextLength`: حد أقصى صارم لإدخال TTS (أحرف). يفشل `/tts audio` إذا تم تجاوزه.
- `timeoutMs`: مهلة الطلب (مللي ثانية).
- `prefsPath`: تجاوز مسار JSON المحلي للتفضيلات (المزود/الحد/الملخص).
- تعود قيم `apiKey` إلى متغيرات البيئة (`ELEVENLABS_API_KEY`/`XI_API_KEY`، و`MINIMAX_API_KEY`، و`OPENAI_API_KEY`).
- `providers.elevenlabs.baseUrl`: تجاوز عنوان ElevenLabs API الأساسي.
- `providers.openai.baseUrl`: تجاوز نقطة نهاية OpenAI TTS.
  - ترتيب الحل: `messages.tts.providers.openai.baseUrl` -> `OPENAI_TTS_BASE_URL` -> `https://api.openai.com/v1`
  - تُعامل القيم غير الافتراضية على أنها نقاط نهاية TTS متوافقة مع OpenAI، لذلك تُقبل أسماء النماذج والأصوات المخصصة.
- `providers.elevenlabs.voiceSettings`:
  - `stability`، و`similarityBoost`، و`style`: ‏`0..1`
  - `useSpeakerBoost`: ‏`true|false`
  - `speed`: ‏`0.5..2.0` ‏(`1.0` = عادي)
- `providers.elevenlabs.applyTextNormalization`: ‏`auto|on|off`
- `providers.elevenlabs.languageCode`: رمز ISO 639-1 من حرفين (مثل `en`، `de`)
- `providers.elevenlabs.seed`: عدد صحيح `0..4294967295` (حتمية بأفضل جهد)
- `providers.minimax.baseUrl`: تجاوز عنوان MiniMax API الأساسي (الافتراضي `https://api.minimax.io`، ومتغير البيئة: `MINIMAX_API_HOST`).
- `providers.minimax.model`: نموذج TTS (الافتراضي `speech-2.8-hd`، ومتغير البيئة: `MINIMAX_TTS_MODEL`).
- `providers.minimax.voiceId`: معرّف الصوت (الافتراضي `English_expressive_narrator`، ومتغير البيئة: `MINIMAX_TTS_VOICE_ID`).
- `providers.minimax.speed`: سرعة التشغيل `0.5..2.0` (الافتراضي 1.0).
- `providers.minimax.vol`: مستوى الصوت `(0, 10]` (الافتراضي 1.0؛ يجب أن يكون أكبر من 0).
- `providers.minimax.pitch`: إزاحة النغمة `-12..12` (الافتراضي 0).
- `providers.microsoft.enabled`: السماح باستخدام Microsoft speech (الافتراضي `true`؛ من دون مفتاح API).
- `providers.microsoft.voice`: اسم الصوت العصبي من Microsoft (مثل `en-US-MichelleNeural`).
- `providers.microsoft.lang`: رمز اللغة (مثل `en-US`).
- `providers.microsoft.outputFormat`: تنسيق إخراج Microsoft (مثل `audio-24khz-48kbitrate-mono-mp3`).
  - راجع تنسيقات إخراج Microsoft Speech للقيم الصالحة؛ ليست كل التنسيقات مدعومة من النقل المدمج المعتمد على Edge.
- `providers.microsoft.rate` / `providers.microsoft.pitch` / `providers.microsoft.volume`: سلاسل نسب مئوية (مثل `+10%`، `-5%`).
- `providers.microsoft.saveSubtitles`: كتابة ترجمات JSON إلى جانب الملف الصوتي.
- `providers.microsoft.proxy`: عنوان URL لـ proxy لطلبات Microsoft speech.
- `providers.microsoft.timeoutMs`: تجاوز مهلة الطلب (مللي ثانية).
- `edge.*`: اسم بديل قديم لإعدادات Microsoft نفسها.

## تجاوزات يقودها النموذج (مفعّلة افتراضيًا)

افتراضيًا، **يمكن** للنموذج إصدار توجيهات TTS لرد واحد.
عندما تكون `messages.tts.auto` هي `tagged`، تكون هذه التوجيهات مطلوبة لتشغيل الصوت.

عند التمكين، يمكن للنموذج إصدار توجيهات `[[tts:...]]` لتجاوز الصوت
لرد واحد، بالإضافة إلى كتلة اختيارية `[[tts:text]]...[[/tts:text]]`
لتوفير وسوم تعبيرية (ضحك، وإشارات غناء، وما إلى ذلك) ينبغي أن تظهر في
الصوت فقط.

يتم تجاهل توجيهات `provider=...` ما لم تكن `modelOverrides.allowProvider: true`.

مثال على حمولة الرد:

```
Here you go.

[[tts:voiceId=pMsXgVXv3BLzUgSXRplE model=eleven_v3 speed=1.1]]
[[tts:text]](laughs) Read the song once more.[[/tts:text]]
```

مفاتيح التوجيه المتاحة (عند التمكين):

- `provider` (معرّف مزود speech مسجل، مثل `openai` أو `elevenlabs` أو `minimax` أو `microsoft`؛ ويتطلب `allowProvider: true`)
- `voice` (صوت OpenAI) أو `voiceId` ‏(ElevenLabs / MiniMax)
- `model` (نموذج OpenAI TTS، أو معرّف نموذج ElevenLabs، أو نموذج MiniMax)
- `stability`، و`similarityBoost`، و`style`، و`speed`، و`useSpeakerBoost`
- `vol` / `volume` (مستوى صوت MiniMax، ‏0-10)
- `pitch` (نغمة MiniMax، ‏-12 إلى 12)
- `applyTextNormalization` ‏(`auto|on|off`)
- `languageCode` (ISO 639-1)
- `seed`

تعطيل جميع تجاوزات النموذج:

```json5
{
  messages: {
    tts: {
      modelOverrides: {
        enabled: false,
      },
    },
  },
}
```

قائمة سماح اختيارية (تمكين تبديل المزود مع إبقاء الإعدادات الأخرى قابلة للضبط):

```json5
{
  messages: {
    tts: {
      modelOverrides: {
        enabled: true,
        allowProvider: true,
        allowSeed: false,
      },
    },
  },
}
```

## التفضيلات لكل مستخدم

تكتب أوامر الشرطة المائلة التجاوزات المحلية إلى `prefsPath` (الافتراضي:
`~/.openclaw/settings/tts.json`، أو تجاوزه باستخدام `OPENCLAW_TTS_PREFS` أو
`messages.tts.prefsPath`).

الحقول المخزنة:

- `enabled`
- `provider`
- `maxLength` (عتبة التلخيص؛ الافتراضي 1500 حرف)
- `summarize` (الافتراضي `true`)

تتجاوز هذه الحقول `messages.tts.*` لذلك المضيف.

## تنسيقات الإخراج (ثابتة)

- **Feishu / Matrix / Telegram / WhatsApp**: رسالة صوتية Opus ‏(`opus_48000_64` من ElevenLabs، و`opus` من OpenAI).
  - يُعد 48kHz / 64kbps توازنًا جيدًا للرسائل الصوتية.
- **القنوات الأخرى**: MP3 ‏(`mp3_44100_128` من ElevenLabs، و`mp3` من OpenAI).
  - يُعد 44.1kHz / 128kbps التوازن الافتراضي لوضوح الكلام.
- **MiniMax**: ‏MP3 (نموذج `speech-2.8-hd`، ومعدل عينة 32kHz). لا يتم دعم تنسيق الملاحظات الصوتية أصليًا؛ استخدم OpenAI أو ElevenLabs للحصول على رسائل صوتية Opus مضمونة.
- **Microsoft**: يستخدم `microsoft.outputFormat` (الافتراضي `audio-24khz-48kbitrate-mono-mp3`).
  - يقبل النقل المدمج `outputFormat`، لكن ليست كل التنسيقات متاحة من الخدمة.
  - تتبع قيم تنسيق الإخراج تنسيقات إخراج Microsoft Speech (بما في ذلك Ogg/WebM Opus).
  - يقبل Telegram `sendVoice` تنسيقات OGG/MP3/M4A؛ استخدم OpenAI/ElevenLabs إذا كنت تحتاج إلى رسائل صوتية Opus مضمونة.
  - إذا فشل تنسيق إخراج Microsoft المُعد، فسيعيد OpenClaw المحاولة باستخدام MP3.

تنسيقات إخراج OpenAI/ElevenLabs ثابتة لكل قناة (انظر أعلاه).

## سلوك Auto-TTS

عند التمكين، يقوم OpenClaw بما يلي:

- يتخطى TTS إذا كان الرد يحتوي بالفعل على وسائط أو توجيه `MEDIA:`.
- يتخطى الردود القصيرة جدًا (< 10 أحرف).
- يلخّص الردود الطويلة عند التمكين باستخدام `agents.defaults.model.primary` (أو `summaryModel`).
- يرفق الصوت المُنشأ بالرد.

إذا تجاوز الرد `maxLength` وكان التلخيص معطّلًا (أو لا يوجد مفتاح API
لنموذج التلخيص)، فسيتم
تخطي الصوت وإرسال الرد النصي العادي.

## مخطط التدفق

```
Reply -> TTS enabled?
  no  -> send text
  yes -> has media / MEDIA: / short?
          yes -> send text
          no  -> length > limit?
                   no  -> TTS -> attach audio
                   yes -> summary enabled?
                            no  -> send text
                            yes -> summarize (summaryModel or agents.defaults.model.primary)
                                      -> TTS -> attach audio
```

## استخدام أوامر الشرطة المائلة

يوجد أمر واحد فقط: `/tts`.
راجع [أوامر الشرطة المائلة](/ar/tools/slash-commands) لمعرفة تفاصيل التمكين.

ملاحظة Discord: ‏`/tts` هو أمر Discord مدمج، لذا يسجل OpenClaw
`/voice` كأمر أصلي هناك. ولا يزال النص `/tts ...` يعمل.

```
/tts off
/tts on
/tts status
/tts provider openai
/tts limit 2000
/tts summary off
/tts audio Hello from OpenClaw
```

ملاحظات:

- تتطلب الأوامر مُرسِلًا مخوّلًا (ولا تزال قواعد allowlist/المالك سارية).
- يجب تمكين `commands.text` أو تسجيل الأوامر الأصلية.
- تقبل الإعدادات `messages.tts.auto` القيم `off|always|inbound|tagged`.
- يكتب `/tts on` تفضيل TTS المحلي إلى `always`؛ ويكتب `/tts off` إلى `off`.
- استخدم الإعدادات عندما تريد القيم الافتراضية `inbound` أو `tagged`.
- يتم تخزين `limit` و`summary` في التفضيلات المحلية، وليس في الإعدادات الرئيسية.
- يقوم `/tts audio` بإنشاء رد صوتي لمرة واحدة (ولا يفعّل TTS).
- يتضمن `/tts status` عرضًا للاحتياطي لأحدث محاولة:
  - احتياطي ناجح: `Fallback: <primary> -> <used>` بالإضافة إلى `Attempts: ...`
  - فشل: `Error: ...` بالإضافة إلى `Attempts: ...`
  - تشخيصات تفصيلية: `Attempt details: provider:outcome(reasonCode) latency`
- تتضمن إخفاقات OpenAI وElevenLabs في API الآن تفاصيل خطأ المزود المحللة ومعرّف الطلب (عند إرجاعه من المزود)، ويتم إظهار ذلك في أخطاء/سجلات TTS.

## أداة الوكيل

تقوم أداة `tts` بتحويل النص إلى كلام وتعيد مرفقًا صوتيًا من أجل
تسليم الرد. عندما تكون القناة Feishu أو Matrix أو Telegram أو WhatsApp،
يتم تسليم الصوت كرسالة صوتية بدلًا من مرفق ملف.

## Gateway RPC

طرق Gateway:

- `tts.status`
- `tts.enable`
- `tts.disable`
- `tts.convert`
- `tts.setProvider`
- `tts.providers`
